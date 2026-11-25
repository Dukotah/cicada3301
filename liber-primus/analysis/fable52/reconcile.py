import json,sys,hashlib,os
# R46-A1: repo-relative. lp2-corpus.json is the external side by design; a sha256-pinned copy lives in inputs/.
HERE=os.path.dirname(os.path.abspath(__file__))
LPROOT=os.path.abspath(os.path.join(HERE,'..','..'))
CORPUS=os.path.join(HERE,'inputs','lp2-corpus.json')
assert hashlib.sha256(open(CORPUS,'rb').read()).hexdigest()=='7f311254d406b755df39510b8b3f4e53d7dfaea87a0320074c16507d46a07522', 'inputs/lp2-corpus.json drifted from its pin'
ours=json.load(open(os.path.join(LPROOT,'dataset','liber_primus.json'),encoding='utf8'))
theirs=json.load(open(CORPUS,encoding='utf8'))
print(type(ours), list(ours.keys())[:20] if isinstance(ours,dict) else len(ours))
print(list(theirs.keys()))
tp=theirs['pages']
print(len(tp), tp[0].keys())
print([ (p['page'],p.get('runic_count')) for p in tp])
print(sum(p.get('runic_count',0) for p in tp))
op=ours['pages'] if isinstance(ours,dict) else ours
print(len(op), op[0].keys() if isinstance(op[0],dict) else op[0])
