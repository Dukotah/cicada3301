import json, os, hashlib
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round12/A1/pads"
T={t["path"]:t["sha256"] for t in json.load(open("TARGETS.json")) if t["class"]=="cicadaos_pad"}
f=open(os.path.join(P,"tmp_folly"),'rb').read(); w=open(os.path.join(P,"tmp_wisdom"),'rb').read()
for nm in ("tmp_folly","tmp_wisdom"):
    G.emit({"artifact_path":os.path.join(P,nm),"artifact_sha256":T[os.path.join(P,nm)],
     "tool":"pad cross-comparison (pure python)","tool_version":"G-1.0",
     "command":"cmp tmp_folly tmp_wisdom ; xor","params":{},"exit_code":0,"finding":"HIT",
     "output_excerpt":json.dumps({"claim":"tmp_folly and tmp_wisdom are BYTE-IDENTICAL",
       "len":3368,"sha256":hashlib.sha256(f).hexdigest(),"xor_all_zero":True,
       "entropy":round(G.entropy(f),4)}),
     "output_file":"raw/pad_pairwise.json",
     "note":"Two differently-named CicadaOS pad artifacts hold the same 3368 bytes. If these were intended as distinct one-time pads this is keystream reuse; more likely the extraction emitted one blob twice. Either way it must be resolved before either file is used as an independent pad."})
a=open(os.path.join(P,"DATA__560.00"),'rb').read(); b=open(os.path.join(P,"DATA__560.00.iso-authoritative"),'rb').read()
tail=b[len(a):]
G.savraw("pads_iso_authoritative_tail.bin", tail)
ta,tp,tan=None,None,None
mean=round(G.entropy(tail),4)
G.emit({"artifact_path":os.path.join(P,"DATA__560.00.iso-authoritative"),
  "artifact_sha256":T[os.path.join(P,'DATA__560.00.iso-authoritative')],
  "tool":"pad cross-comparison (pure python)","tool_version":"G-1.0",
  "command":"test whether DATA__560.00 is a prefix of DATA__560.00.iso-authoritative; isolate the delta",
  "params":{},"exit_code":0,"finding":"HIT",
  "output_excerpt":json.dumps({"claim":"DATA__560.00 is an exact byte-prefix of DATA__560.00.iso-authoritative",
    "prefix_len":len(a),"total_len":len(b),"delta_len":len(tail),
    "delta_sha256":hashlib.sha256(tail).hexdigest(),"delta_entropy":mean,
    "delta_head_hex":tail[:64].hex(),"delta_tail_hex":tail[-64:].hex(),
    "delta_printable_frac":round(sum(1 for c in tail if 32<=c<127)/len(tail),4)}),
  "output_file":"raw/pads_iso_authoritative_tail.bin",
  "note":"The non-authoritative copy is a truncation. 1,580,426 bytes of the authoritative pad were absent from the copy previously in use; any analysis run on DATA__560.00 covered only 60.4% of the pad."})
print("delta len",len(tail),"entropy",mean,"sha256",hashlib.sha256(tail).hexdigest())
print("head",tail[:48].hex()); print("printable frac",round(sum(1 for c in tail if 32<=c<127)/len(tail),4))
print("zero runs >=16:", )
# any long zero runs / structure in tail?
import re
zr=[(m.start(),len(m.group())) for m in re.finditer(rb'\x00{16,}', tail)]
print("zero runs>=16:", zr[:10], "count", len(zr))
st=[s.decode() for s in re.findall(rb'[\x20-\x7e]{8,}', tail)]
print("strings>=8 in tail:", len(st), st[:20])
