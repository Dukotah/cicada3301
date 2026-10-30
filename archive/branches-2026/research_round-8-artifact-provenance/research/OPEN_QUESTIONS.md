# OPEN QUESTIONS — Liber Primus (LP2)

Priority-ordered. The owed **holdout test** is pinned at the top and must be honored before any
newly-proposed decode method is believed. This file is rewritten/refined each round by the Archivist;
the holdout pin is set by the orchestrator and is **not** removed retroactively.

---

## ★ PINNED — OWED HOLDOUT TEST (set Round 8, orchestrator; cannot be added retroactively)

**Reserved blind anchor: `AN END` (LP2 page 56 / file `73.jpg`).**

- It is the **only cipher-solved page located inside the otherwise-unsolved LP2 block** (pages 0–55).
  Its known method is a running **φ(prime) totient keystream** (`(p−1) mod 29`, shift down) with
  F-interrupters. Its plaintext contains a SHA-512 string.
- **The rule:** any method proposed in a future round that claims to decode *unsolved* LP2 pages must
  FIRST recover `AN END`'s plaintext **without being handed the totient key** — i.e. the method must
  discover the key/keystream family on its own from ciphertext + its stated external input. A method
  that can only be validated on the LP1 pages (whose keys are short natural-language words: DIVINITY,
  FIRFUMFERENFE, Atbash, Caesar−3) has **not** been shown to generalize into LP2 and is treated as a
  keyspace search, not a method.
- Agents seeded this round are pointed at the LP1 anchors for calibration but are **not** told to lean
  on `AN END`; it is held in reserve so its recovery remains a genuine blind test.
- **Status: OWED.** No Round-8 hypothesis proposes a new LP2 decode, so no holdout test is consumed
  this round. The pin persists until a live decode method is approved at Gate #1.

### Ground-truth locations (for agent seeding — where solved-page plaintext & keys live)
- `liber-primus/tests/validate.py` — **the trust anchor**: reproduces *every* known solved page from
  canonical runes. Any method must pass through this harness's style of validation.
- `liber-primus/SOLVED-PAGES-AND-INTERRUPTERS.md` — per-page keys, methods, page-numbering schemes,
  the ᚠ-interrupter rule.
- `liber-primus/dataset/liber_primus.json` — machine-readable parsed pages incl. documented `plaintext`.
- `liber-primus/data/sources/relikd_*.txt` — raw per-page rune transcriptions.
- `liber-primus/data/relikd/p0.jpg … p55.jpg` — page **images** (⚠ relikd community re-encode:
  2400×3600 JPEG @400 DPI — a *derived* copy, NOT the original 3301-distributed artifacts; any
  file-level forensic claim must state which layer it measures).

---

## Open questions (priority order)

Two prior research lineages exist and are being reconciled on this branch:
- **`origin/master` (canonical, 2026-07-29):** `liber-primus/ELIMINATION-LEDGER.md` + `FINAL-SYNTHESIS.md`
  — the "Loop iter 1–11" body; already ran a data-provenance red-team, artifact-premise audit,
  red-rune/color-layer follow-up, stego verdict, armada onion-OSINT.
- **`research/round-1…7` (rigor-rail loop):** `research/LEDGER.md` + `research/DEAD_ENDS.md` — the
  pre-registered gated rounds.

The Archivist reconciles both before any hypothesis is approved, so no closed finding is re-derived.

0. **★ PINNED (Round 8, owed) — resolve the S2 DQT anomaly: production-batch vs content-driven.**
   S2 found the two JPEG DQT quantization-table fingerprints are **strongly non-random w.r.t. page order**
   (runs R=11 vs E≈28.1, z=−4.77, MC p≈0) but the batch-vs-content question is INCONCLUSIVE because the
   file-size confound proxy is too weak (MW p=0.091) and the pattern is blocky/**alternating** (~11 blocks),
   not two contiguous batches. **Resolving measurement (pre-specified by Critic Gate #2):** (a) dump the two
   actual 64-coefficient DQT matrices (`32386501afff` vs `a3a96add050f`) — if they are two Ghostscript
   quality-ladder tables that's a tool/quality switch; if structurally distinct, two pipelines; (b) replace
   byte-size with a DIRECT complexity proxy (per-page non-blank DCT energy / rune-region ink area) and re-run
   the Mann–Whitney at adequate power. Upgrade to SURVIVES only if groups are complexity-indistinguishable
   under a real proxy; else NEGATIVE. **Note: ZERO ciphertext bearing regardless — this is production-pipeline
   forensics, not a solve path.** Low priority; cheap; runnable now.
1. **(META, standing) Which attack surfaces has NEITHER lineage actually executed?** Round 8 diffed both
   kill-logs; the file-metadata forensic layer is now near-exhausted on the LOCAL artifacts (images are the
   stock-Ghostscript-sRGB render, no operator metadata; only S2's encoder-layer artifact remains, and it is
   downstream of any glyph/cipher content). Genuinely-untested ground is now scarce; most future rounds will
   correctly end NEGATIVE absent a new external input.
2. **(EXPLORATORY only) Negative-space stylometric exclusion** — Burrows' Delta / nearest-neighbour of
   the ~359–800-word solved LP prose vs public-domain reference sets. Exclusion ("LP does NOT cluster
   with X") is defensible at small N even though positive attribution is not. Label EXPLORATORY.
3. **(EXTERNAL, deferred) Re-run the external-input scout** only when a *new* PGP-signed artifact/key
   surfaces. Do NOT reopen ciphertext attacks absent that. Last verified 3301 signature: April 2017.
4. **(PROVENANCE) Original-artifact forensics vs. relikd re-encode** — is there any file-level evidence
   surviving in the *original* 3301-distributed images (not the local relikd JPGs) that fingerprints
   generation tooling / operator error? Requires sourcing originals; state the provenance layer.
5. **(MONITOR) Court dockets** 26-000013-MZ / 25-012153-CZ for identity-relevant discovery.
