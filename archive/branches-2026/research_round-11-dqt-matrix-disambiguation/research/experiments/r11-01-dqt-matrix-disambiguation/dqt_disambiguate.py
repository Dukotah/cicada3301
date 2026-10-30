#!/usr/bin/env python3
"""R11: DQT-matrix disambiguation. Executes the pre-registration exactly. Deterministic (no RNG).
Part A: dump + relate the two DQT matrices (Annex-K quality fit). Part B: direct ink-coverage
complexity proxy + Mann-Whitney between DQT groups. Writes results.json."""
import json, struct, glob, os, re, io, math

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RELIKD = os.path.join(REPO, "liber-primus", "data", "relikd")
R8 = os.path.join(REPO, "research", "experiments", "r8-02-dqt-page-membership", "results.json")

ZIGZAG = [
 0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,
 35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63]

ANNEX_K_LUMA = [
 16,11,10,16,24,40,51,61, 12,12,14,19,26,58,60,55, 14,13,16,24,40,57,69,56, 14,17,22,29,51,87,80,62,
 18,22,37,56,68,109,103,77, 24,35,55,64,81,104,113,92, 49,64,78,87,103,121,120,101, 72,92,95,98,112,100,103,99]
ANNEX_K_CHROMA = [
 17,18,24,47,99,99,99,99, 18,21,26,66,99,99,99,99, 24,26,56,99,99,99,99,99, 47,66,99,99,99,99,99,99,
 99,99,99,99,99,99,99,99, 99,99,99,99,99,99,99,99, 99,99,99,99,99,99,99,99, 99,99,99,99,99,99,99,99]

def parse_dqt(path):
    """Return {table_id: [64 coeffs in natural (row-major) order]}."""
    with open(path, "rb") as f:
        data = f.read()
    i = 2; tables = {}
    while i < len(data) - 1:
        if data[i] != 0xFF: i += 1; continue
        m = data[i+1]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7: i += 2; continue
        if m == 0xDA: break
        seglen = struct.unpack(">H", data[i+2:i+4])[0]
        seg = data[i+4:i+2+seglen]
        if m == 0xDB:  # DQT
            p = 0
            while p < len(seg):
                pq = seg[p] >> 4; tq = seg[p] & 0xF; p += 1
                n = 128 if pq else 64
                raw = seg[p:p+n]; p += n
                coeffs = list(raw) if not pq else [struct.unpack(">H", raw[k:k+2])[0] for k in range(0,n,2)]
                nat = [0]*64
                for zi, natidx in enumerate(ZIGZAG): nat[natidx] = coeffs[zi]
                tables[tq] = nat
        i += 2 + seglen
    return tables

def fit_annexk(observed, base):
    """Best libjpeg quality Q (1..100) whose scaled Annex-K base matches observed; return (Q, rms_resid)."""
    best = (None, 1e18)
    for Q in range(1, 101):
        scale = (5000.0/Q) if Q < 50 else (200 - 2*Q)
        pred = [min(255, max(1, int((b*scale + 50)//100))) for b in base]
        rms = math.sqrt(sum((pred[k]-observed[k])**2 for k in range(64))/64.0)
        if rms < best[1]: best = (Q, rms)
    return best

def mannwhitney(a, b):
    comb = sorted([(v,0) for v in a]+[(v,1) for v in b])
    ranks=[0.0]*len(comb); i=0
    while i < len(comb):
        j=i
        while j+1<len(comb) and comb[j+1][0]==comb[i][0]: j+=1
        r=(i+j)/2.0+1
        for k in range(i,j+1): ranks[k]=r
        i=j+1
    Ra=sum(ranks[k] for k in range(len(comb)) if comb[k][1]==0)
    na,nb=len(a),len(b)
    Ua=Ra-na*(na+1)/2.0; Ub=na*nb-Ua; U=min(Ua,Ub)
    mu=na*nb/2.0; sd=math.sqrt(na*nb*(na+nb+1)/12.0)
    z=(U-mu)/sd if sd else 0.0
    p=math.erfc(abs(z)/math.sqrt(2))
    rank_biserial = 1 - 2*Ua/(na*nb)   # effect size
    return dict(U=U, z=z, p=p, rank_biserial=rank_biserial)

def ink_coverage(path, width=800, thr=128):
    from PIL import Image
    im = Image.open(path).convert("L")
    w,h = im.size
    if w > width:
        im = im.resize((width, max(1,int(h*width/w))))
    px = im.tobytes()
    dark = sum(1 for v in px if v < thr)
    return dark/len(px)

def pageno(fn): return int(re.search(r"p(\d+)\.jpg", fn).group(1))

def main():
    r8 = json.load(io.open(R8, encoding="utf-8"))
    membership = {int(k):v for k,v in r8["membership_by_page"].items()}
    groups = sorted(set(membership.values()))
    g0, g1 = groups
    paths = {pageno(os.path.basename(p)): p for p in glob.glob(os.path.join(RELIKD, "p*.jpg"))}

    # Part A: verify intra-group identity + dump matrices
    def rep_page(g): return sorted(pg for pg,fp in membership.items() if fp==g)[0]
    dqt_g0 = parse_dqt(paths[rep_page(g0)])
    dqt_g1 = parse_dqt(paths[rep_page(g1)])
    # intra-group identity check (hash the concatenated tables)
    import hashlib
    def tabhash(t): return hashlib.sha256(str([t[k] for k in sorted(t)]).encode()).hexdigest()[:12]
    intra = {}
    for g in groups:
        hs = set()
        for pg,fp in membership.items():
            if fp==g: hs.add(tabhash(parse_dqt(paths[pg])))
        intra[g] = {"n": sum(1 for fp in membership.values() if fp==g), "unique_table_hashes": len(hs)}

    fitA = {"luma": fit_annexk(dqt_g0[0], ANNEX_K_LUMA), "chroma": fit_annexk(dqt_g0.get(1,dqt_g0[0]), ANNEX_K_CHROMA)}
    fitB = {"luma": fit_annexk(dqt_g1[0], ANNEX_K_LUMA), "chroma": fit_annexk(dqt_g1.get(1,dqt_g1[0]), ANNEX_K_CHROMA)}
    # element-wise ratio g1/g0 luma (constant => uniform scale relationship)
    ratios = [dqt_g1[0][k]/dqt_g0[0][k] for k in range(64) if dqt_g0[0][k]]
    ratio_mean = sum(ratios)/len(ratios)
    ratio_cv = (math.sqrt(sum((r-ratio_mean)**2 for r in ratios)/len(ratios))/ratio_mean) if ratio_mean else None
    both_annexk = fitA["luma"][1] < 2.0 and fitB["luma"][1] < 2.0
    relationship = ("two_quality_settings_of_annexK_base" if both_annexk
                    else "structurally_distinct_or_non_annexK")

    # Part B: ink coverage + MW
    ink = {pg: ink_coverage(paths[pg]) for pg in sorted(paths)}
    sizes = {pageno(os.path.basename(e["file"])): e["size"] for e in json.load(io.open(
        os.path.join(REPO,"liber-primus","analysis","stego","out_authentic","results.json"),encoding="utf-8"))}
    ink0=[ink[pg] for pg in ink if membership[pg]==g0]; ink1=[ink[pg] for pg in ink if membership[pg]==g1]
    sz0=[sizes[pg] for pg in sizes if membership.get(pg)==g0]; sz1=[sizes[pg] for pg in sizes if membership.get(pg)==g1]
    mw_ink = mannwhitney(ink0, ink1)
    mw_size = mannwhitney(sz0, sz1)

    complexity_differs = mw_ink["p"] < 0.05
    verdict = "NEGATIVE (content/complexity-driven split)" if complexity_differs else \
              "SURVIVES (positional split not complexity-explained; benign production signal, zero cipher bearing)"

    med=lambda x: sorted(x)[len(x)//2]
    out = {
        "experiment": "r11-01-dqt-matrix-disambiguation",
        "groups": {g0: intra[g0], g1: intra[g1]},
        "partA_dqt_matrices": {
            g0: {"luma_natural_order": dqt_g0[0], "chroma_natural_order": dqt_g0.get(1)},
            g1: {"luma_natural_order": dqt_g1[0], "chroma_natural_order": dqt_g1.get(1)},
            "annexK_bestfit_quality": {g0: {"luma_Q":fitA["luma"][0],"luma_rms":round(fitA["luma"][1],3),
                                            "chroma_Q":fitA["chroma"][0],"chroma_rms":round(fitA["chroma"][1],3)},
                                       g1: {"luma_Q":fitB["luma"][0],"luma_rms":round(fitB["luma"][1],3),
                                            "chroma_Q":fitB["chroma"][0],"chroma_rms":round(fitB["chroma"][1],3)}},
            "g1_over_g0_luma_ratio_mean": round(ratio_mean,4), "g1_over_g0_luma_ratio_cv": round(ratio_cv,4) if ratio_cv else None,
            "relationship": relationship,
        },
        "partB_complexity": {
            "ink_coverage_median": {g0: round(med(ink0),5), g1: round(med(ink1),5)},
            "mannwhitney_ink": mw_ink,
            "byte_size_median": {g0: med(sz0), g1: med(sz1)},
            "mannwhitney_bytesize": mw_size,
            "complexity_differs_p_lt_0.05": complexity_differs,
        },
        "VERDICT": verdict,
    }
    outp = os.path.join(os.path.dirname(__file__), "results.json")
    json.dump(out, io.open(outp,"w",encoding="utf-8"), indent=2)
    # console summary
    print("Part A relationship:", relationship)
    print(f"  {g0} luma Annex-K Q={fitA['luma'][0]} (rms {fitA['luma'][1]:.2f}) | {g1} luma Q={fitB['luma'][0]} (rms {fitB['luma'][1]:.2f})")
    print(f"  g1/g0 luma ratio mean={ratio_mean:.3f} cv={ratio_cv:.3f}")
    print(f"  intra-group unique table hashes: {g0}={intra[g0]['unique_table_hashes']} {g1}={intra[g1]['unique_table_hashes']}")
    print("Part B complexity:")
    print(f"  ink median {g0}={med(ink0):.4f} {g1}={med(ink1):.4f} | MW U={mw_ink['U']} p={mw_ink['p']:.4f} rb={mw_ink['rank_biserial']:.3f}")
    print(f"  bytesize MW p={mw_size['p']:.4f}")
    print("VERDICT:", verdict)

if __name__ == "__main__":
    main()
