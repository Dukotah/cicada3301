"""X1/R34 nav-doc edits (idempotent). Original text kept; supersessions marked, not deleted."""
import re, io
ROOT = 'C:/Users/Jeff/cicada3301/'
LP = ROOT + 'liber-primus/'
GS_NOTE = ("~~9.04\u20139.14~~ \u2192 9.05\u20139.14 (render level, R34-S1: 9.04 ships the e409cef1 srgb.icc file, which was "
           "R18-L1's evidence, but its jpeg device does not embed it; 9.05 first does; one synthetic page, gcc-15 build, no pin inside 9.05\u20139.14)")
TOKEN = re.compile(r'9\.04[\u2013-]9\.14')


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def gs_line(path, lineno, must):
    s = rd(path)
    nl = '\r\n' if '\r\n' in s else '\n'
    L = s.split(nl)
    ln = L[lineno - 1]
    if 'R34-S1' in ln:
        return 'already'
    assert must in ln, (path, lineno, ln[:80])
    L[lineno - 1] = TOKEN.sub(GS_NOTE, ln, count=1)
    wr(path, nl.join(L))
    return 'ok'


print(gs_line(LP + 'README.md', 74, 'GS 9.04'))
print(gs_line(LP + 'PICKUP-HERE.md', 90, 'GS 9.04'))
print(gs_line(ROOT + 'README.md', 329, 'GS 9.04'))
print(gs_line(LP + 'analysis/README.md', 76, 'GS 9.04'))
print(gs_line(LP + 'analysis/README.md', 58, '9.04'))
print(gs_line(LP + 'ELIMINATION-LEDGER.md', 1060, 'GS 9.04'))
# root PICKUP-HERE line 459 (Round 18 table row)
p = ROOT + 'PICKUP-HERE.md'
s = rd(p)
nl = '\r\n' if '\r\n' in s else '\n'
L = s.split(nl)
for i, ln in enumerate(L):
    if ln.startswith('| **L1** | Toolchain forensics') and 'R34-S1' not in ln:
        L[i] = TOKEN.sub(GS_NOTE, ln, count=1)
        print('root PICKUP row', i + 1)
        break
wr(p, nl.join(L))

# ---- liber-primus/PICKUP-HERE.md banner -----------------------------------------------------------------------------
p = LP + 'PICKUP-HERE.md'
s = rd(p)
nl = '\r\n' if '\r\n' in s else '\n'
if 'Round 34 X1 (2026-10-29)' not in s:
    marker = '> **Round 33 X1 (2026-10-29):**'
    assert marker in s
    banner = nl.join([
        "> **Round 34 X1 (2026-10-29) red-team corrections** (details and citations: `analysis/round34/X1-redteam/RESULTS.md`):",
        ">",
        "> - **R34 I2's \"the real ciphertext head is skip-free\" is WRONG.** `U[:40]` (and `U[:120]`) really have zero doublets, but a key skip is *invisible* in the emitted ciphertext (it happens when the candidate rune would equal the previous one). In 600 R32-style plants per cell, 37-51 % of heads contain a skip inside m = 18-24 and that holds even among plants whose cipher head has no doublet. The operative prefilter power of I2's screen is **about 0.66 EN_NOVOWEL / 0.71 EN_MODERN at FPR 1e-3, not 0.998**; R32-B1's 0.47 NOVOWEL is *not* a plant artefact (re-run reproduces 0.555-0.62). B1's reach must be stated from the with-skip column. A skip-tolerant head screen is the open lever.",
        "> - R34 I1's \"Q5 fired\" compared v3's z-scored `pmax` with R32 I3's raw quadgram exponent (-0.55); z-normalisation adds ~+0.5, predicting ~-0.05 (observed -0.105 / -0.136): a false alarm, not evidence of a non-Gumbel tail. The Gumbel bars hold (conservative) at L <= 240 and are not shown conservative at L = 400.",
        "> - R33 I2's \"earned\" relations (`keyskipk`, `decode_with_resets`) are **struck**: the doublet prior is non-discriminating, so nothing is earned (completeness ritual, last in queue).",
        "> - Ghostscript render band is now **9.05-9.14** (R34 S1); ~~9.04-9.14~~ was file-in-tree evidence, S1 measured ICC embedded in the jpeg output (9.04 does not embed it). Synthetic page only; O1 is live, not solved.",
        "> - Capsule: the 13 INTACT-FAIL items are settled (`analysis/round34/X1-redteam/manifest_decision.md`): 9 CRLF checkout noise (fix the checker), `runes.canonical` stale by the issue-12 edit, `tests/validate.py` grew by exactly the Round 19 AN-END guard (refresh the manifest), `kjv`/`mabinogion` are Round 32 I2's substitute copies. Payload rename: GO (P1, nothing flipped); `C-CANON-PAYLOAD-3BYTES` stays `open` until the coordinator renames.",
        ""])
    s = s.replace(marker, banner + nl + marker, 1)
    wr(p, s)
    print('pickup banner ok')

# ---- analysis/README.md row -------------------------------------------------------------------------------------------
p = LP + 'analysis/README.md'
s = rd(p)
nl = '\r\n' if '\r\n' in s else '\n'
if 'round34/X1-redteam' not in s:
    L = s.split(nl)
    for i, ln in enumerate(L):
        if ln.startswith('| [`round33/X1-redteam/`]'):
            row = ("| [`round34/X1-redteam/`](round34/X1-redteam/) | **Round 34 X1 - red-team (R6) 2026-10-29** | Refute-by-default over B3, the Round 33 I2 \"earned\" relations, the 13 capsule INTACT-FAIL items and this round's lanes. "
                   "**FOUND-ERROR:** R34 I2's \"the real head is skip-free\" (a key skip is invisible in the ciphertext; operative prefilter power ~0.66 NOVOWEL / 0.71 EN_MODERN, not 0.998; R32-B1's 0.47 reproduces); R34 I1's Q5 comparator (z-score vs raw quadgram exponent - false alarm); R33 I2 \"earned\" relations struck; P1 wording on R30-B2 gpg stdout; GS band 9.04-9.14 superseded by 9.05-9.14 at render level (S1). "
                   "**NO-ERROR-FOUND:** B3 row counts (404,284 = 192,066 + 212,218; 994 duplicate B2 rows), I3 pooled Wilson (3/100, [0.010, 0.085]; threshold not re-tuned), S1 PHP 5.6 value 1244335972, P1 verdict (GO). Capsule: validate.py growth = exactly the R19 AN-END guard (removing it reproduces the manifest sha); kjv/mabinogion = Round 32 I2 substitutes. Re-runs and `manifest_decision.md` (not applied) are in the folder. |")
            L.insert(i + 1, row)
            break
    wr(p, nl.join(L))
    print('analysis README row ok')

# ---- ELIMINATION-LEDGER.md ------------------------------------------------------------------------------------------
p = LP + 'ELIMINATION-LEDGER.md'
s = rd(p)
nl = '\r\n' if '\r\n' in s else '\n'
a = "`keyskipk` relation + segmentation wrapper is a queued completeness ritual (R4), not merged."
if a in s and 'X1/R34' not in s.split(a)[1][:200]:
    s = s.replace(a, a + " **[X1/R34: \"earned\" STRUCK - the doublet prior is non-discriminating (every construction 0.88-1.00x skip_by_two's error, so the \"within 2x\" gate is vacuous); representability numbers reproduce (two cells re-run bit-identical). Nothing is earned; ritual, queued last.]**", 1)
b = "- **R33-O1** Ghostscript 9.04\u20139.14 render byte-compare: PREREG only, queued for a build box."
if b in s:
    s = s.replace(b, b + " **[R34-S1 ran the synthetic-page form: the jpeg device embeds the e409cef1 ICC from gs 9.05, not 9.04; O1 live on that input only.]**", 1)
if '## Round 34 X1 corrections' not in s:
    block = nl.join([
        "", "",
        "## Round 34 X1 corrections (2026-10-29)", "",
        "Refute-by-default audit; citations and re-runs in `analysis/round34/X1-redteam/RESULTS.md`.",
        "- **R34 I2 prefilter reach** (FOUND-ERROR): the lane's \"real `U[:40]` has no doublets, so the true-key head is skip-free, so the operative power is 0.998\" is wrong. `U[:40]` and `U[:120]` do have zero doublets, but a key skip is invisible in the emitted ciphertext; 37-51 % of true-key heads of 18-24 runes contain a skip, with or without a cipher doublet. Operative power of the lse m=20 screen is ~0.66 EN_NOVOWEL / ~0.71 EN_MODERN at FPR 1e-3 (the lane's own with-skip column). R32-B1/B2's 0.47 NOVOWEL is **not** a planting artefact (R32 logic re-run: 0.555-0.62). R32-B1 RESULTS and ledger row stand unchanged. Lever left: a skip-tolerant head screen.",
        "- **R34 I1 Q5**: the -0.55 exponent was fitted on a raw legacy quadgram score; v3 `pmax` is a per-length z-score (sd ~ n^-1/2), predicting ~-0.05; observed -0.105/-0.136. The trigger was a comparator error, not a non-Gumbel tail. Gumbel bars conservative at L <= 240, not shown at L = 400. R33 B3's bars were 0.08-0.28 below I1's at N = 202,142 (not material; best row 7.068).",
        "- **R33 I2 \"earned\" relations** struck (see the R33 block above).",
        "- **Ghostscript band**: render-level 9.05-9.14 (R34-S1); 9.04-9.14 is file-in-tree evidence (R18-L1) and is superseded for the render claim. R18-L1's `RESULTS.md` is annotated by this ledger, not rewritten.",
        "- **Capsule** INTACT-FAIL (13): 9 CRLF checkout noise; `runes.canonical` stale by the issue-12 separator edit; `tests/validate.py` grew from 3,607 B to 5,133 B by exactly the Round 19 AN-END (73.jpg) guard (removing it reproduces the recorded sha) - refresh the manifest; `corpus.kjv` / `keytext.mabinogion` are Round 32 I2's substitute copies of different downloads. Memo: `analysis/round34/X1-redteam/manifest_decision.md` (not applied).",
        "- **P1**: no reader changed; GO for the `payload_resolved.bin` rename recommended. R30-B1 canon-as-key over T2/folly and R30-B2 folly/2.jpg legs are **unmeasured** (inputs absent), not null. `C-CANON-PAYLOAD-3BYTES` stays `open` until the coordinator renames.",
        ""])
    s = s.rstrip('\r\n') + block
    wr(p, s)
else:
    wr(p, s)
print('elimination ok')
