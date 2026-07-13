"""Untested in 10 years: is the page-56 "AN END" hash the hash of an artifact
INSIDE the book (esp. the pp49-51 data object), rather than a lost .onion page?

Target (page 56, 512-bit): 36367763...132c2a8b4
Community only ever hashed external candidate onion pages (all failed). Here we
hash Cicada's OWN internal artifacts across many representations x algorithms.
A single hit = the first found preimage in a decade.
"""
import hashlib, os, itertools

TARGET = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
here = os.path.dirname(__file__)

def algos(b):
    out = {}
    for name in ['sha512', 'sha256', 'sha384', 'sha3_512', 'sha3_256',
                 'blake2b', 'blake2s', 'shake_256', 'md5', 'sha1']:
        try:
            h = hashlib.new(name)
            h.update(b)
            out[name] = h.hexdigest() if name != 'shake_256' else h.hexdigest(64)
        except Exception:
            pass
    # blake2b-512 with common Cicada-ish params already default; add blake2b digest_size 64
    return out

def reps():
    """Yield (label, bytes) for every reasonable representation of the payload +
    other internal artifacts."""
    for fn in ['canon_256.bin', 'canon_256_decpref.bin']:
        p = os.path.join(here, fn)
        if os.path.exists(p):
            b = open(p, 'rb').read()
            yield f'{fn}', b
            yield f'{fn}:reversed', b[::-1]
            yield f'{fn}:hexstr', b.hex().encode()
            yield f'{fn}:HEXSTR', b.hex().upper().encode()
            yield f'{fn}:+newline', b + b'\n'
    # hex text file as-is (whitespace variants)
    hp = os.path.join(here, 'canon_256.hex')
    if os.path.exists(hp):
        raw = open(hp, 'rb').read()
        yield 'canon_256.hex:raw', raw
        yield 'canon_256.hex:stripped', raw.replace(b'\n', b'').replace(b' ', b'').strip()
    # the runic ciphertext of the unsolved pages, as UTF-8 bytes + as index bytes
    kr = os.path.join(here, '..', '..', 'data', 'krisyotam_runes.txt')
    if os.path.exists(kr):
        t = open(kr, encoding='utf-8').read()
        RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
        idx = {r: i for i, r in enumerate(RUNES)}
        seq = [c for c in t if c in idx]
        yield 'all_runes:utf8', ''.join(seq).encode('utf-8')
        yield 'all_runes:idxbytes', bytes(idx[c] for c in seq)

def run():
    hits = []
    tested = 0
    for label, b in reps():
        for alg, dig in algos(b).items():
            tested += 1
            if dig == TARGET:
                hits.append((label, alg, 'FULL-512 MATCH'))
            # also compare truncated (target could be a longer digest truncated, or
            # our digest longer): match on min length
            elif dig[:128] == TARGET or TARGET.startswith(dig) or dig.startswith(TARGET[:64]):
                hits.append((label, alg, f'PARTIAL: {dig[:32]}...'))
    print(f'tested {tested} (representation x algorithm) combinations against page-56 hash')
    if hits:
        print('\n*** HITS ***')
        for h in hits:
            print('  ', h)
    else:
        print('no preimage match (full or partial).')
    # sanity: show a couple digests so we can eyeball the pipeline works
    b = open(os.path.join(here, 'canon_256.bin'), 'rb').read()
    print(f'\n(sanity) sha512(canon_256.bin) = {hashlib.sha512(b).hexdigest()[:48]}...')
    print(f'(sanity) target                = {TARGET[:48]}...')

run()
