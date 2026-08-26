# L5 / A-04 - resolved payload, per-byte record

Instrument licence: blind visual calibration **40/40 exact-token** (22/22 on the
case-ambiguous glyph classes), pre-registered gate >=38/40 = PASS; independent
native-bitmap leave-one-out **236/237 = 99.58%** on trailing symbols (74/74 = 100% on
the case-ambiguous classes) and **242/242 = 100%** on leading digits.

Row/col use canonicalize.py's convention: r = idx//8, c = idx%8 (0-based, global).

SHA-256 resolved  : `3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290`
SHA-256 canon_256 : `4c8dc85531d256793a6d0d318b8845869b4983e672077b094ed955bde92226d5`
bytes differing from canon_256.bin: 45, 50, 246 (3 of 256)
bytes differing from canon_256_decpref.bin: 9 of 256

## The 11 adjudicated cells

| idx | page | r,c | class | resolved token | byte | canon | decimal-pref | pixel IoU | margin | 3-pass visual | concordant | confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 25 | p49 | r3,c1 | contested (A-04) | `3I` | **198** | 198 | 224 | 1.0000 | 0.091 | 3I / 3I / 3I | yes | RESOLVED |
| 45 | p49 | r5,c5 | token-split | `1l` | **107** | 81 | 81 | 1.0000 | 0.091 | 1l / 1l / 1l | yes | RESOLVED |
| 50 | p49 | r6,c2 | token-split | `0l` | **47** | 21 | 21 | 1.0000 | 0.091 | 0l / 0l / 0l | yes | RESOLVED |
| 165 | p50 | r20,c5 | token-split | `0I` | **18** | 18 | 18 | 1.0000 | 0.091 | (pixel instrument only) | n/a | RESOLVED |
| 172 | p50 | r21,c4 | token-split | `2S` | **148** | 148 | 148 | 1.0000 | 0.316 | (pixel instrument only) | n/a | RESOLVED |
| 175 | p50 | r21,c7 | contested (A-04) | `0I` | **18** | 18 | 44 | 1.0000 | 0.091 | 0I / 0I / 0I | yes | RESOLVED |
| 182 | p50 | r22,c6 | contested (A-04) | `2l` | **167** | 167 | 141 | 1.0000 | 0.091 | 2l / 2l / 2l | yes | RESOLVED |
| 199 | p51 | r24,c7 | contested (A-04) | `0l` | **47** | 47 | 21 | 1.0000 | 0.091 | 0l / 0l / 0l | yes | RESOLVED |
| 215 | p51 | r26,c7 | contested (A-04) | `1O` | **84** | 84 | 5 | 0.9993 | 0.133 | 1O / 1O / 1O | yes | RESOLVED |
| 237 | p51 | r29,c5 | contested (A-04) | `0W` | **32** | 32 | 58 | 1.0000 | 0.521 | 0W / 0W / 0W | yes | RESOLVED |
| 246 | p51 | r30,c6 | token-split | `3I` | **198** | 224 | 224 | 1.0000 | 0.091 | 3I / 3I / 3I | yes | RESOLVED |

Confidence definition: RESOLVED = three-pass visual concordance (where read visually)
AND nearest-exemplar native-bitmap IoU >= 0.99 on both glyphs, against a render whose
measured within-class IoU is 0.9948 and whose closest between-class pair is 0.908.

## Full resolved payload (hex, 256 bytes)

```
000  cb e7 a7 ba 61 ed 7e b7 5c f9 9c de f7 04 b7 d4 79 ca 0f 21 66 89 3b 57 6d c6 ad 19 96 42 8d 85
032  73 72 c5 27 36 50 85 05 50 54 1c 49 e6 6b c7 4c fd 10 2f 3b 56 ab 9c 50 fe 76 92 45 6a c4 7c 33
064  7a ff 19 c0 c7 49 a9 6c a4 4f cd b1 72 90 2e 52 8e 3a c9 c1 ad 1c 6f 41 d3 dc c6 31 ec 54 38 23
096  de 96 48 22 53 e5 20 ce 7a 3f 1f da 0e b8 20 73 49 8f c5 f7 36 ab 23 b8 2a ed 56 36 0d 14 a3 c1
128  c9 b3 56 78 a9 8d 48 ab 0a 81 e9 0d f5 2e a0 98 7d d2 5c ad f6 ae 99 bd e7 21 0e 70 34 fb f9 f8
160  e9 d9 c0 52 69 12 fa f8 f0 e4 fe 36 94 75 d1 12 eb 83 a6 af 90 28 a7 51 80 9c 13 51 26 c0 aa 21
192  00 9b 9f 59 b0 73 69 2f 6e 4a d1 44 c2 4c 7f 15 39 af 06 3d 46 96 fb 54 8e db 94 3b 3a 34 33 97
224  44 34 49 f9 90 00 75 af 6a ea c4 79 ee 20 81 ad 90 8d 2a d6 16 38 c6 c0 71 9e ac e6 b4 24 bd 50
```
