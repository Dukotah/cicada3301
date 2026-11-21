"""R44 / W2-C1 shared reads glue — ONE code path for plants, nulls and real reads.

- streams -> 116-map grid -> panel pmax  (reuses W2-A1 shortnull: the standing short-
  stream instrument; this cell builds its own L=56 node through it)
- generator-family keyed decodes over a page's canon runes (solved-page conventions:
  interrupters=True, sign both ways) -> panel pmax
- matched-length POT nulls (PREREG 5 + run.log addendum): alpha=0.01 at N_CAP=1300
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
A1 = os.path.join(LP, "analysis", "round44", "W2-A1-short-null")
for p in (os.path.join(LP, "src"), A1,
          os.path.join(LP, "analysis", "round19", "I2")):
    if p not in sys.path:
        sys.path.insert(0, p)

import shortnull as SN              # noqa: E402  (A1 grid + POT machinery)
import adjudicate as A              # noqa: E402
from lp import gematria as gp       # noqa: E402
from lp import ciphers as ci        # noqa: E402

N = 29
N_CAP = 1300
ALPHA = 0.01
SEED = 3301

# ---- canon pages (image -> canon segment; mapping verified in run.log) ----
_txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
_segs = _txt.split("%")
IMG2SEG = {p: p for p in range(50)}
IMG2SEG.update({51: 50, 52: 51, 53: 52, 54: 53, 55: 54})   # p50 has no runes


def page_text(img):
    """Raw canon segment text (runes + separators) for a relikd image index."""
    return _segs[IMG2SEG[img]] if img in IMG2SEG else None


def page_len(img):
    t = page_text(img)
    return None if t is None else sum(1 for c in t if c in gp.RUNE_TO_IDX)


def panel():
    return SN.panel()


# ---- generator family (PREREG 5c): 12 decodes keyed by (k, vec) over one page ----
def family_decodes(runes_text, k, vec):
    """Returns list of (variant_name, plain_idx). k int; vec = 8 ints mod 29."""
    out = []
    const = lambda L: [k % N] * L                         # noqa: E731
    pts = lambda L: ci.prime_totient_stream(L, start=k)   # noqa: E731
    ts = lambda L: ci.totient_stream(L, start=2 + k)      # noqa: E731
    key = [v % N for v in vec] or [0]
    vig = lambda L: ci.repeat_key(key, L)                 # noqa: E731
    for sign in (-1, +1):
        out.append(("shift%+d" % sign,
                    ci.transform_runes(runes_text, const, sign=sign)[1]))
        out.append(("atbash_shift%+d" % sign,
                    ci.transform_runes(runes_text, const, sign=sign, atbash=True)[1]))
        out.append(("prime_totient%+d" % sign,
                    ci.transform_runes(runes_text, pts, sign=sign)[1]))
        out.append(("totient%+d" % sign,
                    ci.transform_runes(runes_text, ts, sign=sign)[1]))
        out.append(("vigenere%+d" % sign,
                    ci.transform_runes(runes_text, vig, sign=sign)[1]))
        out.append(("vigenere_atbash%+d" % sign,
                    ci.transform_runes(runes_text, vig, sign=sign, atbash=True)[1]))
    return out


def family_pmax(runes_text, k, vec, pan):
    """pmax over the panel for each of the 12 keyed decodes (lengths may differ by
    interrupter count -> adjudicate one by one, same code path as nulls)."""
    res = []
    for name, pid in family_decodes(runes_text, k, vec):
        r = A.adjudicate(np.asarray(pid, dtype=np.int64), pan=pan)
        res.append(dict(variant=name, pmax=float(r["pmax"]), preg=str(r["preg"]),
                        ioc=float(r["ioc"]), mds=int(r["mds"])))
    return res


# ---- matched-length POT null for the generator read ----
def generator_null_bar(L, pan, rng, n_surr=500):
    """Null: shuffled contiguous canon windows of length L, rebuilt as rune text,
    run through the SAME family code path with random wrong keys."""
    c = SN.canon()
    pm = []
    for i in range(n_surr):
        a = int(rng.integers(0, len(c) - L))
        w = c[a:a + L].copy()
        rng.shuffle(w)
        text = gp.indices_to_runes(w)
        k = int(rng.integers(1, N))
        vec = [int(x) for x in rng.integers(0, N, size=8)]
        dec = family_decodes(text, k, vec)
        lens = {len(pid) for _, pid in dec}
        assert len(lens) == 1, lens          # interrupter positions shared by variants
        X = np.asarray([pid for _, pid in dec], dtype=np.int64)
        pm.extend(A.adjudicate_batch(X, pan=pan)["pmax"].tolist())
    u, p_u, beta, n_exc = SN.pot_fit(np.asarray(pm))
    bar = SN.pot_bar(u, p_u, beta, Nreal=N_CAP, alpha=ALPHA)
    return dict(L=int(L), n_surrogates=n_surr, n_pmax=len(pm), u=u, p_u=p_u,
                beta=beta, n_exceed=n_exc, bar=float(bar))


# ---- value-stream read (116-map grid) ----
def stream_pmax(values, pan):
    x = np.asarray([v % N for v in values], dtype=np.int64)
    pm, r, X, meta = SN.grid_pmax(x, pan)
    i = int(np.argmax(pm))
    return float(pm[i]), meta[i], pm


def stream_null_bar(values, pan, rng, n_surr=1000):
    """PERM + DRAW families on the observed multiset through the same grid."""
    x = np.asarray([v % N for v in values], dtype=np.int64)
    out = {}
    for fam in ("PERM", "DRAW"):
        pm = np.empty(n_surr * 116)
        for i in range(n_surr):
            s = rng.permutation(x) if fam == "PERM" else rng.choice(x, size=len(x))
            pm[i * 116:(i + 1) * 116] = SN.grid_pmax(s, pan)[0]
        u, p_u, beta, n_exc = SN.pot_fit(pm)
        out[fam] = dict(u=u, p_u=p_u, beta=beta, n_exceed=n_exc,
                        bar=float(SN.pot_bar(u, p_u, beta, Nreal=N_CAP, alpha=ALPHA)))
    out["bar_of_record"] = max(out["PERM"]["bar"], out["DRAW"]["bar"])
    return out
