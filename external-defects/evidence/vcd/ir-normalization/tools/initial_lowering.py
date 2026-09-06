"""依据原始 LLHD 的一次初始化过程，为残留双驱动寄存器补充 preset。

这是受限的前端适配，不是 LLHD 仿真器。输入必须来自相同 RTL、参数和工具；
调用方负责保存这些身份，函数额外核对模块、端口及逐信号对应关系。只改写已证明
的初始化驱动，动态驱动和信号保留给官方 llhd-sig2reg 处理。
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field


POLICY = "proven-single-initial-to-preset-v1"
SSA = r"%[A-Za-z0-9_.$-]+"


class InitialLoweringError(ValueError):
    """输入超出已证明的初始化转换范围。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InitialLoweringError(message)


def _without_comment(line: str) -> str:
    quoted = escaped = False
    for i, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == "\\" and quoted:
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and line[i:i + 2] == "//":
            return line[:i]
    return line


def _without_location(text: str) -> str:
    return re.sub(r"\s+loc\(.*\)\s*$", "", text).strip()


@dataclass
class _Op:
    name: str
    result: str | None
    operands: list[str]
    suffix: str
    line: int
    text: str
    children: list[_Op] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)


def _parse(text: str) -> tuple[_Op, list[str]]:
    """只接受 circt-opt 的逐行 generic 打印，未知结构不会被跳过。"""
    lines = text.splitlines(keepends=True)
    stack: list[_Op] = []
    roots: list[_Op] = []
    for index, original in enumerate(lines):
        line = _without_comment(original).strip()
        if not line or re.fullmatch(r"#[-\w]+\s*=\s*loc\(.*\)", line):
            continue
        if line.startswith("^bb"):
            _require(bool(stack) and line.endswith(":"), f"第 {index + 1} 行的 block 格式不支持")
            stack[-1].blocks.append(line)
            continue
        if line.startswith("})"):
            _require(bool(stack), f"第 {index + 1} 行出现无对应区域的结束符")
            _require(_without_location(line) == "}) : () -> ()", "仅支持无区域结果的模块和过程")
            stack.pop()
            continue
        match = re.fullmatch(rf'(?:(?P<result>{SSA})\s*=\s*)?"(?P<name>[\w.]+)"\((?P<args>[^()]*)\)(?P<tail>.*)', line)
        _require(match is not None, f"第 {index + 1} 行不是受支持的单行 generic operation")
        assert match is not None
        args = [x.strip() for x in match["args"].split(",") if x.strip()]
        _require(all(re.fullmatch(SSA, x) for x in args), "仅支持直接 SSA 操作数")
        suffix = _without_location(match["tail"])
        region = suffix.endswith("({")
        op = _Op(match["name"], match["result"], args, suffix, index + 1, original)
        (stack[-1].children if stack else roots).append(op)
        if region:
            _require(op.name in {"builtin.module", "hw.module", "llhd.process"}, f"不支持区域 operation {op.name}")
            stack.append(op)
    _require(not stack and len(roots) == 1 and roots[0].name == "builtin.module", "要求唯一完整 builtin.module")
    outer = roots[0]
    _require(outer.suffix == "({" and not outer.operands, "不支持额外 builtin.module 结构")
    _require(len(outer.children) == 1 and outer.children[0].name == "hw.module", "要求唯一 hw.module，不能跨模块匹配初始化")
    module = outer.children[0]
    _require(len(module.blocks) == 1, "要求单 block 的 hw.module")
    return module, lines


def _identity(module: _Op) -> tuple[str, str]:
    name = re.search(r'\bsym_name\s*=\s*("(?:[^"\\]|\\.)*")', module.suffix)
    ports = re.search(r"\bmodule_type\s*=\s*!hw.modty<([^<>]*)>", module.suffix)
    _require(name is not None and ports is not None, "模块缺少名称或标量端口声明")
    _require(re.search(r"\bparameters\s*=\s*\[\s*\]", module.suffix) is not None, "仅支持已展开参数的模块")
    assert name and ports
    declarations = ports[1].split(",")
    _require(all(re.fullmatch(r"\s*(input|output)\s+[A-Za-z_]\w*\s*:\s*i[1-9][0-9]*\s*", x) for x in declarations), "仅支持顶层正位宽整数端口")
    return json.loads(name[1]), re.sub(r"\s+", "", ports[1])


def _input_arguments(module: _Op) -> dict[str, int]:
    block = re.fullmatch(r"\^bb[0-9]+\((.*)\):", module.blocks[0])
    _require(block is not None, "模块输入 block 格式不支持")
    assert block
    arguments = {}
    for item in block[1].split(","):
        match = re.fullmatch(rf"({SSA})\s*:\s*i([1-9][0-9]*)(?:\s+loc\(.*\))?", item.strip())
        _require(match is not None, "模块 block 仅支持整数输入")
        assert match
        _require(match[1] not in arguments, "模块输入 SSA 重复")
        arguments[match[1]] = int(match[2])
    ports = _identity(module)[1]
    widths = [int(x) for x in re.findall(r"(?:^|,)input[A-Za-z_]\w*:i([1-9][0-9]*)", ports)]
    _require(list(arguments.values()) == widths, "模块端口与 block 输入位宽不一致")
    return arguments


def _definitions(ops: list[_Op]) -> dict[str, _Op]:
    result: dict[str, _Op] = {}
    for op in ops:
        if op.result:
            _require(op.result not in result, f"重复 SSA 定义 {op.result}")
            result[op.result] = op
    return result


def _constant(op: _Op) -> tuple[int, int]:
    _require(op.name == "hw.constant" and not op.operands and not op.children, "初值必须是直接 hw.constant")
    match = re.fullmatch(r"<\{\s*value\s*=\s*(true|false|-?[0-9]+)(?:\s*:\s*i([1-9][0-9]*))?\s*\}>\s*:\s*\(\)\s*->\s*i([1-9][0-9]*)", op.suffix)
    _require(match is not None, "不支持的整数常量表示")
    assert match
    literal, attr_width, result_width = match.groups()
    width = int(result_width)
    if literal in {"true", "false"}:
        _require(width == 1 and attr_width is None, "布尔常量必须是 i1")
        return int(literal == "true"), width
    _require(attr_width is not None and int(attr_width) == width, "常量属性与结果位宽不一致")
    value = int(literal)
    _require(-(1 << (width - 1)) <= value < (1 << width), "常量超出 signless 位宽")
    return value & ((1 << width) - 1), width


def _get(definitions: dict[str, _Op], value: str) -> _Op:
    _require(value in definitions, f"缺少直接定义 {value}")
    return definitions[value]


def _time(definitions: dict[str, _Op], value: str) -> None:
    op = _get(definitions, value)
    _require(op.name == "llhd.constant_time" and not op.operands, "初始化必须使用直接时间常量")
    _require(re.fullmatch(r"<\{\s*value\s*=\s*#llhd.time<0(?:fs|ps|ns|us|ms|s),\s*0d,\s*1e>\s*\}>\s*:\s*\(\)\s*->\s*!llhd.time", op.suffix) is not None, "只支持零物理延迟、0d/1e 的即时初始化，不支持延时")


def _signal(op: _Op, definitions: dict[str, _Op]) -> dict:
    _require(op.name == "llhd.sig" and op.result is not None and len(op.operands) == 1, "不支持的信号定义")
    match = re.fullmatch(r'<\{\s*name\s*=\s*("(?:[^"\\]|\\.)*")\s*\}>\s*:\s*\(i([1-9][0-9]*)\)\s*->\s*!llhd.ref<i([1-9][0-9]*)>', op.suffix)
    _require(match is not None, "只支持具名完整整数 llhd.sig")
    assert match
    name, input_width, output_width = match.groups()
    _require(input_width == output_width, "信号输入与引用位宽不一致")
    value, width = _constant(_get(definitions, op.operands[0]))
    _require(width == int(input_width), "信号初值位宽不一致")
    name = json.loads(name)
    _require(bool(name), "不能用空信号名称匹配初始化")
    return {"name": name, "width": width, "signal_initial_value": value, "ssa": op.result, "line": op.line}


def _drive(op: _Op, width: int, definitions: dict[str, _Op]) -> None:
    _require(op.name == "llhd.drv" and op.result is None and len(op.operands) == 3 and not op.children, "只支持无条件、完整信号的单个驱动")
    expected = rf":\s*\(!llhd.ref<i{width}>,\s*i{width},\s*!llhd.time\)\s*->\s*\(\)"
    _require(re.fullmatch(expected, op.suffix) is not None, "驱动类型、条件或额外属性超出支持范围")
    _time(definitions, op.operands[2])


def _walk(op: _Op):
    yield op
    for child in op.children:
        yield from _walk(child)


def _proofs(module: _Op) -> dict[str, dict]:
    definitions = _definitions(module.children)
    signals = {op.result: _signal(op, definitions) for op in module.children if op.name == "llhd.sig"}
    _require(len({s["name"] for s in signals.values()}) == len(signals), "pre-LLHD 信号名称重复")
    proofs: dict[str, dict] = {}
    for process in (op for op in module.children if op.name == "llhd.process"):
        # 常规循环时钟过程没有 halt；绝不从其常量赋值推断初始化。
        if not any(op.name == "llhd.halt" for op in _walk(process)):
            continue
        _require(process.suffix == "({" and not process.operands and not process.blocks, "初始化过程不能含参数或显式控制流 block")
        actions = [op for op in process.children if op.name not in {"hw.constant", "llhd.constant_time"}]
        _require([op.name for op in actions] == ["llhd.drv", "llhd.halt"], "一次初始化只允许常量定义、单 drv 和 halt；不支持 wait/branch/多操作")
        _require(all(not op.children for op in process.children), "初始化不支持嵌套区域")
        drive, halt = actions
        _require(halt.suffix == ": () -> ()" and not halt.operands and halt.result is None, "不支持的 halt 结构")
        _require(process.children[-1] is halt, "halt 必须是初始化的最后操作")
        local = _definitions(process.children)
        _require(not set(local).intersection(definitions), "初始化局部 SSA 遮蔽了模块定义")
        available = {**definitions, **local}
        _require(drive.operands and drive.operands[0] in signals, "初始化目标必须是模块完整信号")
        signal = signals[drive.operands[0]]
        _drive(drive, signal["width"], available)
        value, width = _constant(_get(available, drive.operands[1]))
        _require(width == signal["width"], "初始化常量与信号位宽不一致")
        _require(signal["name"] not in proofs, f"信号 {signal['name']} 有多个一次初始化过程")
        proofs[signal["name"]] = {**signal, "initial_value": value, "process_line": process.line, "driver_line": drive.line}
    return proofs


def _register(op: _Op, signal: dict, definitions: dict[str, _Op], inputs: dict[str, int]) -> tuple[str, int | None]:
    width = signal["width"]
    _require(op.name == "seq.firreg" and op.result is not None and len(op.operands) == 2 and not op.children, "动态驱动必须是唯一无复位 seq.firreg")
    match = re.fullmatch(r"<\{(.*)\}>\s*:\s*\(i" + str(width) + r",\s*!seq.clock\)\s*->\s*i" + str(width), op.suffix)
    _require(match is not None, "寄存器数据/结果/时钟类型不匹配")
    assert match
    attrs = match[1]
    # 该适配只支持 name 和可选 preset；其他寄存器属性需独立验证。
    name_match = re.search(r'(?:^|,)\s*name\s*=\s*("(?:[^"\\]|\\.)*")\s*(?=,|$)', attrs)
    _require(name_match is not None and json.loads(name_match[1]) == signal["name"], "寄存器与信号名称不一致")
    assert name_match
    remainder = attrs[:name_match.start()] + attrs[name_match.end():]
    remainder = remainder.strip().strip(",").strip()
    preset = None
    if remainder:
        preset_match = re.fullmatch(r"preset\s*=\s*(true|false|-?[0-9]+)(?:\s*:\s*i([1-9][0-9]*))?", remainder)
        _require(preset_match is not None, "已有寄存器属性或 preset 位宽不支持")
        assert preset_match
        if preset_match[1] in {"true", "false"}:
            _require(width == 1 and preset_match[2] is None, "布尔 preset 必须是 i1")
            value = int(preset_match[1] == "true")
        else:
            _require(preset_match[2] is not None and int(preset_match[2]) == width, "preset 位宽不一致")
            value = int(preset_match[1])
        _require(-(1 << (width - 1)) <= value < (1 << width), "preset 超出位宽")
        preset = value & ((1 << width) - 1)
    clock = _get(definitions, op.operands[1])
    _require(clock.name == "seq.to_clock" and len(clock.operands) == 1 and clock.suffix == ": (i1) -> !seq.clock", "只支持直接 i1 输入生成的时钟")
    _require(inputs.get(clock.operands[0]) == 1, "时钟必须直接来自模块的 i1 输入")
    return clock.operands[0], preset


def normalize_initial_registers(raw_hw_generic: str, pre_llhd_generic: str) -> tuple[str, dict]:
    """转换已证明的一次常量初始化；超出范围时抛出 InitialLoweringError。

    只接受 circt-opt generic 格式及零物理延迟的 0d/1e blocking 初始化。
    已由前端消除的零初始化必须仍对应同名、同宽、无 preset 或零 preset 的寄存器，
    由调用方明确采用的二态零初始化策略覆盖；未匹配的非零初值一律拒绝。
    """
    raw, lines = _parse(raw_hw_generic)
    pre, _ = _parse(pre_llhd_generic)
    _require(_identity(raw) == _identity(pre), "两个阶段的模块名称、端口或参数身份不一致")
    inputs = _input_arguments(raw)
    _input_arguments(pre)
    proofs = _proofs(pre)
    _require(bool(proofs), "pre-LLHD 没有可证明的一次初始化过程")
    definitions = _definitions(raw.children)
    _require(all(not op.children for op in raw.children), "raw HW 中仍有过程或其他区域")
    _require(all(not op.name.startswith("llhd.") or op.name in {"llhd.sig", "llhd.prb", "llhd.drv", "llhd.constant_time"} for op in raw.children), "raw HW 含不支持的 LLHD operation")
    signals = [_signal(op, definitions) for op in raw.children if op.name == "llhd.sig"]
    _require(bool(signals), "raw HW 没有需要归一化的残留信号")
    _require(len({s["name"] for s in signals}) == len(signals), "raw HW 信号名称重复")
    raw_register_names = []
    for op in raw.children:
        if op.name == "seq.firreg":
            match = re.search(r'\bname\s*=\s*("(?:[^"\\]|\\.)*")', op.suffix)
            if match:
                raw_register_names.append(json.loads(match[1]))
    _require(len(raw_register_names) == len(set(raw_register_names)), "raw HW 寄存器名称重复，不能唯一匹配初始化")
    replacements = []
    used: set[str] = set()
    clocks: set[str] = set()
    for signal in signals:
        name, width, ssa = signal["name"], signal["width"], signal["ssa"]
        _require(name in proofs, f"残留信号 {name} 缺少一次初始化来源证明")
        proof = proofs[name]
        _require((width, signal["signal_initial_value"]) == (proof["width"], proof["signal_initial_value"]), f"信号 {name} 的阶段位宽或信号初值不一致")
        uses = [op for op in raw.children if ssa in op.operands]
        drives = [op for op in uses if op.name == "llhd.drv"]
        _require(len(drives) == 2, f"信号 {name} 必须恰有初始化和寄存器两个驱动")
        for op in uses:
            _require(op.name in {"llhd.drv", "llhd.prb"} and op.operands[0] == ssa and op.operands.count(ssa) == 1, "信号存在不支持的别名或其他用途")
            if op.name == "llhd.prb":
                _require(op.result is not None and len(op.operands) == 1 and re.fullmatch(rf":\s*\(!llhd.ref<i{width}>\)\s*->\s*i{width}", op.suffix) is not None, "信号读取的位宽或结构不匹配")
        for drive in drives:
            _drive(drive, width, definitions)
        constant_drives = [op for op in drives if _get(definitions, op.operands[1]).name == "hw.constant"]
        register_drives = [op for op in drives if _get(definitions, op.operands[1]).name == "seq.firreg"]
        _require(len(constant_drives) == len(register_drives) == 1, "双驱动必须是一个直接常量和一个直接寄存器")
        initial_drive, register_drive = constant_drives[0], register_drives[0]
        _require(_constant(_get(definitions, initial_drive.operands[1])) == (proof["initial_value"], width), f"信号 {name} 的 raw 初始化值与来源过程不一致")
        register = _get(definitions, register_drive.operands[1])
        clock, preset = _register(register, signal, definitions, inputs)
        _require(preset is None or preset == proof["initial_value"], f"信号 {name} 已有 preset 与一次初始化矛盾")
        clocks.add(clock)
        if preset is None:
            lines[register.line - 1], count = re.subn(
                rf"\}}>(?=\s*:\s*\(i{width},\s*!seq.clock\))",
                f", preset = {proof['initial_value']} : i{width}" + "}>",
                register.text,
            )
            _require(count == 1, "无法唯一定位寄存器属性，拒绝修改")
        lines[initial_drive.line - 1] = ""
        used.add(name)
        replacements.append({"signal_name": name, "width": width, "initial_value": proof["initial_value"], "signal_initial_value": signal["signal_initial_value"], "pre_process_line": proof["process_line"], "pre_signal": proof["ssa"], "raw_signal": ssa, "register": register.result, "register_line": register.line, "removed_driver_line": initial_drive.line, "clock_input": clock, "existing_preset": preset})
    _require(len(clocks) == 1, "受限转换只支持一个共同输入时钟")
    unmatched = []
    for name, proof in proofs.items():
        if name in used:
            continue
        _require(proof["initial_value"] == 0, f"非零初始化 {name} 在 raw HW 中未匹配，拒绝丢失初值")
        registers = [op for op in raw.children if op.name == "seq.firreg" and re.search(r'\bname\s*=\s*' + re.escape(json.dumps(name)), op.suffix)]
        _require(len(registers) == 1, f"未匹配初始化 {name} 缺少唯一同名寄存器")
        clock, preset = _register(registers[0], proof, definitions, inputs)
        _require(preset in (None, 0) and clock in clocks, f"未匹配初始化 {name} 不符合共同输入时钟和默认零初值策略")
        unmatched.append({"signal_name": name, "width": proof["width"], "initial_value": 0, "register": registers[0].result, "existing_preset": preset, "policy": "caller-declared-two-state-zero", "pre_process_line": proof["process_line"]})
    output = "".join(lines)
    sha = lambda value: hashlib.sha256(value.encode()).hexdigest()
    return output, {"schema_version": 1, "policy": POLICY, "module": _identity(raw)[0], "input_sha256": {"raw_hw_generic": sha(raw_hw_generic), "pre_llhd_generic": sha(pre_llhd_generic)}, "output_sha256": sha(output), "initial_processes": list(proofs.values()), "replacements": replacements, "unmatched_source_initials": unmatched, "requires_official_postprocessing": ["llhd-sig2reg", "canonicalize"], "caller_obligations": ["相同 RTL、参数及工具版本生成两个输入并保存哈希", "显式声明二态默认零初始化策略", "归一化后运行官方 verifier、sig2reg 和完整外部 VCD 对照"]}
