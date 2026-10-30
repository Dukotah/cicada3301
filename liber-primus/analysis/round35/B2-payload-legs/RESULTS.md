# Round 35 / B2 -- payload legs (closeout) -- RESULTS
_2026-10-30. PREREG.md written first. One Python process at a time, nproc=1, a few minutes of compute, no git, nothing written outside this directory. Downloaded files were treated as data only (never executed)._

## Inputs (detail: `inputs.json`)
| input | origin | recorded identity | obtained | match |
|---|---|---|---|---|
| `folly.bin` | fetched: cicada-solvers/iddqd `2013/02/folly` (= `wisdom`); upstream 2013 ISO /tmp file | 3368 B, md5 prefix `0c7d18e8` | 3368 B, md5 `0c7d18e82cdac189d165706db4064a84`, sha256 `7e5ec097...c385a` | YES (size + md5 prefix; stored folly XOR rows reproduce) |
| `T2.bin` | fetched: iddqd `lp_outguessed/04.txt` (community OutGuess extract of 2.jpg, seed 38370). Not regenerable here (no outguess, no compiler, not in `data/`) | 7524 B, H 7.978, chi2 226, byte0 0x40; **no full hash recorded anywhere** | 7524 B, H 7.978, chi2 226.4, byte0 0x40, md5 `8c6c06e51928905cfcb85adca2f5db19`, sha256 `35d31e61...f6db` | STATISTICAL only; plus the 8 stored T2 XOR rows and T2 struct-ID reproduce exactly (4 d.p., head hex) |
| `2.jpg` | fetched: iddqd `liber-primus__images--unsolved/2.jpg` | "595 kB", dqt_sig `3e0f1ac7d0b3`, marker sequence, 2400x3600; **no full hash recorded** | 595338 B, md5 `c7d1943adc0db3c818080b50a91152ad`, sha256 `74e955eb...e34`; round29 `jpeg_fingerprint.py` (unmodified) gives dqt_sig `3e0f1ac7d0b3`, same markers | STRUCTURAL only; stored `jpg_trailer_len` = 0 reproduces |
| canon superseded / promoted | committed `pp49_51/` | `4c8dc855...` / `3b9b07d9...` | same | YES |

## Per-leg table
| leg | control (original, run with the leg) | comparator (superseded canon) reproduces stored R30? | promoted result | changed? |
|---|---|---|---|---|
| **R30-B1 cipher battery**, canon-as-key (all `blob:*` keys incl. `blob:canon`, T2, folly; AES/RC4/Blowfish/DES/3DES, ~40 keys) over T2, folly, canon | AES-256-CBC plant recovered; negative 0/500 (control run, comparator, promoted rerun); first promoted run 1/500 (see notes) | YES: struct-ID of all 3 blobs equal, `cipher_hits` [] equal | 0 cipher hits | **No** |
| **R30-B1 cross-XOR**, 12 rows (8 canon x T2/folly) | same detector | YES: 12/12 rows equal (entropy, length, head hex, hits) | 0 hits, all rows structureless; min H 7.0876; the 8 canon rows moved by <= 0.015 bits, the 4 T2/folly rows bit-identical | **No** |
| **R30-B1 gpg/openssl** (13 gpg literal-packet rows, 6 openssl modes) | same | YES: 13 rows equal | 13 rows identical to comparator, 0 detector fires | **No** |
| **R30-B2 folly** (OpenPGP scan, gpg raw, 4 prepends, canon[:32] AES over folly) | RSA-2048 plant flagged, random not; real gpg message parses, random does not | YES (only the gpg first-run "keybox created" stderr and the control message's random salt differ) | folly legs identical to comparator (byte0 0xbf invalid; AES key idx<32 unchanged) | **No** |
| **R30-B2 2.jpg** (post-EOI trailer leg) | same | YES: trailer length 0 | trailer 0 -> empty payload, nothing to test; identical | **No** |
| R30-B2 canon legs (carry-over, now with all inputs present) | same | YES (every substantive field) | not a plausible modulus (even, small factors), gcd(n)=1, byte0 0xcb scan same, gpg parse same; c^e mod n entropy 7.6149 -> 7.6599; canon_tail AES stats move at the echoed bytes | **No** |

## Notes and honesty limits
* Control wrinkle: the original R30-B1 negative control uses unseeded `os.urandom` (500 trials). The first promoted run drew 1/500 false fire (fp 0.002), so that run's control gate printed False; its cipher results are identical (`R30-B1/promoted_run1/`, kept). A rerun of the promoted arm passed 0/500. The stored estimate is 0/500; 1/500 is within noise for a detector with fp of order 0.1%, but the gate is probabilistic.
* "T2 and 2.jpg are the original files" is not hash-verified because no full hash was recorded. Strongest evidence: the stored T2^folly and T2^canon XOR entropies (4 d.p.) and head hex, and T2 struct-ID, reproduce exactly.
* The R30-B2 2.jpg leg inspects only bytes after the last FFD9 (none). T2 (the OutGuess payload of 2.jpg) is covered by R30-B1 only; the B2 OpenPGP/gpg legs never read T2.
* Harness limits as in R34-P1: pycryptodome shim (I added `AES.encrypt` to my copy for the original positive control). "Unmeasured" becomes "measured, null in the same sense as before", not "payload is null".

## Verdict
Nothing changed under the promoted canon. The R34 residual `not_covered` legs for R30-B1/R30-B2 are measured, with the T2/2.jpg identity caveat above. Q5 not triggered.

## Files
`PREREG.md`, `RESULTS.md`, `inputs.json`, `ledger_patches.json`, `ledger.json`, `make_ledger.py`, `run_b1.py`, `run_b2.py`, `cmp_b1.py`, `shim/`, `inputs/` (staged data), `fetch_try/` (raw fetches), `R30-B1/{control,superseded,promoted,promoted_run1}/results.json` + logs + `compare.json`, `R30-B2/{superseded,promoted}/results.json` + `compare.json`.
