"""Campaign XVIII / Armada-2 -- MODEL C2: INTERRUPTER + DOUBLET-SKIP decoder.

Two desync sources the Cicada author is KNOWN to use, never tested together:

  1. INTERRUPTER (from solved LP1 pages).  The rune ᚠ (Gematria index 0, translit
     "F") appears in the ciphertext but does NOT advance the running key -- it is a
     null / interrupter.  On LP1 it decoded as itself and was skipped when reading.

  2. DOUBLET KEY-SKIP (Campaign X/XI/XVIII).  LP2's active plaintext-aware doublet
     suppression: at encipherment, if the emitted rune would double the previous
     emitted rune, the key symbol is advanced (skipped) ~83% of the time and the
     next tried -- desynchronising key from plaintext (~1 skip / 35 runes).

An unsolved page may use BOTH.  Every prior test used rigid 1:1 alignment AND
assumed no interrupter, so the correct key would score as noise on such a page.
This module builds the joint encipher model, a beam decoder that at each position
may (i) treat ᚠ as an interrupter (emit ᚠ, NO key advance) or (ii) decode normally
with 0..max_skip doublet key-skips, and a MANDATORY planted-key validation gate
that a decoder ignoring interrupters must miss.

Run:  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/interrupter_skip.py
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))

from lp import gematria as gp          # noqa
from lp import score as _score         # noqa
from skipdecode import eng_to_idx, idx_to_trans  # noqa  (reuse validated parsing)

N = gp.N
Q = _score.default()
INT = 0                                # ᚠ interrupter index == gp.INTERRUPTER


# ---------------------------------------------------------- encipher model
def encipher_interrupt_skip(P, K, sign=-1, supp=0.83, p_int=0.06, seed=3301):
    """Joint model.  Encipher plaintext indices P under keystream K so the DECODE
    relation is p = (c + sign*k) mod N, with:
      * DOUBLET KEY-SKIP: if the emitted rune would double the previous emitted
        rune, advance (skip) the key with probability `supp` and retry.
      * INTERRUPTER: with probability `p_int`, insert a literal ᚠ into the
        ciphertext WITHOUT advancing the key and WITHOUT consuming a plaintext
        rune (it is a null between real runes).

    Returns (C, meta) where meta['int_pos'] are ciphertext positions that are
    interrupters and meta['skips'] the per-plaintext-rune skip counts.
    """
    rng = random.Random(seed)
    C, skips, int_pos = [], [], []
    j, c_prev = 0, None
    for p in P:
        # optionally emit an interrupter BEFORE this real rune (key frozen)
        if rng.random() < p_int:
            int_pos.append(len(C))
            C.append(INT)
            c_prev = INT
        nsk = 0
        while True:
            c = (p - sign * K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        skips.append(nsk)
        j += 1
        c_prev = c
    return C, {"int_pos": set(int_pos), "skips": skips}


# ---------------------------------------------------------------- scoring
def _quad_delta(tl, add, floor, d):
    """Score of quadgrams newly completed when `add` is appended to `tl`."""
    L1 = len(tl)
    s = tl + add
    tot = 0.0
    for e in range(max(4, L1 + 1), len(s) + 1):
        tot += d.get(s[e - 4:e], floor)
    return tot


# ------------------------------------------------------- beam (both rules)
def beam_decode_int(C, K, sign=-1, o=0, beam_w=400, max_skip=3,
                    allow_interrupt=True):
    """Skip-tolerant beam decode that ALSO models ᚠ interrupters.

    State per hypothesis: (cumscore, key_ptr, translit, plain_idx, c_prev).
    At each ciphertext rune:
      * if rune == ᚠ and allow_interrupt: branch A treats it as an interrupter
        -- key pointer UNCHANGED, plaintext index unchanged, c_prev := ᚠ, no score
        contribution (the ᚠ is dropped from the recovered plaintext).
      * branch B (always available): decode normally with 0..max_skip key-skips,
        validity-checked (each skipped key must have produced the doubled c_prev),
        key pointer advances, plaintext rune emitted.

    Returns dict(score, plain_idx, translit, ptr_end, n_int).
    """
    d, floor = Q.d, Q.floor
    need = o + (len(C) + 1) * (max_skip + 1) + 8
    Kx = K + [0] * max(0, need - len(K)) if need >= len(K) else K

    # seed hypothesis(es) from position 0
    beams = []
    if allow_interrupt and C[0] == INT:
        # leading ᚠ as pure interrupter (nothing emitted yet)
        beams.append((0.0, o, "", [], INT, 1))
    p0 = (C[0] + sign * Kx[o]) % N
    beams.append((0.0, o + 1, gp.IDX_TO_TRANS[p0], [p0], C[0], 0))

    for i in range(1, len(C)):
        ci = C[i]
        nxt = []
        for (sc, kp, tl, pidx, cprev, nint) in beams:
            # branch A: interrupter (only when the ciphertext rune is ᚠ)
            if allow_interrupt and ci == INT:
                nxt.append((sc, kp, tl, pidx, INT, nint + 1))
            # branch B: normal decode with 0..max_skip key-skips
            for dsk in range(0, max_skip + 1):
                acc = kp + dsk                    # key index used for THIS rune
                if acc >= len(Kx):
                    break
                p = (ci + sign * Kx[acc]) % N
                ok = True
                for m in range(kp, acc):          # each skipped key -> doublet
                    if (p - sign * Kx[m]) % N != cprev:
                        ok = False
                        break
                if not ok:
                    continue
                add = gp.IDX_TO_TRANS[p]
                nsc = sc + _quad_delta(tl, add, floor, d)
                nxt.append((nsc, acc + 1, tl + add, pidx + [p], ci, nint))
        if not nxt:
            break
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]

    best = max(beams, key=lambda x: x[0])
    tl = best[2]
    return {"score": Q.score_norm(tl) if tl else 0.0, "beam_score": best[0],
            "plain_idx": best[3], "translit": tl, "ptr_end": best[1],
            "n_int": best[5]}


def rigid_decode(C, K, sign=-1, o=0):
    """Classic 1:1 running-key decode -- no skips, no interrupter handling."""
    p = [(C[i] + sign * K[o + i]) % N for i in range(len(C))]
    tl = idx_to_trans(p)
    return {"score": Q.score_norm(tl), "plain_idx": p, "translit": tl}


# ------------------------------------------------------------------ gate
def gate():
    print("=" * 74)
    print("GATE -- interrupter+skip beam must recover a key that (a) rigid and")
    print("        (b) a skip-only decoder ignoring interrupters both MISS.")
    print("=" * 74)

    plain_en = (
        "THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
        "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
        "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
        "SACRED GEOMETRY OF THE CIRCUMFERENCE AND LOSE THE SELF TO GAIN THE WHOLE")
    P = eng_to_idx(plain_en)
    K = eng_to_idx(open(os.path.join(ROOT, "data", "keys", "self_reliance.txt"),
                        encoding="utf-8", errors="ignore").read())
    sign, o_true, supp, p_int = -1, 500, 0.83, 0.08

    C, meta = encipher_interrupt_skip(P, K[o_true:], sign=sign, supp=supp,
                                      p_int=p_int)
    n_int = len(meta["int_pos"])
    tot_skip = sum(meta["skips"])
    print(f"\nplaintext runes    : {len(P)}")
    print(f"ciphertext runes   : {len(C)}  (+{n_int} interrupters, {tot_skip} key-skips)")
    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
    print(f"ct doublet rate    : {dbl*100:.2f}%  (target <1%, random 3.45%)")
    print(f"ct ᚠ-rate          : {sum(1 for c in C if c==INT)/len(C)*100:.2f}%")

    truth = idx_to_trans(P)
    print(f"\nTRUTH : {truth[:78]}")

    rd = rigid_decode(C, K, sign=sign, o=o_true)
    mr = sum(a == b for a, b in zip(rd["plain_idx"], P)) / len(P)
    print(f"\n[RIGID    correct key]  score={rd['score']:.3f}  match={mr*100:.1f}%")
    print(f"  {rd['translit'][:78]}")

    def _strmatch(a, b):
        L = min(len(a), len(b))
        return (sum(x == y for x, y in zip(a, b)) / L) if L else 0.0

    bs = beam_decode_int(C, K, sign=sign, o=o_true, beam_w=600, max_skip=3,
                         allow_interrupt=False)
    ms = _strmatch(bs["translit"], truth)
    print(f"\n[SKIP-ONLY (no interrupter)  correct key]  score={bs['score']:.3f}  match={ms*100:.1f}%")
    print(f"  {bs['translit'][:78]}")

    bi = beam_decode_int(C, K, sign=sign, o=o_true, beam_w=600, max_skip=3,
                         allow_interrupt=True)
    # String-level recovery: the recovered plaintext is a translit STRING; an
    # index-by-index compare against P breaks the instant the beam's ᚠ-drop count
    # differs from truth. Compare translit strings (char match over min length).
    mi = _strmatch(bi["translit"], truth)
    print(f"\n[INT+SKIP  correct key]  score={bi['score']:.3f}  match={mi*100:.1f}%  (dropped {bi['n_int']} ᚠ)")
    print(f"  {bi['translit'][:78]}")

    # negative control: wrong key must stay noise even with both rules on
    WK = eng_to_idx(open(os.path.join(ROOT, "data", "keys", "mabinogion.txt"),
                         encoding="utf-8", errors="ignore").read())
    wb = beam_decode_int(C, WK, sign=sign, o=1234, beam_w=600, max_skip=3,
                         allow_interrupt=True)
    print(f"\n[INT+SKIP  WRONG key (control)]  score={wb['score']:.3f}")
    print(f"  {wb['translit'][:78]}")

    print("\n" + "-" * 74)
    # Gate: interrupter-aware beam recovers truth; skip-only (no interrupter)
    # is DEGRADED by the ᚠ desync; rigid is noise; wrong key is noise.
    ok = (mi > 0.95 and bi["score"] > -5.0
          and ms < mi - 0.10                     # interrupter handling matters
          and mr < 0.90 and rd["score"] < -5.5
          and wb["score"] < -6.0)
    print("scale: English ~ -4.0 | threshold -5.2 | noise ~ -7.5 (Campaign XI)")
    print("GATE RESULT:", "PASS" if ok else "FAIL", "-- int+skip recovers; "
          "interrupter-blind decoders miss")
    return ok


# ----------------------------------------------------------------- smoke
def smoke():
    print("\n" + "=" * 74)
    print("SMOKE -- referenced texts over 3 unsolved pages (best of sign +/-)")
    print("=" * 74)
    from run_stats import load_pages
    pages = load_pages()[:-2]                    # 55 unsolved
    keys = ["mabinogion", "self_reliance", "king_in_yellow", "agrippa",
            "book_of_the_law"]
    Ks = {}
    for nm in keys:
        fp = os.path.join(ROOT, "data", "keys", nm + ".txt")
        if os.path.exists(fp):
            Ks[nm] = eng_to_idx(open(fp, encoding="utf-8", errors="ignore").read())
    best = None
    for pi in (0, 1, 2):
        C = pages[pi][:120]                      # cap length -- smoke only
        for nm, K in Ks.items():
            for sign in (-1, 1):
                r = beam_decode_int(C, K, sign=sign, o=0, beam_w=200,
                                    max_skip=2, allow_interrupt=True)
                tag = (r["score"], pi, nm, sign, r["translit"][:46], r["n_int"])
                if best is None or r["score"] > best[0]:
                    best = tag
        print(f"  page {pi}: len {len(C)}")
    print(f"\nBEST smoke: score={best[0]:.3f} page={best[1]} key={best[2]} "
          f"sign={best[3]} nint={best[5]}\n  {best[4]}")
    print("(smoke offset=0 only; full offset/key sweep left to orchestrator)")
    return best


if __name__ == "__main__":
    passed = gate()
    smoke()
    print("\nDONE. gate_passed =", passed)
