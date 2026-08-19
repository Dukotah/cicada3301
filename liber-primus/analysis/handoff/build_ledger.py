"""Build liber-primus/LEDGER.json — the machine-readable falsification ledger.

WHY THIS EXISTS
---------------
Answering "what has been tried, and what is genuinely still open?" used to mean reading
~40 prose documents and reconciling them by hand. That is exactly how three load-bearing
overreaches survived for months (Round 12 front D3 caught them: the unconditional
information-theoretic closure, "seeded-PRNG closed", and "keytexts dead by mechanism").
Two of the three had already been flagged by Round 10's RECON-B and were never actioned,
because a flag in one folder does not reach a reader of another.

This script mines the STRUCTURED sources (the RECON-A / RECON-B registers) and merges them
with hand-authored entries for the rounds and campaigns, emitting one queryable JSON file.
It is a generator, not a one-off dump, so the ledger can be rebuilt as new rounds land.

    python3 build_ledger.py            # writes ../../LEDGER.json
    python3 validate_ledger.py         # checks it

THE FIELD THAT MATTERS MOST is `positive_control`. A negative result whose instrument was
never shown capable of detecting a planted signal is not a negative — it is an unknown.
The validator flags every such entry. That single check is the most portable thing this
project has to offer anyone who picks the puzzle up later.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", ".."))          # liber-primus/
ROOT = os.path.abspath(os.path.join(LP, ".."))                # repo root
OUT = os.path.join(LP, "LEDGER.json")

SCHEMA_VERSION = "1.0.0"

# Statuses. Kept deliberately small and mutually exclusive.
STATUSES = ["eliminated", "negative", "inconclusive", "never-run",
            "partially-run", "parked-with-cause", "open", "superseded", "in-flight"]


def rel(p):
    """Repo-relative path, forward slashes, for the evidence fields."""
    return os.path.relpath(p, ROOT).replace("\\", "/")


def exists(p):
    return os.path.exists(os.path.join(ROOT, p))


def normalize_evidence(p):
    """Register rows cite paths relative to liber-primus/ (e.g. `analysis/foo.md`) or to the
    repo root (`research/foo.md`). Resolve against both and return the one that exists, so a
    missing-evidence warning means genuinely missing, not merely differently-rooted."""
    p = p.strip().lstrip("./")
    for cand in (p, f"liber-primus/{p}"):
        if os.path.exists(os.path.join(ROOT, cand)):
            return cand
    return p


# ---------------------------------------------------------------------------
# 1. Mine the structured registers
# ---------------------------------------------------------------------------
def parse_register(path, id_col=0, title_col=1, source_col=2, status_col=3,
                   prio_col=None, lane=""):
    """Parse a RECON register markdown table into rough ledger entries."""
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) <= max(status_col, title_col):
            continue
        if not re.match(r"^[A-Z]-\d+$", cells[id_col]):
            continue
        ev = re.findall(r"`([^`]+)`", cells[source_col]) if source_col < len(cells) else []
        entry = {
            "id": cells[id_col],
            "lane": lane,
            "hypothesis": _clean(cells[title_col]),
            "status": _map_status(cells[status_col]),
            "raw_status": cells[status_col],
            "source_register": rel(path),
            "evidence": [normalize_evidence(e.split(":")[0]) for e in ev],
        }
        if prio_col is not None and prio_col < len(cells):
            entry["priority"] = cells[prio_col]
        out.append(entry)
    return out


def _clean(s):
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    return s.strip()


def _map_status(raw):
    r = raw.lower()
    if "never-run" in r:
        return "never-run"
    if "partially-run" in r:
        return "partially-run"
    if "scope-limited" in r or "declared-closed-but-thin" in r:
        return "open"
    if "stated-but-uninterpreted" in r:
        return "open"
    return "open"


# ---------------------------------------------------------------------------
# 2. Hand-authored entries: the rounds, and the three corrected closures.
#    Every field here traces to a document that was read; unknown fields are null
#    with a note, never invented.
# ---------------------------------------------------------------------------
HAND = [
  # ---- the corrected top-line verdict -------------------------------------
  {
    "id": "VERDICT-OTP-CLASS",
    "lane": "verdict",
    "hypothesis": "LP2 0-54 is OTP-class: a full-length keystream under a soft anti-repeat "
                  "filter (~83% suppression). The ciphertext is indistinguishable between a "
                  "TRUE EXTERNAL PAD (information-theoretically closed) and a SHORT-SEED "
                  "DERIVED keystream (finite keyspace, brute-forceable).",
    "status": "open",
    "round": "10b/B4 + 12/D3",
    "date": "2026-08-17",
    "threshold": "B4/G5 6-statistic separation battery; separation declared if any |z| > 2.93",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "result": {"separated": False, "max_abs_z": 1.60},
    "coverage": "The battery separates the two members of the class; it does not choose "
                "between them. Only running the derived-key dictionary chooses.",
    "evidence": ["liber-primus/analysis/round10b/B4-otp-steelman/b4_results.json",
                 "liber-primus/analysis/round12/D3/RESULTS.md"],
    "reproduce": "python3 liber-primus/analysis/round12/D3/pc_derivedkey.py",
    "supersedes": ["VERDICT-UNSOLVABLE-BY-DESIGN"],
    "reopens_if": "The derived-key dictionary (B-04) returns a hit, which would make the "
                  "keystream derived rather than a true pad.",
    "notes": "This entry replaces the unconditional claim 'information-theoretically "
             "unsolvable / no compute recovers it'. See VERDICT-UNSOLVABLE-BY-DESIGN.",
  },
  {
    "id": "VERDICT-UNSOLVABLE-BY-DESIGN",
    "lane": "verdict",
    "hypothesis": "LP2 0-54 is information-theoretically unsolvable; no compute recovers it; "
                  "unsolvable-by-design.",
    "status": "superseded",
    "round": "12/D3",
    "date": "2026-08-17",
    "threshold": None,
    "threshold_fixed_in_advance": False,
    "positive_control": "none",
    "result": "OVERREACH. One member of an indistinguishability class (a true external pad) "
              "was promoted into a property of the whole class. D3's control planted a "
              "SHA-256 counter-mode keystream from seed CICADA3301 and the project's own beam "
              "decoder RECOVERED it: -4.170 at 98.9% char-recovery, vs -7.349 on a wrong seed "
              "and -6.835 rigid on the CORRECT seed.",
    "coverage": None,
    "evidence": ["liber-primus/analysis/round12/D3/RESULTS.md",
                 "liber-primus/analysis/round12/D3/pc_derivedkey.py"],
    "reproduce": "python3 liber-primus/analysis/round12/D3/pc_derivedkey.py",
    "superseded_by": ["VERDICT-OTP-CLASS"],
    "reopens_if": "Never — this wording is retired. The narrowed claim is VERDICT-OTP-CLASS.",
    "notes": "Round 10's SYNTHESIS already stated the correction ('OTP-class, not a unique "
             "external pad'); it never propagated to README / ELIMINATION-LEDGER / "
             "PICKUP-HERE / Round 11 SYNTHESIS. Corrected in all four on 2026-08-19.",
  },
  # ---- the live lane -------------------------------------------------------
  {
    "id": "B-04",
    "lane": "keystream",
    "hypothesis": "The LP2 keystream is a cryptographic keystream derived from a short, "
                  "Cicada-flavoured seed (MD5/SHA-1/SHA-256/SHA-512 chain or counter, HMAC "
                  "counter-KDF, HMAC-DRBG, AES-CTR, RC4, ChaCha20), reduced mod 29 and applied "
                  "under the pinned soft anti-repeat filter.",
    "status": "in-flight",
    "round": "13",
    "date": "2026-08-19",
    "threshold": "HIT iff score_norm >= max(-5.5, null_max + 0.5). Measured null at L=120 "
                 "(n=200): mean -7.366, max -6.826, so the -5.5 floor binds.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": {
        "G1": "Replicates round12/D3: beam(correct) -4.170, rigid(correct) -6.835, "
              "beam(wrong) -7.349, char-recovery 0.989. PASS.",
        "G2": "Plants a seed genuinely resident in the dictionary ('THE PRIMES ARE SACRED', "
              "family `slogan`) and runs the full Stage-A cross product against the synthetic "
              "ciphertext. The planted config ranks #1 at -4.186, reading "
              "'THEPRIMESARESACREDANDTHETOTIENTFUNCTIONI...' in clear, against a runner-up of "
              "-6.621. PASS.",
    },
    "result": None,
    "coverage": "2,165 seeds x 16 generators x 5 mod-29 reductions x 2 signs x 2 Atbash x 2 "
                "directions, offset 0 (Stage A); 504 core seeds x 10 offsets (Stage B); 504 "
                "core seeds x 55 per-page restarts (Stage C); top-300 escalated to page 0 full "
                "and the whole 12,956-rune stream (Stage D). ~6.22M decodes.",
    "not_covered": ["seeds outside the 2,165-entry dictionary",
                    "key stretching (PBKDF2/scrypt/Argon2, iterated hashes > 1)",
                    "salted constructions H(salt || seed) for unknown salt",
                    "offsets beyond 3301, non-integer or per-line restarts",
                    "filters other than the pinned soft key-skip at supp=0.83",
                    "composite plaintext transforms (interrupters, page-order permutations)"],
    "evidence": ["liber-primus/analysis/round13/B04/PREREG.md",
                 "liber-primus/analysis/round13/B04/sweep.py",
                 "liber-primus/analysis/round13/B04/seeds.py",
                 "liber-primus/analysis/round13/B04/ks.py",
                 "liber-primus/analysis/round13/B04/harness.py"],
    "reproduce": "cd liber-primus/analysis/round13/B04 && python3 sweep.py --nproc 6",
    "reopens_if": "Always extendable — a negative closes only the tabulated region above. "
                  "The named extensions are key stretching and salted constructions.",
    "notes": "Marked never-run in RECON-A since 2026-08-12; the iter-6 MDL kill "
             "('incompressible => not algorithmically generated') has NO power here because a "
             "hash keystream is incompressible by construction. Round 8's 2.52e9 decodes "
             "covered hobbyist integer-seeded PRNGs only, never keyed hash/stream ciphers. "
             "CRITICAL: every prior seed sweep used RIGID alignment, which returns noise even "
             "on the CORRECT seed once the filter is applied - a guaranteed false negative. "
             "Beam is mandatory.",
  },
  {
    "id": "B-05",
    "lane": "keystream",
    "hypothesis": "The pp49-51 256-byte payload is a PRF seed expanded into a runic keystream "
                  "(RC4/AES-CTR/SHA-counter/HMAC-DRBG), rather than key material used directly.",
    "status": "negative",
    "round": "13",
    "date": "2026-08-19",
    "threshold": "HIT iff score >= -5.5 AND score > null_max. Null (shuffled HEAD, n=200): "
                 "mean -7.302, max -7.001.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": {
        "all_generators": "sha256_ctr, rc4, hmac_drbg_sha256 (+1) all recover the plant: beam "
                          "-4.170 at 98.9% char-recovery vs beam(wrong) ~-7.33 and "
                          "rigid(correct) -6.68..-7.48. Flipping ONE contested byte destroys "
                          "recovery (-7.38), confirming avalanche sensitivity."},
    "result": "NEGATIVE. 70,680 beam decodes, 0 hits. Best -6.745 (Part 2b) vs a -5.5 bar "
              "and a null max of -7.001 - 1.25 below the bar, 0.26 above noise. Rigid "
              "control channel peaked at -7.096. Escalation is the informative part: the "
              "top-5 head configs all got WORSE on the full page (-7.22..-7.33 from heads "
              "of -6.77..-6.86), which is the signature of an order statistic, not a "
              "signal - a real key improves with more text, a lucky one degrades.",
    "coverage": "Payload representations (raw, reversed, bit-reversed, dec-prefix) x "
                "{SHA-256/512 ctr+chain, MD5/SHA-1 ctr, HMAC-DRBG, AES-CTR, RC4, ChaCha20} x "
                "{mod29, rejection} x sign x direction x offsets; plus the 6 contested bytes "
                "(RECON-A A-04) as a sensitivity dimension.",
    "evidence": ["liber-primus/analysis/round13/B05/PREREG.md",
                 "liber-primus/analysis/round13/B05/sweep.py",
                 "liber-primus/analysis/round13/B05/control_results.json"],
    "reproduce": "cd liber-primus/analysis/round13/B05 && python3 sweep.py",
    "reopens_if": "JOINT corruption of two or more contested bytes (only single-position "
                  "sweeps and the 64 all-combination masks were run); key stretching applied "
                  "to the payload (that is round15/KDF, not this lane); salted expansion; "
                  "expanders outside the tested set.",
    "notes": "Campaign XX applied AES/RC4/ChaCha to the payload as CIPHERTEXT; nobody had "
             "expanded it into a keystream over the runes. The control measured avalanche "
             "sensitivity directly: flipping ONE contested byte drops recovery from -4.170 "
             "to -7.38, i.e. perfect to noise - which is why Part 2b swept all 256 values "
             "at each of the 6 contested positions rather than assuming them. That "
             "materially weakens RECON-A A-04 as a blocker for THIS lane.",
  },
  # ---- the two other corrected closures ------------------------------------
  {
    "id": "B-21",
    "lane": "keystream",
    "hypothesis": "Seeded-PRNG pads are eliminated ('do not re-run').",
    "status": "partially-run",
    "round": "8, re-audited 12/D3",
    "date": "2026-08-17",
    "threshold": "Round 8 used a fixed bar; round10/L5-seed32 later proved that bar is "
                 "STATISTICALLY INVALID at full-32 scale because the null max grows with trial "
                 "count. A scale-corrected threshold from nullcurve.py is required.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "result": "2.52e9 decodes, 0 hits, best -13.13 (= the null max) - but see coverage.",
    "coverage": "10 integer-seeded generators over ~3% of each seed space (only 2 swept fully). "
                "UNCOVERED and named-plausible in round10/L5-seed32/CENSUS.md: PHP mt_rand "
                "(highest-prior open generator), .NET System.Random, Blum-Blum-Shub as a real "
                "seed space, ISAAC, LFSR/Geffe/Gollmann, plus >2^32, millisecond-resolution and "
                "offset != 0 seed spaces. Round 8 also used RIGID decode throughout.",
    "evidence": ["liber-primus/analysis/round10/L5-seed32/CENSUS.md",
                 "liber-primus/analysis/seed_sweep/",
                 "research/ROUND-8-RESULTS.md"],
    "reproduce": "see liber-primus/analysis/seed_sweep/run_full32.sh",
    "reopens_if": "It is not closed. PHP mt_rand alone is an open, named, high-prior gap.",
    "notes": "Flagged by RECON-B as B-21 in Round 10 and never actioned; the ELIMINATION-LEDGER "
             "line was unchanged until 2026-08-19. '10 generators at ~3% each' was written up "
             "as 'seeded-PRNG pads, closed'.",
  },
  {
    "id": "B-16",
    "lane": "mechanism",
    "hypothesis": "Every keytext null is unsound because the beam decoder was validated against "
                  "the key-SKIP mechanism (key desyncs) while Campaigns X/XI pin the mechanism "
                  "as a value-REWRITE of the output (key stays synced).",
    "status": "eliminated",
    "round": "12/D1",
    "date": "2026-08-17",
    "threshold": "If a correct key under the REWRITE construction fails to score in the English "
                 "band, every ~200-text keytext null is unsound and the lane reopens.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": {"ARM1_skip": "correct key recovered -4.27..-4.32, 95-100% rune match"},
    "result": "ARM 2 (REWRITE, correct key, same beam): recovered to -4.45..-4.70 (95-98% "
              "match) at page length, and -4.80..-5.16 on 250 runes at up to 7% corruption. A "
              "correct keytext under the pinned rewrite mechanism would have scored ~-4.5; the "
              "real sweeps produced -5.75..-5.88. The nulls DO cover rewrite.",
    "coverage": "Rewrite corrupts only ~2.8% of positions on the real cipher and does not "
                "desync the key, so even rigid decode recovers a correct key under it.",
    "evidence": ["liber-primus/analysis/round12/D1_redteam/rewrite_gate.py",
                 "liber-primus/analysis/round12/D1_redteam/RESULTS.md",
                 "liber-primus/analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md"],
    "reproduce": "python3 liber-primus/analysis/round12/D1_redteam/rewrite_gate.py",
    "reopens_if": "A third filter mechanism, distinct from both key-skip and value-rewrite, "
                  "is shown to fit the doublet statistics.",
    "notes": "Closes rather than confirms B-16. Forces a WORDING fix, not a verdict change: "
             "the keytext closure is 'by exhaustion over ~200 texts, verified robust to both "
             "constructions', NOT 'by mechanism, independent of text'. A REWRITE row was added "
             "to COVERAGE-MATRIX.md on 2026-08-19.",
  },
  # ---- round 12's other fronts --------------------------------------------
  {
    "id": "R12-A1",
    "lane": "external-input",
    "hypothesis": "The author's own CicadaOS binary files (DATA/_560.00/.13/.17, prime_echo, "
                  "folly/wisdom, 761.mp3) are the pad - period-correct key material Cicada "
                  "demonstrably used, only ever byte-XOR'd by the community, never fed as a "
                  "mod-29 keystream under the skip-aware decoder.",
    "status": "negative",
    "round": "12/A1",
    "date": "2026-08-17",
    "threshold": "HIT bar -5.5; per-page null (n=200) mean -7.308, max -6.877.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "result": "Five pads (2026-08-17): best per-page -6.517 (560.17, prime_to_idx_rev, page "
              "54) - 1.02 below the bar and 0.36 above the null max; full-stream beam -7.298. "
              "Sixth pad DATA/560.13 (2026-08-19): best -6.965 vs null max -7.037, bar -5.5. "
              "All six NEGATIVE.",
    "coverage": "All 6 author pads x mod-29 / prime-index / nibble / bit-scaled reductions x "
                "forward and reversed x both signs x offsets (to 5e7 on 560.13), whole-stream "
                "and per-page. Tested as LITERAL byte->symbol reductions only, not as PRF "
                "seeds or salts.",
    "evidence": ["liber-primus/analysis/round12/A1/RESULTS.md",
                 "liber-primus/analysis/round12/A1/harness.py",
                 "liber-primus/analysis/round12/A1/sweep.py",
                 "liber-primus/analysis/round12/A1/sweep_560_13.py",
                 "liber-primus/analysis/round12/A1/results_560_13.json"],
    "reproduce": "cd liber-primus/analysis/round12/A1 && python3 sweep.py",
    "reopens_if": "Only as a PRF SEED / salt / keyed input - the pads were tested as literal "
                  "byte->symbol reductions, not hash-expanded. That construction is lanes "
                  "B-04/B-05, not this one.",
    "notes": "This was PA-3's 'highest-prior remaining input'. COMPLETED 2026-08-19: the one "
             "declared gap, DATA/560.13 (118,818,811 B, sha256 db79072c...), was recorded as "
             "unrecoverable after both GitHub LFS mirrors returned 404 on the LFS batch API. "
             "It was recovered from archive.org's 3301.iso, which exposes the ISO's inner "
             "files directly, and verified BYTE-EXACT against the LFS pointer's own digest. "
             "Swept with A1's own builders/beam/null/bar unchanged plus an extended offset "
             "ladder (the pad is ~100x longer than the others): 160 configs, best -6.965 "
             "(prime_to_idx_rev, sign -1, offset 1000) against a -5.5 bar and a null max of "
             "-7.037 - i.e. 0.07 above pure noise. A1 is now complete rather than merely "
             "unreached: all six author binaries are exhausted.",
  },
  {
    "id": "R12-C1",
    "lane": "cipher-class",
    "hypothesis": "The cipher is unbounded k-history feedback / autokey: key at position i = "
                  "f(last k already-known runes), decoded left-to-right. The community state of "
                  "the art stops at exactly this label.",
    "status": "negative",
    "round": "12/C1",
    "date": "2026-08-17",
    "threshold": "Score must jump the noise band (~-7.5) into English (~-4.15).",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": {"all": "21/21 (f, source) combinations at k=3 recovered at 100% match, "
                              "score -4.154; wrong-f decode stays ~-7.4."},
    "result": "Real sweep over LP2 unsolved: null.",
    "coverage": "See the bound table in RESULTS.md.",
    "evidence": ["liber-primus/analysis/round12/C1/RESULTS.md",
                 "liber-primus/analysis/round12/C1/sweep.py",
                 "liber-primus/analysis/round12/C1/control.py"],
    "reproduce": "cd liber-primus/analysis/round12/C1 && python3 sweep.py",
    "reopens_if": "k beyond the swept bound, or a feedback function outside the 21 tested.",
    "notes": None,
  },
  {
    "id": "R12-C2",
    "lane": "keytext",
    "hypothesis": "A fresh esoteric/philosophical corpus (29 texts not used in campaign12/13 or "
                  "armada18/19) contains the running key.",
    "status": "never-run",
    "round": "12/C2",
    "date": "2026-08-17",
    "threshold": None,
    "threshold_fixed_in_advance": False,
    "positive_control": "none",
    "result": None,
    "coverage": "Texts fetched (29 files, ~12 MB); the sweep was never run.",
    "evidence": ["liber-primus/analysis/round12/C2/fetch.sh"],
    "reproduce": "bash liber-primus/analysis/round12/C2/fetch.sh  # then no sweep exists yet",
    "reopens_if": "Low prior: Round 7 + D1 established the keytext class is closed by "
                  "exhaustion, verified robust to both filter constructions. Running C2 adds 29 "
                  "texts to a ~200-text exhaustion, which does not change the argument.",
    "notes": "Left unfinished when the campaign ended. Documented rather than quietly dropped.",
  },
  {
    "id": "R12-D2",
    "lane": "red-team",
    "hypothesis": "A load-bearing statistic is miscounted (page/segment joins double-counting, "
                  "interrupters wrongly included/excluded, etc.).",
    "status": "eliminated",
    "round": "12/D2",
    "date": "2026-08-17",
    "threshold": "Independent recomputation from raw runes must match the repo's claims.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": {"plant": "planted English recovered -4.34 vs shuffled noise -6.60, "
                                "jump +2.26"},
    "result": "All 7 headline statistics reproduce exactly: n=12,956; doublet rate 0.664%; "
              "IoC*N 0.9999; entropy 4.8565 bits; 86 doublets; p* = 400; G3 floor 1.38-1.83% "
              "over 4 corpora. The 54 cross-page join pairs contain 0 doublets; per-page "
              "recomputation gives 0.667% (a 0.003 pp difference).",
    "coverage": "Every load-bearing number, recomputed with independent code.",
    "evidence": ["liber-primus/analysis/round12/D2/RESULTS.md",
                 "liber-primus/analysis/round12/D2/recompute.py"],
    "reproduce": "python3 liber-primus/analysis/round12/D2/recompute.py",
    "reopens_if": "A transcription change (see R12-frontB and A-03) would change n and the "
                  "doublet count.",
    "notes": None,
  },
  {
    "id": "R12-frontB",
    "lane": "transcription",
    "hypothesis": "Canon mis-transcribes the dense OTP pages 45-54, where every prior audit was "
                  "weakest.",
    "status": "inconclusive",
    "round": "12/frontB",
    "date": "2026-08-17",
    "threshold": "An instrument must pass its own control before it can confirm OR refute.",
    "threshold_fixed_in_advance": True,
    "positive_control": "failed",
    "result": "The FORCED per-line re-segmentation instrument scores 12.9% agreement on solved "
              "control pages against the ~98% the validated R9 raw-band decode reaches. By the "
              "campaign's own discipline it therefore certifies nothing. Separately, the "
              "VALIDATED R9 template DP reproduces 98.0% over 5,150 glyphs on 232 count-exact "
              "lines and finds no real localized rune error on 45-54.",
    "coverage": "Pages 45-54 only.",
    "evidence": ["liber-primus/analysis/round12/frontB/RESULTS.md",
                 "liber-primus/analysis/round12/frontB/forceseg.py"],
    "reproduce": "cd liber-primus/analysis/round12/frontB && python3 run_final.py",
    "reopens_if": "A vision model good enough to pass the forced-segmentation control on dense "
                  "pages. This is a PARKED item, not a closed one.",
    "notes": "A model entry for how to report a failed instrument: the forced front is recorded "
             "as INCONCLUSIVE, and only the control-passing instrument is allowed to carry the "
             "conclusion. Do not read this as 'pages 45-54 verified'.",
  },
]


def build():
    entries = []
    entries += HAND
    entries += parse_register(os.path.join(LP, "analysis", "round10", "RECON-A", "REGISTER.md"),
                              lane="recon-a")
    entries += parse_register(os.path.join(LP, "analysis", "round10", "RECON-B", "REGISTER.md"),
                              prio_col=4, lane="recon-b")

    # Hand entries win over a register stub with the same id, but keep the register's
    # source pointer and priority so nothing is lost in the merge.
    merged, seen = [], {}
    for e in entries:
        if e["id"] in seen:
            prior = seen[e["id"]]
            for k, v in e.items():
                if k not in prior or prior[k] in (None, [], ""):
                    prior[k] = v
            continue
        seen[e["id"]] = e
        merged.append(e)

    # Normalise: every entry carries every key, so consumers never KeyError.
    keys = ["id", "lane", "hypothesis", "status", "round", "date", "threshold",
            "threshold_fixed_in_advance", "positive_control", "control_detail", "null",
            "result", "coverage", "not_covered", "evidence", "reproduce", "supersedes",
            "superseded_by", "reopens_if", "priority", "source_register", "raw_status",
            "notes"]
    for e in merged:
        for k in keys:
            e.setdefault(k, None)
        e["evidence"] = e.get("evidence") or []
        e["evidence_missing"] = [p for p in e["evidence"] if not exists(p)]

    by_status = {}
    for e in merged:
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1

    doc = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "liber-primus/analysis/handoff/build_ledger.py",
        "generated_for": "Anyone picking up Liber Primus later - human or model. Query this "
                         "instead of reading 40 prose documents.",
        "read_this_first": {
            "positive_control": "THE FIELD THAT MATTERS MOST. A 'negative' whose instrument was "
                                "never shown able to detect a planted signal is not a negative, "
                                "it is an unknown. validate_ledger.py flags every such entry.",
            "coverage": "Always read this before treating a status as closed. Several entries "
                        "in this repo's history were written up as 'closed' when their coverage "
                        "field says otherwise (see B-21).",
            "reopens_if": "The concrete condition that puts a lane back on the table.",
        },
        "statuses": STATUSES,
        "counts": {"total": len(merged), "by_status": by_status},
        "entries": merged,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    print(f"wrote {rel(OUT)}: {len(merged)} entries")
    for k, v in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {k:20s} {v}")
    return doc


if __name__ == "__main__":
    build()
