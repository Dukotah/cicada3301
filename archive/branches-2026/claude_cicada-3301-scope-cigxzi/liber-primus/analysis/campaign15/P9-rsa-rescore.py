#!/usr/bin/env python3
"""P9-rsa-rescore  (Campaign XV)

Two cheap closers in one script.

(A) pp49-51 payload (analysis/pp49_51/canon_256.bin) tested as an RSA
    signature/ciphertext under the REAL Cicada 3301 public keys
    (fingerprint 6D854CD7933322A601C3286D181F01E57A35090F, e=65537),
    both moduli (primary + encryption subkey), both endiannesses,
    e in {65537,3,17}. For each s<n compute pow(s,e,n) and pattern-match
    PKCS#1 v1.5 (00 01 FF..FF 00 || DigestInfo) and PSS trailer 0xBC.
    Modulus recovered from analysis/campaign15/cicada_pubkey.asc (fetched
    from keyserver.ubuntu.com by keyid 0x181F01E57A35090F; fingerprint
    verified against the repo's KEY-HINT-RESEARCH.md).

(B) Language-agnostic re-scoring. Build rune-index-space quadgram models
    from Old English (data/keys/runepoem_oe.txt) and Latin
    (analysis/campaign15/latin_caesar.txt, Caesar De Bello Gallico) mapped
    through Gematria Primus, plus an English control (solved plaintext).
    Re-score running-key decrypts of the unsolved pages under OE/Latin,
    with decrypt IoC*N>1.3 as a language-blind gate. Any archived-style
    'null' scoring high under OE/Latin, or IoC*N>1.3, would be a MISSED HIT.
"""
import sys, os, re, base64, hashlib, json, math, random
sys.path.insert(0, 'src')
import numpy as np
from lp import gematria as gp
from lp import stats as st
sys.path.insert(0, 'analysis')
from run_stats import load_pages

N = gp.N
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # analysis/
REPO = os.path.dirname(ROOT)
def rp(*p): return os.path.join(REPO, *p)

# ======================================================================
# PROBE A : RSA
# ======================================================================
def parse_pgp_moduli(asc_path):
    txt = open(asc_path).read()
    m = re.search(r'-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END', txt, re.S)
    body = m.group(1)
    lines = [l for l in body.splitlines()
             if l and not l.startswith(('Version', 'Comment', 'Hash')) and not l.startswith('=')]
    data = base64.b64decode(''.join(lines))
    def packets(d):
        off = 0
        while off < len(d):
            c = d[off]; off += 1
            if c & 0x40:
                tag = c & 0x3f; l = d[off]; off += 1
                if l < 192: ln = l
                elif l < 224: ln = ((l-192) << 8) + d[off] + 192; off += 1
                else: ln = int.from_bytes(d[off:off+4], 'big'); off += 4
            else:
                tag = (c >> 2) & 0x0f; lt = c & 3
                if lt == 0: ln = d[off]; off += 1
                elif lt == 1: ln = int.from_bytes(d[off:off+2], 'big'); off += 2
                else: ln = int.from_bytes(d[off:off+4], 'big'); off += 4
            yield tag, d[off:off+ln]; off += ln
    def rd_mpi(b, o):
        bits = int.from_bytes(b[o:o+2], 'big'); o += 2
        nb = (bits + 7) // 8
        return int.from_bytes(b[o:o+nb], 'big'), o + nb, bits
    out = []
    for tag, b in packets(data):
        if tag in (6, 14):
            o = 6
            n, o, nbits = rd_mpi(b, o)
            e, o, ebits = rd_mpi(b, o)
            fpr = hashlib.sha1(b'\x99' + len(b).to_bytes(2, 'big') + b).hexdigest().upper()
            out.append({'tag': tag, 'n': n, 'e': e, 'n_bits': nbits, 'fpr': fpr, 'keyid': fpr[-16:]})
    return out

# DigestInfo DER prefixes (PKCS#1 v1.5) for common hashes
DIGESTINFO = {
    'SHA-1':   bytes.fromhex('3021300906052b0e03021a05000414'),
    'SHA-256': bytes.fromhex('3031300d060960864801650304020105000420'),
    'SHA-512': bytes.fromhex('3051300d060960864801650304020305000440'),
    'MD5':     bytes.fromhex('3020300c06082a864886f70d020505000410'),
}

def pkcs1_v15_match(block):
    # 00 01 FF..FF 00 || DigestInfo   (EMSA-PKCS1-v1_5)
    if len(block) < 11 or block[0] != 0x00 or block[1] != 0x01:
        return None
    i = 2
    while i < len(block) and block[i] == 0xFF:
        i += 1
    if i < 10 or i >= len(block) or block[i] != 0x00:
        return None
    rest = block[i+1:]
    for name, pref in DIGESTINFO.items():
        if rest.startswith(pref):
            return f'PKCS1v1.5/{name}'
    return f'PKCS1v1.5/pad-ok-unknown-digestinfo'

def pss_match(block):
    # EMSA-PSS encoded message ends in 0xBC
    if block and block[-1] == 0xBC:
        return 'PSS-trailer-0xBC'
    return None

def probe_A():
    payload = open(rp('analysis/pp49_51/canon_256.bin'), 'rb').read()
    assert len(payload) == 256
    moduli = parse_pgp_moduli(rp('analysis/campaign15/cicada_pubkey.asc'))
    results = {'payload_bytes': len(payload), 'payload_bits': len(payload)*8,
               'moduli': [], 'matches': [], 'tests_run': 0}
    hits = []
    for mod in moduli:
        n, e0 = mod['n'], mod['e']
        results['moduli'].append({'keyid': mod['keyid'], 'fpr': mod['fpr'],
                                  'n_bits': mod['n_bits'], 'e': e0})
        klen = (n.bit_length() + 7) // 8
        for endian in ('big', 'little'):
            s = int.from_bytes(payload, endian)
            for e in sorted({e0, 3, 17}):
                if s >= n:
                    continue
                t = pow(s, e, n)
                block = t.to_bytes(klen, 'big')
                results['tests_run'] += 1
                for tag, fn in (('pkcs1', pkcs1_v15_match), ('pss', pss_match)):
                    hit = fn(block)
                    if hit:
                        rec = {'keyid': mod['keyid'], 'endian': endian, 'e': e,
                               'scheme': hit, 'head': block[:16].hex()}
                        hits.append(rec)
                        results['matches'].append(rec)
    results['structural_note'] = (
        f"payload is {len(payload)} bytes = {len(payload)*8} bits; the only known "
        f"Cicada keys are 4096-bit (512-byte blocks). Payload is exactly half a "
        f"block, so it cannot be a genuine 4096-bit RSA signature/ciphertext; "
        f"pow() is still computed for every (n,e,endian) as a falsifiable test.")
    results['signal_fired'] = len(hits) > 0
    return results

# ======================================================================
# PROBE B : language-agnostic re-scoring
# ======================================================================
# text -> rune indices via Gematria Primus. Normalise archaic/OE/Latin glyphs.
def text_to_indices(s):
    s = s.upper()
    s = (s.replace('Þ', 'TH').replace('Ð', 'TH').replace('Ƿ', 'W')
          .replace('Æ', 'AE').replace('Œ', 'OE')
          .replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O')
          .replace('Ú','U').replace('Ý','Y').replace('J','I').replace('V','U'))
    letters = re.sub(r'[^A-Z]', '', s)
    return gp.keyword_to_indices(letters)

def build_qgram(indices, order=4):
    """Dense base-29 quadgram log10-prob table over rune indices."""
    size = N ** order
    counts = np.ones(size, dtype=np.float64)  # add-one smoothing
    idx = np.asarray(indices, dtype=np.int64)
    if len(idx) >= order:
        code = np.zeros(len(idx) - order + 1, dtype=np.int64)
        for k in range(order):
            code = code * N + idx[k:len(idx) - order + 1 + k]
        np.add.at(counts, code, 1.0)
    logp = np.log10(counts / counts.sum())
    return logp

def score_indices(p, QG, order=4):
    p = np.asarray(p, dtype=np.int64)
    if len(p) < order:
        return -999.0
    code = np.zeros(len(p) - order + 1, dtype=np.int64)
    for k in range(order):
        code = code * N + p[k:len(p) - order + 1 + k]
    return float(QG[code].mean())

def ioc_n(p):
    p = list(p)
    L = len(p)
    if L < 2:
        return 0.0
    from collections import Counter
    c = Counter(p)
    num = sum(v * (v - 1) for v in c.values())
    return (num / (L * (L - 1))) * N

def _iocn_rows(D, L):
    """Vectorised IoC*N for every row of D (noff,L)."""
    cnt = np.zeros((D.shape[0], N), dtype=np.int32)
    for sym in range(N):
        cnt[:, sym] = (D == sym).sum(axis=1)
    num = (cnt * (cnt - 1)).sum(axis=1).astype(np.float64)
    return num / (L * (L - 1)) * N

def best_running_key(cc_pages, key_idx, QGs, order=4, cap_off=1200, ioc_sample=160):
    """Scan offsets/signs/atbash for one keytext across all pages; score the
    SAME decrypt under every model in QGs (dict). Returns per-model best +
    global max IoC*N (language-blind gate)."""
    best = {m: {'score': -999.0, 'iocn': 0.0, 'plain': ''} for m in QGs}
    iocn_max = 0.0
    iocn_max_full = 0.0  # restricted to full-length pages (L>=200): low null variance
    K = np.asarray(key_idx, dtype=np.int64)
    M = len(K)
    for c in cc_pages:
        c = np.asarray(c, dtype=np.int64)
        L = len(c)
        if M < L + 1 or L < order:
            continue
        noff = min(M - L, cap_off)
        win = np.lib.stride_tricks.sliding_window_view(K, L)[:noff]  # (noff,L)
        for sign in (-1, 1):
            for atb in (False, True):
                cc = (N - 1 - c) if atb else c
                D = (cc[None, :] - sign * win) % N  # (noff,L)
                code = np.zeros((noff, L - order + 1), dtype=np.int64)
                for k in range(order):
                    code = code * N + D[:, k:L - order + 1 + k]
                for m, QG in QGs.items():
                    sc = QG[code].mean(axis=1)
                    o = int(np.argmax(sc))
                    if sc[o] > best[m]['score']:
                        dec = D[o]
                        best[m].update(score=float(sc[o]), iocn=float(ioc_n(dec)),
                                       plain=gp.indices_to_translit(dec.tolist())[:80])
                # language-blind IoC*N over a sample of offsets
                step = max(1, noff // ioc_sample)
                iv = _iocn_rows(D[::step], L)
                if iv.size:
                    iocn_max = max(iocn_max, float(iv.max()))
                    if L >= 200:
                        iocn_max_full = max(iocn_max_full, float(iv.max()))
    return best, iocn_max, iocn_max_full

def load_keytexts():
    files = []
    for pat in ('analysis/foundation/enoch_key.txt',
                'analysis/foundation/hermes_vol1_key.txt',
                'analysis/foundation/monas_clean_key.txt',
                'analysis/foundation/rosicrucian_fama_confessio_key.txt',
                'analysis/foundation/sephir_yetzirah_westcott_key.txt',
                'data/keys/solved_plaintext.txt',
                'data/keys/runepoem_oe.txt',
                'analysis/campaign15/latin_caesar.txt'):
        pth = rp(pat)
        if os.path.exists(pth):
            files.append((os.path.basename(pth), pth))
    return files

def probe_B():
    # reference corpora -> indices
    oe_idx = text_to_indices(open(rp('data/keys/runepoem_oe.txt'), encoding='utf-8', errors='ignore').read())
    lat_idx = text_to_indices(open(rp('analysis/campaign15/latin_caesar.txt'), encoding='utf-8', errors='ignore').read())
    en_idx = text_to_indices(open(rp('data/keys/solved_plaintext.txt'), encoding='utf-8', errors='ignore').read())
    QG = {'OE': build_qgram(oe_idx), 'LAT': build_qgram(lat_idx), 'EN': build_qgram(en_idx)}

    out = {'model_train_sizes': {'OE': len(oe_idx), 'LAT': len(lat_idx), 'EN': len(en_idx)},
           'calibration': {}, 'noise_band': {}, 'rescored': [], 'best_per_model': {},
           'iocn_max_seen': 0.0}

    # calibration: score reference texts under each model (self-hit vs cross vs random)
    rng = random.Random(3301)
    L_ref = 300
    rand_scores = {m: [] for m in QG}
    for _ in range(300):
        r = [rng.randrange(N) for _ in range(L_ref)]
        for m in QG:
            rand_scores[m].append(score_indices(r, QG[m]))
    for m in QG:
        arr = np.array(rand_scores[m])
        out['noise_band'][m] = {'rand_mean': round(float(arr.mean()), 3),
                                'rand_std': round(float(arr.std()), 3),
                                'threshold_4sig': round(float(arr.mean() + 4 * arr.std()), 3)}
    # self / cross calibration on a slice of each reference corpus
    for name, idx in (('OE_text', oe_idx), ('LAT_text', lat_idx), ('EN_text', en_idx)):
        seg = idx[1000:1000 + L_ref]
        out['calibration'][name] = {m: round(score_indices(seg, QG[m]), 3) for m in QG}

    # unsolved ciphertext pages
    pages = load_pages()[:-2]
    out['n_unsolved_pages'] = len(pages)
    out['n_unsolved_runes'] = sum(len(p) for p in pages)

    best_per_model = {m: {'score': -999.0, 'key': None, 'plain': ''} for m in QG}
    for kname, kpath in load_keytexts():
        raw = open(kpath, encoding='utf-8', errors='ignore').read()
        kidx = text_to_indices(raw)[:12000]
        if len(kidx) < 40:
            continue
        row = {'key': kname, 'key_len': len(kidx)}
        best, iocn_max, iocn_max_full = best_running_key(pages, kidx, QG)
        out['iocn_max_seen'] = max(out['iocn_max_seen'], iocn_max)
        out['iocn_max_full_seen'] = max(out.get('iocn_max_full_seen', 0.0), iocn_max_full)
        row['iocn_max'] = round(iocn_max, 3)
        row['iocn_max_full'] = round(iocn_max_full, 3)
        for m in QG:
            b = best[m]
            row[m] = {'best_score': round(b['score'], 3),
                      'iocn_at_best': round(b['iocn'], 3),
                      'plain': b['plain']}
            if b['score'] > best_per_model[m]['score']:
                best_per_model[m] = {'score': round(b['score'], 3), 'key': kname, 'plain': b['plain']}
        out['rescored'].append(row)
    out['best_per_model'] = best_per_model

    # -------- matched random-key CONTROL (same search, structureless keys) --------
    # The analytic 4-sigma band is unreliable (OE model undertrained -> tiny std)
    # and iocn_max is a max over ~10^5 decrypts. The honest null is the SAME
    # best-of-search run with random keys: real keytexts must beat this control.
    rng2 = np.random.default_rng(3301)
    ctrl_best = {m: -999.0 for m in QG}
    ctrl_iocn = 0.0
    ctrl_iocn_full = 0.0
    n_ctrl = max(8, len(out['rescored']))  # match real keytext count (equal search size)
    for _ in range(n_ctrl):
        rkey = rng2.integers(0, N, size=12000).tolist()
        cb, ci, cif = best_running_key(pages, rkey, QG)
        for m in QG:
            ctrl_best[m] = max(ctrl_best[m], cb[m]['score'])
        ctrl_iocn = max(ctrl_iocn, ci)
        ctrl_iocn_full = max(ctrl_iocn_full, cif)
    out['control_random_key'] = {'best_per_model': {m: round(ctrl_best[m], 3) for m in QG},
                                 'iocn_max': round(ctrl_iocn, 3),
                                 'iocn_max_full': round(ctrl_iocn_full, 3)}

    # genuine-language self-calibration midpoints (a real OE/Latin decrypt would
    # score near these, ~0.3-1.2 above the random floor)
    self_cal = {'OE': out['calibration']['OE_text']['OE'],
                'LAT': out['calibration']['LAT_text']['LAT']}

    fired = False
    reasons = []
    for m in ('OE', 'LAT'):
        real = best_per_model[m]['score']
        # a genuine hit must (a) beat the matched random-key control AND
        # (b) reach at least halfway to genuine-language self-calibration.
        halfway = (self_cal[m] + ctrl_best[m]) / 2.0
        beats_ctrl = real > ctrl_best[m] + 0.01
        looks_lang = real > halfway
        out.setdefault('gate_detail', {})[m] = {
            'real_best': round(real, 3), 'ctrl_best': round(ctrl_best[m], 3),
            'self_cal': round(self_cal[m], 3), 'halfway_gate': round(halfway, 3),
            'beats_ctrl': beats_ctrl, 'looks_language': looks_lang}
        if beats_ctrl and looks_lang:
            fired = True
            reasons.append(f"{m}: real {round(real,3)} beats ctrl {round(ctrl_best[m],3)} AND > halfway {round(halfway,3)}")
    # IoC*N gate on FULL-length pages (L>=200; low null variance so >1.3 is ~3sigma).
    # Short-page maxes are extreme-value noise and are reported but not gated.
    real_full = out.get('iocn_max_full_seen', 0.0)
    iocn_fire = real_full > 1.3 and real_full > ctrl_iocn_full * 1.05
    out['gate_detail_iocn'] = {'real_iocn_max_shortpage': round(out['iocn_max_seen'], 3),
                               'ctrl_iocn_max_shortpage': round(ctrl_iocn, 3),
                               'real_iocn_max_fullpage': round(real_full, 3),
                               'ctrl_iocn_max_fullpage': round(ctrl_iocn_full, 3),
                               'gate': 'fullpage L>=200, >1.3 and >1.05x control',
                               'fired': bool(iocn_fire)}
    if iocn_fire:
        fired = True
        reasons.append(f"IoC*N(full-page) real {round(real_full,3)} > 1.3 and > control {round(ctrl_iocn_full,3)}")
    out['signal_fired'] = fired
    out['reasons'] = reasons if reasons else ['no gate fired: all decrypt scores at random floor, IoC*N within control band']
    return out

if __name__ == '__main__':
    A = probe_A()
    B = probe_B()
    result = {'probe_id': 'P9-rsa-rescore', 'A_rsa': A, 'B_rescore': B}
    outp = rp('analysis/campaign15/P9_result.json')
    json.dump(result, open(outp, 'w'), indent=2)
    print("=== PROBE A : RSA ===")
    print("moduli:", [(m['keyid'], m['n_bits'], 'e=%d' % m['e']) for m in A['moduli']])
    print("tests_run:", A['tests_run'], "matches:", A['matches'])
    print("signal_fired:", A['signal_fired'])
    print(A['structural_note'])
    print("\n=== PROBE B : OE/Latin re-score ===")
    print("train sizes:", B['model_train_sizes'])
    print("noise_band:", B['noise_band'])
    print("calibration:", json.dumps(B['calibration']))
    print("best_per_model:", json.dumps(B['best_per_model']))
    print("iocn_max_seen:", round(B['iocn_max_seen'], 4))
    print("signal_fired:", B['signal_fired'], B['reasons'])
    print("\nJSON ->", outp)
