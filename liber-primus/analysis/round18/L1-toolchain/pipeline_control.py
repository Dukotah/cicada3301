"""I2 / PC2 - pipeline discrimination control (Round 18 lane L1).

Builds two synthetic PDFs (one whose page content is pure black-on-white, one
with a colour element), pushes each through every rasterisation pipeline that is
available on this machine, and fingerprints the JPEG each pipeline emits with I1.

The point is NOT to reproduce the LP2 files byte-for-byte (the source document is
not in hand).  It is to establish, with a control, WHICH encoder parameters are
pipeline-discriminating, and therefore what the LP2 parameter vector rules in and
out.

Run under WSL:
  python3 pipeline_control.py            -> control_results.json + stdout table
"""
import os, sys, json, subprocess, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jpeg_fingerprint import fingerprint

OUT = os.path.join(HERE, 'control_out')

PS_GRAY = r"""%!PS-Adobe-3.0
%%BoundingBox: 0 0 432 648
/Times-Roman findfont 40 scalefont setfont
0 setgray
72 500 moveto (LIBER CONTROL PAGE) show
72 440 moveto (abcdefghijklmnop) show
0 setgray 72 100 300 60 rectfill
showpage
"""

PS_COLOUR = r"""%!PS-Adobe-3.0
%%BoundingBox: 0 0 432 648
/Times-Roman findfont 40 scalefont setfont
0 setgray
72 500 moveto (LIBER CONTROL PAGE) show
0.8 0.1 0.1 setrgbcolor
72 100 300 60 rectfill
showpage
"""


def sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
        return r.returncode, r.stdout.decode('utf8', 'replace')[-400:], \
            r.stderr.decode('utf8', 'replace')[-400:]
    except Exception as e:  # noqa
        return -1, '', str(e)


def tool_versions():
    v = {}
    for name, cmd in (('gs', 'gs --version'),
                      ('imagemagick', 'convert --version | head -1'),
                      ('magick', 'magick --version | head -1'),
                      ('pdftoppm', 'pdftoppm -v 2>&1 | head -1'),
                      ('mutool', 'mutool -v 2>&1 | head -1'),
                      ('cjpeg', 'cjpeg -version 2>&1 | head -1'),
                      ('python-pillow', 'python3 -c "import PIL;print(PIL.__version__)"')):
        rc, so, se = sh(cmd)
        v[name] = (so or se).strip() if rc == 0 or so or se else None
    return v


def build_inputs():
    os.makedirs(OUT, exist_ok=True)
    paths = {}
    for tag, src in (('gray', PS_GRAY), ('colour', PS_COLOUR)):
        ps = os.path.join(OUT, 'ctl_%s.ps' % tag)
        pdf = os.path.join(OUT, 'ctl_%s.pdf' % tag)
        open(ps, 'w').write(src)
        sh('gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -o %s %s' % (pdf, ps))
        paths[tag] = pdf
    return paths


PIPELINES = [
    ('gs-jpeg-default',
     'gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -r400 -o {out} {pdf}'),
    ('gs-jpeg-q92',
     'gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -dJPEGQ=92 -r400 -o {out} {pdf}'),
    ('gs-jpeggray-q92',
     'gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeggray -dJPEGQ=92 -r400 -o {out} {pdf}'),
    ('im-convert-default',
     'convert -density 400 {pdf} {out}'),
    ('im-convert-q92',
     'convert -density 400 -quality 92 {pdf} {out}'),
    ('im-convert-q92-420',
     'convert -density 400 -quality 92 -sampling-factor 2x2 {pdf} {out}'),
    ('gs-png-then-im',
     'gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r400 -o {out}.png {pdf} && '
     'convert {out}.png {out}'),
    ('gs-png-then-im-q92-420',
     'gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r400 -o {out}.png {pdf} && '
     'convert {out}.png -quality 92 -sampling-factor 2x2 {out}'),
    ('pdftoppm-then-im',
     'pdftoppm -r 400 -png -singlefile {pdf} {out}_pp && convert {out}_pp.png {out}'),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {'tool_versions': tool_versions(), 'runs': []}
    pdfs = build_inputs()
    for tag, pdf in pdfs.items():
        for name, tmpl in PIPELINES:
            out = os.path.join(OUT, '%s__%s.jpg' % (tag, name))
            for stale in (out, out + '.png', out + '_pp.png'):
                if os.path.exists(stale):
                    os.unlink(stale)
            cmd = tmpl.format(out=out, pdf=pdf)
            rc, so, se = sh(cmd)
            rec = {'content': tag, 'pipeline': name, 'cmd': cmd, 'rc': rc}
            if os.path.exists(out):
                fp = fingerprint(out)
                v = fp['fingerprint_vector']
                rec['vector'] = v
                rec['icc_desc'] = (fp['icc'] or {}).get('icc_desc', {}).get('text')
                rec['icc_cprt'] = (fp['icc'] or {}).get('icc_cprt', {}).get('text')
                rec['icc_len'] = (fp['icc'] or {}).get('len')
                rec['icc_sha256'] = (fp['icc'] or {}).get('sha256')
            else:
                rec['error'] = se[-200:]
            res['runs'].append(rec)
    with open(os.path.join(HERE, 'control_results.json'), 'w') as f:
        json.dump(res, f, indent=1)

    print(json.dumps(res['tool_versions'], indent=1))
    hdr = '%-10s %-24s %-5s %-10s %-6s %-18s %-8s %s' % (
        'content', 'pipeline', 'ncmp', 'subsamp', 'ijgQ', 'huff', 'apps', 'iccdesc')
    print(hdr)
    print('-' * len(hdr))
    for r in res['runs']:
        v = r.get('vector')
        if not v:
            print('%-10s %-24s FAILED %s' % (r['content'], r['pipeline'],
                                             r.get('error', '')[:60]))
            continue
        print('%-10s %-24s %-5s %-10s %-6s %-18s %-8s %s' % (
            r['content'], r['pipeline'], v['ncomp'], v['subsampling'],
            ','.join(str(q) for qq in v['ijg_q'] for q in qq) or 'nonstd',
            ','.join(v['dht_class']), ','.join(v['apps']), r.get('icc_desc')))
    # LP2 reference
    print('\nLP2 reference vector: ncomp 3 or 1 | subsamp 22x11x11 / 11 | ijgQ 92 |'
          ' huff custom-optimised | apps JFIF,ICC_PROFILE | icc "Artifex Software'
          ' sRGB ICC Profile" 2576B | JFIF 1.01 units=1 400x400 | 2400x3600 | no DRI')


if __name__ == '__main__':
    main()
