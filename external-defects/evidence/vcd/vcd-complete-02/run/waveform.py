"""检查完整顶层端口契约，再以外部 diffvcd 工具比较两份波形。"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from vcdvcd import VCDVCD


def _artifact(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _validate_request(ports: list[dict], times: list[int]) -> None:
    if not times or any(type(time) is not int or time < 0 for time in times):
        raise ValueError("采样时刻必须是非空的非负整数列表")
    if sorted(set(times)) != times:
        raise ValueError("采样时刻必须严格递增且无重复")
    if not ports:
        raise ValueError("必须指定非空的顶层端口集合")
    names = set()
    for port in ports:
        name, width = port.get("name"), port.get("width")
        if not isinstance(name, str) or not name or type(width) is not int or width < 1:
            raise ValueError(f"端口契约无效：{port!r}")
        if name in names:
            raise ValueError(f"端口契约重复：{name}")
        names.add(name)


def _value(signal, time: int, *, name: str, width: int) -> int:
    raw = signal[time]
    if raw is None or not raw or set(raw) - {"0", "1"}:
        raise ValueError(f"端口 {name} 在时刻 {time} 没有确定的二态值：{raw!r}")
    value = int(raw, 2)
    if len(raw) > width or value >= 1 << width:
        raise ValueError(f"端口 {name} 在时刻 {time} 的采样值超出 i{width}：{raw!r}")
    return value


def _read(vcd: Path, top: str, ports: list[dict], times: list[int]) -> tuple[VCDVCD, dict, list[dict]]:
    _validate_request(ports, times)
    wave = VCDVCD(str(vcd))
    if wave.timescale.get("timescale") != Decimal("1e-9"):
        raise ValueError(f"{vcd.name} 时间单位必须为 1ns：{wave.timescale}")
    if wave.begintime > times[0] or wave.endtime < times[-1]:
        raise ValueError(
            f"{vcd.name} 时间窗口 [{wave.begintime}, {wave.endtime}] "
            f"未完整覆盖采样窗口 [{times[0]}, {times[-1]}]"
        )
    prefix = top.rstrip(".") + "."
    names = {}
    for port in ports:
        name, width = port["name"], port["width"]
        # 只匹配指定顶层，不能用内部同名信号代替缺失的外部端口。
        pattern = re.compile(re.escape(prefix + name) + r"(?:\[\d+:\d+\])?$")
        matches = [signal for signal in wave.signals if pattern.fullmatch(signal)]
        if len(matches) != 1:
            raise ValueError(f"{vcd.name} 必需顶层端口 {prefix}{name} 声明数量应为 1，实际为 {len(matches)}")
        full_name = matches[0]
        if int(wave[full_name].size) != width:
            raise ValueError(f"{vcd.name} 端口 {name} 位宽应为 i{width}，实际为 i{wave[full_name].size}")
        names[name] = full_name
    samples = [
        {
            port["name"]: _value(wave[names[port["name"]]], time, name=port["name"], width=port["width"])
            for port in ports
        }
        for time in times
    ]
    return wave, names, samples


def read_samples(vcd: Path, top: str, ports: list[dict], times: list[int]) -> list[dict]:
    """读取指定采样时刻的整数端口值；缺失、未知或错误位宽必须报错。"""
    return _read(vcd, top, ports, times)[2]


def _normalize_header(source: Path, target: Path, mappings: list[dict]) -> dict:
    """只删除指定 1 位端口声明中的 [0:0]；标识码、时间戳及取值正文保持原字节。"""
    data = source.read_bytes()
    boundary = re.search(rb"\$enddefinitions\s+\$end", data)
    if boundary is None:
        raise ValueError(f"{source.name} 缺少 VCD 声明结束标记")
    header, body = data[: boundary.end()], data[boundary.end() :]
    requested = {mapping["from"]: mapping["to"] for mapping in mappings}
    seen, scope, replacements = set(), [], []
    for directive in re.finditer(rb"\$(\w+)\b.*?\$end", header, re.DOTALL):
        kind = directive.group(1)
        fields = directive.group().split()
        if kind == b"scope":
            scope.append(fields[2].decode("utf-8"))
        elif kind == b"upscope":
            scope.pop()
        elif kind == b"var":
            reference = b"".join(fields[4:-1]).decode("utf-8")
            full_name = ".".join([*scope, reference])
            if full_name not in requested:
                continue
            match = re.fullmatch(
                rb"(\$var\s+\S+\s+1\s+\S+\s+)(\S+?)(\s*\[0:0\])(\s+\$end)",
                directive.group(),
            )
            if match is None or ".".join([*scope, match.group(2).decode("utf-8")]) != requested[full_name]:
                raise ValueError(f"只允许 1 位 [0:0] 声明规范化为标量：{full_name}")
            if full_name in seen:
                raise ValueError(f"待规范化声明重复：{full_name}")
            seen.add(full_name)
            replacements.append((directive.start() + match.start(3), directive.start() + match.end(3)))
    if seen != set(requested):
        raise ValueError(f"无法唯一定位待规范化的 VCD 声明：{sorted(set(requested) - seen)}")
    for start, end in reversed(replacements):
        header = header[:start] + header[end:]
    if source.resolve() == target.resolve():
        raise ValueError("规范化比较副本不能覆盖原始 VCD")
    target.write_bytes(header + body)
    return {
        "source": _artifact(source),
        "comparison": _artifact(target),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "body_bytes": len(body),
        "body_unchanged": True,
        "mappings": mappings,
    }


def compare_waveforms(
    k_vcd: Path,
    native_vcd: Path,
    *,
    top: str,
    native_top: str,
    ports: list[dict],
    times: list[int],
    work: Path,
    diffvcd_path: Path,
) -> dict:
    """先严格检查完整事件窗口，再调用外部 diffvcd 比较所有必需端口。"""
    work.mkdir(parents=True, exist_ok=True)
    result = {
        "agrees": False,
        "exit_code": None,
        "compared_signals": 0,
        "event_count": len(times),
        "first_mismatch": None,
        "errors": [],
        "artifacts": {},
    }
    records = []
    comparison_paths = {"kimulator": k_vcd, "native": native_vcd}
    normalization = {"policy": "scalar-equals-i1-zero-range-v1", "applied": False, "mappings": []}
    try:
        _validate_request(ports, times)
        if times != list(range(times[-1] + 1)):
            raise ValueError("完整波形比较必须包含从 0 开始的每个 low/high 事件时刻")
        for label, path, scope in (("kimulator", k_vcd, top), ("native", native_vcd, native_top)):
            result["artifacts"][label + "_vcd"] = _artifact(path)
            wave, names, samples = _read(path, scope, ports, times)
            if (wave.begintime, wave.endtime) != (times[0], times[-1]):
                raise ValueError(
                    f"{label} 时间窗口 [{wave.begintime}, {wave.endtime}] "
                    f"必须等于完整事件窗口 [{times[0]}, {times[-1]}]"
                )
            records.append((wave, names, samples))
        k_names, native_names = records[0][1], records[1][1]
        relative_names = []
        for port in ports:
            name = port["name"]
            left = k_names[name][len(top.rstrip(".")) + 1 :]
            right = native_names[name][len(native_top.rstrip(".")) + 1 :]
            if left != right:
                if port["width"] != 1 or {left, right} != {name, name + "[0:0]"}:
                    raise ValueError(f"端口 {name} 的 VCD 声明形式不一致，diffvcd 无法配对：{left!r} / {right!r}")
                backend, full_name = ("kimulator", k_names[name]) if left.endswith("[0:0]") else ("native", native_names[name])
                normalization["mappings"].append(
                    {"backend": backend, "port": name, "width": 1, "from": full_name, "to": full_name[:-5]}
                )
                left = name
            relative_names.append(left)
        for index, time in enumerate(times):
            for port in ports:
                name = port["name"]
                actual, expected = records[0][2][index][name], records[1][2][index][name]
                if actual != expected:
                    result["first_mismatch"] = {
                        "time": time, "event_index": index, "signal": name, "expected": expected, "actual": actual
                    }
                    break
            if result["first_mismatch"] is not None:
                break
        if normalization["mappings"]:
            normalized_files = {}
            for backend, original in comparison_paths.items():
                mappings = [mapping for mapping in normalization["mappings"] if mapping["backend"] == backend]
                if not mappings:
                    continue
                normalized = work / f"{backend}.comparison.vcd"
                normalized_files[backend] = _normalize_header(original, normalized, mappings)
                comparison_paths[backend] = normalized
                result["artifacts"][backend + "_comparison_vcd"] = normalized_files[backend]["comparison"]
            normalization["applied"] = True
            normalization_path = work / "normalization-map.json"
            _save(normalization_path, {"schema_version": 1, **normalization, "files": normalized_files})
            result["artifacts"]["normalization_map"] = _artifact(normalization_path)
    except (OSError, ValueError, KeyError, IndexError) as error:
        result["errors"].append(str(error))
    preflight_path = work / "preflight.json"
    _save(preflight_path, {"passed": not result["errors"], "ports": ports, "times": times, "errors": result["errors"]})
    result["artifacts"]["preflight"] = _artifact(preflight_path)
    result["normalization"] = normalization
    if result["errors"]:
        return result

    # 单个正则包含全部必需端口；省略 ignore-missing，预检也禁止必需端口无值。
    command = [
        sys.executable,
        str(diffvcd_path.resolve()),
        str(comparison_paths["kimulator"].resolve()),
        str(comparison_paths["native"].resolve()),
        "--top1", top.rstrip(".") + ".",
        "--top2", native_top.rstrip(".") + ".",
        "--filter", "^(?:" + "|".join(re.escape(name) for name in relative_names) + ")$",
        "--verbose",
    ]
    stdout_path, stderr_path = work / "diffvcd.stdout.log", work / "diffvcd.stderr.log"
    try:
        result["artifacts"]["diffvcd_script"] = _artifact(diffvcd_path)
        with stdout_path.open("w") as stdout, stderr_path.open("w") as stderr:
            process = subprocess.run(command, cwd=work, stdout=stdout, stderr=stderr, timeout=30, check=False)
        result["exit_code"] = process.returncode
        result["compared_signals"] = len(ports)
        result["agrees"] = process.returncode == 0 and result["first_mismatch"] is None
        if process.returncode not in (0, 1):
            result["errors"].append(f"diffvcd 执行失败，退出码 {process.returncode}")
        elif process.returncode == 0 and result["first_mismatch"] is not None:
            result["errors"].append("diffvcd 未报告预检观察到的真实差异，拒绝通过")
    except (OSError, subprocess.TimeoutExpired) as error:
        result["errors"].append(f"diffvcd 执行失败：{error}")
    command_path = work / "diffvcd.command.json"
    _save(command_path, {"argv": command, "cwd": str(work.resolve()), "timeout_s": 30, "exit_code": result["exit_code"]})
    result["command"] = command
    for label, path in (("command", command_path), ("stdout", stdout_path), ("stderr", stderr_path)):
        if path.exists():
            result["artifacts"][label] = _artifact(path)
    return result
