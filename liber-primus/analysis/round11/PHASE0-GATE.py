"""Round 11 Phase 0 — instrument validation gate.

Nothing in Phase 1/2 is trustworthy unless every check here PASSES:
  1. the value channel reproduces the 12,956-rune unsolved stream
  2. the cipher path decrypts the SOLVED AN END page (prime-totient keystream)
  3. the scorer separates English from noise, and the null band is calibrated
  4. the flagship N1 detector (cumulative-gematria plaintext-feedback autokey)
     RECOVERS a planted message and its wrong-config control does not
Run:  PYTHONUTF8=1 python3 PHASE0-GATE.py
Exit 0 = all pass.
"""
import sys, random
import lib_numchannel as nc
from lp import gematria as gp, ciphers

fail = 0
def check(name, ok, detail=""):
    global fail
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not ok: fail += 1

# 1. unsolved stream ---------------------------------------------------------
u = nc.unsolved()
check("unsolved stream = 12,956 runes", len(u) == 12956, f"got {len(u)}")

# 2. AN END decrypts via the prime-totient keystream -------------------------
ae = nc.anend()
ks = ciphers.prime_totient_stream(len(ae))
dec = nc.apply_keystream(ae, ks, sign=-1)
txt = "".join(gp.IDX_TO_TRANS[i] for i in dec)
check("AN END decrypts to English", txt.startswith("ANENDWITHINTHEDEEPWEB"), txt[:40])

# 3. scorer + null calibration ----------------------------------------------
# English plaintext (from the solved PARABLE page) must score well above the
# unsolved raw stream, which must sit in its own shuffled-null band.
parable = nc.segments()[-1]
s_eng = nc.eng_norm(parable)
s_raw = nc.eng_norm(u)
nmean, nmax, _ = nc.null_band(nc.eng_norm, u, n=60)
# runeglish transliteration scale: English ~ -4.0/-4.4, noise floor ~ -7.5
check("English (PARABLE) scores > -5.0", s_eng > -5.0, f"{s_eng:.3f}")
check("English/noise separation > 2.5", s_eng - nmean > 2.5,
      f"eng {s_eng:.3f} - noise {nmean:.3f} = {s_eng - nmean:.3f}")
check("raw unsolved is null-indistinguishable", s_raw <= nmax + 0.05,
      f"raw {s_raw:.3f} vs null max {nmax:.3f} (mean {nmean:.3f})")

# 4. N1 flagship positive control: cumulative-gematria plaintext-feedback -----
# key[i] = (sum of gematria primes of plaintext[0..i-1]) mod 29.
# encrypt c[i]=(p[i]+key[i])%29 ; decrypt recovers p left-to-right (self-keying).
def n1_encrypt(plain):
    c, run = [], 0
    for pi in plain:
        c.append((pi + (run % nc.N)) % nc.N)
        run += nc.PRIMES[pi]
    return c

def n1_decrypt(cipher):
    p, run = [], 0
    for ci in cipher:
        pi = (ci - (run % nc.N)) % nc.N
        p.append(pi)
        run += nc.PRIMES[pi]
    return p

# plant: real English (PARABLE, repeated to length) as plaintext
plant = (parable * 40)[:2000]
ct = n1_encrypt(plant)
rec = n1_decrypt(ct)
s_plant = nc.eng_norm(plant)
s_rec = nc.eng_norm(rec)
# wrong config: decode with a fixed offset instead of the feedback rule
wrong = [(ci - 7) % nc.N for ci in ct]
s_wrong = nc.eng_norm(wrong)
check("N1 encrypt hides the plaintext", nc.eng_norm(ct) < s_plant - 1.0,
      f"ct {nc.eng_norm(ct):.3f} vs plain {s_plant:.3f}")
check("N1 detector RECOVERS the plant exactly", rec == plant, f"rec_score {s_rec:.3f}")
check("N1 wrong-config stays noise", s_wrong < s_rec - 1.0,
      f"wrong {s_wrong:.3f} vs recovered {s_rec:.3f}")

print()
if fail:
    print(f"GATE FAILED — {fail} check(s) failed. Do not trust Phase 1 until fixed.")
    sys.exit(1)
print("GATE PASS — instrument validated. Phase 1 number-channel lenses may proceed.")
