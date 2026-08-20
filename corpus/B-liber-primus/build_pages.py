#!/usr/bin/env python3
"""Build corpus/B-liber-primus/PAGES.json - the definitive page-by-page LP dataset.

EVERYTHING here is DERIVED BY RUNNING CODE against the canonical in-repo data.
Nothing is hand-transcribed.

Sources (all in-repo, all provenance-pinned):
  liber-primus/data/krisyotam_runes.txt        canonical rune stream, 57 '%'-segments
  liber-primus/data/sources/relikd_*.txt       same stream re-split into onion7 page slots
  liber-primus/data/relikd/pN.jpg              400-DPI renders, SHA-1 == archived onion7 dump
  liber-primus/analysis/stego/provenance.json  the 56/56 SHA-1 verification
  liber-primus/data/scream314_lp.md            LP1 pages incl. the 5 solved ones
  liber-primus/src/lp/gematria.py              Gematria Primus

Run: PYTHONUTF8=1 python corpus/B-liber-primus/build_pages.py
"""
import os
import sys
import re
import json
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis"))
from lp import gematria as gp                    # noqa: E402
from lp import corpus as lpcorpus                # noqa: E402

SRC = os.path.join(LP, "data", "sources")
IMGD = os.path.join(LP, "data", "relikd")
KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")
OUT = os.path.join(HERE, "PAGES.json")

# separator glyphs used by the relikd transcription
WORD_SEP = "•"   # bullet          word break
SENT_SEP = "⁘"   # four dot punct  sentence / stanza end
SECT_SEP = "⁜"   # dotted cross    section end
PARA_SEP = "⁚"   # two dot punct   paragraph mark


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha1_file(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def runes_only(t):
    return "".join(c for c in t if c in gp.RUNE_TO_IDX)


# ---------------------------------------------------------------- relikd split
# Each relikd file is a run of blank-line-separated page blocks. The filename
# gives the inclusive onion7 page range it covers. Page 50 carries NO runes
# (it is a pure 13x8 base-60 token table) so it produces no block; we insert an
# explicit runeless record for it.
RELIKD_FILES = [
    ("relikd_p0-2.txt", 0, 2),
    ("relikd_p3-7.txt", 3, 7),
    ("relikd_p8-14.txt", 8, 14),
    ("relikd_p15-22.txt", 15, 22),
    ("relikd_p23-26.txt", 23, 26),
    ("relikd_p27-32.txt", 27, 32),
    ("relikd_p33-39.txt", 33, 39),
    ("relikd_p40-53.txt", 40, 53),
    ("relikd_p54-55.txt", 54, 55),
    ("relikd_p56_an_end.txt", 56, 56),
    ("relikd_p57_parable.txt", 57, 57),
]
RUNELESS_PAGES = {50}


def relikd_pages(page_lengths):
    """Return {page_number: raw block text (separators intact)} for every runic page.

    The relikd files bundle several onion7 pages each, and blank lines inside a
    file mark stanza breaks as well as page breaks, so blank-line splitting
    over-segments (e.g. relikd_p3-7.txt yields 7 blocks for 5 pages). Instead we
    cut each file's character stream at the rune counts the canonical krisyotam
    segmentation gives for the pages that file covers - a derivation, not a guess.
    Non-rune characters that trail a completed page (a section mark, a newline)
    stay with that page; the cut only advances when the next RUNE arrives.
    """
    out = {}
    for fn, lo, hi in RELIKD_FILES:
        txt = open(os.path.join(SRC, fn), encoding="utf-8").read()
        want = [p for p in range(lo, hi + 1) if p not in RUNELESS_PAGES]
        need = [page_lengths[p] for p in want]
        if sum(need) != len(runes_only(txt)):
            raise SystemExit("%s: %d runes on disk, %d expected for pages %s"
                             % (fn, len(runes_only(txt)), sum(need), want))
        buf, k, n = [], 0, 0
        for ch in txt:
            is_rune = ch in gp.RUNE_TO_IDX
            if is_rune and n >= need[k] and k + 1 < len(want):
                out[want[k]] = "".join(buf).strip()
                buf, k, n = [], k + 1, 0
            buf.append(ch)
            if is_rune:
                n += 1
        out[want[k]] = "".join(buf).strip()
        for p in want:
            if len(runes_only(out[p])) != page_lengths[p]:
                raise SystemExit("%s: page %d cut to %d runes, expected %d"
                                 % (fn, p, len(runes_only(out[p])), page_lengths[p]))
    return out


def kris_segments():
    """The canonical rune stream, as the rig itself loads it (57 segments)."""
    segs = [s for s in open(KRIS, encoding="utf-8").read().split("%")]
    return [runes_only(s) for s in segs if runes_only(s)]


def boundaries(block):
    """Structure of a page in RUNE-OFFSET coordinates (0-based; an offset is the
    number of runes that precede the marker within the page)."""
    n = 0
    words, sents, sects, paras, lines = [], [], [], [], []
    for ch in block:
        if ch in gp.RUNE_TO_IDX:
            n += 1
        elif ch == WORD_SEP:
            words.append(n)
        elif ch == SENT_SEP:
            sents.append(n)
        elif ch == SECT_SEP:
            sects.append(n)
        elif ch == PARA_SEP:
            paras.append(n)
        elif ch == "\n":
            lines.append(n)
    cuts = sorted(set(words + sents + sects + paras + [0, n]))
    wlens = [b - a for a, b in zip(cuts, cuts[1:]) if b - a > 0]
    return {
        "word_break_offsets": words,
        "sentence_end_offsets": sents,
        "section_end_offsets": sects,
        "paragraph_mark_offsets": paras,
        "line_break_offsets": lines,
        "n_words": len(wlens),
        "word_lengths": wlens,
    }


# ------------------------------------------------------------- solved metadata
LP2_SOLVED = {
    56: {"title": "AN END",
         "method": "prime-totient keystream (Vigenere mod 29 over phi(p) of the rune primes)",
         "key": "totients of the Gematria Primus primes, index-shifted",
         "reference": "liber-primus/analysis/round11/PHASE0-GATE.py"},
    57: {"title": "PARABLE",
         "method": "direct transliteration (plaintext runes, no cipher)",
         "key": None,
         "reference": "liber-primus/tests/test_rig.py"},
}
TOKEN_TABLE_PAGES = {   # Campaign VII, liber-primus/analysis/pp49_51/
    49: {"grid": "10x8", "n_tokens": 80},
    50: {"grid": "13x8", "n_tokens": 104},
    51: {"grid": "9x8", "n_tokens": 72},
}


def rec_for(page, block, seg_index, seg_runes, prov):
    runes = runes_only(block) if block is not None else ""
    idxs = [gp.RUNE_TO_IDX[c] for c in runes]
    img = os.path.join(IMGD, "p%d.jpg" % page)
    has_img = os.path.exists(img)
    solved = page in LP2_SOLVED
    r = {
        "page_index": page,
        "numbering_scheme": "onion7 / relikd LP2 page number (0-57)",
        "segment_index": seg_index,
        "image_file": ("liber-primus/data/relikd/p%d.jpg" % page) if has_img else None,
        "image_sha256": sha256_file(img) if has_img else None,
        "image_sha1": sha1_file(img) if has_img else None,
        "image_sha1_matches_archived_onion7_dump": prov.get(page),
        "n_runes": len(runes),
        "runes": runes,
        "rune_indices": idxs,
        "transliteration": "".join(gp.IDX_TO_TRANS[i] for i in idxs),
        "prime_indices": [gp.PRIMES[i] for i in idxs],
        "n_interrupters": idxs.count(0),
        "status": "solved" if solved else ("no-runes" if not runes else "unsolved"),
        "method": LP2_SOLVED.get(page, {}).get("method"),
        "key": LP2_SOLVED.get(page, {}).get("key"),
        "title": LP2_SOLVED.get(page, {}).get("title"),
        "segment_boundaries": boundaries(block) if block is not None else None,
        "source_lineage": ("relikd (rtkd/iddqd 2017 root) - rune-identical to krisyotam and rtkd"
                           if runes else "no runic content"),
        "sha256_of_rune_string": sha256_text(runes) if runes else None,
    }
    if page in TOKEN_TABLE_PAGES:
        r["token_table"] = dict(
            TOKEN_TABLE_PAGES[page],
            note="two-character base-60 tokens; NOT part of the rune stream",
            reference="liber-primus/analysis/pp49_51/CAMPAIGN-VII-FINDINGS.md")
    if seg_runes is not None:
        r["matches_krisyotam_segment"] = (seg_runes == runes)
    return r


def lp1_records():
    """The five SOLVED LP1 pages, from the scream314 transcription."""
    meta = json.load(open(os.path.join(LP, "SOLVED-PAGES.json"), encoding="utf-8"))
    out = []
    for m in meta["pages"]:
        # same substring lookup tests/validate.py uses ('14.jpg' -> '14.jpg - 107.jpg')
        p = lpcorpus.page_by_label(m["page_label"])
        if p is None or not p["runes"]:
            raise SystemExit("LP1 page %s not found in scream314" % m["page_label"])
        runes = runes_only(p["runes"])
        if len(runes) != m["n_runes"]:
            raise SystemExit("LP1 %s: %d runes parsed, SOLVED-PAGES.json says %d"
                             % (m["page_label"], len(runes), m["n_runes"]))
        idxs = [gp.RUNE_TO_IDX[c] for c in runes]
        slug = re.sub(r"[^0-9A-Za-z]+", "_", m["page_label"]).strip("_").lower()
        out.append({
            "page_label": m["page_label"],
            "scream314_header": p["label"],
            "numbering_scheme": ("scream314 LP1 label; NOT in the 0-57 LP2 range"),
            "title": m["title"],
            "n_runes": len(runes),
            "runes": runes,
            "rune_indices": idxs,
            "transliteration": "".join(gp.IDX_TO_TRANS[i] for i in idxs),
            "prime_indices": [gp.PRIMES[i] for i in idxs],
            "n_interrupters": idxs.count(0),
            "n_interrupters_used_by_solve": m["n_interrupters"],
            "status": "solved",
            "method": m["method"],
            "key": m["key"],
            "plaintext_transliteration": m["plaintext_transliteration"],
            "segment_boundaries": boundaries(p["runes"]),
            "source_lineage": "scream314 (rtkd/iddqd 2017 root)",
            "sha256_of_rune_string": sha256_text(runes),
            "reproduce_script": "analysis/reproduce/reproduce_page_%s.py" % slug,
            "transcription_conflicts": (["C-04"] if m["page_label"] == "06.jpg" else []),
        })
    return out



def conflicts_block():
    """Recorded transcription disagreements. BOTH readings are kept. Where a page
    is solved the conflict has been adjudicated by decryption; that verdict is
    stated, but neither reading is deleted. Full detail: CONFLICTS-B.md."""
    return [
        {
            "id": "C-04",
            "where": "LP1 page 06.jpg, rune offsets 142 and 279",
            "reading_a": {"source": "liber-primus/data/scream314_lp.md",
                          "runes": "ᚹᛋ", "translit": "W S", "n_runes": 2},
            "reading_b": {"source": "liber-primus/data/sources/rtkd_master.txt; "
                                    "r4nd0mD3v3l0p3r/LiberPrimusSolver data/firstKoan.txt",
                          "runes": "ᛠ", "translit": "EA", "n_runes": 1},
            "adjudication": ("Decrypting the page (atbash + Caesar shift 3) makes reading B give the "
                             "koan's actual refrain THAT IS NOT WHO YOU ARE / THAT IS WHAT YOU DO NOT "
                             "WHO YOU ARE. Reading A gives the self-contradictory NOT WHAT YOU ARE. "
                             "Reading B (EA) is correct; scream314 is in error."),
            "impact": ("This repository's SOLVED-PAGES.json plaintext for 06.jpg and the words "
                       "tests/validate.py checks are derived from reading A. LP1 only - the 12,956-rune "
                       "unsolved LP2 stream is NOT affected."),
            "status": "recorded, adjudicated, NOT silently fixed",
        },
        {
            "id": "C-06",
            "where": "LP2 pages 0, 3, 6, 19, 26, 33, 35, 39, 56",
            "reading_a": {"source": "canon (krisyotam / relikd / rtkd)"},
            "reading_b": {"source": "henkman/liberprimus, repo created 2016-08-14",
                          "n_runes_total": 13072},
            "adjudication": (
                "ALL FOUR substantive glyph conflicts are now DECIDED, and all four go to canon. "
                "(1) page 56 rune 19: canon ᛉ (X) decrypts to THERE EXISTS A PAGE, henkman ᛚ (L) "
                "to HERE EXISTS A PAGE - the published plaintext is THERE. "
                "(2) page 33 rune 100 and (3) page 33 rune 117: the SHA-1-pinned 400-DPI onion7 "
                "render shows ᛒ (two stacked triangles), not ᚹ (one small triangle); page 33 "
                "line 7 carries a genuine ᚹ two runes away for scale-matched contrast. "
                "(4) page 35: both transcriptions have 271 runes, so it is a transposition, not "
                "an insertion - the image line reads ᚣᛏᛝᛡᚩᛒ, i.e. canon. "
                "The remaining 9 edit blocks are bulk deletes (canon has runs henkman lacks), the "
                "signature of dropped lines. henkman is a copy of the resvolver/c1cada 2015-01-23 "
                "draft with ONE rune changed, so it is not an independent witness at all - see "
                "corpus/B-liber-primus/LINEAGE-2015.json."),
            "detail": ("corpus/B-liber-primus/CONFLICT-henkman-2016.json (full difflib edit "
                       "script); ADJUDICATION-page56.md; ADJUDICATION-pages33-35-images.md"),
            "status": "recorded and fully adjudicated - canon 4/4",
        },
        {
            "id": "C-07",
            "where": "whole book, vs rtkd_master.txt",
            "reading_a": {"source": "liber-primus/data/sources/rtkd_master.txt", "n_runes": 15933},
            "reading_b": {"source": "aautcsh/idkfa assets/liber-primus-translation.txt, "
                                    "repo created 2016-01-17", "n_runes": 15938},
            "adjudication": ("9 edit blocks. On the solved PARABLE page canon reads ᚣ (Y) giving "
                             "DIUINITY and the candidate reads ᛖ (E) giving DIUINITE - canon is "
                             "correct. Four of the nine are lone ᚠ (F) runes at page boundaries, "
                             "i.e. a separator convention rather than a reading."),
            "status": "recorded, partially adjudicated",
        },
    ]


def main():
    prov_rows = json.load(open(os.path.join(LP, "analysis", "stego", "provenance.json"),
                               encoding="utf-8"))["rows"]
    prov = {r["page"]: r["match"] for r in prov_rows}

    segs = kris_segments()

    def seg_of(page):
        if page < 50:
            return page
        if page == 50:
            return None
        return page - 1

    page_lengths = {p: (0 if p == 50 else len(segs[seg_of(p)])) for p in range(58)}
    rel = relikd_pages(page_lengths)

    pages = []
    for p in range(0, 58):
        si = seg_of(p)
        pages.append(rec_for(p, rel.get(p), si, segs[si] if si is not None else None, prov))

    # ---------------- validation, hard gates ----------------
    total = sum(r["n_runes"] for r in pages)
    unsolved_by_page = sum(r["n_runes"] for r in pages if 0 <= r["page_index"] <= 55)
    unsolved_by_seg = sum(len(s) for s in segs[:55])
    assert len(segs) == 57, len(segs)
    assert sum(len(s) for s in segs) == 13136
    assert total == 13136, total
    assert unsolved_by_page == 12956, unsolved_by_page
    assert unsolved_by_seg == 12956, unsolved_by_seg
    mism = [r["page_index"] for r in pages if r.get("matches_krisyotam_segment") is False]
    assert not mism, "relikd/krisyotam rune mismatch on pages %s" % mism
    flat = [i for s in segs[:55] for i in gp.runes_to_indices(s)]
    ident = sha256_text(",".join(str(i) for i in flat))
    pinned = json.load(open(os.path.join(LP, "PROBLEM.json"), encoding="utf-8")
                       )["ciphertext_identity"]["sha256_of_comma_joined_indices"]
    assert ident == pinned, "%s != %s" % (ident, pinned)

    lp1 = lp1_records()

    data = {
        "$schema_note": "Lane B deliverable. Built by corpus/B-liber-primus/build_pages.py. Do not hand-edit.",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "generator": "corpus/B-liber-primus/build_pages.py",
        "numbering": {
            "lp2_pages": "0-57 (onion7 / relikd file numbers). This is the scheme used by page_index.",
            "lp2_unsolved": "pages 0-55 (page 50 carries no runes) = 12,956 runes",
            "lp2_solved": "page 56 = AN END, page 57 = PARABLE",
            "krisyotam_segments": ("0-56, 57 non-empty '%'-separated segments. seg 0-49 == page 0-49; "
                                   "page 50 has no segment (runeless); seg 50-56 == page 51-57."),
            "lp1": ("Liber Primus part 1 pages carry scream314 labels ('Runes - 01.jpg', '03.jpg', ...) "
                    "and are NOT in the 0-57 range. Listed separately under lp1_solved_pages."),
            "warning": ("Sources in the wild use at least three numbering schemes for the same pages. "
                        "See CONFLICTS-B.md C-01/C-02/C-03."),
        },
        "identity": {
            "n_runes_total_lp2": total,
            "n_runes_unsolved_lp2": unsolved_by_page,
            "n_pages_lp2": len(pages),
            "n_krisyotam_segments": len(segs),
            "sha256_of_comma_joined_unsolved_indices": ident,
            "matches_PROBLEM_json": ident == pinned,
        },
        "gematria_primus": [{"index": i, "rune": r, "transliteration": t, "prime": p}
                            for (i, r, t, p) in gp.GEMATRIA],
        "interrupter": {"rune": gp.INTERRUPTER, "index": 0, "transliteration": "F",
                        "note": ("On solved pages this rune sometimes acts as a skip marker. "
                                 "n_interrupters counts literal occurrences, not confirmed skips.")},
        "separators": {
            WORD_SEP: "word break", SENT_SEP: "sentence/stanza end",
            SECT_SEP: "section end", PARA_SEP: "paragraph mark",
        },
        "transcription_conflicts": conflicts_block(),
        "pages": pages,
        "lp1_solved_pages": lp1,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("OK  %s" % OUT)
    print("    LP2 pages: %d   runes: %d   unsolved: %d" % (len(pages), total, unsolved_by_page))
    print("    krisyotam segments: %d  seg 0-54 sum: %d" % (len(segs), unsolved_by_seg))
    print("    identity sha256 matches PROBLEM.json: %s" % (ident == pinned))
    print("    LP1 solved pages: %d  runes: %d" % (len(lp1), sum(r["n_runes"] for r in lp1)))
    nimg = sum(1 for r in pages if r["image_file"])
    allok = all(r["image_sha1_matches_archived_onion7_dump"] for r in pages if r["image_file"])
    print("    images attached: %d/58  all sha1-verified: %s" % (nimg, allok))


if __name__ == "__main__":
    main()
