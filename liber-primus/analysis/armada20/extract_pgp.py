#!/usr/bin/env python3
"""Extract clean English prose from Cicada's PGP-signed message bodies.
Build keyfiles for running-key attack (id=3, kind=keytext)."""
import os, re, glob

PGP = "/mnt/c/Users/dukot/projects/cicada3301/identity/pgp"
OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20"

def body(path):
    """Return text between SIGNED MESSAGE header and SIGNATURE block."""
    txt = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r"-----BEGIN PGP SIGNED MESSAGE-----(.*?)-----BEGIN PGP SIGNATURE-----",
                  txt, re.S)
    if not m:
        # plain .txt (path-lies-empty) -> grab the DECODED PLAINTEXT section
        m2 = re.search(r"DECODED PLAINTEXT\s*-+\s*(.*?)\s*GPG VERIFICATION", txt, re.S)
        return m2.group(1) if m2 else ""
    b = m.group(1)
    b = re.sub(r"^Hash:.*$", "", b, flags=re.M)
    return b

def letters(s):
    return re.sub(r"[^A-Za-z]", "", s)

# 1) the path-lies-empty decoded plaintext (most LP-themed prose)
path_lies = body(os.path.join(PGP, "2016-01-message-path-lies-empty.txt"))

# Collect prose-bearing messages (exclude pure-hex / pure-morse / coords / hash blocks).
# We keep ENGLISH prose only; for onion5 we strip the trailing hex dump.
order = [
    "2012-01-key-announcement.asc",
    "2012-01-key-in-front-of-you.asc",
    "2012-01-second-chance.asc",      # has prose lines
    "2012-01-book-code-poem.asc",     # poem + prose (numbers stripped anyway)
    "2012-01-end-of-puzzle.asc",
    "2012-01-final-message.asc",
    "2012-04-necrome-denial.asc",
    "2013-01-cicada-os-message.asc",
    "2013-01-opening-book-code.asc",  # riddle poem + prose
    "2013-01-telnet-hello.asc",
    "2014-01-onion-welcome.asc",
    "2014-01-final-message.asc",
    "2014-01-opening-book-code.asc",  # poem
    "2014-05-liber-primus-release.asc",
    "2015-07-planned-parenthood-denial.asc",
    "2017-04-final-message.asc",
    "2017-04-final-warning.asc",
]

bodies = {}
for f in order:
    bodies[f] = body(os.path.join(PGP, f))

# onion5: prose prefix only (before first hex run)
o5 = body(os.path.join(PGP, "2014-01-onion5-liber-primus.asc"))
o5_prose = re.split(r"[0-9a-f]{20,}", o5)[0]  # cut at first long hex run
bodies["2014-01-onion5-prose.asc"] = o5_prose

# Build combined prose corpus (all prose, chronological)
combined = "\n".join(bodies[f] for f in order) + "\n" + path_lies + "\n" + o5_prose

# Write keyfiles
def write(name, text):
    p = os.path.join(OUT, name)
    open(p, "w").write(text)
    return p, len(letters(text))

artifacts = []
artifacts.append(write("key_pgp_combined.txt", combined))
artifacts.append(write("key_pgp_path_lies.txt", path_lies))
# also: combined repeated to guarantee coverage of longest page (~277) - it already is long
# Individual longer prose messages, padded by self-concat to reach >278 letters if needed
for f in ["2012-04-necrome-denial.asc","2015-07-planned-parenthood-denial.asc",
          "2012-01-end-of-puzzle.asc","2012-01-final-message.asc",
          "2013-01-opening-book-code.asc","2012-01-book-code-poem.asc"]:
    t = bodies[f]
    # repeat to ensure >= 320 letters for full page coverage
    while len(letters(t)) < 320:
        t = t + "\n" + bodies[f]
    artifacts.append(write("key_" + f.replace(".asc",".txt"), t))

print("Combined corpus letter count:", len(letters(combined)))
print()
for p, n in artifacts:
    print(f"{n:6d}  {p}")
