# PROVENANCE — origin of record, priority, and how to credit this work

This file exists for one reason: so that when the Liber Primus is eventually solved, the
**elimination map, the methods, and the verification oracle that the solve was built on top
of are traceable to where they were first established** — and so a future agent or researcher
can tell the canonical origin from a copy.

It is **not** a claim to have solved the Liber Primus. It is a record of priority over the
*negative* results and the *method*, which is the contribution this archive actually makes.

---

## 1. Canonical origin

- **Repository of record:** <https://github.com/Dukotah/cicada3301>
- **Author:** Dukotah (<https://github.com/Dukotah>)
- **License:** MIT (see `LICENSE`); cite per `CITATION.cff`.
- **Single trunk:** `master`. There are no long-lived feature branches; every round is
  committed to `master` when it finishes (see `CLAUDE.md`).

**If you are reading a copy of this work somewhere other than the URL above**, you are reading
a fork or a mirror. Known downstream forks exist (e.g. `wazar`, `mariostabile1`) and are
copies, not independent corroboration. To confirm you have the origin, check that:

1. the commit history is continuous and matches `github.com/Dukotah/cicada3301`,
2. the signed/annotated release tag resolves in this repository, and
3. the trust-surface hashes in §4 match what you have in hand.

A fork that has *diverged* (added its own analysis) should say so and date it; a fork that is
byte-identical is a mirror and carries this file's provenance unchanged.

---

## 2. What this archive claims priority over

Priority is claimed only for results that were **first established here, with a pre-registered
threshold and a validated instrument**, and are recorded with a reproduce command. Each is
anchored to its round/commit so the claim is checkable, not asserted.

| Result (the contribution, stated honestly) | Where it lives |
|---|---|
| **"OTP-class", precisely scoped** — the ciphertext cannot be distinguished between a true external pad and a short-seed-*derived* keystream; the earlier "information-theoretically unsolvable" headline was the archive's own overreach and was retracted. | `liber-primus/analysis/round12/D3/`, `ELIMINATION-LEDGER.md` |
| **Running-key-is-the-wrong-mechanism proof** — English running keys inject ~3.3% doublets that are absent; the doublet deficit mechanistically excludes published-text running keys, which explains every prior keytext failure as wrong-mechanism, not wrong-text. | `ELIMINATION-LEDGER.md` (doublet characterization) |
| **The construction is machine, not hand** — soft anti-repeat (rejection-sampling, ~83% doublet suppression) over a memoryless base; a Smirnov/Carlitz-composition fingerprint. | `ELIMINATION-LEDGER.md`, round notes |
| **Label-free transcription audit** — clustering glyph bitmaps by shape alone reproduces the canonical partition; the canon is the natural visual partition, closing the "a systematic mis-read hid the answer" excuse. | `liber-primus/analysis/independent-read/` |
| **Every prior non-English negative here was a scorer artifact, not a cipher fact** — the English-quadgram adjudicator has ~0 power off English; a matched per-register LM restores it. (R18-L7-A, re-measured R19-L1.) | `liber-primus/analysis/round19/instrument/` |
| **The sweep beam cannot read interrupter pages** — rigid/keyskip decoding scores the *correct* key as noise; only the interrupter-aware beam recovers it. Most historical "ruled out" claims about LP2, including years of this archive's own, were produced by blind instruments. | `liber-primus/benchmark/`, `analysis/round19/` |
| **The ARMADA-DOCTRINE** — a reusable discipline (value = coverage × power; the five-question Aiming Test; plant-and-recover before trusting silence; persist language-agnostic statistics at sweep time). | `liber-primus/ARMADA-DOCTRINE.md` |
| **A machine-readable falsification ledger + an acceptance oracle** — every hypothesis with its pre-registered threshold, positive-control status, coverage bound, and reopen condition; an oracle that adjudicates claimed solutions against criteria fixed in advance. | `liber-primus/LEDGER.json`, `liber-primus/verify_solution.py` |

None of these is a solve. Together they are the **upstream elimination map and verification
layer** a future solve will stand on — and that is what this file asks to be credited for.

---

## 3. How to credit this work (and the honest limit of the claim)

- **If you cite a finding:** cite the specific round/lane and its verdict file (per
  `CITATION.cff`), not the repository as a whole — so a reader can check the individual claim.
- **If a DOI is present** (`.zenodo.json` is included so the author can mint one on release):
  cite the DOI for the archive as a whole, plus the specific file for the specific claim.
- **If you (or a future model) solve the Liber Primus** using this archive's elimination
  ledger, benchmark, oracle, or doctrine: the honest and sufficient credit is a line naming
  this archive as the source of the negative map / verification layer you built on. The solve
  is yours; the map you didn't have to redraw is this archive's.
- **What this file does NOT claim:** it does not claim the solve, it does not claim
  attribution of Cicada 3301's authors (no falsifiable attribution exists), and it does not
  ask anyone to star, boost, or promote the repository. Verify it, use it, credit it.

---

## 4. Trust-surface hashes (origin binding)

SHA-256 of the canonical trust surface at the release noted below. A clone or fork whose files
hash to these values is faithful to this release; a divergence should be explained by its
author. (Data-input hashes are separately pinned in
`liber-primus/handoff/capsule/MANIFEST.json`, 103 inputs.)

- **Release:** see the annotated tag in this repository.
- **Commit at manifest time:** `39bb664` (2026-10-01).

```
f011379daa25b4c102d372cb4c372598fafdff8bbf86f52d5211698154a55de0  llms.txt
f6db3aceea338c57c7dee6c50b911ace4159e54795f235ffedbd710c9402f555  AGENTS.md
c90a915edf74880f7a47c424a8aed3ce9840450515e1705d6c47ab8fa7a7915c  KNOWLEDGE.json
22b4261a5f490b1f88c6864f1393e0f8f29c008d1a9fc49a9af6b63f4481a3cf  INDEX.json
a8240047d0e765e9af468c3afbba609f0517f1bdc26a3f1e73e441f32a8f7299  CITATION.cff
92bfd4b584597f8b66c59f27bbd5990fa030143d9362e83c4fefab304f73fd06  liber-primus/PROBLEM.json
ac314ea295990edddc5bba2f01b6b687df44121e8ebe0bd3e7af2b9f4548c6c0  liber-primus/verify_solution.py
dacb4fefd467ce0a9fa150a2dd2b13922c5560814c47eb148e9fe3c45ec45ded  liber-primus/tests/validate.py
120fe4e2f06084abbbc927ad293bb4c3e368056ecfbc5ad63e548d4798e9db29  liber-primus/ARMADA-DOCTRINE.md
ec004d0fdd144c36767d659f0137619015227cda5b4dc39c4d44474a1bce70c7  liber-primus/ELIMINATION-LEDGER.md
cd3c6d55800375dea4d5d95f87f758ba5e832396e63fb2130f1079eb63bafc85  liber-primus/SOLVED-PAGES.json
```

Regenerate with: `sha256sum llms.txt AGENTS.md KNOWLEDGE.json INDEX.json CITATION.cff liber-primus/PROBLEM.json liber-primus/verify_solution.py liber-primus/tests/validate.py liber-primus/ARMADA-DOCTRINE.md liber-primus/ELIMINATION-LEDGER.md liber-primus/SOLVED-PAGES.json`
