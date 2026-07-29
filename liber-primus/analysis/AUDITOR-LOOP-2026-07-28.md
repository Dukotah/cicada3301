# Auditor-Directed Fan-Out Loop — 2026-07-28/29

**Method.** Two autonomous multi-agent Workflows, each round: parallel *attack* agents across three
frontiers (external-artifact / attribution / novel-cipher) → adversarial *verifier* agents
(refute-by-default) → one high-effort *auditor* agent that scores both goals 0–100, marks each
frontier live/exhausted, and writes the directives that seed the next round. The loop continues
until the auditor calls the frontiers exhausted or a genuine goal-hit is confirmed.

**Scale.** 26 agents, 2 attack rounds + a final bounded closure agent, ~1.15M tokens, ~75 min.

**Goals.** (1) Solve the unsolved Liber Primus (LP2, runic pages 0–54). (2) Identify the creator.

## Verdict

The independent auditor converged on the standing project verdict and **declared all three
frontiers exhausted.** Final needles: **LP 4/100, Creator 8/100. Zero genuine goal-hits.** The run
produced closures and one reframing, not a solve.

## What was closed this session (add to the negative map)

### Solve frontier
| Lead | Result | Artifact |
|---|---|---|
| Non-additive **linear ciphertext-feedback** (k=2 full 29×29 mod-29 grid, seed-free, both signs, skip-aware beam; gate validated recovering a planted `a1=7` rule @ −4.13) — the last additive-adjacent class the OTP doublet proof did not exclude | **NULL → class sealed** | `campaign18_skip/ctfeedback_coeffs.py` |
| **Welsh-original Mabinogion** book cipher (only the English/Guest translation was ever tested) + Welsh sources | **NULL → sealed** | `bookcipher/bookcipher_expand.py`, `data/keys/welsh/` (gitignored) |
| Expanded book-cipher corpus (Rune Poem, Liber AL, Kybalion, Gnostic tractates, Blake MHH, Welsh Triads) | **NULL** | `bookcipher/bookcipher_expand.py` |
| `pp49_51/canon_256.bin` as a **ciphertext partner** (XOR vs runic slices for entropy collapse; 4×64B quarter relations) | **excluded, NULL** | `pp49_51/campaign20_extcipher.py`, `CAMPAIGN-XX-EXTCIPHER.md` |
| **AN-END 512-bit hash internal-preimage** vs every held object (solved pages, koans, PGP prose, canon_256 + quarters/variants) under SHA-2 / SHA-3 / BLAKE2, broadened 10× | **NULL** | `pp49_51/anend_preimage_broad.py` |
| **AN-END preimage under original BLAKE-512/256** (impl validated against all 4 official BLAKE known-answer vectors before use; 1572 candidate×algo combos) — last untested hash family *within the SHA-3-finalist worldview* | **NULL** [SCOPE CORRECTION 2026-07-29 (iter5 provenance): the AN-END page names NO algorithm — "SHA-512" was a community default. Skein-512-512 / Whirlpool / Streebog-512 were NOT covered; "COMPLETE" retracted until those run. See FRESHNESS/loop iter5-6 + ELIMINATION-LEDGER.] | `pp49_51/blake_closure/` |

Net: the AN-END pointer hashes **no published object we hold** under any hash family — it points at
external, now-lost Tor-v2 content, consistent with `DEEPWEB-HASH-OSINT.md`. The internal cipher
attack surface has no remaining bounded lane.

### Attribution frontier
| Lead | Result |
|---|---|
| Keyserver / web-of-trust forensics on key **7A35090F** (self-contained 2012-01-05 03:39:43 UTC RSA-4096 primary+subkey, self-sigs only, **no trust edge to any identity**) | keyserver-WoT attribution **NULL** |
| PGP signature timestamps as evidence | **spoofable** (RFC 4880 hashed subpacket from local clock) — not real-time proof; closed |
| **Pseudonym-anagram convention** (verified exact: `CageThrottleUs` = anagram of *Charlotte Guest*, Mabinogion's translator; `ImagoOnNib` = anagram of *Mabinogion*) | real signal, **names no person** — Welsh-myth cultural fingerprint |
| **Timezone / working-hours biometric** from all Cicada signing timestamps | **REFUTED** (n=26, irreproducible, attacker-settable input) |
| **`mruzuki` / `cicadeur`** — keyid `02BD208AFB8AFF75`, `mruzuki@gmail.com`, key created 2012-01-12, self-revoked 2012-01-22 (7 days after the first 3301 image): the **earliest Cicada-adjacent keyserver actor**, never investigated before | new lead; **no real-name resolution from public/sandbox sources** |

### Meta-finding (the honest attribution conclusion)
The convergence of *designed-anonymity* signals — self-expiring, WoT-isolated keys; zero
pre-disclosure footprint in 2011–2013 archives; aliases anagrammed from source-text authors rather
than real names; spoofable timestamps — **is itself the strongest supportable conclusion.** The
creator was an operationally-disciplined, cypherpunk-tradition actor who *engineered*
non-attribution. The mystery survives because it was built to survive looking.

## What remains — all outside compute / this sandbox
1. **Breach-DB / people-search on `mruzuki@gmail.com`** (freshest lead; needs a paid lookup).
2. **Private freenode 2012–2014 IRC logs**, or a surviving Tor-v2 AN-END mirror.
3. **Direct contact** with reachable humans (Eriksson `je@clevcode.org`; Wanner).

Do **not** re-run the frontiers above; the auditor already exhausted them. Only genuinely-new
external material (a recovered AN-END page or out-of-band key) can move the solve; only a
falsifiable external record (a pre-disclosure leak or a real identity behind `mruzuki`) can move the
attribution.
