"""Lane B1 - artifact-derived keys vs LP2 0-54, under the AUTHOR'S DEMONSTRATED TOOLKIT ONLY.

Operations swept (nothing else - this is the point of the lane):
  * Vigenere with the artifact string as the keyword, sign -1 and +1
  * Atbash pre-stage on/off
  * key-phase rotation (start the repeating key at any of its own offsets)
  * Caesar/shift over all 29 offsets (keyless arm, run once per page as a baseline)
  * numeric artifact strings as repeating mod-29 additive keystreams (2 readings)
  * the validated F-rune interrupter beam (lp.solve.find_interrupters) on every
    candidate that clears the promotion bar

Controls:
  --pc      PC-B (harness must re-find DIVINITY on 03.jpg / FIRFUMFERENFE on 14.jpg)
            + PC-C (planted artifact key on synthetic English + interrupters)
  --null    run the identical grid against per-page-shuffled LP2 (empirical FP ceiling)

Usage:
  PYTHONUTF8=1 python3 analysis/round10b/B1-overlooked-artifact/b1_sweep.py --pc
  PYTHONUTF8=1 python3 analysis/round10b/B1-overlooked-artifact/b1_sweep.py --real
  PYTHONUTF8=1 python3 analysis/round10b/B1-overlooked-artifact/b1_sweep.py --null
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, HERE)

from lp import gematria as gp, ciphers, solve, corpus, score as _score  # noqa
from run_stats import load_pages  # noqa
from b1_keys import build  # noqa

N = gp.N
SC = _score.default()
TRANS = gp.IDX_TO_TRANS

THRESHOLD = -5.2      # pre-registered BREAK bar
PROMOTE = -6.0        # promote to interrupter beam
MAXPHASE = 12


def translit(idxs):
    return "".join(TRANS[i] for i in idxs)


def unsolved():
    return load_pages()[:-2]


def vig_decode(c, key, sign, atb, phase):
    L = len(key)
    if atb:
        return [(((N - 1) - c[i]) + sign * key[(i + phase) % L]) % N for i in range(len(c))]
    return [(c[i] + sign * key[(i + phase) % L]) % N for i in range(len(c))]


def sweep_pages(pages, alpha, numer, label, log):
    """Full grid. Returns (best_record, hits, top_list)."""
    best = {"score": -99.0}
    hits = []
    top = []
    t0 = time.time()
    # ---- keyless Caesar/Atbash baseline (author's page-1/5/6 toolkit) ----
    for pi, c in enumerate(pages):
        for atb in (False, True):
            base = [((N - 1) - x) for x in c] if atb else c
            for k in range(N):
                for sign in (-1, +1):
                    p = [(x + sign * k) % N for x in base]
                    s = SC.score_norm(translit(p))
                    rec = {"page": pi, "method": f"{'atbash+' if atb else ''}shift{sign*k:+d}",
                           "key": "(keyless)", "tag": "baseline", "score": round(s, 3)}
                    if s > best["score"]:
                        best = dict(rec, score=s, plaintext=translit(p)[:120])
                    top.append((s, rec))
                    if s > THRESHOLD:
                        hits.append(dict(rec, plaintext=translit(p)[:300]))
    log(f"[{label}] keyless baseline done  best={best['score']:.3f}  "
        f"({time.time()-t0:.0f}s)")

    # ---- Vigenere over artifact keywords ----
    keyidx = []
    for r in alpha:
        try:
            keyidx.append((r, gp.keyword_to_indices(r["key"])))
        except ValueError:
            continue
    log(f"[{label}] {len(keyidx)} usable artifact keywords")
    for r, key in keyidx:
        nph = min(len(key), MAXPHASE)
        for pi, c in enumerate(pages):
            for sign in (-1, +1):
                for atb in (False, True):
                    for ph in range(nph):
                        p = vig_decode(c, key, sign, atb, ph)
                        s = SC.score_norm(translit(p))
                        if s > best["score"] or s > PROMOTE:
                            rec = {"page": pi,
                                   "method": f"vigenere sign{sign:+d} atb{int(atb)} ph{ph}",
                                   "key": r["key"], "tag": r["tag"], "prov": r["prov"],
                                   "score": round(s, 3)}
                            if s > best["score"]:
                                best = dict(rec, score=s, plaintext=translit(p)[:120])
                            top.append((s, rec))
                            if s > THRESHOLD:
                                hits.append(dict(rec, plaintext=translit(p)[:300]))
    log(f"[{label}] vigenere grid done  best={best['score']:.3f}  "
        f"({time.time()-t0:.0f}s)")

    # ---- numeric artifact strings as repeating mod-29 keystreams ----
    for r in numer:
        d = r["digits"]
        readings = {
            "digit": [int(ch) for ch in d],
            "pair29": [int(d[i:i + 2]) % N for i in range(0, len(d) - 1, 2)],
        }
        for rd, stream in readings.items():
            if len(stream) < 2:
                continue
            nph = min(len(stream), MAXPHASE)
            for pi, c in enumerate(pages):
                for sign in (-1, +1):
                    for atb in (False, True):
                        for ph in range(nph):
                            p = vig_decode(c, stream, sign, atb, ph)
                            s = SC.score_norm(translit(p))
                            if s > best["score"] or s > PROMOTE:
                                rec = {"page": pi,
                                       "method": f"numstream {rd} sign{sign:+d} "
                                                 f"atb{int(atb)} ph{ph}",
                                       "key": d[:30], "tag": r["tag"], "prov": r["prov"],
                                       "score": round(s, 3)}
                                if s > best["score"]:
                                    best = dict(rec, score=s, plaintext=translit(p)[:120])
                                top.append((s, rec))
                                if s > THRESHOLD:
                                    hits.append(dict(rec, plaintext=translit(p)[:300]))
    log(f"[{label}] numeric grid done  best={best['score']:.3f}  "
        f"({time.time()-t0:.0f}s)")
    top.sort(key=lambda x: -x[0])
    return best, hits, top[:60]


def interrupter_pass(pages, cands, log, limit=40):
    """Promote the best rigid candidates through the validated F-interrupter beam."""
    out = []
    seen = set()
    n = 0
    for s, rec in cands:
        if n >= limit:
            break
        if rec["key"] == "(keyless)":
            continue
        sig = (rec["page"], rec["key"], rec["method"])
        if sig in seen:
            continue
        seen.add(sig)
        try:
            key = gp.keyword_to_indices(rec["key"])
        except ValueError:
            key = [int(ch) for ch in rec["key"] if ch.isdigit()]
            if not key:
                continue
        m = rec["method"]
        sign = -1 if "sign-1" in m else +1
        atb = "atb1" in m
        ph = int(m.split("ph")[-1]) if "ph" in m else 0
        c = pages[rec["page"]]
        stream = [key[(i + ph) % len(key)] for i in range(len(c) + 200)]
        runes_text = gp.indices_to_runes(c)
        r = solve.find_interrupters(runes_text, stream, sign=sign, atbash=atb,
                                    beam_width=200, scorer=SC)
        out.append({**rec, "int_score": round(r["score_norm"], 3),
                    "n_interrupters": r["n_interrupters"],
                    "int_plaintext": r["plaintext"][:200]})
        n += 1
    out.sort(key=lambda d: -d["int_score"])
    if out:
        log(f"  interrupter beam: best={out[0]['int_score']:.3f} "
            f"key={out[0]['key'][:24]} page={out[0]['page']}")
    return out


# ------------------------------------------------------------------ controls
def pc_b(alpha, log):
    """PC-B: point the B1 machinery at REAL solved Cicada ciphertext."""
    ok = True
    tests = [("03.jpg", "DIVINITY", ["WELCOME", "PILGRIM"]),
             ("14.jpg", "FIRFUMFERENFE", ["LESSON", "MASTER"])]
    keys = [r["key"] for r in alpha] + [t[1] for t in tests]
    for label, truekey, expect in tests:
        page = corpus.page_by_label(label)
        c = gp.runes_to_indices(page["runes"])
        runes_text = page["runes"]
        results = []
        for k in keys:
            try:
                ki = gp.keyword_to_indices(k)
            except ValueError:
                continue
            stream = ciphers.repeat_key(ki, len(c) + 200)
            r = solve.find_interrupters(runes_text, stream, sign=-1, atbash=False,
                                        beam_width=200, scorer=SC)
            results.append((r["score_norm"], k, r["plaintext"]))
        results.sort(key=lambda x: -x[0])
        s, k, txt = results[0]
        up = txt.upper()
        hit = (k == truekey) and s > THRESHOLD and all(w in up for w in expect)
        log(f"PC-B {label}: rank1 key={k} score={s:.3f} "
            f"(true={truekey}) -> {'PASS' if hit else 'FAIL'}")
        log(f"      {txt[:100]}")
        log(f"      rank2 = {results[1][1]} @ {results[1][0]:.3f}  "
            f"(margin {s - results[1][0]:.3f})")
        ok &= hit
    return ok


def pc_c(alpha, log):
    """PC-C: plant an ARTIFACT keyword over English + interrupters; must be recovered."""
    plain = ("THEQUICKMORNINGLIGHTFELLUPONTHEOLDSTONEWALLANDTHETRAVELLERKNEWTHATHIS"
             "JOURNEYWASNEARLYATANENDFORBEYONDTHERIVERLAYTHECITYOFHISFATHERSWHEREHE"
             "WOULDATLASTBEABLETORESTANDTOTELLTHESTORYOFALLTHATHEHADSEENUPONTHEROAD")
    truekey = "THEKEYISALLAROUNDYOU"
    pi = gp.keyword_to_indices(plain)
    ki = gp.keyword_to_indices(truekey)
    stream = ciphers.repeat_key(ki, len(pi) + 200)
    # encipher exactly as the author did page 03: c = p - sign*k with sign=-1 -> c = p + k
    ct = [(pi[i] + stream[i]) % N for i in range(len(pi))]
    # insert 6 F-rune interrupters (author's demonstrated device)
    ct_runes = list(gp.indices_to_runes(ct))
    rnd = random.Random(3301)
    for pos in sorted(rnd.sample(range(10, len(ct_runes) - 10), 6), reverse=True):
        ct_runes.insert(pos, gp.INTERRUPTER)
    ct_text = "".join(ct_runes)
    keys = [r["key"] for r in alpha] + [truekey]
    res = []
    for k in keys:
        try:
            kk = gp.keyword_to_indices(k)
        except ValueError:
            continue
        st = ciphers.repeat_key(kk, len(ct_text) + 200)
        r = solve.find_interrupters(ct_text, st, sign=-1, atbash=False,
                                    beam_width=200, scorer=SC)
        res.append((r["score_norm"], k, r["plaintext"]))
    res.sort(key=lambda x: -x[0])
    s, k, txt = res[0]
    ok = (k == truekey) and s > THRESHOLD
    log(f"PC-C planted artifact key: rank1={k} score={s:.3f} "
        f"(true={truekey}) -> {'PASS' if ok else 'FAIL'}")
    log(f"      {txt[:100]}")
    log(f"      rank2 = {res[1][1]} @ {res[1][0]:.3f}  (margin {s - res[1][0]:.3f})")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pc", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "b1_results.json"))
    a = ap.parse_args()

    lines = []

    def log(m):
        print(m, flush=True)
        lines.append(m)

    alpha, numer = build()
    log(f"artifact ALPHA keys = {len(alpha)}, NUMER streams = {len(numer)}")
    payload = {"n_alpha": len(alpha), "n_numer": len(numer), "threshold": THRESHOLD}

    if a.pc:
        payload["pc_b"] = pc_b(alpha, log)
        payload["pc_c"] = pc_c(alpha, log)

    if a.real:
        pages = unsolved()
        log(f"real LP2 pages = {len(pages)}, runes = {sum(len(p) for p in pages)}")
        best, hits, top = sweep_pages(pages, alpha, numer, "REAL", log)
        payload["real_best"] = best
        payload["real_hits"] = hits
        payload["real_top"] = [{"score": s, **r} for s, r in top]
        payload["real_interrupter"] = interrupter_pass(pages, top, log)

    if a.null:
        pages = unsolved()
        rnd = random.Random(20260812)
        sh = []
        for p in pages:
            q = list(p)
            rnd.shuffle(q)
            sh.append(q)
        log(f"NULL: per-page shuffled LP2, {len(sh)} pages")
        best, hits, top = sweep_pages(sh, alpha, numer, "NULL", log)
        payload["null_best"] = best
        payload["null_hits"] = hits
        payload["null_top"] = [{"score": s, **r} for s, r in top[:20]]
        payload["null_interrupter"] = interrupter_pass(sh, top, log)

    old = {}
    if os.path.exists(a.out):
        try:
            old = json.load(open(a.out, encoding="utf-8"))
        except Exception:
            old = {}
    old.update(payload)
    json.dump(old, open(a.out, "w", encoding="utf-8"), indent=2)
    with open(os.path.join(HERE, "RUN.log"), "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"wrote {a.out}")


if __name__ == "__main__":
    main()
