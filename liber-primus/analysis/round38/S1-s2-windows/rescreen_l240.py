import os, sys, json, ctypes
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE,"..","..",".."))
A = os.path.join(LP,"analysis")
for p in ("round25/compute-tail","round33/I1-register-aware-beam"): sys.path.insert(0, os.path.join(A,p))
import numpy as np
class MS(ctypes.Structure):
    _fields_=[("l",ctypes.c_ulong),("ml",ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ("tp","ap","tpf","apf","tv","av","ae")]
m=MS(); m.l=ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); free=m.ap/2**30
print("free GB",free)
if free<0.35: raise SystemExit("RAM too low")
import runner, beam_v3 as V
V.set_panel(os.path.join(LP,"data","panels","panel-r36.npz"))
pan=V.panel(); print("registers",len(pan.registers))
C=list(runner.C_HIT); assert len(C)==240
out={}
for seed in (35563892, 2286867315):
    K=runner.word_stream(seed,240*6+64)
    for bw in (64,400):
        d=V.beam_decode_v3(C,K,1,"panel_max",sign=-1,o=0,beam_w=bw,tau=0.0,max_skip=3)
        x=np.asarray(d["plain_idx"],dtype=np.int64); mu,sd,_,_=pan.cal(len(x)); z=(pan.raw(x)-mu)/sd; i=int(z.argmax())
        out["%d_bw%d"%(seed,bw)]={"seed":seed,"beam_w":bw,"L":240,"n_plain":len(x),"z_max":float(z[i]),"register":pan.registers[i],"n_skips":d.get("n_skips"),"ptr_end":d.get("ptr_end"),"plain_idx_head60":list(map(int,x[:60]))}
        print(seed,bw,out["%d_bw%d"%(seed,bw)]["z_max"],pan.registers[i],d.get("n_skips"))
json.dump(out,open(os.path.join(HERE,"rescreen_l240.json"),"w"),indent=1)
