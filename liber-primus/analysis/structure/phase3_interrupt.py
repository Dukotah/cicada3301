import sys, json
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
import src.lp.gematria as g, src.lp.score as sc, src.lp.solve as solve, src.lp.ciphers as ci
scorer=sc.default()
raw=open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt',encoding='utf-8').read()
pages=raw.split('%')
N=29
# Interrupter beam search over keystreams that solved known pages, per page.
# Keystreams: prime, totient, prime-1, plus const shifts. find_interrupters needs a stream list.
res={}
for pg in range(0,14):
    p=pages[pg]
    nrun=len(g.runes_to_indices(p))
    bscore=-999;binfo=None;btext=''
    streams={
      'prime':ci.prime_stream(nrun),
      'totient':ci.totient_stream(nrun),
      'prime-1':ci.prime_totient_stream(nrun),
    }
    # also a few const
    for k in range(29):
        streams['shift%d'%k]=[k]*nrun
    for name,stream in streams.items():
        for sign in (-1,1):
            for ab in (False,True):
                try:
                    r=solve.find_interrupters(p,stream,sign=sign,atbash=ab,beam_width=300,scorer=scorer)
                except Exception:
                    continue
                s=r.get('score_norm', scorer.score_norm(r['plaintext']))
                if s>bscore:
                    bscore=s;binfo='%s_sign%+d%s'%(name,sign,'+ab' if ab else '');btext=r['plaintext']
    res[pg]=(bscore,binfo,btext)
    print('page %d interrupt best: %.3f %s'%(pg,bscore,binfo),btext[:40])
    sys.stdout.flush()
with open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/structure/phase3_interrupt.json','w') as f:
    json.dump({str(k):[round(v[0],4),v[1],v[2][:120]] for k,v in res.items()},f,indent=1)
print("INTERRUPT DONE")
