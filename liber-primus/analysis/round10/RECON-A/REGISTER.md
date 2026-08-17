# Round 10 — RECON-A: register of un-executed / partially-executed leads

_Produced 2026-08-12 by mining every `*.md` under `liber-primus/` and `research/` (107 files),
then verifying on disk whether the artifact of each named test exists. Pre-registration and
rejection rules: `PREREG.md` (same folder). No attack was run in this lane._

**Result vs threshold:** 30 leads survived (threshold for lane success was ≥15). H0 rejected —
the repo's document layer contains substantial un-finished work.

**What is NOT here.** Anything foreclosed by a mechanism kill was dropped even where a doc still
phrases it as open: another keytext (rigid or skip-aware, Round 7), autokey (positively refuted,
iter 9), additive/number-theoretic/PRNG-structure keystreams, differencing/integration,
page-on-page keying, fractionation/Polybius/trifid, transposition-only (incl. the rail/route
residue — Gate-#1 killed at DEAD_ENDS:74-82), substitution/homophonic-preserving-IoC, Hill,
alphabet reordering, rune-inventory miscount, image byte/DCT stego, AI-vision re-transcription,
page geometry (glyph shape / advance / baseline), byte-payload containers, doublet-pointers,
positional walks and sieves, the AN-END retrieval hunt, the word-length excess (Round 9 closed it
against itself), the ~75-page "transcription gap" (Campaign XIV: solved pages), the T2/T3 blobs
(iter 11), the 2013 Columbus-GA Shamir share (over-determined, iter 4), and the 2012 "7 images"
endpoint (no primary source, iter 4).

**Also corrected on the way through:** `research/DEAD_ENDS.md:255-264` says the Campaign XVIII
skip program "survives only as orphaned Python-3.12 `.pyc` bytecode (source deleted)". That is
now **stale** — all 18 sources are present on `master`
(`analysis/campaign18_skip/**.py`, zero `.pyc`), so that program is auditable and re-runnable
again. Likewise `FRESH-ANGLES §4`'s list of seven "lost" campaign directories: `recon/i6_wordlen`,
`stylometry`, `latin`, `bookcipher`, `stones`, `independent-read`, `stones/altrep` all have
their sources restored. The 2026-08-11 branch merge fixed it.

---

## A. Transcription / artifact layer (highest value — this is the class the program itself
names as one of only three inputs that could reopen the cryptanalysis)

| id | lead | source | status |
|---|---|---|---|
| A-01 | Round 9 Track TEMPLATE, the only genuinely from-scratch re-transcription, stopped at stage 2. `read_lines.json` holds 16,245 image-read glyphs across 646 lines; `diff.py` (stage 3: recover the class→rune permutation, diff vs canon) has **no output artifact on disk** and no verdict was ever appended. | `research/ROUND-9-RESULTS.md:133-143`; `analysis/retranscribe/` | partially-run |
| A-02 | O/A/AE per-instance adjudication. `independent-read/oae_mismatch.json` holds **450** located disagreements (page/line/pos) between the label-free clusterer and canon; no per-instance verdict was ever recorded. FINDINGS ends "the individual calls remain, as ever, a matter for a human expert." | `research/FRESH-ANGLES-2026-08.md:204-223`; `analysis/independent-read/FINDINGS.md:88-96` | partially-run |
| A-03 | Haplography count-audit of the 86 doublet sites — crop the neighbourhoods and audit **rune count** (not identity) against canon. Flagged twice as "documented but heavier"; never run. Campaign IX's i9_ocr only spot-checked p0 lines 1-3. This is the cheap falsifier of the whole engineered-filter edifice: ~20 confirmed merges would put autokey back on the table. | `analysis/CAMPAIGN-XIV-FINDINGS.md:84`; `analysis/campaign14/REDTEAM-PROPOSALS.md:120-125` | never-run |
| A-04 | pp49-51's **6 contested bytes** (idx 25, 175, 182, 199, 215, 237) — flagged open in Campaign VII and repeated in Campaign IX; needs a Latin/digit OCR, which the rune classifier cannot do. Never done. | `analysis/pp49_51/CAMPAIGN-VII-FINDINGS.md:68,170`; `CAMPAIGN-IX-FINDINGS.md:83` | never-run |
| A-05 | Separator audit: 19 rune-count-exact lines disagreed on separator count; listed in `geometry/separator_audit.json` as "the correct shortlist for a human or high-zoom re-read". Never re-read. | `research/ROUND-8-RESULTS.md:375-382` | partially-run |
| A-06 | Ornament bands. Round 8 catalogued 47 non-text bands over 23 pages (`geometry/ornaments.json` holds 62 rows) and states this "is inventory, not a result — the one item in Round 8 left as an open thread"; the short bands (1/3/4/8/16 glyphs) "are the only real ornament candidates and **nobody has read them**". | `research/ROUND-8-RESULTS.md:211-218`; `research/DEAD_ENDS.md:358-360` | never-run |

## B. Keystream-entropy layer (Round 8 SEED's own stated residue)

| id | lead | source | status |
|---|---|---|---|
| B-01 | The full 32-bit sweep is **2/10 complete**. `results_full32.txt` holds only gen=3 (MSVC) and gen=5 (MT19937); gen=0 (glibc — first in `run_full32.sh`'s priority order and the highest-prior generator) is **absent**, and no `DONE` line. PICKUP-HERE still describes it as "still running". | `PICKUP-HERE.md:121-122`; `analysis/seed_sweep/results_full32.txt`, `run_full32.sh` | partially-run |
| B-02 | Keystream **offset ≠ 0**. Round 8 states its sweep "assumes key index 0 aligns with the first rune of LP2 page 0". An author who enciphered LP1 first, or started the pad mid-file, is invisible to it. | `research/ROUND-8-RESULTS.md:124-129`; `research/DEAD_ENDS.md:328-332` | scope-limited |
| B-03 | Generator families Round 8 names as untested: PHP `mt_rand` (distinct tempering), .NET subtractive, xorshift, RC4/ARC4, Java's full 48-bit space, MT `init_by_array` multi-word seeds, `/dev/urandom` (declared unattackable). | `research/DEAD_ENDS.md:328-332` | scope-limited |
| B-04 | **Cryptographic** keystream generators from a Cicada seed dictionary — MD5/SHA-1/SHA-256/SHA-512 in chain and counter mode, HMAC-DRBG, AES-CTR, RC4 — reduced mod 29, with the filter-aware beam. Proposed in Campaign XIV, listed again as "documented but heavier", never run; Round 8 swept only *hobbyist* PRNGs. Note the iter-6 MDL claim ("exactly incompressible → not an algorithmically-generated pad") does **not** kill this: a hash/stream-cipher keystream is incompressible by construction, so that measurement has no power against this family. | `analysis/campaign14/REDTEAM-PROPOSALS.md:64-69`; `analysis/CAMPAIGN-XIV-FINDINGS.md:83` | never-run |
| B-05 | pp49-51's 256-byte payload as a **PRF seed** expanded into a runic keystream (RC4/AES-CTR/SHA-counter/HMAC-DRBG), rather than used directly as key material. Campaign XX applied AES/RC4/ChaCha to the payload as *ciphertext*; nobody expanded it into a keystream over the runes. | `analysis/campaign14/REDTEAM-PROPOSALS.md:71-76`; `analysis/pp49_51/CAMPAIGN-XX-EXTCIPHER.md` | never-run |

## C. Cleartext / plaintext-identification layer

| id | lead | source | status |
|---|---|---|---|
| C-01 | SKELETON corpus extension. Round 8's word-length plaintext-identification is negative **for 51 texts / 8.2M words**, and says so explicitly: "it eliminates a specific 8.2 M-word corpus, not 'any known text'… extending it to a full Gutenberg mirror is the obvious follow-up and `wordlen_search.py` is written for it". Never extended. | `PICKUP-HERE.md:123-124`; `research/ROUND-8-RESULTS.md:333-337`; `research/DEAD_ENDS.md:407-409` | scope-limited |
| C-02 | Line-initial / word-initial / page-initial ciphertext-rune uniformity test — the detector for *forcing* (an acrostic or layout constraint imposed in ciphertext). Proposed with a hard gate (p<0.001); no script and no result anywhere. | `analysis/campaign14/REDTEAM-PROPOSALS.md:29-34` | never-run |

## D. Structure / generator-fingerprint layer (mostly attribution-relevant)

| id | lead | source | status |
|---|---|---|---|
| D-01 | Generator-fingerprint suite items (1)+(2): conditional next-rune distribution after each rune value, and a **windowed χ² under-dispersion sweep**, plus **monogram frequency drift across the book** (fatigue signature). The proposal names these as the two provenance sub-tests **Campaign IV skipped**. Never run. Discriminates a machine sampler from a human drawing a pad by hand — which is exactly the load-bearing claim in FINAL-SYNTHESIS' technique fingerprint. | `analysis/campaign14/REDTEAM-PROPOSALS.md:43-47,127-131` | never-run |
| D-02 | Higher-order model test against **matched** controls. The proposal asked for cross-validated bits/rune at PPM orders 1-8 vs **1,000 controls generated with campaign11's suppression model**. What was actually run (`recon/i6_mdl/mdl_test.py`) uses **40 uniform-random controls** and context order ≤5, with no cross-validation — so the one anomaly it found (order-1 entropy dip, z=−14.6) is exactly what an unmatched control makes inevitable. | `analysis/campaign14/REDTEAM-PROPOSALS.md:43-47`; `analysis/recon/i6_mdl/mdl_test.py:36-37` | scope-limited |
| D-03 | Homophonic-**downward** (surjective 29→k, k=5..26) annealing/EM search. Closed only by an *inference* from bigram flatness (Campaign XIV P4, +0.81σ); the search the proposal specified — anneal the partition, validate on synthetic homophonic ciphertext, score against a 1,000-shuffle envelope, check generalisation to held-out pages — was never coded. | `analysis/campaign14/REDTEAM-PROPOSALS.md:57-62`; `analysis/campaign14/probes.py:118` | declared-closed-but-thin |
| D-04 | Non-additive ciphertext-feedback coefficient sweep ran on **3 of 55 pages** (p0/p5/p20) at orders k≤3 with 3 seeds, then was written up as "closes the last additive-adjacent corner". | `analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md:102-112` | scope-limited |

## E. pp49-51 payload — readings named and never executed

| id | lead | source | status |
|---|---|---|---|
| E-01 | Payload as an **RSA signature/ciphertext** under known Cicada moduli: compute `pow(s,e,n)` in both endiannesses for every published 3301 modulus and pattern-match PKCS#1 v1.5 / PSS structure. Zero-false-positive test, minutes of compute, never run. The ledger's "not a prime / modulus is even" result does not address it. | `analysis/campaign14/REDTEAM-PROPOSALS.md:113-117` | never-run |
| E-02 | Payload as **meta-parameters**: (a) slide a 56-byte window and test for a permutation of 0-55 (chance ≈1e-24 per window); (b) read the payload as 85-128 gap values (8/16-bit LE/BE, varint) and rank-correlate against the real doublet gaps [122, 85, 249, 197, 129, …]. Both "instant"; neither run. Round 8 POINTERS correlated the gaps against primes and Fibonacci, never against the payload. | `analysis/campaign14/REDTEAM-PROPOSALS.md:85-90` | never-run |

## F. Inverted framings named and never executed

| id | lead | source | status |
|---|---|---|---|
| F-01 | **LP2-as-pad inversion** — the unsolved pages are *key material*, not a message. Use the 12,956-rune stream (fwd/rev, ±, Atbash) as a running key against every other machine-readable Cicada object (2012/2013 fragments, the AN-END hash bytes, canon_256, onion names, PGP bodies). Finite candidate set, hours of compute, never run. Note it survives the iter-2 "message-existence is undecidable" finding rather than being killed by it. | `analysis/campaign14/REDTEAM-PROPOSALS.md:148-152` | never-run |
| F-02 | The 2016-01-01 signed message is the **only signed methodological hint 3301 ever gave**. Round 9 attacked "their numbers are the direction" (2,670 readings, negative) and both closing lines of Round 9 and DEAD_ENDS state that its other two clauses — "its words are the map" and "their meaning is the road" — **remain uninterpreted**. No lane has ever treated them as a first-class object. | `research/ROUND-9-RESULTS.md:126-129`; `research/DEAD_ENDS.md:487-489` | stated-but-uninterpreted |

## G. Provenance / physical-artifact layer

| id | lead | source | status |
|---|---|---|---|
| G-01 | **PROVENANCE track never ran.** FRESH-ANGLES proposed five parallel tracks; Round 8 executed SEED, GEOMETRY, PAYLOAD, POINTERS, SKELETON. Track 5 (source PDF + rune-font identification: Ghostscript build fingerprint from DQT+ICC+geometry, hunt circulating PDFs with a real text layer, re-read the on-disk archived `onion7_index.html` for non-`.jpg` assets, match glyph outlines against stock runic faces) was never executed and appears in no results doc. | `research/FRESH-ANGLES-2026-08.md:227-245,274-278` | never-run |
| G-02 | STEGO-VERDICT's own "**decisive next experiment**" #1 — `outguess -r` on a blank/control JPEG through the same 400-DPI Ghostscript pipeline, to prove the shared 1417-byte prefix is a default-key artifact — was deferred because "this Windows box has no way to run OutGuess (no WSL/Docker/compiler)". That constraint has evaporated (WSL2 Ubuntu with gcc is present, and OutGuess 0.4 was later built for the OSINT sweep). The blank-control result appears nowhere. The 60-key sweep that did run was against the **onion images**, not pages 0/4/26. | `analysis/stego/STEGO-VERDICT.md:78-91`; `research/FRESH-ANGLES-2026-08.md:122-128`; `analysis/OSINT-SWEEP-2026-07-27.md:92` | never-run |

## H. OSINT residue explicitly left open by the 2026-07-27 sweep

| id | lead | source | status |
|---|---|---|---|
| H-01 | Per-onion HTTP/server-status anomalies: ports 5240/5241/5242/5243, mock uptime "1 days 0 hours 33 minutes 14 seconds" → 1033, leaked host `li676-224.members.linode.com` / 106.186.123.224, and `<head>`/`</head>` malformation varying per onion ("theorized to bind the onions together"). Listed as item 6 and as "still genuinely open"; **never resolved as a channel**. Raw HTML is held locally. | `analysis/OSINT-SWEEP-2026-07-27.md:44-47,94` | never-run |
| H-02 | Full-corpus whitespace re-audit **at scale**. T6 ran run-length decoding and reproduced known numbers; the sweep still lists the at-scale re-audit as open, and the wiki's own note is that the tab/space channel was "never fully utilized". | `analysis/OSINT-SWEEP-2026-07-27.md:48-50,91,94` | partially-run |
| H-03 | Two named micro-crosses recorded as never executed: the 2013 onion cookies (`167=6941…`, `761=7bc1…`) **XOR'd against the four hex strings** ("that specific cross is untried"), and the 2012 P.S. digit-string **rotate-90°/matrix reading** ("never executed, but P/Q factorization is done; completeness-only"). | `analysis/OSINT-SWEEP-2026-07-27.md:57-60` | never-run |

## I. Attribution goal — leads named and never executed

| id | lead | source | status |
|---|---|---|---|
| I-01 | `mruzuki` / `cicadeur` (keyid `02BD208AFB8AFF75`, `mruzuki@gmail.com`, key created 2012-01-12, self-revoked 2012-01-22 — seven days after the first 3301 image) is the **earliest Cicada-adjacent keyserver actor** and the auditor's own #1 remaining item. No identity resolution was attempted beyond public/sandbox sources. | `analysis/AUDITOR-LOOP-2026-07-28.md:42,52,58` | never-run |
| I-02 | A **separate 2013/2014 winner forum** — closer to the LP than the timeline-eliminated 2012 forum, and the only insider space that could have received a privately-delivered pad. Campaign XIX flags it as an open thread; nobody looked. Adjacent: the un-corroborated 2013-winner claimant "Nox Populi" (reachable, DEF CON 26 speaker) was rated "worth a low-priority contact" and never contacted; the 2026-07-27 Wanner outreach shows no logged response. | `analysis/attribution/CAMPAIGN-XIX-WITNESSES.md:126,148-152,164` | partially-run |
| I-03 | Pre-disclosure search of archived cypherpunks / metzdowd / bitcointalk posts 2011-2013 — Campaign VIII's own #1 open thread, "unresolved only because the archives are thin, not because it was cleared". Never executed as a search. | `analysis/attribution/CAMPAIGN-VIII-ATTRIBUTION.md:83-86` | never-run |
| I-04 | Pull the **full Schoenberger docket** (Michigan Court of Claims 25-000045-MM / 25-000186-MZ, consolidated 26-000013-mz) for admissions. Named as an "optional low-cost operator step"; only the Dec-4-2025 consolidation order was ever read. | `analysis/FRESHNESS-2026-07-29.md:27-29` | partially-run |

## J. Record integrity

| id | lead | source | status |
|---|---|---|---|
| J-01 | `DEAD_ENDS.md`'s Campaign XVIII maintenance note ("source deleted; survives only as orphaned `.pyc`; do NOT backfill its run counts") is **stale**: all 18 sources are present on `master` and no `.pyc` remains. The program is now auditable, so its run counts can be *re-derived by execution* instead of being excluded from the multiple-comparisons denominator. | `research/DEAD_ENDS.md:255-264`; `analysis/campaign18_skip/*.py` | declared-closed-but-thin |

---

## Reading of the register as a whole

Three clusters carry almost all the value, and they are the same three the program keeps
naming and then not finishing:

1. **The artifact layer (A).** The program itself says a *transcription discrepancy* is one of
   only three inputs that can reopen the cryptanalysis — and there are four half-finished
   transcription instruments sitting on disk (a stage-2 independent image read, 450 unadjudicated
   O/A/AE calls, 19 flagged separator lines, an un-run haplography audit). A-01 and A-03 together
   are cheap and would either produce that input or retire the doubt with a recorded verdict.
2. **The keystream-entropy layer (B).** Round 8 turned "OTP" from an inference into a measurement,
   but its own residue is large: 8 of 10 generators of the full-32 sweep, offset ≠ 0, and the
   entire *cryptographic* keystream family (hash-chain / HMAC-DRBG / AES-CTR / RC4). A 2013-14
   author who used `hashlib` rather than `rand()` is not covered by anything on file.
3. **The un-run proposal backlog (D, E, F).** `campaign14/REDTEAM-PROPOSALS.md` is the single
   richest un-mined document in the repo: of its 17 proposals, at least 8 have no artifact
   anywhere on disk, and several are explicitly labelled "instant" or "minutes of compute".
