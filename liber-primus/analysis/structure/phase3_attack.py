import sys, itertools
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
import src.lp.ciphers as ci, src.lp.gematria as g, src.lp.score as sc, src.lp.solve as solve
import src.lp.autokey as ak

scorer = sc.default()
raw = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt', encoding='utf-8').read()
pages = raw.split('%')
N = 29

def sn(text):
    return scorer.score_norm(text)

# stream factories
def const_stream(k):
    return lambda L: [k]*L

results = {}  # page -> (score, method, text)

def consider(page, s, method, text):
    if page not in results or s > results[page][0]:
        results[page] = (s, method, text)

for pg in range(0,14):
    p = pages[pg]
    idx = g.runes_to_indices(p)
    n = len(idx)

    # ---- Atbash (sign -1, k=0) and Atbash+shift all 29, both atbash on/off effectively ----
    for ab in (False, True):
        for k in range(29):
            # sign -1
            for sign in (-1, +1):
                t,_ = ci.transform_runes(p, const_stream(k), sign=sign, interrupters=False, atbash=ab)
                tag = ('atbash+' if ab else '') + 'shift%d_sign%+d'%(k,sign)
                consider(pg, sn(t), tag, t)

    # ---- prime / totient / prime-1 keystreams with offset search, both signs, atbash on/off ----
    streamgens = {
        'prime': lambda L,st: ci.prime_stream(L, start=st),
        'totient': lambda L,st: ci.totient_stream(L, start=st+2),
        'prime-1': lambda L,st: ci.prime_totient_stream(L, start=st),
    }
    for name, gen in streamgens.items():
        for st in range(0, 30):
            for sign in (-1,+1):
                for ab in (False, True):
                    try:
                        t,_ = ci.transform_runes(p, lambda L,gen=gen,st=st: gen(L,st), sign=sign, interrupters=False, atbash=ab)
                    except Exception:
                        continue
                    tag = '%s_off%d_sign%+d%s'%(name,st,sign,'+ab' if ab else '')
                    consider(pg, sn(t), tag, t)

    # ---- autokey ciphertext + plaintext, with short seed keys ----
    seeds = ['', 'A','F','THE','AND','ALL','FIRFUMFERENFE','DIVINITY','PRIMES','TOTIENT','CIRCUMFERENCE','WELCOME','TRUTH']
    for seed in seeds:
        ks = g.keyword_to_indices(seed) if seed else []
        for sign in (-1,+1):
            try:
                pi = ak.decrypt_ciphertext_autokey(idx, ks) if ks else None
            except Exception:
                pi = None
            # try both autokey flavors via raw index API
    # do autokey on indices directly
    for fn, fname in [(ak.decrypt_ciphertext_autokey,'ct'),(ak.decrypt_plaintext_autokey,'pt')]:
        for seed in ['A','F','THE','AND','ALL','PRIMES','TOTIENT','DIVINITY','WELCOME','TRUTH','CIRCUMFERENCE']:
            ks = g.keyword_to_indices(seed)
            try:
                pi = fn(idx, ks)
                t = g.indices_to_translit(pi)
                consider(pg, sn(t), 'autokey_%s_%s'%(fname,seed), t)
            except Exception as e:
                pass

    print('page %d partial best: %.3f %s' % (pg, results[pg][0], results[pg][1]))

# Save phase1 results
import json
with open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/structure/phase3_p1.json','w') as f:
    json.dump({str(k):[round(v[0],4),v[1],v[2][:120]] for k,v in results.items()}, f, indent=1)
print("PHASE1 DONE")
