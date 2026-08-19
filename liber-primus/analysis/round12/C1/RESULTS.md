# FRONT C1 — Unbounded multi-rune-history feedback ciphers — RESULTS

**Verdict: NEGATIVE.** Positive control PASSED; the real sweep found nothing.

## What C1 steelmans

The OTP proof (Rounds 7–11) bounds *rigid* running keys and *single* running-sum
feedback (Round 11 N1). It does NOT bound genuine **k-history feedback / autokey**:
key at position i = f(last k already-known runes), decoded left-to-right. The
community state of the art stops at exactly this label ("autokey/custom"), so it is
the right narrow class to test hard.

## Trust anchors (both PASS)

- `tests/validate.py` — reproduces every known solved page. PASS.
- `analysis/campaign18_skip/skipdecode.py` gate — PASS (beam recovers planted skip key).

## POSITIVE CONTROL — PASS (`control.py`)

Planted a k-history-feedback ciphertext by enciphering known English under every
(f, source) with k=3, then decoded. Result for **all 21** f×source combinations:
recover match **100%**, score **-4.154** (English); wrong-f decode stays **~-7.4**
(noise). The machinery provably recovers this cipher class when it is present, and
the shuffle/wrong-f null stays at noise. Score jumps noise ~-7.5 → English -4.15 as
required by the discipline gate.

## Real sweep — `sweep.py` over LP2 unsolved (0–54)

Bound of the search (exactly what was covered):

| axis | values | count |
|---|---|---|
| f | sum, gemsum(prime-sum), xor, prime_of_sum, prime_of_gemsum, lastdiff, alt_sum | 7 |
| k (history length) | 2,3,4,5,6 | 5 |
| source of history | ct (ciphertext), pt (recovered-plaintext autokey), mix (c+p) | 3 |
| sign | −1, +1 | 2 |
| orientation | forward, reversed | 2 |
| scope | continuous (12,956-rune stream) + per-segment (55 segments) | 56 streams |

**Seed handling (documented bound):**
- **ct-source**: key past position k is *fully determined* by ciphertext history —
  seed-independent, so this is **exhaustive** over (f,k,sign,orient), scoring the
  deterministic tail [k:]. No hidden seed freedom.
- **pt/mix-source**: seed errors propagate, so seed is swept over the 29 all-equal
  seeds (eq0..eq28) as a representative probe, taking the best. This is a **bound**,
  not exhaustive over 29^k arbitrary seeds; a genuine autokey would still light up
  because after a short transient the correct-family key locks on and the English
  tail would dominate the score. It did not.

**Total configs scored: 23,520** in 452.9 s (~7.5 min, within cap).

### Null and hit bar
- Null = `nc.shuffled` (seed 3301), **200 draws**, English scorer on the unsolved
  stream: mean **-7.496**, max **-7.466**.
- Hit bar (recomputed at this N): `max(-5.5, null_max+0.5)` = **-5.5**.

### Best results (all NEGATIVE)
- **Overall best across 23,520 configs: -6.299** (seg49, reversed, sign=−1, f=xor,
  k=5, pt-autokey) — transliteration `THMCOIROGEONGEOYSEHEAEANYTLEAHXCTNOLWTHI` = gibberish.
- Every top-20 entry is a **short per-segment** fragment (seg49/50/54), which have
  higher score variance by chance; **no continuous-scope config reaches even the top 20.**
- Best score -6.299 is above the single-shuffle null (-7.47) only because it is the
  max over 23,520 optimizations on *structured* real ciphertext; it is nowhere near
  English (-4.4) and **below the -5.5 hit bar and below the ledger's known key-attack
  noise ceiling (-5.8 to -6.0)**. No readable plaintext anywhere.

## Conclusion

k-history / autokey feedback for k=2..6 over the seven natural f, both signs, both
orientations, ciphertext-/plaintext-/mixed-history, continuous and per-segment, is
**dead**. The positive control confirms the instrument would have caught it. This
class — the one the community's "autokey/custom" label pointed at — is now bounded
and falsified, consistent with the OTP verdict. No control passed to a solve; refute
stands.
