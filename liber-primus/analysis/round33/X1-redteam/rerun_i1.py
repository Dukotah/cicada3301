import sys, os, json
I1 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'I1-register-aware-beam'))
sys.path.insert(0, I1); sys.dont_write_bytecode = True
import run_envelope as R, numpy as np
out = {}
stored = {n: json.load(open(os.path.join(I1, f'out_grid_{n}.json'))) for n in ('base', 'panel_max')}
cells = [('EN_NOVOWEL', 'skip_by_two', 2, 120), ('EN_NOVOWEL', 'free_q05', 'free', 120), ('EN_MODERN', 'skip_by_two', 2, 120)]
for reg, enc, adv, L in cells:
    for design in ('base', 'panel_max'):
        for tag, seeds in (('same_seeds_0-4', range(0, 5)), ('fresh_seeds_40-44', range(40, 45))):
            c = R.run_cell(design, reg, enc, adv, L, seeds)
            k = f'{design}|{reg}|{enc}|dec={adv}|L{L}'
            st = stored[design].get(k)
            rec = [r['recovery'] for r in c['rows']]
            ent = {'recoveries': rec, 'median': c['median_recovery'], 'mean': round(c['mean_recovery'], 4)}
            if st and tag.startswith('same'):
                orec = [r['recovery'] for r in st['rows'] if r['seed'] in seeds]
                ent['stored_recoveries_same_seeds'] = orec
                ent['row_for_row_match'] = (orec == rec)
                ent['stored_full20_median'] = st['median_recovery']
            out[f'{k}|{tag}'] = ent
            print(f'{k}|{tag}', ent, flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rerun_i1_cells.json'), 'w'), indent=1)
