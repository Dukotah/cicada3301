"""Lane F-01 — LP2-as-pad inversion.

Treat the 12,956-rune unsolved LP2 stream as KEY MATERIAL and run it (forward,
reversed, negated mod-29, Atbash) as a running key through the repo's validated
skip-aware beam decoder against every other machine-readable Cicada object.

The set of targets is finite:
  T1  2012/2013 puzzle text fragments (English -> rune indices)
  T2  Solved LP1 pages (five solved pages concatenated, rune indices)
  T3  PGP message bodies (English prose)
  T4  AN-END hash bytes, mod 29
  T5  pp49-51 payload bytes, mod 29

Key variants K ∈ {LP2_fwd, LP2_rev, LP2_atbash, LP2_neg} × sign ∈ {-1, +1}
= 8 (key, sign) pairs, each tested at offset 0.

For each (target, key_variant, sign) the beam decoder produces a score_norm.
A positive control (plant+recover) MUST PASS before any result is meaningful.

Usage (from repo root):
    cd liber-primus
    python analysis/round16/F-01/sweep.py
"""
import os, sys, json, random, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP   = os.path.join(ROOT, "liber-primus")

for p in (
    os.path.join(LP, "src"),
    os.path.join(LP, "analysis"),
    os.path.join(LP, "analysis", "round11"),
    os.path.join(LP, "analysis", "campaign18_skip"),
):
    if p not in sys.path:
        sys.path.insert(0, p)

import skipdecode as sk    # noqa
import lib_numchannel as nc  # noqa
from lp import gematria as gp  # noqa

N = 29


# ----------------------------------------------------------------- helpers
def atbash(seq):
    return [(N - 1 - x) % N for x in seq]


def neg_mod(seq):
    return [(-x) % N for x in seq]


def null_band_beam(C, K, sign, n=200, seed0=3301, beam_w=400, max_skip=3):
    """Null distribution: shuffle C (not K) and beam-decode each shuffle."""
    rng = random.Random(seed0)
    vals = []
    for k in range(n):
        shuffled = list(C)
        rng.shuffle(shuffled)
        bd = sk.beam_decode(shuffled, K, sign=sign, o=0,
                            beam_w=beam_w, max_skip=max_skip)
        vals.append(bd["score"])
    return sum(vals) / len(vals), max(vals), vals


def load_lp2():
    """The 12,956-rune unsolved LP2 stream, as rune indices."""
    return nc.unsolved()


def load_lp1_runes():
    """All five solved LP pages concatenated, as rune indices (from dataset)."""
    pages = nc.segments()
    # pages[-2] = AN END (solved), pages[-1] = PARABLE (plaintext) - exclude
    # The five solved page rune indices are stored in SOLVED-PAGES.json
    # We load the solved-page transliterations and convert back
    solved_path = os.path.join(LP, "SOLVED-PAGES.json")
    with open(solved_path, encoding="utf-8") as f:
        sp = json.load(f)
    idxs = []
    for pg in sp["pages"]:
        translit = pg["plaintext_transliteration"]
        idxs.extend(sk.eng_to_idx(translit))
    return idxs


def load_cicada_2012_2013():
    """Cicada 2012/2013 English puzzle text -> rune indices."""
    txt_path = os.path.join(
        LP, "data", "keys", "armada18", "cicada_2012_2013_puzzle_texts.txt"
    )
    with open(txt_path, encoding="utf-8") as f:
        text = f.read()
    return sk.eng_to_idx(text)


def load_pgp_messages():
    """Cicada PGP message bodies -> rune indices."""
    txt_path = os.path.join(
        LP, "data", "keys", "armada18", "cicada_pgp_messages.txt"
    )
    with open(txt_path, encoding="utf-8") as f:
        text = f.read()
    return sk.eng_to_idx(text)


def load_anend_hash():
    """AN-END SHA-512 hash bytes as mod-29 values."""
    # The canonical hash from the ledger: 36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4
    # This is the hash of the AN-END deep-web page content
    h = bytes.fromhex(
        "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8"
        "425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8"
    )
    # Pad to 128 bytes by repeating if needed (the actual hash may vary in full form)
    # Use both byte-mod-29 and nibble-mod-29 representations
    return [b % N for b in h]


def load_pp4951_payload():
    """pp49-51 256-byte payload as mod-29 values.

    The payload is stored in the campaign7 results; we reconstruct it from the
    known decoded hex in the dataset.
    """
    # From campaign VII: the pp49-51 table decodes to a 2048-bit high-entropy blob.
    # We read the canonical rune stream of those pages (pp49-51 = pages at indices
    # that encode the payload) and convert via the same hex decode used in campaign VII.
    pp_path = os.path.join(LP, "analysis", "pp49_51")
    # Try to load from the analysis outputs
    candidates = [
        os.path.join(pp_path, "payload.bin"),
        os.path.join(pp_path, "payload.hex"),
        os.path.join(pp_path, "payload_bytes.json"),
    ]
    for cp in candidates:
        if os.path.exists(cp):
            if cp.endswith(".bin"):
                with open(cp, "rb") as f:
                    return [b % N for b in f.read()]
            elif cp.endswith(".hex"):
                with open(cp) as f:
                    return [b % N for b in bytes.fromhex(f.read().strip())]
            elif cp.endswith(".json"):
                with open(cp) as f:
                    data = json.load(f)
                return [b % N for b in data]

    # Fallback: use the known SHA256 of the unsolved stream to verify integrity
    # and derive a synthetic "payload" from the known pp49-51 rune sequence.
    # The pp49-51 runes decode as base-60 tokens; we use the approach from campaign VII.
    print("  [WARN] pp49-51 payload file not found; skipping T5")
    return None


# ----------------------------------------------------------------- positive control
def positive_control(LP2_fwd, beam_w=400, max_skip=3):
    """Plant-and-recover gate.

    Encipher a known English sentence under the LP2 stream (using key-skip model)
    and verify the beam decoder recovers it.
    """
    print("\n=== POSITIVE CONTROL ===")
    PLAIN_TEXT = (
        "THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
        "ENCRYPTEDCNOWTHISSHADOWSAETHEREALBUFFER"
    )
    P = sk.eng_to_idx(PLAIN_TEXT)
    K = LP2_fwd  # Use the actual LP2 stream as the key

    # Encipher under key-skip model
    C_planted, skips, used = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    nsk = sum(1 for s in skips if s)
    dbl = sum(1 for i in range(1, len(C_planted)) if C_planted[i] == C_planted[i - 1]) / max(1, len(C_planted) - 1)
    print(f"  planted: {len(P)} plaintext runes, {nsk} skips injected, doublet={dbl:.4f}")

    plain_score = nc.eng_norm(P)
    beam_result = sk.beam_decode(C_planted, K, sign=-1, o=0, beam_w=beam_w, max_skip=max_skip)
    rigid_result = sk.rigid_decode(C_planted, K, sign=-1, o=0)

    # Null band
    mean_n, max_n, _ = null_band_beam(C_planted, K, sign=-1, n=100, seed0=3301, beam_w=beam_w, max_skip=max_skip)

    char_rec = sum(a == b for a, b in zip(beam_result["translit"], PLAIN_TEXT)) / len(PLAIN_TEXT)

    print(f"  English target score:   {plain_score:.3f}")
    print(f"  RIGID decode (correct): {rigid_result['score']:.3f}")
    print(f"  BEAM decode (correct):  {beam_result['score']:.3f}")
    print(f"  Char recovery:          {char_rec:.3f}")
    print(f"  Null (n=100): mean={mean_n:.3f}  max={max_n:.3f}")

    gate_pass = (
        beam_result["score"] >= -5.5
        and beam_result["score"] >= max_n + 0.5
        and beam_result["score"] > rigid_result["score"] + 0.5
        and char_rec >= 0.80
    )
    status = "PASS" if gate_pass else "FAIL"
    print(f"  Control: {status}")
    return gate_pass, {
        "plain_score": plain_score,
        "rigid_score": rigid_result["score"],
        "beam_score": beam_result["score"],
        "char_recovery": char_rec,
        "null_mean": mean_n,
        "null_max": max_n,
        "gate": status,
    }


# ----------------------------------------------------------------- main sweep
def run():
    t_start = time.time()

    # Load LP2 stream
    LP2_fwd = load_lp2()
    print(f"LP2 loaded: {len(LP2_fwd)} runes")

    # Verify the SHA256 of the unsolved stream matches PROBLEM.json
    import hashlib
    chk = hashlib.sha256(",".join(str(x) for x in LP2_fwd).encode()).hexdigest()
    expected = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    if chk != expected:
        print(f"[ERROR] LP2 hash mismatch! got {chk}")
        sys.exit(1)
    print(f"LP2 hash: OK")

    # Positive control
    pc_pass, pc_data = positive_control(LP2_fwd)
    if not pc_pass:
        print("[FATAL] Positive control FAILED — no null result is meaningful.")
        results = {
            "positive_control": pc_data,
            "positive_control_passed": False,
            "results": [],
            "verdict": "NEGATIVE (control failed — no inference possible)",
        }
        out_path = os.path.join(HERE, "results.json")
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {out_path}")
        return

    # Build all 4 LP2 key variants
    LP2_rev     = list(reversed(LP2_fwd))
    LP2_atbash  = atbash(LP2_fwd)
    LP2_neg     = neg_mod(LP2_fwd)

    key_variants = {
        "lp2_fwd":    LP2_fwd,
        "lp2_rev":    LP2_rev,
        "lp2_atbash": LP2_atbash,
        "lp2_neg":    LP2_neg,
    }

    # Load all targets
    print("\n=== Loading targets ===")
    targets = {}
    try:
        T1 = load_cicada_2012_2013()
        targets["T1_cicada_2012_2013"] = T1
        print(f"  T1 Cicada 2012/2013 texts: {len(T1)} rune-indices")
    except Exception as e:
        print(f"  T1 FAILED: {e}")

    try:
        T2 = load_lp1_runes()
        targets["T2_lp1_solved"] = T2
        print(f"  T2 LP1 solved pages: {len(T2)} rune-indices")
    except Exception as e:
        print(f"  T2 FAILED: {e}")

    try:
        T3 = load_pgp_messages()
        targets["T3_pgp_messages"] = T3
        print(f"  T3 PGP messages: {len(T3)} rune-indices")
    except Exception as e:
        print(f"  T3 FAILED: {e}")

    try:
        T4 = load_anend_hash()
        if T4:
            targets["T4_anend_hash"] = T4
            print(f"  T4 AN-END hash bytes: {len(T4)} mod-29 values")
    except Exception as e:
        print(f"  T4 FAILED: {e}")

    try:
        T5 = load_pp4951_payload()
        if T5:
            targets["T5_pp4951"] = T5
            print(f"  T5 pp49-51 payload: {len(T5)} mod-29 values")
    except Exception as e:
        print(f"  T5 FAILED: {e}")

    # The LP2 stream itself is too large to fit as a target against itself meaningfully,
    # but we can test head segments (first 200 runes as a "ciphertext" vs the rest of LP2 as key)
    # This covers the "LP2 head as ciphertext, LP2 body as key" hypothesis
    T6 = LP2_fwd[:200]
    targets["T6_lp2_head_200"] = T6
    print(f"  T6 LP2 head (first 200 runes as ct): {len(T6)} rune-indices")

    BEAM_W = 400
    MAX_SKIP = 3

    rows = []
    print("\n=== Sweep ===")
    for tname, C in targets.items():
        if C is None:
            continue
        # Cap target at 500 runes (enough for a meaningful quadgram score)
        Ctrim = C[:500]
        print(f"\n  Target {tname} ({len(Ctrim)} runes):")
        for kname, K in key_variants.items():
            # Extend K if needed
            K_ext = K + [0] * max(0, len(Ctrim) * (MAX_SKIP + 2) - len(K) + 128)
            for sign in (-1, +1):
                bd = sk.beam_decode(Ctrim, K_ext, sign=sign, o=0,
                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                s = bd["score"]
                head = bd["translit"][:60]
                row = {
                    "target": tname,
                    "target_len": len(Ctrim),
                    "key_variant": kname,
                    "sign": sign,
                    "score": s,
                    "head": head,
                    "above_bar": s >= -5.5,
                }
                rows.append(row)
                marker = "*** HIT CANDIDATE ***" if s >= -5.5 else ""
                print(f"    {kname:15s} sign={sign:+d}  score={s:.3f}  {head[:40]}  {marker}")

    # Sort by score descending
    rows.sort(key=lambda r: -r["score"])

    # Compute null bands for the top candidates (above -6.0)
    print("\n=== Null bands for top candidates ===")
    TOP_N_NULL = 5
    null_computed = 0
    for row in rows[:TOP_N_NULL]:
        tname = row["target"]
        C = targets.get(tname)
        if C is None:
            continue
        Ctrim = C[:500]
        K = key_variants[row["key_variant"]]
        sign = row["sign"]
        K_ext = K + [0] * max(0, len(Ctrim) * (MAX_SKIP + 2) - len(K) + 128)

        mean_n, max_n, _ = null_band_beam(Ctrim, K_ext, sign=sign, n=200, seed0=3301,
                                          beam_w=BEAM_W, max_skip=MAX_SKIP)
        row["null_mean"] = mean_n
        row["null_max"] = max_n
        row["beats_null_by"] = row["score"] - max_n
        row["hit"] = (row["score"] >= -5.5 and row["score"] >= max_n + 0.5)
        print(f"  {tname}/{row['key_variant']}/sign={row['sign']:+d}: "
              f"score={row['score']:.3f}  null_max={max_n:.3f}  "
              f"beats_by={row['beats_null_by']:.3f}  HIT={row['hit']}")
        null_computed += 1

    best_score = rows[0]["score"] if rows else None
    best_row = rows[0] if rows else None
    any_hit = any(r.get("hit", False) for r in rows)

    elapsed = time.time() - t_start
    print(f"\nElapsed: {elapsed:.1f}s")
    print(f"Best score: {best_score:.3f}")
    print(f"Any HIT: {any_hit}")

    # Build output
    out = {
        "positive_control": pc_data,
        "positive_control_passed": pc_pass,
        "n_decodes": len(rows),
        "elapsed_s": elapsed,
        "best_score": best_score,
        "best_row": best_row,
        "any_hit": any_hit,
        "bar": -5.5,
        "results": rows,
    }

    out_path = os.path.join(HERE, "results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")

    # Verdict
    if any_hit:
        print("\nVERDICT: HIT CANDIDATE — re-derive manually before claiming solve")
    else:
        cov = f"{len(targets)} targets × {len(key_variants)} key_variants × 2 signs = {len(rows)} beam decodes"
        print(f"\nVERDICT: NEGATIVE (best={best_score:.3f} vs bar -5.5). Coverage: {cov}")


if __name__ == "__main__":
    run()
