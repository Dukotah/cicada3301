#!/usr/bin/env python3
"""Round 26 Lane C -- SEMANTIC-SEED sweep against REAL LP2 0-54 (nc.unsolved()).

For each corpus-semantic SEED x each generator in the zoo, produce a keystream, decode the real
LP2 0-54 ciphertext skip-aware (preset 'pair' = keyskip2, AND 'exact' = keyskip1), and adjudicate
through hitfn20. Persist language-agnostic per-row stats (IoC*N, min-distinct-32, best non-EN
panel LM, entropy, distinct count, recovery). A FULL-gate survivor STOPS and is FLAGGED-FOR-ORACLE.

Control (control.py) must PASS first: it proves every generator recovers a semantic-seed plant
at recovery >= 0.90. Only then does a null here count.

Run: python3 sweep.py                 # writes rows.jsonl + summary.json
"""
import os, sys, json, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis/round19/G3", "analysis/round19/G2", "analysis/round19/I1",
          "analysis/round19/I2", "analysis/round20/P3", "analysis/round20/HITFN",
          "analysis/round11", "analysis/campaign18_skip", "benchmark", "src"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import gen_py27 as GPY                 # noqa
import gen_perl as GPERL               # noqa
import driftbeam as DB                 # noqa
import hitfn20 as H                    # noqa
import lib_numchannel as nc            # noqa
from lp import gematria as gp, ciphers as CI   # noqa

N = gp.N
L_SCREEN = 120       # screen length (fast)
L_HIT = 240          # hit-adjudication length (matches C2 / compute-tail)
NEED = L_HIT * 10 + 2048
SCREEN_BAR = 5.0     # frozen (= C2 / S-G3): well below the pair claim bar; only escalate above this

U = list(nc.unsolved())
C_SCREEN = U[:L_SCREEN]
C_HIT = U[:L_HIT]


def gen_py27_r29(seed):     return GPY.keystream(seed, mode="random29", n=NEED)
def gen_py27_grbmod(seed):  return GPY.keystream(seed, mode="grb5_mod", n=NEED)
def gen_py27_grbrej(seed):  return GPY.keystream(seed, mode="grb5_rej", n=NEED)
def gen_perl_r29(seed):     return GPERL.g_r29(int(seed) & 0xFFFFFFFF, NEED)
def gen_prime(seed):        return CI.prime_stream(NEED, start=int(seed) % 5000)
def gen_totient(seed):      return CI.totient_stream(NEED, start=2 + int(seed) % 5000)
def gen_prime_totient(seed):return CI.prime_totient_stream(NEED, start=int(seed) % 5000)

ZOO = {
    "py27_random29": (gen_py27_r29, True),      # (fn, accepts_str)
    "py27_grb5_mod": (gen_py27_grbmod, True),
    "py27_grb5_rej": (gen_py27_grbrej, True),
    "perl_glibc_r29": (gen_perl_r29, False),
    "ladder_prime": (gen_prime, False),
    "ladder_totient": (gen_totient, False),
    "ladder_prime_totient": (gen_prime_totient, False),
}


# ---- language-agnostic per-decode stats (doctrine R3) ------------------------
def ioc(idxs):
    n = len(idxs)
    if n < 2:
        return 0.0
    cnt = [0] * N
    for x in idxs:
        cnt[x] += 1
    s = sum(c * (c - 1) for c in cnt)
    return s / (n * (n - 1))


def entropy(idxs):
    n = len(idxs)
    if n == 0:
        return 0.0
    cnt = [0] * N
    for x in idxs:
        cnt[x] += 1
    h = 0.0
    for c in cnt:
        if c:
            pr = c / n
            h -= pr * math.log2(pr)
    return h


def min_distinct_window(idxs, w=32):
    if len(idxs) < w:
        return len(set(idxs))
    m = N
    for i in range(len(idxs) - w + 1):
        d = len(set(idxs[i:i + w]))
        if d < m:
            m = d
    return m


def decode_stats(plain_idx):
    return {
        "iocN": round(ioc(plain_idx) * N, 4),
        "min_distinct_32": min_distinct_window(plain_idx, 32),
        "distinct": len(set(plain_idx)),
        "entropy": round(entropy(plain_idx), 4),
    }


def main():
    # gate: control must have passed
    cpath = os.path.join(HERE, "control.json")
    if not os.path.exists(cpath):
        print("REFUSE: control.json missing -- run control.py first"); return 2
    ctrl = json.load(open(cpath))
    if not ctrl.get("all_pass"):
        print("REFUSE: control did not pass; null would be meaningless"); return 2

    seeds = json.load(open(os.path.join(HERE, "seeds.json")))["seeds"]

    rows_path = os.path.join(HERE, "rows.jsonl")
    fout = open(rows_path, "w")
    n_rows = 0
    n_screen = 0
    best_screen = -1e9
    best_row = None
    flagged = []
    survivors_escalated = 0
    t0 = time.time()

    for si, s in enumerate(seeds):
        val = s["value"]
        is_str = s["is_str"]
        for gname, (gfn, accepts_str) in ZOO.items():
            if is_str and not accepts_str:
                continue
            try:
                K = gfn(val)
            except Exception as e:
                continue
            if len(K) < NEED:
                continue
            for preset in ("pair", "exact"):
                # fast SCREEN on L_SCREEN
                b = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=64,
                                   **DB.PRESETS[preset])
                pidx = b["plain_idx"]
                st = decode_stats(pidx)
                score = b["score"]
                n_screen += 1
                row = {"seed_label": s["label"], "seed_kind": s["kind"],
                       "seed_value": (val if is_str else int(val)),
                       "generator": gname, "preset": preset,
                       "screen_score": round(score, 4), **st}
                if score > best_screen:
                    best_screen = score
                    best_row = dict(row)
                # ESCALATE any screen clearing SCREEN_BAR to the full hitfn20 gate
                if score >= SCREEN_BAR:
                    survivors_escalated += 1
                    v = H.evaluate(H.HitDecode(C=C_HIT, K=K, o=0, preset=preset,
                                               n_round_adjudicated=len(seeds) * len(ZOO) * 2))
                    row["escalated"] = True
                    row["hit_recovery"] = round(v.recovery, 4)
                    row["hit_heldout"] = round(v.heldout_recovery, 4)
                    row["hit_pmax"] = round(v.pmax, 4)
                    row["hit_bar"] = round(v.bar, 4)
                    row["hit_clears_null"] = v.clears_null
                    row["hit"] = v.hit
                    if v.hit:
                        flagged.append(row)  # STOP-AND-ALERT: full-gate survivor
                fout.write(json.dumps(row) + "\n")
                n_rows += 1
    fout.close()

    summary = {
        "lane": "round26/C",
        "target": "LP2 0-54 (lib_numchannel.unsolved)",
        "n_seeds": len(seeds),
        "n_generators": len(ZOO),
        "n_presets": 2,
        "n_rows": n_rows,
        "n_screen": n_screen,
        "screen_bar": SCREEN_BAR,
        "survivors_escalated": survivors_escalated,
        "best_screen_score": round(best_screen, 4),
        "best_screen_row": best_row,
        "n_flagged_for_oracle": len(flagged),
        "flagged_for_oracle": flagged,
        "control_min_recovery": ctrl.get("min_recovery"),
        "control_all_pass": ctrl.get("all_pass"),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    json.dump(summary, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    print(f"rows={n_rows}  screens={n_screen}  best_screen={best_screen:.3f}  "
          f"escalated={survivors_escalated}  flagged={len(flagged)}  "
          f"elapsed={summary['elapsed_sec']}s")
    if flagged:
        print("!!! STOP-AND-ALERT: full-gate survivor(s) FLAGGED-FOR-ORACLE !!!")
        for f in flagged:
            print("   ", f["seed_label"], f["generator"], f["preset"], "rec", f["hit_recovery"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
