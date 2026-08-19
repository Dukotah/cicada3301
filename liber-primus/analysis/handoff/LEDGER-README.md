# `LEDGER.json` — the machine-readable falsification ledger

_For whoever picks this up next, human or model._

## What this is

One queryable JSON file at [`liber-primus/LEDGER.json`](../../LEDGER.json) holding every
hypothesis this project has tested or named: what was claimed, what threshold was set, whether
the instrument was ever shown capable of detecting the answer, what was actually covered, and
what would put the lane back on the table.

## Why it exists

Before this file, answering *"what has been tried, and what is genuinely still open?"* meant
reading about forty prose documents and reconciling them by hand.

That is not a hypothetical cost. It is exactly how three load-bearing overreaches survived for
months, until Round 12's front D3 went looking for them:

| Claim in the navigation docs | What the evidence actually supported |
|---|---|
| "information-theoretically unsolvable / no compute recovers it" | **OTP-*class*** — the ciphertext cannot separate a true external pad from a short-seed *derived* keystream, and the derived case has a finite, brute-forceable keyspace |
| "seeded-PRNG pads — do not re-run" | 10 generators over **~3% of each seed space**; PHP `mt_rand` was never touched |
| "keytexts dead **by mechanism**, independent of which text" | dead **by exhaustion** over ~200 texts |

Two of those three had *already* been caught by Round 10's RECON-B (items B-16 and B-21) and
were never actioned — because a flag written in one folder does not reach a reader in another.
A single index with a schema is the structural fix for that failure mode.

## The field that matters most

**`positive_control`.**

A null result from an instrument that was never shown able to recover a *planted* signal is not
a negative. It is an unknown wearing a negative's clothes. This project's one genuine
methodological contribution is refusing to accept the first as the second, and the ledger makes
that refusal machine-checkable:

```bash
python3 liber-primus/analysis/handoff/validate_ledger.py
# ...
# Unsound negatives: 0  (this is the number that matters - it should be 0)
```

`validate_ledger.py` raises an **ERROR** for any entry claiming `negative` or `eliminated`
whose `positive_control` is not `passed`, and for any entry whose control **failed** but which
still carries a conclusion. Round 12's `frontB` is the worked example of handling that
honestly: its forced re-segmentation instrument scored 12.9% on control pages where the
validated instrument reaches ~98%, so the front is recorded as `inconclusive` and is not
allowed to claim pages 45–54 are verified.

Read `coverage` before treating any status as closed, and `reopens_if` to know what would
settle it.

## Schema

| field | meaning |
|---|---|
| `id` | Stable. Reuses the RECON-A/RECON-B ids (`B-04`, `A-03`, `B-21`) where they exist. |
| `lane` | Rough grouping: `verdict`, `keystream`, `keytext`, `mechanism`, `transcription`, `external-input`, `red-team`, `recon-a`, `recon-b`. |
| `hypothesis` | One falsifiable sentence. |
| `status` | `eliminated` · `negative` · `inconclusive` · `never-run` · `partially-run` · `parked-with-cause` · `open` · `superseded` · `in-flight` |
| `round` / `date` | Which campaign settled it, and when. |
| `threshold` | The pass/fail bar. |
| `threshold_fixed_in_advance` | `true` only if pre-registered. A bar chosen after seeing the data is a story, not a test. |
| `positive_control` | `passed` · `failed` · `none`. **See above.** |
| `control_detail` | The actual recovery numbers, so a reader can judge the control rather than trust the label. |
| `null` / `result` | The size-matched null used, and what was measured. |
| `coverage` | The honest bound of what was *actually* swept. |
| `not_covered` | Declared in advance, so a negative cannot quietly expand its own scope. |
| `evidence` | Repo-relative paths to script, results JSON, verdict doc. Existence is checked. |
| `reproduce` | The exact command. |
| `supersedes` / `superseded_by` | Ids. Corrections are linked, not deleted. |
| `reopens_if` | The concrete condition that puts this lane back on the table. |
| `priority`, `source_register`, `raw_status`, `notes` | Provenance from the mined registers. |

## Querying it

```bash
# everything genuinely untested
jq -r '.entries[] | select(.status=="never-run") | "\(.id)  \(.hypothesis)"' liber-primus/LEDGER.json

# any "closed" claim resting on an unvalidated instrument
jq -r '.entries[] | select((.status=="negative" or .status=="eliminated")
        and .positive_control!="passed") | .id' liber-primus/LEDGER.json

# what is in flight right now
jq -r '.entries[] | select(.status=="in-flight") | "\(.id)  \(.round)"' liber-primus/LEDGER.json

# how to re-run a given lane
jq -r '.entries[] | select(.id=="B-04") | .reproduce' liber-primus/LEDGER.json
```

## Adding or updating an entry

The ledger is **generated**, not hand-edited — so it can be rebuilt as new rounds land without
drifting from its sources.

1. Edit `build_ledger.py`. Register-derived rows are mined automatically from
   `round10/RECON-A/REGISTER.md` and `RECON-B/REGISTER.md`; anything richer goes in the
   `HAND` list, where a hand-authored entry merges over a register stub of the same id.
2. Never invent a field. If a source doc does not record the threshold or the null, write
   `null` and say so in `notes`. Those gaps are themselves findings — they mark results whose
   soundness cannot now be reconstructed.
3. Rebuild and validate:
   ```bash
   cd liber-primus/analysis/handoff
   python3 build_ledger.py && python3 validate_ledger.py
   ```
4. If a new result overturns an old claim, do **not** delete the old entry. Set its status to
   `superseded`, fill `superseded_by`, and add the new entry with `supersedes`. The reasoning
   that narrowed an avenue stays useful after the avenue closes — and the record of *how* a
   claim was overstated is what stops the next one.

## Known limits of this file

- Register-mined entries carry the register's own imprecision. Three `evidence` paths do not
  resolve because the source cites a glob or a bare filename; the validator reports them as
  warnings rather than silently dropping them.
- Coverage of the pre-Round-10 campaigns is inherited from the registers' summaries rather than
  re-derived from each campaign's own artifacts. An entry with a `null` threshold usually means
  the original document did not record one — not that no bar existed.
- 46 open lanes have no `reopens_if` yet. Filling those in is cheap, useful work for whoever
  comes next; the validator lists them under NOTES.
