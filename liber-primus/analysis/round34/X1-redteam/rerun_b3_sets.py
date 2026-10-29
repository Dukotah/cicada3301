import json
base='C:/Users/Jeff/cicada3301/liber-primus/analysis/'
def kids(p,strip=False):
    s=[];
    for line in open(base+p,encoding='utf-8'):
        if line.startswith('{"v"') or not line.strip(): continue
        d=json.loads(line); k=d[0] if isinstance(d,list) else d['kid']
        s.append(k[3:] if strip else k)
    return s
src=kids('round32/B1-bash-random/sweep_rows.jsonl')+kids('round32/B2-php-mtrand/sweep_rows.jsonl')
b3=kids('round33/B3-v3-readjudication/readjud_rows.jsonl',True)
from collections import Counter
cs,cb=Counter(src),Counter(b3)
r={'src_rows':len(src),'b3_rows':len(b3),'multiset_equal':cs==cb,'src_unique':len(cs),'b3_unique':len(cb),'set_equal':set(cs)==set(cb),
 'dup_kids_src':sum(1 for v in cs.values() if v>1),'extra_decodes_from_dups':len(src)-len(cs)}
print(r); json.dump(r,open(base+'round34/X1-redteam/rerun_b3_sets.json','w'),indent=1)
