"""只读审计正式批次全部 connection；不运行 K 或仿真器，不复用旧审计缓存。"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys

CASES = ('d13', 's1b', 's1r', 's2', 's3', 'd8', 'd11', 'd12', 'd4', 'c4')
CELL = "Lbl'-LT-'connection'-GT-'"
MAP = "Lbl'Unds'Map'Unds'"
UNIT = "Lbl'Stop'Map"
PAIR = "Lbl'UndsPipe'-'-GT-Unds'"
MARKER = (CELL + '{}(').encode()
TOKENS = re.compile(rb'"(?:[^"\\]|\\.)*"|[()]')
NAME = re.compile(r'event-(\d+)\.eval-(\d+)\.kore\.gz')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def record(path, root):
    return {'path': str(path.relative_to(root)), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}


def extract(data):
    if data.count(MARKER) != 1:
        raise ValueError('必须恰有一个 connection cell')
    start = data.index(MARKER)
    depth = 0
    for token in TOKENS.finditer(data, start + len(MARKER) - 1):
        value = token.group()
        if value == b'(':
            depth += 1
        elif value == b')':
            depth -= 1
            if depth == 0:
                return data[start:token.end()]
    raise ValueError('connection cell 括号未闭合')


def parts(node):
    from pyk.kore.syntax import App, LeftAssoc, RightAssoc
    if isinstance(node, (LeftAssoc, RightAssoc)) and node.app.symbol == MAP:
        if node.app.sorts:
            raise ValueError('不支持带 sort 参数的 Map 构造器')
        return [part for arg in node.app.args for part in parts(arg)]
    if isinstance(node, App) and node.symbol == MAP:
        if node.sorts:
            raise ValueError('不支持带 sort 参数的 Map 构造器')
        return [part for arg in node.args for part in parts(arg)]
    if isinstance(node, App) and node.symbol == UNIT:
        if node.args or node.sorts:
            raise ValueError('Map unit 不应含参数')
        return []
    return [node]


def norm(node):
    """仅 Map 项忽略顺序；所有 sort、inj 目标 sort 和 List 次序保留。"""
    from pyk.kore.syntax import App, LeftAssoc, RightAssoc, DV, String
    if isinstance(node, DV):
        return ('DV', node.sort.text, node.value.value)
    if isinstance(node, String):
        return ('String', node.value)
    app = node.app if isinstance(node, (LeftAssoc, RightAssoc)) else node
    if isinstance(app, App) and app.symbol in (MAP, UNIT, PAIR):
        entries = {}
        for pair in parts(node):
            if not isinstance(pair, App) or pair.symbol != PAIR or len(pair.args) != 2 or pair.sorts:
                raise ValueError('Map 含非 key-value 项')
            key, value = map(norm, pair.args)
            if key in entries:
                raise ValueError('Map 存在重复 key')
            entries[key] = value
        return ('Map', tuple(sorted(entries.items(), key=lambda item: repr(item[0]))))
    return (type(node).__name__, getattr(node, 'symbol', ''),
            tuple(str(sort) for sort in getattr(node, 'sorts', ())),
            str(getattr(node, 'value', '')),
            tuple(norm(child) for child in node.patterns))


def canonical(data):
    from pyk.kore.parser import KoreParser
    from pyk.kore.syntax import App
    node = KoreParser(data.decode()).pattern()
    if not isinstance(node, App) or node.symbol != CELL or len(node.args) != 1:
        raise ValueError('connection cell 必须含唯一完整 Map')
    value = norm(node)
    entries = dict(norm(node.args[0])[1])
    return value, entries


def audit_group(root, batch, case, variant, prepared, events):
    directory = batch / case / variant / 'kimulator/simulation'
    result = {'states': [], 'errors': [], 'coverage_complete': False}

    def check(condition, error):
        if not condition:
            result['errors'].append(error)

    for filename in ('result.json', 'commands.jsonl', 'states.json', 'setup.kore', 'inputs.json'):
        result[filename] = record(directory / filename, root)
    cli = read(directory / 'result.json')
    snapshots = read(directory / 'states.json')
    commands = [json.loads(line) for line in (directory / 'commands.jsonl').read_text().splitlines() if line.strip()]
    check(cli['status'] == 'pass', 'CLI 未完成成功执行；仍审计已保存状态')
    check(cli['evaluations_per_input'] == 2, '必须同一输入执行两次')
    check(cli['events_total'] == len(events), 'CLI 与批次输入事件总数不同')
    check(read(directory / 'inputs.json')['events'] == events, 'CLI 输入事件与批次记录不同')
    for field in ('definition_sha256', 'parser_sha256'):
        check(cli[field] == prepared[field], f'CLI {field} 与批次身份不同')
    for field in ('api_sha256', 'simulator_sha256', 'kframework_version'):
        check(cli[field] == prepared['kimulator'][field], f'CLI {field} 与批次身份不同')
    result['identity'] = {field: cli[field] for field in ('definition_sha256', 'parser_sha256', 'api_sha256', 'simulator_sha256', 'kframework_version')}
    setup = (directory / 'setup.kore').read_bytes()
    baseline = extract(setup)
    baseline_ast, baseline_map = canonical(baseline)
    result['baseline_connection'] = {'sha256': sha(baseline), 'bytes': len(baseline), 'map_entries': len(baseline_map)}
    setup_commands = [command for command in commands if Path(command.get('stdout', '')).name == 'setup.kore']
    check(len(setup_commands) == 1 and setup_commands[0]['stdout_sha256'] == sha(setup), 'setup 与唯一 setup 命令 stdout 哈希不同')
    calls = [command for command in commands if re.fullmatch(r'simulated\.\d+\.kore', Path(command.get('stdout', '')).name)]
    check(len(commands) == len(calls) + 3, '除逐次模拟外必须恰有三条构建/setup命令')
    for index, command in enumerate(commands):
        check(command['sequence'] == index and command['returncode'] == 0 and command['status'] == 'pass', f'命令 {index} 顺序或执行状态不符')
        stderr = Path(command['stderr'])
        check(stderr.is_file() and sha(stderr.read_bytes()) == command['stderr_sha256'], f'命令 {index} stderr 哈希不符')
        if command not in calls:
            stdout = Path(command['stdout'])
            check(stdout.is_file() and sha(stdout.read_bytes()) == command['stdout_sha256'], f'前置命令 {index} stdout 哈希不符')
    expected = {(event, evaluation) for event in range(len(events)) for evaluation in (1, 2)}
    seen = set()
    seen_paths = set()
    for index, snapshot in enumerate(snapshots):
        path = (directory / snapshot['path']).resolve()
        if not path.is_relative_to(directory / 'states'):
            raise ValueError('快照路径超出本组 states 目录')
        match = NAME.fullmatch(path.name)
        if match is None:
            raise ValueError(f'快照文件名不符合约定：{path.name}')
        event, evaluation = map(int, match.groups())
        check((event, evaluation) not in seen and path not in seen_paths, f'{path.name}: 重复快照')
        seen.add((event, evaluation))
        seen_paths.add(path)
        check(event == index // 2 and evaluation == index % 2 + 1, f'{path.name}: 索引顺序不是每事件两次')
        check(snapshot['event_index'] == event and snapshot['evaluation'] == evaluation, f'{path.name}: 文件名与索引的事件不符')
        check(event < len(events) and snapshot['time'] == events[event]['time'], f'{path.name}: 事件时间不符')
        compressed = path.read_bytes()
        data = gzip.decompress(compressed)
        cell = extract(data)
        exact = cell == baseline
        equivalent = exact
        changed_keys = []
        if not exact:
            actual_ast, actual_map = canonical(cell)
            equivalent = actual_ast == baseline_ast
            changed_keys = [repr(key) for key in baseline_map.keys() | actual_map.keys()
                            if key not in baseline_map or key not in actual_map or baseline_map[key] != actual_map[key]]
        command = calls[index] if index < len(calls) else None
        payload_sha = sha(data)
        bound = command is not None and payload_sha == snapshot['sha256_uncompressed'] == command['stdout_sha256']
        source_bound = command is not None and snapshot['source_path'] == command['stdout']
        entry = {**record(path, root), 'event_index': event, 'evaluation': evaluation, 'time': snapshot['time'],
                 'state_sha256': payload_sha, 'state_bytes': len(data), 'connection_sha256': sha(cell),
                 'exact_text_equal': exact, 'structurally_equal': equivalent, 'changed_map_keys': changed_keys,
                 'command_sequence': None if command is None else command['sequence'],
                 'matches_index_and_command_stdout_sha256': bound, 'matches_command_source_path': source_bound}
        result['states'].append(entry)
        check(bound, f'{path.name}: gzip/索引/命令 stdout 哈希没有全部匹配')
        check(source_bound, f'{path.name}: 索引来源与命令 stdout 路径不同')
        check(equivalent, f'{path.name}: 完整 connection 内容变化')
    files = {path.resolve() for path in (directory / 'states').glob('*.kore.gz')}
    result['coverage_complete'] = (seen == expected and len(snapshots) == len(expected)
                                   and files == seen_paths and len(calls) == len(expected))
    result['expected_states'] = len(expected)
    result['disk_snapshot_count'] = len(files)
    result['command_call_count'] = len(calls)
    check(result['coverage_complete'], f'状态覆盖不完整：missing={sorted(expected-seen)}, extra={sorted(seen-expected)}, 未索引文件={sorted(str(p) for p in files-seen_paths)}')
    check(cli['events_completed'] == len(events), 'CLI 完成事件数不符')
    check(cli['simulation_calls'] == cli['simulation_calls_attempted'] == len(calls), 'CLI 调用计数不符')
    last = directory / 'last-state.kore'
    check(bool(snapshots) and last.is_file() and sha(last.read_bytes()) == snapshots[-1]['sha256_uncompressed'] == cli['last_state_sha256'], '最后状态、索引和 CLI 末态哈希不符')
    result['passed'] = not result['errors']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='external-defects 实验根目录')
    parser.add_argument('--run', required=True, help='已结束正式批次 ID')
    parser.add_argument('--output', type=Path, required=True, help='新建忽略目录中的审计 JSON，不覆盖旧证据')
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('拒绝覆盖现有审计文件，请指定新的 --output')
    batch = root / '.runs' / args.run
    results = read(batch / 'results.json')
    prepared = read(batch / 'prepared.json')
    identities = [item['variant_id'] for item in results]
    errors = [] if len(identities) == len(CASES) and set(identities) == set(CASES) else ['批次必须含全部十个唯一配置']
    value = {'schema_version': 2, 'run_id': args.run, 'scope': '只读全部状态；按索引重新校验，不缓存已审组，不运行仿真。此独立诊断使用组件环境的 pyk 解析 Kore；公开 runner 外部 CLI 边界不变。',
             'comparison_policy': 'whole connection Map 按 key 精确比较；拒重复 key；只忽略 Map 项顺序/结合，保留所有 sort、inj 目标类型和 List 顺序。',
             'auditor': record(Path(__file__).resolve(), root), 'python': sys.executable, 'python_version': sys.version,
             'kframework_version': importlib.metadata.version('kframework'), 'argv': sys.argv,
             'results': record(batch / 'results.json', root), 'prepared': record(batch / 'prepared.json', root),
             'vcd_case_statuses': dict(Counter(item['status'] for item in results)), 'groups': {}, 'errors': errors}
    for case in CASES:
        for variant in ('golden', 'buggy'):
            key = case + '/' + variant
            try:
                events = read(batch / case / 'test_data.json')['events']
                group = audit_group(root, batch, case, variant, prepared, events)
            except Exception as error:
                group = {'states': [], 'coverage_complete': False, 'passed': False, 'errors': [f'{type(error).__name__}: {error}']}
            value['groups'][key] = group
            value['errors'].extend(key + ': ' + error for error in group['errors'])
            print(key, 'states', len(group['states']), 'passed', group['passed'], flush=True)
    groups = value['groups'].values()
    states = [state for group in groups for state in group['states']]
    value['complete'] = len(value['groups']) == 20 and all(group['coverage_complete'] for group in groups)
    value['passed'] = value['complete'] and not value['errors']
    value['summary'] = {'groups': len(value['groups']), 'expected_groups': 20, 'states': len(states),
                        'connection_changes': sum(not state['structurally_equal'] for state in states),
                        'text_order_only_differences': sum(not state['exact_text_equal'] and state['structurally_equal'] for state in states),
                        'unbound_states': sum(not state['matches_index_and_command_stdout_sha256'] or not state['matches_command_source_path'] for state in states)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'complete': value['complete'], 'passed': value['passed'], 'summary': value['summary'],
                      'errors': value['errors'], 'output': str(output), 'sha256': sha(output.read_bytes())}, ensure_ascii=False), flush=True)
    return 0 if value['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
