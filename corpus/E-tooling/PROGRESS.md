# LANE E — Tooling & Third-Party Corpus — PROGRESS

Started 2026-08-19. Working dir: `corpus/E-tooling/`.

## Baseline hashes established (verified locally, not asserted)
Extractor: `corpus/E-tooling/hash_runes.py` (futhorc glyph -> Gematria Primus index 0..28, comma-joined, SHA-256).

| Object | n runes | SHA-256 |
|---|---|---|
| Full transcription `liber-primus/data/krisyotam_runes.txt` | 13,136 | `74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329` |
| Unsolved subset (LP2 pages 0-54), per `liber-primus/PROBLEM.json` | 12,956 | `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585` |

NOTE: the lane brief paired "13,136 runes" with the `0233120…` hash. Those are two
different objects. `0233120…` is the **12,956-rune unsolved subset**. Vendored
third-party transcriptions are diffed against the **13,136 / `74cebdb0…`** baseline.

## Log
- [x] dir scaffold, hasher built + baseline verified

## 2026-08-19 — root-transcription history resolved (the headline item)
`rtkd/iddqd` cloned WITH FULL HISTORY (59 commits, single branch `master`,
HEAD `f2267b0c2f1e1d2662806b90b9c3a2953b3a7023`, last commit 2019-06-17).
`liber-primus__transcription--master.txt` has been edited exactly THREE times:

| commit | date | message | n runes | index SHA-256 |
|---|---|---|---:|---|
| `218ed88` | 2017-03-01 | Clean up. | 15,935 | `d73e79bba056734dfc7f04f894b567c24680d928767d48c0edf632f91e9412ec` |
| `ed95eb7` | 2017-05-21 | Fix error in segment 2 "A Koan". | 15,933 | `c3eb607844a190915ef3436c148603973ae6bb07e98b3569164d9b7c3e9214e5` |
| `3089b65` | 2019-06-17 | Fix segment offsets and transcription errors. | 15,933 | `c3eb607844a190915ef3436c148603973ae6bb07e98b3569164d9b7c3e9214e5` |

- The 2017-05-21 edit is the ONLY change to the rune sequence: two occurrences of
  `ᚹᛋ` (W,S) replaced by the single ligature `ᛠ` (EA), at rune offsets 998 and 1135,
  both inside segment 2 ("A Koan", a SOLVED LP1 page).
- The 2019-06-17 edit, despite its message, changed **no runes at all** — identical
  index hash. It moved segment offsets/structure only.
- ALL THREE versions contain all 57 of our canonical segments verbatim.
  **Our 13,136 never sat downstream of a root correction.**

## 2026-08-19 — decoder-type reads so far (code-backed)
- `rtkd/idkfa` `lib/shift.js` `mutate()`: `arrKeyData[i][keyOffset++]` advances the key
  pointer for EVERY futhark char, unconditionally -> **RIGID**. Interrupters are handled
  only by a hard-coded `Config.patch` lookup table of literal positions in `config.js`
  (a post-hoc list for pages already solved), never searched. It cannot discover an
  unknown skip pattern.
- `relikd/LiberPrayground` `LP/InterruptSearch.py`: real **SKIP-AWARE** search --
  `all()` enumerates every subset of interrupter positions; `sequential()` is a
  bounded hill-climb over the first `maxdepth=9` interrupts per step, scored by a
  supplied `score_fn`. Bounded to periodic/Vigenere key lengths, not running keys.
- `jens-wedin/liber-primus` `attack_keyskip.py`: **SKIP-AWARE beam search**, self-tested
  to 96-98% recovery on planted key-skip text. Reaches independently almost exactly this
  project's conclusions (86 doublets / 0.66% / lag-1 no-repeat / differencing restores
  3.37%). Its running-key test is declared UNDERPOWERED by its own calibration.
