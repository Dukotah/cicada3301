"""C1 acceptance test: crossdiff.py keeps relikd's page map (CHALLENGES.md, C1).

    python -m pytest challenges/c1_crossdiff_test.py -q

Fails until `load_relikd_chunks()` exists in liber-primus/analysis/transcription/crossdiff.py.
Needs the fetched sources: `python liber-primus/data/fetch_sources.py`.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import _common as C  # noqa: E402

sys.path.insert(0, os.path.join(C.LP, "analysis", "transcription"))
sys.path.insert(0, os.path.join(C.LP, "data"))

SOURCES = os.path.join(C.LP, "data", "sources")
pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(SOURCES, "relikd_p40-53.txt")),
    reason="relikd sources not fetched (python liber-primus/data/fetch_sources.py)")

EXPECTED = {  # chunk -> book pages it covers (book p50 has no runes and no segment)
    "p0-2": range(0, 3), "p3-7": range(3, 8), "p8-14": range(8, 15),
    "p15-22": range(15, 23), "p23-26": range(23, 27), "p27-32": range(27, 33),
    "p33-39": range(33, 40), "p40-53": [p for p in range(40, 54) if p != 50],
    "p54-55": range(54, 56), "p56_an_end": [56], "p57_parable": [57],
}


@pytest.fixture(scope="module")
def chunks():
    import crossdiff
    if not hasattr(crossdiff, "load_relikd_chunks"):
        pytest.fail("crossdiff.load_relikd_chunks() does not exist yet - that is the challenge")
    return crossdiff.load_relikd_chunks()


def test_all_eleven_chunks_in_order(chunks):
    assert [c["chunk"] for c in chunks] == list(EXPECTED)


def test_book_pages_and_segments(chunks):
    for c in chunks:
        assert list(c["book_pages"]) == list(EXPECTED[c["chunk"]]), c["chunk"]
        assert 50 not in c["book_pages"]
        assert list(c["segments"]) == [C.segment_of_book_page(p) for p in c["book_pages"]]


def test_rune_counts_match_canonical_segments(chunks):
    segs = C.canon_segments()
    for c in chunks:
        want = sum(len(C.gp.runes_to_indices(segs[s])) for s in c["segments"])
        assert len(c["runes"]) == want, (c["chunk"], len(c["runes"]), want)


def test_flat_loader_unchanged(chunks):
    import crossdiff
    flat = [r for c in chunks for r in c["runes"]]
    assert flat == crossdiff.load_relikd(), "load_relikd() must keep returning the same flat list"
