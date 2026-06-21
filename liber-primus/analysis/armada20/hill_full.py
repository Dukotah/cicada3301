"""Full 2x2 across pages + offsets, and bounded 3x3 sample. id=16."""
import sys, time, random
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20')
import hill
from lp.gematria import indices_to_translit

pages = hill.load_pages()
score_idx = hill.score_idx
crib_count = hill.crib_count

def best_2x2(idx, topn=5):
    best = []
    for a in range(29):
        for b in range(29):
            for c in range(29):
                for d in range(29):
                    if (a*d - b*c) % 29 == 0: continue
                    dec = hill.hill_decrypt2(idx, [a,b,c,d])
                    s = score_idx(dec)
                    if len(best) < topn or s > best[-1][0]:
                        best.append((s, (a,b,c,d)))
                        best.sort(key=lambda x: -x[0]); best = best[:topn]
    return best

# Test pages 0-9, both alignments (offset 0 and 1)
print("=== 2x2 sweep, pages 0-9, offsets {0,1} ===")
overall = []
for p in range(10):
    idx = pages[p]
    for off in (0, 1):
        sub = idx[off:]
        b = best_2x2(sub, topn=3)
        for s, m in b:
            overall.append((s, p, off, m))
        s0, m0 = b[0]
        print(f"page {p} off {off}: best {s0:7.3f} mat={m0}")
overall.sort(key=lambda x: -x[0])
print("--- global top 8 ---")
for s, p, off, m in overall[:8]:
    sub = pages[p][off:]
    tr = indices_to_translit(hill.hill_decrypt2(sub, list(m)))
    print(f"{s:7.3f} p{p} off{off} mat={m} crib={crib_count(tr)} {tr[:45]}")
