"""Round 19 / C1 -- propagation: re-run B-05's Part-1 grid on the RESOLVED payload.

Why this is not optional. B-05 (LEDGER, round 13) is a NEGATIVE whose seed is
`canon_256.bin`. C1's adjudication changes `canon_256.bin` at indices 45, 50 and 246 --
none of which is one of the six indices B-05 varied. B-05's own control_detail records the
avalanche it measured: "Flipping ONE contested byte destroys recovery (-7.38)", i.e. from
-4.170 (perfect) to noise. So B-05's Part-1 negative covers a 256-byte seed that, on the
image evidence, is not the payload. By C1/PREREG.md 4.1 it must be re-run.

Structure of B-05's grid is inherited unchanged -- 6 representations x 15 generators x
2 reductions x 2 directions x 2 atbash x 2 signs x 14 offsets = 20,160 beam decodes,
exhaustive, plus B-05's constant-shift secondary pass on res.raw.

The bar is B-05's own and is NOT re-tuned: HIT iff score >= -5.5 AND score > null_max.

The positive control (PREREG 4.2) runs first and must PASS or the sweep is reported as a
null from an unvalidated instrument.

    python3 b05_rerun.py
"""
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
B05 = os.path.join(LP, "analysis", "round13", "B05")
for p in (os.path.join(LP, "src"), os.path.join(LP, "analysis"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"), B05):
    sys.path.insert(0, p)

import skipdecode as sk            # noqa: E402
import lib_numchannel as nc        # noqa: E402
import prf                          # noqa: E402

# B-05's pinned grid, copied verbatim from round13/B05/sweep.py
HEAD = 400
BEAM_W = 120
MAX_SKIP = 3
OFFSETS = [0, 1, 2, 3, 5, 8, 13, 29, 64, 128, 256, 512, 1024, 3301]
REDUCTIONS = ["mod", "reject"]
SIGNS = [-1, +1]
DIRECTIONS = ["fwd", "rev"]
ATBASH = [False, True]
HIT_SCORE = -5.5

UNS = nc.unsolved()
HEADSEQ = UNS[:HEAD]
FULL_LEN = len(UNS)
TOTAL_KS = FULL_LEN * (MAX_SKIP + 1) + max(OFFSETS) + 64
HEAD_KS = HEAD * (MAX_SKIP + 1) + max(OFFSETS) + 64

RESOLVED = open(os.path.join(HERE, "payload_resolved.bin"), "rb").read()
CANON = open(os.path.join(LP, "analysis", "pp49_51", "canon_256.bin"), "rb").read()
CHANGED = [i for i in range(256) if RESOLVED[i] != CANON[i]]

PLAIN = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
         "ENCRYPTEDKNOWTHISTHATTHEINSTAREMERGENCEISATHANDANDTHEPILGRIMWHO"
         "SOLVESTHEDEEPWEBSHALLFINDTHETRUTHWITHINTHECIRCUMFERENCEOFTHEEND")


def log(m):
    print(m, flush=True)


def reps_resolved():
    return {"res." + k: fn(RESOLVED) for k, fn in prf.REPR_FNS.items()}


# ------------------------------------------------------------ positive control
def control():
    P = sk.eng_to_idx(PLAIN)
    need = len(P) * 5 + 256
    wrong = bytes((b + 7) % 256 for b in RESOLVED)
    out = []
    for gen, red in (("sha256_ctr", "mod"), ("rc4", "mod"),
                     ("hmac_drbg_sha256", "reject"), ("aes256_ctr_k", "mod")):
        Kt = prf.keystream(RESOLVED, gen, red, need)
        Kw = prf.keystream(wrong, gen, red, need)
        Kc = prf.keystream(CANON, gen, red, need)      # the SUPERSEDED seed
        C, skips, _ = sk.encipher_keyskip(P, Kt, sign=-1, supp=0.83, seed=3301)
        bt = sk.beam_decode(C, Kt, sign=-1, o=0, beam_w=400, max_skip=3)
        bw = sk.beam_decode(C, Kw, sign=-1, o=0, beam_w=400, max_skip=3)
        bc = sk.beam_decode(C, Kc, sign=-1, o=0, beam_w=400, max_skip=3)
        rig = sk.rigid_decode(C, Kt, sign=-1, o=0)
        rec = bt["translit"][:len(PLAIN)]
        frac = sum(1 for a, b in zip(rec, PLAIN) if a == b) / len(PLAIN)
        out.append({"gen": gen, "red": red, "skips": sum(1 for s in skips if s),
                    "beam_correct": bt["score"], "beam_wrong": bw["score"],
                    "beam_old_canon_seed": bc["score"], "rigid_correct": rig["score"],
                    "char_recovery": frac, "head": bt["translit"][:48]})
        log("  %-18s %-7s beam(resolved)=%7.3f  beam(wrong)=%7.3f  "
            "beam(OLD canon_256)=%7.3f  rigid=%7.3f  recovery=%.3f"
            % (gen, red, bt["score"], bw["score"], bc["score"], rig["score"], frac))
    passed = all(c["beam_correct"] >= -5.0 for c in out)
    return {"cases": out, "bar": "beam(correct resolved seed) >= -5.00 on all 4 generators",
            "verdict": "PASS" if passed else "FAIL"}


# ------------------------------------------------------------------ null band
def null_band(n=200, seed0=3301):
    K = prf.keystream(RESOLVED, "sha256_ctr", "mod", HEAD_KS)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(HEADSEQ)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, K, sign=-1, o=(k * 37) % 2000,
                                   beam_w=BEAM_W, max_skip=MAX_SKIP)["score"])
    return sum(vals) / len(vals), max(vals), vals


# --------------------------------------------------------------------- part 1
def part1(bar):
    reps = reps_resolved()
    gens = list(prf.GENERATORS)
    results = []
    t0 = time.time()
    ndone = 0
    for rname in sorted(reps):
        seed = reps[rname]
        for gname in gens:
            for red in REDUCTIONS:
                base = prf.keystream(seed, gname, red, TOTAL_KS)
                for direction in DIRECTIONS:
                    Kd = base if direction == "fwd" else base[::-1]
                    for atb in ATBASH:
                        K = prf.atbash(Kd) if atb else Kd
                        for sign in SIGNS:
                            for o in OFFSETS:
                                bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=o,
                                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                                ndone += 1
                                results.append({"rep": rname, "gen": gname, "red": red,
                                                "dir": direction, "atbash": atb,
                                                "sign": sign, "o": o,
                                                "score": bd["score"],
                                                "head": bd["translit"][:48]})
            log("  [part1] %-14s %-18s cum=%6d %6.0fs best=%.3f"
                % (rname, gname, ndone, time.time() - t0,
                   max(r["score"] for r in results)))
            # incremental checkpoint: this job has been killed once already, and a
            # partial exhaustive sweep with a stated covered fraction is a result;
            # a lost one is not.
            done = sorted({(r["rep"], r["gen"]) for r in results})
            json.dump({"decodes": len(results), "seconds": time.time() - t0,
                       "reps_gens_complete": ["%s/%s" % t for t in done],
                       "best": max(r["score"] for r in results),
                       "top20": sorted(results, key=lambda x: -x["score"])[:20]},
                      open(os.path.join(HERE, "out_b05_partial.json"), "w"), indent=1)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results, [r for r in results if r["score"] >= bar], time.time() - t0


def part1_shift(bar):
    """B-05's secondary constant-shift pass, on the resolved payload."""
    need = HEAD * (MAX_SKIP + 1) + 64
    results = []
    t0 = time.time()
    for gname in prf.GENERATORS:
        for red in REDUCTIONS:
            base = prf.keystream(RESOLVED, gname, red, need)
            for s in range(29):
                K = [(k + s) % 29 for k in base]
                for sign in SIGNS:
                    bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=0,
                                        beam_w=BEAM_W, max_skip=MAX_SKIP)
                    results.append({"gen": gname, "red": red, "shift": s,
                                    "sign": sign, "score": bd["score"]})
    results.sort(key=lambda x: x["score"], reverse=True)
    log("  [shift] %d decodes  %.0fs  best=%.3f"
        % (len(results), time.time() - t0, results[0]["score"]))
    return results, [r for r in results if r["score"] >= bar], time.time() - t0


def main():
    log("=" * 78)
    log("C1 PROPAGATION -- B-05 Part 1 re-run on the RESOLVED pp49-51 payload")
    log("=" * 78)
    log("resolved payload differs from canon_256.bin at %s" % CHANGED)
    log("unsolved runes: %d  HEAD=%d  beam_w=%d  max_skip=%d" %
        (FULL_LEN, HEAD, BEAM_W, MAX_SKIP))

    log("\n--- POSITIVE CONTROL (PREREG 4.2) ---")
    ctrl = control()
    log("  control verdict: %s" % ctrl["verdict"])

    log("\n--- NULL BAND (recomputed on this run, not quoted) ---")
    nmean, nmax, nvals = null_band()
    log("  shuffle null n=200: mean=%.3f  max=%.3f" % (nmean, nmax))
    bar = max(HIT_SCORE, nmax)
    log("  effective bar = max(-5.5, null_max) = %.3f" % bar)

    log("\n--- PART 1 (exhaustive over B-05's pinned grid, resolved reps) ---")
    r1, h1, t1 = part1(bar)
    log("\n--- PART 1-SHIFT (constant additive shift, res.raw) ---")
    rs, hs, ts = part1_shift(bar)

    top = r1[:15]
    log("\ntop 10 of %d Part-1 decodes:" % len(r1))
    for r in r1[:10]:
        log("  %7.3f  %-14s %-18s %-7s %-4s atb=%-5s sign=%+d o=%-5d %s"
            % (r["score"], r["rep"], r["gen"], r["red"], r["dir"], r["atbash"],
               r["sign"], r["o"], r["head"][:36]))

    out = {
        "lane": "round19/C1 propagation of A-04 into B-05",
        "resolved_payload_sha256": __import__("hashlib").sha256(RESOLVED).hexdigest(),
        "bytes_changed_vs_canon": CHANGED,
        "control": ctrl,
        "null": {"n": 200, "mean": nmean, "max": nmax},
        "bar": bar,
        "part1": {"decodes": len(r1), "seconds": t1, "hits": h1,
                  "best": r1[0]["score"], "top15": top},
        "part1_shift": {"decodes": len(rs), "seconds": ts, "hits": hs,
                        "best": rs[0]["score"], "top5": rs[:5]},
        "total_decodes": len(r1) + len(rs) + 200,
        "verdict": "HIT" if (h1 or hs) else "NEGATIVE",
        "conditionals": {
            "key_space": "B-05's pinned Part-1 grid, restricted to the 6 resolved-payload "
                         "representations (the 6 decpref representations are unchanged by "
                         "C1 and stay covered by B-05 itself).",
            "decoder_transition_model": "skipdecode.beam_decode, beam_w=120, max_skip=3 -- "
                                        "exact for encipher_keyskip and NOTHING else "
                                        "(round18 L7-B). skip_by_two is not represented.",
            "adjudicator_register": "English quadgram only (round18 L7-A): measured power "
                                    "0.33 Latin, 0.00 vowel-dropped English. This negative "
                                    "is an ENGLISH-ONLY negative.",
        },
    }
    json.dump(out, open(os.path.join(HERE, "out_b05_rerun.json"), "w"), indent=1)
    log("\nVERDICT: %s   best Part-1 %.3f vs bar %.3f   (%d decodes)"
        % (out["verdict"], r1[0]["score"], bar, out["total_decodes"]))
    log("wrote out_b05_rerun.json")


if __name__ == "__main__":
    main()
