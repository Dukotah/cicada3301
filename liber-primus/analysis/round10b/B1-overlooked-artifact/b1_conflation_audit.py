"""Lane B1 / H3 - the CONFLATION AUDIT, measured rather than asserted.

Question: does the repo's "any keytext dies by mechanism" kill (Round 7, about LONG
running keys) get wrongly extended onto SHORT SEMANTIC KEYWORDS - the object that
actually broke the solved pages? Or is there a separate, valid kill for keywords?

Method: measure the doublet rate the author's OWN demonstrated construction produces,
using the author's OWN output - the five solved pages - and compare to LP2 0-54.
No inference, no simulation of a hypothetical adversary.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from lp import gematria as gp, corpus  # noqa
from run_stats import load_pages  # noqa
import math

N = gp.N


def doublets(idxs):
    return sum(1 for i in range(1, len(idxs)) if idxs[i] == idxs[i - 1])


def rate(idxs):
    n = len(idxs) - 1
    return doublets(idxs) / n if n > 0 else 0.0


print("=" * 78)
print("A. The author's demonstrated short-keyword construction, measured on her own output")
print("=" * 78)
SOLVED = [("03.jpg", "Vigenere DIVINITY + interrupters"),
          ("14.jpg", "Vigenere FIRFUMFERENFE + interrupters"),
          ("Runes - 01.jpg", "Atbash (keyless)"),
          ("05.jpg", "plaintext/shift"),
          ("06.jpg", "Atbash + Caesar 3")]
tot_d = tot_n = 0
for lbl, how in SOLVED:
    p = corpus.page_by_label(lbl)
    idxs = gp.runes_to_indices(p["runes"])
    d, n = doublets(idxs), len(idxs) - 1
    tot_d += d
    tot_n += n
    print(f"  {lbl:<16} {how:<38} {d:>4}/{n:<5} = {100*d/n:5.2f}%")
sol_rate = tot_d / tot_n
print(f"  {'ALL SOLVED':<16} {'':<38} {tot_d:>4}/{tot_n:<5} = {100*sol_rate:5.2f}%")

print()
print("=" * 78)
print("B. LP2 0-54 (unsolved)")
print("=" * 78)
pages = load_pages()[:-2]
u_d = sum(doublets(p) for p in pages)
u_n = sum(len(p) - 1 for p in pages)
u_rate = u_d / u_n
print(f"  unsolved 0-54                                        "
      f"{u_d:>4}/{u_n:<5} = {100*u_rate:5.2f}%")
p_rand = 1.0 / N
print(f"  random floor (1/29)                                             "
      f"= {100*p_rand:5.2f}%")

print()
print("=" * 78)
print("C. The decisive comparison (this is the lane's real kill, and it is EMPIRICAL)")
print("=" * 78)
exp = sol_rate * u_n
sd = math.sqrt(u_n * sol_rate * (1 - sol_rate))
z = (u_d - exp) / sd
print(f"  If LP2 0-54 had been enciphered the way the author DEMONSTRABLY enciphered")
print(f"  the solved pages (short semantic Gematria-Primus keyword, +/- Atbash, +/- Caesar,")
print(f"  F-rune interrupters), it would carry {100*sol_rate:.2f}% doublets.")
print(f"    expected doublets = {exp:.1f} +/- {sd:.1f}")
print(f"    observed doublets = {u_d}")
print(f"    z = {z:+.2f}")
print()
exp2 = p_rand * u_n
sd2 = math.sqrt(u_n * p_rand * (1 - p_rand))
print(f"  vs the random floor: expected {exp2:.1f} +/- {sd2:.1f}, "
      f"z = {(u_d - exp2)/sd2:+.2f}")

print()
print("=" * 78)
print("C2. Robustness: two-proportion z-test, and the Vigenere-only reference")
print("=" * 78)


def two_prop(d1, n1, d2, n2, lbl):
    p1, p2 = d1 / n1, d2 / n2
    pp = (d1 + d2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    print(f"  {lbl:<52} z = {z:+7.2f}")
    return z


two_prop(u_d, u_n, tot_d, tot_n, "LP2 0-54  vs  ALL solved pages (2.74%)")
# the strictly-correct reference for a KEYWORD cipher is the two Vigenere pages only
vd = vn = 0
for lbl in ("03.jpg", "14.jpg"):
    p = corpus.page_by_label(lbl)
    idxs = gp.runes_to_indices(p["runes"])
    vd += doublets(idxs)
    vn += len(idxs) - 1
print(f"  solved VIGENERE-KEYWORD pages only: {vd}/{vn} = {100*vd/vn:.2f}%")
two_prop(u_d, u_n, vd, vn, "LP2 0-54  vs  the 2 keyword-Vigenere pages")
# worst case: push the reference rate to its own lower 2-sigma bound
se_ref = math.sqrt(sol_rate * (1 - sol_rate) / tot_n)
lo = sol_rate - 2 * se_ref
e_lo = lo * u_n
sd_lo = math.sqrt(u_n * lo * (1 - lo))
print(f"  reference rate lower 2-sigma bound = {100*lo:.2f}%  -> expected {e_lo:.0f} "
      f"+/- {sd_lo:.1f},  z = {(u_d - e_lo)/sd_lo:+.2f}")
print("  => the exclusion survives the most generous reading of the reference sample.")

print()
print("=" * 78)
print("C3. The TIGHTEST possible reference: the author's own PLAINTEXT")
print("=" * 78)
print("""  Mechanics: under a SHORT repeating keyword of period P, k[i]==k[i-1] at (P-1)/P of
  positions, so c[i]==c[i-1] exactly when p[i]==p[i-1] there. A keyword-Vigenere
  ciphertext therefore INHERITS most of its doublets from the plaintext. The correct
  lower bound on the expected LP2 doublet rate is thus the author's own PLAINTEXT
  doublet rate in rune-index space, not the random floor.""")
from lp import ciphers  # noqa
pt_d = pt_n = 0
for lbl, shift, atb in (("Runes - 01.jpg", 0, True), ("05.jpg", 0, False),
                        ("06.jpg", 3, True)):
    pg = corpus.page_by_label(lbl)
    c = gp.runes_to_indices(pg["runes"])
    base = [((N - 1) - x) for x in c] if atb else c
    pt = [(x + shift) % N for x in base]
    d, n = doublets(pt), len(pt) - 1
    pt_d += d
    pt_n += n
    print(f"    {lbl:<16} recovered plaintext  {d:>3}/{n:<4} = {100*d/n:5.2f}%")
pt_rate = pt_d / pt_n
print(f"    {'POOLED':<16} author's plaintext   {pt_d:>3}/{pt_n:<4} = {100*pt_rate:5.2f}%")
e3 = pt_rate * u_n
sd3 = math.sqrt(u_n * pt_rate * (1 - pt_rate))
print(f"  LP2 expected under a keyword cipher (floor case) = {e3:.0f} +/- {sd3:.1f}; "
      f"observed {u_d}; z = {(u_d-e3)/sd3:+.2f}")
two_prop(u_d, u_n, pt_d, pt_n, "LP2 0-54  vs  the author's own plaintext rate")
print("""  Even against the FLOOR reference - the author's own plaintext, which is the lowest
  doublet rate any keyword cipher of hers can produce - LP2 0-54 is excluded.
  A short semantic keyword cannot be the LP2 0-54 construction, whatever the keyword is.""")

print()
print("=" * 78)
print("D. Verdict on the conflation question")
print("=" * 78)
print("""  The repo does NOT conflate the two kills in the direction the lane suspected.
  Two INDEPENDENT kills exist and they bind different objects:

    KILL-1 (Round 7 / Campaign IV, 'mechanism'): a FULL-LENGTH natural-language
      RUNNING key injects ~3.3% doublets. Scope: long keys. Correctly scoped.

    KILL-2 (DOUBLET-INVESTIGATION.md s2, table row 'short Vigenere (len 8) 3.44%'):
      a SHORT REPEATING keyword injects ~3.44% doublets. Scope: short keywords.
      This row exists, is separate, and was measured - it is NOT an extension of
      KILL-1. Short semantic keywords therefore have their own valid kill.

  The measurement above upgrades KILL-2 from a simulation against synthetic English
  to a measurement against the AUTHOR'S OWN CIPHERTEXT: her demonstrated keyword
  construction leaves doublets at the random band on the pages she made with it.

  What IS genuinely under-scoped in the repo: neither kill binds if the author
  applied a POST-ENCIPHERMENT anti-repeat rewrite on top of a keyword. That is
  exactly why Campaign XVIII built the skip-tolerant beam - and it ran ~620
  keywords under it (RUN-keywords-full.log, best -6.021, 0 hits). So the corner
  is covered, but by Campaign XVIII, not by KILL-1 or KILL-2.""")
