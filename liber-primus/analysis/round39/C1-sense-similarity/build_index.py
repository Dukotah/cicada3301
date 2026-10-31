import sys, os, json, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R38 = os.path.join(HERE, "..", "..", "round38", "C1-semantic-road")
sys.path.insert(0, os.path.join(HERE, "..", "..", "round37", "C1-composed-clue-readings"))
import enciphers_u2_u3 as E
D = os.path.join(R38, "lex_download", "dict"); sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
man = json.load(open(os.path.join(R38, "lexicon_manifest.json")))["resource_A"]
assert sha(os.path.join(R38, "lex_download", "wn31.tar.gz")) == man["archive_sha256"]
for f, h in man["files"].items(): assert sha(os.path.join(D, f)) == h, f
def load_idx(pos):
    d = {}
    for l in open(os.path.join(D, "index." + pos), encoding="utf-8"):
        if l.startswith("  "): continue
        t = l.split(); pc = int(t[3]); d.setdefault(t[0], int(t[4 + pc + 2]))
    return d
IDX = [(p, load_idx(p)) for p in ("noun", "verb", "adj")]
DAT = {}
for p in ("noun", "verb", "adj"):
    m = {}
    for l in open(os.path.join(D, "data." + p), encoding="utf-8"):
        if l.startswith("  "): continue
        t = l.split("|")[0].split(); off = int(t[0]); lex = int(t[1]); w = int(t[3], 16); i = 4 + 2 * w
        np_ = int(t[i]); i += 1; hyp = None
        for _ in range(np_):
            sym, o2, pp, st = t[i:i + 4]; i += 4
            if sym in ("@", "@i") and hyp is None: hyp = (int(o2), {"n": "noun", "v": "verb", "a": "adj", "s": "adj", "r": "adv"}[pp])
        m[off] = (lex, hyp)
    DAT[p] = m
def cands(w):
    c = [w]
    for suf in ("ing", "es", "ed", "s"):
        if w.endswith(suf) and len(w) > len(suf):
            s = w[:-len(suf)]; c.append(s)
            if suf in ("ing", "ed"): c.append(s + "e")
            break
    return c
def val(w):
    for c in cands(w):
        for p, d in IDX:
            if c in d:
                off = d[c]; lex = DAT[p][off][0]; depth = 0; cur = (off, p); seen = set()
                while True:
                    h = DAT[cur[1]][cur[0]][1]
                    if h is None or h in seen: break
                    seen.add(h); depth += 1; cur = h
                return depth, lex, c, p
    return 0, 0, None, None
rows = []
for k, w in enumerate(E.W):
    d, lx, lem, pos = val(w.lower())
    rows.append({"k": k, "word": w.lower(), "lemma": lem, "pos": pos, "depth": d, "lex": lx, "D": {"R29": d % 29, "R28": d % 28}, "L": {"R29": lx % 29, "R28": lx % 28}})
cov = sum(1 for r in rows if r["lemma"]); md = max(r["depth"] for r in rows)
same = all(r["D"]["R29"] == r["D"]["R28"] for r in rows)
json.dump({"n_words": len(rows), "covered": cov, "max_depth": md, "D_R28_equals_R29": same, "unique_words": len(set(E.W)),
 "data_sha256": {p: sha(os.path.join(D, "data." + p)) for p in ("noun", "verb", "adj")}, "index_sha256_verified": man["files"], "rows": rows}, open(os.path.join(HERE, "lp1_sense_index.json"), "w"), indent=1)
print(cov, len(rows), md, same, len(set(r["lex"] for r in rows)), [(r["word"], r["depth"], r["lex"]) for r in rows[:12]])
