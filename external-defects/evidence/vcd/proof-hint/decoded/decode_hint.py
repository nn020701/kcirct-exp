#!/usr/bin/env python3
"""使用本机官方 K 静态绑定流式解码；只保存尾部详细事件，不运行语义。"""
import argparse
from collections import Counter, deque
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
import traceback

import pyk.kllvm.hints.prooftrace as pt
from pyk.kllvm.parser import parse_definition_file, parse_pattern_file


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path.read_bytes()), "bytes": path.stat().st_size}


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def cell(text, name):
    key = "Lbl'-LT-'" + name + "'-GT-'{}("
    start = text.index(key)
    depth = 1
    quoted = escaped = False
    for pos in range(start + len(key), len(text)):
        c = text[pos]
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    raise ValueError("cell 括号不完整: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--definition", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tail", type=int, default=100)
    parser.add_argument("--compare-final", type=Path)
    parser.add_argument("--k-bin", type=Path, default=Path("/nix/store/d48jsivhwi2bk1sbnjk3zyy5w8fwl1na-profile/bin"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    commands = []
    def run(argv, stem):
        p = subprocess.run([str(x) for x in argv], capture_output=True)
        (args.out / (stem + ".stdout")).write_bytes(p.stdout)
        (args.out / (stem + ".stderr")).write_bytes(p.stderr)
        commands.append({"argv": [str(x) for x in argv], "exit_code": p.returncode,
                         "stdout": identity(args.out / (stem + ".stdout")),
                         "stderr": identity(args.out / (stem + ".stderr"))})
        dump(args.out / "commands.json", commands)
        if p.returncode:
            raise RuntimeError("命令失败: " + str(argv))
        return p.stdout.decode(errors="replace")
    env = {"python": sys.version, "executable": sys.executable,
           "pyk_version": importlib.metadata.version("kframework"),
           "prooftrace_module": identity(pt.__file__), "static_binding_import": True,
           "decoder": identity(__file__), "argv": sys.argv}
    dump(args.out / "environment.json", env)
    for name in ("kore-rich-header", "kore-proof-trace", "llvm-kompile-compute-loc", "llvm-kompile-compute-ordinal"):
        run([args.k_bin / name, "--help"], name + "-help")
    header_path = args.out / "header.bin"
    run([args.k_bin / "kore-rich-header", args.definition, "-o", header_path], "rich-header")
    definition = parse_definition_file(args.definition)
    definition.preprocess()
    rules = {}
    def rule_info(ordinal):
        if ordinal not in rules:
            axiom = repr(definition.get_axiom_by_ordinal(ordinal))
            source = re.search(r'Source\((.*?)\)', axiom)
            location = re.search(r'Location\((\d+),(\d+),(\d+),(\d+)\)', axiom)
            (args.out / "axioms").mkdir(exist_ok=True)
            path = args.out / "axioms" / (str(ordinal) + ".kore")
            path.write_text(axiom + "\n")
            rules[ordinal] = {"ordinal": ordinal, "source": source.group(1) if source else None,
                              "location": list(map(int, location.groups())) if location else None,
                              "axiom": identity(path)}
        return rules[ordinal]
    def brief(argument):
        if argument.is_kore_pattern():
            return {"kind": "configuration"}
        step = argument.step_event
        out = {"kind": type(step).__name__}
        if hasattr(step, "rule_ordinal"):
            out["ordinal"] = step.rule_ordinal
        if hasattr(step, "name"):
            out["name"] = step.name
        if hasattr(step, "function_name"):
            out["function_name"] = step.function_name
        return out
    def term(pattern):
        text = repr(pattern)
        if len(text) <= 2000:
            return {"kore": text}
        digest = sha(text.encode())
        (args.out / "terms").mkdir(exist_ok=True)
        path = args.out / "terms" / (digest + ".kore")
        if not path.exists():
            path.write_text(text)
        return {"artifact": identity(path), "preview": text[:500], "preview_truncated": True}
    def detail(argument):
        out = brief(argument)
        if argument.is_kore_pattern():
            out["value"] = term(argument.kore_pattern)
            return out
        step = argument.step_event
        if hasattr(step, "rule_ordinal"):
            out["rule"] = rule_info(step.rule_ordinal)
        if hasattr(step, "substitution"):
            out["substitution"] = {k: term(v) for k, v in step.substitution.items()}
        if hasattr(step, "args"):
            out["args"] = [detail(a) for a in step.args]
        if hasattr(step, "result"):
            out["result"] = term(step.result)
        for name in ("relative_position", "check_result", "is_tail"):
            if hasattr(step, name):
                out[name] = getattr(step, name)
        return out
    it = pt.LLVMRewriteTraceIterator.from_file(args.trace, pt.KoreHeader.create(header_path))
    counts = Counter()
    tail = deque(maxlen=args.tail)
    last_config = None
    last_rules = deque(maxlen=20)
    events = 0
    with (args.out / "events.ndjson").open("w") as stream:
        for index, annotated in enumerate(it):
            phase = "pre_trace" if annotated.type.is_pre_trace else "initial_config" if annotated.type.is_initial_config else "trace"
            argument = annotated.event
            info = {"event_index": index, "phase": phase, **brief(argument)}
            stream.write(json.dumps(info, ensure_ascii=False) + "\n")
            counts[info["kind"]] += 1
            if info["kind"] == "LLVMRuleEvent":
                last_rules.append(info)
            tail.append((index, phase, argument))
            if argument.is_kore_pattern():
                last_config = (index, phase, argument.kore_pattern)
            events = index + 1
    detailed = [{"event_index": i, "phase": phase, **detail(argument)} for i, phase, argument in tail]
    dump(args.out / "tail.json", detailed)
    dump(args.out / "rules.json", list(rules.values()))
    final = {}
    if last_config:
        index, phase, pattern = last_config
        text = repr(pattern)
        final_path = args.out / "final.kore"
        final_path.write_text(text + "\n")
        final = {"event_index": index, "phase": phase, "artifact": identity(final_path)}
        if args.compare_final:
            ordinary = repr(parse_pattern_file(args.compare_final))
            final["comparison"] = {"ordinary": identity(args.compare_final),
                "native_parsed_repr_equal": text == ordinary,
                "connection_repr_equal": cell(text, "connection") == cell(ordinary, "connection"),
                "hint_connection_sha256": sha(cell(text, "connection").encode()),
                "ordinary_connection_sha256": sha(cell(ordinary, "connection").encode())}
    summary = {"schema_version": 1, "trace": identity(args.trace), "definition": identity(args.definition),
               "header": identity(header_path), "format_version": it.version,
               "streaming": True, "event_count": events, "counts": dict(counts),
               "last_rules": [{**info, "rule": rule_info(info["ordinal"])} for info in last_rules],
               "tail_event_count": len(detailed), "final_config": final,
               "interpretation": "event_index 是 hint 事件序号，不能当作 K rewrite depth；规则/函数/side condition/hook 分别保留。"}
    dump(args.out / "rules.json", list(rules.values()))
    dump(args.out / "summary.json", summary)
    print(json.dumps({"event_count": events, "counts": dict(counts), "last_rules": list(last_rules)[-3:], "final": final}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
