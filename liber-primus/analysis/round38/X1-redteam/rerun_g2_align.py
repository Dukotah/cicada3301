"""R38 X1: C2-G2 printed-line sums: is the position array aligned with the physical line lengths (the R37 U4 misalignment class)?
Uses the same measure.py head as C2's make_printed_lines.py; recomputes prime sums with an INDEPENDENT alignment (cumsum over full lens vs array length)."""
import sys, os, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
mp = os.path.join(LP, "analysis", "round37", "C2-recognizer-index-readings", "U4-prime-line-sums", "measure.py")
src = open(mp, encoding="utf-8").read(); cut = src.index("ctrl_pages = ")
G = {"__file__": mp, "__name__": "m"}; exec(compile(src[:cut], "measure_head", "exec"), G)
import numpy as np
data = G["data"]; out = {}
pl = json.load(open(os.path.join(HERE, "..", "C2-never-cells", "gaps", "printed_lines.json")))
for lab in ["Runes - 01.jpg", "03.jpg", "05.jpg", "06.jpg", "14.jpg", "73.jpg"]:
    d = data[lab]; vals = list(map(int, d["plain"])); lens = [len(l) for l in G["lines_of"](lab)]
    pos = 0; mine = []
    for L in lens:
        mine.append(sum(vals[pos:pos + L])); pos += L
    out[lab] = {"len_plain": len(vals), "sum_lens": sum(lens), "aligned_len": len(vals) == sum(lens), "n_zero_slots": sum(1 for v in vals if v == 0),
                "prime_sums_equal_C2": mine == pl["pages"][lab]["prime_sums"]}
    print(lab, out[lab])
json.dump(out, open(os.path.join(HERE, "rerun_g2_align.json"), "w"), indent=1)
