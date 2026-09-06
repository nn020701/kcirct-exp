"""在独立 archive 中核验五份补丁；仅写 .work，不修改任何服务工作树。"""
from pathlib import Path
import datetime
import difflib
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
SERVICE = ROOT.parents[1] / 'circt-semantics'
COMPONENT = ROOT / 'evidence/vcd/component'
OUT = WORK / 'component-stage-ready'
BASELINE = '3afaa5f93d8ed0cabeb08bdce1fd4c5f74a8a5a2'
SEMANTICS = Path('src/kcirct/kdist/circt_semantics')
FILES = [SEMANTICS / 'hardware/hardware.md']
PATCHES = [COMPONENT / path for path in (
    'public-simulate.patch',
    'packed-array-semantics/packed-array-semantics.patch',
    'scalar-firreg-preset/scalar-firreg-preset.patch',
    'auto-connect-list-preservation/auto-connect-list-preservation.patch',
)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'path': str(path), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}


def hashes(directory):
    return {str(p.relative_to(directory)): sha(p.read_bytes()) for p in sorted(directory.rglob('*')) if p.suffix in ('.md', '.k')}


def main():
    if OUT.exists():
        raise SystemExit('拒绝覆盖已有 component 暂存证据')
    OUT.mkdir()
    commands = []

    def command(argv, cwd):
        proc = subprocess.run(argv, cwd=cwd, capture_output=True)
        commands.append({'argv': argv, 'cwd': str(cwd), 'exit_code': proc.returncode,
                         'stdout': proc.stdout.decode(), 'stderr': proc.stderr.decode()})
        (OUT / 'verification-commands.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2) + '\n')
        proc.check_returncode()
        return proc.stdout

    archive = subprocess.run(['git', 'archive', BASELINE], cwd=SERVICE, capture_output=True, check=True).stdout
    old = json.loads((ROOT / '.runs/vcd-complete-02/prepared.json').read_text())
    source_before = hashes(SERVICE / SEMANTICS)
    # 必须位于仓库外；否则 git apply 会按外层仓库工作树前缀跳过补丁。
    with tempfile.TemporaryDirectory(prefix='kcirct-indexed-read-', dir='/private/tmp') as temporary:
        tree = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(tree, filter='data')
        for patch in PATCHES:
            command(['git', 'apply', '--check', str(patch)], tree)
            command(['git', 'apply', str(patch)], tree)
        assert hashes(tree / SEMANTICS) == old['kimulator']['semantics_hashes']
        expected_changes = {str(path.relative_to(SEMANTICS)) for path in FILES}
        before = hashes(tree / SEMANTICS)
        actual_changes = {key for key in before.keys() | source_before.keys() if before.get(key) != source_before.get(key)}
        assert actual_changes == expected_changes, actual_changes
        text = ''
        file_records = []
        for relative in FILES:
            previous = (tree / relative).read_bytes()
            current = (SERVICE / relative).read_bytes()
            for line in difflib.unified_diff(previous.decode().splitlines(keepends=True), current.decode().splitlines(keepends=True),
                                             fromfile='a/' + str(relative), tofile='b/' + str(relative)):
                # 保留基线文件无尾换行的事实，避免生成不可应用的合并行。
                text += line if line.endswith('\n') else line + '\n\\ No newline at end of file\n'
            for name, payload in [('before', previous), ('after', current)]:
                target = OUT / 'sources' / name / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            file_records.append({'path': str(relative), 'before_sha256': sha(previous), 'after_sha256': sha(current), 'bytes': len(current)})
        patch = OUT / 'indexed-read.patch'
        patch.write_text(text)
        command(['git', 'apply', '--check', str(patch)], tree)
        command(['git', 'apply', str(patch)], tree)
        reconstructed = hashes(tree / SEMANTICS)
        assert reconstructed == source_before
        api_files = {}
        for relative, key in [('src/kcirct/api.py', 'api_sha256'), ('src/kcirct/_simulate.py', 'simulator_sha256'), ('src/kcirct/kdist/plugin.py', 'kdist_plugin_sha256')]:
            actual = sha((tree / relative).read_bytes())
            assert actual == old['kimulator'][key] == sha((SERVICE / relative).read_bytes())
            api_files[relative] = actual
    assert hashes(SERVICE / SEMANTICS) == source_before, '准备期间服务源码变化'
    result = {'schema_version': 1, 'description': '第五份语义层 indexed read 规避补丁；不修改 K/LLVM backend。此暂存记录只核验源码可应用性，不预先声明正式运行通过。',
              'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'baseline': {'repository': 'circt-semantics', 'commit': BASELINE, 'archive_sha256': sha(archive)},
              'prerequisite_patches': [record(patch) for patch in PATCHES], 'patch': record(patch), 'files': file_records,
              'verification': {'all_five_patch_checks_and_applies_passed': True, 'commands': commands,
                               'changed_semantics_files': sorted(actual_changes), 'all_semantics_hashes_match': True,
                               'semantics_file_count': len(reconstructed), 'semantics_hashes': reconstructed,
                               'unchanged_api_simulator_plugin': api_files, 'temporary_directory_removed': True,
                               'compiled_or_simulated_again': False},
              'prepared_run': None, 'prepared_binding_status': '待正式 complete03 prepared.json 与上述 52 份源码哈希逐项绑定'}
    output = OUT / 'identity-stage.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'identity': record(output), 'patch': record(patch), 'changed_files': file_records,
                      'commands': len(commands), 'semantics_file_count': len(reconstructed)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
