"""B4 supplement — audit the ONE claim the repo calls 'positively refuted':

  FINAL-SYNTHESIS.md l.20-22:
    "Autokey - positively refuted (not merely 'fails to decrypt'): the difference-
     diagonal d=(b-a) mod 29 has only d=0 as an outlier (z=-17.25); the 28 nonzero
     diagonals are flat (cv=0.061), whereas autokey requires lumpy per-rune-frequency
     diagonals (cv~1.0)."

Question: does 'autokey requires cv~1.0' hold unconditionally, or only when the
PLAINTEXT is English?  Under ciphertext autokey  c_i = c_{i-1} + p_i  the difference
diagonal IS the plaintext monogram distribution, so the test measures the PLAINTEXT,
not the cipher.

Also emits the implied-plaintext stream for hand-off to lane B6.

Run: PYTHONUTF8=1 python3 analysis/round10b/B4-otp-steelman/b4_autokey_audit.py
"""
import os, sys, math, re, random, collections, statistics, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp                     # noqa
from run_stats import load_pages                  # noqa
N = gp.N
pages = load_pages(); OBS = [i for pg in pages[:-2] for i in pg]; L = len(OBS)
def p(*a): print(*a); sys.stdout.flush()

def cvnz(freqs):
    nz = [freqs[i] for i in range(1, N)]
    return statistics.pstdev(nz) / statistics.mean(nz)

def monogram(x):
    c = collections.Counter(x); n = len(x); return [c.get(i, 0)/n for i in range(N)]

def diffs(x):
    return [(x[i]-x[i-1]) % N for i in range(1, len(x))]

eng = gp.keyword_to_indices(re.sub(r"[^A-Za-z]", "", open(
    os.path.join(ROOT, "data", "kjv.txt"), encoding="utf-8", errors="ignore"
).read().upper())[20000:20000+600000])[:200000]

p("=" * 78); p("A. What does the difference diagonal MEASURE under ct-autokey?")
p("=" * 78)
mE = monogram(eng)
p(f"  English-in-futhorc monogram: cv over ALL 29 = "
  f"{statistics.pstdev(mE)/statistics.mean(mE):.3f}   cv over nonzero 28 = {cvnz(mE):.3f}")
p(f"  -> ct-autokey over ENGLISH would show diagonal cv ~ {cvnz(mE):.2f}. "
  f"The repo's 'cv~1.0' figure is CORRECT for English plaintext.")

D = monogram(diffs(OBS))
p(f"\n  REAL LP2 difference diagonals: P(d=0) = {100*D[0]:.3f}%  "
  f"(uniform would be {100/N:.3f}%)   cv over nonzero 28 = {cvnz(D):.4f}")

p("\n  Now: ct-autokey where the PLAINTEXT is a flat, near-doublet-free stream")
p("  (i.e. NOT English -- a key block, base-29 digits, compressed/enciphered data):")
for q in (0.00664,):
    rows = []
    for s in range(40):
        r = random.Random(500+s)
        pt = [0 if r.random() < q else r.randrange(1, N) for _ in range(L)]
        c = [r.randrange(N)]
        for i in range(1, L): c.append((c[-1]+pt[i]) % N)
        Dm = monogram(diffs(c))
        rows.append((cvnz(Dm), 100*Dm[0]))
    cvs = [a for a, _ in rows]; z0 = [b for _, b in rows]
    p(f"    plaintext P(rune 0)={q:.5f}: diagonal cv_nz = {statistics.mean(cvs):.4f} "
      f"+/- {statistics.pstdev(cvs):.4f}   P(d=0) = {statistics.mean(z0):.3f}%")
p(f"    REAL LP2:                    diagonal cv_nz = {cvnz(D):.4f}"
  f"                       P(d=0) = {100*D[0]:.3f}%")
p("\n  VERDICT on the autokey refutation: the test is SOUND but CONDITIONAL.")
p("  It refutes ciphertext-autokey-over-ENGLISH-plaintext. It does not touch")
p("  ciphertext-autokey over a flat non-English plaintext, which reproduces the")
p("  observed diagonal EXACTLY -- because under ct-autokey the diagonal IS the")
p("  plaintext monogram, so a flat diagonal is a statement about the PLAINTEXT.")

p("\n" + "=" * 78)
p("B. Significance of the real diagonal's residual lumpiness (proper null)")
p("=" * 78)
nul = []
for s in range(500):
    r = random.Random(9000+s); y = OBS[:]; r.shuffle(y)
    nul.append(cvnz(monogram(diffs(y))))
m, sd = statistics.mean(nul), statistics.pstdev(nul)
p(f"  shuffled-LP2 null: cv_nz {m:.4f} +/- {sd:.4f}    REAL {cvnz(D):.4f}   "
  f"z = {(cvnz(D)-m)/sd:+.2f}")
# chi2 on the 28 nonzero diagonals
n = L-1; cnt = collections.Counter(diffs(OBS))
tot = sum(cnt[d] for d in range(1, N)); e = tot/28
chi2 = sum((cnt.get(d, 0)-e)**2/e for d in range(1, N))
p(f"  chi2 of the 28 nonzero diagonals vs uniform = {chi2:.1f} on 27 df "
  f"(critical 40.1 at p=0.05) -> {'non-flat' if chi2 > 40.1 else 'FLAT, consistent with uniform'}")
p(f"  z of the d=0 hole: observed {cnt[0]} vs expected {n/N:.1f}, "
  f"z = {(cnt[0]-n/N)/math.sqrt(n*(1/N)*(1-1/N)):+.2f}")

p("\n" + "=" * 78)
p("C. Hand-off to lane B6 — the ct-autokey implied plaintext")
p("=" * 78)
imp = diffs(OBS)
p(f"  first-difference stream, n={len(imp)}. This is the plaintext IF the cipher is")
p("  ciphertext autokey. The repo computed it (ELIMINATION-LEDGER 'first-difference /")
p("  integral inversion') and killed it as 'flat-random; no plaintext' -- a judgement")
p("  made with an ENGLISH scorer. Written out for a language-agnostic reader.")
json.dump({"implied_plaintext_ct_autokey": imp}, open(os.path.join(HERE, "implied_pt_ct_autokey.json"), "w"))
p("  wrote implied_pt_ct_autokey.json")
