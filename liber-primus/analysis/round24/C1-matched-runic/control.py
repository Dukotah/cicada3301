"""Round 24 / C1 — POSITIVE CONTROL (mandatory, before real scoring).

Reproduces L7-A's register/power measurement but adds the axis C1 is auditing: adjudicate the
CORRECT-key decode under BOTH the repo English quadgram scorer AND the round16 matched-runic scorer,
for Latin and (romanized) Greek plaintexts planted into the rune space, plus EN/EN_NOVOWEL/RAND.

Instrument (repo's, unchanged, = L7-A's a1_scorer_language):
    encipher_keyskip(supp=0.83) -> beam_decode(beam_w=400,max_skip=3) with CORRECT key
    adjudicate recovered plain_idx on rune indices under EN scorer and matched scorer.

Per register x length: measure POWER = fraction of replicates whose adjudicated correct-key score
exceeds that register's OWN seed-3301 order-matched wrong-key null MAX. Reported for each scorer.
Control PASS iff matched power > English power on >=1 non-English register at L=120.

Run: PYTHONUTF8=1 python3 control.py            # writes out_control.json
     PYTHONUTF8=1 python3 control.py --quick    # fewer reps
"""
import os, sys, json, random, re, statistics, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer"), B6, HERE):
    sys.path.insert(0, p)

from lp import gematria as gp          # noqa
from lp import score as _score         # noqa
import skipdecode as sk                # noqa
import plant as PL                     # noqa
import detectors as D                  # noqa
from scorer import matched_scorer      # noqa
from greek_corpus import romanized_greek  # noqa

N = gp.N
Q = _score.default()                   # English quadgram scorer (the repo default)
MQ = matched_scorer()                  # round16 matched-runic scorer
BEAM_W, MAX_SKIP, SUPP = 400, 3, 0.83
LENGTHS = [120, 240]
NREP = 24
NNULL = 60          # order-matched wrong-key null per register x length
SEED0 = 33010


def _read(p):
    return open(p, encoding="utf-8", errors="ignore").read()


def _mid(t):
    return t[len(t) // 8: -len(t) // 8] if len(t) > 40000 else t


def _drop_vowels(text):
    return "".join(c for c in text.upper() if c not in "AEIOUY")


def build_panels():
    P = {}
    en = _mid(_read(os.path.join(LP, "data", "keys", "self_reliance.txt"))) + \
         _mid(_read(os.path.join(LP, "data", "keys", "mabinogion.txt")))
    P["EN_MODERN"] = D.text_to_runes(en, "EN").tolist()
    la = _mid(_read(os.path.join(LP, "analysis", "latin", "latin_218.txt"))) + \
         _mid(_read(os.path.join(LP, "analysis", "latin", "latin_28233.txt")))
    P["LATIN"] = D.text_to_runes(la, "LA").tolist()
    P["GREEK"] = D.text_to_runes(romanized_greek(), "LA").tolist()
    P["EN_NOVOWEL"] = D.text_to_runes(_drop_vowels(en), "EN").tolist()
    r = random.Random(3301)
    P["RAND"] = [r.randrange(N) for _ in range(60000)]
    return P


def _decode_correct(P_idx, L, rep):
    """Plant register under the real key + pinned filter; decode with the CORRECT key.
    Return (recovery, recovered_translit, truth_translit)."""
    rng = random.Random(SEED0 + rep * 977 + L)
    if len(P_idx) < L + 10:
        return None
    start = rng.randrange(0, len(P_idx) - L - 1)
    P = P_idx[start:start + L]
    need = L * (MAX_SKIP + 1) + 512
    K = PL.make_key("sha256_ctr", length=need, seed=b"CICADA3301")
    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=SEED0 + rep)
    bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    rec = sum(1 for a, b in zip(bd["plain_idx"], P) if a == b) / len(P)
    return rec, sk.idx_to_trans(bd["plain_idx"]), sk.idx_to_trans(P), C


def _null_scores(C_example_len, L, scorer_fn):
    """seed-3301 order-matched wrong-key null: decode a freshly-planted ciphertext of this register
    under uniform-random WRONG keys through the identical beam; adjudicate with scorer_fn. Returns the
    list of null scores (we take the max as the family-wise per-register bar)."""
    # handled inside run() where we have the register's own ciphertext samples
    raise NotImplementedError


def run():
    quick = "--quick" in sys.argv
    lengths = [120] if quick else LENGTHS
    nrep = 8 if quick else NREP
    nnull = 30 if quick else NNULL

    panels = build_panels()
    out = {
        "lane": "round24/C1-matched-runic (control)",
        "instrument": ("encipher_keyskip(supp=0.83) -> beam_decode(400,3) CORRECT key; "
                       "adjudicate recovered plain_idx under EN quadgram AND round16 matched-runic"),
        "key_family": "sha256_ctr(seed=CICADA3301)  [B-04/D3 live class]",
        "null": "seed-3301 order-matched uniform-random wrong-key decodes, per register x length",
        "nrep": nrep, "nnull": nnull, "lengths": lengths,
        "panel_sizes": {k: len(v) for k, v in panels.items()},
        "rows": [], "summary": {},
    }
    rng_null = random.Random(3301)
    t0 = time.time()

    for name, idxs in panels.items():
        for L in lengths:
            # --- correct-key decodes ---
            corr = []
            for rep in range(nrep):
                d = _decode_correct(idxs, L, rep)
                if d:
                    corr.append(d)
            if not corr:
                continue
            en_corr = [Q.score_norm(t) for _, t, _, _ in corr]
            mq_corr = [MQ.score_norm(t) for _, t, _, _ in corr]
            en_truth = [Q.score_norm(tt) for _, _, tt, _ in corr]
            mq_truth = [MQ.score_norm(tt) for _, _, tt, _ in corr]
            rec = [r for r, _, _, _ in corr]

            # --- order-matched wrong-key null for THIS register x length ---
            # use the ciphertexts we just planted; decode each under a uniform-random wrong key
            en_null, mq_null = [], []
            for j in range(nnull):
                _, _, _, C = corr[j % len(corr)]
                WK = [rng_null.randrange(N) for _ in range(len(C) * (MAX_SKIP + 1) + 8)]
                wd = sk.beam_decode(C, WK, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
                wt = sk.idx_to_trans(wd["plain_idx"])
                en_null.append(Q.score_norm(wt))
                mq_null.append(MQ.score_norm(wt))
            en_bar = max(en_null)
            mq_bar = max(mq_null)

            # (a) power vs each register's OWN order-matched null MAX (moves the bar with the scorer)
            en_power = sum(1 for s in en_corr if s > en_bar) / len(en_corr)
            mq_power = sum(1 for s in mq_corr if s > mq_bar) / len(mq_corr)
            # (b) power vs the FIXED -5.5 bar = L7-A's own power definition (reproduces 0.33/0.00)
            en_power_fixed = sum(1 for s in en_corr if s > -5.5) / len(en_corr)
            mq_power_fixed = sum(1 for s in mq_corr if s > -5.5) / len(mq_corr)

            key = f"{name}|{L}"
            out["summary"][key] = {
                "panel": name, "L": L, "n": len(corr),
                "median_recovery": statistics.median(rec),
                "median_correct_EN": round(statistics.median(en_corr), 3),
                "median_correct_MATCHED": round(statistics.median(mq_corr), 3),
                "median_truth_EN": round(statistics.median(en_truth), 3),
                "median_truth_MATCHED": round(statistics.median(mq_truth), 3),
                "null_max_EN": round(en_bar, 3),
                "null_max_MATCHED": round(mq_bar, 3),
                "null_mean_EN": round(statistics.fmean(en_null), 3),
                "null_mean_MATCHED": round(statistics.fmean(mq_null), 3),
                "power_EN": en_power,
                "power_MATCHED": mq_power,
                "power_EN_fixed_bar_L7A": en_power_fixed,
                "power_MATCHED_fixed_bar_L7A": mq_power_fixed,
                "matched_beats_english": (mq_power > en_power) or (mq_power_fixed > en_power_fixed),
            }
            s = out["summary"][key]
            print(f"  {name:11s} L={L:3d} rec={s['median_recovery']:.0%} "
                  f"EN corr={s['median_correct_EN']:7.3f} MATCHED corr={s['median_correct_MATCHED']:7.3f} | "
                  f"fixed-5.5 pow EN={en_power_fixed:.2f} MATCHED={mq_power_fixed:.2f} | "
                  f"null-max pow EN={en_power:.2f} MATCHED={mq_power:.2f}"
                  f"  {'<<MATCHED WINS' if s['matched_beats_english'] else ''}")

    # control verdict
    gap = [k for k, v in out["summary"].items()
           if v["L"] == 120 and v["panel"] in ("LATIN", "GREEK", "EN_NOVOWEL")
           and v["matched_beats_english"]]
    out["control_pass"] = bool(gap)
    out["control_pass_registers"] = gap
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "out_control.json"), "w"), indent=1)
    print(f"\ncontrol_pass={out['control_pass']}  registers={gap}")
    print(f"wrote out_control.json  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    run()
