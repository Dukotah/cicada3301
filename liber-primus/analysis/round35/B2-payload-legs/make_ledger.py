import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
cov1 = (" [R35-B2 2026-10-30: T2/folly legs now measured. Inputs fetched as data from github cicada-solvers/iddqd "
        "(folly.bin md5 0c7d18e8..., 3368 B, matches the recorded prefix; T2.bin = lp_outguessed/04.txt, 7524 B, matches the "
        "recorded entropy 7.978 / chi2 226 / byte0 0x40 and reproduces every stored T2 cross-XOR row to 4 d.p.; no full hash was "
        "recorded for T2). Original run.py exec'd unchanged (pycryptodome shim): the FULL stored result is reproduced by the "
        "superseded-canon comparator (struct-ID of all 3 blobs, 0 cipher hits over ~40 keys incl. blob:T2/blob:folly/blob:canon, "
        "12/12 XOR rows, 13 gpg rows). Promoted canon_256.bin: 0 cipher hits, 0 detector fires on all 12 XOR rows (min entropy "
        "7.0876; the 8 canon x T2/folly rows moved by <= 0.015 bits), 13 gpg rows identical. Controls PASS (AES plant; negative "
        "0/500 in the comparator and the promoted rerun; the first promoted run drew 1/500 from the script's unseeded urandom "
        "negative control, cipher results identical). Not changed.]")
nc1 = ("Corrected payload (R35-B2): canon-as-key over T2/folly and canon x T2/folly XOR rows re-run with matching inputs; no "
       "change. Residual: T2.bin identity rests on size + entropy + chi2 + byte0 and reproduction of the stored XOR rows, not a "
       "recorded full hash (none exists); T2 was fetched from a community OutGuess extract (iddqd lp_outguessed/04.txt), not "
       "regenerated (outguess absent).")
cov2 = (" [R35-B2 2026-10-30: folly and 2.jpg legs now run with fetched data (folly.bin md5 0c7d18e8... 3368 B; 2.jpg = iddqd "
        "liber-primus__images--unsolved/2.jpg, 595338 B, DQT signature 3e0f1ac7d0b3 and marker sequence equal the recorded "
        "fingerprint). Original b2_rsa_gpg.py, path/shim substitutions only. Superseded-canon comparator reproduces the stored "
        "b2_results.json on every substantive field (jpg_trailer_len 0, folly byte0 0xbf invalid chain, folly gpg/prepend parse "
        "failures, canon[:32] AES over folly, all canon legs; only the first-run gpg keybox-created stderr line and the random "
        "salt of the gpg-generated positive-control message differ). Promoted canon: folly and 2.jpg legs identical to "
        "comparator (the 2.jpg leg is the post-EOI trailer, length 0, i.e. an empty payload); canon[:32] AES over folly "
        "identical (idx<32 unchanged); canon legs as in R34-P1. Not changed.]")
nc2 = ("Corrected payload (R35-B2): folly and 2.jpg legs re-run; no change. Residual: 2.jpg identity rests on the JPEG "
       "structural fingerprint and size (no full hash was recorded); the 2.jpg leg only examines bytes after the final FFD9 "
       "(zero here); T2 (the OutGuess payload of 2.jpg) was covered by R30-B1 only, never by the B2 OpenPGP/gpg legs.")
P = {"$comment": "PROPOSED patches from round35/B2. NOT merged; coordinator applies.", "lane": "round35/B2", "date": "2026-10-30",
     "patches": [
         {"id": "R30-B1-BLOB-CRYPTO", "coverage_append": cov1,
          "not_covered_replace_item_containing": "NOT re-runnable (T2.bin and folly.bin are gitignored and absent)",
          "not_covered_replacement": nc1},
         {"id": "R30-B2-RSA-GPG", "coverage_append": cov2,
          "not_covered_replace_item_containing": "folly.bin and 2.jpg are absent, so their legs were not re-run",
          "not_covered_replacement": nc2}]}
json.dump(P, open("ledger_patches.json", "w"), indent=1)
led = {"lane": "round35/B2", "date": "2026-10-30", "entries": [{
    "id": "R35-B2-PAYLOAD-LEGS", "lane": "round35/B2", "round": 35, "date": "2026-10-30", "status": "audit",
    "hypothesis": "The previously unmeasured R30-B1 (canon-as-key over T2/folly, 8 canon x T2/folly XOR rows) and R30-B2 (folly, 2.jpg) legs change under the promoted canon_256.bin (sha 3b9b07d9...) relative to canon_256_superseded.bin.",
    "result": "NO CHANGE. Comparator reproduces the stored R30-B1 and R30-B2 results (inputs fetched from github cicada-solvers/iddqd). Promoted canon: 0 cipher hits, 0 detector fires, 12/12 XOR rows structureless (min H 7.0876), 13 gpg rows identical; B2 folly/2.jpg legs identical. These legs are now measured, null in the same sense as before.",
    "positive_control": "R30-B1 original AES-256-CBC plant recovered; R30-B2 original RSA-2048 plant flagged, real gpg message parses.",
    "negative_control": "R30-B1 0/500 (comparator and promoted rerun), 1/500 in the first promoted run (unseeded urandom); R30-B2 random not flagged.",
    "threshold": "A leg changes if the comparator fails to reproduce the stored result, a detector fires, or a verdict flips (R34-P1 rule).",
    "threshold_fixed_in_advance": True,
    "not_covered": [nc1, nc2, "Identity of T2.bin and 2.jpg to the original files is statistical/structural: no full hash was ever recorded."],
    "evidence": ["liber-primus/analysis/round35/B2-payload-legs/RESULTS.md", "liber-primus/analysis/round35/B2-payload-legs/PREREG.md",
                 "liber-primus/analysis/round35/B2-payload-legs/inputs.json"],
    "reopens_if": "Original T2.bin / 2.jpg bytes are found with a hash that differs from the fetched files."}]}
json.dump(led, open("ledger.json", "w"), indent=1)
