#!/usr/bin/env python3
"""N1 positive + negative control.

POSITIVE: build a PDF that embeds a *subset* of a runic TrueType face and typesets
runic text, then prove that `pdffonts` surfaces (emb=yes, sub=yes) with a
`TAG+FaceName` /BaseFont, and recover the six-char subset tag verbatim.

NEGATIVE: wrap a page image into a PDF and prove `pdffonts` reports zero fonts
(a re-wrap of the published JPEGs has neither a subset nor a text layer).

If the instrument cannot surface a planted subset tag, the archival null is worthless.
"""
import os, re, subprocess, sys, tempfile, shutil, json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FONT = os.path.join(REPO, "analysis/round18/L1-toolchain/fonts/NotoSansRunic-Regular.ttf")
OUT = os.path.join(HERE, "control_pos.pdf")
NEG = os.path.join(HERE, "control_neg.pdf")


def pdffonts(path):
    r = subprocess.run(["pdffonts", path], capture_output=True, text=True)
    return r.stdout


def build_positive():
    # runic text: FEHU URUZ THURISAZ ANSUZ  (U+16A0 U+16A2 U+16A6 U+16A8...)
    runes = "ᚠᚢᚦᚨᚱᚷᛁᛇ"
    tex = r"""\documentclass{article}
\usepackage{fontspec}
\newfontface\runic{%s}[Path=/]
\pagestyle{empty}
\begin{document}
{\runic %s}
\end{document}
""" % (FONT, runes)
    # fontspec Path needs a trailing slash dir; give absolute path via Path=<dir>/
    fontdir = os.path.dirname(FONT) + "/"
    fontfile = os.path.basename(FONT)
    tex = r"""\documentclass{article}
\usepackage{fontspec}
\newfontface\runic{%s}[Path=%s]
\pagestyle{empty}
\begin{document}
{\runic %s}
\end{document}
""" % (fontfile, fontdir, runes)
    td = tempfile.mkdtemp(prefix="n1ctrl_")
    texpath = os.path.join(td, "ctrl.tex")
    with open(texpath, "w") as f:
        f.write(tex)
    r = subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error",
                        "ctrl.tex"], cwd=td, capture_output=True, text=True)
    pdf = os.path.join(td, "ctrl.pdf")
    if not os.path.exists(pdf):
        print("LUALATEX FAILED\n", r.stdout[-2000:], file=sys.stderr)
        shutil.rmtree(td, ignore_errors=True)
        return None
    shutil.copy(pdf, OUT)
    shutil.rmtree(td, ignore_errors=True)
    return OUT


def build_negative():
    # rewrap a page jpeg into an image-only PDF via ghostscript's viewjpeg, or
    # simpler: use img2pdf-style gs. Use gs to convert a jpg to pdf.
    jpg = None
    for cand in ["corpus/G-forensics/raw", "analysis"]:
        pass
    # find any LP page jpg
    r = subprocess.run(["bash", "-c",
        "find %s -iname '*.jpg' | head -1" % REPO], capture_output=True, text=True)
    jpg = r.stdout.strip()
    if not jpg:
        return None
    # gs viewjpeg approach
    ps = r"""/infile (%s) (r) file def
<< /PageSize [612 792] >> setpagedevice
infile /DCTDecode filter
""" % jpg
    # simpler: use `gs` with jpg via a helper — but robust path is ImageMagick if present
    if shutil.which("convert"):
        subprocess.run(["convert", jpg, NEG], capture_output=True)
    elif shutil.which("img2pdf"):
        subprocess.run(["img2pdf", jpg, "-o", NEG], capture_output=True)
    else:
        return None
    return NEG if os.path.exists(NEG) else None


def main():
    result = {"font_source": FONT, "font_exists": os.path.exists(FONT)}

    pos = build_positive()
    result["positive_pdf"] = pos
    if pos:
        out = pdffonts(pos)
        result["positive_pdffonts"] = out
        # find a subset line: emb yes sub yes, BaseFont with TAG+Name
        tags = re.findall(r'([A-Z]{6})\+(\S+)', out)
        result["subset_tags"] = ["%s+%s" % (t, n) for t, n in tags]
        # confirm emb/sub columns
        emb_sub = []
        for line in out.splitlines():
            if re.search(r'\bemb\b', line) or 'BaseFont' in line:
                continue
            cols = line.split()
            if len(cols) >= 4 and re.search(r'[A-Z]{6}\+', line):
                emb_sub.append(line)
        result["subset_lines"] = emb_sub
        result["positive_PASS"] = bool(tags) and ("yes" in out)
        # pdftotext text-layer recovery
        rt = subprocess.run(["pdftotext", pos, "-"], capture_output=True, text=True)
        txt = rt.stdout
        runic_cp = [hex(ord(c)) for c in txt if 0x16A0 <= ord(c) <= 0x16FF]
        result["text_layer_runic_codepoints"] = runic_cp

    neg = build_negative()
    result["negative_pdf"] = neg
    if neg:
        outn = pdffonts(neg)
        result["negative_pdffonts"] = outn
        # count font rows (lines after the 2 header lines)
        body = [l for l in outn.splitlines()[2:] if l.strip()]
        result["negative_n_fonts"] = len(body)
        result["negative_PASS"] = (len(body) == 0)

    with open(os.path.join(HERE, "control_results.json"), "w") as f:
        json.dump(result, f, indent=1)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("positive_pdffonts", "negative_pdffonts")}, indent=1))
    print("\n=== positive pdffonts ===\n", result.get("positive_pdffonts", ""))
    print("\n=== negative pdffonts ===\n", result.get("negative_pdffonts", ""))


if __name__ == "__main__":
    main()
