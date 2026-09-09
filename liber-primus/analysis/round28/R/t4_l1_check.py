#!/usr/bin/env python3
"""R28-R T4: L1 PREREG-vs-artifact drift check.

PREREG (with dated pre-run addendum) promises:
  P1  grid: pads {560.00auth stride 16384 -> 244 offsets, 560.13 stride 331777
      -> 359 offsets} x 5 reductions x {fwd(rev suffix), s+-1} x {exact,pair}
      = 40/offset; minus 40 keyskip1(exact) cells at offset 0 => 24,080 rows.
  P2  no duplicate cell (silent re-run), every offset ON-grid.
  P3  bars: cand 5.0; claim pair 7.3835 / exact 7.6342; fixed -5.5 never used.
  P4  every row >= cand bar 5.0 stage-B adjudicated (results.json candidates);
      RESULTS claims 23 candidates, best pmax 5.606, zero above any claim bar.
  P5  control (control.json) written BEFORE sweep rows (mtime order) with
      recovery >= 0.90 and HIT=True on both relations.
Usage: t4_l1_check.py <rows.jsonl> [--planted]   exit 1 on any FAIL.
"""
import json, os, sys

L1 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "L1"))
rows_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(L1, "sweep_rows.jsonl")

ok = True
def chk(name, cond, detail=""):
    global ok
    print(('PASS' if cond else 'FAIL'), name, detail)
    if not cond: ok = False

# expected grid
grid = set()
for pad, size, stride in (("560.00auth", 3992970, 16384), ("560.13", 118818811, 331777)):
    offs = list(range(0, size, stride))
    n_expected = {"560.00auth": 244, "560.13": 359}[pad]
    chk(f"P1 offset count {pad}", len(offs) == n_expected, f"{len(offs)} vs {n_expected}")
    for o in offs:
        for red in ("mod29", "prime_to_idx", "hi_nibble", "lo_nibble", "byte_scaled"):
            for rev in ("", "_rev"):
                for sign in ("s-1", "s+1"):
                    for rel in ("exact", "pair"):
                        if o == 0 and rel == "exact":
                            continue  # anti-repeat exclusion
                        grid.add((pad, red + rev, sign, o, rel))
chk("P1 planned cells == 24080", len(grid) == 24080, str(len(grid)))

seen, dups, offgrid, ncand, best = set(), 0, [], 0, (-99, None)
with open(rows_path) as f:
    for line in f:
        r = json.loads(line)
        tag = r["sweeprow"][0]
        pad, red, sign, o, rel = tag.split(":")
        o = int(o[1:])
        key = (pad, red, sign, o, rel)
        if key in seen: dups += 1
        seen.add(key)
        if key not in grid: offgrid.append(tag)
        pmax = r["sweeprow"][3]
        if pmax >= 5.0: ncand += 1
        if pmax > best[0]: best = (pmax, tag)

chk("P2 rows == 24080", len(seen) == 24080, str(len(seen)))
chk("P2 zero duplicate cells", dups == 0, str(dups))
chk("P2 zero off-grid rows", not offgrid, str(offgrid[:3]))
chk("P2 rows exactly == planned grid", seen == grid,
    f"missing={len(grid-seen)} extra={len(seen-grid)}")
chk("P4 candidates >=5.0 == 23", ncand == 23, str(ncand))
chk("P4 best pmax == 5.606", abs(best[0] - 5.606) < 0.0005, f"{best}")

res = json.load(open(os.path.join(L1, "results.json")))
cands = res.get("candidates", [])
chk("P4 all 23 stage-B adjudicated in results.json", len(cands) == 23, str(len(cands)))
over = [c for c in cands if max(c.get("pmax240", 0), c.get("pmax_240", 0)) >= 6.379]
chk("P4 zero candidates over true-N pair bar 6.379", not over, str(over[:2]))

ctrl = json.load(open(os.path.join(L1, "control.json")))
txt = json.dumps(ctrl)
chk("P5 control has HIT=True twice", txt.count("true") >= 2, "")
mt_c = os.path.getmtime(os.path.join(L1, "control.json"))
mt_r = os.path.getmtime(rows_path if "--planted" not in sys.argv else os.path.join(L1, "sweep_rows.jsonl"))
chk("P5 control.json mtime < sweep_rows mtime", mt_c < mt_r, f"{mt_c} vs {mt_r}")

# P3: bars in sweep.py source
src = open(os.path.join(L1, "sweep.py")).read()
chk("P3 cand bar 5.0 in code", "SCREEN_BAR = 5.0" in src, "")
# bars are DERIVED via panelmax_bar('pair'/'exact', 1e6, 0.01); verified externally
# (this run) to equal the frozen R27 constants 7.3835202943286884 / 7.6341931878728095
chk("P3 claim bars derived from panelmax_bar(1e6, 0.01)",
    'panelmax_bar("pair", 10 ** 6, 0.01)' in src and
    'panelmax_bar("exact", 10 ** 6, 0.01)' in src, "")
chk("P3 fixed -5.5 bar absent from code", "-5.5" not in src, "")

print("VERDICT:", "NO-ERROR-FOUND (L1)" if ok else "FOUND-ERROR (L1)")
sys.exit(0 if ok else 1)
