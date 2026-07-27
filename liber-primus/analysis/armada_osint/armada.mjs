export const meta = {
  name: 'armada-osint-onion',
  description: 'Armada: acquire + forensically extract the overlooked Cicada onion/image artifacts, key-test any recovered payload against the LP2 runes, adversarially verify, synthesize.',
  phases: [
    { title: 'Acquire+Extract', detail: 'one agent per overlooked artifact: download + full forensic battery (OutGuess/steghide/entropy/carve)' },
    { title: 'Keytest', detail: 'any recovered high-entropy payload -> key-test vs the runes using the verified harness' },
    { title: 'Verify', detail: 'adversarial skeptic on any claimed hit (signal vs variance vs English baseline)' },
    { title: 'Synthesize', detail: 'rank findings; completeness critic' },
  ],
}

const REPO = '/mnt/c/Users/dukot/projects/cicada3301/liber-primus'
const WORK = REPO + '/analysis/armada_osint'
const OG = '/tmp/outguess'
const KEYS = WORK + '/keys.txt'

const SHARED = `
ENVIRONMENT (all confirmed working this session):
- Working repo: ${REPO}   (the Liber Primus cryptanalysis rig)
- Scratch dir (create subfolders freely): ${WORK}/artifacts and ${WORK}/extracts
- OutGuess binary: ${OG}  (built + on disk; usage: '${OG} -r -k <key> <in.jpg> <out.bin>' to extract; omit -k for no-key). OutGuess 0.2 is the exact tool Cicada used.
- steghide: /usr/bin/steghide  (steghide extract -sf <img> -p <pass> -xf <out>)
- Python3 with PIL + numpy available. Existing pure-python stego harness: ${REPO}/analysis/stego/stego_scan.py (markers/entropy/EOI-trailing/carve/strings) -- you may run or copy its approach.
- Network via curl WORKS: github raw (raw.githubusercontent.com) and archive.org range/download both return real bytes. WebFetch/WebSearch (via ToolSearch) work for locating things but CANNOT download binaries -- use curl for binaries.
- Key/password candidate list for OutGuess/steghide: ${KEYS} (magic-square words, LP phrases, gematria numbers, 3301-candidates).
RULES:
- Do the actual downloads and actually run the tools. Report real bytes/hashes, never invent.
- A REAL OutGuess/steghide payload is LOW-entropy / printable / has structure / a magic header. Random-looking high-entropy output from a wrong key = NO payload (that is the tool's normal failure mode). Distinguish clearly.
- If you extract a genuine high-entropy BINARY blob that is NOT obviously an image/text (candidate key/pad/ciphertext material), save it to ${WORK}/extracts/<id>.bin and set payloadFound=true with its absolute path.
- Keep downloads under ~10MB each; use curl -sL with a 60s timeout.
`

const ACQUIRE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['id', 'acquired', 'payloadFound', 'payloadPath', 'verdict', 'summary'],
  properties: {
    id: { type: 'string' },
    acquired: { type: 'boolean', description: 'did you successfully download the target artifact(s)?' },
    sourceUrl: { type: 'string', description: 'the exact URL you downloaded from' },
    sha256: { type: 'string' },
    sizeBytes: { type: 'number' },
    payloadFound: { type: 'boolean', description: 'true only if a genuine hidden payload (low-entropy/structured/magic-header, or a high-entropy blob that is candidate key material) was extracted' },
    payloadPath: { type: 'string', description: 'absolute path to the saved candidate payload under extracts/, or empty string' },
    payloadEntropy: { type: 'number', description: 'bits/byte of the extracted payload, or 0' },
    payloadDesc: { type: 'string', description: 'what the payload looks like: format, first bytes, printable %' },
    verdict: { type: 'string', enum: ['new-data', 'image-chain', 'null', 'unresolved', 'not-found'], description: 'new-data=genuinely novel hidden content; image-chain=just more puzzle images; null=nothing hidden; unresolved=evidence of data but could not extract; not-found=could not locate/download' },
    summary: { type: 'string', description: '3-6 sentences: what you fetched, what you ran, what you found' },
  },
}

const KEYTEST_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['id', 'ran', 'hit', 'bestScore', 'summary'],
  properties: {
    id: { type: 'string' },
    ran: { type: 'boolean' },
    hit: { type: 'boolean', description: 'true only if a config scored clearly above the English baseline (-4.0) with readable output' },
    bestScore: { type: 'number' },
    bestConfig: { type: 'string' },
    summary: { type: 'string' },
  },
}

const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['id', 'confirmed', 'summary'],
  properties: {
    id: { type: 'string' },
    confirmed: { type: 'boolean', description: 'true if the claimed hit survives skeptical scrutiny (real signal, not short-page variance or cherry-picking)' },
    summary: { type: 'string' },
  },
}

const TARGETS = [
  {
    id: 'T1-onion3-5x5-rune-outguess',
    label: 'T1:5x5-rune-pw-outguess',
    brief: `FLAGSHIP LEAD. Locate and download the "5x5 runes / magic square" JPG image from the 2014 Cicada 3301 puzzle (~328 KB). Community reports it shows VISIBLE RGB modification in the runes under high contrast = a SUSPECTED password-protected OutGuess container whose key was never found. Find the exact image via: scream314/cicada3301 (raw.githubusercontent.com/scream314/cicada3301/master/2014.md links its assets), cicada-solvers/The-Complete-Cicada3301-Archive/2014, iBotPeaches/cicada_3301, or archive.org onion dumps (ut3qtzbrvs7dtvzp.onion served the magic-square stage; q4utgdi2n4m4uim5.onion served a Goya image). Download the candidate JPG(s). THEN: (1) run the python stego harness for markers/entropy/EOI-trailing/carve. (2) Systematically try OutGuess extraction with EVERY key in ${KEYS}: for k in $(cat ${KEYS}); do ${OG} -r -k "$k" img.jpg out_$k.bin 2>/dev/null; done, plus a no-key run. A wrong key yields tiny/garbage output; a RIGHT key yields structured/printable/larger output -- flag any such. (3) Same sweep with steghide -p <pass>. (4) Also enhance-contrast the runes with PIL to confirm/deny the visible-modification claim. Report the strongest candidate payload if any.`,
  },
  {
    id: 'T2-2jpg-seed38370-blob',
    label: 'T2:2.jpg-7524-blob',
    brief: `Locate and download the Cicada image known as "2.jpg" from which the community extracted an OutGuess payload with seed 38370 = a 7,524-byte blob WITH NO MAGIC HEADER (never identified). It is a Liber Primus-round / 2014 image. Find it via scream314 2014.md assets, The-Complete-Cicada3301-Archive, iddqd (github cicada-solvers/iddqd lp_outguessed), or archive.org. Download it. Extract with ${OG} -r 2.jpg out.bin (no key first; then try keys from ${KEYS}). If you recover a ~7524-byte blob: characterize it fully -- entropy (bits/byte), byte histogram, printable %, first 32 bytes hex, and try transforms: 0xFF bit-flip, gzip/bzip2/zlib inflate, reverse, base64-decode, RSA-OAEP shape. If it is a high-entropy binary that is NOT an image/text, SAVE it to ${WORK}/extracts/T2.bin and set payloadFound=true (it becomes a keytest candidate against the runes).`,
  },
  {
    id: 'T3-iso-folly-wisdom',
    label: 'T3:folly+wisdom',
    brief: `Locate and download the two /tmp files "folly" and "wisdom" from the 2013 Cicada 3301 Linux ISO -- community says they have identical content and were never decoded (a documented pointer is infotomb.com/bjzdi). Try: infotomb, scream314 2013.md, The-Complete-Cicada3301-Archive/2013, or extract from the ISO on archive.org (search details for '3301' iso / 'a2e7j6ic78h0j7eiejd0120'). Download both files (or the pair). Decode attempts: xxd/first bytes, strings, confirm whether the two are byte-identical (sha256 both), then base64-decode, xor-with-self/xor-pairs, gzip/bzip2, gematria-map, and check for onion addresses or key-looking material. Report exactly what they contain and whether anything is recoverable. If a structured payload emerges, save to ${WORK}/extracts/T3.bin.`,
  },
  {
    id: 'T4-htaccess-hex-blobs',
    label: 'T4:.htaccess-hexblobs',
    brief: `VERIFY-OR-DENY lead. Download the two large ".htaccess" hex blobs that most mirrors skip (hidden under the dotfile name): curl -sL 'https://archive.org/download/avowyfgl5lkzfj3n.onion/.htaccess' (~5,064,619 B) and 'https://archive.org/download/fv7lyucmeozzd5j4.onion/.htaccess' (~5,577,967 B); also cu343l33nqaekrnw.onion/761.hex (~3.6 MB) if reachable. These are the raw growing-hex onion payloads. For each: strip whitespace, hex-decode to bytes, then carve for embedded files (JPEG ffd8/gzip 1f8b/PNG). The EXPECTED answer is they decode to gzip'd or bit-flipped embedded JPEGs (just more puzzle images). Your job: CONFIRM that, OR flag any non-image / unexpected data (trailing bytes after the last image, appended key material, the '57'/0x3537 addendum). If you find non-image bytes that look like key/pad material, save to ${WORK}/extracts/T4.bin and set payloadFound=true; otherwise verdict=image-chain.`,
  },
  {
    id: 'T5-4gq25-2016',
    label: 'T5:4gq25.jpg-2016',
    brief: `Locate and download "4gq25.jpg" (surfaced 5 Jan 2016, authenticity DISPUTED, but an OutGuess payload was reportedly preserved). Search scream314, The-Complete-Cicada3301-Archive/2016, fandom/reddit mirrors, archive.org. If found: extract with ${OG} -r (no key, then keys from ${KEYS}) and steghide. Characterize any payload. Note the authenticity dispute in your summary. If not locatable, verdict=not-found with where you looked.`,
  },
  {
    id: 'T6-pgp-whitespace-audit',
    label: 'T6:pgp-whitespace',
    brief: `The community wiki flags the PGP trailing-whitespace channel as "never fully utilized." Fetch the RAW Cicada signed messages (which preserve trailing spaces/tabs -- our local copies may have stripped them) from scream314/cicada3301 and/or cicada-solvers mirrors (messages by year). For EVERY signed message: extract the trailing-whitespace pattern per line (count of spaces/tabs after the last non-space char, and space-vs-tab as a binary channel). Decode candidates: as binary bits, as prime sequences (known instances: 2013 '5,3,2,2,3,5'; 2014 '2,3,5,7..37' = OEIS A194954), as gematria indices. Compare against those KNOWN catalogued sequences and flag ANY message whose whitespace payload is NOT already accounted for (an un-catalogued channel is the win). Report per-message findings and any new sequence. Save any recovered numeric stream to ${WORK}/extracts/T6.txt.`,
  },
  {
    id: 'T7-http-header-channel',
    label: 'T7:onion-header-channel',
    brief: `ANALYSIS-ONLY (no binary download). Pull the archived onion HTTP artifacts from iBotPeaches/cicada_3301 /onions/ (pre/ and post/ folders per address) via raw.githubusercontent.com, and any documented server-status/header captures. The community noted unexplained per-onion anomalies: distinct ports 5240/5241/5242/5243 across auqg/cu343/fv7ly/avowy; a mock server-status uptime "1 days 0 hours 33 minutes 14 seconds" -> 1033; a leaked host li676-224.members.linode.com / 106.186.123.224 / port 5243; and <head>/</head> tag malformations varying per onion. Collect these values in onion ORDER and test whether they form an intentional ordered sequence (ports as a base offset, uptimes/timestamps as numbers, head-tag presence as a bitstring) encoding anything -- indices into the runes, an onion char, a number. This is a long-shot structural check; report what the ordered values are and whether any decode is non-coincidental.`,
  },
]

phase('Acquire+Extract')
log(`Armada launching ${TARGETS.length} artifact fronts against the overlooked Cicada onion/image leads.`)

const results = await pipeline(
  TARGETS,
  // STAGE 1: acquire + forensic battery
  (t) => agent(SHARED + '\n\nYOUR TARGET:\n' + t.brief + `\n\nReturn structured output with id="${t.id}".`,
    { label: t.label, phase: 'Acquire+Extract', schema: ACQUIRE_SCHEMA }),
  // STAGE 2: if a candidate payload was saved, key-test it vs the runes
  (acq, t) => {
    if (!acq || !acq.payloadFound || !acq.payloadPath) return acq ? { ...acq, keytest: { id: t.id, ran: false, hit: false, bestScore: 0, summary: 'no payload to key-test' } } : null
    return agent(SHARED + `\n\nKEY-TEST TASK for ${t.id}. A candidate payload was extracted at: ${acq.payloadPath} (${acq.payloadDesc}). ` +
      `Test it as KEY/PAD/CIPHERTEXT material against the LP2 runes using the VERIFIED existing harness. Study ${REPO}/analysis/pp49_51/keytest.py and ${REPO}/analysis/pp49_51/completeness_keys.py -- reuse the SAME imports (from lp import gematria, ciphers, score; from run_stats import load_pages), the SAME calibrated scorer (score_norm: ~-2.2 English, -4.0 baseline, <-5.2 = noise floor threshold). ` +
      `Write a small script under ${WORK} that loads the payload bytes and tries: bytes mod 29 as additive / Beaufort / atbash key, both signs, forward + reversed, per-page offset sweep on the SHORT pages AND whole-corpus, and XOR-class where sensible. Report the best score and whether ANY config beats the -4.0 English baseline with readable plaintext. Be honest: top hits on short pages are usually variance, not signal.` +
      `\n\nReturn structured output with id="${t.id}".`,
      { label: 'keytest:' + t.id, phase: 'Keytest', schema: KEYTEST_SCHEMA })
      .then((kt) => ({ ...acq, keytest: kt }))
  }
)

// STAGE 3: adversarially verify any claimed keytest hit
phase('Verify')
const hits = results.filter(Boolean).filter((r) => r.keytest && r.keytest.hit)
let verified = []
if (hits.length) {
  log(`${hits.length} claimed keytest hit(s) -> adversarial verify.`)
  verified = await parallel(hits.map((r) => () =>
    agent(SHARED + `\n\nADVERSARIAL VERIFY. A prior agent claims a keytest HIT for ${r.id}: bestScore=${r.keytest.bestScore}, config="${r.keytest.bestConfig}". ` +
      `Your job is to REFUTE it. Re-run the exact config, and check: is the score genuinely above the -4.0 English baseline on a LONG page (not just a short/variance-prone page)? Is the "plaintext" actually readable English/Latin or cherry-picked fragments? Does a random control key score similarly? Default to confirmed=false unless the signal is unambiguous and reproducible. ` +
      `Return structured output with id="${r.id}".`,
      { label: 'verify:' + r.id, phase: 'Verify', schema: VERIFY_SCHEMA })))
  verified = verified.filter(Boolean)
} else {
  log('No keytest hits to verify (expected -- runes are OTP-class; value is in newly-recovered data, not a solve).')
}

// STAGE 4: synthesize + completeness critic
phase('Synthesize')
const dossier = JSON.stringify({ results: results.filter(Boolean), verified }, null, 1)
const report = await agent(
  `You are the armada synthesizer for a Cicada 3301 OSINT forensic sweep. Below is the structured output from ${TARGETS.length} artifact fronts (+ any keytest/verify). ` +
  `Write a RANKED markdown report for the project owner. For each target: what was actually fetched (url/sha/size), what forensic tools were run, and the verdict (new-data / image-chain / null / unresolved / not-found). ` +
  `Lead with the single most important outcome. Clearly separate GENUINELY NEW recovered data from confirmed-just-image-chain and from not-founds. Note any target that found EVIDENCE of hidden data but could not extract it (that is the highest-value residue). ` +
  `End with a COMPLETENESS-CRITIC section: what artifact/method did this sweep NOT cover, and what is the single best next move. Be rigorously honest -- do not overstate; a clean null across all fronts is the likely and acceptable result given the OTP verdict, and should be stated plainly.\n\nDOSSIER:\n${dossier}`,
  { label: 'synthesize', phase: 'Synthesize' })

return { report, results: results.filter(Boolean), verified }
