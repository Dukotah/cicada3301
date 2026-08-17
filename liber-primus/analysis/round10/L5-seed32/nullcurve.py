"""L5-seed32 — how the seed-sweep score's best-of-N grows under the null, and whether
the pre-registered -12.5 decision threshold survives a COMPLETED full-32 sweep.

Why this is the load-bearing test of the lane
---------------------------------------------
Round 8 fixed its hit threshold at -12.5 on the 48-rune window after measuring a null
maximum of -13.13 across 2.52e9 decodes (the 2011-2015 unix-second slice, 10 generators).
The full 32-bit space is 34x larger PER GENERATOR. Best-of-N under a null grows like
mu + beta*ln(N), so a threshold calibrated at one N is not a threshold at another N.
If the null max at the completed sweep's N reaches -12.5, then "hits>-12.5=0" is a
statement about a rule that no longer separates signal from noise, and any decode that
did cross it would be an expected null event rather than a lead.

Estimators (reported separately, never silently blended)
--------------------------------------------------------
  E1  SAME-N MLE on this lane's 2^26-seed chunk maxima for generator 0 on the real
      ciphertext. ~20 iid maxima at one N, one generator: the cleanest beta available,
      with no generator-to-generator confound.
  E2  the same fit on the SHUFFLED-ciphertext null control (the mandated null).
  E3  ACROSS-N slope from Round 8's own logs: mean best over 10 generators at
      N=2.52e8 vs mean best over 2 generators at N=8.59e9. Two points, 34x apart.
E1 and E3 measure the same beta by completely different routes. Agreement is evidence
the Gumbel model is right; disagreement is reported, and the LARGER beta is used for the
threshold arithmetic because a larger beta makes false positives MORE likely (conservative).

Run:  python3 nullcurve.py
"""
import math
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SS = os.path.normpath(os.path.join(HERE, '..', '..', 'seed_sweep'))
EULER = 0.5772156649015329


# ----------------------------------------------------------------- data loading
def read_sweeplog(path):
    out = []
    if not os.path.exists(path):
        return out
    for ln in open(path, encoding='utf-8'):
        m = re.search(r'seeds=(\d+)\.\.(\d+)\s+best=([-0-9.]+)', ln)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            out.append(((hi - lo) * 2, float(m.group(3))))   # x2 = both directions
    return out


def read_chunks(path):
    rows, seen = [], set()
    if not os.path.exists(path):
        return rows
    for ln in open(path, encoding='utf-8'):
        f = ln.rstrip('\n').split('\t')
        if len(f) < 7 or f[0] == 'gen':
            continue
        try:
            g, lo, hi, best = f[0], int(f[1]), int(f[2]), float(f[3])
        except ValueError:
            continue
        if (g, lo, hi) in seen:          # a resumed/overlapping run can repeat a chunk
            continue
        seen.add((g, lo, hi))
        rows.append(((hi - lo) * 2, best))
    return rows


# ------------------------------------------------------------------ Gumbel MLE
def gumbel_mle(xs_raw):
    """MLE for Gumbel(mu, beta) from iid maxima all taken at the same N.

    Data are centred before fitting; exp(-x/beta) overflows otherwise for
    x ~ -13 and small beta. The shift is added back into mu at the end.
    """
    n = len(xs_raw)
    shift = sum(xs_raw) / n
    xs = [x - shift for x in xs_raw]
    var = sum(x * x for x in xs) / max(1, n - 1)
    beta = max(1e-3, math.sqrt(6 * var) / math.pi)
    # MLE fixed point:  beta = mean(x) - sum(x e^{-x/beta}) / sum(e^{-x/beta})
    # (mean(x) == 0 after centring). Damped, with an exp-argument clamp.
    for _ in range(2000):
        m = max(-x / beta for x in xs)
        w = [math.exp(min(700.0, -x / beta - m)) for x in xs]
        sw = sum(w)
        num = sum(x * wi for x, wi in zip(xs, w))
        beta_new = max(1e-4, -num / sw)
        if abs(beta_new - beta) < 1e-12:
            beta = beta_new
            break
        beta = 0.5 * beta + 0.5 * beta_new
    m = max(-x / beta for x in xs)
    lse = m + math.log(sum(math.exp(min(700.0, -x / beta - m)) for x in xs) / n)
    mu = -beta * lse + shift
    return mu, beta


def boot_beta(xs, B=2000, seed=7):
    rng = random.Random(seed)
    bs = []
    for _ in range(B):
        samp = [xs[rng.randrange(len(xs))] for _ in xs]
        try:
            bs.append(gumbel_mle(samp)[1])
        except Exception:
            pass
    bs.sort()
    return bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs))]


def emax(mu, beta, N_ref, N):
    return mu + beta * math.log(N / N_ref) + beta * EULER


def p_exceed(mu, beta, N_ref, N, t):
    z = (t - (mu + beta * math.log(N / N_ref))) / beta
    return 1.0 - math.exp(-math.exp(-z))


# ------------------------------------------------------------------------ main
def main():
    ts = read_sweeplog(os.path.join(SS, 'results_timeseed.txt'))
    f32 = read_sweeplog(os.path.join(SS, 'results_full32.txt'))
    real = read_chunks(os.path.join(HERE, 'chunks_real.tsv'))
    shuf = read_chunks(os.path.join(HERE, 'chunks_shufa.tsv'))

    print('=' * 74)
    print('INPUT max-of-N samples')
    print('=' * 74)
    for tag, s in (('Round 8 time-seed (10 gens)', ts),
                   ('Round 8 full-32 (2 gens)', f32),
                   ('L5 gen0 chunks, REAL ct', real),
                   ('L5 gen0 chunks, SHUFFLED ct (null)', shuf)):
        if s:
            b = [x[1] for x in s]
            print(f'  {tag:36s} n={len(s):3d}  N={s[0][0]:.4g}  '
                  f'max={max(b):+.4f}  mean={sum(b)/len(b):+.4f}')
    print()

    print('=' * 74)
    print('ESTIMATORS FOR THE GUMBEL SCALE beta')
    print('=' * 74)
    est = {}
    for tag, s, key in (('E1 real-ct chunks   ', real, 'E1'),
                        ('E2 shuffled-ct null ', shuf, 'E2')):
        if len(s) >= 5:
            xs = [x[1] for x in s]
            mu, beta = gumbel_mle(xs)
            lo, hi = boot_beta(xs)
            est[key] = (mu, beta, s[0][0])
            print(f'  {tag} n={len(xs):3d}  beta={beta:.4f} '
                  f'[boot 95% {lo:.4f}..{hi:.4f}]  mu={mu:+.4f} at N={s[0][0]:.4g}')
        else:
            print(f'  {tag} n={len(s)} - too few for an MLE')

    if ts and f32:
        m1 = sum(x[1] for x in ts) / len(ts)
        m2 = sum(x[1] for x in f32) / len(f32)
        beta3 = (m2 - m1) / math.log(f32[0][0] / ts[0][0])
        est['E3'] = (m1 - beta3 * EULER, beta3, ts[0][0])
        print(f'  E3 across-N slope    mean {m1:+.4f} at N={ts[0][0]:.3g}  ->  '
              f'{m2:+.4f} at N={f32[0][0]:.3g}   beta={beta3:.4f}')
    print()

    if 'E1' not in est and 'E3' not in est:
        print('not enough data yet')
        return

    # conservative choice: the larger beta (higher null tail => more false positives)
    cands = {k: v for k, v in est.items() if k in ('E1', 'E3')}
    key = max(cands, key=lambda k: cands[k][1])
    mu, beta, N_ref = cands[key]
    print(f'Using {key} (larger beta = conservative): beta={beta:.4f}, '
          f'mu={mu:+.4f} at N={N_ref:.4g}')
    print()

    print('=' * 74)
    print('MODEL CHECK - predict held-out observations')
    print('=' * 74)
    checks = []
    if ts:
        checks.append(('R8 time-seed, mean of 10 gens', ts[0][0],
                       sum(x[1] for x in ts) / len(ts)))
    if f32:
        checks.append(('R8 full-32,   mean of 2 gens', f32[0][0],
                       sum(x[1] for x in f32) / len(f32)))
    if real:
        checks.append(('L5 chunk maxima, mean', real[0][0],
                       sum(x[1] for x in real) / len(real)))
    for label, N, obs in checks:
        print(f'  {label:32s} N={N:.4g}  observed {obs:+.4f}  '
              f'predicted {emax(mu, beta, N_ref, N):+.4f}  '
              f'diff {obs - emax(mu, beta, N_ref, N):+.4f}')
    print()

    N_GEN = 2 ** 32 * 2
    N_TOT = 10 * N_GEN
    N_TOT14 = 14 * N_GEN
    print('=' * 74)
    print('EXTRAPOLATION - the threshold question')
    print('=' * 74)
    for label, N in (('one generator, full 2^32 x 2 dir', N_GEN),
                     ('Round 8 sweep completed (10 gens)', N_TOT),
                     ('with this lane\'s 4 new gens (14)', N_TOT14)):
        print(f'  {label:34s} N={N:.3g}  E[null max]={emax(mu, beta, N_ref, N):+.4f}  '
              f'P(null > -12.5) = {p_exceed(mu, beta, N_ref, N, -12.5):.3f}')
    print()
    print('  PREREG H2 line: threshold safe iff E[null max] at the completed 10-gen')
    print('  sweep is <= -12.60 (>= 0.10 units of margin below -12.5).')
    v = emax(mu, beta, N_ref, N_TOT)
    print(f'  E[null max] = {v:+.4f}  ->  H2 {"PASS" if v <= -12.60 else "FAIL"}')
    print()

    print('=' * 74)
    print('REPLACEMENT THRESHOLDS (family-wise over a completed 10-generator sweep)')
    print('=' * 74)
    muN = mu + beta * math.log(N_TOT / N_ref)
    for alpha in (0.05, 0.01, 0.001):
        t = muN - beta * math.log(-math.log(1 - alpha))
        print(f'  FWER {alpha:<6} -> threshold {t:+.4f}')
    print()

    PLANT = -11.236
    print('=' * 74)
    print('DETECTION POWER - would a real seeded pad still be seen?')
    print('=' * 74)
    print(f'  planted-true score, this box, 14/14 generators : {PLANT:+.4f}')
    print(f'  wrong-seed scores                              : -15.8 .. -16.9')
    z = (PLANT - muN) / beta
    print(f'  true score sits {z:.2f} Gumbel scale units above the completed-sweep null')
    print(f'  P(the null anywhere in a completed sweep reaches {PLANT}) = '
          f'{p_exceed(mu, beta, N_ref, N_TOT, PLANT):.3e}')
    t01 = muN - beta * math.log(-math.log(1 - 0.01))
    print(f'  margin of the true score over the FWER-1% threshold: '
          f'{PLANT - t01:+.4f} ({(PLANT - t01)/beta:.2f} beta)')
    print()
    print('  PREREG H3 line: >= 1.0 units of margin between planted-true and the')
    print('  full-sweep null max => the sweep retains power and finishing it is')
    print('  informative; < 0.5 units => finishing it is a completeness ritual.')
    margin = PLANT - emax(mu, beta, N_ref, N_TOT)
    verdict = ('retains power' if margin >= 1.0
               else 'ritual' if margin < 0.5 else 'ambiguous band')
    print(f'  margin = {margin:+.4f}  ->  {verdict}')

    if 'E1' in est and 'E2' in est:
        print()
        print('=' * 74)
        print('NULL CONTROL - real ciphertext vs shuffled ciphertext at matched N')
        print('=' * 74)
        (mr, br, Nr), (ms, bs_, Ns) = est['E1'], est['E2']
        print(f'  real     mu={mr:+.4f}  beta={br:.4f}   (n={len(real)})')
        print(f'  shuffled mu={ms:+.4f}  beta={bs_:.4f}   (n={len(shuf)})')
        print(f'  difference in location: {mr - ms:+.4f}  '
              f'({abs(mr - ms) / br:.2f} beta)')
        print('  A real seeded-PRNG signal in the swept range would push the REAL')
        print('  location above the SHUFFLED one. |diff| < ~1 beta = no signal.')


if __name__ == '__main__':
    main()
