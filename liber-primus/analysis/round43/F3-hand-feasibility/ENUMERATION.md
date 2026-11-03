# R43 F3b — Hand-Executability Enumeration (the 13k-glyph physical constraint)

**Date:** 2026-11-03 · **Lane:** F3b-scheme-enumeration
**Constraint being filed for the first time:** the Liber Primus is hand-illuminated. ~13,000 rune
encipherments were executed in 2013/14 by a human, or from a human-prepared printed pad. Any
candidate scheme must be runnable at that scale with paper tools, and its statistical output must
match the book. This document enumerates every hand-executable scheme family, **computes** (not
asserts) its statistical fingerprint at 13k-glyph scale, and scores feasibility × consistency.

All statistics below were computed fresh from `data/krisyotam_runes.txt` by
`simulate_hand_schemes.py` (committed beside this file, seed=43) and the inline analyses logged in
this round. No prior project measurements were consulted (firewall condition).

---

## 1. The measured target (what any scheme must reproduce)

Corpus: `data/krisyotam_runes.txt`, 57 `%`-separated pages. Page 57 decodes directly to English
("PARABLE…") and is excluded. **Unsolved pool: 56 pages, 13,041 runes, 2,953 words (mean 4.42
runes/word).**

| statistic | LP measured | uniform-random expectation |
|---|---|---|
| monographic IoC (×29) | **0.9998** | 1.0 (chi² 25.9 on df 28 — *perfectly* uniform) |
| lag-1 coincidence (doublets) | **0.678 % (88/12,985)** | 3.448 % → **z = −17.4** |
| … within words | 0.640 % (z = −15.5) | 3.448 % |
| … across word separators | 0.838 % (z = −7.5) | 3.448 % |
| … across line breaks | 0.767 % (z = −2.9, n=391) | 3.448 % |
| … across page boundaries | 0/55 | 3.448 % |
| lag-2…15 coincidence | 2.97–3.65 %, all &#124;z&#124; ≤ 2.9 | 3.448 % — **flat** |
| periodic IoC, p = 2…200 | max 1.018 (inside uniform null 1.021) | — **no periodicity** |
| periodic IoC with per-page reset, p ≤ 60 | max 1.0076 | — no page-reset key |
| difference stream Δc = c_{i+1}−c_i | IoC **1.0243**; chi² 343 **entirely** in the Δ=0 deficit (z=−17.3); all other 28 buckets uniform (only Δ=9 at z=+3.2) | 1.0 |
| sum stream c_i+c_{i+1} | IoC 0.9997 | 1.0 |
| second difference | IoC 1.0003 | 1.0 |
| bigram IoC (×841) | 1.0253 | doublet-suppressed-uniform null: 1.0231 ± 0.0038 → **z ≈ +0.6, no digraph structure** |
| per-page doublet dispersion | chi² 61.6 / df 55 — homogeneous; doubled symbols spread over 28 of 29 runes | one mechanism, whole book |
| repeated words (len ≥ 3) | 15 types, max ×3 (chance level) | English at same scale: 2,703 tokens in repeated types |

**Summary of the object:** to measurement, the unsolved section is an i.i.d.-uniform 29-symbol
stream with exactly one anomaly — a deep lag-1 repeat deficit (80 % of expected doublets missing),
homogeneous across all 56 pages and across every layout boundary, whose missing probability mass is
redistributed **evenly** over all 28 non-zero deltas.

**Control:** the solved LP1 pages (01, 03, 04, 05, 06) show doublet rate **2.64 %** (z = −1.8,
normal for mono/Vigenère ciphertext of English), and the hand-drawn *plaintext* Parable page
contains a doubled rune (NN in TUNNEL). The suppression is therefore **intrinsic to the unsolved
section's cipher**, not a scribal drawing habit.

## 2. English-in-runes baseline (plaintext model for all simulations)

KJV transliterated through the Gematria Primus (greedy multigraph parse, 837k runes):
IoC 1.808; doublet rate 3.02 %; freq(F)=2.95 %, freq(EA)=0.63 %; delta distribution
P(Δp=d) ranges **1.40 %** (d=4) to 8.27 % (d=16); delta self-collision Σ P(d)² = **4.10 %**.

---

## 3. Two computed closure theorems

These close entire families at once; individual rows below reference them.

**T1 — the smearing bound (kills all independent keystreams).** For any position-wise additive
scheme c_i = p_i ± k_i with keystream independent of plaintext:
P(doublet) = Σ_d P(Δk=d)·P(Δp=−d). Since the plaintext delta distribution's smallest bucket is
1.40 %, the minimum achievable rate is 1.40 % — attained only by a **constant** Δk (a progressive
cipher, which is separately killed by its period-29 IoC spike, measured 1.90 at p=29). Any
non-degenerate Δk mixes toward 3.4 %. LP measures 0.678 % ± 0.072 → the entire family is excluded
at **z ≤ −10**, *without enumerating members*. This kills in one stroke: uniform OTP (dice, cards,
deck-PRNGs incl. Solitaire), human-generated pads (a pad's own repeat-avoidance does **not**
transfer through addition — simulated: 3.56 %), prime/totient/Fibonacci/π-digit/calendar/
chain-addition streams, running keys from any book, Gronsfeld, and all periodic polyalphabetics.

**T2 — the difference-stream kill (kills all static lag-1 feedback).** For any
c_i = c_{i−1} + f(p_i) with a fixed table f (any sign, any added constant): Δc = f(p) + const, so
IoC(Δc) = IoC(plaintext) ≈ 1.8 (measured 1.904 in simulation). LP measures IoC(Δc) = 1.024 with the
excess entirely in the Δ=0 deficit → the whole running-sum/ciphertext-autokey-lag-1 family with a
static inner table is dead, including the striking near-miss `running-sum+1` (its doublet rate
0.78 % ≈ freq(EA) matches LP, but its D-stream betrays it). The sum-stream (IoC 0.9997) kills the
Beaufort-feedback mirror c_i = k − c_{i−1} + f(p_i) the same way.

---

## 4. The enumeration table

Simulation: 13,100 glyphs of KJV-in-runes, one run per scheme (binomial noise on doublet % ≈
±0.16 pp). LP pass bands (≈3σ): IoC 1.000±0.025 · dbl 0.68±0.25 · lag2 3.44±0.5 · maxPer(2..60)
≤1.015 · D-IoC 1.024±0.03 · bigIoC 1.025±0.012.

Columns: **(a)** ops/glyph and projected hours at 13,041 glyphs (model: lookup/addition ≈ 4–8 s
each; mod-29 reduction of a 5–6 digit number ≈ 30–60 s; historical trained-clerk error 0.2–1 % per
glyph, untrained 1–3 %; error class L=local, S=self-synchronizing for the solver, C=catastrophic
for the solver) · **(b)** measured statistics vs target · **(c)** physical key artifact ·
**(d)** falsifiable fingerprint · **F**easibility /10 · **C**onsistency /10.

| # | scheme | (a) ops/glyph · hours · errors | (b) measured (IoC / dbl% / lag2% / maxPer / D-IoC / bigIoC) | (c) key artifact | (d) fingerprint | F | C |
|---|---|---|---|---|---|---|---|
| 1 | Monoalphabetic (shift/Atbash/keyed) | 1 · ~25 h · L | 1.904 / 6.63 / 6.44 / 1.91 / 1.09 / 3.63 — **dead (IoC)** | 1 card | English IoC survives | 10 | 1 |
| 2 | Homophonic 29→29 (disjoint sets, proportional; rotate or random choice) | 1–2 · ~30 h · L | 1.260 / 2.13–2.39 / 1.47–2.74 / — / 1.07 / **3.37** — **dead (4 axes)**; 29 symbols cannot flatten a 29-letter plaintext | 1 card | bigram IoC ≈ 3.4; lag-2 *suppressed* (LP's is flat) | 8 | 2 |
| 3 | Nomenclator / static codebook (words→rune groups) | ~1 lookup/word · ~15 h · L | repeated words ⇒ repeated groups; LP has **zero** excess word repeats (15 chance types vs 2,703 English tokens) — **dead** | booklet (~3k entries) | word-repeat census | 6 | 1 |
| 4 | Vigenère, short key (tableau/slide/volvelle) | 2 · ~30 h · L | 1.345 / 3.44 / 3.89 / **1.91@28** / 1.03 / 2.46 — **dead (period + IoC)** | 1 tableau sheet | periodic IoC spike at key length | 9 | 1 |
| 5 | Vigenère + F-interrupters (the solved-page system) | 2 · ~32 h · L | 1.176 / 3.54 / 3.79 / 1.20 / 1.02 / 1.75 — **dead (IoC, bigram)** | tableau | residual periodicity + elevated IoC | 9 | 2 |
| 6 | Quagmire I–IV / mixed-alphabet periodic, period ≤ 200 | 2 · ~35 h · L | fixed alphabet per column ⇒ column IoC 1.8; LP periodic IoC flat to p=200 (max 1.018, null 1.021) — **dead** | 1–2 cards | periodic column IoC | 8 | 1 |
| 7 | Double Vigenère (two keys, lcm ≤ 200) | 4 · ~60 h · L | = single key at lcm; flat-to-200 scan — **dead**; lcm > 200 ⇒ key material > 200 glyphs ⇒ merges into pad family (T1) | 2 cards | periodic IoC at lcm | 8 | 1 |
| 8 | Trithemius / progressive key (any constant step) | 1 · ~22 h · L | 1.000 / 3.54 / 3.13 / **1.90@29** / 1.27 / 1.27 — **dead (period 29)**; best-case doublet floor 1.40 % (T1) still 10σ high | nothing | period-29 IoC spike | 9 | 1 |
| 9 | Progressive keyword (key L, +1/cycle) | 2 · ~32 h · L | 1.000 / 3.34 / 4.12 / 1.13 / 1.03 / 1.03 — **dead (doublets, lag2)** | 1 card | doublets ~3.4 % | 9 | 1 |
| 10 | Alberti disc, new shift per word (incl. word-level autokey) | 1–2 · ~28 h · L | 1.000 / 2.98 / 4.10 / 1.01 / **1.24** / 1.24 — **dead (within-word doublets = plaintext's 3.1 %; LP within-word 0.64 %)** | 1 disc | within-word doublet rate | 9 | 2 |
| 11 | Gronsfeld on printed digits of π/e/√2 (shifts 0–9) | 2 · ~30 h · L | **1.035** / 3.30 / 3.76 / 1.90@20 / 1.02 / 1.29 — **dead (IoC, period-20 echo, doublets)** | digit book (~10 pp) | only 10 of 29 shifts used ⇒ elevated IoC | 8 | 2 |
| 12 | π in base 29 as keystream | base conversion of 13k digits by hand — **infeasible** (long division chains, C errors) | would be flat / 3.45 — **dead (T1)** anyway | — | T1 | 1 | 3 |
| 13 | Running key from an English/Latin book | 3 · ~45 h · L | **1.076** / 3.61 / 3.53 / 1.08 / 1.00 / **1.21** — **dead (IoC, doublets, bigram)** | tableau + the book | IoC ≈ 1.08, kappa vs book | 8 | 2 |
| 14 | Running key from a *flat* source (earlier LP ciphertext pages keying later ones; previous-page-derived pads) | 2–3 · ~40 h · L | flat IoC ✓ but independent flat stream ⇒ doublets 3.45 % — **dead (T1)** | the book itself | cross-correlation between sections (also: predicts inter-page kappa, measured flat) | 8 | 3 |
| 15 | Plaintext autokey (primer, any lag) | 2 · ~32 h · L | 1.083 / **4.11** / 3.62 / 1.09 / 1.01 / 1.24 — **dead (doublet *excess* = Δp self-collision 4.10 %, measured)** | 1 card | doublets ↑ not ↓ | 8 | 1 |
| 16 | Ciphertext autokey, lag ≥ 2 | 2 · ~32 h · S | 1.000 / 3.46 / 3.62 / 1.008 / 1.00 / 0.995 — everything flat ✓ **except doublets** — dead on the one axis | 1 card | doublets 3.4 % | 8 | 2 |
| 17 | Running gematria sum (ct-autokey lag 1), ± variants | **1 · ~20 h · S** | 0.999 / 2.86 / 1.98 / 1.006 / **1.90** / 1.90 — **dead (T2)** | nothing | D-stream = plaintext | 9 | 3 |
| 18 | Running sum + constant (c=c+p+1) | 1 · ~20 h · S | 1.001 / **0.78** ✓ / 2.57 / 1.011 / **1.90** / 1.90 — doublets *match* (= freq(EA) 0.63 %) but **dead (T2, lag2)** | nothing | D-stream = plaintext | 9 | 3 |
| 19 | φ(prime) stream, AN-END system extended book-wide | ~3 + mod-29 of 6-digit primes · **~140 h** · L (printed prime table) or ~35 h from a pre-reduced pad | 1.002 / **3.28** / 3.55 / 1.013 / 1.03 / 1.03 — flat everywhere ✓, **dead on doublets** (predicted 2.83 % from prime-gap × Δp convolution, simulated 3.28 %) | prime table to 139,409 (~30 pp) | doublets; kappa vs the known stream | 6 | 3 |
| 20 | Totient φ(n) stream | factoring every n ≤ 13k · ~200 h · L | 1.001 / 3.66 / 3.56 / 1.05 / 1.00 / 1.01 — **dead (doublets, T1)** | factor table | T1 | 4 | 3 |
| 21 | Fibonacci mod 29 | 1 add · ~22 h · C | **Pisano period 14** ⇒ maxPer 1.91@28 — **dead (periodicity)** | nothing | period-14/28 spike | 9 | 1 |
| 22 | Lagged Fibonacci / VIC chain addition (width ≥ 5) | 2 adds · ~30 h · **C** (a generation slip desynchronizes every later solver reconstruction) | 1.000 / 3.50 / 3.57 / 1.009 / 1.00 / 1.00 — flat ✓, **dead on doublets (T1)** | seed only | T1 | 8 | 3 |
| 23 | Calendar/date/moon streams | 1–2 · ~25 h · L | values cycle with period ~29–31 ⇒ near-period spike + T1 — **dead** | almanac | periodicity + T1 | 9 | 1 |
| 24 | Card-deck PRNG (Solitaire/Pontifex mod 29) | ~15 · **>110 h** · C | stream ≈ uniform ⇒ doublets 3.4 % — **dead (T1)**; also slow and state-fragile | deck | T1 | 3 | 3 |
| 25 | Dice/deck uniform OTP (pad written, then added) | pad gen ~12 h + 2 ops · ~45 h total · L | 1.000 / **3.41** / 3.44 / 1.013 / 1.00 / 1.00 — matches everything **except doublets, z=−17** — **dead** | ~25 pad sheets | doublets exactly 1/29 | 7 | 3 |
| 26 | OTP with *human-generated* pad (humans avoid repeats) | as 25 | 1.000 / **3.56** / 3.63 / 1.010 / 1.00 / 1.00 — pad's repeat-avoidance does **not** survive addition (smearing) — **dead** | pad sheets | doublets 3.4 % despite avoider pad | 7 | 3 |
| 27 | Pure transposition (columnar, double, grille, route, rail) | ~0.5 · ~15 h + grids · L | marginals preserved: 1.904 — **dead (IoC)**; also doublets 6.6 % (Σf²) | grid/grille card | English IoC | 7 | 1 |
| 28 | Substitution → transposition hybrids | 3–4 · ~50 h · L | transposing any flat stream restores doublets to Σ(1/29)² = 3.45 % — **dead**: the doublet deficit *proves no transposition is the final layer* | cards | doublet restoration | 7 | 2 |
| 29 | Bifid 6×6 (29+fillers), any period | 3 · ~45 h · L | 1.223 / 3.55 / 3.96 / 1.42 / 1.01 / 1.70 — **dead (IoC, period, bigram)** | 1 grid | fractionation leaves period + bigram echo | 7 | 1 |
| 30 | Hill 2×2 mod 29 | 6 mults+adds · ~90 h · L | 1.097 / **5.93** / 3.52 / 1.17 / 1.06 / 2.80 — **dead** | matrix card + mult table | digraphic repeats | 4 | 1 |
| 31 | Digraphic table 29×29 (841-cell sheet, even designed never to emit doubled pairs) | 1 lookup/2 glyphs · ~25 h · L | 1.091 / 1.56 / 3.65 / 1.18 / 1.08 / **2.85** — **dead (bigram IoC; LP has none)** | 1 large sheet | aligned-pair IoC | 6 | 2 |
| 32 | VIC full (straddling checkerboard + chain addition + digit regrouping) | ~6 · ~90 h · C | digit layer has no canonical 29-map; any additive recombination falls under T1 — **dead** | checkerboard card | T1 | 4 | 2 |
| 33 | Chaocipher-29 (two evolving rings, Byrne mechanics) | ~6 incl. two ring permutations · ~70 h · **C** | 1.000 / **3.37** / 3.40 / 1.006 / 1.00 / 1.00 — *every* axis flat ✓ (the twizzle is a superb whitener) — **dead on doublets alone** (z≈+17); dynamic tables per se do not suppress repeats | 2 sliding alphabets | doublets 3.4 %; state-fragility | 5 | 4 |
| 34 | Scribal aesthetic no-doublet drawing rule (over any system) | free | **killed by controls**: solved pages drawn by the same hand show 2.64 % doublets; the plaintext Parable page contains NN | — | solved-page doublet census | 10 | 1 |
| 35 | **Flat keystream + ciphertext no-repeat rule, ~80 % compliance** ("if the rune I am about to write equals the previous one, take the next key symbol / redraw") | 2–3 (+1 comparison) · ~35–50 h · L/S | **1.000 / 0.695 / 3.38 / 1.009 / 1.023 / 1.0229 — matches ALL six axes within noise** | pad sheets *or* arithmetic stream | compliance ≈ 80 % fitted (88 observed vs 448 expected collisions); predicts collision-skip alignment recoverable by beam search | 7 | **10** |
| 36 | **φ(prime) stream + no-repeat rule (80 %)** — Cicada's own AN-END stream plus an interrupter-like skip | as 19 + 1 comparison | **1.000 / 0.725 / 3.28 / 1.006 / 1.042 / 1.039 — matches all axes** (D-IoC at band edge) | prime table | given the stream, skip positions are *deterministic* ⇒ directly decodable by skip-beam | 6 | 9 |
| 37 | **Strict no-repeat + scribal dittography** (rule always applied; the 88 doublets are copying errors — dittography, the classic scribal error, produces doublets directly at 0.68 % ≈ realistic rates) | as 35 | strict variant simulates to **0.000 doublets**, rest identical — needs the 88 explained; dittography does it; random transcription noise does *not* (would need ~10 % error rate) | as 35 | the 88 doublet sites should look like copying slips (oracle-checkable on page photographs); deleting one glyph per doublet should *help* decryption | 7 | 9 |
| 38 | **Asemic / device-generated stream with repeat avoidance** (no per-glyph plaintext; includes the selection/null-cipher variant with a sparse embedded message) | 1 draw + 1 comparison · ~15 h · L | statistically **identical to #35 by construction** — indistinguishable from encrypted text by any statistic computed here; freehand variant excluded (humans cannot hold chi²=26 over 13k draws without a device/tally) | dice or deck | only a solve, or English on a sparse hand schedule, separates it from #35 | 9 | **10** |

(Families sharing a computed kill were merged into single rows: e.g., all pure transpositions; all
periodic polyalphabetics ≤ 200; all independent arithmetic streams under T1. Breadth is in the
closure theorems, which cover every member, enumerated or not.)

## 5. What survives, and why it matters

**The entire classical space is dead except one mechanism class.** Every scheme in which the
ciphertext symbol is *not* chosen with awareness of the previous ciphertext symbol fails the
doublet axis (T1), every static feedback fails the D-stream axis (T2), and everything with
periodic or English-residue structure fails IoC/periodicity. The unique surviving mechanism is:

> **a flat base process + a ciphertext-side collision-avoidance step** — "never (or almost never)
> write the rune you just wrote; on collision, advance/redraw the key"

in three live interpretations: (#35/36) encryption under a hand keystream with skip-on-collision
(an exact procedural cousin of the F-interrupters Cicada demonstrably used on the solved pages, and
of the key-skip the AN-END page needed); (#37) the same with strict compliance and the 88 doublets
as scribal dittography; (#38) no plaintext at all — a device-generated stream with the same rule.

This is precisely a *hand-execution* signature. No machine-generated OTP, no PRNG, no classical
tableau system produces "only-lag-1 deficit, evenly redistributed, homogeneous across 56 pages,
insensitive to word/line/page boundaries." A clerk's rule does — and the even redistribution of the
missing mass over all 28 deltas (no "+1 dump bucket") says the collision was resolved by
*re-drawing/skipping the key source*, not by nudging the output rune.

**Feasibility arithmetic for the survivor:** 2–3 ops/glyph ≈ 35–50 h of enciphering for the whole
book (weeks of evenings), plus pad preparation (~12 h with dice, or a printed prime table), with
local/self-healing error propagation — comfortably inside what one person did in 2013/14, unlike
Chaocipher (~70 h, state-catastrophic), Solitaire (>110 h), Hill (~90 h), or base-29 π (infeasible).

## 6. Caveats

- Plaintext proxy is KJV English in Gematria Primus; Cicada's orthography (heavier NG/EO/IA use)
  shifts baselines by at most a few tenths of a point — none of the kills is within that margin.
- Single simulation run per scheme (doublet σ ≈ ±0.16 pp); all kill margins are ≥ 6σ.
- The 80 % compliance in #35 is **fitted**, not derived (88 observed / 448 expected collisions).
  #37 explains the same 88 with zero free parameters if dittography is confirmed on the plates.
- T1 assumes position-wise group addition; designed non-additive alphabet schedules evade it only
  by being periodic (killed ≤ 200) or by carrying > 200 alphabets of key material (not hand-scale).
- Single transcription source (`krisyotam_runes.txt`); the 88 doublet *sites* (not the deficit,
  which is 17σ) are sensitive to transcription quality.

## 7. Proposed tests (ranked)

1. **Skip-beam decode under collision semantics.** For each stream in the hand-computable library
   (φ(prime) first — it is the validated page-73 stream; then primes mod 29, chain-addition seeds,
   keyword streams), run the existing interrupter beam (`src/lp/solve.find_interrupters` /
   skip-tolerant screen) with skips *forced hypothesis-side at positions where the un-skipped
   output would repeat the previous ciphertext rune*, both signs. Plant a positive control page
   enciphered exactly per #36. This is a small, closed, pre-registerable space.
2. **Dittography audit.** Flag the 88 doublet positions for the human oracle against the page
   scans (dittography usually shows as cramped/duplicated strokes); independently, collapse each
   doublet to a single glyph and re-run the standard screens on the 88-shorter text.
3. **File T1/T2 as ledger constraints.** "No plaintext-independent additive keystream" and "no
   static lag-1 feedback" are family-wide, power-measured negatives (z ≤ −10) that prune future
   rounds at zero cost.
4. **Asemic bound.** Register #38 as the live null: any future candidate must beat the
   "device stream + no-repeat rule" model, which already reproduces every measured statistic.
