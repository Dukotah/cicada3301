export const meta = {
  name: 'cicada-campaign-xiv-redteam',
  description: 'Campaign XIV: Fable 5 red-team of the whole Liber Primus approach (4 lenses) + ingest/analyze the expanded ~75-page corpus',
  phases: [
    { title: 'Red-team', detail: 'Fable 5 panel red-teams the approach for new sound attacks & flawed assumptions', model: 'claude-fable-5' },
    { title: 'Corpus', detail: 'fetch current community transcription, diff vs our 0-55 set, ingest + stat the new pages' },
  ],
}

const REPO = '/c/Users/dukot/projects/cicada3301'
const LP = `${REPO}/liber-primus`

const GROUND = `
You are red-teaming a mature, honest cryptanalysis project on the UNSOLVED Cicada 3301 Liber Primus runic
pages (LP2, pages 0-55). The project's own conclusion is: from the ciphertext alone these pages are
one-time-pad / long-running-key class (IoC.N = 1.000 perfectly flat; doublet rate 0.66% vs 3.45% random =
a deliberate ~83% soft no-adjacent-repeat filter), hence information-theoretically unsolvable without an
external key. It has exhaustively eliminated: all periodic keys (len 1-40), ~112 running-key texts, all
number-theoretic/PRNG keystreams, plaintext & ciphertext autokey (simulated & excluded), first-difference/
integral inversion, page-on-page keying, fractionation (bifid), substitution/homophonic, transposition-only,
Hill 2x2/3x3, crib-dragging, image stego (real OutGuess built), and the pp49-51 base-60 payload (2048-bit
high-entropy blob: not prime/RSA/key/text/format/hash-preimage/repeating-XOR/image). Transcription verified
3 ways. No public external key ever existed; AN END deep-web hash is cold.

READ THESE FILES FIRST (use Read/Grep; repo root ${REPO}):
- ${LP}/ELIMINATION-LEDGER.md   (the master list of everything tried + why -- READ FULLY)
- ${LP}/FINDINGS-FOR-SOLVERS.md
- ${LP}/analysis/CAMPAIGN-X-FINDINGS.md , CAMPAIGN-XI-FINDINGS.md , CAMPAIGN-XII-FINDINGS.md , CAMPAIGN-XIII-FINDINGS.md
- skim ${LP}/attack.py (the validated attack CLI) and ${LP}/src/lp/ (the rig)

YOUR JOB: bring genuinely FRESH thinking. Do NOT propose anything already in the ELIMINATION-LEDGER (that is
re-running dead ends). Every attack you propose MUST (a) be consistent with flat IoC 1.000 AND the 0.66%
doublet deficit, (b) have a concrete, FALSIFIABLE test signal, and (c) say honestly what its prior is. Be
skeptical of the project's own conclusions too -- if an assumption is load-bearing and possibly wrong, say so.
Your final message is DATA (the schema), not prose.
`

const LENSES = [
  ['assumptions', `Attack the ASSUMPTIONS. Is the "one-time-pad / unsolvable" conclusion actually sound, or overstated? What unstated or load-bearing assumption, if false, would REOPEN the whole problem? (e.g. rune inventory / Gematria Primus mapping, page/segmentation boundaries, the interrupter model, treating pages independently, the letter->index encoding, the assumption the key is textual vs generated.) Rank by how much each would change things if wrong.`],
  ['cryptanalysis', `Propose NOVEL sound cryptanalysis not yet tried that FITS flat-IoC + doublet-deficit. Think: constructions that PRODUCE a flat IoC and suppress doublets by design but are NOT a pure external OTP -- e.g. specific self-keying/running-key schedules, key-autokey hybrids with the doublet filter, fractionation+transposition combinations the bifid test didn't cover, polygraphic schemes, a generated keystream with a recoverable seed the project didn't try, or a doublet-avoidant encoding layer sitting ON TOP of a breakable inner cipher. For each: the exact falsifiable signal that would confirm/deny it.`],
  ['structure_meta', `Look BEYOND ciphertext-only attacks. What structural / cross-page / non-crypto avenue is underexplored? Consider: the role of the pp49-51 2048-bit payload as something OTHER than a key (index? seed? checksum? per-page offsets?), interrupter (F-rune) positions as a hidden channel, cross-page relationships, page ORDER/permutation, the possibility that the "key" is a PROCEDURE (e.g. reader-supplied from solved pages) rather than a text, or that meaning is positional. Concrete falsifiable tests only.`],
  ['prioritize', `Given everything already eliminated, name the SINGLE highest-expected-value experiment that is still genuinely untried and sound, and defend why. Separately: state precisely what observation WOULD falsify the "built-to-be-unsolvable / externally-keyed" framing (what would we have to see to know we're wrong?). Also flag anything the project may be OVER-claiming as "closed" that is actually only partially tested.`],
]

const REDTEAM_SCHEMA = {
  type: 'object',
  required: ['lens', 'proposals', 'flawed_assumptions', 'highest_ev_experiment', 'verdict_on_unsolvable'],
  properties: {
    lens: { type: 'string' },
    proposals: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'fits_constraints', 'how_to_test', 'falsifiable_signal', 'prior'],
        properties: {
          name: { type: 'string' },
          rationale: { type: 'string' },
          fits_constraints: { type: 'string', description: 'how it is consistent with flat IoC 1.0 AND the 0.66% doublet deficit' },
          how_to_test: { type: 'string' },
          falsifiable_signal: { type: 'string' },
          already_covered_check: { type: 'string', description: 'why this is NOT already in the elimination ledger' },
          prior: { type: 'string', enum: ['very-low', 'low', 'medium', 'high'] },
          cheap_to_run: { type: 'boolean' },
        },
      },
    },
    flawed_assumptions: {
      type: 'array',
      items: { type: 'object', required: ['assumption', 'why_might_be_wrong', 'consequence_if_wrong'],
        properties: { assumption: { type: 'string' }, why_might_be_wrong: { type: 'string' }, consequence_if_wrong: { type: 'string' } } },
    },
    overclaimed_as_closed: { type: 'array', items: { type: 'string' } },
    highest_ev_experiment: { type: 'string' },
    verdict_on_unsolvable: { type: 'string', description: 'agree / overstated / understated, with reasoning' },
  },
}

const CORPUS_SCHEMA = {
  type: 'object',
  required: ['current_page_count', 'our_page_count', 'new_pages', 'same_class', 'summary'],
  properties: {
    current_page_count: { type: 'number' },
    our_page_count: { type: 'number' },
    new_pages: { type: 'array', items: { type: 'string' } },
    ingested_ok: { type: 'boolean' },
    stats_on_new: { type: 'string', description: 'IoC.N, doublet rate, entropy on the newly-found pages' },
    same_class: { type: 'boolean', description: 'are the new pages the same flat-IoC OTP class?' },
    sources: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
}

log('Campaign XIV: Fable 5 red-team (4 lenses) + expanded-corpus ingest')

const redteamThunks = LENSES.map(([slug, task]) => () =>
  agent(`${GROUND}\n\nYOUR LENS (${slug}): ${task}`,
    { label: `redteam:${slug}`, phase: 'Red-team', schema: REDTEAM_SCHEMA, model: 'fable', effort: 'high' }))

const corpusThunk = () =>
  agent(
    `Cicada 3301 Liber Primus corpus task. Campaign XIII OSINT found the community runic transcription grew to `
    + `~75 pages by late 2024 (Tumbleson), while THIS project only ever ingested pages 0-55. Close that gap.\n\n`
    + `Steps (use Bash + WebFetch in ${LP}):\n`
    + `1. Our canonical runes: ${LP}/data/krisyotam_runes.txt and ${LP}/data/relikd/ (0-55). Establish our exact page count.\n`
    + `2. Find the CURRENT most-complete machine-readable transcription (try rtkd/iddqd github master, krisyotam/cicada3301, `
    + `cicada-solvers, relikd/LiberPrayground). Determine the current total page count and WHICH page indices we lack.\n`
    + `3. Download the additional transcribed pages (runes) into ${LP}/data/campaign14/ (create it). Verify they are `
    + `Gematria Primus runes, not garbage.\n`
    + `4. Run the project's stats on the NEW pages: reuse ${LP}/analysis/run_stats.py / lp.stats (PYTHONUTF8=1 python). `
    + `Report IoC.N, doublet rate, entropy for the new pages and whether they match the flat-IoC OTP class of 0-55.\n`
    + `Be honest if the "~75 pages" figure is really unsolved LP2 vs includes already-solved or LP1 pages. Final message is DATA.`,
    { label: 'corpus:ingest', phase: 'Corpus', schema: CORPUS_SCHEMA, effort: 'high' })

const all = await parallel([...redteamThunks, corpusThunk])
const redteam = all.slice(0, LENSES.length).filter(Boolean)
const corpus = all[LENSES.length] || null

// surface the cheap, not-already-covered proposals for the main loop to execute
const actionable = []
for (const r of redteam) {
  for (const p of (r.proposals || [])) {
    actionable.push({ lens: r.lens, name: p.name, prior: p.prior, cheap: !!p.cheap_to_run,
      test: p.how_to_test, signal: p.falsifiable_signal, fits: p.fits_constraints })
  }
}
actionable.sort((a, b) => (b.cheap - a.cheap) || (({high:3,medium:2,low:1,'very-low':0}[b.prior]||0) - ({high:3,medium:2,low:1,'very-low':0}[a.prior]||0)))

return {
  summary: { lenses: redteam.length, total_proposals: actionable.length,
    cheap_proposals: actionable.filter(a => a.cheap).length,
    corpus_new_pages: corpus ? (corpus.new_pages || []).length : 'n/a',
    corpus_same_class: corpus ? corpus.same_class : 'n/a' },
  redteam, corpus, actionable,
}
