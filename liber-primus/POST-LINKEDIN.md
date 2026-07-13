# Final draft — LinkedIn / blog (professional-brand)

_Practitioner-brand angle. The runes are the hook; the real content is method,
rigor, and intellectual honesty. Says plainly it isn't a solve. Supersedes the
earlier analysis/independent-read/POST-linkedin.md (adds the boundary proof and
the Stallman demo)._

---

I spent a long stretch pointing an AI-agent swarm at the last unsolved cipher in
Cicada 3301's Liber Primus — arguably the most stubborn public cryptogram on the
internet. I did not solve it. The way it *didn't* get solved is the part worth
your time.

Most attempts on a problem like this hit the ciphertext harder and harder. The
more useful move is to red-team the **assumptions** the whole effort quietly
rests on. So instead of guessing more keys, I attacked the premises — eight of
them — and watched each one hold:

the key · the reading order · a hidden acrostic/subsequence · a 1-bit channel ·
the transcription · autokey feedback · **the plaintext language** (maybe it's
Latin, not English?) · **a book cipher** (maybe the runes are pointers into a
book, not a cipher at all?).

All eight sealed, each with reproducible code. That turns a decade-old "unsolved,
maybe nobody's been clever enough" into something stronger and more honest: *a
boundary proof.* Not "unbreakable magic" — a professional red-team sign-off that
the ciphertext **alone** is insufficient, which for a well-built one-time-pad-class
cipher is a property, not a failure. The people who designed this were
cryptographers, and confirming rigorously that they succeeded is a real result.

Two things I'm taking from it, both of which generalize far beyond runes:

**1. Negative results, done rigorously, are a deliverable.** We didn't find the
key — but we *proved why* the popular decade-long approach (guess which book or
number sequence was the key) is mechanically impossible, not just unlucky.
Converting "we haven't found it" into "this cannot be how it works," reproducibly,
is real intellectual output. Most of the value an agent swarm produced here was in
closing doors *permanently*.

**2. Independence and open-vs-closed sets — the trap that names innocent people.**
Late in the project I built a stylometric matcher to ask "who wrote this?" and ran
Cicada's prose through it. It confidently returned a name: **Richard Stallman.**
Obviously wrong. Here's why it happened, and why it matters everywhere:

- A closed-set matcher *always* returns a nearest name — even when the true author
  isn't in the lineup. Calibrated at Cicada's short text length, a confident-looking
  match is the *wrong* person ~62% of the time.
- The "76% accuracy" you'd quote for such a tool is a lie for this purpose, because
  it assumes the author is already in your set. Drop that assumption and it names
  innocents with a straight face.

Every "AI unmasked the anonymous author" headline you'll ever read is probably
making exactly this error. Knowing *why the tempting answer is wrong* is worth more
than the answer.

The whole thing is public — reproducible code, and a complete "elimination ledger"
so the next person doesn't re-run the dead ends. Sometimes the most honest, and
most useful, output of a hard search is a precise map of where the answer *isn't*.

#AI #Cryptography #Cicada3301 #AgentOrchestration #SecurityResearch
