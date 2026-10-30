"""Round 36 / I1 -- power gate on the 12-register panel (Round 32 I2 machinery, nproc=1, reduced null).

Stages (checkpointed to out_gate.json, resumable):
  wk120/wk240 : beam-decode real-LP2 windows under random keys (power.py _wk_chunk logic, seed 90210); decode rune
                streams are stored so the SAME draws are scored under the 9- and 12-register panel.
  sh120       : shuffled-LP2 (permuted real LP2 stream) wrong-key null at L=120, 2000 draws, seed 36036.
  plant       : planted correct key (power.plant_trial verbatim) over held-out text, 24 reps, L in {120,240}, 12 registers.
usage: python run_gate.py [--panel models/panel12.npz] [--tag v1] [--regs GREEK,HEBREW,NORSE] [--skip-null]
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R32 = os.path.abspath(os.path.join(HERE, "..", "..", "round32", "I2-multiregister-readjudication"))
sys.path.insert(0, R32)
import power as P            # round32 power.py verbatim (imports adjudicate from R32 dir)
AJ = P.AJ; sk = P.sk; D = P.D
N = 29
argv = sys.argv
def opt(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d
PANEL = opt("--panel", os.path.join(HERE, "models", "panel12.npz"))
TEST = opt("--test", os.path.join(HERE, "models", "testhalves12.npz"))
TAG = opt("--tag", "v1")
OUT = os.path.join(HERE, f"out_gate_{TAG}.json")
pan = AJ.Panel(PANEL); AJ._PANEL = pan
REGS = pan.registers
d = np.load(TEST)
T = {r: d[r].astype(np.int64) for r in REGS}
pages = [d[f"LP1PAGE{i}"].astype(np.int64) for i in range(5)]
loo = P.lp1_loo_panels(pan)
out = json.load(open(OUT)) if os.path.exists(OUT) else {"registers": REGS, "null": {}, "plant": {}}
def save(): json.dump(out, open(OUT, "w"))
_, stream = D.load_unsolved(); stream = np.asarray(stream, dtype=np.int64)

def decode_null(L, n, seed, shuffled):
    rng = np.random.default_rng(seed)
    need = L * (P.MAX_SKIP + 1) + 512
    decs = np.empty((n, L), dtype=np.int8)
    t0 = time.time()
    for i in range(n):
        if shuffled:
            C = [int(v) for v in stream[rng.choice(len(stream), L, replace=False)]]
        else:
            s = int(rng.integers(0, len(stream) - L)); C = [int(v) for v in stream[s:s + L]]
        K = [int(v) for v in rng.integers(0, N, size=need)]
        bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=P.BEAM_W, max_skip=P.MAX_SKIP)
        decs[i] = bd["plain_idx"]
        if i % 500 == 499: print(f"  null L={L} {'shuf' if shuffled else 'wk'} {i+1}/{n}  {time.time()-t0:.0f}s", flush=True)
    return decs

def null_stats(decs):
    z = AJ.adjudicate_batch(decs.astype(np.int64), pan=pan)["z"]
    return z

if "--skip-null" not in argv:
    for name, L, n, seed, shuf in (("wk120", 120, int(opt("--nwk120", 4000)), 90210, False), ("wk240", 240, int(opt("--nwk240", 2000)), 90210, False),
                                   ("sh120", 120, 2000, 36036, True)):
        if name in out["null"]: continue
        decs = decode_null(L, n, seed, shuf)
        z = null_stats(decs)
        out["null"][name] = {"L": L, "n": n, "seed": seed, "z": np.round(z, 4).tolist()}
        save(); print("saved null", name, flush=True)

only = opt("--regs")
regs_run = only.split(",") if only else REGS
for L in (120, 240):
    for reg in regs_run:
        key = f"{reg}|{L}"
        if key in out["plant"]: continue
        rows = []
        t0 = time.time()
        for rep in range(P.NREP):
            if reg == "LP1_REAL":
                usable = [i for i, p in enumerate(pages) if len(p) >= L + 3]
                if not usable: break
                i = usable[rep % len(usable)]
                r = P.plant_trial(pages[i], L, rep, pan, lm_override=loo[i], seed_off=i * 131)
            else:
                r = P.plant_trial(T[reg], L, rep, pan)
            if r: rows.append({"z": [round(float(v), 4) for v in r["z"]], "rec": r["recovery"], "en": r["en"]})
        out["plant"][key] = rows; save()
        print(f"plant {key} n={len(rows)} {time.time()-t0:.0f}s med_rec={np.median([x['rec'] for x in rows]):.3f}", flush=True)
print("done")
