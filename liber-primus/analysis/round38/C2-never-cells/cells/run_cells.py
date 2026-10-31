#!/usr/bin/env python3
"""Round 38 / C2 sub-lane N: the (a)-cells.  python run_cells.py <H5xF1|H6xF2|L8xF6|L15xF6F7|L17xF7|L4xF3|all>.  Writes only under cells/<cell>/."""
import os, sys, re, hashlib
sys.dont_write_bytecode = True
CD = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(CD))
from lib import *      # noqa
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp, ciphers, corpus
PRIMES = gp.PRIMES
CLUES = {c["id"]: c["text"] for c in json.load(open(os.path.join(LP, "analysis", "round36", "O4-clue-coverage", "clues.json"), encoding="utf-8"))}
NKEY = S.NKEY


def cdir(name):
    d = os.path.join(CD, name); os.makedirs(d, exist_ok=True); return d


def cyc(base, n=NKEY): return [base[i % len(base)] % 29 for i in range(n)]


def beam_grid_rows(rows, fam, keys, L=120, signs=(-1, 1), offs=range(8)):
    """keys: dict name -> K list. Decode U[:L] over rel x sign x off; returns list of (kid, pmax, preg, plain)"""
    out = []
    for kn, K in keys.items():
        for rel, sign, off in itertools.product(RELS, signs, offs):
            d, a = v3dec(U[:L], K, rel, sign, off); kid = "%s:%s:%s:%d:%d" % (fam, kn, rel, sign, off)
            pm = rows.add(a, kid, fam, rel, kn); out.append((kid, pm, rel, d["plain_idx"], a))
    return out


def rank_control(fam, keys, plant_key, rng, nplants=2, extra=None):
    """plant keys[plant_key] through both relations, decode against all keys, report rank / pmax / recovery."""
    res = []
    for rel in RELS:
        K = keys[plant_key]; o = rng.randrange(8); P = held(rng=rng); Cc = E.encipher_with_key(P, K[o:], rel, rng.randrange(1, 10 ** 9))[:240]
        best = {}
        for kn, Kj in keys.items():
            for r2, s2, o2 in itertools.product(RELS, (-1, 1), range(8)):
                d, a = v3dec(Cc[:120], Kj, r2, s2, o2)
                if float(a["pmax"]) > best.get(kn, (-9,))[0]: best[kn] = (float(a["pmax"]), "%s/%d/%d" % (r2, s2, o2))
        rank = sorted(best.items(), key=lambda t: -t[1][0]); pos = [i for i, (k, v) in enumerate(rank) if k == plant_key][0] + 1
        d2, a2 = v3dec(Cc, K, rel, -1, o); e = {"plant": plant_key, "rel": rel, "offset": o, "n_keys": len(rank), "rank": pos, "pmax120_in_grid": round(best[plant_key][0], 3),
                                                  "runner_up": [rank[1][0] if pos == 1 else rank[0][0], round(rank[1][1][0] if pos == 1 else rank[0][1][0], 3)]}
        e.update(judge(best[plant_key][0], float(a2["pmax"]), rec_of(d2["plain_idx"], P), rel)); e["recover"] = bool(e["recover"] and pos == 1); res.append(e)
    return res


def finish_decode_cell(name, rows, N, controls, extra):
    rows.close(); AD.validate_store(rows.path)
    sys.path.insert(0, os.path.join(LP, "analysis", "handoff")); import validate_ledger as VL
    best = {}
    for k, v in rows.best.items(): best.setdefault(k[1], []).append(v)
    out = {"cell": name, "N": N, "control": controls, "best_by_rel": {}}
    for rel, lst in best.items():
        b = max(lst, key=lambda v: v["pmax"]); n = N[rel] if isinstance(N, dict) else N
        out["best_by_rel"][rel] = dict(b, bar_v3_L120_actualN=round(bv3(n, 120, rel), 3), bar12_actualN=round(b12(n, 120, rel), 3), bar_v3_N1e6=round(bv3(1e6, 120, rel), 3),
                                        clears_actualN=bool(b["pmax"] >= bv3(n, 120, rel)))
    out["validate_store"] = "ok"; out["check_r3_store"] = VL.check_r3_store(rows.path); out.update(extra)
    json.dump(out, open(os.path.join(cdir(name), "results.json"), "w"), indent=1); print(name, json.dumps(out["best_by_rel"])[:900], out["check_r3_store"], flush=True)
    return out


def gate_hits(name, hits):
    """hits: list of (kid, pm, rel, plain, a) at/above bar -> re-decode at L=240 is the caller's job; here just write file"""
    json.dump(hits, open(os.path.join(cdir(name), "gate_hits.json"), "w"), indent=1)


# ------------------------------------------------------------------ cell 1: H5 x F1  (the empty path = identity key)
def cell_H5xF1():
    name = "H5xF1"; d = cdir(name); rng = random.Random(38101); wait_mem(); t0 = time.time()
    heads = [U[page_start(p):page_start(p) + 240] for p in range(6)]
    def family(streams):
        out = []
        for hi, c in enumerate(streams):
            for atb in (0, 1):
                base = ciphers.atbash_indices(c) if atb else list(c)
                for s in range(29): out.append(("h%d:atb%d:s%d" % (hi, atb, s), [(x + s) % 29 for x in base]))
        return out
    ctrl = []
    for reg, s, atb in (("EN_MODERN", 0, 0), ("LATIN", 11, 1), ("GREEK", 17, 0)):
        P = held(reg, 240, rng); c = [(p - s) % 29 for p in P]; c = ciphers.atbash_indices(c) if atb else c
        best = max(((float(AD.adjudicate(x)["pmax"]), k) for k, x in family([c])), key=lambda t: t[0])
        ctrl.append({"register": reg, "shift": s, "atbash": atb, "best_kid": best[1], "best_pmax": round(best[0], 3), "bar_v3_240_N1e6": round(bv3(1e6, 240, "keyskip1"), 3),
                     "recover": bool(best[0] >= bv3(1e6, 240, "keyskip1") and best[1].endswith("atb%d:s%d" % (atb, s)))})
    print("H5xF1 control", [c["recover"] for c in ctrl], flush=True)
    valid = all(c["recover"] for c in ctrl)
    rows = Rows(os.path.join(d, "rows.jsonl"), header("round38/C2/H5xF1", "identity key: (c+s) or atbash(c)+s, s 0..28, 6 page heads L=240", "direct panel-R36 pmax of the bare stream (no beam)", "h5:head:atb:shift", 348))
    N = 0; best = (-9, None)
    if valid:
        for k, x in family(heads):
            a = AD.adjudicate(x); rows.add(a, "h5:" + k, "H5xF1", "direct", "identity"); N += 1
            if float(a["pmax"]) > best[0]: best = (float(a["pmax"]), k, REGS[a["preg"]])
    # empirical family-max null on shuffled LP2 (D=100)
    fam_max = []
    for dd in range(100):
        sh = U[:]; random.Random(8100 + dd).shuffle(sh); m = -9
        for hi in range(6):
            for k, x in family([sh[hi * 240:(hi + 1) * 240]]):
                m = max(m, float(AD.adjudicate(x)["pmax"]))
        fam_max.append(m)
    exc = sum(1 for m in fam_max if m >= best[0])
    rows.close(); AD.validate_store(rows.path)
    bar = bv3(N, 240, "keyskip1")
    out = {"cell": name, "N": N, "control": ctrl, "best_pmax": round(best[0], 3), "best_kid": best[1], "best_register": best[2], "bar_v3_L240_actualN_ks1_conservative": round(bar, 3),
           "bar_v3_L240_N1e6": round(bv3(1e6, 240, "keyskip1"), 3), "clears_actualN": bool(best[0] >= bar), "empirical_family_null": {"D": 100, "mean": round(sum(fam_max) / 100, 3), "max": round(max(fam_max), 3), "exceed": exc, "p": round((1 + exc) / 101, 3)},
           "note": "direct panel-R36 pmax of bare streams; beam bar used as a conservative bar; the empirical shuffled-LP2 family-max null is the matched one", "elapsed_s": round(time.time() - t0)}
    json.dump(out, open(os.path.join(d, "results.json"), "w"), indent=1); print(name, json.dumps(out)[:700], flush=True)


# ------------------------------------------------------------------ cell 2: H6 x F2  (7A35090F as a number)
def cell_H6xF2():
    name = "H6xF2"; d = cdir(name); rng = random.Random(38102); wait_mem(); t0 = time.time()
    N0 = 0x7A35090F
    py = random.Random(N0); npr = np.random.RandomState(N0)
    keys = {"decimal_digits": cyc([int(c) for c in str(N0)]), "hex_nibbles": cyc([int(c, 16) for c in "7A35090F"]), "bytes_mod29": cyc([0x7A, 0x35, 0x09, 0x0F]),
            "py_random_getrandbits32_mod29": [py.getrandbits(32) % 29 for _ in range(NKEY)], "numpy_mt19937_randint29": [int(x) for x in npr.randint(0, 29, size=NKEY)]}
    ctrl = []
    for kn in keys: ctrl += rank_control("H6xF2", keys, kn, rng)
    print("H6xF2 control", [(c["plant"][:6], c["rel"][-1], c["rank"], c["recover"]) for c in ctrl], flush=True)
    validk = {kn: all(c["recover"] for c in ctrl if c["plant"] == kn) for kn in keys}
    rows = Rows(os.path.join(d, "rows.jsonl"), header("round38/C2/H6xF2", "key ID 7A35090F as a number: 5 key classes x ks1/ks2 x sign x offset 0..7, L=120", "beam_v3 panel_max keyskip1/keyskip2", "H6xF2:key:rel:sign:off", 160))
    run = beam_grid_rows(rows, "H6xF2", {k: K for k, K in keys.items() if validk[k]})
    n = {rel: sum(1 for r in run if r[2] == rel) for rel in RELS}
    gates = [r[:3] for r in run if r[1] >= bv3(n[r[2]], 120, r[2])]
    finish_decode_cell(name, rows, n, ctrl, {"valid_keys": validk, "at_or_above_bar_L120": gates, "elapsed_s": round(time.time() - t0)})


# ------------------------------------------------------------------ cell 3: L8 x F6  (four unreasonable things: period-4 AP key)
def cell_L8xF6():
    name = "L8xF6"; d = cdir(name); rng = random.Random(38103); wait_mem(); t0 = time.time()
    def key(d0, step): return [(d0 + (i % 4) * step) % 29 for i in range(NKEY)]
    allk = {"ap_d%d_s%d" % (d0, st): None for d0 in range(29) for st in range(29)}
    ctrl = []
    for d0, st in ((5, 7), (20, 3), (0, 0)):
        P = held(rng=rng); K = key(d0, st); Cc = E.encipher_with_key(P, K, "keyskip1", rng.randrange(1, 10 ** 9))[:240]; best = (-9, None)
        for kn in allk:
            a0, s0 = [int(x[1:]) for x in kn.split("_")[1:]]
            d_, a = v3dec(Cc[:120], key(a0, s0), "keyskip1", -1, 0)
            if float(a["pmax"]) > best[0]: best = (float(a["pmax"]), kn)
        d2, a2 = v3dec(Cc, K, "keyskip1", -1, 0); e = {"plant": "ap_d%d_s%d" % (d0, st), "best_in_grid": best[1], "pmax120_in_grid": round(best[0], 3)}
        e.update(judge(best[0], float(a2["pmax"]), rec_of(d2["plain_idx"], P), "keyskip1")); e["recover"] = bool(e["recover"] and best[1] == e["plant"]); ctrl.append(e)
        print("L8xF6 ctrl", e, flush=True)
    valid = all(c["recover"] for c in ctrl)
    rows = Rows(os.path.join(d, "rows.jsonl"), header("round38/C2/L8xF6", "period-4 arithmetic-progression additive key d0 + (i mod 4)*step, 841 keys, ks1, sign -1, L=120", "beam_v3 panel_max keyskip1", "L8xF6:d0:step", 841))
    n = 0
    if valid:
        for kn in allk:
            a0, s0 = [int(x[1:]) for x in kn.split("_")[1:]]
            dd, a = v3dec(U[:120], key(a0, s0), "keyskip1", -1, 0); rows.add(a, "L8xF6:%s" % kn, "L8xF6", "keyskip1", kn); n += 1
    finish_decode_cell(name, rows, {"keyskip1": n}, ctrl, {"valid": valid, "elapsed_s": round(time.time() - t0)})


# ------------------------------------------------------------------ cell 4: L15 x F6/F7  (the held 5x5 square as a key)
def cell_L15():
    name = "L15xF6F7"; d = cdir(name); rng = random.Random(38104); wait_mem(); t0 = time.time()
    txt = CLUES["ST-MAGIC-KNOWTHIS2"]; nums = [int(x) for x in re.findall(r"\d+", txt.split("(")[0])][-25:]
    assert len(nums) == 25, nums
    M5 = [nums[i * 5:(i + 1) * 5] for i in range(5)]
    def spiral(m):
        out = []; top, bot, l, r = 0, len(m) - 1, 0, len(m[0]) - 1
        while top <= bot and l <= r:
            out += [m[top][c] for c in range(l, r + 1)]; top += 1
            out += [m[rr][r] for rr in range(top, bot + 1)]; r -= 1
            if top <= bot: out += [m[bot][c] for c in range(r, l - 1, -1)]; bot -= 1
            if l <= r: out += [m[rr][l] for rr in range(bot, top - 1, -1)]; l += 1
        return out
    rowm = [v for r in M5 for v in r]; colm = [M5[i][j] for j in range(5) for i in range(5)]
    snake = [v for i, r in enumerate(M5) for v in (r if i % 2 == 0 else r[::-1])]
    diag = [M5[i][i] for i in range(5)]; dfirst = diag + [M5[i][j] for i in range(5) for j in range(5) if i != j]
    sp = spiral(M5); orders = {"row": rowm, "col": colm, "snake": snake, "spiral_in": sp, "spiral_out": sp[::-1], "diag_first": dfirst}
    keys = {"%s|m%d" % (o, m): cyc([v % m for v in seq]) for o, seq in orders.items() for m in (29, 28)}
    ctrl = rank_control("L15", keys, "row|m29", rng) + rank_control("L15", keys, "spiral_out|m28", rng)
    print("L15 control", [(c["plant"], c["rel"][-1], c["rank"], c["recover"]) for c in ctrl], flush=True)
    valid = all(c["recover"] for c in ctrl)
    rows = Rows(os.path.join(d, "rows.jsonl"), header("round38/C2/L15", "held 5x5 magic square (ST-MAGIC-KNOWTHIS2) in 6 cell orders x mod 29/28 as cyclic additive key x ks1/ks2 x sign x offset 0..7, L=120", "beam_v3 panel_max keyskip1/keyskip2", "L15:order|mod:rel:sign:off", 384))
    run = beam_grid_rows(rows, "L15", keys) if valid else []
    n = {rel: sum(1 for r in run if r[2] == rel) for rel in RELS}
    gates = [r[:3] for r in run if r[1] >= bv3(n[r[2]], 120, r[2])]
    finish_decode_cell(name, rows, n, ctrl, {"valid": valid, "matrix": M5, "at_or_above_bar_L120": gates, "elapsed_s": round(time.time() - t0)})


# ------------------------------------------------------------------ cell 5: L17 x F7  (LP pages hashed against the AN END hash)
def cell_L17xF7():
    name = "L17xF7"; d = cdir(name); t0 = time.time()
    H = CLUES["LP1-ANEND-HASH"].strip().lower(); assert len(H) == 128
    pages = [p for p in corpus.parse() if p["runes"]]
    RUNE_RE = re.compile(r"[áš -á›¿]")
    def norm(t): return "\n".join(l.strip() for l in t.split("\n"))
    texts = [norm(p["runes"]) for p in pages]
    units = [("page:%s" % pages[i]["label"], texts[i]) for i in range(len(pages))]
    units += [("pair:%s+%s" % (pages[i]["label"], pages[i + 1]["label"]), texts[i] + "\n" + texts[i + 1]) for i in range(len(pages) - 1)]
    units += [("book", "\n".join(texts))]
    def reps(t):
        r = "".join(RUNE_RE.findall(t)); idx = [gp.RUNE_TO_IDX[c] for c in r if c in gp.RUNE_TO_IDX]; tr = "".join(gp.IDX_TO_TRANS[i] for i in idx)
        wl = [w for w in re.split(r"[â€¢\n ]+", t) if w]
        trw = " ".join("".join(gp.IDX_TO_TRANS[gp.RUNE_TO_IDX[c]] for c in RUNE_RE.findall(w) if c in gp.RUNE_TO_IDX) for w in wl)
        trl = "\n".join(" ".join("".join(gp.IDX_TO_TRANS[gp.RUNE_TO_IDX[c]] for c in RUNE_RE.findall(w) if c in gp.RUNE_TO_IDX) for w in re.split(r"[â€¢ ]+", ln) if w) for ln in t.split("\n"))
        return {"raw": t, "raw_LFend": t + "\n", "raw_CRLF": t.replace("\n", "\r\n"), "no_newlines": t.replace("\n", ""), "nl_to_space": t.replace("\n", " "),
                "runes_only": r, "runes_only_LFend": r + "\n", "idx_bytes": bytes(idx), "translit": tr, "translit_lower": tr.lower(), "translit_words": trw, "translit_lines": trl}
    algos = {"sha512": lambda b: hashlib.sha512(b).hexdigest(), "blake2b512": lambda b: hashlib.blake2b(b, digest_size=64).hexdigest(), "sha3_512": lambda b: hashlib.sha3_512(b).hexdigest()}
    def scan(targets, units_):
        hits = []; n = 0
        for uname, t in units_:
            for rn, rv in reps(t).items():
                b = rv if isinstance(rv, bytes) else rv.encode("utf-8")
                for an, f in algos.items():
                    n += 1; h = f(b)
                    if h in targets: hits.append({"unit": uname, "rep": rn, "algo": an, "target": targets[h]})
        return hits, n
    # control: H' = sha512 of page 7's no_newlines representation, substituted for H
    cu = units[7]; hp = hashlib.sha512(reps(cu[1])["no_newlines"].encode("utf-8")).hexdigest()
    ch, cn = scan({hp: "H_prime"}, units)
    ctrl = {"unit": cu[0], "rep": "no_newlines", "algo": "sha512", "found": [h for h in ch if h["unit"] == cu[0] and h["rep"] == "no_newlines" and h["algo"] == "sha512"], "n_hashes": cn}
    ctrl["recover"] = bool(ctrl["found"]); print("L17xF7 control", ctrl["recover"], flush=True)
    # second unit set: the 55 LP2 pages of the cipher stream (PARSE) - runes only, no layout from the md file
    def reps2(rs, ws, lns):
        r = "".join(gp.IDX_TO_RUNE[i] for i in rs); tr = "".join(gp.IDX_TO_TRANS[i] for i in rs)
        wr = [("".join(gp.IDX_TO_RUNE[i] for i in w)) for w in ws]; wt = ["".join(gp.IDX_TO_TRANS[i] for i in w) for w in ws]
        lr = ["".join(gp.IDX_TO_RUNE[i] for i in l) for l in lns]
        return {"runes_only": r, "runes_only_LFend": r + "\n", "idx_bytes": bytes(rs), "translit": tr, "translit_lower": tr.lower(), "words_bullet": "•".join(wr), "words_space": " ".join(wr),
                "translit_words_space": " ".join(wt), "translit_words_dash": "-".join(wt), "lines_LF": "\n".join(lr), "lines_LF_end": "\n".join(lr) + "\n", "lines_CRLF": "\r\n".join(lr)}
    pg = PARSE["pages"]; wp = PARSE["w_page"]; lp_ = PARSE["line_page"]; W_ = PARSE["words"]; L_ = PARSE["lines"]
    def page_obj(ps):
        rs = [i for p in ps for i in pg[p]]; ws = [w for w, q in zip(W_, wp) if q in ps]; lns = [l for l, q in zip(L_, lp_) if q in ps]; return rs, ws, lns
    units2 = [("lp2page:%d" % p, page_obj([p])) for p in range(len(pg))] + [("lp2pair:%d+%d" % (p, p + 1), page_obj([p, p + 1])) for p in range(len(pg) - 1)] + [("lp2full", page_obj(list(range(len(pg)))))]
    def scan2(targets):
        hits = []; n = 0
        for uname, (rs, ws, lns) in units2:
            for rn, rv in reps2(rs, ws, lns).items():
                b = rv if isinstance(rv, bytes) else rv.encode("utf-8")
                for an, f in algos.items():
                    n += 1; h = f(b)
                    if h in targets: hits.append({"unit": uname, "rep": rn, "algo": an, "target": targets[h]})
        return hits, n
    hp2 = hashlib.sha512(reps2(*units2[7][1])["runes_only"].encode("utf-8")).hexdigest(); ch2, cn2 = scan2({hp2: "H_prime2"})
    ctrl["recover2"] = bool([h for h in ch2 if h["unit"] == units2[7][0] and h["rep"] == "runes_only" and h["algo"] == "sha512"]); ctrl["n_hashes2"] = cn2
    hits, n = scan({H: "H_anend"}, units) if ctrl["recover"] else ([], 0)
    hits2, n2 = scan2({H: "H_anend"}) if ctrl["recover2"] else ([], 0)
    hits += hits2; n += n2
    out = {"cell": name, "target_H": H, "n_pages_with_runes": len(pages), "n_units": len(units), "n_units_lp2_stream": len(units2), "n_representations": "12 (md pages) / 12 (LP2 stream pages)", "algorithms": list(algos), "n_hashes": n, "hits": hits, "control": ctrl, "elapsed_s": round(time.time() - t0)}
    json.dump(out, open(os.path.join(d, "results.json"), "w"), indent=1); print(name, len(units), n, "hits", len(hits), flush=True)


# ------------------------------------------------------------------ cell 6: L4 x F3  (word-level primality)
def cell_L4xF3():
    name = "L4xF3"; d = cdir(name); t0 = time.time(); rng = np.random.default_rng(38106)
    LIM = 109 * 600; sv = np.ones(LIM + 1, bool); sv[:2] = False
    for i in range(2, int(LIM ** .5) + 1):
        if sv[i]: sv[i * i::i] = False
    PR = np.array(PRIMES)
    def groups_lp2():
        words = PARSE["words"]; wp = PARSE["w_page"]; g = {}
        for w, p in zip(words, wp): g.setdefault(p, []).append(w)
        out = []
        for p, ws in g.items():
            vals = PR[np.array([i for w in ws for i in w])]; out.append((vals, [len(w) for w in ws]))
        return out
    def groups_lp1(): return [(PR[np.array([i for w in s for i in runes_(w)])], [len(runes_(w)) for w in s]) for s in E.SENTS]
    def runes_(w): return E.runes(w)
    def count(groups, shuffle=False, B=1):
        tot = np.zeros(B)
        for vals, lens in groups:
            b = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(int)
            if not shuffle: tot += sv[np.add.reduceat(vals, b)].sum()
            else:
                perm = np.argsort(rng.random((B, len(vals))), axis=1); tot += sv[np.add.reduceat(vals[perm], b, axis=1)].sum(1)
        return tot
    def test(groups, D=10000, chunk=500):
        obs = float(count(groups)[0]); nw = sum(len(l) for _, l in groups); nul = np.concatenate([count(groups, True, chunk) for _ in range(D // chunk)])
        return {"n_words": nw, "prime_sum_words": int(obs), "null_mean": round(float(nul.mean()), 2), "null_sd": round(float(nul.std()), 2), "z": round((obs - nul.mean()) / nul.std(), 2),
                "p_upper": round(float((1 + (nul >= obs).sum()) / (D + 1)), 4), "p_lower": round(float((1 + (nul <= obs).sum()) / (D + 1)), 4)}
    g2 = groups_lp2(); g1 = groups_lp1()
    # control: planted prime-sum words on the LP2 word-length structure
    pl = []
    for vals, lens in g2:
        out = []
        for l in lens:
            for _ in range(5000):
                r = rng.integers(0, 29, l)
                if sv[int(PR[r].sum())]: break
            out += r.tolist()
        pl.append((PR[np.array(out)], lens))
    cres = test(pl, D=2000, chunk=500); cres["recover"] = bool(cres["p_upper"] < 0.001); print("L4xF3 control", cres, flush=True)
    res = {"cell": name, "control_planted_prime_words": cres, "LP2_cipher_words": test(g2) if cres["recover"] else None, "LP1_plaintext_words": test(g1) if cres["recover"] else None, "elapsed_s": round(time.time() - t0)}
    json.dump(res, open(os.path.join(d, "results.json"), "w"), indent=1); print(name, json.dumps(res)[:900], flush=True)


CELLS = {"H5xF1": cell_H5xF1, "H6xF2": cell_H6xF2, "L8xF6": cell_L8xF6, "L15xF6F7": cell_L15, "L17xF7": cell_L17xF7, "L4xF3": cell_L4xF3}
if __name__ == "__main__":
    for c in (list(CELLS) if sys.argv[1] == "all" else sys.argv[1:]): CELLS[c]()
