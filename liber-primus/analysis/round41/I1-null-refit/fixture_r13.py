"""R41 I1 fixture: reproduce the R13 DIRECTION family p (X1: 0.004 / 0.018 / 0.070 at block 100 / 250 / 1000, 500 draws) through the
STANDING benchmark/bars_matched.matched_shuffle (same RNG Random(60000+j)).  Imports round40 C1 machinery unchanged; writes only here.
python fixture_r13.py [draws] [blocks,comma]"""
import sys, os, json, random, time
sys.dont_write_bytecode = True
LANE = os.path.dirname(os.path.abspath(__file__)); LPD = os.path.abspath(os.path.join(LANE, "..", "..", ".."))
C1D = os.path.join(LPD, "analysis", "round40", "C1-rescore-46")
sys.path.insert(0, C1D); os.chdir(C1D)
sys.path.insert(0, os.path.join(LPD, "benchmark"))
from c1common import *            # noqa
from lib import _load             # noqa
import bars_matched as BM
Dm = _load("direction_mod_i1", os.path.join(AN, "direction", "direction.py"))
sys.path.insert(0, os.path.join(LPD, "analysis", "round40", "X1-redteam"))


def streams_of(stream):
    stream = np.asarray(stream, dtype=np.int64); out = {}
    for sname, f in Dm.STEPS.items():
        for start in range(0, 64):
            for back in (False, True):
                for skipF in (True, False): out["A:%s:s%d:b%d:f%d" % (sname, start, back, skipF)] = np.array(Dm.walk(stream, f, start, back=back, skipF=skipF), dtype=np.int64)
        for start in range(0, 32): out["B:%s:s%d" % (sname, start)] = np.array(Dm.cumwalk(stream, f, start), dtype=np.int64)
    for stride in (1, 2, 3, 5, 7, 11, 13, 29, 33, 133, 331):
        for start in range(0, 16):
            for mode in ("parity", "half"): out["C:%d:s%d:%s" % (stride, start, mode)] = np.array(Dm.signwalk(stream, stride, start, mode=mode), dtype=np.int64)
    for k, v in Dm.sieves(stream).items(): out["D:" + k] = np.asarray(v, dtype=np.int64)
    return out


D = int(sys.argv[1]) if len(sys.argv) > 1 else 500
BLOCKS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [100, 250, 1000]
Ua = np.array(U); obs = streams_of(Ua); res = json.load(open(os.path.join(LANE, "fixture_r13.json"))) if os.path.exists(os.path.join(LANE, "fixture_r13.json")) else {}
x1 = {b: json.load(open(os.path.join(LPD, "analysis", "round40", "X1-redteam", "rerun_r13_matched_BS%d.json" % b)))["blockperm_family"] for b in (100, 250, 1000)}
for BS in BLOCKS:
    wait_mem(); t = time.time()
    gen = lambda j, BS=BS: streams_of(np.array(BM.matched_shuffle(U, BS, random.Random(BM.SEED_BASE + j))))
    out = eval_family(obs, gen, D, "I1_R13_standing_blockperm%d" % BS, part=None, raw_best=True)
    o = {k: v for k, v in out.items() if not k.startswith("_")}
    res[str(BS)] = {"D": D, "p_family": o["p_family"], "exceed": o["exceed"], "best_stream": o["best_stream"], "best_Z": o["best_Z"], "null_max_Z_q99": o["null_max_Z_q99"],
                    "x1_p_family": x1[BS]["p_family"], "x1_exceed": x1[BS]["exceed"], "elapsed": round(time.time() - t, 1)}
    json.dump(res, open(os.path.join(LANE, "fixture_r13.json"), "w"), indent=1, default=float)
    print(BS, res[str(BS)], flush=True)
