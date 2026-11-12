"""Fresh-eyes audit, part 10: the three signed 991-byte "liber-primus-hash-block" blobs are a decoded object.

They are three XOR shares of the PGP-signed January 2014 transposition message ("IDGTK UMLOO ...").
Round 43 X0 (item 29) and the Round 44 plan (lane P5, "hash-block 20-byte-stride digest parse") treat
them as open. Found by audit reader K; verified here byte for byte.
"""
import os

import lp2

A = os.path.abspath(os.path.join(lp2.LP, "..", "corpus", "A-primary-artifacts"))
names = ["2014-01-liber-primus-hash-block.bin", "2014-01-liber-primus-hash-block-outguess-01.bin",
         "2014-01-liber-primus-hash-block-outguess-02.bin"]
a, b, c = (open(os.path.join(A, "signed-payloads", n), "rb").read() for n in names)
x = bytes(p ^ q ^ r for p, q, r in zip(a, b, c))
t = open(os.path.join(A, "pgp", "messages", "2014-01-signed-ciphertext.asc"), "rb").read()
assert len(a) == len(b) == len(c) == len(t) == 991 and x == t
print("XOR of the three 991-byte blobs == pgp/messages/2014-01-signed-ciphertext.asc:", x == t)
print(x[:150].decode("ascii", "replace"))
