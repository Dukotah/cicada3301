"""I2b - two-stage chain control (Round 18 lane L1).

PC2 established that a Ghostscript *jpeg device* render emits IJG-STANDARD Huffman
tables, while ImageMagick emits CUSTOM-OPTIMISED ones.  The LP2 pages carry BOTH
an Artifex (= Ghostscript) sRGB ICC profile AND custom-optimised Huffman tables,
which no single-stage pipeline in PC2 produced.  That points at a TWO-STAGE chain:
Ghostscript writes the JPEG (contributing the ICC and the 4:2:0 sampling), then a
second program re-encodes it (contributing the optimised Huffman tables), carrying
the ICC through.

This script tests that chain directly, and specifically tests the LP2 anomaly that
23 of 58 pages are GRAYSCALE JPEGs that nevertheless carry an sRGB (not sGray) ICC
profile - the signature of an automatic per-page gray detection applied downstream
of a Ghostscript sRGB render.
"""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jpeg_fingerprint import fingerprint

OUT = os.path.join(HERE, 'control_out')
LP2_REF = {
    'ncomp_colour': 3, 'ncomp_gray': 1,
    'subsampling_colour': '22x11x11', 'subsampling_gray': '11',
    'ijg_q': 92, 'huff': 'custom-optimised',
    'apps': ['JFIF', 'ICC_PROFILE'],
    'icc_desc': 'Artifex Software sRGB ICC Profile',
    'icc_len': 2576, 'jfif_ver': '1.01', 'jfif_units': 1, 'density': 400,
    'dri': None, 'com': [],
}


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, timeout=600)
    return r.returncode, r.stderr.decode('utf8', 'replace')[-300:]


def vec(path):
    fp = fingerprint(path)
    v = fp['fingerprint_vector']
    return {
        'ncomp': v['ncomp'], 'subsampling': v['subsampling'],
        'ijg_q': [q for qq in v['ijg_q'] for q in qq],
        'huff': v['dht_class'], 'apps': v['apps'], 'dri': v['dri'],
        'jfif': v['jfif'], 'geometry': v['geometry'],
        'marker_order': v['marker_order'],
        'icc_desc': (fp['icc'] or {}).get('icc_desc', {}).get('text'),
        'icc_cprt': (fp['icc'] or {}).get('icc_cprt', {}).get('text'),
        'icc_len': (fp['icc'] or {}).get('len'),
        'icc_sha256': (fp['icc'] or {}).get('sha256'),
        'com': fp['com'], 'size': fp['size'],
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for tag in ('gray', 'colour'):
        pdf = os.path.join(OUT, 'ctl_%s.pdf' % tag)
        if not os.path.exists(pdf):
            print('run pipeline_control.py first (missing %s)' % pdf)
            return
        for gsq in (75, 92):
            a = os.path.join(OUT, 'chain_%s_gs%d.jpg' % (tag, gsq))
            sh('gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -dJPEGQ=%d -r400 -o %s %s'
               % (gsq, a, pdf))
            res['stage1_gs_q%d_%s' % (gsq, tag)] = vec(a)
            # stage 2 variants
            b = os.path.join(OUT, 'chain_%s_gs%d_im.jpg' % (tag, gsq))
            sh('convert %s %s' % (a, b))
            res['stage2_im_noargs_gs%d_%s' % (gsq, tag)] = vec(b)

            c = os.path.join(OUT, 'chain_%s_gs%d_im_q92.jpg' % (tag, gsq))
            sh('convert %s -quality 92 %s' % (a, c))
            res['stage2_im_q92_gs%d_%s' % (gsq, tag)] = vec(c)

            d = os.path.join(OUT, 'chain_%s_gs%d_im_strip_off.jpg' % (tag, gsq))
            sh('convert %s -quality 92 -define jpeg:optimize-coding=true %s' % (a, d))
            res['stage2_im_q92_optcode_gs%d_%s' % (gsq, tag)] = vec(d)

            e = os.path.join(OUT, 'chain_%s_gs%d_pil.jpg' % (tag, gsq))
            sh('python3 -c "from PIL import Image; im=Image.open(\'%s\');'
               ' im.save(\'%s\', quality=92, optimize=True, icc_profile=im.info.get(\'icc_profile\'))"'
               % (a, e))
            res['stage2_pil_q92opt_gs%d_%s' % (gsq, tag)] = vec(e)
    with open(os.path.join(HERE, 'chain_results.json'), 'w') as f:
        json.dump({'lp2_reference': LP2_REF, 'runs': res}, f, indent=1)

    cols = ('ncomp', 'subsampling', 'ijg_q', 'huff', 'apps', 'icc_desc', 'com')
    w = '%-38s %-5s %-10s %-6s %-18s %-24s %-34s %s'
    print(w % (('run',) + cols))
    print('-' * 175)
    for k, v in res.items():
        print(w % (k, v['ncomp'], v['subsampling'],
                   ','.join(map(str, v['ijg_q'])) or 'nonstd',
                   ','.join(v['huff']), ','.join(a[:22] for a in v['apps']),
                   str(v['icc_desc'])[:34], v['com']))
    print('\nLP2 target: colour 3/22x11x11 | gray 1/11 | q92 | custom-optimised |'
          ' JFIF,ICC_PROFILE | "Artifex Software sRGB ICC Profile" (2576B) | no COM')


if __name__ == '__main__':
    main()
