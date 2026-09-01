# Round 18 / Marsaglia — RESULTS

_2026-09-01. Verdict: **NEGATIVE.** Pre-registration: `PREREG.md`. Machine-readable:
`results.json`, `pads_manifest.json`. Ledger: `R18-MARSAGLIA`._

## Verdict

The **Marsaglia Random Number CDROM (1995)** is not the LP2 keystream, under any of the
readings tested. This closes the item Round 17's SYNTHESIS named FOUND-NOT-SWEPT as the
cheapest live source in the public-pad branch.

| | |
|---|---|
| Pads swept | **63 / 63** (60×`bits.NN` + `calif`/`canada`/`germany.bit`, 630 MB) |
| Offsets scanned | **14,453,903,260** (5,420,213,722 effective after ×0.375 survival) |
| Keystream readings | 6 byte builders × {fwd, rev} × 2 signs = 24 configs/pad |
| Best score_norm | **−6.720** (`bits.10` / `mod29_rev` / sign −1) |
| Pre-registered bar | −5.5 **and** ≥ null_max + 0.5 |
| `benchmark/null.threshold_for(1.45e10)` | **−5.222** (stricter than −5.5; best is far below both) |
| HITS | **none** |
| Best head decode | `XYGHTTUBEATANAYJACYOUYOREAWWEOSNCEORAIASONEATHEAEANJSRTHATTXOEME` — gibberish |

Every one of the 63 per-configuration shuffle nulls (n=200) has `null_max + 0.5` above the
best score, so no configuration reaches the bar by either criterion. The best score across
the entire 14.45-billion-offset sweep (−6.720) sits **~1.2 below** even the loosest bar.

## Provenance

archive.org's `marsaglia-cdrom` item (the one Round 17 named) is egress-blocked in this
environment. The data was fetched instead from the **`jeffThompson/DiehardCDROM`** GitHub
mirror — a recreation of the CD from the Wayback Machine copy of Marsaglia's FSU FTP site.
Every file is 10,000,000 B and 8.000 bits/byte (256/256 byte values); size and SHA-256 for
each are pinned in `pads_manifest.json`. **Caveat:** the archive.org item's own published
SHA-256s were not cross-checked (archive.org unreachable), so provenance rests on the mirror
plus these measured digests, not on the original checksum file.

## The instrument bug this lane caught

This is the first time `analysis/round17/lib_padsweep.py` was run on a **fresh checkout**, and
it exposed a silent failure. `lib_padsweep.trigram_model()` trains its dense-scan prefilter on
`data/{kjv,moby,pride,war}.txt`, which are gitignored (rebuilt from Gutenberg, itself
egress-blocked here). With the corpus absent the model falls back to Laplace-only — i.e.
**uniform** — under which every key offset scores identically, `dense_scan` cannot rank the
true offset, and `control()` reports **survival 0.0 → FAIL**. A sweep run naively past that
would have produced a "negative" from an instrument that provably could not have found the
signal: exactly README lesson #1.

`build_trigram_from_quadgrams.py` rebuilds an equivalent index-space trigram model **offline**
from the committed `english_quadgrams.txt` (each quadgram pushed through the repo's own
`eng_to_idx`). With the real model restored, `lib_padsweep.control(bits.01)` **PASSES**: the
beam recovers 8/8 planted keystreams at 100% of runes, dense-prefilter **survival 0.375** (the
honest coverage discount for 10 MB uniform-random pads; Round 17's own pads measured 0.625).
`sweep.py` refuses to run against the uniform fallback. Any future fresh-checkout run of the
public-pad instrument should run the rebuild first.

## Coverage / not covered

**Covered:** every offset of all 63 pads, 12 keystream readings × 2 signs, control-validated.
**Not covered:** non-byte readings (the pads are uniform binary, so the digit/text builders do
not classify); the ~0.625 of offsets outside the prefilter's power on 10 MB uniform pads (beam
recovery was 100% on plants, so this is a *power* blind spot, not a soundness gap); the
archive.org checksum cross-check. Prior was low going in (one more published-randomness source,
after Round 17 nulled RANDOM.ORG, NIST Beacon, Bitcoin and RAND) and the measurement matches.

## Reproduce

```bash
bash analysis/round18/marsaglia/fetch.sh                       # 630 MB from the GitHub mirror
python analysis/round18/marsaglia/build_trigram_from_quadgrams.py   # restore prefilter power
python analysis/round18/marsaglia/sweep.py --budget 100000     # resumable; ~7h; writes results.json
```
