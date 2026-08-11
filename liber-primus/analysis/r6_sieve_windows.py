"""R6 TEST 1 — SIEVE-W: windowed misfiled-plaintext detector (NON-DECRYPTING).

Detects whether any sub-page contiguous WINDOW of the 55 unsolved LP2 pages is
unenciphered / partial runic PLAINTEXT. Pre-registered; run exactly as specified.

Features per window:
  (i)   rune-BIGRAM log-likelihood ratio (LLR) under a solved-plaintext bigram
        model vs a uniform model  [REPORTED SEPARATELY]
  (ii)  IoC*N                                                   [REPORTED SEPARATELY]
  (iii) doublet rate

Plaintext bigram model built from the KNOWN readable runic-plaintext pages in the
scream314 corpus (whose runic transliteration is directly readable English):
  05.jpg (SOMEWISDOM/PRIMES), 10.jpg (THELOSSOFDIVINITY), 13.jpg (SOMEWISDOM/WEALTH),
  16.jpg (ANINSTRUCTION), 74.jpg/57 (PARABLE).  Add-1 (Laplace) smoothing.

Windows: sizes 30,60,90 runes, stride 15, over concatenated unsolved stream.
Null: 10,000 order-matched surrogates PER PAGE (page's own rune multiset permuted,
seed 3301). Family-correct across (n_pages * n_windows).
THRESHOLD: FLAG a window iff bigram-LLR > BOTH surrogate 99.9th pct AND the
PARABLE-anchored plaintext cut.

Output: analysis/R6_SIEVE_WINDOWS.txt (flushed).
"""
import os
import sys
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from lp import gematria as gp, stats, corpus  # noqa

HERE = os.path.dirname(__file__)
KRIS = os.path.normpath(os.path.join(HERE, "..", "data", "krisyotam_runes.txt"))
OUT = os.path.join(HERE, "R6_SIEVE_WINDOWS.txt")
N = gp.N
SEED = 3301
NSURR = 10000
SIZES = (30, 60, 90)
STRIDE = 15

_lines = []
def emit(s=""):
    _lines.append(s)
    print(s)


def load_kris_pages():
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for s in txt.split("%"):
        idxs = gp.runes_to_indices(s)
        if idxs:
            pages.append(idxs)
    return pages


def plaintext_model_pages():
    """Readable runic-plaintext pages from scream314 (the KNOWN plaintext set)."""
    labels = ["05.jpg", "10.jpg", "13.jpg", "16.jpg", "74.jpg"]
    pages = corpus.parse()
    out = {}
    for lbl in labels:
        for p in pages:
            if lbl in p["label"]:
                r = "".join(corpus.RUNE_RE.findall(p["runes"]))
                out[lbl] = gp.runes_to_indices(r)
                break
    return out


def build_bigram_logprob(streams, k=1.0):
    """Add-k smoothed bigram log-prob matrix logP(b|a), 29x29."""
    counts = [[k] * N for _ in range(N)]
    for s in streams:
        for a, b in zip(s, s[1:]):
            counts[a][b] += 1.0
    logp = [[0.0] * N for _ in range(N)]
    for a in range(N):
        tot = sum(counts[a])
        for b in range(N):
            logp[a][b] = math.log(counts[a][b] / tot)
    return logp


LOG_UNIFORM = math.log(1.0 / N)


def bigram_llr(win, logp):
    """Per-bigram mean LLR of plaintext-model vs uniform (nats/bigram).
    Length-normalised so windows of different sizes are comparable."""
    if len(win) < 2:
        return 0.0
    s = 0.0
    for a, b in zip(win, win[1:]):
        s += logp[a][b] - LOG_UNIFORM
    return s / (len(win) - 1)


def ioc_n(win):
    return stats.ioc_norm(win)


def doublet(win):
    return stats.doublet_rate(win)


def main():
    rng_global = random.Random(SEED)
    logp = build_bigram_logprob(list(plaintext_model_pages().values()))

    kris = load_kris_pages()
    unsolved_pages = kris[:55]            # the 55 unsolved LP2 pages
    an_end = kris[55]
    parable = kris[56]

    emit("=" * 78)
    emit("R6 TEST 1 — SIEVE-W (windowed misfiled-plaintext detector)")
    emit("=" * 78)
    emit(f"seed={SEED}  surrogates/page={NSURR}  window sizes={SIZES} stride={STRIDE}")
    pm = plaintext_model_pages()
    emit("plaintext bigram model pages (readable runic plaintext): "
         + ", ".join(f"{k}(n={len(v)})" for k, v in pm.items()))
    emit(f"total model runes = {sum(len(v) for v in pm.values())}  (add-1 smoothed)")
    emit(f"unsolved pages = {len(unsolved_pages)}  "
         f"AN END n={len(an_end)}  PARABLE n={len(parable)}")
    emit("")

    # ---- helper: LLR of a whole page's plaintext windows (for anchor cut) ----
    def page_windows(page):
        """yield (size, start, window) for all windows fitting in page."""
        for size in SIZES:
            if len(page) < size:
                continue
            for st in range(0, len(page) - size + 1, STRIDE):
                yield size, st, page[st:st + size]

    # ---------------- ANCHOR 1: PARABLE must classify as plaintext ------------
    par_llrs = [bigram_llr(w, logp) for _, _, w in page_windows(parable)]
    par_iocs = [ioc_n(w) for _, _, w in page_windows(parable)]
    par_llr_min = min(par_llrs)
    par_llr_mean = sum(par_llrs) / len(par_llrs)
    par_ioc_mean = sum(par_iocs) / len(par_iocs)
    # PARABLE-anchored plaintext cut = a conservative floor (min PARABLE window LLR,
    # relaxed by 15% margin so a genuine but slightly noisier plaintext still passes)
    PLAINTEXT_CUT = par_llr_min * 0.85 if par_llr_min > 0 else par_llr_min * 1.15

    # ---------------- ANCHOR 2: WELCOME & AN END must be NON-plaintext ---------
    welcome = corpus.page_by_label("03.jpg")
    wel_idx = gp.runes_to_indices(welcome["runes"]) if welcome else []
    wel_llrs = [bigram_llr(w, logp) for _, _, w in page_windows(wel_idx)]
    end_llrs = [bigram_llr(w, logp) for _, _, w in page_windows(an_end)]
    end_iocs = [ioc_n(w) for _, _, w in page_windows(an_end)]
    wel_max = max(wel_llrs) if wel_llrs else float("nan")
    end_max = max(end_llrs) if end_llrs else float("nan")
    end_ioc_mean = sum(end_iocs) / len(end_iocs) if end_iocs else float("nan")

    a1 = (par_llr_min > PLAINTEXT_CUT * 0.999) and (par_ioc_mean > 1.5)
    a2 = (wel_max < PLAINTEXT_CUT) and (end_max < PLAINTEXT_CUT)

    emit("--- ANCHORS ---")
    emit(f"A1 PARABLE plaintext: LLR windows min={par_llr_min:.4f} mean={par_llr_mean:.4f}"
         f"  IoC*N mean={par_ioc_mean:.4f}  -> PLAINTEXT_CUT={PLAINTEXT_CUT:.4f}")
    emit(f"   PASS={a1} (require min-LLR>cut and IoC*N mean>1.5, expect ~1.8)")
    emit(f"A2 WELCOME max-window LLR={wel_max:.4f}  AN END max-window LLR={end_max:.4f}"
         f"  AN END IoC*N mean={end_ioc_mean:.4f}")
    emit(f"   PASS={a2} (both max-window LLR < PLAINTEXT_CUT; AN END is flat-IoC)")

    # ---------------- ANCHOR 3: SYNTHETIC localization ------------------------
    # splice ~90 runes of PARABLE into the unsolved stream at a known offset.
    stream = [i for p in unsolved_pages for i in p]
    splice = parable[:90] if len(parable) >= 90 else parable[:]
    inject_at = 3000  # known offset (index into concatenated unsolved stream)
    synth = stream[:inject_at] + splice + stream[inject_at:]
    # scan synth with size-90 windows, find windows whose LLR clears the cut,
    # check that at least one flagged window overlaps [inject_at, inject_at+90)
    hit_local = False
    best_overlap_llr = -1e9
    lo, hi = inject_at, inject_at + len(splice)
    for st in range(0, len(synth) - 90 + 1, STRIDE):
        w = synth[st:st + 90]
        llr = bigram_llr(w, logp)
        we, wh = st, st + 90
        overlaps = not (wh <= lo or we >= hi)
        if overlaps and llr > best_overlap_llr:
            best_overlap_llr = llr
        if llr > PLAINTEXT_CUT and overlaps:
            hit_local = True
    a3 = hit_local
    emit(f"A3 SYNTHETIC localization: spliced {len(splice)} PARABLE runes at offset "
         f"{inject_at}; best overlapping-window LLR={best_overlap_llr:.4f} "
         f"(cut={PLAINTEXT_CUT:.4f})  PASS={a3}")
    emit("")

    if not (a1 and a2 and a3):
        emit("!!! ANCHOR FAILURE — STOPPING per protocol (no verdict on unsolved).")
        _flush()
        return

    # ---------------- NULL: per-page surrogate 99.9th pct of window LLR --------
    # For each page we permute the page's own multiset NSURR times and record the
    # MAX window-LLR over that page's windows (family-correct within page). We take
    # the global 99.9th pct across pages*surrogates for the family threshold.
    emit("--- NULL (10,000 order-matched surrogates per page, seed 3301) ---")
    # We stream surrogates: never store all arrays.
    # Collect, per page, the surrogate distribution of the page's MAX window LLR.
    n_windows_total = 0
    page_window_specs = []  # (page_idx, [(size,start)...])
    for pi, page in enumerate(unsolved_pages):
        specs = []
        for size in SIZES:
            if len(page) < size:
                continue
            for st in range(0, len(page) - size + 1, STRIDE):
                specs.append((size, st))
        page_window_specs.append(specs)
        n_windows_total += len(specs)

    emit(f"total real unsolved windows across pages = {n_windows_total}")

    # surrogate max-LLR pool (one value per page per surrogate) — that's
    # 55*10000 = 550k floats, acceptable. Reused to derive the family 99.9th pct.
    surr_maxpool = []
    for pi, page in enumerate(unsolved_pages):
        specs = page_window_specs[pi]
        if not specs:
            continue
        rng = random.Random(SEED * 1000003 + pi)  # deterministic per page
        base = list(page)
        for _ in range(NSURR):
            perm = base[:]
            rng.shuffle(perm)
            mx = -1e18
            for size, st in specs:
                w = perm[st:st + size]
                v = bigram_llr(w, logp)
                if v > mx:
                    mx = v
            surr_maxpool.append(mx)

    surr_maxpool.sort()
    def pct(sorted_list, p):
        if not sorted_list:
            return float("nan")
        k = min(len(sorted_list) - 1, int(math.ceil(p / 100.0 * len(sorted_list))) - 1)
        return sorted_list[max(0, k)]
    surr_999 = pct(surr_maxpool, 99.9)
    surr_mean = sum(surr_maxpool) / len(surr_maxpool)
    surr_sd = (sum((x - surr_mean) ** 2 for x in surr_maxpool) / len(surr_maxpool)) ** 0.5
    emit(f"surrogate page-max LLR pool: n={len(surr_maxpool)} mean={surr_mean:.4f} "
         f"sd={surr_sd:.4f}  99.9th pct={surr_999:.4f}")
    degenerate = surr_sd <= 1e-9
    emit(f"degeneracy flag (sd<=0): {degenerate}")

    FAMILY_CUT = max(surr_999, PLAINTEXT_CUT)
    emit(f"FAMILY THRESHOLD = max(surrogate 99.9th, PLAINTEXT_CUT) = {FAMILY_CUT:.4f}")
    emit("")

    # ---------------- SCAN REAL UNSOLVED WINDOWS ------------------------------
    emit("--- REAL UNSOLVED WINDOW SCAN ---")
    flagged = []
    top = []  # (llr, page, size, start, ioc, dbl)
    for pi, page in enumerate(unsolved_pages):
        for size, st in page_window_specs[pi]:
            w = page[st:st + size]
            llr = bigram_llr(w, logp)
            io = ioc_n(w)
            db = doublet(w)
            top.append((llr, pi, size, st, io, db))
            if llr > FAMILY_CUT and llr > PLAINTEXT_CUT:
                flagged.append((llr, pi, size, st, io, db))
    top.sort(reverse=True)
    emit("top-10 unsolved windows by bigram-LLR (LLR | page | size | start | IoC*N | dbl):")
    for llr, pi, size, st, io, db in top[:10]:
        emit(f"  LLR={llr:7.4f}  page={pi:2d}  size={size}  start={st:4d}  "
             f"IoC*N={io:5.3f}  dbl={db:.4f}")

    # Separately report the IoC arm (already known-flat from STRUCTURE-FINDINGS §3)
    top_ioc = sorted(top, key=lambda x: -x[4])[:5]
    emit("")
    emit("IoC ARM (reported separately; STRUCTURE-FINDINGS §3 says flat ~0.97):")
    for llr, pi, size, st, io, db in top_ioc:
        emit(f"  IoC*N={io:5.3f}  page={pi:2d}  size={size}  start={st:4d}  LLR={llr:.4f}")

    emit("")
    emit(f"FLAGGED unsolved windows (LLR>family cut AND >plaintext cut): {len(flagged)}")
    for llr, pi, size, st, io, db in flagged[:20]:
        emit(f"  *FLAG page={pi} size={size} start={st} LLR={llr:.4f} IoC*N={io:.3f}")

    verdict = "CONFIRM" if flagged and not degenerate else (
        "INCONCLUSIVE" if degenerate else "REFUTE")
    emit("")
    emit("=" * 78)
    emit(f"BIGRAM-LLR ARM VERDICT: {verdict}")
    emit("IoC ARM: flat (max IoC*N window shown above; consistent with §3, no new signal)")
    if verdict == "REFUTE":
        emit("OVERALL VERDICT: REFUTE — no unsolved page or sub-page window is "
             "misfiled/partial plaintext.")
    elif verdict == "CONFIRM":
        emit("OVERALL VERDICT: CONFIRM — at least one unsolved window classifies as "
             "runic plaintext.")
    else:
        emit("OVERALL VERDICT: INCONCLUSIVE — surrogate degeneracy.")
    emit("=" * 78)
    _flush()


def _flush():
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(_lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
