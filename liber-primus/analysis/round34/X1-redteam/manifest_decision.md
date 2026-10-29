# Round 34 / X1 -- capsule INTACT-FAIL settlement and manifest decision (NOT APPLIED)

_2026-10-29. Decision memo only. `handoff/capsule/MANIFEST.json`, `verify_capsule.py` and every data file are untouched; nothing is renamed. Source of the 13 items: `round34/P1-payload-promotion/manifest_regen/crlf_diagnosis.json` (13 rows, reproduced: 9 CRLF-only, `runes.canonical`, `groundtruth.validate`, `corpus.kjv`, `keytext.mabinogion`). Hashes below recomputed by X1 from the working tree (`manifest_proposed_hashes.json`). No git was run; "commit" below means a change in the file's own content, identified from the file and its lane docs._

## Verdict table

| item | P1 class | X1 settlement | action |
|---|---|---|---|
| 9 items: `dataset.liber_primus_json`, `gematria.primus`, `groundtruth.scream314_lp`, `groundtruth.solved_plaintext`, `groundtruth.provenance_stego`, `pads.lfs_request`, `corpus.english_quadgrams`, `method.lib_numchannel`, `method.nullcurve` | CRLF noise | **Settled: checkout-EOL noise.** In each, replacing CRLF by LF reproduces the recorded sha256 and byte count (`sha_match_after_CRLF_to_LF: true`, `LF_len_equals_manifest_bytes: true`). The manifest records the git blob form (`.gitattributes:11` `* text=auto eol=lf`); this working tree holds CRLF copies. | **Checker fix**, no manifest edit (below). |
| `runes.canonical` (`data/krisyotam_runes.txt`) | expected drift | **Settled: stale by a deliberate data edit.** LF length 43,739 equals the manifest; sha differs; reverting exactly the two Round 32 B2 / issue #12 separator edits (`-` -> `.` at seg 8 gap 12 and seg 40 gap 8) reproduces the recorded `5e0003aa...` (`P1 runes_revert_check.json`, also X1/R33). | **Manifest refresh** to the LF form (below), plus the checker fix for EOL. |
| `groundtruth.validate` (`tests/validate.py`) | real drift, 5,133 B vs 3,607 B | **Settled: the file was deliberately grown by Round 19; the manifest is stale; the file is right.** See below. | **Manifest refresh** (not a checker fix). |
| `corpus.kjv`, `keytext.mabinogion` | unexplained | **Settled: the recorded bytes are a different download; the on-disk files are Round 32 I2's substitute copies.** See below. | **Manifest text change** (below); nothing to "fix" on disk. |

## 1. `tests/validate.py`: what grew it, and why this is a manifest refresh

The manifest entry (`groundtruth.validate`, generated 2026-08-19T17:58:51Z) records sha256 `14d474ba...`, 3,607 B and a role of "reproduces all **5** solved LP2 pages". The file on disk is 5,133 B, contains no CR, and its docstring/comments say it was changed in Round 19: "AN-END (LP2 p56) ... Added R19 after the red-team found it was documented but NOT machine-guarded" (`tests/validate.py`, `SOLVED` list, `73.jpg` row), together with `_is_prime`, `phi_prime` and a `kind == "totient"` branch in `main()`.

**Exact test (X1, `rerun_validate_py_reconstruct.json`):** delete precisely those four pieces (the `_is_prime` + `phi_prime` functions, the 73.jpg entry with its three comment lines, the `elif kind == "totient":` branch) from today's file and hash the result: **3,607 bytes, sha256 `14d474baa289fcdec49c8bd479b59e69aa880ee9f3e4c918dd1c6033875988c6`, identical to the manifest.** So the entire 1,526-byte difference is the Round 19 AN-END guard and nothing else; the file did not drift in any other way. The Round 19 red-team (`round19/redteam/RESULTS.md:89`) is the lane that found the gap ("tests/validate.py validate only pages 01/03/05/06/14"). The commit that landed it is not identifiable without git; the content-level attribution above is exact.

**Why refresh, not a checker fix:** `validate.py` is the capsule's declared TRUST ANCHOR (manifest `trust_anchor`). A strengthened anchor (6 solved pages instead of 5) is the intended state; the checker should keep failing on any *unrecorded* change to it, and the manifest should record the new bytes. It currently passes (`tests/validate.py` -> ALL VALIDATIONS PASSED).

**Proposed manifest text** (`groundtruth.validate`):
```
"role": "THE TRUST ANCHOR. Reproduces all 6 solved LP2 pages (01, 03, 05, 06, 14 and AN-END p56 / 73.jpg, the last added in Round 19) from runes.canonical through this repo's cipher rig. Must print 'ALL VALIDATIONS PASSED' before any result here is trustworthy.",
"sha256": "dacb4fefd467ce0a9fa150a2dd2b13922c5560814c47eb148e9fe3c45ec45ded",
"sha1": "13a4a28a03c6e8c2a4c43f974f2e6a1714a4454f",
"bytes": 5133,
"notes": "Run first, always. R34-X1: grew from 3,607 B (sha 14d474ba...) when Round 19 added the AN-END (73.jpg) guard; removing exactly that guard reproduces the earlier sha."
```
and `trust_anchor.why` / `runes.canonical.provenance[2]`: "all 5 solved pages" -> "all 6 solved pages".

## 2. `runes.canonical`: record the LF form

The working tree holds CRLF (44,428 B); the repository form is LF (43,739 B). Record the LF form with the two deliberate corrections:
```
"sha256": "9b211a06a4bc31d60516edfad274f145aca0d8bc397d88889313d67adf0cbc55",
"sha1": "c52687b732941500994d00b36276a699c760d821",
"bytes": 43739,
"notes": "<existing note> R34-X1: updated after the Round 32/33 issue-12 correction (two word-separator characters, seg 8 gap 12 and seg 40 gap 8, '.' -> '-'; credit RETSAM3301); the pre-correction sha was 5e0003aa7f7dde3b238d17c5f964790dbf6bf9db5edacc4a5ec0bad81c6f4bce. LF-normalised hash (the on-disk copy in a CRLF checkout is 44,428 B)."
```

## 3. `corpus.kjv` and `keytext.mabinogion`: a different download, not corruption

Evidence that these are not the recorded bytes and why:
* `round32/I2-multiregister-readjudication/RESULTS.md:10-11` records both as **absent** before Round 32 I2 ("`data/keys/mabinogion.txt` ... absent (original 617,362 B) -> copied from `analysis/bookcipher/books/mabinogion.txt` (617,553 B, same text, header differs)"; "`data/kjv.txt` ... absent (original 4,436,268 B) -> copied from `analysis/bookcipher/books/kjv.txt` (4,455,950 B)"). The on-disk byte counts (617,553 and 4,455,950) equal those copies, and both files carry mtime 2026-10-28 16:15 (the restore). Both pairs are sha256-identical to their `analysis/bookcipher/books/` sources (X1 recomputed: kjv `0204adae...`, mabinogion `e177d7c2...`).
* Neither the raw nor the LF-normalised hash matches the recorded one, and the byte counts differ (kjv 4,436,268 recorded vs 4,355,979 LF / 4,455,950 raw; mabinogion 617,362 vs 607,632 / 617,553), so this is not an EOL effect. The manifest's own notes already warn: for `corpus.kjv` "a refetch may NOT reproduce this SHA-256 even though the book is the same"; for `keytext.mabinogion` "these SHA-256s are a record of WHAT WAS TESTED, not a reproducible fetch target".
* The original bytes are not recoverable from this machine. What they were used for is unaffected: `english_quadgrams.txt` (committed, derived) is the reproducible artifact; the substitutes feed only the Round 32 I2 panel's EN_KJV / EN_MODERN / EN_HALFVOWEL / EN_NOVOWEL models.

**Proposed manifest text** (both items keep `status: gitignored-fetchable`; add, do not delete):
```
"notes": "<existing warning> R34-X1: the bytes recorded here (sha256 0f1a83cb..., 4,436,268 B) were the Round <= 31 copy and are no longer on disk. Round 32 I2 restored the file from analysis/bookcipher/books/kjv.txt: now 4,455,950 B (CRLF form; 4,355,979 B LF), sha256 0204adaed1f25700aa854218cae63c7172228c41088f335e99167a071eed83c0, sha1 459c8a46cbb76c0769ac26670ab2cfc9b9711c96. Same work, different Gutenberg issue/header. Results in Rounds <= 31 refer to the old bytes; the Round 32+ nine-register panel was built on the substitute.",
"sha256_current_substitute": "0204adaed1f25700aa854218cae63c7172228c41088f335e99167a071eed83c0",
"bytes_current_substitute": 4455950
```
and for `keytext.mabinogion`: recorded 617,362 B / `80dc6f0d...` -> current substitute `e177d7c2ff357bc5e3f506c7131d158d8b8f5e05883110bdf495f0d9d7f49886`, 617,553 B (LF 607,632 B), sha1 `a7878161be3e3159373661a00721428b5691b969`. Keep `sha256`/`bytes` as the *historical record* and let `verify_capsule.py` treat `gitignored-fetchable` + `sha256_current_substitute` as a second accepted hash (so the item reports OK(substitute) instead of INTACT-FAIL while the original stays recorded).

## 4. The checker fix (9 CRLF items + CRLF forms of items above)

`verify_capsule.py::sha256_file` hashes raw bytes. Proposed change (not applied): for items whose path extension is text (`.py .md .json .txt .tsv .csv .sh .cff`) and whose raw sha does not match, also hash the CRLF->LF-normalised bytes and, if that matches (sha and length), report `OK (eol)` instead of `INTACT-FAIL`. Binary types (`.bin .jpg .png .npz .npy .pdf`) are never normalised (`.gitattributes:14-21`). This leaves a real content change (validate.py, the runes edit) failing, which is the point of the checker. It also makes the capsule stop reporting 13 INTACT-FAIL on every Windows checkout.

Expected result after (a) the checker fix, (b) the manifest edits above, (c) the P1 payload edits: INTACT-FAIL 0 on this machine (9 CRLF -> OK(eol); runes -> OK(eol) after the refresh; validate.py -> OK; kjv/mabinogion -> OK(substitute)).

## 5. Interaction with the payload rename

None of the 13 is caused by the payload. `P1 manifest_regen/MANIFEST.regen.json` changes only `payload.canon_256` and adds `payload.canon_256_superseded` (and the summary count 103 -> 104); the edits above are independent and can be applied on top of it in one manifest regeneration.
