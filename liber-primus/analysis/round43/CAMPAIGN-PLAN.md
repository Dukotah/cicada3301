# Round 43 — FIRST PRINCIPLES: THE FRESH ARMADA (pre-registration / plan of record)

_Drafted 2026-11-03 at the owner's direction, superseding the same-day "THE SCREEN AND THE
REMAINDER" draft (its lanes are deferred to Round 44, not cancelled — see §6; the D1 snapshot
decision survives unchanged because it has a date on it). Doctrine:
[`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md) still binds: PREREG before output, planted
controls **through each lane's own glue** (the R42 X1 rule), coverage × power, flag-never-certify._

## 0. Thesis — the owner's directive, stated as a falsifiable bet

**The directive:** stop extending what the last ten rounds were doing. Build a round that looks at
the released-and-stored material the way a capable stranger would — first principles, no
inheritance from 42 rounds of framing — on the thesis that **something recoverable has been
overlooked in material we already hold or can still fetch.**

**Why this is not a vibe but a strategy with a track record here:** every needle-mover this
project ever produced came from *looking again at the material*, not from sweeping a key space —
the pp49–51 payload (sat untouched in the repo's own data files through six campaigns because the
rune loader silently dropped non-runic tokens), the R18-L3 ornament read (256 non-runic tokens the
analysis tree never held), the R41 X1-B clone-scope finding (four "blocked" cells were runnable all
along), the R42 C1 find (10 of 33 "keytexts" were 404 pages nobody had ever opened). The pattern in
all four: **the overlooked thing was not hidden by the author; it was hidden by our own
representation of the material.** Round 43 industrializes that pattern instead of waiting for it to
happen by accident.

**The honesty rail (non-negotiable):** fresh eyes are for *generating* hypotheses, never for
*re-running* eliminated ones. Every fresh-lane output passes through a ledger-diff firewall (X0)
before any decode fires: map it to an existing row (cite it, done) or PREREG it as new. The ledger
is 304 rows deep; the win condition is finding what is NOT in it, and the failure mode is burning
the round rediscovering what is.

## 1. Doctrine budget allocation

| share | goes to | lanes |
|---|---|---|
| ≈10% | the dated housekeeping | D1 |
| ≈35% | fresh-eyes hypothesis generation (blind) | F1, F2 |
| ≈20% | first-principles constraint modelling | F3 |
| ≈25% | the named, verified-open stored-material threads | F5, F6 |
| ≈10% | firewall + red-team + Round 44 critic | X0, X1 |

## 2. Lane roster

| ID | Type | Title | Gates on |
|---|---|---|---|
| **D1** | decision (expires ~2026-11-09) | Export the R42-S1 full candidate lists from snapshot `snap_Rw1QyGFA39to1dV9rR8qA8WJEgm6` / sandbox `r42-s1-recovery` to the laptop, or record a deliberate lapse in the `R42-S1` row note. One hour either way. | nothing — first |
| **F1** | fresh eyes (BLIND) | Blind re-derivation armada: N≥6 independent agents, each given ONLY primary material (page images, raw transcription files, the released onion/PGP/image corpus) in a clean side workspace — **no repo docs, no ledger, no analysis/**. Each answers from scratch: what is this object, what is odd about it, what would you try first, what does the material itself say the key is? Their hypothesis lists (not decodes) are the deliverable. The pp49–51 precedent, made deliberate. | X0 before any testing |
| **F2** | fresh eyes (inventory) | Total physical-channel inventory: enumerate EVERY mark in the primary scans and releases against what the rig actually consumes — separators, line/page breaks, hyphenation, red/colored glyphs, ornaments, margin art, page numbers, blank space, the final-page grid, file names, byte-level container structure, EXIF — and emit a channel ledger: consumed-by-loader / tested-as-data / **never-represented**. The loader dropped an entire 2048-bit payload once; this lane asks what else it cannot see. | X0 |
| **F3** | first principles | The hand-feasibility constraint, modelled for the first time as a constraint: the book is hand-illuminated; ~13,000 rune encryptions were performed by a human (or printed from a human-prepared pad) in 2013/14. Model the author's demonstrated toolkit from the solved pages (plain → Atbash → shift → Vigenère → totient-stream + ᚠ interrupters: a gentle, teachable escalation) and enumerate the MINIMAL hand-executable extensions of it. Diff that enumeration against the ledger (most PRNG/KDF lanes score LOW on this constraint; what scores HIGH that was never run?). Deliverable: a ranked, hand-feasible, ledger-diffed candidate list, then test the top cells. | X0 |
| **F5** | stored material | The verified-open fetch legs, run to completion: (a) the **Wayback/CDX leg** R36-O2 recorded as BLOCKED-not-searched (tooling refused web.archive.org) — alternate-format/alternate-resolution sources for the 2014 dump, the onion pages, the pastebins; (b) archived 2012–14 **IRC logs** (the attribution campaigns called them dead; dead for *attribution* ≠ searched for *key material*); (c) checksum the community mirror sets against ours (any divergent byte is either corruption or a finding). | network |
| **F6** | the open objects | The dangling internal objects, joined for the first time: (a) the pp49–51 **256-byte payload as CIPHERTEXT** under candidate keys (explicitly untested since Campaign VII characterized it); (b) payload × the **256-byte RSA hex blobs embedded in onions 2/3/4** (`<!--761/1033/3301-->` pages) — both sides are exactly 256 bytes and this cross was never run (the dead "onion hex" lead was onion5, a JPEG dump — different object); (c) the page-56 512-bit hash **as key material** over runes and payload (the R17 hash-hunt was preimage-direction only); (d) identify or bound the **T2/T3 high-entropy blobs** from the 2026-07-27 OSINT sweep, still unidentified. | X0 for (a)/(c) scope |
| **X0** | firewall (standing, not last) | The ledger-diff firewall: every F1/F2/F3 hypothesis is adjudicated against `LEDGER.json` coverage × power (never the bare status text) — CITED (covered, with the row named), REOPEN (covered but at a power the row itself disclaims), or NEW (PREREG and run). Runs continuously as the F lanes emit; nothing decodes without its stamp. | — |
| **X1** | red-team (last) | Blindness audit on F1 (did any agent see repo docs?); F2 inventory completeness vs a second independent pass; F3's feasibility scores re-derived; F5 fetch provenance + hashes; F6 counting; every X0 CITED stamp spot-checked against the actual row; ledger patches; `check_ceiling.py`; the full gate; Round 44 critic. | last |

## 3. Lanes in detail

### F1 — the blind armada _(the core of the round)_
Mechanics matter here. Each agent runs in a side workspace containing ONLY: the page images,
`data/` raw transcriptions, and the released artifact corpus (onion dumps, PGP messages, images) —
no `analysis/`, no `*.md` above the data layer, no ledger, no hint of 42 rounds. Prompts vary by
agent (cryptanalyst / forensic-document-examiner / puzzle-designer / historian-of-hand-ciphers /
data-archaeologist / adversarial "the community is wrong about what kind of object this is"), so
diversity comes from the lens, not the temperature. Deliverable per agent: a ranked hypothesis
list with, for each item, *what in the material* motivates it. The coordinator may NOT discard an
item for being "known dead" — that is X0's job, with a citation. Success test: ≥1 NEW-stamped
hypothesis reaches PREREG. (If all N agents independently converge on only CITED items, that is
itself a publishable result: the material's visible hypothesis space is measured as exhausted.)

### F2 — the channel inventory _(what the rig cannot see)_
Build the inventory from the primary scans mechanically (segmentation + classification of every
non-background mark) and from the raw transcription files (every token class), then diff against
`src/lp/` loader behavior. Each channel gets a row: representation, prior art (ledger rows), and a
tested/untested verdict. Untested channels go to X0 → PREREG. Planted control: inject a synthetic
mark class into a copy of one page and confirm the inventory catches it.

### F3 — hand-feasibility _(the constraint nobody filed)_
This is first-principles in the strict sense: derive what the author COULD have done from what the
object physically is, rather than what the community has proposed. Scoring axes: executable by
hand at 13k-rune scale (or from a printed pad); teachable in the style of the solved pages'
escalation; consistent with the measured doublet mechanism (the ~83% suppression is mechanical —
the ledger's own finding — so the scheme must either be the mechanism or compose with it).
Deliverable: the enumeration, the scores, the ledger diff, and decodes for the top NEW cells —
with plants through the lane's own glue.

### F5 / F6 — the open threads _(fresh thesis, old-fashioned rigor)_
These are the only lanes allowed to touch things with prior rows, because their targets are
*verified open in the rows themselves* (R36-O2 "Wayback unsearched"; T2/T3 "still open"; Campaign
VII "payload-as-ciphertext untested"). Standard PREREG, standard bars, plants through the glue.
F6(b) note: if the onion 2/3/4 RSA hex blobs are moduli/signatures (likely), the XOR cross is a
five-minute null — run it anyway, it is five minutes and the size coincidence (256B = 256B) is
exactly the kind of thing this round exists to not leave untested.

## 4. Verification and hit protocol

Unchanged: `HUMAN-ORACLE.md`; a flag requires the N=1e6 bar of record; nothing auto-certifies.
Blind-lane hypothesis lists are NOT findings and are labelled as such; only X0-stamped,
PREREG'd, control-validated decodes can produce a row.

## 5. Owner decisions this round carries

The D1 export-or-lapse (~2026-11-09); WATCH band yes/no (now gates Round 44's I1(a)); R13
DIRECTION; KDF sign-off; `with_degenerate` default; the N5/N4 bundle read.

## 6. Deferred to Round 44 (from the superseded draft — recorded, not cancelled)

I1(b) the widened k≤3–4 head screen with measured power (still the gate for the whole 110.5-cell
B2 offset remainder); S2 the PHP tier retry; C1 the 10-keytext hash-pinned refetch; B2 behind the
screen. If Round 43's fresh lanes come back all-CITED/null, Round 44 returns to the instrument
grind with the fresh-eyes question answered rather than assumed.

## 7. Orchestration

- **Wave A:** D1 immediately; F1 agents launched blind in parallel; F2 inventory build; X0 stands up.
- **Wave B:** F3 modelling; F5 fetch legs; F6(b)/(c) quick crosses; X0 adjudicates F1/F2 output as it lands.
- **Wave C:** NEW-stamped cells PREREG'd and run (plants through the glue); F6(a)/(d).
- **Wave D:** X1; closeout; Round 44 plan.
