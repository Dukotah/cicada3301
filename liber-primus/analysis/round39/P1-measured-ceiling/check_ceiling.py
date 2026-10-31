#!/usr/bin/env python3
"""Round 39 / P1 - machine check of MEASURED-CEILING.md against LEDGER.json.

Rule set (pre-registered in PREREG.md, dated before this file existed):
  1. every table line in sections 1-3 carries >=1 [[ROW-ID]] citation; every id exists in LEDGER.json;
  2. a section-2 line whose Verdict cell says "excluded at power" or "measured negative" may cite only rows whose
     positive_control is exactly "passed" (X1/R39: the P1 prefix rule was tightened; PC_ALLOW lists the one reasoned exception),
     whose coverage is non-empty, whose threshold_fixed_in_advance is not false unless the line says "post-data null",
     and, if the row's controls are register-narrow, whose line carries a "[plants: ...]" scope;
  3. every section-2 line has a Verdict from the controlled phrases, a non-empty measured-power cell, a conditionals
     cell with three " / "-separated parts, and a non-empty "Re-opens if" cell;
  4. every "<!-- pin: ROW-ID | substring -->" must occur in that row's JSON (numbers cannot drift);
  5. forbidden vocabulary (exhausted, exhaustion, closed, solved, dead, impossible) may appear only inside double
     quotes, backticks, '>' blockquote lines, fenced code or HTML comments.

Exit 0 = pass, 1 = any violation.   usage: python check_ceiling.py [path/to/MEASURED-CEILING.md]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DOC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(LP, "MEASURED-CEILING.md")
LEDGER = os.path.join(LP, "LEDGER.json")

STRONG = ("excluded at power", "measured negative")
WEAK = ("partial", "unmeasured", "inconclusive", "not excluded")
FORBIDDEN = re.compile(r"\b(exhausted|exhaustion|exhaustive\s+closure|closed|solved|dead|impossible|unsolvable|foreclosed|frontier\s+(?:is|are)\s+complete)\b", re.I)   # X1/R39: + R7's "unsolvable", "the frontier is complete"
# X1/R39: rows whose positive_control is not exactly "passed" but may still be cited on a strong line (reason recorded)
PC_ALLOW = {"R37-I1-FREE-NULL-LMATCHED": "cited only as the free-relation qualifier (OE 3/20, EN_HALFVOWEL 7/20 fail at L=240); not support for a negative"}
# X1/R39: a row whose adjudicator_register says the plants were English-only (or EN/LATIN/GREEK only) must be flagged on the line
NARROW_PLANTS = re.compile(r"(plants?|controls?)\s+(?:planted\s+)?EN_MODERN|EN_MODERN[- ]only|control EN_MODERN only", re.I)
CITE = re.compile(r"\[\[([^\[\]\s]+)\]\]")
PIN = re.compile(r"<!--\s*pin:\s*(\S+)\s*\|\s*(.*?)\s*-->")

errors, warns = [], []


def err(msg):
    errors.append(msg)


def cells(line):
    parts = line.strip().strip("|").split("|")
    return [p.strip() for p in parts]


def main():
    ledger = json.load(open(LEDGER, encoding="utf-8"))
    rows = {e["id"]: e for e in ledger["entries"]}
    text = open(DOC, encoding="utf-8").read()
    lines = text.splitlines()

    # --- section boundary: claims live in sections 1-3 (before "## 4.")
    end = next((i for i, l in enumerate(lines) if l.startswith("## 4.")), len(lines))

    claims = 0
    cited = set()
    strong_lines = 0
    headers = None            # column-name -> index for the current table
    in_fence = False
    for n, l in enumerate(lines[:end], 1):
        if l.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence or not l.lstrip().startswith("|"):
            headers = None if not l.lstrip().startswith("|") else headers
            continue
        cs = cells(l)
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cs if c):      # separator row
            continue
        low = [c.lower() for c in cs]
        if "rows" in low and any(c in ("verdict", "status", "measured limits") for c in low) \
                or ("rows" in low and "component" in low):
            headers = {name: i for i, name in enumerate(low)}
            continue
        if headers is None:
            err(f"line {n}: table row with no recognised header")
            continue
        claims += 1
        ids = CITE.findall(l)
        if not ids:
            err(f"line {n}: claim carries no [[ROW-ID]] citation: {cs[0][:60]!r}")
            continue
        for i in ids:
            cited.add(i)
            if i not in rows:
                err(f"line {n}: cited id [[{i}]] is not in LEDGER.json")
        known = [i for i in ids if i in rows]

        verdict = cs[headers["verdict"]].lower() if "verdict" in headers and headers["verdict"] < len(cs) else ""
        is_excl_table = "re-opens if" in headers
        if is_excl_table:
            if not any(p in verdict for p in STRONG + WEAK):
                err(f"line {n}: verdict {verdict!r} not in the controlled phrase list")
            for col in ("measured power", "re-opens if"):
                if headers[col] >= len(cs) or not cs[headers[col]].strip("- "):
                    err(f"line {n}: empty {col!r} cell: {cs[0][:60]!r}")
            ccol = next((k for k in headers if k.startswith("three conditionals")), None)
            if ccol is None or headers[ccol] >= len(cs) or cs[headers[ccol]].count(" / ") < 2:
                err(f"line {n}: conditionals cell must hold key space / transition model / register: {cs[0][:60]!r}")
        if any(p in verdict for p in STRONG):
            strong_lines += 1
            for i in known:
                r = rows[i]
                pc = str(r.get("positive_control") or "").strip().lower()
                cov = r.get("coverage")
                if pc != "passed" and i not in PC_ALLOW:
                    err(f"line {n}: strong verdict cites [[{i}]] whose positive_control is {str(r.get('positive_control'))[:50]!r}")
                if r.get("threshold_fixed_in_advance") is False and "post-data null" not in l:
                    err(f"line {n}: strong verdict cites [[{i}]] whose threshold_fixed_in_advance is false; the line must say 'post-data null'")
                tc = r.get("three_conditionals")
                reg = str(tc.get("adjudicator_register")) if isinstance(tc, dict) else ""
                if NARROW_PLANTS.search(reg) and "[plants:" not in l:
                    err(f"line {n}: strong verdict cites [[{i}]] whose controls are register-narrow ({reg[:60]!r}); the line must carry a '[plants: ...]' scope")
                if cov in (None, "", [], {}):
                    err(f"line {n}: strong verdict cites [[{i}]] whose coverage is null/empty")
            if not any(rows[i].get("reopens_if") or rows[i].get("not_covered") for i in known):
                warns.append(f"line {n}: no cited row carries reopens_if/not_covered")

    # --- pins
    pins = PIN.findall(text)
    for rid, sub in pins:
        if rid not in rows:
            err(f"pin: row {rid} not in LEDGER.json")
        elif sub not in json.dumps(rows[rid], ensure_ascii=False):
            err(f"pin: {sub!r} does not occur in row {rid}")
    for rid in {m.group(1) for m in CITE.finditer(text)}:
        if rid not in rows:
            err(f"citation anywhere: [[{rid}]] not in LEDGER.json")

    # --- forbidden vocabulary (outside quoted history)
    scan, fence = [], False
    for n, l in enumerate(lines, 1):
        if l.strip().startswith("```"):
            fence = not fence
            continue
        if fence or l.lstrip().startswith(">"):
            continue
        s = re.sub(r"<!--.*?-->", "", l)
        s = re.sub(r"`[^`]*`", "", s)
        s = re.sub(r'"[^"]*"', "", s)
        for m in FORBIDDEN.finditer(s):
            err(f"line {n}: forbidden word {m.group(0)!r}")

    # --- report
    print(f"check_ceiling: {os.path.relpath(DOC, LP)} vs LEDGER.json ({len(rows)} rows)")
    print(f"  claim lines (tables, sections 1-3): {claims}   strong-verdict lines: {strong_lines}")
    print(f"  distinct rows cited: {len(cited)}   pins checked: {len(pins)}")
    for w in warns:
        print("  WARN", w)
    for e in errors:
        print("  FAIL", e)
    print("PASS" if not errors else f"FAIL ({len(errors)} violations)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
