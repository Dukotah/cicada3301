#!/usr/bin/env python3
"""Oracle bundle (HUMAN-ORACLE.md section 1, as far as a single L=240 window allows) for the rows above bar_v3(N_screen, 240)."""
import os, sys
sys.dont_write_bytecode = True
HERE0 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE0)
import run_b as B
from run_b import *    # noqa

KIDS = [("U6a_N4_ks", "b5_p1_ks-1:w10000", "keyskip2"), ("U6a_N4_ks", "b5_p1_ks-1:w10000", "keyskip1"),
        ("U6a_N5", "phi_phi_prime_RI_s-1_o11:w0", "keyskip1"), ("U6a_N5", "phi_phi_prime_RI_s-1_o11:w0", "keyskip2")]
out = {"note": "flagged-for-oracle because pmax(L=240) >= bars_v3 at the SCREEN N (N5 2320, N4 168 per relation); below bars_v3 at N=1e6. Expected outcome NOISE-CROSSER (key derived from the ciphertext itself; the bars_v3 null does not re-derive the key). One window per row: the 'two independent pages' of HUMAN-ORACLE.md section 1 item 2 are NOT available, and the held-out clause was not run (see RESULTS.md)", "rows": []}
starts = [page_start(p) for p in range(55)]
for fam, cfg_w, rel in KIDS:
    C, K, sg, s = B.build(fam, cfg_w); L = min(240, len(C) - s); Cw, Kw = B.window(C, K, s, L); d, a = B.dec(Cw, Kw, rel, sg)
    page = max(i for i, st in enumerate(starts) if st <= s) if C is not None and len(C) == len(U) else None
    out["rows"].append({"kid": "%s:%s:%s" % (fam, cfg_w, rel), "reproduce": "python analysis/round38/C2-never-cells/n5n4/make_bundle.py (uses run_b.build + beam_v3 panel_max, sign %d, window start %d, L=%d, relation %s, panel-R36 sha %s)" % (sg, s, L, rel, PANEL_SHA),
                        "stream_window_start": s, "start_page_in_continuous_stream": page, "L": L, "pmax": round(float(a["pmax"]), 3), "argmax_register": REGS[a["preg"]],
                        "z_by_register": {REGS[i]: round(float(z), 2) for i, z in enumerate(a["z"])}, "pmax_ne": round(float(a["pmax_ne"]), 3),
                        "plain_idx": [int(x) for x in d["plain_idx"]], "transliteration": "".join(NC.gp.IDX_TO_TRANS[i] for i in d["plain_idx"]),
                        "bar_v3_240_N_screen": round(bar_v3({"U6a_N5": 2320, "U6a_N4_ks": 168}[fam], 240, rel), 3), "bar_v3_240_N1e6": round(bar_v3(1e6, 240, rel), 3)})
os.makedirs(os.path.join(HERE0, "oracle"), exist_ok=True)
json.dump(out, open(os.path.join(HERE0, "oracle", "bundle.json"), "w"), indent=1)
for r in out["rows"]: print(r["kid"], r["pmax"], r["argmax_register"], r["transliteration"][:90])
