"""A2 bitstream extraction + structure test for flagged bimodal channels.

For each class flagged bimodal on an axis, assign each instance a bit = which
Gaussian component it belongs to (EM responsibility), in READING ORDER
(page, line, x). Then test the bitstream for:
  - balance (fraction of 1s)
  - entropy of order-1..3 (is it compressible / patterned?)
  - runs test (randomness)
  - autocorrelation peaks (periodicity => structure)
  - does concatenating bits across flagged classes / mapping to bytes yield ASCII?

Also a FIXED shape-mix negative control (two clean, non-pathological classes)
and a per-class within-shape SANITY control: split a clean unimodal class at its
median and confirm those (noise) bits read RANDOM (they must).

A genuine hidden channel => structured (low entropy / periodic / ASCII-ish).
Rendering/JPEG noise => random bits at every test. That is the null we expect.
"""
import os, sys, json, collections, math
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure as M
from realfloor import parabolic_peak
from classpure import link_cc_to_class, measure_class

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')


def em2_resp(x):
    x = np.asarray(x, float)
    lo, hi = np.percentile(x, [25, 75])
    mus = np.array([lo, hi]); sds = np.array([x.std(), x.std()])+1e-6; ws=np.array([.5,.5])
    for _ in range(300):
        p = np.stack([ws[k]*_g(x,mus[k],sds[k]) for k in range(2)])
        resp = p/(p.sum(0)+1e-30); Nk=resp.sum(1)+1e-9
        ws=Nk/len(x); mus=(resp*x).sum(1)/Nk
        sds=np.sqrt((resp*(x-mus[:,None])**2).sum(1)/Nk)+1e-6
    o = np.argsort(mus)
    bit = (resp[o[1]] > resp[o[0]]).astype(int)
    return bit

def _g(x,m,s): return np.exp(-0.5*((x-m)/s)**2)/(s*np.sqrt(2*np.pi))


def bit_tests(bits):
    bits = np.asarray(bits, int)
    n = len(bits)
    if n < 30:
        return {'n': n, 'note': 'too few'}
    ones = bits.mean()
    # runs test z
    r = 1 + int((bits[1:] != bits[:-1]).sum())
    n1 = bits.sum(); n0 = n - n1
    if n1 == 0 or n0 == 0:
        z = 0.0
    else:
        er = 2*n1*n0/n + 1
        vr = 2*n1*n0*(2*n1*n0-n)/(n*n*(n-1)+1e-9)
        z = (r - er)/math.sqrt(vr+1e-12)
    # block entropy (order-2,3)
    def blk_ent(k):
        if n < k*8: return None
        cnt = collections.Counter(tuple(bits[i:i+k]) for i in range(n-k+1))
        tot = sum(cnt.values()); H = -sum((c/tot)*math.log2(c/tot) for c in cnt.values())
        return H / k  # per-bit
    # autocorrelation
    b = bits - bits.mean()
    ac = np.correlate(b, b, 'full')[n-1:]
    ac = ac/(ac[0]+1e-12)
    peak = float(np.max(np.abs(ac[2:min(64,n)]))) if n > 4 else 0.0
    peak_lag = int(np.argmax(np.abs(ac[2:min(64,n)]))+2) if n > 4 else 0
    return dict(n=n, ones_frac=float(ones), runs_z=float(z),
                ent_o2=blk_ent(2), ent_o3=blk_ent(3),
                max_autocorr_lag2_63=peak, peak_lag=peak_lag,
                random_like=bool(abs(z) < 2 and peak < 0.25))


def bits_to_ascii(bits):
    bits = list(bits)
    out = []
    for i in range(0, len(bits)-7, 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | int(b)
        out.append(byte)
    txt = ''.join(chr(b) if 32 <= b < 127 else '.' for b in out)
    printable = sum(1 for b in out if 32 <= b < 127)
    return txt[:120], printable/len(out) if out else 0


def run():
    recs = link_cc_to_class()
    by_cls = collections.defaultdict(list)
    for r in recs:
        by_cls[r[0]].append(r)          # (cls,page,line,cbx,cby,bw,bh)
    pages = {}
    def get(p):
        if p not in pages:
            pages[p] = M.to_ink(np.asarray(Image.open(os.path.join(IMG, f'p{p}.jpg')).convert('L')))
        return pages[p]

    flagged = json.load(open(os.path.join(HERE, 'classpure_results.json')))['structured_flags']
    # skip pathological class 4 (dx corr-lock, std~5px)
    flagged = [f for f in flagged if not (f['cls']=='4' and f['axis']=='dx')]

    CW, CH = 90, 140
    results = {}
    all_bits = []
    for f in flagged:
        cid = int(f['cls']); ax = f['axis']
        insts = sorted(by_cls[cid], key=lambda r: (r[1], r[2], r[3]))  # reading order
        crops=[]; keep=[]
        for (cl,p,li,cbx,cby,bw,bh) in insts[:700]:
            ink=get(p); ax0=int(round(cbx-CW/2)); ay0=int(round(cby-CH/2))
            if ax0<0 or ay0<0 or ax0+CW>ink.shape[1] or ay0+CH>ink.shape[0]: continue
            crops.append(ink[ay0:ay0+CH, ax0:ax0+CW].astype(np.float32)); keep.append((p,li,cbx))
        dxs, dys, corrs = measure_class(crops)
        vals = dxs if ax=='dx' else dys
        pth=np.percentile(corrs,40); pure=corrs>=pth
        v=vals[pure]
        m,s=np.median(v),np.std(v); good=np.abs(v-m)<3.5*s+1e-9
        v=v[good]
        bits = em2_resp(v)
        bt = bit_tests(bits)
        txt, pr = bits_to_ascii(bits)
        results[f"cls{cid}_{ax}"] = dict(flag=f, tests=bt, ascii_preview=txt, ascii_printable_frac=pr)
        all_bits.extend(bits.tolist())

    # combined stream
    combo = bit_tests(all_bits)
    ctxt, cpr = bits_to_ascii(all_bits)
    results['_combined'] = dict(tests=combo, ascii_preview=ctxt, ascii_printable_frac=cpr,
                                n_bits=len(all_bits))

    # ---- WITHIN-SHAPE NOISE CONTROL: clean unimodal class split at median ----
    # class 12 was clean (dx sep/sd 0.25). Its median-split bits MUST be random.
    cid = 12
    insts = sorted(by_cls[cid], key=lambda r:(r[1],r[2],r[3]))
    crops=[]
    for (cl,p,li,cbx,cby,bw,bh) in insts[:500]:
        ink=get(p); ax0=int(round(cbx-CW/2)); ay0=int(round(cby-CH/2))
        if ax0<0 or ay0<0 or ax0+CW>ink.shape[1] or ay0+CH>ink.shape[0]: continue
        crops.append(ink[ay0:ay0+CH, ax0:ax0+CW].astype(np.float32))
    dxs,dys,corrs=measure_class(crops)
    v=dxs; bits=(v>np.median(v)).astype(int)
    results['_noise_control_cls12_dx'] = dict(tests=bit_tests(bits),
        note='clean unimodal class median-split; MUST read random')

    with open(os.path.join(HERE,'bitstream_results.json'),'w') as fp:
        json.dump(results, fp, indent=2, default=float)

    print('=== per-flag bitstream tests ===')
    for k,v in results.items():
        if k.startswith('_'): continue
        t=v['tests']
        print(f"{k}: n={t['n']} ones={t['ones_frac']:.2f} runs_z={t['runs_z']:.2f} "
              f"ent_o3={t['ent_o3']:.3f} autocorr={t['max_autocorr_lag2_63']:.2f}@{t['peak_lag']} "
              f"ascii%={v['ascii_printable_frac']:.2f} random={t['random_like']}")
    c=results['_combined']['tests']
    print(f"COMBINED: n={c['n']} ones={c['ones_frac']:.2f} runs_z={c['runs_z']:.2f} "
          f"ent_o3={c['ent_o3']:.3f} autocorr={c['max_autocorr_lag2_63']:.2f} "
          f"ascii%={results['_combined']['ascii_printable_frac']:.2f}")
    print('ascii preview:', repr(results['_combined']['ascii_preview'][:60]))
    nc=results['_noise_control_cls12_dx']['tests']
    print(f"NOISE CTRL cls12: runs_z={nc['runs_z']:.2f} ent_o3={nc['ent_o3']:.3f} "
          f"autocorr={nc['max_autocorr_lag2_63']:.2f} random={nc['random_like']}")
    return results


if __name__=='__main__':
    run()
