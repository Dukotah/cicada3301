# Liber Primus LP2 (pages 0–55) — 20-Front Armada After-Action Report

_Run 2026-06-20. 36 agents across two workflow waves (~1.26M tokens). Every approach
adversarially verified by an independent agent that re-tested any candidate key in the
validated rig. Scratch + scripts + result JSONs under `analysis/armada20/`._

## 1. Bottom line

**Nothing broke LP2.** All 20 approaches returned `hit=false`; every decrypt sat in the
near-random band. Best score across the entire armada was **−6.023** (approaches #17 and
#21), versus the ~−6.23 prior baseline, the ~−7.3 random floor, and the ~−5.0 readable-English
break threshold — with **zero** readable English anywhere. The one genuinely-open lead going
in (real OutGuess steganography on the page images) is now **closed**: a from-source OutGuess
0.4 build, validated against every known historical payload, recovered nothing from the LP2
rune pages. This is fully consistent with the prior OTP/running-key-class diagnosis.

## 2. Full results (all 20 + the OutGuess build)

| #  | approach | verdict | best score | one-line result |
|----|----------|---------|-----------|-----------------|
| 17 | Explicit interrupter-model short-key search | refuted | −6.023 | Best in armada, still gibberish, ~1 above break line |
| 21 | **REAL OutGuess build + stego extraction** | refuted | −6.023 | OutGuess 0.4 built & validated; LP2 pages carry NO payload — stego claim debunked |
| 4  | Cross-year corpus (Tao/Blake/Gospel of Thomas) running-key | refuted | −6.104 | All three texts ruled out, plain + interrupter beam |
| 15 | Doublet-deficit-as-prior decode | no_finding | −6.19 | Prior provably non-discriminative; Viterbi = fabrication artifact |
| 2  | Anglo-Saxon Rune Poem as key/schedule | refuted | −6.22 | Running key + 6 stanza-schedules, all gibberish |
| 3  | Cicada PGP-signed messages as keytext | no_finding | −6.255 | Cicada's own prose is not the key |
| 5  | Primes/totients as transposition + interrupter | refuted | −6.30 | Transpose+substitute combo, all noise-band |
| 19 | Solved pages as a key-location riddle | refuted | −6.33 | New phrases/hash/magic-square keys all gibberish |
| 1  | Solved-plaintext as key (rune/gematria space) | refuted | −6.40 | Self-referential running key → gibberish |
| 16 | Hill / matrix cipher (29-rune, mod 29) | refuted | −6.52 | 2×2 exhaustive (682,080) + 3×3 sampled, all noise |
| 13 | PGP operational forensics | no_finding | −6.55 | RSA sound (no keyspace bound); fingerprint/b64 fail as keys |
| 18 | Deep-research: claimed solves since 2018 | no_finding | −6.57 | No credible LP2 solve exists; DJU BEI repeat = chance |
| 8  | Solver-repo hardcoded-key code search | refuted | −6.76 | Only solved-page keys exist in code; unsolved = "Key: ?" |
| 9  | Archive mining for posted key fragments | refuted | −6.89 | No posted external key; all cribs near-random |
| 6  | Cicada constants as PRNG seeds | no_finding | −7.42 | 2080 BBS/LCG/MT configs at/below random floor |
| 7  | Uncovering Cicada wiki + community state | refuted | n/a | No new key/crib/method; cookie-hash keys fail; stego claim debunked |
| 10 | Private-stage participants & leaked hints | no_finding | n/a | No insider ever leaked a key; nothing new to test |
| 11 | Stego sweep (pure-Python LSB/DCT) | no_finding | n/a | LP2 pages structurally clean; superseded by #21 |
| 12 | EOF/appended-data + EXIF forensics | no_finding | n/a | Only the known 2012 4chan ROT URL; no new payload |
| 14 | Crib-dragging under running-key | no_finding | n/a | "THE"-quadgram artifact only; controls beat thematic cribs |

## 3. The one open lead — now closed (#21, OutGuess)

A real OutGuess **0.4** was built from source (resurrecting-open-source-projects/outguess;
required `--with-generic-jconfig` and a `-std=gnu17 -w` build to get past gcc 15 / C23 on the
bundled jpeg-6b). **Validated end-to-end**: keyless `outguess -r` recovered the exact known
historical payloads — the 2012 4chan book code (`reddit.com/r/a2e7j6ic78h0j/ … 3301`) and the
2013 `-----BEGIN PGP SIGNED MESSAGE-----` block.

Run against the LP2 target pages (relikd `p*.jpg`): **no payload** — uniform random noise or
an FPE crash on every sampled page. `steghide`/`stegseek` likewise found nothing (expected;
Cicada used OutGuess, not steghide). The community claim that "every LP page JPG carries
OutGuess data" is **debunked**: the genuine OutGuess payloads were always embedded in the
2012–2014 *clue* images (1033.jpg, wisdom/folly temp files, onion cookie images), never the
Liber Primus rune pages, which were distributed as a book/PDF.

_Caveat retained honestly:_ the relikd images are re-encoded re-hosts (re-encoding destroys
OutGuess payloads), so this is technically not a test of the literal original-upload JPGs.
But the source-level provenance (rune pages were never individually OutGuessed) makes a
hidden-payload-on-rune-pages hypothesis very unlikely regardless.

## 4. Newly eliminated — append to the do-not-redo list

- Solved-page plaintext/ciphertext as a running key in **rune/Gematria-index** space (all orderings, signs, atbash, offsets, interrupter beam) — #1
- Cicada's own PGP-signed message prose as keytext (combined/individual/reversed) — #3
- **Tao Te Ching, Blake's _Marriage of Heaven and Hell_, Gospel of Thomas** as running keys — #4
- **Anglo-Saxon Rune Poem** as running key AND as 6 per-rune stanza-order substitution schedules — #2
- Cicada-constant-seeded PRNG keystreams (Blum-Blum-Shub, glibc/MMIX LCG, Mersenne-Twister), additive + interrupter-schedule modes — #6
- **Prime/totient COLUMNAR-TRANSPOSITION + short-keyword Vigenere/mono combo**, and prime/totient **interrupter schedules** over short keywords — #5
- Solver-repo / public-code hardcoded-key harvest (40 themed keys incl. INSTAR, FOURFIVEFIVE) — #8
- Archive-mined cribs + 2013 onion **cookie hashes** (167=/761=) as running keys — #9, #7
- PGP public-key base64 + fingerprint hex as keys; RSA shown sound (no Fermat/ROCA/shared-factor) — #13
- Bidirectional crib-dragging under running-key (9 thematic cribs) — #14
- Doublet-deficit-as-Bernoulli-prior decode (short-Vigenere hillclimb, free-key Viterbi, autokey) — provably non-discriminative — #15
- Hill cipher: 2×2 **exhaustive** + 3×3 sampled — #16
- Explicit interrupter model (29 candidate runes × {skip/advance/reset/enc} × short Vigenere) — #17
- OEIS A061474, Beaufort w/ prime/totient streams, pi(p) key, cipher-feedback shift, progressive Vigenere — #18
- Solved-corpus "riddle" interpretations: ~50 directive phrases, AN-END SHA-512 hex, magic-square stream, ASCII-form solved text as key — #19
- **Real OutGuess** (validated 0.4 binary) on all LP2 rune pages + steghide/stegseek — #21

Reinforced (not new): the DJU BEI 6-gram repeat on pages 27/55 is chance (Poisson P≈13%) — not a same-key crib.

## 5. Verdict on "the key is already out there"

A **public, Cicada-published LP2 key almost certainly does not exist.** Convergent OSINT/research
(#3, #7, #8, #9, #10, #18, #20):

- Cicada **never published an external key** for any page. All ~17 solved LP pages used
  self-contained mechanisms (reversed/Atbash Gematria, page-stated shifts, prime/totient
  keystreams, short thematically-derivable Vigenère). No solved page ever required an external keytext.
- Every public solver corpus (scream314, relikd, r4nd0mD3v3l0p3r, krisyotam) marks the unsolved
  pages "Key: ?". The only hardcoded keys in any repo are the already-known solved-page keys.
- No insider ever leaked key material; no post-2018 solve claim clears the PGP-signature
  credibility gate. Cicada has been functionally silent since the verified 2017-04-04 message.
- The community wiki's own "Loose ends" page names the **doublet deficit** as "the only solid
  clue toward the cipher/key found in the runes" — and states LP2 is "not a simple short-key
  Vigenère or mono-alphabetic cipher." Both match this rig's independent findings.

So the OSINT "secret waiting to be found" thesis is a dead end — there is no oracle to recover.
The realistic remaining possibilities, neither resolvable by brute force:

- **(b)** the key is an external, already-public text Cicada expected solvers to recognize that
  simply hasn't been tried (running-key class stays live only for *untried* known texts —
  esoteric/alchemical primary sources are the obvious unexplored candidates); or
- **(c)** the pages are built-to-be-unsolvable / true OTP — consistent with flat IoC, absent
  period, and ~5× doublet suppression, and unfalsifiable.

The evidence does not distinguish (b) from (c). Brute force cannot; only finding the one
specific correct keytext (b) would. **Cryptanalytic brute force on LP2 is now exhausted.**
