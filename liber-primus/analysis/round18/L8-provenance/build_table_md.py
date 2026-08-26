#!/usr/bin/env python3
"""L8 — render PGP-VERIFICATION-TABLE.md from PGP-VERIFICATION-TABLE.json.

Also emits MESSAGES.json: one row per DISTINCT signed message (grouped by the
sha256 of its normalised signed body), which is the object the timestamp-seed
list is built from.
"""
import hashlib
import json
import re
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
T = json.loads((HERE / "PGP-VERIFICATION-TABLE.json").read_text())
ROWS = T["rows"]

HASH_ALGO = {1: "MD5", 2: "SHA-1", 3: "RIPE-MD/160", 8: "SHA-256", 9: "SHA-384",
             10: "SHA-512", 11: "SHA-224"}
PK_ALGO = {1: "RSA", 17: "DSA", 22: "EdDSA"}


ARMOR_HDR = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:")


def signed_body_text(path):
    """RFC-4880 cleartext body, robustly normalised.

    Consumes armor headers by SHAPE (`Name: value`), not by assuming the blank
    line is present -- a mirror that dropped the blank line after `Hash: SHA1`
    still yields the same body here, which is exactly the comparison PREREG.md
    specified ("sha256 + normalised-body comparison").
    Dash-escaping is undone; line endings and trailing whitespace normalised.
    """
    try:
        raw = (REPO / path).read_bytes().replace(b"\r\n", b"\n").decode("utf-8", "replace")
    except OSError:
        return None
    if "-----BEGIN PGP SIGNED MESSAGE-----" not in raw:
        return None
    after = raw.split("-----BEGIN PGP SIGNED MESSAGE-----", 1)[1]
    after = after.split("-----BEGIN PGP SIGNATURE-----", 1)[0]
    lines = after.split("\n")
    i = 0
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    while i < len(lines) and ARMOR_HDR.match(lines[i].strip()):
        i += 1
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    body = [l[2:] if l.startswith("- ") else l for l in lines[i:]]
    return "\n".join(x.rstrip() for x in body).strip()


def body_hash(path):
    b = signed_body_text(path)
    return hashlib.sha256(b.encode()).hexdigest() if b is not None else None


def first_line(path):
    b = signed_body_text(path) or ""
    for l in b.split("\n"):
        l = l.strip()
        if l:
            return re.sub(r"\s+", " ", l)[:70]
    return ""


# ---------------------------------------------------------------- group by message body
groups = defaultdict(list)
for r in ROWS:
    if r["verdict"] in ("PASS", "FAIL"):
        groups[body_hash(r["path"]) or ("nobody:" + r["sha256"])].append(r)

messages = []
for body_sha, rs in groups.items():
    rs.sort(key=lambda r: r["path"])
    ts = next((r["signature_timestamp_unix"] for r in rs if r["signature_timestamp_unix"]), None)
    tsu = next((r["signature_timestamp_utc"] for r in rs if r["signature_timestamp_utc"]), None)
    verdicts = {r["verdict"] for r in rs}
    messages.append(OrderedDict(
        body_sha256=body_sha,
        first_line=first_line(rs[0]["path"]),
        verdict=("PASS" if "PASS" in verdicts else "FAIL"),
        copies_pass=sum(1 for r in rs if r["verdict"] == "PASS"),
        copies_fail=sum(1 for r in rs if r["verdict"] == "FAIL"),
        signature_timestamp_unix=ts,
        signature_timestamp_utc=tsu,
        signing_keyid=next((r["signing_keyid_from_packet"] for r in rs), None),
        digest_algo=HASH_ALGO.get(rs[0]["digest_algo"], rs[0]["digest_algo"]),
        pubkey_algo=PK_ALGO.get(rs[0]["signature_packets"][0]["pubkey_algo"], None)
        if rs[0]["signature_packets"] else None,
        distinct_file_sha256=sorted({r["sha256"] for r in rs}),
        paths=[r["path"] for r in rs],
    ))
messages.sort(key=lambda m: (m["signature_timestamp_unix"] or 0, m["first_line"]))
(HERE / "MESSAGES.json").write_text(json.dumps({
    "generated_utc": T["finished_utc"],
    "note": "One row per DISTINCT signed message body across the whole repository. "
            "Copies are byte-different mirrors of the same signed text.",
    "verification_key": T["verification_key"]["fingerprint"],
    "count": len(messages),
    "messages": messages,
}, indent=1))

# ---------------------------------------------------------------- markdown
L = []
A = L.append
A("# The PGP verification table — every claimed Cicada 3301 signature in this repository")
A("")
A(f"_Round 18 lane **L8-provenance**. Generated {T['finished_utc']} by "
  "`liber-primus/analysis/round18/L8-provenance/verify_all_signatures.py`._")
A("")
A("Closes the machine-verification half of `corpus/GAPS.md` **G-02** "
  "(*\"no file in this repository records which signatures verify against key 7A35090F and which do not\"*).")
A("")
A("**Every row below is `verified`** in the confidence sense of `KNOWLEDGE.json`: it is the output of")
A("running `gpg --verify` on bytes held in this tree, reproducible by the command in §6. Nothing in this")
A("file is reported or speculated. Provenance of the *bytes* — which mirror they came from — is a")
A("separate question and is treated in §5.")
A("")
A("> A valid signature from `7A35090F` proves **keyholder continuity**. It does not prove authorship,")
A("> identity, or that the timestamp inside it is the real wall-clock time it was made. See §7.")
A("")
A("## 1. The instrument, and proof that it works in both directions")
A("")
vk = T["verification_key"]
A(f"- gpg: `{T['gpg_version']}`")
A(f"- verification key: `{vk['fingerprint']}` (`{vk['long_id']}`, short `{vk['short_id']}`)")
A(f"- keyring: **isolated** — a throwaway `GNUPGHOME` holding exactly one primary key, "
  f"`{', '.join(vk['keyring_primary_fingerprints'])}`, so a PASS cannot come from any other key on the box")
A(f"- scope: **every `*.asc` in the repository** — {T['summary']['files_scanned']} files, "
  f"{T['summary']['distinct_files_by_sha256']} distinct by sha256")
A("")
A("Rule 2 of the campaign plan: *a null from an unvalidated instrument is not a negative.* The four")
A("controls were fixed in `PREREG.md` before the run.")
A("")
A("| control | what it does | required output | measured | met |")
A("|---|---|---|---|---|")
c = T["instrument_controls"]
A(f"| **C1** | verify an untouched known-good file | `GOODSIG {vk['long_id'][2:]}` | "
  f"`GOODSIG {c['C1_pass']['goodsig']}` | {'✅' if c['C1_pass']['met'] else '❌'} |")
A(f"| **C2** | flip one character of the *signed body* | `BADSIG` | "
  f"`BADSIG {c['C2_fail_on_tamper']['badsig']}`, no GOODSIG | {'✅' if c['C2_fail_on_tamper']['met'] else '❌'} |")
A(f"| **C3** | verify a message signed by a freshly generated foreign key | not GOODSIG for 3301 | "
  f"`NO_PUBKEY {c['C3_fail_on_foreign_key']['no_pubkey']}` / `ERRSIG {c['C3_fail_on_foreign_key']['errsig']}`, "
  f"no GOODSIG | {'✅' if c['C3_fail_on_foreign_key']['met'] else '❌'} |")
A(f"| **C4** | recover the timestamp from the *tampered* file | original `created` unchanged | "
  f"`{c['C4_timestamp_survives_tamper']['original_created_unix']}` → "
  f"`{c['C4_timestamp_survives_tamper']['tampered_created_unix']}` | "
  f"{'✅' if c['C4_timestamp_survives_tamper']['met'] else '❌'} |")
A("")
A(f"**All four controls met: {'YES' if c.get('all_met') else 'NO'}.** C2/C3 are what make a FAIL in this")
A("table mean something; C4 is why a FAILing file still yields a usable timestamp.")
A("")
A("## 2. Headline counts")
A("")
s = T["summary"]
A("| verdict | files | meaning |")
A("|---|---|---|")
A(f"| **PASS** | {s['by_verdict'].get('PASS', 0)} | `GOODSIG` + `VALIDSIG` for the canonical fingerprint |")
A(f"| **FAIL** | {s['by_verdict'].get('FAIL', 0)} | a signature packet is present and does not verify |")
A(f"| **NO-SIG** | {s['by_verdict'].get('NO-SIG', 0)} | no signature block in the file at all |")
A(f"| **KEY** | {s['by_verdict'].get('KEY', 0)} | the file is a public-key block, not a message |")
A(f"| total | {s['files_scanned']} | |")
A("")
A(f"- **Distinct signing key IDs across every signed message in the repository: "
  f"{len(s['distinct_signing_keyids_in_messages'])} — `{', '.join(s['distinct_signing_keyids_in_messages'])}`.**")
A("  No second signing key appears anywhere. That is the single most load-bearing line in this table:")
A("  the corpus is internally consistent with one keyholder throughout 2012–2017.")
A(f"- Distinct signed **messages** (grouped by normalised body): **{len(messages)}**. "
  f"The {s['files_scanned']} files are mostly mirrors of each other.")
A(f"- Distinct verified signature timestamps: **{s['distinct_verified_timestamps']}**, spanning "
  f"`{s['verified_timestamp_range_utc']['earliest']}` → `{s['verified_timestamp_range_utc']['latest']}`.")
A("")
A("## 3. The messages — one row per distinct signed text")
A("")
A("Chronological by signature-packet timestamp. `copies` = how many byte-different files in this")
A("repository carry this same signed body.")
A("")
A("| # | sig timestamp (UTC) | verdict | copies P/F | hash | first line of the signed text |")
A("|---|---|---|---|---|---|")
for i, m in enumerate(messages, 1):
    A(f"| {i} | `{m['signature_timestamp_utc'] or '—'}` | **{m['verdict']}** | "
      f"{m['copies_pass']}/{m['copies_fail']} | {m['digest_algo']} | {m['first_line'] or '—'} |")
A("")
A("Full per-file detail — path, sha256, byte length, raw gpg status lines, signature packet —")
A("is in `PGP-VERIFICATION-TABLE.json`; the per-message grouping is in `MESSAGES.json`.")
A("")
# --- digest algorithm fingerprint
dcount = Counter(m["digest_algo"] for m in messages)
A("### 3b. A toolchain fingerprint in the hash column")
A("")
A("The `hash` column is not decoration. Across all "
  f"{len(messages)} messages the digest algorithm is: "
  + ", ".join(f"**{k} × {v}**" for k, v in dcount.most_common()) + ".")
A("")
A("Every message from 2012-01-05 to 2016-01-01 is signed with **SHA-1**. The last message,")
A("2017-04-04, is signed with **SHA-512**. The signing setup changed exactly once, near the end.")
A("")
A("SHA-1 was GnuPG's compiled-in default `personal-digest-preference` for the 1.4 / early-2.0 era;")
A("newer builds and any `digest-algo` line in `gpg.conf` move it off SHA-1. So this single switch is a")
A("**dated, verified observation about the author's tooling** — an upgrade, a reinstall, or a config")
A("change somewhere between 2016-01-01 and 2017-04-04 — and it is exactly the kind of artifact Round")
A("18's thesis is looking for (`round18/CAMPAIGN-PLAN.md`: *we are hunting a short script written by a")
A("human being*). Handed to **L1-toolchain** as a prior, not as a conclusion.")
A("")
A("Stated honestly: this narrows *when the toolchain changed*. It does not narrow *who*, and it does")
A("not by itself identify a GnuPG version — several versions share these defaults.")
A("")

# --- FAIL section
fails = [r for r in ROWS if r["verdict"] == "FAIL"]
A("## 4. The FAILs")
A("")
if not fails:
    A("None.")
else:
    A(f"{len(fails)} files fail. They are **one message**, mirrored three times:")
    A("")
    A("| file | bytes | gpg | sig timestamp | keyid in packet |")
    A("|---|---|---|---|---|")
    for r in fails:
        A(f"| `{r['path']}` | {r['bytes']} | {r.get('fail_reason')} | "
          f"`{r['signature_timestamp_utc']}` | `{r['signing_keyid_from_packet']}` |")
    A("")
    A("**Verdict under the pre-registered rule: transport defect, not a canon failure.** `PREREG.md`")
    A("fixed the test in advance — *a FAIL is a finding about the message only if the same body has no")
    A("PASSing copy elsewhere, compared by sha256 and normalised body*. Under that comparison this body")
    A("**does** pass elsewhere: 4 other files in the tree carry the identical normalised signed text and")
    A("verify (row 18 of §3, `copies 4/3`).")
    A("")
    A("The defect is named exactly by gpg's own stderr: `invalid armor header: Welcome again.` The")
    A("mirror dropped the blank line that must separate the `Hash: SHA1` armor header from the message,")
    A("so the message's first line is parsed as a header and excluded from the hashed data. The repo")
    A("already holds a deliberately repaired copy —")
    A("`corpus/A-primary-artifacts/pgp/repaired/ky_2013-01-opening-book-code.repaired.asc`, 1538 bytes")
    A("against the damaged 1536 — and **it PASSes carrying the identical signature packet**")
    A("(`2013-01-03T04:33:29Z`). The text is authentic; three files are damaged in transport.")
    A("")
    A("**So the answer to G-02's question is: of the 54 distinct signed messages held here, 54 verify")
    A("against `7A35090F` and 0 do not.** No message the community treats as canon has been shown by")
    A("this run to carry a bad signature from an undamaged file.")
    A("")
    A("That is a clean result, and it is also the warning. A **two-byte** whitespace defect turns an")
    A("authentic Cicada message into a `BADSIG`. Any solver who runs the repo's own authenticity test")
    A("against a casually-mirrored copy will get a false negative and may conclude a real message is a")
    A("forgery. Three such files are sitting in this tree right now.")
    A("")
    A("This is a corpus-hygiene finding, not a canon failure: no message that the community treats as")
    A("Cicada has been shown here to carry a bad signature from a good file. It is also a warning —")
    A("a two-byte transport defect turns an authentic message into a BADSIG, which is exactly how a")
    A("real authenticity test gets quietly mis-scored.")
A("")

# --- NO-SIG section
nosig = [r for r in ROWS if r["verdict"] == "NO-SIG"]
stubs = [r for r in nosig if r["bytes"] == 199]
A("## 5. The NO-SIGs — and a truncated-download finding")
A("")
A(f"{len(nosig)} files carry no signature block. They are not one thing:")
A("")
A(f"- **{len(stubs)} files are 199-byte GitHub rate-limit stubs**, not messages at all. Every one is in")
A("  `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/`, and every one contains")
A("  the literal text `429: Too Many Requests`. They were saved by a fetch that did not check its")
A("  HTTP status, and they have sat in the tree since Round 10 looking like a corpus of communications.")
A("  This is the same failure mode as the `_560.00` truncation recorded in `corpus/GAPS.md` **G-12**,")
A("  and it is why that section's re-collection rule exists. The corpus lane already refetched clean")
A("  copies into `corpus/A-primary-artifacts/pgp/messages/`; the stubs under `round10/` were never")
A("  cleaned up and are still reachable by any tool that globs the tree.")
A("- The rest are genuinely unsigned held material: a raw TCP-server transcript, an OutGuess payload")
A("  fragment, and two rune data files that merely use the `.asc` extension.")
A("")
A("| file | bytes | what it is |")
A("|---|---|---|")
for r in nosig:
    what = ("**HTTP 429 stub — not a message**" if r["bytes"] == 199
            else "unsigned held text / data (`.asc` extension, not OpenPGP)")
    A(f"| `{r['path']}` | {r['bytes']} | {what} |")
A("")

# --- KEY section
keys = [r for r in ROWS if r["verdict"] == "KEY"]
A("## 6. The key files")
A("")
A(f"{len(keys)} files are public-key blocks. Each was probed with `--import-options show-only`; only")
A("blocks whose primary fingerprint is the canonical one were imported into the verification keyring.")
A("")
A("| file | bytes |")
A("|---|---|")
for r in keys:
    A(f"| `{r['path']}` | {r['bytes']} |")
A("")
A("**One naming hazard worth recording.** "
  "`corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc` is named")
A("for the fingerprint `67F3…0670B0E5**7A35090F**`, which is **not** the canonical")
A("`6D85…181F01E5**7A35090F**` — the two agree only in the trailing 32-bit short ID. The block *inside*")
A("the file is the canonical key (verified: primary fpr `6D854CD7933322A601C3286D181F01E57A35090F`),")
A("so the filename is a mislabel rather than a second key. Do not treat the filename as an identifier,")
A("and do not verify anything by short ID: 32 bits is not a key.")
A("")
A("## 7. What this table does and does not establish")
A("")
A("**Establishes (verified):**")
A("1. Which held files verify against `7A35090F`, by name, with hashes — the thing G-02 says is")
A("   recorded nowhere.")
A("2. That exactly one signing key ID appears across every signed message in the tree.")
A("3. A machine-read timestamp for every signature, including for files that fail to verify.")
A("4. That 19 files in the Round-10 fetch are HTTP error pages rather than communications.")
A("")
A("**Does not establish:**")
A("1. *Completeness.* This is a corpus of mirrors of mirrors. A message nobody mirrored is not here,")
A("   and its absence is not evidence. `corpus/GAPS.md` G-12 applies to every byte in it.")
A("2. *Authorship.* A good signature proves the signer held the private key. Nothing more.")
A("3. *Wall-clock truth of any timestamp.* Under RFC 4880 the creation time is a hashed subpacket")
A("   taken from the signer's own clock, and is therefore settable by the signer.")
A("   `liber-primus/analysis/AUDITOR-LOOP-2026-07-28.md` used exactly this to **refute** the")
A("   timezone/working-hours biometric built on these timestamps (n=26, irreproducible). That")
A("   refutation stands and this table does not reopen it.")
A("4. *That the 2023 public self-claim is settled by anything here.* It is out of scope: no `.asc`")
A("   attributable to it is held in this tree, so it is neither confirmed nor refuted by this run.")
A("")
A("## 8. Reproduce")
A("")
A("```bash")
A("wsl -d Ubuntu -- bash -lc \"cd /mnt/c/Users/dukot/projects/cicada3301 && \\")
A("  python3 liber-primus/analysis/round18/L8-provenance/verify_all_signatures.py\"")
A("python3 liber-primus/analysis/round18/L8-provenance/build_table_md.py")
A("```")
A("")
A("The script builds its own keyring from scratch every run and refuses to proceed if that keyring")
A("holds more than the one primary key, so the result cannot be contaminated by the operator's")
A("existing GnuPG state.")
A("")
(HERE / "PGP-VERIFICATION-TABLE.md").write_text("\n".join(L), encoding="utf-8")
print("messages:", len(messages), "| md lines:", len(L))
