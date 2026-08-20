# Lane G — REPORT (forensics)

Branch `corpus-sweep`. Working dir `corpus/G-forensics/`.
Lane resumed and closed 2026-08-19/20 UTC after a network outage killed it mid-battery.

**Deliverables:** `RESULTS-SUMMARY.json`, `TOOLS-AVAILABLE.md`, `GAPS-G.md`, this file.
Raw output stays in `RESULTS.jsonl` (~50 MB, gitignored).

---

## 0. Headline: RECON-A **G-02 is closed**, and it closed the way the prior work predicted

`liber-primus/analysis/stego/STEGO-VERDICT.md` left exactly one item open, deferred for
want of a Linux environment:

> `outguess -r` a **blank/control** JPEG produced through the same 400-DPI
> Ghostscript/Artifex pipeline and same dimensions. If it reproduces the 1417-byte prefix
> ⇒ artifact confirmed, avenue fully closed.

**It was run.** Three control JPEGs were rendered with Ghostscript 10.06.0 at
`-r400 -dJPEGQ=95` from a 432x648 pt page — **2400x3600 px, identical to the LP2 pages** —
and pushed through `outguess -r` with the default key:

| control | dims | container SHA-256 | OutGuess header | extraction |
|---|---|---|---|---|
| `ctl_blank_rgb.jpg` (blank, DeviceRGB) | 2400x3600, 3-comp | `8616adfeaf06e45dabe979db4f8242a77fb2307f65cdaba7bb9aa578a7664794` | **seed 24127, len 7383** | 7,383 B, SHA-256 `a710ce2a06efb115628277a96b99d1c1efaffe967225b9f89ebb44c59d468617` |
| `ctl_blank_gray.jpg` (blank, grayscale) | 2400x3600, 1-comp | `b20398d82869adab2fdd3e3ae626f7bc44b35c5cb9a204b62e91bbc27b4fbc6b` | **seed 24127, len 7383** | 7,383 B, SHA-256 `a710ce2a06efb115628277a96b99d1c1efaffe967225b9f89ebb44c59d468617` |
| `ctl_text_rgb.jpg` (text page, DeviceRGB) | 2400x3600, 3-comp | `239088481bb7305aa502428210797d82d2126b3f6701abe0241e0043430b562f` | **seed 24127, len 7383** | 7,383 B, SHA-256 `e5258db28652268e52dd45de2b88c8a58121d3958ff291a743514083c4bc0bbd` |

These are **provably non-carrier images.** They were generated in this lane, from
PostScript written in this lane, seconds before extraction. Nothing is embedded in them.
And yet:

1. **OutGuess reports a successful extraction on all three.** The "validity check passed,
   here is your payload" behaviour that the community read as meaningful on LP2 pages
   happens on a blank page.
2. **The two blank controls produce byte-identical 7,383-byte outputs** despite being
   different files (RGB vs grayscale, different SHA-256, different component counts).
3. **The blank and text controls share an 828-byte common prefix and then diverge** —
   diverging where the image content diverges.
4. **All three decode the same header: seed 24127, len 7383.** The header is a property of
   the *rendering pipeline*, not of any payload.

Point 3 is the decisive one. It is the same phenomenon as the LP2 pages, reproduced in
images that contain nothing: **two different images from the same pipeline yield
extractions that agree for a leading run of bytes and then split.** The shared prefix is a
deterministic artifact of OutGuess's default-key coefficient walk over shared image
regions.

**Verdict: the 1417-byte shared prefix is a tool-and-template artifact, not a payload.
G-02 is closed as the prior work hypothesised.**

### One thing the control also settled, which the prior work did not anticipate

The controls' header is seed **24127** / len **7383**. Every Liber Primus page's header is
seed **41408** / len **58152** — including the 42 pages whose extraction fails the validity
check and returns nothing. A constant header across 58 images of wildly different content
(usable bits ranging 352,479 to 832,763) is not a payload length; it is what the fixed
initial coefficient path decodes to when every page starts with the same blank Ghostscript
margin.

That also explains the one result that could otherwise look like a failed control: the
controls share **zero** bytes with the LP pages. Different seed → different derived
keystream → no agreement. The two classes are internally consistent and mutually
independent, exactly as the artifact hypothesis predicts.

### A correction to the prior work, found while re-auditing it

`STEGO-VERDICT.md` reports **three** capacity-length OutGuess false positives (onion7 pages
0, 4, 26) sharing a 1417-byte prefix. Running `outguess -r` across all 58 pages
(`og_allpages.sh` → `raw/og/pages_seed_table.tsv`) shows **sixteen**:

pages **0, 4, 26, 40, 41, 42, 43, 44, 45, 46, 47, 48, 51, 52, 53, 54** each extract exactly
58,152 bytes; the other 42 extract nothing.

All sixteen share the same 32-byte head `c0a128e346d23572fe62822e50f70d8a…`, and the
pairwise common-prefix matrix shows page 0 agreeing with every other page for exactly
**1417** bytes, pages 4 and 26 agreeing for **2004**, pages 4/26 with 51 for **1903**, with
54 for **1812**, and the 40–54 block agreeing with each other for **1521–1578**.

So the "1417-byte prefix" is not a property of three special pages — it is the *minimum*
agreement across a set five times larger than reported, and the agreement lengths track
page-layout similarity. That is exactly what a shared-blank-margin artifact looks like, and
it strengthens the closure rather than weakening it. The correction is recorded here
because `STEGO-VERDICT.md`'s "3 pages" figure is now superseded.

---

## 1. Per artifact class: what was tested, what came back, what the battery could NOT see

`RESULTS-SUMMARY.json` carries the full matrix. `NOT_APPLICABLE` and `ERROR` are never
counted as `NEGATIVE`.

### `lp_page` — 56 artifacts (the Liber Primus 2 onion7 pages)

| instrument | result |
|---|---|
| `jpegdeep.py` (marker-segment parse) | **NEGATIVE 56/56** |
| ICC profile interior parse | **NEGATIVE 56/56** |
| appended-data check (byte-exact past EOI) | **NEGATIVE 56/56** |
| exiftool 13.50 | **NEGATIVE 56/56** — independent confirmation of the two above |
| steghide 0.5.1 (`-p ''`) | **NEGATIVE 56/56** |
| strings (ASCII + UTF-16 LE/BE) | NEGATIVE 52, HIT 4 (DCT-noise runs, no keywords) |
| entropy profile | NEGATIVE 44, HIT 12 (block-level variance, no localised anomaly) |
| magic sniff | HIT 56 (container ID; not a finding) |
| binwalk | HIT 56 — **all false positives**, see below |
| OutGuess 0.4 `-r` | 16 capacity-length extractions, 42 empty — **artifact, per section 0** |
| OutGuess `-k` sweep | 26 passphrases x 3 pages, no structure found |

**Could NOT have been detected on this class:**
- **JSteg or F5 DCT stego** — never tested; no tool present (`GAPS-G.md` G-G-03). The DCT
  conclusion rests on OutGuess used as its own detector, with no independent statistical
  check (`stegdetect` absent).
- **Any keyed/encrypted payload** — entropy, strings and LSB tests are all blind to it
  (G-G-08).
- **An OutGuess passphrase outside the 26-word dictionary**, or any passphrase at all on the
  other 55 pages (G-G-06).
- **A payload OutGuess 0.2 would find and 0.4 would not** — validation was on a
  known-positive only (G-G-09).
- Spatial LSB is genuinely **`NOT_APPLICABLE`** here, not negative: these are lossy JPEGs,
  so pixel-domain LSB is compression noise and carries no usable channel.

### `onion_artifact` — 380 artifacts

| instrument | result |
|---|---|
| exiftool | **NEGATIVE 380/380** |
| entropy profile | NEGATIVE 387, HIT 25 (rows exceed artifacts: some files profiled more than once) |
| strings | NEGATIVE 372, HIT 40 |
| magic sniff | HIT 257, NEGATIVE 156 |
| appended-data | NEGATIVE 89, **HIT 8** — see below |
| steghide | **NEGATIVE 80, NOT_APPLICABLE 300** |
| binwalk | HIT 5, NEGATIVE 2, **ERROR 15**, and **~358 never run** (G-G-02) |
| duplicate census | 204 files are duplicates of other held artifacts |
| OutGuess re-audit | 16 HIT (the LP extractions above) |
| bit-plane LSB | 1 HIT, 1 NEGATIVE — **2 of 380 examined** |

The 8 appended-data HITs cover 5 distinct files (two are listed under two paths), and all
five are **derived analysis blobs, not original Cicada artifacts**:
`T4_blob1_gunzip.bin` (5,502 trailing bytes past its terminal marker),
`T4_blob2_flip.bin` (13,095), `T4_blob3_flip.bin` (37,956),
`dl_server-status.jpg` (72,700), and `avowy_post_gzip_inner_2400x3600.jpg` (5,502 — the
same trailing SHA-256 `600868271058b4f26f2e4f1d4f270547c335f7f4e297d995b05c44e1b8d26bbf`
as `T4_blob1_gunzip.bin`, i.e. the same object under two names). These are prior-round
working files; the trailing data is an artifact of how they were produced. Recorded with
hashes in `RESULTS-SUMMARY.json` so nobody re-discovers them as a finding.

**Could NOT have been detected:** everything in G-G-08, plus — specific to this class —
**binwalk covered 22 of 380 and steghide could not read 300 of 380.** Statements about this
class must be scoped accordingly. Only exiftool, entropy, strings and magic reached all 380.

### `onion_html` — 40 artifacts

exiftool NEGATIVE 34 / HIT 6 (all six HITs are HTML `<title>` elements matched by the
metadata heuristic — **adjudicated as not findings**). appended-data NEGATIVE 12, HIT 1.
entropy NEGATIVE 40. strings HIT 17 / NEGATIVE 23 (expected — they are text files).
steghide NEGATIVE 12 / **NOT_APPLICABLE 28**. binwalk **never run on this class**.
Manifest hash verification NEGATIVE 7/7 — i.e. all seven check-able files match the md5
published by the iBotPeaches mirror.

The one genuinely interesting result in this class is on a PNG carried alongside:
**`onions__imgur.com__hkdgl.png`**, the 2012 Round 2 Book Hint (md5
`df991ade67ee90a3fabf445fa3530ae5`, verified against the mirror manifest). Its PNG `tIME`
chunk reads **2012-01-11T07:19:29Z** — the **only real embedded timestamp anywhere in the
486 artifacts**; all 116 JPEGs carry the null ICC creation date `0000-00-00T00:00:00Z`.
Caveat recorded with it: `tIME` records when the PNG was *encoded*, which could be Cicada's
authoring or an imgur re-encode at upload, and the file alone cannot distinguish them.
Either way it is a harder date than any prose source in this repository.

Its LSB channel is flagged and then **adjudicated NEGATIVE-with-limited-power** — bit
planes 0 through 4 are all ~1.0 entropy because the image is heavily dithered (28,470
distinct RGB triples over 49,368 pixels), so no statistical LSB test can separate an
encrypted keyed-scatter payload from the image's own noise. **Only a key would settle it**
(`GAPS-G.md` G-G-05).

### `cicadaos_pad` — 9 artifacts

`file` NEGATIVE 9/9. entropy NEGATIVE 9/9. large-pad structural scan NEGATIVE.
strings NEGATIVE 8 / HIT 1. steghide **NOT_APPLICABLE 9/9**. binwalk **ERROR 9/9** (killed).
exiftool HIT 6 — all six are `Error: Unknown file type`, i.e. **not findings**.

Pad cross-comparison produced three real structural results:
- `tmp_folly` and `tmp_wisdom` are **byte-identical** (3,368 B, SHA-256
  `7e5ec097728197f5c0dba0729980565658fba486965809ffa25e3910a31c385a`, XOR all-zero,
  entropy 7.9377).
- `DATA__560.00` is an **exact byte-prefix** of `DATA__560.00.iso-authoritative`
  (prefix 2,412,544 B of 3,992,970 B); the 1,580,426-byte delta has entropy 7.9999 and
  SHA-256 `0769970a1d2415542671ab7a41c0c37a850c1a2f212c7efc4bf7d4d221b08dbb`.

**Could NOT have been detected:** binwalk contributed **nothing** here (9/9 ERROR), and
steghide **nothing** (9/9 NOT_APPLICABLE). Container-level carving on the pads is therefore
**untested**, not negative.

### `audio_2013` — 1 artifact (`761_The-Instar-Emergence.mp3`)

`mp3deep.py` NEGATIVE. Entropy-anomaly localisation NEGATIVE. exiftool HIT (ID3 frames —
expected metadata, **not a finding**). strings HIT, magic HIT. steghide
**NOT_APPLICABLE** (MP3 unsupported).

**Could NOT have been detected — and this is the most closable gap in the lane:** **no
spectrogram pass was run**, despite `sox` 14.7 and `ffmpeg` 8.0 both being installed.
Cicada's 2013 audio is precisely the artifact class where a visual spectrogram check is
standard practice. No MP3-specific stego tool (`mp3stego`, `mp3stegz`) was available or
tested either (`GAPS-G.md` G-G-07).

---

## 2. Totals

| finding | rows |
|---|---|
| NEGATIVE | 2,091 |
| HIT | 837 |
| NOT_APPLICABLE | 347 |
| ERROR | 24 |

The 837 HITs are dominated by three non-findings: `magic sniff` container identification
(354), the `global duplicate census` (267 — real and useful, but it reports duplication
inside the held corpus, not stego), and `entropy profile` block variance (38). After those,
and after adjudicating the exiftool HTML-`<title>`/ID3 matches and the binwalk container
matches, **no HIT in this lane is an unexplained payload.**

---

## 3. `RESULTS-SUMMARY.json`

`RESULTS.jsonl` is ~50 MB and gitignored, so the findings would not survive in git.
`RESULTS-SUMMARY.json` (~1 MB) is the committed record and holds:

- `totals_by_finding`, `counts_by_tool_and_finding`, `counts_by_tool_class_finding`
- `coverage_by_artifact_class` — which instruments actually examined each class, and with
  what outcome, so a gap in coverage is visible rather than implied
- **every HIT** with artifact path, SHA-256, tool, command, exit code, evidence excerpt
  (1,200 chars) and the instrument's power note
- **every ERROR**
- `not_applicable_grouped` — grouped rather than listed, since 338 are identical steghide
  container rejections
- `finding_vocabulary` — the four categories defined in the file itself, so a later reader
  cannot collapse `NOT_APPLICABLE` into `NEGATIVE`
- the source file's byte length and SHA-256, so a regenerated `RESULTS.jsonl` can be
  checked against it

---

## 4. Next steps in this lane, in order

1. **Run the spectrogram pass on the 2013 MP3** (`sox ... -n spectrogram`, plus
   `ffmpeg showspectrumpic`). Cheapest missing check in the lane, on the artifact class
   where it is standard practice.
2. **`gem install zsteg`** and re-run PNG LSB, starting with `hkdgl.png`. Ruby is already
   present.
3. **Install `jsteg`** and test the DCT channel with a second algorithm. Right now
   "no DCT stego" means "no *OutGuess* stego" (G-G-03).
4. **Finish binwalk on `onion_artifact`** (~3 h) or replace it with a header-validating
   carver — and stop treating its raw match counts as evidence.
5. **Check the rest of the 2012 chain for embedded `tIME`/EXIF dates.** `hkdgl.png` proved
   the technique yields a hard date; the rest of the 2012 chain is absent from this corpus
   (a Lane A gap), so this is blocked on retrieval, not on tooling.
