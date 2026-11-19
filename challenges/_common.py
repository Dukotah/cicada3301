"""Shared helpers for the challenge checkers: repo paths, the canonical stream, the book-page map.

Nothing here is challenge-specific. Every checker imports it so all of them read the
same stream the same way (one code path, the R42 X1 rule).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LP = os.path.join(ROOT, "liber-primus")
for p in ("src", "benchmark", "analysis", "analysis/campaign18_skip"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import gematria as gp  # noqa: E402

N = gp.N  # 29


def canon_segments():
    """The 57 rune-bearing segments of data/krisyotam_runes.txt (0-54 unsolved, 55-56 solved)."""
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    segs = [s for s in txt.split("%") if gp.runes_to_indices(s)]
    assert len(segs) == 57, len(segs)
    return segs


def segment_of_book_page(book_page):
    """Book page -> segment index. Book p50 has no runes (data/PAGE-NUMBERING.md)."""
    if book_page == 50:
        raise ValueError("book page 50 is the token table and carries no runes")
    if not 0 <= book_page <= 57:
        raise ValueError(f"book page {book_page} is outside LP2 (0-57)")
    return book_page if book_page < 50 else book_page - 1


def page_runes(book_page):
    """Rune indices (0-28) of one book page, from the canonical stream."""
    return gp.runes_to_indices(canon_segments()[segment_of_book_page(book_page)])


def unsolved_stream():
    """(x, page) for the 12,956-rune unsolved stream, page = segment index 0-54."""
    import numpy as np
    stream, page = [], []
    for seg, s in enumerate(canon_segments()[:55]):
        for i in gp.runes_to_indices(s):
            stream.append(i)
            page.append(seg)
    x = np.asarray(stream, dtype=np.int64)
    assert len(x) == 12956, len(x)
    return x, np.asarray(page, dtype=np.int64)


def load_module(path, name="submission"):
    """Import a contributor's .py file by path."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, os.path.abspath(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
