"""普通 Verilator 波形适配器，保留完整边沿 VCD 和辅助 CSV oracle 采样。"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

SAMPLE_PHASE = "low_before_posedge_pre_NBA"
VCD_TIMESCALE = "1ns"
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9]*\Z")


def _save(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _ports(manifest: dict, group: str) -> list[dict]:
    ports = manifest[group]
    names = []
    for port in ports:
        name, width = port["name"], port["width"]
        if not isinstance(name, str) or not _IDENTIFIER.fullmatch(name):
            raise ValueError(f"{group} 端口名称无法用于 C++ 驱动：{name!r}")
        if type(width) is not int or width < 1:
            raise ValueError(f"{name} 位宽必须为正整数：{width!r}")
        names.append(name)
    if len(set(names)) != len(names):
        raise ValueError(f"{group} 包含重复端口")
    return ports


def _capture(argv: list[str], work: Path, stage: str, timeout_s: float, commands: list[dict]) -> dict:
    """保存真实命令和完整日志；超时终止整个子进程组并继续向调用者抛出异常。"""
    record = {"stage": stage, "argv": argv, "command": shlex.join(argv), "cwd": str(work)}
    commands.append(record)
    _save(work / "commands.json", commands)
    begin = time.perf_counter()
    with (work / f"{stage}.stdout.log").open("wb") as stdout, (work / f"{stage}.stderr.log").open("wb") as stderr:
        try:
            process = subprocess.Popen(argv, cwd=work, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                record["exit_code"] = process.wait(timeout=timeout_s)
            except subprocess.TimeoutExpired:
                record["timed_out"] = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                record["exit_code"] = process.returncode
                raise
        except BaseException as error:
            record["error"] = f"{type(error).__name__}: {error}"
            raise
        finally:
            record["seconds"] = time.perf_counter() - begin
            _save(work / "commands.json", commands)
            (work / f"{stage}.log").write_bytes(
                (work / f"{stage}.stdout.log").read_bytes() + (work / f"{stage}.stderr.log").read_bytes()
            )
    if record["exit_code"]:
        raise subprocess.CalledProcessError(record["exit_code"], argv)
    return record


def _driver(inputs: list[dict], outputs: list[dict], clock: str, count: int) -> str:
    assignments = []
    for port in inputs:
        name, width = port["name"], port["width"]
        if name == clock:
            continue
        if width > 64:
            assignments.append(
                f"    for (unsigned lane = 0; lane < {(width + 31) // 32}; ++lane) "
                f"{{ if (!(stimulus >> std::hex >> dut.{name}[lane])) return 3; }}"
            )
        else:
            assignments.append(f"    if (!(stimulus >> std::hex >> value)) return 3; dut.{name} = value;")
    observations = []
    for index, port in enumerate(outputs):
        name, width = port["name"], port["width"]
        lanes = (
            [f"dut.{name}[{lane}]" for lane in range((width + 31) // 32)]
            if width > 64
            else [f"uint32_t(uint64_t(dut.{name}) >> {32 * lane})" for lane in range((width + 31) // 32)]
        )
        separator = '"\\n"' if index + 1 == len(outputs) else '","'
        observations.append(f'    output << decimal({{{", ".join(lanes)}}}) << {separator};')
    return (
        """// 自动生成：每个低/高电平事件求值后 dump VCD；低电平额外保存 CSV oracle 采样。
#include "Vcsvdut.h"
#include "verilated.h"
#include "verilated_vcd_c.h"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

// 按低 32 位 lane 在前的顺序转换任意宽度无符号值，避免 64 位截断。
static std::string decimal(std::vector<uint32_t> words) {
  std::string result;
  do {
    uint64_t carry = 0;
    for (size_t lane = words.size(); lane-- > 0;) {
      const uint64_t value = (carry << 32) | words[lane];
      words[lane] = uint32_t(value / 10);
      carry = value % 10;
    }
    result.push_back(char('0' + carry));
  } while (std::any_of(words.begin(), words.end(), [](uint32_t word) { return word != 0; }));
  std::reverse(result.begin(), result.end());
  return result;
}

int main(int argc, char **argv) {
  VerilatedContext context;
  context.commandArgs(argc, argv);
  context.randReset(0);
  context.traceEverOn(true);
  Vcsvdut dut{&context};
  VerilatedVcdC trace;
  dut.trace(&trace, 1);
  trace.open("trace.vcd");
  std::ifstream stimulus("stimulus.hex");
  std::ofstream output("output.csv");
  if (!stimulus || !output || !trace.isOpen()) return 2;
"""
        + f'  output << "{",".join(port["name"] for port in outputs)}\\n";\n'
        + f"""
  for (size_t sample = 0; sample < {count}; ++sample) {{
    dut.{clock} = 0;
    uint64_t value = 0;
"""
        + "\n".join(assignments)
        + """
    dut.eval();
    if (context.gotFinish()) return 4;
    trace.dump(context.time());
"""
        + "\n".join(observations)
        + f"""
    if (sample + 1 < {count}) {{
      context.timeInc(1);
      dut.{clock} = 1;
      dut.eval();
      if (context.gotFinish()) return 4;
      trace.dump(context.time());
      context.timeInc(1);
    }}
  }}
  std::string extra;
  if (stimulus >> extra) return 5;
  dut.final();
  trace.close();
  output.close();
  if (!output) return 6;
  return 0;
}}
"""
    )


def _validate_header(path: Path, inputs: list[dict], outputs: list[dict], clock: str) -> None:
    declarations = {}
    pattern = r"VL_(INOUT|IN|OUT)(?:8|16|64|W)?\s*\(\s*&?([\w]+)\s*,\s*(\d+)\s*,\s*(\d+)"
    for direction, name, msb, lsb in re.findall(pattern, path.read_text()):
        declarations[name] = (direction, abs(int(msb) - int(lsb)) + 1)
    required = [(port, "IN") for port in inputs] + [(port, "OUT") for port in outputs]
    if clock not in {port["name"] for port in inputs}:
        required.append(({"name": clock, "width": 1}, "IN"))
    for port, direction in required:
        actual = declarations.get(port["name"])
        if actual != (direction, port["width"]):
            raise ValueError(f"原生端口方向或位宽不一致：{port}，实际 {actual}")
    if {port["name"] for port, _ in required} != set(declarations):
        raise ValueError(f"manifest 必须覆盖全部原生端口：实际 {declarations}")


def run_native(
    manifest: dict, sources: list[Path], rows: list[dict[str, int | None]], work: Path, *, verilator: str | None = None
) -> dict:
    """运行普通二态原生仿真；成功仅表示产生全部输出，oracle 判定由 runner 单独执行。"""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    if any(work.iterdir()):
        raise FileExistsError(f"原生仿真要求独立空目录，拒绝覆盖证据：{work}")
    inputs, outputs = _ports(manifest, "inputs"), _ports(manifest, "outputs")
    top, clock = manifest["top"], manifest.get("clock", "clk")
    if not _IDENTIFIER.fullmatch(top) or not _IDENTIFIER.fullmatch(clock):
        raise ValueError("top/clock 必须为可用于 C++ 的普通标识符")
    if not outputs or not rows:
        raise ValueError("输出或 CSV 采样集合为空")
    if set(port["name"] for port in inputs) & set(port["name"] for port in outputs):
        raise ValueError("输入与输出名称重复")
    if any(port["name"] == clock and port["width"] != 1 for port in inputs):
        raise ValueError("时钟必须为 1 位")
    if manifest.get("sample_phase") != SAMPLE_PHASE:
        raise ValueError(f'不支持的原生采样契约：{manifest.get("sample_phase")}')
    timeout_s = float(manifest.get("timeout_s", 300))
    if timeout_s <= 0:
        raise ValueError("timeout_s 必须大于 0")
    sources = [path.resolve(strict=True) for path in sources]
    if not sources:
        raise ValueError("RTL 源文件列表为空")
    stimuli = []
    events = []
    for index, row in enumerate(rows):
        lanes = []
        event_inputs = {clock: 0}
        for port in inputs:
            name, width = port["name"], port["width"]
            if name == clock:
                continue
            if name not in row:
                raise ValueError(f"CSV 索引 {index} 缺少输入列 {name}")
            value = row[name]
            if type(value) is not int or not 0 <= value < 1 << width:
                raise ValueError(f"CSV 索引 {index} 的输入 {name} 超出 i{width} 或不是已定义整数：{value}")
            event_inputs[name] = value
            lanes.extend(
                [format((value >> (32 * lane)) & 0xFFFFFFFF, "x") for lane in range((width + 31) // 32)]
                if width > 64
                else [format(value, "x")]
            )
        stimuli.append(" ".join(lanes))
        events.append({"time": 2 * index, "inputs": event_inputs})
        if index + 1 < len(rows):
            events.append({"time": 2 * index + 1, "inputs": {**event_inputs, clock: 1}})
    (work / "stimulus.hex").write_text("\n".join(stimuli) + "\n")
    _save(work / "stimulus.json", {"schema_version": 1, "timescale": VCD_TIMESCALE, "events": events})
    (work / "driver.cpp").write_text(_driver(inputs, outputs, clock, len(rows)))
    _save(work / "inputs.json", rows)
    contract = {
        "sample_phase": SAMPLE_PHASE,
        "vcd_sample_phase": "every_event_after_eval",
        "clock": clock,
        "events": "每行 drive(clk=0, inputs) -> eval -> dump VCD 并读取 CSV；除最后一行外 drive(clk=1, 相同 inputs) -> eval -> dump VCD",
        "event_count": len(events),
        "vcd_timescale": VCD_TIMESCALE,
        "vcd_top": "TOP",
        "initialization": "Verilator 二态未初始化值为 0；保留 RTL 显式 initial/声明初始化，不额外插入 reset",
        "unknown_values": "原生 --x-initial 0/--x-assign 0；CSV 输入禁止 None/X/Z；输出 mask 由独立 oracle 比较处理",
        "time": "第 i 行 low 时间为 2*i ns，随后 high 为 (2*i+1) ns；最后一行只提交 low；无延迟 DUT 的精度统一为 1ns",
        "limitation": "低电平先更新输入再观察；组合输出可能不同于原 TB 输入 NBA 更新前的观测，须逐例核对原生 oracle",
        "inputs": inputs,
        "outputs": outputs,
        "manifest_initialization": manifest.get("initialization"),
    }
    _save(work / "sampling-contract.json", contract)
    requested_tool = verilator or os.environ.get("VERILATOR") or "verilator"
    verilator = shutil.which(requested_tool)
    if verilator is None:
        raise FileNotFoundError(f"找不到 Verilator：{requested_tool}")
    verilator = str(Path(verilator).absolute())
    commands: list[dict] = []
    _capture([verilator, "--version"], work, "version", timeout_s, commands)
    version = (work / "version.stdout.log").read_text().strip()
    _save(work / "versions.json", {"verilator": version, "verilator_path": verilator})
    arguments = [
        verilator,
        "--cc",
        "--exe",
        "--build",
        "--timing",
        "--trace",
        "-Wno-fatal",
        "--x-initial",
        "0",
        "--x-assign",
        "0",
        "--top-module",
        top,
        "--prefix",
        "Vcsvdut",
        "--Mdir",
        str(work / "obj"),
        "-o",
        "sim",
        "--timescale-override",
        "1ns/1ns",
    ]
    for name, value in manifest.get("parameters", {}).items():
        if not _IDENTIFIER.fullmatch(name) or not isinstance(value, (int, str)):
            raise ValueError(f"参数格式无效：{name!r}={value!r}")
        arguments.append(f"-G{name}={value}")
    arguments.extend(manifest.get("verilator_args", []))
    arguments.extend(str(path) for path in sources)
    arguments.append(str(work / "driver.cpp"))
    build = _capture(arguments, work, "build", timeout_s, commands)
    _validate_header(work / "obj/Vcsvdut.h", inputs, outputs, clock)
    execution = _capture([str(work / "obj/sim")], work, "run", timeout_s, commands)
    begin = time.perf_counter()
    with (work / "output.csv").open() as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != [port["name"] for port in outputs]:
            raise ValueError(f"原生输出列与 manifest 不一致：{reader.fieldnames}")
        actual_rows = []
        for index, row in enumerate(reader):
            if set(row) != set(reader.fieldnames) or any(value is None for value in row.values()):
                raise ValueError(f"原生 CSV 索引 {index} 缺列或多列")
            actual = {name: int(value) for name, value in row.items()}
            for port in outputs:
                if not 0 <= actual[port["name"]] < 1 << port["width"]:
                    raise ValueError(f"原生输出位宽不匹配：索引 {index}，{port}")
            actual_rows.append(actual)
    if len(actual_rows) != len(rows):
        raise ValueError(f"原生输出采样数不一致：{len(actual_rows)} != {len(rows)}")
    vcd_path = work / "trace.vcd"
    if not vcd_path.is_file() or not vcd_path.stat().st_size:
        raise ValueError("原生仿真未产生非空 VCD 波形")
    result = {
        "status": "pass",
        "status_meaning": "原生构建和执行完成；尚未判定 oracle",
        "samples": actual_rows,
        "rows": actual_rows,
        "sample_count": len(actual_rows),
        "event_count": len(events),
        "vcd": str(vcd_path),
        "vcd_sha256": hashlib.sha256(vcd_path.read_bytes()).hexdigest(),
        "vcd_top": "TOP",
        "stimulus_json": str(work / "stimulus.json"),
        "output_csv": str(work / "output.csv"),
        "timings": {
            "build": build["seconds"],
            "execution": execution["seconds"],
            "read_compare": time.perf_counter() - begin,
        },
        "versions": {"verilator": version, "verilator_path": verilator},
        "sampling_contract": contract,
    }
    _save(work / "result.json", result)
    return result
