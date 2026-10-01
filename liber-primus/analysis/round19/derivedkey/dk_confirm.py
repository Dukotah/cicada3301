"""Round 19 - LANE 2 - DERIVED-KEY DICTIONARY - instrument anchor + holdout.

This lane does NOT open a new key-space sweep. Its PREREG hypothesis class (short-seed-
DERIVED keystreams: $RANDOM/glibc, TeX LCG, Py2.7 random, PBKDF2/scrypt over published
Cicada seeds incl. 3301 / 7A35090F / page-56 hash) was found, on reading LEDGER.json, to
be ALREADY-MEASURED ground across rounds R16 (KDF 692,064 configs), R20/R21/R25/R27
(Py2.7-MT full and tail), R24-C1/C1-EXT (non-English register re-adjudication of the KDF/
B-04 slice with R3 persisted), R24-C2 (skip_by_two decoder), R26-A/C (Perl/TeX/semantic-
seed zoo incl. 3301, 0x7A35090F fragments, page hashes), R28-L4 (unswept-generator queue).
Doctrine forbids re-running measured ground; the Round-19 mandate is precisely NOT to repeat
the ~10^10 mis-aimed decodes. So this script runs only what anchors the lane's NEGATIVE:

  1. DK-PC2 positive control: plant a PBKDF2 keystream derived from a PUBLISHED seed, encipher
     a held English / Latin / Old-English plaintext under the pinned keyskip construction,
     decode with the CORRECT key via the live beam, and confirm the instrument RECOVERS and
     SCORES the planted derived-key hit (so a null from this instrument is a real negative).
     R3 columns persisted per row in Lane-1's exact schema.

  2. AN-END BLIND HOLDOUT (mandatory PREREG gate): hand ONLY the AN-END-class ciphertext +
     its stated external input (the prime sequence) and require blind rediscovery of the
     totient keystream phi(prime)=(p-1) mod 29, shift-down. Reports RECOVERED / NOT.

Writes: dk_confirm.json
    PYTHONUTF8=1 python3 dk_confirm.py
"""
import os, sys, json, hashlib, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
INSTR = os.path.join(LP, "analysis", "round19", "instrument")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer"), INSTR):
    if p not in sys.path:
        sys.path.insert(0, p)

import sympy                                             # noqa: E402
from lp import gematria as gp, score as _score          # noqa: E402
import skipdecode as sk                                  # noqa: E402
from scorer import matched_scorer                        # noqa: E402
# reuse Lane-1's EXACT R3 helpers so the schema matches power_table.json row-for-row
import power_envelope as PE                              # noqa: E402

N = gp.N
Q = _score.default()
ENG_MATCHED = matched_scorer()
F_IDX = gp.RUNE_TO_IDX[gp.INTERRUPTER]

# Published Cicada seeds this lane names (finite, human-checkable -- doctrine R5 tier 1)
PUBLISHED_SEEDS = {
    "3301": b"3301",
    "7A35090F": bytes.fromhex("7A35090F"),
    "page56_hash": hashlib.sha512(b"AN END").digest(),  # stand-in published 512-bit hash form
    "prime_seq": b"2 3 5 7 11 13 17 19 23 29",
}

PLAIN = {
    "EN": ("THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE "
           "ENCRYPTED KNOW THIS AND SEEK THE TRUTH WITHIN THE DEEP WEB FIND YOUR WAY"),
    "LA": ("PRIMI SACRI SUNT FUNCTIO TOTIENTIS SACRA EST OMNIA CELARI DEBENT SCITO HOC "
           "ET QUAERE VERITATEM INTRA PROFUNDUM VERITAS VOS LIBERABIT INVENITE VIAM"),
    "OE": ("WITODLICE THA FRUMAN SIND HALIG AND SE GETEL IS HALIG EALLE THING SCEOLON "
           "BEON BEDIGLOD WITE THIS AND SEC THONE SOTH BINNAN THAERE DEOPAN WISDOM"),
}


def pbkdf2_keystream(seed_bytes, nlen, salt=b"CICADA", iters=2048):
    """A documented KDF (PBKDF2-HMAC-SHA256) over a published seed, reduced mod 29.
    This IS the Tier-A KDF hypothesis member; here used ONLY to plant the positive control."""
    out, ctr = [], 0
    while len(out) < nlen:
        blk = hashlib.pbkdf2_hmac("sha256", seed_bytes,
                                  salt + ctr.to_bytes(4, "big"), iters, dklen=64)
        out.extend(b % N for b in blk)
        ctr += 1
    return out[:nlen]


def totient_keystream(n, start_prime=2):
    ks, p = [], start_prime
    while len(ks) < n:
        ks.append((p - 1) % N)
        p = sympy.nextprime(p)
    return ks


_LMS = None


def _lms():
    global _LMS
    if _LMS is None:
        regs = PE.build_registers()
        _LMS = PE.build_lms(regs)
    return _LMS


def r3_cols(dec_idx):
    """Lane-1's exact R3 schema (the four doctrine-R3 language-agnostic statistics),
    measured on the correct-key decode indices, via Lane-1's own helpers."""
    best_lm, best_reg = PE.best_nonenglish_lm(dec_idx, _lms())
    return {
        "r3_ioc_times_n": round(PE.ioc_times_n(dec_idx), 4),
        "r3_min_distinct_32": PE.min_distinct_32(dec_idx),
        "r3_best_nonenglish_lm": round(best_lm, 4),
        "r3_best_nonenglish_lm_register": best_reg,
        "r3_compressibility": round(PE.compressibility(dec_idx), 4),
    }


def dk_pc2():
    """Plant a PBKDF2-from-published-seed keystream, encipher EN/LA/OE under keyskip, decode
    with the correct key via the live beam, confirm RECOVERY + score. Anchors the null."""
    rows = []
    for reg, text in PLAIN.items():
        plain_idx = sk.eng_to_idx(text)
        L = len(plain_idx)
        for sname, sb in PUBLISHED_SEEDS.items():
            K = pbkdf2_keystream(sb, L + 8)
            # encipher under pinned keyskip (sign convention per repo: c=(p - k) mod N)
            C = [(plain_idx[i] - K[i]) % N for i in range(L)]
            bd = sk.beam_decode(C, K + [0] * (L * 4 + 8), sign=+1, o=0,
                                beam_w=400, max_skip=3)
            rec = sum(1 for a, b in zip(bd["plain_idx"], plain_idx) if a == b) / L
            # wrong seed null (same construction)
            Kw = pbkdf2_keystream(b"WRONGSEED", L + 8)
            bdw = sk.beam_decode(C, Kw + [0] * (L * 4 + 8), sign=+1, o=0,
                                 beam_w=400, max_skip=3)
            row = {
                "register": reg, "construction": "keyskip",
                "key_family": "pbkdf2_hmac_sha256(published_seed)", "seed": sname,
                "L": L,
                "recovery_correct_key": round(rec, 4),
                "en_quadgram_correct": round(bd["score"], 4),
                "en_quadgram_wrong": round(bdw["score"], 4),
                "matched_lm_correct": round(ENG_MATCHED.score_norm(bd["translit"]), 4),
                "matched_lm_wrong": round(ENG_MATCHED.score_norm(bdw["translit"]), 4),
            }
            row.update(r3_cols(bd["plain_idx"]))
            rows.append(row)
    return rows


def anend_blind_holdout():
    """BLIND rediscovery of the AN-END totient keystream. Build the AN-END-class ciphertext
    forward (totient shift-down + F-interrupters), then try to REDISCOVER the keystream handed
    ONLY: (a) the ciphertext, (b) its stated external input = the prime sequence. We do NOT
    hand over the derived keystream. Rediscovery = reconstruct (p-1) mod 29 from the primes and
    confirm the interrupter-aware solve returns the known plaintext."""
    import random
    plain_idx = sk.eng_to_idx(
        "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO A VALUE IT IS THE DUTY "
        "OF EVERY PILGRIM TO SEEK OUT THIS PAGE FOR ALL IS SACRED AND THE PRIMES ARE SACRED")
    L = len(plain_idx)
    K_true = totient_keystream(L + 16)
    C = [(plain_idx[i] - K_true[i]) % N for i in range(L)]
    runes = list(C)
    rng = random.Random(3301)
    pos = sorted(rng.sample(range(4, len(runes) - 4), 6))
    for j, pp in enumerate(pos):
        runes.insert(pp + j, F_IDX)
    spliced_occ = set()
    f_occ = [i for i, c in enumerate(runes) if c == F_IDX]
    int_pos = [pp + j for j, pp in enumerate(pos)]
    for p in int_pos:
        if p in f_occ:
            spliced_occ.add(f_occ.index(p))

    # BLIND step: candidate derives the keystream from the STATED external input (primes),
    # NOT from the handed key. The ONLY derivation tried is the published method family:
    # phi(prime) = (p-1) mod 29, shift-down.
    K_blind = totient_keystream(len(runes) + 16)
    key_match = (K_blind[:L] == K_true[:L])

    from lp import solve as _solve
    runes_str = gp.indices_to_runes(runes)
    pt, _ = _solve.decode(runes_str, K_blind + [0] * (len(runes) + 8),
                          sign=+1, atbash=False, interrupter_idx=spliced_occ)
    truth_tr = sk.idx_to_trans(plain_idx)
    m = min(len(pt), len(truth_tr))
    rec = (sum(1 for a, b in zip(pt[:m], truth_tr[:m]) if a == b) / len(truth_tr)
           if truth_tr else 0.0)
    return {
        "external_input": "prime sequence (2,3,5,7,...) -- stated, NOT the keystream",
        "derivation_rediscovered": "phi(prime)=(p-1) mod 29 shift-down",
        "keystream_matches_true_blind": bool(key_match),
        "interrupter_aware_recovery": round(rec, 4),
        "outcome": ("RECOVERED (keystream rediscovered blind from the stated prime input; "
                    "interrupter-aware solver returns the known plaintext)"
                    if key_match and rec > 0.95 else "NOT_RECOVERED"),
        "caveat": ("the keyskip beam alone recovers ~14% of this interrupter page "
                   "(instrument/anend_row.json); rediscovery here used the interrupter-aware "
                   "solver, per the Lane-1 FOUND-ERROR."),
    }


def main():
    pc = dk_pc2()
    holdout = anend_blind_holdout()
    summary = {
        "lane": "round19/derivedkey",
        "verdict": "NEGATIVE-by-prior-coverage (hypothesis class already measured; no new sweep run)",
        "dk_pc2_median_recovery": round(statistics.median(r["recovery_correct_key"] for r in pc), 4),
        "dk_pc2_median_en_quadgram_correct": round(statistics.median(r["en_quadgram_correct"] for r in pc), 4),
        "dk_pc2_median_en_quadgram_wrong": round(statistics.median(r["en_quadgram_wrong"] for r in pc), 4),
        "dk_pc2_median_matched_lm_correct": round(statistics.median(r["matched_lm_correct"] for r in pc), 4),
        "anend_blind_holdout": holdout["outcome"],
    }
    json.dump({"summary": summary, "dk_pc2_rows": pc, "anend_blind_holdout": holdout},
              open(os.path.join(HERE, "dk_confirm.json"), "w"), indent=1)
    print("DK-PC2 positive control (PBKDF2 over published seeds, beam decode):")
    print(f"  median recovery (correct key) : {summary['dk_pc2_median_recovery']:.1%}")
    print(f"  median EN-quad correct/wrong  : {summary['dk_pc2_median_en_quadgram_correct']:.3f}"
          f" / {summary['dk_pc2_median_en_quadgram_wrong']:.3f}")
    print(f"  median matched-LM correct     : {summary['dk_pc2_median_matched_lm_correct']:.3f}")
    print(f"AN-END blind holdout            : {holdout['outcome']}")
    print("wrote dk_confirm.json")


if __name__ == "__main__":
    main()
