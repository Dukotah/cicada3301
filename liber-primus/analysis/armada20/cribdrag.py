import sys, os, glob
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp import gematria as gp
from lp.score import default

Q = default()

CRIBS = ["INSTAR","EMERGENCE","DIVINITY","WISDOM","THEPRIMES","PARABLE",
         "SACRED","TOTIENT","CIRCUMFERENCE"]

# Load ciphertext pages (0..55 per task; chunk 56 ignored but harmless)
pages_raw = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt').read().split('%')
PAGES = [gp.runes_to_indices(p) for p in pages_raw]

# Build reference text index streams from data/ for matching implied key
ref_texts = {}
datadir = '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data'
for f in glob.glob(datadir+'/keys/*.txt') + [datadir+'/kjv.txt', datadir+'/moby.txt',
                                             datadir+'/pride.txt', datadir+'/war.txt']:
    try:
        t = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    # Reference can be runic OR latin. Convert latin -> indices via keyword_to_indices per char-run.
    if any(c in gp.RUNE_TO_IDX for c in t[:2000]):
        idx = gp.runes_to_indices(t)
    else:
        # latin text: strip to letters, map greedily
        s = ''.join(c for c in t.upper() if c.isalpha())
        try:
            idx = gp.keyword_to_indices(s[:5000])
        except Exception:
            idx = []
    ref_texts[os.path.basename(f)] = idx

# Also a "raw runic concatenated" form for the latin texts mapped to runes string for substring search
ref_strings = {}
for name, idx in ref_texts.items():
    ref_strings[name] = ''.join(gp.IDX_TO_RUNE[i] for i in idx[:8000])

def implied_key_str(ck_indices):
    return ''.join(gp.IDX_TO_RUNE[i] for i in ck_indices)

results = []
for crib in CRIBS:
    cidx = gp.keyword_to_indices(crib)
    L = len(cidx)
    for pg in range(56):
        C = PAGES[pg]
        for pos in range(0, len(C)-L+1):
            seg = C[pos:pos+L]
            # implied running key K = (C - P) mod 29   (since decrypt P = C - K)
            K = [(seg[j] - cidx[j]) % 29 for j in range(L)]
            ktrans = gp.indices_to_translit(K)
            sc = Q.score_norm(ktrans)
            # check substring match against any reference text
            krune = implied_key_str(K)
            match = None
            for name, rs in ref_strings.items():
                if krune in rs:
                    match = name
                    break
            results.append((sc, crib, pg, pos, ktrans, match))

# also check the reverse direction: P = C + K  => K = (P - C) = (crib - C)
results2 = []
for crib in CRIBS:
    cidx = gp.keyword_to_indices(crib)
    L = len(cidx)
    for pg in range(56):
        C = PAGES[pg]
        for pos in range(0, len(C)-L+1):
            seg = C[pos:pos+L]
            K = [(cidx[j] - seg[j]) % 29 for j in range(L)]
            ktrans = gp.indices_to_translit(K)
            sc = Q.score_norm(ktrans)
            krune = implied_key_str(K)
            match = None
            for name, rs in ref_strings.items():
                if krune in rs:
                    match = name
                    break
            results2.append((sc, crib, pg, pos, ktrans, match))

print("=== Direction A (K=C-crib), top implied-key by score ===")
for r in sorted(results, reverse=True)[:20]:
    print(f"{r[0]:7.3f} crib={r[1]:14s} pg={r[2]:2d} pos={r[3]:3d} key={r[4]:18s} match={r[5]}")

print("\n=== Direction B (K=crib-C), top implied-key by score ===")
for r in sorted(results2, reverse=True)[:20]:
    print(f"{r[0]:7.3f} crib={r[1]:14s} pg={r[2]:2d} pos={r[3]:3d} key={r[4]:18s} match={r[5]}")

print("\n=== ANY substring matches to reference texts ===")
allm = [r for r in results+results2 if r[5]]
for r in allm[:50]:
    print(f"{r[0]:7.3f} crib={r[1]:14s} pg={r[2]:2d} pos={r[3]:3d} key={r[4]:18s} match={r[5]}")
print("total matches:", len(allm))
