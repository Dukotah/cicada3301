"""Round 10B / Lane B5 -- candidate C2: the SANCTIFIED GENERATOR WITH A NON-ZERO
START OFFSET.

Continuity argument: page 56 (AN END) is the author's last demonstrated cipher --
a keystream phi(p_i) = p_i - 1 mod 29 over consecutive primes starting at p_1 = 2.
That construction has exactly ONE free parameter: WHERE the sequence starts. The
continuity ranking puts "same sacred generator, non-zero start" at #2 (right
behind composition), because it escalates the specification without inventing a
primitive.

PRIOR COVERAGE (why this is not a re-dig): the skip-aware numeric sweep
`campaign18_skip/RUN-numeric.log` declares `Offsets: [0, 1, 2, 3, 4]`; the
plaintext-blind oracle `recon/i7_oracle/sweep.py` used `offsets{0..39}`;
`composed_key.py` (this lane) covered 0..63. Nobody has swept the start offset
DEEP. This does 0..4095 under the validated skip-tolerant beam.

Run: PYTHONUTF8=1 python analysis/round10b/B5-solved-page-method/gen_offset_sweep.py
"""
import os, sys, time, random, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from composed_key import (ROOT, gp, sc, cph, Q, N, beam, BG_LM, MAXSKIP,
                          idx_to_trans, eng_to_idx, load_pages, gens)

PREFIX_W = 26
TIER1_KEEP = 2000
TIER2_KEEP = 60
SCREEN_LEN = 90
BREAK_THR, CONFIRM_THR = -5.2, -5.5


def tier1(ct, G, cg, goffs):
    """Vectorised rigid-prefix index-bigram score over every start offset."""
    Wn = min(PREFIX_W, len(ct))
    go = np.array(goffs, dtype=np.int64)
    best = None
    for j in (0, 6, 12, 18):
        rows = np.empty((Wn, len(go)), dtype=np.int64)
        for i in range(Wn):
            k = i + (1 if (j and i >= j) else 0)
            rows[i] = (int(ct[i]) + cg * G[go + k]) % N
        s = np.zeros(len(go))
        for i in range(1, Wn):
            s += BG_LM[rows[i - 1], rows[i]]
        best = s if best is None else np.maximum(best, s)
    return best


def run(ct, GS, goffs, label, log, truth=None):
    need = len(ct) * (MAXSKIP + 1) + 8
    cands = []
    for gname, G in GS:
        for cg in (+1, -1):
            s = tier1(ct, G, cg, goffs)
            for t, o in enumerate(goffs):
                cands.append((float(s[t]), gname, cg, int(o)))
    cands.sort(key=lambda x: x[0], reverse=True)
    r1 = next((r for r, c in enumerate(cands, 1)
               if truth and (c[1], c[2], c[3]) == truth), None)
    log(f"    tier1: {len(cands)} configs" + (f"  [truth rank {r1}]" if truth else ""))
    GD = dict(GS)
    t2 = []
    for _, gname, cg, o in cands[:TIER1_KEEP]:
        K = (cg * GD[gname][o:o + need]) % N
        p = beam(ct, K, +1, 0, min(30, len(ct)), 60)
        t2.append((Q.score_norm(idx_to_trans(p)), gname, cg, o))
    t2.sort(key=lambda x: x[0], reverse=True)
    r2 = next((r for r, c in enumerate(t2, 1)
               if truth and (c[1], c[2], c[3]) == truth), None)
    log(f"    tier2: kept {len(t2)}" + (f"  [truth rank {r2}]" if truth else ""))
    scr = []
    for _, gname, cg, o in t2[:TIER2_KEEP]:
        K = (cg * GD[gname][o:o + need]) % N
        p = beam(ct, K, +1, 0, min(SCREEN_LEN, len(ct)), 200)
        scr.append((Q.score_norm(idx_to_trans(p)), gname, cg, o))
    scr.sort(key=lambda x: x[0], reverse=True)
    sn, gname, cg, o = scr[0]
    K = (cg * GD[gname][o:o + need]) % N
    tl = idx_to_trans(beam(ct, K, +1, 0, min(len(ct), 200), 400))
    best = (max(sn, Q.score_norm(tl)), f"{gname}({cg:+d}) goff={o}", tl[:100])
    log(f"    [{label}] best {best[0]:.3f}  <- {best[1]}")
    log(f"       {best[2]}")
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="0,1,2,5,20,54")
    ap.add_argument("--maxoff", type=int, default=4096)
    a = ap.parse_args()
    fh = open(os.path.join(HERE, "RESULTS-genoffset.txt"), "w", encoding="utf-8")
    def log(s):
        print(s); fh.write(s + "\n"); fh.flush()

    t0 = time.time()
    goffs = list(range(a.maxoff))
    pages = load_pages()
    unsolved = [np.array(p, dtype=np.int64) for p in pages[:-2]]
    want = [int(x) for x in a.pages.split(",")]
    need_max = max(len(unsolved[i]) for i in want) * (MAXSKIP + 1) + a.maxoff + 64
    GS = gens(need_max + 1024)
    log(f"C2 sanctified-generator START-OFFSET sweep | gens={len(GS)} "
        f"offsets=0..{a.maxoff-1} signs=2 skip-beam maxskip={MAXSKIP}")
    log("prior coverage: RUN-numeric.log offsets 0..4 | i7_oracle 0..39 | "
        "composed_key.py 0..63\n")

    # ---- positive control: plant phi_prime at goff=2000 under the skip filter
    log("POSITIVE CONTROL -- planted phi_prime keystream, goff=2000, 0.83 skip filter")
    P = eng_to_idx("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL "
                   "THINGS SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE "
                   "IS AT HAND AND THE PILGRIM WHO SEEKS THE TRUTH SHALL EMERGE")
    Gp = dict(GS)["phi_prime"]
    rng = random.Random(3301); C, j, cprev = [], 2000, None
    for p in P:
        while True:
            c = (p - int(Gp[j])) % N
            if cprev is not None and c == cprev and rng.random() < 0.83:
                j += 1; continue
            break
        C.append(c); j += 1; cprev = c
    ctp = np.array(C, dtype=np.int64)
    rg = [(int(ctp[i]) + int(Gp[2000 + i])) % N for i in range(len(ctp))]
    log(f"  rigid decode w/ correct key: {Q.score_norm(idx_to_trans(rg)):.3f} (must be < -6)")
    b = run(ctp, GS, goffs, "PC", log, truth=("phi_prime", +1, 2000))
    if not (b[0] >= -5.0 and "phi_prime" in b[1]):
        log("  -> FAIL / ABORT"); return
    log("  -> PASS\n")

    log("REAL PAGES")
    real = [run(unsolved[i], GS, goffs, f"real p{i}", log) for i in want]
    log("\nNULL CONTROL (shuffled)")
    r = np.random.default_rng(3301)
    null = []
    for i in want:
        ct = unsolved[i].copy(); r.shuffle(ct)
        null.append(run(ct, GS, goffs, f"null p{i}", log))
    rb = max(x[0] for x in real); nb = max(x[0] for x in null)
    log(f"\nVERDICT  real {rb:.3f} | null {nb:.3f} | margin {rb-nb:+.3f}")
    log("  => " + ("BREAK CANDIDATE" if rb >= BREAK_THR else
                   "POSITIVE" if (rb >= CONFIRM_THR and rb - nb >= 0.5) else
                   "NEGATIVE: no start offset of the sanctified generators reads"))
    log(f"elapsed {time.time()-t0:.1f}s")
    fh.close()


if __name__ == "__main__":
    main()
