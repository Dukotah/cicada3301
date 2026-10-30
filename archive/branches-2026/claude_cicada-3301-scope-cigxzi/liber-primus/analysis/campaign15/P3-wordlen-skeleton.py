#!/usr/bin/env python3
"""
Campaign XV, Probe P3 — Word-length skeleton attack on LP2.

Thesis: an OTP protects the runes but NOT the word-boundary metadata. Each
unsolved page yields a sequence of rune-word lengths (digraph-compressed).
If the plaintext of a page is a passage from some known corpus, that corpus,
converted to rune-word lengths, must contain a window matching the page's
length-sequence in ORDER. Sliding + a permutation (shuffle) null tells us
whether any real match beats chance.

Run: python analysis/campaign15/P3-wordlen-skeleton.py
"""
import sys, os, glob, re
sys.path.insert(0, 'src')
import numpy as np
from lp import gematria as gp

RNG = np.random.default_rng(3301)
DATA = 'data/krisyotam_runes.txt'

# ---------------------------------------------------------------- page skeletons
def page_word_lengths(page_text):
    """Split a page on word separators '-' and '.', count runes per word."""
    # '/' = newline, keep as nothing; only '-' and '.' are word separators
    cleaned = page_text.replace('/', '')
    words = re.split(r'[-.]', cleaned)
    seqs = []
    for w in words:
        runes = [c for c in w if gp.is_rune(c)]
        if runes:
            seqs.append(len(runes))
    return seqs

def load_pages():
    txt = open(DATA, encoding='utf-8').read()
    pages = [p for p in txt.split('%') if any(gp.is_rune(c) for c in p)]
    unsolved = pages[:-2]          # drop last 2 solved pages
    solved   = pages[-2:]
    return unsolved, solved

# ---------------------------------------------------------------- corpus skeletons
def text_word_lengths(text):
    """Latin text -> list of digraph-compressed rune-lengths per word."""
    out = []
    for w in re.findall(r'[A-Za-z]+', text):
        try:
            idx = gp.keyword_to_indices(w.upper())
        except Exception:
            idx = None
        if idx:
            out.append(len(idx))
    return out

CORPUS_PATHS = []
CORPUS_PATHS += glob.glob('data/keys/*.txt')
CORPUS_PATHS += glob.glob('data/keys/campaign15/*.txt')
CORPUS_PATHS += glob.glob('analysis/foundation/*_key.txt')
CORPUS_PATHS += ['analysis/armada20/taoteching.txt',
                 'analysis/armada20/thomas.txt',
                 'analysis/armada20/pgp_english_prose.txt']
CORPUS_PATHS = [p for p in dict.fromkeys(CORPUS_PATHS) if os.path.exists(p)]

def load_corpora():
    corps = {}
    for p in CORPUS_PATHS:
        try:
            t = open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        seq = text_word_lengths(t)
        if len(seq) >= 3:
            corps[p] = np.array(seq, dtype=np.int16)
    return corps

# ---------------------------------------------------------------- matcher
def window_min_mismatch(seq, corpus):
    """
    Slide seq (len L) over corpus (len M). Return, over all windows:
      n_exact  = #windows with every position identical
      n_tol1   = #windows with every |diff| <= 1
      best_mismatch = min over windows of (#positions differing)   [exact sense]
    Uses sliding_window_view; falls back to loop if L>M.
    """
    L = len(seq); M = len(corpus)
    if L == 0 or M < L:
        return 0, 0, L  # cannot fit
    sw = np.lib.stride_tricks.sliding_window_view(corpus, L)  # (M-L+1, L)
    diff = np.abs(sw.astype(np.int32) - seq.astype(np.int32))
    exact_per_win = (diff == 0).all(axis=1)
    tol1_per_win  = (diff <= 1).all(axis=1)
    mism = (diff != 0).sum(axis=1)
    return int(exact_per_win.sum()), int(tol1_per_win.sum()), int(mism.min())

def best_over_corpora(seq_arr, corpora):
    tot_exact = 0; tot_tol1 = 0; best_mism = len(seq_arr); best_frac = 1.0
    best_where = None
    for name, corp in corpora.items():
        e, t, m = window_min_mismatch(seq_arr, corp)
        tot_exact += e; tot_tol1 += t
        frac = m / max(1, len(seq_arr))
        if frac < best_frac:
            best_frac = frac; best_mism = m; best_where = name
    return tot_exact, tot_tol1, best_mism, best_frac, best_where

# ---------------------------------------------------------------- null calibration
def shuffle_fpr(seq, corpora, n_shuf=1000):
    """Fraction of length-preserving shuffles that produce >=1 exact window
       anywhere in the corpus set, and the shuffle-null distribution of
       best mismatch fraction."""
    seq = np.asarray(seq, dtype=np.int16)
    hits = 0
    best_fracs = np.empty(n_shuf)
    for k in range(n_shuf):
        s = seq.copy(); RNG.shuffle(s)
        e, t, m, frac, _ = best_over_corpora(s, corpora)
        if e > 0:
            hits += 1
        best_fracs[k] = frac
    return hits / n_shuf, best_fracs

# ---------------------------------------------------------------- main
def main():
    unsolved, solved = load_pages()
    corpora = load_corpora()
    print(f"Corpora loaded: {len(corpora)}")
    for n, c in corpora.items():
        print(f"  {n:55s} {len(c):7d} words")
    print(f"Total corpus words: {sum(len(c) for c in corpora.values())}")
    print(f"Unsolved pages: {len(unsolved)}")

    # ---- page skeletons ----
    page_seqs = [page_word_lengths(p) for p in unsolved]
    lens = [len(s) for s in page_seqs]
    print(f"\nPage word-counts: min={min(lens)} max={max(lens)} "
          f"mean={np.mean(lens):.1f} total_words={sum(lens)}")

    # ================= SYNTHETIC VALIDATION =================
    # Take a solved page's OWN plaintext; confirm matcher finds it & rejects shuffles.
    print("\n" + "="*70)
    print("SYNTHETIC VALIDATION: solved-page plaintext vs itself")
    print("="*70)
    # Build a 'plaintext' skeleton from the known solved_plaintext corpus by
    # embedding a real page skeleton into a random corpus and confirming recovery.
    val_seq = page_seqs[0]                       # use page 0 skeleton as 'plaintext truth'
    L = len(val_seq)
    # synthetic corpus: random lengths (1..8) with the true seq embedded at pos P
    synth = RNG.integers(1, 9, size=4000).astype(np.int16)
    P = 1500
    synth[P:P+L] = np.array(val_seq, dtype=np.int16)
    synth_corp = {'SYNTH': synth}
    e, t, m, frac, _ = best_over_corpora(np.array(val_seq, dtype=np.int16), synth_corp)
    fpr, bf = shuffle_fpr(val_seq, synth_corp, n_shuf=1000)
    print(f"  page-0 skeleton len L={L}")
    print(f"  REAL embedded: n_exact_windows={e}  best_mismatch={m}/{L}  frac={frac:.3f}")
    print(f"  SHUFFLE null : exact-hit FPR={fpr:.4f} over 1000 shuffles; "
          f"shuffle best_frac min={bf.min():.3f} mean={bf.mean():.3f}")
    val_pass = (e >= 1) and (fpr < 1e-3)
    print(f"  VALIDATION {'PASS' if val_pass else 'FAIL'}: "
          f"matcher recovers embedded truth (exact={e}) and rejects shuffles (FPR={fpr}).")

    # Literal test: a real solved-page plaintext passage vs its own corpus.
    print("\n  --- Self-match on real solved plaintext (solved_plaintext.txt) ---")
    sp = text_word_lengths(open('data/keys/solved_plaintext.txt',
                                 encoding='utf-8', errors='ignore').read())
    sp = np.array(sp, dtype=np.int16)
    passage = sp[800:850]                        # a genuine 50-word passage
    sp_corp = {'solved_plaintext': sp}
    e2, t2, m2, f2, _ = best_over_corpora(passage, sp_corp)
    fpr2, bf2 = shuffle_fpr(list(passage), sp_corp, n_shuf=1000)
    print(f"  passage(50w) self-search: n_exact={e2} best_mism={m2}/{len(passage)} | "
          f"shuffle exact-FPR={fpr2:.4f} null_frac mean={bf2.mean():.3f}")
    val_pass = val_pass and (e2 >= 1) and (fpr2 < 1e-3)
    print(f"  self-match VALIDATION {'PASS' if (e2>=1 and fpr2<1e-3) else 'FAIL'}")

    # ================= REAL ATTACK =================
    print("\n" + "="*70)
    print("REAL ATTACK: each unsolved page skeleton vs all corpora")
    print("="*70)
    fired = False
    results = []
    for i, seq in enumerate(page_seqs):
        sa = np.array(seq, dtype=np.int16)
        e, t, m, frac, where = best_over_corpora(sa, corpora)
        results.append((i, len(seq), e, t, m, frac, where))
        flag = "  <-- EXACT" if e > 0 else ""
        if i < 6 or e > 0 or t > 0:
            print(f"  page {i:2d} words={len(seq):3d}  exact_win={e:2d}  tol1_win={t:3d}  "
                  f"best_mism={m:3d}/{len(seq):<3d} frac={frac:.3f}  {os.path.basename(str(where))}{flag}")
        if e > 0:
            fired = True

    n_exact_total = sum(r[2] for r in results)
    n_tol1_total  = sum(r[3] for r in results)
    print(f"\n  Across {len(results)} pages: total exact windows={n_exact_total}, "
          f"total tol1 windows={n_tol1_total}")

    # ---- permutation null on the real pages (calibrate FPR) ----
    # For pages with the SMALLEST skeleton (most likely a chance exact hit),
    # compute shuffle FPR to prove even short pages don't spuriously match.
    print("\n  Permutation-null FPR on real corpora (1000 shuffles each):")
    order = sorted(range(len(page_seqs)), key=lambda i: len(page_seqs[i]))
    checked = order[:3] + order[len(order)//2:len(order)//2+1] + order[-1:]
    for i in dict.fromkeys(checked):
        seq = page_seqs[i]
        real_e, real_t, real_m, real_frac, _ = best_over_corpora(
            np.array(seq, dtype=np.int16), corpora)
        fpr, bf = shuffle_fpr(seq, corpora, n_shuf=1000)
        # z-score of real best_frac vs shuffle null
        z = (bf.mean() - real_frac) / (bf.std() + 1e-9)
        print(f"    page {i:2d} words={len(seq):3d}: real exact={real_e} frac={real_frac:.3f} | "
              f"shuffle exact-FPR={fpr:.4f} null_frac mean={bf.mean():.3f} sd={bf.std():.3f} "
              f"-> real z={z:+.2f}")

    print("\n" + "="*70)
    verdict = "BREAK" if fired else "NULL-CLOSED"
    print(f"VERDICT: {verdict}  (signal_fired={fired})")
    print("="*70)
    return fired, val_pass, results

if __name__ == '__main__':
    main()
