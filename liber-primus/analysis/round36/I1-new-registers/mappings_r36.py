"""Round 36 / I1 -- deterministic corpus-alphabet -> ASCII romanisation for Greek, Hebrew, Norse.

Output of every function is an UPPERCASE ASCII string. The existing Latin->rune step
(`detectors.text_to_runes(s, "EN")`: folds K,Q->C, V->U, Z->S, greedy longest-match over
TH EO NG OE AE IA EA, all other letters one rune each, everything non-A-Z is a word break) is
applied afterwards, UNCHANGED, so the new registers are on exactly the same footing as the nine.
Variants: V=1 is the pre-registered mapping, V=2 the single permitted revision (see mappings.md).
Reads data only (parses text, never executes it).
"""
import html
import re
import unicodedata

# ------------------------------------------------------------------ Greek
_G = {"α": "A", "β": "B", "γ": "G", "δ": "D", "ε": "E", "ζ": "Z", "η": "E", "θ": "TH", "ι": "I",
      "κ": "K", "λ": "L", "μ": "M", "ν": "N", "ξ": "X", "ο": "O", "π": "P", "ρ": "R", "σ": "S",
      "ς": "S", "τ": "T", "υ": "Y", "φ": "F", "χ": "CH", "ψ": "PS", "ω": "O"}
_G2 = dict(_G, **{"η": "EA", "ω": "OE", "χ": "K", "φ": "PH", "υ": "U"})   # v2 (see mappings.md)
_VOW = "αεηιουω"


def greek_html_text(raw):
    i = raw.find("<body")
    t = re.sub(r"<[^>]+>", " ", raw[i:] if i >= 0 else raw)
    return html.unescape(t)


def greek_to_ascii(text, V=1):
    tab = _G if V == 1 else _G2
    out = []
    for word in re.split(r"[^Ͱ-Ͽἀ-῿̀-ͯ]+", text):
        if not word:
            continue
        d = unicodedata.normalize("NFD", word.lower())
        # tokens: (base letter, rough?)
        toks = []
        for ch in d:
            if "̀" <= ch <= "ͯ":
                if ch == "̔" and toks:           # rough breathing
                    toks[-1][1] = True
                continue                              # all other marks incl. iota subscript dropped
            if ch in tab:
                toks.append([ch, False])
        s = []
        for k, (c, rough) in enumerate(toks):
            nxt = toks[k + 1][0] if k + 1 < len(toks) else ""
            if c == "γ" and nxt in "γκξχ" and nxt:
                s.append("N")                         # gamma nasal
                continue
            if c == "υ" and k > 0 and toks[k - 1][0] in "αεηο" and V == 1:
                s.append("U")                         # diphthong au eu ou eu
                continue
            if c == "ρ":
                s.append("R" + ("H" if (rough and k == 0) else ""))
                continue
            if rough and k == 0 and c in _VOW:
                s.append("H")
            if c == "υ" and k == 0 and rough:
                s.append("H") if False else None      # (initial rough upsilon handled above via _VOW)
            s.append(tab[c])
        out.append("".join(s))
    return " ".join(out).upper()


# ------------------------------------------------------------------ Hebrew
_HC = {"א": "", "ב": "B", "ג": "G", "ד": "D", "ה": "H", "ו": "W", "ז": "Z", "ח": "H", "ט": "T",
       "י": "Y", "כ": "K", "ך": "K", "ל": "L", "מ": "M", "ם": "M", "נ": "N", "ן": "N", "ס": "S",
       "ע": "", "פ": "P", "ף": "P", "צ": "TS", "ץ": "TS", "ק": "K", "ר": "R", "ש": "SH", "ת": "T"}
_HV = {"ְ": "", "ֱ": "E", "ֲ": "A", "ֳ": "O", "ִ": "I", "ֵ": "E",
       "ֶ": "E", "ַ": "A", "ָ": "A", "ֹ": "O", "ֺ": "O", "ֻ": "U"}
DAGESH, SHIN, SIN = "ּ", "ׁ", "ׂ"


def hebrew_osis_words(raw):
    """Words of an OSIS <w> file: text inside <w ...>..</w>, morpheme '/' removed."""
    ws = re.findall(r"<w [^>]*>([^<]*)</w>", raw)
    return [w.replace("/", "") for w in ws]


def hebrew_to_ascii(words, V=1):
    out = []
    for w in words:
        d = unicodedata.normalize("NFD", w) if False else w
        # cluster: consonant followed by combining marks (Hebrew block U+0591-U+05C7)
        cl = []
        for ch in d:
            if ch in _HC:
                cl.append([ch, set()])
            elif "֑" <= ch <= "ׇ" and cl:
                cl[-1][1].add(ch)
        s = []
        for k, (c, m) in enumerate(cl):
            vow = [_HV[x] for x in m if x in _HV]
            vtxt = "".join(vow)
            prev_v = ""
            if k > 0:
                pm = cl[k - 1][1]
                prev_v = "".join(_HV[x] for x in pm if x in _HV)
            last = k == len(cl) - 1
            if c == "ו":
                if "ֹ" in m:
                    s.append("O"); continue
                if DAGESH in m and not vow:
                    s.append("U"); continue
                s.append("W" + vtxt); continue
            if c == "י" and not vow and prev_v in ("I", "E") and prev_v != "":
                continue                              # mater lectionis
            if c == "ה" and last and DAGESH not in m and (not vow):
                continue                              # final silent he
            if c == "ש":
                s.append(("S" if SIN in m else "SH") + vtxt); continue
            if c in "פף":
                s.append(("P" if DAGESH in m else ("P" if V == 1 else "F")) + vtxt); continue
            base = _HC[c]
            if V == 2 and c == "ע":
                base = "A"
            if V == 2 and c == "א" and not vow and k == 0:
                base = ""
            if V == 2 and c == "ח":
                base = "KH"
            if V == 2 and c in "תּ" and False:
                base = "T"
            s.append(base + vtxt)
            if V == 2 and "ְ" in m and not last and k > 0:
                s.append("E")                          # vocal-ish sheva -> E
        out.append("".join(s))
    return " ".join(out).upper()


# ------------------------------------------------------------------ Norse
_N1 = {"þ": "TH", "ð": "TH", "æ": "AE", "ǽ": "AE", "œ": "OE", "ø": "OE", "ǿ": "OE", "ö": "OE", "ǫ": "O",
       "ó": "O", "á": "A", "é": "E", "í": "I", "ú": "U", "ý": "Y", "ȯ": "O", "ę": "E", "ǭ": "O"}
_N2 = dict(_N1, **{"ð": "D", "ö": "O", "ǫ": "OE", "ø": "O"})            # v2


def norse_html_text(raw):
    i = raw.find("mw-parser-output")
    body = raw[i:] if i >= 0 else raw
    j = body.find("►")                        # drop the Norwegian language-selector header
    if 0 <= j < 3000:
        body = body[j + 1:]
    k = body.find("printfooter")
    if k > 0:
        body = body[:k]
    body = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", body)
    return html.unescape(re.sub(r"<[^>]+>", " ", body))


def norse_to_ascii(text, V=1):
    tab = _N1 if V == 1 else _N2
    t = unicodedata.normalize("NFC", text.lower())
    o = []
    for ch in t:
        if ch in tab:
            o.append(tab[ch])
        elif "a" <= ch <= "z":
            o.append(ch)
        else:
            dch = unicodedata.normalize("NFD", ch)[0]       # strip any other accent
            o.append(dch if "a" <= dch <= "z" else " ")
    return "".join(o).upper()
