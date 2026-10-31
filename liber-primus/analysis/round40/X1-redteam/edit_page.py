#!/usr/bin/env python3
"""Round 40 X1: refresh MEASURED-CEILING.md from MEASURED-CEILING.pre-x1.bak (idempotent)."""
import os, re, sys, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
src = open(os.path.join(HERE, "MEASURED-CEILING.pre-x1.bak"), encoding="utf-8").read().split("\n")
NROWS = json.load(open(os.path.join(LP, "LEDGER.json"), encoding="utf-8"))["counts"]["total"]


def find(prefix):
    hits = [i for i, l in enumerate(src) if l.startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


def cells(l): return [c.strip() for c in l.strip().strip("|").split("|")]
def row(cs): return "| " + " | ".join(cs) + " |"


def edit(prefix, fn):
    i = find(prefix); cs = cells(src[i]); fn(cs); src[i] = row(cs)


def add(cs, k, text, sep="; "):
    assert text not in cs[k]; cs[k] = cs[k] + sep + text if sep else cs[k] + text


# ---- header
i = find("_Round 39, lane P1.")
src[i] = src[i].replace("(262 rows after the X1 audit)", "(%d rows after the Round 40 X1 audit; Round 40 lanes B1, B3, C1, I1 refreshed it, see section 3 and the near-miss notes)" % NROWS)
assert str(NROWS) in src[i]

# ---- section 1: survivor-population mismatch
def f_nulls(cs):
    add(cs, 2, "X1/Round 40: the stored survivors of the sweeps score higher than the null cells they are compared with (L=120 median 2.74-2.86 vs 2.33, q99 4.7-4.8 vs 4.06 in the R37-I2 orbit rows, the B1 rows and the B3 rows), so the 'actual-N' bar is not a 1 % family-wise bar (a pooled empirical bar at N=131,786 is about 9.6 against 8.3 stored); the N=1e6 bar is the effective one and no stored verdict moves. "
                "Direct (stream) families judged against a global shuffle have a related defect: real LP2 walk streams have a trajectory-level pmax spread (mean 2.2, sd 0.8) that no global shuffle reproduces (mean 1.1, sd 0.5)")
edit("| **Observed wrong-key nulls**", f_nulls)

# ---- section 2a: new bash rows after the 4.2 row
i = find("| bash 4.2 `$RANDOM` auto-seed orbit")
newrows = [
 row(["bash 4.0 / 4.1 `$RANDOM` auto-seed orbit (`%29`, offset 0, sign -1)",
      "No separate orbit run: the RANDOM block of 4.0 and 4.1 is textually identical and differs from 4.2 only in the zero-state branch, so the bash 4.2 sweeps (296/296 chunks per ABI) are the 4.0 / 4.1 sweeps by identity; 8 of 296 chunks re-executed through the 4.1 generator (identical survivor and decode sets) and 2 of them again by the red team; the roughly 37 ILP32 seeds that reach state 0 within 1,024 steps are not covered",
      "As the 4.2 row: screen reach 0.952-0.994 x v3 recovery (the lane's own natural-rate controls recovered 59-60 of 60 plants per version); best 7.065 vs 8.027 at actual N (8.999 at N=1e6)",
      "bash 4.0 / 4.1 auto-seed set `tv_sec ^ tv_usec ^ pid`, LP64+ILP32, offset 0 / `keyskip1`+`keyskip2`, heads with at most 2 skips in 24 runes / panel-R36, 12 registers [plants: EN_MODERN / EN_NOVOWEL / HEBREW only in the 4.0 / 4.1 / 3.2 / 5.1 lane controls]",
      "[[R40-B1-BASH41-RANDOM-AUTOSEED]] [[R40-B1-BASH40-RANDOM-AUTOSEED]] [[R37-I2-PFV4-12REG-ORBIT]]",
      "**measured negative** (by identity with the 4.2 sweeps; no 4.0 or 4.1 binary was run)",
      "a 4.0 / 4.1 binary stream differs from the model; a state-0 seed is the key; the re-opens of the 4.2 row"]),
 row(["bash 3.2 (`pid + time(0)`, ANSI-C LCG) and bash 5.1 non-PIE (`genseed`, 32-bit Lehmer) `$RANDOM` auto-seed orbits (`%29`, offset 0, sign -1)",
      "3.2: 76,237,568 seeds (every integer from 2012-01-01 + 1 to 2014-06-01 + 32,768), 291/291 chunks, 64,511 survivors decoded; 5.1: 92,274,688 seeds (88 x 2^20 non-PIE prefixes), 352/352 chunks, 77,772 survivors decoded",
      "Natural-rate controls 59 of 60 per version; best 3.2 `keyskip1` 7.098 vs 8.105 (9.102 at N=1e6), 5.1 `keyskip2` 6.522 vs 8.086; the 3.2 generator is source-derived (read independently by the red team) and was never compared with a 3.2 binary; the 5.1 stream equals a live 5.3.9 binary but the 5.1 auto-seed is source-read only",
      "3.2 `pid + time(0)` (pid <= 32768), 5.1 non-PIE `genseed` family (about 4.3 % of the ~2^31 PIE orbit), offset 0 / `keyskip1`+`keyskip2`, at most 2 skips in the head / panel-R36, 12 registers [plants: EN_MODERN / EN_NOVOWEL / HEBREW only]",
      "[[R40-B1-BASH32-RANDOM-AUTOSEED]] [[R40-B1-BASH51-RANDOM-AUTOSEED]]",
      "**partial** (3.2: the generator is unverified against a binary; 5.1: the non-PIE family only)",
      "a bash 3.2 binary confirms the generator (the row then becomes a bounded negative); a 5.1 PIE-orbit sweep; pid_max above 32768 for 3.2"]),
]
src[i + 1:i + 1] = newrows

# ---- SHA / KDF line
def f_sha(cs):
    add(cs, 1, "Round 40 B3: the regenerated 2,165-seed dictionary (6,998,144 configs) and the 534-secret KDF grid (692,064 configs) re-decoded under pf_v4_12 + beam_v3 `keyskip1`+`keyskip2` on panel-R36")
    add(cs, 2, "B3 re-decode: best 6.336 / 6.049 (seed dictionary) and 5.150 / 6.528 (KDF) vs actual-N bars 7.244 / 7.173 and 6.399 / 6.342 (9.102 / 8.999 at N=1e6); the one KDF crosser (rev buffer, 6.528) is adjudicated noise (coordinator, and independently by the red team: it falls to 5.531 as the read lengthens and has no words)")
    add(cs, 3, " [plants: EN_MODERN / EN_NOVOWEL / LATIN only for the R40-B3 re-decodes]", sep="")
    add(cs, 4, " [[R40-B3-B04-REDECODE]] [[R40-B3-R16KDF-REDECODE]]", sep="")
    cs[5] = cs[5].replace("so these grids carry no stated power under `skip_by_two` outside the R24 slice)", "so the original sweeps carry no stated power under `skip_by_two` outside the R24 slice; the regenerated lists have the R40-B3 `keyskip1`+`keyskip2` re-decode with plants in three registers)")
    assert "R40-B3" in cs[5]
edit("| SHA-256-CTR / HMAC-DRBG", f_sha)

# ---- CicadaOS pads
def f_pads(cs):
    add(cs, 1, "Round 40 B3: the four ISO pads (560.00 authoritative, 560.13, 560.17, 761.mp3) re-decoded at a stated 0.782 % sampled offset fraction (10,006,340 of 1,280,055,240 columns; 20,012,680 configs)")
    add(cs, 2, "B3 re-decode: best 6.066 / 5.967 vs actual-N bars 7.619 / 7.542 (9.102 / 8.999 at N=1e6), 0 flagged; the truncated `_560.00`, `folly`/`wisdom` and `prime_echo` pads were not regenerable")
    add(cs, 3, " [plants: EN_MODERN / EN_NOVOWEL / LATIN only for the R40-B3 re-decode]", sep="")
    add(cs, 4, " [[R40-B3-COSPAD-REDECODE]]", sep="")
edit("| The author's own CicadaOS pads", f_pads)

# ---- public pads
def f_pub(cs):
    add(cs, 1, "Round 40 B3: the regenerated R17-P3 pad list (25 of 28 sha-equal; `canon_256` and the two `cicada_all` pads carry the corrected canon) re-decoded at a stated 0.476 % sampled offset fraction (7,506,611 of 1,577,174,689 builder x direction columns; 15,013,222 configs); P1 and P2 not regenerated")
    add(cs, 2, "B3 re-decode: best 5.745 / 5.846 vs actual-N bars 7.424 / 7.350 (9.102 / 8.999 at N=1e6), 0 flagged")
    add(cs, 3, " [plants: EN_MODERN / EN_NOVOWEL / LATIN only for the R40-B3 re-decode]", sep="")
    add(cs, 4, " [[R40-B3-R17-PUBLIC-PAD-REDECODE]]", sep="")
edit("| Public randomness: blockchain", f_pub)

# ---- I1 tag widenings: cite form + power wording (lines that carry the widened tag)
OLD = "(R40-I1-REPLANT-CONTROLS re-planted LATIN, GREEK, EN_NOVOWEL, HEBREW at power 1.00; CY, OE, DE, NORSE, EN_KJV, EN_HALFVOWEL, LP1 still unplanted)"
NEW = "(re-planted by [[R40-I1-REPLANT-CONTROLS]]: every plant recovered, 12-80 per register, Wilson 95 % lower bounds 0.76-0.95, a point estimate rather than a power of 1.00; the U1 and G1 re-plants test true-setting recovery, not the original rank-1 test; CY, OE, DE, NORSE, EN_KJV, EN_HALFVOWEL, LP1 still unplanted)"
n_tag = 0
for k, l in enumerate(src):
    if OLD in l:
        src[k] = l.replace(OLD, NEW); n_tag += 1
assert n_tag == 5, n_tag

# ---- line 80 split
i = find("| Round 10 map / road streams")
cs = cells(src[i])
a = list(cs); b = list(cs)
a[0] = "Round 10 road streams and the Round 11 number-channel lenses, re-scored outside English"
a[1] = "208 road streams; N1 CT-feedback 24 configs; N2, N4, N5 (4,640 decodes), S1, S2 under 12 registers"
a[2] = "Direct plants 14/14 and beam plants 30/30 (EN_MODERN / LATIN / GREEK); N5 AN END control 1.00 / 0.93; re-planted in five registers with 10 plants per register and family, every plant recovered"
a[3] = ("regenerated streams and ledgered configs / direct and `keyskip1`+`keyskip2` / panel-R36 [plants: EN_MODERN / LATIN / GREEK / EN_NOVOWEL / HEBREW only "
        "(re-planted by [[R40-I1-REPLANT-CONTROLS]], Wilson 95 % lower bound 0.72 at n=10; CY, OE, DE, NORSE, EN_KJV, EN_HALFVOWEL, LP1 unplanted)]")
a[4] = "[[R37-C3-U5-L3-ROAD]] [[R37-C3-U6A-N1-CT]] [[R37-C3-U6A-N2]] [[R37-C3-U6A-N4]] [[R37-C3-U6A-N5]] [[R37-C3-U6A-S1]] [[R37-C3-U6A-S2]]"
assert "post-data null" in a[5]
b[0] = "Round 10 map streams (L2-MAP), re-scored outside English"
b[1] = "M1 464 + 21,808 + M2 348 + M9 290 + M5 1,486 map streams; the z=6.94 map stream is an ordinary member of its own family (family p 0.95)"
b[2] = ("Direct plants 14/14 at EN_MODERN / LATIN / GREEK on the original control; re-plant of the per-page M1 family (n=53 runes): EN_MODERN 8/10, LATIN 10/10, GREEK 10/10, HEBREW 9/10, EN_NOVOWEL 1/10 "
        "(red-team fresh seeds: EN_MODERN 8/10, EN_NOVOWEL 2/10), so that family is not powered at 0.9 even in English")
b[3] = ("regenerated streams / direct / panel-R36 [plants: EN_MODERN / LATIN / GREEK only; the per-page M1 family fails EN_NOVOWEL and sits at 8/10 for EN_MODERN "
        "([[R40-I1-REPLANT-CONTROLS]])]")
b[4] = "[[R37-C3-U5-L2-MAP]] [[R40-I1-REPLANT-CONTROLS]]"
b[5] = "**partial** (the other map families keep the measured-negative reading for EN_MODERN / LATIN / GREEK; the per-page M1 family is unpowered)"
b[6] = "a per-page M1 control that recovers EN_NOVOWEL and EN_MODERN at 0.9 or better, or a longer unit than one page; a stream whose panel pmax and standardised Z both clear the family-wise null with non-degenerate IoC and mds"
src[i:i + 1] = [row(a), row(b)]

# ---- 2b: C1 rows (inserted before the Round 11 lens legacy row)
j = find("| Round 11 lens rows as originally filed")
c1rows = [
 row(["The 46 English-only and legacy-beam clue readings, re-scored under panel-R36 (Round 40 C1)",
      "11 readings as 15 family parts, all candidate sets regenerated: R30 artifact keys (338,832 heads), c18 numerics (139,152), R32 slogan seeds (4,625,920) and lp seeds (803,840), R33 seed zoo (2,137 keystreams), R43 composed keys (1,446,720), R47 LP2-as-pad (112 rows per relation), and the direct families R04 M4, R06 M6, R27 R22-A, R28 R23-A2; 28,236 rows",
      "Beam families: 6 plants per relation recovered 6/6 in every family; direct families: held-out text beats the family null max-Z q99 by more than 1; best beam rows 4.2-5.96 vs bars 5.8-9.7 (for head-screened families C1's 'actual-N' bar uses heads screened as N; the declared 9.10 / 9.00 bars are the safer reading)",
      "regenerated key sets as listed, offset 0 / `keyskip1`+`keyskip2` after the pf_v4_12 head screen (reach at least 0.95 per register), skip-free for direct streams / panel-R36 [plants: EN_MODERN / LATIN / GREEK only; HEBREW, NORSE and EN_NOVOWEL are not planted in the beam controls]",
      "[[R40-C1-R30-B1-ARTIFACT-KEYS]] [[R40-C1-C18-NUMERIC-PS-TWEET-MAYAN]] [[R40-C1-R32-B04-SLOGAN-SEEDS]] [[R40-C1-R32-B04-LP-SEEDS-STAGE-A]] [[R40-C1-R33-SEMANTIC-SEED-ZOO]] [[R40-C1-R43-B5-COMPOSED-KEYS]] [[R40-C1-R47-F01-LP2-AS-PAD]] [[R40-C1-R04-M4-LP1-POINTER]] [[R40-C1-R06-M6-STRUCTURAL-COUNTS]] [[R40-C1-R27-R22A-SELFEMBEDDED]] [[R40-C1-R28-R23A2-LINE-ACROSTIC]]",
      "**measured negative** (the R04 Z statistic is invalid for length-pointer families, so that verdict rests on the raw best-of-family statistic, p 0.72; the direct families use global-shuffle nulls that understate the real text's spread, which cannot turn a negative into a positive)",
      "a stream or head whose panel pmax clears the declared N=1e6 bar with non-degenerate IoC and mds; a reading whose artefact is supplied (section 3 lists the cells that could not be re-scored)"]),
 row(["Round 9 DIRECTION: positional walks and sieves of the LP2 ciphertext (2,670 reads), Round 40 re-score",
      "2,274 scorable reads regenerated from `direction.py`; best a backward self-indexing walk (`A:idx:s60:b1:f1`, a 400-rune stream, pmax 4.733); three global doublet-matched shuffle nulls (D=150, 800, 500) gave p 0.004-0.0066 on both statistics",
      "Held-out text beats the family null max-Z q99 in three registers; red-team matched nulls (block-permuted LP2, 500 draws each): page scale p(Z) 0.018, region scale 0.070, only the 100-rune null reproduces p<0.01; on real LP2 the walk's trajectories (923 distinct) have pmax mean 2.2 sd 0.8, and the best is the top of them at about 3 sd (the expected maximum of 923 draws); a readable 400-rune stream would score tens",
      "2,670 fixed positional reads / none (key-free) / panel-R36 [plants: EN_MODERN / LATIN / GREEK only]",
      "[[R40-C1-R13-R9-DIRECTION-WALKS]]",
      "**inconclusive** (filed open pending the coordinator; not a near-miss under the page- and region-scale matched nulls; the stream's transliteration has no words)",
      "a replication of the excess under a null that matches the walk's positional structure at page scale or coarser, or a human read judging the 400-rune stream as language"]),
]
src[j:j] = c1rows

# ---- section 3
def f_bash(cs):
    cs[0] = "Other bash versions and seedings; other PHP variants; offsets other than 0; sign +1 on most rows"
    cs[1] = ("bash 3.2: the generator is source-derived and unverified against a binary (the red team re-read the source), pid_max above 32768 (about 5.5 % more seeds) and a first `$RANDOM` use inside a subshell (state-dependent reseed); bash 5.x PIE/ASLR builds "
             "(orbit about 2^31; 4.3 % enumerated) and BASH_COMPAT of 50 or less; bash 5.0 / 5.2 / 5.3 seeding differences; a real 32-bit bash 4.2 beyond the swept ILP32 orbit; about 37 ILP32 seeds that reach state 0 in bash 4.0 / 4.1; non-zero key offsets (a Round 40 offset lane was still running at the audit and is not audited here)")
    cs[2] = "partial"
    cs[3] = "[[R40-B1-BASH41-RANDOM-AUTOSEED]] [[R40-B1-BASH40-RANDOM-AUTOSEED]] [[R40-B1-BASH32-RANDOM-AUTOSEED]] [[R40-B1-BASH51-RANDOM-AUTOSEED]] [[R32-B1-BASH42-RANDOM-AUTOSEED]] [[R36-B1-ORBIT-12REG]]"
    cs[4] = "a bash 3.2 binary confirming the generator, a PIE-orbit sweep, a pid_max extension, or a stated offset with its own plant-and-recover control"
edit("| Other bash versions and seedings", f_bash)


def f_en(cs):
    cs[0] = "English-only and legacy-beam matrix cells still not re-scored under panel-R36"
    cs[1] = ("8 TRIED-English cells whose reading was not re-scored: H4xF3, L2xF3, L15xF2 (R14 and R15: the code exists under `archive/branches-2026` and `corpus/H-branch-recovery`, so these are re-scorable, not run), "
             "H7xF9 (dated pad data), H12xF7 (2012-14 book texts), L12xF5, L13xF5, S1xF5 (R31: 5-9-rune readouts below the 32-rune panel floor); 4 PARTIAL cells (H2xF7, H4xF6, H7xF4, H8xF4: one reading inconclusive or open); the R13 DIRECTION reading is filed open")
    cs[2] = "partial"
    cs[3] = "[[R36-O4-CLUE-COVERAGE]] [[R40-C1-R13-R9-DIRECTION-WALKS]] [[R40-C1-INCONCLUSIVE-R14]] [[R40-C1-INCONCLUSIVE-R15]] [[R40-C1-INCONCLUSIVE-R31]] [[R40-C1-INCONCLUSIVE-R35]] [[R40-C1-INCONCLUSIVE-R36]] [[R40-C1-INCONCLUSIVE-R44]]"
    cs[4] = "re-score R14 and R15 from the archived code; supply the R35 key texts (`round12/C2/texts`), the R36 dated pad data and the R44 book texts; a human read of the R13 400-rune stream"
edit("| English-only and legacy-beam rows not yet re-scored", f_en)

# ---- pins
pins = ["R40-B1-BASH32-RANDOM-AUTOSEED | 76,237,568", "R40-B1-BASH51-RANDOM-AUTOSEED | 92,274,688", "R40-B1-BASH32-RANDOM-AUTOSEED | 7.098", "R40-B1-BASH51-RANDOM-AUTOSEED | 6.522",
        "R40-B1-BASH41-RANDOM-AUTOSEED | 7.065", "R40-B3-B04-REDECODE | 6.336", "R40-B3-B04-REDECODE | 6.049", "R40-B3-R16KDF-REDECODE | 6.528", "R40-B3-R16KDF-REDECODE | 692064",
        "R40-B3-R17-PUBLIC-PAD-REDECODE | 5.745", "R40-B3-COSPAD-REDECODE | 6.066", "R40-C1-R13-R9-DIRECTION-WALKS | 4.733", "R40-C1-R32-B04-SLOGAN-SEEDS | 4625920",
        "R40-I1-REPLANT-CONTROLS | EN_NOVOWEL 1/10"]
k = max(i for i, l in enumerate(src) if l.startswith("<!-- pin:"))
src[k + 1:k + 1] = ["<!-- pin: %s -->" % p for p in pins]
open(os.path.join(LP, "MEASURED-CEILING.md"), "w", encoding="utf-8").write("\n".join(src))
print("page written; rows", NROWS)
