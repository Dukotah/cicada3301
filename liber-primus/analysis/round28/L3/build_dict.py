#!/usr/bin/env python3
"""Round 28 / L3 — dictionary builder (PREREG Q3 + amendment A1-A3).

Emits dictionary.jsonl: one JSON row per DEDUPLICATED-BY-64-BIT-HASH-IMAGE candidate
string, ordered tier 0 (corpus priority) first, then tier 1 (full English wordlist),
then tier 1b (wordlist UPPER) / 1c (wordlist Title). Dedup key = the amd64 Py2.7
hash image  n = py2_str_hash(s, 64) & (2^64-1)  — strings that collapse to the same
image produce the same MT state, so only the first is kept (collision count reported).

Sources (all in-repo, no network):
  tier 0: B-04 2,165-entry dictionary (analysis/round13/B04/seeds.py) + case/space
          variants; R26-C 31 str seeds + variants; words_expanded.txt; solved-
          plaintext words/bigrams/trigrams; thematic.txt; Cicada dates 2011-2014 in
          8 spellings; number strings 0..9999 + primes<10k + notable constants;
          onion/keyid strings.
  tier 1: corpus/E-tooling/vendor/cicada-solvers__libergo/words.txt (390,306 words,
          sha256 0ae20e6f... pinned in PREREG amendment A2), as-is (lowercase).
  tier 1b/1c: UPPER / Title variants of tier 1.
"""
import datetime as _dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(LP, ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round13", "B04"))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "G3"))

import seeds as B04  # noqa
from gen_py27 import py2_str_hash  # noqa

MASK64 = (1 << 64) - 1
WORDLIST = os.path.join(REPO, "corpus", "E-tooling", "vendor",
                        "cicada-solvers__libergo", "words.txt")

MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY",
          "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]


def _variants(s):
    """Case/spacing variants of a printable string. Bounded (<=8 per input)."""
    out = {s}
    if any(c.isalpha() for c in s):
        out |= {s.lower(), s.upper(), s.title()}
        if " " in s:
            out |= {s.replace(" ", ""), s.replace(" ", "_"), s.replace(" ", "-")}
    return out


def _words_of(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    ws = [w for w in "".join(c if c.isalnum() else " " for c in txt).split() if w]
    return ws


def tier0():
    cand = []  # (label, string)

    # 1. B-04 dictionary (2,165) — bytes, latin-1 preserves 1 byte == 1 char
    for label, b in B04.build():
        s = b.decode("latin-1")
        cand.append(("b04:" + label, s))
        if s.isprintable() and any(c.isalpha() for c in s) and len(s) <= 64:
            for v in _variants(s):
                cand.append(("b04v:" + label, v))

    # 2. R26-C 31 string seeds + variants (base strings get EXCLUDED per-cell later
    #    by hash image; variants are new ground)
    z = json.load(open(os.path.join(LP, "analysis", "round26", "C", "seeds.json")))
    for e in z["seeds"]:
        v = e.get("value")
        if isinstance(v, str):
            cand.append(("r26c", v))
            for w in _variants(v):
                cand.append(("r26cv", w))

    # 3. words_expanded.txt (567 curated)
    for w in _words_of(os.path.join(LP, "data", "keys", "words_expanded.txt")):
        for v in _variants(w):
            cand.append(("wexp", v))

    # 4. solved plaintext words + consecutive bigrams/trigrams (spaced, UPPER)
    ws = [w.upper() for w in _words_of(os.path.join(LP, "data", "keys", "solved_plaintext.txt"))]
    for w in set(ws):
        for v in _variants(w):
            cand.append(("solved1", v))
    for n in (2, 3):
        for i in range(len(ws) - n + 1):
            g = " ".join(ws[i:i + n])
            cand.append(("solved%d" % n, g))
            cand.append(("solved%d" % n, g.lower()))
            cand.append(("solved%d" % n, g.replace(" ", "")))

    # 5. thematic.txt lines + words
    tpath = os.path.join(LP, "data", "keys", "thematic.txt")
    for line in open(tpath, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if line:
            for v in _variants(line):
                cand.append(("thematic", v))
    for w in _words_of(tpath):
        for v in _variants(w):
            cand.append(("thematicw", v))

    # 6. dates 2011-2014, 8 spellings
    d = _dt.date(2011, 1, 1)
    while d <= _dt.date(2014, 12, 31):
        y, m, dd = d.year, d.month, d.day
        mon = MONTHS[m - 1]
        forms = ["%04d-%02d-%02d" % (y, m, dd), "%02d/%02d/%04d" % (m, dd, y),
                 "%02d/%02d/%04d" % (dd, m, y), "%04d%02d%02d" % (y, m, dd),
                 "%02d.%02d.%04d" % (dd, m, y), "%s %d %d" % (mon, dd, y),
                 "%d %s %d" % (dd, mon, y), "%s %d, %d" % (mon.title(), dd, y)]
        for f in forms:
            cand.append(("date", f))
        d += _dt.timedelta(days=1)

    # 7. number strings: 0..9999, primes < 10000, notable constants
    for i in range(10000):
        cand.append(("num", str(i)))
    sieve = bytearray([1]) * 10000
    sieve[0:2] = b"\x00\x00"
    for i in range(2, 100):
        if sieve[i]:
            sieve[i * i::i] = b"\x00" * len(sieve[i * i::i])
    for i in range(10000):
        if sieve[i]:
            cand.append(("prime", str(i)))  # dedup handles overlap with num
    for c in ("3301", "1033", "509", "503", "761", "1595277641", "3299",
              "131071", "524287", "2147483647", "1387498126", "6567743570",
              "788169", "27191571", "36367763ab73783c9794473e0a1e2d5e",
              "7A35090F", "0x7A35090F", "7a35090f", "0x7a35090f"):
        cand.append(("const", c))

    # 8. onion / key-id strings (curated; several also live in B-04)
    for o in ("ky2khlqdf7qdznac", "ky2khlqdf7qdznac.onion", "cu343l33nqaekrnw",
              "cu343l33nqaekrnw.onion", "mvqpb27yoqcpxbdz", "mvqpb27yoqcpxbdz.onion",
              "dyxrz6crhpjcgkgt", "dyxrz6crhpjcgkgt.onion",
              "7A35090F", "6d854cd7933322a601c3286d", "emiratesnbd"):
        for v in _variants(o):
            cand.append(("onion", v))

    return cand


def main():
    rows = []
    seen = {}
    n_coll = 0
    n_raw = 0

    def add(tier, label, s):
        nonlocal n_coll, n_raw
        n_raw += 1
        try:
            b = s.encode("latin-1")
        except UnicodeEncodeError:
            return  # a Py2 str literal is bytes; non-latin-1 is out of model
        if len(b) == 0 or len(b) > 256:
            return
        img = py2_str_hash(b, 64) & MASK64
        if img in seen:
            n_coll += 1
            return
        seen[img] = True
        rows.append({"t": tier, "l": label, "s": s, "img": img})

    for label, s in tier0():
        add(0, label, s)
    n_t0 = len(rows)

    wl = [w.strip() for w in open(WORDLIST, encoding="utf-8", errors="ignore") if w.strip()]
    for w in wl:
        add(1, "wl", w)
    n_t1 = len(rows) - n_t0
    for w in wl:
        add(2, "wlU", w.upper())
    n_t1b = len(rows) - n_t0 - n_t1
    for w in wl:
        add(3, "wlT", w.title())
    n_t1c = len(rows) - n_t0 - n_t1 - n_t1b

    with open(os.path.join(HERE, "dictionary.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # R26-C per-cell exclusion images (the 31 measured-ground strings, base form only)
    z = json.load(open(os.path.join(LP, "analysis", "round26", "C", "seeds.json")))
    excl = sorted({py2_str_hash(e["value"].encode("latin-1"), 64) & MASK64
                   for e in z["seeds"] if isinstance(e.get("value"), str)})

    meta = {"built": _dt.datetime.now().isoformat(timespec="seconds"),
            "raw_candidates": n_raw, "hash_image_collisions_dropped": n_coll,
            "deduplicated_total": len(rows),
            "tier0_corpus_priority": n_t0, "tier1_wordlist": n_t1,
            "tier1b_wordlist_upper": n_t1b, "tier1c_wordlist_title": n_t1c,
            "wordlist_path": WORDLIST,
            "wordlist_sha256": "0ae20e6fbc8029f2b21a80cf673359ec54903fc14dde3a89d0df64d53ba0c1a9",
            "r26c_exclusion_images_n": len(excl),
            "r26c_exclusion_images": excl}
    with open(os.path.join(HERE, "dict_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != "r26c_exclusion_images"}, indent=1))


if __name__ == "__main__":
    main()
