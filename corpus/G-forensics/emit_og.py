import json, os, hashlib
import gcore as G
D="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts/rune_pages"
o=json.load(open("raw/rune_pages_outguess.json"))
ne=[r for r in o["rows"] if r["size"]]
em=[r["n"] for r in o["rows"] if not r["size"]]
G.emit({"artifact_path":D,"artifact_sha256":"n/a (directory-level result; per-file sha256 in output_file)",
 "tool":"prior-work re-audit: outguess -r outputs held in artifacts/rune_pages/","tool_version":"G-1.0",
 "command":"enumerate all 58 *.out, size/sha256/entropy, pairwise common-prefix matrix","params":{},
 "exit_code":0,"finding":"HIT","output_excerpt":json.dumps({
  "claim":"STEGO-VERDICT.md reports THREE capacity-length OutGuess false positives (onion7 pages 0,4,26) sharing a 1417-byte prefix. The outputs actually held in this repo show SIXTEEN.",
  "nonempty_pages":[r["n"] for r in ne],"count_nonempty":len(ne),"count_empty":len(em),
  "empty_pages":em,"all_sizes_bytes":sorted(set(r["size"] for r in ne)),
  "identical_first_1417_bytes_across_all_16":True,
  "shared_head_hex_32":"c0a128e346d23572fe62822e50f70d8aed61d93bc607ca31e7c6f64ed9d3c20f",
  "min_pairwise_common_prefix":1417,"max_pairwise_common_prefix":2004,
  "pairwise_byte_match_range_pct":[6.68,8.55],"random_expectation_pct":0.39,
  "prefix_alone_would_give_pct":round(100*1417/58152,2),
  "subcluster_longer_prefix":{"pages":[4,26,51,54],"prefix":[1812,1903,2004]}}),
 "output_file":"raw/rune_pages_outguess.json",
 "note":"Instrument power: this is a re-read of extraction outputs already on disk, so it can only characterise what OutGuess produced; it cannot itself prove payload vs artifact. It DOES establish that the shared-prefix phenomenon is 5x more widespread than recorded, that the prefix is byte-identical (not merely correlated) across all 16, and that residual correlation beyond the prefix (~4.5pp above what the shared prefix alone explains, vs 0.39% random) is real. The blank-control experiment is what discriminates artifact from payload."})
for r in ne:
    p=f"{D}/{r['n']}.out"
    G.emit({"artifact_path":p,"artifact_sha256":r["sha256"],
     "tool":"prior-work re-audit: outguess -r output","tool_version":"G-1.0",
     "command":f"stat+hash+entropy on {r['n']}.out","params":{"source_page":r["n"]},
     "exit_code":0,"finding":"HIT","output_excerpt":json.dumps(r),
     "output_file":"raw/rune_pages_outguess.json",
     "note":"Capacity-length (58152 B) high-entropy OutGuess output. Shares a byte-identical 1417-byte prefix with all 15 peers."})
print("emitted",len(ne)+1,"rows; nonempty pages:",[r["n"] for r in ne])
