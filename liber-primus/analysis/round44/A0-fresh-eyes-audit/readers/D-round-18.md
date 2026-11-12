# Fork D — Round 18 fresh-eyes audit (liber-primus/analysis/round18), 2026-11-12

Scope: SYNTHESIS.md, CAMPAIGN-PLAN.md, the eight lanes' PREREG/RESULTS/ledger fragments, load-bearing code
(`L2-filter-leak/{filter_models,a_locus}.py`, `L7-redteam/b1_power_envelope.py`), plus forward traces into rounds 19-43,
LEDGER.json (309 rows), MEASURED-CEILING.md, PICKUP-HERE.md. Repo untouched (`git status` clean after every probe).
Probe scripts (scratch only): `audit/D_work/{hash_recheck,skipnull_check,doublet_plain_link,doublet_plain_link2,reset_ioc,unit_simple_scan}.py`.
Paths below are relative to `liber-primus/analysis/` unless they start with a top-level name.

---------------------------------------------------------------------------------------------------------------------
## A. Answers to the six pointed questions

### Q1. L2 — what exactly was excluded, with what statistic, and what does "power" refer to?
* **Alternative set (complete list)** — `round18/L2-filter-leak/PREREG.md:72-80`, code `filter_models.py:51-141`:
  M0 no filter; M1 ciphertext key-skip (reference); M2 ciphertext value-rewrite; M2n ciphertext fixed-delta nudge;
  M3 keystream-side no-repeat; M4 plaintext-side no-repeat; M5 hard ciphertext rule.
  **Every one of the seven is `c = (p + rng.randrange(29)) % 29`** — an additive mod-29 cipher in Gematria index order with an
  i.i.d.-uniform key independent of the plaintext. They differ only in *where the equality test sits*.
* **Statistic** — ciphertext-only battery (`filter_models.py:145-187`): lag-1 rate, delta-spectrum chi2/df and max|z| over the 28
  non-zero deltas, pooled lag 2-8 "bleed", ABAB count. Parameterised models are bisected to the real lag-1 rate.
* **"Power 1.000"** — power of a Gaussian log-LR classifier to tell 200 *model replicates* from 200 *M1 replicates* at 5 % FPR
  (`a_locus.py`, "pairwise_vs_M1"), plus containment (real stream >= 4 sd outside the model). M3/M4 are excluded trivially:
  with a uniform independent key they cannot move the ciphertext doublet rate at all (0.0349 / 0.0347 at supp 0.999).
* **So the answer to the pointed question is NO**: no deterministic, state-dependent, ciphertext-feedback, polygraphic or
  non-additive construction is in the excluded set. The result is "*inside the uniform-pad family* the anti-repeat must act on
  the emitted symbol"; it is not evidence that a pad+rejection-sampler exists. Any construction whose output is a first-order
  chain with P(c_i=c_{i-1}) = r and flat off-diagonal is "ciphertext-identical" on this battery exactly as M2 is (power 0.175).
  The same additive/uniform-key premise underlies all 8 mechanisms (67 parameterisations) of L7-B
  (`round18/L7-redteam/b1_power_envelope.py:84-208`: every `enc_*` is `(p + K[j]) % N`; only the key POINTER varies).
* **"Drift 373.6 +/- 19.6"** is not measured on LP2: it is `rho*(n-1)` with rho = q s/(1-q s) and s fitted from 86/12,955
  (`RESULTS.md:47-61`). It is a consequence of M1; under M2 the drift is exactly zero (`RESULTS.md:472-477`).
* **"SAT route proved dead"** = `P(c_i | p_i, c_prev) = w/(N-s)` does not contain p_i (`RESULTS.md:350-365`) — conditional on a
  uniform key independent of the plaintext (the lane says so: not-covered #8, `RESULTS.md:498-499`). For any derived key the same
  budget says DETERMINED, so "dead" applies only to the full-entropy-pad member.
* **"Language-free screen at 3.08 sd"**: ONE planted correct key (n_skips 362) against 40 wrong keys of one generator family at
  full-book length 12,956 (`RESULTS.md:306-341`, `b5_skipchannel.json`). Followed up in R20/R21 (n_skips valid only >= ~6000 runes).
  **Verified defect in the same paragraph** (finding 7): "the two nulls agree at z = 0.32 ... an independent, decoder-level
  confirmation of the cipher model against the real data" (`RESULTS.md:328-331`) is vacuous. I measured wrong-key n_skips with the
  lane's own `fastbeam.beam_decode` on (a) UNFILTERED uniform ciphertext (423 doublets): 279/296/277/321/260, mean **286.6**;
  (b) HARD-filtered ciphertext (0 doublets): 268/344/280/307/286, mean **297.0**; published plant 296.3 +/- 21.4, real LP2
  297.8 +/- 19.8. The wrong-key skip count is a property of decoder + random key, not of the ciphertext's generating model.

New probes that narrow the Q1 gap (seconds of compute; scratch `D_work/doublet_plain_link*.py`):
* If repeats were *intrinsic* and tied to plaintext (e.g. a relative cipher whose zero step encodes one plaintext rune), the 86
  doublets would sit where that rune sits in words. Word structure is cleartext, so this is testable without a key:
  LLR over (word length, in-word index) cells of the 86 doublets, H_r (English positional frequency of rune r; 153,899-rune
  corpus from the repo's own prose docs) vs H_0 (uniform over positions). **All 29 runes rejected**: observed LLR lands on the
  H_0 expectation and far from H_r (e.g. EA: obs -209 vs E[H_0] -196 +/- 29 vs E[H_r] +77 +/- 8; T: -12.9 vs -22.5 +/- 7.4 vs
  +19.8 +/- 5.8); simulated power at 1 % = 1.00 for every rune (rare-rune profiles AE/EO/OE/J are corpus-sparse; treat those as
  indicative). Plaintext-pattern links also rejected: "doublet <=> p_i = p_{i-1}" (English rate 2.90 % -> 375 expected vs 86;
  positional LLR -67.9 vs +34.7 +/- 5.4 under H), "<=> p_i = p_{i-2}" (633 expected; power 0.97), "<=> p_i = p_{i-3}" (718; 0.68).
  4-class table: interior 45 (48.2 expected-uniform), word-final 18 (18.7), word-initial 23 (18.6), single-rune word 0 (0.6).
* Consequence: any surviving deterministic alternative must make its repeats **plaintext-independent** (key/state-driven).
  That is a real narrowing the repo has not stated, and it supports the filter reading without proving it.

### Q2. L3 — what became of the "256 non-runic tokens the analysis tree never held"?
* They are **the pp49-51 payload itself**. Verified: `round18/L3-ornaments/nonrunic.json` `base60.values` (256 ints) ==
  `round18/L5-payload/payload_resolved.bin` == current `pp49_51/canon_256.bin` (sha256 3b9b07d9...), and differs from
  `pp49_51/canon_256_superseded.bin` (4c8dc855...) at exactly idx 45/50/246 = L5's three corrections.
* So SYNTHESIS.md §4 ("never held in this repo's analysis tree ... not yet attacked") and §6 ("Cheapest untouched item: attack
  the 256 non-runic tokens") and `L3-ornaments/RESULTS.md:64-94, 367-370` were wrong when written: `pp49_51/` has held and
  attacked that object since Campaign VII (`pp49_51/CAMPAIGN-VII-FINDINGS.md:1-20`), and lane L5 of the same round is about it.
  What was true is narrower: the *geometry/ornament pipeline* binned those lines as ornament.
* It still propagates: `round43/CAMPAIGN-PLAN.md:17-19` lists "the pp49-51 payload" and "the R18-L3 ornament read (256
  non-runic tokens the analysis tree never held)" as two separate needle-movers. They are one object (double count).
* Useful by-product nobody recorded: L3's source for the tokens is two vendored community transcriptions (cmbsolver-lpviewer,
  libergo; byte-identical to each other, `nonrunic.json:checks`). They already carry L5's three "corrected" bytes. The errors
  were introduced by this repo's own majority-vote canonicalisation (relikd + scream decimal column), not by the community record.
* Token classes genuinely new in L3 and their later fate: ink tone (226 light components, 25 sites, 16 pages; `RESULTS.md:283-328`)
  and the p15 grid/`3299` -> R43 F2 + R44 P1/P2 (tracked). The "single grey marks in the left margin of p36, p37x3, p38"
  (`RESULTS.md:308`) are at x 601-670, height ~95 px, i.e. the five list numerals (the transcription holds digits 1-5 once each)
  -> covered by R44 P1 "red numerals". One isolated light component is not explained anywhere: p8, box x 333-355 / y 1569-1598,
  area 337 px, outside the text column (`greyglyphs.json` light list). Make sure P1's extractor keeps isolated marks.
* Still never done from L3's own not-covered list: #6 a from-scratch inventory of all non-body ink (only Round 8's catalogued
  bands were read; R43 F2 is a transcription-level census — coordinator should check with fork J whether it used the images);
  #7 the grey rows were not transcribed and diffed against canon (R44 P1 scope); inter-line leading never measured (B-12 reopen).

### Q3. L5 — do earlier payload analyses on the uncorrected bytes still stand un-re-run?
* Re-fed on corrected bytes: B-05 Part-1 grid (L5 §4.4, re-run by R19 C1), 210 hash probes, R16 zeroFP E-02A/B + H-03 (L5 §4.2-4.3),
  and in R34-P1: R16-KDF (7 payload secrets), R30-B1/B2 canon legs, recon h1_index, campaign18 payload_skip / payload_ciphertext /
  numeric2_skip, pp49_51/hash_hunt (`round34/P1-payload-promotion/RESULTS.md:13-27`).
* **Never re-run** (R34-P1 says so itself, `RESULTS.md:65`; ledger `R34-P1-PAYLOAD-PROMOTION.not_covered`, status `audit`, so it is
  not in the never-run/open query): `pp49_51/{campaign9,keytest,campaign20_extcipher,anend_preimage_3new,anend_preimage_broad,
  blake_closure,characterize}.py`, `campaign11_pin_the_filter.py`, `campaign12/payload_forensics.py`, `campaign14/probes.py`,
  `round29/L2-blob-cross/attack.py`, `round13/B05/prf.py` Parts 1b/2a/2b, `round17/P3_tables/build_pads.py`; plus R30-B1
  canon-as-key legs over T2/folly (inputs absent).
* The one member of that list where three bytes flip an exact answer is the page-56 512-bit preimage hunt under the hash families
  `hash_hunt.py` does not contain. R34-P1's sentence "the hash ones are the same class as hash_hunt, which was run" is not right:
  `hash_hunt.py:17-18` covers hashlib only; Whirlpool / Streebog-512 / Skein-512 (`anend_preimage_3new.py:2-4`) and original
  BLAKE-512 (`blake_closure/`) were never applied to the corrected payload.
* **Discharged here (scratch `D_work/hash_recheck.py`, KAT-gated, exact test):** corrected payload in 222 representations
  (raw/rev/+nl/hex/HEX/bit-reversed/base64/decimal strings/big-int decimal; quarters, halves, per-page slices 80/104/72;
  the printed token text in 30+ layouts incl. per-page, CRLF, no-space, upper/lower) x 10 algorithms (Whirlpool, Skein-512-512,
  BLAKE-512, Streebog-512 in both digest byte orders, Keccak-512 original padding, SHA-512, SHA3-512, BLAKE2b-512, SHAKE256/64)
  = 2,220 comparisons against 36367763...132c2a8b4 (also reversed-hex and byte-reversed digests, and 16-nibble partials): **0 hits**.
  Not run: Groestl-512, JH-512 (no vetted implementation at hand). Needs filing as a row by the coordinator.

### Q4. L8 — were the 433 seed candidates consumed?
* Yes, widely: `TIMESTAMP-SEED-CANDIDATES.json`/`seedprior20.json` is read by R21-L3 (Py2.7 reducers), R24 C1/C2/C2-EXT
  (matched-runic, skip_by_two decoder, bash/perl/tex axes), R25 compute-tail, R32-B2 (PHP) and R32-B3 (glibc gen=0), R34-B1,
  R36-B2 (grep of `sweep*.py` / PREREGs). The Py2.7 `pair` full-2^32 sweep covers every candidate < 2^32 as an int seed.
* Two loose ends: (i) ledger row `G-09` still says "(e) No seed was executed against any generator - coverage of the candidates
  themselves is zero by design" — stale; (ii) **112 of the 433 are >= 2^32** (millisecond and 14-digit forms). On 32-bit-seeded
  generators they either fold mod 2^32 or are dropped; no document states which lane did which. A 433 x generator x relation
  matrix would take minutes and would close G-09's own reopen clause ("a seed lane ... states which generators and index offsets
  it covered").
* L8's stronger legacy is the R19-C3 addendum inside its RESULTS (`L8-provenance/RESULTS.md:575-617`): two signed, verifying
  messages (2012-01-15, 2014-01-06) carry `Crypt::RSA` armor and a `Data::Dumper` dump — the only *measured* link between the
  author and a scripting language. See finding 2.

### Q5. L1 — how strong is the toolchain prior, and what does it assume?
* What is measured (`L1-toolchain/RESULTS.md:314-330`): the page JPEGs came through Ghostscript (ICC profile; render band 9.05-9.14
  per the R34 addendum, `RESULTS.md:441+`) and an ImageMagick-like encoder (R19 R1: a gs -> PIL `quality="keep"` chain reproduces
  all four discriminating JPEG fields, so even "ImageMagick" is not unique — `L8-provenance/RESULTS.md:562-568`); the PGP
  messages were signed with GnuPG 1.4.11 on GNU/Linux 2012-01-05 -> 2014-04-02 (corrected counts; distro bracket loosened).
* What the generator ranking (`RESULTS.md:344-362`) assumes on top of that, none of it measured: (1) the keystream was produced
  by a script at all; (2) on the same box/idiom as the renderer and the signer; (3) with a language's default **non-cryptographic**
  PRNG and a small seed. Every one of F1-F10 is about rendering, typesetting or signing; **no fact in L1 concerns keystream
  generation**. A daily GnuPG / Crypt::RSA user is at least as likely to reach for /dev/urandom, `gpg --gen-random` or
  `openssl rand` (rows 4/6/11), which the ranking leaves "unmoved". The ranking is labelled a prior (NC-8), but Rounds 19-42 spent
  most of their decode budget in its rows 2 and 4 (Py2.7 MT 2^32; bash orbits three times).
* Internal tension never resolved: L1's own example program (`RESULTS.md:383-387`, "`while True: x = rng(); if x != last: emit(x)`")
  is the HARD filter that L2 excludes in the same round (M5, 0 doublets). No lane asks what program yields s = 0.813. Note that a
  typed constant fits: s = 0.8 predicts 91.9 doublets, s = 5/6 predicts 76.6; observed 86 (sd ~9).
* L4 gives toolchain evidence L1 never used: the line breaks are reproduced by a **greedy rune-level line breaker** driven by glyph
  widths, mid-word (`L4-forcing/RESULTS.md:84-170`, 53.5 % exact / 82.5 % within +/-1). TeX's paragraph builder does not break
  that way by default; this bears on L1's rank-5 "LaTeX-shaped job" inference (F4+F5) and on the TeX-LCG prior.
* Cheap finite items that would move the prior and are still open: `G4-ALLRUNES-NC5` (ledger status `open` since Round 19: run
  L1's `font_match.py` with the 72 allrunes faces; R19 G4 struck the "slot search" blocker, `round19/G4/RESULTS.md:273-304`),
  NC-4 Junicode/Everson (B-11). B-11's `not_covered` still repeats the refuted blocker. Neither is in PICKUP-HERE's open list.

### Q6. L4 and L6 — what remains unfinished?
* L4 (`L4-forcing/RESULTS.md:413-435`; ledger C-02): forcing on < ~40 % of lines is masked by typography (blind at f <= 0.2);
  Arm C cannot see a boundary-doublet *deficit* at any alpha (539 transitions); non-rune-valued forcing (word/line lengths,
  punctuation placement) untouched; L3-defined positional subsets never re-run through the layout-aware null; English-only Arm B.
  All recorded in C-02 (tracked). One loose thread: A7 sentence-initial chi2 = 47.7, p = 0.0097 (`RESULTS.md:71`) was never put
  through the layout-aware null that explained A1 (finding 10).
* L6 (`L6-offset-marsaglia/RESULTS.md:226-247, 292-312`; ledger B-13-MARSAGLIA partially-run, B-02, B-08): 679 of 756 Marsaglia
  units (10 of 12 builder x byte-order combos); the whole-ISO view; stage A2 2,516 of 3,024 units; offsets > 2^20 (A1) / 2^18 (A2);
  offset schedules. Everything that *was* swept used the English trigram prefilter (~44-47 % blind) + the one-rejection beam +
  the English scorer, i.e. the pre-R19 instrument; only the top survivors were re-scored under 8 registers. Tracked.

---------------------------------------------------------------------------------------------------------------------
## B. Ranked findings

1. **[LOGIC-GAP / UNDISCHARGED] The value-rewrite locus (M2) has no measured power under the current instrument generation and is
   missing from the ceiling page's conditionals.**
   R18-L2: M1 (key-skip) and M2 (rewrite) are ciphertext-identical, separation power 0.175; "a sweep must cover both, and no
   ciphertext statistic will ever tell you which" (`round18/L2-filter-leak/RESULTS.md:122-128`; ledger `R18-L2-A-LOCUS.not_covered[0]`).
   The project's own verdict sentence through Rounds 20-24 is literally "soft anti-repeat **rewrite** on the ciphertext output"
   (`round20/SYNTHESIS.md:172`, `round24/SYNTHESIS.md:128`, `PICKUP-HERE.md:428`). Yet the R32/R33 instrument lanes list
   "rewrite/keyside/plainside constructions" as **not represented** (`round32/I1-skipbytwo-decoder/RESULTS.md:124`,
   `round33/I1-register-aware-beam/RESULTS.md:103`), `MEASURED-CEILING.md` contains zero occurrences of "rewrite"/"overwrite"
   (its limits cell names skip_by_4/5, per-page/per-line reset, combined axes), and I found no M2 plant through `pf_v4`/`beam_v3`
   in rounds 34-43. The only M2 evidence is Round 12 D1's `rewrite_gate.py` under the old beam and the English scorer (B-16).
   Under M2 a 24-rune head contains >= 1 overwritten rune with probability 1-(1-0.028)^24 = 0.49, and a skip-Viterbi screen has
   no move that explains an overwritten rune. Recovery is probably decent (the zero-skip path is the right path), but the
   "excluded at power 0.95-0.99" figures for the bash/PHP orbits are measured for key-skip plants only.
   Check: grep "rewrite|overwrit|M2" over MEASURED-CEILING, PICKUP-HERE, rounds 32-43 md/py, LEDGER rows R3x/R4x.
   Cost: 1-2 h (plant M2 at supp 0.8129 through the standing control harness: screen power per register, beam_v3 recovery at
   L = 120/240; add the conditional to the page). Finite.

2. **[UNDISCHARGED, tracked but mis-prioritised] The classic time-seed band and the Perl 2^32 were never swept at power, although
   they are the best-evidenced generator cells and the gate that held them is gone.**
   (a) `srand(time)`-type seeding: every unix second 2012-01 -> 2014-06 (~76 M integers, also covers time^pid / time+pid for
   pid < 2^15) is swept under the repaired instrument only for bash 3.2 (`MEASURED-CEILING.md:53`, R40-B1) and, as integer seeds,
   by the Py2.7 `pair` full-2^32 sweep (R27). For glibc `random()/rand()` (L1 rank 1) the list holds only midnight + top-of-hour seconds — 48,036 seeds,
   `not_covered`: "seconds not on the list" (ledger `R32-B3-GLIBC-GEN0-PRIORDENSE`); PHP's uniform tier is a 0.97 % random sample of 2^32
   (so ~1 % of the band; ledger `R32-B2-PHP-MT-RAND`); Perl has ~1,100 seeds scored (`R26-A`) plus the R24 C2-EXT prior slice. Round 8's all-seconds sweep used the rigid decoder
   ("coverage x power ~ coverage x 0", ledger `R19-G2-CORRECTION`). The band is ~1.8 % of each 2^32 cell queued in R28-L4
   (never-run, "15-19 days" for 25 cells) and is the size of one bash orbit, which has been screened and decoded three times.
   (b) Perl: the only generator with a *measured* author link (signed Crypt::RSA / Data::Dumper messages,
   `round18/L8-provenance/RESULTS.md:575-617`; L1 row 3 re-sourced, `L1-toolchain/RESULTS.md:354`). Its auto-seed is a U32 read from
   /dev/urandom, so the complete space is exactly 2^32 *including the "used urandom" case* (`round19/G2/RESULTS.md:157-182`).
   PICKUP-HERE still files it as "sieve-gated ... more of the same letter-stream sweep at a flat prior" (`PICKUP-HERE.md:615-622`);
   the sieve (pf_v4) has existed since Round 35 and the estimate was ~34 h full. Not in the Round 44 plan or its deferred list.
   Cost: band x {glibc TYPE_3, Perl drand48, PHP mt_rand} = hours each on the existing C screen; Perl full 2^32 ~1.5 core-days.
   Enumerable, finite.

3. **[LOGIC-GAP] "The filter acts on the ciphertext (alternatives excluded at power 1.000)" is a statement inside the
   additive-uniform-pad family only** (Q1 above). It is quoted without that scope in SYNTHESIS.md:19, the README headline and
   MEASURED-CEILING's cipher-class line. New evidence from this audit narrows the gap: doublet positions are plaintext-blind
   (single-rune and plaintext-repeat links rejected at power 0.97-1.00). Filing cost: minutes; the probes are in `D_work/`.

4. **[SHARED-PREMISE] Where the soft filter's coin comes from, and unit stride.** L2/L7 draw the coin from a separate RNG
   (`filter_models.py:62`, `b1_power_envelope.py:158`). In a one-PRNG script the coin consumes generator output. Round 19 I1 did
   build `coin_from_key` (`round19/I1/constructions.py:208-230`): missed by keyskip1, 90.8 % / 71.8 % under `pair` at L = 240 / 400,
   1.00 only under the permissive decoder (`round19/I1/RESULTS.md:182, 197, 424`) — and the mass sweeps run keyskip1 + keyskip2
   only. Checked: the first visible doublet in LP2 is at flat index 122, so the L = 120 head of page 0 is safe (coin_from_key
   == skip_by_two there), but an L = 240 escalation of a true key decays under `pair`, and 29 of 55 pages have a visible doublet
   inside their first 120 runes (relevant to any per-page lane, e.g. R44 R1). Not represented anywhere: the coin evaluated
   *before* the equality test (`if rng() < 0.8 and c == prev`), i.e. one coin per rune = a stride-2 keystream; no "stride"/
   "decimat" hit exists for any generator sweep (grep rounds 19-43, MEASURED-CEILING, PICKUP, PARKED). Cost: stride-2 x bash
   orbit = one more orbit pass (hours); the escalation rule fix is a doc line.

5. **[CONTRADICTION] L3's "256 non-runic tokens never held / not yet attacked" is the Campaign-VII payload** (Q2). Double-counted in
   `round43/CAMPAIGN-PLAN.md:17-19`. Tidiness, but it inflates the "overlooked object" track record R43/R44 are argued from, and it
   hides a real fact: the vendored community transcriptions were right on the three bytes all along.

6. **[UNDISCHARGED -> discharged here, NEGATIVE] Corrected payload vs the page-56 hash under Whirlpool / Skein / Streebog /
   BLAKE-512 / Keccak-512** (Q3). 2,220 exact comparisons, 0 hits. Needs a ledger row; Groestl-512 and JH-512 remain.

7. **[LOGIC-GAP, verified by compute] L2 §4.3's "decoder-level confirmation of the cipher model" is vacuous** (Q1): wrong-key
   n_skips is ~287-297 on unfiltered, hard-filtered, soft-filtered and real ciphertext alike. Strike the sentence; the screen's
   usefulness (R20/R21) is unaffected.

8. **[UNDISCHARGED, tracked-stale] `G4-ALLRUNES-NC5` (open since Round 19) and B-11's NC-4** (Q5). Minutes once the fonts are
   fetched; outcome re-ranks the fully enumerable TeX LCG (2^31).

9. **[CONTRADICTION / stale] Ledger `G-09` says no seed was ever run; 112/433 candidates exceed 2^32 with unstated handling** (Q4).

10. **[DROPPED-LEAD, weak] Sentence-initial non-uniformity.** L4 A7 chi2 = 47.7, p = 0.0097, n = 219 (`L4-forcing/RESULTS.md:71`),
    filed NEGATIVE on Bonferroni and never tested with the layout-aware null. My recount: sentence-initial column IoC x 29 = 1.09
    (z = +2.5, n = 217); line-second z = +2.3 (L4's A9 p = 0.043). Likely layout bleed or noise. 5-minute check: restrict to
    sentence starts that are not line starts and compare the over-represented runes with L4's wide-glyph set.

11. **[SHARED-PREMISE, small] The generator census has no awk.** 0 hits for gawk/mawk/awk in LEDGER.json or any census doc, though
    L1 rank 4 is "Bash/coreutils composites". Unseeded gawk `rand()` is ONE fixed stream (its own BSD `random`, not glibc TYPE_3:
    R32-B3 `not_covered` "initstate sizes other than TYPE_3"); `srand()` = the time band; mawk 1.3.3 (Ubuntu's default awk)
    auto-seeds from the clock. Minutes for the fixed stream; one band pass for the rest.

---------------------------------------------------------------------------------------------------------------------
## C. Probes run in this audit that came back clean (useful nulls)

* **Identical key restarts per unit are excluded without a decoder** (`D_work/reset_ioc.py`; extends L4 Arm A beyond index 0).
  Column IoC x 29 at in-unit index 0..11: pages 0.90-1.19 (n = 55, all |z| < 1.5); lines 0.99-1.03 except index 0 = 1.09
  (z = +7.1, the known glyph-width inspection paradox, L4 §2); sentences 0.94-1.09; words 0.96-1.00 (n up to 2,928); from-end
  indices flat. An identically restarting key would give ~1.7 at small indices. R44 R1 can therefore be restricted to resets to
  *different* key positions (page/line-number-dependent), which is a much smaller and different lane.
* **No simply-enciphered unit hides in a mixture** (`D_work/unit_simple_scan.py`): every sentence (204 with >= 8 runes) and every
  line (590) under the 58 keyless reads LP1 used (shift 0-28 x identity/atbash), English quadgrams, length-matched max-over-58
  null: max z 4.28 / 4.56, reads are gibberish; planted control z = 10.0.
* **Headline statistics reproduce** with an independent loader: 12,956 runes, sha 023312..., 86 doublets, 4 crossing a line break,
  0 crossing a page join, delta-spectrum chi2 42.1 / 27 df (L2 reports 1.533/df and flags it at +2.0 sd; still there after the
  R33 transcription fixes; no single cell above Bonferroni).
* L2 closed forms (s* = 0.81288, rho = 0.02884, (1-rho)^24 = 0.495) are arithmetically consistent.
* L5: the three corrected bytes are corroborated by three independent witnesses (scream tokens 11/11, pixel IoU, and the two
  community files via L3). Cells 186/210/211 "never segmented" are not conflict cells in any witness.
* L8 PGP table was independently re-derived by R19 C3 (228/228); not re-audited here.

---------------------------------------------------------------------------------------------------------------------
## D. Premises this round never tested

1. The combination is addition mod 29 in Gematria index order with a uniform, plaintext-independent key (all 7 loci, all 8
   mechanisms, every sweep). Mixed-alphabet / non-additive polyalphabetics escape the G3 floor argument entirely (L7-C.2's
   floor is min over a *shift* delta; for general permutations the minimum is an assignment problem and can be far lower).
2. The coin is exogenous and the keystream is consumed at unit stride.
3. The keystream was generated in the rendering/signing toolchain's idiom with a small-seed default PRNG (no measured fact).
4. One locus and one mechanism for the whole book (stationarity was measured at power 0.075, `L2 RESULTS.md:478-481`).
5. The soft rate is a parameter to fit rather than a clue to the program (0.8 and 5/6 both fit 86).
