"""R44/P3 positive controls — four plants pushed through THE LANE'S OWN glue (R42 X1 rule):
synthetic witness files in relikd format -> extract_channels.parse_witness (the same parser
the real extraction used) -> the same sweep functions in run_p3.py. Pass criteria are fixed
in PREREG.md. Writes plants_results.json and the synthetic witness files plant_*.txt."""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))

from lp import gematria as gp                       # noqa
from extract_channels import parse_witness, sep_streams   # noqa
import run_p3 as R                                  # noqa
from cribs import CRIBS                             # noqa

N = 29
RNG = random.Random(3301)

LONG_TEXT = ("WITHIN THE DEEP THERE IS A BOOK THAT NO MAN HAS READ AND THE MASTER SAID TO "
             "THE STUDENT YOU MUST FIND YOUR OWN PATH THROUGH THE DARK WOOD FOR THE WAY OF "
             "ANOTHER IS NOT YOUR WAY AND THE STUDENT ASKED HOW SHALL I KNOW MY PATH AND THE "
             "MASTER SAID BY WALKING IT ALONE WITH PATIENCE AND WITH CARE FOR ALL THINGS COME "
             "TO THOSE WHO SEEK THEM IN TRUTH AND IN SILENCE THE WISE DO NOT SPEAK OF WHAT "
             "THEY DO NOT KNOW AND THE FOOLISH SPEAK OF NOTHING ELSE SO COMMAND YOUR OWN SELF "
             "AND TEST ALL KNOWLEDGE AGAINST YOUR OWN EXPERIENCE FOR BELIEF WITHOUT TEST IS "
             "A CAGE AND TRUTH WITHOUT WORK IS A DREAM")


def english_idxs(text, n):
    base = gp.keyword_to_indices(text.replace(",", "").replace(".", ""))
    out = []
    while len(out) < n:
        out.extend(base)
    return out[:n]


def filler(n):
    return [RNG.randrange(N) for _ in range(n)]


def build_witness(runes, marks):
    """runes: idx list; marks: list of (rune_offset, glyph) inserted BEFORE the rune at
    that offset (offset == len(runes) appends at end). Returns relikd-format text."""
    by_off = {}
    for off, g in marks:
        by_off.setdefault(off, []).append(g)
    out = []
    for i, v in enumerate(runes):
        for g in by_off.get(i, []):
            out.append(g)
        out.append(gp.IDX_TO_RUNE[v])
    for g in by_off.get(len(runes), []):
        out.append(g)
    return "".join(out)


def word_marks(n_runes, step=6, exclude=()):
    return [(o, "•") for o in range(step, n_runes, step) if o not in exclude]


# ---------------------------------------------------------------- Plant A
def plant_a():
    pt = english_idxs(LONG_TEXT, 160)
    runes = filler(240)
    runes[80:240] = [(p + 11) % N for p in pt]          # encrypt Caesar +11, fwd, atb off
    marks = [(30, '"'), (50, '"'), (80, '"'), (240, '"')] + \
        word_marks(240, exclude={30, 50, 80})
    text = build_witness(runes, marks)
    open(os.path.join(HERE, "plant_a.txt"), "w", encoding="utf-8").write(text)
    parsed = parse_witness(text)
    extraction_ok = (parsed["spans"] == [(30, 50), (80, 240)]
                     and parsed["runes"] == runes)
    streams = [("concat", sum((runes[a:b] for a, b in parsed["spans"]), []))] + [
        (f"span{i+1}", runes[a:b]) for i, (a, b) in enumerate(parsed["spans"])]
    rows, _ = R.sweep_selection(streams, R.BAR_A)
    r2 = next(r for r in rows if r["stream"] == "span2")
    best = r2["best"]
    cell_ok = tuple(best["cell"]) == ("fwd", 0, 18)
    dec = [(v + 18) % N for v in parsed["runes"][80:240]]
    rec_ok = dec == pt
    passed = extraction_ok and cell_ok and rec_ok and (not best["degenerate"]) \
        and best["pmax"] >= r2["bar"]
    return {"plant": "A", "extraction_ok": extraction_ok, "cell_ok": cell_ok,
            "recovery_ok": rec_ok, "pmax": best["pmax"], "bar": r2["bar"],
            "crossed": best["pmax"] >= r2["bar"], "passed": passed}


# ---------------------------------------------------------------- Plant B (b1)
def plant_b():
    pt = english_idxs("THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS "
                      "SHOULD BE ENCRYPTED KNOW THIS", 60)
    assert max(pt) <= 26, pt
    glyphs = "".join("⁘⁚⁜"[t] for v in pt for t in ((v // 9), (v // 3) % 3, v % 3))
    runes = filler(380)
    marks = [(2 * (i + 1), g) for i, g in enumerate(glyphs)] + \
        [(o, "•") for o in range(3, 380, 7)]
    text = build_witness(runes, marks)
    open(os.path.join(HERE, "plant_b.txt"), "w", encoding="utf-8").write(text)
    parsed = parse_witness(text)
    s3i, s3x, _ = sep_streams(parsed)
    stream_ok = (s3i == glyphs)
    decs = R.b1_decodes({"incl": s3i, "excl": s3x})
    rows, _ = R.sweep_token_streams(decs, R.BAR_B)
    planted = next(r for r in rows
                   if r["cell"] == ("b1", "incl", (0, 1, 2), "fwd", "triple"))
    dec = next(d for c, d in decs if c == ("b1", "incl", (0, 1, 2), "fwd", "triple"))
    rec_ok = dec == pt
    nondeg = [r for r in rows if not r["degenerate"]]
    argmax_ok = planted in nondeg and planted["pmax"] == max(r["pmax"] for r in nondeg)
    passed = stream_ok and rec_ok and argmax_ok
    return {"plant": "B", "stream_ok": stream_ok, "recovery_ok": rec_ok,
            "argmax_ok": argmax_ok, "pmax": planted["pmax"], "bar": planted["bar"],
            "crossed": (not planted["degenerate"]) and planted["pmax"] >= planted["bar"],
            "passed": passed,
            "note": "crossed==False caps reading b1 to inconclusive per PREREG"}


# ---------------------------------------------------------------- Plant B2 (b2)
def plant_b2():
    pt = english_idxs(LONG_TEXT + " " + " ".join(CRIBS), 1164)
    bits = [b for v in pt for b in ((v >> 4) & 1, (v >> 3) & 1, (v >> 2) & 1,
                                    (v >> 1) & 1, v & 1)] + [0, 0]
    assert len(bits) == 5822
    vals4 = [2 * bits[i] + bits[i + 1] for i in range(0, 5822, 2)]
    order4 = "•⁘⁚⁜"
    glyphs = "".join(order4[v] for v in vals4)
    runes = filler(2950)
    marks = [(i + 1, g) for i, g in enumerate(glyphs)]
    text = build_witness(runes, marks)
    open(os.path.join(HERE, "plant_b2.txt"), "w", encoding="utf-8").write(text)
    parsed = parse_witness(text)
    _, _, s4 = sep_streams(parsed)
    stream_ok = (s4 == glyphs)
    decs = R.b2_decodes(s4)
    rows, _ = R.sweep_token_streams(decs, R.BAR_B)
    planted = next(r for r in rows if r["cell"] == ("b2", "canon", "fwd", "5bit"))
    dec = next(d for c, d in decs if c == ("b2", "canon", "fwd", "5bit"))
    rec_ok = dec == pt
    nondeg = [r for r in rows if not r["degenerate"]]
    argmax_ok = planted in nondeg and planted["pmax"] == max(r["pmax"] for r in nondeg)
    passed = stream_ok and rec_ok and argmax_ok and planted["pmax"] >= planted["bar"]
    return {"plant": "B2", "stream_ok": stream_ok, "recovery_ok": rec_ok,
            "argmax_ok": argmax_ok, "pmax": planted["pmax"], "bar": planted["bar"],
            "crossed": planted["pmax"] >= planted["bar"], "passed": passed}


# ---------------------------------------------------------------- Plant C (c)
def plant_c():
    crib = gp.keyword_to_indices("THE PRIMES ARE SACRED")        # CRIBS[9], 17 runes
    pt = english_idxs(LONG_TEXT, 240)
    pt[100:100 + len(crib)] = crib
    K = [3, 14, 7, 0, 22, 11, 5]                                  # period-7 additive key
    ct = [(p + K[j % 7]) % N for j, p in enumerate(pt)]
    marks = [(85, '"'), (143, '"')] + word_marks(240, exclude={85, 143})
    text = build_witness(ct, marks)
    open(os.path.join(HERE, "plant_c.txt"), "w", encoding="utf-8").write(text)
    parsed = parse_witness(text)
    extraction_ok = parsed["spans"] == [(85, 143)] and parsed["runes"] == ct
    crib_idx = [gp.keyword_to_indices(c) for c in CRIBS]
    res = R.crib_sweep(parsed["spans"], parsed["runes"], [(0, 240)], crib_idx, R.BAR_C)
    hits = [x for x in res["crossers"]
            if x["crib"] == 9 and x["align"] == 15 and x["deriv"] == "add"
            and x["atb"] == 0 and x["period"] == 7]
    rec_ok = False
    if hits:
        h = hits[0]
        anchor = 85 + 15
        dec = [(c - h["frag"][(j - anchor) % 7]) % N for j, c in enumerate(ct)]
        rec_ok = dec == pt
    passed = extraction_ok and bool(hits) and rec_ok
    return {"plant": "C", "extraction_ok": extraction_ok,
            "n_derivations": res["n_derivations"], "n_survivors": res["n_survivors"],
            "planted_crosser_found": bool(hits), "recovery_ok": rec_ok,
            "pmax": hits[0]["pmax"] if hits else None,
            "bar": hits[0]["bar"] if hits else None, "passed": passed}


# ---------------------------------------------------------------- Plant D (b3)
def plant_d():
    pt = english_idxs(LONG_TEXT, 200)
    sep_marks = ([(o, "⁘") for o in range(10, 200, 25)]
                 + [(55, "⁚"), (125, "⁚")]
                 + [(30, "⁜"), (90, "⁜"), (170, "⁜")])
    vmap = {"⁘": 1, "⁚": 2, "⁜": 3}
    ct = list(pt)
    for off, g in sep_marks:
        ct[off] = (ct[off] + vmap[g]) % N                        # sign +, target next
    marks = sep_marks + word_marks(200, exclude={o for o, _ in sep_marks})
    text = build_witness(ct, marks)
    open(os.path.join(HERE, "plant_d.txt"), "w", encoding="utf-8").write(text)
    parsed = parse_witness(text)
    toks = [(off, c) for off, c in parsed["toks"] if c in "⁘⁚⁜•"]
    rows, _ = R.b3_sweep(parsed["runes"], toks, [(0, 200)], R.BAR_B)
    key = ("b3-3", tuple(sorted(vmap.items())), -1, "next", 0)
    planted = next(r for r in rows if r["cell"] == key)
    delta = [0] * 200
    for off, g in sep_marks:
        delta[off] = -vmap[g]
    dec = [(c + d) % N for c, d in zip(parsed["runes"], delta)]
    rec_ok = dec == pt
    nondeg = [r for r in rows if not r["degenerate"]]
    argmax_ok = planted["pmax"] == max(r["pmax"] for r in nondeg)
    passed = rec_ok and argmax_ok
    return {"plant": "D", "recovery_ok": rec_ok, "argmax_ok": argmax_ok,
            "pmax": planted["pmax"], "bar": planted["bar"],
            "crossed": planted["pmax"] >= planted["bar"], "passed": passed}


def main():
    results = [plant_a(), plant_b(), plant_b2(), plant_c(), plant_d()]
    out = {"all_passed": all(r["passed"] for r in results), "plants": results}
    json.dump(out, open(os.path.join(HERE, "plants_results.json"), "w"), indent=1,
              default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
