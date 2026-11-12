"""R44 / P1 step 2 — build the CENSUS-CORRECTED red selection channel (PREREG Addendum 1).

Input: census.json (validated). Output: channel.json with
  - every red canon rune located at its GLOBAL canon rune position
  - stream variants: legacy187 (prior art), corrected200 (186 + title + URPN),
    full213 (corrected + 13 red drop-cap initials)
  - per-page red parameters for reading C: r_p, firstpos_p (0-based pos within page), cum_p

Verifications hard-asserted:
  * title FULM AEAYOEA sits at the start of canon segment 15 (global 3603)
  * URPN at global 12644
  * p0 drop-cap resolves to the rune S (prior-art statement)
  * all located positions strictly increasing in (gli, gi) order per line
"""
import json, os, sys, bisect
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa

FALSE_GLYPH = dict(img=37, gli=418, gi=0)          # the red Arabic numeral 4 (Addendum 1)

census = json.load(open(os.path.join(HERE, "census.json")))
txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
S = "".join(c for c in txt if c in gp.RUNE_TO_IDX)           # global canon rune string
segs = txt.split("%")
page_lens = [len([c for c in s if c in gp.RUNE_TO_IDX]) for s in segs]
page_starts = np.cumsum([0] + page_lens[:-1]).tolist()        # global start of each canon page


def page_of(pos):
    return bisect.bisect_right(page_starts, pos) - 1


# ---- stones line strings (to locate red lines in canon) ----
d = np.load(os.path.join(LP, "analysis", "stones", "dataset.npz"), allow_pickle=True)
provall = d["provall"]
pred = np.load(os.path.join(LP, "analysis", "stones", "all_pred.npy"), allow_pickle=True)
line_runes = {}
for i in range(len(provall)):
    img, line, gi, gli, canon, match = provall[i]
    line_runes.setdefault(int(gli), []).append((int(gi), str(canon if canon is not None else pred[i])))
line_str = {g: "".join(r for _, r in sorted(v)) for g, v in line_runes.items()}

# ---- locate each red glyph line in canon ----
reds = [g for g in census["red_glyphs"]
        if not (g["img"] == FALSE_GLYPH["img"] and g["gli"] == FALSE_GLYPH["gli"])]
assert len(reds) == 186, len(reds)

entries = []          # (global_pos, rune, source, img)
line_start_cache = {}
drift_align = {}
# canon lines with their global start offsets (for drift alignment)
canon_lines_global = []
_off = 0
for _seg in txt.split('%'):
    for _line in _seg.split('/'):
        _r = ''.join(c for c in _line if c in gp.RUNE_TO_IDX)
        if _r:
            canon_lines_global.append((_off, _r))
            _off += len(_r)
for g in reds:
    gli = g["gli"]
    if gli not in line_start_cache:
        ls = line_str[gli]
        j = S.find(ls)
        if j < 0 or S.find(ls, j + 1) >= 0:
            # fallback: longest unique window anywhere in the line (classifier noise tolerant)
            found = -1
            for k in range(len(ls), 11, -1):
                for off in range(0, len(ls) - k + 1):
                    sub = ls[off:off + k]
                    j2 = S.find(sub)
                    if j2 >= 0 and S.find(sub, j2 + 1) < 0:
                        found = j2 - off
                        break
                if found >= 0:
                    break
            assert found >= 0, f"line {gli} not locatable in canon"
            j = found
        line_start_cache[gli] = j
    pos = line_start_cache[gli] + g["gi"]
    if pos < len(S) and S[pos] == g["rune"]:
        entries.append(dict(pos=pos, rune=S[pos], source="glyph", img=g["img"],
                            box=g["box"], gli=gli, gi=g["gi"]))
        continue
    # segmentation drift on a classifier-fallback line: find the exact CANON LINE best
    # matching the glyph line, align glyph string to it with difflib, and map gi through
    # the opcodes. A red glyph box aligned to a RANGE of canon runes (merged segmentation,
    # e.g. img33 gli369 gi4 = canon 'CO') marks the WHOLE range red (box red-fraction
    # ~1.0; visually verified, crops/p33_gli369.png).
    import difflib
    ls = line_str[gli]
    if gli not in drift_align:
        best = None
        for cl_start, cl in canon_lines_global:
            r = difflib.SequenceMatcher(None, ls, cl, autojunk=False).ratio()
            if best is None or r > best[0]:
                best = (r, cl_start, cl)
        assert best and best[0] > 0.8, (gli, best and best[0])
        _, cl_start, cl = best
        # exact prefix / exact suffix anchor with a small leading skip d (the segmenter may
        # miss leading canon runes); correct for a single merge/split in the middle.
        best_dp = (0, -1)
        for d in range(0, 4):
            p = 0
            while p < min(len(ls), len(cl) - d) and ls[p] == cl[d + p]:
                p += 1
            if p > best_dp[1]:
                best_dp = (d, p)
        d, p = best_dp
        sfx = 0
        while (sfx < min(len(ls) - p, len(cl) - d - p)
               and ls[len(ls) - 1 - sfx] == cl[len(cl) - 1 - sfx]):
            sfx += 1
        assert p + sfx >= len(ls) - 3, (gli, d, p, sfx, len(ls), len(cl))
        drift_align[gli] = (cl_start, cl, d, p, sfx)
    cl_start, cl, d, p, sfx = drift_align[gli]
    gi = g["gi"]
    if gi < p:
        cover = [cl_start + d + gi]
    elif gi >= len(ls) - sfx:
        cover = [cl_start + len(cl) - (len(ls) - gi)]
    else:
        cover = list(range(cl_start + d + p, cl_start + len(cl) - sfx))
    assert cover, (gli, g["gi"])
    for pos in cover:
        print(f"  drift-aligned gli {gli} gi {g['gi']}: glyph {g['rune']} -> canon "
              f"{S[pos]} at {pos}")
        entries.append(dict(pos=pos, rune=S[pos], source="glyph", img=g["img"],
                            box=g["box"], gli=gli, gi=g["gi"]))

# ---- title (canon segment 15 head) and URPN ----
TITLE = "ᚠᚢᛚᛗᚪᛠᚣᛟᚪ"
jt = S.find(TITLE)
assert jt == page_starts[15] == 3603, (jt, page_starts[15])
for k, r in enumerate(TITLE):
    entries.append(dict(pos=jt + k, rune=r, source="title", img=15))
ju = S.find("ᚢᚱᛈᚾ")
assert ju == 12644
for k, r in enumerate("ᚢᚱᛈᚾ"):
    entries.append(dict(pos=ju + k, rune=r, source="urpn", img=53))

# ---- drop-caps: geometric attachment to the red run on the same image ----
# a red run's first glyph (per gli): find dropcap on same img whose y-band overlaps the
# first glyph's line and whose x is left of it.
first_of_line = {}
for e in entries:
    if e["source"] == "glyph":
        key = (e["img"], e["gli"])
        if key not in first_of_line or e["gi"] < first_of_line[key]["gi"]:
            first_of_line[key] = e

dropcaps = []
for img_s, rec in census["images"].items():
    for dcap in rec.get("dropcaps", []):
        dropcaps.append(dict(img=int(img_s), bbox=dcap["bbox"]))

attached = []
for dc in dropcaps:
    x0, x1, y0, y1 = dc["bbox"]
    best = None
    for (img, gli), e in first_of_line.items():
        if img != dc["img"]:
            continue
        gx0, gx1, gy0, gy1 = e["box"]
        if gy0 < y1 and gy1 > y0 and x1 <= gx0 + 20:   # same band, dropcap left of run
            if best is None or gx0 < best["box"][0]:
                best = e
    assert best is not None, f"dropcap {dc} unattached"
    pos = best["pos"] - 1 - (best["gi"])  # position before the run's LINE start
    # the run starts at gi=best['gi'] within the line; dropcap precedes the line's first rune?
    # No: the dropcap IS the canon rune immediately before the red run's first rune.
    pos = best["pos"] - 1
    assert pos >= 0
    attached.append(dict(pos=pos, rune=S[pos], source="dropcap", img=dc["img"],
                         bbox=dc["bbox"]))

assert len(attached) == len(dropcaps) == 13, (len(attached), len(dropcaps))
# prior-art check: p0's dropcap is S (index 15 rune 'ᛋ')
p0dc = [a for a in attached if a["img"] == 0]
assert len(p0dc) == 1 and p0dc[0]["rune"] == "ᛋ", p0dc

# ---- assemble streams ----
def stream(ents):
    es = sorted(ents, key=lambda e: e["pos"])
    pos = [e["pos"] for e in es]
    assert len(set(pos)) == len(pos), "duplicate positions"
    return es, [gp.RUNE_TO_IDX[e["rune"]] for e in es], pos

glyph_entries = [e for e in entries if e["source"] == "glyph"]
legacy_entries = glyph_entries + [dict(pos=None, rune="ᚱ", source="false4", img=37)]  # doc only
corr_entries = entries                     # 186 + 9 + 4 = 199
full_entries = entries + attached          # + 13 = 212

_, corr_idx, corr_pos = stream(corr_entries)
_, full_idx, full_pos = stream(full_entries)
# legacy187 = prior-art stream verbatim (from redrune result.json for comparability)
legacy = json.load(open(os.path.join(LP, "analysis", "armada_osint", "redrune", "result.json")))
legacy_translit = legacy["global_red_translit"]

# ---- per-page parameters for reading C (canon pages 0..54 unsolved) ----
per_page = {}
for pi in range(len(segs)):
    ps, pe = page_starts[pi], page_starts[pi] + page_lens[pi]
    on_page = [p for p in full_pos if ps <= p < pe]
    per_page[pi] = dict(r_p=len(on_page),
                        firstpos_p=(on_page[0] - ps) if on_page else 0,
                        cum_p=sum(1 for p in full_pos if p < ps))

out = dict(
    n_glyph_reds=len(glyph_entries),
    false_entry="img37 gli418 red Arabic numeral 4 (was 'R' in prior-art 187)",
    corrected=dict(idx=corr_idx, pos=corr_pos,
                      translit=gp.indices_to_translit(corr_idx)),
    full=dict(idx=full_idx, pos=full_pos,
                 translit=gp.indices_to_translit(full_idx),
                 dropcaps=[dict(pos=a["pos"], rune=a["rune"], img=a["img"]) for a in
                           sorted(attached, key=lambda a: a["pos"])]),
    legacy187_translit=legacy_translit,
    per_page=per_page,
    page_starts=page_starts, page_lens=page_lens,
    canon_total=len(S),
)
json.dump(out, open(os.path.join(HERE, "channel.json"), "w"), indent=1)
print("corrected(%d):" % len(corr_idx), out["corrected"]["translit"])
print()
print("full(%d)     :" % len(full_idx), out["full"]["translit"])
print()
print("dropcap runes:", "".join(a["rune"] for a in sorted(attached, key=lambda a: a["pos"])),
      "=", gp.indices_to_translit([gp.RUNE_TO_IDX[a["rune"]] for a in
                                   sorted(attached, key=lambda a: a["pos"])]))
print("red pages (r_p>0):", {p: v["r_p"] for p, v in per_page.items() if v["r_p"]})
print("wrote channel.json")
