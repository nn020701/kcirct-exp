"""独立验证：持久化初始化 MLIR 导出 SV，与原始 RTL 全事件逐端口比较。"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
sys.path.insert(0, str(ROOT))
from native import run_native
from runner import load_rows
from waveform import compare_waveforms

TOOLS = Path('/Users/bytedance/cym/tool/firtool-1.147.0/bin')
MANIFEST = json.loads((ROOT / 'manifests/s2.json').read_text())
ROWS, _ = load_rows(MANIFEST)
COMMANDS = json.loads((WORK / 'commands.json').read_text())
RESULTS = {}

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

for variant in ('golden', 'buggy'):
    out = WORK / variant
    out.mkdir(exist_ok=True)
    baseline = ROOT / MANIFEST['ir_baseline'] / variant / 'design.generic.mlir'
    for stage, argv in [
        ('lower-official', [str(TOOLS/'circt-opt'), str(baseline), '--lower-seq-to-sv', '--canonicalize', '-o', str(out/'design.sv.mlir')]),
        ('export-official', [str(TOOLS/'circt-opt'), str(out/'design.sv.mlir'), '--export-verilog', '-o', '/dev/null']),
    ]:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        (out/(stage+'.stdout.log')).write_text(proc.stdout)
        (out/(stage+'.stderr.log')).write_text(proc.stderr)
        COMMANDS.append({'variant':variant, 'stage':stage, 'argv':argv, 'returncode':proc.returncode})
        save(WORK/'commands.json', COMMANDS)
        if proc.returncode:
            raise RuntimeError(proc.stderr)
        if stage == 'export-official':
            (out/'design.sv').write_text(proc.stdout)
    sources = [ROOT / p for p in MANIFEST['golden_sources']]
    if variant == 'buggy':
        sources = [ROOT/MANIFEST['bug_source'] if str(p.relative_to(ROOT)) == MANIFEST['bug_original'] else p for p in sources]
    original = run_native(MANIFEST, sources, ROWS, out/'original', verilator='/opt/homebrew/bin/verilator')
    exported_manifest = {**MANIFEST, 'parameters':{}, 'effective_parameters':{}}
    exported = run_native(exported_manifest, [out/'design.sv'], ROWS, out/'exported', verilator='/opt/homebrew/bin/verilator')
    save(out/'original-result.json', original)
    save(out/'exported-result.json', exported)
    comparison = compare_waveforms(Path(exported['vcd']), Path(original['vcd']), top='TOP', native_top='TOP', ports=MANIFEST['inputs']+MANIFEST['outputs'], times=list(range(2*len(ROWS)-1)), work=out/'comparison', diffvcd_path=ROOT.parent.parent/'circt-semantics/scripts/diffvcd.py')
    RESULTS[variant] = {'baseline':str(baseline), 'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(), 'exported_sv_sha256':hashlib.sha256((out/'design.sv').read_bytes()).hexdigest(), 'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, 'parameters':MANIFEST['parameters'], 'exported_parameters':{}, 'original':original, 'exported':exported, 'comparison':comparison}
    save(WORK/'results.json', RESULTS)
    print(variant, comparison['agrees'], comparison['event_count'], comparison['compared_signals'], comparison['errors'], flush=True)
    if not comparison['agrees']:
        raise RuntimeError('规范化前后的 Verilator 全事件波形不同')
