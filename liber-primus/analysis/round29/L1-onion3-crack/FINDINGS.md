# L1 — onion3 image: first real large-dictionary OutGuess/steghide key attack

**Round 29, Lane L1 — "active attack" armada.** `analysis/round29/L1-onion3-crack/`

**VERDICT: CLEAN NULL.** No key in a 4,013-entry Cicada-native dictionary produced
a valid hidden payload from any onion image under OutGuess or steghide. The images'
only steganographic content is a *keyless* OutGuess payload that is a known-public
2048-bit RSA-signed message — already in the corpus, not a new find.

---

## (a) Which image, and is it the canonical onion3?

The mission flagged the on-disk `dl_onion3.jpg` as possibly the wrong capture
(memory said the canonical "5×5-rune onion3" is ~328 KB). **Verified:**

- `armada_osint/artifacts/dl_onion3.jpg` md5 `497f911a…`, 2400×3600, 175 159 B,
  content = "**Chapter 1 / Intus**" divider page.
- It is **byte-identical** (same md5) to the authoritative
  `micheloosterhof/cicada-2014` `stage03/onion3.jpg`. So the on-disk copy **IS**
  the canonical stage-03 onion3. It is a 175 KB LP2 chapter divider — **not** a
  literal 5×5 rune grid. The "~328 KB 5×5-rune" phrasing in the OSINT memory is an
  imprecise characterisation of the onion image chain.

The 2014 onion image chain is three images (all fetched fresh from the mirror and
verified). All were swept:

| image | size | content | keyless OutGuess |
|-------|------|---------|------------------|
| `onion1.jpg` | 169 KB | "Liber Primus" title page | seed 163, len 2899, PGP RSA-hex |
| `onion2.jpg` | 1.48 MB | **the runic "A WARNING / BELIEVE NOTHING" page** (red drop-cap R, cicada border, ~9 rune lines) | seed 115, len 2899, PGP RSA-hex |
| `onion3.jpg` | 175 KB | "Chapter 1 / Intus" divider | seed 94, len 2899, PGP RSA-hex |

The runic-content page (closest to the "rune grid" the memory referenced) is
**onion2**, not onion3.

### Correction to the prior record (important)
The earlier `armada_osint/extracts/T1-onion3-5x5-rune-outguess.bin` is
**byte-identical (md5 `597414fb…`) to the 1033.jpg "Welcome" payload**, and the
entire prior `artifacts/keysweep/dl_1033__*.bin` sweep ran against **`dl_1033.jpg`**,
not against any onion image. **The onion image chain had never actually been
key-attacked before this lane.** This lane is the first real attempt.

---

## (b) Dictionary — 4,013 unique Cicada-native keys

`keys_big.txt`, built by `build_keys.py` (provenance in `keys_provenance.txt`):

| provenance | count | source |
|-----------|-------|--------|
| E:self_reliance / mabinogion / agrippa / book_of_law / runepoem(_oe) | ~2,970 | corpus tokens (Emerson, Mabinogion, Agrippa, Crowley, OE rune poem) |
| A:solved-txt / solved-word / solved-page / solved-key | ~610 | words from the **solved LP plaintext** (SOLVED-PAGES.json: A WARNING, PARABLE, etc.) + the known keys DIVINITY, FIRFUMFERENFE |
| B:thematic / words_expanded / phrases | ~140 | LP-thematic phrases ("A WARNING", "BELIEVE NOTHING", "THE PRIMES ARE SACRED", "CIRCUMFERENCE", "CONSCIOUSNESS", "AN INSTAR EMERGES", "THE TOTIENT FUNCTION IS SACRED" …) spaced + concatenated + title-case |
| C:rune-name / translit / prime | ~118 | Gematria Primus rune names (FEOH…EAR), transliterations (F,U,TH…EA), numeric prime forms (2,3,5…109) |
| D:cicada-number | 23 | 3301, 1595277641, 509, 503, 1033, 761, 131, 151, 167, 65537, 845145127, 5243 … |
| F:case-variants | ~140 | lower/UPPER/Title of the thematic+number core |
| G:prior-59 | 33 | the prior 59-key list folded in (deduped) |

**68× the prior 59-key attempt, and aimed at the correct images for the first time.**

---

## (c) Tools / modes swept + total attempts

- **OutGuess 0.4** (`/usr/local/bin/outguess`), `-k <key> -r <img> out.bin`.
  Legacy `-t` mode was proven byte-identical to default on the keyless control and
  in a focused thematic spot-check (15 keys × onion2/onion3, no magic headers), so
  bulk used default; `-t` covered by spot-check (`_tcheck/`).
- **steghide** (`/usr/bin/steghide`): `extract -sf <img> -p <key> -xf out.bin -f`.
- Images: onion1, onion2, onion3. (onion5portrait skipped — 520 B stub, not a valid JPEG.)

**Total: 4,013 keys × 3 images × 2 tools = 24,078 adjudicated extraction attempts**
(plus keyless baselines and the 30-run `-t` spot-check).

---

## (d) Positive control — PASS

`outguess -r dl_1033.jpg` (keyless, default and `-t`) reproduces the canonical
payload byte-for-byte: `seed 102, len 1498`, `-----BEGIN PGP SIGNED MESSAGE----- …
Welcome. Good luck. 3301 …`. The harness classifier flags it `HIT magic:pgp/asc`.
The sweep aborts if this control fails; it passed on both runs.

---

## (e) Result — CLEAN NULL

Corrected full sweep, per-image/per-tool adjudication (24,078 attempts, coverage
verified: 12,039 = 3 images × 4,013 keys for each tool):

| tool | ARTIFACT | EMPTY | HIT | MAYBE |
|------|----------|-------|-----|-------|
| OutGuess | 5,570 | 6,469 | **0** | **0** |
| steghide | 0 | 12,039 | **0** | **0** |

- OutGuess: every keyed extraction was EMPTY or ARTIFACT (high-entropy binary,
  no magic header). **0 HIT, 0 MAYBE.**
- steghide: every key rejected (EMPTY). **0 HIT.**
- **0 candidates** with a real magic header (PGP / gzip / JPEG / PNG / zip / …) or
  clean English ASCII structure, across all 24,078 attempts.

No key unlocks a hidden layer. The onion images carry only their keyless payload.

---

## (f) The keyless payloads (already-known, not a find)

All three onions give up, **with no key**, a PGP SIGNED MESSAGE whose body is a
33-line 2048-bit RSA-signed-message hex block (GnuPG v1.4.11, sig `=fabe`). These
are the documented onion `pre`-page RSA blocks — e.g. onion1's body `775d0481…` is
already stored verbatim in `data/keys/solved_plaintext.txt`. Known-public puzzle
content, not novel; no independent hidden layer sits under a password.

## The wrong-key-artifact trap (why prior "hits" were noise)

OutGuess **never fails**: any `-k` key derives a different PRNG seed and returns
*some* bytes. Demonstrated on onion3:

| key | seed | len | header |
|-----|------|-----|--------|
| (none) | 94 | 2899 | `-----BEGIN PGP SIGNED MESSAGE` (real payload) |
| `DIVINITY` | 42513 | 14524 | 0-byte / garbage |
| `3301` | 3456 | 11484 | pure binary garbage |

Every keyed extraction that is not the keyless payload is a wrong-key random
artifact (this lane scored 791 such ARTIFACT blobs and never as a hit). The prior
`keysweep/dl_1033__<key>.bin` files (2–25 KB per key) are exactly this class:
non-empty ≠ a find. Only a magic header or clean English ASCII counts as a hit;
none appeared.

---

## Reproduce

```
cd analysis/round29/L1-onion3-crack
python3 build_keys.py      # -> keys_big.txt (4013 keys) + keys_provenance.txt
python3 sweep_fast.py      # positive control + full parallel sweep
```

Canonical onions in `canonical/` are fetched from
`raw.githubusercontent.com/micheloosterhof/cicada-2014/master/stage03/`
(onion3.jpg md5 `497f911a…` == the on-disk `dl_onion3.jpg`). Tools:
validated `/usr/local/bin/outguess` (OutGuess 0.4) + `/usr/bin/steghide`.
