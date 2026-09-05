"""从完整运行归档生成可移植正式结果，不复制状态、波形或机器相关错误路径。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RUNS = ROOT / ".runs"


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


def selected_runs(requested: list[str] | None) -> list[str]:
    if requested:
        runs = requested
    elif (RESULTS / "selection.json").exists():
        runs = json.loads((RESULTS / "selection.json").read_text())["formal_run_ids"]
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取 .runs，生成轻量正式结果和 RUNS.md；不修改运行归档"
    )
    parser.add_argument(
        "--runs",
        nargs="+",
        help="按顺序指定正式批次；省略则使用 results/selection.json",
    )
    args = parser.parse_args()
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
