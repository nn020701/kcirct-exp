"""从原始 RTL 生成保留常量 initial 的独立 MLIR 版本；仿真仍只消费持久化 IR。"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import time
from pathlib import Path

import runner
from initial_lowering import normalize_initial_registers

ROOT = runner.ROOT
PROFILE = "constant-initial-register-v1"
OP = re.compile(r'^\s*(?:(%[^=]+) = )?"([\w.]+)"\(')


def source_map(executable: Path, debug: Path) -> dict:
    """关联同一 IR 的无位置执行文本与带位置调试文本，不猜测源行。"""
    left, right = executable.read_text().splitlines(), debug.read_text().splitlines()
    eops = [(i, OP.match(line)) for i, line in enumerate(left, 1) if OP.match(line)]
    dops = [(i, OP.match(line)) for i, line in enumerate(right, 1) if OP.match(line)]
    if [m.group(2) for _, m in eops] != [m.group(2) for _, m in dops]:
        raise ValueError("执行与调试 IR 的 operation 序列不一致")
    return {
        "executable_sha256": runner.sha(executable),
        "debug_sha256": runner.sha(debug),
        "mapping_kind": "same_ir_printed_with_and_without_locations",
        "location_aliases": [line for line in right if line.startswith("#loc")],
        "operations": [
            {"ordinal": ordinal, "op": em.group(2), "ssa": (em.group(1) or "").strip(),
             "executable_line": ei, "debug_line": di, "debug_text": right[di - 1]}
            for ordinal, ((ei, em), (di, _)) in enumerate(zip(eops, dops, strict=True))
        ],
    }


def record(path: Path, destination: Path | None = None) -> dict:
    return {"path": (destination or path).relative_to(ROOT).as_posix(),
            "sha256": runner.sha(path), "bytes": path.stat().st_size}


def generate(manifest: dict, generation: str, binaries: dict[str, str]) -> Path:
    """两组均通过转换及 CIRCT verifier 后才发布，已有版本不覆盖。"""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", generation):
        raise ValueError("generation 必须是单个可见目录名")
    runner.validate_manifest(manifest)
    if manifest["initialization"]["mode"] != "rtl_initial_plus_two_state_zero":
        raise ValueError("本转换只用于明确声明 RTL initial 加二态零初始化策略的案例")
    for name, digest in manifest["source_hashes"].items():
        if runner.sha(runner.resource_path(name)) != digest:
            raise ValueError(f"来源哈希不一致：{name}")
    target = ROOT / "designs" / manifest["project_id"] / "mlir" / manifest["variant_id"] / generation
    if target.exists():
        raise FileExistsError(f"已有 IR 版本不可覆盖：{target}")
    staging = ROOT / ".work/ir-preparation" / generation / manifest["variant_id"]
    staging.mkdir(parents=True, exist_ok=False)
    versions = {}
    for name, binary in binaries.items():
        result = subprocess.run([binary, "--version"], text=True, capture_output=True, check=True, timeout=30)
        versions[name] = result.stdout + result.stderr
    for variant in ("golden", "buggy"):
        work = staging / variant
        work.mkdir()
        sources = [manifest["bug_source"] if variant == "buggy" and name == manifest["bug_original"] else name
                   for name in manifest["golden_sources"]]
        commands = []

        def invoke(name: str, args: list[str], stage: str) -> None:
            entry = {"stage": stage, "argv": [name, *args], "cwd": "external-defects/",
                     "resolved_tool": binaries[name], "exit_code": None, "timeout": False}
            commands.append(entry)
            runner.save(work / "commands.json", commands)
            start = time.monotonic()
            with (work / f"{stage}.stdout.txt").open("wb") as stdout, (work / f"{stage}.stderr.txt").open("wb") as stderr:
                try:
                    process = subprocess.Popen([binaries[name], *args], cwd=ROOT, stdout=stdout, stderr=stderr, start_new_session=True)
                    try:
                        entry["exit_code"] = process.wait(timeout=120)
                    except subprocess.TimeoutExpired:
                        entry["timeout"] = True
                        os.killpg(process.pid, signal.SIGKILL)
                        entry["exit_code"] = process.wait()
                        raise TimeoutError(f"{stage} 超过 120 秒；命令和输出已保存：{work}")
                except BaseException as error:
                    entry["error"] = str(error)
                    raise
                finally:
                    entry["seconds"] = time.monotonic() - start
                    runner.save(work / "commands.json", commands)
            if entry["exit_code"]:
                raise ValueError(f"{stage} 转换失败；证据：{work}；{(work / f'{stage}.stderr.txt').read_text()[-1500:]}")

        def output(name: str) -> str:
            return (work / name).relative_to(ROOT).as_posix()

        shared = ["--top=" + manifest["top"], "--mlir-print-debuginfo", "--mlir-print-op-generic",
                  *manifest["frontend_args"], *[f"-G{k}={v}" for k, v in manifest["parameters"].items()], *sources]
        for mode, filename in (("llhd", "frontend.pre-llhd.generic.mlir"), ("hw", "frontend.hw.generic.mlir")):
            invoke("circt-verilog", ["--ir-" + mode, *shared, "-o", output(filename)], "frontend-" + mode)
        normalized, audit = normalize_initial_registers(
            (work / "frontend.hw.generic.mlir").read_text(),
            (work / "frontend.pre-llhd.generic.mlir").read_text(),
        )
        (work / "initialized.hw.generic.mlir").write_text(normalized)
        runner.save(work / "initial-lowering.json", audit)
        invoke("circt-opt", [output("initialized.hw.generic.mlir"), "--llhd-sig2reg", "--canonicalize",
                             "--mlir-print-debuginfo", "-o", output("design.mlir")], "sig2reg")
        for debug, filename in ((True, "design.debug.generic.mlir"), (False, "design.generic.mlir")):
            invoke("circt-opt", [output("design.mlir"), "--mlir-print-op-generic",
                                 *(["--mlir-print-debuginfo"] if debug else []), "-o", output(filename)], filename)
        text = (work / "design.generic.mlir").read_text()
        if "!llhd." in text or '"llhd.' in text or "#llhd." in text:
            raise ValueError(f"转换后仍有 LLHD，拒绝发布：{work}")
        runner.save(work / "source-map.json", source_map(work / "design.generic.mlir", work / "design.debug.generic.mlir"))
        artifacts = {path.name: record(path, target / variant / path.name)
                     for path in work.iterdir() if path.suffix in (".mlir", ".json") and path.name != "commands.json"}
        old_prefix = work.relative_to(ROOT).as_posix()
        new_prefix = (target / variant).relative_to(ROOT).as_posix()
        portable = [{**{key: value for key, value in item.items() if key != "resolved_tool"},
                     "argv": [arg.replace(old_prefix + "/", new_prefix + "/") for arg in item["argv"]]}
                    for item in commands]
        runner.save(work / "provenance.json", {
            "schema_version": 1, "path_base": "external-defects/", "project_id": manifest["project_id"],
            "source_case_id": manifest["source_case_id"], "variant_id": manifest["variant_id"], "design_variant": variant,
            "configuration": {**{key: manifest[key] for key in ("top", "parameters", "effective_parameters", "frontend_args", "sample_phase")},
                              "ir_profile": PROFILE},
            "initialization": manifest["initialization"], "rtl_sources": [record(ROOT / name) for name in sources],
            "artifacts": artifacts, "tool_versions": versions,
            "generation": {"id": generation, "status": "generated_not_simulated", "working_directory": "external-defects/",
                           "commands": portable, "commands_policy": "已执行命令仅将暂存输出目录重定位为持久化目录；工具通过 PATH 或 CLI 参数解析。",
                           "normalization": {"policy": PROFILE, "script": record(ROOT / "initial_lowering.py"),
                                             "input": ["frontend.hw.generic.mlir", "frontend.pre-llhd.generic.mlir"],
                                             "output": "initialized.hw.generic.mlir", "audit": "initial-lowering.json"},
                           "generator": record(Path(__file__).resolve())},
            "location_policy": "从同一原始 RTL、相同参数与工具生成前后端 IR；相对 loc 保留原样。旧基线不覆盖。",
        })
    target.mkdir(parents=True, exist_ok=False)
    for variant in ("golden", "buggy"):
        shutil.copytree(staging / variant, target / variant,
                        ignore=shutil.ignore_patterns("*.stdout.txt", "*.stderr.txt", "commands.json"))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", required=True, choices=runner.CASES, help="要生成初始化转换 IR 的案例")
    parser.add_argument("--generation", required=True, help="新的版本目录名；已有版本不会覆盖")
    parser.add_argument("--circt-bin", default=os.environ.get("CIRCT_BIN"), help="CIRCT 工具目录；默认使用 PATH")
    parser.add_argument("--activate", action="store_true", help="生成成功后将 manifest 指向新版本")
    args = parser.parse_args()
    directory = Path(args.circt_bin).expanduser().resolve() if args.circt_bin else None
    binaries = {name: runner.tool(name, directory) for name in ("circt-verilog", "circt-opt")}
    for identifier in args.cases:
        path = ROOT / "manifests" / f"{identifier}.json"
        manifest = json.loads(path.read_text())
        target = generate(manifest, args.generation, binaries)
        candidate = {**manifest, "ir_baseline": target.relative_to(ROOT).as_posix(), "ir_profile": PROFILE}
        for variant in ("golden", "buggy"):
            runner.baseline(candidate, variant)
        if args.activate:
            runner.save(path, candidate)
        print(f"已保存 IR：{target}；{'已切换 manifest' if args.activate else 'manifest 未切换'}")


if __name__ == "__main__":
    main()
