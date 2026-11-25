"""R46-L1 arm R37: R37-C1 U2b (pointer jumps at printed word starts) and U3 (composed map-road-direction rule)
through words.py, with the lane's own encipherers/decoders/judge().

  equality : for the decoded heads of pages 0-2, compare R37's mapcommon lengths with words.py's.  Convention C1
             (R37's "key restarts per page"): a word wrapping onto page p from p-1 contributes its on-page fragment
             as word 0 of page p (runes consumed = fragment), but its LENGTH VALUE (rho3 pointer) is the full printed
             word length.  mapcommon uses the fragment length there.
  real     : re-decode exactly the jobs whose decode changes under C1 (U3 rho3 on pages that open mid-word), L=120,
             compare with the row's bars at actual N; L=240 gate for any clearer -> flagged-for-oracle.
  plants   : English over LP2's real layout (page-0 head: no opening wrap; page-1 head: opens mid-word), regimes
             a / b / bp, decoder lengths parsed from the rendered text by words.py (L) and by mapcommon's rule (O).
python -I arm_r37.py"""
import os, sys, json, time, random, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import l1lib as G
import words as W
R37 = G.AN("round37", "C1-composed-clue-readings"); sys.path.insert(0, R37)
SW = G._load("r37_sweep", os.path.join(R37, "sweep.py"))
E = SW.E
F = lambda n: os.path.join(HERE, n)
REAL = W.lp2()
BARS_ACTUAL = {"keyskip1": 6.632, "keyskip2": 6.529, "direct": 6.895}    # LEDGER R37-C1-U3 coverage (bar_v3 actual N)
DOVR = {}                                                                  # page -> {k: length value override}


def head_lens_new(parsed, p, L):
    """words.py convention C1: lengths (runes consumed) of the words covering page p's first L runes, plus the
    length VALUE of each (full printed length for an opening fragment)."""
    s0 = G.PAGE_BOUNDS[p]; lens, vals = [], []
    for w in parsed.words:
        a, b = w["start"], w["start"] + w["len"]
        if b <= s0: continue
        if a >= s0 + max(L, 1100): break
        lens.append(b - max(a, s0)); vals.append(w["len"])
    return lens, vals


def head_lens_old(text, p):
    words, wp = G.legacy_parse(text, "mapcommon")
    return [len(w) for w, q in zip(words, wp) if q >= p][:400]


def cuts_within(lens, L):
    out, t = set(), 0
    for l in lens:
        t += l
        if t >= L: break
        out.add(t)
    return out


# --- decoder digits with C1 length-value override (rho3 only differs)
_orig_digits = SW.u3_digits


def u3_digits_c1(p, rho, Mm, s):
    n = len(E.W); d = []; r = 0; ov = DOVR.get(p, {})
    for k, l in enumerate(SW.LENS[p]):
        pk = k if rho == 1 else (r if rho == 2 else ov.get(k, l))
        d.append(E.VAL["prime"][(s + pk) % n] % Mm); r += l
    return d


def enc_u3_c1(P, lens, vals, rho, M, s, sigma, mode, rel=None, seed=1):
    """E.enc_u3 with the length value (rho3) taken from vals instead of the consumed length."""
    n = len(E.W); d = []; r = 0
    for k, l in enumerate(lens):
        pk = k if rho == 1 else (r if rho == 2 else vals[k])
        d.append(E.VAL["prime"][(s + pk) % n] % M); r += l
    if mode in ("A1", "A2"):
        C, i, D = [], 0, 0
        for k, l in enumerate(lens):
            D += d[k]; sh = d[k] if mode == "A1" else D
            for t in range(l):
                if i >= len(P): return C
                C.append((P[i] + sigma * sh) % 29); i += 1
        return C
    K = []; r = 0; J = 0
    for k, l in enumerate(lens):
        J += sigma * d[k]
        for t in range(l): K.append(E.K0[(r + J + t) % len(E.K0)])
        r += l
    return E.encipher_with_key(P, K, rel, seed)


def equality():
    txt = open(W.KRIS, encoding="utf-8").read()
    out = {}
    for p in (0, 1, 2):
        Lh = min(240, SW.PAGE_LEN[p])
        new, vals = head_lens_new(REAL, p, Lh)
        old = SW.LENS[p]
        same_cuts = cuts_within(new, Lh) == cuts_within(old, Lh)
        diffs = [k for k in range(min(len(old), len(new))) if (vals[k] if k < len(vals) else None) != old[k] and sum(new[:k]) < Lh]
        out["page%d" % p] = {"head_runes": Lh, "boundaries_in_head_identical": same_cuts, "opens_mid_word": vals[0] != new[0],
                             "first_word_fragment_vs_full": [new[0], vals[0]],
                             "length_value_differs_at_word_index": diffs,
                             "affected": "U3 rho3 (d_k uses l_k) on this page" if diffs else "none"}
    return out


def real():
    """re-decode U3 rho3 jobs on pages opening mid-word with the C1 length value."""
    eq = equality(); pages = [int(k[4:]) for k, v in eq.items() if v["length_value_differs_at_word_index"]]
    for p in pages:
        _, vals = head_lens_new(REAL, p, 240); DOVR[p] = {0: vals[0]}
    SW.u3_digits = u3_digits_c1
    val = json.load(open(os.path.join(R37, "control.json")))["valid"]["U3_cells"]
    jobs = [j for j in SW.u3_jobs(val) if j["rho"] == 3 and j["page"] in pages]
    best = {}; rows = []; flagged = []
    for j in jobs:
        plain, a = SW.run_job(j, 120); pm = float(a["pmax"])
        rel = j["rel"]; key = rel
        rows.append({"kid": SW.kid(j), "pmax120": round(pm, 3), "preg": SW.PAN.registers[a["preg"]],
                     "ioc_n": round(float(SW.AD.ioc_n(__import__("numpy").asarray(plain))), 4), "min_distinct32": int(SW.AD.min_distinct(__import__("numpy").asarray(plain)))})
        if pm > best.get(key, (-9,))[0]: best[key] = (round(pm, 3), SW.kid(j), SW.PAN.registers[a["preg"]])
        if pm >= BARS_ACTUAL[rel]:
            p2, a2 = SW.run_job(j, 240)
            flagged.append({"kid": SW.kid(j), "pmax120": pm, "pmax240": float(a2["pmax"])})
    SW.u3_digits = _orig_digits; DOVR.clear()
    return {"pages_rerun": pages, "n_decodes": len(jobs), "best_by_relation": best, "bars_actual_N": BARS_ACTUAL,
            "clears": {r: best[r][0] >= BARS_ACTUAL[r] for r in best}, "gate_runs_flagged_for_oracle": flagged, "rows": rows}


def plants(nrep=2):
    rows = []; t0 = time.time()
    U3MODES = ("A1", "A2", "A3k1", "A3k2")
    for regime in ("a", "b", "bp"):
        for page in (0, 1):
            for rep in range(nrep):
                rng = random.Random(46370 + 100 * ("a", "b", "bp").index(regime) + 10 * page + rep)
                P = G.make_plant(regime, rng)
                txt = W.render(G.regroup(P.flat, P.printed_lens), P.sent_ends, G.LINE_STARTS, G.PAGE_STARTS)
                parsed = W.parse(txt)
                s0 = G.PAGE_BOUNDS[page]; Pl = P.flat[s0:s0 + 240]
                # TRUE (encipherer) lengths for the head: from the true word list
                tl, tv = [], []
                for st, l in zip(P.starts, P.true_lens):
                    if st + l <= s0: continue
                    if st >= s0 + 1100: break
                    tl.append(st + l - max(st, s0)); tv.append(l)
                dl_new, dv_new = head_lens_new(parsed, page, 240)
                dl_old = head_lens_old(txt, page)
                jobs = []
                for (ch, nm, m) in E.VARIANTS:
                    jobs.append(("U2b", (ch, nm, m)))
                for rho, mode in itertools.product((1, 2, 3), U3MODES):
                    jobs.append(("U3", (rho, mode)))
                for ji, (sub, spec) in enumerate(jobs):
                    seed = rng.randrange(1, 10 ** 9)
                    if sub == "U2b":
                        ch, nm, m = spec; rel = SW.RELS[rng.randrange(2)]; o = rng.randrange(8)
                        Cc = E.enc_u2b(Pl, ch, nm, m, o, tl, rel, seed)[:240]
                        j = {"sub": "U2", "ch": ch, "nm": nm, "m": m, "mode": "b", "rel": rel, "sign": -1, "o": o, "page": 0}
                        cell = "U2b"
                    else:
                        rho, mode = spec; s = rng.randrange(29); sigma = rng.choice((-1, 1)); m3 = "A3" if mode.startswith("A3") else mode
                        rel = {"A3k1": "keyskip1", "A3k2": "keyskip2"}.get(mode, "direct")
                        Cc = enc_u3_c1(Pl, tl, tv, rho, 29, s, sigma, m3, rel if m3 == "A3" else None, seed)[:240]
                        j = {"sub": "U3", "rho": rho, "M": 29, "mode": m3, "s": s, "sigma": sigma, "rel": rel, "sign": sigma, "o": 0, "page": 0}
                        cell = "U3-rho%d-%s" % (rho, mode)
                    row = {"regime": regime, "page_layout": page, "rep": rep, "cell": cell, "sub": sub}
                    for loader, lens, vals in (("L", dl_new, dv_new), ("O", dl_old, dl_old)):
                        saved = SW.LENS[0]; SW.LENS[0] = lens
                        DOVR[0] = {0: vals[0]} if loader == "L" else {}
                        SW.u3_digits = u3_digits_c1
                        try:
                            p1, a1 = SW.plant_run(j, Cc, 120); p2, a2 = SW.plant_run(j, Cc, 240)
                        finally:
                            SW.LENS[0] = saved; SW.u3_digits = _orig_digits; DOVR.clear()
                        jd = SW.judge(float(a1["pmax"]), float(a2["pmax"]), SW.rec_of(p2, Pl), rel)
                        row[loader] = jd
                    rows.append(row)
                G.heartbeat("r37", "plants %s p%d rep%d %.0fs" % (regime, page, rep, time.time() - t0))
    summ = {}
    for regime in ("a", "b", "bp"):
        for loader in ("L", "O"):
            for grp in ("U2b", "U3", "U3-rho3", "U3-rho1", "U3-rho2"):
                for page in (0, 1, "all"):
                    rr = [r for r in rows if r["regime"] == regime and (page == "all" or r["page_layout"] == page) and
                          (r["sub"] == grp if grp in ("U2b", "U3") else r["cell"].startswith(grp + "-"))]
                    if not rr: continue
                    k = sum(r[loader]["recover"] for r in rr)
                    summ["%s|%s|%s|p%s" % (regime, loader, grp, page)] = {"power": round(k / len(rr), 3), "k": k, "n": len(rr), "wilson": G.wilson(k, len(rr)),
                                                                        "median_rec240": sorted(r[loader]["recovery240"] for r in rr)[len(rr) // 2],
                                                                        "median_pmax240": sorted(r[loader]["pmax240"] for r in rr)[len(rr) // 2]}
    return {"rule": "R37 sweep.judge(): pmax120>=bar_v3(1e6,120) & pmax240>=bar_v3(1e6,240) & recovery240>=0.90",
            "summary": summ, "rows": rows, "elapsed_s": round(time.time() - t0, 1)}


def main():
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "equality": equality()}
    print(json.dumps(out["equality"]), flush=True)
    out["real"] = real(); print("real", {k: v for k, v in out["real"].items() if k != "rows"}, flush=True)
    out["plants"] = plants()
    json.dump(out, open(F("r37_results.json"), "w"), indent=1)
    for k, v in out["plants"]["summary"].items():
        if k.endswith("pall"): print(k, v["power"], v["n"], v["median_rec240"], v["median_pmax240"])


if __name__ == "__main__":
    main()
