"""外部缺陷普通仿真实验；先验证 oracle，再比较两个仿真后端。"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib
import importlib.metadata
import json
import os
import re
import shlex
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
STATUSES = (
    "not_run",
    "frontend_failure",
    "unsupported_semantics",
    "execution_error",
    "timeout",
    "oracle_mismatch",
    "pass",
)


def save(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv: list[str], work: Path, label: str, timeout: float = 120) -> tuple[str, float]:
    """保存命令和失败日志，超时终止该命令的整个进程组。"""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    process = subprocess.Popen(
        argv, cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        timed_out = True
    elapsed = time.perf_counter() - start
    (work / f"{label}.stderr.txt").write_text(stderr)
    # Kore 输出由调用方保存为状态文件；避免每次重复保存一份大状态。
    if "krun" not in Path(argv[0]).name or process.returncode:
        (work / f"{label}.stdout.txt").write_text(stdout)
    item = {
        "argv": argv,
        "cwd": str(work),
        "exit_code": process.returncode,
        "timeout": timed_out,
        "seconds": elapsed,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stdout_bytes": len(stdout.encode()),
        "stderr": f"{label}.stderr.txt",
    }
    with (work / "commands.jsonl").open("a") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")
    if timed_out:
        raise TimeoutError(f"{label} 超过 {timeout} 秒；日志：{work}")
    if process.returncode:
        raise RuntimeError(f"{label} 退出码 {process.returncode}：{stderr[-4000:]}")
    return stdout, elapsed


def service_root(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "kcirct_root", None) or os.environ.get("KCIRCT_ROOT") or SERVICE).expanduser().resolve()


def tool(name: str, directory: Path | None = None) -> str:
    requested = str(directory / name) if directory is not None else name
    found = shutil.which(requested)
    if found is None:
        raise ValueError(f"缺少可执行工具：{requested}")
    # 保留符号链接入口；K 的 launcher 可能依据入口目录寻找安装资源。
    return str(Path(found).absolute())


def validate_service_imports(service: Path) -> dict:
    """核对实际执行模块与所选源码，拒绝仅哈希另一个工作树的情况。"""
    expected = {"api": service / "src/kcirct/api.py", "plugin": service / "src/kcirct/kdist/plugin.py"}
    for path in expected.values():
        if not path.is_file():
            raise ValueError(f"所选 KCIRCT_ROOT 缺少源码：{path}")
    entries = list(importlib.metadata.entry_points(group="kdist", name="circt-semantics"))
    if len(entries) != 1 or entries[0].value != "kcirct.kdist.plugin":
        raise ValueError("当前 Python 环境必须唯一注册 circt-semantics 的 kcirct.kdist.plugin；请安装所选服务")
    modules = {
        "api": importlib.import_module("kcirct.api"),
        "plugin": importlib.import_module(entries[0].value),
    }
    for name, module in modules.items():
        actual = Path(module.__file__).resolve()
        if actual != expected[name].resolve():
            raise ValueError(f"实际导入 {name} 来源不符：{actual}；所选服务要求 {expected[name]}，请安装所选服务")
    plugin = modules["plugin"]
    if Path(plugin.__TARGETS__["source"].SRC_DIR).resolve() != expected["plugin"].parent.resolve():
        raise ValueError("kdist source target 与所选服务不符")
    if Path(modules["api"].kdist.kdist_dir).resolve() != (BUILD / "kdist").resolve():
        raise ValueError("kdist 已在错误的 KDIST_DIR 下导入；请启动新的 Python 进程")
    return {name: str(path.resolve()) for name, path in expected.items()}


def environment(args: argparse.Namespace) -> dict:
    service = service_root(args)
    directories = {}
    for name, variable in [("k_bin", "K_BIN"), ("circt_bin", "CIRCT_BIN")]:
        value = getattr(args, name, None) or os.environ.get(variable)
        directories[name] = Path(value).expanduser().resolve() if value else None
    tools = {name: tool(name, directories["k_bin"]) for name in ("kompile", "krun", "kast")}
    tools.update({name: tool(name, directories["circt_bin"]) for name in ("circt-verilog", "circt-opt")})
    tools["verilator"] = tool(getattr(args, "verilator", None) or os.environ.get("VERILATOR") or "verilator")
    # CIRCT 使用已解析的绝对入口；将它的目录加入 PATH 可能遮蔽已经核验的 K 工具。
    prefixes = [str(directories["k_bin"])] if directories["k_bin"] is not None else []
    search_path = [str(Path(part or ".").absolute()) for part in os.environ.get("PATH", "").split(os.pathsep)]
    os.environ["PATH"] = os.pathsep.join(prefixes + search_path)
    for name in ("kompile", "krun", "kast"):
        if tool(name) != tools[name]:
            raise ValueError(f"{name} 的运行入口与已选工具不符：{tool(name)} != {tools[name]}")
    if "PYTHONPATH" in os.environ:
        # prepare 的子进程切换到证据目录后，仍须从父进程核验过的相同目录导入插件。
        os.environ["PYTHONPATH"] = os.pathsep.join(
            str(Path(part or ".").absolute()) for part in os.environ["PYTHONPATH"].split(os.pathsep)
        )
    os.environ["KDIST_DIR"] = str(BUILD / "kdist")
    imports = validate_service_imports(service)
    args.tools = tools
    args.kcirct_root = service
    versions = {
        "python": sys.version,
        "python_executable": sys.executable,
        "pyk": importlib.metadata.version("kframework"),
        "KDIST_DIR": os.environ["KDIST_DIR"],
        "kcirct_root": str(service),
        "imports": imports,
        "PYTHONPATH": os.environ.get("PYTHONPATH"),
    }
    for name in ("kompile", "krun", "kast"):
        path = tools[name]
        p = subprocess.run([path, "--version"], capture_output=True, text=True, check=True, timeout=30)
        versions[name] = {"path": path, "realpath": str(Path(path).resolve()), "version": p.stdout + p.stderr}
        if not re.search(r"(?<![\w.])v" + re.escape(versions["pyk"]) + r"(?![\w.])", versions[name]["version"]):
            raise ValueError(
                f'{name}（{path}）与 pyk {versions["pyk"]} 版本不匹配；实际：{versions[name]["version"].strip()}'
            )
    for name in ("circt-verilog", "circt-opt", "verilator"):
        path = tools[name]
        p = subprocess.run([path, "--version"], capture_output=True, text=True, check=True, timeout=30)
        versions[name] = {"path": path, "realpath": str(Path(path).resolve()), "version": p.stdout + p.stderr}
    versions["service_head"] = subprocess.check_output(
        ["git", "-C", str(service), "rev-parse", "HEAD"], text=True
    ).strip()
    versions["semantics_hashes"] = {
        str(p.relative_to(service)): sha(p)
        for p in sorted((service / "src/kcirct/kdist/circt_semantics").rglob("*"))
        if p.suffix in (".k", ".md")
    }
    versions["api_sha256"] = sha(service / "src/kcirct/api.py")
    versions["kdist_plugin_sha256"] = sha(service / "src/kcirct/kdist/plugin.py")
    return versions


def prepare(args: argparse.Namespace) -> None:
    versions = environment(args)
    work = ROOT / ".runs/validation" / ("prepare-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    work.mkdir(parents=True, exist_ok=False)
    save(work / "versions.json", versions)
    _, duration = command(
        [sys.executable, "-m", "pyk.kdist", "--verbose", "build", "circt-semantics.llvm"],
        work,
        "kdist-build",
        600,
    )
    definition = BUILD / "kdist/circt-semantics/llvm"
    _, parser_s = command(
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
    )
    versions.update(
        {
            "definition_sha256": sha(definition / "definition.kore"),
            "parser_sha256": sha(BUILD / "parser"),
            "build_s": duration,
            "parser_s": parser_s,
        }
    )
    save(BUILD / "prepared.json", versions)
    save(work / "prepared.json", versions)
    print(f"定义与 parser 已准备：{work}", flush=True)


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


def quiescence(state: Path) -> dict:
    text = state.read_text()
    checks = {name: f"Lbl'-LT-'{name}'-GT-'{{}}(dotk{{}}())" in text for name in ("prog", "setup", "cmd")}
    checks["currents_empty"] = "Lbl'-LT-'current-info'-GT-'" not in text and "Lbl'-LT-'current'-GT-'" not in text
    return checks


def archive_state(path: Path) -> dict:
    start = time.perf_counter()
    digest = sha(path)
    with path.open("rb") as source, gzip.open(str(path) + ".gz", "wb") as target:
        shutil.copyfileobj(source, target)
    path.unlink()
    return {"file": path.name + ".gz", "sha256_uncompressed": digest, "export_s": time.perf_counter() - start}


def source_map(work: Path) -> None:
    executable = work / "design.generic.mlir"
    debug = work / "design.debug.generic.mlir"
    op_pattern = re.compile(r'^\s*(?:(%[^=]+) = )?"([\w.]+)"\(')

    def ops(path):
        return [
            (i, line, op_pattern.match(line))
            for i, line in enumerate(path.read_text().splitlines(), 1)
            if op_pattern.match(line)
        ]

    eops, dops = ops(executable), ops(debug)
    if [m.group(2) for _, _, m in eops] != [m.group(2) for _, _, m in dops]:
        raise ValueError("debug/执行 IR 操作序列不一致，不能建立按序对应")
    save(
        work / "source-map.json",
        {
            "executable_sha256": sha(executable),
            "debug_sha256": sha(debug),
            "mapping_kind": "same_ir_printed_with_and_without_locations",
            "location_aliases": [s for s in debug.read_text().splitlines() if s.startswith("#loc")],
            "operations": [
                {
                    "ordinal": n,
                    "op": em.group(2),
                    "ssa": (em.group(1) or "").strip(),
                    "executable_line": ei,
                    "debug_line": di,
                    "debug_text": dl,
                }
                for n, ((ei, _, em), (di, dl, _)) in enumerate(zip(eops, dops, strict=True))
            ],
        },
    )


def bind_k_command(argv: list[str], tools: dict[str, str]) -> list[str]:
    name = Path(argv[0]).name
    if name in ("kompile", "krun", "kast"):
        return [tools[name], *argv[1:]]
    return argv


def run_k(manifest: dict, sources: list[Path], rows: list[dict], work: Path, args: argparse.Namespace) -> dict:
    validate_service_imports(service_root(args))
    import kcirct.api as api

    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    previous_paths = {
        name: getattr(api, name) for name in ("TOP_LEVEL_PARSER", "WORKING_DIR", "DATA_DIR", "PARSER_DIR")
    }
    api.TOP_LEVEL_PARSER = BUILD / "parser"
    api.WORKING_DIR = work / "api-work"
    api.DATA_DIR = work / "api-work/tmp"
    api.PARSER_DIR = BUILD
    previous_run = api.KCIRCT.run
    seq = 0
    stage = "frontend"
    timings, events, samples, archives = {}, [], [], []

    def archive(path):
        item = archive_state(path)
        archives.append(item)
        timings["state_export"] = timings.get("state_export", 0) + item["export_s"]
        save(work / "state-archives.json", archives)

    def logged_run(argv):
        nonlocal seq
        label = f"k-command-{seq:04d}"
        seq += 1
        stdout, elapsed = command(bind_k_command(argv, args.tools), work, label, manifest["timeout_s"])
        return api.KCIRCT.Result(stdout, elapsed)

    api.KCIRCT.run = staticmethod(logged_run)
    try:
        frontend = [
            args.tools["circt-verilog"],
            "--ir-hw",
            "--top=" + manifest["top"],
            "--mlir-print-debuginfo",
            *manifest.get("frontend_args", []),
        ]
        frontend += [f"-G{name}={value}" for name, value in manifest.get("parameters", {}).items()]
        frontend += [str(p) for p in sources] + ["-o", str(work / "design.mlir")]
        _, timings["frontend"] = command(frontend, work, "frontend", manifest["timeout_s"])
        for suffix, flags in [("debug.generic", ["--mlir-print-debuginfo"]), ("generic", [])]:
            _, timings[suffix] = command(
                [
                    args.tools["circt-opt"],
                    str(work / "design.mlir"),
                    "--mlir-print-op-generic",
                    *flags,
                    "-o",
                    str(work / f"design.{suffix}.mlir"),
                ],
                work,
                suffix,
                manifest["timeout_s"],
            )
        source_map(work)
        text = (work / "design.generic.mlir").read_text()
        modules = re.findall(r'module_type = !hw.modty<([^>]+)>[^\n]*sym_name = "([^"]+)"', text)
        top = next(ports for ports, name in modules if name == manifest["top"])
        inputs = [{"name": n, "width": int(w)} for n, w in re.findall(r"input (\w+) : i(\d+)", top)]
        outputs = [{"name": n, "width": int(w)} for n, w in re.findall(r"output (\w+) : i(\d+)", top)]
        if {p["name"]: p["width"] for p in inputs} != {p["name"]: p["width"] for p in manifest["inputs"]}:
            raise ValueError("实际 IR 输入端口/位宽与 manifest 不一致")
        if {p["name"]: p["width"] for p in outputs} != {p["name"]: p["width"] for p in manifest["outputs"]}:
            raise ValueError("实际 IR 输出端口/位宽与 manifest 不一致")
        save(work / "ports.json", {"inputs_in_ir_order": inputs, "outputs": outputs})
        inventory = {}
        for op in re.findall(r'"([a-z]+\.[a-zA-Z0-9_.]+)"\(', text):
            inventory[op] = inventory.get(op, 0) + 1
        save(work / "op-inventory.json", inventory)
        stage = "compile"
        k = api.KCIRCT()
        for name, fn in [
            ("compile", lambda: k.compile_fast(work / "design.generic.mlir", work / "pgm.kore")),
            ("preprocess", lambda: k.run_preprocess_fast(work / "pgm.kore", work / "preprocessed.kore")),
            ("setup", lambda: k.run_setup_fast(work / "preprocessed.kore", work / "setup.kore", manifest["top"])),
        ]:
            stage = name
            start = time.perf_counter()
            fn()
            timings[name] = time.perf_counter() - start
        state = work / "setup.kore"
        if not all(quiescence(state).values()):
            raise NotImplementedError(f"setup 后有待执行内容：{quiescence(state)}")
        stage = "execution"
        for i, row in enumerate(rows):
            for clock in [0, 1] if i + 1 < len(rows) else [0]:
                values = [(clock if p["name"] == manifest["clock"] else row[p["name"]], p["width"]) for p in inputs]
                target = work / f"event-{len(events):04d}.kore"
                start = time.perf_counter()
                k.run_simulate_fast(state, target, values)
                elapsed = time.perf_counter() - start
                checks = quiescence(target)
                if not all(checks.values()):
                    save(
                        work / "pending.json",
                        {"sample_index": i, "clock": clock, "state": target.name, "checks": checks},
                    )
                    raise NotImplementedError(f"事件 {len(events)} 无法执行至静止：{checks}")
                start = time.perf_counter()
                ports = k.read_ports_fast(target)
                actual = {}
                for p in outputs:
                    value, width = ports[manifest["top"] + "/" + p["name"]]
                    if width != p["width"] or not isinstance(value, int) or value < 0 or value >= 1 << width:
                        raise ValueError(f'输出位宽/值不符：{p["name"]}={value}:{width}')
                    actual[p["name"]] = value
                read_s = time.perf_counter() - start
                event = {
                    "event_index": len(events),
                    "sample_index": i,
                    "clock": clock,
                    "observed": clock == 0,
                    "phase": manifest["sample_phase"] if clock == 0 else "posedge_update",
                    "inputs": dict(zip((p["name"] for p in inputs), (v for v, _ in values), strict=True)),
                    "outputs": actual,
                    "execution_s": elapsed,
                    "read_s": read_s,
                    "state": target.name + ".gz",
                    "sha256_uncompressed": sha(target),
                    "quiescent": checks,
                }
                events.append(event)
                if clock == 0:
                    samples.append(actual)
                save(work / "events.json", events)
                archive(state)
                archive(target.with_suffix(".kore.prestate"))
                state = target
        archive(state)
        timings["execution"] = sum(e["execution_s"] for e in events)
        timings["read_ports"] = sum(e["read_s"] for e in events)
        with (work / "output.csv").open("w") as stream:
            writer = csv.DictWriter(stream, fieldnames=[p["name"] for p in outputs])
            writer.writeheader()
            writer.writerows(samples)
        result = {"status": "pass", "samples": samples, "timings": timings}
    except Exception as error:
        (work / "error.txt").write_text(traceback.format_exc())
        status = (
            "timeout"
            if isinstance(error, TimeoutError)
            else (
                "unsupported_semantics"
                if isinstance(error, NotImplementedError)
                else "frontend_failure" if stage == "frontend" else "execution_error"
            )
        )
        result = {"status": status, "stage": stage, "error": str(error), "samples": samples, "timings": timings}
    finally:
        api.KCIRCT.run = staticmethod(previous_run)
        for name, path in previous_paths.items():
            setattr(api, name, path)
        for path in sorted(work.glob("*.kore*")):
            if path.is_file() and path.suffix != ".gz":
                archive(path)
    save(work / "result.json", result)
    return result


def write_summary(out: Path, results: list[dict]) -> None:
    save(out / "results.json", results)
    columns = [
        "source_case_id",
        "variant_id",
        "samples",
        "status",
        "golden_native_oracle",
        "golden_k_oracle",
        "buggy_k_native",
        "simulator_agrees_with_native",
        "bug_detected_by_oracle",
        "first_bug_difference",
        "phase_timings",
        "evidence",
    ]
    with (out / "results.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for item in results:
            writer.writerow(
                {
                    k: json.dumps(item[k], ensure_ascii=False) if isinstance(item.get(k), (dict, list)) else item.get(k)
                    for k in columns
                }
            )
    cases = shlex.join([r["variant_id"] for r in results])
    replay = f'"${{PYTHON:-python3}}" "$experiment_root/runner.py" run --cases {cases} "$@"'
    (out / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\n"
        "# 每次创建独立结果目录；先用当前环境执行 prepare。工具配置从环境或参数读取。\n"
        'experiment_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)\n' + replay + "\n"
    )


def run_directory(run_id: str | None) -> Path:
    name = run_id or datetime.now(timezone.utc).strftime("batch-%Y%m%dT%H%M%S.%fZ")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) or name == "validation":
        raise ValueError("run-id 必须是单个目录名（字母数字开头，可含 ._-），且不能为 validation")
    path = (ROOT / ".runs" / name).resolve()
    if not path.is_relative_to((ROOT / ".runs").resolve()):
        raise ValueError("run-id 目录越界")
    return path


def run(args: argparse.Namespace) -> None:
    out = run_directory(args.run_id)
    manifests = [
        json.loads(p.read_text())
        for p in sorted((ROOT / "manifests").glob("*.json"))
        if p.name not in ("inventory.json", "schema.json")
    ]
    by_id = {m["variant_id"]: m for m in manifests if "variant_id" in m}
    selected = (
        ["d13", "s3", "s1b", "s1r", "d8", "d12", "d11", "d4", "s2", "c4"] if args.cases == ["all-short"] else args.cases
    )
    if len(selected) != len(set(selected)):
        raise ValueError("cases 不能重复")
    for identifier in selected:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", identifier) or identifier not in by_id:
            raise ValueError(f"未知案例：{identifier}")
    versions = environment(args)
    prepared = json.loads((BUILD / "prepared.json").read_text())
    if (
        prepared["semantics_hashes"] != versions["semantics_hashes"]
        or any(prepared.get(key) != versions[key] for key in ("pyk", "api_sha256", "kdist_plugin_sha256"))
        or any(
            prepared.get(name, {}).get("version") != versions[name]["version"] for name in ("kompile", "krun", "kast")
        )
        or prepared["parser_sha256"] != sha(BUILD / "parser")
        or prepared["definition_sha256"] != sha(BUILD / "kdist/circt-semantics/llvm/definition.kore")
    ):
        raise ValueError("语义或 parser 已变化，请先重新 prepare")
    out.mkdir(parents=True, exist_ok=False)
    save(out / "versions.json", versions)
    save(out / "prepared.json", prepared)
    save(
        out / "arguments.json",
        {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
    )
    for filename in ("runner.py", "native.py"):
        shutil.copy2(ROOT / filename, out / filename)
    service = service_root(args)
    shutil.copy2(service / "src/kcirct/api.py", out / "api.py")
    (out / "service.patch").write_text(
        subprocess.check_output(
            ["git", "-C", str(service), "diff", "--", "src/kcirct/kdist/circt_semantics", "src/kcirct/api.py"],
            text=True,
        )
    )
    results = []
    for identifier in selected:
        m = by_id[identifier]
        case_dir = out / identifier
        case_dir.mkdir()
        save(case_dir / "manifest.json", m)
        r = {
            "source_case_id": m["source_case_id"],
            "variant_id": identifier,
            "status": "not_run",
            "evidence": str(case_dir.relative_to(ROOT)),
            "backends": {},
        }
        results.append(r)
        write_summary(out, results)
        try:
            validate_manifest(m)
            for filename, expected_hash in m["source_hashes"].items():
                if sha(resource_path(filename)) != expected_hash:
                    raise ValueError(f"源哈希不符：{filename}")
            rows, normalizations = load_rows(m)
            save(case_dir / "csv-normalizations.json", normalizations)
            r["samples"] = len(rows)
            source_lists = {
                "golden": [resource_path(p) for p in m["golden_sources"]],
                "buggy": [resource_path(m["bug_source"] if p == m["bug_original"] else p) for p in m["golden_sources"]],
            }
            if m["bug_original"] not in m["golden_sources"]:
                raise ValueError("缺陷替换文件不在正常源列表中")
            for variant, sources in source_lists.items():
                native_work = case_dir / variant / "native"
                native_work.mkdir(parents=True)
                try:
                    from native import run_native

                    native_result = run_native(m, sources, rows, native_work, verilator=args.tools["verilator"])
                    if "samples" not in native_result:
                        native_result["samples"] = native_result["rows"]
                except Exception as error:
                    (native_work / "error.txt").write_text(traceback.format_exc())
                    native_result = {
                        "status": (
                            "timeout"
                            if isinstance(error, (TimeoutError, subprocess.TimeoutExpired))
                            else "execution_error"
                        ),
                        "error": str(error),
                    }
                r["backends"][variant + "_native"] = native_result
                if native_result["status"] == "pass":
                    native_result["oracle"] = compare(rows, native_result["samples"], m["oracle_outputs"])
                    if not native_result["oracle"]["agrees"]:
                        native_result["status"] = "oracle_mismatch"
                save(native_work / "result.json", native_result)
                print(identifier, variant, "native", native_result["status"], flush=True)
                k_result = run_k(m, sources, rows, case_dir / variant / "kimulator", args)
                r["backends"][variant + "_k"] = k_result
                if k_result["status"] == "pass":
                    k_result["oracle"] = compare(rows, k_result["samples"], m["oracle_outputs"])
                    if not k_result["oracle"]["agrees"]:
                        k_result["status"] = "oracle_mismatch"
                    if "oracle" in native_result:
                        k_result["native_comparison"] = compare(
                            native_result["samples"], k_result["samples"], [p["name"] for p in m["outputs"]]
                        )
                save(case_dir / variant / "kimulator/result.json", k_result)
                print(identifier, variant, "kimulator", k_result["status"], flush=True)
                write_summary(out, results)
            gn, gk, bn, bk = [r["backends"][key] for key in ("golden_native", "golden_k", "buggy_native", "buggy_k")]
            r["phase_timings"] = {name: backend.get("timings", {}) for name, backend in r["backends"].items()}
            r["golden_native_oracle"] = gn.get("oracle", {}).get("agrees")
            r["golden_k_oracle"] = gk.get("oracle", {}).get("agrees")
            r["buggy_k_native"] = bk.get("native_comparison", {}).get("agrees")
            r["simulator_agrees_with_native"] = all(
                b.get("native_comparison", {}).get("agrees") is True for b in (gk, bk)
            )
            r["bug_detected_by_oracle"] = all(b.get("oracle", {}).get("agrees") is False for b in (bn, bk))
            r["first_bug_difference"] = bn.get("oracle", {}).get("first_mismatch")
            first_same = r["first_bug_difference"] == bk.get("oracle", {}).get("first_mismatch")
            if all(
                (
                    r["golden_native_oracle"],
                    r["golden_k_oracle"],
                    r["simulator_agrees_with_native"],
                    r["bug_detected_by_oracle"],
                    first_same,
                )
            ):
                r["status"] = "pass"
            else:
                failures = [b["status"] for b in (gn, gk, bn, bk) if b["status"] not in ("pass", "oracle_mismatch")]
                r["status"] = failures[0] if failures else "oracle_mismatch"
        except Exception as error:
            r["status"] = "execution_error"
            r["error"] = str(error)
            (case_dir / "error.txt").write_text(traceback.format_exc())
        save(case_dir / "result.json", r)
        write_summary(out, results)
    print(f'完成：{sum(r["status"] == "pass" for r in results)}/{len(results)} 个变体完整通过；{out}', flush=True)


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="普通仿真外部缺陷实验与证据归档")
    parser.add_argument("action", choices=["prepare", "run"])
    parser.add_argument("--cases", nargs="+", default=["d13"], help="变体 ID 列表，或 all-short")
    parser.add_argument("--run-id", help="新的独立结果目录名；已存在时拒绝覆盖")
    parser.add_argument(
        "--kcirct-root",
        type=Path,
        default=os.environ.get("KCIRCT_ROOT"),
        help="K 服务根目录；默认相邻 circt-semantics，可用 KCIRCT_ROOT 设置",
    )
    parser.add_argument(
        "--k-bin", type=Path, default=os.environ.get("K_BIN"), help="K 工具目录；默认 PATH，可用 K_BIN 设置"
    )
    parser.add_argument(
        "--circt-bin",
        type=Path,
        default=os.environ.get("CIRCT_BIN"),
        help="CIRCT 工具目录；默认 PATH，可用 CIRCT_BIN 设置",
    )
    parser.add_argument(
        "--verilator",
        default=os.environ.get("VERILATOR"),
        help="Verilator 可执行文件或命令名；默认 PATH，可用 VERILATOR 设置",
    )
    return parser


def main() -> None:
    args = argument_parser().parse_args()
    if args.action == "prepare":
        prepare(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
