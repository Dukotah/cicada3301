"""Blocked FFT scanner — same arithmetic as analysis/skeleton/wordlen_search.py,
restructured so a 22M+ word corpus and many patterns fit in memory and budget.

Key differences from the Round-8 scan (arithmetic identical, cost lower):
  * corpus split into fixed blocks with P-1 overlap, so every FFT is size 2^19
    regardless of text length -> constant memory, and the corpus-side transform
    for each rune-length VALUE is computed once per block and reused by every
    range mask (a range indicator is the sum of its value indicators).
  * pattern-side transforms computed once for the whole run.
  * frequency-domain accumulation, one inverse transform per (pattern, block).

Verified against the reference implementation in verify_vs_round8.py.
"""
import numpy as np

P_BLOCK = 1 << 17          # 131,072 corpus words per block
LOGSIZE = 1 << 18          # keeps every cached transform to ~1 MB


class Pattern:
    """one length sequence + one matcher, precompiled to frequency domain"""

    def __init__(self, name, groups, P, size=LOGSIZE):
        self.name, self.P, self.size = name, P, size
        self.groups = []
        for a, rng in groups:
            fa = np.fft.rfft(a[::-1].astype(np.float64), size).astype(np.complex64)
            self.groups.append((fa, rng))


class BlockCache:
    def __init__(self, block, size):
        self.block, self.size = block, size
        self._v, self._r = {}, {}

    def value(self, v):
        if v not in self._v:
            self._v[v] = np.fft.rfft((self.block == v).astype(np.float64),
                                     self.size)
        return self._v[v]

    def rng(self, lo, hi):
        k = (lo, hi)
        if k not in self._r:
            s = None
            for v in range(max(1, lo), min(hi, 40) + 1):
                t = self.value(v)
                s = t.copy() if s is None else s + t
            self._r[k] = s if s is not None else np.zeros(self.size // 2 + 1,
                                                          np.complex128)
        return self._r[k]


def scan_block(block, patterns, size=LOGSIZE):
    """returns {pattern_name: float array of match counts, offset 0..len-P}"""
    bc = BlockCache(block, size)
    out = {}
    for pat in patterns:
        if len(block) < pat.P:
            continue
        acc = None
        for fa, (lo, hi) in pat.groups:
            t = bc.rng(lo, hi) * fa
            acc = t if acc is None else acc + t
        tot = np.fft.irfft(acc, size)
        out[pat.name] = tot[pat.P-1:len(block)]
    return out


def scan_corpus(corpus, patterns, block=P_BLOCK, size=LOGSIZE, progress=None):
    """corpus: {name: int16 array}.  returns {pat: (best, text, offset)} and
    {pat: {text: best}}"""
    P = max(p.P for p in patterns)
    step = block - (P - 1)
    best = {p.name: (-1.0, None, -1) for p in patterns}
    per_text = {p.name: {} for p in patterns}
    for ti, (tname, arr) in enumerate(sorted(corpus.items())):
        M = len(arr)
        if M < P:
            continue
        tbest = {p.name: -1.0 for p in patterns}
        targ = {p.name: -1 for p in patterns}
        for s in range(0, max(1, M - P + 1), step):
            blk = arr[s:s + block]
            if len(blk) < P:
                break
            res = scan_block(blk, patterns, size)
            for k, v in res.items():
                if len(v) == 0:
                    continue
                j = int(v.argmax())
                if v[j] > tbest[k]:
                    tbest[k] = float(v[j]); targ[k] = s + j
        for k in tbest:
            per_text[k][tname] = tbest[k]
            if tbest[k] > best[k][0]:
                best[k] = (tbest[k], tname, targ[k])
        if progress and ti % progress == 0:
            print('   .. %d/%d %s' % (ti, len(corpus), tname), flush=True)
    return best, per_text
