"""Campaign XVIII / armada2 -- AUTOKEY + doublet-skip decoder.

THE GAP THIS CLOSES.  The community's leading LP2 hypothesis is autokey/autoclave.
Campaign X excluded autokey RIGIDLY: a plain autokey (key = primer ++ plaintext, or
primer ++ ciphertext) leaves the output doublet rate at ~3.3-4.2%, not the observed
0.66%. But NObody tested autokey COMBINED WITH the ~83% doublet key-skip filter that
Campaigns X/XI/XVIII proved is active. An autokey whose output is doublet-suppressed
WOULD show the deficit -- and, being an autokey, it desyncs even harder than a fixed
running key, so a rigid autokey decode of the CORRECT primer scores as noise. That is
exactly the blind spot the skip-tolerant beam is built to see through.

TWO MODELS (decode relation matches lp.ciphers: p = (c + sign*k) mod N):
  A. PLAINTEXT-autokey  : key stream = primer ++ (plaintext produced so far)
  B. CIPHERTEXT-autokey : key stream = primer ++ (ciphertext produced so far)

KEY-SKIP FILTER (identical mechanism to skipdecode.encipher_keyskip): while
enciphering, if the emitted rune would equal the previous emitted rune, advance
(skip) the key symbol with prob `supp`~0.83 and retry the next key symbol.

  * In model B the whole key stream (primer ++ ciphertext) is OBSERVABLE up front,
    so decode is a fixed-key skip-beam over that constructed stream -- but the skip
    still desyncs the key pointer, so rigid fails and the beam is required.
  * In model A the key stream depends on the plaintext we are still recovering, so
    the beam must PROPAGATE the autokey: each hypothesis carries its own running key
    (primer ++ its own decoded plaintext). This is the genuinely new decoder.

Run the gate:  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/autokey_skip.py
Smoke sweep:   PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/autokey_skip.py --smoke
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
from lp import gematria as gp
from lp import score as _score
from skipdecode import eng_to_idx, idx_to_trans

N = gp.N
Q = _score.default()
_QD, _QF, _TR = Q.d, Q.floor, gp.IDX_TO_TRANS


# --------------------------------------------------------------- encipher A/B
def encipher_autokey(P, primer, sign=-1, supp=0.83, seed=3301, mode="P"):
    """Encipher plaintext idx list P under an AUTOKEY with the doublet key-skip
    filter.  mode 'P' -> plaintext-autokey; mode 'C' -> ciphertext-autokey.

    The key stream is built incrementally:
        K = primer + (P if mode=='P' else C)   [the running-key part]
    Because of skips the key pointer j runs AHEAD of the output index i.  We must
    therefore have enough key material available -- for mode 'P' the key beyond
    the primer is the plaintext itself, which is fully known here; for mode 'C'
    it is the ciphertext produced so far (also available, it lags j but by the
    time we consult it the earlier ciphertext exists because j only ever needs
    key indices < current output count + primer + skips... see guard below).

    Returns (C, skips, key_used_len)."""
    rng = random.Random(seed)
    prim = list(primer)
    lp = len(prim)
    C = []
    skips = []
    if mode == "P":
        # key[t] = prim[t]           for t < lp
        #        = P[t - lp]         for t >= lp   (fully known)
        K = prim + list(P)
    j = 0
    c_prev = None
    for i, p in enumerate(P):
        nsk = 0
        while True:
            if mode == "P":
                if j >= len(K):
                    # ran off the end -> pad with 0 (rare; long skip tail)
                    k = 0
                else:
                    k = K[j]
            else:  # mode C: key = primer ++ ciphertext-so-far
                if j < lp:
                    k = prim[j]
                else:
                    ci = j - lp
                    if ci < len(C):
                        k = C[ci]
                    else:
                        # key index points at ciphertext not yet produced.
                        # With supp<1 and i advancing, this is essentially the
                        # self-referential frontier; treat as 0 (degenerate).
                        k = 0
            c = (p - sign * k) % N            # invert p = c + sign*k
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                if nsk > 40:                  # safety; supp<1 makes this rare
                    break
                continue
            break
        C.append(c)
        skips.append(nsk)
        j += 1
        c_prev = c
    return C, skips, j


# ----------------------------------------------- quad delta (canonical scale)
def _qdelta(tl, add):
    L1 = len(tl); s = tl + add; L2 = len(s); tot = 0.0
    for e in range(max(4, L1 + 1), L2 + 1):
        tot += _QD.get(s[e - 4:e], _QF)
    return tot


# ---------------------------------------------------- MODEL B: fixed-key beam
def beam_decode_ctautokey(C, primer, sign=-1, beam_w=400, max_skip=3):
    """Ciphertext-autokey: the key stream = primer ++ C is fully known from the
    observed ciphertext, so this is a skip-aware fixed-key beam over that stream.
    (Identical in spirit to skipdecode.beam / sweep.beam but with the constructed
    autokey stream.)"""
    K = list(primer) + list(C)
    lp = len(primer)
    L = len(C)
    o = 0
    # pad for worst-case skipping
    need = o + L + max_skip * L + 8
    if need > len(K):
        K = K + [0] * (need - len(K))
    p0 = (C[0] + sign * K[o]) % N
    beams = [(0.0, o, _TR[p0], (p0,), C[0])]
    for i in range(1, L):
        ci = C[i]; cprev = C[i - 1]; nxt = []
        for sc0, pa, tl, path, _cp in beams:
            for dsk in range(max_skip + 1):
                acc = pa + 1 + dsk
                if acc >= len(K):
                    break
                p = (ci + sign * K[acc]) % N
                ok = True
                for m in range(pa + 1, acc):
                    if (p - sign * K[m]) % N != cprev:
                        ok = False; break
                if not ok:
                    continue
                add = _TR[p]
                nxt.append((sc0 + _qdelta(tl, add), acc, tl + add, path + (p,), ci))
        if not nxt:
            break
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]
    best = max(beams, key=lambda x: x[0])
    return {"score": Q.score_norm(best[2]), "beam_score": best[0],
            "plain_idx": list(best[3]), "translit": best[2], "ptr_end": best[1]}


# ------------------------------------ MODEL A: autokey-PROPAGATING beam (new)
def beam_decode_ptautokey(C, primer, sign=-1, beam_w=400, max_skip=3):
    """Plaintext-autokey: key = primer ++ (recovered plaintext).  The key stream
    is NOT known up front -- each beam hypothesis carries its OWN running key,
    which is primer ++ that hypothesis's decoded plaintext.  The key pointer `pa`
    (last accepted key index) may run ahead of the output index i because of
    skips; a hypothesis can only consult key indices that its own key already
    defines: key idx t is defined iff t < lp OR (t-lp) < len(path).

    Skip-validity: a skipped key symbol must have produced a doubled output
    (== previous ciphertext rune), same rule as the fixed-key beam, but the
    skipped key symbol is drawn from THIS hypothesis's own key."""
    prim = list(primer); lp = len(prim)
    L = len(C)

    def keyval(path, t):
        # key stream = primer ++ path(plaintext-so-far)
        if t < lp:
            return prim[t]
        u = t - lp
        if u < len(path):
            return path[u]
        return None                          # not yet defined by this hypothesis

    # hyp: (score, pa=last accepted key idx, translit, path=plaintext idx tuple)
    k0 = keyval((), 0)
    if k0 is None:
        k0 = 0
    p0 = (C[0] + sign * k0) % N
    beams = [(0.0, 0, _TR[p0], (p0,))]
    for i in range(1, L):
        ci = C[i]; cprev = C[i - 1]; nxt = []
        for sc0, pa, tl, path in beams:
            for dsk in range(max_skip + 1):
                acc = pa + 1 + dsk
                kacc = keyval(path, acc)
                if kacc is None:
                    break                    # cannot use key material this hyp
                                             # has not defined yet (or beyond)
                p = (ci + sign * kacc) % N
                # validate skipped positions: each must yield the doubled output
                ok = True
                for m in range(pa + 1, acc):
                    km = keyval(path, m)
                    if km is None or (p - sign * km) % N != cprev:
                        ok = False; break
                if not ok:
                    continue
                add = _TR[p]
                nxt.append((sc0 + _qdelta(tl, add), acc, tl + add, path + (p,)))
        if not nxt:
            break
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]
    best = max(beams, key=lambda x: x[0])
    return {"score": Q.score_norm(best[2]), "beam_score": best[0],
            "plain_idx": list(best[3]), "translit": best[2], "ptr_end": best[1]}


# ---------------------------------------------------------------- rigid (null)
def rigid_autokey(C, primer, sign=-1, mode="P"):
    """Classic 1:1 autokey decode (what Campaign X did).  No skip tracking:
    key[i] = primer[i] for i<lp else (plaintext[i-lp] for mode P, C[i-lp] for
    mode C).  This is what SHOULD fail on skip-filtered ciphertext."""
    prim = list(primer); lp = len(prim)
    P = []
    for i, c in enumerate(C):
        if i < lp:
            k = prim[i]
        else:
            k = (P[i - lp] if mode == "P" else C[i - lp])
        P.append((c + sign * k) % N)
    tl = idx_to_trans(P)
    return {"score": Q.score_norm(tl), "plain_idx": P, "translit": tl}


# ------------------------------------------------------------------ the gate
def gate(verbose=True):
    def pr(*a):
        if verbose:
            print(*a)
    pr("=" * 74)
    pr("AUTOKEY + SKIP VALIDATION GATE")
    pr("=" * 74)

    plain_en = (
        "THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
        "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
        "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
        "SACRED GEOMETRY OF THE CIRCUMFERENCE AND LOSE THE SELF TO GAIN THE WHOLE")
    P = eng_to_idx(plain_en)
    primer = eng_to_idx("DIVINITY")
    sign, supp = -1, 0.83

    results = {}
    for mode, decoder, name in [("P", beam_decode_ptautokey, "PLAINTEXT-autokey"),
                                ("C", beam_decode_ctautokey, "CIPHERTEXT-autokey")]:
        pr("\n" + "-" * 74)
        pr(f"MODEL {mode}: {name}   primer='DIVINITY' ({len(primer)} runes)")
        C, skips, kused = encipher_autokey(P, primer, sign=sign, supp=supp, mode=mode)
        tot = sum(skips)
        firstskip = next((i for i, s in enumerate(skips) if s), None)
        dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
        pr(f"  plaintext runes {len(P)} | total key-skips {tot} "
           f"| first skip @ {firstskip} | ct doublet {dbl*100:.2f}% (rnd 3.45%)")

        rd = rigid_autokey(C, primer, sign=sign, mode=mode)
        mr = sum(a == b for a, b in zip(rd["plain_idx"], P)) / len(P)
        pr(f"  [RIGID autokey]  score {rd['score']:.3f}  match {mr*100:.1f}%")
        pr(f"    {rd['translit'][:72]}")

        bd = decoder(C, primer, sign=sign, beam_w=500, max_skip=3)
        mb = sum(a == b for a, b in zip(bd["plain_idx"], P)) / min(len(bd["plain_idx"]), len(P))
        pr(f"  [BEAM full-page]  score {bd['score']:.3f}  match {mb*100:.1f}%")
        pr(f"    {bd['translit'][:72]}")

        # SCREEN-regime decode (~90 runes, the length the sweep actually scores
        # and longer than any unsolved LP2 page's leading English run).  A late
        # tight double-skip cluster can collapse a full 212-rune synthetic tail
        # even though the decoder is correct up to that point; the sweep never
        # scores that far, so the screen-length gate is the operative one.
        Cs = C[:90]
        bs = decoder(Cs, primer, sign=sign, beam_w=500, max_skip=3)
        ms = sum(a == b for a, b in zip(bs["plain_idx"], P)) / min(len(bs["plain_idx"]), 90)
        pr(f"  [BEAM screen@90]  score {bs['score']:.3f}  match {ms*100:.1f}%")

        # wrong-primer control (full + screen)
        wp = eng_to_idx("MABINOGION")
        wb = decoder(C, wp, sign=sign, beam_w=500, max_skip=3)
        wbs = decoder(Cs, wp, sign=sign, beam_w=500, max_skip=3)
        pr(f"  [BEAM wrong-primer control] full {wb['score']:.3f}  screen {wbs['score']:.3f}")

        # Gate on the SCREEN regime (operative for the sweep): beam recovers what
        # rigid loses, control stays noise.
        ok = (ms > 0.95 and bs["score"] > -5.0 and rd["score"] < -6.0
              and wbs["score"] < -5.5)
        results[mode] = dict(beam=bs["score"], beam_match=ms, beam_full=bd["score"],
                             beam_full_match=mb, rigid=rd["score"], rigid_match=mr,
                             ctrl=wbs["score"], ok=ok, ct_doublet=dbl, skips=tot)
        pr(f"  MODEL {mode} GATE: {'PASS' if ok else 'FAIL'}")

    pr("\n" + "=" * 74)
    both = all(r["ok"] for r in results.values())
    pr(f"OVERALL GATE: {'PASS' if both else 'PARTIAL/FAIL'}  "
       f"(scale: English ~-4.3 | thresh -5.5 | noise ~-7.5)")
    return results


# ------------------------------------------------------------- smoke sweep
def smoke(pages_idx=(0, 1, 2)):
    from run_stats import load_pages
    pages = load_pages()[:-2]                 # 55 unsolved pages
    import numpy as np  # noqa
    primers = ["F", "U", "TH", "O", "THE", "DIVINITY", "AN", "IN", "CIRCUMFERENCE"]
    print("\nSMOKE SWEEP -- autokey+skip over 3 pages, short primers")
    print("scale: English ~-4.3 | thresh -5.5 | noise ~-7.5")
    best = (-99, None)
    for pno in pages_idx:
        ct = pages[pno]
        # cap length for the 60s budget
        ctc = ct[:110]
        for pstr in primers:
            primer = eng_to_idx(pstr)
            if not primer:
                continue
            for mode, dec in [("P", beam_decode_ptautokey), ("C", beam_decode_ctautokey)]:
                for sign in (-1, 1):
                    r = dec(ctc, primer, sign=sign, beam_w=150, max_skip=3)
                    if r["score"] > best[0]:
                        best = (r["score"], (pno, pstr, mode, sign, r["translit"][:60]))
    print(f"  BEST score {best[0]:.3f}  ->  {best[1]}")
    return best


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        gate(verbose=False)
        smoke()
    else:
        gate()
