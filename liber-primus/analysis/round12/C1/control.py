"""POSITIVE CONTROL for FRONT C1.

Plant a k-history-feedback ciphertext (encipher known English under a given
f/k/source/sign) and confirm:
  (1) the CORRECT (f,k,source,sign,seed) recovers the plaintext -> English score
  (2) WRONG f/source produce noise (negative control)
This gates the real sweep. Uses the project's canonical score_norm scale.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import feedback as fb

PLAIN = (
    "THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
    "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
    "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
    "SACRED GEOMETRY OF THE CIRCUMFERENCE AND LOSE THE SELF TO GAIN THE WHOLE"
)

def eng_to_idx(text):
    # reuse skipdecode's greedy mapping via gematria _TRANS_SORTED
    from lp import gematria as gp
    s = text.upper()
    out, i, n = [], 0, len(s)
    ALIAS = {"V": 1, "K": 5, "Z": 15, "Q": 5}
    while i < n:
        for t, idx in gp._TRANS_SORTED:
            if s.startswith(t, i):
                out.append(idx); i += len(t); break
        else:
            a = ALIAS.get(s[i])
            if a is not None:
                out.append(a)
            i += 1
    return out


def run():
    P = eng_to_idx(PLAIN)
    truth = fb.idx_to_trans(P)
    print("plaintext runes:", len(P))
    print("TRUTH:", truth[:70])
    print("=" * 72)
    allpass = True
    for source in fb.SOURCES:
        for fname, f in fb.F_BASIS.items():
            k = 3
            seed = [7, 11, 2][:k]
            sign = -1
            C = fb.encipher(P, f, k, seed, source=source, sign=sign)
            # sanity: ciphertext should differ from plaintext
            # correct recovery
            Prec = fb.decode(C, f, k, seed, source=source, sign=sign)
            sc = fb.score_norm(Prec)
            match = sum(a == b for a, b in zip(Prec, P)) / len(P)
            # wrong f (different function), same k/source
            wrong_fname = "xor" if fname != "xor" else "sum"
            Pw = fb.decode(C, fb.F_BASIS[wrong_fname], k, seed, source=source, sign=sign)
            scw = fb.score_norm(Pw)
            ok = match > 0.99 and sc > -5.0 and scw < -6.0
            allpass = allpass and ok
            print(f"src={source:3s} f={fname:16s} k={k} : recover match={match*100:5.1f}% "
                  f"score={sc:6.3f} | wrong-f({wrong_fname}) score={scw:6.3f}  "
                  f"{'OK' if ok else 'XX'}")
    print("=" * 72)
    print("CONTROL:", "PASS -- planted feedback ciphers are recoverable, wrong-f stays noise"
          if allpass else "FAIL")
    return allpass


if __name__ == "__main__":
    run()
