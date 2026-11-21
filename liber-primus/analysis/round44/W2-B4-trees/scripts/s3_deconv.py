"""S3: PC3 deconvolution power plants + hallucination controls + real p32 tree deconvolution.

PC3a: rune crop blurred Gaussian(sigma_est from S2), RL-30 -> edge-energy recovery >= 0.5 + crop.
PC3b: 3x-upscaled rune crop (branch-scale strokes) same plant — the scale a tree-embedded
      glyph would live at. (Added control-phase, before any real deconv; extra plant, no
      threshold change.)
Hallucination controls (T3 leg): sharp rune crop + blank paper crop through the full grid;
      novel stroke components must be < 1 per output.
Real: tree crop over full PREREG grid x {Wiener K=0.01, RL-30}; T3 flag iff >= 5 novel
      stroke comps absent from (dilated) original dark mask while controls < 1.
"""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imglib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGMA_EST = 26  # from results/blur_freq.json (S2)


def grid_psfs():
    out = []
    for s in range(2, 31, 2):
        out.append((f'gauss{s}', L.psf_gauss(s)))
    for r in range(2, 31, 2):
        out.append((f'disk{r}', L.psf_disk(r)))
    for Lm in (5, 10, 20, 40):
        for ang in np.arange(0, 180, 22.5):
            out.append((f'motion{Lm}_{ang:g}', L.psf_motion(Lm, ang)))
    return out


def deconv_both(img, psf):
    return {'wiener': L.wiener(img, psf, K=0.01), 'rl30': L.richardson_lucy(img, psf, iters=30)}


def main():
    out = {}
    runes = L.crop(L.loadY(L.PATHS['p32_relikd']), L.P32_RUNES)
    tree = L.crop(L.loadY(L.PATHS['p32_relikd']), L.P32_TREE)
    blank = L.loadY(L.PATHS['p32_relikd'])[50:600, 700:1630]

    # ---------- PC3a / PC3b ----------
    pc3 = {}
    for name, base in [('PC3a_runes', runes),
                       ('PC3b_runes3x', np.asarray(
                           Image.fromarray(runes.astype(np.uint8)).resize(
                               (runes.shape[1] * 3 // 2, runes.shape[0] * 3 // 2), Image.LANCZOS),
                           float))]:
        # crop upscaled to manageable size
        b = base[:1100, :1350]
        blurred = L.blur_with(b, L.psf_gauss(SIGMA_EST))
        rest = L.richardson_lucy(blurred, L.psf_gauss(SIGMA_EST), iters=30)
        e0, eb, er = L.edge_energy(b), L.edge_energy(blurred), L.edge_energy(rest)
        rec = (er - eb) / max(e0 - eb, 1e-9)
        pc3[name] = {'edge_energy_orig': round(e0), 'blurred': round(eb), 'restored': round(er),
                     'recovery': round(float(rec), 3), 'passed_050': bool(rec >= 0.5)}
        L.save_png(np.hstack([b, blurred, rest]),
                   os.path.join(HERE, 'crops', f'{name}_orig_blur_rl30.png'))
        print(name, pc3[name])
    out['PC3'] = pc3
    out['PC3_passed_any_scale'] = any(v['passed_050'] for v in pc3.values())

    psfs = grid_psfs()
    out['grid_size'] = len(psfs)

    # ---------- hallucination controls + real, same loop/glue ----------
    targets = {'control_sharp': runes[:1020, :1350], 'control_blank': blank, 'real_tree': tree}
    res = {k: [] for k in targets}
    worst = {k: 0 for k in targets}
    best_examples = {}
    for pname, psf in psfs:
        for tname, timg in targets.items():
            for method, dec in deconv_both(timg, psf).items():
                n, comps = L.novel_stroke_count(dec, timg)
                res[tname].append({'psf': pname, 'method': method, 'novel': n})
                if n > worst[tname]:
                    worst[tname] = n
                    best_examples[tname] = (pname, method, dec.copy(), comps)
    for tname in targets:
        counts = [r['novel'] for r in res[tname]]
        out[tname] = {'max_novel': int(max(counts)), 'mean_novel': round(float(np.mean(counts)), 3),
                      'n_outputs': len(counts),
                      'worst': sorted(res[tname], key=lambda r: -r['novel'])[:5]}
        print(tname, out[tname]['max_novel'], out[tname]['mean_novel'])

    controls_clean = out['control_sharp']['max_novel'] < 1 and out['control_blank']['max_novel'] < 1
    t3_flag = controls_clean and out['real_tree']['max_novel'] >= 5
    out['T3_controls_clean'] = bool(controls_clean)
    out['T3_flag_for_oracle'] = bool(t3_flag)

    # save oracle/record crops of the real tree deconvolutions at informative PSFs
    for pname in (f'gauss{SIGMA_EST}', 'gauss26', 'gauss14', 'disk14'):
        psf = dict(psfs).get(pname)
        if psf is None:
            continue
        d = deconv_both(tree, psf)
        L.save_png(np.hstack([tree, d['wiener'], d['rl30']]),
                   os.path.join(HERE, 'crops', f'real_tree_{pname}_orig_wiener_rl30.png'))
    if 'real_tree' in best_examples:
        pname, method, dec, comps = best_examples['real_tree']
        L.save_png(dec, os.path.join(HERE, 'crops', f'real_tree_maxnovel_{pname}_{method}.png'))
        out['real_tree']['maxnovel_example'] = {'psf': pname, 'method': method,
                                                'components': [{k: v for k, v in c.items()} for c in comps]}
    json.dump(out, open(os.path.join(HERE, 'results', 'deconv.json'), 'w'), indent=1)
    print('T3 controls clean:', controls_clean, '| T3 flag:', t3_flag)


if __name__ == '__main__':
    main()
