#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hand-authored, code-backed judgements for TOOLS.json.

decoder_type vocabulary (this lane's three tiers):
  "rigid"              - the key/keystream pointer advances once per ciphertext rune,
                         unconditionally. The decoder cannot express a skip at all.
  "skip-capable"       - the decode primitive will hold the key pointer if you HAND it
                         a set of interrupter positions (or an interrupter character),
                         but the tool performs NO SEARCH over unknown skip patterns.
                         Its default call is rigid.
  "skip-aware-search"  - the tool actually SEARCHES over which positions interrupt
                         (subset enumeration, beam, hill-climb, annealing) and can
                         therefore recover a key when the interrupter pattern is unknown.
  "no-decoder"         - transcription, data, gematria table, hash/steg work; no
                         polyalphabetic decode loop to classify.
  "unknown"            - code present but the decisive loop was not read in this lane.

null_trustworthy: is a PUBLISHED NEGATIVE from this tool a real negative?
  true    - the tool searched a space it could actually have succeeded in.
  "partial" - trustworthy for the hypotheses it can express (usually
              "no interrupters" and "every occurrence of X interrupts"), not for
              an unknown/irregular interrupter pattern.
  false   - the decoder could not have succeeded even if its hypothesis were right.
  "unknown" / "n/a".
"""

J = {}

def add(name, **kw):
    J[name] = kw

# ---------------------------------------------------------------- rigid, read
add("rtkd__idkfa",
    decoder_type="rigid", null_trustworthy=False,
    evidence="lib/shift.js:79 `arrKeyData[i][keyOffset ++]` inside `recursiveMap` - the "
             "key pointer is post-incremented for EVERY futhark char, with no branch. "
             "Interrupters exist only as `Config.patch` in config.js: a hard-coded table "
             "of literal positions for pages already solved. Never searched.",
    what_it_tried="The reference community decoder. Gematria Primus shift/Vigenere over "
                  "a key list, with invertible futhark/latin/offset/prime axes and atbash; "
                  "reproduces the known solved pages via its patch table.",
    what_it_concluded="Ships as a tool, not as a negative result; the repo makes no "
                      "'unsolved pages are unbreakable' claim.")
add("cicada-solvers__idkfa-web",
    decoder_type="rigid", null_trustworthy=False,
    evidence="lib/shift.js is byte-identical to rtkd/idkfa's; same unconditional "
             "`keyOffset ++`. A web front-end over the same rigid core.",
    what_it_tried="Browser UI over idkfa's shift engine.",
    what_it_concluded="No published negative.")
add("cicada-solvers__LiberPrimusSolver",
    decoder_type="rigid", null_trustworthy=False,
    evidence="src/ciphers/vigenere.js `decrypt()` calls `this.key.next()` on a "
             "CircularArray for every rune that passes `isRune()`; no skip branch "
             "anywhere in src/. decoder_type_scan skiphits = 0 for the whole repo.",
    what_it_tried="Task-runner brute force over Vigenere / affine / Hill / atbash / "
                  "shift with a partition splitter and a word-list scorer.",
    what_it_concluded="No published negative; its positive control is the WELCOME page "
                      "with key DIUINITY, which contains no interrupters, so the control "
                      "never exercises a skip.")
add("r4nd0mD3v3l0p3r__LiberPrimusSolver",
    decoder_type="rigid", null_trustworthy=False,
    evidence="Upstream of cicada-solvers/LiberPrimusSolver; same vigenere.js.",
    what_it_tried="As above.",
    what_it_concluded="No published negative. NOTE: its data/unsolved.txt is 13,136 runes "
                      "and hashes to 74cebdb0... - identical to our canon.")
add("ale64bit__cicada3301",
    decoder_type="rigid", null_trustworthy=False,
    evidence="cipher/vigenere/vigenere.go Decode(): `defer func(){ index++ }()` inside "
             "the per-rune closure - unconditional advance. Same pattern in "
             "cipher/prime, cipher/totient, cipher/affine.",
    what_it_tried="A wide stateless/stateful transform search (bin/search/main.go): "
                  "reversed gematria, mu and phi of rune index and rune value, "
                  "prime-indexed modular inverse, and running XOR/affine state machines "
                  "with multipliers 10, 29, 60, 1033, 3301, scored by n-grams.",
    what_it_concluded="Exploratory; no explicit negative claim in the repo.")
add("cicada-solvers__libergo",
    decoder_type="rigid", null_trustworthy=False,
    evidence="pkg/utility/cipher/vigenere.go: `keyIndex = (keyIndex + 1) % len(cleanKey)` "
             "runs for every rune. The only hold is for characters outside the alphabet "
             "('do not advance key' comment at line 101), which is punctuation handling, "
             "not an interrupter.",
    what_it_tried="Large Go toolkit (cmbsolver): Vigenere, autokey, atbash, affine, "
                  "rune substitution reports, a linguistic n-gram database builder, "
                  "and DB-backed candidate storage.",
    what_it_concluded="Infrastructure; no single published negative.")
add("NoxxGames__LiberPrimus-GPU",
    decoder_type="rigid", null_trustworthy=False,
    evidence="python/libreprimus/bounded_execution/reset_advance.py: the render loop does "
             "`state_position += 1` for EVERY transformable token, unconditionally. Its "
             "two ADVANCE_MODES are {runes_only, token_break_preserving} - that is "
             "word-separator handling, not a key skip - and its RESET_MODES "
             "{none, word, clause, line} restart the key at punctuation. CUDA kernels "
             "(cuda/kernels/gematria_shift_score_kernel.cu) apply a flat shift under a "
             "`transformable_mask` that is fixed per run, not searched. The string "
             "'interrupt' appears only in two docs/research/*.md backlog files - there is "
             "no interrupter code path in the engine at all.",
    what_it_tried="The largest recent effort in the corpus: 229 commits, ~307k LOC, a "
                  "GPU/CPU bounded-execution rig sweeping Vigenere key packs, "
                  "prime-minus-one / prime-mod-29 / prime-gap / Mersenne keystreams, "
                  "with reset-and-advance ablations, fixture hashes and CI locks.",
    what_it_concluded="Publishes bounded negative sweeps with reproducibility locks. "
                      "Those negatives are rigorous WITHIN the rigid family and say "
                      "nothing about key-skip hypotheses.",
    notes="First commit 2026-05-15; repo carries a .codex/agents directory, so at least "
          "partly agent-authored. Engineering quality is high and the artefacts are "
          "hash-pinned, which makes it the single most useful rigid baseline here.")
add("thecornerspore-dev__rune_swiss",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="rune_swiss.py:194 `decrypt_vigenere(ciphertext, key, skip_indices)` - the "
             "key holds at any index in skip_indices, but skip_indices is a caller "
             "argument and nothing in the repo searches it.",
    what_it_tried="Swiss-army CLI: Vigenere, Caesar, atbash, Playfair, totient streams.",
    what_it_concluded="No published negative.")
add("naliferopoulos__3301",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="lputils/crypto.py:56 `vigenere(arr, key, skip_list=[])`; on a skip it "
             "`continue`s - which HOLDS the key but also DROPS the rune from the output "
             "rather than emitting it literally. skip_list is never searched.",
    what_it_tried="Small utility set: Vigenere, atbash, totient/cototient streams.",
    what_it_concluded="No published negative.",
    notes="The drop-instead-of-emit behaviour means any skip-mode output is shorter than "
          "the input and misaligned against the page; treat its skip results as unsound.")
add("cicada-solvers__LPDecrypter",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="lpdecrypter/ciphers/vigenere_cipher.py:50 `VigenereWithInterruptersCipher`: "
             "`if i in self.interrupters: ...` else `key_index += 1`. Correct hold "
             "semantics. But examples/solve_vigenere.py:38 passes a literal "
             "`[48, 74, 84]` - a hand-written list. No search exists.",
    what_it_tried="Clean library of Vigenere-with-interrupters, totient and substitution "
                  "ciphers over mod 29.",
    what_it_concluded="No published negative.")
add("Protheme-777__Liber-Primus-decoder",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="liber_primus_decoder_v5.py:753 `_apply_key(idx, key, fn, skip_f=False)`: "
             "`if skip_f and i == 0: result.append(0); continue` - the key holds, but "
             "skip_f is an ALL-OR-NOTHING boolean, so the only two hypotheses it can "
             "express are 'no F interrupts' and 'every F interrupts'. It cannot express "
             "an irregular subset, which is the behaviour actually observed on the solved "
             "pages. `beaufort()` does not even take skip_f, so Beaufort runs rigid.",
    what_it_tried="Single-file 1,666-line kitchen sink: Vigenere, Beaufort, affine, "
                  "atbash, autokey, prime/totient/prime-gap streams, plus hill-climbing "
                  "(4,000 iters x 3 restarts) and simulated annealing (T0=10, cooling "
                  "0.995) over monoalphabetic maps.",
    what_it_concluded="Reports no solve. The hill-climb and annealing search the "
                      "SUBSTITUTION map, not the interrupter pattern, so a null from it "
                      "does not bear on the key-skip hypothesis.")
add("neuroretransmit__liberprimus-tool",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="crypto/running_key.py: a `skips` dict holds the key at chosen occurrences, "
             "then `key_index += 1` on the normal path. Crucially both this file and "
             "crypto/vigenere.py raise `NotImplementedError(\"Permutations mode not "
             "implemented yet\")` on the non-`fast` branch - i.e. the author identified "
             "that the skip PERMUTATIONS need enumerating and left it unwritten.",
    what_it_tried="Vigenere / running-key / totient over rune indices, with a genetic "
                  "algorithm (ga/ga.py) seeded from a SOLUTIONS pool.",
    what_it_concluded="No solve. The most explicit admission in the corpus that the "
                      "skip search is the missing piece: it is literally a "
                      "NotImplementedError in the shipped code.")
add("Taiiwo__cicada",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="cicada/gematria.py:142 `running_shift(key, interrupts='', skip_indices=[])`: "
             "on `c in interrupts` or `i in skip_indices` it emits the char and does NOT "
             "call `next(key)` - correct hold semantics, and both a character rule and a "
             "positional list are supported. But nothing in the package searches either; "
             "`vigenere()` and `totient_stream()` just forward the caller's arguments.",
    what_it_tried="The most-reused community library: gematria table, rune/latin "
                  "transliteration, running shift, Vigenere, totient stream, IoC, and a "
                  "validator over the solved pages.",
    what_it_concluded="A library, not a claim. Its primitive is sound; every negative "
                      "built on it inherits the caller's search, not Taiiwo's.")
add("Taiiwo__TaiiwoBot",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="Vendors cicada/gematria.py verbatim. plugins/Gematria.py:125-126 parses "
             "`interrupts` and `skip_indices` from a chat command string - a human types "
             "them. No search.",
    what_it_tried="IRC/Discord bot front-end over Taiiwo/cicada.",
    what_it_concluded="No published negative.")
add("micheloosterhof__aldegonde",
    decoder_type="skip-aware-search", null_trustworthy="partial",
    evidence="examples/lp_lag5_attack.py `phase_sequence()` implements four DETERMINISTIC "
             "phase rules - `skip:R` (rune R is an interrupter, emitted literally, key "
             "does not advance), `reset:R`, `word`, `sent` - and solves each coset by "
             "chi-square, then scores with runeglish trigrams. Its calibration is the "
             "best in the corpus: a doublet-preserving null (shuffle the lag-1 delta "
             "stream and rebuild the walk) because 'against a naive shuffle null every "
             "real page scores high simply because the corpus lacks adjacent doublets, "
             "which is exactly how this attack produced plausible-looking false positives "
             "before the null was fixed'; and a POSITIVE CONTROL - page-57 plaintext "
             "encrypted with a random 5-shift key plus an interrupter - which it cracks "
             "exactly at 95 runes, z ~ +7. Elsewhere: examples/crack_masc.py hill-climb, "
             "gorod_krovi_cipher12.py hill_climb_autokey(5000 iters, 30 restarts).",
    what_it_tried="A general classical-cryptanalysis library (1,585 commits) plus an "
                  "LP-specific programme: period-5 interruptor attack over additive and "
                  "reflective shift families under all four phase rules, and a coset-IoC "
                  "sweep that detects ANY period-5 polyalphabetic substitution "
                  "(including Quagmire-style keyed alphabets) without solving it.",
    what_it_concluded="EXCLUDES the period-5 key-schedule-with-interruptor hypothesis for "
                      "the shift family, and by detection for general period-5 "
                      "polyalphabetic substitution: real pages top out at z ~ +3 over "
                      "6,710 attack runs, no rule clears the multiple-testing threshold.",
    notes="This is the one negative in the corpus that is properly instrumented - it has "
          "a positive control and a null that respects the corpus's own doublet anomaly. "
          "It is 'partial' rather than true only because its interrupter model is "
          "deterministic (every occurrence of R interrupts); an irregular subset is "
          "outside its hypothesis space. Note the repo carries a CLAUDE.md, so the "
          "LP-specific example scripts may be recent AI-assisted work even though the "
          "library itself dates from 2021.")
add("cicada-solvers__aldegonde",
    decoder_type="skip-aware-search", null_trustworthy="partial",
    evidence="Org fork of micheloosterhof/aldegonde at an earlier point (1,497 vs 1,585 "
             "commits). Same engine.",
    what_it_tried="See micheloosterhof/aldegonde.",
    what_it_concluded="See micheloosterhof/aldegonde.")
add("relikd__LiberPrayground",
    decoder_type="skip-aware-search", null_trustworthy=True,
    evidence="LP/InterruptSearch.py: `all()` enumerates EVERY subset of candidate "
             "interrupter positions; `sequential()` is a bounded hill-climb over the "
             "first maxdepth=9 interrupts per step, scored by a caller-supplied "
             "score_fn. playground.py:245 sets SOLVER.INTERRUPT_POS from the search; "
             "probability.py loads a precomputed InterruptDB ('db_norm'/'db_high') and "
             "'perform[s] heuristic search on the keylength, interrupts, and key' "
             "jointly.",
    what_it_tried="Joint search over key length, interrupter positions and key, with an "
                  "IoC objective; OEIS sequence keystreams (oeis.py) with interrupt "
                  "insertion.",
    what_it_concluded="No solve found. Because the instrument can express and search an "
                      "irregular interrupter pattern, its null IS a real negative - but "
                      "only over PERIODIC/Vigenere key lengths. It does not cover running "
                      "keys, so it says nothing about the running-key hypothesis.")
add("cicada-solvers__LiberPrayground",
    decoder_type="skip-aware-search", null_trustworthy=True,
    evidence="Org mirror of relikd/LiberPrayground.",
    what_it_tried="See relikd/LiberPrayground.",
    what_it_concluded="See relikd/LiberPrayground.")
add("cicada-solvers__JBO-cicada_tools",
    decoder_type="skip-aware-search", null_trustworthy="partial",
    evidence="research_utils.py:179 `iterate_potential_interrupter_indices()` yields ALL "
             "2**k subsets of the positions where the interrupter rune occurs - a genuine "
             "exhaustive skip search. transformers.py:609 KeystreamTransformer.transform() "
             "holds the keystream at any index in interrupt_indices. BUT: (a) the "
             "generator is applied to `header_pt`, the first SENTENCE only, so k stays "
             "small; (b) `consider_interrupters` defaults to **False** in "
             "experiments.py:99 and 1050, and with `interrupt_indices=set()` the "
             "transform advances on every rune - i.e. the DEFAULT run is rigid.",
    what_it_tried="Broad experiment suite (273 commits): sentence cribbing against "
                  "prime/emirp keystreams with skip and start-value limits, "
                  "primes-indexed-by-totient keystreams, autokey, Hill cipher, "
                  "page-15 abs(3301-p) function, and hash work.",
    what_it_concluded="No solve. Its skip search is real but is a short-crib search, and "
                      "it is off unless the caller turns it on - so most published runs "
                      "from this tool are rigid runs.")
add("cicada-solvers__lp-decrypter",
    decoder_type="skip-aware-search", null_trustworthy="partial",
    evidence="enc/DecryptModel.py:485 `get_all_interrupter_position_lists()` returns "
             "`get_all_sublists()` = every `combinations()` subset of the positions where "
             "the interrupter rune occurs; the decrypt loop at line 383 holds key_index "
             "at those positions. It adds a self-consistency filter: if a decrypted rune "
             "IS the interrupter rune, the candidate is rejected (line 399). The search "
             "is bounded by `crop_ct_to_keylen_with_interrupter()` - only the first "
             "key_length runes (plus enough extra to cover interrupters) are searched.",
    what_it_tried="Key-recovery over a cropped ciphertext window: itertools.product over "
                  "ciphertext-derived and runeglish keys, gematria rotations, key and "
                  "ciphertext shifts, and the full interrupter-subset enumeration.",
    what_it_concluded="No solve. Trustworthy as a negative for SHORT keys recoverable "
                      "from the first key-length window; silent about long or running "
                      "keys.",
    notes="Its lp_data/lp_section_data.py encodes J as U+16C2, not U+16C4 - see "
          "CONFLICTS-E.md. Downstream consumers must handle the alias.")
add("jens-wedin__liber-primus",
    decoder_type="skip-aware-search", null_trustworthy=True,
    evidence="attack_keyskip.py is a beam search over key-skip hypotheses with a "
             "`--selftest` that recovers 96-98% of a planted key-skip key - i.e. it is a "
             "VALIDATED instrument. attack_runningkey.py self-calibrates and declares "
             "itself UNDERPOWERED rather than reporting a null.",
    what_it_tried="Full toolkit: solved-page validation by forward re-encryption, IoC and "
                  "doublet statistics, autokey brute force, crib dragging with the "
                  "literal-F rule, key-skip beam search over prime/totient streams, "
                  "key-text-free running-key attack, no-repeat mechanism modelling, and "
                  "an n-gram model over rune indices with Stupid Backoff.",
    what_it_concluded="Rules out prime-family key-skip; characterises the lag-1 anomaly "
                      "(86 doublets / 0.66%, differencing restores 3.37%); declares its "
                      "own running-key test underpowered.",
    notes="NOT AN INDEPENDENT WITNESS. All 8 commits are authored "
          "Claude <noreply@anthropic.com>, first commit 2026-08-18T16:51:25Z - one day "
          "before this operation. Its agreement with this project's conclusions is "
          "sibling agreement, not replication. Flagged prominently in CONFLICTS-E.md.")
add("bobby-bobby-bobby-bobby__Libre-Primus-Cicada-3301-Solver-Demo",
    decoder_type="rigid", null_trustworthy=False,
    evidence="lp_solver/config.py:28 strategy='beam', beam_width=256 and "
             "distributed.py's genetic pool search over KEYS. Nothing in lp_solver "
             "mentions interrupters or a key hold; the beam explores the key space with "
             "a rigid decode underneath.",
    what_it_tried="Distributed multiprocess beam/genetic key search with a torch tensor "
                  "scorer.",
    what_it_concluded="Named a 'Demo'; makes no negative claim.",
    notes="First commit 2026-04-23; one of the authors is 198982749+Copilot@users."
          "noreply.github.com, so partly AI-authored.")
add("Skyro7777777__LiberPrimusDecoded",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="decoder/digraph_attack.py runs brute force and hill climbing over 2x2 Hill "
             "matrices mod 29 (50 starts x 500 iters) and magic-square sub-blocks. The "
             "search is over the CIPHER, not over interrupter positions.",
    what_it_tried="Digraph/Hill-cipher attack over Z_29, magic-square derived sub-blocks, "
                  "autokey, Beaufort, atbash, plus a large scraped research corpus.",
    what_it_concluded="No solve reported.",
    notes="First commit 2026-08-11, sole author 'z@container' - likely container-run "
          "agent work; treat as non-independent. Its raw/liber_primus.txt is the "
          "scream314 15,938-rune lineage (see CONFLICTS-E.md), and its decoder/*.json "
          "store runes and raw text in the same file, which breaks naive rune extraction.")
add("AegisTrustCore__Liber-Primus-HMS-Run-Time",
    decoder_type="unknown", null_trustworthy="unknown",
    evidence="hms_tools/gp29.py carries a GP table; research/runs/RUN-0009 reports 640 "
             "observed routes over the 267-rune page 33 stream with add/subtract/Beaufort "
             "operations at continuous and word-reset scopes. CORRECTIONS.md walks back "
             "an earlier prime/totient claim. The decisive key-advance loop was not "
             "located in this lane.",
    what_it_tried="Route/transposition enumeration over single pages with a governance "
                  "and reproducibility wrapper (GOVERNANCE.md, protected branch, "
                  "validate status check).",
    what_it_concluded="Self-corrects an earlier Page-73 prime/totient interpretation.",
    notes="First commit 2026-08-12. 'HMS Endeavour' branding, heavy process scaffolding, "
          "very recent - treat claims with caution and verify independently.")
add("Pitchfork-and-Torch__instar",
    decoder_type="unknown", null_trustworthy="unknown",
    evidence="scripts/build_payloads.py:49 uses `key[ki % len(key)]` over LATIN "
             "(ord - 65), not over runes - this is payload construction, not an LP decode "
             "loop.",
    what_it_tried="Atbash, shift, totient, Vigenere utilities plus hash work.",
    what_it_concluded="No published negative located.",
    notes="First commit 2026-08-14; sibling repo Pitchfork-and-Torch/liber-research "
          "2026-08-18. Very recent, provenance unverified.")

# --------------------------------------------------------- no-decoder / data
for n, why in [
    ("resvolver__c1cada",
     "2015 research dump: Perl frequency scripts, XOR/steg experiments, key-phrase files "
     "and - the important part - an eleven-file rune transcription that is bit-identical "
     "to our canon. See CONFLICTS-E.md Headline 1."),
    ("scream314__cicada3301",
     "Documentation site plus liber_primus.md, the 15,938-rune transcription lineage that "
     "carries the only two reading conflicts in the corpus. See CONFLICTS-E.md."),
    ("cicada-solvers__documenting-cicada3301-scream314",
     "Org mirror of the scream314 documentation."),
    ("cicada-solvers__cicada-runes-2014-transcriber",
     "2015-01-10. Browser transcriber for the 2014 runes: index.html, runes.txt, "
     "primes.txt. Pre-dates the 2017 iddqd root."),
    ("cicada-solvers__GematriaPrimusTool",
     "2015-02-10. Gematria Primus transliteration widget (gematria.js). No decoder."),
    ("micheloosterhof__cicada-2016",
     "2016-01-06. One image plus its outguess payload from the 2016 puzzle. No decoder."),
    ("dude123124144__Liber-Primus-Runes-OCR",
     "2017-03-12. Per-rune template bitmaps plus an OCR script - an INDEPENDENT reading "
     "path from pixels rather than from another text file. Same author as resvolver/"
     "c1cada. The most promising unexploited lead for settling C-E-01 from the scans."),
    ("cicada-solvers__deep-web-hash-as-ed25519",
     "Onion-address / ed25519 key-grinding work on the deep-web hash. Not a rune decoder."),
    ("cicada-solvers__Cicada-DWH-HashcatAttempts", "Hashcat rulesets against the deep-web hash."),
    ("tweqx__dwh-check", "Shell check of the deep-web hash."),
    ("cicada-solvers__3301-hash-alarm", "Monitors for new 3301 artefacts. No decoder."),
    ("cicada-solvers__isitcicada", "Authenticity checker for claimed 3301 messages (PGP)."),
    ("cicada-solvers__3301chef", "A CyberChef fork with 3301 recipes. Generic crypto UI."),
    ("cicada-solvers__GPPrimeView", "Gematria/prime viewer plus a bundled English word list."),
    ("cicada-solvers__cicada-library", "Packaging of Taiiwo/cicada for the org."),
    ("crackalamoo__futhorc", "General Anglo-Saxon futhorc package (33 runes, incl. STAN and "
     "CWEORTH). Not an LP tool; excluded from transcription comparison."),
    ("cicada-solvers__monokuma-ConvolutionKernels", "Convolution kernels over page images."),
    ("cicada-solvers__liber_primus_finds", "Notes/finds only."),
    ("cicada-solvers__Red_Rune_Cribs", "Crib list for the red runes."),
    ("cicada-solvers__Rain-3301", "Data/notes."),
    ("geomatria__CicaData", "Data collection."),
    ("LiberPrimus__Failed-Attempts", "Explicit archive of failed brute-force attempts "
     "(2*pi*R, Vigenere, deep-web hash). Useful as a negative-results record."),
    ("rtkd__iddqd", "THE transcription repository. 59 commits, HEAD "
     "f2267b0c2f1e1d2662806b90b9c3a2953b3a7023. The rune stream changed exactly once "
     "after creation (ed95eb7, 2017-05-21, two W+S pairs -> the EA ligature at offsets "
     "998 and 1135, inside the solved 'A Koan' page). No decoder."),
    ("rtkd__iddt", "Deep-web/hash tooling from the same author. No rune decoder."),
    ("rtkd__kerry", "34 LOC helper."),
    ("_iddqd_tmp", "Superseded: renamed to rtkd__iddqd."),
]:
    add(n, decoder_type="no-decoder", null_trustworthy="n/a", evidence=why,
        what_it_tried=why, what_it_concluded="n/a")

# ------------------------------------------------- small tools, loop not read
SMALL = ["Eternalth__Liber-Primus", "Fafison4k__cicada-3301-page32", "LiberPrimus__primus.py",
         "Locyyx64__liber-primus-analysis", "Locyyx64__lp-cribbs", "MuthuRanjanA__cicada3301",
         "N1-rt__lp-runes-translator", "O4N4c__gematria-primus", "ProfessorJ17__Cicada3301",
         "Taters79__LiberPrimus_CLI_Tool-Zig", "Taters79__liber_primus", "Viusthas__Liber_Primus",
         "VzGarnet__Liber-Primus", "Wra1th__Nebuchadnezzar", "aadishgoel__Cicada-3301",
         "chipper1999__Liber-Primus-Solver", "chipper1999__liber-primus-solutions",
         "cicada-solvers__3301_assist", "cicada-solvers__CICADA2K16-solving-tool",
         "cicada-solvers__LiberPrTools", "cicada-solvers__WPCH-3301",
         "cicada-solvers__lphelper", "cicada-solvers__miteo-3301tools",
         "ctvrty-rozmer__bruh", "greenie-neuko__arg-skills",
         "harry-sar__3301-gematria-primus-solver", "hugvig__liber-primus-research",
         "krcdavis__cicada-tools", "lipeeeee__gematria", "nexon33__cicada3301",
         "ralphatobe__cicada-3301", "seeker-it__3301-gematria", "taraweling__Cicada3301",
         "wtf-jik__cicada3301", "ztlw30813__cicada3301", "0x676f64__Cicada-3301",
         "AABaderko__cicada3301", "Pv3__Cicada3301", "cicada-solvers__cadrypt",
         "cicada-solvers__cmbsolverwp", "artistofreap-byte__liber-primus-matrix-attack",
         "Pitchfork-and-Torch__liber-research"]
for n in SMALL:
    J.setdefault(n, dict(
        decoder_type="unknown", null_trustworthy="unknown",
        evidence="Decisive key-advance loop not read in this lane. Keyword scan results "
                 "are in decoder_type_scan.json under this repo's skip_evidence / "
                 "advance_lines.",
        what_it_tried="See decoder_type_scan.json 'ciphers' counts and the repo README.",
        what_it_concluded="Not assessed."))

# two 2016-era notes worth carrying
J["cicada-solvers__CICADA2K16-solving-tool"].update(
    notes="2016-01-14, pre-dates the iddqd root. Its Gematria table defines "
          "J = u'\\u16c2' (RUNIC LETTER E), which is the J-codepoint alias documented in "
          "CONFLICTS-E.md; the alias is older still, since resvolver/c1cada uses it in "
          "January 2015.")
J["Pv3__Cicada3301"].update(
    notes="2016-03-13. Source begins '# CICADA2K16' - a derivative of "
          "cicada-solvers/CICADA2K16-solving-tool, carrying the same U+16C2 J alias.")
J["dude123124144__Liber-Primus-Runes-OCR"].update(
    notes="Highest-value unexploited lead in this lane: an OCR path from the page images, "
          "by the same author as the 2015 resvolver/c1cada transcription. Running it "
          "against the page-24 scan is the concrete way to settle C-E-01.")

# --------------------------- second pass: additional code-backed classifications
add("cicada-solvers__lphelper",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="core.py:147 `decription(self, key, missing_f=[], cipher_type=...)`: for the "
             "'sequence', 'atbash' and 'vigenere' branches, positions listed in "
             "`missing_f` are emitted unchanged and `key_cursor` does NOT advance. The "
             "parameter name is literally the missing-F (interrupter) positions. "
             "page_loader.py:37 and :64 pass a caller-chosen list; nothing searches it.",
    what_it_tried="Page-oriented helper: load a page, apply a sequence/atbash/Vigenere "
                  "key with a supplied interrupter list, print runes/gematria/English.",
    what_it_concluded="No published negative.")
add("lipeeeee__gematria",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="lib/gematria.py:180 `running_shift(key, interrupts='', skip_indices=[])` is "
             "Taiiwo/cicada's function verbatim - correct key hold on both an interrupter "
             "character and a positional list. No search over either.",
    what_it_tried="Re-packaging of the Taiiwo gematria library with extra CLI/utility "
                  "layers and hash work.",
    what_it_concluded="No published negative.")
add("ztlw30813__cicada3301",
    decoder_type="rigid", null_trustworthy=False,
    evidence="decryptor.py:161 `vigenere_decrypt` and :358 `beaufort_decrypt` both do "
             "`key_idx += 1` on every alphabetic character with no branch. More important: "
             "both operate on the **26-letter Latin alphabet** "
             "(`ord(char) - ord('A')`, `% 26`), not on the 29-rune Gematria Primus. It "
             "cannot decode LP runes at all.",
    what_it_tried="General Cicada text decryptor over a fixed list of guessed keys "
                  "(PSYOP, ENLIGHTENMENT, CICADA, WELCOME, ...), plus an RSA cracker.",
    what_it_concluded="No LP-relevant negative; wrong alphabet for the problem.")
add("Wra1th__Nebuchadnezzar",
    decoder_type="rigid", null_trustworthy=False,
    evidence="Key character and ciphertext character are zipped position-for-position and "
             "combined with `% len(alphabet_list)`; no hold, no interrupter concept.",
    what_it_tried="Iterated shift/Vigenere printouts over a rune alphabet with a totient "
                  "keystream option.",
    what_it_concluded="No published negative.")
add("Locyyx64__lp-cribbs",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="lib/libcrib.py works in DIFFERENTIAL space: `vkeygetf_diff()` reads a "
             "Vigenere key straight off the crib-minus-ciphertext differential, and "
             "`vkeygetf_diff_err()` emits three keys at absolute error +/-1 to absorb "
             "off-by-one alignment. crib_base.py:53 lists Beaufort, Quagmire, Bifid, "
             "Playfair, Nihilist and affine as not-yet-implemented. Differential "
             "crib-dragging does not itself advance a key pointer, so the rigid/skip "
             "distinction enters only through where the crib is placed - and the "
             "+/-1 error keys are an explicit, if crude, tolerance for a one-position "
             "key desynchronisation.",
    what_it_tried="Crib-dragging and key-derivation over the futhorc runeset with Caesar, "
                  "atbash and Vigenere/Beaufort variants.",
    what_it_concluded="No published negative.",
    notes="The +/-1 differential tolerance is the closest thing in the small-tool tier to "
          "acknowledging key desynchronisation, though it tolerates only a single "
          "one-step slip, not an accumulating skip.")
for n, why in [
    ("VzGarnet__Liber-Primus",
     "PHP site/notes; no keyed per-rune decode loop found (grep for key_index / "
     "key_pos / % len(key) over *.php returns nothing)."),
    ("krcdavis__cicada-tools",
     "Gematria/transliteration utilities and page data; no keyed decode loop found."),
    ("cicada-solvers__cadrypt", "C++ utility; no keyed rune decode loop found."),
    ("cicada-solvers__cmbsolverwp", "WordPress-side presentation of cmbsolver's data; no "
     "decode loop."),
    ("taraweling__Cicada3301", "Puzzle notes and scripts; no keyed rune decode loop found."),
    ("nexon33__cicada3301", "Utility scripts; no keyed rune decode loop found."),
    ("ctvrty-rozmer__bruh", "Vendored copy of the Taiiwo cicada package plus notes; the "
     "decode primitive is Taiiwo's - see that row."),
    ("cicada-solvers__3301_assist", "Assistive UI and page data; no keyed decode loop found."),
    ("cicada-solvers__CICADA2K16-solving-tool",
     "2016 rune/gematria frequency tool: builds the Runeset table and counts, no keyed "
     "decode loop. Historically important for the U+16C2 J alias, not as a decoder."),
    ("Pv3__Cicada3301", "2016 derivative of CICADA2K16 with word/OEIS probability work; "
     "no keyed per-rune decode loop."),
]:
    J[n] = dict(decoder_type="no-decoder", null_trustworthy="n/a", evidence=why,
                what_it_tried=why, what_it_concluded="n/a",
                notes=J.get(n, {}).get("notes"))
add("LiberPrimus__primus.py",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="primus.py:62 calls `Runes(text).vigenere(key, [], True)` - the Taiiwo "
             "gematria API, with an EMPTY interrupts list hard-coded at the call site. "
             "The primitive can hold the key; this caller never asks it to.",
    what_it_tried="CLI wrapper: chained Vigenere / atbash / shift / totient over the "
                  "Taiiwo library.",
    what_it_concluded="Sibling repo LiberPrimus/Failed-Attempts records the negatives.")

# ------------------------------------------------------- late-recovered repos
add("henkman__liberprimus",
    decoder_type="skip-capable", null_trustworthy="partial",
    evidence="Go solver (liberprimus.go) with per-page solution scripts under "
             "solutions/. Its transcription liberprimus.txt was added in the INITIAL "
             "commit 8cc9665 (2016-08-14T18:01:14+02:00) and `git log -- liberprimus.txt` "
             "shows that one commit only - the file has never been edited.",
    what_it_tried="Reproduces the solved pages; prime-generator keystreams (commit "
                  "addc306 '56 use primegenerator'); page-by-page solution scripts.",
    what_it_concluded="A solutions archive rather than a negative-results archive.",
    notes="PRE-2017 WITNESS. 13,072 runes (64 short of canon's 13,136); reproduces 48 of "
          "57 canon segments verbatim. Six segments differ by OMISSION, one (35) by a "
          "five-place DISPLACEMENT of a B rune, and three positions are genuine "
          "CONTRADICTIONS: segment 33 @100 and @117 canon B vs henkman W, and segment 55 "
          "@19 canon X vs henkman L. This independently reproduces Lane B's finding. See "
          "CONFLICTS-E.md C-E-03.")
add("rtkd__iddqd",
    decoder_type="no-decoder", null_trustworthy="n/a",
    evidence="Transcription and image repository. HEAD "
             "f2267b0c2f1e1d2662806b90b9c3a2953b3a7023, 59 commits.",
    what_it_tried="Holds liber-primus__transcription--master.txt, the file the community "
                  "treats as the root transcription, plus page images, keys and indices.",
    what_it_concluded="n/a",
    notes="The rune stream changed exactly once after creation: 218ed88 (2017-03-01, "
          "15,935 runes) -> ed95eb7 (2017-05-21, 15,933) replaced two W+S pairs with the "
          "EA ligature at rune offsets 998 and 1135, inside the SOLVED 'A Koan' page. "
          "3089b65 (2019-06-17) changed segment offsets but not a single rune. All three "
          "revisions contain all 57 canon segments verbatim.")
add("cicada-solvers__iddqd", decoder_type="no-decoder", null_trustworthy="n/a",
    evidence="Org mirror of rtkd/iddqd.", what_it_tried="See rtkd/iddqd.",
    what_it_concluded="n/a")
add("krisyotam__cicada3301", decoder_type="no-decoder", null_trustworthy="n/a",
    evidence="Archive repository, HEAD 76d3ee8c762f60025822c8c05edbf31351636469, created "
             "2026-04-11. Holds archives/cijhho/{2012,2014,2016,...} of puzzle material.",
    what_it_tried="Documentation and material archive, not a solver.",
    what_it_concluded="n/a",
    notes="Namesake of this project's canonical file krisyotam_runes.txt, and it settles "
          "where that file came from. Its archives/cijhho/2014/ folder holds TWO rune "
          "streams: 'Liber Primus/runes in text format.txt' is 13,136 runes hashing to "
          "74cebdb0... - a third copy of our canon - while 'additional docs/scripts/"
          "runes.py' (13,092) and 'runescript.py.py' (13,101) reproduce henkman's exact "
          "three contradictions (seg 33 @100 and @117 B->W, seg 55 @19 X->L) and "
          "henkman's missing-segment set. So the dissenting reading is a LINEAGE, not a "
          "slip. Dating caveat: the '2014' is a folder label inside a 2026 archive, not "
          "git evidence. See CONFLICTS-E.md C-E-03b.")
for n, why in [
    ("cicada-solvers__gutenberg-txt", "Plaintext corpus for running-key candidate keys."),
    ("cicada-solvers__neuroretransmit-cicada",
     "Org mirror of neuroretransmit/cicada; clone is broken on disk (see GAPS-E.md)."),
    ("mortlach__Liber-Primus-Rune-Decrypting",
     "mortlach's rune-decrypting work; clone is broken on disk (see GAPS-E.md)."),
]:
    add(n, decoder_type="unknown", null_trustworthy="unknown", evidence=why,
        what_it_tried=why, what_it_concluded="Not assessed.")

add("yo-yo-yo-jbo__cicada_tools",
    decoder_type="skip-aware-search", null_trustworthy="partial",
    evidence="Upstream of cicada-solvers/JBO-cicada_tools; same "
             "research_utils.py:iterate_potential_interrupter_indices() exhaustive "
             "2**k subset enumerator and same KeystreamTransformer key hold, with "
             "consider_interrupters defaulting to False.",
    what_it_tried="See cicada-solvers/JBO-cicada_tools.",
    what_it_concluded="See cicada-solvers/JBO-cicada_tools.")

add("mortlach__Liber-Primus-Rune-Decrypting",
    decoder_type="skip-aware-search", null_trustworthy="partial",
    evidence="key-generator/key_generator.py:56 `getInterrupterPositions(ct, pt)` derives "
             "candidate interrupters from the interrupter's DEFINING property rather than "
             "by blind enumeration: a rune qualifies only if every position where it "
             "appears in the plaintext also carries that same rune in the ciphertext "
             "(`set(pt_pos).issubset(ct_pos)`) - i.e. it was emitted literally. "
             "`getInterrupterData()` then strips those positions from both ct and pt and "
             "derives the key from the remainder, so the key pointer effectively holds "
             "there. The candidate set is per-rune ('every occurrence of R interrupts'), "
             "not an arbitrary subset. README: \"'All' keys means considering: all "
             "possible interrupters, gematria rotations and defined plaintext rune "
             "transpositions.\"",
    what_it_tried="Crib-driven key DERIVATION for any two-variable cipher function "
                  "f(plaintext, key) - arithmetic and XOR mod 29 are supplied, the "
                  "pattern is extensible - across all candidate interrupters, both "
                  "gematria directions for ct and pt, 28 gematria rotations per variable, "
                  "and L2R / R2L transpositions. Scoring uses its own runeglish n-gram "
                  "probability tables (raw_scoring_data/reProbChar2-4, reProbGNG2-3, "
                  "reProbRB2-3).",
    what_it_concluded="No solve. Importantly it ships a POSITIVE CONTROL: "
                      "test_functions_of_2_variables.py randomly encrypts text and checks "
                      "that each solve method recovers the exact key or fails loudly, and "
                      "it re-solves page 56 and the 'A Koan: During' page.",
    notes="One of only two tools in the corpus that pairs a skip-aware search with a "
          "self-test positive control (the other is micheloosterhof/aldegonde). Its "
          "approach is also the most economical: it uses the ct==pt constraint to derive "
          "interrupters instead of enumerating 2**k subsets.")
add("mortlach__runeglish-lm",
    decoder_type="no-decoder", null_trustworthy="n/a",
    evidence="Data repository: Markov transition-probability matrices P(A|B) over "
             "runeglish character n-grams (2-, 3- and 4-grams, plain and word-length-"
             "indexed), plus a worked phrase-probability example showing how scores "
             "degrade as 1% transcription error is injected.",
    what_it_tried="Building a runeglish language model rather than attacking the cipher.",
    what_it_concluded="n/a",
    notes="Directly relevant to this project's scorer problem "
          "(analysis/round15/SCORER/FINDING.md): a scorer trained on raw English is "
          "scoring a different distribution than a 29-rune decoder emits, and these are "
          "matrices trained on runeglish itself. Its README alphabet also spells J as "
          "U+16C2, a fourth repo carrying that alias.")
add("mortlach__Liber-Primus-Crib-Assist",
    decoder_type="no-decoder", null_trustworthy="n/a",
    evidence="Crib-list generator feeding mortlach/Liber-Primus-Rune-Decrypting; the "
             "clone did not complete in this lane (see GAPS-E.md).",
    what_it_tried="Crib generation.", what_it_concluded="Not assessed.")

# ------------------------------------------------- final batch of late clones
for n, why, note in [
 ("thomasandfriends__Cicada3301Runes",
  "Single commit 52e5c7e4827d81ffc705ef61ac0217c9bdd6ff35, 2015-01-09T23:39:25Z, "
  "Misha Wagner. Rune data plus brute/parse scripts, outguess payloads and onion "
  "captures. Scripts are 2015-era analysis, not a keyed rune decoder.",
  "THE EARLIEST DATED RUNE STREAM IN THIS CORPUS. data/runes.rune.old is 13,072 runes "
  "with index SHA-256 a38c30ca109919b8ec55d28f924e7544307e93422bda8c5ed2b22f2e69180d0f "
  "- byte-identical to resvolver/c1cada's 2015-01-23 transcriptions.rne, and carrying "
  "the W/W/L readings that reach henkman/liberprimus in 2016. data/runes.rune is a "
  "13,063-rune variant with the same three contradictions. See CONFLICTS-E.md C-E-03b: "
  "this file shows our reading is the CORRECTION, not the original."),
 ("cicada-solvers__solving-3301-code-2013",
  "First commit 2014-01-23T09:04:50-07:00, last 2017-05-02. Crib-dragging scripts, "
  "dictionaries, a C bit-flipper, an IRC bot and onion alerting - 2013/2014-puzzle "
  "tooling, before the Liber Primus.",
  "OLDEST REPOSITORY IN THIS CORPUS (2014-01-23). Predates the Liber Primus itself, so "
  "it holds no LP transcription, but it is the right place to look for the community's "
  "earliest conventions."),
 ("rtkd__idclip", "Small JS finder (find.js) by the author of idkfa and iddqd; "
  "2018-02-02 to 2018-02-16. Not a rune decoder.", None),
 ("cmbsolver__cmbcidada3301",
  "Large C# solution (LiberPrimusAnalysisTool.*, 2024-12-31 to 2026-07-10) by "
  "cmbsolver, who also maintains cicada-solvers/lp-decrypter and libergo. Decode loop "
  "not read in this lane.", "High-priority unknown: same author as the corpus's most "
  "thorough interrupter-subset enumerator, so its decoder tier is worth establishing."),
 ("localavaster__cadrypt", "Flutter/Dart application (2021-01-19 to 2023-04-13) "
  "presenting the Cicada messages. Decode loop not read in this lane.", None),
 ("sgroveman__cicada3301_lp", "Solving attempts and 3D models (2024-01). Not read.", None),
 ("iBotPeaches__cicada_3301", "2025-03 to 2026-08; clone contains no working-tree files "
  "at HEAD in this checkout. Not assessed.", None),
 ("cijhho123__cicada3301", "Clone landed with a broken checkout. Not assessed.", None),
 ("neuroretransmit__cicada", "Clone landed empty. Not assessed.", None),
]:
    kind = "no-decoder" if n in ("thomasandfriends__Cicada3301Runes",
                                 "cicada-solvers__solving-3301-code-2013",
                                 "rtkd__idclip") else "unknown"
    add(n, decoder_type=kind, null_trustworthy=("n/a" if kind == "no-decoder" else "unknown"),
        evidence=why, what_it_tried=why,
        what_it_concluded=("n/a" if kind == "no-decoder" else "Not assessed."), notes=note)
