"""C8 checker: a scorer that sees a plaintext register the panel cannot (CHALLENGES.md, C8).

    python challenges/c8_register_scorer.py --self-test                          # English + panel baselines
    python challenges/c8_register_scorer.py my_scorer.py --heldout my_text.json  # your scorer, fresh seed
    python challenges/c8_register_scorer.py my_scorer.py --heldout X --seed <maintainer seed>   # the scored run

Your file defines   REGISTER = "<name>"   and   score(idx: list[int]) -> float   (rune indices 0-28, higher =
more like your register). It runs in an isolated child process (challenges/_sandbox.py, R47-H2): it gets one
window per call, positives and every null class mixed in a random order, and returns only the float. --heldout is text in that register that your scorer was NOT trained on, as:
  a C7 manifest (.json)        transliterated with its declared table (see c7_corpus_forge.py), or
  a rune file                  any file whose letters are runes (other characters ignored), or
  a Latin-alphabet text        folded to A-Z and read with the repo's GP greedy mapping (fine for Romance
                               and Germanic languages; use a C7 table for anything else).

Every negative in this repository is an English-register negative unless it was re-adjudicated (ledger
L7-A-SCORER-ENGLISH-ONLY). Panel-R36 sees 12 registers: EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY
EN_HALFVOWEL EN_NOVOWEL GREEK HEBREW NORSE. This challenge asks for a 13th, measured the same way the
repo's instruments are:

  positives  held-out windows of L runes, PLANTED with the repo's standard plant (keyskip encipher under a
             fresh SHA-256-counter key, supp reproducing LP2's doublet rate) and DECODED with the correct key
             by the C3 reference beam. The decode is what gets scored. (--direct skips the plant; iteration only.)
  nulls      (u) uniform random runes   (r) real LP2 windows   (s) the positive windows shuffled
             (w) beam decodes of real LP2 windows under a wrong SHA-256 key (what a sweep actually emits)

The threshold is the highest of the four classes' (1 - FPR) quantiles, so FPR <= 0.01 holds against EVERY
null class. Power is the fraction of positives above it. L = 236 is LP2's mean page (12,956 / 55).

Finish line: power >= 0.80 at FPR 0.01 at L = 236 against every null class, REGISTER not one of the 12, re-run
by the maintainers on their own held-out text of that register at a seed chosen at review. The incumbent
(panel-R36 pmax) is scored on the same windows: if it already reaches 0.80, the result is filed as "already
seen by panel-R36" (still a measured row), not as an extension of the panel.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402
import _common as C  # noqa: E402
import skipdecode as sk  # noqa: E402

LENGTHS = (236, 120, 60)
HEADLINE_L = 236
FPR, FINISH = 0.01, 0.80
CLASSES = ("u", "r", "s", "w")
CLASS_NAME = {"u": "uniform", "r": "real LP2", "s": "shuffled pos", "w": "beam wrong-key"}


def load_heldout(path):
    if path.endswith(".json"):
        import c7_corpus_forge as C7
        errs = []
        M = C7.load_manifest(path, errs)
        src = C7.read_source(M, os.path.dirname(os.path.abspath(path)), errs)
        if src is None:
            raise SystemExit("held-out manifest: " + "; ".join(errs))
        sents, _, _ = C7.derive(src, M, errs)
        return [x for s in sents for w in s for x in w], "C7 manifest"
    t = open(H.repo_path(path), encoding="utf-8", errors="replace").read()
    r = [H.RUNE_IDX[c] for c in t if c in H.RUNE_IDX]
    if len(r) > 1000:
        return r, "rune file"
    return H.latin_text_to_idx(path), "Latin alphabet (GP greedy fold)"


def positives(stream, L, n, rng, direct):
    out = []
    for _ in range(n):
        a = rng.randrange(0, len(stream) - L)
        P = stream[a:a + L]
        if direct:
            out.append(P)
            continue
        K = H.rand_key(rng, 5 * L + 64)
        Cx, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=H.EXACT_SUPP, seed=rng.getrandbits(32))
        out.append(sk.beam_decode(Cx, K, sign=-1, o=0, beam_w=400, max_skip=3)["plain_idx"])
    return out


def nulls(pos, L, rng, n_cheap, n_beam, lp2):
    out = {"u": [[rng.randrange(H.N) for _ in range(L)] for _ in range(n_cheap)]}
    r = []
    for _ in range(n_cheap):
        a = rng.randrange(0, len(lp2) - L)
        r.append(lp2[a:a + L])
    out["r"] = r
    out["s"] = [rng.sample(pos[i % len(pos)], L) for i in range(n_cheap)]
    w = []
    for _ in range(n_beam):
        a = rng.randrange(0, len(lp2) - L)
        w.append(sk.beam_decode(lp2[a:a + L], H.rand_key(rng, 5 * L + 64), sign=-1, o=0, beam_w=400,
                                max_skip=3)["plain_idx"])
    out["w"] = w
    return out


def build(stream, seed, n_pos, n_cheap, n_beam, direct, lengths=LENGTHS):
    lp2 = H.lp2_stream()
    sets = {}
    for L in lengths:
        rng = random.Random(f"{seed}|c8|{L}")
        pos = positives(stream, L, n_pos, rng, direct)
        sets[L] = (pos, nulls(pos, L, rng, n_cheap, n_beam, lp2))
    return sets


def evaluate(score, sets, many=None):
    """score(idx) -> float in-process (the repo's own scorers), or many(list of windows) -> list of floats
    (a submission in the isolated child, _sandbox.Sandbox.map: every window of every class in one call list,
    shuffled, so call order carries no label)."""
    many = many or (lambda xs: [score(list(x)) for x in xs])
    res = {}
    for L, (pos, neg) in sets.items():
        allw = [list(x) for x in pos] + [list(x) for c in CLASSES for x in neg[c]]
        sc = many(allw)
        sp, i = sc[:len(pos)], len(pos)
        per, thr = {}, None
        for c in CLASSES:
            sn = sc[i:i + len(neg[c])]
            i += len(neg[c])
            pw, t = H.power(sp, sn, FPR)
            per[c] = round(pw, 3)
            thr = t if thr is None else max(thr, t)
        k = sum(1 for s in sp if s > thr)
        res[L] = {"power": k / len(sp), "k": k, "n": len(sp), "wilson": H.wilson(k, len(sp)),
                  "per_class": per, "threshold": thr}
    return res


def show(name, res):
    print(f"\n{name}")
    print(f"  {'L':>4} {'power(all)':>10} {'Wilson 95%':>15}   " + "  ".join(f"{CLASS_NAME[c]:>14}" for c in CLASSES))
    for L, r in res.items():
        print(f"  {L:>4} {r['power']:10.3f} {str(r['wilson']):>15}   "
              + "  ".join(f"{r['per_class'][c]:14.3f}" for c in CLASSES))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining REGISTER and score(idx) -> float")
    ap.add_argument("--heldout", action="append", help="held-out text in the register (repeatable)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--pos", type=int, default=200, help="positive windows per length")
    ap.add_argument("--null", type=int, default=2000, help="windows per cheap null class (u, r, s)")
    ap.add_argument("--beam-null", type=int, default=500, help="beam wrong-key null decodes per length")
    ap.add_argument("--direct", action="store_true", help="skip the plant+decode (iteration only, not a claim)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    seed = H.resolve_seed(a.seed)
    H.banner("C8 non-English adjudicator", seed, f"FPR {FPR}, every null class; pos={a.pos}"
             + ("  DIRECT (not a claim)" if a.direct else ""))

    if a.self_test or not a.submission:
        texts = a.heldout or ["data/keys/armada19/stoker_dracula.txt", "analysis/latin/latin_218.txt",
                              "analysis/round10b/B6-non-english-plaintext/corpora/de_2.txt"]
        t0 = time.time()
        ok = True
        for i, path in enumerate(texts):
            stream, how = load_heldout(path)
            sets = build(stream, seed, a.pos, a.null, a.beam_null, a.direct)
            print(f"\n=== held-out: {path}  ({len(stream)} runes, {how})")
            en = evaluate(H.english_score, sets)
            show("English reference (lp.score quadgram score_norm)", en)
            show("incumbent panel-R36 pmax (12 registers)", evaluate(H.panel_pmax, sets))
            if i == 0 and not a.heldout:
                ok = en[HEADLINE_L]["power"] >= FINISH          # control: English sees English
        print(f"\ncontrol (English scorer on English held-out, L={HEADLINE_L}): {'held' if ok else 'FAILED'}"
              f"   ({time.time() - t0:.0f}s)")
        print("SELF-TEST " + ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)

    if not a.heldout:
        raise SystemExit("give --heldout: text in your register that the scorer was not trained on")
    import _sandbox
    with _sandbox.Sandbox(a.submission, "score", "float", attrs=("REGISTER",)) as sb:
        reg = sb.attrs.get("REGISTER")
        if not reg:
            raise SystemExit("your module must define REGISTER = '<name>'")
        stream = []
        for p in a.heldout:
            s, how = load_heldout(p)
            print(f"held-out {p}: {len(s)} runes ({how})")
            stream += s
        sets = build(stream, seed, a.pos, a.null, a.beam_null, a.direct)
        res = evaluate(None, sets, many=lambda xs: sb.map([(x,) for x in xs]))
    inc = evaluate(H.panel_pmax, sets)
    show(f"{a.submission}  (REGISTER = {reg})", res)
    show("incumbent panel-R36 pmax", inc)
    head, ihead = res[HEADLINE_L]["power"], inc[HEADLINE_L]["power"]
    new_reg = reg.upper() not in H.PANEL_REGISTERS
    done = head >= FINISH and new_reg and not a.direct
    print(f"\nL={HEADLINE_L}: power {head:.3f} (need {FINISH}); incumbent {ihead:.3f}; "
          f"register {'new' if new_reg else 'ALREADY IN PANEL-R36'}")
    if done:
        print("FINISH LINE MET, pending code and source review (REGISTER is only a label: the maintainers "
              "check that the held-out text really is a register outside the 12)" + ("  -> files as an EXTENSION of the panel" if ihead < FINISH
                                    else "  -> files as 'already seen by panel-R36' (incumbent >= 0.80)"))
    else:
        print("not yet")
    print(json.dumps({"id": f"C8-{reg}", "seed": seed, "L": HEADLINE_L, "power": head, "incumbent": ihead,
                      "per_class": res[HEADLINE_L]["per_class"], "direct": a.direct}))
    sys.exit(0 if done else 1)


if __name__ == "__main__":
    main()
