"""两份完整审计通过后，原字节晋升 complete03 及第五份组件补丁证据。"""
from pathlib import Path
import hashlib
import json
import sys

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
SERVICE = ROOT.parents[1] / 'circt-semantics'
sys.path.insert(0, str(ROOT))
import report

RUN = 'vcd-complete-03'
BATCH = ROOT / '.runs' / RUN
COMPONENT = ROOT / 'evidence/vcd/component/indexed-read'
METADATA = ROOT / 'evidence/vcd/metadata-integrity' / RUN


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    if path.exists() and path.read_bytes() != payload:
        raise ValueError(f'拒绝覆盖不同内容的既存正式证据：{path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def main():
    connection = read(WORK / (RUN + '-connection-audit.json'))
    audit = read(WORK / (RUN + '-audit.json'))
    assert connection['passed'] and connection['complete'] and connection['summary']['groups'] == 20
    assert connection['summary']['states'] == 2568 and connection['summary']['connection_changes'] == 0 and connection['summary']['unbound_states'] == 0
    assert audit['audit_passed'] and audit['counts']['case_statuses'] == {'pass': 10}
    assert audit['counts']['k_simulation_calls'] == 2568
    prepared = read(BATCH / 'prepared.json')
    stage = WORK / 'component-stage-ready'
    identity = read(stage / 'identity-stage.json')
    assert identity['verification']['semantics_hashes'] == prepared['kimulator']['semantics_hashes']
    artifacts = {}

    def publish(source, relative):
        return report.publish_artifact(source, COMPONENT / relative, artifacts)

    patch = publish(stage / 'indexed-read.patch', 'indexed-read.patch')
    identity['description'] = '第五份语义层 indexed read 规避；只修改 hardware.md，避免在读取共享原参数 List 时头尾解构。没有修改 K/LLVM backend。'
    identity['patch'] = {'path': 'indexed-read.patch', 'sha256': patch['sha256'], 'bytes': patch['bytes'], 'changed_files': 1}
    identity['prerequisite_patches'] = [{'path': str(Path(entry['path']).relative_to(ROOT / 'evidence/vcd/component')), 'path_base': '../', 'sha256': entry['sha256']} for entry in identity['prerequisite_patches']]
    identity['prepared_run'] = {'run_id': RUN, 'source': str((BATCH / 'prepared.json').relative_to(ROOT)),
                                'sha256': report.digest(BATCH / 'prepared.json'), 'kimulator_identity': prepared['kimulator'],
                                'compiled_identity': {key: prepared[key] for key in ('definition_sha256', 'compiled_artifact_sha256', 'parser_sha256')}}
    identity['prepared_binding_status'] = '五补丁还原的全部52份语义源码与正式prepared逐项相同；定义身份仅绑定正式批次，不与独立候选构建混写。'
    save(COMPONENT / 'identity.json', identity)
    publish(COMPONENT / 'identity.json', 'identity.json')
    publish(stage / 'identity-stage.json', 'validation/identity-stage.json')
    publish(stage / 'verification-commands.json', 'validation/verification-commands.json')
    publish(WORK / 'prepare_component.py', 'validation/prepare_component.py')
    publish(WORK / 'prepared-source-binding.json', 'validation/prepared-source-binding.json')
    for path in sorted((stage / 'sources').rglob('*')):
        if path.is_file():
            publish(path, path.relative_to(stage))
    for name in ('build-comparison.json', 'coverage-review.md', 'ast-audit.json', 'replays.json', 'validation.json'):
        publish(SERVICE / '.kcirct/indexed-read' / name, 'validation/' + name)
    publish(SERVICE / 'src/tests/resources/operation/README.md', 'validation/operation-README.md')
    operation = SERVICE / '.kcirct/indexed-read/operation'
    operation_index = read(operation / 'audit-index.json')
    publish(operation / 'audit-index.json', 'operation-validation/source-index.json')
    for item in operation_index['local_artifacts']:
        source = Path(item['path'])
        assert report.digest(source) == item['sha256']
        publish(source, 'operation-validation/' + source.name)
    for item in operation_index['observed_state_artifacts']:
        source = Path(item['path'])
        assert report.digest(source) == item['sha256']
        publish(source, Path('operation-validation/states') / source.relative_to(SERVICE / 'src/tests/resources/operation'))
    operation_records = {key: value for key, value in artifacts.items() if '/operation-validation/' in key}
    save(COMPONENT / 'operation-validation/index.json', {'schema_version': 1, 'artifacts': operation_records,
                                                        'scope': '13组标准operation仿真和VCDdiff共26项通过；独立审计13份setup与最后26份轮换状态。67份输入/参考资产哈希前后不变；不据此声明全部中间状态不变。',
                                                        'evaluate_seconds': 850.50, 'diff_seconds': 4.21})
    publish(COMPONENT / 'operation-validation/index.json', 'operation-validation/index.json')
    publish(WORK / 'component-README.md', 'README.md')
    save(COMPONENT / 'index.json', {'schema_version': 1, 'run_id': RUN, 'artifacts': artifacts,
                                   'identity_sha256': report.digest(COMPONENT / 'identity.json'),
                                   'interpretation': '五补丁可应用性、正式源码身份及独立构建/反例检查分别记录。52源码相同不等于两份definition或binary相同；16条owise生成条件仍有排列差异。'})

    artifacts = {}

    def promote(source, relative):
        return report.publish_artifact(source, METADATA / relative, artifacts)

    for name in ('audit_connections.py', 'audit_batch.py', 'publish_verified.py', 'auditor-checks.json', 'previous-complete02-audit.json',
                 RUN + '-connection-audit.json', RUN + '-audit.json', 'prepared-source-binding.json'):
        promote(WORK / name, 'audit/' + name)
    for name in ('prepared.json', 'results.json', 'protocol.json', 'versions.json', 'batch-exit.json'):
        promote(BATCH / name, 'batch/' + name)
    for stem in ('prepare', 'run'):
        for suffix in ('stdout', 'stderr', 'command.json', 'result.json'):
            path = WORK / (stem + '.' + suffix)
            if path.is_file():
                promote(path, 'invocation/' + path.name)
    for stem in ('audit-connections', 'audit-batch'):
        for suffix in ('stdout.log', 'stderr.log'):
            path = WORK / (stem + '.' + suffix)
            if path.is_file():
                promote(path, 'audit/' + path.name)
    for key, group in connection['groups'].items():
        directory = BATCH / key / 'kimulator/simulation'
        for name in ('setup.kore', 'last-state.kore', 'result.json', 'commands.jsonl', 'states.json'):
            promote(directory / name, key + '/' + name)
        snapshots = read(directory / 'states.json')
        for state in snapshots[-2:]:
            promote(directory / state['path'], key + '/' + state['path'])
    promote(WORK / 'metadata-README.md', 'README.md')
    save(METADATA / 'index.json', {'schema_version': 1, 'source_run': RUN,
                                  'vcd_observation': audit['counts'], 'metadata_observation': connection['summary'] | {'passed': True},
                                  'interpretation': '正式十配置两版VCD通过，另有全部2568逐次状态的whole connection保持setup审计。此有限轨迹支持本轮语义层规避有效，不证明底层runtime缺陷已修复。',
                                  'preservation_scope': '保留全状态审计及原压缩/解压/命令SHA索引、每组setup和末态、最后两份gzip，以及运行身份与命令记录；全部逐次gzip仍保留原.runs归档。complete01/02真实失败不覆盖。',
                                  'artifacts': artifacts, 'artifact_count': len(artifacts), 'bytes': sum(item['bytes'] for item in artifacts.values())})
    for index in (COMPONENT / 'index.json', METADATA / 'index.json'):
        records = read(index)['artifacts']
        for item in records.values():
            assert report.digest(ROOT / item['path']) == item['sha256']
        print(json.dumps({'index': str(index), 'sha256': report.digest(index), 'artifacts': len(records)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
