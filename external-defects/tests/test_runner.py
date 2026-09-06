"""验证外部组件边界、输入协议、来源契约与辅助 oracle。"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("external_defects_runner_audit", ROOT / "runner.py")
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


@pytest.fixture
def csv_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, Path]:
    """使用有输入和输出的小契约；测试数据本身不依赖任何仿真器。"""
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path)
    table = tmp_path / "tb.csv"
    table.write_text("d,q\n1,0\n2,1\n")
    manifest = {
        "variant_id": "toy",
        "csv": "tb.csv",
        "clock": "clk",
        "inputs": [{"name": "clk", "width": 1}, {"name": "d", "width": 8}],
        "outputs": [{"name": "q", "width": 8}],
        "oracle_outputs": ["q"],
        "masks": [],
        "samples": 2,
        "csv_normalization": {"strip_whitespace": True, "allow_one_trailing_empty_field": False},
    }
    return manifest, table


@pytest.mark.parametrize("csv_text", ["q\n0\n1\n", "d\n1\n2\n", "d,q,extra\n1,0,9\n2,1,9\n"])
def test_csv_rejects_missing_or_extra_column(csv_case: tuple[dict, Path], csv_text: str) -> None:
    manifest, table = csv_case
    table.write_text(csv_text)
    with pytest.raises(ValueError, match="CSV 列不符"):
        RUNNER.load_rows(manifest)


@pytest.mark.parametrize("csv_text", ["d,q\n1\n2,1\n", "d,q\n1,0,3\n2,1\n", "d,d\n1,0\n2,1\n"])
def test_csv_rejects_row_shape_and_duplicate_header(csv_case: tuple[dict, Path], csv_text: str) -> None:
    manifest, table = csv_case
    table.write_text(csv_text)
    with pytest.raises(ValueError):
        RUNNER.load_rows(manifest)


@pytest.mark.parametrize("bad_value", ["256", "-1", "1.5", ""])
def test_csv_rejects_invalid_or_out_of_width_values(csv_case: tuple[dict, Path], bad_value: str) -> None:
    manifest, table = csv_case
    table.write_text(f"d,q\n{bad_value},0\n2,1\n")
    with pytest.raises(ValueError):
        RUNNER.load_rows(manifest)


@pytest.mark.parametrize("token", ["x", "z", "-"])
def test_unknown_output_requires_exact_authorized_mask(csv_case: tuple[dict, Path], token: str) -> None:
    manifest, table = csv_case
    table.write_text(f"d,q\n1,{token}\n2,1\n")
    with pytest.raises(ValueError, match="未授权"):
        RUNNER.load_rows(manifest)
    manifest["masks"] = [{"sample_index": 0, "signal": "q", "token": token, "reason": "测试 oracle 明确未知"}]
    rows, normalizations = RUNNER.load_rows(manifest)
    assert rows == [{"d": 1, "q": None}, {"d": 2, "q": 1}]
    assert normalizations == []
    manifest["masks"][0]["sample_index"] = 1
    with pytest.raises(ValueError):
        RUNNER.load_rows(manifest)


def test_unknown_input_cannot_be_masked(csv_case: tuple[dict, Path]) -> None:
    manifest, table = csv_case
    table.write_text("d,q\nx,0\n2,1\n")
    manifest["masks"] = [{"sample_index": 0, "signal": "d", "token": "x", "reason": "输入不能作为 oracle 掩码"}]
    with pytest.raises(ValueError, match="未授权"):
        RUNNER.load_rows(manifest)


def test_unused_mask_is_not_silently_accepted(csv_case: tuple[dict, Path]) -> None:
    manifest, _ = csv_case
    manifest["masks"] = [{"sample_index": 0, "signal": "q", "token": "x", "reason": "CSV 中实际为零"}]
    with pytest.raises(ValueError, match="掩码"):
        RUNNER.load_rows(manifest)


def test_duplicate_mask_is_rejected(csv_case: tuple[dict, Path]) -> None:
    """重复项不能被字典覆盖后伪装成有效的来源掩码。"""
    manifest, table = csv_case
    table.write_text("d,q\n1,x\n2,1\n")
    mask = {"sample_index": 0, "signal": "q", "token": "x", "reason": "重复声明"}
    manifest["masks"] = [mask, dict(mask)]
    with pytest.raises(ValueError, match="掩码|重复"):
        RUNNER.load_rows(manifest)


def test_all_masked_oracle_is_rejected(csv_case: tuple[dict, Path]) -> None:
    manifest, table = csv_case
    table.write_text("d,q\n1,x\n2,x\n")
    manifest["masks"] = [
        {"sample_index": i, "signal": "q", "token": "x", "reason": "仅测试空比较拒绝"} for i in range(2)
    ]
    with pytest.raises(ValueError, match="全部被掩码|没有已定义"):
        RUNNER.load_rows(manifest)


def test_trailing_empty_column_requires_documented_normalization(csv_case: tuple[dict, Path]) -> None:
    manifest, table = csv_case
    table.write_text("d,q\n1,0,\n2,1,\n")
    with pytest.raises(ValueError):
        RUNNER.load_rows(manifest)
    manifest["variant_id"] = "s1b"
    manifest["csv_normalization"]["allow_one_trailing_empty_field"] = True
    rows, normalizations = RUNNER.load_rows(manifest)
    assert len(rows) == 2
    assert [entry["sample_index"] for entry in normalizations] == [0, 1]
    manifest["csv_normalization"]["allow_one_trailing_empty_field"] = False
    with pytest.raises(ValueError):
        RUNNER.load_rows(manifest)


def test_two_trailing_empty_columns_are_never_accepted(csv_case: tuple[dict, Path]) -> None:
    manifest, table = csv_case
    manifest["variant_id"] = "s1r"
    manifest["csv_normalization"]["allow_one_trailing_empty_field"] = True
    table.write_text("d,q\n1,0,,\n2,1,,\n")
    with pytest.raises(ValueError):
        RUNNER.load_rows(manifest)


def test_declared_sample_count_must_match_csv(csv_case: tuple[dict, Path]) -> None:
    manifest, _ = csv_case
    manifest["samples"] = 3
    with pytest.raises(ValueError, match="采样|样本|samples"):
        RUNNER.load_rows(manifest)


@pytest.mark.parametrize(
    "expected,actual,names",
    [([], [], ["q"]), ([{"q": 1}], [], ["q"]), ([{"q": 1}], [{"q": 1}], []), ([{"q": None}], [{"q": 0}], ["q"])],
)
def test_compare_rejects_empty_or_incomplete_comparison(expected: list, actual: list, names: list) -> None:
    with pytest.raises(ValueError):
        RUNNER.compare(expected, actual, names)


@pytest.mark.parametrize("value", [1, None])
def test_required_output_must_exist_even_at_masked_sample(value: int | None) -> None:
    with pytest.raises(ValueError, match="缺少必须输出"):
        RUNNER.compare([{"q": value}], [{}], ["q"])


def test_first_difference_uses_real_sample_and_signal() -> None:
    result = RUNNER.compare([{"q": None}, {"q": 1}, {"q": 2}], [{"q": 0}, {"q": 3}, {"q": 4}], ["q"])
    assert result["agrees"] is False
    assert result["compared_cells"] == 2
    assert result["masked_cells"] == 1
    assert result["first_mismatch"] == {"sample_index": 1, "signal": "q", "expected": 1, "actual": 3}
    assert len(result["mismatches"]) == 2


def test_stimulus_keeps_inputs_at_both_edges_and_excludes_oracle(csv_case: tuple[dict, Path]) -> None:
    manifest, _ = csv_case
    rows = [{"d": 1, "q": 0}, {"d": 2, "q": 1}]
    assert RUNNER.stimulus(manifest, rows) == {
        "schema_version": 1,
        "timescale": "1ns",
        "events": [
            {"time": 0, "inputs": {"clk": 0, "d": 1}},
            {"time": 1, "inputs": {"clk": 1, "d": 1}},
            {"time": 2, "inputs": {"clk": 0, "d": 2}},
        ],
    }


def test_all_manifests_and_persisted_ir_match_sources() -> None:
    for path in sorted((ROOT / "manifests").glob("*.json")):
        m = json.loads(path.read_text())
        RUNNER.validate_manifest(m)
        for filename, digest in m["source_hashes"].items():
            assert RUNNER.sha(RUNNER.resource_path(filename)) == digest
        for variant in ("golden", "buggy"):
            mlir, _ = RUNNER.baseline(m, variant)
            assert mlir.is_file()


def test_baseline_rejects_parameter_drift() -> None:
    m = json.loads((ROOT / "manifests/d13.json").read_text())
    m["parameters"]["LEN_WIDTH"] = 99
    with pytest.raises(ValueError, match="parameters"):
        RUNNER.baseline(m, "golden")


def test_versioned_baseline_binds_profile_and_executable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """新版本可独立选择，但不能用旧产物的哈希替另一份执行文件背书。"""
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path)
    folder = tmp_path / "designs/toy/mlir/version-2/golden"
    folder.mkdir(parents=True)
    rtl = tmp_path / "source.v"
    rtl.write_text("module toy; endmodule\n")
    mlir = folder / "design.generic.mlir"
    mlir.write_text("module {}\n")
    m = {"project_id": "toy", "variant_id": "toy", "top": "toy", "parameters": {},
         "effective_parameters": {}, "frontend_args": [], "golden_sources": ["source.v"],
         "ir_baseline": "designs/toy/mlir/version-2", "ir_profile": None}
    provenance = {"configuration": {key: m[key] for key in
                                    ("top", "parameters", "effective_parameters", "frontend_args", "ir_profile")},
                  "rtl_sources": [{"path": "source.v", "sha256": RUNNER.sha(rtl)}],
                  "artifacts": {"design.generic.mlir": {"path": str(mlir.relative_to(tmp_path)),
                                                       "sha256": RUNNER.sha(mlir)}}}
    RUNNER.save(folder / "provenance.json", provenance)
    assert RUNNER.baseline(m, "golden")[0] == mlir
    m["ir_profile"] = "other-profile"
    with pytest.raises(ValueError, match="ir_profile"):
        RUNNER.baseline(m, "golden")
    m["ir_profile"] = None
    provenance["artifacts"]["design.generic.mlir"]["path"] = "different.mlir"
    RUNNER.save(folder / "provenance.json", provenance)
    with pytest.raises(ValueError, match="可执行文件"):
        RUNNER.baseline(m, "golden")


@pytest.mark.parametrize("folder", ["../escape", "/absolute"])
def test_versioned_baseline_rejects_path_escape(folder: str) -> None:
    m = json.loads((ROOT / "manifests/d13.json").read_text())
    m["ir_baseline"] = folder
    with pytest.raises(ValueError, match="路径"):
        RUNNER.baseline(m, "golden")


@pytest.fixture
def initialized_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, Path, dict]:
    """在隔离副本中破坏证明链，避免修改持久化实验输入。"""
    m = json.loads((ROOT / "manifests/s2.json").read_text())
    folder = ROOT / m["ir_baseline"] / "golden"
    provenance = json.loads((folder / "provenance.json").read_text())
    for item in [*provenance["rtl_sources"], *provenance["artifacts"].values()]:
        target = tmp_path / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / item["path"], target)
    copied = tmp_path / folder.relative_to(ROOT)
    RUNNER.save(copied / "provenance.json", provenance)
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path)
    assert RUNNER.baseline(m, "golden")[0].is_file()
    return m, copied, provenance


@pytest.mark.parametrize("artifact", ["frontend.pre-llhd.generic.mlir", "frontend.hw.generic.mlir", "initial-lowering.json"])
def test_initial_profile_requires_proof_artifacts(initialized_baseline: tuple, artifact: str) -> None:
    m, folder, provenance = initialized_baseline
    del provenance["artifacts"][artifact]
    RUNNER.save(folder / "provenance.json", provenance)
    with pytest.raises(ValueError, match="证明工件"):
        RUNNER.baseline(m, "golden")


def test_initial_profile_rejects_changed_initialization_policy(initialized_baseline: tuple) -> None:
    m, _, _ = initialized_baseline
    m["initialization"]["uninitialized_register_value"] = 1
    with pytest.raises(ValueError, match="初值策略"):
        RUNNER.baseline(m, "golden")


def test_initial_profile_cannot_authorize_nonzero_default(initialized_baseline: tuple) -> None:
    m, folder, provenance = initialized_baseline
    m["initialization"]["uninitialized_register_value"] = 1
    provenance["initialization"] = dict(m["initialization"])
    RUNNER.save(folder / "provenance.json", provenance)
    with pytest.raises(ValueError, match="二态默认零"):
        RUNNER.baseline(m, "golden")


def test_initial_profile_rejects_disconnected_audit_even_with_updated_file_hash(initialized_baseline: tuple) -> None:
    m, folder, provenance = initialized_baseline
    audit_path = folder / "initial-lowering.json"
    audit = json.loads(audit_path.read_text())
    audit["output_sha256"] = "0" * 64
    RUNNER.save(audit_path, audit)
    provenance["artifacts"]["initial-lowering.json"]["sha256"] = RUNNER.sha(audit_path)
    RUNNER.save(folder / "provenance.json", provenance)
    with pytest.raises(ValueError, match="未绑定实际输入输出"):
        RUNNER.baseline(m, "golden")


def test_initial_profile_rejects_unknown_policy(initialized_baseline: tuple) -> None:
    m, folder, provenance = initialized_baseline
    m["ir_profile"] = provenance["configuration"]["ir_profile"] = "unverified"
    RUNNER.save(folder / "provenance.json", provenance)
    with pytest.raises(ValueError, match="未知 IR"):
        RUNNER.baseline(m, "golden")


@pytest.mark.parametrize("run_id", ["../escape", "/absolute", "a/b", "", ".hidden"])
def test_run_id_rejected_before_any_work(run_id: str) -> None:
    with pytest.raises(ValueError, match="run-id"):
        RUNNER.run_directory(run_id)


def test_existing_run_cannot_be_overwritten(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path)
    (tmp_path / ".runs/existing").mkdir(parents=True)
    with pytest.raises(FileExistsError):
        RUNNER.run_directory("existing")


def test_k_backend_uses_only_public_command_files_and_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    m = json.loads((ROOT / "manifests/d13.json").read_text())
    trace = RUNNER.stimulus(m, RUNNER.load_rows(m)[0])
    inputs = tmp_path / "test_data.json"
    RUNNER.save(inputs, trace)
    work = tmp_path / "kimulator"
    args = argparse.Namespace(kimulator="/installed/bin/kcirct", env={})
    calls = []

    def external_command(argv, folder, label, timeout, env):
        calls.append(argv)
        (work / "test.vcd").write_text("由独立组件生成的输出")
        RUNNER.save(
            work / "simulation/result.json",
            {"status": "pass", "events_completed": len(trace["events"]), "simulation_calls": 2 * len(trace["events"])},
        )
        return "", 0.1

    monkeypatch.setattr(RUNNER, "command", external_command)
    result = RUNNER.run_k(m, "golden", inputs, work, args)
    assert result["status"] == "pass"
    argv = calls[0]
    assert argv[:2] == [args.kimulator, "simulate"]
    assert argv[argv.index("--inputs") + 1] == str(inputs)
    assert argv[argv.index("--evaluations-per-input") + 1] == "2"
    assert argv[argv.index("--output") + 1] == str(work / "test.vcd")
    assert "--keep-states" in argv


def test_external_component_failure_is_preserved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    m = json.loads((ROOT / "manifests/d13.json").read_text())
    inputs = tmp_path / "events.json"
    RUNNER.save(inputs, RUNNER.stimulus(m, RUNNER.load_rows(m)[0]))
    work = tmp_path / "kimulator"

    def fail(argv, folder, label, timeout, env):
        RUNNER.save(
            work / "simulation/result.json",
            {
                "status": "timeout",
                "stage": "execution",
                "events_completed": 0,
                "simulation_calls": 0,
                "error": "子进程达到限制",
            },
        )
        raise RuntimeError("组件退出非零")

    monkeypatch.setattr(RUNNER, "command", fail)
    result = RUNNER.run_k(m, "golden", inputs, work, argparse.Namespace(kimulator="kcirct", env={}))
    assert result["status"] == "timeout" and result["stage"] == "execution"
    assert (work / "simulation/result.json").is_file() and (work / "error.txt").is_file()


def test_runner_import_does_not_import_component() -> None:
    code = (
        "import importlib.util, sys; "
        f"s=importlib.util.spec_from_file_location('runner', {str(ROOT / 'runner.py')!r}); "
        "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
        "assert not any(n == 'kcirct' or n.startswith('kcirct.') or n == 'pyk' or n.startswith('pyk.') for n in sys.modules)"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_late_artifact_failure_cannot_be_overridden_by_matching_values() -> None:
    first = {"sample_index": 1, "signal": "q", "expected": 1, "actual": 3}
    result = {
        "backends": {
            "golden_native": {"status": "pass", "oracle": {"agrees": True}},
            "golden_k": {"status": "pass", "oracle": {"agrees": True}},
            "buggy_native": {"status": "oracle_mismatch", "oracle": {"agrees": False, "first_mismatch": first}},
            "buggy_k": {"status": "execution_error", "oracle": {"agrees": False, "first_mismatch": first}},
        },
        "waveform_comparisons": {"golden": {"agrees": True}, "buggy": {"agrees": True}},
    }
    RUNNER.finalize_case(result)
    assert result["simulator_agrees_with_native"] is True
    assert result["bug_detected_by_oracle"] is True
    assert result["status"] == "execution_error"
    result["backends"]["buggy_k"]["status"] = "oracle_mismatch"
    RUNNER.finalize_case(result)
    assert result["status"] == "pass"


@pytest.mark.parametrize("exit_code", [0, 1])
def test_cli_propagates_batch_exit_code(monkeypatch: pytest.MonkeyPatch, exit_code: int) -> None:
    monkeypatch.setattr(sys, "argv", ["runner.py", "run", "--cases", "all-short"])
    monkeypatch.setattr(RUNNER, "run", lambda args: exit_code)
    assert RUNNER.main() == exit_code


def test_prepared_cache_rejects_replaced_executable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(RUNNER, "BUILD", tmp_path)
    definition = tmp_path / "kdist/circt-semantics/llvm"
    definition.mkdir(parents=True)
    for name in ("definition.kore", "compiled.bin", "backend.txt", "interpreter"):
        (definition / name).write_text(name)
    (tmp_path / "parser").write_text("parser")
    identity = {
        "semantics_hashes": {},
        "kframework_version": "test",
        "kdist_plugin_sha256": "test",
        "tools": {name: {"version": "test"} for name in ("kompile", "krun", "kast")},
    }
    prepared = {
        "kimulator": identity,
        "definition_sha256": RUNNER.sha(definition / "definition.kore"),
        "parser_sha256": RUNNER.sha(tmp_path / "parser"),
        "compiled_artifact_sha256": RUNNER.compiled_artifact_hashes(),
    }
    RUNNER.save(tmp_path / "prepared.json", prepared)
    assert RUNNER.verify_prepared({"kimulator": identity}) == prepared
    (definition / "interpreter").write_text("另一份可执行文件")
    with pytest.raises(ValueError, match="make prepare"):
        RUNNER.verify_prepared({"kimulator": identity})


def test_layout_missing_upstream_mapping_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    m = json.loads((ROOT / "manifests/s1b.json").read_text())
    shutil.copytree(ROOT / "designs/axi-lite-s1", tmp_path / "designs/axi-lite-s1")
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path)
    layout_path = tmp_path / m["layout_file"]
    layout = json.loads(layout_path.read_text())
    del layout["files"]["xlnxdemo.v"]
    layout_path.write_text(json.dumps(layout))
    with pytest.raises(ValueError, match="缺少上游文件映射"):
        RUNNER.validate_manifest(m)
