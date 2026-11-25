"""Itemised reconciliation of words.py (2,896 LP2 words) against each legacy loader. -> reconcile.json"""
import os, sys, json, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import words as W


def cuts(lens):
    return set(itertools.accumulate(lens))


def main():
    P = W.lp2()
    new = cuts(P.lengths)
    txt = open(W.KRIS, encoding="utf-8").read()
    # character context around each rune position boundary: separators between rune i-1 and rune i
    seps = {}; k = 0; buf = ""
    for ch in txt:
        if ch in W.IDX:
            if k > 0: seps[k] = buf
            buf = ""; k += 1
            if k > W.N_LP2: break
        else:
            buf += ch
    out = {"words_py": len(P.words), "target": W.N_LP2_WORDS_TARGET, "match_target": len(P.words) == W.N_LP2_WORDS_TARGET,
           "wraps_line_incl_page": sum(w["wraps_line"] for w in P.words), "wraps_page": sum(w["wraps_page"] for w in P.words),
           "wraps_line_only": sum(w["wraps_line"] and not w["wraps_page"] for w in P.words), "legacy": {}}
    for name in ("camp7", "mapcommon", "skeleton"):
        L = W.legacy_words(name); old = cuts(L)
        extra = sorted(old - new); missing = sorted(new - old)
        def ctx(c): return repr(seps.get(c, "<end>")).replace("\\n", "⏎")
        ex_kind = {}
        for c in extra: ex_kind[ctx(c)] = ex_kind.get(ctx(c), 0) + 1
        mi_kind = {}
        for c in missing: mi_kind[ctx(c)] = mi_kind.get(ctx(c), 0) + 1
        out["legacy"][name] = {"n_words": len(L), "same_stream": sum(L) == W.N_LP2, "extra_cuts": len(extra), "missing_cuts": len(missing),
                               "net": len(L) - len(P.words), "extra_cut_separator_context": ex_kind, "missing_cut_separator_context": mi_kind,
                               "missing_cut_positions": missing, "words_identical": len(L) - len(extra) + len(missing)}
        assert len(L) - len(P.words) == len(extra) - len(missing)
    json.dump(out, open(os.path.join(HERE, "reconcile.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: (v if k != "legacy" else {n: {kk: vv for kk, vv in x.items() if kk != "missing_cut_positions"} for n, x in v.items()}) for k, v in out.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
