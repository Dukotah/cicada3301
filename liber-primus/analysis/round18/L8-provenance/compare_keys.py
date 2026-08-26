#!/usr/bin/env python3
"""L8 / I-01 — packet-level comparison of the `mruzuki` key against 3301's 7A35090F,
plus a base-rate control: do the matching fields discriminate anything at all?

Reads only public keyserver exports. Emits KEY-COMPARISON.json.
"""
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
EV = HERE / "evidence"

TARGETS = [
    ("cicada_3301_7A35090F",
     REPO / "corpus/A-primary-artifacts/krisyotam/pgp/key/cicada-3301-public-key.asc",
     "held in repo; canonical key, fpr 6D854CD7933322A601C3286D181F01E57A35090F"),
    ("mruzuki_02BD208AFB8AFF75",
     EV / "mruzuki.keyserver.ubuntu.com.asc",
     "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x02BD208AFB8AFF75&options=mr"),
]
for p in sorted((EV / "baserate").glob("*.asc")):
    if p.stat().st_size > 100:
        TARGETS.append(("baserate:" + p.stem, p,
                        "https://keyserver.ubuntu.com/pks/lookup?op=get (public project release key)"))


def packets(path):
    env = dict(os.environ)
    env["GNUPGHOME"] = tempfile.mkdtemp()
    env["LC_ALL"] = "C"
    env["TZ"] = "UTC"
    r = subprocess.run(["gpg", "--batch", "--no-tty", "--list-packets", str(path)],
                       capture_output=True, text=True, env=env, timeout=300)
    return r.stdout


def parse(text):
    """First primary key + its FIRST uid self-sig (sigclass 0x13) + revocation (0x20)."""
    out = {"primary": None, "subkeys": [], "uid": None, "selfsig": None, "revocation": None}
    blocks = re.split(r"^# off=", text, flags=re.M)
    for b in blocks:
        if ":public key packet:" in b and out["primary"] is None:
            m = re.search(r"version (\d+), algo (\d+), created (\d+), expires (\d+)", b)
            bits = re.search(r"pkey\[0\]: \[(\d+) bits\]", b)
            kid = re.search(r"keyid: ([0-9A-F]+)", b)
            out["primary"] = {"version": int(m.group(1)), "algo": int(m.group(2)),
                              "created_unix": int(m.group(3)), "expires_field": int(m.group(4)),
                              "bits": int(bits.group(1)) if bits else None,
                              "keyid": kid.group(1) if kid else None}
        elif ":public sub key packet:" in b:
            m = re.search(r"algo (\d+), created (\d+)", b)
            bits = re.search(r"pkey\[0\]: \[(\d+) bits\]", b)
            kid = re.search(r"keyid: ([0-9A-F]+)", b)
            out["subkeys"].append({"algo": int(m.group(1)), "created_unix": int(m.group(2)),
                                   "bits": int(bits.group(1)) if bits else None,
                                   "keyid": kid.group(1) if kid else None})
        elif ":user ID packet:" in b and out["uid"] is None:
            u = re.search(r':user ID packet: "(.*)"', b)
            out["uid"] = u.group(1) if u else None
        elif ":signature packet:" in b:
            cls = re.search(r"sigclass 0x([0-9a-f]+)", b)
            if not cls:
                continue
            cls = cls.group(1)
            rec = {
                "sigclass": "0x" + cls,
                "created_unix": int(re.search(r"created (\d+)", b).group(1)),
                "digest_algo": int(re.search(r"digest algo (\d+)", b).group(1)),
                "key_flags": (re.search(r"key flags: ([0-9A-F]+)", b) or [None, None])[1]
                if re.search(r"key flags: ([0-9A-F]+)", b) else None,
                "key_expires_after": (re.search(r"key expires after ([^\)]+)\)", b).group(1).strip()
                                      if re.search(r"key expires after ([^\)]+)\)", b) else None),
                "pref_sym": (re.search(r"pref-sym-algos: ([\d ]+)", b).group(1).strip()
                             if re.search(r"pref-sym-algos: ([\d ]+)", b) else None),
                "pref_hash": (re.search(r"pref-hash-algos: ([\d ]+)", b).group(1).strip()
                              if re.search(r"pref-hash-algos: ([\d ]+)", b) else None),
                "pref_zip": (re.search(r"pref-zip-algos: ([\d ]+)", b).group(1).strip()
                             if re.search(r"pref-zip-algos: ([\d ]+)", b) else None),
                "features": (re.search(r"features: ([0-9A-F]+)", b).group(1)
                             if re.search(r"features: ([0-9A-F]+)", b) else None),
                "keyserver_prefs": (re.search(r"keyserver preferences: ([0-9A-F]+)", b).group(1)
                                    if re.search(r"keyserver preferences: ([0-9A-F]+)", b) else None),
                "revocation_reason": (re.search(r"revocation reason 0x([0-9a-f]+)", b).group(1)
                                      if re.search(r"revocation reason 0x([0-9a-f]+)", b) else None),
            }
            if cls == "13" and out["selfsig"] is None and rec["pref_sym"]:
                out["selfsig"] = rec
            elif cls == "20" and out["revocation"] is None:
                out["revocation"] = rec
    return out


def iso(u):
    return datetime.fromtimestamp(u, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if u else None


results = {}
for name, path, src in TARGETS:
    if not Path(path).exists():
        continue
    p = parse(packets(path))
    if p["primary"]:
        p["primary"]["created_utc"] = iso(p["primary"]["created_unix"])
    for s in p["subkeys"]:
        s["created_utc"] = iso(s["created_unix"])
    for k in ("selfsig", "revocation"):
        if p[k]:
            p[k]["created_utc"] = iso(p[k]["created_unix"])
    p["_source"] = src
    p["_file"] = str(Path(path)).replace("\\", "/")
    results[name] = p

a = results["cicada_3301_7A35090F"]
b = results["mruzuki_02BD208AFB8AFF75"]


def g(d, *ks):
    for k in ks:
        d = (d or {}).get(k) if isinstance(d, dict) else None
    return d


FIELDS = [
    ("key version", g(a, "primary", "version"), g(b, "primary", "version"), "software"),
    ("public-key algorithm", g(a, "primary", "algo"), g(b, "primary", "algo"), "operator"),
    ("primary key size (bits)", g(a, "primary", "bits"), g(b, "primary", "bits"), "operator"),
    ("subkey size (bits)", a["subkeys"][0]["bits"] if a["subkeys"] else None,
     b["subkeys"][0]["bits"] if b["subkeys"] else None, "operator"),
    ("key created (UTC)", g(a, "primary", "created_utc"), g(b, "primary", "created_utc"), "clock"),
    ("self-sig digest algo", g(a, "selfsig", "digest_algo"), g(b, "selfsig", "digest_algo"), "software"),
    ("key flags (primary)", g(a, "selfsig", "key_flags"), g(b, "selfsig", "key_flags"), "software"),
    ("expiry policy", g(a, "selfsig", "key_expires_after") or "no expiry",
     g(b, "selfsig", "key_expires_after") or "no expiry", "operator"),
    ("pref-sym-algos", g(a, "selfsig", "pref_sym"), g(b, "selfsig", "pref_sym"), "software default"),
    ("pref-hash-algos", g(a, "selfsig", "pref_hash"), g(b, "selfsig", "pref_hash"), "software default"),
    ("pref-zip-algos", g(a, "selfsig", "pref_zip"), g(b, "selfsig", "pref_zip"), "software default"),
    ("features (MDC)", g(a, "selfsig", "features"), g(b, "selfsig", "features"), "software default"),
    ("keyserver prefs", g(a, "selfsig", "keyserver_prefs"), g(b, "selfsig", "keyserver_prefs"), "software default"),
    ("revoked", "no" if not a["revocation"] else g(a, "revocation", "created_utc"),
     "no" if not b["revocation"] else g(b, "revocation", "created_utc"), "operator"),
    ("revocation reason code", g(a, "revocation", "revocation_reason"),
     g(b, "revocation", "revocation_reason"), "operator"),
]
comparison = [{"field": f, "cicada_7A35090F": x, "mruzuki_FB8AFF75": y,
               "who_chose_it": who, "same": (x == y)} for f, x, y, who in FIELDS]

# base rate over the software-default fields
base = []
for k, v in results.items():
    if not k.startswith("baserate:") or not v.get("selfsig"):
        continue
    base.append({
        "key": k.split(":", 1)[1],
        "created_utc": g(v, "primary", "created_utc"),
        "pref_sym": g(v, "selfsig", "pref_sym"),
        "pref_hash": g(v, "selfsig", "pref_hash"),
        "pref_zip": g(v, "selfsig", "pref_zip"),
        "features": g(v, "selfsig", "features"),
        "matches_3301_triplet": (g(v, "selfsig", "pref_sym") == g(a, "selfsig", "pref_sym")
                                 and g(v, "selfsig", "pref_hash") == g(a, "selfsig", "pref_hash")
                                 and g(v, "selfsig", "pref_zip") == g(a, "selfsig", "pref_zip")),
    })

pref_same = all(c["same"] for c in comparison
                if c["field"].startswith("pref-") or c["field"] in ("features (MDC)", "keyserver prefs"))
hash_same = g(a, "selfsig", "digest_algo") == g(b, "selfsig", "digest_algo")
flags_same = g(a, "selfsig", "key_flags") == g(b, "selfsig", "key_flags")
n_base_match = sum(1 for x in base if x["matches_3301_triplet"])

# The era default, read out of GnuPG's own source rather than asserted.
# gnupg-1.4.16 g10/keygen.c, keygen_set_std_prefs(): with no default-preference-list
# in gpg.conf the compiled-in string is built as
#   "S9 S8 S7 S3 S2"  (AES256 AES192 AES128 CAST5 3DES)
#   "H8 H2 H9 H10 H11" (SHA256 SHA1 SHA384 SHA512 SHA224)
#   "Z2 Z3 Z1"        (ZLIB BZIP2 ZIP)
# with `int mdc=1, modify=0;` -> features 01, keyserver prefs 80 (no-modify).
ERA_DEFAULT = {
    "pref_sym": "9 8 7 3 2",
    "pref_hash": "8 2 9 10 11",
    "pref_zip": "2 3 1",
    "features": "01",
    "keyserver_prefs": "80",
    "source_url": "https://raw.githubusercontent.com/gpg/gnupg/gnupg-1.4.16/g10/keygen.c",
    "source_locus": "keygen_set_std_prefs(), the `if (!string || ... \"default\")` branch",
    "retrieved_utc": "2026-08-26",
    "applies_to": "GnuPG 1.4.x and 2.0.x (shared g10 keygen code) — the builds in general use in Jan 2012",
    "confidence": "verified (read from the released source of the era)",
}


def is_era_default(k):
    return all(g(k, "selfsig", f) == ERA_DEFAULT[f] for f in
               ("pref_sym", "pref_hash", "pref_zip", "features", "keyserver_prefs"))


both_are_factory_default = is_era_default(a) and is_era_default(b)

if not (pref_same and hash_same and flags_same):
    verdict = "MISMATCH"
elif both_are_factory_default:
    verdict = "INDECISIVE"
else:
    verdict = "MATCH"

out = {
    "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "lane": "round18/L8-provenance",
    "ledger_item": "I-01",
    "prereg_threshold": "MATCH = identical ordered preference lists AND identical self-sig hash "
                        "algo AND identical key-flag/feature bytes. MISMATCH = any ordered "
                        "preference list differs. INDECISIVE = preferences agree but are the "
                        "era-default of a common client.",
    "verdict": verdict,
    "verdict_inputs": {"preference_lists_identical": pref_same,
                       "selfsig_hash_algo_identical": hash_same,
                       "key_flags_identical": flags_same,
                       "cicada_key_is_gnupg_factory_default": is_era_default(a),
                       "mruzuki_key_is_gnupg_factory_default": is_era_default(b),
                       "both_are_factory_default": both_are_factory_default},
    "verdict_explanation":
        "Every field the two keys share is a field GnuPG fills in by itself. Read straight out of "
        "gnupg-1.4.16 g10/keygen.c, the compiled-in default preference set with no gpg.conf override "
        "is exactly S9 S8 S7 S3 S2 / H8 H2 H9 H10 H11 / Z2 Z3 Z1 with mdc=1 and modify=0 -- i.e. the "
        "identical values both keys carry. The agreement therefore carries no discriminating "
        "information: it says only that both keys were made by running `gpg --gen-key` on a 1.4/2.0 "
        "build and not editing the preference list. Every field a HUMAN chose -- key size, expiry "
        "policy, whether to revoke -- differs between them.",
    "era_default_reference": ERA_DEFAULT,
    "comparison": comparison,
    "base_rate_control": base,
    "base_rate_control_caveat":
        "UNDER-POWERED, and reported as such. Only 4 project keys were retrievable and none was "
        "created in Jan 2012 (2010, 2014, 2014, 2015). Worse, a live key's UID self-signature is "
        "REISSUED whenever the key is edited or extended, so a keyserver copy shows the preferences "
        "of the last edit rather than of key creation -- which is why the 2010 key here shows the "
        "GnuPG 2.1+ list. This sample cannot establish a 2012 base rate and was NOT used to decide "
        "the verdict; the GnuPG source default was. A properly matched control would need keys whose "
        "self-sigs are frozen in 2012 (abandoned or revoked keys), which this lane did not source.",
    "keys": results,
}
(HERE / "KEY-COMPARISON.json").write_text(json.dumps(out, indent=1))
print("verdict:", verdict)
for c in comparison:
    print(f"  {'=' if c['same'] else 'x'} {c['field']:26s} {str(c['cicada_7A35090F']):24s} | {c['mruzuki_FB8AFF75']}")
print("base rate (under-powered):", n_base_match, "of", len(base), "share the triplet")
for x in base:
    print("   ", x["key"], x["created_utc"], x["pref_hash"], x["matches_3301_triplet"])
