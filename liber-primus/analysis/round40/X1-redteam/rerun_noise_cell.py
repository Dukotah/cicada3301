import sys, os, json
B3='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/B3-english-era-grids'
sys.path.insert(0,B3); os.chdir(B3); sys.dont_write_bytecode=True
import engine as E, grids as G
import skipdecode as _sk
E.G = type('x', (), {'sk': _sk})
keep=json.load(open(E.F('keep_KDF.json')))
row=[r for r in keep if r['rel']=='keyskip2' and r['pmax']>=6.5][0]; m=row['meta']; g=G.KdfGrid(); Kf=g.keyfull(m)
out={'meta':m,'buffer_len':len(Kf),'stored_pmax':row['pmax']}
for L in (120,174):
    C,Ke=E.apply_variant(E.U[:L],Kf,m['atb'],m['sg'])
    for rel in E.RELS:
        d,a=E.v3dec(C,Ke,rel)
        out[f'L{L}|{rel}']={'pmax':round(float(a['pmax']),3),'preg':E.PAN.registers[a['preg']],'translit':_sk.idx_to_trans(d['plain_idx'])[:120]}
# wrong-key controls: same secret with 20 other reductions/secrets? use the sign flip and fwd twin
twin=dict(m); twin['dir']='fwd'; Kt=g.keyfull(twin); C,Ke=E.apply_variant(E.U[:120],Kt,m['atb'],m['sg']); d,a=E.v3dec(C,Ke,'keyskip2'); out['fwd_twin_L120_ks2']=round(float(a['pmax']),3)
json.dump(out,open('C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/X1-redteam/rerun_noise_cell.json','w'),indent=1)
print(json.dumps(out,indent=1))
