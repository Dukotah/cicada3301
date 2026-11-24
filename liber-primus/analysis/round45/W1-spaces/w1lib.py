# R45-W1 shared library: parsers (LP2 / LP1 / solved LP2 pages), GP transliteration, corpora, statistics.
# Pure stdlib.  See PREREG.md for the frozen rules.
import os, re, math, random, collections, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
LPROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DATA = os.path.join(LPROOT, 'data')
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(RUNES)}
BREAK = set('-.&$§')
N_LP2 = 12956
NCLS = 8  # length classes 1..7, 8+


def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def parse(text):
    """Parse a transcription string. Returns (runes, words) where
    runes: list of dict(v, wi, line, page, brk_before, line_before, page_before)
    words: list of dict(len, start, page, line, sent, para, sect)"""
    runes, words = [], []
    page = line = sent = para = sect = 0
    cur = 0; start = None; wstart_units = None
    brk = False; lb = False; pb = False
    def close():
        nonlocal cur
        if cur > 0:
            words.append(dict(len=cur, start=start, page=wstart_units[0], line=wstart_units[1],
                              sent=wstart_units[2], para=wstart_units[3], sect=wstart_units[4]))
        cur = 0
    for ch in text:
        if ch in IDX:
            if cur == 0:
                start = len(runes); wstart_units = (page, line, sent, para, sect)
            runes.append(dict(v=IDX[ch], wi=len(words), line=line, page=page,
                              brk_before=brk, line_before=lb, page_before=pb))
            brk = lb = pb = False
            cur += 1
        elif ch in BREAK or ch.isdigit():
            close(); brk = True
            if ch in '.&$§': sent += 1
            if ch == '&': para += 1
            if ch == '$': sect += 1
        elif ch == '/':
            line += 1; lb = True
        elif ch == '%':
            page += 1; pb = True
    close()
    return runes, words


def load_lp2_all():
    t = open(os.path.join(DATA, 'krisyotam_runes.txt'), encoding='utf8').read()
    return parse(t)


def split_at_rune(text, n):
    """split transcription text after the n-th rune (keeping separators following it in the first part
    up to the next rune)."""
    k = 0
    for pos, ch in enumerate(text):
        if ch in IDX:
            if k == n:
                return text[:pos], text[pos:]
            k += 1
    return text, ''


def load_lp2():
    """Unsolved LP2: first 12,956 runes. Returns runes, words (words wholly inside)."""
    t = open(os.path.join(DATA, 'krisyotam_runes.txt'), encoding='utf8').read()
    a, b = split_at_rune(t, N_LP2)
    return parse(a)


def load_lp2_solved():
    t = open(os.path.join(DATA, 'krisyotam_runes.txt'), encoding='utf8').read()
    a, b = split_at_rune(t, N_LP2)
    return parse(b)


def load_lp1():
    t = open(os.path.join(DATA, 'sources', 'rtkd_master.txt'), encoding='utf8').read()
    # drop header: start at first rune line
    i = min(t.find(r) for r in RUNES if t.find(r) >= 0)
    i = t.rfind('\n', 0, i) + 1
    t = t[i:]
    k = open(os.path.join(DATA, 'krisyotam_runes.txt'), encoding='utf8').read()
    kr = ''.join(c for c in k if c in IDX)
    tr = ''.join(c for c in t if c in IDX)
    n1 = tr.find(kr[:60])
    assert tr[n1:] == kr, 'rtkd LP2 part not identical to krisyotam'
    a, b = split_at_rune(t, n1)
    return parse(a)


# ---------------- GP transliteration ----------------
TR = ['F', 'U', 'TH', 'O', 'R', 'C', 'G', 'W', 'H', 'N', 'I', 'J', 'EO', 'P', 'X', 'S', 'T', 'B', 'E', 'M', 'L', 'NG',
      'OE', 'D', 'A', 'AE', 'Y', 'IA', 'EA']
SG = {c: i for i, c in enumerate(TR) if len(c) == 1}
SG.update({'K': 5, 'Q': 5, 'V': 1, 'Z': 15})
RULES = {
    'R-A': {'TH': 2, 'EO': 12, 'NG': 21, 'OE': 22, 'AE': 25, 'IA': 27, 'IO': 27, 'EA': 28},
    'R-B': {'TH': 2, 'NG': 21},
    'R-C': {},
}


def to_runes(word, rule='R-A'):
    DG = RULES[rule]
    w = word.upper(); out = []; i = 0
    while i < len(w):
        if DG and w[i:i + 3] == 'ING': out.append(21); i += 3; continue
        if w[i:i + 2] in DG: out.append(DG[w[i:i + 2]]); i += 2; continue
        if w[i] in SG: out.append(SG[w[i]])
        i += 1
    return out


WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")
CORPORA = ['kjv.txt', 'moby.txt', 'pride.txt', 'war.txt', 'keys/king_in_yellow.txt', 'keys/mabinogion.txt',
           'keys/self_reliance.txt', 'keys/book_of_the_law.txt']


def clean_text(t):
    s = t.find('*** START OF'); e = t.find('*** END OF')
    if s >= 0:
        s = t.find('\n', s) + 1
        t = t[s:e if e > s else None]
    else:
        t = t[len(t) // 20:]
    t = re.sub(r'\{\{.*?\}\}', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]*>', ' ', t)
    t = re.sub(r'\[\d+\]', ' ', t)
    return t


def load_corpus(fn, rule='R-A'):
    """returns list of (len_in_runes, sentence_id)"""
    t = clean_text(open(os.path.join(DATA, fn), encoding='utf8', errors='ignore').read())
    out = []; sid = 0
    for m in re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)*|[.!?]", t):
        g = m.group()
        if g in '.!?':
            sid += 1; continue
        n = len(to_runes(g.replace("'", ''), rule))
        if n: out.append((n, sid))
    return out


# ---------------- statistics ----------------
def cls(n):
    return min(n, NCLS) - 1  # 0..7


def train_llr(seqs):
    """seqs: list of class sequences. returns 8x8 table s[a][b]=log P(b|a)/P(b)"""
    J = [[1.0] * NCLS for _ in range(NCLS)]
    for L in seqs:
        for a, b in zip(L, L[1:]): J[a][b] += 1
    tot = sum(map(sum, J)); col = [sum(J[a][b] for a in range(NCLS)) / tot for b in range(NCLS)]
    return [[math.log(J[a][b] / sum(J[a]) / col[b]) for b in range(NCLS)] for a in range(NCLS)]


def llr(L, S):
    return sum(S[a][b] for a, b in zip(L, L[1:]))


def mi(L):
    n = len(L) - 1
    j = collections.Counter(a * NCLS + b for a, b in zip(L, L[1:]))
    A = collections.Counter(L[:-1]); B = collections.Counter(L[1:])
    return sum(c / n * math.log(c * n / (A[k // NCLS] * B[k % NCLS])) for k, c in j.items())


def groups(labels):
    g = collections.OrderedDict()
    for i, l in enumerate(labels): g.setdefault(l, []).append(i)
    return list(g.values())


def shuffle_within(L, grp, rng):
    M = L[:]
    for idx in grp:
        if len(idx) > 1:
            v = [M[i] for i in idx]; rng.shuffle(v)
            for i, x in zip(idx, v): M[i] = x
    return M


def comp_G(L, labels):
    tab = collections.defaultdict(lambda: [0] * NCLS)
    for x, l in zip(L, labels): tab[l][x] += 1
    n = len(L); col = [0] * NCLS
    for r in tab.values():
        for k in range(NCLS): col[k] += r[k]
    G = 0.0
    for r in tab.values():
        rs = sum(r)
        for k in range(NCLS):
            if r[k]: G += r[k] * math.log(r[k] * n / (rs * col[k]))
    return 2 * G


def comp_SS(Lraw, labels):
    g = collections.defaultdict(list)
    for x, l in zip(Lraw, labels): g[l].append(x)
    m = sum(Lraw) / len(Lraw)
    return sum(len(a) * (sum(a) / len(a) - m) ** 2 for a in g.values())


def zp(obs, null, upper=True):
    n = len(null); m = sum(null) / n; sd = (sum((v - m) ** 2 for v in null) / n) ** .5 or 1e-12
    z = (obs - m) / sd
    p = (sum(v >= obs for v in null) + 1) / (n + 1) if upper else (sum(v <= obs for v in null) + 1) / (n + 1)
    return z, p, m, sd


def normal_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def z_for_alpha(a):
    lo, hi = 0.0, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if normal_sf(mid) > a: lo = mid
        else: hi = mid
    return hi
