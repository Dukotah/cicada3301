"""R45 I1 shared helpers: spaced held-out plaintext as rune WORDS, LP2 printed word lengths, the five conditions.
Writes nothing."""
import os, sys, re, random, hashlib, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AN = lambda *a: os.path.join(LP, "analysis", *a)
sys.path.insert(0, os.path.join(LP, "src"))
from lp.gematria import RUNE_TO_IDX  # noqa: E402
import importlib.util as _u


def _load(name, path):
    sp = _u.spec_from_file_location(name, path); m = _u.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


DET = _load("det_b6", AN("round10b", "B6-non-english-plaintext", "detectors.py"))
_WCACHE = {}


def _drop_vowels(w):
    return "".join(c for c in w.upper() if c not in "AEIOUY")


def text_words(fn, novowel=False):
    """Held-out prose -> list of words, each a list of rune indices (panel's own EN mapping, per word)."""
    key = (fn, novowel)
    if key in _WCACHE:
        return _WCACHE[key]
    t = open(os.path.join(LP, "data", fn), encoding="utf-8", errors="ignore").read()
    t = t[len(t) // 20:]                                  # skip front matter (fable52 convention)
    out = []
    for w in re.findall(r"[A-Za-z]+", t):
        if novowel:
            w = _drop_vowels(w)
            if not w:
                continue
        r = list(DET.text_to_runes(w, "EN"))
        if len(r):
            out.append([int(x) for x in r])
    _WCACHE[key] = out
    return out


def page_words(words, L, rng):
    """Contiguous run of whole words starting at a random word, covering >= L runes (+ a tail)."""
    i = rng.randrange(0, len(words) - 4 * L)
    out, n = [], 0
    while n < L + 40:
        out.append(words[i]); n += len(words[i]); i += 1
    return out


def flat(ws):
    return [x for w in ws for x in w]


def cut_lens(lens, L):
    """truncate a length sequence to cover exactly L runes."""
    out, n = [], 0
    for l in lens:
        if n >= L:
            break
        l2 = min(l, L - n); out.append(l2); n += l2
    return out


# ---------------------------------------------------------------- LP2 printed word lengths (separators '-' and '.')
def lp2_page_lengths():
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages = []
    for seg in txt.split("%")[:55]:
        lens, cur = [], 0
        for ch in seg:
            if ch in RUNE_TO_IDX:
                cur += 1
            elif ch in "-.":
                if cur:
                    lens.append(cur)
                cur = 0
        if cur:
            lens.append(cur)
        pages.append(lens)
    return pages


LP2_PAGES = lp2_page_lengths()
LP2_ALL = [l for p in LP2_PAGES for l in p]


def decoy_lengths(rng, L):
    """LP2's actual printed length sequence from a random page start, covering >= L runes (cond c)."""
    p = rng.randrange(55)
    seq = list(LP2_PAGES[p]) + [l for q in LP2_PAGES[p + 1:] + LP2_PAGES[:p] for l in q]
    return seq


def cond_lengths(cond, true_lens, rng, L):
    """printed length sequence the instrument is handed (covering >= L runes)."""
    if cond == "a":
        return list(true_lens)
    if cond == "b":
        x = list(true_lens); rng.shuffle(x); return x
    if cond == "c":
        return decoy_lengths(rng, L)
    if cond == "d":
        return [sum(true_lens)]
    raise ValueError(cond)


def shuffle_words(ws, rng):
    x = list(ws); rng.shuffle(x); return x


def h(idx):
    return hashlib.sha256(",".join(map(str, idx)).encode()).hexdigest()[:16]


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    a = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - a) / d, 3), round((c + a) / d, 3)]
