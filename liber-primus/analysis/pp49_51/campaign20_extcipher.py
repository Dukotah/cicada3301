"""Campaign XX (novel_cipher lane): treat pp49-51 canon_256.bin as CIPHERTEXT in
its own right under a SHORT external key, and test HMAC relationship to page-56 hash.

Untested by all prior campaigns (IX/XII/XVII tested: preimage, tiled-keystream XOR/sub,
autokey, crib-drag). NOT tested: AES / RC4 / ChaCha20 *decryption* of P; HMAC(key, X)==target.

Pure-stdlib RC4; `cryptography` for AES/ChaCha. Scoring = English printability + entropy
collapse. A real hit = a decrypt with high printable ASCII fraction + low entropy + words.
"""
import hashlib, hmac, os, math, itertools

here = os.path.dirname(os.path.abspath(__file__))
P = open(os.path.join(here, 'canon_256.bin'), 'rb').read()
P2 = open(os.path.join(here, 'canon_256_decpref.bin'), 'rb').read()
TARGET = bytes.fromhex(
    "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
    "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

KEYS = [k.strip() for k in open(os.path.join(here, '..', 'armada_osint', 'keys.txt')) if k.strip()]
# add koan / structural phrases and hash-derived keys
KEYS += ["AN END", "A KOAN", "PILGRIM", "THE PRIMES ARE SACRED",
         "THE TOTIENT FUNCTION IS SACRED", "ALL THINGS SHOULD BE ENCRYPTED",
         "WISDOM", "FOLLY", "DIVINITY", "PARABLE", "END OF THE JOURNEY",
         "3301", "1033", "CICADA", "CICADA 3301", "LIBER PRIMUS"]
KEYS = list(dict.fromkeys(KEYS))

def entropy(b):
    if not b: return 0
    c = [0]*256
    for x in b: c[x]+=1
    e = 0.0; n=len(b)
    for v in c:
        if v: p=v/n; e-=p*math.log2(p)
    return e

def printable_frac(b):
    return sum(1 for x in b if 32<=x<127 or x in (9,10,13))/len(b)

WORDS = [b'THE',b'AND',b'END',b'CICADA',b'WISDOM',b'PILGRIM',b'PRIME',b'SACRED',
         b'DIVIN',b'INSTAR',b'EMERG',b'PRIMUS',b'KOAN',b'the',b'and',b'ing',b' the ']
def wordhits(b):
    u = b.upper()
    return sum(u.count(w.upper()) for w in WORDS)

def score(b):
    return (printable_frac(b), round(entropy(b),3), wordhits(b))

# ---- RC4 (pure) ----
def rc4(key, data):
    S=list(range(256)); j=0
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])&255
        S[i],S[j]=S[j],S[i]
    out=bytearray(); i=j=0
    for c in data:
        i=(i+1)&255; j=(j+S[i])&255
        S[i],S[j]=S[j],S[i]
        out.append(c^S[(S[i]+S[j])&255])
    return bytes(out)

def xor_rep(key, data):
    return bytes(d ^ key[i%len(key)] for i,d in enumerate(data))

results=[]
def consider(label, pt):
    pf,ent,wh = score(pt)
    # interesting = markedly more printable OR notably lower entropy OR word hits
    if pf>0.85 or ent<6.5 or wh>=3:
        results.append((label, pf, ent, wh, pt[:48]))

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

for payload_name, payload in [('P', P), ('P2', P2)]:
    for k in KEYS:
        kb = k.encode()
        # key derivations: raw, sha256(32B), sha512(64B first16/24/32)
        keyvars = {
            'raw': kb,
            'sha256': hashlib.sha256(kb).digest(),
            'md5': hashlib.md5(kb).digest(),
        }
        # RC4 (any length key)
        for kn, kv in {'raw':kb, 'sha256':hashlib.sha256(kb).digest()}.items():
            consider(f'{payload_name} RC4/{kn} k={k!r}', rc4(kv, payload))
        # repeating-key XOR (short keyword) -- NEW: Lead B only tiled full keystreams
        consider(f'{payload_name} XORrep k={k!r}', xor_rep(kb, payload))
        # AES: need 16/24/32-byte key
        for klen, kv in [(16, hashlib.md5(kb).digest()),
                         (32, hashlib.sha256(kb).digest())]:
            # AES-ECB
            try:
                c=Cipher(algorithms.AES(kv), modes.ECB())
                d=c.decryptor(); consider(f'{payload_name} AESECB/{klen} k={k!r}', d.update(payload)+d.finalize())
            except Exception: pass
            # AES-CBC iv=0
            try:
                c=Cipher(algorithms.AES(kv), modes.CBC(b'\0'*16))
                d=c.decryptor(); consider(f'{payload_name} AESCBC0/{klen} k={k!r}', d.update(payload)+d.finalize())
            except Exception: pass
            # AES-CTR nonce=0
            try:
                c=Cipher(algorithms.AES(kv), modes.CTR(b'\0'*16))
                d=c.decryptor(); consider(f'{payload_name} AESCTR0/{klen} k={k!r}', d.update(payload)+d.finalize())
            except Exception: pass
        # ChaCha20 (32-byte key, 16-byte nonce)
        try:
            kv=hashlib.sha256(kb).digest()
            c=Cipher(algorithms.ChaCha20(kv, b'\0'*16), None)
            d=c.decryptor(); consider(f'{payload_name} ChaCha20 k={k!r}', d.update(payload))
        except Exception: pass

print(f"== EXT-CIPHER DECRYPT: {len(KEYS)} keys x 2 payloads x ~7 ciphers ==")
print(f"baseline P: printable={printable_frac(P):.3f} entropy={entropy(P):.3f}")
if results:
    print("\n*** INTERESTING (printable>.85 OR entropy<6.5 OR 3+ words) ***")
    for r in sorted(results, key=lambda x:(-x[1], x[2])):
        print(f"  pf={r[1]:.3f} ent={r[2]:.2f} words={r[3]}  {r[0]}\n     {r[4]!r}")
else:
    print("\nno decrypt beat printable>.85 / entropy<6.5 / 3+words -- all noise.")

# ---- HMAC test: does HMAC(key, artifact) == page-56 target? ----
print(f"\n== HMAC(key, artifact) vs page-56 hash ==")
arts = {'P':P, 'P2':P2, 'P_hex':P.hex().encode(), 'runes':None}
kr = os.path.join(here,'..','..','data','krisyotam_runes.txt')
if os.path.exists(kr):
    RUNES='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
    idx={r:i for i,r in enumerate(RUNES)}
    t=open(kr,encoding='utf-8').read()
    arts['runes']=bytes(idx[c] for c in t if c in idx)
hmac_hits=0; hmac_tested=0
for aname,ab in arts.items():
    if ab is None: continue
    for k in KEYS:
        for alg in ('sha512','sha3_512','blake2b'):
            hmac_tested+=1
            if hmac.new(k.encode(), ab, alg).digest()==TARGET:
                print(f"  *** HMAC HIT: HMAC-{alg}(key={k!r}, {aname}) == page56 ***"); hmac_hits+=1
    # also HMAC with artifact AS KEY over cicada strings
    for k in KEYS:
        for alg in ('sha512','sha3_512','blake2b'):
            hmac_tested+=1
            if hmac.new(ab, k.encode(), alg).digest()==TARGET:
                print(f"  *** HMAC HIT: HMAC-{alg}(key={aname}, msg={k!r}) == page56 ***"); hmac_hits+=1
print(f"  tested {hmac_tested} HMAC combos, {hmac_hits} hits")

# ---- structural: is any 64B quarter == a hash of another quarter / cicada string? ----
print(f"\n== structural: 64B quarter as digest of another part ==")
q=[P[i*64:(i+1)*64] for i in range(4)]
h=[P[i*128:(i+1)*128] for i in range(2)]
struct_hits=0
candidates = {f'q{i}':q[i] for i in range(4)}
candidates.update({f'h{i}':h[i] for i in range(2)})
candidates['P128']=P[:128]; candidates['Pfull']=P
for src_n,src in candidates.items():
    for alg in ('sha512','sha3_512','blake2b'):
        dig=hashlib.new(alg,src).digest()
        for tgt_n in range(4):
            if dig==q[tgt_n]:
                print(f"  *** {alg}({src_n}) == quarter q{tgt_n} ***"); struct_hits+=1
    # keyed by cicada string
print(f"  {struct_hits} internal-digest structural hits")
