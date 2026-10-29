#!/usr/bin/env python3
"""R34-P1 reader R16-KDF: re-feed payload-derived secrets through the ORIGINAL round15/KDF harness (nproc=1)."""
import os, sys, json, time, binascii
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "R16-KDF")
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round13", "B04"))
sys.path.insert(0, os.path.join(LP, "analysis", "round15", "KDF"))
import sweep as SWP, kdf, seeds as S
LOG = open(os.path.join(OUT, "run.log"), "a", encoding="utf-8")
def log(m):
    print(m, flush=True); LOG.write(m + "\n"); LOG.flush()
def save(name, obj):  # redirected: never write into round15/KDF
    json.dump(obj, open(os.path.join(OUT, f"results_{name}.json"), "w"), indent=1, default=str)
SWP.log = log; SWP.save = save
def main():
    canon = open(os.path.join(HERE, "inputs/canon/canon_256.bin"), "rb").read()
    res = open(os.path.join(HERE, "inputs/resolved/canon_256.bin"), "rb").read()
    decc = open(os.path.join(HERE, "inputs/canon/canon_256_decpref.bin"), "rb").read()
    decr = open(os.path.join(HERE, "inputs/resolved/canon_256_decpref.bin"), "rb").read()
    def pseeds(b, d):
        return [("canon256_raw", b), ("canon256_rev", b[::-1]), ("canon256_head32", b[:32]), ("canon256_tail32", b[-32:]),
                ("canon256_hex", binascii.hexlify(b)), ("canon256_hex", binascii.hexlify(b).decode().upper().encode()),
                ("canon256_decpref", d)]
    orig = [(l, s if isinstance(s, bytes) else s.encode()) for l, s in SWP.build_secrets() if l.startswith("canon256")]
    assert orig == pseeds(canon, decc), "seed reconstruction != build_secrets()"
    log("build_secrets canon256_* entries == reconstruction: %d" % len(orig))
    E_CAN, E_RES = pseeds(canon, decc), pseeds(res, decr)
    changed = [E_RES[i][0] for i in range(7) if E_RES[i][1] != E_CAN[i][1]]
    log("changed secrets: %d %s" % (len(changed), changed))
    PLANT = ("slogan", b"THE PRIMES ARE SACRED")
    head = SWP.nc.unsolved()[:SWP.HEAD_L]
    nmean, nmax = SWP.null_band(head)
    bar = max(SWP.BAR, nmax + 0.5); log("null mean %.3f max %.3f bar %.3f" % (nmean, nmax, bar))
    out = {"changed_secrets": changed, "null": [nmean, nmax], "bar": bar}
    t0 = time.time()
    # control: K2 with the resolved payload secrets + the plant secret
    g = SWP.gate_k2(E_RES + [PLANT], 1); out["control_K2"] = {"passed": g["passed"], "rank1": g["rank1"], "planted": g["planted"]}
    log("control K2 passed=%s  %.0fs" % (g["passed"], time.time() - t0))
    # published stage A top50 -> families for stage B (original run never executed B: no results_B.json)
    pubA = json.load(open(os.path.join(LP, "analysis", "round15", "KDF", "results_A.json")))
    fams = []
    for d in pubA["top50"]:
        if d["kdf"] not in fams: fams.append(d["kdf"])
        if len(fams) >= 8: break
    out["stageB_families_from_published_A"] = fams
    for tag, ents in (("canon", E_CAN), ("resolved", E_RES)):
        stA = SWP.run_stage(head, ents, kdf.KDF_NAMES, SWP.STAGE_A_SALTS, SWP.REDUCTIONS, 1, "A_" + tag)
        stB = SWP.run_stage(head, ents, fams, list(kdf.SALTS.keys()), SWP.REDUCTIONS, 1, "B_" + tag)
        for st in (stA, stB): st["top50"] = st["top50"][:5]
        out[tag] = {"A": stA, "B": stB}
        log("%s: A best %.3f (%d dec)  B best %.3f (%d dec)  over-bar A=%d B=%d" % (tag, stA["best_score"], stA["n_decodes"], stB["best_score"], stB["n_decodes"], len(stA["over_bar"]), len(stB["over_bar"])))
        save("run_" + tag, out[tag])
    out["elapsed_s"] = round(time.time() - t0, 1)
    save("summary", out)
    log("DONE %.0fs" % out["elapsed_s"])


if __name__ == "__main__":
    main()
