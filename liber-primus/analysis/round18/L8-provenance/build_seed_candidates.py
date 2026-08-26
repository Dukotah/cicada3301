#!/usr/bin/env python3
"""L8 / corpus G-09 — turn authenticated Cicada timestamps into a RANKED seed-candidate
list with provenance per entry, for the seed lanes (L6 / Round 8 successors).

Why this exists: Round 8's sweep enumerated every unix second of 2011-2015 uniformly for
10 generators. Seeds are not uniform. A person seeding an RNG types a number they have in
front of them, and the numbers this author demonstrably had in front of them are the
timestamps their own machine wrote into signature and key packets.

This produces a PRIOR, not a keyspace, and it runs nothing.

Derivation set is FIXED in PREREG.md and is not extended here.
"""
import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTC = timezone.utc

MESSAGES = json.loads((HERE / "MESSAGES.json").read_text())
TABLE = json.loads((HERE / "PGP-VERIFICATION-TABLE.json").read_text())

# --------------------------------------------------------------------- source timestamps
SOURCES = []

for m in MESSAGES["messages"]:
    if m["verdict"] != "PASS" or not m["signature_timestamp_unix"]:
        continue
    SOURCES.append({
        "unix": m["signature_timestamp_unix"],
        "utc": m["signature_timestamp_utc"],
        "kind": "pgp_signature_creation",
        "label": (m["first_line"] or "")[:60],
        "provenance_class": "verified",
        "authorship_proximity": "author_machine",
        "evidence": "signature packet of a message that verifies against 7A35090F under an "
                    "isolated keyring; see PGP-VERIFICATION-TABLE.json",
        "source": "liber-primus/analysis/round18/L8-provenance/MESSAGES.json",
        "retrieved_utc": MESSAGES["generated_utc"],
    })

# key material, read from the packet dump of the canonical key held in-repo
KEY_EVENTS = [
    (1325734783, "2012-01-05T03:39:43Z", "pgp_primary_key_creation",
     "7A35090F primary key packet (RSA-4096)"),
    (1325734783, "2012-01-05T03:39:43Z", "pgp_subkey_creation",
     "7A35090F encryption subkey 4D390ECF671DDEB1, created in the same second"),
    (1325734783, "2012-01-05T03:39:43Z", "pgp_uid_selfsig_creation",
     "7A35090F UID self-signature 'Cicada 3301 (845145127)', sigclass 0x13"),
]
for unix, utc, kind, ev in KEY_EVENTS:
    SOURCES.append({
        "unix": unix, "utc": utc, "kind": kind, "label": "key material",
        "provenance_class": "verified", "authorship_proximity": "author_machine",
        "evidence": ev,
        "source": "gpg --list-packets corpus/A-primary-artifacts/krisyotam/pgp/key/"
                  "cicada-3301-public-key.asc (fpr 6D854CD7933322A601C3286D181F01E57A35090F)",
        "retrieved_utc": "2026-08-26",
    })

# Documented-but-not-machine-verified anchors. Kept SEPARATE and ranked below the verified set.
REPORTED = [
    (1325635200, "2012-01-04T00:00:00Z", "puzzle_event_date_only",
     "First 3301 image posted to 4chan /b/. DATE only - no authenticated second exists for it.",
     "KNOWLEDGE.json: timeline (confidence 'documented')"),
    (1326067200, "2012-01-09T00:00:00Z", "puzzle_event_date_only",
     "845145127.com countdown expires, GPS coordinates posted. DATE only.",
     "KNOWLEDGE.json: timeline (confidence 'documented')"),
]
for unix, utc, kind, ev, src in REPORTED:
    SOURCES.append({
        "unix": unix, "utc": utc, "kind": kind, "label": "puzzle event",
        "provenance_class": "reported", "authorship_proximity": "third_party_or_unknown",
        "evidence": ev, "source": src, "retrieved_utc": "2026-08-26",
    })

# --------------------------------------------------------------------- derivations (FIXED)
PROX = {"author_machine": 3, "author_infrastructure": 2, "third_party_or_unknown": 1}
PROVENANCE = {"verified": 3, "reported": 2, "speculated": 1}


def derivations(t):
    """The neighbour set fixed in PREREG.md. Not extended."""
    d = datetime.fromtimestamp(t, UTC)
    out = [
        (t, "exact", 4, "the timestamp itself"),
        (t - 1, "off_by_one", 3, "t-1: off-by-one at the point the number was copied"),
        (t + 1, "off_by_one", 3, "t+1: off-by-one at the point the number was copied"),
        (t - t % 60, "truncate_minute", 2, "t truncated to the minute"),
        (t - t % 3600, "truncate_hour", 2, "t truncated to the hour"),
        (t - t % 86400, "truncate_day", 2, "t truncated to UTC midnight (the date as an epoch)"),
        (int(d.strftime("%Y%m%d")), "date_int", 1, "the UTC date typed as YYYYMMDD"),
        (int(d.strftime("%Y%m%d%H%M%S")), "datetime_int", 1,
         "the UTC datetime typed as YYYYMMDDHHMMSS"),
        (t * 1000, "millis", 1, "t in milliseconds"),
    ]
    return out


cands = {}
for s in SOURCES:
    for value, form, dist, why in derivations(s["unix"]):
        rank_key = (PROVENANCE[s["provenance_class"]], PROX[s["authorship_proximity"]], dist)
        entry = cands.get(value)
        prov = OrderedDict(
            provenance_class=s["provenance_class"],
            authorship_proximity=s["authorship_proximity"],
            derivation=form,
            derivation_note=why,
            from_timestamp_unix=s["unix"],
            from_timestamp_utc=s["utc"],
            from_kind=s["kind"],
            from_label=s["label"],
            evidence=s["evidence"],
            source=s["source"],
            retrieved_utc=s["retrieved_utc"],
        )
        if entry is None:
            cands[value] = {"seed": value, "_rank_key": rank_key, "provenance": [prov]}
        else:
            entry["provenance"].append(prov)
            entry["_rank_key"] = max(entry["_rank_key"], rank_key)

ordered = sorted(cands.values(), key=lambda c: (tuple(-x for x in c["_rank_key"]), c["seed"]))
for i, c in enumerate(ordered, 1):
    pc, pr, dd = c["_rank_key"]
    c_out = OrderedDict(
        rank=i,
        seed=c["seed"],
        tier=("A" if (pc, pr, dd) >= (3, 3, 4) else
              "B" if (pc, pr) == (3, 3) and dd >= 3 else
              "C" if (pc, pr) == (3, 3) else "D"),
        rank_score={"provenance": pc, "authorship_proximity": pr, "derivation_distance": dd},
        n_independent_sources=len(c["provenance"]),
        provenance=c["provenance"][:6],
        provenance_truncated=(len(c["provenance"]) > 6),
    )
    c.clear()
    c.update(c_out)

out = OrderedDict(
    generated_utc=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    lane="round18/L8-provenance",
    gap="corpus/GAPS.md G-09 (timestamps as a dataset)",
    handed_to="L6-offset-marsaglia / any seed lane; and LEDGER.json",
    what_this_is=(
        "A RANKED PRIOR over RNG seeds, not a keyspace and not a claim. Round 8 enumerated every "
        "unix second of 2011-2015 uniformly for 10 generators; these are the seconds a human "
        "demonstrably had in front of them, so they are the seconds to try FIRST if a seed sweep "
        "is ever re-run or extended. This lane ran none of them."
    ),
    what_this_is_not=[
        "Not a cryptanalytic result. No decode was attempted here.",
        "Not evidence about a person. See the confound note below.",
        "Not exclusive: a seed absent from this list is not excluded by its absence.",
    ],
    confound_declared_before_running=(
        "A PGP signature's creation time is an RFC 4880 hashed subpacket taken from the signer's "
        "own clock, so it is settable by the signer. AUDITOR-LOOP-2026-07-28.md used exactly this "
        "to REFUTE the timezone/working-hours biometric built on these timestamps (n=26, "
        "irreproducible), and that refutation stands. It does not weaken this list: a spoofed "
        "timestamp is still a number the author chose and typed, which is the very property that "
        "makes it a plausible srand() argument. Declared in PREREG.md before the run so it could "
        "not be invented afterwards to rescue a result."
    ),
    ranking_rule_fixed_in_prereg=OrderedDict(
        first="provenance_class: verified(3) > reported(2) > speculated(1, unused)",
        second="authorship_proximity: author_machine(3) > author_infrastructure(2) > third_party(1)",
        third="derivation_distance: exact(4) > off-by-one(3) > truncation(2) > reformatting(1)",
        tiers=OrderedDict(
            A="verified + author_machine + exact -- the raw seconds the author's own machine wrote",
            B="verified + author_machine + off-by-one",
            C="verified + author_machine + truncation or reformatting",
            D="anything resting on a reported (not machine-verified) timestamp",
        ),
    ),
    derivation_set_fixed_in_prereg=[f for _, f, _, _ in derivations(0)],
    source_timestamp_count=len(SOURCES),
    source_timestamps_verified=sum(1 for s in SOURCES if s["provenance_class"] == "verified"),
    candidate_count=len(ordered),
    tier_counts={t: sum(1 for c in ordered if c["tier"] == t) for t in "ABCD"},
    not_covered=[
        "Onion / Tor hidden-service POST times: no authenticated source for any of them was "
        "located, so none is included. They would be author_infrastructure proximity if sourced.",
        "4chan and Twitter post times: third-party-recorded, and no archive capture carrying a "
        "verifiable second was retrieved by this lane.",
        "File mtimes inside the held image dumps and the CicadaOS pads: not read here (that is "
        "L1-toolchain's surface).",
        "The mruzuki key's timestamps are deliberately EXCLUDED: nothing ties that key to the "
        "author, so including them would smuggle a speculated link into a ranked prior.",
    ],
    reopens_if=[
        "A seed lane runs tier A and reports which generators and offsets it covered - at which "
        "point tiers B-D become the next bounded increment.",
        "An authenticated onion post time or a dated archive capture is recovered, adding "
        "author_infrastructure entries above the current tier D.",
    ],
    candidates=ordered,
)
(HERE / "TIMESTAMP-SEED-CANDIDATES.json").write_text(json.dumps(out, indent=1))
print("source timestamps:", len(SOURCES), "| candidates:", len(ordered),
      "| tiers:", out["tier_counts"])
print("top 5:", [c["seed"] for c in ordered[:5]])
