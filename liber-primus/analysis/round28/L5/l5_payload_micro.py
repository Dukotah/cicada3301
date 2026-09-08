#!/usr/bin/env python3
"""Round 28 / L5 -- payload-micro: the genuinely never-run remainders of E-01/E-02/H-03.

Anti-repeat scope (PREREG.md Amendment 1, 2026-09-08):
  E-01w : 432-bit 2013 modulus over every 54-byte WINDOW of the payload
          (ledger E-01 not_covered (b); the whole-payload grid is round19/C1, closed).
  E-02v : varint (LEB128 + MSB-first base-128) reads of the payload rank-correlated
          against the doublet-gap sequence (round16 ran uint8/u16LE/u16BE only).
  H-03r : the 2012 P.S. digit-string rotate-90/matrix reading (never executed;
          the cookie-XOR half is round16, closed).

Order of operations is fixed by the PREREG: ALL positive controls run FIRST in this
process; a control below 0.90 recovery aborts the lane before any null is recorded.

Matcher functions are copied verbatim in structure from round19/C1/e01_rsa.py so the
windowed cells are adjudicated by the same instrument that closed the whole-payload grid.

    nice -n 15 python3 l5_payload_micro.py
"""
import hashlib
import json
import os
import random
import sys
from math import log2

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # liber-primus/
PP = os.path.join(LP, "analysis", "pp49_51")
C1 = os.path.join(LP, "analysis", "round19", "C1")
CT = os.path.join(LP, "analysis", "seed_sweep", "ct.bin")
PS_TXT = os.path.join(LP, "..", "corpus", "A-primary-artifacts", "cijhho123",
                      "2012", "additional docs", "signed messages",
                      "final message for 2012.txt")

RNG = random.Random(3301)
PERMS = 100_000

# ---------------------------------------------------------------- E-01 matchers
# (structure identical to round19/C1/e01_rsa.py -- same instrument, same tiers)
HASHES = {"sha1": hashlib.sha1, "sha256": hashlib.sha256,
          "sha384": hashlib.sha384, "sha512": hashlib.sha512}
STD_SALT_LENS = [0, 20, 28, 32, 48, 64]
DIGEST_OIDS = {
    "SHA-1":   bytes.fromhex("3021300906052b0e03021a05000414"),
    "SHA-224": bytes.fromhex("302d300d060960864801650304020405001c"),
    "SHA-256": bytes.fromhex("3031300d060960864801650304020105000420"),
    "SHA-384": bytes.fromhex("3041300d060960864801650304020205000430"),
    "SHA-512": bytes.fromhex("3051300d060960864801650304020305000440"),
    "MD5":     bytes.fromhex("3020300c06082a864886f70d020505000410"),
}


def match_v15_type1(block):
    """EMSA-PKCS1-v1_5: 00 01 FF*k (k>=8) 00 <DigestInfo>. strict iff DigestInfo known."""
    if len(block) < 11 or block[0] != 0x00 or block[1] != 0x01:
        return None
    i = 2
    while i < len(block) and block[i] == 0xFF:
        i += 1
    k = i - 2
    if k < 8 or i >= len(block) or block[i] != 0x00:
        return None
    rest = block[i + 1:]
    out = {"scheme": "pkcs1_v15_type1", "ff_bytes": k, "tail_hex": rest[:24].hex(),
           "digest_info": None, "strict": False}
    for name, pfx in DIGEST_OIDS.items():
        if rest[:len(pfx)] == pfx:
            out["digest_info"] = name
            out["strict"] = True
    return out


def match_v15_type2(block):
    """EME-PKCS1-v1_5: 00 02 <>=8 nonzero> 00 <msg>. loose tier only (no strict exists)."""
    if len(block) < 11 or block[0] != 0x00 or block[1] != 0x02:
        return None
    i = 2
    while i < len(block) and block[i] != 0x00:
        i += 1
    if (i - 2) < 8 or i >= len(block):
        return None
    msg = block[i + 1:]
    if not msg:
        return None
    return {"scheme": "pkcs1_v15_type2", "ps_bytes": i - 2, "msg_len": len(msg),
            "msg_hex": msg[:32].hex(), "strict": False}


def _mgf1(seed, length, hf):
    out = b""
    c = 0
    while len(out) < length:
        out += hf(seed + c.to_bytes(4, "big")).digest()
        c += 1
    return out[:length]


def match_pss(block, embits, hname, hf):
    """EMSA-PSS: maskedDB || H || 0xBC; unmasked DB == 00*ps || 01 || salt.
    strict iff ps >= 8 (the round19/C1 zero-FP condition)."""
    emlen = len(block)
    hlen = hf().digest_size
    if emlen < hlen + 2 or block[-1] != 0xBC:
        return None
    maskeddb = block[:emlen - hlen - 1]
    h = block[emlen - hlen - 1:emlen - 1]
    dbmask = _mgf1(h, len(maskeddb), hf)
    db = bytearray(a ^ b for a, b in zip(maskeddb, dbmask))
    nbits = 8 * emlen - embits
    if nbits:
        db[0] &= 0xFF >> nbits
    for slen in STD_SALT_LENS + [hlen]:
        pslen = emlen - hlen - slen - 2
        if pslen < 0:
            continue
        if bytes(db[:pslen]) == b"\x00" * pslen and len(db) > pslen and db[pslen] == 0x01:
            return {"scheme": "pss", "hash": hname, "salt_len": slen,
                    "strict": pslen >= 8}
    return None


def all_matchers(block, embits):
    hits = []
    for m in (match_v15_type1(block), match_v15_type2(block)):
        if m:
            hits.append(m)
    for hname, hf in HASHES.items():
        m = match_pss(block, embits, hname, hf)
        if m:
            hits.append(m)
    return hits


# ------------------------------------------------------------ tiny RSA (control)
def _miller_rabin(n, rounds=40):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = RNG.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _gen_prime(bits):
    while True:
        c = RNG.getrandbits(bits) | (1 << (bits - 1)) | 1
        if _miller_rabin(c):
            return c


def gen_rsa_432():
    while True:
        p = _gen_prime(216)
        q = _gen_prime(216)
        if p == q:
            continue
        n = p * q
        if n.bit_length() != 432:
            continue
        phi = (p - 1) * (q - 1)
        e = 65537
        if phi % e == 0:
            continue
        d = pow(e, -1, phi)
        return n, e, d


def emsa_v15_sha1(msg, emlen=54):
    di = DIGEST_OIDS["SHA-1"] + hashlib.sha1(msg).digest()
    ps = b"\xff" * (emlen - len(di) - 3)
    return b"\x00\x01" + ps + b"\x00" + di


def emsa_pss_sha1(msg, embits=431, slen=20):
    emlen = (embits + 7) // 8  # 54
    hlen = 20
    salt = bytes(RNG.getrandbits(8) for _ in range(slen))
    mhash = hashlib.sha1(msg).digest()
    h = hashlib.sha1(b"\x00" * 8 + mhash + salt).digest()
    ps = b"\x00" * (emlen - slen - hlen - 2)
    db = ps + b"\x01" + salt
    dbmask = _mgf1(h, len(db), hashlib.sha1)
    maskeddb = bytearray(a ^ b for a, b in zip(db, dbmask))
    nbits = 8 * emlen - embits
    if nbits:
        maskeddb[0] &= 0xFF >> nbits
    return bytes(maskeddb) + h + b"\xbc"


# --------------------------------------------------------------- E-01w pipeline
def e01w_scan(payload, n, exps, tag):
    """All 203 54-byte windows x 2 byte orders; pow-mode (s<n) + direct-EM mode."""
    rows = []
    excluded = 0
    evaluated = 0
    strict_hits = []
    for off in range(len(payload) - 54 + 1):
        w = payload[off:off + 54]
        for order, wb in (("be", w), ("rev", w[::-1])):
            # direct-EM reading (no pow)
            for m in all_matchers(wb, 431):
                rec = {"variant": tag, "offset": off, "order": order,
                       "mode": "direct", "e": None, "match": m}
                rows.append(rec)
                if m.get("strict"):
                    strict_hits.append(rec)
            s = int.from_bytes(wb, "big")
            for e in exps:
                if s >= n:
                    excluded += 1
                    continue
                evaluated += 1
                m_int = pow(s, e, n)
                block = m_int.to_bytes(54, "big")
                for m in all_matchers(block, 431):
                    rec = {"variant": tag, "offset": off, "order": order,
                           "mode": "pow", "e": e, "match": m}
                    rows.append(rec)
                    if m.get("strict"):
                        strict_hits.append(rec)
    return {"evaluated_pow": evaluated, "excluded_s_ge_n": excluded,
            "loose_rows": [r for r in rows if not r["match"].get("strict")],
            "strict_hits": strict_hits}


# ---------------------------------------------------------------- E-02v pipeline
def dec_leb128(b):
    vals, cur, shift = [], 0, 0
    for byte in b:
        cur |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
        else:
            vals.append(cur)
            cur, shift = 0, 0
    return vals  # incomplete trailing value dropped


def dec_msb128(b):
    vals, cur = [], 0
    for byte in b:
        cur = (cur << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            vals.append(cur)
            cur = 0
    return vals


def spearman(x, y):
    n = len(x)

    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(x), ranks(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def perm_p(x, y, nperm=PERMS):
    obs = abs(spearman(x, y))
    y2 = list(y)
    ge = 0
    for _ in range(nperm):
        RNG.shuffle(y2)
        if abs(spearman(x, y2)) >= obs:
            ge += 1
    return obs, (ge + 1) / (nperm + 1)


def e02v_test(payload, gaps_by_name, tag):
    out = []
    for encname, dec in (("leb128_fwd", lambda b: dec_leb128(b)),
                         ("leb128_rev", lambda b: dec_leb128(b[::-1])),
                         ("msb128_fwd", lambda b: dec_msb128(b)),
                         ("msb128_rev", lambda b: dec_msb128(b[::-1]))):
        vals = dec(payload)
        for gname, gaps in gaps_by_name.items():
            n_use = min(len(vals), len(gaps))
            row = {"variant": tag, "encoding": encname, "target": gname,
                   "decoded_n": len(vals), "n_used": n_use}
            if n_use < 20:
                row["verdict"] = "undecodable(<20 values)"
                out.append(row)
                continue
            rho = spearman(vals[:n_use], gaps[:n_use])
            row["rho"] = round(rho, 4)
            if abs(rho) > 0.5:
                _, p = perm_p(vals[:n_use], gaps[:n_use])
                row["perm_p"] = p
                row["verdict"] = "HIT" if p < 1e-4 else "gate-cleared-but-p-fails"
            else:
                row["verdict"] = "null"
            out.append(row)
    return out


def enc_leb128(vals):
    b = bytearray()
    for v in vals:
        while True:
            byte = v & 0x7F
            v >>= 7
            if v:
                b.append(byte | 0x80)
            else:
                b.append(byte)
                break
    return bytes(b)


def enc_msb128(vals):
    b = bytearray()
    for v in vals:
        chunks = []
        while True:
            chunks.append(v & 0x7F)
            v >>= 7
            if not v:
                break
        for c in chunks[:0:-1]:
            b.append(c | 0x80)
        b.append(chunks[0])
    return bytes(b)


# ---------------------------------------------------------------- H-03r pipeline
KNOWN_CONSTANTS = [
    # >=8-digit pinned constants (R3). Shorter motifs (3301/1033/761/167/509/503)
    # are report-only statistics, not hit bars -- chance rate too high at 131 digits.
    "1325734783",            # 7A35090F key creation time 2012-01-05
    "845145127",             # uid comment 'Cicada 3301 (845145127)'
    "1231507051321",         # 2012 'first prime' constant
    "36367763ab73783c7af284446c",  # (hex, never matches digits; kept for symmetry)
    "10412790658919985359827898739594318956404425106955675643739226952372682423852959081739834390370374475764863415203423499357108713631",
]


def h03r_readings(lines):
    reads = {}
    ncols = max(len(l) for l in lines)
    for coldir, rowdir, name in ((1, 1, "cols_L2R_top2bot"),
                                 (1, -1, "cols_L2R_bot2top"),
                                 (-1, 1, "cols_R2L_top2bot"),
                                 (-1, -1, "cols_R2L_bot2top")):
        s = []
        cols = range(ncols) if coldir == 1 else range(ncols - 1, -1, -1)
        rows = lines if rowdir == 1 else lines[::-1]
        for c in cols:
            for row in rows:
                if c < len(row):
                    s.append(row[c])
        reads[name] = "".join(s)
    concat = "".join(lines)
    reads["concat_fwd"] = concat
    reads["concat_rev"] = concat[::-1]
    return reads


def pair_ascii_stats(digits):
    """digit pairs 00-99 -> chr; printable = 32..126. Both pair alignments (Amendment 2);
    returns the better fraction and its text."""
    best = (0.0, "")
    for a in (0, 1):
        pairs = [int(digits[i:i + 2]) for i in range(a, len(digits) - 1, 2)]
        if not pairs:
            continue
        printable = [32 <= v <= 126 for v in pairs]
        frac = sum(printable) / len(pairs)
        if frac > best[0]:
            txt = "".join(chr(v) if 32 <= v <= 126 else "." for v in pairs)
            best = (frac, txt)
    return best


def h03r_test(lines, tag):
    out = []
    for name, s in h03r_readings(lines).items():
        frac, txt = pair_ascii_stats(s)
        row = {"block": tag, "reading": name, "len": len(s),
               "pair_ascii_printable": round(frac, 3),
               "pair_ascii_text": txt,
               "n_3301": s.count("3301"), "n_1033": s.count("1033"),
               "is_prime": _miller_rabin(int(s)) if s and s[0] != "0" else
                           _miller_rabin(int(s or "0")),
               "const_match": None, "verdict": "null"}
        for c in KNOWN_CONSTANTS:
            if c.isdigit() and len(c) >= 8 and c in s and c != s:
                row["const_match"] = c
        if s in (KNOWN_CONSTANTS[-1],):
            pass  # the concatenation IS the constant; matching itself is not a hit
        elif row["const_match"]:
            row["verdict"] = "HIT(R3)"
        if frac >= 0.95:  # Amendment 2: bar recalibrated for the digit-pair alphabet
            row["verdict"] = "HIT(R2)"
        out.append(row)
    return out


# ------------------------------------------------------------------- controls
def controls():
    rep = {"E-01w": {}, "E-02v": {}, "H-03r": {}}

    # --- E-01w positive: 10 v1.5-SHA1 plants + 5 PSS plants under a fresh 432-bit key
    n, e, d = gen_rsa_432()
    ok_v15 = 0
    for _ in range(10):
        msg = bytes(RNG.getrandbits(8) for _ in range(32))
        em = emsa_v15_sha1(msg)
        s_int = pow(int.from_bytes(em, "big"), d, n)
        sig = s_int.to_bytes(54, "big")
        off = RNG.randrange(0, 256 - 54 + 1)
        buf = bytearray(RNG.getrandbits(8) for _ in range(256))
        buf[off:off + 54] = sig
        res = e01w_scan(bytes(buf), n, [65537], "plant")
        hits = [h for h in res["strict_hits"]
                if h["mode"] == "pow" and h["match"]["scheme"] == "pkcs1_v15_type1"]
        if any(h["offset"] == off and h["order"] == "be" for h in hits) and len(hits) == 1:
            ok_v15 += 1
    rep["E-01w"]["v15_recovery"] = ok_v15 / 10.0
    ok_pss = 0
    for _ in range(5):
        msg = bytes(RNG.getrandbits(8) for _ in range(32))
        em = emsa_pss_sha1(msg)
        s_int = pow(int.from_bytes(em, "big"), d, n)
        sig = s_int.to_bytes(54, "big")
        off = RNG.randrange(0, 256 - 54 + 1)
        buf = bytearray(RNG.getrandbits(8) for _ in range(256))
        buf[off:off + 54] = sig
        res = e01w_scan(bytes(buf), n, [65537], "plant")
        hits = [h for h in res["strict_hits"]
                if h["mode"] == "pow" and h["match"]["scheme"] == "pss"]
        if any(h["offset"] == off and h["order"] == "be" for h in hits):
            ok_pss += 1
    rep["E-01w"]["pss_recovery"] = ok_pss / 5.0
    # negative: 200 random buffers, require 0 strict
    fp = 0
    for _ in range(200):
        buf = bytes(RNG.getrandbits(8) for _ in range(256))
        fp += len(e01w_scan(buf, n, [65537], "neg")["strict_hits"])
    rep["E-01w"]["neg_strict_hits_200"] = fp

    # --- E-02v positive: real gaps re-encoded, 10 plants across flavours
    ct = open(CT, "rb").read()
    dp = [i for i in range(1, len(ct)) if ct[i] == ct[i - 1]]
    gaps = [dp[i + 1] - dp[i] for i in range(len(dp) - 1)]
    gaps_by = {"gaps85": gaps, "gaps86_lead122": [dp[0]] + gaps}
    ok = 0
    for i in range(10):
        if i % 2 == 0:
            payload = enc_leb128(gaps)[:256]
        else:
            payload = enc_msb128(gaps)[:256]
        rows = e02v_test(payload, gaps_by, "plant")
        if any(r.get("verdict") == "HIT" for r in rows):
            ok += 1
    rep["E-02v"]["recovery"] = ok / 10.0
    # negative: 50 random payloads
    fp = 0
    for _ in range(50):
        payload = bytes(RNG.getrandbits(8) for _ in range(256))
        rows = e02v_test(payload, gaps_by, "neg")
        fp += sum(1 for r in rows if r.get("verdict") == "HIT")
    rep["E-02v"]["neg_hits_50"] = fp

    # --- H-03r positive: 10 blocks whose column reading pair-decodes printable
    ok = 0
    for _ in range(10):
        msg = "".join(RNG.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ ") for _ in range(65))
        digits = "".join("%02d" % ord(c) for c in msg)  # 130 digits, all printable pairs
        digits += str(RNG.randrange(10))                # 131, ragged like the artifact
        # arrange so that cols_L2R_top2bot reproduces `digits`: 3 rows read col-wise
        rows_ = ["", "", ""]
        for i, ch in enumerate(digits):
            rows_[i % 3] += ch
        res = h03r_test(rows_, "plant")
        if any(r["reading"] == "cols_L2R_top2bot" and r["verdict"] == "HIT(R2)"
               for r in res):
            ok += 1
    rep["H-03r"]["recovery"] = ok / 10.0
    fp = 0
    for _ in range(200):
        rows_ = ["".join(str(RNG.randrange(10)) for _ in range(k))
                 for k in (40, 45, 46)]
        res = h03r_test(rows_, "neg")
        fp += sum(1 for r in res if r["verdict"].startswith("HIT"))
    rep["H-03r"]["neg_hits_200"] = fp
    return rep, gaps_by


def main():
    out = {"lane": "round28/L5", "date": "2026-09-08", "controls": None,
           "E-01w": None, "E-02v": None, "H-03r": None}

    print("[controls] running all planted controls FIRST ...")
    ctrl, gaps_by = controls()
    out["controls"] = ctrl
    print(json.dumps(ctrl, indent=1))
    gates = [ctrl["E-01w"]["v15_recovery"] >= 0.90,
             ctrl["E-01w"]["pss_recovery"] >= 0.80,   # 5 plants: 4/5 minimum
             ctrl["E-01w"]["neg_strict_hits_200"] == 0,
             ctrl["E-02v"]["recovery"] >= 0.90,
             ctrl["E-02v"]["neg_hits_50"] == 0,
             ctrl["H-03r"]["recovery"] >= 0.90,
             ctrl["H-03r"]["neg_hits_200"] == 0]
    if not all(gates):
        out["verdict"] = "CONTROL-FAILED -- lane aborted before any null"
        json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
        print("CONTROL FAILED", gates)
        sys.exit(1)
    print("[controls] all gates passed.\n")

    # real 2013 modulus
    moduli = json.load(open(os.path.join(C1, "moduli.json")))
    m2013 = [m for m in moduli["other_moduli"] if m["name"] == "2013_puzzle"][0]
    n2013 = int(m2013["n_hex"], 16)
    assert n2013.bit_length() == 432

    variants = {
        "canon_256": open(os.path.join(PP, "canon_256.bin"), "rb").read(),
        "canon_256_decpref": open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read(),
        "payload_resolved": open(os.path.join(C1, "payload_resolved.bin"), "rb").read(),
    }

    print("[E-01w] windowed 2013-modulus scan ...")
    e01 = {}
    for tag, pl in variants.items():
        r = e01w_scan(pl, n2013, [65537, 3, 17], tag)
        e01[tag] = {"evaluated_pow": r["evaluated_pow"],
                    "excluded_s_ge_n": r["excluded_s_ge_n"],
                    "strict_hits": r["strict_hits"],
                    "loose_count": len(r["loose_rows"]),
                    "loose_rows": r["loose_rows"][:20]}
        print(f"  {tag}: pow evaluated {r['evaluated_pow']}, excluded {r['excluded_s_ge_n']}, "
              f"strict {len(r['strict_hits'])}, loose {len(r['loose_rows'])}")
    out["E-01w"] = e01

    print("[E-02v] varint gap reads ...")
    e02 = []
    for tag, pl in variants.items():
        rows = e02v_test(pl, gaps_by, tag)
        e02.extend(rows)
        for r in rows:
            print(f"  {tag} {r['encoding']} vs {r['target']}: n={r['decoded_n']} "
                  f"rho={r.get('rho')} verdict={r['verdict']}")
    out["E-02v"] = e02

    print("[H-03r] 2012 P.S. rotate-90 ...")
    raw = open(PS_TXT, "rb").read().decode("utf-8", "replace")
    ps_lines = []
    grab = False
    for line in raw.splitlines():
        t = line.strip().rstrip("\\")
        if "P.S." in line:
            grab = True
            t = t.split("P.S.")[1].strip().rstrip("\\")
        if grab and t and all(c.isdigit() for c in t):
            ps_lines.append(t)
        elif grab and ps_lines:
            break
    assert [len(l) for l in ps_lines] == [40, 45, 46], ps_lines
    h03 = h03r_test(ps_lines, "2012_PS")
    out["H-03r"] = {"lines": ps_lines, "rows": h03}
    for r in h03:
        print(f"  {r['reading']}: printable={r['pair_ascii_printable']} "
              f"3301x{r['n_3301']} 1033x{r['n_1033']} prime={r['is_prime']} "
              f"verdict={r['verdict']}")

    hits = ([h for v in e01.values() for h in v["strict_hits"]]
            + [r for r in e02 if r.get("verdict") == "HIT"]
            + [r for r in h03 if r["verdict"].startswith("HIT")])
    out["verdict"] = "FLAGGED-FOR-ORACLE" if hits else "NEGATIVE"
    out["hits"] = hits
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("\nVERDICT:", out["verdict"], f"({len(hits)} hits)")


if __name__ == "__main__":
    main()
