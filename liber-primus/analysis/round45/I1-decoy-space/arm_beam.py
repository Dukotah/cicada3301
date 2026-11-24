"""R45 I1 arm_beam: beam_v3 panel_max + panel-R36 + bars_v3 (the oracle pipeline) and the pf_v4_12 head screen,
correct key handed over, under conditions a-d (printed spaces altered, rune stream in order) and e (word-shuffled
stream).  Conditions a-d are run LITERALLY: the ciphertext page is rendered as a canon-style string with '-' word
separators placed by the condition's length sequence, then parsed back the way the repo's page loaders do
(rune characters only) before decoding.   python -I arm_beam.py   -> out_beam.json"""
import os, sys, json, time, random, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common45 as G
import numpy as np
from lp.gematria import RUNE_TO_IDX, IDX_TO_RUNE

sys.path.insert(0, G.AN("round33", "I1-register-aware-beam"))
import beam_v3 as V
PANEL_PATH = os.path.join(G.LP, "data", "panels", "panel-r36.npz")
V.set_panel(PANEL_PATH)
AD = V.A
PAN = AD.Panel(PANEL_PATH); V._PAN = PAN
assert len(PAN.registers) == 12
B2 = V.B2
sys.path.insert(0, G.AN("round34", "I1-v3-null"))
from bars_v3 import bar_v3
PF = G._load("pf_v4_12", G.AN("round37", "I2-pfv4-12reg", "pf_v4_12.py"))

OUT = os.path.join(HERE, "out_beam.json")
NPL = 20
CELLS = [(reg, enc, L) for reg in ("EN", "EN_NOVOWEL") for enc in ("keyskip1", "skip_by_two") for L in (120, 240)]
ADV = {"keyskip1": 1, "skip_by_two": 2}
BREL = {"keyskip1": "keyskip1", "skip_by_two": "keyskip2"}
CONDS = ("a", "b", "c", "d", "e")


def render(C, lens):
    """canon-style page string: runes in order, '-' at the condition's word boundaries."""
    out, i = [], 0
    for l in lens:
        if i >= len(C):
            break
        out.append("".join(IDX_TO_RUNE[x] for x in C[i:i + l])); i += l
    if i < len(C):
        out.append("".join(IDX_TO_RUNE[x] for x in C[i:]))
    return "-".join(out)


def parse(s):
    return [RUNE_TO_IDX[c] for c in s if c in RUNE_TO_IDX]


def pf_pass(C, K, a):
    m, k = PF.FROZEN["m"], PF.FROZEN["k"]
    Cc = np.array(C[:m], dtype=np.int32).reshape(m, 1)
    Kc = np.array(K[:m + a * k], dtype=np.int32).reshape(-1, 1)
    s = float(PF.dp_cols(Cc, Kc, k, a, PF.FROZEN["pen_a%d" % a], m)[0])
    return s, bool(s > PF.FROZEN["thr"]["a%d" % a])


def run():
    t0 = time.time(); res = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "panel_sha_ok": True, "cells": {}}
    if os.path.exists(OUT):
        res["cells"] = json.load(open(OUT)).get("cells", {})           # resume: completed cells are kept
    for reg, enc, L in CELLS:
        if "%s|%s|L%d" % (reg, enc, L) in res["cells"]:
            continue
        words_all = G.text_words("pride.txt", novowel=(reg == "EN_NOVOWEL"))
        b6 = bar_v3(1e6, L, BREL[enc]); b1 = bar_v3(1, L, BREL[enc])
        rows = []
        for s in range(NPL):
            rng = random.Random(4500 + 1000 * CELLS.index((reg, enc, L)) + s)
            pw = G.page_words(words_all, L, rng)
            true_lens = G.cut_lens([len(w) for w in pw], L)
            P_in = G.flat(pw)[:L]
            P_sh = G.flat(G.shuffle_words(pw, rng))[:L]
            K = B2.sha_ctr_key(L * 12 + 2048, seed=("R45I1-%d" % s).encode())
            row = {"seed": s}
            open(os.path.join(HERE, "heartbeat.txt"), "w").write("%s arm_beam %s %s L%d plant %d\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), reg, enc, L, s))
            for cond in CONDS:
                P = P_sh if cond == "e" else P_in
                C, info = B2.ENCIPHER[enc](P, K, 0.83, 3301 + s)
                lens = true_lens if cond == "e" else G.cond_lengths(cond, true_lens, rng, L)
                page = render(C, lens)
                Cp = parse(page)
                assert Cp == list(C)
                d = V.beam_decode_v3(Cp, K, ADV[enc], "panel_max", sign=-1, o=0, tau=0.0, lam_u=4.0)
                a = AD.adjudicate(d["plain_idx"], pan=PAN)
                rec = float(B2.recovery(d["plain_idx"], P))
                pm = float(a["pmax"])
                pfs, pfp = pf_pass(C, K, ADV[enc])
                row[cond] = {"rec": round(rec, 4), "pmax": round(pm, 3), "preg": PAN.registers[int(a["preg"])],
                             "hash": G.h(d["plain_idx"]), "n_seps": page.count("-"),
                             "pow1e6": bool(rec >= 0.90 and pm >= b6), "pow1": bool(rec >= 0.90 and pm >= b1),
                             "pf_lse": round(pfs, 3), "pf_pass": pfp}
            row["abcd_identical"] = len({row[c]["hash"] for c in "abcd"}) == 1 and len({row[c]["pmax"] for c in "abcd"}) == 1
            rows.append(row)
            if s == 9 and not all(r["abcd_identical"] for r in rows):
                print("Q5: a-d NOT identical on first 10 plants", reg, enc, L, flush=True)
        cell = {"register": reg, "enc": enc, "advance": ADV[enc], "L": L, "n": len(rows), "bar_1e6": round(b6, 3),
                "bar_N1": round(b1, 3), "abcd_identical_frac": sum(r["abcd_identical"] for r in rows) / len(rows), "cond": {}}
        for cond in CONDS:
            rr = [r[cond] for r in rows]
            k6 = sum(x["pow1e6"] for x in rr); k1 = sum(x["pow1"] for x in rr); kp = sum(x["pf_pass"] for x in rr)
            pairs = [(rr[2 * j]["pow1"] and rr[2 * j + 1]["pow1"]) for j in range(len(rr) // 2)]
            cell["cond"][cond] = {"median_rec": float(np.median([x["rec"] for x in rr])), "mean_rec": round(float(np.mean([x["rec"] for x in rr])), 4),
                                  "median_pmax": float(np.median([x["pmax"] for x in rr])),
                                  "power_1e6": k6 / len(rr), "power_1e6_wilson": G.wilson(k6, len(rr)),
                                  "power_N1": k1 / len(rr), "oracle_pass_pairs": "%d/%d" % (sum(pairs), len(pairs)),
                                  "pf_power": kp / len(rr), "pf_wilson": G.wilson(kp, len(rr))}
        cell["rows"] = rows
        res["cells"]["%s|%s|L%d" % (reg, enc, L)] = cell
        c = cell["cond"]
        print("%-10s %-11s L%d  a-d identical %.2f | pow1e6 a %.2f e %.2f | rec a %.3f e %.3f | pf a %.2f e %.2f  %.0fs" % (
            reg, enc, L, cell["abcd_identical_frac"], c["a"]["power_1e6"], c["e"]["power_1e6"], c["a"]["median_rec"], c["e"]["median_rec"],
            c["a"]["pf_power"], c["e"]["pf_power"], time.time() - t0), flush=True)
        json.dump(res, open(OUT, "w"), indent=1)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    run()
