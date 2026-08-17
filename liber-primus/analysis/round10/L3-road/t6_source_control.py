"""L3-ROAD T6 — the SOURCE-SIDE control: does the author's own PLAINTEXT carry
engineered per-word gematria structure at all?

Every other test in this lane asks whether LP2's *ciphertext* word sums were
engineered. That question is weak on its own: an additive keystream would erase
plaintext structure anyway, so a null is expected either way.

T6 asks the prior question, on data where the plaintext IS known: in the SOLVED
Liber Primus pages, are per-word gematria sums marked (prime / emirp / etc.)
above chance? If the author never engineered word sums even where we can read
them, then "their meaning is the road" was never a per-word arithmetic
instruction, and the whole family this lane tests is refuted at its source
rather than merely unobserved in the ciphertext.

Null: the same text's rune stream shuffled and re-cut into the identical
word-length sequence (preserves inventory + word lengths, destroys arithmetic).
Pre-registered bar, same as T1: |z| >= 4.0 and p < 0.001/Nstat.
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "..", "src"))
import road_lib as R  # noqa: E402
from lp import corpus  # noqa: E402

rng = np.random.default_rng(3301)

# solved runic pages whose plaintext is documented PROSE (not hashes/PGP blocks)
WANT = ("03.jpg", "05.jpg", "14.jpg", "15.jpg", "16.jpg", "73.jpg", "74.jpg")
pages = corpus.parse()
texts = {}
for p in pages:
    lbl = p["label"]
    if not any(w in lbl for w in WANT):
        continue
    pt = (p.get("plaintext") or "")
    pt = re.sub(r"=\s*[\d,]+(\s*\(composite\))?", " ", pt)   # strip "= 317" tags
    pt = re.sub(r"[^A-Za-z\s]", " ", pt)
    if len(re.findall(r"[A-Za-z]+", pt)) >= 8:
        texts[lbl] = pt

# also the published per-sentence gematria sums the author's own transcript lists
PUBLISHED = [317, 2113, 2647, 4577, 1791, 468, 853, 1039, 1237, 157]

OUT = {"pages_used": list(texts), "published_sentence_sums": {}}

pv = np.array(PUBLISHED)
OUT["published_sentence_sums"] = dict(
    n=len(PUBLISHED),
    prime=[int(v) for v in pv[R.is_prime(pv)]],
    composite=[int(v) for v in pv[~R.is_prime(pv)]],
    prime_rate=float(R.is_prime(pv).mean()),
    note="the author's OWN published sums include composites -> primality was "
         "not enforced on sentence sums")

# ------------------------------------------------- per-word sums of the plaintext
allw = []
for lbl, t in texts.items():
    allw += R.eng_words_to_runes(t)
allw = [np.asarray(w, dtype=np.int64) for w in allw if len(w) > 0]
lens = np.array([len(w) for w in allw])
stream = np.concatenate(allw)
cuts = np.r_[0, np.cumsum(lens)[:-1]]
S = np.add.reduceat(R.PRIME[stream], cuts)


def stats(s):
    return {"prime": float(R.is_prime(s).mean()),
            "emirp": float(R.is_emirp(s).mean()),
            "s+1_prime": float(R.is_prime(s + 1).mean()),
            "s%29==0": float((s % 29 == 0).mean()),
            "gematria_prime": float(np.isin(s, R.PRIME).mean())}


real = stats(S)
null = {k: [] for k in real}
for _ in range(4000):
    s2 = np.add.reduceat(R.PRIME[rng.permutation(stream)], cuts)
    st = stats(s2)
    for k in real:
        null[k].append(st[k])

res = {}
NST = len(real)
for k in real:
    v = np.array(null[k])
    z = (real[k] - v.mean()) / (v.std() + 1e-12)
    p = (np.sum(np.abs(v - v.mean()) >= abs(real[k] - v.mean())) + 1) / (len(v) + 1)
    res[k] = dict(real=round(real[k], 5), null_mean=round(float(v.mean()), 5),
                  null_sd=round(float(v.std()), 5), z=round(float(z), 3),
                  p=round(float(p), 5),
                  SIGNAL=bool(abs(z) >= 4.0 and p < 0.001 / NST))
OUT["solved_plaintext_word_sums"] = dict(n_words=int(len(allw)),
                                         n_runes=int(stream.size), stats=res)

json.dump(OUT, open(os.path.join(HERE, "t6_results.json"), "w"), indent=1)
print("solved-plaintext words:", len(allw), " runes:", stream.size,
      " pages:", list(texts))
for k, v in res.items():
    print(f"  {k:16s} real={v['real']:.5f} null={v['null_mean']:.5f} "
          f"z={v['z']:+7.3f} p={v['p']:.5f} {'SIGNAL' if v['SIGNAL'] else ''}")
print("\npublished sentence sums:", OUT["published_sentence_sums"])

# ---------------------------------------------------------------------------
# T6b — is the emirp/s+1 excess AUTHORIAL or just a property of English?
# Decisive control: run the identical statistic on ordinary English passages of
# the same size (270 words), each against its own shuffled null.
eng = []
for f in ("pride.txt", "moby.txt", "kjv.txt", "war.txt"):
    p = os.path.join(R.ROOT, "data", f)
    if os.path.exists(p):
        eng.append(open(p, encoding="utf-8", errors="ignore").read())

zs = {k: [] for k in ("emirp", "s+1_prime", "prime")}
for _ in range(120):
    t = eng[rng.integers(0, len(eng))]
    i = int(rng.integers(0, max(1, len(t) - 4000)))
    ws = [np.asarray(w, dtype=np.int64) for w in R.eng_words_to_runes(t[i:i + 4000])][:270]
    if len(ws) < 200:
        continue
    ln = np.array([len(w) for w in ws])
    st_ = np.concatenate(ws)
    ct_ = np.r_[0, np.cumsum(ln)[:-1]]
    s0 = np.add.reduceat(R.PRIME[st_], ct_)
    r0 = stats(s0)
    nn = {k: [] for k in zs}
    for _ in range(300):
        s2 = np.add.reduceat(R.PRIME[rng.permutation(st_)], ct_)
        s2s = stats(s2)
        for k in zs:
            nn[k].append(s2s[k])
    for k in zs:
        a = np.array(nn[k])
        zs[k].append(float((r0[k] - a.mean()) / (a.std() + 1e-12)))

OUT["T6b_english_control"] = {
    k: dict(n=len(v), mean_z=round(float(np.mean(v)), 3),
            sd_z=round(float(np.std(v)), 3),
            frac_z_ge_3_27=round(float(np.mean(np.array(v) >= 3.265)), 3))
    for k, v in zs.items() if v}
json.dump(OUT, open(os.path.join(HERE, "t6_results.json"), "w"), indent=1)
print("\nT6b ordinary-English control (same statistic, same null, n=270 words):")
for k, v in OUT["T6b_english_control"].items():
    print(f"  {k:12s} mean z={v['mean_z']:+6.3f} sd={v['sd_z']:.3f}  "
          f"P(z >= LP-solved's 3.27) = {v['frac_z_ge_3_27']:.3f}")
