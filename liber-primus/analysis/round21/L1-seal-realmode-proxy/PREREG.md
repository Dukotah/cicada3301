# L1 — Seal the real-mode held-out proxy to >=0.90 catch (disjoint folds)

_Pre-registered 2026-08-28, BEFORE any measurement on the fold variant. Binding: `ARMADA-DOCTRINE.md`.
This lane ships one instrument (a strengthened no-oracle proxy) and audits it; its "hit" is a
mis-classification (a bar-clearing EN_NOVOWEL hallucination the strengthened real-mode proxy wrongly
ACCEPTS, or the genuine decode it wrongly REJECTS). Per doctrine mechanic 2 (Q1) the recogniser is
planted before it is trusted, and the tuning population is FROZEN before the audit population is
scored._

## The defect this closes (SYNTHESIS §8.4 FOUND-ERROR, carried explicitly to Round 21)

`hitfn20.is_hit` STRICT (oracle) mode catches 45/45 EN_NOVOWEL hallucinations (correct key,
vowel-dropped English, bar-clearing). Its REAL (no-oracle) clause-3 held-out proxy — the ONLY mode a
real LP2 candidate can be judged in — catches only **15/45 (33 %)**
(`round20/S-RESCOPE/out_heldout_proxy_audit.json`). The leak: the single 1/4->3/4 cut lets a wrong
decode that reproduces its OWN wrong indices consistently on the tail pass clause 3. Until this
closes, no bar-clearing real survivor can be certified a solve — the ledger has no sealed no-oracle
gate.

## Q1 — the recogniser (what a HIT / a mis-classification is, stated before measuring)

The strengthened proxy is `_heldout_recovery_folds(dec, k_folds, agree_rule)`: partition the page
into `k` disjoint contiguous folds; for each fold-k, attribute the key phase on fold-k's window
(that sub-decode's ending key pointer fixes the phase entering the complement) and RE-DECODE the
complement under the SAME key, measuring rune-index self-consistency vs the full-page decode. The
fold-level held-out recovery is combined by `agree_rule` (candidate: MIN across folds, i.e. require
reproduction on ALL folds). An overfit basin reproduces on the window it fit but NOT on disjoint
folds, so MIN-across-folds collapses for a hallucination and stays high for a genuine key.

- A **caught** hallucination = strengthened proxy held-out recovery < 0.90 (is_hit real-mode False).
- A **false-reject** = genuine decode (true recovery 1.0) with strengthened held-out recovery < 0.90.
- The recogniser is proven by the STRICT (truth-supplied) path agreeing with the intent on controls.

## Q2 — prior / measured foothold

`round20/S-RESCOPE/out_heldout_proxy_audit.json` localises the leak to the keyskip relation's single
1/4->3/4 cut and lists the 45 hallucinations' single-cut held-out recoveries (30 of them >=0.90 =
the misses). The candidate mechanism (disjoint folds) is named in SYNTHESIS §8.4 and CAMPAIGN-PLAN
L1. This is a measured redesign of one clause, not a build from zero. Composed instruments
(driftbeam recovery, adjudicate/pmax, panelmax_bar exact/1e6=7.634) are all already validated.

## Q3 — bounded / enumerable

Proxy parameter space = fold count k in {2,3,4,5,6} x agreement rule in {min, mean, frac_pass} x
(pass-threshold for frac_pass). ~15-20 (k, rule) cells. Tune the cell on the FROZEN planted-45,
freeze the winning cell, then audit on a held-out surrogate set (fresh seeds / fresh
order-preserving surrogate). Each cell costs (k+1) extra beam decodes per case; 45 cases x ~18 cells
x ~6 decodes ~ 5000 beam calls at ~0.02s each ~ a few minutes. Time-boxed <=20 min; if larger, run
a stated fraction.

## Q4 — three conditionals reported together (catch SURFACE)

Report catch as a function of (relation {keyskip1/exact}, register {EN_NOVOWEL}, fold-scheme
{k, rule}). `catch_surface.json` is that surface, so every downstream HIT-certification names its
operating point. Every negative names: (key space = correct key, the hardest case), (decoder
relation = exact/keyskip1 preset), (adjudicator register = EN_NOVOWEL argmax).

## Q5 — pass / kill condition (SET IN ADVANCE, not editable after results)

**PASS requires ALL of:**
- (P-a) Some frozen (k, rule) cell reaches **>=0.90 catch** on the planted-45 EN_NOVOWEL population
  (>= 41/45 caught).
- (P-b) That SAME frozen cell holds **>=0.90 catch** on a held-out surrogate set (fresh seeds +
  fresh order-preserving surrogate) — generalisation, not overfit to the 45.
- (P-c) The genuine decode (true recovery 1.0) is still **ACCEPTED**: its strengthened held-out
  recovery >= 0.90 (genuine-decode false-reject rate <= 0.10 measured over a genuine-decode panel).
- (P-d) `tests/validate.py` still PASSES (trust anchor untouched); SWEEPROW/3 field order unchanged.

**KILL (declare the no-oracle gate provably leaky):** if NO (k, rule) cell reaches >=0.90 catch
without genuine-decode false-reject exceeding 0.10, rule that Round 21's sweeps report bar-clearing
survivors as **flagged-for-oracle** (never auto-certified). Report it as a measured bound. High-prior
lanes still run (coverage x power bounds regardless); only auto-HIT-calling is withheld.

## Positive controls (planted, run FIRST; gate everything)

1. **Genuine decode:** English plaintext, keyskip encipherment, CORRECT key -> expect true recovery
   1.0 and strengthened held-out recovery >= 0.90 -> is_hit real-mode = True. Also a genuine-decode
   PANEL (>= 10 genuine decodes) to measure false-reject rate under the frozen cell.
2. **Hallucination population:** the 45 EN_NOVOWEL bar-clearing decodes (reproduced bit-identically
   from the S-RESCOPE recipe: Kfull=make_ks("sha256_ctr","mod29",b"CICADA",L*4+1024), L=240,
   rep in range(60), rng=Random(5000+rep), P=EN_NOVOWEL slice, C=encipher_keyskip(P,Kfull,sign=-1,
   supp=0.83,seed=600+rep), keep pmax>=bar & true recovery<0.90). Must reproduce 45/45 and the
   15/45 single-cut baseline before the fold variant is trusted.

A null from this instrument is trustworthy only after both controls pass (doctrine: a null from an
unvalidated instrument is not a negative). The frozen cell is chosen on the 45 and NOT re-tuned after
seeing the held-out surrogate result.
