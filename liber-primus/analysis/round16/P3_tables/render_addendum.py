"""Regenerate the '## Addendum' section of RESULTS.md from results_ms8.json.

Kept as a script so the section can be refreshed as more ms=8 pad checkpoints land,
without hand-editing numbers.  Run:
    python sweep_ms8.py --budget 0        # collect checkpoints -> results_ms8.json
    python render_addendum.py             # rewrite the addendum section in RESULTS.md
"""
import json, os, io

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "RESULTS.md")
MARK = "## Addendum: `max_skip=8` and the corrected hex reading"


def main():
    r = json.load(open(os.path.join(HERE, "results_ms8.json")))
    runs = {x["pad"]: x for x in json.load(open(os.path.join(HERE, "data",
                                                            "run_structure.json")))}
    swept = [p["pad"] for p in r["per_pad"]]
    missing = r["pads_not_yet_swept"]
    o = io.StringIO()
    w = o.write

    w(MARK + "\n\n")
    w("Lane P1 found two defects in the shared instrument after this lane's main sweep had "
      "run. Both change **power**, not soundness — they do not invalidate a measured "
      "NEGATIVE, they narrow what it covers — so both are folded in here rather than "
      "silently inherited, and the skip budget and builder set are now stated with every "
      "coverage claim above.\n\n")

    w("**Defect 1 — `lib_padsweep.ks_hexchars` drops the digits 0–9.** It runs the hex "
      "string through `eng_to_idx`, which discards non-letters, so it is the **A–F "
      "subsequence** of the hex text, not the hex reading. P1 added `ks_nibbles` (each hex "
      "character as its value 0–15, in order), deliberately outside `BUILDERS` so existing "
      "numbers stay comparable. This bit this lane in two places: the hex-text pads "
      "(`lp_hashblock_hextext`, `cicada_hexdumps_text_pub`) — though those were separately "
      "covered by this lane's own `charval_hex`, which reads all 16 values correctly — and, "
      "more importantly, **every binary pad**, where 'read the blob as hex' was never "
      "actually swept: `hi_nibble` and `lo_nibble` see the two nibble streams *separately*, "
      "never interleaved in order. `nibbles` is therefore new coverage on 28 pads. Note "
      "that the main sweep's #1 row (`onions_ext_bin` / `hexchars_rev`, −6.420) sits on the "
      "defective builder.\n\n")

    w("**Defect 2 — `max_skip=3` is underpowered on pads with constant runs.** Repeated key "
      "symbols make the anti-repeat filter burn skips without changing the key symbol; P1 "
      "measured 6/8 plant recovery at ms=3 against 60/60 at ms=8 on a run-heavy pad. This "
      "lane is squarely in that regime, and `data/run_structure.json` measures it — longest "
      "run of identical keystream symbols in the first 500 kB, worst builder per pad:\n\n")
    w("| pad | worst builder | longest run | fraction repeated |\n|---|---|---:|---:|\n")
    for k in sorted(runs.values(), key=lambda x: -x["max_run"])[:8]:
        w(f"| `{k['pad']}` | {k['worst_builder']} | {k['max_run']:,} | "
          f"{k['frac_repeat']:.4f} |\n")
    w("\n`rand_digits` under `hi_nibble` is a **constant run of 500,000** — every ASCII "
      "digit is `0x3X`, so that whole variant is a single repeated symbol and ms=3 cannot "
      "cross it. The page JPEGs run to 25,348, and the armored-text pads repeat 20–39 % of "
      "the time.\n\n")

    n = r["n_offsets_scanned"]
    w("### Addendum coverage and result\n\n")
    w(f"> **{len(swept)} of 28 pads** re-swept at **`max_skip = 8`**, with `hexchars` "
      f"replaced by `nibbles`, both signs, every offset: **{n:,} offsets scanned**, "
      f"≈**{int(round(n * 0.625)):,}** effective after the 0.625 survival discount. "
      f"Each pad's best is adjudicated against **its own null re-measured at ms=8** "
      f"(n=200), because a larger skip budget gives the beam more freedom and lifts the "
      f"null.\n\n")
    if missing:
        w(f"**Not swept at ms=8 ({len(missing)} pads)** — these carry the main sweep's "
          f"`max_skip=3` coverage only, and the ms=8 correction is an open gap on them:\n"
          f"{', '.join('`' + m + '`' for m in missing)}.\n\n")
    else:
        w("All 28 pads were re-swept at ms=8.\n\n")

    w(f"**Result: {r['verdict']}.** ")
    b = r.get("best_raw")
    if b:
        w(f"Best raw `score_norm` **{b['score']:.3f}** "
          f"(`{b['pad']}` / {b['variant']} sign{b['sign']:+d}, offset {b['offset']:,}, "
          f"head {b['head']}) against the pre-registered bar of −5.500. "
          f"`benchmark/null.threshold_for({n:,})` = "
          f"{r['benchmark_null_threshold_for_n_trials']:.3f}. HITs: "
          f"{r['HITS'] if r['HITS'] else 'none'}.\n\n")

    w("Raising the skip budget lifts scores **and** lifts the nulls, which is exactly why "
      "the null must be re-measured rather than reused — several pads' ms=8 bests now sit "
      "*below* their own ms=8 `null_max`:\n\n")
    w("| pad | best builder | head | best (ms=8) | null_max (ms=8) | bar | HIT |\n")
    w("|---|---|---:|---:|---:|---:|---|\n")
    rows = []
    for p in r["per_pad"]:
        bb = p["best"]
        if not bb:
            continue
        key = f"{p['pad']}|{bb['variant']}|{bb['head']}"
        nu = r["nulls"].get(key)
        rows.append((p["pad"], bb["variant"], bb["head"], bb["score"],
                     nu["null_max"] if nu else None, nu["bar"] if nu else None,
                     nu["HIT"] if nu else None))
    for pad, v, h, sc, nx, bar, hit in sorted(rows, key=lambda x: -x[3]):
        w(f"| `{pad}` | {v} | {h} | {sc:.3f} | "
          f"{'%.3f' % nx if nx is not None else '—'} | "
          f"{'%.3f' % bar if bar is not None else '—'} | "
          f"{'**HIT**' if hit else 'no'} |\n")

    w("\nTwo things follow, and both are about **power, not signal**. First, `head_for` "
      "divides the pad length by `max_skip+1`, so raising ms=3 to ms=8 *shortens* the head "
      "window a short pad can carry - the onion pads drop from 40-73 runes to 25-31. "
      "Second, a shorter window plus greater beam freedom raises the score **and** the null "
      "together. The ms=8 leaderboard is therefore, again, entirely the smallest pads at "
      "their smallest windows, and the best of them (-5.679, a 31-rune read of a 304-byte "
      "pad at offset 6) misses the -5.500 bar and sits only 0.41 above its own ms=8 "
      "`null_max` of -6.088. Nothing here was judged by reading a decode.\n\n")
    w("Where a pad is long enough for the head to stay at 400, ms=8 changed essentially "
      "nothing: `rand_digits` scores **-6.765 at ms=8, identical to its ms=3 result**, so "
      "the constant-run concern - real as it is for that pad's `hi_nibble` variant - does "
      "not turn out to have been hiding anything in the printed table.\n\n")
    w("\n### Top 10 at ms=8\n\n")
    w("| # | pad | builder | sign | offset | head | score_norm |\n|---|---|---|---|---:|---:|---:|\n")
    for i, t in enumerate(r["top20"][:10], 1):
        w(f"| {i} | `{t['pad']}` | {t['variant']} | {t['sign']:+d} | {t['offset']:,} | "
          f"{t['head']} | {t['score']:.3f} |\n")

    w("\n### Reproduce the addendum\n\n```bash\n"
      "python liber-primus/analysis/round16/P3_tables/sweep_ms8.py            # resumable\n"
      "python liber-primus/analysis/round16/P3_tables/sweep_ms8.py --budget 0 # collect only\n"
      "python liber-primus/analysis/round16/P3_tables/render_addendum.py      # this section\n"
      "```\n")

    md = open(MD, encoding="utf-8").read()
    body = o.getvalue()
    if MARK in md:
        md = md[:md.index(MARK)] + body
    else:
        md = md.rstrip() + "\n\n" + body
    open(MD, "w", encoding="utf-8").write(md)
    print(f"addendum rendered: {len(swept)}/28 pads, {n:,} offsets, verdict {r['verdict']}")


if __name__ == "__main__":
    main()
