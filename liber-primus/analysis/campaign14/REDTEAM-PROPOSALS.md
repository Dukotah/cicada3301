# Campaign XIV — Fable 5 red-team: prioritized proposal agenda

Fresh-eyes proposals from a 4-lens Fable 5 red-team of the whole approach. Each was required to fit
flat-IoC 1.000 + the 0.66% doublet deficit and to state a falsifiable signal. Ordered by the reviewers'
stated prior. Items marked **[DONE XIV]** were executed in this campaign (see CAMPAIGN-XIV-FINDINGS.md);
the rest are the standing agenda for future researchers.

## [high] Word-length / separator metadata battery (the plaintext-visible side channel the cipher never touched)
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** Orthogonal to the rune stream — makes no claim about IoC or doublets, so trivially consistent; it tests the load-bearing assumption UNDER the OTP verdict (that there is an English message).
- **how to test:** Chi-square word-length and word-length-bigram distributions of unsolved pages vs (i) solved-LP plaintext, (ii) English/Latin/Old-English corpora mapped through Gematria Primus, (iii) random-filler models (uniform lengths, copied-length templates). Also compare per-page word-count/line-length structure against solved pages.
- **falsifiable signal:** Match to solved-LP English profile => plaintext is real English prose (constrains every future attack, enables word-boundary pruning in the beam decoders above); match to nothing => first positive evidence for the filler/pad hypothesis, overturning the implicit 'there is a message' assumption. Either outcome is information; the test cannot 'fail silently'.
- **cheap:** True

## [medium] Skip-tolerant keystream decode (the page-73 mechanism generalized): DP/beam over key-advance skips, anchored backward from the solved AN-END page
- **lens:** structure_meta
- **fits constraints:** Verified by direct simulation using the repo's own lp.stats: uniform-mod-29 keystream (phi(primes)) + soft skip-on-collision yields IoC*N = 1.000 (flat) and doublet 0.46% at suppress=0.83 (0.66% at ~0.75) — the only proposed mechanism besides the project's resample-OTP model that hits both numbers, and unlike resample-OTP it is low-entropy and attackable. Short WORD keys fail the flat-IoC constraint (sim: IoC*N 1.204) so the sweep should be over uniform-coverage streams, not keywords.
- **how to test:** 1) Build a DP decoder: state=(position i, stream index j); transitions j+1 (always) and j+2 (only when c[i-1]-c[i] = st[j]-st[j+1] mod 29, small log-penalty); emission = quadgram score of decoded rune. 2) Validate on synthetic: encrypt English with each generator + soft skip, confirm the DP recovers it and that wrong generators score in the noise band. 3) Sweep the Cicada-attested generator family (primes, phi(primes), iterated phi, prime gaps, Fibonacci seeds) x start offsets 0-1000 x both signs x +/-Atbash, per page AND as one continuous stream. 4) Sharpest sub-case: page 73's phi(prime) alignment is KNOWN — if the book is one continuous stream (the project's own STRUCTURE-FINDINGS evidence), run the DP backward from that anchored index across pages 55..0, absorbing unknown skip count (~430 expected) in the DP window. Also compose with the F-interrupter beam (plaintext nulls) the rig already has in solve.py.
- **falsifiable signal:** For any (generator, offset, sign, atbash): DP best-path score in the English band (score_norm -4.0 to -4.4, threshold -5.2) with readable Gematria-English, vs the noise band (~-6). Synthetic validation gives the exact expected separation. A full null over the attested generator family cleanly closes the skip variant and genuinely upgrades the OTP verdict.
- **cheap:** True

## [low] Doublet forensics: the 86 tolerated doublets as a fingerprint or side-channel
- **lens:** structure_meta
- **fits constraints:** This analyzes the observed statistics rather than assuming a mechanism, so it is consistent with flat IoC and the deficit by construction. Any positive finding would refine WHICH filter model holds; a null still discriminates rejection-sampling from deterministic exemption (constrains hand vs tool generation).
- **how to test:** All cheap, one script: (a) KS test of the 86 positions against uniform, and gap distribution against geometric; (b) chi-square of the 86 doubled VALUES against uniform; (c) cross-reference positions with word boundaries, line starts, F-rune adjacency, and page offsets; (d) gaps and positions mod 29 / mod small n as rune indices, scored for English; (e) the 86 doubled runes read in order as an 86-rune string through identity/Atbash/gematria; (f) positions vs primes and vs the pp49-51 payload interpreted as a gap table (see proposal 4).
- **falsifiable signal:** Distribution tests: p < 0.001 non-uniformity = structure exists. Decode tests: score_norm in the English band. Otherwise: a measured 'positions are uniform, values are uniform' null that pins the filter as memoryless rejection — itself a publishable refinement of Campaign XI.
- **cheap:** True

## [low] Preserved plaintext metadata: word-length / punctuation / layout channel (and the English-shape test the whole project silently depends on)
- **lens:** structure_meta
- **fits constraints:** Fully consistent: it makes no claim about the rune stream at all — flat IoC and the doublet deficit are untouched whether the metadata carries content or not. An acrostic forced in CIPHERTEXT would locally dent uniformity, which is itself the test in (c).
- **how to test:** (a) chi-square word-length distribution of the 55 pages vs solved-page plaintext word lengths vs random-segmentation null; (b) word-length sequence and punctuation sequence as base-10/base-29 digit streams -> primes/ASCII/runes, scored; (c) uniformity test on line-initial, word-initial, and page-initial ciphertext runes vs the global uniform distribution (any forcing = non-uniform); (d) per-page word counts and line counts as an integer sequence vs primes/OEIS; (e) word-length n-gram matching against an LP1 phrase bank (A WARNING, AN END, THE PRIMES ARE SACRED...) to generate positional crib hypotheses feeding proposal 1.
- **falsifiable signal:** (a) is decisive either way: match (p > 0.05 vs solved pages) = English plaintext confirmed; mismatch (p < 0.001) = the scoring assumption is broken. (b)/(d): any decode over threshold. (c): p < 0.001 non-uniformity at line/page starts.
- **cheap:** True

## [low] Plaintext-side word-boundary forensics (the channel an OTP cannot protect)
- **lens:** Highest-expected-value untried experimen
- **fits constraints:** Fully consistent by construction: word-length metadata is orthogonal to symbol statistics. A filtered-OTP over English with real separators produces exactly IoC·N 1.000 and 0.66% doublets AND English-like word lengths; a hand-generated decoy produces the same symbol stats but arbitrary word lengths. The test does not propose an alternative cipher — it interrogates the one channel the established mechanism leaves open.
- **how to test:** Extract word-length sequences from data/krisyotam_runes.txt (split on -/./%); build the English-in-runes reference from solved-page plaintexts and from corpus texts encoded with src/lp/gematria.keyword_to_indices; run KS/chi-square on distributions; run sliding exact+fuzzy sequence matching (edit distance on length vectors) of each page against each candidate text with permutation-based p-values. Pure Python over existing repo data; an afternoon of work.
- **falsifiable signal:** Arm 1: KS statistic inside vs outside the solved-page/English band (either outcome is decisive: match = a real English plaintext exists, framing survives but 'no purchase' weakens; mismatch = plaintext is not ordinary segmented English, so every English-scored elimination is conditional and the decoy hypothesis gains). Arm 2: any page whose word-length sequence matches a public text above the decoy null (p < 1e-3) — verify by subtracting to recover the pad and checking the pad's own statistics.
- **cheap:** True

## [low] Total-structure closure: cross-validated compression / sequence-model test vs matched filtered-uniform controls
- **lens:** Highest-expected-value untried experimen
- **fits constraints:** The controls are constructed to reproduce both signature statistics precisely, so the test measures only structure BEYOND the two constraints — it cannot contradict them, it audits what they leave unexamined.
- **how to test:** Generate 1,000 filtered-uniform 12,956-rune controls with campaign11's suppression model (seeded); compute cross-validated bits/rune for LP2 vs the control band using (a) KT/PPM context models orders 1-8, (b) LZMA on packed indices, (c) optionally a tiny transformer. Also add the two provenance sub-tests Campaign IV skipped: sliding-window dispersion (multinomial vs under-dispersed — machine sampler vs human/deck generation) and monogram frequency drift across the book (fatigue signature).
- **falsifiable signal:** LP2 bits/rune below the 1st percentile of the control band (or predictor accuracy significantly above 1/29-adjusted baseline) = computable structure exists = the OTP verdict is WRONG and there is an attack surface. LP2 inside the band = the strongest possible ciphertext-side confirmation ever run — upgrades 'OTP-class' from low-order-verified to model-class-verified.
- **cheap:** True

## [low] Word-length skeleton attack (the metadata channel the rig never enumerates)
- **lens:** assumptions — is the "OTP-class / inform
- **fits constraints:** Uses only metadata (separator positions), so it is orthogonal to — and fully consistent with — flat IoC 1.000 and the 0.66% doublet deficit; a filtered pad over word-preserving encipherment produces exactly the observed rune statistics while leaking the word skeleton.
- **how to test:** (1) Convert candidate corpora (the 112 already-fetched keytexts are sitting in analysis/campaign12-13 — reuse them as PLAINTEXT candidates, which nobody did) to rune-word lengths via the Gematria digraph compression (TH/EO/NG/OE/AE/IA/EA); (2) slide each unsolved page's length sequence over each corpus with exact and ±1-tolerance matching; (3) calibrate false-positive rate on shuffled skeletons. Separately: compare the skeleton's bigram/positional statistics (1-rune-word placement, sentence-like rhythm) against solved-page plaintexts vs a decoy-generator null.
- **falsifiable signal:** A corpus passage whose rune-word-length sequence matches a page beyond the shuffled-control FPR → instant plaintext candidate → subtract to get the key and inspect it. Clean null over large corpora is also informative: plaintext is original composition (like the koans), or the boundaries are decoys — either way the skeleton's English-likeness must then be explained.
- **cheap:** True

## [low] Homophonic-downward / variable-rate encoding search (the ledger's substitution row eliminates the wrong class)
- **lens:** assumptions — is the "OTP-class / inform
- **fits constraints:** Uniform choice among homophones → IoC·N = 1.000 flat; repeat-avoiding homophone selection → doublet deficit, soft (author slips ~1 in 6) — matches 0.664% without any keystream at all.
- **how to test:** Simulated-annealing / EM over surjective maps 29→k (k = 5..26) maximizing class-stream quadgram score under multiple language models (English, Latin, Old English) plus structured-data models; validate the searcher first on synthetic homophonic ciphertext (rig tradition); score real pages against a 1000-shuffle control envelope. Also test the natural partitions first (futhorc aetts, vowel/consonant, index mod k, prime residues).
- **falsifiable signal:** An optimized partition whose class-stream score on real ciphertext exceeds the shuffled-control 99.9th percentile and generalizes across held-out pages. Failure across all k and language models = class closed with a measured null.
- **cheap:** True

## [low] Seeded-generator keystream with encryption-time skip filter (hash-chain / HMAC-DRBG / RC4 / AES-CTR / MD5-SHA1-SHA256 chains from a Cicada-derived seed dictionary), decrypted with filter-aware beam
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** Hash/stream-cipher output is uniform => IoC.N 1.000 and flat bigram (both now measured true); skip-on-repeat applied at encryption => doublet deficit, strictly lag-1 (measured today: lag-2..12 all ~3.4%, only lag-1 suppressed — exactly this signature); hand slips ~1-in-6 => soft 83%.
- **how to test:** One harness: seeds = {37-string Cicada dict, 3301 variants, magic-square constants, the AN END 512-bit hash string, solved-page phrases} x generators {MD5/SHA-1/SHA-256/SHA-512 chain & counter, HMAC-DRBG, RC4, AES-CTR} x mod-29 reductions {byte mod 29, rejection >=232, 16-bit word} x {filter-aware skip beam on/off, sign, Atbash}. ~10-20k configs x 55 pages, hours. Validate the beam on synthetic filtered ct first (rig-style).
- **falsifiable signal:** Any page scoring above the validated -5.2 quadgram threshold (or IoC.N of decrypt > 1.3, language-agnostic) = break; clean sweep = the family joins the ledger with named seeds/generators. The harness self-validates by recovering a planted synthetic key.
- **cheap:** True

## [low] pp49-51 payload as PRF seed / stream-cipher key for the runic pages (payload EXPANDED, not used directly)
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** PRF expansion of a high-entropy seed => uniform keystream => IoC.N 1.000 + flat bigram (both measured); the doublet filter sits at encryption exactly as in the previous proposal; strictly-lag-1 suppression consistent.
- **how to test:** Expand canon_256.bin via {RC4(key=payload), AES-128/256-CTR (key||IV from payload), SHA-256/SHA-1/MD5 in counter and chain mode, HMAC-DRBG(seed=payload)} x 3 mod-29 reductions x {skip-beam on/off, sign, Atbash, per-page vs continuous stream, payload forward/reversed}; decrypt all 55 pages, score quadgram + language-agnostic IoC. A few hundred configs — an afternoon.
- **falsifiable signal:** Any decrypt over -5.2 (or decrypt IoC.N > 1.3) = solve; all-null = a new named ledger row ('payload as PRF seed: dead'), closing the payload's last natural cryptographic role.
- **cheap:** True

## [low] Extended-corpus second-order rerun (ingest the ~75-page community corpus; kappa/in-depth/bigram across old-new joins)
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** Makes no mechanism claim; targets the one weakness (reuse) that flat IoC and the doublet deficit cannot exclude across data the rig has never loaded.
- **how to test:** Verify + ingest the additional community-transcribed pages (3-way check as before); rerun the kappa spectrum to full corpus length, page-on-page in-depth, bigram matrix, and re-test the lag-3915/5091 blips on the enlarged stream.
- **falsifiable signal:** Any lag with kappa > 5 sigma AND aligned-difference IoC.N > ~1.02 (English-difference signature) = in-depth attackable key reuse; otherwise the OTP verdict extends to the full book and the blips die.
- **cheap:** True

## [very-low] pp49-51 payload as per-page/meta PARAMETERS: page permutation, keystream offsets, or the doublet-gap table
- **lens:** structure_meta
- **fits constraints:** Makes no mechanism claim about the rune stream; per-page offsets compose with proposal 1 (offsets into a shared generator preserve flat IoC and the skip-produced deficit). Page-permutation readings only claim the reading ORDER differs, which the underpowered 54-pair boundary test (see flawed assumptions) does not exclude.
- **how to test:** (a) instant: slide a 56-byte window over the payload, test each for being a permutation of 0-55 (mod-56 and rank-order variants); (b) instant: read the payload as 85-128 gap values (8-bit, 16-bit LE/BE, varint) and correlate against the real doublet-position gaps [122, 85, 249, 197, 129, ...]; (c) cheap: use bytes 0-55 (and windows) as per-page start offsets into each generator of proposal 1's DP sweep; (d) bytes mod 29 as per-page Atbash/shift toggles feeding the same DP.
- **falsifiable signal:** (a) a valid permutation window (probability ~10^-24 by chance per window — unambiguous); (b) rank correlation with observed doublet gaps, |r| > 0.5 with p < 10^-6; (c)/(d) English-band DP scores. All tests have hard numeric gates; expected outcome is null and that is fine — each is minutes of compute.
- **cheap:** True

## [very-low] Reader-supplied procedural keys: Cicada-attested TRANSFORMS of the solved-page plaintext as keystreams
- **lens:** structure_meta
- **fits constraints:** These streams have near-uniform mod-29 coverage (prime values mod 29 are equidistributed), so flat IoC holds; the doublet deficit comes from the same skip/filter layer as proposal 1 (compose each derived stream with the skip-DP). A raw derived stream alone would fail the deficit — which is why it must be run through the skip decoder, not the plain runningkey attack.
- **how to test:** Enumerate the transform set: {identity, Atbash} x {gematria prime value, phi(prime), index, cumulative sum} x {LP1 plaintext, solved LP2 plaintext, the rune poem, Gematria Primus table order} — a few dozen streams. Run each through the validated runningkey harness AND through proposal 1's skip-DP, all offsets, both signs. Strictly cap the set at Cicada-attested operations to avoid open-ended dredging.
- **falsifiable signal:** score_norm over -5.2 with readable English on any page vs the -6 noise band; synthetic validation of the harness on a known transform first. A null closes the 'procedural key from solver-held material' class with named, enumerated members.
- **cheap:** True

## [very-low] Full-lag self-coincidence scan (lags 31-6,478) + corpus-wide long-period attack (periods 41-2,000)
- **lens:** Highest-expected-value untried experimen
- **fits constraints:** IoC: periods >=~80 are observationally indistinguishable from 1.000 at n=12,956. Doublets: the 0.66% deficit is produced by the output-side no-repeat filter that EVERY surviving model already requires (Campaigns X/XI showed the filter acts on the written output, not the key) — the filter is orthogonal to key periodicity, so 'periodic key + the same output filter' reproduces both statistics.
- **how to test:** One script: coincidence rate c(L) = P(c_i == c_{i+L}) over the full concatenation for every L in 1-6,478 with binomial error bars; flag any L above 4%. If a spike appears, run the existing column-frequency attack corpus-wide at that period (both signs, +Atbash), with scoring made tolerant to ~2.7% filter-perturbed positions.
- **falsifiable signal:** Any lag with coincidence rate significantly above 3.45% (>4 sigma) = key reuse/periodicity = the OTP verdict is falsified and the page is breakable. All-flat = the 'every periodic key' claim finally becomes true for all periods, corpus-wide, instead of 1-40 per-page.
- **cheap:** True

## [very-low] Second-tokenization running-key re-sweep (letterwise + prime-value mappings)
- **lens:** Highest-expected-value untried experimen
- **fits constraints:** Identical consistency story to the ledger's own running-key attacks: the doublet deficit and flat IoC come from the ct-side no-repeat filter layered on the running key; a filtered running-key ciphertext still decrypts to ~97% English under the true key, so the attack remains valid and both statistics remain explained.
- **how to test:** Add a letterwise_to_indices variant (and a prime-value-mod-29 variant) beside keyword_to_indices; re-run attack.py runningkey over the already-fetched 112-text corpus (data/keys/, campaign12/13 fetchers) — pure re-execution, no new data. Threshold and scoring unchanged.
- **falsifiable signal:** Any page/text/offset scoring above the validated -5.2 threshold (English -4.0 to -4.4); the existing selftest already proves the pipeline recovers planted keys.
- **cheap:** True

## [very-low] pp49-51 payload as RSA signature/ciphertext under known Cicada public keys
- **lens:** Highest-expected-value untried experimen
- **fits constraints:** The payload is a separate non-runic object; the runic statistics (IoC 1.000, 0.66% doublets) place no constraint on it. No conflict possible.
- **how to test:** Collect all RSA moduli from Cicada's published PGP keys (keyservers/archives already mirrored in analysis/osint/) and the 2012/2013 puzzle RSA values; for each (n, e) with n > payload-as-int, compute pow(s, e, n) in both endiannesses and pattern-match PKCS#1/PSS/known-digest structure. Minutes of compute.
- **falsifiable signal:** pow(s, e, n) yielding 0x0001FF..FF00||DigestInfo (or valid PSS trailer 0xBC) for any known Cicada modulus — unambiguous, zero-false-positive structure. Clean nulls close the last natural 2048-bit interpretation of the blob.
- **cheap:** True

## [very-low] Targeted doublet-site image count-audit (haplography test — the cheap falsifier of the entire 'engineered filter' edifice)
- **lens:** assumptions — is the "OTP-class / inform
- **fits constraints:** Challenges whether the 0.66% statistic is real rather than needing to reproduce it; flat IoC is untouched either way (IoC is insensitive to ~2.7% merged runes).
- **how to test:** From the SHA1-verified 400-DPI renders, crop the neighborhoods of all 86 canon doublet sites plus ~200 random adjacent-pair sites; audit RUNE COUNT (not identity) per crop by eye and/or the existing template matcher (which was 69.5% on full pages but is near-trivial on 3-5 rune crops). Also cross-check per-page rune totals against line-count × runes-per-line from the images.
- **falsifiable signal:** Any systematic finding of adjacent-equal rune pairs in the images where canon records a single rune. Even ~20 confirmed merges moves the true doublet rate toward random and forces re-running Campaign X — ciphertext autokey (IoC 1.000, doublets 3.45%) would come straight back onto the table. Clean audit = the deficit is finally count-verified and the OTP verdict hardens.
- **cheap:** True

## [very-low] Generator-fingerprint suite: pin down HOW the filtered stream was produced (finish what I started above)
- **lens:** assumptions — is the "OTP-class / inform
- **fits constraints:** These are measurements OF the two constraint statistics' fine structure; by construction consistent.
- **how to test:** (1) Conditional next-rune distribution following each rune value (a resampler leaves uniform-over-28; a Fisher-Yates-with-swap or shuffle-bag leaves detectable under-dispersion); (2) windowed chi2 under-dispersion sweep (shuffle-bag = sub-random symbol balance in windows); (3) recompute everything over the ~75-page community corpus (the project's own flagged gap) — 40% more data doubles power on all fine-structure tests, including the underpowered page-boundary result; (4) doublet rate conditioned on preceding doublet distance (geometric-gap test: soft-iid filter predicts geometric; I saw no periodicity but never fit the gap law).
- **falsifiable signal:** Any deviation from the iid-rejection-sampler predictions (non-uniform post-repeat distribution, windowed under-dispersion, non-geometric gaps) = a NEW exploitable regularity in the keystream and a fingerprint of specific generator code; full conformance = the strongest possible confirmation of the OTP verdict, with the 'hand-generated pad' loophole (and its human-bias attack surface) formally closed.
- **cheap:** True

## [very-low] Generalized-combiner ciphertext-feedback family (permutation-chain c_i = p_i + g(c_{i-1}), full Latin-square tableau chain c_i = T[p_i][c_{i-1}], and doublet-avoidant homophonic-class re-encoding)
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** Doubly stochastic transition kernel => unigram IoC.N exactly 1.000; rare-letter fixed points => doublet ~0.66% (soft, plaintext-dependent); complete-mapping g => marginal differences flat with hole at 0; chain never resets => continuity across page joins. Fits every statistic the project published.
- **how to test:** Compute the 29x29 bigram matrix over the 12,955 adjacent pairs; measure conditional IoC.N per row and off-diagonal chi-square vs uniform. If structured, anneal g (29! space, trivial) / T (Latin-square-constrained) against quadgram score, validated first on synthetic ct.
- **falsifiable signal:** EXECUTED during this review: bigram matrix is dead flat — off-diagonal chi2 = 841 vs df 811 (z = +0.75 sigma), conditional IoC.N mean 1.026 vs 1.037 for the uniform-with-hole null, bigram entropy 9.642/9.716 bits. The entire first-order feedback-combiner family (and homophonic-class encoding over any structured inner stream) is hereby FALSIFIED with new data — this should be added to the elimination ledger as a genuinely new closure, because until this measurement the family was live and the 'autokey excluded' claim did not cover it.
- **cheap:** True

## [very-low] Skip-tolerant re-verification of the 112 'eliminated' keytexts (soundness patch, not a lead)
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** Skip-filter at encryption produces the doublet deficit and lag-1-only suppression; the IoC 1.000 constraint is only satisfied if the keytext is near-uniform in rune space (numeric/tabular text) or the plaintext is not frequency-typical — stated honestly as the surviving corner.
- **how to test:** Beam decoder with key-skip transitions (penalized), validated on synthetic skip-filtered running-key ct, re-run over the existing ~117-text corpus (fetch scripts already in analysis/campaign12).
- **falsifiable signal:** Beam finds an over-threshold decrypt some text where rigid alignment scored ~-6 => break; all-null => the keytext eliminations become sound against filtered use, and the ledger caveat is discharged.
- **cheap:** True

## [very-low] LP2-as-pad inversion: the unsolved pages ARE key material, not a message
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** If LP2 IS the random keystream, IoC.N 1.000, max entropy, flat bigram, and a generation-time no-repeat discipline (soft 83%) are all properties of the artifact itself — the constraints are satisfied by construction rather than explained by a cipher.
- **how to test:** Use the 12,956-rune stream (fwd/rev, +/-, Atbash) as running key against every other machine-readable Cicada object: unsolved 2012/2013 fragments, the 512-bit AN END hash bytes, the pp49-51 payload (payload minus LP2-stream => structure?), onion names, PGP message bodies. Finite, hours.
- **falsifiable signal:** Any counterpart object decrypting to over-threshold English/structure = paradigm-level break; all-null = documented closure of the inversion (it is finitely testable precisely because the candidate message set is small).
- **cheap:** True

## [very-low] Language-agnostic and non-English re-scoring of all sweep bests (Old English / Latin / IoC-of-decrypt)
- **lens:** cryptanalysis — constructions that produ
- **fits constraints:** Scoring-layer change only; no mechanism claim, so trivially consistent with both statistics.
- **how to test:** Build OE and Latin quadgram tables mapped through Gematria Primus; re-score the archived best-candidate decrypts of every prior sweep (vigauto, runningkey, keystream, autokey brute) plus add decrypt-IoC.N > 1.3 as a language-blind gate to all future harnesses.
- **falsifiable signal:** Any archived 'null' whose decrypt scores high under OE/Latin or shows IoC.N > 1.3 = missed hit; none = the English-plaintext assumption is discharged for everything already run.
- **cheap:** True
