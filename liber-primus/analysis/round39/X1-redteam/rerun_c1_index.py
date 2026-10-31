import json,os,re,sys
D=r'C:\Users\Jeff\cicada3301\liber-primus\analysis\round38\C1-semantic-road\lex_download\dict'
J=json.load(open(r'C:\Users\Jeff\cicada3301\liber-primus\analysis\round39\C1-sense-similarity\lp1_sense_index.json'))
rows=J['rows']
# my own parse: regex on lines, store gloss-free part
def data(pos):
    m={}
    for l in open(os.path.join(D,'data.'+pos),encoding='utf-8'):
        if l[0]==' ':continue
        head=l.split(' | ')[0].split()
        off=head[0];lex=int(head[1]);wc=int(head[3],16)
        rest=head[4+2*wc:]
        pc=int(rest[0]);ptrs=[tuple(rest[1+4*j:5+4*j]) for j in range(pc)]
        first=next(((p[1],p[2]) for p in ptrs if p[0] in('@','@i')),None)
        m[off]=(lex,first)
    return m
DATA={p:data(p) for p in('noun','verb','adj')}
pmap={'n':'noun','v':'verb','a':'adj','s':'adj'}
def idx(pos,lem):
    for l in open(os.path.join(D,'index.'+pos),encoding='utf-8'):
        if l.startswith(lem+' '):
            t=l.split();pc=int(t[3]);sc=int(t[2])
            return t[-sc]   # first synset offset = first of last synset_cnt tokens
    return None
def depth(off,pos):
    d=0;seen=set()
    while True:
        h=DATA[pos][off][1]
        if not h or h in seen:break
        seen.add(h);d+=1;off,pos=h[0],pmap[h[1]]
    return d
import random
random.seed(5)
cov=[r for r in rows if r['lemma']]
pick=[r for r in rows if r['word'] in('warning','believe','is','lives')][:0]
chosen={}
for r in cov:
    if r['word'] in('warning','believe','is','lives','road') and r['word'] not in chosen: chosen[r['word']]=r
for r in random.sample(cov,3): chosen.setdefault(r['word'],r)
bad=0
for w,r in chosen.items():
    pos=r['pos'];lem=r['lemma']
    # find index file line: confirm pos by trying order noun,verb,adj with the lemma
    got=None
    for p in('noun','verb','adj'):
        o=idx(p,lem)
        if o: got=(o,p);break
    d=depth(*got);lex=DATA[got[1]][got[0]][0]
    ok=(d==r['depth'] and lex==r['lex'] and got[1]==pos)
    bad+=not ok
    print(w,lem,got,'depth',d,'lex',lex,'| stored',r['depth'],r['lex'],pos,'OK' if ok else 'MISMATCH')
print('mismatch',bad)
# full re-derivation of all covered rows
mm=0
for r in cov:
    o=idx(r['pos'],r['lemma'])
    if o is None: mm+=1;continue
    if depth(o,r['pos'])!=r['depth'] or DATA[r['pos']][o][0]!=r['lex']: mm+=1
print('all covered rows mismatches:',mm,'of',len(cov))
