# Lane A — PROGRESS

Started 2026-08-19. Resume from the first unchecked box. Everything below is on disk.

## Environment (verified)
- `gpg 2.4.9` at `/usr/bin/gpg` (Git Bash). **No apt/pgpy needed.**
  - It is an MSYS binary: `GNUPGHOME` and file args must be POSIX (`/c/...`), not `C:\...`.
    Passing a Windows path silently yields NO_PUBKEY, which reads like a failed signature.
  - Isolated keyring: `pgp/.gnupg-lane-a/`
- `curl` at `/mingw64/bin/curl`. No wget, no 7z. `python3` = 3.12.
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
- [x] `gpg --verify` on all 37 messages → **36 VALID, 1 NO_SIGNATURE** → `SIGNATURES.json`
      (G-02 CLOSED)
- [x] Signature-timestamp timeline extracted, 36 rows, 2012-01-05 → 2017-04-04 (G-09 partial)
- [x] Extracted the hex-encoded binaries carried **inside** signed messages →
      `signed-payloads/` (see REPORT-A.md — this is the highest-fidelity source that exists)
- [x] archive.org sweep: item `Interconnectedness_201805` byte-confirms the signed MP3
- [x] Wayback CDX walks: `845145127.com`, `1033adacic.{cf,ga,gq,ml}`, `uncovering-cicada.wikia.com`
- [x] `1033adacic.*` 2015 artifacts pulled from Wayback raw (`id_`) → `2015-1033/`
- [x] Pastebin `yEiTHhvF` (2017-04-04 message of record) → `2016-2017/`

## Running / partial
- [ ] `wiki-uncovering-cicada/images/` — 829-file Fandom pull (`_tools/bulk_fandom.py`,
      resumable, log `_logs/bulk_fandom.log`). **MUST use `?format=original`** or Fandom
      returns a WebP re-encode ~3% of original size. Even with it, JPEGs come back 18 bytes
      short of the wiki's own declared SHA-1 — PNGs match exactly. See CONFLICTS-A.md.
- [ ] `cijhho123/` — 447-file / 206 MB pull from github.com/cijhho123/cicada3301
      (`_logs/batch_cijhho.tsv`, log `_logs/batch_cijhho.log`). Contains the 2012 posters,
      the 845145127.com site capture, the MIDI, the outguess outputs.

## Not started (ranked, see GAPS-A.md)
- [ ] `krisyotam/cicada3301` (529 MB) and `0x676f64/Cicada-3301` (54 MB), `BHQST/3301` (100 MB)
- [ ] archive.4plebs.org original 4chan image bytes
- [ ] IA full-text search for further items; `3301.iso` inner-file listing
- [ ] Non-English boards
