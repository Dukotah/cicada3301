# A2 — campaign-era artifact / transcription / OSINT partition — full notes (2026-11-12)

Scope read: analysis/{stones, osint, pp49_51, attribution, independent-read, stylometry(skim), armada_osint, stego,
transcription, vision(skim), retranscribe, anend_hunt, geometry(json only)}, DEEPWEB-HASH-OSINT.md, OSINT-SWEEP-2026-07-27.md,
handoff/{PARKED.md, PARKED-SWEEPS.md, capsule/RECOVERY-560.13.md, FOR-FUTURE-SOLVERS (outline), SOLVER-STRATEGY (outline)},
data/, dataset/. Cross-checked against LEDGER.json (309 rows), PICKUP-HERE, MEASURED-CEILING, round18/L5, round19/T1-T3/C1,
round43/F2/F5/F6/X0. Repo untouched. Scratch scripts: scratchpad/payload_probe.py (+ inline snippets).

All paths below are relative to liber-primus unless noted.

---------------------------------------------------------------------------------------------------
## FINDINGS (ranked)

### F1 [UNDISCHARGED + LOGIC-GAP] The T2 OutGuess blob was only ever tested as a pad by a rigid English-only decoder
- What: T2 = the 7,524-byte, entropy-7.978 blob (`extracts/T2.bin` = rtkd `lp_outguessed/04.txt`; OutGuess seed 38370)
  hidden in the Jan-2014 Liber Primus page ("red B section", LiberPrimusPage6.jpg).
- Only pad test: `analysis/armada_osint/t2_keytest.py:1-60` — bytes mod 29 (+rev), offsets, additive/Beaufort/Atbash through
  `ciphers.apply_stream_to_indices` = RIGID alignment, `score_norm` English quadgrams, fixed bar -5.2. Doctrine sec.4 item 3:
  rigid scores the CORRECT key at -6.835 under the filter. `t3_keytest.py:65` (3,368 B folly-class blob) is the same rigid shape,
  but folly later got skip-aware coverage (R12-A1; R17-P0 dense scan lists `tmp_folly`, planted-offset survival 0.75). T2 never did.
- Sibling pads were re-run under repaired instruments (CicadaOS pads: R12-A1 skip-aware, R17-P0 dense, R28-L1 pair relation,
  R40-B3 panel-R36 at 0.782% offsets — MEASURED-CEILING.md:66). T2 is in none of them (grep of round12/A1, round17,
  round28/L1, round40 for T2/7524/outguess: zero hits). R17-P3 "Cicada's own published bytes" = PGP blobs/hash blocks/onion
  addresses, not T2 (round17/PREREG.md:66).
- Tracking: LEDGER `B-09` status `open`, hypothesis literally "OSINT residue — T2/T3 blobs, items 6-9", coverage None.
  R30-B1/B2 + R35-B2 treated T2 as CIPHERTEXT (symmetric battery, XOR crosses) — never as a keystream under beam_v3.
- New since: round43/F5-stored/wayback-log.md:39 recovered the carrier from Wayback with the payload INTACT and
  byte-identical to `og_out/lp_page_04_3a8f1a3f_kNONE.bin` — provenance of T2 is now strong, but F5a did not connect it to B-09.
- Unresolved prior question nobody asked: is T2 a REAL embedded payload or an OutGuess false positive on a non-carrier
  (the explanation the repo accepts for the three 58,152-byte LP2-page blobs)? No validity control exists for either.
  If T2 is a false positive the pad test is moot; if real, it is the only unexplained Cicada-authored random blob shipped
  inside the book itself (R4-grade prior).
- Cost: (a) T2 as a byte->rune pad via the R40-B3 harness verbatim: 7,524 offsets x reductions x signs x 3 relations,
  anchored at the 8-9 section heads -> minutes to ~1 h. (b) false-positive control -> see F2. Needs T2.bin (gitignored;
  re-derivable from the Wayback capture named in wayback-log.md:39).

### F2 [UNDISCHARGED] STEGO-VERDICT's "decisive next experiment" on LP2 pages 0/4/26 was never run; B-10 is mis-discharged
- `analysis/stego/STEGO-VERDICT.md:54-73, 83-96`: 3 of 33 sampled LP2 pages (onion7 0, 4, 26) yield 58,152-byte
  entropy-7.997 OutGuess output with a shared 1,417-byte prefix (pages 4 & 26 share 2,004 B); verdict "closed pending the
  Linux control run": (1) `outguess -r` on a blank control JPEG through the same pipeline, (2) passphrase re-extraction.
- LEDGER `B-10` = `superseded` by `R29-L1-ONION-STEGO`; the X1/R32 note records a TOOL mismatch (0.2 vs 0.4) but not the
  OBJECT mismatch: R29-L1 attacked onion1/2/3 images with a key dictionary; it never touched LP2 pages 0/4/26 nor ran the
  blank control. `handoff/PARKED.md:664` (G-02 row) already says the blocker "has evaporated". ARMADA-20 lane #21 ran OutGuess
  0.4 on the LP2 pages (ARMADA-20-FINDINGS.md:79) but there is no control/prefix adjudication on record.
- Why it matters: it is the only stego residue on the unsolved pages themselves, and the "mundane" explanation has an
  untested hole: if identical blank margins give an identical early path, why do 30 pages fail the validity check and exactly
  three pass with capacity-length output? Pages 0 and 26 are the first page of section 1 and the last page of section 5.
- Cost: 1-2 h on Linux (R18-L1 gives the gs -> ImageMagick q92 recipe; needs data/relikd images + the three blobs).
  Same experiment settles T2's real-vs-artifact status (F1).

### F3 [LOGIC-GAP] "The keystream is continuous across the whole book (no boundary reset)" is a non sequitur
- `analysis/STRUCTURE-FINDINGS.md:17-35`; propagated to `dataset/build_dataset.py:108` /
  `dataset/liber_primus.json: statistical_profile.keystream`.
- Evidence offered: 0 doublets at 54 page joins. Under NO filter at joins P(0) = (28/29)^54 = 0.150; under the filter 0.70.
  Likelihood ratio 4.6 — weak. More fundamentally the anti-repeat rule compares adjacent CIPHERTEXT runes: suppression across
  a join shows the filter remembers the previous output; it carries no information about whether the KEY restarts.
- Consequence: this is the origin of the offset-0 / one-continuous-stream assumption in every decoder since Campaign IV.
  R33-I2 lists resets as unrepresented and R44-R1 now targets them — but the old claim is not marked superseded.
- Section inventory (cleartext, from `data/krisyotam_runes.txt` `$` marks; my count): 8 unsolved sections of
  729 / 1145 / 1738 / 1894 / 1021 / 1433 / 1680 / 3316 runes (segments 0-2, 3-7, 8-15@9, 15@9-22, 23-26, 27-32, 33-39, 40-54).
  relikd's chunk files (data/fetch_sources.py:21-22) give NINE (…p40-53, p54-55); an R43 blind agent counts 18 `&`/`$` units.
  LP1 changed key per titled section. R44 CAMPAIGN-PLAN R1 says "per-page/per-line"; X0 item 4 says "section/page" — the
  reset unit should be pinned (and the lineage disagreement resolved against the images) before R1 runs.
- Cost: zero to fix the docs/plan; resolving the 8-vs-9 section question = look at image 54 (drop cap / red title?).

### F4 [CONTRADICTION / LOGIC-GAP] The DJU-BEI repeat is still adjudicated "chance, P≈13%" — that number ignores word alignment
- `analysis/ARMADA-20-FINDINGS.md:32,81` ("chance (Poisson P≈13%) — not a same-key crib"); no ledger row (X0 confirms:
  round43/X0-firewall/ADJUDICATION.md:27,72). R43-F1 blind agents re-found it (hypothesis_lists.json:8,38,307,355).
- My recomputation (lpdata loader): it is the ONLY repeated 6-gram (expected 0.141) AND the only repeated word-bigram among
  2,928 words; both copies are two whole 3-rune words. Expected number of repeated whole-word pairs of total length >= 6 under
  uniform runes with the real word structure: 3.7e-5. Conservative variant (a chance 6-gram repeat whose boundary pattern
  merely coincides): ~0.141 x 0.05 = 7e-3. Post hoc either way, but 2-4 orders below "13%".
- Locations: seg 27 pos 28-33 (first page of section 6, directly after its first sentence) and seg 54 pos 70-75 = the LAST
  two words of the entire unsolved text (then `.&$`, then AN END). Global distance 6395 = 5 x 1279. No common offset from
  page/line/sentence starts (28 vs 70; 8 vs 2; 9 vs 293). Delta-stream has no repeated 6-gram.
- Status: tracked as a lead (R44-R1) — the finding here is the uncorrected "chance" verdict + the unrecorded significance.

### F5 [CONTRADICTION] `dataset/liber_primus.json` (the advertised canonical machine-readable dataset) is wrong for pages 50-56
- `dataset/build_dataset.py:44-60`: maps segment i -> `{i}.jpg` and stamps every page `"status": "unsolved"`.
  True map (round19/T2/RESULTS.md:59, T2/linemap.py): images 0-49 identity; image 50 is RUNELESS (payload table only);
  segments 50-54 = images 51-55; segments 55/56 (AN END / PARABLE) = images 56/57.
- Effects: 7 pages carry another page's image hash/size; AN END and PARABLE are labelled unsolved; meta says "0-55 unsolved"
  (PROBLEM.json: 0-54); `ruled_out` uses the retired foreclosure vocabulary; `open_threads` and `keystream: continuous…` stale.
- Not tracked anywhere (grep for dataset corrections: none). Cost 30 min. Matters for outside solvers doing image work.

### F6 [CONTRADICTION] Stale tracking that still tells a reader an item is open/closed when it is not
- `PROBLEM.json` search_space_status.open_or_untested still lists "haplography count-audit (A-03)" and "generator-fingerprint
  suite: by HAND? (D-01)". Ledger: A-03 negative (K_bound 26 vs 93), A-01 measured (indel <= 1, round19/T2), D-01 run (R17).
- LEDGER `A-02` still `partially-run`, no notes; round19/T1/RESULTS.md:16 adjudicated 450/450 (all agree with canon).
- `handoff/PARKED.md:656-674` "Not parked — merely unfinished": C-02, D-01, E-01, E-02, F-01, G-01, H-03, A-01/02/05 all
  listed as never run; all since run (R16-R19). Only G-02 (F2 above) and H-01 remain. P-8 (lines 435-470) "never run" has
  no banner although A-03/A-01 discharge it.
- `analysis/stego/STEGO-VERDICT.md:42`: red/black rune colour = "a solver-tool annotation … originals are black-on-white".
  False: `armada_osint/t1_chroma/README.md`, `armada_osint/redrune/FINDINGS.md` (genuine saturated red in the SHA-verified
  originals; 187 red runes on 14 pages). No superseded marker; this false premise kept colour out of the first stego sweep.
- `analysis/retranscribe/FINDINGS.md:30-36` still says buckets A/B are on "solved pages" (they are canon segments 18-39;
  corrected only inside round19/T2/RESULTS.md:245).
- `analysis/attribution/TECHNIQUE-FINGERPRINT-2026-07-29.md:21` "human calligrapher" (R17: machine) — no marker.
- `analysis/pp49_51/blake_closure/FINDINGS.txt` "internal preimage surface COMPLETE" — see F7.

### F7 [LOGIC-GAP, low prior] AN-END hash: the algorithm axis is not complete and "unreachable by construction" is inferred
- Covered digests: SHA-2, SHA3-512 (FIPS-202 padding), BLAKE2b/2s, SHAKE-256, MD5, SHA-1, RIPEMD-160
  (`pp49_51/hash_hunt.py:15-18`, `anend_preimage_broad.py:45-48`), original BLAKE (`blake_closure/`), Whirlpool / Streebog /
  Skein (`anend_preimage_3new.py`), and only sha512/sha3_512/blake2b on the representation axis (`anend_hunt/repr_hashscan.py:30-34`).
- Never tested: Keccak-512 with the ORIGINAL padding (what "SHA-3" meant in Jan 2014; FIPS 202 is Aug 2015), Groestl-512,
  JH-512 (the other SHA-3 finalists). Whirlpool is skipped for inputs > 64 KB (`anend_preimage_3new.py:156`, "run separately";
  no record that it was), so the page JPEGs were never Whirlpool-hashed.
- `anend_hunt/FINDINGS.md:20-33`: "address gated behind LP2 0-54" is an analogy to the 2014 chain grammar, not a measurement.
- Cost ~1 h pure Python over the existing candidate set. Completeness ritual (doctrine Q2), honestly labelled.

---------------------------------------------------------------------------------------------------
## POINTED QUESTIONS

### Q1 Transcription
- Lineage: every transcription descends from rtkd/iddqd 2017; krisyotam = relikd = rtkd over 13,136 runes
  (transcription/TRANSCRIPTION-VERDICT.md:16-34). Unanimity is not independence.
- Campaign V classifier (stones/CAMPAIGN-V-FINDINGS.md:21-34): 99.2% CV but trained on canon labels (circular; admitted in
  independent-read/FINDINGS.md:16-20). Covers 10,774 "clean" glyphs.
- Label-free clustering (independent-read): ARI 0.745; only fragile family O/A/AE = 10.7% of runes.
- R9 template read (retranscribe): 96.93% on 5,207 glyphs, 232/604 lines.
- State of the art (outside my partition, read for the answer): round19/T1 per-glyph reader 95.56% on the LP2 face,
  450/450 O/A/AE loci agree with canon; round19/T2 forced alignment: 0.9973 per-slot agreement over 13,121/13,136 slots on
  604/604 lines, control 1.0000 on the 180 decryption-proven runes, indel bound <= 1 insertion and <= 1 deletion (95%),
  35 slot disagreements all segmentation; 15 illuminated initials never machine-adjudicated (they are in segments 18-39).
  T3: doublet argument survives ~500-700 random wrong runes; full-book correct-key recovery fails near 450 wrong runes
  (~3.5%) — margin "NARROW"; decoder tolerance to insertions/deletions NOT measured (round19/T3/RESULTS.md:472) but T2 bounds
  indels at <= 1.
- Residual: identity error point estimate 0; LP2-typeface only; power lowest exactly on confusable pairs (forced alignment
  takes identity from canon). A 1-3% substitution rate would not defeat the beam; nobody measured the 24-rune head screen
  against one wrong rune in C[:24] (page 0 line 1 was eye-checked: transcription verdict line 40-42).
- Non-rune tokens: all explained in round43/F2-inventory/token-channels.md:25-36 (`&` x18 section end, `$` x9 chapter end,
  `§` end of book, digits 1-5 = list labels on segments 36-38, `7` inline on segment 10). Segment/image map: see F5.
- Line-initial rune chi2(28) = 81.4 over 594 lines (my recompute; repo 78.66) is layout (wide glyphs wrap), measured in R18-L4.

### Q2 pp49-51 payload
- 256 base-60 tokens (80 on image 49, 104 on 50, 72 on 51) -> 256 bytes, entropy 7.17 (= uniform-random expectation for
  256 samples). canon_256.bin now equals payload_resolved (sha 3b9b07d9…).
- Tried: primality/RSA of the full integer and halves; polyalphabetic key over runes (337,944 configs, rigid); numeric keys;
  4x64 digest structure; XOR vs known streams; 210 hash probes vs AN-END; E-01 RSA under all published moduli incl. the
  measured Crypt::RSA OAEP layout (round19/C1); B-05 PRF seed (re-run under repaired instrument); E-02; H-03; R30 symmetric
  battery; R43-F6 payload x onion blobs.
- My quick probe (scratchpad/payload_probe.py, seconds): no prime among 128/64/32/16-byte blocks in either endianness
  (8-byte: 2 of 64 vs 1.44 expected; 4-byte: 6 of 128 vs 5.8); per-page chunks composite; both 128-byte halves have small
  factors (not RSA-1024 moduli); v2-onion addresses derived from the halves match no known Cicada onion. NULL.
- Not covered (already on rows): cells 186/210/211 unsegmented; unpublished moduli; raw RSA/OAEP under unknown keys.

### Q3 AN-END hash — see F7. Community state per anend_hunt/FINDINGS.md:83-93 (hashcat repo 0 matches 2025-10-29).

### Q4 PARKED.md / PARKED-SWEEPS.md, item by item
- P-1 per-rune vision: superseded banner present (A-01/T2-INDEL). OK.
- P-2 / P-12 seed sweeps: R27 pair lane complete; exact lane now 52.05% (R42-S1). Tracked.
- P-3 DATA/560.13 + truncated `_560.00`: re-run same day (R12-A1), dense R17-P0 (planted-offset survival 0.542 on 560.13
  per round17/P0_dense/RESULTS.md:65, English-only), R28-L1, R40-B3 at 0.782% offsets under panel-R36. Tracked as partial
  (MEASURED-CEILING.md:66).
- P-4 PHP mt_rand: tracked (R38-S2-PHP-SANDBOX never-run; R44 deferral).
- P-5 / P-6 AN-END: passive only (see F7 for the residual).
- P-7 six contested payload bytes: resolved (R18-L5, R19-C1, promoted R34-P1).
- P-8 haplography: discharged by A-03 + A-01; PARKED text and PROBLEM.json stale (F6).
- P-9 ornament bands: ledger P-9 / A-06 measured (109/109 bands); not_covered = colour/chroma, non-English registers. Tracked.
- P-10 wider seed spaces: still parked with its power ceiling. P-11 attribution: parked behind the ethical wall. Fine.
- PARKED-SWEEPS #1 (S2 44.14%): advanced to 52.05%; the 35563892 flag discrepancy is resolved as the known noise-crosser.
  #2 (R28-L4 queue): ledger never-run. #3 (R28-L3): ledger row now exists, `inconclusive` (stage-B rows absent). Tracked.
- "Not parked — merely unfinished" table: stale (F6); G-02 is the one real leftover (F2); H-01 is ledger never-run.

---------------------------------------------------------------------------------------------------
## CHECKED AND CLEAN
- OSINT loose ends (OSINT-SWEEP items 6-9, cookies, whitespace): all on ledger rows H-01 never-run, H-02 partial, H-03 negative, B-09 open.
- Red-rune selection (redrune/): 187 red runes on 14 pages = section-opening words; R44-P1 covers the full channel.
- CicadaOS pads incl. the truncated `_560.00`: tracked with coverage fractions.
- Committed key corpora data/keys/**: 96 files, no HTML/404 captures (the 10 corrupt R35 texts are elsewhere and tracked).
- Stylometry / attribution: no key-material lead; nothing bearing on the cipher beyond the stale "by hand" line.
- Foundation statistics reproduced independently (86 doublets, hash 023312…).

## PREMISES THIS ERA NEVER TESTED
1. That an OutGuess extraction with a "valid" header is a payload (T2) or an artifact (LP2 pages 0/4/26) — no validity control either way.
2. That doublet suppression across a boundary implies key continuity (it shows only filter memory).
3. That the page is the cryptographic unit — the transcription's own `$`/`&` marks and red titles define 8-9 sections, and LP1 re-keyed per section.
4. That word boundaries and titles carry no cryptanalytic information (the one repeat was scored position-free; red titles are cribs of known shape, e.g. section 1 title = 8 + 5 runes).
5. That the AN-END page's address must be inside LP2 0-54 (chain-grammar analogy), and that "SHA-3" in 2014 means FIPS-202 padding.
