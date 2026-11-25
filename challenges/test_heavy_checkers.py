"""Smoke tests for the heavy-lift checkers C7-C10: each one's plant and its controls behave as documented.

    python -m pytest challenges/test_heavy_checkers.py -q      (~2 min; c1_crossdiff_test.py fails on purpose, run this file alone)

R47-H2 added the isolation regressions: R47-X1's four cheats (liber-primus/analysis/round47/X1-redteam/) and a
call-order cheat must all FAIL now that submissions run in an isolated child process (challenges/_sandbox.py).
"""
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402
import c7_corpus_forge as C7  # noqa: E402
import c8_register_scorer as C8  # noqa: E402
import c9_rejection_loops as C9  # noqa: E402
import c10_shuffled_lengths as C10  # noqa: E402
import _sandbox as SB  # noqa: E402

X1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "liber-primus", "analysis", "round47", "X1-redteam")


def test_c7_example_valid_and_corruption_caught():
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "corpus.txt")
        code, row = C7.check(C7.EXAMPLE, build=True, seed=1, corpus_override=cp, quiet=True)
        assert code == 0 and row["n_words"] > 20000 and not row["crosses_finish_line"]
        assert row["lp2_two_rune_share"] == 0.1547
        lines = open(cp, encoding="utf-8").read().split("\n")
        lines = [H.RUNES[(H.RUNE_IDX[ln[0]] + 1) % 29] + ln[1:] if ln else ln for ln in lines]
        open(cp, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        code, _ = C7.check(C7.EXAMPLE, seed=1, corpus_override=cp, quiet=True)
        assert code == 1


def test_c7_table_rejects_non_gp_tokens():
    errs = []
    C7.compile_table({"a": "A", "q": "QU"}, errs)
    assert errs and "QU" in errs[0]


def test_c8_threshold_holds_every_class():
    sets = C8.build(H.english_stream(), 3, 30, 200, 5, True, lengths=(120,))
    r = C8.evaluate(H.english_score, sets)[120]
    assert r["power"] >= 0.8 and set(r["per_class"]) == set(C8.CLASSES)


def test_c9_variants_match_lp2_surface_and_keyskip_control():
    rng = random.Random(5)
    P = H.english_stream()[:13000]
    lag = lambda x, d: sum(x[i] == x[i + d] for i in range(len(x) - d)) / (len(x) - d)
    for v in ("V-BACK", "V-NULL", "V-DEFER"):
        c = C9.VARIANTS[v](P, H.rand_key(rng, 60000), H.EXACT_SUPP, rng)
        assert 0.003 < lag(c, 1) < 0.011 and 0.028 < lag(c, 2) < 0.042, v
    assert len(C9.enc_null(P, H.rand_key(rng, 60000), H.EXACT_SUPP, rng)) > len(P)
    res = C9.evaluate(C9.ref_beam, C9.make_plants("KEYSKIP (control)", 3, 7, H.english_stream()))
    assert res["k"] == 3


def test_c10_true_lengths_decode_exactly_and_family_is_searchable():
    plants, nulls = C10.make_cases(3, 11, H.english_sentences())
    for c in plants:
        K = C10.key_stream(c["s"], max(C10.positions(c["true_lens"])) + 1)
        assert C10.decode_with(c["C"], K, c["true_lens"]) == c["P"] and c["s"] < C10.F_KEYS
    assert all(c["s"] >= C10.NULL_KEY_MIN for c in nulls)
    b = C10.key_block(100, 104, [0, 7, 5000])
    assert [[C10.key_stream(s, 5001)[t] for t in (0, 7, 5000)] for s in range(100, 104)] == b.tolist()
    q, out, s = C10.exhaustive(plants[0]["C"], plants[0]["true_lens"])          # baseline (i) on one plant
    assert s == plants[0]["s"] and out == plants[0]["P"]


# ------------------------------------------------------------------ isolation regressions (R47-H2)
def _write(td, name, src):
    p = os.path.join(td, name)
    open(p, "w", encoding="utf-8").write(src)
    return p


def test_sandbox_child_has_no_checker_state():
    with tempfile.TemporaryDirectory() as td:
        p = _write(td, "probe.py", "import sys\n"
                   "def score(idx):\n"
                   "    names = set()\n"
                   "    f = sys._getframe(0)\n"
                   "    while f is not None:\n"
                   "        names |= set(f.f_locals)\n"
                   "        f = f.f_back\n"
                   "    bad = {'sets', 'pos', 'neg', 'plants', 'P', 'K', 'WK', 'seed'} & names\n"
                   "    return float(len(bad)) + (1000.0 if any('c8_register' in m or 'c9_rej' in m for m in sys.modules) else 0)\n")
        with SB.Sandbox(p, "score", "float") as sb:
            assert sb.call([1, 2, 3]) == 0.0


def test_x1_c8_frame_cheat_fails_isolated():
    sets = C8.build(H.english_stream(), 99, 30, 200, 5, True, lengths=(120,))
    with SB.Sandbox(os.path.join(X1, "x1_cheat_c8.py"), "score", "float") as sb:
        r = C8.evaluate(None, sets, many=lambda xs: sb.map([(x,) for x in xs]))[120]
    assert r["power"] < C8.FINISH, r


def test_c8_call_order_cheat_fails_isolated():
    """Positives used to be scored first: a stateful scorer that says 'yes' to the first n calls must fail."""
    sets = C8.build(H.english_stream(), 98, 30, 200, 5, True, lengths=(120,))
    with tempfile.TemporaryDirectory() as td:
        p = _write(td, "order.py", "N = [0]\n"
                   "def score(idx):\n"
                   "    N[0] += 1\n"
                   "    return 1.0 if N[0] <= 30 else 0.0\n")
        with SB.Sandbox(p, "score", "float") as sb:
            r = C8.evaluate(None, sets, many=lambda xs: sb.map([(x,) for x in xs]))[120]
    assert r["power"] < C8.FINISH, r


def test_x1_c9_frame_cheat_fails_isolated():
    with SB.Sandbox(os.path.join(X1, "x1_cheat_c9.py"), "decode", "plain") as sb:
        res = C9.run(None, 3, 99, H.english_stream(), ["V-NULL", "V-BACK"], sb=sb)
    assert res["V-NULL"]["k"] == 0 and res["V-BACK"]["k"] == 0, res


def test_x1_c10_frame_cheats_fail_isolated():
    plants, nulls = C10.make_cases(2, 99, H.english_sentences())
    cases = plants + nulls
    args = [(list(c["C"]), [list(s) for s in c["printed"]]) for c in cases]
    with SB.Sandbox(os.path.join(X1, "x1_cheat_c10.py"), "attack", "list") as sb:     # old (C, K, printed) cheat
        outs = sb.map(args, on_error=lambda i, e: [])
    assert C10.summarise(plants, nulls, outs[:2], outs[2:])["k"] == 0
    with tempfile.TemporaryDirectory() as td:
        p = _write(td, "walk.py", "import sys\n"
                   "def attack(C, printed):\n"
                   "    f = sys._getframe(1)\n"
                   "    while f is not None:\n"
                   "        for v in f.f_locals.values():\n"
                   "            if isinstance(v, dict) and 'P' in v and v.get('C') == C:\n"
                   "                return list(v['P'])\n"
                   "        f = f.f_back\n"
                   "    return [0] * len(C)\n")
        with SB.Sandbox(p, "attack", "list") as sb:
            outs = sb.map(args)
    assert C10.summarise(plants, nulls, outs[:2], outs[2:])["k"] == 0


def test_x1_c7_english_labelled_old_norse_rejected():
    import json
    import shutil
    with tempfile.TemporaryDirectory() as td:
        shutil.copy(os.path.join(X1, "x1_cheat_c7_manifest.json"), os.path.join(td, "manifest.json"))
        errs = []
        code, row = C7.check(os.path.join(td, "manifest.json"), build=True, seed=1, quiet=True, errs_out=errs)
        assert code == 1 and row is None and any(e.startswith("label check") for e in errs), errs
    assert json.load(open(C7.EXAMPLE, encoding="utf-8"))["language"] == "lat"
