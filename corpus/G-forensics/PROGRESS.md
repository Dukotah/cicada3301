# Lane G — PROGRESS

Started 2026-08-19. Repo branch `corpus-sweep`. All work under `corpus/G-forensics/`.

- [x] Read prior work (`liber-primus/analysis/stego/STEGO-VERDICT.md`) before repeating anything
- [x] Target enumeration + SHA-256: **486 artifacts** -> `TARGETS.json`
      (56 lp_page, 380 onion_artifact, 40 onion_html, 9 cicadaos_pad, 1 audio_2013)
- [x] Pure-Python battery core (`gcore.py`), JPEG deep parser (`jpegdeep.py`)
- [x] LP pages: container/segment parse, appended-data, ICC interior (56/56) -> RESULTS.jsonl
- [x] DQT/ICC clustering across 56 pages -> `raw/lp_dqt_partition.json`
- [ ] Tool install in WSL (exiftool/binwalk/sox/ffmpeg pending; outguess NOT in Ubuntu repos -> build from source)
- [ ] Entropy profiles, strings, LSB, MP3 spectrogram, pads, onion blobs
- [ ] OutGuess blank-control (G-02)

## RESUMED 2026-08-19/20 UTC after network outage (ENOTFOUND)

- [x] **RECON-A G-02 blank-control OutGuess run — CLOSED.** Three Ghostscript 10.06.0
      2400x3600 400-DPI control JPEGs (blank RGB, blank grayscale, text) all yield a
      "successful" OutGuess extraction (seed 24127 / len 7383); the two blanks are
      byte-identical outputs and blank-vs-text share an 828-byte prefix then diverge.
      The shared-prefix phenomenon is reproduced in provably empty carriers =>
      **the 1417-byte prefix is a tool/template artifact, not a payload.**
      Rows appended by `g02_emit.py`; raw in `raw/g02_control/`.
- [x] **Correction to STEGO-VERDICT.md:** it reports 3 capacity-length OutGuess false
      positives (pages 0, 4, 26). All 58 pages were run (`og_allpages.sh`): there are
      **16** (0,4,26,40-48,51-54), all sharing the same 32-byte head, and all 58 pages
      decode the same header seed 41408 / len 58152 regardless of extraction success.
- [x] External instrument battery extended: **exiftool now covers all 486 artifacts**
      (`ext_tools.py`); **steghide now covers 148 examined + 338 NOT_APPLICABLE**
      (`steg_sweep.py`). binwalk partial (~87 of 486) at ~26 s/artifact.
- [x] `RESULTS-SUMMARY.json` built (`mksummary.py`) — committable distillation of the
      gitignored 50 MB `RESULTS.jsonl`: counts by tool x finding and tool x class x
      finding, per-class instrument coverage, every HIT with evidence, every ERROR,
      grouped NOT_APPLICABLE, plus the source file SHA-256.
- [x] `TOOLS-AVAILABLE.md`, `GAPS-G.md`, `REPORT-G.md` written.
- [ ] Still open: spectrogram pass on the 2013 MP3; zsteg; jsteg/F5; binwalk completion.
