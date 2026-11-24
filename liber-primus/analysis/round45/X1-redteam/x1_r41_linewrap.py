# R45-X1: the R41-C1-R14 real-data run segments LP2 with camp7.word_pages(), which breaks a word at ANY non-rune
# character -- including the line-wrap '/' + newline.  In LP2, 420 of 593 line breaks fall inside printed words
# (W1 parse convention, verified on solved LP1).  So even if the printed spaces ARE the plaintext's words in order,
# the R41 decoder was handed a different segmentation than the encipherer used.  Measure the power cost:
# English plaintext (pride, GP R-A) laid out with LP2's exact page lengths and line-break rune positions, enciphered
# per page with the true segmentation (I1's verbatim copy of run_c1.enc_words), then decrypted with camp7's own
# decrypt_variant under (i) camp7.word_pages-style parsing (break at any non-rune) and (ii) '-'-only parsing.
import os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'W1-spaces')); sys.path.insert(0, os.path.join(LP, 'src'))
import importlib.util as U
import w1lib as w
sp = U.spec_from_file_location('camp7', os.path.join(LP, 'analysis', 'round41', 'C1-r14-r15', 'camp7.py'))
C7 = U.module_from_spec(sp); sp.loader.exec_module(C7)
from lp import gematria as gp
N = C7.N

def enc_words(plain_words, variant, sign, atb):          # verbatim (I1 arm_wordsched copy, diff-checked vs run_c1)
    tf = (lambda c: (C7.N - 1 - c) if atb else c)
    N = C7.N; out = []
    if variant == "W5":
        flat = [x for w in plain_words for x in w]; prev = 0; cf = []
        for p in flat:
            c = tf((p - sign * (C7.gp.PRIMES[prev] % N)) % N); cf.append(c); prev = c
        pos = 0
        for w in plain_words: out.append(cf[pos:pos + len(w)]); pos += len(w)
        return out
    k, cum = 0, 0
    for w in plain_words:
        cw = [tf((p - sign * k) % N) for p in w]; out.append(cw)
        if variant == "W1": k = C7.primesum(cw) % N
        elif variant == "W2": k = C7.primesum(w) % N
        elif variant == "W3": cum += C7.primesum(cw); k = cum % N
        elif variant == "W4": k = C7._totient(C7.primesum(cw)) % N
    return out

def parse_page(s, mode):
    words, cur = [], []
    for c in s:
        if c in gp.RUNE_TO_IDX: cur.append(gp.RUNE_TO_IDX[c])
        elif (mode == 'camp7') or c in '-.':
            if cur: words.append(cur); cur = []
    if cur: words.append(cur)
    return words

def main():
    runes, _ = w.load_lp2()
    pages = {}; 
    for i, x in enumerate(runes): pages.setdefault(x['page'], []).append(i)
    lb = set(i for i, x in enumerate(runes) if x['line_before'])
    corpus = [w.to_runes(t) for t in __import__('re').findall(r"[A-Za-z]+", open(os.path.join(LP, 'data', 'pride.txt'), encoding='utf8', errors='ignore').read())]
    corpus = [c for c in corpus if c]
    res = {}
    rng = random.Random(4545)
    for v in ('W1', 'W2', 'W3', 'W4', 'W5'):
        for sign in (1, -1):
            stats = {'camp7': [], 'dash_only': []}
            for rep in range(3):
                start = rng.randrange(0, len(corpus) - 5000)
                flat = []; bounds = set(); wi = start
                while len(flat) < len(runes):
                    bounds.add(len(flat)); flat.extend(corpus[wi]); wi += 1
                for p, idx in sorted(pages.items()):
                    a, b = idx[0], idx[-1] + 1
                    # true words inside page (cut at page edges)
                    pw = []; cur = []
                    for i in range(a, b):
                        if i in bounds and cur: pw.append(cur); cur = []
                        cur.append(flat[i])
                    if cur: pw.append(cur)
                    cw = enc_words(pw, v, sign, False)
                    # render with '-' between words and '/\n' at LP2's line-break rune positions
                    s = []; i = a
                    for k, word in enumerate(cw):
                        if k: s.append('-')
                        for c in word:
                            if i in lb and i != a: s.append('/\n')
                            s.append(gp.IDX_TO_RUNE[c]); i += 1
                    s = ''.join(s); P = [x for x in flat[a:b]]
                    for mode in stats:
                        dec = C7.decrypt_variant(parse_page(s, mode), v, sign, False)
                        stats[mode].append(sum(1 for x, y in zip(dec, P) if x == y) / len(P))
            res['%s%+d' % (v, sign)] = {m: dict(mean_page_recovery=round(sum(z) / len(z), 3),
                                                 frac_pages_ge_0p9=round(sum(1 for q in z if q >= 0.9) / len(z), 3))
                                        for m, z in stats.items()}
            print(v, sign, res['%s%+d' % (v, sign)], flush=True)
    real = C7.word_pages()[:55]
    out = dict(n_words_lp2_camp7_word_pages=sum(len(p) for p in real), n_words_lp2_W1_convention=2896,
               line_breaks_inside_words=sum(1 for x in runes if x['line_before'] and not x['brk_before']), results=res)
    json.dump(out, open(os.path.join(HERE, 'x1_r41_linewrap.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'results'}))

if __name__ == '__main__':
    main()
