#!/usr/bin/env python3
"""Lane A: verify every claimed Cicada PGP message against key 7A35090F.

Emits SIGNATURES.json. Never invents a value: everything comes from gpg's
--status-fd machine-readable output or from hashlib.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GNUPGHOME = ROOT / "pgp" / ".gnupg-lane-a"


def msys(path):
    r"""gpg here is an MSYS binary: it needs /c/... not C:\..."""
    s = str(path).replace("\\", "/")
    if len(s) > 1 and s[1] == ":":
        s = "/" + s[0].lower() + s[2:]
    return s
MSGDIR = ROOT / "pgp" / "messages"
OUT = ROOT / "SIGNATURES.json"
SOURCES = ROOT / "_sources.json"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gpg_verify(path):
    env = dict(os.environ)
    env["GNUPGHOME"] = msys(GNUPGHOME)
    try:
        r = subprocess.run(
            ["gpg", "--batch", "--status-fd", "1", "--verify", msys(path)],
            capture_output=True, text=True, env=env, timeout=180,
        )
    except subprocess.TimeoutExpired:
        return {"signature_status": "TIMEOUT", "raw": ""}
    status = r.stdout + "\n" + r.stderr
    out = {"raw_status": [l for l in r.stdout.splitlines() if l.startswith("[GNUPG:]")]}

    m = re.search(r"\[GNUPG:\] VALIDSIG ([0-9A-F]+) (\S+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) ([0-9A-F]+)", r.stdout)
    good = re.search(r"\[GNUPG:\] GOODSIG ([0-9A-F]+)", r.stdout)
    bad = re.search(r"\[GNUPG:\] BADSIG ([0-9A-F]+)", r.stdout)
    errsig = re.search(r"\[GNUPG:\] ERRSIG (\S+) (\S+) (\S+) (\S+) (\d+) (\S+)", r.stdout)
    nodata = "[GNUPG:] NODATA" in r.stdout

    ts = None
    keyid = None
    fpr = None
    hashalg = None
    pubkeyalg = None

    if m:
        fpr = m.group(1)
        keyid = fpr[-16:]
        try:
            ts = datetime.fromtimestamp(int(m.group(3)), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            ts = None
        pubkeyalg = m.group(7)
        hashalg = m.group(8)

    if good and m:
        st = "VALID"
    elif good:
        st = "VALID_NO_VALIDSIG"
    elif bad:
        st = "INVALID"
        keyid = bad.group(1)
    elif errsig:
        keyid = errsig.group(1)
        rc = errsig.group(6)
        st = "KEY_UNAVAILABLE" if rc == "9" else "ERROR_RC_" + rc
        try:
            ts = datetime.fromtimestamp(int(errsig.group(5)), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass
    elif nodata or "no valid OpenPGP data" in status:
        st = "NO_SIGNATURE"
    else:
        st = "NO_SIGNATURE"

    out.update({
        "signature_status": st,
        "signing_key_id": keyid,
        "signing_key_fingerprint": fpr,
        "signature_timestamp_utc": ts,
        "hash_algorithm": hashalg,
        "pubkey_algorithm": pubkeyalg,
        "gpg_stderr": r.stderr.strip().splitlines()[:6],
    })
    return out


def main():
    sources = {}
    if SOURCES.exists():
        sources = json.loads(SOURCES.read_text(encoding="utf-8"))

    rows = []
    for p in sorted(MSGDIR.glob("*.asc")):
        size = p.stat().st_size
        head = p.read_bytes()[:64]
        row = {
            "file": str(p.relative_to(ROOT)).replace("\\", "/"),
            "bytes": size,
            "sha256": sha256_file(p),
        }
        body = p.read_bytes()
        if b"BEGIN PGP" not in body[:4096] and (b"<!DOCTYPE html" in body[:200] or b"Too Many Requests" in body[:200]):
            row.update({
                "signature_status": "FETCH_ERROR_PAGE",
                "signing_key_id": None,
                "signature_timestamp_utc": None,
                "note": p.read_text(errors="replace")[:200],
            })
        elif b"BEGIN PGP" not in body[:4096]:
            row.update({
                "signature_status": "NO_SIGNATURE",
                "signing_key_id": None,
                "signature_timestamp_utc": None,
                "note": p.read_text(errors="replace")[:200],
            })
        else:
            row.update(gpg_verify(p))
        meta = sources.get(p.name, {})
        row["source_url"] = meta.get("source_url")
        row["retrieved_utc"] = meta.get("retrieved_utc")
        row["upstream_note"] = meta.get("note")
        rows.append(row)
        print(f"{row['signature_status']:20s} {p.name}")

    counts = {}
    for r in rows:
        counts[r["signature_status"]] = counts.get(r["signature_status"], 0) + 1

    OUT.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verification_key": {
            "fingerprint": "6D854CD7933322A601C3286D181F01E57A35090F",
            "long_id": "0x181F01E57A35090F",
            "short_id": "7A35090F",
            "uid": "Cicada 3301 (845145127)",
            "created": "2012-01-05",
            "algo": "rsa4096",
        },
        "gpg_version": subprocess.run(["gpg", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
        "summary": counts,
        "messages": rows,
    }, indent=2), encoding="utf-8")
    print("\n== summary ==")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
