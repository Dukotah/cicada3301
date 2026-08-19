"""Campaign XV, probe P1 -- SKIP-TOLERANT / FILTER-AWARE keystream decode.

SOUNDNESS PATCH on ~112 prior keystream/keytext nulls. Every prior elimination
assumed RIGID key alignment (plaintext position i uses keystream position i). If
the LP2 doublet-suppression filter *skips a keystream symbol on collision* the true
alignment drifts, and a rigid decode of the CORRECT generator would look like noise
after the first skip. This probe builds a beam decoder whose state is
(text position i, keystream index j), allowing a j->j+2 "skip" transition at
collision-consistent sites (small log-penalty), so a correct-but-misaligned
keystream can still be recovered.

Filter / skip model (internally self-consistent so synthetic recovery is exact):
  Encrypt (sign +): c[i] = (p[i] + st[j]) mod N, normally j+=1.
  On a collision (trial c would equal c[i-1]) the encoder SKIPS one key symbol
  with prob p_soft (~0.83): it advances j once (dropping st[j]) then encodes, so
  the key index used at position i is one *ahead* of the rigid expectation.
  The decoder's skip gate at transition i->i+1 choosing j+2 is therefore:
      c[i+1] - c[i]  ==  st[j+2] - st[j+1]   (mod N)
  which is exactly the condition under which st[j+1] would have produced a doublet.

Decode (sign s in {+1,-1}, optional atbash on c): p[i] = (c[i] - s*st[j]) mod N.

GATE: any (generator/text, offset, sign, atbash) whose beam best-path score_norm
> -5.2 with readable Gematria-English = BREAK. A clean null over the attested
generator family + cached keytexts UPGRADES the OTP verdict (rigid caveat discharged).

Run:  PYTHONUTF8=1 python analysis/campaign15/P1-skip-beam.py
"""
import os, sys, glob, math, time, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp, stats, ciphers, score as _score  # noqa

N = gp.N
RUNE = gp.RUNE_TO_IDX
TR = gp.IDX_TO_TRANS
SC = _score.default()
QD = SC.d
FLOOR = SC.floor
GATE = -5.2            # score_norm break threshold
NOISE = -6.0          # rough noise band centre

# ------------------------------------------------------------------ ct stream
def load_stream():
    raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages_raw = [p for p in raw.split("%") if any(ch in RUNE for ch in p)]
    body = pages_raw[:-2]
    pages = [[RUNE[c] for c in p if c in RUNE] for p in body]
    stream = [i for pg in pages for i in pg]
    return pages, stream

# ------------------------------------------------------------------ generators
def gen_primes(L, off):
    return np.array(ciphers.prime_stream(L, start=off), dtype=np.int64)

def gen_phi_prime(L, off):          # totient(prime)=prime-1
    return np.array(ciphers.prime_totient_stream(L, start=off), dtype=np.int64)

def gen_totient(L, off):            # totient of consecutive ints
    full = ciphers.totient_stream(L + off, start=2)
    return np.array(full[off:off + L], dtype=np.int64)

def gen_prime_gaps(L, off):
    ps = ciphers._sieve_primes(L + off + 2)
    gaps = [(ps[i + 1] - ps[i]) % N for i in range(len(ps) - 1)]
    return np.array(gaps[off:off + L], dtype=np.int64)

def _fib(seed, L, off):
    a, b = seed
    out = []
    for _ in range(L + off):
        out.append(a % N)
        a, b = b, (a + b)
    return np.array(out[off:off + L], dtype=np.int64)

def make_fib(seed):
    return lambda L, off, s=seed: _fib(s, L, off)

GENERATORS = [
    ("primes", gen_primes),
    ("phi(prime)", gen_phi_prime),
    ("totient(int)", gen_totient),
    ("prime_gaps", gen_prime_gaps),
    ("fib(1,1)", make_fib((1, 1))),
    ("fib(0,1)", make_fib((0, 1))),
    ("fib(1,2)", make_fib((1, 2))),
    ("fib(2,1)", make_fib((2, 1))),
    ("fib(3,5)", make_fib((3, 5))),
    ("fib(2,3)", make_fib((2, 3))),
]

# ------------------------------------------------------------------ scoring
# Incremental letter-quadgram scoring that EXACTLY reproduces score.py over the
# concatenated translit string. Beam guides search; the winning path is re-scored
# with the real SC.score_norm so every reported number is repo-comparable.
def _emit_delta(buf, idx):
    """buf: last<=3 letters (str). idx: rune index. Returns (newbuf, dlp, dcnt)."""
    dlp = 0.0; dcnt = 0
    for ch in TR[idx]:
        if len(buf) >= 3:
            dlp += QD.get(buf[-3:] + ch, FLOOR); dcnt += 1
        buf = (buf + ch)[-3:] if len(buf) >= 3 else buf + ch
    return buf, dlp, dcnt

def real_score(pidx):
    return SC.score_norm(gp.indices_to_translit(pidx))

# ------------------------------------------------------------------ beam decode
def beam_decode(c, st, sign, atbash, W=48, skip_pen=3.0, allow_skip=True):
    """c: ciphertext idx array (len L). st: keystream idx array (len >= L+slack).
    Returns (best_score_norm, best_pidx list). p[i]=(c[i]-sign*st[j])%N."""
    L = len(c)
    cc = ((N - 1) - c) if atbash else c
    stL = len(st)
    # beam: list of dicts {j, buf, lp, cnt, path(list)}
    beams = [{"j": 0, "buf": "", "lp": 0.0, "cnt": 0, "path": []}]
    for i in range(L):
        nxt = []
        for b in beams:
            j = b["j"]
            if j >= stL:
                continue
            # ---- normal transition j -> j+1 (consume st[j] at pos i)
            p = (cc[i] - sign * int(st[j])) % N
            nb, dlp, dcnt = _emit_delta(b["buf"], p)
            nxt.append({"j": j + 1, "buf": nb, "lp": b["lp"] + dlp,
                        "cnt": b["cnt"] + dcnt, "path": b["path"] + [p]})
            # ---- skip transition j -> j+2 at collision-consistent site
            if allow_skip and i + 1 < L and j + 2 < stL:
                # gate: c[i+1]-c[i] == st[j+2]-st[j+1] (mod N) -> st[j+1] skipped
                if (int(cc[i + 1]) - int(cc[i])) % N == (int(st[j + 2]) - int(st[j + 1])) % N:
                    p2 = (cc[i] - sign * int(st[j + 1])) % N  # use st[j+1] here, drop st[j]
                    nb2, dlp2, dcnt2 = _emit_delta(b["buf"], p2)
                    nxt.append({"j": j + 2, "buf": nb2, "lp": b["lp"] + dlp2 - skip_pen,
                                "cnt": b["cnt"] + dcnt2, "path": b["path"] + [p2]})
        # prune to top W by total lp
        nxt.sort(key=lambda x: x["lp"], reverse=True)
        beams = nxt[:W]
        if not beams:
            break
    best = max(beams, key=lambda x: (x["lp"] / x["cnt"]) if x["cnt"] else -99)
    return real_score(best["path"]), best["path"]

# ------------------------------------------------------------------ synthetic
def encrypt_softskip(p, st, p_soft=0.83, seed=0):
    """Encrypt plaintext idx p with keystream st, soft skip-on-collision filter.
    Returns (ct list, n_skips). c[i]=(p[i]+st[j])%N; on collision skip st[j] w.p. p_soft."""
    rng = np.random.default_rng(seed)
    ct = []; j = 0; nsk = 0
    for i in range(len(p)):
        if i > 0:
            trial = (p[i] + int(st[j])) % N
            if trial == ct[-1] and rng.random() < p_soft and j + 1 < len(st):
                j += 1; nsk += 1  # drop st[j], re-encode with next
        ct.append((p[i] + int(st[j])) % N)
        j += 1
    return ct, nsk

def synthetic_validation():
    print("=" * 72)
    print("PHASE A -- SYNTHETIC VALIDATION (plant English, confirm recovery + separation)")
    print("=" * 72)
    sys.path.insert(0, os.path.join(ROOT, "analysis"))
    from run_stats import english_baseline
    eng = english_baseline()[:1600]
    Lsyn = len(eng)
    print(f"  planted plaintext: {Lsyn} runes of English->Gematria")
    print(f"  first 60 translit: {gp.indices_to_translit(eng[:60])}")
    print(f"  clean-English score_norm reference = {real_score(eng):+.3f}")

    true_gen = ("phi(prime)", gen_phi_prime)
    st = true_gen[1](Lsyn + 400, 0)
    ct, nsk = encrypt_softskip(eng, st, p_soft=0.83, seed=11)
    ct = np.array(ct)
    dr = 100 * stats.doublet_rate(ct.tolist())
    print(f"  encrypted with {true_gen[0]} + soft skip filter: {nsk} skips, "
          f"ciphertext doublet%={dr:.3f} (raw English/rigid pad ~3.4%)")

    # rigid decode with CORRECT gen but NO skip awareness (motivates the beam)
    rig = beam_decode(ct, st, sign=+1, atbash=False, allow_skip=False)[0]
    # skip-aware beam with CORRECT gen
    t0 = time.time()
    corr, cpath = beam_decode(ct, st, sign=+1, atbash=False, allow_skip=True)
    match = np.mean(np.array(cpath[:Lsyn]) == np.array(eng[:len(cpath)][:Lsyn])) if cpath else 0
    dt = time.time() - t0
    print(f"  CORRECT gen, rigid (no-skip) beam   score_norm = {rig:+.3f}")
    print(f"  CORRECT gen, SKIP-AWARE beam        score_norm = {corr:+.3f}  "
          f"(plaintext match {100*match:.1f}%, {dt:.1f}s)")
    print(f"    recovered head: {gp.indices_to_translit(cpath[:60])}")

    # WRONG generators (negative controls) -- must stay in noise even WITH skips
    wrongs = []
    for name, fn in [("primes", gen_primes), ("fib(1,1)", make_fib((1, 1))),
                     ("totient(int)", gen_totient), ("fib(3,5)", make_fib((3, 5)))]:
        wst = fn(Lsyn + 400, 0)
        w = beam_decode(ct, wst, sign=+1, atbash=False, allow_skip=True)[0]
        wrongs.append((name, w))
        print(f"  WRONG gen {name:14s} SKIP-AWARE beam  score_norm = {w:+.3f}")
    best_wrong = max(w for _, w in wrongs)
    sep = corr - best_wrong
    print(f"\n  SEPARATION: correct {corr:+.3f}  -  best-wrong {best_wrong:+.3f}  = {sep:.3f}")
    ok = corr > GATE and best_wrong < GATE
    print(f"  VALIDATION {'PASS' if ok else 'WEAK'}: correct>GATE({GATE}) and all wrong<GATE = {ok}")
    return dict(ref=real_score(eng), correct=corr, rigid=rig, best_wrong=best_wrong,
                sep=sep, ok=ok, nsk=nsk, dr=dr, match=float(match))

# ------------------------------------------------------------------ sweeps
def sweep_generators(ct_full, offsets, Lwin, W):
    print("\n" + "=" * 72)
    print(f"PHASE B -- GENERATOR FAMILY sweep on CONTINUOUS stream "
          f"(win={Lwin}, offsets={list(offsets)}, W={W})")
    print("=" * 72)
    ct = np.array(ct_full[:Lwin])
    best = None; hits = []; ntot = 0
    for gname, gfn in GENERATORS:
        gbest = None
        for off in offsets:
            st = gfn(Lwin + 500, off)
            for sign in (+1, -1):
                for atb in (False, True):
                    ntot += 1
                    sc, _ = beam_decode(ct, st, sign, atb, W=W)
                    if gbest is None or sc > gbest[0]:
                        gbest = (sc, off, sign, atb)
                    if best is None or sc > best[0]:
                        best = (sc, gname, off, sign, atb)
                    if sc > GATE:
                        hits.append((sc, gname, off, sign, atb))
        print(f"  {gname:14s} best={gbest[0]:+.3f} "
              f"(off={gbest[1]} sign={gbest[2]:+d} atbash={gbest[3]})")
    print(f"  --- {ntot} configs; GLOBAL best {best[0]:+.3f} via {best[1]} "
          f"off={best[2]} sign={best[3]:+d} atbash={best[4]}")
    return best, hits, ntot

# ------------------------------------------------------------------ keytexts
def load_keytext(path):
    try:
        txt = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return None
    runes = [RUNE[c] for c in txt if c in RUNE]
    if len(runes) >= 300:
        return np.array(runes, dtype=np.int64)
    letters = re.sub(r"[^A-Za-z]", "", txt)
    if len(letters) >= 300:
        try:
            return np.array(gp.keyword_to_indices(letters), dtype=np.int64)
        except Exception:
            return None
    return None

def sweep_keytexts(ct_full, Lwin, W):
    print("\n" + "=" * 72)
    print(f"PHASE C -- CACHED KEYTEXTS as running keys, skip-aware (win={Lwin}, W={W})")
    print("=" * 72)
    paths = []
    paths += sorted(glob.glob(os.path.join(ROOT, "data", "keys", "*.txt")))
    for pat in ("*_key.txt", "*hermes*", "*sephir*", "*rosicrucian*", "*monas*", "*enoch*"):
        paths += glob.glob(os.path.join(ROOT, "analysis", "foundation", pat))
    paths += sorted(glob.glob(os.path.join(ROOT, "analysis", "armada20", "*.txt")))
    paths = sorted(set(paths))
    ct = np.array(ct_full[:Lwin])
    best = None; hits = []; nfiles = 0; ntot = 0
    for path in paths:
        key = load_keytext(path)
        if key is None or len(key) < Lwin + 20:
            continue
        nfiles += 1
        offs = [0]
        if len(key) > Lwin + 400:
            offs = list(range(0, min(401, len(key) - Lwin), 200))
        fbest = None
        for off in offs:
            st = key[off:off + Lwin + 300]
            if len(st) < Lwin + 4:
                continue
            for sign in (+1, -1):
                for atb in (False, True):
                    ntot += 1
                    sc, _ = beam_decode(ct, st, sign, atb, W=W)
                    if fbest is None or sc > fbest[0]:
                        fbest = (sc, off, sign, atb)
                    if best is None or sc > best[0]:
                        best = (sc, os.path.basename(path), off, sign, atb)
                    if sc > GATE:
                        hits.append((sc, os.path.basename(path), off, sign, atb))
        print(f"  {os.path.basename(path):42s} len={len(key):6d} "
              f"best={fbest[0]:+.3f} (off={fbest[1]} sign={fbest[2]:+d} atb={fbest[3]})")
    print(f"  --- {nfiles} usable keytexts, {ntot} configs; "
          f"GLOBAL best {best[0]:+.3f} via {best[1]} off={best[2]} sign={best[3]:+d} atb={best[4]}"
          if best else "  --- no usable keytexts")
    return best, hits, nfiles, ntot

# ------------------------------------------------------------------ per-page
def sweep_pages(pages, W):
    print("\n" + "=" * 72)
    print(f"PHASE D -- PER-PAGE generator beam (offset 0, page-local keys, W={W})")
    print("=" * 72)
    best = None; hits = []; ntot = 0
    for pi, pg in enumerate(pages):
        if len(pg) < 24:
            continue
        ct = np.array(pg)
        pbest = None
        for gname, gfn in GENERATORS:
            st = gfn(len(pg) + 200, 0)
            for sign in (+1, -1):
                for atb in (False, True):
                    ntot += 1
                    sc, _ = beam_decode(ct, st, sign, atb, W=W)
                    if pbest is None or sc > pbest[0]:
                        pbest = (sc, gname, sign, atb)
                    if best is None or sc > best[0]:
                        best = (sc, pi, gname, sign, atb)
                    if sc > GATE:
                        hits.append((sc, pi, gname, sign, atb))
        if pi < 6 or (pbest and pbest[0] > GATE):
            print(f"  page{pi:02d} (len {len(pg):3d}) best={pbest[0]:+.3f} "
                  f"({pbest[1]} sign={pbest[2]:+d} atb={pbest[3]})")
    print(f"  --- {ntot} configs across {len(pages)} pages; "
          f"GLOBAL best {best[0]:+.3f} via page{best[1]} {best[2]}")
    return best, hits, ntot

# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    pages, stream = load_stream()
    print(f"LP2 unsolved: {len(pages)} pages, {len(stream)} runes; "
          f"IoC*N={stats.ioc_norm(stream):.4f} doublet%={100*stats.doublet_rate(stream):.3f} "
          f"as-is score_norm={real_score(stream[:2000]):+.3f}")

    val = synthetic_validation()

    W = 48
    bB, hB, nB = sweep_generators(stream, offsets=range(0, 1001, 100), Lwin=2500, W=W)
    bC, hC, nfC, nC = sweep_keytexts(stream, Lwin=2000, W=W)
    bD, hD, nD = sweep_pages(pages, W=W)

    all_hits = hB + hC + hD
    print("\n" + "=" * 72); print("SUMMARY"); print("=" * 72)
    print(f"  synthetic: correct={val['correct']:+.3f} best_wrong={val['best_wrong']:+.3f} "
          f"sep={val['sep']:.3f} ok={val['ok']}")
    print(f"  PHASE B generators : best {bB[0]:+.3f}  ({nB} configs)")
    print(f"  PHASE C keytexts   : best {bC[0]:+.3f}  ({nC} configs, {nfC} files)" if bC else "  PHASE C: none")
    print(f"  PHASE D per-page   : best {bD[0]:+.3f}  ({nD} configs)")
    grand = max(bB[0], bC[0] if bC else -99, bD[0])
    print(f"  GRAND BEST score_norm over ALL skip-aware decodes = {grand:+.3f}   GATE={GATE}")
    print(f"  configs over GATE: {len(all_hits)}")
    if all_hits:
        print("  !!! HITS !!!")
        for h in sorted(all_hits, reverse=True)[:10]:
            print("   ", h)
    verdict = "BREAK" if all_hits else ("SOUNDNESS-CONFIRMED/NULL-CLOSED" if val["ok"] else "INCONCLUSIVE")
    print(f"  VERDICT: {verdict}   (elapsed {time.time()-t0:.1f}s)")
    return dict(val=val, bB=bB, bC=bC, bD=bD, grand=grand, hits=all_hits,
                nB=nB, nC=nC, nfC=nfC, nD=nD, verdict=verdict)


if __name__ == "__main__":
    main()
