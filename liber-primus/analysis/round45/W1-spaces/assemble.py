# R45-W1: merge per-question outputs into results.json with the registered verdict per test.
import json
c = json.load(open('calib.json')); q1 = json.load(open('q1_results.json')); q2 = json.load(open('q2_results.json'))
q2b = json.load(open('q2b_posthoc.json')); q3 = json.load(open('q3q4_results.json'))
pp = q1['plant_power']
def inf_A(k): return pp['intact'][k] >= 0.8
def inf_B(k, u):
    return pp[u][k] >= 0.5 and pp['global'][k] <= 2 * q1['alpha_per_test'] + 1e-12
q1v = {}
for k, v in q1['real'].items():
    if k.startswith('A_'): inf = inf_A(k)
    elif k.startswith('B_'): inf = inf_B(k, k.split('_')[1])
    elif k == 'C_scan': inf = pp['intact'][k] >= 0.8
    else: inf = q1['D_unit_plant_power'][k.split('_')[1]] >= 0.5
    q1v[k] = dict(z=round(v['z'], 3), p=v['p'], reject=v['reject'],
                  informative=inf, verdict=('POSITIVE' if v['reject'] else 'null' if inf in (True, None) else 'uninformative'))
out = dict(lane='R45-W1', date='2026-11-23', calib=c,
           Q1=dict(alpha_per_test=q1['alpha_per_test'], tests=q1v, plant_power=pp, solved_reference=q1['solved_reference'],
                   C_patch_power=q1['C_patch_power'], D_unit_plant_power=q1['D_unit_plant_power'],
                   D_per_section_z=q1['real']['D_sect_max']['per_unit_z']),
           Q2=dict(alpha_per_test=q2['alpha_per_test'],
                   M1=dict(q2['M1_LP2_vs_solved'], control=q2['M1_control'], verdict='uninformative (size control failed: 0.43)'),
                   M2=dict(q2['M2_LP2_vs_english'], power=q2['M2_power'], verdict='null (within English spread; power vs 20% merges 0.68, vs <=10% merges 0)'),
                   M3=dict(q2['M3_geometric'], verdict='POSITIVE: geometric/random insertion rejected'),
                   M4=dict(q2['M4_period'], verdict='null (power >=0.8 at keyed fraction f>=0.2)'),
                   describe=q2['describe'], describe_per_section=q2['describe_per_section'], posthoc=q2b),
           Q3=dict(alpha_per_test=q3['alpha_per_test'], L1=dict(q3['L1_real'], plants=q3['L1_plants'], LP1_reference=q3['L1_LP1_reference'],
                                                               verdict='null (power 0.93 at q=0.10 content-keyed rewiring; BLIND to true spacing under OTP-class key: power 0.00)'),
                   L2=dict(q3['L2_real'], plants=q3['L2_plants'], verdict='null (power 0.93 at q=0.20)')),
           Q4=dict(R1_q_estimates=q3['R1_q_estimates'], R1_lag_equality=q3['R1_lag_equality'], R2_otp_demo=q3['R2_otp_demo']))
json.dump(out, open('results.json', 'w'), indent=1)
for k, v in q1v.items(): print(k, v)
