"""R44 / W2-C1 — THE FIGURAL-MOTIF CATALOG (agent classification pass).

Encodes the full dual-pass census: detector regions (results/detect.json, crops/) +
the agent full-page visual pass over all 56 relikd pages (run.log). Every read-class
entry cites its evidence crop or the full-page master. Count convention (fixed before
streams were computed): a unit = a recognizable depicted OBJECT (animal, cross, tree,
corpse); for abstract scrollwork, a unit = a maximal connected ink piece.

Taxonomy: read classes {cross, tree, corpse_figure, insect, emblem_circle, grid_square,
humanoid_other, other_figural}; excluded-from-reads classes carry covered_by.
Orientation: up/down/left/right/saltire/na.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)


def M(page, typ, sub, ori, cx, cy, evidence, note=""):
    return dict(page=page, cls=typ, subtype=sub, orientation=ori,
                centroid=[cx, cy], evidence=evidence, note=note)


motifs = []

# pp0-2: two large black three-bar (patriarchal) crosses, left cross low / right cross
# high, same plates all three pages; lemniscate squiggles above and below the text block.
for p in (0, 1, 2):
    motifs += [
        M(p, "cross", "three_bar_cross", "up", 300, 2320, "crops/p%02d_r01.png" % p if p == 0 else "crops/p%02d_r00.png" % p,
          "left margin, low; tilted slightly CCW; detector bbox [1682,2960,56,550]"),
        M(p, "cross", "three_bar_cross", "up", 2100, 1278, "crops/p%02d_r02.png" % p if p == 0 else "crops/p%02d_r01.png" % p,
          "right margin, high; detector bbox [640,1916,1852,2346]"),
        M(p, "other_figural", "lemniscate", "na", 1185, 630, "full-page %d (backstop; sub-detector size)" % p),
        M(p, "other_figural", "lemniscate", "na", 1185, 2965, "full-page %d (backstop)" % p),
    ]
# p2 extra: cicada, side view, facing right, lower third
motifs += [M(2, "insect", "cicada_side", "right", 1223, 2766, "crops/p02_r02.png")]

# pp3-7: vine scrolls, 2 connected pieces per margin (upper hook scroll, lower S scroll)
for p in (3, 4, 5, 6, 7):
    ev = "crops/p%02d_r00.png" % p
    ev2 = "crops/p%02d_r01.png" % p
    motifs += [
        M(p, "other_figural", "vine_scroll", "na", 374, 1100, ev, "left upper"),
        M(p, "other_figural", "vine_scroll", "na", 374, 2300, ev, "left lower"),
        M(p, "other_figural", "vine_scroll", "na", 2026, 1100, ev2, "right upper"),
        M(p, "other_figural", "vine_scroll", "na", 2026, 2300, ev2, "right lower"),
    ]

# pp8-14: single bare tree (roots at bottom), alternating margin L,R,L,R,L,R,L
for i, p in enumerate(range(8, 15)):
    left = (i % 2 == 0)
    motifs += [M(p, "tree", "bare_tree", "up", 286 if left else 2070, 1784,
                 "crops/p%02d_r00.png" % p, "margin %s" % ("left" if left else "right"))]
# p14 extra: mayfly in flight, side view, facing right
motifs += [M(14, "insect", "mayfly_side", "right", 1430, 2342, "crops/p14_r01.png")]

# p15: lemniscate between the number grid and the text
motifs += [M(15, "other_figural", "lemniscate", "na", 1151, 1604, "crops/p15_r00.png")]

# p22: beam bearing three upright crosses + the shrouded corpse at page bottom
for i, cx in enumerate((750, 980, 1490)):
    motifs += [M(22, "cross", "beam_cross", "up", cx, 2430, "crops/p22_r01.png",
                 "one of three crosses on a horizontal beam")]
motifs += [M(22, "corpse_figure", "shrouded_corpse", "right", 1200, 3370,
             "crops/p22_r00.png", "lying, head at right, page bottom, full width")]

# pp24-26: two mayflies per margin joined tail-to-tail (top one upright, bottom inverted)
for p in (24, 25, 26):
    motifs += [
        M(p, "insect", "mayfly_margin", "up", 240, 1480, "crops/p%02d_r00.png" % p, "left top"),
        M(p, "insect", "mayfly_margin", "down", 240, 2100, "crops/p%02d_r00.png" % p, "left bottom"),
        M(p, "insect", "mayfly_margin", "up", 2042, 1480, "crops/p%02d_r01.png" % p, "right top"),
        M(p, "insect", "mayfly_margin", "down", 2042, 2100, "crops/p%02d_r01.png" % p, "right bottom"),
    ]

# p27: single detached mayfly wing above the text
motifs += [M(27, "insect", "wing", "na", 1216, 686, "crops/p27_r00.png")]

# p32: the blurred tree (B4's blur forensics; catalogued here as a motif)
motifs += [M(32, "tree", "blurred_tree", "up", 1168, 2688, "crops/p32_r00.png")]

# pp40-54: root-vine (rooted scroll vine) both margins, same plates; p55 both margins
for p in list(range(40, 55)) + [55]:
    if p == 55:
        evL, evR = "crops/p55_r01.png", "crops/p55_r00.png"
    else:
        evL = "crops/p%02d_r0%d.png" % (p, 1 if p not in (50, 51, 53) else 0)
        evR = "crops/p%02d_r0%d.png" % (p, 0 if p not in (50, 51, 53) else 1)
    motifs += [
        M(p, "other_figural", "root_vine", "up", 300, 1816, evL, "left margin"),
        M(p, "other_figural", "root_vine", "up", 2100, 1816, evR, "right margin"),
    ]

# p53: cicada, wings spread, head up, page bottom
motifs += [M(53, "insect", "cicada_spread", "up", 1200, 2908, "crops/p53_r02.png")]
# p55: grey ghost tree (pale ink) + cicada wings spread
motifs += [M(55, "tree", "ghost_tree", "up", 1200, 1950, "crops/p55_r00.png",
             "pale/grey ink, caught by the pale mask inside merged region")]
motifs += [M(55, "insect", "cicada_spread", "up", 1244, 2936, "crops/p55_r00.png")]

# ---- excluded-from-reads catalog entries (presence recorded, no read) ----
excluded = [
    dict(pages=[0, 1, 2, 3, 6, 7, 8, 15, 23, 27, 33, 36, 37, 38, 39, 53, 54, 55, 22, 26, 32],
         cls="red_mark", covered_by="R44-P1 (red channel, wave 1)",
         note="red drop-caps/bind-runes/words/dot-matrices/numerals 1-5/closing paragraph"),
    dict(pages=[33, 34, 35, 36, 37, 38, 39], cls="cuneiform_cluster", covered_by="R44 W2-B2"),
    dict(pages=[7, 23, 33, 39, 22] + list(range(40, 56)), cls="dot_cluster",
         covered_by="R44 W2-B2 (incl. root-vine margin dot pairs/quintets)"),
    dict(pages=[15], cls="grid_square", covered_by="R44-P2 (p15 4x4 Arabic grid)",
         note="in read taxonomy but already read by wave-1 P2; excluded here"),
    dict(pages=[49, 50, 51], cls="latin_text_numeral", covered_by="A-06 / pp49-51 payload rows"),
]

catalog = dict(generated="2026-11-09", n_pages=56, motifs=motifs, excluded=excluded,
               count_convention="unit = depicted object; scrollwork = connected piece",
               orientation_values=["up", "down", "left", "right", "saltire", "na"])
os.makedirs(os.path.join(CELL, "results"), exist_ok=True)
json.dump(catalog, open(os.path.join(CELL, "results", "catalog.json"), "w"), indent=1)

# per-page feature vectors + streams
READ_CLASSES = ["cross", "tree", "corpse_figure", "insect", "emblem_circle",
                "grid_square", "humanoid_other", "other_figural"]
pages = {p: {c: 0 for c in READ_CLASSES} for p in range(56)}
for m in motifs:
    pages[m["page"]][m["cls"]] += 1
V1 = [sum(pages[p].values()) for p in range(56)]
V2 = {c: [pages[p][c] for p in range(56)] for c in READ_CLASSES
      if sum(1 for p in range(56) if pages[p][c] > 0) >= 3}
order = sorted(range(len(motifs)), key=lambda i: (motifs[i]["page"], motifs[i]["centroid"][1], motifs[i]["centroid"][0]))
T1 = [motifs[i]["cls"] for i in order]
O1 = [motifs[i]["orientation"] for i in order if motifs[i]["orientation"] != "na"]
CY = [(motifs[i]["page"], motifs[i]["centroid"][1]) for i in order]
streams = dict(V1=V1, V2=V2, T1=T1, O1=O1, centroid_y=CY,
               n_motifs=len(motifs), motif_pages=sorted({m["page"] for m in motifs}))
json.dump(streams, open(os.path.join(CELL, "results", "streams.json"), "w"), indent=1)
print("motifs:", len(motifs), "| motif pages:", len(streams["motif_pages"]))
print("V1 =", V1)
print("V2 classes:", list(V2.keys()))
print("O1 (%d):" % len(O1), O1)
print("T1 (%d)" % len(T1))
