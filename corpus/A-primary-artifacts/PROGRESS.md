# Lane A — PROGRESS

Started 2026-08-19. Killed once by a network outage (ENOTFOUND); resumed 2026-08-20.
Resume from the first unchecked box. Everything below is on disk.

## Environment (verified)
- `gpg 2.4.9` at `/usr/bin/gpg` (Git Bash). **No apt/pgpy needed.**
  - It is an MSYS binary: `GNUPGHOME` and file args must be POSIX (`/c/...`), not `C:\...`.
    Passing a Windows path silently yields NO_PUBKEY, which reads like a failed signature.
  - Isolated keyring: `pgp/.gnupg-lane-a/`
- `curl` at `/mingw64/bin/curl`. No wget, no 7z. `python3` = 3.12, **Pillow 12.1.1 present**.
- **This shell is Git Bash, not WSL.** `/mnt/c/...` does not exist here; use `C:/Users/...`.
- **`python3` defaults to cp1252 on this box.** Always `open(..., encoding="utf-8")` and
  never `print()` non-ASCII — that is what killed the first Fandom bulk run.
- archive.org throughput is ~50 KB/s here — **always background archive.org pulls.**
- Fandom/GitHub raw are fast.

## Done
- [x] Read `corpus/INVENTORY.md` §2 and `corpus/GAPS.md` G-01/G-02
- [x] Canonical public key fetched from 3 independent sources, all fingerprint
      `6D854CD7933322A601C3286D181F01E57A35090F` → `pgp/keys/`
      (keys.openpgp.org, keyserver.ubuntu.com, and the on-disk jaxonkuipers copy;
      the ubuntu copy carries **315 signature packets** — third-party certifications,
      an unmined dataset of its own)
- [x] Found that **17 of the repo's 42 `.asc` files were 199-byte GitHub "429 Too Many
      Requests" stubs**, not signatures. Refetched all 17.
- [x] Extracted the hex-encoded binaries carried **inside** signed messages →
      `signed-payloads/`
- [x] archive.org sweep: item `Interconnectedness_201805` byte-confirms the signed MP3
- [x] Wayback CDX walks: `845145127.com`, `1033adacic.{cf,ga,gq,ml}`, `uncovering-cicada.wikia.com`
- [x] `1033adacic.*` 2015 artifacts pulled from Wayback raw (`id_`) → `2015-1033/`
- [x] Pastebin `yEiTHhvF` (2017-04-04 message of record) → `2016-2017/`
- [x] `wiki-uncovering-cicada/images/` — Fandom pull **COMPLETE: 829/829, 0 failures,
      345 MB** (232 had landed before the outage; the rest were pulled this session).
      **MUST use `?format=original`** or Fandom returns a WebP re-encode ~3% of original size.
      343 files match the wiki's declared SHA-1; **486 do not, 288 of them short by exactly
      18 bytes** — see `CONFLICTS-A.md` C-05.
- [x] `krisyotam/` (34 MB), `Hadyn_cicada/` (30 MB), `micheloosterhof_cicada-2016/`

### 2026-08-20 session
- [x] **Third independent message corpus located and collected**: upstream
      `github.com/iBotPeaches/cicada_3301` → `ibotpeaches/` (60 files). It carries **20
      distinct Cicada signatures nothing else in this corpus held**, almost all 2013
      (the SSSS shares, the coordinate messages, `tcp-server`, `no-more-testing`,
      `do-not-share-this-information`).
      Two upstream filenames literally contain angle brackets (`<space>.asc`,
      `<data-blob>.asc`); NTFS forbids those, so they are stored as `_space_.asc` and
      `_data-blob_.asc`. Bytes are unmodified; the rename is recorded in MANIFEST.json.
- [x] **`SIGNATURES.json` rebuilt and widened** — 140 files verified (80 distinct by
      sha256): **137 VALID, 2 INVALID (same damaged file, two mirror paths),
      1 NO_SIGNATURE**. **56 distinct signatures. Exactly one signing key.**
      Range 2012-01-05T03:46:03Z → 2017-04-04T23:23:28Z (1916 days). G-02 CLOSED.
      Corpus total at handover: **1,686 files, ~673 MB**.
- [x] **`SIGNATURE-TIMELINE.json` emitted** (G-09): every signature-packet timestamp,
      chronological, plus inter-signature gaps and year/hour/weekday distributions.
      Timestamps are read from the packets themselves, so a file that fails to verify
      still contributes its real timestamp.
- [x] **The INVALID signature is a mirror defect, not a forgery.** Cause isolated to a
      single missing blank line in the krisyotam mirror's armor. A clean copy of the same
      message from an independent mirror verifies. See `CONFLICTS-A.md` C-01 and
      `pgp/repaired/README.md`.
- [x] **G-01 partially closed and measured.** The 2012 chain images, the 2012/2013 poster
      photographs and the `845145127.com` site save are on disk from two mirrors, and 7 of
      8 imgur-hosted chain images are **byte-identical** to the Internet Archive's own
      independent capture. See `REPORT-A.md` §3.
- [x] **`1CcV1.jpg` — the 2012 opening image — has two byte-streams, and the archive's is
      the degraded one.** The community copy carries 61 plaintext bytes after EOI; imgur's
      re-encode dropped them. `CONFLICTS-A.md` C-02. This is the most important
      methodological finding of the session.
- [x] **`TRAILING-DATA.json`** — every JPEG/PNG in the corpus parsed structurally (markers
      walked, `FF00` stuffing and RST markers handled) to find the true end of the image and
      measure what lies past it. **8 files carry data after their real EOI/IEND**, 7 files do
      not parse as well-formed images at all. Includes a 3.49 MB second JPEG appended to
      `onion6.jpg`, a 336 KB trailer on Liber Primus page 05 that ends in a byte-reversed
      JPEG header, and a 10.9 KB trailer on a **signature-attested** file.
- [x] `_tools/grab.py` resume bug fixed: it skipped any path already in MANIFEST.json even
      when the file was absent from disk, so every resumed batch was a no-op.
- [x] `GAPS-A.md`, `CONFLICTS-A.md`, `REPORT-A.md` written.

- [x] `_tools/bulk_fandom.py` crash cause found and fixed: it `print()`ed raw wiki filenames
      to a cp1252 stdout, so the first non-ASCII name raised UnicodeEncodeError and killed
      the run. Names are now ASCII-escaped before printing.

- [x] `cijhho123/` — **COMPLETE: 447/447, 192 MB.** The 198 files missing after the crash
      were refetched (`_logs/batch_cijhho_resume.tsv`). This recovered the whole of the
      previously-empty `2016/`, `2017/`, `2014/additional images/` and `2014/additional
      docs/` trees, including the **2016 oak-tree-with-runes image**
      (`cijhho123/2016/2016/additional images/4gq25.jpg`) and the **2013 entry image**
      (`cijhho123/2013/additional images/1357366592898.jpg`), both visually confirmed.

## Running / partial
- (nothing running at handover)

## Not started (ranked, see GAPS-A.md)
- [ ] `krisyotam/cicada3301` remainder (529 MB total upstream), `0x676f64/Cicada-3301`
      (54 MB), `BHQST/3301` (100 MB), `scream314/cicada3301`
- [ ] The 315 third-party certifications on the public key (`pgp/keys/…ubuntu…asc`) —
      an untouched social-graph dataset
- [ ] archive.4plebs.org / desuarchive original 4chan bytes (see GAPS-A A-01: /b/ 2012 is
      almost certainly unarchived anywhere)
- [ ] IA full-text search for further items; `3301.iso` inner-file listing
- [ ] Non-English boards
