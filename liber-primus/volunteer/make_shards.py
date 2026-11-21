#!/usr/bin/env python3
"""Generate shards.json for the volunteer kit. Run once; it refuses to overwrite.

The S2 shards are exactly the uncovered remainder of the Round 27 S2 lane, read from the
sha-verified recovered state (Round 42 S1): per worker band, [cursor, band_end). Each gap is
split into 6 equal shards (~57M seeds, ~42 min on one core at the measured 22.9k seeds/s).

Usage: python make_shards.py [--force]
"""
import json
import sys

from _kit import LP, SHARDS_PATH, sha256_file, write_shards

STATUS = "analysis/round42/S1-s2-recovery/state_recovered/STATUS.json"
STATUS_SHA = "1aa529444548e3e1f3add420936ddfd40ee9b9fe4cb6d25b74c197a2e070c2ba"
ENGINE_DIR = "analysis/round36/P1-panel-r36/engine_inputs_copy"
ENGINE_FILES = ["grind27.c", "engine.dat", "panel_lm.f32", "english_quadgrams.txt", "check_panel_gate.py"]
PIECES_PER_GAP = 6


def main():
    if SHARDS_PATH.exists() and "--force" not in sys.argv:
        sys.exit("shards.json exists; refusing to overwrite claims (use --force only before anyone has claimed)")
    if sha256_file(LP / STATUS) != STATUS_SHA:
        sys.exit("recovered STATUS.json does not match its recorded sha256 1aa52944..; stop")
    st = json.load(open(LP / STATUS, encoding="utf-8"))
    assert st["current_lane"] == "S2" and st["relation"] == "exact" and st["aggregate"]["n_claim_bar_hits"] == 0
    covered = sum(w["cursor"] - w["band_start"] for w in st["workers"])
    assert covered == st["aggregate"]["lane_words_covered"] == 2235695586

    lane = {
        "title": "Round 27 S2: Py2.7 MT19937 init_by_array([w]) -> random29 -> keyskip1 'exact' relation "
                 "(max_skip 3), offset 0, sign -1, beam 64, 12-register panel-R36 pmax at L=120",
        "status_doc": "liber-primus/handoff/PARKED-SWEEPS.md section 1 + 2026-11-09 banner",
        "engine_dir": ENGINE_DIR,
        "engine_source_sha256": {f: sha256_file(LP / ENGINE_DIR / f) for f in ENGINE_FILES},
        "reducer": "random29", "relation": "exact", "offset": 0, "sign": -1,
        "cand_bar": float(st["cand_bar"]), "claim_bar": float(st["claim_bar"]),
        "space": [0, 4294967296],
        "candidate_rate": 1.135e-4,
        "candidate_rate_source": "38,576 candidates >= 5.0 in the 339,966,702 panel-R36 seeds of R36 + R38 w1 + R42 "
                                 "(round36/38/42 RESULTS); re-measured 2026-11-17: 230 in 2,000,000 seeds "
                                 "[3231257507, 3233257507). Used only for the verifier's missing-stretch check.",
        "control": {
            "source": "analysis/round38/S1-s2-windows/control_exact.json",
            "cipher": "analysis/round38/S1-s2-windows/ctl_cipher_1234567891.json",
            "seed": 1234567891, "band": [1234565843, 1234569939],
            "expect_pmax": 19.81452418236752, "expect_second": [1234566462, 4.734968541121583],
        },
        "anchor": {
            "source": "analysis/round36/S1-s2-window/RESULTS.md (resume test a2) and round38 top_rescored.json",
            "seed": 35563892, "pmax": 7.6707232992600876,
            "note": "the S1/S2 claim-bar crosser adjudicated NOISE-CROSSER in analysis/round27/ORACLE-35563892.md",
        },
        "prior": {
            "covered_seeds": covered,
            "source": STATUS, "sha256": STATUS_SHA,
            "n_claim_bar_hits": 0,
            "note": "prior work, not volunteer work. Mixed instrument: seeds below each worker's R36 resume "
                    "cursor (44.14 % of 2^32) were judged by the Round 19 9-register panel; only ~7.9 pp by "
                    "panel-R36 (analysis/round42/SYNTHESIS.md). Volunteer shards are all panel-R36.",
        },
    }
    shards = []
    n = 0
    for w in st["workers"]:
        lo, hi = w["cursor"], w["band_end"]
        size = hi - lo
        for i in range(PIECES_PER_GAP):
            a = lo + size * i // PIECES_PER_GAP
            b = lo + size * (i + 1) // PIECES_PER_GAP
            n += 1
            shards.append({"id": "S2-%03d" % n, "lane": "S2", "from": a, "to": b, "seeds": b - a,
                           "gap": "R27 worker %d band" % w["worker"],
                           "status": "unclaimed", "claimant": None, "result": None})
    assert sum(s["seeds"] for s in shards) == 2 ** 32 - covered
    shards.append({"id": "TEST-S2", "lane": "S2", "from": 35561844, "to": 35565940, "seeds": 4096,
                   "gap": "TEST ONLY: already-covered band around anchor seed 35563892 (a known noise-crosser); "
                          "never counted as coverage",
                   "status": "test", "claimant": None, "result": None})
    db = {
        "kit_version": 1,
        "about": "Volunteer shard table. Status: unclaimed -> claimed (issue opened) -> done (PR with "
                 "results/<id>.json merged). 'test' shards are smoke tests and never count as coverage.",
        "lanes": {"S2": lane},
        "shards": shards,
    }
    write_shards(db)
    print("wrote %d shards (%d S2 + 1 test), remaining S2 seeds %d" % (len(shards), n, 2 ** 32 - covered))


if __name__ == "__main__":
    main()
