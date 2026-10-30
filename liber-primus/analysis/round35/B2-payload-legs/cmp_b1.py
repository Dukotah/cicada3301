import json,os
L=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(L,'R30-B1')
st=json.load(open(os.path.join(L,'..','..','round30','B1-blob-crypto','results.json')))
def ld(a): return json.load(open(os.path.join(R,a,'results.json')))
sup=ld('superseded'); pro=ld('promoted'); pro1=ld('promoted_run1')
def xo(r): return {(x['a'],x['b']):(x['entropy'],x['xlen'],x['head_hex'],tuple(map(str,x['hits']))) for x in r['cross_xor']}
def og(r): return [(x['tool'],x['blob'],x['pass'],x['len'],x.get('algo'),str(x['hits'])) for x in r['openssl_gpg']]
out={}
out['comparator_vs_stored']={'structural_equal_all3':sup['structural']==st['structural'],
 'cipher_hits_equal':sup['cipher_hits']==st['cipher_hits'],'cross_xor_equal':xo(sup)==xo(st),
 'openssl_gpg_equal':og(sup)==og(st),'summary_equal_ex_ctrl':{k:sup['summary'][k]==st['summary'][k] for k in ['cipher_success_hits','cross_xor_structure','openssl_gpg_hits','all_three_random']}}
out['controls']={'superseded':sup['controls']['positive']['PASS'],'superseded_neg':sup['controls']['negative'],'promoted_neg_run2':pro['controls']['negative'],'promoted_neg_run1':pro1['controls']['negative']}
sx,px=xo(sup),xo(pro)
out['promoted_vs_comparator']={'cipher_hits_promoted':len(pro['cipher_hits']),'cipher_hits_comparator':len(sup['cipher_hits']),
 'structural_T2_folly_equal':all(pro['structural'][k]==sup['structural'][k] for k in('T2','folly')),
 'structural_canon_equal':pro['structural']['canon']==sup['structural']['canon'],
 'xor_rows':{f"{a}^{b}":{'comp':sx[(a,b)][0],'prom':px[(a,b)][0],'hits_prom':px[(a,b)][3]} for (a,b) in sx if 'canon' in (a,b.split(':')[0])},
 'xor_rows_changed_count':sum(1 for k in sx if sx[k]!=px[k]),
 'xor_noncanon_rows_unchanged':all(sx[k]==px[k] for k in sx if 'canon' not in (k[0],k[1].split(':')[0])),
 'min_xor_entropy_prom':min(v[0] for v in px.values()),'any_hits':any(v[3] for v in px.values()),
 'openssl_gpg_equal':og(sup)==og(pro),'summary_prom':pro['summary']}
json.dump(out,open(os.path.join(R,'compare.json'),'w'),indent=1,default=str); print(json.dumps(out,indent=1,default=str))
