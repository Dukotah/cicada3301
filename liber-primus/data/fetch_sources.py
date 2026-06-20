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
    print("done.")
