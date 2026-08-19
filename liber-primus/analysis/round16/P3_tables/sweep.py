"""Round 16 / lane P3 - dense-offset sweep of the printed-table and Cicada-published pads.

Instrument: analysis/round16/lib_padsweep.py (control PASSED 2026-08-19: 8/8 planted pads
recovered by the beam, dense-prefilter survival 0.625).  lib_padsweep is SHARED - this file
adds its extra keystream builders locally and never edits it.

Extra builders added here
-------------------------
lib_padsweep's six builders are byte-oriented.  Two of this lane's pad families are not
bytes at all as published:

  * a printed DECIMAL TABLE.  A reader of RAND's book handles digits, so the natural
    keystreams are digit-native: one digit per rune, digit PAIRS mod 29, digit TRIPLES
    mod 29, five-digit GROUPS mod 29 (the book's printed grouping), and overlapping pairs.
  * ASCII ARMOR / HEX / BASE32 TEXT.  A reader copying a signature block off a web page
    handles base64 characters.  `textchars` reads them through the repo's eng_to_idx
    (letters only, the project's keytext convention); `charval_b64/hex/b32` use each
    character's alphabet VALUE.

Adjudication
------------
HIT iff score_norm >= -5.5 AND >= null_max + 0.5.  Since bar = max(-5.5, null_max+0.5)
is >= -5.5 by construction, any configuration scoring below -5.5 cannot be a HIT whatever
its null is; nulls (n=200, A1's shuffle null under the exact keystream) are therefore
computed for every configuration that reaches -5.5, plus a reference null per pad.

Run:  python liber-primus/analysis/round16/P3_tables/sweep.py
"""
import os, sys, json, time, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import numpy as np                                            # noqa: E402
import lib_padsweep as L                                      # noqa: E402
import skipdecode as sk                                       # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "benchmark")))
import null as nullmod                                        # noqa: E402

N = L.N
PADS = os.path.join(HERE, "data", "pads")
MANIFEST = os.path.join(HERE, "pads_manifest.json")
OUT = os.path.join(HERE, "results.json")
PARTIAL = os.path.join(HERE, "data", "partial")
SURVIVAL = 0.625            # measured dense-prefilter survival, lib_padsweep.control()
TEXTCHARS_MAX = 2_000_000   # eng_to_idx is pure python; skipped above this pad size


# ------------------------------------------------------------- extra builders
B64AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
B32AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
HEXAL = "0123456789abcdef"


def _digits(b):
    a = np.frombuffer(b, dtype=np.uint8)
    return (a[(a >= 48) & (a <= 57)] - 48).astype(np.int16)


def dig1(b):
    """one printed digit per rune (0-9 used directly as a rune index)"""
    return _digits(b)


def dig2(b):
    d = _digits(b); d = d[:len(d) // 2 * 2]
    return ((d[0::2] * 10 + d[1::2]) % N).astype(np.int16)


def dig2ov(b):
    d = _digits(b)
    return ((d[:-1] * 10 + d[1:]) % N).astype(np.int16)


def dig3(b):
    d = _digits(b).astype(np.int32); d = d[:len(d) // 3 * 3]
    return ((d[0::3] * 100 + d[1::3] * 10 + d[2::3]) % N).astype(np.int16)


def dig5(b):
    """the book's printed five-digit groups, mod 29"""
    d = _digits(b).astype(np.int64); d = d[:len(d) // 5 * 5]
    v = np.zeros(len(d) // 5, dtype=np.int64)
    for k in range(5):
        v = v * 10 + d[k::5]
    return (v % N).astype(np.int16)


def _pairs(b, overlap=False):
    d = _digits(b).astype(np.int16)
    if overlap:
        return d[:-1] * 10 + d[1:]
    d = d[:len(d) // 2 * 2]
    return d[0::2] * 10 + d[1::2]


def dig2_rej29(b):
    """the TEXTBOOK way to read a printed decimal table as a mod-29 pad:
    take two digits, use the value if it is 00-28, otherwise discard and read on."""
    v = _pairs(b)
    return v[v < N]


def dig2_rej87(b):
    """the efficient variant: accept 00-86 (3 x 29) and reduce mod 29"""
    v = _pairs(b)
    return (v[v < 3 * N] % N).astype(np.int16)


def dig2ov_rej29(b):
    """the same rejection rule read with a sliding, overlapping window"""
    v = _pairs(b, overlap=True)
    return v[v < N]


def dig2_rej26(b):
    """pairs read as A1Z26 letters (01-26), the classic pencil-and-paper reading"""
    v = _pairs(b)
    return (v[(v >= 1) & (v <= 26)] - 1).astype(np.int16)


def _charval(b, alphabet):
    lut = np.full(256, -1, dtype=np.int16)
    for i, c in enumerate(alphabet):
        lut[ord(c)] = i
    a = np.frombuffer(b, dtype=np.uint8)
    v = lut[a]
    return (v[v >= 0] % N).astype(np.int16)


def charval_b64(b):
    return _charval(b, B64AL)


def charval_hex(b):
    return _charval(b, HEXAL)


def charval_b32(b):
    return _charval(b, B32AL)


def textchars(b):
    """the pad READ AS TEXT through eng_to_idx (letters only) - the keytext convention"""
    return np.array(sk.eng_to_idx(b.decode("latin-1")), dtype=np.int16)


DIGIT_BUILDERS = {"dig1": dig1, "dig2": dig2, "dig2ov": dig2ov,
                  "dig3": dig3, "dig5": dig5,
                  "dig2_rej29": dig2_rej29, "dig2_rej87": dig2_rej87,
                  "dig2ov_rej29": dig2ov_rej29, "dig2_rej26": dig2_rej26}
TEXT_BUILDERS = {"textchars": textchars, "charval_b64": charval_b64,
                 "charval_hex": charval_hex, "charval_b32": charval_b32}


def classify(b):
    """which extra builders are meaningful for this pad"""
    a = np.frombuffer(b[:200000], dtype=np.uint8)
    frac_dig = float(((a >= 48) & (a <= 57)).mean())
    frac_pr = float(((a >= 32) & (a < 127)).mean())
    ex = {}
    if frac_dig > 0.80:
        ex.update(DIGIT_BUILDERS)
    if frac_pr > 0.95:
        # eng_to_idx is a pure-python greedy matcher (~30 us/kB); it is skipped on pads
        # over TEXTCHARS_MAX bytes and on all-digit pads (where it returns nothing).
        # That is a recorded coverage limit, not a claim.
        if frac_dig <= 0.80 and len(b) <= TEXTCHARS_MAX:
            ex["textchars"] = textchars
        hexlike = float(np.isin(a, np.frombuffer(HEXAL.encode(), dtype=np.uint8)).mean())
        b32like = float(np.isin(a, np.frombuffer((B32AL + B32AL.lower()).encode(),
                                                 dtype=np.uint8)).mean())
        if hexlike > 0.95:
            ex["charval_hex"] = charval_hex
        if b32like > 0.95:
            ex["charval_b32"] = charval_b32
        ex["charval_b64"] = charval_b64
    return ex, {"frac_digit": round(frac_dig, 4), "frac_printable": round(frac_pr, 4)}


def all_keystreams(b):
    ks = L.build_keystreams(b)                    # 6 byte builders x {fwd, rev}
    extra, meta = classify(b)
    for name, fn in extra.items():
        try:
            ks[name] = fn(b)
            ks[name + "_rev"] = fn(b[::-1])
        except Exception as e:
            print(f"    ! builder {name} failed: {e}")
    return ks, meta


# ------------------------------------------------------------- head sizing
def head_for(nk):
    """Largest head window a keystream of nk symbols can carry under max_skip=3.

    A pad shorter than ~13k symbols cannot key the 12,956-rune stream at all; a pad
    shorter than 400*(max_skip+1)+8 = 1,608 symbols cannot even carry the standard
    400-rune head, and is swept against a proportionally shorter head with its own null.
    """
    cap = (nk - 8) // (L.MAX_SKIP + 1) - 1
    return int(max(24, min(L.HEAD, cap)))


def escalate_head(hits, K, C, sign, head, top=40):
    Kl = [int(x) for x in K]
    out = []
    for score, o in hits[:top]:
        o = int(o)
        if o + head * (L.MAX_SKIP + 1) + 8 >= len(Kl):
            continue
        bd = sk.beam_decode([int(x) for x in C[:head]], Kl, sign=sign, o=o,
                            beam_w=L.BEAM_W, max_skip=L.MAX_SKIP)
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": float(bd["score"]), "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


# ------------------------------------------------------------- main
def main(only=None, out=None, budget=540.0):
    """Sweep pads, checkpointing one JSON per pad into data/partial/ so the run is
    resumable (each invocation stops after `budget` seconds and is simply re-run)."""
    os.makedirs(PARTIAL, exist_ok=True)
    man = json.load(open(MANIFEST))
    if only:
        man["pads"] = [p for p in man["pads"] if p["name"] in only]
    C = L.nc.unsolved()
    L.trigram_model()
    print(f"unsolved stream: {len(C)} runes\n")

    out_path = out or OUT
    rows, per_pad, n_trials, nulls = [], [], 0, {}
    t0 = time.time()
    for p in man["pads"]:
        name = p["name"]
        ck = os.path.join(PARTIAL, name + ".json")
        if os.path.exists(ck):
            continue
        if time.time() - t0 > budget:
            print(f"[budget {budget:.0f}s reached - re-run to continue]")
            break
        b = open(os.path.join(PADS, name + ".bin"), "rb").read()
        ks, meta = all_keystreams(b)
        pad_rec = {"pad": name, "bytes": len(b), "sha256": p["sha256"],
                   "source": p["source"], "keys_full_stream": p["keys_full_stream"],
                   "content": meta, "variants": {}, "n_offsets_scanned": 0}
        print(f"[{name}] {len(b):,} B  {len(ks)} variants  digit={meta['frac_digit']:.2f}")
        best_pad = None
        for vname, K in sorted(ks.items()):
            nk = int(len(K))
            if nk < 64:
                continue
            head = head_for(nk)
            noff = max(0, nk - L.PREFILTER_LEN)
            for sign in (-1, +1):
                hits = L.dense_scan(K, C, sign=sign)
                res = escalate_head(hits, K, C, sign, head)
                n_trials += noff
                pad_rec["n_offsets_scanned"] += noff
                if not res:
                    continue
                top = res[0]
                key = f"{vname}|sign{sign:+d}"
                pad_rec["variants"][key] = {
                    "ks_len": nk, "head": head, "offsets": noff,
                    "best_score": top["score"], "best_offset": top["offset"],
                    "best_pre": top["pre"], "head_translit": top["head"],
                }
                r = dict(top); r["pad"] = name; r["variant"] = vname
                r["ks_len"] = nk; r["head"] = head
                rows.append(r)
                if best_pad is None or top["score"] > best_pad["score"]:
                    best_pad = r
        pad_rec["best"] = best_pad
        per_pad.append(pad_rec)
        if best_pad:
            print(f"    best {best_pad['score']:+.3f}  "
                  f"{best_pad['variant']} sign{best_pad['sign']:+d} "
                  f"off={best_pad['offset']} head={best_pad['head']}  "
                  f"({pad_rec['n_offsets_scanned']:,} offsets, {time.time()-t0:.0f}s)")

        # ---- nulls, computed inline while this pad's keystreams are in memory -----
        # bar = max(-5.5, null_max + 0.5) >= -5.5 always, so anything under -5.5 cannot
        # be a HIT whatever its null is.  Nulls are computed for (a) every configuration
        # of this pad that reaches -5.5 and (b) the pad's single best, as a reference.
        need = [r for r in rows if r["pad"] == name and r["score"] >= -5.5]
        if best_pad and best_pad not in need:
            need.append(best_pad)
        seen = set()
        for r in need:
            k = (r["pad"], r["variant"], r["head"])
            if k in seen:
                continue
            seen.add(k)
            nm, nx = L.null_ceiling(ks[r["variant"]], seq_len=r["head"], n=200)
            nulls["|".join(map(str, k))] = {"null_mean": nm, "null_max": nx,
                                            "bar": L.hit_bar(nx), "best": r["score"],
                                            "HIT": r["score"] >= L.hit_bar(nx)}
            print(f"    null {r['variant']}(head={r['head']}): mean={nm:.3f} "
                  f"max={nx:.3f} bar={L.hit_bar(nx):.3f} best={r['score']:.3f}")
        del ks
        json.dump({"pad_rec": pad_rec,
                   "rows": [r for r in rows if r["pad"] == name],
                   "nulls": {k: v for k, v in nulls.items() if k.startswith(name + "|")}},
                  open(ck, "w"), indent=1)

    # ---- collect every checkpoint (this run's and earlier runs') ---------
    rows, per_pad, nulls, n_trials = [], [], {}, 0
    names = [p["name"] for p in json.load(open(MANIFEST))["pads"]]
    missing = []
    for nm_ in names:
        ck = os.path.join(PARTIAL, nm_ + ".json")
        if not os.path.exists(ck):
            missing.append(nm_)
            continue
        d = json.load(open(ck))
        per_pad.append(d["pad_rec"])
        rows.extend(d["rows"])
        nulls.update(d["nulls"])
        n_trials += d["pad_rec"]["n_offsets_scanned"]
    if missing:
        print(f"INCOMPLETE - {len(missing)} pads not yet swept: {missing}")
    rows.sort(key=lambda r: r["score"], reverse=True)
    hits = [k for k, v in nulls.items() if v["HIT"]]
    best = rows[0] if rows else None
    fw = nullmod.threshold_for(n_trials)
    eff = int(round(n_trials * SURVIVAL))

    out = {
        "lane": "round16/P3_tables",
        "hypothesis": ("(a) printed random-number tables (RAND 1955); "
                       "(b) Cicada's own published high-entropy bytes as a pad"),
        "instrument": "analysis/round16/lib_padsweep.py",
        "control": {"status": "PASS (lib_padsweep.control, 2026-08-19)",
                    "beam_recovered": "8/8", "dense_survival": SURVIVAL},
        "n_pads": len(per_pad),
        "n_offsets_scanned": n_trials,
        "n_offsets_effective_after_survival_discount": eff,
        "prereg_bar": "score_norm >= -5.5 AND >= null_max + 0.5",
        "benchmark_null_threshold_for_n_trials": fw,
        "best_raw": best,
        "HITS": hits,
        "pads_not_yet_swept": missing,
        "verdict": ("INCOMPLETE" if missing else
                    ("NEGATIVE (no configuration reached the bar)" if not hits else "HIT")),
        "nulls": nulls,
        "top20": rows[:20],
        "per_pad": per_pad,
        "runtime_sec": round(time.time() - t0, 1),
    }
    json.dump(out, open(out_path, "w"), indent=1)

    print("\n" + "=" * 78)
    print(f"pads {len(per_pad)}   offsets scanned {n_trials:,}   "
          f"effective (x{SURVIVAL}) {eff:,}")
    if best:
        print(f"best raw score_norm  {best['score']:+.3f}   "
              f"({best['pad']} / {best['variant']} sign{best['sign']:+d} "
              f"off={best['offset']})")
    print(f"pre-registered bar   -5.500 (and >= null_max+0.5)")
    print(f"benchmark/null.threshold_for({n_trials:,}) = {fw:+.3f}")
    print(f"HITS: {hits if hits else 'none'}")
    print(f"VERDICT: {out['verdict']}")
    print(f"wrote {out_path}  ({out['runtime_sec']}s)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated pad names to sweep")
    ap.add_argument("--out", help="results path (default results.json)")
    ap.add_argument("--budget", type=float, default=540.0,
                    help="seconds before this invocation stops; re-run to continue")
    a = ap.parse_args()
    main(only=set(a.only.split(",")) if a.only else None, out=a.out,
         budget=a.budget)
