#!/usr/bin/env python3
"""R44 W2-C4 — positive controls PC1/PC2/PC3 through the cell's own glue (PREREG)."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.abspath(os.path.join(HERE, ".."))
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
sys.path.insert(0, HERE)
import sweep as sw

res = {}

# ---- PC1: the author's own artifact, keyless, through the driver glue ----
img_1033 = os.path.join(LP, "analysis", "armada_osint", "artifacts", "dl_1033.jpg")
r = sw.row_for("og", "1033", "pc1", None, img_1033, "/dev/shm/c4_pc1.bin")
res["PC1"] = dict(row=r, passed=bool(r[-1]) and r[4] == 102 and r[5] == 1498 and r[9] == 1)
print("PC1 (1033.jpg keyless, expect seed 102 len 1498, F1 armor):", res["PC1"])

# ---- PC2: keyed outguess plant in the hunted shape (armored PGP) ----
kp = json.load(open(os.path.join(CELL, "results", "keys_per_page.json")))["keys"]
key12 = kp["12"][0]                       # A1 key of page 12 (PREREG)
plant = ("-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n"
         "R44 W2-C4 PLANTED CONTROL. NOT A REAL 3301 PAYLOAD.\n"
         "-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.11 (GNU/Linux)\n\n"
         "iQIcBAEBAgAGBQJSYplant\n-----END PGP SIGNATURE-----\n").encode()
open("/dev/shm/c4_plant.txt", "wb").write(plant)
sw.stage_pages()
stego12 = "/dev/shm/c4_p12_stego.jpg"
subprocess.run([sw.OUTGUESS, "-k", key12, "-d", "/dev/shm/c4_plant.txt",
                f"{sw.SHM}/p12.jpg", stego12], capture_output=True, check=True)
hits = []
for k in kp["12"] + [None]:
    r = sw.row_for("og", "12S", "pc2", k, stego12, "/dev/shm/c4_pc2.bin")
    if r[-1]:
        hits.append((k, r))
pc2_ok = any(k == key12 and r[9] == 1 for k, r in hits)
res["PC2"] = dict(planted_key=key12, flagged_keys=[k for k, _ in hits], passed=pc2_ok)
print("PC2 (outguess keyed plant via page-12 keylist):", res["PC2"])

# ---- PC3: steghide plant under the page-33 gematria-sum key ----
key33 = next(k for k in kp["33"] if k.isdigit() and len(k) > 2)   # D1 page prime-sum
stego33 = "/dev/shm/c4_p33_stego.jpg"
subprocess.run([sw.STEGHIDE, "embed", "-cf", f"{sw.SHM}/p33.jpg",
                "-ef", "/dev/shm/c4_plant.txt", "-sf", stego33, "-p", key33, "-f"],
               capture_output=True, check=True)
hits3 = []
for k in kp["33"]:
    r = sw.row_for("sh", "33S", "pc3", k, stego33, "/dev/shm/c4_pc3.bin")
    if r[-1]:
        hits3.append((k, r))
pc3_ok = len(hits3) >= 1 and all(k == key33 for k, _ in hits3)
res["PC3"] = dict(planted_key=key33, flagged_keys=[k for k, _ in hits3], passed=pc3_ok)
print("PC3 (steghide keyed plant via page-33 keylist):", res["PC3"])

res["all_passed"] = all(res[p]["passed"] for p in ("PC1", "PC2", "PC3"))
json.dump(res, open(os.path.join(CELL, "results", "controls.json"), "w"),
          indent=1, default=str)
print("ALL CONTROLS PASSED:" , res["all_passed"])
sys.exit(0 if res["all_passed"] else 1)
