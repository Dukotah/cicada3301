"""R45/S1 adjudication. Run from anywhere:  PYTHONUTF8=1 python adjudicate.py

1. Records sha256 + mtime of blind_reads.json BEFORE opening sealed_manifest.json.
2. Exact-box items: checks the crop's line registration against corrected_map.json. If the committed
   alignment put the crop on a different canon line (false-exact), the glyph actually shown is
   canon[true_line][j]; the item is scored against that ('crop_canon') and flagged 'misregistered'.
3. Window items: the strip read is aligned (difflib, rune tokens) to the TRUE canon line of the image line
   the strip was cut from; the target's read is the aligned token (if the target falls in an equal or
   equal-length replace block), else 'unresolved'.
4. Every item whose read != crop canon is listed for unblinded re-inspection; verdicts come from
   reinspect.json (written by hand after looking at the zoom crops) and are merged here.
Outputs: adjudications.json, adjudicate.log
"""
import difflib
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "stones"))
from lp import gematria as gp  # noqa: E402

os.chdir(LP)
import pipeline as P  # noqa: E402

T = gp.RUNE_TO_TRANS
T2R = {v: k for k, v in T.items()}
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


br = os.path.join(HERE, "blind_reads.json")
log("blind_reads.json sha256", hashlib.sha256(open(br, "rb").read()).hexdigest(),
    "mtime", time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(br))))
reads = json.load(open(br))["reads"]
sealed = json.load(open(os.path.join(HERE, "sealed_manifest.json"), encoding="utf-8"))
meta, items = sealed, sealed["items"]
relabel = json.load(open(os.path.join(HERE, "controls_relabel.json"), encoding="utf-8"))["items"]
cmap = json.load(open(os.path.join(HERE, "corrected_map.json")))
align = json.load(open("analysis/stones/alignment.v1.json"))
sreg = json.load(open(os.path.join(HERE, "strip_registration.json")))  # addendum A5
reinspect = {}
rp = os.path.join(HERE, "reinspect.json")
if os.path.exists(rp):
    reinspect = json.load(open(rp, encoding="utf-8"))
gl, po = P.global_lines()
flat = [c for L in gl for c in L]
pos_map = [(li, j) for li, L in enumerate(gl) for j in range(len(L))]


def clean_index(gline):
    """(image, clean_i) the build used for canon line gline (positional pairing with alignment.json)."""
    for n in range(56):
        al = align[str(n)]
        if gline in al:
            return n, al.index(gline)
    return None, None


def true_line(gline):
    n, ci = clean_index(gline)
    if n is None:
        return None, None
    rows = cmap[str(n)]
    if ci >= len(rows):
        return n, None
    return n, rows[ci]["true_gline"]


def crop_canon_at(gpos):
    """What canon rune is actually in the exact-box crop made for gpos (None if not determinable)."""
    li, j = pos_map[gpos]
    n, tl = true_line(li)
    if tl is None:
        return None, "unregistered"
    if tl == li:
        return flat[gpos], "ok"
    if j < len(gl[tl]):
        return gl[tl][j], f"misregistered(true_line={tl})"
    return None, f"misregistered(true_line={tl})"


def window_target(gpos, strip, reg_key):
    """A5: the strip is registered by its own blind read (strip_registration.json); if it registers to the
    target's line, align strip tokens to that line and return the read for gpos."""
    li, j = pos_map[gpos]
    reg = sreg.get(reg_key)
    if reg is None or not reg["registered"]:
        return None, f"misregistered(strip_best_line={reg['best_line'] if reg else None})"
    canon_tok = [T[c] for c in gl[li]]
    sm = difflib.SequenceMatcher(a=canon_tok, b=strip, autojunk=False)
    for tag, a0, a1, b0, b1 in sm.get_opcodes():
        if a0 <= j < a1:
            if tag == "equal":
                return strip[b0 + (j - a0)], "aligned-equal"
            if tag == "replace" and (a1 - a0) == (b1 - b0):
                return strip[b0 + (j - a0)], "aligned-replace"
            return None, f"unresolved({tag})"
    return None, "unresolved(outside)"


rows = []
for iid in sorted(items):
    rec = items[iid]
    rd = reads.get(iid)
    fr = rec["frame"]
    if fr == "C":
        lab = relabel[iid]["new_label"]
        if lab is None:
            rows.append({"id": iid, "frame": "C", "status": "control-dropped(74.jpg unalignable, A2)"})
            continue
        rows.append({"id": iid, "frame": "C", "img": rec["img"], "blind_read": rd["read"][0], "canon": T[lab],
                     "confidence": rd["conf"], "verdict": "control-hit" if T2R[rd["read"][0]] == lab else "control-miss"})
        continue
    targets = [rec["gpos"]] if rec["kind"] in ("single", "window") else [rec["gpos"], rec["gpos"] + 1]
    if rec["kind"] in ("single", "pair", "unloc"):
        rlist = rd["read"]
        for k, g in enumerate(targets):
            if rec["kind"] == "unloc":
                cc, how = flat[g], "ok(render_unloc first-line registration)"
            else:
                cc, how = crop_canon_at(g)
            rows.append({"id": iid, "frame": fr, "gpos": g, "slot": k, "blind_read": rlist[k], "read_how": "glyph",
                         "canon": T[flat[g]], "crop_canon": T[cc] if cc else None, "registration": how,
                         "confidence": rd["conf"]})
    else:  # window / pairwin
        strips = rd["read_strip"]
        if rec["kind"] == "window":
            plan = [(rec["gpos"], 0)]
        else:  # one strip = both glyphs in one same-line window; two strips = [part for gpos, part for gpos+1]
            if len(strips) == 1:
                plan = [(g, 0) for g in targets]
            else:
                plan = [(g, min(k, len(strips) - 1)) for k, g in enumerate(targets)]
        for k, (g, si) in enumerate(plan):
            strip = strips[si]
            exact_part = rec["kind"] == "pairwin" and len(strip) == 1 and len(strips) > 1
            if exact_part:
                cc, how = crop_canon_at(g)
                r, rhow = strip[0], "glyph"
            else:
                r, rhow = window_target(g, strip, f"{iid}:{si}")
                cc, how = (flat[g], "ok") if not rhow.startswith("misreg") else (None, rhow)
            rows.append({"id": iid, "frame": fr, "gpos": g, "slot": k, "blind_read": r, "read_how": rhow,
                         "canon": T[flat[g]], "crop_canon": T[cc] if cc else None, "registration": how,
                         "confidence": rd["conf"]})

# per-row verdicts
for r in rows:
    if r["frame"] == "C" or "status" in r:
        continue
    r["page"] = po[pos_map[r["gpos"]][0]]
    r["line"], r["offset_in_line"] = pos_map[r["gpos"]]
    key = f'{r["id"]}:{r["slot"]}'
    misreg = r["registration"].startswith("misregistered")
    if misreg and r["crop_canon"] is not None and r["blind_read"] is not None:
        # target glyph not in the crop: the item is NOT read; the crop agreement is reader evidence only
        r["crop_check"] = "read==crop_canon" if r["blind_read"] == r["crop_canon"] else "read!=crop_canon"
        r["verdict"] = "not-read (target not in crop; " + r["registration"] + ")"
    elif r["crop_canon"] is None or r["blind_read"] is None:
        r["verdict"] = "not-read (" + (r["registration"] if r["crop_canon"] is None else r["read_how"]) + ")"
    elif r["blind_read"] == r["crop_canon"]:
        r["verdict"] = "canon-confirmed"
    else:
        r["verdict"] = reinspect.get(key, {}).get("verdict", "PENDING-REINSPECTION")
        if key in reinspect:
            r["reinspection"] = reinspect[key]
    rr = reinspect.get(f'{r["id"]}:{r["slot"]}')
    if r["verdict"].startswith("not-read") and rr and "unblinded_reread" in rr:
        r["unblinded_reread"] = rr["unblinded_reread"]; r["verdict"] = rr["verdict"]; r["reinspection"] = rr
    if r["registration"] != "ok" and not r["registration"].startswith("ok("):
        r["note"] = "crop shows a different canon line than the item's (alignment.json defect); scored vs crop_canon"
    r["rat"] = "not available (no committed per-position RAT data; not fetched)"

# addendum A3 extra controls
xs = json.load(open(os.path.join(HERE, "extra_controls_sealed.json"), encoding="utf-8"))
xr = json.load(open(os.path.join(HERE, "extra_controls_reads.json")))["reads"]
for iid in sorted(xs):
    lab = xs[iid]["canon"]
    rows.append({"id": iid, "frame": "C", "img": "73.jpg", "blind_read": xr[iid]["read"][0], "canon": T[lab],
                 "confidence": xr[iid]["conf"], "verdict": "control-hit" if T2R[xr[iid]["read"][0]] == lab else "control-miss"})
json.dump({"blind_reads_sha256": hashlib.sha256(open(br, "rb").read()).hexdigest(), "rows": rows},
          open(os.path.join(HERE, "adjudications.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- summary
from collections import Counter  # noqa: E402

c = Counter((r["frame"], r.get("verdict", r.get("status"))) for r in rows)
for k in sorted(c):
    log(k, c[k])
pend = [r for r in rows if r.get("verdict") == "PENDING-REINSPECTION"]
log("pending reinspection:", len(pend))
for r in pend:
    log(f'  {r["id"]}:{r["slot"]} {r["frame"]} gpos={r["gpos"]} p{r["page"]} L{r["line"]}+{r["offset_in_line"]} '
        f'read={r["blind_read"]} crop_canon={r["crop_canon"]} canon={r["canon"]} conf={r["confidence"]} reg={r["registration"]}')
mis = [r for r in rows if r.get("registration", "ok") not in ("ok",) and not str(r.get("registration", "")).startswith("ok(")]
log("misregistered/unregistered rows:", len(mis))
for r in mis:
    log(f'  {r["id"]}:{r.get("slot")} {r["frame"]} gpos={r.get("gpos")} reg={r["registration"]} read={r.get("blind_read")} '
        f'crop_canon={r.get("crop_canon")} canon={r.get("canon")} verdict={r.get("verdict")}')
open(os.path.join(HERE, "adjudicate.log"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
