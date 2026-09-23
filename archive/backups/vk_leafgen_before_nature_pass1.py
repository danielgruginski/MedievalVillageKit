
LEAF_CELLS=["broadleaf","broadleaf_dark","autumn_orange","autumn_red",
            "birch","pine","willow","fern",
            "berry","blossom","apple","hydrangea",
            "reeds","tallgrass","wildflowers","deadtwigs"]
AT=2048; CS=AT//4
def cell_bounds(name,m=6):
    i=LEAF_CELLS.index(name); cx=i%4; cy=i//4
    return (cx*CS+m, cy*CS+m, (cx+1)*CS-m, (cy+1)*CS-m)
class Painter:
    def __init__(s,S):
        s.S=S; s.img=np.zeros((S,S,3),f32); s.a=np.zeros((S,S),f32); s.h=np.zeros((S,S),f32)
    def _box(s,B,x0,y0,x1,y1):
        x0=int(max(B[0],math.floor(x0))); x1=int(min(B[2],math.ceil(x1))); y0=int(max(B[1],math.floor(y0))); y1=int(min(B[3],math.ceil(y1)))
        return (x0,y0,x1,y1) if (x1>x0 and y1>y0) else None
    def put(s,bx,cov,col,h):
        x0,y0,x1,y1=bx
        reg=s.img[y0:y1,x0:x1]; a=cov[...,None]
        reg[:]=reg*(1-a)+col*a
        ar=s.a[y0:y1,x0:x1]; ar[:]=np.maximum(ar,cov)
        hr=s.h[y0:y1,x0:x1]; hr[:]=hr*(1-cov)+h*cov
    def inside(s,B,x,y,m=0,mb=None):
        mb=m if mb is None else mb
        return B[0]+m<=x<=B[2]-m and B[1]+m<=y<=B[3]-mb
    def seg(s,B,ax,ay,bx_,by,w,col,h=0.35,col2=None):
        r=w*0.5+2
        bb=s._box(B,min(ax,bx_)-r,min(ay,by)-r,max(ax,bx_)+r,max(ay,by)+r)
        if not bb: return
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        dx,dy=bx_-ax,by-ay; L2=dx*dx+dy*dy+1e-6
        t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/L2,0,1)
        d=np.hypot(xx-(ax+t*dx),yy-(ay+t*dy))
        cov=np.clip(w*0.5-d+0.5,0,1)
        if cov.max()<=0: return
        q=np.clip(1-d/(w*0.5+1e-3),0,1)
        c0=np.array(col,f32)[None,None,:]
        if col2 is not None: c0=c0*(1-t[...,None])+np.array(col2,f32)[None,None,:]*t[...,None]
        c=c0*(0.72+0.34*q)[...,None]
        s.put(bb,cov,c,h*(0.6+0.4*q))
    def poly(s,B,pts,w0,w1,col,h=0.35,col2=None):
        n=len(pts)-1
        for i in range(n):
            w=w0+(w1-w0)*i/max(1,n-1)
            c=col if col2 is None else tuple(np.array(col)+(np.array(col2)-np.array(col))*i/max(1,n-1))
            s.seg(B,pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],w,c,h)
    def fitL(s,B,x,y,ang,L,W):
        ca,sa=math.cos(ang),math.sin(ang); m=W+3; lim=L
        if ca>1e-4: lim=min(lim,(B[2]-m-x)/ca)
        if ca<-1e-4: lim=min(lim,(B[0]+m-x)/ca)
        if sa>1e-4: lim=min(lim,(B[3]-m-y)/sa)
        if sa<-1e-4: lim=min(lim,(B[1]+m-y)/sa)
        return lim
    def leaf(s,B,x,y,ang,L,W,col,kind=0,bend=0.0,side=1.0,fit=True,minL=18):
        if not s.inside(B,x,y,W*0.5): return
        if fit:
            L2=s.fitL(B,x,y,ang,L,W)
            if L2<minL: return
            if L2<L: W=W*(0.6+0.4*L2/L); L=L2
        ca,sa=math.cos(ang),math.sin(ang)
        mx=x+ca*L/2; my=y+sa*L/2; R=L/2+W+3
        bb=s._box(B,mx-R,my-R,mx+R,my+R)
        if not bb: return
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        dx=xx-x; dy=yy-y
        sl=(dx*ca+dy*sa)/L; tt=(-dx*sa+dy*ca)
        slc=np.clip(sl,0,1)
        tt=tt-bend*L*np.sin(np.pi*slc)
        if kind==2: prof=W*np.sqrt(np.clip(1-(2*slc-1)**2,0,1))
        elif kind==3: prof=W*np.clip(1-slc,0,1)**0.8*np.clip(slc*8,0,1)
        else:
            prof=W*np.clip(np.sin(np.pi*slc),0,1)**0.7*(1-0.3*slc)
            if kind==1: prof=prof*(0.66+0.34*np.abs(np.cos(3.5*np.pi*slc)))
        cov=np.clip(prof-np.abs(tt)+0.7,0,1)*((sl>0)&(sl<1))
        if cov.max()<=0: return
        rel=np.abs(tt)/np.maximum(prof,1e-3)
        shade=0.74+0.36*slc+0.07*np.sign(tt)*side
        mid=1-0.25*np.exp(-(tt/1.3)**2)*(slc<0.95)
        vein=1-0.08*((np.abs(np.sin((slc*7-rel*1.3)*np.pi))<0.14)&(rel<0.85))
        edge=1-0.18*np.clip(1-(prof-np.abs(tt))/2.5,0,1)
        c=np.array(col,f32)[None,None,:]*(shade*mid*vein*edge)[...,None]
        hh=0.45+0.4*np.sqrt(np.clip(1-rel**2,0,1))*np.clip(np.sin(np.pi*slc),0,1)**0.4-0.1*(1-mid)
        s.put(bb,cov,c,hh)
    def disc(s,B,x,y,r,col,h=0.7,hl=True):
        if not s.inside(B,x,y,r+1): return
        bb=s._box(B,x-r-2,y-r-2,x+r+2,y+r+2)
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        d=np.hypot(xx-x,yy-y); cov=np.clip(r-d+0.7,0,1)
        q=np.clip(1-d/r,0,1)
        c=np.array(col,f32)[None,None,:]*(0.6+0.48*np.sqrt(q))[...,None]
        if hl:
            hd=np.hypot(xx-(x-r*0.35),yy-(y-r*0.38)); hi=np.clip(1-hd/(r*0.32),0,1)**1.5
            c=c*(1-hi[...,None]*0.75)+np.array([1,0.98,0.92],f32)*hi[...,None]*0.75
        s.put(bb,cov,c,h*np.sqrt(np.clip(1-(d/r)**2,0,1)))
    def flower(s,B,x,y,r,n,col,ccol,rot=0.0,inner=0.25,sharp=0.8,h=0.6,ragged=0.0):
        if not s.inside(B,x,y,r+1): return
        bb=s._box(B,x-r-2,y-r-2,x+r+2,y+r+2)
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        dx=xx-x; dy=yy-y; d=np.hypot(dx,dy); th=np.arctan2(dy,dx)+rot
        R=r*(0.5+0.5*np.abs(np.cos(n*th/2))**sharp)
        if ragged: R=R*(1-ragged*np.abs(np.sin(n*3*th)))
        cov=np.clip(R-d+0.7,0,1)
        if cov.max()<=0: return
        q=np.clip(d/r,0,1)
        c=np.array(col,f32)[None,None,:]*(0.7+0.4*q)[...,None]
        sep=np.abs(np.cos(n*th/2))<0.1
        c=c*(1-0.22*(sep&(q>inner))[...,None])
        ci=np.clip((inner*r-d)*0.8+0.5,0,1)
        c=c*(1-ci[...,None])+np.array(ccol,f32)[None,None,:]*(0.75+0.35*np.clip(1-d/(inner*r+1e-3),0,1))[...,None]*ci[...,None]
        s.put(bb,cov,c,h*(0.6+0.4*(1-q)))
def twig(P,B,rng,x0,y0,ang,L,w,col,depth,maxd,out,leaf_step=18,nkids=2,curl=0.12,kid_ang=(0.45,0.85),kid_len=(0.5,0.7)):
    n=max(3,int(L/10)); pts=[(x0,y0)]; a=ang; x,y=x0,y0
    for i in range(n):
        a+=rng.uniform(-curl,curl); nx=x+math.cos(a)*L/n; ny=y+math.sin(a)*L/n
        if not P.inside(B,nx,ny,26,2): break
        x,y=nx,ny; pts.append((x,y))
    if len(pts)<2: return
    P.poly(B,pts,w,max(1.2,w*0.45),col)
    acc=0.0
    for i in range(1,len(pts)):
        (xa,ya),(xb,yb)=pts[i-1],pts[i]; acc+=math.hypot(xb-xa,yb-ya)
        if acc>=leaf_step: acc=0.0; out.append((xb,yb,math.atan2(yb-ya,xb-xa),depth,False))
    xa,ya=pts[-2]; out.append((pts[-1][0],pts[-1][1],math.atan2(pts[-1][1]-ya,pts[-1][0]-xa),depth,True))
    if depth<maxd:
        for kk in range(nkids):
            t=rng.uniform(0.3,0.85); i=max(1,int(t*(len(pts)-1))); bx,by=pts[i]
            sd=1 if kk%2==0 else -1
            twig(P,B,rng,bx,by,a+sd*rng.uniform(*kid_ang),L*rng.uniform(*kid_len),w*0.6,col,depth+1,maxd,out,leaf_step,nkids,curl,kid_ang,kid_len)
def fan_twigs(P,B,rng,nt=5,spread=1.0,Lf=(0.42,0.58),w=6,stem=(0.30,0.21,0.12),maxd=2,leaf_step=20,kid_ang=(0.55,1.1),kid_len=(0.45,0.65),curl=0.1,droop=0.0):
    cx=(B[0]+B[2])/2; bot=B[3]-4; H=B[3]-B[1]; pts=[]
    for i in range(nt):
        f=(i/(nt-1)-0.5) if nt>1 else 0.0
        ang=-math.pi/2+f*2*spread+rng.uniform(-0.12,0.12)
        L=H*rng.uniform(*Lf)*(1-0.25*abs(f)*2)
        twig(P,B,rng,cx+rng.uniform(-8,8),bot,ang,L,w,stem,0,maxd,pts,leaf_step=leaf_step,nkids=2,curl=curl,kid_ang=kid_ang,kid_len=kid_len)
    return pts
def draw_leaves(P,B,rng,pts,pal,kind=0,Lr=(70,105),Wr=(0.28,0.36),ang_off=(0.5,1.1),droop=0.0):
    order=list(range(len(pts))); rng.shuffle(order)
    for j in order:
        x,y,a,d,tip=pts[j]
        for sd in ((0,) if tip else (-1,1)):
            aa=a+rng.uniform(-0.2,0.2) if sd==0 else a+sd*rng.uniform(*ang_off)
            if droop: aa=aa+(math.pi/2-aa)*droop*rng.uniform(0.5,1.0) if abs(((aa-math.pi/2)+math.pi)%(2*math.pi)-math.pi)<2.2 else aa
            L=rng.uniform(*Lr)*(0.85 if d>=2 else 1.0); W=L*rng.uniform(*Wr)
            col=np.array(pal[rng.integers(0,len(pal))],f32)*rng.uniform(0.88,1.12)
            P.leaf(B,x,y,aa,L,W,col,kind=kind,bend=rng.uniform(-0.1,0.1),side=sd or 1)
def cell_broad(P,name,rng,pal,kind=0,dens=1.0,Lr=(70,105),Wr=(0.28,0.36),stem=(0.30,0.21,0.12),maxd=2,nt=5,spread=1.0,Lf=(0.42,0.58)):
    B=cell_bounds(name)
    pts=fan_twigs(P,B,rng,nt=nt,spread=spread,Lf=Lf,stem=stem,maxd=maxd,leaf_step=22/dens)
    draw_leaves(P,B,rng,pts,pal,kind,Lr,Wr)
    return B,pts
def cell_pine(P,rng):
    B=cell_bounds("pine"); cx=(B[0]+B[2])/2; bot=B[3]-4
    dark=np.array((0.12,0.34,0.22),f32); tipc=np.array((0.32,0.58,0.34),f32)
    def spray(x0,y0,ang,L,w,nl):
        pts=[(x0,y0)]; a=ang; x,y=x0,y0; n=max(4,int(L/7))
        for i in range(n):
            a+=rng.uniform(-0.04,0.04); nx=x+math.cos(a)*L/n; ny=y+math.sin(a)*L/n
            if not P.inside(B,nx,ny,18,2): break
            x,y=nx,ny; pts.append((x,y))
        P.poly(B,pts,w,max(1.5,w*0.4),(0.32,0.22,0.13))
        return pts
    def needles(pts,Lmax,taper=True):
        N=len(pts)
        for i in range(1,N):
            (xa,ya),(xb,yb)=pts[i-1],pts[i]; a=math.atan2(yb-ya,xb-xa)
            f=i/(N-1); Ln=Lmax*((1-0.55*f) if taper else 1.0)
            for sd in (-1,1):
                for rep in range(2):
                    na=a+sd*rng.uniform(0.45,0.85); Lr=Ln*rng.uniform(0.8,1.1)
                    ex=xb+math.cos(na)*Lr; ey=yb+math.sin(na)*Lr
                    if not P.inside(B,ex,ey,4): continue
                    c1=dark*rng.uniform(0.85,1.15); c2=tipc*rng.uniform(0.85,1.15)
                    P.seg(B,xb,yb,ex,ey,rng.uniform(3.0,4.2),c1,0.5,col2=c2)
    main=spray(cx+rng.uniform(-10,10),bot,-math.pi/2+rng.uniform(-0.06,0.06),(B[3]-B[1])*0.92,8,0)
    for k in range(12):
        if len(main)<3: break
        t=0.08+0.72*k/11+rng.uniform(-0.03,0.03); i=max(1,int(t*(len(main)-1))); bx,by=main[i]
        sd=1 if k%2==0 else -1
        br=spray(bx,by,-math.pi/2+sd*rng.uniform(0.7,1.05),rng.uniform(170,230)*(1-0.6*t),5,0)
        needles(br,rng.uniform(38,50))
    needles(main,rng.uniform(48,60))
def cell_willow(P,rng):
    B=cell_bounds("willow"); pal=[(0.46,0.62,0.18),(0.37,0.53,0.14),(0.56,0.67,0.24),(0.30,0.46,0.12)]
    for k in range(5):
        x0=B[0]+55+k*(B[2]-B[0]-110)/4+rng.uniform(-12,12); ph=rng.uniform(0,6.28); amp=rng.uniform(8,22)
        pts=[]
        for i in range(34):
            t=i/33; y=B[1]+4+t*(B[3]-B[1]-10); x=x0+amp*math.sin(t*math.pi*1.2+ph)+t*t*rng.uniform(-10,10)
            pts.append((x,y))
        P.poly(B,pts,2.8,1.4,(0.34,0.36,0.14))
        acc=0
        for i in range(1,len(pts)):
            (xa,ya),(xb,yb)=pts[i-1],pts[i]
            for sd in (-1,1):
                if rng.random()<0.85:
                    a=math.pi/2+sd*rng.uniform(0.3,0.65)
                    L=rng.uniform(40,58); col=np.array(pal[rng.integers(0,4)],f32)*rng.uniform(0.88,1.12)
                    P.leaf(B,xb,yb,a,L,rng.uniform(7,9.5),col,kind=0,bend=rng.uniform(-0.12,0.12),side=sd)
def cell_fern(P,rng):
    B=cell_bounds("fern"); pal=[(0.22,0.48,0.13),(0.28,0.55,0.16),(0.18,0.42,0.11),(0.34,0.60,0.2)]
    x0=B[0]+215; y0=B[3]-4; H=B[3]-B[1]-10
    pts=[]
    for i in range(60):
        t=i/59; pts.append((x0+95*t**1.6, y0-H*t))
    P.poly(B,pts,7,2,(0.30,0.36,0.14))
    for i in range(3,len(pts)-1,2):
        t=i/59; (xa,ya),(xb,yb)=pts[i-1],pts[i]; a=math.atan2(yb-ya,xb-xa)
        Lp=175*(1-t)**0.75*min(1,t*6)
        for sd in (-1,1):
            col=np.array(pal[rng.integers(0,4)],f32)*rng.uniform(0.9,1.1)
            P.leaf(B,xb,yb,a+sd*rng.uniform(1.05,1.3),Lp,Lp*0.17,col,kind=1,bend=0.05*sd,side=sd,minL=10)
def cell_berry(P,rng):
    pal=[(0.16,0.40,0.12),(0.21,0.46,0.14),(0.26,0.52,0.17),(0.13,0.34,0.11)]
    B,pts=cell_broad(P,"berry",rng,pal,kind=0,dens=0.9,Lr=(62,92))
    for k in range(9 if pts else 0):
        x,y,a,d,tip=pts[rng.integers(0,len(pts))]
        cx=x+rng.uniform(-25,25); cy=y+rng.uniform(-25,10)
        for j in range(rng.integers(4,8)):
            bx=cx+rng.uniform(-18,18); by=cy+rng.uniform(-16,16)
            col=(0.80,0.07,0.10) if rng.random()<0.75 else (0.52,0.04,0.12)
            P.disc(B,bx,by,rng.uniform(9,12.5),col,0.8)
def cell_blossom(P,rng):
    B=cell_bounds("blossom"); cx=(B[0]+B[2])/2; bot=B[3]-4; H=B[3]-B[1]
    pts=fan_twigs(P,B,rng,nt=5,spread=1.0,Lf=(0.42,0.58),w=6,stem=(0.30,0.19,0.13),maxd=2,leaf_step=18)
    for (x,y,a,d,tip) in pts[::2]:
        for sd in (-1,1):
            if rng.random()<0.5: P.leaf(B,x,y,a+sd*rng.uniform(0.6,1.0),rng.uniform(40,55),rng.uniform(13,17),np.array((0.42,0.62,0.2),f32)*rng.uniform(0.9,1.1),kind=0,side=sd)
    pinks=[(0.98,0.72,0.82),(0.95,0.60,0.74),(1.0,0.84,0.90),(0.90,0.52,0.68)]
    for (x,y,a,d,tip) in pts:
        for j in range(3 if tip else 2):
            fx=x+rng.uniform(-24,24); fy=y+rng.uniform(-24,24)
            P.flower(B,fx,fy,rng.uniform(19,27),5,pinks[rng.integers(0,4)],(0.98,0.85,0.35),rot=rng.uniform(0,6.28),inner=0.22,sharp=0.6)
def cell_apple(P,rng):
    pal=[(0.26,0.50,0.12),(0.33,0.56,0.15),(0.22,0.44,0.10),(0.40,0.60,0.18)]
    B,pts=cell_broad(P,"apple",rng,pal,kind=0,dens=0.9,Lr=(65,95))
    picks=rng.choice(len(pts),min(6,len(pts)),replace=False) if pts else []
    for j in picks:
        x,y,a,d,tip=pts[j]; ax=x+rng.uniform(-10,10); ay=y+rng.uniform(8,22); r=rng.uniform(22,29)
        if not P.inside(B,ax,ay,r+2): continue
        P.seg(B,ax,ay-r*0.7,ax+rng.uniform(-6,6),ay-r*1.25,3,(0.28,0.2,0.1))
        P.disc(B,ax,ay,r,(0.80,0.12,0.08),0.9)
        bb=P._box(B,ax-r,ay-r,ax+r,ay+r); x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32); d=np.hypot(xx-ax,yy-ay)
        blush=np.clip((yy-(ay-r*0.2))/(r*1.2),0,1)*np.clip(r-d,0,1)*0.6
        reg=P.img[y0:y1,x0:x1]; reg[:]=reg*(1-blush[...,None])+np.array((0.85,0.62,0.16),f32)*blush[...,None]
def cell_hydrangea(P,rng):
    B=cell_bounds("hydrangea"); cx=(B[0]+B[2])/2; bot=B[3]-4
    pal=[(0.12,0.30,0.10),(0.16,0.36,0.12),(0.20,0.40,0.14)]
    for k in range(12):
        a=-math.pi/2+rng.uniform(-1.3,1.3); x=cx+rng.uniform(-60,60); y=bot-rng.uniform(10,120)
        P.leaf(B,x,y,a,rng.uniform(105,145),rng.uniform(42,55),np.array(pal[rng.integers(0,3)],f32)*rng.uniform(0.9,1.1),kind=0,bend=rng.uniform(-0.1,0.1))
    balls=[(cx-95,B[1]+170,95),(cx+95,B[1]+150,100),(cx+5,B[1]+300,105)]
    # one palette per flower head: lilac-blue / soft pink-white / soft blue. The blues are the old vivid ones
    # desaturated ~35% towards their luma. The rng draws are unchanged (base_i is still drawn), so every other
    # atlas cell stays identical.
    heads=[[(0.57,0.52,0.76),(0.67,0.57,0.80),(0.60,0.56,0.80),(0.52,0.50,0.74)],
           [(0.86,0.62,0.72),(0.84,0.80,0.78),(0.80,0.56,0.68),(0.88,0.84,0.82)],
           [(0.48,0.55,0.79),(0.55,0.65,0.84),(0.43,0.48,0.72),(0.52,0.58,0.80)]]
    for bi,(bx,by,br) in enumerate(balls):
        base_i=rng.integers(0,5); cols=heads[bi]
        for j in range(95):
            rr=br*math.sqrt(rng.random()); aa=rng.uniform(0,6.28); fx=bx+math.cos(aa)*rr; fy=by+math.sin(aa)*rr
            shade=0.8+0.3*(1-(fy-by+br)/(2*br))
            c=np.array(cols[(base_i+rng.integers(0,2))%len(cols)],f32)*shade*rng.uniform(0.92,1.08)
            P.flower(B,fx,fy,rng.uniform(12,16),4,c,(0.95,0.95,0.85),rot=rng.uniform(0,6.28),inner=0.16,sharp=0.5)
def blades(P,B,rng,n,Lr,wr,spread,cols,tipc=None,xmargin=40):
    for i in range(n):
        x=rng.uniform(B[0]+xmargin,B[2]-xmargin); y=B[3]-4; a=-math.pi/2+rng.uniform(-spread,spread); L=rng.uniform(*Lr); w=rng.uniform(*wr)
        pts=[(x,y)]
        for j in range(12):
            a+=rng.uniform(-0.03,0.03)+0.012*(1 if a>-math.pi/2 else -1)
            nx=pts[-1][0]+math.cos(a)*L/12; ny=pts[-1][1]+math.sin(a)*L/12
            if not P.inside(B,nx,ny,6): break
            pts.append((nx,ny))
        c=np.array(cols[rng.integers(0,len(cols))],f32)*rng.uniform(0.88,1.15)
        P.poly(B,pts,w,1.2,tuple(c),0.45,col2=tuple(c*1.25) if tipc is None else tipc)
    return
def cell_reeds(P,rng):
    B=cell_bounds("reeds")
    blades(P,B,rng,34,(300,490),(7,11),0.14,[(0.36,0.54,0.22),(0.44,0.60,0.26),(0.30,0.48,0.20)])
    for k in range(6):
        x=rng.uniform(B[0]+60,B[2]-60); ytop=B[1]+rng.uniform(40,130)
        P.seg(B,x,B[3]-4,x+rng.uniform(-8,8),ytop,3.5,(0.36,0.42,0.2))
        P.seg(B,x,ytop+20,x,ytop-30,2.0,(0.4,0.36,0.22))
        P.seg(B,x,ytop+25,x,ytop+85,15,(0.38,0.21,0.10),0.8)
def cell_tallgrass(P,rng):
    B=cell_bounds("tallgrass")
    cols=[(0.50,0.68,0.21),(0.62,0.72,0.29),(0.70,0.74,0.36),(0.42,0.62,0.18)]
    blades(P,B,rng,60,(180,420),(5,9),0.36,cols)
    for k in range(12):
        x=rng.uniform(B[0]+60,B[2]-60); ytop=B[1]+rng.uniform(30,160)
        P.seg(B,x,B[3]-4,x+rng.uniform(-15,15),ytop,2.5,(0.5,0.56,0.26))
        for j in range(7):
            yy=ytop+j*10; 
            for sd in (-1,1): P.leaf(B,x,yy,-math.pi/2+sd*0.35,20,4.5,(0.78,0.72,0.46),kind=2,fit=True,minL=8)
def cell_wildflowers(P,rng):
    B=cell_bounds("wildflowers")
    blades(P,B,rng,30,(90,260),(5,8),0.45,[(0.30,0.50,0.14),(0.38,0.56,0.18)])
    kinds=[("poppy",(0.90,0.12,0.08),(0.12,0.08,0.06),5,(20,26),0.2,0.5,0.0),
           ("corn",(0.28,0.42,0.92),(0.2,0.22,0.5),10,(16,21),0.18,1.5,0.25),
           ("butter",(0.98,0.84,0.16),(0.9,0.6,0.1),5,(12,15),0.22,0.5,0.0),
           ("daisy",(0.97,0.96,0.92),(0.96,0.72,0.12),12,(14,18),0.3,1.2,0.0)]
    for k in range(26):
        kd=kinds[rng.integers(0,4)]
        x=rng.uniform(B[0]+40,B[2]-40); y=B[1]+rng.uniform(40,(B[3]-B[1])*0.62)
        P.seg(B,x+rng.uniform(-15,15),B[3]-4,x,y+kd[4][0],2.4,(0.30,0.46,0.14))
        P.flower(B,x,y,rng.uniform(*kd[4]),kd[3],kd[1],kd[2],rot=rng.uniform(0,6.28),inner=kd[5],sharp=kd[6],ragged=kd[7])
def cell_deadtwigs(P,rng):
    B=cell_bounds("deadtwigs"); cx=(B[0]+B[2])/2
    def rec(x,y,a,L,w,d):
        pts=[(x,y)]; n=max(3,int(L/12))
        for i in range(n):
            a+=rng.uniform(-0.18,0.18); nx=pts[-1][0]+math.cos(a)*L/n; ny=pts[-1][1]+math.sin(a)*L/n
            if not P.inside(B,nx,ny,8,2): break
            pts.append((nx,ny))
        c=np.array((0.34,0.27,0.20),f32)*rng.uniform(0.85,1.2)
        P.poly(B,pts,w,max(1.2,w*0.55),tuple(c),0.4,col2=tuple(c*1.25))
        if d<5 and len(pts)>2:
            for kk in range(2 if d<3 else rng.integers(1,3)):
                i=rng.integers(1,len(pts)); bx,by=pts[i]
                rec(bx,by,a+(1 if kk%2==0 else -1)*rng.uniform(0.35,0.8),L*rng.uniform(0.5,0.72),w*0.62,d+1)
    for a0 in (-math.pi/2-0.5,-math.pi/2,-math.pi/2+0.5):
        rec(cx+rng.uniform(-10,10),B[3]-4,a0+rng.uniform(-0.1,0.1),(B[3]-B[1])*rng.uniform(0.45,0.6),11,0)
def paint_leaf_atlas(seed=301):
    P=Painter(AT); rng=np.random.default_rng(seed)
    broad=[(0.26,0.53,0.12),(0.34,0.61,0.15),(0.43,0.68,0.19),(0.21,0.46,0.10),(0.50,0.72,0.22)]
    dark=[(0.14,0.35,0.10),(0.19,0.42,0.12),(0.24,0.46,0.14),(0.12,0.30,0.10)]
    aor=[(0.86,0.46,0.08),(0.95,0.62,0.12),(0.78,0.32,0.06),(0.92,0.74,0.20),(0.70,0.40,0.08)]
    ard=[(0.72,0.14,0.07),(0.86,0.26,0.08),(0.58,0.10,0.07),(0.90,0.46,0.10),(0.80,0.20,0.10)]
    birch=[(0.52,0.70,0.18),(0.62,0.76,0.23),(0.44,0.63,0.14),(0.70,0.80,0.30)]
    cell_broad(P,"broadleaf",rng,broad,kind=0,dens=0.72,Lr=(95,135),nt=3,spread=0.75,Lf=(0.5,0.7))
    cell_broad(P,"broadleaf_dark",rng,dark,kind=0,dens=0.95,Lr=(85,120),nt=4,spread=0.9)
    cell_broad(P,"autumn_orange",rng,aor,kind=1,dens=0.75,Lr=(95,130),Wr=(0.36,0.44),nt=3,spread=0.75,Lf=(0.5,0.7))
    cell_broad(P,"autumn_red",rng,ard,kind=1,dens=0.75,Lr=(95,130),Wr=(0.36,0.44),nt=3,spread=0.75,Lf=(0.5,0.7))
    Bb=cell_bounds("birch")
    ptsb=fan_twigs(P,Bb,rng,nt=5,spread=1.15,Lf=(0.4,0.55),w=4,stem=(0.36,0.30,0.24),maxd=2,leaf_step=15,kid_ang=(0.7,1.3),kid_len=(0.5,0.75),curl=0.14)
    draw_leaves(P,Bb,rng,ptsb,birch,kind=0,Lr=(36,50),Wr=(0.45,0.58),ang_off=(0.7,1.3))
    cell_pine(P,rng); cell_willow(P,rng); cell_fern(P,rng)
    cell_berry(P,rng); cell_blossom(P,rng); cell_apple(P,rng); cell_hydrangea(P,rng)
    cell_reeds(P,rng); cell_tallgrass(P,rng); cell_wildflowers(P,rng); cell_deadtwigs(P,rng)
    return P
def repaint_leaf_cell(cell,seed=301,name="T_VK_Leaves",dry=False,save=True,inset=5):
    # Re-paint ONE atlas cell in place. The atlas shares one rng across all cells and rng use does not depend on
    # pixel content, so replaying paint_leaf_atlas with a painter that only draws into `cell` reproduces that
    # cell exactly while every other cell of the existing image stays bit-identical (it is never written).
    # The height map is not touched: only use this for colour-only changes (same rng draws, same shapes).
    # dry=True: returns the max abs difference between the replay and the current image (a check that the
    # replay is exact before a colour change is made).
    TB=cell_bounds(cell); Base=Painter
    class _Only(Base):
        def seg(s,B,*a,**k):
            if B==TB: return Base.seg(s,B,*a,**k)
        def leaf(s,B,*a,**k):
            if B==TB: return Base.leaf(s,B,*a,**k)
        def disc(s,B,*a,**k):
            if B==TB: return Base.disc(s,B,*a,**k)
        def flower(s,B,*a,**k):
            if B==TB: return Base.flower(s,B,*a,**k)
    G=globals(); G["Painter"]=_Only
    try: P=paint_leaf_atlas(seed)
    finally: G["Painter"]=Base
    rgb=P.img.copy(); a=P.a; m=a>0.5
    for _ in range(10):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    S=P.S; rgba=np.concatenate([np.clip(rgb,0,1),a[...,None]],-1).astype(f32)[::-1]
    im=bpy.data.images[name+"_BCA"]
    cur=np.zeros(S*S*4,f32); im.pixels.foreach_get(cur); cur=cur.reshape(S,S,4)
    i=LEAF_CELLS.index(cell); cx=i%4; cy=i//4
    r0=S-(cy+1)*CS+inset; r1=S-cy*CS-inset; c0=cx*CS+inset; c1=(cx+1)*CS-inset
    if dry: return float(np.abs(cur[r0:r1,c0:c1]-rgba[r0:r1,c0:c1]).max())
    cur[r0:r1,c0:c1]=rgba[r0:r1,c0:c1]
    im.pixels.foreach_set(cur.ravel()); im.update()
    if save:
        im.filepath_raw=os.path.join(TEXDIR,name+"_BCA.png"); im.file_format="PNG"; im.save(); im.pack()
    return im
def save_leaf_atlas(P,name="T_VK_Leaves"):
    img=P.img.copy(); a=P.a.copy()
    rgb=img.copy(); m=a>0.5
    for _ in range(10):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    S=P.S
    rgba=np.concatenate([np.clip(rgb,0,1),a[...,None]],-1).astype(f32)
    im=bpy.data.images.get(name+"_BCA")
    if im is None: im=bpy.data.images.new(name+"_BCA",S,S,alpha=True)
    elif tuple(im.size)!=(S,S): im.scale(S,S)
    im.alpha_mode="STRAIGHT"
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel()); im.update()
    im.filepath_raw=os.path.join(TEXDIR,name+"_BCA.png"); im.file_format="PNG"; im.save(); im.pack()
    nrm=normal_from_height(blur(P.h,0.8),0.012,3.0)*0.5+0.5
    write_map(name+"_N",nrm,True)
