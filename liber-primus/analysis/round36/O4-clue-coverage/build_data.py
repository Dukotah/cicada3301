# O4 builder: reads vendored texts, writes clues.json. Tiny; no heavy compute.
import json, re, os
ROOT = "C:/Users/Jeff/cicada3301"
MSG = ROOT + "/corpus/A-primary-artifacts/pgp/messages/"
SIG = json.load(open(ROOT + "/corpus/A-primary-artifacts/SIGNATURES.json"))["messages"]
sigmap = {}
for r in SIG:
    if r["file"].startswith("pgp/messages/"):
        sigmap.setdefault(r["file"].split("/")[-1], r)

def body(fn):
    t = open(MSG + fn, encoding="utf-8", errors="replace").read().replace("\r", "")
    t = t.split("-----BEGIN PGP SIGNATURE-----")[0]
    t = t.replace("-----BEGIN PGP SIGNED MESSAGE-----", "")
    lines = [l for l in t.split("\n") if not l.startswith("Hash:")]
    return "\n".join(l.rstrip() for l in lines).strip()

clues = []
def addc(**k):
    clues.append(k)

rowmap = {
 "2013-cicada-os-message.asc": "H7", "2012-01-key-in-front-of-you.asc": "H8", "2013-01-knock-on-the-sky.asc": "H9",
 "2014-01-let-the-text-guide-you.asc": "H10", "2014-01-opening-book-code.asc": "H10",
 "2014-01-signed-ciphertext.asc": "H11", "2014-01-fallen-behind-outguess-08.asc": "H11",
 "2012-01-patience-check-back.asc": "H12", "2012-01-end-of-puzzle.asc": "H12", "2012-01-coordinates.asc": "H12",
 "2012-01-location-numbers.asc": "H12", "2012-01-book-code-poem.asc": "H12", "2012-01-mabinogion-book-code.asc": "H12",
 "2012-01-second-chance.asc": "H12", "2013-01-opening-book-code.asc": "H12",
 "2017-04-final-warning.asc": "H6", "2013-01-rune-table-morse.asc": "H11",
}
for fn in sorted(os.listdir(MSG)):
    if fn.startswith("ky_") or not fn.endswith(".asc"):
        continue
    b = body(fn)
    s = sigmap.get(fn, {})
    if fn == "2016-01-liber-primus.asc":
        parts = [("H5", "The path lies empty; epiphany seeks the devoted."),
                 ("H1", "Liber Primus is the way."),
                 ("H2", "Its words are the map,"), ("H3", "their meaning is the road,"),
                 ("H4", "and their numbers are the direction."),
                 ("H6", "Seek and you will be found."), ("H6", "Beware false paths.  Verify OpenPGP 7A35090F.")]
        for i, (row, txt) in enumerate(parts):
            addc(id="C-2016-%d" % (i + 1), row=row, text=txt, kind="out-of-book signed hint",
                 provenance="corpus/A-primary-artifacts/pgp/messages/" + fn,
                 signature=s.get("signature_status"), sig_time_utc=s.get("signature_timestamp_utc"),
                 date="2016-01", note="full body verbatim in C-2016-0")
        addc(id="C-2016-0", row=None, text=b, kind="out-of-book signed message (full body)",
             provenance="corpus/A-primary-artifacts/pgp/messages/" + fn,
             signature=s.get("signature_status"), sig_time_utc=s.get("signature_timestamp_utc"), date="2016-01",
             note="OWNER CORRECTION: 'Liber Primus is the way' is this 2016 message, not 2014. Web search reports the post as image 4gq25.jpg with disputed image channel; the PGP-signed text is VALID in SIGNATURES.json.")
        continue
    m = re.match(r"(\d{4})", fn)
    yr = m.group(1) if m else "?"
    addc(id="C-" + fn[:-4], row=rowmap.get(fn), text=b[:1200] + ("..." if len(b) > 1200 else ""),
         kind="out-of-book signed message", provenance="corpus/A-primary-artifacts/pgp/messages/" + fn,
         signature=s.get("signature_status"), sig_time_utc=s.get("signature_timestamp_utc"), date=yr,
         note=("hex payload truncated here" if len(b) > 1200 else ("logistics/routing, not a method clue" if fn not in rowmap else "")))

TR = ROOT + "/corpus/B-liber-primus/fetched/zenodo_18199474/liber-primus__translation.txt"
trl = open(TR, encoding="utf-8", errors="replace").read().replace("\r", "").split("\n")

def lp_row(code):
    p = code.split(".")
    if code.startswith("0.0.0"):
        if p[3] in ("6", "7"): return "L3"
        if p[3] in ("8", "9"): return "L2"
        return "L1"
    if code.startswith("0.1.0"): return "L11"
    if code.startswith("0.1.1"): return "L7"
    if code.startswith("0.1.2"): return "L4" if p[3] in ("1", "2") else "L5"
    if code.startswith("0.2.0"): return "L12"
    if code.startswith("0.2.1"): return "L8"
    if code.startswith("0.3.0") or code.startswith("0.3.1"): return "L14"
    if code.startswith("0.3.2"): return "L9"
    if code.startswith("0.4.0"): return "L13"
    if code.startswith("0.4.1"): return "L10"
    if code.startswith("0.13"): return "L17"
    if code.startswith("0.14"): return "L18"
    return None

for n, l in enumerate(trl, 1):
    m = re.match(r"^(0\.\d+\.\d+\.\d+)\t+(.*)$", l)
    if m:
        txt = re.sub(r"\s{2,}", " ", m.group(2)).strip()
        addc(id="LP1-" + m.group(1), row=lp_row(m.group(1)), text=txt, kind="in-book solved sentence",
             provenance="corpus/B-liber-primus/fetched/zenodo_18199474/liber-primus__translation.txt:%d" % n,
             signature="n/a (in-book; 5 pages reproduced by repo rig: SOLVED-PAGES.json, tests/validate.py)", date="2014-01 release")

SP = ROOT + "/liber-primus/data/keys/solved_plaintext.txt"
spl = open(SP, encoding="utf-8", errors="replace").read().replace("\r", "").split("\n")
hexl = [l.strip() for l in spl[321:326]]
addc(id="LP1-ANEND-HASH", row="L17", text="".join(hexl),
     kind="in-book solved: hash value on AN END page (128 hex chars)",
     provenance="liber-primus/data/keys/solved_plaintext.txt:322-326", signature="n/a", date="2014-01 release")

def S(id, row, text, prov):
    addc(id=id, row=row, text=text, kind="structural clue", provenance=prov,
         signature="n/a (in-book / measured)", date="2014-01 release / repo measurement")

S("ST-MAGIC-05", "L15", "Page 05 SOME WISDOM: 5x5 magic square mixing runic words and numbers; words' gematria complete it (SHADOWS=341, AETHEREAL=366, ...); rows sum 1033", "liber-primus/data/scream314_lp.md:895-950")
S("ST-MAGIC-KNOWTHIS2", "L15", "Second 5x5 matrix under KNOW THIS: 434 1311 312 278 966 / 204 812 934 280 1071 / 626 620 809 620 626 / 1071 280 934 812 204 / 966 278 312 1311 434 (trace 3301 per campaign7)", "liber-primus/data/keys/solved_plaintext.txt:~303-310; campaign7 HINT-DERIVED-METHODS H6")
S("ST-MAGIC-4x4", "L15", "Third matrix 4x4 trace 10673; the 2014 interactive phase demanded solvers 'post the three magic squares'", "corpus/H-branch-recovery/recovered/claude_master-roadmap-libra-qk527u/liber-primus/analysis/campaign7/HINT-DERIVED-METHODS.md H6; messages 2014-01-magic-square-upload-*")
S("ST-LINE-SUMS", "L16", "Gematria sum of each A WARNING line is prime (757,1009,691,353,769,911,1051,859,677); WELCOME 317, 2113, 2647; SOME WISDOM 468, 853, 1039, 1237, 157", "liber-primus/data/scream314_lp.md:122-136, 832-837, 952-958")
S("ST-761-PARABLE", "L16", "'The Instar Emergence' = 761 = its own filename; PARABLE tagged 1,595,277,641 = product of per-line gematria sums", "liber-primus/analysis/round10/L3-road/PREREG.md:20-26")
S("ST-PRIMES-RUNES", "L4", "29 runes <-> primes 2..109 (Gematria Primus): runes are numbers; mod-29 reduction discards magnitude", "liber-primus/analysis/NEXT-ARMADA-ROADMAP.md:11-18")
S("ST-LADDER", "S1", "Solved-page ladder: atbash+shift0 (01) -> shift0 (05) -> atbash+shift3 (06) -> Vigenere DIVINITY + F-interrupters (03) -> Vigenere FIRFUMFERENFE (14) -> AN END/p56 phi(prime) stream; each method taught by adjacent content", "liber-primus/SOLVED-PAGES.json; analysis/recon/LP1-METHODOLOGY.txt; campaign7 HINT-DERIVED-METHODS H4")
S("ST-KEYS", "S1", "Page keys are thematic words: DIVINITY (WELCOME; next theme THE LOSS OF DIVINITY) and FIRFUMFERENFE (koan about the CIRCUMFERENCE; C and F share a rune)", "liber-primus/SOLVED-PAGES.json; analysis/round10/L3-road/PREREG.md:127-134")
S("ST-INTERRUPTER", "S2", "Every clear-text F is an F-rune that must be skipped by the key on the solved Vigenere pages (7 on 03.jpg, 2 on 14.jpg)", "liber-primus/data/scream314_lp.md (04.jpg note); SOLVED-PAGES.json n_interrupters")
S("ST-LP2-SHAPE", "S2", "LP2 unsolved: pages 0-54, 55 segments, 12,956 runes, 2,928 words, 594 lines, 14 red section heads; keystream continuous across page joins", "liber-primus/PROBLEM.json; analysis/round10/L2-map/results.json G0; ELIMINATION-LEDGER.md:551-569")
S("ST-PAYLOAD", "S3", "pp49-51 base-60 table: 256-byte payload (canon_256), 6 contested bytes", "liber-primus/ELIMINATION-LEDGER.md:155-169; LEDGER.json A-04, C-CANON-PAYLOAD-3BYTES")
S("ST-ORNAMENT", "S4", "47 ornament bands/23 pages; 15 illuminated drop-caps; figural motifs never coded as data", "LEDGER.json A-06, R19-FINITE-ORNAMENT-REGISTER, R22-D-ILLUSTRATION-DROPCAP")
S("ST-RENDER", "S4", "2014 LP master is a machine-rendered PDF (Ghostscript 9.05-9.14); width-greedy line breaks (line-initial chi2 explained by rune widths r=0.72)", "LEDGER.json R30-A3-PDF-FORENSICS; analysis/round10/L2-map/diag_lineinit.json")
S("ST-SIGTIMES", "S5", "All VALID signatures by key 7A35090F span 2012-01-05 .. 2017-04-04 (signer-clock, settable)", "corpus/A-primary-artifacts/SIGNATURES.json summary; analysis/round18/L8-provenance/TIMESTAMP-SEED-CANDIDATES.json")
S("ST-CIRC", "L13", "THE I IS THE VOICE OF THE CIRCUMFERENCE + key FIRFUMFERENFE: circumference = alphabet cycle / page frame (never formalised)", "corpus/B-liber-primus/fetched/zenodo_18199474/liber-primus__translation.txt (0.4.0.2); SOLVED-PAGES.json p14")

json.dump(clues, open("clues.json", "w"), indent=1, ensure_ascii=False)
print("clues", len(clues), "with row", sum(1 for c in clues if c["row"]))
