"""FRONT D3 positive control.

Claim under audit: the top-line verdict says LP2 is "information-theoretically
unsolvable / no compute recovers it / unsolvable-by-design". B4/G5 already showed a
SHORT-SEED SHA-256-counter keystream is ciphertext-indistinguishable from an OTP -- i.e.
the ciphertext CANNOT rule that family out. RECON-A B-04 lists exactly that dictionary
lane (SHA/AES-CTR/HMAC-DRBG keystreams from a Cicada seed) as NEVER-RUN.

If that lane is genuinely open, then the CORRECT short seed must be RECOVERABLE through
the project's own validated skip-aware beam decoder (score jumps noise ~ -7.5 -> English
~ -4.4), and a WRONG seed must stay in noise. This is the plant-recover gate: it proves
the dictionary sweep is a real, powered test -- not an information-theoretic dead end --
so "unsolvable-by-design" over this lane is a scope-overreach, not a fact.
"""
import os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "campaign18_skip")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "round11")))

import skipdecode as sk
import lib_numchannel as nc

N = 29

def sha_counter_keystream(seed_bytes, length):
    """B-04 family: SHA-256 counter-mode derived keystream, reduced mod 29.
    key = SHA256(seed || counter), each output byte -> mod 29."""
    out, ctr = [], 0
    while len(out) < length:
        h = hashlib.sha256(seed_bytes + ctr.to_bytes(4, "big")).digest()
        for b in h:
            out.append(b % N)
            if len(out) >= length:
                break
        ctr += 1
    return out

PLAIN = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
         "ENCRYPTEDKNOWTHISTHATTHEINSTAREMERGENCEISATHANDANDTHEPILGRIMWHO"
         "SOLVESTHEDEEPWEBSHALLFINDTHETRUTHWITHINTHECIRCUMFERENCEOFTHEEND")
P = sk.eng_to_idx(PLAIN)

TRUE_SEED = b"CICADA3301"          # short, dictionary-reachable
WRONG_SEED = b"WELCOME"

K_true = sha_counter_keystream(TRUE_SEED, len(P) * 5 + 64)
K_wrong = sha_counter_keystream(WRONG_SEED, len(P) * 5 + 64)

# encipher with the SAME soft anti-repeat key-skip filter the repo pinned
C, skips, used = sk.encipher_keyskip(P, K_true, sign=-1, supp=0.83, seed=3301)
nsk = sum(1 for s in skips if s)
dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i-1]) / (len(C)-1)

print(f"plaintext runes: {len(P)}  skips injected: {nsk}  ct doublet rate: {dbl:.4f}")

# baselines
plain_score = nc.eng_norm(P)                      # the target English score
rig_true = sk.rigid_decode(C, K_true, sign=-1, o=0)   # rigid MISSES (desync)
beam_true = sk.beam_decode(C, K_true, sign=-1, o=0, beam_w=400, max_skip=3)
beam_wrong = sk.beam_decode(C, K_wrong, sign=-1, o=0, beam_w=400, max_skip=3)

print(f"\nEnglish plaintext eng_norm target : {plain_score:.3f}")
print(f"RIGID decode, CORRECT seed        : {rig_true['score']:.3f}   (prior tests used this)")
print(f"BEAM  decode, CORRECT seed        : {beam_true['score']:.3f}   -> {beam_true['translit'][:60]}")
print(f"BEAM  decode, WRONG seed          : {beam_wrong['score']:.3f}   -> {beam_wrong['translit'][:60]}")

# null band from the repo's seed-3301 shuffled control, at N=200
mean, mx, allv = nc.null_band(lambda s: nc.eng_norm(s), P, n=200, seed0=3301)
print(f"\nnull (shuffled P, N=200): mean {mean:.3f}  max {mx:.3f}")

recovered = beam_true['translit'][:len(PLAIN)]
frac = sum(1 for a, b in zip(recovered, PLAIN) if a == b) / len(PLAIN)
print(f"char-recovery of planted plaintext: {frac:.3f}")

gate_pass = (beam_true['score'] >= -5.5 and beam_true['score'] >= mx + 0.5
             and beam_true['score'] - beam_wrong['score'] > 1.0)
print(f"\nGATE (beam recovers correct seed, jumps noise->English, beats wrong seed & null): "
      f"{'PASS' if gate_pass else 'FAIL'}")
