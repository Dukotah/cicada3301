# Lane G — GAPS

What the forensic battery did **not** test, could not test, or tested with insufficient
power. Written so that no coverage gap in this lane can later be mistaken for a closure.

**The distinction this file exists to protect:**

| finding | meaning |
|---|---|
| `NEGATIVE` | the instrument examined the artifact and reported nothing |
| `NOT_APPLICABLE` | the instrument **could not examine** the artifact (unsupported container, wrong media type). It contributes **no evidence either way** |
| `ERROR` | the instrument failed or was killed. Also **no evidence either way** |

`RESULTS-SUMMARY.json` carries all four categories separately and never collapses them.

Corpus: **486 artifacts** — 380 `onion_artifact`, 56 `lp_page`, 40 `onion_html`,
9 `cicadaos_pad`, 1 `audio_2013` (`TARGETS.json`).

---

## G-G-01 — steghide: 338 of 486 artifacts were NOT_APPLICABLE

steghide supports only JPEG, BMP, WAV and AU carriers. It **examined 148 artifacts** and
**could not examine 338**.

| class | examined (NEGATIVE) | NOT_APPLICABLE |
|---|---|---|
| `lp_page` | 56 | 0 |
| `onion_artifact` | 80 | 300 |
| `onion_html` | 12 | 28 |
| `cicadaos_pad` | 0 | 9 |
| `audio_2013` | 0 | 1 (MP3 is not an AU/WAV carrier) |

**All 56 Liber Primus pages were examined and are NEGATIVE** — an independent instrument
agreeing with the DCT/metadata results.

The 338 `NOT_APPLICABLE` rows say **nothing** about those artifacts. In particular the
2013 MP3 (`761_The-Instar-Emergence.mp3`) has never been tested by steghide, because
steghide cannot read MP3 at all.

---

## G-G-02 — binwalk coverage is partial, and its HITs are mostly noise

Two separate problems.

**(a) Coverage.** binwalk costs **~26 seconds per artifact** on this mount. Completed:
all 56 `lp_page`, 9 `cicadaos_pad` (all `ERROR`), and only **22 of 380** `onion_artifact`.
The `onion_html` class was never reached. **~370 artifacts have no binwalk row at all.**

**(b) Reliability.** binwalk reports HIT on **all 56** Liber Primus pages. The matches are
the JPEG container itself, the `Copyright Artifex Software 2011` string inside the shared
Ghostscript ICC profile, and a spurious `JBOOT STAG header` inside the DCT entropy stream
claiming a 591 MB image inside a 595 KB file. **No binwalk HIT in this corpus has been
shown to be a payload.** Counts are meaningless here; only the per-row evidence in
`RESULTS-SUMMARY.json` means anything.

**(c) 24 ERROR rows.** 9 on the `cicadaos_pad` files (killed, exit `-9`) and 15 on
`onion_artifact` (`timeout`, exit `-1`) — the large `T4_blob*` binaries exceed the 40 s
per-file limit. These artifacts have **no binwalk result**, not a negative one.

**To close:** run `python3 ext_tools.py <seconds> onion_artifact binwalk` to completion
(budget ~3 hours), or replace binwalk with a header-validating carver.

---

## G-G-03 — JSteg and F5 were never tested on any artifact

The DCT-domain sweep tested **OutGuess only**. `jsteg` and any F5/nsF5 implementation are
absent from the environment (`TOOLS-AVAILABLE.md`), and `stegdetect` — which would have
given an *independent* statistical discrimination between jsteg / jphide / outguess / F5 —
is also absent.

**Consequence, stated plainly:** the conclusion "no DCT stego in the LP2 pages" rests on
**one algorithm's extractor being used as its own detector.** A JSteg or F5 payload would
not have been detected by anything run in this lane. This is a genuine coverage gap, and
it must not be recorded as a negative.

**To close:** `stegdetect` (hard to build on modern glibc) or a modern DCT-histogram
detector; `jsteg` is a single Go binary and is easy.

---

## G-G-04 — zsteg absent: PNG LSB coverage rests on one implementation

The lane's own Pillow/numpy bit-plane analysis ran on **3 images only** (2 HIT, 1 NEGATIVE,
1 adjudicated). `zsteg`, the standard PNG/BMP LSB scanner, is not installed — so palette-
index channels, alpha-only embedding, and the per-channel bit-order permutations zsteg
enumerates were **never tested**.

Ruby 3.3.8 is present, so `gem install zsteg` closes this in one command.

---

## G-G-05 — the LSB channel on `onions__imgur.com__hkdgl.png` is statistically untestable

Recorded because it is the clearest example in the lane of a negative with **limited
power**, and the lane's own adjudication row says so.

The automatic LSB test flagged this PNG (bit-0 plane entropy > 0.9999 in all three
channels, in a *lossless* carrier). The adjudication row supersedes that flag as NEGATIVE,
because bit planes 0, 1, 2, 3 **and 4** are all ~1.0 entropy — a raw-LSB payload occupies
the low planes and leaves the higher planes structured, so uniform randomness through bit 4
means the *image itself* is noise-like. The image is 363x136 px with 28,470 distinct RGB
triples over 49,368 pixels (58% of pixels a unique colour) — heavily dithered.

**The gap:** in a carrier whose upper bit planes are already maximally random, **no
statistical LSB test can distinguish an encrypted, keyed-scatter payload from image
noise.** For this artifact only a correct key would settle it. The lane's own note records
this as *"NEGATIVE-with-limited-power, not closure"* — that phrasing should be preserved
wherever this result is cited.

This artifact matters: it is the **2012 Round 2 Book Hint** (md5 `df991ade67ee90a3fabf445fa3530ae5`,
verified against the iBotPeaches mirror manifest) and it carries the only real embedded
timestamp in the whole corpus (PNG `tIME` = 2012-01-11T07:19:29Z).

---

## G-G-06 — the OutGuess passphrase sweep covers 26 keys on 3 pages, not the space

`og_keysweep.sh` tried 26 candidate passphrases (`3301`, `cicada`, `CICADA`, `DIVINITY`,
`CIRCUMFERENCE`, `FIRFUMFERENFE`, `INSTAR`, `MOBIUS`, `ADHERE`, `WELCOME`, `PILGRIM`,
`TOTIENT`, `SHADOWS`, `AN END`, `845145127`, `7A35090F`, `1033`, `761`, `33011033`,
`1595277641`, and case variants) against pages 0, 4 and 26 — 51 extraction outputs in
`raw/og/keysweep/`.

**Not covered:** the other 55 pages, and every passphrase not on that list. A passphrase
sweep is a dictionary attack; a null result bounds nothing beyond the dictionary. Nothing
in this lane licenses "there is no OutGuess passphrase".

---

## G-G-07 — the 2013 MP3 got one deep pass and no spectrogram

`761_The-Instar-Emergence.mp3` (the single `audio_2013` artifact) was covered by
`mp3deep.py` (NEGATIVE), an entropy profile, an entropy-anomaly localisation (NEGATIVE),
exiftool, magic sniff and strings. It was **not** covered by:

- steghide (`NOT_APPLICABLE` — MP3 unsupported)
- any **spectrogram** pass, despite `sox` and `ffmpeg` both being installed. Cicada's 2013
  audio is exactly the artifact class where a visual spectrogram check is standard practice.
- MP3-specific stego tools (`mp3stego`, `mp3stegz`) — none installed, none tested.

**To close:** `sox in.mp3 -n spectrogram -o out.png` plus an `ffmpeg showspectrumpic` pass,
and inspect by eye. Cheap, and currently missing.

---

## G-G-08 — no artifact class was tested against a keyed/encrypted payload

A general limit that applies across every channel tested. Every instrument here is a
*statistical* or *structural* detector:

- appended-data: exact, but only finds data **past** a terminal marker
- entropy profile: finds a region whose entropy differs from its surroundings — **blind to
  a payload whose entropy matches**
- strings: finds plaintext and UTF-16 — **blind to anything encrypted or compressed**
- LSB: finds unencrypted or compressed raw-LSB — **blind to encrypted keyed-scatter**
- OutGuess/steghide: need the right algorithm and (for a keyed payload) the right key

**Therefore: an encrypted payload embedded by a keyed scheme is invisible to this entire
battery, in every artifact class.** That is not a defect in the execution; it is the
ceiling of statistical steganalysis. It should be stated whenever this lane's negatives
are cited.

---

## G-G-09 — OutGuess 0.4 was used where the historical tool is 0.2

See `TOOLS-AVAILABLE.md`. Validated against a known-positive carrier
(`artifacts/4gq25.jpg`), which is why the results are admissible — but validation on a
known-positive **does not bound disagreement on negatives**. A payload that 0.2 would
extract and 0.4 would not is not excluded.

---

## G-G-10 — `RESULTS.jsonl` is gitignored; the summary is the committed record

`RESULTS.jsonl` is ~50 MB and excluded from git. `RESULTS-SUMMARY.json` (~1 MB) is the
committed artifact and carries counts by (tool x finding), counts by
(tool x class x finding), per-class instrument coverage, **every HIT with its evidence
excerpt**, **every ERROR**, and grouped `NOT_APPLICABLE`. It also records the
`RESULTS.jsonl` byte length and SHA-256 so a regenerated copy can be checked against it.

What is **lost** if `RESULTS.jsonl` is deleted: the full (untruncated) tool output for
NEGATIVE rows. Regenerable by re-running the lane's scripts against `TARGETS.json`.

---

## G-G-11 — artifact classes outside this corpus were never touched

`TARGETS.json` covers what the repository holds. Not held, therefore not tested:

- **the 2012 chain** beyond the single `hkdgl.png` book hint. The lane's own note flags
  this: no other 2012-chain artifact has been checked for an embedded `tIME`/EXIF date
  because the 2012 chain is otherwise absent from the corpus (a Lane A gap).
- the 2014 and 2016 image sets beyond what the iBotPeaches onion mirror carried.
- any artifact recoverable only from the archives Lane D did not finish fetching.
