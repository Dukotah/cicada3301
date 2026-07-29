#!/usr/bin/env python3
"""H1: the base-60 256-byte table as a PER-SECTION INDEX / OFFSET table keyed to
the 14 red-section-head pages. Tests T1-T3 from LP2-STRUCTURE.txt.

An index does NOT require a keystream reset, so H1 is not refuted by the proven
cross-page continuity. We test whether ANY interpretation of the 256 table bytes
as indices/offsets lands non-randomly on the red-section structure OR yields
English on the material it selects.

Baseline English ~ -4.0 (score_norm); threshold -5.2; noise ~ -7 to -8.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from lp import gematria as gp
from lp import score

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
Q = score.default()

RED = [0, 3, 6, 7, 8, 15, 23, 27, 33, 37, 39, 40, 53, 54]  # red-section-head pages

# ---------------------------------------------------------------- load corpus
data = open(os.path.join(ROOT, "data/krisyotam_runes.txt"), encoding="utf-8").read()
segs = data.split("%")
# per-page rune index lists (only pages 0..54 are unsolved)
page_idx = []          # list of lists of rune indices, one per page
page_lines = []        # per-page list of line-start rune offsets (global)
global_idx = []        # flat rune-index stream over pages 0..54
page_bounds = []       # global rune offset where each page starts
line_starts = []       # global rune offset of every line start (594 lines)

for p in range(55):
    seg = segs[p]
    page_bounds.append(len(global_idx))
    idxs = []
    # walk chars, tracking line breaks '/' to record line starts
    at_line_start = True
    for ch in seg:
        if ch == "/":
            at_line_start = True
            continue
        if ch in gp.RUNE_TO_IDX:
            if at_line_start:
                line_starts.append(len(global_idx))
                at_line_start = False
            idxs.append(gp.RUNE_TO_IDX[ch])
            global_idx.append(gp.RUNE_TO_IDX[ch])
    page_idx.append(idxs)
page_bounds.append(len(global_idx))  # sentinel end

TABLE = list(open(os.path.join(ROOT, "analysis/pp49_51/canon_256.bin"), "rb").read())
N_RUNES = len(global_idx)
N_LINES = len(line_starts)
print(f"[setup] pages=55  total_runes={N_RUNES}  total_lines={N_LINES}  table_bytes={len(TABLE)}")
print(f"[setup] red pages ({len(RED)}): {RED}")


def sn(idxs):
    """score_norm of a list of rune indices as English."""
    return Q.score_norm(gp.indices_to_translit(idxs))


BASELINE = -4.0
THRESH = -5.2

# ================================================================= T1
# Decode the 256 table bytes as candidate INDICES and check whether they land
# on the red-section-head pages / line offsets non-randomly.
print("\n" + "=" * 70)
print("T1 : do the 256 table values concentrate on red boundaries?")
print("=" * 70)


def bootstrap_pval(observed, n_draws, hit_universe_size, n_hits_in_universe, iters=20000, seed=1):
    """Prob of >= observed hits when drawing n_draws uniform ints in
    [0, hit_universe_size) and counting how many fall in a hit-set of size
    n_hits_in_universe."""
    rng = random.Random(seed)
    ge = 0
    for _ in range(iters):
        h = 0
        for _ in range(n_draws):
            if rng.randrange(hit_universe_size) < n_hits_in_universe:
                h += 1
        if h >= observed:
            ge += 1
    return ge / iters


# T1a: bytes as PAGE indices mod 55 -> cluster on red pages?
red_set = set(RED)
pages_hit = [b % 55 for b in TABLE]
obs_a = sum(1 for p in pages_hit if p in red_set)
exp_a = len(TABLE) * len(RED) / 55.0
pval_a = bootstrap_pval(obs_a, len(TABLE), 55, len(RED))
print(f"T1a page-index (byte%55): red hits {obs_a}/{len(TABLE)}  "
      f"expected {exp_a:.1f}  p={pval_a:.4f}")

# T1b: cumulative offsets into the LINE stream -> land on red-section line starts?
# Which line indices begin a red page?
red_line_idx = set()
for p in RED:
    # first global rune offset of page p -> which line index is that?
    start = page_bounds[p]
    # find line index whose line_start == start (page always begins a line)
    if start in line_starts:
        red_line_idx.add(line_starts.index(start))
# cumulative sum of table bytes mod N_LINES
cum = 0
cum_line_hits = 0
line_hits_positions = []
for b in TABLE:
    cum = (cum + b) % N_LINES
    line_hits_positions.append(cum)
    if cum in red_line_idx:
        cum_line_hits += 1
exp_b = len(TABLE) * len(red_line_idx) / N_LINES
pval_b = bootstrap_pval(cum_line_hits, len(TABLE), N_LINES, len(red_line_idx))
print(f"T1b cumulative-offset into {N_LINES} lines: hits on red-page line-starts "
      f"{cum_line_hits}/{len(TABLE)}  expected {exp_b:.2f}  p={pval_b:.4f}")

# T1c: direct byte values as line indices (bytes 0..255, lines 0..593; take b as line# if <N_LINES)
direct_line = [b for b in TABLE if b < N_LINES]
dl_hits = sum(1 for b in direct_line if b in red_line_idx)
exp_c = len(direct_line) * len(red_line_idx) / N_LINES
pval_c = bootstrap_pval(dl_hits, len(direct_line), N_LINES, len(red_line_idx))
print(f"T1c direct byte-as-line (b<{N_LINES}, n={len(direct_line)}): red-line hits "
      f"{dl_hits}  expected {exp_c:.2f}  p={pval_c:.4f}")

# T1d: bytes as RUNE offsets into the 12956 stream -> land near page/red starts?
# treat each byte as an offset; land within +-2 runes of any red page start?
red_starts = [page_bounds[p] for p in RED]
def near_any(pos, targets, tol=2):
    return any(abs(pos - t) <= tol for t in targets)
# scale bytes into the rune range: b * (N_RUNES/256)
scaled = [int(b * N_RUNES / 256) for b in TABLE]
near_red = sum(1 for pos in scaled if near_any(pos, red_starts))
# expected: each target covers (2*tol+1) rune positions
cover = len(red_starts) * 5
exp_d = len(scaled) * cover / N_RUNES
pval_d = bootstrap_pval(near_red, len(scaled), N_RUNES, cover)
print(f"T1d byte->rune-offset near red page-starts (+-2): {near_red}/{len(scaled)}  "
      f"expected {exp_d:.2f}  p={pval_d:.4f}")

# ================================================================= T2
# Read the table in base-60 as (section, offset) PAIRS. The raw base-60 tokens
# are 2 digits each -> 256 tokens. Reinterpret pairs of TOKENS or the two base-60
# digits of each token as (section, offset).
print("\n" + "=" * 70)
print("T2 : (section, offset) pair structural consistency")
print("=" * 70)
# Re-derive base-60 digit pairs from the tokens. Reconstruct each byte's two
# base-60 digits: byte = d0*60 + d1, but bytes are 0..255 so d0 in 0..4, d1 0..59.
# That is NOT the original token layout (tokens were the SOURCE of the byte).
# The faithful reconstruction: each byte b -> (b//60, b%60) is the base-60 token.
pairs = [(b // 60, b % 60) for b in TABLE]   # (d0 in 0..4, d1 in 0..59)
d0s = [p[0] for p in pairs]
d1s = [p[1] for p in pairs]
# If d0 = section index, it must span the ~11-14 red sections. It ranges 0..4 only.
print(f"T2a first-digit (d0) range: {min(d0s)}..{max(d0s)}  distinct={sorted(set(d0s))}")
print(f"    -> d0 max is {max(d0s)}; cannot index {len(RED)} sections (needs >= {len(RED)-1}). "
      f"{'FAIL geometry' if max(d0s) < len(RED)-1 else 'possible'}")

# Alternative: treat consecutive BYTE PAIRS as (section, offset): 128 pairs.
# section = byte[2k] mod 14 (into red sections); offset = byte[2k+1].
# Build red sections: rune ranges between consecutive red pages.
red_sorted = sorted(RED)
sec_ranges = []
for i, sp in enumerate(red_sorted):
    start = page_bounds[sp]
    end = page_bounds[red_sorted[i + 1]] if i + 1 < len(red_sorted) else page_bounds[55]
    sec_ranges.append((start, end, end - start))
sec_lens = [r[2] for r in sec_ranges]
print(f"T2b red-section rune lengths ({len(sec_ranges)} sections): {sec_lens}")
byte_pairs = [(TABLE[2 * k], TABLE[2 * k + 1]) for k in range(128)]
in_range = 0
for (sb, ob) in byte_pairs:
    sec = sb % len(sec_ranges)
    seclen = sec_ranges[sec][2]
    if ob < seclen:                 # offset falls within that section's runes
        in_range += 1
# expected fraction: for a random (sec,off), P(off<seclen) with off in 0..255
exp_frac = sum(min(l, 256) for l in sec_lens) / (len(sec_ranges) * 256)
exp_in = 128 * exp_frac
print(f"T2b offsets-within-section: {in_range}/128  expected~{exp_in:.1f}  "
      f"({'consistent w/ random' if abs(in_range-exp_in)<2*math.sqrt(exp_in) else 'DEVIATES'})")

# ================================================================= T1e/decode
# The real test: use the table as a per-section SHIFT SCHEDULE or offset
# selector and see if it yields English. Try several concrete decode models.
print("\n" + "=" * 70)
print("T1e : does any index-decode yield English? (best score vs baseline)")
print("=" * 70)
results = []

# Model A: per-section constant shift. Assign each of the (up to 14) red sections
# a shift from a table byte; subtract that shift (mod 29) from every rune in the
# section. Try table byte k for section k, both signs.
for sign in (-1, +1):
    scores = []
    plain_all = []
    for si, (start, end, _l) in enumerate(sec_ranges):
        shift = TABLE[si] % 29
        seg_idx = global_idx[start:end]
        dec = [(c + sign * shift) % 29 for c in seg_idx]
        plain_all.extend(dec)
    s = sn(plain_all)
    results.append((f"A per-section const shift (table[sec]), sign={sign}", s))

# Model B: per-section running shift from table, table cycles across a section.
for sign in (-1, +1):
    plain_all = []
    ti = 0
    for si, (start, end, _l) in enumerate(sec_ranges):
        seg_idx = global_idx[start:end]
        # use a contiguous slice of the table as a repeating key for this section
        key = [TABLE[(ti + j) % 256] % 29 for j in range(len(seg_idx))]
        dec = [(c + sign * key[j]) % 29 for j, c in enumerate(seg_idx)]
        plain_all.extend(dec)
        ti += 1  # advance table start per section
    s = sn(plain_all)
    results.append((f"B per-section table-key (advance 1/sec), sign={sign}", s))

# Model C: whole-corpus running key = table bytes mod 29 repeated (baseline OTP-style,
# already known dead as a KEY, but include as control).
for sign in (-1, +1):
    key = [TABLE[j % 256] % 29 for j in range(N_RUNES)]
    dec = [(c + sign * key[j]) % 29 for j, c in enumerate(global_idx)]
    results.append((f"C table-as-repeating-key (control), sign={sign}", sn(dec)))

# Model D: table bytes select STARTING OFFSET per section into the prime keystream.
# For each section, start the prime-1 keystream at offset = table[sec], decrypt.
from lp import ciphers as cip
primes_full = cip.prime_totient_stream(N_RUNES + 300)  # (prime-1) mod 29 stream, plenty long
for sign in (-1, +1):
    plain_all = []
    for si, (start, end, _l) in enumerate(sec_ranges):
        off = TABLE[si] % 256
        seg_idx = global_idx[start:end]
        dec = [(c + sign * primes_full[off + j]) % 29 for j, c in enumerate(seg_idx)]
        plain_all.extend(dec)
    results.append((f"D per-section prime-keystream offset=table[sec], sign={sign}", sn(plain_all)))

# Model E: table byte as index -> read runes AT those indices (gather), form text.
gathered = [global_idx[b % N_RUNES] for b in TABLE]
results.append(("E gather runes at table-byte indices (%N_RUNES)", sn(gathered)))
gathered2 = [global_idx[int(b * N_RUNES / 256)] for b in TABLE]
results.append(("E2 gather runes at scaled table indices", sn(gathered2)))
# cumulative-offset gather (book-cipher-into-self)
cum = 0; gath3 = []
for b in TABLE:
    cum = (cum + b) % N_RUNES
    gath3.append(global_idx[cum])
results.append(("E3 cumulative-offset gather into corpus", sn(gath3)))

for name, s in sorted(results, key=lambda x: -x[1]):
    flag = "  <-- OVER THRESHOLD" if s > THRESH else ""
    print(f"  {s:7.3f}  {name}{flag}")

# ================================================================= T3
print("\n" + "=" * 70)
print("T3 : sexagesimal margin-art pages 34-39 encode the table dims?")
print("=" * 70)
# table blocks are 10x8, 13x8, 9x8 -> rows 10,13,9 ; cols 8. Check whether
# pages 34-39 rune/line counts reference {10,13,9,8,80,104,72,256}.
dims = {10, 13, 9, 8, 80, 104, 72, 256, 23}  # 23 = span? 34..39 is 6 pages
for p in range(34, 40):
    rc = len(page_idx[p])
    lc = segs[p].count("/")
    hits = [d for d in (rc, lc) if d in dims]
    print(f"  page {p}: runes={rc} lines={lc}  dim-match={hits if hits else 'none'}")
# 6 pages of sexagesimal art; 6 != table block count(3). line counts:
lines_34_39 = [segs[p].count("/") for p in range(34, 40)]
print(f"  lines 34-39: {lines_34_39}  sum={sum(lines_34_39)}  (table rows sum=10+13+9=32)")

# ---------------------------------------------------------------- verdict
print("\n" + "=" * 70)
best = max(s for _, s in results)
print(f"H1 BEST decode score = {best:.3f}   (baseline English {BASELINE}, threshold {THRESH})")
sig = (pval_a < 0.01 or pval_b < 0.01 or pval_c < 0.01 or pval_d < 0.01 or best > THRESH)
print(f"H1 index-concentration p-values: T1a={pval_a:.4f} T1b={pval_b:.4f} "
      f"T1c={pval_c:.4f} T1d={pval_d:.4f}")
print(f"H1 VERDICT: {'SIGNAL (escalate)' if sig else 'CLEAN NULL (sealed)'}")
