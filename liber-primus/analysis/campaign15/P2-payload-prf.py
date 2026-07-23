#!/usr/bin/env python3
"""
Campaign XV, Probe P2 -- pp49-51 base-60 payload as a PRF / stream-cipher SEED.

Prior work (Campaign VII/IX/XI/XII) used the 256-byte payload DIRECTLY as a
polyalphabetic key over the runic pages -> clean null. This probe never uses the
payload directly: it EXPANDS the payload into a full-length mod-29 keystream via
standard stream-cipher / PRF constructions, then decrypts all 55 unsolved pages.

Generators : RC4, AES-128-CTR, AES-256-CTR, SHA-256/SHA-1/MD5 (counter + chain),
             HMAC-DRBG(SHA-256)
Reductions : byte mod 29 ; rejection (>=232 discard) mod 29 ; 16-bit word mod 29
Decrypt    : subtract & add ; per-page & continuous ; seed forward & reversed ;
             ciphertext +/- Atbash
Gate       : decrypt score_norm > -5.2  OR  decrypt IoC*N > 1.3  => SOLVE
             else -> null-closed.

Includes a synthetic self-validation: plant a payload-seeded RC4 keystream over
real English, confirm the pipeline recovers it (English band) and a wrong seed
scores in noise.
"""
import sys, os, hashlib, hmac
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp, stats, score, ciphers

N = gp.N  # 29
S = score.default()
RUNE = gp.RUNE_TO_IDX

# ---------------------------------------------------------------- load stream
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
pages_raw = [p for p in raw.split("%") if any(ch in RUNE for ch in p)]
body_pages = pages_raw[:-2]
page_idx = [[RUNE[c] for c in p if c in RUNE] for p in body_pages]
stream = [i for pg in page_idx for i in pg]
L = len(stream)

PAYLOAD = open(os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin"), "rb").read()
assert len(PAYLOAD) == 256, len(PAYLOAD)

NEED_BYTES = 40000  # generous: >= 2*L for 16-bit-word reduction

# ---------------------------------------------------------------- generators
def gen_rc4(seed, nbytes):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + seed[i % len(seed)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    out = bytearray(); i = j = 0
    while len(out) < nbytes:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xFF])
    return bytes(out)

def _aes_ctr(key, nonce, nbytes):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    c = Cipher(algorithms.AES(key), modes.CTR(nonce))
    e = c.encryptor()
    return e.update(b"\x00" * nbytes) + e.finalize()

def gen_aes128(seed, nbytes):
    return _aes_ctr(seed[:16], seed[16:32], nbytes)

def gen_aes256(seed, nbytes):
    return _aes_ctr(seed[:32], seed[32:48], nbytes)

def _hash_counter(seed, nbytes, algo):
    out = bytearray(); ctr = 0
    while len(out) < nbytes:
        h = hashlib.new(algo)
        h.update(seed); h.update(ctr.to_bytes(8, "big"))
        out += h.digest(); ctr += 1
    return bytes(out[:nbytes])

def _hash_chain(seed, nbytes, algo):
    out = bytearray(); st = hashlib.new(algo, seed).digest()
    while len(out) < nbytes:
        out += st
        st = hashlib.new(algo, seed + st).digest()
    return bytes(out[:nbytes])

def gen_sha256_ctr(s, n): return _hash_counter(s, n, "sha256")
def gen_sha256_chn(s, n): return _hash_chain(s, n, "sha256")
def gen_sha1_ctr(s, n):   return _hash_counter(s, n, "sha1")
def gen_sha1_chn(s, n):   return _hash_chain(s, n, "sha1")
def gen_md5_ctr(s, n):    return _hash_counter(s, n, "md5")
def gen_md5_chn(s, n):    return _hash_chain(s, n, "md5")

def gen_hmac_drbg(seed, nbytes):
    # NIST SP800-90A HMAC-DRBG (SHA-256), no reseed
    K = b"\x00" * 32; V = b"\x01" * 32
    def upd(data):
        nonlocal K, V
        K = hmac.new(K, V + b"\x00" + data, hashlib.sha256).digest()
        V = hmac.new(K, V, hashlib.sha256).digest()
        if data:
            K = hmac.new(K, V + b"\x01" + data, hashlib.sha256).digest()
            V = hmac.new(K, V, hashlib.sha256).digest()
    upd(seed)
    out = bytearray()
    while len(out) < nbytes:
        V = hmac.new(K, V, hashlib.sha256).digest()
        out += V
        upd(b"")
    return bytes(out[:nbytes])

GENERATORS = {
    "RC4": gen_rc4,
    "AES128CTR": gen_aes128,
    "AES256CTR": gen_aes256,
    "SHA256ctr": gen_sha256_ctr,
    "SHA256chn": gen_sha256_chn,
    "SHA1ctr": gen_sha1_ctr,
    "SHA1chn": gen_sha1_chn,
    "MD5ctr": gen_md5_ctr,
    "MD5chn": gen_md5_chn,
    "HMACDRBG": gen_hmac_drbg,
}

# ---------------------------------------------------------------- reductions
def red_byte(b):
    return [x % N for x in b]

def red_reject(b):
    return [x % N for x in b if x < 232]  # 232 = 8*29, unbiased

def red_word(b):
    return [((b[i] << 8) | b[i + 1]) % N for i in range(0, len(b) - 1, 2)]

REDUCTIONS = {"byte": red_byte, "reject": red_reject, "word": red_word}

# ---------------------------------------------------------------- decrypt/score
def score_idx(idxs):
    return S.score_norm(gp.indices_to_translit(idxs))

def decrypt_continuous(cipher, ks, sign):
    return [(cipher[i] + sign * ks[i]) % N for i in range(len(cipher))]

def decrypt_perpage(pages, ks, sign):
    out = []
    for pg in pages:
        out += [(c + sign * ks[i]) % N for i, c in enumerate(pg)]
    return out

def evaluate(pages_or_stream, ks, sign, per_page):
    if per_page:
        # need ks at least max page length; reset each page from ks[0]
        if len(ks) < max(len(p) for p in pages_or_stream):
            return None
        dec = decrypt_perpage(pages_or_stream, ks, sign)
    else:
        if len(ks) < L:
            return None
        dec = decrypt_continuous(stream, ks, sign)
    return dec

# ---------------------------------------------------------------- run sweep
def run_sweep(verbose=True):
    best = {"score": -999.0, "cfg": None, "ioc": 0.0}
    best_ioc = {"ioc": 0.0, "cfg": None, "score": -999.0}
    rows = []
    seeds = {"fwd": PAYLOAD, "rev": PAYLOAD[::-1]}
    # atbash variants of the ciphertext
    atbash_stream = ciphers.atbash_indices(stream)
    atbash_pages = [ciphers.atbash_indices(p) for p in page_idx]

    n_cfg = 0
    for gname, gfn in GENERATORS.items():
        for sname, seed in seeds.items():
            rawks = gfn(seed, NEED_BYTES)
            for rname, rfn in REDUCTIONS.items():
                ks = rfn(rawks)
                for atb in (False, True):
                    cont_ct = atbash_stream if atb else stream
                    page_ct = atbash_pages if atb else page_idx
                    for sign in (-1, +1):
                        for per_page in (False, True):
                            if per_page:
                                if len(ks) < max(len(p) for p in page_ct):
                                    continue
                                dec = decrypt_perpage(page_ct, ks, sign)
                            else:
                                if len(ks) < L:
                                    continue
                                dec = [(cont_ct[i] + sign * ks[i]) % N for i in range(L)]
                            n_cfg += 1
                            sc = score_idx(dec)
                            io = stats.ioc_norm(dec)
                            cfg = f"{gname}/{sname}/{rname}/atb={atb}/sign={sign:+d}/{'perpage' if per_page else 'cont'}"
                            if sc > best["score"]:
                                best = {"score": sc, "cfg": cfg, "ioc": io}
                            if io > best_ioc["ioc"]:
                                best_ioc = {"ioc": io, "cfg": cfg, "score": sc}
    if verbose:
        print(f"configs evaluated: {n_cfg}")
        print(f"BEST score : {best['score']:.4f}  IoC*N={best['ioc']:.4f}  [{best['cfg']}]")
        print(f"BEST IoC*N : {best_ioc['ioc']:.4f}  score={best_ioc['score']:.4f}  [{best_ioc['cfg']}]")
    return best, best_ioc, n_cfg

# ---------------------------------------------------------------- synthetic validation
def synthetic_validation():
    print("--- SYNTHETIC VALIDATION ---")
    eng = ("WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOT"
           "ANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONEALONGTHEWAY"
           "YOUWILLFINDANENDTOALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURILLUSIONS"
           "YOURCERTAINTYANDYOURREALITY")
    pt = gp.keyword_to_indices(eng)
    pt = (pt * ((L // len(pt)) + 1))[:L]
    base = score_idx(pt)
    # encrypt with RC4(payload) byte-mod29, continuous, sign convention C = P + K
    ks = red_byte(gen_rc4(PAYLOAD, NEED_BYTES))
    ct = [(pt[i] + ks[i]) % N for i in range(L)]
    ct_sc = score_idx(ct)
    ct_ioc = stats.ioc_norm(ct)
    # recover with correct pipeline: P = C - K
    rec = [(ct[i] - ks[i]) % N for i in range(L)]
    rec_sc = score_idx(rec)
    rec_ioc = stats.ioc_norm(rec)
    # wrong seed
    wrong_ks = red_byte(gen_rc4(bytes(reversed(bytearray(hashlib.sha256(PAYLOAD).digest()*8))), NEED_BYTES))
    wrong = [(ct[i] - wrong_ks[i]) % N for i in range(L)]
    wrong_sc = score_idx(wrong)
    print(f"  plaintext English score   : {base:.4f}  (IoC*N={stats.ioc_norm(pt):.3f})")
    print(f"  ciphertext (encrypted)    : {ct_sc:.4f}  (IoC*N={ct_ioc:.3f})  <- should be noise/flat")
    print(f"  recovered (correct seed)  : {rec_sc:.4f}  (IoC*N={rec_ioc:.3f})  <- should == plaintext")
    print(f"  recovered (WRONG seed)    : {wrong_sc:.4f}  <- should be noise")
    ok = (abs(rec_sc - base) < 1e-6) and (ct_sc < -5.2) and (wrong_sc < -5.2)
    print(f"  VALIDATION {'PASS' if ok else 'FAIL'}")
    return ok, dict(plain=base, cipher=ct_sc, recovered=rec_sc, wrong=wrong_sc)

if __name__ == "__main__":
    print("="*72)
    print(f"P2-payload-prf : {len(page_idx)} pages, {L} runes; payload {len(PAYLOAD)}B")
    print(f"baseline ciphertext IoC*N={stats.ioc_norm(stream):.4f} doublet={stats.doublet_rate(stream):.4f}")
    print("="*72)
    vok, vinfo = synthetic_validation()
    print("="*72)
    best, best_ioc, ncfg = run_sweep()
    print("="*72)
    solved = (best["score"] > -5.2) or (best_ioc["ioc"] > 1.3)
    print(f"GATE: score>-5.2 OR IoC*N>1.3  =>  {'*** SOLVE ***' if solved else 'NULL (no signal)'}")
