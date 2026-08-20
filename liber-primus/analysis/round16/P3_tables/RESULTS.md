# Round 16 — lane P3 — printed random-number tables + Cicada's own published bytes

**VERDICT: NEGATIVE** over the coverage stated below, in **both** passes. No configuration
reached the pre-registered bar.

| pass | pads | builders | skip budget | offsets scanned | best raw `score_norm` | bar | HITs |
|---|---:|---|---|---:|---:|---:|---|
| main | 28/28 | 19 families × {fwd, rev} | `max_skip=3` | 2,466,258,498 | **−6.420** | −5.500 | none |
| addendum | 28/28 | `hexchars`→`nibbles`, else as above | `max_skip=8` | 3,291,058,250 | **−5.679** | −5.500 | none |
| **combined** | **28** | — | — | **5,757,316,748** (≈3,598,322,967 effective ×0.625) | **−5.679** | −5.500 | **none** |

On a scale where correct-key English sits near −4.2 and shuffle noise near −7.3, the best
result across both passes misses the bar by 0.18 — and it is a 31-rune read of a 304-byte pad
whose own null at that window reaches −6.088, so it clears its own noise floor by only 0.41.

This is a bound on *what was swept*, not a verdict on either family. See **Coverage bound**,
the **Addendum**, and **Honest limits**.

| | |
|---|---|
| Instrument | `analysis/round16/lib_padsweep.py` (dense scan → beam escalation, A1's beam/score/null) |
| Control | **PASS** — `lib_padsweep.control()`, 2026-08-19: beam recovered **8/8** planted pads at ≥95 % of runes; dense prefilter retained the true offset in **5/8** → **survival 0.625** |
| Oracle | `python liber-primus/verify_solution.py --selftest` → **SELF-TEST: PASS** (accepts a known-good key at −4.14/−4.31/−4.32, rejects a wrong one) |
| Pre-registered bar | `score_norm ≥ −5.5` **AND** `≥ null_max + 0.5` |
| `benchmark/null.threshold_for(n_trials)` | **−5.350** at the main pass's 2,466,258,498 trials, **−5.329** at the addendum's 3,291,058,250, **−5.289** over the combined 5,757,316,748 (family-wise, α=0.01). All three are *stricter* than the fixed −5.5 floor at these trial counts; the combined raw best (−5.679) misses the strictest of them by 0.39. |
| HITs | **none** in either pass — so no full-stream escalation and no refuter round was triggered |
| Machine record | `results.json` (ms=3), `results_ms8.json` (ms=8), `pads_manifest.json`, `corpus_inventory.json`, `data/run_structure.json` |

## The hypothesis

**(a) Printed random-number tables.** RAND's *A Million Random Digits with 100,000 Normal
Deviates* (1955) exists precisely so two parties can share randomness without sharing a seed —
a physical one-time pad with a permanent public record. Never swept here.

**(b) Cicada's own published high-entropy bytes, used as a pad.** Round 12's A1 swept the
author's *binaries*. Nobody had swept the bytes 3301 published **to the world**: the PGP
signature packets, the public-key packets, the 2014 hash block, the hex-dumped JPEG/MP3
payloads, the onion addresses, `canon_256`, and the 56 page JPEGs themselves — concatenated in
publication order and in reverse. Prior work used some of this material as *ciphertext* or as
*keytext* (`ELIMINATION-LEDGER.md:101`, ARMADA-20 #3/#13); using the **signature bytes as a
pad** was untried. Cf. the 2012 message: *"The key has always been right in front of your
eyes."*

## Coverage bound

> **28 pads, 112,631,095 bytes**, under **19 keystream builder families × {forward, reversed}
> = 660 (variant, sign) configurations**, both signs (`p = c − k` and `p = c + k`), at
> **every** key offset, **at skip budget `max_skip = 3`**: **2,466,258,498 offsets scanned**,
> which at the measured dense-prefilter survival of 0.625 is an honest
> **≈1,541,411,561 effective offsets**.
> Split: **77,416,040** offsets over family (a) (2.44 MB of RAND digits) and
> **2,388,842,458** over family (b) (110.19 MB of Cicada-published bytes).
>
> **Plus a second full pass over all 28 pads at `max_skip = 8` with `hexchars` replaced by
> the corrected `nibbles` reading: 3,291,058,250 further offsets** (≈2,056,911,406
> effective). See [Addendum](#addendum-max_skip8-and-the-corrected-hex-reading). The skip
> budget and the builder set are part of every coverage claim here and are stated with it.

Builders: the six byte-oriented ones from `lib_padsweep` (`mod29`, `hi_nibble`, `lo_nibble`,
`byte_scaled`, `prime_to_idx`, `hexchars` — but see the `hexchars` defect below), four
text-oriented ones added in `sweep.py`
(`textchars` via the repo's `eng_to_idx`, `charval_b64`, `charval_hex`, `charval_b32`), and
nine digit-native ones for the printed table — `dig1` (one printed digit per rune), `dig2`,
`dig2ov`, `dig3`, `dig5` (the book's own five-digit grouping), and the rejection-sampling
readings that are the textbook way to turn a decimal table into a mod-29 pad: `dig2_rej29`
(accept 00–28, discard the rest), `dig2_rej87` (accept 00–86, reduce mod 29),
`dig2ov_rej29`, `dig2_rej26` (A1Z26). Builders are applied only where they are meaningful
(digit builders on ≥80 %-digit pads; text builders on ≥95 %-printable pads), so per-pad
variant counts differ.

### Pads swept

Full name / bytes / sha256 / source for all 28 is in `pads_manifest.json`.

| pad | bytes | keys full 12,956-rune stream? | variants | offsets | best |
|---|---:|---|---:|---:|---:|
| `lp_pages_jpeg_pub` | 34,654,341 | yes | 10 | 693,086,340 | −6.773 |
| `lp_pages_jpeg_rev` | 34,654,341 | yes | 10 | 693,086,340 | −6.773 |
| `cicada_hexdumps_text_pub` | 13,390,097 | yes | 14 | 374,922,044 | −6.808 |
| `cicada_all_pub` | 6,841,185 | yes | 12 | 155,885,888 | −6.787 |
| `cicada_all_rev` | 6,841,185 | yes | 12 | 155,885,888 | −6.787 |
| `cicada_hexdumps_bytes_rev` | 6,695,048 | yes | 12 | 152,549,416 | −6.878 |
| `cicada_hexdumps_bytes_pub` | 6,695,048 | yes | 12 | 152,548,570 | −6.787 |
| `rand_digits` | 1,000,000 | yes | 32 | 44,136,712 | −6.765 |
| `rand_digits_raw_file` | 1,440,000 | yes | 14 | 33,279,328 | −6.868 |
| `cicada_key_ubuntu_b64` | 149,500 | yes | 16 | 4,220,826 | −6.874 |
| `cicada_key_ubuntu_bin` | 112,125 | yes | 12 | 2,559,426 | −6.887 |
| `cicada_sigs_b64_pub` | 41,268 | yes | 16 | 1,164,094 | −6.888 |
| `cicada_sigs_b64_rev` | 41,268 | yes | 16 | 1,164,094 | −6.816 |
| `cicada_sigs_bin_pub` | 30,951 | yes | 12 | 706,744 | −6.906 |
| `cicada_sigs_bin_rev` | 30,951 | yes | 12 | 706,744 | −6.906 |
| `cicada_key_local_b64` | 2,932 | **no** | 14 | 82,050 | −6.925 |
| `cicada_key_openpgp_b64` | 2,168 | **no** | 14 | 60,436 | −6.949 |
| `lp_hashblock_hextext` | 1,980 | **no** | 14 | 57,572 | −6.929 |
| `cicada_key_local_bin` | 2,198 | **no** | 10 | 49,442 | −6.880 |
| `cicada_key_openpgp_bin` | 1,625 | **no** | 4 | 36,526 | −7.084 |
| `lp_hashblock_bytes` | 990 | **no** | 3 | 22,136 | −7.223 |
| `onions_ext_text` | 400 | **no** | 4 | 12,044 | −6.809 |
| `onions_rev_text` | 304 | **no** | 9 | 8,966 | −6.826 |
| `onions_pub_text` | 304 | **no** | 9 | 8,964 | −6.906 |
| `canon_256` | 256 | **no** | 8 | 5,274 | −6.663 |
| `onions_ext_bin` | 250 | **no** | 7 | 5,124 | −6.420 |
| `onions_pub_bin` | 190 | **no** | 8 | 3,756 | −6.663 |
| `onions_rev_bin` | 190 | **no** | 11 | 3,754 | −6.703 |

("variants" counts builder variants; each is swept under both signs, so configurations = 2×.)

### Short pads — head-window only

**Thirteen pads are shorter than ~13,000 keystream symbols and therefore cannot key the whole
12,956-rune unsolved stream at all.** They were swept against the head window only, at the
largest window their length can carry under `max_skip=3`, with their own null measured at that
same window length:

| pad | bytes | keystream symbols | head window used |
|---|---:|---|---|
| `cicada_key_local_b64` | 2,932 | 741–2,932 | 182–400 |
| `cicada_key_local_bin` | 2,198 | 1,511–2,198 | 374–400 |
| `cicada_key_openpgp_b64` | 2,168 | 1,741–2,168 | 400 |
| `cicada_key_openpgp_bin` | 1,625 | 1,148–1,625 | 284–400 |
| `lp_hashblock_hextext` | 1,980 | 725–1,980 | 178–400 |
| `lp_hashblock_bytes` | 990 | 725–990 | 178–244 |
| `onions_ext_text` | 400 | 330–400 | 79–97 |
| `onions_pub_text` / `onions_rev_text` | 304 | 256–304 | 61–73 |
| `canon_256` | 256 | 181–256 | 42–61 |
| `onions_ext_bin` | 250 | 174–250 | 40–59 |
| `onions_pub_bin` / `onions_rev_bin` | 190 | 132–190 | 30–44 |

A negative on these means only *"this pad does not key the first 30–400 runes."* It cannot
mean more, because there is not enough pad for it to mean more. In the ms=8 addendum these
windows shrink further — `head_for` divides pad length by `max_skip+1`, so the onion pads drop
to 25–31 runes — and each pad's null is re-measured at its own ms=8 window accordingly.

## Top 20

| # | pad | builder | sign | offset | head | score_norm |
|---|---|---|---|---:|---:|---:|
| 1 | `onions_ext_bin` | hexchars_rev | +1 | 2 | 40 | −6.420 |
| 2 | `onions_pub_bin` | lo_nibble | +1 | 5 | 44 | −6.663 |
| 3 | `canon_256` | hexchars | +1 | 1 | 42 | −6.663 |
| 4 | `onions_rev_bin` | lo_nibble_rev | +1 | 5 | 44 | −6.703 |
| 5 | `rand_digits` | dig2 | +1 | 418,996 | 400 | −6.765 |
| 6 | `lp_pages_jpeg_pub` | lo_nibble | −1 | 24,252,344 | 400 | −6.773 |
| 7 | `lp_pages_jpeg_rev` | lo_nibble | −1 | 11,101,906 | 400 | −6.773 |
| 8 | `onions_pub_bin` | hexchars | +1 | 2 | 30 | −6.781 |
| 9 | `cicada_all_pub` | prime_to_idx_rev | +1 | 5,773,583 | 400 | −6.787 |
| 10 | `cicada_all_rev` | prime_to_idx_rev | +1 | 5,918,828 | 400 | −6.787 |
| 11 | `cicada_hexdumps_bytes_pub` | prime_to_idx_rev | +1 | 5,773,137 | 400 | −6.787 |
| 12 | `canon_256` | prime_to_idx_rev | +1 | 1 | 61 | −6.802 |
| 13 | `cicada_hexdumps_text_pub` | charval_hex | +1 | 1,000,772 | 400 | −6.808 |
| 14 | `onions_ext_text` | charval_b64 | +1 | 2 | 97 | −6.809 |
| 15 | `onions_rev_bin` | mod29_rev | +1 | 1 | 44 | −6.815 |
| 16 | `cicada_sigs_b64_rev` | hexchars_rev | +1 | 5,332 | 400 | −6.816 |
| 17 | `canon_256` | mod29_rev | +1 | 3 | 61 | −6.824 |
| 18 | `rand_digits` | dig2_rej26 | −1 | 85,841 | 400 | −6.824 |
| 19 | `onions_rev_text` | hi_nibble_rev | −1 | 1 | 73 | −6.826 |
| 20 | `canon_256` | lo_nibble_rev | +1 | 1 | 61 | −6.827 |

**Read this table as noise, and note its shape.** The leaderboard is dominated by the
*shortest* pads at their *smallest* head windows (a 40-rune read of a 250-byte pad at offset
2). That is the signature of a short-segment variance artefact, not of signal: fewer runes
means a noisier `score_norm`, so tiny pads float to the top of any raw ranking. The
per-configuration nulls confirm it — 27 of 28 pad-best nulls sat at `null_max ≤ −6.5` (bar
−5.500), and the single exception is exactly the leader: `onions_ext_bin`'s 40-rune null_max
was **−5.941**, lifting its bar to **−5.441**, which its −6.420 still misses by 0.98. Nothing
here was judged by reading a decode.

Nulls across all 28 pad-bests: `null_mean` ∈ [−7.532, −7.244], `null_max` ∈ [−7.048, −5.941].

Note also that four of these rows (`hexchars`/`hexchars_rev`, including the #1 row) are on a
builder that turned out to be defective — see the addendum.

## What P4's result does to this lane's priors

P4 finished and reports the anti-repeat filter is **machine, not hand-applied** — flat,
unscoped, single-lag at supp = 0.813, with lag-2..8 suppression above 1.70 % excluded at 95 %.
That cuts both ways here, and it cuts the two halves of this lane in opposite directions. It
**raises** the prior on family (b): a program that applies a uniform single-lag filter is a
program reading a pad out of a *file*, and every family-(b) pad is exactly that — a
machine-readable byte source the author already had on disk. It **lowers** the prior on family
(a): a 1,000,000-digit printed table has to be copied out by a human before a program can use
it, and P4's filter shows no human in the loop. Family (a)'s remaining live sub-case is the
narrow one where the author used a *digitised* copy of the table — which is what
`rand_digits` (the RAND datafile itself) actually is, and it is swept above.

## Honest limits

1. **This is a coverage bound, not a family verdict.** "Printed tables are dead" and "Cicada's
   published bytes are dead" are both unsupported by this run. What is supported is the boxed
   paragraph above, discounted by 0.625.
2. **Two instrument defects were found by lane P1 *after* the main pass and are corrected in
   the addendum, not in the main numbers.** `lib_padsweep.ks_hexchars` drops the digits 0–9
   (so it is the A–F subsequence, not the hex reading), and `max_skip=3` is underpowered on
   pads with constant runs — which this lane's pads have in abundance. The main pass's
   `hexchars` rows, including its #1 row, stand on the defective builder and were deliberately
   *not* re-run under that name, so that the ms=3 numbers stay comparable to
   `round12/A1`. Every claim in this document names its skip budget and builder set.
3. **The control was measured at `max_skip=3`, not at 8.** `lib_padsweep.control()` passed
   8/8 at ms=3 with survival 0.625, and the 0.625 discount is applied to both passes. P1
   measured 60/60 recovery at ms=8 on its own pad, but this lane did not re-run the plant-and-
   recover control at ms=8 against its own pads. The addendum's coverage therefore inherits a
   survival figure measured at a different skip budget.
4. **The 0.625 discount is a power limit, not a soundness limit.** The dense prefilter reads
   24 runes rigidly; the anti-repeat filter drifts the key pointer inside that window and loses
   ~37.5 % of true offsets before the beam ever sees them. A pad that keys the stream from an
   offset the prefilter dropped would be missed. Raising `PREFILTER_LEN`/`keep` is the obvious
   follow-up.
5. **Only RAND was reachable for family (a).** Tippett (1927, 41,600 digits), Kendall &
   Babington Smith (1939, 100,000), and Fisher & Yates (15,000) have no machine-readable
   public copy I could find; all three were searched for and none was swept. Note that
   Fisher & Yates at 15,000 digits is barely longer than the 12,956-rune stream and Tippett at
   41,600 is short — but "not swept" is the honest status, not "eliminated". RAND's 100,000
   *normal deviates* companion file is also not served by rand.org (403) and was not swept.
6. **`rand_digits_raw_file` did not get the digit builders.** The verbatim datafile is 76 %
   digits, below the 80 % gate, so it was swept under 14 byte/text variants only. The
   line-number-stripped `rand_digits` got all 32.
7. **`hexchars` was capped at 8 MB of pad** (`HEXCHARS_MAX`). It models "hex copy-pasted off a
   web page" — a block hash, a beacon value — which is not a thing anyone did to a
   69-million-character dump, and `eng_to_idx` is pure Python. The two 34.65 MB page-JPEG pads
   were therefore swept under 10 builders rather than 12. The hex that 3301 *actually
   published as text* is covered in full by `cicada_hexdumps_text_pub`.
8. **`textchars` was capped at 2 MB of pad** for the same pure-Python reason, and is skipped on
   all-digit pads where `eng_to_idx` returns nothing by construction.
9. **`charval_b32` was initially broken** (uppercase-only alphabet vs. lowercase onion
   addresses → empty keystream). It was fixed to fold case and the four affected text pads were
   re-swept; it changed no pad's best. Reported figures are post-fix.
10. **`corpus/` is a moving target.** Another session added 21 `ky_*` mirror files mid-run, so
   `cicada_sigs_*` concatenates **57 signature packets of which 36 are distinct**. Duplicates
   inside a concatenated pad are a mirroring artefact, not a publication event; a deduped
   36-packet run of `cicada_sigs_bin_pub` (19,548 B) done earlier in this lane scored −6.835 at
   best, i.e. the dedup does not move the answer. `pads_manifest.json`'s per-pad sha256 pins the
   exact bytes swept; `corpus_inventory.json` records the inputs.
11. **Concatenation order is part of the hypothesis and only two orders were tried** —
   publication and reverse — for `cicada_all_*`, `cicada_sigs_*`, `cicada_hexdumps_*`,
   `onions_*`, `lp_pages_jpeg_*`. Note the `_rev` **pads** reverse component order while each
   component's bytes stay forward; the `_rev` **builders** reverse the whole byte string. Both
   were swept; per-message orderings, interleavings, and date-sorted-vs-filename orderings were
   not.
12. **Nulls were computed where they can matter.** Since `bar = max(−5.5, null_max + 0.5) ≥
    −5.5` by construction, any configuration below −5.5 cannot be a HIT whatever its null is;
    n=200 shuffle nulls were run for every configuration reaching −5.5 (there were none) plus
    each pad's best as a reference (28 nulls). This is a valid adjudication, not a full
    per-configuration null table.
13. **Not swept, and adjacent:** the onion7 page JPEGs are in as raw bytes, but their
    *entropy-coded scan segments* stripped of JPEG headers are not; nor are the 2013 onion
    cookie hashes as pads (they were tested as *keytexts* in ARMADA-20 #9), the 761/1033 audio
    payloads, or the RSA modulus digits from the 2014 challenge.

## Reproduce

```bash
# 1. assemble the pads (fetches the RAND datafile, verifies its sha256 + first printed line)
python liber-primus/analysis/round16/P3_tables/build_pads.py

# 2. sweep; resumable, one checkpoint per pad in data/partial/
python liber-primus/analysis/round16/P3_tables/sweep.py
#    subset / bounded invocation:
python liber-primus/analysis/round16/P3_tables/sweep.py --only rand_digits --budget 300
#    re-collect results.json from existing checkpoints without sweeping:
python liber-primus/analysis/round16/P3_tables/sweep.py --budget 0

# 3. the instrument's own gate, and the oracle
python liber-primus/analysis/round16/lib_padsweep.py     # CONTROL: PASS, survival 0.625
python liber-primus/verify_solution.py --selftest        # SELF-TEST: PASS
```

Reproduce the single best row directly:

```python
import sys; sys.path.insert(0, r'liber-primus/analysis/round16')
sys.path.insert(0, r'liber-primus/analysis/round16/P3_tables')
import lib_padsweep as L, sweep, skipdecode as sk
b = open(r'liber-primus/analysis/round16/P3_tables/data/pads/onions_ext_bin.bin','rb').read()
K = [int(x) for x in L.ks_hexchars(b[::-1])]          # variant hexchars_rev
C = L.nc.unsolved()
print(sk.beam_decode([int(x) for x in C[:40]], K, sign=+1, o=2,
                     beam_w=120, max_skip=3)["score"])   # -> -6.420, bar -5.441
```

## Addendum: `max_skip=8` and the corrected hex reading

Lane P1 found two defects in the shared instrument after this lane's main sweep had run. Both change **power**, not soundness — they do not invalidate a measured NEGATIVE, they narrow what it covers — so both are folded in here rather than silently inherited, and the skip budget and builder set are now stated with every coverage claim above.

**Defect 1 — `lib_padsweep.ks_hexchars` drops the digits 0–9.** It runs the hex string through `eng_to_idx`, which discards non-letters, so it is the **A–F subsequence** of the hex text, not the hex reading. P1 added `ks_nibbles` (each hex character as its value 0–15, in order), deliberately outside `BUILDERS` so existing numbers stay comparable. This bit this lane in two places: the hex-text pads (`lp_hashblock_hextext`, `cicada_hexdumps_text_pub`) — though those were separately covered by this lane's own `charval_hex`, which reads all 16 values correctly — and, more importantly, **every binary pad**, where 'read the blob as hex' was never actually swept: `hi_nibble` and `lo_nibble` see the two nibble streams *separately*, never interleaved in order. `nibbles` is therefore new coverage on 28 pads. Note that the main sweep's #1 row (`onions_ext_bin` / `hexchars_rev`, −6.420) sits on the defective builder.

**Defect 2 — `max_skip=3` is underpowered on pads with constant runs.** Repeated key symbols make the anti-repeat filter burn skips without changing the key symbol; P1 measured 6/8 plant recovery at ms=3 against 60/60 at ms=8 on a run-heavy pad. This lane is squarely in that regime, and `data/run_structure.json` measures it — longest run of identical keystream symbols in the first 500 kB, worst builder per pad:

| pad | worst builder | longest run | fraction repeated |
|---|---|---:|---:|
| `rand_digits` | hi_nibble | 500,000 | 1.0000 |
| `lp_pages_jpeg_rev` | nibbles | 25,348 | 0.1499 |
| `lp_pages_jpeg_pub` | charval_hex | 8,655 | 0.3135 |
| `cicada_hexdumps_text_pub` | hi_nibble | 433 | 0.5741 |
| `cicada_all_pub` | nibbles | 118 | 0.0764 |
| `cicada_all_rev` | nibbles | 118 | 0.0794 |
| `cicada_hexdumps_bytes_pub` | nibbles | 118 | 0.0794 |
| `cicada_hexdumps_bytes_rev` | nibbles | 118 | 0.0797 |

`rand_digits` under `hi_nibble` is a **constant run of 500,000** — every ASCII digit is `0x3X`, so that whole variant is a single repeated symbol and ms=3 cannot cross it. The page JPEGs run to 25,348, and the armored-text pads repeat 20–39 % of the time.

### Addendum coverage and result

> **28 of 28 pads** re-swept at **`max_skip = 8`**, with `hexchars` replaced by `nibbles`, both signs, every offset: **3,291,058,250 offsets scanned**, ≈**2,056,911,406** effective after the 0.625 survival discount. Each pad's best is adjudicated against **its own null re-measured at ms=8** (n=200), because a larger skip budget gives the beam more freedom and lifts the null.

All 28 pads were re-swept at ms=8.

**Result: NEGATIVE (no configuration reached the bar).** Best raw `score_norm` **-5.679** (`onions_pub_text` / lo_nibble_rev sign+1, offset 6, head 31) against the pre-registered bar of −5.500. `benchmark/null.threshold_for(3,291,058,250)` = -5.329. HITs: none.

Raising the skip budget lifts scores **and** lifts the nulls, which is exactly why the null must be re-measured rather than reused — several pads' ms=8 bests now sit *below* their own ms=8 `null_max`:

| pad | best builder | head | best (ms=8) | null_max (ms=8) | bar | HIT |
|---|---|---:|---:|---:|---:|---|
| `onions_pub_text` | lo_nibble_rev | 31 | -5.679 | -6.088 | -5.500 | no |
| `onions_ext_bin` | mod29_rev | 25 | -5.756 | -5.952 | -5.452 | no |
| `onions_rev_text` | textchars | 26 | -5.797 | -5.827 | -5.327 | no |
| `onions_pub_bin` | nibbles_rev | 40 | -6.183 | -6.150 | -5.500 | no |
| `canon_256` | lo_nibble_rev | 26 | -6.304 | -6.109 | -5.500 | no |
| `onions_ext_text` | charval_b64 | 42 | -6.357 | -6.215 | -5.500 | no |
| `onions_rev_bin` | nibbles_rev | 40 | -6.506 | -6.039 | -5.500 | no |
| `rand_digits` | dig2 | 400 | -6.765 | -6.938 | -5.500 | no |
| `lp_pages_jpeg_pub` | lo_nibble | 400 | -6.773 | -6.940 | -5.500 | no |
| `lp_pages_jpeg_rev` | lo_nibble | 400 | -6.773 | -7.020 | -5.500 | no |
| `cicada_all_pub` | prime_to_idx_rev | 400 | -6.787 | -6.937 | -5.500 | no |
| `cicada_all_rev` | prime_to_idx_rev | 400 | -6.787 | -6.977 | -5.500 | no |
| `cicada_hexdumps_bytes_pub` | prime_to_idx_rev | 400 | -6.787 | -7.017 | -5.500 | no |
| `cicada_hexdumps_bytes_rev` | nibbles | 400 | -6.808 | -7.040 | -5.500 | no |
| `cicada_hexdumps_text_pub` | charval_hex | 400 | -6.808 | -6.956 | -5.500 | no |
| `rand_digits_raw_file` | prime_to_idx | 400 | -6.868 | -6.867 | -5.500 | no |
| `cicada_key_ubuntu_bin` | nibbles_rev | 400 | -6.872 | -7.017 | -5.500 | no |
| `cicada_key_ubuntu_b64` | textchars_rev | 400 | -6.874 | -6.984 | -5.500 | no |
| `cicada_sigs_b64_rev` | byte_scaled | 400 | -6.886 | -6.963 | -5.500 | no |
| `cicada_sigs_b64_pub` | nibbles_rev | 400 | -6.890 | -6.872 | -5.500 | no |
| `cicada_sigs_bin_pub` | mod29_rev | 400 | -6.906 | -6.989 | -5.500 | no |
| `cicada_sigs_bin_rev` | mod29_rev | 400 | -6.906 | -7.010 | -5.500 | no |
| `lp_hashblock_bytes` | hi_nibble | 108 | -6.917 | -6.665 | -5.500 | no |
| `cicada_key_openpgp_bin` | mod29 | 178 | -6.952 | -6.922 | -5.500 | no |
| `cicada_key_local_b64` | nibbles_rev | 400 | -6.965 | -6.982 | -5.500 | no |
| `cicada_key_openpgp_b64` | nibbles_rev | 400 | -6.987 | -6.953 | -5.500 | no |
| `cicada_key_local_bin` | lo_nibble | 242 | -7.074 | -6.864 | -5.500 | no |
| `lp_hashblock_hextext` | nibbles_rev | 400 | -7.139 | -6.953 | -5.500 | no |

Two things follow, and both are about **power, not signal**. First, `head_for` divides the pad length by `max_skip+1`, so raising ms=3 to ms=8 *shortens* the head window a short pad can carry - the onion pads drop from 40-73 runes to 25-31. Second, a shorter window plus greater beam freedom raises the score **and** the null together. The ms=8 leaderboard is therefore, again, entirely the smallest pads at their smallest windows, and the best of them (-5.679, a 31-rune read of a 304-byte pad at offset 6) misses the -5.500 bar and sits only 0.41 above its own ms=8 `null_max` of -6.088. Nothing here was judged by reading a decode.

Where a pad is long enough for the head to stay at 400, ms=8 changed essentially nothing: `rand_digits` scores **-6.765 at ms=8, identical to its ms=3 result**, so the constant-run concern - real as it is for that pad's `hi_nibble` variant - does not turn out to have been hiding anything in the printed table.


### Top 10 at ms=8

| # | pad | builder | sign | offset | head | score_norm |
|---|---|---|---|---:|---:|---:|
| 1 | `onions_pub_text` | lo_nibble_rev | +1 | 6 | 31 | -5.679 |
| 2 | `onions_ext_bin` | mod29_rev | -1 | 10 | 25 | -5.756 |
| 3 | `onions_rev_text` | textchars | +1 | 3 | 26 | -5.797 |
| 4 | `onions_ext_bin` | prime_to_idx_rev | +1 | 11 | 25 | -5.928 |
| 5 | `onions_pub_text` | charval_b64 | +1 | 2 | 31 | -6.009 |
| 6 | `onions_ext_bin` | mod29_rev | +1 | 11 | 25 | -6.076 |
| 7 | `onions_pub_bin` | nibbles_rev | +1 | 0 | 40 | -6.183 |
| 8 | `onions_ext_bin` | byte_scaled | -1 | 14 | 25 | -6.286 |
| 9 | `canon_256` | lo_nibble_rev | -1 | 10 | 26 | -6.304 |
| 10 | `onions_rev_text` | mod29 | +1 | 12 | 31 | -6.305 |

### Reproduce the addendum

```bash
python liber-primus/analysis/round16/P3_tables/sweep_ms8.py            # resumable
python liber-primus/analysis/round16/P3_tables/sweep_ms8.py --budget 0 # collect only
python liber-primus/analysis/round16/P3_tables/render_addendum.py      # this section
```
