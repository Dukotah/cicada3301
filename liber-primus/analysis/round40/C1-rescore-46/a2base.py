"""R28 follow-up: natural-English baseline for word-last / word-first streams (the matched control the shuffled nulls lack)."""
import os, sys, json, random
from c1common import *
from lib import _mapc, _load
M = _mapc(); words = M.solved_english_words()
ad = os.path.join(AN, "round23", "A2-line-acrostic"); sys.path.insert(0, ad)
S = _load("lib_selfread", os.path.join(AN, "round22", "A-selfembedded-read", "lib_selfread.py"))
G = _load("lib_geom", os.path.join(ad, "lib_geom.py")); RS = _load("a2_run_sweep", os.path.join(ad, "run_sweep.py"))
pages = G.load_all_pages(); cands = dict(RS.enumerate_candidates(pages))
summ = json.load(open(F("parts", "R28_R23A2_line_acrostic_ownhist.done")))
def rs(l): return np.array(S._greedy_translit_to_indices(l), dtype=np.int64)
out = {"n_english_words": len(words), "streams": {}}
for desc in ("CONCAT|word_last|rev", "CONCAT|word_last|fwd", "06|word_last|rev", "CONCAT|word_first|fwd", "CONCAT|word_first|rev", "CONCAT|line_last|fwd"):
    L = cands[desc]; obs = rs(L); n_obs = len(obs)
    kind = "last" if "last" in desc else "first"; rev = desc.endswith("rev")
    seq = "".join((w[-1] if kind == "last" else w[0]) for w in words if w.isalpha())
    seq = seq[::-1] if rev else seq
    # windows of the same LETTER length over the natural English word-final/initial stream
    nl = len(L); vals = []
    for st in range(0, max(1, len(seq) - nl), max(1, nl // 4)):
        w = seq[st:st + nl]
        if len(w) == nl: vals.append(pm_many({"x": rs(w)})["x"])
    vals = np.array(vals); po = pm_many({"x": obs})["x"]
    out["streams"][desc] = {"letters": nl, "runes": n_obs, "obs_pmax": round(po, 3), "natural_windows": len(vals), "natural_mean": round(float(vals.mean()), 3) if len(vals) else None,
                            "natural_max": round(float(vals.max()), 3) if len(vals) else None, "natural_q95": round(float(np.quantile(vals, .95)), 3) if len(vals) else None,
                            "frac_natural_ge_obs": round(float((vals >= po).mean()), 3) if len(vals) else None}
    print(desc, out["streams"][desc], flush=True)
json.dump(out, open(F("a2_natural_baseline.json"), "w"), indent=1)
