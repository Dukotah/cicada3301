# Lane G — TOOLS AVAILABLE

The instrument inventory this lane actually had, with versions, and — more importantly —
**what each instrument can and cannot see.** A negative result is only as strong as the
instrument's power, so the "blind to" column is the load-bearing one.

Environment: **WSL Ubuntu** (`wsl -d Ubuntu`), repo mounted at
`/mnt/c/Users/dukot/projects/cicada3301`. Verified 2026-08-19/20 UTC by
`toolcheck2.sh`; the earlier `checktools.sh` predates the outage.

---

## Present

| tool | version | path | what it examines | blind to |
|---|---|---|---|---|
| **outguess** | **0.4 "Universal Stego"** (Provos et al., 1999-2021) | `/usr/local/bin/outguess` (built from source; **not** in Ubuntu repos) | JPEG DCT-coefficient stego, OutGuess algorithm, with or without `-k` passphrase | any other DCT scheme (JSteg, F5, nsF5), spatial LSB, appended data. **See the version caveat below.** |
| **exiftool** | 13.50 | `/usr/bin/exiftool` | EXIF, XMP, IPTC, Photoshop IRB, ICC, MakerNotes, PDF/PNG/GIF/ID3 metadata, non-standard APPn/chunks | DCT coefficients, appended data past the terminal marker, anything not in a metadata container |
| **binwalk** | (Ubuntu package, no `--version` string) | `/usr/bin/binwalk` | embedded container signatures at any offset | nothing, in the wrong direction — inside compressed/encrypted regions it produces **false positives at a high rate**; see the note below |
| **steghide** | 0.5.1 | `/usr/bin/steghide` | steghide-embedded payloads in **JPEG / BMP / WAV / AU only** | every other container (→ `NOT_APPLICABLE`), every non-steghide scheme, and any payload under an unknown passphrase |
| **ghostscript** | 10.06.0 | `/usr/bin/gs` | — (used to *produce* the G-02 control JPEGs through the same pipeline as the LP2 pages) | — |
| **ImageMagick** | 7.1.2-18 Q16 | `/usr/bin/convert` | format conversion, geometry, colour census | — |
| **ffmpeg** | 8.0.1 | `/usr/bin/ffmpeg` | audio/video decode, spectrogram generation | — |
| **sox** | SoX_ng 14.7.0.9 | `/usr/bin/sox` | audio transforms, spectrograms | — |
| **python3** | 3.14.4 | `/usr/bin/python3` | the lane's own pure-Python battery | — |
| **Pillow** | 12.1.1 | (python) | bit-plane LSB analysis, colour census | encrypted/keyed-scatter LSB (see `REPORT-G.md`) |
| **numpy / scipy** | 2.4.6 / 1.18.0 | (python) | statistics for the above | — |
| **openssl** | 3.5.5 | `/usr/bin/openssl` | hashing, PGP-adjacent primitives | — |
| **xxd** | — | `/usr/bin/xxd` | hex dumps | — |
| **ruby / gem** | 3.3.8 | `/usr/bin/ruby` | (host for `zsteg`, which is not installed) | — |

## Absent

| tool | why it matters | consequence |
|---|---|---|
| **zsteg** | the standard PNG/BMP LSB scanner; covers palette-index, alpha-channel and per-channel bit orders the lane's own Python does not | PNG LSB coverage rests on this lane's own implementation only. Installable with `gem install zsteg` — ruby is present. |
| **stegdetect** | Provos's statistical JPEG stego detector (jsteg/jphide/outguess/F5 discrimination) | there is **no independent statistical check** on the OutGuess conclusions; the lane used OutGuess itself as its own detector. Unmaintained and hard to build on modern glibc. |
| **foremost** | file carving with header/footer validation | carving rests on binwalk (poor validation) + the lane's own appended-data check |
| **jsteg** | the JSteg DCT scheme | **JSteg was never tested on any artifact.** A real coverage gap — see `GAPS-G.md` G-G-03. |
| **stegsolve** | interactive bit-plane/colour-channel viewer | no human-eye visual pass over bit planes; only statistical tests were run |

---

## Version caveat on OutGuess — read before citing any OutGuess result

The historically documented Cicada tool is **OutGuess 0.2**. The binary available here is
**OutGuess 0.4 "Universal Stego"**, a later fork. They are not guaranteed to agree.

**What was done about it:** `og_validate.sh` re-extracted a known-good carrier
(`artifacts/4gq25.jpg`) with 0.4 and compared byte-for-byte against the prior-work payload
held in the repo. The result is recorded in `RESULTS.jsonl`. **Instrument validation on a
known-positive is the only reason any 0.4 result in this lane is admissible**, and it
validates 0.4 for *this* carrier and command only. It does not prove 0.2 and 0.4 agree in
general, and in particular it does not prove they agree on **negative** results — a payload
0.2 would find and 0.4 would not is not excluded by this check.

## Note on binwalk's error rate in this corpus

binwalk `--signature` reports a HIT on **all 56 Liber Primus pages**. Inspection of a
representative page shows the matches are:

- offset 0 — `JPEG image data, JFIF standard 1.01` (the container itself)
- offset 0x1A6 — `Copyright string: "Copyright Artifex Software 2011"` (the Ghostscript ICC
  profile, present identically in every page)
- a spurious `JBOOT STAG header` deep inside the DCT entropy stream, claiming an image size
  of 591,379,275 bytes in a 595,338-byte file

None is a payload. **A bare binwalk match count is not evidence in this corpus** — short
magic sequences occur by chance inside compressed data. Every binwalk HIT in
`RESULTS-SUMMARY.json` must be read with its evidence excerpt, never as a count.

binwalk also costs **~26 seconds per artifact** here, which is why its coverage of the
380-file `onion_artifact` class is partial (`GAPS-G.md` G-G-02).

---

## Reproducing the environment

```bash
sudo apt install libimage-exiftool-perl binwalk steghide sox ffmpeg imagemagick ghostscript ruby
gem install zsteg                     # closes the PNG LSB gap
# outguess is NOT packaged for Ubuntu; build from source:
git clone https://github.com/resurrecting-open-source-projects/outguess
cd outguess && ./autogen.sh && ./configure && make && sudo make install
```

Scripts in this lane that use these tools: `ext_tools.py` (exiftool / binwalk / file),
`steg_sweep.py` (steghide), `og_validate.sh` (instrument validation),
`og_allpages.sh` (per-page OutGuess), `og_keysweep.sh` + `ks_run.sh` (passphrase sweep),
`g02_control.sh` + `g02_control2.sh` (the RECON-A G-02 control), `g02_emit.py`
(records the control into `RESULTS.jsonl`), `mksummary.py` (builds `RESULTS-SUMMARY.json`).
