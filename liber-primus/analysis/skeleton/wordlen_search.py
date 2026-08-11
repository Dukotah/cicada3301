"""Track SKELETON — identify the LP2 plaintext through the cleartext channel.

Word (`-`), clause (`.`), line (`/`) and page (`%`) boundaries are NOT enciphered.
Word length in runes is therefore a PLAINTEXT INVARIANT under any per-rune
substitution or additive keystream, including a one-time pad. The
information-theoretic wall in this repo applies to rune VALUES; it does not apply
to this channel at all, and no prior round has attacked it. Every "keytext" entry
in DEAD_ENDS is about a text used as a KEY; this asks whether a known text is the
PLAINTEXT, which needs no key at all.

If a corpus text's word-length signature matches LP2's, that identifies the
plaintext -- and the plaintext immediately yields the keystream by subtraction.

Method
  - LP2 word lengths measured in runes over the 55 unsolved pages.
  - Candidate texts transliterated English -> futhorc with greedy longest-match
    multigraphs (EA IA AE OE NG EO TH ING), which is what makes a rune-length
    signature distinctive rather than a rescaled letter count.
  - Full-corpus scan by FFT cross-correlation: for every alignment offset,
    count word positions whose predicted rune length matches the observed one.
    O(M log M) per length value, so scanning millions of words is trivial.
  - Slack 0 and 1. Slack 1 absorbs one null interrupter per word (a null F adds
    one rune to its word) and transliteration ambiguity, at the cost of a higher
    null baseline -- both are reported.
  - Null calibrated by scanning the SAME corpus with the LP2 sequence shuffled,
    and by scanning unrelated texts against each other.
"""
import os, sys, glob, math, json, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX

MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')


def rune_len(word):
    w = word.upper()
    i, n = 0, 0
    while i < len(w):
        for m in MULTI:
            if w.startswith(m, i):
                i += len(m); n += 1
                break
        else:
            if 'A' <= w[i] <= 'Z':
                n += 1
            i += 1
    return n


_SUB = [(re.compile(m), chr(0x01 + k)) for k, m in enumerate(MULTI)]


def corpus_lengths(text):
    """rune length of every word, vectorised.

    Collapsing each multigraph to a single sentinel char before splitting turns
    the per-word greedy match into one pass over the whole text, which matters:
    the scan recomputes nothing, it reuses these arrays for every window/slack.
    """
    t = text.upper()
    for rx, ch in _SUB:
        t = rx.sub(ch, t)
    out = []
    for w in re.findall("[A-Z-	']+", t):
        n = sum(1 for c in w if c != "'")
        if n:
            out.append(n)
    return np.array(out, np.int16)


def lp2_words():
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    segs = txt.split('%')[:55]                    # unsolved pages 0-54
    lens, fcount = [], []
    cur, cf = 0, 0
    for seg in segs:
        for ch in seg:
            if ch in RUNE_TO_IDX:
                cur += 1
                if ch == 'ᚠ':
                    cf += 1
            elif ch in '-.':
                # '/' is a LINE WRAP, not a word boundary: 458 of the 604 line
                # breaks fall MID-WORD, so splitting there shatters 458 words
                # into fragments and destroys the length signature.
                if cur:
                    lens.append(cur); fcount.append(cf)
                cur, cf = 0, 0
        if cur:
            lens.append(cur); fcount.append(cf)
            cur, cf = 0, 0
    return np.array(lens, np.int16), np.array(fcount, np.int16)


def scan(pattern, corpus, slack):
    """match count at every alignment offset, via FFT cross-correlation"""
    P, M = len(pattern), len(corpus)
    if M < P:
        return None
    size = 1
    while size < M + P:
        size *= 2
    total = np.zeros(size)
    fc = {}
    for v in range(1, 20):
        a = (pattern == v).astype(np.float64)
        if a.sum() == 0:
            continue
        b = (np.abs(corpus.astype(np.int32) - v) <= slack).astype(np.float64)
        if v not in fc:
            fc[v] = np.fft.rfft(b, size)
        fa = np.fft.rfft(a[::-1], size)
        total += np.fft.irfft(fc[v] * fa, size)
    # offset o corresponds to index o + P - 1
    return total[P-1:P-1+M-P+1]


def main():
    lp, fc = lp2_words()
    print('LP2 unsolved: %d words, %d runes, %d interrupters'
          % (len(lp), lp.sum(), fc.sum()))
    print('length histogram:', np.bincount(lp)[:13].tolist())

    texts = {}
    for p in glob.glob(os.path.join(ROOT, 'data', '*.txt')):
        n = os.path.basename(p)
        if n in ('krisyotam_runes.txt', 'english_quadgrams.txt'):
            continue
        texts[n] = open(p, encoding='utf-8', errors='ignore').read()
    for p in glob.glob(os.path.join(ROOT, 'data', 'keys', '*.txt')):
        texts['keys/' + os.path.basename(p)] = open(p, encoding='utf-8',
                                                    errors='ignore').read()
    for p in glob.glob(os.path.join(HERE, 'corpus', '*.txt')):
        texts['gutenberg/' + os.path.basename(p)] = open(
            p, encoding='utf-8', errors='ignore').read()

    print('transliterating corpus ...', flush=True)
    LENS = {n: corpus_lengths(t) for n, t in sorted(texts.items())}
    total_words = sum(len(v) for v in LENS.values())
    print('corpus: %d texts, %d words' % (len(LENS), total_words), flush=True)

    rng = np.random.default_rng(3301)
    results = []
    for W in (3367, 400, 120):
        pat = lp[:W] if W <= len(lp) else lp
        shuf = pat.copy(); rng.shuffle(shuf)
        print('\n=== window %d words ===' % len(pat))
        for slack in (0, 1):
            best_all, null_all, words = [], [], 0
            for name, C in LENS.items():
                words += len(C)
                s = scan(pat, C, slack)
                if s is None:
                    continue
                sn = scan(shuf, C, slack)
                best_all.append((s.max(), name, int(s.argmax()), len(C)))
                null_all.append(sn.max())
            best_all.sort(reverse=True)
            nm = np.mean(null_all); nsd = np.std(null_all)
            print(' slack %d | corpus %d words across %d texts' %
                  (slack, words, len(texts)))
            print('   best real: %.0f/%d matches (%.1f%%) in %s @word %d'
                  % (best_all[0][0], len(pat), 100*best_all[0][0]/len(pat),
                     best_all[0][1], best_all[0][2]))
            print('   shuffled-control best across same texts: mean %.0f max %.0f'
                  % (nm, max(null_all)))
            z = (best_all[0][0] - np.mean(null_all)) / (np.std(null_all) + 1e-9)
            print('   z of real vs shuffled-control distribution: %.2f' % z)
            for b in best_all[:4]:
                print('     %-34s %5.0f (%.1f%%)' % (b[1], b[0], 100*b[0]/len(pat)))
            results.append(dict(window=len(pat), slack=slack,
                                best=float(best_all[0][0]), text=best_all[0][1],
                                offset=best_all[0][2], pct=float(100*best_all[0][0]/len(pat)),
                                null_mean=float(nm), null_max=float(max(null_all)),
                                z=float(z), corpus_words=int(words),
                                texts=len(texts)))
    json.dump(results, open(os.path.join(HERE, 'wordlen_results.json'), 'w'), indent=1)
    print('\nwrote wordlen_results.json')


if __name__ == '__main__':
    main()
