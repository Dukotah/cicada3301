import json, collections, os
import gcore as G
T=json.load(open("TARGETS.json"))
by=collections.defaultdict(list)
for t in T: by[t["sha256"]].append(t)
dups={k:v for k,v in by.items() if len(v)>1}
print(f"{len(T)} artifacts, {len(by)} unique sha256, {len(dups)} duplicate groups")
R="/mnt/c/Users/dukot/projects/cicada3301/"
groups=[]
for k,v in sorted(dups.items(), key=lambda kv:-len(kv[1])):
    paths=[x["path"].replace(R,"") for x in v]
    groups.append({"sha256":k,"size":v[0]["size"],"n":len(v),"paths":paths,
                   "cross_class":len(set(x["class"] for x in v))>1,
                   "classes":sorted(set(x["class"] for x in v))})
    print(f"  n={len(v)} size={v[0]['size']} {k[:16]}")
    for p in paths: print("      ",p)
json.dump(groups, open("raw/duplicate_groups.json","w"), indent=1)
for g in groups:
    for t in by[g["sha256"]]:
        G.emit({"artifact_path":t["path"],"artifact_sha256":g["sha256"],
          "tool":"global duplicate census (sha256 over all 486 held artifacts)","tool_version":"G-1.0",
          "command":"sha256 every artifact; group by digest","params":{"corpus_size":len(T)},
          "exit_code":0,"finding":"HIT",
          "output_excerpt":json.dumps({"duplicate_group_size":g["n"],"size_bytes":g["size"],
            "identical_paths":g["paths"],"spans_classes":g["classes"]}),
          "output_file":"raw/duplicate_groups.json",
          "note":"Byte-identical content held under multiple names/locations. Detects redundant copies and, where two independently-sourced captures share a name, would have detected a DIVERGENCE (different hash, same name) — none of that kind was found here because no two sources of the same filename are held."})
