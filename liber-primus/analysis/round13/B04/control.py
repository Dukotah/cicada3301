"""ROUND 13 / B-04 — the two mandatory positive controls (PREREG section 4).

G1  replicate round12/D3/pc_derivedkey.py: a planted SHA-256 counter keystream from
    b"CICADA3301" under the pinned soft key-skip filter must be recovered by the
    project's own skip-aware beam, while rigid stays in noise.

G2  plant-recover through THIS SWEEP'S OWN Stage-A screen: plant a keystream from a seed
    that is genuinely resident in the dictionary, then run the FULL Stage-A cross product
    (2165 seeds x 16 gens x 5 reds x sign x atbash x direction) against the synthetic
    ciphertext and require the planted config to rank #1 and clear the HIT bar.

A sweep that cannot find a planted seed proves nothing. Both gates must PASS before the
real sweep result is trusted.

Run:  PYTHONUTF8=1 python3 analysis/round13/B04/control.py
"""
import os, sys, json, time, random, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)

import skipdecode as sk                       # noqa: E402
import lib_numchannel as nc                   # noqa: E402
import ks                                     # noqa: E402
import seeds as seedmod                       # noqa: E402
from harness import stage_a_configs, run_configs, BEAM_W, MAX_SKIP, HEAD_L  # noqa: E402

PLAIN = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
         "ENCRYPTEDKNOWTHISTHATTHEINSTAREMERGENCEISATHANDANDTHEPILGRIMWHO"
         "SOLVESTHEDEEPWEBSHALLFINDTHETRUTHWITHINTHECIRCUMFERENCEOFTHEEND"
         "OFALLTHINGSJOURNEYDEEPWITHINANDYOUWILLARRIVEOUTSIDELIKETHEINSTAR")

PLANT_SEED = b"THE PRIMES ARE SACRED"     # resident in seeds.py, family "slogan"
PLANT_GEN, PLANT_RED = "sha256_ctr", "mod29"
PLANT_SIGN, PLANT_ATBASH, PLANT_DIR = -1, 0, "fwd"


# ---------------------------------------------------------------- G1
def gate_g1():
    """Verbatim replication of round12/D3/pc_derivedkey.py."""
    P = sk.eng_to_idx(PLAIN[:190])
    true_seed, wrong_seed = b"CICADA3301", b"WELCOME"

    def sha_ctr(seed, length):
        out, ctr = [], 0
        while len(out) < length:
            h = hashlib.sha256(seed + ctr.to_bytes(4, "big")).digest()
            for b in h:
                out.append(b % 29)
                if len(out) >= length:
                    break
            ctr += 1
        return out

    K = sha_ctr(true_seed, len(P) * 5 + 64)
    Kw = sha_ctr(wrong_seed, len(P) * 5 + 64)
    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
    rig = sk.rigid_decode(C, K, sign=-1, o=0)
    bt = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    bw = sk.beam_decode(C, Kw, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    truth = sk.idx_to_trans(P)
    rec = sum(1 for a, b in zip(bt["translit"], truth) if a == b) / len(truth)
    nmean, nmax, _ = nc.null_band(lambda s: nc.eng_norm(s), P, n=200, seed0=3301)
    res = {
        "plaintext_runes": len(P), "skips_injected": sum(skips),
        "ct_doublet_rate": dbl,
        "plain_eng_norm": nc.eng_norm(P),
        "rigid_correct_seed": rig["score"],
        "beam_correct_seed": bt["score"],
        "beam_wrong_seed": bw["score"],
        "char_recovery": rec,
        "null_shuffledP_mean": nmean, "null_shuffledP_max": nmax,
        "beam_head": bt["translit"][:60],
    }
    res["PASS"] = bool(bt["score"] >= -5.5 and rec >= 0.90
                       and bt["score"] - bw["score"] > 1.0
                       and rig["score"] < -6.0)
    return res


# ---------------------------------------------------------------- G2
def gate_g2(nproc=None, hit_bar=-5.5):
    """Plant a dictionary-resident seed and run the FULL Stage-A screen on it."""
    P = sk.eng_to_idx(PLAIN)[:HEAD_L]
    K = ks.make_ks(PLANT_GEN, PLANT_RED, PLANT_SEED, HEAD_L * (MAX_SKIP + 2) + 128)
    C, skips, _ = sk.encipher_keyskip(P, K, sign=PLANT_SIGN, supp=0.83, seed=3301)

    entries = seedmod.build()
    cfgs = stage_a_configs(entries)
    t0 = time.time()
    rows = run_configs(C, cfgs, nproc=nproc)
    rows.sort(key=lambda r: -r["score"])
    elapsed = time.time() - t0

    want = (PLANT_SEED, PLANT_GEN, PLANT_RED, PLANT_SIGN, PLANT_ATBASH, PLANT_DIR)
    rank = None
    hit = None
    for i, r in enumerate(rows):
        if (r["seed_bytes"] == PLANT_SEED and r["gen"] == PLANT_GEN
                and r["red"] == PLANT_RED and r["sign"] == PLANT_SIGN
                and r["atbash"] == PLANT_ATBASH and r["dir"] == PLANT_DIR):
            rank, hit = i + 1, r
            break
    truth = sk.idx_to_trans(P)
    rec = (sum(1 for a, b in zip(hit["head"], truth) if a == b) / len(hit["head"])
           if hit else 0.0)
    res = {
        "plant_seed": PLANT_SEED.decode(), "plant_gen": PLANT_GEN,
        "plant_red": PLANT_RED, "segment_len": HEAD_L,
        "skips_injected": sum(skips),
        "n_configs": len(rows), "elapsed_s": elapsed,
        "planted_rank": rank,
        "planted_score": hit["score"] if hit else None,
        "runner_up_score": rows[1]["score"] if len(rows) > 1 else None,
        "runner_up": (f"{rows[1]['label']}/{rows[1]['gen']}/{rows[1]['red']}"
                      if len(rows) > 1 else None),
        "head_recovery_vs_truth": rec,
        "top5": [{"score": r["score"], "label": r["label"],
                  "seed": r["seed_bytes"][:40].decode("utf-8", "replace"),
                  "gen": r["gen"], "red": r["red"], "sign": r["sign"],
                  "atbash": r["atbash"], "dir": r["dir"]} for r in rows[:5]],
    }
    res["PASS"] = bool(rank == 1 and hit and hit["score"] >= hit_bar)
    return res


# ---------------------------------------------------------------- null
def null_band(seq, n=200, seed0=3301):
    """PREREG s5 null: shuffle the segment, beam-decode under a B-04-family keystream."""
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(seq)
        r.shuffle(s)
        K = ks.make_ks("sha256_ctr", "mod29", b"NULL%d" % k,
                       len(s) * (MAX_SKIP + 2) + 128)
        vals.append(sk.beam_decode(s, K, sign=-1, o=0,
                                   beam_w=BEAM_W, max_skip=MAX_SKIP)["score"])
    vals.sort()
    return {"n": n, "mean": sum(vals) / len(vals), "max": vals[-1],
            "p99": vals[int(0.99 * (n - 1))], "p95": vals[int(0.95 * (n - 1))],
            "min": vals[0]}


if __name__ == "__main__":
    print("=" * 74)
    print("G1 — replicate round12/D3 positive control")
    print("=" * 74)
    g1 = gate_g1()
    for k, v in g1.items():
        print(f"  {k:26s} {v}")
    print(f"\nG1: {'PASS' if g1['PASS'] else 'FAIL'}\n")

    print("=" * 74)
    print("G2 — plant-recover through the Stage-A screen (full cross product)")
    print("=" * 74)
    g2 = gate_g2()
    print(f"  configs run     : {g2['n_configs']:,}  in {g2['elapsed_s']:.0f}s")
    print(f"  planted rank    : {g2['planted_rank']}   score {g2['planted_score']}")
    print(f"  runner-up       : {g2['runner_up_score']}  ({g2['runner_up']})")
    print(f"  head recovery   : {g2['head_recovery_vs_truth']:.3f}")
    for t in g2["top5"]:
        print(f"    {t['score']:.3f}  {t['label']:10s} {t['seed'][:28]:28s} "
              f"{t['gen']:16s} {t['red']:6s} s{t['sign']:+d} a{t['atbash']} {t['dir']}")
    print(f"\nG2: {'PASS' if g2['PASS'] else 'FAIL'}")

    out = {"G1": g1, "G2": g2}
    with open(os.path.join(HERE, "control_results.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nwrote control_results.json")
    print("CONTROLS:", "PASS" if (g1["PASS"] and g2["PASS"]) else "FAIL")
