"""Round 16 / lane P3 - assemble the two never-swept PUBLIC pad families.

(a) PRINTED RANDOM-NUMBER TABLES.  RAND's *A Million Random Digits with 100,000 Normal
    Deviates* (1955) exists precisely so two parties can share randomness without sharing
    a seed: a physical one-time pad with a permanent public record.

(b) CICADA'S OWN PUBLISHED HIGH-ENTROPY BYTES, USED AS A PAD.  Round 12's A1 swept the
    author's *binaries* (CicadaOS).  Nobody has swept the bytes 3301 published to the
    world: the PGP signature blobs, the public-key packets, the 2014 hash block, the
    hex-dumped JPEG/MP3 payloads, the onion addresses, canon_256.  Prior work used some of
    these as ciphertext or as keytext; using the signature bytes as a PAD is untried.
    ("The key has always been right in front of your eyes." - 3301, 2012-01.)

Reads corpus/A-primary-artifacts/pgp/ READ ONLY.  Writes only into P3_tables/data/.

Regenerate:
    python liber-primus/analysis/round16/P3_tables/build_pads.py
(the RAND digits are fetched once; see data/.gitignore)
"""
import os, sys, re, json, base64, hashlib, zipfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(HERE, "data")
PADS = os.path.join(DATA, "pads")
PGP = os.path.join(REPO, "corpus", "A-primary-artifacts", "pgp")
LP = os.path.join(REPO, "liber-primus")

RAND_URL = ("https://www.rand.org/content/dam/rand/pubs/monograph_reports/"
            "MR1418/MR1418.digits.txt.zip")
RAND_ZIP_SHA256 = "9083cef4571f3a79729aaf9f4d3cdb946c26033b77b4f929155ca067ad0d8d8b"
RAND_TXT_SHA256 = "657622b6eba115bec547ddd83093d259b370294ae6efaa48f5c4e3b3690b862e"

# 3301's onion addresses in PUBLICATION ORDER, taken from the dated OSINT transcripts in
# liber-primus/analysis/armada_osint/artifacts/raw/{2012,2013,2014}.md (first-appearance
# order inside each dated file).
ONIONS_PUB = [
    "sq6wmgv2zcsrix6t", "cginiziglyaobyph",                                   # 2012
    "emiwp4muu2ktwknf", "xsxnaksict6egxkq", "pklmx2eeh6fjt7zf",
    "gbyh7znm6c7ezsmr", "y2wyuvrqraowagc5", "wzwmcwmsk5cb7gjn",
    "qw7mhchzvuq6f2mf", "4l6uipnstbggwjyv", "erwfcsdvx6pm2rsk",
    "p7amjopgric7dfdi",                                                        # 2013
    "auqgnxjtvdbll3pv", "cu343l33nqaekrnw", "fv7lyucmeozzd5j4",
    "avowyfgl5lkzfj3n", "q4utgdi2n4m4uim5", "ut3qtzbrvs7dtvzp",
    "ky2khlqdf7qdznac",                                                        # 2014
]
# later 3301 onions (2016-2017 era); appended for the "_ext" variant
ONIONS_LATE = ["lwplxqzvmgu43uff", "yniir5c6cmuwslfl", "5fpp2orjc2ejd2g7",
               "rjzdqt4z3z3xo73h", "2lol7ha4j442rqeg", "gy3hoy2zizvuzvdb"]

STUB_MAX = 400          # GitHub "429" stubs are 199 bytes; anything tiny is not an armor


# ------------------------------------------------------------------ helpers
def sha256(b):
    return hashlib.sha256(b).hexdigest()


def armor_blocks(text, kind):
    """Yield (b64_text, binary) for every '-----BEGIN PGP <kind>-----' block."""
    pat = re.compile(r"-----BEGIN PGP " + kind + r"-----(.*?)-----END PGP " + kind + r"-----",
                     re.S)
    for m in pat.finditer(text):
        body = m.group(1)
        lines = [ln.strip() for ln in body.splitlines()]
        b64 = []
        for ln in lines:
            if not ln or ":" in ln or ln.startswith("="):
                continue                     # armor headers and the CRC24 line
            b64.append(ln)
        s = "".join(b64)
        try:
            raw = base64.b64decode(s)
        except Exception:
            continue
        yield s, raw


def hex_blocks(text):
    """Long lower-case hex lines as published (the JPEG / MP3 / hash-block dumps)."""
    out = []
    for ln in text.splitlines():
        ln = ln.strip()
        if len(ln) >= 40 and re.fullmatch(r"[0-9a-f]+", ln):
            out.append(ln)
    return out


def fetch_rand():
    txt = os.path.join(DATA, "digits.txt")
    if not os.path.exists(txt):
        os.makedirs(DATA, exist_ok=True)
        zp = os.path.join(DATA, "rand.zip")
        req = urllib.request.Request(RAND_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180) as r, open(zp, "wb") as f:
            f.write(r.read())
        with zipfile.ZipFile(zp) as z:
            z.extract("digits.txt", DATA)
    b = open(txt, "rb").read()
    assert sha256(b) == RAND_TXT_SHA256, "RAND digits.txt sha256 mismatch"
    return b


# ------------------------------------------------------------------ build
def main():
    os.makedirs(PADS, exist_ok=True)
    pads, prov = {}, {}

    # ---------- family (a): the printed table -------------------------------
    raw = fetch_rand()
    # digits.txt is 20,000 lines of "NNNNN" line-number + 10 five-digit groups.
    # The RANDOM digits are everything after the 5-digit line number.
    digits = []
    for ln in raw.decode("ascii").splitlines():
        body = ln[5:]                                    # strip the printed line number
        digits.append("".join(ch for ch in body if ch.isdigit()))
    d = "".join(digits)
    assert len(d) == 1_000_000, len(d)
    assert d[:20] == "10097325337652013586", d[:20]      # published first line, verified
    pads["rand_digits"] = d.encode("ascii")
    prov["rand_digits"] = ("RAND MR1418 A Million Random Digits (1955), the 1,000,000 "
                           "random digits with printed line numbers stripped; "
                           "first line cross-checked against Wikipedia/independent source")
    pads["rand_digits_raw_file"] = raw
    prov["rand_digits_raw_file"] = ("the RAND datafile verbatim, line numbers and layout "
                                    "included - what a copy-paste actually yields")

    # ---------- family (b): Cicada's published high-entropy bytes -----------
    msgs = sorted(os.listdir(os.path.join(PGP, "messages")))
    sig_bin, sig_b64, hexchunks, msg_used = [], [], [], []
    for name in msgs:
        p = os.path.join(PGP, "messages", name)
        n = os.path.getsize(p)
        if n < STUB_MAX and n <= 250:
            continue                                     # 199-byte GitHub 429 stubs
        t = open(p, encoding="utf-8", errors="ignore").read()
        got = list(armor_blocks(t, "SIGNATURE"))
        for s, b in got:
            sig_b64.append(s)
            sig_bin.append(b)
        hx = hex_blocks(t)
        if hx:
            hexchunks.append((name, "".join(hx)))
        if got:
            msg_used.append(name)

    pads["cicada_sigs_bin_pub"] = b"".join(sig_bin)
    pads["cicada_sigs_bin_rev"] = b"".join(reversed(sig_bin))
    pads["cicada_sigs_b64_pub"] = "".join(sig_b64).encode("ascii")
    pads["cicada_sigs_b64_rev"] = "".join(reversed(sig_b64)).encode("ascii")
    for k in ("cicada_sigs_bin_pub", "cicada_sigs_bin_rev",
              "cicada_sigs_b64_pub", "cicada_sigs_b64_rev"):
        prov[k] = (f"{len(sig_bin)} PGP signature packets from "
                   f"{len(msg_used)} signed 3301 messages, "
                   + ("publication (chronological filename) order"
                      if k.endswith("pub") else "reverse publication order")
                   + (" - de-armoured binary" if "_bin_" in k else " - base64 armor text"))

    # keys
    keydir = os.path.join(PGP, "keys")
    for kn in sorted(os.listdir(keydir)):
        p = os.path.join(keydir, kn)
        if os.path.getsize(p) <= 250:
            continue
        t = open(p, encoding="utf-8", errors="ignore").read()
        blocks = list(armor_blocks(t, "PUBLIC KEY BLOCK"))
        if not blocks:
            continue
        tag = ("openpgp" if "openpgp.org" in kn else
               "ubuntu" if "ubuntu" in kn else "local")
        b64 = "".join(s for s, _ in blocks)
        bb = b"".join(b for _, b in blocks)
        pads[f"cicada_key_{tag}_bin"] = bb
        pads[f"cicada_key_{tag}_b64"] = b64.encode("ascii")
        prov[f"cicada_key_{tag}_bin"] = f"3301 public key packet bytes from {kn}"
        prov[f"cicada_key_{tag}_b64"] = f"3301 public key ASCII armor text from {kn}"

    # the 2014 Liber Primus hash block, as published hex text and as bytes
    hb = dict(hexchunks).get("2014-01-liber-primus-hash-block.asc", "")
    if hb:
        pads["lp_hashblock_hextext"] = hb.encode("ascii")
        pads["lp_hashblock_bytes"] = bytes.fromhex(hb[:len(hb) // 2 * 2])
        prov["lp_hashblock_hextext"] = "2014-01 signed hash block, hex characters as published"
        prov["lp_hashblock_bytes"] = "2014-01 signed hash block, hex decoded to bytes"

    # every published hex dump (JPEGs, the MP3/ID3 corpus), publication order + reverse
    hx_all = "".join(s for _, s in hexchunks)
    pads["cicada_hexdumps_text_pub"] = hx_all.encode("ascii")
    pads["cicada_hexdumps_bytes_pub"] = bytes.fromhex(hx_all[:len(hx_all) // 2 * 2])
    rev = "".join(s for _, s in reversed(hexchunks))
    pads["cicada_hexdumps_bytes_rev"] = bytes.fromhex(rev[:len(rev) // 2 * 2])
    for k in ("cicada_hexdumps_text_pub", "cicada_hexdumps_bytes_pub",
              "cicada_hexdumps_bytes_rev"):
        prov[k] = ("all long hex lines published inside signed 3301 messages "
                   f"({', '.join(n for n, _ in hexchunks)}), "
                   + ("reverse" if k.endswith("rev") else "publication") + " order")

    # onion addresses (base32) as text and decoded
    def onion_pads(names, tag):
        s = "".join(names)
        pads[f"onions_{tag}_text"] = s.encode("ascii")
        b32 = s.upper()
        b32 += "=" * (-len(b32) % 8)
        pads[f"onions_{tag}_bin"] = base64.b32decode(b32)
        prov[f"onions_{tag}_text"] = f"{len(names)} 3301 .onion addresses, base32 text, {tag}"
        prov[f"onions_{tag}_bin"] = f"{len(names)} 3301 .onion addresses, base32-decoded, {tag}"

    onion_pads(ONIONS_PUB, "pub")
    onion_pads(list(reversed(ONIONS_PUB)), "rev")
    onion_pads(ONIONS_PUB + ONIONS_LATE, "ext")

    # canon_256 / magic-square material already in-repo
    c256 = os.path.join(LP, "analysis", "pp49_51", "canon_256.bin")
    if os.path.exists(c256):
        pads["canon_256"] = open(c256, "rb").read()
        prov["canon_256"] = "liber-primus/analysis/pp49_51/canon_256.bin"

    # the 56 LP2 page JPEGs 3301 published on onion7 (ky2khlqdf7qdznac.onion, May 2014),
    # in page order.  These are the highest-volume high-entropy bytes 3301 ever published
    # and they are literally the file the runes arrived in - "the key has always been
    # right in front of your eyes".  Paths + SHA-256 come from the capsule MANIFEST.
    cap = os.path.join(LP, "handoff", "capsule", "MANIFEST.json")
    if os.path.exists(cap):
        items = json.load(open(cap))["items"]
        pages = sorted((it for it in items if it["id"].startswith("images.onion7.p")),
                       key=lambda it: it["id"])
        blobs = []
        for it in pages:
            fp = os.path.join(REPO, it["path"])
            if os.path.exists(fp):
                blobs.append(open(fp, "rb").read())
        if len(blobs) == len(pages) and blobs:
            pads["lp_pages_jpeg_pub"] = b"".join(blobs)
            pads["lp_pages_jpeg_rev"] = b"".join(reversed(blobs))
            prov["lp_pages_jpeg_pub"] = (f"{len(blobs)} onion7 LP2 page JPEGs "
                                         "(capsule images.onion7.p00-p55), page order")
            prov["lp_pages_jpeg_rev"] = (f"the same {len(blobs)} page JPEGs, "
                                         "reverse page order")

    # ---------- the grand concatenation: everything 3301 published ----------
    order = [pads.get("cicada_sigs_bin_pub", b""),
             pads.get("cicada_key_openpgp_bin", b""),
             pads.get("cicada_key_ubuntu_bin", b""),
             pads.get("lp_hashblock_bytes", b""),
             pads.get("cicada_hexdumps_bytes_pub", b""),
             pads.get("onions_pub_bin", b""),
             pads.get("canon_256", b"")]
    pads["cicada_all_pub"] = b"".join(order)
    pads["cicada_all_rev"] = b"".join(reversed(order))
    prov["cicada_all_pub"] = ("sigs + keys + hash block + hex dumps + onions + canon_256, "
                              "publication order")
    prov["cicada_all_rev"] = "the same seven components in reverse order"

    # ---------- write + manifest -------------------------------------------
    man = []
    for name in sorted(pads):
        b = pads[name]
        if not b:
            continue
        path = os.path.join(PADS, name + ".bin")
        with open(path, "wb") as f:
            f.write(b)
        man.append({"name": name, "bytes": len(b), "sha256": sha256(b),
                    "source": prov.get(name, ""),
                    "keys_full_stream": len(b) >= 12956})
    out = {"generated_by": "P3_tables/build_pads.py",
           "n_pads": len(man),
           "note": ("a pad shorter than 12,956 keystream symbols cannot key the whole "
                    "unsolved stream; those are swept against the head window only"),
           "pads": man}
    with open(os.path.join(HERE, "pads_manifest.json"), "w") as f:
        json.dump(out, f, indent=1)
    for r in man:
        print(f"{r['name']:<32} {r['bytes']:>10} B  full={r['keys_full_stream']}")
    print(f"\n{len(man)} pads -> {PADS}")


if __name__ == "__main__":
    main()
