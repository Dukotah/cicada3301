# X1 independent re-derivation of $RANDOM for RANDOM=1 (does NOT import B1 generators.py)
import json, subprocess
M64=(1<<64)-1; M32=(1<<32)-1
def stream(step, seed, n):
    s=seed; last=0; out=[]
    while len(out)<n:
        rv,s=step(s)
        if rv==last: continue
        last=rv; out.append(rv)
    return out
def s32(s):               # 3.2 ANSI LCG, unsigned long (64-bit)
    s=(s*1103515245+12345)&M64; return (s>>16)&32767, s
def s4x(s):               # 4.0/4.1/4.2 LP64: long h,l ; rseed unsigned long = 16807*l-2836*h wraps mod 2^64
    if s==0: s=123459876  # 4.2 branch (4.0/4.1: seedrand() instead -> nondeterministic)
    h=s//127773; l=s%127773
    s=(16807*l-2836*h)&M64
    return s&32767, s
def s4x32(s):             # ILP32: unsigned long = 32 bit
    if s==0: s=123459876
    h=s//127773; l=s%127773
    s=(16807*l-2836*h)&M32
    return s&32767, s
def s51(s):               # 5.1 intrand32 + fold, compat>50
    r=123459876 if s==0 else s
    h=r//127773; l=r-127773*h
    t=16807*l-2836*h
    r=t+0x7fffffff if t<0 else t
    r&=M32
    return ((r>>16)^(r&65535))&32767, r
V=json.load(open('../B1-bash-versions/verification.json'))['versions']
res={}
for name,fn,key in [('bash3.2',s32,'bash3.2'),('bash4.1',s4x,'bash4.1'),('bash4.0',s4x,'bash4.0'),('bash5.1',s51,'bash5.1')]:
    mine=stream(fn,1,20)
    theirs=V[key].get('first20_after_RANDOM_eq_1')
    res[name]={'mine':mine,'theirs':theirs,'equal':mine==theirs}
res['bash4.1_ilp32']={'mine':stream(s4x32,1,20),'equal_to_lp64':stream(s4x32,1,20)==stream(s4x,1,20)}
# live bash 5.3.9 binary
live=subprocess.run(['bash','-c','RANDOM=1; for i in $(seq 20); do printf "%s " $RANDOM; done'],capture_output=True,text=True).stdout.split()
res['live_bash_5.3.9']={'vals':[int(x) for x in live],'equals_mine_5.1':[int(x) for x in live]==res['bash5.1']['mine']}
# more seeds vs live binary (incl. >=2^31)
ok=[]
for sd in (1,2,3301,2147483646,3000000000,4000000000,1354603465):
    l=[int(x) for x in subprocess.run(['bash','-c',f'RANDOM={sd}; for i in $(seq 20); do printf "%s " $RANDOM; done'],capture_output=True,text=True).stdout.split()]
    ok.append((sd,l==stream(s51,sd&M32,20)))
res['live_vs_mine_5.1_seeds']=ok
# orbit arithmetic
SEC0,SEC1=1325376000,1401580800
res['arith']={'3.2_orbit':SEC1-SEC0+32768,'3.2_chunks_2^18':-(-(SEC1-SEC0+32768)//262144),
 '4x_prefixes':(SEC1>>20)-(SEC0>>20)+1,'4x_orbit':((SEC1>>20)-(SEC0>>20)+1)<<20,
 '5.1_prefixes_closure':len({p^x for p in range(SEC0>>20,(SEC1>>20)+1) for x in range(8)}),
 'SEC0>>20':SEC0>>20,'SEC1>>20':SEC1>>20,
 '5.1_orbit':len({p^x for p in range(SEC0>>20,(SEC1>>20)+1) for x in range(8)})<<20,
 'frac_of_2^31':(len({p^x for p in range(SEC0>>20,(SEC1>>20)+1) for x in range(8)})<<20)/2**31,
 'pid32768_extra_pct_if_pidmax_4194304':(4194304-32768)/(SEC1-SEC0)*100}
json.dump(res,open('rerun_generators.json','w'),indent=1)
for k,v in res.items(): print(k, v if k in('arith','live_vs_mine_5.1_seeds') else {a:b for a,b in v.items() if a.startswith('equal') or a=='equals_mine_5.1'})
