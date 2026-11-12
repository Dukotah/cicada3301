# Fork G — fresh-eyes audit of Rounds 25–30 (+ the missing Round 31) — full notes

Paths relative to `liber-primus/` unless noted. "canonical" = the hash-verified 12,956-rune
krisyotam stream (55 pages). All checks below were run read-only on 2026-11-12.

## 0. Round 31
No `round31/` folder, no ledger row, no doc, no nav-doc entry: `analysis/README.md` goes round30 (2026-09-28) -> round32
(2026-10-28). Git history in this clone is shallow (50 commits, oldest 2026-10-30), so the commit trail cannot show it.
The only traces are a folder OUTSIDE the repo: `._round31_stale_backup/` in the owner's home directory
(`analysis/round36/AUDIT-inhibitors.md:122` "Stale folder ... Not in this repo ... Owner deletes"; `:164`), and
`analysis/round35/P1-restore-r19-panel/RESULTS.md:15`, which names that same folder as a place the LOST ORIGINAL WELSH
CORPUS might still be ("S2 stays parked unless the original Welsh file is found (another checkout/backup, e.g.
._round31_stale_backup in the home dir ...)"). ("R31" in the O4 matrix is a *reading id*, not Round 31.)
=> Round 31 was either run outside the repo and abandoned, or the number was skipped; nobody recorded which.
=> The R36 audit recommends DELETING the folder; R35-P1 says it may hold the one artefact (Welsh corpus, panel sha
   14a23d36) that would make 44.14 % of the S2 `exact` sweep reproducible. Nobody inspected it. Owner-only, minutes.

## 1. FINDINGS (ranked)

### F1 [INSTRUMENT-DEFECT] R26-A decoded the Perl/TeX/Py2.7-reducer keystreams against a mid-book paragraph, not the head
- `analysis/round26/A/sweep.py:128-131`: `pages = corpus.parse(); pg = pages[19]` — target = scream314 section 19
  ('23.jpg, 24.jpg - 6.jpg-7.jpg', 333 runes). I matched it to the canonical stream: flat index 1541..1873 =
  canonical page 6 rune 71 (right after an `&` paragraph mark) through the end of page 7.
- `sweep.py:194`: every decode is `HitDecode(C=C_real, K=K, o=0, ...)` — keystream offset 0.
- So the "first-ever scored decodes for Perl rand and TeX RNG; 347 corpus-derived prior-dense seeds fully swept
  (empty)" (`round26/SYNTHESIS.md`, `LEDGER.json` R26-A-GEN-SWEEP-FIRST-FIRE, `MEASURED-CEILING.md:64`) has power ONLY
  under "the generator restarts at the paragraph break p6:71". Under the hypothesis every other generator lane tests
  (stream starts at the book head: R25/R27/R28-L3/L4/R26-C all use `nc.unsolved()[:120]`, later lanes `C[:24]`), its
  power is zero. The row's `not_covered` does not say so; the R26-D red-team returned NO-ERROR-FOUND.
- Root cause: `src/lp/corpus.py` marks a section "solved" when ANY latin block exists; sections 17 (pages 0-2, 729
  runes) and 18 (pages 3-5) are thereby flagged `plaintext`, so "first unsolved page" became section 19.
- Checked not tracked: grep of MEASURED-CEILING/PICKUP-HERE/ELIMINATION-LEDGER/X1 reports for idx19/333 -> nothing.
- Why it matters: Perl 5.14 `rand` and TeX LCGs are the two generators R18-L1's toolchain prior PROMOTED; their
  prior-dense front has effectively not been tested. Cost: minutes-1 h (347+400 seeds x 12 axes x 2 relations on
  C[:120] through beam_v3/panel-R36; plant through the same glue).
- Other users of `corpus.parse()` as a target (for the coordinator): `round26/B`, `round38/C2-never-cells/cells/run_cells.py:186`,
  `round10/L3-road/t6_source_control.py`, `recon/lp1h_norepeat`, `r6_sieve_windows.py`.

### F2 [LOGIC-GAP + stale tracking] R26-B keytext coverage is mislabelled and ~10x thinner than tracked
- `analysis/round26/B/sweep.py:47-55` uses the same parser. Its "9 unsolved rune-pages 19,20,22,23,25,26,27,28,29" are
  scream314 SECTION indices. Mapped to canonical: 19 = p6[71:]-p7 (333); 20 = p8-p14 (1729); 22 = p15[9:]-p22 (1894);
  23 = p23-p26 (1021; NOT rune-identical to canonical — transcription variant); 25 = p27-p32; 26 = p33[:91];
  27 = p33[91:]-p39[:119]; 28 = p39[119:240] (121); 29 = p40-p52 (3008).
- NEVER in the target set (parser artefact, not in `not_covered`): canonical pages 0-5 (1,470 runes — the head of the
  book), p6[:71], p15[:9], pages 53-54 (308). The tracked remainder ("pages 20/22/25/27/29", `PICKUP-HERE.md:222`,
  `MEASURED-CEILING.md:65`, ledger reopens_if) is therefore wrong: a reader takes "pages 19, 26, 28 complete" as LP2
  pages 19/26/28.
- Completed = sections 19, 26, 28 = 545 runes (4.2 % of the stream) + 86 % of section 23.
- Offsets: `usable*k//4, k=0..3` on the RAW file (`sk.eng_to_idx(f.read())`): offset 0 is Gutenberg/HTML boilerplate,
  not the start of the text; the other three are arbitrary. ~2e-5 of the offset axis; the control (`control.py`) gives
  the decoder the true offset, so "power 1.00" says nothing about the offset axis.
- Texts: `analysis/round12/C2/fetch.sh` — 23 Gutenberg + 10 `url` fetches. 4 are globalgrey (the "4 truncated
  5,336-rune texts" in RESULTS §2 are four copies of one 404 page — identical length was the tell); 6 are
  archive.org `/stream/..._djvu.txt` HTML wrappers. R26-B's global best (5.470) is `theologia_germanica` (an HTML capture).
- None of the texts 3301 itself used or cited (Self-Reliance, Liber AL, Mabinogion, Agrippa, Blake MHH, King Arthur,
  the 2012-14 book-code texts) is in R26-B. Self-Reliance appears only as the control PLAINTEXT.
- R42-C1 (the "discharge") is rigid: `analysis/round42/C1-keytexts/run_c1.py:52-56` `vig_running` has no skip axis
  (R43-X1 REPORT:48 already says so) and compares a rigid pmax to the `free` beam bar 17.42. Under the project's own
  key-skip model a correct running key decodes ~36 runes then desyncs.
- `MEASURED-CEILING.md:65` itself says "the earlier keytext nulls were unsound and are retracted". So the citable
  skip-aware running-key evidence in the whole repo is: 23 real texts x 4 arbitrary offsets x 545 mid-book runes.
- Yet `analysis/round43/X0-firewall/ADJUDICATION.md:32` stamps "running-key from released texts (Self-Reliance /
  Blake / own plaintext) + skip" as CITED (X1 kept the stamp, only fixed the wording).
- Cost to discharge properly: hours. A dense all-offset, skip-tolerant head screen (pf_v4-style, 24-32 runes) over
  each page head AND each `&`/`$` section head (17 `&`, 9 `$` marks in `data/krisyotam_runes.txt`), both signs, for the
  3301-cited texts first, then the 23; plants through the same glue.

### F3 [LOGIC-GAP / mis-prioritised] `grb5_rej` is Python >=3.2's randrange/randint/choice stream, queued as a "Py2.7 ritual"
- `analysis/round19/G3/RESULTS.md:118-122` (Py3 `randrange`/`choice`/`shuffle` = `_randbelow` = getrandbits(5) with
  rejection) and `:229-231` ("int seed: py2 grb5_rej == py3 grb5_rej : True").
- `analysis/round27/PREREG.md:125-132` and `analysis/round28/L4/QUEUE.md` call grb5_mod/grb5_rej/shuffle29 "Py2.7
  spellings ... no Q2 fact beyond 'same interpreter, different idiom' — completeness rituals", queue them last, and
  only at offsets {1,3,5,7,13} x `pair`. `analysis/round28/L4/queued_cells.json`: NO offset-0 cell for any grb5 reducer.
- Coverage under a skip-aware decoder: R21-L3 216,000-288,000 words = 0.005-0.007 % (keyskip1, R19 panel) + semantic
  seeds (R26-A/C). The only full-2^32 pass is Round 8's rigid `sweep.c` (R19-G3-CORRECTION: power unmeasured).
- Python 3.2 (2011-02) / 3.3 (2012-09) both predate the Jan-2014 release. `random.seed(int(time.time()))` +
  `random.choice(runes)` is as idiomatic as it gets. The unix-time band 2012-01..2014-01 (~6.3e7 seeds) x {exact,pair}
  is < 1 h on a grind28-class engine; the full two cells ~1-2 days.
- Tracked only as "Py2.7 other reducers ... under 0.1 %" (`MEASURED-CEILING.md` §2a/§3). The prior label is the defect.

### F4 [UNEXAMINED-INPUT] OutGuess's second-message / error-correcting channel was never tried
- OutGuess 0.2 embeds two messages: `-k key1 -d f1 -E -K key2 -D f2`; the second is Golay-coded and (per the man
  page) is retrieved with `-k key2 -e -r`. 
- `analysis/round29/L1-onion3-crack/sweep_fast.py:42`: `[OUTGUESS, "-k", key, "-r", img, out]` — no `-e`. An ECC
  message extracted without `-e` is raw coded bits -> classified ARTIFACT even when the key is right.
- grep over all tracked .py/.sh/.md (excluding archive/) for outguess with `-e`/`-K`/`-D`/`-x`: zero hits.
- Run: keyless + the 4,013-key dictionary with `-e`, on onion1/2/3, 1033, the Jan-2014 carriers, the 2012/2013
  carriers. Control: embed a second message in a test JPEG and prove the classifier flags it. Minutes.
- Caveat: `outguess` is not installed in this container; verify the `-e` retrieval semantics on the binary first.

### F5 [UNDISCHARGED, untracked] R43-F5a's "new capture route" arrived and no image battery was re-run
- `PROBLEM.json` eliminated_families: stego "reopens only with a new capture route"; R29-L1 reopens_if "a canonical
  ... capture with a different embedding".
- `analysis/round43/F5-stored/RESULTS-wayback.md:20-27,66-73`: masters of 56.jpg (AN END, the page carrying the
  deep-web hash) and 57.jpg recovered for the first time ("the corpus is currently 56/58"); Jan-2014 carriers p5/p6
  recovered; follow-ons listed: import 56/57, fetch the other 13 Jan-2014 carriers, X1 spot-check.
- grep for `56_2022|57_2022|56/58|other 13|jan14_p5` outside `F5-stored/`: zero hits. Not in round43/SYNTHESIS §4,
  round44/CAMPAIGN-PLAN.md, PICKUP-HERE, LEDGER.
- Never done: any stego/forensic pass on the 56/57 masters (keyless + keyed OutGuess, steghide, appended bytes,
  DQT/ICC fingerprint vs the other 56, LSB/chroma as R29-L3); R29-L1's keyed dictionary on ANY Jan-2014 LP carrier
  (its scope was onion1/2/3 only, FINDINGS §c). R30-A1/A2 also stop at page 53 (unsolved page 54 omitted).
- Cost: minutes-1 h after a Wayback refetch (`fetched/` is gitignored, .gitignore:469).

### F6 [LOGIC-GAP] T2 ("one of the three genuinely random blobs") is almost certainly an OutGuess no-payload artefact
- T2 = keyless OutGuess output of the 2014 `04.jpg`/`2.jpg`: `analysis/OSINT-SWEEP-2026-07-27.md:34,88` ("seed 38370,
  7,524-byte blob"); the community source the repo ships says "Outguessing the image yields 7,5kB garbage output"
  (`data/scream314_lp.md:887`).
- Every REAL 3301 payload in the repo has a small header seed: onion1 163, onion2 115, onion3 94, 1033.jpg 102
  (`round29/L1-onion3-crack/FINDINGS.md` §a,d). Wrong-key artefacts: 42513, 3456 (same file, "wrong-key-artifact
  trap"). OutGuess picks its seed by a bounded search from 0 (default iteration window 256, to be confirmed on the
  binary), so a real default-settings payload cannot carry seed 38370; a non-carrier read keyless yields a uniform
  16-bit seed.
- Yet T2 is carried as a live ciphertext candidate: `round29/SYNTHESIS.md` "three genuinely-random blobs";
  R30-B1 (37 keys x 7 cipher families), R35-B2, `round43/F6-objects/RESULTS.md:102` "still-open true opaque".
  R43-F5a even logs it as "outguess payload INTACT (seed 38370, 7524 B)".
- Zero-compute discharge: tabulate header seeds of every known carrier; if all real ones are < 256, strike T2 and
  the three 58,152-byte outputs on the same ground. Removes a red herring; does not move the solve.

### F7 [SHARED-PREMISE] The soft filter's coin is always exogenous to the keystream
- Every plant: `campaign18_skip/skipdecode.py:68,75` and `round26/B/control.py:71-78` draw the 0.83 suppression
  decision from a separate `random.Random(3301)`. `round33/I2-construction-axis/RESULTS.md:8-16` varies skip_by_k and
  resets, never the coin source. grep for "same stream / same generator / coin draw" in R18-R43 docs: no modelling.
- For a seeded-PRNG script (the hypothesis behind every 2^32 sweep in R25-R28 and later) softness needs a randomness
  source; the natural single-generator implementation draws the coin from the SAME stream. Then (a) a suppressed
  doublet costs coin+redraw = 2 draws (= `pair`, fine), but (b) each of the 86 SURVIVING doublets also cost one coin
  draw: a deterministic +1 key advance at a position that is visible in the ciphertext.
- Head screens are unaffected (first visible doublets are at flat index 122 and 207; C[:120] has none) — I checked.
  But every L=240 confirmation (R27 ORACLE-*.md "collapses when the window doubles = noise"; hitfn20 at L=240) and
  every page-length decode crosses them, and `pair`/`exact` desync exactly there. For the three S1 crossers the
  verdict is safe on magnitude (7.4-7.7 vs plants 17.9 at L=120), but the rule itself is unsound in general.
- Positive side: under this construction the 86 doublet sites are KNOWN-POSITION key-advance events — free anchors
  no decoder uses. Cost: one new relation in beam_v3 ("+1 at observed doublets", composable with keyskip2); hours.

### F8 [UNDISCHARGED] R28-L4 queue — status per cell (answer to pointed Q3)
- Cells 1-8 PHP mt_rand (2 twists x scale/mod x pair/exact, 2^32 each): the grind28 queue NEVER fired (chainer died
  with the 2026-09-15/16 host reboot; row corrected to never-run 2026-10-05). Partly covered later by a different
  instrument (pf_v4 + beam_v3): prior-dense 48,036 seeds/cell + ~1 % uniform tier (R32-B2, R34-B1, R36-B2); ~99 % open
  ("S2 PHP retry" deferred R38->R44).
- Cells 9-10 glibc random()%29 gen=0: only R32-B3's 48,036 prior-dense seeds (1.1e-5).
- Cells 11-25 S3 (grb5_mod/grb5_rej/shuffle29 x offsets {1,3,5,7,13} x pair): zero coverage; see F3.
- Gates for all 25 cells exist and passed (1600/1600 vectors, 25/25 plants) but the engine binary/gates are
  gitignored (.gitignore:359-368) and were built on the R19 nine-register panel that R35 declared unrebuildable.

### F9 [UNDISCHARGED, tail] R28-L3 is "inconclusive" only on a clone-scoped absence that was never re-checked
- `round28/L3/RESULTS.md` §7 (written by R32-B3): `candidates28.jsonl` + `dictionary.jsonl` "absent from this
  checkout ... they lived on the originating machine". R41-X1B later proved four such "absent" claims were artefacts
  of running in a fresh clone. grep of round36-44 docs: R28-L3 never re-checked on the canonical tree. Minutes for
  the owner; upgrades the row to a bounded negative with no re-sweep.

### F10 [CONTRADICTION, tail]
- R42-C1 / PICKUP "10 of 33 are globalgrey 404 captures" vs `round12/C2/fetch.sh`: 4 globalgrey + 6 archive.org
  stream pages (HTML-wrapped full OCR text; R26-B used them at full length). The 6 need unwrapping, not re-fetching.
- `LEDGER.json` R27-CPORT-MT32-FULLSWEEP `result`/`coverage` still narrate "S2 IN-FLIGHT"; R25 row `not_covered`
  still says ">99.49 % of the tail is unswept" with no `superseded_by` although R27-S1 scored all 2^32 under `pair`.
- R26-B ledger row + MEASURED-CEILING:65 still say "33 texts" and "pages 19, 26, 28".
- R30-A1/A2 `not_covered` lumps unsolved page 54 with solved 55-57 ("pp54-57 not clustered").
- R30-C1's reopen (the 402-gated "Art of Liber Primus" wiki page; true reverse-image search) never run — attribution only.

## 2. Pointed questions — direct answers
1. R26 keytexts: 33 files from R12-C2 (23 real Gutenberg texts: Plotinus x2, Apuleius, Epictetus, Seneca, Plato x2,
   Swedenborg x3, Boehme, a Kempis, Law, Inge, Underhill x2, W. James, Augustine, Aquinas, Bruno, Ginsburg, Enoch
   (Charles), Frazer; 6 HTML-wrapped archive.org texts; 4 globalgrey 404s) x offsets {0,1/4,1/2,3/4} (8 on sections
   19-20) x sign -1 x {keyskip1, keyskip2} x scream314 sections; completed sections 19/26/28 + 86 % of 23; 1,562
   decodes. Uncovered: everything in F2. Self-keying (LP's own plaintext / ciphertext / LP1 as running key under the
   skip-aware decoder): NOT in R26. Elsewhere: F-01 / R40-C1-R47 (LP2 as pad over OTHER objects, 500-rune windows) and
   R22-C X3 (solved plaintext as running key) — different lanes. 3301-cited texts: none in R26-B; editions therefore n/a
   (R29-L1 used tokens of Self-Reliance/Mabinogion/Agrippa/Book of the Law only as stego PASSWORDS).
2. R27: three S1 crossers (35563892 / 348625413 / 86514964; L=120 pmax 7.67 / 7.60 / 7.42 vs bar 7.3835 set at
   N=1e6 for a 4.3e9 sweep) adjudicated by hitfn20 at L=240 (4.96 / 4.53 / 5.78 -> clause-1 fail) + reading the decode;
   all fired LP1_REAL. K4 parity = C engine vs Python reference: 10,971 flags re-scored, max |d| = 0.0. The pair/exact
   confusion: R25's "tail" and R27-S1 are `pair` (skip_by_two); the repo's own pinned filter (`encipher_keyskip`,
   one draw per rejection) is `exact` = S2, which died at 41.7-44.14 % and has since reached 52.05 % on mixed panels;
   for weeks docs said "coverage 1.00 / EXHAUSTED" without "pair-only" (fixed by R32-X1 and the R36 audit banner).
3. R28: L1 (2 pads, strides 16,384 / 331,777, 24,080 rows, negative; off-grid disclosed; R17-P0 dense scan is
   English-only); L2 (payload contested bytes: canon stands; 21.6 M-decode battery negative); L3 (inconclusive, F9);
   L4 (F8); L5 negative. The final SYNTHESIS was never written (INTERIM only).
4. R29/R30: capture routes examined = onion1/2/3 from micheloosterhof/cicada-2014 stage03 (md5-matched), 56 relikd
   pages (byte-identical to onion7), 2012 images for the toolchain split. R43-F5a's masters are a new route and the
   battery was NOT re-run (F5).
5. Carried-forward items: R28's final-closeout checklist items 2-5 (queue, L3 write-up, chainer lock, final
   synthesis) lapsed with the host reboot — 3 was done by R32-B3, 2 is F8, 5 never; R29's human-in-the-loop
   attribution contacts (mruzuki email, Wanner, Oct-2025 Eriksson podcast transcript, Nox Populi DEF CON 26) appear
   in no later doc; R30 live threads 1-2 were discharged (R33-O1, R34-S1, R36-O2, R43-F5a), 3 not.

## 3. Checked & clean
- R25: target canonical head (`runner.py:61-62`), superseded by R27-S1; no claim beyond its checkpoints.
- R26-C: canonical head, 323 seeds x 7 generators x 2 relations, re-decoded by R40-C1 under beam_v3/panel-R36.
- R27-S1: canonical C[:120]; histogram = 2^32; crossers noise by magnitude; unix-time int seeds are inside both the
  S1 space and the S2 cursor (<2.2e9). Py2.7 randrange/randint/choice == random29 (R19-G3) so the idiom is right for 2.7.
- R28-L1/L2/L5: plants through the real path, conditionals disclosed, targets canonical.
- R29-L2/L3/L4, R30-A1/A2/A3/B1/B2/E1: controls real; follow-ups discharged or disclosed.

## 4. Premises this era never tested
1. A seeded keystream starts at rune 0 of page 0 with zero prior draws (all 2^32 sweeps) — or, by accident, at one
   scream314 paragraph break (R26-A/B). No lane tests restarts at the 26 `&`/`$` section marks.
2. The suppression coin is exogenous to the keystream (F7).
3. Stego = first message only (no `-e`/`-K`) (F4).
4. A running key is found by sampling offsets (4 or ~150 per text) rather than scanning all of them.
5. Sign -1 and `int(random()*29)` only, for the one full-space cell.
