# C8 — date-indexed public pad via PGP signature timestamps — PREREG

_Round 24, lane C8. Binding: `../../../ARMADA-DOCTRINE.md`. Pre-registered before any decode.
Reduced-scope survivor per `../PLAN.md` (C8 row): needs a bounded external fetch, covers only
post-2013-09-signed pages._

## Hypothesis
A public, date-stamped random source (NIST Randomness Beacon and/or dated Bitcoin block
headers) is the one-time pad, **JOINED to each page by that page's own PGP signature creation
time** — a join key R17-PUBLIC-PAD never used (it swept beacon/blockchain as *undated*
contiguous offsets only). The pad value emitted at time T is used as the keystream for the
page signed at time T. R17's `not_covered` explicitly names "non-contiguous selections" and
"the beacon beyond 2013-11-13"; a timestamp-indexed selection is exactly that.

## STEP 0 — the two premises, validated BEFORE any decode (this is the crux)

### Premise 1 — which pages carry a usable timestamp?
The decrypt target is **LP2 / onion7 pages 0–55** (`data/campaign14/page_*.txt`, the unsolved
runic corpus; `ELIMINATION-LEDGER.md:4`). The join key requires each *target* page to carry
its own signature creation time.

Enumeration of every PGP-signed Cicada artifact in-repo (`data/scream314_lp.md`, the canonical
LP corpus) yields **exactly 8 clearsigned message blocks**, all under key `7A35090F`, all
`GnuPG v1.4.11`, extracted sig-creation-times (parsed from the armored v4 signature packets):

| blk | section in scream314_lp.md | sig-creation (UTC) | what is signed |
|----:|---|---|---|
| 0 | 00.jpg ("Liber Primus") | 2014-01-07T03:16:41Z | JPEG-hex of an OutGuess clue image |
| 1 | 01/02 intro | 2014-01-07T03:16:44Z | intro prose |
| 2 | 02.jpg ("Intus") | 2014-01-07T03:16:48Z | intro prose |
| 3 | 03.jpg | 2014-01-10T05:42:54Z | "Let the text guide you" + JPEG-hex of a clue image |
| 4 | 10.jpg (index.1) | 2014-01-19T07:39:57Z | index/instruction prose (magic-square upload task) |
| 5 | 11.jpg (index.2) | 2014-01-19T07:39:42Z | index/instruction prose |
| 6 | 12.jpg (index.3) | 2014-01-19T07:39:50Z | index/instruction prose |
| 7 | 13.jpg (index.4) | 2014-01-19T07:39:57Z | index/instruction prose |

**The mapping is explicit and it fails the join.** All 8 signatures cover *cleartext /
known-plaintext prose or JPEG-hash wrappers* on the intro and index pages. **None of the
unsolved runic ciphertext pages (04–09, 14–16 solved runes; 17–55 unsolved runes) carries any
PGP signature block at all.** The runic pages were distributed as a book/PDF of images; the
signatures are integrity metadata on the *distribution wrapper*, not per-page keys. So the
target corpus has **no per-page timestamp** to index a dated pad by. This is the finding: the
join key does not exist for the decrypt target.

### Premise 2 — does the pad source cover the dates?
The 8 timestamps are all **Jan 2014**, which is **after** the NIST Beacon v1 genesis
(2013-09-05). So *if* a target page carried one of these timestamps, the beacon would cover it,
and Bitcoin headers (genesis 2009-01) cover it a fortiori. Premise 2 PASSES on dates — but it
is moot because Premise 1 fails: there is no target page to index.

### Premise 3 — causal-direction sanity
A public random pad is unpredictable, so the author must have generated the page at/after the
pulse: the correct index is the pulse **at-or-immediately-before** the signature time. Also
noted and not ignored: **PGP sig-creation-time is attacker/author-settable** (`--faked-system-time`,
or simply a wrong clock), so even a hit would be only *suggestive*, never proof. This further
weakens the lane even in the steelman.

## Consequence for scope
Because Premise 1 fails for the decrypt target, the lane's primary verdict is **UNAVAILABLE**:
the timestamp-index join cannot be applied to the unsolved pages, since those pages carry no
timestamp. To avoid manufacturing a null, we do NOT fabricate a timestamp→page mapping.

Two things ARE still run, honestly labelled:
1. **Positive control (mandatory).** Encipher a control page FROM a real fetched beacon value
   at a known date; confirm the decoder recovers it when the pad is indexed at the RIGHT date
   and fails at wrong dates / wrong source. This validates the *pipeline* independent of the
   premise, per doctrine R1/mechanics-2. If the control fails, STOP.
2. **Steelman probe (labelled non-primary).** The only pages with a real timestamp are the
   *solved/prose* pages. As the strongest defensible test the artifacts permit, index each of
   the 8 real (page, timestamp) pairs into the fetched beacon/Bitcoin pad and run the
   recovery-gated hit function over that page's runes where runes exist (04/14/15/16 are solved
   rune pages adjacent to signed sections; the signed pages themselves are prose). This can
   only ever *reconfirm* the solved pages under their known keys or return null; it cannot
   solve LP2. It exists to close the "you never even tried the timestamp index" objection with
   a measured negative rather than an assertion.

## Instrument
- Trust anchor: `python3 tests/validate.py` = 5/5 PASS (reported in RESULTS).
- Decoder: `round20/HITFN/hitfn20.py` (driftbeam + 9-register panel + panel-max bar +
  recovery≥0.90 + held-out-3/4 reproduction). Score alone is never a hit.
- Also cover key-skip desync via the C2 pair/drift decoders where a survivor appears.
- Pad builders: reuse R17 `lib_padsweep` builders (mod29, hi/lo-nibble, byte_scaled,
  prime_to_idx, nibbles) applied to the fetched 512-bit beacon `outputValue` / block header.

## Positive control — pass/fail
- Encipher a real LP page's runes with a keystream derived from the beacon `outputValue` at a
  KNOWN date D (mod-29 additive). Decode with the pad indexed at D → **must recover ≥0.90**.
  Decode with the pad indexed at a WRONG date (and a WRONG source) → **must fail (<0.90)**.
- If the right-date recovery is < 0.90, the pipeline is wrong; STOP and report pipeline error.

## Null
Seed-3301 wrong-date / wrong-source index over the same pages (shuffle which pulse maps to
which page). Refute-by-default (R6).

## Family-wise bar
`benchmark/null.threshold_for(N)` at the actual N of (page × source × nearby-pulse) tests run;
never −5.5. Any survivor is FLAGGED-FOR-ORACLE, never auto-certified.

## Kill condition (Q5)
If Step 0 shows the decrypt-target pages carry no signature timestamp (it does), the lane is
UNAVAILABLE for its stated purpose at 0% of decode budget. We still run the control + the
labelled steelman probe, then close.

## Aiming Test (doctrine §1)
- **Q1 (would the instrument recognise a hit?)** Yes — the positive control plants a real
  beacon-derived pad and proves recovery ≥0.90 at the right date; instrument validated.
- **Q2 (measured fact raising the prior?)** R18 L1 toolchain (GnuPG 1.4.11 / Ubuntu box) +
  R17-P4 (pad is machine-applied) make an imported public byte-stream a natural hypothesis.
  BUT the specific join (per-page sig timestamp → pad offset) has **no supporting fact** because
  the target pages carry no timestamp — so the join-key prior is at the flat rate. Honest.
- **Q3 (bounded?)** Bounded and tiny: 8 real timestamps × 2 sources × few nearby pulses. The
  fetch is a handful of records, not a crawl.
- **Q4 (three conditionals)** key space = timestamp-indexed pulses at the 8 real dates;
  decoder = driftbeam + C2 pair/drift; adjudicator = 9-register panel-max.
- **Q5 (abandon at 10%)** the Step-0 premise check — already answered: abandon-as-UNAVAILABLE
  for the decrypt target.
