"""L3 step 3 — controls + characterize WHAT the anomaly actually is.

(A) Positive control: embed a known message into a clean JPEG with outguess, then
    read it back, proving the extraction pipeline works when a payload exists.
(B) Negative control: a synthetic clean JPEG (uniform + noise) run through the same
    interior mask + bitstream reader must produce null (no mask pixels, noise-floor
    entropy). Report the JPEG-LSB bias baseline.
(C) Characterize the 107/229 anomaly: is R-G a DC offset (constant push = decoration)
    or a modulated per-pixel value (could carry data)? Histogram of R-G over mask;
    fraction where R>G; per-region constancy.
"""
import os, subprocess, json, math
import numpy as np
from PIL import Image

OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round29/L3-chroma-bitstream"

def byte_entropy(bs):
    if not bs: return 0.0
    c = np.bincount(np.frombuffer(bs, np.uint8), minlength=256); p = c / c.sum(); p = p[p>0]
    return float(-(p*np.log2(p)).sum())

# ---------- (C) anomaly characterization ----------
def characterize_anomaly(name):
    rgb = np.load(os.path.join(OUT, f"rgb_{name}.npy")).astype(np.int16)
    R, G = rgb[...,0], rgb[...,1]
    mask = np.load(os.path.join(OUT, f"mask_{name}.npy"))
    RmG = (R - G)[mask]
    hist = {int(v): int(c) for v, c in zip(*np.unique(RmG, return_counts=True))}
    # top-5 most common R-G values
    top = sorted(hist.items(), key=lambda kv: -kv[1])[:8]
    return {
        "image": name,
        "mask_px": int(mask.sum()),
        "RmG_mean": round(float(RmG.mean()), 3),
        "RmG_std": round(float(RmG.std()), 3),
        "RmG_pos_frac": round(float((RmG > 0).mean()), 4),
        "RmG_neg_frac": round(float((RmG < 0).mean()), 4),
        "RmG_top_values(value:count)": top,
        # entropy of the R-G value stream itself (is the modification's amplitude a signal?)
        "RmG_value_entropy_bits": round(byte_entropy(((RmG.clip(-128,127)+128).astype(np.uint8)).tobytes()), 3),
    }

# ---------- (B) negative control: clean synthetic JPEG ----------
def make_clean_jpeg(path, seed=1):
    rng = np.random.default_rng(seed)
    a = np.full((3600, 2400, 3), 240, np.uint8)  # light paper
    # add some dark strokes so 'ink' mask is nonempty, but chroma-neutral (R==G==B)
    for _ in range(400):
        y = rng.integers(0, 3560); x = rng.integers(0, 2360)
        v = rng.integers(20, 60)
        a[y:y+rng.integers(5,40), x:x+rng.integers(2,8)] = v
    a = (a.astype(int) + rng.integers(-2, 3, a.shape)).clip(0,255).astype(np.uint8)
    Image.fromarray(a).save(path, quality=90)

def clean_negative():
    p = os.path.join(OUT, "clean_neg.jpg")
    make_clean_jpeg(p)
    im = np.asarray(Image.open(p).convert("RGB")).astype(np.int16)
    R, G, B = im[...,0], im[...,1], im[...,2]
    L = 0.299*R+0.587*G+0.114*B
    ink = L < (L.mean()-1.0*L.std())
    RmG = np.abs(R-G)
    interior_RmG = RmG[ink].mean() if ink.sum() else 0
    mask_px = int((ink & (RmG>5)).sum())
    # full-interior LSB baseline entropy
    iy, ix = np.where(ink)
    bitsR = (R[iy,ix] & 1).astype(np.uint8)
    n = (len(bitsR)//8)*8
    bs = np.packbits(bitsR[:n]).tobytes()
    return {
        "clean_neg_abs_RmG_ink_mean": round(float(interior_RmG),4),
        "clean_neg_mask_px(RmG>5)": mask_px,
        "clean_neg_lsbR_byteH": round(byte_entropy(bs),3),
        "clean_neg_lsbR_ones_frac": round(float(bitsR.mean()),4),
    }

# ---------- (A) positive control: outguess embed+extract ----------
def positive_outguess():
    msg = b"L3 POSITIVE CONTROL: hidden payload 3301 the reader works"
    src = os.path.join(OUT, "clean_neg.jpg")  # reuse the clean carrier
    if not os.path.exists(src): make_clean_jpeg(src)
    msgf = os.path.join(OUT, "pc_msg.txt"); open(msgf,"wb").write(msg)
    stego = os.path.join(OUT, "pc_stego.jpg")
    outf = os.path.join(OUT, "pc_extract.txt")
    res = {}
    try:
        e = subprocess.run(["outguess","-d",msgf,src,stego],capture_output=True,timeout=120)
        res["embed_rc"] = e.returncode; res["embed_err"] = e.stderr.decode()[-200:]
        x = subprocess.run(["outguess","-r",stego,outf],capture_output=True,timeout=120)
        res["extract_rc"] = x.returncode
        got = open(outf,"rb").read() if os.path.exists(outf) else b""
        res["recovered"] = got.decode("latin1")[:80]
        res["roundtrip_ok"] = (got == msg)
    except Exception as ex:
        res["error"] = str(ex)
    return res

if __name__ == "__main__":
    out = {"anomaly": [characterize_anomaly(n) for n in ("dl_107.jpg","dl_229.jpg","dl_167.jpg")],
           "negative_control": clean_negative(),
           "positive_control": positive_outguess()}
    print(json.dumps(out, indent=2))
    json.dump(out, open(os.path.join(OUT,"controls_results.json"),"w"), indent=2)
