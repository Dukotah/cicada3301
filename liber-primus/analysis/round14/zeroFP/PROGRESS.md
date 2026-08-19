# R14-B zeroFP — PROGRESS

- [x] `python3 tests/validate.py` -> ALL VALIDATIONS PASSED (2026-08-19)
- [x] sources located (see below)
- [x] PREREG.md written
- [ ] E-01 RSA/PKCS#1
- [ ] E-02 meta-parameters
- [ ] H-03 micro-crosses
- [ ] H-01 onion HTTP anomalies
- [ ] RESULTS.md

## Source inventory (verified this run)
| object | path | note |
|---|---|---|
| pp49-51 payload ("String 4") | `analysis/pp49_51/canon_256.bin` | 256 B; `canon_256_decpref.bin` = decimal-witness variant |
| 2014 onion hex strings 1-3 | `analysis/armada_osint/onions_ibotpeaches/rsahex_{cu343_761,fv7ly_1033,avowy_3301}.bin` | 256 B each |
| 2013 cookies | `analysis/armada20/key_cookie167.txt`, `key_cookie761.txt` | 32 B each |
| 2012 modulus (365 bit) | `analysis/armada_osint/artifacts/raw/2012.md:875` | Crypt::RSA dump, e=65537 |
| 2013/14 modulus (430 bit) | `analysis/armada_osint/artifacts/raw/2014.md:128` | e=65537 |
| 3301 PGP key 7A35090F | `analysis/round10/L6-archives/fetched/jaxonkuipers/comms/cicada-3301-public-key.asc` | two 4096-bit RSA moduli (primary pkt6 + subkey pkt14), e=65537 |
| 2012 P.S. digit string | `analysis/armada_osint/artifacts/raw/2012.md:1413-1415` | 128 digits |
| rune stream | `analysis/seed_sweep/ct.bin` | 12,956 runes; 86 doublets, 85 gaps, 458 F-runes(idx 0) — recomputed this run |
| quadgram model | `analysis/seed_sweep/ngram.bin` | float32 29^4 |
| onion HTML | `analysis/armada_osint/onions_ibotpeaches/onions__*index.html` | 12 pages |
