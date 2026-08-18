# Round 12 — the "honest best shot" campaign (external-input first)

_Drafted 2026-08-17. This is the ONLY armada configuration with nonzero hope of a solve, and
it is deliberately NOT a ciphertext assault. Owner chose "all fronts"; authorized levers =
fetch external data, paid/deep OSINT, long compute. Human outreach was NOT authorized, so
Front A recovers key material through DATA and ARCHIVES, not by contacting people._

## Why this shape (read first)

LP2 0–54 is OTP-class: a full-length keystream against an EXTERNAL pad. That is proven
(doublet floor, entropy, and — Round 11 — the number channel, all with validated instruments).
A one-time-padded plaintext is **information-theoretically not present in the ciphertext**, so
no compute recovers it. Therefore the puzzle is solvable **iff** we obtain the external input the
construction requires. Every front below either (A) hunts that external input, (B) re-checks the
one internal thing that could still be wrong, (C) steelmans the narrow cipher classes the proof
does NOT cover, or (D) tries to break our own load-bearing assumptions. Honest odds are still
low — but this is where the odds are nonzero, and that is the whole point.

## Front A — RECOVER THE PAD (highest hope; needs owner levers)

The only class that can actually solve it. Two sub-fronts, both data-driven:

- **A1 — the author's own never-fed pads.** PA-3 found that Cicada shipped ~4 MB of authored
  binary files as key material in the 2013 CicadaOS (`DATA/_560.00/.17/.13`) and the published
  `761.mp3`⊕`twitter.txt` pair — period-correct, hand-selected, and **never fed under the
  skip-aware decoder** (only byte-XOR'd by the community). This is the single most-promising
  untested INPUT. Plan: locate + fetch the CicadaOS image / these files; extract the byte
  streams; feed each as a pad/keystream over the runes under the anti-repeat-aware decoder
  (the only decoder that survives the doublet filter), with the same positive-control gate we
  use everywhere. *Owner lever: fetch external data.*
- **A2 — key-delivery provenance via deep OSINT.** The pad, if shared, went to vetted insiders
  through channels now offline. The earliest Cicada-adjacent keyserver actor
  (`mruzuki@gmail.com`, key created 5 days after the first 3301 image, self-revoked at 7 days)
  was never resolved from public sources. Plan: breach-DB / people-search / paste-site lookups
  to attach a real identity and surface any archived 2012–14 IRC/forum/key-escrow material that
  could contain the pad or a pointer to it. *Owner lever: paid/deep OSINT accounts.*

## Front B — SOURCE FIDELITY (the one internal reopener; I run this)

The R9 re-transcription audit was bounded to 38.4% of lines and is **weakest exactly on the
dense OTP pages** — the only place a transcription error could still hide and, if real, would
change the ciphertext and reopen everything. Plan: forced per-line glyph-count re-segmentation
(connected-component-free) of pages 45–54 specifically, label-free, at maximum fidelity from the
onion7 master renders; adjudicate every disagreement against canon; quantify crypto impact of any
real change. *Owner lever: long compute.*

## Front C — STEELMAN THE UNCOVERED CIPHER CLASSES (low prior; I run this)

Our proof excludes rigid + bounded-feedback keystreams. Two classes it does NOT bound:

- **C1 — unbounded multi-rune-history ciphertext feedback.** Round 11 N1 tested only *single*
  running-sum feedback. Test genuine k-history feedback (key = f(last k plaintext/ciphertext
  runes/gematria), k=2..6) with strict plant-recover gates and the shuffle null. Unbounded, so we
  bound it to natural f and small k and report exactly what was covered.
- **C2 — book ciphers outside Cicada's known reference set.** Every keytext tried was English/
  Latin/Welsh from the known-refs list. Widen to a large, deduplicated corpus of period-plausible
  esoteric/philosophical texts NOT previously tried, under the skip-aware decoder, with the
  mechanism caveat stated (rigid running keys are doublet-excluded regardless of text).

## Front D — ASSUME WE'RE WRONG (meta; I run this)

A fresh red-team whose only job is to find the load-bearing ERROR in our own verdict — the way
Round 10's B4 found that "flat IoC forces a full-length key" was false. Re-derive every
exclusion's key assumption from scratch, hunt for a circularity / miscount / scope-overreach that
would make the "OTP" verdict an artifact rather than a fact. If it finds one, that is the solve
path; if it finds none, the boundary is maximally hardened.

## Execution & honesty ledger

- **Runnable now by me:** B (fidelity), C1/C2 (steelman), D (red-team) — launched as a large
  background Workflow, positive-control-gated, adversarially verified, long compute.
- **Needs owner:** A1 fetch (external data), A2 paid OSINT — I prepare scripts + an exact runbook;
  owner runs the network/account-gated steps, then I process the results.
- **Honest prior:** A1 is the best single shot but still low; B is the highest-hope internal check;
  C is near-zero (cipher space); D is a long shot that pays off huge if it hits. No front is
  guaranteed, and I will report each as a true positive-controlled result, not hope.
- Trust anchor `tests/validate.py` must pass before any negative is trusted. No re-runs of any
  ELIMINATION-LEDGER lane.
