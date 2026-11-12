"""R44/P3 — the four preregistered readings, exactly as fixed in PREREG.md.

This module is BOTH the library the plants are pushed through (plants.py imports every sweep
function here — the R42 X1 own-glue rule) and the real-run entry point (main()).

Thresholds are the PREREG constants below; they are not recomputed at run time.
"""
import itertools, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))

from run_stats import load_pages      # noqa
from lp import gematria as gp         # noqa
import adjudicate as A                # noqa
from cribs import CRIBS               # noqa

N = 29
SEPS3 = "⁘⁚⁜"
WORD = "•"

# PREREG thresholds (bars_v3 free bar of record; L_cap floored at 120)
BAR_A = {120: 11.584, 400: 16.902}                                  # N_a = 928
BAR_B = {120: 11.943, 240: 15.925, 400: 17.362, 729: 20.296}        # N_b = 1,820
BAR_C = {120: 13.376, 240: 17.913}                                  # N_c = 26,784

_PAN = None


def panel():
    global _PAN
    if _PAN is None:
        _PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
    return _PAN


def l_cap(L):
    return max([c for c in (120, 240, 400, 729) if c <= L] or [120])


def bar_for(L, bars):
    return bars[l_cap(L)]


def adj(idxs):
    r = A.adjudicate(idxs, pan=panel())
    return {"pmax": float(r["pmax"]), "preg": int(r["preg"]),
            "degenerate": bool(r["degenerate"])}


# ------------------------------------------------------------- reading (a)
def sweep_selection(streams, bars=BAR_A):
    """streams: list of (name, idx_list). 116 dressings per stream."""
    rows, crossers = [], []
    for name, s in streams:
        best = {"pmax": -99.0}
        bar = bar_for(len(s), bars)
        for dirn, atb, shift in itertools.product(("fwd", "rev"), (0, 1), range(N)):
            x = s[::-1] if dirn == "rev" else s
            if atb:
                x = [(N - 1) - v for v in x]
            d = [(v + shift) % N for v in x]
            r = adj(d)
            r.update(cell=(dirn, atb, shift))
            if r["pmax"] > best["pmax"]:
                best = r
        clears = (not best["degenerate"]) and best["pmax"] >= bar
        row = {"stream": name, "L": len(s), "bar": bar, "best": best, "clears": clears}
        rows.append(row)
        if clears:
            crossers.append(row)
    return rows, crossers


# ------------------------------------------------------------- reading (b1/b2)
def b1_decodes(sep3_streams):
    """sep3_streams: dict variant_name -> glyph string over SEPS3.
    6 perms x 2 dirs x 2 packings per variant."""
    out = []
    for vname, stream in sep3_streams.items():
        for perm in itertools.permutations((0, 1, 2)):
            m = dict(zip(SEPS3, perm))
            for dirn in ("fwd", "rev"):
                t = [m[c] for c in (stream[::-1] if dirn == "rev" else stream)]
                tri = [9 * t[i] + 3 * t[i + 1] + t[i + 2]
                       for i in range(0, len(t) - len(t) % 3, 3)]
                pr = [3 * t[i] + t[i + 1] for i in range(0, len(t) - len(t) % 2, 2)]
                out.append((("b1", vname, perm, dirn, "triple"), tri))
                out.append((("b1", vname, perm, dirn, "pair"), pr))
    return out


def b2_decodes(sep4):
    order4 = (WORD + SEPS3)
    out = []
    for aname, assign in (("canon", {c: i for i, c in enumerate(order4)}),
                          ("rev", {c: 3 - i for i, c in enumerate(order4)})):
        for dirn in ("fwd", "rev"):
            t = [assign[c] for c in (sep4[::-1] if dirn == "rev" else sep4)]
            pair16 = [4 * t[i] + t[i + 1] for i in range(0, len(t) - len(t) % 2, 2)]
            bits = []
            for v in t:
                bits += [(v >> 1) & 1, v & 1]
            fiveb = [16 * bits[i] + 8 * bits[i + 1] + 4 * bits[i + 2]
                     + 2 * bits[i + 3] + bits[i + 4]
                     for i in range(0, len(bits) - len(bits) % 5, 5)]
            tri64 = [(16 * t[i] + 4 * t[i + 1] + t[i + 2]) % N
                     for i in range(0, len(t) - len(t) % 3, 3)]
            out.append((("b2", aname, dirn, "pair16"), pair16))
            out.append((("b2", aname, dirn, "5bit"), [v % N for v in fiveb]))
            out.append((("b2", aname, dirn, "tri64"), tri64))
    return out


def sweep_token_streams(decodes, bars=BAR_B):
    rows, crossers = [], []
    for cell, d in decodes:
        bar = bar_for(len(d), bars)
        r = adj(d)
        clears = (not r["degenerate"]) and r["pmax"] >= bar
        row = {"cell": cell, "L": len(d), "bar": bar, **r, "clears": clears}
        rows.append(row)
        if clears:
            crossers.append(row)
    return rows, crossers


# ------------------------------------------------------------- reading (b3)
def b3_configs():
    cfgs = []
    for perm in itertools.permutations((1, 2, 3)):
        vmap = dict(zip(SEPS3, perm))
        for sign in (1, -1):
            for target in ("next", "prev"):
                cfgs.append(("b3-3", vmap, sign, target))
    order4 = (WORD + SEPS3)
    for aname, vmap in (("canon", {c: i for i, c in enumerate(order4)}),
                        ("rev", {c: 3 - i for i, c in enumerate(order4)})):
        for sign in (1, -1):
            for target in ("next", "prev"):
                cfgs.append(("b3-4" + aname, vmap, sign, target))
    return cfgs


def b3_sweep(canon, sep_toks, page_bounds, bars=BAR_B):
    """canon: full rune idx list; sep_toks: list of (rune_offset, glyph); page_bounds:
    list of (start, end). Decode p_hat = (c + sign*v) at targeted positions."""
    rows, crossers = [], []
    for cname, vmap, sign, target in b3_configs():
        delta = [0] * len(canon)
        for off, ch in sep_toks:
            if ch not in vmap:
                continue
            pos = off if target == "next" else off - 1
            if 0 <= pos < len(canon):
                delta[pos] = (delta[pos] + sign * vmap[ch]) % N
        dec = [(c + dl) % N for c, dl in zip(canon, delta)]
        for pi, (a, b) in enumerate(page_bounds):
            d = dec[a:b]
            bar = bar_for(len(d), bars)
            r = adj(d)
            clears = (not r["degenerate"]) and r["pmax"] >= bar
            row = {"cell": (cname, tuple(sorted(vmap.items())), sign, target, pi),
                   "L": len(d), "bar": bar, **r, "clears": clears}
            rows.append(row)
            if clears:
                crossers.append(row)
    return rows, crossers


# ------------------------------------------------------------- reading (c)
def exact_period(frag, pmax_period=13):
    for p in range(1, pmax_period + 1):
        if len(frag) >= 2 * p and all(frag[i] == frag[i - p] for i in range(p, len(frag))):
            return p
    return None


def exact_ap(frag):
    if len(frag) < 3:
        return None
    b = (frag[1] - frag[0]) % N
    if b == 0:
        return None  # constant = period 1, handled by exact_period
    if all((frag[i] - frag[i - 1]) % N == b for i in range(1, len(frag))):
        return b
    return None


def crib_sweep(spans, canon, page_bounds, crib_idx_lists, bars=BAR_C):
    """spans: list of (start, end). For every placement x {add,beau} x {atb0,atb1}, derive
    the implied key fragment; screen (exact period<=13 w/ len>=2p, or exact AP); survivors
    extend over every touched page and are adjudicated."""
    n_deriv = 0
    survivors, crossers, adjudications = [], [], 0
    gbest = {"pmax": -99.0}
    for si, (a, b) in enumerate(spans):
        ct = canon[a:b]
        for ci, kidx in enumerate(crib_idx_lists):
            Lc = len(kidx)
            if Lc > len(ct):
                continue
            for al in range(len(ct) - Lc + 1):
                for deriv in ("add", "beau"):
                    for atb in (0, 1):
                        n_deriv += 1
                        cseg = ct[al:al + Lc]
                        if atb:
                            cseg = [(N - 1) - v for v in cseg]
                        if deriv == "add":
                            frag = [(c - p) % N for c, p in zip(cseg, kidx)]
                        else:
                            frag = [(c + p) % N for c, p in zip(cseg, kidx)]
                        per = exact_period(frag)
                        ap = None if per else exact_ap(frag)
                        if per is None and ap is None:
                            continue
                        anchor = a + al
                        surv = {"span": si, "crib": ci, "align": al,
                                "deriv": deriv, "atb": atb,
                                "period": per, "ap": ap, "frag": frag}
                        # extend over every page the SPAN touches
                        pages_hit = [pi for pi, (pa, pb) in enumerate(page_bounds)
                                     if pa < b and a < pb]
                        page_rs = []
                        for pi in pages_hit:
                            pa, pb = page_bounds[pi]
                            dec = []
                            for j in range(pa, pb):
                                c = canon[j]
                                if atb:
                                    c = (N - 1) - c
                                if per is not None:
                                    k = frag[(j - anchor) % per]
                                else:
                                    k = (frag[0] + ap * (j - anchor)) % N
                                dec.append((c - k) % N if deriv == "add"
                                           else (k - c) % N)
                            r = adj(dec)
                            adjudications += 1
                            bar = bar_for(len(dec), bars)
                            clears = (not r["degenerate"]) and r["pmax"] >= bar
                            pr = {"page": pi, "L": len(dec), "bar": bar, **r,
                                  "clears": clears}
                            page_rs.append(pr)
                            if clears:
                                crossers.append({**surv, **pr})
                            if not r["degenerate"] and r["pmax"] > gbest["pmax"]:
                                gbest = {**surv, **pr}
                        surv["pages"] = page_rs
                        survivors.append(surv)
    return {"n_derivations": n_deriv, "n_survivors": len(survivors),
            "n_adjudications": adjudications, "survivors": survivors,
            "crossers": crossers, "global_best": gbest}


# ------------------------------------------------------------- main (the real run)
def main():
    t0 = time.time()
    ch = json.load(open(os.path.join(HERE, "channels.json"), encoding="utf-8"))
    if ch["killed"]:
        raise SystemExit("channels.json is KILLED; no sweep may run")
    C = ch["channels"]
    pages = load_pages()[:-2]
    bounds, pos = [], 0
    for pg in pages:
        bounds.append((pos, pos + len(pg)))
        pos += len(pg)
    canon = [v for pg in pages for v in pg]
    assert pos == 12956

    # (a)
    streams = [("concat", C["concat_runes"])] + [
        (f"span{i+1}", s["runes"]) for i, s in enumerate(C["spans"])]
    a_rows, a_cross = sweep_selection(streams)
    print(f"(a) done {time.time()-t0:.0f}s crossers={len(a_cross)}", flush=True)

    # (b1 + b2)
    b12 = b1_decodes({"incl": C["sep3_incl"], "excl": C["sep3_excl"]}) \
        + b2_decodes(C["sep4"])
    b12_rows, b12_cross = sweep_token_streams(b12)
    print(f"(b1/b2) done {time.time()-t0:.0f}s crossers={len(b12_cross)}", flush=True)

    # (b3) — separator offsets from the extraction (all SEPS3 + WORD toks)
    rel_toks = extract_sep_toks()
    b3_rows, b3_cross = b3_sweep(canon, rel_toks, bounds)
    print(f"(b3) done {time.time()-t0:.0f}s crossers={len(b3_cross)}", flush=True)

    # (c)
    crib_idx = [gp.keyword_to_indices(c) for c in CRIBS]
    spans = [(s["start"], s["end"]) for s in C["spans"]]
    c_res = crib_sweep(spans, canon, bounds, crib_idx)
    print(f"(c) done {time.time()-t0:.0f}s derivations={c_res['n_derivations']} "
          f"survivors={c_res['n_survivors']} crossers={len(c_res['crossers'])}", flush=True)

    # (d) census
    apo = C["apostrophes"]
    d_census = {
        "apostrophe_offsets": apo,
        "apostrophe_offsets_mod29": [x % N for x in apo],
        "rune_before_after": [[gp.IDX_TO_TRANS[canon[x - 1]],
                               gp.IDX_TO_TRANS[canon[x]]] for x in apo],
        "gaps": [apo[i + 1] - apo[i] for i in range(len(apo) - 1)],
        "gaps_mod29": [(apo[i + 1] - apo[i]) % N for i in range(len(apo) - 1)],
        "numerals": C["numerals"],
        "note": "census only per PREREG (streams of length <=12, below the L=120 bar node; "
                "no verdict claimed)"}

    def summarize(rows):
        nd = [r for r in rows if not (r.get("degenerate") or
                                      r.get("best", {}).get("degenerate"))]
        def pm(r):
            return r.get("pmax", r.get("best", {}).get("pmax", -99))
        best = max(nd, key=pm) if nd else None
        return {"n": len(rows), "n_degenerate": len(rows) - len(nd),
                "best_nondeg": best}

    out = {
        "N_fixed": {"a": 928, "b": 1820, "c": 26784},
        "a": {"rows": a_rows, "crossers": a_cross, "summary": summarize(a_rows)},
        "b12": {"rows": b12_rows, "crossers": b12_cross,
                "summary": summarize(b12_rows)},
        "b3": {"n_rows": len(b3_rows), "crossers": b3_cross,
               "summary": summarize(b3_rows)},
        "c": c_res,
        "d_census": d_census,
        "counts_check": {"a_decodes": sum(1 for _ in ())},
        "elapsed_s": round(time.time() - t0, 1),
    }
    out["counts_check"] = {"a_decodes": len(streams) * 116,
                           "b12_decodes": len(b12),
                           "b3_decodes": len(b3_rows),
                           "c_derivations": c_res["n_derivations"],
                           "c_adjudications": c_res["n_adjudications"]}
    json.dump(out, open(os.path.join(HERE, "p3_results.json"), "w"), indent=1,
              default=str)
    print(json.dumps({"counts": out["counts_check"],
                      "crossers": {"a": len(a_cross), "b12": len(b12_cross),
                                   "b3": len(b3_cross), "c": len(c_res["crossers"])},
                      "elapsed_s": out["elapsed_s"]}, indent=1))


def extract_sep_toks():
    """Separator tokens with rune offsets from the relikd witness (same parse as
    extract_channels)."""
    from extract_channels import parse_witness, RELIKD_ORDER
    rel_text = "".join(open(os.path.join(LP, "data", "relikd", n + ".txt"),
                            encoding="utf-8").read() for n in RELIKD_ORDER)
    parsed = parse_witness(rel_text)
    return [(off, c) for off, c in parsed["toks"] if c in SEPS3 or c == WORD]


if __name__ == "__main__":
    main()
