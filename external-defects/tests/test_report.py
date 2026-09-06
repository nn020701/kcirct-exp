"""验证报告可以保留真实失败，并且不把旧批次证据误归给新运行。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "external_defects_report", Path(__file__).resolve().parents[1] / "report.py"
)
assert SPEC is not None and SPEC.loader is not None
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


@pytest.fixture
def report_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(REPORT, "ROOT", tmp_path)
    monkeypatch.setattr(REPORT, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(REPORT, "RUNS", tmp_path / ".runs")
    return tmp_path


def test_configuration_failure_preserves_unknown_samples_and_replaces_selection(
    report_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """配置失败没有 samples，仍须可报告且不能留下上次正式集合的案例文件。"""
    REPORT.save(
        report_root / ".runs/new/results.json",
        [
            {
                "source_case_id": "TOY",
                "variant_id": "bad",
                "status": "validation_error",
            },
            {
                "source_case_id": "OK",
                "variant_id": "ok",
                "status": "pass",
                "samples": 2,
            },
        ],
    )
    REPORT.save(report_root / "results/cases/stale.json", {"variant_id": "stale"})
    monkeypatch.setattr(sys, "argv", ["report.py", "--runs", "new"])
    REPORT.main()
    summary = json.loads((report_root / "results/summary.json").read_text())
    assert summary["counts"]["unknown_sample_count"] == 1
    assert summary["counts"]["csv_samples_attempted"] == 2
    assert summary["counts"]["csv_samples_passed"] == 2
    assert summary["cases"][0]["samples"] is None
    assert summary["cases"][0]["status"] == "validation_error"
    assert {path.name for path in (report_root / "results/cases").glob("*.json")} == {
        "bad.json",
        "ok.json",
    }
    assert "未知" in (report_root / "RUNS.md").read_text()


def test_output_evidence_requires_exact_run_and_verified_bytes(
    report_root: Path,
) -> None:
    output = report_root / "evidence/toy/golden_native/output.csv"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"q\n0\n")
    REPORT.save(
        report_root / "evidence/index.json",
        {
            "artifacts": [
                {
                    "source": ".runs/old/toy/golden/native/output.csv",
                    "path": "evidence/toy/golden_native/output.csv",
                    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                }
            ]
        },
    )
    original = {
        "source_case_id": "TOY",
        "variant_id": "toy",
        "status": "pass",
        "samples": 1,
        "backends": {"golden_native": {"status": "pass"}},
    }
    new = REPORT.compact_result(original, "new")
    assert "evidence" not in new
    assert "output_csv" not in new["backends"]["golden_native"]
    old = REPORT.compact_result(original, "old")
    assert old["evidence"] == ["evidence/toy/golden_native/output.csv"]
    output.write_bytes(b"q\n1\n")
    with pytest.raises(ValueError, match="哈希不一致"):
        REPORT.compact_result(original, "old")


def test_published_selection_without_raw_archive_has_actionable_error(
    report_root: Path,
) -> None:
    REPORT.save(
        report_root / "results/selection.json", {"formal_run_ids": ["archived"]}
    )
    with pytest.raises(FileNotFoundError, match="已发布精简结果仍可直接阅读"):
        REPORT.selected_runs(None)


def _vcd_case(root: Path, run: str, *, variant: str = "toy") -> dict:
    """报告层夹具只构造归档，不替代 waveform/native 的真实波形比较测试。"""
    case_root = root / ".runs" / run / variant
    result = {
        "source_case_id": "TOY", "variant_id": variant, "protocol": REPORT.VCD_PROTOCOL,
        "status": "pass", "samples": 2, "vcd_events": 3,
        "golden_native_oracle": True, "golden_k_oracle": True, "buggy_k_native": True,
        "simulator_agrees_with_native": True, "bug_detected_by_oracle": True,
        "backends": {}, "waveform_comparisons": {},
    }
    for group in ("golden", "buggy"):
        artifacts = {}
        paths = {
            "kimulator_vcd": case_root / group / "kimulator/test.vcd",
            "native_vcd": case_root / group / "native/trace.vcd",
            "preflight": case_root / group / "comparison/preflight.json",
            "command": case_root / group / "comparison/diffvcd.command.json",
            "stdout": case_root / group / "comparison/diffvcd.stdout.log",
            "stderr": case_root / group / "comparison/diffvcd.stderr.log",
            "diffvcd_script": root / "tool/diffvcd.py",
        }
        for label, path in paths.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("归档测试工件\n")
            artifacts[label] = {"path": str(path), "sha256": REPORT.digest(path), "bytes": path.stat().st_size}
        result["waveform_comparisons"][group] = {
            "agrees": True, "exit_code": 0, "compared_signals": 2, "event_count": 3,
            "first_mismatch": None, "errors": [], "artifacts": artifacts,
        }
        for backend in ("native", "k"):
            result["backends"][group + "_" + backend] = {
                "status": "pass" if group == "golden" else "oracle_mismatch",
                "events_completed": 3, "simulation_calls": 6, "evaluations_per_input": 2,
            }
    REPORT.save(case_root / "result.json", result)
    REPORT.save(case_root / "test_data.json", {"events": []})
    REPORT.save(root / ".runs" / run / "results.json", [result])
    REPORT.save(root / ".runs" / run / "versions.json", {"protocol": REPORT.VCD_PROTOCOL})
    return result


def test_vcd_report_exports_exact_evidence_without_rewriting_csv_history(
    report_root: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _vcd_case(report_root, "vcd-run")
    REPORT.save(report_root / ".runs/vcd-run/batch-exit.json", {"exit_code": 0, "source": "宿主执行器"})
    REPORT.save(report_root / "results/summary.json", {"history": "csv"})
    REPORT.save(report_root / "results/selection.json", {"formal_run_ids": ["old"]})
    (report_root / "RUNS.md").write_text("历史 CSV\n")
    history = {path: path.read_bytes() for path in [
        report_root / "results/summary.json", report_root / "results/selection.json", report_root / "RUNS.md",
    ]}
    monkeypatch.setattr(sys, "argv", ["report.py", "--protocol", "vcd", "--runs", "vcd-run"])
    REPORT.main()
    summary = json.loads((report_root / "results/vcd/summary.json").read_text())
    assert summary["counts"]["variants_passed"] == 1
    assert summary["counts"]["vcd_events_passed"] == 3
    assert summary["cases"][0]["backends"]["buggy_k"]["native_comparison"]["compared_signals"] == 2
    exported = summary["cases"][0]["waveform_comparisons"]["golden"]["artifacts"]["kimulator_vcd"]
    assert exported["path"] == "evidence/vcd/vcd-run/toy/golden/kimulator/test.vcd"
    index = json.loads((report_root / "evidence/vcd/index.json").read_text())
    assert any(item["path"].endswith("/run/batch-exit.json") for item in index["artifacts"])
    for artifact in index["artifacts"]:
        assert REPORT.digest(report_root / artifact["path"]) == artifact["sha256"]
        source = Path(artifact["source"])
        if not source.is_absolute():
            source = report_root / source
        assert (report_root / artifact["path"]).read_bytes() == source.read_bytes()
    assert "[toy](results/vcd/cases/toy.json)" in (report_root / "VCD_RUNS.md").read_text()
    assert f'[K]({exported["path"]})' in (report_root / "VCD_RUNS.md").read_text()
    assert "[Verilator](evidence/vcd/vcd-run/toy/golden/native/trace.vcd)" in (report_root / "VCD_RUNS.md").read_text()
    assert REPORT.selected_runs(None, vcd=True) == ["vcd-run"]
    assert all(path.read_bytes() == contents for path, contents in history.items())


def test_vcd_report_rejects_old_protocol_and_implicit_selection(report_root: Path) -> None:
    REPORT.save(report_root / ".runs/old/results.json", [{"variant_id": "old", "status": "pass"}])
    REPORT.save(report_root / "results/selection.json", {"formal_run_ids": ["old"]})
    with pytest.raises(ValueError, match="首次 VCD"):
        REPORT.selected_runs(None, vcd=True)
    with pytest.raises(ValueError, match="不是.*不能纳入"):
        REPORT.report_vcd(["old"])
    assert not (report_root / "results/vcd").exists()
    assert not (report_root / "evidence/vcd").exists()


def test_vcd_report_rejects_truncated_execution_and_changed_waveform(report_root: Path) -> None:
    case = _vcd_case(report_root, "vcd-run")
    case["backends"]["buggy_k"]["simulation_calls"] = 5
    with pytest.raises(ValueError, match="全事件同输入双执行"):
        REPORT.validate_vcd_record(case)
    case["backends"]["buggy_k"]["simulation_calls"] = 6
    wave = Path(case["waveform_comparisons"]["golden"]["artifacts"]["kimulator_vcd"]["path"])
    wave.write_text("已变化\n")
    with pytest.raises(ValueError, match="证据哈希不一致"):
        REPORT.report_vcd(["vcd-run"])
    assert not (report_root / "evidence/vcd").exists()


def test_vcd_failure_keeps_waveform_difference_and_cli_blocker(report_root: Path) -> None:
    case = _vcd_case(report_root, "failed")
    case["status"] = "failed"
    case["waveform_comparisons"]["golden"].update({
        "agrees": False, "exit_code": 1,
        "first_mismatch": {"time": 1, "event_index": 1, "signal": "q", "expected": 1, "actual": 0},
    })
    case["backends"]["buggy_k"].update({"status": "timeout", "stage": "execution", "error": "超过时限"})
    case["waveform_comparisons"].pop("buggy")
    REPORT.save(report_root / ".runs/failed/results.json", [case])
    REPORT.save(report_root / ".runs/failed/toy/result.json", case)
    REPORT.report_vcd(["failed"])
    summary = json.loads((report_root / "results/vcd/summary.json").read_text())
    assert summary["counts"]["variants_passed"] == 0
    assert summary["cases"][0]["blockers"][0]["error"] == "超过时限"
    assert summary["cases"][0]["waveform_comparisons"]["golden"]["first_mismatch"]["time"] == 1
    assert "t=1 q, Verilator=1, K=0" in (report_root / "VCD_RUNS.md").read_text()


def test_vcd_rerun_retains_failed_attempt_and_additional_normalization_evidence(report_root: Path) -> None:
    old = _vcd_case(report_root, "first")
    old["status"] = "failed"
    old["waveform_comparisons"]["golden"]["agrees"] = False
    REPORT.save(report_root / ".runs/first/results.json", [old])
    REPORT.save(report_root / ".runs/first/toy/result.json", old)
    new = _vcd_case(report_root, "second")
    mapping = report_root / ".runs/second/toy/golden/comparison/normalization.json"
    REPORT.save(mapping, {"policy": "单比特声明配对", "mappings": [{"old": "q[0:0]", "new": "q"}]})
    new["waveform_comparisons"]["golden"]["normalization"] = {"policy": "单比特声明配对"}
    new["waveform_comparisons"]["golden"]["artifacts"]["normalization_map"] = {
        "path": str(mapping), "sha256": REPORT.digest(mapping), "bytes": mapping.stat().st_size,
    }
    REPORT.save(report_root / ".runs/second/results.json", [new])
    REPORT.save(report_root / ".runs/second/toy/result.json", new)
    REPORT.report_vcd(["first", "second"])
    summary = json.loads((report_root / "results/vcd/summary.json").read_text())
    attempts = json.loads((report_root / "results/vcd/attempts.json").read_text())
    assert summary["counts"]["case_attempts"] == 2
    assert summary["counts"]["variants_attempted"] == 1
    assert summary["cases"][0]["run_id"] == "second"
    assert [item["status"] for item in attempts] == ["failed", "pass"]
    comparison = summary["cases"][0]["waveform_comparisons"]["golden"]
    assert comparison["normalization"]["policy"] == "单比特声明配对"
    assert (report_root / comparison["artifacts"]["normalization_map"]["path"]).read_bytes() == mapping.read_bytes()


def test_vcd_parser_failure_exports_original_stderr_without_kore(report_root: Path) -> None:
    case_root = report_root / ".runs/parser-failure/s2"
    simulation = case_root / "golden/kimulator/simulation"
    simulation.mkdir(parents=True)
    stderr = simulation / "command-0000.stderr"
    stderr.write_bytes(b"design.generic.mlir:15:53: syntax error, unexpected <, expecting }\n")
    (simulation / "command-0001.stderr").write_bytes(b"")
    (simulation / "compiled.kore").write_bytes(b"Kore payload\n")
    case = {
        "source_case_id": "S2", "variant_id": "s2", "protocol": REPORT.VCD_PROTOCOL,
        "status": "execution_error", "samples": 45, "vcd_events": 89,
        "backends": {"golden_k": {"status": "execution_error", "stage": "compile", "simulation_calls_attempted": 0}},
        "waveform_comparisons": {},
    }
    REPORT.save(case_root / "result.json", case)
    REPORT.save(report_root / ".runs/parser-failure/results.json", [case])
    REPORT.report_vcd(["parser-failure"])
    exported = report_root / "evidence/vcd/parser-failure/s2/golden/kimulator/simulation/command-0000.stderr"
    assert exported.read_bytes() == stderr.read_bytes()
    index = json.loads((report_root / "evidence/vcd/index.json").read_text())
    record = next(item for item in index["artifacts"] if item["path"].endswith("command-0000.stderr"))
    assert record["sha256"] == REPORT.digest(stderr)
    assert not any(item["path"].endswith(".kore") for item in index["artifacts"])
    assert not any(item["path"].endswith("command-0001.stderr") for item in index["artifacts"])
    assert "| 未完成 | 未完成 | execution_error |" in (report_root / "VCD_RUNS.md").read_text()
