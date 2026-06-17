"""Investigate the doublet deficit and test the autokey hypothesis.

Steps:
  A. SYNTHETIC GROUND TRUTH — encrypt real English with a ciphertext autokey,
     confirm (i) doublet rate ≈ plaintext freq of the K-rune, (ii) our decrypt
     recovers the plaintext. Validates the theory + the implementation.
  B. PREDICTION — compute the plaintext frequency of each rune in English; the
     observed unsolved doublet rate (0.664%) should match some rune's frequency
     if the construction is a ciphertext autokey with that K.
  C. ATTACK — brute every (seed, K, sign, atbash) ciphertext-autokey AND
     plaintext-autokey decryption of the unsolved pages; score with quadgrams.
     If any reads as English we have cracked it; if none does, autokey alone is
     refuted and we report that honestly.

Run: PYTHONUTF8=1 python analysis/doublet_probe.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from lp import gematria as gp, stats, score as _score, autokey  # noqa
from run_stats import load_pages, english_baseline  # reuse loaders

N = gp.N


def doublet_rate(idxs):
    return stats.doublet_rate(idxs)


def section(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def main():
    sc = _score.default()
    eng = english_baseline()
    pages = load_pages()
    unsolved_pages = pages[:-2]
    unsolved = [i for p in unsolved_pages for i in p]
    obs = 100 * doublet_rate(unsolved)

    # ---- A. synthetic validation
    section("A. SYNTHETIC VALIDATION (does the theory + code hold?)")
    for K in (0, 19):  # 0 -> doublets when plaintext==F(0); 19 -> when ==M(19)
        ct = autokey.encrypt_ciphertext_autokey(eng, seed=7, K=K, sign=+1)
        dr = 100 * doublet_rate(ct)
        fK = 100 * (eng.count((-K) % N) / len(eng))
        rec = autokey.decrypt_ciphertext_autokey(ct, seed=7, K=K, sign=+1)
        ok = rec == eng
        print(f"  K={K:2d}: ciphertext doublet%={dr:5.3f}  "
              f"predicted=freq(rune {(-K)%N})={fK:5.3f}  decrypt_recovers={ok}")

    # ---- B. prediction: which plaintext rune has freq ≈ observed doublet rate?
    section("B. PREDICTION — English plaintext rune frequencies vs observed doublet rate")
    freqs = [(i, 100 * eng.count(i) / len(eng)) for i in range(N)]
    print(f"  observed unsolved doublet rate = {obs:.3f}%")
    print("  runes whose English freq is within 0.4% of that:")
    for i, f in sorted(freqs, key=lambda x: abs(x[1] - obs)):
        if abs(f - obs) <= 0.4:
            print(f"    rune {i:2d} '{gp.IDX_TO_TRANS[i]:>2}'  freq={f:.3f}%  "
                  f"=> would need K={(-i) % N}")

    # ---- C. attack
    section("C. ATTACK — brute autokey decryptions of unsolved pages")
    baseline_eng = sc.score_norm(gp.indices_to_translit(eng[:2000]))
    print(f"  reference: real-English score_norm = {baseline_eng:.3f}  "
          f"(unsolved ciphertext as-is = {sc.score_norm(gp.indices_to_translit(unsolved[:2000])):.3f})")

    def brute(decfn, idxs):
        best = None
        for sign in (+1, -1):
            for atb in (False, True):
                for K in range(N):
                    # seed only affects position 0; fix seed=0 (1 rune of slop)
                    p = decfn(idxs, seed=0, K=K, sign=sign, atbash=atb)
                    s = sc.score_norm(gp.indices_to_translit(p))
                    if best is None or s > best[0]:
                        best = (s, sign, atb, K, p)
        return best

    # try whole-corpus and a few individual pages
    targets = [("AGGREGATE", unsolved)] + [
        (f"page{idx}", p) for idx, p in enumerate(unsolved_pages[:6])]
    for kind, decfn in (("ciphertext-autokey", autokey.decrypt_ciphertext_autokey),
                        ("plaintext-autokey", autokey.decrypt_plaintext_autokey)):
        print(f"\n  --- {kind} ---")
        for name, idxs in targets:
            s, sign, atb, K, p = brute(decfn, idxs)
            tx = gp.indices_to_translit(p[:70])
            print(f"  {name:9s} best score={s:6.3f} (sign={sign:+d} atbash={atb} "
                  f"K={K:2d})  {tx}")

    section("INTERPRETATION")
    print("  If any 'best score' approaches the real-English reference "
          f"(~{baseline_eng:.2f}) and reads as words, that construction is the cipher.")
    print("  If all scores stay near the as-is ciphertext baseline, plain autokey "
          "is refuted — the deficit comes from a more complex keyed/seeded stream.")


if __name__ == "__main__":
    main()
