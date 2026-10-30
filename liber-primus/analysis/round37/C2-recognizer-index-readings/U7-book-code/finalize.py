import json
r = json.load(open('results.json')); S = r['selections']; C = r['controls']
L = []
L.append("# RESULTS - R37 C2-U7 book-code indices (signed numeric strings as indices)\n")
L.append("PREREG.md (+Addendum 1) written first. Panel-R36, statistic pmax_ne, two nulls (random-index over the scheme alphabet; order-shuffle), M=2000 each, refine 100k/20k if p<=0.005. Family bar 0.01/320 = 3.1e-5. Runtime 31 s.\n")
L.append("## Planted controls (before the sweep)\n| control | n runes | real pmax_ne | p_a (order) | p_b (index null) | null max | verdict |\n|---|---|---|---|---|---|---|")
for k, lab, plant in [('A_LP1_R_triple', 'A: 60-rune LP1 phrase via 3-digit list into LP1 runes', 1), ('A0_random_digits', 'A0: random 3-digit list, same scheme', 0),
                      ('B_LP1_W_triple', 'B: LP1 sentence "THE PRIMES ARE SACRED..." via word indices (W readout)', 1), ('B0_random', 'B0: random word indices', 0),
                      ('C_UNS_F_triple', 'C: 60-rune phrase via first-rune-of-UNS-word indices', 1), ('C0_random', 'C0: random indices', 0)]:
    v = C[k]
    if plant:
        ok = 'PASS' if v['p_gate'] <= 0.002 else 'FAIL'
    else:
        ok = 'ok (not detected)' if v['p_gate'] > 0.01 else 'FALSE POSITIVE'
    L.append(f"| {lab} | {v['n']} | {v['real']:.2f} | {v['p_a']:.4g} | {v['p_b']:.4g} | {v['null_max']:.2f} | {ok} |")
L.append("\nControls A and C (R / F readouts) PASS at the p floor (5e-4 at M=2000); random-index controls are not detected. **Control B FAILS** (p 0.065 / 0.022): a whole-LP1-word readout is not separable from random LP1 words under the panel, because the panel's LP1_REAL register already contains LP1's words, so any bag of LP1 words scores high (null max 16.6 vs real 14.5). The word-W readout (80 cells) is therefore UNPOWERED for LP1 and untested for UNS; those cells are inconclusive, not negative. R/F cells (240) are powered at n>=~40 (controls at n=56-60).\n")
L.append("## Scheme table (best p_gate = max(p_a,p_b); bar = 0.01/N_group; family bar 3.1e-5)\n| target | digit scheme | readouts | N | best p_gate | real pmax_ne (null max) at best | n at best | cells with n<30 (unpowered) | bar 0.01/N |\n|---|---|---|---|---|---|---|---|---|")
for tgt in ('LP1', 'UNS'):
    for sc in ('pair', 'triple', 'single', 'whole'):
        for lab, cond in (('R,F-word,F-line', lambda x: x['readout'] != 'word-W'), ('W (UNPOWERED)', lambda x: x['readout'] == 'word-W')):
            s = [x for x in S if x['target'] == tgt and x['scheme'] == sc and cond(x)]
            b = min(s, key=lambda x: x['p_gate'])
            L.append(f"| {tgt} | {sc} | {lab} | {len(s)} | {b['p_gate']:.3g} | {b['real']:.2f} ({b['null_max']:.2f}) | {b['n']} | {sum(x['n'] < 30 for x in s)} | {0.01 / len(s):.2g} |")
fl = r['flagged']
L.append(f"\nSelections swept: {r['N']}. Selections refined (p_gate <= 5e-3): {sum(1 for x in S if x.get('refined'))}. **Flagged (p <= {r['bar_fw']:.2g}): {len(fl)}.** Smallest p_gate overall: {min(x['p_gate'] for x in S):.3g} (consistent with noise over 320 cells).\n")
L.append("Lowest five p_gate cells (all noise level, none readable):\n")
for x in sorted(S, key=lambda x: x['p_gate'])[:5]:
    L.append(f"- {x['string']} {x['scheme']} {x['target']} {x['readout']} base{x['base']} rev{x['rev']} n={x['n']} p={x['p_gate']:.3g}: `{x['text'][:60]}`")
L.append("\n## Verdict\nNEGATIVE for the 240 powered (R / F-word / F-line) selections: no signed numeric string (P.S. integer, `@1231507051321`, location numbers) retrieves, under any enumerated pair/triple/single/whole x 0/1-based x forward/reversed index scheme into LP1 plaintext or the LP2 rune stream, a letter string the 12-register panel separates from either null. 80 W-readout cells INCONCLUSIVE (control B failed). No oracle bundle: nothing cleared the family-wise bar.\n")
L.append("## Three conditionals\n1. **Rule space:** exactly the 320 enumerated selections (mod-wrap indexing, non-overlapping digit groups). Not covered: page:line:char addressing, the reverse direction into Mabinogion/KJV/other books, overlapping/sliding digit windows, other radices, per-block short strings, the colon-list book-code messages.\n2. **Decoder:** verbatim retrieval with mod wrap; a different edition/transliteration of LP1 (here: koans file, greedy digraph parse, K->C V->U) or a skip/offset convention is missed.\n3. **Adjudicator:** panel-R36 pmax_ne trigram z; powered only for n>=~40 runes (A: 60, C: 56). S2 (@1231507051321) gives n=4-13 under pair/triple/single and the 10 whole-number block selections n=10: essentially unpowered. Word-whole readouts unpowered (control B).\n")
L.append("## not_covered\npage:line:char; reverse-direction books; W readout power; S2 / whole-number short selections; n-th-letter-of-word schemes.\n")
L.append("## Files\nPREREG.md, u7.py, finalize.py, results.json (all 320 rows + controls), run.log, ledger.json, RESULTS.md\n")
open('RESULTS.md', 'w').write("\n".join(L))
led = {"$comment": "written by R37 C2-U7 lane agent", "entries": [
    {"id": "R37-C2-U7-BOOK-CODE", "round": 37, "lane": "C2-U7", "date": "2026-10-30", "status": "negative", "positive_control": "passed",
     "control_detail": "A (60-rune LP1 phrase via triple-digit list into LP1 runes) p=5e-4 floor; C (60-rune phrase via UNS word-first-rune indices) p=5e-4 floor; random-index controls not detected. R/F readouts only.",
     "hypothesis": "The signed numeric strings (P.S. integer, @1231507051321, location numbers) are book-code indices into LP1 plaintext / the LP2 rune stream.",
     "coverage": "240 powered selections: 3 strings (S1,S2,LOC) x pair/triple/single (+LOCW whole) x {LP1,UNS} x {rune, first-rune-of-word, first-rune-of-line} x 0/1-based x reversed; panel-R36 pmax_ne vs index-alphabet null and order-shuffle null, M=2000 (refine 100k/20k), family bar 3.1e-5 over 320.",
     "result": "0 selections flagged; best p_gate 0.027 (noise level).", "threshold": "p_gate<=0.01/320 after refinement",
     "power": "controls at n=56-60 detected at the p floor; S2 and whole-number selections (n<=13) unpowered",
     "conditionals": ["rule space: 320 enumerated selections only; no page:line:char, no reverse-direction books", "decoder: verbatim mod-wrap retrieval from koans-file LP1 transliteration", "adjudicator: panel-R36 pmax_ne, powered only n>=~40"],
     "not_covered": ["page:line:char addressing", "indices into non-LP books", "overlapping digit windows / other radices", "short-selection power"],
     "artifacts": ["PREREG.md", "u7.py", "results.json", "RESULTS.md", "run.log"]},
    {"id": "R37-C2-U7-BOOK-CODE-W", "round": 37, "lane": "C2-U7", "date": "2026-10-30", "status": "inconclusive", "positive_control": "failed",
     "control_detail": "B: LP1 sentence located by word indices, W readout: p_a 0.065, p_b 0.022 (null max 16.6 > real 14.5). LP1_REAL register contains LP1 words so random LP1 word bags score as high as a real sentence.",
     "hypothesis": "Same as R37-C2-U7-BOOK-CODE with the whole indexed word retrieved.", "coverage": "80 word-whole readout selections swept (0 flagged) but the readout has no measured power.",
     "result": "inconclusive: instrument cannot see a planted word-whole retrieval from LP1.", "threshold": "as parent", "power": "control failed",
     "conditionals": ["rule space as parent", "decoder as parent", "adjudicator cannot separate LP1-word bags (register contains LP1)"],
     "not_covered": ["any word-whole retrieval verdict; needs an LP1-excluded register or a word-order statistic"],
     "artifacts": ["results.json", "RESULTS.md"]}]}
json.dump(led, open('ledger.json', 'w'), indent=1)
