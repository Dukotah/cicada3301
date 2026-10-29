#!/usr/bin/env python3
"""R33-B1 row R17 (round17/P3_tables pad `canon_256`).
Q5 check, then a SUPPLEMENTARY exhaustive-offset beam over the corrected pad (NOT the original harness)."""
import os, sys, json, random, time
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "R17")
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round17", "P3_tables"))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I1"))
sys.path.insert(0, os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication"))
sys.path.insert(0, os.path.join(LP, "benchmark"))
import numpy as np
import sweep as P3                       # round17/P3_tables/sweep.py (functions only; main not run)
import lib_padsweep as L
import skipdecode as sk, adjudicate as AD, null as NU
BAR_EXACT = 7.6342
canon = open(os.path.join(LP, "analysis", "pp49_51", "canon_256.bin"), "rb").read()
res = open(os.path.join(LP, "analysis", "round19", "C1", "payload_resolved.bin"), "rb").read()

# ---- Q5 check
need = {f: os.path.exists(os.path.join(LP, "data", f)) for f in ("kjv.txt", "moby.txt", "pride.txt", "war.txt")}
cache = [p for p in (os.path.join(LP, "analysis", "round17", "trigram_idx.npy"), os.path.join(LP, "analysis", "round16", "trigram_idx.npy")) if os.path.exists(p)]
padfile = os.path.join(P3.PADS, "canon_256.bin")
q5 = {"trigram_inputs_present": need, "trigram_idx_cache_found": cache, "data_pads_dir_exists": os.path.isdir(P3.PADS),
      "pad_sha_matches_manifest": None, "original_harness_rerunnable": bool(all(need.values()) or cache)}
import hashlib
man = [p for p in json.load(open(P3.MANIFEST))["pads"] if p["name"] == "canon_256"][0]
q5["pad_sha_matches_manifest"] = hashlib.sha256(canon).hexdigest() == man["sha256"]
print("Q5", json.dumps(q5), flush=True)


def sweep_pad(blob, tag):
    C = L.nc.unsolved()
    ks, meta = P3.all_keystreams(blob)
    rows, best_by = [], {}
    f = open(os.path.join(OUT, "sweep_rows%s.jsonl" % tag), "w")
    hdr = AD.header("round33/B1/R17-canon256-pad/supplementary-exhaustive" + tag, key_space="canon_256 pad, %d keystream variants x sign +-1 x EVERY valid offset (no prefilter)" % len(ks),
                    decoder="round17 lib_padsweep beam (beam_w 120, max_skip 3) on head_for(nk) runes", register_panel="round32/I2 nine-register panel",
                    n_round_adjudicated_reference=10 ** 6, NOTE="SUPPLEMENTARY; NOT the original harness (prefilter model inputs absent)")
    f.write(json.dumps(hdr) + "\n"); n = 0; flagged = []
    for vname, K in sorted(ks.items()):
        nk = int(len(K))
        if nk < 64: continue
        head = P3.head_for(nk); Kl = [int(x) for x in K]
        for sign in (-1, 1):
            for o in range(0, nk):
                if o + head * (L.MAX_SKIP + 1) + 8 >= nk: break
                bd = sk.beam_decode([int(x) for x in C[:head]], Kl, sign=sign, o=o, beam_w=L.BEAM_W, max_skip=L.MAX_SKIP)
                a = AD.adjudicate(bd["plain_idx"], translit=bd.get("translit"))
                f.write(json.dumps(AD.to_row(a, "r17:%s:s%+d:o%d:h%d" % (vname, sign, o, head))) + "\n"); n += 1
                sc, pm = float(bd["score"]), float(a["pmax"])
                if sc > best_by.get("score", -99): best_by = {"cfg": "%s s%+d o%d head%d" % (vname, sign, o, head), "score": sc, "pmax": pm, "head": bd["translit"][:40]}
                if sc >= -5.5 or pm >= BAR_EXACT: flagged.append({"cfg": "%s s%+d o%d" % (vname, sign, o), "score": sc, "pmax": pm, "FLAGGED_FOR_ORACLE": True})
    f.close()
    bp = max((json.loads(l)[3] for l in open(os.path.join(OUT, "sweep_rows%s.jsonl" % tag)).readlines()[1:]), default=None)
    v = AD.validate_store(os.path.join(OUT, "sweep_rows%s.jsonl" % tag))
    heads = sorted({P3.head_for(len(K)) for K in ks.values() if len(K) >= 64})
    return {"n_decodes": n, "n_variants": len(ks), "heads_used": heads, "best_score": best_by, "best_pmax": bp, "flagged": flagged,
            "bar_L_aware_threshold_for_N": {str(h): NU.threshold_for(max(n, 2), segment_len=h) for h in heads},
            "bar_hitfn20_exact": BAR_EXACT, "validate_store_rows": v["rows_validated"]}


def control(blob):
    """Plant English under the corrected pad's own keystreams (head-sized plant at an in-range offset); recover by exhaustive offsets."""
    P_en = sk.eng_to_idx("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND THE PILGRIM")
    out = []
    for vn in ("mod29", "hi_nibble", "lo_nibble", "byte_scaled", "mod29_rev"):
        K = L.build_keystreams(blob)[vn]; Kl = [int(x) for x in K]; nk = len(Kl); head = P3.head_for(nk)
        for o_true in (0, 2):
            P = P_en[:head]
            C, skips, _ = sk.encipher_keyskip(P, Kl[o_true:], sign=-1, supp=0.83, seed=3301)
            C = list(C)[:head]
            bests = []
            for o in range(0, nk):
                if o + head * (L.MAX_SKIP + 1) + 8 >= nk: break
                bd = sk.beam_decode(C, Kl, sign=-1, o=o, beam_w=L.BEAM_W, max_skip=L.MAX_SKIP)
                bests.append((bd["score"], o, bd))
            bests.sort(key=lambda r: -r[0]); top = bests[0]
            rec = float(np.mean([a == b for a, b in zip(top[2]["plain_idx"], P)]))
            out.append({"variant": vn, "o_true": o_true, "head": head, "recovered_offset": top[1], "score": float(top[0]), "recovery": rec,
                        "PASS": bool(top[1] == o_true and rec >= 0.95)})
            print("control", out[-1], flush=True)
    return {"plants": out, "ALL_PASS": all(p["PASS"] for p in out)}


if __name__ == "__main__":
    t0 = time.time()
    ctl = control(res)
    summ = {"Q5": q5, "control_exhaustive_offsets_on_corrected_pad": ctl}
    if ctl["ALL_PASS"]:
        summ["supplementary_canon"] = sweep_pad(canon, "_canon_comparator")
        summ["supplementary_resolved"] = sweep_pad(res, "")
        summ["published_lane_canon_256_best"] = json.load(open(os.path.join(LP, "analysis", "round17", "P3_tables", "results.json")))["per_pad"]
        summ["published_lane_canon_256_best"] = [p for p in summ["published_lane_canon_256_best"] if p["pad"] == "canon_256"][0]["best"]
    summ["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in summ.items() if k.startswith("supp")}, default=str)[:1500]); print("DONE", summ["elapsed_s"])
