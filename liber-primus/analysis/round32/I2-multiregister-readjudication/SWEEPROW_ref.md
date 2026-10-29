# `SWEEPROW/1` — the record every Round 19+ sweep persists per decode

_Round 19, lane I2. Validator: `adjudicate.validate_row` / `adjudicate.validate_store`._

> **Why this file exists.** Round 10b issued a binding handoff requirement — persist a
> language-agnostic statistic *at sweep time*, alongside the English score. Compliance across
> the 15 sweeps that ran afterwards was **0 of 15**
> (`round18/L7-redteam/out_a2.json → b6_handoff_compliance`): every one stored only
> `(parameters, English score, 64-char head)`. 6,224,300 + 692,064 + 52,556 decodes and
> ≈1.45 × 10¹⁰ offsets are therefore **permanently un-reinterpretable** — only the
> argmax-by-English survivors still exist, and re-scoring them has zero power for the registers
> that matter most (L7-A §A.5). Doctrine **R3** makes this non-negotiable. This is the schema
> that makes it mechanical.

---

## 1. The call

```python
import sys; sys.path.insert(0, ".../analysis/round19/I2")
from adjudicate import adjudicate, to_row, header, validate_row

res = adjudicate(plain_idx)             # plain_idx = the decode's RUNE INDICES (0..28)
row = to_row(res, kid)                  # kid = whatever identifies the decode's parameters
```

`plain_idx` is the **only** required argument. Never pass the transliteration string as the
thing to be scored — 7 of 29 runes are two characters (doctrine §4 rule 5). `adjudicate` will
build the transliteration itself for the legacy `en` field; pass `translit=` only if you
already have it and want to save the join.

## 2. The store

A SWEEPROW store is **JSONL**: line 1 is the header object, every subsequent line is one row
array in fixed field order.

```python
hdr = header("round19/S1/G1-bash-random", key_space="...", decoder="...", notes="...")
f.write(json.dumps(hdr) + "\n")
for kid, plain_idx in decodes:
    f.write(json.dumps(to_row(adjudicate(plain_idx), kid)) + "\n")
```

The header pins everything needed to reinterpret the rows later, and it is the reason a
Round 22 lane can re-adjudicate a Round 19 sweep without re-running it:

| header key | meaning |
|---|---|
| `v` | `"SWEEPROW/1"` |
| `sweep` | the lane's own sweep id |
| `fields` | the field order (below) — a store whose header disagrees is rejected |
| `registers` | the nine register names, **in the order `z` is stored in** |
| `english_ref` | which register `pcon` regresses out (`EN_MODERN`) |
| `window` | the sliding-window width for `mds` (32) |
| `panel_build`, `lambdas`, `null` | which panel build and null calibration produced these z |
| `corpora_sha256` | SHA-256 of every training corpus, so the panel is reproducible |
| `precision` | rounding applied to each field |

Plus anything the lane adds (`key_space`, `decoder`, `beam_w`, `max_skip`, `supp`, …). **All
three conditionals of doctrine Q4 belong in the header**: key space, decoder transition model,
adjudicator register set.

## 3. Field order — `SWEEPROW/1`

Fixed. **Never reorder; append only, with a version bump.**

| # | field | type | precision | meaning |
|---:|---|---|---:|---|
| 0 | `kid` | str \| int | — | key/parameter identity. Must be sufficient, **with the header**, to regenerate this exact decode |
| 1 | `n` | int | — | rune length of the decode |
| 2 | `en` | float | 4dp | **legacy** `lp.score.Quadgram.score_norm`, unchanged — keeps every Phase 2 number comparable with every published number in this repo |
| 3 | `pmax` | float | 3dp | max over the nine-register panel of the standardised score `z` |
| 4 | `preg` | int | — | index into `registers` of the `pmax` argmax |
| 5 | `pmax_ne` | float | 3dp | **R3 statistic (3)** — best **non-English** panel z (excludes `EN_MODERN`, `EN_KJV`) |
| 6 | `pcon` | float | 3dp | the **selection-corrected** statistic (§5) |
| 7 | `pcreg` | int | — | index into `registers` of the `pcon` argmax |
| 8 | `ioc` | float | 4dp | **R3 statistic (1)** — decrypt IoC·N |
| 9 | `mds` | int | — | **R3 statistic (2)** — min distinct symbols over any sliding 32-rune window |
| 10 | `h2` | float | 4dp | **R3 statistic (4a)** — plug-in order-2 conditional entropy, bits/rune |
| 11 | `zl` | float | 4dp | **R3 statistic (4b)** — `len(zlib.compress(bytes,9)) / n` |
| 12 | `z` | float[9] | 2dp | per-register standardised score, in `registers` order |

Example row:

```json
["seed=0x2f19c4", 240, -7.2668, 0.858, 8, 0.858, 1.439, 2, 0.9343, 16, 0.1744, 0.7167,
 [-0.67, 0.15, 0.80, -1.33, -2.48, -0.89, -0.81, -1.95, 0.86]]
```

### Size

JSONL: ≈ 130 bytes/row → 10⁷ rows ≈ 1.3 GB. For anything past ~10⁶ rows use the **binary
store** instead: `adjudicate.ROW_DTYPE` is a fixed 77-byte numpy record
(`kid` as a `uint64` index into a separately stored key table).

```
10^7 rows  ->  770 MB
10^8 rows  ->  7.7 GB   (chunk by shard; ship only the header + top-N with the round)
```

Both forms are gitignorable and rebuildable **only if the sweep is re-run**, which is exactly
the thing that is not affordable — so the *header*, the *top-N store* and the *summary
histograms* are the parts that get committed. See §6.

## 4. The top-N store — the one place decode strings live

The bulk store deliberately carries **no decode text**. Full decode strings go in a separate
`top-N` file, one per ranking statistic, so that a later round can re-read actual candidates:

```
topN.jsonl   {"stat": "pmax",    "rank": 1, "kid": ..., "row": [...], "translit": "..."}
             {"stat": "en",      "rank": 1, ...}
             {"stat": "pcon",    "rank": 1, ...}
             {"stat": "pmax_ne", "rank": 1, ...}
             {"stat": "ioc",     "rank": 1, ...}
```

**Keep a top-N per statistic, not one top-N by English.** This is the specific defect L7-A
§A.5 measured: because every archived candidate was the *English* argmax of its sweep, a Welsh
plaintext would have ranked ~651st and a vowel-dropped-English plaintext ~1.2 × 10⁶th of
1.39 × 10⁶, so neither could ever have entered the stored top-50, and the archive has **zero**
power for them — permanently. `N ≥ 50` per statistic.

## 5. `pcon` — the selection-corrected statistic, and why it is not L7-A's

L7-A §A.4 re-scored 340 archived candidates and found the naive per-register z confounded:
every archived candidate **is the English argmax of its own sweep**, so English-correlated
models (OE, DE) light up by selection alone. Its fix was the contrast `score_M − score_EN`,
standardised against *the archive's own distribution*.

`SWEEPROW/1` uses the **null-whitened English residual** instead:

```
r_M = ( z_M − rho_M · z_EN ) / sqrt(1 − rho_M²)          rho_M from the PRE-COMPUTED null
pcon = max over the seven non-English registers of r_M
```

Three concrete improvements, all pre-registered before measurement (`PREREG.md` §2.3):

1. **`rho` comes from the null, not from a post-selection sample.** Standardising against 340
   already-English-selected candidates shrinks the denominator by exactly the effect being
   removed.
2. **Common scale.** `score_M − score_EN` mixes models with different variances (a Latin
   trigram's spread is not a Welsh trigram's), so a fixed contrast is not comparable across
   registers. `r_M` is unit-variance under the null by construction.
3. **Row-local and streaming.** L7-A's statistic needs the whole archive to exist before any
   row can be scored — which is why it could only ever be a retrofit. `pcon` is computable at
   sweep time from the row alone, which is what R3 actually demands.

Measured null correlations `rho(z_M, z_EN)` are in `out_build.json → null.rho_vs_EN_MODERN`
and the empirical null distribution of `pcon` is in `out_null.json`.

## 6. What a sweep must commit

| artifact | committed? |
|---|---|
| the JSONL/binary **bulk store** | **no** — gitignored; too large |
| the **header** object | **yes** — as `<lane>/sweeprow_header.json` |
| the **top-N per statistic** (`N ≥ 50`, with decode text) | **yes** |
| **summary histograms** of `en`, `pmax`, `pcon`, `pmax_ne`, `ioc`, `mds`, `h2`, `zl` (≥ 200 bins each, with n / mean / sd / max) | **yes** |
| the thresholds used, and the null they came from | **yes** |

The histograms are what let a later round recompute a family-wise bar without the rows. Their
absence is why R17's `expected_null_max_at_n` could not be reconciled against its own observed
maximum (L7-C §C.3).

## 7. Validation

```python
from adjudicate import validate_row, validate_store
validate_row(row, hdr)                    # raises RowError with a specific message
validate_store("sweep.jsonl")             # header + every row
```

`validate_row` rejects, among other things, a row that carries only an English score — the
exact 0/15 failure mode this schema exists to prevent:

```
RowError: z must be a 9-vector of per-register standardised scores; got None.
Storing only the English score is precisely the R3 violation that made 10^10 decodes
un-reinterpretable.
```

Wire `validate_store` into `analysis/handoff/validate_ledger.py` for any lane that declares a
sweep, per doctrine R3's "CI-enforced".

## 8. Versioning

`SWEEPROW/1` is frozen. Additional statistics are appended as fields 13+ under
`SWEEPROW/2`; readers must accept a longer row whose first 13 fields match. Never change the
meaning or the order of an existing field — the whole point is that a Round 25 lane can read a
Round 19 store.
