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
        # R35-X1: this is the Round 32 SUBSTITUTE recipe (cache/epub). R35-P1 had changed it to the
        # /files/N/N-0.txt form, which yields ~20 KB different bytes (781,166 vs 761,024 B measured);
        # that URL form is the byte-exact source for the Round 19 KJV/Mabinogion only (ensure_r19_corpora).
        url = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"
        req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
        with urllib.request.urlopen(req, timeout=60) as r:
            parts.append(_strip_gutenberg(r.read().decode("utf-8", "replace")))
    with open(WELSH_DST, "w", encoding="utf-8", newline="") as f:
        f.write("".join(parts))
    if verbose:
        print(f"  built Welsh substitute corpus ({sum(map(len, parts))} chars) -> {WELSH_DST}")
    return WELSH_DST


# --- R35 / P1 + X1: the two Round 19 corpora that ARE byte-recoverable (raw bytes, no stripping) --------
# Recorded in analysis/round19/I2/out_build.json. The third (Welsh CY, 4b3fd926..., 524,561 B) is not.
R19_CORPORA = {
    "kjv.txt": ("https://www.gutenberg.org/files/10/10-0.txt",
                "0f1a83cbcdc1d3fae6bcc3daaa496d4fa723fcce9526e84e20df12ae33fda986", 4436268),
    os.path.join("keys", "mabinogion.txt"): ("https://www.gutenberg.org/files/5160/5160-0.txt",
                "80dc6f0d8efc8398a2d1cc8cdf17237020c881cf4fbd2412dfa37ec8be19a5ed", 617362),
}


def ensure_r19_corpora(force=False, verbose=True):
    """Fetch data/kjv.txt and data/keys/mabinogion.txt byte-exact (sha256-verified); raises on mismatch."""
    import hashlib
    for rel, (url, sha, n) in R19_CORPORA.items():
        dst = os.path.join(HERE, rel)
        if os.path.exists(dst) and not force and hashlib.sha256(open(dst, "rb").read()).hexdigest() == sha:
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if hashlib.sha256(data).hexdigest() != sha or len(data) != n:
            raise RuntimeError(f"{url}: sha/size differs from the recorded Round 19 corpus (mirror re-issued?)")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
        if verbose:
            print(f"  fetched {rel} ({n} B, sha verified)")


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
    if "--r19" in sys.argv:
        ensure_r19_corpora(force=force)
    if "--welsh" in sys.argv:
        ensure_welsh_substitute(force=force)
    print("done.")
