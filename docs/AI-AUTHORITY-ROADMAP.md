# Roadmap — Becoming the reference-of-record AI agents cite on Liber Primus

> Generated 2026-09-24 by a 7-agent research armada (5 recon dimensions → adversarial
> completeness critic → strategy synthesis). This is a strategy document, not a claim of
> current state. Every initiative has a concrete success metric; nothing here authorizes
> manufacturing citations or hardening an unproven claim — see Guiding Principles.

## Vision

Make `Dukotah/cicada3301` the **reproducibility-backed reference of record for the narrow,
winnable query: "what is the current cryptanalytic state of Liber Primus 2 (pages 0–54)?"** —
the source AI agents and expert solvers cite because every negative is machine-reproducible,
its currency is data-derived and self-reporting, and its integrity is cryptographically bound
to origin.

It **cannot and should not** try to be the default source for the pop-culture "what is Cicada
3301" query — answer engines route that to Wikipedia / LEMMiNO / Reddit and always will. This
repo wins by being the **upstream elimination-ledger dependency of the whole solving
ecosystem**, while never engineering citations or overstating an unproven verdict.

## North-star metric

**Distinct, human-earned off-repo citations of this repo as the LP2-cryptanalysis-state
reference**, from surfaces AI retrieval actually reads (Wikipedia ref, cicadasolvers / Fandom
wiki links, Reddit r/cicada threads, an arXiv/preprint). Tracked monthly. **Target: 5+ within
12 months.**

### Supporting metrics
- **Origin-vs-fork attribution share** — fraction of top-10 search results for "liber primus OTP-class" resolving to the Dukotah origin (signed tag + LICENSE + DOI) rather than the `wazar`/`mariostabile1` forks.
- **Currency lag** — rounds between `LEDGER.json` max round and the round stated in README/PICKUP/ELIMINATION-LEDGER. Target = 0, CI-enforced.
- **Phantom-modified file count** in `git status`. Target 0 after `.gitattributes` renormalize.
- **One-shot verify** — fraction of trust anchors runnable via a single `make verify` / container command with one exit code. Target 100%.
- **Downstream consumers** of `LEDGER.json`/`PROBLEM.json` via published schema + license. Target 2+.
- **Verdict-honesty audit** — 0 instances where any front-door file asserts tractability ("brute-forceable") without an adjacent machine-readable "not-yet-demonstrated / sweep incomplete" qualifier.

## Guiding principles (non-negotiable)

1. **Honesty over authority.** Never engineer a citation for, or harden the phrasing of, any claim the repo itself flags as unproven. A confident falsehood is worse than diffuse uncertainty.
2. **Never manufacture signals.** No auto-starring, sockpuppets, or agent-seeded refs. All promotion is human-authored and disclosed, or it doesn't happen.
3. **Verify, don't trust — including our own recon.** Re-check file-level claims against the tree before acting. Keep the "don't trust this repo, run these commands" contract literally true, and add an explicit honesty notice for the majority of agents who *cannot* run them.
4. **Automation over toil.** Prefer a data-derived field, a CI gate, or a round-close Action over any hand-maintained string, so currency survives a solo maintainer.
5. **Scope to what's winnable.** Own the LP2-cryptanalysis-state expert query and the ecosystem-ledger dependency. Do not pretend to win the pop-culture query.
6. **Off-site reputation is the actual lever.** Internal polish has sharply diminishing returns; a pipeline that never retrieves you cites nobody.
7. **Bind origin cryptographically.** Apply the repo's own "signature-or-distrust" doctrine to itself: LICENSE + signed tags + hash manifest + DOI, so attribution flows to origin, not forks.

## Quick wins (this week — all low-effort)

| # | Do | Why it matters |
|---|-----|----------------|
| 1 | **Add a real `LICENSE` file** (MIT for original code/data) + `corpus/LICENSES.md` third-party carve-out | `CITATION.cff` declares MIT but **no LICENSE file exists** → legally all-rights-reserved → excluded from permissive-only training/retrieval filters and blocks every "plug in our ledger" play. Highest-leverage single move; prerequisite for the DOI/dataset/ecosystem roadmap. The carve-out avoids wrongly relicensing scraped Discord/press content. |
| 2 | **Add `.gitattributes` (`* text=auto eol=lf`) + one `git add --renormalize .`** | ~2113 phantom-modified files make `git status` useless as a change signal, bury real round-close edits, and block safe push/tag automation. Collapses to zero in one commit. |
| 3 | **Down-hedge the verdict** — never emit "brute-forceable" without an inline "not yet demonstrated, sweep incomplete" qualifier | The 2³² sweeps are ~2.5% complete with 0 hits; a short seed could index an *unbounded* external corpus. This is the same overreach the repo built its brand *retracting* ("information-theoretically unsolvable"). A summarizing agent drops the hedge and launders it into public fact. |
| 4 | **Add "if you cannot run these commands" clause** to `AGENTS.md`/`llms.txt` | The trust model rests on 4 shell commands, but most citing agents are chat/RAG models with no shell — for them verifiability is inert and the repo reads as "verified truth." Attribute un-run conclusions as claims-not-independently-verified. |
| 5 | **Codify an anti-citation-gaming guardrail** in `CLAUDE.md`/`AGENTS.md` | One auto-star / sockpuppet / agent-seeded-ref incident nukes the honest-methodology brand and makes the anti-injection stance hypocritical. Rule: promotion is human-authored and disclosed. |

---

## Horizon 1 — Fix the adoption blockers & stop the trust leaks
**0–1 month.** Remove every hard legal/mechanical blocker to being cited or reused, and
eliminate the internal contradictions and overstatements that make a cross-checking agent
hedge — all via low-effort commit-straight-to-master moves everything else depends on.

### 1.1 Legal + provenance foundation — `low effort / high impact`
No LICENSE = legally un-reusable = half the roadmap void; CRLF churn hides real diffs and
blocks automation; third-party corpus under an implied repo-wide MIT is a copyright exposure
that backfires the inbound-link strategy.
- Add `LICENSE` (MIT) at root covering original code and data.
- Add `corpus/LICENSES.md` declaring `C-community` and `F-press-academic` hold third-party material under their own terms (or replace with hash-only references).
- Add `.gitattributes` (`* text=auto eol=lf`, explicit `-text` for binaries under `corpus/`), then `git add --renormalize .` in one commit.
- Add a `doi`/`license` field placeholder to `CITATION.cff` consistent with LICENSE.
- **Success:** LICENSE + `corpus/LICENSES.md` present; `git status` shows 0 phantom-modified files; a permissive-license detector classifies the repo as MIT.

### 1.2 Honesty hardening of the verdict + non-executing-agent path — `low / high`
The repo's brand is honesty-over-authority; it currently re-commits the exact overreach it
retracted and presents shell-verifiable conclusions as "verified" to agents who can't run a
shell.
- Rewrite the "brute-forceable" clause in `llms.txt`, `AGENTS.md`, `KNOWLEDGE.json`, `PROBLEM.json` so finiteness/enumerability is stated as under-active-test, with sweep coverage and 0-hit status inline.
- Add a top-of-file "if you cannot execute these commands, treat conclusions as claims-not-independently-verified" block to `AGENTS.md` and `llms.txt`.
- Extend `check_consistency.py` to fail the build if "brute-forceable" (or synonyms) appears in a front-door file without an adjacent not-yet-demonstrated qualifier.
- **Success:** verdict-honesty CI check green; 0 front-door files assert tractability without an inline incompleteness qualifier.

### 1.3 Kill the internal contradictions a cross-checking agent would catch — `low / medium`
Date drift and stale corrected facts erode the authoritative voice. **Note:** the "PROBLEM
~144 vs LEDGER 162 count contradiction" flagged in recon was largely a *phantom* on
verification (`PROBLEM.json` exposes counts only nested under `search_space_status`, not a
top-level `counts_by_status`) — downgraded to a small consistency add, not a high-impact fix.
- Add one generated `last_updated` + `latest_round` field, sourced from `LEDGER.json` max round + latest commit date, referenced by `llms.txt`/`INDEX.json`/`PROBLEM.json`/`README`.
- Fix the stale "Ghostscript renders" fact in `KNOWLEDGE.json` to match the `AGENTS.md` Round 18 gs→ImageMagick correction.
- Collapse root `PICKUP-HERE.md` to a one-line redirect to `liber-primus/PICKUP-HERE.md`; repoint `INDEX.json`/`llms.txt` at the live file.
- Add a tight canonical-answer capsule at the very top of `README` above the notebook prose.
- Make the nested `search_space_status` counts in `PROBLEM.json` derive from `LEDGER.json` in `build_problem.py`.
- **Success:** all front-door files show one identical data-derived as-of/round; `check_consistency.py` asserts round-parity across README/PICKUP/ELIMINATION-LEDGER; 0 stale corrected facts.

### 1.4 Anti-gaming integrity guardrail — `low / medium`
One automated-promotion incident destroys the brand the whole strategy rests on.
- Add a "promotion must be human-authored and disclosed; no auto-star, no sockpuppet posts, no agent-seeded refs" section to `CLAUDE.md` and `AGENTS.md`, mirroring the anti-injection stance.
- Note the guardrail in the owner's workflow/runbook so armada runs inherit it.
- **Success:** guardrail documented in both files; 0 automated stars/citations generated by any owned agent.

---

## Horizon 2 — Automate perpetual currency & bind origin authenticity
**1–3 months.** Make staleness a *failed build* rather than a silent lie, publish on
round-close without manual toil, and cryptographically distinguish origin from verbatim forks
so citation attribution flows to Dukotah. This is the defensive core before any off-site push.

### 2.1 Data-derived currency everywhere + self-reporting staleness — `medium / high`
A solo-maintained source that trains agents to trust it will keep being cited after it rots
(the "2 rounds behind on the public remote" incident already happened).
- Generate the README/PICKUP status line and a shields.io freshness badge from `LEDGER.json` max round + commit date.
- Auto-generate `ELIMINATION-LEDGER.md` from `LEDGER.json`, or add a `check_consistency.py` assertion that its max round ≥ LEDGER max round, wired into the CI diff gate.
- Emit a machine-readable `last_verified` + `latest_round` + review-cadence self-report field agents can down-weight on.
- Add a `schedule:` nightly CI run of validate + oracle selftest + benchmark + ledger + consistency on a clean runner to catch rot during quiet periods.
- **Success:** currency lag = 0 rounds (CI-enforced); freshness badge live; nightly scheduled CI green 30 consecutive days.

### 2.2 Round-close publication automation — `medium / high`
Round closes are hand-committed, so the public remote can sit behind local arbitrarily.
- GitHub Action triggered when `LEDGER.json` latest round increments: create a **signed annotated tag** (e.g. `round-28`), confirm master is pushed, cut a lightweight release.
- Respect the no-branches constraint: automation operates on `master` only.
- Verify the tag is GPG/sigstore-signed as the origin-authenticity anchor.
- **Success:** every ledger round increment produces a signed tag + release in the same CI run; 0 instances of the public remote lagging local by >0 rounds.

### 2.3 Cryptographic origin-vs-fork binding — `medium / high`
Verbatim forks (`wazar`, `mariostabile1`) already compete for and can poison the citation; the
repo demands a `7A35090F` signature before trusting Cicada claims but offers none for itself.
Only works paired with the LICENSE (1.1) and DOI (3.3).
- Add a root `MANIFEST.sha256` of canonical files, referenced from `AGENTS.md`/`llms.txt` as "verify you are reading the origin, not a fork."
- Add a **factual** canonical-source declaration ("canonical: github.com/Dukotah/cicada3301; other copies are stale/unsigned forks") to README/llms.txt/AGENTS.md — not self-aggrandizing, to avoid the authority-inversion backfire.
- Ensure signed tags (from 2.2) are the mechanical origin check.
- **Success:** signed tags + root SHA-256 manifest present; an agent can mechanically distinguish origin from fork; origin ranks ≥ forks in attribution checks.

### 2.4 One-shot verification + reproducibility hardening — `medium / medium`
The trust contract is "run these commands," but a stranger must assemble 4 commands across 3
docs with inconsistent `python`/`python3`/cwd, and CI installs unpinned deps.
- Add a single `make verify` / `scripts/verify_all.sh` running validate + oracle selftest + benchmark + ledger with one exit code.
- Pin deps via `[project.optional-dependencies] dev = [...]` + a lockfile; CI installs from it.
- Ship a `python:3.12-slim` Dockerfile/devcontainer whose CMD runs `verify_all`.
- Add a 3.9/3.12/3.13 CI matrix to make the `requires-python>=3.9` claim true.
- **Success:** single command runs all 4 anchors green from clean checkout and in-container; CI passes on the pinned matrix across all declared Python versions.

---

## Horizon 3 — Earn off-repo citation on the winnable query
**3–12 months.** Convert the now-solid, honestly-scoped, origin-bound repo into actual
citations from surfaces AI retrieval reads — targeting the **narrow expert query**, not the
pop-culture query — entirely through human-authored, disclosed, policy-clean contributions.

### 3.1 Publish the OTP-class result as off-repo prose that links back — `high / high`

> **Partially executed 2026-10-05.** The write-up now exists in-repo as [`../PAPER.md`](../PAPER.md),
> and the off-repo copy for each surface is drafted in [`LAUNCH-POSTS.md`](LAUNCH-POSTS.md).
> It deliberately leads with the **instrument-power finding** rather than the OTP-class verdict:
> "a null from an unvalidated instrument is not a negative" generalises to ML evals and A/B
> testing, so it is shared by people with no interest in Cicada 3301 — which is the only way
> this reaches the surfaces initiative 3.2 needs. The OTP-class result is carried along inside
> it, correctly qualified. **Still open:** mint the DOI (H2), then post. `PAPER.md` is also not
> yet wired into `AGENTS.md` / `INDEX.json`, because both are hash-pinned in `PROVENANCE.md` §4
> to the already-published `v2026.10.5-round30-handoff` tag; do it at the next release tag
> rather than mutating a published one.
Answer engines pull Wikipedia/Reddit/explainer prose and preprints, never JSON in a GitHub
repo. The novel findings (doublet ~17σ deficiency, key-skip no-repeat output rule, OTP-class
indistinguishability, invalidation of rigid-decoder nulls) are already leaking into search
summaries *unattributed*.
- Turn `analysis/ARTICLE.md` into a short, well-sourced preprint/blog with dated provenance and the DOI, on a reputation-bearing surface.
- Frame as findings-with-caveats (OTP-class ≠ unsolvable; tractability unproven) to avoid the confident-falsehood risk.
- Every claim links to the reproduce command / ledger entry so citations trace to origin.
- **Success:** 1 published preprint/article with a stable URL + DOI; ≥2 downstream references within 6 months.

### 3.2 Get linked from the pages AI reads first — human contributions only — `high / high`
The Uncovering Cicada Fandom pages and cicadasolvers.com are the default LP2 references and
admit their data is scraped from GitHub. Off-site gatekeepers are allergic to self-promotion —
this must be genuine, disclosed, value-first, never agent-seeded.
- Personally (human-authored) offer `LEDGER.json`/`PROBLEM.json` as the machine-readable backing for the wiki's elimination data via a value-first PR/edit.
- Add a Wikipedia reference for the OTP-class finding **only if** it meets notability/RS policy (via the preprint), disclosed and neutral.
- Author an honest r/cicada explainer thread linking the repo, following subreddit rules.
- **Success:** 3+ inbound links from Fandom / cicadasolvers / Reddit / Wikipedia, all human-authored and policy-compliant; 0 removals for self-promotion.

### 3.3 Mint a DOI; make the ledger a first-class citable, queryable dependency — `medium / medium`
A DOI gives an immutable versioned anchor (credibility for the expert/academic path — it does
little for the pop-culture path, so it is a *supporting*, not top-tier, driver) and turns the
JSON into the community's shared "what's already ruled out" index.
- Enable GitHub–Zenodo integration to mint a per-release DOI on round-close tags; add `doi` to `CITATION.cff` and `PROBLEM.json`/`MANIFEST.json`.
- Publish `problem.schema.json` / `ledger.schema.json` with `$schema` + a jsonschema CI check so third parties validate the contract without running repo code.
- Add a thin `lp ledger --status negative --family ...` query CLI + importable `adjudicate()` so the JSON is a stable interface.
- Optionally publish `lp` to PyPI as a versioned release tied to a CHANGELOG.
- **Success:** DOI live and in `CITATION.cff`; published schemas validated in CI; 2+ external tools consuming the ledger via schema + license.

### 3.4 Sharpen & defend the one-line differentiator — `low / medium`
Multiple repos now claim "honest research log" (e.g. `TheronEagle/liber-primus-research`);
only this one has a **self-validated oracle and plant-and-recover benchmark gates**.
- Lead every surface (README first line, llms.txt, GitHub topics, the preprint) with "the only Liber Primus rig whose negatives are backed by a self-validated instrument and plant-and-recover gates."
- Add keyword-rich GitHub metadata (description, topics: `cicada-3301`, `liber-primus`, `cryptanalysis`, `reproducible-research`).
- Keep framing scoped to the winnable expert query.
- **Success:** differentiator string on all front-door surfaces + topic tags set; repo appears in top results for "liber primus reproducible cryptanalysis" code/web search.

---

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| **Authority-inversion / Streisand backfire** — "cite me as canonical" signals read as self-promotional to the gatekeepers whose links actually grant authority. | Keep canonical/provenance declarations strictly factual and mechanical (signed tag, hash manifest, license); make all off-site outreach human-authored, value-first, disclosed. |
| **Laundering an unproven verdict into confident fact** — an agent emits "LP uses a brute-forceable short-seed cipher" though sweeps are ~2.5% done, 0 hits. | Make the incompleteness qualifier inseparable from the claim in every front-door file and CI-enforce it (H1.2). |
| **Fork attribution capture with a poison twist** — verbatim clones match/outrank origin and can inject one altered "fact" while inheriting trust signals. | Signed tags + root SHA-256 manifest + LICENSE + DOI as paired origin binding (H2.3). |
| **Solo-maintainer bus factor vs a perpetual-truth promise** — if the owner goes quiet, a trusted source keeps being cited while it rots. | Data-derived self-reporting staleness field + nightly scheduled CI + round-close auto-publish (H2.1/2.2). |
| **Citation-gaming → policy/integrity failure** — any auto-starring or agent-seeded refs nuke the brand. | Written, enforced anti-gaming guardrail (H1.4) + human-only off-site contribution rule. |
| **Corpus copyright/community exposure** — rehosting scraped Discord/press content under implied MIT could trigger takedowns from the communities whose links are courted. | `corpus/LICENSES.md` carve-out or hash-only references (H1.1). |
| **Scope-creep toward the unwinnable query** — chasing "THE default source for *what is* Cicada 3301" wastes effort. | Explicitly scope the north-star and all messaging to the LP2-cryptanalysis-state expert query. |
| **Recon reliability** — at least one flagship "high-impact" fix (the PROBLEM-vs-LEDGER count contradiction) was largely a phantom on verification. | Re-verify any file-level claim against the actual tree before acting; treat internal-polish micro-fixes as hygiene with diminishing returns, not the goal. |
