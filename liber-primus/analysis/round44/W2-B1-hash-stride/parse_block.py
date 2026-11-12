#!/usr/bin/env python3
"""R44 W2-B1: parse the signed 991-byte liber-primus hash-block(s) into digest strides
and match every window against per-page candidate digests. Pure stdlib, no network.
PREREG: PREREG.md (sha256-stamped in run.log before first execution)."""
import base64, hashlib, json, math, os, sys
from collections import Counter

ROOT = "/mnt/c/Users/dukot/projects/cicada3301"
SP = f"{ROOT}/corpus/A-primary-artifacts/signed-payloads"
PGPM = f"{ROOT}/corpus/A-primary-artifacts/pgp/messages"
CELL = f"{ROOT}/liber-primus/analysis/round44/W2-B1-hash-stride"

BLOCKS = {
    "main": (f"{SP}/2014-01-liber-primus-hash-block.bin",
             "f8fa59ec133168d8aaf9c67d13152286eebcec191c5668f7f143a2c7764fc530",
             f"{PGPM}/2014-01-liber-primus-hash-block.asc"),
    "outguess01": (f"{SP}/2014-01-liber-primus-hash-block-outguess-01.bin",
             "6600c94b199f30c70c58f5800ccf80537b335122bd66768b6049241d8b20f318",
             f"{PGPM}/2014-01-liber-primus-hash-block-outguess-01.asc"),
    "outguess02": (f"{SP}/2014-01-liber-primus-hash-block-outguess-02.bin",
             "07d660d76e24dac92dc0350881ed7771263905a4a64f66c68f7f88ef77c9e07d",
             f"{PGPM}/2014-01-liber-primus-hash-block-outguess-02.asc"),
}
KEYID = bytes.fromhex("181F01E57A35090F")  # 7A35090F long id
WIDTHS = (16, 20, 32, 64)
ALGOS = {"md5": hashlib.md5, "sha1": hashlib.sha1,
         "sha256": hashlib.sha256, "sha512": hashlib.sha512}

# Gematria Primus (same constants as corpus/E-tooling/hash_runes.py)
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
IDX["ᛂ"] = 11  # encoding alias
TR = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B",
      "E","M","L","NG","OE","D","A","AE","Y","IA","EA"]


def pin_artifacts():
    """Premise gate: sizes, sha256, and issuer key-id inside each armored signature."""
    pins = {}
    for name, (binp, want, ascp) in BLOCKS.items():
        b = open(binp, "rb").read()
        assert len(b) == 991, f"{name}: size {len(b)} != 991"
        got = hashlib.sha256(b).hexdigest()
        assert got == want, f"{name}: sha256 mismatch {got}"
        txt = open(ascp, "r").read()
        sigb64 = txt.split("BEGIN PGP SIGNATURE-----")[1]
        lines = [l.strip() for l in sigb64.splitlines()
                 if l.strip() and not l.startswith(("Version", "-----", "="))]
        sig = base64.b64decode("".join(lines))
        assert KEYID in sig, f"{name}: issuer key-id 181F01E57A35090F not in signature packet"
        pins[name] = {"path": os.path.relpath(binp, ROOT), "bytes": len(b), "sha256": got,
                      "asc": os.path.relpath(ascp, ROOT), "issuer_keyid": "181F01E57A35090F",
                      "verify_log": "corpus/A-primary-artifacts/_logs/verify_sigs_run3.log: VALID"}
    return pins


def candidates():
    """The frozen PREREG Q3 grid: 354 byte-strings, labelled."""
    cands = []  # (label, bytes)
    canon_path = f"{ROOT}/liber-primus/data/krisyotam_runes.txt"
    canon = open(canon_path, encoding="utf8").read()
    segs = [s.strip() for s in canon.split("%")]
    assert len(segs) == 57, len(segs)
    for i, seg in enumerate(segs):
        tag = f"seg{i:02d}" + ("_ANEND" if i == 55 else "_PARABLE" if i == 56 else "")
        runes = [c for c in seg if c in IDX]
        idxs = [IDX[c] for c in runes]
        tru = "".join(TR[k] for k in idxs)
        cands += [(f"{tag}:raw", seg.encode("utf8")),
                  (f"{tag}:runes", "".join(runes).encode("utf8")),
                  (f"{tag}:idxcsv", ",".join(map(str, idxs)).encode()),
                  (f"{tag}:translit_up", tru.encode()),
                  (f"{tag}:translit_low", tru.lower().encode())]
    solved = json.load(open(f"{ROOT}/liber-primus/SOLVED-PAGES.json"))
    for p in solved["pages"]:
        pt = p["plaintext_transliteration"]
        lab = p["page_label"].replace(" ", "")
        cands += [(f"solved:{lab}:pt_up", pt.encode()),
                  (f"solved:{lab}:pt_low", pt.lower().encode())]
    for i in range(56):
        cands.append((f"img:p{i}.jpg", open(f"{ROOT}/liber-primus/data/relikd/p{i}.jpg", "rb").read()))
    cands.append(("img:0_wisdom.jpg", open(f"{ROOT}/liber-primus/data/relikd/0_wisdom.jpg", "rb").read()))
    unsolved_flat = ",".join(str(IDX[c]) for s in segs[:-2] for c in s if c in IDX)
    cands += [("whole:canon_file", canon.encode("utf8")),
              ("whole:unsolved_idxcsv", unsolved_flat.encode())]
    assert len(cands) == 57 * 5 + 10 + 57 + 2 == 354, len(cands)
    return cands


def digest_tables(cands):
    """lookup[w][prefix_bytes] -> list of hit descriptors."""
    lookup = {w: {} for w in WIDTHS}
    n_dig = 0
    for label, data in cands:
        for aname, afn in ALGOS.items():
            d = afn(data).digest()
            for orient, db in (("fwd", d), ("rev", d[::-1])):
                n_dig += 1
                for w in WIDTHS:
                    if len(db) >= w:
                        desc = f"{label}|{aname}|{orient}" + ("" if len(db) == w else f"|trunc{w}")
                        lookup[w].setdefault(db[:w], []).append(desc)
    return lookup, n_dig


def scan(block, name, lookup):
    hits = []
    n_windows = 0
    for w in WIDTHS:
        tab = lookup[w]
        for off in range(0, len(block) - w + 1):
            n_windows += 1
            win = bytes(block[off:off + w])
            if win in tab:
                for desc in tab[win]:
                    hits.append({"block": name, "offset": off, "width": w,
                                 "aligned": off % w == 0, "candidate": desc,
                                 "window_hex": win.hex()})
    return hits, n_windows


def side_stats(blocks):
    out = {}
    allw = Counter()
    for name, b in blocks.items():
        c = Counter(b)
        n = len(b)
        ent = -sum(v / n * math.log2(v / n) for v in c.values())
        chi2 = sum((c.get(i, 0) - n / 256) ** 2 / (n / 256) for i in range(256))
        wins = Counter(bytes(b[i:i + 20]) for i in range(n - 19))
        dups = {k.hex(): v for k, v in wins.items() if v > 1}
        for k in wins:
            allw[k] += wins[k]
        out[name] = {"entropy_bits_per_byte": round(ent, 4), "chi2_255df": round(chi2, 1),
                     "dup_20byte_windows_within": dups}
    out["dup_20byte_windows_across_blocks"] = {k.hex(): v for k, v in allw.items() if v > 1}
    out["remainder_arithmetic"] = {"991_is_prime": True,
        "w20": "49*20+11", "w32": "30*32+31", "w16": "61*16+15", "w64": "15*64+31"}
    return out


def main():
    pins = pin_artifacts()
    print("[gate] artifact identity pinned: 3 blocks, 991B each, issuer 181F01E57A35090F")
    cands = candidates()
    lookup, n_dig = digest_tables(cands)
    print(f"[grid] {len(cands)} candidate byte-strings -> {n_dig} digests")

    blocks = {n: open(p, "rb").read() for n, (p, _, _) in BLOCKS.items()}

    # ---- PLANT (identical glue, run FIRST) ----
    seg0_runes = cands[1]  # seg00:runes by construction
    assert seg0_runes[0] == "seg00:runes"
    plant = bytearray(blocks["main"])
    inj_a = hashlib.sha1(seg0_runes[1]).digest()           # aligned, offset 140 = 7*20
    inj_b = hashlib.md5(open(f"{ROOT}/liber-primus/data/relikd/p0.jpg", "rb").read()).digest()
    plant[140:160] = inj_a
    plant[333:349] = inj_b                                  # unaligned
    open(f"{CELL}/plant.bin", "wb").write(bytes(plant))
    phits, _ = scan(plant, "PLANT", lookup)
    got_a = any(h["offset"] == 140 and h["width"] == 20 and h["aligned"]
                and h["candidate"].startswith("seg00:runes|sha1|fwd") for h in phits)
    got_b = any(h["offset"] == 333 and h["width"] == 16 and not h["aligned"]
                and h["candidate"].startswith("img:p0.jpg|md5|fwd") for h in phits)
    assert got_a and got_b, f"PLANT FAILED: aligned={got_a} unaligned={got_b}"
    plant_extra = [h for h in phits if h["offset"] not in
                   range(125, 160) and not (318 <= h["offset"] <= 348)]
    print(f"[plant] PASSED: both injections recovered (aligned sha1 @140, unaligned md5 @333); "
          f"{len(phits)} plant hits, {len(plant_extra)} outside injection zones")

    # ---- REAL SCAN ----
    all_hits, n_windows = [], 0
    for name, b in blocks.items():
        h, nw = scan(b, name, lookup)
        all_hits += h
        n_windows += nw
    stats = side_stats(blocks)

    entries_per_width = {w: sum(len(v) for v in lookup[w].values()) for w in WIDTHS}
    efp = sum((991 - w + 1) * 3 * entries_per_width[w] / 2 ** (8 * w) for w in WIDTHS)

    results = {
        "cell": "R44-W2-B1-hash-stride", "date": "2026-11-09",
        "artifact_pins": pins,
        "positive_control": {"status": "passed",
            "detail": "copy of main block with sha1(seg00 runes-only utf8) injected at aligned "
                      "offset 140 and md5(relikd/p0.jpg bytes) at unaligned offset 333; both "
                      "recovered by the identical scan glue with correct attribution"},
        "grid": {"n_candidates": len(cands), "n_digests": n_dig,
                 "entries_per_width": {str(k): v for k, v in entries_per_width.items()},
                 "widths": list(WIDTHS), "algos": list(ALGOS), "orientations": ["fwd", "rev"]},
        "scan": {"n_blocks": 3, "n_windows": n_windows,
                 "expected_false_positives_uniform_null": efp,
                 "n_matches": len(all_hits), "matches": all_hits},
        "side_stats": stats,
        "verdict": ("FLAGGED-FOR-ORACLE" if all_hits else
                    "NEGATIVE (structural, measured): 0 window<->digest matches"),
    }
    json.dump(results, open(f"{CELL}/results.json", "w"), indent=1)
    print(f"[scan] {n_windows} windows x grid; matches={len(all_hits)}; "
          f"E[FP|uniform]={efp:.2e}")
    for name in blocks:
        s = stats[name]
        print(f"[stats] {name}: H={s['entropy_bits_per_byte']} b/B chi2={s['chi2_255df']} "
              f"dup20={len(s['dup_20byte_windows_within'])}")
    print(f"[stats] cross-block dup 20B windows: {len(stats['dup_20byte_windows_across_blocks'])}")
    print("[verdict]", results["verdict"])


if __name__ == "__main__":
    main()
