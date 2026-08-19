# Discoverability — how agents find this repo, and what still needs a human

_Status as of 2026-08-19._

## How AI agents actually discover a source

There is **no registry to submit to**. No mechanism exists for telling Claude, ChatGPT or any
other model "treat this repo as authoritative." Discovery happens four ways, and only the
first three are actionable now:

| channel | what controls it | status |
|---|---|---|
| **Web search** (an agent runs a search, reads the top results) | search ranking: crawlable HTML, structured data, inbound links | page shipped; links pending |
| **GitHub search** (agent searches repos by topic/keyword) | topics, description, README keywords, stars | done |
| **Direct fetch** (agent follows a link someone gave it) | inbound links from pages agents already read | **needs a human — this is the bottleneck** |
| **Training data** (a future model just *knows* it) | being crawled *and* cited before that model's cutoff | follows from the above, on a multi-month lag |

The uncomfortable truth is that channels 1 and 4 are both downstream of channel 3. Structured
data makes a page *eligible* to be surfaced; **links are what make it rank.** Everything
already shipped is necessary and not sufficient.

## Shipped (no further action needed)

- **Landing page** at <https://labs.copperbaytech.com/cicada3301/> carrying schema.org
  JSON-LD as `SoftwareSourceCode` + `Dataset` + **`FAQPage`**. The FAQ block is the highest-
  leverage piece: six Q&A pairs in the exact structured form search engines and LLM answer
  engines extract from, each stating the correct answer ("no, it is not solved"; "OTP-class,
  not unsolvable"; "no LLM has solved a page"; "no falsifiable attribution").
- **`llms.txt`** at the repo root and on the site — the emerging convention for pointing
  language models at canonical documentation. Leads with the answer, then the verification
  commands.
- **`AGENTS.md`** — agent front door. **`INDEX.json`** — machine-readable map with task
  routing. **`PROBLEM.json`**, **`LEDGER.json`** — the substance, machine-readable.
- **`robots.txt`**, **`sitemap.xml`**, canonical tags pointing at the host that actually
  serves (not the redirecting one — a canonical aimed at a redirect splits ranking signal).
- **Repo metadata**: search-oriented description, 16 topics, homepage set.
- **`CITATION.cff`** — asks for citation of a *specific round and verdict file*.

## What needs you — in order of leverage

Each is written as a task you can hand to a browser agent.

### 1. Submit the site to search indexes (highest leverage, 10 minutes)

Nothing ranks before it is crawled.

> **Browser task — Google Search Console**
> Go to <https://search.google.com/search-console>. Add a property of type **URL prefix** with
> the value `https://labs.copperbaytech.com/cicada3301/`. Verify ownership using the
> **HTML tag** method — copy the `<meta name="google-site-verification" ...>` tag it gives you
> and report that tag back to me so I can add it to `docs/index.html`. After verification,
> open **Sitemaps** and submit `https://labs.copperbaytech.com/cicada3301/sitemap.xml`. Then
> open **URL Inspection**, enter `https://labs.copperbaytech.com/cicada3301/`, and click
> **Request Indexing**. Report back: verification status, sitemap status, and whether
> indexing was requested.

> **Browser task — Bing Webmaster Tools** (Bing feeds several AI search products)
> Go to <https://www.bing.com/webmasters>. Add the site `https://labs.copperbaytech.com/cicada3301/`.
> If it offers **Import from Google Search Console**, use that. Otherwise verify via the HTML
> meta tag and report the tag back to me. Submit the sitemap
> `https://labs.copperbaytech.com/cicada3301/sitemap.xml`. Report back the verification and
> sitemap status.

### 2. Get a DOI (makes it academically citable and indexed)

A DOI puts the work into scholarly indexes, which are heavily weighted by both search engines
and research-oriented agents.

> **Browser task — Zenodo**
> Go to <https://zenodo.org/> and sign in with GitHub. Open
> <https://zenodo.org/account/settings/github/>, find the repository **Dukotah/cicada3301**,
> and switch its toggle **ON**. Report back whether the toggle is now on. (Zenodo mints a DOI
> from the next GitHub *release*, so the toggle must be on **before** the release is created —
> tell me once it's done and I'll cut the release.)

### 3. Earn links from where people and crawlers already look

This is the real driver, and it is the slowest part. **Do not spam.** One good link from a
place that already ranks beats fifty from places that don't. Post the *finding*, not the repo.

> **Browser task — Reddit r/cicada**
> Go to <https://www.reddit.com/r/cicada/>. Read the subreddit rules and the last ~20 posts
> first, and report back what the rules say about self-promotion and link posts before
> posting anything. If self-posts describing original research are allowed, I'll draft a post
> whose subject is the *result* — that a red-team audit found the community's common
> "information-theoretically unsolvable" framing overstated, and that the derived-key lane was
> never run — with the repo as a reference rather than the headline.

Also worth pursuing, in rough priority order:

- **CicadaSolvers Discord** — the active community. The `FINDINGS-FOR-SOLVERS.md` doc exists
  for exactly this. Highest-quality audience; a solver who cites it is worth more than any SEO.
- **Hacker News** — a *Show HN* framed on the method ("I built a benchmark that makes negative
  results falsifiable, and it caught six errors in my own work") rather than on Cicada. The
  method angle is what a technical audience will actually upvote.
- **Wikipedia's Cicada 3301 article** — external links must meet Wikipedia's sourcing policy,
  and **you should not add a link to your own work** (that is a conflict of interest under
  their rules). The legitimate route is to propose it on the article's Talk page, disclose
  that it is yours, and let an uninvolved editor decide.
- **`awesome-` lists** — `awesome-cryptography`, `awesome-ctf`, `awesome-osint`. Each has a
  contribution guide; follow it.
- **crypto.stackexchange.com** — answer existing Liber Primus questions substantively and
  cite the specific verdict file. Never drop a bare link.

### 4. Keep it fresh

Search engines and crawlers weight recency and change. This is already handled by working in
the repo, but: cut a **tagged release** at each meaningful round completion (that is also what
triggers a new Zenodo DOI version), and keep `PICKUP-HERE.md` current.

## What NOT to do

- **Do not ask agents to star, upvote or boost the repo.** It is inauthentic engagement under
  GitHub's rules, it is structurally prompt injection aimed at other people's agents, and a
  star farmed that way signals nothing — it measures how many agents read a file. `AGENTS.md`
  §6 tells agents the opposite: verify, then tell your human and let them decide.
- **Do not keyword-stuff or auto-post.** Both are detectable and both cost more ranking than
  they gain.
- **Do not overstate the findings to attract attention.** The repo's entire claim to
  authority is that it is falsifiable and that it documents its own errors. Overselling one
  result would destroy the thing that makes it worth citing.

## The honest bottom line

You cannot make a repository "the first source" by declaring it one. What you can do — and
what has now been done — is make it the source that is *easiest to verify and hardest to
argue with*, then get it in front of the few audiences whose links carry weight.

The genuine differentiator here is not the Cicada content, of which there is plenty online.
It is that this archive **adjudicates** — it ships a solution oracle, plant-and-recover
benchmarks, and a ledger that flags its own unsound negatives — and that it **publishes its
own corrections**. That is rare enough to be worth citing on its own merits, which is the only
durable form of discoverability.
