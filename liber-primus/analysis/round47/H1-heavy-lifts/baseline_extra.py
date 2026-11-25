"""R47-H1: C8 baselines on two registers derived from English held-out text (stoker_dracula), through the full
C8 protocol (plant + reference-beam decode, four null classes): vowel-dropped English (a panel register,
EN_NOVOWEL; replicates L7-A for the English scorer) and reversed English (not in panel-R36; an illustration of
a register the incumbent does not model). Writes baseline_extra.json.  python -I baseline_extra.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "challenges")))
import _heavy as H
import c8_register_scorer as C8

VOWELS = {18, 24, 10, 3, 1, 26, 25, 22, 12, 27, 28}     # E A I O U Y AE OE EO IA EA
eng = H.latin_text_to_idx("data/keys/armada19/stoker_dracula.txt")
out = {"seed": 4705, "source": "data/keys/armada19/stoker_dracula.txt"}
for name, st in (("EN_NOVOWEL (vowel runes removed)", [x for x in eng if x not in VOWELS]),
                 ("EN_REVERSED (not in panel-R36)", eng[::-1])):
    sets = C8.build(st, 4705, 200, 2000, 500, False)
    out[name] = {}
    for nm, sc in (("english_reference", H.english_score), ("panel_r36_pmax", H.panel_pmax)):
        r = C8.evaluate(sc, sets)
        C8.show(f"{name} / {nm}", r)
        out[name][nm] = {str(L): {k: v for k, v in x.items() if k != "threshold"} for L, x in r.items()}
json.dump(out, open(os.path.join(HERE, "baseline_extra.json"), "w"), indent=1)
