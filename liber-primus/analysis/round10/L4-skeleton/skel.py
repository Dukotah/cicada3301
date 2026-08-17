"""L4 SKELETON EXTENSION — shared library.

Inherits, unchanged and deliberately, from analysis/skeleton/wordlen_search.py:
  * the LP2 word parse (split on '-' and '.' ONLY; '/' is a line wrap, 458 of 604
    line breaks fall mid-word -- DEAD_ENDS.md:411),
  * the greedy longest-match multigraph transliteration (verified against the
    unenciphered PARABLE page, 20/20 word lengths exact -- ROUND-9 Track LENGTH),
  * FFT cross-correlation over every alignment offset.

Adds:
  * a recursive corpus loader (Round 8 globbed data/keys/*.txt top-level only and
    so never saw the ~208 files in data/keys/{campaign12,campaign13,armada18,
    armada19,welsh}/),
  * HTML stripping + Gutenberg boilerplate trimming,
  * content-hash dedup,
  * the DIRECTIONAL INTERVAL matcher: corpus length v matches LP2 word i iff
    v in [obs_i - fc_i, obs_i].  A null F can only lengthen a word, never shorten
    it, so this is the honest tolerance shape for the interrupter ambiguity that
    Round 9 bounded as [4.268, 4.425].
"""
import os, sys, re, glob, hashlib, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))   # liber-primus/
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX

MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')
_SUB = [(re.compile(m), chr(0x01 + k)) for k, m in enumerate(MULTI)]
_TAG = re.compile(r'<[^>]+>')
_SCRIPT = re.compile(r'<(script|style)\b.*?</\1>', re.S | re.I)


def rune_len(word):
    """rune length of a single English word under the repo's greedy encoder"""
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


def corpus_lengths(text):
    """rune length of every word in a text (vectorised, identical convention)"""
    t = text.upper()
    for rx, ch in _SUB:
        t = rx.sub(ch, t)
    out = []
    for w in re.findall("[A-Z\x01-\x09\\-']+", t):
        n = sum(1 for c in w if c != "'" and c != '-')
        if n:
            out.append(n)
    return np.array(out, np.int16)


def clean(raw, path=''):
    """strip HTML and Gutenberg boilerplate; leave plain text alone"""
    if path.lower().endswith(('.html', '.htm', '.xml')) or '<html' in raw[:4000].lower():
        raw = _SCRIPT.sub(' ', raw)
        raw = _TAG.sub(' ', raw)
        raw = (raw.replace('&nbsp;', ' ').replace('&amp;', '&')
                  .replace('&quot;', '"').replace('&#39;', "'"))
    m = re.search(r'\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG[^\n]*\n', raw)
    if m:
        raw = raw[m.end():]
    m = re.search(r'\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG', raw)
    if m:
        raw = raw[:m.start()]
    return raw


def lp2_words():
    """LP2 unsolved pages 0-54: (observed rune length per word, F-count per word)"""
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    segs = txt.split('%')[:55]
    lens, fcount = [], []
    cur, cf = 0, 0
    for seg in segs:
        for ch in seg:
            if ch in RUNE_TO_IDX:
                cur += 1
                if ch == 'ᚠ':          # F rune
                    cf += 1
            elif ch in '-.':
                if cur:
                    lens.append(cur); fcount.append(cf)
                cur, cf = 0, 0
        if cur:
            lens.append(cur); fcount.append(cf)
            cur, cf = 0, 0
    return np.array(lens, np.int16), np.array(fcount, np.int16)


# ---------------------------------------------------------------- corpus ----

SOURCES = [
    (os.path.join(ROOT, 'data', '*.txt'), 'data'),
    (os.path.join(ROOT, 'data', 'keys', '**', '*.txt'), 'keys'),
    (os.path.join(ROOT, 'data', 'keys', '**', '*.html'), 'keys'),
    (os.path.join(ROOT, 'data', 'sources', '**', '*.txt'), 'sources'),
    (os.path.join(ROOT, 'analysis', 'skeleton', 'corpus', '*.txt'), 'r8corpus'),
    (os.path.join(ROOT, 'analysis', 'skeleton', 'lang', '*.txt'), 'r8lang'),
    (os.path.join(HERE, 'corpus', '*.txt'), 'l4new'),
]
SKIP = {'krisyotam_runes.txt', 'english_quadgrams.txt'}


def load_corpus(min_words=300, verbose=True, extra_globs=()):
    """returns {name: int16 array of word rune-lengths}, deduped by content hash"""
    seen_hash, out, meta = {}, {}, []
    srcs = list(SOURCES) + [(g, 'extra') for g in extra_globs]
    for pat, tag in srcs:
        for p in sorted(glob.glob(pat, recursive=True)):
            base = os.path.basename(p)
            if base in SKIP:
                continue
            try:
                raw = open(p, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            txt = clean(raw, p)
            L = corpus_lengths(txt)
            if len(L) < min_words:
                continue
            h = hashlib.sha1(L.tobytes()).hexdigest()
            if h in seen_hash:
                meta.append((tag + '/' + base, 'dup-of ' + seen_hash[h], len(L)))
                continue
            seen_hash[h] = tag + '/' + base
            name = tag + '/' + base
            out[name] = L
            meta.append((name, 'ok', len(L)))
    if verbose:
        nd = sum(1 for m in meta if m[1] != 'ok')
        print('corpus: %d unique texts, %d words (%d duplicate files dropped)'
              % (len(out), sum(len(v) for v in out.values()), nd), flush=True)
    return out, meta


# ------------------------------------------------------------------ scan ----

def _fft_scan(groups, corpus, P, vcache=None):
    """groups: list of (indicator_over_pattern, accept_mask_over_corpus).

    Accumulates in the FREQUENCY domain and inverts once (irfft is linear), and
    reuses one rfft per corpus VALUE across all range masks (a range indicator is
    the sum of its value indicators, so its transform is the sum of theirs).
    Same arithmetic as the Round-8 scan, ~5x less of it.
    """
    M = len(corpus)
    if M < P:
        return None
    size = 1
    while size < M + P:
        size *= 2
    acc = None
    for a, b in groups:
        if a.sum() == 0:
            continue
        fb = np.fft.rfft(b.astype(np.float64), size)
        fa = np.fft.rfft(a[::-1].astype(np.float64), size)
        acc = fb * fa if acc is None else acc + fb * fa
    if acc is None:
        return None
    total = np.fft.irfft(acc, size)
    return total[P-1:P-1+M-P+1]


class TextFFT:
    """cached per-text corpus-side transforms, one per rune-length value"""
    def __init__(self, corpus, size):
        self.corpus, self.size = corpus, size
        self._v = {}
        self._r = {}

    def value(self, v):
        if v not in self._v:
            self._v[v] = np.fft.rfft((self.corpus == v).astype(np.float64),
                                     self.size)
        return self._v[v]

    def rng(self, lo, hi):
        key = (lo, hi)
        if key not in self._r:
            s = None
            for v in range(max(1, lo), min(hi, 40) + 1):
                t = self.value(v)
                s = t.copy() if s is None else s + t
            self._r[key] = s if s is not None else np.zeros(
                self.size // 2 + 1, complex)
        return self._r[key]


def fftsize(M, P):
    size = 1
    while size < M + P:
        size *= 2
    return size


def scan_groups_cached(groups, tf, P, M):
    """groups: list of (pattern_indicator, (lo,hi))"""
    acc = None
    for a, (lo, hi) in groups:
        if not a.any():
            continue
        fa = np.fft.rfft(a[::-1].astype(np.float64), tf.size)
        term = tf.rng(lo, hi) * fa
        acc = term if acc is None else acc + term
    if acc is None:
        return None
    total = np.fft.irfft(acc, tf.size)
    return total[P-1:P-1+M-P+1]


def groups_slack(pattern, slack):
    g = []
    for v in range(1, 30):
        a = (pattern == v)
        if a.any():
            g.append((a, (v - slack, v + slack)))
    return g


def groups_interval(pattern, fc, extra_lo=0, extra_hi=0):
    g = []
    fmax = int(fc.max()) if len(fc) else 0
    for o in range(1, 30):
        for f in range(0, fmax + 1):
            a = (pattern == o) & (fc == f)
            if a.any():
                g.append((a, (o - f - extra_lo, o + extra_hi)))
    return g


def scan_slack(pattern, corpus, slack):
    """Round-8 matcher: |corpus - obs| <= slack"""
    groups = []
    for v in range(1, 22):
        a = (pattern == v)
        if not a.any():
            continue
        b = (np.abs(corpus.astype(np.int32) - v) <= slack)
        groups.append((a, b))
    return _fft_scan(groups, corpus, len(pattern))


def scan_interval(pattern, fc, corpus, extra_lo=0, extra_hi=0):
    """directional interval matcher: corpus in [obs-fc-extra_lo, obs+extra_hi]"""
    groups = []
    ci = corpus.astype(np.int32)
    cache = {}
    for o in range(1, 22):
        for f in range(0, int(fc.max()) + 1):
            a = (pattern == o) & (fc == f)
            if not a.any():
                continue
            lo, hi = o - f - extra_lo, o + extra_hi
            key = (lo, hi)
            if key not in cache:
                cache[key] = (ci >= lo) & (ci <= hi)
            groups.append((a, cache[key]))
    return _fft_scan(groups, corpus, len(pattern))
