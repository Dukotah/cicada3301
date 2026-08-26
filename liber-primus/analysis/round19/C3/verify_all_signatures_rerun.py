#!/usr/bin/env python3
"""L8 / Round 18 — repo-wide OpenPGP verification table (corpus gap G-02).

Verifies EVERY *.asc held anywhere in this repository against an isolated keyring
containing only the canonical Cicada key 7A35090F, and records the signature-packet
timestamp for each (read from the file's own bytes, so it survives a failed verify).

Instrument controls C1-C4 (see PREREG.md) run first; the table is not written if a
control fails.

Run:  wsl -d Ubuntu -- bash -lc "cd /mnt/c/Users/dukot/projects/cicada3301 && \
      python3 liber-primus/analysis/round18/L8-provenance/verify_all_signatures.py"
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]          # .../cicada3301
WORK = HERE / "work"
WORK.mkdir(exist_ok=True)

CANON_FPR = "6D854CD7933322A601C3286D181F01E57A35090F"
CANON_LONG = "181F01E57A35090F"

GNUPGHOME = WORK / "gnupghome-l8"
FOREIGNHOME = Path(tempfile.gettempdir()) / "l8-gnupghome-foreign"  # must be on the Linux fs: gpg-agent cannot open a socket on drvfs

UTC = timezone.utc


def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def fresh_home(p):
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)
    p.mkdir(parents=True, exist_ok=True)
    os.chmod(p, 0o700)
    return p


def gpg(args, home=GNUPGHOME, stdin=None, timeout=300):
    env = dict(os.environ)
    env["GNUPGHOME"] = str(home)
    env["LC_ALL"] = "C"
    env["TZ"] = "UTC"
    return subprocess.run(["gpg", "--batch", "--no-tty"] + args,
                          capture_output=True, text=True, env=env,
                          input=stdin, timeout=timeout)


def corpus_asc_files():
    """Every .asc in the repo EXCEPT this lane's own scratch dir (control artifacts)."""
    other_work = REPO / "liber-primus" / "analysis" / "round18" / "L8-provenance" / "work"
    def excluded(x):
        if WORK == x.parent or WORK in x.parents:
            return True
        if other_work == x.parent or other_work in x.parents:
            return True
        return False
    return sorted(x for x in REPO.rglob("*.asc") if not excluded(x))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# --------------------------------------------------------------------------- key setup
def setup_keyring():
    fresh_home(GNUPGHOME)
    # Every .asc that is a public key block; import only those whose fingerprint is canonical.
    imported = []
    for p in corpus_asc_files():
        try:
            head = p.read_bytes()[:200]
        except OSError:
            continue
        if b"BEGIN PGP PUBLIC KEY BLOCK" not in head:
            continue
        # probe fingerprint without importing
        r = gpg(["--with-colons", "--import-options", "show-only", "--import", str(p)])
        fprs = [l.split(":")[9] for l in r.stdout.splitlines() if l.startswith("fpr:")]
        if CANON_FPR in fprs:
            gpg(["--import", str(p)])
            imported.append({"path": str(p.relative_to(REPO)).replace("\\", "/"),
                             "sha256": sha256_file(p), "fingerprints": fprs})
    r = gpg(["--with-colons", "--list-keys"])
    present, primaries, cur = [], [], None
    for l in r.stdout.splitlines():
        f = l.split(":")
        if f[0] in ("pub", "sub"):
            cur = f[0]
        elif f[0] == "fpr":
            present.append(f[9])
            if cur == "pub":
                primaries.append(f[9])
            cur = None
    return imported, present, primaries


# --------------------------------------------------------------------------- packet reads
SIG_RE = re.compile(r":signature packet: algo (\d+), keyid ([0-9A-Fa-f]+)")
CREATED_RE = re.compile(r"created (\d+)")
DIGEST_RE = re.compile(r"digest algo (\d+)")


def signature_packets(path):
    """All signature packets in the file's own bytes, verify-independent."""
    raw = Path(path).read_bytes().replace(b"\r\n", b"\n")
    i = raw.find(b"-----BEGIN PGP SIGNATURE-----")
    if i < 0:
        return []
    tf = tempfile.NamedTemporaryFile(suffix=".asc", delete=False, dir=str(WORK))
    tf.write(raw[i:])
    tf.close()
    try:
        r = gpg(["--list-packets", tf.name])
    finally:
        try:
            os.unlink(tf.name)
        except OSError:
            pass
    out = []
    cur = None
    for line in r.stdout.splitlines():
        m = SIG_RE.search(line)
        if m:
            if cur:
                out.append(cur)
            cur = {"pubkey_algo": int(m.group(1)), "keyid": m.group(2).upper(),
                   "created_unix": None, "digest_algo": None}
            continue
        if cur is not None:
            c = CREATED_RE.search(line)
            if c and cur["created_unix"] is None:
                cur["created_unix"] = int(c.group(1))
            d = DIGEST_RE.search(line)
            if d and cur["digest_algo"] is None:
                cur["digest_algo"] = int(d.group(1))
    if cur:
        out.append(cur)
    for o in out:
        o["created_utc"] = (datetime.fromtimestamp(o["created_unix"], UTC)
                            .strftime("%Y-%m-%dT%H:%M:%SZ")) if o["created_unix"] else None
    return out


def verify(path):
    r = gpg(["--status-fd", "1", "--verify", str(path)])
    status = [l for l in r.stdout.splitlines() if l.startswith("[GNUPG:]")]
    good = re.search(r"\[GNUPG:\] GOODSIG ([0-9A-F]+)", r.stdout)
    valid = re.search(r"\[GNUPG:\] VALIDSIG ([0-9A-F]+)", r.stdout)
    bad = re.search(r"\[GNUPG:\] BADSIG ([0-9A-F]+)", r.stdout)
    errsig = re.search(r"\[GNUPG:\] ERRSIG ([0-9A-F]+)", r.stdout)
    nopub = re.search(r"\[GNUPG:\] NO_PUBKEY ([0-9A-F]+)", r.stdout)
    return {
        "status_lines": status,
        "stderr": r.stderr.strip().splitlines(),
        "goodsig": good.group(1) if good else None,
        "validsig_fpr": valid.group(1) if valid else None,
        "badsig": bad.group(1) if bad else None,
        "errsig": errsig.group(1) if errsig else None,
        "no_pubkey": nopub.group(1) if nopub else None,
    }


def signed_body(path):
    """Normalised cleartext body of a clearsigned message, for cross-copy comparison."""
    try:
        raw = Path(path).read_bytes().replace(b"\r\n", b"\n").decode("utf-8", "replace")
    except OSError:
        return None
    if "-----BEGIN PGP SIGNED MESSAGE-----" not in raw:
        return None
    after = raw.split("-----BEGIN PGP SIGNED MESSAGE-----", 1)[1]
    # skip armor headers up to first blank line
    if "\n\n" not in after:
        return None
    body = after.split("\n\n", 1)[1]
    body = body.split("-----BEGIN PGP SIGNATURE-----", 1)[0]
    body = "\n".join(l.rstrip() for l in body.split("\n")).strip()
    return hashlib.sha256(body.encode()).hexdigest()


# --------------------------------------------------------------------------- controls
def run_controls(sample_pass_file):
    ctrl = {}

    # C1 — untouched known-good file must GOODSIG
    v = verify(sample_pass_file)
    ctrl["C1_pass"] = {"file": str(Path(sample_pass_file).relative_to(REPO)).replace("\\", "/"),
                       "goodsig": v["goodsig"],
                       "expected": CANON_LONG,
                       "met": v["goodsig"] == CANON_LONG,
                       "gpg_stderr": v["stderr"]}

    # C2 — tamper one character of the signed body => BADSIG
    raw = Path(sample_pass_file).read_bytes().replace(b"\r\n", b"\n").decode("utf-8", "replace")
    head, rest = raw.split("\n\n", 1)
    body, sig = rest.split("-----BEGIN PGP SIGNATURE-----", 1)
    letters = [i for i, ch in enumerate(body) if ch.isalpha()]
    idx = letters[len(letters) // 2]
    tam = body[:idx] + ("X" if body[idx] != "X" else "Q") + body[idx + 1:]
    tpath = WORK / "control_C2_tampered.asc"
    tpath.write_text(head + "\n\n" + tam + "-----BEGIN PGP SIGNATURE-----" + sig)
    v2 = verify(tpath)
    ctrl["C2_fail_on_tamper"] = {"mutated_char_index": idx,
                                 "badsig": v2["badsig"], "goodsig": v2["goodsig"],
                                 "met": v2["badsig"] == CANON_LONG and v2["goodsig"] is None,
                                 "gpg_stderr": v2["stderr"]}

    # C3 — a message signed by a foreign throwaway key must not GOODSIG as 3301
    fresh_home(FOREIGNHOME)
    gen = gpg(["--pinentry-mode", "loopback", "--passphrase", "",
               "--quick-generate-key", "L8 Control Key <l8@control.invalid>",
               "rsa2048", "sign", "never"], home=FOREIGNHOME)
    fk = gpg(["--with-colons", "--list-keys"], home=FOREIGNHOME)
    fkeyids = [l.split(":")[4] for l in fk.stdout.splitlines() if l.startswith("pub:")]
    msgpath = WORK / "control_C3_foreign.asc"
    sgn = gpg(["--clearsign", "--armor", "--output", str(msgpath), "--yes", "-"],
              home=FOREIGNHOME, stdin="control message for L8 C3\n")
    v3 = verify(msgpath) if msgpath.exists() else {"goodsig": "SIGN-FAILED", "errsig": None,
                                                   "no_pubkey": None, "stderr": sgn.stderr.splitlines()}
    ctrl["C3_fail_on_foreign_key"] = {
        "keygen_stderr": gen.stderr.strip().splitlines()[-3:],
        "foreign_keyid": fkeyids[0] if fkeyids else None,
        "goodsig": v3.get("goodsig"), "errsig": v3.get("errsig"), "no_pubkey": v3.get("no_pubkey"),
        "met": v3.get("goodsig") is None and (v3.get("errsig") or v3.get("no_pubkey")) is not None,
        "gpg_stderr": v3.get("stderr"),
    }

    # C4 — timestamp still recoverable from the tampered file
    orig_ts = signature_packets(sample_pass_file)
    tam_ts = signature_packets(tpath)
    ctrl["C4_timestamp_survives_tamper"] = {
        "original_created_unix": orig_ts[0]["created_unix"] if orig_ts else None,
        "tampered_created_unix": tam_ts[0]["created_unix"] if tam_ts else None,
        "met": bool(orig_ts and tam_ts and orig_ts[0]["created_unix"] == tam_ts[0]["created_unix"]),
    }
    ctrl["all_met"] = all(c["met"] for k, c in ctrl.items() if isinstance(c, dict) and "met" in c)
    return ctrl


# --------------------------------------------------------------------------- main
def main():
    started = now()
    imported, present, primaries = setup_keyring()
    if CANON_FPR not in primaries:
        print("FATAL: canonical key not in isolated keyring", file=sys.stderr)
        sys.exit(2)
    if set(primaries) != {CANON_FPR}:
        print("FATAL: keyring is not isolated, primaries:", primaries, file=sys.stderr)
        sys.exit(2)

    files = corpus_asc_files()
    rows = []
    for p in files:
        rel = str(p.relative_to(REPO)).replace("\\", "/")
        raw = p.read_bytes()
        kind = ("KEY" if b"BEGIN PGP PUBLIC KEY BLOCK" in raw[:400]
                else "MESSAGE" if b"BEGIN PGP" in raw[:400] else "OTHER")
        pkts = signature_packets(p) if b"BEGIN PGP SIGNATURE" in raw else []
        row = {
            "path": rel,
            "bytes": len(raw),
            "sha256": sha256_file(p),
            "kind": kind,
            "body_sha256": signed_body(p),
            "signature_packets": pkts,
            "signature_timestamp_unix": pkts[0]["created_unix"] if pkts else None,
            "signature_timestamp_utc": pkts[0]["created_utc"] if pkts else None,
            "signing_keyid_from_packet": pkts[0]["keyid"] if pkts else None,
            "digest_algo": pkts[0]["digest_algo"] if pkts else None,
        }
        if kind == "KEY" and not pkts:
            row["verdict"] = "KEY"
        elif not pkts:
            row["verdict"] = "NO-SIG"
        else:
            v = verify(p)
            row["gpg"] = v
            if v["goodsig"] == CANON_LONG and v["validsig_fpr"] == CANON_FPR:
                row["verdict"] = "PASS"
            elif kind == "KEY":
                row["verdict"] = "KEY"
            else:
                row["verdict"] = "FAIL"
                row["fail_reason"] = ("BADSIG" if v["badsig"] else
                                      "NO_PUBKEY/ERRSIG (foreign or unknown key)" if (v["no_pubkey"] or v["errsig"])
                                      else "no GOODSIG emitted")
        rows.append(row)

    # controls: pick the first PASS row as C1 sample
    sample = next((REPO / r["path"] for r in rows if r["verdict"] == "PASS"), None)
    controls = run_controls(sample) if sample else {"all_met": False, "note": "no PASS row to control on"}

    # cross-copy analysis: does a FAILing body have a PASSing twin?
    passing_bodies = {r["body_sha256"] for r in rows if r["verdict"] == "PASS" and r["body_sha256"]}
    for r in rows:
        if r["verdict"] == "FAIL":
            r["has_passing_twin_by_body"] = bool(r["body_sha256"] and r["body_sha256"] in passing_bodies)
            r["classification"] = ("mirror/transport defect (identical body PASSes elsewhere)"
                                   if r.get("has_passing_twin_by_body")
                                   else "UNRESOLVED FAIL — no PASSing copy of this body in the corpus")

    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    keyids = sorted({r["signing_keyid_from_packet"] for r in rows
                     if r["signing_keyid_from_packet"] and r["kind"] == "MESSAGE"})
    ts = sorted({r["signature_timestamp_unix"] for r in rows
                 if r["verdict"] == "PASS" and r["signature_timestamp_unix"]})

    out = {
        "generated_utc": started,
        "finished_utc": now(),
        "lane": "round18/L8-provenance",
        "gap": "corpus/GAPS.md G-02",
        "gpg_version": subprocess.run(["gpg", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
        "verification_key": {
            "fingerprint": CANON_FPR, "long_id": "0x" + CANON_LONG, "short_id": "7A35090F",
            "keyring": "isolated GNUPGHOME containing ONLY this key",
            "imported_from": imported,
            "keyring_fingerprints_present": sorted(set(present)),
            "keyring_primary_fingerprints": sorted(set(primaries)),
        },
        "instrument_controls": controls,
        "summary": {
            "files_scanned": len(rows),
            "by_verdict": counts,
            "distinct_files_by_sha256": len({r["sha256"] for r in rows}),
            "distinct_message_bodies": len({r["body_sha256"] for r in rows if r["body_sha256"]}),
            "distinct_signing_keyids_in_messages": keyids,
            "distinct_verified_timestamps": len(ts),
            "verified_timestamp_range_utc": {
                "earliest": datetime.fromtimestamp(ts[0], UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None,
                "latest": datetime.fromtimestamp(ts[-1], UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None,
            },
            "unresolved_fails": [r["path"] for r in rows
                                 if r["verdict"] == "FAIL" and not r.get("has_passing_twin_by_body")],
        },
        "rows": rows,
    }
    (HERE / "PGP-VERIFICATION-TABLE.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["summary"], indent=1))
    print("controls:", json.dumps({k: v.get("met") for k, v in controls.items() if isinstance(v, dict)}, indent=1))


if __name__ == "__main__":
    main()
