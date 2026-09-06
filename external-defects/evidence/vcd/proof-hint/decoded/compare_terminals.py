"""对照已解码 hint 与普通输出；不运行语义。"""
from collections import Counter
import json
from pathlib import Path
import subprocess
from pyk.kore.parser import KoreParser
from pyk.kore.syntax import App, LeftAssoc, RightAssoc, DV, String
from decode_hint import cell, identity, sha, dump

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
MAP = "Lbl'Unds'Map'Unds'"
LIST = "Lbl'Unds'List'Unds'"
PAIR = "Lbl'UndsPipe'-'-GT-Unds'"
ASSOC = {MAP: "Lbl'Stop'Map", LIST: "Lbl'Stop'List",
         "Lbl'Unds'CurrentInfoCellMap'Unds'": "Lbl'Stop'CurrentInfoCellMap"}


def walk(n):
    yield n
    for ch in n.patterns:
        yield from walk(ch)


def parts(n, symbol):
    if isinstance(n, (LeftAssoc, RightAssoc)) and n.app.symbol == symbol:
        return [x for a in n.app.args for x in parts(a, symbol)]
    if isinstance(n, App) and n.symbol == symbol:
        return [x for a in n.args for x in parts(a, symbol)]
    if isinstance(n, App) and n.symbol == ASSOC[symbol]:
        return []
    return [n]


def norm(n):
    # 只对照值结构，另外保留原始KORE及repr比较。二进制reader可能选择不同inj目标sort。
    if isinstance(n, (LeftAssoc, RightAssoc)):
        return norm(n.app)
    if isinstance(n, App):
        if n.symbol in ASSOC:
            values = [norm(x) for x in parts(n, n.symbol)]
            if n.symbol != LIST:
                values.sort(key=repr)
            if len(values) == 1:
                return values[0]
            return (n.symbol, values)
        if n.symbol in ASSOC.values():
            symbol = next(k for k, v in ASSOC.items() if v == n.symbol)
            return (symbol, [])
        if n.symbol == "inj":
            return ("inj-source-sort", str(n.sorts[0]), norm(n.args[0]))
        return ("App", n.symbol, [str(s) for s in n.sorts], [norm(x) for x in n.args])
    if isinstance(n, DV):
        return ("DV", str(n.sort), n.value.value)
    if isinstance(n, String):
        return ("String", n.value)
    return (type(n).__name__, n.text)


def strings(n):
    return [x.value.value for x in walk(n) if isinstance(x, DV) and x.sort.text == 'SortString{}']


def op(n):
    found = [x for x in walk(n) if isinstance(x, App) and len(x.args) == 4 and strings(x.args[0]) == ['comb.mux']]
    return [{"operation": "comb.mux", "operands": strings(x.args[1]),
             "operand_kore": x.args[1].text} for x in found]


def inspect(path, key):
    text = path.read_text()
    tree = KoreParser(text).pattern()
    conn = next(n for n in walk(tree) if getattr(n, 'symbol', '') == "Lbl'-LT-'connection'-GT-'")
    entries = {}
    for pair in parts(conn.args[0], MAP):
        assert isinstance(pair, App) and pair.symbol == PAIR
        name = strings(pair.args[0])
        assert len(name) == 1 and name[0] not in entries
        entries[name[0]] = pair.args[1]
    currents = []
    for node in walk(tree):
        if getattr(node, 'symbol', '') == "Lbl'-LT-'current-info'-GT-'":
            body = next(n for n in node.args if getattr(n, 'symbol', '') == "Lbl'-LT-'current'-GT-'")
            muxes = op(body)
            if muxes:
                current_id = next(n for n in node.args if getattr(n, 'symbol', '') == "Lbl'-LT-'current-id'-GT-'").args[0].value.value
                currents.append({"id": current_id, "muxes": muxes, "body_kore": body.text})
    return {"artifact": identity(path), "connection_key": key,
            "connection_entry_kore": entries[key].text, "connection_mux": op(entries[key]),
            "current_muxes": currents}, entries


CASES = {
    's2': (BASE/'current/depth-1023.kore', BASE/'current/depth-1024.kore', 'xlnxstream_2018_3/%53'),
    'd12': (BASE/'old/d12/normal-depth-942/state.kore', BASE/'old/d12/normal-depth-943/state.kore', 'axis_fifo/%69'),
    's3': (BASE/'old/s3/normal-depth-1956/state.kore', BASE/'old/s3/normal-depth-1957/state.kore', 'axis_adapter/%131'),
}


def main():
    for case, (before, after, key) in CASES.items():
        out = ROOT/case
        b, bm = inspect(before, key)
        a, am = inspect(after, key)
        h, hm = inspect(out/'final.kore', key)
        def differences(x, y):
            return [k for k in sorted(x.keys() | y.keys()) if k not in x or k not in y or norm(x[k]) != norm(y[k])]
        tail = json.loads((out/'tail.json').read_text())
        last_rule = next(e for e in reversed(tail) if e['kind'] == 'LLVMRuleEvent')
        counts = Counter(json.loads(l).get('name') for l in (out/'events.ndjson').read_text().splitlines())
        result = {"schema_version": 1, "case": case, "before": b, "ordinary_after": a,
            "hint_after": h, "connection_entry_count": len(bm),
            "ordinary_changed_keys": differences(bm, am),
            "hint_vs_before_changed_keys": differences(bm, hm),
            "hint_vs_ordinary_after_changed_keys": differences(am, hm),
            "value_comparison_policy": "Map项按key比较；展开List/Map左右结合表示；忽略inj目标sort但保留源sort、构造器、叶值及List次序。原始KORE全文和repr比较另存，不声称类型相等。",
            "last_applied_rule": last_rule,
            "all_trace_list_hook_counts": {k:v for k,v in counts.items() if k and k.startswith('LIST.')},
            "limitation": "不存在LIST.range事件不能证明未执行编译器lowering的hook_LIST_range_long。hint终态与普通输出的差异不得解释为普通运行无异常。"}
        cmd = ['/nix/store/d48jsivhwi2bk1sbnjk3zyy5w8fwl1na-profile/bin/llvm-kompile-compute-loc', str(Path(json.loads((out/'summary.json').read_text())['definition']['path']).parent), str(last_rule['ordinal'])]
        p = subprocess.run(cmd, capture_output=True)
        (out/'compute-loc.stdout').write_bytes(p.stdout)
        (out/'compute-loc.stderr').write_bytes(p.stderr)
        result['official_location_command'] = {'argv':cmd,'exit_code':p.returncode,'stdout':identity(out/'compute-loc.stdout'),'stderr':identity(out/'compute-loc.stderr')}
        dump(out/'terminal-comparison.json',result)
        print(json.dumps({'case':case,'ordinary':a['connection_mux'][0]['operands'],'hint':h['connection_mux'][0]['operands'], 'ordinary_changed_keys':result['ordinary_changed_keys'], 'hint_vs_before_changed_keys':result['hint_vs_before_changed_keys'],'hint_vs_ordinary_after_changed_keys':result['hint_vs_ordinary_after_changed_keys'], 'rule':last_rule['ordinal']},ensure_ascii=False))


if __name__ == '__main__':
    main()
