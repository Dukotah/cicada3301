"""R44 / W2-A2 shared glue — vocabulary, difference tables, keys, crib filter, decode glue.

Everything pre-registered in PREREG.md.  Pure python3 + numpy, no network.
Reuses the R44-R1 validated key/decode code (resets.py) and the standing panel instrument.
"""
import json
import os
import re
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R1 = os.path.join(LP, "analysis", "round44", "R1-key-resets")
for p in (os.path.join(LP, "src"), R1, os.path.join(LP, "tests"),
          os.path.join(LP, "analysis", "round19", "I2"),
          os.path.join(LP, "analysis", "round34", "I1-v3-null")):
    sys.path.insert(0, p)

from lp import gematria as gp, corpus, solve, score as _score   # noqa: E402
import resets as R                                              # noqa: E402

N = 29
KEY_LEN = 13400                 # global phase needs 12956 + 200 + 85 + slack
SITE_A_PAGE, SITE_A_POS, SITE_A_GLOBAL = 27, 28, 6555
SITE_B_PAGE, SITE_B_POS, SITE_B_GLOBAL = 54, 70, 12950
P55_GLOBAL = 12956
GRAM = (23, 11, 1, 17, 18, 10, 25)   # D J U B E I AE
CRIB_C, CRIB_P = 25, 24              # p55 pos 0: ciphertext AE, known plaintext A
N_BAR = 400_000
BARS = {120: 14.8161, 240: 19.9112}  # bars_v3(400000, L, 'free'), PREREG section 6
CFGS = R.CFGS                        # ("vigm","vigp","beau","vigm_atb","vigp_atb","beau_atb")


# ------------------------------------------------------------------ config algebra
def derive_key(c, p, cfg):
    """The key value that decodes ciphertext c to plaintext p under cfg."""
    x = (N - 1) - c if cfg.endswith("_atb") else c
    base = cfg.split("_")[0]
    if base == "vigm":                 # p = x - k
        return (x - p) % N
    if base == "vigp":                 # p = x + k
        return (p - x) % N
    return (p + x) % N                 # beau: p = k - x


def cfg_sign(cfg):
    """Collision condition k1 - k2 = sign * (P1 - P2) mod 29 (identical ciphertext).
    vigm: k = x - p  -> k1-k2 = p2-p1 = -(P1-P2):  sign -1
    vigp: k = p - x  -> k1-k2 = p1-p2:             sign +1
    beau: k = p + x  -> k1-k2 = p1-p2:             sign +1
    atbash-pre only changes x (same at both sites), so signs carry."""
    return -1 if cfg.split("_")[0] == "vigm" else +1


REQ_K = {cfg: derive_key(CRIB_C, CRIB_P, cfg) for cfg in CFGS}
# sanity (PREREG section 6): vigm 1, vigp 28, beau 20, vigm_atb 8, vigp_atb 21, beau_atb 27
assert REQ_K == {"vigm": 1, "vigp": 28, "beau": 20,
                 "vigm_atb": 8, "vigp_atb": 21, "beau_atb": 27}, REQ_K


# ------------------------------------------------------------------ canon / p55 ground truth
def canon_pages():
    return R.parse_pages()          # 57 pages, dict(idx, line_of)


def verify_premise(pages):
    """Re-verify the R44-R1 site facts + the crib facts (PREREG Q5 ii)."""
    flat = [i for pg in pages for i in pg["idx"]]
    lens = [len(pg["idx"]) for pg in pages]
    gA = sum(lens[:SITE_A_PAGE]) + SITE_A_POS
    gB = sum(lens[:SITE_B_PAGE]) + SITE_B_POS
    ok = (gA == SITE_A_GLOBAL and gB == SITE_B_GLOBAL
          and tuple(flat[gA:gA + 7]) == GRAM and tuple(flat[gB:gB + 7]) == GRAM
          and sum(lens[:55]) == P55_GLOBAL and lens[54] == 76
          and pages[55]["idx"][0] == CRIB_C)
    return ok, dict(gA=gA, gB=gB, p54_len=lens[54], p55_first=pages[55]["idx"][0])


def _phi_prime(length):
    out, p = [], 2
    def isp(n):
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return True
    while len(out) < length:
        out.append((p - 1) % N)
        p += 1
        while not isp(p):
            p += 1
    return out


def p55_ground_truth():
    """The known p55 (73.jpg) solve: plaintext indices, null-F cutoff, per-cfg required key
    vector R_j for the continuous-stream hypothesis (PREREG section 6 'Propagation')."""
    page = corpus.page_by_label("73.jpg")
    idxs = gp.runes_to_indices(page["runes"])
    stream = _phi_prime(len(idxs))
    res = solve.find_interrupters(page["runes"], stream, sign=-1,
                                  beam_width=500, scorer=_score.default())
    nulls = set(res["interrupters"])              # F-occurrence numbers that are nulls
    # walk ciphertext; find the position of the first null-F (propagation truncates there)
    plain, f_seen, j, cutoff = [], 0, 0, None
    for pos, c in enumerate(idxs):
        if c == 0:                                # an F rune
            if f_seen in nulls:
                if cutoff is None:
                    cutoff = pos
                f_seen += 1
                plain.append(None)                # null: no plaintext, key not advanced
                continue
            f_seen += 1
        plain.append((c - stream[j]) % N)
        j += 1
    T_max = cutoff if cutoff is not None else len(idxs)
    T_max = min(T_max, 30)                        # PREREG cap
    req = {cfg: [derive_key(idxs[t], plain[t], cfg) for t in range(T_max)] for cfg in CFGS}
    head_translit = gp.indices_to_translit([p for p in plain[:12] if p is not None])
    assert head_translit.startswith("ANEND"), head_translit
    return dict(cipher=idxs, plain=plain, T_max=T_max, req=req,
                n_interrupters=len(nulls), head=head_translit)


# ------------------------------------------------------------------ vocabulary (PREREG section 3)
def _brute_simple_transform(idxs):
    """validate.py brute_simple, returning the per-rune transform (atb, sign, k)."""
    scorer = _score.default()
    best = None
    for atb in (False, True):
        base = [(N - 1) - c for c in idxs] if atb else idxs
        for k in range(N):
            for sign in (-1, +1):
                out = [(c + sign * k) % N for c in base]
                sc = scorer.score_norm(gp.indices_to_translit(out))
                if best is None or sc > best[0]:
                    best = (sc, atb, sign, k)
    return best[1], best[2], best[3]


def _page_words(runes_text):
    """Word tokens as lists of rune indices (maximal rune runs)."""
    words, cur = [], []
    for ch in runes_text:
        if ch in gp.RUNE_TO_IDX:
            cur.append(gp.RUNE_TO_IDX[ch])
        elif cur:
            words.append(cur)
            cur = []
    if cur:
        words.append(cur)
    return words


def solved_page_words():
    """Plaintext words (index tuples) from the 6 solved pages, decoded per validate.py."""
    out = []
    scorer = _score.default()
    for lab in ("Runes - 01.jpg", "05.jpg", "06.jpg"):          # simple pages
        page = corpus.page_by_label(lab)
        idxs = gp.runes_to_indices(page["runes"])
        atb, sign, k = _brute_simple_transform(idxs)
        for w in _page_words(page["runes"]):
            dec = [((((N - 1) - c) if atb else c) + sign * k) % N for c in w]
            out.append(tuple(dec))
    for lab, key in (("03.jpg", "DIVINITY"), ("14.jpg", "FIRFUMFERENFE")):
        page = corpus.page_by_label(lab)
        idxs = gp.runes_to_indices(page["runes"])
        from lp import ciphers
        stream = ciphers.repeat_key(gp.keyword_to_indices(key), len(idxs))
        res = solve.find_interrupters(page["runes"], stream, sign=-1,
                                      beam_width=500, scorer=scorer)
        out += _keyed_words(page["runes"], stream, set(res["interrupters"]))
    # 73.jpg via ground truth machinery
    page = corpus.page_by_label("73.jpg")
    idxs = gp.runes_to_indices(page["runes"])
    res = solve.find_interrupters(page["runes"], _phi_prime(len(idxs)), sign=-1,
                                  beam_width=500, scorer=scorer)
    out += _keyed_words(page["runes"], _phi_prime(len(idxs)), set(res["interrupters"]))
    return out


def _keyed_words(runes_text, stream, nulls):
    """Decode a vigenere/totient page word-by-word honouring null-F interrupters."""
    words, cur, f_seen, j = [], [], 0, 0
    for ch in runes_text:
        if ch in gp.RUNE_TO_IDX:
            c = gp.RUNE_TO_IDX[ch]
            if c == 0:
                if f_seen in nulls:
                    f_seen += 1
                    continue                       # null: nothing emitted
                f_seen += 1
            cur.append((c - stream[j]) % N)
            j += 1
        elif cur:
            words.append(tuple(cur))
            cur = []
    if cur:
        words.append(tuple(cur))
    return words


def _corpus_words(path, top_words, top_heads):
    txt = open(path, encoding="utf-8", errors="ignore").read().upper()
    toks = Counter(re.findall(r"[A-Z]+", txt))
    enc3, heads = [], []
    for w, _n in toks.most_common():
        try:
            e = gp.keyword_to_indices(w)
        except ValueError:
            continue
        if len(e) == 3 and len(enc3) < top_words:
            enc3.append(tuple(e))
        if len(e) >= 2 and len(heads) < top_heads:
            heads.append(e[0])
        if len(enc3) >= top_words and len(heads) >= top_heads:
            break
    return enc3, heads


def build_vocab():
    """(V3 set of index triples, H set of head indices) exactly per PREREG section 3."""
    sw = solved_page_words()
    v3 = {w for w in sw if len(w) == 3}
    heads = {w[0] for w in sw if len(w) >= 2}
    kj3, kjh = _corpus_words(os.path.join(LP, "data", "kjv.txt"), 150, 500)
    la3, lah = _corpus_words(os.path.join(LP, "analysis", "latin", "latin_28233.txt"), 100, 300)
    v3 |= set(kj3) | set(la3)
    heads |= set(kjh) | set(lah)
    return v3, heads


# ------------------------------------------------------------------ difference tables
def pack3(d):
    """Pack a (...,3) array of mod-29 digits into base-29 ints."""
    d = np.asarray(d, dtype=np.int64) % N
    return d[..., 0] * N * N + d[..., 1] * N + d[..., 2]


def g3_table(v3):
    """g3[packed d] = #{(u,v) in V3^2 : (u-v) mod 29 == d} (directed pairs, incl. u==v)."""
    A = np.array(sorted(v3), dtype=np.int64)               # (n,3)
    D = (A[:, None, :] - A[None, :, :]) % N                # (n,n,3)
    t = np.zeros(N ** 3, dtype=np.int64)
    np.add.at(t, pack3(D).ravel(), 1)
    return t, A


def v3_packed_set(v3):
    return set(int(pack3(np.array(w))) for w in v3)


# ------------------------------------------------------------------ keys
def build_keys():
    R.KEY_LEN = KEY_LEN
    return R.build_keys()           # 51 keys, np arrays length 13400


# ------------------------------------------------------------------ crib filter + decode
def crib_cells(keys):
    """All crib-consistent (kname, cfg, mode, o) per PREREG section 6, plus the o<=29
    section flags (reported, not decoded)."""
    cells, flags_only = [], []
    for kname, K in keys.items():
        for cfg in CFGS:
            req = REQ_K[cfg]
            for o in range(0, 30):
                if K[o + 76] == req:
                    flags_only.append((kname, cfg, "section", o))
            for o in range(30, 201):
                if K[o + 76] == req:
                    cells.append((kname, cfg, "section", o))
            for o in range(0, 201):
                if K[o + P55_GLOBAL] == req:
                    cells.append((kname, cfg, "global", o))
    return cells, flags_only


def propagation_depth(K, o, cfg, mode, gt):
    """Leading p55 positions matched by K under the continuous hypothesis (cap gt['T_max'])."""
    base = (o + 76) if mode == "section" else (o + P55_GLOBAL)
    req = gt["req"][cfg]
    t = 0
    while t < gt["T_max"] and K[base + t] == req[t]:
        t += 1
    return t


def page_phases(pages):
    """Per unsolved page: section phase vector (resets.py) and global phase vector."""
    pv = R.phase_vectors(pages)
    lens = [len(pg["idx"]) for pg in pages]
    starts = np.cumsum([0] + lens[:-1])
    out = []
    for pi in range(55):
        out.append({"section": pv[pi]["section"],
                    "global": np.arange(lens[pi], dtype=np.int64) + int(starts[pi])})
    return out


def decode_cell_pages(c_list, ph_list, K, o, cfg, mode):
    """Decode every page for one cell; returns list of decode arrays."""
    outs = []
    for c, ph in zip(c_list, ph_list):
        Kmat = K[np.asarray([o], dtype=np.int64)[:, None] + np.asarray(ph[mode])[None, :]]
        outs.append(R.decode_block(np.asarray(c, dtype=np.int64), Kmat, cfg)[0])
    return outs


def lcap(L):
    return 240 if L >= 240 else 120


# ------------------------------------------------------------------ part-1 solver core
def ap_scan(v3, heads, fixed_head=CRIB_P, list_pairs=True):
    """Constant (b=0) + AP cells: e_i = a + b*i. Returns the 29x29 count tables and the
    explicit constant-row pairs. P2 = P1 - e; site-B head fixed -> P1[6] = fixed_head + e6."""
    A = np.array(sorted(v3), dtype=np.int64)
    packed = np.sort(pack3(A))
    out = np.zeros((N, N), dtype=np.int64)          # with-head counts (i=0..6)
    out_nh = np.zeros((N, N), dtype=np.int64)       # head-free counts (i=0..5, page-style)
    const_pairs = []
    for a in range(N):
        for b in range(N):
            s1 = np.array([a, a + b, a + 2 * b]) % N
            s2 = np.array([a + 3 * b, a + 4 * b, a + 5 * b]) % N
            m1 = np.isin(pack3((A - s1) % N), packed)
            m2 = np.isin(pack3((A - s2) % N), packed)
            c1, c2 = int(m1.sum()), int(m2.sum())
            x = (fixed_head + a + 6 * b) % N        # P1[6]
            headok = 1 if x in heads else 0
            n7, n6 = c1 * c2 * headok, c1 * c2
            if a == 0 and b == 0:                   # the same-plaintext diagonal, excluded
                n7, n6 = 0, 0
            out[a, b], out_nh[a, b] = n7, n6
            if list_pairs and b == 0 and n7 > 0:
                row = []
                for u in A[m1]:
                    for v in A[m2]:
                        row.append(dict(
                            s=a, P1_w1=u.tolist(), P1_w2=v.tolist(), P1_head=int(x),
                            P2_w1=((u - a) % N).tolist(), P2_w2=((v - a) % N).tolist(),
                            P1_translit=gp.indices_to_translit(
                                list(u) + list(v) + [int(x)]),
                            P2_translit=gp.indices_to_translit(
                                list((u - a) % N) + list((v - a) % N) + [fixed_head])))
                        if len(row) >= 80:          # per-row cap (R44 W2-A2 plant fix:
                            break                   # a global cap hid planted rows)
                    if len(row) >= 80:
                        break
                const_pairs += row
    return out, out_nh, const_pairs


def gen_scan_key(K, g3, headmask, nv3, omax_grid=260, fixed_head=CRIB_P):
    """One key's free (o1,o2) grid + both diagonals.  headmask = 29-bool (h in H),
    nv3 = |V3| (for the identical-plaintext subtraction at D==0).
    Returns dict of counts; count7 uses i=0..6 w/ head, count6 ignores the head slot."""
    W7 = np.lib.stride_tricks.sliding_window_view(K[:omax_grid + 7], 7)[:omax_grid + 1]
    res = {}
    for tag, D in (("grid", (W7[:, None, :] - W7[None, :, :]) % N),
                   ("diag_section", (K[28:28 + 201 + 7], K[70:70 + 201 + 7])),
                   ("diag_global", (K[SITE_A_GLOBAL:SITE_A_GLOBAL + 201 + 7],
                                    K[SITE_B_GLOBAL:SITE_B_GLOBAL + 201 + 7]))):
        if tag != "grid":
            a, b = D
            Wa = np.lib.stride_tricks.sliding_window_view(a, 7)[:201]
            Wb = np.lib.stride_tricks.sliding_window_view(b, 7)[:201]
            D = (Wa - Wb) % N
        best = {}
        for sg in (+1, -1):
            E = (sg * D) % N
            body = g3[pack3(E[..., 0:3])] * g3[pack3(E[..., 3:6])]
            x = (fixed_head + E[..., 6]) % N
            n7 = body * headmask[x]
            zero = E.sum(axis=-1) == 0              # E is mod-29 nonneg: sum 0 <=> all 0
            n7 = np.maximum(n7 - zero * (nv3 * nv3), 0)   # drop identical-plaintext pairs
            n6 = np.maximum(body - zero * (nv3 * nv3), 0)
            best[sg] = (n7, n6)
        n7 = np.maximum(best[+1][0], best[-1][0])
        n6 = np.maximum(best[+1][1], best[-1][1])
        res[tag] = dict(sat7=int((n7 > 0).sum()), sat6=int((n6 > 0).sum()),
                        cells=int(n7.size), max7=int(n7.max()), max6=int(n6.max()),
                        argmax7=[int(v) for v in np.unravel_index(int(n7.argmax()),
                                                                  n7.shape)])
    return res
