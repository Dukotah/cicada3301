"""Crib-dragging attack that RECOVERS an arbitrary fixed feedback function.

Blind sweeps are the wrong weapon against an autokey cipher; the right one is a
known-plaintext crib. Key idea (works for ANY cipher of the form
c[i] = p[i] + K(p[i-1]) with K a FIXED but unknown 29->29 table -- i.e. any
fixed single-rune-history autokey, not just prime/totient):

  Assume a crib p[0..m-1] at a page start. Each step gives one equation
      K(p[i-1]) = (c[i] - p[i]) mod 29.
  If the crib is correct, all equations sharing the same p[i-1] must agree ->
  a CONSISTENT partial table K. A wrong crib almost always yields a CONTRADICTION
  (same previous rune demanding two different key values). So we can test cribs
  WITHOUT knowing K, recover K where the crib determines it, then extend the
  decrypt and score it. Contradiction-rate is itself the filter.

Also sweeps: subtract/add sign, atbash on ciphertext, and crib offset (0..6) in
case of a decorated/interrupter lead rune.
Reproduce: PYTHONUTF8=1 python analysis/crib_autokey.py
"""
import os, sys
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp
from lp import score as _score

N = 29
SC = _score.default()

# Known Cicada plaintext openers / high-frequency words (crib candidates).
CRIBS = ["AKOAN", "ANINSTRUCTION", "ANEND", "AWARNING", "PARABLE", "SOMEWISDOM",
         "WELCOME", "THELOSSOFDIVINITY", "THEPRIMESARESACRED", "ANINSTAR",
         "THEBOOK", "PILGRIM", "AQUESTION", "ACOMMAND", "THETOTIENT", "DONOT",
         "THECIRCUMFERENCE", "WITHIN", "THEDEEPWEB", "BELIEVENOTHING",
         "THEUNIVERSE", "CONSUME", "REALITY", "ENLIGHTENMENT"]

def load_pages():
    segs = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read().split("%")
    out = []
    for s in segs:
        ix = gp.runes_to_indices(s)
        if ix:
            out.append(ix)
    return out[:-2]

def crib_ix(word):
    return gp.keyword_to_indices(word)

def try_crib(cix, crib, sign):
    """Return (consistent?, K_table, contradictions). K derived from crib on cix."""
    m = len(crib)
    if m > len(cix):
        return False, None, 99
    K = {}
    contra = 0
    for i in range(1, m):
        prev = crib[i - 1]
        kv = (cix[i] - crib[i]) % N if sign > 0 else (crib[i] - cix[i]) % N
        if prev in K and K[prev] != kv:
            contra += 1
        else:
            K[prev] = kv
    return contra == 0, K, contra

def extend(cix, crib, K, sign):
    """Decrypt as far as K determines; stop at first unknown previous rune."""
    pt = list(crib)
    for i in range(len(crib), len(cix)):
        prev = pt[i - 1]
        if prev not in K:
            break
        p = (cix[i] - K[prev]) % N if sign > 0 else (K[prev] - cix[i]) % N
        # careful: for sign<0 the encrypt/decrypt symmetry differs; use additive convention
        p = (cix[i] - K[prev]) % N
        pt.append(p)
    return pt

def main():
    pages = load_pages()
    print(f"crib-dragging fixed-function autokey over {len(pages)} pages, "
          f"{len(CRIBS)} cribs\n")
    hits = []
    for pi, page in enumerate(pages):
        for atb in (False, True):
            cix = [(N - 1 - c) for c in page] if atb else page
            for w in CRIBS:
                crib = crib_ix(w)
                if len(crib) < 4:
                    continue
                for off in range(0, 7):
                    if off + len(crib) > len(cix):
                        continue
                    seg = cix[off:]
                    for sign in (+1, -1):
                        ok, K, contra = try_crib(seg, crib, sign)
                        if ok and len(K) >= 4:
                            pt = extend(seg, crib, K, sign)
                            if len(pt) >= len(crib) + 6:  # extended beyond crib
                                sc = SC.score_norm(gp.indices_to_translit(pt))
                                hits.append((sc, pi, w, off, atb, sign, len(pt),
                                             gp.indices_to_translit(pt)[:60]))
    hits.sort(reverse=True)
    print("top consistent-crib extensions (score_norm; English ~ -2.2, noise < -4):")
    for h in hits[:12]:
        sc, pi, w, off, atb, sign, ln, head = h
        print(f"  {sc:6.2f}  p{pi:<2} crib={w:<14} off{off} atb={int(atb)} "
              f"s{sign:+d} len{ln}  {head}")
    if not hits:
        print("  no crib produced a consistent extendable table -> fixed-function")
        print("  single-history autokey with these openers is refuted.")
    else:
        best = hits[0]
        print(f"\n  best {best[0]:.2f} vs English ~ -2.2 / noise ~ -4.5")
        print("  A real break sits near -2.2; anything < -4 is noise (no break).")

if __name__ == "__main__":
    main()
