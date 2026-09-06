"""标准 operation 完成后的只读审计；仅核对保留的最后两个状态，不重新仿真。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from pyk.kore.parser import KoreParser
from pyk.kore.syntax import App, LeftAssoc, RightAssoc

sys.setrecursionlimit(20000)
WORK = Path(__file__).resolve().parent
SERVICE = WORK.parents[2]
MAP = "Lbl'Unds'Map'Unds'"
PAIR = "Lbl'UndsPipe'-'-GT-Unds'"
UNIT = "Lbl'Stop'Map"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path):
    return {'path':str(path.resolve()),'sha256':sha(path),'bytes':path.stat().st_size}


def walk(node):
    yield node
    for child in node.patterns:
        yield from walk(child)


def symbol(node):
    return getattr(node, 'symbol', '')


def map_parts(node):
    if isinstance(node, (LeftAssoc, RightAssoc)) and node.app.symbol == MAP:
        return [part for child in node.app.args for part in map_parts(child)]
    if isinstance(node, App) and node.symbol == MAP:
        return [part for child in node.args for part in map_parts(child)]
    if isinstance(node, App) and node.symbol == UNIT:
        return []
    if not isinstance(node, App) or node.symbol != PAIR:
        raise ValueError('Map 内出现未支持结构: ' + node.text[:100])
    return [node]


def canonical(node):
    is_map = (isinstance(node,(LeftAssoc,RightAssoc)) and node.app.symbol == MAP) or (isinstance(node,App) and node.symbol in (MAP,UNIT))
    if is_map:
        items = [(canonical(pair.args[0]),canonical(pair.args[1])) for pair in map_parts(node)]
        keys = [repr(key) for key,value in items]
        if len(keys) != len(set(keys)):
            raise ValueError('Map 中存在重复 key')
        return ('Map',tuple(sorted(items,key=lambda x:repr(x[0]))))
    value = getattr(node,'value',None)
    return (type(node).__name__,symbol(node),tuple(s.text for s in getattr(node,'sorts',())),
            getattr(getattr(node,'sort',None),'text',None),getattr(node,'name',None),
            getattr(value,'value',value),tuple(canonical(child) for child in node.patterns))


def inspect(path):
    tree = KoreParser(path.read_text()).pattern()
    nodes = list(walk(tree))
    connections = [n for n in nodes if symbol(n) == "Lbl'-LT-'connection'-GT-'"]
    if len(connections) != 1:
        raise ValueError('必须恰好存在一个 connection cell')
    entries = {}
    for pair in map_parts(connections[0].args[0]):
        key = pair.args[0].text
        if key in entries:
            raise ValueError('connection 中存在重复 key: ' + key)
        entries[key] = canonical(pair.args[1])
    controls = {}
    for name in ('prog','setup','cmd'):
        found = [n for n in nodes if symbol(n) == "Lbl'-LT-'" + name + "'-GT-'"]
        if len(found) != 1:
            raise ValueError('必须恰好存在一个 ' + name + ' cell')
        controls[name] = found[0].args[0].text
    currents = sum(symbol(n) == "Lbl'-LT-'current-info'-GT-'" for n in nodes)
    return {'connection':entries,'control_cells':controls,'current_cells':currents,
            'terminal':currents == 0 and all(v == 'dotk{}()' for v in controls.values())}


def differences(before, after):
    return [k for k in sorted(before.keys() | after.keys()) if before.get(k) != after.get(k)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execution-complete',action='store_true',required=True,
                        help='仅在负责执行者确认全部标准 operation 已完成后使用')
    args = parser.parse_args()
    command_file = WORK/'test_evaluate_operation.command.json'
    command = json.loads(command_file.read_text())
    assert Path(command['cwd']).resolve() == SERVICE
    original_inputs = json.loads((WORK/'inputs-before.json').read_text())
    unchanged = all((SERVICE/p).is_file() and sha(SERVICE/p) == entry['sha256'] for p,entry in original_inputs.items())
    result = {'schema_version':1,'scope':'每个标准operation的setup与最终simulated.0/.1；未保留中间逐次快照，不能声明所有中间状态连接均不变。',
        'method':'完整connection按key匹配并拒绝重复key；递归Map只忽略项顺序，所有sort、构造器、叶值及List顺序均严格保留。',
        'simulation_command':identity(command_file),'script':identity(Path(__file__)),
        'inputs_before':identity(WORK/'inputs-before.json'),'inputs_unchanged':unchanged,'cases':[]}
    for case in command['cases']:
        directory = SERVICE/'src/tests/resources/operation'/case
        setup_path = directory/'setup.kore'
        before = inspect(setup_path)
        entry = {'case':case,'setup':identity(setup_path),'connection_entries':len(before['connection']),'states':[]}
        for name in ('simulated.0.kore','simulated.1.kore'):
            path = directory/name
            after = inspect(path)
            changed = differences(before['connection'],after['connection'])
            entry['states'].append({'artifact':identity(path),'connection_entries':len(after['connection']),
                'changed_keys':changed,'connection_unchanged':not changed,
                'current_cells':after['current_cells'],'control_cells':after['control_cells'],
                'terminal':after['terminal'],'pass':not changed and after['terminal']})
        entry['pass'] = all(s['pass'] for s in entry['states'])
        result['cases'].append(entry)
    result['pass'] = unchanged and all(c['pass'] for c in result['cases'])
    result['case_count'] = len(result['cases'])
    result['state_count'] = sum(len(c['states']) for c in result['cases'])
    (WORK/'final-state-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['case_count','state_count','inputs_unchanged','pass']},ensure_ascii=False))
    raise SystemExit(0 if result['pass'] else 1)


if __name__ == '__main__':
    main()
