# R46-A1: derive lp2-grid-256.json (the 256 base-60 tokens on LP2 grid pages 49/50/51, other repo's numbering)
# from the in-repo rtkd/iddqd master transcription, replacing the external lpx\r\...\lp2-grid-256.json.
# NB: dataset/liber_primus.json holds rune pages only (no grid). rtkd_master.txt and data/sources/relikd_p40-53.txt
# agree at all 256 cells; the external file differs at 5 cells (idx 45,50,165,172,246: letter case, its "2021
# corrections"); no leading digit differs. Output schema = the subset t2_p50_mask.py reads (alphabet, pages[].tokens).
import os, re, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'data', 'sources', 'rtkd_master.txt')
ALPHA = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx'
ROW = re.compile(r'^([0-9A-Za-z]{2}-){7}[0-9A-Za-z]{2}/$')
pages, cur = [], None
for line in open(SRC, encoding='utf8').read().splitlines():
    if ROW.match(line):
        if cur is None: cur = []
        cur += line[:-1].split('-')
    elif cur is not None:
        pages.append(cur); cur = None
if cur: pages.append(cur)
assert [len(p) for p in pages] == [80, 104, 72], [len(p) for p in pages]
out = dict(schema=1, source='data/sources/rtkd_master.txt sha256 ' + hashlib.sha256(open(SRC, 'rb').read()).hexdigest(),
           alphabet=ALPHA, byte_rule='value = 60*digit(first) + digit(second)',
           pages=[dict(page=pg, tokens=t, bytes=[60 * ALPHA.index(x[0]) + ALPHA.index(x[1]) for x in t])
                  for pg, t in zip((49, 50, 51), pages)])
json.dump(out, open(os.path.join(HERE, 'lp2-grid-256.json'), 'w', encoding='utf8'), indent=1)
print('wrote lp2-grid-256.json, 256 tokens')
