"""SOLVER BENCHMARK -- the plant.

One API to build a synthetic LP2-like ciphertext whose answer is KNOWN, so a
decoder can be measured instead of merely run.

Everything here is assembled from machinery the project already validated:

  campaign18_skip/skipdecode.py   eng_to_idx, encipher_keyskip, beam/rigid decode
  round12/D1_redteam/rewrite_gate encipher_rewrite (the in-place value-rewrite arm)
  round12/D3/pc_derivedkey.py     SHA-256 counter-mode derived keystream
  round12/C1/feedback.py          k-history feedback / autokey encipher+decode
  round11/lib_numchannel.py       eng_norm, shuffled, null_band
  src/lp/{gematria,ciphers,stats,score,solve}   the rig itself

Nothing about the cipher is re-implemented here; plant.py only *composes* those
pieces and reports whether the composition still looks like the real thing.

THE CONTRACT
------------
A plant is a fair proxy for LP2 only if its ciphertext carries the same surface
statistics as the real unsolved stream:

    doublet rate   0.664 %      (random mod-29 expectation is 3.448 %)
    IoC * N        0.9999
    entropy        4.8565 bits  (log2(29) = 4.8580)

`signature(C)` measures those and `signature_check()` prints the comparison.

USAGE
-----
    from plant import plant
    pl = plant(key="running", keytext="self_reliance.txt", mechanism="skip")
    pl.C          # ciphertext rune indices
    pl.P          # the known plaintext rune indices  (ground truth)
    pl.K          # the keystream that was actually used (for the positive arm)
    pl.truth      # dict describing exactly what was planted
    pl.stats      # doublet / IoC / entropy of pl.C
"""
import hashlib
import os
import random
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
for _p in (os.path.join(ROOT, "src"),
           os.path.join(ROOT, "analysis"),
           os.path.join(ROOT, "analysis", "campaign18_skip"),
           os.path.join(ROOT, "analysis", "round11"),
           os.path.join(ROOT, "analysis", "round12", "C1")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lp import gematria as gp, stats as _stats, score as _score, ciphers  # noqa: E402
import skipdecode as sk                                                   # noqa: E402
import feedback as fb                                                     # noqa: E402

N = gp.N                      # 29
Q = _score.default()
KEYDIR = os.path.join(ROOT, "data", "keys")

# The real LP2 signature (measured on the 12,956-rune unsolved stream; see
# analysis/STATS.md and round11/lib_numchannel.unsolved()).
LP2_SIGNATURE = {"n": 12956, "doublet_rate_pct": 0.664,
                 "ioc_norm": 0.9999, "entropy_bits": 4.8565}

# The project's pinned filter strength (Campaign X/XI). At this strength the
# residual doublet rate is (1 - supp) * 3.448 % = 0.586 %.
PINNED_SUPP = 0.83
# supp that reproduces LP2's 0.664 % exactly, if you want the tightest proxy.
EXACT_SUPP = 1.0 - LP2_SIGNATURE["doublet_rate_pct"] / 3.448   # ~0.8074


# --------------------------------------------------------------- plaintexts
PLAINTEXTS = {
    # canonical Cicada-voice English, ~180 runes
    "primes": ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
               "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
               "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
               "SACRED GEOMETRY OF THE CIRCUMFERENCE AND LOSE THE SELF TO GAIN THE WHOLE"),
    # the real WARNING page plaintext (a genuine LP plaintext, not invented)
    "warning": ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE "
                "TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT "
                "EDIT OR CHANGE THIS BOOK OR THE MESSAGE WITHIN EITHER THE WORDS OR "
                "THEIR NUMBERS FOR ALL IS SACRED"),
    # B-04's plant plaintext, kept verbatim so round13/B04's G2 can be replicated
    "b04": ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
            "ENCRYPTEDKNOWTHISSHADOWSTHEJOURNEYTOWARDTHEENDOFALLTHINGSISNOT"
            "ANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAY"),
}
DEFAULT_PLAINTEXT = "primes"


def eng_to_idx(text):
    """English -> rune indices. Thin re-export of the validated mapping."""
    return sk.eng_to_idx(text)


def idx_to_trans(idxs):
    return sk.idx_to_trans(idxs)


def load_keytext(name):
    return open(os.path.join(KEYDIR, name), encoding="utf-8", errors="ignore").read()


def available_keytexts():
    return sorted(f for f in os.listdir(KEYDIR) if f.endswith(".txt"))


# ------------------------------------------------------------- key families
def ks_running(keytext="self_reliance.txt", offset=0, length=4096, **_):
    """RUNNING KEY: an English book read as rune indices."""
    K = sk.eng_to_idx(load_keytext(keytext))
    return K[offset:offset + length]


def ks_sha256_ctr(seed=b"CICADA3301", length=4096, **_):
    """DERIVED KEYSTREAM: SHA-256 counter mode reduced mod 29 (round12/D3, B-04)."""
    if isinstance(seed, str):
        seed = seed.encode()
    out, ctr = [], 0
    while len(out) < length:
        h = hashlib.sha256(seed + ctr.to_bytes(4, "big")).digest()
        out.extend(b % N for b in h)
        ctr += 1
    return out[:length]


def ks_prng(seed=3301, length=4096, **_):
    """SEEDED PRNG: Mersenne Twister, uniform over 0..28 (Round 8 seed-sweep family)."""
    r = random.Random(seed)
    return [r.randrange(N) for _ in range(length)]


def ks_otp(seed=None, length=4096, **_):
    """TRUE RANDOM PAD: os.urandom-derived, no seed to find. The unrecoverable
    control -- any gate that 'recovers' this one is broken."""
    if seed is None:
        return [b % N for b in os.urandom(length * 2)][:length]
    r = random.SystemRandom() if seed == "sys" else random.Random(seed)
    return [r.randrange(N) for _ in range(length)]


def ks_vigenere(keyword="DIVINITY", length=4096, **_):
    """REPEATING KEYWORD: the solved pages' actual construction."""
    return ciphers.repeat_key(gp.keyword_to_indices(keyword), length)


KEY_FAMILIES = {
    "running": ks_running,
    "sha256_ctr": ks_sha256_ctr,
    "prng": ks_prng,
    "otp": ks_otp,
    "vigenere": ks_vigenere,
}


def make_key(kind, length=4096, **kw):
    if kind not in KEY_FAMILIES:
        raise ValueError(f"unknown key family {kind!r}; have {sorted(KEY_FAMILIES)}")
    return KEY_FAMILIES[kind](length=length, **kw)


# -------------------------------------------------------- filter mechanisms
def encipher_none(P, K, sign=-1, **_):
    """No doublet filter. c_i = (p_i - sign*k_i) mod N, key rigidly synced."""
    C = [(p - sign * K[i]) % N for i, p in enumerate(P)]
    return C, {"n_skips": 0, "n_rewrites": 0}


def encipher_skip(P, K, sign=-1, supp=PINNED_SUPP, seed=3301, **_):
    """KEY-SKIP desync (Campaign XVIII). Validated implementation, imported."""
    C, skips, _used = sk.encipher_keyskip(P, K, sign=sign, supp=supp, seed=seed)
    return C, {"n_skips": int(sum(skips)), "n_rewrites": 0}


def encipher_rewrite(P, K, sign=-1, supp=PINNED_SUPP, seed=3301, **_):
    """VALUE-REWRITE in place (round12/D1_redteam). Key stays synced; a would-be
    doublet is resampled to a different rune, i.e. a substitution ERROR, not a
    desync. Ported verbatim from rewrite_gate.encipher_rewrite."""
    rng = random.Random(seed)
    C, nrw, c_prev = [], 0, None
    for i, p in enumerate(P):
        c = (p - sign * K[i]) % N
        if c_prev is not None and c == c_prev and rng.random() < supp:
            alt = rng.randrange(N - 1)
            if alt >= c_prev:
                alt += 1
            c = alt
            nrw += 1
        C.append(c)
        c_prev = c
    return C, {"n_skips": 0, "n_rewrites": nrw}


MECHANISMS = {"none": encipher_none, "skip": encipher_skip, "rewrite": encipher_rewrite}


# ------------------------------------------------------------------- result
@dataclass
class Plant:
    C: list                       # ciphertext rune indices (what a solver sees)
    P: list                       # ground-truth plaintext rune indices
    K: list                       # keystream actually used (positive-arm key)
    truth: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)
    runes: str = ""               # ciphertext as runes (for solve.decode consumers)

    @property
    def truth_translit(self):
        return idx_to_trans(self.P)

    def recovery(self, plain_idx):
        """Fraction of ground-truth runes a candidate decode got right."""
        if not plain_idx:
            return 0.0
        n = min(len(plain_idx), len(self.P))
        return sum(1 for a, b in zip(plain_idx[:n], self.P[:n]) if a == b) / len(self.P)

    def recovery_text(self, translit):
        n = min(len(translit), len(self.truth_translit))
        if n == 0:
            return 0.0
        return sum(1 for a, b in zip(translit[:n], self.truth_translit[:n])
                   if a == b) / len(self.truth_translit)


# ------------------------------------------------------------------ metrics
def signature(C):
    """The three surface statistics that make a plant a fair LP2 proxy."""
    s = _stats.summary(C)
    return {"n": s["n"], "doublet_rate_pct": s["doublet_rate_pct"],
            "ioc_norm": s["ioc_norm"], "entropy_bits": s["entropy_bits"]}


def signature_delta(C):
    """Signed distance of a plant's signature from the real LP2 stream."""
    g = signature(C)
    return {k: round(g[k] - LP2_SIGNATURE[k], 4)
            for k in ("doublet_rate_pct", "ioc_norm", "entropy_bits")}


# -------------------------------------------------------------- the planter
def plant(plaintext=DEFAULT_PLAINTEXT, key="running", mechanism="skip",
          supp=PINNED_SUPP, length=None, offset=0, sign=-1, atbash=False,
          seed=3301, key_kw=None, repeat_to=None):
    """Build a synthetic LP2-like ciphertext with a KNOWN answer.

    plaintext  key of PLAINTEXTS, or raw English text
    key        one of KEY_FAMILIES ('running','sha256_ctr','prng','otp','vigenere')
    key_kw     dict of family-specific args, e.g. {'keytext': 'agrippa.txt'} or
               {'seed': b'CICADA3301'} or {'keyword': 'DIVINITY'}
    mechanism  'none' | 'skip' (key desync) | 'rewrite' (in-place value rewrite)
    supp       doublet-suppression probability of the filter (0 = off, 0.83 pinned)
    length     truncate the plaintext to this many runes (None = all)
    offset     key offset actually used when enciphering (the solver must find it)
    sign       decode relation p = (c + sign*k) mod N
    atbash     apply Atbash to the ciphertext after enciphering
    repeat_to  repeat the plaintext until it reaches this many runes (for long plants)

    Returns a Plant.
    """
    txt = PLAINTEXTS.get(plaintext, plaintext)
    P = eng_to_idx(txt)
    if repeat_to:
        while len(P) < repeat_to:
            P = P + eng_to_idx(txt)
        P = P[:repeat_to]
    if length:
        P = P[:length]
    if not P:
        raise ValueError("empty plaintext")

    key_kw = dict(key_kw or {})
    need = len(P) * 4 + 256          # worst case skipping
    K_full = make_key(key, length=need + offset, **key_kw)
    K = K_full[offset:]
    if len(K) < len(P) + 8:
        raise ValueError(f"key family {key!r} produced too little material "
                         f"({len(K)} for {len(P)} runes)")

    if mechanism not in MECHANISMS:
        raise ValueError(f"unknown mechanism {mechanism!r}; have {sorted(MECHANISMS)}")
    C, info = MECHANISMS[mechanism](P, K, sign=sign, supp=supp, seed=seed)

    if atbash:
        C = [(N - 1) - c for c in C]

    truth = {"plaintext_key": plaintext if plaintext in PLAINTEXTS else "<custom>",
             "key_family": key, "key_kw": {k: (v.decode() if isinstance(v, bytes) else v)
                                           for k, v in key_kw.items()},
             "mechanism": mechanism, "supp": supp, "offset": offset,
             "sign": sign, "atbash": bool(atbash), "seed": seed,
             "n_runes": len(P), **info}
    pl = Plant(C=C, P=P, K=K_full, truth=truth, stats=signature(C),
               runes=gp.indices_to_translit and "".join(_IDX_TO_RUNE[c] for c in C))
    return pl


_IDX_TO_RUNE = {i: r for r, i in gp.RUNE_TO_IDX.items()}


# ------------------------------------------- feedback / autokey plant (C1)
def plant_feedback(plaintext=DEFAULT_PLAINTEXT, f="sum", k=3, source="ct",
                   sign=-1, seedkeys=(7, 11, 2), length=None):
    """k-history feedback (autokey-class) plant. The key at position i is
    f(last k runes of the chosen source stream) -- there is no keystream to
    guess, only (f, k, source, sign, seed). Uses round12/C1/feedback.py."""
    txt = PLAINTEXTS.get(plaintext, plaintext)
    P = eng_to_idx(txt)
    if length:
        P = P[:length]
    fn = fb.F_BASIS[f]
    sk_ = list(seedkeys)[:k]
    C = fb.encipher(P, fn, k, sk_, source=source, sign=sign)
    truth = {"key_family": "feedback", "f": f, "k": k, "source": source,
             "sign": sign, "seedkeys": sk_, "mechanism": "none",
             "n_runes": len(P)}
    return Plant(C=C, P=P, K=[], truth=truth, stats=signature(C),
                 runes="".join(_IDX_TO_RUNE[c] for c in C))


# --------------------------------- vigenere + interrupters plant (solved pages)
def plant_vigenere_interrupters(plaintext=DEFAULT_PLAINTEXT, keyword="DIVINITY",
                                n_interrupters=6, sign=-1, atbash=False,
                                length=None, seed=3301):
    """The SOLVED pages' actual construction: repeating-keyword Vigenere where a
    subset of the ᚠ runes in the CIPHERTEXT are nulls -- removed on decode and
    NOT advancing the key (see src/lp/solve.py).

    We encipher normally, then splice `n_interrupters` extra ᚠ runes into the
    ciphertext at pseudo-random positions. A decoder that ignores interrupters
    desyncs at the first splice; solve.find_interrupters must find them.
    Returns a Plant whose .runes is the rune string to hand to solve.*.
    """
    txt = PLAINTEXTS.get(plaintext, plaintext)
    P = eng_to_idx(txt)
    if length:
        P = P[:length]
    stream = ciphers.repeat_key(gp.keyword_to_indices(keyword), len(P))
    C = [(p - sign * stream[i]) % N for i, p in enumerate(P)]
    if atbash:
        C = [(N - 1) - c for c in C]
    runes = [_IDX_TO_RUNE[c] for c in C]

    rng = random.Random(seed)
    # splice positions in the final rune stream, spread out, never adjacent
    pos = sorted(rng.sample(range(4, len(runes) - 4), n_interrupters))
    for j, p in enumerate(pos):
        runes.insert(p + j, gp.INTERRUPTER)
    truth = {"key_family": "vigenere_interrupters", "keyword": keyword,
             "n_interrupters": n_interrupters, "sign": sign, "atbash": bool(atbash),
             "mechanism": "interrupter", "n_runes": len(P),
             "splice_positions": [p + j for j, p in enumerate(pos)]}
    Cx = [gp.RUNE_TO_IDX[r] for r in runes]
    return Plant(C=Cx, P=P, K=stream, truth=truth, stats=signature(Cx),
                 runes="".join(runes))


# --------------------------------------------------------------- self-check
def signature_check(n=12956, supp=EXACT_SUPP, verbose=True):
    """Does a plant reproduce the real LP2 surface signature?

    Uses a long repeated-plaintext plant under a SHA-counter keystream (so the
    key itself is flat) with the pinned key-skip filter. Returns (ok, table).
    """
    pl = plant(plaintext="primes", key="sha256_ctr", key_kw={"seed": b"CICADA3301"},
               mechanism="skip", supp=supp, repeat_to=n)
    got, want = pl.stats, LP2_SIGNATURE
    tol = {"doublet_rate_pct": 0.15, "ioc_norm": 0.02, "entropy_bits": 0.01}
    rows, ok = [], True
    for k in ("doublet_rate_pct", "ioc_norm", "entropy_bits"):
        d = abs(got[k] - want[k])
        good = d <= tol[k]
        ok = ok and good
        rows.append((k, want[k], got[k], round(d, 4), tol[k], good))
    if verbose:
        print(f"PLANT SIGNATURE vs REAL LP2   (n={got['n']}, supp={supp:.4f})")
        print(f"  {'statistic':18s} {'LP2':>9s} {'plant':>9s} {'|diff|':>8s} "
              f"{'tol':>7s}  ok")
        for k, w, g, d, t, good in rows:
            print(f"  {k:18s} {w:9.4f} {g:9.4f} {d:8.4f} {t:7.3f}  "
                  f"{'YES' if good else 'NO'}")
        print(f"  -> plant is a {'FAIR' if ok else 'POOR'} proxy for LP2")
    return ok, rows


if __name__ == "__main__":
    signature_check()
    print()
    for mech in ("none", "skip", "rewrite"):
        pl = plant(mechanism=mech)
        print(f"{mech:8s} n={len(pl.C):4d} doublet={pl.stats['doublet_rate_pct']:.3f}% "
              f"iocN={pl.stats['ioc_norm']:.4f} H={pl.stats['entropy_bits']:.4f} "
              f"{pl.truth}")
    for fam, kw in (("running", {"keytext": "self_reliance.txt"}),
                    ("sha256_ctr", {"seed": b"THE PRIMES ARE SACRED"}),
                    ("prng", {"seed": 3301}),
                    ("otp", {}),
                    ("vigenere", {"keyword": "DIVINITY"})):
        pl = plant(key=fam, key_kw=kw, mechanism="skip")
        print(f"{fam:12s} doublet={pl.stats['doublet_rate_pct']:.3f}% "
              f"iocN={pl.stats['ioc_norm']:.4f}")
    pv = plant_vigenere_interrupters()
    print("vig+interrupters:", len(pv.runes), "runes,",
          pv.truth["n_interrupters"], "nulls spliced")
    pf = plant_feedback()
    print("feedback:", pf.truth)
