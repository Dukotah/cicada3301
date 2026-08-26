"""L6 - TIER-2 adjudication (PREREG s2.2) of anything flagged.

A correct key gets BETTER as more text is added; a lucky one decays toward the noise mean.
Round 13 stage D is the precedent: 0 of 150 survivors improved, and the best fell from
-6.654 to -7.239 on the full stream. This runs the same check on this lane's flagged rows.

Also reports the reference IoC*N of real Liber Primus plaintext, so a flagged IoC can be
read against what a real hit would look like rather than only against the null.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L
import skipdecode as sk

N = 29


def ioc_n(p):
    p = np.asarray(p)
    c = np.bincount(p, minlength=N).astype(float)
    n = p.size
    return float((c * (c - 1)).sum() / (n * (n - 1)) * N)


def main():
    la = json.load(open(os.path.join(X.OUT, "langagnostic.json")))
    man = json.load(open(os.path.join(X.DATA, "MANIFEST.json")))
    padmap = {p["name"]: os.path.join(X.DATA, "iso", p["extracted"])
              for p in man["verified_pads"]}
    padmap["MARSAGLIA_CDROM.iso"] = os.path.join(X.DATA, "MARSAGLIA_CDROM.iso")

    # reference: what a REAL hit looks like on these statistics
    sp = json.load(open(os.path.join(X.ROOT, "SOLVED-PAGES.json"), encoding="utf-8"))
    lp1 = sk.eng_to_idx("".join(p["plaintext_transliteration"] for p in sp["pages"]))
    ref = {"lp1_solved_plaintext_ioc_times_n": round(ioc_n(lp1), 4),
           "lp1_runes": len(lp1),
           "ciphertext_ioc_times_n": round(ioc_n([int(x) for x in L.nc.unsolved()]), 4)}
    print("reference:", ref, flush=True)

    C0 = [int(x) for x in L.nc.unsolved()]
    segs = L.nc.segments()
    page0 = [int(x) for x in segs[0]]
    rows = []
    for a in la.get("anomalies", []):
        r = a["row"]
        if "pad" not in r:
            continue
        fp = padmap.get(r["pad"])
        arr = np.fromfile(fp, dtype=np.uint8)
        src = arr[::-1] if r.get("rev") else arr
        fn, spb = X.BUILDERS[r["builder"]]
        o = int(r["offset"]); b0 = o // spb
        out = {"flagged": a.get("stat") or a.get("register"), **{k: r[k] for k in
               ("pad", "builder", "rev", "offset", "english_score", "ioc_times_n")}}
        for name, C in (("head400", C0[:400]), ("page0_full", page0),
                        ("full_stream", C0)):
            need = len(C) * (X.MS + 1) + 64
            b1 = min(arr.size, b0 + need // spb + 64)
            K = [int(x) for x in fn(np.ascontiguousarray(src[b0:b1]))]
            loc = o - b0 * spb
            if loc + need >= len(K):
                out[name] = None
                continue
            bd = sk.beam_decode(C, K, sign=int(r["sign"]) if "sign" in r else 1,
                                o=loc, beam_w=X.BEAM_W2, max_skip=X.MS)
            out[name] = {"score": round(bd["score"], 4), "runes": len(C),
                         "ioc_times_n": round(ioc_n(bd["plain_idx"]), 4),
                         "head": bd["translit"][:64]}
            print(f"  {r['pad']}/{r['builder']} off={o} {name}: "
                  f"score={out[name]['score']} ioc*N={out[name]['ioc_times_n']}", flush=True)
            del K
        h, f = out.get("head400"), out.get("full_stream")
        out["improves_with_more_text"] = bool(h and f and f["score"] > h["score"])
        rows.append(out)
        del arr, src

    res = {"reference": ref, "rows": rows,
           "verdict": ("no flagged row improves under escalation - every one decays toward "
                       "the noise mean, which is the signature of a lucky draw, not a key"
                       if rows and not any(r["improves_with_more_text"] for r in rows)
                       else ("nothing was flagged" if not rows else
                             "a flagged row IMPROVED under escalation - INSPECT"))}
    X.jdump(res, os.path.join(X.OUT, "tier2.json"))
    print("\n" + res["verdict"])


if __name__ == "__main__":
    main()
