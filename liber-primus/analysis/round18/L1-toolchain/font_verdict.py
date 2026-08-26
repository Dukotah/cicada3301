"""Instrument correction + final font verdict.

WHY THIS EXISTS.  `font_match.py` reports two distances per candidate face:
D_aspect (aspect-preserving fit) and D_stretch (both bitmaps independently
stretched to a common box, so only stroke topology is compared).  Inspecting
`runes_observed_meta.json` after the first run shows every one of the 29 observed
rune bitmaps has height EXACTLY 114 px.  Real runic faces do not have 29 glyphs of
identical height - so that uniformity is an artefact of the R9 template pipeline,
which normalises cluster heights.  **D_aspect is therefore confounded for the LP2
side and must not be used.**  D_stretch is unaffected and is the valid metric.

This script recomputes the whole PC3 calibration on D_stretch and re-issues the
verdict against the pre-registered rule (inside the degraded-self band, and
>= 2 sigma clear of the runner-up over >= 20 rune classes).
"""
import os, sys, json, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from font_match import render_font, degrade, compare, FONTS
from font_sheet import half_centroids


def main():
    obs_npz = np.load(os.path.join(HERE, 'runes_observed.npz'))
    obs = {int(k[1:]): obs_npz[k].astype(np.uint8) for k in obs_npz.files}

    bank = {}
    for p in sorted(glob.glob(os.path.join(FONTS, '*.ttf')) +
                    glob.glob(os.path.join(FONTS, '*.otf'))):
        r = render_font(p)
        if r:
            bank[os.path.basename(p)] = r

    M = 'mean_stretch'
    # PC3b degraded self-match, on the aspect-free metric
    pc3b, selfd = {}, []
    for name, glyphs in bank.items():
        deg = degrade(glyphs)
        sc = {o: compare(deg, bank[o])[M] for o in bank}
        rank = sorted(sc, key=sc.get)
        pc3b[name] = {'degraded_self_distance': round(sc[name], 5),
                      'rank_of_self': rank.index(name) + 1,
                      'runner_up': rank[1], 'runner_up_distance': round(sc[rank[1]], 5)}
        selfd.append(sc[name])
    cross = [compare(bank[a], bank[b])[M] for a in bank for b in bank if a != b]

    # PC3c: LP2's own split-half reproducibility, same metric
    A, B = half_centroids()
    noise = compare(A, B)

    real = {}
    for name, glyphs in bank.items():
        c = compare(obs, glyphs)
        c.pop('per_rune')
        real[name] = c
    order = sorted(real, key=lambda n: real[n][M])
    best, second = order[0], order[1]
    sd = real[best]['sd_stretch']
    sep = (real[second][M] - real[best][M]) / sd if sd > 0 else None

    band = [round(min(selfd), 5), round(max(selfd), 5)]
    out = {
     'metric': 'mean_stretch (aspect-free; D_aspect disqualified because the R9 '
               'template pipeline height-normalises every observed glyph to 114 px)',
     'PC3b_degraded_self_match': pc3b,
     'PC3b_PASS': all(v['rank_of_self'] == 1 for v in pc3b.values()),
     'PC3c_LP2_split_half_noise_floor': round(noise[M], 5),
     'PC3c_n_classes': noise['n'],
     'calibration': {
        'degraded_self_band': band,
        'degraded_self_mean': round(float(np.mean(selfd)), 5),
        'cross_face_mean': round(float(np.mean(cross)), 5),
        'cross_face_min': round(float(np.min(cross)), 5),
        'cross_face_p05': round(float(np.percentile(cross, 5)), 5),
        'n_cross_pairs': len(cross),
     },
     'ranking': [(n, round(real[n][M], 5)) for n in order],
     'verdict': {
        'best': best, 'best_distance': round(real[best][M], 5),
        'runner_up': second, 'runner_up_distance': round(real[second][M], 5),
        'separation_sigma': round(sep, 3) if sep is not None else None,
        'n_rune_classes': real[best]['n'],
        'inside_degraded_self_band': band[0] <= real[best][M] <= band[1],
        'below_cross_face_p05': real[best][M] < float(np.percentile(cross, 5)),
        'ratio_to_LP2_noise_floor': round(real[best][M] / noise[M], 2),
        'IDENTIFIED_per_prereg': bool(band[0] <= real[best][M] <= band[1] and
                                      sep is not None and sep >= 2.0 and
                                      real[best]['n'] >= 20),
     },
    }
    json.dump(out, open(os.path.join(HERE, 'font_verdict.json'), 'w'), indent=1)
    print(json.dumps({k: out[k] for k in
                      ('metric', 'PC3b_PASS', 'PC3c_LP2_split_half_noise_floor',
                       'calibration', 'ranking', 'verdict')}, indent=1))


if __name__ == '__main__':
    main()
