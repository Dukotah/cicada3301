"""Round 10B / Lane B5 -- candidate C3: SACRED-VALUATION KEYWORD KEYS.

See PREREG-C3.md. Every keyword sweep ever run (here and publicly) converts a key
word to shifts through ONE map: the rune INDEX 0..28. The Gematria Primus gives
each rune a second number -- its PRIME -- and the book sanctifies primes and the
totient function (p05), then page 56 keys off phi(p) = p-1 mod 29. C3 keys a
themed WORD through those sacred valuations instead of through the index.

A valuation is a NON-AFFINE permutation of the key alphabet, so it is not
reachable by the sign / Atbash / offset knobs of any prior keyword sweep.

Run:
  PYTHONUTF8=1 python analysis/round10b/B5-solved-page-method/sacred_valuation.py
"""
import os, sys, time, random, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from composed_key import (ROOT, gp, cph, Q, N, beam, BG_LM, MAXSKIP,
                          idx_to_trans, eng_to_idx, load_pages, pc_a, load_words)

PREFIX_W = 26
TIER1_KEEP = 2000
TIER2_KEEP = 80
SCREEN_LEN, SCREEN_BEAM, FULL_BEAM = 90, 200, 400
BREAK_THR, CONFIRM_THR = -5.2, -5.5
MAXPHASE = 12

PR = np.array(gp.PRIMES, dtype=np.int64)

def _cum(idxs):
    c, out, t = 0, [], 0
    for i in idxs:
        t += int(PR[i]); out.append(t % N)
    return np.array(out, dtype=np.int64)

MAPS = {
    "index":     lambda k: k % N,                       # anchor: the known null family
    "prime":     lambda k: PR[k] % N,                   # the sacred numbers themselves
    "phi_prime": lambda k: (PR[k] - 1) % N,             # the page-56 sacred map
    "atbash":    lambda k: (N - 1 - k) % N,             # affine anchor
    "cumprime":  _cum,                                  # running total of the numbers
}


def load_wordlist(cap=None):
    """thematic + words_expanded + priority_seeds keywords, as index arrays."""
    ws, seen = [], set()
    for fn in ("thematic.txt", "words_expanded.txt"):
        p = os.path.join(ROOT, "data", "keys", fn)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            w = line.strip().upper()
            if w and w.isalpha() and w not in seen:
                seen.add(w); ws.append(w)
    for w, _ in load_words():
        if w not in seen:
            seen.add(w); ws.append(w)
    out = []
    for w in ws:
        k = gp.keyword_to_indices(w)
        if 2 <= len(k) <= 20:
            out.append((w, np.array(k, dtype=np.int64)))
    return out[:cap] if cap else out


def keyvals(Widx, mname):
    return MAPS[mname](Widx).astype(np.int64) % N


def build_K(KV, phase, sign, need):
    L = len(KV)
    return (sign * KV[(np.arange(need) + phase) % L]) % N


def prefix_scores(ct, KV, sign, phases):
    """Vectorised rigid-prefix index-bigram score over all phases at once."""
    Wn = min(PREFIX_W, len(ct)); L = len(KV)
    ph = np.array(phases, dtype=np.int64)
    best = None
    for j in (0, 6, 12, 18):
        rows = np.empty((Wn, len(ph)), dtype=np.int64)
        for i in range(Wn):
            k = i + (1 if (j and i >= j) else 0)
            rows[i] = (int(ct[i]) + sign * KV[(k + ph) % L]) % N
        s = np.zeros(len(ph))
        for i in range(1, Wn):
            s += BG_LM[rows[i - 1], rows[i]]
        best = s if best is None else np.maximum(best, s)
    return best


def run_page(ct, words, label, log, truth=None):
    need = len(ct) * (MAXSKIP + 1) + 8
    cands = []
    KVcache = {}
    for wname, W in words:
        for mname in MAPS:
            KV = keyvals(W, mname)
            KVcache[(wname, mname)] = KV
            phases = list(range(min(len(KV), MAXPHASE)))
            for sign in (+1, -1):
                s = prefix_scores(ct, KV, sign, phases)
                for t, ph in enumerate(phases):
                    cands.append((float(s[t]), wname, mname, sign, int(ph)))
    cands.sort(key=lambda x: x[0], reverse=True)
    r1 = next((r for r, c in enumerate(cands, 1)
               if truth and (c[1], c[2]) == truth), None)
    log(f"    tier1 (rigid prefix): {len(cands)} configs"
        + (f"  [truth (word,map) rank {r1}]" if truth else ""))
    t2 = []
    for _, wname, mname, sign, ph in cands[:TIER1_KEEP]:
        K = build_K(KVcache[(wname, mname)], ph, sign, need)
        t2.append((Q.score_norm(idx_to_trans(beam(ct, K, +1, 0, min(30, len(ct)), 60))),
                   wname, mname, sign, ph))
    t2.sort(key=lambda x: x[0], reverse=True)
    r2 = next((r for r, c in enumerate(t2, 1)
               if truth and (c[1], c[2]) == truth), None)
    log(f"    tier2 (skip beam 30): kept {len(t2)}"
        + (f"  [truth rank {r2}]" if truth else ""))
    scr = []
    for _, wname, mname, sign, ph in t2[:TIER2_KEEP]:
        K = build_K(KVcache[(wname, mname)], ph, sign, need)
        scr.append((Q.score_norm(idx_to_trans(
            beam(ct, K, +1, 0, min(SCREEN_LEN, len(ct)), SCREEN_BEAM))),
            wname, mname, sign, ph))
    scr.sort(key=lambda x: x[0], reverse=True)
    sn, wname, mname, sign, ph = scr[0]
    K = build_K(KVcache[(wname, mname)], ph, sign, need)
    tl = idx_to_trans(beam(ct, K, +1, 0, min(len(ct), 200), FULL_BEAM))
    best = (max(sn, Q.score_norm(tl)),
            f"{wname}/{mname}({sign:+d}) phase={ph}", tl[:110])
    log(f"    [{label}] best {best[0]:.3f}  <- {best[1]}   (top3: " +
        ", ".join(f"{x[0]:.2f}/{x[1]}/{x[2]}" for x in scr[:3]) + ")")
    log(f"       {best[2]}")
    return best


def pc_b(words, log):
    """Plant English under the phi_prime VALUATION of CIRCUMFERENCE + 0.83 skip filter."""
    log("=" * 78); log("PC-B  planted SACRED-VALUATION key (phi_prime of CIRCUMFERENCE)"); log("=" * 78)
    P = eng_to_idx("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL "
                   "THINGS SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE "
                   "IS AT HAND AND THE PILGRIM WHO SEEKS THE TRUTH SHALL EMERGE")
    W = np.array(gp.keyword_to_indices("CIRCUMFERENCE"), dtype=np.int64)
    KV = keyvals(W, "phi_prime")
    need = len(P) * (MAXSKIP + 1) + 64
    Kt = build_K(KV, 0, +1, need)
    rng = random.Random(3301); C, j, cprev = [], 0, None
    for p in P:
        while True:
            c = (p - int(Kt[j])) % N
            if cprev is not None and c == cprev and rng.random() < 0.83:
                j += 1; continue
            break
        C.append(c); j += 1; cprev = c
    ct = np.array(C, dtype=np.int64)
    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
    rg = [(int(ct[i]) + int(Kt[i])) % N for i in range(len(ct))]
    log(f"  planted ct: n={len(C)} doublet={100*dbl:.2f}% (random 3.45%)")
    log(f"  RIGID decode w/ CORRECT key: {Q.score_norm(idx_to_trans(rg)):.3f} (must be < -6.0)")
    b = run_page(ct, words, "PC-B", log, truth=("CIRCUMFERENCE", "phi_prime"))
    hit = (b[0] >= -5.0 and "CIRCUMFERENCE" in b[1] and "phi_prime" in b[1])
    log(f"  -> {'PASS' if hit else 'FAIL'}")
    return hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="0,1,2,5,20,54")
    ap.add_argument("--words-cap", type=int, default=0)
    ap.add_argument("--skip-pca", action="store_true")
    ap.add_argument("--out", default="RESULTS-C3-valuation.txt")
    a = ap.parse_args()
    fh = open(os.path.join(HERE, a.out), "w", encoding="utf-8")
    def log(s):
        print(s); fh.write(s + "\n"); fh.flush()

    t0 = time.time()
    words = load_wordlist(a.words_cap or None)
    log(f"C3 sacred-valuation keyword sweep | words={len(words)} maps={len(MAPS)} "
        f"signs=2 phases<={MAXPHASE} skip-beam maxskip={MAXSKIP}")
    log(f"maps: {', '.join(MAPS)}")
    log(f"Thresholds (PREREG-C3): BREAK>={BREAK_THR} CONFIRM>={CONFIRM_THR} "
        f"POSITIVE also needs null-margin >= 0.5\n")

    if not a.skip_pca:
        if not pc_a(load_words(), log):
            log("ABORT: PC-A failed"); return
    if not pc_b(words, log):
        log("ABORT: PC-B failed -- instrument blind to its own planted valuation key"); return
    log("")

    pages = load_pages()
    unsolved = [np.array(p, dtype=np.int64) for p in pages[:-2]]
    want = [int(x) for x in a.pages.split(",")]
    log("=" * 78); log("REAL LP2 PAGES"); log("=" * 78)
    real = []
    for i in want:
        log(f"  page {i}  n={len(unsolved[i])}")
        real.append(run_page(unsolved[i], words, f"real p{i}", log))
    log("")
    log("=" * 78); log("NULL CONTROL -- length-matched shuffles"); log("=" * 78)
    r = np.random.default_rng(3301); null = []
    for i in want:
        ct = unsolved[i].copy(); r.shuffle(ct)
        log(f"  shuffled page {i}  n={len(ct)}")
        null.append(run_page(ct, words, f"null p{i}", log))

    rb = max(x[0] for x in real); nb = max(x[0] for x in null)
    log("")
    log("=" * 78); log("VERDICT"); log("=" * 78)
    log(f"  best REAL {rb:.3f} | best NULL {nb:.3f} | margin {rb-nb:+.3f}")
    log("  => " + ("BREAK CANDIDATE" if rb >= BREAK_THR else
                   "POSITIVE (lead)" if (rb >= CONFIRM_THR and rb - nb >= 0.5) else
                   "NEGATIVE: sacred-valuation keyword keys show no signal"))
    log(f"elapsed {time.time()-t0:.1f}s")
    fh.close()


if __name__ == "__main__":
    main()
