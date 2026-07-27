"""KEY-TEST for T5-4gq25-2016: the OutGuess-extracted clearsigned PGP message
(analysis/armada_osint/extracts/T5-4gq25-2016.outguess.txt) as KEY / PAD /
CIPHERTEXT material over the LP2 runes.

Same rig as pp49_51/keytest.py: identical imports, identical calibrated scorer
(score_norm: ~-2.2 English text, -4.0 English baseline over runes, <-5.2 noise
floor). Additive / Beaufort / atbash, both signs, forward + reversed, per-page
offset sweep on short pages + whole corpus, plus XOR-class variants.

Payload byte-sources tried (a real key could be any of these views):
  raw    : all 1136 bytes of the file
  print  : the printable/ASCII bytes (same as raw here, it's 100% printable)
  body   : just the human message body between the header and signature
  b64dec : the base64 signature block decoded to raw bytes (the actual RSA sig)
Each reduced mod 29 for the additive/Beaufort/atbash families; raw byte values
used for the XOR-class family.
"""
import os, sys, base64
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline

N = gp.N
SC = _score.default()
THRESHOLD = -5.2
BASELINE = -4.0

def translit(idxs):
    return gp.indices_to_translit(idxs)

# ---- load payload byte-sources ----
PATH = os.path.join(HERE, "extracts", "T5-4gq25-2016.outguess.txt")
raw = open(PATH, "rb").read()
text = raw.decode("latin-1")

# body: between the blank line after "Hash:" header and the signature block
body = text
if "\n\n" in text:
    body = text.split("\n\n", 1)[1]
body = body.split("-----BEGIN PGP SIGNATURE-----")[0]
body_bytes = body.encode("latin-1")

# printable only
printable = bytes(b for b in raw if 32 <= b < 127)

# base64-decoded signature block
sig_b64 = ""
if "-----BEGIN PGP SIGNATURE-----" in text:
    blk = text.split("-----BEGIN PGP SIGNATURE-----", 1)[1]
    blk = blk.split("-----END PGP SIGNATURE-----", 1)[0]
    for ln in blk.splitlines():
        ln = ln.strip()
        if not ln or ":" in ln or ln.startswith("="):
            continue
        sig_b64 += ln
b64dec = b""
try:
    b64dec = base64.b64decode(sig_b64 + "===")
except Exception as e:
    print("b64 decode failed:", e)

SOURCES = {
    "raw":    list(raw),
    "print":  list(printable),
    "body":   list(body_bytes),
    "b64dec": list(b64dec),
}
print("=== payload byte-sources ===")
for k, v in SOURCES.items():
    print(f"  {k:8s} {len(v):5d} bytes")
print()

# ---- calibration anchors ----
pages = load_pages()
print("=== calibration (score_norm) ===")
print(f"  english baseline : {SC.score_norm(translit(english_baseline())):.3f}  (target for a real break)")
import random
rng = random.Random(3301)
rand_idx = [rng.randrange(N) for _ in range(6000)]
print(f"  random runes     : {SC.score_norm(translit(rand_idx)):.3f}  (noise floor)")
print(f"  BASELINE {BASELINE}   THRESHOLD {THRESHOLD}\n")

# unsolved pages = all but the last two solved (AN END / PARABLE)
unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
print(f"unsolved pages: {len(unsolved)}   total runes: {len(corpus)}\n")

def key_streams():
    """(name, key-as-mod29-list) for additive/Beaufort/atbash families."""
    for sname, bys in SOURCES.items():
        if not bys:
            continue
        base = [b % N for b in bys]
        yield f"{sname}", base
        yield f"{sname}-rev", base[::-1]

def xor_streams():
    """(name, raw-byte-list) for XOR-class family (values used mod 29 post-xor)."""
    for sname, bys in SOURCES.items():
        if not bys:
            continue
        yield f"{sname}", bys
        yield f"{sname}-rev", bys[::-1]

def decrypt_add(idxs, key, offset, sign, atbash, beaufort):
    L = len(idxs)
    stream = [key[(offset + i) % len(key)] for i in range(L)]
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    if beaufort:                      # p = k - c
        return [(stream[i] - c) % N for i, c in enumerate(src)]
    return ciphers.apply_stream_to_indices(src, stream, sign=sign)

def decrypt_xor(idxs, kbytes, offset, atbash):
    """XOR-class: xor rune index with key byte, reduce mod 29."""
    L = len(idxs)
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    return [(c ^ kbytes[(offset + i) % len(kbytes)]) % N for i, c in enumerate(src)]

results = []
def run_add(tname, idxs, sweep):
    for kname, key in key_streams():
        offs = range(min(len(key), 256)) if sweep else [0]
        for sign in (-1, +1):
            for atbash in (False, True):
                for beaufort in (False, True):
                    if beaufort and sign == +1:
                        continue
                    for off in offs:
                        p = decrypt_add(idxs, key, off, sign, atbash, beaufort)
                        sc = SC.score_norm(translit(p))
                        mode = f"{kname} sign{sign:+d}{' atbash' if atbash else ''}{' beaufort' if beaufort else ''} off{off}"
                        results.append((sc, tname, mode))

def run_xor(tname, idxs, sweep):
    for kname, kbytes in xor_streams():
        offs = range(min(len(kbytes), 256)) if sweep else [0]
        for atbash in (False, True):
            for off in offs:
                p = decrypt_xor(idxs, kbytes, off, atbash)
                sc = SC.score_norm(translit(p))
                results.append((sc, tname, f"XOR {kname}{' atbash' if atbash else ''} off{off}"))

for pi, p in enumerate(unsolved):
    sweep = (len(p) <= 400)   # every page qualifies; sweep offsets everywhere feasible
    run_add(f"page{pi}(len{len(p)})", p, sweep)
    run_xor(f"page{pi}(len{len(p)})", p, sweep)
run_add("CORPUS", corpus, sweep=False)
run_xor("CORPUS", corpus, sweep=False)

results.sort(reverse=True)
print("=== TOP 30 decryptions (score_norm, higher=more English) ===")
for sc, tname, mode in results[:30]:
    flag = ""
    if sc > BASELINE:
        flag = "  <-- ABOVE ENGLISH BASELINE"
    elif sc > THRESHOLD:
        flag = "  <-- above noise floor"
    print(f"  {sc:7.3f}  {tname:16s}  {mode}{flag}")

above_base = [r for r in results if r[0] > BASELINE]
above_thr = [r for r in results if r[0] > THRESHOLD]
print(f"\nconfigs tried: {len(results)}")
print(f"above ENGLISH BASELINE ({BASELINE}): {len(above_base)}")
print(f"above THRESHOLD ({THRESHOLD}): {len(above_thr)}")

# show plaintext of the single best hit for eyeball inspection
best = results[0]
print(f"\nBEST: {best[0]:.3f}  {best[1]}  {best[2]}")

if above_base:
    print("\nVERDICT: at least one config beats the English baseline -- inspect plaintext above.")
else:
    print("\nVERDICT: NO config beats the English baseline (-4.0). The PGP message does not")
    print("function as additive/Beaufort/atbash/XOR key, pad, or ciphertext over the LP2")
    print("runes, any byte-source, both signs, forward+reversed, per-page or corpus. Null.")
