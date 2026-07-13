"""Forensic-linguistic profile of the authentic Cicada English prose.

Attribution (match to a named suspect) is impossible here -- see the sample-size
result: there is no suspect with a corpus, and Cicada's own connected prose is
far below the ~500-1000-word floor stylometric authorship methods need. So this
does the thing that IS valid on short texts: PROFILING + CONSISTENCY.

Measures markers that survive tiny samples and tests whether they are CONSISTENT
across independent messages (one hand / one style guide) or divergent (many):
  - double-space-after-period (a generational/typewriter-era typographic tell)
  - US vs UK spelling
  - archaic / formal-literary register ("thus", "alas", "thee", "shall"...)
  - em-dash / ellipsis punctuation habits
  - function-word density (shows WHY it is un-fingerprintable: aphorisms are
    function-word-poor, so the connected-prose signal is even smaller than the
    raw word count suggests)
"""
import json, re, os

base = os.path.dirname(__file__)
corpus = json.load(open(os.path.join(base, 'corpus.json'), encoding='utf-8'))

UK = ['colour', 'honour', 'realise', 'organise', 'centre', 'theatre', 'defence',
      'travelled', 'grey', 'programme', 'whilst', 'towards', 'behaviour']
US = ['color', 'honor', 'realize', 'organize', 'center', 'theater', 'defense',
      'traveled', 'gray', 'program', 'while', 'toward', 'behavior']
ARCHAIC = ['thus', 'alas', 'thee', 'thou', 'thy', 'shall', 'hath', 'unto',
           'henceforth', 'pilgrim', 'sacred', 'divinity', 'wisdom', 'seek',
           'journey', 'emerge', 'instar', 'behold', 'lest', 'yield']
FUNCTION = set("""the of and to a in that it is was for on are as with his they at be this
have from or had by not but what all were we when your can there use word how said an each she
which do their time if will way about many then them would these her long make thing see him two
has look more day could go come did my no most who over know than call first been now find any new
work part take get place made where after back little only round man year came show every good me
give our under name very through just form much great think say help low line before turn cause same
mean differ move right boy old too does tell sentence set three want air well also play small end put
home read hand port large spell add even land here must big high such follow act why ask men change
went light kind off need house picture try us again animal point mother world near build self earth""".split())

def markers(text):
    low = text.lower()
    words = re.findall(r"[a-z']+", low)
    n = max(1, len(words))
    periods = len(re.findall(r'[.!?]', text))
    dbl = len(re.findall(r'[.!?] {2,}\S', text))  # double-space after sentence end
    return {
        'words': len(words),
        'double_space_after_period': (dbl, periods),
        'uk_hits': [w for w in UK if re.search(r'\b'+w+r'\b', low)],
        'us_hits': [w for w in US if re.search(r'\b'+w+r'\b', low)],
        'archaic': sorted({w for w in ARCHAIC if w in words}),
        'archaic_rate_per100w': round(100*sum(words.count(w) for w in ARCHAIC)/n, 1),
        'emdash': text.count('—') + len(re.findall(r'--', text)),
        'ellipsis': text.count('…') + len(re.findall(r'\.\.\.', text)),
        'function_word_density_pct': round(100*sum(w in FUNCTION for w in words)/n, 1),
    }

print('=== CONNECTED-PROSE CORPUS (PGP messages only; koans excluded as aphorism) ===')
msgs = {k: v for k, v in corpus.items() if v['source'] == 'pgp_message'}
prose_words = sum(v['words'] for v in msgs.values())
print(f'{len(msgs)} messages, {prose_words} connected-prose words '
      f'(stylometric authorship floor ~500-1000w/doc; largest doc = '
      f'{max(v["words"] for v in msgs.values())}w)\n')

agg_dbl = [0, 0]
alluk, allus, allarch = set(), set(), set()
rows = []
for k, v in sorted(msgs.items()):
    m = markers(v['text'])
    d, p = m['double_space_after_period']
    agg_dbl[0] += d; agg_dbl[1] += p
    alluk |= set(m['uk_hits']); allus |= set(m['us_hits']); allarch |= set(m['archaic'])
    rows.append((k, v['era'], m))
    print(f"[{v['era']}] {k}  ({m['words']}w)")
    print(f"    dbl-space/periods: {d}/{p}   archaic: {m['archaic'] or '-'}   "
          f"fn-word density: {m['function_word_density_pct']}%")

print('\n=== CROSS-MESSAGE CONSISTENCY (one hand or many?) ===')
print(f"double-space-after-period: {agg_dbl[0]}/{agg_dbl[1]} sentence-ends across ALL messages "
      f"= {100*agg_dbl[0]/max(1,agg_dbl[1]):.0f}%  -> {'CONSISTENT habit' if agg_dbl[1] and agg_dbl[0]/agg_dbl[1]>0.6 else 'mixed'}")
print(f"spelling: UK markers={sorted(alluk) or 'none'}  US markers={sorted(allus) or 'none'}")
print(f"archaic/literary register words used: {sorted(allarch)}")

# koan register (vocab/theme only -- not for function-word stylometry)
koan = {k: v for k, v in corpus.items() if v['source'] == 'liber_primus'}
if koan:
    v = list(koan.values())[0]
    m = markers(v['text'])
    print(f"\n=== KOAN/LP register ({v['words']}w) ===")
    print(f"    function-word density: {m['function_word_density_pct']}% "
          f"(low density = aphoristic, carries little authorship signal)")

json.dump({'connected_prose_words': prose_words, 'n_messages': len(msgs),
           'double_space_after_period': agg_dbl,
           'uk': sorted(alluk), 'us': sorted(allus), 'archaic': sorted(allarch)},
          open(os.path.join(base, 'forensic.json'), 'w'), ensure_ascii=False, indent=2)
