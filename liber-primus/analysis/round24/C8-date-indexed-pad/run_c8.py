"""C8 -- date-indexed public pad: bounded fetch + positive control + steelman probe.

The lane's PRIMARY verdict is UNAVAILABLE (Step 0: the unsolved runic decrypt-target pages
carry no PGP signature timestamp to index a dated pad by). This script does the two things the
PREREG still commits to, both honestly labelled:

  (1) POSITIVE CONTROL (mandatory): encipher a real LP rune page from a REAL fetched beacon
      value at a known date; confirm the recovery-gated decoder recovers it when the pad is
      indexed at the RIGHT date and FAILS at a wrong date / wrong source. Validates the pipeline
      independent of the (failed) premise. If the control fails, STOP.

  (2) STEELMAN PROBE (non-primary): the only pages with a REAL timestamp are the solved/prose
      pages. Index the fetched beacon pad by each of the 8 real (page, timestamp) pairs and run
      HITFN over the rune content that exists. Can only reconfirm solved pages or return null;
      cannot solve LP2. Closes the "you never tried the timestamp index" objection with a
      measured negative.

Reproduce: python3 analysis/round24/C8-date-indexed-pad/run_c8.py
Bounded fetch: <= 8 beacon v1 records (one per real timestamp). No crawl. Cached to cache/.
"""
import os, sys, re, json, hashlib, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
for p in (os.path.join(LP, "src"),
          os.path.join(LP, "analysis", "round17"),
          os.path.join(LP, "analysis", "round19", "I1"),
          os.path.join(LP, "analysis", "round20", "HITFN"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "benchmark")):
    if p not in sys.path:
        sys.path.insert(0, p)

from lp import gematria as G                      # noqa: E402
import lib_padsweep as PS                         # noqa: E402
import hitfn20 as HF                              # noqa: E402
import skipdecode as SK                           # noqa: E402  encipher under the anti-repeat filter
import null as NULL                               # noqa: E402

BEACON_V1 = "https://beacon.nist.gov/rest/record/%d"
UA = {"User-Agent": "cicada-c8-lane/1.0 (research; bounded fetch)"}


# --------------------------------------------------------------------------- bounded fetch
def fetch_beacon(unix_ts: int):
    """Fetch the NIST Beacon v1 record for the pulse at-or-immediately-before unix_ts
    (causal-direction rule: a public pad must precede the page). Cache to disk. Returns the
    512-bit outputValue as bytes, or None if unreachable."""
    minute = (unix_ts // 60) * 60           # pulse minute at-or-before
    fp = os.path.join(CACHE, f"beacon_v1_{minute}.xml")
    if os.path.exists(fp):
        xml = open(fp, "r", encoding="utf-8").read()
    else:
        url = BEACON_V1 % minute
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                xml = r.read().decode("utf-8")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            return None, {"unreachable": True, "err": f"{type(e).__name__}: {e}", "url": url}
        open(fp, "w", encoding="utf-8").write(xml)
    m = re.search(r"<outputValue>([0-9A-Fa-f]+)</outputValue>", xml)
    ts = re.search(r"<timeStamp>(\d+)</timeStamp>", xml)
    if not m:
        return None, {"unreachable": False, "err": "no outputValue in record"}
    return bytes.fromhex(m.group(1)), {
        "pulse_minute": minute, "record_ts": int(ts.group(1)) if ts else None,
        "outputValue_sha256": hashlib.sha256(bytes.fromhex(m.group(1))).hexdigest(),
        "cache": os.path.relpath(fp, LP),
    }


# --------------------------------------------------------------------------- pad from beacon
def fetch_beacon_chain(unix_ts: int, n_pulses: int):
    """Fetch n_pulses CONSECUTIVE v1 records starting at the pulse at-or-before unix_ts and
    concatenate their outputValues -- the causal-direction steelman pad (an author with one
    signing instant would extend it with the following pulses). Returns (concat_bytes, metas)."""
    minute0 = (unix_ts // 60) * 60
    blobs, metas = [], []
    for k in range(n_pulses):
        b, meta = fetch_beacon(minute0 + k * 60)
        if b is None:
            metas.append(meta)
            break
        blobs.append(b)
        metas.append(meta)
    return (b"".join(blobs) if blobs else None), metas


def pad_from_beacon(blob: bytes, builder="mod29"):
    """Turn the beacon outputValue into a rune-index keystream via an R17 builder.

    NOTE (learned in this lane): a single 512-bit pulse yields only ~64 rune symbols (mod29
    builder), fewer for nibble/prime builders' effective range. Do NOT tile a single pulse to
    fill a longer page -- tiling injects periodic doublet structure that desyncs the anti-repeat
    beam (control recovery collapsed 1.00 -> 0.28 across the tile boundary). The correct index
    for a page-length pad would concatenate CONSECUTIVE pulses; but a page signed at one instant
    maps to exactly one pulse, so we cap the tested length at one pulse's worth of symbols. This
    is the honest scope: one pulse pads at most ~64 runes."""
    fn = PS.BUILDERS.get(builder) or getattr(PS, "ks_" + builder)
    return [int(x) % 29 for x in fn(blob)]


# --------------------------------------------------------------------------- corpus
def solved_rune_pages():
    """Real LP rune pages with a signature nearby, from data/campaign14 (the solved LP1 set).
    Returns {name: rune_index_list}. These are the ONLY runic pages we can honestly index by a
    real timestamp; the unsolved LP2 pages have no timestamp (Step 0)."""
    cdir = os.path.join(LP, "data", "campaign14")
    out = {}
    for f in sorted(os.listdir(cdir)):
        if not re.match(r"page_\d+\.txt$", f):
            continue
        txt = open(os.path.join(cdir, f), encoding="utf-8").read()
        idx = G.runes_to_indices(txt)
        if len(idx) >= 24:                  # need enough runes to score
            out[f] = idx
    return out


# --------------------------------------------------------------------------- positive control
def positive_control():
    """Encipher Cicada-register English with a REAL beacon-derived pad at a known date, UNDER
    THE ANTI-REPEAT KEY-SKIP FILTER (the construction the beam is built to invert -- exactly
    R17's own control model, `skipdecode.encipher_keyskip`), planted at a deep offset in a pad
    of CONSECUTIVE pulses from the signing time. Then prove the recovery-gated decoder recovers
    it at the RIGHT date and FAILS at a WRONG date / WRONG source.

    Decode relation: p = (c + sign*k) mod N. NOTE: an earlier version enciphered plain-additive
    without the filter; the beam then desynced (control recovery 0.28-0.50) because it inserts
    phantom anti-repeat skips a filterless ciphertext does not contain. Enciphering WITH the
    filter is the correct, R17-matched control."""
    # Cicada-register plaintext (R17 control text), long enough to span several pulses.
    plain_en = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
                "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
                "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
                "SACRED GEOMETRY OF THE CIRCUMFERENCE")
    P = SK.eng_to_idx(plain_en)
    npad = len(P) + 40                       # room for a deep offset + the filter's skips

    right_ts = 1389064601                    # blk 0 sig-creation (2014-01-07T03:16:41Z)
    wrong_ts = 1390117197                    # blk 4/7 sig-creation (2014-01-19), a real wrong date
    n_pulses = (npad // 64) + 4              # ~64 mod29 symbols per 512-bit pulse
    b_right, metas_r = fetch_beacon_chain(right_ts, n_pulses)
    b_wrong, metas_w = fetch_beacon_chain(wrong_ts, n_pulses)
    if b_right is None:
        return {"status": "SOURCE_UNAVAILABLE", "detail": metas_r}

    K_right = pad_from_beacon(b_right, "mod29")
    o_true = 137                             # a deep offset (not 0)
    # encipher UNDER THE FILTER at the deep offset
    C, skips, used = SK.encipher_keyskip(P, K_right[o_true:], sign=-1, supp=0.83)

    # decode at RIGHT date/offset (correct pad) -- must recover >= 0.90 vs ground truth P
    v_right = HF.evaluate(HF.HitDecode(C=C, K=K_right, o=o_true, sign=-1, preset="exact",
                                       n_round_adjudicated=64, truth_idx=P))
    # decode at WRONG date (real other pulse), same offset -- must FAIL to recover
    if b_wrong is not None:
        K_wrong = pad_from_beacon(b_wrong, "mod29")
    else:
        K_wrong = [((x * 7 + 3) % 29) for x in range(len(K_right))]
    v_wrong = HF.evaluate(HF.HitDecode(C=C, K=K_wrong, o=o_true, sign=-1, preset="exact",
                                       n_round_adjudicated=64, truth_idx=P))
    # decode at WRONG source (deterministic seed-3301 pad, not the beacon) -- must FAIL
    import random
    rng = random.Random(3301)
    K_src = [rng.randrange(29) for _ in range(len(K_right))]
    v_src = HF.evaluate(HF.HitDecode(C=C, K=K_src, o=o_true, sign=-1, preset="exact",
                                     n_round_adjudicated=64, truth_idx=P))

    passed = (v_right.recovery >= 0.90 and v_wrong.recovery < 0.90 and v_src.recovery < 0.90)
    return {
        "status": "PASS" if passed else "FAIL",
        "control_model": "encipher_keyskip (anti-repeat filter, supp=0.83) at deep offset "
                         f"o={o_true}; consecutive-pulse pad; n_plain={len(P)}, "
                         f"n_skips={int(sum(skips))}",
        "n_pulses_fetched": {"right": sum(1 for m in metas_r if not m.get('unreachable')),
                             "wrong": sum(1 for m in metas_w if not m.get('unreachable'))},
        "right_date": {"ts": right_ts, "beacon_first": metas_r[0] if metas_r else None,
                       "recovery": round(v_right.recovery, 4),
                       "heldout": round(v_right.heldout_recovery, 4),
                       "pmax": round(v_right.pmax, 3), "bar": round(v_right.bar, 3),
                       "hit": v_right.hit},
        "wrong_date": {"ts": wrong_ts, "recovery": round(v_wrong.recovery, 4), "hit": v_wrong.hit},
        "wrong_source_seed3301": {"recovery": round(v_src.recovery, 4), "hit": v_src.hit},
        "verdict": ("pipeline VALIDATED: right-date recovers >=0.90, wrong-date and "
                    "wrong-source do not" if passed else
                    "pipeline BROKEN -- STOP; investigate before trusting any null"),
    }


# --------------------------------------------------------------------------- steelman probe
# The 8 real signed sections, from Step 0, mapped to the nearest solved RUNE page we can score.
# The signatures themselves are on PROSE pages (00-03 intro, 10-13 index); the runic pages that
# carry actual runes and sit in the signed neighbourhood are 01, 04-09, 14-16. We index each
# available solved rune page by each of the 8 real timestamps -> (page x timestamp x builder)
# and run HITFN. This is the fullest defensible application of the timestamp-index the artifacts
# permit; it cannot solve LP2 because LP2 has no timestamp.
SIG_TIMESTAMPS = [1389064601, 1389064604, 1389064608, 1389332574,
                  1390117197, 1390117182, 1390117190, 1390117197]
BUILDERS = ["mod29", "hi_nibble", "lo_nibble", "byte_scaled", "prime_to_idx", "nibbles"]


def steelman_probe():
    pages = solved_rune_pages()
    rows, fetched = [], {}
    n_tests = 0
    survivors = []
    for ts in sorted(set(SIG_TIMESTAMPS)):
        if ts not in fetched:
            blob, meta = fetch_beacon(ts)
            fetched[ts] = (blob, meta)
        blob, meta = fetched[ts]
        if blob is None:
            rows.append({"ts": ts, "status": "SOURCE_UNAVAILABLE", "detail": meta})
            continue
        for pname, P in pages.items():
            for builder in BUILDERS:
                K = pad_from_beacon(blob, builder)         # one pulse; NO tiling
                m = min(len(P), len(K))                    # cap at pad length
                if m < 24:
                    continue
                Pn, K = P[:m], K[:m]
                # treat the page runes AS ciphertext, index the beacon pad by this timestamp
                dec = HF.HitDecode(C=Pn, K=K, o=0, sign=-1, preset="exact",
                                   n_round_adjudicated=10 ** 6)
                v = HF.evaluate(dec)
                n_tests += 1
                row = {"ts": ts, "page": pname, "builder": builder,
                       "score": round(v.score, 3), "pmax": round(v.pmax, 3),
                       "bar": round(v.bar, 3), "recovery": round(v.recovery, 4),
                       "heldout": round(v.heldout_recovery, 4), "hit": v.hit}
                if v.hit:
                    survivors.append(row)
                rows.append(row)
    # family-wise: threshold_for over the number of tests actually run
    try:
        fw_bar = NULL.threshold_for(n_tests) if n_tests else None
    except Exception:
        fw_bar = None
    best = max((r for r in rows if "pmax" in r), key=lambda r: r["pmax"], default=None)
    return {
        "n_tests": n_tests,
        "n_pages": len(pages), "n_timestamps": len(set(SIG_TIMESTAMPS)),
        "n_builders": len(BUILDERS),
        "family_wise_threshold_for_N": fw_bar,
        "expected_fp_at_alpha0.01": round(n_tests * 0.01, 2),
        "survivors_flagged_for_oracle": survivors,
        "best_row": best,
        "rows": rows,
    }


def main():
    result = {"lane": "R24-C8", "trust_anchor": "see tests/validate.py (5/5) reported in RESULTS"}
    print("== positive control ==")
    ctrl = positive_control()
    result["positive_control"] = ctrl
    print(json.dumps({k: v for k, v in ctrl.items() if k != "rows"}, indent=1))
    if ctrl["status"] == "SOURCE_UNAVAILABLE":
        result["steelman_probe"] = {"status": "SKIPPED -- beacon source unreachable"}
        json.dump(result, open(os.path.join(HERE, "results.json"), "w"), indent=1)
        print("\nSOURCE UNAVAILABLE -- recorded, probe skipped.")
        return
    if ctrl["status"] != "PASS":
        result["steelman_probe"] = {"status": "SKIPPED -- control failed, pipeline suspect"}
        json.dump(result, open(os.path.join(HERE, "results.json"), "w"), indent=1)
        print("\nCONTROL FAILED -- STOP.")
        return
    print("\n== steelman probe (non-primary) ==")
    probe = steelman_probe()
    result["steelman_probe"] = probe
    print(json.dumps({k: v for k, v in probe.items() if k != "rows"}, indent=1))
    json.dump(result, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("\nwrote results.json")


if __name__ == "__main__":
    main()
