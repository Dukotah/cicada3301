#!/usr/bin/env python3
"""R44 W2-C4 step 1 — per-page passphrase builder (PREREG 'Key-derivation rules', FIXED).

Verifies input identity (sha1 of relikd pN.jpg vs dataset published_sha1; canon %-segment
rune counts vs dataset n_runes), then emits results/keys_per_page.json.
"""
import json, os, hashlib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CELL = os.path.abspath(os.path.join(HERE, ".."))

dataset = json.load(open(os.path.join(LP, "dataset", "liber_primus.json")))
gem = dataset["gematria"]
R2L = {g["rune"]: g["translit"] for g in gem}          # rune char -> latin
R2P = {g["rune"]: g["prime"] for g in gem}             # rune char -> prime
I2L = {g["index"]: g["translit"] for g in gem}         # index -> latin
RUNES = set(R2L)

# ---- identity verification (PREREG 'Inputs') ----
bad = []
for p in dataset["pages"]:
    n = p["page"]
    if n > 55:
        continue
    fp = os.path.join(LP, "data", "relikd", f"p{n}.jpg")
    h = hashlib.sha1(open(fp, "rb").read()).hexdigest()
    if h != p["image"]["published_sha1"]:
        bad.append((n, h, p["image"]["published_sha1"]))
assert not bad, f"sha1 mismatch: {bad}"

canon = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
segs = canon.split("%")
seg_runes = ["".join(c for c in s if c in RUNES) for s in segs]
for p in dataset["pages"]:
    assert len(seg_runes[p["page"]]) == p["n_runes"], f"segment/page mismatch at {p['page']}"
print("identity OK: 56 sha1 matches; 57 segment rune-counts == dataset n_runes")

# ---- red channel slices ----
ch = json.load(open(os.path.join(LP, "analysis", "round44", "P1-red-ink", "channel.json")))
starts = ch["page_starts"] + [ch["canon_total"]]
red_pos = ch["full"]["pos"]
red_idx = ch["full"]["idx"]
def red_slice(m):
    lo, hi = starts[m], starts[m + 1]
    return [i for p_, i in zip(red_pos, red_idx) if lo <= p_ < hi]

def words(seg):
    out, cur = [], []
    for c in seg:
        if c in RUNES:
            cur.append(c)
        elif cur:
            out.append("".join(cur)); cur = []
    if cur:
        out.append("".join(cur))
    return out

def translit(rs):
    return "".join(R2L[c] for c in rs)

keys = {}
for n in range(56):
    seg = segs[n]
    ws = words(seg)
    W1 = ws[0]
    W2 = ws[1] if len(ws) > 1 else ""
    ks = []
    t1 = translit(W1)
    ks += [t1.upper(), t1.lower(), t1.capitalize(), W1]                       # A
    t12 = translit(W1 + W2)
    ks += [t12.upper(), t12.lower()]                                          # B
    for m in (n - 1, n, n + 1):                                               # C
        if 0 <= m <= 56:
            sl = red_slice(m)
            if sl:
                tr = "".join(I2L[i] for i in sl)
                rn = "".join(g["rune"] for i in sl for g in [gem[i]])
                ks += [tr.upper(), tr.lower(), rn]
    ks += [str(sum(R2P[c] for c in seg_runes[n])),                            # D
           str(sum(R2P[c] for c in W1))]
    ks += [str(n), f"{n:02d}", f"p{n}", f"page{n}",                           # E
           str(n + 1), f"{n+1:02d}", f"p{n+1}", f"page{n+1}", f"{n}.jpg"]
    seen, ded = set(), []
    for k in ks:
        if k and k not in seen:
            seen.add(k); ded.append(k)
    keys[str(n)] = ded

counts = [len(v) for v in keys.values()]
out = {"rule_source": "PREREG.md Key-derivation rules (FIXED)",
       "n_pages": 56, "keys_total": sum(counts),
       "min_per_page": min(counts), "max_per_page": max(counts),
       "keys": keys}
json.dump(out, open(os.path.join(CELL, "results", "keys_per_page.json"), "w"),
          ensure_ascii=False, indent=1)
print(f"keys/page min {min(counts)} max {max(counts)} total {sum(counts)}")
print("sample p12 A1:", keys["12"][0], "| p33 D1:", [k for k in keys["33"] if k.isdigit()][:1])
