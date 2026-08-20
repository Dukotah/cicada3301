#!/usr/bin/env python3
"""For a canon segment that does NOT appear verbatim in a vendored transcription,
find the best partial alignment and print the exact rune position where the two
diverge, with context. Usage:
    python locate_divergence.py <vendor/relpath/to/file> <seg_index> [<seg_index> ...]
"""
import os, sys

E = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(E, "..", ".."))
CANON_FILE = os.path.join(REPO, "liber-primus", "data", "krisyotam_runes.txt")
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
TR = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M",
      "L","NG","OE","D","A","AE","Y","IA","EA"]


def runes(t):
    return [IDX[c] for c in t if c in IDX]


def segments():
    raw = open(CANON_FILE, encoding="utf-8").read()
    return [r for r in (runes(p) for p in raw.split("%")) if r]


def show(seq):
    return "".join(GP[i] for i in seq)


def tr(seq):
    return "".join(TR[i] for i in seq)


def main():
    path = os.path.join(E, "vendor", sys.argv[1])
    hay = runes(open(path, encoding="utf-8", errors="ignore").read())
    segs = segments()
    for a in sys.argv[2:]:
        si = int(a)
        s = segs[si]
        print(f"\n=== canon segment {si} ({len(s)} runes) vs {sys.argv[1]} ===")
        # find best anchor: longest prefix of s that occurs in hay
        lo, hi = 0, len(s)
        best, bestpos = 0, -1
        # binary search on prefix length that still occurs
        while lo <= hi:
            mid = (lo + hi) // 2
            if mid == 0:
                lo = 1; continue
            pref = "".join(chr(0xE000 + x) for x in s[:mid])
            h = "".join(chr(0xE000 + x) for x in hay)
            pos = h.find(pref)
            if pos >= 0:
                best, bestpos = mid, pos
                lo = mid + 1
            else:
                hi = mid - 1
        print(f"longest matching prefix: {best}/{len(s)} runes, at file offset {bestpos}")
        if bestpos >= 0 and best < len(s):
            i = best
            print(f"  canon[{i}] = {GP[s[i]]} ({TR[s[i]]})")
            got = hay[bestpos + i] if bestpos + i < len(hay) else None
            if got is not None:
                print(f"  file [{bestpos+i}] = {GP[got]} ({TR[got]})")
            print(f"  canon ctx: ...{show(s[max(0,i-25):i])} >>{GP[s[i]]}<< {show(s[i+1:i+26])}...")
            print(f"  file  ctx: ...{show(hay[max(0,bestpos+i-25):bestpos+i])} >>"
                  f"{GP[got] if got is not None else '?'}<< "
                  f"{show(hay[bestpos+i+1:bestpos+i+26])}...")
            # how far does the tail realign?
            tail = "".join(chr(0xE000 + x) for x in s[i+1:i+41])
            h = "".join(chr(0xE000 + x) for x in hay)
            p2 = h.find(tail, bestpos + i)
            print(f"  canon tail (40 runes after divergence) re-found at file offset {p2}"
                  f" (delta {p2 - (bestpos+i+1) if p2>=0 else 'n/a'})")


if __name__ == "__main__":
    main()
