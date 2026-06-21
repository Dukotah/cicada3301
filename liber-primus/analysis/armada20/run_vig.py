"""Exhaustive short Vigenere primer (len 1-3) x explicit interrupter (29 runes
+ None) x modes {skip,advance,reset,enc}, scored per page.

Strategy: the interrupter is a STRUCTURE. For a given (page, interrupt_rune,
mode), the keystream alignment changes. We brute keys len 1,2,3 (29^L) and keep
global best. This is ~24k keys * a handful of interrupter/mode combos per page;
we prune by only scanning interrupter runes that actually appear in the page and
the high-frequency 'F' default.
"""
import sys, itertools, time
sys.path.insert(0, 'analysis/armada20')
import interrupter_search as I
N = I.N

MODES = ['skip', 'advance', 'reset', 'enc']

def search_page(pi, max_keylen=3, top=5, time_budget=40):
    runes = I.page_runes(I.pages[pi])
    if len(runes) < 20:
        return []
    present = sorted(set(I.gp.RUNE_TO_IDX[c] for c in runes))
    # candidate interrupters: None (no interrupter) + each present rune
    cand_int = [None] + present
    results = []
    t0 = time.time()
    # exhaustive keys
    for L in range(1, max_keylen + 1):
        for key in itertools.product(range(N), repeat=L):
            key = list(key)
            for interrupt_idx in cand_int:
                modes = MODES if interrupt_idx is not None else ['enc']
                for mode in modes:
                    for sign in (-1, +1):
                        pt = I.decrypt_vig(runes, key, interrupt_idx, mode, sign=sign)
                        if len(pt) < 10:
                            continue
                        s = I.score_idx(pt)
                        results.append((s, L, tuple(key), interrupt_idx, mode, sign))
            if time.time() - t0 > time_budget:
                break
        # keep only top to bound memory
        results.sort(key=lambda r: r[0], reverse=True)
        results = results[:50]
        if time.time() - t0 > time_budget:
            break
    results.sort(key=lambda r: r[0], reverse=True)
    return results[:top]

if __name__ == '__main__':
    target_pages = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else list(range(0, 56))
    global_best = []
    for pi in target_pages:
        res = search_page(pi, max_keylen=3, time_budget=25)
        if not res:
            continue
        best = res[0]
        s, L, key, ii, mode, sign = best
        keytrans = I.gp.indices_to_translit(list(key))
        irune = I.gp.IDX_TO_RUNE[ii] if ii is not None else '-'
        print(f"p{pi:2d} best={s:.3f} L={L} key={keytrans!r} int={irune} mode={mode} sign={sign:+d}")
        global_best.append((s, pi, L, key, ii, mode, sign))
    print('\\n=== TOP GLOBAL ===')
    global_best.sort(key=lambda r: r[0], reverse=True)
    for s, pi, L, key, ii, mode, sign in global_best[:10]:
        runes = I.page_runes(I.pages[pi])
        pt = I.decrypt_vig(runes, list(key), ii, mode, sign=sign)
        snippet = I.text_of(pt)[:80]
        irune = I.gp.IDX_TO_RUNE[ii] if ii is not None else '-'
        print(f"p{pi} {s:.3f} key={I.gp.indices_to_translit(list(key))!r} int={irune} mode={mode} sign={sign:+d} :: {snippet}")
