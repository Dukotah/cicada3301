import os, re, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import run_all as R
from lp import gematria as gp

CROPS = R.CROPS
OUT = R.OUT


def ncc(a, b):
    af = a.astype(np.float32).ravel(); bf = b.ravel().astype(np.float32)
    af -= af.mean(); bf -= bf.mean()
    na = np.linalg.norm(af); nb = np.linalg.norm(bf)
    return 0.0 if na == 0 or nb == 0 else float(af.dot(bf) / (na * nb))


def main():
    canon = R.canon_page_lines()
    # collect all segmentations + aligned set
    page_seg = {}
    aligned = []
    for pi in range(56):
        path = os.path.join(R.RELIKD, f"p{pi}.jpg")
        if not os.path.exists(path):
            continue
        seg, ink = R.segment_page_lines(path)
        page_seg[pi] = (seg, ink, path)
        cpls = canon[pi] if pi < len(canon) else []
        for li in range(min(len(seg), len(cpls))):
            gl = seg[li][0]; cl = cpls[li]
            if len(gl) == len(cl):
                for idx, (g, r) in enumerate(zip(gl, cl)):
                    aligned.append((pi, li, idx, g, gp.RUNE_TO_IDX[r]))
    # templates
    acc = {i: [] for i in range(29)}
    for (pi, li, idx, g, lab) in aligned:
        acc[lab].append(g["norm"].astype(np.float32))
    T = {i: np.mean(acc[i], 0) for i in range(29) if acc[i]}

    def match(norm):
        sc = sorted(((ncc(norm, t), i) for i, t in T.items()), reverse=True)
        return sc[0][1], sc[0][0], sc[0][0] - (sc[1][0] if len(sc) > 1 else 0)

    # round-trip accuracy
    cor = sum(1 for (_, _, _, g, lab) in aligned if match(g["norm"])[0] == lab)
    acc_solved = cor / len(aligned) if aligned else 0.0

    # write independent transcription: best match per glyph, all pages, by line
    total = 0
    with open(os.path.join(OUT, "template_transcription.txt"), "w",
              encoding="utf-8") as f:
        f.write("# Independent image-derived transcription (template matching)\n")
        f.write("# WARNING: matcher round-trip accuracy on aligned glyphs = "
                f"{acc_solved:.3f} (<0.90 usable bar) -- LOW CONFIDENCE.\n")
        f.write("# segmentation is approximate; per-line glyph counts often "
                "disagree with canon, so absolute alignment is unreliable.\n")
        for pi in range(56):
            if pi not in page_seg:
                continue
            seg = page_seg[pi][0]
            f.write(f"% p{pi}\n")
            for (gl, band) in seg:
                runes = []
                for g in gl:
                    mi, scv, mar = match(g["norm"])
                    runes.append(gp.IDX_TO_RUNE[mi])
                    total += 1
                f.write("".join(runes) + "\n")
    # disagreement diff on aligned glyphs (alignment defined)
    disagreements = []
    hi = 0
    for (pi, li, idx, g, lab) in aligned:
        mi, scv, mar = match(g["norm"])
        if mi != lab:
            crop_path = ""
            highconf = (mar > 0.12 and scv > 0.55)
            if highconf and hi < 60:
                ink = page_seg[pi][1]
                c = ink[g["y0"]:g["y1"] + 1, g["x0"]:g["x1"] + 1]
                im = Image.fromarray(((~c) * 255).astype(np.uint8))
                crop_path = os.path.join(CROPS, f"p{pi}_l{li}_i{idx}.png")
                im.save(crop_path)
            if highconf:
                hi += 1
            disagreements.append(dict(
                page=pi, line=li, index=idx,
                canonical=gp.IDX_TO_TRANS[lab],
                matched=gp.IDX_TO_TRANS[mi],
                matchConfidence=round(scv, 3), margin=round(mar, 3),
                cropPath=crop_path, highConf=highconf))
    # sort: high-conf and high-margin first
    disagreements.sort(key=lambda d: (d["highConf"], d["margin"]), reverse=True)
    json.dump(dict(matcherAccuracy=acc_solved, totalAligned=len(aligned),
                   totalGlyphs=total, nDisagree=len(disagreements),
                   nHigh=hi, disagreements=disagreements[:200]),
              open(os.path.join(OUT, "disagreements.json"), "w"), indent=1)
    print(f"matcher_acc={acc_solved:.4f} aligned={len(aligned)} "
          f"total_glyphs={total} disagree={len(disagreements)} highconf={hi}")
    return acc_solved, len(aligned), total, disagreements, hi


if __name__ == "__main__":
    main()
