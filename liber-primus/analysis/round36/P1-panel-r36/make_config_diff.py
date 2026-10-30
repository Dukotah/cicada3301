"""P1: engine_config_diff.txt = unified diff of (Round 27 engine inputs as export_data.py writes them, reconstructed from vectors.json + the recorded R19 panel hash)
vs (engine_inputs_copy/engine.dat), plus the grind27.c diff and the sweep_plan check."""
import difflib, hashlib, json, os, sys
sys.dont_write_bytecode = True
LANE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(LANE, "..", "..", ".."))
v = json.load(open(os.path.join(LP, "analysis/round27/P0-spec/vectors.json"))); c = v["constants"]
R19 = "14a23d3619fa02dfb6aa20efafdd0fc0ff633c83d8dc5f02ac4d5d035b996297"
L = ["GRIND27DATA 1", "PANEL_SHA256 " + R19, "PANEL_PATH <abs>/panel_lm.f32", "QGRAM_PATH <abs>/data/english_quadgrams.txt", "QGRAM_TOTAL %d" % c["quadgram"]["total"],
     "QGRAM_FLOOR " + c["quadgram"]["floor"], "QGRAM_NENTRIES %d" % c["quadgram"]["n_entries"], "NREG %d" % len(c["registers"]),
     "MU " + " ".join(c["panel_mu_n120"]), "SD " + " ".join(c["panel_sd_n120"]), "CAND_BAR %r" % float(c["SCREEN_BAR"]),
     "CLAIM_BAR_PAIR " + c["claim_bar_pair_1e6"], "CLAIM_BAR_EXACT 7.6341931878728095"]
cs = v["ciphertext"]["C_SCREEN"]; L += ["CSCREEN %d" % len(cs), " ".join(map(str, cs))]
pa = v["planted_stage_a"]
L += ["PLANT_SEED %d" % pa["seed"], "PLANT_PMAX " + pa["pmax"], "PLANT_CIPHER %d" % len(pa["cipher_idx_120"]), " ".join(map(str, pa["cipher_idx_120"])),
      "PLANT_PLAIN %d" % len(pa["plain_idx"]), " ".join(map(str, pa["plain_idx"]))]
sv = v["seed_vectors"]; L.append("NVEC %d" % len(sv))
for r in sv:
    L += ["VEC %d %s %s %d %d %d" % (r["seed"], r["pmax"], r["beam_score"], r["ptr_end"], r["n_skips"], r["nchars"]), "KS " + " ".join(map(str, r["ks128"])),
          "PLAIN " + " ".join(map(str, r["plain_idx"]))]
L.append("END")
new = open(os.path.join(LANE, "engine_inputs_copy/engine.dat")).read().splitlines()
# normalise the two path lines (absolute in the old export, relative in the copy) so only substantive changes show
old = [l.replace("<abs>/", "") for l in L]
def clip(l): return l if len(l) < 230 else l[:200] + " ...[%d chars]" % len(l)
out = ["# engine_config_diff.txt - Round 36 / P1.  Live Round 27 files are untouched; this is the diff of the COPY in engine_inputs_copy/.",
       "# engine.dat.R27 is RECONSTRUCTED (export_data.py output format, vectors.json fields, recorded R19 panel sha) - the real engine.dat was never committed (regenerable, gitignored).",
       "# Long lines are clipped for readability; unchanged KS/PLAIN/CSCREEN/PLANT_CIPHER/PLANT_PLAIN lines do not appear.", ""]
out += [clip(l) for l in difflib.unified_diff(old, new, "engine.dat.R27 (reconstructed)", "engine_inputs_copy/engine.dat", n=0, lineterm="")]
out += ["", "# ---- grind27.c : round27/P1-engine/grind27.c -> engine_inputs_copy/grind27.c ----"]
a = open(os.path.join(LP, "analysis/round27/P1-engine/grind27.c"), encoding="utf-8", errors="replace").read().splitlines()
b = open(os.path.join(LANE, "engine_inputs_copy/grind27.c"), encoding="utf-8", errors="replace").read().splitlines()
out += list(difflib.unified_diff(a, b, "round27/P1-engine/grind27.c", "engine_inputs_copy/grind27.c", n=0, lineterm=""))
sp = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
out += ["", "# ---- sweep_plan.json: UNCHANGED (sha256 %s == %s). claim_bar S1=7.3835.. S2=7.6341.. are Round-19-panel quantities and are NOT recalibrated (see GATE-CHANGE.md, decision D1)." %
        (sp(os.path.join(LP, "analysis/round27/sweep_plan.json"))[:16], sp(os.path.join(LANE, "engine_inputs_copy/sweep_plan.json"))[:16]),
        "# ---- gate hash: PANEL_SHA256 %s (Round 19 panel_lm.f32) -> see engine.dat diff above (panel-R36 panel_lm.f32)." % R19[:16],
        "# ---- new file engine_inputs_copy/check_panel_gate.py: grind27.c never compares PANEL_SHA256 to the file, so the gate is enforced by this script before --self-test.",
        "# ---- NOT changed: CAND_BAR 5.0, CLAIM_BAR_PAIR, CLAIM_BAR_EXACT, quadgram constants, ciphertext, ks128/plain_idx/beam_score/ptr_end/n_skips/nchars of every V1 vector, PLANT_* cipher/plain."]
open(os.path.join(LANE, "engine_config_diff.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(out), "lines")
