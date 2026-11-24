import json,sys,hashlib
ours=json.load(open(r'C:\Users\dukot\projects\cicada3301\liber-primus\dataset\liber_primus.json',encoding='utf8'))
theirs=json.load(open(r'C:\Users\dukot\AppData\Local\Temp\lpx\r\resources\liber-primus\lp2-corpus.json',encoding='utf8'))
print(type(ours), list(ours.keys())[:20] if isinstance(ours,dict) else len(ours))
print(list(theirs.keys()))
tp=theirs['pages']
print(len(tp), tp[0].keys())
print([ (p['page'],p.get('runic_count')) for p in tp])
print(sum(p.get('runic_count',0) for p in tp))
op=ours['pages'] if isinstance(ours,dict) else ours
print(len(op), op[0].keys() if isinstance(op[0],dict) else op[0])
