"""L7 / sub-attack A-i,A-ii — how much power does the English quadgram scorer lose when the
plaintext is NOT modern English?

Every negative in this repository was adjudicated by `lp.score.Quadgram.score_norm` against a
fixed English band (>= -5.5). This script measures, for each plaintext register, what the
**correct key** scores under the repo's own instrument. If a register's correct-key score sits
below the bar, every sweep's negative is silent about that register.

Instrument is the repo's, unchanged:
    encipher_keyskip(supp=0.83)  ->  beam_decode(beam_w=400, max_skip=3)  ->  score_norm
Recovery is measured on RUNE INDICES (AGENTS.md s4).

    python3 a1_scorer_language.py            # full run, writes out_a1.json
    python3 a1_scorer_language.py --quick    # 3 replicates, L=120 only
"""
import os, sys, json, random, re, statistics, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"), B6):
    sys.path.insert(0, p)

from lp import gematria as gp                 # noqa: E402
from lp import score as _score                # noqa: E402
import skipdecode as sk                       # noqa: E402
import plant as PL                            # noqa: E402
import detectors as D                         # noqa: E402

N = gp.N
Q = _score.default()
BEAM_W, MAX_SKIP, SUPP = 400, 3, 0.83
LENGTHS = [31, 120, 240, 400]
NREP = 12
SEED0 = 33010


# --------------------------------------------------------------------- corpora
def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _mid(t):
    """Drop Gutenberg boiler-plate head/tail crudely, as B6's loader does."""
    return t[len(t) // 8: -len(t) // 8] if len(t) > 40000 else t


def _drop_vowels(text, frac=1.0, seed=7):
    r = random.Random(seed)
    out = []
    for ch in text.upper():
        if ch in "AEIOUY" and (frac >= 1.0 or r.random() < frac):
            continue
        out.append(ch)
    return "".join(out)


def build_panels():
    """Each panel -> a long list of rune indices (the plaintext stream)."""
    P = {}

    # --- English, held out of the quadgram training set -----------------------
    en_held = _mid(_read(os.path.join(LP, "data", "keys", "self_reliance.txt"))) + \
              _mid(_read(os.path.join(LP, "data", "keys", "mabinogion.txt")))
    P["EN_MODERN"] = D.text_to_runes(en_held, "EN").tolist()

    # --- English, IN the training set (upper bound) ---------------------------
    P["EN_KJV"] = D.text_to_runes(_mid(_read(os.path.join(LP, "data", "kjv.txt")))[:900000],
                                  "EN").tolist()

    # --- the REAL LP1 register: the solved pages' own plaintext ---------------
    sp = json.load(open(os.path.join(LP, "SOLVED-PAGES.json"), encoding="utf-8"))
    lp1 = "".join(p["plaintext_transliteration"] for p in sp["pages"])
    # already in transliteration space: greedy longest-match parse is its inverse
    P["LP1_REAL"] = sk.eng_to_idx(lp1)

    # --- Latin ----------------------------------------------------------------
    la = _mid(_read(os.path.join(LP, "analysis", "latin", "latin_218.txt"))) + \
         _mid(_read(os.path.join(LP, "analysis", "latin", "latin_28233.txt")))
    P["LATIN"] = D.text_to_runes(la, "LA").tolist()

    # --- Old English (B6's extraction: lines carrying thorn/eth/ash) ----------
    oe_raw = _read(os.path.join(B6, "corpora", "oe_beowulf.txt"))
    oe = "\n".join(l for l in oe_raw.split("\n") if re.search(r"[þðæÞÐÆ]", l))
    oe += _read(os.path.join(LP, "data", "keys", "runepoem_oe.txt"))
    P["OE"] = D.text_to_runes(oe, "OE").tolist()

    # --- German / Welsh, extra non-English references -------------------------
    de = _mid(_read(os.path.join(B6, "corpora", "de_faust.txt"))) + \
         _mid(_read(os.path.join(B6, "corpora", "de_2.txt")))
    P["DE"] = D.text_to_runes(de, "DE").tolist()
    cy = _mid(_read(os.path.join(LP, "data", "keys", "welsh", "welsh_mabinogion.txt")))
    P["CY"] = D.text_to_runes(cy, "CY").tolist()

    # --- abbreviated / vowel-dropped English ----------------------------------
    P["EN_NOVOWEL"] = D.text_to_runes(_drop_vowels(en_held, 1.0), "EN").tolist()
    P["EN_HALFVOWEL"] = D.text_to_runes(_drop_vowels(en_held, 0.5), "EN").tolist()

    # --- uniform-random runes: the noise floor --------------------------------
    r = random.Random(3301)
    P["RAND"] = [r.randrange(N) for _ in range(200000)]

    return P


# --------------------------------------------------------------------- one trial
def trial(P_idx, L, rep, key_family, key_kw):
    """Plant the register under a real key + the pinned filter; decode with the
    CORRECT key; also decode with a wrong key. Returns one row."""
    rng = random.Random(SEED0 + rep * 977 + L)
    if len(P_idx) < L + 10:
        return None
    start = rng.randrange(0, len(P_idx) - L - 1)
    P = P_idx[start:start + L]

    need = L * (MAX_SKIP + 1) + 512
    K = PL.make_key(key_family, length=need, **key_kw)
    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=SEED0 + rep)

    bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    rec = sum(1 for a, b in zip(bd["plain_idx"], P) if a == b) / len(P)

    WK = [(i * 7 + 13) % N for i in range(len(K))]
    wd = sk.beam_decode(C, WK, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)

    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(1, len(C) - 1)
    return {"L": L, "rep": rep, "score": bd["score"], "recovery": rec,
            "wrong_key_score": wd["score"],
            "truth_plain_score": Q.score_norm(sk.idx_to_trans(P)),
            "n_skips": int(sum(skips)), "ct_doublet_rate": dbl}


def main():
    quick = "--quick" in sys.argv
    lengths = [120] if quick else LENGTHS
    nrep = 3 if quick else NREP

    panels = build_panels()
    print("panel sizes (runes):", {k: len(v) for k, v in panels.items()})

    out = {"lane": "round18/L7-redteam/A1",
           "instrument": ("encipher_keyskip(supp=0.83) -> beam_decode(beam_w=400,max_skip=3) "
                          "-> lp.score.Quadgram.score_norm; recovery on rune indices"),
           "key_family": "sha256_ctr(seed=CICADA3301)  [the B-04/D3 live class]",
           "bar": -5.5, "nrep": nrep, "lengths": lengths,
           "panel_sizes": {k: len(v) for k, v in panels.items()},
           "rows": [], "summary": {}}

    t0 = time.time()
    for name, idxs in panels.items():
        for L in lengths:
            rows = []
            for rep in range(nrep):
                r = trial(idxs, L, rep, "sha256_ctr", {"seed": b"CICADA3301"})
                if r:
                    r["panel"] = name
                    rows.append(r)
                    out["rows"].append(r)
            if not rows:
                continue
            med = statistics.median(r["score"] for r in rows)
            medrec = statistics.median(r["recovery"] for r in rows)
            out["summary"][f"{name}|{L}"] = {
                "panel": name, "L": L, "n": len(rows),
                "median_score": med,
                "mean_score": statistics.fmean(r["score"] for r in rows),
                "sd_score": (statistics.pstdev([r["score"] for r in rows])
                             if len(rows) > 1 else 0.0),
                "min_score": min(r["score"] for r in rows),
                "max_score": max(r["score"] for r in rows),
                "median_recovery": medrec,
                "median_wrong_key": statistics.median(r["wrong_key_score"] for r in rows),
                "median_truth_plain_score": statistics.median(
                    r["truth_plain_score"] for r in rows),
                "median_ct_doublet_pct": 100 * statistics.median(
                    r["ct_doublet_rate"] for r in rows),
                "verdict": ("INVISIBLE" if med < -5.5
                            else ("DEGRADED" if medrec < 0.85 else "VISIBLE")),
            }
            s = out["summary"][f"{name}|{L}"]
            print(f"  {name:14s} L={L:3d}  score {med:7.3f}  rec {medrec:6.1%}  "
                  f"wrong {s['median_wrong_key']:7.3f}  {s['verdict']}")

    # --- orthography cost: same English text, scored raw vs rune round-tripped
    en_raw = re.sub(r"[^A-Z]", "", _mid(_read(os.path.join(
        LP, "data", "keys", "self_reliance.txt"))).upper())
    costs = []
    for rep in range(20):
        r = random.Random(11 + rep)
        s = r.randrange(0, len(en_raw) - 400)
        chunk = en_raw[s:s + 400]
        raw = Q.score_norm(chunk)
        rt = Q.score_norm(sk.idx_to_trans(sk.eng_to_idx(chunk)))
        costs.append((raw, rt, rt - raw))
    out["orthography_cost"] = {
        "note": ("Same English text scored raw, then after a Gematria round trip "
                 "(K->C, V->U, Q->C, Z->S, 7 digraph expansions). Isolates the "
                 "orthography penalty from the language penalty."),
        "median_raw": statistics.median(c[0] for c in costs),
        "median_roundtrip": statistics.median(c[1] for c in costs),
        "median_delta": statistics.median(c[2] for c in costs), "n": len(costs)}
    print("\north cost: raw %.3f -> roundtrip %.3f  (delta %.3f)" % (
        out["orthography_cost"]["median_raw"],
        out["orthography_cost"]["median_roundtrip"],
        out["orthography_cost"]["median_delta"]))

    out["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "out_a1.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote out_a1.json  (%.1fs)" % out["elapsed_s"])


if __name__ == "__main__":
    main()
