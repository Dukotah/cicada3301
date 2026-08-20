import json, collections
A=json.load(open("raw/lp_jpeg_segments.json"))
key=lambda n:int(n[1:-4])
rows={}
for n,r in A.items():
    rows[n]={"ncomp":r["sof"]["ncomp"],"ndqt":len(r["dqt"]),
             "dqt_sha1s":[d["sha1"] for d in r["dqt"]],"size":r["size"]}
gray=sorted([n for n in rows if rows[n]["ncomp"]==1], key=key)
col =sorted([n for n in rows if rows[n]["ncomp"]==3], key=key)
print("GRAYSCALE(ncomp=1):",len(gray),[key(n) for n in gray])
print("COLOUR(ncomp=3):",len(col),[key(n) for n in col])
print()
print("gray dqt sha1s uniq:", set(tuple(rows[n]["dqt_sha1s"]) for n in gray))
print("col  dqt sha1s uniq:", set(tuple(rows[n]["dqt_sha1s"]) for n in col))
# is luma table identical between the two groups?
lg=set(rows[n]["dqt_sha1s"][0] for n in gray); lc=set(rows[n]["dqt_sha1s"][0] for n in col)
print("luma table identical across ALL 56:", lg==lc, lg, lc)
# print actual luma table
print("luma DQT vals:", A[gray[0]]["dqt"][0]["vals"])
print("chroma DQT vals:", A[col[0]]["dqt"][1]["vals"] if len(A[col[0]]["dqt"])>1 else None)
json.dump({"grayscale_pages":[key(n) for n in gray],"colour_pages":[key(n) for n in col],
  "luma_dqt_sha1":list(lg)[0],"identical_luma_all56":lg==lc,
  "luma_vals":A[gray[0]]["dqt"][0]["vals"],
  "chroma_vals":A[col[0]]["dqt"][1]["vals"] if len(A[col[0]]["dqt"])>1 else None},
  open("raw/lp_dqt_partition.json","w"), indent=1)
