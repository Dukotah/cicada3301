"""Round 39 X1: scope/power corrections to MEASURED-CEILING.md (each substitution asserted to match exactly once)."""
import sys
sys.dont_write_bytecode = True
p = r"C:\Users\Jeff\cicada3301\liber-primus\MEASURED-CEILING.md"
raw = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw else "\n"
lines = raw.replace("\r\n", "\n").split("\n")


def sub1(lineno, old, new):
    i = lineno - 1
    assert lines[i].count(old) == 1, (lineno, old, lines[i].count(old))
    lines[i] = lines[i].replace(old, new)


def tag(lineno, scope):
    i = lineno - 1
    l = lines[i]
    cut = l.index("[[")
    pre, post = l[:cut], l[cut:]
    k = pre.rindex("panel-R36")
    pre = pre[:k + 9] + " [plants: " + scope + "]" + pre[k + 9:]
    lines[i] = pre + post


def rep(t, old, new):
    assert t.count(old) == 1, (old[:60], t.count(old))
    return t.replace(old, new)


# header
sub1(3, "(256 rows)", "(261 rows after the X1 audit)")

# section 1
sub1(31, "(pooled control, not per-register);", "(pooled control, not per-register; the R37 control names four registers, so the row's own count of seven is unreconciled); earlier controls also failed in places (R32-I1 EN_NOVOWEL 0.72 / 0.71 under `skip_by_two` before the R33 repair; R34-I1 `free` failed at L=120 and at L=31);")
# 2a
sub1(49, "(assumed for seven registers)", "(assumed for seven registers per the row; its control names four)")
sub1(51, "tier overall reach about 0.98-0.99;", "tier overall reach about 0.98-0.99 at the best registers and about 0.95 at the lowest (20.3 % of seeds decoded unfiltered, 79.7 % through pf_v4 at the 0.940 minimum); the row's PHP plants cover EN_MODERN and EN_NOVOWEL only;")
sub1(51, "**excluded at power 0.98** (nine registers)", "**excluded at power 0.95-0.99** (nine registers; 0.98 is the best case; v3 recovery assumed for the other seven; HALFVOWEL and LATIN unmeasured)")
sub1(53, "K4 parity 0.0 across 10,971 re-scores)", "K4 parity 0.0 across 10,971 re-scores; the plant is a single held-out English text, the false-reject sample is 0 of 6; non-English power is the panel's own, min 0.92 at L=120 on the rebuilt sibling panel, not planted through this engine)")
sub1(53, "**excluded at power 1.00** (Round 19 panel)", "**excluded at power 1.00** (English plant; other registers at panel level only)")
sub1(54, "Exact-relation control 3/3 independent of the engine flag;", "Exact-relation control 3/3 independent of the engine flag (English plaintext plants);")
sub1(54, "**measured negative** (47.95 % cumulative, mixed instrument)", "**measured negative** (3.809 pp under panel-R36; the 44.138 % Round 19-gated part predates any exact-relation control and was not re-scored; 47.95 % is a mixed-instrument cursor sum)")
sub1(57, "**excluded at power 1.00** (English register);", "**excluded at power 1.00** (English register and the one-symbol-per-rejection relation only: the same beam recovers 0.258 of a `skip_by_two` plant, so these grids carry no stated power under `skip_by_two` outside the R24 slice);")
sub1(62, "Planted control passed |", "Planted controls recovered 1.000 (`keyskip1`) and 0.996 (`skip_by_two`) on the real pad bytes; the `keyskip1` beam alone recovers 0.071 of the `skip_by_two` plant |")
sub1(62, "English-leaning panel of that round", "nine-register panel of that round")
sub1(63, "English plaintext only; the date-indexed join key", "English plaintext only: the R17 dense prefilter kept the true offset in 5 of 8 planted pads (measured survival 0.375-0.875, English plants), and 14,522,916,046 offsets were scored of which about 8.38e9 effective; the date-indexed join key")
# 2b register tags
tag(69, "EN_MODERN only")
tag(70, "EN_MODERN only")
tag(71, "EN_MODERN only")
tag(76, "EN_MODERN only")
tag(77, "EN_MODERN only")
tag(78, "EN_MODERN / LATIN / GREEK only")
tag(80, "EN_MODERN / LATIN / GREEK only")
# 75: semantic address incl. C1 R39
sub1(75, "Semantic address: \"meaning\" as a frozen public lexical address (WordNet 3.1 first-synset offset; Norvig frequency rank)", "Semantic address and sense position: \"meaning\" as a frozen public lexical address (WordNet 3.1 first-synset offset; Norvig frequency rank) and as sense position (first-synset hypernym depth; lexicographer-file index)")
sub1(75, "28,224 decodes per variant set, pages 0-2, `keyskip1`, L=120", "R38: 28,224 decodes per variant set; R39: 14,112 decodes; pages 0-2, `keyskip1`, L=120")
sub1(75, "36/36 planted variants recovered; best 5.296 vs 7.85", "R38 36/36 and R39 18/18 planted variants recovered; best 5.296 vs 7.85 (R38) and 5.351 vs 7.59 (R39)")
sub1(75, "(an offset is a file address, not a sense; the frequency-rank row is not a reading of \"meaning\")", "(an offset is a file address, not a sense; the frequency-rank row is not a reading of \"meaning\"; depth and lexicographer file are two sense features, not a pairwise similarity; the lemma rule maps 22 \"is\" tokens to the noun \"i\")")
sub1(75, "[[R38-C1-SEMANTIC-WORDNET]] [[R38-C1-SEMANTIC-FREQRANK]]", "[[R38-C1-SEMANTIC-WORDNET]] [[R38-C1-SEMANTIC-FREQRANK]] [[R39-C1-SENSE-SIMILARITY]]")
sub1(75, "**measured negative** (address-type readings only)", "**measured negative** (address-type and first-synset sense-position readings only)")
sub1(75, "a determinate sense-level reading is stated (see section 3, sense similarity)", "a pairwise-similarity, multi-sense, other-lexicon or clue-specific reading is stated (section 3)")
tag(75, "EN_MODERN only")
# 78 / 80 / 79
sub1(78, "(N3 whole-book integer structure is inconclusive)", "(N3 whole-book integer structure is inconclusive; N2 and N4 used a post-data null: the first-pass plain-shuffle family p of 0.003-0.007 became 0.41-0.50 under the doublet-matched null, so `threshold_fixed_in_advance` is false for them)")
sub1(80, "**measured negative** | a width other than 4", "**measured negative** (post-data null: the doublet-matched null replaced a plain-shuffle null after the first-pass results; `threshold_fixed_in_advance` is false for R37-C3-U6B-R22C) | a width other than 4")
sub1(79, "**measured negative** (noise-crosser; human read pending)", "**inconclusive** (a flagged-for-oracle bundle awaits the owner's read, expected noise-crosser; the matched null is fixed-config with 22-30 draws per family at L=240, so anti-conservative)")
t = "\n".join(lines)
t = rep(t, "refuses a strong verdict that cites a row without a passed positive control and a coverage\nstatement, and refuses the foreclosure vocabulary.",
        "refuses a strong verdict that cites a row without a passed positive control and a coverage\nstatement (and, after the Round 39 X1 audit, without a fixed-in-advance threshold or a stated `post-data null`, and without a\n`[plants: ...]` scope where the row's controls are register-narrow), and refuses the foreclosure vocabulary.")
t = rep(t, "and pointed it\nat every enumerable key family the ledger names and every clue reading the clue matrix found untried.",
        "and pointed it\nat the enumerable key families and clue readings listed in section 2 (section 3 lists the enumerable ones it has not finished, for example the Marsaglia CDROM, and the clue cells run only once).")
t = rep(t, "`not excluded`: outside every\nswept space.",
        "`not excluded`: outside every\nswept space. A `[plants: ...]` tag in a conditionals cell names the only registers the cited positive controls planted: the adjudicator may span\ntwelve registers while the measured power is for those registers alone.")
# section 3 rows 97-98 (Round 39 not run)
t = rep(t, "recover window 2 from its snapshot (after the quota reset, before about 2026-11-07), then persistent-session windows |",
        "recover window 2 from its snapshot (after the quota reset, before about 2026-11-07), then persistent-session windows (Round 39 did not run S1/S2: moved to Round 40) |")
t = rep(t, "| partial | [[R38-S1-S2-WINDOWS]] [[R36-S1-S2-WINDOW]] |", "| partial | [[R38-S1-S2-WINDOWS]] [[R36-S1-S2-WINDOW]] [[R39-S1-S2-WINDOWS]] |")
t = rep(t, "| unmeasured | [[R38-S2-PHP-SANDBOX]] [[R36-B2-PHP-AWAKE-PFV4]] | the retry harness: control and FPR persisted first,",
        "| unmeasured | [[R38-S2-PHP-SANDBOX]] [[R36-B2-PHP-AWAKE-PFV4]] [[R39-S1-S2-WINDOWS]] | the retry harness (not run in Round 39; moved to Round 40): control and FPR persisted first,")
# section 3 sense row
old = [l for l in t.split("\n") if l.startswith("| The 18 sense-similarity cells")]
assert len(old) == 1
new = ("| The 18 F5 cells beyond one generic operationalization (hypernym depth, synonym class, lemma-sense count, gloss length, all senses, pairwise similarity, clue-specific content) | "
       "Round 38 C1 (address) and Round 39 C1 (first-synset hypernym depth, lexicographer-file index) read only \"their meaning is the road\" (H3 x F5); the 18 other F5 cells are clue-specific semantic readings never run, now PARTIAL (one generic reading of the family), not TRIED; "
       "non-first senses, other lexicons and pairwise metrics untested | partial | [[R39-C1-SENSE-SIMILARITY]] [[R36-O4-CLUE-COVERAGE]] [[R38-X1-REDTEAM]] | each cell's own clue content operationalized with a frozen lexicon and per-variant planted controls |")
t = t.replace(old[0], new)
# new section 3 rows after the ciphertext-side channels row
anchor = [l for l in t.split("\n") if l.startswith("| Ciphertext-side channels the readers cannot see")]
assert len(anchor) == 1
add = [
    "| The Marsaglia Random Number CDROM as a public pad (63 verified random-data files; 756 pad x builder x byte-order units) | 77 of 756 units swept (1.54e9 offsets, best -6.74 vs bar -5.38 on the legacy English scorer); the R20 scaffolded lane swept 0 of 679 units | partial | [[B-13-MARSAGLIA]] [[R20-SMARS-SCAFFOLDED]] | the remaining units under beam_v3 and panel-R36 (about 21 CPU-hours for the 679-unit lane) |",
    "| The input and cipher-class assumptions of every row above: the 12,956-rune canon is correct (cross-verified in Round 19, scoped to the LP2 typeface by Round 32 X1, p27:93 unresolved) and the cipher is a mod-29 additive stream | 450 located O/A/AE disagreements never decided per instance; a homophonic-downward (surjective 29 to k) search never coded; a non-additive ciphertext-feedback sweep run on 3 of 55 pages | not excluded | [[A-02]] [[B-13]] [[D-03]] [[D-04]] | per-instance human adjudication of the 450 calls; the specified annealing / EM search; the feedback sweep over all pages |",
    "| Limits stated in section 1 but not repeated above: v3 recovery of seven registers assumed at orbit level; `free` at L=240 unlicensed for OE and EN_HALFVOWEL; the 12-register PHP-cell false-positive rate logged but never persisted | orbit-level v3 plants for four registers only; OE 3/20 and EN_HALFVOWEL 7/20 control recovery at L=240; pooled FPR 8.58e-4 (450/524,288) in sandbox logs only | partial | [[R37-I2-PFV4-12REG-ORBIT]] [[R37-I1-FREE-NULL-LMATCHED]] [[R38-S2-PHP-SANDBOX]] | per-register v3 plants at orbit level; `free` nulls and controls for OE / EN_HALFVOWEL at L=240; the PHP retry persists control and FPR first |",
]
t = t.replace(anchor[0], anchor[0] + "\n" + "\n".join(add))
# section 5
t = rep(t, "python data/fetch_sources.py                                                  # 1. fetch the gitignored transcription sources\npython analysis/round36/I1-new-registers/fetch_r36.py && \\\n  python analysis/round36/P1-panel-r36/build_r36.py analysis/round36/P1-panel-r36/build1   # 2. build panel-R36 (npz sha256 a0682f0c...)",
        "python data/fetch_sources.py --r19 --welsh --r36                              # 1. fetch the gitignored transcription sources plus the sha-pinned panel corpora\npython analysis/round36/P1-panel-r36/build_r36.py analysis/round36/P1-panel-r36/build1   # 2. rebuild panel-R36 (npz sha256 a0682f0c...); optional, see below")
t = rep(t, "A fresh clone carries a committed copy of the panel (`data/panels/panel-r36.npz`), so step 4 runs without step 2.",
        "A fresh clone carries a committed copy of the panel (`data/panels/panel-r36.npz`), so step 4 runs without step 2. Step 2 reproduces the committed sha only if every pinned input reproduces: `--welsh` aborts if the Gutenberg mirror drifted from the pinned sha, and the original Welsh corpus is unrecoverable (CY is a substitute); the unpinned `fetch_r36.py` is not used here because it would overwrite the sha-pinned corpora.")
# pins
pins = ["<!-- pin: R39-C1-SENSE-SIMILARITY | N=14112 -->", "<!-- pin: R39-S1-S2-WINDOWS | moved to Round 40 -->", "<!-- pin: B-13-MARSAGLIA | \"done\": 77 -->",
        "<!-- pin: R37-C3-U6A-N2 | \"threshold_fixed_in_advance\": false -->", "<!-- pin: R37-C3-U6A-N4 | \"threshold_fixed_in_advance\": false -->", "<!-- pin: R37-C3-U6B-R22C | \"threshold_fixed_in_advance\": false -->",
        "<!-- pin: R38-C2-N5N4-L240 | PENDING OWNER -->", "<!-- pin: R24-C2-SKIP-BY-TWO-DECODER | 0.258 -->", "<!-- pin: R17-PUBLIC-PAD | 5/8 -->",
        "<!-- pin: R36-B2-PHP-AWAKE-PFV4 | 20.3 % unfiltered -->", "<!-- pin: R27-CPORT-MT32-FULLSWEEP | held-out English -->"]
t = t.rstrip("\n") + "\n" + "\n".join(pins) + "\n"
open(p, "w", encoding="utf-8", newline="").write(t.replace("\n", nl))
print("ok")
