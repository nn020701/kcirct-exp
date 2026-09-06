"""分别汇总历史 CSV 与外部 CLI 双执行 VCD，保存可分享的原始波形证据。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RUNS = ROOT / ".runs"
VCD_PROTOCOL = "external-cli-double-eval-vcd-v1"


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comparison(value: dict | None) -> dict | None:
    if value is None:
        return None
    return {
        key: value.get(key)
        for key in ["agrees", "compared_cells", "masked_cells", "first_mismatch"]
    } | {"mismatch_count": len(value.get("mismatches", []))}


def compact_result(original: dict, run: str) -> dict:
    variant = original["variant_id"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", variant):
        raise ValueError(f"无效变体名称：{variant!r}")
    backends, blockers = {}, []
    for name, backend in original.get("backends", {}).items():
        detail = {
            "status": backend["status"],
            "stage": backend.get("stage"),
            "timings_s": backend.get("timings", {}),
            "oracle": comparison(backend.get("oracle")),
            "native_comparison": comparison(backend.get("native_comparison")),
        }
        source_variant, source_backend = name.split("_", 1)
        source_backend = "kimulator" if source_backend == "k" else source_backend
        raw_output = (
            f".runs/{run}/{variant}/{source_variant}/{source_backend}/output.csv"
        )
        index_file = ROOT / "evidence/index.json"
        artifacts = (
            json.loads(index_file.read_text())["artifacts"]
            if index_file.exists()
            else []
        )
        matches = [item for item in artifacts if item["source"] == raw_output]
        if matches:
            artifact = matches[0]
            output = ROOT / artifact["path"]
            if digest(output) != artifact["sha256"]:
                raise ValueError(f'关键输出证据哈希不一致：{artifact["path"]}')
            detail["output_csv"] = artifact["path"]
            detail["output_sha256"] = artifact["sha256"]
        if backend["status"] not in ("pass", "oracle_mismatch", "not_run"):
            blockers.append(
                {
                    "backend": name,
                    "status": backend["status"],
                    "stage": backend.get("stage", "unknown"),
                }
            )
        backends[name] = detail
    fields = [
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
    ]
    result = {key: original.get(key) for key in fields}
    result.update(
        {
            "run_id": run,
            "backends": backends,
            "blockers": blockers,
            "raw_result": f".runs/{run}/{variant}/result.json",
        }
    )
    evidence = sorted(
        {detail["output_csv"] for detail in backends.values() if "output_csv" in detail}
    )
    if evidence:
        result["evidence"] = evidence
    raw_result = ROOT / result["raw_result"]
    if raw_result.exists():
        result["raw_result_sha256"] = digest(raw_result)
    return result


def selected_runs(requested: list[str] | None, *, vcd: bool = False) -> list[str]:
    selection = RESULTS / "vcd/selection.json" if vcd else RESULTS / "selection.json"
    if requested:
        runs = requested
    elif selection.exists():
        runs = json.loads(selection.read_text())["formal_run_ids"]
    elif vcd:
        raise ValueError("首次 VCD 汇总必须用 --runs 显式选择新协议批次；不能自动采用历史 CSV 批次")
    else:
        runs = [
            path.name
            for path in sorted(
                RUNS.iterdir() if RUNS.exists() else [],
                key=lambda path: (path.stat().st_mtime_ns, path.name),
            )
            if path.is_dir() and (path / "results.json").exists()
        ]
    if not runs:
        raise ValueError("没有可汇总的运行；请先运行案例或使用 --runs 指定正式批次")
    if len(set(runs)) != len(runs):
        raise ValueError("正式批次列表不能重复")
    for run in runs:
        if (
            not isinstance(run, str)
            or not re.fullmatch(r"[A-Za-z0-9_.-]+", run)
            or run in (".", "..")
        ):
            raise ValueError(f"运行名称必须为单个目录名：{run!r}")
        if not (RUNS / run / "results.json").is_file():
            raise FileNotFoundError(
                f"缺少运行归档：.runs/{run}/results.json；已发布精简结果仍可直接阅读"
            )
    return runs


def flag(value: Any) -> str:
    return "一致" if value is True else "不一致" if value is False else "未完成"


def markdown(summary: dict) -> str:
    counts = summary["counts"]
    lines = [
        "# 正式运行结果",
        "",
        f'固定短池实际运行 **{counts["variants_attempted"]} 个缺陷变体 / {counts["source_cases_attempted"]} 个原始案例**，'
        f'共 {counts["csv_samples_attempted"]} 条已知独立 CSV 采样（{counts["unknown_sample_count"]} 个变体样本数未知）；完整通过 **{counts["variants_passed"]} 个变体 / '
        f'{counts["source_cases_passed"]} 个原始案例**，共 {counts["csv_samples_passed"]} 条采样。',
        "",
        "完整通过要求正常原生和正常 K 满足独立 oracle，正常/缺陷 K 分别与对应原生全部规定观测一致，"
        "并且缺陷两后端保留相同首次 oracle 差异。不同后端、正常/缺陷版本和重复运行不增加独立案例数。",
        "",
        "| 原案例 | 变体 | 采样 | 正常原生/oracle | 正常 K/oracle | 缺陷 K/原生 | 缺陷首次 oracle 差异 | 当前状态 |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for result in summary["cases"]:
        first = result.get("first_bug_difference")
        difference = (
            f'{first["sample_index"]}: {first["signal"]} {first["expected"]} → {first["actual"]}'
            if first
            else "未获得"
        )
        lines.append(
            f'| {result["source_case_id"]} | [{result["variant_id"]}](results/cases/{result["variant_id"]}.json) | '
            f'{result["samples"] if result["samples"] is not None else "未知"} | {flag(result.get("golden_native_oracle"))} | '
            f'{flag(result.get("golden_k_oracle"))} | {flag(result.get("buggy_k_native"))} | '
            f'{difference} | {result["status"]} |'
        )
    lines += [
        "",
        "未完成 K 执行的行，其首次差异来自已完成的缺陷原生运行，不能算作 K 重现成功。",
        "",
        "## 统计来源",
        "",
        f'本表从 {len(summary["formal_run_ids"])} 个指定正式批次、{counts["case_attempts"]} 次批量案例尝试生成；'
        "同一变体选用清单中最后一次结果。正式批次选择保存在 [selection.json](results/selection.json)，"
        "迁移检查和其他验证不会自动进入已有正式清单。",
        "",
        "| 批次 | 案例尝试数 | 原始结果 SHA256 |",
        "|---|---:|---|",
    ]
    for run in summary["source_runs"]:
        lines.append(f'| {run["run_id"]} | {run["case_count"]} | `{run["sha256"]}` |')
    lines += [
        "",
        "精简机器表：[JSON](results/summary.json)、[CSV](results/summary.csv)；"
        "保留每次尝试的状态和首次差异：[attempts.json](results/attempts.json)。"
        "关键原始输出、状态窗口和来源哈希见 [evidence/index.json](evidence/index.json)。",
        "",
        "## 结论的适用范围",
        "",
        "这是固定配置、外部输入轨迹和独立检查依据下的有限仿真重现，不是形式化证明，"
        "也不表示无需驱动适配就兼容全部 SV/C++ 测试环境。D13/S3 完整原 TB 轨迹和 D8 的13条共有前缀另有对照；"
        "D8 的最后一条由完整外部 CSV 验证。",
        "",
        "阶段耗时保留在机器结果中，包含进程启动及 Kore I/O；验证期间的并行运行成本不能用作公平性能倍率。"
        "本表只由实际案例结果计算，不将历史单元测试数量写成迁移后的验证结论。",
        "",
        "当前卡点见 [STATUS.md](STATUS.md)，使用方法见 [README.md](README.md)，"
        "三例详细分析见 [failure-analysis.md](failure-analysis.md)。本轮未开发 Error-trace；"
        "后续功能需求见 [error-trace-requirements.md](error-trace-requirements.md)。",
        "",
    ]
    return "\n".join(lines)


def publish_artifact(source: Path, target: Path, artifacts: dict[str, dict], expected: str | None = None) -> dict:
    """原字节导出；同名证据已存在时只接受相同哈希，避免改写已发布运行。"""
    source = source.resolve(strict=True)
    checksum = digest(source)
    if expected is not None and checksum != expected:
        raise ValueError(f"VCD 证据哈希不一致：{source}")
    if target.exists() and digest(target) != checksum:
        raise ValueError(f"拒绝覆盖不同内容的已发布证据：{target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(source, target)
    try:
        origin = str(source.relative_to(ROOT.resolve()))
    except ValueError:
        origin = str(source)
    item = {
        "path": str(target.relative_to(ROOT)),
        "source": origin,
        "sha256": checksum,
        "bytes": source.stat().st_size,
    }
    artifacts[item["path"]] = item
    return item


def publish_case(original: dict, run: str, artifacts: dict[str, dict]) -> dict:
    """导出完整波形与诊断入口；体积较大的 Kore 状态和本机构建仍保留在 .runs。"""
    variant = original["variant_id"]
    if not isinstance(variant, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", variant):
        raise ValueError(f"无效变体名称：{variant!r}")
    source_root = (RUNS / run / variant).resolve()
    destination = ROOT / "evidence/vcd" / run / variant
    selected = {
        "result.json", "manifest.json", "test_data.json", "csv-normalizations.json", "error.txt",
        "commands.json", "commands.jsonl", "versions.json", "sampling-contract.json", "driver.cpp",
        "stimulus.hex", "stimulus.json", "inputs.json", "ir-baseline.json", "output.csv",
        "trace.vcd", "test.vcd", "state.json", "states.json",
    }
    case_artifacts = []
    if source_root.exists():
        for path in sorted(source_root.rglob("*")):
            relative = path.relative_to(source_root)
            if not path.is_file() or "obj" in relative.parts or "states" in relative.parts:
                continue
            # 成功 K 调用的空 stderr 已由 commands.jsonl 的哈希确认，避免导出数千个过程空文件。
            if path.suffix == ".stderr" and path.stat().st_size == 0:
                continue
            if path.name in selected or path.suffix in (".log", ".stderr") or path.name.endswith((".stdout.txt", ".stderr.txt")):
                case_artifacts.append(publish_artifact(path, destination / relative, artifacts))
    comparisons = {}
    for design_variant, value in original.get("waveform_comparisons", {}).items():
        if design_variant not in ("golden", "buggy"):
            raise ValueError(f"无效 VCD 对照组：{design_variant}")
        detail = {key: value.get(key) for key in (
            "agrees", "exit_code", "compared_signals", "event_count", "first_mismatch", "errors", "normalization"
        )}
        detail["artifacts"] = {}
        for label, record in value.get("artifacts", {}).items():
            source = Path(record["path"])
            if not source.is_absolute():
                source = ROOT / source
            if label == "diffvcd_script":
                target = ROOT / "evidence/vcd" / run / "tools/diffvcd.py"
            else:
                try:
                    target = destination / source.resolve().relative_to(source_root)
                except ValueError as error:
                    raise ValueError(f"VCD 工件超出本案例目录：{record['path']}") from error
            detail["artifacts"][label] = publish_artifact(source, target, artifacts, record["sha256"])
        comparisons[design_variant] = detail
    backends, blockers = {}, []
    for name, value in original.get("backends", {}).items():
        detail = {key: value.get(key) for key in (
            "status", "stage", "error", "events_total", "events_completed", "simulation_calls",
            "simulation_calls_attempted", "evaluations_per_input", "vcd_top", "vcd_sha256"
        )}
        detail["timings_s"] = value.get("timings", {})
        detail["oracle"] = comparison(value.get("oracle"))
        group, backend = name.split("_", 1)
        backend = "kimulator" if backend == "k" else backend
        detail["evidence"] = [entry for entry in case_artifacts if f"/{group}/{backend}/" in entry["path"]]
        if name.endswith("_k"):
            detail["native_comparison"] = comparisons.get(group)
        if value["status"] not in ("pass", "oracle_mismatch", "not_run"):
            blockers.append({"backend": name, "status": value["status"], "stage": value.get("stage"), "error": value.get("error")})
        backends[name] = detail
    fields = [
        "source_case_id", "variant_id", "protocol", "samples", "vcd_events", "status", "error",
        "golden_native_oracle", "golden_k_oracle", "buggy_k_native", "simulator_agrees_with_native",
        "bug_detected_by_oracle", "first_bug_difference",
    ]
    result = {key: original.get(key) for key in fields}
    result.update({
        "run_id": run, "backends": backends, "waveform_comparisons": comparisons, "blockers": blockers,
        "raw_result": f".runs/{run}/{variant}/result.json", "evidence": case_artifacts,
    })
    return result


def validate_vcd_record(original: dict) -> None:
    if original.get("protocol") != VCD_PROTOCOL:
        raise ValueError(f"案例 {original.get('variant_id')} 不是 {VCD_PROTOCOL}，不能纳入 VCD 正式报告")
    for value in original.get("waveform_comparisons", {}).values():
        for record in value.get("artifacts", {}).values():
            path = Path(record["path"])
            if not path.is_absolute():
                path = ROOT / path
            if digest(path) != record["sha256"]:
                raise ValueError(f"VCD 证据哈希不一致：{path}")
    if original.get("status") != "pass":
        return
    count = original.get("vcd_events")
    if type(count) is not int or count <= 0:
        raise ValueError("VCD 成功记录缺少有效事件数")
    for group in ("golden", "buggy"):
        value = original.get("waveform_comparisons", {}).get(group, {})
        required = {"kimulator_vcd", "native_vcd", "preflight", "diffvcd_script", "command", "stdout", "stderr"}
        if (value.get("agrees") is not True or value.get("exit_code") != 0 or value.get("errors")
                or value.get("event_count") != count or not value.get("compared_signals")
                or not required.issubset(value.get("artifacts", {}))):
            raise ValueError(f"VCD 成功记录缺少完整 {group} 波形对照证据")
        backend = original.get("backends", {}).get(group + "_k", {})
        if backend.get("events_completed") != count or backend.get("simulation_calls") != 2 * count:
            raise ValueError(f"VCD 成功记录未完成 {group} 全事件同输入双执行")


def waveform_cell(value: dict | None) -> str:
    if value is None:
        return "未完成"
    artifacts = value.get("artifacts", {})
    if not {"kimulator_vcd", "native_vcd"}.issubset(artifacts):
        return "未完成"
    return (
        f'{flag(value.get("agrees"))} · [K]({artifacts["kimulator_vcd"]["path"]}) / '
        f'[Verilator]({artifacts["native_vcd"]["path"]})'
    )


def vcd_markdown(summary: dict) -> str:
    counts = summary["counts"]
    lines = [
        "# 外部组件双执行 VCD 正式结果", "",
        f'协议：`{VCD_PROTOCOL}`。实际尝试 {counts["variants_attempted"]} 个变体 / '
        f'{counts["source_cases_attempted"]} 个来源案例，完整通过 {counts["variants_passed"]} 个变体 / '
        f'{counts["source_cases_passed"]} 个来源案例。', "",
        f'输入共 {counts["csv_samples_attempted"]} 条 CSV 行，展开为 {counts["vcd_events_attempted"]} 个 low/high 事件；'
        f'通过案例覆盖 {counts["vcd_events_passed"]} 个事件。每个事件的 Kimulator 调用在同一输入下执行两次后 dump，'
        "Verilator eval 完成后 dump；两版各自比较全部顶层输入和输出。事件数不重复乘以设计版本或后端数量。", "",
        "完整通过还要求正常两后端满足低电平 CSV oracle，缺陷两后端触发同一首次 oracle 差异。"
        "缺陷版 oracle_mismatch 可以是预期结果；超时、解析失败、部分波形及 VCD 不一致均不能通过。", "",
        "本页 pass 仅表示上述 VCD 与 oracle 协议通过。内部状态不变性等额外检查及未解决问题见 "
        "[STATUS.md](STATUS.md)，不能由波形一致推定内部状态完整性通过。", "",
        "| 案例 | 变体 | CSV / 事件 | 正常 VCD | 缺陷 VCD | 状态 | 首个波形差异或阻塞 |",
        "|---|---|---:|---|---|---|---|",
    ]
    for row in summary["cases"]:
        comparisons = row["waveform_comparisons"]
        issues = []
        for group, value in comparisons.items():
            first = value.get("first_mismatch")
            if first:
                issues.append(f'{group}: t={first["time"]} {first["signal"]}, Verilator={first["expected"]}, K={first["actual"]}')
            issues.extend(value.get("errors") or [])
        issues.extend(f'{item["backend"]}: {item["status"]} / {item.get("stage") or "未知阶段"}' for item in row["blockers"])
        issue = "; ".join(issues) or (row.get("error") or "无")
        issue = issue.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f'| {row["source_case_id"]} | [{row["variant_id"]}](results/vcd/cases/{row["variant_id"]}.json) | '
            f'{row["samples"]} / {row["vcd_events"]} | {waveform_cell(comparisons.get("golden"))} | '
            f'{waveform_cell(comparisons.get("buggy"))} | {row["status"]} | {issue} |'
        )
    lines += [
        "", "## 证据与统计范围", "",
        "[selection.json](results/vcd/selection.json) 固定正式批次；同一变体采用清单中最后一次尝试。"
        "[summary.json](results/vcd/summary.json)、[summary.csv](results/vcd/summary.csv) 保存当前结果，"
        "[attempts.json](results/vcd/attempts.json) 保留全部入选尝试。", "",
        "| 批次 | 案例尝试 | 批量原始结果 SHA256 |", "|---|---:|---|",
    ]
    for run in summary["source_runs"]:
        lines.append(f'| {run["run_id"]} | {run["case_count"]} | `{run["sha256"]}` |')
    lines += [
        "", "[evidence/vcd/index.json](evidence/vcd/index.json) 保存本报告原始 VCD、事件输入、CLI 结果、"
        "实际命令、工具版本、比较日志与错误诊断的路径和 SHA256。文件按原字节导出；日志中的绝对路径表示"
        "运行时来源，重新运行使用 [README](README.md) 的可配置命令。干净检出可直接打开波形并查看失败证据，"
        "无需本地 .runs；重新生成报告仍需要完整原始归档。", "",
        "历史单执行低电平 CSV 结果保留在 [RUNS.md](RUNS.md)，不计入本表的 VCD 通过数量。"
        "当前结论与卡点见 [STATUS.md](STATUS.md)，单个用户的外部组件流程见 [USER_WORKFLOW.md](USER_WORKFLOW.md)。", "",
        "这些结果验证固定输入、参数和二态初始化下的有限波形对照；不将接口可用性当作用户研究结论。"
        "未开发 Error-trace，保存的普通仿真状态仍需独立分析。", "",
    ]
    return "\n".join(lines)


def report_vcd(requested: list[str] | None) -> None:
    runs = selected_runs(requested, vcd=True)
    sources = []
    # 在导出前检查整个选择，禁止混入历史单执行 CSV 的成功记录。
    for run in runs:
        records = json.loads((RUNS / run / "results.json").read_text())
        if not isinstance(records, list):
            raise ValueError("批量 results.json 必须是逐案例数组")
        for original in records:
            validate_vcd_record(original)
        sources.append((run, records))
    artifacts, attempts, latest, origins = {}, [], {}, []
    for run, records in sources:
        run_root = RUNS / run
        run_evidence = []
        for filename in ("results.json", "versions.json", "protocol.json", "prepared.json", "batch-exit.json", "runner.py", "native.py", "waveform.py"):
            if (run_root / filename).is_file():
                run_evidence.append(publish_artifact(run_root / filename, ROOT / "evidence/vcd" / run / "run" / filename, artifacts))
        origins.append({"run_id": run, "path": f".runs/{run}/results.json", "sha256": digest(run_root / "results.json"),
                        "case_count": len(records), "evidence": run_evidence})
        for original in records:
            result = publish_case(original, run, artifacts)
            attempts.append(result)
            latest[result["variant_id"]] = result
    rows = list(latest.values())
    passed = [row for row in rows if row["status"] == "pass"]
    cases = {row["source_case_id"] for row in rows}
    counts = {
        "case_attempts": len(attempts), "variants_attempted": len(rows), "source_cases_attempted": len(cases),
        "variants_passed": len(passed),
        "source_cases_passed": sum(all(row["status"] == "pass" for row in rows if row["source_case_id"] == case) for case in cases),
        "csv_samples_attempted": sum(row["samples"] or 0 for row in rows),
        "csv_samples_passed": sum(row["samples"] or 0 for row in passed),
        "vcd_events_attempted": sum(row["vcd_events"] or 0 for row in rows),
        "vcd_events_passed": sum(row["vcd_events"] or 0 for row in passed),
        "unknown_sample_count": sum(row["samples"] is None for row in rows),
    }
    summary = {"schema_version": 1, "protocol": VCD_PROTOCOL, "formal_run_ids": runs,
               "source_runs": origins, "counts": counts, "cases": rows}
    target = RESULTS / "vcd"
    save(target / "selection.json", {"schema_version": 1, "protocol": VCD_PROTOCOL, "formal_run_ids": runs,
                                    "policy": "显式选择双执行 VCD 批次；历史 CSV 结果不得计入"})
    save(target / "summary.json", summary)
    save(target / "attempts.json", attempts)
    for row in rows:
        save(target / "cases" / f'{row["variant_id"]}.json', row)
    for path in (target / "cases").glob("*.json"):
        if path.stem not in latest:
            path.unlink()
    fields = ["source_case_id", "variant_id", "samples", "vcd_events", "status", "simulator_agrees_with_native", "bug_detected_by_oracle", "run_id"]
    with (target / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    save(ROOT / "evidence/vcd/index.json", {"schema_version": 1, "protocol": VCD_PROTOCOL,
                                          "formal_run_ids": runs, "artifacts": list(artifacts.values())})
    (ROOT / "VCD_RUNS.md").write_text(vcd_markdown(summary))
    print(json.dumps(counts, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取 .runs，独立生成历史 CSV 或新协议 VCD 报告；不修改运行归档"
    )
    parser.add_argument(
        "--protocol", choices=["csv", "vcd"], default="csv",
        help="csv 保留历史低电平报告；vcd 单独导出外部组件双执行波形报告",
    )
    parser.add_argument(
        "--runs",
        nargs="+",
        help="按顺序指定正式批次；省略则使用 results/selection.json",
    )
    args = parser.parse_args()
    if args.protocol == "vcd":
        report_vcd(args.runs)
        return
    runs = selected_runs(args.runs)
    attempts, latest, origins = [], {}, []
    for run in runs:
        path = RUNS / run / "results.json"
        records = json.loads(path.read_text())
        if not isinstance(records, list):
            raise ValueError(f"{path.name} 必须是逐案例结果数组")
        origins.append(
            {
                "run_id": run,
                "path": f".runs/{run}/results.json",
                "sha256": digest(path),
                "case_count": len(records),
            }
        )
        for original in records:
            result = compact_result(original, run)
            attempts.append(
                {
                    key: result[key]
                    for key in [
                        "run_id",
                        "source_case_id",
                        "variant_id",
                        "samples",
                        "status",
                        "first_bug_difference",
                        "blockers",
                        "raw_result",
                    ]
                }
            )
            latest[result["variant_id"]] = result
    rows = list(latest.values())
    passed = [row for row in rows if row["status"] == "pass"]
    case_ids = {row["source_case_id"] for row in rows}
    counts = {
        "case_attempts": len(attempts),
        "variants_attempted": len(rows),
        "source_cases_attempted": len(case_ids),
        "variants_passed": len(passed),
        "source_cases_passed": sum(
            all(
                row["status"] == "pass" for row in rows if row["source_case_id"] == case
            )
            for case in case_ids
        ),
        "csv_samples_attempted": sum(
            row["samples"] for row in rows if row["samples"] is not None
        ),
        "csv_samples_passed": sum(
            row["samples"] for row in passed if row["samples"] is not None
        ),
        "unknown_sample_count": sum(row["samples"] is None for row in rows),
    }
    summary = {
        "schema_version": 1,
        "formal_run_ids": runs,
        "source_runs": origins,
        "counts": counts,
        "cases": rows,
    }
    save(
        RESULTS / "selection.json",
        {
            "schema_version": 1,
            "formal_run_ids": runs,
            "policy": "显式选择正式批次；保留重跑前结果，迁移验证不自动计入",
        },
    )
    save(RESULTS / "summary.json", summary)
    save(RESULTS / "attempts.json", attempts)
    for row in rows:
        save(RESULTS / "cases" / f'{row["variant_id"]}.json', row)
    # 此目录是当前选择的派生视图，历史结果仍保存在不可变的 .runs 中。
    for old_case in (RESULTS / "cases").glob("*.json"):
        if old_case.stem not in latest:
            old_case.unlink()
    fields = [
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
        "run_id",
    ]
    with (RESULTS / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        json.dumps(row[key], ensure_ascii=False)
                        if isinstance(row.get(key), dict)
                        else row.get(key)
                    )
                    for key in fields
                }
            )
    (ROOT / "RUNS.md").write_text(markdown(summary))
    print(json.dumps(counts, ensure_ascii=False))


if __name__ == "__main__":
    main()
