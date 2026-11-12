# Round 44 / WAVE-2 CELL C7 — AUDIO REDUCTIONS BEYOND LITERAL BYTES — PREREG

_Dated 2026-11-09, written and sha256-stamped into `run.log` BEFORE any reduction, plant or
sweep output existed (R44 X1 hygiene fix). Cell dir: `analysis/round44/W2-C7-audio/`.
Analysis glue pure python3 (numpy), no network. Pages: the 55 unsolved LP2 pages via
`analysis/run_stats.load_pages()[:-2]` (the R43 F5b-T loader). Standing instrument:
panel-R36 (12 registers) via `analysis/round19/I2/adjudicate.py` (`Panel` +
`adjudicate_batch`), bars via `analysis/round34/I1-v3-null/bars_v3.py`, harness pattern =
`analysis/round43/F5bT-timing-keystream/run_f5bt.py` (reused per the cell brief)._

## 0. Declared tool exception (recorded before first run)

MP3→PCM decoding is NOT implementable in pure python within this cell's budget. The PCM
reductions use the LOCAL system decoder `ffmpeg 8.0.1-3ubuntu2` (`/usr/bin/ffmpeg`,
no network, deterministic — determinism asserted by double-decode sha256 equality, a kill
condition if it fails). Exact command lines and the sha256 of every raw PCM output are
persisted in `results/pcm_manifest.json`. ffmpeg (and its libmp3lame encoder) is also used
to BUILD the plant mp3s. Everything downstream of the raw PCM bytes — frame parsing, onset
detection, spectral peaks, metadata walk, enciphering, decoding, adjudication — is pure
python3/numpy committed in `scripts/`. The MP3 frame/metadata walker (`scripts/mp3meta.py`)
is pure python on the raw file bytes and uses no external tool.

## 1. Hypothesis

The two held audio artifacts carry the LP2 key not in their literal file bytes (measured
ground, R12-A1/R28-L1/R40-B3) but in a DERIVED channel: decoded PCM as a byte pad, the
onset/beat interval sequence (the F5b-T timing-channel analogue), the spectral-peak
sequence, or the frame-size/metadata number stream — each used as a mod-29 keystream over
the 55 unsolved pages.

## 2. Artifacts (ignore-blind corpus search performed; both halves PRESENT)

- **761.mp3** = `puzzles/2013/artifacts/761_The-Instar-Emergence.mp3`, 4,010,732 B,
  sha256 `83008217439110c3b824898af73b99cb2cf0657dda88cb363c3aa34a4ec0a460`
  (byte-identical copies at `corpus/A-primary-artifacts/wiki-uncovering-cicada/images/761.MP3`
  etc. are checked at run time; if they differ the copy list goes in RESULTS).
- **onion5 "interconnectedness" mp3** = `corpus/A-primary-artifacts/2014/ia_onion5_data.mp3`,
  6,651,873 B, sha256 `1ce3839b4a62462d9009c4469acc189b523e1bdcf338cb49cda1cd7bb4efffc6`,
  attested by THREE byte-identical in-repo copies (also at
  `corpus/A-primary-artifacts/cijhho123/2014/Websites/Interconnectedness fron onion 5/3301 - Interconnectedness.mp3`
  and `corpus/A-primary-artifacts/signed-payloads/corpus_2014-01-interconnectedness-hex.mp3`).
  A FOURTH, non-identical encode exists (`corpus/A-primary-artifacts/krisyotam/media/audio/
  3301 - Interconnectedness.mp3`, 5,086,016 B, sha256 `bb6e449e…`): it is a re-encode of the
  same track and is NOT swept (goes to not_covered).
  Both are MPEG-1 Layer III, 44.1 kHz stereo, ~192 kbps (ffprobe: 167.02 s / 277.16 s).

## 3. Cited ledger rows (`not_covered` verified verbatim before freezing)

- **R12-A1** (negative): 761.mp3 swept as LITERAL byte→symbol reductions only; its
  `not_covered` (a) ">99.99% of single-byte offsets remain unswept" and coverage line
  "Tested as LITERAL byte->symbol reductions only". Decoded PCM, onsets, spectral peaks and
  metadata numbers appear nowhere in the row. This cell does NOT re-run literal file-byte
  reductions at any offset.
- **R28-L1-CICADAOS-PADS-DENSE-PAIR** (negative): dense literal-byte offsets on the two
  authoritative CicadaOS pads only; its `not_covered` names "Reductions outside the 5
  per-byte maps" — the derived channels here are outside those maps and outside its pads.
- **R40-B3-COSPAD-REDECODE** (partially-run): literal reductions of the 4 ISO pads
  (761.mp3 included) at a SAMPLED offset fraction; `not_covered` = "Dense offsets; …".
  This cell stays off the literal-byte axis entirely; the dense literal-offset gap REMAINS
  OPEN after this cell.
- **Ledger scan**: all 322 entries grepped for onion5/interconnectedness/instar/audio —
  the onion5 mp3 has NEVER been used as key material in any row (only R29-L1 onion-image
  stego and I-03 OSINT touch "onion"). CONFIRMED OPEN for every reduction including PCM.

## 4. The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?** A hit is a
non-degenerate panel-R36 pmax ≥ the fixed battery bar (§6) at one (artifact, reduction,
direction, mapping, config, mode, offset/rotation, page) cell, reproducible byte-exactly.
Recognizer = this cell's own glue; proven by FOUR plants (§7) run through the IDENTICAL
sweep code BEFORE any real target, including a full audio-side round trip (synthesized
audio → libmp3lame → my decoder/reductions → keystream → sweep). No verdict without all
four passing. Any crosser is FLAGGED-FOR-ORACLE per `HUMAN-ORACLE.md`, never certified.

**Q2 — Measured fact raising the prior.** (i) 761.mp3 IS author key material the author
shipped inside CicadaOS (R12-A1 row: "period-correct key material Cicada demonstrably
used") and spectrogram data inside this very file carried the 2013 clue image — the
artifact demonstrably has a non-literal data channel (spectral), which the literal-byte
sweeps cannot see by construction. (ii) The onion5 mp3 was served from the puzzle's own
onion and has never been key-tested at all (ledger scan above). (iii) R43 F5b-T measured
that a timing/interval channel is extractable and testable end-to-end with plant power
≫ bar (its 3/3 plants cleared by 14–25 z) — the same harness is reused here. Honest label:
the onset/spectral/metadata reductions are a bounded completeness battery over named held
artifacts with a channel-existence prior, not a lore prior; the PCM pad is the direct
"beyond literal bytes" continuation of the R12-A1 family.

**Q3 — Bounded space?** ENUMERABLE, fixed here. Battery S (short derived streams, DENSE
offsets as the brief requires): per artifact the streams {onset-interval, spectral-peak,
frame-size, bitrate-index, metadata-digit} × {fwd, rev} × 3 mappings (m1 k mod 29, m2
5k mod 29, m3 GP-prime map — the F5b-T set) × 6 configs (vig−, vig+, Beaufort, each ± atbash)
× {repeating: EVERY rotation (constant streams dedup to 1); one-shot page-start aligned:
EVERY suffix ≥ 60 not already identical to a repeating decode} × 55 pages. Battery P (PCM
pads, SAMPLED offsets — literal-pad convention, prompt-mandated): per artifact 3 reductions
{u8 mono mod 29, s16le mono byte stream mod 29, s16 mono sample mod 29} × {fwd, rev} ×
6 configs × offsets ({0..7} ∪ stride-4096 grid; offsets with < page-length remaining
dropped) × 55 pages, one-shot page-start aligned. Runtime asserts: battery S total decodes
≤ N_bar_S = 6e7, battery P ≤ N_bar_P = 2e7.

**Q4 — The three conditionals.**
1. *Key space*: ONLY the named derived reductions of the two named artifacts at the stated
   offset/rotation grids; not literal file bytes (measured elsewhere), not MFCC/phase/LSB/
   stereo-difference/cepstral channels, not the krisyotam re-encode, not PRF/seed uses.
2. *Transition model*: exact skip-free Vigenère±/Beaufort ± atbash composition, repeating
   and one-shot. NO rejection-loop/skip relation is represented (R18-L7-B conditional: a
   skip_by_two-class construction would be missed).
3. *Adjudicator register*: panel-R36 (12 registers) pmax vs `bars_v3(N_bar, L_cap, "free")`;
   registers outside the panel are invisible (L7-A conditional).

**Q5 — Kill condition at 10% budget.** (i) Any of the four plants fails (reduction does not
recover its designed sequence at the §7 tolerance, or the sweep does not return the planted
cell as grid max with byte-exact plaintext) → STOP, report INSTRUMENT-INCOMPLETE for the
affected battery; no verdict from it. (ii) ffmpeg double-decode sha256 mismatch on any
artifact → battery P killed as non-deterministic. (iii) Frame walker disagrees with ffprobe
frame count by > 1% on either artifact → frame-size/metadata streams killed. Checkpoint:
plants and consistency checks run and are judged BEFORE the first real-page decode.

## 5. What is deliberately NOT swept (goes to not_covered verbatim)

Dense single-byte literal-file offsets (still open from R40-B3); the krisyotam re-encode;
PCM at sample rates/channels other than 44.1 kHz mono downmix; sub-stride PCM offsets
(stride 4096 + ladder {0..7} only — the pad does not resynchronise, so off-grid stays
open); reductions beyond those named (bit-planes of PCM, stereo L−R, phase, MFCC,
spectrogram-image pixel channels); intervals/peaks as transposition or skip material;
mappings beyond m1/m2/m3; rejection-loop constructions; registers outside panel-R36;
PRF/seed/salt uses of any stream.

## 6. Fixed thresholds (computed from the standing instrument BEFORE any run; never edited)

`bar_v3(N, L_cap, "free")` with L_cap = largest of {120, 240, 400, 729} ≤ decode length
(floor 120), per battery at its fixed family size:

| battery | N_bar | L120 | L240 | L400 | L729 |
|---|---|---|---|---|---|
| S (short streams, dense) | 6e7 | **17.4858** | **23.6153** | **24.4660** | **27.8298** |
| P (PCM pads, sampled) | 2e7 | **16.9004** | **22.8032** | **23.7158** | **27.0342** |

Crosser iff non-degenerate pmax ≥ its battery bar at the decode's L_cap. Plants are judged
against the same bars by the same code path.

## 7. Positive controls (gate, BEFORE any real target, through this cell's OWN glue)

All plant audio is synthesized (seeded numpy), encoded to MP3 44.1 kHz by the same local
ffmpeg, then fed through the IDENTICAL reduction + sweep code as the real artifacts (the
sweep code cannot distinguish plants from targets). Plaintexts: known English-register
rune sequences (the F5b-T PT texts). Gate = ALL FOUR pass.

- **PC1 (PCM pad, end-to-end):** 30 s noise WAV → mp3 → my ffmpeg-decode glue → the
  DECODED u8 stream IS the key; encipher PT1[:240] (vig−, fwd) at on-grid offset 4096 →
  synthetic page through battery-P sweep of the plant pad. Pass = planted cell is the grid
  max, pmax ≥ P-bar, plaintext byte-exact.
- **PC2 (onset intervals):** 80 click intervals I\* drawn from [4, 28] hop-units (seeded)
  → click track → mp3 → my onset extractor; pass(a) ≥ 90% of recovered intervals equal I\*
  element-wise after the extractor's own quantization; encipher PT2[:200] with
  m1(recovered), Beaufort, rot 7 → battery-S sweep; pass(b) planted cell = grid max,
  byte-exact.
- **PC3 (spectral peaks):** 70 pure-tone segments (150 ms) at known FFT-4096 bins b\* ∈
  [40, 900] (seeded) → mp3 → my spectral reduction; pass(a) ≥ 90% bins exact; encipher
  PT3[:240] with m2(recovered), vig+ ∘ atbash, rot 0 → battery-S sweep; pass(b) as PC2.
- **PC4 (frame-size/metadata):** my pure-python frame walker on the PC1 mp3 and BOTH real
  artifacts; pass(a) frame count within 1% of ffprobe's and sample-rate/bitrate fields
  exact; encipher PT1[:240] with m1(frame-size stream of the PC1 mp3), vig−, rot 11 →
  battery-S sweep; pass(b) as PC2.

## 8. Reduction definitions (frozen)

- **PCM**: `ffmpeg -i <mp3> -ac 1 -ar 44100 -f u8|s16le -` (mono downmix, native rate).
  u8 stream = bytes; s16 byte stream = interleaved lo/hi bytes; s16 sample stream =
  little-endian signed sample values; key symbol = value mod 29.
- **Onsets**: mono s16 → float; frame energy, win 1024 hop 512, half-wave-rectified energy
  flux; onset = local max of flux above median+3·MAD with ≥ 4-hop separation; stream =
  inter-onset intervals in hop units.
- **Spectral peaks**: at each onset, FFT-4096 (Hann) starting 512 samples after the onset
  sample (zero-padded at EOF); stream = argmax bin over bins 1..2047.
- **Frame sizes**: pure-python MPEG frame walk (ID3v2 skipped, Xing/Info frame recorded and
  excluded); stream = per-frame byte length. **Bitrate indices**: per-frame bitrate-index
  nibble (constant ⇒ dedups to a length-1 constant key). **Metadata digits**: decimal
  digit stream of [file_size_B, n_frames, sample_rate, nominal_bitrate, duration_ms,
  n_pcm_samples_mono] concatenated in that order.
- One-shot decodes identical to a repeating decode (key remainder ≥ page length) are
  counted once (the F5b-T equivalence); one-shot suffixes shorter than 60 runes are not
  adjudicated (MIN_ONESHOT = 60, the F5b-T floor).

## 9. Outputs

`run.log` (hash stamp first line), `scripts/*.py`, `results/pcm_manifest.json`,
`results/streams.json`, `results/plants.json`, `results/sweep_S.json`,
`results/sweep_P.json`, `RESULTS.md`, `ledger_rows.json` (draft; `LEDGER.json` untouched).

## Addendum A1 — dated 2026-11-10, appended BEFORE any real-target execution

The first plant-gate run (`results/plants.pregate-A1.json`) PASSED both sweep legs of all
four controls (planted cells recovered as grid max, byte-exact, 32–39 vs bars) and PASSED
PC1/PC4 outright, but FAILED the reduction leg of PC2 (3/80) and PC3 (1/70): the frozen
onset threshold (median + 3·MAD of HALF-WAVE-rectified flux) is degenerate — with ≥ 50% of
rectified flux exactly 0, median and MAD collapse to ~0 and the detector fires at nearly
every allowed position (265 onsets for 81 clicks), which also corrupts PC3's FFT windows.
Fix (scripts/reduce.py, marked "addendum A1"): onset = local max of the UNRECTIFIED frame
energy difference d, one-sided threshold 6.0 × (1.4826·median|d|), min-gap and all other
frozen parameters unchanged. No real page, no real-artifact stream and no score threshold
was seen or touched before this addendum; the score bars of section 6 are UNCHANGED. The
gate is re-run in full; the failed pre-gate file is retained.

## Addendum A2 — dated 2026-11-10, appended during the real sweep, before any result was read

Q2 clause (i) contains the unsupported sentence "spectrogram data inside this very file
carried the 2013 clue image" — an ignore-blind grep over the repo finds NO in-repo citation
for a spectrogram payload in 761.mp3, so under doctrine R4 that clause is STRUCK as a lore
prior and carries no weight. The surviving Q2 priors are the cited ones: 761.mp3 is author
key material shipped in CicadaOS (LEDGER row R12-A1), the onion5 mp3 is a held primary
artifact never key-tested (ledger scan, section 3), and the F5b-T harness measured
end-to-end plant power for interval channels (R43-F5BT-TIMING-KEYSTREAM). No threshold,
space or instrument change.
