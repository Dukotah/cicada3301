"""Build handoff/capsule/MANIFEST.json — the frozen data capsule index.

WHY THIS EXISTS
---------------
Half the inputs to this repo's analysis are not in the repo. The 56 page images are
gitignored and re-fetched from third-party GitHub mirrors; the corpora come from
Project Gutenberg; the CicadaOS pads came from a community archive whose Git-LFS
objects have already been deleted once. Every one of those is one dead link away
from taking a decade of negative results with it.

This script walks a hand-curated registry of every essential input, computes SHA-256
(and SHA-1, to cross-check `analysis/stego/provenance.json`) for everything present
on disk, and emits MANIFEST.json. `verify_capsule.py` consumes that manifest and
re-checks drift or death per item.

Design rules:
  * Hashes are MEASURED here, never transcribed by hand.
  * Provenance and mirror URLs are recorded as data, including when they are
    reconstructed rather than documented — see `provenance_confidence`.
  * Large binaries are NEVER committed. The manifest is the artifact; the bytes are
    re-fetchable (or, for one item, were).

Run:  python3 handoff/capsule/build_manifest.py
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", ".."))          # liber-primus/
REPO = os.path.abspath(os.path.join(LP, ".."))                 # repo root
SCHEMA_VERSION = "1.0"

# --------------------------------------------------------------------------- status vocabulary
# in-repo             : committed; a fresh clone has the bytes
# gitignored-fetchable: not committed; recipe + mirrors below reproduce it byte-identically
# derived             : computed from another capsule item by a script in this repo
# LOST                : the authoritative bytes are not retrievable from any known source
# RECOVERED           : was LOST in a prior round; this capsule re-established a live source

CHUNK = 1 << 20


def digests(path):
    """SHA-256, SHA-1 and byte size of a file, streamed."""
    s256, s1, n = hashlib.sha256(), hashlib.sha1(), 0
    with open(path, "rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            n += len(b)
            s256.update(b)
            s1.update(b)
    return s256.hexdigest(), s1.hexdigest(), n


def item(iid, role, path, status, provenance, mirrors, notes="",
         provenance_confidence="documented", expect_sha1=None, extra=None):
    """One manifest row. `path` is repo-relative (or None for pure-URL items)."""
    rec = {
        "id": iid,
        "role": role,
        "path": path,
        "status": status,
        "provenance": provenance,
        "provenance_confidence": provenance_confidence,
        "mirrors": mirrors,
        "notes": notes,
    }
    if extra:
        rec.update(extra)
    if path:
        ap = os.path.join(REPO, path)
        if os.path.exists(ap) and os.path.isfile(ap):
            s256, s1, n = digests(ap)
            rec["sha256"] = s256
            rec["sha1"] = s1
            rec["bytes"] = n
            rec["hash_verified_locally"] = True
            if expect_sha1 is not None:
                rec["published_sha1"] = expect_sha1
                rec["published_sha1_match"] = (s1 == expect_sha1)
        else:
            rec["sha256"] = None
            rec["sha1"] = None
            rec["bytes"] = None
            rec["hash_verified_locally"] = False
            if expect_sha1 is not None:
                rec["published_sha1"] = expect_sha1
    return rec


# --------------------------------------------------------------------------- registry
def build():
    items = []

    # ---------------------------------------------------------------- 1. the ciphertext
    items.append(item(
        "runes.canonical",
        "THE PRIMARY INPUT. Canonical rune transcription of Liber Primus part 2 "
        "(onion7 pages 0-57), '%'-delimited per page. Every attack in this repo reads this file.",
        "liber-primus/data/krisyotam_runes.txt",
        "in-repo",
        ["rtkd/iddqd 2017 community-root transcription lineage (krisyotam copy)",
         "All community lineages verified rune-identical -- see liber-primus/analysis/transcription/",
         "Independently corroborated: liber-primus/tests/validate.py reproduces all 5 solved "
         "pages from these exact runes, which a materially wrong transcription could not do."],
        ["https://raw.githubusercontent.com/rtkd/iddqd/master/liber-primus__transcription--master/"
         "liber-primus__transcription--master.txt",
         "https://github.com/relikd/LiberPrayground/tree/master/pages"],
        notes="If you replace this file you invalidate every result in the repo. "
              "Re-run tests/validate.py before and after any change.",
    ))

    # derived: the 12,956-rune unsolved stream actually fed to attacks
    try:
        sys.path.insert(0, os.path.join(LP, "src"))
        sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
        import lib_numchannel as nc  # noqa: E402
        u = nc.unsolved()
        payload = ",".join(str(x) for x in u).encode()
        items.append({
            "id": "runes.unsolved_stream",
            "role": "THE ATTACK TARGET. The 12,956 rune indices of the unsolved pages "
                    "(LP2 pages 0-54), in reading order, as produced by "
                    "analysis/round11/lib_numchannel.py nc.unsolved().",
            "path": None,
            "status": "derived",
            "derived_from": ["runes.canonical"],
            "derivation": "python3 -c \"import sys; sys.path[:0]=['liber-primus/src',"
                          "'liber-primus/analysis/round11']; import lib_numchannel as nc; "
                          "print(len(nc.unsolved()))\"",
            "length_runes": len(u),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "sha256_of": "comma-joined decimal rune indices, ASCII, no trailing newline",
            "bytes": len(payload),
            "hash_verified_locally": True,
            "provenance": ["derived from runes.canonical by this repo"],
            "provenance_confidence": "documented",
            "mirrors": [],
            "notes": "This is the single number that must match for any future re-analysis to be "
                     "comparable to this repo's: 12,956 runes. If your pipeline yields a "
                     "different count or a different SHA-256 here, stop and reconcile before "
                     "reading any result in this repo as a comparison.",
        })
    except Exception as e:  # pragma: no cover - environment-dependent
        items.append({
            "id": "runes.unsolved_stream", "path": None, "status": "derived",
            "role": "THE ATTACK TARGET (12,956 rune indices)",
            "error": f"could not derive in this environment: {e!r}",
            "provenance": [], "mirrors": [], "notes": "",
            "provenance_confidence": "documented", "hash_verified_locally": False,
        })

    items.append(item(
        "dataset.liber_primus_json",
        "Machine-readable LP2 dataset: gematria table, per-page runes/transliteration/indices, "
        "verified image hashes, solved-page key reference. Built by dataset/build_dataset.py.",
        "liber-primus/dataset/liber_primus.json",
        "in-repo",
        ["built in-repo from runes.canonical + images.onion7.* + analysis/stego/provenance.json"],
        [],
        notes="Rebuild: python3 liber-primus/dataset/build_dataset.py (needs data/relikd/ present).",
    ))

    items.append(item(
        "gematria.primus",
        "The mod-29 Gematria Primus: rune -> index -> transliteration -> prime. The alphabet "
        "every cipher in this repo operates over.",
        "liber-primus/src/lp/gematria.py",
        "in-repo",
        ["Cicada 3301's own published Gematria Primus table (2013 Liber Primus page 'A WARNING' "
         "context); universally agreed across the solver community"],
        [],
    ))

    # ---------------------------------------------------------------- 2. ground truth
    items.append(item(
        "groundtruth.validate",
        "THE TRUST ANCHOR. Reproduces all 5 solved LP2 pages from runes.canonical through this "
        "repo's cipher rig. Must print 'ALL VALIDATIONS PASSED' before any result here is "
        "trustworthy.",
        "liber-primus/tests/validate.py",
        "in-repo",
        ["in-repo; asserts against community-accepted solved-page plaintexts"],
        [],
        notes="Run first, always: "
              "python3 liber-primus/tests/validate.py",
    ))

    items.append(item(
        "groundtruth.scream314_lp",
        "THE VALIDATION CORPUS. scream314's Liber Primus markdown: per-page runes for LP1 "
        "(17 pages) and LP2 (58 pages, 0-57) with the solved pages' documented transforms. "
        "This is the file tests/validate.py actually parses (via src/lp/corpus.py) to "
        "re-derive the five solved pages.",
        "liber-primus/data/scream314_lp.md",
        "in-repo",
        ["scream314's Liber Primus writeup, a community compilation of the published pages "
         "and their accepted solutions"],
        ["https://github.com/scream314/cicada3301"],
        notes="Without this file tests/validate.py cannot run, and without validate.py nothing "
              "in this repo is trustworthy. It is committed for exactly that reason.",
    ))

    items.append(item(
        "groundtruth.solved_plaintext",
        "Solved-page plaintexts (LP1 + LP2 pages 55-57 and the solved LP2 pages), used as the "
        "positive-control corpus and as a candidate keytext.",
        "liber-primus/data/keys/solved_plaintext.txt",
        "in-repo",
        ["community-accepted solved-page decryptions, cross-checked by tests/validate.py"],
        [],
    ))

    items.append(item(
        "groundtruth.provenance_stego",
        "The 56/56 SHA-1 provenance table tying the circulating page images to the archived "
        "onion7 dump. Cross-checked and extended to SHA-256 by this capsule.",
        "liber-primus/analysis/stego/provenance.json",
        "in-repo",
        ["computed in-repo against archive.org item ky2khlqdf7qdznac.onion files.xml"],
        ["https://archive.org/metadata/ky2khlqdf7qdznac.onion",
         "https://archive.org/download/ky2khlqdf7qdznac.onion/ky2khlqdf7qdznac.onion_files.xml"],
    ))

    # ---------------------------------------------------------------- 3. the 56 page images
    prov_path = os.path.join(LP, "analysis", "stego", "provenance.json")
    pub = {}
    if os.path.exists(prov_path):
        pj = json.load(open(prov_path, encoding="utf-8"))
        pub = {r["page"]: r.get("published_sha1") for r in pj.get("rows", [])}

    for p in range(56):
        items.append(item(
            f"images.onion7.p{p:02d}",
            f"LP2 page image {p} (onion7 file {p}.jpg), 2400x3600 JPEG, 400 DPI, "
            "Artifex/Ghostscript sRGB ICC. The primary-source artifact behind runes.canonical.",
            f"liber-primus/data/relikd/p{p}.jpg",
            "gitignored-fetchable",
            ["Cicada 3301 onion7 hidden service ky2khlqdf7qdznac.onion, May 2014 LP2 dump",
             "archived: Internet Archive item ky2khlqdf7qdznac.onion",
             "circulating copy: relikd/LiberPrayground -- proven SHA-1 identical to the "
             "archived onion dump, 56/56 (analysis/stego/provenance.json)"],
            ["https://archive.org/download/ky2khlqdf7qdznac.onion/%d.jpg" % p,
             "https://github.com/relikd/LiberPrayground",
             "https://github.com/rtkd/iddqd (unmodified files)",
             "https://github.com/micheloosterhof/cicada-2014 (original 2014-05 capture)"],
            expect_sha1=pub.get(p),
            notes="Gitignored under 'liber-primus/data/relikd/'. published_sha1 is the value in "
                  "the archived onion7 files.xml; published_sha1_match true means the local copy "
                  "IS the original bytes.",
        ))

    # ---------------------------------------------------------------- 4. pp49-51 payload
    items.append(item(
        "payload.canon_256",
        "The 256-byte binary payload canonicalised from LP2 pages 49-51 (the only non-runic "
        "payload in the unsolved corpus). Input to the B-05 'payload as PRF seed' lane.",
        "liber-primus/analysis/pp49_51/canon_256.bin",
        "in-repo",
        ["canonicalised in-repo by analysis/pp49_51/canonicalize.py from the page 49-51 hex "
         "digits as transcribed off images.onion7.p49/p50/p51"],
        [],
        notes="CAVEAT recorded in analysis/pp49_51/CAMPAIGN-VII-FINDINGS.md and repeated in "
              "CAMPAIGN-IX: 6 bytes are CONTESTED (indices 25, 175, 182, 199, 215, 237). They "
              "have never been resolved by a Latin/digit OCR. Any negative result over this "
              "payload is conditional on those 6 bytes. See PARKED.md item P-07.",
    ))

    items.append(item(
        "payload.canon_256_decpref",
        "Alternate canonicalisation of the pages 49-51 payload (decimal-preferring reading).",
        "liber-primus/analysis/pp49_51/canon_256_decpref.bin",
        "in-repo",
        ["canonicalised in-repo by analysis/pp49_51/canonicalize.py"],
        [],
    ))

    items.append(item(
        "payload.canonicalize_script",
        "The script that turns the transcribed pages 49-51 characters into canon_256.bin.",
        "liber-primus/analysis/pp49_51/canonicalize.py",
        "in-repo", ["in-repo"], [],
    ))

    # ---------------------------------------------------------------- 5. CicadaOS pads (Round 12 A1)
    ISO_INNER = "https://archive.org/download/3301.iso/3301.iso/DATA%2F{}"
    pad_prov = [
        "CicadaOS 2013 bootable ISO shipped by Cicada 3301 (the '3301.iso' / Instar Emergence "
        "stage). These are the author's own binary blobs.",
        "Round 12 front A1 fetched them from the cicada-solvers community archive.",
    ]
    pad_mirrors = [
        "https://archive.org/details/3301.iso",
        "https://archive.org/download/3301.iso/3301.iso  (whole ISO, 136,398,848 B, "
        "sha1 df433cba87644b35cbc47f702a02e2b58d90af6a; supports HTTP Range)",
        "https://archive.org/download/3301.iso/3301.iso/  (archive.org serves an inner-file "
        "listing and streams individual members)",
    ]
    items.append(item(
        "pads.cicadaos.DATA_560.17",
        "CicadaOS DATA/560.17 -- 1,183,811 B binary blob. Candidate authored key material; fed "
        "as a mod-29 keystream under the skip-aware beam decoder in Round 12 front A1 "
        "(result: NEGATIVE).",
        "liber-primus/analysis/round12/A1/pads/DATA_560.17",
        "in-repo", pad_prov, [ISO_INNER.format("560.17")] + pad_mirrors,
        notes="VERIFIED 2026-08-19 byte-identical to the copy inside the authoritative "
              "archive.org 3301.iso (sha256 d5676b1e...). This mirror copy is sound.",
    ))

    items.append(item(
        "pads.cicadaos.DATA__560.00.TRUNCATED",
        "CicadaOS DATA/_560.00 as fetched from the cicada-solvers community archive and "
        "ACTUALLY TESTED by Round 12 front A1 -- 2,412,544 B.",
        "liber-primus/analysis/round12/A1/pads/DATA__560.00",
        "in-repo", pad_prov, [],
        notes="*** DEFECTIVE INPUT -- DO NOT USE FOR NEW WORK. *** This copy is 1,580,426 bytes "
              "SHORT of the file in the authoritative CicadaOS ISO (2,412,544 vs 3,992,970 -- "
              "~40% missing), and the two have different sha256. Verified 2026-08-19; see "
              "handoff/capsule/RECOVERY-560.13.md. Round 12 A1 used this file both as a swept pad "
              "AND to build its positive control and null ceiling, so A1's _560.00 negative "
              "covers only ~60% of the real blob. Kept in place, unmodified, so A1's existing "
              "results stay reproducible against the input that produced them.",
    ))

    items.append(item(
        "pads.cicadaos.DATA__560.00",
        "CicadaOS DATA/_560.00, AUTHORITATIVE copy -- 3,992,970 B, extracted from the "
        "archive.org 3301.iso first-party image. This is the real blob; use this one.",
        "liber-primus/analysis/round12/A1/pads/DATA__560.00.iso-authoritative",
        "gitignored-fetchable", pad_prov,
        [ISO_INNER.format("_560.00")] + pad_mirrors,
        notes="Recovered 2026-08-19 by this capsule after discovering the community-archive copy "
              "is truncated. NEVER swept -- Round 12 A1 tested the short file. Re-running A1 "
              "over this copy is part of PARKED.md P-3.",
    ))

    for fn, desc in [
        ("tmp_folly", "CicadaOS tmp/folly -- 3,368 B (byte-identical to tmp/wisdom; one pad)"),
        ("tmp_wisdom", "CicadaOS tmp/wisdom -- 3,368 B (byte-identical to tmp/folly)"),
        ("usr_local_bin_prime_echo",
         "CicadaOS usr/local/bin/prime_echo -- 12,248 B; the binary that CONSUMES the DATA pads"),
    ]:
        items.append(item(
            f"pads.cicadaos.{fn}", desc,
            f"liber-primus/analysis/round12/A1/pads/{fn}",
            "in-repo", pad_prov, pad_mirrors,
        ))

    # DATA/560.13 -- the item recorded LOST in Round 12 A1
    r13 = os.path.join(LP, "handoff", "capsule", "recovered", "DATA_560.13.sha256")
    r13_status = "LOST"
    r13_extra = {
        "expected_sha256": "db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f",
        "expected_bytes": 118818811,
        "recovery_log": "handoff/capsule/RECOVERY-560.13.md",
    }
    if os.path.exists(r13):
        got = open(r13, encoding="utf-8").read().split()
        if got and got[0] == r13_extra["expected_sha256"]:
            r13_status = "RECOVERED"
            r13_extra["recovered_sha256"] = got[0]
            r13_extra["recovered_bytes"] = int(got[1]) if len(got) > 1 else None
    items.append(item(
        "pads.cicadaos.DATA_560.13",
        "CicadaOS DATA/560.13 -- 118,818,811 B, the LARGEST authored blob and the one pad Round "
        "12 front A1 could never test. In both the cicada-solvers and krisyotam GitHub mirrors "
        "this path is a 134-byte Git-LFS pointer and the LFS batch API returns "
        "'404 Object does not exist on the server'.",
        "liber-primus/analysis/round12/A1/pads/DATA_560.13",
        r13_status,
        pad_prov + ["Git-LFS object deleted from both GitHub mirrors (verified Round 12, "
                    "2026-08-17). Only surviving avenue: the archive.org 3301.iso item."],
        # direct inner-file URL FIRST: a probe must hit real bytes, not the details page
        [ISO_INNER.format("560.13")] + pad_mirrors,
        notes="Round 12 A1's stated single remaining lever. See handoff/PARKED.md P-03 and "
              "handoff/capsule/RECOVERY-560.13.md. The bytes are deliberately NOT committed "
              "(118 MB); the manifest records the hash and the live fetch recipe.",
        extra=r13_extra,
    ))

    items.append(item(
        "pads.lfs_request",
        "The exact Git-LFS batch request body that proves DATA/560.13's object is deleted "
        "upstream (oid + size).",
        "liber-primus/analysis/round12/A1/lfs_req.json",
        "in-repo", ["written by Round 12 front A1"], [],
    ))

    items.append(item(
        "audio.761_instar_emergence",
        "The 2013 '761 / The Instar Emergence' MP3 -- 4,010,732 B of author-shipped bytes, also "
        "tried as a pad in Round 12 A1 (NEGATIVE).",
        "puzzles/2013/artifacts/761_The-Instar-Emergence.mp3",
        "in-repo",
        ["Cicada 3301 2013 puzzle round"],
        ["https://archive.org/download/3301.iso/3301.iso/AUDIO%2F761.MP3"],
    ))

    # ---------------------------------------------------------------- 6. corpora
    GUT = "https://www.gutenberg.org/files/{}"
    for fn, gid, title in [
        ("kjv.txt", "10/10-0.txt", "King James Bible (Gutenberg #10) -- archaic register, "
                                   "closest to LP's own"),
        ("moby.txt", "2701/2701-0.txt", "Moby-Dick (Gutenberg #2701)"),
        ("pride.txt", "1342/1342-0.txt", "Pride and Prejudice (Gutenberg #1342)"),
        ("war.txt", "2600/2600-0.txt", "War and Peace (Gutenberg #2600)"),
    ]:
        items.append(item(
            f"corpus.{fn.split('.')[0]}",
            f"{title}. One of the four texts the English quadgram scorer is built from.",
            f"liber-primus/data/{fn}",
            "gitignored-fetchable",
            ["Project Gutenberg, public domain",
             "recipe: liber-primus/data/BUILD-QUADGRAMS.md"],
            [GUT.format(gid),
             "https://www.gutenberg.org/ebooks/" + gid.split("/")[0],
             "https://gutenberg.pglaf.org/ (official mirror)",
             "https://aleph.gutenberg.org/ (official mirror)"],
            notes="WARNING: Gutenberg re-issues files (header/footer edits, -0.txt vs .txt vs "
                  "utf-8 variants). A refetch may NOT reproduce this SHA-256 even though the "
                  "book is the same. That is why english_quadgrams.txt is committed: the "
                  "DERIVED model is the reproducible artifact, not the raw corpus.",
        ))

    items.append(item(
        "corpus.english_quadgrams",
        "THE SCORER. Committed English quadgram counts derived from the four corpora above. "
        "Every score in this repo (-4.x = English band, -7.x = noise) comes from this file.",
        "liber-primus/data/english_quadgrams.txt",
        "in-repo",
        ["derived in-repo from corpus.kjv/moby/pride/war -- see data/BUILD-QUADGRAMS.md"],
        [],
        notes="This is the single most important committed derived artifact. If you rebuild it "
              "from a different corpus, every numeric threshold in this repo shifts and the "
              "repo's pre-registered bars stop being comparable. Prefer the committed file.",
    ))

    # ---------------------------------------------------------------- 7. candidate keytexts
    for fn, title, gid, mirrors in [
        ("mabinogion.txt", "The Mabinogion, tr. Lady Charlotte Guest", "5160",
         ["https://www.gutenberg.org/ebooks/5160"]),
        ("king_in_yellow.txt", "The King in Yellow, R. W. Chambers", "8492",
         ["https://www.gutenberg.org/ebooks/8492"]),
        ("self_reliance.txt", "Self-Reliance, R. W. Emerson", None,
         ["https://www.gutenberg.org/ebooks/16643",
          "https://en.wikisource.org/wiki/Essays:_First_Series/Self-Reliance"]),
        ("book_of_the_law.txt", "Liber AL vel Legis (The Book of the Law), Crowley 1909", None,
         ["https://en.wikisource.org/wiki/The_Book_of_the_Law",
          "https://sacred-texts.com/oto/engccxx.htm"]),
        ("agrippa.txt", "Agrippa (A Book of the Dead), William Gibson 1992", None,
         ["https://www.williamgibsonbooks.com/source/agrippa.asp",
          "https://web.archive.org/web/*/williamgibsonbooks.com/source/agrippa.asp"]),
    ]:
        items.append(item(
            f"keytext.{fn.split('.')[0]}",
            f"Candidate running-key text: {title}. Part of the ~200-text exhaustion sweep "
            "(Round 7 / Campaigns XII-XIII). All null.",
            f"liber-primus/data/keys/{fn}",
            "gitignored-fetchable",
            [f"Project Gutenberg #{gid}" if gid else "public-domain text; exact edition NOT "
             "recorded by this repo"],
            mirrors,
            provenance_confidence="documented" if gid else "reconstructed-from-content",
            notes="HONESTY NOTE: this repo has no fetch script for data/keys/*.txt, so the exact "
                  "edition/URL was never recorded. The provenance above is reconstructed from "
                  "the file's own opening lines. A refetch will very likely differ in bytes "
                  "(headers/whitespace) while being the same work. For keytext sweeps that is "
                  "usually harmless -- the scorer strips to A-Z -- but it means these SHA-256s "
                  "are a record of WHAT WAS TESTED, not a reproducible fetch target.",
        ))

    items.append(item(
        "keytext.runepoem_oe",
        "The Old English Rune Poem (and its transliteration) -- the highest-prior thematic "
        "keytext for a runic cipher.",
        "liber-primus/data/keys/runepoem_oe.txt",
        "in-repo", ["in-repo"], [],
    ))
    items.append(item(
        "keytext.runepoem_translit",
        "Transliterated Old English Rune Poem.",
        "liber-primus/data/keys/runepoem_translit.txt",
        "in-repo", ["in-repo"], [],
    ))

    # ---------------------------------------------------------------- 8. transcription sources
    RTKD = ("https://raw.githubusercontent.com/rtkd/iddqd/master/"
            "liber-primus__transcription--master/liber-primus__transcription--master.txt")
    items.append(item(
        "transcription.rtkd_master",
        "rtkd/iddqd 2017 community-root transcription -- the lineage root of runes.canonical.",
        "liber-primus/data/sources/rtkd_master.txt",
        "gitignored-fetchable",
        ["rtkd/iddqd GitHub repository, 2017"],
        [RTKD, "https://github.com/rtkd/iddqd"],
        notes="Fetch: python3 liber-primus/data/fetch_sources.py",
    ))
    RELIKD = "https://raw.githubusercontent.com/relikd/LiberPrayground/master/pages/"
    for c in ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32",
              "p33-39", "p40-53", "p54-55", "p56_an_end", "p57_parable"]:
        items.append(item(
            f"transcription.relikd_{c}",
            f"relikd/LiberPrayground per-page transcription chunk {c} -- the second lineage, "
            "used for cross-verification.",
            f"liber-primus/data/sources/relikd_{c}.txt",
            "gitignored-fetchable",
            ["relikd/LiberPrayground GitHub repository"],
            [RELIKD + c + ".txt", "https://github.com/relikd/LiberPrayground"],
            notes="Fetch: python3 liber-primus/data/fetch_sources.py",
        ))

    # ---------------------------------------------------------------- 9. method artifacts
    items.append(item(
        "method.skipdecode",
        "The skip-aware (anti-repeat / desync-tolerant) beam decoder. The ONLY decoder that "
        "survives LP2's engineered doublet filter; every post-Campaign-XVIII result uses it.",
        "liber-primus/analysis/campaign18_skip/skipdecode.py",
        "in-repo", ["in-repo, Campaign XVIII"], [],
        notes="A rigid decoder scores the CORRECT key as noise (~-6.8) on filtered ciphertext. "
              "If you attack LP2 with a rigid decoder you will produce a false negative. This "
              "is the single most-repeated mistake in this problem.",
    ))
    items.append(item(
        "method.lib_numchannel",
        "Shared data/null/scorer harness: nc.unsolved(), nc.segments(), nc.shuffled (seed 3301), "
        "nc.eng_norm. Defines the null model every pre-registered bar is measured against.",
        "liber-primus/analysis/round11/lib_numchannel.py",
        "in-repo", ["in-repo, Round 11"], [],
    ))
    items.append(item(
        "method.nullcurve",
        "Gumbel best-of-N null-growth model for the seed sweep; derives the scale-corrected "
        "family-wise thresholds that replace the invalid pre-registered -12.5.",
        "liber-primus/analysis/round10/L5-seed32/nullcurve.py",
        "in-repo", ["in-repo, Round 10 lane L5"], [],
        notes="Run it before resuming the 32-bit sweep. See handoff/PARKED.md P-01.",
    ))

    return items


def main():
    items = build()
    counts = {}
    for it in items:
        counts[it["status"]] = counts.get(it["status"], 0) + 1
    verified = sum(1 for it in items if it.get("hash_verified_locally"))
    sha1_checked = [it for it in items if "published_sha1_match" in it]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "liber-primus/handoff/capsule/build_manifest.py",
        "repo_root_relative_paths": True,
        "trust_anchor": {
            "command": "python3 liber-primus/tests/validate.py",
            "must_print": "ALL VALIDATIONS PASSED",
            "why": "reproduces all 5 solved LP2 pages from runes.canonical through this repo's "
                   "cipher rig; nothing else in the capsule is trustworthy if this fails",
        },
        "status_vocabulary": {
            "in-repo": "committed; a fresh clone has the bytes",
            "gitignored-fetchable": "not committed; the mirrors below reproduce it",
            "derived": "computed from another capsule item by a script in this repo",
            "LOST": "authoritative bytes not retrievable from any known source",
            "RECOVERED": "was LOST in a prior round; this capsule re-established a live source",
        },
        "summary": {
            "n_items": len(items),
            "by_status": counts,
            "hash_verified_locally": verified,
            "published_sha1_cross_checked": len(sha1_checked),
            "published_sha1_matches": sum(1 for it in sha1_checked
                                          if it.get("published_sha1_match")),
        },
        "items": items,
    }
    out = os.path.join(HERE, "MANIFEST.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {out}")
    print(f"  items                 : {len(items)}")
    for k in sorted(counts):
        print(f"  {k:22s}: {counts[k]}")
    print(f"  hashed locally        : {verified}")
    print(f"  sha1 cross-checked    : {len(sha1_checked)} "
          f"(matching: {manifest['summary']['published_sha1_matches']})")


if __name__ == "__main__":
    main()
