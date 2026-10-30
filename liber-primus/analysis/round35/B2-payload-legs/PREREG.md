# Round 35 / B2 -- payload legs (closeout) -- PREREG
_2026-10-30, written before any fetch/run beyond reading the repo._

Scope: R30-B1 (canon-as-key + 8 canon x T2/folly XOR rows over T2.bin, folly.bin) and R30-B2 (folly.bin, 2.jpg legs), for canon_256_superseded.bin (comparator) and canon_256.bin (promoted).

Provenance read from the repo (no hashes of full files were recorded except a prefix):
* folly.bin: 3368 B, md5 prefix 0c7d18e8 (round29 L2 FINDINGS; ELIMINATION-LEDGER l.811); == wisdom == T3.bin. Origin: 2013 Cicada ISO /tmp file; GitHub mirror cicada-solvers/iddqd path 2013/02/folly (candidate).
* 2.jpg: ~595 kB (exif_authored.json), no hash recorded. Downloaded by the armada (armada.mjs T2 brief). 
* T2.bin: 7524 B, entropy 7.978, chi2 226, no full hash recorded; produced by OutGuess (-r, seed 38370) on 2.jpg ("stage04 rev-index extract"). `outguess` is not installed here.

Plan: fetch folly candidate into fetch_try/ subdirs (data only, never executed), accept as the original only if size=3368 and md5 starts 0c7d18e8. 2.jpg: attempt mirror fetch; accept only if usable; T2 requires outguess with seed 38370 plus a recorded hash to compare -- none recorded beyond length/entropy/chi2, so a regenerated T2 could only be checked against those three statistics (weak identity, stated as such). Q5 applies to any input failing its check: file not_covered and stop that leg.
Legs run via original scripts (shim for pycryptodome) with original controls first, comparator then promoted. No git, write only here, nproc=1, no "solved/closed/exhausted".
