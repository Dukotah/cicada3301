"""Unit tests for words.py (stdlib; runnable with `python -m pytest -q test_words.py` or `python test_words.py`)."""
import os, sys, re, difflib, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import words as W

REF = os.path.join(W.LP, "analysis", "round45", "W1-spaces", "inputs", "lp1-plaintext-reference.txt")
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")
SG = {c: i for i, c in enumerate(["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P", "X", "S", "T", "B",
                                  "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y", "IA", "EA"]) if len(c) == 1}
SG.update({"K": 5, "Q": 5, "V": 1, "Z": 15})
DG = {"TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25, "IA": 27, "IO": 27, "EA": 28}


def to_runes(word):
    """GP rule R-A (the rule R45-W1 calibrated at 739/739 on the solved pages)."""
    w = word.upper().replace("'", ""); out = []; i = 0
    while i < len(w):
        if w[i:i + 3] == "ING": out.append(21); i += 3; continue
        if w[i:i + 2] in DG: out.append(DG[w[i:i + 2]]); i += 2; continue
        if w[i] in SG: out.append(SG[w[i]])
        i += 1
    return out


def ref_sections():
    sec, cur = {}, None
    for line in open(REF, encoding="utf-8").read().splitlines():
        if line.startswith("#"):
            m = re.match(r"###\s+(\d+)", line)
            if m: cur = int(m.group(1)); sec[cur] = []
            continue
        if cur is not None:
            sec[cur] += WORD_RE.findall(line)
    return sec


# ---------------------------------------------------------------- identity of the object
def test_stream_identity_and_hash():
    v = W.verify_stream()
    assert v["n_runes"] == 12956 and v["sha256"] == v["problem_sha256"] and v["page_lengths_match"]


def test_lp2_word_count_is_2896():
    P = W.lp2()
    assert len(P.words) == 2896
    assert sum(P.lengths) == 12956 and min(P.lengths) >= 1
    assert [x for w in P.words for x in w["idx"]] == P.runes          # contiguous, in order, no gaps


def test_wrapping_words_joined():
    P = W.lp2()
    assert sum(w["wraps_page"] for w in P.words) == 32
    assert sum(w["wraps_line"] for w in P.words) == 420                # 388 line-only + 32 page wraps (X1: 420)
    assert not W.straddlers(W.lp2_all(), W.N_LP2)


def test_legacy_counts_reproduced_and_only_extra_cuts():
    new = set(itertools.accumulate(W.lp2().lengths))
    for name, n in (("camp7", 3316), ("mapcommon", 2928), ("skeleton", 2928)):
        L = W.legacy_words(name)
        assert len(L) == n and sum(L) == 12956
        assert new <= set(itertools.accumulate(L))                     # legacy = new + extra cuts, never fewer


def test_parse_rules_small():
    t = "ᚠᚢ/\nᚦ-ᚩ.ᚱ&ᚳ$ᚷ§ᚹ7ᚻ/\n%\nᚾᛁ-"
    P = W.parse(t)
    assert P.lengths == [3, 1, 1, 1, 1, 1, 3]
    assert P.words[0]["wraps_line"] and not P.words[0]["wraps_page"]
    assert P.words[-1]["wraps_page"] and P.page_starts == [9] and 2 in P.line_starts
    # a line that begins with '-' does not make the previous word a wrapping word
    Q = W.parse("ᚠᚢ/\n-ᚦ")
    assert Q.lengths == [2, 1] and not Q.words[0]["wraps_line"]


def test_render_roundtrip_on_lp2_layout():
    P = W.lp2()
    words = P.word_lists()
    sent_ends = set(k for k in range(len(words) - 1) if P.words[k + 1]["sent"] != P.words[k]["sent"])
    t = W.render(words, sent_ends, P.line_starts, P.page_starts)
    Q = W.parse(t)
    assert Q.word_lists() == words and Q.line_starts == P.line_starts and Q.page_starts == P.page_starts


# ---------------------------------------------------------------- solved pages
def test_lp1_counts():
    assert len(W.lp1().words) == 694 and len(W.lp2_solved().words) == 45


def test_solved_page_A_WARNING_atbash_word_by_word():
    ref = ref_sections()[1]                                            # 'A WARNING BELIEVE NOTHING ... SACRED'
    P = W.lp1()
    dec = [[28 - c for c in w] for w in P.word_lists()[:len(ref)]]
    exp = [to_runes(x) for x in ref]
    assert dec == exp, [(i, ref[i]) for i in range(len(ref)) if dec[i] != exp[i]][:5]
    # the page has words wrapped across lines; a line-splitting loader cannot reproduce it
    assert any(w["wraps_line"] for w in P.words[:len(ref)])


def test_solved_page_PARABLE_plaintext_word_by_word():
    ref = ref_sections()[57]
    S = W.lp2_solved().word_lists()
    got = S[-len(ref):]
    assert got == [to_runes(x) for x in ref]


def test_all_solved_lengths_align_with_reference():
    sec = ref_sections()
    ref = [w for k in sorted(sec) for w in sec[k]]
    E = [len(to_runes(x)) for x in ref]
    P = W.lp1().lengths + W.lp2_solved().lengths
    sm = difflib.SequenceMatcher(None, P, E, autojunk=False)
    m = sum(b.size for b in sm.get_matching_blocks())
    assert len(P) == 739 and m / len(P) >= 0.98


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("PASS", name)
            except Exception as e:
                fails += 1; print("FAIL", name, repr(e)[:300])
    sys.exit(1 if fails else 0)
