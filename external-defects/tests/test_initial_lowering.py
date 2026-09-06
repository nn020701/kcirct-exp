"""一次初始化转换必须有来源证明；非零值及拒绝路径使用小型 IR。"""

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("external_defects_initial_lowering", ROOT / "initial_lowering.py")
assert SPEC is not None and SPEC.loader is not None
LOWERING = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LOWERING
SPEC.loader.exec_module(LOWERING)


def _module(body: str) -> str:
    return '''"builtin.module"() ({
  "hw.module"() <{module_type = !hw.modty<input clk : i1, input data : i4, output q : i4>, parameters = [], sym_name = "test"}> ({
  ^bb0(%arg0: i1, %arg1: i4):
''' + body + '''
  }) : () -> ()
}) : () -> ()
'''


TIME = '    %time = "llhd.constant_time"() <{value = #llhd.time<0ns, 0d, 1e>}> : () -> !llhd.time\n'
ZERO = '    %zero = "hw.constant"() <{value = 0 : i4}> : () -> i4\n'
SIGNAL = '    %sig = "llhd.sig"(%zero) <{name = "q"}> : (i4) -> !llhd.ref<i4>\n'
CLOCK = '    %clock = "seq.to_clock"(%arg0) : (i1) -> !seq.clock\n'
REG = '    %reg = "seq.firreg"(%arg1, %clock) <{name = "q"}> : (i4, !seq.clock) -> i4\n'
DYNAMIC = '    "llhd.drv"(%sig, %reg, %time) : (!llhd.ref<i4>, i4, !llhd.time) -> ()\n'
INITIAL = '    "llhd.drv"(%sig, %init, %time) : (!llhd.ref<i4>, i4, !llhd.time) -> ()\n'
HALT = '      "llhd.halt"() : () -> ()\n'
READ = '    %read = "llhd.prb"(%sig) : (!llhd.ref<i4>) -> i4\n'
OUTPUT = '    "hw.output"(%read) : (i4) -> ()\n'


def _fixture(value: int = 5, *, local: bool = False) -> tuple[str, str]:
    constant = f'    %init = "hw.constant"() <{{value = {value} : i4}}> : () -> i4\n'
    raw = _module(TIME + ZERO + constant + SIGNAL + CLOCK + REG + DYNAMIC + INITIAL + READ + OUTPUT)
    process = '    "llhd.process"() ({\n' + (constant + TIME if local else "") + INITIAL + HALT + '    }) : () -> ()\n'
    pre = _module(ZERO + ("" if local else TIME + constant) + SIGNAL + process + READ + OUTPUT)
    return raw, pre


def _normalize(raw: str, pre: str):
    return LOWERING.normalize_initial_registers(raw, pre)


@pytest.mark.parametrize("value", [0, 5, 15, -1, -8])
@pytest.mark.parametrize("local", [False, True])
def test_preserves_nonzero_bit_pattern_and_only_removes_proven_driver(value, local):
    raw, pre = _fixture(value, local=local)
    output, report = _normalize(raw, pre)
    expected = raw.replace(INITIAL, "").replace('name = "q"}> : (i4, !seq.clock)', f'name = "q", preset = {value & 15} : i4}}> : (i4, !seq.clock)')
    assert output == expected
    assert DYNAMIC in output and SIGNAL in output and READ in output
    assert report["replacements"][0]["initial_value"] == value & 15
    assert report["replacements"][0]["width"] == 4
    assert len(report["initial_processes"]) == 1
    assert report["unmatched_source_initials"] == []
    assert report["input_sha256"] == {"raw_hw_generic": hashlib.sha256(raw.encode()).hexdigest(), "pre_llhd_generic": hashlib.sha256(pre.encode()).hexdigest()}
    assert report["output_sha256"] == hashlib.sha256(output.encode()).hexdigest()


def test_compatible_existing_preset_is_not_duplicated():
    raw, pre = _fixture(-1)
    raw = raw.replace('name = "q"}> : (i4, !seq.clock)', 'preset = -1 : i4, name = "q"}> : (i4, !seq.clock)')
    output, report = _normalize(raw, pre)
    assert output == raw.replace(INITIAL, "")
    assert output.count("preset") == 1
    assert report["replacements"][0]["existing_preset"] == 15


def test_debug_locations_and_comments_are_preserved():
    raw, pre = _fixture()
    raw = '#loc = loc("fixture.sv":2:3)\n' + raw.replace(' -> i4\n', ' -> i4 loc(#loc) // 原始位置\n')
    pre = '#loc = loc("fixture.sv":2:3)\n' + pre.replace(' -> ()\n', ' -> () loc(#loc)\n')
    output, _ = _normalize(raw, pre)
    assert '#loc = loc("fixture.sv":2:3)' in output
    assert 'preset = 5 : i4}> : (i4, !seq.clock) -> i4 loc(#loc) // 原始位置' in output


def _with_eliminated(raw: str, pre: str, value: int = 0, preset: int | None = None):
    constant = f'    %extra_init = "hw.constant"() <{{value = {value} : i4}}> : () -> i4\n'
    signal = '    %extra = "llhd.sig"(%zero) <{name = "done"}> : (i4) -> !llhd.ref<i4>\n'
    process = '    "llhd.process"() ({\n' + INITIAL.replace("%sig", "%extra").replace("%init", "%extra_init") + HALT + '    }) : () -> ()\n'
    attrs = 'name = "done"' + ("" if preset is None else f", preset = {preset} : i4")
    reg = f'    %done = "seq.firreg"(%arg1, %clock) <{{{attrs}}}> : (i4, !seq.clock) -> i4\n'
    return raw.replace(OUTPUT, reg + OUTPUT), pre.replace(OUTPUT, constant + signal + process + OUTPUT)


@pytest.mark.parametrize("preset", [None, 0])
def test_eliminated_zero_initial_requires_same_name_width_register(preset):
    raw, pre = _with_eliminated(*_fixture(), preset=preset)
    output, report = _normalize(raw, pre)
    assert '%done = "seq.firreg"' in output
    assert report["unmatched_source_initials"] == [{"signal_name": "done", "width": 4, "initial_value": 0, "register": "%done", "existing_preset": preset, "policy": "caller-declared-two-state-zero", "pre_process_line": next(i for i, line in enumerate(pre.splitlines(), 1) if '"llhd.drv"(%extra' in line) - 1}]


@pytest.mark.parametrize("value,preset,mutation", [
    (3, None, lambda raw: raw),
    (0, 2, lambda raw: raw),
    (0, None, lambda raw: raw.replace('name = "done"', 'name = "other"')),
    (0, None, lambda raw: raw.replace('name = "done"}> : (i4, !seq.clock) -> i4', 'name = "done"}> : (i3, !seq.clock) -> i3')),
])
def test_unmatched_initial_cannot_silently_disappear(value, preset, mutation):
    raw, pre = _with_eliminated(*_fixture(), value=value, preset=preset)
    with pytest.raises(LOWERING.InitialLoweringError):
        _normalize(mutation(raw), pre)


@pytest.mark.parametrize("mutation", [
    lambda pre: pre.replace(HALT, ''),
    lambda pre: pre.replace(HALT, '      "llhd.wait"() : () -> ()\n' + HALT),
    lambda pre: pre.replace(HALT, '      "cf.br"() [^bb1] : () -> ()\n' + HALT),
    lambda pre: pre.replace(HALT, '      "test.side_effect"() : () -> ()\n' + HALT),
    lambda pre: pre.replace(INITIAL, INITIAL + INITIAL),
    lambda pre: pre.replace(INITIAL, INITIAL.replace('%init', '%arg1')),
    lambda pre: pre.replace('0ns, 0d, 1e', '1ns, 0d, 1e'),
    lambda pre: pre.replace('0ns, 0d, 1e', '0ns, 1d, 1e'),
    lambda pre: pre.replace('0ns, 0d, 1e', '0ns, 0d, 0e'),
    lambda pre: pre.replace(INITIAL, INITIAL.replace('%time)', '%time, %arg0)').replace('!llhd.time)', '!llhd.time, i1)')),
    lambda pre: pre.replace('name = "q"', 'name = "other"'),
    lambda pre: pre.replace('value = 5 : i4', 'value = 6 : i4'),
    lambda pre: pre.replace('value = 0 : i4', 'value = 1 : i4'),
    lambda pre: pre.replace(INITIAL, INITIAL.replace('!llhd.ref<i4>', '!llhd.ref<i3>')),
    lambda pre: pre.replace('value = 5 : i4}> : () -> i4', 'value = 5 : i3}> : () -> i4'),
    lambda pre: pre.replace('sym_name = "test"', 'sym_name = "other"'),
    lambda pre: pre.replace('parameters = []', 'parameters = [1 : i32]'),
    lambda pre: pre.replace('input data : i4', 'input data : i3'),
    lambda pre: pre.replace('    "llhd.process"() ({', '    "llhd.process"() ({\n    ^bb1:'),
])
def test_rejects_unproven_or_inconsistent_source_initial(mutation):
    raw, pre = _fixture()
    with pytest.raises(LOWERING.InitialLoweringError):
        _normalize(raw, mutation(pre))


@pytest.mark.parametrize("mutation", [
    lambda raw: raw.replace(INITIAL, ''),
    lambda raw: raw.replace(DYNAMIC, ''),
    lambda raw: raw.replace(INITIAL, INITIAL + INITIAL),
    lambda raw: raw.replace(DYNAMIC, DYNAMIC.replace('%reg', '%init')),
    lambda raw: raw.replace(DYNAMIC, DYNAMIC.replace('%reg', '%arg1')),
    lambda raw: raw.replace(REG, REG.replace('name = "q"', 'name = "other"')),
    lambda raw: raw.replace(REG, REG.replace('name = "q"', 'name = "q", preset = 2 : i4')),
    lambda raw: raw.replace(REG, REG.replace('name = "q"', 'name = "q", isAsync')),
    lambda raw: raw.replace(REG, REG.replace('(i4, !seq.clock)', '(i3, !seq.clock)')),
    lambda raw: raw.replace(CLOCK, CLOCK.replace('%arg0)', '%arg_missing)')),
    lambda raw: raw.replace(CLOCK, CLOCK.replace('%arg0)', '%arg1)')),
    lambda raw: raw.replace(CLOCK, CLOCK.replace('%arg0)', '%zero)')),
    lambda raw: raw.replace(INITIAL, INITIAL.replace('%time)', '%time, %arg0)').replace('!llhd.time)', '!llhd.time, i1)')),
    lambda raw: raw.replace('0ns, 0d, 1e', '0ns, 1d, 0e'),
    lambda raw: raw.replace(READ, READ.replace('-> i4', '-> i3')),
    lambda raw: raw.replace(OUTPUT, '    "test.alias"(%sig) : (!llhd.ref<i4>) -> ()\n' + OUTPUT),
    lambda raw: raw.replace(OUTPUT, '    "llhd.wait"() : () -> ()\n' + OUTPUT),
    lambda raw: raw.replace(SIGNAL, ''),
    lambda raw: raw.replace('%arg1: i4', '%arg1: i3'),
])
def test_rejects_unsupported_raw_driver_shapes(mutation):
    raw, pre = _fixture()
    with pytest.raises(LOWERING.InitialLoweringError):
        _normalize(mutation(raw), pre)


def test_duplicate_source_initial_and_duplicate_register_identity_rejected():
    raw, pre = _fixture()
    process = '    "llhd.process"() ({\n' + INITIAL + HALT + '    }) : () -> ()\n'
    with pytest.raises(LOWERING.InitialLoweringError, match="多个一次初始化"):
        _normalize(raw, pre.replace(process, process + process))
    raw, pre = _with_eliminated(raw, pre)
    duplicate = '    %done2 = "seq.firreg"(%arg1, %clock) <{name = "done"}> : (i4, !seq.clock) -> i4\n'
    with pytest.raises(LOWERING.InitialLoweringError, match="寄存器名称重复"):
        _normalize(raw.replace(OUTPUT, duplicate + OUTPUT), pre)


@pytest.mark.parametrize("value,literal", [(0, "false"), (1, "true")])
def test_boolean_initial_and_existing_boolean_preset(value, literal):
    raw, pre = _fixture(value)
    raw = raw.replace("i4", "i1").replace("value = 0 : i1", "value = false").replace(f"value = {value} : i1", f"value = {literal}")
    pre = pre.replace("i4", "i1").replace("value = 0 : i1", "value = false").replace(f"value = {value} : i1", f"value = {literal}")
    raw = raw.replace('name = "q"}> : (i1, !seq.clock)', f'name = "q", preset = {literal}}}> : (i1, !seq.clock)')
    output, report = _normalize(raw, pre)
    assert f"preset = {literal}" in output
    assert report["replacements"][0]["initial_value"] == value
    assert report["replacements"][0]["existing_preset"] == value
