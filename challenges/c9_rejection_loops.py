"""C9 checker: recover plaintext through null insertion, a rejection loop no beam here can read (CHALLENGES.md, C9).

    python challenges/c9_rejection_loops.py --self-test                 # reference beams on the sealed variants
    python challenges/c9_rejection_loops.py my_decoder.py               # your decoder, fresh seed
    python challenges/c9_rejection_loops.py my_decoder.py --plants 40 --seed <maintainer seed>   # the scored run

Your file defines   decode(C, K, sign=-1) -> {"plain_idx": [int], ...}   exactly as for C3. It runs in an
isolated child process (challenges/_sandbox.py): it is handed (C, K, sign) one call at a time, in a random
order, and returns only plain_idx. The checker recomputes the English score itself.

beam_v3 represents keyskip1, keyskip2 and a 'free' relation: all MONOTONE in the key pointer, each cipher rune
from exactly one plaintext rune (ledger L7-B-BEAM-ENVELOPE). The variants:

  V-NULL   SCORED. Null insertion: on a would-be doublet, with probability supp, the encipherer emits a null
           rune (uniform, different from the previous rune) and discards the rejected key symbol, then retries
           with the next one. Because the discarded symbol is used up, the key still advances once per cipher
           rune, so beams stay in sync; unlike the solved pages' interrupters it does not shift the key. The
           beams already score the correct key as English (-4.54): this is a RECOVERY gap (every null leaves a
           junk rune; positional recovery 0.17), and crossing it changes no detection negative.
  V-BACK   diagnostic since R47-H2. Backstep: on a would-be doublet the pointer steps BACK one place (j -= 1)
           with probability supp and retries. Both beams score the correct key as noise (0/40), so no
           beam-based negative covers it; but one added backstep relation recovers 32/40 (R47-X1, dev seed).
           That gap is closable in-house and is scheduled for Round 48 (re-adjudicate the beam negatives with a
           backstep-aware beam). It is reported, not scored.
  V-DEFER  diagnostic: the rejected key symbol is held back and used for the next rune (beams already 39/40).

All variants reproduce LP2's lag-1 (0.66 %) and lag-2 (3.40 %) repeat rates at this supp.

Plants: 240-rune English windows (dev texts; held-out text at review), a fresh SHA-256-counter key per plant,
supp = the filter strength that reproduces LP2's 0.664 % doublet rate, sign -1, key offset 0 (the C3 setting).
A plant PASSES when rune-index recovery >= 0.85 and the recomputed English score >= -5.2, AND the same
ciphertext under an independent wrong key scores <= -6.0. A variant PASSES when >= 80 % of its plants pass
and wrong-key false positives are <= 5 %.

Finish line: C3 7/7 AND V-NULL passes at --plants 40 on the maintainers' seed and held-out text, then code
review. Exit 0 = finish line met (or, with --self-test, the self-test's own controls held).
"""
import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402
import _common as C  # noqa: E402
import skipdecode as sk  # noqa: E402

N = H.N
L = 240
ENGLISH, NOISE_CEIL, MIN_RECOVERY = -5.2, -6.0, 0.85       # benchmark/gates.py constants
VARIANT_PASS, WRONG_FP_MAX = 0.80, 0.05
SCORED = ("V-NULL",)       # R47-H2: V-BACK is diagnostic (closable in-house, R47-X1 32/40; Round 48)


# ------------------------------------------------------------------ the rejection loops (decode p = c - k)
def enc_keyskip(P, K, supp, rng):
    """Control: the construction the reference beam represents (skipdecode.encipher_keyskip, sign -1)."""
    C_, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=supp, seed=rng.getrandbits(32))
    return C_


def enc_backstep(P, K, supp, rng):
    out, j, cp = [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % N
            if cp is not None and c == cp and j > 0 and rng.random() < supp:
                j -= 1
                continue
            break
        out.append(c)
        cp = c
        j += 1
    return out


def enc_null(P, K, supp, rng):
    """Null + discard (PREREG Addendum 1): emitting the rejected value after the null would put every null
    between two equal runes (lag-2 repeat 6.0 % vs LP2's 3.40 %), which LP2 already excludes."""
    out, j, cp = [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                z = rng.randrange(N - 1)
                z = z + 1 if z >= cp else z                # null != previous rune; consumes no key
                out.append(z)
                cp = z
                j += 1                                     # the rejected key symbol is discarded
                continue
            break
        out.append(c)
        cp = c
        j += 1
    return out


def enc_defer(P, K, supp, rng):
    out, j, cp, held = [], 0, None, None
    for p in P:
        pend = None
        while True:
            if held is not None:
                idx, held = held, None
            else:
                idx, j = j, j + 1
            c = (p + K[idx]) % N
            if cp is not None and c == cp and rng.random() < supp:
                if pend is None:
                    pend = idx
                continue
            break
        out.append(c)
        cp = c
        held = pend
    return out


VARIANTS = {"KEYSKIP (control)": enc_keyskip, "V-BACK": enc_backstep, "V-NULL": enc_null, "V-DEFER": enc_defer}


# ------------------------------------------------------------------ reference decoders
def ref_beam(C_, K, sign=-1):
    return sk.beam_decode(C_, K, sign=sign, o=0, beam_w=400, max_skip=3)


_B3 = None


def v3_best(C_, K, sign=-1):
    """beam_v3 (panel-R36, panel_max) under advance 1, 2 and 'free'; returns the decode with the best
    recomputed English score (the checker's own adjudication)."""
    global _B3
    if _B3 is None:
        sys.path.insert(0, os.path.join(C.LP, "analysis", "round33", "I1-register-aware-beam"))
        import beam_v3
        beam_v3.set_panel(H.PANEL_PATH)
        _B3 = beam_v3
    best = None
    for adv in (1, 2, "free"):
        d = _B3.beam_decode_v3(list(C_), K, adv, "panel_max", sign=sign)
        s = H.english_score(d["plain_idx"])
        if best is None or s > best[0]:
            best = (s, d)
    return best[1]


# ------------------------------------------------------------------ run
def make_plants(variant, n, seed, text_stream):
    rng = random.Random(f"{seed}|{variant}")
    enc = VARIANTS[variant]
    out = []
    for _ in range(n):
        a = rng.randrange(0, len(text_stream) - L)
        P = text_stream[a:a + L]
        K = H.rand_key(rng, 6 * L)
        WK = H.rand_key(rng, 6 * L)
        out.append((P, enc(P, K, H.EXACT_SUPP, rng), K, WK))
    return out


def recovery(plain_idx, P):
    return sum(1 for a, b in zip(plain_idx, P) if a == b) / len(P)


def evaluate(decode, plants, many=None):
    """decode(C, K, sign) in-process (reference beams), or many(list of (C, K, sign)) -> list of plain_idx
    (a submission in the isolated child; see run())."""
    many = many or (lambda args: [list(decode(*x)["plain_idx"]) for x in args])
    outs = many([(list(C_), list(K), -1) for P, C_, K, WK in plants] + [(list(C_), list(WK), -1) for P, C_, K, WK in plants])
    return summarise(plants, outs[:len(plants)], outs[len(plants):])


def summarise(plants, right, wrong):
    rows = []
    for (P, C_, K, WK), pi, pw in zip(plants, right, wrong):
        pi = list(pi)
        rec, sc, sw = recovery(pi, P), H.english_score(pi), H.english_score(list(pw))
        rows.append({"recovery": rec, "score": sc, "wrong": sw,
                     "pass": rec >= MIN_RECOVERY and sc >= ENGLISH, "wrong_fp": sw > NOISE_CEIL})
    n = len(rows)
    k = sum(r["pass"] for r in rows)
    fp = sum(r["wrong_fp"] for r in rows)
    return {"n": n, "k": k, "rate": k / n, "wilson": H.wilson(k, n), "wrong_fp": fp / n,
            "mean_recovery": sum(r["recovery"] for r in rows) / n,
            "median_score": sorted(r["score"] for r in rows)[n // 2],
            "passed": k / n >= VARIANT_PASS and fp / n <= WRONG_FP_MAX}


def table(name, res):
    print(f"\n{name}")
    print(f"  {'variant':18s} {'plants ok':>10} {'rate':>6} {'Wilson 95%':>14} {'mean rec':>9} {'med score':>10} {'wrong FP':>9}  verdict")
    for v, r in res.items():
        print(f"  {v:18s} {r['k']:>4}/{r['n']:<5} {r['rate']:6.2f} {str(r['wilson']):>14} {r['mean_recovery']:9.3f} "
              f"{r['median_score']:10.3f} {r['wrong_fp']:9.2f}  {'PASS' if r['passed'] else 'fail'}")


def run(decode, n, seed, text_stream, variants, sb=None):
    """In-process for the reference beams; for a submission (sb = _sandbox.Sandbox) every call of every
    variant goes through ONE shuffled call list, so neither the variant nor right-vs-wrong key is in the order."""
    plants = {v: make_plants(v, n, seed, text_stream) for v in variants}
    if sb is None:
        return {v: evaluate(decode, plants[v]) for v in variants}
    args = []
    for v in variants:
        args += [(list(C_), list(K), -1) for P, C_, K, WK in plants[v]]
        args += [(list(C_), list(WK), -1) for P, C_, K, WK in plants[v]]
    outs = sb.map(args)
    res, i = {}, 0
    for v in variants:
        m = len(plants[v])
        res[v] = summarise(plants[v], outs[i:i + m], outs[i + m:i + 2 * m])
        i += 2 * m
    return res


def sandboxed_decoder(sb):
    """C3-gate adapter: the gates get a decode whose score/translit the CHECKER computes from plain_idx."""
    def decode(C_, K, sign=-1):
        pi = sb.call(list(C_), list(K), sign)
        return {"plain_idx": pi, "score": H.english_score(pi), "translit": sk.idx_to_trans(pi)}
    return decode


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining decode(C, K, sign=-1)")
    ap.add_argument("--plants", type=int, default=12, help="plants per variant (scored run: 40)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--text", action="append", help="plaintext source(s) instead of the English dev texts")
    ap.add_argument("--no-gates", action="store_true", help="skip the C3 gates (iteration only; not valid for a claim)")
    ap.add_argument("--self-test", action="store_true", help="reference beams on every variant (the baseline)")
    ap.add_argument("--v3", action="store_true", help="with --self-test: also run beam_v3 (3 relations)")
    a = ap.parse_args()
    seed = H.resolve_seed(a.seed)
    stream = H.english_stream(a.text) if a.text else H.english_stream()
    H.banner("C9 second rejection-loop decoder", seed, f"plants/variant={a.plants}  L={L}")

    if a.self_test or not a.submission:
        t0 = time.time()
        res = run(ref_beam, a.plants, seed, stream, list(VARIANTS))
        table("reference beam (skipdecode.beam_decode, C3 reference)", res)
        ok = res["KEYSKIP (control)"]["passed"]
        if a.v3:
            res3 = run(v3_best, a.plants, seed, stream, list(VARIANTS))
            table("beam_v3 panel_max, best of advance 1 / 2 / free (panel-R36)", res3)
            ok = ok and res3["KEYSKIP (control)"]["passed"]
        print(f"\ncontrol (keyskip, the construction the beam represents) {'held' if ok else 'FAILED'}; "
              f"{time.time() - t0:.0f}s")
        print("SELF-TEST " + ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)

    import _sandbox
    with _sandbox.Sandbox(a.submission, "decode", "plain") as sb:
        gates_ok = True
        if not a.no_gates:
            import gates
            print("\nC3 gates (submission in an isolated child process):")
            rows = gates.run_all(decoder=sandboxed_decoder(sb), verbose=True)
            gates_ok = all(r["passed"] for r in rows)
        res = run(None, a.plants, seed, stream, list(VARIANTS), sb=sb)
    table(a.submission, res)
    scored = all(res[v]["passed"] for v in SCORED)
    done = gates_ok and scored and not a.no_gates
    print(f"\nC3 gates {'7/7' if gates_ok else 'NOT qualified'}; scored variants "
          + ", ".join(f"{v} {'PASS' if res[v]['passed'] else 'fail'}" for v in SCORED))
    if done and a.plants < 40:
        print("Looks good: re-run with --plants 40 before you submit (the scored run uses 40).")
    print("FINISH LINE MET, pending code review" if done and a.plants >= 40 else "not yet")
    sys.exit(0 if done and a.plants >= 40 else 1)


if __name__ == "__main__":
    main()
