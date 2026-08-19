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

  * decode LP2 pages 0-54 to text scoring in the ENGLISH band (>= -5.5), not merely
    better than noise;
  * do so on MORE THAN ONE PAGE independently — the single most common failure mode is a
    key tuned to one page's statistics;
  * beat a size-matched shuffle null by a stated margin;
  * survive both the rigid and the skip-aware decoder consistently with your stated
    mechanism.

A PASS is not proof. It is the point at which the claim becomes worth a human's time and
should be taken to the CicadaSolvers community for independent reproduction.

A FAIL is much more informative than it feels: it tells you exactly which criterion your
candidate missed and by how much, so you can tell "close" from "not close" — a distinction
that is nearly impossible to make by eye and is where almost every false claim dies.

THE TRUST ANCHOR
----------------
Before judging anything, this script re-derives the five known solved pages through the same
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


SELFTEST_PLAIN = (
    "WELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOTANEASYTRIPBUT"
    "FORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONEALONGTHEWAYYOUWILLFINDANENDTO"
    "ALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURILLUSIONSYOURCERTAINTYANDYOURREALITY"
    "ULTIMATELYYOUWILLDISCOVERANENDTOSELFTHEPRIMESARESACREDTHETOTIENTFUNCTIONIS"
    "SACREDALLTHINGSSHOULDBEENCRYPTEDKNOWTHISSHADOWSTHEJOURNEYISNOTANEASYONEBUT"
    "FORTHOSEWHOSEEKTHETRUTHITISTHEONLYONEWORTHTAKINGSEEKWITHINANDFINDYOURTRUTH")


def selftest():
    """The oracle's OWN plant-and-recover gate.

    An adjudicator that has never been shown to accept a KNOWN-GOOD solution is worth
    nothing — it could reject everything, including the real answer, and look rigorous
    doing it. So: plant a keystream, encipher real English under the repo's pinned
    anti-repeat filter, and require this oracle to PASS the correct key and FAIL a wrong
    one. Both directions must hold.
    """
    print("=" * 74)
    print("ORACLE SELF-TEST — can this adjudicator recognise a KNOWN-GOOD solution?")
    print("=" * 74)

    rnd = random.Random(3301)
    P = sk.eng_to_idx(SELFTEST_PLAIN)
    PGL = 130          # short enough that 415 runes give >= 3 independent pages
    pages = [P[i:i + PGL] for i in range(0, len(P) - PGL + 1, PGL)][:4]
    if len(pages) < 2:
        print("!! self-test plaintext too short to build 2 pages")
        return 2

    K_true = [rnd.randrange(N) for _ in range(4096)]
    C_pages = []
    for pg in pages:
        C, _sk_, _u = sk.encipher_keyskip(pg, K_true, sign=-1, supp=0.83, seed=3301)
        C_pages.append(C)
    dr = (sum(sum(1 for i in range(1, len(c)) if c[i] == c[i - 1]) for c in C_pages)
          / sum(len(c) - 1 for c in C_pages))
    print(f"\nplanted {len(C_pages)} synthetic pages, "
          f"doublet rate {dr:.4f} (real LP2 is 0.0066)")

    K_wrong = [random.Random(4242).randrange(N) for _ in range(4096)]

    results = {}
    for name, K in (("CORRECT key", K_true), ("WRONG key", K_wrong)):
        rows = judge_keystream(K, C_pages, name)
        nmean, nmax = null_band(C_pages[0], K, n=60)
        bar = max(ENGLISH_BAR, nmax + NULL_MARGIN)
        best = max(rows, key=lambda r: r["score"])
        passing = [r for r in rows if r["score"] >= bar]
        ok = best["score"] >= bar and len(passing) >= MIN_PAGES
        results[name] = ok
        print(f"\n{name}:")
        for r in rows:
            print(f"    page {r['page']}  {r['mech']:5s} {r['score']:7.3f}  "
                  f"{r['text'][:52]}")
        print(f"    null max {nmax:.3f}  bar {bar:.3f}  pages passing {len(passing)}"
              f"  -> oracle says {'PASS' if ok else 'FAIL'}")

    good = results["CORRECT key"] is True and results["WRONG key"] is False
    print("\n" + "=" * 74)
    print(f"SELF-TEST: {'PASS' if good else 'FAIL'}")
    print("=" * 74)
    if good:
        print("The oracle accepts a known-good key and rejects a wrong one. Verdicts")
        print("from it are meaningful.")
    else:
        print("The oracle FAILED its own control. Do not trust any verdict it gives:")
        if not results["CORRECT key"]:
            print("  - it rejected a CORRECT key (it would reject the real solution too)")
        if results["WRONG key"]:
            print("  - it accepted a WRONG key (it would accept false solutions)")
    return 0 if good else 2


def main():
    ap = argparse.ArgumentParser(
        description="Adjudicate a candidate solution to Liber Primus LP2 pages 0-54.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true",
                   help="verify the ORACLE ITSELF: plant a known key, require PASS on it "
                        "and FAIL on a wrong one. Run this before trusting any verdict.")
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
    print("LIBER PRIMUS LP2 — SOLUTION ORACLE")
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
    print(f"\n[1] trust anchor (re-derive the five known solved pages)")
    if a.skip_anchor:
        print("    SKIPPED by request. The verdict below is NOT interpretable.")
        anchor_ok = None
    else:
        anchor_ok, tail = trust_anchor()
        print(f"    -> {'PASS' if anchor_ok else 'FAIL'}")
        if not anchor_ok:
            print("    The rig cannot reproduce known solves, so it cannot adjudicate an")
            print("    unknown one. Fix this first. Tail of output:")
            print("    " + tail.replace("\n", "\n    ")[:600])
            return 2

    segments = nc.segments()[:a.pages]
    verdict = {"n": len(UNS), "sha256": h, "anchor": anchor_ok,
               "submitted": "keystream" if a.keystream else
                            "key-module" if a.key_module else "plaintext"}

    # ---- 2. plaintext-only submissions
    if a.plaintext:
        txt = "".join(c for c in open(a.plaintext, encoding="utf-8").read().upper()
                      if c.isalpha())
        sc = nc.eng_norm_text(txt)
        print(f"\n[2] plaintext submission")
        print(f"    length {len(txt):,}   English score {sc:.3f}")
        print(f"    NOTE: a plaintext alone cannot be verified against the ciphertext")
        print(f"    without the key. What this checks is only that your text IS English.")
        print(f"    To be adjudicated as a SOLUTION, submit the key that produces it —")
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
    print(f"\n[2] candidate key: {len(K):,} symbols "
          f"(sha256 {canon_hash(K)[:16]}...)")

    print(f"\n[3] decoding {len(segments)} unsolved pages, both decoders, both signs")
    rows = judge_keystream(K, segments, "candidate")
    for r in rows:
        flag = "  <-- ENGLISH BAND" if r["score"] >= ENGLISH_BAR else ""
        print(f"    page {r['page']:2d}  {r['mech']:5s} sign{r['sign']:+d}  "
              f"{r['score']:7.3f}{flag}")
        print(f"              {r['text'][:72]}")

    print(f"\n[4] size-matched shuffle null (n={NULL_N}) on page 0")
    nmean, nmax = null_band(segments[0], K)
    bar = max(ENGLISH_BAR, nmax + NULL_MARGIN)
    print(f"    null mean {nmean:.3f}   null max {nmax:.3f}   -> bar {bar:.3f}")

    # ---- 4. the pre-committed criteria
    passing = [r for r in rows if r["score"] >= bar]
    strong = [r for r in rows if r["score"] >= STRONG_BAR]
    best = max(rows, key=lambda r: r["score"])

    print(f"\n[5] criteria (all fixed in advance — see PROBLEM.json)")
    c1 = best["score"] >= bar
    c2 = len(passing) >= MIN_PAGES
    c3 = best["score"] > nmax + NULL_MARGIN
    print(f"    (a) best page in the English band (>= {bar:.2f}) "
          f"...... {'PASS' if c1 else 'FAIL'}  [best {best['score']:.3f}]")
    print(f"    (b) at least {MIN_PAGES} pages independently pass "
          f"........ {'PASS' if c2 else 'FAIL'}  [{len(passing)} passing]")
    print(f"    (c) beats the shuffle null by {NULL_MARGIN} "
          f"............. {'PASS' if c3 else 'FAIL'}")
    print(f"    (d) {len(strong)} page(s) reach the strong band (>= {STRONG_BAR})")

    ok = c1 and c2 and c3
    verdict.update(best_score=best["score"], null_mean=nmean, null_max=nmax,
                   bar=bar, pages_passing=len(passing), pages_strong=len(strong),
                   criteria={"english_band": c1, "multi_page": c2, "beats_null": c3},
                   rows=rows, verdict="PASS" if ok else "FAIL")

    print("\n" + "=" * 74)
    if ok:
        print("VERDICT: PASS")
        print("=" * 74)
        print("This candidate clears every pre-committed criterion. That is a genuinely")
        print("rare outcome and it is worth a human's attention.")
        print("\nDo this next, in order:")
        print("  1. Re-run this from a clean checkout, to rule out local contamination.")
        print("  2. Run it over ALL 55 unsolved pages (--pages 55), not just a sample.")
        print("  3. Read the decoded text yourself. Does it read as continuous prose in")
        print("     the voice of the solved pages, or as word-salad that merely scores?")
        print("  4. Take it to CicadaSolvers for independent reproduction. A solve is")
        print("     accepted by the community, not by this script.")
        print("  5. If it holds, you have overturned this repository's central verdict —")
        print("     which would mean the keystream was DERIVED, not a true external pad.")
    else:
        print("VERDICT: FAIL")
        print("=" * 74)
        gap = bar - best["score"]
        print(f"Best page scored {best['score']:.3f} against a bar of {bar:.3f} "
              f"— short by {gap:.3f}.")
        print("\nHow to read that number, because 'close' is the trap here:")
        if gap > 1.5:
            print("  > 1.5 short: this is NOISE, not a near miss. The decode is")
            print("  indistinguishable from a random key. Do not tune it; the")
            print("  hypothesis is wrong, not the parameters.")
        elif gap > 0.5:
            print("  0.5-1.5 short: still the noise band. Sweeps of millions of wrong")
            print("  keys routinely produce scores here — it is the best-of-N order")
            print("  statistic, not a signal. Genuine solved pages land at -4.1 to -5.0.")
        else:
            print("  < 0.5 short: worth a second look, but be careful — this is exactly")
            print("  where large sweeps generate false positives. Re-run on MORE pages;")
            print("  a real key improves with more text, a lucky one degrades.")
        print("\nBefore concluding anything, prove your instrument works at all:")
        print("  python3 -m pytest benchmark/ -q")
        print("  A null from an instrument that cannot recover a PLANTED signal is not")
        print("  a negative result. That mistake invalidated years of work here.")

    if a.json:
        json.dump(verdict, open(a.json, "w"), indent=1, default=str)
        print(f"\nwrote {a.json}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
