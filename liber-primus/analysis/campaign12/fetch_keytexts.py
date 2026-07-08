"""Campaign XII, Part 2a -- fetch the expanded running-key candidate corpus.

The repo's tested key corpus was small (~8 texts: the 5 explicitly-referenced works,
the rune poem, solved plaintext). This assembles a DOCUMENTED, closed set of further
candidate keytexts that Cicada thematically gestured at but that were never tested as
running keys -- so the "we can't say we tried all keytexts" gap becomes an enumerated,
reproducible null table.

Each entry is (slug, gutenberg_id, verify_substring, why). We download the Gutenberg
cache text, VERIFY the expected title/author string is present (guards against a wrong
ID silently mislabeling the corpus), and save verified texts to data/keys/campaign12/.
Anything that fails to fetch/verify is DROPPED and reported -- never guessed.

Stdlib only. Reproduce:  PYTHONUTF8=1 python3 fetch_keytexts.py
"""
import os, sys, json, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "data", "keys", "campaign12")
os.makedirs(OUT, exist_ok=True)

# (slug, gutenberg id, case-insensitive verify substring, thematic justification)
CANDIDATES = [
    ("tao_te_ching",     216,  "tao",         "Cicada's Taoist 'the way' / duality imagery"),
    ("bhagavad_gita",    2388, "arjuna",      "Eastern scripture; instar/rebirth themes"),
    ("meditations",      2680, "antoninus",   "Stoicism; 'question all things' ethos"),
    ("art_of_war",       132,  "sun",         "strategy/paths; cypherpunk canon"),
    ("zarathustra",      1998, "zarathustra", "self-overcoming = 'instar emergence'"),
    ("alice_wonderland", 11,   "alice",       "Carroll; Cicada used Carroll refs in 2012"),
    ("rubaiyat",         246,  "khayyam",     "esoteric quatrains; enlightenment"),
    ("beowulf",          16328,"beowulf",     "Anglo-Saxon (rune-language) primary text"),
    ("gold_bug_poe",     2147, "gold-bug",    "Poe cryptogram story; cipher lineage"),
    ("i_ching",          16016,"ching",       "divination/duality; number mysticism"),
    ("kybalion",         57724,"kybalion",    "Hermetic 'the Principles'; 'as above so below'"),
    ("book_of_the_dead", 24565,"osiris",      "Egyptian esoterica; death/rebirth"),
    ("fabre_insects",    2884, "cicada",      "Fabre on the CICADA + 17-yr prime emergence"),
    ("leaves_of_grass",  1322, "whitman",     "transcendentalist; 'self' theme like Emerson"),
    ("prophet_gibran",   58585,"almustafa",   "mystic aphorism; pilgrimage/emergence"),
    ("confessions_aug",  3296, "augustine",   "confession/awakening; primary devotional"),
    ("divine_comedy",    8800, "dante",       "descent/ascent pilgrimage; esoteric numerology"),
    ("walden",           205,  "walden",      "Thoreau; solitude/self-reliance sibling"),
    ("gilgamesh",        11000,"enkidu",      "oldest quest/immortality epic"),
    ("dhammapada",       2017, "buddha",      "path/enlightenment aphorisms"),
]

def fetch(gid):
    url = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"
    req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig/campaign12"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "ignore")

results = []
for slug, gid, verify, why in CANDIDATES:
    dst = os.path.join(OUT, f"{slug}.txt")
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        results.append((slug, "cached", why)); print(f"  cached   {slug}"); continue
    try:
        txt = fetch(gid)
        if verify.lower() not in txt.lower():
            results.append((slug, f"VERIFY-FAIL(no '{verify}')", why))
            print(f"  DROP     {slug}: '{verify}' not in pg{gid} -> wrong ID, skipped")
            continue
        with open(dst, "w", encoding="utf-8") as f:
            f.write(txt)
        results.append((slug, f"ok {len(txt)}B", why))
        print(f"  fetched  {slug} ({len(txt)} B, verified '{verify}')")
    except Exception as e:
        results.append((slug, f"ERR {type(e).__name__}", why))
        print(f"  ERROR    {slug}: {type(e).__name__} {e}")

json.dump(results, open(os.path.join(HERE, "keytext_manifest.json"), "w"), indent=2)
ok = [r for r in results if r[1].startswith(("ok","cached"))]
print(f"\n{len(ok)}/{len(CANDIDATES)} keytexts available in {OUT}")
