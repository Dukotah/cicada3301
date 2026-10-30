"""X1/R36: nav-doc edits (idempotent). Run from cicada3301/ (repo root)."""
import io

def edit(path, old, new, count=1):
    t = io.open(path, encoding="utf-8", newline="").read()
    if new in t:
        print("already", path); return
    assert t.count(old) >= 1, (path, old[:60])
    t = t.replace(old, new, count)
    io.open(path, "w", encoding="utf-8", newline="").write(t)
    print("edited", path)

# ---------------- liber-primus/PICKUP-HERE.md
P = "liber-primus/PICKUP-HERE.md"
old = "> ## Round 35 (2026-10-30) — THE SKIP-TOLERANT SCREEN: shipped. Read `analysis/round35/SYNTHESIS.md` first."
new = """> ## Round 36 (2026-10-30) — THE 12-REGISTER PANEL, THE RE-GATE, AND THE CLUE AUDIT: filed (B1 still sweeping at X1's audit). Read `analysis/round36/X1-redteam/RESULTS.md` first.
>
> No survivor, no crosser. **I1** Greek/Hebrew/Norse registers pass the power gate (1.000 at L=120/240) and no existing register loses power.
> **P1** panel-R36 (12 registers, built from disk, 53 hashed inputs, byte-reproducible under three hash seeds, sha `a0682f0c…`) is the recorded S2 gate;
> the Round 19 gate is retired (`P1-panel-r36/GATE-CHANGE.md`: S2 rows after it are a NEW measurement). **S1** engine self-test 64/64 exact, then one 35-min sandbox
> window: **+54,967,546 seeds, 0 crossers, best 7.1256** — but the 45.418 % cursor coverage is MIXED-instrument (44.138 % Round 19-gated + **1.28 % panel-R36**).
> **B2** the four PHP cells re-run awake with rows persisted: 0 flagged, best 6.608 vs 7.941; its tier-b seeds are the first 199 blocks of the SAME
> `default_rng(3301)` stream R32-B2 already drew 318 blocks from (no new key space, higher screen power). **I2** pf_v4 power ≥0.94 on ILP32/PHP. **I3** the two-margin D5c rule
> FAILS at L=150 (SEAL_PASS=false; pause seal work). **O3** the recurring near-miss (bash 4.2 seed 1354603465, 7.068) is the order statistic of the sweep (NOISE; held-out windows at null level).
> **O2** no alternate-format source found (Wayback leg unsearched). **O4** clue-coverage matrix: 68 NEVER cells of 140 applicable (X1: ≥2 misclassified), 53 English-only/legacy; top untried readings in `O4-clue-coverage/untried.md`.
> **X1** found hash-seed-dependent Hebrew mapping in I1, the mixed-instrument S1 wording, B2's wrong patch id and shared seed stream, two O4 cells.
> **Next (Round 37):** see `analysis/round36/X1-redteam/RESULTS.md` section 7 (U1–U3 composed clue readings; re-score the R10/R11/R22-C streams under the 12-panel; S2 windows; PHP remainder; deferred tooling fixes).
>
> ## ~~Round 35~~ (2026-10-30) — THE SKIP-TOLERANT SCREEN: shipped (the "Next:" at its end is superseded by Round 36 above). Read `analysis/round35/SYNTHESIS.md` first."""
edit(P, old, new)

# ---------------- ELIMINATION-LEDGER.md
P = "liber-primus/ELIMINATION-LEDGER.md"
old = "## Round 35 — THE SKIP-TOLERANT SCREEN (2026-10-30)"
new = """## Round 36 — THE 12-REGISTER PANEL AND THE RE-GATE (2026-10-30)

Rows `R36-*` in `LEDGER.json` (I1, I2, I3, P1, S1, B2, O2, O3, O4, X1 filed after refute-by-default audit; B1 was still sweeping at audit time). Full write-up `analysis/round36/X1-redteam/RESULTS.md`.
- **R36-I1** Greek (Nestle 1904), Hebrew (WLC, pointed) and Norse (heimskringla) registers: power 1.000 at L=120/240; nine existing registers unmoved. **X1:** the Hebrew mapper iterates python sets, so I1's own `panel12.npz` is hash-seed dependent (superseded by panel-R36).
- **R36-P1** panel-R36 (`panel12.npz` a0682f0c…, 12 registers, 53 hashed inputs, byte-identical under PYTHONHASHSEED 1, 2 and X1's 7) replaces the unrebuildable Round 19 gate; GATE-CHANGE.md records S2 after the change as a NEW measurement. CY remains the modern-Welsh substitute.
- **R36-S1** C engine self-test V1 64/64, V2 17.931158509762; S2 window +54,967,546 seeds (**1.28 % panel-R36**; the 44.138 % before it stays Round 19-gated, so the 45.418 % cursor figure is mixed-instrument), 0 claim-bar crossers, best 7.1256. Live `run/` untouched; state_after resumable; window lists only in sandbox snapshot (expires ~2026-11-06).
- **R36-B2** PHP mt_rand 4 cells awake, pf_v4 + v3, 263,906 rows persisted: 0 flagged (best 6.608 vs 7.941). Tier b (0.6073 %/cell) is a SUBSET of R32-B2's draw (same `default_rng(3301)` stream); **not** new seed coverage. **R36-I2** pf_v4 power ≥0.94 on ILP32/PHP, FPR 6.6e-4–9.6e-4. **R36-I3** two-margin D5c rule FAILS at L=150: SEAL_PASS=false.
- **R36-O3** the recurring near-miss seed 1354603465 (7.068) is NOISE (family-wise P≈0.20; held-out windows 1.73 vs null median 2.19; plants read verbatim). `free` relation needs an L-matched null before it can be evidence. **R36-O2** no source artifact found (partially-run; Wayback unsearched). **R36-O4** clue x reading-family audit: 68 NEVER of 140 applicable cells (X1: ≥2 misclassified); 53 English-only/legacy cells.
- **R36-X1** FOUND-ERROR (minor): I1 reproducibility claim, P1 build_twice records no seeds and 5 unresolvable Norse paths, S1 mixed-instrument coverage, B2 patch id + shared stream, O4 H7/H12 x F2. NO-ERROR-FOUND elsewhere (see RESULTS).

## Round 35 — THE SKIP-TOLERANT SCREEN (2026-10-30)"""
edit(P, old, new)

# ---------------- analysis/README.md
P = "liber-primus/analysis/README.md"
old = "| [`round35/`](round35/) |"
new = ("| [`round36/`](round36/) | **Round 36 — THE 12-REGISTER PANEL, THE RE-GATE AND THE CLUE AUDIT (10 lanes; no survivor; B1 sweeping at audit) 2026-10-30** | **I1** Greek/Hebrew/Norse registers, gate 1.000, nine unmoved. **P1** panel-R36 (a0682f0c…) replaces the unrebuildable Round 19 gate (`GATE-CHANGE.md`). **S1** engine self-test 64/64 + one S2 window (+54.97 M seeds, 0 crossers; 1.28 % panel-R36, 45.418 % mixed-instrument). **B2** PHP mt_rand awake, 263,906 rows, 0 flagged (tier b ⊂ R32-B2's seed stream). **I2** pf_v4 ≥0.94 on ILP32/PHP. **I3** two-margin D5c FAILS at L=150. **O2** no source artifact (Wayback unsearched). **O3** near-miss 1354603465 = NOISE. **O4** clue x family matrix (68 NEVER cells). **X1** red-team: hash-seed-dependent Hebrew mapper, mixed-instrument S1 wording, B2 patch id/shared stream, O4 cell misclassification; Round 37 list. | "
       "[`CAMPAIGN-PLAN.md`](round36/CAMPAIGN-PLAN.md), [`X1-redteam/RESULTS.md`](round36/X1-redteam/RESULTS.md), [`P1-panel-r36/GATE-CHANGE.md`](round36/P1-panel-r36/GATE-CHANGE.md), [`O4-clue-coverage/untried.md`](round36/O4-clue-coverage/untried.md) |\n"
       "| [`round35/`](round35/) |")
edit(P, old, new)

# ---------------- README.md (root)
P = "README.md"
old = "*Status current as of 2026-10-30 (Round 34 merged; **Round 35 partially filed**"
new = ("*Status current as of 2026-10-30 (**Round 36 filed, B1 still sweeping**: a 12-register panel (Greek/Hebrew/Norse added) is now the recorded S2 gate, replacing the unrebuildable Round 19 panel; one S2 window ran on a sandbox (+55 M seeds, 0 crossers); the PHP tier was re-run awake with rows persisted; the recurring near-miss is noise; a clue-coverage audit lists the readings never run under the repaired instrument; X1 red-team found and recorded the errors in "
       "[`liber-primus/analysis/round36/X1-redteam/RESULTS.md`](liber-primus/analysis/round36/X1-redteam/RESULTS.md)). Earlier: Round 34 merged; **Round 35 partially filed**")
edit(P, old, new)
