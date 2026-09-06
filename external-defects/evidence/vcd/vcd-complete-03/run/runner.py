"""通过完整外部命令运行 Kimulator，以双执行 VCD 对照作为主判据。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import tomllib
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVICE = ROOT.parent.parent / "circt-semantics"
BUILD = ROOT.parent / ".build/external-defects"
PROTOCOL = "external-cli-double-eval-vcd-v1"
CASES = ["d13", "s3", "s1b", "s1r", "d8", "d12", "d11", "d4", "s2", "c4"]


def save(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(
    argv: list[str], work: Path, label: str, timeout: float = 120, env: dict | None = None
) -> tuple[str, float]:
    """外部进程边界：仅传文件与参数，记录退出码和日志，超时终止进程组。"""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    process = subprocess.Popen(
        argv, cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        timed_out = True
    elapsed = time.perf_counter() - start
    (work / f"{label}.stdout.txt").write_text(stdout)
    (work / f"{label}.stderr.txt").write_text(stderr)
    item = {
        "argv": argv,
        "cwd": str(work),
        "exit_code": process.returncode,
        "timeout": timed_out,
        "seconds": elapsed,
        "stdout": f"{label}.stdout.txt",
        "stderr": f"{label}.stderr.txt",
    }
    with (work / "commands.jsonl").open("a") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")
    if timed_out:
        raise TimeoutError(f"{label} 超过 {timeout} 秒；日志：{work}")
    if process.returncode:
        raise RuntimeError(f"{label} 退出码 {process.returncode}：{stderr[-2000:]}")
    return stdout, elapsed


def tool(name: str, directory: Path | None = None) -> str:
    requested = str(directory / name) if directory is not None else name
    found = shutil.which(requested)
    if found is None:
        raise ValueError(f"缺少可执行工具：{requested}")
    return str(Path(found).absolute())


def environment(args: argparse.Namespace) -> dict:
    """通过公开 --describe 查询安装身份；本进程不导入 kcirct 或 pyk。"""
    args.kimulator = tool(args.kimulator or "kcirct")
    args.env = dict(os.environ)
    args.env["PATH"] = str(Path(args.kimulator).parent) + os.pathsep + args.env.get("PATH", "")
    if args.k_bin:
        args.env["K_BIN"] = str(Path(args.k_bin).expanduser().resolve())
        args.env["PATH"] = args.env["K_BIN"] + os.pathsep + args.env.get("PATH", "")
    args.env["KDIST_DIR"] = str(BUILD / "kdist")
    response = subprocess.run(
        [args.kimulator, "simulate", "--describe"], env=args.env, text=True, capture_output=True, check=True, timeout=60
    )
    identity = json.loads(response.stdout)
    if identity.get("schema_version") != 1 or not identity.get("semantics_hashes"):
        raise ValueError("所选 Kimulator 未提供支持的公开模拟接口身份，请安装含 simulate 的版本")
    args.tools = {name: data["path"] for name, data in identity["tools"].items() if data.get("path")}
    for name in ("kompile", "krun", "kast", "kdist"):
        if name not in args.tools:
            raise ValueError(f"所选组件缺少 {name}；请检查其安装环境")
    for name in ("kompile", "krun", "kast"):
        if not re.search(
            r"(?<![\w.])v" + re.escape(identity["kframework_version"]) + r"(?![\w.])",
            identity["tools"][name]["version"],
        ):
            raise ValueError(f"{name} 与组件 kframework {identity['kframework_version']} 版本不一致")
    args.tools["verilator"] = tool(args.verilator or "verilator")
    service = Path(args.kcirct_root or SERVICE).expanduser().resolve()
    args.diffvcd = Path(args.diffvcd or service / "scripts/diffvcd.py").expanduser().resolve(strict=True)
    native = subprocess.run(
        [args.tools["verilator"], "--version"], capture_output=True, text=True, check=True, timeout=30
    )
    return {
        "protocol": PROTOCOL,
        "python": sys.version,
        "kimulator_executable": args.kimulator,
        "kimulator": identity,
        "verilator": {"path": args.tools["verilator"], "version": native.stdout + native.stderr},
        "diffvcd": {"path": str(args.diffvcd), "sha256": sha(args.diffvcd)},
    }


def prepare(args: argparse.Namespace) -> None:
    versions = environment(args)
    work = ROOT / ".runs/validation" / ("prepare-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    work.mkdir(parents=True, exist_ok=False)
    save(work / "versions.json", versions)
    command([args.tools["kdist"], "--verbose", "build", "circt-semantics.llvm"], work, "kdist-build", 600, args.env)
    definition = BUILD / "kdist/circt-semantics/llvm"
    command(
        [
            args.tools["kast"],
            str(BUILD / "parser"),
            "--gen-parser",
            "--bison-stack-max-depth",
            "1000000000",
            "--sort",
            "TopLevel",
            "--definition",
            str(definition),
        ],
        work,
        "parser-build",
        300,
        args.env,
    )
    versions.update(
        {
            "definition_sha256": sha(definition / "definition.kore"),
            "compiled_artifact_sha256": compiled_artifact_hashes(),
            "parser_sha256": sha(BUILD / "parser"),
        }
    )
    save(BUILD / "prepared.json", versions)
    save(work / "prepared.json", versions)
    print(f"组件的定义与 parser 已准备：{work}", flush=True)


def compiled_artifact_hashes() -> dict[str, str]:
    """绑定实际参与 LLVM 执行的编译产物，避免只校验语义文本。"""
    definition = BUILD / "kdist/circt-semantics/llvm"
    return {name: sha(definition / name) for name in ("definition.kore", "compiled.bin", "backend.txt", "interpreter")}


def verify_prepared(versions: dict) -> dict:
    prepared = json.loads((BUILD / "prepared.json").read_text())
    old, new = prepared.get("kimulator", {}), versions["kimulator"]
    if (
        any(old.get(k) != new[k] for k in ("semantics_hashes", "kframework_version", "kdist_plugin_sha256"))
        or any(
            old.get("tools", {}).get(n, {}).get("version") != new["tools"][n]["version"]
            for n in ("kompile", "krun", "kast")
        )
        or prepared["parser_sha256"] != sha(BUILD / "parser")
        or prepared["definition_sha256"] != sha(BUILD / "kdist/circt-semantics/llvm/definition.kore")
        or prepared.get("compiled_artifact_sha256") != compiled_artifact_hashes()
    ):
        raise ValueError("编译定义、工具版本或 parser 已变化，请先 make prepare")
    return prepared


def resource_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"实验资源路径必须位于实验目录内：{relative}")
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError(f"实验资源路径越界：{relative}")
    return resolved


def validate_manifest(manifest: dict) -> None:
    """用上游配置核验源替换及测试关联，不把 manifest 本身当独立依据。"""
    config_path = resource_path(manifest["project_toml"])
    config = tomllib.loads(config_path.read_text())
    project = config["project"]
    layout = json.loads(resource_path(manifest["layout_file"]).read_text())["files"]

    def mapped(upstream: str) -> str:
        if upstream not in layout:
            raise ValueError(f"layout 缺少上游文件映射：{upstream}")
        resource_path(layout[upstream])
        return layout[upstream]

    expected_sources = [mapped(p) for p in project["sources"]]
    bugs = [b for b in config["bugs"] if b["name"] == manifest["variant_id"]]
    if len(bugs) != 1:
        raise ValueError("上游 bugs 未唯一关联该变体")
    bug = bugs[0]
    if (
        manifest["top"] != project["toplevel"]
        or manifest["golden_sources"] != expected_sources
        or manifest["bug_original"] != mapped(bug["original"])
        or manifest["bug_source"] != mapped(bug["buggy"])
    ):
        raise ValueError("manifest 的 top/源替换与 project.toml 不符")
    tests = [
        t for t in config["testbenches"] if "table" in t and ("bugs" not in t or manifest["variant_id"] in t["bugs"])
    ]
    selected = [t for t in tests if mapped(t["table"]) == manifest["csv"]]
    if len(selected) != 1 or selected[0] != manifest["selected_testbench"]:
        raise ValueError("CSV 与 project.toml 的 bugs 关联不符")
    required_files = set(
        expected_sources + [manifest["bug_source"], manifest["csv"], manifest["project_toml"], manifest["layout_file"]]
    )
    if not required_files.issubset(manifest["source_hashes"]):
        raise ValueError("必需来源文件没有 SHA256")
    ports = manifest["inputs"] + manifest["outputs"]
    names = [p["name"] for p in ports]
    if len(names) != len(set(names)) or any(type(p["width"]) is not int or p["width"] < 1 for p in ports):
        raise ValueError("端口重复或位宽无效")
    if {"name": manifest["clock"], "width": 1} not in manifest["inputs"]:
        raise ValueError("时钟必须为 1 位输入")
    if not set(manifest["oracle_outputs"]).issubset(p["name"] for p in manifest["outputs"]):
        raise ValueError("oracle 引用了非输出端口")
    if len(set(manifest["oracle_outputs"])) != len(manifest["oracle_outputs"]):
        raise ValueError("oracle 输出重复")
    if manifest["sample_phase"] != "low_before_posedge_pre_NBA":
        raise ValueError("尚未实现该采样阶段")
    if manifest["initialization"]["mode"] != "rtl_initial_plus_two_state_zero":
        raise ValueError("尚未实现该初始化策略")
    if manifest["initialization"]["uninitialized_register_value"] != 0:
        raise ValueError("尚未实现非零的缺省初始化")


def load_rows(manifest: dict) -> tuple[list[dict], list[dict]]:
    """只接受有来源的掩码和 S1 已确认的单个尾随空列。"""
    path = resource_path(manifest["csv"])
    data = list(csv.reader(path.read_text().splitlines(), skipinitialspace=True))
    if len(data) < 2:
        raise ValueError("CSV 没有样本")
    header = [name.strip() for name in data[0]]
    if len(header) != len(set(header)) or any(not n for n in header):
        raise ValueError("CSV 表头为空或重复")
    ports = {p["name"]: p["width"] for p in manifest["inputs"] + manifest["outputs"]}
    required = {p["name"] for p in manifest["inputs"]} - {manifest["clock"]}
    required.update(manifest["oracle_outputs"])
    if set(header) != required:
        raise ValueError(f"CSV 列不符：缺少 {required-set(header)}，额外 {set(header)-required}")
    if not manifest["oracle_outputs"]:
        raise ValueError("oracle 比较集合为空")
    masks = {(m["sample_index"], m["signal"]): m for m in manifest.get("masks", [])}
    if len(masks) != len(manifest.get("masks", [])):
        raise ValueError("掩码单元格重复")
    used_masks, normalizations, rows = set(), [], []
    for i, cells in enumerate(data[1:]):
        if (
            len(cells) == len(header) + 1
            and not cells[-1].strip()
            and manifest.get("csv_normalization", {}).get("allow_one_trailing_empty_field") is True
        ):
            cells = cells[:-1]
            normalizations.append({"sample_index": i, "kind": "documented_single_trailing_empty_field"})
        if len(cells) != len(header):
            raise ValueError(f"CSV 样本 {i} 列数不符")
        row = {}
        for name, value in zip(header, cells, strict=True):
            token = value.strip()
            if token.lower() in ("-", "x", "z"):
                mask = masks.get((i, name))
                if not mask or token.lower() != mask["token"].lower() or name not in manifest["oracle_outputs"]:
                    raise ValueError(f"样本 {i}/{name} 有未授权的未知值 {token}")
                used_masks.add((i, name))
                row[name] = None
            else:
                number = int(token, 10)
                if number < 0 or number >= 1 << ports[name]:
                    raise ValueError(f"样本 {i}/{name} 超出 i{ports[name]} 位宽：{number}")
                row[name] = number
        rows.append(row)
    if used_masks != set(masks):
        raise ValueError("manifest 的掩码没有对应 CSV 单元格")
    if "samples" in manifest and len(rows) != manifest["samples"]:
        raise ValueError("CSV 样本数量与 manifest 不一致")
    if not any(row[n] is not None for row in rows for n in manifest["oracle_outputs"]):
        raise ValueError("oracle 全部被掩码排除")
    return rows, normalizations


def compare(expected: list[dict], actual: list[dict], names: list[str]) -> dict:
    if not names or not expected or len(expected) != len(actual):
        raise ValueError("比较集合为空或样本数量不一致")
    differences, count, masked = [], 0, 0
    for i, (left, right) in enumerate(zip(expected, actual, strict=True)):
        for name in names:
            if name not in right:
                raise ValueError(f"缺少必须输出 {name}")
            if left[name] is None:
                masked += 1
                continue
            count += 1
            if left[name] != right[name]:
                differences.append({"sample_index": i, "signal": name, "expected": left[name], "actual": right[name]})
    if not count:
        raise ValueError("没有已定义值参与比较")
    return {
        "agrees": not differences,
        "compared_cells": count,
        "masked_cells": masked,
        "first_mismatch": differences[0] if differences else None,
        "mismatches": differences,
    }


def stimulus(manifest: dict, rows: list[dict]) -> dict:
    events = []
    for i, row in enumerate(rows):
        for clock in [0, 1] if i + 1 < len(rows) else [0]:
            values = {
                p["name"]: clock if p["name"] == manifest["clock"] else row[p["name"]] for p in manifest["inputs"]
            }
            events.append({"time": len(events), "inputs": values})
    return {"schema_version": 1, "timescale": "1ns", "events": events}


def stimulus_path(manifest: dict) -> Path:
    return ROOT / "designs" / manifest["project_id"] / "testbench" / (manifest["variant_id"] + ".events.json")


def export_inputs(cases: list[str]) -> None:
    selected = CASES if cases == ["all-short"] else cases
    for identifier in selected:
        if identifier not in CASES:
            raise ValueError(f"未知案例：{identifier}")
        manifest = json.loads((ROOT / "manifests" / f"{identifier}.json").read_text())
        validate_manifest(manifest)
        trace = stimulus(manifest, load_rows(manifest)[0])
        target = stimulus_path(manifest)
        if target.exists() and json.loads(target.read_text()) != trace:
            raise ValueError(f"事件文件已有不同内容，请审阅后移走旧文件再生成：{target}")
        save(target, trace)
        print(f"输入事件：{target}")


def baseline(manifest: dict, variant: str) -> tuple[Path, dict]:
    """仿真直接消费版本管理的 generic MLIR，先验证其参数与当前 RTL 的对应关系。"""
    if variant not in ("golden", "buggy"):
        raise ValueError(f"未知设计组：{variant}")
    root = manifest.get("ir_baseline", f"designs/{manifest['project_id']}/mlir/{manifest['variant_id']}")
    folder = resource_path(root) / variant
    provenance = json.loads((folder / "provenance.json").read_text())
    for key in ("top", "parameters", "effective_parameters", "frontend_args"):
        if provenance["configuration"][key] != manifest[key]:
            raise ValueError(f"持久化 MLIR 的 {key} 与当前 manifest 不一致")
    if provenance["configuration"].get("ir_profile") != manifest.get("ir_profile"):
        raise ValueError("持久化 MLIR 的 ir_profile 与当前 manifest 不一致")
    profile = manifest.get("ir_profile")
    if profile is not None:
        if profile != "constant-initial-register-v1":
            raise ValueError(f"未知 IR 转换策略：{profile}")
        required = {"frontend.pre-llhd.generic.mlir", "frontend.hw.generic.mlir", "initialized.hw.generic.mlir",
                    "initial-lowering.json", "design.mlir", "design.generic.mlir", "design.debug.generic.mlir", "source-map.json"}
        if not required <= provenance["artifacts"].keys():
            raise ValueError("初始化转换基线缺少必须的证明工件")
        if provenance.get("initialization") != manifest["initialization"]:
            raise ValueError("初始化转换基线与 manifest 的初值策略不一致")
        initialization = manifest["initialization"]
        if (initialization.get("mode") != "rtl_initial_plus_two_state_zero"
            or type(initialization.get("uninitialized_register_value")) is not int
            or initialization["uninitialized_register_value"] != 0
            or initialization.get("four_state_equivalence_claimed") is not False):
            raise ValueError("初始化转换只支持明确的二态默认零初值策略")
        if provenance.get("generation", {}).get("normalization", {}).get("policy") != profile:
            raise ValueError("初始化转换基线缺少匹配的归一化策略")
        for name in required:
            if resource_path(provenance["artifacts"][name]["path"]) != folder / name:
                raise ValueError("初始化转换证明工件必须位于同一版本目录")
    executable = provenance["artifacts"]["design.generic.mlir"]
    if resource_path(executable["path"]) != folder / "design.generic.mlir":
        raise ValueError("持久化 MLIR 的可执行文件与 provenance 不一致")
    sources = (
        manifest["golden_sources"]
        if variant == "golden"
        else [
            manifest["bug_source"] if source == manifest["bug_original"] else source
            for source in manifest["golden_sources"]
        ]
    )
    if [entry["path"] for entry in provenance["rtl_sources"]] != sources:
        raise ValueError("持久化 MLIR 的 RTL 来源不一致")
    for record in [*provenance["rtl_sources"], *provenance["artifacts"].values()]:
        if sha(resource_path(record["path"])) != record["sha256"]:
            raise ValueError(f"持久化 MLIR 来源或产物 SHA256 不一致：{record['path']}")
    if profile is not None:
        audit = json.loads((folder / "initial-lowering.json").read_text())
        if (audit.get("policy") != "proven-single-initial-to-preset-v1" or not audit.get("replacements")
            or audit.get("input_sha256") != {
                "raw_hw_generic": sha(folder / "frontend.hw.generic.mlir"),
                "pre_llhd_generic": sha(folder / "frontend.pre-llhd.generic.mlir")}
            or audit.get("output_sha256") != sha(folder / "initialized.hw.generic.mlir")):
            raise ValueError("初始化转换记录未绑定实际输入输出")
    return folder / "design.generic.mlir", provenance


def run_k(manifest: dict, variant: str, inputs_path: Path, work: Path, args: argparse.Namespace) -> dict:
    """仅启动公开 CLI；Kore/编译/仿真/端口读取全部由外部组件负责。"""
    work.mkdir(parents=True, exist_ok=False)
    try:
        mlir, provenance = baseline(manifest, variant)
        save(work / "ir-baseline.json", provenance)
        output = work / "test.vcd"
        argv = [
            args.kimulator,
            "simulate",
            str(mlir),
            "--top-module",
            manifest["top"],
            "--inputs",
            str(inputs_path),
            "--output",
            str(output),
            "--work-dir",
            str(work / "simulation"),
            "--evaluations-per-input",
            "2",
            "--definition-dir",
            str(BUILD / "kdist/circt-semantics/llvm"),
            "--parser",
            str(BUILD / "parser"),
            "--timeout",
            str(manifest["timeout_s"]),
            "--keep-states",
        ]
        events = json.loads(inputs_path.read_text())["events"]
        timeout = manifest["timeout_s"] * (2 * len(events) + 5) + 60
        command(argv, work, "kimulator", timeout, args.env)
        result = json.loads((work / "simulation/result.json").read_text())
        if result["status"] != "pass" or result["events_completed"] != len(events):
            raise ValueError("组件未完成全部输入事件")
        if result["simulation_calls"] != len(events) * 2 or not output.is_file():
            raise ValueError("组件未完成同输入双执行或没有生成 VCD")
        result.update({"vcd": str(output), "vcd_sha256": sha(output), "vcd_top": manifest["top"]})
        return result
    except Exception as error:
        (work / "error.txt").write_text(traceback.format_exc())
        result_file = work / "simulation/result.json"
        result = json.loads(result_file.read_text()) if result_file.exists() else {}
        return {
            **result,
            "status": (
                result.get("status", "timeout" if isinstance(error, TimeoutError) else "execution_error")
                if result.get("status") != "pass"
                else "execution_error"
            ),
            "error": str(error),
        }


def write_summary(out: Path, results: list[dict]) -> None:
    save(out / "results.json", results)
    fields = [
        "source_case_id",
        "variant_id",
        "protocol",
        "status",
        "samples",
        "vcd_events",
        "simulator_agrees_with_native",
        "bug_detected_by_oracle",
    ]
    with (out / "summary.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def run_directory(run_id: str | None) -> Path:
    if run_id is None:
        run_id = "vcd-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", run_id):
        raise ValueError("run-id 只能包含字母、数字、下划线和连字符")
    path = ROOT / ".runs" / run_id
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"运行目录已存在，拒绝覆盖：{path}")
    return path.resolve()


def finalize_case(result: dict) -> None:
    """先传播执行和证据保存失败，再综合波形对照与辅助 oracle。"""
    gn, gk, bn, bk = [result["backends"][key] for key in ("golden_native", "golden_k", "buggy_native", "buggy_k")]
    result["golden_native_oracle"] = gn.get("oracle", {}).get("agrees")
    result["golden_k_oracle"] = gk.get("oracle", {}).get("agrees")
    result["buggy_k_native"] = result["waveform_comparisons"].get("buggy", {}).get("agrees")
    result["simulator_agrees_with_native"] = all(
        result["waveform_comparisons"].get(v, {}).get("agrees") is True for v in ("golden", "buggy")
    )
    result["bug_detected_by_oracle"] = all(b.get("oracle", {}).get("agrees") is False for b in (bn, bk))
    result["first_bug_difference"] = bn.get("oracle", {}).get("first_mismatch")
    first_same = result["first_bug_difference"] == bk.get("oracle", {}).get("first_mismatch")
    failures = [b["status"] for b in (gn, gk, bn, bk) if b["status"] not in ("pass", "oracle_mismatch")]
    if failures:
        result["status"] = failures[0]
    elif all(
        (
            result["golden_native_oracle"],
            result["golden_k_oracle"],
            result["simulator_agrees_with_native"],
            result["bug_detected_by_oracle"],
            first_same,
        )
    ):
        result["status"] = "pass"
    else:
        result["status"] = "vcd_mismatch" if not result["simulator_agrees_with_native"] else "oracle_mismatch"


def run(args: argparse.Namespace) -> int:
    from native import run_native
    from waveform import compare_waveforms, read_samples

    out = run_directory(args.run_id)
    by_id = {
        m["variant_id"]: m
        for path in sorted((ROOT / "manifests").glob("*.json"))
        if "variant_id" in (m := json.loads(path.read_text()))
    }
    selected = CASES if args.cases == ["all-short"] else args.cases
    if len(selected) != len(set(selected)) or any(case not in by_id for case in selected):
        raise ValueError("cases 含未知或重复变体")
    versions = environment(args)
    prepared = verify_prepared(versions)
    out.mkdir(parents=True, exist_ok=False)
    save(out / "versions.json", versions)
    save(out / "prepared.json", prepared)
    save(
        out / "protocol.json",
        {
            "name": PROTOCOL,
            "evaluations_per_input": 2,
            "vcd_sampling": "每个低/高输入事件",
            "main_comparison": "全部顶层输入输出的 VCD diff",
            "auxiliary_oracle": "上游 CSV 的低电平采样",
            "component_boundary": "公开 CLI 的文件、参数、退出码；实验进程不导入 kcirct/pyk",
        },
    )
    for filename in ("runner.py", "native.py", "waveform.py"):
        shutil.copy2(ROOT / filename, out / filename)
    results = []
    for identifier in selected:
        m = by_id[identifier]
        case_dir = out / identifier
        case_dir.mkdir()
        save(case_dir / "manifest.json", m)
        r = {
            "source_case_id": m["source_case_id"],
            "variant_id": identifier,
            "protocol": PROTOCOL,
            "status": "not_run",
            "backends": {},
            "waveform_comparisons": {},
        }
        results.append(r)
        write_summary(out, results)
        print(f"开始 {identifier}：正常/缺陷 × Verilator/Kimulator，双执行后全事件 VCD", flush=True)
        try:
            validate_manifest(m)
            for name, expected in m["source_hashes"].items():
                if sha(resource_path(name)) != expected:
                    raise ValueError(f"源哈希不符：{name}")
            rows, normalizations = load_rows(m)
            save(case_dir / "csv-normalizations.json", normalizations)
            trace = stimulus(m, rows)
            stored_inputs = stimulus_path(m)
            if json.loads(stored_inputs.read_text()) != trace:
                raise ValueError("版控事件文件与来源 CSV 不一致，请审阅输入契约")
            inputs_path = case_dir / "test_data.json"
            shutil.copy2(stored_inputs, inputs_path)
            r.update({"samples": len(rows), "vcd_events": len(trace["events"])})
            times = [event["time"] for event in trace["events"]]
            low_times = [event["time"] for event in trace["events"] if event["inputs"][m["clock"]] == 0]
            for variant in ("golden", "buggy"):
                sources = [
                    resource_path(m["bug_source"] if variant == "buggy" and p == m["bug_original"] else p)
                    for p in m["golden_sources"]
                ]
                native_work = case_dir / variant / "native"
                try:
                    nr = run_native(m, sources, rows, native_work, verilator=args.tools["verilator"])
                    native_trace = json.loads(Path(nr["stimulus_json"]).read_text())
                    if native_trace != trace:
                        raise ValueError("两个后端的实际输入事件不一致")
                except Exception as error:
                    native_work.mkdir(parents=True, exist_ok=True)
                    (native_work / "error.txt").write_text(traceback.format_exc())
                    nr = {
                        "status": "timeout" if isinstance(error, subprocess.TimeoutExpired) else "execution_error",
                        "error": str(error),
                    }
                r["backends"][variant + "_native"] = nr
                kr = run_k(m, variant, inputs_path, case_dir / variant / "kimulator", args)
                r["backends"][variant + "_k"] = kr
                if nr["status"] == "pass" and kr["status"] == "pass":
                    comparison = compare_waveforms(
                        Path(kr["vcd"]),
                        Path(nr["vcd"]),
                        top=m["top"],
                        native_top=nr["vcd_top"],
                        ports=m["inputs"] + m["outputs"],
                        times=times,
                        work=case_dir / variant / "comparison",
                        diffvcd_path=args.diffvcd,
                    )
                    r["waveform_comparisons"][variant] = comparison
                    kr["native_comparison"] = comparison
                for label, backend in (("native", nr), ("k", kr)):
                    if backend["status"] == "pass":
                        try:
                            values = read_samples(
                                Path(backend["vcd"]), top=backend["vcd_top"], ports=m["outputs"], times=low_times
                            )
                            backend["samples"] = values
                            backend["oracle"] = compare(rows, values, m["oracle_outputs"])
                            if not backend["oracle"]["agrees"]:
                                backend["status"] = "oracle_mismatch"
                            with (
                                case_dir / variant / ("native" if label == "native" else "kimulator") / "output.csv"
                            ).open("w") as stream:
                                writer = csv.DictWriter(stream, fieldnames=[p["name"] for p in m["outputs"]])
                                writer.writeheader()
                                writer.writerows(values)
                        except Exception as error:
                            backend.update({"status": "execution_error", "error": str(error)})
                    save(case_dir / variant / ("native" if label == "native" else "kimulator") / "result.json", backend)
                print(
                    f"{identifier}/{variant}：native={nr['status']}，K={kr['status']}，VCD={r['waveform_comparisons'].get(variant, {}).get('agrees')}",
                    flush=True,
                )
                write_summary(out, results)
            finalize_case(r)
        except Exception as error:
            r.update({"status": "execution_error", "error": str(error)})
            (case_dir / "error.txt").write_text(traceback.format_exc())
        save(case_dir / "result.json", r)
        write_summary(out, results)
        print(f"完成 {identifier}：{r['status']}，证据 {case_dir}", flush=True)
    print(f"批次完成：{out}", flush=True)
    return int(any(result["status"] != "pass" for result in results))


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="把 Kimulator 作为外部组件执行双执行 VCD 对照实验")
    parser.add_argument("action", choices=["inputs", "prepare", "run"])
    parser.add_argument("--cases", nargs="+", default=["d13"], help="变体 ID 列表，或 all-short")
    parser.add_argument("--run-id", help="新的独立结果目录名；不覆盖已有证据")
    parser.add_argument(
        "--kimulator", default=os.environ.get("KIMULATOR"), help="安装后的 kcirct 可执行文件；默认 PATH"
    )
    parser.add_argument("--k-bin", type=Path, default=os.environ.get("K_BIN"), help="K 工具目录；默认组件的 PATH")
    parser.add_argument("--verilator", default=os.environ.get("VERILATOR"), help="Verilator 可执行文件；默认 PATH")
    parser.add_argument(
        "--kcirct-root", type=Path, default=os.environ.get("KCIRCT_ROOT"), help="默认查找 diffvcd 的 K-CIRCT 仓库位置"
    )
    parser.add_argument(
        "--diffvcd", type=Path, default=os.environ.get("DIFFVCD"), help="独立 diffvcd.py 路径，可脱离服务源码目录配置"
    )
    return parser


def main() -> int:
    args = argument_parser().parse_args()
    if args.action == "inputs":
        export_inputs(args.cases)
    elif args.action == "prepare":
        prepare(args)
    else:
        return run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
