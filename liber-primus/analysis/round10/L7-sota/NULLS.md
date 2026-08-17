# L7-sota — NULLS

Every item the sweep surfaced and dismissed, with the dismissal reason, so nobody re-checks it.
Dismissals follow the NULL list fixed in `PREREG.md` before any query was issued.

| # | Item | Date | Dismissal reason (one line) |
|---|---|---|---|
| N01 | **Thomas Schoenberger** self-attribution as Cicada 3301 creator, via his own filings (MI Court of Claims 26-000013-MZ; *Schoenberger & Cicada 3301 Metaverse LLC v. Trustees of MSU et al.*) | 2025-09 → 2026 | Pre-registered NULL. Unsigned, self-asserted, contested and actively litigated. A pleading is not a 7A35090F signature. Do not launder. |
| N02 | **Zenodo 18199474** — "Final and Complete Translation of the Liber Primus (IA Gemini with Keys)", Bruno Becker, v2 | 2026 | Pre-registered NULL (OFELLIA class). Filenames `ΩFFΣLLIα_Ŧ€ŞLŁΔ_TOTAL.py`, `deep_mind_learnings.jsonl` = LLM output; no statistics on the unsolved pages; no community body reports reproducing it. Already known to the repo. |
| N03 | **arXiv 2607.18538 — CryptanalysisBench** (Fluri, Shafran, Carlini, Jagielski, Nasr, Dunkelman, Ronen, Tramèr), submitted 2026-07-20, rev. 2026-07-29 | 2026-07 | Real, current, high-calibre — and irrelevant. 191 tasks over NIST-competition primitives (block ciphers, hashes; e.g. SpoC, KINDI). Zero mention of Cicada 3301, Liber Primus, or any unsolved historical cipher. |
| N04 | **blankline.org/research/primus** — "Primus", an LLM reasoning system | 2026-04-05 | Name collision only. FRB drift-rates and a combinatorics proof. No Cicada content. |
| N05 | **esovitae.com**, thespearheadmagazine, nahgcorp/stationoneohone Substacks, Medium "Liber Primus, the Puzzle that Baffled the Internet" | various | Journalism/SEO tier. The esovitae page is the source of the floating phrase "what appear to be one-time-pad fragments" — it cites nothing and concedes "no community-wide consensus exists". See H2 in FINDINGS; this is *not* independent OTP prior art. |
| N06 | **Kowatsch, *The Complete Liber Primus*** (2018 paperback, ISBN 9781987441260) | 2018 | Reprint of the imagery, not analysis. Predates everything. Already known. |
| N07 | **"Liber Primus page 42 solved August 2026"** | — | NC1 decoy. Returned only the standard background pages plus explicit "no such thing found". Channel is not hallucinating positives. |
| N08 | **"Cicada 3301 new signed message August 2026"** | — | NC1 decoy. Same: returned the 2017-04-04 last-known-message fact and the SHA-1 forgeability caveat. Clean. |
| N09 | **"one-time pad proof published peer reviewed 2026"** | — | NC1 decoy. Returned generic OTP textbook material and Kowatsch's book. Clean. |
| N10 | **mortlach/RuneDecrypterPrime** and the rest of the mortlach corpus | 2026-08-11 | Not a null on merit — genuinely the deepest active single-person body — but **already censused by sibling lane `round10b/PA-1`**, which is more thorough than anything I would re-derive. Not re-claimed here. |
| N11 | **NoxxGames/LiberPrimus-GPU**, cmbsolver, neuroretransmit/liberprimus-tool (GA), RuneSwiss, hugvig, etc. | 2024–2026 | Same: covered by `round10b/PA-1` §2c. Per PREREG, ports/rewrites/faster-search are explicit NULLs for H1d; the GPU repo's own README says the broad unsolved-page campaigns are "not started". |
| N12 | **Tumbleson, "AI & Cicada 3301"** | 2024-01-29 | Already in the repo's record. GPT-4 did magic-square ID, rune lookup and OCR; "No specific cipher decryption methods were tested". Not an LLM cryptanalytic assault. |
| N13 | **uncovering-cicada fandom wiki** frequency/doublet pages | last touched 2026-03-18 | Not a null on merit — it is the H1c evidence — but it **corroborates** rather than contradicts (see FINDINGS §3). Direct fetch now blocked (HTTP 402 on both normal and `?action=raw`); numbers taken from search snippets + PA-1's earlier successful fetch. |
| N14 | **cicada-solvers org, all repos other than aldegonde** | ≤2026-07-22 | Nothing in the org has moved since 2026-07-22 except aldegonde (2026-08-10). No new artifact in the 2026-08-12 → 2026-08-17 window. |

## Standing note on the signature gate

Both the sweep and the repo's own `FRESHNESS-2026-07-29` land in the same place: the last
verified 3301 message is **2017-04-04**, and because every genuine 3301 signature used a
**SHA-1** digest, the SHAttered chosen-prefix result means a valid-looking 7A35090F signature
is now *necessary but not sufficient*. The independent statement of this is Katayama,
*On the Forgery of Cicada 3301 PGP Signatures via SHA-1 Collision Attacks* (ResearchGate
403192960), re-found by this sweep via query S02 (NC2 recall item).
