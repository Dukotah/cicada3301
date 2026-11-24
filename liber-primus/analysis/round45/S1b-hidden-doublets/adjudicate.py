"""R45/S1b — unseal and score the frozen blind reads (PREREG §2-3).

Records sha256 of reads_L.txt / reads_P.txt BEFORE opening sealed_*.json. Output: adjudicate_raw.json
Run from anywhere:  PYTHONUTF8=1 python adjudicate.py
"""
import difflib, hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
frozen = {k: sha(os.path.join(HERE, k)) for k in ("reads_L.txt", "reads_P.txt")}
print("frozen read hashes:", frozen)

TR = {r: gp.RUNE_TO_TRANS[r].upper() for r in gp.RUNE_TO_TRANS}
# normalise transliteration variants to the tokens used in the reads
ALIAS = {"Þ": "TH", "IO": "IA", "ING": "NG", "K": "C", "Z": "X", "V": "U", "Q": "C", "EO": "EO"}
def tok(r):
    t = TR[r]
    return ALIAS.get(t, t)
CLS = {"M": "MD", "D": "MD", "M|D": "MD", "TH": "THW", "W": "THW", "TH|W": "THW"}
def cls(t): return CLS.get(t, t)

def parse(fn):
    out = {}
    for line in open(os.path.join(HERE, fn), encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line:
            p = line.split(); out[p[0]] = p[1:]
    return out

RL, RP = parse("reads_L.txt"), parse("reads_P.txt")
SL = json.load(open(os.path.join(HERE, "sealed_lines.json"), encoding="utf-8"))
SP = json.load(open(os.path.join(HERE, "sealed_pairs.json"), encoding="utf-8"))

# ---------------- pass P
P = {"rows": [], "by_kind": {}}
for pid, rec in sorted(SP.items()):
    v = RP[pid]; verdict, r1, r2, conf = v
    a, b = rec["canon"][0], rec["canon"][1]
    canon_same = a == b
    row = {"id": pid, **rec, "canon_tok": [tok(a), tok(b)], "verdict": verdict, "read": [r1, r2],
           "conf": conf, "correct_samediff": (verdict == "SAME") == canon_same}
    P["rows"].append(row)
    k = P["by_kind"].setdefault(rec["kind"], {"n": 0, "correct": 0, "said_same": 0})
    k["n"] += 1; k["correct"] += row["correct_samediff"]; k["said_same"] += verdict == "SAME"
print("PASS P by kind:", json.dumps(P["by_kind"]))
for r in P["rows"]:
    if not r["correct_samediff"]:
        print("  P-miss", r["id"], r["kind"], "t", r["t"], "canon", r["canon_tok"], "read", r["verdict"], r["read"], r["conf"])

# ---------------- pass L
L = {"rows": [], "ctrl_doublets": 0, "ctrl_doublets_read_equal": 0, "glyphs": 0, "agree_exact": 0, "agree_cls": 0}
for lid, rec in sorted(SL.items()):
    can = [tok(r) for r in rec["canon"]]
    rd = RL[lid]
    inserted = [i for i, t in enumerate(rd) if t.startswith("+")]
    rd_clean = [t.lstrip("+") for t in rd]
    sm = difflib.SequenceMatcher(a=[cls(t) for t in rd_clean], b=[cls(t) for t in can], autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    exact = sum(1 for i, j in zip(range(len(rd_clean)), range(len(can))) if False)
    # per-glyph agreement on equal blocks
    ag_e = ag_c = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                ag_c += 1; ag_e += rd_clean[i] == can[j]
    # read-equal adjacent pairs (definite tokens only) vs canon
    req = [i for i in range(len(rd_clean) - 1) if rd_clean[i] == rd_clean[i + 1] and "|" not in rd_clean[i]]
    amb = [i for i in range(len(rd_clean) - 1) if cls(rd_clean[i]) == cls(rd_clean[i + 1]) and "|" in rd_clean[i] + rd_clean[i + 1]]
    cdbl = [j for j in range(len(can) - 1) if rec["canon"][j] == rec["canon"][j + 1]]
    row = {"id": lid, **{k: rec[k] for k in ("kind", "gline", "img", "page", "start", "nseg")},
           "canon_len": len(can), "read_len": len(rd_clean), "inserted_unboxed": inserted,
           "diff_ops": [[t, i1, i2, j1, j2, rd_clean[i1:i2], can[j1:j2]] for t, i1, i2, j1, j2 in ops],
           "read_equal_pairs": req, "ambiguous_class_pairs": amb, "canon_doublets": cdbl,
           "agree_exact": ag_e, "agree_class": ag_c}
    L["rows"].append(row)
    L["glyphs"] += len(can); L["agree_exact"] += ag_e; L["agree_cls"] += ag_c
    if rec["kind"] == "C":
        L["ctrl_doublets"] += len(cdbl)
        # map canon doublet j to read index via opcodes
        for j in cdbl:
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "equal" and j1 <= j and j + 1 < j2:
                    i = i1 + (j - j1)
                    L["ctrl_doublets_read_equal"] += cls(rd_clean[i]) == cls(rd_clean[i + 1])
    print(f"{lid} {rec['kind']} gl{rec['gline']} start{rec['start']} len{len(can)} read{len(rd_clean)} "
          f"ops={[(t, rd_clean[i1:i2], can[j1:j2]) for t, i1, i2, j1, j2 in ops]} req={req} amb={amb} cdbl={cdbl}")
print("PASS L glyphs", L["glyphs"], "class-agree", L["agree_cls"], "exact-agree", L["agree_exact"],
      "ctrl doublets", L["ctrl_doublets"], "read equal", L["ctrl_doublets_read_equal"])
json.dump({"frozen_read_sha256": frozen, "P": P, "L": L},
          open(os.path.join(HERE, "adjudicate_raw.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
