"""Round 22 Lane C -- the FOUR literal imperatives (X1, X3, X4) as OPERATIONS.

Reuses, by citation and unchanged:
  round19/I1/driftbeam.py     beam_decode, recovery, PRESETS      (decoder)
  round19/I2/adjudicate.py    adjudicate, panel                   (9-register panel-max)
  round20/P3/panelmax20.py    panelmax_bar                        (the calibrated bar)
  round20/HITFN/hitfn20.py    HitDecode, evaluate, is_hit         (recovery-gated HIT)
  round11/lib_numchannel.py   v_prime/v_prime_index/v_totient, apply_keystream, shuffled

Never -5.5. The recognizer is the panel-max bar + the recovery-gated is_hit.
This module: (Phase 0) plant-and-recover each operation; (Phase 1) sweep LP2 0-54;
(persist) language-agnostic stats per row into ledger.json.
"""
import os
import sys
import json
import random

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(LP, "src"),
           os.path.join(LP, "analysis"),
           os.path.join(LP, "analysis", "round11"),
           os.path.join(LP, "analysis", "round19", "I1"),
           os.path.join(LP, "analysis", "round19", "I2"),
           os.path.join(LP, "analysis", "round20", "P3"),
           os.path.join(LP, "analysis", "round20", "HITFN"),
           os.path.join(LP, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import hitfn20 as HF                       # noqa: E402  (also wires driftbeam/adjudicate/panelmax onto sys.path)
import driftbeam as DB                     # noqa: E402
import adjudicate as AD                    # noqa: E402
import panelmax20 as PM                    # noqa: E402
import lib_numchannel as NC                # noqa: E402
from lp import gematria as gp              # noqa: E402

Nsym = 29
ALPHA = 0.01


# ============================================================ inputs
def lp2_stream():
    """The 12,956-rune unsolved LP2 stream (pages 0-54), flattened."""
    return NC.unsolved()


def known_english(nlen):
    """A known-English rune-index stream of length ~nlen, encoded the way the book does."""
    from run_stats import english_baseline
    e = english_baseline()
    while len(e) < nlen:
        e = e + e
    return e[:nlen]


def solved_key_stream():
    """The in-repo solved plaintext as an English running-key stream (for X3b)."""
    return known_english(4000)


# ============================================================ operations
def decimate(seq, phase, step=4):
    return seq[phase::step]


def interleave4(seq):
    """4-way braid: split into 4 columns by position mod 4, concatenate column-major."""
    cols = [seq[r::4] for r in range(4)]
    return [x for col in cols for x in col]


def deinterleave4(seq):
    """Inverse of interleave4: reconstruct the original read-order from 4 concatenated columns."""
    n = len(seq)
    lens = [len(range(r, n, 4)) for r in range(4)]
    cols, off = [], 0
    for L in lens:
        cols.append(seq[off:off + L]); off += L
    out = [0] * n
    for r in range(4):
        for j, v in enumerate(cols[r]):
            out[r + 4 * j] = v
    return out


def atbash(seq):
    return [(Nsym - 1 - c) % Nsym for c in seq]


def shift(seq, k):
    return [(c + k) % Nsym for c in seq]


def iterate_cipher(seq, op, times):
    s = list(seq)
    for _ in range(times):
        s = op(s)
    return s


# ============================================================ recognizer wrappers
def adj_row(idxs):
    """adjudicate() record with the language-agnostic stats, for a bare rune stream."""
    r = AD.adjudicate(list(idxs))
    return {"n": int(r["n"]), "en": float(r["en"]), "pmax": float(r["pmax"]),
            "preg": AD.panel().registers[int(r["preg"])], "pmax_ne": float(r["pmax_ne"]),
            "pcon": float(r["pcon"]), "ioc": float(r["ioc"]), "mds": int(r["mds"]),
            "h2": float(r["h2"]), "zl": float(r["zl"])}


def structural_bar(n_adj, preset="exact"):
    return float(PM.panelmax_bar(preset=preset, n_round_adjudicated=max(1, n_adj), alpha=ALPHA))


def keyed_hit(C, K, sign=-1, preset="exact", n_adj=10**6, truth=None):
    """Recovery-gated is_hit via hitfn20; returns the full verdict dict."""
    dec = HF.HitDecode(C=list(C), K=list(K), o=0, sign=sign, preset=preset,
                       n_round_adjudicated=max(1, n_adj), alpha=ALPHA,
                       truth_idx=(list(truth) if truth is not None else None))
    v = HF.evaluate(dec)
    return {"hit": bool(v.hit), "pmax": float(v.pmax), "bar": float(v.bar),
            "recovery": float(v.recovery), "heldout": float(v.heldout_recovery),
            "preg": v.preg_name, "score": float(v.score), "reason": v.reason}


# ============================================================ PHASE 0 -- plant & recover
def phase0():
    out = {}

    # ---- X1 control: 4-interleave a known text, de-interleave must recover it exactly ----
    e = known_english(400)
    braided = interleave4(e)
    recon = deinterleave4(braided)
    rec = sum(1 for a, b in zip(recon, e) if a == b) / len(e)
    out["X1_deinterleave_recovers"] = {"recovery": rec, "pass": rec >= 0.999,
                                       "n": len(e)}

    # ---- X3a control: reverse a known text, re-encipher forward with shift k; the X3a
    #      operation (decrypt the reversal by the inverse shift, then un-reverse) recovers it ----
    k = 7
    rev = list(reversed(e))
    ct = shift(rev, k)                          # "encrypt forwards on the reversed stream"
    # X3a recovery: decrypt the reversed cipher (inverse shift), then reverse back
    back = list(reversed(shift(ct, -k)))
    rec3 = sum(1 for a, b in zip(back, e) if a == b) / len(e)
    out["X3a_reversal_recovers"] = {"recovery": rec3, "pass": rec3 >= 0.999, "shift": k}

    # ---- X3b control: plant the solved-key as a genuine running key over a known target,
    #      is_hit must ACCEPT (recovery>=0.90) ----
    key = solved_key_stream()[:len(e)]
    C_x3b = NC.apply_keystream(e, key, sign=+1)          # encipher e with the running key
    v3b = keyed_hit(C_x3b, key, sign=-1, preset="exact", n_adj=len(e), truth=e)
    out["X3b_runningkey_recovers"] = {"is_hit": v3b["hit"], "recovery": v3b["recovery"],
                                      "heldout": v3b["heldout"], "pass": v3b["recovery"] >= 0.90,
                                      "reason": v3b["reason"]}

    # ---- X4 control: encipher a known text with a NUMBER keystream, matching X4 config recovers ----
    ks = [v % Nsym for v in NC.v_totient(e)]             # totient(prime) keystream, mod 29
    C_x4 = NC.apply_keystream(e, ks, sign=+1)            # combine: number transform over letters
    v4 = keyed_hit(C_x4, ks, sign=-1, preset="exact", n_adj=len(e), truth=e)
    out["X4_numberkeystream_recovers"] = {"is_hit": v4["hit"], "recovery": v4["recovery"],
                                          "heldout": v4["heldout"], "pass": v4["recovery"] >= 0.90,
                                          "reason": v4["reason"]}
    return out


# ============================================================ PHASE 1 -- LP2 sweep
def sweep_x1(seq, null=False):
    """X1: 4 decimation phases (+ solved cipher ladder), iterate xN, 4-way (de)interleave."""
    rows = []
    # X1a: every 4th rune, 4 phases, raw + under shift 0..28 + atbash
    for ph in range(4):
        sub = decimate(seq, ph, 4)
        rows.append(("X1a_decim_phase%d_raw" % ph, sub))
        for kk in range(Nsym):
            rows.append(("X1a_decim_phase%d_shift%d" % (ph, kk), shift(sub, kk)))
        rows.append(("X1a_decim_phase%d_atbash" % ph, atbash(sub)))
    # X1b: iterate the cipher N times (atbash^N == atbash for odd, identity even; shift*N)
    for N in (2, 3, 4):
        rows.append(("X1b_atbash_x%d" % N, iterate_cipher(seq, atbash, N)))
        for kk in (1, 3, 7):
            rows.append(("X1b_shift%d_x%d" % (kk, N), iterate_cipher(seq, lambda s: shift(s, kk), N)))
    # X1c: 4-way interleave and de-interleave, both orderings
    rows.append(("X1c_interleave4", interleave4(seq)))
    rows.append(("X1c_deinterleave4", deinterleave4(seq)))
    return score_structural(rows)


def sweep_x3(seq, solved_key, null=False):
    """X3: (a) reversal re-enciphered forward; (b) solved-key running-key inversion."""
    struct_rows = []
    rev = list(reversed(seq))
    struct_rows.append(("X3a_reversed_raw", rev))
    for kk in range(Nsym):
        struct_rows.append(("X3a_reversed_shift%d" % kk, shift(rev, kk)))
    struct_rows.append(("X3a_reversed_atbash", atbash(rev)))
    struct = score_structural(struct_rows)

    # X3b keyed: solved plaintext as running key over the unsolved stream (both signs),
    # and the inverted role (unsolved as key over the solved cipher, on the solved-page length).
    keyed = []
    K = (solved_key * (len(seq) // len(solved_key) + 1))[:len(seq)]
    for sign in (-1, +1):
        v = keyed_hit(seq, K, sign=sign, preset="exact", n_adj=len(seq))
        keyed.append({"op": "X3b_solvedkey_running_sign%d" % sign, **v})
        vd = keyed_hit(seq, K, sign=sign, preset="drift", n_adj=len(seq))
        keyed.append({"op": "X3b_solvedkey_running_sign%d_drift" % sign, **vd})
    return {"structural": struct, "keyed": keyed}


def sweep_x4(seq, null=False):
    """X4: number transform of the stream as a KEYSTREAM over the letter stream."""
    keyed = []
    transforms = {"v_prime": NC.v_prime, "v_prime_index": NC.v_prime_index,
                  "v_totient": NC.v_totient}
    for tname, tf in transforms.items():
        base_ks = [v % Nsym for v in tf(seq)]
        variants = {"none": seq, "atbash_pre": atbash(seq)}
        for vname, letters in variants.items():
            for sign in (-1, +1):
                v = keyed_hit(letters, base_ks, sign=sign, preset="exact", n_adj=len(seq))
                keyed.append({"op": "X4_%s_%s_sign%d" % (tname, vname, sign),
                              "letter_twin_pmax": adj_row(seq)["pmax"], **v})
    return {"keyed": keyed}


def score_structural(named_streams):
    rows = []
    n_adj = len(named_streams)
    for name, s in named_streams:
        r = adj_row(s)
        r["op"] = name
        r["bar"] = structural_bar(n_adj)
        r["clears_null"] = r["pmax"] >= r["bar"]
        rows.append(r)
    return rows


# ============================================================ main
def main():
    random.seed(3301)
    seq = lp2_stream()
    solved_key = solved_key_stream()
    result = {"lane": "R22-C-literal-imperatives", "n_lp2": len(seq),
              "recognizer": {"bar": "panelmax20.panelmax_bar (never -5.5)",
                             "hit": "hitfn20.is_hit (recovery-gated 3-clause)",
                             "registers": AD.panel().registers}}

    print("== PHASE 0: plant-and-recover ==")
    result["phase0"] = phase0()
    for k, v in result["phase0"].items():
        print("  %-32s %s" % (k, v))

    print("== PHASE 1: LP2 sweep (real) ==")
    result["X1"] = {"real": sweep_x1(seq)}
    result["X3"] = {"real": sweep_x3(seq, solved_key)}
    result["X4"] = {"real": sweep_x4(seq)}

    print("== PHASE 1: size-matched null (seed 3301 shuffle) ==")
    nseq = NC.shuffled(seq, seed=3301)
    result["X1"]["null"] = sweep_x1(nseq, null=True)
    result["X3"]["null"] = sweep_x3(nseq, solved_key, null=True)
    result["X4"]["null"] = sweep_x4(nseq, null=True)

    # ---- summarize survivors ----
    survivors = []

    def scan_struct(rows, lane):
        for r in rows:
            if r.get("clears_null"):
                survivors.append({"lane": lane, "op": r["op"], "pmax": r["pmax"],
                                  "bar": r["bar"], "preg": r["preg"], "kind": "structural"})

    def scan_keyed(rows, lane):
        for r in rows:
            if r.get("hit"):
                survivors.append({"lane": lane, "op": r["op"], "pmax": r["pmax"],
                                  "recovery": r["recovery"], "heldout": r["heldout"],
                                  "preg": r["preg"], "kind": "keyed_is_hit"})

    scan_struct(result["X1"]["real"], "X1")
    scan_struct(result["X3"]["real"]["structural"], "X3a")
    scan_keyed(result["X3"]["real"]["keyed"], "X3b")
    scan_keyed(result["X4"]["real"]["keyed"], "X4")
    result["survivors"] = survivors

    # ---- coverage & best-of stats ----
    def best(rows, key):
        return max((r[key] for r in rows if key in r), default=None)
    result["coverage"] = {
        "X1_ops": len(result["X1"]["real"]),
        "X3a_struct_ops": len(result["X3"]["real"]["structural"]),
        "X3b_keyed_ops": len(result["X3"]["real"]["keyed"]),
        "X4_keyed_ops": len(result["X4"]["real"]["keyed"]),
        "best_pmax_X1": best(result["X1"]["real"], "pmax"),
        "best_pmax_X3a": best(result["X3"]["real"]["structural"], "pmax"),
        "best_recovery_X3b": best(result["X3"]["real"]["keyed"], "recovery"),
        "best_recovery_X4": best(result["X4"]["real"]["keyed"], "recovery"),
        "best_pmax_X4": best(result["X4"]["real"]["keyed"], "pmax"),
    }
    result["coverage"]["total_ops"] = (result["coverage"]["X1_ops"]
                                       + result["coverage"]["X3a_struct_ops"]
                                       + result["coverage"]["X3b_keyed_ops"]
                                       + result["coverage"]["X4_keyed_ops"])

    with open(os.path.join(HERE, "ledger.json"), "w") as f:
        json.dump(result, f, indent=1, default=float)

    print("\n== SUMMARY ==")
    print(json.dumps(result["coverage"], indent=1, default=float))
    print("survivors (is_hit / bar-clearing):", len(survivors))
    for s in survivors:
        print("  SURVIVOR:", s)
    print("ledger -> ledger.json")


if __name__ == "__main__":
    main()
