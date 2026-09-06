import hashlib,json,re,subprocess,shutil
from pathlib import Path
from pyk.kore.parser import KoreParser
WORK=Path(__file__).resolve().parent
SOURCE=WORK.parents[2]/'.runs/vcd-complete-01/d12/golden/kimulator/simulation'
shutil.copyfile(SOURCE/'simulated.1.kore.prestate',WORK/'previous-input.kore')
BASE=json.loads((WORK/'replays.json').read_text())[0]['argv']
BASE[1]=str(WORK/'previous-input.kore')
RECORDS=[]
def walk(n):
    yield n
    for c in n.patterns:yield from walk(c)
def inspect(data):
    tree=KoreParser(data.decode()).pattern()
    conn=next(x for x in walk(tree) if getattr(x,'symbol','')=="Lbl'-LT-'connection'-GT-'")
    target=next(x for x in walk(conn) if getattr(x,'symbol','')=="Lbl'UndsPipe'-'-GT-Unds'" and x.args[0].text=='inj{SortString{}, SortKItem{}}(\\dv{SortString{}}("axis_fifo/%69"))')
    args=re.findall(r'\\dv\{SortString\{\}\}\("([^\"]*)"\)',target.args[1].text)[:4]
    currents=[]
    for cell in walk(tree):
        if getattr(cell,'symbol','')=="Lbl'-LT-'current-info'-GT-'":
            cells={x.symbol:x for x in cell.args}
            cur=cells["Lbl'-LT-'current'-GT-'"]
            ident=cells["Lbl'-LT-'current-id'-GT-'"]
            currents.append({'id':ident.args[0].text,'current':cur.args[0].text[:5500]})
    return args,currents
def run(depth):
    name='previous-full' if depth is None else f'previous-depth-{depth}'
    path=WORK/(name+'.kore')
    argv=BASE+([] if depth is None else ['--depth',str(depth)])
    if not path.exists():
        p=subprocess.run(argv,capture_output=True,timeout=30,cwd=WORK);assert p.returncode==0,p.stderr
        path.write_bytes(p.stdout);(WORK/(name+'.stderr')).write_bytes(p.stderr)
    data=path.read_bytes();args,currents=inspect(data)
    record={'depth':depth,'argv':argv,'sha256':hashlib.sha256(data).hexdigest(),'args':args,'currents':currents,'matches_previous_formal':data==(SOURCE/'simulated.1.kore').read_bytes()}
    RECORDS.append(record);(WORK/'connection-bisect.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    print(depth,args,flush=True)
    return args!=['comb.mux','axis_fifo/%57','axis_fifo/%65','axis_fifo/%70']
assert run(None)
hi=2000
while not run(hi):hi*=2
lo=0
while hi-lo>1:
    mid=(hi+lo)//2
    if run(mid):hi=mid
    else:lo=mid
print('CONNECTION BOUNDARY',lo,hi,flush=True)
for depth in range(max(0,lo-3),hi+3):run(depth)
