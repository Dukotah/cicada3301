# Round 18 · Lane L5 — PAYLOAD CLOSURE · RESULTS

_Status: **A-04 COMPLETE. E-01 COMPLETE** (null, controls passed). Propagation complete except
the B-05 beam grid, which is running as a background job. Written 2026-08-26._

Scope: **A-04** (the 6 contested bytes of the pp49–51 256-byte payload) and **E-01**
(payload as an RSA signature/ciphertext under 3301's published moduli — the Round 16
coverage gap "the 7A35090F RSA-4096 moduli were not fetched").
Pre-registration: `PREREG.md`, binding; no threshold in it was edited.

## 0. Provenance of this run

A first agent built the grid/crop/calibration/glyphmatch/moduli pipeline and was killed by an
infrastructure fault before writing any results. Its artifacts were on disk; its claim that
"all six cells read concordantly" was **not**, so nothing was inherited on trust. Every
number below was re-derived in this run, and the adjudication was redone with a **new,
independent instrument** (`pixelmatch.py`) that did not exist in the first agent's work.

## 1. Instrument validation — the licence

### 1.0 Input integrity (PREREG A.2.1 — a hard stop)

`p49.jpg`, `p50.jpg`, `p51.jpg`, `canon_256.bin` and `canon_256_decpref.bin` all match their
`handoff/capsule/MANIFEST.json` SHA-256 exactly. Gate passed; pixels were read only after this.

### 1.1 Grid (PREREG A.2.2)

`grid.py` derives cells by projection profiling, not typed coordinates, and reproduces
**80 / 104 / 72 = 256** cells for p49 / p50 / p51 — the pre-registered validation count.
253 of the 256 cells segment into exactly two glyphs; **186, 210 and 211 do not** (they fuse
or shatter under the column-gap split). None of the 11 conflict cells is among them, so this
does not touch the adjudication; it is recorded as a coverage hole in §6.

### 1.2 Visual calibration — the pre-registered gate

40 uncontested cells drawn by the pre-registered rule `random.Random(3301).sample()` over the
245 non-conflict indices, read at maximum zoom without the canonical value in view, scored
against `canon_256.bin` (`calibrate.py` → `calibration.json`):

| measure | result |
|---|---|
| overall exact-token agreement | **40 / 40 = 100.0 %** |
| case-ambiguous-glyph subset (`0 1 I K L O S W i k l o s w`) | **22 / 22 = 100.0 %** |
| pre-registered gate | ≥ 38/40 → **PASS** |

The sample naturally contained 22 case-ambiguous cells, so the PREREG A.3 top-up rule never
fired. Reported separately per PREREG A.3, because overall accuracy on unambiguous glyphs
would flatter the instrument.

**Honest caveat.** The blindness of those 40 reads rests on the first agent's own procedure
note in `calibrate.py`, which this run cannot verify from the outside. That is exactly why a
second, machine-checkable control was built.

### 1.3 The second instrument and its controls (`pixelmatch.py`, new in this run)

The pp49–51 images are 400-DPI Ghostscript renders of typeset text. If that is true, two
occurrences of the same character should be *pixel-identical*, not merely similar — a testable
claim that turns glyph reading from scoring into lookup. `pixelmatch.py` compares **native,
un-rescaled** glyph bitmaps by best-alignment IoU over integer shifts in [−3, 3]².

**Control 1 — render determinism.** Over the 54 symbol classes with ≥ 2 uncontested exemplars:

| measure | result |
|---|---|
| mean within-class pairwise IoU | **0.9948** |
| worst within-class pair, excluding one mis-segmented `t` | **0.995** |
| worst overall (idx 209, a `t` that segmented wrongly) | 0.117 |
| highest **between**-class IoU among the deciding classes | `l`/`I` = 0.908, `O`/`Q` = 0.865, `L`/`I` = 0.719 |

The render is deterministic. Same-class glyphs sit at ≥ 0.995; the closest *different*-class
pair sits at 0.908. That gap is what licenses using the classes `I`, `i` and `l`, each of
which has exactly **one** uncontested exemplar in the payload (cells 90, 72 and 2 respectively
— all three are cells where all three witnesses agree, so they are 3-way anchors, not
single-lineage ones).

**Control 2 — leave-one-out nearest-exemplar accuracy** over the uncontested cells:

| glyph position | accuracy | case-ambiguous subset |
|---|---|---|
| trailing symbol | **236 / 237 = 99.58 %** | **74 / 74 = 100 %** |
| leading digit | **242 / 242 = 100 %** | **108 / 108 = 100 %** |

The single symbol miss is idx 209, the mis-segmented `t` from Control 1 — an extraction
failure, not a discrimination failure. Five cells are **not testable** by leave-one-out
(classes `I`, `R`, `h`, `i`, `l` have one exemplar each, so removing it removes the class);
that limitation is carried into §6.

## 2. A-04 — the contested bytes

### 2.1 Three independent visual passes

Per PREREG A.4, three passes with different crop padding, different upscale factor and a
differently-ordered presentation (`visualpass.py`):

- **Pass A** — scale 10, pad 16, ascending index
- **Pass B** — scale 7, pad 4, descending index
- **Pass C** — scale 14, pad 24, ordered by `i mod 7`

All six pre-registered cells returned the **same token on all three passes**, and every
visual read matches the pixel instrument's independent verdict.

### 2.2 The six pre-registered cells — RESOLVED

| idx | page r,c | relikd tok | scream tok | scream decimal | 3-pass visual | pixel best IoU | runner-up | **resolved** | byte | confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 25  | p49 r3,c1  | `3I`=198 | `3I`=198 | 224 (`3i`) | `3I` ×3 | `I` **1.0000** | `l` 0.908 | **`3I`** | **198** | RESOLVED |
| 175 | p50 r11,c7 | `0I`=18  | `0I`=18  | 44 (`0i`)  | `0I` ×3 | `I` **1.0000** | `l` 0.908 | **`0I`** | **18**  | RESOLVED |
| 182 | p50 r12,c6 | `2l`=167 | `2l`=167 | 141 (`2L`) | `2l` ×3 | `l` **1.0000** | `I` 0.908 | **`2l`** | **167** | RESOLVED |
| 199 | p51 r1,c7  | `0l`=47  | `0l`=47  | 21 (`0L`)  | `0l` ×3 | `l` **1.0000** | `I` 0.908 | **`0l`** | **47**  | RESOLVED |
| 215 | p51 r3,c7  | `1O`=84  | `1O`=84  | 5 (`05`)   | `1O` ×3 | `O` **0.9993**, digit `1` 1.0000 (margin 0.837) | `Q` 0.867 | **`1O`** | **84**  | RESOLVED |
| 237 | p51 r6,c5  | `0W`=32  | `0W`=32  | 58 (`0w`)  | `0W` ×3 | `W` **1.0000** | `V` 0.479 | **`0W`** | **32**  | RESOLVED |

**All six agree with the majority-vote canon already on disk. None of the six bytes changes.**
Every one of the six also refutes the scream314 decimal column, which is the only witness that
dissented on them.

The discriminations, stated physically rather than as scores:

- **`I` vs `l`** (cells 25, 175, 182, 199) is a 7-pixel height difference at 400 DPI: the `I`
  bar measures **8 × 67 px** with its top level with the digit's cap line (`dy_top` = −1), the
  `l` bar measures **8 × 74 px** and rises **6 px above** cap height. Both are visible directly
  at max zoom against the cell's own digit, which is why the visual and pixel passes agree.
- **`l` vs `L`** is not close at all: `L` carries a horizontal foot (`wrel` 0.382 vs 0.118).
  No candidate cell has a foot stroke.
- **`i` vs `I`**: `i` is a shorter body with a *separate dot*. No candidate cell has a dot.
- **`W` vs `w`**: `W` is cap-height (`hrel` 1.07, `toprel` +0.03); `w` is x-height
  (`hrel` 0.67, `toprel` −0.35). Cell 237 measures 1.058 / +0.029 — cap `W`, not close.

### 2.3 idx 215, the one contested in *both* positions — extra scrutiny

215 is the only cell whose two witnesses differ in both glyphs (`1O` = 84 vs `05` = 5), so its
leading digit was adjudicated too rather than assumed, and a labelled side-by-side strip was
rendered against every competing class (`compare215.py` → `crops/compare215.png`):

- the leading glyph is the **`1`** with the angled flag — the digit `0` in this face is a
  **narrow oval**, visibly unlike it (`1` IoU 1.000 vs `0` IoU 0.126, margin **0.837**);
- the trailing glyph is a **wide circle with no tail**. `Q` in this face carries a clear
  diagonal tail crossing the bowl (visible in cells 52 and 130); `0` is the narrow oval;
  `5` has a flat top bar and a bowl. IoU: `O` 0.9993, `Q` 0.867, `G` 0.715, `C` 0.681.

`1O` = **84**. The decimal witness's `05` is wrong in *both* glyph positions.

### 2.4 Coverage extension — the other 5 conflict cells, and 3 byte corrections

`canonicalize.py` finds **11** disagreeing cells, not 6. The other five are *token-split*
cells, where relikd and scream314 disagree and `canonicalize.py` broke the tie **with the same
decimal column** that has now gone 0-for-6 on the pre-registered cells. Leaving that authority
unexamined would have been arbitrary, so the validated instrument was turned on all 11
(`adjudicate_all.py`). Three of the five come back **different from `canon_256.bin`**:

| idx | relikd | scream | decimal | image verdict | pixel IoU | 3-pass visual | canon byte | **corrected byte** |
|---|---|---|---|---|---|---|---|---|
| 45  | `1L`=81  | `1l`=107 | 81  | **`1l`** | 1.0000 | `1l` ×3 | 81  | **107** |
| 50  | `0L`=21  | `0l`=47  | 21  | **`0l`** | 1.0000 | `0l` ×3 | 21  | **47**  |
| 165 | `0l`=47  | `0I`=18  | 18  | `0I`     | 1.0000 | (pixel only) | 18 | 18 (unchanged) |
| 172 | `2s`=174 | `2S`=148 | 148 | `2S`     | 1.0000 | (pixel only) | 148 | 148 (unchanged) |
| 246 | `3i`=224 | `3I`=198 | 224 | **`3I`** | 1.0000 | `3I` ×3 | 224 | **198** |

The three changed cells were given the *same* three-pass visual treatment as the
pre-registered six, because a byte change earns at least that much rigour. In each case the
discrimination is a presence/absence of a stroke rather than a judgement call: cells 45 and 50
have **no foot**, so they are `l` and not `L`; cell 246 has **no dot**, so it is `I` and
not `i`.

### 2.5 What this says about the three witnesses

Scored over all 11 conflict cells against the image:

| witness | correct |
|---|---|
| **scream314 token table** | **11 / 11** |
| relikd token table | 6 / 11 |
| scream314 decimal column | 2 / 11 (and only where it happened to agree with scream's token) |

The decimal column is a *derived* column, and it is the least reliable of the three. It should
not have been used as the tie-breaker; `canonicalize.py`'s `maj` rule inherits its errors on
exactly the cells where the tokens split. This is a reusable finding for anyone else
transcribing these pages.

## 3. The resolved payload

Artifacts: `payload_resolved.json` (per-byte record, confidence, three-pass concordance and
the calibrated accuracy that licenses it), `payload_resolved.bin`, `adjudication.json`.

| | |
|---|---|
| SHA-256, resolved payload | `3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290` |
| SHA-256, `canon_256.bin` (majority vote) | `4c8dc85531d256793a6d0d318b8845869b4983e672077b094ed955bde92226d5` |
| bytes changed vs `canon_256.bin` | **3** — indices 45, 50, 246 |
| bytes changed vs `canon_256_decpref.bin` | 9 |
| pre-registered contested bytes changed | **0** — all six confirm the majority vote |
| candidate variants remaining | **1** (the Cartesian product PREREG A.5 budgeted for is empty; no cell stayed contested) |

`canon_256.bin` is **not** replaced by this lane — the coordinator decides that. The corrected
stream lives in `payload_resolved.bin` and every propagation below is run on **both**.

## 4. Propagation (PREREG A.5)

No cell stayed contested, so the Cartesian product PREREG A.5 budgeted for (≤ 2^6 = 64
variants) collapses to **one** resolved payload. Every test below was run on all three
streams — `canon_majority`, `canon_decimal_preferred` and `L5_resolved` — so the effect of
the 3-byte correction is visible rather than assumed. Artifacts: `propagate.py`,
`propagation_results.json`.

### 4.1 Structural characterization

| stream | entropy b/B | distinct bytes | ASCII-printable | BE integer prime? | smallest factor |
|---|---|---|---|---|---|
| canon_majority | 7.1697 | 161 | 102 | no | 2 |
| canon_decimal_preferred | 7.1648 | 161 | 101 | no | 2 |
| **L5_resolved** | **7.1697** | **161** | **103** | no | 2 |

The correction does not change the object's character: still high-entropy, still even (so not
a prime and not an RSA modulus), still ~40 % printable — consistent with a 2048-bit
random-looking blob rather than a structured record.

### 4.2 Hash / checksum probes — the page-56 "AN END" target

210 hashes: 3 payload streams × 7 representations (raw, reversed, hex string lower/upper,
`+\n`, hex `+\n`, bit-reversed) × 10 algorithms (SHA-256/384/512, SHA3-256/512, BLAKE2b/2s,
SHAKE-256, MD5, SHA-1), compared against the 512-bit page-56 target `36367763…132c2a8b4`.
**Zero hits.** This is an exact test — its false-positive rate is 2^-512 per trial — so the
null is analytic rather than scored.

### 4.3 round16 zeroFP E-02 / H-03, re-run on the resolved payload

Run with round16's own instrument (`zerofp_tests.py`), imported and pointed at
`payload_resolved.bin` by redirecting its `load_bytes`. The test code is byte-for-byte the
round16 code, so a hit here would have been a hit there.

| test | verdict on the resolved payload |
|---|---|
| E-02A — any 56-byte window a permutation of 0..55 | **NULL** (exact test, ~1e-24 FP/window) |
| E-02B — payload as gap values vs the real doublet gaps | **NULL** |
| H-03 — 2013 onion cookies XOR'd against the payload | **NULL** |

Per PREREG Part C this is a coverage extension of A-04's propagation, not a new E-02 sweep.

### 4.4 B-05 — payload as PRF seed (the genuinely new coverage)

B-05 (LEDGER, Round 13) expanded the payload into a runic keystream and returned NEGATIVE
over 70,680 beam decodes. Its `reopens_if` names exactly the case this lane creates:

> "JOINT corruption of two or more contested bytes (only single-position sweeps and the 64
> all-combination masks were run)"

The resolved payload differs from `canon_256.bin` at **three positions jointly** — and,
crucially, at indices **45, 50 and 246, which are not among B-05's six contested indices at
all**. B-05 varied only {25, 175, 182, 199, 215, 237}; no part of it ever touched 45/50/246.
So the resolved stream is a seed B-05 provably never evaluated. Given B-05's own measured
avalanche control — one byte flip moves a keystream decode from −4.170 (perfect) to −7.38
(noise) — that is not a negligible difference.

`propagate_b05.py` re-runs B-05's **pinned Part-1 grid** on the resolved payload's six
representations: 6 reps × 15 generators × {mod, reject} × {fwd, rev} × {atbash, plain} ×
{+1, −1} × 14 offsets = **20,160 skip-aware beam decodes**, at the same HEAD = 400,
beam_w = 120, max_skip = 3 as Round 13 so the numbers are directly comparable.

Bar, per Rule 4 and PREREG A.5: `benchmark/null.py: threshold_for(20160, 400)` returns
**−5.5** — the historical floor still binds at this N, the scale-corrected family-wise term
being −6.20, below it — and the operative bar is `max(−5.5, null_max)` exactly as in B-05.

_Status: RUNNING. `threshold_for(20160, 400)` returned **-5.5** as predicted, and the
size-matched shuffle null (n = 200) is recomputed in-run, so the operative bar is
`max(-5.5, null_max)`. Progress and the running best are checkpointed to
`b05_propagation.json` after every (representation, generator) block, so an infrastructure
stall costs at most one block. At the ~1,600-decode mark the best score is **-6.909**, i.e.
1.4 below the bar and inside the noise band where Round 13's whole sweep sat. Until the run
lands, the A-04 ledger entry carries it in `not_covered`._

## 5. E-01 — the payload as an RSA signature/ciphertext

**Verdict: NULL, with passing controls.** Artifacts: `extract_moduli.py`, `moduli.json`,
`e01_extended.py`, `e01_results.json`.

### 5.1 The named coverage gap is closed

Round 16 recorded E-01 as coverage-limited for one stated reason: *"the 7A35090F RSA-4096
moduli (the correct size) were not on disk and not fetched."* They were on disk all along —
in `corpus/`, under ten independent witnesses including **two keyserver pulls**
(`keys.openpgp.org`, `keyserver.ubuntu.com`), so no network fetch was required.

`extract_moduli.py` parses the OpenPGP packets directly and computes the RFC 4880 §12.2 v4
fingerprint from the packet bytes, so identification does not rest on a filename:

| role | fingerprint | key id | bits | e | independently confirmed by |
|---|---|---|---|---|---|
| primary | `6D854CD7933322A601C3286D181F01E57A35090F` | `181F01E57A35090F` | 4096 | 65537 | `gpg --with-colons --import-options show-only` |
| subkey | `DEC57731ACCBFD11EEBA13434D390ECF671DDEB1` | `4D390ECF671DDEB1` | 4096 | 65537 | same |
| 2013 puzzle | (not a PGP key) | — | 432 | 65537 | `armada20/pgp_welcome.txt` |

Both PGP keys carry uid `Cicada 3301 (845145127)` and creation time 1325734783 = 2012-01-05.
This is the canonical 3301 key.

**Provenance nit worth recording:**
`corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc`
is **misnamed** — its filename asserts a fingerprint that is not the key's. The file contains
the canonical key (`6D854CD7…7A35090F`); the two strings share only the 32-bit short id
`7A35090F`. Anyone verifying by filename would draw the wrong conclusion.

A sweep of every `BEGIN PGP PUBLIC KEY BLOCK` in `corpus/` and the round10 L6 archive found
no other 3301 RSA key: the remaining hits are a GitHub-Action test key (`DAFAFE35…`, uid
says "Not real"), a revoked 2016 impostor key whose *uid string* is "7A35090F"
(`CEBB2647…`), and a community member's brainpool ECC key. None is a usable modulus.

### 5.2 Instrument and the mandatory controls (PREREG B.4)

`e01_extended.py` **extends** round16's instrument rather than replacing it: it imports
`zerofp_tests.pkcs1_v15_check` and `zerofp_tests.check_digest_info` and uses them unchanged,
so any hit here would be a hit there. Added: the 4096-bit moduli, little-endian and
block-alignment encodings, an EMSA-PSS structural matcher, the three payload variants, and
the controls.

Controls, on a locally generated RSA-2048 key with genuine signatures from `cryptography`:

| matcher | positive control (genuine signature) | negative control (10,000 random blocks) |
|---|---|---|
| PKCS#1 v1.5 signature | **FIRES, strict** — 202 FF bytes then a real SHA-256 DigestInfo | strict **0**, loose **0** |
| EMSA-PSS | **FIRES, strict** — 190 zero bytes then `0x01`, saltlen 32 | strict **0**, loose **1** |
| PKCS#1 v1.5 type 2 (encryption) | **FIRES** (loose tier; type-2 blocks carry no DigestInfo) | loose **0** |

**CONTROL VERDICT: PASS.** The one loose PSS false positive in 10,000 random blocks
(measured rate 1e-4) is exactly why the strict tier exists: strict additionally requires ≥ 8
zero bytes before the `0x01` delimiter, and fired **zero** times on noise. Only strict
matches count as a hit.

### 5.3 Coverage of the sweep

| dimension | covered |
|---|---|
| moduli | 3 — 7A35090F primary (4096), 7A35090F subkey (4096), 2013 puzzle (432) |
| payload variants | 3 — `canon_majority`, `canon_decimal_preferred`, `L5_resolved` |
| encodings | big-endian, little-endian (byte-reversed), and for the 4096-bit moduli both left-aligned (zero-padded low) and right-aligned block placements |
| exponents | 65537, 3, 17 |
| matchers | PKCS#1 v1.5 signature (+ DigestInfo for MD5, SHA-1/224/256/384/512), PKCS#1 v1.5 type 2, EMSA-PSS under MGF1-SHA-1/256/384/512 |
| **tuples evaluated** | **162** |
| encodings skipped | 12, each because `s ≥ n` so the payload is not a valid RSA element there: the 2048-bit payload exceeds the 432-bit 2013 modulus (6), and big-endian-left-aligned overflows both 4096-bit moduli because the payload's leading byte `0xcb` exceeds their leading bytes `0xc1` / `0xbc` (6) |

**Result: no structural match on any tuple.** The controls fire on genuine signatures and are
silent on noise, so this is a trustworthy null rather than an uncalibrated silence.

One correction to the Round 16 record while closing its gap: `zerofp_tests.py` notes that
under a 4096-bit modulus `pow(s,e,n)` "would trivially return s^e as-is (s << n), so PKCS1
padding is impossible." That holds only for `e = 1`. For `e` ∈ {3, 17, 65537} a 2048-bit `s`
raised to `e` is far wider than 4096 bits, so the reduction mod `n` is a full one and the
test is meaningful. The gap was real; the reason recorded for it was not.

## 6. Coverage / not covered / reopens-if

### What this lane measured

- **A-04**: all **11** disagreeing cells of the pp49–51 payload adjudicated against the
  400-DPI page images by two independent instruments (three-pass max-zoom visual reading;
  native-resolution nearest-exemplar bitmap matching), on a render whose determinism was
  measured (within-class IoU 0.9948) and whose reading accuracy was measured (visual 40/40;
  bitmap leave-one-out 236/237 symbols, 242/242 digits, 74/74 on case-ambiguous classes).
- **E-01**: 162 (modulus, exponent, encoding, payload) tuples across every published 3301 RSA
  modulus, with positive and negative controls both measured and reported.
- **Propagation**: structural characterization, 210 hash probes against the page-56 target,
  and round16's E-02A / E-02B / H-03 re-run on the corrected payload.

### What is NOT covered

1. **Three cells never segmented.** Indices **186, 210, 211** do not split into exactly two
   glyphs under the column-gap rule, so the bitmap instrument has no reading for them. All
   three are cells where all three witnesses already agree, so nothing is contested there —
   but they are outside this instrument's demonstrated reach and are stated as such.
2. **Five glyph classes are single-exemplar** (`I`, `R`, `h`, `i`, `l`) and so cannot be
   leave-one-out validated. Their use rests on the measured render determinism, not on a
   cross-validated accuracy. `I` and `l` are load-bearing for six of the eleven cells.
3. **The 40-cell visual calibration's blindness is not externally verifiable** — it rests on
   the first agent's procedure note in `calibrate.py`. The bitmap instrument's controls are
   machine-checkable and are what the conclusions should be leant on.
4. **E-01 covers only *published* moduli.** If the payload is an RSA block under an
   unpublished modulus — e.g. one of the 2013 puzzle's implicit 2048-bit keys, whose public
   moduli were never released — no version of this test can see it.
5. **E-01 covers only PKCS#1 v1.5 and PSS.** Raw/textbook RSA, OAEP, ISO 9796-2, and
   non-RSA public-key structures are untested.
6. **B-05 propagation is the pinned Part-1 grid only.** B-05's Part 1b (constant-shift),
   Parts 2a/2b (contested-byte masks) and the rigid control channel are not re-run on the
   resolved payload.
7. **All decode-based coverage inherits Round 18 L7's two conditionals**: it is an
   English-only negative, and it covers one rejection-loop transition model.

### Reopen conditions

- **A-04 reopens if** a higher-resolution or lossless source for pp49–51 appears (these are
  400-DPI JPEGs; a PNG or PDF-native render would let the singleton-class limitation be
  cross-validated); or if a *third independent transcription lineage* disagrees with
  `payload_resolved.bin` at any of the 11 cells; or if any witness ever contests cells
  186/210/211, for which this instrument has no reading.
- **E-01 reopens if** a further 3301 RSA modulus is published or recovered — in particular a
  2048-bit one, the only size for which the payload is a *natural* full-width block — or if
  the payload is to be tested under OAEP / ISO 9796-2 / raw-RSA structure.
- **The B-05 lane reopens if** the resolved-payload grid produces a score above
  `max(−5.5, null_max)`; see `b05_propagation.json`.
- **A cheap unrun follow-on this lane exposes:** the scream314 *token* table scores 11/11
  against the pixels and the relikd table 6/11. Every other transcription in this repo
  sourced from relikd inherits an error rate this lane has now measured. Re-adjudicating the
  other relikd-sourced pages with `pixelmatch.py` is a small job with a validated instrument
  already behind it.

### Doctrine note

`ARMADA-DOCTRINE.md` (binding from Round 19) records that every genuinely new finding in this
project came from auditing a closure, an instrument, an artifact or an input, and none from a
new key-space sweep. This lane is another data point: the byte corrections at 45/50/246 came
from auditing an **input** — a transcription witness that had never been checked against the
pixels — and they were only findable because the instrument was validated first.

---

## ADDENDUM — 2026-08-26, Round 19 lane C1

_Appended, not overwritten. This file was already complete when C1 ran; C1 is the Round 19
closeout lane for the same two items and re-derived everything here independently. Full
write-up: [`../../round19/C1/RESULTS.md`](../../round19/C1/RESULTS.md)._

**Everything above reproduced.** C1 re-derived §§1–3 from the on-disk artifacts rather than
trusting the transcript: input integrity 5/5, grid 80/104/72 with `grid.json` **byte-identical**,
the leave-one-out and render-determinism controls to the digit, the 11-cell adjudication to the
same `sha256 3b9b07d9…b290`, and the witness table (scream tokens 11/11, relikd 6/11, decimal
2/11). No number above was contradicted.

**C1 added the control this file was missing.** Leave-one-out cannot test the five singleton
classes (`I`, `R`, `h`, `i`, `l`), and `I`/`i`/`l` decide 8 of the 11 cells — including 4 of
the 6 pre-registered. C1 measured that regime directly:

- **single-template accuracy** (every class reduced to one exemplar): symbol **182/183 = 99.45 %**,
  case-ambiguous subset **59/59 = 100 %**; digit **237/237 = 100 %**.
- **global separation**, all 29,161 uncontested pairs: `max_between` **0.9085** (`l`/`I`) <
  0.995 ≤ `min_within` **0.9954**. The "IoU ≥ 0.995 ⇒ same class" rule has zero counterexamples.
- **label-swap closed by typography**: cell 2 (`l`) sits in the lowercase-ascender cluster
  (`b` +0.096, `d` +0.087, `k` +0.094, `h` +0.088) and cell 90 (`I`) in the capital cluster
  (`P`/`Y`/`H`/`X`/`Z` −0.015, `E` −0.021), so the two singletons' labels are correct
  independently of any transcription.

**§5's E-01 was correct but mis-specified.** R1 found — and C3's signature table confirms —
that 3301 declared their scheme in **signed** text: `Scheme: Crypt::RSA::ES::OAEP`,
`Version: 1.99`, in two messages that both PASS under `181F01E57A35090F` (2012-01-15 and
2014-01-06). That is not PKCS#1 v1.5 or PSS. C1 recovered the 2013 key's prime factors from
two corpus decrypt scripts (`p·q` equals the published 432-bit modulus **exactly**), decrypted
3301's own ciphertext, and **measured** the wire layout: `emLen = k − 1`,
`EM = maskedSeed(20) ‖ maskedDB`, MGF1-SHA-1, `DB[0:20] = SHA-1("")`. The matcher built on that
160-bit predicate fires **3/3 on 3301's own blocks** with **0/10,000** false positives, and
returns **NULL** on the payload. §5's verdict stands and is now specified against the right shape.

**§4.4's B-05 re-run.** C1 ran the same 20,160-decode grid, then re-ran it under Round 19's
repaired instrument, because the first pass stored only (parameters, English score, head) —
doctrine **R3** requires the language-agnostic statistics at sweep time — and judged against
**−5.5**, which I3 has since measured to be the wrong bar in **14 of 14** historical sweeps.
The corrected pass persists a full `SWEEPROW/1` per decode and takes its bars from I3's
calibrated contract. Verdict unchanged; the conditionals are now stateable.

**Standing correction to this file's framing:** the negative in §4.4 does **not** cover
`skip_by_two` — that decoder's transition relation is exact for `encipher_keyskip` and nothing
else (L7-B). Any future re-scoring of this payload belongs to Round 19 lane **S2**, seeded from
`payload_resolved.bin` rather than `canon_256.bin`.
