"""Lane B1 - build the artifact-derived key set.

Every key carries a PROVENANCE tag naming the 2012-2016 Cicada artifact it came from,
so the sweep result is auditable against PA-3's inventory (../PA-3/ARTIFACT-INVENTORY.md).

Two classes:
  ALPHA  -> Vigenere keywords / running keys (letters only, C->F orthography variant added)
  NUMER  -> numeric strings used as repeating mod-29 additive keystreams

Source of record for verbatim text: analysis/armada_osint/artifacts/raw/{2012..2017}.md
(the locally-held scream314 year-by-year archive, 149 KB).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RAW = os.path.join(ROOT, "analysis", "armada_osint", "artifacts", "raw")


# --------------------------------------------------------------- curated ALPHA
# (tag, key-string, provenance)
CURATED_ALPHA = [
    # ---- Tier 3: published prose / names never used as a key ----
    ("2013-boot", "THEKEYISALLAROUNDYOU", "3301.iso boot screen final stage, 2013"),
    ("2013-boot", "THEKEYISALLAROUND", "3301.iso boot screen (short form)"),
    ("2013-boot", "KEYISALLAROUNDYOU", "3301.iso boot screen (short form)"),
    ("2013-boot", "ALLAROUNDYOU", "3301.iso boot screen (short form)"),
    ("2013-tcp", "RANDQUINEBASECODEKOANDHNEXTGOODBYE", "TCP-server spec command list, 2013"),
    ("2013-tcp", "QUINE", "TCP-server spec, 2013"),
    ("2013-tcp", "BASE", "TCP-server spec BASE29, 2013"),
    ("2013-tcp", "GOODBYE", "TCP-server spec response name, 2013"),
    ("2013-tcp", "WELCOMEOKERRORDATAGOODBYE", "TCP-server spec response-name table, 2013"),
    ("2013-koan", "SOLONGASYOUCANNOTGOBEYONDTHEMOUNTAIN",
     "TCP-spec KOAN example text, 2013"),
    ("2013-koan", "WHATAFINEMOUNTAINTHISIS", "TCP-spec KOAN, 2013"),
    ("2013-koan", "WHATISTHEWAY", "TCP-spec KOAN, 2013"),
    ("2013-koan", "THEWAY", "TCP-spec KOAN, 2013"),
    ("2013-koan", "MOUNTAIN", "TCP-spec KOAN, 2013"),
    ("2013-koan", "HERMIT", "TCP-spec KOAN, 2013"),
    ("2013-iso", "PRIMEECHO", "3301.iso usr_local_bin/prime_echo, 2013"),
    ("2013-iso", "SPLASH", "3301.iso BOOT/SPLASH.RLE, 2013"),
    ("2013-iso", "CICADOS", "Cicada OS / UA string CicaDOS, 2013-2014"),
    ("2013-iso", "FOLLY", "3301.iso tmp/folly, 2013"),
    ("2013-iso", "WISDOM", "3301.iso tmp/wisdom, 2013"),
    ("2013-iso", "FOLLYWISDOM", "3301.iso tmp/ pair, 2013"),
    ("2013-iso", "WISDOMFOLLY", "3301.iso tmp/ pair, 2013"),
    ("2013-mp3", "THEINSTAREMERGENCE", "761.mp3 ID3 title, 2013"),
    ("2013-mp3", "INSTAREMERGENCE", "761.mp3 ID3 title, 2013"),
    ("2013-mp3", "INTERCONNECTEDNESS", "onion5 Interconnectedness.mp3, 2014"),
    ("2013-q", "SELFREFERENTIAL", "p7amjopgric7dfdi 19-question answer option, 2013"),
    ("2013-q", "STRANGELOOP", "p7amjopgric7dfdi answer option, 2013"),
    ("2013-q", "GAMERULE", "p7amjopgric7dfdi answer option, 2013"),
    ("2013-q", "INDETERMINATE", "p7amjopgric7dfdi answer option, 2013"),
    ("2013-q", "MEANINGLESS", "p7amjopgric7dfdi answer option, 2013"),
    ("2013-q", "THEREISNOTRUTH", "p7amjopgric7dfdi question statement, 2013"),
    ("2013-q", "ALLTHINGSARETRUE", "p7amjopgric7dfdi question statement, 2013"),
    ("2013-q", "THISSENTENCEISFALSE", "p7amjopgric7dfdi question statement, 2013"),
    ("2013-q", "YOUCANNOTSTEPINTOTHESAMERIVERTWICE", "p7amjopgric7dfdi statement, 2013"),
    ("2013-q", "IAMTHEVOICEINSIDEMYHEAD", "p7amjopgric7dfdi statement, 2013"),
    ("2013-q", "THEONEWHOSEESTHEREFLECTION", "p7amjopgric7dfdi lake question, 2013"),
    ("2013-q", "REFLECTION", "p7amjopgric7dfdi lake question, 2013"),
    ("2013-ssss", "SHAMIRSSECRETSHARINGSCHEME", "2013 poster/SSSS chain"),
    ("2012-midi", "VERYGOODYOUHAVEPROVENTOBEMOSTDEDICATED", "2012 MIDI plaintext"),
    ("2012-midi", "GARDENBALLHOUSECATSHOREBACKHEADGALON", "2012 MIDI per-solver word list"),
    ("2012-midi", "HABITRES", "2012 habitres.midi filename"),
    ("2012-midi", "ASONGOFLIBERTY", "2012 MIDI second song = Blake, A Song of Liberty"),
    ("2012-midi", "LETTHECHORUSBEYOURGUIDETOTHEDEPTHS", "2012 MIDI hint"),
    ("2012-phone", "VERYGOODYOUHAVEDONEWELL", "2012 (214) 390-9608 recording"),
    ("2012-phone", "THEREARETHREEPRIMENUMBERSASSOCIATEDWITHTHEORIGINALFINALJPG",
     "2012 phone recording"),
    ("2012-phone", "MULTIPLYTHESETHREENUMBERSTOGETHER", "2012 phone recording"),
    ("2012-4chan", "WHOOOPS", "2012 m9sYK.jpg decoy image text"),
    ("2012-4chan", "VALETE", "2012 vjuNp.jpg final message"),
    ("2012-book", "THEMARRIAGEOFHEAVENANDHELL", "2012 hkdgl.png book code target"),
    ("2014-onion", "FOREVERYTHINGTHATLIVESISHOLY",
     "auqgnxjtvdbll3pv index.html, 2014 (Blake)"),
    ("2014-onion", "GOODWORK", "2014 three-JPEG columnar transposition output"),
    ("2014-onion", "ULTIMATETRUTHISTHEULTIMATEILLUSION", "2014 onion payload"),
    ("2014-onion", "JOINUSAT", "2014 onion payload"),
    ("2014-onion", "GODELESCHERBACH", "onion5 2014 book code source book"),
    ("2014-ua", "CICADAEEDITION", "UA 'Cicada/33.01 CicaDOS 1.033 E Edition', 2014"),
    ("2014-ua", "SEDITION", "UA 'Cic/DOS/ 1.033 S Edition', 2014"),
    ("2014-ua", "EEDITION", "UA 2014"),
    ("2016-msg", "THEPATHLIESEMPTY", "4gq25.jpg 2016 message"),
    ("2016-msg", "ITSWORDSARETHEMAP", "4gq25.jpg 2016 message"),
    ("2016-msg", "THEIRMEANINGISTHEROAD", "4gq25.jpg 2016 message"),
    ("2016-msg", "THEIRNUMBERSARETHEDIRECTION", "4gq25.jpg 2016 message"),
    ("2016-msg", "WORDSARETHEMAPMEANINGISTHEROADNUMBERSARETHEDIRECTION",
     "4gq25.jpg 2016 message, compressed"),
    ("2017-msg", "BEWAREFALSEPATHS", "2017-04-04 signed message"),
    ("2017-msg", "CICADAPG", "2017 PGP Version header 'CicadaPG v.3301'"),
    # ---- onion addresses (base32, letters only) - never fed ----
    ("2012-onion", "SQWMGVZCSRIXT", "sq6wmgv2zcsrix6t.onion, 2012 (digits stripped)"),
    ("2013-onion", "EMIWPMUUKTWKNF", "emiwp4muu2ktwknf.onion, 2013"),
    ("2013-onion", "XSXNAKSICTEGXKQ", "xsxnaksict6egxkq.onion, 2013"),
    ("2013-onion", "PKLMXEEHFJTZF", "pklmx2eeh6fjt7zf.onion, 2013"),
    ("2013-onion", "PAMJOPGRICDFDI", "p7amjopgric7dfdi.onion, 2013"),
    ("2013-onion", "YWYUVRQRAOWAGC", "y2wyuvrqraowagc5.onion, Dallas 2013"),
    ("2013-onion", "WZWMCWMSKCBGJN", "wzwmcwmsk5cb7gjn.onion, Okinawa 2013"),
    ("2013-onion", "QWMHCHZVUQFMF", "qw7mhchzvuq6f2mf.onion, Moscow 2013"),
    ("2013-onion", "LUIPNSTBGGWJYV", "4l6uipnstbggwjyv.onion, Little Rock 2013"),
    ("2013-onion", "ERWFCSDVXPMRSK", "erwfcsdvx6pm2rsk.onion, Annapolis 2013"),
    ("2013-onion", "GBYHZNMCEZSMR", "gbyh7znm6c7ezsmr.onion, Portland 2013"),
    ("2014-onion", "AUQGNXJTVDBLLPV", "auqgnxjtvdbll3pv.onion, 2014"),
    ("2014-onion", "CULNQAEKRNW", "cu343l33nqaekrnw.onion, 2014"),
    ("2014-onion", "FVLYUCMEOZZDJ", "fv7lyucmeozzd5j4.onion, 2014"),
    ("2014-onion", "AVOWYFGLLKZFJN", "avowyfgl5lkzfj3n.onion, 2014"),
    ("2014-onion", "QUTGDINMUIM", "q4utgdi2n4m4uim5.onion, 2014"),
    ("2014-onion", "UTQTZBRVSDTVZP", "ut3qtzbrvs7dtvzp.onion, 2014"),
    ("2014-onion", "KYKHLQDFQDZNAC", "ky2khlqdf7qdznac.onion, 2014 (the LP host)"),
    # ---- poster access-code letter pairs (never fed) ----
    ("2013-poster", "JDYFCRLMPXGHNR", "the 7 poster access-code letter prefixes, 2013"),
    ("2013-poster", "JDYFCRLMPXGH", "6 recovered poster prefixes, 2013"),
    # ---- filenames / identifiers ----
    ("2012-file", "CICADA", "845145127.com/cicada.jpg"),
    ("2013-file", "GEMATRIAPRIMUS", "gematria-primus.jpg filename, 2013"),
    ("2014-file", "LIBERPRIMUS", "the book title"),
]

# systematic C->F orthography variants (the author's demonstrated spelling, per
# FIRFUMFERENFE vs CIRCUMFERENCE), added automatically below.


# --------------------------------------------------------------- curated NUMER
CURATED_NUMER = [
    ("2013-poster-codes", "3789103213117167434717232911",
     "the 7 poster access codes JD/YF/CR/LM/PX/GH/NR, 2013"),
    ("2013-poster-ds", "13128211737861013111111113138311777971317617",
     "Dataset/Offset triplets from the 7 posters, 2013"),
    ("2013-gps", "330928179608265264196812773254557937653757860834747791922690863"
                 "3897784576486451455009212265251232478944849836745",
     "the 7 poster GPS coordinate digit strings, 2013"),
    ("2012-gps", "3301", "control marker"),
    ("2013-phones", "1205396330116265861033192823733011719428330112536551033"
                    "142499910331469251103",
     "the 7 poster phone numbers, 2013"),
    ("2013-tweet", "1231507051321", "the 2013 twitter handle @1231507051321"),
    ("2013-tweet2", "00650988", "2013 reactivation tweet Offset0 Skip0 Col65 Line988"),
    ("2013-tweet3", "3301006516", "2013 second reactivation tweet"),
    ("2012-book", "761526315410261526141361568421718191420582210823617263330"
                  "463247534920910511523953443843811920",
     "the 2012 OutGuess book-code number list (76 pairs), first-pass digits"),
    ("2013-boot-primes", "10333301", "3301.iso boot pauses at 1033 then 3301"),
    ("2013-ssss-1", "0241cc481a51fe77f91600f593c1db2ce9babd2626ea6e",
     "SSSS share 02 (Dallas), 2013 - hex digits"),
    ("2013-ssss-all",
     "024103760578070f0808b90982a9", "SSSS share index+first bytes, 2013"),
    ("2014-port", "5243", "2014 onion 'Port 5243'"),
    ("2014-hdr", "133331", "onion7 index.html title 133 / div 331, 2014"),
    ("2014-lm", "201404020833193", "onion7 Last-Modified 2014-04-02 08:33:19, 2014"),
    ("2013-cookies-idx", "167761", "the two 2013 cookie indices"),
]


def cf_variant(s):
    """The author's demonstrated C->F orthography (FIRFUMFERENFE)."""
    return s.replace("C", "F")


def hex_letters(s):
    """a-f hex letters of a hex string, uppercased -> a legal keyword."""
    return re.sub(r"[^A-Fa-f]", "", s).upper()


def auto_alpha_from_raw(min_len=6, max_len=40):
    """Auto-extract ALL-CAPS tokens and quoted short phrases from the held archive.

    This is the 'every key-shaped string' sweep required by the lane, on top of the
    curated list. Deliberately generous; deduped against the curated set later.
    """
    out = []
    for yr in ("2012", "2013", "2014", "2015", "2016", "2017"):
        p = os.path.join(RAW, yr + ".md")
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        # ALL-CAPS runs of >=4 letters (protocol names, banners, headers)
        for m in set(re.findall(r"\b[A-Z]{4,20}\b", txt)):
            if min_len <= len(m) <= max_len:
                out.append((f"auto-{yr}-caps", m, f"ALL-CAPS token in raw/{yr}.md"))
        # backtick-quoted identifiers, letters only
        for m in set(re.findall(r"`([A-Za-z0-9_.\-]{4,40})`", txt)):
            w = re.sub(r"[^A-Za-z]", "", m).upper()
            if min_len <= len(w) <= max_len:
                out.append((f"auto-{yr}-tick", w, f"backtick token `{m}` in raw/{yr}.md"))
    return out


def build():
    seen = set()
    alpha = []

    def add(tag, key, prov):
        key = re.sub(r"[^A-Z]", "", key.upper())
        if len(key) < 3 or key in seen:
            return
        seen.add(key)
        alpha.append({"tag": tag, "key": key, "prov": prov})

    for tag, k, prov in CURATED_ALPHA:
        add(tag, k, prov)
        v = cf_variant(k)
        if v != k:
            add(tag + "-cf", v, prov + " [C->F orthography variant]")
    # hex-letter keys from the SSSS shares / poster data blobs
    for tag, s, prov in CURATED_NUMER:
        hl = hex_letters(s)
        if len(hl) >= 6:
            add(tag + "-hexletters", hl[:40], prov + " [a-f letters only]")
    for tag, k, prov in auto_alpha_from_raw():
        add(tag, k, prov)

    numer = []
    nseen = set()
    for tag, s, prov in CURATED_NUMER:
        d = re.sub(r"[^0-9]", "", s)
        if len(d) < 3 or d in nseen:
            continue
        nseen.add(d)
        numer.append({"tag": tag, "digits": d, "prov": prov})
    return alpha, numer


if __name__ == "__main__":
    a, n = build()
    print(f"ALPHA keys: {len(a)}")
    print(f"NUMER streams: {len(n)}")
    for r in a[:20]:
        print("  ", r["tag"], r["key"][:40])
