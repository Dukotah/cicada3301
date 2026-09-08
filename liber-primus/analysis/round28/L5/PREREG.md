# L5 — payload-micro: the never-run minutes-of-compute payload tests (E-01, E-02, H-03)

_Round 28, pre-registered 2026-09-08. Mode: run-now-light (stdlib Python, minutes total,
nice -15 single-thread). Added lane (1 of the 2 permitted additions): cheapest never-run
items on the board, all named in `handoff/PARKED.md` "Not parked — merely unfinished"._

## Hypothesis

The 256-byte pp49–51 payload (`analysis/pp49_51/canon_256.bin`) is not key material or
ciphertext (both swept dead) but a **structured object**: an RSA signature/ciphertext under
a published 3301 modulus (E-01), a permutation / gap-table of meta-parameters describing the
cipher (E-02), or one of two never-executed micro-crosses resolves an external channel
(H-03: 2013 onion cookies XOR the four hex strings; 2012 P.S. digit-string rotate-90).

## Anti-repeat (ledger ids bounded against)

- **`B-05`** (negative): payload as **PRF seed / keystream source** — not as an RSA object
  or meta-parameter table. `R11` number-channel lenses: corpus numbers as data/feedback —
  not these tests. Campaign XX (`pp49_51/CAMPAIGN-XX-EXTCIPHER.md`): external-cipher
  battery — RSA-signature pattern-match and permutation-window scan absent from it.
- `handoff/PARKED.md` bottom table lists E-01, E-02, H-03 explicitly as "never run /
  never executed" with no ledger row. This lane consumes those three pointers.

## Aiming Test

**Q1 — Hit shape + recognizer (all zero-false-positive by design).**
- E-01: `pow(payload-as-int, e, n)` for every published 3301 modulus × both endiannesses ×
  both directions; recognizer = PKCS#1 v1.5 structure (`00 01 FF…FF 00 ‖ DigestInfo`) or
  PSS trailer `0xBC` — chance rate ≲2⁻⁸⁰. **Control:** construct a real PKCS#1 v1.5
  signature under a locally generated test key, run it through the detector, must fire.
- E-02a: slide every 56-byte window; recognizer = the window is a permutation of 0–55
  (chance ≈1e−24/window). **Control:** plant a shuffled range(56) window in a random
  256-byte buffer, detector must fire at the planted offset only.
- E-02b: read the payload as 8/16-bit LE/BE and varint gap streams; recognizer = Spearman
  rank-correlation vs the real doublet-gap sequence [122, 85, 249, 197, 129, …] with a
  permutation-test p < 1e-4 (Bonferroni over the ~10 encodings). **Control:** feed the real
  gap sequence itself re-encoded, must hit p≈0.
- H-03: cookie-XOR outputs scanned for printable/base32/onion shape; rotate-90 reading
  scanned for digit/ASCII structure. Recognizer thresholds written in the runner before
  execution; anything below threshold is reported as the raw statistic, not spun.

**Q2 — Measured fact above flat prior.** The payload is a held artifact of the target that
has *failed* as key, ciphertext and container (measured, B-05/VII/IX/XX) — which raises the
conditional prior of the remaining readings of the same finite object (doctrine R5 class 1).
Honest label: these are cheap completeness closures, and E-01/E-02's zero-FP recognizers
mean a null costs nothing and a hit is unmistakable.

**Q3 — Bounded?** Fully enumerable and tiny: ≤ a few thousand `pow` calls + ~200 window
tests + ~10 encodings + 2 micro-crosses. Minutes. 100% coverage of the enumerated grid.

**Q4 — Three conditionals of the negative:**
1. key/object space: published 3301 moduli only (an unpublished modulus is untouchable);
   the enumerated window sizes/encodings; the two named micro-crosses;
2. transition model: n/a (no decoder) — the structural recognizers named above, only;
3. register: printable-ASCII/base32/DigestInfo/permutation structure — a hit in a shape
   outside these recognizers is not covered.

**Q5 — Kill at 10%.** Not applicable at this cost; the only gate is that all four planted
controls fire before nulls are recorded. Cross-lane rider: if L2 flips any payload byte,
re-run E-01/E-02 on the corrected stream (seconds) and report both.

## Coverage promise (honest)

Delivered: 100% of the enumerated grid, controls-first, one RESULTS.md + ledger row.
Not covered: unpublished moduli, window sizes ≠56 for the permutation read beyond the
stated scan set, semantic readings outside the recognizer set.

---

## AMENDMENT 1 — 2026-09-08, written BEFORE any lane compute (anti-repeat narrowing)

The planner's premise ("E-01/E-02/H-03 have no ledger row") is **stale**. `LEDGER.json`
carries rows for all three ids, and per doctrine R7 the binding fields are
`coverage`/`not_covered`, which were read in full before this amendment:

- **E-01** (round 19/C1, 2026-08-26, NEGATIVE): 738 tuples over both 4096-bit 7A35090F
  moduli + the 432-bit 2013 modulus + 20 base-rate keys, 3 payload variants, both
  endiannesses, e∈{65537,3,17}, PKCS#1 v1.5/PSS/OAEP matchers with a passed strict-tier
  positive control. **Consumed remainder — its `not_covered` (b): "The 432-bit 2013
  modulus as a signing key over a 54-byte WINDOW of the payload rather than the whole
  256 bytes — all 18 of its tuples are excluded by s >= n and no windowing was
  pre-registered."** That windowed cell is the ONLY published-modulus E-01 cell still
  runnable, and this lane runs it.
- **E-02** (round 16/zeroFP, 2026-08-23, NEGATIVE): E-02A permutation windows CLOSED
  (201×56B + 57B windows, analytic FP ~1e-24 — **not re-run here**); E-02B ran uint8,
  uint16-LE, uint16-BE only. **Consumed remainder: the varint reads named in the E-02
  hypothesis text but never executed.**
- **H-03** (round 16/zeroFP, 2026-08-23, NEGATIVE): the cookie-XOR half CLOSED (64
  trials, 80% printable gate — **not re-run here**). **Consumed remainder: the 2012
  P.S. digit-string rotate-90°/matrix reading, named in the H-03 hypothesis and never
  executed by any round.**

### Amended run grid (supersedes the Q1/Q3 grid above; recognizers unchanged in kind)

**E-01w — windowed 2013-modulus check.** n = the 432-bit 2013 puzzle modulus
(`round19/C1/moduli.json`, n_hex `ae748248…9f`, e published 65537; e∈{65537,3,17} kept
for symmetry with C1). Windows: all 203 consecutive 54-byte windows × 3 payload variants
(`canon_256.bin`, `canon_256_decpref.bin`, `round19/C1/payload_resolved.bin`) × 2 byte
orders (as-is big-endian int, byte-reversed). For each s < n: m = pow(s,e,n) encoded as
54 bytes, matched with round 19/C1's exact matcher set (PKCS#1 v1.5 type 1 strict-with-
DigestInfo / type 2, EMSA-PSS embits=431, standard salt set). Additionally each raw
54-byte window is matched DIRECTLY as an EM (no pow) — the "payload carries the encoded
message itself" reading, 0 extra cost. s ≥ n cells recorded as arithmetic exclusions.
HIT = strict-tier structural match only (as C1: no tunable threshold).

**E-02v — varint gap reads.** Decodings: LEB128 (little-endian base-128) and MSB-first
base-128, each over forward and byte-reversed payload, × 3 variants = 12 decoded
sequences (incomplete trailing value dropped; sequences with <20 values recorded as
undecodable, not counted as nulls). Targets: (i) the 85 inter-doublet gaps
[85,249,197,129,127,…], (ii) the 86-value sequence [122,85,249,…] (first-doublet
position prepended — the form quoted in this PREREG's own hypothesis; verified against
`seed_sweep/ct.bin`: 12,956 runes, 86 doublets, first at 122). HIT = |Spearman ρ| > 0.5
AND permutation-test p < 1e-4 (100,000 permutations, seed 3301) — the ρ bar is round 16's
own pre-registered bar, kept identical.

**H-03r — 2012 P.S. rotate-90.** Source pinned to the primary artifact
`corpus/A-primary-artifacts/cijhho123/2012/additional docs/signed messages/final message
for 2012.txt` (3 backslash-continued lines, 40+45+46 = 131 digits). Readings: the 3-line
ragged block read column-wise in all 4 direction combinations (top↓/bottom↑ ×
left→right/right→left), plus the 131-digit concatenation and its reverse = 6 derived
strings. (131 is prime, so no other rectangular reshape exists — the 3-line layout is
the only matrix in the artifact.) Recognizers, fixed now: **HIT bars** = (R2) digit-pair
ASCII decode (00–99 → chr, printable window 32–126) ≥ 80% printable over the full
string; (R3) a ≥8-digit exact substring match against the pinned 3301 constant list
written in the runner (onion cookies, 3301/1033/761/167/509/503, key timestamps).
**Report-only statistics** (not hits, stated with analytic chance rates): occurrences of
"3301"/"1033" (~1e-4 per 4-digit window — the community claim is checked and quantified,
not adopted); Miller-Rabin primality of each derived string (~1/301 chance per 131-digit
string).

### Amended controls (3 fronts → 3 planted controls + negative FP runs, controls FIRST)

1. E-01w: locally generated 432-bit RSA key; 10 genuine PKCS#1 v1.5-SHA-1 signatures
   (54-byte EM: 00 01 FF×15 00 DigestInfo) each embedded at a random window offset of a
   random 256-byte buffer; full windowed pipeline must fire strict at the planted offset
   (≥0.90 recovery) and nowhere else. +5 PSS-SHA-1 plants. Negative: 200 random buffers
   through the same pipeline, 0 strict hits required.
2. E-02v: the real 85-gap sequence re-encoded as each varint flavour, planted as the
   payload; pipeline must report ρ=1, p<1e-4 for ≥0.90 of 10 plants (mixed flavours).
   Negative: 50 random 256-byte payloads, 0 hits above the joint bar required.
3. H-03r: 10 planted 3-line digit blocks whose column reading pair-decodes to ≥80%
   printable ASCII; pipeline must fire R2 on ≥0.90. Negative: 200 random 131-digit
   3-line blocks, R2/R3 fire rate recorded, required 0.

E-02a is NOT re-run (closed with analytic certainty, round 16). The cookie-XOR half of
H-03 is NOT re-run (closed, round 16). The whole-payload E-01 grid is NOT re-run
(closed, round 19/C1). Cross-lane rider: round 28/L2's verdict KEEPS canon (change bar
not met), so the rider condition "a contested byte flips" did NOT trigger; the
`payload_resolved.bin` variant is nevertheless swept as one of the 3 variants.

## AMENDMENT 2 — 2026-09-08, after the H-03r NEGATIVE control failed, BEFORE any real-data run

The planted-control phase ran first, as required. E-01w (v1.5 1.0, PSS 1.0, 0/200 neg),
E-02v (1.0, 0/50 neg) passed. **H-03r's negative control FAILED: 37 HIT(R2) firings on
200 random 131-digit blocks.** Cause, found analytically: the 80%-printable bar was
inherited from round 16's H-03, which gated random BYTES (P(printable byte) ≈ 0.44); a
digit PAIR 00–99 maps into ASCII 32–99, so P(printable pair) = 0.68 and the 80% bar sits
only ~2.1 sd above the noise mean — not remotely zero-FP for this alphabet.

Recalibration (fixed now, before any real reading is examined): R2 fires iff the
digit-pair decode is ≥ 0.95 printable at EITHER pair alignment (offset 0 or 1; both are
now read, since a planted message has no reason to be pair-aligned). Analytic FP:
P(X ≥ 0.95·n | p=0.68) ≈ 1.3e-6 per reading × 6 readings × 2 alignments ≈ 1.6e-5 per
block. Gate: the 200-block negative control must show 0 firings at the new bar; positive
plants (100% printable by construction) must still recover ≥ 0.90. No other bar changes.

## AMENDMENT 3 — 2026-09-08, after the main run (NEGATIVE, 0 hits), BEFORE one extra H-03r cell

The main grid returned 0 occurrences of "3301"/"1033" in all 6 pinned readings — i.e. the
community claim in `armada_osint/artifacts/raw/2012.md` ("The P.S. string rotated 90
degrees contains 3301 or 1033") does NOT reproduce on the bare 3-line digit block. In the
primary artifact, however, line 1 carries the visual "P.S. " 5-column indent, so the
VISUAL block a solver would rotate has line 1 shifted right by 5 columns. To ensure a
real arrangement cannot hide there, one additional block variant is added: line 1
indented 5 columns (non-digit cells skipped at read time), same 4 column readings, same
recognizers and bars (R2 at 0.95 per Amendment 2, R3, report-only motif/prime stats).
No bar changes; this widens coverage only.
