# Round 37 / C3 - re-score the reopened English-only / legacy-beam families: PREREG
Dated 2026-10-30, written BEFORE any code in this lane ran. Bounded re-score. No git; one Python process; nproc=1; RAM rule (wait if free < 0.4 GB, max 20 min); append-mode streaming; hard cap ~90 min.

## Families, artifact re-scored, how
| id | ledger row | artifact | route |
|---|---|---|---|
| U5-L2 | R10-L2-MAP (proposed, C1 patch) | REGENERATED cleartext streams (no stored streams exist; `results.json` holds only winners): M1 word/line-free initial+final acrostics (4 stream types x 4 transforms x 29 shifts, pooled; 55 per-page variants), M2 word sum/len mod 29 (x2 F-handling x2 base x29), M5 walk paths, M9 address streams. Regenerated with the committed parse (`mapcommon.parse`) | DIRECT panel-R36 score of the stream (no decode). Per stream: 12-wide z, pmax, pmax_ne. Null = size-matched histogram-preserving shuffle of the stream itself (>=300 draws per stream), family-wise via max of per-stream standardised pmax. |
| U5-L2-Z694 | same, the z=6.94 near-flag | the pooled M1 family (4 stream types x 116 transforms = 464 readings; includes first-of-word/noF atbash/rev/+28) | best-of-464 panel pmax vs 2,000 `null_A` draws (shuffle rune content, hold word boundaries - the lane's own null), Wilson 95% bound on the exceedance rate |
| U5-L3 | R10-L3-ROAD (proposed) | T2/T3/T4 readings (`road.py::readings`, source exec'd unchanged, 208 streams) + T5 book-like streams | same direct route; null = the stream's own shuffle |
| U6a-N1 | R11-N1 | CT-feedback keystreams (24 configs: f in {mod29,totient,digitsum} x sign x fwd/rev x continuous/per-segment-reset): REGENERATED (no top-N stored) and run through beam_v3 | keyskip1 + keyskip2, L=120, panel-R36, 10 page-start windows |
| U6a-N1pt | R11-N1 | PT-feedback decodes (24 configs): the key depends on the recovered plaintext, so a fixed-K skip beam cannot represent it | NOT beam-decodable -> direct skip-free decode, panel-R36 on the decoded stream; the transition model stays legacy for this half (`not_covered`) |
| U6a-N2 | R11-N2 | prime_gap/prime_index/(+cumsum) streams read as data, mod29 / base29 (2,3 digits) -> rune stream | direct |
| U6a-N3 | R11-N3 | primality/factor structure; NO decode, NO adjudicator | not re-scored; row restated only (the reopen is vacuous: nothing English-gated) |
| U6a-N4 | R11-N4 | digit planes (bases 3,5,7,10) as mod-29 keystream (both signs) -> beam_v3; as direct text -> direct | both routes |
| U6a-N5 | R11-N5 | 8 totient-ladder generators x 29 offsets x 2 signs = 464 keystreams -> beam_v3, 3 windows | keyskip1+2 |
| U6a-S1 | R11-S1 | gaps between F occurrences, mod29/base29/mod n -> rune stream (ASCII/bit routes are text/bytes, not rune space) | direct; ASCII/bit routes `not_covered` |
| U6a-S2 | R11-S2 | separator run lengths mod 29 (binary/ternary byte routes not rune space) | direct |
| U6b | R22-C | the 185 operations: 138 X1 + 31 X3a STRUCTURAL (a transformed rune stream, no key) -> direct panel-R36 re-score vs shuffle null; 4 X3b + 12 X4 KEYED -> beam_v3 keyskip1+keyskip2 at page length, windows | structural ops have no key, so "x keyskip1/2" applies only to the 16 keyed ops (the plan's ~370 decodes is read as 16 x 2 x windows); stated openly |

pf_v4 is not used: none of these families screens a head over a seed space (nothing to prefilter).

## Controls (run FIRST; a family whose control fails is `inconclusive`, not negative)
- **Beam families** (N1ct, N4ks, N5, X3b, X4): plant held-out text from `testhalves12.npz` (EN_MODERN, LATIN, GREEK; real `enc_exact` / `enc_pair`) with the FAMILY's own keystream (the actual regenerated K at a page start), decode with the true K via beam_v3 panel_max at L=120 and L=240 on panel-R36. PASS = pmax120 >= 12-register declared-N (1e6) L=120 bar AND pmax240 >= L=240 bar AND recovery240 >= 0.90, >=2 of 3 registers per relation per family. N5 additionally: AN END (the real keyed page) under phi(prime) must decode (pmax >= bar, recovery vs known plaintext >= 0.90).
- **Direct families**: plant held-out text into the shape each stream family produces (stream length n of the family; text in a random-symbol carrier through the family's own transform), run the identical direct pipeline, PASS = planted Z (standardised pmax vs the stream's own shuffle null) above the family-wise bar. Round 11's own control per lens is re-stated, not re-run (their English scorer is the retired instrument).
- X1/X3a: inverse-op plant (decimation embed, interleave, reversal+shift) through the same direct route.

## Bars and kill
- Beam rows: 12-register Gumbel/POT bars `round36/B1-orbit-12reg/null12.json` (u, p_u, beta, mu per L|rel): bar(N) = mu + beta ln(N / -ln 0.99) at the ACTUAL N of the family and at declared N = 1e6. Plus a family-matched wrong-key null (shuffled windows, same K, 100 draws per rel) as a sanity check on the transferred bar.
- Direct rows: family-wise exceedance vs the family-max of per-stream standardised null pmax (>= 300 draws/stream, same draw index across the family), alpha = 0.01. The panel calibration for n > 1000 is clamped at the grid end, so stored z is rescaled by sqrt(n/1000); verdicts use the self-calibrating shuffle null and do not depend on it.
- A row clearing actual-N -> L=240 re-screen (beam) -> flagged-for-oracle per HUMAN-ORACLE.md; clears actual-N but not declared-N -> near-miss, listed. Clearing is never "solved".
- Kill: control fails -> that family `inconclusive`. A beam family whose Round-37 plants recover < 0.90 at L=240 under its own K is dropped, not scored.

## Three conditionals each negative carries
(1) key space = exactly the regenerated config set above (not wider); (2) transition model = keyskip1 + keyskip2 under beam_v3 panel_max (PT-feedback, structural streams: none / skip-free); (3) adjudicator = panel-R36, 12 registers.
Q5 abandon: if the beam control cannot be passed for N5's key family at L=240, N5 is `inconclusive` after 10% of budget.
