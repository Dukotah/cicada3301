# Round 42 / S1 (+ S3) — S2 window-2 recovery and the bash 3.2 real binary: RESULTS

2026-11-02. `PREREG.md` written first. Sandbox: Vercel, project `skyfling`, team `dukotahs-projects`,
`create_sandboxes_v4` from the snapshot, 4 vCPU / 8 GB. Deadline beaten: the source snapshot
`snap_ff0SWU76EW32OqbWJvp00fnORypR` would have expired ~2026-11-06.

## S1 — window-2 recovery: SUCCESS (byte-exact)

The Round 38 S2 window 2 ran but its end state was unrecovered (laptop slept, 45-min session cap,
then Vercel Hobby quota 402 until 2026-11-01). Quota has since reset. Created sandbox
`r42-s1-recovery` from the snapshot; the whole window-2 work tree was intact at
`/vercel/w/run_r36` (mtime Oct 30 23:32, final).

- **STATUS.json** read back, saved locally, **sha256 `1aa529444548e3e1f3add420936ddfd40ee9b9fe4cb6d25b74c197a2e070c2ba`** (the local copy equals the sandbox file byte-for-byte).
- **No survivor.** `HIT-CANDIDATE.json` = `hits:[]`. Aggregate best pmax **7.3071** (seed 1087113973), below the 7.5342 near-miss bar and the 7.6342 claim bar. `n_claim_bar_hits: 0`.
- **Candidate distribution** (38,576 ≥ 5.0): 5.5 → 4,736; 6.0 → 487; 6.5 → 44; 7.0 → 5; 7.3 → 2; **7.5342 → 0; 7.6342 → 0**. Top seeds: 1087113973 (7.3071), 3905907872 (7.3007), 1774592253 (7.2853).
- **Coverage.** Engine cursor sum advanced 2,059,308,008 → **2,235,695,586** (47.947 → **52.054 pp** of 2³², +4.107 pp in window 2); mixed-instrument, same caveat as R38-S1. Window-2 panel-R36 seeds advanced = 176,387,578.

**Q5 success test met:** cursors monotone vs window 1, seeds_advanced internally consistent, candidate counts monotone. The Round 38 "window 2 unrecovered" caveat is closed; no survivor appeared.

### Export / durability
The MCP file channel caps ~2 KB per call (the same limit R38-S1 (c) hit), so the 2.4 MB
`candidates.jsonl` was **summarised**, not transferred byte-for-byte; STATUS.json and
HIT-CANDIDATE.json (small) were pulled whole and sha-verified. The full lists
(`candidates.jsonl`, `top_S2.json`, `hist_S2.u64`) are preserved three ways:
1. the original snapshot `snap_ff0SWU76EW32OqbWJvp00fnORypR` (expires ~2026-11-06),
2. a fresh manual snapshot **`snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6`** (expires **2026-11-09**),
3. the persistent sandbox `r42-s1-recovery:/vercel/w/S1-recovered/` (with `SHA256SUMS`).

Uncompressed shas (from the sandbox): STATUS `1aa52944..`, HIT-CANDIDATE `b05fd0ba..`,
candidates.jsonl `bd5c8289..`, hist_S2.u64 `60c1744a..`, top_S2.json `f60eece8..`.

## S3 — real bash 3.2 binary: SUCCESS (L4 → L1)

Built **bash 3.2.0(2)-release** from the pinned tarball `bash-3.2.tar.gz`
(sha256 `26c99025b59e3077..`, == round40 verification.json) under gcc 15.2. Three modern-toolchain
fixes were needed and are recorded for reproducibility: `-fcommon` (gcc-10 `-fno-common`),
`-fpermissive` (gcc-14/15 made implicit-function-declaration a hard error), and forcing
`HAVE_STRSIGNAL 1` in `config.h` (glibc ≥2.34 removed `sys_siglist`, which `siglist.c` used; configure
mis-detected). Binary sha256 `447a00e9a39adb9a..`.

- `RANDOM=1` first-20 = `[16838, 5758, 10113, 17515, 31051, 5627, 23010, 7419, 16212, 4086, 2749, 12767, 9084, 12060, 32225, 17543, 25089, 21183, 25137, 25566]` = round40 `verification.json` `first20_after_RANDOM_eq_1` **exactly (20/20)**.
- `RANDOM=1` mod-29 first-20 = `[18,16,21,28,21,1,13,24,1,26,23,7,7,25,6,27,4,13,23,17]`.

The 3.2 `$RANDOM` generator source (`variables.c` brand/sbrand) is unchanged across the 3.2.x patch
series, so a real binary L1-confirms the generator the campaign plan named as "3.2.57" as well.
**Effect:** `R40-B1-BASH32-RANDOM-AUTOSEED` flips **partially-run → negative** — its 76.2 M
enumerated auto-seed orbit (0 flagged) is now a real-binary negative. The pid_max>32768 and
subshell-reseed holes stand.

## Ledger
Two new rows (`R42-S1-S2-WINDOW2-RECOVERED`, `R42-S3-BASH32-BINARY-L1`, both measured) + two
patches (`R40-B1-BASH32` → negative; `R38-S1` note). `ledger_patches.json` + `apply_ledger.py`
(idempotent). LEDGER.json 301 entries, 0 errors, 0 unsound; counts recounted.

## Files
`PREREG.md`, `RESULTS.md`, `ledger_patches.json`, `apply_ledger.py`,
`state_recovered/{STATUS.json, STATUS.json.gz, HIT-CANDIDATE.json, candidates_summary.json}`,
`bash32_first20.json`.
