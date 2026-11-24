"""Addendum A5: register each window strip by its own blind read. For every window/pairwin strip, the
difflib ratio of the strip read against canon lines item_line-2 .. item_line+2 (rune tokens, best
contiguous sub-span). The line with the highest ratio is the strip's registration; a target is scored
only if that line is the target's own line and the best ratio >= 0.6 and beats the runner-up by >= 0.15.
Output: strip_registration.json"""
import difflib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src")); sys.path.insert(0, os.path.join(LP, "analysis", "stones")); os.chdir(LP)
from lp import gematria as gp; import pipeline as P
gl, po = P.global_lines(); T = gp.RUNE_TO_TRANS
pos_map = [(li, j) for li, L in enumerate(gl) for j in range(len(L))]
reads = json.load(open(os.path.join(HERE, "blind_reads.json")))["reads"]
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))["items"]
def fit(strip, line):
    c = [T[x] for x in gl[line]]; best = 0
    for s in range(0, max(1, len(c) - len(strip) + 1)):
        seg = c[max(0, s - 2): s + len(strip) + 2]
        best = max(best, difflib.SequenceMatcher(a=seg, b=strip, autojunk=False).ratio())
    return round(best, 3)
out = {}
for iid, rd in reads.items():
    if "read_strip" not in rd: continue
    rec = sealed[iid]; targets = [rec["gpos"]] if rec["kind"] == "window" else [rec["gpos"], rec["gpos"] + 1]
    for si, strip in enumerate(rd["read_strip"]):
        if len(strip) < 3: continue
        g = targets[min(si, len(targets) - 1)] if len(rd["read_strip"]) > 1 else targets[0]
        li = pos_map[g][0]
        sc = {L: fit(strip, L) for L in range(max(0, li - 2), min(len(gl), li + 3))}
        ranked = sorted(sc.items(), key=lambda kv: -kv[1]); best, second = ranked[0], ranked[1]
        ok = best[0] == li and best[1] >= 0.6 and best[1] - second[1] >= 0.15
        out[f"{iid}:{si}"] = {"item_line": li, "scores": sc, "best_line": best[0], "registered": ok}
        print(iid, si, "item_line", li, "best", best, "2nd", second, "OK" if ok else "NOT-REGISTERED")
json.dump(out, open(os.path.join(HERE, "strip_registration.json"), "w"), indent=1)
