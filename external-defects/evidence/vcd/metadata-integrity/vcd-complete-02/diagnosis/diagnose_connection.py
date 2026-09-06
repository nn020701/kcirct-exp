import hashlib,json,re,subprocess
from pathlib import Path
from pyk.kore.parser import KoreParser
WORK=Path(__file__).resolve().parent
BASE=json.loads((WORK/'commands.jsonl').read_text().splitlines()[0])['argv']
RECORDS=[]
def walk(n):
    yield n
    for c in n.patterns:yield from walk(c)
def inspect(data):
    tree=KoreParser(data.decode()).pattern()
    conn=next(x for x in walk(tree) if getattr(x,'symbol','')=="Lbl'-LT-'connection'-GT-'")
    target=next(x for x in walk(conn) if getattr(x,'symbol','')=="Lbl'UndsPipe'-'-GT-Unds'" and x.args[0].text=='inj{SortString{}, SortKItem{}}(\\dv{SortString{}}("xlnxstream_2018_3/%53"))')
    args=re.findall(r'\\dv\{SortString\{\}\}\("([^\"]*)"\)',target.args[1].text)[:4]
    currents=[]
    for cell in walk(tree):
        if getattr(cell,'symbol','')=="Lbl'-LT-'current-info'-GT-'":
            cells={x.symbol:x for x in cell.args}
            currents.append({'id':cells["Lbl'-LT-'current-id'-GT-'"].args[0].text,'current':cells["Lbl'-LT-'current'-GT-'"].args[0].text[:6500]})
    return args,currents
def run(depth):
    path=WORK/f'depth-{depth}.kore';argv=BASE+['--depth',str(depth)]
    if not path.exists():
        p=subprocess.run(argv,capture_output=True,timeout=30,cwd=WORK);assert p.returncode==0,p.stderr
        path.write_bytes(p.stdout);(WORK/f'depth-{depth}.stderr').write_bytes(p.stderr)
    data=path.read_bytes();args,currents=inspect(data)
    record={'depth':depth,'argv':argv,'sha256':hashlib.sha256(data).hexdigest(),'args':args,'currents':currents}
    RECORDS.append(record);(WORK/'connection-bisect.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    print(depth,args,flush=True)
    return args!=['comb.mux','xlnxstream_2018_3/%51','xlnxstream_2018_3/%50','xlnxstream_2018_3/%54']
hi=2000
while not run(hi):hi*=2
lo=0
while hi-lo>1:
    mid=(hi+lo)//2
    if run(mid):hi=mid
    else:lo=mid
print('CONNECTION BOUNDARY',lo,hi,flush=True)
for depth in range(max(0,lo-3),hi+3):run(depth)
