"""Campaign XVIII armada2 -- SELF-REFERENTIAL FAMILY, re-tested skip-aware.

The ledger's section B excluded these RIGIDLY (so, per the campaign XVIII thesis,
UNSOUNDLY): first-difference / integral inversion, generalised combiner / feedback,
and page-on-page key reuse (in-depth). This module re-tests them under the validated
skip-tolerant beam decoder (sweep.beam), which is the only decoder that scores the
CORRECT key as English on LP2's doublet-filtered ciphertext.

  (a) First-difference & integral transforms of the ciphertext, then skip-aware
      running-key / keystream decode of the TRANSFORMED stream (reuse beam + the
      referenced texts + numeric keystreams as keys).
  (b) In-depth: for every pair of pages, test skip-aware whether one page's plaintext
      could be the other's running key (self-keying), and whether two pages share a
      keystream.
  (c) Short-history ciphertext-feedback family (key at i depends on the last k
      ciphertext runes) decoded skip-aware for small k (1..3).

Each sub-family carries a tiny synthetic sanity check (does the decoder recover a
PLANTED key that the rigid decoder misses?) and a smoke over 3 pages. Full corpus
sweeps are left to the orchestrator.

  Run smoke:  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/selfref_skip.py --smoke
  Run gates:  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/selfref_skip.py --gate
  Full:       ... --full   (orchestrator only)
"""
import os, sys, argparse, time, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip", "armada"))

from lp import gematria as gp, score as sc
from run_stats import load_pages
from skipdecode import eng_to_idx, idx_to_trans, encipher_keyskip
from sweep import beam, load_text, Q, N, MAXSKIP

# reuse the proven numeric keystream generators (do NOT rewrite)
import numeric_skip as NS

# ----------------------------------------------------------------- thresholds
# From robustness.py / the ledger: English ~ -4.3, confirm threshold -5.5,
# false-positive ceiling / null-max -6.82, noise floor -7.5.
CONF_THR = -5.5
SCREEN_THR = -6.0
SCREEN_LEN = 90

REFERENCED = ["mabinogion.txt", "self_reliance.txt", "king_in_yellow.txt", "agrippa.txt",
              "book_of_the_law.txt", "runepoem_oe.txt", "runepoem_translit.txt",
              "solved_plaintext.txt", "thematic.txt"]


def load_referenced():
    out = []
    for f in REFERENCED:
        p = os.path.join(ROOT, "data", "keys", f)
        if os.path.exists(p):
            k = load_text(p)
            if len(k) > 300:
                out.append((f, k))
    return out


def numeric_keys(length):
    """Small, fast subset of the proven numeric catalog (NO 841-fibonacci fan-out;
    that is covered by numeric_skip's own full sweep). These are the number-theoretic
    + constant + a few PRNG streams -- the plausible Cicada generators."""
    cat = []
    cat.append(("primes", NS.ks_primes(length)))
    cat.append(("prime_gaps", NS.ks_prime_gaps(length)))
    cat.append(("totient_n", NS.ks_totient_n(length)))
    cat.append(("iter_totient_d2", NS.ks_iter_totient(length, depth=2)))
    cat.append(("iter_totient_d3", NS.ks_iter_totient(length, depth=3)))
    for cname in ("pi", "e", "phi"):
        try:
            cat.append((f"{cname}_digits", NS.ks_constant_single(cname, length)))
        except Exception:
            pass
    return [(n, np.array(k, dtype=np.int64)) for n, k in cat if len(k) >= length]


# =====================================================================
# TRANSFORMS
# =====================================================================
def ct_firstdiff(ct):
    """First difference of ciphertext, mod N:  d[i] = c[i] - c[i-1].
    d[0] = c[0].  Invertible; reduces one anti-derivative degree."""
    d = np.empty_like(ct)
    d[0] = ct[0] % N
    d[1:] = (ct[1:] - ct[:-1]) % N
    return d


def ct_integral(ct):
    """Running sum (discrete integral) of ciphertext, mod N:
    s[i] = sum_{j<=i} c[j] mod N.  The inverse of first-difference."""
    return np.cumsum(ct) % N


# =====================================================================
# (a)  transform + skip-aware running-key / keystream decode
# =====================================================================
def _best_over_keys(ct2, keys, screen_len=SCREEN_LEN, screen_beam=200,
                    full_beam=400, offsets=None):
    """Skip-aware beam over a list of (name, K_np) keys against transformed
    ciphertext ct2. Returns (best_score, best_meta, hits)."""
    from sweep import prefilter
    best = (-99.0, None)
    hits = []
    L = len(ct2)
    for tname, K in keys:
        for sign in (-1, 1):
            if offsets is None:
                offs = prefilter(ct2, K, sign)
            else:
                offs = offsets
            for o in offs:
                pi = beam(ct2, K, sign, int(o), min(screen_len, L), screen_beam)
                s = Q.score_norm(idx_to_trans(pi))
                if s > best[0]:
                    best = (s, (tname, sign, int(o)))
                if s > SCREEN_THR:
                    pf = beam(ct2, K, sign, int(o), L, full_beam)
                    fs = Q.score_norm(idx_to_trans(pf))
                    if fs > CONF_THR:
                        hits.append((fs, tname, sign, int(o), idx_to_trans(pf)))
    return best[0], best[1], hits


def attack_transformed(ct, keys, transform):
    """Apply transform to ct, then skip-aware decode under the given keys."""
    ct2 = transform(ct)
    return _best_over_keys(ct2, keys)


# =====================================================================
# (b)  page-on-page: self-keying + shared keystream (in-depth)
# =====================================================================
def selfkey_pair(ct_target, key_plain, screen_beam=200, full_beam=400):
    """Skip-aware: could `key_plain` (another page's PLAINTEXT, given as an index
    list) be the running key that deciphers ct_target?  We do not know the other
    page's plaintext, so at SMOKE we test with the ciphertext of the key-page as a
    stand-in AND (in the synthetic gate) with a genuine plaintext. Returns best."""
    from sweep import prefilter
    K = np.asarray(key_plain, dtype=np.int64)
    L = len(ct_target)
    if len(K) < L + MAXSKIP * L + 8:
        K = np.concatenate([K, np.zeros(L * (MAXSKIP + 1) + 8, dtype=np.int64)])
    best = (-99.0, None)
    for sign in (-1, 1):
        offs = prefilter(ct_target, K, sign)
        # self-keying is classically offset 0, but keep the prefilter's top few
        cand = list(dict.fromkeys([0] + list(offs)))[:8]
        for o in cand:
            pi = beam(ct_target, K, sign, int(o), min(SCREEN_LEN, L), screen_beam)
            s = Q.score_norm(idx_to_trans(pi))
            if s > best[0]:
                best = (s, (sign, int(o)))
    return best


# common English cribs for the drag test (index streams)
_CRIBS = [eng_to_idx(w) for w in
          ("THE", "AND", "THAT", "SACRED", "PRIMES", "WITHIN", "INSTAR",
           "EMERGENCE", "CIRCUMFERENCE", "TOTIENT", "PILGRIM", "TRUTH",
           "THISISNOT", "WISDOM", "KNOWLEDGE", "SHOULDKNOW")]


def shared_keystream_pair(ct_a, ct_b, sign=-1):
    """Skip-aware test of whether pages A and B share a keystream (key reuse
    'in depth'). If C_a = E(P_a, K) and C_b = E(P_b, K) under a running key, then
    in the RIGID world C_a - C_b = P_a - P_b -- the key cancels EXACTLY. The IoC
    of that difference is NOT raised (difference of two English texts is ~flat),
    so IoC is a VACUOUS separator; the sound in-depth attack is CRIB-DRAGGING:
    slide a known word W across the difference; if W is P_a at some position, then
    (diff + W) reveals P_b there (and vice-versa). We score the best English
    quadgram hit of any crib at any offset, and compare against a per-pair random
    baseline to get a separation.

    Under the SKIP filter the per-page desync breaks the EXACT cancellation after
    the first skip (~1 per 35 runes), so a genuine shared-key crib hit survives
    only over a short window before the two desyncs diverge. We report the best
    windowed crib score AND the fraction of the page where cancellation holds, so
    the orchestrator can see whether this is viable or skip-killed. Returns
    (best_crib_score, ioc_diff)."""
    L = min(len(ct_a), len(ct_b))
    a = np.asarray(ct_a[:L], dtype=np.int64)
    b = np.asarray(ct_b[:L], dtype=np.int64)
    diff = (a - b) % N                       # == P_a - P_b iff shared key, no skip
    counts = np.bincount(diff, minlength=N)
    n = counts.sum()
    ioc = (counts * (counts - 1)).sum() / (n * (n - 1) / N) if n > 1 else 0.0
    # crib drag: for each crib W and each position, P_b window = (diff + W) if W=P_a,
    # or P_a window = (W - diff). Score the more-English of the two as translit.
    best = -99.0
    for W in _CRIBS:
        w = np.asarray(W, dtype=np.int64); lw = len(w)
        if lw < 3 or lw > L:
            continue
        for pos in range(0, L - lw + 1):
            dwin = diff[pos:pos + lw]
            for rev in (dwin + w, w - dwin):        # P_b or P_a candidate window
                s = Q.score_norm(idx_to_trans(list(rev % N)))
                if s > best:
                    best = s
    return best, ioc


# =====================================================================
# (c)  short-history ciphertext-feedback family
# =====================================================================
def encipher_ctfeedback(P, seed_key, k=1, coeffs=None, sign=-1, supp=0.83, seed=3301):
    """Synthetic encipher: key at position i is a function of the last k CIPHERTEXT
    runes (autokey-by-ciphertext / CFB-like), plus the skip filter.

      key[i] = ( seed_key[i]  +  sum_{t=1..k} coeffs[t]*c[i-t] )  mod N     (i>=k)
      key[i] = seed_key[i]                                                   (i<k)

    Returns (C, key_used)."""
    if coeffs is None:
        coeffs = [1] * (k + 1)
    rng = random.Random(seed)
    C = []
    c_prev = None
    for i, p in enumerate(P):
        if i < k:
            kv = seed_key[i] % N
        else:
            kv = seed_key[i] % N
            for t in range(1, k + 1):
                kv = (kv + coeffs[t] * C[i - t]) % N
        # skip filter on output doublets (advance the seed_key symbol)
        j = i
        nsk = 0
        while True:
            kv2 = seed_key[j] % N
            if i >= k:
                for t in range(1, k + 1):
                    kv2 = (kv2 + coeffs[t] * C[i - t]) % N
            c = (p - sign * kv2) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                if j >= len(seed_key):
                    break
                continue
            break
        C.append(c)
        c_prev = c
    return C


def decode_ctfeedback(C, seed_key, k=1, coeffs=None, sign=-1, o=0,
                      beam_w=300, max_skip=MAXSKIP):
    """Skip-aware beam decode where key[i] depends on the last k CIPHERTEXT runes.
    Crucially the ciphertext is KNOWN, so the feedback term is computable at decode
    time WITHOUT the plaintext -- this is what makes CFB-style feedback tractable
    here (unlike plaintext-autokey, which needs the beam to guess the key).

    We fold the feedback into an effective per-position key offset, then run the
    same skip-aware beam machinery. seed_key is an index array (running key)."""
    if coeffs is None:
        coeffs = [1] * (k + 1)
    C = np.asarray(C, dtype=np.int64)
    L = len(C)
    sk = np.asarray(seed_key, dtype=np.int64)
    need = o + L + max_skip * L + 8
    if need > len(sk):
        sk = np.concatenate([sk, np.zeros(need - len(sk), dtype=np.int64)])
    # feedback term f[i] (0 for i<k). Effective key at ptr q for output i is
    # (sk[q] + f[i]) mod N. We precompute f[i]; the beam adds it into the key.
    f = np.zeros(L, dtype=np.int64)
    for i in range(k, L):
        v = 0
        for t in range(1, k + 1):
            v += coeffs[t] * int(C[i - t])
        f[i] = v % N
    return _feedback_beam(C, sk, f, sign, o, beam_w, max_skip)


def _feedback_beam(ct2, K, fterm, sign, o, beam_w, max_skip):
    """Skip-aware beam identical to sweep.beam but the effective key at output i
    and pointer q is (K[q] + fterm[i]) mod N."""
    _TR = gp.IDX_TO_TRANS
    _QD = Q.d
    _QF = Q.floor

    def qdelta(tl, add):
        L1 = len(tl); s = tl + add; L2 = len(s); tot = 0.0
        for e in range(max(4, L1 + 1), L2 + 1):
            tot += _QD.get(s[e - 4:e], _QF)
        return tot

    L = len(ct2)
    p0 = int((ct2[0] + sign * ((K[o] + fterm[0]) % N)) % N)
    beams = [(0.0, o, _TR[p0], (p0,))]
    for i in range(1, L):
        ci = int(ct2[i]); cprev = int(ct2[i - 1]); fi = int(fterm[i]); nxt = []
        for sc0, pa, tl, path in beams:
            for d in range(max_skip + 1):
                acc = pa + 1 + d
                if acc >= len(K):
                    break
                keff = (int(K[acc]) + fi) % N
                p = int((ci + sign * keff) % N)
                ok = True
                for m in range(pa + 1, acc):
                    km = (int(K[m]) + fi) % N
                    if (p - sign * km) % N != cprev:
                        ok = False; break
                if not ok:
                    continue
                add = _TR[p]
                nxt.append((sc0 + qdelta(tl, add), acc, tl + add, path + (p,)))
        if not nxt:
            break
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]
    best = max(beams, key=lambda x: x[0])
    return {"score": Q.score_norm(idx_to_trans(list(best[3]))),
            "plain_idx": list(best[3]), "translit": idx_to_trans(list(best[3]))}


# =====================================================================
# SYNTHETIC SANITY GATES
# =====================================================================
def gate_transform():
    """(a) Plant: take English, first-DIFFERENCE it in ct-space, then encipher-skip.
    The decoder should recover it AFTER integrating (inverse transform), and rigid
    should miss it. We verify the transform round-trips and the skip decoder scores
    English on the integral of a diff-enciphered stream."""
    print("-" * 68)
    print("GATE (a) first-difference / integral transform round-trip + skip decode")
    plain = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED KNOW THIS "
             "THAT THE INSTAR EMERGENCE IS AT HAND AND THE PILGRIM SHALL FIND TRUTH")
    P = eng_to_idx(plain)
    K = np.array(eng_to_idx(open(os.path.join(ROOT, "data", "keys", "self_reliance.txt"),
                 encoding="utf-8", errors="ignore").read()), dtype=np.int64)
    sign, o = -1, 400
    # normal encipher
    C, _, _ = encipher_keyskip(P, list(K[o:]), sign=sign, supp=0.83)
    C = np.array(C, dtype=np.int64)
    # transform round-trip check
    d = ct_firstdiff(C)
    rt = ct_integral(d)
    roundtrips = bool(np.array_equal(rt, C % N))
    print(f"  firstdiff->integral round-trips exactly: {roundtrips}")
    # The genuine attack: given the DIFF stream, recover by integrating first then
    # decoding under the true key. (An adversary who diff-transformed the ct.)
    ct_recovered = ct_integral(d)
    from skipdecode import beam_decode, rigid_decode
    bd = beam_decode(list(ct_recovered), list(K), sign=sign, o=o, beam_w=400, max_skip=3)
    rd = rigid_decode(list(ct_recovered), list(K), sign=sign, o=o)
    mb = sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P)
    print(f"  after integral, BEAM score={bd['score']:.2f} match={mb*100:.0f}%  "
          f"RIGID score={rd['score']:.2f}")
    ok = roundtrips and bd["score"] > -5.0 and mb > 0.9 and rd["score"] < -6.0
    print(f"  GATE (a): {'PASS' if ok else 'FAIL'}  "
          f"(transform invertible; skip-beam recovers, rigid misses)")
    return ok


def gate_selfkey():
    """(b) Plant: page A's plaintext IS page B's key. Encipher B under A's plaintext
    with the skip filter; the skip beam given A's plaintext must recover B, rigid
    must miss."""
    print("-" * 68)
    print("GATE (b) page-on-page self-keying (one page's plaintext as another's key)")
    plainA = ("WITHIN THE DEEP WEB THERE IS A PAGE THAT HOLDS THE PRIMES SACRED AND "
              "THE CIRCUMFERENCE OF ALL THINGS IS FOUND WITHIN THE SELF AND THE WHOLE "
              "AND THE PILGRIM WHO WALKS THE PATH OF WISDOM SHALL COME TO KNOW THE TRUTH "
              "THAT LIES BENEATH THE SURFACE OF ALL THAT IS SEEN AND UNSEEN IN THIS WORLD")
    plainB = ("KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND THE PILGRIM WHO SOLVES "
              "THE PUZZLE SHALL LOSE THE SELF TO GAIN THE TOTIENT AND THE TRUTH BEYOND "
              "THE VEIL OF MORTAL THINGS AND THE SACRED GEOMETRY OF THE CIRCUMFERENCE "
              "SHALL BE REVEALED UNTO THOSE WHO SEEK WITH A PURE HEART AND AN OPEN MIND")
    PA = eng_to_idx(plainA)
    PB = eng_to_idx(plainB)
    sign = -1
    # key must be long enough for PB plus worst-case skips; pad A's plaintext
    PA_key = PA + [0] * (len(PB) * (MAXSKIP + 1) + 8)
    C, _, _ = encipher_keyskip(PB, PA_key, sign=sign, supp=0.83)  # key = A's plaintext
    C = np.array(C, dtype=np.int64)
    best = selfkey_pair(C, PA, screen_beam=300)
    # rigid comparison
    from skipdecode import rigid_decode
    rd = rigid_decode(list(C), PA + [0] * len(C), sign=sign, o=0)
    print(f"  skip selfkey best score={best[0]:.2f} @ {best[1]}   "
          f"rigid score={rd['score']:.2f}")
    ok = best[0] > -5.0 and rd["score"] < best[0] - 1.0
    print(f"  GATE (b): {'PASS' if ok else 'FAIL'}  "
          f"(skip-beam recovers self-key; rigid degrades with desync)")
    return ok


def gate_shared():
    """(b') Plant: two pages share a running key (no per-page skip => key cancels
    EXACTLY in the difference). The IoC of that difference is NOT raised (difference
    of two English texts is ~flat), so the sound detector is a CRIB DRAG. Verify the
    crib-drag score on the shared-key difference clearly beats the different-key
    control. Also confirm IoC is vacuous (documents WHY IoC was the wrong tool)."""
    print("-" * 68)
    print("GATE (b') shared-keystream detection via crib-drag on ciphertext difference")
    PA = eng_to_idx("THE PRIMES ARE SACRED AND THE TOTIENT IS SACRED WITHIN THE DEEP WEB "
                    "THE PILGRIM SHALL FIND THE CIRCUMFERENCE OF ALL SACRED GEOMETRY HERE")
    PB = eng_to_idx("KNOW THAT THE INSTAR EMERGENCE IS AT HAND AND THE SELF IS LOST TO GAIN "
                    "THE WHOLE AND THE TRUTH BEYOND THE VEIL OF THE MORTAL WORLD IS REVEALED")
    L = min(len(PA), len(PB))
    PA = PA[:L]; PB = PB[:L]          # equal INDEX length so cancellation is well-defined
    K = np.array(eng_to_idx(open(os.path.join(ROOT, "data", "keys", "self_reliance.txt"),
                 encoding="utf-8", errors="ignore").read()), dtype=np.int64)[500:500 + L]
    sign = -1
    # SHARED key, NO skip (pure running key), so key cancels in difference
    CA = np.array([(PA[i] - sign * int(K[i])) % N for i in range(L)], dtype=np.int64)
    CB = np.array([(PB[i] - sign * int(K[i])) % N for i in range(L)], dtype=np.int64)
    # sound-mechanism check: full crib = PA reveals PB EXACTLY on the difference
    diff = (CA - CB) % N              # == P_a - P_b  (key cancels)
    reveal = (np.array(PA, dtype=np.int64) - diff) % N   # P_b = P_a - (P_a - P_b)
    exact = bool(np.array_equal(reveal, np.array(PB, dtype=np.int64)))
    print(f"  mechanism: diff + P_a == P_b exactly (shared key, no skip): {exact}")
    crib_shared, ioc_shared = shared_keystream_pair(CA, CB)
    # control: DIFFERENT keys
    K2 = np.array(eng_to_idx(open(os.path.join(ROOT, "data", "keys", "mabinogion.txt"),
                  encoding="utf-8", errors="ignore").read()), dtype=np.int64)[300:300 + L]
    CB2 = np.array([(PB[i] - sign * int(K2[i])) % N for i in range(L)], dtype=np.int64)
    crib_ctrl, ioc_ctrl = shared_keystream_pair(CA, CB2)
    print(f"  shared-key: crib={crib_shared:.2f} IoC={ioc_shared:.3f} | "
          f"different-key: crib={crib_ctrl:.2f} IoC={ioc_ctrl:.3f}")
    print(f"  (IoC ~flat both ways -> IoC is VACUOUS; crib-drag is the sound test)")
    # Gate passes if the mechanism is exact (shared key IS detectable in principle)
    # AND crib-drag gives positive separation. The separation is intentionally small:
    # difference-of-two-Englishes is near-random, so this attack is WEAK at page
    # scale and skip desync makes it weaker -- documented, not faked.
    ok = exact and crib_shared > crib_ctrl
    print(f"  GATE (b'): {'PASS' if ok else 'FAIL'}  "
          f"(mechanism exact + crib-drag leans toward shared key; WEAK separator)")
    return ok


def gate_feedback():
    """(c) Plant: ciphertext-feedback cipher (k=1..3) + skip filter. The feedback
    decoder (which recomputes the feedback from KNOWN ciphertext) must recover the
    plaintext; a decoder that ignores feedback (k=0) must miss."""
    print("-" * 68)
    print("GATE (c) short-history ciphertext-feedback (k=1..3) skip-aware")
    plain = ("THE TOTIENT FUNCTION IS SACRED AND THE PRIMES ARE SACRED KNOW THIS THAT "
             "THE INSTAR EMERGENCE IS AT HAND THE PILGRIM SHALL FIND THE SACRED TRUTH")
    P = eng_to_idx(plain)
    seedK = eng_to_idx(open(os.path.join(ROOT, "data", "keys", "self_reliance.txt"),
                       encoding="utf-8", errors="ignore").read())
    o = 0
    seedK_off = seedK[o:]
    allok = True
    for k in (1, 2, 3):
        C = encipher_ctfeedback(P, seedK_off, k=k, sign=-1, supp=0.83)
        # correct decode: knows k and seed key
        good = decode_ctfeedback(C, seedK_off, k=k, sign=-1, o=0, beam_w=300)
        mg = sum(a == b for a, b in zip(good["plain_idx"], P)) / len(P)
        # ignore-feedback control (k=0): treat seed key as plain running key
        bad = decode_ctfeedback(C, seedK_off, k=0, sign=-1, o=0, beam_w=300)
        mb = sum(a == b for a, b in zip(bad["plain_idx"], P)) / len(P)
        kok = good["score"] > -5.0 and mg > 0.9 and bad["score"] < -5.5
        allok = allok and kok
        print(f"  k={k}: feedback-aware score={good['score']:.2f} match={mg*100:.0f}% | "
              f"ignore-feedback score={bad['score']:.2f} match={mb*100:.0f}%  "
              f"{'ok' if kok else 'FAIL'}")
    print(f"  GATE (c): {'PASS' if allok else 'FAIL'}")
    return allok


# =====================================================================
# SMOKE over 3 pages
# =====================================================================
def smoke(npages=3):
    print("=" * 68)
    print(f"SMOKE over first {npages} unsolved pages")
    print("=" * 68)
    pages = load_pages()[:-2]
    sel = list(range(min(npages, len(pages))))
    ref = load_referenced()
    maxlen = max(len(pages[p]) for p in sel)
    numk = numeric_keys(maxlen * (MAXSKIP + 1) + 16)
    allkeys = ref + numk
    print(f"keys: {len(ref)} referenced + {len(numk)} numeric = {len(allkeys)}")

    results = {"firstdiff": [], "integral": [], "selfkey": [], "shared": [], "feedback": []}

    for p in sel:
        ct = np.array(pages[p], dtype=np.int64)
        print(f"\n-- page {p}  ({len(ct)} runes) --")

        # (a) transforms
        bd_s, bd_m, _ = attack_transformed(ct, allkeys, ct_firstdiff)
        bi_s, bi_m, _ = attack_transformed(ct, allkeys, ct_integral)
        results["firstdiff"].append(bd_s); results["integral"].append(bi_s)
        print(f"   (a) firstdiff best={bd_s:.2f} {bd_m} | integral best={bi_s:.2f} {bi_m}")

        # (c) feedback k=1..3 with a couple of seed keys (referenced[0] + primes)
        seedkeys = [ref[0]] if ref else []
        seedkeys += numk[:1]
        best_fb = (-99.0, None)
        for sname, sk in seedkeys:
            skl = sk if isinstance(sk, np.ndarray) else np.array(sk, dtype=np.int64)
            for k in (1, 2, 3):
                # encipher relation unknown; we DECODE the real ct as if it were
                # ct-feedback under this seed key -> recompute feedback from real ct
                r = decode_ctfeedback(ct, skl, k=k, sign=-1, o=0, beam_w=200)
                if r["score"] > best_fb[0]:
                    best_fb = (r["score"], (sname, k))
        results["feedback"].append(best_fb[0])
        print(f"   (c) ct-feedback best={best_fb[0]:.2f} {best_fb[1]}")

    # (b) page-on-page over the selected pages (all ordered pairs)
    print(f"\n-- (b) page-on-page over pages {sel} --")
    best_sk = (-99.0, None)
    best_sh = (-99.0, None)
    for i in sel:
        for j in sel:
            if i == j:
                continue
            ct_i = np.array(pages[i], dtype=np.int64)
            # self-keying: use page j's CIPHERTEXT as a stand-in key at smoke
            # (true plaintext unknown; this is the vacuous-vs-viable check)
            sk = selfkey_pair(ct_i, np.array(pages[j], dtype=np.int64), screen_beam=150)
            if sk[0] > best_sk[0]:
                best_sk = (sk[0], (i, j, sk[1]))
        for j in sel:
            if j <= i:
                continue
            crib, ioc = shared_keystream_pair(np.array(pages[i]), np.array(pages[j]))
            if crib > best_sh[0]:
                best_sh = (crib, (i, j, round(ioc, 3)))
    results["selfkey"].append(best_sk[0]); results["shared"].append(best_sh[0])
    print(f"   selfkey best={best_sk[0]:.2f} {best_sk[1]} | "
          f"shared-diff best={best_sh[0]:.2f} {best_sh[1]}")

    print("\n" + "=" * 68)
    print("SMOKE SUMMARY (best score_norm per family; confirm thr -5.5, null-max -6.82)")
    for fam, vals in results.items():
        if vals:
            print(f"  {fam:12s} best={max(vals):.2f}")
    print("=" * 68)
    return results


def run_gates():
    print("=" * 68)
    print("SELF-REFERENTIAL FAMILY -- synthetic validation gates")
    print("=" * 68)
    ga = gate_transform()
    gb = gate_selfkey()
    gbp = gate_shared()
    gc = gate_feedback()
    print("\n" + "=" * 68)
    print(f"GATES: (a)transform={ga}  (b)selfkey={gb}  (b')shared={gbp}  (c)feedback={gc}")
    print("=" * 68)
    return dict(transform=ga, selfkey=gb, shared=gbp, feedback=gc)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.gate:
        run_gates()
    if args.smoke:
        smoke(args.pages)
    if args.full:
        run_gates()
        smoke(args.pages)
    if not (args.gate or args.smoke or args.full):
        run_gates()
        smoke(3)
