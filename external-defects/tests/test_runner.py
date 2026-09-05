"""验证批量入口对来源契约、CSV 错误、比较集合和证据丢失的拒绝行为。"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types
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


def test_archive_preserves_complete_state_and_digest(tmp_path: Path) -> None:
    source = tmp_path / "event-0001.kore"
    content = ("状态证据\n" * 2000).encode()
    source.write_bytes(content)
    record = RUNNER.archive_state(source)
    assert source.exists() is False
    assert gzip.decompress((tmp_path / record["file"]).read_bytes()) == content
    assert record["sha256_uncompressed"] == hashlib.sha256(content).hexdigest()


def _run_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, argparse.Namespace, list]:
    """隔离运行调度，只记录后端是否被调用；不运行 K 或 Verilator。"""
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path)
    for script in ["runner.py", "native.py"]:
        shutil.copyfile(ROOT / script, tmp_path / script)
    build = tmp_path / "build"
    monkeypatch.setattr(RUNNER, "BUILD", build)
    definition = build / "kdist/circt-semantics/llvm/definition.kore"
    definition.parent.mkdir(parents=True)
    definition.write_text("固定定义")
    (build / "parser").write_text("固定 parser")
    prepared = {
        "semantics_hashes": {},
        "pyk": "test",
        "api_sha256": "test-api",
        "kdist_plugin_sha256": "test-plugin",
        **{name: {"version": "test"} for name in ("kompile", "krun", "kast")},
        "parser_sha256": RUNNER.sha(build / "parser"),
        "definition_sha256": RUNNER.sha(definition),
    }
    (build / "prepared.json").write_text(json.dumps(prepared))
    monkeypatch.setattr(RUNNER, "environment", lambda args: dict(prepared))
    manifest = json.loads((ROOT / "manifests/s1b.json").read_text())
    shutil.copytree(ROOT / "designs/axi-lite-s1", tmp_path / "designs/axi-lite-s1")
    (tmp_path / "manifests").mkdir()
    (tmp_path / "manifests/s1b.json").write_text(json.dumps(manifest))
    calls = []

    def fake_native(m, sources, rows, work, **kwargs):
        calls.append(("native", m["variant_id"]))
        return {"status": "pass", "samples": [{p["name"]: row[p["name"]] for p in m["outputs"]} for row in rows]}

    def fake_k(m, sources, rows, work, args):
        calls.append(("k", m["variant_id"]))
        return {"status": "pass", "samples": [{p["name"]: row[p["name"]] for p in m["outputs"]} for row in rows]}

    module = types.ModuleType("native")
    module.run_native = fake_native
    monkeypatch.setitem(sys.modules, "native", module)
    monkeypatch.setattr(RUNNER, "run_k", fake_k)
    service = tmp_path / "selected-service"
    (service / "src/kcirct").mkdir(parents=True)
    (service / "src/kcirct/api.py").write_text("测试 API 快照")
    monkeypatch.setattr(RUNNER.subprocess, "check_output", lambda *args, **kwargs: "测试 git diff")
    args = argparse.Namespace(run_id="test-run", cases=["s1b"], kcirct_root=service, tools={"verilator": "verilator"})
    return manifest, args, calls


@pytest.mark.parametrize("invalid_change", ["wrong_testbench", "missing_source_hash"])
def test_manifest_contract_failure_precedes_backend_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, invalid_change: str
) -> None:
    """S1 的两份 CSV 均有哈希，只有核查 bugs 关联才能识别误选测试。"""
    manifest, args, calls = _run_fixture(tmp_path, monkeypatch)
    if invalid_change == "wrong_testbench":
        manifest["csv"] = "designs/axi-lite-s1/testbench/tb1.csv"
    else:
        del manifest["source_hashes"][manifest["golden_sources"][0]]
    (tmp_path / "manifests/s1b.json").write_text(json.dumps(manifest))
    RUNNER.run(args)
    result = json.loads((tmp_path / ".runs/test-run/s1b/result.json").read_text())
    assert calls == [], "来源契约无效时不应继续调用任何后端"
    assert result["status"] == "execution_error"


def test_prepared_definition_hash_is_verified(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, args, calls = _run_fixture(tmp_path, monkeypatch)
    definition = tmp_path / "build/kdist/circt-semantics/llvm/definition.kore"
    definition.write_text("定义已被替换，但 parser 和源语义哈希仍一致")
    with pytest.raises(ValueError, match="定义|definition|prepare"):
        RUNNER.run(args)
    assert calls == []


def test_pinned_s1_manifests_select_distinct_correct_traces() -> None:
    cases = {name: json.loads((ROOT / f"manifests/{name}.json").read_text()) for name in ["s1b", "s1r"]}
    assert cases["s1b"]["csv"].endswith("/tb0.csv")
    assert cases["s1r"]["csv"].endswith("/tb1.csv")
    for name, case in cases.items():
        assert case["selected_testbench"]["bugs"] == [name]
        rows, normalizations = RUNNER.load_rows(case)
        assert len(rows) == 10 and len(normalizations) == 10
    assert cases["s1b"]["csv"] != cases["s1r"]["csv"]


def test_cli_uses_path_by_default_and_explicit_options_override_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("KCIRCT_ROOT", "K_BIN", "CIRCT_BIN", "VERILATOR"):
        monkeypatch.delenv(name, raising=False)
    args = RUNNER.argument_parser().parse_args(["prepare"])
    monkeypatch.chdir(tmp_path)
    assert RUNNER.service_root(args) == RUNNER.SERVICE.resolve()
    assert (args.k_bin, args.circt_bin, args.verilator) == (None, None, None)
    monkeypatch.setenv("KCIRCT_ROOT", str(tmp_path / "environment-service"))
    monkeypatch.setenv("K_BIN", str(tmp_path / "environment-k"))
    monkeypatch.setenv("CIRCT_BIN", str(tmp_path / "environment-circt"))
    monkeypatch.setenv("VERILATOR", "environment-verilator")
    args = RUNNER.argument_parser().parse_args(
        ["run", "--kcirct-root", "selected", "--verilator", "selected-verilator"]
    )
    assert RUNNER.service_root(args) == tmp_path / "selected"
    assert args.k_bin == tmp_path / "environment-k"
    assert args.circt_bin == tmp_path / "environment-circt"
    assert args.verilator == "selected-verilator"


def test_explicit_tool_directory_cannot_fall_back_to_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool_dir = tmp_path / "runtime-bin"
    tool_dir.mkdir()
    executable = tool_dir / "krun"
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(tool_dir))
    assert RUNNER.tool("krun") == str(executable)
    with pytest.raises(ValueError, match="缺少可执行工具"):
        RUNNER.tool("krun", tmp_path / "wrong-installation")


def test_command_uses_evidence_directory_not_callers_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    caller = tmp_path / "caller"
    caller.mkdir()
    monkeypatch.chdir(caller)
    work = tmp_path / "evidence"
    stdout, _ = RUNNER.command([sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"], work, "cwd")
    assert stdout.strip() == str(work)
    record = json.loads((work / "commands.jsonl").read_text())
    assert record["cwd"] == str(work)


@pytest.mark.parametrize("run_id", ["../escape", "/tmp/escape", "nested/run", ".", "..", "validation", "bad name"])
def test_run_id_is_rejected_before_environment_or_backend_dispatch(
    run_id: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(RUNNER, "environment", lambda _: pytest.fail("无效 run-id 不应检查或执行环境"))
    with pytest.raises(ValueError, match="run-id"):
        RUNNER.run(argparse.Namespace(run_id=run_id))


def test_run_id_cannot_follow_existing_symlink_outside_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(RUNNER, "ROOT", tmp_path / "experiment")
    runs = RUNNER.ROOT / ".runs"
    runs.mkdir(parents=True)
    (runs / "escape").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="越界"):
        RUNNER.run_directory("escape")


def test_reproduce_script_replays_batch_once_with_shared_run_id_after_move(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = tmp_path / "original experiment"
    monkeypatch.setattr(RUNNER, "ROOT", original)
    out = original / ".runs/example"
    out.mkdir(parents=True)
    RUNNER.write_summary(out, [{"variant_id": "d13"}, {"variant_id": "s3"}])
    script = (out / "reproduce.sh").read_text()
    assert sys.executable not in script and str(original) not in script
    moved = tmp_path / "moved experiment"
    original.rename(moved)
    executor = tmp_path / "selected-python"
    executor.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    executor.chmod(0o755)
    monkeypatch.setenv("PYTHON", str(executor))
    result = subprocess.run(
        [
            "sh",
            str(moved / ".runs/example/reproduce.sh"),
            "--kcirct-root",
            "current-service",
            "--run-id",
            "replayed-batch",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.splitlines() == [
        str(moved / "runner.py"),
        "run",
        "--cases",
        "d13",
        "s3",
        "--kcirct-root",
        "current-service",
        "--run-id",
        "replayed-batch",
    ]


@pytest.fixture
def imported_service(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, dict]:
    """提供独立的安装元数据与真实模块路径，验证来源校验而不导入 K 依赖。"""
    service = tmp_path / "selected-service"
    api_path = service / "src/kcirct/api.py"
    plugin_path = service / "src/kcirct/kdist/plugin.py"
    plugin_path.parent.mkdir(parents=True)
    api_path.write_text("测试 API")
    plugin_path.write_text("测试 kdist 插件")
    build = tmp_path / "experiment/.build/external-defects"
    monkeypatch.setattr(RUNNER, "BUILD", build)
    modules = {
        "kcirct.api": types.SimpleNamespace(
            __file__=str(api_path), kdist=types.SimpleNamespace(kdist_dir=build / "kdist")
        ),
        "kcirct.kdist.plugin": types.SimpleNamespace(
            __file__=str(plugin_path),
            __TARGETS__={"source": types.SimpleNamespace(SRC_DIR=plugin_path.parent)},
        ),
    }
    entry = types.SimpleNamespace(value="kcirct.kdist.plugin")
    monkeypatch.setattr(RUNNER.importlib.metadata, "entry_points", lambda **kwargs: [entry])
    original_import = RUNNER.importlib.import_module
    monkeypatch.setattr(
        RUNNER.importlib, "import_module", lambda name: modules[name] if name in modules else original_import(name)
    )
    return service, modules


@pytest.mark.parametrize("module_name", ["kcirct.api", "kcirct.kdist.plugin"])
def test_rejects_import_from_different_checkout(imported_service: tuple[Path, dict], module_name: str) -> None:
    service, modules = imported_service
    modules[module_name].__file__ = str(service.parent / "other-checkout/api.py")
    with pytest.raises(ValueError, match="实际导入.*来源不符"):
        RUNNER.validate_service_imports(service)


def test_rejects_kdist_source_target_and_cached_build_directory_mismatch(imported_service: tuple[Path, dict]) -> None:
    service, modules = imported_service
    api, plugin = modules["kcirct.api"], modules["kcirct.kdist.plugin"]
    expected_source = plugin.__TARGETS__["source"].SRC_DIR
    plugin.__TARGETS__["source"].SRC_DIR = service / "wrong-target"
    with pytest.raises(ValueError, match="source target"):
        RUNNER.validate_service_imports(service)
    plugin.__TARGETS__["source"].SRC_DIR = expected_source
    api.kdist.kdist_dir = service / "cached-before-configuration"
    with pytest.raises(ValueError, match="错误的 KDIST_DIR"):
        RUNNER.validate_service_imports(service)


def test_missing_or_ambiguous_plugin_registration_is_rejected(
    imported_service: tuple[Path, dict], monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _ = imported_service
    for entries in ([], [types.SimpleNamespace(value="wrong.plugin")], [object(), object()]):
        monkeypatch.setattr(RUNNER.importlib.metadata, "entry_points", lambda **kwargs: entries)
        with pytest.raises(ValueError, match="唯一注册"):
            RUNNER.validate_service_imports(service)


@pytest.mark.parametrize("tool_version", ["1.2.3", "1.2.33"])
def test_environment_configures_build_before_import_and_checks_tool_versions(
    imported_service: tuple[Path, dict], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tool_version: str
) -> None:
    service, _ = imported_service
    binaries = tmp_path / "runtime-tools"
    binaries.mkdir()
    for name in ("kompile", "krun", "kast", "circt-verilog", "circt-opt", "verilator"):
        path = binaries / name
        path.write_text(f'#!/bin/sh\nprintf "tool v{tool_version}\\n"\n')
        path.chmod(0o755)
    monkeypatch.setenv("PATH", str(binaries))
    monkeypatch.setenv("KDIST_DIR", "ignored-previous-value")
    for name in ("K_BIN", "CIRCT_BIN", "VERILATOR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(RUNNER.importlib.metadata, "version", lambda _: "1.2.3")
    monkeypatch.setattr(RUNNER.subprocess, "check_output", lambda *args, **kwargs: "test-head\n")
    check_imports = RUNNER.validate_service_imports

    def check_after_configuration(path):
        assert os.environ["KDIST_DIR"] == str(RUNNER.BUILD / "kdist")
        return check_imports(path)

    monkeypatch.setattr(RUNNER, "validate_service_imports", check_after_configuration)
    args = argparse.Namespace(kcirct_root=service, k_bin=None, circt_bin=None, verilator=None)
    if tool_version != "1.2.3":
        with pytest.raises(ValueError, match="版本不匹配") as error:
            RUNNER.environment(args)
        assert str(binaries / "kompile") in str(error.value)
        assert "v1.2.33" in str(error.value)
        return
    versions = RUNNER.environment(args)
    assert versions["imports"]["api"] == str(service / "src/kcirct/api.py")
    assert versions["kdist_plugin_sha256"] == RUNNER.sha(service / "src/kcirct/kdist/plugin.py")
    assert versions["verilator"]["path"] == str(binaries / "verilator")
    assert args.tools["krun"] == str(binaries / "krun")


@pytest.mark.parametrize("configured_k", [False, True])
def test_child_processes_preserve_checked_k_and_relative_pythonpath(
    imported_service: tuple[Path, dict], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, configured_k: bool
) -> None:
    """CIRCT 目录混入另一套 K 时，API/kdist 子进程仍必须执行已核验的入口。"""
    service, _ = imported_service
    default_bin, circt_bin, k_bin = [tmp_path / name for name in ("default-tools", "circt-tools", "selected-k")]
    for directory, prefix in ((default_bin, "default"), (circt_bin, "shadow"), (k_bin, "selected")):
        directory.mkdir()
        for name in ("kompile", "krun", "kast", "circt-verilog", "circt-opt", "verilator"):
            path = directory / name
            path.write_text(f'#!/bin/sh\nprintf "{prefix} v1.2.3\\n"\n')
            path.chmod(0o755)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", "default-tools")
    monkeypatch.setenv("PYTHONPATH", "relative-sources")
    monkeypatch.setenv("KDIST_DIR", "previous-value")
    for name in ("K_BIN", "CIRCT_BIN", "VERILATOR"):
        monkeypatch.delenv(name, raising=False)
    python_sources = tmp_path / "relative-sources"
    python_sources.mkdir()
    (python_sources / "portable_import_probe.py").write_text('ORIGIN = "chosen-parent-directory"\n')
    monkeypatch.setattr(RUNNER.importlib.metadata, "version", lambda _: "1.2.3")
    monkeypatch.setattr(RUNNER.subprocess, "check_output", lambda *args, **kwargs: "test-head\n")
    args = argparse.Namespace(
        kcirct_root=service, k_bin=k_bin if configured_k else None, circt_bin=circt_bin, verilator=None
    )
    versions = RUNNER.environment(args)
    expected_bin = k_bin if configured_k else default_bin
    child_work = tmp_path / "different-cwd"
    child_work.mkdir()
    assert str(circt_bin) not in os.environ["PATH"].split(os.pathsep)
    for name in ("kompile", "krun", "kast"):
        assert args.tools[name] == str(expected_bin / name) == shutil.which(name)
        actual = subprocess.run([name, "--version"], cwd=child_work, capture_output=True, text=True, check=True)
        assert actual.stdout == versions[name]["version"]
    assert versions["circt-opt"]["path"] == str(circt_bin / "circt-opt")
    imported = subprocess.run(
        [sys.executable, "-c", "import portable_import_probe; print(portable_import_probe.ORIGIN)"],
        cwd=child_work,
        capture_output=True,
        text=True,
        check=True,
    )
    assert imported.stdout.strip() == "chosen-parent-directory"
    # 即使后续代码改变 PATH，API 的 K 命令仍绑定到之前核验的绝对入口。
    monkeypatch.setenv("PATH", str(circt_bin))
    for executable in ("krun", str(circt_bin / "krun")):
        argv = RUNNER.bind_k_command([executable, "--version"], args.tools)
        result = subprocess.run(argv, cwd=child_work, capture_output=True, text=True, check=True)
        assert result.stdout == versions["krun"]["version"]


def test_all_manifests_follow_layout_and_source_hashes() -> None:
    for path in sorted((ROOT / "manifests").glob("*.json")):
        manifest = json.loads(path.read_text())
        RUNNER.validate_manifest(manifest)
        for filename, digest in manifest["source_hashes"].items():
            assert RUNNER.sha(RUNNER.resource_path(filename)) == digest, filename


def test_layout_missing_upstream_mapping_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest, _, _ = _run_fixture(tmp_path, monkeypatch)
    layout_path = tmp_path / manifest["layout_file"]
    layout = json.loads(layout_path.read_text())
    del layout["files"]["xlnxdemo.v"]
    layout_path.write_text(json.dumps(layout))
    with pytest.raises(ValueError, match="缺少上游文件映射"):
        RUNNER.validate_manifest(manifest)
