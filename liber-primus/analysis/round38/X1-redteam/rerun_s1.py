import json,random,os,sys
sys.dont_write_bytecode=True
S1=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","S1-s2-windows")
d=json.load(open(os.path.join(S1,"control_inputs.json"))); out={}
for w in (777,1234567891,3000000017):
    r=random.Random(w); k=[int(r.random()*29) for _ in range(64)]
    out[str(w)]={"first64_match_control_inputs_first32":k[:32]==d[str(w)]["ks_first32"],"first8":k[:8]}
# cipher for 777 differs from the R27 plant (same plaintext, different rejection stream)
v=json.load(open(os.path.join(S1,"..","..","round27","P0-spec","vectors_s2.json")))["planted_selftest"]["cipher_idx"]
c=json.load(open(os.path.join(S1,"ctl_cipher_777.json")))["cipher_idx"]
out["777_cipher_positions_differing_from_R27_plant"]=sum(a!=b for a,b in zip(v,c))
a,b=1950696430,2059308008
out["window1"]={"advanced":b-a,"pp":(b-a)/2**32*100,"rate_per_s_at_1950s":(b-a)/1950,"cum_panelR36_seeds":54967546+b-a,"cum_pp":(54967546+b-a)/2**32*100,"R36_start_check":1950696430-1895728884}
json.dump(out,open("rerun_s1.json","w"),indent=1); print(json.dumps(out))
