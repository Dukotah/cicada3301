#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble TOOLS.json from mechanical facts + hand-authored, code-backed judgements."""
import os, json, datetime, importlib.util

E = os.path.dirname(os.path.abspath(__file__))
CANON_FULL = "74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329"
CANON_UNSOLVED = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
SCREAM = "67a41c67b6a8e8678944d26e9c6af547ef0a07a21eb47e3fd483790ba48e81d7"

spec = importlib.util.spec_from_file_location("judgements", os.path.join(E, "judgements.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
JUDGE = mod.J

facts = json.load(open(os.path.join(E, "tools_facts.json"), encoding="utf-8"))["repos"]
try:
    dscan = json.load(open(os.path.join(E, "decoder_type_scan.json"), encoding="utf-8"))["repos"]
except Exception:
    dscan = {}
try:
    divc = json.load(open(os.path.join(E, "divergence_classified.json"), encoding="utf-8"))["results"]
except Exception:
    divc = []
divergent = {}
for r in divc:
    divergent.setdefault(r["repo"], []).append(
        {"path": r["path"], "verdicts": sorted({f["verdict"] for f in r["findings"]})})

def url_of(remote):
    if not remote: return None
    u = remote.rstrip("/")
    if u.endswith(".git"): u = u[:-4]
    return u

rows = []
for d, f in sorted(facts.items()):
    if d == "_iddqd_tmp":
        continue
    j = JUDGE.get(d, {})
    rf = f.get("rune_files") or []
    big = [x for x in rf if x["n_runes"] >= 5000]
    trans = None
    if big:
        b = max(big, key=lambda x: x["n_runes"])
        lineage = "unclassified"
        if b["sha256_indices"] == CANON_FULL:
            lineage = "IDENTICAL to canon (13,136 / 74cebdb0...)"
        elif b["sha256_indices"] == SCREAM:
            lineage = "scream314 15,938 lineage - carries C-E-01 and C-E-02"
        trans = {"path": b["path"], "n_runes": b["n_runes"],
                 "file_sha256": b["file_sha256"],
                 "sha256_indices": b["sha256_indices"], "lineage": lineage,
                 "other_rune_files": [x["path"] for x in rf if x is not b][:8]}
    ciph = dscan.get(d, {}).get("ciphers", {})
    row = {
        "name": d.replace("__", "/", 1),
        "vendor_dir": "corpus/E-tooling/vendor/" + d,
        "url": url_of(f.get("remote")),
        "clone_sha": f.get("clone_sha"),
        "shallow_clone": f.get("shallow"),
        "license": f.get("license"),
        "license_files": f.get("license_files"),
        "language": f.get("language"),
        "languages": f.get("languages"),
        "loc": dscan.get(d, {}).get("loc"),
        "first_commit_date": f.get("first_commit_date"),
        "last_commit_date": f.get("last_commit_date"),
        "n_commits": f.get("n_commits"),
        "authors": f.get("authors"),
        "cipher_families_referenced": dict(sorted(ciph.items(), key=lambda x: -x[1])[:10]),
        "what_it_tried": j.get("what_it_tried"),
        "what_it_concluded": j.get("what_it_concluded"),
        "has_transcription": bool(big),
        "transcription": trans,
        "transcription_sha256": (trans or {}).get("file_sha256"),
        "decoder_type": j.get("decoder_type", "unknown"),
        "decoder_evidence": j.get("evidence"),
        "null_trustworthy": j.get("null_trustworthy", "unknown"),
        "divergences_vs_canon": divergent.get(d),
        "notes": j.get("notes"),
    }
    rows.append(row)

order = {"skip-aware-search": 0, "skip-capable": 1, "rigid": 2, "unknown": 3, "no-decoder": 4}
rows.sort(key=lambda r: (order.get(r["decoder_type"], 9), -(r["loc"] or 0)))

counts = {}
for r in rows:
    counts[r["decoder_type"]] = counts.get(r["decoder_type"], 0) + 1
tn = {}
for r in rows:
    tn[str(r["null_trustworthy"])] = tn.get(str(r["null_trustworthy"]), 0) + 1

out = {
    "$comment": "Lane E catalogue of third-party Cicada 3301 / Liber Primus tooling. "
                "Every row is a repository cloned into corpus/E-tooling/vendor/ (the "
                "vendor tree itself is gitignored; clone_sha makes each row "
                "reproducible). Judgement fields (decoder_type, null_trustworthy, "
                "what_it_tried, what_it_concluded) are hand-authored from reading the "
                "code; decoder_evidence names the file and line the judgement rests on. "
                "Rows marked decoder_type 'unknown' were NOT read - do not treat them "
                "as rigid.",
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "decoder_type_vocabulary": {
        "rigid": "Key/keystream pointer advances once per ciphertext rune, "
                 "unconditionally. Cannot express a skip at all.",
        "skip-capable": "The decode primitive holds the key pointer if HANDED a set of "
                        "interrupter positions or an interrupter character, but the tool "
                        "performs no search over unknown skip patterns. Default call is "
                        "rigid.",
        "skip-aware-search": "The tool searches over which positions interrupt (subset "
                             "enumeration, beam, hill-climb, annealing) and can therefore "
                             "recover a key when the interrupter pattern is unknown.",
        "no-decoder": "Transcription, data, gematria table, hash or steganography work; "
                      "no polyalphabetic decode loop to classify.",
        "unknown": "Code present but the decisive loop was not read in this lane.",
    },
    "null_trustworthy_vocabulary": {
        "true": "The tool searched a space in which it could actually have succeeded, so "
                "a null from it is a real negative for that space.",
        "partial": "Trustworthy for the hypotheses it can express - usually 'no "
                   "interrupters' and 'every occurrence of X interrupts' - and not for an "
                   "unknown or irregular interrupter pattern.",
        "false": "The decoder could not have succeeded even if its hypothesis were right; "
                 "its null carries no information about that hypothesis.",
        "unknown": "Not assessed.", "n/a": "No decoder, so no null.",
    },
    "why_this_matters": "Under this project's anti-repeat filter, rigid decoding scores "
                        "the CORRECT key as noise (-6.835) while a skip-aware beam decoder "
                        "recovers it (-4.170). A null produced by a rigid decoder is "
                        "therefore not evidence against a key-skip hypothesis - it is "
                        "evidence that the instrument could not see it.",
    "canonical_hashes": {
        "full_13136_index_sha256": CANON_FULL,
        "unsolved_12956_index_sha256": CANON_UNSOLVED,
        "note": "Two different objects, not a conflict. See CONFLICTS-E.md.",
        "scream314_15938_index_sha256": SCREAM,
    },
    "summary": {"n_tools": len(rows), "by_decoder_type": counts,
                "by_null_trustworthy": tn},
    "tools": rows,
}
json.dump(out, open(os.path.join(E, "TOOLS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(json.dumps(out["summary"], indent=1))
for r in rows:
    print(f"{r['decoder_type']:18s} {str(r['null_trustworthy']):8s} {r['name'][:52]:52s} "
          f"{str(r['license'])[:12]:12s} {(r['first_commit_date'] or '')[:10]}")
