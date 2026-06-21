import glob
def realeoi_trail(p):
    d=open(p,'rb').read()
    i=2
    while i<len(d)-1:
        if d[i]!=0xFF: i+=1; continue
        m=d[i+1]
        if m==0xD9: return len(d)-(i+2)  # bytes after first real EOI
        if m in (0xD8,0x01) or 0xD0<=m<=0xD7: i+=2; continue
        if m==0xFF: i+=1; continue
        L=(d[i+2]<<8)|d[i+3]
        if m==0xDA:
            j=i+2+L
            while j<len(d)-1:
                if d[j]==0xFF and d[j+1]!=0 and not(0xD0<=d[j+1]<=0xD7): break
                j+=1
            i=j; continue
        i+=2+L
    return -1
bad=[]
for p in sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/*.jpg")):
    t=realeoi_trail(p)
    if t>32: bad.append((p.split('/')[-1],t))
print("relikd files with >32B trailing after real EOI:", bad if bad else "NONE")
