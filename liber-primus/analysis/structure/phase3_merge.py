import json
base='/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/structure/'
files={
 'simple/keystream/autokey':'phase3_p1.json',
 'vigenere L1-3':'phase3_vig123.json',
 'vigenere L4':'phase3_vig4.json',
 'interrupter beam':'phase3_interrupt.json',
}
data={}
for label,fn in files.items():
    d=json.load(open(base+fn))
    for pg,v in d.items():
        score=v[0]; method=v[1]; text=v[2]
        pg=int(pg)
        if isinstance(method,list): method='vigkey'+str(method)
        rec=(score,label+': '+str(method),text)
        if pg not in data or score>data[pg][0]:
            data[pg]=rec
flagged=[]
for pg in sorted(data):
    s,m,t=data[pg]
    flag = s>-5.5
    if flag: flagged.append(pg)
    print('PAGE %2d  best=%.3f  %s'%(pg,s,m))
    print('         %s'%t[:80])
print('FLAGGED (<-5.5 i.e. score>-5.5):',flagged)
# global best
gb=max(data.items(),key=lambda kv:kv[1][0])
print('GLOBAL BEST page %d score %.3f method %s'%(gb[0],gb[1][0],gb[1][1]))
json.dump({str(k):v for k,v in data.items()},open(base+'phase3_FINAL.json','w'),indent=1)
