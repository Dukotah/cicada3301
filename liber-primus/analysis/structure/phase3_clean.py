"""Re-run recording best NON-overfitting method per page (exclude vigauto column
hill-climb which optimizes the reported metric => spurious). Records best among
shift/atbash, vigenere L1-2 exhaustive, prime/totient/prime-1 keystreams, autokey."""
import sys, json, itertools
sys.path.insert(0, 'src'); sys.path.insert(0, 'analysis')
from lp import gematria as gp, ciphers, autokey, score
from run_stats import load_pages

sc = score.default()
N = gp.N
pages = load_pages()

WORDS = ["THE","AND","THAT","WITHIN","YOU","ARE","FOR","WITH","THIS","WHICH",
         "FROM","HAVE","NOT","ALL","YOUR","WILL","SHALL","TRUTH","DIVINITY",
         "WISDOM","PRIMUS","LIBER","CIRCUMFERENCE","INSTAR","KNOW","SACRED",
         "MOBIUS","REALITY","PILGRIM","ENLIGHTEN","BELIEVE","MASTER","PARABLE"]

def sscore(idxs): return sc.score_norm(gp.indices_to_translit(idxs))
def frags(idxs):
    t = gp.indices_to_translit(idxs)
    return [w for w in WORDS if w in t], t

best = {}
def consider(pi, sval, method, idxs):
    cur = best.get(pi)
    if cur is None or sval > cur["score"]:
        fr, t = frags(idxs)
        best[pi] = {"page": pi, "score": round(sval,4), "method": method,
                    "fragments": fr, "translit": t[:160]}

for pi in range(14, 28):
    idxs = pages[pi]
    for name, base in [("plain", idxs), ("atbash", ciphers.atbash_indices(idxs))]:
        for sh in range(N):
            consider(pi, sscore([(x-sh)%N for x in base]), f"{name}+shift-{sh}", [(x-sh)%N for x in base])
            consider(pi, sscore([(x+sh)%N for x in base]), f"{name}+shift+{sh}", [(x+sh)%N for x in base])
    for keylen in (1,2):
        for key in itertools.product(range(N), repeat=keylen):
            for sign in (-1,1):
                for atb in (False,True):
                    b = ciphers.atbash_indices(idxs) if atb else idxs
                    stream = [key[i%keylen] for i in range(len(b))]
                    dec = ciphers.apply_stream_to_indices(b, stream, sign=sign)
                    consider(pi, sscore(dec), f"vig L{keylen} key{key} s{sign:+d} atb{atb}", dec)
    for sign in (-1,1):
        for atb in (False,True):
            b = ciphers.atbash_indices(idxs) if atb else idxs
            nlen = len(b)
            for off in range(0,60):
                ps = ciphers.prime_stream(nlen+off)[off:off+nlen]
                ts = ciphers.totient_stream(nlen+off, start=2)[off:off+nlen]
                pts = ciphers.prime_totient_stream(nlen+off)[off:off+nlen]
                pm1 = [(p-1)%N for p in ciphers.prime_stream(nlen+off)[off:off+nlen]]
                for nm, stream in (("prime",ps),("totient",ts),("primetot",pts),("prime-1",pm1)):
                    if len(stream)!=nlen: continue
                    dec = ciphers.apply_stream_to_indices(b, stream, sign=sign)
                    consider(pi, sscore(dec), f"key {nm} off{off} s{sign:+d} atb{atb}", dec)
    for atb in (False,True):
        for sign in (-1,1):
            for seed in range(N):
                d1 = autokey.decrypt_ciphertext_autokey(idxs, seed=seed, sign=sign, atbash=atb)
                consider(pi, sscore(d1), f"autokey-CT seed{seed} s{sign:+d} atb{atb}", d1)
                d2 = autokey.decrypt_plaintext_autokey(idxs, seed=seed, sign=sign, atbash=atb)
                consider(pi, sscore(d2), f"autokey-PT seed{seed} s{sign:+d} atb{atb}", d2)
    b = best[pi]
    print(f"page {pi}: {b['score']} {b['method']} frags={b['fragments']}", flush=True)

allrecs=[best[p] for p in sorted(best)]
json.dump({"range":"14-27","perPageBest":allrecs}, open('analysis/structure/phase3_clean.json','w'), indent=2)
g=max(allrecs,key=lambda r:r["score"])
print("\nGLOBAL BEST (clean):", g["page"], g["score"], g["method"])
print("flagged:", [(r["page"],r["score"],r["fragments"]) for r in allrecs if r["score"]>-5.5])
