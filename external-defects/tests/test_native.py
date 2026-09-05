"""验证原 TB 采样一致性、宽端口以及拒绝丢失输入的行为。"""

import csv
import importlib.util
import json
import os
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("external_defects_native", ROOT / "native.py")
assert SPEC is not None and SPEC.loader is not None
NATIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NATIVE)


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
