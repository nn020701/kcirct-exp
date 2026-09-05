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
