"""Round 16 lane P2 - acquire PUBLIC RANDOMNESS ARCHIVES as candidate one-time pads.

Why this file exists
--------------------
`analysis/round10/L5-seed32/CENSUS.md:87-94` closes the search programme by placing
`random.org` in the same bucket as `/dev/urandom` and physical dice - "nothing can touch
it". That merge is wrong for any source that *publishes and archives* its output. The NIST
Randomness Beacon has emitted a signed 512-bit value every 60 s since 2013-09-05T15:39:00Z,
four months before LP2 was posted, and **every one of those 2013-2018 records is still
served today** by the legacy v1 REST endpoint. It is a seedless full-entropy pad with a
public, dated, byte-exact record. Nobody has swept it.

Endpoints, measured 2026-08-19
------------------------------
    LIVE   https://beacon.nist.gov/rest/record/<unix_seconds>   -> v1 XML record
           genesis  ts=1378395540 (2013-09-05T15:39:00Z), previousOutputValue = 0*128
           last     ts=1545840420 (2018-12-26T16:07:00Z)
           requires a User-Agent header (bare urllib gets HTTP 403)
    NOT USEFUL FOR PRE-2014
           https://beacon.nist.gov/beacon/2.0/pulse/time/<ms>  clamps to chain 1 pulse 1,
           which is 2018-07-23T19:26:00Z. The v2 API does not serve the v1 era at all.

Self-verification
-----------------
v1 records are hash-chained: record[n].previousOutputValue == record[n-1].outputValue.
This script checks every adjacent pair it fetched and reports the link rate, so the corpus
proves itself rather than being trusted. (This repo has twice been burned by a file accepted
as what it claimed to be; a chain check is stronger than spot-checking "a couple of pulses".)

Regenerate
----------
    python fetch.py --start 2013-09-05 --end 2014-01-06 --workers 48
    python fetch.py --verify           # chain-link check + pad assembly only
Output (gitignored): data/v1/YYYY-MM-DD.jsonl , data/pad_<field>_<window>.bin
"""
import argparse, datetime as dt, json, os, sys, threading, time
import concurrent.futures as cf
import re

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
V1DIR = os.path.join(DATA, "v1")
BASE = "https://beacon.nist.gov/rest/record/"
UA = {"User-Agent": "cicada3301-liber-primus-research/1.0 (round16 lane P2)"}
GENESIS = 1378395540          # 2013-09-05T15:39:00Z
V1_LAST = 1545840420          # 2018-12-26T16:07:00Z

FIELDS = ("timeStamp", "seedValue", "previousOutputValue", "outputValue", "statusCode")
_loc = threading.local()


def _sess():
    s = getattr(_loc, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        a = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=0)
        s.mount("https://", a)
        _loc.s = s
    return s


def parse_record(xml):
    out = {}
    for f in FIELDS:
        m = re.search(r"<%s>(.*?)</%s>" % (f, f), xml, re.S)
        if not m:
            return None
        out[f] = m.group(1).strip()
    out["timeStamp"] = int(out["timeStamp"])
    out["statusCode"] = int(out["statusCode"])
    return out


def fetch_one(ts, tries=3):
    for k in range(tries):
        try:
            r = _sess().get(BASE + str(ts), timeout=30)
            if r.status_code == 200:
                rec = parse_record(r.text)
                if rec:
                    return rec
                return None
            if r.status_code in (404, 400):
                return None
        except Exception:
            time.sleep(0.4 * (k + 1))
    return "ERR"


def day_path(d):
    return os.path.join(V1DIR, d.isoformat() + ".jsonl")


def fetch_day(d, workers, log=sys.stdout):
    """Fetch every minute of UTC day `d`. Idempotent: resumes a partial shard."""
    p = day_path(d)
    have = {}
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        r = json.loads(line)
                        have[r["timeStamp"]] = r
                    except Exception:
                        pass
    t0 = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
    want = [t for t in range(t0, t0 + 86400, 60)
            if GENESIS <= t <= V1_LAST and t not in have]
    if want:
        t = time.time()
        with cf.ThreadPoolExecutor(workers) as ex:
            for ts, rec in zip(want, ex.map(fetch_one, want)):
                if isinstance(rec, dict):
                    have[ts] = rec
        with open(p, "w", encoding="utf-8") as f:
            for ts in sorted(have):
                f.write(json.dumps(have[ts], separators=(",", ":")) + "\n")
        print(f"  {d} fetched {len(want)} missing -> {len(have)} records "
              f"({time.time() - t:.0f}s)", file=log, flush=True)
    else:
        print(f"  {d} complete ({len(have)} records, cached)", file=log, flush=True)
    return len(have)


def load_window(start, end):
    """All records with start <= day < end, in timestamp order."""
    recs = []
    d = start
    while d < end:
        p = day_path(d)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        recs.append(json.loads(line))
        d += dt.timedelta(days=1)
    recs.sort(key=lambda r: r["timeStamp"])
    return recs


def chain_verify(recs):
    """record[n].previousOutputValue must equal record[n-1].outputValue."""
    linked = broken = gap = 0
    breaks = []
    for a, b in zip(recs, recs[1:]):
        if b["timeStamp"] - a["timeStamp"] != 60:
            gap += 1
            continue
        if b["previousOutputValue"].upper() == a["outputValue"].upper():
            linked += 1
        else:
            broken += 1
            if len(breaks) < 10:
                breaks.append(b["timeStamp"])
    genesis_ok = bool(recs) and (recs[0]["timeStamp"] != GENESIS or
                                 set(recs[0]["previousOutputValue"]) == {"0"})
    return {"n_records": len(recs), "adjacent_linked": linked, "adjacent_broken": broken,
            "minute_gaps": gap, "link_rate": linked / max(1, linked + broken),
            "genesis_zero_prev": genesis_ok, "first_break_ts": breaks}


def assemble(recs, field):
    """Concatenate one hex field over the window, in pulse order, into raw bytes."""
    return bytes.fromhex("".join(r[field] for r in recs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2013-09-05")
    ap.add_argument("--end", default="2014-01-06")      # exclusive
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--verify", action="store_true", help="skip fetching; verify + assemble")
    a = ap.parse_args()
    os.makedirs(V1DIR, exist_ok=True)
    start = dt.date.fromisoformat(a.start)
    end = dt.date.fromisoformat(a.end)

    if not a.verify:
        d = start
        while d < end:
            fetch_day(d, a.workers)
            d += dt.timedelta(days=1)

    recs = load_window(start, end)
    v = chain_verify(recs)
    print(json.dumps(v, indent=2))
    meta = {"source": "NIST Randomness Beacon v1 (legacy /rest/record REST API)",
            "window_utc": [a.start, a.end], "fetched_utc": dt.datetime.now(
                dt.timezone.utc).isoformat(), "verify": v, "pads": {}}
    for field in ("outputValue", "seedValue"):
        blob = assemble(recs, field)
        name = f"pad_{field}_{a.start}_{a.end}.bin"
        with open(os.path.join(DATA, name), "wb") as f:
            f.write(blob)
        meta["pads"][field] = {"file": name, "bytes": len(blob),
                               "first_ts": recs[0]["timeStamp"] if recs else None,
                               "last_ts": recs[-1]["timeStamp"] if recs else None}
        print(f"  wrote {name}  {len(blob):,} bytes")
    with open(os.path.join(DATA, "fetch_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)



# ======================================================================================
# RANDOM.ORG Pregenerated File Archive
# ======================================================================================
# Measured 2026-08-19 (this is the finding that most directly contradicts the census):
#
#   https://archive.random.org/binary   lists ONE 1 MiB file of true random bytes PER DAY,
#   continuously since 2006-03-11 (7,395 daily .bin files as of today). A parallel /text
#   listing carries the same data as ASCII '0'/'1'.
#
#   Retrieval:
#     direct HTTP  https://archive.random.org/download?file=2013-12-01.bin  -> HTTP 403
#                  (subscription; only the newest day is free)
#     BitTorrent   https://archive.random.org/download?file=2013-09-bin.torrent -> HTTP 200,
#                  FREE, 245 monthly torrents back to 2006-03, tracker
#                  http://tracker.random.org:6969/announce, seeded by random.org itself.
#     MD5          https://archive.random.org/download?file=2013-09-bin.md5 -> HTTP 200, FREE
#
#   So random.org's pre-LP2 randomness is publicly retrievable AND independently verifiable
#   against random.org's own published MD5s. It does not belong in the census's "nothing can
#   touch it" bucket.
#
# Regenerate:
#     python fetch.py randomorg --months 2013-09,2013-10,2013-11,2013-12,2014-01
RDO_BASE = "https://archive.random.org/download?file="
RDODIR = os.path.join(DATA, "rdo")


def rdo_get(name, dest, tries=5):
    for k in range(tries):
        try:
            r = requests.get(RDO_BASE + name, headers=UA, timeout=60)
        except Exception:
            time.sleep(2 * (k + 1))
            continue
        if r.status_code != 200:
            return None
        with open(dest, "wb") as f:
            f.write(r.content)
        return len(r.content)
    return None


def rdo_fetch_months(months, minutes_per_month=45):
    """Download monthly .torrent + .md5 free, then pull the payload over BitTorrent."""
    import libtorrent as lt                                   # noqa: E402
    os.makedirs(RDODIR, exist_ok=True)
    ses = lt.session({"listen_interfaces": "0.0.0.0:6881", "enable_dht": False})
    handles = []
    for m in months:
        tor = os.path.join(RDODIR, f"{m}-bin.torrent")
        md5 = os.path.join(RDODIR, f"{m}-bin.md5")
        if not os.path.exists(tor) and rdo_get(f"{m}-bin.torrent", tor) is None:
            print(f"  {m}: no torrent (HTTP != 200)", flush=True)
            continue
        if not os.path.exists(md5):
            rdo_get(f"{m}-bin.md5", md5)
        ti = lt.torrent_info(tor)
        p = lt.add_torrent_params()
        p.ti = ti
        p.save_path = RDODIR
        handles.append((m, ses.add_torrent(p)))
        print(f"  {m}: queued {ti.name()} {ti.total_size():,} B", flush=True)
    deadline = time.time() + 60 * minutes_per_month * max(1, len(handles))
    while time.time() < deadline:
        done = 0
        for m, h in handles:
            s = h.status()
            if s.is_seeding or s.progress >= 1.0:
                done += 1
        if done == len(handles):
            break
        st = " ".join(f"{m}:{h.status().progress * 100:.0f}%" for m, h in handles)
        print(f"  [{time.strftime('%H:%M:%S')}] {st}", flush=True)
        time.sleep(30)
    return rdo_verify(months)


def rdo_verify(months):
    """Check every downloaded daily file against random.org's own published MD5."""
    import hashlib
    out = {}
    for m in months:
        md5f = os.path.join(RDODIR, f"{m}-bin.md5")
        want = {}
        if os.path.exists(md5f):
            for line in open(md5f, encoding="utf-8", errors="ignore"):
                parts = line.split()
                if len(parts) == 2:
                    want[parts[1].lstrip("*")] = parts[0].lower()
        d = os.path.join(RDODIR, f"random.org-pregenerated-{m}-bin")
        ok = bad = missing = 0
        for fn, h in sorted(want.items()):
            p = os.path.join(d, fn)
            if not os.path.exists(p):
                missing += 1
                continue
            if hashlib.md5(open(p, "rb").read()).hexdigest() == h:
                ok += 1
            else:
                bad += 1
        out[m] = {"md5_ok": ok, "md5_bad": bad, "missing": missing, "listed": len(want)}
        print(f"  {m}: md5 ok={ok} bad={bad} missing={missing} of {len(want)}", flush=True)
    return out


def rdo_assemble(months, out_name):
    """Concatenate the verified daily files in date order into one pad."""
    import hashlib
    parts = []
    for m in months:
        d = os.path.join(RDODIR, f"random.org-pregenerated-{m}-bin")
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".bin"):
                parts.append(os.path.join(d, fn))
    blob = b"".join(open(p, "rb").read() for p in parts)
    dest = os.path.join(DATA, out_name)
    with open(dest, "wb") as f:
        f.write(blob)
    print(f"  wrote {out_name} {len(blob):,} B from {len(parts)} daily files "
          f"sha256={hashlib.sha256(blob).hexdigest()[:16]}", flush=True)
    return dest, len(blob), [os.path.basename(p) for p in parts]


def main_randomorg(a):
    months = [m.strip() for m in a.months.split(",") if m.strip()]
    if not a.verify:
        rdo_fetch_months(months, a.minutes)
    v = rdo_verify(months)
    dest, n, files = rdo_assemble(months, a.out or ("pad_randomorg_%s_%s.bin" %
                                                    (months[0], months[-1])))
    meta = {"source": "RANDOM.ORG Pregenerated File Archive (binary, 1 MiB/day)",
            "months": months, "retrieval": "free monthly BitTorrent + free published MD5",
            "verify": v, "pad": {"file": os.path.basename(dest), "bytes": n,
                                 "daily_files": len(files),
                                 "first": files[0] if files else None,
                                 "last": files[-1] if files else None}}
    with open(os.path.join(DATA, "fetch_meta_randomorg.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


if __name__ == "__main__":
    top = argparse.ArgumentParser()
    sub = top.add_subparsers(dest="cmd")
    b = sub.add_parser("beacon")
    b.add_argument("--start", default="2013-09-05")
    b.add_argument("--end", default="2014-01-06")
    b.add_argument("--workers", type=int, default=96)
    b.add_argument("--verify", action="store_true")
    r = sub.add_parser("randomorg")
    r.add_argument("--months", default="2013-09,2013-10,2013-11,2013-12,2014-01")
    r.add_argument("--minutes", type=int, default=45, help="patience per month")
    r.add_argument("--out", default=None)
    r.add_argument("--verify", action="store_true")
    args, extra = top.parse_known_args()
    if args.cmd == "randomorg":
        main_randomorg(args)
    else:
        sys.argv = [sys.argv[0]] + [x for x in sys.argv[1:] if x != "beacon"]
        main()
