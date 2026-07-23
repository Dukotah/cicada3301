# Campaign XVIII — ARMADA RUN QUEUE

Prioritised heavy runs for the orchestrator. All ranked by probability of moving the
needle against LP2 (onion7 pages 0–55). Everything here is skip-tolerant-decoder-aware
(the validated Campaign-XVIII beam), so a "clean null" from any lane is now an
*unconditional* elimination, not one conditional on rigid alignment.

Confirm thresholds (this project): screen −6.5, confirm −5.5, English solve −4.0..−4.35,
false-positive ceiling −6.82, noise floor ~−7.5.

Corpus inventory (data/keys/armada18): 37 substantial texts (>=2000 words) totaling
~2.61M words + 5 small intentional rosetta files (LP1 English fwd/rev, cicada koans/PGP/
puzzle texts) + lp1_runes_as_key.{txt,json}. NONE deleted: the <2000w files are deliberate
keying material (LP1 plaintext / Cicada corpora), not failed downloads.

---

## RANK 1 — Skip-aware running-key sweep over the FULL armada18 corpus
This is the single genuinely-productive avenue the ELIMINATION-LEDGER leaves open: an
untried already-public keytext Cicada expected solvers to recognise. Falsifiable — the
right text at the right offset decrypts to high-scoring English. The armada18 set adds the
REAL Cornelius Agrippa Occult Philosophy (all 3 books — the prior data/keys/agrippa.txt was
Gibson's poem), Blavatsky Secret Doctrine v1, Levi History of Magic, Manly Hall, full
Lovecraft/Poe corpora, Plato Republic, Homer, KJB books, Dante (2 translations), Emerson
both series, clean Crowley (Lies/Law/777), and the Owen-Edwards Mabinogion — all
never-before-tested through the skip decoder.

**Command:**
```
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/campaign18_skip && \
PYTHONUTF8=1 python3 sweep.py --texts armada18 --pages "" 2>&1 | tee RUN-armada18-fullcorpus.log
```
Consumes: all 37 armada18 texts x 55 unsolved pages, both signs, both atbash, offset scan.
Hope: highest-prior lane. If any single primary source is the pad, it decrypts here to
readable English above −5.5. The Agrippa books especially were never tested as the real text.

---

## RANK 2 — Rosetta LP1-discipline key hypotheses (skip-aware)
Keys built to obey the PROVEN LP1 author discipline (sign=−1 always, phi(prime)/primes/
totient streams, thematic keywords DIVINITY/CIRCUMFERENCE/INSTAR/EMERGENCE/MOBIUS/PILGRIM,
continuous-across-pages, optional atbash pre-shift, optional +3 Caesar). Self-test passes:
pg73 phi(prime) reproduces ANEND. This is the "same generator family, decoded skip-aware"
bet — the LP1 F-skip interrupter is the same mechanic class as the LP2 doublet filter.

**Command:**
```
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/campaign18_skip && \
PYTHONUTF8=1 python3 armada/rosetta_keys.py --texts armada18 --pages "" 2>&1 | tee RUN-rosetta.log
```
(rosetta_keys.py exposes KEYSTREAMS/build_registry/high_prior; the sweep driver in the file
feeds them to `beam`. If a dedicated CLI is thin, orchestrator may instead import the
registry and drive `sweep.beam` per page.)
Hope: 2nd-highest prior. Same keys that solved LP1, now able to tolerate the desync that
made every rigid re-test score them as noise. If Cicada reused a phi/keyword key for LP2,
it surfaces here and NOWHERE else.

---

## RANK 3 — Numeric / PRNG keystreams (skip-aware), full run
874 number-theoretic + PRNG streams (primes mod29, prime gaps, phi iterates, pi/e/phi/
sqrt2/ln2 digit + pair encodings, all 841 Fibonacci mod-29 seeds, LCG/BBS/MT seeded with
the 6 Cicada constants). Smoke on pages 0–2 completed in 44.6s, best −6.092 (safely in
noise). Full run extends to all 55 pages.

**Command:**
```
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus && \
python3 analysis/campaign18_skip/armada/numeric_skip.py --full 2>&1 | tee analysis/campaign18_skip/RUN-numeric.log
```
Consumes: 874 generated keystreams x 55 pages.
Hope: LOW. The ledger already marks "number-theoretic/PRNG keystreams" as a dead family
under rigid tests; this re-tests skip-aware for completeness. Smoke gave no hint of signal
(best −6.09, well below −5.5). Run it, but expect null.

---

## RANK 4 — Payload-as-ciphertext (skip-aware + byte transforms)
Treat the 256-byte outguess payload as OTP ciphertext mod-29 under 12 Cicada key gens, plus
byte-level XOR/SUB/ADD vs 9 candidate streams, plus zlib/gzip/bz2/lzma sniff, plus 4x64
cross-block analysis. Note: this script runs its full analysis ON IMPORT (no __main__ guard)
and completed in <60s during verification — best skip score −6.855 (null), best entropy
collapse P1-SUB-ps_digits ent=6.587 (still high, no plaintext). Already effectively executed.

**Command:**
```
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus && \
python3 analysis/campaign18_skip/armada/payload_ciphertext.py 2>&1 | tee analysis/campaign18_skip/RUN-payload-ct.log
```
Consumes: the outguess payload bytes (both variants).
Hope: LOW, and mostly already-known-null from the verification run. Keep the log for the
record. No entropy collapse or magic bytes seen → payload is not a compressed/xored message.

---

## RANK 5 — Skip-model VARIANT confirmation (no new heavy run needed)
skipvariants.py already validated (1.8s smoke, PASS) that only Model A (key-skip baseline)
and Model C2 (interrupter + key-skip) are viable doublet mechanisms and BOTH are covered by
the existing Model-A decoder. Models B/C1/D/E need no separate decoder. So there is no new
heavy sweep to launch — the deliverable of this lane is the validation itself.

**Command (re-verify only, cheap):**
```
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus && \
PYTHONUTF8=1 python3 analysis/campaign18_skip/armada/skipvariants.py 2>&1 | tee analysis/campaign18_skip/RUN-skipvariants.log
```
Hope: N/A for solving — this de-risks RANK 1/2 by confirming the decoder's skip model is the
right one. Do NOT expand into a per-variant full-corpus sweep; the validation says it's
redundant with RANK 1.

---

## RANK 6 (external, low-prior, non-Python) — AN END deep-web page recovery
Only place a key might physically exist. Tor v2 dead (Oct 2021), CT-log brute ruled
non-viable (Campaign XIII). The one tractable-but-low-prior path: a finite lookup of
archived v2-onion corpora for the AN END page (hash 36367763…c2a8b4). Actionable but
requires external archive access, not a run on this box. Track as an OSINT ticket, not a
compute job.

---

## Summary priority

| Rank | Lane | Prior | Command head |
|------|------|-------|--------------|
| 1 | armada18 full skip-sweep | HIGH | sweep.py --texts armada18 |
| 2 | rosetta LP1-discipline keys | MED-HIGH | armada/rosetta_keys.py --texts armada18 |
| 3 | numeric/PRNG streams | LOW | numeric_skip.py --full |
| 4 | payload-as-ciphertext | LOW (near-done) | payload_ciphertext.py |
| 5 | skip-variant confirm | N/A (de-risk) | skipvariants.py |
| 6 | AN END v2-onion OSINT | LOW (external) | manual archive lookup |

Run RANK 1 and RANK 2 first and to completion. If both are clean nulls across all 55 pages,
the "untried public keytext" frontier narrows hard and the honest verdict tips toward
information-theoretic OTP-completeness rather than an undiscovered break.
