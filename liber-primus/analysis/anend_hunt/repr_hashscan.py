#!/usr/bin/env python3
"""
AN-END hash hunt — address-free content hash-scan (REPRESENTATION space).

The AN END page (LP2 p56) states: "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT
HASHES TO: 36367763...c2a8b4. IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS
PAGE." It gives a 512-bit content hash but NO address.

Prior work (blake_closure / iter-6) hashed every held blob's RAW BYTES against the
target across all major 512-bit digests -> NULL. This script attacks the axis that
was never covered: the TARGET IS A "PAGE", so the intended preimage is plausibly a
text/normalized representation of an HTML page, not its raw on-disk bytes. We scan
the correctly-targeted local Cicada 2014 onion corpus (iBotPeaches capture of
onion1-7 + extras) plus the held onion/wiki HTML and the decrypted AN-END/PARABLE
text, across many representations x candidate algorithms.

This is address-free: it does NOT assume we know the target's onion address (we
don't — it is gated behind solving LP2). It only asks whether any page we ALREADY
HOLD is the pre-image under some representation. Honest expected result: NULL
(extends the standing verdict); a HIT would be the biggest possible win.
"""
import hashlib, re, os, sys, html, glob

TARGET = "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4"

# Candidate algorithms named by the primary source (KEY-HINT-RESEARCH lead #2):
# SHA-512, BLAKE-512, BLAKE2b.  hashlib provides sha512, sha3_512, blake2b(512).
# BLAKE-512 (original) + Skein/Whirlpool/Streebog were KAT-tested vs RAW blobs by
# prior work (null); here we cover the representation axis with the available algos.
def algos(b):
    return {
        "sha512":   hashlib.sha512(b).hexdigest(),
        "sha3_512": hashlib.sha3_512(b).hexdigest(),
        "blake2b512": hashlib.blake2b(b, digest_size=64).hexdigest(),
    }

def representations(raw):
    """Yield (label, bytes) for many plausible 'page content' normalizations."""
    yield ("raw", raw)
    # text decodings
    try:
        t = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            t = raw.decode("latin-1")
        except Exception:
            return
    yield ("utf8_text", t.encode("utf-8"))
    yield ("text_stripCR", t.replace("\r\n", "\n").encode("utf-8"))
    yield ("text_noTrailNL", t.rstrip("\n").encode("utf-8"))
    yield ("text_stripws", t.strip().encode("utf-8"))
    # HTML -> visible text
    notag = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", t)
    notag = re.sub(r"(?s)<[^>]+>", " ", notag)
    notag = html.unescape(notag)
    yield ("html_text", notag.encode("utf-8"))
    collapsed = re.sub(r"\s+", " ", notag).strip()
    yield ("html_text_collapsed", collapsed.encode("utf-8"))
    yield ("html_text_collapsed_upper", collapsed.upper().encode("utf-8"))
    # alnum/upper only (Cicada plaintext style)
    alnum = re.sub(r"[^A-Za-z0-9]", "", t)
    yield ("alnum", alnum.encode("utf-8"))
    yield ("alnum_upper", alnum.upper().encode("utf-8"))
    letters = re.sub(r"[^A-Za-z]", "", t).upper()
    yield ("letters_upper", letters.encode("utf-8"))

def scan_file(path):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except Exception as e:
        return []
    hits = []
    for label, b in representations(raw):
        for alg, dig in algos(b).items():
            if dig == TARGET:
                hits.append((path, label, alg, dig))
    return hits

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(root, "..", "..", ".."))
    lp = os.path.join(repo, "liber-primus")
    globs = [
        os.path.join(lp, "analysis/armada_osint/onions_ibotpeaches/*"),
        os.path.join(lp, "analysis/stones/onion-archive/*"),
        os.path.join(lp, "analysis/armada_osint/artifacts/*"),
        os.path.join(lp, "data/scream314_lp.md"),
        os.path.join(lp, "data/keys/solved_plaintext.txt"),
    ]
    files = []
    for g in globs:
        files.extend(sorted(p for p in glob.glob(g) if os.path.isfile(p)))
    # also: the decrypted AN-END + PARABLE text, as strings
    extra_strings = {
        "AN_END_msg": "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO: "
                      + TARGET + " IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE.",
    }

    print(f"TARGET = {TARGET}")
    print(f"algorithms: sha512, sha3_512, blake2b512")
    print(f"files scanned: {len(files)}")
    n_pairs = 0
    all_hits = []
    for p in files:
        try:
            sz = os.path.getsize(p)
        except OSError:
            continue
        if sz > 30_000_000:  # skip absurdly large
            print(f"  skip (large {sz}): {os.path.relpath(p, repo)}")
            continue
        h = scan_file(p)
        # count representation x algo pairs for the correction denominator
        with open(p, "rb") as f:
            raw = f.read()
        n_pairs += sum(1 for _ in representations(raw)) * 3
        if h:
            all_hits.extend(h)
    for name, s in extra_strings.items():
        for label, b in representations(s.encode("utf-8")):
            for alg, dig in algos(b).items():
                n_pairs += 1
                if dig == TARGET:
                    all_hits.append((name, label, alg, dig))

    print(f"(representation x algo) tests run: {n_pairs}")
    if all_hits:
        print("\n!!!!! HIT !!!!!")
        for p, label, alg, dig in all_hits:
            print(f"  {alg}  repr={label}  file={p}")
    else:
        print("\nRESULT: CLEAN NULL — no held Cicada page/artifact hashes to the AN-END "
              "target under any tested representation x algorithm.")
        print("Consistent with prior raw-blob null; extends it across the representation axis.")

if __name__ == "__main__":
    main()
