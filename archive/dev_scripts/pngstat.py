import zlib,struct,sys
def load(p):
    d=open(p,'rb').read(); i=8; idat=b''
    while i<len(d):
        L,=struct.unpack('>I',d[i:i+4]); t=d[i+4:i+8]; c=d[i+8:i+8+L]; i+=12+L
        if t==b'IHDR': w,h,bd,ct=struct.unpack('>IIBB',c[:10])
        elif t==b'IDAT': idat+=c
    raw=zlib.decompress(idat)
    ch={2:3,6:4,0:1,4:2}[ct]; bpp=ch*bd//8; stride=w*bpp
    out=[]; prev=bytearray(stride); pos=0
    for y in range(h):
        f=raw[pos]; line=bytearray(raw[pos+1:pos+1+stride]); pos+=1+stride
        if f==1:
            for x in range(bpp,stride): line[x]=(line[x]+line[x-bpp])&255
        elif f==2:
            for x in range(stride): line[x]=(line[x]+prev[x])&255
        elif f==3:
            for x in range(stride): line[x]=(line[x]+(((line[x-bpp] if x>=bpp else 0)+prev[x])>>1))&255
        elif f==4:
            for x in range(stride):
                a=line[x-bpp] if x>=bpp else 0; b=prev[x]; c=prev[x-bpp] if x>=bpp else 0
                pa=abs(b-c); pb=abs(a-c); pc=abs(a+b-2*c)
                pr=a if pa<=pb and pa<=pc else (b if pb<=pc else c)
                line[x]=(line[x]+pr)&255
        out.append(bytes(line)); prev=line
    return w,h,bd,ch,out
base=sys.argv[1]
w,h,bd,ch,bc=load(base+'_BC.png'); _,_,bdh,chh,hh=load(base+'_H.png')
print('BC',w,h,bd,ch,'H',bdh,chh)
step=2
sm=[0,0,0];sn=0;mm=[0,0,0];mn=0;lums=[]
for y in range(0,h,step):
    r=bc[y]; q=hh[y]
    for x in range(0,w,step):
        hv=q[x*chh*(bdh//8)]/255.0
        px=[r[x*ch*(bd//8)+k*(bd//8)] for k in range(3)]
        if hv<0.25:
            mn+=1
            for k in range(3): mm[k]+=px[k]
        else:
            sn+=1
            for k in range(3): sm[k]+=px[k]
            lums.append(0.2126*px[0]+0.7152*px[1]+0.0722*px[2])
tot=sn+mn
print('mortar frac %.3f'%(mn/tot))
print('stone mean',[round(v/sn) for v in sm],'mortar mean',[round(v/mn) for v in mm])
print('all mean',[round((sm[k]+mm[k])/tot) for k in range(3)])
lums.sort(); n=len(lums)
print('stone lum p5 p50 p95',round(lums[n//20]),round(lums[n//2]),round(lums[19*n//20]))
