#!/usr/bin/env python3
"""
P7 — LP2-AS-PAD INVERSION (Campaign XV)

Hypothesis: the unsolved LP2 pages are NOT a message but the RANDOM KEYSTREAM
(a one-time pad). If so, the plaintext lives in some OTHER Cicada object,
enciphered under LP2. Use the 12,956-rune LP2 stream as a RUNNING KEY against
every machine-readable counterpart object in the repo.

Key variants : forward, reversed, atbash(28-k) of each  -> 4 keys
Combine ops  : plain = (target - key) mod 29   and   (target + key) mod 29
Offsets      : slide the (short) counterpart across the full LP2 stream.

Two scoring families:
  (F1) 29-symbol / rune-native: map counterpart -> mod-29, quadgram score_norm
       (via translit) + IoC*N on the residue.  Gate: score_norm > -5.2 or IoC*N > 1.3.
  (F2) byte-native (byte targets only): key = raw rune value (0..28),
       plain_byte = (cipher_byte -/+ keyrune) mod 256. Check printable-ASCII
       fraction and container magic bytes at each decrypt's offset-0.
       Gate: printable frac > 0.90 or a valid magic signature.

Random baselines: mod-29 residue IoC*N ~ 1.0, score_norm ~ -6.0;
random-byte printable fraction ~ 0.37.
"""
import sys, os
sys.path.insert(0, 'src')
import numpy as np
from lp import gematria as gp, stats, score

N = gp.N  # 29
RUNE = gp.RUNE_TO_IDX
Q = score.default()

# ---------- LP2 keystream ----------
raw = open('data/krisyotam_runes.txt', encoding='utf-8').read()
pages_raw = [p for p in raw.split('%') if any(ch in RUNE for ch in p)]
body_pages = pages_raw[:-2]
stream = [RUNE[c] for p in body_pages for c in p if c in RUNE]
KEY = np.array(stream, dtype=np.int64)
KLEN = len(KEY)
assert KLEN == 12956, f"LP2 stream len {KLEN} != 12956"

KEY_ATB = (N - 1 - KEY) % N
KEY_FWD = KEY
KEY_REV = KEY[::-1].copy()
KEY_REV_ATB = (N - 1 - KEY_REV) % N
KEYVARS = {
    'fwd': KEY_FWD, 'fwd_atbash': KEY_ATB,
    'rev': KEY_REV, 'rev_atbash': KEY_REV_ATB,
}

TRANS = gp.IDX_TO_TRANS  # idx -> translit string

def translit(idxs):
    return "".join(TRANS[int(i)] for i in idxs)

def iocN_np(arr):
    n = len(arr)
    if n < 2: return 0.0
    c = np.bincount(arr, minlength=N).astype(np.float64)
    return (c * (c - 1)).sum() / (n * (n - 1)) * N

def iocN_rows(res):
    """Vectorized IoC*N per row of an (n_off, L) residue matrix."""
    n_off, L = res.shape
    if L < 2:
        return np.zeros(n_off)
    counts = np.zeros((n_off, N), dtype=np.float64)
    for v in range(N):
        counts[:, v] = (res == v).sum(axis=1)
    return (counts * (counts - 1)).sum(axis=1) / (L * (L - 1)) * N

# ---------- counterpart loaders -> mod-29 index arrays ----------
def bytes_to_mod29(b):
    return np.frombuffer(b, dtype=np.uint8).astype(np.int64) % N

B32 = "abcdefghijklmnopqrstuvwxyz234567"
def onion_to_mod29(s):
    return np.array([B32.index(c) % N for c in s if c in B32], dtype=np.int64)

def load_hex_bytes(path):
    return bytes.fromhex(open(path).read().strip())

def load_pgp_bytes(path):
    """Extract the base64 payload from an ASCII-armored PGP block -> raw bytes."""
    import base64
    lines = open(path, encoding='utf-8', errors='ignore').read().splitlines()
    body, in_block, seen_blank = [], False, False
    for ln in lines:
        ls = ln[2:] if ln.startswith('- ') else ln  # undo PGP dash-space escaping
        if ls.startswith('-----BEGIN') and ls.rstrip().endswith('-----'):
            in_block, seen_blank, body = True, False, []
            continue
        if ls.startswith('-----END') and ls.rstrip().endswith('-----'):
            break
        if in_block:
            ln = ls
            if not seen_blank:
                if ln.strip() == '':
                    seen_blank = True
                continue
            if ln.startswith('='):  # checksum line -> stop
                break
            body.append(ln.strip())
    b64 = ''.join(body)
    if not b64:
        return None
    try:
        return base64.b64decode(b64 + '===')
    except Exception:
        return None

# ---------- assemble targets ----------
targets = []  # (name, mod29_array, raw_bytes_or_None)

# byte targets
for nm, path in [('canon_256', 'analysis/pp49_51/canon_256.bin'),
                 ('canon_256_decpref', 'analysis/pp49_51/canon_256_decpref.bin')]:
    b = open(path, 'rb').read()
    targets.append((nm, bytes_to_mod29(b), b))

anend = load_hex_bytes('analysis/armada20/key_anend_hash.txt')
targets.append(('anend_hash64', bytes_to_mod29(anend), anend))

# onions (rune-space, no byte family)
for nm, s in [('onion_ky2khlqdf7qdznac', 'ky2khlqdf7qdznac'),
              ('onion_xsxnaksict6egxkq', 'xsxnaksict6egxkq')]:
    targets.append((nm, onion_to_mod29(s), None))

# PGP/armored byte bodies: any pgp_ file with a decodable armored payload.
for f in sorted(os.listdir('analysis/armada20')):
    if not f.startswith('pgp_') or not f.endswith('.txt'):
        continue
    b = load_pgp_bytes(os.path.join('analysis/armada20', f))
    if b and len(b) >= 8:
        targets.append(('pgp_' + f[4:-4], bytes_to_mod29(b), b))

# ---------- magic byte signatures ----------
# Only signatures >= 4 bytes count as evidence. A 1-2 byte "magic" over ~100k
# offset trials is statistically inevitable noise (0xc1 alone: 1/256 -> ~400
# expected hits) and is NOT a container. We therefore require length >= 4.
MAGICS = [
    (b'PK\x03\x04', 'zip'), (b'PK\x05\x06', 'zip-empty'),
    (b'\xfd7zXZ\x00', 'xz'), (b'7z\xbc\xaf\x27\x1c', '7z'),
    (b'\x89PNG\r\n\x1a\n', 'png'), (b'GIF87a', 'gif'), (b'GIF89a', 'gif'),
    (b'%PDF-', 'pdf'), (b'Rar!\x1a\x07', 'rar'), (b'OggS', 'ogg'),
    (b'\x00\x00\x01\x00', 'ico'), (b'\x7fELF', 'elf'), (b'ustar', 'tar'),
]
MAGICS = [(s, t) for (s, t) in MAGICS if len(s) >= 4]

def printable_frac(b):
    a = np.frombuffer(b, dtype=np.uint8)
    ok = ((a >= 32) & (a <= 126)) | (a == 9) | (a == 10) | (a == 13)
    return ok.mean()

# ============================================================
# FAMILY 1 — mod-29 running-key decrypt, quadgram + IoC*N
# ============================================================
# Quadgram is scored only on the TOP_K highest-IoC offsets per (keyvar,op).
# Rationale: an English decrypt has IoC*N ~1.7-2.0, far above the flat OTP floor
# (~1.0), so any real plaintext is guaranteed to appear among the top-IoC rows.
# IoC is computed exactly on ALL offsets (vectorized); quadgram on survivors.
TOP_K = 60

def _search(tgt, keyvars):
    """Core search over offsets/ops/key-variants. Returns
    (best_score, score_loc, best_iocN, ioc_loc)."""
    L = len(tgt)
    n_off = KLEN - L + 1
    best_score, score_loc = -999.0, None
    best_ioc, ioc_loc = 0.0, None
    for kname, kv in keyvars.items():
        win = np.lib.stride_tricks.sliding_window_view(kv, L)  # (n_off, L)
        for op, sign in (('sub', -1), ('add', +1)):
            res = (tgt[None, :] + sign * win) % N
            iocs = iocN_rows(res)
            j = int(iocs.argmax())
            if iocs[j] > best_ioc:
                best_ioc = float(iocs[j]); ioc_loc = (kname, op, j)
            k = min(TOP_K, n_off)
            cand = np.argpartition(-iocs, k - 1)[:k]
            for i in cand:
                s = Q.score_norm(translit(res[int(i)]))
                if s > best_score:
                    best_score = s; score_loc = (kname, op, int(i))
    return best_score, score_loc, best_ioc, ioc_loc

def family1(name, tgt):
    L = len(tgt)
    if L < 4 or L > KLEN:
        return None
    bs, sl, bi, il = _search(tgt, KEYVARS)
    return {'score': bs, 'score_loc': sl, 'iocN': bi, 'ioc_loc': il,
            'L': L, 'n_off': KLEN - L + 1}

def search_max(tgt, keyvars):
    bs, _, bi, _ = _search(tgt, keyvars)
    return bs, bi

def null_calibration(tgt, n_shuf=5, seed=1234):
    """Best-of-search statistic under shuffled LP2 keys -> the null band for the
    same multiple-testing search. A real break must EXCEED this band."""
    rng = np.random.default_rng(seed)
    ss, ii = [], []
    for _ in range(n_shuf):
        perm = KEY.copy(); rng.shuffle(perm)
        pa = (N - 1 - perm) % N
        pr = perm[::-1].copy()
        kv = {'a': perm, 'b': pa, 'c': pr, 'd': (N - 1 - pr) % N}
        s, i = search_max(tgt, kv)
        ss.append(s); ii.append(i)
    return (max(ss), np.mean(ss), max(ii), np.mean(ii))

# ============================================================
# FAMILY 2 — byte-native decrypt (byte targets only)
# ============================================================
def family2(name, rawb):
    b = np.frombuffer(rawb, dtype=np.uint8).astype(np.int64)
    L = len(b)
    n_off = KLEN - L + 1
    best = {'pfrac': 0.0, 'magic': None, 'magic_loc': None, 'pfrac_loc': None}
    for kname, kv in KEYVARS.items():
        win = np.lib.stride_tricks.sliding_window_view(kv, L)
        for op, sign in (('sub', -1), ('add', +1)):
            res = ((b[None, :] + sign * win) % 256).astype(np.uint8)  # (n_off, L)
            a = res
            ok = ((a >= 32) & (a <= 126)) | (a == 9) | (a == 10) | (a == 13)
            pf = ok.mean(axis=1)
            j = int(pf.argmax())
            if pf[j] > best['pfrac']:
                best['pfrac'] = float(pf[j]); best['pfrac_loc'] = (kname, op, j)
            # magic: check offset-0 of each decrypt row
            head = res[:, :8].tobytes()  # not per-row convenient; loop cheaply
            for sig, tag in MAGICS:
                sl = len(sig)
                if sl > L: continue
                sigarr = np.frombuffer(sig, dtype=np.uint8)
                m = (res[:, :sl] == sigarr[None, :]).all(axis=1)
                if m.any():
                    idx = int(np.argmax(m))
                    best['magic'] = tag; best['magic_loc'] = (kname, op, idx)
    return best

# ============================================================
# RUN
# ============================================================
print(f"LP2 keystream: {KLEN} runes. Targets: {len(targets)}")
print("="*72)
GATE_FIRED = False
rows = []
for name, tgt, rawb in targets:
    f1 = family1(name, tgt)
    nc = null_calibration(tgt)  # (max_score, mean_score, max_ioc, mean_ioc)
    line = f"{name:34s} L={f1['L']:4d}  best_score_norm={f1['score']:7.3f}  best_iocN={f1['iocN']:6.3f}"
    print(line)
    print(f"    score@{f1['score_loc']}   ioc@{f1['ioc_loc']}")
    print(f"    NULL (shuffled-key best): score max={nc[0]:7.3f} mean={nc[1]:7.3f} | iocN max={nc[2]:6.3f} mean={nc[3]:6.3f}")
    # A genuine break must EXCEED the shuffled-key max (calibrated for the same
    # multiple-testing search), not merely a fixed threshold.
    score_exceeds = f1['score'] > max(-5.2, nc[0])
    ioc_exceeds = f1['iocN'] > max(1.3, nc[2])
    fired = score_exceeds or ioc_exceeds
    rec = dict(name=name, L=f1['L'], score=f1['score'], iocN=f1['iocN'],
               score_loc=f1['score_loc'], ioc_loc=f1['ioc_loc'],
               null_score_max=nc[0], null_ioc_max=nc[2],
               score_exceeds=bool(score_exceeds), ioc_exceeds=bool(ioc_exceeds),
               pfrac=None, magic=None)
    if rawb is not None:
        f2 = family2(name, rawb)
        rec['pfrac'] = f2['pfrac']; rec['magic'] = f2['magic']
        print(f"    byte: max_printable_frac={f2['pfrac']:.4f} @{f2['pfrac_loc']}  magic(>=4B)={f2['magic']} @{f2['magic_loc']}")
        fired = fired or (f2['pfrac'] > 0.90) or (f2['magic'] is not None)
    if fired:
        GATE_FIRED = True
        print("    *** GATE FIRED (exceeds calibrated null) ***")
    else:
        print("    null: within shuffled-key band")
    rows.append(rec)
    print("-"*72)

print("="*72)
print("SIGNAL_FIRED =", GATE_FIRED)
best_score = max(r['score'] for r in rows)
best_ioc = max(r['iocN'] for r in rows)
best_pf = max((r['pfrac'] for r in rows if r['pfrac'] is not None), default=None)
print(f"GLOBAL best score_norm = {best_score:.3f}  (threshold > -5.2)")
print(f"GLOBAL best IoC*N      = {best_ioc:.3f}  (threshold > 1.3)")
print(f"GLOBAL best printable  = {best_pf}  (threshold > 0.90)")
print("VERDICT:", "BREAK" if GATE_FIRED else "NULL-CLOSED")
