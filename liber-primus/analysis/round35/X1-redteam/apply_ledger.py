"""X1/R35: merge audited Round 35 rows + patches into LEDGER.json (idempotent; originals kept in *_original / x1_r35 fields)."""
import json, collections, copy
LP = 'C:/Users/Jeff/cicada3301/liber-primus/'
A = LP + 'analysis/round35/'
LJ = LP + 'LEDGER.json'
L = json.load(open(LJ, encoding='utf-8'))
E = {e['id']: e for e in L['entries']}
new = []
ev = lambda *p: ['liber-primus/analysis/round35/' + x for x in p]


def add(row):
    if row['id'] in E:
        return
    new.append(row)
    E[row['id']] = row


def append_text(e, key, txt):
    if txt and txt not in str(e.get(key, '')):
        e[key] = (e.get(key) or '') + txt


def replace_nc(e, containing, repl):
    nc = e.get('not_covered')
    if isinstance(nc, list):
        for j, it in enumerate(nc):
            if containing in it:
                nc[j] = repl
                return True
        if repl not in nc:
            nc.append(repl)
    return False


# ---- I1
add({
    "id": "R35-I1-PFV4-SKIP-TOLERANT-SCREEN", "lane": "round35/I1", "round": 35, "date": "2026-10-30", "status": "measured",
    "hypothesis": "A skip-tolerant head screen (Viterbi over key advance 1/2, k<=2 skips, lse over nine registers) lifts head-screen power on NATURAL-rate plants (heads containing key skips at the real rate) to EN_NOVOWEL>=0.85 / others>=0.90 at FPR<=1e-3, where pf_v3 passes with-skip heads at only 0.19-0.34.",
    "verdict": "BAR MET at the frozen point (m=24, k=2, relation-agnostic OR of keyskip1/keyskip2 screens, pen 2 nats/skip) - at 10.9x pf_v3's cost, not the <=3x target",
    "result": "Held-out natural power at FPR 1e-3: EN_NOVOWEL 0.98, min other EN_HALFVOWEL 0.948 (keyskip1 and keyskip2 plants; with-skip 0.92-0.99; pf_v3-equivalent natural 0.65-0.78). Held-out FPR 8.4e-4 pooled, no generator above 1e-3 (bash LP64 7.8e-4, ILP32 9.2e-4). k=0 reproduces pf_v3.lse_stat to max |diff| 0.0. Cheaper alternative (24,1,both) 3.5x meets the bar only at FPR 3e-3. X1/R35 re-ran EN_NOVOWEL / EN_HALFVOWEL keyskip2 (300 plants each, own seed) at the frozen thresholds: 0.973 / 0.970; fresh-seed FPR 8.7e-4 (LP64) / 7.8e-4 (ILP32) on 2^16 heads.",
    "coverage": "m in {20,24} x k in {0,1,2} x relation {keyskip1,keyskip2,both} x pen {0..3}; 2000 plants per register x 9 registers x 2 relations through the real encipherer (bash LP64 keystream), 1000 calibration / 1000 held-out; nulls 131,072 per generator x six generators (bash LP64/ILP32, four PHP cells), thresholds on half A, FPR on half B.",
    "not_covered": ["heads past 24 runes", "3+ skips in the head at k=2", "free relation and any construction outside keyskip1/keyskip2", "registers outside the nine", "generators outside the six", "PHP and ILP32 plant power (plants use the bash LP64 keystream; FPR is measured on all six)", "other ciphertext heads (thresholds are calibrated against the real C[:24]; recalibrate)", "the beam's own recovery is a separate factor (0.98-1.00 at L>=120)"],
    "threshold": "EN_NOVOWEL>=0.85 and every other register>=0.90 on held-out natural-rate plants at FPR<=1e-3 (PREREG, fixed before output; PREREG mtime 09:29:26, first pf_v4.py 09:29:48)",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "positive_control_note": "natural-rate plants through the real encipherer; k=0 reproduces pf_v3 exactly; X1/R35 independent re-run reproduces the frozen-point power within 2 SE",
    "reopens_if": "a screen is needed beyond 24 runes, at lower cost (<=3x), for ciphertext heads other than C[:24], or for constructions outside keyskip1/keyskip2.",
    "evidence": ev("I1-skip-tolerant-screen/RESULTS.md", "I1-skip-tolerant-screen/PREREG.md", "I1-skip-tolerant-screen/roc.json", "I1-skip-tolerant-screen/roc_both.json", "I1-skip-tolerant-screen/frozen_op.json", "I1-skip-tolerant-screen/power_per_register.json", "I1-skip-tolerant-screen/throughput.json", "X1-redteam/rerun_i1.json"),
    "x1_r35": "NO-ERROR-FOUND. run.py plants are natural-rate (run.py enc1/enc2 + the plant loop: no skip-free or doublet-free selection anywhere; windows are random testhalves offsets; the only split is calibration (i<1000) vs held-out). Re-run with an independent seed/encipherer (common.enc_pair / sk.encipher_keyskip): EN_NOVOWEL keyskip2 300 plants 0.973 (lane 0.980), EN_HALFVOWEL 0.970 (lane 0.949, +1.7 SE), pf_v3-equivalent 0.73 / 0.64 on the same plants; k=0 vs pf_v3 max|diff| 0.0 over 1000 heads; fresh-seed FPR 57/65,536 = 8.7e-4 (LP64), 51/65,536 = 7.8e-4 (ILP32). roc_both.json (24,1) alternative reproduces RESULTS (NOVOWEL 0.907, min other 0.889 @1e-3; 0.922/0.902 @3e-3)."
})

# ---- P1
add({
    "id": "R35-P1-R19-PANEL-RESTORE", "lane": "round35/P1", "round": 35, "date": "2026-10-30", "status": "measured",
    "hypothesis": "The Round 19 panel (round19/I2/models/panel.npz, sha 14a23d36...) can be rebuilt byte-exact by re-fetching the original corpora recorded in round19/I2/out_build.json.",
    "verdict": "NO-MATCH, panel NOT rebuilt. Two of the three substituted corpora restored byte-exact; the Welsh CY corpus is UNRECOVERABLE (tried, not found)",
    "result": "data/kjv.txt = gutenberg.org/files/10/10-0.txt raw, sha 0f1a83cb... 4,436,268 B == recorded; data/keys/mabinogion.txt = gutenberg.org/files/5160/5160-0.txt raw, sha 80dc6f0d... 617,362 B == recorded (the cache/epub URLs give the 4,455,950 / 617,553 B substitutes). The other 8 corpora already matched. CY = data/keys/welsh/welsh_mabinogion.txt, recorded sha 4b3fd926... 524,561 B: no source URL was ever recorded; six archive.org OCR candidates (Rhys-Evans x3, Edwards x2, Pedeir Keinc; 152k-671k B) match neither size nor hash; the on-disk file (761,030 B, sha 624ffc97...) is the Round 32 modern-Welsh substitute. No per-model hashes are recorded, so no partial panel comparison is possible. Q5 stop; the power gate and S1 were not run.",
    "coverage": "11 recorded corpus inputs checked against out_build.json (10 match byte-exact after the restore, 1 unrecoverable); 2 Gutenberg URL forms x 2 corpora; 6 archive.org Welsh candidates.",
    "not_covered": ["Welsh CY corpus 4b3fd926... / 524,561 B: unrecoverable from this checkout, GitHub and the public mirrors tried (other checkouts or backups unsearched beyond ._round31_stale_backup, which holds no corpus)", "numpy .npz byte-determinism of a rebuild was untestable (no rebuild)", "per-model hashes (never recorded)"],
    "threshold": "sha256(panel.npz) == 14a23d36... (binary recognizer)", "threshold_fixed_in_advance": True,
    "reopens_if": "the original welsh_mabinogion.txt (4b3fd926..., 524,561 B) turns up (another checkout, backup or clone), or a decision is taken to re-gate the S2 engine on a NEW panel with a recorded build (a governance change, not a hack).",
    "evidence": ev("P1-restore-r19-panel/RESULTS.md", "P1-restore-r19-panel/PREREG.md", "P1-restore-r19-panel/fetch_log.json", "P1-restore-r19-panel/panel_sha.json", "P1-restore-r19-panel/manifest_patch.json", "X1-redteam/RESULTS.md"),
    "x1_r35": "FOUND-ERROR (substantive) x2, fixed. (1) RESULTS says 'No files written outside the lane dir ... substitutes untouched' but data/kjv.txt, data/keys/mabinogion.txt, data/fetch_sources.py and handoff/capsule/MANIFEST.json were replaced/edited at 09:31 (after RESULTS, 09:30:29); the Round 32 substitutes now live only in round35/P1-restore-r19-panel/backup/ (sha 0204adae... / e177d7c2...), so Round 32's recorded EN_KJV/EN_MODERN corpus hashes no longer match data/. (2) data/fetch_sources.py contained NO fetch for KJV/Mabinogion; P1's edit changed the Welsh SUBSTITUTE URLs from cache/epub to /files/N/N-0.txt (bytes differ by ~20 KB: 781,166 vs 761,024 B), which broke that recipe. X1 reverted the Welsh URL form and added ensure_r19_corpora() (sha-verified, --r19), tested against live Gutenberg. Hash chain otherwise NO-ERROR-FOUND: sha256(data/kjv.txt)=0f1a83cb.., sha256(mabinogion.txt)=80dc6f0d.. recomputed against out_build.json (10/11 corpora equal); capsule verifier PASS (89 OK, 14 ABSENT, 1 SKIP)."
})

# ---- S1 (skipped)
add({
    "id": "R35-S1-S2-WINDOW", "lane": "round35/S1", "round": 35, "date": "2026-10-30", "status": "never-run",
    "hypothesis": "With the Round 19 panel restored, the fixed grind27 engine passes --self-test and S2 (Py2.7-MT, exact/keyskip1) can be resumed for a stated sandbox window from 44.14 %.",
    "verdict": "SKIPPED with cause: P1 NO-MATCH (the Welsh CY corpus is unrecoverable, so panel.npz 14a23d36... cannot be rebuilt). S2 was NOT resumed; the parked state (44.14 %, 1,895,728,884 / 2^32) is untouched.",
    "result": "No run. No engine, self-test or sandbox action was taken in Round 35.",
    "coverage": "none (S2 remains PARKED at 44.14 %).",
    "not_covered": ["S2 resume (blocked on the Round 19 panel gate, recorded hash 14a23d36..., Welsh corpus 4b3fd926... / 524,561 B)"],
    "threshold": "n/a - not run", "threshold_fixed_in_advance": True,
    "reopens_if": "the original Welsh corpus is found, or the S2 engine is re-gated on a new panel with a recorded build (governance decision); then run the self-test (V1 64/64, V2 17.9312) and resume for a capped window.",
    "evidence": ev("CAMPAIGN-PLAN.md", "P1-restore-r19-panel/RESULTS.md")
})

# ---- B2
b2 = copy.deepcopy(json.load(open(A + 'B2-payload-legs/ledger.json', encoding='utf-8'))['entries'][0])
b2['evidence'] = ev("B2-payload-legs/RESULTS.md", "B2-payload-legs/PREREG.md", "B2-payload-legs/inputs.json", "B2-payload-legs/R30-B1/compare.json", "B2-payload-legs/R30-B2/compare.json")
b2['x1_r35'] = "NO-ERROR-FOUND. Identity caveat is on the row (not_covered #3 and the R30-B1/R30-B2 patch texts): T2.bin and 2.jpg are statistical/structural matches only (no full hash was ever recorded); sha256 of the staged copies recomputed (T2 35d31e61.., 2.jpg 74e955eb.., folly 7e5ec097..). Comparator legs spot-checked against round30/B1-blob-crypto/results.json: T2^canon fwd entropy 7.1666 and canon^folly rev 7.138 match the stored values exactly. Minor wording: RESULTS says 'the 8 canon rows moved by <=0.015 bits' while compare.json shows folly^canon:rev bit-identical at 4 d.p. (7.2487), so 7 of 8 moved; and compare.json gpg_raw differs from stored (declared: first-run keybox stderr / random salt)."
add(b2)
Pb = json.load(open(A + 'B2-payload-legs/ledger_patches.json', encoding='utf-8'))
for p in Pb['patches']:
    e = E[p['id']]
    append_text(e, 'coverage', p.get('coverage_append', ''))
    if 'not_covered_replace_item_containing' in p:
        replace_nc(e, p['not_covered_replace_item_containing'], p['not_covered_replacement'])
    e['x1_r35_b2'] = "R35-B2 patch applied after X1/R35 audit (NO-ERROR-FOUND); T2/2.jpg identity is statistical/structural only; folly.bin md5 prefix and the stored XOR rows reproduce."

# ---- R34-B1 corrections
e = E['R34-B1-ORBITS-V3-PFV3']
e.setdefault('coverage_original_r34', e['coverage'])
e['coverage'] = e['coverage'].replace("prior-dense 48,036 seeds fraction 1.000 (no prefilter)", "prior-dense 48,036 seeds fraction 1.000 (487 'core' seeds decoded unfiltered, 47,549 'dense' seeds went through the pf_v3 prefilter - R35 X1 correction)")
e['coverage'] = e['coverage'].replace("Store: 26,050 SWEEPROW rows (validate_store passes, check_r3_store []).", "Store: 26,050 SWEEPROW rows, ALL PHP; the 324,798 bash decodes were not persisted (R35 X1: the resumed invocation reopened the rows file with mode 'w'); bash numbers survive only in sweep_summary_final.json / keep_rows.json / sweep.log.")
e['notes'] = e['notes'].replace("PHP tier (b) log shows a 38,223 s gap (laptop slept) before SWEEP DONE; tier (b) did not advance past 2,621,440 seeds per cell.", "PHP tier (b) log: 1,966,080 seeds at t=110 s, 2,621,440 at t=38,223 s (the laptop slept inside the last block; the 2,100 s cap was consumed by wall-clock, not compute; at the pre-sleep rate the cap alone would have reached roughly 1 percent of 2^32). The first sweep invocation crashed at php_tier_a (NameError, sweep.log) and PHP ran in a resumed invocation.")
extra = "Per-seed bash rows (R3 persistence) were not stored: the store holds PHP rows only (R35 X1). The PHP prior-dense reach is NOT the beam's 0.98-1.00: 47,549 of 48,036 seeds went through pf_v3 (reach ~0.65-0.71 there too)."
nc = e['not_covered']
e['not_covered'] = (nc + ' ' + extra) if isinstance(nc, str) else (nc + [extra])
e['x1_r35'] = "FOUND-ERROR (mixed): (a) RESULTS/row call the PHP prior-dense tier 'decoded with no prefilter / reach ~1.00' - only the 487 core seeds are unfiltered; 47,549 dense seeds pass chunk_php (sweep.py:51-56, 200-212), so reach there is ~0.65-0.71; (b) the 38,223 s gap is misread: 2,621,440 is reached AT t=38,223 s, not t=110 s (sweep_php.log); the sleep consumed the 2,100 s cap, so the 0.061 % is an artefact of the sleep, not of the compute budget; (c) sweep_rows.jsonl holds only PHP rows (26,050): the resumed invocation truncated the store (sweep.py:161 mode 'w'; resume skips the bash loop) - R3 persistence for 324,798 bash decodes is lost and the row/RESULTS describe the store as complete; (d) the store header still says 'ILP32 stated fraction' (ILP32 ran 296/296) and carries power_EN_NOVOWEL 0.998 (superseded; RESULTS did not flag the header field); (e) 'bash phases took 911 s each': LP64 933.7 s, ILP32 911.1 s. NO-ERROR-FOUND on: 296/296 chunks of 2^18 = 77,594,624 per ABI (sweep.log 74+74 progress lines at every 4th chunk, sweep_summary.json chunks_done 296); the 12-cell table re-derived from sweep_summary_final.json; fraction 1.000; reach arithmetic (0.66-0.71 x 0.98-1.00 = 0.65-0.71); N_actual = survivors (81,414 / 80,985 / 3,190-3,297); 0.00061 = 2,621,440/2^32; the control caveat (sweep.py:70-71) is disclosed."

# ---- pointers
E['R34-I2-NOVOWEL-PREFILTER']['r35_i1'] = "R35-I1 built the skip-tolerant screen this row's reopens_if asked for (R35-I1-PFV4-SKIP-TOLERANT-SCREEN): natural-rate power 0.95-0.99 at FPR 1e-3 (m=24,k=2,both) at 10.9x pf_v3's cost. The B1 orbit re-screen with it had not completed at X1/R35 audit time."
E['R27-CPORT-MT32-FULLSWEEP']['r35_p1'] = "R35-P1 (2026-10-30): resume of S2 remains BLOCKED. The engine self-test gates on round19/I2/models/panel.npz (sha 14a23d36...), which needs the Welsh CY corpus (recorded sha 4b3fd926..., 524,561 B); that corpus is unrecoverable (R35-P1-R19-PANEL-RESTORE) and R35-S1 was skipped. S2 was NOT resumed in Round 35: still PARKED at 44.14 % (1,895,728,884 / 2^32)."
E['R34-S1-BUILD-BOX']['r35_p1'] = "R35-P1: the missing panel could NOT be rebuilt (Welsh corpus unrecoverable); S2 resume stays blocked on it. See R35-P1-R19-PANEL-RESTORE / R35-S1-S2-WINDOW."

add({
    "id": "R35-X1-REDTEAM", "lane": "round35/X1", "round": 35, "date": "2026-10-30", "status": "audit",
    "hypothesis": "Round 34 B1 (as written by the coordinator), R35 I1/P1/B2 and the lanes' pre-registration discipline contain errors that survive refute-by-default review.",
    "result": "FOUND-ERROR: R34-B1 x5 (PHP dense tier is prefiltered; 38,223 s gap misread; bash rows missing from the store; stale header fields; timing); P1 x2 (data/ files replaced contrary to RESULTS; fetch_sources.py had no KJV/Mabinogion fetch and its Welsh recipe was altered; both fixed). NO-ERROR-FOUND on I1 numerics and harness (natural-rate, re-run within 2 SE, k=0 identity exact, fresh FPR 7.8-8.7e-4), on B2 (identity caveat present; comparator numbers reproduce), on PREREG-before-output for I1/P1/B2/I3. B1-bash-orbit-pfv4 and I3 RESULTS not available at audit time (B1 directory absent; I3 mid-run).",
    "coverage": "see round35/X1-redteam/RESULTS.md",
    "not_covered": ["round35 B1 (not yet available at audit time)", "round35 I3 RESULTS (running)", "re-download of the six archive.org Welsh candidates", "pf_v4 FPR on ciphertext heads other than the real C[:24]"],
    "threshold": "n/a - audit (no null, no threshold)", "threshold_fixed_in_advance": True, "positive_control": "n/a - audit; recomputations reproduce lane numbers where stated",
    "evidence": ev("X1-redteam/RESULTS.md", "X1-redteam/rerun_i1.json", "X1-redteam/rerun_b1_r34.json"),
    "reopens_if": "A corrected claim is re-asserted without new evidence."
})

L['entries'].extend(new)
c = collections.Counter(x.get('status') for x in L['entries'])
L['counts']['total'] = len(L['entries'])
L['counts']['by_status'] = dict(c)
tag = " | Round 35 X1 merged 2026-10-30 (partial: I1/P1/S1(skipped)/B2/X1; B1 and I3 not available at audit): I1 measured (bar met at 10.9x cost); P1 NO-MATCH (Welsh corpus unrecoverable, panel not rebuilt, S2 NOT resumed, S1 never-run); B2 legs measured, no change (R30-B1/B2 patched); R34-B1 corrected (PHP dense tier is prefiltered, store holds PHP rows only, sleep-gap misread)."
if 'Round 35 X1 merged' not in L['counts']['note']:
    L['counts']['note'] += tag
json.dump(L, open(LJ, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('added', [n['id'] for n in new], 'total', len(L['entries']))
