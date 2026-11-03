# Round 42 — SYNTHESIS (THE WASTING ASSET AND THE OPEN CELLS)

_Lanes run 2026-11-02 on the owner's laptop + the Vercel sandbox; X1 executed and closeout filed
2026-11-03. Plan of record: [`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine:
[`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Five lanes closed (S1, S3, C1, C2, C3, X1);
**S2 (PHP retry) and I1 (WATCH band + widened screen) never ran — they roll to Round 43.**
`LEDGER.json` **304 rows**, 0 errors, 0 unsound negatives; `tests/validate.py` passes; the full
non-network pytest gate **110 passed / 5 skipped**; `check_ceiling.py` PASS (125 rows, 110 pins);
X1 23/23 independent checks, 0 fails._

## 1. Verdict in one paragraph

No survivor. The round did what it pre-registered: it spent itself on the asset with a date on it
and the cells Round 41 proved were open. **S1 recovered the S2 window-2 end state byte-exact from
the expiring snapshot** (sha-verified STATUS.json): no survivor — best pmax 7.3071 vs the 7.5342
near-miss and 7.6342 claim bars, 0 claim-bar hits, cursor coverage 47.95 → **52.05 %** of 2³²
(mixed-instrument: only 7.9 pp of that is panel-R36-judged). The Round 38 "window 2 unrecovered"
caveat is closed. **S3 built the real bash 3.2 binary** from the pinned tarball — `RANDOM=1`
first-20 matches `round40/verification.json` 20/20, flipping `R40-B1-BASH32-RANDOM-AUTOSEED`
partially-run → **negative** (a real-binary L1 negative over its 76.2 M-seed orbit). **The three
artefact cells Round 41 carried as "blocked" all ran and all came back negative at full
12-register power:** C1 swept the 23 intact R35 keytexts (best 5.479 vs bar 17.42 — and found **10
of the 33 "keytexts" are corrupt globalgrey 404 pages**, classified out before scoring, recorded
as not-covered-pending-refetch); C2 swept the 523 MB of R36 dated pads as additive mod-29 pads
(best 5.003 vs 16.94); C3 re-derived the 43 auto keys from the present OSINT raw (MIDISCV +
WORKING reproduce) and re-scored the whole 184-key grid under panel-R36 (best 5.496 vs 17.09).
Cells H7×F4, H8×F4, H7×F9 and the 43-B1 cell move from blocked/legacy to **TRIED (panel-R36)**.
X1 re-derived every load-bearing number independently (23/23 PASS) and recorded one bounded
process deviation: the C lanes substituted the standing bar of record for fresh planted controls
(declared in their PREREGs before output; negatives sit 11–12 pmax units below bar — no verdict
flip, but future artefact lanes must plant through their own glue).

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| S1 | window-2 RECOVERED, no survivor | counting from sha-verified downloaded state only (X1) | +4.107 pp of 2³² in window 2 → 52.054 % total (mixed-instrument; 7.9 pp panel-R36) | best 7.3071 vs claim bar 7.6342, `hits:[]`; lists preserved in a fresh snapshot `snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6` (**expires ~2026-11-09**) + persistent sandbox `r42-s1-recovery`. |
| S3 | bash 3.2 L4 → **L1 negative** | first-20 vs `verification.json` 20/20 | the full 76.2 M auto-seed orbit, now real-binary | built 3.2.0 from the pinned tarball (sha matches) under gcc 15.2 (`-fcommon`, `-fpermissive`, forced `HAVE_STRSIGNAL`); `$RANDOM` source unchanged across 3.2.x. pid_max>32768 + subshell-reseed holes stand. |
| C1 | R35 keytexts **NEGATIVE** (panel-R36); H7×F4, H8×F4 → TRIED | standing instrument (deviation recorded, X1) | 23/33 texts × ~150 start offsets × 2 signs × 2 atbash × 55 pages, 12 registers | best 5.479 (`boehme_aurora`, p26) vs free bar 17.42, 0 crossers; **10 texts are corrupt 404 captures** → not-covered-pending-refetch. |
| C2 | R36 dated pads **NEGATIVE** (panel-R36); H7×F9 → TRIED | standing instrument (deviation recorded, X1) | 12 pad streams (Bitcoin-era + NIST beacon + random.org), 4 MB prefixes, ~150 offsets, both signs | best 5.003 (`hash_internal_2013`, p46) vs 16.94, 0 crossers — consistent with the doublet exclusion of additive full-entropy keystreams. |
| C3 | 43-B1 auto keys **NEGATIVE** (panel-R36); cell unblocked | MIDISCV + WORKING re-derive from the present raw | 485,760 decodes (184 keys × 2 × 2 × 12 phases × 55 pages), 12 registers | best 5.496 (`SHAMIRSSECRETSHARINGSCHEME`, p24) vs 17.09, 0 crossers; dominates the original English-only pass. |
| S2 / I1 | **NOT RUN** | — | — | the PHP tier retry and the WATCH-band wiring + widened (k≤3–4) head screen head Round 43; the whole B2 offset remainder stays gated behind I1(b). |
| X1 | 23/23 PASS, 0 fails; FOUND-DEVIATION ×1 (bounded) | independent re-hash/recount/re-derive | — | S1 counted from downloaded state; C-lane artefact provenance re-derived; bars sane; ledger 304==304; the no-fresh-plants deviation dispositioned (`X1-redteam/RESULTS.md`). |

## 3. What the board now says that it did not say yesterday

1. **The Round 38 S2 recovery debt is paid.** Window 2's end state is on the laptop, sha-verified,
   and it contains nothing: the 2³² derived-keystream space is now 52.05 % cursor-covered with zero
   claim-bar survivors. The deadline asset was recovered five days before it died.
2. **"Blocked" was a clone artefact, and the cells were empty.** All three zero-network artefact
   cells (R35 keytexts, R36 dated pads, 43-B1 auto keys) ran within one afternoon of being
   declared runnable — each a measured 12-register negative, each strictly dominating its
   English-only predecessor. The clue-coverage matrix loses four long-standing blocked/legacy
   entries.
3. **The R35 keytext corpus was partly rotten.** 10 of 33 files are globalgrey "Page Not Found"
   HTML, not esoterica — a stale fetch nobody had ever opened. The negative covers the 23 intact
   texts; the 10 need a hash-pinned refetch before anyone may quote that cell as fully covered.
4. **The bash 3.2 row is a real-binary negative now** (L1), closing the last open generator-identity
   question on that orbit short of the pid_max/subshell holes.
5. **A new expiry replaced the old one:** the full S1 candidate lists live sandbox-side under
   snapshot `snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6` until ~2026-11-09 (plus the persistent sandbox).
   Only summaries are local. Export or deliberately lapse — decide, don't drift.

## 4. Red-team findings

`X1-redteam/RESULTS.md` (+ `x1_verify.py`, `x1_output.txt`): every lane's headline number
re-derived from artefacts, 0 fails. One process deviation (no fresh plants through the C-lane
glue — bounded, dispositioned, binding guidance for future artefact lanes), plus the Round 43
critic list: the mixed-instrument split must travel with the 52.05 % figure; the 11-09 snapshot
decision; the standing-null caveat if any future cell lands near its bar.

## 5. Owner decisions pending (carried to Round 43, unchanged from Round 41 §5)

1. **WATCH band** (pmax > 7.10 → L=240 decode + human look) — gates I1(a); recommended before any
   mass sweep.
2. **R13 DIRECTION** open → negative.
3. **KDF noise-crosser** sign-off.
4. **`with_degenerate` SWEEPROW default**; the **N5/N4 L=240 bundle read**.
5. NEW: the **snapshot lapse decision** (§3.5) — export the S1 full lists before ~2026-11-09, or
   record the deliberate lapse.

## 6. Next

`analysis/round43/CAMPAIGN-PLAN.md` — the two lanes this round did not reach (the PHP tier retry;
the widened k≤3–4 head screen whose power measurement gates the 110.5-cell B2 offset remainder),
the WATCH band if adopted, the R35 corrupt-text refetch, and the R44-expand control redesign.
