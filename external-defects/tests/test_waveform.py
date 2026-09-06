"""防止必需端口、上升沿变化或尾部时间窗口被 VCD 比对静默略过。"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("external_defects_waveform", ROOT / "waveform.py")
assert SPEC is not None and SPEC.loader is not None
WAVEFORM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WAVEFORM)
KCIRCT_ROOT = Path(os.environ.get("KCIRCT_ROOT", ROOT.parents[1] / "circt-semantics"))
DIFFVCD = KCIRCT_ROOT / "scripts/diffvcd.py"
PORTS = [{"name": "clk", "width": 1}, {"name": "q", "width": 8}]
TIMES = [0, 1, 2]


def write_vcd(
    path: Path,
    *,
    top: str = "dut",
    q: list[tuple[int, str]] | None = None,
    width: int = 8,
    missing: bool = False,
    extra: bool = False,
    end: int = 2,
    timescale: str = "1ns",
    q_range: str | None = None,
) -> Path:
    signals = [("clk", 1, [(0, "0"), (1, "1"), (2, "0")])]
    if not missing:
        signals.append(("q", width, [(0, "00000001")] if q is None else q))
    if extra:
        signals.append(("unused", 1, [(0, "1")]))
    lines = [f"$timescale {timescale} $end"]
    lines += [f"$scope module {part} $end" for part in top.split(".")]
    for index, (name, size, _) in enumerate(signals):
        suffix = f" [{size - 1}:0]" if size > 1 else ""
        if name == "q" and q_range is not None:
            suffix = " " + q_range
        lines.append(f"$var wire {size} {chr(33 + index)} {name}{suffix} $end")
    lines += ["$upscope $end"] * len(top.split("."))
    lines += ["$enddefinitions $end"]
    for time in range(end + 1):
        lines.append(f"#{time}")
        for index, (_, size, transitions) in enumerate(signals):
            for event_time, value in transitions:
                if event_time == time:
                    identifier = chr(33 + index)
                    lines.append(value + identifier if size == 1 else f"b{value} {identifier}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def compare(tmp_path: Path, first: Path, second: Path) -> dict:
    return WAVEFORM.compare_waveforms(
        first, second, top="dut", native_top="TOP.csvdut", ports=PORTS, times=TIMES,
        work=tmp_path / "comparison", diffvcd_path=DIFFVCD,
    )


def test_all_ports_and_events_use_real_external_diffvcd(tmp_path: Path) -> None:
    result = compare(tmp_path, write_vcd(tmp_path / "k.vcd"), write_vcd(tmp_path / "n.vcd", top="TOP.csvdut", extra=True))
    assert result["agrees"] is True
    assert result["exit_code"] == 0
    assert result["compared_signals"] == 2
    assert result["event_count"] == 3
    assert not result["errors"]
    command = json.loads(Path(result["artifacts"]["command"]["path"]).read_text())["argv"]
    assert command[1] == str(DIFFVCD.resolve())
    assert command.count("--filter") == 1
    assert "--ignore-missing-signals" not in command
    assert "2 filtered and unignored signals" in Path(result["artifacts"]["stderr"]["path"]).read_text()
    assert all(len(record["sha256"]) == 64 for record in result["artifacts"].values())


@pytest.mark.parametrize(
    "changes,diagnostic",
    [
        ({"missing": True}, "必需顶层端口"),
        ({"q": []}, "没有确定的二态值"),
        ({"q": [(1, "00000001")]}, "时刻 0"),
        ({"q": [(0, "xxxxxxxx")]}, "没有确定的二态值"),
        ({"width": 4}, "位宽应为 i8"),
        ({"end": 1}, "未完整覆盖"),
        ({"end": 3}, "必须等于完整事件窗口"),
        ({"timescale": "1ps"}, "时间单位必须为 1ns"),
    ],
)
def test_rejects_incomplete_or_invalid_required_waveform(tmp_path: Path, changes: dict, diagnostic: str) -> None:
    result = compare(tmp_path, write_vcd(tmp_path / "k.vcd", **changes), write_vcd(tmp_path / "n.vcd", top="TOP.csvdut"))
    assert result["agrees"] is False
    assert result["compared_signals"] == 0
    assert result["exit_code"] is None
    assert diagnostic in result["errors"][0]
    assert "command" not in result


def test_high_only_mismatch_cannot_pass_low_sampling_oracle(tmp_path: Path) -> None:
    first = write_vcd(tmp_path / "k.vcd", q=[(0, "00000001"), (1, "00000011"), (2, "00000001")])
    second = write_vcd(tmp_path / "n.vcd", top="TOP.csvdut")
    assert WAVEFORM.read_samples(first, "dut", PORTS, [0, 2]) == WAVEFORM.read_samples(second, "TOP.csvdut", PORTS, [0, 2])
    result = compare(tmp_path, first, second)
    assert result["agrees"] is False
    assert result["exit_code"] == 1
    assert result["first_mismatch"] == {"time": 1, "event_index": 1, "signal": "q", "expected": 1, "actual": 3}
    assert "1  3  1  q[7:0]" in Path(result["artifacts"]["stdout"]["path"]).read_text()


def test_read_samples_validates_required_outputs(tmp_path: Path) -> None:
    path = write_vcd(tmp_path / "k.vcd", q=[(0, "xxxxxxxx")])
    with pytest.raises(ValueError, match="没有确定的二态值"):
        WAVEFORM.read_samples(path, "dut", PORTS, [0, 2])


def test_comparison_rejects_skipping_clock_events(tmp_path: Path) -> None:
    result = WAVEFORM.compare_waveforms(
        write_vcd(tmp_path / "k.vcd"), write_vcd(tmp_path / "n.vcd", top="TOP.csvdut"),
        top="dut", native_top="TOP.csvdut", ports=PORTS, times=[0, 2], work=tmp_path / "comparison", diffvcd_path=DIFFVCD,
    )
    assert result["agrees"] is False
    assert "每个 low/high 事件" in result["errors"][0]


def test_internal_names_cannot_substitute_for_missing_top_port(tmp_path: Path) -> None:
    result = compare(tmp_path, write_vcd(tmp_path / "k.vcd", top="dut.inner"), write_vcd(tmp_path / "n.vcd", top="TOP.csvdut"))
    assert result["agrees"] is False
    assert "必需顶层端口 dut.clk" in result["errors"][0]


@pytest.mark.parametrize("vector_backend", ["kimulator", "native"])
@pytest.mark.parametrize("high_mismatch", [False, True])
def test_scalar_and_zero_range_keep_signal_in_real_external_diff(
    tmp_path: Path, vector_backend: str, high_mismatch: bool
) -> None:
    """S3 的 1 位端口允许等价声明，但该端口仅在高相位不同也必须失败。"""
    ports = [{"name": "clk", "width": 1}, {"name": "q", "width": 1}]
    first = write_vcd(
        tmp_path / "k.vcd", width=1, q=[(0, "0"), (1, "1" if high_mismatch else "0"), (2, "0")],
        q_range="[0:0]" if vector_backend == "kimulator" else None,
    )
    second = write_vcd(
        tmp_path / "n.vcd", top="TOP.csvdut", width=1, q=[(0, "0")],
        q_range="[0:0]" if vector_backend == "native" else None,
    )
    vector = first if vector_backend == "kimulator" else second
    # 内部同名声明不能跟着顶层端口一起改名。
    vector.write_bytes(vector.read_bytes().replace(
        b"$upscope $end",
        b"$scope module extra $end\n$var wire 1 z q [0:0] $end\n$upscope $end\n$upscope $end",
        1,
    ))
    before = {path: path.read_bytes() for path in (first, second)}
    result = WAVEFORM.compare_waveforms(
        first, second, top="dut", native_top="TOP.csvdut", ports=ports, times=TIMES,
        work=tmp_path / "comparison", diffvcd_path=DIFFVCD,
    )
    assert not result["errors"]
    assert result["agrees"] is not high_mismatch
    assert result["exit_code"] == int(high_mismatch)
    assert result["compared_signals"] == 2
    assert "2 filtered and unignored signals" in Path(result["artifacts"]["stderr"]["path"]).read_text()
    if high_mismatch:
        assert result["first_mismatch"] == {"time": 1, "event_index": 1, "signal": "q", "expected": 0, "actual": 1}
        assert "1  1  0  q" in Path(result["artifacts"]["stdout"]["path"]).read_text()
    else:
        assert result["first_mismatch"] is None
    normalized = Path(result["artifacts"][vector_backend + "_comparison_vcd"]["path"])
    mapping = json.loads(Path(result["artifacts"]["normalization_map"]["path"]).read_text())
    record = mapping["files"][vector_backend]
    assert mapping["policy"] == "scalar-equals-i1-zero-range-v1"
    assert result["normalization"]["applied"] is True
    assert len(mapping["mappings"]) == 1
    assert mapping["mappings"][0]["port"] == "q"
    assert record["source"]["sha256"] == result["artifacts"][vector_backend + "_vcd"]["sha256"]
    assert record["body_unchanged"] is True
    assert normalized.read_bytes().split(b"$enddefinitions $end", 1)[1] == before[vector].split(b"$enddefinitions $end", 1)[1]
    assert b"$var wire 1 z q [0:0] $end" in normalized.read_bytes()
    assert all(path.read_bytes() == original for path, original in before.items())
    command = json.loads(Path(result["artifacts"]["command"]["path"]).read_text())["argv"]
    assert str(normalized.resolve()) in command
    assert command.count("--filter") == 1
    assert "--ignore-missing-signals" not in command


@pytest.mark.parametrize("width,range_text", [(1, "[1:1]"), (8, "[0:0]")])
def test_normalization_rejects_other_ranges_or_widths(tmp_path: Path, width: int, range_text: str) -> None:
    ports = [{"name": "clk", "width": 1}, {"name": "q", "width": width}]
    result = WAVEFORM.compare_waveforms(
        write_vcd(tmp_path / "k.vcd", width=width, q=[(0, "0")], q_range=""),
        write_vcd(tmp_path / "n.vcd", top="TOP.csvdut", width=width, q=[(0, "0")], q_range=range_text),
        top="dut", native_top="TOP.csvdut", ports=ports, times=TIMES,
        work=tmp_path / "comparison", diffvcd_path=DIFFVCD,
    )
    assert result["agrees"] is False
    assert "声明形式不一致" in result["errors"][0]
    assert result["exit_code"] is None
    assert "normalization_map" not in result["artifacts"]
