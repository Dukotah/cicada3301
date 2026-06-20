"""Build the canonical, provenance-verified, machine-readable LP2 dataset.

One JSON anyone can build on: gematria table, per-page runes + transliteration,
the VERIFIED image hashes (sha1 confirmed == archive.org onion7), the solved-page
key reference, and the ruled-out registry. Run: python dataset/build_dataset.py
"""
import os, sys, json, hashlib, re

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp  # noqa: E402

KRIS = os.path.join(ROOT, "data", "krisyotam_runes.txt")
XML = os.path.join(ROOT, "data", "onion7", "files.xml")
IMGDIR = os.path.join(ROOT, "data", "relikd")  # SHA1-verified == onion7 originals


def pub_hashes():
    if not os.path.exists(XML):
        return {}
    x = open(XML, encoding="utf-8", errors="replace").read()
    h = {}
    for m in re.finditer(r'<file name="([^"]+\.jpg)"[^>]*>(.*?)</file>', x, re.S):
        name, body = m.group(1), m.group(2)
        sha = re.search(r"<sha1>([0-9a-f]+)</sha1>", body)
        md5 = re.search(r"<md5>([0-9a-f]+)</md5>", body)
        sz = re.search(r"<size>(\d+)</size>", body)
        h[name] = {"sha1": sha.group(1) if sha else None,
                   "md5": md5.group(1) if md5 else None,
                   "size": int(sz.group(1)) if sz else None}
    return h


def main():
    pages_raw = [s for s in open(KRIS, encoding="utf-8").read().split("%")]
    pub = pub_hashes()
    pages = []
    for i, seg in enumerate(pages_raw):
        runes = "".join(c for c in seg if c in gp.RUNE_TO_IDX)
        if not runes:
            continue
        onion = f"{i}.jpg"
        local = os.path.join(IMGDIR, f"p{i}.jpg")
        img_sha1 = hashlib.sha1(open(local, "rb").read()).hexdigest() if os.path.exists(local) else None
        rec = {
            "page": i,
            "onion7_file": onion,
            "n_runes": len(runes),
            "runes": runes,
            "translit": "".join(gp.RUNE_TO_TRANS[c] for c in runes),
            "indices": gp.runes_to_indices(runes),
            "status": "unsolved",
            "image": {
                "sha1": img_sha1,
                "published_sha1": pub.get(onion, {}).get("sha1"),
                "published_md5": pub.get(onion, {}).get("md5"),
                "size": pub.get(onion, {}).get("size"),
                "provenance_verified": bool(img_sha1 and pub.get(onion, {}).get("sha1") == img_sha1),
            },
        }
        pages.append(rec)

    data = {
        "meta": {
            "title": "Cicada 3301 Liber Primus — unsolved LP2 corpus (provenance-verified)",
            "source_transcription": "rtkd/iddqd 2017 lineage (krisyotam copy); all community lineages verified rune-identical (analysis/transcription)",
            "image_provenance": "relikd images are SHA1-identical to archive.org item ky2khlqdf7qdznac.onion (the onion7 LP2 dump); see analysis/stego/provenance.json",
            "numbering": "onion7 file numbers; 0-55 unsolved. AN END (56) and PARABLE (57) are solved.",
            "verify_first": "tests/validate.py reproduces all solved pages from this gematria+cipher rig",
            "note": "ciphertext is one-time-pad-class; see SOLVERS-DOSSIER.md",
        },
        "gematria": [{"index": i, "rune": r, "translit": t, "prime": p}
                     for (i, r, t, p) in gp.GEMATRIA],
        "interrupter_rune": gp.INTERRUPTER,
        "pages": pages,
        "solved_pages_reference": {
            "01_A_WARNING": {"method": "atbash"},
            "05_SOME_WISDOM": {"method": "plaintext transliteration"},
            "06-09_A_KOAN": {"method": "atbash + caesar shift -3"},
            "03-04_WELCOME": {"method": "vigenere", "key": "DIVINITY", "note": "F-interrupters, subtract"},
            "14-15_CIRCUMFERENCE": {"method": "vigenere", "key": "FIRFUMFERENFE (=CIRCUMFERENCE, F-spelled)"},
            "56_AN_END": {"method": "totient(prime) keystream, F-interrupters", "note": "contains SHA-512-class hash 36367763...c2a8b4"},
            "57_PARABLE": {"method": "plaintext transliteration"},
        },
        "ruled_out": [
            "periodic keys len 1-40 (Friedman/column-freq, both dirs, +atbash)",
            "running keys from referenced texts + solved plaintext",
            "number-theoretic keystreams (primes, totient, iterated totient, gaps, cumsums, page-seeded, fibonacci)",
            "plaintext & ciphertext autokey",
            "first-difference / integral inversion",
            "page-on-page key reuse / in-depth",
            "fractionation (bifid/Polybius)",
            "substitution / homophonic",
            "transposition-only (and transposition-validity: file order is native)",
            "block/permutation/Lehmer decode (no F-gap peak)",
            "no-repeat/collision inversion decodes",
            "AI-vision re-transcription (not viable; 0.145 alignment)",
            "image steganography (appended/EXIF/LSB/carve/color/OutGuess)",
        ],
        "open_threads": [
            "the AN END deep-web page (hash 36367763...c2a8b4) — the one place a key may exist",
            "a from-scratch independent human re-transcription (all lineages share the 2017 root)",
            "OutGuess control run on Linux to confirm the LP2 blob artifact",
        ],
        "statistical_profile": {
            "n_unsolved_runes": 12956,  # established: pages 0-55 excl. solved AN END/PARABLE (analysis/run_stats.py)
            "ioc_times_N": 1.000, "doublet_rate": 0.0066, "random_doublet": 0.0345,
            "entropy_bits": 4.857, "max_entropy_bits": 4.858,
            "keystream": "continuous across the whole book (no boundary reset); full-length (OTP-class)",
        },
    }
    dst = os.path.join(HERE, "liber_primus.json")
    json.dump(data, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    verified = sum(1 for p in pages if p["image"]["provenance_verified"])
    print(f"wrote {dst}: {len(pages)} pages, {verified} with verified image provenance")
    print(f"unsolved runes: {data['statistical_profile']['n_unsolved_runes']}")


if __name__ == "__main__":
    main()
