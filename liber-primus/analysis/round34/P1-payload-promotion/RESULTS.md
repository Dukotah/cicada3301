# Round 34 / P1 -- payload promotion: `payload_resolved.bin` re-fed to the unfed readers -- RESULTS

_2026-10-29. `PREREG.md` written first and followed (one deviation, listed in "Deviations"). One Python process at a time, nproc=1, about 25 min of compute in total. No git; nothing written outside this directory; no file in `data/` or `analysis/` renamed, copied or overwritten. Every reader below was run on the **original source or a stated faithful re-implementation**, its control first, and a **canon comparator** (same harness on the old `canon_256.bin`) alongside._

## Verdict

* **No reader changed.** Every reader's verdict under the corrected bytes equals its canon comparator's; no best score newly clears a bar; every canon comparator reproduces the published or stored canon result where one exists. Q5 is **not triggered**.
* **Capsule:** the regenerated `MANIFEST.json` copy verifies the corrected payload; the **13 INTACT-FAIL items are the same 13** as with the current manifest (none added by the promotion): **9 are pure CRLF checkout noise, 4 are real drift unrelated to the payload**.
* **GO for the rename**, conditional on the coordinator accepting the legs that could not be re-run (inputs gitignored/absent, see "Not re-runnable") and on the three companion decisions at the end (`canon_256.hex`, `canon_256_decpref.bin`, applying the regenerated manifest).

## Per-reader table

"Changed?" is judged by the PREREG rule (verdict flip, new bar crossing, or comparator not reproducing the published result). Score movements are in legacy quadgram `score_norm` (bar -5.5; null max about -6.8) and panel `pmax` (hitfn20 bars 7.3835 pair / 7.6342 exact, N = 10^6).

| reader | harness | control (run first) | subset | decodes | best vs bar (canon -> resolved) | changed? |
|---|---|---|---|---|---|---|
| **R16-KDF** (`round15/KDF`, via `round13/B04/seeds.py:289`) | original `kdf.py`, `sweep.run_stage` (nproc 1), `sk.beam_decode` beam 400 max_skip 3, L = 120 head; `build_secrets()` asserted equal to my reconstruction of the 7 `canon256_*` entries | **PASS**: K2 plant (PBKDF2-SHA256-10000, salt 3301, mod29, "THE PRIMES ARE SACRED") over the 7 resolved secrets + the plant secret, 10,368 decodes: planted config rank 1 at -4.186. Null band reproduces the original (mean -7.399, max -6.773 -> bar -5.5) | 7 payload-derived secrets of 534 (raw, rev, head32, tail32, hex lower, hex UPPER, decpref); **6 of 7 change bytes**, head32 identical | per arm: stage A 9,072 (27 KDF x 3 salts x 2 red x dir x sign x atbash) + stage B 9,856 (8 best published-A families x 11 salts); 37,856 in total + 10,368 control | stage A -6.464 -> **-6.408** (pmax 5.07 -> 4.89); stage B -6.488 -> -6.408; bar -5.5, pmax bar 7.6342; 0 over bar. Published lane-wide A best (534 secrets) -6.259, no `canon256_*` row in its top 50 | **No** |
| **R30-B1** (`round30/B1-blob-crypto`) | **minimal re-implementation**: original `battery.py` unmodified, `pycryptodome` (absent) replaced by a `cryptography`-package shim (`shim/Crypto`), gpg + openssl arm of `run.py`; **canon blob only** (T2.bin, folly.bin absent) | **PASS**: original positive (AES-256-CBC plant recovered through the battery path) and negative (0/500 false fires); shim known-answer vectors AES/RC4/Blowfish/DES pass | the canon blob as ciphertext under 38 keys (original about 40: `blob:T2`, `blob:folly` missing), ~7 cipher families, plus gpg -d with 13 passphrases and 6 openssl modes | battery over 38 keys per arm; 13 gpg + 78 openssl calls per arm | 0 cipher hits both; gpg parses it as a literal-data packet and emits 22 B under every passphrase, **identical bytes (sha1 7f54831c...) and identical 13 rows** canon vs resolved (and identical to the stored `results.json` rows); struct-ID identical (H 7.16965, chi 254.0, 161 distinct); no detector fire | **No** (canon-as-key and XOR legs over T2/folly: **not re-runnable**) |
| **R30-B2** (`round30/B2-rsa-gpg`) | original `b2_rsa_gpg.py` exec'd with path/shim substitutions only; `folly.bin` and `2.jpg` absent so only the canon legs ran (modulus detector, gcd with the 4096-bit n, c^e mod n, OpenPGP header scan, `gpg --list-packets` raw and four prepends, canon[:32] AES key over canon[32:]) | **PASS** (original controls): planted RSA-2048 modulus flagged plausible, random 256 B not flagged, real gpg symmetric message parses, random blob does not parse | the canon blob | 7 test legs per arm | canon comparator reproduces the stored `b2_results.json` on every substantive field (only the first-run "keybox created" stderr line differs). Resolved: `plausible_rsa_modulus` False (even, small factors, as canon), gcd(n) = 1, byte0 0xcb LiteralData scan unchanged, raw gpg stdout identical, prepend parses identical; c^e mod n entropy 7.6149 -> 7.6599, printable 0.369 -> 0.365 (echo of the 3 bytes) | **No** (folly/2.jpg legs **not re-runnable**; the canon[:32] AES key over them is unchanged by construction, idx < 32 identical) |
| **recon `h1_index`** (`recon/lp2h_index/h1_index.py`) | original source, table path substituted | **PASS**: the script's own `[setup]` gate (55 pages, 12,956 runes, 594 lines, 256 bytes) reproduced; scorer samples THE PRIMES ARE SACRED -4.18, PARABLE -4.10, random -7.39 | the 256-byte table | T1a-T1e, 11 decode models, T2, T3 | canon reproduces `FINDINGS.txt` (T1a 0.5955, T1b 0.7202, T1c 0.0809, T1d 0.0484, best -7.200). Resolved: T1a 0.5384, T1b 0.2550, T1c 0.0809, T1d 0.0484, best -7.225 (E2); every model -7.2 to -7.6; verdict CLEAN NULL both; no p < 0.01 | **No** |
| **campaign18 `payload_skip.py`** | original source, path substituted | original has none; **added and PASS**: English plant enciphered key-skip under the resolved payload mod 29, decoded with the same `SW.beam`: -4.186, recovery 1.00 (both signs) | 4 variants (canon / decpref, fwd / rev; decpref patched in the resolved arm) x 2 signs x 2 atbash x 55 pages | 880 per arm (SWEEPROW persisted, `validate_store` ok) | canon -6.756 (page 15, sign -1, atbash) reproduces the published -6.756 exactly; resolved **-6.744** same configuration; 0 hits over -5.5; best pmax 5.09 / 4.71 vs 7.6342 | **No** |
| **campaign18 `payload_ciphertext.py`** | original source, both paths substituted | original has no planted control (internal sniff/entropy only); **added and PASS**: `beam_decode` recovers a key-skip message under a known payload-derived key, -4.186 | payload as ciphertext, P1 and P2 | 12 beam keys + 54 byte transforms + compression probes per arm | section 1 best -6.855 (reproduces the published log) -> **-6.927**; 0 hits; decompression hits 0 both; best transform entropy 6.587 -> 6.602 (statistic, not a hit) | **No** |
| **campaign18 `numeric2_skip.py`** Part B (payload, all offsets) + `payload_hex_nibbles` | original module, payload and hex loaders patched, same 55 pages | **PASS (added)**: plant under the payload key at offset 0 and 17 found by the same `_score_page`, -4.186 | 4 payload variants x sign x atbash x all offsets x 55 pages; hex-nibble stream at offsets 0-4 | Part B + hex, ~10^5 short screen beams per arm (not persisted) | Part B best screen **-5.833 both** (reproduces the published -5.833; best window avoids the 3 bytes), hex-nibble -6.089 both; 0 hits | **No** |
| *extra:* `pp49_51/hash_hunt.py` (AN END preimage hunt, reads canon `.bin`, `.hex`) | original source, `here` substituted | **PASS**: plant target = sha512(resolved) -> FULL-512 MATCH found | 12 representations x 10 hashes | 120 per arm | 0 matches (full or partial) both | **No** |

SWEEPROW stores (round32 I2 panel, `validate_store` passes): `R16-KDF/sweep_rows_A_{canon,resolved}.jsonl` (9,072 rows each), `c18-payload_skip/sweep_rows_{canon,resolved}.jsonl` (880 each). Not persisted: R16-KDF stage B and the K2 control, `numeric2_skip`, `payload_ciphertext`, `h1_index` (legacy-scored, short or tiny, scores in the stdout files) -- see Deviations.

## Not re-runnable (Q5 clause, "corrected payload: harness not re-runnable")

`analysis/armada_osint/extracts/T2.bin`, `artifacts/folly.bin` and `artifacts/2.jpg` are gitignored and absent (no filesystem-wide search was made), and `pycryptodome` is not installed.

* **R30-B1:** the canon blob **as a key** over T2 and folly (`fit_key` hash modes, RC4 raw/hash, Blowfish/DES/3DES keys; trunc-mode AES keys use bytes 0..31 and are unchanged by construction) and the 8 canon x T2/folly cross-XOR rows. These are the legs where the 3 bytes can matter; the re-run covers the canon blob as ciphertext only.
* **R30-B2:** the folly and 2.jpg-payload legs of the OpenPGP scan/gpg parse (they do not read canon bytes), and the canon[:32] AES key over them (key bytes unchanged).
* **R17 pad** (carried from R33-B1): dense-prefilter inputs absent.

These residual legs are small (about 10^2 trial decrypts and 8 XOR streams, each judged by a detector whose measured false-fire rate is 0/500) but the result there is **unmeasured, not null**. They are listed in `not_covered` of the patched rows.

## Capsule (`manifest_regen/`)

Files: `MANIFEST.orig.copy.json` (byte copy), `MANIFEST.regen.json` (**the regenerated copy**), `regen.py`, three verifier copies and logs, `crlf_diagnosis.json`, `runes_revert_check.json`.

`MANIFEST.regen.json` = the original with `payload.canon_256` sha256 / sha1 / bytes taken from the resolved bytes (**sha256 3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290**, was 4c8dc855...), a PROVENANCE line citing R19-C1, Round 33 B1/X1 and the owner's 2026-10-29 decision, the six still-contested bytes kept in `notes`, plus a new item `payload.canon_256_superseded` (old sha 4c8dc855..., path `canon_256_superseded.bin`); `summary` counts 103 -> 104. The generator code, timestamp and every other item are untouched.

`verify_capsule.py` is a copy with only `HERE`/`REPO`/`MANIFEST` re-pointed and an optional path-override map:

| run | manifest | result |
|---|---|---|
| A (baseline) | current `MANIFEST.json`, real tree | OK 75, SKIP 1, ABSENT 14, **INTACT-FAIL 13** (reproduces the Round 33 X1 count) |
| B (pre-rename) | regen copy, real tree | INTACT-FAIL 14 (the 13 + `payload.canon_256`), ABSENT 15 (+ the superseded file): the expected state before the coordinator renames |
| C (post-rename simulation) | regen copy with `canon_256.bin` -> staged resolved bytes and `canon_256_superseded.bin` -> staged old bytes | OK 76, SKIP 1, ABSENT 14, **INTACT-FAIL 13**: `payload.canon_256` and the superseded item both verify; the 13 are the same 13 |

**Diagnosis of the 13 (test: replace CRLF by LF and re-hash; `.gitattributes` says `* text=auto eol=lf` and `*.bin binary`, so the working tree is a CRLF checkout of LF content):**

| class | items | evidence |
|---|---|---|
| **CRLF checkout noise (9)** | `dataset.liber_primus_json`, `gematria.primus`, `groundtruth.scream314_lp`, `groundtruth.solved_plaintext`, `groundtruth.provenance_stego`, `pads.lfs_request`, `corpus.english_quadgrams`, `method.lib_numchannel`, `method.nullcurve` | sha256 **matches the manifest after CRLF -> LF**, LF byte length equals manifest `bytes` |
| **real drift, same length (1)** | `runes.canonical` (`data/krisyotam_runes.txt`) | LF length 43,739 = manifest, sha differs. Reverting exactly the two R32-B2 edits (`-` back to `.` at seg 8 U+16D2\|U+16E1 and seg 40 U+16BB\|U+16AA) in the LF text **reproduces the manifest sha 5e0003aa...** (`runes_revert_check.json`). The manifest is stale by the deliberate R32-B2 data correction |
| **real drift (1)** | `groundtruth.validate` (`tests/validate.py`) | no CR at all; 5,133 B on disk vs 3,607 B recorded: the script grew after the manifest (2026-08-19) |
| **neither CRLF nor explained here (2)** | `corpus.kjv`, `keytext.mabinogion` (gitignored-fetchable corpora) | LF-normalised sha and length match neither (kjv 4,355,979 LF / 4,455,950 disk vs 4,436,268 recorded; mabinogion 607,632 / 617,553 vs 617,362). The manifest itself warns that refetched Gutenberg-class files differ; these are local copies that are not the recorded bytes. Not related to the payload |

Nothing in the 13 is a consequence of promoting the payload. Fixing the 4 real ones (runes sha, validate.py sha, kjv, mabinogion) is a separate manifest-maintenance decision and is **not** done in the copy, so the copy differs from the current manifest only in the payload items. `handoff/capsule/build_manifest.py:260` hard-codes `payload.canon_256`; it recomputes the sha from disk, so a rebuild after the rename would give the same hash but drop the PROVENANCE line and the superseded item.

## Other readers of `canon_256.bin` (inventory, from a scoped grep of `analysis/`)

Run here: the seven above and `hash_hunt.py`. Already on the corrected bytes: R19-C1, R28-L5, R20-SRESCOPE, B-05 (R19-C1 `b05_rerun.py`), R33-B1's four rows. **Not run** (inventoried only): `pp49_51/{campaign9,keytest,campaign20_extcipher,anend_preimage_3new,anend_preimage_broad,blake_closure,characterize}.py` (older campaign-VII/IX/XX scripts and AN END preimage hunts; the hash ones are the same class as `hash_hunt`, which was run), `campaign11_pin_the_filter.py`, `campaign12/payload_forensics.py`, `campaign14/probes.py`, `round29/L2-blob-cross/attack.py` (hard-codes a `/mnt/c/Users/dukot/...` path and needs T2/folly), `round28/L2/{reader,keysweep}.py` (comparator for the byte resolution itself), `round13/B05/prf.py`, `round17/P3_tables/build_pads.py`. `round17/P3_tables/pads_manifest.json` and `results*.json` record the **old pad's sha** and are historical: leave them.

## Deviations from PREREG and honest limits

* PREREG said SWEEPROW "where a decode happened" under the I2 panel; I persisted rows for the two sweep-style readers that matter most (KDF stage A, `payload_skip`), and for none of: KDF stage B and K2 control, `numeric2_skip` (~10^5 short beams), `payload_ciphertext` (12 decodes), `h1_index` (11 models). The first-pass KDF/skip results were produced without rows; rows came from a second, identical pass (`run_rows.py`) whose best scores reproduce the first pass exactly (-6.464, -6.408, -6.756, -6.744), which also doubles as a determinism check.
* R16-KDF stage B has **no counterpart in the original run** (`results_B.json` was never written); I ran it as an extension over the families of the published stage A. It adds coverage but is not a like-for-like comparator of anything published.
* R30-B1/B2 are re-implementations around absent inputs (above). The shim's AES/RC4/Blowfish/DES known-answer vectors pass; 3DES was exercised through the battery only (no separate vector). B2's first-run gpg stderr line ("keybox created") differs from the stored one and is ignored.
* The decpref arm uses a decpref patched at idx 45/50/246 (the R33-B1 assumption); no independently corrected decpref exists.
* All verdicts are conditional on the English-quadgram legacy score and the I2 panel as before; the non-English power of these decoders was not re-measured here. A result "not changed" means the reader's output on the corrected bytes is the same kind of null as on the old bytes; it does not make the payload a null.

## Coordinator decisions

1. **Rename GO/NO-GO.** GO recommended: `canon_256.bin` -> `canon_256_superseded.bin`, `round19/C1/payload_resolved.bin` -> `canon_256.bin`, with the PROVENANCE text in `ledger_patches.json` (`promotion_text`). The residual unmeasured legs (canon-as-key over T2/folly) are the only argument for waiting; they would need T2/folly regenerated.
2. **`canon_256.hex`** (pp49_51) mirrors the old bytes and is read by `numeric2_skip` and `hash_hunt`; after the rename it will disagree with `canon_256.bin` unless regenerated (`hexlify` of the new file; `inputs/resolved/canon_256.hex` is the staged candidate).
3. **`canon_256_decpref.bin`** keeps the three uncorrected bytes (and the capsule item `payload.canon_256_decpref`); patch it or label it legacy.
4. **Apply `manifest_regen/MANIFEST.regen.json`** (or equivalent edit) at the rename, and decide separately whether to refresh the 4 non-payload drifted shas.
5. `LEDGER.json` / `ELIMINATION-LEDGER.md` / `analysis/README.md` / `PICKUP-HERE.md`: apply `ledger_patches.json`; `ledger.json` is the lane's audit row. C-CANON-PAYLOAD-3BYTES can move to resolved only after the rename.

## Files

`PREREG.md`, `RESULTS.md`, `ledger_patches.json`, `ledger.json`, `make_ledger.py`; drivers `stage_inputs.py`, `run_kdf.py`, `run_b1.py`, `run_b2.py`, `run_scripts.py`, `run_rows.py`, `shim/Crypto/`; staged inputs `inputs/{canon,resolved}/`; `chain.log`, `rows_chain.log`; per reader: `R16-KDF/` (results_*.json, rows_summary_*.json, sweep_rows_A_*.jsonl, run.log, stdout.txt), `R30-B1/` (results.json, run.log), `R30-B2/` (results.json, compare.json), `recon-h1/` (stdout_*.txt, control.json), `c18-payload_skip/` (control.json, stdout_*.txt, sweep_rows_*.jsonl, rows_stdout_*.txt), `c18-payload_ciphertext/` (control.json, stdout_*.txt), `c18-numeric2/` (control.json, results_*.json), `extra-hash_hunt/` (stdout_*.txt, control.txt), `manifest_regen/`.
