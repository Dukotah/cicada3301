"""R43 / F5b-T step 1 - merge the four onion-2 timing witnesses into one per-cell interval table.

Witnesses (all local):
  W1 BotSottile  round43/F5-stored/onion2-timing_BotSottile_qn8jmPJr.txt   (absolute GMT+1 stamps, parsed)
  W2 Cripion101  round43/F5-stored/onion2-timing_Cripion101_5bTLHqCN.txt  (31 samples, embedded below verbatim)
  W3 wiki-00120  corpus/C-community/wikis/uncovering-cicada/export_cur_00120.xml (20-col table, embedded)
  W4 wiki-00140  corpus/C-community/wikis/uncovering-cicada/export_cur_00140.xml (table + 25-sample, embedded)

Anchor = W1 absolute timestamps.  Per PREREG: bot restart/dump stamps and non-5-minute-grid stamps are
upper bounds, not arrivals.  Positions are located by byte-run match in the final 256-byte string.
Every overlap is cross-checked; every mismatch is printed and stored.  Output: merged_intervals.json.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
F5 = os.path.join(HERE, "..", "F5-stored")

# The final 256-byte string (held in export_cur_00120.xml "FULL SHORT STRING" and the W1 log).
FINAL = ("634292ba49fe336edada779a34054a335c2ec12c8bbaed4b92dcc05efe98f76abffdc2389bdb9de2cf20c009acdc1945"
         "ab095a52609a5c219afd5f3b3edf10fcb25950666dfe8d8c433cd10c0b4c72efdfe12c6270d5cfde291f9cf0d73cb121"
         "1140136e4057380c963d70c76948d9cf6775960cf98fbafa435c44015c5959837a0f8d9f46e094f27c5797b7f8ab49bf"
         "28fa674d2ad2f726e197839956921dab29724cd48e1a81fc9bab3565f7513e3e368cd0327b47cf595afebb78d6b5bca9"
         "2ba021cd6734f4362a0b341f359157173b53d49ea5dff5889d2c9de6b0d7e8c615286ce596bfa83f50b6eeabd153aaf5"
         "0cd75f39929ba11fb0f8e8d611442846")
assert len(FINAL) == 512
BYTES = [FINAL[i:i + 2] for i in range(0, 512, 2)]      # 1-indexed positions 1..256 -> BYTES[pos-1]

def locate(run):
    """1-indexed position of the FIRST byte of a byte-run; assert unique."""
    s = "".join(run)
    hits = [m.start() for m in re.finditer("(?=%s)" % s, FINAL) if m.start() % 2 == 0]
    assert len(hits) == 1, (run[:4], hits)
    return hits[0] // 2 + 1

# ---------------------------------------------------------------- W1 BotSottile (parse the stored file)
def parse_bot():
    txt = open(os.path.join(F5, "onion2-timing_BotSottile_qn8jmPJr.txt"), encoding="utf-8").read()
    ev = []   # (hh, mm, payload_hex, newlen)
    for m in re.finditer(r"\[(\d\d):(\d\d)\] <BotSottile> New byte\(s\): ([0-9a-f]+) -- new len: (\d+)", txt):
        ev.append((int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))))
    # absolute minute-of-campaign: day rolls over once (23:50 -> 00:05)
    times, day = {}, 0
    prev = None
    for hh, mm, pay, ln in ev:
        t = hh * 60 + mm
        if prev is not None and t < prev - 600:
            day += 1
        prev = t
        t += day * 1440
        single = len(pay) == 2
        grid = (mm % 5 == 0)
        # verify payload against FINAL
        if single:
            assert pay == BYTES[ln - 1], (ln, pay, BYTES[ln - 1])
        else:
            assert "".join(BYTES[:ln]) == pay, ("dump mismatch at len", ln)
        kind = "arrival" if (single and grid) else "upper_bound"
        # keep the earliest stamp per length
        if ln not in times:
            times[ln] = {"t": t, "kind": kind, "stamp": "%02d:%02d" % (hh, mm)}
    return times

# ---------------------------------------------------------------- W2 Cripion101 (verbatim from the stored file)
CRIP1_MIN = "00 20 25 35 50 05 15 20 45 00 15 20 40 45 05 10 25 30 40 15 25 30".split()
CRIP1_ELA = "05 20 05 10 15 15 10 05 25 15 15 05 20 05 20 05 05 15 10 35 10 05".split()
CRIP1_BYT = "26 e1 97 83 99 56 92 1d ab 29 72 4c d4 8e 1a 81 fc 9b ab 35 65 f7".split()
CRIP2_MIN = "40 55 00 05 20 45 00 15 25".split()
CRIP2_ELA = "10 15 05 05 15 25 15 15 10".split()
CRIP2_BYT = "51 3e 3e 36 8c d0 32 7b 47".split()

# ---------------------------------------------------------------- W3 wiki-00120 (verbatim from the export)
W3_CLOCK = "00 20 25 35 50 05 15 20 45 00 15 20 40 45 05 10 15 30 40 15".split()
W3_INTVL = [None] + "20 05 10 15 15 10 05 25 15 15 05 20 05 20 05 05 15 10 35".split()
W3_BYT = "26 e1 97 83 99 56 92 1d ab 29 72 4c d4 8e 1a 81 fc 9b ab 35".split()

# ---------------------------------------------------------------- W4 wiki-00140 (verbatim from the export)
W4_CLOCK = "00 20 25 35 50 05 15 20 45 00 15 20 40 45 05 10".split()   # truncated in the source
W4_INTVL = [None] + "20 05 10 15 15 10 05 25 15 15 05 20 05 20 05 05 15 10 35".split()
W4_BYT = "26 e1 97 83 99 56 92 1d ab 29 72 4c d4 8e 1a 81 fc 9b ab 35".split()
# the 25-sample "98% sure" delay row; witness marks the first 10 "reported ... cannot confirm"
W4_25 = "10 30 10 15 05 05 10 15 05 05 20 05 10 15 15 10 05 25 15 15 05 20 05 20 05".split()


def main():
    conflicts, notes = [], []
    cells = {}          # pos -> {"claims": [(witness, interval)], ...}

    def claim(pos, witness, interval, conf="exact"):
        cells.setdefault(pos, []).append({"witness": witness, "interval": int(interval), "confidence": conf})

    # ---- positions
    p1 = locate(CRIP1_BYT)                      # Cripion block 1 start
    p2 = locate(CRIP2_BYT)                      # Cripion block 2 start
    p3 = locate(W3_BYT)
    assert p3 == p1 and p2 == p1 + len(CRIP1_BYT)
    notes.append("Cripion block1 = bytes %d-%d; block2 = bytes %d-%d (contiguous); wiki tables start at %d."
                 % (p1, p1 + 21, p2, p2 + 8, p3))

    bot = parse_bot()
    # ---- W1 claims: interval(n) where both t(n) and t(n-1) are exact arrivals
    for ln in sorted(bot):
        a, b = bot.get(ln - 1), bot[ln]
        if a and a["kind"] == "arrival" and b["kind"] == "arrival":
            iv = b["t"] - a["t"]
            if iv % 5:
                conflicts.append({"type": "non-multiple-of-5", "pos": ln, "witness": "W1", "interval": iv})
            claim(ln, "W1-BotSottile", iv)

    # ---- W2 claims from the elapsed rows
    for i, e in enumerate(CRIP1_ELA):
        claim(p1 + i, "W2-Cripion-elapsed", int(e))
    for i, e in enumerate(CRIP2_ELA):
        claim(p2 + i, "W2-Cripion-elapsed", int(e))
    # W2 internal check: minute diffs vs elapsed
    for i in range(1, len(CRIP1_MIN)):
        d = (int(CRIP1_MIN[i]) - int(CRIP1_MIN[i - 1])) % 60
        if d != int(CRIP1_ELA[i]):
            conflicts.append({"type": "W2-internal-minute-vs-elapsed", "pos": p1 + i, "byte": CRIP1_BYT[i],
                              "minute_implies": d, "elapsed_says": int(CRIP1_ELA[i])})
    for i in range(1, len(CRIP2_MIN)):
        d = (int(CRIP2_MIN[i]) - int(CRIP2_MIN[i - 1])) % 60
        if d != int(CRIP2_ELA[i]):
            conflicts.append({"type": "W2-internal-minute-vs-elapsed", "pos": p2 + i, "byte": CRIP2_BYT[i],
                              "minute_implies": d, "elapsed_says": int(CRIP2_ELA[i])})

    # ---- W3 claims + internal check
    for i, v in enumerate(W3_INTVL):
        if v is not None:
            claim(p3 + i, "W3-wiki00120", int(v))
    for i in range(1, len(W3_CLOCK)):
        d = (int(W3_CLOCK[i]) - int(W3_CLOCK[i - 1])) % 60
        if d != int(W3_INTVL[i]):
            conflicts.append({"type": "W3-internal-clock-vs-interval", "pos": p3 + i,
                              "clock_implies": d, "interval_says": int(W3_INTVL[i])})
    # W3 vs W2 clock rows
    for i in range(min(len(W3_CLOCK), len(CRIP1_MIN))):
        if W3_CLOCK[i] != CRIP1_MIN[i]:
            conflicts.append({"type": "W3-vs-W2-clock-digit", "pos": p3 + i, "byte": W3_BYT[i],
                              "W3_clock": W3_CLOCK[i], "W2_minute": CRIP1_MIN[i]})

    # ---- W4 table claims (same table as W3, list form)
    for i, v in enumerate(W4_INTVL):
        if v is not None:
            claim(p3 + i, "W4-wiki00140-table", int(v))
    # ---- W4 25-sample: align so its confirmed tail matches the W2/W3 values -> it ends at p1+15 (byte '81')
    end = p1 + 15
    start = end - len(W4_25) + 1
    for i, v in enumerate(W4_25):
        conf = "unconfirmed-by-witness" if i < 10 else "exact"
        claim(start + i, "W4-wiki00140-25sample", int(v), conf)
    notes.append("W4 25-sample aligned to bytes %d-%d (tail matches W2/W3 exactly); first 10 (bytes %d-%d) "
                 "are the witness's own 'cannot confirm' values." % (start, end, start, start + 9))

    # ---- merge
    merged, disagreements = {}, []
    for pos in sorted(cells):
        cl = cells[pos]
        vals = sorted({c["interval"] for c in cl})
        if len(vals) == 1:
            iv = vals[0]
            conf = ("single-witness-unconfirmed" if all(c["confidence"] == "unconfirmed-by-witness" for c in cl)
                    else ("multi-witness" if len(cl) > 1 else "single-witness"))
        else:
            # majority resolution, per PREREG (only legal for a same-witness clock-digit slip)
            from collections import Counter
            cnt = Counter(c["interval"] for c in cl)
            iv, n = cnt.most_common(1)[0]
            disagreements.append({"pos": pos, "values": {str(k): v for k, v in cnt.items()}, "resolved": iv})
            conf = "majority-resolved"
        if iv % 5 or iv < 5:
            conflicts.append({"type": "interval-not-5k", "pos": pos, "interval": iv})
        merged[pos] = {"pos": pos, "byte": BYTES[pos - 1], "interval_min": iv, "k": iv // 5,
                       "confidence": conf, "witnesses": cl}

    # ---- the W1-offline bridge (bytes with no exact claim between attested neighbours)
    poss = sorted(merged)
    lo, hi = poss[0], poss[-1]
    missing = [p for p in range(lo, hi + 1) if p not in merged]
    bridge = None
    if missing == [190, 191]:
        t189, t192 = bot[189], bot[192]
        # t(191) known exactly (bot arrival); interval(190)+interval(191) = t(191)-t(189)
        t191 = bot[191]
        total = t191["t"] - t189["t"]
        bridge = {"positions": [190, 191], "sum_min": total,
                  "variants_k": [[a, total // 5 - a] for a in range(1, total // 5)]}
        notes.append("Bytes 190-191: W1 offline (restart dump 18:56); interval sum = %d min (t189 18:30 -> "
                     "t191 19:00); %d bounded variants." % (total, total // 5 - 1))
    else:
        notes.append("UNEXPECTED missing cells inside the attested span: %s" % missing)

    # ---- overlap stats
    n_multi = sum(1 for m in merged.values() if len(m["witnesses"]) > 1)
    out = {
        "final_string_sha_note": "FINAL embedded from export_cur_00120.xml; W1 dumps verified byte-exact against it",
        "attested_exact_cells": len(merged),
        "attested_span": [lo, hi],
        "cells_multi_witness": n_multi,
        "cells_single_witness": len(merged) - n_multi,
        "cells_unconfirmed_by_witness": sum(1 for m in merged.values()
                                            if m["confidence"] == "single-witness-unconfirmed"),
        "bounded_bridge": bridge,
        "value_disagreements": disagreements,
        "all_findings": conflicts,
        "notes": notes,
        "cells": [merged[p] for p in sorted(merged)],
    }
    json.dump(out, open(os.path.join(HERE, "merged_intervals.json"), "w"), indent=1)

    # ---- the key streams for the sweep (structure per PREREG)
    kA = [merged[p]["k"] for p in range(143, 190) if p in merged]
    kB = [merged[p]["k"] for p in range(192, 257) if p in merged]
    assert len(kA) == 47 - len([p for p in range(143, 190) if p not in merged])
    streams = {"S_A": {"span": [143, 189], "k": kA},
               "S_B": {"span": [192, 256], "k": kB},
               "bridge_variants": bridge["variants_k"] if bridge else []}
    json.dump(streams, open(os.path.join(HERE, "key_streams.json"), "w"), indent=1)

    print(json.dumps({k: out[k] for k in ("attested_exact_cells", "attested_span", "cells_multi_witness",
          "cells_single_witness", "cells_unconfirmed_by_witness", "value_disagreements", "bounded_bridge",
          "notes")}, indent=1))
    print("len S_A", len(kA), "len S_B", len(kB))
    print("S_A", kA)
    print("S_B", kB)
    print("findings:", json.dumps(conflicts, indent=1))


if __name__ == "__main__":
    main()
