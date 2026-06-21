"""Explicit-interrupter ciphertext-autokey search.

Per autokey.py, a ciphertext-autokey uniquely suppresses doublets, which is the
LP fingerprint. But a plain ciphertext-autokey was already eliminated. The NEW
angle here: model an explicit interrupter rune that breaks/resets the autokey
chain (a structured spacer), then brute the 29*29 seed/K primer. If the
interrupter is what hides the chain's residual structure, the explicit model
should recover it.

We scan interrupter rune in {None}+present, mode in {skip,advance,reset},
seed in 0..28, K in 0..28, sign +/-. Cheap: <2*29*29*4 = ~13k decrypts/page.
"""
import sys, time
sys.path.insert(0, 'analysis/armada20')
import interrupter_search as I
N = I.N
MODES = ['skip', 'advance', 'reset']

def search_page(pi, top=3):
    runes = I.page_runes(I.pages[pi])
    if len(runes) < 20:
        return []
    present = sorted(set(I.gp.RUNE_TO_IDX[c] for c in runes))
    cand_int = [None] + present
    best = []
    for interrupt_idx in cand_int:
        modes = MODES if interrupt_idx is not None else ['enc']
        for mode in modes:
            for sign in (-1, +1):
                for seed in range(N):
                    for K in range(N):
                        pt = I.decrypt_autokey(runes, seed, K, interrupt_idx, mode, sign=sign)
                        if len(pt) < 10:
                            continue
                        s = I.score_idx(pt)
                        best.append((s, seed, K, interrupt_idx, mode, sign))
        best.sort(key=lambda r: r[0], reverse=True)
        best = best[:20]
    best.sort(key=lambda r: r[0], reverse=True)
    return best[:top]

if __name__ == '__main__':
    targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else list(range(0, 56))
    gb = []
    for pi in targets:
        res = search_page(pi)
        if not res:
            continue
        s, seed, K, ii, mode, sign = res[0]
        irune = I.gp.IDX_TO_RUNE[ii] if ii is not None else '-'
        print(f"p{pi:2d} best={s:.3f} seed={seed} K={K} int={irune} mode={mode} sign={sign:+d}")
        gb.append((s, pi, seed, K, ii, mode, sign))
    print('\n=== TOP GLOBAL (autokey) ===')
    gb.sort(key=lambda r: r[0], reverse=True)
    for s, pi, seed, K, ii, mode, sign in gb[:10]:
        runes = I.page_runes(I.pages[pi])
        pt = I.decrypt_autokey(runes, seed, K, ii, mode, sign=sign)
        snip = I.text_of(pt)[:80]
        irune = I.gp.IDX_TO_RUNE[ii] if ii is not None else '-'
        print(f"p{pi} {s:.3f} seed={seed} K={K} int={irune} mode={mode} sign={sign:+d} :: {snip}")
