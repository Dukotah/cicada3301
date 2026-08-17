"""Round 10B / Lane B5 -- METHOD CONTINUITY.

Tests hypothesis H-B5 (see PREREG.md): LP2 0-54 uses a COMPOSED keystream
    K[j] = ( cw*W[(j+wphase) mod L] + cg*G[j+goff] ) mod 29
where W is a themed Gematria-Primus word (the demonstrated key TYPE of pages
03/14) and G is one of the author's sanctified deterministic generators
(prime / prime-totient / totient, the p56 family) -- i.e. the author's two
demonstrated KEYED constructions COMPOSED, which is the same move p06-09 makes
with Atbash-then-Caesar.

This is the repo's own never-executed proposal G5 from
analysis/recon/i7_constants/AUDIT.md l.140 and priority_seeds.json.

Decoding uses the VALIDATED skip-tolerant beam from campaign18_skip (imported
verbatim), because the ~83% doublet filter desynchronises any key.

Run:
  PYTHONUTF8=1 python analysis/round10b/B5-solved-page-method/composed_key.py
  ... --pages 0,1,2,5,20,54   --words-cap 60  --goffs 64
"""
import os, sys, time, argparse, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))

from lp import gematria as gp, score as sc, ciphers as cph, corpus, solve
from run_stats import load_pages
from skipdecode import eng_to_idx, idx_to_trans, encipher_keyskip
from sweep import beam, BG_LM, MAXSKIP

Q = sc.default(); N = gp.N

# --- thresholds, fixed in PREREG.md -----------------------------------------
BREAK_THR = -5.2
CONFIRM_THR = -5.5
SCREEN_LEN = 90
SCREEN_BEAM = 200
FULL_BEAM = 400
PREFIX_W = 26          # rigid-prefix screen window (tier 1)
TIER1_KEEP = 2500      # configs kept by the vectorised bigram prefix screen
TOPK_BEAM = 120        # configs promoted from tier 2 to the len-90 beam screen


# ----------------------------------------------------------------- word list
def load_words(cap=None):
    ws = []
    p = os.path.join(ROOT, "data", "keys", "thematic.txt")
    for line in open(p, encoding="utf-8"):
        w = line.strip().upper()
        if w:
            ws.append(w)
    import json
    seeds = json.load(open(os.path.join(
        ROOT, "analysis", "recon", "i7_constants", "priority_seeds.json")))
    for w in seeds.get("keyword_seeds", []):
        if w.upper() not in ws:
            ws.append(w.upper())
    out = []
    for w in ws:
        k = gp.keyword_to_indices(w)
        if 2 <= len(k) <= 20:
            out.append((w, np.array(k, dtype=np.int64)))
    return out[:cap] if cap else out


# ------------------------------------------------------------- generators G
def gens(length):
    return [
        ("phi_prime", np.array(cph.prime_totient_stream(length), dtype=np.int64)),
        ("prime",     np.array(cph.prime_stream(length), dtype=np.int64)),
        ("totient",   np.array(cph.totient_stream(length), dtype=np.int64)),
    ]


COEFS = [(+1, +1), (+1, -1), (-1, +1), (-1, -1),
         (+1, 0), (-1, 0),           # pure keyword (anchor: prior null)
         (0, +1), (0, -1)]           # pure generator (anchor: prior null)


def build_K(W, wphase, G, goff, cw, cg, need):
    """Composed key array of length >= need, as INDICES mod 29."""
    L = len(W)
    if cw:
        idx = (np.arange(need) + wphase) % L
        kw = cw * W[idx]
    else:
        kw = np.zeros(need, dtype=np.int64)
    if cg:
        kg = cg * G[goff:goff + need]
    else:
        kg = np.zeros(need, dtype=np.int64)
    return (kw + kg) % N


# ------------------------------------------------- fast rigid-prefix screen
def gmat(G, goffs, kmax):
    """Gm[k, t] = G[goffs[t] + k]  -- built once per generator."""
    go = np.array(goffs, dtype=np.int64)
    return np.stack([G[go + k] for k in range(kmax)], axis=0)


def prefix_scores(ct, W, Gm, cw, cg, goffs, wphases):
    """Vectorised index-bigram score of the RIGID prefix decode for every
    (wphase, goff) pair.  Tolerant of one early key-skip via a small grid, the
    same trick sweep.prefilter uses.  Returns list of (score, wphase, goff)."""
    Wn = min(PREFIX_W, len(ct))
    L = len(W)
    T = len(goffs)
    out = []
    skipgrid = (0, 6, 12, 18)
    for wp in wphases:
        bestrow = None
        for j in skipgrid:
            rows = np.empty((Wn, T), dtype=np.int64)
            for i in range(Wn):
                k = i + (1 if (j and i >= j) else 0)
                gpart = cg * Gm[k] if cg else 0
                wpart = cw * int(W[(k + wp) % L]) if cw else 0
                rows[i] = (int(ct[i]) + wpart + gpart) % N
            s = np.zeros(T)
            for i in range(1, Wn):
                s += BG_LM[rows[i - 1], rows[i]]
            bestrow = s if bestrow is None else np.maximum(bestrow, s)
        for t, go in enumerate(goffs):
            out.append((float(bestrow[t]), wp, int(go)))
    return out


def _rank_of(cands, truth):
    """Rank (1-based) of the true (word, gen, cw, cg) family in a ranked list."""
    if truth is None:
        return None
    for r, c in enumerate(cands, 1):
        if (c[1], c[2], c[3], c[4]) == truth:
            return r
    return None


def run_page(ct, words, GS, goffs, label, log, truth=None):
    """Full pipeline on one ciphertext index array. Returns best (score, desc, translit)."""
    need = len(ct) + MAXSKIP * len(ct) + 8
    kmax = min(PREFIX_W, len(ct)) + 2
    WD = dict(words); GD = dict(GS)
    GM = {gname: gmat(G, goffs, kmax) for gname, G in GS}
    cands = []
    for wname, W in words:
        wphases = list(range(len(W)))
        for gname, G in GS:
            Gm = GM[gname]
            for cw, cg in COEFS:
                if cw == 0 and cg == 0:
                    continue
                gl = goffs if cg else [0]
                wl = wphases if cw else [0]
                Gmx = Gm if cg else Gm[:, :1]
                for s, wp, go in prefix_scores(ct, W, Gmx, cw, cg, list(gl), wl):
                    cands.append((s, wname, gname, cw, cg, wp, go))
    cands.sort(key=lambda x: x[0], reverse=True)
    r1 = _rank_of(cands, truth)
    log(f"    tier1 (rigid bigram prefix, W={PREFIX_W}): {len(cands)} configs"
        + (f"  [truth-family rank {r1}]" if truth else ""))
    # tier 2: tiny SKIP-AWARE beam over the tier-1 survivors
    t2 = []
    for s, wname, gname, cw, cg, wp, go in cands[:TIER1_KEEP]:
        K = build_K(WD[wname], wp, GD[gname], go, cw, cg, need)
        path = beam(ct, K, +1, 0, min(30, len(ct)), 60)
        t2.append((Q.score_norm(idx_to_trans(path)), wname, gname, cw, cg, wp, go))
    t2.sort(key=lambda x: x[0], reverse=True)
    r2 = _rank_of(t2, truth)
    log(f"    tier2 (skip beam, 30 runes): kept {len(t2)}; promoting {TOPK_BEAM}"
        + (f"  [truth-family rank {r2}]" if truth else ""))
    screened = []
    for s, wname, gname, cw, cg, wp, go in t2[:TOPK_BEAM]:
        W = WD[wname]; G = GD[gname]
        K = build_K(W, wp, G, go, cw, cg, need)
        path = beam(ct, K, +1, 0, min(SCREEN_LEN, len(ct)), SCREEN_BEAM)
        sn = Q.score_norm(idx_to_trans(path))
        screened.append((sn, wname, gname, cw, cg, wp, go))
    screened.sort(key=lambda x: x[0], reverse=True)
    sn, wname, gname, cw, cg, wp, go = screened[0]
    K = build_K(WD[wname], wp, GD[gname], go, cw, cg, need)
    pathf = beam(ct, K, +1, 0, min(len(ct), 200), FULL_BEAM)
    tlf = idx_to_trans(pathf)
    desc = f"{wname}({cw:+d}) + {gname}({cg:+d}) wphase={wp} goff={go}"
    best = (max(sn, Q.score_norm(tlf)), desc, tlf[:110])
    log(f"    [{label}] best {best[0]:.3f}  <- {best[1]}   (screen top3: " +
        ", ".join(f"{x[0]:.2f}/{x[1]}+{x[2]}" for x in screened[:3]) + ")")
    log(f"       {best[2]}")
    return best


# ------------------------------------------------------------------ controls
def pc_a(words, log):
    """Task-mandated positive control: re-find DIVINITY (03.jpg) and
    FIRFUMFERENFE (14.jpg) as the top word out of the full candidate list."""
    log("=" * 78)
    log("PC-A  re-find the known solved keys from the same word list")
    log("=" * 78)
    ok = True
    for label, truth in (("03.jpg", "DIVINITY"), ("14.jpg", "FIRFUMFERENFE")):
        pg = corpus.page_by_label(label)
        runes = pg["runes"]
        nr = len(gp.runes_to_indices(runes))
        rows = []
        for w, _ in words:
            stream = cph.repeat_key(gp.keyword_to_indices(w), nr)
            res = solve.find_interrupters(runes, stream, sign=-1,
                                          beam_width=200, scorer=Q)
            rows.append((res["score_norm"], w))
        rows.sort(reverse=True)
        top = rows[0]
        hit = (top[1] == truth) and top[0] >= -5.0
        ok &= hit
        log(f"  {label}: top = {top[1]} @ {top[0]:.3f}   (truth {truth})  "
            f"runner-up {rows[1][1]} @ {rows[1][0]:.3f}   -> {'PASS' if hit else 'FAIL'}")
    return ok


def pc_b(words, goffs, log):
    """Planted composed key: DIVINITY (+1) + phi_prime (+1) at goff=17, under the
    0.83 doublet key-skip filter. The sweep must find it; rigid must miss it."""
    log("=" * 78)
    log("PC-B  planted COMPOSED key + doublet key-skip filter")
    log("=" * 78)
    plain = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
             "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND "
             "AND THE PILGRIM WHO SEEKS THE TRUTH SHALL SHED HIS OWN CIRCUMFERENCE "
             "AND FIND THE DIVINITY WITHIN AND EMERGE INTO THE LIGHT OF THE END")
    P = eng_to_idx(plain)
    need = len(P) * (MAXSKIP + 1) + 64
    GS = gens(need + 4096)
    G = dict(GS)["phi_prime"]
    W = gp.keyword_to_indices("DIVINITY")
    Wn = np.array(W, dtype=np.int64)
    Ktrue = build_K(Wn, 0, G, 17, +1, +1, need)
    # encipher with p = (c + K) so c = (p - K); key-skip on would-be doublets
    rng = random.Random(3301)
    C, j, cprev = [], 0, None
    for p in P:
        while True:
            c = (p - int(Ktrue[j])) % N
            if cprev is not None and c == cprev and rng.random() < 0.83:
                j += 1; continue
            break
        C.append(c); j += 1; cprev = c
    ct = np.array(C, dtype=np.int64)
    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
    log(f"  planted ct: n={len(C)} doublet={100*dbl:.2f}% (target <1%, random 3.45%)")
    rigid = [(int(ct[i]) + int(Ktrue[i])) % N for i in range(len(ct))]
    log(f"  RIGID decode w/ CORRECT key : {Q.score_norm(idx_to_trans(rigid)):.3f}  "
        "(must be < -6.0)")
    best = run_page(ct, words, GS, goffs, "PC-B", log,
                    truth=("DIVINITY", "phi_prime", +1, +1))
    # PASS = recovers the planted plaintext at English scale with the correct
    # WORD and correct GENERATOR. (wphase/goff are recovered only up to the
    # aliasing wphase+d, goff+d, which is the same key started d symbols in --
    # the beam absorbs the d leading positions as skips.)
    hit = (best[0] >= -5.0 and "DIVINITY" in (best[1] or "")
           and "phi_prime" in (best[1] or "")
           and ("SACRED" in (best[2] or "") or "TOTIENT" in (best[2] or "")))
    log(f"  -> {'PASS' if hit else 'FAIL'}")
    return hit, best


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="0,1,2,5,20,54")
    ap.add_argument("--goffs", type=int, default=64)
    ap.add_argument("--words-cap", type=int, default=0)
    ap.add_argument("--skip-controls", action="store_true")
    ap.add_argument("--out", default="RESULTS.txt")
    ap.add_argument("--atbash", action="store_true",
                    help="reflect the ciphertext (i -> 28-i) before the sweep -- the p01/p06 move")
    a = ap.parse_args()

    outp = os.path.join(HERE, a.out)
    fh = open(outp, "w", encoding="utf-8")
    def log(s):
        print(s); fh.write(s + "\n"); fh.flush()

    t0 = time.time()
    words = load_words(a.words_cap or None)
    goffs = list(range(a.goffs))
    log(f"Lane B5 composed-key sweep | words={len(words)} gens=3 coefs={len(COEFS)-0} "
        f"goffs={len(goffs)} maxskip={MAXSKIP}")
    log(f"Thresholds: BREAK>={BREAK_THR}  CONFIRM>={CONFIRM_THR}  "
        f"English -4.1..-5.0  historical skip null-max -6.82\n")

    if not a.skip_controls:
        if not pc_a(words, log):
            log("\nABORT: PC-A failed; instrument cannot re-find known keys."); return
        okb, _ = pc_b(words, goffs, log)
        if not okb:
            log("\nABORT: PC-B failed; instrument cannot find its own planted composed key.")
            return
        log("")

    pages = load_pages()
    unsolved = [np.array(p, dtype=np.int64) for p in pages[:-2]]
    if a.atbash:
        unsolved = [(N - 1) - u for u in unsolved]
        log("ATBASH pre-reflection APPLIED to every ciphertext page")
    want = [int(x) for x in a.pages.split(",")]
    need_max = max(len(unsolved[i]) for i in want) * (MAXSKIP + 1) + max(goffs) + 64
    GS = gens(need_max + 4096)

    log("=" * 78); log("REAL LP2 PAGES"); log("=" * 78)
    real = []
    for pi in want:
        ct = unsolved[pi]
        log(f"  page {pi}  n={len(ct)}")
        real.append((pi, run_page(ct, words, GS, goffs, f"real p{pi}", log)))

    log("")
    log("=" * 78); log("NULL CONTROL -- same sweep on length-matched SHUFFLES"); log("=" * 78)
    rng = np.random.default_rng(3301)
    null = []
    for pi in want:
        ct = unsolved[pi].copy(); rng.shuffle(ct)
        log(f"  shuffled page {pi}  n={len(ct)}")
        null.append((pi, run_page(ct, words, GS, goffs, f"null p{pi}", log)))

    rb = max(b[0] for _, b in real); nb = max(b[0] for _, b in null)
    log("")
    log("=" * 78); log("VERDICT"); log("=" * 78)
    log(f"  best REAL      : {rb:.3f}")
    log(f"  best NULL(shuf): {nb:.3f}")
    log(f"  margin         : {rb - nb:+.3f}   (POSITIVE needs >= +0.50 and >= {CONFIRM_THR})")
    if rb >= BREAK_THR:
        log("  => BREAK CANDIDATE -- inspect plaintext and re-verify")
    elif rb >= CONFIRM_THR and (rb - nb) >= 0.5:
        log("  => POSITIVE (lead)")
    else:
        log("  => NEGATIVE: composed keyword-x-sacred-generator family shows no signal")
    log(f"\nelapsed {time.time()-t0:.1f}s")
    fh.close()


if __name__ == "__main__":
    main()
