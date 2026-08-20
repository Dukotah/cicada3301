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
