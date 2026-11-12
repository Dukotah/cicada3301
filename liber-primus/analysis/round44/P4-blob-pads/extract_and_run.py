"""R44 / P4 - the three onion pre-page 256-byte blobs as per-page mod-29 pads over the 55
unsolved LP2 pages, through the STANDING instrument (adjudicate/adjudicate_batch + panel-R36 +
bars_v3 'free'), exactly as pre-registered in PREREG.md.  Harness is R43-F5bT's runner with the
key material swapped (that lane's construction = R28-L2's, validated there).  Three positive
controls are enciphered through THIS lane's own extracted+derived keystreams and recovered by
the same sweep loop; no verdict without all three passing.

Matrix per page (fixed in PREREG): {3 blobs x (mod29, div9) + 3 blobs x nib + 18 canon-joined
mod29 streams} x 2 directions x 6 configs x all rotations  ->  N_grid = 92,160 decodes/page.
Bars of record at N=92,160: L_cap 120 -> 14.0340, L_cap 240 -> 18.8261.
"""
import hashlib
import json
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp                      # noqa
from run_stats import load_pages                   # noqa
import adjudicate as A                             # noqa
import bars_v3 as B                                # noqa

N = gp.N                                           # 29
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
FREE_LS = (120, 240, 400, 729)
NGRID = 92160
CFGS = ["vigm", "vigp", "beau", "vigm_atb", "vigp_atb", "beau_atb"]

# ------------------------------------------------------------------ extraction (own glue)
BLOB_FILES = {
    "blob3301": ("onions__avowyfgl5lkzfj3n.onion__pre__index.html",
                 "4f1cef871153b8211472d6afd0acfa120eb331b8793e6eb7690484bcb1f89da2"),
    "blob761": ("onions__cu343l33nqaekrnw.onion__pre__index.html",
                "05acf0d8e2ba7d851e2b4bbc32b85e461a1bd41576a50504487f33d4c1522c56"),
    "blob1033": ("onions__fv7lyucmeozzd5j4.onion__pre__index.html",
                 "d8c0f83cf91d0deda658035e3eb07712b12e72b36ed0e471a71a2fe07dd14ba6"),
}
CANON_FILES = {
    "canon": ("analysis/pp49_51/canon_256.bin",
              "3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290"),
    "decpref": ("analysis/pp49_51/canon_256_decpref.bin",
                "f42b7caa1e7df703a1edda91a715c9164b8c652a9a9dc67bbc8f60a3306b8244"),
}


def extract_blobs():
    out = {}
    for name, (fn, sha) in BLOB_FILES.items():
        path = os.path.join(LP, "analysis", "armada_osint", "onions_ibotpeaches", fn)
        html = open(path, encoding="utf-8", errors="replace").read()
        runs = re.findall(r"[0-9a-fA-F]{512,}", html)
        assert len(runs) == 1, (name, len(runs))
        b = bytes.fromhex(runs[0])
        assert len(b) == 256, (name, len(b))
        got = hashlib.sha256(b).hexdigest()
        assert got == sha, f"{name} sha mismatch: {got}"   # cross-check vs R43-F6 record
        out[name] = b
    for name, (rel, sha) in CANON_FILES.items():
        b = open(os.path.join(LP, rel), "rb").read()
        assert len(b) == 256 and hashlib.sha256(b).hexdigest() == sha, name
        out[name] = b
    return out


# ------------------------------------------------------------------ keystream derivation
def build_streams(obj):
    """[(name, mod-29 key np.array)] per PREREG: 6 single-256 + 3 nib-512 + 18 joined-256."""
    streams = []
    for bn in ("blob761", "blob1033", "blob3301"):
        b = obj[bn]
        streams.append((f"{bn}:mod29", np.array([x % N for x in b], dtype=np.int64)))
        streams.append((f"{bn}:div9", np.array([x // 9 for x in b], dtype=np.int64)))
        nib = []
        for x in b:
            nib.extend((x >> 4, x & 0xF))
        streams.append((f"{bn}:nib", np.array(nib, dtype=np.int64)))
    for cv in ("canon", "decpref"):
        a = obj[cv]
        for bn in ("blob761", "blob1033", "blob3301"):
            b = obj[bn]
            for op, fn in (("xor", lambda u, v: u ^ v), ("add", lambda u, v: (u + v) % 256),
                           ("sub", lambda u, v: (u - v) % 256)):
                j = bytes(fn(u, v) for u, v in zip(a, b))
                streams.append((f"comb:{cv}:{bn}:{op}",
                                np.array([x % N for x in j], dtype=np.int64)))
    assert len(streams) == 27
    assert sum(len(k) for _, k in streams) == 7680
    # distinctness report (PREREG: report, don't dedupe)
    seen, collisions = {}, []
    for name, k in streams:
        t = tuple(k.tolist())
        if t in seen:
            collisions.append((name, seen[t]))
        seen[t] = name
    return streams, collisions


def decode(c, K, cfg):
    """c, K broadcastable int arrays.  R43-F5bT verbatim."""
    x = (N - 1) - c if cfg.endswith("_atb") else c
    base = cfg.split("_")[0]
    if base == "vigm":
        return (x - K) % N
    if base == "vigp":
        return (x + K) % N
    return (K - x) % N


def encode(p, K, cfg):
    """Exact inverse of decode: plaintext + key -> ciphertext (for the plants)."""
    base = cfg.split("_")[0]
    if base == "vigm":
        x = (p + K) % N
    elif base == "vigp":
        x = (p - K) % N
    else:
        x = (K - p) % N
    return (N - 1) - x if cfg.endswith("_atb") else x


def free_bar(L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(NGRID, max(cand), "free")


def key_variants(k):
    return [("fwd", k), ("rev", k[::-1])]


# ------------------------------------------------------------------ positive controls (PREREG)
def to_idx(text):
    out = []
    for w in text.split():
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    return out


PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE "
       "FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED "
       "WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED SOME WISDOM THE PRIMES ARE SACRED "
       "THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS")
PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR "
       "THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL "
       "STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY "
       "YOU WILL DISCOVER AN END TO SELF")
PT3 = ("SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL "
       "THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY A KOAN DURING A LESSON THE MASTER "
       "EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO "
       "EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD")

PLANTS = [  # (name, text, L, stream, dir, cfg, rot)  -- PREREG cells, verbatim
    ("P1", PT1, 240, "blob1033:div9", "fwd", "vigm", 77),
    ("P2", PT2, 200, "comb:decpref:blob761:xor", "rev", "beau", 201),
    ("P3", PT3, 240, "blob3301:nib", "fwd", "vigp_atb", 500),
]


def build_controls(streams):
    sd = dict(streams)
    plants = []
    for name, text, L, sname, dname, cfg, rot in PLANTS:
        p = np.array(to_idx(text)[:L], dtype=np.int64)
        assert len(p) == L, (name, len(p))
        K = sd[sname] if dname == "fwd" else sd[sname][::-1]
        Lk = len(K)
        kk = K[(rot + np.arange(L)) % Lk]
        c = encode(p, kk, cfg)
        plants.append((name, c, dict(stream=sname, dir=dname, cfg=cfg, rot=rot), p))
    return plants


# ------------------------------------------------------------------ the sweep
def sweep_page(c, streams):
    c = np.asarray(c, dtype=np.int64)
    Lp = len(c)
    bar = free_bar(Lp)
    best = {"pmax": -99.0}
    crossers = []
    count = 0
    for sname, K0 in streams:
        for dname, K in key_variants(K0):
            Lk = len(K)
            idx = (np.arange(Lk)[:, None] + np.arange(Lp)[None, :]) % Lk
            Kmat = K[idx]                                     # (Lk, Lp)
            rows, meta = [], []
            for cfg in CFGS:
                rows.append(decode(c[None, :], Kmat, cfg))
                meta.extend((cfg, r) for r in range(Lk))
            X = np.concatenate(rows, axis=0)
            r = A.adjudicate_batch(X, pan=PAN)
            count += X.shape[0]
            pm = r["pmax"]
            i = int(pm.argmax())
            if pm[i] > best["pmax"]:
                cfg, rot = meta[i]
                best.update(pmax=float(pm[i]), preg=int(r["preg"][i]), stream=sname,
                            dir=dname, cfg=cfg, rot=rot, L=int(Lp), bar=round(float(bar), 4),
                            decode=X[i].tolist())
            for j in np.nonzero(pm >= bar)[0]:
                full = A.adjudicate(X[j], pan=PAN)
                if not full["degenerate"] and full["pmax"] >= bar:
                    cfg, rot = meta[int(j)]
                    crossers.append(dict(pmax=float(full["pmax"]), preg=int(full["preg"]),
                                         stream=sname, dir=dname, cfg=cfg, rot=rot, L=int(Lp),
                                         bar=round(float(bar), 4), decode=X[int(j)].tolist()))
    return count, best, crossers


def full_stats(dec):
    f = A.adjudicate(np.array(dec, dtype=np.int64), pan=PAN)
    return {k: (round(float(f[k]), 4) if isinstance(f[k], float) else f[k])
            for k in ("en", "pmax", "preg", "pmax_ne", "pcon", "pcreg",
                      "ioc", "mds", "h2", "zl", "degenerate")} | {
           "z": [round(float(v), 2) for v in f["z"]]}


def main():
    t0 = time.time()
    obj = extract_blobs()
    streams, collisions = build_streams(obj)
    pages = load_pages()[:-2]
    assert len(pages) == 55
    per_cfg = sum(len(k) for _, k in streams)
    assert per_cfg * 2 * 6 == NGRID, per_cfg

    out = {"prereg": "PREREG.md", "ngrid_per_page": NGRID,
           "bars": {str(L): round(float(free_bar_L), 4) for L, free_bar_L in
                    ((120, free_bar(120)), (240, free_bar(240)))},
           "objects_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in obj.items()},
           "stream_names": [s for s, _ in streams],
           "mod29_key_collisions": collisions,
           "controls": [], "pages": [], "crossers": [], "verdict": None}

    # ---- controls FIRST (gate)
    plants = build_controls(streams)
    ok = True
    for name, cipher, cell, p in plants:
        cnt, best, cross = sweep_page(cipher, streams)
        assert cnt == NGRID, (name, cnt)
        hit = (best["pmax"] >= best["bar"]
               and all(best[k] == cell[k] for k in ("stream", "dir", "cfg", "rot")))
        recovered = bool(hit and best["decode"] == list(map(int, p)))
        full = A.adjudicate(np.array(best["decode"], dtype=np.int64), pan=PAN)
        rec = dict(control=name, planted=cell,
                   grid_best={k: best[k] for k in ("pmax", "preg", "stream", "dir",
                                                   "cfg", "rot", "L", "bar")},
                   non_degenerate=bool(not full["degenerate"]),
                   found_planted_cell=bool(hit), plaintext_recovered=recovered,
                   passed=bool(hit and recovered and not full["degenerate"]))
        out["controls"].append(rec)
        ok &= rec["passed"]
        print(json.dumps(rec), flush=True)
    out["control_gate"] = "passed" if ok else "FAILED"
    if not ok:
        out["verdict"] = "KILLED - positive control failed; no keystream verdict"
        json.dump(out, open(os.path.join(HERE, "p4_results.json"), "w"), indent=1)
        print(out["verdict"])
        return

    # ---- the real pages
    gbest = {"pmax": -99.0}
    for pi, c in enumerate(pages):
        cnt, best, cross = sweep_page(c, streams)
        assert cnt == NGRID
        dec = best.pop("decode", None)
        best["page"] = pi
        best["full"] = full_stats(dec)                  # R3 stats for the per-page best
        out["pages"].append(best)
        for x in cross:
            x["page"] = pi
            x["full"] = full_stats(x["decode"])
        out["crossers"].extend(cross)
        if best["pmax"] > gbest["pmax"]:
            gbest = dict(best)
        if pi % 5 == 0:
            print("page %d/55 gbest %.3f (page %s %s/%s/%s rot %s) %.0fs"
                  % (pi, gbest["pmax"], gbest.get("page"), gbest.get("stream"),
                     gbest.get("dir"), gbest.get("cfg"), gbest.get("rot"),
                     time.time() - t0), flush=True)

    out["observed_global_best"] = gbest
    out["n_decodes_total"] = NGRID * len(pages)
    out["n_crossers"] = len(out["crossers"])
    out["verdict"] = ("NEGATIVE" if not out["crossers"]
                      else "CROSSER(S) - FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, not certified")
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "p4_results.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("control_gate", "observed_global_best",
                                          "n_decodes_total", "n_crossers", "verdict",
                                          "bars", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
