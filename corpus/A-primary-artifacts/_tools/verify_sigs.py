#!/usr/bin/env python3
"""Lane A: verify every claimed Cicada PGP message held in this corpus.

Emits SIGNATURES.json (full record) and SIGNATURE-TIMELINE.json (chronological,
signature-packet timestamps only).

Rules this script obeys:
  * Nothing is invented. Every field comes from gpg's --status-fd machine output,
    gpg --list-packets, hashlib, MANIFEST.json, or _sources.json.
  * The signature-packet timestamp is read from the file's own bytes
    (gpg --list-packets on the isolated signature block) even when the signature
    does NOT verify, so a mirror-damaged file still yields its real timestamp.
  * Files are never modified. Repaired copies live under pgp/repaired/ and are
    flagged is_derived=true.

gpg here is an MSYS binary: it needs /c/... paths, not C:\\...
"""
import collections
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GNUPGHOME = ROOT / "pgp" / ".gnupg-lane-a"
OUT = ROOT / "SIGNATURES.json"
TIMELINE = ROOT / "SIGNATURE-TIMELINE.json"
SOURCES = ROOT / "_sources.json"
MANIFEST = ROOT / "MANIFEST.json"

# Directories scanned for signed messages. Key files are excluded on purpose.
SCAN = [
    ("pgp/messages", "*.asc"),
    ("pgp/repaired", "*.asc"),
    ("ibotpeaches/messages", "**/*.asc"),
    ("cijhho123", "**/message.txt.asc"),
    ("krisyotam/puzzles", "**/message.txt.asc"),
    ("krisyotam/pgp/messages", "*.asc"),
    ("krisyotam/liber-primus", "**/message.txt.asc"),
    ("Hadyn_cicada", "**/*.asc"),
    ("scream314_cicada3301", "**/*.asc"),
]


def msys(path):
    s = str(path).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = "/" + s[0].lower() + s[2:]
    return s


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gpg_env():
    env = dict(os.environ)
    env["GNUPGHOME"] = msys(GNUPGHOME)
    return env


def packet_timestamp(path):
    """Signature-packet creation time straight from the file's bytes.

    Works on BADSIG / armor-damaged files, which --verify will not report a
    VALIDSIG for. Returns (iso_utc, unix, keyid, digest_algo, pubkey_algo) or Nones.
    """
    try:
        raw = Path(path).read_bytes().replace(b"\r\n", b"\n")
        i = raw.find(b"-----BEGIN PGP SIGNATURE-----")
        if i < 0:
            return (None,) * 5
        with tempfile.NamedTemporaryFile(suffix=".asc", delete=False,
                                         dir=str(ROOT / "_logs")) as tf:
            tf.write(raw[i:])
            tmp = tf.name
        try:
            r = subprocess.run(["gpg", "--list-packets", msys(tmp)],
                               capture_output=True, text=True,
                               env=gpg_env(), timeout=120)
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        m = re.search(r"created (\d+), md5len \d+, sigclass", r.stdout)
        k = re.search(r":signature packet: algo (\d+), keyid ([0-9A-F]+)", r.stdout)
        d = re.search(r"digest algo (\d+)", r.stdout)
        unix = int(m.group(1)) if m else None
        iso = (datetime.fromtimestamp(unix, tz=timezone.utc)
               .strftime("%Y-%m-%dT%H:%M:%SZ")) if unix else None
        return (iso, unix,
                k.group(2) if k else None,
                d.group(1) if d else None,
                k.group(1) if k else None)
    except Exception:
        return (None,) * 5


def gpg_verify(path):
    try:
        r = subprocess.run(
            ["gpg", "--batch", "--status-fd", "1", "--verify", msys(path)],
            capture_output=True, text=True, env=gpg_env(), timeout=300,
        )
    except subprocess.TimeoutExpired:
        return {"signature_status": "TIMEOUT", "raw_status": []}

    out = {"raw_status": [l for l in r.stdout.splitlines() if l.startswith("[GNUPG:]")]}
    m = re.search(r"\[GNUPG:\] VALIDSIG ([0-9A-F]+) (\S+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) ([0-9A-F]+)", r.stdout)
    sigid = re.search(r"\[GNUPG:\] SIG_ID (\S+) (\S+) (\d+)", r.stdout)
    good = re.search(r"\[GNUPG:\] GOODSIG ([0-9A-F]+)", r.stdout)
    bad = re.search(r"\[GNUPG:\] BADSIG ([0-9A-F]+)", r.stdout)
    errsig = re.search(r"\[GNUPG:\] ERRSIG (\S+) (\S+) (\S+) (\S+) (\d+) (\S+)", r.stdout)
    nodata = "[GNUPG:] NODATA" in r.stdout

    ts = keyid = fpr = hashalg = pubkeyalg = None
    ts_src = None
    if m:
        fpr = m.group(1)
        keyid = fpr[-16:]
        ts = datetime.fromtimestamp(int(m.group(3)), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ts_src = "gpg VALIDSIG"
        pubkeyalg, hashalg = m.group(7), m.group(8)

    if good and m:
        st = "VALID"
    elif good:
        st = "VALID_NO_VALIDSIG"
    elif bad:
        st, keyid = "INVALID", bad.group(1)
    elif errsig:
        keyid = errsig.group(1)
        rc = errsig.group(6)
        st = "KEY_UNAVAILABLE" if rc == "9" else "ERROR_RC_" + rc
    elif nodata or "no valid OpenPGP data" in (r.stdout + r.stderr):
        st = "NO_SIGNATURE"
    else:
        st = "NO_SIGNATURE"

    # Packet-level timestamp: authoritative, and works when --verify does not
    # emit VALIDSIG (BADSIG, damaged armor, unavailable key).
    p_iso, p_unix, p_key, p_digest, p_pub = packet_timestamp(path)
    if ts is None and p_iso:
        ts, ts_src = p_iso, "signature packet (gpg --list-packets)"
        keyid = keyid or p_key
        hashalg = hashalg or p_digest
        pubkeyalg = pubkeyalg or p_pub
    if ts is None and st == "NO_SIGNATURE":
        ts_src = "n/a - file contains no PGP signature packet"
    # packet_timestamp() only parses armored clearsign / detached blocks. For a
    # -----BEGIN PGP MESSAGE----- container gpg still reports VALIDSIG, so derive
    # the unix value from that rather than leaving it null.
    if p_unix is None and ts:
        p_unix = int(datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                     .replace(tzinfo=timezone.utc).timestamp())

    out.update({
        "signature_status": st,
        "signing_key_id": keyid,
        "signing_key_fingerprint": fpr,
        "signature_timestamp_utc": ts,
        "signature_timestamp_unix": p_unix if p_unix is not None else None,
        "signature_timestamp_source": ts_src,
        "sig_id": sigid.group(1) if sigid else None,
        "hash_algorithm": hashalg,
        "pubkey_algorithm": pubkeyalg,
        "gpg_stderr": r.stderr.strip().splitlines()[:8],
    })
    return out


def main():
    sources = json.loads(SOURCES.read_text(encoding="utf-8")) if SOURCES.exists() else {}
    manifest = {}
    if MANIFEST.exists():
        for it in json.loads(MANIFEST.read_text(encoding="utf-8")).get("items", []):
            manifest[it["path"]] = it
    # Side manifests written by the per-repo bulk fetchers. Without these, files
    # pulled by those fetchers end up with a null source_url, which reads as
    # "provenance unknown" when it is in fact recorded, just elsewhere.
    for side in sorted((ROOT / "_logs").glob("manifest_*.json")):
        try:
            doc = json.loads(side.read_text(encoding="utf-8"))
        except Exception:
            continue
        rowsx = doc.get("items", doc) if isinstance(doc, dict) else doc
        for it in rowsx if isinstance(rowsx, list) else []:
            if isinstance(it, dict) and it.get("path") and it["path"] not in manifest:
                manifest[it["path"]] = it

    seen = set()
    paths = []
    for sub, pat in SCAN:
        base = ROOT / sub
        if not base.exists():
            continue
        for p in sorted(base.glob(pat)):
            rp = str(p.relative_to(ROOT)).replace("\\", "/")
            if rp in seen:
                continue
            seen.add(rp)
            paths.append((rp, p))

    rows = []
    for rp, p in paths:
        body = p.read_bytes()
        row = {"file": rp, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
        if b"BEGIN PGP" not in body[:8192]:
            head = body[:200]
            st = "FETCH_ERROR_PAGE" if (b"<!DOCTYPE html" in head or b"Too Many Requests" in head) else "NO_SIGNATURE"
            row.update({
                "signature_status": st,
                "signing_key_id": None,
                "signing_key_fingerprint": None,
                "signature_timestamp_utc": None,
                "signature_timestamp_unix": None,
                "signature_timestamp_source": "n/a - file contains no PGP signature packet",
                "sig_id": None,
                "hash_algorithm": None,
                "pubkey_algorithm": None,
                "raw_status": [],
                "gpg_stderr": [],
                "note": body[:400].decode("utf-8", "replace"),
            })
        else:
            row.update(gpg_verify(p))

        meta = manifest.get(rp) or sources.get(p.name) or {}
        row["source_url"] = meta.get("source_url")
        row["retrieved_utc"] = meta.get("retrieved_utc")
        row["upstream_note"] = meta.get("notes") or meta.get("note")
        row["is_derived"] = rp.startswith("pgp/repaired/")
        if row["is_derived"] and not row["source_url"]:
            # A derived file has no retrieval URL by definition. Say so explicitly
            # rather than leaving a null that reads as missing provenance.
            row["source_url"] = "derived (not retrieved) - see pgp/repaired/README.md"
            row["retrieved_utc"] = "n/a - derived from a retrieved file, not fetched"
            row["upstream_note"] = (
                "byte-level repair of pgp/messages/ky_2013-01-opening-book-code.asc: the "
                "RFC 4880 blank line between the armor headers and the signed text was "
                "re-inserted. No other byte changed. See CONFLICTS-A.md C-01.")
        rows.append(row)
        print(f"{row['signature_status']:18s} {rp}")

    # duplicate detection by sha256 (first occurrence wins)
    first = {}
    for r in rows:
        h = r["sha256"]
        if h in first:
            r["duplicate_of"] = first[h]
        else:
            first[h] = r["file"]
            r["duplicate_of"] = None

    counts = {}
    for r in rows:
        counts[r["signature_status"]] = counts.get(r["signature_status"], 0) + 1

    keys = sorted({r["signing_key_id"] for r in rows if r["signing_key_id"]})
    fprs = sorted({r["signing_key_fingerprint"] for r in rows if r["signing_key_fingerprint"]})
    stamped = [r for r in rows if r["signature_timestamp_utc"]]
    stamps = sorted(r["signature_timestamp_utc"] for r in stamped)
    distinct_sigids = sorted({r["sig_id"] for r in rows if r.get("sig_id")})
    distinct_stamps = sorted({r["signature_timestamp_utc"] for r in stamped})
    span = None
    if stamps:
        a = datetime.strptime(stamps[0], "%Y-%m-%dT%H:%M:%SZ")
        b = datetime.strptime(stamps[-1], "%Y-%m-%dT%H:%M:%SZ")
        span = (b - a).days

    gpgv = subprocess.run(["gpg", "--version"], capture_output=True, text=True).stdout.splitlines()[0]

    doc = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verification_key": {
            "fingerprint": "6D854CD7933322A601C3286D181F01E57A35090F",
            "long_id": "0x181F01E57A35090F",
            "short_id": "7A35090F",
            "uid": "Cicada 3301 (845145127)",
            "created": "2012-01-05",
            "algo": "rsa4096",
        },
        "gpg_version": gpgv,
        "summary": {
            "files_verified": len(rows),
            "distinct_files_by_sha256": len(first),
            "by_status": dict(sorted(counts.items())),
            "distinct_signing_key_ids": keys,
            "distinct_signing_key_fingerprints": fprs,
            "distinct_sig_ids": len(distinct_sigids),
            "distinct_signature_timestamps": len(distinct_stamps),
            "timestamp_range_utc": {
                "earliest": stamps[0] if stamps else None,
                "latest": stamps[-1] if stamps else None,
                "span_days": span,
                "files_with_timestamp": len(stamped),
                "files_without_timestamp": len(rows) - len(stamped),
            },
            "notes": [
                "Every message that carries a signature packet is signed by exactly the "
                "keys listed in distinct_signing_key_ids. No second key appears.",
                "Rows with duplicate_of set are byte-identical copies held under a second "
                "path (mirror-of-a-mirror); they are verified anyway rather than assumed.",
                "is_derived=true marks a repaired copy under pgp/repaired/. It is NOT a "
                "retrieved artifact and must not be cited as one.",
                "signature_timestamp_utc is read from the signature packet itself, so it is "
                "present even for a file whose signature fails to verify.",
            ],
        },
        "messages": rows,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    tl = [{
        "signature_timestamp_utc": r["signature_timestamp_utc"],
        "signature_timestamp_unix": r["signature_timestamp_unix"],
        "sig_id": r.get("sig_id"),
        "signing_key_id": r["signing_key_id"],
        "signature_status": r["signature_status"],
        "file": r["file"],
        "sha256": r["sha256"],
        "duplicate_of": r["duplicate_of"],
        "is_derived": r["is_derived"],
        "source_url": r["source_url"],
        "retrieved_utc": r["retrieved_utc"],
    } for r in rows if r["signature_timestamp_utc"]]
    tl.sort(key=lambda x: (x["signature_timestamp_unix"] or 0, x["file"]))

    # per-distinct-signature view: one entry per SIG_ID, earliest file that carries it
    # gpg emits no SIG_ID for a signature that fails to verify. Fold such a row
    # into the bucket of the signature that has the same key id and the same
    # packet timestamp, so a mirror-damaged copy is not counted as an extra
    # distinct signature. Fallback key is the file hash.
    ts_key_to_sigid = {}
    for e in tl:
        if e["sig_id"]:
            ts_key_to_sigid.setdefault((e["signature_timestamp_unix"], e["signing_key_id"]), e["sig_id"])
    byid = {}
    for e in tl:
        k = e["sig_id"] or ts_key_to_sigid.get((e["signature_timestamp_unix"], e["signing_key_id"])) or e["sha256"]
        if k in byid and not e["sig_id"]:
            byid[k]["carried_by_files"].append(e["file"])
            continue
        byid.setdefault(k, {"sig_id": e["sig_id"] or k,
                            "signature_timestamp_utc": e["signature_timestamp_utc"],
                            "signature_timestamp_unix": e["signature_timestamp_unix"],
                            "signing_key_id": e["signing_key_id"],
                            "carried_by_files": []})
        byid[k]["carried_by_files"].append(e["file"])
    uniq = sorted(byid.values(), key=lambda x: x["signature_timestamp_unix"] or 0)

    gaps = []
    for i in range(1, len(uniq)):
        gaps.append({
            "from_utc": uniq[i - 1]["signature_timestamp_utc"],
            "to_utc": uniq[i]["signature_timestamp_utc"],
            "delta_seconds": (uniq[i]["signature_timestamp_unix"] or 0) - (uniq[i - 1]["signature_timestamp_unix"] or 0),
        })

    TIMELINE.write_text(json.dumps({
        "generated_utc": doc["generated_utc"],
        "what_this_is": (
            "Every PGP signature-packet creation timestamp held in Lane A, sorted "
            "chronologically. Timestamps come from the signature packets themselves "
            "(gpg --list-packets), not from any narrative. Timestamps are UTC as stored "
            "in the packet; the signer's local timezone is not recorded by OpenPGP."
        ),
        "counts": {
            "timestamp_rows": len(tl),
            "distinct_signatures": len(uniq),
            "earliest_utc": tl[0]["signature_timestamp_utc"] if tl else None,
            "latest_utc": tl[-1]["signature_timestamp_utc"] if tl else None,
            "span_days": span,
        },
        "dedupe_rule": (
            "One entry per OpenPGP SIG_ID. gpg emits no SIG_ID for a signature that "
            "fails to verify, so such a row is folded into the bucket with the same "
            "(packet timestamp, key id); if no such bucket exists it stands alone under "
            "its file hash."
        ),
        "distributions": {
            "by_year_utc": dict(sorted(collections.Counter(
                x["signature_timestamp_utc"][:4] for x in uniq).items())),
            "by_utc_hour": {f"{h:02d}": collections.Counter(
                int(x["signature_timestamp_utc"][11:13]) for x in uniq).get(h, 0)
                for h in range(24)},
            "by_utc_weekday": dict(collections.Counter(
                datetime.strptime(x["signature_timestamp_utc"], "%Y-%m-%dT%H:%M:%SZ").strftime("%a")
                for x in uniq)),
        },
        "distinct_signatures": uniq,
        "inter_signature_gaps": gaps,
        "all_rows": tl,
    }, indent=2), encoding="utf-8")

    print("\n== summary ==")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    print(f"  distinct sig ids: {len(distinct_sigids)}")
    print(f"  range: {stamps[0] if stamps else None} .. {stamps[-1] if stamps else None} ({span} d)")
    print(f"wrote {OUT}\nwrote {TIMELINE}")


if __name__ == "__main__":
    main()
