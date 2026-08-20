import json
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/onions_ibotpeaches/onions__imgur.com__hkdgl.png"
S="f4be4b74b1cc1479f9482d0e670375450b43d1b500a991de644f1cc9dea00217"
G.emit({"artifact_path":P,"artifact_sha256":S,
 "tool":"bit-plane LSB analysis (PIL+numpy) - ADJUDICATED","tool_version":"G-1.0",
 "command":"per-channel bit-plane entropy profile bit0..bit7; distinct-colour census","params":{},"exit_code":0,
 "finding":"NEGATIVE",
 "output_excerpt":json.dumps({"supersedes":"the automatic HIT flag on this file (bit0 entropy>0.9999)",
  "why_the_flag_fires":"bit0 plane entropy is ~1.0 in all 3 channels",
  "why_it_is_nonetheless_negative":"bit planes 0,1,2,3 AND 4 are ALL ~1.0 entropy (ch0: 0.99998/0.99997/1.0/0.99998/0.99997). A raw-LSB payload occupies the low plane(s) and leaves the higher planes structured. Uniform maximal randomness through bit4 means the IMAGE ITSELF is noise-like, not that bit0 was overwritten.",
  "corroborating":"136x363 px with 28,470 distinct RGB triples over 49,368 pixels (58% of pixels a unique colour) - a heavily dithered/noisy raster",
  "bitplane_entropies_ch0":[0.99998,0.99997,1.0,0.99998,0.99997,0.99911,0.99838,0.92408],
  "bitplane_entropies_ch2":[0.99998,0.99999,0.99998,0.99997,0.99609,0.97202,0.98936,0.49836],
  "extraction_attempted":"row-major and column-major RGB-interleaved LSB extraction, 18,513 B each; zlib and raw-deflate both fail; printable fraction 0.369/0.381 (chance ~0.37); longest ASCII runs 8-10 chars, all gibberish"}),
 "output_file":"raw/lsb_extract/",
 "note":"Power statement: this test WOULD have detected an unencrypted or compressed raw-LSB payload in any channel or bit plane, row- or column-major. It CANNOT distinguish an encrypted, keyed-scatter LSB payload from image noise - and in an image whose upper bit planes are already maximally random, no statistical LSB test can. For THIS carrier the LSB channel is effectively untestable by statistics alone; only a correct key would settle it. Recorded as NEGATIVE-with-limited-power, not as closure."})
G.emit({"artifact_path":P,"artifact_sha256":S,"tool":"PNG chunk parse + embedded-timestamp extraction",
 "tool_version":"G-1.0","command":"walk PNG chunks; decode tIME","params":{},"exit_code":0,"finding":"HIT",
 "output_excerpt":json.dumps({"artifact_identity":"2012 Round 2 Book Hint (per onions__imgur.com__README.md; md5 verified df991ade67ee90a3fabf445fa3530ae5)",
   "tIME":"2012-01-11T07:19:29Z",
   "significance":"This is the ONLY real embedded timestamp anywhere in the 486 artifacts held. Every one of the 116 JPEGs carries the null ICC creation date 0000-00-00T00:00:00Z.",
   "chunks":["IHDR","sRGB","bKGD","pHYs","tIME","IDAT x11","IEND"],
   "idat_chunk_size":8192,"trailing_after_IEND":0,"dimensions":[363,136],
   "pHYs":"2835x2835 px/m (=72 dpi), unit=metre"}),
 "output_file":"raw/timestamps.json",
 "note":"Caveat stated plainly: tIME records when this PNG was ENCODED, which may be Cicada's own authoring or an imgur/host re-encode at upload. It cannot be distinguished from the file alone. Either way it pins the artifact to 2012-01-11 07:19:29 UTC, which is consistent with the documented Round-2 release window and is a harder date than any prose source in this repo. Unpulled lead: no other 2012-chain artifact has been checked for a tIME/EXIF date because the 2012 chain is otherwise absent from the corpus (Lane A gap)."})
print("emitted")
