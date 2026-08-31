#!/usr/bin/env python3
"""
Round 22 — Lane D — order/structure test for the drop-cap channel.

Given features.json, test whether the DROP-CAP PRESENCE SEQUENCE (and the derived
integer sequences: red-pixel counts, centroids) carries ORDER structure beyond a
size-matched shuffled null (seed 3301). Per doctrine R3, we persist language-agnostic
order statistics, not just an English score.

Recognizers (Q1 — written before the run, see PREREG.md):
A message hidden in "which pages are illuminated, in what order" would show up as:
  (S1) the presence bitstring parsing as ASCII / a base-29 index / a run-length code
       that is *non-random* — measured by its compressibility vs the null;
  (S2) the gap sequence between illuminated pages being non-uniform beyond null;
  (S3) the count of illuminated pages hitting a distinguished value (prime, 29, 3301-ish);
  (S4) a monotone / periodic trend in a per-page integer feature (red centroid, px count)
       stronger than a size-matched shuffle.

Null: shuffle the per-page feature vector 10000x under seed 3301, recompute each
statistic, report the empirical p-value (fraction of shuffles >= observed).
"""
import os, json, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 3301
NSHUF = 10000


def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True


def compress_len(bits):
    b = bytes(int("".join(map(str, bits[i:i+8].tolist())).ljust(8, "0"), 2)
              for i in range(0, len(bits), 8))
    return len(zlib.compress(b, 9))


def main():
    with open(os.path.join(HERE, "features.json")) as fh:
        data = json.load(fh)
    feats = data["features"]
    pages = sorted(int(k) for k in feats)
    presence = np.array([1 if feats[str(p)]["has_dropcap"] else 0 for p in pages], dtype=int)
    redpx = np.array([feats[str(p)]["red_px"] for p in pages], dtype=float)

    rng = np.random.default_rng(SEED)
    n_illum = int(presence.sum())
    illum_pages = [p for p in pages if feats[str(p)]["has_dropcap"]]

    results = {}

    # --- S3: count of illuminated pages, distinguished-value check ---
    results["n_illuminated"] = n_illum
    results["n_illuminated_is_prime"] = is_prime(n_illum)
    results["n_illuminated_is_29"] = (n_illum == 29)
    results["n_pages"] = len(pages)
    results["illuminated_pages"] = illum_pages

    # --- S2: gap sequence between illuminated pages, uniformity vs null ---
    def gap_var(order):
        idx = np.where(order == 1)[0]
        if len(idx) < 2:
            return 0.0
        return float(np.var(np.diff(idx)))
    obs_gapvar = gap_var(presence)
    null_gapvar = np.empty(NSHUF)
    for i in range(NSHUF):
        s = presence.copy(); rng.shuffle(s)
        null_gapvar[i] = gap_var(s)
    # two-sided-ish: report fraction of null with gap-var <= observed (clustered) and >= (spread)
    p_clustered = float((null_gapvar <= obs_gapvar).mean())
    p_spread = float((null_gapvar >= obs_gapvar).mean())
    results["gap_var_observed"] = round(obs_gapvar, 3)
    results["gap_var_p_clustered"] = round(p_clustered, 4)
    results["gap_var_p_spread"] = round(p_spread, 4)

    # --- S1: compressibility of the presence bitstring vs null ---
    obs_clen = compress_len(presence)
    null_clen = np.empty(NSHUF)
    for i in range(NSHUF):
        s = presence.copy(); rng.shuffle(s)
        null_clen[i] = compress_len(s)
    # a real code compresses BETTER (smaller) than random -> low p
    p_compress = float((null_clen <= obs_clen).mean())
    results["presence_bits"] = "".join(map(str, presence.tolist()))
    results["compress_len_observed"] = obs_clen
    results["compress_len_null_mean"] = round(float(null_clen.mean()), 3)
    results["compress_p_more_structured"] = round(p_compress, 4)

    # --- S1b: ASCII / base-29 read of the presence bitstring ---
    bits = presence.tolist()
    # pack to bytes, show printable-ASCII fraction
    bs = bytes(int("".join(map(str, bits[i:i+8])).ljust(8, "0"), 2)
               for i in range(0, len(bits), 8))
    printable = sum(1 for c in bs if 32 <= c < 127)
    results["presence_ascii"] = "".join(chr(c) if 32 <= c < 127 else "." for c in bs)
    results["presence_ascii_printable_frac"] = round(printable / len(bs), 3) if bs else 0.0

    # --- S4: monotone/periodic trend in red centroid_y of illuminated pages vs null ---
    cys = np.array([feats[str(p)]["red_cy"] for p in illum_pages if feats[str(p)]["red_cy"] is not None])
    if len(cys) >= 3:
        # Spearman-like rank correlation of cy with page order
        order = np.arange(len(cys))
        def rankcorr(a, b):
            ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
            return float(np.corrcoef(ra, rb)[0, 1])
        obs_rc = abs(rankcorr(order, cys))
        null_rc = np.empty(NSHUF)
        for i in range(NSHUF):
            s = cys.copy(); rng.shuffle(s)
            null_rc[i] = abs(rankcorr(order, s))
        results["centroid_y_rankcorr_observed"] = round(obs_rc, 3)
        results["centroid_y_rankcorr_p"] = round(float((null_rc >= obs_rc).mean()), 4)
    else:
        results["centroid_y_rankcorr_observed"] = None
        results["centroid_y_rankcorr_p"] = None

    # --- verdict ---
    ps = [results["gap_var_p_clustered"], results["gap_var_p_spread"],
          results["compress_p_more_structured"]]
    if results["centroid_y_rankcorr_p"] is not None:
        ps.append(results["centroid_y_rankcorr_p"])
    # Bonferroni over the ~5 tests: survivor bar p < 0.01
    min_p = min(ps)
    results["min_p"] = min_p
    results["BAR"] = "p < 0.01 (Bonferroni over 5 order statistics)"
    results["survivor"] = bool(min_p < 0.01)

    with open(os.path.join(HERE, "order_results.json"), "w") as fh:
        json.dump(results, fh, indent=2)

    print(json.dumps(results, indent=2))
    print()
    print(f"n_illuminated = {n_illum} / {len(pages)}  (prime={results['n_illuminated_is_prime']})")
    print(f"min p over order statistics = {min_p:.4f}  -> "
          f"{'SURVIVOR (flag-for-oracle)' if results['survivor'] else 'NO STRUCTURE (null)'}")
    return results


if __name__ == "__main__":
    main()
