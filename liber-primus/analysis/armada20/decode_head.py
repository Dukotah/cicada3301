p="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"
d=open(p,'rb').read()
app=d[336353:]
head=app[:400]
print("RAW repr:", repr(head[:200]))
# The leading 'a' then hex digits. Try: strip non-hex, hex-decode
import re
# show as chars
print()
txt=head.decode('latin1')
# It begins '\n\na0237323020...'. Maybe 'a' is junk, rest is hexpairs of ASCII
hexpart=re.sub(r'[^0-9a-fA-F]','', txt[2:])  # after \n\n
print("hexpart len", len(hexpart), hexpart[:80])
try:
    dec=bytes.fromhex(hexpart[:200] if len(hexpart[:200])%2==0 else hexpart[:199])
    print("hexdecode->", repr(dec[:120]))
except Exception as e:
    print("err",e)
# Alternatively the bytes ARE ascii digits representing a decimal/columnar dump
# print actual bytes 0..120 as decimal
print()
print("bytes:", list(app[:60]))
