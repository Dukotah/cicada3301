"""Round 46 / L1 -- THE printed-word loader for LP1 and LP2 (stdlib only).

Rule (R45-W1 canonical, X1-audited; PREREG.md section 2):
  * words break at  -  .  &  $  §  and at any digit;
  * '/' (line wrap), '%' (page wrap), newline and other whitespace do NOT break a word, so words that wrap
    across a line or a page are JOINED;
  * sentence boundary at  . & $ §  ; paragraph at & ; segment at $ ; chapter at §.
The rune stream is pinned: LP2 pages 0-54 must equal dataset/liber_primus.json and hash to PROBLEM.json's
ciphertext_identity.sha256_of_comma_joined_indices.

Public API
  parse(text)            -> Parsed(runes, words, line_starts, page_starts)
  lp2()                  -> Parsed for the 12,956 unsolved runes (words wholly inside); stream verified
  lp2_all(), lp2_solved(), lp1()
  verify_stream()        -> dict of identity checks (raises on mismatch)
  legacy_words(name)     -> word-length lists of the legacy loaders, for reconciliation
  render(words, sent_ends, line_starts, page_starts) -> krisyotam-format text (for plants on LP2's layout)
"""
import os, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(LP, "data")
KRIS = os.path.join(DATA, "krisyotam_runes.txt")
RTKD = os.path.join(DATA, "sources", "rtkd_master.txt")
DATASET = os.path.join(LP, "dataset", "liber_primus.json")
PROBLEM = os.path.join(LP, "PROBLEM.json")

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(RUNES)}
BREAK = set("-.&$§")
SENT = set(".&$§")
N_LP2 = 12956
N_LP2_WORDS_TARGET = 2896


class Parsed:
    """runes: list of rune indices.  words: list of dicts
         idx (rune indices), start (global rune pos), len, page, page_end, line, line_end, sent, para, sect,
         wraps_line (bool), wraps_page (bool)
       line_starts / page_starts: rune positions at which a new printed line / page begins (excluding 0)."""

    def __init__(self, runes, words, line_starts, page_starts):
        self.runes, self.words, self.line_starts, self.page_starts = runes, words, line_starts, page_starts

    @property
    def lengths(self):
        return [w["len"] for w in self.words]

    def word_lists(self):
        return [w["idx"] for w in self.words]

    def pages_of_words(self):
        """words grouped by the page on which they START (R41 convention for per-page key reset)."""
        out = {}
        for w in self.words:
            out.setdefault(w["page"], []).append(w["idx"])
        return [out[p] for p in sorted(out)]

    def sentences(self):
        out = {}
        for k, w in enumerate(self.words):
            out.setdefault(w["sent"], []).append(k)
        return [out[s] for s in sorted(out)]


def parse(text):
    runes, words, line_starts, page_starts = [], [], [], []
    page = line = sent = para = sect = 0
    cur = None
    pend_line = pend_page = False
    last = (0, 0)                      # (page, line) of the most recent rune: a word ends where its last rune is

    def close():
        nonlocal cur, last
        if cur is not None:
            cur["len"] = len(cur["idx"]); cur["page_end"] = last[0]; cur["line_end"] = last[1]
            cur["wraps_line"] = cur["line_end"] != cur["line"]; cur["wraps_page"] = cur["page_end"] != cur["page"]
            words.append(cur)
        cur = None

    for ch in text:
        if ch in IDX:
            if pend_line and runes:
                line_starts.append(len(runes))
            if pend_page and runes:
                page_starts.append(len(runes))
            pend_line = pend_page = False
            if cur is None:
                cur = dict(idx=[], start=len(runes), page=page, line=line, sent=sent, para=para, sect=sect)
            cur["idx"].append(IDX[ch]); runes.append(IDX[ch]); last = (page, line)
        elif ch in BREAK or ch.isdigit():
            close()
            if ch in SENT: sent += 1
            if ch == "&": para += 1
            if ch == "$": sect += 1
        elif ch == "/":
            line += 1; pend_line = True
        elif ch == "%":
            page += 1; pend_page = True
            # a page break is also a line break for layout purposes (lines are numbered per stream)
            if not pend_line:
                line += 1; pend_line = True
        # whitespace / newline / anything else: ignored, does not break a word
    close()
    return Parsed(runes, words, line_starts, page_starts)


def _read(p):
    return open(p, encoding="utf-8").read()


def _cut(P, n0, n1):
    """sub-Parsed of words wholly inside rune positions [n0, n1); positions re-based to n0."""
    ws = []
    for w in P.words:
        if w["start"] >= n0 and w["start"] + w["len"] <= n1:
            x = dict(w); x["start"] -= n0; ws.append(x)
    return Parsed(P.runes[n0:n1], ws, [s - n0 for s in P.line_starts if n0 < s < n1],
                  [s - n0 for s in P.page_starts if n0 < s < n1])


def straddlers(P, n):
    return [w for w in P.words if w["start"] < n < w["start"] + w["len"]]


def lp2_all():
    return parse(_read(KRIS))


def lp2():
    P = lp2_all()
    assert not straddlers(P, N_LP2), "a word straddles the unsolved/solved boundary"
    Q = _cut(P, 0, N_LP2)
    return Q


def lp2_solved():
    P = lp2_all()
    return _cut(P, N_LP2, len(P.runes))


def lp1_text():
    t = _read(RTKD)
    i = min(t.find(r) for r in RUNES if t.find(r) >= 0)
    t = t[t.rfind("\n", 0, i) + 1:]
    kr = "".join(c for c in _read(KRIS) if c in IDX)
    tr = "".join(c for c in t if c in IDX)
    n1 = tr.find(kr[:60])
    assert n1 > 0 and tr[n1:] == kr, "rtkd LP2 part not identical to krisyotam"
    k = 0
    for pos, ch in enumerate(t):
        if ch in IDX:
            if k == n1:
                return t[:pos]
            k += 1
    raise AssertionError("LP1 cut failed")


def lp1():
    return parse(lp1_text())


def sha_indices(idx):
    return hashlib.sha256(",".join(map(str, idx)).encode()).hexdigest()


def verify_stream():
    D = json.load(open(DATASET, encoding="utf-8"))
    pages = [p for p in D["pages"] if p["page"] <= 54]
    ds = [i for p in pages for i in p["indices"]]
    want = json.load(open(PROBLEM, encoding="utf-8"))["ciphertext_identity"]["sha256_of_comma_joined_indices"]
    P = lp2()
    got = sha_indices(P.runes)
    assert len(ds) == N_LP2 and sha_indices(ds) == want, "dataset stream != PROBLEM.json"
    assert P.runes == ds and got == want, "krisyotam stream != dataset stream"
    starts = [0] + P.page_starts
    plen = [b - a for a, b in zip(starts, starts[1:] + [N_LP2])]
    assert plen == [p["n_runes"] for p in pages], "page lengths differ from dataset"
    return dict(n_runes=len(P.runes), sha256=got, problem_sha256=want, pages=len(plen), page_lengths_match=True)


# ------------------------------------------------------------------ legacy loaders (for reconciliation only)
def legacy_words(name):
    """word-length list over the 12,956 unsolved runes, reproducing each legacy loader's rule."""
    txt = _read(KRIS)
    segs = txt.split("%")[:55]
    out = []
    for seg in segs:
        cur = 0
        for ch in seg:
            if ch in IDX:
                cur += 1; continue
            if name == "camp7":                               # round41 camp7.word_pages: ANY non-rune breaks
                brk = True
            elif name == "mapcommon":                         # round10 L2-map: '-' '.' (and '%' via segs)
                brk = ch in "-."
            elif name == "skeleton":                          # skeleton/wordlen_search.lp2_words: same as mapcommon
                brk = ch in "-."
            else:
                raise ValueError(name)
            if brk and cur:
                out.append(cur); cur = 0
        if cur:
            out.append(cur)
    return out


# ------------------------------------------------------------------ rendering (plants on a real layout)
def render(words, sent_ends, line_starts, page_starts):
    """words: list of rune-index lists laid contiguously from rune 0; sent_ends: set of word indices after which a
    '.' is printed (else '-'); line_starts/page_starts: rune positions where LP2's lines/pages begin."""
    ls, ps = set(line_starts), set(page_starts)
    out = []; pos = 0
    for k, w in enumerate(words):
        for c in w:
            if pos in ps:
                out.append("/\n%\n")
            elif pos in ls:
                out.append("/\n")
            out.append(RUNES[c]); pos += 1
        out.append("." if k in sent_ends else "-")
    return "".join(out)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(verify_stream()))
    P = lp2()
    print("LP2 words", len(P.words), "wrap-line", sum(w["wraps_line"] for w in P.words),
          "wrap-page", sum(w["wraps_page"] for w in P.words))
    print("LP1 words", len(lp1().words), "solved-tail words", len(lp2_solved().words))
    for n in ("camp7", "mapcommon", "skeleton"):
        print(n, len(legacy_words(n)))
