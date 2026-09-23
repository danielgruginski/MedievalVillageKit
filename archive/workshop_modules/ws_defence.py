# ===================== ws_defence : M7 defence + M8 civic pieces (agent "defence", prefix def_) =====================
# Executed after vk_helpers in the same namespace. Every module-level name is prefixed def_ (builders: build_*).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

DEF_WALK=6.2      # town-wall walk height (top of the guard_tower hoarding floor)
DEF_LVL=1.5       # terrain step
DEF_TW_TOP=7.1    # town-wall breastwork top
DEF_TW_MER=7.9    # town-wall merlon top

def def_pick(name,fallback):
    return name if bpy.data.objects.get(name) else fallback

# ---------------------------------------------------------------- generic helpers
def def_frame(d):
    d=Vector(d).normalized()
    a=Vector((1,0,0)) if abs(d.x)<0.9 else Vector((0,1,0))
    t1=d.cross(a).normalized(); t2=d.cross(t1).normalized()
    return t1,t2

def def_endcap_uv(f,k,c,t1,t2,r):
    for l in f.loops:
        d=l.vert.co-c; l[k.uv].uv=(0.5+d.dot(t1)/r*0.44,0.5+d.dot(t2)/r*0.44)

def def_log(k,p0,p1,r,segs=10,mi=BARK_OAK,tip=0.0,tip_mi=ENDGRAIN,top_cap=True,bot_cap=False,taper=0.93,
            seed=0,wob=0.07,ts=(0.0,0.35,0.7,1.0),bend=0.0):
    """irregular log from p0 to p1 with cylindrical bark UVs.
       tip>0 : carved point of length tip beyond p1 (tip_mi); else a flat end-grain cap at p1."""
    rnd=random.Random(seed)
    p0=Vector(p0); p1=Vector(p1); d=p1-p0; L=d.length; dn=d/L
    t1,t2=def_frame(dn)
    T=TILE.get(mi,1.2); urep=max(1,round(2*math.pi*r/T))
    uo=rnd.random(); vo=rnd.random()
    col=[1+wob*rnd.uniform(-1,1) for _ in range(segs)]
    col=[(col[j-1]+2*col[j]+col[(j+1)%segs])/4 for j in range(segs)]
    bdir=t1*math.cos(rnd.uniform(0,6.28))+t2*math.sin(rnd.uniform(0,6.28))
    rings=[]
    for t in ts:
        c=p0+d*t+bdir*bend*math.sin(math.pi*t)
        rr=r*(1-(1-taper)*t)*(1+0.03*rnd.uniform(-1,1))
        rings.append((c,[c+(t1*math.cos(2*math.pi*j/segs)+t2*math.sin(2*math.pi*j/segs))*rr*col[j] for j in range(segs)],t*L))
    vr=[[k.bm.verts.new(p) for p in ring] for (_,ring,_) in rings]
    fs=[]
    for i in range(len(rings)-1):
        va=rings[i][2]; vb=rings[i+1][2]
        for j in range(segs):
            j2=(j+1)%segs
            f=k.bm.faces.new((vr[i][j],vr[i][j2],vr[i+1][j2],vr[i+1][j])); f.material_index=mi; fs.append(f)
            us=(j/segs*urep+uo,(j+1)/segs*urep+uo,(j+1)/segs*urep+uo,j/segs*urep+uo)
            vs=(va/T+vo,va/T+vo,vb/T+vo,vb/T+vo)
            for l,uu,vv in zip(f.loops,us,vs): l[k.uv].uv=(uu,vv)
    ct=rings[-1][0]; top=vr[-1]
    if tip>0:
        inner=[k.bm.verts.new(ct+(v.co-ct)*0.86+dn*0.03) for v in top]
        ap=k.bm.verts.new(ct+dn*tip+t1*rnd.uniform(-0.03,0.03)+t2*rnd.uniform(-0.03,0.03))
        tf=[]
        for j in range(segs):
            j2=(j+1)%segs
            tf.append(k.bm.faces.new((top[j],top[j2],inner[j2],inner[j])))
            tf.append(k.bm.faces.new((inner[j],inner[j2],ap)))
        for f in tf: f.material_index=tip_mi
        k.bm.normal_update(); k.project(tf,tip_mi)
    elif top_cap:
        cv=k.bm.verts.new(ct+dn*0.012)
        for j in range(segs):
            f=k.bm.faces.new((cv,top[j],top[(j+1)%segs])); f.material_index=ENDGRAIN
            def_endcap_uv(f,k,ct,t1,t2,r)
    if bot_cap:
        cb=rings[0][0]; cv=k.bm.verts.new(cb-dn*0.012); bot=vr[0]
        for j in range(segs):
            f=k.bm.faces.new((cv,bot[(j+1)%segs],bot[j])); f.material_index=ENDGRAIN
            def_endcap_uv(f,k,cb,t1,t2,r)
    k.bm.normal_update()
    return fs

def def_band(k,c,r,h,mi=BURLAP,segs=10,axis=None):
    """rope / iron band around a log (short closed cylinder)"""
    if axis is None: _cyl(k,c,r,r,h,segs,mi)
    else:
        q=Vector((0,0,1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
        _cyl(k,c,r,r,h,segs,mi,rot=q)

def def_beam(k,a,b,w,h,mi=WOOD,bevel=0.03,up=(0,0,1)):
    """box beam from point a to point b (w across, h up-ish)"""
    a=Vector(a); b=Vector(b); d=b-a; L=d.length
    X=d/L; U=Vector(up); Y=U.cross(X).normalized(); Z=X.cross(Y).normalized()
    M=Matrix((X,Y,Z)).transposed().to_4x4(); M.translation=(a+b)/2
    return k.box((0,0,0),(L,w,h),mi,bevel=bevel,xform=M)

def def_roof_cone(k,r,h,segs=16,rot=0.0,z0=0.0,mi=ROOF,under=WOOD,thick=0.16,kick=0.25,concave=1.15,
                  finial=True,rings=4,c=(0,0,0),hips=0.0):
    """cone / pyramid roof with a bell-cast skirt. segs=4 & rot=pi/4 -> square pyramid (half width r/sqrt2).
       Top uses the roof tile texture (planar per facet, V = slope distance from the eave), underside WOOD."""
    cx,cy,_=c
    zk=kick*r*math.tan(KICK) if kick>0 else 0.0
    prof=[(r,0.0)]
    if kick>0: prof.append((r*(1-kick),zk))
    rm=prof[-1][0]
    for i in range(1,rings+1):
        t=i/rings
        prof.append((rm*(1-t),zk+(h-zk)*(t**concave)))
    angs=[rot+2*math.pi*j/segs for j in range(segs)]
    def P(rad,z,a): return Vector((cx+math.cos(a)*rad,cy+math.sin(a)*rad,z0+z))
    dist=[0.0]
    for i in range(1,len(prof)):
        dist.append(dist[-1]+math.hypot(prof[i][0]-prof[i-1][0],prof[i][1]-prof[i-1][1]))
    T=TILE[ROOF]
    top=[[k.bm.verts.new(P(rr,z,a)) for a in angs] for (rr,z) in prof[:-1]]
    apex=k.bm.verts.new(P(0,h,0))
    # underside ring offsets (normal of profile)
    bot=[]
    for i,(rr,z) in enumerate(prof[:-1]):
        a_=prof[max(i-1,0)]; b_=prof[i+1]
        dr,dz=b_[0]-a_[0],b_[1]-a_[1]; L=math.hypot(dr,dz); nr,nz=dz/L,-dr/L
        if nz<0: nr,nz=-nr,-nz
        bot.append([k.bm.verts.new(P(rr-nr*thick,z-nz*thick,a)) for a in angs])
    apb=k.bm.verts.new(P(0,h-thick*1.4,0))
    fs_top=[]
    for i in range(len(top)):
        for j in range(segs):
            j2=(j+1)%segs; am=(angs[j]+math.pi/segs)
            Ut=Vector((-math.sin(am),math.cos(am),0))
            if i<len(top)-1:
                q=(top[i][j],top[i][j2],top[i+1][j2],top[i+1][j]); dv=(dist[i],dist[i],dist[i+1],dist[i+1])
            else:
                q=(top[i][j],top[i][j2],apex); dv=(dist[i],dist[i],dist[-1])
            f=k.bm.faces.new(q); f.material_index=mi; fs_top.append(f)
            for l,vv in zip(f.loops,dv): l[k.uv].uv=((l.vert.co-Vector((cx,cy,0))).dot(Ut)/T+j*0.37,vv/T)
            if i<len(top)-1:
                qb=(bot[i+1][j],bot[i+1][j2],bot[i][j2],bot[i][j])
            else:
                qb=(apb,bot[i][j2],bot[i][j])
            fb=k.bm.faces.new(qb); fb.material_index=under
            for l in fb.loops: l[k.uv].uv=(l.vert.co.x/TILE[WOOD],l.vert.co.y/TILE[WOOD])
        # nothing
    for j in range(segs):
        j2=(j+1)%segs
        f=k.bm.faces.new((bot[0][j],bot[0][j2],top[0][j2],top[0][j])); f.material_index=under
        for l,uv in zip(f.loops,((0,0),(0.6,0),(0.6,0.1),(0,0.1))): l[k.uv].uv=uv
    k.bm.normal_update()
    if hips>0:
        for j in range(segs):
            pts=[P(rr,z+0.02,angs[j]) for (rr,z) in prof[:-1]]+[P(0,h+0.02,0)]
            for i,(pa,pb) in enumerate(zip(pts[:-1],pts[1:])):
                dd=pb-pa; q=Vector((0,0,1)).rotation_difference(dd.normalized()).to_matrix().to_4x4()
                sub=Kit(); _cyl(sub,(0,0,0),hips*(1.1 if i==0 else 1.0),hips*0.92,dd.length+0.08,8,mi)
                merge_kit(k,sub,Matrix.Translation((pa+pb)/2)@q)
    if finial:
        _ico(k,(cx,cy,z0+h+0.02),0.12+0.02*r,mi,sub=1)
        k.box((cx,cy,z0+h+0.45),(0.12,0.12,0.8),WOOD,bevel=0.03)
        _ico(k,(cx,cy,z0+h+0.9),0.13,BRONZE,sub=1)
    return fs_top

def def_rope(k,a,b,r=0.025,sag=0.0,n=6,mi=BURLAP,segs=5):
    a=Vector(a); b=Vector(b); pts=[a+(b-a)*(i/n)-Vector((0,0,sag*math.sin(math.pi*i/n))) for i in range(n+1)]
    for pa,pb in zip(pts[:-1],pts[1:]):
        dd=pb-pa; q=Vector((0,0,1)).rotation_difference(dd.normalized()).to_matrix().to_4x4()
        sub=Kit(); _cyl(sub,(0,0,0),r,r,dd.length+0.01,segs,mi); merge_kit(k,sub,Matrix.Translation((pa+pb)/2)@q)

def def_tongue(k,c,h,r,mi,bend=(0,0),segs=6,twist=0.0):
    """one stylised flame tongue (lathe) bent sideways toward its tip"""
    fs=lathe(k,[(r,0.0),(r*1.12,h*0.22),(r*0.78,h*0.5),(r*0.34,h*0.78),(0.0,h)],center=c,segs=segs,mi=mi)
    vs={v for f in fs for v in f.verts}; cz=c[2]
    for v in vs:
        t=max(0.0,(v.co.z-cz)/h); v.co.x+=bend[0]*t*t; v.co.y+=bend[1]*t*t
        if twist:
            dx,dy=v.co.x-c[0],v.co.y-c[1]; a=twist*t
            v.co.x=c[0]+dx*math.cos(a)-dy*math.sin(a); v.co.y=c[1]+dx*math.sin(a)+dy*math.cos(a)
    return fs
def def_flame(k,c,h,r,seed=0,glow_base=True):
    """stylised fire: GLOW ember core + orange / yellow tongues (lit part toggles with GLOW)"""
    rnd=random.Random(seed); cx,cy,cz=c
    if glow_base: _ico(k,(cx,cy,cz+r*0.25),r*1.05,GLOW,(1,1,0.55),sub=1)
    def_tongue(k,(cx,cy,cz),h,r*0.8,PUMPKIN,bend=(rnd.uniform(-.1,.1)*h,rnd.uniform(-.1,.1)*h),twist=0.6)
    for i in range(4):
        a=i*1.571+rnd.uniform(-0.4,0.4); d=r*0.62
        hh=h*rnd.uniform(0.45,0.7)
        def_tongue(k,(cx+math.cos(a)*d,cy+math.sin(a)*d,cz),hh,r*0.42,PUMPKIN if i%2 else YELLOW,
                   bend=(math.cos(a)*hh*0.25,math.sin(a)*hh*0.25),twist=-0.5)
    def_tongue(k,(cx,cy,cz+h*0.05),h*0.55,r*0.5,GLOW,twist=0.3)

def def_torch(k,x,y,z,out=(0,-1,0)):
    """iron wall bracket with a burning torch"""
    o=Vector(out).normalized(); base=Vector((x,y,z))
    k.box(tuple(base),(0.12,0.12,0.26),IRON,bevel=0.02)
    def_beam(k,base+Vector((0,0,-0.08)),base+o*0.28+Vector((0,0,0.05)),0.05,0.05,IRON,bevel=0.01)
    c=base+o*0.3+Vector((0,0,0.12))
    _cyl(k,tuple(c),0.05,0.035,0.5,6,WOOD)
    _cyl(k,tuple(c+Vector((0,0,0.24))),0.08,0.06,0.1,8,IRON)
    def_flame(k,tuple(c+Vector((0,0,0.28))),0.42,0.09,seed=int(x*7+z*3))

def def_flag(k,c,L,H,mi=CLOTH_A,n=6,dirv=(0,1,0),notch=0.3):
    """waving two-sided pennant from a pole at c (vertical centre of the hoist edge), flying along dirv"""
    d=Vector(dirv).normalized(); side=Vector((0,0,1)).cross(d).normalized(); C=Vector(c)
    top=[];bot=[];mid=[]
    for i in range(n+1):
        t=i/n; w=0.1*math.sin(t*math.pi*2.0)*t
        base=C+d*L*t+side*w-Vector((0,0,0.12*t*t)); hh=H*(1-0.2*t)
        top.append(base+Vector((0,0,hh/2))); bot.append(base-Vector((0,0,hh/2))); mid.append(base)
    mid[-1]=mid[-1]-d*L*notch/ n*2
    for off,flip in ((0.006,False),(-0.006,True)):
        o=side*off
        T=[k.bm.verts.new(p+o) for p in top]; B=[k.bm.verts.new(p+o) for p in bot]; M=[k.bm.verts.new(p+o) for p in mid]
        for i in range(n):
            for q in ((T[i],M[i],M[i+1],T[i+1]),(M[i],B[i],B[i+1],M[i+1])):
                f=k.bm.faces.new(q[::-1] if flip else q); f.material_index=mi
                for l in f.loops: l[k.uv].uv=((l.vert.co-C).dot(d),l.vert.co.z-C.z)

def def_shield(k,c,r,normal=(0,-1,0),mi=CLOTH_A,seed=0):
    """round painted shield: wooden disc, painted face, iron rim + boss"""
    n=Vector(normal).normalized(); q=Vector((0,0,1)).rotation_difference(n).to_matrix().to_4x4()
    sub=Kit()
    _cyl(sub,(0,0,0),r,r,0.06,14,WOOD)
    _cyl(sub,(0,0,0.035),r*0.82,r*0.82,0.02,14,mi)
    ring(sub,(0,0,0.03),r*0.95,r*1.04,0.05,IRON,n=14,axis="Z")
    _ico(sub,(0,0,0.05),r*0.22,IRON,(1,1,0.6),sub=1)
    for i in range(2):
        a=i*math.pi/2+0.785; sub.box((0,0,0.05),(r*1.6,0.05,0.02),mi if i else WOOD,rot=(0,0,a),bevel=0)
    merge_kit(k,sub,Matrix.Translation(Vector(c))@q)

# ================================================================ PALISADE SET
def def_palisade_run(k,L,n,seed=0,rails=True,hmin=3.3,hmax=3.9):
    """row of sharpened logs along local x (length L, centred), outer face -Y; inner rails on +Y"""
    rnd=random.Random(seed)
    sp=L/n
    for i in range(n):
        x=-L/2+sp*(i+0.5)
        r=0.15+rnd.uniform(-0.04,0.04)
        h=rnd.uniform(hmin,hmax); tip=0.45+rnd.uniform(-0.05,0.08)
        lx=rnd.uniform(-0.04,0.04); ly=rnd.uniform(-0.03,0.03)
        bark=BARK_PINE if rnd.random()<0.22 else BARK_OAK
        def_log(k,(x+rnd.uniform(-0.02,0.02),rnd.uniform(-0.03,0.03),-0.8),(x+lx,ly,h-tip),r,segs=9,tip=tip,mi=bark,
                seed=seed*97+i,ts=(0.0,0.24,0.5,1.0),bend=0.03)
    if rails:
        for zr in (1.0,2.6):
            k.box((0,0.24,zr+rnd.uniform(-0.03,0.03)),(L,0.14,0.2),WOOD,rot=(0,rnd.uniform(-0.01,0.01),0),bevel=0.03)
            for i in range(n):
                if (i+int(zr))%2: continue
                x=-L/2+sp*(i+0.5)
                k.box((x,0.1,zr),(0.07,0.42,0.3),BURLAP,rot=(0,0.25,0),bevel=0.02)
def def_palisade_straight(k): def_palisade_run(k,CELL,10,seed=3)
def def_palisade_diag(k): def_palisade_run(k,CELL*math.sqrt(2),14,seed=5)

def def_palisade_post(k):
    """3-log bundle at a grid vertex (corner / end / T joint)"""
    rnd=random.Random(12)
    for i,(h,a) in enumerate(((4.2,math.pi/2),(3.85,math.pi/2+2.094),(4.0,math.pi/2+4.19))):
        x=math.cos(a)*0.22; y=math.sin(a)*0.22
        def_log(k,(x,y,-0.8),(x+rnd.uniform(-0.03,0.03),y+rnd.uniform(-0.03,0.03),h-0.5),0.2,segs=10,tip=0.5,seed=40+i,bend=0.02)
    for z in (1.1,3.0):
        ring(k,(0,0,z),0.42,0.5,0.14,BURLAP,n=12,axis="Z")
        ring(k,(0,0,z+0.16),0.42,0.49,0.08,BURLAP,n=12,axis="Z")

def def_palisade_walk(k):
    """catwalk behind a palisade module: deck top z 2.3, y 0.25..1.25, posts at x -1.5 and 0"""
    zt=2.3
    for x in (-1.5,0.0):
        def_log(k,(x,1.12,-0.6),(x,1.12,zt-0.02),0.12,segs=8,seed=int(x*10)+60,taper=0.95)
        def_beam(k,(x,1.1,1.45),(x,0.34,zt-0.16),0.1,0.12,WOOD)          # knee brace to the palisade rail
    for y in (0.36,1.12):
        k.box((0,y,zt-0.16),(CELL,0.14,0.18),WOOD,bevel=0.03)             # joists along x
    for x in (-1.5,0.0):
        k.box((x,0.75,zt-0.3),(0.14,1.1,0.16),WOOD,bevel=0.03)            # cross bearers on the posts
    rnd=random.Random(7); n=10; w=CELL/n
    for i in range(n):
        x=-1.5+w*(i+0.5)
        k.box((x,0.75+rnd.uniform(-0.03,0.03),zt-0.035),(w-0.025,1.0+rnd.uniform(-0.04,0.06),0.07),PLANKS,rot=(0,0,rnd.uniform(-0.02,0.02)),bevel=0.012)

def def_palisade_ladder(k):
    """ladder for the catwalk: leans from the ground (y 2.0) to the deck edge (y 1.25, z 2.3)"""
    zt=2.3; y0,y1=2.05,1.28; L=math.hypot(zt+0.6,y0-y1)
    for sx in (-0.28,0.28):
        def_beam(k,(sx,y0,0.0),(sx,y1-0.02,zt+0.6),0.08,0.1,WOOD,up=(0,-1,0))
    for i in range(8):
        t=(i+0.5)/8.3; y=y0+(y1-y0)*t; z=(zt+0.6)*t
        _cyl(k,(0,y,z),0.03,0.03,0.64,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))

def def_gate_post(k,x,seed):
    def_log(k,(x,0.0,-0.9),(x,0.0,4.75),0.225,segs=12,tip=0.45,seed=seed,ts=(0,0.2,0.5,0.8,1),bend=0.02)
def def_palisade_gate(k):
    """gate frame: 2 posts at x +-1.5 (5.2), lintel log at 4.4, knee braces, torches, shields; leaves separate"""
    for i,x in enumerate((-1.5,1.5)): def_gate_post(k,x,70+i)
    rnd=random.Random(71)
    def_log(k,(-2.05,-0.02,4.4),(2.05,0.03,4.42),0.2,segs=10,seed=72,top_cap=True,bot_cap=True,taper=0.95,ts=(0,0.5,1))
    def_log(k,(-1.8,0.1,3.62),(1.8,0.1,3.6),0.13,segs=8,seed=73,top_cap=True,bot_cap=True,taper=0.97,ts=(0,0.5,1))
    for s in (-1,1):
        def_beam(k,(s*1.45,0.1,2.9),(s*0.8,0.1,3.58),0.12,0.14,WOOD)
        for z in (4.4,3.6):
            ring(k,(s*1.5,0,z),0.22,0.27,0.3 if z>4 else 0.2,BURLAP,n=12,axis="Z")
        def_torch(k,s*1.5,-0.2,2.55)
        def_shield(k,(s*0.72,-0.22,4.28),0.36,(0,-1,-0.05),mi=CLOTH_A)
    # a skull-free wooden emblem: crossed logs on the lintel centre
    for s in (-1,1):
        def_beam(k,(-0.35*s,-0.24,4.0),(0.35*s,-0.24,4.75),0.09,0.09,WOOD,up=(0,-1,0))
    # threshold log (half buried)
    def_log(k,(-1.3,0.2,-0.05),(1.3,0.2,-0.05),0.13,segs=8,seed=74,top_cap=True,bot_cap=True,ts=(0,1))

def def_palisade_gateleaf(k):
    """one gate leaf, hinge at the origin, leaf along +X (1.45 wide x 3.4). Symmetric front/back so the
       opposite leaf is the same piece rotated 180 deg. Custom prop hinge_axis = local Z."""
    n=5; W=1.45; sp=(W-0.05)/n
    for i in range(n):
        x=0.05+sp*(i+0.5); h=3.4-0.3*abs(i-2)/2+(0.06 if i%2 else 0)
        def_log(k,(x,0,0.05),(x,0,h-0.4),0.14,segs=8,tip=0.4,seed=80+i,taper=0.97,ts=(0,0.5,1),bend=0.01)
    for s in (-1,1):
        for z in (0.55,2.55):
            k.box((W/2+0.02,s*0.16,z),(W-0.05,0.1,0.22),WOOD,bevel=0.03)
        def_beam(k,(0.2,s*0.17,0.65),(W-0.2,s*0.17,2.45),0.09,0.2,WOOD,up=(0,s*-1,0))
        for z in (0.55,2.55):
            k.box((0.3,s*0.22,z),(0.55,0.03,0.12),IRON,bevel=0.01)
    for z in (0.55,2.55): _cyl(k,(0.0,0,z),0.06,0.06,0.34,8,IRON)
    k.box((W-0.12,-0.25,1.5),(0.06,0.06,0.3),IRON,bevel=0.01)

def def_palisade_tower(k):
    """stilt watch tower centred on a grid vertex (the palisade runs through underneath).
       legs at +-1.25, platform top z 4.5, log parapet to 5.6, pyramid roof from 6.5. Ladder on the +X+Y side."""
    rnd=random.Random(90); zp=4.5; zr=6.5; A=1.25
    for i,(sx,sy) in enumerate(((-1,-1),(1,-1),(1,1),(-1,1))):
        def_log(k,(sx*A,sy*A,-0.9),(sx*(A-0.1),sy*(A-0.1),zr+0.05),0.18,segs=10,seed=91+i,ts=(0,0.12,0.4,0.7,1.0),taper=0.9,bend=0.03)
    # X bracing on the four sides
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        def_beam(sub,(-A+0.1,-A-0.1,0.6),(A-0.15,-A-0.1,zp-0.45),0.1,0.13,WOOD)
        def_beam(sub,(A-0.1,-A-0.12,0.6),(-A+0.15,-A-0.12,zp-0.45),0.1,0.13,WOOD)
        def_beam(sub,(-A,-A-0.05,zp-0.25),(A,-A-0.05,zp-0.25),0.18,0.22,WOOD)       # platform bearer
        def_beam(sub,(-A,-A+0.05,zr-0.08),(A,-A+0.05,zr-0.08),0.16,0.18,WOOD)       # top plate
        merge_kit(k,sub,R)
    # floor: joists poking out + planks
    for i in range(5):
        y=-1.4+i*0.7
        k.box((0,y,zp-0.14),(3.6,0.14,0.14),WOOD,bevel=0.03)
    n=12; w=3.3/n
    for i in range(n):
        x=-1.65+w*(i+0.5)
        k.box((x,rnd.uniform(-0.03,0.03),zp-0.035),(w-0.02,3.3+rnd.uniform(-0.05,0.08),0.07),PLANKS,rot=(0,0,rnd.uniform(-0.015,0.015)),bevel=0.012)
    # log parapet (log-cabin style crossing corners)
    E=1.58
    for lvl in range(4):
        for side in range(4):
            zz=zp+0.13+lvl*0.25+(0.125 if side%2 else 0.0)
            R=Matrix.Rotation(side*math.pi/2,4,"Z"); sub=Kit()
            def_log(sub,(-E-0.28,-E,zz),(E+0.28,-E,zz+rnd.uniform(-0.03,0.03)),0.125,segs=8,seed=100+lvl*4+side,
                    top_cap=True,bot_cap=True,taper=0.95,ts=(0,0.5,1))
            merge_kit(k,sub,R)
    # corner roof posts are the legs; add knee braces under the roof
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        for s in (-1,1):
            def_beam(sub,(s*(A-0.12),-A+0.02,zr-0.75),(s*(A-0.62),-A+0.02,zr-0.12),0.09,0.1,WOOD)
        merge_kit(k,sub,R)
    # hatch + ladder (+X +Y quadrant)
    k.quad([(0.25,0.35,zp+0.005),(0.95,0.35,zp+0.005),(0.95,1.0,zp+0.005),(0.25,1.0,zp+0.005)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for sx in (0.32,0.88):
        def_beam(k,(sx,0.95,0.0),(sx,0.68,zp+0.9),0.07,0.09,WOOD,up=(0,-1,0))
    for i in range(15):
        t=(i+0.6)/16.5; z=(zp+0.9)*t; y=0.95+(0.68-0.95)*t
        _cyl(k,(0.6,y,z),0.028,0.028,0.6,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # roof
    def_roof_cone(k,2.95,2.4,segs=4,rot=math.pi/4,z0=zr,thick=0.14,kick=0.2,concave=1.1,rings=3,finial=False,hips=0.1)
    k.box((0,0,zr+2.9),(0.12,0.12,2.2),WOOD,bevel=0.03)
    def_flag(k,(0,0.06,zr+3.95),1.1,0.62)
    _ico(k,(0,0,zr+2.44),0.2,ROOF,sub=1)
    _ico(k,(0,0,zr+4.05),0.1,BRONZE,sub=1)
    for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
        rock(k,(sx*A,sy*A,0.12),(0.62,0.62,0.36),seed=int(5+sx*3+sy),tilt=0.05)
    # lantern-ish torch on the outer face
    def_torch(k,0,-A-0.2,zp+0.7+0.3)

def def_beacon(k):
    """signal beacon: 5 m pole with raking struts, iron fire basket full of coal and flame (GLOW). Smoke socket at z 6.3"""
    def_log(k,(0,0,-0.8),(0,0,5.0),0.17,segs=10,seed=120,taper=0.85,ts=(0,0.15,0.5,1),bend=0.03)
    for i in range(3):
        a=i*2.094+0.3; b=Vector((math.cos(a)*1.25,math.sin(a)*1.25,-0.3))
        def_log(k,b,(math.cos(a)*0.16,math.sin(a)*0.16,2.3),0.09,segs=7,seed=121+i,taper=0.9,ts=(0,0.5,1))
        rock(k,(b.x*1.05,b.y*1.05,0.1),(0.45,0.4,0.3),seed=125+i,tilt=0.1)
    def_band(k,(0,0,2.2),0.2,0.18,BURLAP,10)
    # peg rungs
    for i in range(8):
        z=0.8+i*0.5; a=(i%2)*math.pi
        _cyl(k,(math.cos(a)*0.2,math.sin(a)*0.2,z),0.035,0.035,0.34,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y")@Matrix.Rotation(0,4,"Z"))
    # basket
    zb=5.0
    _cyl(k,(0,0,zb+0.02),0.28,0.2,0.18,10,IRON)
    for z,r in ((zb+0.12,0.36),(zb+0.45,0.52),(zb+0.8,0.62)):
        ring(k,(0,0,z),r-0.04,r+0.02,0.06,IRON,n=16,axis="Z")
    for i in range(8):
        a=2*math.pi*i/8
        def_beam(k,(math.cos(a)*0.3,math.sin(a)*0.3,zb+0.1),(math.cos(a)*0.64,math.sin(a)*0.64,zb+0.95),0.05,0.05,IRON,bevel=0.01)
        _cyl(k,(math.cos(a)*0.66,math.sin(a)*0.66,zb+1.02),0.03,0.0,0.16,4,IRON)
    rnd=random.Random(9)
    for i in range(9):
        a=rnd.uniform(0,6.28); d=rnd.uniform(0,0.38)
        _ico(k,(math.cos(a)*d,math.sin(a)*d,zb+0.45+rnd.uniform(0,0.15)),0.14,COAL if i%3 else GLOW,sub=1,jit=0.03,seed=i)
    _cyl(k,(0,0,zb+0.52),0.5,0.5,0.06,12,GLOW)
    def_flame(k,(0,0,zb+0.5),1.35,0.42,seed=3,glow_base=False)

# ================================================================ TOWN WALL (2.0 thick, outer face -Y at y=-1.0, walk 6.2)
def def_new_verts(k,before):
    return [v for v in k.bm.verts if v not in before]
def def_new_faces(k,before):
    return [f for f in k.bm.faces if f not in before]

def def_tw_wobble(k,amp=0.045,verts=None):
    """hand-made bulge, periodic in x and ZERO at x=+-1.5 so modules, corners and towers meet exactly"""
    for v in (verts if verts is not None else k.bm.verts):
        x,z=v.co.x,v.co.z
        v.co.y-=amp*(1+math.cos(2*math.pi*x/3.0))/2*math.sin(math.pi*max(0.0,min(z,8.0))/8.0)

def def_tw_batter(vs,face=-1.0,amt=0.35,top=1.8,axis=1,sign=-1):
    for v in vs:
        if abs(v.co[axis]-face)<0.02 and v.co.z<top-1e-4:
            v.co[axis]+=sign*amt*min(1.0,(top-max(v.co.z,0.0))/top)

def def_uv_shift(faces,k,du=0.5,mats=(STONE,)):
    for f in faces:
        if f.material_index in mats:
            for l in f.loops: l[k.uv].uv.x+=du

def def_tw_plinth(k,x0,x1,face=-1.35,seed=0,axis="x"):
    """chunky foundation rocks along the batter foot"""
    rnd=random.Random(seed); x=x0
    while x<x1-0.1:
        w=min(rnd.uniform(0.5,0.85),x1-x)
        if x1-(x+w)<0.3: w=x1-x
        h=rnd.uniform(0.38,0.55); d=rnd.uniform(0.34,0.46)
        c=(x+w/2,face+d/2-0.12,h/2-0.1) if axis=="x" else (face+d/2-0.12,x+w/2,h/2-0.1)
        sz=(w-0.06,d,h) if axis=="x" else (d,w-0.06,h)
        rock(k,c,sz,seed=rnd.randrange(1<<30),tilt=0.06,segs=1)
        x+=w

def def_tw_merlon(k,x,dz=0.0,slit=True,w=0.9,y0=-1.0,y1=-0.5,z0=7.22,z1=7.82):
    stone_panel(k,x-w/2,x+w/2,z0+dz-0.25,z1+dz,y0,y1)
    rock(k,(x,(y0+y1)/2,z1+dz+0.05),(w+0.08,(y1-y0)+0.08,0.14),seed=int(x*37+dz*11)+500,tilt=0.015,segs=1)
    if slit:
        k.quad([(x-0.05,y0-0.004,z0+dz+0.08),(x+0.05,y0-0.004,z0+dz+0.08),(x+0.05,y0-0.004,z1+dz-0.1),(x-0.05,y0-0.004,z1+dz-0.1)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        k.box((x,y0-0.03,z0+dz+0.05),(0.3,0.08,0.07),STONE_BLOCK,bevel=0.02)

def def_tw_top(k,x0,x1,merlons=(-0.75,0.75),seed=0,corbels=True,slits=True):
    """breastwork, coping, merlons, ASHLAR walk (6.2) with corbelled inner lip, ASHLAR string course 5.6"""
    stone_panel(k,x0,x1,6.05,7.1,-1.0,-0.5)
    k.box(((x0+x1)/2,-0.75,7.16),(x1-x0,0.64,0.12),STONE_BLOCK,bevel=0.025)
    for mx in merlons: def_tw_merlon(k,mx,slit=slits)
    k.box(((x0+x1)/2,0.325,6.125),(x1-x0,1.65,0.15),ASHLAR,bevel=0)
    k.box(((x0+x1)/2,1.08,6.12),(x1-x0,0.2,0.2),STONE_BLOCK,bevel=0.03)
    if corbels:
        n=int(round((x1-x0)/0.5))
        for i in range(n):
            x=x0+0.25+0.5*i
            k.box((x,1.06,5.9),(0.24,0.2,0.22),STONE_BLOCK,bevel=0.03)
            k.box((x,1.03,5.7),(0.2,0.12,0.2),STONE_BLOCK,bevel=0.03)
    k.box(((x0+x1)/2,-1.07,5.6),(x1-x0,0.2,0.24),ASHLAR,bevel=0.03)

def def_tw_buttress(k,x=-1.5,w=0.84,broken=False):
    """two-stage buttress on the outer face at the module's left seam (the left edge belongs to the module)"""
    stone_panel(k,x-w/2,x+w/2,-1.5,2.7 if not broken else 2.2,-1.62,-0.95)
    if broken:
        rock(k,(x,-1.3,2.3),(w,0.6,0.3),seed=1201,tilt=0.2,segs=1); return
    stone_panel(k,x-w/2+0.08,x+w/2-0.08,2.7,4.55,-1.36,-0.95)
    k.box((x,-1.42,2.73),(w+0.06,0.46,0.14),STONE_BLOCK,rot=(0.55,0,0),bevel=0.03)
    k.box((x,-1.18,4.56),(w-0.08,0.4,0.14),STONE_BLOCK,rot=(0.6,0,0),bevel=0.03)

def def_tw_module(k,seed=0,merlons=(-0.75,0.75),rocks=True,buttress=True):
    b=set(k.bm.verts)
    stone_panel(k,-1.5,1.5,-1.5,6.05,-1.0,1.0)
    def_tw_batter(def_new_verts(k,b))
    if buttress: def_tw_buttress(k)
    def_tw_top(k,-1.5,1.5,merlons,seed)
    if rocks:
        wall_rocks(k,-1.5,1.5,1.95,5.35,face=-1.0,n=4,seed=seed+3)
        sub=Kit(); wall_rocks(sub,-1.5,1.5,0.4,5.3,face=-1.0,n=3,seed=seed+9); merge_kit(k,sub,Matrix.Rotation(math.pi,4,"Z"))
    def_tw_plinth(k,-1.5,1.5,seed=seed+17)

def def_townwall_straight(k):
    def_tw_module(k,seed=4); def_tw_wobble(k)

def def_townwall_corner_out(k):
    """convex corner at the grid vertex, outer faces -X and -Y; runs leave along +X (rot 0) and +Y (rot -90)"""
    bf=set(k.bm.faces); b=set(k.bm.verts)
    stone_panel(k,-1.0,0.0,-1.5,6.05,-1.0,0.0)
    vs=def_new_verts(k,b); def_tw_batter(vs,axis=1); def_tw_batter(vs,axis=0)
    stone_panel(k,-1.0,0.0,6.05,7.1,-1.0,-0.5); stone_panel(k,-1.0,-0.5,6.05,7.1,-0.5,0.0)
    def_uv_shift(def_new_faces(k,bf),k)
    for (c,s) in (((-0.5,-0.75,7.16),(1.08,0.64,0.12)),((-0.75,-0.25,7.16),(0.64,0.6,0.12))):
        k.box(c,s,STONE_BLOCK,bevel=0.025)
    # big corner merlon + cap
    bf=set(k.bm.faces)
    stone_panel(k,-1.02,-0.22,6.97,8.02,-1.02,-0.22)
    def_uv_shift(def_new_faces(k,bf),k)
    rock(k,(-0.62,-0.62,8.07),(0.9,0.9,0.15),seed=611,tilt=0.015,segs=1)
    k.quad([(-1.024,-0.67,7.3),(-1.024,-0.57,7.3),(-1.024,-0.57,7.78),(-1.024,-0.67,7.78)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.quad([(-0.57,-1.024,7.3),(-0.67,-1.024,7.3),(-0.67,-1.024,7.78),(-0.57,-1.024,7.78)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    # raised walk slab over the corner square (hides the overlap of the two runs' walks)
    k.box((0.25,0.25,6.145),(1.5,1.5,0.19),ASHLAR,bevel=0.02)
    k.box((1.08,0.33,6.14),(0.2,1.66,0.22),STONE_BLOCK,bevel=0.03)
    k.box((0.33,1.08,6.14),(1.66,0.2,0.22),STONE_BLOCK,bevel=0.03)
    # string course around the corner
    k.box((-0.54,-1.07,5.6),(1.1,0.2,0.24),ASHLAR,bevel=0.03)
    k.box((-1.07,-0.54,5.6),(0.2,1.1,0.24),ASHLAR,bevel=0.03)
    # quoins up the corner edge (follow the batter)
    rnd=random.Random(5); z=0.1; i=0
    while z<5.4:
        h=rnd.uniform(0.42,0.55); zc=z+h/2
        bt=0.35*max(0.0,min(1.0,(1.8-zc)/1.8))
        sx,sy=(1.0,0.55) if i%2==0 else (0.55,1.0)
        rock(k,(-1.0-bt+sx/2-0.06,-1.0-bt+sy/2-0.06,zc),(sx,sy,h-0.04),seed=620+i,tilt=0.015,segs=1)
        z+=h; i+=1
    def_tw_plinth(k,-1.35,0.0,face=-1.35,seed=31)
    def_tw_plinth(k,-1.0,0.0,face=-1.35,seed=37,axis="y")

def def_townwall_corner_in(k):
    """concave corner at the grid vertex: outside is the +X+Y quadrant; runs leave along +X (rot 180) and +Y (rot 90)"""
    bf=set(k.bm.faces)
    stone_panel(k,-1.0,0.0,-1.5,6.05,-1.0,0.0)
    def_uv_shift(def_new_faces(k,bf),k)
    k.box((-0.325,-0.325,6.145),(1.65,1.65,0.19),ASHLAR,bevel=0.02)
    k.box((-1.08,-0.33,6.14),(0.2,1.66,0.22),STONE_BLOCK,bevel=0.03)
    k.box((-0.25,-1.08,6.14),(1.5,0.2,0.22),STONE_BLOCK,bevel=0.03)
    for i in range(2):
        for (x,y,sx,sy) in ((-1.06,-0.25-0.5*i,0.2,0.24),(-0.25-0.5*i,-1.06,0.24,0.2)):
            k.box((x,y,5.9),(sx,sy,0.22),STONE_BLOCK,bevel=0.03)
    # corner pier (inner corner post of dressed stone)
    rnd=random.Random(8); z=0.0; i=0
    while z<5.5:
        h=rnd.uniform(0.42,0.55)
        rock(k,(-1.0+0.2,-1.0+0.2,z+h/2),(0.5 if i%2 else 0.62,0.62 if i%2 else 0.5,h-0.04),seed=700+i,tilt=0.015,segs=1)
        z+=h; i+=1

def def_townwall_stair(k):
    """stone stair against the INNER face (y 1.0..2.1), climbs +X: rise 2.067 over the 3 m module (8 steps).
       Stack three modules at z 0, 2.067, 4.133 on consecutive cells to reach the 6.2 walk (34.6 deg)."""
    n=8; R=2.067/n; T=3.0/n; y0,y1=1.0,2.1; zb=-4.2
    prof=[(-1.5,zb),(1.5,zb)]
    for i in range(n-1,-1,-1):
        prof+= [(-1.5+(i+1)*T,(i+1)*R),(-1.5+i*T,(i+1)*R)]
    # dedupe consecutive equal points
    pts=[prof[0]]
    for p in prof[1:]:
        if abs(p[0]-pts[-1][0])>1e-6 or abs(p[1]-pts[-1][1])>1e-6: pts.append(p)
    fs=[]
    for yy,flip in ((y1,False),(y0,True)):
        vs=[k.bm.verts.new((x,yy,z)) for x,z in pts]
        f=k.bm.faces.new(vs[::-1] if flip else vs); fs.append(f)
    k.bm.normal_update()
    if fs[0].normal.y<0:
        for f in fs: f.normal_flip()
    k.project(fs,STONE)
    for f in fs:
        for l in f.loops: l[k.uv].uv.x+=0.5
    for i in range(n):
        x0=-1.5+i*T; zt=(i+1)*R
        riser=k.quad([(x0,y1,zt-R if i else zb),(x0,y0,zt-R if i else zb),(x0,y0,zt),(x0,y1,zt)],STONE)
        k.box((x0+T/2+0.02,(y0+y1)/2+0.03,zt-0.045),(T+0.05,y1-y0+0.06,0.1),STONE_BLOCK,bevel=0.025,jitter=0.008,seed=i)
    k.quad([(1.5,y0,zb),(1.5,y1,zb),(1.5,y1,n*R),(1.5,y0,n*R)],STONE)
    # sloped coping along the open edge
    L=math.hypot(3.0,n*R); ang=math.atan2(n*R,3.0)
    k.box((0.0,y1-0.1,n*R/2+0.12),(L,0.24,0.14),STONE_BLOCK,rot=(0,-ang,0),bevel=0.03)

def def_townwall_step(k):
    """straight module whose base, walk and parapet rise by LVL (1.5) over 3 m (slope tiles); merlons stepped"""
    def_tw_module(k,seed=6,merlons=(),buttress=False)
    def_tw_wobble(k)
    for v in k.bm.verts: v.co.z+=DEF_LVL*(v.co.x+1.5)/3.0
    def_tw_buttress(k)
    for mx in (-0.75,0.75):
        def_tw_merlon(k,mx,dz=DEF_LVL*(mx+1.5)/3.0)

def def_townwall_ruin(k):
    """breached module: ragged top U(3.8,5.2), no merlons, rubble heaps both sides"""
    rnd=random.Random(21)
    xs=[-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5]
    hs=[5.25,4.75,4.15,3.8,4.05,4.6,5.2]
    b=set(k.bm.verts)
    for i in range(6):
        h=hs[i]+rnd.uniform(-0.12,0.12)
        stone_panel(k,xs[i],xs[i+1],-1.5,h,-1.0,1.0)
    def_tw_batter(def_new_verts(k,b))
    def_tw_buttress(k,broken=True)
    wall_rocks(k,-1.5,1.5,1.95,3.6,face=-1.0,n=3,seed=5)
    # broken stones on the ragged top
    for i in range(6):
        h=hs[i]
        for j in range(2):
            x=xs[i]+0.25*(j*2+1)/2+rnd.uniform(-0.05,0.05)
            rock(k,(x,rnd.uniform(-0.6,0.6),h+rnd.uniform(0.0,0.12)),(rnd.uniform(0.35,0.5),rnd.uniform(0.5,0.9),rnd.uniform(0.2,0.34)),seed=800+i*3+j,tilt=0.25,segs=1)
    # string course remnants at the high ends
    for x0,x1 in ((-1.5,-0.9),(0.9,1.5)):
        k.box(((x0+x1)/2,-1.07,4.5),(x1-x0,0.2,0.24),ASHLAR,rot=(0,rnd.uniform(-0.05,0.05),0),bevel=0.03)
    # rubble heaps
    for side in (-1,1):
        for i in range(9):
            x=rnd.uniform(-1.3,1.3); d=rnd.uniform(0.2,1.3)
            y=side*(1.0+0.35*(side<0)+d); s=rnd.uniform(0.35,0.75)*(1.25-d*0.4)
            mi=ROCK_MOSSY if rnd.random()<0.25 else None
            rock(k,(x,y,s*0.28),(s,s*rnd.uniform(0.7,1.0),s*0.6),seed=850+i+side*20,tilt=0.35,mi=mi,segs=1)
    def_tw_plinth(k,-1.5,1.5,seed=23)
    def_tw_wobble(k)

def def_cyl_body(k,c,rfun,zs,segs,mi=STONE,a0=0.0,inward=False,urep=None):
    """ring-built cylinder wall with cylindrical UVs (no caps). rfun(z)->radius"""
    T=TILE.get(mi,3.0); cx,cy=c
    urep=urep or max(1,round(2*math.pi*rfun(zs[-1])/T))
    angs=[a0+2*math.pi*j/segs for j in range(segs)]
    rings=[[k.bm.verts.new((cx+math.cos(a)*rfun(z),cy+math.sin(a)*rfun(z),z)) for a in angs] for z in zs]
    fs=[]
    for i in range(len(zs)-1):
        for j in range(segs):
            j2=(j+1)%segs
            q=(rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j])
            f=k.bm.faces.new(q[::-1] if inward else q); f.material_index=mi; fs.append(f)
            for l in f.loops:
                vv=l.vert; jj=rings[i].index(vv) if vv in rings[i] else rings[i+1].index(vv)
                if jj==0 and (l.vert is q[1] or l.vert is q[2]) and j==segs-1: jj=segs
                l[k.uv].uv=(jj/segs*urep,vv.co.z/T)
    return fs,rings

def def_annulus(k,r0,r1,z,segs,a0,mi,skip=(),only=None,down=True):
    """flat ring of per-segment quads (segment j spans a0+2pi j/segs .. +1), facing down (or up)"""
    fs=[]
    for j in range(segs):
        if j in skip or (only is not None and j not in only): continue
        a,b=a0+2*math.pi*j/segs,a0+2*math.pi*(j+1)/segs
        q=[(r0*math.cos(a),r0*math.sin(a)),(r1*math.cos(a),r1*math.sin(a)),(r1*math.cos(b),r1*math.sin(b)),(r0*math.cos(b),r0*math.sin(b))]
        vs=[k.bm.verts.new((x,y,z)) for x,y in q]
        f=k.bm.faces.new(vs[::-1] if down else vs); f.material_index=mi; fs.append(f)
    k.bm.normal_update(); k.project(fs,mi)
    return fs

def def_slit(k,ang,r,z,h=0.95,c=(0,0)):
    """arrow slit with dressed jambs on a round/flat surface at radius r, facing outward at angle ang"""
    sub=Kit()
    sub.quad([(-0.06,-r-0.03,z-h/2),(0.06,-r-0.03,z-h/2),(0.06,-r-0.03,z+h/2),(-0.06,-r-0.03,z+h/2)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for s in (-1,1): sub.box((s*0.17,-r+0.02,z),(0.2,0.18,h+0.1),STONE_BLOCK,bevel=0.03,jitter=0.01,seed=int(z*10)+s)
    sub.box((0,-r+0.02,z+h/2+0.1),(0.56,0.2,0.18),STONE_BLOCK,bevel=0.03)
    sub.box((0,-r+0.0,z-h/2-0.08),(0.46,0.24,0.12),STONE_BLOCK,bevel=0.03)
    merge_kit(k,sub,Matrix.Translation((c[0],c[1],0))@Matrix.Rotation(ang+math.pi/2,4,"Z"))

def def_arch_opening(k,hw,zs,z0,y,mi_fill=VOID,ring_mi=STONE_BLOCK,n=7,planks=False):
    """flat arched opening (VOID or plank door) facing -Y at plane y, with voussoirs + jambs"""
    pts=[(hw,z0),(hw,zs)]+[(math.cos(math.pi*j/10)*hw,zs+math.sin(math.pi*j/10)*hw) for j in range(1,10)]+[(-hw,zs),(-hw,z0)]
    vs=[k.bm.verts.new((x,y,z)) for x,z in pts]; f=k.bm.faces.new(vs); f.material_index=PLANKS if planks else mi_fill
    k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    for l in f.loops: l[k.uv].uv=(l.vert.co.x/2.0,l.vert.co.z/2.0)
    for i in range(n):
        a=math.pi*(i+0.5)/n; rr=hw+0.14
        k.box((math.cos(a)*rr,y+0.02,zs+math.sin(a)*rr),(0.22,0.24,0.3 if i!=n//2 else 0.38),ring_mi,rot=(0,-(a-math.pi/2),0),bevel=0.03)
    for s in (-1,1):
        for j,zz in enumerate([z0+0.25+0.5*t for t in range(int((zs-z0)/0.5))]):
            k.box((s*(hw+0.12),y+0.02,zz),(0.28 if j%2 else 0.36,0.24,0.46),ring_mi,bevel=0.03)
    if planks:
        for zz in (z0+0.5,zs-0.2):
            k.box((0,y-0.03,zz),(2*hw-0.08,0.03,0.09),IRON,bevel=0.01)
        k.box((hw*0.55,y-0.05,z0+1.0),(0.05,0.05,0.14),IRON,bevel=0.01)

def def_townwall_tower_round(k):
    """round flanking tower r 3.0 centred on a grid vertex. Walk 8.5, 16 merlons, 3 levels of slits,
       doors at 6.2 on +-X for the wall walk, ground door on +Y (town side)."""
    segs=24; a0=-math.pi/segs; R=3.0
    def rf(z): return R+0.35*max(0.0,min(1.0,(1.8-z)/1.8))
    zs=[-1.5,0.0,0.6,1.2,1.8,3.0,4.2,5.4,6.6,7.4,8.5]
    def_cyl_body(k,(0,0),rf,zs,segs,STONE,a0)
    dseg={23,0,1,11,12,13}          # machicolation left open over the two walk doors (+-X, 45 deg each)
    # plinth rocks around the foot
    rnd=random.Random(3)
    for i in range(20):
        a=2*math.pi*i/20+rnd.uniform(-0.05,0.05); w=rnd.uniform(0.8,1.1)
        rock(k,(math.cos(a)*(R+0.33),math.sin(a)*(R+0.33),0.12),(0.45,w,rnd.uniform(0.36,0.5)),seed=900+i,rot_z=a,tilt=0.05,segs=1)
    ring(k,(0,0,5.6),2.9,3.13,0.24,ASHLAR,n=segs,axis="Z")
    # corbel table + projecting parapet
    for i in range(segs):
        if i in dseg: continue
        a=a0+2*math.pi*(i+0.5)/segs
        k.box((math.cos(a)*3.1,math.sin(a)*3.1,7.72),(0.34,0.28,0.26),STONE_BLOCK,rot=(0,0,a),bevel=0.03)
        k.box((math.cos(a)*3.02,math.sin(a)*3.02,7.5),(0.2,0.22,0.2),STONE_BLOCK,rot=(0,0,a),bevel=0.03)
    fs,_=def_cyl_body(k,(0,0),lambda z:3.36,[7.85,8.6],segs,STONE,a0)
    loose=set()
    for j,f in enumerate(fs):
        if j in dseg: loose|=set(f.verts); k.bm.faces.remove(f)
    for e in [e for v in loose for e in v.link_edges if not e.link_faces]:
        if e.is_valid: k.bm.edges.remove(e)
    for v in [v for v in loose if v.is_valid and not v.link_faces]: k.bm.verts.remove(v)
    def_cyl_body(k,(0,0),lambda z:3.36,[8.6,9.35],segs,STONE,a0)
    def_cyl_body(k,(0,0),lambda z:2.96,[8.5,9.35],segs,STONE,a0,inward=True)
    def_annulus(k,2.98,3.36,7.85,segs,a0,STONE_BLOCK,skip=dseg)                     # overhang underside
    def_annulus(k,2.99,3.36,8.6,segs,a0,STONE_BLOCK,only=dseg)                      # soffit over the door gaps
    for jb,phi in ((23,0.0),(2,0.0),(11,math.pi),(14,math.pi)):                     # gap jambs
        th=a0+2*math.pi*jb/segs; c,s=math.cos(th),math.sin(th)
        vs=[k.bm.verts.new(p) for p in ((2.99*c,2.99*s,7.85),(3.36*c,3.36*s,7.85),(3.36*c,3.36*s,8.6),(2.99*c,2.99*s,8.6))]
        f=k.bm.faces.new(vs); f.material_index=STONE_BLOCK; k.bm.normal_update()
        tng=Vector((-s,c,0))*(1 if math.sin(phi-th)>0 else -1)
        if f.normal.dot(tng)<0: f.normal_flip()
        k.project([f],STONE_BLOCK)
    ring(k,(0,0,9.41),2.9,3.44,0.12,STONE_BLOCK,n=segs,axis="Z")
    # floor
    vs=[k.bm.verts.new((math.cos(a0+2*math.pi*j/segs)*2.97,math.sin(a0+2*math.pi*j/segs)*2.97,8.5)) for j in range(segs)]
    f=k.bm.faces.new(vs); f.material_index=ASHLAR
    for l in f.loops: l[k.uv].uv=(l.vert.co.x/3.0,l.vert.co.y/3.0)
    k.bm.normal_update()
    # 16 merlons
    for i in range(16):
        a=2*math.pi*(i+0.5)/16
        k.box((math.cos(a)*3.17,math.sin(a)*3.17,9.85),(0.42,0.66,0.78),STONE,rot=(0,0,a),bevel=0.04,jitter=0.01,seed=i)
        k.box((math.cos(a)*3.17,math.sin(a)*3.17,10.28),(0.5,0.74,0.1),STONE_BLOCK,rot=(0,0,a),bevel=0.03)
    # slits: 3 levels, outer (-Y) half + one inside
    for z,angs in ((2.6,(-90,-135,-45,90)),(4.4,(-112,-68,-160,-20)),(6.7,(-90,-135,-45,90))):
        for d in angs:
            a=math.radians(d); def_slit(k,a,rf(z),z)
    # doors at 6.2 on +-X (onto the wall walk)
    for sgn in (1,-1):
        sub=Kit(); def_arch_opening(sub,0.5,7.7,6.2,-R-0.03,n=7)          # 2.0 m door (6.2 -> 8.2)
        sub.box((0,-R-0.1,6.15),(1.3,0.4,0.1),STONE_BLOCK,bevel=0.02)
        merge_kit(k,sub,Matrix.Rotation(sgn*math.pi/2,4,"Z")@Matrix.Translation((0.3*sgn,0,0)))
    # ground door on the town side (+Y)
    sub=Kit(); def_arch_opening(sub,0.62,1.7,0.0,-rf(1.0)-0.04,planks=True,n=7)
    merge_kit(k,sub,Matrix.Rotation(math.pi,4,"Z"))
    # flag pole
    k.box((0,0,8.5+1.9),(0.14,0.14,3.8),WOOD,bevel=0.03)
    rock(k,(0,0,8.65),(0.6,0.6,0.3),seed=951,tilt=0.02)
    def_flag(k,(0,0.07,11.55),1.6,0.95)
    _ico(k,(0,0,12.35),0.12,BRONZE,sub=1)

# ---------------------------------------------------------------- gatehouse
def def_gatehouse_block(k):
    """3x2-cell gatehouse centred on the wall line: masonry to 6.2 (x -4.5..4.5, y -3..3), passage along Y
       (hw 1.6, spring 2.8, crown 4.4), portcullis slot at y -2.4, half-round towers r 1.8 at (+-3,-3) to 9.0
       (cap them with Roof_Cone_R2). Timber upper storey + roofs are placed by build_townwall_demo."""
    hw=1.6; sp=2.8; top=6.05; Y0,Y1=-3.0,3.0
    b=set(k.bm.verts)
    stone_panel(k,-4.5,-hw,-1.5,top,Y0,Y1); stone_panel(k,hw,4.5,-1.5,top,Y0,Y1)
    arch_cut_panels(k,hw,sp,top,Y0,Y1,STONE)
    def_tw_batter(def_new_verts(k,b),face=Y0,amt=0.3)
    arch_soffit(k,hw,sp,Y0,Y1,ASHLAR)
    # passage paving (kept flat and low so the leaves swing and the portcullis drops without clipping)
    k.box((0,0,0.015),(2*hw-0.04,Y1-Y0+0.3,0.05),ASHLAR,bevel=0)
    # passage paving edge + portcullis slots
    for s in (-1,1):
        k.quad([(s*hw*1.0-s*0.002,-2.5,0.0),(s*hw-s*0.002,-2.3,0.0),(s*hw-s*0.002,-2.3,sp+0.5),(s*hw-s*0.002,-2.5,sp+0.5)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for j,zz in enumerate((0.25,0.8,1.35,1.9,2.45)):
            k.box((s*(hw+0.02),Y1-0.25,zz),(0.2,0.5 if j%2 else 0.7,0.5),STONE_BLOCK,bevel=0.04)
            k.box((s*(hw+0.02),Y0+0.3,zz),(0.2,0.6 if j%2 else 0.8,0.5),STONE_BLOCK,bevel=0.04)
    for i in range(11):                      # town-side arch: clean dressed voussoirs, keystone proud
        a=math.pi*(i+0.5)/11; r=hw+0.19; ks=(i==5)
        k.box((math.cos(a)*r,Y1+0.05+(0.04 if ks else 0),sp+math.sin(a)*r),(0.36 if ks else 0.3,0.24,0.56 if ks else 0.42),
              STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2)
    for s in (-1,1): k.box((s*(hw+0.2),Y1+0.05,sp-0.1),(0.5,0.26,0.2),STONE_BLOCK,bevel=0.04)       # imposts
    # outer face arch: only the voussoirs clear of the flanking towers
    for i in range(11):
        a=math.pi*(i+0.5)/11; r=hw+0.19
        if abs(math.cos(a)*r)>1.05: continue
        k.box((math.cos(a)*r,Y0-0.04,sp+math.sin(a)*r),(0.3 if i!=5 else 0.36,0.2,0.42 if i!=5 else 0.56),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2)
    # corbel course under the jettied timber storey (front and back)
    for yy,sg in ((Y0,-1),(Y1,1)):
        for i in range(18):
            x=-4.25+0.5*i
            if abs(x)>hw+0.3 or yy>0:
                k.box((x,yy+sg*0.12,5.85),(0.26,0.26,0.3),STONE_BLOCK,bevel=0.03)
        k.box((0,yy+sg*0.05,5.62),(9.0,0.12,0.16),ASHLAR,bevel=0.02)
    # landings for the end-wall doors of the timber storey (door at y 1..2 above the 6.2 walk)
    for s in (-1,1):
        k.box((s*4.85,1.5,6.12),(0.8,1.3,0.16),ASHLAR,bevel=0.03)
        for yy in (1.05,1.95):
            k.box((s*4.7,yy,5.85),(0.5,0.24,0.3),STONE_BLOCK,bevel=0.03)
    # quoins on the front corners
    for s in (-1,1):
        z=0.1; i=0; rnd=random.Random(40+s)
        while z<5.4:
            h=rnd.uniform(0.42,0.55); zc=z+h/2; bt=0.3*max(0.0,min(1.0,(1.8-zc)/1.8))
            sx,sy=(0.9,0.5) if i%2==0 else (0.5,0.9)
            rock(k,(s*(4.5-sx/2+0.06),Y1-sy/2+0.06,zc),(sx,sy,h-0.04),seed=960+i+s*50,tilt=0.015,segs=1)
            z+=h; i+=1
    def_tw_plinth(k,-4.5,-1.65,face=Y0-0.3,seed=41); def_tw_plinth(k,1.65,4.5,face=Y0-0.3,seed=43)
    # flanking half-round towers
    for s in (-1,1):
        cx,cy=s*3.0,Y0
        def rf(z): return 1.8+0.25*max(0.0,min(1.0,(1.8-z)/1.8))
        zs=[-1.5,0.0,0.6,1.2,1.8,3.0,4.4,5.8,7.2,8.2,8.8]
        # half cylinder toward -Y (angles pi..2pi) built as a full ring of 16 (back half hidden in the block)
        def_cyl_body(k,(cx,cy),rf,zs,16,STONE,0.0)
        ring(k,(cx,cy,5.6),1.72,1.95,0.24,ASHLAR,n=16,axis="Z")
        ring(k,(cx,cy,8.9),1.7,2.02,0.2,STONE_BLOCK,n=16,axis="Z")
        vs=[k.bm.verts.new((cx+math.cos(2*math.pi*j/16)*1.8,cy+math.sin(2*math.pi*j/16)*1.8,9.0)) for j in range(16)]
        f=k.bm.faces.new(vs); f.material_index=WOOD; k.bm.normal_update()
        for z,angs in ((2.4,(-110,)),(4.6,(-70,-140)),(7.4,(-100,))):
            for d in angs:
                a=math.radians(d if s<0 else -180-d); def_slit(k,a,rf(z),z,h=0.8,c=(cx,cy))
        for i in range(12):
            a=math.pi+math.pi*(i+0.5)/12; rock(k,(cx+math.cos(a)*2.1,cy+math.sin(a)*2.1,0.12),(0.42,0.8,0.42),seed=990+i+s*20,rot_z=a,tilt=0.05,segs=1)
    for s in (-1,1): def_torch(k,s*1.12,Y0-0.35,3.2,out=(-s*0.3,-1,0))

def def_gatehouse_portcullis(k):
    """IRON portcullis for the gatehouse passage (3.3 wide x 4.6), origin at the bottom centre; slides on local Z"""
    W=3.3; H=4.6
    for i in range(12):
        x=-W/2+0.15+i*0.3
        k.box((x,0,H/2+0.12),(0.08,0.08,H-0.24),IRON,bevel=0.012)
        _cyl(k,(x,0,0.08),0.045,0.0,0.24,4,IRON,rot=Matrix.Rotation(math.pi,4,"X"))
    for j in range(15):
        z=0.35+j*0.3
        k.box((0,0.07,z),(W,0.07,0.07),IRON,bevel=0.012)
    k.box((0,0,H+0.02),(W+0.1,0.2,0.16),WOOD,bevel=0.03)
    for x in (-W/2,W/2): k.box((x,0,H/2),(0.12,0.14,H),IRON,bevel=0.015)

def def_gatehouse_gateleaf(k):
    """one oak gate leaf for the gatehouse passage; hinge at the origin, leaf along +X (1.6), arched top
       (spring 2.8, crown 4.4). Symmetric front/back: the other leaf is the same piece rotated 180."""
    hw=1.6; sp=2.8; th=0.16
    n=6; w=(hw-0.04)/n
    for i in range(n):
        x0=0.02+i*w; x1=x0+w-0.012; xm=(x0+x1)/2
        # top follows the arch (centre of the arch at x=hw)
        def zt(x): return sp+math.sqrt(max(0.0,hw*hw-(hw-x)**2))-0.04
        pts=[(x0,0.02),(x1,0.02),(x1,zt(x1)),(x0,zt(x0))]
        fr=[k.bm.verts.new((x,-th/2,z)) for x,z in pts]; bk=[k.bm.verts.new((x,th/2,z)) for x,z in pts]
        fs=[k.bm.faces.new(fr[::-1]),k.bm.faces.new(bk)]
        for a in range(4):
            b_=(a+1)%4; fs.append(k.bm.faces.new((fr[a],fr[b_],bk[b_],bk[a])))
        for f in fs: f.material_index=PLANKS
        k.bm.normal_update(); k.project(fs,PLANKS,axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))],sizes=[w,th,3.0])
    for s in (-1,1):
        for z in (0.6,2.2,3.5):
            L=hw-0.1 if z<3.4 else 1.0
            k.box((0.05+L/2 if z<3.4 else 0.05+L/2,s*(th/2+0.02),z),(L,0.04,0.12),IRON,bevel=0.01)
            for i in range(6 if z<3.4 else 4): k.box((0.2+i*0.25,s*(th/2+0.045),z),(0.04,0.03,0.04),IRON,bevel=0.01)
        def_beam(k,(0.25,s*(th/2+0.05),0.75),(hw-0.2,s*(th/2+0.05),2.05),0.08,0.16,WOOD,up=(0,-s,0))
    for z in (0.6,2.2,3.5): _cyl(k,(0.0,0,z),0.07,0.07,0.34,8,IRON)
    ring(k,(hw-0.35,-th/2-0.06,1.4),0.1,0.14,0.03,IRON,n=12,axis="Y")

# ---------------------------------------------------------------- parapets + roofs (tower house / keep)
def def_parapet_crenel(k):
    """3 m parapet module for stone towers: sits at the wall top (z 0 = wall top, wall face y -0.25).
       6 corbels, breast 0.9 at y -0.6..-0.25, merlons at x +-0.75, coping, walk slab (grime off)"""
    for i in range(6):
        x=-1.25+0.5*i
        k.box((x,-0.42,-0.2),(0.3,0.45,0.4),STONE_BLOCK,bevel=0.03)
        k.box((x,-0.32,-0.5),(0.24,0.26,0.26),STONE_BLOCK,bevel=0.03)
    k.box((0,-0.43,-0.02),(3.0,0.38,0.04),STONE_BLOCK,bevel=0.0)
    stone_panel(k,-1.5,1.5,0.0,0.9,-0.6,-0.25)
    k.box((0,-0.42,0.96),(3.0,0.5,0.12),STONE_BLOCK,bevel=0.025)
    for mx in (-0.75,0.75):
        stone_panel(k,mx-0.45,mx+0.45,0.9,1.62,-0.6,-0.25)
        rock(k,(mx,-0.42,1.67),(0.98,0.45,0.12),seed=int(mx*10)+1100,tilt=0.015,segs=1)
        k.quad([(mx-0.05,-0.604,1.1),(mx+0.05,-0.604,1.1),(mx+0.05,-0.604,1.52),(mx-0.05,-0.604,1.52)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.box((0,0.35,-0.06),(3.0,1.2,0.12),ASHLAR,bevel=0)
    k.box((0,0.95,-0.14),(3.0,0.12,0.2),STONE_BLOCK,bevel=0.02)

def def_parapet_corner(k):
    """corner of the tower parapet at the grid vertex (outer faces -X,-Y), with a bigger corner merlon + corbel"""
    bf=set(k.bm.faces)
    stone_panel(k,-0.6,0.0,0.0,0.9,-0.6,-0.25); stone_panel(k,-0.6,-0.25,0.0,0.9,-0.25,0.0)
    stone_panel(k,-0.62,0.02,0.9,1.8,-0.62,0.02)
    def_uv_shift(def_new_faces(k,bf),k)
    rock(k,(-0.3,-0.3,1.86),(0.74,0.74,0.14),seed=1150,tilt=0.015,segs=1)
    rock(k,(-0.34,-0.34,-0.3),(0.62,0.62,0.6),seed=1151,tilt=0.02)
    rock(k,(-0.26,-0.26,-0.72),(0.4,0.4,0.3),seed=1152,tilt=0.02)
    k.box((-0.35,-0.35,0.95),(0.62,0.62,0.1),STONE_BLOCK,bevel=0.02)
    k.box((0.35,0.35,-0.06),(0.7,0.7,0.12),ASHLAR,bevel=0)

def def_roof_pyramid_6(k):
    """square pyramid roof for a 2x2-cell tower house: r 2.83 (half width 2.0) x h 2.86, hips + finial (grime off)"""
    def_roof_cone(k,2.83,2.86,segs=4,rot=math.pi/4,thick=0.14,kick=0.18,concave=1.05,rings=3,hips=0.1)
    # stone curb it sits on
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-1.85,-0.12),(3.9,0.3,0.26),STONE_BLOCK,bevel=0.03)
        merge_kit(k,sub,R)

def def_roof_cone_r2(k):
    """16-segment cone for round towers up to r 1.8 (eave r 2.2): h 1.9 r, bell-cast skirt, finial (grime off)"""
    def_roof_cone(k,2.2,4.18,segs=16,thick=0.14,kick=0.25,concave=1.2,rings=4)
    ring(k,(0,0,-0.08),1.62,1.9,0.16,WOOD,n=16,axis="Z")

# ---------------------------------------------------------------- tower-house fallbacks (used only if the town agent's
# StoneUp / Turret pieces are missing): upper stone storey 2.8 with the kit's flat wobble, corner quoins, bartizan
def def_flat_wobble(k):
    for v in k.bm.verts: v.co.y+=0.035*math.sin(2*math.pi*v.co.x/CELL+0.9)

def def_stoneup(k,kind="."):
    H=H2
    if kind in (".","X"):
        stone_panel(k,-1.5,1.5,0,H,-0.25,0.25)
        if kind=="X":
            def_slit(k,-math.pi/2,0.25,1.35,h=1.0)
            wall_rocks(k,-1.5,1.5,0.3,H,n=1,seed=31,avoid=((-0.5,0.5,0.5,2.2),))
        else: wall_rocks(k,-1.5,1.5,0.3,H,n=2,seed=33)
    elif kind=="W":
        x0,x1,z0,z1=-0.45,0.45,0.85,1.95
        stone_panel(k,-1.5,x0,0,H); stone_panel(k,x1,1.5,0,H); stone_panel(k,x0,x1,0,z0); stone_panel(k,x0,x1,z1,H)
        window_frame(k,x0,x1,z0,z1)
        rock(k,(0,-0.3,z1+0.38),(1.35,0.22,0.28),seed=41,tilt=0.02,segs=1)
    elif kind=="D":
        hw=0.55; sp=1.6; top=H
        stone_panel(k,-1.5,-hw,0,H); stone_panel(k,hw,1.5,0,H)
        arch_cut_panels(k,hw,sp,top,-0.25,0.25,STONE)
        def_arch_opening(k,hw,sp,0.0,-0.27,planks=True,n=7)
        k.box((0,-0.45,0.05),(1.5,0.5,0.1),STONE_BLOCK,bevel=0.02)
    k.box((0,-0.3,0.1),(CELL,0.14,0.2),ASHLAR,bevel=0.03)
    def_flat_wobble(k)

def def_cornerup(k):
    k.box((0,0,H2/2),(0.8,0.8,H2),STONE,bevel=0)
    k.box((-0.08,-0.08,0.1),(0.88,0.88,0.2),ASHLAR,bevel=0.03)
    z=0.2; i=0; rnd=random.Random(15)
    while z<H2-0.05:
        h=min(rnd.uniform(0.38,0.5),H2-z)
        sx,sy=(1.05,0.62) if i%2==0 else (0.62,1.05)
        rock(k,(-0.43+sx/2,-0.43+sy/2,z+h/2),(sx,sy,h-0.03),seed=i*17+50,tilt=0.02,segs=1)
        z+=h; i+=1

def def_bartizan(k):
    """corbelled corner turret r 0.85 with a cone cap. Origin = tower corner vertex at wall-top level;
       turret axis at (-0.25,-0.25) so it bulges out over the two faces (grime off)"""
    cx,cy=-0.25,-0.25; R=0.85
    lathe(k,[(0.12,-1.7),(0.34,-1.45),(0.5,-1.1),(0.66,-0.7),(0.8,-0.3),(R+0.04,0.0)],center=(cx,cy,0),segs=12,mi=STONE_BLOCK)
    for z,r in ((-1.1,0.53),(-0.7,0.69),(-0.3,0.83)):
        ring(k,(cx,cy,z),r-0.05,r+0.05,0.12,STONE_BLOCK,n=12,axis="Z")
    def_cyl_body(k,(cx,cy),lambda z:R,[0.0,0.9,1.9],12,STONE,0.0)
    ring(k,(cx,cy,1.95),R-0.1,R+0.1,0.14,STONE_BLOCK,n=12,axis="Z")
    for a in (math.radians(225),math.radians(165),math.radians(285)):
        def_slit(k,a,R,0.95,h=0.7,c=(cx,cy))
    def_roof_cone(k,1.12,2.3,segs=12,z0=2.0,thick=0.12,kick=0.25,concave=1.2,rings=3,c=(cx,cy,0))

# ================================================================ TRAINING PROPS
def def_training_dummy(k):
    """quintain-style straw dummy: post, crossbar arms, burlap body + head, painted shield (CLOTH_A)"""
    for s in (-1,1):
        def_beam(k,(-0.55*s,-0.55,0.06),(0.55*s,0.55,0.06),0.14,0.12,WOOD)
    def_log(k,(0,0,0.0),(0,0,1.95),0.09,segs=8,mi=WOOD,seed=1301,taper=0.95,ts=(0,1))
    for s in (-1,1):
        def_beam(k,(0,0,0.5),(0.38*s,0.0,0.05),0.07,0.07,WOOD)
    def_log(k,(-0.72,0,1.45),(0.72,0,1.47),0.06,segs=6,mi=WOOD,seed=1302,bot_cap=True,ts=(0,1))
    _ico(k,(0,0,1.22),0.34,BURLAP,(1.0,0.78,1.35),sub=2,jit=0.02,seed=1)
    for z in (1.0,1.42): def_band(k,(0,0,z),0.27 if z<1.2 else 0.3,0.05,WOOD,10)
    _ico(k,(0,0,1.82),0.19,BURLAP,(1,0.95,1.1),sub=2,jit=0.01,seed=2)
    def_band(k,(0,0,1.66),0.1,0.06,WOOD,8)
    for s in (-1,1):
        _ico(k,(0.72*s,0,1.46),0.11,BURLAP,(1.5,0.9,0.9),sub=1,seed=3)
        lathe(k,[(0.06,0.0),(0.1,-0.08),(0.0,-0.2)],center=(0.82*s,0,1.46),segs=5,mi=HAY)
    k.box((0.07,-0.17,1.86),(0.05,0.02,0.05),VOID,bevel=0); k.box((-0.07,-0.17,1.86),(0.05,0.02,0.05),VOID,bevel=0)
    k.box((0,-0.175,1.76),(0.12,0.02,0.02),VOID,bevel=0)
    lathe(k,[(0.08,1.94),(0.14,1.98),(0.04,2.08),(0.0,2.12)],segs=6,mi=HAY)
    def_shield(k,(-0.62,-0.16,1.25),0.3,(-0.1,-1,0),mi=CLOTH_A)
    k.box((0.45,-0.24,1.18),(0.05,0.03,0.7),WOOD,rot=(0,0.5,0),bevel=0.01)      # practice sword stuck in
    k.box((0.3,-0.24,1.43),(0.2,0.05,0.04),WOOD,rot=(0,0.5,0),bevel=0.01)

def def_archery_butt(k):
    """straw target disc r 0.6 x 0.3 on an A-frame, rings YELLOW / CLOTH_A / CLOTH_B, a few arrows; faces -Y"""
    tilt=0.2; C=Vector((0,0,1.15))
    R=Matrix.Translation(C)@Matrix.Rotation(-tilt,4,"X")
    sub=Kit()
    _cyl(sub,(0,0,0),0.62,0.62,0.3,16,HAY,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for z in (-0.1,0.1): ring(sub,(0,z,0),0.6,0.66,0.05,WOOD,n=16,axis="Y")
    for r0,r1,mi in ((0.44,0.56,CLOTH_B),(0.3,0.44,CLOTH_A),(0.16,0.3,CLOTH_B)):
        ring(sub,(0,-0.155,0),r0,r1,0.012,mi,n=16,axis="Y")
    _cyl(sub,(0,-0.156,0),0.16,0.16,0.014,12,YELLOW,rot=Matrix.Rotation(math.pi/2,4,"X"))
    rnd=random.Random(4)
    for i in range(4):
        a=rnd.uniform(0,6.28); d=rnd.uniform(0.05,0.45)
        p=Vector((math.cos(a)*d,-0.12,math.sin(a)*d))
        q=Matrix.Rotation(math.pi/2+rnd.uniform(-0.2,0.2),4,"X")@Matrix.Rotation(rnd.uniform(-0.2,0.2),4,"Y")
        ar=Kit(); _cyl(ar,(0,0,0.3),0.014,0.014,0.6,5,WOOD)
        for j in range(3): ar.box((0,0,0.54),(0.1,0.006,0.13),PAPER,rot=(0,0,j*1.047),bevel=0)
        merge_kit(sub,ar,Matrix.Translation(p)@q)
    merge_kit(k,sub,R)
    for s in (-1,1):
        def_beam(k,(s*0.62,-0.35,0.0),(s*0.2,0.05,1.85),0.1,0.1,WOOD,up=(0,-1,0))
    def_beam(k,(0,0.95,0.0),(0,0.12,1.7),0.1,0.1,WOOD,up=(0,-1,0))
    k.box((0,-0.02,0.55),(1.3,0.08,0.08),WOOD,bevel=0.02)
    def_rope(k,(-0.25,0.05,1.8),(0.25,0.05,1.8),r=0.02,sag=0.04,n=3)

def def_armor_stand(k):
    """wooden mannequin stand with steel helm, breastplate, pauldrons, CLOTH_A tabard; shield + spear leaning"""
    for s in (-1,1): def_beam(k,(-0.45*s,-0.45,0.05),(0.45*s,0.45,0.05),0.12,0.1,WOOD)
    k.box((0,0,0.95),(0.1,0.1,1.8),WOOD,bevel=0.02)
    k.box((0,0,1.5),(0.9,0.09,0.09),WOOD,bevel=0.02)
    lathe(k,[(0.18,1.0),(0.26,1.1),(0.28,1.3),(0.3,1.48),(0.24,1.56),(0.1,1.6)],segs=10,mi=STEEL)      # breastplate
    for s in (-1,1):
        _ico(k,(0.31*s,0,1.53),0.17,STEEL,(1.1,1.05,0.7),sub=2)
        ring(k,(0.31*s,0,1.47),0.14,0.2,0.04,BRONZE,n=10,axis="Z")
    k.box((0,-0.24,1.24),(0.4,0.06,0.62),CLOTH_A,bevel=0.02)        # tabard front
    k.box((0,-0.28,1.3),(0.16,0.02,0.2),YELLOW,bevel=0.01)
    ring(k,(0,0,1.05),0.19,0.28,0.08,HIDE,n=10,axis="Z")          # belt
    k.box((0,-0.28,1.05),(0.08,0.02,0.08),BRONZE,bevel=0.01)
    ring(k,(0,0,1.56),0.16,0.25,0.05,BRONZE,n=10,axis="Z")        # gorget
    lathe(k,[(0.0,1.62),(0.13,1.64),(0.17,1.72),(0.17,1.86),(0.14,1.97),(0.07,2.03),(0.0,2.05)],segs=10,mi=STEEL)   # helm
    ring(k,(0,0,1.74),0.165,0.185,0.05,BRONZE,n=10,axis="Z")
    k.box((0,-0.17,1.8),(0.04,0.03,0.2),STEEL,bevel=0.005)
    k.box((0,-0.165,1.85),(0.24,0.02,0.035),VOID,bevel=0)
    _cyl(k,(0,0,2.08),0.03,0.02,0.08,6,BRONZE)
    lathe(k,[(0.04,2.08),(0.07,2.14),(0.03,2.3),(0.0,2.34)],segs=6,mi=CLOTH_A)     # plume
    def_shield(k,(0.55,-0.18,0.45),0.32,(0.35,-1,0.35),mi=CLOTH_A)
    k.box((-0.52,0.02,1.05),(0.04,0.04,2.1),WOOD,rot=(0.12,-0.18,0),bevel=0.01)
    lathe(k,[(0.03,0.0),(0.05,0.06),(0.0,0.26)],center=(-0.71,0.15,2.1),segs=4,mi=STEEL)

# ================================================================ CIVIC PROPS
def def_market_cross(k):
    """3 octagonal ASHLAR steps (r 1.8/1.4/1.0, 0.3 each), tapering shaft 3.5, small gabled head (5.3 total)"""
    for i,r in enumerate((1.8,1.4,1.0)):
        if i==0: _cyl(k,(0,0,-0.17),r,r,0.86,8,STONE_BLOCK,rot=Matrix.Rotation(math.pi/8,4,"Z"))   # bottom step + hidden skirt to -0.6
        else: _cyl(k,(0,0,0.13+0.3*i),r,r,0.26,8,STONE_BLOCK,rot=Matrix.Rotation(math.pi/8,4,"Z"))
        _cyl(k,(0,0,0.28+0.3*i),r+0.04,r+0.04,0.06,8,ASHLAR,rot=Matrix.Rotation(math.pi/8,4,"Z"))
    k.box((0,0,1.18),(0.86,0.86,0.56),STONE_BLOCK,bevel=0.06,segs=2)
    k.box((0,0,1.5),(0.96,0.96,0.1),STONE_BLOCK,bevel=0.03)
    lathe(k,[(0.34,1.55),(0.3,1.7),(0.23,4.1),(0.3,4.2),(0.3,4.28),(0.4,4.36)],segs=8,mi=STONE_BLOCK)
    ring(k,(0,0,2.1),0.26,0.33,0.1,BRONZE,n=8,axis="Z")
    # head: shrine block with arched niches, stone pyramid cap, wheel cross
    k.box((0,0,4.66),(0.74,0.74,0.56),STONE_BLOCK,bevel=0.05,segs=2)
    for a in range(4):
        sub=Kit()
        pts=[(0.13,4.5),(0.13,4.72)]+[(math.cos(math.pi*j/6)*0.13,4.72+math.sin(math.pi*j/6)*0.13) for j in range(1,6)]+[(-0.13,4.72),(-0.13,4.5)]
        vs=[sub.bm.verts.new((x,-0.374,z)) for x,z in pts]; f=sub.bm.faces.new(vs[::-1]); f.material_index=VOID
        sub.bm.normal_update()
        if f.normal.y>0: f.normal_flip()
        sub.box((0,-0.37,4.43),(0.34,0.08,0.05),STONE_BLOCK,bevel=0.01)
        merge_kit(k,sub,Matrix.Rotation(a*math.pi/2,4,"Z"))
    k.box((0,0,4.98),(0.86,0.86,0.1),STONE_BLOCK,bevel=0.03)
    _cyl(k,(0,0,5.2),0.58,0.05,0.42,4,STONE_BLOCK,rot=Matrix.Rotation(math.pi/4,4,"Z"))
    k.box((0,0,5.62),(0.13,0.13,0.62),STONE_BLOCK,bevel=0.03)
    k.box((0,0,5.72),(0.5,0.13,0.13),STONE_BLOCK,bevel=0.03)
    ring(k,(0,0,5.72),0.13,0.19,0.08,STONE_BLOCK,n=12,axis="Y")
    _ico(k,(0,0,5.97),0.07,BRONZE,sub=1)
    k.box((0,-0.44,1.2),(0.38,0.03,0.26),BRONZE,bevel=0.01)
    for a in (0.4,2.3,4.0):   # candles + flowers left on the steps
        x,y=math.cos(a)*1.2,math.sin(a)*1.2
        _cyl(k,(x,y,0.72),0.04,0.04,0.16,6,PAPER); _ico(k,(x,y,0.83),0.03,GLOW,sub=0)
    for a in (1.2,3.3,5.3):
        x,y=math.cos(a)*1.55,math.sin(a)*1.55
        _ico(k,(x,y,0.36),0.08,PINK if a<3 else YELLOW,sub=1); _ico(k,(x+0.1,y,0.34),0.07,LEAF,sub=1)

def def_maypole(k):
    """9 m pole with spiral CLOTH_A/B stripes, flower wreath at 7.0, 8 ribbons to stakes at r 3.2 (sag 0.3)"""
    segs=12; z0=1.6; ztop=9.0; n=int((ztop-z0)/0.25)
    def_log(k,(0,0,-0.4),(0,0,z0),0.15,segs=segs,mi=WOOD,seed=1400,top_cap=False,ts=(0,1))
    rings=[]
    for i in range(n+1):
        z=z0+(ztop-z0)*i/n; r=0.15-0.05*i/n
        rings.append([k.bm.verts.new((math.cos(2*math.pi*j/segs)*r,math.sin(2*math.pi*j/segs)*r,z)) for j in range(segs)])
    for i in range(n):
        for j in range(segs):
            j2=(j+1)%segs
            f=k.bm.faces.new((rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j]))
            t=(j/segs+(z0+(ztop-z0)*(i+0.5)/n)/1.2)%1.0
            f.material_index=CLOTH_A if t<0.5 else CLOTH_B
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
    top=k.bm.verts.new((0,0,ztop+0.02))
    for j in range(segs):
        f=k.bm.faces.new((top,rings[-1][j],rings[-1][(j+1)%segs])); f.material_index=CLOTH_A
    k.bm.normal_update()
    _ico(k,(0,0,ztop+0.15),0.18,BRONZE,sub=2)
    def_flag(k,(0,0.03,ztop-0.3),0.9,0.35,mi=CLOTH_A)
    # wreath + flowers
    zw=7.0
    ring(k,(0,0,zw),0.32,0.62,0.22,LEAF,n=16,axis="Z")
    rnd=random.Random(5)
    for i in range(12):
        a=2*math.pi*i/12+rnd.uniform(-0.1,0.1)
        _ico(k,(math.cos(a)*0.55,math.sin(a)*0.55,zw+0.1),0.1,PINK if i%2 else YELLOW,sub=1)
    for i in range(10):
        a=2*math.pi*i/10+0.3
        card(k,(math.cos(a)*0.62,math.sin(a)*0.62,zw-0.08),(-math.sin(a),math.cos(a),0),(math.cos(a)*0.6,math.sin(a)*0.6,-1),0.38,0.4,"ivy",flip=i%2==0)
    # ribbons + stakes
    mats=(CLOTH_A,CLOTH_B,YELLOW,PINK)
    for i in range(8):
        a=2*math.pi*i/8+math.pi/8
        A=Vector((math.cos(a)*0.4,math.sin(a)*0.4,zw-0.05)); B=Vector((math.cos(a)*3.2,math.sin(a)*3.2,0.35))
        side=Vector((-math.sin(a),math.cos(a),0))*0.04
        m=6; pts=[A+(B-A)*(t/m)-Vector((0,0,0.3*math.sin(math.pi*t/m))) for t in range(m+1)]
        for s_,fl in ((1,False),(-1,True)):
            vs=[(k.bm.verts.new(p+side),k.bm.verts.new(p-side)) for p in pts]
            for t in range(m):
                q=(vs[t][0],vs[t][1],vs[t+1][1],vs[t+1][0])
                f=k.bm.faces.new(q[::-1] if fl else q); f.material_index=mats[i%4]
                for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
            for v in [v for pr in vs for v in pr]: v.co.z+=0.004*s_
        k.box((math.cos(a)*3.25,math.sin(a)*3.25,0.2),(0.07,0.07,0.5),WOOD,rot=(0,0,a),bevel=0.015)
    k.bm.normal_update()
    rock(k,(0,0,0.06),(0.7,0.7,0.2),seed=1410,tilt=0.02,segs=1)

def def_stage(k):
    """festival stage: plank platform 6x3x0.8 (front -Y), steps, painted skirt, striped canopy on 4 posts"""
    W,D,H=6.0,3.0,0.8
    k.box((0,0,H-0.05),(W,D,0.1),PLANKS,bevel=0.02)
    for x in (-2.9,-1.45,0,1.45,2.9):
        for y in (-1.4,1.4): k.box((x,y,(H-0.1-0.6)/2),(0.16,0.16,H-0.1+0.6),WOOD,bevel=0.03)   # posts sunk to -0.6
    k.box((0,-1.46,H-0.18),(W,0.1,0.18),WOOD,bevel=0.02)
    # scalloped cloth skirt on the front
    for i in range(8):
        x0=-W/2+i*W/8; x1=x0+W/8
        pts=[(x0,H-0.12),(x1,H-0.12)]+[(x1-(x1-x0)*t/6,H-0.12-0.38-0.12*math.sin(math.pi*t/6)) for t in range(7)]
        vs=[k.bm.verts.new((x,-1.52,z)) for x,z in pts]
        f=k.bm.faces.new(vs); f.material_index=CLOTH_A if i%2 else YELLOW
        k.bm.normal_update()
        if f.normal.y>0: f.normal_flip()
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
    k.box((0,-1.49,-0.1),(W,0.05,1.0),PLANKS,bevel=0.01)                 # front boards, continued down as a skirt
    # steps (front left)
    for i in range(3):
        k.box((-2.1,-1.72-0.3*i,H-0.27*(i+1)+0.03),(1.1,0.32,0.08),PLANKS,bevel=0.015)
        for s in (-1,1): k.box((-2.1+0.52*s,-1.72-0.3*i,(H-0.27*(i+1))/2),(0.08,0.3,H-0.27*(i+1)),WOOD,bevel=0.01)
    # posts + canopy
    zc=3.4
    for x in (-2.9,2.9):
        for y in (-1.35,1.35): def_log(k,(x,y,H),(x,y,zc+0.1),0.09,segs=8,mi=WOOD,seed=int(x*10+y*3)+1500,ts=(0,1))
    for x in (-2.9,2.9): k.box((x,0,zc),(0.14,2.9,0.14),WOOD,bevel=0.03)
    for y in (-1.35,1.35): k.box((0,y,zc),(5.95,0.14,0.14),WOOD,bevel=0.03)
    nx=12
    for i in range(nx):
        x0=-3.1+i*6.2/nx; x1=x0+6.2/nx; mi=CLOTH_A if i%2==0 else CLOTH_B
        for s,fl in ((0.0,False),(-0.012,True)):
            vs=[k.bm.verts.new(p) for p in ((x0,-1.75,zc-0.15+s),(x1,-1.75,zc-0.15+s),(x1,0,zc+0.55+s),(x0,0,zc+0.55+s))]
            vs2=[k.bm.verts.new(p) for p in ((x0,0,zc+0.55+s),(x1,0,zc+0.55+s),(x1,1.6,zc+0.05+s),(x0,1.6,zc+0.05+s))]
            for q in (vs,vs2):
                f=k.bm.faces.new(q[::-1] if fl else q); f.material_index=mi
                for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
        vs=[k.bm.verts.new(p) for p in ((x0,-1.75,zc-0.15),(x1,-1.75,zc-0.15),((x0+x1)/2,-1.76,zc-0.42))]
        f=k.bm.faces.new(vs); f.material_index=mi
        vs=[k.bm.verts.new(p) for p in ((x1,-1.745,zc-0.15),(x0,-1.745,zc-0.15),((x0+x1)/2,-1.746,zc-0.42))]
        f=k.bm.faces.new(vs); f.material_index=mi
    k.box((0,0,zc+0.58),(6.3,0.12,0.1),WOOD,bevel=0.02)
    # back curtain
    for i in range(10):
        x=-2.7+i*0.6
        k.box((x,1.42,(H+zc)/2),(0.62,0.06+0.05*(i%2),zc-H-0.1),CLOTH_A,bevel=0.02)
    k.box((0,1.42,zc-0.35),(5.8,0.14,0.3),YELLOW,bevel=0.02)
    # props on stage: barrel + lute-ish stool
    barrel(k,2.2,0.6,H,0.32,0.8)
    _cyl(k,(-1.0,0.8,H+0.25),0.22,0.22,0.06,10,WOOD)
    for i in range(3):
        a=i*2.094; k.box((-1.0+math.cos(a)*0.12,0.8+math.sin(a)*0.12,H+0.12),(0.05,0.05,0.25),WOOD,bevel=0.01)

def def_stocks(k):
    """ankle stocks: 2 posts, holed plank pair, bench behind"""
    for x in (-0.85,0.85):
        k.box((x,0,0.2),(0.16,0.16,1.6),WOOD,bevel=0.03)                 # posts sunk to -0.6
        k.box((x,0,1.02),(0.2,0.2,0.06),WOOD,bevel=0.02)
    k.box((0,0,0.32),(1.9,0.12,0.2),PLANKS,bevel=0.02)
    k.box((0,0,0.54),(1.9,0.12,0.2),PLANKS,bevel=0.02)
    for x in (-0.35,0.35):
        _cyl(k,(x,-0.065,0.43),0.075,0.075,0.02,10,VOID,rot=Matrix.Rotation(math.pi/2,4,"X"))
        _cyl(k,(x,0.065,0.43),0.075,0.075,0.02,10,VOID,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for x in (-0.85,0.85):
        k.box((x,-0.08,0.43),(0.08,0.04,0.42),IRON,bevel=0.01)
    k.box((0.0,-0.09,0.64),(0.12,0.05,0.08),IRON,bevel=0.01)
    # bench
    k.box((0,0.55,0.42),(1.7,0.34,0.08),PLANKS,bevel=0.02)
    for x in (-0.7,0.7):
        for y in (0.44,0.66): k.box((x,y,0.2),(0.08,0.08,0.4),WOOD,rot=((y-0.55)*1.5,0,0),bevel=0.01)
    rock(k,(0,0,0.03),(2.2,0.9,0.08),seed=1601,tilt=0.0,segs=1)

def def_pillory(k):
    """pillory on a small plank platform: post, neck+wrist board with 3 holes, little hood roof"""
    k.box((0,0,0.2),(1.5,1.5,0.4),PLANKS,bevel=0.03)
    k.box((0,0,-0.3),(1.4,1.4,0.6),STONE,bevel=0)                         # hidden footing skirt
    for x in (-0.68,0.68):
        for y in (-0.68,0.68): k.box((x,y,-0.1),(0.16,0.16,1.0),WOOD,bevel=0.02)
    k.box((0,-0.95,0.12),(0.8,0.4,0.2),PLANKS,bevel=0.02)
    k.box((0,0.1,1.45),(0.18,0.18,2.1),WOOD,bevel=0.03)
    for dz in (0.0,0.22):
        k.box((0,0.0,1.72+dz),(1.3,0.1,0.2),PLANKS,bevel=0.02)
    for x,r in ((-0.38,0.06),(0.0,0.1),(0.38,0.06)):
        _cyl(k,(x,-0.055,1.83),r,r,0.02,10,VOID,rot=Matrix.Rotation(math.pi/2,4,"X"))
    k.box((0.55,-0.07,1.83),(0.1,0.05,0.12),IRON,bevel=0.01)
    k.box((-0.6,-0.07,1.83),(0.06,0.05,0.4),IRON,bevel=0.01)
    for s in (-1,1): k.box((0,0.1+s*0.26,2.66),(0.95,0.6,0.06),ROOF,rot=(-s*0.52,0,0),bevel=0.015)
    k.box((0,0.1,2.81),(1.0,0.1,0.1),WOOD,bevel=0.02)
    for s in (-1,1): def_beam(k,(0,0.1,2.2),(0,0.1+s*0.42,2.55),0.07,0.07,WOOD)
    k.box((0.25,-0.09,1.25),(0.3,0.02,0.4),PAPER,rot=(0,0.08,0),bevel=0)

def def_lowwall_gatearch(k):
    """gate arch for SM_VK_LowWall runs (3 m, centred on y=0): 2 rubble piers, arch_ring, iron gate leaves ajar"""
    hw=0.95; sp=1.75; pier=0.6
    for s in (-1,1):
        x=s*(hw+pier/2)
        for j,(z,h,w) in enumerate(((0.2,0.44,0.8),(0.62,0.42,0.72),(1.02,0.4,0.72),(1.41,0.4,0.72),(1.8,0.4,0.7))):
            rock(k,(x+s*0.02,0,z),(w,0.66,h),seed=1700+j+s*10,tilt=0.02,segs=1)
        k.box((s*1.35,0,0.43),(0.3,0.5,0.86),STONE,bevel=0)
        k.box((x,0,-0.3),(0.72,0.6,0.6),STONE,bevel=0)                    # hidden skirt
    arch_ring(k,hw,sp,-0.3,0.3,STONE_BLOCK,n=9,seed=17)
    arch_cut_panels(k,1.3,sp,sp+hw+0.32,-0.27,0.27,STONE)
    k.box((0,0,sp+hw+0.4),(3.0-0.3,0.66,0.18),STONE_BLOCK,bevel=0.04)
    for s in (-1,1): k.box((s*1.15,0,sp+hw+0.58),(0.5,0.5,0.2),STONE_BLOCK,bevel=0.04)
    lathe(k,[(0.3,sp+hw+0.5),(0.3,sp+hw+0.62),(0.0,sp+hw+0.95)],segs=4,mi=STONE_BLOCK)
    # iron gate leaves, ajar
    for s in (-1,1):
        sub=Kit()
        for i in range(5):
            x=0.1+i*0.18
            sub.box((x,0,0.85),(0.035,0.035,1.6),IRON,bevel=0)          # thin iron: no bevel (tri budget)
            lathe(sub,[(0.03,1.65),(0.05,1.7),(0.0,1.82)],center=(x,0,0),segs=4,mi=IRON)
        for z in (0.2,0.9,1.5): sub.box((0.47,0,z),(0.9,0.04,0.05),IRON,bevel=0)
        ring(sub,(0.47,0,1.2),0.15,0.18,0.03,IRON,n=12,axis="Y")
        M=Matrix.Translation((s*hw,0.05,0))@Matrix.Rotation((0 if s<0 else math.pi)+s*0.45,4,"Z")
        merge_kit(k,sub,M)

def def_hedge(k):
    """trimmed hedge 3.0 x 0.8 x 1.2 (centred on the cell edge like SM_VK_LowWall): LEAF core + ivy cards"""
    rnd=random.Random(1800)
    vs=k.box((0,0,0.6),(3.0,0.7,1.1),MOSS,bevel=0.14,segs=2,jitter=0.02,seed=3,tile=0.9)
    for v in set(vs):
        v.co.x=max(-1.5,min(1.5,v.co.x))
        v.co.y*=1.0+0.06*math.sin(v.co.x*4.1+1.0)
    k.box((0,0,-0.22),(2.9,0.5,0.76),SOIL,bevel=0.03)                     # soil bed + hidden skirt to -0.6
    # leaf cards laid on the surfaces (tilted outward), dense grid with jitter so the trimmed block reads leafy
    def put(c,N,U,V,sz):
        a=rnd.uniform(0,6.28); R=(U*math.cos(a)+V*math.sin(a)).normalized(); up=N.cross(R).normalized()
        up=(up+N*rnd.uniform(0.5,0.9)).normalized()
        card(k,tuple(c),tuple(R),tuple(up),sz,sz*0.92,"ivy",flip=rnd.random()<0.5,bend=0.06)
    for side in (-1,1):
        N=Vector((0,side,0)); U=Vector((1,0,0)); V=Vector((0,0,1))
        for i in range(10):
            for j in range(3):
                c=Vector((-1.35+i*0.3+rnd.uniform(-0.08,0.08),side*0.37,0.28+j*0.34+rnd.uniform(-0.06,0.06)))
                put(c,N,U,V,rnd.uniform(0.36,0.46))
    N=Vector((0,0,1)); U=Vector((1,0,0)); V=Vector((0,1,0))
    for i in range(10):
        for j in range(2):
            c=Vector((-1.35+i*0.3+rnd.uniform(-0.08,0.08),-0.16+j*0.32+rnd.uniform(-0.05,0.05),1.14))
            put(c,N,U,V,rnd.uniform(0.38,0.48))
    for s in (-1,1):
        for j in range(3):
            c=Vector((s*1.47,rnd.uniform(-0.2,0.2),0.3+j*0.34))
            put(c,Vector((s,0,0)),Vector((0,1,0)),Vector((0,0,1)),0.4)

# ---------------------------------------------------------------- demo-only terrain stand-ins (until the terrain kit lands)
def def_standin_plateau(k):
    """DEMO ONLY: one 3x3 cell of a 1.5 m terrain plateau, top at local z 0 (place at z=DEF_LVL).
       Dry-stone (FIELDSTONE) terrace faces, MOSS turf top. Not a kit piece: the terrain kit replaces it."""
    k.box((0,0,-0.8),(CELL,CELL,1.5),FIELDSTONE,bevel=0)
    k.box((0,0,-0.06),(CELL+0.06,CELL+0.06,0.13),MOSS,bevel=0.04)
    rnd=random.Random(1900)
    for a in range(4):
        sub=Kit()
        for i in range(2):
            rock(sub,(rnd.uniform(-1.1,1.1),-1.56,-1.35+rnd.uniform(0,0.1)),(rnd.uniform(0.5,0.8),0.4,0.35),seed=1901+a*3+i,tilt=0.1,mi=ROCK_MOSSY if i else None,segs=1)
        merge_kit(k,sub,Matrix.Rotation(a*math.pi/2,4,"Z"))

def def_standin_ramp(k):
    """DEMO ONLY: 3x3 cell slope rising 1.5 along +X (top z -1.5 at x=-1.5 to 0 at x=+1.5; place at z=DEF_LVL)"""
    bm=k.bm; zl=-1.55
    P=[(-1.5,-1.5,-1.5),(1.5,-1.5,0.0),(1.5,1.5,0.0),(-1.5,1.5,-1.5),(1.5,-1.5,zl),(1.5,1.5,zl),(-1.5,-1.5,zl),(-1.5,1.5,zl)]
    V=[bm.verts.new(p) for p in P]
    top=bm.faces.new((V[0],V[1],V[2],V[3])); top.material_index=MOSS
    sides=[bm.faces.new((V[6],V[4],V[1],V[0])),bm.faces.new((V[5],V[7],V[3],V[2])),bm.faces.new((V[4],V[5],V[2],V[1]))]
    for f in sides: f.material_index=FIELDSTONE
    bm.normal_update()
    for f in [top]+sides:
        if f.normal.dot(f.calc_center_median())<0 and f is not top: f.normal_flip()
    if top.normal.z<0: top.normal_flip()
    k.project([top],MOSS); k.project(sides,FIELDSTONE)

# ================================================================ BUILDERS
def def_placer(coll,origin,style=None):
    base=style or {}
    def P(n,x,y,z=0.0,r=0.0,st=None,**props):
        if n is None or bpy.data.objects.get(n) is None: return None
        o=place_v(coll,n,x,y,z,r,origin,base if st is None else st)
        for k_,v_ in props.items(): o[k_]=v_
        return o
    return P

def build_palisade_demo(coll,origin,seed=0):
    """palisade ring 6x4 cells (x -9..9, y -6..6): gate on the south middle cell with 2 leaves (open),
       stilt towers on the SW and NE vertices, a diagonal across the SE cell, catwalks + ladder, beacon."""
    P=def_placer(coll,origin)
    rnd=random.Random(seed)
    S="SM_VK_Palisade_Straight"
    for x in (-7.5,-4.5,-1.5,4.5): P(S,x,-6,0,0)
    P("SM_VK_Palisade_Gate",1.5,-6,0,0)
    P("SM_VK_Palisade_GateLeaf",1.5-1.45,-6+0.35,0,72,hinge_axis="local Z")
    P("SM_VK_Palisade_GateLeaf",1.5+1.45,-6+0.35,0,180-72,hinge_axis="local Z")
    P("SM_VK_Palisade_Diag",7.5,-4.5,0,45)
    for y in (-1.5,1.5,4.5): P(S,9,y,0,90)
    for x in (7.5,4.5,1.5,-1.5,-4.5,-7.5): P(S,x,6,0,180)
    for y in (4.5,1.5,-1.5,-4.5): P(S,-9,y,0,-90)
    sh={"roof":"Shingle","cloth":"Red"}                 # frontier look: wooden shingles on the stilt towers
    P("SM_VK_Palisade_Tower",-9,-6,0,0,sh); P("SM_VK_Palisade_Tower",9,6,0,180,sh)
    for (x,y) in ((-9,6),(6,-6),(9,-3)): P("SM_VK_Palisade_Post",x,y,0,rnd.choice((0,90,180,270)))
    for x in (-4.5,-1.5,4.5): P("SM_VK_Palisade_Walk",x,-6,0,0)
    for x in (1.5,-1.5): P("SM_VK_Palisade_Walk",x,6,0,180)
    P("SM_VK_Palisade_Ladder",-3.7,-6,0,0); P("SM_VK_Palisade_Ladder",0.8,6,0,180)
    P("SM_VK_Prop_Beacon",-5.6,-2.2,0,20)
    # a little life inside and out
    P("SM_VK_Prop_WeaponRack",5.4,-4.2,0,180); P("SM_VK_Prop_BarrelStack",-7.3,3.8,0,90)
    P("SM_VK_Prop_Woodpile",-5.0,4.6,0,180); P("SM_VK_Prop_Crates",6.2,3.4,0,15)
    P("SM_VK_Prop_Cart",4.2,-10.0,0,25); P("SM_VK_Prop_Trough",-2.2,-2.6,0,90)
    P("SM_VK_Prop_TrainingDummy",2.0,-1.0,0,-20); P("SM_VK_Prop_TrainingDummy",4.2,0.4,0,15)

def def_dress_gatehouse(P,gx,st):
    """timber storey (6.2 -> 9.0), hip/mid/hip roof, cone caps, portcullis + leaves for a Gatehouse_Block at x=gx"""
    Z=DEF_WALK
    P("SM_VK_Gatehouse_Portcullis",gx,-2.4,2.2,0,slide_axis="local Z",travel=4.4)
    P("SM_VK_Gatehouse_GateLeaf",gx-1.6,-1.2,0,78,hinge_axis="local Z")
    P("SM_VK_Gatehouse_GateLeaf",gx+1.6,-1.2,0,180-78,hinge_axis="local Z")
    P("SM_VK_Wall_Timber_Window",gx,-3,Z,0,st)
    for i,x in enumerate((gx-3,gx,gx+3)):
        P(("SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_Window","SM_VK_Wall_Timber_K")[i],x,3,Z,180,st)
    P("SM_VK_Wall_Timber_Door",gx-4.5,1.5,Z,-90,st); P("SM_VK_Wall_Timber",gx-4.5,-1.5,Z,-90,st)
    P("SM_VK_Wall_Timber_Door",gx+4.5,1.5,Z,90,st); P("SM_VK_Wall_Timber",gx+4.5,-1.5,Z,90,st)
    P("SM_VK_Corner_Timber",gx-4.5,3,Z,-90,st); P("SM_VK_Corner_Timber",gx+4.5,3,Z,180,st)
    RT=Z+H2
    P("SM_VK_Roof_Hip",gx-3,0,RT,180,st); P("SM_VK_Roof_Mid",gx,0,RT,0,st); P("SM_VK_Roof_Hip",gx+3,0,RT,0,st)
    for s in (-1,1): P("SM_VK_Roof_Cone_R2",gx+3*s,-3,RT,0,st)
    ban=def_pick("SM_VK_Banner_Wall",None)          # projecting banners on the town side, at the module seams
    for bx in (gx-1.5,gx+1.5): P(ban,bx,3.18,Z+H2,180,{"cloth":"Red"})

def build_townwall_demo(coll,origin,seed=0,style=None):
    """town-wall section (outer face -Y): convex corner + return, 3 stacked stair modules landing on the
       gatehouse (x -3..6), timber-storey gatehouse with portcullis and leaves, round flanking tower on vertex 12,
       a breach (ruin), concave corner at vertex 21 and a run going -Y with a terrain Step."""
    st=style or {"roof":"Slate"}
    P=def_placer(coll,origin)
    W="SM_VK_TownWall_Straight"
    P("SM_VK_TownWall_Corner_Out",-12,0,0,0)
    for y in (1.5,4.5): P(W,-12,y,0,-90)
    for i,x in enumerate((-10.5,-7.5,-4.5)):
        P(W,x,0,0,0); P("SM_VK_TownWall_Stair",x,0,i*2.067,0)
    P("SM_VK_Gatehouse_Block",1.5,0,0,0)
    def_dress_gatehouse(P,1.5,st)
    for x in (7.5,10.5,13.5,19.5): P(W,x,0,0,0)
    P("SM_VK_TownWall_Tower_Round",12,0,0,0)
    P("SM_VK_TownWall_Ruin",16.5,0,0,0)
    P("SM_VK_TownWall_Corner_In",21,0,0,180)
    P(W,21,-1.5,0,-90); P("SM_VK_TownWall_Step",21,-4.5,0,-90); P(W,21,-7.5,DEF_LVL,-90)
    # circuit ends: a round tower caps the raised east run (walk doors on +-Y, ground door toward the town, +X);
    # the west return hands over to the old palisade it replaces (upgrade story palisade -> town wall)
    P("SM_VK_TownWall_Tower_Round",21,-9,DEF_LVL,-90)
    # demo-only stand-in terrain: the Step climbs a 1.5 m slope onto a plateau (the terrain kit replaces these)
    for x in (16.5,19.5,22.5,25.5):
        P("SM_VK_Def_Standin_Ramp",x,-4.5,DEF_LVL,-90)
        for y in (-7.5,-10.5,-13.5): P("SM_VK_Def_Standin_Plateau",x,y,DEF_LVL,0)
    P("SM_VK_Palisade_Post",-12,6.1,0,0)
    for y in (7.5,10.5,13.5): P("SM_VK_Palisade_Straight",-12,y,0,-90)
    P("SM_VK_Palisade_Post",-12,15,0,90)
    # dressing
    P("SM_VK_Deco_Ivy_B",7.5,-0.78,0,0); P("SM_VK_Deco_Ivy_A",-7.5,-0.78,0,0); P("SM_VK_Deco_Ivy_A",19.5,-0.78,0,0)
    P("SM_VK_Prop_WeaponRack",-10.4,3.0,0,180); P("SM_VK_Prop_BarrelStack",-8.0,3.2,0,0)
    P("SM_VK_Prop_Cart",3.2,-8.5,0,-25); P("SM_VK_Prop_LampPost",-2.4,4.3,0,180); P("SM_VK_Prop_LampPost",5.4,4.3,0,180)
    P("SM_VK_Prop_Crates",8.2,2.6,0,10)

def build_tower_house(coll,origin,kind="fortified",seed=0):
    """2x2-cell stone tower house, 4 storeys (walls to 11.4). kind="fortified": crenellated parapet on corbels,
       corner bartizans, inner Roof_Pyramid_6; kind="domestic": slate hip pyramid + corner turrets.
       Uses the town agent's StoneUp/Turret/Stair pieces when present, else SM_VK_Def_* fallbacks / kit Stair_Ext."""
    rnd=random.Random(seed)
    st={"roof":"Slate","shutter":rnd.choice(["Red","Blue","Natural"])}
    P=def_placer(coll,origin,st)
    up={c:def_pick(n,f) for c,n,f in ((".","SM_VK_Wall_StoneUp","SM_VK_Def_StoneUp"),("X","SM_VK_Wall_StoneUp_Slit","SM_VK_Def_StoneUp_Slit"),
                                     ("W","SM_VK_Wall_StoneUp_Window","SM_VK_Def_StoneUp_Window"),("D","SM_VK_Wall_StoneUp_Door","SM_VK_Def_StoneUp_Door"))}
    cup=def_pick("SM_VK_Corner_StoneUp","SM_VK_Def_CornerUp")
    gw={".":"SM_VK_Wall_Stone","W":"SM_VK_Wall_Stone_Window","D":"SM_VK_Wall_Stone_Door"}
    # faces per level: F (y=-3, x -1.5,1.5), R (x=3), B (y=3, read from outside), L (x=-3)
    lv=[{"F":"..","R":".W","B":"D.","L":"W."},
        {"F":".D","R":"XW","B":"W.","L":".X"},
        {"F":"XX","R":"W.","B":"XW","L":"WX"},
        {"F":"WW","R":"XW","B":"WX","L":"WW"}]
    corners=((-3,-3,0),(3,-3,90),(3,3,180),(-3,3,-90))
    for li,faces in enumerate(lv):
        z=0.0 if li==0 else H1+H2*(li-1)
        lib=gw if li==0 else up
        for side,(cx,cy,rot,axis) in {"F":(0,-3,0,"x"),"R":(3,0,90,"y"),"B":(0,3,180,"x"),"L":(-3,0,-90,"y")}.items():
            s=faces[side]
            for i,c in enumerate(s):
                off=-1.5+3*i
                if side=="F": x,y=off,-3
                elif side=="B": x,y=-off,3
                elif side=="R": x,y=3,off
                else: x,y=-3,-off
                P(lib.get(c,lib["."]),x,y,z,rot)
        for (cx,cy,r) in corners: P("SM_VK_Corner_Stone" if li==0 else cup,cx,cy,z,r)
    top=H1+3*H2
    P(def_pick("SM_VK_Stair_Stone_Ext","SM_VK_Stair_Ext"),-1.5,-3,0,0)
    if kind=="fortified":
        for side,(rot,pos) in {"F":(0,((-1.5,-3),(1.5,-3))),"R":(90,((3,-1.5),(3,1.5))),"B":(180,((1.5,3),(-1.5,3))),"L":(-90,((-3,1.5),(-3,-1.5)))}.items():
            for (x,y) in pos: P("SM_VK_Parapet_Crenel",x,y,top,rot)
        for (cx,cy,r) in corners:
            P("SM_VK_Parapet_Corner",cx,cy,top,r); P("SM_VK_Def_Bartizan",cx,cy,top,r)
        P("SM_VK_Roof_Pyramid_6",0,0,top,0)
        P(def_pick("SM_VK_Banner_Roof",None),0,0,top+2.86,0)
    else:
        P("SM_VK_Roof_Hip",1.5,0,top,0); P(def_pick("SM_VK_Roof_Hip_Plain","SM_VK_Roof_Hip"),-1.5,0,top,180)
        seg=def_pick("SM_VK_Turret_Seg_Stone",None)
        for (cx,cy,r) in corners:
            if seg:   # town turret pieces already carry their axis at local (-0.6,-0.6): place on the corner vertex
                z0=top-H2                     # corbel under the top storey, one seg beside it + one above the eaves
                P(def_pick("SM_VK_Turret_Corbel",None),cx,cy,z0,r)
                for z in (z0,z0+H2): P(seg,cx,cy,z,r)
                P(def_pick("SM_VK_Turret_Cap",None),cx,cy,z0+2*H2,r)
            else:
                P("SM_VK_Def_Bartizan",cx,cy,8.6,r)
    # yard dressing
    P("SM_VK_Prop_Woodpile",3.0,-4.6,0,0,{}); P("SM_VK_Prop_BarrelStack",4.6,1.5,0,90,{})
    P("SM_VK_Deco_Weeds",1.5,-3,0,0,{}); P("SM_VK_Deco_Ivy_B",3.0,1.5,0,90,{})

def build_training_yard(coll,origin,seed=0):
    """barracks (4x2, two storeys, kit house) on the north edge + fenced yard 4x3 cells in front:
       dummies, archery lane (butts facing -X), armor stands, weapon racks, trough. Lot 4x5 cells."""
    rnd=random.Random(seed)
    ox,oy,orz=origin; c,s_=math.cos(orz),math.sin(orz)
    bo=(ox-4.5*s_,oy+4.5*c,orz)
    build_house_v(coll,bo,4,2,{"ground":"Stone","plaster":"White","shutter":"Red","roof":"Slate","seed":seed+7},front=".DW.",back="W..W",chimney=True)
    P=def_placer(coll,origin)
    # first-floor timber gallery along the yard front (town agent's pieces; skipped when absent)
    gal=def_pick("SM_VK_Gallery_Timber",None)
    if gal:
        for x in (-4.5,-1.5,1.5): P(gal,x,1.5,0,0)
        P(def_pick("SM_VK_Gallery_End",gal),4.5,1.5,0,0)
        P(def_pick("SM_VK_Gallery_Side",None),-6.0,1.5,0,0)
    ban=def_pick("SM_VK_Banner_Wall",None)
    for bx in (-3.0,3.0): P(ban,bx,1.32,H1+H2,0,{"cloth":"Red"})
    for i,x in enumerate((-4.2,-2.0,0.2)): P("SM_VK_Prop_TrainingDummy",x,-5.6+0.3*(i%2),0,rnd.uniform(-20,20))
    for y in (-3.6,-0.9): P("SM_VK_Prop_ArcheryButt",4.8,y,0,-90)
    P("SM_VK_Prop_ArmorStand",-4.5,-0.9,0,-10); P("SM_VK_Prop_ArmorStand",-3.4,-0.7,0,15)
    P("SM_VK_Prop_WeaponRack",-1.5,0.85,0,0); P("SM_VK_Prop_WeaponRack",1.5,0.85,0,0)
    P("SM_VK_Prop_Trough",-5.2,-3.0,0,90); P("SM_VK_Prop_BarrelStack",4.2,0.9,0,0)
    P(def_pick("SM_VK_Banner_Pole",None),-5.4,-7.0,0,0,{"cloth":"Red"})
    fence_run(coll,(-6.3,-7.6),(6.3,-7.6),origin,gate_at=2)
    fence_run(coll,(-6.3,-7.6),(-6.3,1.4),origin); fence_run(coll,(6.3,-7.6),(6.3,1.4),origin)

def build_festival_green(coll,origin,seed=0):
    """4x4-cell village green: maypole centre, stage on the north edge, market cross, stocks + pillory,
       hedges east/west, low wall with the gate arch on the south edge, benches, tables, festoon lights."""
    P=def_placer(coll,origin)
    rnd=random.Random(seed)
    P("SM_VK_Prop_Maypole",0,-0.5,0,0)
    P("SM_VK_Prop_Stage",0,4.5,0,0)
    P("SM_VK_Prop_MarketCross",-4.1,-3.4,0,0)
    P("SM_VK_Prop_Stocks",4.3,-4.4,0,-15); P("SM_VK_Prop_Pillory",4.4,-1.7,0,-100)
    for y in (-4.5,-1.5,1.5,4.5):
        P("SM_VK_Deco_Hedge",-6,y,0,90); P("SM_VK_Deco_Hedge",6,y,0,90)
    for x in (-4.5,4.5): P("SM_VK_Deco_Hedge",x,6,0,0)
    for x in (-4.5,-1.5,4.5): P("SM_VK_LowWall",x,-6,0,0)
    P("SM_VK_LowWall_GateArch",1.5,-6,0,0)
    for x in (-6,6): P("SM_VK_LowWall_Post",x,-6,0,0)
    P("SM_VK_Prop_Bench",-3.8,1.6,0,70); P("SM_VK_Prop_Bench",3.9,1.4,0,-70)
    P("SM_VK_Prop_Table",-3.9,-0.6,0,90)
    for dy in (-0.6,0.6): P("SM_VK_Prop_Stool",-3.1,-0.6+dy,0,0); P("SM_VK_Prop_Stool",-4.7,-0.6+dy,0,0)
    P("SM_VK_Prop_BarrelStack",-4.6,4.4,0,90)
    for x in (-3.2,3.2): P("SM_VK_Prop_LampPost",x,-3.6,0,0)
    bunt=def_pick("SM_VK_Prop_Bunting_6",None)
    if bunt: P(bunt,0,-3.6,2.7,0)
    else: P("SM_VK_Prop_Festoon",0,-3.6,2.85,0)
    P("SM_VK_Prop_Festoon",0,2.9,3.35,0)

# ================================================================ SPECS
WS_SPECS=[
    ("SM_VK_Palisade_Straight",def_palisade_straight,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_Diag",def_palisade_diag,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_Post",def_palisade_post,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_Walk",def_palisade_walk,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_Ladder",def_palisade_ladder,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_Gate",def_palisade_gate,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_GateLeaf",def_palisade_gateleaf,dict(wobble=False,grime=True)),
    ("SM_VK_Palisade_Tower",def_palisade_tower,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Beacon",def_beacon,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Straight",def_townwall_straight,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Corner_Out",def_townwall_corner_out,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Corner_In",def_townwall_corner_in,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Stair",def_townwall_stair,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Step",def_townwall_step,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Ruin",def_townwall_ruin,dict(wobble=False,grime=True)),
    ("SM_VK_TownWall_Tower_Round",def_townwall_tower_round,dict(wobble=False,grime=True)),
    ("SM_VK_Gatehouse_Block",def_gatehouse_block,dict(wobble=False,grime=True)),
    ("SM_VK_Gatehouse_Portcullis",def_gatehouse_portcullis,dict(wobble=False,grime=False)),
    ("SM_VK_Gatehouse_GateLeaf",def_gatehouse_gateleaf,dict(wobble=False,grime=True)),
    ("SM_VK_Parapet_Crenel",def_parapet_crenel,dict(wobble=False,grime=False)),
    ("SM_VK_Parapet_Corner",def_parapet_corner,dict(wobble=False,grime=False)),
    ("SM_VK_Roof_Pyramid_6",def_roof_pyramid_6,dict(wobble=False,grime=False)),
    ("SM_VK_Roof_Cone_R2",def_roof_cone_r2,dict(wobble=False,grime=False)),
    ("SM_VK_Prop_TrainingDummy",def_training_dummy,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_ArcheryButt",def_archery_butt,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_ArmorStand",def_armor_stand,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_MarketCross",def_market_cross,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Maypole",def_maypole,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Stage",def_stage,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Stocks",def_stocks,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Pillory",def_pillory,dict(wobble=False,grime=True)),
    ("SM_VK_LowWall_GateArch",def_lowwall_gatearch,dict(wobble=False,grime=True)),
    ("SM_VK_Deco_Hedge",def_hedge,dict(wobble=False,grime=True)),
    # fallbacks for build_tower_house when the town agent's StoneUp / Turret pieces are absent
    ("SM_VK_Def_StoneUp",lambda k: def_stoneup(k,"."),dict(wobble=False,grime=False)),
    ("SM_VK_Def_StoneUp_Slit",lambda k: def_stoneup(k,"X"),dict(wobble=False,grime=False)),
    ("SM_VK_Def_StoneUp_Window",lambda k: def_stoneup(k,"W"),dict(wobble=False,grime=False)),
    ("SM_VK_Def_StoneUp_Door",lambda k: def_stoneup(k,"D"),dict(wobble=False,grime=False)),
    ("SM_VK_Def_CornerUp",def_cornerup,dict(wobble=False,grime=False)),
    ("SM_VK_Def_Bartizan",def_bartizan,dict(wobble=False,grime=False)),
    # demo-only terrain stand-ins used by build_townwall_demo (replace with the terrain kit)
    ("SM_VK_Def_Standin_Plateau",def_standin_plateau,dict(wobble=False,grime=False)),
    ("SM_VK_Def_Standin_Ramp",def_standin_ramp,dict(wobble=False,grime=False)),
]
EXTRA_SPECS+=WS_SPECS
