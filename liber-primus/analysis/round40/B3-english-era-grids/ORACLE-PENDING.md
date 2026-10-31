# ORACLE-PENDING (R40-B3): one flagged row, protocol-mandated, with the lane's non-binding observations

`HUMAN-ORACLE.md` requires any row that clears its pre-registered bar to be flagged-for-oracle. The adjudicator is the repo owner; this file only supplies the bundle.

**Row.** `KDF|03000000:iter_md5_1000:self:mod29:rev|v01|U|keyskip2` = secret bytes `03 00 00 00` (B-04 `num_le`), KDF `iter_md5_1000` (R15 `kdf.iterated`, MD5 x 1000), salt = the secret itself ("self"),
reduction `mod29`, direction `rev` (reversal of the 184-symbol SHA-256-counter expansion), sign +1 (decode C + K), atbash off, relation keyskip2, L=120, panel argmax EN_MODERN.

**Why it is flagged.** pmax120 = 6.528 >= the null12 bar 6.342 at the lane's actual N (591 KDF survivors per relation). It does NOT clear the N=1e6 bar (8.999) nor the bar at the number of configs screened (692,064; 8.868).
The L=240 gate does not exist for this row: a `rev` KDF key in R15/R16 was the reversal of a 184-symbol buffer, so no 240-rune read and no second page can be keyed. By PREREG section 5/addendum 5 such a row is flagged directly.

**Bundle** (`ORACLE-KDF-iter_md5_1000-rev/bundle.json`, produced by `oracle_kdf.py`): provenance and reproduce line, decodes at L=120/150/170/174 under both relations with panel z-vectors, IoC, mds, transliteration, the null12 cell, and the exceedance probability.
Missing from the bundle by construction: a second independent page, the hitfn20 held-out clause (key buffer too short), the commit hash (no `git` in this lane).

**Observations (not an adjudication).**
- Under the fitted POT null the probability that the maximum of 591 draws reaches 6.528 is 0.6% for this single cell; the lane ran 8 (grid x relation) cells, so about 5% for at least one such crosser somewhere.
- The score FALLS as the read is extended inside the 184-symbol buffer (keyskip2: 6.528 at L=120, 6.145 at L=150, 5.891 at L=170 and 5.531 at L=174; the register shifts EN_MODERN -> EN_HALFVOWEL), the opposite of a true key.
- The L=120 transliteration (`FICNIFGEWWIAOORSNCENSUWENCLACOYNGAEBHEUEBYMMUTHPEEXEHUF...`) has English letter-pair flavour but no word structure.
- The fwd twin (same secret, KDF, salt, reduction, forward buffer) scores 1.957.

Ledger status stays `measured` with a `flagged-for-oracle` note until the owner records PASS or NOISE-CROSSER.

## Adjudication (coordinator, 2026-10-31)

Read per `HUMAN-ORACLE.md` by the coordinator on the owner's delegated authority: the L=120/150/170/174 transliterations
(`FICNIFGEWWIAOORSNCENSUWENCLACOY…`) contain no words in any of the twelve registers; the score falls monotonically as the
read is extended (6.528 → 5.531); the row fails the bar at the number of configurations screened (8.868) and the N=1e6
bar (8.999); the forward twin scores 1.957. **NOISE-CROSSER.** The owner may overrule by reading the bundle. Ledger row:
`measured`, note "flagged-by-protocol; adjudicated noise-crosser (coordinator)". Policy note (revised after Round 40 X1): report both bars; neither actual-N nor screened-N is the bar of record for a flag until null12 is refit on the sweep survivor population (Round 41 I1) — until then only the N=1e6 bar gates a flag.
