"""RED TEAM: attack the ASSUMPTIONS, not the ciphertext.

Every prior campaign analysed the bulk rune stream read straight, as a keyed
substitution of English. This attacks the premises that were never verified:

  A. SERIALIZATION  -- maybe the runes aren't read L->R/top->bottom/page-order.
     Test reversed, per-page-reversed, and boustrophedon (alternating line dir);
     recompute doublet rate + best monoalphabetic English fit on each.
  B. SELECTION / ACROSTIC -- maybe the message is a SUBSEQUENCE and the bulk is
     chaff (invisible to every cipher attack). Extract first/last rune of each
     line / word / page, diagonal reads, prime-position reads, and score them
     both as PLAINTEXT and as a candidate Vigenere KEY over the pages.
  C. UNIT / BITSTREAM -- maybe each rune carries one bit (parity / prime-vs-
     composite value). Extract the bitstream, repack to bytes, look for ASCII.

Anything scoring near English (score_norm ~ -2.2; noise < -4) is a real lead.
Reproduce: PYTHONUTF8=1 python analysis/red_team.py
"""
import os, sys
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp
from lp import score as _score

N = 29
SC = _score.default()
RUNES = set(gp.RUNE_TO_IDX)

def parse():
    """Return structured pages: list of pages; page = list of lines; line = list
    of rune indices. Also flat pooled stream. Drops the 2 solved trailing pages."""
    raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages = []
    for seg in raw.split("%"):
        lines = []
        for ln in seg.split("/"):
            ix = [gp.RUNE_TO_IDX[c] for c in ln if c in gp.RUNE_TO_IDX]
            if ix:
                lines.append(ix)
        if lines:
            pages.append(lines)
    return pages[:-2]

def doublet(seq):
    return sum(1 for a, b in zip(seq, seq[1:]) if a == b) / max(1, len(seq) - 1)

def best_mono(seq):
    """best single-shift (Caesar) + atbash English fit -- cheap OTP-vs-lead check."""
    best = -99
    for atb in (False, True):
        s0 = [(N - 1 - x) if atb else x for x in seq]
        for sh in range(N):
            t = gp.indices_to_translit([(x - sh) % N for x in s0])
            best = max(best, SC.score_norm(t))
    return best

def as_key_over_pages(key, pages_flat):
    """score using `key` as a repeating Vigenere key over each page; best page."""
    if len(key) < 3:
        return -99
    best = -99
    for pg in pages_flat:
        for sign in (-1, 1):
            pt = [(pg[i] - sign * key[i % len(key)]) % N for i in range(len(pg))]
            best = max(best, SC.score_norm(gp.indices_to_translit(pt)))
    return best

def main():
    pages = parse()
    pages_flat = ["".join for _ in []]  # placeholder
    pages_flat = [[x for ln in pg for x in ln] for pg in pages]
    pooled = [x for pg in pages_flat for x in pg]
    print(f"red-team over {len(pages)} pages, {len(pooled)} runes")
    print(f"baseline: pooled doublet={100*doublet(pooled):.2f}%  mono-fit={best_mono(pooled):.2f}\n")

    leads = []

    # ---- A. serialization ----
    variants = {
        "reversed": pooled[::-1],
        "per-page-reversed": [x for pg in pages_flat for x in pg[::-1]],
    }
    # boustrophedon: reverse every other LINE
    bous = []
    flip = False
    for pg in pages:
        for ln in pg:
            bous += ln[::-1] if flip else ln
            flip = not flip
    variants["boustrophedon-line"] = bous
    print("A. SERIALIZATION")
    for name, seq in variants.items():
        d, m = 100 * doublet(seq), best_mono(seq)
        print(f"   {name:20} doublet={d:5.2f}%  mono-fit={m:.2f}")
        if m > -3.5:
            leads.append((m, f"serialization:{name}"))

    # ---- B. selection / acrostic ----
    sels = {}
    sels["first-of-line"]  = [pg[i][0]  for pg in pages for i in range(len(pg))]
    sels["last-of-line"]   = [pg[i][-1] for pg in pages for i in range(len(pg))]
    sels["first-of-page"]  = [pg[0][0]  for pg in pages]
    sels["first-line-per-page"] = [x for pg in pages for x in pg[0]]
    # first rune of each WORD needs word boundaries -> reparse with '-'
    raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    words = []
    for seg in raw.split("%")[:-2] if False else raw.split("%"):
        for ln in seg.replace("/", "-").split("-"):
            ix = [gp.RUNE_TO_IDX[c] for c in ln if c in gp.RUNE_TO_IDX]
            if ix:
                words.append(ix)
    sels["first-of-word"] = [w[0] for w in words]
    sels["last-of-word"]  = [w[-1] for w in words]
    # prime-position read (positions that are prime indices in the pooled stream)
    def is_prime(n):
        return n > 1 and all(n % k for k in range(2, int(n**0.5) + 1))
    sels["prime-positions"] = [pooled[i] for i in range(len(pooled)) if is_prime(i)]

    print("\nB. SELECTION / ACROSTIC  (as plaintext | as Vigenere key)")
    for name, seq in sels.items():
        if len(seq) < 4:
            continue
        pt = SC.score_norm(gp.indices_to_translit(seq))
        ky = as_key_over_pages(seq[:40], pages_flat)
        print(f"   {name:20} n={len(seq):4d}  plaintext={pt:6.2f}  as-key={ky:6.2f}")
        if pt > -3.5 or ky > -3.5:
            leads.append((max(pt, ky), f"selection:{name}"))

    # ---- C. bitstream ----
    print("\nC. BITSTREAM (1 bit/rune -> ASCII bytes)")
    def bits_to_ascii(bits):
        by = [bits[i:i+8] for i in range(0, len(bits) - 7, 8)]
        chars = [chr(int("".join(map(str, b)), 2)) for b in by]
        printable = sum(1 for c in chars if 32 <= ord(c) < 127) / max(1, len(chars))
        return "".join(c if 32 <= ord(c) < 127 else "." for c in chars), printable
    parity = [x & 1 for x in pooled]
    primev = [1 if gp.RUNE_TO_PRIME[gp.IDX_TO_RUNE[x]] and x in range(N) else 0 for x in pooled]
    # prime-vs-composite of the rune's Gematria prime is always prime; use value>median instead
    med = sorted(pooled)[len(pooled)//2]
    hi = [1 if x > med else 0 for x in pooled]
    for name, bits in [("parity", parity), ("value>median", hi)]:
        txt, pr = bits_to_ascii(bits)
        print(f"   {name:14} printable-ASCII={100*pr:4.0f}%  head={txt[:40]!r}")
        if pr > 0.9:
            leads.append((pr, f"bitstream:{name}"))

    print("\n" + "="*50)
    if leads:
        leads.sort(reverse=True)
        print("LEADS (above threshold — verify!):")
        for s, w in leads:
            print(f"   {s:.2f}  {w}")
    else:
        print("No assumption-attack crossed the English threshold.")
        print("Serialization, selection/acrostic, and bitstream framings are null:")
        print("the message is not a simple re-reading, subsequence, or 1-bit channel.")

if __name__ == "__main__":
    main()
