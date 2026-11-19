"""C4 checker: compare an independent page transcription to the canonical stream (CHALLENGES.md, C4).

    python challenges/c4_transcription.py --page 23 my_p23.txt    # diff your read of book page 23
    python challenges/c4_transcription.py --board                  # which pages have independent reads

Transcribe from the page image (liber-primus/data/relikd/p<N>.jpg, or any scan you trust)
WITHOUT looking at any transcription first. Put the runes in a UTF-8 text file; spaces,
line breaks and punctuation are ignored, only runes are compared. Page numbers are BOOK
pages (book p50 has no runes; see liber-primus/data/PAGE-NUMBERING.md).

A disagreement is not your mistake by default. Every published transcription descends from
one 2017 root, so a careful independent read that disagrees, with a pixel crop showing why,
is exactly how #12 and #14 found real errors.
"""
import argparse
import json
import os
import sys
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

BOARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c4_reads.json")
RUNE_PAGES = [p for p in range(58) if p != 50]


def compare(book_page, text):
    canon = C.page_runes(book_page)
    mine = C.gp.runes_to_indices(text)
    sm = SequenceMatcher(None, canon, mine, autojunk=False)
    same = sum(b.size for b in sm.get_matching_blocks())
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    return canon, mine, same, ops


def show(idx):
    return "".join(C.gp.IDX_TO_RUNE[i] for i in idx)


def board():
    reads = json.load(open(BOARD, encoding="utf-8"))
    done = {int(p) for p in reads}
    print(f"Independent reads: {len(done)}/{len(RUNE_PAGES)} rune pages\n")
    for p in sorted(done):
        for r in reads[str(p)]:
            print(f"  book p{p:<3} {r['match']:>9}  {r['by']}  ({r['date']})  {r.get('ref', '')}")
    todo = [p for p in RUNE_PAGES if p not in done]
    print(f"\nUnread ({len(todo)}): {', '.join(map(str, todo))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", nargs="?", help="your transcription (UTF-8 runes)")
    ap.add_argument("--page", type=int, help="BOOK page number")
    ap.add_argument("--board", action="store_true")
    a = ap.parse_args()
    if a.board:
        return board()
    if a.file is None or a.page is None:
        ap.error("give --page N and a transcription file, or --board")

    canon, mine, same, ops = compare(a.page, open(a.file, encoding="utf-8").read())
    seg = C.segment_of_book_page(a.page)
    print(f"C4 - book page {a.page} (segment {seg}): canonical {len(canon)} runes, yours {len(mine)}")
    print(f"agreement: {same}/{max(len(canon), len(mine))} runes matched in order\n")
    for tag, i1, i2, j1, j2 in ops:
        print(f"  {tag:8s} canonical[{i1}:{i2}] {show(canon[i1:i2]) or '-':>12}   "
              f"yours[{j1}:{j2}] {show(mine[j1:j2]) or '-'}")
    if not ops:
        print("  exact match")
    else:
        print("\nFor each difference, check the image again. If you still read it your way, file a")
        print("Data correction issue with a crop of the glyph (see CHALLENGES.md, C4).")


if __name__ == "__main__":
    main()
