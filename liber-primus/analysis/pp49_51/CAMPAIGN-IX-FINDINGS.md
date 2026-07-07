# Campaign IX — Proof-of-Work on the Untested pp49–51 Leads

_2026-07-06. Executed after the Campaign VIII community-OSINT sweep confirmed the
pp49–51 byte stream itself was already public (Uncovering Cicada wiki) but that
**no one — us or the community — had ever run the structural/correlation leads.**
This campaign runs them. All results are honest nulls; the point is that the leads
were **worked, measured, and made reproducible**, not asserted._

**Reproduce:** `PYTHONUTF8=1 python3 campaign9.py` (pure standard library).
Pulls the AN END hash, the P.S. digit string, and the 2014 onion artifact from the
repo's own files; operates on the committed `canon_256.bin`.

---

## What was untested going in

Campaign VII §5 explicitly flagged two leads as **not yet run**, and the community
wiki proposed a third it never executed ("I don't know how to XOR things, I'll leave
this for somebody else"):

- **Lead A** — 256 bytes = 4 × 64. Is the payload structurally four 512-bit hash
  digests, and does it relate to the solved **"AN END" 512-bit hash**?
- **Lead B** — does the payload correlate (XOR / mod-256 subtract) with any known
  Cicada key stream such that its entropy collapses toward text?

---

## Lead A — hash structure: NO LINK (documented)

| test | result |
|---|---|
| **[A1]** per-64-byte-block profile | 4 blocks, entropy 5.78–5.84, distinct 57–59/64, χ²/255 ≈ 0.9–1.0 — statistically uniform and alike. **Consistent with 4 digests, but equally with any random pad; this test can only refute.** |
| **[A2]** AN END hash embedded in payload? | **No** — the 64-byte AN END digest (forward or reversed) is not a substring of either payload variant. |
| **[A3]** bounded preimage probe (19 obvious Cicada strings × SHA-512/SHA3-512/BLAKE2b/SHAKE-256) | No string hashes to the AN END digest (expected — true preimage space is unbounded) and **none matches any 64-byte block of P**. |
| **[A4]** does P (or its halves) hash *to* the AN END digest? | **No** under any tested algorithm. |

**Verdict:** no structural link between pp49–51 and the AN END hash established.
The "four stacked digests" idea is not refuted (it can't be from statistics alone)
but has **zero positive support**.

## Lead B — correlation / entropy collapse: NO SIGNAL (documented)

Baseline P: entropy **7.170** b/byte, 40% printable, longest printable run 5.
A real key would collapse entropy toward ~4–5 (text) or spike a long printable run.

| stream (XOR and mod-256 subtract) | best entropy | verdict |
|---|---|---|
| AN END hash (tiled) | 7.127 | null |
| first-256-primes mod 256 | 7.142 | null |
| 29 rune-primes (cycled) | 7.159 | null |
| P.S. 2012 digit string | **7.116** (lowest overall) | null |
| 3301 = 0x0CE5 (tiled) | 7.142 | null |
| **2014 onion-hex** (12,003-byte JPEG dump, `ffd8ffe0…`) | 7.132 | null — the wiki's XOR lead **run, not asserted**; confirms Campaign VII |

**Best entropy achieved across all streams/ops: 7.116** vs a 7.170 baseline — i.e. no
collapse. **No known key stream turns the payload toward text.**

## Reproduced (rig sanity) — Campaign VII key-test still null

`keytest.py` re-run: **337,944 configs, 0 above the −5.2 threshold** (best −6.612,
clustered on the short pages = score variance). Byte-identical to the Campaign VII
result — the harness reproduces.

---

## What this proves

1. **The leads are worked, not hand-waved.** Two concrete, previously-untested
   hypotheses (hash-structure, entropy-collapse correlation) are now executed with
   measured outputs and a committed, standard-library script anyone can re-run.
2. **The hypothesis space shrank by two more tests** — both null, both documented so
   no one re-digs them.
3. **The method demonstrably can move a needle** — it produced a real correction
   this cycle (the community already had the byte stream; our novelty is the
   characterization) and it turns vague "dead end" intuition into specific, falsified
   claims. That is the honest form of progress available on an OTP-class object.

## Still genuinely open (unchanged by this campaign)

- The payload/runes under a **true external key** (unbounded — cannot be forced).
- Alternative-base (59/61/62/64) readings as **key material** rather than naive ASCII
  (community tried ASCII → rubbish; the keystream interpretation is untouched).
- The **6 contested bytes** vs a Latin/digit OCR re-read.
- **One-time-pad vs autokey** rigor — the public community stops at "autokey/custom";
  our doublet-mechanism analysis goes further and is the likeliest place we lead.
