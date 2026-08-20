#!/usr/bin/env python3
"""Establish the 2015 origin of the canonical Liber Primus rune stream and
place henkman/liberprimus inside that lineage.

Reproduces, from files already in corpus/B-liber-primus/fetched/:
  * resvolver/c1cada `translation/liber_primus.rne` (committed 2015-01-23) is
    rune-for-rune IDENTICAL to canon, two years before rtkd/iddqd;
  * resvolver/c1cada `transcriptions.rne` (same day, the superseded draft) is
    13,072 runes and carries all 14 divergences from canon;
  * henkman/liberprimus (2016-08-14) is that draft with ONE rune changed --
    it is a copy, not an independent transcription;
  * Be5haram/CICADA2K16 `RuneSolver.py` (2016-01-14) embeds the canonical
    13,136-rune stream as a contiguous substring.

Writes LINEAGE-2015.json.  Run:
    PYTHONIOENCODING=utf-8 python corpus/B-liber-primus/lineage_2015.py
"""
import datetime
import difflib
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "liber-primus", "src"))
from lp import gematria as gp   # noqa: E402

FETCHED = os.path.join(HERE, "fetched")
ALIASES = {"ᛂ": "ᛄ", "ᛣ": "ᛞ", "ᚡ": "ᚠ"}

WITNESSES = [
    ("resvolver/c1cada", "translation/liber_primus.rne", "2015-01-23T17:56:18Z", "420a2f4d",
     os.path.join(FETCHED, "resvolver__c1cada", "translation", "liber_primus.rne")),
    ("resvolver/c1cada", "transcriptions.rne", "2015-01-23T17:56:18Z", "420a2f4d",
     os.path.join(FETCHED, "resvolver__c1cada", "transcriptions.rne")),
    ("resvolver/c1cada", "transcriptions.rne@42d33941", "2015-01-16T08:04:24Z", "42d33941",
     os.path.join(FETCHED, "resvolver__c1cada", "_history",
                  "transcriptions_42d33941_2015-01-16.rne")),
    ("Be5haram/CICADA2K16", "RuneSolver.py", "2016-01-14T21:52:08Z", "6ffa03c7",
     os.path.join(FETCHED, "Be5haram__CICADA2K16", "RuneSolver.py")),
    ("henkman/liberprimus", "liberprimus.txt", "2016-08-14T16:01:14Z", "8cc96656",
     os.path.join(FETCHED, "henkman__liberprimus", "liberprimus.txt")),
]


def runes(path):
    t = open(path, encoding="utf-8").read()
    t = "".join(ALIASES.get(c, c) for c in t)
    return "".join(c for c in t if c in gp.RUNE_TO_IDX)


def main():
    canon = runes(os.path.join(ROOT, "liber-primus", "data", "krisyotam_runes.txt"))
    csha = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    pages = json.load(open(os.path.join(HERE, "PAGES.json"), encoding="utf-8"))["pages"]
    starts, off = [], 0
    for p in pages:
        if p["n_runes"]:
            starts.append((p["page_index"], off, off + p["n_runes"]))
            off += p["n_runes"]

    def page_of(i):
        for pg, lo, hi in starts:
            if lo <= i < hi:
                return pg, i - lo
        return None, None

    out = {
        "$comment": ("The canonical Liber Primus rune stream is attested in a public "
                     "GitHub repository on 2015-01-23, two years before rtkd/iddqd "
                     "(2017-01-04), which prior work in this repo treated as the root. "
                     "henkman/liberprimus is a copy of a superseded 2015 draft, not an "
                     "independent transcription."),
        "generated_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "corpus/B-liber-primus/lineage_2015.py",
        "canon": {"n_runes": len(canon), "sha256_of_rune_string": csha,
                  "source": "liber-primus/data/krisyotam_runes.txt"},
        "codepoint_aliases_normalised": ALIASES,
        "witnesses": [],
    }

    for repo, path, date, sha, fp in WITNESSES:
        if not os.path.exists(fp):
            out["witnesses"].append({"repo": repo, "path": path, "status": "FILE NOT FETCHED"})
            continue
        r = runes(fp)
        rec = {
            "repo": repo, "path": path, "commit_date_utc": date, "commit": sha,
            "n_runes": len(r), "sha256_of_rune_string": hashlib.sha256(r.encode()).hexdigest(),
            "identical_to_canon": r == canon,
            "canon_is_contiguous_substring": canon in r,
        }
        if not rec["identical_to_canon"] and not rec["canon_is_contiguous_substring"]:
            sm = difflib.SequenceMatcher(None, canon, r, autojunk=False)
            ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
            rec["n_edit_blocks_vs_canon"] = len(ops)
            rec["edits_vs_canon"] = []
            for op, i1, i2, j1, j2 in ops:
                pg, col = page_of(i1 if i1 < len(canon) else len(canon) - 1)
                rec["edits_vs_canon"].append({
                    "op": op, "canon_span": [i1, i2], "candidate_span": [j1, j2],
                    "lp2_page": pg, "rune_index_in_page": col,
                    "canon_runes": canon[i1:i2], "candidate_runes": r[j1:j2],
                })
        out["witnesses"].append(rec)

    # henkman vs the 2015 draft
    draft = runes(os.path.join(FETCHED, "resvolver__c1cada", "transcriptions.rne"))
    henk = runes(os.path.join(FETCHED, "henkman__liberprimus", "liberprimus.txt"))
    sm = difflib.SequenceMatcher(None, draft, henk, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    out["henkman_vs_resvolver_2015_draft"] = {
        "n_runes_each": [len(draft), len(henk)],
        "n_edit_blocks": len(ops),
        "edits": [{"op": o[0], "draft_span": [o[1], o[2]], "henkman_span": [o[3], o[4]],
                   "draft_runes": draft[o[1]:o[2]], "henkman_runes": henk[o[3]:o[4]]}
                  for o in ops],
        "verdict": ("henkman/liberprimus is the resvolver 2015-01-23 draft with a single "
                    "rune changed. It is NOT an independent transcription."),
    }

    p = os.path.join(HERE, "LINEAGE-2015.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote %s" % p)
    for w in out["witnesses"]:
        print("  %-22s %-34s %s  %6s runes  %s" % (
            w["repo"], w["path"], w.get("commit_date_utc", "-"), w.get("n_runes", "-"),
            "== CANON" if w.get("identical_to_canon") else
            ("CANON is substring" if w.get("canon_is_contiguous_substring") else
             "%d edit blocks" % w.get("n_edit_blocks_vs_canon", -1))))
    print("  henkman vs 2015 draft: %d edit block(s)"
          % out["henkman_vs_resvolver_2015_draft"]["n_edit_blocks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
