"""ROUND 13 / B-04 — the Cicada seed dictionary.

Every entry is a BYTES object handed to a keystream generator. The dictionary is
built ONLY from material that exists inside this repo (solved-page plaintexts,
the 2012-2014 puzzle chain, the AN END hash, pp49-51's canon_256 payload, the PGP
fingerprints, the onion addresses, the lore book/author names) plus the obvious
numeric constants (3301 and friends, primes, dates).

Design rule: a seed must be something a puzzle author could plausibly have typed
or pasted. We therefore emit, for every text seed, the ASCII forms an author
would actually use (as-written, UPPER, lower, de-spaced) and, for every hex
string, BOTH its ASCII form and its RAW BYTE form.

`build()` returns a list of (label, seed_bytes) with duplicates removed, in a
deterministic order. `CORE_LABEL_PREFIXES` marks the higher-prior subset used
for the deeper (offset / per-page) stages.
"""
import os, re, binascii

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DK = os.path.join(ROOT, "data", "keys")
A18 = os.path.join(DK, "armada18")
A19 = os.path.join(DK, "armada19")

AN_END_HASH = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
               "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

PGP_FPR = "6D854CD7933322A601C3286D181F01E57A35090F"
PGP_KEYID = "7A35090F"
PGP_LONGID = "181F01E57A35090F"
FAKE_KEYID = "07CB82E3D0E8A26C"

# The 2012-2014 chain, as recorded across this repo's notes.
ONIONS = [
    "7z6bnpmiyxp2sgmn.onion",       # 2012 stage
    "sq6wmgv2zcsrix6t.onion",
    "auqgnxjtvdbll3pv.onion",
    "a4qgnxjtvdbll3pv.onion",
    "4l6uipnstbggwjyv.onion",
    "avowyfgl5lkzfj3n.onion",
    "fv7lyucmeozzd5j4.onion",
    "cginiziglyaobyph.onion",
    "cu343l33nqaekrnw.onion",
    "emiwp4muu2ktwknf.onion",
    "erwfcsdvx6pm2rsk.onion",
    "gbyh7znm6c7ezsmr.onion",
    "gy3hoy2zizvuzvdb.onion",
    "ky2khlqdf7qdznac.onion",
    "p7amjopgric7dfdi.onion",
    "pklmx2eeh6fjt7zf.onion",
    "q4utgdi2n4m4uim5.onion",
    "qw7mhchzvuq6f2mf.onion",
    "ut3qtzbrvs7dtvzp.onion",
    "wzwmcwmsk5cb7gjn.onion",
    "xsxnaksict6egxkq.onion",
    "y2wyuvrqraowagc5.onion",
    "5tdmziarqin6f4qw.onion",
    "5qcyeerbnina7esx.onion",
    "a6d7f6hjfg6eyrye.onion",
    "dxwd42hgpd7qrccm.onion",
    "167761adacic1033.onion",
    "1facdeebd0792a76.onion",
    "5ddf72edee76dfda.onion",
    "5ddf72edee76dfdd.onion",
    "767fbb5ca1de5cde.onion",
    "afafa1798984bafa.onion",
    "3301aidbwkwbdidiwbwfau.onion",
]

SLOGANS = [
    "THE PRIMES ARE SACRED",
    "THE TOTIENT FUNCTION IS SACRED",
    "ALL THINGS SHOULD BE ENCRYPTED",
    "EITHER THE WORDS OR THEIR NUMBERS",
    "THEIR NUMBERS ARE THE DIRECTION",
    "FOR ALL IS SACRED",
    "FIND YOUR TRUTH",
    "TEST THE KNOWLEDGE",
    "EXPERIENCE YOUR DEATH",
    "COMMAND YOUR OWN SELF",
    "DO FOUR UNREASONABLE THINGS EACH DAY",
    "AN END",
    "AN INSTRUCTION",
    "A WARNING",
    "SOME WISDOM",
    "INSTAR EMERGENCE",
    "THE LOSS OF DIVINITY",
    "WELCOME PILGRIM",
    "KNOW THIS",
    "THE KEY IS ALL AROUND YOU",
    "BEWARE FALSE PATHS",
    "GOOD LUCK",
    "THREE THREE ZERO ONE",
    "LIBER PRIMUS",
    "CICADA 3301",
    "WE ARE 3301",
    "PRIMUS",
    "THE INSTAR EMERGENCE",
    "SHED YOUR CIRCUMFERENCE",
    "FIND THE DIVINITY WITHIN AND EMERGE",
    "PARABLE",
    "A KOAN",
    "THE DEEP WEB",
    "PILGRIMAGE",
    "MOBIUS",
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE",
    "3301",
    "CICADA3301",
    "CICADA",
]

# Book titles / author names in the lore (Cicada's 2012-2014 book-code chain
# and the repo's own key corpus).
LORE = [
    "MABINOGION", "THE MABINOGION", "LADY CHARLOTTE GUEST",
    "AGRIPPA", "CORNELIUS AGRIPPA", "THREE BOOKS OF OCCULT PHILOSOPHY",
    "LIBER AL VEL LEGIS", "THE BOOK OF THE LAW", "ALEISTER CROWLEY",
    "THE KING IN YELLOW", "ROBERT W CHAMBERS", "SELF RELIANCE",
    "RALPH WALDO EMERSON", "EMERSON", "WILLIAM GIBSON", "AGRIPPA A BOOK OF THE DEAD",
    "THE LOSS OF INNOCENCE", "MOBY DICK", "HERMAN MELVILLE",
    "THE SECRET DOCTRINE", "BLAVATSKY", "MANLY P HALL", "LIBER 777",
    "THE BOOK OF LIES", "ELIPHAS LEVI", "DANTE", "INFERNO",
    "LOVECRAFT", "HP LOVECRAFT", "THE CALL OF CTHULHU", "NECRONOMICON",
    "KING ARTHUR", "PARZIVAL", "TIBERIUS", "AUGUSTINE",
    "PILGRIMS PROGRESS", "JOHN BUNYAN", "THE ODYSSEY", "HOMER",
    "MARCUS WANNER", "WIND", "3301ACTUAL",
]

NUM_STRINGS = [
    "3301", "1033", "0331", "13303", "33013301", "3301330133013301",
    "761", "845145127", "1595277641", "1033031", "3301.0",
    "509", "503", "311", "167", "1595277641", "845145127",
    "2012", "2013", "2014", "2016", "2017",
    "01042012", "04012012", "20120104", "20130104", "20140105",
    "1325635200",           # 2012-01-04 epoch
    "1357257600",           # 2013-01-04 epoch
    "1388880000",           # 2014-01-05 epoch
    "29", "3301029", "1033x3301",
]

# integers whose BIG-ENDIAN and DECIMAL byte forms are both plausible
NUM_INTS = [3301, 1033, 761, 29, 509, 503, 311, 167, 845145127, 1595277641,
            2012, 2013, 2014, 2016, 3, 3 * 3 * 0 + 1]

FIRST_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
                59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def _text_forms(s):
    """ASCII forms an author would plausibly type."""
    out = [s, s.upper(), s.lower()]
    ns = re.sub(r"\s+", "", s)
    if ns != s:
        out += [ns, ns.upper(), ns.lower()]
    return out


def build():
    seen, out = set(), []

    def add(label, b):
        if not isinstance(b, bytes):
            b = b.encode("utf-8", "ignore")
        if not b or b in seen:
            return
        seen.add(b)
        out.append((label, b))

    def add_text(label, s):
        for f in _text_forms(s):
            add(label, f)

    # ---- 1. slogans / koan phrases -------------------------------------
    for s in SLOGANS:
        add_text("slogan", s)

    # ---- 2. thematic keyword list (the repo's own solved-page keywords) --
    for line in _read(os.path.join(DK, "thematic.txt")).splitlines():
        w = line.strip()
        if w:
            add_text("thematic", w)

    # the canonical solved-page Vigenere keys, explicitly
    for w in ["DIVINITY", "FIRFUMFERENFE", "CIRCUMFERENCE", "FIRFUMFERENFE",
              "INSTAR", "WELCOME", "MOBIUS", "ADHERE", "PILGRIM", "TOTIENT",
              "PRIMES", "SACRED", "AENDA", "ANEND"]:
        add_text("solvedkey", w)

    # ---- 3. every word + every line of the solved LP plaintexts and the
    #        2012-2014 puzzle texts -------------------------------------
    corpus = ""
    for fn in ("cicada_koans_and_lp_sections.txt",
               "cicada_2012_2013_puzzle_texts.txt",
               "cicada_pgp_messages.txt"):
        corpus += _read(os.path.join(A18, fn)) + "\n"
    words = sorted(set(w for w in re.findall(r"[A-Za-z]{3,}", corpus)))
    for w in words:
        add("lp_word", w.upper())
        add("lp_word", w.lower())
    for line in sorted(set(l.strip() for l in corpus.splitlines())):
        if 4 <= len(line) <= 120:
            add_text("lp_line", line)

    # ---- 4. lore: book titles / author names ---------------------------
    for s in LORE:
        add_text("lore", s)
    # key-corpus filenames double as title/author tokens
    for d in (A18, A19):
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                stem = os.path.splitext(fn)[0]
                add("lore_file", stem)
                add("lore_file", stem.replace("_", " ").upper())
                add("lore_file", stem.replace("_", "").upper())

    # ---- 5. numbers: strings, decimal-bytes and big-endian ints --------
    for s in NUM_STRINGS:
        add("num_str", s)
    for n in NUM_INTS:
        add("num_dec", str(n))
        for w in (2, 4, 8):
            try:
                add("num_be", n.to_bytes(w, "big"))
                add("num_le", n.to_bytes(w, "little"))
            except OverflowError:
                pass
    # prime sequences
    for k in (5, 10, 15, 29):
        add("primes_csv", ",".join(str(p) for p in FIRST_PRIMES[:k]))
        add("primes_cat", "".join(str(p) for p in FIRST_PRIMES[:k]))
        add("primes_bytes", bytes(FIRST_PRIMES[:k]))
    add("primes_29", bytes(FIRST_PRIMES))

    # ---- 6. the AN END 512-bit hash ------------------------------------
    add("anend_hex", AN_END_HASH)
    add("anend_hex", AN_END_HASH.upper())
    add("anend_raw", binascii.unhexlify(AN_END_HASH))
    add("anend_raw_rev", binascii.unhexlify(AN_END_HASH)[::-1])
    add("anend_half", binascii.unhexlify(AN_END_HASH)[:32])
    add("anend_half", binascii.unhexlify(AN_END_HASH)[32:])

    # ---- 7. pp49-51 canon_256 payload (B-05's object) ------------------
    p = os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin")
    if os.path.exists(p):
        with open(p, "rb") as f:
            b = f.read()
        add("canon256_raw", b)
        add("canon256_rev", b[::-1])
        add("canon256_head32", b[:32])
        add("canon256_tail32", b[-32:])
        add("canon256_hex", binascii.hexlify(b).decode())
        add("canon256_hex", binascii.hexlify(b).decode().upper())
    p2 = os.path.join(ROOT, "analysis", "pp49_51", "canon_256_decpref.bin")
    if os.path.exists(p2):
        with open(p2, "rb") as f:
            add("canon256_decpref", f.read())

    # ---- 8. PGP identifiers --------------------------------------------
    for s in (PGP_FPR, PGP_KEYID, PGP_LONGID, FAKE_KEYID):
        add("pgp", s)
        add("pgp", s.lower())
        try:
            add("pgp_raw", binascii.unhexlify(s))
        except binascii.Error:
            pass
    add("pgp", "6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F")
    add("pgp", "Cicada 3301 (845145127)")

    # ---- 9. onion addresses --------------------------------------------
    for o in ONIONS:
        add("onion", o)
        add("onion", o.upper())
        add("onion", o.split(".")[0])
        add("onion", "http://" + o + "/")

    return out


# The higher-prior subset that gets the deeper offset / per-page stages.
CORE_LABEL_PREFIXES = ("slogan", "thematic", "solvedkey", "num_", "primes_",
                       "anend_", "canon256_", "pgp", "onion")


def core(entries):
    return [e for e in entries if e[0].startswith(CORE_LABEL_PREFIXES)]


if __name__ == "__main__":
    e = build()
    from collections import Counter
    c = Counter(l for l, _ in e)
    print(f"total seeds: {len(e)}   core: {len(core(e))}")
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {k:16s} {v}")
