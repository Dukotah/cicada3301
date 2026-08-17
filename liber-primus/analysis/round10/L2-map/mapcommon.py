"""Shared parse + scorers for Round 10 lane L2-MAP ("its words are the map").

Parse convention is fixed by PREREG.md and by the Round-8 parsing-bug entry
(DEAD_ENDS.md:407-417): '/' is a LINE WRAP, not a word separator. Words split on
'-' and '.' and on the page marker '%' only.

Gate G0 (verified in run_map.py): pages 0-54 -> 2,928 words / 12,956 runes, and
the flat rune stream is byte-identical to analysis/seed_sweep/ct.bin.
"""
import os, sys, re, math, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))   # liber-primus/
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp import gematria as gp
from lp import score as SCORE

N = 29
F_IDX = 0  # interrupter rune
UNSOLVED_MAX_PAGE = 54

RAW = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()

# ---- rune 4-gram model (stream scale: English -11..-12, random ~ -16) ----
NG = np.fromfile(os.path.join(ROOT, 'analysis', 'seed_sweep', 'ngram.bin'), np.float32)


def ng_score(seq):
    """Mean log-prob of rune 4-grams. Needs >= 24 symbols to be meaningful."""
    if len(seq) < 24:
        return -99.0
    a = np.asarray(seq, np.int32)
    idx = ((a[:-3] * N + a[1:-2]) * N + a[2:-1]) * N + a[3:]
    return float(NG[idx].mean())


_Q = SCORE.default()


def eng_score(text):
    """English quadgram score_norm (page scale: English -4.2..-5.0, random -7.3)."""
    t = ''.join(c for c in text.upper() if c.isalpha())
    if len(t) < 8:
        return -99.0
    return _Q.score_norm(t)


def translit(seq):
    return ''.join(gp.IDX_TO_TRANS[i] for i in seq)


# ---------------------------------------------------------------- parse ----
def parse(max_page=UNSOLVED_MAX_PAGE):
    words, cur = [], []
    w_page, w_line, w_sent = [], [], []
    lines, line_page, curline = [], [], []
    pages, curpage = [], []
    page_id, line_id, sent_id = 0, 0, 0
    pend = (0, 0, 0)

    def flush():
        nonlocal cur
        if cur:
            words.append(cur); w_page.append(pend[0])
            w_line.append(pend[1]); w_sent.append(pend[2])
            cur = []

    for ch in RAW:
        if page_id > max_page:
            break
        if ch in gp.RUNE_TO_IDX:
            if not cur:
                pend = (page_id, line_id, sent_id)
            i = gp.RUNE_TO_IDX[ch]
            cur.append(i); curline.append(i); curpage.append(i)
        elif ch == '-':
            flush()
        elif ch == '.':
            flush(); sent_id += 1
        elif ch == '/':
            lines.append(curline); line_page.append(page_id); curline = []; line_id += 1
        elif ch == '%':
            flush()
            if curline:
                lines.append(curline); line_page.append(page_id); curline = []; line_id += 1
            pages.append(curpage); curpage = []; page_id += 1
    flush()
    if curline:
        lines.append(curline); line_page.append(page_id)
    if curpage:
        pages.append(curpage)
    return dict(words=words, w_page=w_page, w_line=w_line, w_sent=w_sent,
                lines=lines, line_page=line_page, pages=pages)


def flat(words):
    return [r for w in words for r in w]


# ---------------------------------------------------------------- nulls ----
def null_A(words, seed):
    """Shuffle the rune CONTENT; hold every word-boundary position fixed."""
    rng = random.Random(seed)
    pool = flat(words); rng.shuffle(pool)
    out, k = [], 0
    for w in words:
        out.append(pool[k:k + len(w)]); k += len(w)
    return out


def zscore(real, nulls):
    a = np.asarray(nulls, float)
    sd = a.std(ddof=1)
    return 0.0 if sd == 0 else float((real - a.mean()) / sd)


# ----------------------------------------------------- solved LP English ----
SOLVED_TXT = os.path.join(ROOT, 'data', 'keys', 'armada18',
                          'cicada_koans_and_lp_sections.txt')


def solved_english_words():
    txt = open(SOLVED_TXT, encoding='utf-8').read()
    return [w for w in ''.join(c if c.isalpha() else ' ' for c in txt.upper()).split() if w]


MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')


def rune_len(word):
    """Greedy-multigraph rune length of an English word (repo convention;
    reproduces all 20 PARABLE word lengths exactly - Round 9 Track LENGTH)."""
    w = word.upper(); i = n = 0
    while i < len(w):
        for m in MULTI:
            if w.startswith(m, i):
                i += len(m); n += 1; break
        else:
            if 'A' <= w[i] <= 'Z':
                n += 1
            i += 1
    return n
