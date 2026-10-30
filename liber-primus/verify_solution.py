#!/usr/bin/env python3
"""THE ORACLE — submit a candidate solution to Liber Primus LP2 and get a verdict.

    ┌──────────────────────────────────────────────────────────────────────────┐
    │  If you are a model or a researcher who thinks you have solved LP2,      │
    │  THIS is the file to run. You do not need to understand anything else    │
    │  in this repository to use it.                                           │
    └──────────────────────────────────────────────────────────────────────────┘

WHY THIS EXISTS
---------------
"I solved Liber Primus" has been claimed many times and has never once been true. The
claims are not usually dishonest — they are usually a person or a model looking at a
partially-English-looking decode and believing it. A cipher this flat produces
English-looking fragments by chance constantly, and human/model pattern-matching is not
calibrated for a 12,956-symbol search over millions of candidate keys.

So this repository refuses to adjudicate solutions by eye. It adjudicates them by a
pre-committed, mechanical test that was written down BEFORE any candidate existed, and
that the five ALREADY-SOLVED pages must pass and random keys must fail.

HOW TO SUBMIT
-------------
Three ways, in increasing order of how much we can check for you:

  1. A keystream — the mod-29 symbols you claim were combined with the plaintext:
         python3 verify_solution.py --keystream mykeys.txt
     (whitespace/comma separated integers 0-28, at least 12,956 of them)

  2. A generator module — a .py exposing `keystream(n) -> list[int]`:
         python3 verify_solution.py --key-module mykey.py
     This is the best form: it is reproducible, and it records HOW the key was made.

  3. A plaintext — if you claim to know the message but not the key:
         python3 verify_solution.py --plaintext myplain.txt

WHAT "PASS" MEANS
-----------------
A PASS here is a strong claim and the bar is deliberately high. Your candidate must:

  * decode LP2 pages under the register-aware beam (beam_v3, design panel_max) with the
    key advancing by 1 (keyskip1), by 2 (keyskip2) or freely (free), and score each
    decode by the PANEL MAX (pmax) over the 12-register panel-R36 (English, Latin, Old
    English, German, Welsh, vowel-dropped/half-vowel English, Greek, Hebrew, Norse, ...);
  * clear the observed-null bar `bars_v3.bar_v3(N=1, L, relation, family="lp2")` for a
    single submitted key (alpha 0.01) on MORE THAN ONE PAGE under the same relation —
    the single most common failure mode is a key tuned to one page's statistics.

A PASS is a FLAG, not proof: "flagged-for-oracle". A human must read two independent pages
as language before the ledger moves (HUMAN-ORACLE.md). The PASS prints the bundle skeleton.

A FAIL is negative under these registers and these three relations ONLY (the L7 caveat);
it does not rule out a construction or language outside the panel. The old English-only
-5.5 score is still printed, labelled LEGACY, as an informational line.

THE TRUST ANCHOR
----------------
Before judging anything, this script re-derives the five known-decoded pages through the same
rig. If that fails, the rig is broken and no verdict from it means anything, so the oracle
refuses to run. That check is why a PASS here is worth something.
"""
import argparse, hashlib, importlib.util, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, os.path.join(HERE, "analysis", "round11"))
sys.path.insert(0, os.path.join(HERE, "analysis", "campaign18_skip"))

import lib_numchannel as nc
import skipdecode as sk
from lp import gematria as gp

N = 29

# ---- the problem, pinned. If these do not match, you are not solving the same problem.
EXPECT_N = 12956
EXPECT_SHA256 = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"

# ---- the acceptance criteria, fixed in advance (see PROBLEM.json)
ENGLISH_BAR = -5.5        # the repo's long-standing confirm threshold
STRONG_BAR = -4.6         # where genuine solved pages actually land
MIN_PAGES = 2             # must work on more than one page independently
NULL_N = 200
NULL_MARGIN = 0.5         # must beat the shuffle null's max by this


def canon_hash(idxs):
    return hashlib.sha256(",".join(map(str, idxs)).encode()).hexdigest()


def trust_anchor():
    """Re-derive the known solves. No verdict is issued if this fails."""
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "tests", "validate.py")],
                       capture_output=True, text=True, timeout=1800)
    ok = "ALL VALIDATIONS PASSED" in (r.stdout + r.stderr)
    return ok, (r.stdout or "")[-800:]


def load_keystream_file(path):
    txt = open(path, encoding="utf-8").read().replace(",", " ")
    vals = [int(t) for t in txt.split() if t.lstrip("-").isdigit()]
    bad = [v for v in vals if not 0 <= v < N]
    if bad:
        raise SystemExit(f"keystream contains {len(bad)} values outside 0..28 "
                         f"(first: {bad[0]}). Reduce mod 29 before submitting.")
    return vals


def load_key_module(path):
    spec = importlib.util.spec_from_file_location("candidate_key", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "keystream"):
        raise SystemExit(f"{path} must expose `keystream(n) -> list[int]` "
                         f"(values 0..28).")
    ks = list(mod.keystream(EXPECT_N + 512))
    bad = [v for v in ks if not 0 <= v < N]
    if bad:
        raise SystemExit(f"keystream() returned {len(bad)} values outside 0..28.")
    return ks


def null_band(seg, K, n=NULL_N, seed0=3301):
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(seg)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, K, sign=-1, o=0, beam_w=400,
                                   max_skip=3)["score"])
    return sum(vals) / len(vals), max(vals)


def judge_keystream(K, segments, label):
    """Decode each unsolved page under the candidate key, both decoders."""
    rows = []
    for i, seg in enumerate(segments):
        best = None
        for mech, fn in (("rigid", sk.rigid_decode), ("beam", sk.beam_decode)):
            for sign in (-1, 1):
                kw = {} if mech == "rigid" else {"beam_w": 400, "max_skip": 3}
                try:
                    d = fn(seg, K, sign=sign, o=0, **kw)
                except TypeError:
                    d = fn(seg, K, sign=sign, **kw)
                cand = {"page": i, "mech": mech, "sign": sign,
                        "score": d["score"], "text": d["translit"][:120]}
                if best is None or cand["score"] > best["score"]:
                    best = cand
        rows.append(best)
    return rows


# ======================================================================================
# Register-aware adjudication (Round 36 audit item 1). Replaces the English-only -5.5 band.
# ======================================================================================
PANEL_R36_PATH = os.path.join(HERE, "analysis", "round36", "P1-panel-r36", "build1", "panel12.npz")
PANEL_R36_TEST = os.path.join(HERE, "analysis", "round36", "P1-panel-r36", "build1", "testhalves12.npz")
PANEL_R36_SHA = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
# Committed fixture of the same bytes (data/panels/, Round 36 P1 build1) so a fresh clone and CI can run
# the self-test without rebuilding the panel; the build dir is preferred when present.
_FIX_P = os.path.join(HERE, "data", "panels", "panel-r36.npz")
_FIX_T = os.path.join(HERE, "data", "panels", "testhalves-r36.npz")
if not os.path.exists(PANEL_R36_PATH) and os.path.exists(_FIX_P):
    PANEL_R36_PATH, PANEL_R36_TEST = _FIX_P, _FIX_T
RELATIONS = ("keyskip1", "keyskip2", "free")
ADV = {"keyskip1": 1, "keyskip2": 2, "free": "free"}
MAX_LEN = 240            # decode at most this many runes of a page (bars are fitted L<=400; RAM)
FREE_L = 120             # `free` has an observed null at L=120 ONLY
ALPHA = 0.01
BAR_N = 1                # one submitted key
SELFTEST_REGS = ("EN_MODERN", "LATIN", "EN_NOVOWEL", "GREEK")
SELFTEST_L = 120

_V = None                # beam_v3 module
_BARS = None
_PAN = None
_PANEL_INFO = {}


def _sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def load_instruments(quiet=False):
    """Import beam_v3 / bars_v3 and install the panel (panel-R36, else the 9-register fallback)."""
    global _V, _BARS, _PAN
    if _PAN is not None:
        return _V, _BARS, _PAN
    sys.path.insert(0, os.path.join(HERE, "analysis", "round34", "I1-v3-null"))
    sys.path.insert(0, os.path.join(HERE, "analysis", "round33", "I1-register-aware-beam"))
    import beam_v3 as V
    import bars_v3 as BR
    A = V.A
    if os.path.exists(PANEL_R36_PATH):
        sha = _sha_file(PANEL_R36_PATH)
        pan = A.Panel(PANEL_R36_PATH)
        _PANEL_INFO.update(name="panel-R36", path=PANEL_R36_PATH, sha256=sha, registers=pan.registers,
                           sha_ok=(sha == PANEL_R36_SHA))
        if not quiet:
            print(f"    panel: panel-R36, {pan.R} registers, sha256 {sha[:8]}...")
            if sha != PANEL_R36_SHA:
                print(f"    !! WARNING: panel sha {sha[:8]}... differs from the recorded {PANEL_R36_SHA[:8]}...")
    else:
        pan = A.Panel(V.PANEL_PATH)
        _PANEL_INFO.update(name="round32-nine-register", path=V.PANEL_PATH, sha256=_sha_file(V.PANEL_PATH),
                           registers=pan.registers, sha_ok=False)
        if not quiet:
            print(f"    !! WARNING: panel-R36 not found at {PANEL_R36_PATH}.")
            print(f"       FALLING BACK to the Round 32 nine-register panel ({pan.R} registers). Greek/Hebrew/Norse")
            print(f"       are NOT covered and the bars were fitted for a different panel: treat the verdict as weaker.")
    V._PAN = pan
    V._WCACHE.clear()
    _V, _BARS, _PAN = V, BR, pan
    return _V, _BARS, _PAN


def panel_available():
    r32 = os.path.join(HERE, "analysis", "round32", "I2-multiregister-readjudication", "models", "panel.npz")
    return os.path.exists(PANEL_R36_PATH) or os.path.exists(r32)


def plan_page(seg, relation):
    """Runes actually decoded for a page under a relation (None if the relation has no bar here)."""
    s = list(seg)[:MAX_LEN]
    if relation == "free":
        if len(s) < FREE_L:
            return None
        return s[:FREE_L]
    return s


def page_bar(L, relation):
    _, BR, _ = load_instruments(quiet=True)
    return float(BR.bar_v3(BAR_N, L, relation, alpha=ALPHA, family="lp2"))


def judge_register(K, pages, relations=RELATIONS, o=0, sign=-1, beam_w=400):
    """Decode every page under every relation with beam_v3 panel_max; adjudicate with the panel.

    Adjudicated directly (adjudicate.adjudicate), NOT through the 9-wide SWEEPROW row writer.
    """
    V, _, pan = load_instruments(quiet=True)
    A = V.A
    rows = []
    for i, seg in enumerate(pages):
        for rel in relations:
            c = plan_page(seg, rel)
            if c is None:
                rows.append({"page": i, "relation": rel, "L": len(seg), "pmax": None, "preg": None,
                             "bar": None, "margin": None, "clears": False, "plain_idx": None,
                             "translit": "", "z": None, "note": f"free needs >= {FREE_L} runes"})
                continue
            r = V.beam_decode_v3(c, K, ADV[rel], design="panel_max", sign=sign, o=o, beam_w=beam_w)
            res = A.adjudicate(r["plain_idx"], pan=pan)
            bar = page_bar(len(c), rel)
            pm = float(res["pmax"])
            rows.append({"page": i, "relation": rel, "L": len(c), "pmax": pm,
                         "preg": pan.registers[int(res["preg"])], "bar": bar, "margin": pm - bar,
                         "clears": pm >= bar, "plain_idx": [int(v) for v in r["plain_idx"]],
                         "translit": A.idx_to_trans(r["plain_idx"]),
                         "z": {pan.registers[j]: float(v) for j, v in enumerate(res["z"])},
                         "n_skips": r.get("n_skips")})
    return rows


def decide(rows):
    """PASS iff, under ONE relation, at least MIN_PAGES distinct pages clear that relation's bar."""
    per = {}
    for rel in RELATIONS:
        rr = [r for r in rows if r["relation"] == rel and r["pmax"] is not None]
        clearing = [r for r in rr if r["clears"]]
        per[rel] = {"tested": len(rr), "clearing": len(clearing),
                    "best": max(rr, key=lambda r: r["margin"]) if rr else None}
    ok_rels = [rel for rel in RELATIONS if per[rel]["clearing"] >= MIN_PAGES]
    best_rel = max(ok_rels, key=lambda r: per[r]["clearing"]) if ok_rels else None
    return (best_rel is not None), best_rel, per


def legacy_line(K, segments):
    """INFORMATIONAL ONLY: the old English-only -5.5 score (rigid + legacy beam)."""
    rows = judge_keystream(K, segments, "legacy")
    best = max(rows, key=lambda r: r["score"])
    return best["score"], best["page"], (best["score"] >= ENGLISH_BAR)


def print_rows(rows):
    for r in rows:
        if r["pmax"] is None:
            print(f"    page {r['page']:2d}  {r['relation']:8s}  (not tested: {r['note']})")
            continue
        flag = "  <-- clears bar" if r["clears"] else ""
        print(f"    page {r['page']:2d}  {r['relation']:8s} L={r['L']:3d}  pmax {r['pmax']:7.2f} "
              f"[{r['preg']}]  bar {r['bar']:6.2f}{flag}")


# ---- self-test: plant a correct key in four registers, require recovery -------------------
def _encipher(P, K, seed=3301):
    load_instruments(quiet=True)
    return _V.B2.encipher_keyskip1(P, K, supp=0.83, seed=seed)


def _plant_pages(reg, L=SELFTEST_L, npages=2):
    import numpy as np
    p = PANEL_R36_TEST if os.path.exists(PANEL_R36_TEST) else os.path.join(
        HERE, "analysis", "round32", "I2-multiregister-readjudication", "models", "testhalves.npz")
    t = np.load(p)
    if reg not in t.files:
        raise SystemExit(f"self-test register {reg} missing from the held-out text store {p}")
    x = [int(v) for v in t[reg]]
    base = 7000
    return [x[base + 3 * L * j: base + 3 * L * j + L] for j in range(npages)]


def selftest(regs=SELFTEST_REGS):
    """The oracle's OWN plant-and-recover gate, across registers.

    Plants a correct key in held-out text of EN_MODERN, LATIN, EN_NOVOWEL and GREEK under the
    keyskip1 enciphering (L=120, 2 pages each) and requires: the CORRECT key PASSes, a WRONG
    key FAILs. An adjudicator that cannot recover a planted non-English key is the Round 18
    L7-A defect, so all four registers must recover.
    """
    print("=" * 74)
    print("ORACLE SELF-TEST — can this adjudicator recognise a KNOWN-GOOD key, in any register?")
    print("=" * 74)
    if not panel_available():
        print("SELF-TEST: UNAVAILABLE - no register panel is built in this checkout (the panel .npz files are")
        print("gitignored build artefacts). Rebuild panel-R36 per analysis/round36/P1-panel-r36/RESULTS.md.")
        print("No verdict can be issued without it; this is NOT a pass.")
        return 3
    load_instruments()
    rnd = random.Random(3301)
    out = {}
    all_ok = True
    for n_reg, reg in enumerate(regs):
        plain = _plant_pages(reg)
        K_true = [rnd.randrange(N) for _ in range(4096)]
        K_wrong = [random.Random(4242 + n_reg).randrange(N) for _ in range(4096)]
        C_pages = [_encipher(pg, K_true, seed=3301 + j)[0] for j, pg in enumerate(plain)]
        res = {}
        for name, K in (("CORRECT", K_true), ("WRONG", K_wrong)):
            rows = judge_register(K, C_pages, relations=("keyskip1",))
            ok, rel, per = decide(rows)
            res[name] = "PASS" if ok else "FAIL"
            pm = ", ".join(f"{r['pmax']:.1f}/{r['bar']:.1f}" for r in rows)
            print(f"  {reg:11s} {name:7s} key: pmax/bar per page = {pm}  argmax {rows[0]['preg']:10s} -> "
                  f"{res[name]}")
        good = res["CORRECT"] == "PASS" and res["WRONG"] == "FAIL"
        out[reg] = {"recovered": res["CORRECT"] == "PASS", "wrong_rejected": res["WRONG"] == "FAIL",
                    "ok": good}
        all_ok &= good
    print("\n" + "=" * 74)
    print(f"SELF-TEST: {'PASS' if all_ok else 'FAIL'}   "
          + "  ".join(f"{k}={'ok' if v['ok'] else 'BAD'}" for k, v in out.items()))
    print("=" * 74)
    if all_ok:
        print("The oracle recovers a planted key in every tested register and rejects wrong keys.")
        print("(Plants use keyskip1; keyskip2/free decoding is not recovery-gated here.)")
    else:
        print("The oracle FAILED its own control. Do not trust any verdict it gives:")
        for k, v in out.items():
            if not v["recovered"]:
                print(f"  - it rejected a CORRECT key planted in {k} (L7-A: it would reject the real one)")
            if not v["wrong_rejected"]:
                print(f"  - it accepted a WRONG key against {k} text")
    return 0 if all_ok else 2


def print_bundle(rows, rel, src, K_sha, panel_info):
    """HUMAN-ORACLE.md section 1 bundle skeleton, for the PASS case."""
    print("\n" + "-" * 74)
    print("HUMAN-ORACLE BUNDLE SKELETON (complete per HUMAN-ORACLE.md section 1)")
    print("-" * 74)
    print(f"  provenance : submitted via --{src}")
    print(f"  key sha256 : {K_sha}   (seed / generator / parameters: YOU must add)")
    print(f"  relation   : {rel} (advance {ADV[rel]!r}); sign -1; key offset o=0 (key restarts at each page)")
    print(f"  panel      : {panel_info['name']} sha256 {panel_info['sha256']}")
    print(f"  bar        : bars_v3.bar_v3(N={BAR_N}, L, {rel!r}, alpha={ALPHA}, family='lp2')")
    for r in [r for r in rows if r["relation"] == rel and r["clears"]]:
        print(f"\n  page {r['page']}  L={r['L']}  pmax {r['pmax']:.2f}  bar {r['bar']:.2f}  "
              f"argmax register {r['preg']}")
        print("    panel argmax trace (per-register z): " +
              ", ".join(f"{k}={v:.1f}" for k, v in r["z"].items()))
        print(f"    decoded rune indices: {' '.join(map(str, r['plain_idx']))}")
        print(f"    decoded text        : {r['translit']}")
    print("\n  Still to add by hand: observed-null max for this decoder, planted-control recovery,")
    print("  the language-agnostic row (IoC, mds, pmax_ne, zl), the code commit hash, a `reproduce:` line.")


def main():
    ap = argparse.ArgumentParser(
        description="Adjudicate a candidate solution to Liber Primus LP2 pages 0-54.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true",
                   help="verify the ORACLE ITSELF: plant a known key in four registers (EN_MODERN, "
                        "LATIN, EN_NOVOWEL, GREEK), require PASS on it and FAIL on a wrong one. "
                        "Run this before trusting any verdict.")
    g.add_argument("--keystream", help="file of >=12,956 integers 0-28")
    g.add_argument("--key-module", help=".py exposing keystream(n) -> list[int]")
    g.add_argument("--plaintext", help="file with your claimed plaintext")
    ap.add_argument("--pages", type=int, default=6,
                    help="how many unsolved pages to test (default 6)")
    ap.add_argument("--json", help="write the full verdict here")
    ap.add_argument("--skip-anchor", action="store_true",
                    help="skip the trust anchor (NOT recommended; the verdict is "
                         "uninterpretable without it)")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    print("=" * 74)
    print("LIBER PRIMUS LP2 — SOLUTION ORACLE (register-aware)")
    print("=" * 74)

    # ---- 0. the problem must be the one we think it is
    UNS = nc.unsolved()
    h = canon_hash(UNS)
    print(f"\n[0] problem identity")
    print(f"    runes            : {len(UNS):,}  (expected {EXPECT_N:,})")
    print(f"    sha256(indices)  : {h}")
    if len(UNS) != EXPECT_N or h != EXPECT_SHA256:
        print(f"    !! MISMATCH — expected {EXPECT_SHA256}")
        print("    Your checkout's ciphertext differs from the canonical one. Every")
        print("    number in this repository is computed on the canonical stream;")
        print("    reconcile before comparing anything.")
        return 2
    print(f"    -> canonical. This is the same problem the repo's results describe.")

    # ---- 1. trust anchor
    print(f"\n[1] trust anchor (re-derive the five known-decoded pages)")
    if a.skip_anchor:
        print("    SKIPPED by request. The verdict below is NOT interpretable.")
        anchor_ok = None
    else:
        anchor_ok, tail = trust_anchor()
        print(f"    -> {'PASS' if anchor_ok else 'FAIL'}")
        if not anchor_ok:
            print("    The rig cannot reproduce known decodes, so it cannot adjudicate an")
            print("    unknown one. Fix this first. Tail of output:")
            print("    " + tail.replace("\n", "\n    ")[:600])
            return 2

    segments = nc.segments()[:a.pages]
    src = ("keystream" if a.keystream else "key-module" if a.key_module else "plaintext")
    verdict = {"n": len(UNS), "sha256": h, "anchor": anchor_ok, "submitted": src}

    # ---- 2. plaintext-only submissions
    if a.plaintext:
        txt = "".join(c for c in open(a.plaintext, encoding="utf-8").read().upper()
                      if c.isalpha())
        sc = nc.eng_norm_text(txt)
        print(f"\n[2] plaintext submission")
        print(f"    length {len(txt):,}   English score {sc:.3f}   (LEGACY English-only score)")
        print(f"    NOTE: a plaintext alone cannot be verified against the ciphertext")
        print(f"    without the key. What this checks is only that your text IS English.")
        print(f"    To be adjudicated, submit the key that produces it —")
        print(f"    a plaintext with no key is unfalsifiable, and that is precisely why")
        print(f"    every historical 'solve' of this kind was never accepted.")
        verdict.update(plaintext_score=sc, verdict="NOT-ADJUDICABLE")
        print(f"\nVERDICT: NOT-ADJUDICABLE (submit a key)")
        if a.json:
            json.dump(verdict, open(a.json, "w"), indent=1)
        return 1

    # ---- 3. key submissions
    K = (load_keystream_file(a.keystream) if a.keystream
         else load_key_module(a.key_module))
    if len(K) < EXPECT_N:
        print(f"\n!! keystream is {len(K):,} symbols; LP2 0-54 needs {EXPECT_N:,}.")
        return 2
    K_sha = canon_hash(K)
    print(f"\n[2] candidate key: {len(K):,} symbols (sha256 {K_sha[:16]}...)")

    print(f"\n[3] instruments")
    if not panel_available():
        print("    !! no register panel is built in this checkout (gitignored .npz). Cannot adjudicate;")
        print("    rebuild panel-R36 per analysis/round36/P1-panel-r36/RESULTS.md. NOT a FAIL, NOT a PASS.")
        return 3
    load_instruments()
    pinfo = dict(_PANEL_INFO)

    print(f"\n[4] decoding {len(segments)} pages (first <= {MAX_LEN} runes each) under keyskip1, keyskip2 and free")
    print(f"    beam_v3 panel_max, sign -1, key offset 0 per page; score = panel pmax")
    print(f"    (free is decoded on the first {FREE_L} runes only: it has an observed null at L={FREE_L} only)")
    rows = judge_register(K, segments)
    print_rows(rows)

    print(f"\n[5] bar: bars_v3.bar_v3(N={BAR_N}, L, relation, alpha={ALPHA}, family='lp2')")
    print(f"    N={BAR_N}: this is the bar for ONE submitted key fixed in advance. If you swept many keys,")
    print(f"    the bar for your sweep's N is higher; this oracle does not know your N.")
    print(f"    Three relations are tried, so the family-wise alpha is up to ~{3 * ALPHA:.2f}.")
    print(f"    CAVEAT: `free` has no observed bar above L={FREE_L}; it is decoded at L={FREE_L} only.")

    ok, rel, per = decide(rows)
    print(f"\n[6] criteria (pre-committed; see PROBLEM.json)")
    for r_ in RELATIONS:
        p = per[r_]
        b = p["best"]
        extra = (f"best margin {b['margin']:+.2f} on page {b['page']} (argmax {b['preg']})"
                 if b else "no page eligible")
        print(f"    {r_:8s}: {p['clearing']}/{p['tested']} pages clear the bar (need >= {MIN_PAGES})  {extra}")

    ls, lp_, lin = legacy_line(K, segments)
    print(f"\n    LEGACY (informational only, English-only band, NOT used in the verdict): "
          f"best rigid/beam score {ls:.3f} on page {lp_}"
          f"{'  (>= -5.5)' if lin else '  (< -5.5)'}")

    verdict.update(panel=pinfo.get("name"), panel_sha256=pinfo.get("sha256"), bar_N=BAR_N, alpha=ALPHA,
                   relations=list(RELATIONS),
                   per_relation={k: {"tested": v["tested"], "clearing": v["clearing"]} for k, v in per.items()},
                   legacy_best=ls, rows=[{k: v for k, v in r.items() if k != "plain_idx"} for r in rows],
                   verdict="PASS" if ok else "FAIL", passing_relation=rel)

    print("\n" + "=" * 74)
    if ok:
        print("VERDICT: PASS  (flagged-for-oracle)")
        print("=" * 74)
        print(f"Under relation '{rel}', {per[rel]['clearing']} pages clear the panel-max bar at N={BAR_N}.")
        print("flagged-for-oracle: a human must read two independent pages before the ledger moves.")
        print("A PASS here is a reproduction gate, not a claim. Next, in order: re-run from a clean")
        print("checkout; run all 55 pages (--pages 55); read the decoded text as language (any panel")
        print("register counts); then follow HUMAN-ORACLE.md (bundle, issue, adjudicator).")
        print_bundle(rows, rel, src, K_sha, pinfo)
        verdict["bundle_pages"] = [{"page": r["page"], "L": r["L"], "pmax": r["pmax"], "argmax": r["preg"],
                                    "plain_idx": r["plain_idx"], "translit": r["translit"], "z": r["z"]}
                                   for r in rows if r["relation"] == rel and r["clears"]]
    else:
        print("VERDICT: FAIL")
        print("=" * 74)
        best = max((p["best"] for p in per.values() if p["best"]), key=lambda b: b["margin"], default=None)
        if best:
            print(f"Closest: relation {best['relation']}, page {best['page']}, pmax {best['pmax']:.2f} "
                  f"[{best['preg']}] vs bar {best['bar']:.2f} (margin {best['margin']:+.2f}); "
                  f"a PASS needs >= {MIN_PAGES} pages clearing the bar under ONE relation.")
        print("\nThis FAIL was tested under exactly three conditionals:")
        print(f"  1. relation in {{keyskip1, keyskip2, free}} (key advance 1 / 2 / free; free at L={FREE_L} only)")
        print(f"  2. registers = the {len(pinfo['registers'])}-register panel: {', '.join(pinfo['registers'])}")
        print(f"  3. the key applied as given, restarting at each page (o=0), sign -1, one key (N={BAR_N})")
        print("L7 caveat: NEGATIVE UNDER THESE REGISTERS/RELATIONS ONLY. A plaintext in a language or")
        print("construction outside the panel, a different key offset/sign, or a key needing a")
        print("different rejection rule is NOT detected, and 'close' is the trap: do not tune to the bar.")
        print("Before reading anything into it, prove the instrument can recover a plant:")
        print("  python3 verify_solution.py --selftest")

    if a.json:
        json.dump(verdict, open(a.json, "w"), indent=1, default=str)
        print(f"\nwrote {a.json}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
