"""Pre-registered test H1 — "Interrupter-stripped doublet re-baseline".

EXECUTOR script. Runs the test EXACTLY as pre-registered. No mid-flight
redesign. Uses the repo's own canonical transcription (data/krisyotam_runes.txt
via run_stats.load_pages), Gematria Primus mapping (src/lp/gematria), stats
(src/lp/stats), and the documented interrupter rule (src/lp/solve, ciphers).

N = 29.  ᚠ (F) = index 0.  RNG seed fixed = 3301.

Run: PYTHONUTF8=1 python analysis/h1_interrupter_strip.py
"""
import os
import sys
import random
import math

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)  # for run_stats

from lp import gematria as gp, stats, ciphers, solve, score as _score  # noqa
from lp import corpus  # noqa
from run_stats import load_pages  # reuse the canonical loader  # noqa

N = gp.N
assert N == 29
F = gp.RUNE_TO_IDX["ᚠ"]
assert F == 0, "ᚠ must be index 0"

SEED = 3301


def line(t=""):
    print(t)


# ======================================================================
# PART A — GROUND TRUTH: reproduce the known WELCOME solve round-trip.
# ======================================================================
def part_a():
    line("=" * 70)
    line("PART A — GROUND TRUTH (WELCOME / DIVINITY, ᚠ interrupter rule)")
    line("=" * 70)
    scorer = _score.default()

    page = corpus.page_by_label("03.jpg")
    if not page or not page["runes"]:
        line("FAIL: could not load page 03.jpg runes from repo corpus.")
        return False
    runes_text = page["runes"]
    ct_idx = gp.runes_to_indices(runes_text)  # raw ciphertext indices (incl. ᚠ)

    key = gp.keyword_to_indices("DIVINITY")
    # keystream sized to number of enciphered (non-interrupter) runes; the
    # beam search advances it exactly per the documented rule.
    stream = ciphers.repeat_key(key, len(ct_idx))

    # 1+2. DECRYPT with DIVINITY under the interrupter rule (repo beam search,
    # exactly as tests/validate.py does), recovering plaintext + which ᚠ are null.
    res = solve.find_interrupters(runes_text, stream, sign=-1,
                                  beam_width=500, scorer=scorer)
    interrupters = frozenset(res["interrupters"])  # occurrence-indices of null ᚠ
    pt_text, pos = solve.decode(runes_text, stream, sign=-1,
                                interrupter_idx=interrupters)

    # sanity: the recovered plaintext must be the documented WELCOME English.
    import re
    up = re.sub(r"[^A-Z]", "", pt_text.upper())
    up = up.replace("K", "C").replace("V", "U").replace("Z", "S").replace("Q", "C")
    expect = ["WELCOME", "PILGRIM", "JOURNEY", "NECESSARY"]
    hits = [w for w in expect if w in up]
    line(f"recovered plaintext (canon, first 90): {up[:90]}")
    line(f"expected words present: {len(hits)}/{len(expect)}  {hits}")

    # Now the ROUND TRIP: re-encipher the recovered plaintext with DIVINITY,
    # re-inserting the SAME interrupter ᚠ at the SAME occurrence positions and
    # NOT advancing the key on them, and confirm we regenerate the EXACT
    # original ciphertext rune sequence.  encrypt = (plain + key) mod N.
    runes = [c for c in runes_text if c in gp.RUNE_TO_IDX]
    # Rebuild plaintext INDICES aligned to enciphered positions.
    # Re-run decode but capture plain indices (decode returns translit letters;
    # recompute indices directly from the same logic to be exact).
    pt_indices = []
    f_seen, j = 0, 0
    for ch in runes:
        if ch == "ᚠ":
            if f_seen in interrupters:
                f_seen += 1
                continue
            f_seen += 1
        c = gp.RUNE_TO_IDX[ch]
        p = (c - stream[j]) % N
        pt_indices.append(p)
        j += 1

    # Encrypt back.
    regen = []
    f_seen, j, pk = 0, 0, 0
    for ch in runes:
        if ch == "ᚠ":
            if f_seen in interrupters:
                regen.append(F)      # null ᚠ re-inserted verbatim, key NOT advanced
                f_seen += 1
                continue
            f_seen += 1
        p = pt_indices[pk]
        c = (p + stream[j]) % N      # encrypt = plain + key
        regen.append(c)
        j += 1
        pk += 1

    match = regen == runes_to_indices_list(runes)
    orig_prefix = gp.indices_to_runes(runes_to_indices_list(runes)[:24])
    regen_prefix = gp.indices_to_runes(regen[:24])
    line(f"original  ciphertext prefix: {orig_prefix}")
    line(f"regen     ciphertext prefix: {regen_prefix}")
    line(f"full ciphertext round-trip identical: {match}  "
         f"(len={len(regen)}, n_interrupters={len(interrupters)})")

    anchored = (len(hits) == len(expect)) and match
    line(f"\nPART A RESULT: {'ANCHORED' if anchored else 'NOT ANCHORED'}")
    return anchored


def runes_to_indices_list(runes):
    return [gp.RUNE_TO_IDX[c] for c in runes]


# ======================================================================
# PART B — MEASUREMENT on the full unsolved LP2 corpus.
# ======================================================================
def strip_f(idxs):
    """Delete ALL ᚠ (index 0) runes, rejoining neighbors across each deletion."""
    return [x for x in idxs if x != F]


def doublet_rate_pct(idxs):
    return 100.0 * stats.doublet_rate(idxs)


def flank_identity(idxs):
    """Of all INTERIOR ᚠ occurrences (a ᚠ b, both neighbors exist and are non-ᚠ),
    fraction where a == b. Returns (rate, n_interior_considered)."""
    same, tot = 0, 0
    for i in range(1, len(idxs) - 1):
        if idxs[i] == F:
            a, b = idxs[i - 1], idxs[i + 1]
            if a == F or b == F:
                continue  # a flanking rune is itself ᚠ -> not a clean non-ᚠ flank
            tot += 1
            if a == b:
                same += 1
    return (same / tot if tot else 0.0), tot


def unigram_collision_prob(idxs):
    """Empirical P(two independent draws equal) = sum p_i^2 over the NON-ᚠ
    unigram distribution (the appropriate 'random flank' baseline)."""
    nonf = [x for x in idxs if x != F]
    n = len(nonf)
    if n == 0:
        return 0.0
    from collections import Counter
    c = Counter(nonf)
    return sum((v / n) ** 2 for v in c.values())


def part_b(anchored):
    line("\n" + "=" * 70)
    line("PART B — MEASUREMENT ON UNSOLVED STREAM")
    line("=" * 70)
    if not anchored:
        line("Part A did not anchor; Part B numbers reported but verdict void.")

    pages = load_pages()
    # run_stats: last two LP2 pages (AN END, PARABLE) are solved -> exclude.
    unsolved = [i for p in pages[:-2] for i in p]
    n_total = len(unsolved)
    n_f = sum(1 for x in unsolved if x == F)
    line(f"unsolved corpus: {len(pages) - 2} pages, {n_total} runes, "
         f"ᚠ count = {n_f}")

    # B1. raw doublet rate (all ᚠ in place) -- sanity vs repo ~0.664%.
    dbl_raw = doublet_rate_pct(unsolved)
    line(f"\nB1 doublet%_raw (ᚠ left in)          = {dbl_raw:.4f}%  "
         f"(repo sanity ~0.664%)")

    # B2. de-ᚠ doublet rate: delete all ᚠ, rejoin, measure adjacent doublets.
    def_stream = strip_f(unsolved)
    dbl_def = doublet_rate_pct(def_stream)
    line(f"B2 doublet%_deᚠ (all ᚠ removed)      = {dbl_def:.4f}%  "
         f"(len={len(def_stream)})")

    # B3. flank-identity rate of interior ᚠ.
    fi_rate, fi_n = flank_identity(unsolved)
    coll = unigram_collision_prob(unsolved)
    line(f"B3 flank-identity rate (a ᚠ b, a==b) = {100*fi_rate:.4f}%  "
         f"(n_interior ᚠ considered = {fi_n})")
    line(f"   expected under random placement   = {100/N:.4f}% (1/29)  |  "
         f"empirical non-ᚠ unigram collision = {100*coll:.4f}%")

    # B4. ᚠ frequency vs Gematria unigram expectation (z-score).
    # Expectation under uniform 29-symbol: p = 1/29.
    p0 = 1.0 / N
    exp_f = p0 * n_total
    sd_f = math.sqrt(n_total * p0 * (1 - p0))
    z_f = (n_f - exp_f) / sd_f
    line(f"B4 ᚠ frequency = {n_f} obs vs {exp_f:.1f} exp (uniform 1/29); "
         f"z = {z_f:+.3f}  (obs freq {100*n_f/n_total:.3f}%, exp {100*p0:.3f}%)")

    return {
        "unsolved": unsolved, "n_total": n_total, "n_f": n_f,
        "dbl_raw": dbl_raw, "dbl_def": dbl_def,
        "fi_rate": fi_rate, "fi_n": fi_n, "coll": coll,
    }


# ======================================================================
# NULL MODEL — 10,000 order-matched surrogates (ᚠ positions permuted).
# ======================================================================
def null_model(bundle, n_surrogates=10000):
    line("\n" + "=" * 70)
    line(f"NULL MODEL — {n_surrogates} surrogates (ᚠ positions permuted, "
         f"same multiset & ᚠ count)")
    line("=" * 70)
    unsolved = bundle["unsolved"]
    n_total = bundle["n_total"]
    n_f = bundle["n_f"]

    # The non-ᚠ runes, IN THEIR ORIGINAL ORDER. A surrogate = choose n_f of the
    # n_total slots to be ᚠ (uniformly at random), fill the rest with the non-ᚠ
    # runes in order. This preserves unigram distribution and ᚠ count and
    # destroys any doublet-avoiding ᚠ placement, exactly as pre-registered.
    nonf = [x for x in unsolved if x != F]
    assert len(nonf) == n_total - n_f
    positions = list(range(n_total))

    rng = random.Random(SEED)
    dbl_defs = []
    fi_rates = []
    for _ in range(n_surrogates):
        f_pos = set(rng.sample(positions, n_f))
        surro = [0] * n_total
        it = iter(nonf)
        for p in range(n_total):
            surro[p] = F if p in f_pos else next(it)
        # stat 1: de-ᚠ doublet rate (identical to nonf order -> constant!)
        # NOTE: removing ᚠ from a surrogate always yields `nonf` in order, so
        # doublet%_deᚠ of every surrogate == doublet%_deᚠ of nonf. Compute it
        # once but record per-surrogate for the reported distribution.
        dbl_defs.append(doublet_rate_pct([x for x in surro if x != F]))
        # stat 2: flank-identity of interior ᚠ in the surrogate
        fr, _ = flank_identity(surro)
        fi_rates.append(100.0 * fr)

    def dist(v):
        v2 = sorted(v)
        m = sum(v2) / len(v2)
        sd = math.sqrt(sum((x - m) ** 2 for x in v2) / len(v2))
        p99 = v2[min(len(v2) - 1, int(math.ceil(0.99 * len(v2))) - 1)]
        return m, sd, p99, v2[0], v2[-1]

    m1, sd1, p99_1, mn1, mx1 = dist(dbl_defs)
    m2, sd2, p99_2, mn2, mx2 = dist(fi_rates)
    line(f"surrogate doublet%_deᚠ : mean={m1:.4f}  sd={sd1:.4f}  "
         f"99th={p99_1:.4f}  [min {mn1:.4f}, max {mx1:.4f}]")
    line("   (note: deleting permuted ᚠ always restores the non-ᚠ runes in their "
         "original order, so this statistic is constant across surrogates)")
    line(f"surrogate flank-identity : mean={m2:.4f}  sd={sd2:.4f}  "
         f"99th={p99_2:.4f}  [min {mn2:.4f}, max {mx2:.4f}]")
    return {"dbl_def_p99": p99_1, "fi_p99": p99_2,
            "dbl_def_mean": m1, "fi_mean": m2}


# ======================================================================
# DIAGNOSTIC — within-word doublet rate (no ᚠ, no separator between the pair).
# ======================================================================
def diagnostic_within_word():
    line("\n" + "=" * 70)
    line("DIAGNOSTIC — within-word doublet rate (adjacent pair, no ᚠ, no sep)")
    line("=" * 70)
    # Rebuild from the raw krisyotam text so separators are visible. run_stats
    # splits on '%' (page break); word sep is '-', line break '/', title '.'.
    KRIS = os.path.normpath(os.path.join(HERE, "..", "data", "krisyotam_runes.txt"))
    txt = open(KRIS, encoding="utf-8").read()
    segs = txt.split("%")
    # unsolved = all but last two pages that actually contain runes
    rune_segs = [s for s in segs if gp.runes_to_indices(s)]
    unsolved_segs = rune_segs[:-2]

    pairs = 0
    doubles = 0
    excl_f = 0
    for s in unsolved_segs:
        prev = None
        for ch in s:
            if ch in gp.RUNE_TO_IDX:
                idx = gp.RUNE_TO_IDX[ch]
                if prev is not None:
                    # adjacent runes with NO intervening separator char
                    if prev == F or idx == F:
                        excl_f += 1
                    else:
                        pairs += 1
                        if prev == idx:
                            doubles += 1
                prev = idx
            else:
                # any non-rune char (sep/line/title/space) breaks adjacency
                prev = None
    rate = 100.0 * doubles / pairs if pairs else 0.0
    line(f"within-word non-ᚠ adjacent pairs = {pairs}, doublets = {doubles} "
         f"-> {rate:.4f}%  (pairs touching ᚠ excluded = {excl_f})")
    line("   (probes suppression where NO interrupter could be acting)")
    return rate


def main():
    anchored = part_a()
    bundle = part_b(anchored)
    nulls = null_model(bundle, n_surrogates=10000)
    diagnostic_within_word()

    line("\n" + "=" * 70)
    line("VERDICT (fixed pre-registered threshold)")
    line("=" * 70)
    dbl_def = bundle["dbl_def"]
    p99 = nulls["dbl_def_p99"]
    cond1 = dbl_def >= 2.9
    cond2 = dbl_def > p99
    confirm = cond1 and cond2
    line(f"doublet%_deᚠ = {dbl_def:.4f}%  |  threshold >= 2.9%  -> {cond1}")
    line(f"doublet%_deᚠ > 99th pct surrogate ({p99:.4f}%) -> {cond2}")
    line(f"\n{'CONFIRM H1' if confirm else 'REFUTE H1'}")
    if not anchored:
        line("(WARNING: Part A did not anchor -> verdict is not method-valid.)")


if __name__ == "__main__":
    main()
