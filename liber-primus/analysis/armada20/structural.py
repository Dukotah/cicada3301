#!/usr/bin/env python3
# Properly parse JPEG by walking SEGMENT structure (respect length fields, skip scan data)
def parse_jpeg(path):
    with open(path,"rb") as f:
        d=f.read()
    n=len(d)
    if d[:2]!=b"\xff\xd8":
        return ("not jpeg",None,d)
    i=2
    while i < n-1:
        if d[i]!=0xff:
            i+=1; continue
        m=d[i+1]
        if m==0xff:
            i+=1; continue
        if m==0xd9:  # real EOI
            return ("EOI", i+2, d)
        if 0xd0<=m<=0xd7 or m==0x01:  # standalone markers, no length
            i+=2; continue
        if m==0xda:  # SOS: read length then scan to next marker
            seglen=(d[i+2]<<8)|d[i+3]
            i+=2+seglen
            # skip entropy coded data until next real marker (FF xx, xx!=00 and not RSTn)
            while i<n-1:
                if d[i]==0xff:
                    nb=d[i+1]
                    if nb==0x00 or (0xd0<=nb<=0xd7):
                        i+=2; continue
                    break
                i+=1
            continue
        # generic segment with length
        seglen=(d[i+2]<<8)|d[i+3]
        i+=2+seglen
    return ("no EOI found", None, d)

for p in ["/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg",
          "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"]:
    status, end, d = parse_jpeg(p)
    print(p)
    print(f"  status={status} EOI_end={end} filesize={len(d)} trailing_after_real_EOI={len(d)-end if end else 'N/A'}")
    if end and len(d)-end>0:
        tail=d[end:]
        print("  TAIL hex:", tail[:64].hex())
