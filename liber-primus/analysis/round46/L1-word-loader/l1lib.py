"""R46-L1 shared plant machinery: English sentences laid over LP2's real layout, regimes a / b / b', legacy parsers.
Writes nothing.  Stdlib + (for callers that score) the repo's numpy-based panel."""
import os, sys, re, json, time, random, hashlib, bisect, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import words as W

LP = W.LP
AN = lambda *a: os.path.join(LP, "analysis", *a)


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


DET = _load("det_b6", AN("round10b", "B6-non-english-plaintext", "detectors.py"))
LP2 = W.lp2()
LINE_STARTS, PAGE_STARTS = LP2.line_starts, LP2.page_starts
PAGE_BOUNDS = [0] + PAGE_STARTS + [W.N_LP2]
_SENT = None


def sentences():
    """data/pride.txt (front 1/20 skipped, I1 convention) -> list of sentences, each a list of rune-index words
    (EN mapping of round10b/B6 detectors.text_to_runes, per word)."""
    global _SENT
    if _SENT is not None:
        return _SENT
    t = open(os.path.join(LP, "data", "pride.txt"), encoding="utf-8", errors="ignore").read()
    t = t[len(t) // 20:]
    out, cur = [], []
    for m in re.finditer(r"[A-Za-z]+|[.!?]", t):
        g = m.group()
        if g in ".!?":
            if cur: out.append(cur); cur = []
            continue
        r = [int(x) for x in DET.text_to_runes(g, "EN")]
        if r: cur.append(r)
    if cur: out.append(cur)
    _SENT = out
    return out


def page_of(pos):
    return bisect.bisect_right(PAGE_STARTS, pos)


class Plant:
    """true_words: the encipherer's word sequence (rune lists) laid from rune 0 over exactly n runes (last word cut);
    sent_ends: word indices followed by '.'; printed_lens: what the print shows (== true lens for a/b)."""
    pass


def make_plant(regime, rng, n=W.N_LP2):
    S = sentences()
    i = rng.randrange(0, len(S) - 4000)
    words, sent_ends, sent_of = [], set(), []
    tot = 0; sid = 0
    while tot < n:
        s = [list(w) for w in S[i]]; i += 1
        if regime == "b":
            rng.shuffle(s)
        for w in s:
            words.append(w); sent_of.append(sid); tot += len(w)
        sent_ends.add(len(words) - 1); sid += 1
    # cut the stream to exactly n runes (the last sentence usually overruns by more than one word)
    keep, acc = [], 0
    for w in words:
        if acc >= n: break
        keep.append(w[:n - acc]); acc += len(keep[-1])
    words = keep; sent_of = sent_of[:len(words)]
    true_lens = [len(w) for w in words]
    printed = list(true_lens)
    if regime == "bp":                                   # b': printed lengths permuted within sentence
        groups = {}
        for k, s in enumerate(sent_of): groups.setdefault(s, []).append(k)
        for ks in groups.values():
            v = [printed[k] for k in ks]; rng.shuffle(v)
            for k, x in zip(ks, v): printed[k] = x
    P = Plant()
    P.regime, P.words, P.true_lens, P.printed_lens = regime, words, true_lens, printed
    P.sent_ends = set(k for k in sent_ends if k < len(words) - 1)
    P.flat = [x for w in words for x in w]
    starts = [0]
    for l in true_lens[:-1]: starts.append(starts[-1] + l)
    P.starts = starts
    P.word_page = [page_of(s) for s in starts]
    return P


def regroup(flat, lens):
    out, i = [], 0
    for l in lens:
        out.append(flat[i:i + l]); i += l
    return out


def render_cipher(cflat, printed_lens, sent_ends):
    return W.render(regroup(cflat, printed_lens), sent_ends, LINE_STARTS, PAGE_STARTS)


# ---------------------------------------------------------------- legacy text parsers (applied to rendered text)
def legacy_parse(text, name):
    """returns (words, word_page) with the legacy rule: camp7 = any non-rune breaks, pages split at '%';
    mapcommon/skeleton = '-' '.' break, pages split at '%'."""
    words, wp = [], []
    for p, seg in enumerate(text.split("%")):
        cur = []
        for ch in seg:
            if ch in W.IDX:
                cur.append(W.IDX[ch]); continue
            brk = True if name == "camp7" else (ch in "-.")
            if brk and cur:
                words.append(cur); wp.append(p); cur = []
        if cur:
            words.append(cur); wp.append(p)
    return words, wp


def new_parse(text):
    Q = W.parse(text)
    return Q.word_lists(), [w["page"] for w in Q.words], Q


def by_page(words, wp, npages=55):
    out = [[] for _ in range(npages)]
    for w, p in zip(words, wp):
        if p < npages: out[p].append(w)
    return out


def wilson(k, n, z=1.96):
    if n == 0: return [0.0, 1.0]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    a = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - a) / d, 3), round((c + a) / d, 3)]


def h(idx):
    return hashlib.sha256(",".join(map(str, idx)).encode()).hexdigest()[:16]


def heartbeat(tag, msg):
    open(os.path.join(HERE, "heartbeat_%s.txt" % tag), "w").write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg))
