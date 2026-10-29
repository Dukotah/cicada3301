import binascii, hashlib
r=open('../../round19/C1/payload_resolved.bin','rb').read()
d=bytearray(open('inputs/canon/canon_256_decpref.bin','rb').read())
for i in (45,50,246): d[i]=r[i]
open('inputs/resolved/canon_256.bin','wb').write(r)
open('inputs/resolved/canon_256_decpref.bin','wb').write(bytes(d))
h=open('inputs/canon/canon_256.hex','rb').read()
nl = b"\n" if h.endswith(b"\n") else b""
open('inputs/resolved/canon_256.hex','wb').write(binascii.hexlify(r)+nl)
print(hashlib.sha256(r).hexdigest(), len(r))
