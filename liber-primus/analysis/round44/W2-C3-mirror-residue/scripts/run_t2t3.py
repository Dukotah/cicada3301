"""W2-C3 step 4 — T2_2jpg / T3-folly / canon_256 structural battery, ONLY on transforms
NOT in R29-L2 / R30-B1 / R43-F6 coverage (PREREG §2, §4.4):
  - all-offset magic + decompression under id/rev/xff/revxff (R29-L2 was a header-position
    hunt, not an all-offset decompression sweep; F6 ran this battery on T4 blobs only);
  - NEW transforms: rot5, rot6, nibble-swap, per-byte bit-reverse, delta, cumsum, xor-index
    (R29-L2 covered rotate 1,2,3,4,7 header-hunt only);
  - windowed entropy, smallest period, palindrome core.
NO cipher keys, NO pad/keystream legs (those rows stay closed).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
sys.path.insert(0, HERE)
import residue_lib as R

BLOBS = {
    "T2_2jpg": os.path.join(LP, "analysis", "armada_osint", "extracts", "T2.bin"),
    "T3_folly": os.path.join(LP, "analysis", "armada_osint", "artifacts", "folly.bin"),
    "canon_256": os.path.join(LP, "analysis", "pp49_51", "canon_256.bin"),
}
EXPECT = {  # premise gate: identity pins from R35-B2 inputs.json / promoted canon
    "T2_2jpg": ("35d31e61275c6b0420e7729161d5f6272122ea7edb87076fe84f3fe3c70af6db", 7524),
    "T3_folly": ("7e5ec097728197f5c0dba0729980565658fba486965809ffa25e3910a31c385a", 3368),
    "canon_256": (None, 256),
}
ALL_T = dict(R.CORE)
ALL_T.update(R.EXT)

OUT = {}
for name, path in BLOBS.items():
    b = open(path, "rb").read()
    exp_sha, exp_len = EXPECT[name]
    ok = (len(b) == exp_len) and (exp_sha is None or R.sha(b) == exp_sha)
    rep = {"path": os.path.relpath(path, LP), "premise_ok": bool(ok), "sha256": R.sha(b)}
    if not ok:
        rep["verdict"] = "UNAVAILABLE-BY-PREMISE (identity pin failed)"
        OUT[name] = rep
        continue
    rep.update(R.identify(b, transforms=ALL_T, decomp_headers_only=False))
    # count decompression hits that produce LOW-entropy (structured) output
    structured = []
    for tname, tr in rep["transforms"].items():
        for p in tr["decompressed"]:
            if p["out_entropy"] < 7.0 and p["out_bytes"] >= 64:
                structured.append({"transform": tname, **p})
    rep["structured_decompressions"] = structured
    OUT[name] = rep
    print(name, "premise_ok", ok, "| structured decompressions:", len(structured),
          "| win_H", rep["win_entropy_min"], "-", rep["win_entropy_max"],
          "| period", rep["smallest_period_16k"], "| palin_core", rep["palindrome_core"],
          flush=True)

json.dump(OUT, open(os.path.join(CELL, "results", "t2t3_battery.json"), "w"), indent=1)
print("WROTE results/t2t3_battery.json")
