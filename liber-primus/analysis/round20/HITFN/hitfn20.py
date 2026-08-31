"""hitfn20 -- THE recovery-gated hit decision for Round 20 Phase S.

Resolves red-team FOUND-ERROR (d) (SYNTHESIS Section 3): before this module, panelmax20.py
returned a SCORE bar only, SWEEPROW/1 carried no recovery field, and no hit-decision function
existed -- so any S-lane certifying on `pmax >= bar` would certify a HALLUCINATING decode
(EN_NOVOWEL clears the panel-max bar at rune-index recovery 0.84 exact / 0.26 drift, both
< 0.90). This module ships the one predicate the win-condition demands.

    from hitfn20 import is_hit, HitDecode, adjudicate_hit_row

    dec = HitDecode(C=cipher_idx, K=key_idx, o=0, preset="exact",
                    n_round_adjudicated=10**6)      # a real LP2 candidate: no truth_idx
    verdict = is_hit(dec)                            # -> HitVerdict(hit=bool, ...)

A HIT requires ALL THREE (CAMPAIGN-PLAN Section 2; doctrine win-condition):
  (1) pmax clears the P3 panel-max null  (panelmax20.panelmax_bar, NEVER -5.5, NEVER a k_eff)
  (2) rune-INDEX recovery >= 0.90, recovered from the driftbeam DECODE PATH (never from score)
  (3) the SAME key, attributed on 1/4 of the page, reproduces recovery >= 0.90 on the
      held-out 3/4 of the same page under that key.

Score alone is NOT a hit. is_hit REJECTS on the first failing clause and names it.

WHY THIS IS COMPUTABLE ON A REAL CANDIDATE (the crux of defect d).
`driftbeam.recovery(plain_idx, truth_idx)` needs ground-truth plaintext, which no real LP2
candidate provides. Clause (3) removes that dependency: it re-runs the SAME beam decoder with
the SAME key on the HELD-OUT 3/4 of the ciphertext and measures whether the re-decode
reproduces the full-page decode's own rune indices on that region. A genuine key reproduces
(the decode is a fixed function of key x ciphertext); a hallucinating beam (wandering into a
low-alphabet basin off the true transition relation) does NOT reproduce off the window it
overfit. So the gate needs no plaintext oracle. When a ground-truth `truth_idx` IS supplied
(plants/controls only), clause (2)+(3) are measured against it directly -- the strict test the
hallucination guard is proven against.
"""
import os
import sys
from dataclasses import dataclass, field
from typing import Optional, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R19 = os.path.join(LP, "analysis", "round19")
R20 = os.path.join(LP, "analysis", "round20")
for _p in (os.path.join(R19, "I1"), os.path.join(R19, "I2"), os.path.join(R20, "P3"),
           os.path.join(LP, "src"), os.path.join(LP, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import driftbeam as DB                 # noqa: E402  the drift-tolerant beam decoder (I1)
import adjudicate as AD                # noqa: E402  the 9-register panel + SWEEPROW (I2)
import panelmax20 as PM                # noqa: E402  the ONE calibrated panel-max bar (P3a)

RECOVERY_BAR = 0.90                     # CAMPAIGN-PLAN Section 2; NEVER relax without re-prereg
HELDOUT_FIT_FRACTION = 0.25            # attribute on 1/4, verify on the held-out 3/4
EN_NOVOWEL_REG = 8                      # index of EN_NOVOWEL in AD.panel().registers (detection-only)


# --------------------------------------------------------------------------- decode contract
@dataclass
class HitDecode:
    """One candidate to adjudicate. On a REAL LP2 candidate, supply C/K/o/preset only; the
    plaintext-index path and the held-out re-decode are both derived from the beam decoder.
    On a PLANT/control, additionally supply `truth_idx` to measure the STRICT recovery the
    hallucination guard is proven against."""
    C: Sequence[int]                                # ciphertext rune indices for the page
    K: Sequence[int]                                # attributed keystream rune indices
    o: int = 0                                      # key offset
    sign: int = -1
    preset: str = "exact"                           # driftbeam preset -> panelmax preset
    n_round_adjudicated: int = 10 ** 6              # how many decodes THIS lane adjudicated (bar N)
    alpha: float = 0.01                             # claim level
    truth_idx: Optional[Sequence[int]] = None       # plaintext indices -- CONTROLS ONLY
    # optional pre-computed full-page decode (skips one beam call when the caller already has it)
    _decoded: Optional[dict] = field(default=None, repr=False)

    def preset_kw(self):
        return DB.PRESETS[self.preset]


@dataclass
class HitVerdict:
    hit: bool
    reason: str                                     # which clause fired (or "all clauses pass")
    pmax: float
    bar: float
    clears_null: bool
    recovery: float                                 # clause-2 rune-index recovery (path, not score)
    recovery_ok: bool
    heldout_recovery: float                         # clause-3 held-out 3/4 recovery
    heldout_ok: bool
    preg: int                                       # argmax register (8 == EN_NOVOWEL, detection-only)
    preg_name: str
    score: float                                    # the beam score -- reported, NOT gated on
    n: int
    preset: str
    recovery_source: str                            # "truth_idx" (control) | "heldout_selfconsistency"


# --------------------------------------------------------------------------- helpers
def _full_decode(dec: HitDecode) -> dict:
    if dec._decoded is None:
        dec._decoded = DB.beam_decode(list(dec.C), list(dec.K), sign=dec.sign, o=dec.o,
                                      beam_w=400, want_path=True, **dec.preset_kw())
    return dec._decoded


def _heldout_recovery(dec: HitDecode, full_idx: Sequence[int]) -> float:
    """Clause 3, the real-candidate-safe recovery. FIT/attribute the key on the first 1/4 of
    the page, then RE-DECODE the held-out 3/4 with the SAME key from the attributed key phase
    and measure agreement. No plaintext oracle needed.

    FIT step (on 1/4). Decode ONLY the first quarter with the candidate key. That sub-decode's
    ending key pointer (`ptr_end`) is where the key phase stands entering the held-out 3/4 --
    a genuine key advances its pointer by (cut + its own skips), which is exactly what the
    quarter sub-decode reproduces. This is 'attribute the key on 1/4' made concrete: the
    quarter fixes the phase, nothing is fit to the held-out region.

    VERIFY step (on 3/4). Decode the held-out tail from that attributed pointer and compare
    rune-for-rune. A genuine key reproduces the tail (its transition relation holds on unseen
    ciphertext); a hallucinating beam that only clears the bar by wandering into a low-alphabet
    basin does NOT reproduce off the window it overfit -> low held-out recovery -> rejected."""
    C = list(dec.C)
    K = list(dec.K)
    n = len(C)
    if n < 8:
        return 0.0
    cut = max(1, int(round(n * HELDOUT_FIT_FRACTION)))
    head_C, tail_C = C[:cut], C[cut:]
    if len(tail_C) < 3 or len(head_C) < 1:
        return 0.0
    # FIT: attribute the key phase on the first quarter (its ending key pointer).
    head_dec = DB.beam_decode(head_C, K, sign=dec.sign, o=dec.o, beam_w=400,
                              want_path=True, **dec.preset_kw())
    # ptr_end is the key index consumed by the head's LAST rune; the tail's first rune consumes
    # the NEXT key position, so the attributed phase entering the tail is ptr_end + 1.
    kp = head_dec["ptr_end"] + 1                   # attributed key pointer entering the tail
    # VERIFY: decode the held-out 3/4 from the attributed phase with the SAME key.
    tail_dec = DB.beam_decode(tail_C, K, sign=dec.sign, o=kp, beam_w=400,
                              want_path=True, **dec.preset_kw())
    tail_idx = tail_dec["plain_idx"]
    if dec.truth_idx is not None:
        # STRICT control path: compare the held-out re-decode to GROUND TRUTH on the tail.
        truth_tail = list(dec.truth_idx)[cut:]
        m = min(len(tail_idx), len(truth_tail))
        if m == 0:
            return 0.0
        return sum(1 for a, b in zip(tail_idx[:m], truth_tail[:m]) if a == b) / m
    # REAL path: self-consistency of the held-out re-decode vs the full decode's own tail.
    tail_full = list(full_idx)[cut:]
    m = min(len(tail_idx), len(tail_full))
    if m == 0:
        return 0.0
    return sum(1 for a, b in zip(tail_idx[:m], tail_full[:m]) if a == b) / m


# --------------------------------------------------------------------------- THE PREDICATE
def evaluate(dec: HitDecode) -> HitVerdict:
    """Full adjudication returning every measured field. `is_hit` is the boolean of this."""
    d = _full_decode(dec)
    plain_idx = d["plain_idx"]
    a = AD.adjudicate(plain_idx, translit=d.get("translit"))
    pmax = float(a["pmax"])
    preg = int(a["preg"])
    preg_name = AD.panel().registers[preg]

    bar = PM.panelmax_bar(preset=dec.preset, n_round_adjudicated=dec.n_round_adjudicated,
                          alpha=dec.alpha)
    clears = pmax >= bar

    # clause (2): rune-INDEX recovery from the DECODE PATH, never from score.
    if dec.truth_idx is not None:
        rec = DB.recovery(plain_idx, list(dec.truth_idx))
        rec_src = "truth_idx"
    else:
        # real candidate: recovery IS the held-out self-consistency (no plaintext oracle).
        # We compute the held-out number once and use it for clause 2 as well, so a real
        # candidate is gated purely on reproduction -- exactly what defect (d) demands.
        rec = _heldout_recovery(dec, plain_idx)
        rec_src = "heldout_selfconsistency"
    rec_ok = rec >= RECOVERY_BAR

    # clause (3): held-out 3/4 reproduction under the SAME key.
    ho = _heldout_recovery(dec, plain_idx)
    ho_ok = ho >= RECOVERY_BAR

    # decide + name the FIRST failing clause (order: null, recovery, held-out).
    if not clears:
        hit, reason = False, f"FAIL clause1: pmax {pmax:.3f} < panel-max bar {bar:.3f}"
    elif not rec_ok:
        hit, reason = False, (f"FAIL clause2: rune-index recovery {rec:.3f} < {RECOVERY_BAR} "
                              f"(source={rec_src}, preg={preg_name}); "
                              f"score {d['score']:.3f} clears the bar but the DECODE DOES NOT "
                              f"RECOVER -- a hallucinating decode, rejected.")
    elif not ho_ok:
        hit, reason = False, (f"FAIL clause3: held-out 3/4 recovery {ho:.3f} < {RECOVERY_BAR} "
                              f"-- key attributed on 1/4 does not reproduce on the held-out "
                              f"page; overfit, rejected.")
    else:
        hit, reason = True, "HIT: clears panel-max null AND recovery>=0.90 AND held-out 3/4 reproduces"

    return HitVerdict(
        hit=hit, reason=reason, pmax=pmax, bar=float(bar), clears_null=clears,
        recovery=float(rec), recovery_ok=rec_ok,
        heldout_recovery=float(ho), heldout_ok=ho_ok,
        preg=preg, preg_name=preg_name, score=float(d["score"]),
        n=int(len(plain_idx)), preset=dec.preset, recovery_source=rec_src)


def is_hit(decode: HitDecode) -> bool:
    """THE predicate. True ONLY when the decode clears the panel-max null AND has rune-index
    recovery >= 0.90 (from the decode path, not score) AND reproduces on the held-out 3/4 of
    the same page under the same key. Score alone is never a hit."""
    return evaluate(decode).hit


# --------------------------------------------------------------------------- SWEEPROW/3 emitter
# SWEEPROW/1 (I2) has no recovery field. Defect (d) requires every downstream row to carry
# recovery. We EXTEND the fixed field order by appending (append-only, per I2 SWEEPROW.md), so
# every existing SWEEPROW/1 consumer still reads its fields at the same positions.
SCHEMA_VERSION_V3 = "SWEEPROW/3"
ROW_FIELDS_V3 = AD.ROW_FIELDS + ["recovery", "heldout_recovery", "recovery_source",
                                 "clears_null", "hit"]


def adjudicate_hit_row(dec: HitDecode, kid):
    """Return a SWEEPROW/3 row: the full SWEEPROW/1 array PLUS the recovery gate fields.
    This is the emitter every Phase-S lane calls so no downstream row is score-only again."""
    d = _full_decode(dec)
    res = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    base = AD.to_row(res, kid)
    v = evaluate(dec)
    return base + [round(v.recovery, 4), round(v.heldout_recovery, 4),
                   v.recovery_source, bool(v.clears_null), bool(v.hit)]


def header_v3(sweep_id, dec_preset="exact", n_round_adjudicated=10 ** 6, **extra):
    """SWEEPROW/3 header: the I2 header plus the recovery-gate contract, so a store is
    self-describing about which bar and which recovery rule gated it."""
    h = AD.header(sweep_id, **extra)
    h["v"] = SCHEMA_VERSION_V3
    h["fields"] = ROW_FIELDS_V3
    h["recovery_gate"] = {
        "recovery_bar": RECOVERY_BAR,
        "heldout_fit_fraction": HELDOUT_FIT_FRACTION,
        "panelmax_contract": PM.panelmax_contract(preset=dec_preset,
                                                  n_round_adjudicated=n_round_adjudicated),
        "rule": ("HIT iff pmax>=panelmax_bar AND recovery>=0.90 (from decode path, not score) "
                 "AND held-out-3/4 recovery>=0.90 under the same key. Score alone is not a hit "
                 "(resolves red-team defect d)."),
    }
    return h


def validate_row_v3(row, hdr=None):
    """Raise AD.RowError unless `row` is a well-formed SWEEPROW/3 (the I2 validator on the base
    fields, plus the recovery-gate fields)."""
    if not isinstance(row, (list, tuple)) or len(row) != len(ROW_FIELDS_V3):
        raise AD.RowError(f"SWEEPROW/3 needs {len(ROW_FIELDS_V3)} fields {ROW_FIELDS_V3}, "
                          f"got {len(row) if isinstance(row,(list,tuple)) else type(row).__name__}")
    AD.validate_row(list(row)[:len(AD.ROW_FIELDS)])   # base SWEEPROW/1 must be valid
    d = dict(zip(ROW_FIELDS_V3, row))
    for f in ("recovery", "heldout_recovery"):
        if not isinstance(d[f], (int, float)) or not (0.0 <= d[f] <= 1.0):
            raise AD.RowError(f"{f} must be a fraction in [0,1], got {d[f]!r}")
    if not isinstance(d["hit"], bool):
        raise AD.RowError(f"hit must be bool, got {d['hit']!r}")
    if not isinstance(d["clears_null"], bool):
        raise AD.RowError(f"clears_null must be bool, got {d['clears_null']!r}")
    # a row cannot be a HIT unless it cleared the null and recovered on the held-out page
    if d["hit"] and not d["clears_null"]:
        raise AD.RowError("hit=True with clears_null=False -- gate is inconsistent")
    if d["hit"] and d["heldout_recovery"] < RECOVERY_BAR:
        raise AD.RowError(f"hit=True with held-out recovery {d['heldout_recovery']} < "
                          f"{RECOVERY_BAR} -- gate is inconsistent")
    return True


if __name__ == "__main__":
    import json
    from guard import run_guard
    out = run_guard()
    print(json.dumps(out["summary"], indent=1))
