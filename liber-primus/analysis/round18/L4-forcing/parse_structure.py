"""Round 18 / L4-FORCING — geometry extractor.

Turns the krisyotam transcription into the positional index sets that the C-02
forcing detector needs. Every position is an index into the SAME flat 12,956-rune
stream that lib_numchannel.unsolved() returns, so any statistic computed here is
directly comparable to every other measurement in this repo.

Gate: parse_structure.py --selftest must report 12,956 runes and byte-identical
agreement with lib_numchannel.unsolved() before any arm is trusted.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis"))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))

from lp import gematria as gp  # noqa: E402

KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")

WORD_BREAKS = set("-.")          # word separators inside a line
LINE_BREAK = "/"
PAGE_BREAK = "%"
IGNORE = set("&$§\n0123456789 \t\r")   # marks that are neither runes nor breaks


class Geometry:
    """Flat rune stream plus every boundary index set."""

    def __init__(self, n_pages=55):
        txt = open(KRIS, encoding="utf-8").read()
        self.runes = []          # rune indices 0..28
        self.page_of = []        # page id per rune
        self.line_of = []        # global line id per rune
        self.word_of = []        # global word id per rune
        self.sent_of = []        # global sentence(.)-unit id per rune
        self.pos_in_line = []
        self.pos_in_word = []

        page = 0
        line = -1
        word = -1
        sent = -1
        new_line = True
        new_word = True
        new_sent = True
        pl = pw = 0

        for ch in txt:
            if ch == PAGE_BREAK:
                page += 1
                new_line = new_word = new_sent = True
                continue
            if page >= n_pages:
                continue
            if ch == LINE_BREAK:
                new_line = True
                # a line break is NOT a word break: LP2 hyphenates across lines
                continue
            if ch in WORD_BREAKS:
                new_word = True
                if ch == ".":
                    new_sent = True
                continue
            if ch in IGNORE:
                continue
            if not gp.is_rune(ch):
                continue
            if new_line:
                line += 1
                pl = 0
                new_line = False
            if new_word:
                word += 1
                pw = 0
                new_word = False
            if new_sent:
                sent += 1
                new_sent = False
            self.runes.append(gp.RUNE_TO_IDX[ch])
            self.page_of.append(page)
            self.line_of.append(line)
            self.word_of.append(word)
            self.sent_of.append(sent)
            self.pos_in_line.append(pl)
            self.pos_in_word.append(pw)
            pl += 1
            pw += 1

        self.n = len(self.runes)
        self.n_pages = page if page < n_pages else n_pages
        self.n_lines = line + 1
        self.n_words = word + 1
        self.n_sents = sent + 1

    # ---------------------------------------------------------------- subsets
    @staticmethod
    def _firsts(group):
        out, seen = [], set()
        for i, g in enumerate(group):
            if g not in seen:
                seen.add(g)
                out.append(i)
        return out

    @staticmethod
    def _lasts(group):
        last = {}
        for i, g in enumerate(group):
            last[g] = i
        return [last[g] for g in sorted(last)]

    @staticmethod
    def _nth(group, k):
        """index of the k-th element of each group, skipping groups shorter than k+1"""
        out, cnt = [], {}
        for i, g in enumerate(group):
            c = cnt.get(g, 0)
            if c == k:
                out.append(i)
            cnt[g] = c + 1
        return out

    @staticmethod
    def _nth_last(group, k):
        idx = {}
        for i, g in enumerate(group):
            idx.setdefault(g, []).append(i)
        return [v[-1 - k] for v in idx.values() if len(v) > k]

    def subsets(self):
        return {
            "A1_line_initial": self._firsts(self.line_of),
            "A2_line_final": self._lasts(self.line_of),
            "A3_word_initial": self._firsts(self.word_of),
            "A4_word_final": self._lasts(self.word_of),
            "A5_page_initial": self._firsts(self.page_of),
            "A6_page_final": self._lasts(self.page_of),
            "A7_sentence_initial": self._firsts(self.sent_of),
            "A8_sentence_final": self._lasts(self.sent_of),
            "A9_line_second": self._nth(self.line_of, 1),
            "A10_line_penultimate": self._nth_last(self.line_of, 1),
        }

    def lines(self):
        out = {}
        for i, g in enumerate(self.line_of):
            out.setdefault(g, []).append(self.runes[i])
        return [out[g] for g in sorted(out)]

    def pages_lines(self):
        """page -> list of lines (each a list of rune indices)"""
        pg = {}
        for i, g in enumerate(self.line_of):
            pg.setdefault(self.page_of[i], {}).setdefault(g, []).append(self.runes[i])
        return [[pg[p][l] for l in sorted(pg[p])] for p in sorted(pg)]


def selftest():
    import lib_numchannel as nc
    g = Geometry()
    uns = nc.unsolved()
    ok = (g.runes == uns)
    print(f"runes           : {g.n}          (expect 12956)  {'OK' if g.n == 12956 else 'FAIL'}")
    print(f"matches nc.unsolved(): {ok}")
    print(f"pages {g.n_pages}  lines {g.n_lines}  words {g.n_words}  sentences {g.n_sents}")
    sub = g.subsets()
    for k, v in sub.items():
        print(f"  {k:22s} n={len(v):5d}  all-distinct={len(set(v)) == len(v)}")
    # doublets, cross-checked against round17's published count of 86
    d = sum(1 for i in range(1, g.n) if g.runes[i] == g.runes[i - 1])
    cross = sum(1 for i in range(1, g.n)
                if g.runes[i] == g.runes[i - 1] and g.pos_in_line[i] == 0)
    print(f"doublets        : {d}   (round17 published 86)  cross-line: {cross} (round17: 4)")
    assert ok and g.n == 12956
    print("SELFTEST PASS" if (d == 86 and cross == 4) else
          "SELFTEST PASS (rune stream) — doublet cross-check differs, see above")


if __name__ == "__main__":
    selftest()
