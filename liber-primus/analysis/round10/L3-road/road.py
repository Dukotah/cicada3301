"""L3-ROAD main run — "their meaning is the road" on the real LP2 ciphertext.

T1  count tests on per-word / per-sentence / per-line / per-page gematria sums
T2  sum-reduction decodes  (each word's meaning IS one symbol of the road)
T3  sum-predicate selectors (meaning selects which words are on the road)
T4  gematria reading order  (road = path)
T5  word-sum book cipher    (low prior, confirmatory only)

Thresholds and null design are fixed in PREREG.md (+ AMENDMENT 1). Null for
every test = the 12,956-rune stream shuffled and re-cut into LP2's IDENTICAL
word-length sequence, so word boundaries, word lengths and the rune multiset are
all preserved and only the per-word arithmetic is destroyed.
"""
import json
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import road_lib as R  # noqa: E402

T0 = time.time()
rng = np.random.default_rng(3301)
OUT = {}

# ------------------------------------------------------------------ load LP2
PAGES = R.lp2_words()
WORDS = [np.asarray(w, dtype=np.int64) for p in PAGES for w in p]
LENS = np.array([len(w) for w in WORDS])
NW = len(WORDS)
STREAM = np.concatenate(WORDS)
CUTS = np.cumsum(LENS)[:-1]
assert NW == 2928 and STREAM.size == 12956
OUT["parse"] = dict(words=NW, runes=int(STREAM.size),
                    mean_len=float(LENS.mean()), lp2_stream_score=R.score(STREAM))

# sentence / line / page groupings (word indices)
_raw = open(os.path.join(R.ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
_segs = [s for s in _raw.split("%") if re.search(r"[ᚠ-᛿]", s)][:-2]


def _sentence_groups():
    """Word-index lists grouped by '.', '&', '$' (sentence/paragraph/section)."""
    g, cur, wi = [], [], 0
    for s in _segs:
        t = s.replace("/", "").replace("\n", "")
        buf = ""
        for ch in t + "\x00":
            if re.match(r"[ᚠ-᛿]", ch):
                buf += ch
                continue
            if buf:
                cur.append(wi)
                wi += 1
                buf = ""
            if ch in ".&$" or ch == "\x00":
                if cur:
                    g.append(cur)
                cur = []
        if cur:
            g.append(cur)
            cur = []
    return g, wi


SENT, _nw_check = _sentence_groups()
assert _nw_check == 2928, _nw_check

# physical LINES: a line is a rune run between '/' or newline. Words straddle
# line breaks (458 of 604 do), so lines are grouped over RUNES, not words.
LINE_RUNES = []
_ptr = 0
for s in _segs:
    for ln in re.split(r"[/\n]", s):
        rr = [c for c in ln if re.match(r"[ᚠ-᛿]", c)]
        if rr:
            LINE_RUNES.append(np.array([R.RUNE_TO_IDX[c] for c in rr], dtype=np.int64))
assert sum(a.size for a in LINE_RUNES) == 12956
LINE_OFF = np.r_[0, np.cumsum([a.size for a in LINE_RUNES])[:-1]]
LINE_LEN = np.array([a.size for a in LINE_RUNES])

PAGE = []
_wi = 0
for p in PAGES:
    PAGE.append(list(range(_wi, _wi + len(p))))
    _wi += len(p)

S = R.wsum(WORDS)
OUT["sums"] = dict(n=int(S.size), min=int(S.min()), max=int(S.max()),
                   mean=float(S.mean()), total=int(S.sum()),
                   distinct=int(np.unique(S).size))

# --------------------------------------------------------------- null machinery
NPERM_COUNT = 2000
NPERM_READ = 200


def shuffled_words(r):
    return list(np.split(r.permutation(STREAM), CUTS))


# ------------------------------------------------------------------ helpers
_SQ = set(i * i for i in range(1, 3000))
_FIB = set()
a, b = 1, 2
while a < 10 ** 7:
    _FIB.add(a)
    a, b = b, a + b
CICADA = {3301, 761, 1033, 2113, 3203, 1595277641, 317, 853, 1039, 1237, 157,
          1259, 1031, 1229, 2647, 4577, 1791, 468}
_PI = np.cumsum(R._S.astype(np.int32))          # prime-counting function pi(n)


def digit_sum(x):
    return np.array([sum(int(d) for d in str(int(v))) for v in x])


def omega(x):
    """number of prime factors with multiplicity (small values only)"""
    out = []
    for v in x:
        v = int(v)
        c = 0
        d = 2
        while d * d <= v:
            while v % d == 0:
                v //= d
                c += 1
            d += 1
        if v > 1:
            c += 1
        out.append(c)
    return np.array(out)


def lpf(x):
    out = []
    for v in x:
        v = int(v)
        best = 1
        d = 2
        while d * d <= v:
            while v % d == 0:
                best = d
                v //= d
            d += 1
        out.append(v if v > 1 else best)
    return np.array(out)


# ======================================================================= T1a
def t1a_stats(sums):
    return {
        "prime": float(R.is_prime(sums).mean()),
        "emirp": float(R.is_emirp(sums).mean()),
        "s+1_prime": float(R.is_prime(sums + 1).mean()),
        "s-1_prime": float(R.is_prime(sums - 1).mean()),
        "s%29==0": float((sums % 29 == 0).mean()),
        "s%7==0": float((sums % 7 == 0).mean()),
        "s%13==0": float((sums % 13 == 0).mean()),
        "square": float(np.mean([int(v) in _SQ for v in sums])),
        "fibonacci": float(np.mean([int(v) in _FIB for v in sums])),
        "gematria_prime": float(np.isin(sums, R.PRIME).mean()),
        "cicada_number": float(np.mean([int(v) in CICADA for v in sums])),
        "palindrome": float(np.mean([str(int(v)) == str(int(v))[::-1] for v in sums])),
        "distinct_frac": float(np.unique(sums).size / sums.size),
    }


real = t1a_stats(S)
null = {k: [] for k in real}
for _ in range(NPERM_COUNT):
    sw = np.add.reduceat(R.PRIME[rng.permutation(STREAM)],
                         np.r_[0, np.cumsum(LENS)[:-1]])
    st = t1a_stats(sw)
    for k in real:
        null[k].append(st[k])
t1a = {}
NSTAT = len(real)
for k in real:
    v = np.array(null[k])
    z = (real[k] - v.mean()) / (v.std() + 1e-12)
    p = (np.sum(np.abs(v - v.mean()) >= abs(real[k] - v.mean())) + 1) / (len(v) + 1)
    t1a[k] = dict(real=round(real[k], 5), null_mean=round(float(v.mean()), 5),
                  null_sd=round(float(v.std()), 5), z=round(float(z), 3),
                  p=round(float(p), 5),
                  SIGNAL=bool(abs(z) >= 4.0 and p < 0.001 / NSTAT))
OUT["T1a_word_sums"] = t1a
print(f"[T1a done {time.time()-T0:.0f}s]")

# ======================================================================= T1b
t1b = {}
for nm, grp in (("sentence", SENT), ("line", None), ("page", PAGE)):
    if nm == "line":
        gs = np.add.reduceat(R.PRIME[STREAM], LINE_OFF)
    else:
        gs = np.array([int(S[g].sum()) for g in grp if g])
    rp = float(R.is_prime(gs).mean())
    re_ = float(R.is_emirp(gs).mean())
    nl_p, nl_e = [], []
    for _ in range(400):
        perm = rng.permutation(STREAM)
        if nm == "line":
            g2 = np.add.reduceat(R.PRIME[perm], LINE_OFF)
        else:
            sw = np.add.reduceat(R.PRIME[perm], np.r_[0, np.cumsum(LENS)[:-1]])
            g2 = np.array([int(sw[g].sum()) for g in grp if g])
        nl_p.append(float(R.is_prime(g2).mean()))
        nl_e.append(float(R.is_emirp(g2).mean()))
    nl_p, nl_e = np.array(nl_p), np.array(nl_e)
    # null for the "a group sum equals a known Cicada number" coincidence count
    nl_c = []
    for _ in range(400):
        perm = rng.permutation(STREAM)
        if nm == "line":
            g2 = np.add.reduceat(R.PRIME[perm], LINE_OFF)
        else:
            sw = np.add.reduceat(R.PRIME[perm], np.r_[0, np.cumsum(LENS)[:-1]])
            g2 = np.array([int(sw[g].sum()) for g in grp if g])
        nl_c.append(sum(int(v) in CICADA for v in g2))
    nl_c = np.array(nl_c)
    hits = [int(v) for v in gs if int(v) in CICADA]
    t1b[nm] = dict(
        n=int(gs.size),
        prime=dict(real=round(rp, 4), null_mean=round(float(nl_p.mean()), 4),
                   z=round(float((rp - nl_p.mean()) / (nl_p.std() + 1e-12)), 3)),
        emirp=dict(real=round(re_, 4), null_mean=round(float(nl_e.mean()), 4),
                   z=round(float((re_ - nl_e.mean()) / (nl_e.std() + 1e-12)), 3)),
        cicada_hits=hits,
        cicada_hits_null=dict(mean=round(float(nl_c.mean()), 3),
                              sd=round(float(nl_c.std()), 3),
                              z=round(float((len(hits) - nl_c.mean()) /
                                            (nl_c.std() + 1e-12)), 3)),
        min=int(gs.min()), max=int(gs.max()))
OUT["T1b_group_sums"] = t1b
OUT["T1b_total_corpus_sum"] = dict(
    total=int(S.sum()), is_prime=bool(R.is_prime(np.array([int(S.sum())]))[0]),
    per_page_product_mod=None)
print(f"[T1b done {time.time()-T0:.0f}s]")


# ======================================================================= T2/T3/T4/T5
def reductions(words, sums):
    """T2: each word -> one rune. Returns {name: rune-index array}."""
    d = {}
    s = sums
    d["s%29"] = s % 29
    d["atbash(s%29)"] = (28 - s % 29)
    d["-s%29"] = (-s) % 29
    d["(s//29)%29"] = (s // 29) % 29
    d["digitsum%29"] = digit_sum(s) % 29
    d["pi(s)%29"] = _PI[np.clip(s, 0, _PI.size - 1)] % 29
    d["omega(s)%29"] = omega(s) % 29
    d["lpf(s)%29"] = lpf(s) % 29
    d["cumsum%29"] = np.cumsum(s) % 29
    d["diff%29"] = np.r_[0, np.diff(s)] % 29
    d["(s+i)%29"] = (s + np.arange(s.size)) % 29
    d["(s-i)%29"] = (s - np.arange(s.size)) % 29
    d["s%29 rev"] = (s % 29)[::-1]
    d["primeidx(s)"] = np.array([R.PRIME.tolist().index(int(v)) if int(v) in
                                 set(R.PRIME.tolist()) else 0 for v in s])
    d["len*s%29"] = (s * np.array([len(w) for w in words])) % 29
    # F-interrupter convention: drop every word containing the null rune F(=0)
    keep = np.array([0 not in set(w.tolist()) for w in words])
    d["s%29 noF-words"] = (s[keep] % 29)
    # other granularities of "meaning": sentence / line / page sums
    d["sentence_s%29"] = np.array([int(s[g].sum()) for g in SENT if g]) % 29
    d["line_s%29"] = np.add.reduceat(
        R.PRIME[np.concatenate(list(words))], LINE_OFF) % 29
    return d


PREDS = {}


def build_preds(s):
    p = {"prime": R.is_prime(s), "emirp": R.is_emirp(s),
         "s+1_prime": R.is_prime(s + 1), "s-1_prime": R.is_prime(s - 1),
         "square": np.array([int(v) in _SQ for v in s]),
         "fibonacci": np.array([int(v) in _FIB for v in s]),
         "gematria_prime": np.isin(s, R.PRIME),
         "palindrome": np.array([str(int(v)) == str(int(v))[::-1] for v in s]),
         "pi(s)_prime": R.is_prime(_PI[np.clip(s, 0, _PI.size - 1)])}
    for k in (2, 3, 5, 7, 11, 13, 29, 33, 43):
        p[f"s%{k}==0"] = (s % k == 0)
    for k in range(29):
        p[f"s%29=={k}"] = (s % 29 == k)
    return p


def readings(words, sums):
    """All T2/T3/T4 readings for one corpus -> {name: rune array}."""
    out = {}
    for nm, v in reductions(words, sums).items():
        out["T2:" + nm] = np.asarray(v) % 29
    for pn, mask in build_preds(sums).items():
        k = np.where(mask)[0]
        if k.size < 30:
            continue
        out[f"T3:{pn}:whole"] = np.concatenate([words[i] for i in k])
        out[f"T3:{pn}:first"] = np.array([words[i][0] for i in k])
        out[f"T3:{pn}:last"] = np.array([words[i][-1] for i in k])
        out[f"T3:{pn}:at_s%len"] = np.array(
            [words[i][int(sums[i]) % len(words[i])] for i in k])
    for on, key in (("asc", sums), ("desc", -sums), ("mod29", sums % 29),
                    ("mod26", sums % 26), ("pi", _PI[np.clip(sums, 0, _PI.size - 1)]),
                    ("len_then_s", np.array([len(w) for w in words]) * 10000 + sums)):
        o = np.argsort(key, kind="stable")
        out["T4:order_" + on] = np.concatenate([words[i] for i in o])
    return out


rd_real = readings(WORDS, S)
print(f"[readings built {len(rd_real)} {time.time()-T0:.0f}s]")

null_by_name = {k: [] for k in rd_real}
for t in range(NPERM_READ):
    sw = shuffled_words(rng)
    ss = R.wsum(sw)
    rd = readings(sw, ss)
    for k in null_by_name:
        if k in rd:
            null_by_name[k].append(R.score(rd[k]))
    if t % 10 == 0:
        print(f"  null {t}/{NPERM_READ}  {time.time()-T0:.0f}s")

rows = []
for k, seq in rd_real.items():
    sc = R.score(seq)
    v = np.array(null_by_name[k]) if null_by_name[k] else np.array([-16.7])
    z = (sc - v.mean()) / (v.std() + 1e-9)
    rows.append(dict(name=k, n=int(np.asarray(seq).size), score=round(sc, 4),
                     null_mean=round(float(v.mean()), 4),
                     null_sd=round(float(v.std()), 4),
                     null_max=round(float(v.max()), 4), z=round(float(z), 2),
                     HIT=bool(sc >= -12.0 and np.asarray(seq).size >= 100
                              and sc > v.max() + 0.5) or bool(z >= 8.0),
                     head=R.show(seq, 70)))
rows.sort(key=lambda r: -r["score"])
OUT["T234_readings"] = rows
OUT["T234_summary"] = dict(
    n_readings=len(rows), best=rows[0]["name"], best_score=rows[0]["score"],
    best_z=rows[0]["z"],
    global_null_max=round(max(r["null_max"] for r in rows), 4),
    n_hits=sum(r["HIT"] for r in rows))
print(f"[T2/3/4 done {time.time()-T0:.0f}s]  best {rows[0]['name']} {rows[0]['score']}")

# ======================================================================= T5
t5 = []
KEYTEXTS = []
for f in ("kjv.txt", "moby.txt", "pride.txt", "war.txt"):
    p = os.path.join(R.ROOT, "data", f)
    if os.path.exists(p):
        KEYTEXTS.append((f, open(p, encoding="utf-8", errors="ignore").read()))
for f in ("mabinogion.txt", "self_reliance.txt", "book_of_the_law.txt",
          "agrippa.txt", "solved_plaintext.txt", "runepoem_oe.txt"):
    p = os.path.join(R.ROOT, "data", "keys", f)
    if os.path.exists(p):
        KEYTEXTS.append((f, open(p, encoding="utf-8", errors="ignore").read()))

for nm, txt in KEYTEXTS:
    tw = [w for w in re.split(r"[^A-Za-z]+", txt) if w]
    if len(tw) < 100:
        continue
    M = len(tw)
    for scheme, idxs in (("s%M", S % M), ("cumsum%M", np.cumsum(S) % M),
                         ("(s*i)%M", (S * np.arange(1, NW + 1)) % M)):
        letters = "".join(tw[int(j)][0] for j in idxs)
        seq = np.array(R.eng_to_runes(letters), dtype=np.int64)
        nulls = []
        for _ in range(8):
            s2 = R.wsum(shuffled_words(rng))
            i2 = (s2 % M) if scheme == "s%M" else (
                np.cumsum(s2) % M if scheme == "cumsum%M"
                else (s2 * np.arange(1, NW + 1)) % M)
            l2 = "".join(tw[int(j)][0] for j in i2)
            nulls.append(R.score(np.array(R.eng_to_runes(l2), dtype=np.int64)))
        nl = np.array(nulls)
        t5.append(dict(text=nm, scheme=scheme, n=int(seq.size),
                       score=round(R.score(seq), 4),
                       null_mean=round(float(nl.mean()), 4),
                       null_max=round(float(nl.max()), 4),
                       z=round(float((R.score(seq) - nl.mean()) / (nl.std() + 1e-9)), 2),
                       head=R.show(seq, 60)))
t5.sort(key=lambda r: -r["score"])
OUT["T5_booklike"] = t5
print(f"[T5 done {time.time()-T0:.0f}s] best {t5[0] if t5 else None}")

OUT["runtime_s"] = round(time.time() - T0, 1)
json.dump(OUT, open(os.path.join(HERE, "road_results.json"), "w"), indent=1)
print("\n== T1a ==")
for k, v in OUT["T1a_word_sums"].items():
    print(f"  {k:16s} real={v['real']:.5f} null={v['null_mean']:.5f} "
          f"z={v['z']:+7.3f} p={v['p']:.5f} {'SIGNAL' if v['SIGNAL'] else ''}")
print("\n== T2/T3/T4 top 12 ==")
for r in rows[:12]:
    print(f"  {r['score']:8.3f} z={r['z']:+7.2f} n={r['n']:6d} {r['name']:28s} {r['head'][:48]}")
print("\n== T5 top 5 ==")
for r in t5[:5]:
    print(f"  {r['score']:8.3f} z={r['z']:+6.2f} {r['text']:22s} {r['scheme']:10s} {r['head'][:40]}")
print(f"\nHITS: {OUT['T234_summary']['n_hits']}   runtime {OUT['runtime_s']}s")
