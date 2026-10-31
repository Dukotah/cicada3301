"""python direct.py m4 | m6 | dir | self | a2    direct panel-R36 re-scores (C3 machinery: eval_family, direct_control, doublet-matched shuffles)"""
import os, sys, json, time, random
from c1common import *
from lp import gematria as gp
from lib import _mapc, _load
MD = deg_thr()


def run_direct(fam, key_space, decoder, streams, gen_null, D, nrep, extra, ctl_n=None):
    part = Part(fam, key_space, decoder, len(streams))
    if part.skip:
        log(fam, "already done"); return json.load(open(part.done))
    wait_mem(); res = eval_family(streams, gen_null, D, fam, part=part, raw_best=True)
    ctl = direct_control(res, ctl_n or nrep, fam)
    ndeg = 0
    for k, s in streams.items():
        s = np.asarray(s)
        if len(s) >= 32 and (AD.min_distinct(s) <= MD[0] or AD.ioc_n(s) >= MD[1]): ndeg += 1
    extra = dict(extra); extra["n_degenerate_streams"] = ndeg; extra["n_streams_total"] = len(streams)
    return finish_direct(part, fam, res, ctl, extra)


# ------------------------------------------------------------------ M4 (R04)
def stage_m4():
    M = _mapc(); d = M.parse(); W = d["words"]; assert len(W) == 2928
    book = M.solved_english_words(); B = len(book)
    cache = {}

    def widx(w):
        if w not in cache:
            try: cache[w] = list(gp.keyword_to_indices(w))
            except Exception: cache[w] = []
        return cache[w]

    def streams_of(Wd):
        sp, si, ln = wnums(Wd).values()
        fams = {"len": ln, "len-1": ln - 1, "Sprime": sp, "Sidx": si, "cumSprime": np.cumsum(sp), "cumSidx": np.cumsum(si),
                "idx+Sidx": si + np.arange(len(Wd)), "idx+Sprime": sp + np.arange(len(Wd))}
        out = {}
        for nm, arr in fams.items():
            for base in (0, 1):
                ptr = (np.asarray(arr) - base) % B; s = []
                for i in ptr: s.extend(widx(book[i]))
                out["M4:%s:base%d" % (nm, base)] = np.array(s, dtype=np.int64)
        return out
    obs = streams_of(W)
    log("M4 book words", B, "stream lens", {k: len(v) for k, v in list(obs.items())[:4]})
    run_direct("R04_M4_LP1_pointer", "R10 L2 M4: 16 pointer streams (8 families x base 0/1) into the %d solved-English book words, each retrieved word -> rune idx (greedy keyword parse)" % B,
               "direct panel-R36 pmax of the bare stream", obs, lambda j: streams_of(M.null_A(W, 500 + j)), 300, 12000,
               {"universe": 16, "null": "null_A (rune content shuffled, word boundaries held), pointer family re-derived, 300 draws"}, ctl_n=3000)


# ------------------------------------------------------------------ M6 (R06)
def stage_m6():
    M = _mapc(); d = M.parse()
    seqs = {"words-per-line": np.bincount(d["w_line"], minlength=max(d["w_line"]) + 1), "words-per-page": np.bincount(d["w_page"], minlength=55),
            "words-per-sentence": np.bincount(d["w_sent"], minlength=max(d["w_sent"]) + 1), "runes-per-line": np.array([len(l) for l in d["lines"] if l]),
            "runes-per-page": np.array([len(p) for p in d["pages"]])}
    LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def streams_of(sq):
        out = {}
        for nm, arr in sq.items():
            arr = np.asarray(arr, dtype=np.int64); r29 = arr % 29
            for bn, b in (("id", r29), ("atbash", 28 - r29)):
                for k in range(29): out["M6:%s:%s+%d" % (nm, bn, k)] = (b + k) % 29
            for k in range(26):
                t = "".join(LET[(int(x) + k) % 26] for x in arr)
                try: out["M6:%s:letters26+%d" % (nm, k)] = np.array(gp.keyword_to_indices(t), dtype=np.int64)
                except Exception: pass
        return out
    obs = streams_of(seqs)
    run_direct("R06_M6_structural_counts", "R10 L2 M6: 5 count sequences (words/line, words/page, words/sentence, runes/line, runes/page) x {mod29 id/atbash x 29 shifts, mod26 letters x 26 shifts -> rune idx}",
               "direct panel-R36 pmax", obs, lambda j: streams_of({k: np.random.RandomState(900 + j).permutation(v) for k, v in seqs.items()}), 300, 55,
               {"universe": len(obs), "null": "each sequence randomly permuted, same transforms, 300 draws", "note": "streams < 32 runes are not scorable by the panel and are excluded (counted in n_streams_total)"})


# ------------------------------------------------------------------ DIRECTION (R13)
def stage_dir():
    Dm = _load("direction_mod", os.path.join(AN, "direction", "direction.py"))

    def streams_of(stream):
        stream = np.asarray(stream, dtype=np.int64); out = {}
        for sname, f in Dm.STEPS.items():
            for start in range(0, 64):
                for back in (False, True):
                    for skipF in (True, False): out["A:%s:s%d:b%d:f%d" % (sname, start, back, skipF)] = np.array(Dm.walk(stream, f, start, back=back, skipF=skipF), dtype=np.int64)
            for start in range(0, 32): out["B:%s:s%d" % (sname, start)] = np.array(Dm.cumwalk(stream, f, start), dtype=np.int64)
        for stride in (1, 2, 3, 5, 7, 11, 13, 29, 33, 133, 331):
            for start in range(0, 16):
                for mode in ("parity", "half"): out["C:%d:s%d:%s" % (stride, start, mode)] = np.array(Dm.signwalk(stream, stride, start, mode=mode), dtype=np.int64)
        for k, v in Dm.sieves(stream).items(): out["D:" + k] = np.asarray(v, dtype=np.int64)
        return out
    obs = streams_of(np.array(U)); log("R13 readings", len(obs), "scorable (>=32)", sum(len(v) >= 32 for v in obs.values()))
    DD = int(os.environ.get("DIR_D", "150")); sfx = "" if DD == 150 else "_D%d" % DD
    if os.environ.get("DIR_SEED"): sfx += "_seed" + os.environ["DIR_SEED"]
    run_direct("R13_R9_DIRECTION_walks" + sfx, "R9 DIRECTION: %d positional reads (A self-indexing walks, B cumulative walks, C sign walks, D sieves) of the LP2 ciphertext, unchanged direction.py" % len(obs),
               "direct panel-R36 pmax", obs, lambda j: streams_of(np.array(dfshuffle(U, random.Random(int(os.environ.get("DIR_SEED", "8000")) + j)))), DD, 150,
               {"universe": len(obs), "null": "doublet-matched (<=86 pairs) shuffled LP2 run through the identical reads, %d draws" % DD})


# ------------------------------------------------------------------ R22-A (R27)
def stage_self():
    sd = os.path.join(AN, "round22", "A-selfembedded-read"); S = _load("lib_selfread", os.path.join(sd, "lib_selfread.py"))
    seq = S.concat_rune_indices(); log("R27 solved rune stream", len(seq))

    def streams_of(sq): return {desc: np.array(sub, dtype=np.int64) for desc, sub in S.enumerate_selections(list(sq)) if len(sub) >= 4}
    obs = streams_of(seq)

    def gnull(j):
        sh = list(seq); random.Random(7000 + j).shuffle(sh); return streams_of(sh)
    run_direct("R27_R22A_selfembedded", "R22-A: %d every-k / diagonal / anti-diagonal / reverse selections of the solved-plaintext rune-index stream (%d runes), lib_selfread.enumerate_selections unchanged" % (len(obs), len(seq)),
               "direct panel-R36 pmax", obs, gnull, 200, 150, {"universe": len(obs), "null": "order-shuffled solved source, selections re-enumerated, 200 draws"})


# ------------------------------------------------------------------ R23-A2 (R28)
def stage_a2():
    ad = os.path.join(AN, "round23", "A2-line-acrostic"); sys.path.insert(0, ad)
    G = _load("lib_geom", os.path.join(ad, "lib_geom.py")); sd = os.path.join(AN, "round22", "A-selfembedded-read"); S = _load("lib_selfread", os.path.join(sd, "lib_selfread.py"))
    RS = _load("a2_run_sweep", os.path.join(ad, "run_sweep.py"))
    pages = G.load_all_pages(); cands = list(RS.enumerate_candidates(pages))
    obs = {}
    for desc, letters in cands: obs[desc] = np.array(S._greedy_translit_to_indices(letters), dtype=np.int64)
    scorable = {k: v for k, v in obs.items() if len(v) >= 32}
    log("R28 candidates", len(cands), "scorable (>=32 runes)", len(scorable))
    pool = list(RS.pool()); clen = {desc: len(letters) for desc, letters in cands}

    own = os.environ.get("A2_NULL", "pool") == "own"
    letters_of = {desc: letters for desc, letters in cands}

    def gnull(j):
        out = {}
        if own:
            for desc in scorable:
                l = list(letters_of[desc]); random.Random(9100 + j * 131 + len(l)).shuffle(l); out[desc] = np.array(S._greedy_translit_to_indices("".join(l)), dtype=np.int64)
            return out
        sh = list(pool); random.Random(9000 + j).shuffle(sh)
        for desc in scorable: out[desc] = np.array(S._greedy_translit_to_indices("".join(sh[:clen[desc]])), dtype=np.int64)
        return out
    run_direct("R28_R23A2_line_acrostic" + ("_ownhist" if own else ""), "R23-A2: %d printed-line / word acrostic reads (letters of 5 solved pages at true geometry, greedy rune parse); %d of them have >= 32 runes and are scorable, %d are below the panel floor" % (len(cands), len(scorable), len(cands) - len(scorable)),
               "direct panel-R36 pmax", scorable, gnull, 300, 120, {"universe": len(scorable), "below_floor": len(cands) - len(scorable), "null": ("each read's OWN letters histogram-shuffled (matched: keeps the English first/last-letter skew), 300 draws" if own else "lane null: order-shuffled solved letter pool, same lengths, 300 draws")})


if __name__ == "__main__":
    globals()["stage_" + sys.argv[1]]()
