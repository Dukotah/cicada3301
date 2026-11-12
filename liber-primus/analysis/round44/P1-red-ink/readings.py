"""R44 / P1 step 4 — the pre-registered readings of the red channel (PREREG §4 + Addendum 1).

A1  selection streams {legacy187, corrected200, full213} x {fwd,rev} x affine(a in {1,-1},
    s in 0..28)  = 348 decodes, bar L_cap 120.
A2  per-section ('$'-delimited canon sections) red substreams of full213 with L >= 60,
    same 116-map family each, bar L_cap 120.
A3  red as KEY over the black remainder (canon minus full213 positions, L=12,923):
    keys {legacy187, full213} x {fwd,rev} x {vigm,vigp,beau} x {plain, atbash-ct} x all
    rotations = 4,800 decodes, bar L_cap 729.
B   red dot blocks / numerals: complete enumeration (streams are far below the minimum
    adjudicable length 60 -> census-only, no panel verdict; recorded not_covered).
C   red key-parameters into the solved-page generator family: per unsolved canon page
    (0..54), offsets dedup{r_p, firstpos_p, cum_p} x gens {prime, prime_totient, totient}
    x 6 cfgs, bar at the page's L_cap.

Verdict gate: plant_results.json all_passed must be true (PREREG §5).
Bars FIXED at N=10,000 (PREREG §3): 120->12.8507 240->17.1842 400->18.5252 729->21.5296.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp, ciphers  # noqa
import adjudicate as A  # noqa
import bars_v3 as B  # noqa

N = gp.N
BARS = {L: B.bar_v3(10000, L, "free") for L in (120, 240, 400, 729)}


def bar_for(L):
    cand = [x for x in (120, 240, 400, 729) if x <= L] or [120]
    return BARS[max(cand)]


def _panel():
    return A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))


# ------------------------------------------------------------------ shared collect
def collect(X, meta, L, pan, best, crossers, family):
    """X: (B, L) decode block. meta: list of dicts per row."""
    r = A.adjudicate_batch(X, pan=pan)
    bar = bar_for(L)
    pm = r["pmax"]
    i = int(pm.argmax())
    if pm[i] > best.get("pmax", -99):
        best.clear()
        best.update(meta[i])
        best.update(pmax=float(pm[i]), preg=int(r["preg"][i]), L=int(L),
                    bar=round(float(bar), 4), family=family, decode=X[i].tolist())
    for j in np.nonzero(pm >= bar)[0]:
        full = A.adjudicate(np.asarray(X[int(j)], dtype=np.int64), pan=pan)
        if not full["degenerate"] and full["pmax"] >= bar:
            c = dict(meta[int(j)])
            c.update(pmax=float(full["pmax"]), preg=full["preg"], L=int(L),
                     bar=round(float(bar), 4), family=family, degenerate=False,
                     ioc=full["ioc"], mds=full["mds"], h2=full["h2"], zl=full["zl"],
                     decode=X[int(j)].tolist())
            crossers.append(c)
    return X.shape[0]


# ------------------------------------------------------------------ A: affine family
def affine_block(x):
    """(116, L): {fwd, rev} x a in {1, 28} x s in 0..28, with meta."""
    rows, meta = [], []
    for dname, v in (("fwd", np.asarray(x)), ("rev", np.asarray(x)[::-1])):
        for a in (1, N - 1):
            for s in range(N):
                rows.append((a * v + s) % N)
                meta.append(dict(dir=dname, a=int(a), s=int(s)))
    return np.stack(rows), meta


# ------------------------------------------------------------------ C: generator glue
GENS = {
    "prime": lambda L, o: ciphers.prime_stream(L + o)[o:o + L],
    "prime_totient": lambda L, o: ciphers.prime_totient_stream(L + o)[o:o + L],
    "totient": lambda L, o: ciphers.totient_stream(L + o + 2, start=2)[o:o + L],
}
CFGS = ["vigm", "vigp", "beau", "vigm_atb", "vigp_atb", "beau_atb"]


def decode(c, K, cfg):
    x = (N - 1) - c if cfg.endswith("_atb") else c
    base = cfg.split("_")[0]
    if base == "vigm":
        return (x - K) % N
    if base == "vigp":
        return (x + K) % N
    return (K - x) % N


def sweep_reading_c(cpage, offsets, pan, best=None, crossers=None, page=None):
    """The reading-C glue: one page, red-derived offsets, generator family, 6 cfgs.
    Used identically by the P3 plant and the real sweep."""
    c = np.asarray(cpage, dtype=np.int64)
    L = len(c)
    if best is None:
        best = {}
    if crossers is None:
        crossers = []
    offs = sorted(set(int(o) for o in offsets))
    rows, meta = [], []
    for gname, gfn in GENS.items():
        for o in offs:
            K = np.asarray(gfn(L, o), dtype=np.int64)
            for cfg in CFGS:
                rows.append(decode(c, K, cfg))
                meta.append(dict(gen=gname, offset=o, cfg=cfg, page=page))
    X = np.stack(rows)
    n = collect(X, meta, L, pan, best, crossers, family="C")
    return best, crossers, n


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    plants = json.load(open(os.path.join(HERE, "plant_results.json")))
    assert plants["all_passed"], "positive controls not passed - no verdict (PREREG §5)"

    pan = _panel()
    ch = json.load(open(os.path.join(HERE, "channel.json")))
    census = json.load(open(os.path.join(HERE, "census.json")))

    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    S = "".join(c for c in txt if c in gp.RUNE_TO_IDX)
    canon = np.array([gp.RUNE_TO_IDX[c] for c in S], dtype=np.int64)

    legacy = json.load(open(os.path.join(LP, "analysis", "armada_osint", "redrune",
                                         "result.json")))
    legacy_idx = [gp.RUNE_TO_IDX[c] for c in legacy["global_red_runes"]]
    corr_idx = ch["corrected"]["idx"]
    full_idx = ch["full"]["idx"]
    full_pos = ch["full"]["pos"]
    streams = {"legacy187": legacy_idx, "corrected200": corr_idx, "full213": full_idx}

    out = dict(bars={str(k): round(v, 4) for k, v in BARS.items()},
               n_total=0, families={}, crossers=[])
    crossers = []

    # ---- A1
    bestA1, n = {}, 0
    for sname, sidx in streams.items():
        X, meta = affine_block(sidx)
        for m in meta:
            m["stream"] = sname
        n += collect(X, meta, X.shape[1], pan, bestA1, crossers, family="A1")
    bestA1.pop("decode", None)
    out["families"]["A1"] = dict(n=n, best=bestA1)
    out["n_total"] += n
    print("A1 done n=%d best pmax %.3f (bar %.3f)" % (n, bestA1["pmax"], bestA1["bar"]))

    # ---- A2: '$'-delimited sections
    sec_bounds, off = [0], 0
    for c in txt:
        if c in gp.RUNE_TO_IDX:
            off += 1
        elif c == "$":
            sec_bounds.append(off)
    sec_bounds.append(len(S))
    subs = {}
    for si in range(len(sec_bounds) - 1):
        lo, hi = sec_bounds[si], sec_bounds[si + 1]
        sub = [i for p, i in zip(full_pos, full_idx) if lo <= p < hi]
        subs[si] = sub
    bestA2, n2 = {}, 0
    a2_skipped = {si: len(sub) for si, sub in subs.items() if 0 < len(sub) < 60}
    for si, sub in subs.items():
        if len(sub) < 60:
            continue
        X, meta = affine_block(sub)
        for m in meta:
            m["section"] = si
        n2 += collect(X, meta, X.shape[1], pan, bestA2, crossers, family="A2")
    out["families"]["A2"] = dict(n=n2, best=bestA2 or None, section_sizes={k: len(v) for
                                 k, v in subs.items()}, below_min_len=a2_skipped)
    if bestA2:
        bestA2.pop("decode", None)
    out["n_total"] += n2
    print("A2 done n=%d sections %s" % (n2, {k: len(v) for k, v in subs.items()}))

    # ---- A3: red as key over black remainder
    redset = set(full_pos)
    black = np.array([v for i, v in enumerate(canon) if i not in redset], dtype=np.int64)
    Lb = len(black)
    bestA3, n3 = {}, 0
    for sname in ("legacy187", "full213"):
        key = np.asarray(streams[sname], dtype=np.int64)
        for dname in ("fwd", "rev"):
            kd = key if dname == "fwd" else key[::-1]
            Lk = len(kd)
            idx = (np.arange(Lk)[:, None] + np.arange(Lb)[None, :]) % Lk
            Kmat = kd[idx]
            for cfg in CFGS:
                X = decode(black[None, :], Kmat, cfg)
                meta = [dict(stream=sname, dir=dname, cfg=cfg, rot=r) for r in range(Lk)]
                n3 += collect(X, meta, Lb, pan, bestA3, crossers, family="A3")
    bestA3.pop("decode", None)
    out["families"]["A3"] = dict(n=n3, L_black=int(Lb), best=bestA3)
    out["n_total"] += n3
    print("A3 done n=%d best pmax %.3f (bar %.3f) %.0fs"
          % (n3, bestA3["pmax"], bestA3["bar"], time.time() - t0))

    # ---- B: enumeration (below adjudicable length -> census-only, PREREG §4 B)
    blocks = sorted(census["blocks"], key=lambda b: (b["img"], b["bbox"][2], b["bbox"][0]))
    counts_all = [b["n_dots"] for b in blocks]
    big = [(b["img"], b["n_dots"]) for b in blocks if b["n_dots"] in (10, 13)]
    bits_13_1 = "".join("1" if c == 13 else "0" for _, c in big)
    nums = [1, 2, 3, 4, 5]
    out["families"]["B"] = dict(
        n=0, verdict="census-only (max stream length %d < 60; no bar exists)" % len(big),
        block_counts_in_book_order=counts_all,
        blocks_13_or_10=[dict(img=i, n=c) for i, c in big],
        bits_13_as_1=bits_13_1, bits_13_as_0="".join("01"[b == "0"] for b in bits_13_1),
        counts_mod29_translit=gp.indices_to_translit([c % N for _, c in big]),
        red_margin_numerals=nums,
        red_grid_cell=3299,
        notes=["3299 mod 29 = %d ('%s'); 3301-3299 = 2" % (3299 % N,
               gp.indices_to_translit([3299 % N])),
               "margin numerals 1-5 all red; label the five numbered list items",
               "1/2/4-dot 'blocks' are red word-separator dots inside red text lines"])

    # ---- C: red parameters into the generator family
    segs = txt.split("%")
    page_idx = []
    for seg in segs:
        ii = [gp.RUNE_TO_IDX[c] for c in seg if c in gp.RUNE_TO_IDX]
        page_idx.append(np.array(ii, dtype=np.int64))
    per_page = ch["per_page"]
    bestC, nC = {}, 0
    for pi in range(55):
        pp = per_page[str(pi)]
        offs = {pp["r_p"], pp["firstpos_p"], pp["cum_p"]}
        _, _, cnt = sweep_reading_c(page_idx[pi], offs, pan, bestC, crossers, page=pi)
        nC += cnt
    bestC.pop("decode", None)
    out["families"]["C"] = dict(n=nC, best=bestC)
    out["n_total"] += nC
    print("C done n=%d best pmax %.3f (bar %.3f)" % (nC, bestC["pmax"], bestC["bar"]))

    # ---- verdict
    assert out["n_total"] <= 10000, out["n_total"]
    for c in crossers:
        c["flag"] = "FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md (never self-certified)"
    out["crossers"] = crossers
    out["n_crossers"] = len(crossers)
    gb = max((f["best"] for f in out["families"].values()
              if isinstance(f, dict) and f.get("best")), key=lambda b: b["pmax"])
    out["observed_global_best"] = gb
    out["verdict"] = ("NEGATIVE" if not crossers
                      else "CROSSER(S) FLAGGED-FOR-ORACLE - not certified")
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print(json.dumps(dict(n_total=out["n_total"], n_crossers=len(crossers),
                          verdict=out["verdict"],
                          global_best={k: gb[k] for k in ("family", "pmax", "bar")}),
                     indent=1))


if __name__ == "__main__":
    main()
