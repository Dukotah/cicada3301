# Campaign XV — Probe P1: Skip-tolerant / filter-aware keystream decode

- **probe_id:** P1-skip-beam
- **verdict:** soundness-confirmed  (also a clean null-closed over the attested generator family + cached keytexts)
- **headline_number:** grand-best skip-aware DP score_norm = **-6.442** over ALL real decodes (GATE = -5.2); the discriminating power is proven by synthetic **separation = 2.958** (correct gen -4.277 vs best wrong -7.235).
- **falsifiable_signal:** any (generator/keytext, offset, sign, ±Atbash) whose skip-aware beam best-path `score_norm > -5.2` with readable Gematria-English = BREAK.
- **signal_fired:** **false** (0 of 2876 real configs cleared the gate; best real decode -6.442, i.e. 1.24 below gate, in the noise band).

## synthetic_validation
Planted 1600 runes of real English→Gematria, encrypted with the attested **φ(prime)** generator through a **soft skip-on-collision filter** (p_soft=0.83; 38 skips; ciphertext doublet rate driven down to 0.375%, mimicking LP2's ~0.66% deficit vs the ~3.4% of a rigid pad). Results:
- **Correct generator, RIGID (no-skip) beam → score_norm = -7.471** (noise). This is the whole point: the *correct* keystream looks like garbage once the alignment drifts — exactly the blind spot that could have made ~112 prior rigid nulls unsound.
- **Correct generator, SKIP-AWARE beam → score_norm = -4.277, 97.4% plaintext recovery** (head decodes back to the planted text). The DP recovers the plaintext through the skips.
- **Four WRONG generators (primes, fib(1,1), totient(int), fib(3,5)), skip-aware → -7.24…-7.33** — the extra freedom of the skip transition does NOT let a wrong keystream cheat above the gate.
- **Separation = correct(-4.277) − best-wrong(-7.235) = 2.958.** Method has real discriminating power and a wide margin.

## method
Beam DP with state (text pos i, keystream index j): transition j→j+1 always, and j→j+2 only at collision-consistent sites where `c[i+1]-c[i] ≡ st[j+2]-st[j+1] (mod 29)` (the condition under which st[j+1] would have produced a doublet), with a per-skip log-penalty of 3.0. Emission = incremental letter-quadgram logprob that exactly reproduces `score.score_norm` over the decoded translit; the winning path is re-scored with the repo's real scorer so every number is comparable to the -5.2 gate. Swept the Cicada-attested generator family (consecutive primes, φ(prime), totient(int), prime gaps, six Fibonacci-mod-29 seeds) × offsets 0..1000 step 100 × both signs × ±Atbash on the continuous stream, plus 21 cached keytexts as running keys (data/keys, foundation Hermetica/Sephir-Yetzirah/Rosicrucian/Monas/Enoch, armada20), plus every generator per page. All computed, no network.

- **script_path:** /home/user/cicada3301/liber-primus/analysis/campaign15/P1-skip-beam.py
- **reproduce_cmd:** `PYTHONUTF8=1 python analysis/campaign15/P1-skip-beam.py`

## Measured ceilings (all real decodes, GATE = -5.2)
| Phase | Scope | Configs | Best score_norm |
|---|---|---|---|
| B | Generator family × offset × sign × Atbash, continuous stream | 440 | -7.152 (primes, off 700, −, Atbash) |
| C | 21 cached keytexts as running keys, skip-aware | 236 | -7.154 (monas_clean_key, off 200, −, Atbash) |
| D | Per-page, all generators, offset 0 | 2200 | -6.442 (page49, φ(prime) — the non-prose pp49–51 base-60 payload region) |
| — | **GRAND BEST** | **2876** | **-6.442** |

## one_paragraph
The soundness worry was concrete and, it turns out, well-founded in the abstract: my synthetic control shows the *correct* keystream, when a skip filter drifts its alignment, scores -7.47 under the rigid decode every prior campaign used — indistinguishable from noise. So the ~112 prior keystream/keytext nulls genuinely *were* alignment-fragile, and a skip-tolerant decoder was the right tool to close that gap. I built one, validated that it recovers planted English at 97.4% (score -4.28) while wrong generators stay pinned at -7.2 to -7.3 even with full skip freedom (separation 2.96), then turned it on LP2. Across 2,876 skip-aware decodes — the entire attested generator family (primes, φ(prime), iterated totient, prime gaps, Fibonacci seeds) over offsets, both signs and ±Atbash, per-page and as one continuous stream, plus 21 cached esoteric/PGP keytexts as running keys — nothing cleared the -5.2 break threshold. The best real decode was -6.442 (and that was the non-prose base-60 payload region, not the runic prose), a full 1.24 below the gate and well inside the noise band. This is a clean null with proven discriminating power: the rigid-alignment caveat on the keystream/generator eliminations is now discharged, strengthening the one-time-pad-class verdict rather than weakening it.

## ledger_row
| Attack | Verdict | Why | Where |
|---|---|---|---|
| **Skip-tolerant / filter-aware keystream decode** (DP beam, j→j+2 skip on collision-consistent sites; attested generator family + 21 cached keytexts × offsets × signs × ±Atbash, per-page and continuous) | ❌ dead — soundness caveat discharged | Synthetic control proves rigid decode of the *correct* key collapses to noise (-7.47) while the skip-aware beam recovers it (-4.28, 97.4%, separation 2.96); yet 0/2876 real LP2 decodes clear -5.2 (grand best -6.442). The ~112 rigid-alignment nulls were vulnerable in principle but hold in fact. | Campaign XV `analysis/campaign15/P1-skip-beam.py` |
