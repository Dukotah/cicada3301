# Cicada 3301 Liber Primus — Campaign III After-Action Report (Foundation)

_Run 2026-06-21. 23 agents (~0.91M tokens). Two thrusts: (A/B) transcription
integrity across all public sources, (C) Cicada-thematic esoterica as running keys.
Artifacts under `analysis/foundation/`._

## 1. Bottom line

Nothing broke LP2. Best score this campaign was **−6.049** (Mathers, Kabbalah Unveiled) —
near-random band (random ~−7.3), worse than the prior armada best of −6.023, zero readable
English. The canonical transcription is **internally consistent but NOT independently
verified**: every public source traces to a single origin (rtkd/iddqd), so the "consensus" is
just canon restated. There is exactly one in-scope glyph where even a fork diverges
(page 24 index 172), and image-level examination could not resolve it with confidence.

## 2. Transcription integrity (the new, foundational result)

**The public sources are not independent — they are one origin.** All 8 compared
transcriptions descend from the **rtkd/iddqd community master**: krisyotam/canon is a verbatim
copy, cicada-solvers/iddqd is a fork, r4nd0mD3v3l0p3r and the Uncovering Cicada wiki explicitly
cite rtkd, relikd is by the rtkd author. The one supposedly-independent "raw OCR"
(dude123124144) is **byte-identical to canon** after J-rune glyph normalization — 0 edits
across all 13,136 runes, all 453 J-runes in identical positions — so it is the same text
re-copied, not a separate reading.

**Genuine disagreements among independent origins: zero** (rate 0/13,041 in-scope rune
positions). The only intra-lineage variants are 3 edits from the scream314 re-presentation:

- **page 24 : 172 — `ᚫ` (AE, canon) vs `ᚪ` (A, scream314)** — the lone *in-scope* divergence.
- page 56 : 80 — `ᚣ` (Y) vs `ᛖ` (E) — out of scope (solved parable region).
- an extra tail `ᚠ` from the "skip clear-text F" convention — a convention difference, not an error.

**Consensus vs canonical: identical** (`differsFromCanonical = false`). With only one
independent origin, majority voting is undefined.

**What this means:** all ~48 attack approaches to date (three campaigns) have assumed a
ciphertext that **cannot be validated from text comparison alone** — every witness is one
source. This does not prove the transcription wrong, but a systematic error (a wrong glyph or
a mis-propagated skip-rune convention from rtkd) would be invisible to every solver and would
silently defeat every cryptanalytic attack. The only true verification path is re-reading the
original Cicada page **images**.

### 2a. Image-level examination of page 24 : 172 (this session, by hand)

The lone in-scope divergence was examined directly off the page image (relikd `p24.jpg`,
2400×3600). The glyph is the first rune of the word `ᚫᚢ`/`ᚪᚢ` on text-line 8
(`ᛚ·ᚩᚦᛝ·ᚠᚪᛋᛡᛁᚻᛒᚱ·ᚪᚢᚣ·[172]ᚢ·ᛟᛠᚪᚣ·ᛖᛟ`), with confirmed `ᚪ` (A) glyphs at
positions 169 and 176 of the same line as same-scribe references. Examined at up to 6× zoom
with multiple crops and objective structural metrics (stem detection, arm-stroke counts, ink
fraction vs confirmed `ᚠ`/`ᚪ`/`ᚩ`/`ᚱ` on the same line).

**Result: UNRESOLVED with confidence.** The `ᚪ`/`ᚫ` distinction for this stylized hand could
not be reliably determined — no runic reference font is installed, the eyeball call is
unstable, and objective arm/ink metrics did not cleanly separate the target from same-line
confirmed `ᚪ`. This is consistent with the prior finding that AI vision is unreliable on these
glyphs. Reliable resolution needs the **original high-resolution upload** (relikd is a
re-encoded re-host) and ideally a human runologist. Crops saved under
`analysis/foundation/crops/`. **Note: this single rune does not change LP2's status either
way.**

## 3. Esoteric running-key results (best-first)

| # | Text | Verdict | Best score | Result |
|---|------|---------|-----------|--------|
| 36 | Mathers — The Kabbalah Unveiled | refuted | −6.049 | gibberish |
| 42 | Crowley — Book of Thoth (+777) | refuted | −6.079 | gibberish |
| 33 | Corpus Hermeticum (Mead) | no_finding | −6.133 | gibberish |
| 37 | John Dee — Monas + Enochian Keys | no_finding | −6.145 | gibberish |
| 41 | Lesser Key of Solomon (Goetia) | no_finding | −6.183 | gibberish |
| 40 | Pistis Sophia (Mead) | no_finding | −6.207 | gibberish |
| 31 | Iamblichus (Pythagoras / Theology of Arithmetic) | refuted | −6.209 | gibberish |
| 32 | Nicomachus — Introduction to Arithmetic | no_finding | −6.225 | gibberish |
| 35 | Sepher Yetzirah (Westcott) | no_finding | −6.257 | gibberish |
| 39 | Chymical Wedding of C. Rosenkreutz | no_finding | −6.265 | gibberish |
| 38 | Rosicrucian — Fama + Confessio | no_finding | −6.330 | gibberish |
| 34 | The Kybalion + Emerald Tablet | (failed — content filter) | — | not completed |

All texts run two passes (plain running-key sweep over both signs / atbash / all offsets, then
interrupter beam width 200). Interrupter beams were uniformly worse (−6.6 to −7.0). Selftest
(DIVINITY −4.34) passed before every run. Three results independently reproduced to exact
score/offset/sign.

## 4. Promising leads

**None cryptanalytic.** Every score sits in the −6.0 to −6.3 near-random band, worse than the
prior −6.023, with no readable English. The one genuinely open, non-cryptanalytic item is
image-level transcription verification (page 24:172 and the page-56/tail convention question) —
and that requires the original high-res scans, not text or re-hosted images.

## 5. Newly eliminated — append to the do-not-redo list

Plain running-key AND interrupter-beam, canonical ciphertext, all 55 pages:
Iamblichus (Life of Pythagoras + Theology of Arithmetic), Nicomachus (Introduction to
Arithmetic), Corpus Hermeticum (Mead), Sepher Yetzirah (Westcott), Mathers (Kabbalah
Unveiled), John Dee (Monas + 19 Enochian Calls), Rosicrucian (Fama + Confessio), Chymical
Wedding of CR, Pistis Sophia (Mead), Lesser Key of Solomon (Goetia), Crowley (Book of Thoth;
Liber 777 is tabular, not viable as a running key). Methodological: **text-only transcription
comparison** is exhausted — all public sources are one origin (rtkd/iddqd).

## 6. Honest final verdict

After three campaigns (~48 approaches), **LP2 (pages 0–55) remains unbroken, and the realistic
status is that the easy hypotheses are exhausted, not that a solution is close.**

- **Brute-force cryptanalysis: dead.** Best ever −6.023.
- **Published-text running keys, including Cicada-thematic esoterica: dead so far.** Hermetic,
  Kabbalistic, Pythagorean, Rosicrucian, Dee, Crowley, Gnostic, Goetic — all fail uniformly in
  the near-random band. A single contiguous published English keytext looks increasingly like
  the **wrong mechanism**.
- **Transcription: an unfalsified assumption, not a verified fact.** All witnesses agree only
  because they are the same source. This is the largest remaining unknown and is only
  resolvable from the original page images.

The two highest-value moves both point away from "try another keytext": (1) image-level
re-transcription of the highest-doubt runes against the **original** Cicada scans (starting at
page 24:172), and (2) accepting that the OTP/running-key class may mean a true one-time /
non-published / per-page key that is **not recoverable from any corpus search**. Plainly: LP2
is consistent with a genuinely unsolved one-time-pad-class cipher, and further keytext-hunting
has low expected value.
