"""L6 instrument audit — run BEFORE any sweep.  PREREG s2.1.

Round 17 was bitten twice by an instrument it trusted:
  * `ks_hexchars` silently dropped the digits 0-9,
  * `max_skip=3` was underpowered on pads with constant byte runs.

The lesson generalises: audit every text->keystream converter before trusting it.  This
script does that by RE-DERIVING the defect rather than citing it, and proves that this
lane's shardable builders are identical to lib_padsweep's whole-blob builders.

Nothing here is a hypothesis test.  It writes out/audit.json.
"""
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L

rep = {"checks": []}


def chk(name, ok, detail):
    rep["checks"].append({"check": name, "PASS": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail, flush=True)
    return ok


# --------------------------------------------------------------- 1. the hexchars defect
blob = hashlib.sha512(b"L6-AUDIT").digest() * 64          # 4096 B, all 256 byte values likely
hx = blob.hex().upper()
kept = L.ks_hexchars(blob)
expect_full = len(hx)
af = sum(1 for c in hx if c in "ABCDEF")
digraphs = sum(1 for i in range(len(hx) - 1) if hx[i:i + 2] in ("AE", "EA"))
chk("ks_hexchars drops digits (R17/P1 defect, re-derived)",
    len(kept) < expect_full * 0.5 and len(kept) <= af,
    f"hex string {expect_full} chars, ks_hexchars kept {len(kept)}"
    f" ({100.0*len(kept)/expect_full:.1f}%), A-F count {af}, "
    f"AE/EA digraph sites {digraphs}. "
    f"SECOND, SMALLER DEFECT FOUND HERE and not recorded in R17: beyond dropping 0-9, "
    f"eng_to_idx also COLLAPSES the runic digraphs AE and EA, so ks_hexchars keeps "
    f"{af - len(kept)} fewer symbols than even the A-F subsequence "
    f"({af} A-F chars -> {len(kept)} symbols). "
    f"EXCLUDED from this lane: {X.EXCLUDED_BUILDERS['hexchars']}")

nb = X.b_nibbles(np.frombuffer(blob, dtype=np.uint8))
chk("ks_nibbles conserves length (the true hex reading)",
    len(nb) == expect_full and int(nb.max()) <= 15 and int(nb.min()) >= 0,
    f"{len(nb)} symbols for {expect_full} hex chars, range [{int(nb.min())},{int(nb.max())}]")

# --------------------------------------------------------------- 2. builder equivalence
a = np.frombuffer(blob, dtype=np.uint8)
pairs = [("mod29", L.ks_mod29), ("hi_nibble", L.ks_hi_nibble), ("lo_nibble", L.ks_lo_nibble),
         ("byte_scaled", L.ks_byte_scaled), ("prime_to_idx", L.ks_prime_to_idx),
         ("nibbles", L.ks_nibbles)]
allok = True
for name, ref in pairs:
    mine = X.BUILDERS[name][0](a)
    ok = np.array_equal(np.asarray(mine, dtype=np.int16), np.asarray(ref(blob), dtype=np.int16))
    allok &= ok
    chk(f"builder `{name}` == lib_padsweep", ok, f"{len(mine)} symbols")

# --------------------------------------------------------------- 3. sharding loses nothing
rng = np.random.default_rng(3301)
pad = rng.integers(0, 256, size=1 << 19, dtype=np.uint8)         # 512 KiB
C = L.nc.unsolved()
L.trigram_model()
for name in ("mod29", "nibbles"):
    K = X.build_full(pad, name)
    whole = L.dense_scan(K, C, sign=-1, keep=200)
    sh, noff, tot = X.sharded_scan(pad, name, -1, C, keep=200, shard_bytes=1 << 16)
    wset = {int(o): round(float(s), 5) for s, o in whole[:50]}
    sset = {int(o): round(float(s), 5) for s, o in sh[:200]}
    miss = [o for o in wset if o not in sset or sset[o] != wset[o]]
    chk(f"sharded_scan reproduces whole-blob dense_scan top-50 (`{name}`)",
        not miss, f"{len(wset)} top offsets checked, {len(miss)} mismatched; "
                  f"shard n_offsets={noff:,} total_symbols={tot:,}")

# --------------------------------------------------------------- 4. the beam, not rigid
#   AGENTS.md s4 lesson 2: rigid scores the CORRECT key at noise under the filter.
import skipdecode as sk
P = sk.eng_to_idx("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
                  "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND")
Kl = [int(x) for x in X.build_full(pad, "mod29")]
Ct, skips, used = sk.encipher_keyskip(P, Kl[5000:], sign=-1, supp=0.83)
bd = sk.beam_decode(Ct, Kl, sign=-1, o=5000, beam_w=400, max_skip=X.MS)
match = sum(1 for x, y in zip(bd["plain_idx"], P) if x == y) / len(P)
chk("skip-aware beam recovers a planted key at ms=8", match > 0.95 and bd["score"] > -5.5,
    f"beam score {bd['score']:.3f}, rune match {match:.3f}, skips planted {int(sum(skips))}")

# --------------------------------------------------------------- 5. the bar, at real N
import null as nullmod
tbl = {}
for n in (200, 10**6, 1.8e9, 1.8e10, 1.5e10):
    tbl[f"{int(n):,}"] = round(nullmod.threshold_for(int(n), segment_len=X.HEAD), 4)
rep["threshold_for_table"] = tbl
print("threshold_for:", json.dumps(tbl, indent=1))
chk("threshold_for is STRICTER than the habitual -5.5 at this lane's N",
    tbl["1,800,000,000"] > -5.5, f"threshold_for(1.8e9) = {tbl['1,800,000,000']}")

rep["all_pass"] = all(c["PASS"] for c in rep["checks"])
X.jdump(rep, os.path.join(X.OUT, "audit.json"))
print("\nAUDIT:", "PASS" if rep["all_pass"] else "FAIL")
sys.exit(0 if rep["all_pass"] else 1)
