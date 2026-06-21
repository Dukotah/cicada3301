import sys, numpy as np
sys.path.insert(0,'analysis/structure')
import seg

def segment_page(path, verbose=False):
    ink = seg.load_ink(path)
    H, W = ink.shape
    x0, x1 = seg.central_text_window(ink)
    bands = seg.line_bands(ink, x0, x1)
    glyphs = []
    for (ry0, ry1) in bands:
        band_h = ry1 - ry0
        line_ink = ink[ry0:ry1, x0:x1]
        cols = seg.glyph_cols(line_ink)
        for (cx0, cx1) in cols:
            w = cx1 - cx0
            # crop within band, then trim rows
            sub = line_ink[:, cx0:cx1]
            ys = np.where(sub.any(axis=1))[0]
            if len(ys)==0: continue
            gh = ys.max()-ys.min()+1
            area = sub.sum()
            glyphs.append(dict(band=(ry0,ry1), x=(x0+cx0,x0+cx1), w=w, h=gh,
                               band_h=band_h, area=int(area), sub=sub))
    return glyphs, bands, ink

def classify(glyphs):
    # decide which segments are real runes vs separators/decoration
    ws=[g['w'] for g in glyphs]; hs=[g['h'] for g in glyphs]
    med_w=np.median(ws); med_h=np.median(hs)
    return med_w, med_h

if __name__=='__main__':
    import sys
    path=sys.argv[1]
    glyphs,bands,ink=segment_page(path)
    med_w,med_h=classify(glyphs)
    print(path)
    print('bands',len(bands),'segments',len(glyphs),'med_w',med_w,'med_h',med_h)
    # histogram of widths and heights
    import collections
    print('band heights:', [b[1]-b[0] for b in bands])
    for g in glyphs[:40]:
        print(f"  w={g['w']:3d} h={g['h']:3d} bh={g['band_h']:3d} area={g['area']:4d} x={g['x']}")
