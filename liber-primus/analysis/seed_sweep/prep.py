"""Track SEED — data preparation.

Emits, for the C sweep:
  ct.bin        : 12956 uint8 rune indices, unsolved LP2 pages 0-54, file order
  ngram.bin     : rune 4-gram log-prob table (29^4 float32) built from English
                  corpora transliterated into futhorc (greedy longest-match)
  anchor.txt    : the solved AN END page (ct + known plaintext) for harness validation

Page alignment verified against the published per-page F counts in
analysis/STRUCTURE-FINDINGS.md (our segments 0..49 == published 0..49; published
index 50 is a blank page absent from the krisyotam segmentation; our 50..54 ==
published 51..55). Segments 55/56 are the SOLVED AN END / PARABLE pages and are
excluded from the ciphertext.
"""
import sys, os, re, math, array, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lp.gematria import RUNE_TO_IDX, GEMATRIA

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, '..', '..', 'data'))
N = 29

# ---------------------------------------------------------------- ciphertext
txt = open(os.path.join(DATA, 'krisyotam_runes.txt'), encoding='utf-8').read()
segs = txt.split('%')
UNSOLVED = segs[:55]          # LP2 pages 0-54
ANEND    = segs[55]           # solved: totient keystream

ct = [RUNE_TO_IDX[c] for s in UNSOLVED for c in s if c in RUNE_TO_IDX]
assert len(ct) == 12956, len(ct)
assert ct.count(0) == 458, ct.count(0)

# ------------------------------------------------------- futhorc transliterator
# Greedy longest-match English -> rune indices. Multigraphs first.
MULTI = [('ING', 21), ('EA', 28), ('IA', 27), ('IO', 27), ('AE', 25), ('OE', 22),
         ('NG', 21), ('EO', 12), ('TH', 2)]
SINGLE = {}
for i, r, t, p in GEMATRIA:
    if len(t) == 1:
        SINGLE[t] = i
SINGLE['V'] = 1   # U/V
SINGLE['K'] = 5   # C/K
SINGLE['Z'] = 15  # S/Z
SINGLE['Q'] = 5   # nearest
SINGLE['QU'] = 5


def to_runes(s):
    s = s.upper()
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if not ('A' <= c <= 'Z'):
            i += 1
            continue
        for m, idx in MULTI:
            if s.startswith(m, i):
                out.append(idx)
                i += len(m)
                break
        else:
            if c in SINGLE:
                out.append(SINGLE[c])
            i += 1
    return out


# ------------------------------------------------------------ 4-gram model
def build_ngram():
    corp = []
    for f in ('kjv.txt', 'moby.txt', 'pride.txt', 'war.txt'):
        p = os.path.join(DATA, f)
        if os.path.exists(p):
            corp.append(open(p, encoding='utf-8', errors='ignore').read())
    for f in ('mabinogion.txt', 'self_reliance.txt', 'king_in_yellow.txt'):
        p = os.path.join(DATA, 'keys', f)
        if os.path.exists(p):
            corp.append(open(p, encoding='utf-8', errors='ignore').read())
    text = '\n'.join(corp)
    print('corpus chars:', len(text))
    seq = to_runes(text)
    print('corpus runes:', len(seq))
    counts = array.array('L', [0]) * (N ** 4)
    counts = [0] * (N ** 4)
    k = 0
    for j in range(3, len(seq)):
        idx = ((seq[j-3] * N + seq[j-2]) * N + seq[j-1]) * N + seq[j]
        counts[idx] += 1
        k += 1
    tot = k
    # add-alpha smoothing
    alpha = 0.25
    denom = tot + alpha * (N ** 4)
    out = array.array('f', [0.0]) * 0
    out = array.array('f', [0.0] * (N ** 4))
    for i in range(N ** 4):
        out[i] = math.log((counts[i] + alpha) / denom)
    return out, seq


def main():
    ng, corpseq = build_ngram()
    with open(os.path.join(HERE, 'ct.bin'), 'wb') as f:
        f.write(bytes(ct))
    with open(os.path.join(HERE, 'ngram.bin'), 'wb') as f:
        ng.tofile(f)

    # --- calibration: score distribution of real English vs uniform random
    def score(seq):
        s = 0.0
        for j in range(3, len(seq)):
            s += ng[((seq[j-3]*N + seq[j-2])*N + seq[j-1])*N + seq[j]]
        return s / max(1, len(seq) - 3)

    import random
    random.seed(3301)
    W = 48
    eng = [score(corpseq[i:i+W]) for i in
           random.sample(range(len(corpseq) - W), 20000)]
    rnd = [score([random.randrange(N) for _ in range(W)]) for _ in range(20000)]
    eng.sort(); rnd.sort()
    print('W=%d  English mean %.4f  p01 %.4f  p001 %.4f' %
          (W, sum(eng)/len(eng), eng[int(.01*len(eng))], eng[int(.001*len(eng))]))
    print('        random  mean %.4f  p999 %.4f  max %.4f' %
          (sum(rnd)/len(rnd), rnd[int(.999*len(rnd))], rnd[-1]))

    # --- AN END anchor (known plaintext, totient keystream, F interrupters)
    an = [RUNE_TO_IDX[c] for c in ANEND if c in RUNE_TO_IDX]
    with open(os.path.join(HERE, 'anchor.bin'), 'wb') as f:
        f.write(bytes(an))
    print('anchor AN END runes:', len(an), 'F:', an.count(0))

    # --- interrupter geometry at the head of the ciphertext
    fpos = [i for i, v in enumerate(ct) if v == 0]
    print('first 12 F positions:', fpos[:12])
    print('F in first 48 runes:', sum(1 for p in fpos if p < 48))
    print('F in first 96 runes:', sum(1 for p in fpos if p < 96))
    print('ct[:24]:', ct[:24])


if __name__ == '__main__':
    main()
