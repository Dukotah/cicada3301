#!/usr/bin/env python3
"""lp-try — test a key/method hypothesis against the unsolved Liber Primus pages.

For casual solvers: plug in a key + cipher and instantly see a scored, ranked
decrypt across all pages, with a built-in sanity gate so you don't fool yourself.

Examples:
  python lp_try.py --key DIVINITY                      # vigenere, subtract, interrupters
  python lp_try.py --key CIRCUMFERENCE --no-interrupt
  python lp_try.py --keystream totient                 # totient(prime) keystream
  python lp_try.py --key WISDOM --sign +1 --atbash
  python lp_try.py --selftest                          # prove the scorer/rig works

Scoring: english quadgram log10-prob per rune. Real English ≈ -2.2; random ≈ -4.5.
A real break jumps WELL above the unsolved baseline AND shows readable text — be
skeptical of small bumps (the pages are one-time-pad-class; see SOLVERS-DOSSIER.md).
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
from lp import gematria as gp                       # noqa: E402
from lp.ciphers import (vigenere_decrypt, transform_runes,       # noqa: E402
                        totient_stream, prime_stream)
from lp.score import Quadgram                       # noqa: E402

KRIS = os.path.join(HERE, "data", "krisyotam_runes.txt")
SCORER = Quadgram()


def pages():
    out = []
    for i, seg in enumerate(open(KRIS, encoding="utf-8").read().split("%")):
        runes = "".join(c for c in seg if c in gp.RUNE_TO_IDX)
        if runes:
            out.append((i, runes))
    return out


def score_per_rune(translit):
    n = sum(c.isalpha() for c in translit)
    return (SCORER.score(translit) / n) if n else -9.9


def decode(runes, args):
    if args.keystream:
        fn = {"totient": totient_stream, "prime": prime_stream}[args.keystream]
        out = transform_runes(runes, lambda L: fn(L), sign=args.sign,
                              interrupters=not args.no_interrupt, atbash=args.atbash)
    else:
        out = vigenere_decrypt(runes, args.key, sign=args.sign,
                               interrupters=not args.no_interrupt, atbash=args.atbash)
    # transform_runes returns (translit_text, interrupter_positions)
    return out[0] if isinstance(out, tuple) else out


def run(args):
    label = (f"keystream={args.keystream}" if args.keystream else f"key={args.key}")
    print(f"# lp-try  {label}  sign={'+' if args.sign>0 else '-'}  "
          f"interrupters={not args.no_interrupt}  atbash={args.atbash}\n")
    rows = []
    for i, runes in pages():
        out = decode(runes, args)
        rows.append((i, score_per_rune(out), out))
    rows.sort(key=lambda r: -r[1])
    # calibrated scale (space-less rune transliteration): plaintext ≈ -4.3,
    # ciphertext/noise ≈ -7.4. A real break lands near/above the plaintext level.
    BREAK = -5.0
    print(f"{'page':>4} {'score/rune':>10}   preview   (plaintext≈-4.3, ciphertext≈-7.4)")
    for i, s, out in rows[:8]:
        flag = "  <-- ENGLISH? verify!" if s > BREAK else ""
        print(f"{i:>4} {s:>10.3f}   {out[:50]}{flag}")
    best = rows[0]
    print(f"\nbest: page {best[0]} @ {best[1]:.3f}/rune. "
          f"{'LOOKS LIKE A LEAD — verify by eye!' if best[1] > BREAK else 'no break (expected: OTP-class).'}")


def selftest():
    """Prove the scorer + rig: the PARABLE page is plaintext -> should score English;
    an unsolved page should score like noise."""
    ps = dict(pages())
    # the last page is PARABLE (plaintext); transliterate directly (no cipher)
    last = sorted(ps)[-1]
    pl = "".join(gp.RUNE_TO_TRANS[c] for c in ps[last])
    s_plain = score_per_rune(pl)
    s_noise = score_per_rune("".join(gp.RUNE_TO_TRANS[c] for c in ps[0]))
    print(f"selftest: PARABLE plaintext page {last} score/rune = {s_plain:.3f}")
    print(f"          unsolved page 0 score/rune        = {s_noise:.3f}")
    print(f"          gap = {s_plain - s_noise:.3f} (plaintext should score MUCH higher)")
    ok = (s_plain - s_noise) > 2.0
    print("RESULT:", "PASS — scorer cleanly separates English from ciphertext" if ok else "CHECK")
    return ok


def main_cli():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", default="DIVINITY", help="vigenere keyword (default DIVINITY)")
    ap.add_argument("--keystream", choices=["totient", "prime"], help="use a numeric keystream instead of a key")
    ap.add_argument("--sign", type=int, default=-1, choices=[-1, 1], help="-1 subtract (default), +1 add")
    ap.add_argument("--no-interrupt", action="store_true", help="disable ᚠ interrupter handling")
    ap.add_argument("--atbash", action="store_true", help="apply atbash")
    ap.add_argument("--selftest", action="store_true", help="prove the scorer/rig works")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    run(a)


if __name__ == "__main__":
    main_cli()
