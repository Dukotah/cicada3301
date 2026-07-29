"""AN END (page-56, 512-bit) preimage brute — BROAD lane.

Target: 36367763...132c2a8b4 (128 hex = 512 bits).
Assignment: test whether AN END hashes something WE ALREADY HOLD:
  - every SOLVED-page plaintext (individually + concatenated)
  - every Cicada PGP prose block (individually + concatenated)
  - the koans / riddle phrases
  - canon_256.bin + variants/quarters + concatenations
Variants per candidate: raw, +trailing \n, stripped, uppercased, lowercased,
  no-spaces, rune-transliterated (English->Futhorc gematria), reversed.
Algorithms: sha512, sha256, sha384, sha3_512, sha3_256, blake2b(64), blake2s,
  shake_256(64), md5, sha1, ripemd160.
"""
import hashlib, os, itertools, re

TARGET = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

# --- English -> Futhorc (Gematria Primus) transliteration, multichar first ---
GP = [
    ('ING','ᛝ'),('OE','ᛟ'),('EO','ᛇ'),('IA','ᛡ'),('IO','ᛡ'),('EA','ᛠ'),
    ('AE','ᚫ'),('TH','ᚦ'),('NG','ᛝ'),('OE','ᛟ'),
    ('F','ᚠ'),('U','ᚢ'),('V','ᚢ'),('O','ᚩ'),('R','ᚱ'),('C','ᚳ'),('K','ᚳ'),
    ('G','ᚷ'),('W','ᚹ'),('H','ᚻ'),('N','ᚾ'),('I','ᛁ'),('J','ᛄ'),('P','ᛈ'),
    ('X','ᛉ'),('S','ᛋ'),('Z','ᛋ'),('T','ᛏ'),('B','ᛒ'),('E','ᛖ'),('M','ᛗ'),
    ('L','ᛚ'),('D','ᛞ'),('A','ᚪ'),('Y','ᚣ'),('Q','ᚳ'),
]
def translit(s):
    s = s.upper()
    out = []
    i = 0
    while i < len(s):
        m = None
        for eng, rune in GP:
            if s.startswith(eng, i):
                m = (eng, rune); break
        if m:
            out.append(m[1]); i += len(m[0])
        else:
            i += 1  # skip non-letters
    return ''.join(out)

def algos(b):
    out = {}
    for name in ['sha512','sha256','sha384','sha3_512','sha3_256',
                 'blake2b','blake2s','shake_256','md5','sha1','ripemd160']:
        try:
            h = hashlib.new(name)
            h.update(b)
            out[name] = h.hexdigest(64) if name == 'shake_256' else h.hexdigest()
        except Exception:
            pass
    return out

def variants(label, s):
    """s is a python str (text candidate). Yield (sublabel, bytes)."""
    base = s
    stripped = s.strip()
    nospace = re.sub(r'\s+', '', s)
    upper = stripped.upper()
    lower = stripped.lower()
    tl = translit(stripped)
    forms = {
        'raw': base,
        'strip': stripped,
        'strip+nl': stripped + '\n',
        'nospace': nospace,
        'upper': upper,
        'lower': lower,
        'reversed': stripped[::-1],
        'translit': tl,
        'translit+nl': tl + '\n',
    }
    for sub, val in forms.items():
        yield f'{label}:{sub}', val.encode('utf-8')

def bin_variants(label, b):
    yield f'{label}:raw', b
    yield f'{label}:rev', b[::-1]
    yield f'{label}:+nl', b + b'\n'
    yield f'{label}:hex', b.hex().encode()
    yield f'{label}:HEX', b.hex().upper().encode()
    yield f'{label}:hex+nl', (b.hex()+'\n').encode()

# ------------------- gather candidates -------------------
text_cands = {}   # label -> str
bin_cands = {}    # label -> bytes

# 1. AN END page text + solved English corpus
kse = os.path.join(ROOT, 'analysis/armada20/key_solved_english.txt')
if os.path.exists(kse):
    full = open(kse, encoding='utf-8').read()
    text_cands['solved_english_full'] = full
    # AN END page substring
    m = re.search(r'ANENDWITHINTHEDEEPWEB.*?SEEKOUTTHISPAGE', full)
    if m:
        text_cands['anend_page'] = m.group(0)
    # the parable (page 57, plaintext)
    m2 = re.search(r'Parablelike.*', full)
    if m2:
        text_cands['parable'] = m2.group(0)

# 2. solved_plaintext.txt (PGP-formatted 2014 hash block)
sp = os.path.join(ROOT, 'data/keys/solved_plaintext.txt')
if os.path.exists(sp):
    text_cands['solved_plaintext_file'] = open(sp, encoding='utf-8').read()

# 3. individual PGP prose blocks
pgp_dir = os.path.join(ROOT, 'analysis/armada20')
pgp_files = [f for f in os.listdir(pgp_dir)
             if (f.startswith('pgp_') or f.startswith('key_pgp')) and f.endswith('.txt')]
pgp_bodies = []
for f in sorted(pgp_files):
    p = os.path.join(pgp_dir, f)
    try:
        t = open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    if len(t) > 40000:  # skip the giant jpeg-hex dumps as text (still hashed as concat below is skipped)
        continue
    text_cands[f'pgp:{f}'] = t
    pgp_bodies.append(t.strip())

# 4. riddle phrases (each + concat)
rp = os.path.join(ROOT, 'analysis/armada20/riddle_phrases.txt')
if os.path.exists(rp):
    lines = [l.strip() for l in open(rp) if l.strip()]
    for l in lines:
        text_cands[f'phrase:{l}'] = l
    text_cands['phrases_concat_nl'] = '\n'.join(lines)
    text_cands['phrases_concat'] = ''.join(lines)

# 5. canon_256 binaries + quarters/halves
for fn in ['canon_256.bin', 'canon_256_decpref.bin']:
    p = os.path.join(HERE, fn)
    if os.path.exists(p):
        b = open(p, 'rb').read()
        bin_cands[fn] = b
        n = len(b)
        bin_cands[f'{fn}:q0'] = b[:n//4]
        bin_cands[f'{fn}:q1'] = b[n//4:n//2]
        bin_cands[f'{fn}:q2'] = b[n//2:3*n//4]
        bin_cands[f'{fn}:q3'] = b[3*n//4:]
        bin_cands[f'{fn}:h0'] = b[:n//2]
        bin_cands[f'{fn}:h1'] = b[n//2:]

# 6. concatenations
if pgp_bodies:
    text_cands['pgp_all_concat_nl'] = '\n'.join(pgp_bodies)
    text_cands['pgp_all_concat'] = ''.join(pgp_bodies)
if 'solved_english_full' in text_cands and 'anend_page' in text_cands:
    # solved corpus + canon appended
    pass

# ------------------- run -------------------
def check(label, digs):
    for alg, dig in digs.items():
        d = dig.lower()
        if d == TARGET:
            return (label, alg, 'FULL-512 MATCH', dig)
        if len(d) >= 64 and (TARGET.startswith(d) or d.startswith(TARGET) or TARGET.startswith(d[:64]) and len(d) < 128):
            # near/partial (prefix) — flag for eyeball
            if d[:32] == TARGET[:32]:
                return (label, alg, 'PARTIAL-PREFIX', dig)
    return None

hits = []
tested = 0
seen_labels = set()

def process(label, b):
    global tested
    for alg, dig in algos(b).items():
        tested += 1
        d = dig.lower()
        if d == TARGET:
            hits.append((label, alg, 'FULL-512 MATCH'))
        elif d[:32] == TARGET[:32] and len(d) >= 32:
            hits.append((label, alg, f'PREFIX32: {dig[:40]}'))

for label, s in text_cands.items():
    for sub, b in variants(label, s):
        process(sub, b)
for label, b in bin_cands.items():
    for sub, bb in bin_variants(label, b):
        process(sub, bb)

print(f'candidates: {len(text_cands)} text + {len(bin_cands)} binary')
print(f'tested {tested} (candidate-variant x algorithm) combinations vs page-56 AN END hash')
if hits:
    print('\n*** HITS ***')
    for h in hits:
        print('   ', h)
else:
    print('NO preimage match (full or 32-hex-prefix).')

# sanity
print(f'\n(sanity) sha512("ANEND...page") variants exist: '
      f'{"anend_page" in text_cands}')
print(f'(sanity) target prefix = {TARGET[:32]}')
