"""C3 / L3 -- the control H7 needs before its p = 6.7e-10 may be believed.

H7 asks whether the catalogued bands' GLYPH COUNTS lie on a binary ladder {1,2,4,8,16,32}.
`hypotheses.py` measures 29/109 = 26.6% against a base rate of 7.3% taken from all 646 image
bands, and reports p = 6.74e-10 -- which clears the family bar of 1.67e-4 by six orders of
magnitude. Taken at face value that is the only PASS in the H1-H8 family.

It is almost certainly a SELECTION EFFECT, and this script is the test that decides it.

The 109 records are not a sample of the 646 bands. They are exactly the bands Round 8's
ornament rule REJECTED -- and that rule rejects short things. Conditioning on shortness
concentrates the length distribution on small integers, and small integers are mechanically
rich in powers of two: five of the first sixteen positive integers are 2^k. So a base rate
computed over the unconditioned population is the wrong denominator, and any set of small
"special" numbers will look enriched against it.

TWO CONTROLS, both fixed here before either is read:

  C-H7a  DECOY SETS. Score the same 109 lengths against six OTHER six-element integer sets
         of comparable magnitude -- squares, triangulars, primes, Fibonacci, multiples of
         three, and a random six-element set drawn from 1..32. If the decoys score as high
         as the binary ladder, H7's enrichment is about magnitude, not about binaries.
         PASS for H7 iff the binary ladder's hit count EXCEEDS every decoy's.

  C-H7b  MATCHED NULL. Recompute the base rate over the subset of the 646 bands whose
         lengths fall in the SAME RANGE as the 109 catalogued bands, and over the subset
         that Round 8's own rejection rule would also have rejected. That is the correct
         reference class. PASS for H7 iff p < 1.67e-4 still holds against it.

H7 is only a finding if it survives both.
"""
import json, os, sys
import numpy as np
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402

FAMILY_BAR = 0.001 / 6
RNG = np.random.default_rng(3301)

LADDER = np.array([1, 2, 4, 8, 16, 32])
DECOYS = {
    'squares':        np.array([1, 4, 9, 16, 25, 36]),
    'triangular':     np.array([1, 3, 6, 10, 15, 21]),
    'primes':         np.array([2, 3, 5, 7, 11, 13]),
    'fibonacci':      np.array([1, 2, 3, 5, 8, 13]),
    'multiples_of_3': np.array([3, 6, 9, 12, 15, 18]),
    'random_1_32':    np.sort(RNG.choice(np.arange(1, 33), 6, replace=False)),
}


def binom_tail(k, n, p):
    return float(sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def main():
    inv = json.load(open(os.path.join(HERE, 'inventory.json')))
    lens = np.array([b['n'] for b in inv])
    n = len(lens)

    g2 = np.load(os.path.join(R.LP, 'analysis', 'geometry', 'glyphs2.npz'))
    allb = g2['bands'][:, 3].astype(int)

    out = dict(n_catalogued=n,
               catalogued_length_min=int(lens.min()),
               catalogued_length_max=int(lens.max()),
               catalogued_length_median=float(np.median(lens)),
               n_all_bands=int(len(allb)))

    # ---------------------------------------------------------------- C-H7a decoys
    lad_k = int(np.isin(lens, LADDER).sum())
    rows = []
    for name, S in list(DECOYS.items()):
        k = int(np.isin(lens, S).sum())
        p = float(np.isin(allb, S).mean())
        rows.append(dict(set=name, members=[int(v) for v in S], hits=k,
                         base_rate_all_646=round(p, 4),
                         binom_p_vs_all_646=binom_tail(k, n, p) if p > 0 else None))
    lad_p_all = float(np.isin(allb, LADDER).mean())
    out['C_H7a'] = dict(
        ladder=dict(set='binary_ladder', members=[int(v) for v in LADDER], hits=lad_k,
                    base_rate_all_646=round(lad_p_all, 4),
                    binom_p_vs_all_646=binom_tail(lad_k, n, lad_p_all)),
        decoys=rows,
        ladder_beats_every_decoy=all(lad_k > r['hits'] for r in rows),
        n_decoys_scoring_at_least_as_high=sum(1 for r in rows if r['hits'] >= lad_k))

    # ---------------------------------------------------------------- C-H7b matched null
    lo, hi = int(lens.min()), int(lens.max())
    inrange = allb[(allb >= lo) & (allb <= hi)]
    p_matched = float(np.isin(inrange, LADDER).mean()) if len(inrange) else float('nan')
    p_val_matched = binom_tail(lad_k, n, p_matched) if p_matched > 0 else None

    # a second matched reference: bands whose length is <= the catalogued 90th percentile,
    # i.e. the short tail Round 8's rule preferentially rejected
    q90 = float(np.quantile(lens, 0.90))
    shortref = allb[allb <= q90]
    p_short = float(np.isin(shortref, LADDER).mean()) if len(shortref) else float('nan')
    p_val_short = binom_tail(lad_k, n, p_short) if p_short > 0 else None

    out['C_H7b'] = dict(
        catalogued_range=[lo, hi],
        n_all_bands_in_range=int(len(inrange)),
        base_rate_matched_range=round(p_matched, 4),
        binom_p_matched_range=p_val_matched,
        catalogued_p90_length=q90,
        n_all_bands_le_p90=int(len(shortref)),
        base_rate_short_tail=round(p_short, 4),
        binom_p_short_tail=p_val_short,
        survives_matched_null=bool(p_val_matched is not None and p_val_matched < FAMILY_BAR),
        survives_short_tail_null=bool(p_val_short is not None and p_val_short < FAMILY_BAR))

    # ---------------------------------------------------------------- verdict
    survives = (out['C_H7a']['ladder_beats_every_decoy'] and
                out['C_H7b']['survives_matched_null'] and
                out['C_H7b']['survives_short_tail_null'])
    out['H7_verdict_after_controls'] = 'PASS' if survives else 'FAIL — selection effect'
    out['family_bar'] = FAMILY_BAR

    json.dump(out, open(os.path.join(HERE, 'h7_control.json'), 'w'), indent=1)

    print('catalogued bands n=%d  lengths %d..%d  median %.0f'
          % (n, lo, hi, np.median(lens)))
    print('\n--- C-H7a  decoy sets (same 109 lengths, other 6-element integer sets) ---')
    L = out['C_H7a']['ladder']
    print('  %-16s %-28s hits %3d  base %.4f  p=%.3g'
          % ('binary_ladder', str(L['members']), L['hits'], L['base_rate_all_646'],
             L['binom_p_vs_all_646']))
    for r in rows:
        print('  %-16s %-28s hits %3d  base %.4f  p=%s'
              % (r['set'], str(r['members']), r['hits'], r['base_rate_all_646'],
                 ('%.3g' % r['binom_p_vs_all_646']) if r['binom_p_vs_all_646'] is not None
                 else 'n/a'))
    print('  ladder beats EVERY decoy: %s   (decoys >= ladder: %d)'
          % (out['C_H7a']['ladder_beats_every_decoy'],
             out['C_H7a']['n_decoys_scoring_at_least_as_high']))

    print('\n--- C-H7b  matched reference class ---')
    print('  base rate over ALL 646 bands          : %.4f  -> p=%.3g'
          % (lad_p_all, binom_tail(lad_k, n, lad_p_all)))
    print('  base rate over bands in range %d..%-4d : %.4f  -> p=%.3g'
          % (lo, hi, p_matched, p_val_matched))
    print('  base rate over bands <= p90 (%.0f)      : %.4f  -> p=%.3g'
          % (q90, p_short, p_val_short))
    print('\nH7 AFTER CONTROLS: %s   (family bar p < %.3g)'
          % (out['H7_verdict_after_controls'], FAMILY_BAR))
    print('wrote h7_control.json')


if __name__ == '__main__':
    main()
