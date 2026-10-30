#!/usr/bin/env python3
"""Round 36 / P1 - engine inputs re-pointed at panel-R36 (COPY of round27/P1-engine/export_data.py's output format).

Reads (never writes): analysis/round27/P0-spec/vectors.json  and  ../build1/panel12.npz (panel-R36).
Writes next to this file: engine.dat, panel_lm.f32 (12 x 24389 LE float32, register-major), rescore_r36.json.

What changes vs the Round 27 engine inputs, and why that is all that can change:
  * LM table / NREG / MU / SD (n=120)       -> panel-R36 (12 registers).
  * PANEL_SHA256                            -> sha256 of the new panel_lm.f32 blob.
  * V1 `pmax` x64 and PLANT_PMAX            -> RE-SCORED with the engine's own formula from the stored plain_idx.
  * everything else (ks128, plain_idx, beam_score, ptr_end, n_skips, nchars, ciphertext, quadgram constants, CAND_BAR,
    CLAIM_BAR_*) is carried unchanged: the beam decode uses quadgram scores only (driftbeam imports lp.gematria / lp.score,
    no panel), so the decoded plaintext of each seed is panel-independent; only the panel-max z of that plaintext moves.
  * CLAIM bars are NOT recalibrated here (they are Gumbel-cell quantities of the Round 19 panel's null) - see GATE-CHANGE.md.
"""
import hashlib, json, os, sys
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication"))
import adjudicate as AJ
VECTORS = os.path.join(LP, "analysis", "round27", "P0-spec", "vectors.json")
PANEL = os.path.abspath(os.path.join(HERE, "..", "build1", "panel12.npz"))
NTRI = 29 ** 3

def main():
    v = json.load(open(VECTORS)); c = v["constants"]
    assert c["PRESET"] == "pair" and c["MODE"] == "random29" and c["L_SCREEN"] == 120 and c["SCREEN_BEAM_W"] == 64
    pan = AJ.Panel(PANEL); R = pan.R
    assert R == 12 and pan.LMF.shape == (12, NTRI) and pan.LMF.dtype == np.float32
    blob = np.ascontiguousarray(pan.LMF).astype("<f4").tobytes()
    open(os.path.join(HERE, "panel_lm.f32"), "wb").write(blob)
    sha_lm = hashlib.sha256(blob).hexdigest()
    mu, sd = pan.cal(120)[:2]
    mu0 = np.array([float(x) for x in c["panel_mu_n120"]]); sd0 = np.array([float(x) for x in c["panel_sd_n120"]])

    def pmax_of(plain):
        p = np.asarray(plain, dtype=np.int64)
        f = p[:-2] * 841 + p[1:-1] * 29 + p[2:]
        acc = np.zeros(R)
        for t in f:                                  # sequential double accumulation of float32 entries, as grind27.c does
            acc += pan.LMF[:, t].astype(np.float64)
        z = (acc / 118.0 - mu) / sd
        return float(z.max()), int(z.argmax())

    L = ["GRIND27DATA 1", "PANEL_SHA256 " + sha_lm, "PANEL_PATH panel_lm.f32", "QGRAM_PATH english_quadgrams.txt",
         "QGRAM_TOTAL %d" % c["quadgram"]["total"], "QGRAM_FLOOR " + c["quadgram"]["floor"], "QGRAM_NENTRIES %d" % c["quadgram"]["n_entries"],
         "NREG %d" % R, "MU " + " ".join(repr(float(x)) for x in mu), "SD " + " ".join(repr(float(x)) for x in sd),
         "CAND_BAR %r" % float(c["SCREEN_BAR"]), "CLAIM_BAR_PAIR " + c["claim_bar_pair_1e6"],
         "CLAIM_BAR_EXACT 7.6341931878728095"]
    cs = v["ciphertext"]["C_SCREEN"]; L += ["CSCREEN %d" % len(cs), " ".join(map(str, cs))]
    pa = v["planted_stage_a"]; pm_new, pm_arg = pmax_of(pa["plain_idx"])
    L += ["PLANT_SEED %d" % pa["seed"], "PLANT_PMAX " + repr(pm_new),
          "PLANT_CIPHER %d" % len(pa["cipher_idx_120"]), " ".join(map(str, pa["cipher_idx_120"])),
          "PLANT_PLAIN %d" % len(pa["plain_idx"]), " ".join(map(str, pa["plain_idx"]))]
    sv = v["seed_vectors"]; L.append("NVEC %d" % len(sv))
    rows = []
    for r in sv:
        pn, arg = pmax_of(r["plain_idx"])
        rows.append({"seed": r["seed"], "pmax_r19": float(r["pmax"]), "pmax_r36": pn, "argmax_register_r36": pan.registers[arg]})
        L.append("VEC %d %s %s %d %d %d" % (r["seed"], repr(pn), r["beam_score"], r["ptr_end"], r["n_skips"], r["nchars"]))
        L.append("KS " + " ".join(map(str, r["ks128"]))); L.append("PLAIN " + " ".join(map(str, r["plain_idx"])))
    L.append("END")
    open(os.path.join(HERE, "engine.dat"), "w").write("\n".join(L) + "\n")
    d = np.array([x["pmax_r36"] - x["pmax_r19"] for x in rows])
    out = {"panel_R36_npz_sha256": hashlib.sha256(open(PANEL, "rb").read()).hexdigest(), "panel_lm_f32_sha256": sha_lm,
           "r19_panel_lm_f32_sha256_in_live_engine": "14a23d3619fa02df...",
           "mu_n120_r36": mu.tolist(), "sd_n120_r36": sd.tolist(), "mu_n120_r19_first9": mu0.tolist(), "sd_n120_r19_first9": sd0.tolist(),
           "registers": pan.registers, "plant": {"seed": pa["seed"], "pmax_r19": float(pa["pmax"]), "pmax_r36": pm_new, "argmax": pan.registers[pm_arg], "cand_bar": float(c["SCREEN_BAR"])},
           "v1_rows": rows, "v1_delta_pmax": {"min": float(d.min()), "median": float(np.median(d)), "max": float(d.max()), "n_changed_gt_1e-9": int((np.abs(d) > 1e-9).sum())}}
    json.dump(out, open(os.path.join(HERE, "rescore_r36.json"), "w"), indent=1)
    print("panel_lm.f32 sha256", sha_lm); print("plant pmax r19 %.12f -> r36 %.12f (%s)" % (float(pa["pmax"]), pm_new, pan.registers[pm_arg]))
    print("V1 delta pmax", out["v1_delta_pmax"])

if __name__ == "__main__":
    main()
