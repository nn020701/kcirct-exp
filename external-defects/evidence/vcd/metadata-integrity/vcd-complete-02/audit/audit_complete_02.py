"""独立只读审计已结束批次；不运行仿真，不改原始结果。"""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import report
from waveform import _read
BATCH = ROOT / '.runs/vcd-complete-02'
OUT = ROOT / '.work/complete-exp/vcd-complete-02-audit.json'
errors=[]
checks=collections.Counter()
def check(condition, message, kind='consistency'):
    checks[kind]+=1
    if not condition: errors.append(message)
def sha_bytes(value): return hashlib.sha256(value).hexdigest()
def sha(path): return sha_bytes(Path(path).read_bytes())
def read(path): return json.loads(Path(path).read_text())
def jsonl(path): return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
def record(path):
    return {'path':str(Path(path).relative_to(ROOT)), 'sha256':sha(path), 'bytes':Path(path).stat().st_size}
def hash_check(path, expected, label):
    check(Path(path).is_file() and sha(path)==expected,label,'sha256')
results=read(BATCH/'results.json'); prepared=read(BATCH/'prepared.json')
check(len(results)==10 and len({x['variant_id'] for x in results})==10,'批次必须恰有10个唯一案例')
check(collections.Counter(x['status'] for x in results)=={'pass':10},'历史VCD结果应为10通过')
case_audits=[]; failures=[]; full_pair_count=0; partial_pair_count=0; sampled_values=0; snapshots=0; commands_count=0; total_calls=0; total_completed=0
for item in results:
    variant=item['variant_id']; case=BATCH/variant; manifest=read(case/'manifest.json'); stimulus=read(case/'test_data.json'); events=stimulus['events']; times=[event['time'] for event in events]; ports=manifest['inputs']+manifest['outputs']
    check(read(case/'result.json')==item,f'{variant}: 聚合与单案结果不同')
    check(len(events)==item['vcd_events']==2*item['samples']-1,f'{variant}: 事件数不匹配')
    check(times==list(range(len(events))),f'{variant}: 时间序列不连续')
    for event in events:
        check(set(event['inputs'])=={p['name'] for p in manifest['inputs']},f'{variant}/{event["time"]}: 输入端口集合不符')
        check(event['inputs'][manifest['clock']]==event['time']%2,f'{variant}: 时钟不符合low/high协议')
    for low, high in zip(events[::2],events[1::2]):
        check({k:v for k,v in low['inputs'].items() if k!=manifest['clock']}=={k:v for k,v in high['inputs'].items() if k!=manifest['clock']},f'{variant}: low/high间非时钟输入变化')
    try:
        report.validate_vcd_record(item); checks['report_evidence_contract']+=1
    except Exception as e: errors.append(f'{variant}: report验证失败 {e}')
    group_audits=[]
    for group in ('golden','buggy'):
        label=f'{variant}/{group}'; k=case/group/'kimulator'; sim=k/'simulation'; native=case/group/'native'; raw=read(sim/'result.json'); backend=item['backends'][group+'_k']; native_record=item['backends'][group+'_native']; states=read(sim/'states.json'); commands=jsonl(sim/'commands.jsonl'); outer=jsonl(k/'commands.jsonl')
        check(raw['ports']=={'inputs':manifest['inputs'],'outputs':manifest['outputs']},f'{label}: CLI端口不符')
        check(raw['evaluations_per_input']==2 and raw['events_total']==len(events),f'{label}: CLI协议不符')
        for key in ['definition_sha256','parser_sha256']:
            check(raw[key]==prepared[key],f'{label}: 批次身份字段{key}不符')
        for key in ['api_sha256','simulator_sha256','kframework_version']:
            check(raw[key]==prepared['kimulator'][key],f'{label}: 组件身份字段{key}不符')
        for key in ['events_completed','simulation_calls','simulation_calls_attempted','input_sha256','inputs_sha256','vcd_sha256','last_state_sha256','stage']:
            check(raw[key]==backend[key],f'{label}: 原始CLI与runner字段{key}不符')
        for path,key in [(sim/'design.generic.mlir','input_sha256'),(sim/'inputs.json','inputs_sha256'),(case/'test_data.json','inputs_sha256'),(k/'test.vcd','vcd_sha256'),(sim/'last-state.kore','last_state_sha256')]:
            hash_check(path,raw[key],f'{label}: {path.name}哈希不符')
        check(read(sim/'inputs.json')==stimulus==read(native/'stimulus.json'),f'{label}: 两后端实际事件输入不同')
        check(raw['simulation_calls']==raw['simulation_calls_attempted']==len(states)==len(commands)-3,f'{label}: 执行/快照/命令计数不符')
        total_calls+=raw['simulation_calls'];total_completed+=raw['events_completed'];snapshots+=len(states);commands_count+=len(commands)
        check(len(outer)==1 and outer[0]['argv'][1]=='simulate' and '--evaluations-per-input' in outer[0]['argv'] and not outer[0]['timeout'],f'{label}: 外部CLI执行记录不完整')
        check(outer[0]['argv'][outer[0]['argv'].index('--evaluations-per-input')+1]=='2',f'{label}: 外部CLI未配置双执行')
        for stream in ['stdout','stderr']:
            check((k/outer[0][stream]).is_file(),f'{label}: 缺外部CLI {stream}')
        for i,cmd in enumerate(commands):
            check(cmd['sequence']==i and cmd['returncode']==0 and cmd['status']=='pass',f'{label}: K命令{i}未完成')
            hash_check(Path(cmd['stderr']),cmd['stderr_sha256'],f'{label}: K命令{i} stderr损坏')
            if i<3:
                hash_check(Path(cmd['stdout']),cmd['stdout_sha256'],f'{label}: K预处理命令{i} stdout损坏')
            else:
                state=states[i-3]; payload=gzip.decompress((sim/state['path']).read_bytes())
                check(sha_bytes(payload)==state['sha256_uncompressed']==cmd['stdout_sha256'],f'{label}: 快照{i-3}与对应命令stdout不符','decompressed_state_sha256')
                check(state['event_index']==(i-3)//2 and state['evaluation']==(i-3)%2+1 and state['time']==events[(i-3)//2]['time'],f'{label}: 快照{i-3}顺序/事件/重复次数不符')
                check(state['source_path']==cmd['stdout'],f'{label}: 快照{i-3}来源不符')
        check(states[-1]['sha256_uncompressed']==raw['last_state_sha256'],f'{label}: last-state与末快照不同')
        native_commands=read(native/'commands.json')
        check([x['stage'] for x in native_commands]==['version','build','run'] and all(x['exit_code']==0 for x in native_commands),f'{label}: 原生执行未完成')
        for cmd in native_commands:
            for suffix in ['stdout.log','stderr.log']:
                check((native/f'{cmd["stage"]}.{suffix}').is_file(),f'{label}: 缺原生日志')
        hash_check(Path(native_record['vcd']),native_record['vcd_sha256'],f'{label}: 原生VCD哈希不符')
        nw,_,native_samples=_read(Path(native_record['vcd']),native_record['vcd_top'],ports,times)
        check(nw.begintime==0 and nw.endtime==times[-1],f'{label}: 原生完整窗口不符')
        for event,row in zip(events,native_samples):
            check(all(row[p['name']]==event['inputs'][p['name']] for p in manifest['inputs']),f'{label}: 原生输入波形不符')
        complete=raw['status']=='pass'
        check(complete==(raw['stage']=='complete'),f'{label}: CLI状态/阶段冲突')
        check(outer[0]['exit_code']==(0 if complete else 1),f'{label}: CLI进程退出码不符')
        if complete:
            check(raw['events_completed']==len(events) and raw['simulation_calls']==2*len(events),f'{label}: 完整CLI记录未完成全部双执行')
            check(group in item['waveform_comparisons'],f'{label}: 完整CLI缺VCDdiff记录')
            comparison=item['waveform_comparisons'][group]
            check(comparison['agrees'] is True and comparison['exit_code']==0 and not comparison['errors'] and comparison['compared_signals']==len(ports) and comparison['event_count']==len(events),f'{label}: 完整VCDdiff未通过完整端口')
            kw,_,k_samples=_read(k/'test.vcd',raw['top_module'],ports,times)
            check(kw.begintime==0 and kw.endtime==times[-1],f'{label}: K完整窗口不符')
            check(k_samples==native_samples,f'{label}: 独立逐事件全端口采样不符','waveform_pair')
            full_pair_count+=1;sampled_values+=len(times)*len(ports)
        else:
            check(raw['status']=='execution_error' and item['status']=='execution_error' and item['simulator_agrees_with_native'] is False,f'{label}: 失败被误报通过')
            check(group not in item['waveform_comparisons'],f'{label}: 不完整K执行不应有完整比较')
            check(raw['events_completed']<len(events),f'{label}: 失败完成计数异常')
            prefix=times[:raw['events_completed']]
            if prefix:
                _,_,k_samples=_read(k/'test.vcd',raw['top_module'],ports,prefix)
                check(k_samples==native_samples[:len(prefix)],f'{label}: 失败前已完成窗口与原生不同','partial_waveform_pair')
                partial_pair_count+=1;sampled_values+=len(prefix)*len(ports)
            failures.append({'variant_id':variant,'design_variant':group,'status':raw['status'],'stage':raw['stage'],'event_index':raw['event_index'],'event_time':raw['event_time'],'evaluation':raw['evaluation'],'events_total':raw['events_total'],'events_completed':raw['events_completed'],'simulation_calls':raw['simulation_calls'],'outer_cli_exit_code':outer[0]['exit_code'],'last_krun_exit_code':commands[-1]['returncode'],'raw_error':raw['error'],'runner_error':backend['error'],'result':record(sim/'result.json'),'last_state':record(sim/'last-state.kore'),'last_snapshot':record(sim/states[-1]['path']),'failed_prestate':record(Path(commands[-1]['argv'][1])),'full_waveform_compared':False,'partial_completed_events_checked':len(prefix)})
        group_audits.append({'variant':group,'cli_status':raw['status'],'events_completed':raw['events_completed'],'calls':len(states),'command_records':len(commands),'all_snapshot_hashes_match':True,'native_vcd_events':len(events),'full_waveform_compared':complete})
    if item['status']=='pass':
        check(all(item.get(k) is True for k in ['golden_native_oracle','golden_k_oracle','buggy_k_native','simulator_agrees_with_native','bug_detected_by_oracle']),f'{variant}: 通过标志不完整')
    case_audits.append({'variant_id':variant,'status':item['status'],'ports':len(ports),'events':len(events),'groups':group_audits})
exit_record=read(BATCH/'batch-exit.json')
check(exit_record['host_exit_code']==0 and exit_record['runner_exit_code']==0 and exit_record['status']=='pass','批次宿主/runner退出记录不符')
file_records=[]
for path in sorted(BATCH.rglob('*')):
    if path.is_file() and not any(part in {'obj','obj_dir','__pycache__'} for part in path.relative_to(BATCH).parts):
        file_records.append(record(path))
result={'schema_version':1,'run_id':BATCH.name,'audit_passed':not errors,'meaning':'审计通过表示原始证据完整且VCD结果忠实；本批次10例VCD通过不代表内部状态元数据完整性已获验证。另有connection独立审计发现S2golden只读Map发生变化。','scope':'只读取本批次保存的工件和VCD；没有重跑仿真或用新定义替换历史身份。','results':record(BATCH/'results.json'),'prepared':record(BATCH/'prepared.json'),'batch_exit':record(BATCH/'batch-exit.json'),'auditor':record(Path(__file__)),'counts':{'cases':len(results),'case_statuses':dict(collections.Counter(x['status'] for x in results)),'planned_events':sum(x['vcd_events'] for x in results),'backends':4*len(results),'completed_k_events':total_completed,'k_simulation_calls':total_calls,'k_command_records':commands_count,'decompressed_snapshots_verified':snapshots,'full_waveform_pairs_checked':full_pair_count,'partial_waveform_pairs_checked':partial_pair_count,'compared_port_event_values':sampled_values,'files_hashed_excluding_native_build_cache':len(file_records),'bytes_hashed':sum(x['bytes'] for x in file_records)},'checks':dict(checks),'errors':errors,'cases':case_audits,'failures':failures,'limitations':['首次损坏的语义步数和规则归因由独立诊断提供；本审计仅核对原始正式批次。','历史 ping-pong stdout 按每次 states/*.gz 解压哈希校验，不能拿最后同名 simulated 文件冒充历史输出。','两次执行中未变更输入的实现约束由已保存的 CLI 源码补丁与 --evaluations-per-input 2 绑定；快照索引只证明事件和调用顺序。'],'files':file_records}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'audit_passed':not errors,'counts':result['counts'],'errors':errors,'path':str(OUT),'sha256':sha(OUT)},ensure_ascii=False,indent=2))
sys.exit(0 if not errors else 1)
