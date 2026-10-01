"""A2 final controls tying the verdict down.

(1) POSITIVE end-to-end: take a clean unimodal class's real dx values, ADD a
    known 0.6px bimodal perturbation carrying an ASCII message's bits (balanced),
    push through EM+bit_tests+ascii. Confirm the pipeline RECOVERS the message.
    -> proves that IF a >=0.6px positional channel existed it WOULD be detected,
       balanced, low-entropy, and ASCII-recoverable.

(2) BIAS EXPLANATION: show that the cls3_dy / cls9_dy 'non-random' runs_z is
    explained by distribution SKEW alone: shuffle the bits (destroys any order
    structure, keeps the bias) and confirm runs_z stays similarly negative and
    autocorr collapses -> the signal is bias, not sequence structure.
"""
import os, sys, json, math, collections
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure as M
from classpure import link_cc_to_class, measure_class
from bitstream_test import em2_resp, bit_tests, bits_to_ascii

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.normpath(os.path.join(HERE,'..','..','..'))
IMG=os.path.join(ROOT,'data','relikd')
RNG=np.random.default_rng(3301)


def run():
    recs = link_cc_to_class()
    by_cls=collections.defaultdict(list)
    for r in recs: by_cls[r[0]].append(r)
    pages={}
    def get(p):
        if p not in pages:
            pages[p]=M.to_ink(np.asarray(Image.open(os.path.join(IMG,f'p{p}.jpg')).convert('L')))
        return pages[p]
    CW,CH=90,140
    out={}

    # ---- (1) positive end-to-end on class 12 dx (clean) ----
    cid=12; insts=sorted(by_cls[cid],key=lambda r:(r[1],r[2],r[3]))
    crops=[]
    for (cl,p,li,cbx,cby,bw,bh) in insts[:400]:
        ink=get(p); ax0=int(round(cbx-CW/2)); ay0=int(round(cby-CH/2))
        if ax0<0 or ay0<0 or ax0+CW>ink.shape[1] or ay0+CH>ink.shape[0]: continue
        crops.append(ink[ay0:ay0+CH,ax0:ax0+CW].astype(np.float32))
    dxs,dys,corrs=measure_class(crops)
    n=len(dxs)
    msg='CICADA3301'
    mbits=[]
    for ch in msg:
        for k in range(7,-1,-1): mbits.append((ord(ch)>>k)&1)
    mbits=(mbits*((n//len(mbits))+1))[:n]
    injected = dxs + 0.6*np.array(mbits)   # inject 0.6px balanced-ish channel
    rec = em2_resp(injected)
    # align recovered bits to message bits (best of rec, ~rec)
    def acc(a,b): a=np.array(a);b=np.array(b);return max((a==b).mean(),(a==(1-b)).mean())
    a1=acc(rec,mbits)
    txt,pr=bits_to_ascii(rec)
    out['positive_e2e']=dict(n=n, injected_px=0.6, bit_accuracy=float(a1),
                             recovered_ascii=txt[:40], ascii_printable=pr,
                             tests=bit_tests(rec),
                             verdict='RECOVERED' if a1>0.9 else 'PARTIAL' if a1>0.7 else 'FAILED')

    # ---- (2) bias explanation for cls3_dy ----
    cid=3; insts=sorted(by_cls[cid],key=lambda r:(r[1],r[2],r[3]))
    crops=[]
    for (cl,p,li,cbx,cby,bw,bh) in insts[:600]:
        ink=get(p); ax0=int(round(cbx-CW/2)); ay0=int(round(cby-CH/2))
        if ax0<0 or ay0<0 or ax0+CW>ink.shape[1] or ay0+CH>ink.shape[0]: continue
        crops.append(ink[ay0:ay0+CH,ax0:ax0+CW].astype(np.float32))
    dxs,dys,corrs=measure_class(crops)
    pth=np.percentile(corrs,40); pure=corrs>=pth
    v=dys[pure]; m,s=np.median(v),np.std(v); v=v[np.abs(v-m)<3.5*s+1e-9]
    bits=em2_resp(v)
    orig=bit_tests(bits)
    shuf=bits.copy(); RNG.shuffle(shuf)
    sh=bit_tests(shuf)
    out['bias_explanation_cls3_dy']=dict(
        original=dict(ones=orig['ones_frac'],runs_z=orig['runs_z'],autocorr=orig['max_autocorr_lag2_63']),
        shuffled=dict(ones=sh['ones_frac'],runs_z=sh['runs_z'],autocorr=sh['max_autocorr_lag2_63']),
        note='if runs_z survives shuffle -> it is BIAS not order-structure')

    with open(os.path.join(HERE,'final_control_results.json'),'w') as f:
        json.dump(out,f,indent=2,default=float)
    print('POSITIVE E2E: inject 0.6px CICADA3301 ->',
          f"bit_acc={out['positive_e2e']['bit_accuracy']:.2f}",
          f"ascii={out['positive_e2e']['recovered_ascii']!r}",
          out['positive_e2e']['verdict'])
    b=out['bias_explanation_cls3_dy']
    print(f"BIAS CTRL cls3_dy: orig runs_z={b['original']['runs_z']:.2f} autocorr={b['original']['autocorr']:.2f}"
          f" | shuffled runs_z={b['shuffled']['runs_z']:.2f} autocorr={b['shuffled']['autocorr']:.2f}")
    return out


if __name__=='__main__':
    run()
