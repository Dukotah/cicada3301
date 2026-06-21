import sys
def parse(p):
    d=open(p,'rb').read()
    i=0; n=len(d)
    print(p, "len", n)
    if d[:2]!=b'\xff\xd8':
        print("  not jpeg"); return
    i=2
    while i < n-1:
        if d[i]!=0xff:
            i+=1; continue
        m=d[i+1]
        if m==0xd8: print(f"  @{i} SOI"); i+=2; continue
        if m==0xd9: print(f"  @{i} EOI  (bytes after EOI to next marker/end)"); i+=2; continue
        if m in (0x01,) or 0xd0<=m<=0xd7: i+=2; continue
        if m==0xff: i+=1; continue
        if i+4>n: break
        seg=(d[i+2]<<8)|d[i+3]
        name={0xc0:'SOF0',0xc2:'SOF2',0xc4:'DHT',0xdb:'DQT',0xdd:'DRI',0xda:'SOS',0xe0:'APP0',0xe1:'APP1',0xee:'APP14',0xfe:'COM'}.get(m,f'M{m:02x}')
        extra=''
        if m==0xe1: extra=d[i+4:i+14].decode('latin1',errors='replace')
        if m==0xfe: extra=d[i+4:i+4+seg-2].decode('latin1',errors='replace')[:60]
        print(f"  @{i} {name} len={seg} {extra}")
        if m==0xda:
            # scan data until next marker that's not RSTn/FF00
            j=i+2+seg
            while j<n-1:
                if d[j]==0xff and d[j+1]!=0 and not(0xd0<=d[j+1]<=0xd7):
                    break
                j+=1
            print(f"     SOS scan data {j-(i+2+seg)} bytes, next marker @{j} = ff{d[j+1]:02x}")
            i=j; continue
        i+=2+seg
parse(sys.argv[1])
