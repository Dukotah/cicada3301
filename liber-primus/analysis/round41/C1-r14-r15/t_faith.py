"""Faithfulness check: the lane copy reproduces the archived best scores (-6.897 R14, -6.873 R15) using repo lp.score."""
import os, sys, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camp7 as C
from lp import gematria as gp, score as _score
SC = _score.default()
AR = os.path.join(C.LPD, "..", "archive", "branches-2026", "claude_master-roadmap-libra-qk527u", "liber-primus", "analysis", "campaign7")
pages = C.word_pages(); un = pages[:-2]
best = {"score": -99.0, "rec": None}; pv = {}
for variant in ("W1", "W2", "W3", "W4", "W5"):
    for sign in (-1, +1):
        for atb in (False, True):
            for pi, words in enumerate(un):
                plain = C.decrypt_variant(words, variant, sign, atb)
                s = SC.score_norm(gp.indices_to_translit(plain))
                pv[variant] = max(pv.get(variant, -99), round(s, 3))
                if s > best["score"]:
                    best.update(score=s, rec=(variant, sign, atb, pi, gp.indices_to_translit(plain)[:70]))
arch = json.load(open(os.path.join(AR, "wordsum_selfkey_results.json")))
r14 = {"copy_best": round(best["score"], 3), "copy_rec": best["rec"], "copy_per_variant": pv, "archived_best": arch["best_score"],
       "archived_rec": arch["best"], "archived_per_variant": arch["per_variant_best"],
       "match": round(best["score"], 3) == arch["best_score"] and pv == arch["per_variant_best"] and best["rec"][4] == arch["best"]["text"]}
pg2 = C.load_pages(); un2 = pg2[:-2]; whole = [i for pg in un2 for i in pg]
targets = [("p%02d" % i, pg) for i, pg in enumerate(un2)] + [("WHOLE", whole)]
hb = {"score": -99.0}; pm = {}
for (mname, vn), mat in C.hill_variants().items():
    for tn, idxs in targets:
        p = C.apply_hill(idxs, mat)
        if not p:
            continue
        s = SC.score_norm(gp.indices_to_translit(p)); k = "%s.%s" % (mname, vn)
        pm[k] = max(pm.get(k, -99), round(s, 3))
        if s > hb["score"]:
            hb.update(score=s, rec=(mname, vn, tn, gp.indices_to_translit(p)[:70]))
arch2 = json.load(open(os.path.join(AR, "hill5_magic_results.json")))
r15 = {"copy_best": round(hb["score"], 3), "copy_rec": hb["rec"], "archived_best": arch2["best_score"], "archived_rec": arch2["best"],
       "per_matrix_equal": pm == arch2["per_matrix_best"],
       "match": round(hb["score"], 3) == arch2["best_score"] and pm == arch2["per_matrix_best"] and hb["rec"][3] == arch2["best"]["text"]}
json.dump({"R14": r14, "R15": r15}, open(os.path.join(HERE, "faithfulness.json"), "w"), indent=1, default=str)
print(json.dumps({"R14_match": r14["match"], "R15_match": r15["match"], "r14": r14["copy_best"], "r15": r15["copy_best"]}))
