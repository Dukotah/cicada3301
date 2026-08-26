"""I5 - hunt every PDF in the local corpus for a runic text layer or an embedded
runic font subset.

The 58 page images are two-stage renders of a typeset document, so a PDF or
PostScript source existed.  If any circulating PDF carries the ORIGINAL typesetting
rather than a re-wrap of the published JPEGs, it will show one of two tells:
  * an extractable text layer containing Unicode Runic (U+16A0..U+16F8), or
  * an embedded font subset whose /BaseFont name identifies the rune face - and,
    through the subset-tag convention, the typesetting program.
A re-wrap of the JPEGs has neither: it has one image XObject per page and no fonts.

Writes pdf_hunt.json incrementally (one line per file) so a long run never loses work.
"""
import os, sys, json, subprocess, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(HERE, 'pdf_hunt.jsonl')
RUNIC = re.compile(r'[ᚠ-ᛸ]')


def run(cmd, timeout=25):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.stdout.decode('utf8', 'replace')
    except Exception as e:
        return 'ERROR: %s' % e


def main():
    pdfs = sorted(glob.glob(os.path.join(ROOT, '**', '*.pdf'), recursive=True))
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding='utf8'):
            try:
                done.add(json.loads(line)['path'])
            except Exception:
                pass
    hits = []
    with open(OUT, 'a', encoding='utf8') as f:
        for p in pdfs:
            rel = os.path.relpath(p, ROOT)
            if rel in done:
                continue
            fonts = run(['pdffonts', p])
            txt = run(['pdftotext', '-l', '5', p, '-'])
            runic = RUNIC.findall(txt)
            names = [l.split()[0] for l in fonts.splitlines()[2:] if l.strip()]
            rec = {'path': rel, 'n_fonts': len(names),
                   'fonts': sorted(set(names))[:20],
                   'n_runic_chars': len(runic),
                   'text_len': len(txt.strip())}
            rec['interesting'] = bool(
                runic or any(re.search(r'run|futh|juni|anglo|saxon|cicada|liber',
                                       n, re.I) for n in names))
            f.write(json.dumps(rec) + '\n')
            f.flush()
            if rec['interesting']:
                hits.append(rec)
    print(json.dumps({'n_pdfs': len(pdfs), 'n_interesting': len(hits),
                      'hits': hits[:40]}, indent=1))


if __name__ == '__main__':
    main()
