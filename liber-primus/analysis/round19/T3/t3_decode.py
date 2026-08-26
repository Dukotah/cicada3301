"""T3 — CHANNEL K. Do the NEGATIVES survive a noisy transcription?

Every statistic in the other arms is a property of the ciphertext. The repo's ~10^10
negatives are properties of a DECODE. This arm asks the question those negatives depend on
and that nobody has asked:

    if the transcription carries k wrong runes, would a sweep still have RANKED the
    correct key above noise?

Design (PREREG §2.6), bar-free by construction:
  1. plaintext = the real LP1 solved-page register (SOLVED-PAGES.json), rune indices;
  2. encipher under a known keystream with `campaign18_skip.encipher_keyskip(supp=0.83)`
     -- the repo's pinned filter, unmodified;
  3. corrupt k ciphertext runes (uniform substitution) -- the transcription error;
  4. decode with the CORRECT key through round18/L2 `fastbeam.beam_decode`
     (gate-F0-identical to `skipdecode.beam_decode`), beam_w=400, max_skip=3;
  5. record score_norm and rune-index recovery, and the same for a WRONG key in the
     same cell.

No absolute score bar is used anywhere: the endpoints are
  K-REC  median recovery < 0.90   (L2's own B.3 gate value)
  K-SEP  correct-key p05 < wrong-key p95 in the SAME cell

Run: python3 t3_decode.py            (writes out_decode.json)
"""
import json, os, random, statistics, sys, hashlib, time
import t3_lib as T

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(T.ROOT, "analysis", "round18", "L2-filter-leak"))
sys.path.insert(0, os.path.join(T.ROOT, "analysis", "campaign18_skip"))

import fastbeam                                   # noqa: E402
import skipdecode as sk                           # noqa: E402
from lp import gematria as gp                     # noqa: E402

SUPP = 0.83
BEAM_W = 400
MAX_SKIP = 3


def lp1_plaintext():
    """The real LP1 register: the solved pages' own plaintext, as rune indices."""
    d = json.load(open(os.path.join(T.ROOT, "SOLVED-PAGES.json"), encoding="utf-8"))
    txt = ""
    def walk(o):
        nonlocal txt
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("plaintext_transliteration", "plaintext", "plain", "decoded"):
                    if isinstance(v, str):
                        txt += v
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
    idxs = []
    i = 0
    up = "".join(ch for ch in txt.upper() if ch.isalpha())
    # transliteration -> rune index, longest match first (7 of 29 runes are 2 chars)
    two = {t: i for i, t in gp.IDX_TO_TRANS.items() if len(t) == 2}
    one = {t: i for i, t in gp.IDX_TO_TRANS.items() if len(t) == 1}
    while i < len(up):
        if up[i:i + 2] in two:
            idxs.append(two[up[i:i + 2]]); i += 2
        elif up[i] in one:
            idxs.append(one[up[i]]); i += 1
        else:
            i += 1
    return idxs


def kjv_plaintext(n):
    """EN_KJV register in rune indices -- used only where LP1's 1,768-rune pool is too
    short (the full-book cell). L7-A power 1.00."""
    txt = open(os.path.join(T.ROOT, "data", "kjv.txt"), encoding="utf-8", errors="ignore").read()
    up = "".join(ch for ch in txt.upper() if ch.isalpha())
    up = (up.replace("K", "C").replace("V", "U").replace("Q", "C").replace("Z", "S"))
    two = {t: i for i, t in gp.IDX_TO_TRANS.items() if len(t) == 2}
    one = {t: i for i, t in gp.IDX_TO_TRANS.items() if len(t) == 1}
    idxs, i = [], 0
    while i < len(up) and len(idxs) < n:
        if up[i:i + 2] in two:
            idxs.append(two[up[i:i + 2]]); i += 2
        elif up[i] in one:
            idxs.append(one[up[i]]); i += 1
        else:
            i += 1
    return idxs


def keystream(seed, n):
    """sha256-CTR keystream over 29 symbols -- the B-04/D3 live class."""
    out, ctr = [], 0
    while len(out) < n:
        h = hashlib.sha256(f"{seed}:{ctr}".encode()).digest()
        out.extend(b % 29 for b in h)
        ctr += 1
    return out[:n]


def cell(P, kseed, wrong_seed, eseed, k, L):
    """One replicate. Returns (score_correct, rec_correct, score_wrong, rec_wrong)."""
    rng = random.Random(eseed)
    K = keystream(kseed, L * (MAX_SKIP + 2) + 64)
    KW = keystream(wrong_seed, L * (MAX_SKIP + 2) + 64)
    C, skips, used = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=eseed)
    Cn = list(C)
    if k:
        for i in rng.sample(range(len(Cn)), min(k, len(Cn))):
            Cn[i] = rng.choice([v for v in range(29) if v != Cn[i]])
    rc = fastbeam.beam_decode(Cn, K, sign=-1, beam_w=BEAM_W, max_skip=MAX_SKIP)
    rw = fastbeam.beam_decode(Cn, KW, sign=-1, beam_w=BEAM_W, max_skip=MAX_SKIP)
    recc = sum(1 for a, b in zip(rc["plain_idx"], P) if a == b) / len(P)
    recw = sum(1 for a, b in zip(rw["plain_idx"], P) if a == b) / len(P)
    # RIGID reference: decode with the true key at the TRUE key indices, no beam.
    # Its recovery is exactly 1 - k/L by construction -- it isolates "the errors
    # themselves" from "the beam losing key synchronisation".
    rigid = sum(1 for i, u in enumerate(used) if (Cn[i] - K[u]) % 29 == P[i]) / len(P)
    return (rc["score"], recc, rw["score"], recw,
            rc.get("n_skips"), sum(skips), rigid)


def band(v):
    v = sorted(v)
    n = len(v)
    return {"median": statistics.median(v), "mean": statistics.fmean(v),
            "sd": statistics.pstdev(v) if n > 1 else 0.0,
            "p05": v[max(0, int(0.05 * n) - 1)], "p95": v[min(n - 1, int(0.95 * n))],
            "min": v[0], "max": v[-1]}


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    REG = sys.argv[3] if len(sys.argv) > 3 else "LP1"

    # gate F0 -- fastbeam identical to the repo beam, re-run in this lane
    g = fastbeam.gate_F0(reps=10, lengths=(120, 400), seed=20260826, verbose=False)
    print("gate F0:", json.dumps(g))
    assert g["pass"], g

    PT = lp1_plaintext() if REG == "LP1" else kjv_plaintext(L * (REPS + 2) + 4000)
    print(f"{REG} plaintext pool: {len(PT)} runes")
    assert len(PT) >= L + 50, len(PT)

    # transcription error RATES matched to absolute k over 12,956, so the x-axis is
    # comparable with the other arms:  eps = k_book / 12956,  k_cell = round(eps * L)
    KBOOK = [int(x) for x in os.environ.get("T3_KBOOK","0,5,10,20,30,50,100,200,450,900,1800,3600,6478,12956").split(",")]
    out = {"L": L, "reps": REPS, "supp": SUPP, "beam_w": BEAM_W, "max_skip": MAX_SKIP,
           "gate_F0": g, "conditionals": {
               "decoder": "campaign18_skip.encipher_keyskip -> round18/L2 fastbeam.beam_decode "
                          "(key-skip only; L7-B: does NOT cover skip_by_two or free drift)",
               "adjudicator": "lp.score Quadgram.score_norm (ENGLISH ONLY; L7-A power 0.33 Latin, "
                              "0.00 vowel-dropped English)",
               "register": "LP1_REAL (the solved pages' own plaintext) -- L7-A power 1.00"},
           "rows": []}

    for kb in KBOOK:
        kc = round(kb * L / 12956)
        sc, rc, sw, rw, dsk, rg, derail = [], [], [], [], [], [], []
        t0 = time.time()
        for t in range(REPS):
            st = 7 + t * (L + 13)
            P = PT[st % (len(PT) - L): st % (len(PT) - L) + L]
            a, b, c, d, ns, ts, rgd = cell(P, f"CICADA3301-{t}", f"WRONGKEY-{t}",
                                           90000 + t, kc, L)
            sc.append(a); rc.append(b); sw.append(c); rw.append(d); rg.append(rgd)
            derail.append(1.0 if b < rgd - 0.10 else 0.0)
            dsk.append(abs((ns if ns is not None else ts) - ts))
        row = {"k_book": kb, "eps": kb / 12956, "k_cell": kc,
               "score_correct": band(sc), "recovery_correct": band(rc),
               "score_wrong": band(sw), "recovery_wrong": band(rw),
               "recovery_rigid_truekeyidx": band(rg),
               "skip_count_error": band(dsk),
               "derail_fraction": sum(derail) / len(derail),
               "graceful_recovery_expected": 1.0 - kc / L,
               "separated": bool(band(sc)["p05"] > band(sw)["p95"]),
               "secs": round(time.time() - t0, 1)}
        out["rows"].append(row)
        print(f"  k_book={kb:6d} (eps={kb/12956:.4f}, k_cell={kc:3d})  "
              f"correct score med={row['score_correct']['median']:.3f} p05={row['score_correct']['p05']:.3f} "
              f"rec={row['recovery_correct']['median']:.3f} rigid={row['recovery_rigid_truekeyidx']['median']:.3f} "
              f"derail={row['derail_fraction']:.2f} | "
              f"wrong med={row['score_wrong']['median']:.3f} p95={row['score_wrong']['p95']:.3f} | "
              f"sep={row['separated']}  ({row['secs']}s)", flush=True)

    # endpoints
    krec = next((r["k_book"] for r in out["rows"]
                 if r["recovery_correct"]["median"] < 0.90), None)
    ksep = next((r["k_book"] for r in out["rows"] if not r["separated"]), None)
    out["K_REC_k_book"] = krec
    out["K_SEP_k_book"] = ksep
    print(f"K-REC (median recovery < 0.90) at k_book = {krec}")
    print(f"K-SEP (correct p05 <= wrong p95) at k_book = {ksep}")
    out["register"] = REG
    json.dump(out, open(os.path.join(HERE, f"out_decode_L{L}_{REG}.json"), "w"), indent=1)
    print(f"wrote out_decode_L{L}_{REG}.json")


if __name__ == "__main__":
    main()
