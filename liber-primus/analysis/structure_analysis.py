"""Novel structural probes that could surface a method/lead (run on the
delimiter-rich rtkd/iddqd transcription, restricted to the unsolved LP2 pages).

  1. INTERRUPTER (ᚠ) structure  -- the F-interrupter is an authorial choice.
     Per-page F counts, gaps between F runes, and the F/not-F mask as a bitstream
     -> tested for ASCII text and against prime/fibonacci/totient sequences.
  2. KEYSTREAM-BOUNDARY RESET  -- does the no-repeat suppression (doublet 0.66%)
     hold across page / paragraph / clause / line boundaries, or RESET at them?
     A boundary where doublets jump to ~random means the keystream restarts there
     -> shorter effective key windows + in-depth attack become possible.
  3. PER-PAGE FINGERPRINT  -- cluster the 55 unsolved pages by IoC/doublet/entropy
     to find any OUTLIER page that isn't OTP-flat (the best attack target).

Run: python analysis/structure_analysis.py
"""
import os, sys, math
from collections import Counter

try:  # cross-platform: don't crash printing runes under Windows cp1252
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "data"))
from lp import gematria as gp            # noqa: E402
from lp.stats import ioc_norm, doublet_rate, shannon_entropy  # noqa: E402
from fetch_sources import ensure_sources  # noqa: E402

RTKD = os.path.join(ROOT, "data", "sources", "rtkd_master.txt")
N = 29
F = 0
DELIMS = {"-": "word", ".": "clause", "&": "paragraph", "$": "segment",
          "§": "chapter", "/": "line", "%": "page"}


def tokenize(text):
    """-> list of pages; each page = list of tokens, token is ('r', idx) or ('d', name)."""
    pages, cur = [], []
    for ch in text:
        if ch in gp.RUNE_TO_IDX:
            cur.append(("r", gp.RUNE_TO_IDX[ch]))
        elif ch == "%":
            pages.append(cur); cur = []
        elif ch in DELIMS:
            cur.append(("d", DELIMS[ch]))
    if cur:
        pages.append(cur)
    return pages


def lp2_unsolved(pages):
    # find the page that starts with krisyotam's SHEOGMIAF (onion7 page 0)
    head = gp.runes_to_indices("ᛋᚻᛖᚩᚷᛗᛡᚠ")
    start = None
    for i, p in enumerate(pages):
        runes = [v for t, v in p if t == "r"]
        if runes[:8] == head:
            start = i; break
    assert start is not None, "LP2 start not found"
    return pages[start:start + 56]  # 0..55 (AN END=56, PARABLE=57 excluded)


# ---- 1. interrupter structure -------------------------------------------
def gen_primes(n):
    out, c = [], 2
    while len(out) < n:
        if all(c % p for p in out if p * p <= c):
            out.append(c)
        c += 1
    return out


def probe_interrupter(pages):
    counts, all_gaps, masks = [], [], []
    for p in pages:
        runes = [v for t, v in p if t == "r"]
        fpos = [i for i, v in enumerate(runes) if v == F]
        counts.append(len(fpos))
        all_gaps += [fpos[i] - fpos[i-1] for i in range(1, len(fpos))]
        masks.append("".join("1" if v == F else "0" for v in runes))
    print("1. INTERRUPTER (ᚠ) structure")
    print(f"   F-count per unsolved page (n={len(counts)}): {counts}")
    primes = gen_primes(len(counts))
    fib = [1, 2]
    while len(fib) < len(counts): fib.append(fib[-1] + fib[-2])
    print(f"   == primes?  {counts == primes}   == fibonacci? {counts == fib[:len(counts)]}")
    print(f"   F-count stats: total={sum(counts)} min={min(counts)} max={max(counts)} "
          f"mean={sum(counts)/len(counts):.2f}")
    gc = Counter(all_gaps)
    print(f"   gaps between F (pooled n={len(all_gaps)}): top={gc.most_common(6)} "
          f"mean={sum(all_gaps)/len(all_gaps):.2f}")
    # F-mask -> ASCII test (per page, MSB-first)
    hits = 0
    for i, m in enumerate(masks):
        b = bytes(int(m[j:j+8], 2) for j in range(0, len(m) - 7, 8))
        printable = sum(32 <= x < 127 for x in b) / max(1, len(b))
        if printable > 0.85 and len(b) >= 4:
            hits += 1
            print(f"   * page {i}: F-mask decodes to mostly-ASCII: {b[:40]!r}")
    print(f"   F-mask-as-ASCII hits: {hits}/{len(masks)} "
          f"({'investigate' if hits else 'none -> F-mask is not hidden ASCII'})")


# ---- 2. keystream-boundary reset ----------------------------------------
def probe_boundaries(pages):
    # classify each adjacent rune pair by the strongest delimiter between them
    levels = ["none", "word", "clause", "line", "paragraph", "segment", "chapter", "page"]
    rank = {n: i for i, n in enumerate(levels)}
    pair_eq = {n: [0, 0] for n in levels}  # name -> [equal, total]
    # build a global token stream across pages with explicit page delimiters
    stream = []
    for p in pages:
        stream += p + [("d", "page")]
    prev_rune = None
    between = "none"
    for t, v in stream:
        if t == "d":
            if rank.get(v, 0) > rank[between]:
                between = v
        else:  # rune
            if prev_rune is not None:
                pair_eq[between][0] += (v == prev_rune)
                pair_eq[between][1] += 1
            prev_rune = v
            between = "none"
    print("\n2. KEYSTREAM-BOUNDARY RESET (doublet rate by what separates the pair)")
    print(f"   {'boundary':>10} {'pairs':>7} {'doublet':>8}   (random=0.0345; native within-word=suppressed)")
    base = None
    for n in levels:
        eq, tot = pair_eq[n]
        if tot < 20:
            continue
        rate = eq / tot
        if n == "none":
            base = rate
        flag = ""
        if base is not None and n != "none" and rate > 0.025:
            flag = "  <-- RESETS toward random (keystream restart? attackable)"
        print(f"   {n:>10} {tot:>7} {rate:>8.4f}{flag}")
    print("   (if any boundary's doublet ~0.0345 while 'none'/'word' stays ~0.007,")
    print("    the keystream resets at that boundary -> in-depth attack at boundaries)")


# ---- 3. per-page fingerprint outliers -----------------------------------
def probe_pages(pages):
    print("\n3. PER-PAGE FINGERPRINT (outliers = best attack targets)")
    rows = []
    for i, p in enumerate(pages):
        r = [v for t, v in p if t == "r"]
        rows.append((i, len(r), ioc_norm(r), doublet_rate(r), shannon_entropy(r)))
    iocs = [x[2] for x in rows]
    mean = sum(iocs) / len(iocs)
    sd = (sum((x - mean) ** 2 for x in iocs) / len(iocs)) ** 0.5
    print(f"   IoC_norm across pages: mean={mean:.3f} sd={sd:.3f} "
          f"(English-class ~1.7; flat ~1.0)")
    rows.sort(key=lambda x: -x[2])
    print("   most non-flat pages (highest IoC):")
    for i, n, io, db, en in rows[:6]:
        flag = "  <-- OUTLIER" if io > mean + 2.5 * sd else ""
        print(f"     page {i:>2}: len={n:>3} IoC={io:.3f} doublet={db:.4f} entropy={en:.3f}{flag}")


if __name__ == "__main__":
    if not os.path.exists(RTKD):
        ensure_sources()
    pages = lp2_unsolved(tokenize(open(RTKD, encoding="utf-8").read()))
    nr = sum(1 for p in pages for t, _ in p if t == "r")
    print(f"unsolved LP2 (rtkd): {len(pages)} pages, {nr} runes\n")
    probe_interrupter(pages)
    probe_boundaries(pages)
    probe_pages(pages)
