"""Assemble the authentic Cicada English prose corpus and clean it.

Sources (things Cicada actually WROTE, not quoted): the PGP-signed message
bodies 2012-2015, and the solved Liber Primus plaintext / koans. We strip PGP
armor, SHA hash blocks, embedded JPEG hex dumps, book-code number pairs (a:b),
and the '3301' signatures -- leaving only natural-language prose.

Emits stylometry/corpus.json: {doc_id: {era, source, text, words}} and prints
the honest sample-size picture (the whole study lives or dies on this).
"""
import re, json, glob, os

def is_prose_line(ln):
    s = ln.strip()
    if not s:
        return False
    # drop base64 PGP signature blocks: long, no spaces, base64 charset
    if ' ' not in s and len(s) >= 40 and re.fullmatch(r'[A-Za-z0-9+/=]+', s):
        return False
    # drop hex dumps / hash blocks: lines that are mostly hex or digits/colons
    alnum = re.sub(r'[^0-9a-fA-F]', '', s)
    if len(s) >= 20 and len(alnum) / len(s) > 0.85 and re.fullmatch(r'[0-9a-fA-F ]+', s):
        return False
    # drop book-code pairs like "1:5", "152:24"
    if re.fullmatch(r'[\d:.\s]+', s):
        return False
    # drop PGP armor / headers
    if s.startswith('-----') or s.lower().startswith('hash:') or s.lower().startswith('version:'):
        return False
    # must contain some real letters/words
    letters = sum(c.isalpha() for c in s)
    return letters >= 4 and letters / len(s) > 0.4

def clean(raw):
    lines = [l for l in raw.splitlines() if is_prose_line(l)]
    txt = '\n'.join(lines)
    # remove standalone 3301 signatures and lone number tokens
    txt = re.sub(r'\b3301\b', '', txt)
    txt = re.sub(r'\n\s*\d+\s*\n', '\n', txt)
    # collapse >2 spaces? NO -- we WANT to preserve double-space-after-period tell.
    return txt.strip()

base = os.path.dirname(__file__)
armada = os.path.join(base, '..', 'armada20')
corpus = {}

# 1) individual PGP message bodies, tagged by year
for f in sorted(glob.glob(os.path.join(armada, 'pgp_20*.txt'))):
    name = os.path.basename(f)[:-4]
    m = re.search(r'20(1\d)', name)
    era = f'20{m.group(1)}' if m else '20xx'
    txt = clean(open(f, encoding='utf-8', errors='ignore').read())
    if len(txt.split()) >= 12:  # skip near-empty
        corpus[name] = {'era': era, 'source': 'pgp_message', 'text': txt,
                        'words': len(txt.split())}

# 2) solved Liber Primus plaintext / koans (one doc)
sp = os.path.join(base, '..', '..', 'data', 'keys', 'solved_plaintext.txt')
if os.path.exists(sp):
    txt = clean(open(sp, encoding='utf-8', errors='ignore').read())
    corpus['solved_liber_primus_koans'] = {'era': 'LP', 'source': 'liber_primus',
                                           'text': txt, 'words': len(txt.split())}

json.dump(corpus, open(os.path.join(base, 'corpus.json'), 'w'),
          ensure_ascii=False, indent=2)

total = sum(d['words'] for d in corpus.values())
print(f'{len(corpus)} documents, {total} clean prose words total\n')
for k, d in sorted(corpus.items(), key=lambda kv: -kv[1]['words']):
    print(f"  {d['words']:4d}w  [{d['era']:4}] {k}")
print('\n--- sample of the largest doc ---')
biggest = max(corpus.values(), key=lambda d: d['words'])
print(biggest['text'][:400])
