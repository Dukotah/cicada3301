"""R44/W2-A4 library — ciphertext-feedback lag-k decode with per-page additive offsets
drawn from presentation channels (PREREG.md section 3; everything here is pre-registered).

Pure python3 + numpy, no network.  Prior art (decode side): the 2026-07 auditor-loop gate
analysis/campaign18_skip/ctfeedback_coeffs.py; this glue is built fresh (own-glue rule).
"""
import bisect
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round19/I2", "analysis/round34/I1-v3-null",
          "analysis/round44/P3-punct-channels"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp            # noqa: E402
import extract_channels as EC            # noqa: E402  (P3's committed parse glue of record)

N = 29
SECTIONS = [0, 3, 6, 7, 8, 15, 23, 27, 33, 39, 40, 53, 54]   # red-head map (P1/R1)
SIGNS = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]             # (sigma1, sigma2)
KS = (1, 2)
SCOPES = ("page", "continuous")
CHANNELS = ("r", "s3", "s4", "page", "sec")
FS = ("identity", "prime_index", "cumulative")               # mod29 == identity (deduped)
F_NAMED = ("identity", "mod29", "prime_index", "cumulative")
SIG3S = (+1, -1)
SHIFTS = list(range(29))
N_BAR = 50_000
BARS = {120: 13.7082, 240: 18.3740, 729: 22.6951}            # bars_v3 'free' @ N_BAR (PREREG)
FREE_LS = (120, 240, 400, 729)


def l_cap(L):
    return max([x for x in FREE_LS if x <= L] or [120])


def bar_for(L):
    return BARS[l_cap(L)]


# ------------------------------------------------------------------ canon + channels
def load_corpus():
    """The 55 unsolved pages + per-page presentation channels, with the PREREG asserts."""
    ch1 = json.load(open(os.path.join(LP, "analysis", "round44", "P1-red-ink", "channel.json")))
    starts, lens = ch1["page_starts"], ch1["page_lens"]
    kris = gp.runes_to_indices(open(os.path.join(LP, "data", "krisyotam_runes.txt"),
                                    encoding="utf-8").read())
    rel_text = "".join(open(os.path.join(LP, "data", "relikd", n + ".txt"),
                            encoding="utf-8").read() for n in EC.RELIKD_ORDER)
    parsed = EC.parse_witness(rel_text)
    n_unsolved = sum(lens[:55])
    assert len(parsed["runes"]) == 12_956 == n_unsolved
    assert kris[:12_956] == parsed["runes"], "relikd stream != canon prefix"

    pages = [np.asarray(kris[starts[p]:starts[p] + lens[p]], dtype=np.int64) for p in range(55)]

    # per-page separator counts via P3's own glue, bucketed by P1 page_starts
    s3 = [0] * 55
    s4 = [0] * 55
    bounds = [starts[i] for i in range(55)]
    tail3 = tail4 = 0
    for off, c in parsed["toks"]:
        if not (c in EC.SEPS3 or c == EC.WORD):
            continue
        pi = bisect.bisect_right(bounds, off) - 1
        in_tail = off >= starts[54] + lens[54]
        if in_tail:
            tail4 += 1
            if c in EC.SEPS3:
                tail3 += 1
            continue
        s4[pi] += 1
        if c in EC.SEPS3:
            s3[pi] += 1
    ch3 = json.load(open(os.path.join(LP, "analysis", "round44",
                                      "P3-punct-channels", "channels.json")))["channels"]
    assert sum(s3) + tail3 == sum(ch3["sep3_counts"].values()), "s3 totals mismatch"
    assert sum(s4) + tail4 == ch3["sep4_len"], "s4 totals mismatch"

    r = [int(ch1["per_page"][str(p)]["r_p"]) for p in range(55)]
    assert r[0] == 13 and r[3] == 19, "r_p spot-check failed"
    sec = [max(i for i, st in enumerate(SECTIONS) if st <= p) for p in range(55)]
    chans = {"r": r, "s3": s3, "s4": s4, "page": list(range(55)), "sec": sec}
    return {"pages": pages, "starts": starts[:55], "lens": lens[:55], "chans": chans}


def _sieve(count):
    primes, cand = [], 2
    while len(primes) < count:
        if all(cand % p for p in primes if p * p <= cand):
            primes.append(cand)
        cand += 1
    return primes


_PR = _sieve(4000)


def f_apply(fname, vals):
    """Per-page offsets f(ch)_p mod 29 (PREREG f-set)."""
    v = np.asarray(vals, dtype=np.int64)
    if fname in ("identity", "mod29"):
        return v % N
    if fname == "prime_index":
        return np.asarray([_PR[int(x)] for x in v], dtype=np.int64) % N
    if fname == "cumulative":
        return np.cumsum(v) % N
    raise ValueError(fname)


def offsets_for(theta, chans):
    """o_p vector (55,) for theta = dict(ch, f, sig3, s)."""
    fv = f_apply(theta["f"], chans[theta["ch"]])
    return (theta["sig3"] * fv + theta["s"]) % N


# ------------------------------------------------------------------ decode / encipher
def feedback_vec(pages, pi, k, scope):
    """fb (Lp,) for page pi: c_{i-k} within the scope stream, 0 where unavailable."""
    c = pages[pi]
    fb = np.zeros(len(c), dtype=np.int64)
    fb[k:] = c[:-k]
    if scope == "continuous" and pi > 0:
        prev = pages[pi - 1]
        take = min(k, len(prev))
        fb[:take] = prev[len(prev) - k:len(prev) - k + take]
    return fb


def decode_page(pages, pi, s1, s2, k, scope, o):
    c = pages[pi]
    fb = feedback_vec(pages, pi, k, scope)
    return (s1 * c + s2 * fb + o) % N


def decode_page_grid(pages, pi, s1, s2, k, scope):
    """(29, Lp): all offsets 0..28 for one (s1,s2,k,scope) on page pi."""
    c = pages[pi]
    fb = feedback_vec(pages, pi, k, scope)
    base = (s1 * c + s2 * fb) % N
    return (base[None, :] + np.arange(N, dtype=np.int64)[:, None]) % N


def encipher_page(pt, prev_tail, s1, s2, k, scope, o):
    """Encipher plaintext indices pt (list) so decode_page inverts it.
    prev_tail = the last k ciphertext runes of the previous page (continuous scope), or None.
    c_i = s1 * (p_i - s2*fb - o) mod 29   (s1 in {+1,-1} is its own inverse mod 29)."""
    out = []
    for t, p in enumerate(pt):
        if t >= k:
            fb = out[t - k]
        elif scope == "continuous" and prev_tail is not None:
            fb = prev_tail[t - k]          # t-k in {-k..-1} indexes the tail
        else:
            fb = 0
        out.append((s1 * (int(p) - s2 * int(fb) - o)) % N)
    return out


# ------------------------------------------------------------------ enumerations
def tierA_variants():
    """The 16 (s1,s2,k,scope) blocks; x29 offsets x55 pages = 25,520 cells."""
    return [(s1, s2, k, sc) for (s1, s2) in SIGNS for k in KS for sc in SCOPES]


def tierB_thetas():
    """All 13,920 nominal constructions (3 effective f; mod29 deduped into identity)."""
    out = []
    for (s1, s2) in SIGNS:
        for k in KS:
            for sc in SCOPES:
                for ch in CHANNELS:
                    for f in FS:
                        for sig3 in SIG3S:
                            for s in SHIFTS:
                                out.append(dict(s1=s1, s2=s2, k=k, scope=sc, ch=ch, f=f,
                                                sig3=sig3, s=s))
    assert len(out) == 13_920
    return out


def collapse_lemma_check(chans):
    """PREREG Q5: for a fixed page, {(sig3*f(ch_p)+s) % 29 : s in 0..28} == Z_29 for every
    (ch, f, sig3). True by arithmetic; asserted anyway."""
    for ch in CHANNELS:
        for f in FS:
            for sig3 in SIG3S:
                fv = f_apply(f, chans[ch])
                for p in (0, 27, 54):
                    got = {int((sig3 * fv[p] + s) % N) for s in range(29)}
                    assert got == set(range(N)), (ch, f, sig3, p)
    return True


def decode_head(pages, lens, s1, s2, k, scope, o_pages, head_pages=3):
    """Tier-B decode of the concatenated head (pages 0..head_pages-1) under theta."""
    out = []
    for pi in range(head_pages):
        out.append(decode_page(pages, pi, s1, s2, k, scope, int(o_pages[pi])))
    return np.concatenate(out)
