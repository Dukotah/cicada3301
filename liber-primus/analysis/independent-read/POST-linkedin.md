# LinkedIn draft — brand / practitioner angle

---

I spent a stretch pointing an AI-agent swarm at the last unsolved cipher in Cicada 3301's "Liber Primus" — arguably the most stubborn public cryptogram on the internet. I did not solve it. I want to talk about that, because the *way* it didn't get solved is the interesting part.

Fourteen campaigns. Each one a coordinated fan-out of AI agents attacking from a different angle, with every dead end written down so the next campaign wouldn't waste effort re-running it. And here's the trap that catches thorough people: the list of things you've ruled out becomes so impressive that you stop noticing the one thing you never fed into the machine at all.

Six campaigns had declared the case effectively closed — a text statistically indistinguishable from a one-time pad, unbreakable without a key that was never published. All correct. And all six had never loaded a 2,048-bit data object that was sitting in the project's own data files the whole time, because a loader had quietly dropped it. It was found by reading three image files by hand.

Two things I'm taking away from it:

**1. Negative results, done rigorously, are a deliverable.** We didn't find the key. But we *proved why* the popular decade-long approach — guessing which book or number sequence was used as the key — is mechanically impossible, not just unlucky. Converting "we haven't found it" into "this cannot be how it works" is real intellectual output. Most of the value an agent swarm produced here was in closing doors permanently and reproducibly.

**2. Independence is a thing you have to engineer, not assume.** The transcription everyone attacks had been "verified" by a classifier — but that classifier was trained on the transcription's own labels, so it could only ever agree with itself. I ran a read that never sees the labels: cluster every rune by shape alone, then check whether that emergent partition matches the canonical one. It did. That's the first genuinely independent confirmation the ciphertext is real — and it took separating the *read* from the *answer key*, which is a mistake that shows up everywhere in ML evaluation, not just in runes.

The whole thing is public, with reproducible code and a full elimination ledger, so the next person doesn't re-run the dead ends.

Sometimes the most honest — and most useful — output of a hard search is a precise map of where the answer *isn't*.

[link to repo / writeup]

#AI #Cryptography #Cicada3301 #AgentOrchestration #SecurityResearch
