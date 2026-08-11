"""Track PAYLOAD — is the LP2 plaintext binary rather than prose?

Motivation: every "no language" verdict in this repo (IoC_norm, quadgram scoring,
CRYPTO-RIGOR §C, R5 ROSETTA) is blind to a *compressed or binary* plaintext.
gzip output, a PGP packet stream, a key file and a one-time pad all have flat
IoC by construction, so "flat IoC" has been read as "still encrypted" when it is
equally consistent with "already decoded, but not prose".

This closes that hole: take the parameter-free, key-free decodes, pack them to
bytes across every reasonable representation, and look for *structure a language
model cannot see* — file magic, container framing, ASCII-armor, compression
headers, byte-histogram anomalies.

Representations
  streams   : raw ct | first difference | rank-in-28 | collision-unbump
              (each also reversed, and Atbash-mapped)
  packing   : base-29 and base-28 bignum -> bytes (both digit orders);
              5-bits-per-symbol bitpacking (both bit orders, 8 phase offsets)
  detectors : 40 file magics, PGP/PEM armor, printable-ASCII runs, zlib/gzip
              inflate at every offset, byte-entropy and chi-square vs uniform

A hit would be a solve. A null is a stated, reproducible elimination of the
"the pages are an encoded binary payload" hypothesis.
"""
import sys, os, zlib, gzip, io, math, collections, binascii

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

HERE = os.path.dirname(os.path.abspath(__file__))
N = 29

ct = list(open(os.path.join(HERE, 'ct.bin'), 'rb').read())
assert len(ct) == 12956

# ------------------------------------------------------------------ streams
def first_diff(s):
    return [(s[i] - s[i-1]) % N for i in range(1, len(s))]

def rank_in_28(s):
    """rank of c[i] among the 28 values != c[i-1] -- the natural inverse of a
    no-repeat (delta-plus-one) encoder. 28 symbols, information-preserving."""
    out = []
    for i in range(1, len(s)):
        v, prev = s[i], s[i-1]
        if v == prev:
            continue          # the 86 residual doublets are not representable
        out.append((v - prev - 1) % N)
    return out

def unbump(s):
    return [(s[i] - s[i-1] - 1) % N for i in range(1, len(s))]

def atbash(s):
    return [(N - 1 - v) for v in s]

STREAMS = {
    'raw':          ct,
    'firstdiff':    first_diff(ct),
    'rank28':       rank_in_28(ct),
    'unbump':       unbump(ct),
    'raw_rev':      ct[::-1],
    'firstdiff_rev': first_diff(ct[::-1]),
    'rank28_rev':   rank_in_28(ct[::-1]),
    'raw_atbash':   atbash(ct),
    'firstdiff_atbash': first_diff(atbash(ct)),
}

# ------------------------------------------------------------------ packing
def bignum_bytes(digits, base, msd_first=True):
    d = digits if msd_first else digits[::-1]
    n = 0
    for x in d:
        n = n * base + x
    if n == 0:
        return b''
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')

def bitpack(digits, bits=5, msb_first=True, phase=0):
    out = bytearray()
    acc = 0
    nb = 0
    for x in digits:
        if msb_first:
            acc = (acc << bits) | (x & ((1 << bits) - 1))
        else:
            acc |= (x & ((1 << bits) - 1)) << nb
        nb += bits
        while nb >= 8:
            if msb_first:
                nb -= 8
                out.append((acc >> nb) & 0xff)
                acc &= (1 << nb) - 1
            else:
                out.append(acc & 0xff)
                acc >>= 8
                nb -= 8
    b = bytes(out)
    return b[phase:] if phase else b

# ---------------------------------------------------------------- detectors
MAGICS = {
    b'\x1f\x8b': 'gzip', b'\x78\x01': 'zlib(none)', b'\x78\x9c': 'zlib(default)',
    b'\x78\xda': 'zlib(best)', b'\x78\x5e': 'zlib(low)', b'BZh': 'bzip2',
    b'\xfd7zXZ': 'xz', b'\x04\x22\x4d\x18': 'lz4', b'PK\x03\x04': 'zip',
    b'\x89PNG': 'png', b'\xff\xd8\xff': 'jpeg', b'GIF8': 'gif', b'BM': 'bmp',
    b'%PDF': 'pdf', b'\x7fELF': 'elf', b'MZ': 'mz', b'\xca\xfe\xba\xbe': 'class',
    b'OggS': 'ogg', b'RIFF': 'riff', b'\x1a\x45\xdf\xa3': 'matroska',
    b'SQLite': 'sqlite', b'\xd0\xcf\x11\xe0': 'ole', b'Rar!': 'rar',
    b'\x00\x00\x01\x00': 'ico', b'\x30\x82': 'asn1-der-seq',
    b'\x99\x01': 'pgp-pubkey-pkt', b'\x95\x01': 'pgp-seckey-pkt',
    b'\x85\x01': 'pgp-pkesk', b'\x8c\x0d': 'pgp-onepass',
    b'\xc6': 'pgp-new-pubkey', b'\xc5': 'pgp-new-seckey',
    b'ustar': 'tar', b'7z\xbc\xaf': '7z', b'\x25\x21PS': 'postscript',
    b'\xed\xab\xee\xdb': 'rpm', b'ITSF': 'chm', b'CWS': 'swf', b'FWS': 'swf',
}
ARMOR = [b'-----BEGIN', b'BEGIN PGP', b'ssh-rsa', b'-----END', b'PuTTY-User-Key']

def entropy(b):
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum(v/n * math.log2(v/n) for v in c.values())

def printable_runs(b, minlen=8):
    runs, cur = [], bytearray()
    for x in b:
        if 32 <= x < 127:
            cur.append(x)
        else:
            if len(cur) >= minlen:
                runs.append(bytes(cur))
            cur = bytearray()
    if len(cur) >= minlen:
        runs.append(bytes(cur))
    return runs

WORDS = set(b'THE AND THAT HAVE FOR NOT WITH YOU THIS BUT HIS FROM THEY SAY HER SHE '
            b'WILL ONE ALL WOULD THERE THEIR WHAT OUT ABOUT WHO GET WHICH WHEN MAKE '
            b'CAN LIKE TIME JUST HIM KNOW TAKE INTO YEAR YOUR GOOD SOME COULD THEM '
            b'THAN THEN NOW LOOK ONLY COME OVER ALSO BACK AFTER USE TWO HOW WORK '
            b'CICADA PRIMUS LIBER INSTAR DIVINITY PRIME TOTIENT SACRED PILGRIM'.split())


def looks_like_content(out):
    """Reject the classic deflate-garbage hit: a long run of one repeated byte
    is 'printable' but is not content. Require real lexical structure."""
    if len(out) < 64:
        return False
    head = out[:2000]
    pr = sum(1 for x in head if 32 <= x < 127 or x in (9, 10, 13)) / len(head)
    if pr < 0.95:
        return False
    c = collections.Counter(head)
    if c.most_common(1)[0][1] / len(head) > 0.35:      # dominated by one byte
        return False
    if len(c) < 12:                                     # too few distinct bytes
        return False
    toks = set(t.upper() for t in bytes(head).split() if t.isalpha())
    if len(toks & WORDS) < 3:                           # no dictionary content
        return False
    return True


def try_inflate(b, limit=4096):
    """attempt zlib/deflate/gzip at every offset in the first `limit` bytes"""
    good = []
    for off in range(min(limit, len(b))):
        for wbits, tag in ((15, 'zlib'), (-15, 'raw-deflate'), (31, 'gzip')):
            try:
                d = zlib.decompressobj(wbits)
                out = d.decompress(b[off:off + 200000])
                if looks_like_content(out):
                    good.append((off, tag, out[:120]))
            except Exception:
                pass
    return good

def scan(name, b, report):
    if len(b) < 32:
        return
    for m, tag in MAGICS.items():
        if b.startswith(m):
            report.append('MAGIC-HEAD %s: %s' % (name, tag))
        i = b.find(m, 0, 8192)
        if i > 0 and len(m) >= 3:
            report.append('MAGIC@%d %s: %s' % (i, name, tag))
    for a in ARMOR:
        i = b.find(a)
        if i >= 0:
            report.append('ARMOR@%d %s: %r' % (i, name, a))
    # a meaningful ASCII find is a long run that is mostly letters/space, not a
    # 10-byte smear of random punctuation (which uniform bytes produce by chance)
    runs = [r for r in printable_runs(b, 16)
            if sum(1 for x in r if x in b' ' or 65 <= x < 91 or 97 <= x < 123)
            / len(r) > 0.8]
    if runs:
        report.append('ASCII %s: %d letter-runs>=16, longest %r' %
                      (name, len(runs), max(runs, key=len)[:60]))
    inf = try_inflate(b)
    for off, tag, head in inf:
        report.append('INFLATE %s @%d %s -> %r' % (name, off, tag, head))
    h = entropy(b)
    if h < 7.0:
        report.append('LOWENT %s: entropy %.3f over %d bytes' % (name, h, len(b)))


def main():
    report = []
    tested = 0
    for sname, s in STREAMS.items():
        for base in (29, 28):
            if base == 28 and max(s) > 27:
                continue
            for msd in (True, False):
                b = bignum_bytes(s, base, msd)
                scan('%s/base%d/%s' % (sname, base, 'msd' if msd else 'lsd'), b, report)
                tested += 1
        for msb in (True, False):
            for phase in range(8):
                b = bitpack(s, 5, msb, phase)
                scan('%s/bit5/%s/ph%d' % (sname, 'msb' if msb else 'lsb', phase),
                     b, report)
                tested += 1
    print('representations tested:', tested)
    # summary stats for the record
    print('\n--- byte-level profile of the primary representations ---')
    for sname in ('raw', 'firstdiff', 'rank28'):
        b = bignum_bytes(STREAMS[sname], 29, True)
        c = collections.Counter(b)
        chi = sum((v - len(b)/256)**2 / (len(b)/256) for v in
                  [c.get(i, 0) for i in range(256)])
        print('%-10s bytes=%5d entropy=%.4f chi2(255df)=%.1f printable=%.3f' %
              (sname, len(b), entropy(b), chi,
               sum(1 for x in b if 32 <= x < 127) / len(b)))
    print('\n--- findings ---')
    if not report:
        print('NONE — no magic, no armor, no inflatable region, no long ASCII run,')
        print('no low-entropy representation in any of the %d representations.' % tested)
    else:
        for r in report:
            print(r)


if __name__ == '__main__':
    main()
