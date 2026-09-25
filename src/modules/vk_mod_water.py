# =====================  WATER SET  (workshop agent "water", prefix wat_)  =====================
# Datum: bank z 0, water surface -0.6, bed -1.5, piles to -3.0.  Executed after vk_helpers in one namespace.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

WAT_Z=-0.6; WAT_BED=-1.5; WAT_PILE=-3.0

def wat_pick(name,fallback): return name if bpy.data.objects.get(name) else fallback

# ---------------------------------------------------------------- small geometry helpers
def wat_seg(k,a,b,w,h,mi,bevel=0.02,roll=0.0,ext=0.0,segs=1):
    """box of cross-section w x h running from a to b"""
    a=Vector(a); b=Vector(b); d=b-a; L=d.length
    yaw=math.atan2(d.y,d.x); pitch=math.atan2(d.z,math.hypot(d.x,d.y))
    return k.box(tuple((a+b)/2),(L+ext,w,h),mi,rot=(roll,-pitch,yaw),bevel=bevel,segs=segs)

def wat_endgrain(k,f,axis):
    """turn a cylinder cap face into an ENDGRAIN disc"""
    ax=Vector(axis).normalized(); t1=ax.orthogonal().normalized(); t2=ax.cross(t1)
    c=f.calc_center_median(); r=max((v.co-c).length for v in f.verts) or 1.0
    f.material_index=ENDGRAIN
    for l in f.loops:
        d=l.vert.co-c; l[k.uv].uv=(0.5+d.dot(t1)/r*0.44,0.5+d.dot(t2)/r*0.44)

def wat_rod(k,a,b,r1,r2,segs,mi,caps=None):
    """cylinder from a (radius r1) to b (radius r2); caps: None | 'end' (endgrain both) | 'top' (endgrain at b)"""
    a=Vector(a); b=Vector(b); d=b-a; L=d.length
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    vs=_cyl(k,tuple((a+b)/2),r1,r2,L,segs,mi,rot=q)
    if caps:
        dn=d.normalized()
        for f in {f for v in vs for f in v.link_faces}:
            dd=f.normal.dot(dn)
            if dd>0.95 or (caps=="end" and dd<-0.95): wat_endgrain(k,f,f.normal)
    return vs

def wat_tube(k,pts,prof,mi,up=(0,0,1),caps=True,smooth=False,uscale=1.0):
    """continuous swept tube along a polyline; prof = CCW list of (side,up) offsets"""
    pts=[Vector(p) for p in pts]; n=len(pts); rings=[]; Ls=[0.0]
    for i in range(1,n): Ls.append(Ls[-1]+(pts[i]-pts[i-1]).length)
    for i,p in enumerate(pts):
        t=(pts[min(i+1,n-1)]-pts[max(i-1,0)]).normalized()
        u=Vector(up)
        if abs(t.dot(u))>0.97: u=Vector((1,0,0)) if abs(t.x)<0.9 else Vector((0,1,0))
        nx=u.cross(t).normalized(); ny=t.cross(nx).normalized()
        rings.append([k.bm.verts.new(p+nx*a+ny*b) for (a,b) in prof])
    m=len(prof); per=[0.0]
    for j in range(m): per.append(per[-1]+(Vector(prof[(j+1)%m])-Vector(prof[j])).length)
    T=TILE.get(mi,1.0); fs=[]
    for i in range(n-1):
        for j in range(m):
            jj=(j+1)%m
            f=k.bm.faces.new((rings[i][j],rings[i][jj],rings[i+1][jj],rings[i+1][j])); f.material_index=mi; f.smooth=smooth; fs.append(f)
            uv={rings[i][j]:(Ls[i]/T*uscale,per[j]/T),rings[i][jj]:(Ls[i]/T*uscale,per[j+1]/T),
                rings[i+1][jj]:(Ls[i+1]/T*uscale,per[j+1]/T),rings[i+1][j]:(Ls[i+1]/T*uscale,per[j]/T)}
            for l in f.loops: l[k.uv].uv=uv[l.vert]
    if caps:
        for ring_,rev in ((rings[0],True),(rings[-1],False)):
            f=k.bm.faces.new(ring_[::-1] if rev else ring_); f.material_index=mi; fs.append(f)
            for l in f.loops: l[k.uv].uv=(l.vert.co.x/T,l.vert.co.y/T)
    k.bm.normal_update()
    return fs

def wat_circ(r,n=5): return [(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n)) for i in range(n)]
def wat_rect(w,h,dy=0.0): return [(w/2,-h/2+dy),(w/2,h/2+dy),(-w/2,h/2+dy),(-w/2,-h/2+dy)]

def wat_rope(k,pts,r=0.025,mi=HAY,segs=5):
    return wat_tube(k,pts,wat_circ(r,segs),mi,caps=False,smooth=True,uscale=0.3)

def wat_sag(a,b,sag,n=8):
    a=Vector(a); b=Vector(b)
    return [a.lerp(b,i/n)-Vector((0,0,sag*math.sin(math.pi*i/n))) for i in range(n+1)]

def wat_blk(k,P,mi,bevel=0.03,segs=1,tile=None):
    """8-corner block. P(sx,sy,sz) -> point for sx,sy,sz in (-1,1). Returns faces."""
    vs=bmesh.ops.create_cube(k.bm,size=2.0)["verts"]
    sg={}
    for v in vs:
        s=(1 if v.co.x>0 else -1,1 if v.co.y>0 else -1,1 if v.co.z>0 else -1); sg[v]=s
        v.co=Vector(P(*s))
    o=Vector(P(-1,-1,-1)); J=Matrix(((Vector(P(1,-1,-1))-o),(Vector(P(-1,1,-1))-o),(Vector(P(-1,-1,1))-o)))
    faces=list({f for v in vs for f in v.link_faces})
    for f in faces: f.material_index=mi
    if J.determinant()<0:
        for f in faces: f.normal_flip()
    k.bm.normal_update()
    allv=set(vs)
    if bevel>0:
        edges=list({e for v in vs for e in v.link_edges})
        res=bmesh.ops.bevel(k.bm,geom=edges+vs,offset=bevel,segments=segs,profile=0.5,affect="EDGES",clamp_overlap=True)
        allv={v for v in vs if v.is_valid}|set(res["verts"])
    faces=list({f for v in allv for f in v.link_faces})
    k.bm.normal_update()
    k.project(faces,mi,tile=tile)
    return faces

def wat_poly(k,pts,mi,uvfn=None,flip_to=None):
    """single n-gon; flip_to: vector the normal should roughly face"""
    f=k.bm.faces.new([k.bm.verts.new(p) for p in pts]); f.material_index=mi
    k.bm.normal_update()
    if flip_to is not None and f.normal.dot(Vector(flip_to))<0: f.normal_flip()
    if uvfn:
        for l in f.loops: l[k.uv].uv=uvfn(l.vert.co)
    else: k.project([f],mi)
    return f

def wat_strip(k,A,B,mi,uvA=None,uvB=None,out=None):
    """quad strip between two point rows A[i],B[i]; out(center)->vector the face should face"""
    va=[k.bm.verts.new(p) for p in A]; vb=[k.bm.verts.new(p) for p in B]; fs=[]
    for i in range(len(A)-1):
        f=k.bm.faces.new((va[i],va[i+1],vb[i+1],vb[i])); f.material_index=mi; fs.append(f)
        if uvA:
            for l,uv in zip(f.loops,(uvA[i],uvA[i+1],uvB[i+1],uvB[i])): l[k.uv].uv=uv
    k.bm.normal_update()
    if out:
        for f in fs:
            if f.normal.dot(Vector(out(f.calc_center_median())))<0: f.normal_flip()
    if not uvA: k.project(fs,mi)
    return fs

def wat_pile(k,x,y,z0,z1,r,lean=(0.0,0.0),algae=True,segs=8):
    """driven pile, top at (x,y,z1) with an endgrain cap; bottom offset by -lean; slimy band at the waterline"""
    top=Vector((x,y,z1)); bot=Vector((x-lean[0],y-lean[1],z0))
    zs=WAT_Z+0.22
    if algae and z0<zs<z1:
        t=(zs-z0)/(z1-z0); mid=bot.lerp(top,t)
        wat_rod(k,bot,mid,r*0.9,r*(0.9+0.1*t),segs,BARK_MOSSY)
        wat_rod(k,mid,top,r*(0.9+0.1*t),r,segs,WOOD,caps="top")
    else: wat_rod(k,bot,top,r*0.9,r,segs,WOOD,caps="top")

# ---------------------------------------------------------------- PIERS (run along local +X, deck top +0.05)
def wat_deck_planks(k,x0,x1,top=0.05,W=3.0,n=13,seed=0,short=6,short_len=0.4):
    rnd=random.Random(seed); pw=(x1-x0)/n
    for i in range(n):
        xc=x0+(i+0.5)*pw; L=W+rnd.uniform(-0.05,0.05); yc=rnd.uniform(-0.03,0.03)
        if i==short:
            s=1 if rnd.random()<0.5 else -1; L=W-short_len; yc=-s*short_len/2
        k.box((xc,yc,top-0.035+rnd.uniform(-0.012,0.008)),(pw-0.014,L,0.07),PLANKS,
              rot=(rnd.uniform(-0.015,0.015),0,rnd.uniform(-0.01,0.01)),bevel=0.014)

def wat_pier_bent(k,x,seed=0,top=0.35,brace=True):
    """two piles at (x,+-1.35), walings, x-brace"""
    rnd=random.Random(seed)
    for y in(-1.35,1.35):
        wat_pile(k,x+rnd.uniform(-0.03,0.03),y,WAT_PILE,top+rnd.uniform(-0.04,0.03),0.16,lean=(rnd.uniform(-0.12,0.12),rnd.uniform(-0.1,0.1)))
    for dx in(-0.2,0.2): k.box((x+dx,0,-0.47),(0.12,3.3,0.3),WOOD,bevel=0.03)
    if brace:
        wat_seg(k,(x-0.19,-1.3,-1.8),(x-0.19,1.3,-0.4),0.1,0.18,WOOD,bevel=0.02)
        wat_seg(k,(x+0.19,-1.3,-0.4),(x+0.19,1.3,-1.8),0.1,0.18,WOOD,bevel=0.02)
        for y in(-1.35,1.35):
            for dx in(-0.19,0.19): k.box((x+dx*1.25,y,-0.47),(0.04,0.1,0.1),IRON,bevel=0.01)

def wat_pier_deck(k,seed=1):
    wat_deck_planks(k,-1.5,1.5,seed=seed)
    for y in(-1.2,0.0,1.2): k.box((0,y,-0.17),(3.0,0.18 if y else 0.14,0.3),WOOD,bevel=0.03)
    wat_pier_bent(k,-1.5,seed=seed)

def wat_pier_end(k):
    wat_pier_deck(k,seed=2)
    wat_pier_bent(k,1.5,seed=7,top=0.35)
    for y in(-0.9,0.9):                                            # bollards
        lathe(k,[(0.2,0.0),(0.2,0.06),(0.15,0.1),(0.13,0.36),(0.19,0.42),(0.19,0.5),(0.0,0.52)],center=(1.05,y,0.05),segs=10,mi=WOOD)
    rope=[Vector((1.05+0.17*math.cos(a),0.9+0.17*math.sin(a),0.22+0.03*a)) for a in [i*0.7 for i in range(12)]]
    wat_rope(k,rope,0.03)
    # ladder down the end face
    for y in(-0.3,0.3): wat_seg(k,(1.72,y,-1.4),(1.72,y,0.75),0.07,0.06,WOOD,bevel=0.015)
    z=-1.3
    while z<0.7:
        k.box((1.72,0,z),(0.05,0.62,0.05),WOOD,bevel=0.01); z+=0.3
    # lantern pole on the +Y pile
    wat_rod(k,(1.5,1.35,0.3),(1.5,1.35,2.5),0.1,0.085,8,WOOD,caps="top")
    k.box((1.5,1.0,2.35),(0.08,0.8,0.08),WOOD,bevel=0.02)
    wat_seg(k,(1.5,1.35,1.9),(1.5,0.95,2.32),0.06,0.06,WOOD,bevel=0.01)
    sub=Kit(); prop_lantern(sub); merge_kit(k,sub,Matrix.Translation((1.5,1.02+0.42,2.33))@Matrix.Rotation(0,4,"Z"))

def wat_pier_stairs(k):
    """side attachment (same transform as the deck module), hangs off the -Y edge, 4 steps down to -0.55"""
    rnd=random.Random(4)
    for i in range(4):
        z=-0.1-0.15*i; y=-1.65-0.3*i
        k.box((0,y,z-0.035),(1.5,0.3,0.07),PLANKS,rot=(0,0,rnd.uniform(-0.02,0.02)),bevel=0.012)
    for x in(-0.72,0.72):
        wat_seg(k,(x,-1.45,-0.02),(x,-2.85,-0.72),0.07,0.24,WOOD,bevel=0.02)
        wat_pile(k,x,-2.8,WAT_PILE,-0.3,0.12,lean=(0,-0.06))
        wat_rod(k,(x,-2.5,-0.45),(x,-2.5,0.7),0.05,0.045,6,WOOD,caps="top")
    for x in(-0.72,0.72):
        wat_seg(k,(x,-2.5,0.62),(x,-1.45,1.0),0.06,0.06,WOOD,bevel=0.01)
        wat_rod(k,(x,-1.45,0.02),(x,-1.45,1.05),0.05,0.045,6,WOOD,caps="top")

def wat_pier_rail(k):
    """rope rail on the -Y edge of a deck module; posts at x -1.5 and 0 (the +1.5 post belongs to the next module)"""
    y=-1.4
    for x in(-1.5,0.0):
        k.box((x,y,0.45),(0.12,0.12,1.1),WOOD,bevel=0.025)
        k.box((x,y,1.02),(0.15,0.15,0.06),WOOD,bevel=0.02)
    for (za,sag) in ((0.92,0.12),(0.5,0.08)):
        pts=wat_sag((-1.5,y,za),(1.5,y,za),sag,10)
        wat_rope(k,pts,0.022)
    for x in(-1.5,0.0):
        wat_rope(k,[Vector((x+0.075*math.cos(a),y+0.075*math.sin(a),0.9+0.012*a)) for a in [i*0.9 for i in range(9)]],0.02)

# ---------------------------------------------------------------- BOATS: lofted hull
def wat_hull(k,L,N,bfn,kfn,sfn,ffn,p=0.75,q=0.9,m=4,th=0.05,bow="point",stern="transom",nin=None,mi=PLANKS,rim=WOOD):
    """Lofted hull, stern at -L/2, bow at +L/2, origin at the waterline.
       bfn/kfn/sfn/ffn(t): half beam at the sheer, keel z, sheer z, flat-bottom half width.
       Returns dict with station data for fitting thwarts etc."""
    T=TILE[mi]
    def sec(t,inner=False):
        b=bfn(t); kz=kfn(t); sz=sfn(t); fb=min(ffn(t),b*0.95)
        if inner: b=max(b-th,0.0); kz=kz+th; fb=max(fb-th,0.0)
        pts=[]
        for j in range(m+1):
            a=(j/m)*math.pi/2
            y=fb+(b-fb)*(math.sin(a)**p); z=kz+(sz-kz)*((1-math.cos(a))**q)
            pts.append((y,z))
        return pts
    ts=[i/N for i in range(N+1)]
    xs=[-L/2+L*t for t in ts]
    def full(pts):   # left sheer ... keel ... right sheer
        left=[(-y,z) for (y,z) in reversed(pts)]; right=list(pts)
        if pts[0][0]<1e-6: right=right[1:]
        return left+right
    def girth(row):
        g=[0.0];
        for a,b in zip(row[:-1],row[1:]): g.append(g[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
        mid=g[len(g)//2]; return [x-mid for x in g]
    outer=[full(sec(t)) for t in ts]
    nin=N if nin is None else nin
    inner_x=list(xs); inner_x[0]=xs[0]+th*(1 if stern=="transom" else 0)
    if bow=="transom": inner_x[N]=xs[N]-th
    inner=[full(sec(t,True)) for t in ts]
    def mk(rows,X,upto,flip):
        V=[[k.bm.verts.new((X[i],y,z)) for (y,z) in rows[i]] for i in range(upto+1)]
        fs=[]
        for i in range(upto):
            ga=girth(rows[i]); gb=girth(rows[i+1])
            for j in range(len(rows[i])-1):
                q_=(V[i][j],V[i][j+1],V[i+1][j+1],V[i+1][j])
                f=k.bm.faces.new(q_[::-1] if flip else q_); f.material_index=mi; fs.append(f)
                uv={V[i][j]:(ga[j]/T,X[i]/T),V[i][j+1]:(ga[j+1]/T,X[i]/T),V[i+1][j+1]:(gb[j+1]/T,X[i+1]/T),V[i+1][j]:(gb[j]/T,X[i+1]/T)}
                for l in f.loops: l[k.uv].uv=uv[l.vert]
        return V,fs
    Vo,fo=mk(outer,xs,N,False)
    Vi,fi=mk(inner,inner_x,nin,True)
    k.bm.normal_update()
    zax=(kfn(0.5)+sfn(0.5))/2+0.05
    def outv(c):
        ax=max(-L/2+0.6,min(L/2-0.6,c.x)); return Vector((c.x-ax,c.y,c.z-zax))
    for f in fo:
        if f.normal.dot(outv(f.calc_center_median()))<0: f.normal_flip()
    for f in fi:
        if f.normal.dot(outv(f.calc_center_median()))>0: f.normal_flip()
    W=TILE[rim]
    def face(vs,m_,want):
        f=k.bm.faces.new(vs); f.material_index=m_; k.bm.normal_update()
        if f.normal.dot(Vector(want))<0: f.normal_flip()
        k.project([f],m_); return f
    # rims (outer sheer -> inner sheer) along both sides
    for side in(0,-1):
        for i in range(nin):
            face((Vo[i][side],Vo[i+1][side],Vi[i+1][side],Vi[i][side]),rim,(0,0,1))
    # stern
    if stern=="transom":
        face(list(Vo[0]),mi,(-1,0,0)); face(list(Vi[0]),mi,(1,0,0))
        face((Vo[0][0],Vo[0][-1],Vi[0][-1],Vi[0][0]),rim,(0,0,1))
    if bow=="transom":
        face(list(Vo[N]),mi,(1,0,0)); face(list(Vi[N]),mi,(-1,0,0))
        face((Vo[N][0],Vo[N][-1],Vi[N][-1],Vi[N][0]),rim,(0,0,1))
    elif bow=="point":
        # bulkhead at station nin + foredeck over the pointed bow
        if nin<N:
            face(list(Vi[nin]),PLANKS,(-1,0,0))
            ring=[Vi[nin][0]]+[Vo[i][0] for i in range(nin,N+1)]+[Vo[i][-1] for i in range(N,nin-1,-1)]+[Vi[nin][-1]]
            seen=[];
            for v in ring:
                if not seen or (v.co-seen[-1].co).length>1e-5: seen.append(v)
            f=k.bm.faces.new(seen); f.material_index=PLANKS; k.bm.normal_update()
            if f.normal.z<0: f.normal_flip()
            for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[PLANKS],l.vert.co.x/TILE[PLANKS])
    bmesh.ops.remove_doubles(k.bm,verts=[v for row in Vo for v in row],dist=0.002)
    return dict(xs=xs,ts=ts,sec=sec,outer=outer,inner=inner)

def wat_gunwale(k,H,mi=SHUTTER,w=0.07,h=0.1,drop=0.05,out=0.035,upto=None,start=0):
    """rubbing strake along the outer sheer (SHUTTER slot, recolourable)"""
    xs=H["xs"]; n=len(xs)-1 if upto is None else upto
    c=0.022
    prof=[(w/2,-h/2),(w/2,h/2-c),(w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2)]
    for s in(-1,1):
        pts=[]
        for i in range(start,n+1):
            y,z=H["outer"][i][-1]; pts.append(Vector((xs[i],s*(abs(y)+out-w/2),z-drop)))
        pts[-1]+= (pts[-1]-pts[-2]).normalized()*0.02
        wat_tube(k,pts,prof,mi)

def wat_inner_at(H,t):
    """inner half width and z of the sheer + keel at parameter t"""
    pts=H["sec"](t,True); return pts[-1][0],pts[-1][1],pts[0][1]

def wat_oar(k,a,b,r=0.03):
    a=Vector(a); b=Vector(b); d=(b-a).normalized()
    wat_rod(k,a,b-d*0.5,r,r,6,WOOD)
    c=b-d*0.3; yaw=math.atan2(d.y,d.x); pitch=math.atan2(d.z,math.hypot(d.x,d.y))
    k.box(tuple(c),(0.62,0.15,0.025),WOOD,rot=(0.25,-pitch,yaw),bevel=0.01)
    k.box(tuple(a+d*0.08),(0.18,0.05,0.05),WOOD,rot=(0,-pitch,yaw),bevel=0.01)

def wat_rowboat(k):
    L=4.2; B2=0.675
    def bfn(t):
        if t<=0.45: return B2*(1-0.36*((0.45-t)/0.45)**2)
        return B2*max(0.0,1-((t-0.45)/0.55)**2)**0.55
    def kfn(t): return -0.2+0.62*max(0.0,(t-0.7)/0.3)**2.2+0.18*max(0.0,(0.18-t)/0.18)**2
    def sfn(t): return 0.33+0.14*abs(2*t-1)**2.4+0.06*t**4
    H=wat_hull(k,L,14,bfn,kfn,sfn,lambda t:0.0,p=0.8,q=1.0,m=4,th=0.045,bow="point",stern="transom",nin=12)
    wat_gunwale(k,H,upto=14)
    # stem post rising over the bow + keel strip
    xs=H["xs"]
    k.box((L/2-0.02,0,sfn(1)+0.03),(0.12,0.08,0.22),SHUTTER,rot=(0,0.25,0),bevel=0.02)
    wat_tube(k,[(xs[i],0,kfn(H["ts"][i])-0.025) for i in range(1,15)],wat_rect(0.08,0.06),WOOD)
    # thwarts
    for t in(0.3,0.62):
        hb,zs,zk=wat_inner_at(H,t); x=-L/2+L*t
        k.box((x,0,zs-0.17),(0.26,2*hb+0.02,0.05),WOOD,bevel=0.015)
        for s in(-1,1): k.box((x,s*(hb-0.03),zs-0.22),(0.08,0.05,0.12),WOOD,bevel=0.01)
    # stern bench
    hb,zs,zk=wat_inner_at(H,0.1); x=-L/2+L*0.1
    k.box((x,0,zs-0.2),(0.5,2*hb+0.02,0.05),WOOD,bevel=0.015)
    # frames (ribs)
    for t in(0.2,0.38,0.5,0.7,0.82):
        pts=H["sec"](t,True); x=-L/2+L*t
        row=[(-y,z) for (y,z) in reversed(pts[1:])]+list(pts)
        wat_tube(k,[(x,ya*0.97,za+0.018) for (ya,za) in row],wat_rect(0.05,0.035),WOOD,up=(1,0,0))
    # bottom boards
    hb,zs,zk=wat_inner_at(H,0.5)
    k.box((-0.15,0,zk+0.03),(2.5,0.42,0.03),PLANKS,bevel=0.005)
    # rowlocks
    for s in(-1,1):
        hb,zs,zk=wat_inner_at(H,0.5); x=-L/2+L*0.5
        k.box((x,s*(hb+0.02),zs+0.06),(0.04,0.04,0.12),IRON,bevel=0.005)
    # oars resting inside
    for s in(-1,1):
        wat_oar(k,(-1.55,s*0.2,0.2),(1.3,s*0.34,0.3))
    # rope coil on the foredeck + painter ring
    ring(k,(1.7,0,sfn(0.9)+0.03),0.06,0.14,0.05,HAY,n=14,axis="Z")
    k.box((L/2-0.05,0,sfn(1)-0.05),(0.04,0.04,0.08),IRON,bevel=0.005)

def wat_barge(k):
    L=7.5; B2=1.3
    def bfn(t): return B2*(1-0.1*abs(2*t-1)**5)
    def kfn(t):
        e=abs(2*t-1); return -0.3+0.58*max(0.0,(e-0.72)/0.28)**1.6
    def sfn(t): return 0.5+0.12*abs(2*t-1)**3
    H=wat_hull(k,L,16,bfn,kfn,sfn,lambda t:B2-0.35,p=0.45,q=1.6,m=4,th=0.07,bow="transom",stern="transom")
    wat_gunwale(k,H,w=0.1,h=0.13)
    # end decks
    for s in(-1,1):
        x0=s*(L/2-0.07); x1=s*(L/2-1.25)
        hb,zs,zk=wat_inner_at(H,0.5+s*0.4)
        k.box(((x0+x1)/2,0,zs-0.1),(abs(x1-x0),2*hb-0.04,0.06),PLANKS,bevel=0.01)          # deck (boards are in the texture)
        k.box((x1,0,zs-0.25),(0.12,2*hb,0.3),WOOD,bevel=0.02)
    # cross beams + floor boards in the hold
    hb,zs,zk=wat_inner_at(H,0.5)
    k.box((0,0,zk+0.04),(L-2.6,2*hb-0.1,0.04),PLANKS,bevel=0.005)
    for x in(-1.2,1.2):
        k.box((x,0,zs-0.14),(0.2,2*hb+0.04,0.12),WOOD,bevel=0.02)
    # mast, yard, furled sail, stays
    xm=1.2
    wat_rod(k,(xm,0,zk),(xm,0,5.2),0.13,0.08,10,WOOD,caps="top")
    k.box((xm,0,zs-0.08),(0.34,0.34,0.14),WOOD,bevel=0.03)
    for z in(1.3,2.8): k.box((xm,0,z),(0.24,0.24,0.06),IRON,bevel=0.01)
    yard=((xm+0.15,-1.8,4.55),(xm+0.15,1.8,4.55))
    wat_rod(k,yard[0],yard[1],0.055,0.055,8,WOOD,caps="end")
    for i,(y,sy) in enumerate(((-1.25,2.6),(-0.4,2.4),(0.45,2.6),(1.3,2.3))):     # furled sail: 4 stretched bundles between gaskets
        _ico(k,(xm+0.15,y,4.36),0.2,CLOTH_B,(1.0,sy,0.9),sub=1,jit=0.02,seed=i)
    for y in(-0.83,0.02,0.88): ring(k,(xm+0.15,y,4.36),0.17,0.22,0.05,BURLAP,n=8,axis="Y")
    for s in(-1,1): wat_rod(k,(xm+0.15,s*1.7,4.55),(xm+0.15,s*1.5,4.52),0.06,0.04,6,WOOD)
    wat_rope(k,[(xm,0,5.0),(L/2-0.15,0,sfn(1)+0.05)],0.018,WOOD)
    for s in(-1,1): wat_rope(k,[(xm,0,4.9),(xm-1.2,s*(B2-0.05),sfn(0.66)+0.05)],0.018,WOOD)
    wat_rope(k,[(xm,0,4.95),(-L/2+0.4,0,sfn(0.05)+0.05)],0.018,WOOD)
    # cargo
    for (x,y,s,r) in ((-0.5,-0.55,0.62,0.1),(-0.5,0.2,0.62,-0.15),(-1.25,0.5,0.55,0.3)):
        k.box((x,y,zk+0.08+s/2),(s,s,s),WOOD,rot=(0,0,r),bevel=0.03)
        k.box((x,y,zk+0.08+s-0.08),(s+0.03,s+0.03,0.07),WOOD,rot=(0,0,r),bevel=0.015)
    k.box((-0.5,-0.17,zk+0.08+0.62+0.28),(0.55,0.55,0.55),WOOD,rot=(0,0,0.25),bevel=0.03)
    for (x,y) in ((0.35,-0.6),(0.35,0.1)): barrel(k,x,y,zk+0.08,0.3,0.8)
    barrel(k,0.3,0.75,zk+0.38,0.3,0.8,lying=True)
    for i,(x,y) in enumerate(((2.1,-0.45),(2.3,0.35),(2.2,-0.02))):
        _ico(k,(x,y,zk+0.35+(0.33 if i==2 else 0)),0.32,BURLAP,(1.05,0.85,0.9),sub=1,jit=0.02,seed=i)
    # steering sweep over the stern
    wat_rod(k,(-L/2+0.15,0.35,sfn(0)+0.55),(-L/2+0.15,0.35,sfn(0)-0.2),0.06,0.06,6,WOOD,caps="top")
    wat_oar(k,(-L/2+1.3,0.2,1.35),(-L/2-2.3,0.55,-0.35),r=0.05)

# ---------------------------------------------------------------- WOODEN BRIDGES (road along local X, deck top +0.35)
def wat_smooth01(t): t=max(0.0,min(1.0,t)); return t*t*(3-2*t)
def wat_bw_planks(k,x0,x1,zfn,seed=0,W=3.4,n=12):
    rnd=random.Random(seed); pw=(x1-x0)/n
    for i in range(n):
        xc=x0+(i+0.5)*pw; z=zfn(xc); pitch=math.atan2(zfn(xc+0.05)-zfn(xc-0.05),0.1)
        k.box((xc,rnd.uniform(-0.04,0.04),z-0.035+rnd.uniform(-0.012,0.006)),(pw-0.016,W+rnd.uniform(-0.08,0.06),0.07),PLANKS,
              rot=(rnd.uniform(-0.012,0.012),-pitch,rnd.uniform(-0.018,0.018)),bevel=0.014)
def wat_bw_stringers(k,x0,x1,zfn,n=8):
    xs=[x0+(x1-x0)*i/n for i in range(n+1)]
    for y in(-1.4,-0.7,0.0,0.7,1.4):
        wat_tube(k,[(x,y,zfn(x)-0.07-0.15) for x in xs],wat_rect(0.2,0.3),WOOD)
def wat_bw_post(k,x,y,z0,z1,w=0.14):
    k.box((x,y,(z0+z1)/2),(w,w,z1-z0),WOOD,bevel=0.025)
    k.box((x,y,z1+0.03),(w+0.05,w+0.05,0.07),WOOD,bevel=0.02)
def wat_bw_rails(k,pts_top,drop=0.5,seed=0):
    rnd=random.Random(seed)
    wat_tube(k,pts_top,wat_rect(0.12,0.14),WOOD,up=(0,0,1))
    wat_tube(k,[Vector(p)-Vector((0,0,drop)) for p in pts_top],wat_rect(0.08,0.1),WOOD,up=(0,0,1))

def wat_bridge_wood_mid(k):
    zf=lambda x:0.35
    wat_bw_planks(k,-1.5,1.5,zf,seed=3); wat_bw_stringers(k,-1.5,1.5,zf,n=1)
    for s in(-1,1):
        for x in(-1.5,0.0): wat_bw_post(k,x,s*1.62,-0.25,1.38)
        wat_bw_rails(k,[(-1.5,s*1.62,1.3),(0.0,s*1.62,1.3),(1.5,s*1.62,1.3)])
        k.box((0,s*1.52,-0.02),(3.0,0.1,0.26),WOOD,bevel=0.02)        # edge fascia over the outer stringer
        for x in(-1.5,0.0): wat_seg(k,(x,s*1.62,0.1),(x+0.45,s*1.62,0.75),0.09,0.1,WOOD,bevel=0.015)

def wat_bridge_wood_end(k):
    zf=lambda x:0.05+0.3*wat_smooth01((x+1.5)/2.4)
    wat_bw_planks(k,-1.5,1.5,zf,seed=5); wat_bw_stringers(k,-1.5,1.5,zf)
    rnd=random.Random(11)
    for i,y in enumerate((-1.3,-0.45,0.4,1.25)):                      # rock abutment on the bank
        rock(k,(-0.9+rnd.uniform(-0.15,0.15),y,-0.35),(1.1,0.95,0.75),seed=40+i,mi=ROCK,tilt=0.1)
    rock(k,(-1.3,-1.6,-0.2),(0.7,0.7,0.6),seed=48,mi=ROCK); rock(k,(-1.25,1.62,-0.25),(0.8,0.7,0.6),seed=49,mi=ROCK)
    k.box((-0.75,0,-0.02),(0.3,3.6,0.24),WOOD,bevel=0.03)             # sill beam on the rocks
    for s in(-1,1):
        yf=s*1.92
        wat_bw_post(k,-1.4,yf,-0.3,1.3,w=0.18)
        k.box((-1.4,yf,1.43),(0.12,0.12,0.12),WOOD,rot=(0,0,0.785),bevel=0.03)
        wat_bw_post(k,0.0,s*1.62,-0.25,1.38)
        top=[(-1.4,yf,zf(-1.4)+1.0),(-0.7,s*1.75,zf(-0.7)+1.0),(0.0,s*1.62,1.3),(1.5,s*1.62,1.3)]
        wat_bw_rails(k,top,drop=0.45)
        k.box((0.75,s*1.52,-0.02),(1.5,0.1,0.26),WOOD,bevel=0.02)

def wat_bridge_wood_bent(k):
    rnd=random.Random(21)
    for y in(-1.3,0.0,1.3):
        wat_pile(k,rnd.uniform(-0.02,0.02),y,WAT_PILE,-0.1,0.14,lean=(rnd.uniform(-0.08,0.08),rnd.uniform(-0.1,0.1)))
    k.box((0,0,-0.17),(0.3,3.6,0.3),WOOD,bevel=0.035)
    for s in(-1,1):
        wat_seg(k,(s*0.17,-1.3,-1.9),(s*0.17,1.3,-0.45),0.08,0.16,WOOD,bevel=0.015) if s<0 else \
        wat_seg(k,(s*0.17,-1.3,-0.45),(s*0.17,1.3,-1.9),0.08,0.16,WOOD,bevel=0.015)
    k.box((0,0,-0.95),(0.46,3.0,0.14),WOOD,bevel=0.02)
    for y in(-1.3,0,1.3):
        for dx in(-0.16,0.16): k.box((dx*1.3,y,-0.17),(0.04,0.09,0.09),IRON,bevel=0.01)

def wat_bridge_log(k):
    z0,z1=0.12,0.2; top=0.17
    vs=wat_rod(k,(-2.25,0,z0),(2.25,0,z1),0.31,0.27,10,BARK_OAK,caps="end")
    for v in vs:
        zt=z0+(z1-z0)*(v.co.x+2.25)/4.5+top
        if v.co.z>zt: v.co.z=zt
    k.bm.normal_update()
    for f in {f for v in vs for f in v.link_faces}:
        if f.normal.z>0.9: f.material_index=WOOD; k.project([f],WOOD)
    rnd=random.Random(5); ptop=[]
    for x in(-1.9,0.1,2.0):
        a=Vector((x,0.42,-0.9)); b=Vector((x+rnd.uniform(-0.06,0.06),0.44+rnd.uniform(-0.03,0.05),1.08))
        wat_rod(k,a,b,0.06,0.05,6,BARK_OAK,caps="top"); ptop.append(b-Vector((0,0,0.08)))
    rail=[Vector((-2.2,0.44,1.0))]+ptop+[Vector((2.25,0.44,1.02))]
    wat_tube(k,rail,wat_circ(0.05,6),BARK_BIRCH,caps=True)
    for p in ptop: ring(k,tuple(p),0.05,0.085,0.07,HAY,n=8,axis="Z")

# ---------------------------------------------------------------- STONE BRIDGE (road along local X, 6 m span)
WAT_SB_HW=2.25; WAT_SB_YF=1.95; WAT_SB_IN=1.6
def wat_sb_arc(hw=WAT_SB_HW,zs=-0.6,za=0.8):
    R=(hw*hw+(za-zs)**2)/(2*(za-zs)); zc=za-R; th=math.asin(hw/R); return R,zc,th
def wat_sb_deck(x): return 1.2+0.1*math.cos(math.pi*max(-3.0,min(3.0,x))/6.0)
WAT_SB_COURSES=[0.46,0.42,0.5,0.44,0.48,0.42,0.46]
def wat_sb_string(k,x0,x1,dfn,s,nb,seed=0,bot=0.14,top=0.06,out=0.13):
    rnd=random.Random(seed); xs=[x0]
    for i in range(1,nb): xs.append(x0+(x1-x0)*(i+rnd.uniform(-0.2,0.2))/nb)
    xs.append(x1); yf=s*WAT_SB_YF
    for a,b in zip(xs[:-1],xs[1:]):
        ya,yb=yf+s*out,yf-s*0.25
        wat_blk(k,lambda sx,sy,sz,a=a,b=b,ya=ya,yb=yb:((a+0.006) if sx<0 else (b-0.006),ya if sy<0 else yb,dfn(a if sx<0 else b)+(top if sz>0 else -bot)),
                STONE_BLOCK,bevel=0.03)
def wat_sb_coping(k,x0,x1,dfn,s,nb,seed=0,h0=0.8,th=0.13,w=0.45):
    rnd=random.Random(seed); xs=[x0]
    for i in range(1,nb): xs.append(x0+(x1-x0)*(i+rnd.uniform(-0.18,0.18))/nb)
    xs.append(x1); yc=s*(WAT_SB_YF-WAT_SB_PARW/2)
    for a,b in zip(xs[:-1],xs[1:]):
        dz=rnd.uniform(-0.012,0.018); tl=rnd.uniform(-0.012,0.012)
        wat_blk(k,lambda sx,sy,sz,a=a,b=b,dz=dz,tl=tl:((a+0.008) if sx<0 else (b-0.008),yc+sy*w/2,dfn(a if sx<0 else b)+h0+dz+(th+tl*sy if sz>0 else 0.0)),
                STONE_BLOCK,bevel=0.035)
WAT_SB_PARW=0.35
def wat_sb_parapet(k,xs,dfn,s,z_out=0.06,h=0.8):
    yo=s*WAT_SB_YF; yi=s*(WAT_SB_YF-WAT_SB_PARW)
    wat_strip(k,[(x,yo,dfn(x)+z_out) for x in xs],[(x,yo,dfn(x)+h) for x in xs],STONE,out=lambda c:(0,s,0))
    wat_strip(k,[(x,yi,dfn(x)-0.02) for x in xs],[(x,yi,dfn(x)+h) for x in xs],STONE,out=lambda c:(0,-s,0))
def wat_sb_road(k,xs,dfn,crown=0.035):
    ys=[-WAT_SB_IN,-0.8,0.0,0.8,WAT_SB_IN]
    for a,b in zip(ys[:-1],ys[1:]):
        za=crown*(1-(a/WAT_SB_IN)**2); zb=crown*(1-(b/WAT_SB_IN)**2)
        wat_strip(k,[(x,a,dfn(x)+za) for x in xs],[(x,b,dfn(x)+zb) for x in xs],ASHLAR,out=lambda c:(0,0,1),
                  uvA=[(x/3.0,a/3.0) for x in xs],uvB=[(x/3.0,b/3.0) for x in xs])
def wat_sb_quoins(k,x_in,x_out,s,z0,z1,seed=0,out=0.13,wet=-0.3):
    """stacked chunky blocks up a pier face (x_in..x_out), alternating long/short"""
    z=z0; i=0; yf=s*WAT_SB_YF
    while z<z1-0.08:
        h=min(WAT_SB_COURSES[i%len(WAT_SB_COURSES)],z1-z)
        xa=x_in if i%2==0 else x_in+(x_out-x_in)*0.22
        mi=ROCK_MOSSY if z+h<wet+0.25 else STONE_BLOCK
        k.box(((xa+x_out)/2,yf+s*(out-0.35)/2,z+h/2),(abs(x_out-xa)-0.02,0.35+out,h-0.03),mi,bevel=0.05,segs=2,jitter=0.012,seed=seed*31+i)
        z+=h; i+=1
def wat_bridge_stone_span(k):
    R,zc,th=wat_sb_arc(); hw=WAT_SB_HW; yf=WAT_SB_YF; dfn=wat_sb_deck
    n=18; angs=[math.pi/2+th-2*th*i/n for i in range(n+1)]
    arc=[(R*math.cos(a),zc+R*math.sin(a)) for a in angs]
    zt=lambda x: dfn(x)-0.14
    for s in(-1,1):
        y=s*yf; o=lambda c,s=s:(0,s,0)
        for (xa,xb) in ((-3.0,-hw),(hw,3.0)):
            xs=[xa,(xa+xb)/2,xb]
            wat_strip(k,[(x,y,-1.6) for x in xs],[(x,y,zt(x)) for x in xs],STONE,out=o)
        wat_strip(k,[(x,y,z) for x,z in arc],[(x,y,zt(x)) for x,z in arc],STONE,out=o)
    # soffit (barrel) + pier sides under the springing
    A=[(x,-yf,z) for x,z in arc]; B=[(x,yf,z) for x,z in arc]
    sl=[R*(angs[0]-a) for a in angs]
    wat_strip(k,A,B,ASHLAR,uvA=[(-yf/3.0,u/3.0) for u in sl],uvB=[(yf/3.0,u/3.0) for u in sl],out=lambda c:(-c.x,0,zc-c.z))
    for sx in(-1,1):
        wat_poly(k,[(sx*hw,-yf,-1.6),(sx*hw,yf,-1.6),(sx*hw,yf,-0.6),(sx*hw,-yf,-0.6)],STONE,flip_to=(-sx,0,0))
    # voussoir rings
    nv=13; da=2*th/nv; ga=0.014/R
    for s in(-1,1):
        for i in range(nv):
            a0=math.pi/2+th-i*da-ga; a1=a0-da+2*ga; ks=(i==nv//2)
            rd=0.55 if ks else (0.45 if i%2==0 else 0.53); ob=0.18 if ks else 0.1
            y0=s*(yf+ob); y1=s*(yf-0.32)
            def P(sx,sy,sz,a0=a0,a1=a1,rd=rd,y0=y0,y1=y1):
                a=a0 if sx<0 else a1; r=R-0.035 if sz<0 else R+rd
                return (math.cos(a)*r,y0 if sy<0 else y1,zc+math.sin(a)*r)
            wat_blk(k,P,STONE_BLOCK,bevel=0.045,segs=2)
    # half-pier quoins (course heights shared so neighbouring spans line up at the seam)
    for sx in(-1,1):
        for s in(-1,1):
            wat_sb_quoins(k,sx*hw,sx*3.0,s,-1.6,zt(sx*2.6)-0.02,seed=(sx+2)*3+s)
    # string course, parapets, coping, road
    xs=[-3.0+0.5*i for i in range(13)]
    for s in(-1,1):
        wat_sb_string(k,-3.0,3.0,dfn,s,9,seed=5+s)
        wat_sb_parapet(k,xs,dfn,s)
        wat_sb_coping(k,-3.0,3.0,dfn,s,11,seed=8+s)
    wat_sb_road(k,xs,dfn)

def wat_bridge_stone_ramp(k):
    """span side at x -1.5 (deck +1.2), bank at x +1.5 (deck 0.0); newels + splayed wing walls at the bank end"""
    dfn=lambda x:1.2*(1.5-max(-1.5,min(1.5,x)))/3.0; yf=WAT_SB_YF
    xs=[-1.5+0.375*i for i in range(9)]
    for s in(-1,1):
        wat_strip(k,[(x,s*yf,-0.6) for x in xs],[(x,s*yf,dfn(x)-0.14) for x in xs],STONE,out=lambda c,s=s:(0,s,0))
        wat_sb_string(k,-1.5,1.5,dfn,s,5,seed=15+s)
        xp=[x for x in xs if x<=0.95]+[0.95]
        wat_sb_parapet(k,xp,dfn,s)
        wat_sb_coping(k,-1.5,0.95,dfn,s,5,seed=18+s)
        # newel
        yc=s*(yf-WAT_SB_PARW/2)
        for j,(z0,h,w) in enumerate(((-0.3,0.55,0.66),(0.25,0.45,0.62),(0.7,0.4,0.6))):
            rock(k,(1.22,yc,z0+h/2),(w,w,h-0.02),seed=60+j+(s+1)*5,tilt=0.02)
        k.box((1.22,yc,1.16),(0.74,0.74,0.13),STONE_BLOCK,bevel=0.04)
        lathe(k,[(0.3,1.22),(0.3,1.3),(0.0,1.62)],center=(1.22,yc,0),segs=4,mi=STONE_BLOCK)
        # splayed wing wall
        d=Vector((math.cos(math.radians(30)),s*math.sin(math.radians(30)),0)); nrm=Vector((-d.y,d.x,0))*(-s)
        p0=Vector((1.5,s*(yf-WAT_SB_PARW/2),0)); L=1.55; tw=WAT_SB_PARW/2
        def WP(sx,sy,sz,p0=p0,d=d,nrm=nrm):
            p=p0+d*(0.0 if sx<0 else L)+nrm*(tw*sy)
            return (p.x,p.y,-0.4 if sz<0 else (0.82 if sx<0 else 0.5))
        wat_blk(k,WP,STONE,bevel=0)
        for j in range(3):
            ta,tb=j/3,(j+1)/3
            def CP(sx,sy,sz,ta=ta,tb=tb,p0=p0,d=d,nrm=nrm):
                t=ta if sx<0 else tb; p=p0+d*(L*t+(0.01 if sx<0 else -0.01))+nrm*(0.23*sy)
                return (p.x,p.y,0.82-0.32*t+(0.13 if sz>0 else 0.0))
            wat_blk(k,CP,STONE_BLOCK,bevel=0.035)
        pe=p0+d*(L+0.1)
        rock(k,(pe.x,pe.y,0.2),(0.5,0.5,0.62),seed=70+s,tilt=0.02)
    wat_sb_road(k,xs,dfn)

def wat_bridge_stone_pier(k):
    """cutwater pier placed at the seam between two spans (origin on the seam, river bed -1.5)"""
    yf=WAT_SB_YF
    k.box((0,0,-1.75),(1.9,2*yf+0.3,0.5),STONE,bevel=0)
    for s in(-1,1):
        tip=Vector((0,s*(yf+1.2),0)); a=Vector((-0.75,s*yf,0)); b=Vector((0.75,s*yf,0))
        for (p,q) in ((a,tip),(tip,b)):
            for (z0,z1,mi) in ((-2.0,-0.35,ROCK_MOSSY),(-0.35,0.3,STONE)):
                wat_poly(k,[(p.x,p.y,z0),(q.x,q.y,z0),(q.x,q.y,z1),(p.x,p.y,z1)],mi,flip_to=((p+q)/2-Vector((0,s*yf,0))).normalized()*1.0+Vector((0,0,0)))
        # cap: sloped pyramid leaning on the spandrel
        c0=Vector((-0.85,s*(yf-0.02),0.3)); c1=Vector((0.85,s*(yf-0.02),0.3)); ct=Vector((0,s*(yf+1.33),0.3)); ap=Vector((0,s*(yf+0.05),1.0))
        for tri in ((c0,ct,ap),(ct,c1,ap)):
            wat_poly(k,[tuple(v) for v in tri],STONE_BLOCK,flip_to=(0,s*0.5,1))
        wat_poly(k,[tuple(c0),tuple(ct),tuple(c1)],STONE_BLOCK,flip_to=(0,0,-1))
        z=-0.62
        for i,h in enumerate((0.46,0.46)):
            k.box((0,s*(yf+1.02),z+h/2),(0.5 if i%2 else 0.62,0.55,h-0.03),STONE_BLOCK,rot=(0,0,math.pi/4),bevel=0.05,segs=2,jitter=0.01,seed=90+i+s)
            z+=h

# ---------------------------------------------------------------- generic lathe (partial arcs, cylindrical UVs)
def wat_lathe(k,prof,center=(0,0,0),segs=16,mi=STONE_BLOCK,a0=0.0,a1=2*math.pi,smooth=False,uvcyl=True):
    cx,cy,cz=center; closed=abs((a1-a0)-2*math.pi)<1e-6; n=segs if closed else segs+1
    T=TILE.get(mi,1.0); rm=max(0.05,sum(r for r,z in prof)/len(prof))
    rings=[[k.bm.verts.new((cx+math.cos(a0+(a1-a0)*i/segs)*r,cy+math.sin(a0+(a1-a0)*i/segs)*r,cz+z)) for i in range(n)] for (r,z) in prof]
    dist=[0.0]
    for (ra,za),(rb,zb) in zip(prof[:-1],prof[1:]): dist.append(dist[-1]+math.hypot(rb-ra,zb-za))
    fs=[]
    for j in range(len(prof)-1):
        for i in range(segs):
            i2=(i+1)%n
            f=k.bm.faces.new((rings[j][i],rings[j][i2],rings[j+1][i2],rings[j+1][i])); f.material_index=mi; f.smooth=smooth; fs.append(f)
            if uvcyl:
                ua=(a1-a0)*i/segs*rm/T; ub=(a1-a0)*(i+1)/segs*rm/T
                uv={rings[j][i]:(ua,dist[j]/T),rings[j][i2]:(ub,dist[j]/T),rings[j+1][i2]:(ub,dist[j+1]/T),rings[j+1][i]:(ua,dist[j+1]/T)}
                for l in f.loops: l[k.uv].uv=uv[l.vert]
    k.bm.normal_update()
    if not uvcyl: k.project(fs,mi)
    return fs,rings

def wat_disc(k,c,r,mi,n=12,axis=(0,0,1),uvscale=None):
    ax=Vector(axis).normalized(); t1=ax.orthogonal().normalized(); t2=ax.cross(t1); C=Vector(c)
    f=k.bm.faces.new([k.bm.verts.new(C+(t1*math.cos(2*math.pi*i/n)+t2*math.sin(2*math.pi*i/n))*r) for i in range(n)]); f.material_index=mi
    k.bm.normal_update()
    if f.normal.dot(ax)<0: f.normal_flip()
    s=uvscale or TILE.get(mi,1.0)
    for l in f.loops: d=l.vert.co-C; l[k.uv].uv=(d.dot(t1)/s+0.5,d.dot(t2)/s+0.5)
    return f

def wat_annulus(k,c,r_in,r_out,depth,mi,n=24,axis="X"):
    """flat ring with thickness, normal along axis X / Y / Z"""
    cx,cy,cz=c
    def P(r,a,d):
        ca,sa=math.cos(a)*r,math.sin(a)*r
        if axis=="X": return (cx+d,cy+ca,cz+sa)
        if axis=="Y": return (cx+ca,cy+d,cz+sa)
        return (cx+ca,cy+sa,cz+d)
    A=Vector({"X":(1,0,0),"Y":(0,1,0),"Z":(0,0,1)}[axis])
    fo=[];fi=[];bo=[];bi=[]
    for i in range(n):
        a=2*math.pi*i/n
        fo.append(k.bm.verts.new(P(r_out,a,-depth/2))); fi.append(k.bm.verts.new(P(r_in,a,-depth/2)))
        bo.append(k.bm.verts.new(P(r_out,a,depth/2))); bi.append(k.bm.verts.new(P(r_in,a,depth/2)))
    fs=[]; C=Vector(c)
    for i in range(n):
        j=(i+1)%n
        for q_,want in (((fo[i],fo[j],fi[j],fi[i]),-A),((bo[i],bo[j],bi[j],bi[i]),A),((fo[i],fo[j],bo[j],bo[i]),None),((fi[i],fi[j],bi[j],bi[i]),"in")):
            f=k.bm.faces.new(q_); f.material_index=mi; fs.append(f); k.bm.normal_update()
            cc=f.calc_center_median(); rad=(cc-C)-A*(cc-C).dot(A)
            w=want if isinstance(want,Vector) else (rad if want is None else -rad)
            if f.normal.dot(w)<0: f.normal_flip()
    k.project(fs,mi); return fs

# ---------------------------------------------------------------- QUAYS (contour pieces: face -Y toward the water, pivot at the segment midpoint)
def wat_quay_body(k,x0,x1,seed=0,cop=True):
    k.box(((x0+x1)/2,0.0,-0.31),(x1-x0,0.9,0.58),STONE,bevel=0)                      # face -0.45, z -0.6..-0.02
    wat_blk(k,lambda sx,sy,sz:(x0 if sx<0 else x1,(-0.45-(0.1 if sz<0 else 0.0)) if sy<0 else 0.45,-2.0 if sz<0 else -0.45),ROCK_MOSSY,bevel=0)
    if cop:
        rnd=random.Random(seed); n=max(1,int(round((x1-x0)/0.55))); xs=[x0]+[x0+(x1-x0)*(i+rnd.uniform(-0.15,0.15))/n for i in range(1,n)]+[x1]
        for a,b in zip(xs[:-1],xs[1:]):
            dz=rnd.uniform(-0.012,0.01)
            k.box(((a+b)/2,-0.27,-0.12+dz),(b-a-0.02,0.56,0.26),STONE_BLOCK,rot=(rnd.uniform(-0.01,0.01),rnd.uniform(-0.015,0.015),0),bevel=0.04,segs=2,jitter=0.008,seed=int(a*100)+seed)
def wat_quay_ring(k,x):
    k.box((x,-0.47,-0.36),(0.14,0.04,0.14),IRON,bevel=0.01)
    wat_annulus(k,(x,-0.52,-0.5),0.1,0.15,0.035,IRON,n=14,axis="Y")
def wat_quay_straight(k):
    wat_quay_body(k,-1.5,1.5,seed=3); wat_quay_ring(k,0.0)
def wat_quay_post(k):
    k.box((0,0,-0.3),(0.58,0.58,0.6),STONE_BLOCK,bevel=0)                       # hidden skirt to -0.6
    rock(k,(0,0,0.14),(0.66,0.66,0.3),seed=81,tilt=0.02)
    k.box((0,0,0.55),(0.54,0.54,0.56),STONE_BLOCK,bevel=0.05,segs=2,jitter=0.01,seed=82)
    k.box((0,0,0.87),(0.64,0.64,0.1),STONE_BLOCK,bevel=0.03)
    lathe(k,[(0.3,0.92),(0.3,0.98),(0.0,1.18)],segs=4,mi=STONE_BLOCK)
    wat_annulus(k,(0,-0.3,0.55),0.07,0.11,0.03,IRON,n=12,axis="Y")
def wat_quay_stair(k):
    """quay module with 4 steps (rise 0.15) cut down to the water, 1.2 wide, landing at -0.6"""
    wat_quay_body(k,-1.5,-0.6,seed=5); wat_quay_body(k,0.6,1.5,seed=6)
    wat_blk(k,lambda sx,sy,sz:(-0.6 if sx<0 else 0.6,(-0.55 if sz<0 else -0.45) if sy<0 else 0.45,-2.0 if sz<0 else -0.9),ROCK_MOSSY,bevel=0)
    rnd=random.Random(7)
    for i in range(4):
        top=-0.15*(i+1); y1=0.45-0.3*i; y0=y1-0.3-(0.05 if i==3 else 0.0)
        k.box((0,(y0+y1)/2-0.02,(top-0.95)/2),(1.2,y1-y0+0.04,top+0.95),STONE_BLOCK,rot=(0,0,rnd.uniform(-0.01,0.01)),bevel=0.035,jitter=0.006,seed=i)
    for sx in(-1,1):
        k.box((sx*0.72,-0.27,-0.05),(0.28,0.58,0.26),STONE_BLOCK,bevel=0.04,segs=2)
    wat_quay_ring(k,1.05)

# ---------------------------------------------------------------- MILL: wheel (animated, hub at origin, axle along local X), axle wall, wheel pier, millstone
def wat_waterwheel(k):
    for x in(-0.45,0.45):
        wat_annulus(k,(x,0,0),2.15,2.4,0.12,WOOD,n=32,axis="X")
        for i in range(8):
            a=2*math.pi*(i+0.5)/8
            k.box((x,math.cos(a)*1.26,math.sin(a)*1.26),(0.12,1.9,0.12),WOOD,rot=(a,0,0),bevel=0.02)
        wat_annulus(k,(x,0,0),0.36,0.5,0.16,WOOD,n=12,axis="X")
    for i in range(16):
        a=2*math.pi*i/16
        k.box((0,math.cos(a)*2.34,math.sin(a)*2.34),(1.0,0.52,0.08),PLANKS,rot=(a+0.12,0,0),bevel=0.015)
        k.box((0,math.cos(a)*2.14,math.sin(a)*2.14),(0.98,0.07,0.07),WOOD,rot=(a,0,0),bevel=0.01)
    wat_rod(k,(-0.55,0,0),(0.55,0,0),0.35,0.35,12,WOOD,caps="end")
    for x in(-0.3,0.3): wat_annulus(k,(x,0,0),0.34,0.38,0.06,IRON,n=12,axis="X")
    wat_rod(k,(-1.1,0,0),(1.2,0,0),0.15,0.15,10,WOOD,caps="end")
    for x in(-1.0,1.1): wat_annulus(k,(x,0,0),0.14,0.17,0.06,IRON,n=10,axis="X")

def wat_wall_axle(k):
    """Wall_Stone variant for the wheel end: masonry down into the race (-1.6), bearing block + axle hole at z 1.3"""
    stone_panel(k,-1.5,1.5,-1.6,H1); batter(k)
    k.box((0,-0.33,-1.0),(3.0,0.1,1.2),ROCK_MOSSY,bevel=0)                       # wet band z -1.6..-0.4
    rnd=random.Random(12); x=-1.5
    while x<1.4:                                                                  # footing rocks at the waterline
        w=min(rnd.uniform(0.45,0.8),1.5-x)
        rock(k,(x+w/2,-0.3,-0.45),(w-0.06,0.34,0.4),seed=rnd.randrange(1<<20),mi=ROCK_MOSSY); x+=w
    wall_rocks(k,-1.5,1.5,0.5,H1,n=2,seed=9,avoid=((-0.75,0.75,0.6,2.0),))
    k.box((0,-0.42,1.3),(0.64,0.34,0.62),STONE_BLOCK,bevel=0.05,segs=2)          # bearing block
    k.box((0,-0.38,0.9),(0.52,0.26,0.2),STONE_BLOCK,bevel=0.04)                  # corbel
    wat_disc(k,(0,-0.595,1.3),0.19,VOID,n=14,axis=(0,-1,0))
    wat_annulus(k,(0,-0.6,1.3),0.18,0.25,0.03,IRON,n=14,axis="Y")
    for x in(-1.5,1.5):                                                           # close the ends below ground
        wat_poly(k,[(x,-0.33,-1.6),(x,0.25,-1.6),(x,0.25,0.0),(x,-0.33,0.0)],STONE,flip_to=(x,0,0))

def wat_wheel_pier(k):
    """free-standing pier for the outer axle end: 0.8 x 1.0, z -1.6..1.5; bearing faces -X at z 1.3"""
    k.box((0,0,-0.05),(0.8,1.0,3.1),STONE,bevel=0)
    k.box((0,0,-1.0),(0.86,1.06,1.2),ROCK_MOSSY,bevel=0)
    for s in(-1,1):                                                               # small cutwaters
        tip=Vector((0,s*0.95,0)); a=Vector((-0.4,s*0.5,0)); b=Vector((0.4,s*0.5,0))
        for p,q in ((a,tip),(tip,b)):
            wat_poly(k,[(p.x,p.y,-1.6),(q.x,q.y,-1.6),(q.x,q.y,-0.3),(p.x,p.y,-0.3)],ROCK_MOSSY,flip_to=tuple(((p+q)/2).normalized()))
        wat_poly(k,[(-0.42,s*0.5,-0.3),(0,s*0.98,-0.3),(0,s*0.5,0.15)],STONE_BLOCK,flip_to=(-1,s,1))
        wat_poly(k,[(0,s*0.98,-0.3),(0.42,s*0.5,-0.3),(0,s*0.5,0.15)],STONE_BLOCK,flip_to=(1,s,1))
    z=-0.45; i=0
    for h in (0.46,0.42,0.48,0.44):
        for sx in(-1,1):
            for sy in(-1,1):
                lx=(i%2==0)
                k.box((sx*(0.4-(0.22 if lx else 0.15)),sy*(0.5-(0.15 if lx else 0.22)),z+h/2),(0.5 if lx else 0.36,0.36 if lx else 0.5,h-0.03),STONE_BLOCK,bevel=0.045,segs=2,jitter=0.01,seed=i*7+sx*3+sy)
        z+=h; i+=1
    k.box((0,0,1.55),(0.98,1.18,0.16),STONE_BLOCK,bevel=0.04,segs=2)
    k.box((-0.52,0,1.28),(0.3,0.5,0.46),STONE_BLOCK,bevel=0.04,segs=2)
    wat_annulus(k,(-0.68,0,1.3),0.15,0.22,0.03,IRON,n=12,axis="X")
    wat_disc(k,(-0.675,0,1.3),0.15,VOID,n=12,axis=(-1,0,0))

def wat_millstone_one(k,M):
    sub=Kit()
    wat_lathe(sub,[(0.1,0.0),(0.62,0.0),(0.66,0.04),(0.66,0.25),(0.62,0.3),(0.1,0.3),(0.1,0.0)],segs=16,mi=STONE_BLOCK)
    wat_disc(sub,(0,0,0.15),0.1,VOID,n=10)
    for i in range(8):
        a=2*math.pi*i/8+0.2
        sub.box((math.cos(a)*0.38,math.sin(a)*0.38,0.302),(0.48,0.035,0.01),VOID,rot=(0,0,a+0.35),bevel=0)
    sub.box((0,0,0.31),(0.3,0.06,0.03),IRON,bevel=0.005)
    merge_kit(k,sub,M)
def wat_millstone(k):
    wat_millstone_one(k,Matrix.Identity(4))
    wat_millstone_one(k,Matrix.Translation((0.95,0.35,0.64))@Matrix.Rotation(math.radians(76),4,"Y")@Matrix.Translation((0,0,-0.15)))
    k.box((1.45,0.35,0.08),(0.18,0.8,0.16),WOOD,rot=(0,0,0.05),bevel=0.02)

# ---------------------------------------------------------------- FISHING PROPS
def wat_fish(k,M,L=0.42,mi=STEEL,belly=PAPER):
    """low-poly fish along local +X (head), flattened in Y, back toward +Z (core kit_fish); mi BREAD = smoked"""
    return kit_fish(k,M,L,cell="fish_smoked" if mi==BREAD else "fish")

def wat_net_rack(k):
    rnd=random.Random(2)
    for x in(-1.6,1.6):
        wat_rod(k,(x,0,-0.3),(x+rnd.uniform(-0.05,0.05),0,2.35),0.075,0.065,8,WOOD,caps="top")
        for s in(-1,1): wat_seg(k,(x,0,2.15),(x,s*0.18,2.5),0.05,0.05,WOOD,bevel=0.01)
    wat_rod(k,(-1.85,0,2.33),(1.85,0.02,2.35),0.05,0.05,8,BARK_BIRCH,caps="end")
    nx,nz=12,6; W=3.0; H=1.8
    def P(i,j):
        x=-W/2+W*i/nx; t=j/nz
        sag=0.06*math.sin(math.pi*((x+W/2)/0.75%1.0))
        z=2.28-sag-t*H*(1+0.08*math.sin(i*1.3))+0.12*t*t*math.sin(math.pi*i/nx)*1.5
        y=0.12*math.sin(math.pi*i/nx)*t**1.3+0.05*math.sin(i*2.1+j)*t
        return Vector((x,y,z))
    G=[[P(i,j) for j in range(nz+1)] for i in range(nx+1)]
    for side,off in((1,0.004),(-1,-0.004)):
        V=[[k.bm.verts.new(G[i][j]+Vector((0,off,0))) for j in range(nz+1)] for i in range(nx+1)]
        for i in range(nx):
            for j in range(nz):
                q_=(V[i][j],V[i+1][j],V[i+1][j+1],V[i][j+1])
                f=k.bm.faces.new(q_ if side>0 else q_[::-1]); f.material_index=NET
                for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
    k.bm.normal_update()
    for i in range(1,nx,1):
        p=G[i][0]; _cyl(k,(p.x,p.y,p.z-0.02),0.045,0.045,0.12,6,BREAD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    for i in range(0,nx+1,2):
        p=G[i][nz]; k.box((p.x,p.y,p.z-0.02),(0.06,0.04,0.05),IRON,bevel=0.01)
    ring(k,(-1.0,0.55,0.05),0.12,0.3,0.1,HAY,n=14,axis="Z"); ring(k,(-1.0,0.55,0.13),0.1,0.27,0.08,HAY,n=14,axis="Z")
    _cyl(k,(1.1,0.5,0.25),0.25,0.28,0.5,10,WOOD)
    for i in range(3): _cyl(k,(1.1+(i-1)*0.12,0.5+0.05*i,0.54),0.06,0.06,0.14,6,BREAD,rot=Matrix.Rotation(0.4*i,4,"X"))

def wat_fish_rack(k):
    rnd=random.Random(5)
    for x in(-1.4,1.4):
        for s in(-1,1): wat_rod(k,(x,s*0.75,-0.2),(x,s*0.06,1.95),0.06,0.05,6,WOOD,caps="top")
        wat_seg(k,(x,-0.55,0.55),(x,0.55,0.55),0.07,0.07,WOOD,bevel=0.015)
    wat_rod(k,(-1.6,0,1.83),(1.6,0,1.85),0.055,0.055,8,WOOD,caps="end")
    for s in(-1,1):
        wat_rod(k,(-1.55,s*0.3,1.25),(1.55,s*0.3,1.27),0.035,0.035,6,WOOD,caps="end")
        for i in range(9):
            x=-1.15+i*0.29+rnd.uniform(-0.03,0.03); L=rnd.uniform(0.34,0.46)
            for (yy,zt) in ((s*0.3,1.23),):
                ztail=zt-0.04
                M=Matrix.Translation((x,yy,ztail-0.68*L))@Matrix.Rotation(math.pi/2,4,"Y")@Matrix.Rotation(rnd.uniform(-0.35,0.35),4,"X")
                wat_fish(k,M,L,mi=BREAD if (i+(s>0))%3 else STEEL)
                k.box((x,yy,zt-0.01),(0.012,0.012,0.06),HAY,bevel=0)
    for i in range(4):
        x=-1.0+i*0.62
        M=Matrix.Translation((x,0,1.8-0.7*0.5))@Matrix.Rotation(math.pi/2,4,"Y")@Matrix.Rotation(math.pi/2,4,"X")
        wat_fish(k,M,0.5,mi=BREAD)

def wat_lobster_pot(k,M):
    """hooped creel: plank base, 3 hoops, net cover, entrance funnel on +X"""
    sub=Kit(); L,W=0.72,0.52; r=W/2; zb=0.06
    sub.box((0,0,zb/2),(L,W,zb),PLANKS,bevel=0.01)
    for x in(-L/2+0.04,0.0,L/2-0.04):
        arc=[(x,math.cos(math.pi*i/8)*r,zb+math.sin(math.pi*i/8)*r) for i in range(9)]
        wat_tube(sub,arc,wat_rect(0.035,0.03),WOOD,up=(1,0,0))
    na=8
    for off,flip in ((0.006,False),(-0.006,True)):
        rr=r+off; V=[[sub.bm.verts.new((-L/2+L*i/3,math.cos(math.pi*j/na)*rr,zb+math.sin(math.pi*j/na)*rr)) for j in range(na+1)] for i in range(4)]
        for i in range(3):
            for j in range(na):
                q_=(V[i][j],V[i+1][j],V[i+1][j+1],V[i][j+1]); f=sub.bm.faces.new(q_[::-1] if flip else q_); f.material_index=NET
                for l in f.loops: l[sub.uv].uv=(l.vert.co.x*1.6,(math.atan2(l.vert.co.z-zb,l.vert.co.y)*r)*1.6)
        for x in(-L/2,L/2):
            pts=[(x+(off if x>0 else -off),math.cos(math.pi*j/na)*rr,zb+math.sin(math.pi*j/na)*rr) for j in range(na+1)]
            f=sub.bm.faces.new([sub.bm.verts.new(p) for p in pts]); f.material_index=NET
            sub.bm.normal_update()
            want=(1 if x>0 else -1)*(-1 if flip else 1)
            if f.normal.x*want<0: f.normal_flip()
            for l in f.loops: l[sub.uv].uv=(l.vert.co.y*1.6,l.vert.co.z*1.6)
    wat_annulus(sub,(L/2+0.01,0,zb+0.14),0.06,0.1,0.04,WOOD,n=10,axis="X")
    wat_disc(sub,(L/2+0.02,0,zb+0.14),0.06,VOID,n=8,axis=(1,0,0))
    merge_kit(k,sub,M)
def wat_basket(k,M,fish=True,seed=0):
    sub=Kit()
    wat_lathe(sub,[(0.0,0.0),(0.22,0.0),(0.27,0.28),(0.3,0.32),(0.26,0.31)],segs=12,mi=WATTLE)
    for s in(-1,1):
        arc=[(s*0.27,math.cos(math.pi*i/6)*0.1,0.32+math.sin(math.pi*i/6)*0.08) for i in range(7)]
        wat_tube(sub,arc,wat_circ(0.018,4),WOOD,up=(1,0,0))
    if fish:
        rnd=random.Random(seed)
        wat_disc(sub,(0,0,0.26),0.26,HAY,n=10)
        for i in range(4):
            wat_fish(sub,Matrix.Translation((rnd.uniform(-0.08,0.08),rnd.uniform(-0.08,0.08),0.3+0.03*i))@Matrix.Rotation(rnd.uniform(0,6.3),4,"Z")@Matrix.Rotation(math.pi/2,4,"X"),0.34)
    merge_kit(k,sub,M)
def wat_creels(k):
    wat_lobster_pot(k,Matrix.Rotation(0.1,4,"Z"))
    wat_lobster_pot(k,Matrix.Translation((0.05,0.62,0))@Matrix.Rotation(-0.08,4,"Z"))
    wat_lobster_pot(k,Matrix.Translation((0.02,0.3,0.32))@Matrix.Rotation(0.35,4,"Z"))
    wat_basket(k,Matrix.Translation((0.85,-0.2,0)),seed=1)
    wat_rope(k,[Vector((-0.62+0.22*math.cos(a),-0.35+0.22*math.sin(a),0.03+0.012*a)) for a in [i*0.8 for i in range(18)]],0.028,segs=4)
    _ico(k,(0.95,0.55,0.14),0.14,CLOTH_A,(1,1,1.1),sub=1); _cyl(k,(0.95,0.55,0.34),0.02,0.02,0.24,5,WOOD)

def wat_fish_crate(k,M,seed=0,n=6):
    sub=Kit(); rnd=random.Random(seed)
    W,D,H=0.8,0.55,0.3
    sub.box((0,0,0.03),(W,D,0.06),PLANKS,bevel=0)
    for s in(-1,1):
        sub.box((0,s*(D/2-0.025),H/2),(W,0.05,H),PLANKS,bevel=0.012)
        sub.box((s*(W/2-0.025),0,H/2),(0.05,D-0.1,H),PLANKS,bevel=0.012)
        for t in(-1,1): sub.box((s*(W/2-0.04),t*(D/2-0.04),H/2),(0.07,0.07,H+0.02),WOOD,bevel=0)
    sub.box((0,0,H-0.08),(W-0.1,D-0.1,0.04),PAPER,bevel=0)
    for i in range(n):
        x=rnd.uniform(-0.22,0.22); y=rnd.uniform(-0.14,0.14)
        Mf=Matrix.Translation((x,y,H-0.02+0.03*(i%3)))@Matrix.Rotation(rnd.uniform(0,6.28),4,"Z")@Matrix.Rotation(math.pi/2+rnd.uniform(-0.2,0.2),4,"X")
        wat_fish(sub,Mf,rnd.uniform(0.3,0.4))
    merge_kit(k,sub,M)
def wat_pile_fish(n):
    def fn(k):
        if n>=1: wat_fish_crate(k,Matrix.Rotation(0.05,4,"Z"),seed=1)
        if n>=2: wat_fish_crate(k,Matrix.Translation((0.85,0.12,0))@Matrix.Rotation(-0.12,4,"Z"),seed=2)
        if n>=3:
            wat_fish_crate(k,Matrix.Translation((0.42,0.05,0.31))@Matrix.Rotation(0.2,4,"Z"),seed=3,n=7)
            for i in range(2):
                wat_fish(k,Matrix.Translation((-0.3+i*0.45,-0.52,0.04))@Matrix.Rotation(1.2+i*0.7,4,"Z")@Matrix.Rotation(math.pi/2,4,"X"),0.4)
        if n>=2:
            k.box((0.35,0.62,0.02),(1.6,0.3,0.04),PLANKS,bevel=0.005)
    return fn

# ---------------------------------------------------------------- WASHING / WATER SUPPLY
def wat_lavoir_basin(k):
    """5.4 x 2.0 ashlar basin, water at 0.3, 4 washing slabs at 20 deg (Work sockets on the long sides)"""
    L,W,h=5.4,2.0,0.45; t=0.3
    for s in(-1,1):
        k.box((0,s*(W/2-t/2),(h-0.35)/2),(L,t,h+0.35),ASHLAR,bevel=0.03)
        k.box((s*(L/2-t/2),0,(h-0.35)/2),(t,W-2*t+0.01,h+0.35),ASHLAR,bevel=0.03)
    rnd=random.Random(3)
    for s in(-1,1):
        x=-L/2
        while x<L/2-0.05:
            w=min(rnd.uniform(0.7,1.0),L/2-x)
            k.box((x+w/2,s*(W/2-0.18),h+0.05),(w-0.02,0.4,0.1),STONE_BLOCK,rot=(0,rnd.uniform(-0.01,0.01),0),bevel=0.03,jitter=0.006,seed=int(x*10)+s)
            x+=w
        k.box((s*(L/2-0.18),0,h+0.05),(0.4,W-0.72,0.1),STONE_BLOCK,bevel=0.03)
    k.box((0,0,0.03),(L-0.5,W-0.5,0.06),STONE,bevel=0)
    wat_poly(k,[(-L/2+t,-W/2+t,0.3),(L/2-t,-W/2+t,0.3),(L/2-t,W/2-t,0.3),(-L/2+t,W/2-t,0.3)],WATER,uvfn=lambda p:(p.x/1.5,p.y/1.5),flip_to=(0,0,1))
    for s in(-1,1):
        for x in(-1.2,1.2):
            k.box((x+s*0.1,s*(W/2-t-0.12),0.38),(1.05,0.56,0.08),STONE_BLOCK,rot=(s*math.radians(20),0,0),bevel=0.025)
    # laundry: pile of cloth on a slab, beater, basket
    for i,(x,y) in enumerate(((-2.05,-0.84),(-1.8,-0.86),(-1.95,-0.8))):       # wet laundry heaped on the front curb
        _ico(k,(x,y,0.63+0.07*i),0.2,CLOTH_B if i!=1 else CLOTH_A,(1.3,0.9,0.4),sub=1,jit=0.02,seed=i)
    k.box((1.0,-0.64,0.52),(0.35,0.12,0.04),WOOD,rot=(math.radians(-20),0,0.3),bevel=0.01)
    wat_seg(k,(1.2,-0.6,0.52),(1.45,-0.72,0.47),0.035,0.035,WOOD,bevel=0.005)
    fs,_=wat_lathe(k,[(0.0,0.0),(0.24,0.0),(0.3,0.26),(0.33,0.3),(0.3,0.3)],center=(2.2,-1.35,0),segs=10,mi=WATTLE)
    for i,(dx,dy,mi) in enumerate(((-0.1,0.05,CLOTH_A),(0.1,-0.06,CLOTH_B),(0.02,0.1,PAPER),(0.05,-0.12,CLOTH_A))):
        _ico(k,(2.2+dx,-1.35+dy,0.29+0.03*(i%2)),0.13,mi,(1.2,0.9,0.5),sub=1,jit=0.015,seed=9+i)

def wat_wall_fountain(k):
    """wall-mounted fountain, same transform as the wall module (outer face at y -0.25)"""
    y0,y1=-0.25,-0.5
    k.box((0,(y0+y1)/2,0.6),(1.2,0.25,1.2),STONE_BLOCK,bevel=0.04,segs=2)
    arc=[(math.cos(math.pi*i/10)*0.6,1.2+math.sin(math.pi*i/10)*0.6) for i in range(11)]
    wat_poly(k,[(x,y1,z) for x,z in arc],STONE_BLOCK,flip_to=(0,-1,0))
    wat_strip(k,[(x,y1,z) for x,z in arc],[(x,y0,z) for x,z in arc],STONE_BLOCK,out=lambda c:(c.x,0,c.z-1.2))
    for i in range(7):                                                           # arch moulding
        a=math.pi*(i+0.5)/7
        k.box((math.cos(a)*0.55,y1-0.04,1.2+math.sin(a)*0.55),(0.12,0.1,0.26),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.02)
    k.box((0,y1-0.05,1.2),(1.34,0.12,0.12),STONE_BLOCK,bevel=0.03)
    # bronze mask + spout
    _ico(k,(0,y1-0.06,1.02),0.16,BRONZE,(1,0.5,1.1),sub=1)
    wat_rod(k,(0,y1-0.1,0.98),(0,y1-0.34,0.94),0.045,0.04,8,BRONZE)
    wat_disc(k,(0,y1-0.341,0.94),0.03,VOID,n=8,axis=(0,-1,0))
    for sx in(-1,1): _ico(k,(sx*0.09,y1-0.12,1.1),0.03,VOID,sub=0)
    # half basin
    c=(0,y1,0.0)
    wat_lathe(k,[(0.72,-0.2),(0.76,0.45),(0.84,0.5),(0.84,0.6),(0.66,0.6),(0.66,0.45)],center=c,segs=10,mi=STONE_BLOCK,a0=math.pi,a1=2*math.pi)
    for sx in(-1,1):
        wat_poly(k,[(sx*0.66,y1,0.45),(sx*0.66,y1,0.6),(sx*0.84,y1,0.6),(sx*0.84,y1,0.5),(sx*0.76,y1,0.45),(sx*0.72,y1,-0.2)],STONE_BLOCK,flip_to=(0,1,0))
    pts=[(math.cos(math.pi+math.pi*i/10)*0.67,y1+math.sin(math.pi+math.pi*i/10)*0.67,0.5) for i in range(11)]
    wat_poly(k,pts,WATER,uvfn=lambda p:(p.x/1.5,p.y/1.5),flip_to=(0,0,1))
    # water stream from the spout
    st=[Vector((0,y1-0.34-0.12*t,0.94-0.44*t*t)) for t in [i/6 for i in range(7)]]
    wat_tube(k,st,[(0.035,-0.015),(0.035,0.015),(-0.035,0.015),(-0.035,-0.015)],WATER,caps=False,smooth=True)
    wat_annulus(k,(0,y1-0.46,0.505),0.05,0.12,0.01,WATER,n=10,axis="Z")
    k.box((0,-0.8,0.05),(1.8,1.0,0.1),STONE_BLOCK,bevel=0.03)

def wat_hand_pump(k):
    k.box((0,0,0.07),(1.1,0.8,0.14),STONE_BLOCK,bevel=0.03,jitter=0.01,seed=2)
    k.box((0,0.15,0.84),(0.26,0.26,1.4),WOOD,bevel=0.03)
    k.box((0,0.15,1.58),(0.34,0.34,0.08),IRON,bevel=0.015)
    lathe(k,[(0.14,1.62),(0.14,1.66),(0.0,1.78)],center=(0,0.15,0),segs=6,mi=IRON)
    for z in(0.3,1.2): k.box((0,0.15,z),(0.29,0.29,0.05),IRON,bevel=0.008)
    wat_rod(k,(0,0.02,1.0),(0,-0.32,1.0),0.05,0.05,8,IRON)
    wat_rod(k,(0,-0.32,1.0),(0,-0.36,0.86),0.05,0.045,8,IRON)
    k.box((0,0.18,1.7),(0.06,0.14,0.14),IRON,bevel=0.01)
    wat_seg(k,(0,0.2,1.7),(0,0.95,2.05),0.05,0.05,IRON,bevel=0.01)
    wat_rod(k,(0,0.93,2.04),(0,1.12,2.13),0.04,0.04,6,WOOD)
    wat_seg(k,(0,0.26,1.7),(0,0.3,1.1),0.03,0.03,IRON,bevel=0)
    # trough under the spout
    k.box((0,-0.55,0.3),(0.95,0.5,0.06),WOOD,bevel=0.01)
    for s in(-1,1):
        k.box((0,-0.55+s*0.22,0.48),(0.95,0.06,0.36),WOOD,bevel=0.012)
        k.box((s*0.45,-0.55,0.48),(0.06,0.4,0.36),WOOD,bevel=0.012)
        k.box((s*0.36,-0.55,0.14),(0.1,0.52,0.28),WOOD,bevel=0.012)
    wat_poly(k,[(-0.42,-0.74,0.58),(0.42,-0.74,0.58),(0.42,-0.36,0.58),(-0.42,-0.36,0.58)],WATER,uvfn=lambda p:(p.x,p.y),flip_to=(0,0,1))
    wat_lathe(k,[(0.0,0.0),(0.17,0.0),(0.2,0.34),(0.21,0.36)],center=(0.62,0.1,0.14),segs=10,mi=WOOD)
    wat_annulus(k,(0.62,0.1,0.44),0.2,0.215,0.04,IRON,n=10,axis="Z")

# ---------------------------------------------------------------- fallback helpers (used only when the frontier agent's pieces are absent)
def wat_family_S(fn):
    """run fn with the S roof family (3 m deep: HALF 1.5, eave 0.9 out, ridge 2.27, verge 2.1); globals restored after"""
    def run(k):
        G=globals(); keep={n:G[n] for n in ("HALF","EAVE","RIDGE","GX")}
        try:
            G["HALF"]=1.5; G["EAVE"]=2.4; G["GX"]=2.1; G["RIDGE"]=roof_z(0)
            fn(k)
        finally: G.update(keep)
    return run
def wat_roofS_prof(): return [(y,roof_z(y)) for y in (0.0,0.5,1.0,1.5,1.95,EAVE)]
def wat_roofS_slab(k,x0,x1,side,end_caps=(False,False)):
    prof=wat_roofS_prof(); nx=max(2,int(round((x1-x0)/0.5))); xs=[x0+(x1-x0)*i/nx for i in range(nx+1)]
    dist=[0.0]*len(prof)
    for i in range(len(prof)-2,-1,-1): dist[i]=dist[i+1]+math.hypot(prof[i+1][0]-prof[i][0],prof[i+1][1]-prof[i][1])
    top=[];bot=[]
    for x in xs:
        rt=[];rb=[]
        for j,(ay,z) in enumerate(prof):
            a=prof[max(j-1,0)]; b=prof[min(j+1,len(prof)-1)]
            ty,tz=b[0]-a[0],b[1]-a[1]; L=math.hypot(ty,tz); ny,nz=tz/L,-ty/L
            if nz<0: ny,nz=-ny,-nz
            zz=z+roof_sag(x,ay)
            rt.append(k.bm.verts.new((x,side*ay,zz))); rb.append(k.bm.verts.new((x,side*(ay-ny*RT),zz-nz*RT)))
        top.append(rt); bot.append(rb)
    def F(vs,mi,uvs):
        if side>0: vs=vs[::-1]; uvs=uvs[::-1]
        f=k.bm.faces.new(vs); f.material_index=mi
        for l,u in zip(f.loops,uvs): l[k.uv].uv=u
    T=TILE[ROOF]; W=TILE[WOOD]
    for i in range(nx):
        for j in range(len(prof)-1):
            F([top[i][j],top[i][j+1],top[i+1][j+1],top[i+1][j]],ROOF,[(xs[i]/T,dist[j]/T),(xs[i]/T,dist[j+1]/T),(xs[i+1]/T,dist[j+1]/T),(xs[i+1]/T,dist[j]/T)])
            F([bot[i+1][j],bot[i+1][j+1],bot[i][j+1],bot[i][j]],WOOD,[(xs[i+1]/W,dist[j]/W),(xs[i+1]/W,dist[j+1]/W),(xs[i]/W,dist[j+1]/W),(xs[i]/W,dist[j]/W)])
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
def wat_gableS(k,sgn=1,vent=True):
    prof=wat_roofS_prof()
    for s in(-1,1):
        for j in range(len(prof)-1):
            (y0,z0),(y1,z1)=prof[j],prof[j+1]; L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,y1-y0)
            k.box((sgn*(GX+0.08),s*(y0+y1)/2,(z0+z1)/2-0.15),(0.18,L+0.18,0.4),WOOD,rot=(s*ang,0,0),bevel=0.045,segs=2)
    k.box((sgn*(GX+0.08),0,RIDGE+0.3),(0.18,0.18,0.75),WOOD,bevel=0.05,segs=2)
    k.box((sgn*(GX+0.08),0,RIDGE+0.72),(0.26,0.26,0.26),WOOD,rot=(0,0,math.pi/4),bevel=0.08,segs=2)
    XF=sgn*(1.5+0.26); XB=sgn*1.45
    def under(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.05
    YC=HALF+0.02; ys=[YC,1.25,1.0,0.75,0.5,0.25,0.0]
    outline=[(-YC,0.0),(YC,0.0)]+[(y,under(y)) for y in ys]+[(-y,under(y)) for y in ys[::-1][1:]]
    for xf,want in ((XF-sgn*0.06,sgn),(XB,-sgn)):
        wat_poly(k,[(xf,y,z) for y,z in outline],PLANKS,uvfn=lambda p:(p.y/TILE[PLANKS],p.z/TILE[PLANKS]),flip_to=(want,0,0))
    top=under(0)
    k.box((XF,0,0.1),(0.2,2*YC,0.2),WOOD,bevel=0.03)
    for y in(-1.0,-0.5,0.5,1.0):
        h=top*(1-abs(y)/YC)-0.08; k.box((XF+sgn*0.02,y,h/2),(0.06,0.1,h),WOOD,bevel=0.01)
    if vent:
        wat_poly(k,[(XF+sgn*0.01,-0.28,top*0.45),(XF+sgn*0.01,0.28,top*0.45),(XF+sgn*0.01,0.28,top*0.45+0.35),(XF+sgn*0.01,-0.28,top*0.45+0.35)],VOID,uvfn=lambda p:(0,0),flip_to=(sgn,0,0))
        for z in(top*0.45+0.09,top*0.45+0.2,top*0.45+0.31): k.box((XF+sgn*0.05,0,z),(0.04,0.62,0.05),WOOD,rot=(0,sgn*0.5,0),bevel=0.005)
def wat_roofS_gable(k):
    for s in(-1,1): wat_roofS_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
    ridge(k,-1.5,GX+0.1); wat_gableS(k,1)
def wat_roofS_single(k):
    for s in(-1,1): wat_roofS_slab(k,-GX,GX,s,end_caps=(True,True)); eave_tabs(k,-GX,GX,s)
    ridge(k,-GX-0.1,GX+0.1); wat_gableS(k,1); wat_gableS(k,-1,vent=False)
def wat_posts(k,H=3.0):
    """open-bay module (Wall_Posts stand-in): post at x -1.5 on a pad, beam at the top, 2 knee braces"""
    rock(k,(-1.5,0,0.08),(0.52,0.52,0.24),seed=31,tilt=0.02)
    k.box((-1.5,0,H/2+0.1),(0.28,0.28,H-0.2),WOOD,bevel=0.04,segs=2)
    k.box((0,0,H-0.15),(3.0,0.3,0.3),WOOD,bevel=0.04)
    for s in(-1,1): wat_seg(k,(-1.5+s*0.1,0,H-0.85),(-1.5+s*0.62,0,H-0.28),0.14,0.14,WOOD,bevel=0.02)
    k.box((-1.5,0,-0.3),(0.4,0.4,0.6),STONE_BLOCK,bevel=0.02)

# ---------------------------------------------------------------- BUILDERS
def wat_spin(o,rpm=6.0,phase=0.0,fps=24.0):
    """tag an instance for the engine (spin_axis/rpm custom props) and drive its local-X spin in Blender (frame driver, no python needed)"""
    o["spin_axis"]="local X"; o["rpm"]=float(rpm)
    try:
        fc=o.driver_add("rotation_euler",0); d=fc.driver; d.type="SCRIPTED"
        d.expression="%.4f-frame*%.6f"%(phase,rpm*2*math.pi/60.0/fps)       # 6 rpm -> half a turn per 120 frames
    except Exception as e: print("wat_spin: driver not added",e)
    return o

def wat_place(coll,piece,x,y,z,rot,origin,style=None):
    if not piece or not bpy.data.objects.get(piece): return None
    return place_v(coll,piece,x,y,z,rot,origin,style or {})

def build_watermill(coll,origin,seed=0,roof="Red"):
    """3x2 two-storey stone/timber mill; wheel strip on the +X end: water must cover house-local x 5.35..6.35, y -3.9..0.9.
       Wheel hub at (5.85,-1.5,1.3), wheel pier at (7.6,-1.5), quay faces at x 5.35."""
    r=random.Random(seed); st={"ground":"Stone","plaster":r.choice(["Cream","Ochre","White"]),"shutter":r.choice(["Red","Green","Natural"]),"roof":roof,"seed":seed}
    L=9.0
    walls=[(-3,-3,0,"W"),(0,-3,0,"D"),(3,-3,0,"W"),(3,3,180,"."),(0,3,180,"W"),(-3,3,180,"D"),
           (-L/2,-1.5,-90,"W"),(-L/2,1.5,-90,"."),(L/2,1.5,90,"W")]
    corners=[(-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)]
    _assemble(coll,origin,walls,corners,2,st,r)
    place_v(coll,"SM_VK_Wall_Stone_Axle",L/2,-1.5,0,90,origin,st)
    place_v(coll,"SM_VK_Wall_Timber_Window",L/2,-1.5,H1,90,origin,st)
    top=roof_top(2)
    for i in range(3):
        x=-L/2+1.5+3*i; pc="SM_VK_Roof_Mid" if i==1 else "SM_VK_Roof_Gable"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,st)
    place_v(coll,"SM_VK_Chimney",-3,0,top,180,origin,st)
    w=place_v(coll,"SM_VK_WaterWheel",L/2+1.35,-1.5,1.3,0,origin,{})
    wat_spin(w,6.0,phase=seed*0.37)
    place_v(coll,"SM_VK_Mill_WheelPier",L/2+1.35+1.75,-1.5,0,0,origin,{})
    for y in(-4.5,-1.5,1.5,4.5): place_v(coll,"SM_VK_Quay_Straight",L/2+0.4,y,0,90,origin,{})
    wat_place(coll,"SM_VK_Quay_Post",L/2+0.55,-5.9,0,90,origin)
    wat_place(coll,"SM_VK_Prop_Millstone",2.0,-4.6,0,-15,origin)
    wat_place(coll,"SM_VK_Prop_Sacks",-1.3,-4.1,0,10,origin); wat_place(coll,"SM_VK_Prop_Sacks",1.0,4.3,0,160,origin)
    wat_place(coll,"SM_VK_Prop_Cart",-6.8,-3.6,0,70,origin)
    wat_place(coll,"SM_VK_Prop_Crates",-6.2,2.6,0,95,origin)
    wat_place(coll,"SM_VK_Prop_BarrelStack",-2.2,4.4,0,180,origin)
    return dict(wall_top=top,footprint=(3,2),water_strip=((L/2+0.85,-3.9),(L/2+1.85,0.9)),wheel=w)

def wat_hut_set():
    if bpy.data.objects.get("SM_VK_Wall_Shed"):
        return dict(W="SM_VK_Wall_Shed",D=wat_pick("SM_VK_Wall_Shed_Door","SM_VK_Wall_Shed"),Wi=wat_pick("SM_VK_Wall_Shed_Window","SM_VK_Wall_Shed"),
                    C=wat_pick("SM_VK_Corner_Shed","SM_VK_Corner_Plaster"),top=2.6)
    return dict(W="SM_VK_Wall_Plaster",D="SM_VK_Wall_Plaster_Door",Wi="SM_VK_Wall_Plaster_Window",C="SM_VK_Corner_Plaster",top=3.0)
def wat_roofS_names():
    return wat_pick("SM_VK_RoofS_Gable","SM_VK_WatRoofS_Gable"),wat_pick("SM_VK_RoofS_Single","SM_VK_WatRoofS_Single")

def build_fisher_hut(coll,origin,seed=0):
    """2x1 shed hut on the bank (y 3..6, door at x -1.5 facing -Y), 3-module pier (2 decks + end) on x -1.5 running out
       to -Y from the bank edge at y 0, rowboat at the pier stairs, net/fish racks. Water must cover y < 0 (x -3.5..3, y -9..0)."""
    r=random.Random(seed); hs=wat_hut_set(); rg,rs=wat_roofS_names()
    st={"plaster":r.choice(["Daub","Sky","White"]),"shutter":r.choice(["Blue","Teal","Natural"]),"roof":r.choice(["Thatch","Shingle"]),"seed":seed}
    for (x,y,rot,p) in ((-1.5,3,0,hs["D"]),(1.5,3,0,hs["Wi"]),(1.5,6,180,hs["W"]),(-1.5,6,180,hs["W"]),(-3,4.5,-90,hs["Wi"]),(3,4.5,90,hs["W"])):
        place_v(coll,p,x,y,0,rot,origin,st)
    for (x,y,rot) in ((-3,3,0),(3,3,90),(3,6,180),(-3,6,-90)): place_v(coll,hs["C"],x,y,0,rot,origin,st)
    place_v(coll,rg,1.5,4.5,hs["top"],0,origin,st); place_v(coll,rg,-1.5,4.5,hs["top"],180,origin,st)
    px=-1.5                                                   # pier on the door cell's centre line (grid-aligned)
    for i,y in enumerate((-1.5,-4.5)): place_v(coll,"SM_VK_Pier_Deck",px,y,0,-90,origin,{})
    place_v(coll,"SM_VK_Pier_End",px,-7.5,0,-90,origin,{})
    for y in(-1.5,-4.5): place_v(coll,"SM_VK_Pier_Rail",px,y,0,-90,origin,{})
    place_v(coll,"SM_VK_Pier_Stairs",px,-4.5,0,90,origin,{})
    wat_place(coll,"SM_VK_Prop_Rowboat",px+4.15,-6.2,-0.6,-96,origin,{"shutter":st["shutter"]})
    wat_place(coll,"SM_VK_Prop_Creels",px-0.5,-8.0,0.05,20,origin)
    wat_place(coll,"SM_VK_Pile_Fish_2",px+0.3,-1.2,0.05,90,origin)
    wat_place(coll,"SM_VK_Prop_NetRack",-6.0,2.2,0,15,origin)
    wat_place(coll,"SM_VK_Prop_FishRack",5.6,2.6,0,-10,origin)
    wat_place(coll,"SM_VK_Pile_Fish_1",1.4,2.2,0,-20,origin)
    wat_place(coll,"SM_VK_Prop_Crates",-4.6,6.6,0,190,origin)
    wat_place(coll,"SM_VK_Prop_BarrelStack",4.2,6.9,0,180,origin)
    return dict(wall_top=hs["top"],footprint=(2,1),pier=((px,-1.5),(px,-4.5),(px,-7.5)))

def build_smokehouse(coll,origin,seed=0):
    """1x1 stone smokehouse (door on -Y), S single roof with gable vents, Roof_Vent on the ridge if available"""
    r=random.Random(seed); rg,rs=wat_roofS_names()
    st={"stone":"Dark","roof":r.choice(["Slate","Shingle"]),"shutter":"Natural","seed":seed}
    for (x,y,rot,p) in ((0,-1.5,0,"SM_VK_Wall_Stone_Door"),(0,1.5,180,"SM_VK_Wall_Stone"),(-1.5,0,-90,"SM_VK_Wall_Stone"),(1.5,0,90,"SM_VK_Wall_Stone")):
        place_v(coll,p,x,y,0,rot,origin,st)
    for (x,y,rot) in ((-1.5,-1.5,0),(1.5,-1.5,90),(1.5,1.5,180),(-1.5,1.5,-90)): place_v(coll,"SM_VK_Corner_Stone",x,y,0,rot,origin,st)
    place_v(coll,rs,0,0,H1,0,origin,st)
    wat_place(coll,wat_pick("SM_VK_Roof_Vent",None),0,0,H1+2.27-0.15,0,origin,st)
    wat_place(coll,"SM_VK_Prop_Woodpile",-3.3,0.2,0,90,origin)
    wat_place(coll,"SM_VK_Prop_FishRack",0.6,-4.3,0,5,origin)
    wat_place(coll,"SM_VK_Pile_Fish_1",2.4,-2.6,0,30,origin)
    wat_place(coll,"SM_VK_Prop_BarrelStack",2.9,1.0,0,90,origin)
    return dict(wall_top=H1,footprint=(1,1),smoke=(0,0,H1+2.27+0.35))

def build_lavoir(coll,origin,seed=0):
    """2x1 open wash-house: posts on all sides, S gable roof at 3.0, basin centred; laundry line and pump alongside"""
    r=random.Random(seed); rg,rs=wat_roofS_names(); pp=wat_pick("SM_VK_Wall_Posts","SM_VK_WatPosts")
    st={"roof":r.choice(["Red","Slate","Shingle"]),"seed":seed}
    for (x,y,rot) in ((-1.5,-1.5,0),(1.5,-1.5,0),(1.5,1.5,180),(-1.5,1.5,180),(3,0,90),(-3,0,-90)):
        place_v(coll,pp,x,y,0,rot,origin,st)
    place_v(coll,rg,1.5,0,H1,0,origin,st); place_v(coll,rg,-1.5,0,H1,180,origin,st)
    place_v(coll,"SM_VK_Prop_LavoirBasin",0,0,0,0,origin,{})
    wat_place(coll,"SM_VK_Prop_Laundry",0.2,4.2,0,3,origin)
    wat_place(coll,"SM_VK_Prop_HandPump",4.2,-1.2,0,-90,origin)
    wat_place(coll,"SM_VK_Prop_Bench",-4.1,-0.6,0,-90,origin)
    return dict(wall_top=H1,footprint=(2,1))

def wat_riverside_dress(coll,origin,seed,BX0,BX1):
    """reeds at the bank toes, willows, bushes, grass (kit nature pieces; skipped when absent)"""
    r=random.Random(seed+99)
    toe=5.55; zt=-0.5           # on the stand-in bank slope (z -0.48 there), stems rising out of the shallows
    for x in (-52,-44,-37,-6.5,24,27.5,39,53):
        wat_place(coll,"SM_VK_Plant_Reeds",x+r.uniform(-0.8,0.8),-toe,zt,r.uniform(0,360),origin)
    for x in (-50,-41,-11,23,30,41,56):
        wat_place(coll,"SM_VK_Plant_Reeds",x+r.uniform(-0.8,0.8),toe,zt,r.uniform(0,360),origin)
    for y in (-11,-23,-36):
        wat_place(coll,"SM_VK_Plant_Reeds",BX0+0.3,y+r.uniform(-1,1),-0.5,r.uniform(0,360),origin)
        wat_place(coll,"SM_VK_Plant_Reeds",BX1-0.3,y-4+r.uniform(-1,1),-0.5,r.uniform(0,360),origin)
    for (x,y,p) in ((25.5,-12.5,"SM_VK_Tree_Willow"),(-46,11.5,"SM_VK_Tree_Willow"),(53,-12,"SM_VK_Tree_Willow"),
                    (-40,-16,"SM_VK_Tree_Oak_A"),(4.5,17,"SM_VK_Tree_Oak_B"),(26,14,"SM_VK_Tree_Birch"),
                    (7,-24,"SM_VK_Tree_Apple"),(-4,-25,"SM_VK_Tree_Oak_B"),(21,-21,"SM_VK_Tree_Birch")):
        wat_place(coll,p,x,y,0,r.uniform(0,360),origin)
    for (x,y,p) in ((-33,-10,"SM_VK_Bush_Round"),(5,-14.5,"SM_VK_Bush_Round"),(24,9.5,"SM_VK_Bush_Large"),(-31,11,"SM_VK_Bush_Berry"),
                    (-6,-17,"SM_VK_Plant_TallGrass"),(-18,-17,"SM_VK_Plant_Wildflowers"),(2.5,-12,"SM_VK_Plant_TallGrass"),
                    (40,-9,"SM_VK_Plant_Wildflowers"),(50,-20,"SM_VK_Plant_TallGrass"),(-9,10,"SM_VK_Plant_TallGrass"),
                    (38,10,"SM_VK_Plant_Wildflowers"),(-52,-9,"SM_VK_Rock_Cluster"),(49.5,-8.5,"SM_VK_Rock_Boulder_Flat")):
        wat_place(coll,p,x,y,0,r.uniform(0,360),origin)

def build_riverside_demo(coll,origin,seed=0,terrain=True,dress=True):
    """River along local X (bank edges at y -6 / +6, water -0.6): stone bridge (2 spans + cutwater pier) on x 0,
       watermill on the north bank, fisher hut + pier on the south bank, quay with a moored barge, wooden bridge upstream,
       smokehouse + lavoir, a brook (x 44..47, south) crossed by Bridge_Log and a stepping-stone ford.
       terrain=True builds the stand-in banks/water (replace with the terrain track's river tiles in the game)."""
    ox,oy,orz=origin
    def O(x,y,rot=0.0):
        c,s=math.cos(orz),math.sin(orz); return (ox+x*c-y*s,oy+x*s+y*c,orz+math.radians(rot))
    BX0,BX1=44.0,47.0   # brook
    if terrain:
        q=6.9   # land steps back behind the quay runs
        env=wat_env(coll,"WS_water_DemoTerrain_%d_%d"%(int(ox),int(oy)),
            land=[(-60,-27,6.0,45),(-27,-15,q,45),(-15,60,6.0,45),(-60,BX0,-45,-6.0),(BX1,60,-45,-6.0)],
            water=[(-60,60,-6.0,q),(BX0,BX1,-45,-6.0)],
            banks=[(-60,-27,6.0,-1.4),(-15,9,6.0,-1.4),(21,60,6.0,-1.4),(-60,BX0,-6.0,1.4),(BX1,60,-6.0,1.4),
                   ("x",-45,-6.0,BX0,1.0),("x",-45,-6.0,BX1,-1.0)])
        env.location=(ox,oy,0); env.rotation_euler=(0,0,orz)
    # brook crossings: squared-log footbridge + stepping-stone ford
    place_v(coll,"SM_VK_Bridge_Log",(BX0+BX1)/2,-17.0,0,0,origin,{})
    wat_place(coll,"SM_VK_Rock_StepStones",(BX0+BX1)/2,-29.0,-0.48,57,origin)      # diagonal ford, stones ~0.25 above the water
    if dress: wat_riverside_dress(coll,origin,seed,BX0,BX1)
    # stone bridge: road along local Y (rot 90), spans at y -3 / +3, pier on the seam
    for y in(-3.0,3.0): place_v(coll,"SM_VK_Bridge_Stone_Span",0,y,0,90,origin,{})
    place_v(coll,"SM_VK_Bridge_Stone_Pier",0,0,0,90,origin,{})
    place_v(coll,"SM_VK_Bridge_Stone_Ramp",0,7.5,0,90,origin,{}); place_v(coll,"SM_VK_Bridge_Stone_Ramp",0,-7.5,0,-90,origin,{})
    for s in(-1,1):
        for x in(-3.3,3.3): wat_place(coll,"SM_VK_Prop_LampPost",x,s*8.4,0,90 if x<0 else -90,origin)
    # watermill on the north bank, grid-aligned (house x 12..18, end wall on the bank line y 6), wheel end facing the river
    # (house +X -> world -Y); its own quays stand 0.85 out in the river so the wheel strip is water
    build_watermill(coll,O(15.0,6.0+4.5,-90),seed=seed+1)
    # quay + moored barge west of the bridge (north bank)
    for i,x in enumerate((-25.5,-22.5,-19.5,-16.5)):
        place_v(coll,"SM_VK_Quay_Stair" if i==2 else "SM_VK_Quay_Straight",x,6.45,0,0,origin,{})
    for x in(-27.0,-15.0): place_v(coll,"SM_VK_Quay_Post",x,6.75,0,0,origin,{})
    place_v(coll,"SM_VK_Prop_Barge",-22.5,4.25,-0.6,3,origin,{"shutter":"Red"})
    wat_place(coll,"SM_VK_Prop_Crates",-25.0,8.4,0,10,origin); wat_place(coll,"SM_VK_Prop_Sacks",-21.0,8.1,0,0,origin)
    wat_place(coll,"SM_VK_Prop_BarrelStack",-17.4,8.5,0,-5,origin)
    # fisher hut on the south bank (its water side -Y -> world +Y)
    build_fisher_hut(coll,O(-12.0,-6.0,180),seed=seed+2)
    # smokehouse + lavoir
    build_smokehouse(coll,O(-24.0,-12.0,180),seed=seed+3)
    build_lavoir(coll,O(13.5,-12.0,180),seed=seed+4)
    # wooden bridge upstream + a spare rowboat
    zf=[("SM_VK_Bridge_Wood_End",-7.5,90),("SM_VK_Bridge_Wood_Mid",-4.5,90),("SM_VK_Bridge_Wood_Mid",-1.5,90),("SM_VK_Bridge_Wood_Mid",1.5,90),("SM_VK_Bridge_Wood_Mid",4.5,90),("SM_VK_Bridge_Wood_End",7.5,-90)]
    for (p,y,rot) in zf: place_v(coll,p,34.0,y,0,rot,origin,{})
    for y in(-3.0,0.0,3.0,-6.0,6.0): place_v(coll,"SM_VK_Bridge_Wood_Bent",34.0,y,0,90,origin,{})
    place_v(coll,"SM_VK_Prop_Rowboat",24.0,-3.5,-0.6,172,origin,{"shutter":"Green"})

# ---------------------------------------------------------------- stand-in terrain for renders (assembly only)
def wat_env_mesh(coll,name,quads,mats):
    """quads: list of (pts4, mat_index_into_mats, uv_scale)"""
    me=bpy.data.meshes.get(name)
    if me is None: me=bpy.data.meshes.new(name)
    else: me.clear_geometry()
    me.materials.clear()
    for m in mats: me.materials.append(m)
    bm=bmesh.new(); uvl=bm.loops.layers.uv.new("UVMap"); cl=bm.loops.layers.color.new("Col")   # kit shaders multiply by Col
    for pts,mi,s in quads:
        f=bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index=mi
        bm.normal_update()
        n=f.normal
        for l in f.loops:
            p=l.vert.co
            l[uvl].uv=(p.x/s,p.y/s) if abs(n.z)>0.7 else ((p.x+p.y)/s,p.z/s)
            g_=max(0.55,min(1.0,1.0+0.3*p.z)); l[cl]=(g_,g_,g_,1.0)
    bm.to_mesh(me); bm.free()
    o=bpy.data.objects.get(name)
    if o is None: o=bpy.data.objects.new(name,me); coll.objects.link(o)
    return o

def wat_box_quads(x0,x1,y0,y1,z0,z1,mt,ms,s=3.0,sides=True):
    q=[([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],mt,s*2)]
    if sides:
        q+=[([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],ms,s),([(x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1)],ms,s),
            ([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],ms,s),([(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)],ms,s)]
    return q

def wat_env(coll,name,land,water,bed=None,banks=()):
    """land: list of (x0,x1,y0,y1) at z 0; water: list of rects at -0.6; bed: rects at -1.5;
       banks: (x0,x1,y_edge,dy) sloped soil strips from the bank edge (z 0) down to the bed at y_edge+dy"""
    gm=bpy.data.objects.get("VK_Ground")
    grass=gm.data.materials[0] if gm and gm.data.materials else bpy.data.materials["M_VK_Soil"]
    wm=bpy.data.materials.get("M_VKT_Water") or bpy.data.materials["M_VK_Water"]     # terrain track's river water when present
    mats=[grass,bpy.data.materials["M_VK_Soil"],wm,bpy.data.materials["M_VK_RockMossy"]]
    q=[]
    for (x0,x1,y0,y1) in land: q+=wat_box_quads(x0,x1,y0,y1,WAT_BED-0.1,0.0,0,3,s=2.0)
    for b in banks:
        if len(b)==4:                      # edge at constant y
            x0,x1,ye,dy=b; pts=[(x0,ye,0.0),(x1,ye,0.0),(x1,ye+dy,WAT_BED),(x0,ye+dy,WAT_BED)]
        else:                              # ("x", y0, y1, x_edge, dx): edge at constant x
            _,y0,y1,xe,dx=b; pts=[(xe,y0,0.0),(xe,y1,0.0),(xe+dx,y1,WAT_BED),(xe+dx,y0,WAT_BED)]
        P=[Vector(p) for p in pts]
        if (P[1]-P[0]).cross(P[2]-P[1]).z<0: pts=pts[::-1]
        q.append((pts,1,2.0))
    for (x0,x1,y0,y1) in water: q+=[([(x0,y0,WAT_Z),(x1,y0,WAT_Z),(x1,y1,WAT_Z),(x0,y1,WAT_Z)],2,6.0)]
    for (x0,x1,y0,y1) in (bed or water): q+=[([(x0,y0,WAT_BED),(x1,y0,WAT_BED),(x1,y1,WAT_BED),(x0,y1,WAT_BED)],1,3.0)]
    return wat_env_mesh(coll,name,q,mats)

def wat_catalog_stage(coll,origin=(150.0,-150.0,0.0)):
    """render helper (not a game builder): one instance of every water piece around a 12 m channel.
       North bank y 0 (quays face -Y), south bank y -12; two props rows on the south land (y -17, -23.5)."""
    ox,oy,orz=origin; P=lambda n,x,y,z=0.0,r=0.0,st=None: wat_place(coll,"SM_VK_"+n,x,y,z,r,origin,st or {})
    env=wat_env(coll,"WS_water_CatalogTerrain",
        land=[(-12,6,0,45),(6,15,0.9,45),(15,18,0,45),(18,27,0.9,45),(27,60,0,45),(-12,60,-40,-12)],
        water=[(-12,60,-12,0.9)],banks=[(-12,6,0,-1.4),(15,18,0,-1.4),(27,60,0,-1.4),(-12,60,-12,1.4)])
    env.location=(ox,oy,0); env.rotation_euler=(0,0,orz)
    # pier out from the north bank + rowboat
    P("Pier_Deck",0,-1.5,0,-90); P("Pier_End",0,-4.5,0,-90)
    for y in(-1.5,-4.5): P("Pier_Rail",0,y,0,-90)
    P("Pier_Stairs",0,-4.5,0,90); P("Prop_Rowboat",3.4,-5.4,-0.6,-94,{"shutter":"Blue"})
    # barge quay (straight + stair + straight, posts) and the barge
    for x,n in ((7.5,"Quay_Straight"),(10.5,"Quay_Stair"),(13.5,"Quay_Straight")): P(n,x,0.45)
    for x in(6.3,14.7): P("Quay_Post",x,0.6)
    P("Prop_Barge",10.5,-1.7,-0.6,180,{"shutter":"Red"})
    # mill end: quays, stone wall with the axle bearing, wheel (spinning) + outer pier, millstone
    for x in(19.5,22.5,25.5): P("Quay_Straight",x,0.45)
    P("Wall_Stone",19.5,0.55); P("Wall_Stone_Axle",22.5,0.55); P("Wall_Stone",25.5,0.55)
    P("Corner_Stone",18,0.55,0,0); P("Corner_Stone",27,0.55,0,90)
    w=P("WaterWheel",22.5,-0.5,1.3,-90)
    if w: wat_spin(w,6.0)
    P("Mill_WheelPier",22.5,-2.25,0,-90); P("Prop_Millstone",29.0,2.2,0,-20)
    # bridges across the channel
    for y in(-3,-9): P("Bridge_Stone_Span",32,y,0,90)
    P("Bridge_Stone_Pier",32,-6,0,90); P("Bridge_Stone_Ramp",32,1.5,0,90); P("Bridge_Stone_Ramp",32,-13.5,0,-90)
    P("Bridge_Wood_End",41,1.5,0,-90); P("Bridge_Wood_End",41,-13.5,0,90)
    for y in(-1.5,-4.5,-7.5,-10.5): P("Bridge_Wood_Mid",41,y,0,90)
    for y in(0,-3,-6,-9,-12): P("Bridge_Wood_Bent",41,y,0,90)
    # row 1 (behind): the S-roof fallbacks on the open-post fallback (2x1 + 1x1 shelters), log bridge, lavoir basin
    for (x,y,r) in ((-1.5,-1.5,0),(1.5,-1.5,0),(1.5,1.5,180),(-1.5,1.5,180),(3,0,90),(-3,0,-90)): P("WatPosts",3.5+x,-18.5+y,0,r)
    P("WatRoofS_Gable",5.0,-18.5,H1,0); P("WatRoofS_Gable",2.0,-18.5,H1,180)
    for (x,y,r) in ((0,-1.5,0),(0,1.5,180),(1.5,0,90),(-1.5,0,-90)): P("WatPosts",11.5+x,-18.5+y,0,r)
    P("WatRoofS_Single",11.5,-18.5,H1,0)
    P("Bridge_Log",18.5,-18.0); P("Prop_LavoirBasin",25.5,-18.3)
    # row 2 (front): fishing and water-supply props
    for (n,x) in (("Prop_NetRack",1.5),("Prop_FishRack",7.3),("Prop_HandPump",17.5),("Prop_Creels",21.5),
                  ("Pile_Fish_1",25.0),("Pile_Fish_2",28.0),("Pile_Fish_3",31.5)):
        P(n,x,-24.5)
    P("Wall_Stone",12.5,-24.0); P("Prop_WallFountain",12.5,-24.0)

# ---------------------------------------------------------------- registry
WAT_NW=dict(wobble=False,grime=False); WAT_NG=dict(wobble=False,grime=True)
WS_SPECS=[
    ("SM_VK_Pier_Deck",wat_pier_deck,WAT_NG),
    ("SM_VK_Pier_End",wat_pier_end,WAT_NG),
    ("SM_VK_Pier_Stairs",wat_pier_stairs,WAT_NG),
    ("SM_VK_Pier_Rail",wat_pier_rail,WAT_NG),
    ("SM_VK_Prop_Rowboat",wat_rowboat,WAT_NW),
    ("SM_VK_Prop_Barge",wat_barge,WAT_NW),
    ("SM_VK_Bridge_Wood_Mid",wat_bridge_wood_mid,WAT_NG),
    ("SM_VK_Bridge_Wood_End",wat_bridge_wood_end,WAT_NG),
    ("SM_VK_Bridge_Wood_Bent",wat_bridge_wood_bent,WAT_NG),
    ("SM_VK_Bridge_Stone_Span",wat_bridge_stone_span,WAT_NG),
    ("SM_VK_Bridge_Stone_Ramp",wat_bridge_stone_ramp,WAT_NG),
    ("SM_VK_Bridge_Stone_Pier",wat_bridge_stone_pier,WAT_NG),
    ("SM_VK_Bridge_Log",wat_bridge_log,WAT_NG),
    ("SM_VK_Quay_Straight",wat_quay_straight,WAT_NG),
    ("SM_VK_Quay_Post",wat_quay_post,WAT_NW),
    ("SM_VK_Quay_Stair",wat_quay_stair,WAT_NG),
    ("SM_VK_WaterWheel",wat_waterwheel,WAT_NW),
    ("SM_VK_Wall_Stone_Axle",wat_wall_axle,{}),
    ("SM_VK_Mill_WheelPier",wat_wheel_pier,WAT_NG),
    ("SM_VK_Prop_Millstone",wat_millstone,WAT_NG),
    ("SM_VK_Prop_NetRack",wat_net_rack,WAT_NG),
    ("SM_VK_Prop_FishRack",wat_fish_rack,WAT_NG),
    ("SM_VK_Prop_Creels",wat_creels,WAT_NG),
    ("SM_VK_Pile_Fish_1",wat_pile_fish(1),WAT_NG),
    ("SM_VK_Pile_Fish_2",wat_pile_fish(2),WAT_NG),
    ("SM_VK_Pile_Fish_3",wat_pile_fish(3),WAT_NG),
    ("SM_VK_Prop_LavoirBasin",wat_lavoir_basin,WAT_NG),
    ("SM_VK_Prop_WallFountain",wat_wall_fountain,WAT_NG),
    ("SM_VK_Prop_HandPump",wat_hand_pump,WAT_NG),
    # fallback helpers for the builders (frontier's RoofS_* / Wall_Posts are used instead when they exist)
    ("SM_VK_WatRoofS_Gable",wat_family_S(wat_roofS_gable),WAT_NW),
    ("SM_VK_WatRoofS_Single",wat_family_S(wat_roofS_single),WAT_NW),
    ("SM_VK_WatPosts",wat_posts,WAT_NG),
]
EXTRA_SPECS += WS_SPECS
