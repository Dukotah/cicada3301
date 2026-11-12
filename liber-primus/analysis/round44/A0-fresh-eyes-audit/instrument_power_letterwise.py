"""Fresh-eyes audit, part 8: can the instrument of record see LETTER-WISE English when handed the right key?

The cleartext word lengths say the plaintext is spelled one rune per letter (wordlen.py). Every
language model in panel-R36 was trained on multigraph spelling, so this had to be measured: plant
letter-wise English under the oracle's own keyskip1 encipherer, decode with beam_v3 panel_max and the
correct key, adjudicate with panel-R36. A multigraph plant of the same text is the control.
Output: instrument_power_letterwise.json. Needs the panel fixtures in data/panels/.
"""
import sys, os, re, random, collections, json
HERE = os.path.dirname(os.path.abspath(__file__))
LPDIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LPDIR)
sys.path.insert(0, LPDIR)
import verify_solution as vs
from lp import gematria as gp
V, BR, pan = vs.load_instruments(quiet=True)
A = V.A
T = gp.TRANSLIT
single = {t: i for i, t in enumerate(T) if len(t) == 1}
single.update({'K': single['C'], 'V': single['U'], 'Z': single['S'], 'Q': single['C']})
def letterwise(txt):
    return [single[ch] for ch in txt if ch in single]
MULTI = sorted(((t, i) for i, t in enumerate(T)), key=lambda x: -len(x[0]))
def multigraph(txt, wordwise=True):
    out = []
    words = txt.split() if wordwise else [txt.replace(' ', '')]
    for w in words:
        w = w.replace('K', 'C').replace('V', 'U').replace('Z', 'S').replace('Q', 'C')
        i = 0
        while i < len(w):
            if w.startswith('ING', i): out.append(T.index('NG')); i += 3; continue
            if w.startswith('IO', i): out.append(T.index('IA')); i += 2; continue
            for t, k in MULTI:
                if w.startswith(t, i): out.append(k); i += len(t); break
            else: i += 1
    return out
def load_text(fn):
    t = open(fn, encoding='utf-8', errors='ignore').read()
    t = t[int(len(t) * .3):int(len(t) * .7)].upper()
    return re.sub(r'[^A-Z]+', ' ', t)
texts = {n: load_text(os.path.join('data/keys', d, n + '.txt')) for d, n in (('armada18', 'melville_moby_dick'), ('armada19', 'ovid_metamorphoses'), ('armada18', 'emerson_essays_first_series'))}
rnd = random.Random(20261112)
def trial(P, L, rel='keyskip1'):
    K = [rnd.randrange(29) for _ in range(4096)]
    C = vs._encipher(P[:L], K, seed=rnd.randrange(10**6))[0]
    r = V.beam_decode_v3(C, K, vs.ADV[rel], design='panel_max', sign=-1, o=0, beam_w=400)
    res = A.adjudicate(r['plain_idx'], pan=pan)
    rec = sum(1 for a, b in zip(r['plain_idx'], P[:L]) if a == b) / L
    Kw = [rnd.randrange(29) for _ in range(4096)]
    rw = V.beam_decode_v3(C, Kw, vs.ADV[rel], design='panel_max', sign=-1, o=0, beam_w=400)
    resw = A.adjudicate(rw['plain_idx'], pan=pan)
    return float(res['pmax']), pan.registers[int(res['preg'])], rec, float(resw['pmax']), len(set(r['plain_idx'])), len(set(rw['plain_idx']))
out = {}
for L in (120, 240):
    bar = vs.page_bar(L, 'keyskip1')
    for enc_name, enc in (('LETTERWISE', letterwise), ('MULTIGRAPH(control)', multigraph)):
        rows = []
        for name, txt in texts.items():
            Pall = enc(txt)
            for j in range(8):
                s = rnd.randrange(0, len(Pall) - L - 1)
                rows.append(trial(Pall[s:s + L], L))
        pm = sorted(r[0] for r in rows); rec = sum(r[2] for r in rows) / len(rows)
        clears = sum(1 for r in rows if r[0] >= bar)
        regs = collections.Counter(r[1] for r in rows).most_common(3)
        wr = sorted(r[3] for r in rows)
        print(f"L={L} {enc_name:20s} n={len(rows)} bar(N=1)={bar:.2f} | correct-key pmax min/med/max = {pm[0]:.1f}/{pm[len(pm)//2]:.1f}/{pm[-1]:.1f}  clears {clears}/{len(rows)}  mean recovery {rec:.3f}  argmax {regs} | wrong-key pmax med/max {wr[len(wr)//2]:.1f}/{wr[-1]:.1f} | distinct runes correct/wrong median {sorted(r[4] for r in rows)[len(rows)//2]}/{sorted(r[5] for r in rows)[len(rows)//2]}")
        out[f"{L}:{enc_name}"] = rows
json.dump(out, open(os.path.join(HERE, 'instrument_power_letterwise.json'), 'w'))
