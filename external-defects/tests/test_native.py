"""验证真实 Verilator 的完整边沿 VCD、原 TB 采样一致性与宽端口。"""

import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("external_defects_native", ROOT / "native.py")
assert SPEC is not None and SPEC.loader is not None
NATIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NATIVE)


def _read_top_vcd(path: Path) -> tuple[set[str], dict[int, dict[str, int]]]:
    """只读取真实 Verilator 工件中的顶层二态值，按事件保留未变化的信号。"""
    contents = path.read_text()
    assert re.search(r"\$timescale\s+1ns\s+\$end", contents)
    header, body = contents.split("$enddefinitions $end", 1)
    scope = []
    names = {}
    for line in header.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "$scope":
            scope.append(parts[2])
        elif parts[0] == "$upscope":
            scope.pop()
        elif parts[0] == "$var" and scope == ["TOP"]:
            names.setdefault(parts[3], []).append(parts[4])
    frames = {}
    values = {}
    timestamp = None
    for line in body.splitlines():
        if not line or line.startswith("$"):
            continue
        if line.startswith("#"):
            if timestamp is not None:
                frames[timestamp] = dict(values)
            timestamp = int(line[1:])
            continue
        if line[0] in "bB":
            value, code = line[1:].split()
        elif line[0] in "01xXzZ":
            value, code = line[0], line[1:]
        else:
            continue
        if code in names:
            assert set(value) <= {"0", "1"}, f"顶层信号出现未知值：{line}"
            values.update({name: int(value, 2) for name in names[code]})
    if timestamp is not None:
        frames[timestamp] = dict(values)
    return {name for aliases in names.values() for name in aliases}, frames


def _check_vcd_inputs(result: dict, manifest: dict, rows: list[dict]) -> dict[int, dict[str, int]]:
    path = Path(result["vcd"])
    assert result["vcd_top"] == "TOP"
    assert result["vcd_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    port_names, frames = _read_top_vcd(path)
    expected_ports = {port["name"] for port in manifest["inputs"] + manifest["outputs"]}
    assert port_names == expected_ports
    assert list(frames) == list(range(2 * len(rows) - 1))
    assert result["event_count"] == len(frames)
    stimulus = json.loads(Path(result["stimulus_json"]).read_text())
    assert stimulus["schema_version"] == 1
    assert stimulus["timescale"] == "1ns"
    expected_events = []
    for timestamp, frame in frames.items():
        inputs = {
            port["name"]: rows[timestamp // 2][port["name"]]
            for port in manifest["inputs"]
            if port["name"] != "clk"
        }
        inputs["clk"] = timestamp % 2
        assert {name: frame[name] for name in inputs} == inputs
        expected_events.append({"time": timestamp, "inputs": inputs})
    assert stimulus["events"] == expected_events
    return frames


def _d13_paths() -> dict:
    return json.loads((ROOT / "manifests/d13.json").read_text())


def _d13_manifest() -> dict:
    return {
        "top": "axis_frame_len",
        "clock": "clk",
        "inputs": [
            {"name": name, "width": width}
            for name, width in [
                ("clk", 1),
                ("rst", 1),
                ("monitor_axis_tkeep", 8),
                ("monitor_axis_tvalid", 1),
                ("monitor_axis_tready", 1),
                ("monitor_axis_tlast", 1),
            ]
        ],
        "outputs": [{"name": "frame_len", "width": 16}, {"name": "frame_len_valid", "width": 1}],
        "sample_phase": NATIVE.SAMPLE_PHASE,
        "timeout_s": 60,
    }


@pytest.mark.skipif(shutil.which(os.environ.get("VERILATOR", "verilator")) is None, reason="未安装 Verilator")
@pytest.mark.parametrize("variant", ["golden", "buggy"])
def test_d13_matches_original_tb(tmp_path: Path, variant: str) -> None:
    """两版适配器全轨迹必须等于独立执行原样 TB 得到的输出。"""
    manifest = _d13_paths()
    with (ROOT / manifest["csv"]).open() as handle:
        rows = [
            {key: int(value) for key, value in row.items()} for row in csv.DictReader(handle, skipinitialspace=True)
        ]
    native_path = ROOT / "evidence/d13/native-independent" / variant / "output.csv"
    with native_path.open() as handle:
        expected = [
            {key: int(value) for key, value in row.items() if key in {"frame_len", "frame_len_valid"}}
            for row in csv.DictReader(handle, skipinitialspace=True)
        ]
    filename = manifest["golden_sources"][0] if variant == "golden" else manifest["bug_source"]
    result = NATIVE.run_native(_d13_manifest(), [ROOT / filename], rows, tmp_path / variant)
    assert result["samples"] == expected
    assert len(result["samples"]) == 6
    frames = _check_vcd_inputs(result, _d13_manifest(), rows)
    # VCD low 采样等于原 TB；high 必须已体现该边沿完成后的寄存器输出。
    for index, sample in enumerate(expected):
        assert {name: frames[2 * index][name] for name in sample} == sample
        if index + 1 < len(expected):
            assert {name: frames[2 * index + 1][name] for name in sample} == expected[index + 1]


@pytest.mark.skipif(shutil.which(os.environ.get("VERILATOR", "verilator")) is None, reason="未安装 Verilator")
def test_wide_ports_and_pre_edge_observation(tmp_path: Path) -> None:
    """96 位输入/输出不能截成 64 位；组合输出观察当行输入，寄存器观察前一上升沿。"""
    source = tmp_path / "wide.sv"
    source.write_text(
        "module wide(input clk, input [95:0] d, output [95:0] immediate, output reg [95:0] q = 0);\n"
        "assign immediate = d; always @(posedge clk) q <= d; endmodule\n"
    )
    manifest = {
        "top": "wide",
        "clock": "clk",
        "sample_phase": NATIVE.SAMPLE_PHASE,
        "inputs": [{"name": "clk", "width": 1}, {"name": "d", "width": 96}],
        "outputs": [{"name": "immediate", "width": 96}, {"name": "q", "width": 96}],
        "timeout_s": 60,
    }
    values = [(1 << 95) | (1 << 65) | 123, (1 << 96) - 1, 0]
    result = NATIVE.run_native(manifest, [source], [{"d": value} for value in values], tmp_path / "work")
    assert result["samples"] == [
        {"immediate": values[0], "q": 0},
        {"immediate": values[1], "q": values[0]},
        {"immediate": 0, "q": values[1]},
    ]
    frames = _check_vcd_inputs(result, manifest, [{"d": value} for value in values])
    assert [(frame["immediate"], frame["q"]) for frame in frames.values()] == [
        (values[0], 0),
        (values[0], values[0]),
        (values[1], values[0]),
        (values[1], values[1]),
        (0, values[1]),
    ]
    records = json.loads((tmp_path / "work/commands.json").read_text())
    assert [record["stage"] for record in records] == ["version", "build", "run"]
    assert all(record["exit_code"] == 0 for record in records)


@pytest.mark.parametrize("bad_value", [None, -1, 256])
def test_rejects_undefined_or_out_of_width_input(tmp_path: Path, bad_value: int | None) -> None:
    manifest = _d13_manifest()
    row = {
        "rst": 0,
        "monitor_axis_tkeep": bad_value,
        "monitor_axis_tvalid": 0,
        "monitor_axis_tready": 0,
        "monitor_axis_tlast": 0,
    }
    with pytest.raises(ValueError, match="超出 i8"):
        NATIVE.run_native(manifest, [ROOT / _d13_paths()["golden_sources"][0]], [row], tmp_path / "work")


def test_rejects_missing_input(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="缺少输入列 rst"):
        NATIVE.run_native(_d13_manifest(), [ROOT / _d13_paths()["golden_sources"][0]], [{}], tmp_path / "work")


@pytest.mark.parametrize("explicit", [False, True])
def test_verilator_is_selected_at_runtime_with_explicit_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, explicit: bool
) -> None:
    environment_tool, explicit_tool = tmp_path / "environment-verilator", tmp_path / "selected-verilator"
    for path in (environment_tool, explicit_tool):
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
    monkeypatch.setenv("VERILATOR", str(environment_tool))
    chosen = explicit_tool if explicit else environment_tool
    captured = []

    def capture(argv, *args):
        captured.append(argv)
        raise RuntimeError("已记录工具选择，无需调用编译器")

    monkeypatch.setattr(NATIVE, "_capture", capture)
    row = {
        "rst": 0,
        "monitor_axis_tkeep": 1,
        "monitor_axis_tvalid": 0,
        "monitor_axis_tready": 0,
        "monitor_axis_tlast": 0,
    }
    with pytest.raises(RuntimeError, match="已记录工具选择"):
        NATIVE.run_native(
            _d13_manifest(),
            [ROOT / _d13_paths()["golden_sources"][0]],
            [row],
            tmp_path / "work",
            verilator=str(explicit_tool) if explicit else None,
        )
    assert captured == [[str(chosen), "--version"]]
