"""Fetch the third-party transcription sources used by the cross-verification
and structure analyses (gitignored, so a fresh clone / CI can pull them on demand).

Downloads to liber-primus/data/sources/:
  - rtkd_master.txt              (rtkd/iddqd 2017 community-root transcription)
  - relikd_<chunk>.txt x11       (relikd/LiberPrayground per-page chunks)

Stdlib only (urllib), so it runs in CI without curl. Idempotent: skips files
already present unless --force. Call ensure_sources() programmatically.
"""
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sources")

RTKD_URL = ("https://raw.githubusercontent.com/rtkd/iddqd/master/"
            "liber-primus__transcription--master/liber-primus__transcription--master.txt")
RELIKD_BASE = "https://raw.githubusercontent.com/relikd/LiberPrayground/master/pages/"
RELIKD_CHUNKS = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32",
                 "p33-39", "p40-53", "p54-55", "p56_an_end", "p57_parable"]

FILES = {"rtkd_master.txt": RTKD_URL}
FILES.update({f"relikd_{c}.txt": f"{RELIKD_BASE}{c}.txt" for c in RELIKD_CHUNKS})


def _get(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    with open(dst, "wb") as f:
        f.write(data)
    return len(data)


# --- R32 / X1: key corpora the nine-register panel (round19/I2, round32/I2) needs --------------------
# Round 32 I2 found data/keys/welsh/welsh_mabinogion.txt was never fetched by this script (the panel
# could not be rebuilt on a fresh clone). The ORIGINAL corpus (524,561 B, Middle-Welsh Mabinogion,
# sha 4b3fd926...) is NOT recoverable from here; I2 used a SUBSTITUTE of modern Welsh prose from four
# Project Gutenberg texts (716,409 chars after boilerplate strip). Panel numbers built from it are a
# sibling of, not identical to, round19/I2's. Pass --welsh to fetch it (opt-in; ~1 MB).
WELSH_GUTENBERG_IDS = [3680, 57981, 56275, 67424]   # Cartrefi Cymru, Brethyn Cartref, I'r Aifft Ac Yn Ol, Nedw
WELSH_DST = os.path.join(os.path.dirname(HERE), "data", "keys", "welsh", "welsh_mabinogion.txt")


def _strip_gutenberg(txt):
    s = txt.find("*** START")
    if s != -1:
        s = txt.find("\n", s) + 1
    else:
        s = 0
    e = txt.find("*** END")
    return txt[s:e if e != -1 else len(txt)]


def ensure_welsh_substitute(force=False, verbose=True):
    """Rebuild the I2 Welsh (CY) substitute corpus from Project Gutenberg (see note above)."""
    if os.path.exists(WELSH_DST) and not force:
        return WELSH_DST
    os.makedirs(os.path.dirname(WELSH_DST), exist_ok=True)
    parts = []
    for gid in WELSH_GUTENBERG_IDS:
        # R35-P1: the /files/N/N-0.txt form is the byte-exact source of the Round 19 corpora (recorded
        # hashes 0f1a83cb... for #10, 80dc6f0d... for #5160); cache/epub/pgN.txt serves a re-issued text.
        url = f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt"
        req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
        with urllib.request.urlopen(req, timeout=60) as r:
            parts.append(_strip_gutenberg(r.read().decode("utf-8", "replace")))
    with open(WELSH_DST, "w", encoding="utf-8", newline="") as f:
        f.write("".join(parts))
    if verbose:
        print(f"  built Welsh substitute corpus ({sum(map(len, parts))} chars) -> {WELSH_DST}")
    return WELSH_DST


def ensure_sources(force=False, verbose=True):
    """Download any missing source files; return the sources dir path."""
    os.makedirs(SRC, exist_ok=True)
    for name, url in FILES.items():
        dst = os.path.join(SRC, name)
        if os.path.exists(dst) and not force:
            continue
        n = _get(url, dst)
        if verbose:
            print(f"  fetched {name} ({n} B)")
    return SRC


if __name__ == "__main__":
    force = "--force" in sys.argv
    print(f"fetching {len(FILES)} source files -> {SRC}")
    ensure_sources(force=force)
    if "--welsh" in sys.argv:
        ensure_welsh_substitute(force=force)
    print("done.")
