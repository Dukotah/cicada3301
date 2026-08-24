"""Round 16 lane P1 -- acquire the Bitcoin blockchain pad candidates.

WHY
---
The seed census lumps "leaves no seed" together with "unreachable". The Bitcoin blockchain
is the counter-example: full-entropy, seedless, permanently public, timestamped, ordered.
Block hashes are the canonical "randomness nobody can forge and everybody can verify
later" and a 2013-14 crypto-literate author had every cultural reason to reach for them.

WHAT THIS FETCHES
-----------------
Blockchair's public per-day block dumps (one TSV row per block, columns include
`id` = height, `hash`, `merkle_root`, `nonce`, `time`).  Days 2009-01-03 .. 2014-06-01,
which is heights 0 .. ~305,000 -- i.e. everything that existed before LP2 was posted
(2014-01-05, height ~277,000) plus headroom.

  https://gz.blockchair.com/bitcoin/blocks/blockchair_bitcoin_blocks_YYYYMMDD.tsv.gz

VERIFICATION (this repo has twice been burned by files accepted as what they claimed)
-------------------------------------------------------------------------------------
  * heights must be contiguous 0..max with no gaps and no duplicates;
  * five independently-known block hashes are asserted byte-exact (genesis, 1, 170,
    100000, 210000) plus the genesis merkle root and the genesis nonce;
  * every emitted pad file's SHA-256 is written into data/MANIFEST.json.

REGENERATE
----------
  python liber-primus/analysis/round16/P1_blockchain/fetch.py

Outputs (all gitignored -- see .gitignore):
  data/blocks.tsv          height<TAB>hash<TAB>merkle_root<TAB>nonce<TAB>unixtime
  data/hash_display.bin    32 B/block, big-endian *display* order (hex as everyone sees it)
  data/hash_internal.bin   32 B/block, byte-reversed (little-endian, as stored on the wire)
  data/merkle_display.bin  32 B/block
  data/merkle_internal.bin 32 B/block
  data/nonce_le.bin         4 B/block, little-endian (header order)
  data/time_le.bin          4 B/block, little-endian (header order)
  data/MANIFEST.json
"""
import os, sys, io, gzip, json, time, hashlib, datetime, concurrent.futures as cf
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
BASE = "https://gz.blockchair.com/bitcoin/blocks/blockchair_bitcoin_blocks_%s.tsv.gz"
START = datetime.date(2009, 1, 3)
END   = datetime.date(2014, 6, 1)          # height ~305,000
CACHE = os.path.join(DATA, "raw")

# independently known values (bitcoin whitepaper era / block explorers / BIP text)
KNOWN_HASH = {
    0:      "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",
    1:      "00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048",
    170:    "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee",
    100000: "000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506",
    210000: "000000000000048b95347e83192f69cf0366076336c639f9b7228e9ba171342e",
}
KNOWN_MERKLE = {
    0: "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
}
KNOWN_NONCE = {0: 2083236893}


def days():
    d, out = START, []
    while d <= END:
        out.append(d.strftime("%Y%m%d"))
        d += datetime.timedelta(days=1)
    return out


def fetch_day(sess, ymd):
    """Return raw gz bytes for one day, cached on disk. None if that day has no dump."""
    p = os.path.join(CACHE, "%s.tsv.gz" % ymd)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return p
    for attempt in range(10):
        try:
            r = sess.get(BASE % ymd, timeout=120)
        except Exception:
            time.sleep(1.5 * (attempt + 1))
            continue
        if r.status_code == 404:
            return None                     # days with no blocks (early 2009) are absent
        if r.status_code == 200 and r.content[:2] == b"\x1f\x8b":
            with open(p, "wb") as f:
                f.write(r.content)
            return p
        time.sleep(1.5 * (attempt + 1))     # blockchair throttles bursts; back off
    raise RuntimeError("failed to fetch %s (last status %s)" % (ymd, r.status_code))


def download_all(workers=6):
    os.makedirs(CACHE, exist_ok=True)
    ymds = days()
    got = {}
    sessions = [requests.Session() for _ in range(workers)]
    for s in sessions:
        s.headers["User-Agent"] = "cicada3301-round16-P1/1.0"

    def job(i_ymd):
        i, ymd = i_ymd
        return ymd, fetch_day(sessions[i % workers], ymd)

    with cf.ThreadPoolExecutor(workers) as ex:
        for n, (ymd, p) in enumerate(ex.map(job, list(enumerate(ymds))), 1):
            if p:
                got[ymd] = p
            if n % 100 == 0:
                print("  fetched %d/%d days (%d with blocks)" % (n, len(ymds), len(got)),
                      flush=True)
    return [got[k] for k in sorted(got)]


def parse(paths):
    rows = {}
    for p in paths:
        with gzip.open(p, "rt", encoding="utf-8", errors="strict") as f:
            hdr = f.readline().rstrip("\n").split("\t")
            ci = {c: i for i, c in enumerate(hdr)}
            for need in ("id", "hash", "merkle_root", "nonce", "time"):
                if need not in ci:
                    raise RuntimeError("%s: missing column %r" % (p, need))
            for line in f:
                v = line.rstrip("\n").split("\t")
                if len(v) < len(hdr):
                    continue
                h = int(v[ci["id"]])
                t = datetime.datetime.strptime(v[ci["time"]], "%Y-%m-%d %H:%M:%S")
                rec = (v[ci["hash"]].strip(), v[ci["merkle_root"]].strip(),
                       int(v[ci["nonce"]]), int(t.replace(
                           tzinfo=datetime.timezone.utc).timestamp()))
                if h in rows and rows[h] != rec:
                    raise RuntimeError("height %d disagrees between dumps" % h)
                rows[h] = rec
    return rows


def verify(rows):
    hs = sorted(rows)
    assert hs[0] == 0, "no genesis block"
    gaps = [h for h, e in zip(hs, range(hs[0], hs[-1] + 1)) if h != e]
    if gaps:
        raise RuntimeError("height sequence not contiguous; first break near %d" % gaps[0])
    for h, want in KNOWN_HASH.items():
        got = rows[h][0]
        if got != want:
            raise RuntimeError("block %d hash mismatch\n  got  %s\n  want %s" % (h, got, want))
        if len(got) != 64 or int(got, 16) is None:
            raise RuntimeError("block %d hash is not 32 hex bytes" % h)
    for h, want in KNOWN_MERKLE.items():
        if rows[h][1] != want:
            raise RuntimeError("block %d merkle mismatch" % h)
    for h, want in KNOWN_NONCE.items():
        if rows[h][2] != want:
            raise RuntimeError("block %d nonce mismatch" % h)
    bad = [h for h in hs if len(rows[h][0]) != 64 or len(rows[h][1]) != 64]
    if bad:
        raise RuntimeError("%d rows with malformed 32-byte fields, first %d" % (len(bad), bad[0]))
    return hs


def emit(rows, hs):
    hd = bytearray(); hi = bytearray(); md = bytearray(); mi = bytearray()
    nz = bytearray(); tm = bytearray()
    with open(os.path.join(DATA, "blocks.tsv"), "w", encoding="ascii", newline="\n") as f:
        f.write("height\thash\tmerkle_root\tnonce\ttime\n")
        for h in hs:
            bh, bm, non, ts = rows[h]
            f.write("%d\t%s\t%s\t%d\t%d\n" % (h, bh, bm, non, ts))
            a = bytes.fromhex(bh); b = bytes.fromhex(bm)
            hd += a; hi += a[::-1]
            md += b; mi += b[::-1]
            nz += (non & 0xFFFFFFFF).to_bytes(4, "little")
            tm += (ts & 0xFFFFFFFF).to_bytes(4, "little")
    out = {"hash_display.bin": bytes(hd), "hash_internal.bin": bytes(hi),
           "merkle_display.bin": bytes(md), "merkle_internal.bin": bytes(mi),
           "nonce_le.bin": bytes(nz), "time_le.bin": bytes(tm)}
    man = {"source": BASE, "days": "%s..%s" % (START, END),
           "n_blocks": len(hs), "height_min": hs[0], "height_max": hs[-1],
           "regenerate": "python liber-primus/analysis/round16/P1_blockchain/fetch.py",
           "known_hash_checks": KNOWN_HASH, "files": {}}
    for name, blob in out.items():
        p = os.path.join(DATA, name)
        with open(p, "wb") as f:
            f.write(blob)
        man["files"][name] = {"bytes": len(blob),
                              "sha256": hashlib.sha256(blob).hexdigest()}
        print("  wrote %-22s %10d B  sha256=%s" % (name, len(blob),
                                                   man["files"][name]["sha256"][:16]))
    with open(os.path.join(DATA, "MANIFEST.json"), "w") as f:
        json.dump(man, f, indent=2)
    return man


def main():
    os.makedirs(DATA, exist_ok=True)
    print("[1/4] downloading blockchair daily block dumps %s..%s" % (START, END), flush=True)
    paths = download_all()
    print("      %d daily dumps on disk" % len(paths), flush=True)
    print("[2/4] parsing", flush=True)
    rows = parse(paths)
    print("      %d block rows" % len(rows), flush=True)
    print("[3/4] verifying (contiguity + 5 known hashes + genesis merkle/nonce)", flush=True)
    hs = verify(rows)
    print("      OK: heights %d..%d contiguous, all spot-checks byte-exact" % (hs[0], hs[-1]))
    print("[4/4] emitting pads", flush=True)
    man = emit(rows, hs)
    print(json.dumps({k: v for k, v in man.items() if k != "known_hash_checks"}, indent=2))


if __name__ == "__main__":
    main()
