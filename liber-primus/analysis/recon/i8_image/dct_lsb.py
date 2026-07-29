"""
Baseline-JPEG DCT-coefficient LSB extractor (pure Python, no external binary).

WHY: prior stego work (analysis/stego/STEGO-VERDICT.md) declared DCT-domain stego
"NOT testable here (needs a binary)". That is false for BASELINE JPEGs -- the
quantized DCT coefficients are recoverable with a from-scratch Huffman decoder.
OutGuess/jsteg hide payload in the LSBs of NONZERO AC coefficients. This decodes
every MCU, collects quantized coefficients, and tests their LSB stream:
  - jsteg model: LSB of every nonzero AC coeff, in scan (zig-zag) order.
  - outguess model: same pool, but OutGuess pseudo-randomly permutes; if a payload
    exists, the LSB pool is still ~50/50 and (post-key) high-entropy -- BUT a jsteg
    or naive embed leaves a readable prefix. We test both raw and byte-packed.

Signal we look for (control-beating): a printable-ASCII / PGP / base64 / gzip /
low-entropy structured prefix in the packed LSB stream. Null = LSB stream is
statistically indistinguishable from a clean JPEG's coefficient LSBs.

Baseline only (SOF0), single scan, no restart-interval handling beyond RSTn skip.
"""
import sys, struct, math, os, json
from collections import Counter

ZIGZAG = [
 0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,
 35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63]

def build_huff(counts, symbols):
    # counts: 16 ints (num codes of each length 1..16), symbols: flat list
    table = {}
    code = 0; k = 0
    for length in range(1, 17):
        for _ in range(counts[length-1]):
            table[(length, code)] = symbols[k]; k += 1; code += 1
        code <<= 1
    return table

class BitReader:
    def __init__(self, data):
        self.data = data; self.pos = 0; self.bits = 0; self.nbits = 0
    def _fill(self):
        while self.nbits <= 24 and self.pos < len(self.data):
            b = self.data[self.pos]; self.pos += 1
            if b == 0xFF:
                nb = self.data[self.pos] if self.pos < len(self.data) else 0
                if nb == 0x00:
                    self.pos += 1
                elif 0xD0 <= nb <= 0xD7:
                    self.pos += 1; continue  # RST marker inside entropy -> skip
                else:
                    # real marker: stop feeding, treat as end of entropy
                    self.pos -= 1
                    b = 0  # pad
                    self.bits = (self.bits << 8) | b; self.nbits += 8
                    return
            self.bits = (self.bits << 8) | b; self.nbits += 8
    def read_bit(self):
        if self.nbits == 0: self._fill()
        if self.nbits == 0: return 0
        self.nbits -= 1
        return (self.bits >> self.nbits) & 1
    def decode(self, table):
        code = 0
        for length in range(1, 17):
            code = (code << 1) | self.read_bit()
            if (length, code) in table:
                return table[(length, code)]
        return 0
    def receive_extend(self, s):
        if s == 0: return 0
        v = 0
        for _ in range(s): v = (v << 1) | self.read_bit()
        if v < (1 << (s-1)): v -= (1 << s) - 1
        return v

def parse(data):
    i = 2
    qt = {}; huff_dc = {}; huff_ac = {}
    comps = []; W = H = 0
    restart = 0
    while i < len(data)-1:
        if data[i] != 0xFF: i += 1; continue
        m = data[i+1]
        if m == 0xD9: break
        if m == 0xD8 or 0xD0 <= m <= 0xD7:
            i += 2; continue
        ln = struct.unpack(">H", data[i+2:i+4])[0]
        seg = data[i+4:i+2+ln]
        if m == 0xDB:  # DQT
            p = 0
            while p < len(seg):
                pq_tq = seg[p]; tq = pq_tq & 0x0F; prec = pq_tq >> 4; p += 1
                n = 64 * (2 if prec else 1); p += n
        elif m == 0xC4:  # DHT
            p = 0
            while p < len(seg):
                tc_th = seg[p]; tc = tc_th >> 4; th = tc_th & 0x0F; p += 1
                counts = list(seg[p:p+16]); p += 16
                total = sum(counts)
                symbols = list(seg[p:p+total]); p += total
                t = build_huff(counts, symbols)
                (huff_ac if tc else huff_dc)[th] = t
        elif m == 0xC0:  # SOF0 baseline
            H = struct.unpack(">H", seg[1:3])[0]
            W = struct.unpack(">H", seg[3:5])[0]
            nc = seg[5]; p = 6
            for _ in range(nc):
                cid = seg[p]; hv = seg[p+1]; tq = seg[p+2]
                comps.append({"id": cid, "h": hv>>4, "v": hv&0x0F, "tq": tq}); p += 3
        elif m == 0xDD:  # DRI
            restart = struct.unpack(">H", seg[0:2])[0]
        elif m == 0xDA:  # SOS
            ns = seg[0]; p = 1
            scan = []
            for _ in range(ns):
                cs = seg[p]; td_ta = seg[p+1]; p += 2
                scan.append({"id": cs, "td": td_ta>>4, "ta": td_ta&0x0F})
            entropy_start = i + 2 + ln
            return dict(W=W,H=H,comps=comps,scan=scan,huff_dc=huff_dc,huff_ac=huff_ac,
                        restart=restart, entropy=data[entropy_start:])
        i += 2 + ln
    return None

def decode_coeffs(info, max_mcus=None):
    """Return list of nonzero-AC-coefficient LSBs in scan order (jsteg pool)."""
    comps = info["comps"]; scan = info["scan"]
    hmax = max(c["h"] for c in comps); vmax = max(c["v"] for c in comps)
    mcux = (info["W"] + 8*hmax - 1)//(8*hmax)
    mcuy = (info["H"] + 8*vmax - 1)//(8*vmax)
    total_mcu = mcux*mcuy
    if max_mcus: total_mcu = min(total_mcu, max_mcus)
    br = BitReader(info["entropy"])
    pred = {c["id"]: 0 for c in comps}
    scan_by_id = {s["id"]: s for s in scan}
    ac_lsbs = []   # jsteg: LSB of every nonzero AC coeff
    all_ac_nonzero = 0
    restart = info["restart"]; mcu_count = 0
    for my in range(mcuy):
        for mx in range(mcux):
            if max_mcus and mcu_count >= max_mcus:
                return ac_lsbs, all_ac_nonzero, total_mcu
            for c in comps:
                sc = scan_by_id[c["id"]]
                dctab = info["huff_dc"][sc["td"]]; actab = info["huff_ac"][sc["ta"]]
                for by in range(c["v"]):
                    for bx in range(c["h"]):
                        # DC
                        t = br.decode(dctab)
                        diff = br.receive_extend(t)
                        pred[c["id"]] += diff
                        # AC
                        k = 1
                        while k < 64:
                            rs = br.decode(actab)
                            r = rs >> 4; s = rs & 0x0F
                            if s == 0:
                                if r == 15: k += 16; continue
                                break  # EOB
                            k += r
                            if k >= 64: break
                            coeff = br.receive_extend(s)
                            if coeff != 0:
                                ac_lsbs.append(coeff & 1)
                                all_ac_nonzero += 1
                            k += 1
            mcu_count += 1
            if restart and mcu_count % restart == 0:
                # align + skip handled by BitReader RST skip; reset predictors
                br.nbits = 0; br.bits = 0
                for cid in pred: pred[cid] = 0
    return ac_lsbs, all_ac_nonzero, total_mcu

def entropy_bytes(b):
    if not b: return 0.0
    c = Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def analyze(lsbs):
    # pack bits MSB-first into bytes
    n = len(lsbs)//8
    out = bytearray()
    for i in range(n):
        byte = 0
        for j in range(8): byte = (byte<<1) | lsbs[i*8+j]
        out.append(byte)
    ones = sum(lsbs); frac1 = ones/len(lsbs) if lsbs else 0
    # chi-square vs 50/50
    exp = len(lsbs)/2
    chi = ((ones-exp)**2/exp + ((len(lsbs)-ones)-exp)**2/exp) if lsbs else 0
    prefix = bytes(out[:512])
    printable = sum(32<=x<127 for x in prefix)/len(prefix) if prefix else 0
    return {
        "n_lsb": len(lsbs), "frac_ones": round(frac1,5), "chi2_vs_uniform": round(chi,2),
        "packed_entropy_first4k": round(entropy_bytes(bytes(out[:4096])),4),
        "printable_frac_first512": round(printable,4),
        "ascii_preview_128": bytes(out[:128]).decode("latin1","replace"),
        "hex_preview_48": bytes(out[:48]).hex(),
        "has_pgp": b"BEGIN" in bytes(out[:4096]),
        "has_gzip": bytes(out[:3])==b"\x1f\x8b\x08",
        "has_zip": bytes(out[:4])==b"PK\x03\x04",
    }

def main():
    args = sys.argv[1:]
    cap = None
    if args and args[0].startswith("--cap="):
        cap = int(args[0].split("=")[1]); args = args[1:]
    files = args
    results = {}
    for f in files:
        data = open(f,"rb").read()
        info = parse(data)
        if not info:
            results[os.path.basename(f)] = {"error":"parse failed / not baseline"}
            continue
        lsbs, nz, tmcu = decode_coeffs(info, max_mcus=cap)
        a = analyze(lsbs)
        a["total_mcu"] = tmcu; a["nonzero_ac"] = nz
        results[os.path.basename(f)] = a
        print(f"{os.path.basename(f)}: nzAC={nz} frac1={a['frac_ones']} chi2={a['chi2_vs_uniform']} "
              f"printable512={a['printable_frac_first512']} pgp={a['has_pgp']} preview={a['ascii_preview_128'][:40]!r}",
              flush=True)
    json.dump(results, open("liber-primus/analysis/recon/i8_image/dct_lsb_results.json","w"), indent=1)

if __name__=="__main__":
    main()
