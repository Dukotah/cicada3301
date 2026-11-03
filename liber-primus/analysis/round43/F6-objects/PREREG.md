# R43 / F6 — PREREG: the open internal objects, joined for the first time

Written BEFORE any experiment ran. Thresholds fixed here; the runner scripts implement
exactly this and nothing that crosses is reported as a hit unless it clears these bars.

## Objects (inputs, hashed at extraction time in RESULTS.md)

1. **canon_256** — `analysis/pp49_51/canon_256.bin` (256 bytes, the pp49–51 payload) and
   the variant `analysis/pp49_51/canon_256_decpref.bin` (256 bytes). The `*_superseded.bin`
   files are explicitly EXCLUDED (superseded by name).
2. **Onion pre-page blobs** — the 256-byte hex blobs embedded in
   `analysis/armada_osint/onions_ibotpeaches/onions__{avowyfgl5lkzfj3n,cu343l33nqaekrnw,fv7lyucmeozzd5j4}.onion__pre__index.html`,
   with their HTML-comment markers (`<!--3301-->`, `<!--761-->`, `<!--1033-->`).
   Extraction rule: the single run of ≥512 hex chars in each file, taken exactly; sha256
   of each extracted 256-byte binary recorded.
3. **Page-56 hash** — the 512-bit value stated on solved LP2 p56 ("AN END"):
   `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4`
   (canonical per `analysis/KEY-HINT-RESEARCH.md` and `data/keys/solved_plaintext.txt`).
4. **T4 blobs** — `analysis/armada_osint/artifacts/T4_blob{1,2,3}.bin` (+ the committed
   `_flip` variants and `T4_blob1_gunzip.bin`). No T2/T3 `.bin` blobs exist in
   `artifacts/` (checked at listing time); T2/T3 are covered only by their historical
   keytest drivers and will be noted as absent.

## (a) Payload-as-ciphertext — canon_256 vs the onion blobs

Grid: {canon_256, canon_256_decpref} × {blob761, blob1033, blob3301} × {blob forward,
blob byte-reversed} × ops {XOR, ADD mod 256, SUB (payload−blob) mod 256} = 36 outputs,
256 bytes each.

Structure detectors (ALL fixed in advance), applied to every output:
- **D1 printable**: fraction of bytes in 0x20–0x7E plus `\t\n\r`. FLAG iff ≥ 0.85.
- **D2 printable run**: longest consecutive printable run. FLAG iff ≥ 40 bytes.
- **D3 entropy**: Shannon entropy (bits/byte, 256-byte sample). FLAG iff ≤ 6.00.
  (Reference: random 256-byte strings measure ≈ 7.1–7.3; English text ≈ 4.3–4.8.)
- **D4 magic**: known magic at offset 0 from the fixed list {PK\x03\x04, \x1f\x8b, BZh,
  \xfd7zXZ, %PDF, \x89PNG, GIF8, \xff\xd8\xff, 7z\xbc\xaf, Rar!, \x30\x82 (DER SEQUENCE
  with plausible length), 0x99/0x85/0xc6/0x95 high-bit PGP packet tag with valid
  length covering ≥ 64 bytes, "-----BEGIN"}. FLAG on any match.
- **D5 ASN.1**: byte 0 == 0x30 and the DER definite length parses to exactly 254 or 256
  total bytes. FLAG on parse.
- **D6 mod-29 screen** (SCREEN ONLY, not a hit criterion by itself): bytes %29 → rune
  indices, adjudicated with panel-R36 (`analysis/round19/I2/adjudicate.py`, the R41
  instrument). Record pmax/preg. A mod-29 screen value is only promoted to a finding if
  pmax ≥ bar_v3(N=36 grid, L=240, "free") from `analysis/round34/I1-v3-null/bars_v3.py`.

**Hit rule (a)**: an output is a candidate iff (D1 or D2 or D4 or D5) fires, or (D3 AND D6
bar-crossing) together. Anything else = null, reported with numbers.

**Control (mandatory)**: take the first 256 bytes of `data/pride.txt` (known English),
XOR with blob761-forward, then XOR the result with blob761-forward again inside the same
detector pipeline — the recovered text MUST fire D1+D2 (and D3). If the control does not
fire, the run is invalid and must be fixed before results are read.

## (b) The blobs themselves

For each blob as a big-endian integer: bit length, parity (even ⇒ not an RSA modulus),
trial division by all primes < 10^6 (any factor ⇒ not a well-formed modulus), pairwise
GCDs, GCD with each of {3301, 503, 509, 761, 1033, 503·509, 503·509·3301}. Pairwise XOR
of the three blobs: printable fraction, entropy, longest shared prefix/suffix in bytes.
Also each blob XOR canon_256 is already covered in (a).

**Interpretation rule**: 2048-bit odd integers with no small factors are *consistent with*
RSA moduli OR signatures OR random bytes — we can only bound, not identify, absent the
7A35090F public modulus (not stored in this repo as a raw number; if
`analysis/armada_osint/keys.txt` contains a usable modulus+exponent, additionally compute
sig^e mod n for e=65537 and test the result against D1–D5). Shared prefix ≥ 4 bytes or any
pairwise GCD > 1 = finding.

## (c) Page-56 hash as key

- **Keystream over the 55 unsolved pages**: key = the 64 hash bytes, each mod 29.
  Decode = Vigenère-style additive over rune indices, grid = {sign ±1} × {atbash 0/1} ×
  {offset 0..63} = 256 decodes/page over the same 55-page set as R42-C3
  (`load_pages()[:-2]` from `analysis/run_stats.py`). Scoring: panel-R36 adjudication,
  identical glue to `analysis/round42/C3-auto-keys/run_c3.py`. Bar: standing free-null
  `bar_v3(N=256, L=nearest tabulated ≤ page length, "free")`, non-degenerate decodes only.
  **Hit rule**: a page crosses iff grid-max pmax ≥ its bar. Language scoring here IS the
  adjudicator, but it is the repo's standing instrument with its standing bar — not an
  ad-hoc screen.
  Also one secondary variant: key = hash bytes interpreted as the 128 hex NIBBLES mod 29
  (length-128 key), same grid (offsets 0..127, capped at 0..63 to keep the family size
  prereg'd: offsets 0..63), flagged in output as `nibble`.
- **XOR over canon_256**: hash repeated ×4 (and byte-reversed hash ×4) XOR each payload
  variant → 4 outputs through the (a) detector pipeline, same hit rule as (a).

## (d) T4 blobs — identify or bound

Per blob (and its `_flip` variant): size, sha256, whole-file Shannon entropy, windowed
entropy profile (4 KiB windows — report min/median/max), magic scan at ALL offsets for the
D4 list, decompression sweep: zlib (raw, +gzip, +auto headers) / bz2 / lzma attempted at
every offset where a plausible header byte occurs (gzip `\x1f\x8b`, bz2 `BZh[1-9]`, xz
`\xfd7zXZ`, zlib `\x78[\x01\x9c\xda\x5e]`) — cap 10,000 attempted offsets per blob per
format; base64 and base85 decode attempts on the `.hex`-as-text and on any ≥1 KiB
printable run. `T4_blob1_gunzip.bin` gets the same entropy + magic treatment.
**Bound statement**: if every sweep fails and windowed entropy stays ≥ 7.9 bits/byte
throughout, the blob is declared "indistinguishable from random/encrypted at this
granularity", with numbers.

## Reporting

RESULTS.md with all numbers (nulls stated plainly), ledger_rows.json with drafted rows
(NOT applied to LEDGER.json). No threshold moves after seeing data.
