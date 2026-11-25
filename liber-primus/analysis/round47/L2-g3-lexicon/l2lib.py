"""R47-L2 shared machinery: page units under fragment conventions C0 / CS / CE (PREREG s1), plants via R46-L1 l1lib.
Writes nothing by itself."""
import os, sys, json, time, random, bisect
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
L1DIR = os.path.join(LP, "analysis", "round46", "L1-word-loader")
sys.path.insert(0, L1DIR)
import words as W      # noqa: E402
import l1lib as G      # noqa: E402

NKEY = 1100
CONVS = ("C0", "CS", "CE")
PB = G.PAGE_BOUNDS                     # [0, page starts..., 12956]


def segments(words, conv):
    """words: list of (start, len) contiguous from rune 0.  C0 splits every word at every page boundary (mapcommon
    rule); CS/CE keep words joined (words.py)."""
    if conv != "C0":
        return list(words)
    out = []
    for a, l in words:
        b = a + l; cur = a
        for s in PB[1:-1]:
            if cur < s < b:
                out.append((cur, s - cur)); cur = s
        out.append((cur, b - cur))
    return out


def unit(words, p, conv, nkey=NKEY):
    """-> (u0, lens covering >= nkey runes from u0 (or to stream end), unit_end).  PREREG s1."""
    segs = segments(words, conv)
    lo, hi = PB[p], PB[p + 1]
    if conv == "C0":
        i0 = next(i for i, (a, l) in enumerate(segs) if a >= lo); uend = hi
    elif conv == "CS":
        i0 = next(i for i, (a, l) in enumerate(segs) if a >= lo)
        uend = max(a + l for a, l in segs if a < hi)
    elif conv == "CE":
        i0 = next(i for i, (a, l) in enumerate(segs) if a + l > lo)
        uend = max(a + l for a, l in segs if a + l <= hi)
    else:
        raise ValueError(conv)
    u0 = segs[i0][0]; lens = []; tot = 0
    for a, l in segs[i0:]:
        lens.append(l); tot += l
        if tot >= nkey: break
    return u0, lens, uend


def real_words():
    R = W.lp2(); return [(w["start"], w["len"]) for w in R.words]


def plant_words_true(P):
    return list(zip(P.starts, P.true_lens))


def plant_words_printed(P):
    """words parsed by words.py from the rendered print (never handed over directly)."""
    txt = W.render(G.regroup(P.flat, P.printed_lens), P.sent_ends, G.LINE_STARTS, G.PAGE_STARTS)
    Q = W.parse(txt)
    assert Q.runes[:len(P.flat)] == P.flat
    return [(w["start"], w["len"]) for w in Q.words]


def plant_rng(row, regime, page, conv, rep):
    k = ("a", "b", "bp").index(regime) * 1000 + page * 100 + CONVS.index(conv) * 10 + rep
    return random.Random(47200000 + {"g3": 0, "r38": 100000, "r39": 200000}[row] + k)


wilson = G.wilson


def heartbeat(tag, msg):
    open(os.path.join(HERE, "heartbeat_%s.txt" % tag), "w").write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg))


def summarize(rows, keys):
    """rows: dicts with 'recover' plus grouping keys -> {group: power...}"""
    out = {}
    for r in rows:
        g = "|".join(str(r[k]) for k in keys)
        e = out.setdefault(g, [0, 0]); e[0] += bool(r["recover"]); e[1] += 1
    return {g: {"power": round(k / n, 3), "k": k, "n": n, "wilson": wilson(k, n)} for g, (k, n) in sorted(out.items())}
