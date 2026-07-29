"""AN END (page-56, 512-bit) preimage brute — ORIGINAL BLAKE lane.

The ONE hash function never tried against the AN END pointer: original BLAKE
(SHA-3 finalist), NOT BLAKE2. Reuses the EXACT candidate object set from
../anend_preimage_broad.py (solved-page plaintexts, koans/riddle phrases,
Cicada PGP prose blocks, canon_256.bin + quarters/halves + variants,
concatenations) with the same per-candidate variant expansion.

Algorithms here: original BLAKE-512 (primary) + BLAKE-256 (cheap secondary).
blake_ref.py is validated against official BLAKE known-answer vectors first.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blake_ref

# --- HARD GATE: never run an unvalidated hash ---
for msg, expect in blake_ref.TEST_VECTORS_512.items():
    assert blake_ref.blake512(msg) == expect, "BLAKE-512 vector failed — aborting"
for msg, expect in blake_ref.TEST_VECTORS_256.items():
    assert blake_ref.blake256(msg) == expect, "BLAKE-256 vector failed — aborting"
print("[gate] original-BLAKE-512/256 validated against official test vectors OK")

TARGET = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

# Candidate set root: ../.. relative to pp49_51 == analysis/  (matches broad script's ROOT)
PP = os.path.abspath(os.path.join(HERE, '..'))          # analysis/pp49_51
ROOT = os.path.abspath(os.path.join(PP, '..'))          # analysis/

# --- English -> Futhorc (Gematria Primus) transliteration (from broad script) ---
GP = [
    ('ING', 'ᛝ'), ('OE', 'ᛟ'), ('EO', 'ᛇ'), ('IA', 'ᛡ'), ('IO', 'ᛡ'), ('EA', 'ᛠ'),
    ('AE', 'ᚫ'), ('TH', 'ᚦ'), ('NG', 'ᛝ'), ('OE', 'ᛟ'),
    ('F', 'ᚠ'), ('U', 'ᚢ'), ('V', 'ᚢ'), ('O', 'ᚩ'), ('R', 'ᚱ'), ('C', 'ᚳ'), ('K', 'ᚳ'),
    ('G', 'ᚷ'), ('W', 'ᚹ'), ('H', 'ᚻ'), ('N', 'ᚾ'), ('I', 'ᛁ'), ('J', 'ᛄ'), ('P', 'ᛈ'),
    ('X', 'ᛉ'), ('S', 'ᛋ'), ('Z', 'ᛋ'), ('T', 'ᛏ'), ('B', 'ᛒ'), ('E', 'ᛖ'), ('M', 'ᛗ'),
    ('L', 'ᛚ'), ('D', 'ᛞ'), ('A', 'ᚪ'), ('Y', 'ᚣ'), ('Q', 'ᚳ'),
]
def translit(s):
    s = s.upper(); out = []; i = 0
    while i < len(s):
        m = None
        for eng, rune in GP:
            if s.startswith(eng, i):
                m = (eng, rune); break
        if m:
            out.append(m[1]); i += len(m[0])
        else:
            i += 1
    return ''.join(out)

def variants(label, s):
    base = s; stripped = s.strip(); nospace = re.sub(r'\s+', '', s)
    upper = stripped.upper(); lower = stripped.lower(); tl = translit(stripped)
    forms = {
        'raw': base, 'strip': stripped, 'strip+nl': stripped + '\n',
        'nospace': nospace, 'upper': upper, 'lower': lower,
        'reversed': stripped[::-1], 'translit': tl, 'translit+nl': tl + '\n',
    }
    for sub, val in forms.items():
        yield f'{label}:{sub}', val.encode('utf-8')

def bin_variants(label, b):
    yield f'{label}:raw', b
    yield f'{label}:rev', b[::-1]
    yield f'{label}:+nl', b + b'\n'
    yield f'{label}:hex', b.hex().encode()
    yield f'{label}:HEX', b.hex().upper().encode()
    yield f'{label}:hex+nl', (b.hex() + '\n').encode()

# ------------------- gather candidates (identical to broad script) -------------------
text_cands = {}
bin_cands = {}

kse = os.path.join(ROOT, 'armada20/key_solved_english.txt')
if os.path.exists(kse):
    full = open(kse, encoding='utf-8').read()
    text_cands['solved_english_full'] = full
    m = re.search(r'ANENDWITHINTHEDEEPWEB.*?SEEKOUTTHISPAGE', full)
    if m:
        text_cands['anend_page'] = m.group(0)
    m2 = re.search(r'Parablelike.*', full)
    if m2:
        text_cands['parable'] = m2.group(0)

sp = os.path.join(ROOT, '..', 'data/keys/solved_plaintext.txt')
if os.path.exists(sp):
    text_cands['solved_plaintext_file'] = open(sp, encoding='utf-8').read()

pgp_dir = os.path.join(ROOT, 'armada20')
pgp_files = [f for f in os.listdir(pgp_dir)
             if (f.startswith('pgp_') or f.startswith('key_pgp')) and f.endswith('.txt')]
pgp_bodies = []
for f in sorted(pgp_files):
    p = os.path.join(pgp_dir, f)
    try:
        t = open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    if len(t) > 40000:
        continue
    text_cands[f'pgp:{f}'] = t
    pgp_bodies.append(t.strip())

rp = os.path.join(ROOT, 'armada20/riddle_phrases.txt')
if os.path.exists(rp):
    lines = [l.strip() for l in open(rp) if l.strip()]
    for l in lines:
        text_cands[f'phrase:{l}'] = l
    text_cands['phrases_concat_nl'] = '\n'.join(lines)
    text_cands['phrases_concat'] = ''.join(lines)

for fn in ['canon_256.bin', 'canon_256_decpref.bin']:
    p = os.path.join(PP, fn)
    if os.path.exists(p):
        b = open(p, 'rb').read()
        bin_cands[fn] = b
        n = len(b)
        bin_cands[f'{fn}:q0'] = b[:n // 4]
        bin_cands[f'{fn}:q1'] = b[n // 4:n // 2]
        bin_cands[f'{fn}:q2'] = b[n // 2:3 * n // 4]
        bin_cands[f'{fn}:q3'] = b[3 * n // 4:]
        bin_cands[f'{fn}:h0'] = b[:n // 2]
        bin_cands[f'{fn}:h1'] = b[n // 2:]

if pgp_bodies:
    text_cands['pgp_all_concat_nl'] = '\n'.join(pgp_bodies)
    text_cands['pgp_all_concat'] = ''.join(pgp_bodies)

# ------------------- run BLAKE preimage battery -------------------
def algos(b):
    return {'blake512': blake_ref.blake512(b), 'blake256': blake_ref.blake256(b)}

hits = []
tested = 0

def process(label, b):
    global tested
    for alg, dig in algos(b).items():
        tested += 1
        d = dig.lower()
        if d == TARGET:
            hits.append((label, alg, 'FULL-512 MATCH'))
        elif len(d) >= 32 and d[:32] == TARGET[:32]:
            hits.append((label, alg, f'PREFIX32: {dig}'))

for label, s in text_cands.items():
    for sub, b in variants(label, s):
        process(sub, b)
for label, b in bin_cands.items():
    for sub, bb in bin_variants(label, b):
        process(sub, bb)

print(f'target   : {TARGET}')
print(f'candidates: {len(text_cands)} text + {len(bin_cands)} binary base objects')
print(f'tested    : {tested} (candidate-variant x BLAKE-algorithm) combinations')
if hits:
    print('\n*** HITS ***')
    for h in hits:
        print('   ', h)
    print('\nRESULT: MATCH')
else:
    print('\nRESULT: clean NULL — no original-BLAKE-512/256 preimage (full or 32-hex-prefix).')
