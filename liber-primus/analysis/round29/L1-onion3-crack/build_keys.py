#!/usr/bin/env python3
"""L1 Round-29: build a large Cicada-native key dictionary for the onion image
OutGuess/steghide key attack. Writes keys_big.txt (deduped, provenance in
keys_provenance.txt).

Sources:
  A. every word in solved LP plaintext (SOLVED-PAGES.json) + AN END / PARABLE.
  B. LP-thematic phrases + words (data/keys/thematic.txt, words_expanded.txt).
  C. Gematria Primus: rune transliterations, rune names, numeric prime forms.
  D. Cicada numbers: 3301, 1595277641, 509, 503, 1033, 761, 131, 151, 167, ...
  E. magic-square words + corpus tokens (runepoem, self_reliance, agrippa,
     book_of_the_law, mabinogion, thematic).
  F. case variants (lower/UPPER/Title) + a few concatenations.
  G. the prior 59-key list (analysis/armada_osint/keys.txt) folded in.
"""
import os, re, json, itertools

ROOT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus"
HERE = os.path.dirname(os.path.abspath(__file__))
keys = {}          # key -> provenance tag (first source wins)

def add(k, tag):
    k = k.strip()
    if not k:
        return
    if len(k) > 64:          # outguess/steghide keys: cap length
        return
    if k not in keys:
        keys[k] = tag

# ---- A. solved LP plaintext words ----
sp = json.load(open(os.path.join(ROOT, "SOLVED-PAGES.json")))
for pg in sp["pages"]:
    txt = pg.get("plaintext_transliteration") or ""
    # the transliteration is run-together; also split known word-ish chunks
    add(txt[:64], "A:solved-page-full")
    for w in re.findall(r"[A-Za-z]{3,}", txt):
        add(w, "A:solved-word")
    if pg.get("key"):
        add(pg["key"], "A:solved-key")

# also fold the raw solved_plaintext.txt tokens (English words in it)
try:
    raw = open(os.path.join(ROOT, "data/keys/solved_plaintext.txt")).read()
    for w in re.findall(r"[A-Za-z]{3,}", raw):
        if not re.fullmatch(r"[0-9a-f]+", w):   # skip pure hex
            add(w.upper(), "A:solved-txt")
except FileNotFoundError:
    pass

# ---- B. thematic + expanded word lists ----
for fn, tag in [("data/keys/thematic.txt", "B:thematic"),
                ("data/keys/words_expanded.txt", "B:words_expanded")]:
    p = os.path.join(ROOT, fn)
    if os.path.exists(p):
        for line in open(p):
            add(line.strip(), tag)

# LP-thematic phrases (spaced + concatenated)
phrases = [
    "A WARNING", "BELIEVE NOTHING", "THE PRIMES ARE SACRED",
    "AN INSTAR EMERGES", "INSTAR EMERGENCE", "AN END", "A KOAN",
    "CIRCUMFERENCE", "CONSCIOUSNESS", "THE LOSS OF DIVINITY",
    "COMMAND YOUR OWN SELF", "KNOW THIS", "LIKE THE INSTAR TUNNELING",
    "WITHIN THE DEEP WEB THERE EXISTS A PAGE", "FIND YOUR TRUTH",
    "THE TOTIENT FUNCTION IS SACRED", "ALL THINGS SHOULD BE ENCRYPTED",
    "FOR ALL IS SACRED", "EXPERIENCE YOUR DEATH", "PILGRIM", "PILGRIMAGE",
    "WELCOME", "THE GREAT JOURNEY", "END OF ALL THINGS", "SELF RELIANCE",
    "EMERGE", "SACRED", "DIVINITY", "TOTIENT", "PARABLE", "WISDOM",
    "MOBIUS", "ANALOG", "SHADOWS", "AETHEREAL", "VOID", "CARNAL",
    "OBSCURA", "MOURNFUL", "CABAL", "BUFFERS", "FORM", "EPIPHANY",
    "ENLIGHTENMENT", "PRESERVE", "ADHERE", "DECEPTION", "CONSUMPTION",
    "THE INSTAR", "GOOD LUCK", "PATIENCE", "CICADA", "THE SEEKER",
    "SOME WISDOM", "A PARABLE", "THE PATH", "FOLLOW",
]
for ph in phrases:
    add(ph, "B:phrase-spaced")
    add(ph.replace(" ", ""), "B:phrase-concat")
    add(ph.title().replace(" ", ""), "B:phrase-title")

# ---- C. Gematria Primus ----
GEMATRIA = [
    (0,"F",2),(1,"U",3),(2,"TH",5),(3,"O",7),(4,"R",11),(5,"C",13),(6,"G",17),
    (7,"W",19),(8,"H",23),(9,"N",29),(10,"I",31),(11,"J",37),(12,"EO",41),
    (13,"P",43),(14,"X",47),(15,"S",53),(16,"T",59),(17,"B",61),(18,"E",67),
    (19,"M",71),(20,"L",73),(21,"NG",79),(22,"OE",83),(23,"D",89),(24,"A",97),
    (25,"AE",101),(26,"Y",103),(27,"IA",107),(28,"EA",109),
]
# rune poem names (Anglo-Saxon futhorc)
rune_names = ["FEOH","UR","THORN","OS","RAD","CEN","GYFU","WYNN","HAEGL","NYD",
    "IS","GER","EOH","PEORTH","EOLH","SIGEL","TIR","BEORC","EH","MANN","LAGU",
    "ING","ETHEL","DAEG","AC","AESC","YR","IOR","EAR","ETHEL","OETHEL"]
for _,t,pr in GEMATRIA:
    add(t, "C:rune-translit")
    add(str(pr), "C:rune-prime")
for rn in rune_names:
    add(rn, "C:rune-name")
    add(rn.title(), "C:rune-name")
# product / sum of all primes (3301!) already covered by numbers below

# ---- D. Cicada numbers ----
nums = ["3301","1595277641","509","503","1033","761","131","151","199","481",
        "167","845145127","17","29","3301","1033","36","5243","162667212858",
        "65537","2013","2014","2012","33011033","3301761","3301167","10331033"]
for nnum in nums:
    add(nnum, "D:cicada-number")

# ---- E. corpus tokens (top frequency) ----
import collections
for fn, tag, topn in [
        ("data/keys/runepoem_translit.txt","E:runepoem",9999),
        ("data/keys/runepoem_oe.txt","E:runepoem_oe",9999),
        ("data/keys/self_reliance.txt","E:self_reliance",800),
        ("data/keys/agrippa.txt","E:agrippa",800),
        ("data/keys/book_of_the_law.txt","E:book_of_law",800),
        ("data/keys/mabinogion.txt","E:mabinogion",1200),
        ("data/keys/thematic.txt","E:thematic",9999)]:
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p):
        continue
    words = re.findall(r"[A-Za-z]{3,}", open(p, encoding="latin-1").read())
    cnt = collections.Counter(w.upper() for w in words)
    for w,_ in cnt.most_common(topn):
        add(w, tag)

# ---- G. prior 59-key list ----
prior = os.path.join(ROOT, "analysis/armada_osint/keys.txt")
if os.path.exists(prior):
    for line in open(prior):
        add(line.strip(), "G:prior-59")

# ---- F. case variants for the compact thematic/number core ----
core = [k for k,v in list(keys.items())
        if v.startswith(("B:phrase","C:","D:","A:solved-key")) and k.isalpha()]
for k in core:
    add(k.lower(), "F:lower")
    add(k.upper(), "F:upper")
    add(k.capitalize(), "F:title")

# empty key (keyless) as an explicit entry for the control path
add("", "H:keyless")  # will be filtered by add()'s empty guard -> handled separately

# ---- write out ----
out = os.path.join(HERE, "keys_big.txt")
with open(out, "w") as f:
    for k in keys:
        f.write(k + "\n")
with open(os.path.join(HERE, "keys_provenance.txt"), "w") as f:
    prov = collections.Counter(keys.values())
    for tag,c in prov.most_common():
        f.write(f"{c:6d}  {tag}\n")
    f.write(f"\nTOTAL unique keys: {len(keys)}\n")

print(f"wrote {len(keys)} unique keys -> {out}")
prov = collections.Counter(keys.values())
for tag,c in prov.most_common():
    print(f"  {c:6d}  {tag}")
