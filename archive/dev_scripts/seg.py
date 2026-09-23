from an import *
TOL=5.0
grp={}; gbox=[]; g=-1
kg=[k for k,o in enumerate(d) if o[0]=='SM_VK_Gatehouse_Block_inst'][0]
kb=[k for k,o in enumerate(d) if base(o[0]).startswith('Bridge_Stone')][0]
for k,o in enumerate(d):
    c=cat(o[0])
    if c in ("VEG","TREE") or "LipGrass" in o[0]: continue
    if c=='FORT' or kg<=k<kb: grp[o[0]]='FORT'; continue
    x,y=o[2],o[3]
    if g>=0:
        b=gbox[g]
        if b[0]-TOL<=x<=b[1]+TOL and b[2]-TOL<=y<=b[3]+TOL:
            b[0]=min(b[0],x);b[1]=max(b[1],x);b[2]=min(b[2],y);b[3]=max(b[3],y); grp[o[0]]=g; continue
    g+=1; gbox.append([x,x,y,y,k]); grp[o[0]]=g
