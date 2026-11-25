# R46-P1: merge stage outputs into results.json and write ledger_rows.json. Pure stdlib.
import os, json, hashlib

H = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(H, f)))
s1i, ri, s1ii, rii = J('lead_i_stage1.json'), J('lead_i_results.json'), J('lead_ii_stage1.json'), J('lead_ii_results.json')
s1i.pop('solved_len', None)
s1i['T1'].pop('windows', None)
for p in s1i['T2'].values(): p.pop('fe_vals', None)
prereg_sha = hashlib.sha256(open(os.path.join(H, 'PREREG.md'), 'rb').read()).hexdigest()
res = dict(lane='round46/P1-leads', date='2026-11-24', prereg_sha256=prereg_sha,
           lead_i=dict(stage1_controls=s1i, results=ri), lead_ii=dict(stage1_controls=s1ii, results=rii))
json.dump(res, open(os.path.join(H, 'results.json'), 'w'), indent=1)

ev = lambda *f: ['liber-primus/analysis/round46/P1-leads/' + x for x in f]
common = dict(round='46/P1', date='2026-11-24', lane='round46/P1-leads', threshold_fixed_in_advance=True,
              reproduce='cd liber-primus/analysis/round46/P1-leads && python p1_lead_i.py && python p1_lead_ii.py && python assemble.py')
T1, T2, T3, T4 = ri['T1'], ri['T2'], ri['T3'], ri['T4']
U1, U2, U3 = rii['U1'], rii['U2'], rii['U3']
rows = [
    dict(common, id='R46-P1-TWO-RUNE-DEFICIT-REPLICATION',
         hypothesis="LP2's 2-rune printed-word share (15.47%) is below the English range on fresh reference corpora not used in R45, and the deficit is carried by every held-out half/chapter set of LP2.",
         status='measured',
         threshold='T1: equal-weight fraction of 6,000 fresh-English (FE, 30 corpora) 2,896-word windows with share <= LP2 must be <= 0.01; informative iff leave-one-corpus-out size <= 0.03 and LP2-size thinning plant power >= 0.8. T2: all four parts (halves, odd/even $-sections) p <= 0.05 vs FE windows of their size; section G permutation p <= 0.01 = heterogeneous.',
         positive_control='partial',
         control_detail={'T1 size (leave-one-corpus-out)': '%.4f -> FAILS the 0.03 bar; driven by one corpus (Paradise Lost: 0.99 of its windows below the others\' 1st percentile)' % s1i['T1']['S1_size_mean'],
                         'T1 PC2 power (thinned to 15.5%)': round(s1i['T1']['PC2_power'], 3),
                         'T2 PC2 power per part': {p: round(d['pc2_power'], 3) for p, d in s1i['T2'].items()},
                         'T2 section-heterogeneity plant power': s1i['T2_sect_plant']['power']},
         null='FE window distribution at the same word count (200 windows x 30 corpora; 60 per corpus for parts); 10,000 within-LP2 length permutations for section G.',
         result='T1: LP2 15.47%% vs FE pooled min 16.06%%, 1st pct %.2f%%; p_FE = 0 of 6,000, but T1 is formally UNINFORMATIVE (size control failed by Paradise Lost, whose windows reach 16.1%%). Every other FE corpus min >= 19.2%%. T2 REPLICATES: H1 15.3%%, H2 15.6%%, odd sections 15.4%%, even 15.6%%, all p <= 0.0006 (power >= 0.995). Sections homogeneous (G p = %.2f, plant power 0.98; per-section 12.5-17.7%%).' % (100 * T1['fe_pooled_q01'], T2['section_G_p']),
         coverage='30 fresh English corpora (6 archaic, 11 translated, 12 modern prose, 1 verse) at power 0.96 for an LP2-size deficit; LP2 split two ways at power >= 0.995.',
         not_covered=['A reference panel whose size control passes with Milton-like verse included (needs a register-stratified null).',
                      'Registers outside the 30 FE corpora (e.g. technical, epistolary, 2010s web English).'],
         evidence=ev('PREREG.md', 'RESULTS.md', 'results.json', 'p1_lead_i.py', 'p1lib.py', 'run.log'),
         reopens_if='A pre-registered register-stratified null with a passing size control is built; or an English register is found whose windows routinely reach 15.5%.',
         notes='Post-hoc lead from R45-W1 q2b; the LP2 value itself was seen. The deficit is whole-text (not one chapter). Only archaic verse (Paradise Lost) comes near it.'),
    dict(common, id='R46-P1-TWO-RUNE-EXPLANATIONS',
         hypothesis="LP2's 9-class word-length profile is consistent with (a) fresh English, (b) English without articles, (c) English with 10%/20% of separators missing, (d) Latin, (e) German, (f) Welsh, (g) Old English, (h) the solved Cicada pages; and dropped line-final separators could by themselves restore an English 2-rune share.",
         status='measured',
         threshold='T3: admitted iff G(LP2 vs first-half q_R) <= 99th pct of 300 second-half windows; diagonal of 100-window confusion matrix >= 0.95; distinguishable iff both off-diagonals <= 0.2. T4: split all line-spanning words; "cannot explain" iff s_max <= FE 1st pct at the new count.',
         positive_control='passed',
         control_detail={'confusion diagonal': {R: s1i['T3']['confusion'][R][R] for R in s1i['T3']['confusion']},
                         'EN-FE vs EN-noART vs EN-merge10': 'mutual admit rates 0.96-1.00: NOT distinguishable',
                         'LA, CY vs English': 'off-diagonal <= 0.07: distinguishable'},
         null='Second-half windows of each reference (equal weight per corpus); SOLVED by resample-then-multinomial bootstrap.',
         result='Admitted: EN-FE (G %.0f / bar %.0f), EN-noART (%.0f / %.0f), EN-merge10 (%.0f / %.0f), EN-merge20 (%.0f / %.0f). Rejected: LA %.0f/%.0f, DE %.0f/%.0f, CY %.0f/%.0f, OE %.0f/%.0f, SOLVED %.0f/%.0f. The admitted four are mutually indistinguishable by this test (confusion 0.56-1.00). T4: splitting every line-spanning word gives 18.73%% vs FE 1st pct 17.97%% (p = %.3f) -> the line-merge ceiling DOES reach the bottom of the English range; T4 does not exclude dropped separators.' % tuple(
             [T3[R][k] for R in ['EN-FE', 'EN-noART', 'EN-merge10', 'EN-merge20', 'LA', 'DE', 'CY', 'OE', 'SOLVED'] for k in ('G', 'bar99')] + [T4['p']]),
         coverage='9 generators, 9-class length profile, 2,896 words; German/Old English rejections are sharp (bars 121/137); English-family members are not separable from each other.',
         not_covered=['Lengths borrowed from a specific other text (unidentifiable from a multiset).', 'Greek, Hebrew, Norse (R36 corpora not on disk) and other languages.', 'Discrimination among English register / article deletion / missing separators (the G test cannot).'],
         evidence=ev('PREREG.md', 'RESULTS.md', 'results.json', 'p1_lead_i.py', 'p1lib.py'),
         reopens_if='A statistic that separates article deletion from separator merging at power >= 0.8 (e.g. a 1-rune/3-rune joint test) is pre-registered.',
         notes='Pooled-English bars are wide because between-corpus spread is large; admission into EN-FE is weak evidence. The solved Cicada pages are the one English-like reference that rejects LP2.'),
    dict(common, id='R46-P1-LINEBREAK-INSIDE-WORDS',
         hypothesis="LP2's line breaks prefer word boundaries less than LP1's in every held-out part (U1b); LP2 still prefers boundaries above chance (U1a); the residual preference shows the short-line signature of word-aware wrapping (U2); line-spanning LP2 words contain merged pairs from dropped separators (U3).",
         status='inconclusive',
         threshold='U1b one-sided permutation (10,000) p <= 0.01 in all four parts, informative iff typesetting-plant power >= 0.8 and size <= 0.02; U1a binomial p <= 0.01; U2 within-page label permutation p <= 0.01 (LP1 must pass, plant power >= 0.8 for an informative null); U3 LR > 99th pct of 1,000 layout plants, informative iff power(d=1) >= 0.8.',
         positive_control='partial',
         control_detail={'U1b plant power per part': {p: d['power_b'] for p, d in s1ii['U1_plants'].items()}, 'U1b size': 0.0,
                         'U1a plant power': {p: d['power_a'] for p, d in s1ii['U1_plants'].items()},
                         'U2': 'LP1 real D=%.2f p=%.4f (passes); plant power %.2f (fails); size %.3f' % (s1ii['U2_controls']['LP1_D'], s1ii['U2_controls']['LP1_p'], s1ii['U2_controls']['power_rho_LP2'], s1ii['U2_controls']['size_blind']),
                         'U3': 'power d=1.0 %.2f, d=0.5 %.2f (fails 0.8); LP1 w_hat=%.2f' % (s1ii['U3_controls']['power']['1.0']['power'], s1ii['U3_controls']['power']['0.5']['power'], s1ii['U3_controls']['LP1_w_hat'])},
         null='Permutation of boundary-excess indicators between LP1 and the part; binomial at (1-c); within-page shuffle of line end types; justified-typesetting layout simulation (blind cut / word-aware mixture, slack 6) on LP2 widths.',
         result='Running-line definition: LP1 pi=0.22 (126 lines), LP2 pi=0.062 (532 lines). Full LP2 vs LP1 p=%.4f (descriptive). U1b parts: P1 p=%.3f, P2 %.4f, S_odd %.3f, S_even %.4f -> not all pass, and every part is UNINFORMATIVE (power 0.46-0.62, limited by LP1\'s 126 lines). U1a: full LP2 p=%.4f; parts uninformative (power <= 0.26). U2: LP2 D=%.2f p=%.3f, null uninformative (power 0.27). U3: w_hat=0.00, LR=0.00 (bar %.2f), uninformative (power 0.55).' % (rii['LP2_full_p_b'], U1['P1']['p_b'], U1['P2']['p_b'], U1['S_odd']['p_b'], U1['S_even']['p_b'], rii['LP2_full_p_a'], U2['D'], U2['p'], U3['bar99']),
         coverage='All 532 LP2 and 126 LP1 running line breaks; layout models: blind fixed-width cut, word-aware mixture wrap (slack 6), blind cut with line-final separator drops.',
         not_covered=['A held-out replication with adequate power (needs more word-aware reference pages than LP1\'s 126 running lines).', 'Glyph-width-aware justification, hyphenation rules, keyed layouts.', 'Page images: whether line-final dots are printed but untranscribed.'],
         evidence=ev('PREREG.md', 'RESULTS.md', 'results.json', 'p1_lead_ii.py', 'p1lib.py', 'run.log'),
         reopens_if='A larger word-aware reference layout (e.g. other Cicada-typeset pages) or an image check of line-final separators is available.',
         notes='The LP1-vs-LP2 difference stands on the full data (p=0.005) but the pre-registered held-out replication cannot be powered with LP1 as the only comparator.'),
]
json.dump(rows, open(os.path.join(H, 'ledger_rows.json'), 'w'), indent=1)
print('ok', prereg_sha)
