import hashlib, collections, math
def trail(p):
    d=open(p,'rb').read()
    i=d.rfind(b'\xff\xd9')
    return d, d[i+2:]
for p in ["/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg",
          "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg"]:
    d,t=trail(p)
    print(p)
    print("  filelen",len(d),"trail",len(t),"md5",hashlib.md5(t).hexdigest())
    # entropy
    c=collections.Counter(t); ent=-sum((n/len(t))*math.log2(n/len(t)) for n in c.values())
    print("  entropy bits/byte",round(ent,3),"first16",t[:16].hex())
    # count FFD9 occurrences in whole file
    print("  num FFD9 in file", d.count(b'\xff\xd9'), "num FFD8", d.count(b'\xff\xd8'))
# are the two trailers identical?
_,t1=trail("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg")
_,t2=trail("/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg")
print("trailers identical:", t1==t2)
# Is trailer itself a JPEG/structured? check for markers
print("trailer starts with JPEG?", t1[:2]==b'\xff\xd8', "PNG?", t1[:4]==b'\x89PNG')
