"""直接 KCIRCT API，复用 arc_test.py 的双状态槽调度；仅用于独立诊断。"""
import gzip
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[2]
SERVICE=ROOT.parent.parent/'circt-semantics'
DEFINITION=ROOT.parent/'.build/external-defects/kdist/circt-semantics/llvm'
PARSER=ROOT.parent/'.build/external-defects/parser'
FORMAL=ROOT/'.runs/vcd-complete-02/s2/golden/kimulator'
EXPECTED_DEFINITION='52a62a553fa6eda77309e207f62bac26f6d047222eb0eca06bb9db4f103a600f'
os.environ['KDIST_DIR']=str(ROOT.parent/'.build/external-defects/kdist')
os.environ['PATH']='/nix/store/d48jsivhwi2bk1sbnjk3zyy5w8fwl1na-profile/bin:'+os.environ['PATH']
from kcirct import api
from kcirct.api import KCIRCT
from kcirct.vcd import KVCD
sys.path.insert(0,str(WORK.parent))
from audit_connections import extract
sys.path.insert(0,str(ROOT))
from waveform import compare_waveforms
assert 'kcirct._simulate' not in sys.modules

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

assert sha(DEFINITION/'definition.kore')==EXPECTED_DEFINITION
manifest=json.loads((ROOT/'manifests/s2.json').read_text())
cli=json.loads((FORMAL/'simulation/result.json').read_text())
events=json.loads(Path(cli['inputs_file']).read_text())['events']
design=ROOT/manifest['ir_baseline']/'golden/design.generic.mlir'
inputs=cli['ports']['inputs']
items=[[(event['inputs'][port['name']],port['width']) for port in inputs] for event in events]
save(WORK/'arc-events.json',[entry for i,item in enumerate(items) for entry in [{'input':item},{'vcd_dump':events[i]['time']}]])
metadata=[{'name':manifest['top'],'states':[{'name':port['name'],'numBits':port['width'],'type':direction} for direction,ports in [('input',inputs),('output',cli['ports']['outputs'])] for port in ports]}]
save(WORK/'state.json',metadata)

# 仅配置现有 API 的工具路径，不替换任何 API 方法或增加子进程包装器。
api.TOP_LEVEL_PARSER=PARSER
kcirct=KCIRCT()
kcirct.set_definition_dir(DEFINITION)
kcirct.ensure_env()
pgm_file=WORK/'pgm.kore'
preprocessed_file=WORK/'preprocessed.kore'
setup_file=WORK/'setup.kore'
calls=[]
counts={'compile':0,'preprocess':0,'setup':0,'simulate':0}
for stage,args,method in [('compile',(design,pgm_file),kcirct.compile_fast),('preprocess',(pgm_file,preprocessed_file),kcirct.run_preprocess_fast),('setup',(preprocessed_file,setup_file,manifest['top']),kcirct.run_setup_fast)]:
    start=time.perf_counter();method(*args);counts[stage]+=1
    out=args[1]
    calls.append({'stage':stage,'args':[str(a) for a in args],'output_sha256':sha(out),'seconds':time.perf_counter()-start})
baseline=extract(setup_file.read_bytes())

# 以下文件轮换与 arc_test.py:_run_event_case 一致。
state_files=[WORK/'simulated.0.kore',WORK/'simulated.1.kore']
shutil.copyfile(setup_file,state_files[0])
current_state=0
simulation_calls=0
vcd=KVCD(WORK/'kcirct.vcd',design,state_json_path=WORK/'state.json',time_scale='1ns')
(WORK/'states').mkdir()
states=[]
first_change=None
try:
    for input_index,input_data in enumerate(items):
        for evaluation in range(1,3):
            source=state_files[current_state]
            target=state_files[current_state^1]
            start=time.perf_counter()
            kcirct.run_simulate_fast(source,target,input_data)
            current_state^=1
            simulation_calls+=1
            counts['simulate']+=1
            data=state_files[current_state].read_bytes()
            digest=hashlib.sha256(data).hexdigest()
            unchanged=extract(data)==baseline
            reference=FORMAL/'simulation/states'/f'event-{input_index:04d}.eval-{evaluation}.kore.gz'
            ref_digest=hashlib.sha256(gzip.decompress(reference.read_bytes())).hexdigest()
            if not unchanged and first_change is None:
                first_change={'event_index':input_index,'evaluation':evaluation,'call':simulation_calls}
            archive=WORK/'states'/reference.name
            archive.write_bytes(gzip.compress(data,mtime=0))
            entry={'event_index':input_index,'evaluation':evaluation,'call':simulation_calls,'source':source.name,'target':target.name,'input_values':input_data,'expected_command':kcirct.krun_cmd(Path(str(target)+'.prestate')),'state_sha256':digest,'prestate_sha256':sha(Path(str(target)+'.prestate')),'reference_cli_state_sha256':ref_digest,'bytes_equal_cli_state':digest==ref_digest,'connection_equals_setup':unchanged,'seconds':time.perf_counter()-start}
            states.append(entry)
        vcd.time=events[input_index]['time']
        vcd.dump(kcirct.read_ports_fast(state_files[current_state]))
        if input_index%20==0 or input_index==len(items)-1:
            print('event',input_index,'calls',simulation_calls,'first connection change',first_change,flush=True)
finally:
    vcd.close()
    save(WORK/'pipeline-calls.json',calls)
    save(WORK/'states.json',states)
assert sha(DEFINITION/'definition.kore')==EXPECTED_DEFINITION
ports=manifest['inputs']+manifest['outputs']
comparisons={}
for label,reference,scope in [('cli',FORMAL/'test.vcd',manifest['top']),('native',FORMAL.parent/'native/trace.vcd','TOP')]:
    comparisons[label]=compare_waveforms(WORK/'kcirct.vcd',reference,top=manifest['top'],native_top=scope,ports=ports,times=[e['time'] for e in events],work=WORK/('comparison-'+label),diffvcd_path=SERVICE/'scripts/diffvcd.py')
result={'schema_version':1,'method':'直接 KCIRCT 实例；compile/preprocess/setup 各一次；setup复制slot0；每输入两次run_simulate_fast、每次current_state ^= 1；两次之后dump','source_reference':{'path':str(SERVICE/'src/tests/integration/arc_test.py'),'sha256':sha(SERVICE/'src/tests/integration/arc_test.py'),'functions':['_prepare_pipeline','_run_event_case']},'api_sha256':sha(SERVICE/'src/kcirct/api.py'),'new_cli_wrapper_imported':'kcirct._simulate' in sys.modules,'counts':counts,'events':len(events),'states':len(states),'all_state_bytes_equal_new_cli':all(s['bytes_equal_cli_state'] for s in states),'first_connection_change':first_change,'changed_states':sum(not s['connection_equals_setup'] for s in states),'definition_sha256':EXPECTED_DEFINITION,'parser_sha256':sha(PARSER),'design_sha256':sha(design),'comparisons':comparisons,'differences_from_direct_arc_entry':['未直接调用 _run_event_case：其内部 _open_vcd 会调用 arcilator 生成 metadata，且函数不保留逐eval状态；为本审计逐行复用其调度并增加只读快照检查。','只在本诊断进程将 api.TOP_LEVEL_PARSER 配置为同一已准备 parser，并用现有 set_definition_dir 选择同一52a定义；没有替换API方法、子进程执行器或调用_simulate包装。','S2事件名值按公开输入端口顺序转换为原arc接受的(value,width)；metadata仅声明同样7个顶层端口，全部VCD值来自read_ports_fast。','保留每次评估快照并记录哈希，模拟完成后用外部diffvcd核对CLI和原生完整89事件。']}
save(WORK/'results.json',result)
print(json.dumps({'counts':counts,'all_states_equal_cli':result['all_state_bytes_equal_new_cli'],'first_change':first_change,'changed_states':result['changed_states'],'vcd':{k:v['agrees'] for k,v in comparisons.items()}},ensure_ascii=False),flush=True)
