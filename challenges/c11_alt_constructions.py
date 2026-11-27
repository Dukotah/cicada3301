"""C11 checker: decode through the three constructions that fit LP2's doublet leak as well as the coin does
(CHALLENGES.md, C11; liber-primus/analysis/round48/M1-leak-census/RESULTS.md).

    python challenges/c11_alt_constructions.py --self-test          # the reference beam on every variant
    python challenges/c11_alt_constructions.py my_decoder.py        # your decoder, fresh seed, 12 plants each
    python challenges/c11_alt_constructions.py my_decoder.py --plants 40 --seed <maintainer seed>

Your file defines   decode(C, K, variant) -> {"plain_idx": [int, ...]}   (or a plain list). It runs in an
isolated child process (challenges/_sandbox.py) and is handed only the printed cipher runes C, the CORRECT or a
WRONG key K (you are not told which) and the variant name. Return the plaintext runes you can recover, in order.

Round 48 / M1 showed that the repo's filter model ("redraw a would-be doublet with probability 0.813") is one
of at least four constructions that reproduce LP2's 86 doublets and cannot be told apart at LP2's size. Every
beam here is built for the first. The variants are the other three, as ciphers (decode p = c - k):

  KEYSKIP    control: the construction the reference beam represents.
  V-DELETE   SCORED. Strict filter (a would-be doublet always skips the key symbol), then each cipher rune is
             deleted with probability 0.187. A deleted rune takes its plaintext rune and its key symbol with it.
  V-SILENT   SCORED. The cipher works mod 36: 29 runes + 7 silent symbols. Plaintext is English with symbol 29
             as the word space; the key is uniform on 0..35; c = (p + k) mod 36 under a strict filter over all
             36 symbols; cipher symbols >= 29 are not printed. K holds values 0..35.
  V-TWOLAYER diagnostic. Strict-filtered keyskip cipher, then a second additive shift that jumps to a new value
             with probability 0.186 per rune. The shift is NOT given. Whether this is recoverable at all from
             240 runes is itself an open question; it is reported, not scored.

Plants: ~240 printed runes of English (dev texts; held-out text at review), a fresh key per plant.
"Recoverable" plaintext = the plaintext runes whose cipher symbol was printed. A plant PASSES when
  * LCS(your output, recoverable plaintext) / max(len(output), len(recoverable)) >= 0.85, and
  * the English score of your output under the correct key beats the 95th percentile of the scores of your
    outputs under wrong keys (so a decoder that turns every key into English fails).
A variant PASSES when >= 80 % of its plants pass.

Finish line: both SCORED variants pass at --plants 40 on the maintainers' seed and held-out text, then code
review. Exit 0 = finish line met (or, with --self-test, the keyskip control held).
"""
import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402
import skipdecode as sk  # noqa: E402

N, M, L = H.N, 36, 240
DELTA, Q2 = 0.187, 0.186              # fitted in round48/M1-leak-census/census.py (F2, F3)
MIN_RECOVERY, VARIANT_PASS = 0.85, 0.80
SCORED = ("V-DELETE", "V-SILENT")


def _strict(P, K, mod):
    """Strict filter: skip key symbols until the cipher symbol differs from the previous one."""
    out, j, cp = [], 0, None
    for p in P:
        while (p + K[j]) % mod == cp:
            j += 1
        cp = (p + K[j]) % mod
        out.append(cp)
        j += 1
    return out


def enc_keyskip(P, rng):
    K = H.rand_key(rng, 6 * len(P))
    C_, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=H.EXACT_SUPP, seed=rng.getrandbits(32))
    return C_, K, list(P), 29


def enc_delete(P, rng):
    K = H.rand_key(rng, 6 * len(P))
    A = _strict(P, K, N)
    keep = [rng.random() >= DELTA for _ in A]
    return [c for c, k in zip(A, keep) if k], K, [p for p, k in zip(P, keep) if k], 29


def enc_silent(P36, rng):
    K = [rng.randrange(M) for _ in range(6 * len(P36))]
    A = _strict(P36, K, M)
    return [c for c in A if c < N], K, [p for p, c in zip(P36, A) if c < N and p < N], M


def enc_twolayer(P, rng):
    K = H.rand_key(rng, 6 * len(P))
    A = _strict(P, K, N)
    s, out = rng.randrange(N), []
    for a in A:
        if rng.random() < Q2:
            s = (s + rng.randrange(1, N)) % N
        out.append((a + s) % N)
    return out, K, list(P), 29


VARIANTS = {"KEYSKIP (control)": enc_keyskip, "V-DELETE": enc_delete, "V-SILENT": enc_silent,
            "V-TWOLAYER": enc_twolayer}


def sources(paths):
    sents = H.english_sentences(paths) if paths else H.english_sentences()
    plain = [x for s in sents for w in s for x in w]
    spaced = []
    for s in sents:
        for w in s:
            spaced.extend(w)
            spaced.append(N)                               # symbol 29 = word space
    return plain, spaced


def make_plants(variant, n, seed, plain, spaced):
    rng = random.Random(f"{seed}|{variant}")
    out = []
    for _ in range(n):
        if variant == "V-SILENT":
            ln = int(L * M / N * 1.0)                      # ~240 printed runes after the silent symbols drop
            a = rng.randrange(0, len(spaced) - ln)
            P = spaced[a:a + ln]
        else:
            ln = int(L / (1 - DELTA)) if variant == "V-DELETE" else L
            a = rng.randrange(0, len(plain) - ln)
            P = plain[a:a + ln]
        C_, K, truth, mod = VARIANTS[variant](P, rng)
        WK = [rng.randrange(mod) for _ in K] if mod != N else H.rand_key(rng, len(K))
        out.append((truth, C_, K, WK))
    return out


def lcs(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def summarise(plants, right, wrong):
    ws = sorted(H.english_score(list(w)) if len(w) >= 8 else -99.0 for w in wrong)
    bar = ws[min(len(ws) - 1, int(0.95 * len(ws)))]
    rows = []
    for (truth, C_, K, WK), out in zip(plants, right):
        out = list(out)
        rec = lcs(out, truth) / max(len(out), len(truth), 1)
        sc = H.english_score(out) if len(out) >= 8 else -99.0
        rows.append((rec, sc, rec >= MIN_RECOVERY and sc > bar))
    n, k = len(rows), sum(r[2] for r in rows)
    return {"n": n, "k": k, "rate": k / n, "wilson": H.wilson(k, n), "wrong_bar": bar,
            "mean_recovery": sum(r[0] for r in rows) / n, "median_score": sorted(r[1] for r in rows)[n // 2],
            "detected": sum(r[1] > bar for r in rows) / n, "passed": k / n >= VARIANT_PASS}


def run(decode_many, n, seed, plain, spaced):
    res = {}
    for v in VARIANTS:
        plants = make_plants(v, n, seed, plain, spaced)
        args = [(list(C_), list(K), v) for t, C_, K, WK in plants] + [(list(C_), list(WK), v) for t, C_, K, WK in plants]
        outs = decode_many(args)
        res[v] = summarise(plants, outs[:n], outs[n:])
    return res


def table(name, res):
    print(f"\n{name}")
    print(f"  {'variant':18s} {'plants ok':>10} {'rate':>6} {'Wilson 95%':>14} {'mean rec':>9} {'med score':>10} "
          f"{'wrong-key bar':>14} {'detected':>9}  verdict")
    for v, r in res.items():
        tag = "PASS" if r["passed"] else "fail"
        if v not in SCORED and not v.startswith("KEYSKIP"):
            tag += " (diagnostic)"
        print(f"  {v:18s} {r['k']:>4}/{r['n']:<5} {r['rate']:6.2f} {str(r['wilson']):>14} {r['mean_recovery']:9.3f} "
              f"{r['median_score']:10.3f} {r['wrong_bar']:14.3f} {r['detected']:9.2f}  {tag}")


def ref_many(args):
    """Reference beam (mod 29). On V-SILENT it is handed a mod-36 key and is expected to fail."""
    return [list(sk.beam_decode(C_, [k % N for k in K], sign=-1, o=0, beam_w=400, max_skip=3)["plain_idx"])
            for C_, K, v in args]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining decode(C, K, variant)")
    ap.add_argument("--plants", type=int, default=12, help="plants per variant (scored run: 40)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--text", action="append", help="plaintext source(s) instead of the English dev texts")
    ap.add_argument("--self-test", action="store_true", help="reference beam on every variant (the baseline)")
    a = ap.parse_args()
    seed = H.resolve_seed(a.seed)
    plain, spaced = sources(a.text)
    H.banner("C11 alternative constructions", seed, f"plants/variant={a.plants}  L~{L}")

    if a.self_test or not a.submission:
        t0 = time.time()
        res = run(ref_many, a.plants, seed, plain, spaced)
        table("reference beam (skipdecode.beam_decode, C3 reference)", res)
        ok = res["KEYSKIP (control)"]["passed"]
        print(f"\ncontrol (keyskip, the construction the beam represents) {'held' if ok else 'FAILED'}; "
              f"{time.time() - t0:.0f}s")
        print("SELF-TEST " + ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)

    import _sandbox

    def coerce(i, e):
        return []
    with _sandbox.Sandbox(a.submission, "decode", "plain") as sb:
        res = run(lambda args: sb.map(args, on_error=coerce), a.plants, seed, plain, spaced)
    table(a.submission, res)
    done = all(res[v]["passed"] for v in SCORED)
    print("\nscored variants " + ", ".join(f"{v} {'PASS' if res[v]['passed'] else 'fail'}" for v in SCORED))
    if done and a.plants < 40:
        print("Looks good: re-run with --plants 40 before you submit (the scored run uses 40).")
    print("FINISH LINE MET, pending code review" if done and a.plants >= 40 else "not yet")
    sys.exit(0 if done and a.plants >= 40 else 1)


if __name__ == "__main__":
    main()
