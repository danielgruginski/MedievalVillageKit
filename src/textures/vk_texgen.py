
def facets(S,seed,fmin=5,fmax=48,amp=1.0):
    """broad chiselled facets: creases where low-freq noise crosses zero"""
    return (-np.abs(fbm(S,3.0,seed,fmin=fmin,fmax=fmax))*amp).astype(f32)
def gen_stone(S=1024,seed=9,tile=3.0,depth=0.05):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.006)%1; Y=(y+fbm(S,3.5,seed+2)*0.005)%1
    rows=rng.uniform(0.12,0.27,6); rows/=rows.sum(); rcum=np.concatenate([[0],np.cumsum(rows)])
    ri=np.clip(np.searchsorted(rcum,Y,side="right")-1,0,len(rows)-1)
    dist=np.zeros((S,S),f32); sid=np.zeros((S,S),np.int32); cu=np.zeros((S,S),f32); cv=np.zeros((S,S),f32)
    rad=40.0; nid=0
    for r in range(len(rows)):
        m=ri==r
        widths=rng.uniform(0.16,0.42,12); k=1
        while widths[:k].sum()<1: k+=1
        widths=widths[:k]; widths/=widths.sum()
        wc=np.concatenate([[0],np.cumsum(widths)]); off=rng.uniform(0,1)
        xs=(X[m]+off)%1; si=np.clip(np.searchsorted(wc,xs,side="right")-1,0,len(widths)-1)
        u=(xs-wc[si])/widths[si]; v=(Y[m]-rcum[r])/rows[r]
        split=rng.random(len(widths))<0.35; sp=split[si]
        v2=np.where(sp,np.where(v<0.5,v*2,(v-0.5)*2),v); hsc=np.where(sp,0.5,1.0)
        dx=np.minimum(u,1-u)*widths[si]*S; dy=np.minimum(v2,1-v2)*rows[r]*S*hsc
        qx=np.maximum(rad-dx,0); qy=np.maximum(rad-dy,0)
        d=np.minimum(dx,dy); c=(qx>0)&(qy>0); d=np.where(c,rad-np.hypot(qx,qy),d)
        dist[m]=d; sub=np.where(sp&(v>=0.5),1,0)
        sid[m]=nid+si*2+sub; cu[m]=u-0.5; cv[m]=v2-0.5
        nid+=len(widths)*2
    en=fbm(S,2.6,seed+3,fmin=4,fmax=60)*4.5
    d=dist+en; gap=6.5
    mask=smooth(gap,gap+2.0,d)
    prof=smooth(gap,gap+46,d)**0.5
    tv=rng.uniform(-1,1,(nid,2)).astype(f32)
    tilt=tv[sid,0]*cu*0.22+tv[sid,1]*cv*0.18
    dome=1-np.clip(np.abs(cu)*2,0,1)**2*0.15-np.clip(np.abs(cv)*2,0,1)**2*0.22
    fac=facets(S,seed+5,6,40,0.10)+facets(S,seed+12,14,90,0.04)
    grain=fbm(S,1.6,seed+13,fmin=120)*0.006
    stone_h=0.36+0.5*prof*dome+tilt*prof+fac*prof+grain
    mortar_h=0.09+0.02*fbm(S,2.0,seed+6,fmin=20,fmax=200)
    h=blur(np.clip(mask*stone_h+(1-mask)*mortar_h,0,1),0.8)
    pal=np.array([(0.66,0.60,0.50),(0.56,0.53,0.48),(0.70,0.62,0.50),(0.52,0.50,0.47),(0.63,0.55,0.45),(0.60,0.58,0.54),(0.58,0.52,0.44)],f32)
    pid=rng.integers(0,len(pal),nid); tint=rng.uniform(0.9,1.08,nid).astype(f32)
    base=pal[pid[sid]]*tint[sid][...,None]
    light=painted_light(normal_from_height(blur(h,2.5),depth*3.0,tile))
    mott=fbm(S,2.6,seed+7,fmin=3,fmax=80)*0.05
    col=base*(0.76+0.36*light[...,None]+mott[...,None])
    rim=smooth(gap+0.5,gap+4,d)-smooth(gap+4,gap+12,d)
    col=col+0.06*rim[...,None]
    lich=smooth(1.25,1.9,fbm(S,2.8,seed+9,fmin=3))*mask*smooth(-0.4,0.8,fbm(S,2.2,seed+10,fmin=20))
    col=col*(1-0.5*lich[...,None])+np.array([0.50,0.56,0.33],f32)*0.5*lich[...,None]
    mortar=np.array([0.26,0.22,0.18],f32)*(1+mott[...,None])
    col=col*mask[...,None]+mortar*(1-mask[...,None])
    rough=np.clip(0.8+0.05*fbm(S,2.4,seed+11,fmin=6)+0.14*(1-mask)+0.06*lich,0,1)
    PBR_SETS["T_VK_Stone"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Stone",col,h,rough,depth,tile)
def gen_ashlar(S=1024,seed=13,tile=2.5,depth=0.03):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.002)%1; Y=(y+fbm(S,3.5,seed+2)*0.002)%1
    nrow=5; row=np.minimum((Y*nrow).astype(int),nrow-1); v=(Y*nrow)%1
    blocks=np.array([3,4,3,4,3]); offs=rng.uniform(0,1,nrow)
    nb=blocks[row]; xo=(X+offs[row])%1; c=np.minimum((xo*nb).astype(int),nb-1); u=(xo*nb)%1
    d=np.minimum(np.minimum(u,1-u)*S/nb,np.minimum(v,1-v)*S/nrow)
    d=d+fbm(S,2.6,seed+3,fmin=6,fmax=80)*1.8; gap=3.0
    mask=smooth(gap,gap+1.5,d); cham=smooth(gap,gap+16,d)
    sid=row*8+c; tv=rng.uniform(-1,1,(nrow*8,2)).astype(f32)
    tool=np.sin(2*np.pi*(146*x+37*y)).astype(f32)
    chip=smooth(1.4,1.9,fbm(S,2.6,seed+5,fmin=6,fmax=60))*(1-smooth(gap+2,gap+26,d))
    hs=0.45+0.42*cham+(tv[sid,0]*(u-0.5)+tv[sid,1]*(v-0.5))*0.08*cham+0.008*tool*cham+facets(S,seed+4,6,50,0.05)*cham-0.3*chip
    h=blur(np.clip(mask*hs+(1-mask)*0.12,0,1),0.7)
    val=rng.uniform(0.9,1.07,nrow*8).astype(f32); warm=rng.uniform(-1,1,nrow*8).astype(f32)
    base=np.array([0.74,0.70,0.62],f32)*val[sid][...,None]*(1+warm[sid][...,None]*np.array([0.025,0.0,-0.03],f32))
    light=painted_light(normal_from_height(blur(h,2.0),depth*3,tile))
    mott=fbm(S,2.6,seed+6,fmin=3,fmax=90)*0.045
    col=base*(0.8+0.3*light[...,None]+mott[...,None])
    col=col*mask[...,None]+np.array([0.36,0.32,0.28],f32)*(1-mask[...,None])
    stain=smooth(0.8,2.2,fbm(S,2.0,seed+8,fmin=2,ay=5))
    col=col*(1-0.12*stain[...,None])
    rough=np.clip(0.8+0.05*fbm(S,2.4,seed+9,fmin=6)+0.12*(1-mask),0,1)
    PBR_SETS["T_VK_Ashlar"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Ashlar",col,h,rough,depth,tile)
def gen_plaster(S=1024,seed=21,tile=1.5,depth=0.02,patches=False):
    rng=np.random.default_rng(seed); x,y=grid(S)
    lumps=fbm(S,3.2,seed,fmin=2); strokes=fbm(S,2.8,seed+1,fmin=3,fmax=60,ax=3.5)
    hp=0.62+0.10*lumps+0.05*strokes+0.004*fbm(S,1.5,seed+2,fmin=150)
    # hairline cracks: branching random walks
    crack=draw_segments(S,crack_segments(S,rng,n=2,steps=(12,26),step_px=(4,8),w0=1.2,branch=0.05))*0.6   # few faint cracks: repeats stay unnoticed
    # a few larger patches of fallen plaster showing brick
    pm=fbm(S,3.6,seed+4,fmin=1.5)+fbm(S,2.6,seed+5,fmin=8,fmax=60)*0.10
    patch=smooth(2.25,2.32,pm)*patches     # off by default: fallen-plaster patches read as a repeating decal
    rimz=smooth(2.1,2.25,pm)*(1-patch)*patches
    nr=21; nbk=6
    br=(y*nr).astype(int); bv=(y*nr)%1; bxo=(x*nbk+0.5*(br%2))%nbk; bci=bxo.astype(int); bu=bxo%1
    bd=np.minimum(np.minimum(bu,1-bu)*S/nbk,np.minimum(bv,1-bv)*S/nr)
    bmask=smooth(2.0,3.5,bd); bprof=smooth(2,10,bd)
    hb=0.2+0.16*bmask*bprof
    h=hp*(1-patch)+hb*patch-0.2*crack*(1-patch)+0.03*rimz
    h=blur(np.clip(h,0,1),0.7)
    base=np.array([0.93,0.85,0.67],f32)
    col=base*(1+0.045*lumps[...,None])
    blot=smooth(0.2,1.8,fbm(S,3.2,seed+6,fmin=1.5))
    col=col*(1-0.3*blot[...,None])+np.array([0.88,0.76,0.56],f32)*0.3*blot[...,None]
    hi=smooth(0.5,2.0,fbm(S,3.2,seed+14,fmin=1.5))
    col=col*(1-0.25*hi[...,None])+np.array([0.95,0.91,0.80],f32)*0.25*hi[...,None]
    streak=smooth(1.3,2.6,fbm(S,3.0,seed+7,fmin=2,fmax=60,ay=6))
    col=col*(1-0.05*streak[...,None])
    bid=br*nbk+bci; bpal=np.array([(0.60,0.33,0.22),(0.52,0.29,0.20),(0.64,0.40,0.27),(0.56,0.36,0.25)],f32)
    bcol=bpal[(bid*7)%4]*(0.88+0.2*bprof[...,None])
    bcol=bcol*bmask[...,None]+np.array([0.62,0.58,0.52],f32)*(1-bmask[...,None])
    col=col*(1-patch[...,None])+bcol*patch[...,None]
    col=col*(1-0.12*rimz[...,None])
    col=col*(1-0.5*crack[...,None]*(1-patch[...,None]))
    rough=np.clip(0.92-0.05*patch+0.03*fbm(S,2.4,seed+8,fmin=6),0,1)
    PBR_SETS["T_VK_Plaster"]=dict(depth=depth,tile=tile)
    ao=cavity_ao(blur(h,2.5),radii=(6,24),k=(1.5,1.0),floor=0.5)
    ao=np.minimum(ao,1-0.6*crack*(1-patch))
    return write_set("T_VK_Plaster",col,h,rough,depth,tile,ao=ao,ao_in_albedo=0.35)

def gen_wood(S=1024,seed=41,tile=1.6,depth=0.022):
    rng=np.random.default_rng(seed); x,y=grid(S)
    warp=fbm(S,3.2,seed,fmin=1,ax=5)*0.035
    rings=np.sin(2*np.pi*(y*8+warp*4+fbm(S,2.8,seed+1,fmin=1,ax=7)*0.1)).astype(f32)
    fib=fbm(S,2.2,seed+2,fmin=4,fmax=90,ax=10)
    fib2=fbm(S,1.8,seed+3,fmin=20,fmax=200,ax=16)
    h=0.55+0.10*rings+0.08*fib+0.015*fib2
    # cracks along the grain (random walks biased to the x axis)
    cr=draw_segments(S,crack_segments(S,rng,n=7,steps=(20,45),step_px=(8,14),w0=2.6,branch=0.04,dirbias=0.0,jit=0.12))
    h-=0.35*cr
    # knots
    kn=np.zeros((S,S),f32); knr=np.zeros((S,S),f32)
    for kx,ky in rng.uniform(0,1,(3,2)):
        dx=((x-kx+0.5)%1-0.5)*2.4; dy=((y-ky+0.5)%1-0.5)*7.0
        d=np.hypot(dx,dy); kn=np.maximum(kn,np.exp(-(d/0.035)**2)); knr+=np.sin(d*150)*np.exp(-(d/0.1)**2)
    gl=np.abs(np.sin(2*np.pi*(y*13+warp*6+fbm(S,3.0,seed+6,fmin=1,ax=8)*0.08)))
    gline=(1-smooth(0.02,0.07,gl))*smooth(-0.3,0.6,fbm(S,2.6,seed+7,fmin=2,ay=6))
    h+=0.05*knr-0.12*kn-0.06*gline
    h=blur(np.clip(h,0,1),0.6)
    lum=0.55+0.06*rings+0.07*fib+0.02*fib2+0.05*knr-0.3*kn-0.16*gline
    lum=np.clip(lum,0.1,1)[...,None]
    dark=np.array([0.13,0.075,0.045],f32); mid=np.array([0.32,0.20,0.115],f32); light=np.array([0.50,0.35,0.21],f32)
    col=np.where(lum<0.6,dark+(mid-dark)*(lum/0.6),mid+(light-mid)*((lum-0.6)/0.4))
    col*= (0.93+0.08*fbm(S,3.0,seed+4,fmin=1.5))[...,None]
    grey=smooth(0.4,1.6,fbm(S,3.2,seed+8,fmin=1.5,ax=3))[...,None]*0.35
    col=col*(1-grey)+col.mean(-1,keepdims=True)*np.array([1.05,1.0,0.95],f32)*grey
    col*= (1-0.6*cr[...,None])
    light_=painted_light(normal_from_height(blur(h,2),depth*3,tile))
    col*= (0.85+0.28*light_[...,None])
    rough=np.clip(0.84+0.05*fib+0.1*cr,0,1)
    PBR_SETS["T_VK_Wood"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Wood",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.4)
def gen_planks(S=1024,seed=61,tile=2.0,depth=0.025):
    rng=np.random.default_rng(seed); x,y=grid(S)
    nb=8; b=np.minimum((x*nb).astype(int),nb-1); u=(x*nb)%1
    G=fbm(S,1.8,seed,fmin=4,ay=12); G2=fbm(S,1.5,seed+1,fmin=30,ay=18)
    rings=np.sin(2*np.pi*(x*37+fbm(S,3.0,seed+2,fmin=1,ay=6)*0.25)).astype(f32)
    shifts=rng.integers(0,S,nb); gr=np.empty_like(G); gr2=np.empty_like(G2)
    for i in range(nb):
        cols=slice(i*S//nb,(i+1)*S//nb)
        gr[:,cols]=np.roll(G,shifts[i],0)[:,cols]; gr2[:,cols]=np.roll(G2,shifts[i],0)[:,cols]
    btint=rng.uniform(0.82,1.1,nb).astype(f32); bgrey=(rng.random(nb)<0.3).astype(f32)
    edge=np.minimum(u,1-u)*S/nb
    gapm=smooth(1.5,4.0,edge)
    bow=1-((2*u-1)**2)*0.25
    h=gapm*(0.5+0.3*bow+0.07*gr+0.03*gr2+0.03*rings)+(1-gapm)*0.05
    # nails
    nail=np.zeros((S,S),f32)
    for i in range(nb):
        for yy in (0.06,0.56):
            cx=(i+0.5)/nb*S; cy=(yy+0.02*rng.uniform(-1,1))*S
            d=np.hypot(x*S-cx,y*S-cy); nail=np.maximum(nail,smooth(6,4,d))
    h=np.maximum(h,nail*0.9)
    cr=draw_segments(S,crack_segments(S,rng,n=6,steps=(15,35),step_px=(8,14),w0=2.2,branch=0.03,dirbias=math.pi/2,jit=0.12))
    h-=0.3*cr*gapm
    h=blur(np.clip(h,0,1),0.6)
    lum=np.clip(0.58+0.13*gr+0.05*gr2+0.04*rings,0.1,1)[...,None]
    dark=np.array([0.22,0.13,0.07],f32); mid=np.array([0.46,0.30,0.17],f32); light=np.array([0.64,0.46,0.28],f32)
    col=np.where(lum<0.6,dark+(mid-dark)*(lum/0.6),mid+(light-mid)*((lum-0.6)/0.4))*btint[b][...,None]
    grey=np.array([0.46,0.43,0.38],f32)*(0.8+0.3*lum)
    col=col*(1-0.55*bgrey[b][...,None])+grey*0.55*bgrey[b][...,None]
    col=col*(0.35+0.65*gapm[...,None])*(1-0.5*cr[...,None])
    col=col*(1-nail[...,None])+np.array([0.16,0.16,0.18],f32)*nail[...,None]
    light_=painted_light(normal_from_height(blur(h,2),depth*3,tile))
    col*= (0.85+0.28*light_[...,None])
    rough=np.clip(0.86+0.04*gr-0.3*nail,0,1)
    PBR_SETS["T_VK_Planks"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Planks",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.4)

def shingle_layout(S,seed,nrow=8,ncol=6):
    rng=np.random.default_rng(seed); x,y=grid(S)
    row=np.minimum((y*nrow).astype(int),nrow-1); v=(y*nrow)%1
    xo=(x*ncol+0.5*(row%2))%ncol; c=np.minimum(xo.astype(int),ncol-1); u=xo%1
    bl=rng.uniform(0.9,0.97,(nrow,ncol)).astype(f32)
    chip=fbm(S,2.6,seed+1,fmin=8,fmax=80)*0.012
    bottom=bl[row,c]-0.27*(1-np.sqrt(np.clip(1-(2*u-1)**2,0,1)))+chip
    inside=v<bottom
    t=np.clip(v/np.maximum(bottom,0.05),0,1)
    tv=rng.uniform(-1,1,(nrow,ncol)).astype(f32)
    row2=(row+1)%nrow; xo2=(x*ncol+0.5*(row2%2))%ncol; c2=np.minimum(xo2.astype(int),ncol-1); u2=xo2%1
    return dict(row=row,c=c,u=u,v=v,bottom=bottom,inside=inside,t=t,tilt=tv,rng=rng,row2=row2,c2=c2,u2=u2)
def shingle_height(L,S,seed):
    u,t,inside=L["u"],L["t"],L["inside"]
    across=1-((2*u-1)**2)*0.35
    gapm=smooth(0.0,0.035,np.minimum(u,1-u))
    hin=(0.18+0.72*t**0.85*across+L["tilt"][L["row"],L["c"]]*(u-0.5)*0.18)*(0.55+0.45*gapm)
    hin+=facets(S,seed+3,8,60,0.035)
    gap2=smooth(0.0,0.035,np.minimum(L["u2"],1-L["u2"]))
    hout=0.18*(0.55+0.45*gap2)*(1-((2*L["u2"]-1)**2)*0.35)
    return blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.8)
def gen_roofs(S=1024,seed=71,tile=3.0,depth=0.045):
    L=shingle_layout(S,seed); h=shingle_height(L,S,seed)
    ao=cavity_ao(h,radii=(3,10,24),k=(2.5,1.8,1.0),floor=0.3)
    # shadow band just below each rounded edge
    shadow=np.where(L["inside"],1.0,0.55+0.45*smooth(0,0.25,L["v"]-L["bottom"])).astype(f32)
    ao=np.minimum(ao,shadow)
    rng=L["rng"]; row,c,t,u=L["row"],L["c"],L["t"],L["u"]
    light=painted_light(normal_from_height(blur(h,2.5),depth*3,tile))
    def paint(pal,name,moss=0.0,mseed=0):
        pal=np.array(pal,f32); pick=rng.integers(0,len(pal),(8,6)); tint=rng.uniform(0.86,1.12,(8,6)).astype(f32)
        ins=L["inside"][...,None]
        col=np.where(ins,pal[pick[row,c]]*tint[row,c][...,None],pal[pick[L["row2"],L["c2"]]]*tint[L["row2"],L["c2"]][...,None])
        teff=np.where(L["inside"],t,0.0)[...,None]
        col=col*(0.72+0.4*teff**0.8)*(0.85+0.25*light[...,None])
        col=col*(1+0.05*fbm(S,2.6,mseed+5,fmin=3,fmax=90)[...,None])
        rough=np.clip(0.68+0.08*fbm(S,2.4,mseed+6,fmin=6)+0.2*(1-L["inside"]),0,1).astype(f32)
        if moss>0:
            mz=smooth(0.6,1.6,fbm(S,3.0,mseed+7,fmin=2))*moss
            mz=mz*(0.6+0.4*(1-np.where(L["inside"],t,0.0)))            # moss gathers at the top of each shingle / in overlaps
            mcol=np.array([0.30,0.42,0.12],f32)*(0.8+0.4*fbm(S,2.0,mseed+8,fmin=20)[...,None]*0.3)
            col=col*(1-mz[...,None])+mcol*mz[...,None]
            rough=np.clip(rough+0.2*mz,0,1)
        PBR_SETS[name]=dict(depth=depth,tile=tile)
        write_map(name+"_BC",col*(0.45+0.55*ao)[...,None])
        write_map(name+"_R",rough,True)
    paint([(0.70,0.26,0.15),(0.62,0.22,0.12),(0.74,0.32,0.18),(0.58,0.25,0.15)],"T_VK_RoofRed",0.0,71)
    paint([(0.22,0.33,0.55),(0.26,0.38,0.60),(0.19,0.29,0.48),(0.28,0.36,0.52)],"T_VK_RoofBlue",0.0,72)
    paint([(0.30,0.38,0.30),(0.26,0.34,0.28),(0.34,0.40,0.32),(0.24,0.30,0.27)],"T_VK_RoofGreen",0.55,73)
    for name in ("T_VK_RoofRed","T_VK_RoofBlue","T_VK_RoofGreen"):
        write_map(name+"_N",normal_from_height(h,depth,tile)*0.5+0.5,True)
        write_map(name+"_H",h,True); write_map(name+"_AO",ao,True)
def gen_thatch(S=1024,seed=81,tile=3.0,depth=0.07):
    rng=np.random.default_rng(seed); x,y=grid(S)
    nrow=6; row=np.minimum((y*nrow).astype(int),nrow-1); v=(y*nrow)%1
    edge=0.87+0.05*np.sin(2*np.pi*(x*9+row*0.37)).astype(f32)+0.03*fbm(S,2.8,seed,fmin=4,fmax=30)
    inside=v<edge
    t=np.clip(v/edge,0,1)
    strands=fbm(S,1.6,seed+1,fmin=20,fmax=300,ay=16)
    bundles=fbm(S,2.6,seed+2,fmin=3,fmax=40,ay=5)
    hin=0.25+0.62*t**0.7+0.07*strands+0.06*bundles
    hout=0.25+0.07*strands+0.06*bundles
    h=blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.7)
    ao=cavity_ao(h,radii=(3,10,30),k=(2.0,1.6,1.0),floor=0.3)
    shadow=np.where(inside,1.0,0.5+0.3*smooth(0,0.2,v-edge)).astype(f32); ao=np.minimum(ao,shadow)
    base=np.array([0.78,0.61,0.32],f32)
    teff=np.where(inside,t,0.0)[...,None]
    col=base*(0.62+0.42*teff**0.8)*(0.85+0.15*strands[...,None]*0.5+0.1*bundles[...,None])
    grey=smooth(0.5,1.6,fbm(S,3.2,seed+3,fmin=1.5))
    col=col*(1-0.5*grey[...,None])+np.array([0.52,0.47,0.38],f32)*(0.6+0.4*t[...,None])*0.5*grey[...,None]
    moss=smooth(1.4,2.0,fbm(S,3.2,seed+4,fmin=2))*(1-teff[...,0])
    col=col*(1-0.6*moss[...,None])+np.array([0.34,0.42,0.14],f32)*0.6*moss[...,None]
    rough=np.clip(0.9+0.05*strands,0,1)
    PBR_SETS["T_VK_Thatch"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Thatch",col.astype(f32),h,rough,depth,tile,ao=ao,ao_in_albedo=0.6)

def lattice(S,n=5):
    x,y=grid(S); a=(x+y)*n; b=(x-y)*n
    da=np.abs(a-np.round(a)); db=np.abs(b-np.round(b))
    lead=np.minimum(da,db); ia=np.floor(a).astype(int); ib=np.floor(b).astype(int)
    pane=np.minimum(da,db)   # distance to lead (in diamond units)
    return x,y,lead,ia,ib
def gen_window(S=512,seed=91,tile=1.0,depth=0.008):
    x,y,lead,ia,ib=lattice(S,5)
    lm=1-smooth(0.03,0.05,lead)
    bulge=smooth(0.04,0.3,lead)
    h=np.clip(0.35+0.25*bulge+0.02*fbm(S,3.0,seed,fmin=3,fmax=40)+0.55*lm,0,1)
    h=blur(h,0.6)
    glass=np.array([0.09,0.20,0.24],f32)+np.array([0.20,0.26,0.24],f32)*np.clip(1-y,0,1)[...,None]*0.7
    refl=np.exp(-(((x-y*0.6+0.35)%1-0.25)**2)/0.004)*0.35+np.exp(-(((x-y*0.6+0.35)%1-0.36)**2)/0.0008)*0.25
    pv=(np.sin(ia*12.9+ib*7.3)*0.5+0.5).astype(f32)*0.12
    col=glass*(0.85+pv[...,None])+refl[...,None]*np.array([0.85,0.95,1.0],f32)
    col=col*(1-lm[...,None])+np.array([0.13,0.13,0.14],f32)*lm[...,None]
    rough=np.clip(0.06+0.5*lm,0,1)
    PBR_SETS["T_VK_Window"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Window",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.2)
def gen_stained(S=512,seed=92,tile=1.0,depth=0.008):
    x,y,lead,ia,ib=lattice(S,5)
    lm=1-smooth(0.035,0.055,lead)
    pal=np.array([(0.80,0.12,0.10),(0.12,0.28,0.80),(0.90,0.68,0.12),(0.12,0.58,0.26),(0.58,0.16,0.62),(0.16,0.48,0.80)],f32)
    hsh=(ia*7+ib*13)%len(pal)
    glow=0.75+0.35*smooth(0.05,0.3,lead)
    col=pal[hsh]*glow[...,None]*(0.9+0.12*fbm(S,2.6,seed,fmin=3,fmax=60)[...,None])
    col=col*(1-lm[...,None])+np.array([0.06,0.06,0.07],f32)*lm[...,None]
    h=blur(np.clip(0.4+0.2*smooth(0.04,0.3,lead)+0.55*lm,0,1),0.6)
    rough=np.clip(0.12+0.5*lm,0,1)
    PBR_SETS["T_VK_Stained"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Stained",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.15)
def gen_iron(S=512,seed=93,tile=0.5,depth=0.004):
    rng=np.random.default_rng(seed); x,y=grid(S)
    F1,F2,ID=voronoi(x,y,rng.uniform(0,1,(60,2)))
    dent=np.clip(F1/0.08,0,1)**0.7
    h=blur(np.clip(0.4+0.4*dent+0.05*fbm(S,2.4,seed+1,fmin=6),0,1),0.8)
    rust=smooth(0.7,1.5,fbm(S,2.8,seed+2,fmin=2))*(1-dent*0.6)
    base=np.array([0.20,0.20,0.23],f32)*(0.8+0.3*dent[...,None])
    col=base*(1-rust[...,None])+np.array([0.34,0.17,0.08],f32)*(0.8+0.3*fbm(S,2,seed+3,fmin=10)[...,None]*0.3)*rust[...,None]
    rough=np.clip(0.45+0.45*rust+0.05*fbm(S,2,seed+4,fmin=10),0,1)
    PBR_SETS["T_VK_Iron"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Iron",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.3,extra={"M":np.clip(0.85-0.8*rust,0,1)})
def gen_straw(S=1024,seed=94,tile=1.2,depth=0.02):
    h=np.zeros((S,S),f32)
    for i,ang in enumerate((0.35,1.2,2.1,2.75,-0.4)):
        st=fbm(S,1.5,seed+i,fmin=30,fmax=400,ax=18,angle=ang)
        h=np.maximum(h,np.clip(st*0.35+0.4,0,1))
    h=blur(h,0.6)
    base=np.array([0.86,0.68,0.32],f32)
    col=base*(0.55+0.55*h[...,None])*(0.95+0.08*fbm(S,3,seed+9,fmin=2)[...,None])
    dry=smooth(0.6,1.6,fbm(S,3,seed+10,fmin=2))
    col=col*(1-0.35*dry[...,None])+np.array([0.62,0.55,0.38],f32)*0.35*dry[...,None]*(0.55+0.55*h[...,None])
    rough=np.full((S,S),0.9,f32)
    PBR_SETS["T_VK_Straw"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Straw",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.5)
def weave(S,f,seed,irr=0.15):
    x,y=grid(S)
    xw=(x+fbm(S,3.0,seed,fmin=2)*0.002)%1; yw=(y+fbm(S,3.0,seed+1,fmin=2)*0.002)%1
    cx=(xw*f)%1; cy=(yw*f)%1; ix=(xw*f).astype(int); iy=(yw*f).astype(int)
    over=((ix+iy)%2==0)
    tx=np.sin(np.pi*cy)**0.7; ty=np.sin(np.pi*cx)**0.7
    alongx=0.75+0.25*np.cos(np.pi*(cx-0.5)); alongy=0.75+0.25*np.cos(np.pi*(cy-0.5))
    h=np.where(over,0.45+0.5*tx*alongx,0.45+0.5*ty*alongy).astype(f32)
    h=h*(1-irr+irr*(0.5+0.5*fbm(S,2.0,seed+2,fmin=f/4)))
    return blur(np.clip(h,0,1),0.5)
def gen_burlap(S=512,seed=95,tile=0.8,depth=0.004):
    h=weave(S,48,seed,0.25)
    col=np.array([0.64,0.52,0.34],f32)*(0.62+0.5*h[...,None])*(0.92+0.1*fbm(S,2.6,seed+5,fmin=2)[...,None])
    PBR_SETS["T_VK_Burlap"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Burlap",col.astype(f32),h,np.full((S,S),0.95,f32),depth,tile,ao_in_albedo=0.4)
def gen_cloth(S=512,seed=96,tile=0.5,depth=0.002):
    h=weave(S,64,seed,0.1)
    col=np.full((S,S,3),0.93,f32)*(0.84+0.18*h[...,None])*(0.96+0.05*fbm(S,2.6,seed+5,fmin=2)[...,None])
    PBR_SETS["T_VK_Cloth"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Cloth",col.astype(f32),h,np.full((S,S),0.85,f32),depth,tile,ao_in_albedo=0.3)
def gen_soil(S=512,seed=97,tile=1.0,depth=0.03):
    rng=np.random.default_rng(seed); x,y=grid(S)
    F1,F2,ID=voronoi(x,y,rng.uniform(0,1,(90,2)))
    clod=np.clip((F2-F1)/0.04,0,1)**0.5
    pF1,pF2,pID=voronoi(x,y,rng.uniform(0,1,(160,2)))
    peb=smooth(0.012,0.006,pF1)*(rng.random(160)<0.35)[pID]
    h=blur(np.clip(0.3+0.35*clod+0.1*fbm(S,2.4,seed+1,fmin=4)+0.35*peb,0,1),0.7)
    col=np.array([0.22,0.15,0.09],f32)*(0.75+0.45*clod[...,None])
    col=col*(1-peb[...,None])+np.array([0.48,0.44,0.38],f32)*peb[...,None]
    PBR_SETS["T_VK_Soil"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Soil",col.astype(f32),h,np.clip(0.95-0.2*peb,0,1),depth,tile,ao_in_albedo=0.5)
def gen_paper(S=512,seed=98,tile=0.3,depth=0.001):
    rng=np.random.default_rng(seed); x,y=grid(S)
    fib=fbm(S,1.6,seed,fmin=40)
    col=np.array([0.92,0.86,0.70],f32)*(0.95+0.04*fib[...,None])
    ink=np.zeros((S,S),f32)
    for r in range(9):
        yy=0.1+r*0.09
        segs=[]; xx=0.08+rng.uniform(0,0.05)
        while xx<0.9:
            L=rng.uniform(0.04,0.12); 
            pts=[(xx+i*L/6,yy+0.006*math.sin(i*2.1+r)+rng.uniform(-0.002,0.002)) for i in range(7)]
            for a,b in zip(pts[:-1],pts[1:]): segs.append((a[0]*S,a[1]*S,b[0]*S,b[1]*S,1.4))
            xx+=L+rng.uniform(0.02,0.04)
        ink=np.maximum(ink,draw_segments(S,segs))
    col=col*(1-0.8*ink[...,None])+np.array([0.12,0.09,0.07],f32)*0.8*ink[...,None]
    h=0.5+0.05*fib
    PBR_SETS["T_VK_Paper"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Paper",col.astype(f32),h.astype(f32),np.full((S,S),0.9,f32),depth,tile,ao_in_albedo=0.1)
def gen_water(S=512,seed=99,tile=1.0,depth=0.01):
    h=np.clip(0.5+0.2*fbm(S,3.2,seed,fmin=3),0,1)
    col=np.array([0.10,0.27,0.31],f32)*(0.9+0.2*fbm(S,3,seed+1,fmin=2)[...,None])*np.ones((S,S,1),f32)
    PBR_SETS["T_VK_Water"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Water",col.astype(f32),h.astype(f32),np.full((S,S),0.04,f32),depth,tile,ao_in_albedo=0.0)
def gen_paintedwood(S=1024,seed=100,tile=1.6,depth=0.02):
    # reuse the beam-wood generator for the bare wood, paint layer on top, chipped where the mask is low
    rng=np.random.default_rng(seed); x,y=grid(S)
    wood=bpy.data.images["T_VK_Wood_BC"]; wa=np.array(wood.pixels[:],f32).reshape(S,S,4)[::-1,:,:3]
    wh=np.array(bpy.data.images["T_VK_Wood_H"].pixels[:],f32).reshape(S,S,4)[::-1,:,0]
    chip=smooth(1.0,1.25,fbm(S,2.6,seed,fmin=3,fmax=80)+0.25*fbm(S,1.8,seed+1,fmin=30))
    paint=1-chip
    brush=fbm(S,2.2,seed+2,fmin=4,fmax=120,ax=8)
    pcol=np.full((S,S,3),0.86,f32)*(0.92+0.06*brush[...,None])
    col=wa*(1-paint[...,None])+pcol*paint[...,None]
    h=np.clip(wh*0.7+0.25*paint+0.02*brush*paint,0,1)
    rough=np.clip(0.55*paint+0.88*(1-paint),0,1)
    PBR_SETS["T_VK_PaintedWood"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_PaintedWood",col.astype(f32),h.astype(f32),rough.astype(f32),depth,tile,ao_in_albedo=0.35,extra={"Mask":paint})

def gen_rock(S=1024,seed=111,tile=1.5,depth=0.05):
    rng=np.random.default_rng(seed); x,y=grid(S)
    h=0.5+0.16*fbm(S,3.0,seed,fmin=2)+facets(S,seed+1,3,30,0.20)+facets(S,seed+2,8,80,0.08)+0.006*fbm(S,1.6,seed+3,fmin=120)
    pits=smooth(1.7,2.3,fbm(S,2.2,seed+4,fmin=30,fmax=200))
    h=blur(np.clip(h-0.08*pits,0,1),0.7)
    n=normal_from_height(blur(h,2),depth*3,tile); light=painted_light(n)
    warm=smooth(-1,1,fbm(S,3.2,seed+5,fmin=1.5))[...,None]
    base=np.array([0.55,0.54,0.52],f32)*(1-warm)+np.array([0.68,0.61,0.50],f32)*warm
    col=base*(0.72+0.42*light[...,None])*(1+0.05*fbm(S,2.4,seed+6,fmin=4,fmax=100)[...,None])
    # crevices darker
    ao=cavity_ao(h,radii=(3,12,30),k=(3.0,2.2,1.4),floor=0.3)
    lich=smooth(1.6,2.1,fbm(S,2.4,seed+7,fmin=12,fmax=160))
    col=col*(1-0.6*lich[...,None])+np.array([0.80,0.70,0.36],f32)*0.6*lich[...,None]
    moss=smooth(1.2,1.9,fbm(S,3.0,seed+8,fmin=2))*smooth(0.3,0.7,n[...,1])
    col=col*(1-0.55*moss[...,None])+np.array([0.34,0.44,0.16],f32)*0.55*moss[...,None]
    rough=np.clip(0.82+0.06*fbm(S,2.4,seed+9,fmin=6)+0.08*moss,0,1)
    PBR_SETS["T_VK_Rock"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Rock",col.astype(f32),h,rough,depth,tile,ao=ao,ao_in_albedo=0.5)

def gen_clock(S=512,seed=121):
    x,y=grid(S); cx=x-0.5; cy=y-0.5; r=np.sqrt(cx*cx+cy*cy); a=np.arctan2(cx,-cy)   # a=0 at 12 o'clock
    col=np.zeros((S,S,3),f32)+np.array([0.93,0.87,0.68],f32)*(0.95+0.05*fbm(S,2.5,seed,fmin=3)[...,None])
    ring=(smooth(0.415,0.425,r)-smooth(0.455,0.465,r))
    outer=smooth(0.465,0.475,r)
    col=col*(1-ring[...,None])+np.array([0.10,0.09,0.08],f32)*ring[...,None]
    col=col*(1-outer[...,None])+np.array([0.20,0.13,0.07],f32)*outer[...,None]
    h=np.full((S,S),0.5,f32)
    segs=[]
    for i in range(12):
        ang=2*math.pi*i/12; L0=0.34 if i%3 else 0.30; w=5.0 if i%3 else 9.0
        segs.append((S*(0.5+math.sin(ang)*L0),S*(0.5-math.cos(ang)*L0),S*(0.5+math.sin(ang)*0.40),S*(0.5-math.cos(ang)*0.40),w))
    # hands at 10:10
    for ang,L,w in ((2*math.pi*(10/12+10/720),0.2,11.0),(2*math.pi*(10/60),0.33,7.0)):
        segs.append((S*0.5,S*0.5,S*(0.5+math.sin(ang)*L),S*(0.5-math.cos(ang)*L),w))
    ink=draw_segments(S,segs)
    hub=smooth(0.025,0.018,r)
    ink=np.maximum(ink,hub)
    col=col*(1-ink[...,None])+np.array([0.08,0.07,0.06],f32)*ink[...,None]
    h=h+0.25*ink+0.15*ring-0.2*outer
    rough=np.clip(0.7-0.3*ink,0,1).astype(f32)
    PBR_SETS["T_VK_Clock"]=dict(depth=0.01,tile=1.1)
    return write_set("T_VK_Clock",col,h.astype(f32),rough,0.01,1.1,ao_in_albedo=0.2)

def _poly_fill(S,img,alpha,shape_fn,cx,cy,rad,ang,color_fn):
    x0=int(max(0,cx-rad-2)); x1=int(min(S,cx+rad+2)); y0=int(max(0,cy-rad-2)); y1=int(min(S,cy+rad+2))
    if x0>=x1 or y0>=y1: return
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
    dx=(xx-cx)/rad; dy=(yy-cy)/rad
    ca,sa=math.cos(ang),math.sin(ang)
    u=dx*ca+dy*sa; v=-dx*sa+dy*ca
    inside,shade=shape_fn(u,v)
    a=np.clip(inside,0,1)
    c=color_fn(u,v,shade)
    reg=img[y0:y1,x0:x1]; ar=alpha[y0:y1,x0:x1]
    reg[:]=reg*(1-a[...,None])+c*a[...,None]; ar[:]=np.maximum(ar,a)
def ivy_leaf(u,v):
    th=np.arctan2(u,-v); r=np.hypot(u,v)
    R=0.62+0.3*np.abs(np.cos(1.5*th))**0.6-0.12*(np.cos(th)<-0.3)
    inside=np.clip((R-r)*14,0,1)
    vein=np.minimum(np.abs(th),np.minimum(np.abs(th-2.1),np.abs(th+2.1)))
    shade=0.8+0.25*(-v)*0.5-0.18*np.exp(-(vein*r*6)**2)*(r<R)
    return inside,shade
def petal_flower(n=5,inner=0.28):
    def f(u,v):
        th=np.arctan2(v,u); r=np.hypot(u,v)
        R=0.55+0.45*np.abs(np.cos(n*th/2))**0.8
        inside=np.clip((R-r)*10,0,1)
        center=(r<inner).astype(f32)
        return inside,np.stack([center,r],-1)
    return f
def gen_foliage(S=1024,seed=141):
    rng=np.random.default_rng(seed)
    img=np.zeros((S,S,3),f32); alpha=np.zeros((S,S),f32); H=S//2
    greens=[np.array(c,f32) for c in [(0.16,0.36,0.08),(0.22,0.44,0.10),(0.28,0.50,0.12),(0.13,0.30,0.08),(0.34,0.52,0.16)]]
    def green_col(g):
        return lambda u,v,sh: (g[None,None,:]*sh[...,None]).astype(f32)
    # ---- cell (0,0): ivy
    ox,oy=0,0
    segs=[]
    for _ in range(4):
        x=ox+rng.uniform(60,H-60); y=oy+H-10; a=-math.pi/2+rng.uniform(-0.5,0.5)
        for i in range(22):
            a+=rng.uniform(-0.35,0.35); nx=x+math.cos(a)*20; ny=y+math.sin(a)*20
            if not (ox+20<nx<ox+H-20 and oy+20<ny<oy+H-20): break
            segs.append((x,y,nx,ny,3.0)); x,y=nx,ny
    stem=draw_segments(S,segs,wrap=False)
    img=img*(1-stem[...,None])+np.array([0.28,0.2,0.1],f32)*stem[...,None]; alpha=np.maximum(alpha,stem)
    for _ in range(95):
        cx=ox+rng.uniform(35,H-35); cy=oy+rng.uniform(35,H-35)
        _poly_fill(S,img,alpha,ivy_leaf,cx,cy,rng.uniform(22,36),rng.uniform(-0.9,0.9),green_col(greens[rng.integers(0,5)]*rng.uniform(0.85,1.15)))
    # ---- cell (1,0): pink flower cluster
    ox,oy=H,0
    for _ in range(40):
        cx=ox+rng.uniform(40,H-40); cy=oy+rng.uniform(H*0.35,H-30)
        _poly_fill(S,img,alpha,ivy_leaf,cx,cy,rng.uniform(22,32),rng.uniform(-1.2,1.2),green_col(greens[rng.integers(0,5)]))
    pinks=[np.array(c,f32) for c in [(0.92,0.35,0.62),(0.85,0.22,0.48),(0.98,0.55,0.75),(0.75,0.18,0.55)]]
    for _ in range(30):
        cx=ox+rng.uniform(45,H-45); cy=oy+rng.uniform(40,H*0.8)
        pc=pinks[rng.integers(0,4)]
        def colf(u,v,sh,pc=pc):
            center=sh[...,0]; r=sh[...,1]
            c=pc[None,None,:]*(0.75+0.35*np.clip(r,0,1))[...,None]
            return (c*(1-center[...,None])+np.array([0.98,0.85,0.25],f32)*center[...,None]).astype(f32)
        _poly_fill(S,img,alpha,petal_flower(5,0.22),cx,cy,rng.uniform(20,30),rng.uniform(0,6.28),colf)
    # ---- cell (0,1): white daisies + yellow
    ox,oy=0,H
    for _ in range(40):
        cx=ox+rng.uniform(40,H-40); cy=oy+rng.uniform(H*0.35,H-30)
        _poly_fill(S,img,alpha,ivy_leaf,cx,cy,rng.uniform(22,32),rng.uniform(-1.2,1.2),green_col(greens[rng.integers(0,5)]))
    for _ in range(30):
        cx=ox+rng.uniform(45,H-45); cy=oy+rng.uniform(40,H*0.8)
        pc=np.array([0.96,0.95,0.9],f32) if rng.random()<0.6 else np.array([0.98,0.8,0.2],f32)
        def colf(u,v,sh,pc=pc):
            center=sh[...,0]; r=sh[...,1]
            c=pc[None,None,:]*(0.8+0.25*np.clip(r,0,1))[...,None]
            return (c*(1-center[...,None])+np.array([0.95,0.65,0.1],f32)*center[...,None]).astype(f32)
        _poly_fill(S,img,alpha,petal_flower(8,0.3),cx,cy,rng.uniform(18,26),rng.uniform(0,6.28),colf)
    # ---- cell (1,1): grass tuft (blades from the bottom)
    ox,oy=H,H
    segs=[]
    blades=np.zeros((S,S),f32); bcol=np.zeros((S,S,3),f32)
    for _ in range(70):
        x=ox+rng.uniform(70,H-70); y=oy+H-8; a=-math.pi/2+rng.uniform(-0.3,0.3); L=rng.uniform(150,320); w=rng.uniform(6,11)
        pts=[]
        for i in range(10):
            t=i/9; pts.append((x+math.cos(a)*L*t+rng.uniform(-2,2),y+math.sin(a)*L*t)); a+=rng.uniform(-0.06,0.06)
        sg=[(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],w*(1-i/10)+1) for i in range(9)]
        cov=draw_segments(S,sg,wrap=False)
        g=greens[rng.integers(0,5)]*rng.uniform(0.9,1.25)
        tip=np.clip((oy+H-np.mgrid[0:S,0:S][0])/400.0,0,1)[...,None]
        c=g*(0.7+0.5*tip)
        img=img*(1-cov[...,None])+c*cov[...,None]; alpha=np.maximum(alpha,cov)
    # colour dilation for mips
    rgb=img.copy(); m=alpha>0.5
    for _ in range(12):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    rgba=np.concatenate([np.clip(rgb,0,1),alpha[...,None]],-1).astype(f32)
    name="T_VK_Foliage_BCA"
    im=bpy.data.images.get(name)
    if im is None: im=bpy.data.images.new(name,S,S,alpha=True)
    im.alpha_mode="STRAIGHT"
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel()); im.update()
    im.filepath_raw=os.path.join(TEXDIR,name+".png"); im.file_format="PNG"; im.save(); im.pack()
    return im

def gen_crops(S=1024,seed=151):
    rng=np.random.default_rng(seed); H=S//2
    img=np.zeros((S,S,3),f32); alpha=np.zeros((S,S),f32)
    def blades(ox,oy,n,cols,L=(180,330),w=(6,10),spread=0.3,ears=None,tipcol=None):
        nonlocal img,alpha
        for _ in range(n):
            x=ox+rng.uniform(70,H-70); y=oy+H-8; a=-math.pi/2+rng.uniform(-spread,spread); Ll=rng.uniform(*L); ww=rng.uniform(*w)
            pts=[]
            for i in range(10):
                t=i/9; pts.append((x+math.cos(a)*Ll*t,y+math.sin(a)*Ll*t)); a+=rng.uniform(-0.05,0.05)
            sg=[(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],ww*(1-i/11)+1) for i in range(9)]
            cov=draw_segments(S,sg,wrap=False)
            c=cols[rng.integers(0,len(cols))]*rng.uniform(0.85,1.15)
            img=img*(1-cov[...,None])+c*cov[...,None]; alpha=np.maximum(alpha,cov)
            if ears is not None:
                ex,ey=pts[-1]; ang=math.atan2(pts[-1][1]-pts[-3][1],pts[-1][0]-pts[-3][0])
                for j in range(7):
                    px=ex-math.cos(ang)*j*9; py=ey-math.sin(ang)*j*9
                    for sgn in(-1,1):
                        qx=px+math.cos(ang+sgn*0.6)*9; qy=py+math.sin(ang+sgn*0.6)*9
                        cv=draw_segments(S,[(px,py,qx,qy,8.0)],wrap=False)
                        ec=ears*rng.uniform(0.85,1.15)*(0.85+0.03*j)
                        img=img*(1-cv[...,None])+ec*cv[...,None]; alpha=np.maximum(alpha,cv)
    gold=[np.array(c,f32) for c in [(0.80,0.62,0.26),(0.72,0.55,0.22),(0.86,0.70,0.32)]]
    blades(0,0,45,gold,ears=np.array([0.90,0.72,0.30],f32))
    greens=[np.array(c,f32) for c in [(0.20,0.45,0.10),(0.28,0.52,0.14),(0.16,0.38,0.08)]]
    # leafy tops (carrot / beet): short wide feathery blades
    blades(H,0,60,greens,L=(90,200),w=(10,16),spread=0.8)
    dry=[np.array(c,f32) for c in [(0.70,0.62,0.36),(0.62,0.55,0.30),(0.78,0.70,0.42)]]
    blades(0,H,60,dry,L=(150,300),w=(4,7),spread=0.45)
    # lavender: grey-green stems with purple spikes
    blades(H,H,40,[np.array((0.42,0.5,0.36),f32)],L=(200,320),w=(4,6),spread=0.35,ears=np.array([0.52,0.36,0.78],f32))
    rgb=img.copy(); m=alpha>0.5
    for _ in range(12):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    rgba=np.concatenate([np.clip(rgb,0,1),alpha[...,None]],-1).astype(f32)
    name="T_VK_Crops_BCA"; im=bpy.data.images.get(name)
    if im is None: im=bpy.data.images.new(name,S,S,alpha=True)
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel()); im.update()
    im.filepath_raw=os.path.join(TEXDIR,name+".png"); im.file_format="PNG"; im.save(); im.pack()

# =====================  NATURE TEXTURES  =====================
def warp(field,du,dv):
    S=field.shape[0]
    yy,xx=np.mgrid[0:S,0:S].astype(f32)
    X=(xx+du*S)%S; Y=(yy+dv*S)%S
    x0=np.floor(X).astype(np.int32); y0=np.floor(Y).astype(np.int32); fx=X-x0; fy=Y-y0
    x1=(x0+1)%S; y1=(y0+1)%S; x0%=S; y0%=S
    return (field[y0,x0]*(1-fx)*(1-fy)+field[y0,x1]*fx*(1-fy)+field[y1,x0]*(1-fx)*fy+field[y1,x1]*fx*fy).astype(f32)
def ramp3(t,c0,c1,c2,mid=0.5):
    t=np.clip(t,0,1)[...,None]; c0=np.array(c0,f32); c1=np.array(c1,f32); c2=np.array(c2,f32)
    return np.where(t<mid,c0+(c1-c0)*(t/mid),c1+(c2-c1)*((t-mid)/(1-mid))).astype(f32)
def gen_bark_oak(S=1024,seed=201,tile=1.2,depth=0.07):
    x,y=grid(S)
    n1=fbm(S,2.4,seed+1,fmin=3,fmax=40,ay=5.0)
    n1=warp(n1,fbm(S,3.0,seed+7,fmin=1.5)*0.03,np.zeros((S,S),f32))
    plates=smooth(0.1,0.6,np.abs(n1))
    n2=fbm(S,2.2,seed+2,fmin=3,fmax=40,ax=4.0)
    gate=smooth(0.2,0.9,fbm(S,2.2,seed+3,fmin=2,fmax=30))
    breaks=(1-smooth(0.0,0.14,np.abs(n2)))*gate
    fine=fbm(S,1.8,seed+4,fmin=40,fmax=300,ay=3.0)
    h=0.12+0.72*plates*(1-0.6*breaks)+0.05*fine*plates+facets(S,seed+8,6,50,0.05)*plates
    h=blur(np.clip(h,0,1),0.8)
    n=normal_from_height(blur(h,2.0),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.09,0.07,0.055),(0.29,0.23,0.18),(0.47,0.40,0.32),0.45)
    col=col*(0.8+0.35*light[...,None])*(1+0.05*fbm(S,3,seed+9,fmin=2)[...,None])
    lich=smooth(1.35,1.9,fbm(S,2.6,seed+5,fmin=5,fmax=80))*plates
    col=col*(1-0.55*lich[...,None])+np.array([0.56,0.60,0.46],f32)*0.55*lich[...,None]*(0.8+0.3*light[...,None])
    moss=smooth(0.9,1.8,fbm(S,3.0,seed+6,fmin=2))*(1-plates)
    col=col*(1-0.5*moss[...,None])+np.array([0.20,0.30,0.09],f32)*0.5*moss[...,None]
    rough=np.clip(0.84+0.12*(1-plates),0,1)
    PBR_SETS["T_VK_BarkOak"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkOak",col,h,rough,depth,tile,ao_in_albedo=0.6)
def gen_bark_birch(S=1024,seed=211,tile=1.0,depth=0.02):
    x,y=grid(S)
    base=np.array([0.88,0.86,0.80],f32)*(0.93+0.06*fbm(S,3.0,seed,fmin=2)[...,None]+0.04*fbm(S,2.0,seed+1,fmin=4,ax=8)[...,None])
    lent=smooth(1.45,2.0,fbm(S,1.6,seed+2,fmin=25,fmax=220,ax=7.0))
    patch=smooth(1.75,2.25,fbm(S,2.9,seed+3,fmin=2,fmax=30,ax=1.7))
    rim=smooth(1.45,1.75,fbm(S,2.9,seed+3,fmin=2,fmax=30,ax=1.7))*(1-patch)
    peel=smooth(1.55,1.95,fbm(S,2.4,seed+4,fmin=6,fmax=60,ax=3.0))*(1-patch)
    h=0.5+0.03*fbm(S,2.0,seed+5,fmin=8,ax=5)-0.22*lent-0.12*patch+0.08*fbm(S,1.5,seed+6,fmin=60)*patch+0.1*peel
    h=blur(np.clip(h,0,1),0.6)
    col=base*(1-0.8*lent[...,None])+np.array([0.16,0.14,0.13],f32)*0.8*lent[...,None]
    col=col*(1-0.25*rim[...,None])
    col=col*(1-patch[...,None])+np.array([0.09,0.08,0.08],f32)*(0.8+0.3*fbm(S,2,seed+7,fmin=10)[...,None])*patch[...,None]
    col=col*(1-0.6*peel[...,None])+np.array([0.84,0.70,0.56],f32)*0.6*peel[...,None]
    rough=np.clip(0.68+0.25*patch+0.1*lent,0,1)
    PBR_SETS["T_VK_BarkBirch"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkBirch",col,h,rough,depth,tile,ao_in_albedo=0.35)
def gen_bark_pine(S=1024,seed=221,tile=1.4,depth=0.08):
    rng=np.random.default_rng(seed); x,y=grid(S)
    xw=(x+fbm(S,3.0,seed,fmin=2)*0.015)%1; yw=(y+fbm(S,3.0,seed+1,fmin=2)*0.015)%1
    npts=80; pts=rng.uniform(0,1,(npts,2))
    F1,F2,ID=voronoi(xw,yw,pts,sx=1.0,sy=0.42)
    e=F2-F1; plate=smooth(0.003,0.028,e)
    rid=rng.uniform(0.55,1.0,npts).astype(f32); grey=(rng.random(npts)<0.3).astype(f32)
    step=smooth(0.02,0.05,e)*0.12
    h=plate*(0.45+0.3*rid[ID]+step+0.05*fbm(S,1.8,seed+2,fmin=30,ay=3))+(1-plate)*0.08
    h=blur(np.clip(h,0,1),0.7)
    n=normal_from_height(blur(h,2.0),depth*2.5,tile); light=painted_light(n)
    tint=rng.uniform(0.85,1.12,npts).astype(f32)
    pc=np.array([0.50,0.27,0.15],f32)*tint[ID][...,None]
    pc=pc*(1-0.5*grey[ID][...,None])+np.array([0.44,0.38,0.33],f32)*0.5*grey[ID][...,None]
    col=pc*(0.72+0.45*light[...,None])+np.array([0.10,0.04,0.0],f32)*smooth(0.6,0.9,light)[...,None]
    col=col*plate[...,None]+np.array([0.13,0.10,0.085],f32)*(1-plate[...,None])
    rough=np.clip(0.82+0.12*(1-plate),0,1)
    PBR_SETS["T_VK_BarkPine"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkPine",col,h,rough,depth,tile,ao_in_albedo=0.55)
def gen_endgrain(S=512,seed=231):
    rng=np.random.default_rng(seed); x,y=grid(S); cx=x-0.5; cy=y-0.5
    r=np.sqrt(cx*cx+cy*cy)*2.0; ang=np.arctan2(cy,cx)
    wr=r+0.025*fbm(S,3.2,seed,fmin=2)+0.012*np.sin(ang*3+1.3)
    rings=(np.sin(2*np.pi*wr*15)*0.5+0.5)**1.6
    col=ramp3(1-rings*0.8,(0.56,0.38,0.22),(0.72,0.54,0.34),(0.84,0.68,0.46),0.5)
    col=col*(0.85+0.15*smooth(0.1,0.45,r))[...,None]
    sap=smooth(0.72,0.8,r)*(1-smooth(0.88,0.9,r))
    col=col*(1-0.3*sap[...,None])+np.array([0.9,0.78,0.58],f32)*0.3*sap[...,None]
    barkm=smooth(0.88,0.91,r)
    bark=np.array([0.22,0.15,0.10],f32)*(0.8+0.4*(fbm(S,2,seed+1,fmin=20)*0.5+0.5))[...,None]
    col=col*(1-barkm[...,None])+bark*barkm[...,None]
    crack=np.zeros((S,S),f32)
    for i in range(6):
        a0=rng.uniform(-math.pi,math.pi); L=rng.uniform(0.25,0.7)
        da=np.abs(((ang-a0)+math.pi)%(2*math.pi)-math.pi)
        w=0.02*(1-np.clip(r/L,0,1))+0.004
        crack=np.maximum(crack,(1-smooth(0,w,da*r))*(r<L)*(r>0.02))
    pith=1-smooth(0.02,0.045,r)
    col=col*(1-0.75*crack[...,None])*(1-0.6*pith[...,None])
    outside=smooth(0.985,1.0,r)
    h=np.clip(0.55-0.05*rings-0.35*crack+0.15*barkm*(0.7+0.3*fbm(S,2,seed+2,fmin=20)),0,1)
    rough=np.clip(0.8+0.15*barkm,0,1)
    PBR_SETS["T_VK_EndGrain"]=dict(depth=0.01,tile=0.6)
    return write_set("T_VK_EndGrain",col.astype(f32),h.astype(f32),rough.astype(f32),0.01,0.6,ao_in_albedo=0.3)
def gen_moss(S=1024,seed=241,tile=1.0,depth=0.035):
    rng=np.random.default_rng(seed); x,y=grid(S)
    pts=rng.uniform(0,1,(140,2)); F1,F2,ID=voronoi(x,y,pts)
    cush=np.clip(1-F1/0.06,0,1)**0.6
    clumps=fbm(S,2.6,seed,fmin=3,fmax=60); fuzz=fbm(S,1.1,seed+1,fmin=150)
    h=np.clip(0.35+0.35*cush+0.12*clumps+0.06*fuzz,0,1)
    h=blur(h,0.6)
    n=normal_from_height(blur(h,1.5),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.10,0.17,0.04),(0.26,0.42,0.09),(0.52,0.64,0.18),0.55)
    col=col*(0.78+0.35*light[...,None])
    spr=smooth(1.9,2.4,fbm(S,1.0,seed+2,fmin=90))
    col=col*(1-spr[...,None])+np.array([0.72,0.74,0.30],f32)*spr[...,None]
    tintz=fbm(S,3.0,seed+3,fmin=1.5)[...,None]
    col=col*(1+0.06*tintz*np.array([1.0,0.6,-0.5],f32))
    rough=np.clip(0.92+0.05*fuzz,0,1)
    PBR_SETS["T_VK_Moss"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Moss",col.astype(f32),h,rough.astype(f32),depth,tile,ao_in_albedo=0.5)

def gen_bark_oak(S=1024,seed=201,tile=1.2,depth=0.07):
    rng=np.random.default_rng(seed); x,y=grid(S)
    N=7
    wv=fbm(S,2.8,seed,fmin=1,fmax=10,ay=3.0)*0.32+fbm(S,2.2,seed+11,fmin=4,fmax=30,ay=4.0)*0.07
    u=x*N+wv
    cell=np.floor(u).astype(np.int32); f=u-cell; cid=cell%N
    M=rng.integers(2,5,N); ph=rng.uniform(0,1,N).astype(f32); tilt=rng.uniform(-0.35,0.35,N).astype(f32)
    v=y*M[cid]+ph[cid]+tilt[cid]*(f-0.5)+0.05*fbm(S,2.4,seed+12,fmin=3,fmax=40)
    g=v-np.floor(v)
    wid=0.03+0.02*(fbm(S,2.0,seed+13,fmin=3,fmax=30)*0.5+0.5)
    brk=(1-smooth(0.0,1.0,np.minimum(g,1-g)/wid))
    seg=np.floor(v).astype(np.int32)%6
    brk_gate=(rng.random(N*6)<0.7).astype(f32)[cid*6+seg]
    brk=brk*brk_gate*smooth(0.08,0.3,np.minimum(f,1-f))
    dome=np.clip(np.sin(np.pi*np.clip(f,0,1)),0,1)**0.55
    fib=fbm(S,1.5,seed+2,fmin=20,fmax=260,ay=6.0)
    h=0.1+0.75*dome*(1-0.65*brk)+0.035*fib*dome+facets(S,seed+8,6,50,0.04)*dome
    h=blur(np.clip(h,0,1),0.8)
    n=normal_from_height(blur(h,2.5),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.07,0.055,0.045),(0.27,0.21,0.16),(0.46,0.39,0.31),0.45)
    col=col*(0.78+0.38*light[...,None])*(1+0.05*fbm(S,3,seed+9,fmin=2)[...,None])
    lich=smooth(1.45,2.0,fbm(S,2.6,seed+5,fmin=5,fmax=80))*smooth(0.4,0.7,h)
    col=col*(1-0.55*lich[...,None])+np.array([0.57,0.61,0.47],f32)*0.55*lich[...,None]*(0.8+0.3*light[...,None])
    moss=smooth(1.0,1.9,fbm(S,3.0,seed+6,fmin=2))*(1-smooth(0.2,0.45,h))
    col=col*(1-0.6*moss[...,None])+np.array([0.20,0.31,0.08],f32)*0.6*moss[...,None]
    rough=np.clip(0.84+0.12*(1-dome),0,1)
    PBR_SETS["T_VK_BarkOak"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkOak",col,h,rough,depth,tile,ao_in_albedo=0.6)
def gen_endgrain(S=512,seed=231):
    rng=np.random.default_rng(seed); x,y=grid(S); cx=x-0.5; cy=y-0.5
    r=np.sqrt(cx*cx+cy*cy)*2.0; ang=np.arctan2(cy,cx)
    wr=r*(1+0.03*np.sin(ang*2+0.7)+0.02*np.sin(ang*5+2.1))+0.008*fbm(S,3.2,seed,fmin=2)
    nr=11.5
    rr=wr*nr; fr=rr-np.floor(rr)
    late=smooth(0.72,0.9,fr)*(1-smooth(0.93,1.0,fr))
    wood=ramp3(smooth(0.05,0.85,r),(0.62,0.44,0.26),(0.78,0.60,0.38),(0.86,0.70,0.48),0.5)
    col=wood*(1-0.42*late[...,None])
    col=col*(1+0.05*fbm(S,2.4,seed+3,fmin=6)[...,None])
    barkm=smooth(0.885,0.905,r)
    bark=np.array([0.24,0.16,0.10],f32)*(0.75+0.45*(fbm(S,2,seed+1,fmin=20)*0.5+0.5))[...,None]
    cambium=smooth(0.86,0.88,r)*(1-barkm)
    col=col*(1-0.35*cambium[...,None])
    col=col*(1-barkm[...,None])+bark*barkm[...,None]
    crack=np.zeros((S,S),f32)
    for i in range(4):
        a0=rng.uniform(-math.pi,math.pi); r_in=rng.uniform(0.35,0.6)
        da=np.abs(((ang-a0)+math.pi)%(2*math.pi)-math.pi)
        wid=0.012+0.05*np.clip((r-r_in)/(0.9-r_in),0,1)
        crack=np.maximum(crack,(1-smooth(0.0,wid,da*np.maximum(r,1e-3)*1.0))*(r>r_in)*(r<0.9))
    pith=1-smooth(0.015,0.04,r)
    col=col*(1-0.8*crack[...,None])*(1-0.5*pith[...,None])
    h=np.clip(0.55-0.04*late-0.4*crack+0.18*barkm*(0.6+0.4*(fbm(S,2,seed+2,fmin=20)*0.5+0.5)),0,1)
    rough=np.clip(0.8+0.15*barkm,0,1)
    PBR_SETS["T_VK_EndGrain"]=dict(depth=0.01,tile=0.6)
    return write_set("T_VK_EndGrain",col.astype(f32),h.astype(f32),rough.astype(f32),0.01,0.6,ao_in_albedo=0.3)
