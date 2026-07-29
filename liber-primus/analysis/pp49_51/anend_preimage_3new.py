"""AN END (page-56, 512-bit) preimage gate for the THREE never-tested 512-bit digests:
  - Whirlpool          (whirlpool_ref.py, ISO KAT-gated)
  - Streebog-512       (gostcrypto, RFC6986/empty KAT-gated)
  - Skein-512-512      (skein_ref.py, Skein v1.3 KAT-gated)

Whole-file hash of EVERY held candidate:
  * open blobs: armada_osint T2.bin, T3.bin, artifacts/2.jpg, folly.bin, wisdom.bin (3368B trio) + siblings
  * internal candidate-object set the prior BLAKE/SHA battery used:
      solved plaintexts, koans/riddle phrases, canon_256.bin + variants/quarters, PGP prose
Variant expansion mirrors anend_preimage_broad.py (raw/strip/upper/lower/nospace/translit/reversed/hex...).
Compare each against AN-END target 36367763...132c2a8b4. Report KAT-pass proof, count, MATCH or NULL.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import whirlpool_ref, skein_ref
import gostcrypto

# ---------------- HARD KAT GATES (never run an unvalidated hash) ----------------
for m, e in whirlpool_ref.TEST_VECTORS.items():
    assert whirlpool_ref.whirlpool(m) == e, "Whirlpool KAT FAILED"
for m, e in skein_ref.TEST_VECTORS.items():
    assert skein_ref.skein512_512(m) == e, "Skein-512-512 KAT FAILED"
def streebog512(b):
    h = gostcrypto.gosthash.new('streebog512'); h.update(b); return h.digest().hex()
# empty-string natural-order published KAT
assert streebog512(b"") == ("8e945da209aa869f0455928529bcae4679e9873ab707b55315f56ceb98bef0a7"
                            "362f715528356ee83cda5f2aac4c6ad2ba3a715c1bcd81cb8e9f90bf4c1c1a8a"), "Streebog KAT FAILED"
# RFC6986 M1 (natural order == RFC-expected reversed)
_m1 = b"012345678901234567890123456789012345678901234567890123456789012"
_exp = bytes.fromhex("486f64c1917879417fef082b3381a4e211c324f074654c38823a7b76f830ad00"
                     "fa1fbae42b1285c0352f227524bc9ab16254288dd6863dccd5b9f54a1ad0541b")
assert bytes.fromhex(streebog512(_m1)) == _exp[::-1], "Streebog RFC6986-M1 FAILED"
print("[gate] Whirlpool / Streebog-512 / Skein-512-512 all KAT-validated OK")

TARGET = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))   # liber-primus/
PP = HERE

# --- English -> Futhorc transliteration (from broad script) ---
GP = [
    ('ING','ᛝ'),('OE','ᛟ'),('EO','ᛇ'),('IA','ᛡ'),('IO','ᛡ'),('EA','ᛠ'),
    ('AE','ᚫ'),('TH','ᚦ'),('NG','ᛝ'),('OE','ᛟ'),
    ('F','ᚠ'),('U','ᚢ'),('V','ᚢ'),('O','ᚩ'),('R','ᚱ'),('C','ᚳ'),('K','ᚳ'),
    ('G','ᚷ'),('W','ᚹ'),('H','ᚻ'),('N','ᚾ'),('I','ᛁ'),('J','ᛄ'),('P','ᛈ'),
    ('X','ᛉ'),('S','ᛋ'),('Z','ᛋ'),('T','ᛏ'),('B','ᛒ'),('E','ᛖ'),('M','ᛗ'),
    ('L','ᛚ'),('D','ᛞ'),('A','ᚪ'),('Y','ᚣ'),('Q','ᚳ'),
]
def translit(s):
    s = s.upper(); out=[]; i=0
    while i < len(s):
        m=None
        for eng,rune in GP:
            if s.startswith(eng,i): m=(eng,rune); break
        if m: out.append(m[1]); i+=len(m[0])
        else: i+=1
    return ''.join(out)

def variants(label, s):
    stripped=s.strip(); nospace=re.sub(r'\s+','',s)
    forms={'raw':s,'strip':stripped,'strip+nl':stripped+'\n','nospace':nospace,
           'upper':stripped.upper(),'lower':stripped.lower(),'reversed':stripped[::-1],
           'translit':translit(stripped),'translit+nl':translit(stripped)+'\n'}
    for sub,val in forms.items():
        yield f'{label}:{sub}', val.encode('utf-8')

def bin_variants(label, b):
    yield f'{label}:raw', b
    yield f'{label}:rev', b[::-1]
    yield f'{label}:+nl', b + b'\n'
    yield f'{label}:hex', b.hex().encode()
    yield f'{label}:HEX', b.hex().upper().encode()
    yield f'{label}:hex+nl', (b.hex()+'\n').encode()

text_cands = {}
bin_cands = {}

# ---- internal candidate set (mirror of broad/blake battery) ----
kse = os.path.join(ROOT, 'analysis/armada20/key_solved_english.txt')
if os.path.exists(kse):
    full = open(kse, encoding='utf-8').read()
    text_cands['solved_english_full'] = full
    m = re.search(r'ANENDWITHINTHEDEEPWEB.*?SEEKOUTTHISPAGE', full)
    if m: text_cands['anend_page'] = m.group(0)
    m2 = re.search(r'Parablelike.*', full)
    if m2: text_cands['parable'] = m2.group(0)

sp = os.path.join(ROOT, 'data/keys/solved_plaintext.txt')
if os.path.exists(sp):
    text_cands['solved_plaintext_file'] = open(sp, encoding='utf-8').read()

pgp_dir = os.path.join(ROOT, 'analysis/armada20')
pgp_bodies=[]
if os.path.isdir(pgp_dir):
    for f in sorted(os.listdir(pgp_dir)):
        if (f.startswith('pgp_') or f.startswith('key_pgp')) and f.endswith('.txt'):
            p=os.path.join(pgp_dir,f)
            try: t=open(p,encoding='utf-8',errors='replace').read()
            except Exception: continue
            if len(t)>40000: continue
            text_cands[f'pgp:{f}']=t; pgp_bodies.append(t.strip())

rp = os.path.join(ROOT, 'analysis/armada20/riddle_phrases.txt')
if os.path.exists(rp):
    lines=[l.strip() for l in open(rp) if l.strip()]
    for l in lines: text_cands[f'phrase:{l}']=l
    text_cands['phrases_concat_nl']='\n'.join(lines)
    text_cands['phrases_concat']=''.join(lines)

for fn in ['canon_256.bin','canon_256_decpref.bin']:
    p=os.path.join(PP,fn)
    if os.path.exists(p):
        b=open(p,'rb').read(); bin_cands[fn]=b; n=len(b)
        bin_cands[f'{fn}:q0']=b[:n//4]; bin_cands[f'{fn}:q1']=b[n//4:n//2]
        bin_cands[f'{fn}:q2']=b[n//2:3*n//4]; bin_cands[f'{fn}:q3']=b[3*n//4:]
        bin_cands[f'{fn}:h0']=b[:n//2]; bin_cands[f'{fn}:h1']=b[n//2:]

if pgp_bodies:
    text_cands['pgp_all_concat_nl']='\n'.join(pgp_bodies)
    text_cands['pgp_all_concat']=''.join(pgp_bodies)

# ---- HELD OPEN BLOBS (the armada OSINT externals) ----
AO = os.path.join(ROOT, 'analysis/armada_osint')
blob_paths = [
    ('T2.bin',        os.path.join(AO,'extracts/T2.bin')),
    ('T3.bin',        os.path.join(AO,'extracts/T3.bin')),
    ('T1_onion3',     os.path.join(AO,'extracts/T1-onion3-5x5-rune-outguess.bin')),
    ('2.jpg',         os.path.join(AO,'artifacts/2.jpg')),
    ('folly.bin',     os.path.join(AO,'artifacts/folly.bin')),
    ('folly_snap2',   os.path.join(AO,'artifacts/folly_snap2.bin')),
    ('wisdom.bin',    os.path.join(AO,'artifacts/wisdom.bin')),
    ('t.tmp3368',     os.path.join(AO,'artifacts/t.tmp')),
    ('t5_nokey',      os.path.join(AO,'artifacts/t5_nokey.bin')),
    ('lpc02_out',     os.path.join(AO,'artifacts/lpc02_out.bin')),
    ('T6txt',         os.path.join(AO,'extracts/T6.txt')),
    ('T5_4gq25',      os.path.join(AO,'extracts/T5-4gq25-2016.outguess.txt')),
]
for label, p in blob_paths:
    if os.path.exists(p) and os.path.getsize(p) > 0:
        bin_cands[f'blob:{label}'] = open(p,'rb').read()

# also the 3368-byte trio concatenations (folly/wisdom/T3 are all 3368B)
trio = {}
for k in ('blob:folly.bin','blob:wisdom.bin','blob:T3.bin'):
    if k in bin_cands: trio[k]=bin_cands[k]
if len(trio)>=2:
    keys=list(trio)
    import itertools
    for a,b in itertools.permutations(keys,2):
        bin_cands[f'concat:{a}+{b}']=trio[a]+trio[b]

# ------------------- run the 3-algo whole-file preimage gate -------------------
WP_MAX = int(os.environ.get('WP_MAX', '65536'))  # skip pure-Python Whirlpool above this size (run separately)
def algos(b):
    out = {
        'streebog512':  streebog512(b),
        'skein512':     skein_ref.skein512_512(b),
    }
    if len(b) <= WP_MAX:
        out['whirlpool'] = whirlpool_ref.whirlpool(b)
    return out

hits=[]; tested=0
def process(label, b):
    global tested
    for alg,dig in algos(b).items():
        tested+=1
        d=dig.lower()
        if d==TARGET:
            hits.append((label,alg,'FULL-512 MATCH'))
        elif len(d)>=32 and d[:32]==TARGET[:32]:
            hits.append((label,alg,f'PREFIX32: {dig}'))

for label,s in text_cands.items():
    for sub,b in variants(label,s):
        process(sub,b)
for label,b in bin_cands.items():
    for sub,bb in bin_variants(label,b):
        process(sub,bb)

print(f'target    : {TARGET}')
print(f'candidates: {len(text_cands)} text + {len(bin_cands)} binary base objects')
print(f'  held blobs among binary: '+', '.join(k for k in bin_cands if k.startswith("blob:") or k.startswith("concat:")))
print(f'tested    : {tested} (candidate-variant x {{whirlpool,streebog512,skein512}}) combinations')
if hits:
    print('\n*** HITS ***')
    for h in hits: print('   ',h)
    print('\nRESULT: MATCH')
else:
    print('\nRESULT: clean NULL — no Whirlpool / Streebog-512 / Skein-512-512 preimage (full or 32-hex-prefix).')
