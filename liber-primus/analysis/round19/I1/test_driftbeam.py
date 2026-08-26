"""Round 19 / I1 -- tests for driftbeam.

    python3 -m pytest liber-primus/analysis/round19/I1/test_driftbeam.py -q

The load-bearing ones are:
  * test_equivalence_with_repo_decoder  -- gate G-EQ; a failure voids the lane
  * test_histogram_matches_naive_relation -- the O(1) histogram identity that the whole
    speed argument rests on, checked against a brute-force implementation of the repo's
    original per-position validity loop
"""
import os
import sys
import random

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driftbeam as db                       # noqa: E402
import constructions as cx                   # noqa: E402

sys.path.insert(0, os.path.join(db.ROOT, "analysis", "campaign18_skip"))
import skipdecode as sk                      # noqa: E402

N = db.N


# ------------------------------------------------------------------ gate G-EQ
def test_equivalence_with_repo_decoder():
    r = db.gate_EQ(reps=4, lengths=(60, 120, 240), verbose=False)
    assert r["path_mismatches"] == 0
    assert r["max_score_delta"] < 1e-9
    assert r["cases"] >= 12


def test_equivalence_with_fastbeam():
    r = db.gate_EQ_fast(reps=3, lengths=(120, 240), verbose=False)
    assert r["pass"]


# ------------------------------------------- the identity the speed rests on
def _naive_unexplained(Kx, pa, acc, sign, cprev, ci):
    """Brute force: count skipped positions that would NOT have reproduced cprev,
    written the way skipdecode.beam_decode writes it."""
    p = (ci + sign * Kx[acc]) % N
    bad = 0
    for m in range(pa + 1, acc):
        if (p - sign * Kx[m]) % N != cprev:
            bad += 1
    return bad


def test_histogram_matches_naive_relation():
    rng = random.Random(4242)
    for _ in range(400):
        Kx = [rng.randrange(N) for _ in range(80)]
        sign = rng.choice((-1, 1))
        ci = rng.randrange(N)
        cprev = rng.randrange(N)
        pa = rng.randrange(0, 40)
        sgn_delta = (sign * (cprev - ci)) % N
        cnt = [0] * N
        for dsk in range(0, 12):
            acc = pa + 1 + dsk
            if dsk:
                cnt[Kx[acc - 1]] += 1
            v = (Kx[acc] - sgn_delta) % N
            fast = dsk - cnt[v]
            slow = _naive_unexplained(Kx, pa, acc, sign, cprev, ci)
            assert fast == slow, (dsk, fast, slow)


# ------------------------------------------------------- mode-exactness checks
@pytest.mark.parametrize("supp", [0.5, 0.83, 1.0])
def test_keyskip2_is_exact_for_skip_by_two(supp):
    P = cx.take_plain(240, 3)
    K = cx.key_sha(240 * 6 + 1024)
    C, _ = cx.enc_skip_by_two(P, K, supp=supp, seed=3301)
    r = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=8, mode="keyskip2")
    assert db.recovery(r["plain_idx"], P) >= 0.90
    assert r["score"] >= -5.5


def test_permissive_covers_skip_by_two():
    P = cx.take_plain(240, 3)
    K = cx.key_sha(240 * 6 + 1024)
    C, _ = cx.enc_skip_by_two(P, K, supp=0.83, seed=3301)
    r = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, **db.PRESETS["drift"])
    assert db.recovery(r["plain_idx"], P) >= 0.90
    assert r["score"] >= -5.5


def test_permissive_does_not_regress_the_baseline():
    """G-COST: on the construction the repo decoder is exact for, permissive must not
    lose score or recovery."""
    for seed in (0, 1, 2):
        P = cx.take_plain(240, seed)
        K = cx.key_sha(240 * 6 + 1024)
        C, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301 + seed)
        a = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, **db.PRESETS["exact"])
        b = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, **db.PRESETS["drift"])
        assert b["score"] >= a["score"] - 0.15
        assert db.recovery(b["plain_idx"], P) >= db.recovery(a["plain_idx"], P) - 0.02


def test_unpenalised_permissive_is_a_known_failure():
    """lam = 0 buys freedom the beam spends on English-looking WRONG paths: the score
    stays respectable while rune recovery collapses.  Pinned as a test so nobody ships
    lam = 0 by accident."""
    P = cx.take_plain(240, 0)
    K = cx.key_sha(240 * 6 + 1024)
    C, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    r = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, mode="permissive",
                       max_skip=40, max_free=2, lam=0.0, start_slack=2)
    assert db.recovery(r["plain_idx"], P) < 0.60


def test_reported_score_is_unpenalised_quadgram():
    """The lam penalty must steer the search only; the reported score must remain the
    project's canonical score_norm of the emitted transliteration."""
    P = cx.take_plain(120, 5)
    K = cx.key_sha(120 * 6 + 1024)
    C, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    r = db.beam_decode(C, K, sign=-1, o=0, beam_w=200, **db.PRESETS["drift"])
    assert abs(r["score"] - db.Q.score_norm(r["translit"])) < 1e-9


def test_skip_count_channel():
    P = cx.take_plain(400, 1)
    K = cx.key_sha(400 * 6 + 1024)
    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    r = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, **db.PRESETS["exact"])
    assert r["n_skips"] == int(sum(skips))


def test_permissive_requires_max_free():
    with pytest.raises(ValueError):
        db.beam_decode([1, 2, 3], list(range(29)) * 4, mode="permissive", max_free=0)


def test_bad_mode_rejected():
    with pytest.raises(ValueError):
        db.beam_decode([1, 2, 3], list(range(29)) * 4, mode="nonsense")


def test_want_path_false_scores_identically():
    P = cx.take_plain(200, 2)
    K = cx.key_sha(200 * 6 + 1024)
    C, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    a = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, want_path=True,
                       **db.PRESETS["drift"])
    b = db.beam_decode(C, K, sign=-1, o=0, beam_w=400, want_path=False,
                       **db.PRESETS["drift"])
    assert abs(a["score"] - b["score"]) < 1e-12
    assert a["n_skips"] == b["n_skips"]


def test_coin_from_key_doublet_rate_is_lp2_like():
    """The new two-draws construction is only interesting if it reproduces LP2's surface
    statistic, the same test L7-B applied to skip_by_two."""
    rates = []
    for seed in range(5):
        P = cx.take_plain(400, seed)
        K = cx.key_sha(400 * 6 + 1024)
        C, _ = cx.enc_coin_from_key(P, K, supp=0.83, seed=3301 + seed)
        rates.append(cx.doublet_pct(C))
    med = sorted(rates)[len(rates) // 2]
    assert med < 1.5, med          # far below the 3.448 % unfiltered expectation
