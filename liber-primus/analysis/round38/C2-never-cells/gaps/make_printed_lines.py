"""G2: printed-line sums of the six solved LP1 pages (physical rune lines of data/scream314_lp.md), via the C2-R37 U4 decode path."""
import sys, os, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
mp = os.path.join(LP, "analysis", "round37", "C2-recognizer-index-readings", "U4-prime-line-sums", "measure.py")
src = open(mp, encoding="utf-8").read(); cut = src.index("ctrl_pages = ")
G = {"__file__": mp, "__name__": "m"}
exec(compile(src[:cut], "measure_head", "exec"), G)
import numpy as np
data, PR = G["data"], list(G["PR"]); inv = {int(p): i for i, p in enumerate(PR)}
order = ["Runes - 01.jpg", "03.jpg", "05.jpg", "06.jpg", "14.jpg", "73.jpg"]
out = {"parse": "physical rune lines of each solved page in data/scream314_lp.md (src/lp/corpus.py page_by_label + lines_of), plaintext via C2-R37 U4 decode_pos (simple / Vigenere+F-interrupters / phi(prime)); line value = sum over the line's positions of the plaintext rune's Gematria Primus prime (prime) or 0-based rune index (index); interrupter F positions = 0; pages in ascending label order", "pages": {}}
P, I = [], []
for lab in order:
    d = data[lab]; vals = np.array(d["plain"]); lens = G["lines_of"](lab); lens = [len(l) for l in lens]
    b = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(int)
    sp = np.add.reduceat(vals, b).tolist(); idx = np.array([inv[int(v)] if int(v) else 0 for v in vals])
    si = np.add.reduceat(idx, b).tolist()
    out["pages"][lab] = {"decode_ok": d["decode_ok"], "lens": lens, "prime_sums": sp, "index_sums": si}
    P += [int(x) for x in sp]; I += [int(x) for x in si]
out["prime_seq"] = P; out["index_seq"] = I; out["n_lines"] = len(P)
json.dump(out, open(os.path.join(HERE, "printed_lines.json"), "w"), indent=1)
print(len(P), P[:12], I[:12])
