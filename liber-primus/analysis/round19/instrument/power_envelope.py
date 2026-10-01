"""Round 19 — LANE 1 — INSTRUMENT POWER ENVELOPE.

Crosses the two axes R18-L7 only measured separately:

    register   (adjudicator) : EN / LA / OE / DE / CY / abbrev-EN  + controls
    construction (decoder)   : rigid / beam(keyskip) / skip_by_two / rewrite(soft-anti-repeat)
                               + the R18-L7-B transition-hole stressors free_drift / drift_at

Method is plant-the-CORRECT-key: take a register corpus (held out of the LM's own training
half), encipher it under a known key x a named construction, decode with the CORRECT key with
the repo's beam, and record what the adjudicator scores -- under BOTH the repo-default English
quadgram scorer (continuity with every prior null) AND a per-register MATCHED rune-space LM
(the R2 power number). Recovery is on RUNE INDICES (doctrine mechanics 5).

R3 columns persisted for every row: decrypt IoC*N, min-distinct over a 32-rune window, best
non-English LM score over the register panel, gzip compressibility.

    PYTHONUTF8=1 python3 power_envelope.py            # full run
    PYTHONUTF8=1 python3 power_envelope.py --quick    # fast smoke (fewer seeds, L=120)

Writes:  power_table.json  (one row per register x construction x L x key_family x seed)
         power_summary.json (per-cell medians, the thing POWER-ENVELOPE.md tables cite)
"""
import os, sys, json, gzip, random, re, statistics, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "analysis", "round16", "scorer"), B6):
    if p not in sys.path:
        sys.path.insert(0, p)

from lp import gematria as gp                 # noqa: E402
from lp import score as _score                # noqa: E402
import skipdecode as sk                       # noqa: E402
import plant as PL                            # noqa: E402
import detectors as D                         # noqa: E402
from scorer import matched_scorer             # noqa: E402  (English-via-runes matched quad)
import null as NULL                           # noqa: E402

N = gp.N
Q = _score.default()
ENG_MATCHED = matched_scorer()

LENGTHS = [31, 120, 240, 400]
NSEED = 7
BEAM_W, MAX_SKIP, SUPP = 400, 3, 0.83
SEED0 = 190001

# wrong-key stream reused as the per-cell null (same construction, deterministic)
def wrong_key(nlen):
    return [(i * 7 + 13) % N for i in range(nlen)]


# ============================================================ register corpora
def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _mid(t):
    return t[len(t) // 8: -len(t) // 8] if len(t) > 40000 else t


def _drop_vowels(text, frac=1.0, seed=7):
    r = random.Random(seed)
    out = []
    for ch in text.upper():
        if ch in "AEIOUY" and (frac >= 1.0 or r.random() < frac):
            continue
        out.append(ch)
    return "".join(out)


def build_registers():
    """Each register -> rune-index stream (np.int64). Split is handled per-cell:
    the LM trains on the FIRST half, plants are drawn from the SECOND half, so a
    matched-LM power number is never inflated by scoring the LM's own training text."""
    R = {}

    en_held = _mid(_read(os.path.join(LP, "data", "keys", "self_reliance.txt"))) + \
              _mid(_read(os.path.join(LP, "data", "keys", "mabinogion.txt")))
    R["EN"] = D.text_to_runes(en_held, "EN")

    # the solved pages' own lossy orthography -- the real LP1 register (control)
    sp = json.load(open(os.path.join(LP, "SOLVED-PAGES.json"), encoding="utf-8"))
    lp1 = "".join(p["plaintext_transliteration"] for p in sp["pages"])
    R["LP1"] = np.array(sk.eng_to_idx(lp1), dtype=np.int64)

    la = _mid(_read(os.path.join(LP, "analysis", "latin", "latin_218.txt"))) + \
         _mid(_read(os.path.join(LP, "analysis", "latin", "latin_28233.txt")))
    R["LA"] = D.text_to_runes(la, "LA")

    oe_raw = _read(os.path.join(B6, "corpora", "oe_beowulf.txt"))
    oe = "\n".join(l for l in oe_raw.split("\n") if re.search(r"[þðæÞÐÆ]", l))
    oe += _read(os.path.join(LP, "data", "keys", "runepoem_oe.txt"))
    R["OE"] = D.text_to_runes(oe, "OE")

    de = _mid(_read(os.path.join(B6, "corpora", "de_faust.txt"))) + \
         _mid(_read(os.path.join(B6, "corpora", "de_2.txt")))
    R["DE"] = D.text_to_runes(de, "DE")

    cy = _mid(_read(os.path.join(LP, "data", "keys", "welsh", "welsh_mabinogion.txt")))
    R["CY"] = D.text_to_runes(cy, "CY")

    R["EN_NOVOWEL"] = D.text_to_runes(_drop_vowels(en_held, 1.0), "EN")

    r = random.Random(3301)
    R["RAND"] = np.array([r.randrange(N) for _ in range(60000)], dtype=np.int64)
    return R


# ============================================================ matched LM panel
def build_lms(registers):
    """One rune-space trigram LM per prose register, trained on its FIRST HALF.
    (RAND / LP1 are controls, not LM targets; LP1 reuses the EN-via-runes matched
    quad scorer -- it IS English orthography.)"""
    lms = {}
    for reg in ("EN", "LA", "OE", "DE", "CY", "EN_NOVOWEL"):
        s = registers[reg]
        half = len(s) // 2
        lms[reg] = D.build_trigram(s[:half])
    return lms


def train_half(registers):
    return {k: len(v) // 2 for k, v in registers.items()}


# ============================================================ constructions
def enc_rigid(P, K, **_):
    """No doublet filter: c = (p - sign*k), key rigid. sign=-1."""
    C = [(p + K[i]) % N for i, p in enumerate(P)]
    return C, {}


def enc_keyskip(P, K, supp=SUPP, seed=3301, **_):
    C, skips, _u = sk.encipher_keyskip(P, K, sign=-1, supp=supp, seed=seed)
    return C, {"n_skips": int(sum(skips))}


def enc_skip_by_two(P, K, supp=SUPP, seed=3301, **_):
    """Rejection burns TWO key draws (the R18-L7-B miss)."""
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], 0, None, 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk}


def enc_rewrite(P, K, supp=SUPP, seed=3301, **_):
    """soft-anti-repeat: in-place value rewrite, key stays synced (round12/D1)."""
    C, info = PL.encipher_rewrite(P, K, sign=-1, supp=supp, seed=seed)
    return C, {"n_rewrites": info["n_rewrites"]}


def enc_free_drift(P, K, supp=SUPP, q=0.01, seed=3301, **_):
    """keyskip PLUS a key advance with prob q for a reason the beam cannot
    represent (interrupter/line-break/discarded draw)."""
    rng = random.Random(seed)
    C, j, c_prev, nsk, nd = [], 0, None, 0, 0
    for p in P:
        if rng.random() < q:
            j += 1
            nd += 1
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_drift": nd}


def enc_drift_at(P, K, supp=SUPP, ndrift=1, seed=3301, **_):
    """keyskip plus EXACTLY ndrift evenly-spaced unrepresentable key advances."""
    n = len(P)
    pos = {int((i + 1) * n / (ndrift + 1)) for i in range(ndrift)} if ndrift else set()
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        if i in pos:
            j += 1
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_drift": len(pos)}


CONSTRUCTIONS = {
    "rigid": (enc_rigid, {}),
    "keyskip": (enc_keyskip, {"supp": SUPP}),
    "skip_by_two": (enc_skip_by_two, {"supp": SUPP}),
    "rewrite": (enc_rewrite, {"supp": SUPP}),
    "free_drift": (enc_free_drift, {"supp": SUPP, "q": 0.01}),
    "drift_at": (enc_drift_at, {"supp": SUPP, "ndrift": 1}),
}

# decode: rigid construction uses the rigid decoder; everything else uses the beam.
# (doctrine 4.3: never rigid-decode LP2; here rigid is a measured ground-truth cell.)


# ============================================================ R3 statistics
def ioc_times_n(idx):
    n = len(idx)
    if n < 2:
        return 0.0
    c = np.bincount(np.asarray(idx), minlength=N)
    num = float((c * (c - 1)).sum())
    return num / (n * (n - 1)) * N


def min_distinct_32(idx):
    a = np.asarray(idx)
    if len(a) < 32:
        return int(len(set(a.tolist())))
    best = 99
    for s in range(0, len(a) - 32 + 1):
        d = len(set(a[s:s + 32].tolist()))
        if d < best:
            best = d
    return int(best)


def compressibility(idx):
    """gzip ratio of the rune-index byte stream: compressed/raw (lower = more
    structured). 1.0 means incompressible."""
    b = bytes(bytearray(int(x) for x in idx))
    if not b:
        return 1.0
    return len(gzip.compress(b, 9)) / len(b)


def best_nonenglish_lm(idx, lms):
    """Best (highest) matched-LM score over every non-English register LM."""
    a = np.asarray(idx)
    best, who = -99.0, None
    for reg, lm in lms.items():
        if reg == "EN":
            continue
        s = D.score_trigram(lm, a)
        if s > best:
            best, who = s, reg
    return best, who


# ============================================================ one cell
def run_cell(register, construction, L, registers, lms, splits,
             key_family="sha256_ctr", key_kw=None, nseed=NSEED):
    key_kw = dict(key_kw or {"seed": b"CICADA3301"})
    enc, mkw = CONSTRUCTIONS[construction]
    stream = registers[register]
    half = splits[register]
    lm = lms.get(register)                     # None for RAND / LP1
    rows = []
    lo = half if register not in ("RAND", "LP1") else 0   # plant from held-out half
    hi = len(stream) - L - 1
    if hi <= lo + 1:
        lo = 0
        hi = len(stream) - L - 1
    if hi <= lo + 1:
        return None, []
    for s in range(nseed):
        rng = random.Random(SEED0 + s * 131 + L + hash(register) % 997)
        start = rng.randrange(lo, hi)
        P = stream[start:start + L].tolist()
        need = L * (MAX_SKIP + 2) * 2 + 1024
        K = PL.make_key(key_family, length=need, **key_kw)
        C, info = enc(P, K, seed=3301 + s, **mkw)

        # correct-key decode
        if construction == "rigid":
            cd = sk.rigid_decode(C, K, sign=-1, o=0)
            wd = sk.rigid_decode(C, wrong_key(len(K)), sign=-1, o=0)
        else:
            cd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
            wd = sk.beam_decode(C, wrong_key(len(K)), sign=-1, o=0,
                                beam_w=BEAM_W, max_skip=MAX_SKIP)
        dec = cd["plain_idx"]
        rec = sum(1 for a, b in zip(dec, P) if a == b) / len(P)

        # adjudicators: English-quadgram (repo default) AND matched register LM
        en_q = cd["score"]                                # repo default (translit quad)
        en_matched = ENG_MATCHED.score_norm(cd["translit"])
        reg_lm = D.score_trigram(lm, np.asarray(dec)) if lm is not None else None
        true_lm = D.score_trigram(lm, np.asarray(P)) if lm is not None else None

        # wrong-key adjudicator scores (per-cell null)
        wk_en_q = wd["score"]
        wk_reg_lm = D.score_trigram(lm, np.asarray(wd["plain_idx"])) if lm is not None else None

        # R3 columns, measured on the CORRECT-KEY DECODE (the candidate plaintext)
        best_lm, best_lm_reg = best_nonenglish_lm(dec, lms)
        row = {
            "register": register, "construction": construction, "L": L,
            "key_family": key_family, "seed": s,
            "recovery": rec,
            "en_quadgram_score": en_q,              # continuity-with-prior-nulls axis
            "en_matched_score": en_matched,
            "matched_lm_score": reg_lm,             # R2 power axis (matched register LM)
            "true_plaintext_lm_score": true_lm,
            "wrong_key_en_quadgram": wk_en_q,
            "wrong_key_matched_lm": wk_reg_lm,
            # ---- R3 (CI-ENFORCED) on the candidate decode ----
            "r3_ioc_times_n": round(ioc_times_n(dec), 4),
            "r3_min_distinct_32": min_distinct_32(dec),
            "r3_best_nonenglish_lm": round(best_lm, 4),
            "r3_best_nonenglish_lm_register": best_lm_reg,
            "r3_compressibility": round(compressibility(dec), 4),
            **{("info_" + k): v for k, v in info.items()},
        }
        rows.append(row)
    return summarize(register, construction, L, key_family, rows, lm is not None), rows


def _med(rows, k):
    vals = [r[k] for r in rows if r.get(k) is not None]
    return statistics.median(vals) if vals else None


def summarize(register, construction, L, key_family, rows, has_lm):
    med_rec = _med(rows, "recovery")
    med_en = _med(rows, "en_quadgram_score")
    med_lm = _med(rows, "matched_lm_score")
    med_true = _med(rows, "true_plaintext_lm_score")
    med_wk_en = _med(rows, "wrong_key_en_quadgram")
    med_wk_lm = _med(rows, "wrong_key_matched_lm")
    # power on the ENGLISH-QUADGRAM axis (continuity): fraction of correct-key
    # replicates whose English-quad score clears the scale-corrected floor AND beats
    # its own wrong-key null.
    bar = NULL.threshold_for(1, segment_len=L)        # single correct-key test per replicate
    pow_en = sum(1 for r in rows
                 if r["en_quadgram_score"] >= bar
                 and r["en_quadgram_score"] > r["wrong_key_en_quadgram"]) / len(rows)
    # power on the MATCHED-LM axis: correct-key matched-LM score separable from the
    # wrong-key matched-LM null (the R2 number the PREREG defines).
    if has_lm:
        pow_lm = sum(1 for r in rows
                     if r["matched_lm_score"] is not None
                     and r["wrong_key_matched_lm"] is not None
                     and r["matched_lm_score"] > r["wrong_key_matched_lm"]) / len(rows)
    else:
        pow_lm = None
    return {
        "register": register, "construction": construction, "L": L,
        "key_family": key_family, "n_seeds": len(rows),
        "median_recovery": med_rec,
        "median_en_quadgram": med_en,
        "median_matched_lm": med_lm,
        "median_true_plaintext_lm": med_true,
        "median_wrong_key_en_quadgram": med_wk_en,
        "median_wrong_key_matched_lm": med_wk_lm,
        "en_quadgram_bar": round(bar, 4),
        "power_en_quadgram": pow_en,      # axis: adjudicator = repo-default English
        "power_matched_lm": pow_lm,       # axis: adjudicator = matched register LM
        # R3 medians at the cell level too
        "median_r3_ioc_times_n": _med(rows, "r3_ioc_times_n"),
        "median_r3_min_distinct_32": _med(rows, "r3_min_distinct_32"),
        "median_r3_best_nonenglish_lm": _med(rows, "r3_best_nonenglish_lm"),
        "median_r3_compressibility": _med(rows, "r3_compressibility"),
    }


# ============================================================ driver
def main():
    quick = "--quick" in sys.argv
    lengths = [120] if quick else LENGTHS
    nseed = 3 if quick else NSEED
    t0 = time.time()

    print("building register corpora ...")
    registers = build_registers()
    print("  sizes (runes):", {k: len(v) for k, v in registers.items()})
    print("training matched rune-space LMs (first-half of each register) ...")
    lms = build_lms(registers)
    splits = train_half(registers)

    # secondary key families (to show the effect is a scorer/decoder property, not a
    # key property -- R18 flagged this as not-covered). Keep light: EN only, L=240.
    reg_order = ["EN", "LP1", "LA", "OE", "DE", "CY", "EN_NOVOWEL", "RAND"]
    con_order = ["rigid", "keyskip", "skip_by_two", "rewrite", "free_drift", "drift_at"]

    all_rows, summary = [], []
    print("\n=== PRIMARY GRID: register x construction x L  (key=sha256_ctr) ===")
    for reg in reg_order:
        for con in con_order:
            for L in lengths:
                summ, rows = run_cell(reg, con, L, registers, lms, splits)
                if summ is None:
                    continue
                summary.append(summ)
                all_rows.extend(rows)
                pl = summ["power_matched_lm"]
                print(f"  {reg:10s} {con:12s} L={L:3d}  rec {summ['median_recovery']:5.0%}"
                      f"  EN-q {summ['median_en_quadgram']:7.3f} (pow {summ['power_en_quadgram']:.2f})"
                      f"  matched-LM {str(round(summ['median_matched_lm'],3)) if summ['median_matched_lm'] is not None else '  n/a':>7}"
                      f" (pow {pl if pl is not None else 'n/a'})")

    # secondary key families at one representative cell set
    print("\n=== SECONDARY KEY FAMILIES (EN, L=240, keyskip+rigid) ===")
    for fam, kw in (("running", {"keytext": "agrippa.txt"}),
                    ("vigenere", {"keyword": "DIVINITY"}),
                    ("prng", {"seed": 3301})):
        for con in ("rigid", "keyskip"):
            L = 120 if quick else 240
            summ, rows = run_cell("EN", con, L, registers, lms, splits,
                                  key_family=fam, key_kw=kw, nseed=nseed)
            if summ is None:
                continue
            summary.append(summ)
            all_rows.extend(rows)
            print(f"  {fam:10s} {con:12s} L={L}  rec {summ['median_recovery']:5.0%}"
                  f"  EN-q {summ['median_en_quadgram']:7.3f} (pow {summ['power_en_quadgram']:.2f})"
                  f"  matched-LM {round(summ['median_matched_lm'],3)} (pow {summ['power_matched_lm']})")

    meta = {
        "lane": "round19/instrument",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "instrument": {
            "decoder": "skipdecode.beam_decode(beam_w=400,max_skip=3) / rigid_decode for rigid cell",
            "adjudicators": ["lp.score.Quadgram.score_norm (repo default, English)",
                             "round16 matched English-via-runes quadgram",
                             "per-register rune-space trigram LM (detectors.build_trigram)"],
            "recovery": "measured on RUNE INDICES",
            "null": "wrong key [(i*7+13)%29], same construction, per replicate",
            "bar": "benchmark/null.threshold_for(1, segment_len=L)",
        },
        "axes": {"register": reg_order, "construction": con_order, "L": lengths},
        "n_seeds": nseed,
        "note_lm_training": ("LMs trained on first half of each register corpus; plants drawn "
                             "from second half -- matched-LM power is never scored on training text."),
        "note_r3": ("R3 columns (ioc_times_n, min_distinct_32, best_nonenglish_lm, compressibility) "
                    "are measured on the CORRECT-KEY DECODE, persisted per row."),
        "elapsed_s": round(time.time() - t0, 1),
    }
    json.dump({"meta": meta, "rows": all_rows},
              open(os.path.join(HERE, "power_table.json"), "w"), indent=1)
    json.dump({"meta": meta, "summary": summary},
              open(os.path.join(HERE, "power_summary.json"), "w"), indent=1)
    print(f"\nwrote power_table.json ({len(all_rows)} rows) + power_summary.json "
          f"({len(summary)} cells) in {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
