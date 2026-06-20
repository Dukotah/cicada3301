"""Cross-diff the LP2 rune transcription across the community's lineages:
  K = krisyotam  (our canonical, data/krisyotam_runes.txt)
  R = relikd     (data/sources/relikd_*.txt, independent-ish re-read, diff delimiters)
  T = rtkd/iddqd (data/sources/rtkd_master.txt, the 2017 community ROOT w/ PR fixes)

All collapse to a pure rune-index stream (every non-rune char dropped), then
global-aligned with difflib so page-break/numbering differences don't matter.
Divergences = the exact runes where the lineages disagree = candidate
transcription errors to adjudicate against the authentic page images (linecrop.py).
"""
import os, sys, glob
from difflib import SequenceMatcher

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS  # noqa: E402

DATA = os.path.join(ROOT, "data")


def runes_of(text):
    return [RUNE_TO_IDX[c] for c in text if c in RUNE_TO_IDX]


def tr(seq):
    return "".join(IDX_TO_TRANS[i] for i in seq)


def load_krisyotam():
    return runes_of(open(os.path.join(DATA, "krisyotam_runes.txt"), encoding="utf-8").read())


def load_relikd():
    order = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32",
             "p33-39", "p40-53", "p54-55", "p56_an_end", "p57_parable"]
    s = []
    for name in order:
        fn = os.path.join(DATA, "sources", f"relikd_{name}.txt")
        if os.path.exists(fn):
            s += runes_of(open(fn, encoding="utf-8").read())
    return s


def load_rtkd_lp2(kris):
    """rtkd master = LP1 + LP2; strip to LP2 by aligning to krisyotam's start."""
    full = runes_of(open(os.path.join(DATA, "sources", "rtkd_master.txt"), encoding="utf-8").read())
    head = kris[:24]
    # find krisyotam's first 24 runes inside rtkd
    for i in range(len(full) - 24):
        if full[i:i+24] == head:
            return full[i:], i
    # fallback: fuzzy — best-matching 24-window
    best, bi = -1, 0
    for i in range(len(full) - 24):
        m = sum(1 for a, b in zip(full[i:i+24], head) if a == b)
        if m > best:
            best, bi = m, i
    return full[bi:], bi


def diff(a, b, na, nb):
    sm = SequenceMatcher(None, a, b, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    print(f"\n=== {na} vs {nb} ===  ratio={sm.ratio():.5f}  "
          f"lens {len(a)}/{len(b)}  divergences={len(ops)}")
    subs = []
    for tag, i1, i2, j1, j2 in ops:
        ca, cb = a[i1:i2], b[j1:j2]
        kind = tag
        print(f"  [{kind}] @{na}{i1}: {tr(ca)!r}({len(ca)}) -> {tr(cb)!r}({len(cb)})")
        if tag == "replace" and len(ca) <= 3 and len(cb) <= 3:
            subs.append((i1, tr(ca), tr(cb)))
    return ops, subs


def main():
    K = load_krisyotam()
    R = load_relikd()
    T, off = load_rtkd_lp2(K)
    print(f"loaded: krisyotam={len(K)} relikd={len(R)} rtkd_full->LP2={len(T)} (LP1 prefix stripped at rune {off})")
    diff(K, R, "K", "R")          # canonical vs relikd
    diff(K, T, "K", "T")          # canonical vs rtkd root
    diff(R, T, "R", "T")          # relikd vs rtkd root


if __name__ == "__main__":
    main()
