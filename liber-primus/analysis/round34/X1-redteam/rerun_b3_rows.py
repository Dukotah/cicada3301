import json,sys,collections
base='C:/Users/Jeff/cicada3301/liber-primus/analysis/'
def scan(p):
    n=0;hdr=0;kids=[];other=0
    for line in open(p,encoding='utf-8'):
        line=line.strip()
        if not line: continue
        if line.startswith('{'):
            d=json.loads(line); hdr+=1; continue
        n+=1; kids.append(line.split('\t')[0] if '\t' in line else line)
    return n,hdr,kids
out={}
for name,p in [('B1','round32/B1-bash-random/sweep_rows.jsonl'),('B2','round32/B2-php-mtrand/sweep_rows.jsonl'),('B3','round33/B3-v3-readjudication/readjud_rows.jsonl')]:
    f=open(base+p,encoding='utf-8'); first=f.readline(); f.readline()
    print(name,'line2 sample:',repr(f.readline()[:200]) if False else '')
    n=0;hdr=0;kids=[]
    f=open(base+p,encoding='utf-8')
    for line in f:
        if line.startswith('{"v"'): hdr+=1; continue
        if not line.strip(): continue
        n+=1
        try: d=json.loads(line)
        except Exception: d=None
        if isinstance(d,list): kids.append(d[0])
        elif isinstance(d,dict): kids.append(d.get('kid'))
        else: kids.append(line.split(',')[0])
    out[name]={'rows':n,'headers':hdr,'unique_kid':len(set(kids)),'sample':kids[:3]}
    print(name,out[name])
json.dump(out,open(base+'round34/X1-redteam/rerun_b3_rows.json','w'),indent=1)
