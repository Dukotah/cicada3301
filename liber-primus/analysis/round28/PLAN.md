# ROUND 28 — PLAN (planning gate, 2026-09-08)

_Charter (owner): keep exhausting every remaining runnable option with current technical
abilities, optimistically — treat every lane as if the key IS inside it and build so a hit
cannot be missed; the deliverable either way is a checked-off box future researchers can trust._

Binding doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Trust anchor
`python3 tests/validate.py` must stay 5/5 before and after every lane. Standing verdict under
test (not re-derived): **LP2 0–54 is OTP-class** (`LEDGER.json:VERDICT-OTP-CLASS`, 157 entries).

## Hard operational constraints (all lanes)

- **DO NOT DISTURB S2.** `grind27` (PID in `../round27/sweep.pid`, verified alive at planning
  time) is sweeping the full 2³² 'exact' cell on all 6 cores. Nothing in this round touches the
  sweep process or `../round27/P1-engine/run/`. All Round-28 compute runs `nice -n 15` and
  **single-threaded**; multi-thread bursts <1 min are allowed for builds only. Full-space
  2³²-class sweeps are **QUEUED** until S2 exits (lane L4).
- Anti-repeat is proven per lane against `LEDGER.json` `coverage`/`not_covered` (never bare
  `status`); each PREREG names the ledger ids it extends.
- Plant-and-recover positive control (≥0.90 recovery, HIT=True) validated **before** any null
  counts, per lane and per cell.
- Any bar-clearing survivor is **FLAGGED-FOR-ORACLE, never auto-certified** (R21-L1: the
  no-oracle seal is provably leaky). Adjudication of record: Python re-score parity →
  `../round20/HITFN/hitfn20.py` 3-clause gate with `../round19/I2/adjudicate.py`, following the
  `../round27/oracle_crosser.py` pattern.
- Every negative names its **3 conditionals** (key space / decoder transition model /
  adjudicator register) and reports **coverage × power**, with the un-swept remainder in
  `not_covered`. Bounds, not verdicts (doctrine R7).
- Git: commit to `master` only, explicit paths only, never `git add -A`, no push.

## Slate decisions (owner candidates + 2 additions)

| id | lane | verdict | mode | one line |
|---|---|---|---|---|
| **L1** | cicadaos-pads | **RUN** (re-scoped) | run-now-light | P-3 as written is **stale**: the "never-performed" A1 re-run on the authoritative pads WAS run 2026-08-19 (`../round12/A1/results_560_13.json` 160 configs / 8 offsets; `results_560_00_full.json` 220 configs / 11 offsets; both NEGATIVE, absorbed into ledger row `R12-A1`). What is genuinely uncovered: **offset density** (8 sampled positions on a 118.8 MB pad), the **keyskip2/pair relation** (prior runs were keyskip1-beam only), and the **hitfn20 N-scaled gate** (prior runs used a fixed −5.5 bar). L1 sweeps exactly those axes on one throttled core. |
| **L2** | contested-bytes | **RUN** | run-now-light | The 6 contested canon_256 cells (idx 25,175,182,199,215,237) have never been adjudicated — `B-05` covers them only as a *sensitivity dimension*, and P-7's cheap variant-enumeration was never run either. Build a same-page template-match reader (control: 100/100 blind reproduction of uncontested cells), enumerate the reading-variant Cartesian product through `../pp49_51/keytest.py` with a variant-count-corrected bar, and re-run the battery on any corrected stream. |
| **L3** | string-seed-dictionary | **RUN** | run-now-light | Pinned exact Py2.7 `seed(str)` semantics: `PyObject_Hash` (pre-randomization ×1000003 string hash) → abs → `init_by_array(words)`. **New closure claimed:** the i386 (32-bit hash) image is a subset of [0,2³²) ⇒ already fully excluded by R27-S1 (pair, measured-exhaustion NULL) and by S2 on completion (exact) for {random29, offset 0} — zero compute, documented subsumption (red-team lane verifies it empirically). The runnable extension is the **amd64 64-bit hash image** — not subsumed (`R21-L3` NC-2) — over a ~10⁵–10⁶-entry dictionary via the validated `../round19/G3/gen_py27.py` wordsize=64 path. Round 8's `string_seeds.py` demonstrably never used Py2 semantics (it seeds the running Py3 interpreter), so this is the first true run of R18-L1's promoted family. |
| **L4** | unswept-generators | **RUN** | build-now-queue-heavy | Build `grind28` (separate binary; grind27 sources untouched) for: PHP `mt_rand` **canonical + pre-7.1 broken variant** — the P-4 blocker has evaporated: `/usr/bin/php` 8.5.4 is on the box and exposes both modes (`MT_RAND_MT19937`, `MT_RAND_PHP`), verified emitting distinct streams at planning time; glibc `rand`/`random` incl. the open `gen=0` full-2³² row (`R19-G3-CORRECTION`); and the R27-PREREG S3 cells (grb5_mod/grb5_rej/shuffle29 × offsets {1,3,5,7,13} × pair). The tasking's "wordsize-64" S3 cell is a **no-op for integer seeds** (`../round27/PREREG.md` S3: wordsize only enters string hashing) — dropped with citation; its live content is L3's string path. NOW: vectors + planted controls + null micro-samples at nice-15 single-thread. QUEUED post-S2: the full 2³² sweeps. |
| **L5** | payload-micro (ADDED) | **RUN** | run-now-light | The never-run RECON-A minutes-of-compute items on the 256-byte payload: **E-01** (payload as RSA signature/ciphertext under every published 3301 modulus, both endiannesses, PKCS#1 v1.5 / PSS pattern match — zero-false-positive), **E-02** (56-byte permutation-window scan + gap-value rank-correlation vs the real doublet gaps), **H-03** (2013 onion cookies XOR'd against the four hex strings; 2012 P.S. rotate-90 reading). All listed in `handoff/PARKED.md` "Not parked — merely unfinished"; no ledger row covers them. Re-runs on L2's corrected stream if any byte flips. |
| **R** | red-team (ADDED) | **RUN** | run-now-light | Doctrine R6 mandates a standing red-team lane; the owner slate had none. Targets: (1) `R12-A1`'s `not_covered: null` despite 8-offset sampling of a 118.8 MB pad (candidate doctrine-R7 defect) + the stale P-3 text in PARKED.md; (2) recompute S1-CLOSEOUT's headline claims from artifacts; (3) L3's subsumption claim, verified empirically (≥100 dictionary words: i386 py2-hash keystream ≡ `init_by_array([w])` keystream); (4) PREREG-vs-code drift across L1–L5 (the R26-D lesson). Reports FOUND-ERROR / NO-ERROR-FOUND only. |

**No KILLs.** All four owner candidates survive the ledger check as genuinely (or partially)
un-run; L1 required re-scoping rather than killing. The two permitted additions are spent on
L5 (cheap, never-run, bounded) and R (doctrine-mandated).

## Budget vs doctrine §3

- ~30% instrument: L2's template reader + control, L4's vectors/planted controls, L3's
  hash-image pinning vectors.
- ~40% high-prior bounded: L3 (R18-L1 promoted family, first true run), L4 (PHP = the census's
  highest-prior open generator, now validatable), L1 (author's own artifact, finite).
- ~20% red-team: lane R.
- ~10% completeness: L5, plus L1's fine-grid remainder honestly left in `not_covered`.

## Sequencing

1. `python3 tests/validate.py` (5/5) gates everything.
2. L5, L2, R start immediately (cheapest first; L5 is minutes).
3. L1 and L3 run their planted controls, then their single-core throttled sweeps (6–10 h each,
   they may run on different single cores concurrently — total load stays ≤2 cores at nice 15,
   leaving S2's 6 workers dominant).
4. L4 builds + validates now; its heavy queue file (`L4/QUEUE.md`) executes only after
   `ps -p $(cat ../round27/sweep.pid)` shows S2 exited AND S2's closeout (batch parity +
   planted control) has been run per `PICKUP-HERE.md`.
5. Closeout: per-lane RESULTS.md, ledger rows with coverage×power + 3 conditionals, nav-doc
   updates, single explicit-path commit.

## What this round cannot touch (stated up front)

The `/dev/urandom` / true-external-pad branch (majority of honest prior mass) is unreachable
by every lane here, as always. A clean sweep of all six lanes **hardens** the OTP-class
verdict; it does not close the book. Bounds, not verdicts.
