# ===================== FRONTIER PACK (prefix fro_) =====================
# Log-cabin walls (3.0 m, interlocking notched corners), plank sheds (2.6 m), open post bays,
# the S roof family (3 m deep, ridge 2.27) and frontier buildings.
# Executed after vk_helpers in the same namespace: every kit function / constant is available.

# ---------------------------------------------------------------- constants
fro_HS=2.6                 # shed wall top
fro_LOG_Y=-0.09            # log centre line (outer face at -0.255)
fro_ZA=0.47                # course 0 of long-side walls (phase A: walls along local/world X)
fro_ZB=0.62                # course 0 of end walls      (phase B: walls along world Y), half a course up
fro_DZ=0.30                # course pitch
fro_NC=9                   # courses per 3.0 m wall
fro_LOG_T=1.5              # texture tile along logs (3 m / 1.5 = 2 tiles -> seamless between modules)
fro_SEG=12                 # log sides

def fro_pick(name,fallback):
    return name if bpy.data.objects.get(name) else fallback

# ---------------------------------------------------------------- S roof family (context manager)
class fro_roof_family:
    """with fro_roof_family("S"): ... temporarily switches HALF/EAVE/RIDGE/GX (restored in __exit__)"""
    FAM={"M":(3.0,1.35,0.95),"S":(1.5,0.90,0.60)}
    def __init__(s,fam): s.fam=fam
    def __enter__(s):
        global HALF,EAVE,RIDGE,GX
        s.old=(HALF,EAVE,RIDGE,GX)
        try:
            h,over,gxo=fro_roof_family.FAM[s.fam]
            HALF=h; EAVE=h+over; GX=1.5+gxo; RIDGE=roof_z(0)
        except Exception:
            HALF,EAVE,RIDGE,GX=s.old; raise
        return s
    def __exit__(s,*exc):
        global HALF,EAVE,RIDGE,GX
        HALF,EAVE,RIDGE,GX=s.old
        return False

def fro_roof_profile():
    over=EAVE-HALF
    ys=[HALF*t for t in (0,.25,.5,.75,1)]+[HALF+over/3,HALF+2*over/3,EAVE]
    return [(y,roof_z(y)) for y in ys]

def fro_under(ay):
    return roof_z(ay)-RT/math.cos(PITCH)-0.05

def fro_roof_slab(k,x0,x1,side,end_caps=(False,False)):
    """copy of the kit roof_slab driven by fro_roof_profile (works for M and S)"""
    prof=fro_roof_profile(); nx=max(2,int(round((x1-x0)/0.5)))
    xs=[x0+(x1-x0)*i/nx for i in range(nx+1)]
    dist=[0.0]*len(prof)
    for i in range(len(prof)-2,-1,-1):
        dist[i]=dist[i+1]+math.hypot(prof[i+1][0]-prof[i][0],prof[i+1][1]-prof[i][1])
    top=[];bot=[]
    for x in xs:
        rt=[];rb=[]
        for j,(ay,z) in enumerate(prof):
            a=prof[max(j-1,0)]; b=prof[min(j+1,len(prof)-1)]
            ty,tz=b[0]-a[0],b[1]-a[1]; L=math.hypot(ty,tz); ny,nz=tz/L,-ty/L
            if nz<0: ny,nz=-ny,-nz
            zz=z+roof_sag(x,ay)
            rt.append(k.bm.verts.new((x,side*ay,zz)))
            rb.append(k.bm.verts.new((x,side*(ay-ny*RT),zz-nz*RT)))
        top.append(rt); bot.append(rb)
    def F(vs,mi,uvs):
        if side>0: vs=vs[::-1]; uvs=uvs[::-1]
        f=k.bm.faces.new(vs); f.material_index=mi
        for l,u in zip(f.loops,uvs): l[k.uv].uv=u
        return f
    T=TILE[ROOF]; W=TILE[WOOD]
    for i in range(nx):
        for j in range(len(prof)-1):
            F([top[i][j],top[i][j+1],top[i+1][j+1],top[i+1][j]],ROOF,
              [(xs[i]/T,dist[j]/T),(xs[i]/T,dist[j+1]/T),(xs[i+1]/T,dist[j+1]/T),(xs[i+1]/T,dist[j]/T)])
            F([bot[i+1][j],bot[i+1][j+1],bot[i][j+1],bot[i][j]],WOOD,
              [(xs[i+1]/W,dist[j]/W),(xs[i+1]/W,dist[j+1]/W),(xs[i]/W,dist[j+1]/W),(xs[i]/W,dist[j]/W)])
        j=len(prof)-1
        F([top[i][j],top[i+1][j],bot[i+1][j],bot[i][j]],WOOD,[(xs[i]/W,0),(xs[i+1]/W,0),(xs[i+1]/W,RT/W),(xs[i]/W,RT/W)])
        F([bot[i][0],bot[i+1][0],top[i+1][0],top[i][0]],WOOD,[(0,0),(1,0),(1,0.2),(0,0.2)])
    for ci,(cap,xi) in enumerate(zip(end_caps,(0,nx))):
        if not cap: continue
        for j in range(len(prof)-1):
            vs=[top[xi][j],top[xi][j+1],bot[xi][j+1],bot[xi][j]]
            if (ci==0)==(side>0): vs=vs[::-1]
            f=k.bm.faces.new(vs); f.material_index=WOOD
            for l in f.loops: l[k.uv].uv=(l.vert.co.y/W,l.vert.co.z/W)
    k.bm.normal_update()

def fro_thatch_slab(k,x0,x1,side,end_caps=(False,False)):
    global RT
    before=set(k.bm.faces); old=RT; RT=TRT
    try: fro_roof_slab(k,x0,x1,side,end_caps)
    finally: RT=old
    for f in k.bm.faces:
        if f not in before: f.material_index=THATCH

def fro_thatch_rake_roll(k,xg,seed=0.0):
    """kit thatch_rake_roll driven by fro_roof_profile"""
    prof=fro_roof_profile()
    pts=[(-y,z) for (y,z) in reversed(prof)]+[(y,z) for (y,z) in prof[1:]]
    R=TRT/2+0.06; nt=10; rings=[]
    for idx,(y,z) in enumerate(pts):
        a=pts[max(idx-1,0)]; b=pts[min(idx+1,len(pts)-1)]
        ty,tz=b[0]-a[0],b[1]-a[1]; L=math.hypot(ty,tz); ty/=L; tz/=L
        ny,nz=-tz,ty
        if nz<0: ny,nz=-ny,-nz
        Nn=Vector((0,ny,nz)); X=Vector((1,0,0))
        C=Vector((xg-0.06,y,z))-Nn*(TRT/2)
        rr=R*(1+0.1*_pnoise(y*1.3,seed))
        rings.append([k.bm.verts.new(C+(X*math.cos(math.pi/2-math.pi*j/nt)+Nn*math.sin(math.pi/2-math.pi*j/nt))*rr) for j in range(nt+1)])
    fs=[]
    for i in range(len(rings)-1):
        for j in range(nt):
            fs.append(k.bm.faces.new((rings[i][j],rings[i][j+1],rings[i+1][j+1],rings[i+1][j])))
    k.bm.normal_update()
    if fs[len(fs)//2].normal.x<0:
        for f in fs: f.normal_flip()
    T=TILE[THATCH]
    for f in fs:
        f.material_index=THATCH; f.smooth=True
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.y/T*0.5,0.03+0.05*((p.z%1.0)))
    for s_ in(-1,1):
        _ico(k,(xg-0.08,s_*(EAVE-0.05),roof_z(EAVE)-TRT/2),R*1.05,THATCH,sub=2,jit=0.02,seed=int(seed*10)+s_)

def fro_mirror_merge(k,fn):
    """build fn(sub) and merge it mirrored across x=0 (winding fixed)"""
    sub=Kit(); fn(sub)
    bmesh.ops.reverse_faces(sub.bm,faces=list(sub.bm.faces))
    merge_kit(k,sub,Matrix.Scale(-1,4,(1,0,0)))

# ---------------------------------------------------------------- logs
def fro_course_r(phase,i):
    """radius + texture offset of course i (same seeds for walls, corners and gables)"""
    rnd=random.Random((101 if phase=="A" else 202)*1000+i)
    return 0.165+rnd.uniform(-0.015,0.015), rnd.random()

def fro_course_z(phase,i):
    """centre height of course i (a few cm of seeded irregularity, identical in walls, corners and gables)"""
    rnd=random.Random((303 if phase=="A" else 404)*1000+i)
    return (fro_ZA if phase=="A" else fro_ZB)+fro_DZ*i+rnd.uniform(-0.012,0.012)

def fro_log(k,x0,x1,r,M,caps=(False,False),rfun=None,voff=0.0,seed=0,tilt=0.045,ch=0.035,mi=None,seg=None,step=0.75):
    """round log along local X (x0..x1), radius r*rfun(x), placed by matrix M.
       caps: chamfered ENDGRAIN discs (slightly slanted saw cuts). Open ends are for seams."""
    mi=WOOD if mi is None else mi; seg=seg or fro_SEG
    rnd=random.Random(seed)
    nl=max(1,int(round((x1-x0)/step)))
    xs=[x0+(x1-x0)*i/nl for i in range(nl+1)]
    if caps[0] and caps[0]!="flat": xs[0]=x0+ch
    if caps[1] and caps[1]!="flat": xs[-1]=x1-ch
    rf=rfun or (lambda x:1.0)
    def ring(x,rr,dx=None):
        out=[]
        for j in range(seg):
            a=2*math.pi*j/seg
            xx=x+(dx(a) if dx else 0.0)
            out.append(k.bm.verts.new(M@Vector((xx,rr*math.cos(a),rr*math.sin(a)))))
        return out
    rings=[ring(x,r*rf(x)) for x in xs]
    T=fro_LOG_T; C=2*math.pi*r/T
    def quads(ra,rb,xa,xb,mat):
        for j in range(seg):
            j2=(j+1)%seg
            f=k.bm.faces.new((ra[j],ra[j2],rb[j2],rb[j])); f.material_index=mat
            for l,(xx,jj) in zip(f.loops,((xa,j),(xa,j+1),(xb,j+1),(xb,j))):
                l[k.uv].uv=(xx/T,jj/seg*C+voff)
    for i in range(len(xs)-1): quads(rings[i],rings[i+1],xs[i],xs[i+1],mi)
    for e in (0,1):
        if not caps[e]: continue
        xe=x0 if e==0 else x1
        phi=rnd.uniform(0,2*math.pi); tl=rnd.uniform(-tilt,tilt)
        if caps[e]=="flat":
            rc=rings[-1] if e==1 else rings[0]
        else:
            rc=ring(xe,r*rf(xe)*0.84,lambda a,phi=phi,tl=tl: tl*math.cos(a-phi))
            if e==1: quads(rings[-1],rc,xs[-1],xe,mi)
            else: quads(rc,rings[0],xe,xs[0],mi)
        f=k.bm.faces.new(rc if e==1 else rc[::-1]); f.material_index=ENDGRAIN
        rot=rnd.uniform(0,2*math.pi)
        for l in f.loops:
            j=rc.index(l.vert); a=2*math.pi*j/seg+rot
            l[k.uv].uv=(0.5+0.46*math.cos(a),0.5+0.46*math.sin(a))
    k.bm.normal_update()

def fro_Mx(y,z): return Matrix.Translation((0,y,z))                                   # log along X
def fro_My(x,z): return Matrix.Translation((x,0,z))@Matrix.Rotation(math.pi/2,4,"Z")   # log along Y (local x -> world +Y)

def fro_bulge(x): return 1.0+0.03*math.sin(math.pi*(x+1.5)/3.0)    # zero at the module seams

def fro_log_plinth(k,x0,x1,top,seed=0,y=-0.09,tall=False):
    """stone footing under a log wall: skirt to -0.6 plus chunky rocks proud of the log face"""
    k.box(((x0+x1)/2,y,(top-0.1-0.6)/2),(x1-x0,0.40,top-0.1+0.6),STONE,bevel=0)
    rnd=random.Random(seed); x=x0
    while x<x1-0.12:
        w=min(rnd.uniform(0.45,0.8),x1-x)
        if x1-(x+w)<0.3: w=x1-x
        h=rnd.uniform(0.40,0.52)+(0.14 if tall else 0.0); d=rnd.uniform(0.30,0.38)
        zc=top-h/2+rnd.uniform(-0.05,0.02)
        rock(k,(x+w/2,y-0.19+d/2-0.12,zc),(w-0.05,d,h),seed=rnd.randrange(1<<30),tilt=0.05)
        x+=w

def fro_chink(k,x0,x1,zc,y=fro_LOG_Y-0.085):
    """daub chinking in the groove between two courses (PLASTER -> recolours with the plaster style)"""
    if x1-x0<0.05: return
    k.box(((x0+x1)/2,y,zc),(x1-x0,0.07,0.06),PLASTER,bevel=0)

def fro_segments(x0,x1,cuts):
    """split [x0,x1] by cut intervals -> list of (a,b,cap_a,cap_b)"""
    out=[]; a=x0; ca=False
    for (c0,c1) in sorted(cuts):
        if c1<=a or c0>=x1: continue
        if c0>a: out.append((a,c0,ca,True))
        a=max(a,c1); ca=True
    if a<x1: out.append((a,x1,ca,False))
    return out

def fro_log_wall(k,phase="A",kind="."):
    """Wall_Log (phase A: courses at 0.47+0.3i) / Wall_Log_B (phase B: 0.62+0.3i). kind . W D"""
    z0=fro_ZA if phase=="A" else fro_ZB
    ptop=z0-0.14
    fro_log_plinth(k,-1.5,1.5,ptop,seed={".":3,"W":5,"D":7}[kind]+(0 if phase=="A" else 20),tall=(phase=="B"))
    zs=[fro_course_z(phase,i) for i in range(fro_NC)]
    cut={}
    if kind=="W":
        for i in (3,4,5): cut[i]=[(-0.55,0.55)]
        wz0=zs[2]+0.165; wz1=zs[6]-0.165
    if kind=="D":
        for i in range(7): cut[i]=[(-0.6,0.6)]
        cut[7]=[(-0.9,0.9)]
    for i,z in enumerate(zs):
        r,vo=fro_course_r(phase,i)
        for (a,b,ca,cb) in fro_segments(-1.5,1.5,cut.get(i,[])):
            if kind=="D" and i==7: ca=cb=False       # hidden inside the lintel
            fro_log(k,a,b,r,fro_Mx(fro_LOG_Y,z),caps=(ca,cb),rfun=fro_bulge,voff=vo,seed=i*31+len(kind)+(0 if phase=="A" else 500)+int(a*10))
        if i<fro_NC-1:
            cc=sorted(set(cut.get(i,[]))|set(cut.get(i+1,[])))
            for (a,b,_,_) in fro_segments(-1.5,1.5,cc): fro_chink(k,a+(0.05 if a>-1.5 else 0),b-(0.05 if b<1.5 else 0),z+fro_DZ/2)
    if kind=="W": fro_log_window(k,-0.55,0.55,wz0,wz1)
    if kind=="D": fro_log_door(k,phase,zs,ptop)

def fro_log_window(k,x0,x1,z0,z1):
    w=x1-x0; h=z1-z0
    xi0,xi1=x0+0.08,x1-0.08
    k.quad([(xi0,-0.05,z0),(xi1,-0.05,z0),(xi1,-0.05,z1),(xi0,-0.05,z1)],WINDOW,uvs=[(0,0),(xi1-xi0,0),(xi1-xi0,h),(0,h)])
    for sx in (x0+0.045,x1-0.045): k.box((sx,-0.03,(z0+z1)/2),(0.09,0.16,h+0.04),WOOD,bevel=0.02)
    k.box(((x0+x1)/2,-0.2,z1+0.03),(w+0.34,0.3,0.15),WOOD,bevel=0.035)                 # head board
    k.box(((x0+x1)/2,-0.25,z0-0.03),(w+0.4,0.36,0.1),WOOD,bevel=0.03)                  # sill board
    for sx in (-0.4,0.4): k.box((sx*w/1.1,-0.36,z0-0.12),(0.07,0.1,0.18),WOOD,bevel=0.015)   # sill brackets
    k.box(((x0+x1)/2,-0.07,(z0+z1)/2),(0.06,0.05,h),WOOD,bevel=0.01)
    k.box(((x0+x1)/2,-0.07,z0+h*0.55),(w-0.16,0.05,0.06),WOOD,bevel=0.01)
    shutter(k,x0-0.08,-1,z0+0.02,h-0.04,w=0.52)
    shutter(k,x1+0.08,1,z0+0.02,h-0.04,w=0.52)

def fro_log_door(k,phase,zs,ptop):
    hw=0.6; zb=ptop; ztop=zs[7]-0.21
    # lintel log (proud, heavier) replaces course 7 over the opening
    fro_log(k,-0.95,0.95,0.205,fro_Mx(fro_LOG_Y-0.03,zs[7]+0.01),caps=(True,True),voff=0.3,seed=77,tilt=0.03)
    for sx in (-1,1): k.box((sx*(hw-0.05),-0.02,(zb+ztop)/2),(0.1,0.15,ztop-zb),WOOD,bevel=0.02)   # jamb boards
    k.box((0,-0.1,zb-0.03),(2*hw+0.1,0.38,0.1),WOOD,bevel=0.03)                                   # sill board
    # VOID behind (interior) over a plank floor at the sill, door leaf ajar 20 degrees inward
    k.quad([(-0.85,-0.05,zb-0.005),(0.85,-0.05,zb-0.005),(0.85,0.5,zb-0.005),(-0.85,0.5,zb-0.005)],PLANKS,uvs=[(0,0),(1.7,0),(1.7,0.55),(0,0.55)])
    k.quad([(-0.85,0.5,zb-0.05),(0.85,0.5,zb-0.05),(0.85,0.5,ztop+0.2),(-0.85,0.5,ztop+0.2)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.quad([(-0.85,0.5,zb-0.05),(-0.85,0.5,ztop+0.2),(-0.85,0.05,ztop+0.2),(-0.85,0.05,zb-0.05)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.quad([(0.85,0.5,zb-0.05),(0.85,0.05,zb-0.05),(0.85,0.05,ztop+0.2),(0.85,0.5,ztop+0.2)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    lw=2*hw-0.12; lh=ztop-zb-0.03
    M=Matrix.Translation((-hw+0.1,0.0,zb+0.01))@Matrix.Rotation(math.radians(20),4,"Z")
    sub=Kit()
    nb=5; bw=lw/nb
    for i in range(nb):
        fro_board(sub,i*bw,(i+1)*bw-0.012,0,lh-(0.0 if i%2 else 0.03),-0.03,0.03,col=i+2)
    for zz in (0.35,lh-0.35): sub.box((lw/2,-0.05,zz),(lw-0.08,0.04,0.13),WOOD,bevel=0.015)
    L=math.hypot(lw-0.25,lh-0.85); ang=math.atan2(lh-0.85,lw-0.25)
    sub.box((lw/2,-0.05,lh/2),(L,0.04,0.12),WOOD,rot=(0,-ang,0),bevel=0.015)
    for zz in (0.35,lh-0.35): sub.box((0.28,-0.08,zz),(0.5,0.02,0.06),IRON,bevel=0.005)
    _cyl(sub,(lw-0.18,-0.09,lh*0.47),0.05,0.05,0.02,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
    merge_kit(k,sub,M)
    # stone step
    rock(k,(0.05,-0.62,0.09),(1.3,0.55,0.3),seed=41,tilt=0.03)
    k.box((0.05,-0.62,-0.3),(1.1,0.45,0.6),STONE,bevel=0)

def fro_corner_log(k,xphase="A"):
    """notched corner: log ends of both walls cross and stick out ~0.25 m past the faces.
       Corner_Log: X arm = phase A (use at rot 0/180). Corner_Log_B: X arm = phase B (use at rot 90/-90)."""
    yphase="B" if xphase=="A" else "A"
    rock(k,(-0.12,-0.12,0.2),(0.85,0.85,0.46),seed=11,tilt=0.03)
    k.box((-0.1,-0.1,-0.25),(0.62,0.62,0.7),STONE,bevel=0)
    for ph,arm in ((xphase,"x"),(yphase,"y")):
        z0=fro_ZA if ph=="A" else fro_ZB
        # the top phase-B course sits at the eave line: its stub would pierce the roof, so it stops at the wall
        for i in range(fro_NC if ph=="A" else fro_NC-1):
            r,vo=fro_course_r(ph,i); z=fro_course_z(ph,i)
            rnd=random.Random((1 if ph=="A" else 2)*1000+(1 if arm=="x" else 2)*100+i)
            e=-0.47-rnd.uniform(0.0,0.1)
            M=fro_Mx(fro_LOG_Y,z) if arm=="x" else fro_My(fro_LOG_Y,z)
            fro_log(k,e,0.0,r,M,caps=(True,False),voff=vo,seed=i*13+(1 if arm=="x" else 2),rfun=lambda x,e=e: 1.0-0.04*(x/e))

def fro_gable_logs(k,XF=1.755):
    """gable triangle of stacked phase-B logs, cut to the rake, small window, purlin ends and crossed horns"""
    xc=XF-0.165
    j=0; logs=[]
    while True:
        z=fro_course_z("B",fro_NC+j)-H1
        if z>fro_under(0)-0.2: break
        u=z-0.12
        ay=HALF-(u-0.35+RT/math.cos(PITCH)+0.05)/math.tan(PITCH)
        logs.append((j,z,max(0.25,ay))); j+=1
    wz0,wz1,wy=1.07,1.67,0.34
    for (j,z,ay) in logs:
        r,vo=fro_course_r("B",fro_NC+j)
        cuts=[(-wy,wy)] if wz0<z<wz1 else []
        for (a,b,ca,cb) in fro_segments(-ay,ay,cuts):
            # outer ends tuck into the roof slab (flat caps); window cuts get chamfered end grain
            fro_log(k,a,b,r,fro_My(xc,z),caps=(True if ca else "flat",True if cb else "flat"),voff=vo,seed=900+j*7+int(a*10),step=3.0)
    for n_ in range(len(logs)-1):
        j,z,ay=logs[n_]; ay2=logs[n_+1][2]
        L=min(ay,ay2)-0.1
        zc=z+fro_DZ/2
        cuts=[(-wy-0.05,wy+0.05)] if wz0-0.2<zc<wz1+0.2 else []
        for (a,b,_,_) in fro_segments(-L,L,cuts):
            k.box((xc+0.105,(a+b)/2,zc),(0.07,b-a,0.085),PLASTER,bevel=0.02)
    # gable window
    xw=xc+0.02
    k.quad([(xw,wy-0.06,wz0),(xw,wy-0.06,wz1),(xw,-wy+0.06,wz1),(xw,-wy+0.06,wz0)],WINDOW,uvs=[(0,0),(0,0.6),(0.56,0.6),(0.56,0)])
    for sy in (-wy+0.04,wy-0.04): k.box((xc+0.03,sy,(wz0+wz1)/2),(0.16,0.09,wz1-wz0+0.05),WOOD,bevel=0.02)
    k.box((xc+0.1,0,wz1+0.03),(0.26,2*wy+0.3,0.14),WOOD,bevel=0.03)
    k.box((xc+0.12,0,wz0-0.03),(0.3,2*wy+0.3,0.09),WOOD,bevel=0.03)
    k.box((xc+0.05,0,(wz0+wz1)/2),(0.05,0.05,wz1-wz0),WOOD,bevel=0.01)
    k.box((xc+0.05,0,(wz0+wz1)/2+0.04),(0.05,2*wy-0.1,0.05),WOOD,bevel=0.01)
    # purlin ends carrying the verge (ridge + one each side)
    for ay_ in (0.0,-HALF*0.52,HALF*0.52):
        zp=fro_under(abs(ay_))-0.13
        fro_log(k,xc-0.35,GX+0.12,0.13,fro_Mx(ay_,zp),caps=(False,True),voff=0.2,seed=int(ay_*10)+71,tilt=0.02,step=3.0,seg=10)

def fro_bargeboards(k,finial="post"):
    prof=fro_roof_profile()
    for s in(-1,1):
        for j in range(len(prof)-1):
            (y0,z0),(y1,z1)=prof[j],prof[j+1]
            L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,y1-y0)
            k.box((GX+0.08,s*(y0+y1)/2,(z0+z1)/2-0.16),(0.2,L+0.2,0.46),WOOD,rot=(s*ang,0,0),bevel=0.05,segs=1)
    if finial=="post":
        k.box((GX+0.08,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,segs=2)
        k.box((GX+0.08,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)
    elif finial=="horns":
        # crossed barge ends ("horns"): each rake board continues past the apex
        (y0,z0),(y1,z1)=prof[0],prof[1]; ang=math.atan2(z1-z0,y1-y0)
        for s in(-1,1):
            d=0.3
            k.box((GX+0.08,-s*d,RIDGE-0.16+d*math.tan(PITCH)),(0.17,0.72,0.26),WOOD,rot=(s*ang,0,0),bevel=0.05,segs=1)

def fro_gable_end(k,kind="timber",XF=1.9,trim=True,window=None,finial="post"):
    """generalised gable_end for any roof family (M or S) plus the 'logs' kind"""
    if window is None: window=HALF>=3
    if trim: fro_bargeboards(k,finial)
    if kind=="logs":
        fro_gable_logs(k,XF); return
    YC=HALF+0.02; XB=1.5-0.05; top=fro_under(0)
    TRI={"timber":PLASTER,"planks":PLANKS,"stone":ASHLAR}[kind]
    ys=[YC]+[HALF*t for t in (5/6,4/6,3/6,2/6,1/6,0)]
    outline=[(-YC,0.0),(YC,0.0)]+[(y,fro_under(y)) for y in ys]+[(-y,fro_under(y)) for y in ys[::-1][1:]]
    for (xf,flip) in ((XF-0.06,False),(XB,True)):
        vs=[k.bm.verts.new((xf,y,z)) for y,z in outline]
        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=TRI
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[TRI],l.vert.co.z/TILE[TRI])
    k.bm.normal_update()
    if kind=="timber":
        k.box((XF-0.02,0,0.12),(0.2,2*YC,0.24),WOOD,bevel=0.04)
        for i in range(int(round(2*HALF))):
            k.box((XF+0.1,-(HALF-0.5)+i,-0.12),(0.3,0.16,0.2),WOOD,bevel=0.03)
        zc=top*0.45; half_c=YC*(1-zc/top)*0.98
        k.box((XF-0.02,0,zc),(0.18,2*half_c,0.2),WOOD,bevel=0.035)
        k.box((XF-0.02,0,top/2),(0.18,0.24,top),WOOD,bevel=0.035)
        for s_ in(-1,1):
            L=math.hypot(YC,top); ang=math.atan2(top,YC)
            k.box((XF-0.02,s_*YC/2,top/2-0.14),(0.18,L,0.2),WOOD,rot=(-s_*ang,0,0),bevel=0.035)
            k.box((XF-0.02,s_*1.6*HALF/3,zc/2+0.1),(0.16,0.16,zc-0.1),WOOD,bevel=0.03)
        if window:
            wz=zc+0.25
            k.quad([(XF-0.04,-0.35,wz),(XF-0.04,0.35,wz),(XF-0.04,0.35,wz+0.8),(XF-0.04,-0.35,wz+0.8)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,0.8),(0,0.8)])
            for yy in(-0.42,0.42): k.box((XF+0.02,yy,wz+0.4),(0.14,0.13,0.95),WOOD,bevel=0.025)
            for zz in(wz-0.05,wz+0.85): k.box((XF+0.02,0,zz),(0.16,0.95,0.13),WOOD,bevel=0.025)
    elif kind=="planks":
        for y in (-HALF*0.73,-HALF*0.37,HALF*0.37,HALF*0.73):
            h=top*(1-abs(y)/YC)-0.1
            if h>0.15: k.box((XF+0.0,y,h/2),(0.07,0.12,h),WOOD,bevel=0.02)
        k.box((XF+0.0,0,0.12),(0.16,2*YC,0.2),WOOD,bevel=0.03)
        # small loft hatch with one leaf swung open
        hy=0.3; hz0=0.34; hz1=min(1.0,top-0.45)
        k.quad([(XF-0.03,-hy,hz0),(XF-0.03,hy,hz0),(XF-0.03,hy,hz1),(XF-0.03,-hy,hz1)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for yy in (-hy-0.05,hy+0.05): k.box((XF+0.02,yy,(hz0+hz1)/2),(0.1,0.1,hz1-hz0+0.1),WOOD,bevel=0.02)
        for zz in (hz0-0.04,hz1+0.04): k.box((XF+0.02,0,zz),(0.1,2*hy+0.2,0.09),WOOD,bevel=0.02)
        sub=Kit()
        for i in range(2): sub.box((0.02,0.15+i*0.3,(hz1-hz0)/2),(0.05,0.29,hz1-hz0-0.02),PLANKS,bevel=0.01)
        sub.box((0.06,0.3,(hz1-hz0)/2),(0.03,0.55,0.08),WOOD,bevel=0.01)
        merge_kit(k,sub,Matrix.Translation((XF+0.02,-hy-0.02,hz0))@Matrix.Rotation(math.radians(-100),4,"Z"))
    elif kind=="stone":
        k.box((XF+0.02,0,0.12),(0.3,2*YC,0.26),ASHLAR,bevel=0.04)

# ---------------------------------------------------------------- log family pieces
def fro_wall_log(k): fro_log_wall(k,"A",".")
def fro_wall_log_window(k): fro_log_wall(k,"A","W")
def fro_wall_log_door(k): fro_log_wall(k,"A","D")
def fro_wall_log_b(k): fro_log_wall(k,"B",".")
def fro_wall_log_b_window(k): fro_log_wall(k,"B","W")
def fro_wall_log_b_door(k): fro_log_wall(k,"B","D")
def fro_corner_log_a(k): fro_corner_log(k,"A")
def fro_corner_log_b(k): fro_corner_log(k,"B")
def fro_roof_gable_logs(k):
    with fro_roof_family("M"):
        for s in(-1,1): fro_roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
        ridge(k,-1.5,GX+0.1)
        fro_gable_end(k,"logs",XF=1.755,finial="horns")

# ---------------------------------------------------------------- S roofs
fro_XF_S={"timber":1.78,"planks":1.60}
def fro_roofS_mid(k):
    with fro_roof_family("S"):
        for s in(-1,1): fro_roof_slab(k,-1.5,1.5,s); eave_tabs(k,-1.5,1.5,s)
        ridge(k,-1.5,1.5)
def fro_roofS_gable(k,kind="timber"):
    with fro_roof_family("S"):
        for s in(-1,1): fro_roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
        ridge(k,-1.5,GX+0.1)
        fro_gable_end(k,kind,XF=fro_XF_S[kind],window=False)
def fro_roofS_single(k,kind="planks"):
    with fro_roof_family("S"):
        for s in(-1,1): fro_roof_slab(k,-GX,GX,s,end_caps=(True,True)); eave_tabs(k,-GX,GX,s)
        ridge(k,-GX-0.1,GX+0.1)
        fro_gable_end(k,kind,XF=fro_XF_S[kind],window=False)
        fro_mirror_merge(k,lambda sub: fro_gable_end(sub,kind,XF=fro_XF_S[kind],window=False))
def fro_roofthatchS_mid(k):
    with fro_roof_family("S"):
        for s in(-1,1): fro_thatch_slab(k,-1.5,1.5,s); thatch_eave_roll(k,-1.5,1.5,s,seed=1.0+s)
        thatch_ridge_cap(k,-1.5,1.5)
def fro_roofthatchS_gable(k):
    with fro_roof_family("S"):
        for s in(-1,1): fro_thatch_slab(k,-1.5,GX,s,end_caps=(False,True)); thatch_eave_roll(k,-1.5,GX,s,seed=1.0+s)
        thatch_ridge_cap(k,-1.5,GX+0.05)
        fro_thatch_rake_roll(k,GX,seed=2.0)
        fro_gable_end(k,"timber",XF=fro_XF_S["timber"],trim=False,window=False)
def fro_roofthatchS_single(k):
    with fro_roof_family("S"):
        for s in(-1,1): fro_thatch_slab(k,-GX,GX,s,end_caps=(True,True)); thatch_eave_roll(k,-GX,GX,s,seed=1.0+s)
        thatch_ridge_cap(k,-GX-0.05,GX+0.05)
        fro_thatch_rake_roll(k,GX,seed=2.0)
        fro_gable_end(k,"timber",XF=fro_XF_S["timber"],trim=False,window=False)
        def back(sub):
            fro_thatch_rake_roll(sub,GX,seed=3.0)
            fro_gable_end(sub,"timber",XF=fro_XF_S["timber"],trim=False,window=False)
        fro_mirror_merge(k,back)

# ---------------------------------------------------------------- shed family (2.6 m)
fro_BOARD=0.25     # board width = one painted board of T_VK_Planks at tile 2.0

def fro_board(k,x0,x1,z0,z1,y0,y1,col=0,rot=(0,0,0),voff=0.0,bevel=0.012,xform=None,axis="y"):
    """one PLANKS board whose broad-face UVs show exactly one painted board (column col of 8).
       axis="y": broad faces face +-Y, grain along Z (wall boards); axis="z": broad faces +-Z, grain along Y (floors)"""
    vs=k.box(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),PLANKS,rot=rot,bevel=bevel,xform=xform)
    fs={f for v in vs for f in v.link_faces}
    cx=(x0+x1)/2
    Minv=xform.inverted() if xform is not None else None
    for f in fs:
        n=f.normal if Minv is None else (Minv.to_3x3()@f.normal)
        if abs(n.y if axis=="y" else n.z)<0.7: continue
        for l in f.loops:
            p=l.vert.co if Minv is None else Minv@l.vert.co
            u=((col%8)+0.5+(p.x-cx)/(x1-x0)*0.92)/8.0
            l[k.uv].uv=(u,(p.z if axis=="y" else p.y)/2.0+voff)

def fro_shed_boards(k,cuts=(),seed=0,z_lo=0.30,z_hi=None):
    """vertical boards x -1.5..1.5 (12 x 0.25), y -0.06..0.0; cuts: list of (x0,x1,z0,z1) holes"""
    z_hi=z_hi or fro_HS-0.18
    rnd=random.Random(seed)
    for i in range(12):
        x0=-1.5+i*fro_BOARD; x1=x0+fro_BOARD-0.012
        zb=z_lo+rnd.uniform(0.0,0.07); zt=z_hi
        spans=[(zb,zt)]
        for (c0,c1,cz0,cz1) in cuts:
            if x1<=c0+0.01 or x0>=c1-0.01: continue
            new=[]
            for (a,b) in spans:
                if cz1<=a or cz0>=b: new.append((a,b)); continue
                if cz0>a+0.05: new.append((a,cz0))
                if cz1<b-0.05: new.append((cz1,b))
            spans=new
        col=(i*3+seed)%8; tilt=rnd.uniform(-0.012,0.012)
        for (a,b) in spans:
            fro_board(k,x0,x1,a,b,-0.06,0.0,col=col,rot=(0,tilt,0),voff=rnd.random())

def fro_shed_frame(k,raised=False,battens=True,brace=True,cuts=()):
    if not raised:
        for i,x in enumerate((-1.2,0.0,1.2)):
            rock(k,(x,0.02,0.09),(0.44,0.42,0.32),seed=60+i,tilt=0.04)
        k.box((0,0.03,-0.22),(3.0,0.18,0.78),STONE,bevel=0)          # recessed footing / skirt
    else:
        k.box((0,0.03,0.02),(3.0,0.30,0.30),WOOD,bevel=0.04)         # heavy bearer on staddle stones
    k.box((0,0.03,0.25),(3.0,0.26,0.18),WOOD,bevel=0.035)            # sill beam 0.16..0.34
    k.box((0,0.03,fro_HS-0.1),(3.0,0.26,0.2),WOOD,bevel=0.035)       # top plate 2.4..2.6
    k.box((-1.5,-0.07,(0.34+fro_HS-0.2)/2),(0.16,0.1,fro_HS-0.2-0.34),WOOD,bevel=0.025)   # module post (outside)
    k.box((-1.5,0.08,(0.34+fro_HS-0.2)/2),(0.14,0.14,fro_HS-0.2-0.34),WOOD,bevel=0.02)   # inner stud
    if battens:
        for x in (-1.0,-0.5,0.0,0.5,1.0):
            if any(c0-0.05<x<c1+0.05 for (c0,c1,cz0,cz1) in cuts):
                for (c0,c1,cz0,cz1) in cuts:
                    if c0-0.05<x<c1+0.05:
                        if cz0>0.6: k.box((x,-0.08,(0.36+cz0-0.1)/2),(0.06,0.04,cz0-0.1-0.36),WOOD,bevel=0.012)
                        if cz1<fro_HS-0.5: k.box((x,-0.08,(cz1+0.1+fro_HS-0.22)/2),(0.06,0.04,fro_HS-0.22-cz1-0.1),WOOD,bevel=0.012)
                continue
            k.box((x,-0.08,(0.36+fro_HS-0.22)/2),(0.06,0.04,fro_HS-0.22-0.36),WOOD,bevel=0.012)
    if brace:
        x0,z0,x1,z1=-1.38,0.42,-0.1,fro_HS-0.3
        L=math.hypot(x1-x0,z1-z0); ang=math.atan2(z1-z0,x1-x0)
        k.box(((x0+x1)/2,-0.115,(z0+z1)/2),(L,0.05,0.13),WOOD,rot=(0,-ang,0),bevel=0.015)

def fro_shed_wall(k,kind=".",raised=False):
    if kind==".":
        fro_shed_frame(k,raised); fro_shed_boards(k,seed=1)
    elif kind=="D":
        hw=0.5; zt=2.3; cuts=[(-hw,hw,0.2,zt)]
        fro_shed_frame(k,raised,brace=False,cuts=cuts); fro_shed_boards(k,cuts=cuts,seed=2)
        fro_shed_door_frame(k,hw,zt)
        fro_shed_leaf(k,-hw,0.34,2*hw,zt-0.37,ang=-30,seed=3)
    elif kind=="B":
        hw=1.0; zt=2.36; cuts=[(-hw,hw,0.2,zt)]
        fro_shed_frame(k,raised,brace=False,cuts=cuts); fro_shed_boards(k,cuts=cuts,seed=4)
        fro_shed_door_frame(k,hw,zt)
        fro_shed_leaf(k,-hw,0.34,hw-0.01,zt-0.37,ang=0,seed=5)
        fro_shed_leaf(k,hw,0.34,hw-0.01,zt-0.37,ang=100,seed=6,mirror=True)
        _ico(k,(0.2,-0.35,0.36),0.34,HAY,scale=(1.5,1.0,0.35),sub=2,jit=0.04,seed=8)
    elif kind=="W":
        x0,x1,z0,z1=-0.25,0.25,1.45,1.95; cuts=[(x0,x1,z0,z1)]
        fro_shed_frame(k,raised,cuts=[(x0,x1,z0,z1)],brace=True); fro_shed_boards(k,cuts=cuts,seed=7)
        k.quad([(x0,0.0,z0),(x1,0.0,z0),(x1,0.0,z1),(x0,0.0,z1)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for sx in (x0-0.05,x1+0.05): k.box((sx,-0.08,(z0+z1)/2),(0.1,0.1,z1-z0+0.2),WOOD,bevel=0.02)
        k.box((0,-0.09,z0-0.06),(x1-x0+0.36,0.14,0.1),WOOD,bevel=0.02)
        k.box((0,-0.09,z1+0.06),(x1-x0+0.3,0.12,0.1),WOOD,bevel=0.02)
        for sx in (-0.08,0.08): k.box((sx,-0.02,(z0+z1)/2),(0.03,0.03,z1-z0),WOOD,bevel=0)
        # top-hinged flap propped open 45 degrees + prop stick
        sub=Kit()
        for i in range(2): fro_board(sub,-0.3+i*0.3,-0.3+i*0.3+0.29,-0.56,0.0,-0.02,0.03,col=i+2)
        sub.box((0,-0.035,-0.28),(0.56,0.03,0.07),WOOD,bevel=0.01)
        merge_kit(k,sub,Matrix.Translation((0,-0.14,z1+0.08))@Matrix.Rotation(math.radians(-45),4,"X"))
        a=math.radians(45); tip=Vector((0.2,-0.14-0.5*math.sin(a),z1+0.08-0.5*math.cos(a)))
        base=Vector((0.2,-0.12,z0-0.06)); d=tip-base
        k.box(tuple((tip+base)/2),(0.035,0.035,d.length),WOOD,rot=(math.atan2(-d.y,d.z),0,0),bevel=0.01)

def fro_shed_door_frame(k,hw,zt):
    for sx in (-1,1): k.box((sx*(hw+0.06),-0.08,(0.3+zt)/2),(0.12,0.12,zt-0.3+0.05),WOOD,bevel=0.025)
    k.box((0,-0.09,zt+0.06),(2*hw+0.4,0.14,0.14),WOOD,bevel=0.03)
    k.quad([(-hw,0.04,0.3),(hw,0.04,0.3),(hw,0.04,zt),(-hw,0.04,zt)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    rock(k,(0,-0.45,0.07),(2*hw+0.2,0.5,0.24),seed=int(hw*10)+90,tilt=0.02)

def fro_shed_leaf(k,hx,z0,w,h,ang=-30,seed=0,mirror=False):
    """plank door leaf hinged at x=hx (extends toward +x, or -x if mirror), Z-braced, rotated ang deg about z (negative = swung outward)"""
    sub=Kit(); nb=max(2,int(round(w/fro_BOARD))); bw=w/nb
    for i in range(nb): fro_board(sub,i*bw,(i+1)*bw-0.01,0,h,-0.025,0.025,col=(i+seed)%8,bevel=0.01)
    for zz in (0.3,h-0.3): sub.box((w/2,-0.05,zz),(w-0.1,0.04,0.13),WOOD,bevel=0.015)
    L=math.hypot(w-0.3,h-0.75); a=math.atan2(h-0.75,w-0.3)
    sub.box((w/2,-0.05,h/2),(L,0.04,0.12),WOOD,rot=(0,-a,0),bevel=0.015)
    for zz in (0.3,h-0.3): sub.box((0.22,-0.075,zz),(0.42,0.015,0.05),IRON,bevel=0.004)
    M=Matrix.Translation((hx,-0.03,z0))@Matrix.Rotation(math.radians(ang),4,"Z")
    if mirror:
        bmesh.ops.reverse_faces(sub.bm,faces=list(sub.bm.faces))
        M=M@Matrix.Scale(-1,4,(1,0,0))
    merge_kit(k,sub,M)

def fro_corner_shed(k,raised=False):
    if not raised:
        rock(k,(-0.06,-0.06,0.1),(0.5,0.5,0.34),seed=65,tilt=0.03)
        k.box((-0.06,-0.06,-0.3),(0.34,0.34,0.62),STONE,bevel=0)
    else:
        k.box((-0.06,-0.06,0.02),(0.4,0.4,0.3),WOOD,bevel=0.04)
    k.box((-0.06,-0.06,(0.2+fro_HS)/2),(0.28,0.28,fro_HS-0.2+0.02),WOOD,bevel=0.04,segs=2)
    k.box((-0.02,-0.02,fro_HS-0.1),(0.36,0.36,0.2),WOOD,bevel=0.04)

# ---------------------------------------------------------------- open post bays
def fro_brace(k,x0,z0,x1,z1,y,w=0.14):
    L=math.hypot(x1-x0,z1-z0); a=math.atan2(z1-z0,x1-x0)
    k.box(((x0+x1)/2,y,(z0+z1)/2),(L,w,w),WOOD,rot=(0,-a,0),bevel=0.025)

def fro_wall_posts(k,H=3.0):
    y=-0.05
    rock(k,(-1.5,y,0.1),(0.52,0.52,0.26),seed=int(H*10)+3,tilt=0.03)
    k.box((-1.5,y,-0.3),(0.36,0.36,0.6),STONE,bevel=0)
    k.box((-1.5,y,(0.2+H-0.3)/2),(0.28,0.28,H-0.3-0.2+0.02),WOOD,bevel=0.04,segs=2)
    k.box((0,y,H-0.15),(3.0,0.3,0.3),WOOD,bevel=0.04)
    d=0.5
    fro_brace(k,-1.5+0.1,H-0.3-d,-1.5+0.1+d,H-0.28,y)
    fro_brace(k,1.5-0.1,H-0.3-d,1.5-0.1-d,H-0.28,y)

def fro_corner_posts(k,H=3.0):
    rock(k,(-0.05,-0.05,0.1),(0.62,0.62,0.28),seed=int(H*10)+9,tilt=0.03)
    k.box((-0.05,-0.05,-0.3),(0.42,0.42,0.6),STONE,bevel=0)
    k.box((-0.05,-0.05,(0.2+H)/2),(0.34,0.34,H-0.2),WOOD,bevel=0.05,segs=2)
    k.box((-0.05,-0.05,H+0.02),(0.4,0.4,0.08),WOOD,bevel=0.02)
    d=0.5
    fro_brace(k,0.1,H-0.3-d,0.1+d,H-0.28,-0.05)
    sub=Kit(); fro_brace(sub,0.1,H-0.3-d,0.1+d,H-0.28,0.05)
    merge_kit(k,sub,Matrix.Rotation(math.pi/2,4,"Z"))

def fro_ceiling_cell(k,H=3.0):
    """loft floor for one cell (cell-centred, placed at the storey base): planks top at H-0.24, joists below"""
    for i in range(12):
        x0=-1.5+i*0.25
        fro_board(k,x0,x0+0.245,H-0.30,H-0.24,-1.5,1.5,col=(i*5)%8,bevel=0.008,axis="z",voff=(i*0.37)%1)
    for x in (-1.0,0.0,1.0):
        k.box((x,0,H-0.41),(0.2,3.0,0.22),WOOD,bevel=0.03)

# ---------------------------------------------------------------- granary props
def fro_staddle(k):
    prof=[(0.20,-0.6),(0.19,0.0),(0.155,0.2),(0.13,0.44),(0.35,0.5),(0.36,0.58),(0.30,0.645)]
    fs=lathe(k,prof,(0,0,0),segs=12,mi=ROCK,cap_top=True)
    rnd=random.Random(3)
    for v in {v for f in fs for v in f.verts}:
        if v.co.z>0.02: v.co+=Vector((rnd.uniform(-1,1)*0.012,rnd.uniform(-1,1)*0.012,rnd.uniform(-1,1)*0.008))
    k.bm.normal_update(); k.project(fs,ROCK)

def fro_tree_nursery(k):
    """Crop_TreeNursery: one 3x3 cell of soil ridges with 4 rows of young trees (forester's sapling beds).
       Rows 0/2 young conifers (stacked cones), rows 1/3 staked broadleaf whips; taller toward the back (+Y)."""
    soil_bed(k,rows=4,ridge_h=0.14)
    rnd=random.Random(7)
    for i in range(4):
        y=-1.45+(i+0.5)*2.9/4
        for j in range(4):
            x=-1.45+(j+0.5)*2.9/4+rnd.uniform(-0.08,0.08); yy=y+rnd.uniform(-0.05,0.05)
            h=(0.65+0.17*i)*rnd.uniform(0.85,1.12); z0=0.13
            if i%2==0:
                _cyl(k,(x,yy,z0+0.12),0.035,0.03,0.24,5,BARK_PINE)
                for t,(rr,dz) in enumerate(((0.30,0.16),(0.23,0.42),(0.15,0.66))):
                    c=_cyl(k,(x,yy,z0+h*dz+h*0.13),rr*h/0.9,0.0,h*0.36,7,MOSS,
                           rot=Matrix.Rotation(rnd.uniform(-0.08,0.08),4,"X")@Matrix.Rotation(rnd.uniform(0,1),4,"Z"))
            else:
                lean=Matrix.Rotation(rnd.uniform(-0.06,0.06),4,"Y")
                _cyl(k,(x,yy,z0+h*0.4),0.03,0.02,h*0.8,5,BARK_BIRCH,rot=lean)
                # leafy crown: small moss-green core + crossed ivy cards (same painted foliage as the crops)
                _ico(k,(x,yy,z0+h*0.8),0.1*h/0.9+0.04,MOSS,(1.0,1.0,1.3),sub=1,jit=0.015,seed=i*10+j)
                a0=rnd.uniform(0,math.pi)
                for t in range(3):
                    aa=a0+t*math.pi/3
                    card(k,(x,yy,z0+h*0.8),(math.cos(aa),math.sin(aa),0),(0,0,1),0.55*h/0.9+0.1,0.5*h/0.9+0.12,"ivy",flip=t%2==0)
                k.box((x+0.11,yy,z0+h*0.33),(0.045,0.045,h*0.66+0.1),WOOD,bevel=0.01)      # stake
                k.box((x+0.06,yy,z0+h*0.5),(0.13,0.05,0.035),BURLAP,bevel=0.005)          # tie
    # row-end marker pegs
    for i in range(4):
        y=-1.45+(i+0.5)*2.9/4
        k.box((-1.42,y,0.28),(0.06,0.06,0.42),WOOD,bevel=0.012,rot=(0,0.08,0))

def fro_granary_step(k):
    """3 detached stone steps (door-local, outer -Y); the top step ends 0.3 short of the wall face"""
    y=-0.4
    for i,(zt,dep) in enumerate(((0.84,0.38),(0.57,0.36),(0.3,0.38))):
        rock(k,(0,y-dep/2,zt-0.16),(1.1-i*0.0,dep+0.02,0.34),seed=120+i,tilt=0.025)
        k.box((0,y-dep/2,(zt-0.3-0.6)/2),(0.95,dep-0.04,zt-0.3+0.6),STONE,bevel=0)
        y-=dep

# ---------------------------------------------------------------- builders
fro_LOG_A={".":"SM_VK_Wall_Log","W":"SM_VK_Wall_Log_Window","D":"SM_VK_Wall_Log_Door"}
fro_LOG_B={".":"SM_VK_Wall_Log_B","W":"SM_VK_Wall_Log_B_Window","D":"SM_VK_Wall_Log_B_Door"}
fro_SHED={".":"SM_VK_Wall_Shed","D":"SM_VK_Wall_Shed_Door","B":"SM_VK_Wall_Shed_Wide","W":"SM_VK_Wall_Shed_Window"}
fro_SHED_R={".":"SM_VK_Wall_Shed_Raised","D":"SM_VK_Wall_Shed_Door_Raised"}

def fro_ring_walls(coll,origin,n,d,faces,st,fam,corners,z=0.0,cornerB=None,dress=None):
    """walls of an n x d cell rectangle centred on the local origin.
       faces: F (-Y, n chars), B (+Y, n chars), L (-X, d chars), R (+X, d chars), read left->right from outside.
       fam: {char: piece} for F/B, famB for L/R via fam if cornerB is None. corners: piece at rot 0/180, cornerB at +-90."""
    L=n*CELL; D=d*CELL; out=[]
    famF,famE=fam if isinstance(fam,tuple) else (fam,fam)
    for i,c in enumerate(faces["F"]): out.append((famF[c],-L/2+1.5+3*i,-D/2,0,c))
    for i,c in enumerate(faces["B"]): out.append((famF[c],L/2-1.5-3*i,D/2,180,c))
    for i,c in enumerate(faces["L"]): out.append((famE[c],-L/2,D/2-1.5-3*i,-90,c))
    for i,c in enumerate(faces["R"]): out.append((famE[c],L/2,-D/2+1.5+3*i,90,c))
    for (pc,x,y,r,c) in out:
        place_v(coll,pc,x,y,z,r,origin,st)
        if dress: dress(x,y,r,c)
    for (x,y,r) in ((-L/2,-D/2,0),(L/2,-D/2,90),(L/2,D/2,180),(-L/2,D/2,-90)):
        place_v(coll,corners if (cornerB is None or r in (0,180)) else cornerB,x,y,z,r,origin,st)
    return out

def fro_wall_local(x,y,rot,lx,ly):
    a=math.radians(rot); return (x+lx*math.cos(a)-ly*math.sin(a),y+lx*math.sin(a)+ly*math.cos(a))

def fro_log_dress(coll,origin,r,st):
    """weeds / flower boxes / lantern along the log walls (wall-local placement)"""
    def fn(x,y,rot,c):
        if c=="W" and r.random()<0.75:
            px,py=fro_wall_local(x,y,rot,0,-0.47)
            zb=1.0 if rot in (0,180) else 1.15
            place_v(coll,"SM_VK_Prop_FlowerBox" if r.random()<0.6 else "SM_VK_Prop_FlowerBox_Daisy",px,py,zb,rot,origin,{})
        if r.random()<0.5: place_v(coll,"SM_VK_Deco_Weeds",x,y-0.0,0,rot,origin,{})
        if c=="D":
            px,py=fro_wall_local(x,y,rot,1.0,-0.26)
            place_v(coll,"SM_VK_Prop_Lantern",px,py,2.3,rot,origin,{})
    return fn

def build_logcabin(coll,origin,seed=0,n=2):
    """frontier log cabin, n x 2 cells (n>=2): dark logs on a fieldstone footing, shingle roof with log gables,
       gable chimney on the L end, door on the long front (or on the R gable with a porch)."""
    r=random.Random(seed); n=max(2,n); L=n*CELL
    st={"roof":"Shingle","stone":"Field","plaster":r.choice(["Daub","Daub","Cream"]),
        "shutter":r.choice(["Red","Green","Natural","Blue","Teal"])}
    gable_door=r.random()<0.4
    front={2:"DW",3:"WDW"}.get(n,"W"+"D"+"W"*(n-2)) if not gable_door else ("W"*n if n<3 else "W.W"+"W"*(n-3))
    back="".join(r.choice(".W.") for _ in range(n-1))+"."        # last back cell (-X end) is blank: woodpile
    faces={"F":front,"B":back,"L":"..","R":("D." if gable_door else r.choice(["W.",".W",".."]))}
    fro_ring_walls(coll,origin,n,2,faces,st,(fro_LOG_A,fro_LOG_B),"SM_VK_Corner_Log",cornerB="SM_VK_Corner_Log_B",
                   dress=fro_log_dress(coll,origin,r,st))
    for i in range(n):
        x=-L/2+1.5+3*i
        pc="SM_VK_Roof_Gable_Logs" if i in (0,n-1) else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,H1,180 if i==0 else 0,origin,st)
    ch=fro_pick("SM_VK_Chimney_Gable_H30",None)
    if ch: place_v(coll,ch,-L/2,0,0,-90,origin,st)
    else:  place_v(coll,"SM_VK_Chimney",-L/2+1.5,0,H1,0,origin,st)
    if gable_door:
        place_v(coll,"SM_VK_Porch",L/2,-1.5,0,90,origin,st)
    # yard dressing
    place_v(coll,"SM_VK_Prop_Woodpile",-L/2+2.2,4.05,0,180,origin,{"roof":st["roof"]})   # against the blank back cell
    place_v(coll,"SM_VK_Stump",-L/2+0.4+r.uniform(-0.5,0.5),-4.6,0,r.uniform(0,360),origin,{})
    place_v(coll,fro_pick("SM_VK_Prop_ChoppingBlock","SM_VK_Stump"),L/2-0.8,-4.4,0,r.uniform(0,360),origin,{})
    place_v(coll,"SM_VK_Plant_TallGrass",L/2+1.2,2.6,0,r.uniform(0,360),origin,{})
    return dict(wall_top=H1,footprint=(n,2))

def build_woodcutter(coll,origin,seed=0):
    """woodcutter's lodge, lot 3x3: 2x2 log cabin + lean-to log store on the R gable, chopping yard, felled logs"""
    r=random.Random(seed+17)
    O=origin; c_,s_=math.cos(O[2]),math.sin(O[2])
    cab=(O[0]-1.5*c_-1.5*s_,O[1]-1.5*s_+1.5*c_,O[2])          # cabin in the back-left 2x2 of the 3x3 lot
    st={"roof":"Shingle","stone":"Field","plaster":"Daub","shutter":r.choice(["Red","Green","Natural"])}
    faces={"F":"DW","B":".W","L":"..","R":".."}
    fro_ring_walls(coll,cab,2,2,faces,st,(fro_LOG_A,fro_LOG_B),"SM_VK_Corner_Log",cornerB="SM_VK_Corner_Log_B",
                   dress=fro_log_dress(coll,cab,r,st))
    for i in range(2): place_v(coll,"SM_VK_Roof_Gable_Logs",-1.5+3*i,0,H1,180 if i==0 else 0,cab,st)
    ch=fro_pick("SM_VK_Chimney_Gable_H30",None)
    if ch: place_v(coll,ch,-3,0,0,-90,cab,st)
    else:  place_v(coll,"SM_VK_Chimney",-1.5,0,H1,0,cab,st)
    # lean-to log store against the R gable (x=+3 of the cabin), roof matches the cabin
    place_v(coll,"SM_VK_LeanTo",3,0,0,90,cab,{"roof":"Shingle"})
    pile=fro_pick("SM_VK_Pile_Logs_3",None)
    if pile: place_v(coll,pile,4.6,0,0,90,cab,{})
    else:
        place_v(coll,"SM_VK_Prop_Woodpile",4.4,-0.2,0,90,cab,{})
    # work yard in the front cell row (y -4.5..-1.5); the path from the door (x -3) stays clear
    place_v(coll,fro_pick("SM_VK_Prop_Sawhorse","SM_VK_Prop_Grindstone"),-0.7,-3.6,0,12,O,{})
    place_v(coll,"SM_VK_Log_Fallen",2.4,-3.7,0,r.uniform(-6,6),O,{})
    place_v(coll,fro_pick("SM_VK_Prop_ChoppingBlock","SM_VK_Stump"),3.3,-1.9,0,r.uniform(0,360),O,{})
    place_v(coll,"SM_VK_Stump",-4.0,-4.0,0,r.uniform(0,360),O,{})
    for (x,y) in ((-4.2,-2.3),(4.2,-4.3),(1.0,-4.4)): place_v(coll,"SM_VK_Plant_TallGrass",x,y,0,r.uniform(0,360),O,{})
    return dict(wall_top=H1,footprint=(3,3))

def fro_shed_hut(coll,origin,n,faces,st,roofs=("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable_Planks"),single="SM_VK_RoofS_Single",raised=False,z=0.0):
    """n x 1 plank shed with an S roof"""
    fam=fro_SHED_R if raised else fro_SHED
    fro_ring_walls(coll,origin,n,1,faces,st,fam,"SM_VK_Corner_Shed_Raised" if raised else "SM_VK_Corner_Shed",z=z)
    L=n*CELL; top=z+fro_HS
    if n==1: place_v(coll,single,0,0,top,0,origin,st)
    else:
        for i in range(n):
            place_v(coll,roofs[1] if i in (0,n-1) else roofs[0],-L/2+1.5+3*i,0,top,180 if i==0 else 0,origin,st)

def build_forester_hut(coll,origin,seed=0):
    """forester's hut, lot 3x2: one-cell plank hut with RoofS_Single + fenced sapling nursery"""
    r=random.Random(seed+29)
    st={"roof":r.choice(["Shingle","Shingle","Thatch"]),"stone":"Field"}
    O=origin
    def sub(lx,ly):
        c,s=math.cos(O[2]),math.sin(O[2]); return (O[0]+lx*c-ly*s,O[1]+lx*s+ly*c,O[2])
    hut=sub(-3.0,-1.5)                                   # front-left cell of the 3x2 lot
    single="SM_VK_RoofThatchS_Single" if st["roof"]=="Thatch" else "SM_VK_RoofS_Single"
    fro_shed_hut(coll,hut,1,{"F":"D","B":"W","L":".","R":"W"},st,single=single)
    place_v(coll,"SM_VK_Deco_Weeds",0,-1.5,0,0,hut,{})
    # nursery: the two front-right cells (x -1.5..4.5, y -3..0), fenced; the hut wall closes the left side
    sap=fro_pick("SM_VK_Crop_Saplings","SM_VK_Crop_TreeNursery")
    for x in (0.45,3.0): place_v(coll,sap,x,-1.5,0,0,O,{})
    fence_run(coll,(-1.0,-3.0),(4.5,-3.0),O,gate_at=0)
    fence_run(coll,(4.5,-3.0),(4.5,0.0),O); fence_run(coll,(4.5,0.0),(-1.0,0.0),O)
    # back cells: water, barrow, stumps of harvested trees, one young pine kept as seed tree
    place_v(coll,"SM_VK_Prop_Trough",-3.0,1.2,0,0,O,{})
    place_v(coll,fro_pick("SM_VK_Prop_Wheelbarrow","SM_VK_Prop_Sacks"),0.2,1.4,0,25,O,{})
    place_v(coll,"SM_VK_Tree_Pine_Young",3.6,2.2,0,r.uniform(0,360),O,{})
    place_v(coll,"SM_VK_Stump",-4.0,2.3,0,r.uniform(0,360),O,{})
    place_v(coll,"SM_VK_Stump",1.6,2.5,0,r.uniform(0,360),O,{})
    return dict(wall_top=fro_HS,footprint=(3,2))

def build_granary(coll,origin,seed=0):
    """granary, 2x2: raised plank store on 9 staddle stones, thatch pyramid (2 x RoofThatch_Hip), detached steps"""
    r=random.Random(seed+41)
    zs=0.645+0.12           # staddle top + bearer half -> wall base
    st={"roof":"Thatch"}
    for x in (-2.85,0.0,2.85):
        for y in (-2.85,0.0,2.85):
            place_v(coll,"SM_VK_Prop_StaddleStone",x,y,0,r.choice((0,30,60,90)),origin,{})
    for (x,y) in ((-1.5,-1.5),(1.5,-1.5),(-1.5,1.5),(1.5,1.5)):
        place_v(coll,"SM_VK_Ceiling_Cell",x,y,zs-2.60,90,origin,{})          # granary floor: planks top = sill beam bottom
    faces={"F":".D","B":"..","L":"..","R":".."}
    fro_ring_walls(coll,origin,2,2,faces,st,fro_SHED_R,"SM_VK_Corner_Shed_Raised",z=zs)
    top=zs+fro_HS
    place_v(coll,"SM_VK_RoofThatch_Hip",-1.5,0,top,180,origin,st)
    place_v(coll,"SM_VK_RoofThatch_Hip",1.5,0,top,0,origin,st)
    place_v(coll,"SM_VK_Prop_GranaryStep",1.5,-3,0,0,origin,{})
    place_v(coll,fro_pick("SM_VK_Pile_Sacks_2","SM_VK_Prop_Sacks"),-1.6,-4.3,0,r.uniform(-20,20),origin,{})
    place_v(coll,"SM_VK_Prop_Sacks",3.9,-3.9,0,r.uniform(0,360),origin,{})
    place_v(coll,"SM_VK_Prop_Cart",-4.6,0.5,0,80,origin,{})
    return dict(wall_top=top,footprint=(2,2))

def build_storehouse(coll,origin,seed=0):
    """storehouse, 3x2 plank barn with an open Posts_Barn cart bay (+ loft) and a bordered 3x2 stock yard in front"""
    r=random.Random(seed+53); L=9.0
    roof=r.choice(["Thatch","Red","Shingle"])
    st={"roof":roof}
    def P(nm,x,y,z,rot,s=st): place_v(coll,nm,x,y,z,rot,origin,s)
    front=["SM_VK_Wall_Barn","SM_VK_Wall_Barn_Door","SM_VK_Wall_Posts_Barn"]
    for i,pc in enumerate(front): P(pc,-L/2+1.5+3*i,-3,0,0)
    for i in range(3): P("SM_VK_Wall_Barn",-L/2+1.5+3*i,3,0,180)
    for yy in (-1.5,1.5):
        P("SM_VK_Wall_Barn",-L/2,yy,0,-90); P("SM_VK_Wall_Barn",L/2,-yy,0,90)
        P("SM_VK_Wall_Barn",1.5,yy,0,90)                       # partition between store and cart bay
        P("SM_VK_Ceiling_Cell",3.0,yy,HB-3.0,0,{})              # hay loft over the bay
    for (cx,cy,rot) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): P("SM_VK_Corner_Barn",cx,cy,0,rot)
    for i in range(3):
        x=-L/2+1.5+3*i
        if roof=="Thatch": pc="SM_VK_RoofThatch_Gable_Planks" if i in (0,2) else "SM_VK_RoofThatch_Mid"
        else: pc="SM_VK_Roof_Gable_Planks" if i in (0,2) else "SM_VK_Roof_Mid"
        P(pc,x,0,HB,180 if i==0 else 0)
    P("SM_VK_Prop_Cart",3.0,-0.4,0,-80,{})
    # yard: 3 x 2 cells in front of the building (y -3.6 .. -9.6)
    yc=[-5.1,-8.1]; xc=[-3.0,0.0,3.0]
    border=fro_pick("SM_VK_Stockpile_Border",None)
    piles=[fro_pick("SM_VK_Pile_Logs_2","SM_VK_Prop_Woodpile"),fro_pick("SM_VK_Pile_Planks_2","SM_VK_Prop_Crates"),
           fro_pick("SM_VK_Pile_Stone_1","SM_VK_Prop_BarrelStack"),fro_pick("SM_VK_Pile_Sacks_2","SM_VK_Prop_Sacks"),
           fro_pick("SM_VK_Pile_Planks_1","SM_VK_Prop_Crates")]
    # the x=+3 column is the cart lane out of the bay, the cell in front of the door stays open
    k_=0
    for j,y in enumerate(yc):
        for i,x in enumerate(xc):
            if i==2 or (i,j)==(1,0): continue
            if border: P(border,x,y,0,0,{})
            pc=piles[k_%len(piles)]
            P(pc,x,y,0,90 if pc=="SM_VK_Prop_Woodpile" else 0,{}); k_+=1
    if not border:
        fence_run(coll,(-L/2,-9.8),(1.5,-9.8),origin)
        fence_run(coll,(-L/2,-3.6),(-L/2,-9.8),origin)
    P("SM_VK_Prop_Sacks",-1.1,-4.1,0,r.uniform(0,360),{})
    P("SM_VK_Prop_Signpost",4.8,-9.9,0,0,{})
    return dict(wall_top=HB,footprint=(3,2),yard=(3,2))

# ---------------------------------------------------------------- piece table
_nw=dict(wobble=False,grime=False); _ng=dict(wobble=False,grime=True)
WS_SPECS=[
 ("SM_VK_Wall_Log",fro_wall_log,_ng),
 ("SM_VK_Wall_Log_Window",fro_wall_log_window,_ng),
 ("SM_VK_Wall_Log_Door",fro_wall_log_door,_ng),
 ("SM_VK_Wall_Log_B",fro_wall_log_b,_ng),
 ("SM_VK_Wall_Log_B_Window",fro_wall_log_b_window,_ng),
 ("SM_VK_Wall_Log_B_Door",fro_wall_log_b_door,_ng),
 ("SM_VK_Corner_Log",fro_corner_log_a,_ng),
 ("SM_VK_Corner_Log_B",fro_corner_log_b,_ng),
 ("SM_VK_Roof_Gable_Logs",fro_roof_gable_logs,_nw),
 ("SM_VK_Wall_Shed",lambda k: fro_shed_wall(k,"."),{}),
 ("SM_VK_Wall_Shed_Door",lambda k: fro_shed_wall(k,"D"),{}),
 ("SM_VK_Wall_Shed_Wide",lambda k: fro_shed_wall(k,"B"),{}),
 ("SM_VK_Wall_Shed_Window",lambda k: fro_shed_wall(k,"W"),{}),
 ("SM_VK_Corner_Shed",fro_corner_shed,_ng),
 ("SM_VK_Wall_Shed_Raised",lambda k: fro_shed_wall(k,".",raised=True),dict(wobble=True,grime=False)),
 ("SM_VK_Wall_Shed_Door_Raised",lambda k: fro_shed_wall(k,"D",raised=True),dict(wobble=True,grime=False)),
 ("SM_VK_Corner_Shed_Raised",lambda k: fro_corner_shed(k,raised=True),_nw),
 ("SM_VK_Wall_Posts",lambda k: fro_wall_posts(k,3.0),_ng),
 ("SM_VK_Wall_Posts_Barn",lambda k: fro_wall_posts(k,4.2),_ng),
 ("SM_VK_Corner_Posts",lambda k: fro_corner_posts(k,3.0),_ng),
 ("SM_VK_Corner_Posts_Barn",lambda k: fro_corner_posts(k,4.2),_ng),
 ("SM_VK_Ceiling_Cell",lambda k: fro_ceiling_cell(k,3.0),_nw),
 ("SM_VK_RoofS_Mid",fro_roofS_mid,_nw),
 ("SM_VK_RoofS_Gable",lambda k: fro_roofS_gable(k,"timber"),_nw),
 ("SM_VK_RoofS_Gable_Planks",lambda k: fro_roofS_gable(k,"planks"),_nw),
 ("SM_VK_RoofS_Single",lambda k: fro_roofS_single(k,"planks"),_nw),
 ("SM_VK_RoofThatchS_Mid",fro_roofthatchS_mid,_nw),
 ("SM_VK_RoofThatchS_Gable",fro_roofthatchS_gable,_nw),
 ("SM_VK_RoofThatchS_Single",fro_roofthatchS_single,_nw),
 ("SM_VK_Prop_StaddleStone",fro_staddle,_ng),
 ("SM_VK_Prop_GranaryStep",fro_granary_step,_ng),
 ("SM_VK_Crop_TreeNursery",fro_tree_nursery,_ng),
]
EXTRA_SPECS+=WS_SPECS
