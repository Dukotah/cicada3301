# R44 / WAVE-2 CELL C7 — AUDIO REDUCTIONS BEYOND LITERAL BYTES — RESULTS

_Completed 2026-11-12T05:43:06Z (UTC). PREREG hash of record
`b326b052727d7f4c06cb453d216b879c3b5accfba60f1ee0c405219ad1f002d6` (stamped before run,
re-stamped unchanged at resume, closing stamp in `run.log`)._

## Verdict

**NEGATIVE — both batteries, all 55 unsolved LP2 pages, zero crossers.** Neither decoded
PCM nor any derived channel (onset intervals, spectral peaks, frame sizes, bitrate indices,
metadata digits) of 761.mp3 or the onion5 "Interconnectedness" mp3 acts as a mod-29
keystream under exact Vigenère±/Beaufort ± atbash at this cell's offsets/rotations.
Every observed score sits in the noise floor, **10.9–11.3 panel units below the lowest bar**.

| battery | decodes | budget | bars (L120/240/400/729) | global best | best bar at its L | margin | crossers |
|---|---|---|---|---|---|---|---|
| S (short streams, dense) | 42,468,048 | ≤ 6e7 | 17.4858 / 23.6153 / 24.4660 / 27.8298 | **6.173** | 17.4858 (L=66→120 floor) | −11.31 | 0 |
| P (PCM pads, sampled) | 12,655,368 | ≤ 2e7 | 16.9004 / 22.8032 / 23.7158 / 27.0342 | **6.014** | 16.9004 (L=201→120 node) | −10.89 | 0 |

## Best vs bar per reduction leg

Per-leg maxima over the 55 page-best rows (a leg that never won a page is bounded above by
the global best of its battery, i.e. < 6.173 for S, < 6.014 for P — all legs are deep noise):

**Battery S** (bar 17.4858 at L120 floor / 23.6153 at L240):
| leg | best pmax | at | pages won |
|---|---|---|---|
| onion5:meta_digits | 6.173 | rev/m2/vigp_atb rot 27, page 49, L66 | 1 |
| onion5:spec_peak | 6.007 | rev/m3/vigp rot 464, page 1, L266 | 12 |
| onion5:onset_iv | 5.688 | fwd/m1/vigm rot 522, page 54, L76 | 19 |
| 761:spec_peak | 5.550 | rev/m1/vigp_atb rot 148, page 46, L270 | 11 |
| 761:onset_iv | 5.467 | rev/m1/vigp_atb rot 227, page 40, L231 | 11 |
| onion5:frame_sz | 5.121 | rev/m2/beau rot 10416, page 30, L263 | 1 |
| 761:frame_sz, 761:br_idx, 761:meta_digits, onion5:br_idx | < 6.173 (never page-best) | — | 0 |

**Battery P** (bar 16.9004 at L120 floor / 22.8032 at L240):
| leg | best pmax | at | pages won |
|---|---|---|---|
| onion5:pcm_s16samp | 6.014 | fwd/vigm offset 278528, page 2, L201 | 7 |
| 761:pcm_s16bytes | 5.860 | rev/vigp_atb offset 9965568, page 30, L263 | 13 |
| onion5:pcm_s16bytes | 5.803 | fwd/beau_atb offset 16134144, page 48, L271 | 17 |
| 761:pcm_s16samp | 5.790 | fwd/vigp offset 12288, page 52, L179 | 6 |
| onion5:pcm_u8 | 5.423 | rev/beau_atb offset 8077312, page 37, L228 | 7 |
| 761:pcm_u8 | 5.409 | fwd/vigm offset 6860800, page 12, L261 | 5 |

Full doctrine-R3 rows for every page-best are in `results/sweep_S.json` / `sweep_P.json`
(assembled from the per-page checkpoints `results/progress_{S,P}.jsonl`).

## Power (plant gate 4/4 through the identical sweep code, BEFORE any real decode)

After dated addendum A1 (extractor fix; pre-gate failure file `results/plants.pregate-A1.json`
retained): PC1 pmax 38.32 vs bar 22.80 (PCM end-to-end round trip through libmp3lame);
PC2 33.40 vs 17.49 (onset intervals, 80/80 recovered exactly); PC3 32.32 vs 23.62 (spectral
peaks, 70/70 bins exact); PC4 cleared with frame walker within 1 frame of ffprobe on the
plant mp3 AND both real artifacts. All planted cells recovered as grid max, plaintext
byte-exact. Plant margins ≥ 8.7 units above bar; real margins ≥ 10.9 below. ffmpeg
double-decode determinism held on both artifacts (Q5 ii never fired).

## Coverage — including the artifact-presence premise check

**Both halves of the audio corpus are PRESENT and were swept.** The premise check did NOT
find the onion5 mp3 unavailable: `corpus/A-primary-artifacts/2014/ia_onion5_data.mp3`
(6,651,873 B, sha256 `1ce3839b…ffffc6`) exists with THREE byte-identical in-repo copies and
its sha256 was asserted at the top of every run slice; same for 761.mp3 (`830082…4a60`).
The only unswept encode is the krisyotam re-encode (different bytes, same track) —
deliberately excluded per PREREG §2/§5. Covered: 2 artifacts × {5 derived short streams ×
fwd/rev × m1/m2/m3 × 6 configs × all rotations + one-shot suffixes ≥ 60} (battery S, dense)
and × {3 PCM reductions × fwd/rev × 6 configs × offsets {0..7} ∪ stride-4096} (battery P,
sampled) × 55 pages.

**not_covered (PREREG §5 verbatim):** dense single-byte literal-file offsets (still open
from R40-B3); the krisyotam re-encode; PCM at rates/channels other than 44.1 kHz mono
downmix; sub-stride PCM offsets; bit-planes of PCM, stereo L−R, phase, MFCC,
spectrogram-image pixel channels; intervals/peaks as transposition or skip material;
mappings beyond m1/m2/m3; rejection-loop constructions (R18-L7-B conditional); registers
outside panel-R36 (L7-A conditional); PRF/seed/salt uses of any stream.

## Run-integrity notes (X1 WAVE2 §C7 remediation)

- The first real sweep died silently at page 12/55 with no per-page persistence. Per the
  X1 dead-man finding the sweep was **RESTARTED from page 0** (resume-at-12 would have
  shipped a record missing 12 pages of R3 rows that existed only in the dead process's
  memory). Pages are independent; reductions deterministic.
- The restart reproduced the dead run's pages 0–12 **exactly** (same per-page decode counts,
  same gbest 6.007 at onion5:spec_peak/rev/m3/vigp rot 464 page 1) — a free determinism
  cross-check.
- Harness changes were operational only (per-page checkpoint jsonl, 10-min heartbeat to
  run.log, time-sliced foreground driving): zero analytic change — `c7lib.py`, `reduce.py`,
  bars, space and thresholds untouched; PREREG unchanged (hash re-stamped identical).
- `sweep_S.json` `elapsed_s` = 190,060 s includes ≈188,000 s of machine suspend during
  page 19 (wall clock jumped 2026-11-10 → 2026-11-12 UTC mid-slice); true compute for
  battery S ≈ 2,100 s, battery P ≈ 400 s.

## Flags

None. Zero crossers in either battery; nothing goes to the oracle. (Standing rule: any
crosser would have been FLAGGED-FOR-ORACLE per `HUMAN-ORACLE.md`, never certified.)
