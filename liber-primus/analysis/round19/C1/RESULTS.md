# Round 19 · Lane C1 — CLOSEOUT of Round 18 L5 (PAYLOAD) · RESULTS

_Written 2026-08-26. Pre-registration: [`PREREG.md`](PREREG.md) (+ Addendum 1, dated, added
after R1/C3 reported and **before** the Crypt::RSA sub-test ran). Binding:
[`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

Scope: **A-04** (the 6 contested pp49–51 bytes) and **E-01** (the payload as an RSA
signature/ciphertext), plus the propagation of whatever A-04 changes.

**Trust anchor.** Before: `python3 liber-primus/tests/validate.py` → *ALL VALIDATIONS PASSED*
(5/5); `python3 -m pytest liber-primus/benchmark/ -q` → **8 passed**. After: identical, re-run
and recorded in §7.

---

## 0. What already existed, and what this lane did

The campaign plan describes `round18/L5-payload/RESULTS.md` as a TBD skeleton. **It is not**,
and this lane verified that first — and found it further along than even R1's audit reported.
R1 saw **206 lines with A-04 complete**; by the time C1 read it, it was **409 lines with
A-04 *and* E-01 complete** and only the propagation section still moving. Round 18's L5 continuation processes were still running in
this worktree after Round 19 was planned, and a concurrent agent was completing that file
during C1's own wall-clock window (its `RESULTS.md` grew from 11 KB to 24 KB and its
`ledger.json` appeared at 12:10 while C1 was running). Per the coordinator's instruction and
the precedent set by C2 and C3, **C1 did not overwrite it**; §8 records the dated addendum
appended to it instead.

| | already on disk (Round 18 L5) | what C1 did |
|---|---|---|
| grid / crop / calibration pipeline | `grid.py`, `calibrate.py`, `glyphmatch.py`, `pixelmatch.py`, `montage.py`, `crops/` | **re-derived every claim** from the artifacts; `grid.json` reproduces byte-identically |
| A-04 adjudication | `adjudication.json`, `payload_resolved.bin/.json` — 6 cells + 5 more | re-ran `adjudicate_all.py`; byte-identical result (`sha256 3b9b07d9…b290`) |
| A-04 positive control | render-determinism + leave-one-out, **but both blind to the classes that decide the answer** | **supplied the missing control** — §1.3, §1.4, §1.5 |
| E-01 moduli | `moduli.json` (2 × RSA-4096 + the 432-bit 2013 modulus) | re-derived byte-identically; **broadened the scan** to all 3,716 key-shaped files |
| E-01 test | a concurrent L5 run produced a PKCS#1/PSS null | **independently replicated** it (§3.3), and then found the test was **mis-specified** (§3.4) |
| **Crypt::RSA `ES::OAEP`** | *nothing — not tested by anyone* | **measured the real wire layout from 3301's own ciphertext and tested it** (§3.4–3.5) |
| propagation | a concurrent L5 run started `propagate_b05.py` | ran it, then **re-ran it properly** under I2/I3 because the first pass was R3-non-compliant and used the −5.5 bar I3 invalidated (§4.2) |

The honest summary of prior state: **A-04 was finished as an adjudication but not as an
experiment** (doctrine mechanic 2 — the control did not cover the deciding classes), and
**E-01 was finished against the wrong shape**.

---

## 1. A-04 — the instrument and its measured control accuracy

### 1.1 Input integrity (L5 PREREG A.2.1 — a hard stop)

`p49.jpg`, `p50.jpg`, `p51.jpg`, `canon_256.bin`, `canon_256_decpref.bin` — **5/5 SHA-256
match** `handoff/capsule/MANIFEST.json`. Pixels were read only after this passed.

### 1.2 Grid (L5 PREREG A.2.2)

Projection profiling yields exactly **80 / 104 / 72 = 256** cells. `grid.json` re-derived in
this lane is **byte-identical** to L5's. 253/256 cells segment into exactly two glyphs;
**186, 210, 211** do not (§6).

### 1.3 The control L5 had — and why it does not reach the answer

`pixelmatch.py`'s two controls re-derived exactly:

| control | measured |
|---|---|
| render determinism, 54 classes with n ≥ 2 | mean within-class native-bitmap IoU **0.9948** |
| leave-one-out, trailing symbol | **236 / 237 = 99.58 %**; case-ambiguous subset **74/74 = 100 %** |
| leave-one-out, leading digit | **242 / 242 = 100 %**; case-ambiguous subset **108/108 = 100 %** |

**The gap.** Five classes have exactly **one** uncontested exemplar — `I` (cell 90), `R` (23),
`h` (126), `i` (72), `l` (2) — so leave-one-out cannot test them: removing the exemplar
removes the class. And `I`, `i`, `l` are precisely what decide **8 of the 11** conflict cells,
including **4 of the 6 pre-registered ones**. L5's licence for those cells was an
extrapolation from classes with 2–7 exemplars. Under doctrine mechanic 2 that adjudication
certifies nothing until the extrapolation is measured.

### 1.4 Control 3 — the single-template regime (NEW, pre-registered in PREREG §2.1)

Reduce **every** class to exactly one exemplar — reproducing the exact regime `I`/`i`/`l` are
used in — then classify every remaining uncontested cell:

| | accuracy | case-ambiguous subset |
|---|---|---|
| trailing symbol | **182 / 183 = 99.45 %** | **59 / 59 = 100 %** |
| leading digit | **237 / 237 = 100 %** | **106 / 106 = 100 %** |

Pre-registered gate ≥ 99 % overall **and** 100 % case-ambiguous → **PASS**. The single miss is
idx 209, the objectively mis-segmented `t` — an extraction failure, not a discrimination
failure, and it is an uncontested cell.

**This is the measured positive-control accuracy behind the six bytes: 100 % (59/59) on
case-ambiguous glyphs in the one-template-per-class regime the six are decided in, and
99.45 % overall.**

### 1.5 Control 4 — global separation (NEW, pre-registered in PREREG §2.2)

All-pairs best-alignment IoU over the 242 uncontested segmented cells — **29,161 pairs**:

| | min within-class | max between-class |
|---|---|---|
| all pairs | 0.1166 (idx 32/209, `t` — mis-segmented) | 0.9085 (idx 2/90, `l`/`I`) |
| excluding the one mis-segmented cell | **0.9954** (idx 84/239, `r`) | **0.9085** |

`max_between (0.9085) < 0.995 ≤ min_within (0.9954)`, so the decision rule *"best IoU ≥ 0.995
⇒ same class"* has **zero counterexamples in 29,161 measured pairs** and is **LICENSED**.
Every contested cell's winning IoU is **0.9993–1.0000**; every runner-up is **≤ 0.908**.

### 1.6 The label-swap risk, closed by typography (NEW in C1)

Controls 3 and 4 still leave one hole: the two singleton exemplars are `l` (cell 2) and `I`
(cell 90) and their labels come from `canon_256.bin`. If those two labels were *swapped*,
every `I`/`l` verdict would invert. This is closed **without reference to any transcription**,
by measuring each glyph against its own cell's digit cap line:

| cluster | `toprel` (+ = rises above cap height) |
|---|---|
| lowercase ascenders | `b` +0.096 (n=2), `d` +0.087 (n=3), `k` +0.094 (n=5), `h` +0.088, **`l` +0.088** |
| capitals | `P` −0.015 (n=3), `Y` −0.015 (n=2), `H` −0.015 (n=3), `X` −0.015 (n=4), `Z` −0.015 (n=3), `E` −0.021 (n=6), **`I` −0.015** |

Cell 2 sits inside the ascender cluster; cell 90 sits inside the cap cluster. Ascenders
overshoot cap height by ~6 px at 400 DPI and capitals do not — a fact about the typeface,
anchored by **four multi-exemplar classes on each side**. The labels are correct.

### 1.7 Second-reader visual check

All 11 conflict cells re-rendered beside their candidate exemplars (`visualcheck.py` →
`crops/c1_cell*.png`) and read by a second reader **in this run**; all 11 agree with the pixel
verdict. This is **non-blind** (the pixel verdict was known) and is claimed only as
corroboration. L5's three "blind" visual passes are a hard-coded table in `adjudicate_all.py`
that this lane cannot verify from outside; they carry **no weight** in this result.

---

## 2. A-04 — the six bytes, and three that nobody was looking at

### 2.1 The six pre-registered cells — all RESOLVED, none changes

| idx | page r,c | relikd | scream tok | scream decimal | pixel best IoU | runner-up | **resolved** | byte |
|---|---|---|---|---|---|---|---|---|
| 25 | p49 r3,c1 | `3I`=198 | `3I`=198 | 224 (`3i`) | `I` **1.0000** | `l` 0.908 | **`3I`** | **198** |
| 175 | p50 r11,c7 | `0I`=18 | `0I`=18 | 44 (`0i`) | `I` **1.0000** | `l` 0.908 | **`0I`** | **18** |
| 182 | p50 r12,c6 | `2l`=167 | `2l`=167 | 141 (`2L`) | `l` **1.0000** | `I` 0.908 | **`2l`** | **167** |
| 199 | p51 r1,c7 | `0l`=47 | `0l`=47 | 21 (`0L`) | `l` **1.0000** | `I` 0.908 | **`0l`** | **47** |
| 215 | p51 r3,c7 | `1O`=84 | `1O`=84 | 5 (`05`) | `O` **0.9993**, digit `1` 1.0000 | `Q` 0.867 | **`1O`** | **84** |
| 237 | p51 r6,c5 | `0W`=32 | `0W`=32 | 58 (`0w`) | `W` **1.0000** | `V` 0.479 | **`0W`** | **32** |

**All six confirm the majority vote already in `canon_256.bin`. No pre-registered byte
changes.** All six refute scream314's decimal column — the only witness that dissented.

The discriminations are physical, not judgemental: `I` is an **8 × 67 px** bar with its top
level with the digit cap line (`dy_top` −1); `l` is **8 × 74 px** and rises **6 px above** it;
`L` carries a foot (`wrel` 0.382 vs `l` 0.118); `i` carries a separate dot (`wrel` 0.162,
`hrel` 0.926); `W` is cap-height (`hrel` 1.071 / `toprel` +0.034) where `w` is x-height
(0.672 / −0.347) — cell 237 measures 1.058 / +0.029.

### 2.2 The coverage extension — 3 bytes DO change

`canonicalize.py` finds **11** disagreeing cells, not 6. The other five are *token-split*
cells that it tie-broke with **the same decimal column** that has now gone 0-for-6. Leaving
that authority unexamined would have been arbitrary, so the validated instrument was turned on
all 11:

| idx | relikd | scream | decimal | image verdict | IoU | canon byte | **corrected** |
|---|---|---|---|---|---|---|---|
| 45 | `1L`=81 | `1l`=107 | 81 | **`1l`** | 1.0000 | 81 | **107** |
| 50 | `0L`=21 | `0l`=47 | 21 | **`0l`** | 1.0000 | 21 | **47** |
| 165 | `0l`=47 | `0I`=18 | 18 | `0I` | 1.0000 | 18 | 18 (unchanged) |
| 172 | `2s`=174 | `2S`=148 | 148 | `2S` | 1.0000 | 148 | 148 (unchanged) |
| 246 | `3i`=224 | `3I`=198 | 224 | **`3I`** | 1.0000 | 224 | **198** |

Cells 45 and 50 have **no foot** ⇒ `l` not `L`; cell 246 has **no dot** ⇒ `I` not `i`.

### 2.3 Witness accuracy — a reusable finding

Scored over all 11 conflict cells against the image:

| witness | correct |
|---|---|
| **scream314 token table** | **11 / 11** |
| relikd token table | 6 / 11 |
| scream314 **decimal** column | **2 / 11** |

The decimal column is a *derived* column and is the least reliable of the three.
`canonicalize.py` used it as its tie-breaker and inherits its errors on exactly the cells
where the tokens split. Anyone transcribing pp49–51 should prefer scream314's **token** table.

### 2.4 The resolved payload

| | |
|---|---|
| SHA-256, resolved | `3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290` |
| SHA-256, `canon_256.bin` | `4c8dc85531d256793a6d0d318b8845869b4983e672077b094ed955bde92226d5` |
| bytes changed vs `canon_256.bin` | **3** — indices **45, 50, 246** |
| bytes changed vs `canon_256_decpref.bin` | 9 |
| pre-registered contested bytes changed | **0** |
| candidate variants remaining | **1** — the ≤ 2⁶ Cartesian product L5 PREREG A.5 budgeted for is **empty** |

`canon_256.bin` is **not** overwritten by this lane. The corrected stream is
`payload_resolved.bin`; the coordinator decides whether it becomes canonical.

---

## 3. E-01 — the payload as an RSA signature/ciphertext

### 3.1 What Round 16 actually left behind

`LEDGER.json` marks E-01 `partially-run`. Re-running `round16/zeroFP/zerofp_tests.py` shows
what that amounted to: **1 modulus, 8 `pow()` checks, all 8 SKIPPED for `s ≥ n`** — Round 16
evaluated **zero** modular exponentiations for E-01.

Its stated reason for not fetching the 4096-bit moduli is in its own source:

> *"under a 4096-bit modulus, `pow(s,e,n)` would trivially return s^e as-is (s ≪ n), so PKCS1
> padding is impossible."*

**That is arithmetically false for every e > 1.** `s` is 2048-bit, so `s³` is ~6144-bit and
`s^65537` is ~1.3 × 10⁸ bits; both reduce mod a 4096-bit `n`. The test was always runnable.
(Second, minor: that function's `notes` string calls the 2013 modulus "365-bit"; its own
runtime parse correctly reports **432** bits.)

### 3.2 The moduli were never missing

`extract_moduli.py` computes the RFC 4880 §12.2 v4 fingerprint from the **packet body**, so
identification does not rest on a filename:

| role | fingerprint | bits | e | witnesses |
|---|---|---|---|---|
| primary | `6D854CD7933322A601C3286D181F01E57A35090F` | 4096 | 65537 | 10, incl. two keyserver pulls |
| subkey | `DEC57731ACCBFD11EEBA13434D390ECF671DDEB1` | 4096 | 65537 | 10 |
| 2013 puzzle | (not a PGP key) | 432 | 65537 | `armada20/pgp_welcome.txt` |

No network fetch was required. **Provenance nit:**
`corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc`
is **misnamed** — the key inside fingerprints as `6D854CD7…7A35090F`; the two strings share
only the 32-bit short id `7A35090F`.

**Broadened scan (PREREG §3.1):** all **3,716** key-shaped files under `corpus/` and
`liber-primus/` → **22** distinct RSA public keys. Exactly **2 are 3301's**. The other 20 are
Round 18 L8's base-rate keys (Tor Browser devs, Tails, GnuPG release, bitcoin-core, mruzuki)
and two solver-tool keys. **No previously-unknown 3301 modulus exists on disk.**

### 3.3 Sub-result A — generic PKCS#1 v1.5 / PSS: **NULL**

Controls (PREREG §3.2), on locally generated RSA-2048 and RSA-4096 keys:

| plant | fires | recovered correctly |
|---|---|---|
| v1.5 type-1 (2048 & 4096) | ✔ | DigestInfo = SHA-256, digest **equals** the real SHA-256 of the message |
| EMSA-PSS (2048 & 4096) | ✔ | salt length 32 = the salt length used |
| v1.5 type-2 (2048 & 4096) | ✔ | plaintext recovered exactly |

False positives: **0 / 10,000** at each key size across all three matchers — the
pre-registered bar. A non-bar 100,000-block run measured **1** FP at each size, both from the
v1.5 type-2 matcher (1.0 × 10⁻⁵ measured vs ~1.5 × 10⁻⁵ analytic), and **zero** from type-1
and PSS: the matchers' measured FP rate matches their analytic rate. **Control PASS.**

Result: **738 tuples enumerated** over 23 moduli × 3 payload variants × {big-endian,
little-endian} × {right-aligned, and left-aligned wherever the modulus is wider than the
payload} × {65537, 3, 17}. **594 evaluated, 144 arithmetically excluded (`s ≥ n`),
0 structural matches.** Restricted to 3301's own three moduli: **54 evaluated, 36 excluded,
0 hits.**

One exclusion is itself informative: the payload's leading byte is **`0xcb`**, which exceeds
the leading bytes of both 3301 moduli (`0xc1` primary, `0xbc` subkey), so the 256-byte payload
placed in the **high half** of a 4096-bit block is already too large to be a valid signature
representative. That placement is excluded **by arithmetic**, not merely untested.

This sub-result was **independently replicated** in the same wall-clock window by the
concurrent `round18/L5-payload` run — different matcher implementation, different encoding
enumeration, same verdict NULL and the same skip pattern.

### 3.4 Sub-result B — **Crypt::RSA `ES::OAEP`, the author's own declared scheme: NULL**

**Yes, this shape was tested — and it had never been tested by anyone.** §3.3 alone would have
been a mis-specified negative.

R1 found 3301 naming their library; C3's `round19/C3/PGP-VERIFICATION-TABLE.json` confirms the
signatures. Both carrier messages **PASS** under `181F01E57A35090F`:

| file | signed | C3 verdict |
|---|---|---|
| `…/ibotpeaches/messages/2012/this-message-will-only-be-displayed.asc` | 2012-01-15T01:39:42Z | **PASS** |
| `…/pgp/messages/2014-01-rsa-oaep-challenge.asc` (= `…/2014/welcome.asc`, same SHA-256 `c9053eb4…`) | 2014-01-06T07:35:27Z | **PASS** |

Both carry `Version: 1.99`, `Scheme: Crypt::RSA::ES::OAEP`. **The scheme is the author's own
signed declaration, not an inference.**

**The layout was measured, not reconstructed.** The corpus contains the 2013/2014 key's prime
factors, hard-coded in two independent solver scripts
(`corpus/E-tooling/vendor/ctvrty-rozmer__bruh/perl-rsa-decrypt.pl` and
`corpus/A-primary-artifacts/cijhho123/2014/additional docs/scripts/Program to decrypt RSA message in perl.txt`).
The pre-registered gate — `p·q` must equal the published 432-bit modulus — **holds exactly**.
So 3301's own ciphertext was decrypted here (round-trip `pow(m,e,n) == c` verified) and the
encoded block read off the wire:

| property | measured value |
|---|---|
| block size | `k = 54` (432-bit key) |
| encoded message length | **`emLen = k − 1 = 53`** — every block's `m` is exactly 53 bytes |
| `EM` | `maskedSeed(20) ‖ maskedDB(33)` |
| MGF | MGF1, **SHA-1**, 4-byte big-endian counter |
| `DB[0:20]` | **`da39a3ee5e6b4b0d3255bfef95601890afd80709`** = SHA-1(""), i.e. label `P = ""` |

The `emLen = k − 1` quirk is real and is **not** what OpenSSL emits — testing only
OpenSSL-shaped padding would have missed it. The layout was identified **without assuming it**:
over (hash × field order), only one combination makes `DB[0:hLen]` identical across all three
of 3301's blocks, and its constant is exactly SHA-1(""), the value the specification predicts.

Two artifact findings fell out. (a) The container is
`len(name)\0 len(value)\0 name value` with **no separator** — the `,` that looks like a
delimiter is `0x2c`, the ciphertext's own first byte; reading it as a delimiter makes the value
come out one byte short of its declared length, and the armour's MD5 (which matches the
compressed blob **exactly**) proves nothing was lost in transmission. (b) The recovered 39-byte
message body is **not ASCII** and does not carry the `0x01` delimiter the v2.1 spec predicts,
which is recorded as an open observation, not a claim — the `lHash` predicate does not depend
on it.

**Matcher:** HIT iff MGF1-unmasked `DB[0:20] == SHA-1("")`. A **160-bit** predicate, FP ≈ 2⁻¹⁶⁰.

**Controls (PREREG Addendum A1.3):**

| control | required | measured |
|---|---|---|
| positive — 3301's **own** ciphertext blocks | 3/3 | **3 / 3 fire, recovery 1.000** |
| negative — random blocks at 53 B | 0 | **0 / 10,000** |
| negative — random blocks at 511 B | 0 | **0 / 10,000** |

**Control PASS**, and the plant is 3301's own artifact rather than a modern library's analogue.

**Result: NULL.** 126 rows, 36 arithmetically excluded, **0 hits**, over three sub-tests:
payload read directly as an `ES::OAEP` encoded block (36 configurations: 3 variants ×
{big, little} × block sizes {256, 128, 64} × offsets {0, 1}); `pow(s,e,n)` result read as an
encoded block at `emLen ∈ {k−1, k}`; and the block-count arithmetic below.

### 3.5 Key sizes — covered and not covered

`Crypt::RSA` concatenates `k`-byte blocks, so a 256-byte payload can only be a *whole*
ciphertext when `k | 256`:

| modulus | k | 256 / k |
|---|---|---|
| 7A35090F primary (4096) | 512 | **not an integer** → cannot be a whole ciphertext |
| 7A35090F subkey (4096) | 512 | **not an integer** |
| 2013 puzzle (432) | 54 | **not an integer** |

A 256-byte payload *is* a whole number of blocks under a **512-bit** (4 blocks), **1024-bit**
(2 blocks) or **2048-bit** (1 block) key. **3301 published no key of any of those sizes**, so
those three cases are **NOT COVERED** — not because they were skipped, but because the modulus
does not exist in the record. This is the single most concrete `reopens_if` in the lane.

Note also that the 2013 key is the **only** 3301 key whose private half is recoverable (from
the corpus primes), and `256 mod 54 ≠ 0` excludes it structurally.

---

## 4. Propagation — what moves

### 4.1 The rule, applied

PREREG §4.1: re-run iff the downstream input includes `canon_256.bin` at an index C1 changes
**and** its own control records single-byte sensitivity.

| downstream | touches idx 45/50/246? | verdict |
|---|---|---|
| **B-05** (payload as PRF seed, LEDGER `negative`) | **yes** — and it varied only the *other* six indices | **RE-RUN REQUIRED — done, §4.2** |
| E-02A/E-02B (zeroFP) | yes, but exact tests | re-run (cheap) — **verdict unchanged**, §4.3 |
| H-03 (cookie XOR) | yes, exact test | re-run — **verdict unchanged**, §4.3 |
| `characterize.py` battery | yes | re-run — **character unchanged**, §4.3 |
| `hash_hunt.py` AN-END probe | yes | re-run — **no preimage**, §4.3 |
| E-01 | yes | all three payload variants tested throughout §3 |
| B-04 (`seeds.py` §7 uses `canon_256.bin` as a seed source) | yes | **FLAGGED, NOT RE-RUN** — handed to S2, §4.4 |
| R16-KDF / R17 offset ladders | yes | **FLAGGED, NOT RE-RUN** — handed to S2, §4.4 |

### 4.2 B-05 — the headline, and why its negative was void

B-05's own `control_detail` records the avalanche it measured: *"Flipping ONE contested byte
destroys recovery (−7.38)"* — from −4.170 (perfect) to noise. B-05 swept single-position
variation at the **six** contested indices only. C1 changes **45, 50 and 246 — none of them**.
So B-05's Part-1 negative was computed on a seed that, on the image evidence, **is not the
payload**.

C1's plant-and-recover control measures that directly, on the resolved payload:

| generator | beam(resolved seed) | beam(wrong seed) | beam(**old `canon_256`** seed) | recovery |
|---|---|---|---|---|
| `sha256_ctr` | **−4.170** | −7.273 | **−7.512** | 0.989 |
| `rc4` | **−4.170** | −7.395 | **−7.050** | 0.989 |
| `hmac_drbg_sha256` | **−4.170** | −7.599 | **−7.617** | 0.989 |
| `aes256_ctr_k` | **−4.170** | −6.975 | −4.170 | 0.989 |

Control **PASS** (recovery 98.9 %, and **recovery — not score — is the gate**, per I1). On
**3 of 4** generators the superseded `canon_256` seed collapses to noise. (`aes256_ctr_k` is
insensitive because it consumes only the first 32 bytes of the seed, and all three corrections
lie beyond byte 32 — a useful reminder that "the payload" means different things to different
generators.)

**The re-run.** B-05's pinned Part-1 grid on the resolved payload's 6 representations:
6 × 15 generators × {mod, reject} × {fwd, rev} × {atbash, plain} × {±1} × 14 offsets =
**20,160 beam decodes**, exhaustive, plus B-05's constant-shift pass (1,740) and a freshly
recomputed shuffle null (200) = **22,100 decodes**.

**Scoring — corrected twice.** The first pass (`out_b05_rerun.json`) reproduced Round 13's
method: English quadgram only, judged against **−5.5**. Two Round-19 findings make that
inadmissible on its own — I3 measured −5.5 to be the wrong bar in **14 of 14** historical
sweeps, and doctrine **R3** requires the language-agnostic statistics to be stored *at sweep
time*, which that pass did not do (it would have been the 16th consecutive non-compliant
sweep). So the grid was decoded again and adjudicated through **I2**, persisting a full
**`SWEEPROW/1`** row per decode to `out_b05_sweeprow.jsonl`
(`b05_readjudicate.py` → `out_b05_readjudicated.json`).

Bars taken from I3's contract — **never −5.5** — for
`register = I19:vecbeam.keyskip1+I2` (licensed by I3's R-I1-5: this decoder is numerically
identical to `driftbeam`'s `keyskip1` preset), `segment_len = 120` (a calibrated length),
`n_trials = 20,160`, cells `CALIBRATED` at M = 10⁶:

| statistic | ESCALATE (α=0.05) | CLAIM (α=0.01) |
|---|---|---|
| `pmax` | **6.0485** | **6.5156** |
| `en` | **−6.2091** | **−6.0970** |

**Result — NEGATIVE, 0 escalations in 20,160 decodes:**

| statistic | best observed | ESCALATE bar | CLAIM bar | margin to escalate |
|---|---|---|---|---|
| `pmax` (max over the 9-register panel) | **5.203** (register **LP1_REAL**, `res.raw \| shake256 \| mod \| fwd \| atbash \| s−1 \| o=29`) | 6.0485 | 6.5156 | **−0.85** |
| `en` at L=120 | **−6.3785** | −6.2091 | −6.0970 | −0.17 |
| `en` at L=400 (Round-13 comparable) | **−6.8275** | — | — | — |

Not one decode of 20,160 reaches even the per-lane ESCALATE tier. `out_b05_sweeprow.jsonl`
passes I2's own `validate_store`: **20,160 / 20,160 rows validated**, header carrying the panel
build, the nine registers, the corpus SHA-256s and all three doctrine-Q4 conditionals.

Best-in-register, so the null is readable per register rather than only at the max:

| register | best `pmax` | | register | best `pmax` |
|---|---|---|---|---|
| LP1_REAL | 5.203 | | LATIN | 4.539 |
| OE | 4.867 | | EN_HALFVOWEL | 4.515 |
| EN_KJV | 4.867 | | DE | 4.418 |
| CY | 4.648 | | EN_NOVOWEL | 3.956 |
| EN_MODERN | 4.647 | | | |

The four R3-mandated language-agnostic statistics are stored for every row and sit exactly
where noise sits: IoC·N ∈ [0.841, 1.409] (mean **1.002** — flat), min-distinct-symbols over a
32-rune window ∈ [12, 20], conditional H₂ ∈ [0.000, 0.362], zlib ratio ∈ [0.792, 0.850]
(mean 0.822 — incompressible). Nothing anywhere in the grid looks like language.

**One incidental finding worth carrying forward.** Across the 20,160 decodes the register that
wins `pmax` is **non-English 83 % of the time** (EN_MODERN 1,755 + EN_KJV 1,603 = 3,358 of
20,160; CY 2,913, LATIN 2,888, OE 2,488, LP1_REAL 2,328, DE 2,309 lead it). That is L7-A's
point made mechanically on a live sweep: an English-only adjudicator is not merely weaker on
non-English plaintext, it is looking at the wrong channel for most of the search space even
when the answer is noise. It also means the *shape* of this null is only interpretable because
the panel was stored — which is the whole argument for R3.

**What this negative is worth.** It restores B-05's *arithmetic* validity under the corrected
seed and upgrades its adjudicator from English-only to a nine-register panel with calibrated
bars. It does **not** widen the decoder: see §6.1, conditional 2.

### 4.3 The zero-false-positive re-runs — all verdicts unchanged

Run on **both** `canon_256.bin` and `payload_resolved.bin` (`propagate.py` →
`out_propagation.json`). zeroFP's E-02/H-03 were re-run by **importing `zerofp_tests.py`
itself** and swapping only the payload bytes, so the false-positive accounting is identical to
Round 16's.

| test | canon | resolved | changed? |
|---|---|---|---|
| E-02A — any 56-byte window a permutation of 0..55 (201 windows; also 57-byte) | NULL | NULL | no |
| E-02B — payload as gap values vs the real doublet gaps | NULL (max \|r\| 0.042) | NULL (max \|r\| 0.042) | no |
| H-03 — 2013 onion cookies XOR'd against the payload | NULL (max printable 0.625) | NULL | no |
| AN-END page-56 preimage, 50 rep×alg combinations | 0 hits | 0 hits | no |
| entropy / distinct / printable | 7.1697 / 161 / 0.3984 | 7.1697 / 161 / **0.4023** | negligible |
| BE integer prime? smallest factor? | no, 2 | no, 2 | no |

**`hash_hunt.py` had no positive control at all.** C1 supplied one: planting a real digest as
the target makes the matcher fire as a **FULL** match; flipping the **first** nibble makes it
silent; **0 false positives on 10,000 random targets**. (Flipping the *last* nibble still fires
as **PARTIAL** — that is `hash_hunt`'s deliberate truncated-digest allowance, recorded so
nobody mistakes a PARTIAL for a preimage.) **Control PASS.**

### 4.4 Flagged but not re-run — handed to S2

**B-04** (`round13/B04/seeds.py` §7 seeds a generator from `canon_256.bin`), the **R16-KDF**
configs and **R17**'s offset ladders all consume the payload and are all input-sensitive. They
are **not** re-run here, because PREREG §4.1's second clause applies: their adjudicating
instrument is the one Phase 0 has just repaired, so re-running them against the *old*
instrument would spend budget to produce another English-only negative. They belong in **S2**,
which is already re-adjudicating the highest-prior slice of swept space — and S2 should use
`payload_resolved.bin`, not `canon_256.bin`, wherever the payload is an input.

**This is the concrete hand-off:** S2's B-04 slice must be re-seeded from the corrected
payload; its inputs change at 3 of 256 bytes, and B-05's avalanche control shows that is
enough to move a keystream decode from perfect recovery to noise on 3 of 4 generators.

---

## 5. Coverage × power

| item | coverage | measured power |
|---|---|---|
| **A-04** | all 11 disputed cells × 2 glyphs × 59 symbol + 5 digit classes, native 400 DPI, shifts in [−3,3]² — exhaustive, doctrine R5 rank-1 | **100 %** (59/59) on case-ambiguous glyphs in the single-template regime; 99.45 % overall; 100 % (106/106) on digits; separation rule licensed with 0 counterexamples in 29,161 pairs |
| **E-01 (PKCS#1/PSS)** | 23 moduli × 3 payload variants × 2 endiannesses × 2 alignments × 3 exponents = 738 tuples, 594 evaluated, exhaustive over what is published | plants fire 6/6 with exact digest/salt/message recovery; **0/10,000** FP per size; measured FP rate matches analytic |
| **E-01 (Crypt::RSA OAEP)** | 126 rows; direct-block, `pow`-then-decode, and block arithmetic; `emLen ∈ {k−1,k}` | **3/3 recovery on 3301's own ciphertext**; **0/10,000** FP at both block lengths; 160-bit predicate |
| **B-05 propagation** | 20,160 decodes, exhaustive over B-05's pinned Part-1 grid on the resolved payload; every decode persisted as `SWEEPROW/1` | plant recovers at **98.9 %**; but see the three conditionals — this is a *narrow* power envelope |

---

## 6. The three conditionals, what is NOT covered, and what reopens it

### 6.1 The three conditionals on the B-05 propagation negative (doctrine Q4)

1. **Key space** — B-05's pinned Part-1 grid restricted to the 6 representations of the
   resolved payload. The 6 `decpref` representations are unchanged by C1 and remain covered by
   B-05 itself. Nothing outside that grid is covered.
2. **Decoder transition model** — `skipdecode.beam_decode`, beam_w 120, max_skip 3. Its
   transition relation is **exact for `encipher_keyskip` and nothing else** (L7-B).
   **`skip_by_two` and free drift are not representable**, and L7-B measured the correct key
   at **−6.90 / 25.8 % recovery** under that construction. I1's repaired decoder recovers the
   same case at **−4.285 / 100 %**. This sweep deliberately did **not** use I1 — its purpose
   was comparability with Round 13 — so **this negative does not cover `skip_by_two`.**
3. **Adjudicator register** — I2's **9-register panel** on rune indices (not English-only, and
   not the 2013-era quadgram scorer alone), with `pmax` as the operative statistic and the
   four R3 language-agnostic statistics persisted per row. This is the one conditional C1
   *improves* on Round 13.

### 6.2 A-04 — not covered

- **3 of 256 cells (186, 210, 211)** do not segment into exactly two glyphs and were never
  adjudicated by the pixel instrument. None is a conflict cell; all three agree across all
  three witnesses, so they are **unchallenged rather than verified**.
- **idx 209** is objectively mis-segmented (best same-class IoU 0.117) and is the single miss
  in Controls 2 and 3. It is uncontested; its canon value stands unchallenged.
- The **class alphabet is closed** to the 59 symbol classes that occur in the payload. A glyph
  belonging to none of them — e.g. the never-occurring `f` = 41 — could not be recognised.
- The 245 non-conflict cells are **ground truth from `canon_256.bin`**, so an error shared by
  **all three** witnesses at a cell nobody disputed is outside this lane by construction.
- L5's three visual passes remain an **unverifiable transcript**; C1's second-reader pass is
  non-blind corroboration, not an independent blind read.

**Reopens if:** a higher-resolution or lossless master of pp49–51 appears (the current masters
are 400-DPI JPEGs); or an independent **blind** transcription of the 11 conflict cells
disagrees; or a better splitter segments 186/210/211 and disagrees with canon; or an exemplar
of a class absent from the payload turns up in a contested position.

### 6.3 E-01 — not covered

- **RSA moduli 3301 never published** — in particular the moduli behind the three 2014 onion
  RSA blobs, which are encrypted **messages**, not public keys, so their `n` is not recoverable
  from anything on disk.
- **512-, 1024- and 2048-bit keys** — the *only* sizes under which the 256-byte payload is a
  whole number of `Crypt::RSA` blocks (§3.5). 3301 published none.
- The **432-bit 2013 modulus over a 54-byte *window*** of the payload rather than the whole
  256 bytes; all 18 of its tuples are excluded by `s ≥ n` and no windowing was pre-registered.
- **Blinded, partial or fragmentary** signatures; **OAEP with a non-empty label `P`**;
  `Crypt::RSA::SS::PSS` and `Crypt::RSA::ES::PKCS1v15` as *signature* schemes (only
  `ES::OAEP` was measured from a held artifact); raw unpadded RSA.
- Payload transforms outside the four enumerated integer encodings (bit-reversed, hex-ASCII, a
  re-ordered byte permutation), and exponents outside {65537, 3, 17}.

**Reopens if:** a 3301 RSA modulus of 512, 1024 or 2048 bits is published or recovered; or the
moduli of the 2014 onion message blobs are recovered; or a windowed reading against the 432-bit
key is pre-registered; or a `Crypt::RSA::SS::*` signature artifact is found on disk from which
its wire layout can be measured the way `ES::OAEP`'s was here.

### 6.4 The propagation — not covered

B-04, R16-KDF and R17 are input-sensitive and **not** re-run (§4.4). Until S2 re-seeds them
from `payload_resolved.bin`, **their coverage of the payload family is conditional on a byte
string that the image evidence says is wrong at 3 positions.**

---

## 7. Trust anchor, after

```
python3 liber-primus/tests/validate.py        -> ALL VALIDATIONS PASSED (5/5)
python3 -m pytest liber-primus/benchmark/ -q  -> 8 passed
```

Unchanged from before the lane. No file outside `round19/C1/` was modified except the dated
addendum appended to `round18/L5-payload/RESULTS.md` (§8). No `git commit` from this lane.

## 8. Files

| file | what |
|---|---|
| `PREREG.md` | pre-registration + dated Addendum 1 (Crypt::RSA sub-test, I3 bar policy) |
| `singletons.py`, `out_singletons.json` | Controls 3 & 4 + physical discriminators |
| `visualcheck.py`, `crops/c1_cell*.png` | second-reader comparison strips |
| `adjudicate_all.py`, `adjudication.json`, `payload_resolved.bin/.json` | the 11-cell adjudication |
| `extract_moduli.py`, `moduli.json` | fingerprint-verified moduli |
| `e01_rsa.py`, `out_e01.json` | PKCS#1 v1.5 / PSS sub-result + controls |
| `cryptrsa.py`, `out_cryptrsa.json` | the measured `ES::OAEP` wire layout |
| `e01_cryptrsa.py`, `out_e01_cryptrsa.json` | the Crypt::RSA sub-result + its controls |
| `propagate.py`, `out_propagation.json` | zero-FP propagation + the AN-END control |
| `b05_rerun.py`, `out_b05_rerun.json` | B-05 re-run, Round-13-comparable scoring |
| `b05_readjudicate.py`, `out_b05_readjudicated.json`, `out_b05_sweeprow.jsonl` | the same grid under I2 + I3, **R3-compliant** |
| `ledger.json` | A-04 and E-01 fragments |

A dated addendum pointing here was appended to `round18/L5-payload/RESULTS.md`; that file was
**not** overwritten.
