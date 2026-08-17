"""Pick the TARGETED corpus extension from the Project Gutenberg catalog.

Rationale (lane brief): bulk Gutenberg is the obvious move; the smarter one is
coverage of what LP2 plausibly IS.  The Liber Primus' register is esoteric /
hermetic / alchemical / gnostic / runic / aphoristic, and Cicada's own cited and
gestured-at canon is documented in analysis/campaign12/fetch_keytexts.py and the
armada18/19 key sets (already on disk and already in this corpus).

So: score every English Gutenberg title by esoteric/mystic/aphoristic keyword hits
in Title + Subjects + Bookshelves, take the top N, and add a size-ranked bulk
tranche for coverage.  Deterministic, reproducible, no hand-picked IDs to get
wrong.
"""
import csv, sys, os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = sys.argv[1] if len(sys.argv) > 1 else 'pg_catalog.csv'

STRONG = ['hermetic', 'alchem', 'occult', 'kabbal', 'cabala', 'qabalah',
          'rosicrucian', 'gnostic', 'theosoph', 'mystic', 'esoteric',
          'freemason', 'masonic', 'magic', 'astrolog', 'divination', 'tarot',
          'talisman', 'druid', 'runic', 'rune', 'apocrypha', 'gospel',
          'sufi', 'vedanta', 'upanishad', 'zohar', 'grimoire', 'necroman',
          'philosopher\'s stone', 'paracelsus', 'swedenborg', 'blavatsky',
          'crowley', 'agrippa', 'boehme', 'eckhart', 'plotinus', 'neoplaton',
          'orphic', 'pythagor', 'zoroast', 'mithra', 'eleusin', 'initiat',
          'secret doctrine', 'sacred books', 'cipher', 'cryptograph', 'oracle']
MEDIUM = ['mythology', 'folklore', 'legend', 'saga', 'norse', 'celtic',
          'anglo-saxon', 'proverb', 'aphorism', 'maxim', 'meditation',
          'wisdom', 'prophecy', 'apocalypse', 'scripture', 'theology',
          'buddhis', 'hindu', 'taois', 'confucian', 'islam', 'koran', 'quran',
          'talmud', 'psalms', 'philosophy', 'ethics', 'metaphysic',
          'transcendental', 'symbolis', 'emblem', 'allegory', 'poem',
          'sermon', 'devotional', 'egypt', 'babylon', 'chald']


def main():
    rows = []
    with open(CAT, encoding='utf-8', errors='ignore') as f:
        for r in csv.DictReader(f):
            if r.get('Language') != 'en' or r.get('Type') != 'Text':
                continue
            blob = ' '.join([r.get('Title', ''), r.get('Subjects', ''),
                             r.get('Bookshelves', ''),
                             r.get('Authors', '')]).lower()
            sc = sum(3 for k in STRONG if k in blob) + \
                 sum(1 for k in MEDIUM if k in blob)
            if sc <= 0:
                continue
            try:
                gid = int(r['Text#'])
            except Exception:
                continue
            title = re.sub(r'\s+', ' ', r.get('Title', ''))[:90]
            rows.append((sc, gid, title))
    rows.sort(reverse=True)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    top = rows[:n]
    print('scored %d english texts, taking top %d (score %d..%d)'
          % (len(rows), len(top), top[0][0], top[-1][0]))
    json.dump([dict(score=s, gid=g, title=t) for s, g, t in top],
              open(os.path.join(HERE, 'targets.json'), 'w'), indent=0)
    for s, g, t in top[:25]:
        print('  %3d  %6d  %s' % (s, g, t))


if __name__ == '__main__':
    main()
