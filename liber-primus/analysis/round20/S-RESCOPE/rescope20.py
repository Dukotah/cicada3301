"""S-RESCOPE -- re-adjudicate the B-04 stored survivors through the REPAIRED Round-20 instrument.

NOT new key space. Re-scores the keys Round-13 B-04 stored (the English-argmax of a measured
6.2M-decode sweep) through I1 driftbeam (keyskip1 `exact` + repaired `drift` channel) -> I2 panel
-> P3 panel-max null -> HITFN recovery-gated is_hit. Score alone is never a hit.

Mandatory positive control FIRST (plant a B-04-generator key, recover it rank-1 + is_hit through
the full pipeline) before any null is trusted. Also a negative control (EN_NOVOWEL hallucination
must be is_hit->False). Emits SWEEPROW/3 rows with the recovery field per defect (d).

Run:  python3 rescope20.py
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

import driftbeam as DB          # noqa: E402  I1 repaired beam
import adjudicate as AD         # noqa: E402  I2 nine-register panel + SWEEPROW
import panelmax20 as PM         # noqa: E402  P3 panel-max bar
import hitfn20 as H             # noqa: E402  recovery-gated gate
import plants as PL3            # noqa: E402  I3 register plaintext streams
import skipdecode as sk         # noqa: E402  encipher_keyskip (for the plant)
import ks                       # noqa: E402  B-04 keystream generators
import lib_numchannel as nc     # noqa: E402  the LP2 ciphertext

B04 = os.path.join(LP, "analysis", "round13", "B04")
PAYLOAD_RESOLVED = os.path.join(LP, "analysis", "round19", "C1", "payload_resolved.bin")

# The two decode relations we carry (SYNTHESIS: keyskip1 for its clean bar, drift_rec for
# transcription robustness). Each survivor is adjudicated under BOTH.
PRESETS = ["exact", "drift"]
N_CANON = 10 ** 6               # canonical bar N per HITFN doctrine (conservative 7.634 / 13.842)


# --------------------------------------------------------------------------- key reconstruction
def reconstruct_key(row, nsym):
    """Rebuild the keystream a stored B-04 survivor row encodes: gen+red over seed bytes,
    reversed if dir=='rev'. Returns the Z_29 key list of length >= nsym."""
    seed = bytes.fromhex(row["seed_hex"])
    base = ks.make_ks(row["gen"], row["red"], seed, nsym)
    return base[::-1] if row.get("dir") == "rev" else base


def atbash29(C):
    return [(28 - x) for x in C]


def survivor_ciphertext(row, C_unsolved):
    """Apply the row's atbash flag to the target ciphertext (the row's own segment is the
    unsolved head/full; we re-adjudicate on the unsolved stream, atbash'd per the row)."""
    return atbash29(C_unsolved) if row.get("atbash") == 1 else list(C_unsolved)


# --------------------------------------------------------------------------- load survivors
def load_survivors():
    """Every stored survivor row that carries full key params (Stage A/B/C top-50 + Stage-D)."""
    rows = []
    for stage, fn in (("A", "results_A.json"), ("B", "results_B.json"), ("C", "results_C.json")):
        d = json.load(open(os.path.join(B04, fn), encoding="utf-8"))
        for r in d["top50"]:
            r = dict(r); r["_stage"] = stage; rows.append(r)
    # Stage D deepenings (page0_full + unsolved_full)
    dD = json.load(open(os.path.join(B04, "results_D.json"), encoding="utf-8"))
    for e in dD:
        for r in e.get("top50", []):
            if "seed_hex" in r and "gen" in r:
                r = dict(r); r["_stage"] = "D:" + e["stage"]; rows.append(r)
    return rows


# --------------------------------------------------------------------------- adjudicate one row
def adjudicate_row(row, C_target, L, preset):
    """Re-decode one survivor key on C_target[:L] with the repaired beam+preset, adjudicate,
    and gate through is_hit. Returns the measured dict (no plaintext oracle -> real-mode gate)."""
    C = survivor_ciphertext(row, C_target)[:L]
    K = reconstruct_key(row, L * 4 + 512)
    sign = int(row.get("sign", -1))
    off = int(row.get("offset", 0))
    dec = H.HitDecode(C=C, K=list(K), o=off, sign=sign, preset=preset,
                      n_round_adjudicated=N_CANON, alpha=0.01)
    v = H.evaluate(dec)
    return v


# --------------------------------------------------------------------------- POSITIVE CONTROL
def positive_control(C_unsolved, L=240):
    """Plant a B-04-generator key over REAL English plaintext via the keyskip relation, drop it
    into the survivor pile, and require: (a) rank-1 by pmax among the pile, (b) is_hit -> True."""
    panels = PL3._panels()
    stream = panels["EN_MODERN"]
    rng = random.Random(3301)
    # a real B-04 generator (sha256_ctr + mod29), a real seed
    seed = b"CICADA"
    Kfull = ks.make_ks("sha256_ctr", "mod29", seed, L * 4 + 1024)
    # plant real English plaintext, enciphered under the keyskip relation the instrument targets
    s = rng.randrange(0, len(stream) - L - 1)
    P = list(stream[s:s + L])
    C, _nsk, _ = sk.encipher_keyskip(P, Kfull, sign=-1, supp=0.83, seed=3301)

    # is_hit on the plant, strict (truth supplied) AND real-mode (held-out proxy)
    strict = H.HitDecode(C=C, K=list(Kfull), o=0, sign=-1, preset="exact",
                         n_round_adjudicated=N_CANON, truth_idx=P)
    vs = H.evaluate(strict)
    real = H.HitDecode(C=C, K=list(Kfull), o=0, sign=-1, preset="exact",
                       n_round_adjudicated=N_CANON)
    vr = H.evaluate(real)

    # rank-1 test: does the planted key out-pmax the survivor keys decoded on the SAME planted C?
    survivors = load_survivors()
    rng.shuffle(survivors)
    plant_pmax = vs.pmax
    beaten = 0
    checked = 0
    for row in survivors[:60]:            # a representative sample (time-boxed) of wrong keys on C
        try:
            K = reconstruct_key(row, L * 4 + 512)
            d = DB.beam_decode(list(C), list(K), sign=int(row.get("sign", -1)),
                               o=int(row.get("offset", 0)), beam_w=400, **DB.PRESETS["exact"])
            a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
            checked += 1
            if float(a["pmax"]) >= plant_pmax:
                beaten += 1
        except Exception:
            continue
    rank1 = (beaten == 0)

    # NEGATIVE control: an EN_NOVOWEL hallucination that clears the bar on pmax but recovers < 0.90
    neg = negative_control(Kfull, panels, L)

    return {
        "generator": "sha256_ctr+mod29", "seed": seed.decode(), "L": L,
        "plant_pmax": float(vs.pmax), "bar_exact_1e6": float(vs.bar),
        "true_recovery": float(vs.recovery), "heldout_recovery_realmode": float(vr.heldout_recovery),
        "is_hit_strict": bool(vs.hit), "is_hit_realmode": bool(vr.hit),
        "preg": vs.preg_name,
        "rank1_among_wrong_keys": rank1, "wrong_keys_checked": checked, "wrong_keys_beating_plant": beaten,
        "negative_control": neg,
        "PASS": bool(vs.hit and vr.hit and rank1 and neg["rejected"]),
    }


def negative_control(Kfull, panels, L):
    """A vowel-dropped-English decode that clears the panel-max bar on pmax but recovers < 0.90 --
    the EN_NOVOWEL hallucination. is_hit MUST reject it (both strict and real mode)."""
    stream = panels["EN_NOVOWEL"]
    bar = PM.panelmax_bar("exact", N_CANON, 0.01)
    for rep in range(40):
        rng = random.Random(5000 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _n, _ = sk.encipher_keyskip(P, Kfull, sign=-1, supp=0.83, seed=600 + rep)
        d = DB.beam_decode(C, list(Kfull), sign=-1, o=0, beam_w=400, **DB.PRESETS["exact"])
        a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
        rec = DB.recovery(d["plain_idx"], P)
        if float(a["pmax"]) >= bar and rec < 0.90:
            strict = H.HitDecode(C=C, K=list(Kfull), o=0, sign=-1, preset="exact",
                                 n_round_adjudicated=N_CANON, truth_idx=P)
            real = H.HitDecode(C=C, K=list(Kfull), o=0, sign=-1, preset="exact",
                               n_round_adjudicated=N_CANON)
            vs, vr = H.evaluate(strict), H.evaluate(real)
            return {"found": True, "pmax": float(a["pmax"]), "true_recovery": float(rec),
                    "heldout_recovery": float(vr.heldout_recovery),
                    "is_hit_strict": bool(vs.hit), "is_hit_realmode": bool(vr.hit),
                    # the gate PROVES hallucination-rejection in STRICT mode (truth available on
                    # controls). real-mode held-out is a weaker proxy (see out_heldout_proxy_audit)
                    # -- we gate the CONTROL on strict rejection, which is the proven property.
                    "rejected": bool(not vs.hit),
                    "rejected_realmode": bool(not vr.hit)}
    return {"found": False, "rejected": False}


def heldout_proxy_audit(L=240, n=60):
    """RED-TEAM audit of the HITFN real-mode held-out proxy on THIS lane's target relation.
    For each EN_NOVOWEL hallucination (pmax>=bar, TRUE recovery<0.90 -- the decodes score alone
    would certify), measure whether the deployable real-mode held-out proxy catches it. Strict
    mode (truth) always catches; the question is how leaky the no-oracle proxy is. This is the
    exact leak that matters when adjudicating a REAL survivor: no truth is available, so the gate
    IS the held-out proxy."""
    panels = PL3._panels()
    stream = panels["EN_NOVOWEL"]
    Kfull = ks.make_ks("sha256_ctr", "mod29", b"CICADA", L * 4 + 1024)
    bar = PM.panelmax_bar("exact", N_CANON, 0.01)
    n_halluc = caught = missed = 0
    heldouts = []
    for rep in range(n):
        rng = random.Random(5000 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _n, _ = sk.encipher_keyskip(P, Kfull, sign=-1, supp=0.83, seed=600 + rep)
        d = DB.beam_decode(C, list(Kfull), sign=-1, o=0, beam_w=400, **DB.PRESETS["exact"])
        a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
        rec = DB.recovery(d["plain_idx"], P)
        if float(a["pmax"]) >= bar and rec < 0.90:
            n_halluc += 1
            real = H.HitDecode(C=C, K=list(Kfull), o=0, sign=-1, preset="exact",
                               n_round_adjudicated=N_CANON)
            vr = H.evaluate(real)
            heldouts.append(round(float(vr.heldout_recovery), 3))
            if vr.hit:
                missed += 1
            else:
                caught += 1
    return {"n_en_novowel_hallucinations": n_halluc,
            "realmode_proxy_caught": caught, "realmode_proxy_MISSED": missed,
            "realmode_catch_rate": (caught / n_halluc) if n_halluc else None,
            "strict_mode_catch_rate": 1.0 if n_halluc else None,
            "heldout_recoveries_of_hallucinations": heldouts,
            "finding": ("The HITFN real-mode held-out self-consistency proxy is LEAKY on this "
                        "lane's keyskip relation: it catches only %d/%d EN_NOVOWEL hallucinations "
                        "(the rest reproduce their own wrong decode consistently on the held-out "
                        "3/4). STRICT mode (truth) catches 100%%. On a REAL survivor no truth "
                        "exists, so a survivor clearing the bar cannot be certified a HIT on the "
                        "real-mode proxy alone -- clears_null is reported, is_hit is NOT trusted "
                        "as a solve without strict recovery. This RE-OPENS red-team defect (d) at "
                        "the deployable operating point." % (caught, n_halluc))}


# --------------------------------------------------------------------------- MAIN SWEEP
def run(L=240):
    C_unsolved = nc.unsolved()

    # ---- 0. RED-TEAM: audit the deployable held-out proxy on this relation ----
    proxy_audit = heldout_proxy_audit(L=L)
    json.dump(proxy_audit, open(os.path.join(HERE, "out_heldout_proxy_audit.json"), "w"), indent=1)

    # ---- 1. POSITIVE + NEGATIVE control (MANDATORY, gates everything) ----
    pc = positive_control(C_unsolved, L=L)
    json.dump(pc, open(os.path.join(HERE, "out_poscontrol.json"), "w"), indent=1)
    if not pc["PASS"]:
        return {"aborted": True, "reason": "positive/negative control failed -- instrument not "
                "trusted; a null here would be from an unvalidated instrument (doctrine)",
                "poscontrol": pc}

    # ---- 2. re-adjudicate the stored survivors on the canonical unsolved head ----
    survivors = load_survivors()
    hdr = H.header_v3("S-RESCOPE-B04-survivors", dec_preset="exact", n_round_adjudicated=N_CANON,
                      L=L, target="LP2 unsolved head", note="re-adjudicating Round-13 B-04 stored "
                      "English-argmax survivors through repaired I1/I2/P3 + recovery gate")
    rows_out = []
    per_reg_clears = {}
    per_reg_total = {}
    n_hit = 0
    best = {"pmax": -99, "row": None, "preset": None, "recovery": None}
    for row in survivors:
        for preset in PRESETS:
            try:
                v = adjudicate_row(row, C_unsolved, L, preset)
            except Exception as ex:
                continue
            per_reg_total[v.preg_name] = per_reg_total.get(v.preg_name, 0) + 1
            if v.clears_null:
                per_reg_clears[v.preg_name] = per_reg_clears.get(v.preg_name, 0) + 1
            if v.hit:
                n_hit += 1
            if v.pmax > best["pmax"]:
                best = {"pmax": float(v.pmax), "row": {k: row[k] for k in
                        ("_stage", "seed", "gen", "red", "sign", "atbash", "dir", "offset", "score")},
                        "preset": preset, "recovery": float(v.recovery),
                        "heldout": float(v.heldout_recovery), "bar": float(v.bar),
                        "preg": v.preg_name, "clears_null": bool(v.clears_null), "is_hit": bool(v.hit)}
            rows_out.append({"stage": row["_stage"], "gen": row["gen"], "red": row["red"],
                             "dir": row.get("dir"), "atbash": row.get("atbash"),
                             "sign": row.get("sign"), "preset": preset,
                             "orig_score": row.get("score"), "pmax": round(float(v.pmax), 4),
                             "bar": round(float(v.bar), 4), "clears_null": bool(v.clears_null),
                             "recovery": round(float(v.recovery), 4),
                             "heldout_recovery": round(float(v.heldout_recovery), 4),
                             "preg": v.preg_name, "score": round(float(v.score), 4),
                             "is_hit": bool(v.hit)})

    with open(os.path.join(HERE, "out_survivors.jsonl"), "w") as f:
        f.write(json.dumps({"header": hdr}) + "\n")
        for r in rows_out:
            f.write(json.dumps(r) + "\n")

    # ---- 3. re-seed the B-04 slice from payload_resolved.bin (3 changed bytes idx 45,50,246) ----
    reseed = reseed_payload_resolved()

    n_rows = len(rows_out)
    summary = {
        "aborted": False,
        "poscontrol_PASS": pc["PASS"],
        "poscontrol": {k: pc[k] for k in ("is_hit_strict", "is_hit_realmode", "rank1_among_wrong_keys",
                                          "plant_pmax", "bar_exact_1e6", "true_recovery",
                                          "wrong_keys_checked", "wrong_keys_beating_plant")},
        "negative_control": pc["negative_control"],
        "heldout_proxy_audit": proxy_audit,
        "n_survivor_keys": len(survivors),
        "n_adjudications": n_rows,
        "presets": PRESETS,
        "L": L,
        "n_is_hit": n_hit,
        "any_hit": n_hit > 0,
        "best_survivor": best,
        "clears_null_by_register": {k: [per_reg_clears.get(k, 0), per_reg_total.get(k, 0)]
                                    for k in sorted(per_reg_total)},
        "n_clears_null_total": sum(per_reg_clears.values()),
        "payload_resolved_reseed": reseed,
        "coverage_note": ("150 stored survivor keys (Stage A/B/C top-50 + Stage-D) re-adjudicated "
                          "under 2 presets = %d adjudications. This is the RECOVERABLE fraction of "
                          "the ~1,312 repo-wide English-argmax rows R1 D-iii names; the rest were "
                          "either not stored with keys (R17 partial) or fall in the coverage HOLE "
                          "R1 D-iii proves: B-04's -6.412 cutoff excluded any true skip_by_two key "
                          "(scores -6.718, 0.31 below), so those keys were NEVER stored and cannot "
                          "be re-adjudicated here." % n_rows),
    }
    json.dump(summary, open(os.path.join(HERE, "out_rescope.json"), "w"), indent=1, default=float)
    return summary


def reseed_payload_resolved():
    """Re-seed the B-04 slice from payload_resolved.bin: use its 32 bytes as a seed into the B-04
    generators, re-adjudicate on the unsolved head. (The 3 changed bytes idx 45,50,246 change the
    resolved payload; this checks whether the resolved-canon seed produces any hit that the old
    canon seed missed.) Bounded: a handful of generator/reduction combos on the resolved seed."""
    if not os.path.exists(PAYLOAD_RESOLVED):
        return {"skipped": True, "reason": "payload_resolved.bin not found"}
    payload = open(PAYLOAD_RESOLVED, "rb").read()
    C_unsolved = nc.unsolved()
    L = 240
    results = []
    n_hit = 0
    # seed the generators with the resolved payload (and a few slices of it)
    seeds = {"full256": payload, "first32": payload[:32], "first16": payload[:16]}
    gens = ["sha256_ctr", "sha512_ctr", "hmac_drbg_sha256", "aes_ctr_zeroiv"]
    reds = ["mod29", "rej29"]
    for sname, seed in seeds.items():
        for g in gens:
            if g not in ks.GENERATORS:
                continue
            for rd in reds:
                for sign in (-1, 1):
                    for preset in PRESETS:
                        try:
                            K = ks.make_ks(g, rd, seed, L * 4 + 512)
                            dec = H.HitDecode(C=list(C_unsolved)[:L], K=list(K), o=0, sign=sign,
                                              preset=preset, n_round_adjudicated=N_CANON)
                            v = H.evaluate(dec)
                        except Exception:
                            continue
                        if v.hit:
                            n_hit += 1
                        results.append({"seed": sname, "gen": g, "red": rd, "sign": sign,
                                        "preset": preset, "pmax": round(float(v.pmax), 4),
                                        "bar": round(float(v.bar), 4),
                                        "clears_null": bool(v.clears_null),
                                        "recovery": round(float(v.recovery), 4),
                                        "is_hit": bool(v.hit)})
    best = max(results, key=lambda r: r["pmax"]) if results else None
    return {"skipped": False, "sha256_payload": __import__("hashlib").sha256(payload).hexdigest(),
            "n_adjudications": len(results), "n_is_hit": n_hit, "any_hit": n_hit > 0,
            "best": best, "changed_bytes": [45, 50, 246]}


if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1, default=float)[:4000])
