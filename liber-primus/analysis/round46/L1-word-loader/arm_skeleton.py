"""R46-L1 arm SKELETON (C-01): Round 8 word-length plaintext identification (analysis/skeleton/wordlen_search.py,
corpus_lengths() and FFT scan() unchanged) through words.py.

  real   : LP2's printed lengths from words.py (2,896) and from the legacy lp2_words (2,928) scanned over the
           repo-resident corpus with wordlen_search.main()'s own glob (data/*.txt, data/keys/*.txt, skeleton/corpus/*.txt),
           windows full/400/120, slack 0/1, one shuffled-pattern control per text (the original statistic).
  plants : pride sentences (corpus_lengths per sentence) laid over LP2's real layout from a random page start,
           regimes a / b / bp; pattern = W words parsed from the rendered text by words.py (L) or by lp2_words' rule (O).
           Detection (I1 rule) = global argmax over pride+moby at the planted offset AND count > max of 5 shuffled scans.
python -I arm_skeleton.py real|plants"""
import os, sys, re, json, time, glob, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import l1lib as G
import words as W
WS = G._load("wordlen_search", G.AN("skeleton", "wordlen_search.py"))
F = lambda n: os.path.join(HERE, n)
NPL, NNULL = 20, 5


def corpus_texts():
    ROOT = WS.ROOT; texts = {}
    for p in glob.glob(os.path.join(ROOT, "data", "*.txt")):
        n = os.path.basename(p)
        if n in ("krisyotam_runes.txt", "english_quadgrams.txt"): continue
        texts[n] = open(p, encoding="utf-8", errors="ignore").read()
    for p in glob.glob(os.path.join(ROOT, "data", "keys", "*.txt")):
        texts["keys/" + os.path.basename(p)] = open(p, encoding="utf-8", errors="ignore").read()
    for p in glob.glob(os.path.join(WS.HERE, "corpus", "*.txt")):
        texts["gutenberg/" + os.path.basename(p)] = open(p, encoding="utf-8", errors="ignore").read()
    return texts


def real():
    t0 = time.time()
    texts = corpus_texts()
    LENS = {n: WS.corpus_lengths(t) for n, t in sorted(texts.items())}
    pats = {"words_py": np.array(W.lp2().lengths, np.int16), "legacy_lp2_words": WS.lp2_words()[0]}
    rng = np.random.default_rng(3301)
    out = {"corpus_texts": len(LENS), "corpus_words": int(sum(len(v) for v in LENS.values())), "results": []}
    for W_ in (None, 400, 120):
        for name, lp in pats.items():
            pat = lp if W_ is None else lp[:W_]
            shuf = pat.copy(); rng.shuffle(shuf)
            for slack in (0, 1):
                best, nulls = [], []
                for tn, C in LENS.items():
                    s = WS.scan(pat, C, slack)
                    if s is None: continue
                    sn = WS.scan(shuf, C, slack)
                    best.append((float(s.max()), tn, int(s.argmax()))); nulls.append(float(sn.max()))
                best.sort(reverse=True)
                z = (best[0][0] - np.mean(nulls)) / (np.std(nulls) + 1e-9)
                out["results"].append({"pattern": name, "window": len(pat), "slack": slack, "best": best[0][0], "text": best[0][1], "offset": best[0][2],
                                       "pct": round(100 * best[0][0] / len(pat), 2), "null_mean": round(float(np.mean(nulls)), 2),
                                       "null_max": max(nulls), "z": round(float(z), 3), "real_beats_all_shuffled": best[0][0] > max(nulls)})
                print(out["results"][-1], "%.0fs" % (time.time() - t0), flush=True)
                G.heartbeat("skel", "real %s W%s slack%d" % (name, W_, slack))
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(F("skeleton_real.json"), "w"), indent=1)


def pride_sentence_lengths():
    t = open(os.path.join(G.LP, "data", "pride.txt"), encoding="utf-8", errors="ignore").read()
    full = WS.corpus_lengths(t)
    sents = [s for s in re.split(r"[.!?]", t)]
    per = [WS.corpus_lengths(s) for s in sents]
    flat = np.concatenate([p for p in per if len(p)])
    # the per-sentence tokenisation must reproduce the corpus array the scan sees
    assert len(flat) == len(full) and (flat == full).all(), (len(flat), len(full))
    return full, [list(map(int, p)) for p in per if len(p)]


def plants():
    t0 = time.time()
    LENS = {n: WS.corpus_lengths(open(os.path.join(G.LP, "data", n), encoding="utf-8", errors="ignore").read()) for n in ("pride.txt", "moby.txt")}
    full, sents = pride_sentence_lengths()
    sent_start = np.cumsum([0] + [len(s) for s in sents])
    res = {"cells": {}}
    for Wn in (120, 400):
        rows = []
        for regime in ("a", "b", "bp"):
            for s in range(NPL):
                rng = random.Random(46800 + 97 * Wn + 1000 * ("a", "b", "bp").index(regime) + s)
                si = rng.randrange(len(sents) // 20, len(sents) - 3000)
                base = int(sent_start[si])
                lens, sent_ends, sent_of = [], set(), []
                tot = 0; k = si
                while tot < W.N_LP2:
                    seq = list(sents[k])
                    if regime == "b": rng.shuffle(seq)
                    for l in seq: lens.append(l); sent_of.append(k); tot += l
                    sent_ends.add(len(lens) - 1); k += 1
                lens[-1] -= tot - W.N_LP2
                if lens[-1] <= 0: lens.pop()
                printed = list(lens)
                if regime == "bp":
                    grp = {}
                    for i, q in enumerate(sent_of[:len(printed)]): grp.setdefault(q, []).append(i)
                    for ks in grp.values():
                        v = [printed[i] for i in ks]; rng.shuffle(v)
                        for i, x in zip(ks, v): printed[i] = x
                txt = W.render(G.regroup([0] * W.N_LP2, printed), set(e for e in sent_ends if e < len(printed) - 1), G.LINE_STARTS, G.PAGE_STARTS)
                # pattern from a random page start (pages 1..40)
                pg = rng.randrange(1, 41); s0 = G.PAGE_BOUNDS[pg]
                Q = W.parse(txt)
                iL = next(i for i, w in enumerate(Q.words) if w["start"] >= s0)
                patL = np.array(Q.lengths[iL:iL + Wn], np.int16)
                # true corpus offset of that word (plaintext word index); regime b shuffles so order is not the corpus order
                off = base + iL
                legacy = []; cur = 0
                for seg in txt.split("%")[pg:]:
                    for ch in seg:
                        if ch in W.IDX: cur += 1
                        elif ch in "-." and cur: legacy.append(cur); cur = 0
                    if cur: legacy.append(cur); cur = 0
                patO = np.array(legacy[:Wn], np.int16)
                offO = off - (1 if Q.words[iL]["start"] > s0 else 0)      # a legacy pattern opening on a fragment aligns one word earlier
                row = {"regime": regime, "seed": s, "page": pg, "offset": off}
                for loader, pat, o in (("L", patL, off), ("O", patO, offO)):
                    top = (-1, None, None)
                    for name, arr in LENS.items():
                        r = WS.scan(pat, arr, 0); i = int(np.argmax(r)); v = float(r[i])
                        if v > top[0]: top = (v, name, i)
                    nulls = []
                    for q in range(NNULL):
                        sh = pat.copy(); np.random.default_rng(1000 * s + q).shuffle(sh)
                        nb = max(float(WS.scan(sh, arr, 0).max()) for arr in LENS.values()); nulls.append(nb)
                    tc = float(WS.scan(pat, LENS["pride.txt"], 0)[o])
                    row[loader] = {"best": top[0], "where": [top[1], top[2]], "true_count_frac": round(tc / len(pat), 3), "null_max": max(nulls),
                                   "detected": bool(top[1] == "pride.txt" and top[2] == o and top[0] > max(nulls))}
                rows.append(row)
            G.heartbeat("skelp", "plants W%d %s %.0fs" % (Wn, regime, time.time() - t0))
        cell = {}
        for regime in ("a", "b", "bp"):
            for loader in ("L", "O"):
                rr = [r for r in rows if r["regime"] == regime]; k = sum(r[loader]["detected"] for r in rr)
                cell["%s|%s" % (regime, loader)] = {"power": k / len(rr), "k": k, "n": len(rr), "wilson": G.wilson(k, len(rr)),
                                                    "median_true_count_frac": float(np.median([r[loader]["true_count_frac"] for r in rr]))}
        res["cells"]["W%d" % Wn] = {"summary": cell, "rows": rows}
        print("W", Wn, {k: v["power"] for k, v in cell.items()}, "%.0fs" % (time.time() - t0), flush=True)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(F("skeleton_plants.json"), "w"), indent=1)


if __name__ == "__main__":
    {"real": real, "plants": plants}[sys.argv[1]]()
