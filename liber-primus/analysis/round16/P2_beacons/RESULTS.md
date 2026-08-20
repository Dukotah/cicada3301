# Round 16 — lane P2 — PUBLIC RANDOMNESS SERVICES AS ONE-TIME PADS

**Sweep verdict: NEGATIVE.** 0 hits in 96 configurations over 3,464,597,548 scored offsets
(2,165,373,468 after the measured 0.625 survival discount). Best `score_norm` **−6.8106**
against a pre-registered bar of **−5.500**; the lane's own 48 shuffle nulls span −7.040 to
−6.760, so the best result sits *inside* the noise band, not above it.

**The lane's durable finding is not the sweep.** It is that two of the sources the repo's
seed census names as unreachable are not unreachable, and one of them had never been
downloaded by anyone working on this puzzle:

> `analysis/round10/L5-seed32/CENSUS.md:87-94` — repeated verbatim at `handoff/PARKED.md:273-278`
> and `ELIMINATION-LEDGER.md:365-368`:
> *"**No seed at all.** `/dev/urandom`, a hardware RNG, **`random.org`**, or physical dice
> produce a pad with no compressible key. … Nothing in the seed sweep — finished or
> unfinished — touches it, **and nothing can.**"*

`random.org` publishes **one 1 MiB file of true random data per day and has done so without
a break since 2006-03-11**. This lane downloaded the 153 daily files covering
2013-09-01 → 2014-01-31 and checked every one against random.org's own published MD5:
**153/153 matched, 0 bad, 0 missing.** The NIST Randomness Beacon's 2013 records are
likewise still served, and 99,861 of them were pulled and verified three independent ways.

That sentence in the census merges two different properties — *leaves no seed* and *leaves
no public record* — and a published randomness archive has only the first. The correction is
not that the census's conclusion is wrong; it is that **`random.org` was never in the
category the census put it in**, so "nothing can touch it" was never a statement about
random.org at all. Section 2 replaces the assertion with a measured list.

---

## 1. Control status — PASS

| control | result |
|---|---|
| Round gate `lib_padsweep.control()` (PREREG.md) | **PASS** — 8/8 planted pads recovered by the beam, dense prefilter survival **0.625** |
| **Lane control on the REAL beacon pad** (`control_pad.py`, NIST Beacon `outputValue`, `nibbles`, 8 plants at random deep offsets) | **PASS** — dense survival **7/8 = 0.875**, beam recovered **8/8 at `max_skip=3` and 8/8 at `max_skip=8`**, mean rune match **1.000**, score **−4.212** |
| **Lane control on the REAL random.org pad** (`control_pad.py`, 95 MB pad, `mod29`, 8 plants) | **PASS** — dense survival **4/8 = 0.500**, beam recovered **8/8 at ms=3 and 8/8 at ms=8**, mean rune match **1.000**, score **−4.212** |
| `sweep.py::_assert_window_equiv()` | windowed beam/null bit-identical to `lib_padsweep`'s |
| `sweep.py::_assert_scan_equiv()` | `fast_dense_scan` bit-identical to `lib_padsweep.dense_scan` across 3 builders × 2 signs |
| Two-code-path reproduction (`parts/CROSSCHECK.json`) | one 95 MB pad swept twice — once whole-pad in one process with the reference scanner, once config-by-config in ten processes with the fast scanner. **13/13 config scores and 10/10 nulls identical to the last bit.** |
| `python liber-primus/verify_solution.py --selftest` | **PASS** — accepts a known-good key (−4.139/−4.307/−4.321 on three pages), rejects a wrong one |

The lane control is the one that matters here, and it was run *because* lane P1 reported that
A1's `max_skip=3` is underpowered on pads with constant byte runs (P1's own control fell to
6/8 at ms=3 and recovered 60/60 at ms=8). On **this** lane's pads that failure mode is
measurably absent — see §5.

The gap between control and result is the cleanest statement of the negative: a planted pad
scores **−4.212**; the best of 3.46 billion real offsets scores **−6.811**. The instrument
recovers the signal it is looking for at 2.6 score units above anything these pads produced.

---

## 2. Which public randomness sources have a retrievable pre-2014 archive

Everything in this table was probed on **2026-08-19**. This is the part of the lane that
survives the negative: it converts a one-line assertion into a checked list.

| source | producing since | dated pre-2014 archive retrievable **today**? | measured evidence |
|---|---|---|---|
| **NIST Randomness Beacon v1** | 2013-09-05 15:39 UTC | ✅ **yes — fetched here** | legacy `https://beacon.nist.gov/rest/record/<unix_seconds>` still serves the 2013 XML records. Genesis `timeStamp=1378395540`, `previousOutputValue` = 128 zeros, `previous/<genesis>` → 404. Last v1 record `1545840420` = 2018-12-26T16:07:00Z. Needs a `User-Agent` (bare `urllib` → HTTP 403). |
| **RANDOM.ORG Pregenerated File Archive** | 2006-03-11 | ✅ **yes — fetched and MD5-verified here** | `https://archive.random.org/binary` lists **7,395 daily 1 MiB `.bin` files** from 2006-03-11, plus **245 monthly `.torrent`** and **246 monthly `.md5`**, both free. Direct HTTP on an old day is subscription-gated (`download?file=2013-12-01.bin` → **403**); the monthly torrent is not (`2013-09-bin.torrent` → **200**), tracker `http://tracker.random.org:6969/announce`, seeded by random.org. 153/153 files MD5-matched. |
| **Marsaglia Random Number CDROM** (FSU, 1995) | 1995 | ✅ yes — **not swept by this lane** | original host `stat.fsu.edu/pub/diehard` → redirects to `ani.stat.fsu.edu/diehard/`, which times out; archive.org item **`marsaglia-cdrom`** serves `MARSAGLIA_CDROM.iso`, **634,124,288 bytes**, with `checksums.sha256.txt`. Range request returned **HTTP 206**. ~600 MB of published physical randomness, dated, still downloadable, **never swept** — see §6. |
| **ANU QRNG** (`qrng.anu.edu.au`) | 2011 | ❌ **no — archive host decommissioned** | site is live (HTTP 200) but is a *live stream*. Its FAQ's only pre-generated bundle is `cloudstor.aarnet.edu.au/plus/s/9Ik6roa7ACFyWL4`; **AARNet CloudStor shut down 2023-12-15** and the host no longer answers (curl exit 000). The Wayback capture of 2023-12-10 is the JavaScript shell with no file list. Unreachable **with cause**, not merely unfetched. |
| **HotBits** (Fourmilab) | 1996 | ❌ **no — by design** | live, and states: *"Once the random bytes are delivered to you, they are immediately discarded—the same data will never be sent to any other user and no records are kept of the data at this or any other site."* Genuinely live-only. |
| **Quantum Random Bit Generator Service** (`random.irb.hr`) | 2007 | ❌ no — host dead | curl exit 000 |
| **randomnumbers.info** (HU Berlin QRNG) | ~2010 | ❌ no — host dead | curl exit 000 |
| **LavaRnd** (`lavarnd.org`) | 2000 | ❌ no | site live (HTTP 200) but publishes design and source, not an output archive |
| **NIST Beacon v2** | 2018-07-23 | ✅ retrievable — but **post-dates LP2** | `/beacon/2.0/chain/1/pulse/1` = 2018-07-23T19:26:00Z. Note the v2 API **cannot** serve the v1 era: `/beacon/2.0/pulse/time/1378339200000` clamps to chain 1 pulse 1. Anyone sweeping "the NIST beacon since 2013" through the v2 API is silently sweeping 2018 onward. |
| **drand / League of Entropy** | 2020-04 | ✅ retrievable — but **post-dates LP2** | `api.drand.sh/public/1` → HTTP 200 |

**Two rows changed category as a result of being checked.** `random.org` moves out of
"nothing can touch it" and into "downloaded, hash-verified, and swept". ANU QRNG moves the
other way: it is often described as offering pre-generated files, and it did, but the host
that served them has been gone since 2023 — that is a *reason*, not an assumption.

---

## 3. Provenance — how the bytes were proved to be what they claim

This repo has twice accepted a file as what it claimed to be and been wrong, so each corpus
proves itself rather than being trusted.

**NIST Beacon v1** — 99,861 records, 2013-09-05T15:39:00Z → 2013-11-13T23:59:00Z:

| check | result |
|---|---|
| hash chain: `record[n].previousOutputValue == record[n-1].outputValue` for **every** adjacent pair | **99,855 / 99,855 linked, 0 broken** (link rate 1.000) |
| genesis `previousOutputValue` is 128 zeros | **true** |
| spec invariant `outputValue == SHA-512(signatureValue)`, re-pulled live for a random sample | **300/300 OK, 0 bad, 0 fetch errors** |
| minute gaps inside the window | **5** — the beacon's own outages, not fetch holes (see the window rule below) |

The pad stops at **2013-11-13** because 2013-11-14 is the first day the API would no longer
serve completely (1206/1440 records). Carrying a fetch hole into the keystream would shift
every offset after it and silently destroy alignment, so the window ends at the last fully
fetched day rather than at the last day with *some* data. That is the coverage bound, and
§6 says what it costs.

**RANDOM.ORG** — 153 daily 1 MiB files, 2013-09-01 → 2014-01-31, obtained over BitTorrent
from random.org's own tracker and checked against random.org's own published MD5s:

| month | listed | MD5 ok | bad | missing |
|---|---|---|---|---|
| 2013-09 | 30 | **30** | 0 | 0 |
| 2013-10 | 31 | **31** | 0 | 0 |
| 2013-11 | 30 | **30** | 0 | 0 |
| 2013-12 | 31 | **31** | 0 | 0 |
| 2014-01 | 31 | **31** | 0 | 0 |

`fetch.py`'s assembler **refuses** to concatenate a daily file whose MD5 does not match. An
earlier pad built before that gate was added contained 49 partially-downloaded files and was
discarded; the gate is why that did not reach the sweep.

Reproduce:

```bash
cd liber-primus/analysis/round16/P2_beacons
python fetch.py beacon    --start 2013-09-05 --end 2013-11-14 --workers 32
python fetch.py beaconcheck --start 2013-09-05 --end 2013-11-14 --n 300
python fetch.py randomorg --months 2013-09,2013-10,2013-11,2013-12,2014-01
python sweep.py --pad pad_outputValue_2013-09-05_2013-10-12.bin --tag beacon
python sweep.py --pad pad_randomorg_2013-09_2013-11.bin --builder mod29 --rev 0
python merge.py
```

---

## 4. Coverage bound

Not a verdict on "public randomness". This, exactly:

| pad | source & window (UTC) | bytes | builders | configs | offsets scanned | × 0.625 = effective | best |
|---|---|---|---|---|---|---|---|
| `outputValue_2013-09-05_2013-10-12` | NIST Beacon v1 `outputValue`, genesis → 2013-10-11T23:59 | 3,349,824 | 6 | 24 | 76,850,772 | 48,031,732 | −6.8273 |
| `seedValue_2013-09-05_2013-10-12` | NIST Beacon v1 `seedValue`, same window | 3,349,824 | 6 | 24 | 76,847,704 | 48,029,815 | −6.8690 |
| `outputValue_2013-09-05_2013-11-14` | NIST Beacon v1 `outputValue`, genesis → 2013-11-13T23:59 | 6,391,104 | 1 (`nibbles`) | 4 | 51,128,736 | 31,955,460 | −6.8528 |
| `seedValue_2013-09-05_2013-11-14` | NIST Beacon v1 `seedValue`, same window | 6,391,104 | 1 (`nibbles`) | 4 | 51,128,736 | 31,955,460 | −6.9264 |
| `randomorg_2013-09_2013-11` | RANDOM.ORG daily archive, 2013-09-01 → 2013-11-30 | 95,420,416 | 5 | 20 | 1,908,407,840 | 1,192,754,900 | **−6.8106** |
| `randomorg_2013-12_2014-01` | RANDOM.ORG daily archive, 2013-12-01 → 2014-01-31 | 65,011,712 | 5 | 20 | 1,300,233,760 | 812,646,100 | −6.8300 |
| **total** | | **179,913,984** | | **96** | **3,464,597,548** | **2,165,373,468** | **−6.8106** |

- **Builders.** The five byte builders (`mod29`, `hi_nibble`, `lo_nibble`, `byte_scaled`,
  `prime_to_idx`) on every pad; `hexchars` additionally on the beacon pads; `nibbles`
  (the true hex-text reading) on the longer beacon window. Each × forward and reversed
  blob × sign −1 and +1.
- `hexchars` is **not** run on the RANDOM.ORG pads on purpose: that archive is distributed
  as an opaque binary file, so there is no hex text for anyone to have copied.
- **Every offset in each pad was scored**, not a ladder. For comparison, round 12 front A1
  used **8 offsets per keystream variant**.
- **× 0.625** is the round's pre-registered survival discount, and it is kept in the table
  for comparability — but this lane measured its own, on its own pads, and **the rate
  depends on pad size**: 7/8 = 0.875 on the 6.4 MB beacon pad, 4/8 = **0.500** on the 95 MB
  random.org pad (16 plants on real pads, 11 retained, pooled 0.6875). That is what a
  fixed top-400 keep window does as the number of competing decoy offsets grows. Applying
  each pad its own measured rate instead of the round's flat 0.625 gives a **more
  conservative effective coverage of 1,828,282,255 offsets** (beacon 255,955,948 × 0.875 +
  random.org 3,208,641,600 × 0.500) rather than 2,165,373,468. Use the smaller number.
  Either way the beam recovered **8/8 in both real-pad controls**, so this is a power limit,
  not a soundness one.
- **Not covered:** any beacon window after 2013-11-13; the beacon `signatureValue` stream
  (1 KiB/pulse of public but non-random RSA bytes); random.org's parallel `/text` ASCII-bit
  encoding of the same daily data; the **2,659 further daily random.org files dated before
  2013-09-01** (the archive runs back to 2006-03-11 and every one of them is retrievable by
  the same free route used here); the Marsaglia CDROM (§6). Offsets straddling the join between two
  pads of the same source are not covered — 4 boundaries, ~1,608 key symbols each.


### Top 20 — every configuration that survived the dense scan, best first

No adjudication is done by reading these. The `head` column is the first runes the beam
emitted and is shown only so the table is not a wall of numbers; a flat 29-symbol cipher
emits English-looking fragments constantly (AGENTS.md §3), and the verdict comes from
`score_norm` against the bar and the null, nothing else.

| # | pad | variant | sign | offset | `score_norm` | null max | bar | first 32 runes decoded |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | `randomorg_2013-09_2013-11` | `mod29_rev` | -1 | 68,875,671 | **-6.8106** | -6.958 | -5.500 | `EONGEADARTSOLAMALROSTISHHOFNTHEO` |
| 2 | `outputValue_2013-09-05_2013-10-12` | `byte_scaled` | +1 | 1,982,843 | **-6.8273** | -6.961 | -5.500 | `AEJBHULMOFAECNGXIAINANBANDWHWGST` |
| 3 | `randomorg_2013-12_2014-01` | `byte_scaled_rev` | +1 | 28,669,483 | **-6.8300** | -6.933 | -5.500 | `UOEOELEIUCHIMIRRESHNEOUSAMEAIATH` |
| 4 | `outputValue_2013-09-05_2013-10-12` | `prime_to_idx_rev` | +1 | 382,059 | **-6.8450** | -6.955 | -5.500 | `JOLICHTHOUEBTHEATCOODFOEXCURHSTE` |
| 5 | `outputValue_2013-09-05_2013-10-12` | `hexchars_rev` | -1 | 1,284,501 | **-6.8469** | -7.007 | -5.500 | `LHAHBMICINARCYTUWATBORPSEPOEMNGY` |
| 6 | `randomorg_2013-09_2013-11` | `mod29_rev` | -1 | 23,638,891 | **-6.8502** | -6.958 | -5.500 | `OTSCAMARYSENREATSOSOETILDMUANUIW` |
| 7 | `outputValue_2013-09-05_2013-10-12` | `lo_nibble` | +1 | 158,390 | **-6.8506** | -6.865 | -5.500 | `NGSANHAPODUOEALTHABRIDOODHITHXTH` |
| 8 | `outputValue_2013-09-05_2013-11-14` | `nibbles` | +1 | 3,313,003 | **-6.8528** | -7.020 | -5.500 | `APEEOTCONAUOEAEPREWORTANITSATTHE` |
| 9 | `randomorg_2013-09_2013-11` | `lo_nibble_rev` | +1 | 78,955,639 | **-6.8624** | -7.004 | -5.500 | `NGXUCHFOUSGREALPSLUCEYRISNDIYFAE` |
| 10 | `outputValue_2013-09-05_2013-11-14` | `nibbles` | -1 | 7,561,392 | **-6.8639** | -7.020 | -5.500 | `ODRAUSEYSANIIAAEJFXAREENDAWCGDRM` |
| 11 | `seedValue_2013-09-05_2013-10-12` | `hi_nibble_rev` | -1 | 1,734,200 | **-6.8690** | -6.963 | -5.500 | `FEAGORTYANDWINGEHOABOLEAFENTTHGN` |
| 12 | `randomorg_2013-12_2014-01` | `hi_nibble_rev` | -1 | 26,072,284 | **-6.8695** | -7.023 | -5.500 | `UOILAGEBOLEOLONGOYEMOLONTOHAPAON` |
| 13 | `randomorg_2013-12_2014-01` | `byte_scaled_rev` | +1 | 34,931,352 | **-6.8784** | -6.933 | -5.500 | `ONLINHEAWHAPIEFERYSTASTHNLBFWOEW` |
| 14 | `randomorg_2013-12_2014-01` | `mod29` | -1 | 5,768,773 | **-6.8785** | -6.953 | -5.500 | `YOEEOTHEABHINGGITESAUSAPONCNONGU` |
| 15 | `outputValue_2013-09-05_2013-10-12` | `prime_to_idx_rev` | -1 | 519,451 | **-6.8785** | -6.955 | -5.500 | `AEEALOFARIALEUTPLYORDAYCEMEEEAMS` |
| 16 | `randomorg_2013-09_2013-11` | `mod29_rev` | +1 | 80,240,950 | **-6.8811** | -6.958 | -5.500 | `OEFROLENTNETHSMOTWATTHYLAITTHBUE` |
| 17 | `seedValue_2013-09-05_2013-10-12` | `hi_nibble_rev` | +1 | 2,391,355 | **-6.8815** | -6.963 | -5.500 | `TMORWUPTHEFATHETALROPOERNGNAFEOM` |
| 18 | `outputValue_2013-09-05_2013-11-14` | `nibbles_rev` | +1 | 4,568,003 | **-6.8863** | -6.760 | -5.500 | `BLONSDIHEGETHENDMRITTHINGWDAMFUS` |
| 19 | `randomorg_2013-09_2013-11` | `mod29_rev` | -1 | 89,419,001 | **-6.8888** | -6.958 | -5.500 | `UGHTETHNORTHSFHINGAPULTENSBLOTAT` |
| 20 | `randomorg_2013-12_2014-01` | `prime_to_idx_rev` | -1 | 57,622,389 | **-6.8906** | -6.912 | -5.500 | `NGEDLEALEIAFSWILLMEOFSIXINEDPCBS` |

Every row is 1.3 or more below the −5.500 bar and inside the −7.040…−6.760 null band. For
scale, the same beam scores a **known-correct** key at **−4.212** on a planted pad in this
lane's own control and at −4.139/−4.307/−4.321 on the three real solved pages in the
oracle's self-test.

### Extreme-value check (AGENTS.md lesson 3)

A fixed −5.5 bar is invalid at large trial counts, so `benchmark/null.threshold_for()` is
reported beside the raw best:

| quantity | value |
|---|---|
| `threshold_for(3,464,597,548)` — offsets scored | **−5.3257** |
| `threshold_for(3,839)` — beam escalations | **−5.5000** |
| raw best `score_norm` | **−6.8106** |
| lane's 48 shuffle nulls (n=200 each) | −7.0399 … −6.7604 |

The best result is **1.49 below** the trial-count-corrected threshold and sits inside the
null band. Nothing here is close.

---

## 5. Two corrections from other lanes, applied

**`ks_hexchars` is not the hex reading** (found by lane P1). `eng_to_idx` drops every
character it cannot map, so `hexchars` is the **A–F subsequence** of the hex string: on the
6,391,104-byte beacon pad it keeps 4,701,174 of 12,782,208 hex characters — **36.8%**, with
the digits 0–9 silently gone. Beacon values are *published as hex text*, which makes the hex
reading one of this lane's highest-prior variants, so it was re-run with P1's `ks_nibbles`
(every hex character as its value 0–15, in order; `|K|` = 12,782,208, i.e. 2× the byte
count). Both are reported: the `hexchars` numbers stand, labelled as the A–F subsequence,
and `nibbles` is a separate, larger, genuinely-new sweep. It found nothing either
(best −6.8528).

**`max_skip=3` can be underpowered** (also from P1: on a pad with constant byte runs the
anti-repeat filter burns skips without changing the key symbol). Measured on this lane's
pads (`data/pad_run_structure.json`) rather than assumed:

| pad | byte-histogram χ²/df | longest constant byte run | iid expectation | longest constant nibble run | iid expectation |
|---|---|---|---|---|---|
| beacon `outputValue` | 0.846 | 3 | 3.71 | 6 | 6.67 |
| beacon `seedValue` | 0.936 | 3 | 3.71 | 6 | 6.67 |
| `randomorg_2013-09_2013-11` | 0.942 | 4 | 4.31 | 8 | 7.88 |
| `randomorg_2013-12_2014-01` | 1.090 | 4 | 4.24 | 7 | 7.74 |

Every pad is indistinguishable from iid uniform, which is what full-entropy sources are
supposed to look like, so P1's failure mode has nothing to bite on. Confirmed empirically
anyway: 8 configs re-escalated at **`max_skip=8`**, each against its own ms=8 null. Best at
ms=8 is **−6.810640700106527** at offset **68,875,671** — bit-for-bit the same score at the
same offset as at ms=3. The skip budget is not what is limiting this lane.

---

## 6. Honest limits

The thing this lane most wants a reader to distrust is the word "negative", so here is
what it does *not* establish.

**The window is small and the choice of window is a guess.** The beacon has emitted a pulse
every 60 seconds since 2013-09-05 and 6.8 million of them exist; this lane swept 99,861 —
about **1.5%** of the beacon's life, and 70 of the 122 days between the beacon going live
and LP2 being posted. The reason to prefer that window is that a pad has to exist before the
book that uses it, not evidence that the author started at the genesis pulse. If the author
concatenated beacon output starting from an arbitrary later date, this sweep would not see
it, and the same is true of random.org outside the five months fetched. **This is a bound on
2013-09-01 → 2014-01-31, not on public randomness.**

**The construction space is barely explored.** Six ways of turning bytes into rune indices
were tried, forward and reversed, both signs. An author could as easily have taken every
second byte, XORed `outputValue` with `seedValue`, used the pulses' `previousOutputValue`
chain, base-64'd the values, decimated the stream, started mid-pulse, or concatenated in
reverse pulse order. Each of those is a different keystream and none of them is covered.
The *offset* axis is now exhaustive; the *construction* axis is a handful of samples.

**The prefilter is the power ceiling, and it gets worse on big pads.** The dense scan keeps
only the best 400 offsets before the beam sees anything, and the chance the true offset is
among them falls as the pad grows: measured here at **0.875** on the 6.4 MB beacon pad but
only **0.500** on the 95 MB random.org pad. So on the two random.org pads — which are 93% of
this lane's offsets — roughly **half** of true offsets would have been discarded before
adjudication. §4 restates the coverage with each pad's own rate. A miss is entirely
possible; a *systematic* miss is not, because at the beam stage all 16 planted pads across
both real-pad controls were recovered at 100% of runes at both ms=3 and ms=8. The way to
close that gap is a larger `keep` window, which costs nothing but beam time — a concrete,
cheap follow-up rather than a caveat.

**One source in the table was found and left alone.** The Marsaglia Random Number CDROM —
~600 MB of physical randomness, published 1995, still downloadable from archive.org with
published SHA-256s — is exactly the shape this lane is testing and is **not swept**. It is
recorded here with its identifier, size, and a verified 206 response so the next person can
pick it up rather than rediscover it. Sweeping it is roughly 12 billion offsets, about
4× everything above — and on a pad that size the prefilter survival measured above suggests
a `keep` window well over 400 would be needed for it to mean anything.

**One thing here raises the prior rather than lowering it.** Lane P4 measured the
anti-repeat filter and found it **machine-applied**: flat, unscoped, single-lag, suppression
80.75%, with under 1/47 of the lag-1 effect leaking to any other lag and no per-line scope.
The pad came out of a program or a file, not a person's hand. That is the world in which an
imported public byte stream is a *more* natural hypothesis than a hand-built one — which is
an argument for continuing along this axis with different windows and different
constructions, not for closing it.

**What would change the verdict.** A hit needs `score_norm ≥ −5.5` *and* `≥ null_max + 0.5`.
Nothing in this lane came within 1.3 of that. The lane reports NEGATIVE for the pads,
windows, builders, signs and offsets in §4, and takes no position on the family.

---

## 7. Files

| file | what it is |
|---|---|
| `fetch.py` | acquires both corpora; `beacon` walks the v1 REST API, `beaconcheck` re-verifies the SHA-512 signature invariant on a live sample, `randomorg` pulls the monthly torrents and gates every daily file on random.org's published MD5 |
| `sweep.py` | dense offset scan + A1 beam. Whole-pad mode, and a per-config mode (`--builder/--rev/--sign/--max-skip`) that writes one part file per configuration so an interrupted run costs at most one config |
| `control_pad.py` | this lane's positive control, planting into the **real** pads at ms=3 and ms=8 |
| `merge.py` | folds whole-pad results and part files into `results.json` without double-counting |
| `results.json` | the lane's machine-readable record: coverage, nulls, controls, top-20, verdict |
| `parts/CROSSCHECK.json` | the two-code-path reproduction |
| `parts/_superseded/` | correct runs excluded from the merge because their offsets are already counted on another window; `README.txt` says which and why |
| `data/` | gitignored; regenerated by the commands in §3 |

Two bugs were fixed in this lane's own code and are worth knowing about: `fetch.py` created
a thread-local `requests.Session` per worker per day and leaked ~4,000 of them, degrading
into a CPU spin that made no progress (observed twice, at 885 s and 801 s of CPU with the day
counter frozen); and `merge.py` initially dropped every config of a builder after the first,
because the duplicate-detection set was being mutated by the fold it was guarding. The second
one would have quietly understated coverage — the exact failure mode this round exists to
catch.
