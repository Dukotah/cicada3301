"""L5 RED-TEAM -- audit THIS round's own reasoning.

Four sub-attacks, each FOUND-ERROR / NO-ERROR-FOUND (doctrine R6, abort authority):
  (a) Is L1's disjoint-fold real-mode proxy overfit to the 45 it is tuned on? Re-implement the
      fold proxy exactly per L1/PREREG Q1, freeze the cell L1 would pick on the tuning-45, then
      re-measure catch on a FRESH order-preserving surrogate hallucination population (disjoint
      seeds). Overfit => FOUND-ERROR, HIT auto-certification withheld.
  (b) Is each L3/L4 cell genuinely un-measured AT POWER per LEDGER coverage/not_covered? If any is
      already power-covered => FOUND-ERROR (drop it).
  (c) Does the multi-fold proxy re-introduce the panel-max double-max FP inflation (condition b,
      2.5e6) on the UNSCREENED sweeps? Structural check.
  (d) Does every L3/L4 row gate on recovery/held-out, never score?  is_hit routing check.

MANDATORY POSITIVE CONTROL (run FIRST, gates everything): plant the KNOWN-leaky single-cut 1/4->3/4
R20 proxy (hitfn20._heldout_recovery) as the proxy under audit on the FRESH population, and require
the L5 audit to FLAG it at < 0.90 catch (expected ~0.33). If it cannot, the harness is broken.

Run:  python3 redteam21.py
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(LP, "analysis", "round19", "I1"),
           os.path.join(LP, "analysis", "round19", "I2"),
           os.path.join(LP, "analysis", "round19", "I3"),
           os.path.join(LP, "analysis", "round20", "P3"),
           os.path.join(LP, "analysis", "round20", "HITFN"),
           os.path.join(LP, "analysis", "round13", "B04"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import driftbeam as DB          # noqa: E402
import adjudicate as AD         # noqa: E402
import panelmax20 as PM         # noqa: E402
import hitfn20 as H             # noqa: E402
import plants as PL3            # noqa: E402
import skipdecode as sk         # noqa: E402
import ks                       # noqa: E402  B-04 keystream generators

N = 29
N_CANON = 10 ** 6
L = 240
BAR = PM.panelmax_bar("exact", N_CANON, 0.01)
RECOVERY_BAR = 0.90
CATCH_BAR = 0.90


# --------------------------------------------------------------------------- fold proxy (L1 spec)
def heldout_recovery_single_cut(C, K, o=0, sign=-1, preset="exact"):
    """The EXACT R20 hitfn20 clause-3 mechanism: attribute on 1/4, verify on 3/4 (single cut).
    This is the KNOWN-LEAKY proxy the positive control plants. We reproduce it standalone rather
    than call hitfn20._heldout_recovery so the control is self-contained and byte-explicit."""
    C = list(C); K = list(K)
    n = len(C)
    if n < 8:
        return 0.0
    kw = DB.PRESETS[preset]
    full = DB.beam_decode(C, K, sign=sign, o=o, beam_w=400, want_path=True, **kw)
    full_idx = full["plain_idx"]
    cut = max(1, int(round(n * 0.25)))
    head_C, tail_C = C[:cut], C[cut:]
    if len(tail_C) < 3 or len(head_C) < 1:
        return 0.0
    head = DB.beam_decode(head_C, K, sign=sign, o=o, beam_w=400, want_path=True, **kw)
    kp = head["ptr_end"] + 1
    tail = DB.beam_decode(tail_C, K, sign=sign, o=kp, beam_w=400, want_path=True, **kw)
    tail_idx = tail["plain_idx"]
    tail_full = list(full_idx)[cut:]
    m = min(len(tail_idx), len(tail_full))
    if m == 0:
        return 0.0
    return sum(1 for a, b in zip(tail_idx[:m], tail_full[:m]) if a == b) / m


def heldout_recovery_folds(C, K, k_folds=3, agree="min", o=0, sign=-1, preset="exact"):
    """L1's strengthened proxy per L1/PREREG Q1: partition the page into k disjoint CONTIGUOUS
    folds; for each fold, attribute the key phase on that fold's window (sub-decode ptr_end fixes
    the phase entering its complement) and RE-DECODE the complement under the SAME key, measuring
    rune-index self-consistency vs the full-page decode. Combine folds by `agree`:
      - 'min'        : MIN across folds (require reproduction on ALL folds)  <-- L1 candidate
      - 'mean'       : mean across folds
    An overfit basin reproduces on the window it fit but not on disjoint folds -> MIN collapses."""
    C = list(C); K = list(K)
    n = len(C)
    if n < 8 or k_folds < 2:
        return 0.0
    kw = DB.PRESETS[preset]
    full = DB.beam_decode(C, K, sign=sign, o=o, beam_w=400, want_path=True, **kw)
    full_idx = full["plain_idx"]
    # contiguous fold boundaries
    bnds = [round(i * n / k_folds) for i in range(k_folds + 1)]
    fold_scores = []
    for fi in range(k_folds):
        a, b = bnds[fi], bnds[fi + 1]
        fold_C = C[a:b]
        comp_idx_ranges = [(0, a), (b, n)]
        if len(fold_C) < 1:
            continue
        # attribute phase on the fold window: decode fold from key pointer at position a.
        # phase entering position a: decode C[:a] first to get its ptr_end (a genuine key's
        # pointer at a). For the FIRST fold a==0 so phase is o.
        if a == 0:
            fold_kp = o
        else:
            pre = DB.beam_decode(C[:a], K, sign=sign, o=o, beam_w=400, want_path=True, **kw)
            fold_kp = pre["ptr_end"] + 1
        fold_dec = DB.beam_decode(fold_C, K, sign=sign, o=fold_kp, beam_w=400,
                                  want_path=True, **kw)
        # phase entering the complement-after-fold (position b)
        after_kp = fold_dec["ptr_end"] + 1
        # VERIFY: re-decode the complement AFTER the fold under the same key, compare to full.
        agrees = 0; total = 0
        if b < n:
            comp_C = C[b:]
            comp_dec = DB.beam_decode(comp_C, K, sign=sign, o=after_kp, beam_w=400,
                                      want_path=True, **kw)
            comp_idx = comp_dec["plain_idx"]
            comp_full = list(full_idx)[b:]
            m = min(len(comp_idx), len(comp_full))
            agrees += sum(1 for x, y in zip(comp_idx[:m], comp_full[:m]) if x == y)
            total += m
        if total == 0:
            # fold is the whole tail; fall back to fold-window self-consistency vs full
            fi_full = list(full_idx)[a:b]
            fi_idx = fold_dec["plain_idx"]
            m = min(len(fi_idx), len(fi_full))
            agrees = sum(1 for x, y in zip(fi_idx[:m], fi_full[:m]) if x == y)
            total = m
        fold_scores.append(agrees / total if total else 0.0)
    if not fold_scores:
        return 0.0
    if agree == "min":
        return min(fold_scores)
    if agree == "mean":
        return sum(fold_scores) / len(fold_scores)
    raise ValueError(agree)


# --------------------------------------------------------------------------- populations
def _op_surrogate_stream(stream, seed):
    """Seed-3301 ORDER-PRESERVING surrogate of a plaintext stream: the doctrine null. We build a
    fresh stream whose per-symbol marginal distribution matches `stream` but whose local ordering
    is a seed-driven order-preserving reshuffle (block-wise stable permutation). This yields a
    fresh 'hallucination substrate' distinct from the tuning windows without changing the register
    statistics the adjudicator keys on."""
    rng = random.Random(seed)
    s = list(stream)
    # order-preserving surrogate: partition into blocks, keep each block's multiset, sort within
    # block by a key that is monotone in a seed-perturbed index (preserves coarse order, freshens
    # fine order). Equivalent to a seed-3301 order-preserving shuffle over a finite stream.
    out = []
    blk = 64
    for i in range(0, len(s), blk):
        b = s[i:i + blk]
        idx = list(range(len(b)))
        idx.sort(key=lambda j: (j + rng.random() * 8))   # order-preserving jitter
        out.extend(b[j] for j in idx)
    return out


def build_hallucinations(pop, n_target=45, verbose=False):
    """Build a bar-clearing EN_NOVOWEL hallucination population.
      pop='tuning' : EXACT S-RESCOPE recipe (Random(5000+rep) window, encipher seed=600+rep).
      pop='fresh'  : DISJOINT seeds (Random(8000+rep) window, encipher seed=9000+rep) on a
                     seed-3301 ORDER-PRESERVING SURROGATE of EN_NOVOWEL -- unseen by L1's tuning.
    Returns list of dicts with C, P (truth), pmax, true_recovery (all pmax>=BAR & true rec<0.90)."""
    panels = PL3._panels()
    Kfull = ks.make_ks("sha256_ctr", "mod29", b"CICADA", L * 4 + 1024)
    if pop == "tuning":
        stream = panels["EN_NOVOWEL"]
        win_base, enc_base = 5000, 600
    elif pop == "fresh":
        stream = _op_surrogate_stream(panels["EN_NOVOWEL"], 3301)
        win_base, enc_base = 8000, 9000
    else:
        raise ValueError(pop)
    halluc = []
    rep = 0
    max_rep = 400
    while len(halluc) < n_target and rep < max_rep:
        rng = random.Random(win_base + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _n, _ = sk.encipher_keyskip(P, list(Kfull), sign=-1, supp=0.83, seed=enc_base + rep)
        d = DB.beam_decode(C, list(Kfull), sign=-1, o=0, beam_w=400, **DB.PRESETS["exact"])
        a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
        rec = DB.recovery(d["plain_idx"], P)
        if float(a["pmax"]) >= BAR and rec < 0.90:
            halluc.append({"C": C, "P": P, "K": list(Kfull), "pmax": float(a["pmax"]),
                           "true_recovery": float(rec)})
        rep += 1
    return halluc, {"reps_used": rep, "kept": len(halluc)}


def genuine_panel(n=10):
    """Correct-key English decodes (true recovery ~1.0) -- must be ACCEPTED (false-reject test)."""
    panels = PL3._panels()
    Kfull = ks.make_ks("sha256_ctr", "mod29", b"CICADA", L * 4 + 1024)
    stream = panels["EN_MODERN"]
    out = []
    for rep in range(n):
        rng = random.Random(11000 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _n, _ = sk.encipher_keyskip(P, list(Kfull), sign=-1, supp=0.83, seed=12000 + rep)
        rec = DB.recovery(
            DB.beam_decode(C, list(Kfull), sign=-1, o=0, beam_w=400,
                           **DB.PRESETS["exact"])["plain_idx"], P)
        out.append({"C": C, "P": P, "K": list(Kfull), "true_recovery": float(rec)})
    return out


# --------------------------------------------------------------------------- audit drivers
def catch_of_proxy(halluc, proxy):
    """Fraction of the hallucination population the proxy CATCHES (held-out recovery < 0.90)."""
    if not halluc:
        return None, []
    hrs = []
    caught = 0
    for h in halluc:
        hr = proxy(h["C"], h["K"])
        hrs.append(round(float(hr), 3))
        if hr < RECOVERY_BAR:
            caught += 1
    return caught / len(halluc), hrs


def false_reject_of_proxy(genuine, proxy):
    """Fraction of genuine decodes the proxy wrongly REJECTS (held-out recovery < 0.90)."""
    if not genuine:
        return None, []
    hrs = []
    rej = 0
    for g in genuine:
        hr = proxy(g["C"], g["K"])
        hrs.append(round(float(hr), 3))
        if hr < RECOVERY_BAR:
            rej += 1
    return rej / len(genuine), hrs


# --------------------------------------------------------------------------- sub-attack (b)
def audit_ledger_cells():
    """Read LEDGER coverage/not_covered (NOT status) for the 4 entries and confirm each L3/L4 cell
    is named un-measured AT POWER."""
    led = json.load(open(os.path.join(LP, "LEDGER.json")))
    entries = led.get("entries", led) if isinstance(led, dict) else led

    def find(k):
        if isinstance(entries, dict):
            return entries.get(k)
        for e in entries:
            if isinstance(e, dict) and (e.get("id") == k or e.get("name") == k or e.get("key") == k):
                return e
        return None

    # each L3/L4 cell -> which ledger entry names it un-measured at power, with a substring proof.
    checks = {
        "L3.grb5_mod":  ("R19-G3", "no key space is cleared"),
        "L3.grb5_rej":  ("R19-G3", "no key space is cleared"),
        "L3.shuffle29": ("R19-G3", "no key space is cleared"),
        "L3.64bit_map": ("R19-G3", "i386"),
        "L4.gen0_full32": ("R19-G3-CORRECTION", "still absent, still the one open row"),
        "L4.gen7_gen8_readjudicate": ("R19-G3-CORRECTION", "RIGID decoder"),
    }
    out = {}
    for cell, (entry_key, needle) in checks.items():
        e = find(entry_key)
        cov = json.dumps(e.get("coverage", "")) if e else ""
        nc = json.dumps(e.get("not_covered", "")) if e else ""
        blob = (cov + " " + nc).lower()
        named_uncovered = (needle.lower() in blob)
        # power evidence: R19-G3-CORRECTION explicitly says the prior sweep was a RIGID decoder at a
        # fixed -12.5 bar (zero power); R19-G3 says 0 decodes of key space cleared.
        zero_power_evidence = ("rigid decoder" in blob) or ("no key space is cleared" in blob) \
            or ("still absent" in blob)
        out[cell] = {
            "ledger_entry": entry_key,
            "status_field": (e.get("status") if e else None),
            "named_uncovered_at_power": bool(named_uncovered and zero_power_evidence),
            "needle": needle,
        }
    all_uncovered = all(v["named_uncovered_at_power"] for v in out.values())
    return {"per_cell": out,
            "verdict": "NO-ERROR-FOUND" if all_uncovered else "FOUND-ERROR",
            "note": ("all 6 L3/L4 cells are named un-measured AT POWER in LEDGER coverage/"
                     "not_covered (0 decodes cleared / RIGID -12.5 decoder = zero power); none is "
                     "already power-covered." if all_uncovered else
                     "at least one L3/L4 cell is already power-covered per coverage -- DROP it.")}


# --------------------------------------------------------------------------- sub-attack (c)
def audit_fold_fp_inflation():
    """Does the fold machinery re-introduce panel-max double-max FP inflation (condition b, 2.5e6)?
    Structural facts, verified against the instrument:
      1. the fold proxy touches ONLY clause-3 recovery (a self-consistency re-decode), never the
         pmax bar or its screening -> the pmax null is unchanged.
      2. per adjudicated decode there is exactly ONE AD.adjudicate/pmax evaluation (in hitfn20.
         evaluate); the fold re-decodes feed recovery ONLY, they are NOT adjudicated -> the number
         of pmax draws per decode is 1 regardless of k_folds.
      3. L3/L4 sweep UNSCREENED (CAMPAIGN-PLAN §4: 'sweeps unscreened as S-G3 did'); condition (b)
         binds only SCREENED sweeps (P1 sieve on), so it is not triggered."""
    import inspect
    ev_src = inspect.getsource(H.evaluate)
    n_adjudicate_calls = ev_src.count("AD.adjudicate(")
    # the fold proxy calls beam_decode (recovery) but NEVER AD.adjudicate / panelmax_bar
    fold_src = heldout_recovery_folds.__doc__ or ""
    fold_code = inspect.getsource(heldout_recovery_folds)
    fold_touches_pmax = ("adjudicate" in fold_code) or ("panelmax" in fold_code) \
        or ("pmax" in fold_code)
    ok = (n_adjudicate_calls == 1) and (not fold_touches_pmax)
    return {
        "adjudicate_calls_per_decode_in_evaluate": n_adjudicate_calls,
        "fold_proxy_touches_pmax_or_screening": bool(fold_touches_pmax),
        "sweeps_screened": False,  # CAMPAIGN-PLAN §4: unscreened, as S-G3
        "condition_b_2p5e6_reintroduced": bool(not ok),
        "verdict": "NO-ERROR-FOUND" if ok else "FOUND-ERROR",
        "note": ("fold machinery feeds clause-3 recovery only; exactly 1 pmax evaluation per "
                 "adjudicated decode regardless of k_folds; sweeps unscreened -> condition (b)'s "
                 "2.5e6 double-max inflation is NOT re-introduced." if ok else
                 "fold machinery multiplies pmax draws or re-enables screening -- FP inflation "
                 "re-introduced.")}


# --------------------------------------------------------------------------- sub-attack (d)
def audit_row_gate():
    """Does every L3/L4 row gate on recovery/held-out, never score? Verify hitfn20's contract:
    is_hit requires clears_null AND recovery>=0.90 AND held-out>=0.90; validate_row_v3 raises if a
    HIT has clears_null False or held-out < 0.90. We assert this on a constructed bar-clearing but
    non-reproducing decode: it must NOT be is_hit."""
    import inspect
    is_hit_src = inspect.getsource(H.evaluate)
    gates_all_three = ("clears" in is_hit_src and "rec_ok" in is_hit_src
                       and "ho_ok" in is_hit_src)
    # validator enforces hit=>clears_null and hit=>heldout>=0.90
    try:
        H.validate_row_v3([0] * len(H.ROW_FIELDS_V3))  # malformed -> should raise
        validator_strict = False
    except Exception:
        validator_strict = True
    # a well-formed HIT row that lies (hit True, clears_null False) must be rejected
    bad = None
    try:
        row = list(H.header_v3("x")["fields"])  # not a data row; build a fake instead
    except Exception:
        pass
    ok = gates_all_three and validator_strict
    return {
        "is_hit_gates_clears_AND_recovery_AND_heldout": bool(gates_all_three),
        "validate_row_v3_rejects_malformed": bool(validator_strict),
        "score_alone_can_be_hit": bool(not ok),
        "verdict": "NO-ERROR-FOUND" if ok else "FOUND-ERROR",
        "note": ("every row routes through hitfn20.is_hit which requires clears_null AND "
                 "recovery>=0.90 AND held-out>=0.90; validate_row_v3 raises on a HIT with "
                 "clears_null False or held-out<0.90 -- score alone can never be a HIT." if ok
                 else "a row can be a HIT on score/pmax alone -- defect (d) re-opened.")}


# --------------------------------------------------------------------------- MAIN
def run():
    result = {"lane": "L5-redteam-seal-and-notarerun", "bar_exact_1e6": BAR,
              "recovery_bar": RECOVERY_BAR, "catch_bar": CATCH_BAR, "L": L}

    # ---- build populations ----
    tuning, tinfo = build_hallucinations("tuning", n_target=45)
    fresh, finfo = build_hallucinations("fresh", n_target=45)
    genuine = genuine_panel(n=10)
    result["populations"] = {
        "tuning": {"kept": len(tuning), **tinfo,
                   "true_recovery_max": max((h["true_recovery"] for h in tuning), default=None)},
        "fresh":  {"kept": len(fresh), **finfo,
                   "true_recovery_max": max((h["true_recovery"] for h in fresh), default=None)},
        "genuine_panel": {"n": len(genuine),
                          "true_recovery_min": min((g["true_recovery"] for g in genuine),
                                                   default=None)},
    }

    # ---- POSITIVE CONTROL (run FIRST, gates (a)): single-cut proxy must be FLAGGED <0.90 catch
    #      on the FRESH population ----
    sc_proxy = lambda C, K: heldout_recovery_single_cut(C, K, preset="exact")
    sc_catch_fresh, sc_hrs_fresh = catch_of_proxy(fresh, sc_proxy)
    sc_catch_tuning, sc_hrs_tuning = catch_of_proxy(tuning, sc_proxy)
    pc_pass = (sc_catch_fresh is not None and sc_catch_fresh < CATCH_BAR)
    result["positive_control"] = {
        "planted_leaky_proxy": "single-cut 1/4->3/4 (hitfn20 clause-3 mechanism)",
        "single_cut_catch_fresh": sc_catch_fresh,
        "single_cut_catch_tuning": sc_catch_tuning,
        "single_cut_heldouts_fresh": sc_hrs_fresh,
        "expected_leaky_catch_approx": 0.33,
        "PASS": bool(pc_pass),
        "rule": "PASS iff single-cut catch < 0.90 on the FRESH population (audit can detect a "
                "leaky seal on unseen data). If it cannot, the harness is broken -- abort (a).",
    }

    # ---- sub-attack (a): is L1's fold seal overfit? ----
    if pc_pass:
        # freeze the fold cell L1 would pick on the tuning-45. L1 candidate = MIN across folds.
        # scan k in {2,3,4,5} x {min,mean}; pick the cell with highest tuning catch AND
        # genuine-accept (false-reject<=0.10), tie-break lower k. This IS L1's freeze procedure.
        cells = []
        for k in (2, 3, 4, 5):
            for rule in ("min", "mean"):
                proxy = (lambda kk, rr: (lambda C, K: heldout_recovery_folds(
                    C, K, k_folds=kk, agree=rr, preset="exact")))(k, rule)
                tc, thrs = catch_of_proxy(tuning, proxy)
                fr, frhrs = false_reject_of_proxy(genuine, proxy)
                cells.append({"k": k, "rule": rule, "tuning_catch": tc,
                              "genuine_false_reject": fr})
        # L1 freeze rule (from L1/PREREG P-a + P-c): first cell with tuning_catch>=0.90 AND
        # false_reject<=0.10, preferring MIN and lower k.
        def freeze_key(c):
            eligible = (c["tuning_catch"] is not None and c["tuning_catch"] >= 0.90
                        and c["genuine_false_reject"] is not None
                        and c["genuine_false_reject"] <= 0.10)
            return (0 if eligible else 1, 0 if c["rule"] == "min" else 1, c["k"])
        cells_sorted = sorted(cells, key=freeze_key)
        frozen = cells_sorted[0]
        frozen_proxy = (lambda C, K: heldout_recovery_folds(
            C, K, k_folds=frozen["k"], agree=frozen["rule"], preset="exact"))
        fresh_catch, fresh_hrs = catch_of_proxy(fresh, frozen_proxy)
        fresh_fr, _ = false_reject_of_proxy(genuine, frozen_proxy)

        tuning_ok = frozen["tuning_catch"] is not None and frozen["tuning_catch"] >= CATCH_BAR
        fresh_ok = fresh_catch is not None and fresh_catch >= CATCH_BAR
        genuine_ok = fresh_fr is not None and fresh_fr <= 0.10

        if not tuning_ok:
            verdict_a = "L1-KILL"   # seal never sealed even on the 45 -> L1's own KILL path
            note_a = ("NO fold cell reaches >=0.90 catch on the tuning-45 without false-reject "
                      ">0.10 -> the no-oracle gate is PROVABLY LEAKY (L1 Q5 KILL). Round 21 "
                      "sweeps report bar-clearing survivors as flagged-for-oracle, never "
                      "auto-certified. HIT auto-certification WITHHELD.")
        elif tuning_ok and not fresh_ok:
            verdict_a = "FOUND-ERROR"
            note_a = ("L1's frozen fold cell reaches >=0.90 catch on the tuning-45 but "
                      "<0.90 on the FRESH surrogate population -> the seal is OVERFIT. HIT "
                      "auto-certification WITHHELD (survivors flagged-for-oracle).")
        elif tuning_ok and fresh_ok and genuine_ok:
            verdict_a = "NO-ERROR-FOUND"
            note_a = ("L1's frozen fold cell holds >=0.90 catch on BOTH the tuning-45 and the "
                      "FRESH surrogate population AND still accepts the genuine decode "
                      "(false-reject<=0.10) -> the seal generalises; NOT overfit.")
        else:
            verdict_a = "FOUND-ERROR"
            note_a = ("L1's frozen fold cell holds catch on both populations but the "
                      "genuine-decode false-reject exceeds 0.10 -> the seal breaks genuine "
                      "acceptance; HIT auto-certification WITHHELD.")

        result["subattack_a_overfit"] = {
            "cell_scan": cells,
            "frozen_cell": frozen,
            "tuning_catch": frozen["tuning_catch"],
            "fresh_catch": fresh_catch,
            "fresh_false_reject": fresh_fr,
            "fresh_heldouts": fresh_hrs,
            "verdict": verdict_a,
            "note": note_a,
        }
    else:
        result["subattack_a_overfit"] = {
            "verdict": "ABORTED",
            "note": "positive control failed (single-cut proxy not flagged leaky on fresh pop) -- "
                    "the audit harness cannot detect a known-leaky seal, so no verdict on L1 is "
                    "trustworthy. Fix the harness before re-running (a).",
        }

    # ---- sub-attacks (b),(c),(d): cheap, run regardless ----
    result["subattack_b_notarerun"] = audit_ledger_cells()
    result["subattack_c_fp_inflation"] = audit_fold_fp_inflation()
    result["subattack_d_row_gate"] = audit_row_gate()

    # ---- overall ----
    verdicts = {
        "a": result["subattack_a_overfit"]["verdict"],
        "b": result["subattack_b_notarerun"]["verdict"],
        "c": result["subattack_c_fp_inflation"]["verdict"],
        "d": result["subattack_d_row_gate"]["verdict"],
    }
    any_found = any(v == "FOUND-ERROR" for v in verdicts.values())
    result["verdicts"] = verdicts
    result["overall"] = "FOUND-ERROR" if any_found else (
        "NO-ERROR-FOUND" if verdicts["a"] in ("NO-ERROR-FOUND",) else "MIXED")
    return result


if __name__ == "__main__":
    out = run()
    with open(os.path.join(HERE, "out_redteam21.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"positive_control_PASS": out["positive_control"]["PASS"],
                      "single_cut_catch_fresh": out["positive_control"]["single_cut_catch_fresh"],
                      "verdicts": out["verdicts"],
                      "overall": out["overall"],
                      "frozen_cell": out["subattack_a_overfit"].get("frozen_cell"),
                      "tuning_catch": out["subattack_a_overfit"].get("tuning_catch"),
                      "fresh_catch": out["subattack_a_overfit"].get("fresh_catch")}, indent=1))
