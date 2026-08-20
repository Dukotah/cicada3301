#!/usr/bin/env python3
"""Align the henkman/liberprimus (2016) transcription against canon, page by page.

henkman/liberprimus was created 2016-08-14 -- BEFORE the 2017 rtkd/iddqd root that
every lineage this repository holds descends from. It uses its own page markers
('----- N -----') and its own codepoint convention. It disagrees with canon.

This script produces an honest, mechanical edit script: for every page, the
difflib opcodes turning the henkman rune string into the canon rune string, with
the transliterations of both sides so a human can adjudicate against the images.

Writes corpus/B-liber-primus/CONFLICT-henkman-2016.json.
Run: PYTHONUTF8=1 python corpus/B-liber-primus/align_henkman.py
"""
import os
import re
import sys
import json
import difflib
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "liber-primus", "src"))
from lp import gematria as gp   # noqa: E402

SRC = os.path.join(HERE, "fetched", "henkman__liberprimus", "liberprimus.txt")
OUT = os.path.join(HERE, "CONFLICT-henkman-2016.json")
ALIAS = {"ᛂ": "ᛄ"}          # henkman writes GER (J) as U+16C2, canon uses U+16C4
PAGE_RE = re.compile(r"^-{3,}\s*(\d+)\s*-{3,}\s*$")


def runes_of(t):
    return "".join(ALIAS.get(c, c) for c in t if ALIAS.get(c, c) in gp.RUNE_TO_IDX)


def tr(s):
    return "".join(gp.RUNE_TO_TRANS[c] for c in s)


def henkman_pages():
    pages, cur, num = {}, [], None
    for ln in open(SRC, encoding="utf-8").read().splitlines():
        m = PAGE_RE.match(ln.strip())
        if m:
            if num is not None:
                pages[num] = "\n".join(cur)
            num, cur = int(m.group(1)), []
        elif num is not None:
            cur.append(ln)
    if num is not None:
        pages[num] = "\n".join(cur)
    return pages


def main():
    canon = json.load(open(os.path.join(HERE, "PAGES.json"), encoding="utf-8"))
    canon_pages = {p["page_index"]: p["runes"] for p in canon["pages"]}
    hp = henkman_pages()

    rows, tot_edits, tot_runes = [], 0, 0
    for pn in sorted(hp):
        h = runes_of(hp[pn])
        c = canon_pages.get(pn, "")
        tot_runes += len(h)
        sm = difflib.SequenceMatcher(a=h, b=c, autojunk=False)
        ops = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            ops.append({
                "op": tag,
                "henkman_span": [i1, i2],
                "canon_span": [j1, j2],
                "henkman_runes": h[i1:i2],
                "canon_runes": c[j1:j2],
                "henkman_translit": tr(h[i1:i2]),
                "canon_translit": tr(c[j1:j2]),
                "henkman_context": tr(h[max(0, i1 - 8):i2 + 8]),
                "canon_context": tr(c[max(0, j1 - 8):j2 + 8]),
            })
        tot_edits += len(ops)
        rows.append({
            "page_index": pn,
            "henkman_n_runes": len(h),
            "canon_n_runes": len(c),
            "identical": h == c,
            "similarity_ratio": round(sm.ratio(), 6),
            "n_edit_blocks": len(ops),
            "n_runes_differing": sum(max(o["henkman_span"][1] - o["henkman_span"][0],
                                         o["canon_span"][1] - o["canon_span"][0]) for o in ops),
            "edits": ops,
        })

    ident = [r for r in rows if r["identical"]]
    data = {
        "$comment": ("A genuinely DIVERGENT Liber Primus transcription. Recorded, NOT adjudicated. "
                     "Both readings are preserved; deciding which is right requires the page images."),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "generator": "corpus/B-liber-primus/align_henkman.py",
        "candidate": {
            "name": "henkman/liberprimus",
            "source_url": "https://raw.githubusercontent.com/henkman/liberprimus/master/liberprimus.txt",
            "repo_created_utc": "2016-08-14T15:58:10Z",
            "why_it_matters": ("Created 2016-08, before the 2017 rtkd/iddqd transcription that "
                               "krisyotam, relikd and rtkd all descend from. Its page markers, "
                               "line breaks and codepoint convention are its own."),
            "independence": "NOT ESTABLISHED - the repo carries no provenance statement. Treat as a candidate.",
            "sha256_of_file": hashlib.sha256(open(SRC, "rb").read()).hexdigest(),
        },
        "normalisation": {"ᛂ (U+16C2)": "ᛄ (U+16C4) - the GER/J rune; a codepoint convention, not a reading"},
        "summary": {
            "henkman_pages": len(rows),
            "henkman_total_runes": tot_runes,
            "canon_total_runes_same_pages": sum(r["canon_n_runes"] for r in rows),
            "pages_identical_to_canon": len(ident),
            "pages_identical_list": [r["page_index"] for r in ident],
            "pages_diverging": len(rows) - len(ident),
            "total_edit_blocks": tot_edits,
        },
        "pages": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("henkman pages          : %d" % len(rows))
    print("henkman runes          : %d   (canon, same pages: %d)"
          % (tot_runes, sum(r["canon_n_runes"] for r in rows)))
    print("pages identical to canon: %d / %d" % (len(ident), len(rows)))
    print("total edit blocks      : %d" % tot_edits)
    print("")
    print("%-6s %8s %8s %8s %6s  %s" % ("page", "henkman", "canon", "edits", "ratio", "verdict"))
    for r in rows:
        print("%-6d %8d %8d %8d %6.3f  %s"
              % (r["page_index"], r["henkman_n_runes"], r["canon_n_runes"],
                 r["n_edit_blocks"], r["similarity_ratio"],
                 "IDENTICAL" if r["identical"] else "DIVERGES"))
    print("")
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
