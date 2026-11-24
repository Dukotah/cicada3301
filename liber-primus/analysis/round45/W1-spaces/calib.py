# R45-W1 calibration step (PREREG s1): parser sanity + GP transliteration rule selection on printed LP1 lengths.
import json, difflib, collections
import w1lib as w
r2, w2 = w.load_lp2(); r1, w1 = w.load_lp1(); rs, ws = w.load_lp2_solved()
P = [x['len'] for x in w1] + [x['len'] for x in ws]
ref = open('inputs/lp1-plaintext-reference.txt', encoding='utf8').read()
words = []
for line in ref.splitlines():
    if line.startswith('#'): continue
    words += [x.replace("'", "") for x in w.WORD_RE.findall(line)]
res = {}
for rule in ('R-A', 'R-B', 'R-C'):
    E = [len(w.to_runes(x, rule)) for x in words]
    sm = difflib.SequenceMatcher(None, P, E, autojunk=False)
    m = sum(b.size for b in sm.get_matching_blocks())
    res[rule] = dict(printed_words=len(P), ref_words=len(E), matched=m, agreement=round(m / len(P), 4))
best = max(res, key=lambda r: (res[r]['agreement'], r == 'R-A'))
out = dict(lp2=dict(runes=len(r2), words=len(w2), pages=len(set(x['page'] for x in w2)),
                    sections=len(set(x['sect'] for x in w2)), paragraphs=len(set(x['para'] for x in w2)),
                    sentences=len(set(x['sent'] for x in w2)), lines=len(set(x['line'] for x in w2))),
           lp1=dict(runes=len(r1), words=len(w1)), lp2_solved=dict(runes=len(rs), words=len(ws)),
           solved_reference_words=len(P), translit_rules=res, chosen_rule=best,
           inputs={'krisyotam_runes.txt': w.sha256(w.DATA + '/krisyotam_runes.txt'),
                   'rtkd_master.txt': w.sha256(w.DATA + '/sources/rtkd_master.txt'),
                   'inputs/lp1-plaintext-reference.txt': w.sha256('inputs/lp1-plaintext-reference.txt')},
           kill_check='PASS' if len(w2) > 2850 and res[best]['agreement'] >= 0.9 else 'FAIL')
json.dump(out, open('calib.json', 'w'), indent=1); print(json.dumps(out, indent=1))
