"""Parse the scream314 Liber Primus markdown into structured pages.

The source (data/scream314_lp.md) documents each page under a '## <label>'
header, with labelled indented code blocks: 'Runes:', 'Key:', 'Outguess:',
plaintext after 'Reversing the cipher yields:' etc. We extract, per page:
  - label
  - runes        : the raw runic string (runes + '•' word seps + newlines)
  - key_note     : the **Key:** annotation line, if any
  - plaintext    : documented decrypted English, if any (for the gate)
"""
import os
import re

HERE = os.path.dirname(__file__)
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data", "scream314_lp.md"))

RUNE_RE = re.compile(r"[ᚠ-᛿]")


def _indented_block(lines, start):
    """Collect a contiguous indented (4-space/tab) code block starting at/after
    `start`, skipping blank lines inside it. Returns (text, next_index)."""
    i = start
    buf, seen = [], False
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "":
            if seen:
                # peek: stop if the block clearly ended
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if not (nxt.startswith("    ") or nxt.startswith("\t")):
                    break
            i += 1
            continue
        if ln.startswith("    ") or ln.startswith("\t"):
            buf.append(ln.strip("\n"))
            seen = True
            i += 1
        else:
            break
    return "\n".join(buf), i


HEX_RE = re.compile(r"^[0-9a-f\s]+$")


def _classify(blk):
    if RUNE_RE.search(blk):
        return "runes"
    s = blk.strip()
    if not s:
        return "empty"
    if HEX_RE.match(s) and len(s.replace(" ", "").replace("\n", "")) > 40:
        return "hex"
    letters = sum(c.isalpha() for c in s)
    digits = sum(c.isdigit() for c in s)
    if letters > digits and letters > 8:
        return "latin"
    return "other"


def parse(path=DATA):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    pages, cur = [], None
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^## (.+)", ln)
        if m:
            cur = {"label": m.group(1).strip(), "runes": "", "key_note": "",
                   "plaintext": "", "latin_blocks": []}
            pages.append(cur)
            i += 1
            continue
        if cur is not None:
            km = re.match(r"\s*\*\*Key:\*\*\s*(.+)", ln)
            if km:
                cur["key_note"] = km.group(1).strip()
            # any indented block, regardless of preceding label
            if ln.startswith("    ") or ln.startswith("\t"):
                blk, i = _indented_block(lines, i)
                kind = _classify(blk)
                if kind == "runes" and not cur["runes"]:
                    cur["runes"] = blk.strip()
                elif kind == "latin":
                    cur["latin_blocks"].append(blk.strip())
                continue
        i += 1
    # documented English plaintext is conventionally the LAST latin block
    # (after intermediate transliteration steps)
    for p in pages:
        if p["latin_blocks"]:
            p["plaintext"] = p["latin_blocks"][-1]
    return pages


def page_by_label(substr, path=DATA):
    for p in parse(path):
        if substr in p["label"]:
            return p
    return None


if __name__ == "__main__":
    pages = parse()
    print(f"parsed {len(pages)} page sections")
    withrunes = [p for p in pages if p["runes"]]
    print(f"{len(withrunes)} have runes")
    p3 = page_by_label("03.jpg")
    print("\n-- 03.jpg --")
    print("key_note:", p3["key_note"])
    print("runes (first 60):", "".join(RUNE_RE.findall(p3["runes"]))[:60])
    print("plaintext (first 120):", p3["plaintext"][:120].replace("\n", " "))
