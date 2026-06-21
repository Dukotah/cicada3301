"""Task 1: Solved-plaintext-as-key in RUNE/gematria-index space.

Use the decrypted English of the SOLVED LP pages as a RUNNING KEY against the
unsolved pages, but keyed on Gematria-Primus rune INDICES (multi-letter runes
collapsed: TH/EO/NG/OE/AE/IA/EA -> single index), in several orderings.

Orderings tested:
  - per-page forward
  - per-page reversed
  - all-solved concatenated (reading order) forward
  - all-solved concatenated reversed
Sign in {-1,+1}, atbash in {F,T}, ALL running-key offsets (vectorised numpy).
Top offsets per (page,config) then re-scored; best few also run through the
interrupter beam (which the stock runningkey lacks).
"""
import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "analysis"))
import numpy as np
from lp import gematria as gp, solve, score as _score, corpus
from run_stats import load_pages, english_baseline

N = gp.N
SC = _score.default()

# monogram log-prob table (English baseline) for a proper prefilter
_eng = np.array(english_baseline())
_cnt = np.bincount(_eng, minlength=N).astype(float) + 1.0
MONO = np.log10(_cnt / _cnt.sum())

# --- build solved-plaintext rune-index keys (gematria space) ----------------
SOLVED_LABELS = ["03.jpg", "05.jpg", "14.jpg", "16.jpg", "73.jpg", "74.jpg"]

def english_to_indices(text):
    letters = re.sub(r"[^A-Za-z]", "", text)
    return gp.keyword_to_indices(letters)

solved_pts = {}
for lab in SOLVED_LABELS:
    p = corpus.page_by_label(lab)
    pt = p["plaintext"]
    # cut trailing gematria-value/number noise lines: keep only letter runs,
    # english_to_indices already strips non-letters.
    idxs = english_to_indices(pt)
    if idxs:
        solved_pts[lab] = idxs

# concatenated reading order
concat = []
for lab in SOLVED_LABELS:
    concat += solved_pts.get(lab, [])

keys = {}
for lab, idxs in solved_pts.items():
    keys[f"solved[{lab}]fwd"] = idxs
    keys[f"solved[{lab}]rev"] = idxs[::-1]
keys["solved[ALL]fwd"] = concat
keys["solved[ALL]rev"] = concat[::-1]

print("Key sizes:")
for k, v in keys.items():
    print(f"  {k:24s} {len(v)}")

# --- unsolved pages ----------------------------------------------------------
all_pages = load_pages()
unsolved = all_pages[:-2]  # last two solved (AN END / PARABLE)

# also keep rune text per page for interrupter beam
# reconstruct runes_text per unsolved page from indices
def idxs_to_runes(idxs):
    return gp.indices_to_runes(idxs)

best = {"score": -99, "rec": None}
hits = []

def consider(s, rec):
    if s > best["score"]:
        best["score"] = s; best["rec"] = rec
    if s > -5.2:
        r = dict(rec); r["score"] = round(s, 3)
        hits.append(r)

# track top configs per page for interrupter follow-up
top_for_beam = []  # (score, page_idx, keyname, sign, atb, offset)

for pi, idxs in enumerate(unsolved):
    c = np.array(idxs)
    L = len(c)
    if L < 20:
        continue
    for kname, kidx in keys.items():
        key = np.array(kidx)
        if len(key) < L + 1:
            continue
        noff = len(key) - L
        for sign in (-1, +1):
            for atb in (False, True):
                cc = (N - 1 - c) if atb else c
                # sliding window over all offsets, monogram prefilter
                best_off, best_mono = [], []
                step = 4000
                for o0 in range(0, noff, step):
                    o1 = min(o0 + step, noff)
                    win = np.lib.stride_tricks.sliding_window_view(key, L)[o0:o1]
                    p = (cc[None, :] - sign * win) % N
                    mono = MONO[p].sum(axis=1)  # proper monogram log-prob
                    k = min(10, len(mono))
                    topk = np.argpartition(-mono, k - 1)[:k]
                    for t in topk:
                        best_off.append(o0 + int(t))
                        best_mono.append(float(mono[t]))
                order = np.argsort(best_mono)[::-1][:40]
                for oi in order:
                    o = best_off[oi]
                    p = (cc - sign * key[o:o + L]) % N
                    txt = gp.indices_to_translit(p.tolist())
                    s = SC.score_norm(txt)
                    rec = {"page": pi, "method": f"runkey {kname} sign{sign:+d} atb{atb} off{o}",
                           "key": kname, "plaintext": txt[:120]}
                    consider(s, rec)
                    top_for_beam.append((s, pi, kname, sign, atb, o))

print(f"\nBest pre-beam: {best['score']:.3f}")
if best["rec"]:
    print("  ", best["rec"]["method"], "::", best["rec"]["plaintext"][:80])

# --- interrupter beam on the best few (only pages with F runes) -------------
top_for_beam.sort(reverse=True)
seen = set()
beam_done = 0
for s, pi, kname, sign, atb, o in top_for_beam:
    if beam_done >= 15:
        break
    sig = (pi, kname, sign, atb)
    if sig in seen:
        continue
    seen.add(sig)
    idxs = unsolved[pi]
    runes_text = idxs_to_runes(idxs)
    if gp.INTERRUPTER not in runes_text:
        continue
    key = np.array(keys[kname])
    L = len(idxs)
    stream = key[o:o + L].tolist()
    try:
        r = solve.find_interrupters(runes_text, stream, sign=sign, atbash=atb, beam_width=200)
    except Exception as e:
        continue
    beam_done += 1
    consider(r["score_norm"], {"page": pi, "method": f"runkey+beam {kname} sign{sign:+d} atb{atb} off{o}",
             "key": kname + "+beam", "plaintext": r["plaintext"][:120]})

print(f"\nFINAL best: {best['score']:.3f}")
if best["rec"]:
    print("  ", best["rec"]["method"])
    print("  ", best["rec"]["plaintext"][:120])
print(f"\nhits over -5.2: {len(hits)}")
for h in sorted(hits, key=lambda x: -x["score"])[:10]:
    print(f"  {h['score']:.2f} p{h['page']} {h['method']}  {h['plaintext'][:60]}")

import json
json.dump({"best_score": best["score"], "best": best["rec"], "n_hits": len(hits),
           "hits": sorted(hits, key=lambda x: -x["score"])[:30]},
          open(os.path.join(os.path.dirname(__file__), "task1_result.json"), "w"), indent=2)
