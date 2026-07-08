export const meta = {
  name: 'cicada-campaign-xiii-armada',
  description: 'Campaign XIII armada: wide never-tested running-key corpus sweep + fresh OSINT + adversarial verify on the unsolved Liber Primus pages',
  phases: [
    { title: 'Sweep', detail: '~10 thematic lanes fetch & test never-tested keytexts as running keys' },
    { title: 'OSINT', detail: '3 fresh external deep-dives (post-2021 state, AN END hash, attribution/key)' },
    { title: 'Verify', detail: 'adversarially verify any near-threshold running-key hit' },
  ],
}

const REPO = '/c/Users/dukot/projects/cicada3301/liber-primus'

const ALREADY = [
  'Mabinogion','Self-Reliance (Emerson)','The King in Yellow','The Book of the Law / Liber AL (Crowley)',
  'Agrippa','Anglo-Saxon Rune Poem','the solved LP plaintext','KJV Bible','Moby-Dick','Pride and Prejudice',
  'War and Peace','Mathers The Kabbalah Unveiled','Blake Marriage of Heaven and Hell','Gospel of Thomas',
  "Cicada's own PGP prose",
  'Tao Te Ching','Bhagavad Gita','Meditations (Marcus Aurelius)','Thus Spake Zarathustra','I Ching',
  'Beowulf','Poe The Gold-Bug','Epic of Gilgamesh','Dhammapada','Walden','Leaves of Grass',
  'Rubaiyat of Omar Khayyam','The Prophet (Gibran)','Confessions (Augustine)','The Art of War (Sun Tzu)',
]

const HOWTO = `
You are attacking the UNSOLVED Cicada 3301 Liber Primus runic pages (LP2). Prior work proved they are
one-time-pad / long-running-key class; the ONE falsifiable open avenue is an untried already-public keytext
Cicada may have expected solvers to recognize. Your job: fetch never-before-tested candidate keytexts in your
theme and run them through the project's VALIDATED running-key attack, reporting honest results.

ENVIRONMENT / EXACT COMMANDS (use the Bash tool):
- Work in the repo:  cd ${REPO}
- For each keytext, download a plain-text (UTF-8) copy to a UNIQUE file under data/keys/campaign13/
  (prefix filenames with your lane slug to avoid collisions, e.g. data/keys/campaign13/<lane>_<slug>.txt).
  Use python urllib or curl. Good sources, try in order and skip on failure (do not hang; ~45s timeout each):
    * https://www.gutenberg.org/cache/epub/<ID>/pg<ID>.txt
    * https://www.gutenberg.org/files/<ID>/<ID>-0.txt
    * sacred-texts.com plain pages, wikisource "?action=raw", or archive.org fulltext
  VERIFY each download actually contains an expected title/author word before testing (guard against wrong file).
- Run the attack (all offsets, both signs, +-Atbash, per page; ~25s each):
    PYTHONUTF8=1 python attack.py runningkey --key "data/keys/campaign13/<file>" --label <slug>
  Read its stdout: it prints "N hits over threshold -5.2" and "best score seen: X".
  INTERPRET: threshold -5.2. Real English decode ~ -4.0..-4.4. Noise floor ~ -7.4. A "break" = N hits > 0
  (best score above -5.2). Everything is expected to be null (~ -6.0..-6.4); that null IS the valuable result.
- If best score is ABOVE -5.6 (near threshold), also capture the printed best plaintext snippet so it can be verified.

RULES:
- DO NOT test any text on this already-tested list (case-insensitive, includes translations): ${ALREADY.join('; ')}.
- Pick 8-14 thematically-justified, genuinely NEVER-tested primary sources in your lane. Prefer specific
  translations/editions Cicada plausibly used. Quality of candidate choice matters.
- Be honest: report fetch failures as failures, nulls as nulls. Do not claim a break unless N hits > 0.
- Your final message is DATA (the schema), not prose to a human.
`

const LANES = [
  ['hermetica', 'Hermetica & alchemy: Corpus Hermeticum / Divine Pymander (Everard), Emerald Tablet, The Kybalion, Turba Philosophorum, Aurora Consurgens, The Chemical Wedding of Christian Rosenkreutz, Mutus Liber commentary, Splendor Solis text'],
  ['occult', 'Western occult/magick: Dee & Kelley Enochian keys/calls, Eliphas Levi Transcendental Magic, Crowley Book of Lies + Liber 777 + Book of Thoth, Francis Barrett The Magus, MacGregor Mathers Goetia, Golden Dawn rituals'],
  ['kabbalah_gnostic', 'Kabbalah & Gnostic: Sepher Yetzirah, Zohar excerpts, Pistis Sophia, Gospel of Philip, Book of Enoch (1 Enoch), Sepher ha-Bahir, The Book of Formation'],
  ['scripture', 'World scripture NOT yet tested: The Quran (Rodwell or Pickthall), the Upanishads, the Analects of Confucius, the Book of Mormon, Popol Vuh, Zend-Avesta, the Egyptian Book of the Dead (Budge, Papyrus of Ani)'],
  ['norse_runic', 'Norse/Germanic/runic: Poetic Edda (Bellows), Prose Edda (Sturluson/Brodeur), Havamal, the Kalevala, the Exeter Book Anglo-Saxon riddles, Sir Gawain and the Green Knight'],
  ['english_canon', 'English canon Cicada-adjacent: complete William Blake (Songs of Innocence & Experience, Jerusalem, Urizen), Milton Paradise Lost, complete Lewis Carroll (Alice, Through the Looking-Glass, The Hunting of the Snark), Coleridge (Kubla Khan, Ancient Mariner), Shakespeare Sonnets'],
  ['philosophy', 'Philosophy/rationalist primary texts: Plato Republic, Descartes Meditations, Spinoza Ethics, Boethius Consolation of Philosophy, Nietzsche Beyond Good and Evil, Hume Enquiry, Berkeley Principles'],
  ['math_science', 'Mathematics/number/science: Euclid Elements, Newton Principia (Motte trans.), Nicomachus Introduction to Arithmetic, Boole Laws of Thought, Poincare Science and Hypothesis, Dedekind, prime-related public texts'],
  ['cypherpunk', 'Cypherpunk / dystopian / hacker canon that is public domain or freely licensed: A Cypherpunks Manifesto (Hughes), The Crypto Anarchist Manifesto (May), The Conscience of a Hacker (Mentor), the GNU Manifesto, Kafka The Trial/Metamorphosis, Zamyatin We'],
  ['mysticism_poetry', 'Mysticism & poetry: Rumi Masnavi (Whinfield), St John of the Cross Dark Night, Meister Eckhart sermons, Tagore Gitanjali, Blavatsky The Voice of the Silence, The Cloud of Unknowing, Thomas a Kempis Imitation of Christ'],
]

const SWEEP_SCHEMA = {
  type: 'object',
  required: ['lane', 'tested', 'best_overall', 'any_break'],
  properties: {
    lane: { type: 'string' },
    tested: {
      type: 'array',
      items: {
        type: 'object',
        required: ['keytext', 'best_score', 'over_threshold'],
        properties: {
          keytext: { type: 'string' },
          source_url: { type: 'string' },
          best_score: { type: 'number', description: 'best score seen; use -99 if fetch/test failed' },
          over_threshold: { type: 'boolean' },
          note: { type: 'string' },
        },
      },
    },
    fetch_failures: { type: 'array', items: { type: 'string' } },
    best_overall: { type: 'number' },
    best_keytext: { type: 'string' },
    best_plaintext_snippet: { type: 'string' },
    any_break: { type: 'boolean' },
  },
}

const OSINT_SCHEMA = {
  type: 'object',
  required: ['angle', 'verdict', 'findings'],
  properties: {
    angle: { type: 'string' },
    findings: { type: 'array', items: { type: 'string' } },
    new_since_2021: { type: 'boolean' },
    actionable_leads: { type: 'array', items: { type: 'string' } },
    sources: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string' },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['keytext', 'is_real_english', 'reasoning'],
  properties: {
    keytext: { type: 'string' },
    is_real_english: { type: 'boolean' },
    rescored_best: { type: 'number' },
    reasoning: { type: 'string' },
  },
}

const OSINT = [
  ['post2021-state', `Establish the CURRENT (2022-2026) public state of Cicada 3301 / Liber Primus. Is LP2 still unsolved? Have any new pages been solved since 2017? Any credible key reveal, new 3301 activity, or notable community consensus/claims? Search CicadaSolvers, r/codes, GitHub, uncovering-cicada wiki, news. Report what is CONFIRMED vs rumored, with sources.`],
  ['an-end-hash', `Investigate recovery of the lost "AN END" deep-web page (512-bit hash 36367763ab73783c...c2a8b4). Has anyone found the page or a preimage? Assess Certificate-Transparency-log brute feasibility (tweqx/dwh-check tooling), Tor v2 archive recovery, and any 2022-2026 progress. Honest verdict on whether this trail is recoverable.`],
  ['attribution-key', `Fresh 2023-2026 sweep for any credible external KEY or keytext for LP2, and any new attribution evidence. Has anyone published a claimed running-key / method that reproduces even one unsolved page? Any leaked artifact? Distinguish confirmed from speculation, with sources.`],
]

log(`Campaign XIII armada: ${LANES.length} sweep lanes + ${OSINT.length} OSINT angles`)
const sweepThunks = LANES.map(([slug, desc]) => () =>
  agent(`${HOWTO}\n\nYOUR LANE (${slug}): ${desc}`,
    { label: `sweep:${slug}`, phase: 'Sweep', schema: SWEEP_SCHEMA, model: 'sonnet', effort: 'low' }))
const osintThunks = OSINT.map(([slug, desc]) => () =>
  agent(`Deep-research OSINT for the Cicada 3301 project. Use WebSearch/WebFetch. Angle "${slug}": ${desc}\n`
    + `Be rigorous and skeptical; adversarially check claims before reporting them as confirmed. `
    + `Your final message is DATA (the schema), not prose.`,
    { label: `osint:${slug}`, phase: 'OSINT', schema: OSINT_SCHEMA }))

const all = await parallel([...sweepThunks, ...osintThunks])
const sweep = all.slice(0, LANES.length).filter(Boolean)
const osint = all.slice(LANES.length).filter(Boolean)

phase('Verify')
const suspects = sweep.filter(s => s && (s.any_break || (typeof s.best_overall === 'number' && s.best_overall > -5.6)))
let verified = []
if (suspects.length) {
  log(`${suspects.length} lane(s) near/over threshold -> adversarial verify`)
  verified = (await parallel(suspects.map(s => () =>
    agent(`A running-key sweep on the unsolved Cicada LP2 pages reported a possibly-promising result:\n`
      + `lane=${s.lane} keytext=${s.best_keytext} best_score=${s.best_overall}\n`
      + `plaintext snippet: ${s.best_plaintext_snippet || '(none captured)'}\n\n`
      + `Adversarially verify. Default to is_real_english=FALSE unless the decode is clearly readable English. `
      + `A score near -5.2 with gibberish text is a NULL, not a break. If you can, re-run in ${REPO}: `
      + `PYTHONUTF8=1 python attack.py runningkey --key "<the key file in data/keys/campaign13/>" --label recheck, `
      + `and inspect the actual plaintext. Report honestly.`,
      { label: `verify:${s.lane}`, phase: 'Verify', schema: VERIFY_SCHEMA })
  ))).filter(Boolean)
} else {
  log('no lane scored near threshold -> clean null, no verification needed')
}

const tested = sweep.reduce((n, s) => n + (s.tested ? s.tested.length : 0), 0)
const breaks = sweep.filter(s => s && s.any_break).length
const confirmedBreaks = verified.filter(v => v && v.is_real_english)
const bestScore = Math.max(...sweep.map(s => (typeof s.best_overall === 'number' ? s.best_overall : -99)))

return {
  summary: { lanes: sweep.length, osint_angles: osint.length, keytexts_tested: tested,
    lanes_reporting_break: breaks, confirmed_real_english_breaks: confirmedBreaks.length,
    best_score_across_corpus: bestScore },
  sweep, osint, verified,
}
