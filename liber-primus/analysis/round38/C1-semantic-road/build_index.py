#!/usr/bin/env python3
"""Build lexicon_manifest.json + lp1_meaning_index.json per PREREG (frozen). Reads lex_download/ as DATA only."""
import sys, os, json, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "round37", "C1-composed-clue-readings"))
import enciphers_u2_u3 as E
D = os.path.join(HERE, "lex_download")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def load_idx(pos):
    d = {}
    for l in open(os.path.join(D, "dict", "index." + pos), encoding="utf-8"):
        if l.startswith("  "): continue
        t = l.split(); lem = t[0]; pc = int(t[3]); off = int(t[4 + pc + 2])
        d.setdefault(lem, off)  # first offset listed
    return d
IDX = [(p, load_idx(p)) for p in ("noun", "verb", "adj")]
def cands(w):
    c = [w]
    for suf in ("ing", "es", "ed", "s"):
        if w.endswith(suf) and len(w) > len(suf):
            s = w[:-len(suf)]; c.append(s)
            if suf in ("ing", "ed"): c.append(s + "e")
            break
    return c
def valA(w):
    for c in cands(w):
        for p, d in IDX:
            if c in d: return d[c], c, p
    return 0, None, None
N = 50000; rank = {}
for i, l in enumerate(open(os.path.join(D, "count_1w.txt"), encoding="utf-8")):
    if i >= N: break
    rank.setdefault(l.split()[0], i + 1)
ds = lambda v: sum(int(ch) for ch in str(v))
words = {}
rows = []
for k, w in enumerate(E.W):
    wl = w.lower(); a, lem, pos = valA(wl); b = rank.get(wl, N + 1)
    rows.append({"k": k, "word": wl, "A_offset": a, "A_lemma": lem, "A_pos": pos, "B_rank": b,
                 "A": {"R29": a % 29, "R28": a % 28, "D29": ds(a) % 29}, "B": {"R29": b % 29, "R28": b % 28, "D29": ds(b) % 29}})
json.dump({"n_words": len(rows), "A_covered": sum(1 for r in rows if r["A_offset"]), "B_covered": sum(1 for r in rows if r["B_rank"] <= N), "rows": rows}, open(os.path.join(HERE, "lp1_meaning_index.json"), "w"), indent=1)
man = {"date": "2026-10-30", "resource_A": {"name": "Princeton WordNet 3.1", "url": "https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz", "archive_sha256": sha(os.path.join(D, "wn31.tar.gz")),
       "files": {f: sha(os.path.join(D, "dict", f)) for f in ("index.noun", "index.verb", "index.adj")}},
       "resource_B": {"name": "Norvig count_1w.txt (Google Web Trillion Word Corpus), top 50000", "url": "https://norvig.com/ngrams/count_1w.txt", "sha256": sha(os.path.join(D, "count_1w.txt")), "N": N},
       "fallbacks_used": False, "unique_words": len(set(E.W)),
       "coverage": {"A_nonzero": sum(1 for r in rows if r["A_offset"]), "B_in_top_N": sum(1 for r in rows if r["B_rank"] <= N), "of": len(rows)}}
json.dump(man, open(os.path.join(HERE, "lexicon_manifest.json"), "w"), indent=1); print(json.dumps(man["coverage"]), man["unique_words"])
print([ (r["word"], r["A_offset"], r["B_rank"]) for r in rows[:12]])
