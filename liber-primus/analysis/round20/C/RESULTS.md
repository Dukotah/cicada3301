# Lane C — CLOSEOUT & PRIOR PROPAGATION · RESULTS

_Round 20, Phase C. Pre-registration: [`PREREG.md`](PREREG.md), written before any edit.
Binding: [`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

**Trust anchor, before + after the lane:**
`python3 liber-primus/tests/validate.py` → `ALL VALIDATIONS PASSED — rig reproduces known solves.` (5/5)
`python3 liber-primus/analysis/handoff/validate_ledger.py` → schema 1.0.0, **Unsound negatives: 0**.

Lane C ran **no search** and **scored no decode**. Its four jobs, all from the campaign plan §6
Phase C, are done. Nothing here overturns a verdict; the OTP-class standing verdict is untouched.

---

## Headline

| job | what shipped |
|---|---|
| **C-prop** | The three L1-prior corrections no Round-19 lane had write-scope for are propagated to their **source-of-record**: F6/F7 counts, the looser distro bracket, and G2's prior re-sourced to Crypt::RSA. Written into `round18/L1-toolchain/RESULTS.md` (superseded-markers, not deletions), plus a consolidating `LEDGER.json` entry `L1-PRIOR-PROPAGATION`. |
| **C-nav** | Round 19 + Round 20 rows appended to `ELIMINATION-LEDGER.md` and `analysis/README.md`; a "Latest rounds" block added to `README.md`; `PICKUP-HERE.md` opened for Round 21. |
| **C-eyeball** | The one weak transcription candidate **T1 p27:93, U→B, margin 5** flagged for a human, in `PICKUP-HERE.md`. |
| **C-canon** | Recorded as **decision-pending** (NOT decided by Lane C): whether the 3 changed payload bytes (45, 50, 246) become canonical, since B-04 / R16-KDF / R17 are input-sensitive downstream. Tracked as `LEDGER.json:C-CANON-PAYLOAD-3BYTES` (status `open`). |

---

## C-prop — the L1-prior corrections, propagated to source

Round 19's C3 measured three defects in L1's evidence-derived prior but stated explicitly (C3
§6.5, parenthetical) that fixing them at source was **outside C3's write scope**. R1 reached the
same distro-bracket defect from the render side. Lane C carries the corrections home.

### (i) F6/F7 counts — `46/46 · 2012→2014 · no drift` is wrong

Source: `round19/C3/RESULTS.md` §6.5, re-derived independently (PGP table reproduced **228/228
file-for-file identical to R18**, including every sha256, with the C2 tamper→BADSIG and C3
foreign-key→no-GOODSIG controls both PASSing — that is the positive control licensing this edit).

Corrected facts now written into `round18/L1-toolchain/RESULTS.md`:
- The `ibotpeaches/messages/` directory holds **56 PASSing files / 54 distinct signed messages
  running to 2017-04-04**, not 46 ending in 2014.
- Armor `Version:` headers: **53 × `GnuPG v1.4.11 (GNU/Linux)`, 2 × `GnuPG v1`, 1 ×
  `CicadaPG v.3301`**.
- The **toolchain changed twice, not once**: an armor-form change (2014-04-02 → 2015-07-28) and a
  hand-set `CicadaPG v.3301` + SHA-512 on the final 2017-04-04 message.
- L1's *conclusion survives and sharpens*: the 1.4.11 environment is bounded to **2012-01-05 →
  2014-04-02 (818 days)**, covering the whole LP release window.

Edits made (superseded-markers per `CLAUDE.md`, old text struck not deleted): the §6.1 F6 row, the
§6.2/§6.1 F7 row, the composite-inference paragraph, the §6.2 rank-3 Perl row, and the summary
`46/46` line, plus a dated correction block under the intro. See §"Files changed" below.

### (ii) The distro bracket is looser than published

Sources: `round19/R1/RESULTS.md` §C (render/packaging side) + `round19/C3/RESULTS.md` §6.5b (signed
corpus side). Two independent lanes, two independent evidence bases, one conclusion: GnuPG 1.4.11
shipped across **≥6 OS generations including Ubuntu 12.10**, *outside* L1's stated 11.04–12.04
bracket. The *era* attribution stays (if anything tighter); the *distro bracket* used to rank the
generator families is looser. Written into the F7 row and the composite-inference block of
`round18/L1-toolchain/RESULTS.md` as a bracket-loosening note, with the ranking explicitly stated
as **not weakened** — only the bracket that ordered it.

### (iii) G2's Perl prior re-sourced to the Crypt::RSA fact

Source: `round19/C3/RESULTS.md` §6.6. The rank-3 Perl 5.14 prior was justified by a distro
inference ("Ubuntu 12.04's system Perl"). C3 found a strictly stronger, dated, authenticated fact:
a signed 3301 message (**2012-01-15, PASS**) states "the Crypt::RSA Perl module available in CPAN"
and pastes a live `Crypt::RSA::Key::Public` object as `Data::Dumper` output; the library's own
`Version: 1.99 / Scheme: Crypt::RSA::ES::OAEP` armor recurs on a second PASSing message
(**2014-01-06**). Both dates fall inside the 1.4.11 window. The §6.2 rank-3 row is re-sourced to
this. **This is not a claim about the keystream** — it establishes a working Perl+CPAN environment,
per C3 §6.6 "What this is not."

### The consolidating ledger entry

`LEDGER.json` gains `L1-PRIOR-PROPAGATION` (status `audit`, round 20) recording all three
corrections with `coverage`/`not_covered` (never a bare status) and pointing at the source lanes
`L1-F6-CORRECTION`, `R19-G2`, `R19-G2-CORRECTION`, `G-02`. Its `not_covered` states plainly: the
keystream question is untouched, the "short `GnuPG v1` form" version is not pinned, the bracket
loosening changes search-order weighting only, and the C-canon decision is deferred.

---

## C-nav — the navigation docs, kept true

Per `CLAUDE.md`'s four-doc rule (a result that lives only in its own folder is a result nobody will
find). Before this lane, **neither Round 19 nor Round 20 had a row** in the main round tables of
`ELIMINATION-LEDGER.md` or `analysis/README.md`; Round 19's synthesis lived only in `LEDGER.json`.

- **`ELIMINATION-LEDGER.md`** — added a Round 19 row (repair-the-instrument; I1/I2/I3 built,
  R1 found the round couldn't affordably sweep, canon upheld 450/450, 3 payload bytes corrected)
  and a Round 20 row (sieve INFEASIBLE, P-gate held, no S-lane scored, P3 PASS×3, R FOUND-ERROR
  latent, N1/N2 negative).
- **`analysis/README.md`** — added Round 19 + Round 20 folder-table rows pointing at the per-lane
  `RESULTS.md` and this file.
- **`README.md`** — added a "Latest rounds (2026-08)" block summarising Rounds 18–20 and linking
  `PICKUP-HERE.md`. The stable "Quick status" (OTP-class) is unchanged because it is still true.
- **`PICKUP-HERE.md`** (repo root, opened) — state of the board, what Round 20 shipped, the ranked
  open items for Round 21 (S-G3 is the cheapest and was authorised-but-not-run; fix the sieve ×
  panel-max FP inflation; reconsider the 0.90-at-100× bar), the C-canon governance item, the
  C-eyeball flag, and the do-not-re-run foreclosed list.

---

## C-eyeball — the one weak transcription candidate

**T1 p27:93, U→B, margin 5** is flagged for a human eye in `PICKUP-HERE.md`. Round 19's T1 upheld
canon 450/450 overall, but this cell's decision margin is thin. It wants a look at the actual glyph,
not another automated pass. Not load-bearing for any current verdict.

---

## C-canon — recorded, NOT decided

The 3 changed payload bytes (idx **45, 50, 246** → `payload_resolved.bin`, corrected by Round 19
C1) are **input-sensitive downstream**: **B-04** (its 6.22M-decode sweep keys/scores off the
payload), **R16-KDF** (692,064 configs consume the payload), and **R17** (public-pad branch, also
downstream). Promoting `payload_resolved.bin` to canonical would require re-checking each of those
three lanes against the new bytes and restating their `LEDGER.json` coverage.

Per PREREG Q5, Lane C does **not** decide this unilaterally. It is recorded for the coordinator as
`LEDGER.json:C-CANON-PAYLOAD-3BYTES` (status `open`, reopens when the coordinator promotes the
bytes) and surfaced in `PICKUP-HERE.md`. The canon files (`canon_256.bin` etc.) are **not** rewritten
by this lane.

---

## Files changed (no git commit — coordinator commits)

| file | change |
|---|---|
| `analysis/round18/L1-toolchain/RESULTS.md` | superseded-markers on F6 (46→56/54, twice-changed toolchain), F7 (bracket loosened), the §6.1 composite-inference line, the §6.2 rank-3 Perl prior (→Crypt::RSA), and the summary 46/46 line; a dated correction block under the intro. Old figures struck, not deleted. |
| `LEDGER.json` | +2 entries: `L1-PRIOR-PROPAGATION` (audit) and `C-CANON-PAYLOAD-3BYTES` (open); counts total 124→126. Unsound-negatives still 0. |
| `ELIMINATION-LEDGER.md` | +Round 19 and +Round 20 rows in the campaign/round summary table. |
| `analysis/README.md` | +Round 19 and +Round 20 folder-table rows. |
| `README.md` | +"Latest rounds (2026-08)" block. |
| `PICKUP-HERE.md` | **created** at repo root — opens Round 21. |
| `analysis/round20/C/PREREG.md`, `RESULTS.md` | this lane's pre-registration + results. |

No file outside the set above was modified. No `git commit` was made.

---

## Coverage × power (doctrine R2)

Lane C is not a search lane: it has **no key-space coverage and asserts no negative**, so a
coverage×power pair does not apply to it. The corrections it propagates carry the coverage and
power of *their source lanes* (C3's 228/228 PGP re-derivation; R1's four-field JPEG reproduction),
cited inline so a reader can trace each one. The one number that governs Lane C is the pair of
trust anchors, both green before and after: `validate.py` 5/5, `validate_ledger.py` Unsound = 0.

## Bounds, not verdicts (doctrine R7)

Nothing here is closed. The L1 prior's *conclusion* stands and sharpens; its *bracket* is looser
than published and its *counts* are corrected. The canon-payload question is open and deferred.
The transcription cell p27:93 is open pending a human. And the substantive Round-20 result — that
the sieve is infeasible at the 0.90-at-100× target, leaving the enumerable-PRNG families
built-but-unswept — is a **bound**, not a closure: S-G3 (authorised, unrun) is the cheapest reopener,
and any sieve reaching the target reopens the rest.
