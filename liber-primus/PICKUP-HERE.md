# PICKUP-HERE — where the work left off, and what is still open

_Refreshed **2026-10-30** (Round 34 closeout). Read this first, then [`ELIMINATION-LEDGER.md`](ELIMINATION-LEDGER.md)

> ## Round 34 (2026-10-29/30) — CLOSE THE LOOP: shipped. Read `analysis/round34/SYNTHESIS.md` first.
>
> No survivor. **B1** screened the FULL bash 4.2 `$RANDOM` auto-seed orbit (both ABIs, 77.6 M seeds each) with a
> register-aware head prefilter and decoded 162 k survivors with the register-aware beam under an observed null: 0
> flagged (best 7.068 = the Round 32 near-miss seed again, vs 8.12 actual-N bar). PHP prior-dense tier full, uniform
> tier 0.061 % of 2³². **The remaining hole is the head screen:** 37–51 % of true-key heads contain a key skip and
> pass the screen at only 0.19–0.34 (X1) → orbit reach ≈0.65–0.70, not the beam's 0.98. Round 35 I1 = skip-tolerant
> screen. **I1** v3 has an observed Gumbel null (`round34/I1-v3-null/bars_v3.py`; L≥120, keyskip1/2 only).
> **P1 + coordinator:** `canon_256.bin` is now the R19-C1 resolved payload (every re-runnable reader re-fed first,
> none changed; superseded bytes kept); capsule manifest refreshed, verifier CRLF-tolerant (INTACT-FAIL 13 → 2 labelled
> substitutes). **S1 (Vercel sandbox):** fixed grind27/28 compile clean and pass 4/4 resume tests on copies — **S2
> resume is blocked only by the missing Round 19 panel (sha 14a23d36…)**; PHP 5.6 `mt_srand(1); mt_rand()` =
> 1244335972 matches `php_mt.py`; Ghostscript band tightened to **9.05–9.14** (9.04 ships the ICC file but does not
> embed it). **I3:** D5c calibrates at L=120/180/240/400 (recipe 1, `m_NV≈0.055·L`, post-hoc); SEAL_PASS=false.
> **X1:** I2's "0.998 prefilter power" was an artefact of skip-free plants (operative ≈0.66); I1's "not Gumbel" alarm
> was a like-for-like error; Round 33 I2's "earned" relations struck.
>
> **Next:** `analysis/round35/CAMPAIGN-PLAN.md` — skip-tolerant head screen + bash orbit re-screen; restore the Round 19
> panel byte-exact (fetch original corpora) and, if it matches, resume S2 for a stated window on the sandbox;
> pre-registered D5c rule; the R30-B1/B2 T2/folly payload legs.

> ## Round 33 (2026-10-29) — THE REGISTER-AWARE BEAM: shipped. Read `analysis/round33/SYNTHESIS.md` first.
>
> No survivor. The beam now searches all nine registers (`round33/I1-register-aware-beam/beam_v3.py`, panel-max
> design): **EN_NOVOWEL recovery 0.72 → 1.000** with the correct key, no other register loses > 0.012, 1.4–2.3× cost.
> Every stored survivor row of R32-B1 (bash `$RANDOM`) and R32-B2 (PHP `mt_rand`) re-decoded through it: 404,284 rows,
> coverage 1.00 of stored survivors, 0 flagged (best 7.068 vs modelled bar 8.373). **The orbits were never searched
> with a NOVOWEL-aware prefilter (0.47 power) — that is Round 34 B1.** The Round 18 `skip_by_two` doublet prior
> (0.84 %) does not replicate (≈0.60 % for every construction incl. keyskip1) — superseded, relation kept.
> Corrected payload bytes flip nothing in B-04/E-01/E-02 (R17 not re-runnable). Issue #12 separator correction landed
> (two gaps, outside provenance); p27:93 = U; LP1 read-gate failure is image coverage (one 75-rune block), not
> substitution. X1: the Round 32 C-engine patch could never have compiled — fixed, still **unbuilt**; S2 stays
> do-not-resume. SEAL_PASS=false (D5c holds at L=240, fails at L=120).
>
> **Next:** `analysis/round34/CAMPAIGN-PLAN.md` — v3 null of record, NOVOWEL-aware prefilter + the two orbits under
> v3, payload promotion done safely (five more readers + capsule manifest), D5c `m_NV(L)`, and a Linux sandbox for the
> C engine / PHP 5 reference / Ghostscript render kill test.

> ## Round 32 (2026-10-28) — INSTRUMENT & RED-TEAM armada: shipped. Read `analysis/round32/SYNTHESIS.md` first.
>
> Eight lanes, all with passing positive controls, all filed in `LEDGER.json` (181 rows, 0 errors).
> No survivor. What changed is the **instrument**, not the board:
> - **I1** the three-relation decoder already existed (`round19/I1/driftbeam.py`); it now has a measured power
>   envelope — planted `skip_by_two` recovers 1.00 under `advance=2` (legacy relation: 0.30). **Vowel-dropped
>   English is still not recovered by any relation (0.72)** → Round 33 #1.
> - **I2** nine-register panel rebuilt (Welsh/KJV/Mabinogion corpora were missing; `fetch_sources.py --welsh`
>   now restores them). Historical negatives B-04 / R16-KDF / R16-PRNG / R17 re-scored at survivor level: nothing
>   clears the escalate bar — but only English-ranked heads were ever stored, so the sweeps keep an English-only
>   conditional (restated in their rows).
> - **I3** R3 is now a hard validator check (round >= 19, sweep-declaring rows); `threshold_for(n, segment_len=L)`
>   scales with L; null curve refit on 6 points (exponent -0.546 +/- 0.041).
> - **I4** `SEAL_PASS=false` stands; learned gates that look perfect are register detectors. Post-hoc rule D5c clears
>   0.90/0.10 on one L=240 split — unreplicated, NOT adopted.
> - **B1** bash 4.2 `$RANDOM` auto-seed orbit (77.6M x 2 ABIs) prefiltered in full, 192k survivors decoded under
>   keyskip1+2: 0 flagged (prefilter-lossy, power 0.47–0.74). **B2** PHP `mt_rand`, both twists x 2 reductions x
>   2 relations: prior-dense tier fully decoded + 0.97 % uniform sample of 2^32: 0 flagged. Remaining 99.03 %
>   → `R28-L4` queue (~71 h at laptop rate). **B3** R28-L3 filed `inconclusive` (bulk store never reached this
>   machine); glibc `gen=0` prior-dense first-fire: 0 flagged over 48k seeds.
> - **X1** FOUND-ERROR on all seven standing claims (see banner below and `round32/X1-redteam/RESULTS.md`).
>
> **Open for the owner:** (1) `C-CANON-PAYLOAD-3BYTES` — promote `payload_resolved.bin` or restate `not_covered`
> (X1 §3, both written); (2) build + test the patched `grind27.c`/`grind28.c` before resuming S2 (no C toolchain
> here); (3) confirm X1's 8 drafted `not_covered` texts; (4) R30-A1/A2/B1/B2/C1 still carry `not_covered: null`.

> **Round 34 X1 (2026-10-29) red-team corrections** (details and citations: `analysis/round34/X1-redteam/RESULTS.md`):
>
> - **R34 I2's "the real ciphertext head is skip-free" is WRONG.** `U[:40]` (and `U[:120]`) really have zero doublets, but a key skip is *invisible* in the emitted ciphertext (it happens when the candidate rune would equal the previous one). In 600 R32-style plants per cell, 37-51 % of heads contain a skip inside m = 18-24 and that holds even among plants whose cipher head has no doublet. The operative prefilter power of I2's screen is **about 0.66 EN_NOVOWEL / 0.71 EN_MODERN at FPR 1e-3, not 0.998**; R32-B1's 0.47 NOVOWEL is *not* a plant artefact (re-run reproduces 0.555-0.62). B1's reach must be stated from the with-skip column. A skip-tolerant head screen is the open lever.
> - R34 I1's "Q5 fired" compared v3's z-scored `pmax` with R32 I3's raw quadgram exponent (-0.55); z-normalisation adds ~+0.5, predicting ~-0.05 (observed -0.105 / -0.136): a false alarm, not evidence of a non-Gumbel tail. The Gumbel bars hold (conservative) at L <= 240 and are not shown conservative at L = 400.
> - R33 I2's "earned" relations (`keyskipk`, `decode_with_resets`) are **struck**: the doublet prior is non-discriminating, so nothing is earned (completeness ritual, last in queue).
> - Ghostscript render band is now **9.05-9.14** (R34 S1); ~~9.04-9.14~~ was file-in-tree evidence, S1 measured ICC embedded in the jpeg output (9.04 does not embed it). Synthetic page only; O1 is live, not solved.
> - Capsule: the 13 INTACT-FAIL items are settled (`analysis/round34/X1-redteam/manifest_decision.md`): 9 CRLF checkout noise (fix the checker), `runes.canonical` stale by the issue-12 edit, `tests/validate.py` grew by exactly the Round 19 AN-END guard (refresh the manifest), `kjv`/`mabinogion` are Round 32 I2's substitute copies. Payload rename: GO (P1, nothing flipped); `C-CANON-PAYLOAD-3BYTES` stays `open` until the coordinator renames.

> **Round 33 X1 (2026-10-29):** the R32 `grind27.c`/`grind28.c` patch had a syntax error (raw newline in a string literal) - fixed, still UNBUILT; **S2: do not resume until compiled and tested**. Owner chose Option A on `C-CANON-PAYLOAD-3BYTES` (file move pending, coordinator). p27:93 machine-resolved to U (B2). The `0.84 %` skip_by_two doublet prior is superseded (full-length 0.595 % = keyskip1). D5c replicates at L=240, fails at L=120. See `analysis/round33/X1-redteam/RESULTS.md`.
>
> **Round 32 X1 (2026-10-28) corrections applied throughout this file and the other nav docs:** GS bound 9.04-9.14; Py2.7-MT coverage is per-relation; transcription claim LP2-typeface-only with p27:93 still needing a human; seed 35563892 now has an S2-lane (`exact`) re-screen (NOISE at L=240) -- the 'one unresolved flag' on S2 is discharged at the one-seed level. **Before resuming S2, build the patched `P1-engine/grind27.c` (hit-restore on resume) and test it against the parked state.** Coordinator decision still open: `C-CANON-PAYLOAD-3BYTES`.
and query [`LEDGER.json`](LEDGER.json) `coverage`/`not_covered` (never the bare `status`)._

> ## 🛑 NOTHING IS RUNNING. Read this before any block below that says IN-FLIGHT.
>
> Every sweep in this repository was killed by a host reboot on **2026-09-15** and **none has
> been resumed**. Every PID in the tree is dead. Until 2026-10-05 this document and the ledger
> both still described three of them as in-flight, which told anyone arriving that those
> branches were being handled. They are not. They are **parked and available**:
>
> | branch | real state |
> |---|---|
> | **R27 / S1** (Py2.7-MT 2³², `pair`) | **genuinely COMPLETE — NULL.** All 2³² seeds scored once; 3 claim-bar crossers all oracle-adjudicated NOISE-CROSSER. Closed; needs nobody. |
> | **R27 / S2** (same space, `exact`) | **STOPPED at 44.14 %** (1,895,728,884 / 2³² seeds). Resumable. One unresolved flag on seed 35563892 to check first. |
> | **R28 / L4** (25-cell generator queue) | **NEVER FIRED.** Zero authoritative coverage. The chainer that was waiting on S2 died with it. |
> | **R28 / L3** (string-seed amd64 dict) | **sweep FINISHED** (all 11 items, 2,500,207 seeds, best pmax 6.3148, no survivors) but **never written up** — no RESULTS.md, no ledger row. Cheapest open item here. |
>
> Exact coverage numbers, the committed state files that prove them, and the resume route for
> each: **[`handoff/PARKED-SWEEPS.md`](handoff/PARKED-SWEEPS.md)**. Ledger rows
> `R27-CPORT-MT32-FULLSWEEP` and `R28-L4-UNSWEPT-GENERATORS-QUEUE` were moved off `in-flight`
> on 2026-10-05 to `partially-run` and `never-run` respectively; the ledger now carries **no**
> `in-flight` row, because nothing is in flight.
>
> **Why it stopped, stated plainly:** not because the branches were finished or judged
> worthless. The work ran out of machine and out of instrument. S2 wanted ~9 more hours on
> hardware that rebooted; L4 wanted 15–19 days of six-core wall. The lanes that would actually
> move the verdict now need capability this project does not have — see
> [`handoff/PARKED.md`](handoff/PARKED.md), each item with a testable threshold for when you
> are good enough to unpark it, and `AGENTS.md` §8.

> ## ⚡ Rounds 29–30 (2026-09-28): the attack pivoted OFF the ciphertext onto the CONTAINER — one real positive.
>
> After R28, two "active attack" armadas were run (no more ciphertext-only sweeps). **Round 29** (5 lanes,
> `analysis/round29/`): onion-image large-dictionary stego crack (24,078 extractions, **0 hits** — and the
> record was corrected: the onion chain had *never* actually been key-attacked; the "5×5-rune" page is
> onion2 not onion3); opaque-blob two-time-pad cross-XOR (**NULL**, only 3 blobs are truly random —
> 2.jpg-payload, folly, canon_256); rune-107/229 chroma-as-bitstream (**NULL**, constant red ink =
> decoration); **image forensics (POSITIVE)**; OSINT people-hunt (mruzuki = zero-footprint burner, dead end).
> **Round 30** (8 lanes, `analysis/round30/`, each adversarially verified): the big new fact is that
> **the 2014 LP master is a machine-rendered PDF** — its embedded ICC profile is **byte-identical to
> Ghostscript 9.06's Artifex `srgb.icc`** (toolchain narrowed to GS ~~9.04–9.14~~ → 9.05–9.14 (render level, R34-S1: 9.04 ships the e409cef1 srgb.icc file, which was R18-L1's evidence, but its jpeg device does not embed it; 9.05 first does; one synthetic page, gcc-15 build, no pin inside 9.05–9.14) (9.00–9.02 measured non-matching; 9.03 unmeasured; 9.15–9.21 byte-identical but post-date the May-2014 dump); A3 POSITIVE). Everything else
> NULL/consolidation: rune glyphs are a deterministic vector font with no variant channel (A1); no sub-pixel
> positioning channel (A2); the 3 random blobs carry no keyed-symmetric plaintext (B1) and no RSA/OpenPGP
> structure (B2); no attributable artist (C1); the 6 contested pp49-51 bytes resolved from the render →
> **canon_256 unchanged** (E1). **OTP-class verdict UNCHANGED + reinforced.** Ledger 162→**171**, unsound=0,
> validate.py 5/5. See `analysis/round30/SYNTHESIS.md`. Live threads are now all OFF-repo: recover the source
> PDF/PS (would name the `/BaseFont` typeface + expose TJ kerning), pin the exact GS release, close art
> attribution via reverse-image/Wayback. (Committed and pushed since; `validate.py` is now 6/6, not 5/5, and the ledger is at 172.)

> ## ⚡ Round 27: S1 is COMPLETE (first full-space sweep in project history) — NULL. S2 is STOPPED at 44.14 %.
>
> **(Status corrected 2026-10-05. The block below was written while S2 was live and still reads
> that way; S2 died with the 2026-09-15 reboot at 44.14 % coverage and was never resumed.
> Treat every "IN-FLIGHT" / "is sweeping" below as "parked, resumable" —
> [`handoff/PARKED-SWEEPS.md`](handoff/PARKED-SWEEPS.md) §1 has the numbers and the resume route.)**
>
> The R25 Py2.7-MT branch — the only internally-runnable verdict-changer — is being **finished**,
> not sampled, by the bit-exact C port `grind27` (gate **GO**: V1 64/64 vectors |Δ|=0,
> planted-screen margin 12.9, false-reject 0/6; red-team **NO-ERROR-FOUND** on the gate).
>
> **S1 (pair/keyskip2) COMPLETED 2026-09-08: all 2³² = 4,294,967,296 seeds scored exactly once**
> (histogram sums to 2³² exactly). 392,131 flags at 1.31× the Gumbel prediction (K2 pass); three
> claim-bar crossers — 35563892 (7.6707), 348625413 (7.6001), 86514964 (7.4210) — **all
> oracle-adjudicated NOISE-CROSSER** (hitfn20 clause-1 FAIL at L=240: 4.96/4.53/5.78 vs bar
> 7.384; parity Δ=0.0 on all three). **K4 discharged**: 10,971 flags (all 8,971 ≥ hard gate
> 5.8835 + 2,000 random) batch re-scored in Python at **max |C−Python| = 0.0**. Lane verdict
> ([`analysis/round27/S1-CLOSEOUT.md`](analysis/round27/S1-CLOSEOUT.md)): **S1 NULL — the
> Py2.7-MT 2³² integer-seed space under the pair relation contains no key; branch EXHAUSTED**
> (conditional on the 3 named conditionals: this seed space, this transition model, the
> 9-register adjudicator). Oracle records: `analysis/round27/ORACLE-{35563892,348625413,86514964}.md`.
>
> **S2 (keyskip1 'exact', full 2³²) is PARKED at 44.14 % — it was IN-FLIGHT** per
> [`analysis/round27/sweep_plan.json`](analysis/round27/sweep_plan.json) — detached via `setsid`
> (survives session exit), ~11 h at sustained throughput. Full docs:
> [`analysis/round27/SYNTHESIS.md`](analysis/round27/SYNTHESIS.md) ·
> [`analysis/round27/MONITORING.md`](analysis/round27/MONITORING.md) ·
> [`analysis/round27/PREREG.md`](analysis/round27/PREREG.md).
>
> **Check status:**
> ```bash
> cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round27/P1-engine && ./grind27 --status --run-dir run
> ```
>
> **If `run/HIT-CANDIDATE.json` grows a new S2 hit:** a seed's screen pmax cleared the S2 CLAIM
> bar 7.6341931878728095. It is a **flag, not a verdict** — adjudicate exactly like the three S1
> crossers (`analysis/round27/oracle_crosser.py`, adapting C_PMAX/claim bar for S2): Python
> re-score parity, 3-clause `analysis/round20/HITFN/hitfn20.py` with
> `analysis/round19/I2/adjudicate.py` as adjudicator of record; even HIT=True stays
> **FLAGGED-FOR-ORACLE, never auto-certified** (R21-L1).
>
> **If the process died** (check `ps -p "$(cat analysis/round27/sweep.pid)"`): resume is proven
> exact (no gap, no double-count; the completed S1 is skipped) — use the resume block in
> `MONITORING.md`. Kill only by PID, never `pkill -f`.
>
> **When S2 finishes:** batch-re-score its `run/candidates.jsonl` rows through Python stage_b
> (pattern: `analysis/round27/s1_batch_parity.py`; K4: any C-vs-Python pmax disagreement > 1e-6
> voids parity — halt), validate S2's own planted control (its null does NOT count without it;
> `GRIND27_S2_CONTROL_OK=1` gates the lane), then convert ledger row
> **R27-CPORT-MT32-FULLSWEEP** (in-flight; S1 portion already recorded complete) into the
> completed null or the flagged survivor. Until then the OTP-class verdict is **UNCHANGED —
> hardened by the S1 null**.

> ## Round 28 — INTERIM CLOSEOUT 2026-09-15 (round OPEN: S2 sweeping, grind28 queue armed)
>
> Interim synthesis: [`analysis/round28/SYNTHESIS-INTERIM.md`](analysis/round28/SYNTHESIS-INTERIM.md).
> Ledger merged **157 → 162** (`R28-L1/L2/L5/R` + in-flight `R28-L4-UNSWEPT-GENERATORS-QUEUE`);
> `validate_ledger.py` Unsound-negatives = **0**; `R12-A1.not_covered` filled per the T1 patch.
> Lane state:
> - **L1** (pad-densification + pair relation) — **CLOSED, NEGATIVE** (`R28-L1-CICADAOS-PADS-DENSE-PAIR`):
>   24,080/24,080 rows, best 5.606 vs claim 7.384/7.634, 23 screeners all stage-B collapsed, 0 flagged.
> - **L2** (contested-bytes) — **CLOSED** (`R28-L2-CONTESTED-BYTES`). *Read half FINAL: canon stands*
>   (independent blind instrument = A-04 on all 11 conflict cells incl. the 3 byte flips;
>   186/209/210/211 first-verified; payload remains `round19/C1/payload_resolved.bin`).
>   *Decode half NEGATIVE*: 21,628,416 decodes, 0 ≥ family bar −5.7923, best −6.350 inside the null.
> - **L3** (string-seed Py2.7 amd64 dictionary) — **IN-FLIGHT**, PID **689907**
>   (`setsid nice -n 15 python3 sweep28.py --budget 345600`, resumed 21:34 PDT 09-15).
>   Tier-0 cells ×5 complete-NULL; tier-1 r29_pair ~347k words, best 6.095. Live: `L3/progress28.json`.
>   Coordinator decision of record (red-team D3): left running — measured cost ~4 %/thread at nice 15;
>   T5's prescription amended to "niced single-thread lanes tolerated". Row files at lane close.
> - **L4** (grind28: PHP both twists / glibc gen=0 / S3, 25 gated 2³² cells) — **QUEUED**
>   (`R28-L4-UNSWEPT-GENERATORS-QUEUE`, in-flight, ZERO coverage claimed). Frozen in
>   `L4/queued_cells.json` = merged `sweep_plan_r28.json` (set-verified); ≈15–19 days 6-core when fired.
> - **L5** (payload-micro E-01w/E-02v/H-03r) — **CLOSED, NEGATIVE** (`R28-L5-PAYLOAD-MICRO`);
>   the community "3301 in the 2012 P.S. digits" claim RESOLVED as a layout artifact.
> - **R** (red-team ×2) — **CLOSED** (`R28-R-REDTEAM`, audit). Pass 1: T2/T3/T4 NO-ERROR-FOUND;
>   T1 + T5 FOUND-ERROR (process-class). Pass 2 (`R-redteam/RESULTS.md`, 2026-09-16Z):
>   **ERRORS-FOUND-NONE-SCIENTIFIC** — every lane headline reproduces from raw artifacts,
>   0 dropped candidates (incl. the audited premature-grind28 orphan), 6 defects D1–D6 dispositioned
>   in SYNTHESIS-INTERIM.md.
>
> **Post-S2 auto-chainer — ARMED & running:** `analysis/round28/chain_after_s2.sh`, PID
> **701073** (`chainer.pid`; relaunched 2026-09-16T05:02Z after a host outage killed grind27
> 494140 at 41.7 % — chainer resumed it cleanly, checkpoint continuity verified). S2 = grind27
> PID **701083** (`round27/sweep.pid`), ~43 % at ~76k seeds/s → exits in hours. Chainer logic:
> polls `round27/sweep.pid` every 60 s; if grind27 dies with `lanes_completed` lacking `S2` →
> resumes it (`GRIND27_S2_CONTROL_OK=1`, pgrep double-launch guard); when S2 completes → writes
> `round28/S2-COMPLETE.marker` **first**, then launches the 25-cell grind28 queue
> (`setsid nice -n 10`, run dir `round28/run/` — physically separate from S2's,
> HIT-CANDIDATE copied + FLAGGED-FOR-ORACLE, progress → `round28/chain.log`).
>
> **How to STOP it all** (kill by PID only, never `pkill -f`):
> `kill $(cat analysis/round28/chainer.pid)` **first** (else it resumes what you stop), then
> `kill $(cat analysis/round28/grind28.pid)` if the queue is live (checkpointed, resumable),
> then — only if you truly mean to halt S2 — `kill $(cat analysis/round27/sweep.pid)`
> (resume recipe in `round27/MONITORING.md`). L3: `kill $(cat analysis/round28/L3/sweep28.pid)`
> (resumes from `progress28.json`). Never touch `round27/P1-engine/run/`.
>
> **Final-closeout checklist** (converts INTERIM → final; list also in SYNTHESIS-INTERIM.md):
> (1) S2 done → planted-control validation + candidates batch parity + **S2-lane oracle
> adjudication of crosser 35563892** (S1 verdict NOISE — must be recorded, not inherited) →
> convert `R27-CPORT-MT32-FULLSWEEP`; (2) queue runs → per-cell `stage_a28.py` parity +
> oracle on every crosser → convert `R28-L4-…-QUEUE`; (3) L3 close → own row;
> (4) apply red-team **D1** chainer `flock` patch at next chainer restart + the **D4**
> 8-row `not_covered` hygiene pass (`R/T1-PATCH-PROPOSALS.md` §3); (5) final SYNTHESIS.md.

Binding: [`liber-primus/ARMADA-DOCTRINE.md`](ARMADA-DOCTRINE.md). For a NEW solver deciding
where to spend effort (rather than picking up this project's own threads), read
[`handoff/SOLVER-STRATEGY-2026.md`](handoff/SOLVER-STRATEGY-2026.md). Trust anchor:
`python liber-primus/tests/validate.py` → `ALL VALIDATIONS PASSED` (5/5), passing through
Round 25 and re-verified 2026-08-31 (`pytest -m "not network"` 85 passed).
`validate_ledger.py` Unsound-negatives = **0**. `LEDGER.json` now holds **162 entries**
(R22-A/B/C/D/R, R23-A2, R24 ×5, R25 merged, the ten Round-20 lanes filed 2026-08-31, Round 26 ×4
[R26-A/B partially-run, R26-C negative, R26-D audit], **R27-CPORT-MT32-FULLSWEEP [in-flight]**
— S1 complete with a measured-exhaustion NULL, S2 still sweeping — and the Round-28 interim
merge of 2026-09-15: **R28-L1/L2/L5 negative, R28-R audit, R28-L4 queue in-flight**, see the
block above).

**The Round 23 seed at the bottom of
[`analysis/NEXT-ARMADA-ROADMAP.md`](analysis/NEXT-ARMADA-ROADMAP.md) ("ROUND 23 SEED") has been
RUN.** Its one scoped task — the printed-line-geometry acrostic — came back a clean,
control-validated NULL (Round 23), and the seed's own decision line therefore stands: **the
active work sits at a natural stopping point at the tested resolution.** Rounds 24 and 25 then
did the two things that judgment leaves open — Round 24 discharged the L7-A/L7-B instrument
conditionals (the negatives hold under the corrected scorers and the skip-aware decoder), and
Round 25 began the owner-elected grind of the last runnable branch (the Py2.7-MT 2³² tail),
**parked at 0.5015 % coverage, 0 hits, fully resumable**.

> **Round 26 is CLOSED (2026-08-31).** Merged, validated (Unsound-negatives = 0), trust anchor
> 5/5. Four lanes under `analysis/round26/` (SYNTHESIS: [`analysis/round26/SYNTHESIS.md`](analysis/round26/SYNTHESIS.md)):
> **A** fired the built-but-never-swept R19 generators — first-ever scored decodes for **Perl** (G2,
> was zero seeds) and **TeX** (G4, was zero decodes), plus the Py2.7 reducers on the **distinct
> amd64-w64 / non-zero-offset / `skip_by_two`** axis R21-L3 never ran; all control-validated at
> 1.000 recovery, 0 clears over the prior-dense front (dense-from-0 baseline tail still running at
> close-out → row is **partially-run**/interim). **B** executed R12-C2's staged-but-never-run
> 33-keytext running-key sweep skip-aware: **0/1,562** clears, 3 of 9 pages complete at 4 offsets,
> large pages honestly capped into `not_covered` (**partially-run**). **C** enumerated a bounded
> **323-value corpus-semantic seed set × 7 generators × 2 decoders = 4,274 rows at 100 % coverage**
> (incl. the page-56 totient/prime ladder), control min recovery 0.9917, best screen −6.578
> (flat-random), **0 escalated** (**negative**). **D** red-team: **NO-ERROR-FOUND**, coverage×power
> reproduced from raw rows, no silent re-run, no FP-inflation, two MINOR hygiene defects noted.
> **0 oracle flags, no stop-and-alert. OTP-class verdict UNCHANGED — hardened along three
> previously un-swept axes, not overturned.** One loose thread: Lane A's dense-from-0 baseline
> sweep (`analysis/round26/A/sweep.py`) is still running in the background; it only extends the
> same null and finalizes `control.json` on completion.

---

## The one-paragraph state of the board

The standing verdict is unchanged: **LP2 0–54 is OTP-class** — statistically indistinguishable
from a one-time pad under every tested class, with a soft anti-repeat rewrite (~83% suppression)
acting on the ciphertext output. Rounds 18–25 did not move that; they moved the *instrument*, the
*measured status of branches inside it*, and **which of the signed-hint channels have actually
been read.** Round 18 proved the old magnet was broken; Round 19 rebuilt it (drift-tolerant
decoder, nine-register adjudicator, recalibrated nulls — no verdict flips); Round 20 found the sieve
that would make the enumerable-PRNG sweeps affordable **infeasible**; Round 21 found the no-oracle
seal **provably leaky** (best fold 0.80 vs a 0.90 bar → **HIT auto-certification WITHHELD; survivors
flagged-for-oracle**), swept one more Py2.7 slice clean, and measured the `n_skips` window at
**≥ ~6000 runes**. **Round 22 turned away from the letter-stream PRNG branch and, for the first
time, read every channel the signed hints point at** — the hidden message *inside the already-solved
plaintext* (X2, Lane A), the *numbers-as-direction* turtle render (G1, Lane B), the
*koans-as-operations* (X1/X3/X4, Lane C), and the *art-as-data* drop-cap channel (S3, Lane D) — and
**all four came back clean, control-validated NEGATIVES**, with the red-team lane (R) returning
**NO-ERROR-FOUND**. Combined with Round 11 (N1–N5, S1–S2), **every roadmap lens the hints name has
now been read at least once at the tested resolution.** The "we never even looked at the hinted
channels" objection is now **largely closed.** The two branches that could still hide the true pad
are untouched by any of this and remain exactly where they were: the **PRNG/seed tail** (built
byte-exact, unswept, **bounded — not closed**) and the **`/dev/urandom` branch** (untouchable by
construction). The completeness-critic's verdict that round: **the sharpest surviving reopener is
Lane A's printed-line-geometry acrostic — the one representation R22-A could not build — and after
that single cheap task the honest prior on the remaining reopeners is low.**

**Since then (2026-08-30/31):** **Round 23** ran exactly that task — the printed-line acrostic at
the true page-image line breaks, geometry from the same transcription `validate.py` trusts — and
it is a **clean, control-validated NULL** (48 reads, Phase-0 recovery 2/2 = 1.000, 0 family-wise
survivors). Every roadmap-named lens is now read. **Round 24** killed 5 of 8 candidate lanes at
its planning gate and ran the three survivors: the strongest prior B-04 slice re-adjudicated
under **matched-runic + genuinely language-aware scorers** (L7-A axis — clean NULL, 20,480
decodes ×2 lanes), the **`skip_by_two`-capable decoder** re-decode plus its broadening across 7
generator axes (L7-B axis — 245,975 + 113,432 keys, 0 hits, no beam-based negative reopens), and
the date-indexed-pad lane (**premise fails at Step 0**: the unsolved runic pages carry no PGP
signature). **The two conditionals hanging over every historic negative since Round 18 are now
measured through, and the negatives hold.** **Round 25** is the owner-elected compute grind of
the one runnable branch left — the Py2.7-MT 2³² seed tail under the skip-aware decoder —
**PARKED 2026-08-31 at 0.5015 % of 2³² (21,539,647 words), 0 hits, best pmax 6.826 vs bar
7.384**, resumable per-worker from the committed `progress_w{0..5}.json` checkpoints
(`analysis/round25/compute-tail/RESULTS-parked.md`).

---

## What Rounds 23–25 shipped (details)

| round | verdict | one line |
|---|---|---|
| **23** A2 printed-line acrostic | **CLEAN NULL, control-validated** | The last roadmap-named reopener, read at true resolution: 48 reads ({line,word} × {first,last} × {fwd,rev} × {5 pages + concat}) over the validated geometry; family bar −3.597, best real read −6.22; the single per-cell crosser is below the expected-FP count and gibberish. [`analysis/round23/SYNTHESIS.md`](analysis/round23/SYNTHESIS.md) |
| **24** C1 + C1-EXT register axis | **NULL — negatives HOLD** | Matched-runic scorer + language-aware Latin/Greek/OE-poetic/Enochian panels (each proven to beat the English scorer on its own planted language) over the strongest B-04 slice: 0 survivors. The English-only negatives were not hiding a non-English plaintext there. [`analysis/round24/SYNTHESIS.md`](analysis/round24/SYNTHESIS.md) |
| **24** C2 + C2-EXT relation axis | **NULL — no negative reopens** | The `pair`/`keyskip2` decoder (100% plant recovery on `skip_by_two` where the beam gets 25.8%, own bar 7.384) over the top-prior slice + bash/perl/tex/sha-keytexts/offsets/drift-cousin: 359,407 keys total, 0 hits, 8/8 + all controls validated. |
| **24** C8 date-indexed pad | **UNAVAILABLE at Step 0** | The unsolved runic pages carry **no PGP signature**, so the timestamp→offset join key does not exist; steelman probe (630 tests vs the NIST beacon) null anyway. |
| **25** compute-tail | **PARKED, 0 hits at 0.5015 %** | Owner-elected checkpointed grind of the Py2.7-MT 2³² tail; planted-seed control passes every invocation; a live drill proved the HIT path stops all 6 workers. ~25–32 wall-days remain at CPython speed; a GPU/C port does it in hours. [`analysis/round25/SYNTHESIS.md`](analysis/round25/SYNTHESIS.md) |

---

## What Round 22 shipped

| lane | roadmap | verdict | one line |
|---|---|---|---|
| **A** self-embedded read | X2 | **NULL, control-validated** | 3,508 selection functions (every-k / reversed / diagonal folds) over the 5 rig-solved pages' DECRYPTED plaintext; Phase-0 planted-acrostic recovery **1.000**; **0 family-wise survivors** (6 per-cell FPs vs 3.5 by chance = noise). "Seek within" as an acrostic-of-the-solution is clean-negative. **Sharpest reopener:** first-rune-of-each-PRINTED-LINE acrostic using real page-image line geometry (this lane had only the concatenated transliteration). `sweep_results.json`. |
| **B** turtle + spatial | G1, G3 | **CLEAN NULL, 0 flagged-for-oracle** | The value / π(p) / φ(p) stream drawn as a turtle path across **72 render combos**; Phase-0 planted square fires 5/6 geometry stats; 6 shape-stat p<0.01 candidates all fail Bonferroni (2.3e-5) as multiple-comparisons noise; G3 base32/onion/lat-long **POINTER_FOUND=False**. Already merged R22-B + R22-C into `LEDGER.json`. **Reopeners:** G2 non-turtle 2D/columnar reads, other moduli/step-fns, 3D lifts. `g3_results.json`. |
| **C** literal imperatives | X1, X3, X4 | **NEGATIVE, 0 survivors** | **185 enumerated operations** (decimation, cipher-iterate, interleave, reversal, running-key, prime-value/index/totient keystreams) under the 9-register panel-max bar; all 4 Phase-0 controls recover 1.000 (X3b/X4 held-out 1.000). 4 keyed decodes cleared 0.90 recovery but were **correctly rejected at panel-max** — the exact hallucination the recovery gate exists to catch. **X4-totient re-adjudicates Round-11 N5 under the repaired instrument, re-confirms NEGATIVE.** `ledger.json`. |
| **D** illustration / drop-cap | S3 | **NEGATIVE (min p=0.18); RUNNABLE** | First LP2 drop-cap catalog (15/58 illuminated, runes `SLXHXFUMDSFAINGP`); presence/order/gap/centroid/identity clear no p<0.01 Bonferroni bar; controls 4/4 + page0=S. **NOT blocked on assets — page scans are in-repo.** **Reopener:** figural-motif channel (crosses/trees/shrouded-corpse/mayflies) not yet coded as data. `features.json`. |
| **R** red-team | R6 | **NO-ERROR-FOUND** | Independently reconfirmed B's family-wise 0-survivor (P(≥6)=0.072, noise; the 4.7σ 'components' candidate is a discrete-stat z-tail artifact). No lane silently re-reads a Round-11 negative; all nulls seed-3301; no −5.5 relapse; no lane on an unvalidated instrument. One low-severity non-blocking disclosure gap (B's G3 coord-pair ~ Round-11 N2 route (d)) — **fix applied** (B now cites N2). `RESULTS.md`. |

Standing OTP-class verdict unchanged. All five lanes' positive controls fired first; `validate.py`
5/5 before and after; `validate_ledger.py` Unsound-negatives = 0. Merged as `LEDGER.json` entries
**R22-A-SELFEMBEDDED-READ / R22-B-TURTLE-SPATIAL-RENDER / R22-C-LITERAL-IMPERATIVES /
R22-D-ILLUSTRATION-DROPCAP / R22-R-REDTEAM** (130 → 135).

---

## What Round 21 shipped

| lane | verdict | one line |
|---|---|---|
| **L1** seal (real-mode no-oracle proxy) | **KILL — gate provably leaky** | The disjoint-fold proxy lifts correct-key EN_NOVOWEL catch from the single-cut **0.33 → 0.80** (genuine-safe, k=5/min) / **0.87** ceiling (genuine-unsafe), but **no cell reaches the pre-registered 0.90** and the winning cell's false-reject drifts **0.00 → 0.167** on a fresh held-out surrogate. Positive controls fired first (45/45 hallucination reproduction, 15/45 single-cut baseline, 20/20 genuine panel). **Consequence: Round 21 HIT auto-certification WITHHELD — bar-clearing survivors are flagged-for-oracle.** Seal open to a *non-fold* family. `catch_surface.json`. |
| **L3** Py2.7 reducers + amd64 map | **CLEAN NEGATIVE** | **884,000 words**, 0 hits, across `grb5_mod`/`grb5_rej`/`shuffle29` (i386) + `random29` (amd64 2-word init) — the reducer axis + 64-bit ABI map S-G3 left open. **4/4 positive controls recover 1.000 (pmax 28.3, rank-1)**; best decode **pmax 6.248 vs the 7.634 bar** (1.39 below). All 45,975 prior-dense words covered per config. **Bounded, not closed** (>99.99% flat-prior tail ≈61 core-days + 2⁶⁴ amd64 image + inherited S-G3 gaps). `reducers_sweep.jsonl`. |
| **L2** `n_skips` crossover length | **MEASURED — L\*=6000** | On the exact `keyskip1` relation, `n_skips` crosses from non-separating to separating at **L\*=6000** (bracket (3600,6000], holds at 9000/12956); correct-key overtakes the wrong-key *mean* at L≈1000 but clears the 1% right *tail* only at 6000. **Any whole-book / concatenated-page n_skips adjudication needs a window ≥ ~6000 runes.** `drift` "separation" is a LEFT-tail artifact; `skip_by_two` is beam-unrepresentable (crossover None). Plant recovery ≥0.998 at every L; R20 endpoints reproduced. `nskips_crossover.json`. |
| **L5** red-team | **MIXED** | Confirms the **L1 KILL** independently; **NO-ERROR-FOUND** on (b) no silent re-run of foreclosed lanes, (c) the 2.5×10⁶ sieve × panel-max FP inflation is **not** re-introduced (fold machinery FP-neutral, sweeps unscreened), (d) the row gate is honest (score alone can never be a HIT). FP-inflation conditional stands exactly as R left it in Round 20, binding on any FUTURE screened sieve only. |

Standing OTP-class verdict unchanged. All four lanes' positive controls fired first and passed;
`tests/validate.py` 5/5 before and after; `validate_ledger.py` Unsound-negatives = 0. Merged as
`LEDGER.json` entries **R21-L1-SEAL / R21-L2-NSKIPS-CROSSOVER-LENGTH / R21-L3-PY27-REDUCERS /
R21-L5-REDTEAM-SEAL** (126 → 130).

---

## What Round 20 shipped

| lane | verdict | one line |
|---|---|---|
| **P1** sieve | **INFEASIBLE** | Best simultaneous survival at ≥100× reduction on CY + half-vowel English = **0.667** (Wilson95 UB 0.85 < 0.90 bar). The multi-register lever *works* — it lifts vowel-dropped English **0.000→0.800**, half-vowel **0.067→0.667**, Welsh **0.300→0.733** off the English-only floor — but cannot reach 0.90 on a 24–32-rune decrypt head. `survival_surface.json` published. |
| **P2** `n_skips` null | **2 of 3 PASS** | `nskips_null.json` built (seed 3301, order-preserving) + `SWEEPROW/2` wired; the positive control does **not** separate at page-window lengths (separation appears only at full-book scale). |
| **P3** null/seed/drift | **PASS ×3** | Panel-max direct null `panelmax20.json` (correct-key power **1.00** / wrong-key 0.00 on LP1_REAL/LATIN/OE/half-vowel); seed prior `seedprior20.json` (**433** candidates, rank 1 = **1325734783**); drift re-baseline confirms OE `pmax` shortfall (13.543 vs 13.842) and the fragile-decode-channel bound. |
| **R** red-team | **NO-ERROR-FOUND / FOUND-ERROR (latent)** | No power leak on a structured wrong-key null (survival 0.000). **But** sieve × panel-max FP interaction inflates the survivor FP to **0.025/decode** vs the nominal **1e-8** — a 2.5×10⁶ inflation any future sieve must correct. |
| **N1** PDF/font hunt | **NEGATIVE** | No surviving LP PDF/PostScript with a runic text-layer or embedded font subset in 195 local PDFs or across the 4 named mirrors; the S-TEX `allrunes` promotion trigger did **not** fire. |
| **N2** haplography | **NO-ERROR-FOUND** | ~20 doublet-site merges do **not** reopen autokey; the positive refutation is hardened. |
| **C** closeout | **DONE** | L1-prior corrections propagated to source; nav docs + this file. |

Because Phase S was hard-gated on **P1∧P2∧P3 all PASS** and P1 failed, **no S-lane scored a single
decode.** The PRNG sweeps are exactly where Round 19 left them.

---

## What is still OPEN (ranked after Round 22; per-item updates through Round 25 marked inline)

> **Completeness-critic finding (this round's roadmap Phase-6 pass).** The six untouched roadmap
> lenses that justified Round 22 — **S3, X1–X4, G1-turtle** — are **now all read** (Round 22 lanes
> A/B/C/D), each a control-validated NEGATIVE. Combined with Round 11 (N1–N5, S1–S2), **every roadmap
> lens the signed hints name has been read at least once at the tested resolution.** The
> high-prior novel-channel budget is therefore mostly spent — what remains are **resolution gaps
> inside those reads**, not new channels. The doctrine's optimism clause (§5) is real, but all three
> of this project's past reopenings came from **auditing an instrument or a closure**, never from one
> more framing of an already-read channel — and two of the three Round-23 threads (D2, B2) are the
> latter. **The one thread worth running is A2** (item 0): a first-rune-of-each-PRINTED-LINE acrostic
> using the real page-image line geometry, the single representation R22-A could not build and the
> most conventional hiding spot for a self-embedded message. It is cheap (a transcription task + a
> re-run of R22-A's validated sweep) — **an afternoon, not an armada.** See
> `analysis/NEXT-ARMADA-ROADMAP.md` → "ROUND 23 SEED" for the honest-prior judgment.

0. ~~**[highest surviving novelty × prior] A2 — printed-line-geometry acrostic (from R22-A
   `not_covered`).**~~ **RUN — Round 23 closed it: CLEAN NULL, control-validated**
   (`analysis/round23/A2-line-acrostic/`, ledger `R23-A2-LINE-ACROSTIC`). The original text is
   kept below because its reasoning still ranks D2/B2 correctly (both remain un-run and
   low-expectation). R22-A read every-k / diagonal / substring selections of the concatenated solved
   plaintext and returned a control-validated NULL, but it could **not** reach the one representation
   a human calligrapher's message would most likely use: **the first rune of each PRINTED LINE (and
   per-word) acrostic, using the true page-image line breaks + word spacing.** R22-A had only the
   concatenated transliteration; the physical layout is unreconstructed. This reuses R22-A's
   validated acrostic recognizer (recovery 1.000) — only the input geometry changes — so it needs
   just a line-break transcription of the 5 solved pages plus a re-pointed Phase-0 control. **The
   single place a self-embedded read could still hide.** Then D2 (figural-motif channel, gated on
   building a control-validated motif extractor first) and B2 (non-turtle 2D/columnar reads at true
   line width, Lane G2) are cheap-to-run but **low-expectation** — see the Round 23 seed.

1. **~~S-G3 Python 2.7 `random.seed(<string>)`~~ — the reducer + amd64-map axis is now SWEPT
   (Round 21 L3, CLEAN NEGATIVE).** 884,000 words across `grb5_mod`/`grb5_rej`/`shuffle29` (i386) +
   `random29` (amd64 2-word init), 0 hits, best pmax 6.248 vs 7.634. **What remains is a
   stated-fraction negative that is bounded, not closed:** >99.99% of each config's 2³² flat-prior
   tail (~61 core-days for all four full enumerations), the full 2⁶⁴ amd64 hash image, and the
   inherited S-G3 family gaps — other decoder relations (`skip_by_two`/`keyskip2`), non-panel
   registers, PYTHONHASHSEED/`-R` randomized hash, WichmannHill, float/jumpahead seeds, Python
   2.6/2.5. `random29/i386-1word` was already S-G3-covered (round20) and was deliberately **not**
   re-run. Reopens the moment someone spends the core-days or validates a new Py2.x seed family.
   Measured in `analysis/round21/L3-py27-reducers-plus-64bit-map/`.
   _Update (Rounds 24–25):_ the `skip_by_two`/`keyskip2` relation gap named here is now covered
   for the prior-dense slices (R24 C2 + C2-EXT, 359,407 keys, 0 hits), and the `random29` flat
   tail is being ground directly — Round 25 parked at **0.5015 % of 2³²**, resumable
   (`analysis/round25/compute-tail/`).

2. **The no-oracle held-out SEAL is provably leaky — HIT auto-certification is WITHHELD (Round 21
   L1, KILL).** No disjoint-fold cell in the swept grid reaches ≥0.90 catch at ≤0.10 false-reject on
   held-out data (best 0.80 genuine-safe / 0.87 ceiling; held-out false-reject 0.167). **Until a
   no-oracle gate that clears 0.90 exists, any bar-clearing real-mode survivor from any sweep is
   flagged-for-oracle, never auto-certified as a solve.** The fold family alone is bounded at
   ~0.82–0.87; the seal is **still open to a NON-fold proxy** — a longer decrypt head than the 24–32
   rune head that capped R20 P1, a per-register fold bar, or a learned self-consistency gate. A
   `keyskip1`-relation hallucination population (the exact-preset overfits used here do not populate
   the relation axis) would also extend the surface. Measured in
   `analysis/round21/L1-seal-realmode-proxy/` (`catch_surface.json`).

3. **Fix the sieve × panel-max FP inflation (R's Round-20 FOUND-ERROR) before trusting any screened
   sweep.** Screened survivors carry a **2.5×10⁶ FP inflation** against the nominal panel-max bar.
   Any future P1-style sieve must either re-derive the null *on the screened population* or apply the
   measured correction. Until then, sweep **unscreened** (as R21 L3 did) or carry the inflation as an
   explicit conditional. **Round 21 L5 confirmed this item is NOT re-introduced** — R21's sweeps are
   unscreened and the fold machinery is FP-neutral (exactly one pmax evaluation per decode) — so it
   stands exactly as R left it, binding on any FUTURE screened sieve only.

4. **The sieve itself — is 0.90-at-100× the right bar?** P1 is infeasible *for that gate*. A future
   round could (a) lower the reduction target (e.g. 30× instead of 100×) if compute allows, (b) use a
   longer decrypt head than 24–32 runes (the signal ceiling that capped the hard registers), or
   (c) accept a per-register sieve with published leakage. `round20/P1/survival_surface.json` has the
   full surface to decide with numbers.

5. **P2's `n_skips` separation appears only at full-book scale — Round 21 L2 measured the
   crossover length: L\* = 6000 (≈11–12 pages) on the exact `keyskip1` relation.** At page-window
   lengths the statistic does not separate planted from wrong-key; it first clears the FPR=0.01
   two-sided bar at **L=6000** (bracket (3600, 6000], holds at 9000/12956), while the correct-key
   footprint overtakes the wrong-key *mean* already at L≈1000 but does not clear the 1% right *tail*
   until 6000. So any concatenated-page / whole-book `n_skips` adjudication must use a window of
   **≥ ~6000 runes** before `n_skips` **alone** is valid; below that, combine with the P3a panel-max
   score or enlarge the window. **Two channels do NOT give this crossover honestly and must not be
   read as page-scale discriminators:** the `drift` permissive beam fabricates huge wrong-key skip
   counts so the correct key sits in a LEFT-tail artifact at every L; and `skip_by_two` (R18 L7-B)
   the beam cannot represent, recovering 0 skips. Measured in
   `analysis/round21/L2-nskips-crossover-length/` (`nskips_crossover.json`, RESULTS.md); plant
   recovery ≥0.998 at every L; R20 endpoints (L=400 no-sep, L=12956 sep@0.999) reproduced.

6. **The remaining enumerable families stay sieve-gated and unswept:** bash `$RANDOM` (77.6M
   auto-seeded orbit, ~28 min), Perl 5.14 (2³², ~34 h full or a stated-fraction sample), TeX LCG
   one-cycle (~18 h), Marsaglia held units (679 units, ~21 CPU-h). None is closed. Each reopens the
   moment a sieve reaches the target *or* the coordinator accepts an unscreened stated-fraction sweep.
   *(Note: the doctrine and the completeness-critic both counsel against leading Round 22 with these —
   they are more of the same letter-stream sweep at a flat prior; queue them behind item 0.)*
   _Update (2026-08-31):_ their **prior-dense fronts** were swept clean under the skip-aware
   decoder in R24 C2-EXT (bash/perl/tex axes, 0 hits); the full tails remain compute-only.
   Two housekeeping sub-items surfaced by the Round-21 synthesis (filed late) also live here:
   **(a)** Round 21's planned **L4** never ran — the glibc `gen=0` full-32 row
   (`LEDGER.json:R19-G3-CORRECTION`) is still the one open row, and `gen=7`/`gen=8` are still
   un-re-adjudicated through I1+I2; **(b)** Round 21's planned **L6** never ran — the sieve
   reopening decision from `round20/P1/survival_surface.json` (carry Perl/TeX/Marsaglia as
   stated-fraction unscreened samples, or name the lowered feasible operating point) costs no
   compute and has now been deferred twice.

7. **The `/dev/urandom` branch is untouched and untouchable.** If the pad was a CSPRNG or hardware
   draw, nothing in any round recovers it. A clean negative on the enumerable families does **not**
   touch this branch — it only shrinks the "cheap seeded PRNG" hypothesis. This branch is real and may
   be the true one (doctrine §5); leave it untouched.

---

## Open governance item the coordinator must decide (C-canon)

**Should the 3 changed payload bytes (idx 45, 50, 246 → `payload_resolved.bin`) become canonical?**
Round 19 C1 corrected them and re-ran B-05 clean, but **B-04 / R16-KDF / R17 are input-sensitive
downstream** of the payload bytes. Lane C **flags but does not decide** this. If promoted to canon,
those three lanes must be re-checked against the new input and their `LEDGER.json` coverage restated.
Tracked as `LEDGER.json:C-CANON-PAYLOAD-3BYTES` (status `open`).

---

## One transcription candidate flagged for a human (C-eyeball)

> **[X1/R32 scope note]** "Transcription closed / verified three ways" holds for the **LP2 typeface only**: T1's
> pooled G-READ-ALL FAILED (1,879/1,976 = 95.09 %, bar 99 %; LP1 94.60 % recall, undiagnosed). **p27:93 (U→B, margin 5,
> smallest in corpus; `round19/T1/RESULTS.md` line 414/488) is STILL UNRESOLVED and still needs a human to look at the glyph.**

**T1 p27:93, U→B, margin 5.** This is the single weakest transcription disagreement Round 19's T1
audit surfaced (canon upheld 450/450 overall, but this cell's margin is thin). It wants a human eye
on the actual glyph, not another automated pass. Not load-bearing for any current verdict, but worth
resolving before the next transcription-dependent sweep.

---

## Do NOT re-run (foreclosed — `ELIMINATION-LEDGER.md:328–384`)

Published-keytext/running-key (doublet-excluded by mechanism); the number channel (Round 11, 7 lenses
NULL); OSINT/AN-END retrieval (unreachable by construction); attribution-to-a-name (359-word corpus
< floor); stego/LSB/OutGuess/red-rune re-runs; autokey/ciphertext-feedback (positively refuted — the
one live reopener, A-03 haplography, was checked NEGATIVE by Round 20 N2); any ciphertext-only sweep
under a flat prior, a rigid decoder, or an English-only scorer. Before opening any lane, query
`LEDGER.json` `coverage`/`not_covered`, not `status`.
