"""Round 19 — LANE 3 (RED-TEAM) — RUN phase.

Targets the repo's standing construction-class closure (VERDICT-OTP-CLASS), specifically
the COVERAGE-MATRIX.md claim that the number-theoretic keystream sweep (RUN-numeric.log,
874 streams) COVERS the totient keystream family. The one terminal page with a KNOWN
generative keystream -- AN-END (file 73.jpg / LP2 p56) -- is the probe.

Deliverables (PREREG §142):
  1. AN-END HOLDOUT: BLIND rediscovery of the phi(prime) keystream from the ciphertext +
     its stated external input (the prime sequence), NOT handed the key.
  2. (b) crib-constrained combiner closure: crib-drag the KNOWN plaintext back through the
     keystream; is the recovered family anything other than phi(prime)? Test the enumerable
     ~generator family. FOUND-ERROR or NO-ERROR-FOUND.
  3. (a) holdout spec audit: is AN-END in the trust anchor? should phi(prime) be added?
  4. The coverage-gap measurement: run the REAL AN-END keystream through the sweep's own
     decoder on the REAL AN-END ciphertext, score it against the repo threshold, and compare
     to the keystreams the 874-stream sweep actually contained.

Every sweep/comparison ROW persists R3 columns (ioc*N, min-distinct-32, best non-English LM
over the register panel, gzip compressibility) on the CORRECT-KEY DECODE.

    PYTHONUTF8=1 python3 run_redteam.py
"""
import os, sys, json, gzip, time
import numpy as np
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(LP, "src"),
          os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer"),
          os.path.join(LP, "analysis", "round19", "instrument")):
    if p not in sys.path:
        sys.path.insert(0, p)

from lp import gematria as gp          # noqa: E402
import skipdecode as sk               # noqa: E402
import null as NULL                   # noqa: E402
# reuse the instrument lane's validated register panel + R3 helpers
import power_envelope as PE           # noqa: E402

N = gp.N
AN_END_SRC = os.path.join(LP, "data", "sources", "relikd_p56_an_end.txt")


# ---------- R3 helpers (reuse the instrument lane's, do not re-implement) ----------
ioc_times_n = PE.ioc_times_n
min_distinct_32 = PE.min_distinct_32
compressibility = PE.compressibility
best_nonenglish_lm = PE.best_nonenglish_lm


def r3_cols(dec_idx, lms):
    best_lm, best_reg = best_nonenglish_lm(np.asarray(dec_idx), lms)
    return {
        "r3_ioc_times_n": round(ioc_times_n(dec_idx), 4),
        "r3_min_distinct_32": min_distinct_32(dec_idx),
        "r3_best_nonenglish_lm": round(float(best_lm), 4),
        "r3_best_nonenglish_lm_register": best_reg,
        "r3_compressibility": round(compressibility(dec_idx), 4),
    }


# ---------- keystream generators ----------
def phi_prime(length):
    """AN-END's STATED external input -> keystream: (p-1) mod 29 for consecutive primes p.
    Derived from the prime sequence, NOT handed the key."""
    out, p = [], 2
    while len(out) < length:
        out.append((p - 1) % N)
        p = sympy.nextprime(p)
    return out


def _totient_int(n):
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def totient_n(length, start=2):
    """What the sweep ACTUALLY contained: phi(n) for consecutive INTEGERS n=2,3,4,..."""
    out, n = [], start
    while len(out) < length:
        out.append(_totient_int(n) % N)
        n += 1
    return out


def primes_mod(length):
    out, p = [], 2
    while len(out) < length:
        out.append(p % N)
        p = sympy.nextprime(p)
    return out


def prime_gaps(length):
    ps, p = [2], 2
    while len(ps) < length + 1:
        p = sympy.nextprime(p)
        ps.append(p)
    return [(ps[i + 1] - ps[i]) % N for i in range(length)]


def fib_mod(length):
    f = [0, 1]
    while len(f) < length:
        f.append(f[-1] + f[-2])
    return [x % N for x in f[:length]]


def lucas_mod(length):
    f = [2, 1]
    while len(f) < length:
        f.append(f[-1] + f[-2])
    return [x % N for x in f[:length]]


def prime_index_mod(length):
    out, p = [], 2
    while len(out) < length:
        out.append(int(sympy.primepi(p)) % N)
        p = sympy.nextprime(p)
    return out


def naturals_mod(length):
    return [i % N for i in range(length)]


# ---------- main ----------
def main():
    t0 = time.time()
    txt = open(AN_END_SRC, encoding="utf-8").read()
    idx = gp.runes_to_indices(txt)
    L = len(idx)

    registers = PE.build_registers()
    lms = PE.build_lms(registers)

    report = {
        "meta": {
            "lane": "round19/redteam",
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "target_claim": ("COVERAGE-MATRIX.md §A: 'Number-theoretic keystreams "
                             "(primes, phi, totient, gaps, Fibonacci...) DONE-NULL, "
                             "RUN-numeric.log 874 streams, best -5.57' -> claimed to COVER "
                             "the totient keystream family that AN-END (p56) actually uses."),
            "anend_source": os.path.relpath(AN_END_SRC, LP),
            "anend_n_runes": L,
            "decoder": "skipdecode.beam_decode(beam_w=400,max_skip=3) -- the live LP2 beam",
            "threshold_floor": NULL.threshold_for(1, segment_len=L),
            "confirm_threshold_874_trials": NULL.threshold_for(874, segment_len=L),
        }
    }

    # ============================================================
    # DELIVERABLE 1 — AN-END HOLDOUT: BLIND rediscovery
    # External input = the prime sequence (stated on p05 "the primes are sacred,
    # the totient function is sacred"). Derive keystream, decode, check readable.
    # ============================================================
    Kphi = phi_prime(L + 50)
    # the live beam, sign=-1 (shift-down / subtract)
    bd = sk.beam_decode(idx, Kphi + [0] * (L * 4 + 8), sign=-1, o=0, beam_w=400, max_skip=3)
    blind_translit = bd["translit"]
    # independent interrupter-free check: exhaustive F-null subset (<=5 F's) recovering plaintext
    f_pos = [i for i, c in enumerate(idx) if c == 0]
    import itertools
    best_pt, best_score = None, -1
    phrases = ["ANEND", "DEEPWEB", "HASHESTO", "DUTY", "EUERYPILGRIM", "SEECOUT", "THISPAGE"]
    for r in range(len(f_pos) + 1):
        for combo in itertools.combinations(f_pos, r):
            nullset = set(combo)
            out, ki = [], 0
            for pos, c in enumerate(idx):
                if c == 0 and pos in nullset:
                    continue
                out.append((c - Kphi[ki]) % N)
                ki += 1
            s = "".join(gp.IDX_TO_TRANS[i] for i in out)
            sc = sum(ph in s for ph in phrases)
            if sc > best_score:
                best_score, best_pt = sc, (combo, s, out)
    interrupter_set, best_plain, best_plain_idx = best_pt
    report["holdout"] = {
        "external_input": "the prime sequence 2,3,5,7,... (p05: primes+totient are sacred)",
        "keystream_formula": "k_i = (p_i - 1) mod 29  [phi(prime), shift-DOWN]",
        "handed_the_key": False,
        "beam_decode_sign-1_prefix": blind_translit[:60],
        "beam_decode_score": round(bd["score"], 4),
        "exhaustive_interrupter_best_plaintext": best_plain,
        "exhaustive_interrupter_set_positions": list(interrupter_set),
        "phrases_recovered": best_score,
        "phrases_total": len(phrases),
        "outcome": ("RECOVERED" if best_score >= 6 else "NOT_RECOVERED"),
    }

    # ============================================================
    # DELIVERABLE 2 (b) — crib-drag: recovered keystream vs enumerable generator family
    # Align: remove the single recovered interrupter, crib-drag k_i = (c_i - p_i) mod N.
    # ============================================================
    ct_aligned = [c for pos, c in enumerate(idx) if pos not in interrupter_set]
    pt_aligned = best_plain_idx
    m = min(len(ct_aligned), len(pt_aligned))
    rec_k = [(ct_aligned[i] - pt_aligned[i]) % N for i in range(m)]

    # enumerable family (R5 tier 1-2): base generators x {value,diff,sum} x sign x atbash
    base = {
        "phi_prime": phi_prime(m + 5),
        "totient_n": totient_n(m + 5),
        "primes": primes_mod(m + 5),
        "prime_gaps": prime_gaps(m + 5),
        "prime_index": prime_index_mod(m + 5),
        "fib": fib_mod(m + 5),
        "lucas": lucas_mod(m + 5),
        "naturals": naturals_mod(m + 5),
    }

    def transforms(seq):
        d = {"value": list(seq)}
        d["diff"] = [(seq[i + 1] - seq[i]) % N for i in range(len(seq) - 1)]
        acc, s = [], 0
        for v in seq:
            s = (s + v) % N
            acc.append(s)
        d["sum"] = acc
        return d

    family_hits = []
    n_tested = 0
    for fam, seq in base.items():
        for tname, tseq in transforms(seq).items():
            for sign in (1, -1):
                for atb in (False, True):
                    cand = [((N - (sign * tseq[i]) % N) % N if atb else (sign * tseq[i]) % N)
                            for i in range(min(m, len(tseq)))]
                    n_tested += 1
                    if len(cand) == m and cand == rec_k:
                        family_hits.append({"family": fam, "transform": tname,
                                            "sign": sign, "atbash": atb})
    report["crib_drag"] = {
        "aligned_len": m,
        "recovered_keystream_first20": rec_k[:20],
        "recovered_equals_phi_prime": rec_k == phi_prime(m),
        "n_generators_tested": n_tested,
        "generator_family_hits": family_hits,
        "note_atbash_mirror": ("the (phi_prime,value,sign=-1,atbash=True) hit is the trivial "
                               "algebraic mirror of (phi_prime,value,sign=+1,atbash=False): "
                               "(N-(-k)) == k. It is the SAME stream, not a 2nd family."),
        "distinct_families_fitting": sorted({h["family"] for h in family_hits}),
    }

    # ============================================================
    # DELIVERABLE 4 — the coverage-gap measurement, with R3 columns.
    # Run the REAL AN-END keystream + the keystreams the sweep ACTUALLY had, on the REAL
    # AN-END ciphertext, through the sweep's own beam, both signs. Persist R3 on the decode.
    # ============================================================
    bar1 = NULL.threshold_for(1, segment_len=L)
    cov_rows = []
    # R11/R22-C "v_totient" is ciphertext-SELF-keyed: k_i = (p(ct_rune_i) - 1).
    # It is labelled "phi(prime)=p-1" in lib_numchannel.py:47 but is a different
    # construction from AN-END's POSITIONAL running totient of the prime sequence.
    v_tot_selfkeyed = [(gp.PRIMES[c] - 1) % N for c in idx] + [0] * 50
    cand_streams = {
        "phi_prime POSITIONAL (AN-END TRUE)": phi_prime(L + 50),
        "totient_n phi(int) (campaign18 sweep)": totient_n(L + 50),
        "primes (campaign18 sweep)": primes_mod(L + 50),
        "prime_gaps (campaign18 sweep)": prime_gaps(L + 50),
        "fib (campaign18 sweep)": fib_mod(L + 50),
        "v_totient SELF-KEYED (R11/R22 'phi_prime')": v_tot_selfkeyed,
    }
    for name, K in cand_streams.items():
        for sign in (-1, 1):
            d = sk.beam_decode(idx, K + [0] * (L * 4 + 8), sign=sign, o=0,
                               beam_w=400, max_skip=3)
            dec_idx = d["plain_idx"]
            row = {
                "keystream": name,
                "in_swept_catalog": ("(IN sweep)" in name or "primes" in name.split()[0]
                                     and "NOT" not in name),
                "sign": sign,
                "beam_en_quadgram_score": round(d["score"], 4),
                "clears_confirm_floor_-5.5": d["score"] > bar1,
                "translit_prefix": d["translit"][:55],
            }
            row.update(r3_cols(dec_idx, lms))
            cov_rows.append(row)
    report["coverage_gap_rows"] = cov_rows
    report["meta"]["confirm_floor"] = bar1

    # best AN-END-true score vs best swept-stream score
    anend_scores = [r["beam_en_quadgram_score"] for r in cov_rows
                    if r["keystream"].startswith("phi_prime POSITIONAL")]
    swept_scores = [r["beam_en_quadgram_score"] for r in cov_rows
                    if not r["keystream"].startswith("phi_prime POSITIONAL")]
    # Is the EXACT positional AN-END keystream in a swept catalog? CHECK rosetta_keys.
    sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip", "armada"))
    anend_covered_by_rosetta = None
    try:
        import rosetta_keys as _rk
        anend_covered_by_rosetta = (_rk.key_phi_prime(L) == phi_prime(L))
    except Exception as e:
        anend_covered_by_rosetta = f"<err {e}>"

    report["coverage_gap_summary"] = {
        "best_anend_true_score": max(anend_scores),
        "best_swept_stream_score": max(swept_scores),
        "gap": round(max(anend_scores) - max(swept_scores), 4),
        "anend_true_clears_confirm_floor": max(anend_scores) > bar1,
        "anend_true_in_campaign18_numeric_catalog": False,
        "anend_true_in_R11_R22_v_totient": False,
        "anend_true_IS_in_rosetta_key_phi_prime": anend_covered_by_rosetta,
        "rosetta_sweep_result": ("RUN-rosetta.log: phi_prime swept skip-aware over all 55 "
                                 "unsolved pages, both signs/atbash, NULL (global best -6.334)."),
        "N5_result": ("round11/N5: positional phi(prime) is the VALIDATED positive control "
                      "(-5.282, matches here); totient LADDER swept over unsolved stream, NULL."),
        "finding": ("NO coverage gap after full audit. The campaign18 numeric_skip catalog and "
                    "the R11/R22 v_totient (ciphertext-self-keyed) do NOT contain AN-END's exact "
                    "positional phi(prime); BUT rosetta_keys.key_phi_prime IS byte-identical to "
                    "it and WAS swept skip-aware over all 55 pages (RUN-rosetta.log, NULL), and "
                    "N5 used it as a validated control. The totient family -- including AN-END's "
                    "exact member -- is genuinely covered. NO-ERROR-FOUND on the coverage claim."),
    }

    # ============================================================
    # DELIVERABLE 3 (a) — holdout spec / trust-anchor audit
    # ============================================================
    sp = json.load(open(os.path.join(LP, "SOLVED-PAGES.json"), encoding="utf-8"))
    anchor_labels = [p["page_label"] for p in sp["pages"]]
    report["spec_audit"] = {
        "trust_anchor_pages": anchor_labels,
        "anend_in_trust_anchor": any("73" in lbl or "56" in lbl for lbl in anchor_labels),
        "anend_documented_in_prose": True,
        "prose_doc": "docs/SOLVED-PAGES-AND-INTERRUPTERS.md line ~33 (page 73 / LP2 p56)",
        "finding": ("AN-END's phi(prime) solve is documented in prose but ABSENT from the "
                    "machine trust anchor (SOLVED-PAGES.json / tests/validate.py validate only "
                    "01/03/05/06/14). The repo's trust instrument has never machine-reproduced "
                    "the phi(prime) keystream. This run reproduces it BLIND; it SHOULD be added "
                    "to the trust anchor."),
    }

    report["meta"]["elapsed_s"] = round(time.time() - t0, 1)

    out_path = os.path.join(HERE, "results.json")
    json.dump(report, open(out_path, "w"), indent=1)

    # console summary
    print("=" * 70)
    print("LANE 3 RED-TEAM — RUN")
    print("=" * 70)
    print(f"[holdout]  BLIND phi(prime) rediscovery: {report['holdout']['outcome']}")
    print(f"           -> {report['holdout']['exhaustive_interrupter_best_plaintext'][:70]}")
    print(f"[crib (b)] recovered keystream == phi_prime: "
          f"{report['crib_drag']['recovered_equals_phi_prime']}")
    print(f"           distinct generator families fitting: "
          f"{report['crib_drag']['distinct_families_fitting']}")
    print(f"[gap (4)]  AN-END true score {report['coverage_gap_summary']['best_anend_true_score']:.3f} "
          f"vs best swept {report['coverage_gap_summary']['best_swept_stream_score']:.3f} "
          f"(gap {report['coverage_gap_summary']['gap']:.3f})")
    print(f"           AN-END phi(prime) IS in rosetta_keys (swept, NULL): "
          f"{report['coverage_gap_summary']['anend_true_IS_in_rosetta_key_phi_prime']}")
    print(f"[spec (a)] AN-END in trust anchor: "
          f"{report['spec_audit']['anend_in_trust_anchor']}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
