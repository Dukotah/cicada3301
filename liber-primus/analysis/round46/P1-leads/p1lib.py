# R46-P1 shared library. Pure stdlib. Imports R45-W1's w1lib read-only for parsing + GP transliteration.
import os, sys, re, math, random, unicodedata, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
W1 = os.path.abspath(os.path.join(HERE, '..', '..', 'round45', 'W1-spaces'))
sys.path.insert(0, W1)
import w1lib as w  # noqa: E402

LP = w.LPROOT
KEYS = os.path.join(LP, 'data', 'keys')
B6 = os.path.join(LP, 'analysis', 'round10b', 'B6-non-english-plaintext', 'corpora')

FE = {
    'archaic': ['armada19/tyndale_new_testament', 'armada19/bible_douay_rheims', 'armada18/shakespeare_hamlet',
                'armada18/agrippa_occult_philosophy_book1_1651jf', 'armada19/bunyan_pilgrims_progress',
                'campaign13/englishcanon_paradise_lost'],
    'translated': ['armada18/homer_odyssey_butler', 'armada18/plato_republic_jowett', 'armada18/dante_inferno_longfellow',
                   'armada19/cervantes_don_quixote_ormsby', 'armada19/herodotus_histories', 'armada19/tao_te_ching_legge',
                   'armada19/goethe_faust_taylor', 'armada19/arabian_nights_lane', 'armada19/kant_critique_pure_reason',
                   'armada19/upanishads_hume', 'campaign13/cypherpunk_kafka_trial'],
    'modern': ['armada18/emerson_essays_first_series', 'armada18/poe_tales_vol2', 'armada18/lovecraft_charles_dexter_ward',
               'armada19/mill_on_liberty', 'armada19/paine_age_of_reason', 'armada19/shelley_frankenstein',
               'armada19/stoker_dracula', 'campaign13/mathscience_abbott_flatland', 'campaign13/philosophy_hume_enquiry',
               'campaign12/walden', 'armada19/carroll_sylvie_and_bruno', 'armada18/crowley_book_of_lies_clean'],
    'verse': ['campaign12/leaves_of_grass'],
}
LANG = {
    'LA': [os.path.join(KEYS, 'armada19', 'virgil_aeneid_latin.txt'), os.path.join(LP, 'analysis', 'latin', 'latin_218.txt')],
    'DE': [os.path.join(B6, 'de_faust.txt'), os.path.join(B6, 'de_2.txt')],
    'CY': [os.path.join(KEYS, 'welsh', 'welsh_mabinogion.txt')],
    'OE': [os.path.join(B6, 'oe_beowulf.txt')],
}
FOLD = {'þ': 'th', 'ð': 'th', 'Þ': 'TH', 'Ð': 'TH', 'æ': 'ae', 'Æ': 'AE', 'ø': 'oe', 'œ': 'oe', 'ö': 'oe', 'Ö': 'OE',
        'Ø': 'OE', 'Œ': 'OE', 'ä': 'ae', 'Ä': 'AE', 'ü': 'ue', 'Ü': 'UE', 'ß': 'ss'}
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")
ARTICLES = {'THE', 'A', 'AN'}


def read_text(path):
    b = open(path, 'rb').read()
    t = b.decode('utf8', errors='replace')
    if t.count('�') > 0.01 * max(1, len(t)):
        t = b.decode('latin-1')
    return t


def fold(t):
    t = ''.join(FOLD.get(ch, ch) for ch in t)
    t = unicodedata.normalize('NFD', t)
    return ''.join(ch for ch in t if not unicodedata.combining(ch))


_MEMO = {}


def tokens(text):
    """list of (UPPER word, rune length)"""
    out = []
    for m in WORD_RE.finditer(text):
        g = m.group().replace("'", '')
        n = _MEMO.get(g)
        if n is None:
            n = _MEMO[g] = len(w.to_runes(g, 'R-A'))
        if n:
            out.append((g.upper(), n))
    return out


def load_fe(rel):
    p = os.path.join(KEYS, rel + '.txt')
    return tokens(w.clean_text(read_text(p)))


def load_lang(code):
    out = []
    for p in LANG[code]:
        t = read_text(p)
        if code == 'OE':
            t = '\n'.join(l for l in t.split('\n') if re.search(r'[þðæÞÐÆ]', l))
        else:
            t = w.clean_text(t)
        out.append(tokens(fold(t)))
    return out  # list of corpora (token lists)


def s2(L):
    return sum(1 for x in L if x == 2) / len(L)


def cls9(n):
    return min(n, 9) - 1


def counts9(L):
    c = [0] * 9
    for x in L:
        c[cls9(x)] += 1
    return c


def dist9(L):
    c = counts9(L); t = sum(c) + 4.5
    return [(x + 0.5) / t for x in c]


def G(L, q):
    c = counts9(L); n = len(L)
    return 2 * sum(x * math.log(x / (n * p)) for x, p in zip(c, q) if x)


def window(L, n, rng):
    a = rng.randrange(0, len(L) - n + 1)
    return L[a:a + n]


def merge(L, m, rng):
    out = [];
    for x in L:
        if out and rng.random() < m:
            out[-1] += x
        else:
            out.append(x)
    return out


def thin2(L, q, rng):
    return [x for x in L if not (x == 2 and rng.random() < q)]


def pct(vals, p):
    v = sorted(vals)
    k = max(0, min(len(v) - 1, int(math.floor(p * (len(v) - 1) + 1e-9))))
    return v[k]


def heartbeat(msg):
    with open(os.path.join(HERE, 'heartbeat.txt'), 'w') as f:
        f.write('%s %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), msg))


def log(msg):
    print(msg, flush=True)
    with open(os.path.join(HERE, 'run.log'), 'a', encoding='utf8') as f:
        f.write(msg + '\n')
