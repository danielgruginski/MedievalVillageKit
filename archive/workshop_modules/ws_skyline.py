# =====================================================================================
# ws_skyline : roofline variety pack for the Village Kit            (agent prefix sky_)
#   single-bay roofs, gable chimneys, party chimney, vents, flush / stepped / hoist gables,
#   firewall, half-hips, cross gable, hatch / skylight bays, bellcote, ridge emblems,
#   banners and bunting + build_skyline_street().
#   Executed after vk_helpers in the same namespace; every roof joins Roof_Mid at x=+-1.5
#   with the same roof_z()+roof_sag() profile.
# =====================================================================================
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

SKY_TP=math.tan(PITCH)                  # rise per metre of the 52 deg pitch
SKY_CR=0.35+1.5*SKY_TP                  # ridge of the 3 m wide cross gable (2.27)

def sky_pick(name,fallback):
    return name if bpy.data.objects.get(name) else fallback

def sky_merge(dst,src,M=None,mirror_x=False):
    """append src Kit into dst; optional X mirror (with face reversal) and transform"""
    bm=src.bm
    if mirror_x:
        bmesh.ops.transform(bm,matrix=Matrix.Scale(-1,4,(1,0,0)),verts=list(bm.verts))
        bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    if M is not None:
        bmesh.ops.transform(bm,matrix=M,verts=list(bm.verts))
    merge_kit(dst,src,Matrix.Identity(4))

def sky_fade(x):
    """1 at the seam x=-1.5 -> 0 at x>=0 (sag fades out toward a hipped end)"""
    t=min(1.0,max(0.0,-x/1.5)); return 0.5-0.5*math.cos(math.pi*t)

# ------------------------------------------------------------------ generic geometry helpers
def sky_field(k,zfun,xs,ys,mat,uvfun,diag,rt,keep=None,free=None):
    """roof surface on a grid (x,y): top faces (mat), underside offset along the normal by rt,
    fascia on free boundary edges. diag(x0,x1,y0,y1)->'a' splits along (x0,y0)-(x1,y1), 'b' along the other.
    uvfun(x,y,cx,cy)->(u,v) in metres (divided by TILE[mat])."""
    T=TILE[mat]; W=TILE[WOOD]; umat=WOOD if mat==ROOF else mat
    top={}; bot={}
    def V(p):
        if p not in top:
            x,y=p; z=zfun(x,y); h=0.01
            gx=(zfun(x+h,y)-zfun(x-h,y))/(2*h); gy=(zfun(x,y+h)-zfun(x,y-h))/(2*h)
            n=Vector((-gx,-gy,1.0)).normalized()
            top[p]=k.bm.verts.new((x,y,z)); bot[p]=k.bm.verts.new(Vector((x,y,z))-n*rt)
        return p
    cnt={}
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
            if keep and not keep((x0+x1)/2,(y0+y1)/2): continue
            q=[V((x0,y0)),V((x1,y0)),V((x1,y1)),V((x0,y1))]
            tris=((0,1,2),(0,2,3)) if diag(x0,x1,y0,y1)=="a" else ((0,1,3),(1,2,3))
            for tr in tris:
                pts=[q[t] for t in tr]
                cx=sum(p[0] for p in pts)/3; cy=sum(p[1] for p in pts)/3
                f=k.bm.faces.new([top[p] for p in pts]); f.material_index=mat
                for l,p in zip(f.loops,pts):
                    u,v=uvfun(p[0],p[1],cx,cy); l[k.uv].uv=(u/T,v/T)
                fb=k.bm.faces.new([bot[p] for p in pts[::-1]]); fb.material_index=umat
                for l in fb.loops: l[k.uv].uv=(l.vert.co.x/W,l.vert.co.y/W)
            for a,b in ((q[0],q[1]),(q[1],q[2]),(q[2],q[3]),(q[3],q[0])):
                key=(min(a,b),max(a,b))
                if key in cnt: cnt[key][0]+=1
                else: cnt[key]=[1,a,b]
    for key,(c,a,b) in cnt.items():
        if c!=1 or (free and not free(a,b)): continue
        f=k.bm.faces.new((top[a],bot[a],bot[b],top[b])); f.material_index=umat
        for l in f.loops:
            co=l.vert.co; l[k.uv].uv=((co.x+co.y)/W,co.z/W)
    k.bm.normal_update()

def sky_prism(k,pts,a0,a1,mi,axis="y",bevel=0.0):
    """extrude a 2D polygon. axis 'y': pts=(x,z), extruded y a0..a1; axis 'x': pts=(y,z), extruded x a0..a1"""
    n=len(pts); before=set(k.bm.faces)
    area=sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))
    if area<0: pts=pts[::-1]
    def P(u,v,a): return (u,a,v) if axis=="y" else (a,u,v)
    f0=[k.bm.verts.new(P(u,v,a0)) for u,v in pts]; f1=[k.bm.verts.new(P(u,v,a1)) for u,v in pts]
    fs=[k.bm.faces.new(f0),k.bm.faces.new(f1[::-1])]
    for i in range(n):
        j=(i+1)%n; fs.append(k.bm.faces.new((f0[i],f1[i],f1[j],f0[j])))
    for f in fs: f.material_index=mi
    if axis=="x":
        for f in fs: f.normal_flip()
    k.bm.normal_update()
    if bevel>0:
        edges=list({e for f in fs for e in f.edges})
        bmesh.ops.bevel(k.bm,geom=edges+f0+f1,offset=bevel,segments=1,profile=0.5,affect="EDGES",clamp_overlap=True)
        k.bm.normal_update()
    fs=[f for f in k.bm.faces if f not in before]
    for f in fs: f.material_index=mi
    k.project(fs,mi)
    return fs

def sky_spline(ctrl,n_per=4,closed=False):
    """Catmull-Rom through control points"""
    P=[Vector(c) for c in ctrl]; N=len(P); out=[]
    for i in (range(N) if closed else range(N-1)):
        p0=P[(i-1)%N] if closed else P[max(i-1,0)]; p1=P[i]; p2=P[(i+1)%N]
        p3=P[(i+2)%N] if closed else P[min(i+2,N-1)]
        for s in range(n_per):
            t=s/n_per; t2=t*t; t3=t2*t
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3))
    if not closed: out.append(P[-1].copy())
    return out

def sky_tube(k,pts,r,mi,segs=8,closed=False,radii=None,plane_n=None,caps=True,strip=None):
    """round tube along a polyline. plane_n: fixed binormal for planar curves (no twist).
    strip=T -> thatch-style strip UVs (u=length/T), else box projection"""
    P=[Vector(p) for p in pts]; n=len(P)
    tans=[]
    for i in range(n):
        a,b=((P[(i-1)%n],P[(i+1)%n]) if closed else (P[max(i-1,0)],P[min(i+1,n-1)]))
        tans.append((b-a).normalized())
    frames=[]
    if plane_n is not None:
        W=Vector(plane_n).normalized()
        for t in tans: frames.append((t.cross(W).normalized(),W))
    else:
        t0=tans[0]; ref=Vector((0,0,1)) if abs(t0.z)<0.9 else Vector((1,0,0))
        u=t0.cross(ref).normalized()
        for i,t in enumerate(tans):
            if i>0:
                u=tans[i-1].rotation_difference(t)@u; u=(u-t*u.dot(t)).normalized()
            frames.append((u,t.cross(u).normalized()))
    rings=[]; info={}; acc=0.0
    for i,p in enumerate(P):
        if i>0: acc+=(P[i]-P[i-1]).length
        u,w=frames[i]; rr=radii[i] if radii else r; ring=[]
        for j in range(segs):
            a=2*math.pi*j/segs
            v=k.bm.verts.new(p+(u*math.cos(a)+w*math.sin(a))*rr); ring.append(v); info[v]=(acc,j)
        rings.append(ring)
    fs=[]
    for i in range(n if closed else n-1):
        A=rings[i]; B=rings[(i+1)%n]
        for j in range(segs):
            jj=(j+1)%segs; fs.append(k.bm.faces.new((A[j],A[jj],B[jj],B[j])))
    if caps and not closed:
        fs.append(k.bm.faces.new(rings[0][::-1])); fs.append(k.bm.faces.new(rings[-1]))
    k.bm.normal_update()
    f0=fs[0]; mid=(P[0]+P[1])/2
    if f0.normal.dot(f0.calc_center_median()-mid)<0:
        for f in fs: f.normal_flip()
    for f in fs: f.material_index=mi; f.smooth=True
    if strip:          # straws run along the tube (texture V along the length)
        for f in fs:
            js=[info.get(l.vert,(0.0,0))[1] for l in f.loops]
            for l in f.loops:
                acc_,j=info.get(l.vert,(0.0,0))
                if max(js)==segs-1 and j==0: j=segs
                l[k.uv].uv=(0.1+0.45*j/segs,0.03+0.04*(0.5+0.5*math.sin(acc_*2.2/strip*3.0)))
    else: k.project(fs,mi)
    return fs

def sky_cloth(k,P,nu,nv,mi,thick=0.012,uvs=(1.0,1.0)):
    """double-sided cloth sheet from a parametric surface P(u,v)->Vector"""
    G=[[P(i/nu,j/nv) for j in range(nv+1)] for i in range(nu+1)]
    def N(i,j):
        a=G[min(i+1,nu)][j]-G[max(i-1,0)][j]; b=G[i][min(j+1,nv)]-G[i][max(j-1,0)]
        c=a.cross(b); return c.normalized() if c.length>1e-9 else Vector((1,0,0))
    NN=[[N(i,j) for j in range(nv+1)] for i in range(nu+1)]
    F=[[k.bm.verts.new(G[i][j]+NN[i][j]*thick/2) for j in range(nv+1)] for i in range(nu+1)]
    B=[[k.bm.verts.new(G[i][j]-NN[i][j]*thick/2) for j in range(nv+1)] for i in range(nu+1)]
    fs=[]
    for i in range(nu):
        for j in range(nv):
            f=k.bm.faces.new((F[i][j],F[i+1][j],F[i+1][j+1],F[i][j+1]))
            b=k.bm.faces.new((B[i][j+1],B[i+1][j+1],B[i+1][j],B[i][j]))
            for ff,idx in ((f,((i,j),(i+1,j),(i+1,j+1),(i,j+1))),(b,((i,j+1),(i+1,j+1),(i+1,j),(i,j)))):
                ff.material_index=mi; ff.smooth=True
                for l,(a_,b_) in zip(ff.loops,idx): l[k.uv].uv=(a_/nu*uvs[0],b_/nv*uvs[1])
            fs+=[f,b]
    k.bm.normal_update()
    return fs,G,NN

def sky_frustum(k,z0,z1,b0,b1,mi):
    """box-like hull between rectangle b0=(x0,x1,y0,y1) at z0 and b1 at z1"""
    def R(b,z): return [k.bm.verts.new((b[0],b[2],z)),k.bm.verts.new((b[1],b[2],z)),k.bm.verts.new((b[1],b[3],z)),k.bm.verts.new((b[0],b[3],z))]
    A=R(b0,z0); B=R(b1,z1)
    fs=[k.bm.faces.new(A[::-1]),k.bm.faces.new(B)]
    for i in range(4):
        j=(i+1)%4; fs.append(k.bm.faces.new((A[i],A[j],B[j],B[i])))
    k.bm.normal_update(); k.project(fs,mi); return fs

def sky_pot(k,x,y,z):
    _cyl(k,(x,y,z+0.22),0.15,0.115,0.44,12,CLAY)
    _cyl(k,(x,y,z+0.47),0.145,0.145,0.07,12,CLAY)
    _cyl(k,(x,y,z+0.505),0.1,0.1,0.01,10,VOID)

def sky_barge(k,x,prof,s,h=0.46,t=0.2,segs=2):
    """bargeboards along a (ay,z) polyline on side s (as gable_end)"""
    for (y0,z0),(y1,z1) in zip(prof[:-1],prof[1:]):
        L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,y1-y0)
        k.box((x,s*(y0+y1)/2,(z0+z1)/2-0.16),(t,L+0.2,h),WOOD,rot=(s*ang,0,0),bevel=0.05 if segs>1 else 0.035,segs=segs)

def sky_finial(k,x):
    k.box((x,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,segs=2)
    k.box((x,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)

def sky_hip_roll(k,p0,p1,n=5,r0=0.19,r1=0.16):
    """tiled hip ridge from p0 to p1 made of n tapered roll segments"""
    p0=Vector(p0); p1=Vector(p1)
    for i in range(n):
        a=p0.lerp(p1,i/n); b=p0.lerp(p1,(i+1)/n); d=b-a
        q=Vector((1,0,0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        sub=Kit(); _cyl(sub,(0,0,0),r0,r1,d.length+0.05,10,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
        merge_kit(k,sub,Matrix.Translation((a+b)/2)@q)

# ------------------------------------------------------------------ timber gable wall (clip / door)
def sky_gable_wall(k,XF=1.9,rt=None,clipz=None,window=True,door=False,joists=True):
    """timber-framed plaster gable at x=XF (wall line x=1.5). clipz -> trapezoid (half-hip)."""
    rt=RT if rt is None else rt
    c=rt/math.cos(PITCH)+0.05
    def und(ay): return roof_z(ay)-c
    XB=1.45; YC=HALF+0.02
    ay0=HALF-(c-0.35)/SKY_TP
    top=und(0.0)
    if clipz is not None and clipz<top:
        ayc=HALF-(clipz+c-0.35)/SKY_TP; ztop=clipz
        outline=[(-ay0,0.0),(ay0,0.0),(ayc,clipz),(-ayc,clipz)]
    else:
        ayc=0.0; ztop=top; outline=[(-ay0,0.0),(ay0,0.0),(0.0,top)]
    for xf,flip in ((XF-0.06,False),(XB,True)):
        vs=[k.bm.verts.new((xf,y,z)) for y,z in outline]
        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=PLASTER
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[PLASTER],l.vert.co.z/TILE[PLASTER])
    k.bm.normal_update()
    k.box((XF-0.02,0,0.12),(0.2,2*YC,0.24),WOOD,bevel=0.04)
    if joists:
        for i in range(6): k.box((XF+0.1,-2.5+i*1.0,-0.12),(0.3,0.16,0.2),WOOD,bevel=0.03)
    for s in(-1,1):
        y0,z0,y1,z1=s*ay0,0.1,s*ayc,ztop
        L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,abs(y1-y0))
        k.box((XF-0.02,(y0+y1)/2,(z0+z1)/2-0.12),(0.18,L+0.1,0.2),WOOD,rot=(-s*ang,0,0),bevel=0.035)
    if clipz is not None and clipz<top:
        k.box((XF-0.02,0,ztop-0.09),(0.2,2*ayc+0.25,0.2),WOOD,bevel=0.035)
        zs=ztop-0.2
        for s in(-1,1):
            k.box((XF-0.02,s*1.6,(0.24+zs)/2),(0.16,0.16,zs-0.24),WOOD,bevel=0.03)
            k.box((XF-0.02,s*0.48,(0.24+zs)/2),(0.16,0.16,zs-0.24),WOOD,bevel=0.03)
        if window:
            w0,w1=0.33,min(0.93,zs-0.12)
            k.quad([(XF-0.04,-0.33,w0),(XF-0.04,0.33,w0),(XF-0.04,0.33,w1),(XF-0.04,-0.33,w1)],WINDOW,uvs=[(0,0),(0.66,0),(0.66,w1-w0),(0,w1-w0)])
            for zz in (w0-0.05,w1+0.05): k.box((XF+0.02,0,zz),(0.16,0.85,0.12),WOOD,bevel=0.025)
            k.box((XF+0.02,0,(w0+w1)/2),(0.06,0.05,w1-w0),WOOD,bevel=0.01)
        return ztop
    zc=top*0.45
    if door: zc=2.3
    half_c=YC*(1-zc/top)*0.98
    k.box((XF-0.02,0,zc),(0.18,2*half_c,0.2),WOOD,bevel=0.035)
    if door:
        k.box((XF-0.02,0,(zc+top)/2),(0.18,0.24,top-zc),WOOD,bevel=0.035)
    else:
        k.box((XF-0.02,0,top/2),(0.18,0.24,top),WOOD,bevel=0.035)
    for s_ in(-1,1): k.box((XF-0.02,s_*1.6,zc/2+0.1),(0.16,0.16,zc-0.1),WOOD,bevel=0.03)
    if window and not door:
        wz=zc+0.25
        k.quad([(XF-0.04,-0.35,wz),(XF-0.04,0.35,wz),(XF-0.04,0.35,wz+0.8),(XF-0.04,-0.35,wz+0.8)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,0.8),(0,0.8)])
        for yy in(-0.42,0.42): k.box((XF+0.02,yy,wz+0.4),(0.14,0.13,0.95),WOOD,bevel=0.025)
        for zz in(wz-0.05,wz+0.85): k.box((XF+0.02,0,zz),(0.16,0.95,0.13),WOOD,bevel=0.025)
        k.box((XF+0.02,0,wz+0.4),(0.06,0.05,0.8),WOOD,bevel=0.01)
    return ztop

# ================================================================== ROOFS
def sky_roof_single(k):
    """one-bay gable roof for a 1-cell house: gables at both ends (x=+-1.5 wall lines)"""
    for s in(-1,1): roof_slab(k,-GX,GX,s,end_caps=(True,True)); eave_tabs(k,-GX,GX,s,seed=3)
    ridge(k,-GX-0.1,GX+0.1)
    gable_end(k)
    g=Kit(); gable_end(g); sky_merge(k,g,mirror_x=True)

def sky_roof_thatch_single(k):
    for s in(-1,1): thatch_slab(k,-GX,GX,s,end_caps=(True,True)); thatch_eave_roll(k,-GX,GX,s,seed=1.0+s)
    thatch_ridge_cap(k,-GX-0.05,GX+0.05)
    thatch_rake_roll(k,GX,seed=2.0)
    g=Kit(); thatch_rake_roll(g,GX,seed=3.0); sky_merge(k,g,mirror_x=True)
    gable_end(k,"timber",trim=False)
    g=Kit(); gable_end(g,"timber",trim=False); sky_merge(k,g,mirror_x=True)

def sky_hip_z(x,y):
    ay=abs(y)
    return min(roof_z(ay),roof_z(max(0.0,x+1.5)))+roof_sag(x,min(ay,EAVE))*sky_fade(x)

def sky_roof_hip_plain(k):
    """hipped end (drop-in for Roof_Gable) without the finial; exact Roof_Mid profile at x=-1.5"""
    XE=1.5+(EAVE-HALF)
    xs=[round(-1.5+0.25*i,4) for i in range(18)]+[XE]
    ys=sorted(set([round(0.25*i,4) for i in range(-17,18)]+[-EAVE,EAVE]))
    def uv(x,y,cx,cy):
        if abs(cy)<cx+1.5: return (y,slope_dist(max(0.0,x+1.5)))
        return (x,slope_dist(abs(y)))
    sky_field(k,sky_hip_z,xs,ys,ROOF,uv,lambda x0,x1,y0,y1:"a" if y0>=-1e-6 else "b",RT,
              free=lambda a,b: not (abs(a[0]+1.5)<1e-6 and abs(b[0]+1.5)<1e-6))
    for s in(-1,1):
        sky_hip_roll(k,(-1.5,0,sky_hip_z(-1.5,0)+0.03),(1.5,s*3.0,sky_hip_z(1.5,s*3.0)+0.03),n=6)
        sky_hip_roll(k,(1.5,s*3.0,sky_hip_z(1.5,s*3.0)+0.03),(XE,s*EAVE,sky_hip_z(XE,s*EAVE)+0.03),n=2,r0=0.16,r1=0.14)
    _ico(k,(-1.5,0,sky_hip_z(-1.5,0)+0.12),0.24,ROOF,sub=1)
    for s in(-1,1): eave_tabs(k,-1.5,1.55,s)
    sub2=Kit(); eave_tabs(sub2,-HALF+0.02,HALF-0.02,1)
    merge_kit(k,sub2,Matrix.Translation((-1.5,0,0))@Matrix.Rotation(-math.pi/2,4,"Z"))

def sky_hh_z(x,y):
    ay=abs(y)
    return min(roof_z(ay),roof_z(max(0.0,x)))+roof_sag(x,min(ay,EAVE))*sky_fade(x)

def sky_roof_halfhip(k,thatch=False):
    """half-hip (jerkinhead) end, drop-in for Roof_Gable (x -1.5..GX)"""
    mat=THATCH if thatch else ROOF; rt=TRT if thatch else RT
    xs=[round(-1.5+0.25*i,4) for i in range(16)]+[GX]
    ys=sorted(set([round(0.25*i,4) for i in range(-17,18)]+[-EAVE,EAVE,-GX,GX]))
    def uv(x,y,cx,cy):
        if abs(cy)<cx: return (y,slope_dist(max(0.0,x)))
        return (x,slope_dist(abs(y)))
    sky_field(k,sky_hh_z,xs,ys,mat,uv,lambda x0,x1,y0,y1:"a" if y0>=-1e-6 else "b",rt,
              free=lambda a,b: not (abs(a[0]+1.5)<1e-6 and abs(b[0]+1.5)<1e-6))
    zg=roof_z(GX)
    lower=[(GX,zg),(HALF,roof_z(HALF)),(EAVE,roof_z(EAVE))]
    if not thatch:
        for s in(-1,1): eave_tabs(k,-1.5,GX,s,seed=5)
        ridge(k,-1.5,0.05)
        for s in(-1,1): sky_hip_roll(k,(0,0,sky_hh_z(0,0)+0.03),(GX,s*GX,sky_hh_z(GX,s*GX)+0.03),n=5)
        _ico(k,(0.0,0,RIDGE+0.12),0.24,ROOF,sub=1)
        for s in(-1,1): sky_barge(k,GX+0.04,[(GX-0.08,zg+0.1)]+lower[1:],s,h=0.34,t=0.1)
        # fascia board on the hip eave (perpendicular to the 52 deg hip slab)
        k.box((GX-0.087,0,zg-0.132),(0.08,2*GX+0.12,0.36),WOOD,rot=(0,PITCH,0),bevel=0.03)
        clip=roof_z(1.9)-rt/math.cos(PITCH)-0.04
    else:
        for s in(-1,1): thatch_eave_roll(k,-1.5,GX,s,seed=1.0+s)
        thatch_ridge_cap(k,-1.5,0.15)
        _ico(k,(0.12,0,RIDGE+0.08),0.3,THATCH,scale=(1.3,1.2,0.8),sub=2,jit=0.02,seed=3)
        R=TRT/2+0.05
        for s in(-1,1):
            pts=[Vector((d,s*d,sky_hh_z(d,s*d)+0.02)) for d in [GX*i/8 for i in range(9)]]
            sky_tube(k,pts,0.15,THATCH,segs=8,radii=[0.2-0.06*i/8 for i in range(9)],strip=TILE[THATCH])
            pr=[Vector((GX-0.06,s*y,roof_z(y)-TRT/2)) for y in (GX,2.75,HALF,3.45,3.9,EAVE-0.05)]
            sky_tube(k,pr,R,THATCH,segs=10,radii=[R*(1+0.1*_pnoise(p.y*1.3,2.0)) for p in pr],strip=TILE[THATCH])
            _ico(k,(GX-0.08,s*(EAVE-0.05),roof_z(EAVE)-TRT/2),R*1.05,THATCH,sub=2,jit=0.02,seed=4+s)
            _ico(k,(GX-0.02,s*GX,zg-TRT/2),R*1.1,THATCH,sub=2,jit=0.02,seed=6+s)
        pe=[Vector((GX-0.02,y,zg-TRT/2+0.02)) for y in [-GX+GX*2*i/12 for i in range(13)]]
        sky_tube(k,pe,R,THATCH,segs=10,radii=[R*(1+0.12*_pnoise(p.y,1.0)) for p in pe],strip=TILE[THATCH])
        clip=roof_z(1.9)-rt/math.cos(PITCH)-0.04
    sky_gable_wall(k,1.9,rt=rt,clipz=clip,window=True)

def sky_roof_mid_cap(k,left=True):
    """Roof_Mid with a closed slab end + thin verge board (roof ending against a taller wall)"""
    ec=(True,False) if left else (False,True)
    for s in(-1,1): roof_slab(k,-1.5,1.5,s,end_caps=ec); eave_tabs(k,-1.5,1.5,s)
    ridge(k,-1.5,1.5)
    x=-1.45 if left else 1.45; sgn=-1 if left else 1
    prof=[(y,z+roof_sag(sgn*1.5,y)) for (y,z) in roof_profile()]
    for s in(-1,1): sky_barge(k,x,prof,s,h=0.4,t=0.1,segs=1)
    _ico(k,(x,0,RIDGE+0.05+roof_sag(1.5,0)),0.24,ROOF,sub=1)

def sky_roof_mid_opening(k,kind="hatch"):
    """Roof_Mid + 1x1 m opening on the front (-Y) slope at ay 1.7: hatch (lid open 65 deg) or skylight"""
    roof_mid(k)
    ay=1.7; P=Vector((0,-ay,roof_z(ay)))
    M=Matrix.Translation(P)@Matrix.Rotation(PITCH,4,"X")      # local: x, up-slope, normal
    for s in(-1,1):
        k.box((s*0.47,0,0.05),(0.14,1.08,0.3),WOOD,bevel=0.03,xform=M)
        k.box((0,s*0.47,0.05),(1.08,0.14,0.3),WOOD,bevel=0.03,xform=M)
    k.box((0,-0.6,0.02),(1.2,0.12,0.12),ROOF,bevel=0.03,xform=M)          # little tile flashing below
    if kind=="hatch":
        k.box((0,0,-0.02),(0.82,0.82,0.1),VOID,bevel=0,xform=M)
        H=M@Matrix.Translation((0,0.47,0.2))@Matrix.Rotation(-math.radians(65),4,"X")@Matrix.Translation((0,-0.47,-0.2))
        k.box((0,0,0.24),(0.98,0.98,0.07),PLANKS,bevel=0.02,xform=H)
        for v in(-0.28,0.28): k.box((0,v,0.3),(0.9,0.1,0.05),WOOD,bevel=0.012,xform=H)
        for u in(-0.3,0.3): k.box((u,0.25,0.29),(0.06,0.5,0.03),IRON,bevel=0.008,xform=H)
        # prop stick from the curb to the lid edge
        a=M@Vector((0.32,-0.42,0.2)); b=H@Vector((0.32,-0.46,0.22)); d=b-a
        q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        sub=Kit(); sub.box((0,0,0),(0.04,0.04,d.length),WOOD,bevel=0.01)
        merge_kit(k,sub,Matrix.Translation((a+b)/2)@q)
    else:
        v=[M@Vector(p) for p in ((-0.42,-0.42,0.12),(0.42,-0.42,0.12),(0.42,0.42,0.12),(-0.42,0.42,0.12))]
        k.quad([tuple(p) for p in v],WINDOW,uvs=[(0,0),(0.84,0),(0.84,0.84),(0,0.84)])
        k.box((0,0,0.14),(0.05,0.86,0.04),WOOD,bevel=0.01,xform=M)
        k.box((0,0,0.14),(0.86,0.05,0.04),WOOD,bevel=0.01,xform=M)
        k.box((0,-0.35,0.03),(0.8,0.1,0.1),VOID,bevel=0,xform=M)

# ------------------------------------------------------------------ cross gable (wall gablet on the front slope)
def sky_cg_cross(x): return 0.35+(1.5-abs(x))*SKY_TP
def sky_cg_z(x,y):
    ay=abs(y); s=roof_sag(x,min(ay,EAVE)); m=roof_z(ay)+s
    if y<=-1.5: return max(m,sky_cg_cross(x)+s)
    return m

def sky_roof_crossgable(k):
    """replaces a Roof_Mid bay; small gable facing -Y with ridge 2.27, valleys to (0,-1.5)"""
    YF=-3.6
    xs=[round(-1.5+0.25*i,4) for i in range(13)]
    ys=[YF]+[round(0.25*i,4) for i in range(-14,18)]+[EAVE]
    def isx(cx,cy): return cy<=-1.5 and sky_cg_cross(cx)>roof_z(abs(cy))
    def uv(x,y,cx,cy):
        if isx(cx,cy): return (y,slope_dist(1.5+abs(x)))
        return (x,slope_dist(abs(y)))
    def diag(x0,x1,y0,y1):
        if -3.0-1e-6<=y0 and y1<=-1.5+1e-6: return "b" if x0>=-1e-6 else "a"
        return "a"
    def free(a,b):
        return not (abs(abs(a[0])-1.5)<1e-6 and abs(abs(b[0])-1.5)<1e-6 and a[1]>=-3.0-1e-6 and b[1]>=-3.0-1e-6)
    sky_field(k,sky_cg_z,xs,ys,ROOF,uv,diag,RT,free=free)
    ridge(k,-1.5,1.5)
    eave_tabs(k,-1.5,1.5,1)
    # cross ridge rolls along -Y
    n=5; ya,yb=-1.3,YF-0.12
    for i in range(n):
        y0=ya+(yb-ya)*i/n; y1=ya+(yb-ya)*(i+1)/n
        _cyl(k,(0,(y0+y1)/2,SKY_CR+0.04),0.21,0.175,abs(y1-y0)+0.06,10,ROOF,rot=Matrix.Rotation(math.pi/2,4,"X"))
    # bargeboards + finial on the cross gable
    yb_=YF-0.08; L=math.hypot(1.5,1.5*SKY_TP)
    for sx in(-1,1):
        k.box((sx*0.72,yb_,(0.35+SKY_CR)/2-0.16),(L+0.08,0.2,0.46),WOOD,rot=(0,sx*PITCH,0),bevel=0.05,segs=2)
    k.box((0,yb_,SKY_CR+0.3),(0.2,0.2,0.8),WOOD,bevel=0.06,segs=2)
    k.box((0,yb_,SKY_CR+0.75),(0.28,0.28,0.28),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)
    # timber-framed plaster triangle at y=-3.40
    c=RT/math.cos(PITCH)+0.05
    xb=1.5-(c-0.35)/SKY_TP; ztop=sky_cg_cross(0)-c
    for yf,flip in ((-3.34,False),(-2.95,True)):
        vs=[k.bm.verts.new((x,yf,z)) for x,z in ((-xb,0.0),(xb,0.0),(0.0,ztop))]
        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=PLASTER
        for l in f.loops: l[k.uv].uv=(l.vert.co.x/TILE[PLASTER],l.vert.co.z/TILE[PLASTER])
    k.bm.normal_update()
    k.box((0,-3.36,0.12),(3.0,0.2,0.24),WOOD,bevel=0.04)
    for x in(-1.0,0.0,1.0): k.box((x,-3.48,-0.12),(0.16,0.3,0.2),WOOD,bevel=0.03)
    Lr=math.hypot(xb,ztop); ang=math.atan2(ztop,xb)
    for sx in(-1,1): k.box((sx*xb/2,-3.36,ztop/2-0.12),(Lr+0.1,0.18,0.2),WOOD,rot=(0,sx*ang,0),bevel=0.035)
    w0,w1=0.36,0.96
    k.quad([(-0.3,-3.38,w0),(0.3,-3.38,w0),(0.3,-3.38,w1),(-0.3,-3.38,w1)],WINDOW,uvs=[(0,0),(0.6,0),(0.6,0.6),(0,0.6)])
    for xx in(-0.37,0.37): k.box((xx,-3.42,(w0+w1)/2),(0.13,0.14,w1-w0+0.14),WOOD,bevel=0.025)
    for zz in(w0-0.06,w1+0.06): k.box((0,-3.42,zz),(0.9,0.16,0.12),WOOD,bevel=0.025)
    k.box((0,-3.42,(w0+w1)/2),(0.05,0.06,w1-w0),WOOD,bevel=0.01)
    k.box((0,-3.38,(w1+0.12+ztop)/2),(0.16,0.16,ztop-w1-0.12),WOOD,bevel=0.03)
    # eave stops closing the neighbours' cut eaves (x=+-1.5, ay 3.0..4.35)
    for sx in(-1,1):
        x0,x1=(1.46,1.52) if sx>0 else (-1.52,-1.46)
        sg=roof_sag(1.5,3.0); sg2=roof_sag(1.5,EAVE)
        pts=[(-3.0,roof_z(3.0)+sg+0.02),(-EAVE,roof_z(EAVE)+sg2+0.02),(-EAVE,roof_z(EAVE)+sg2-0.36),(-3.0,roof_z(3.0)+sg-0.36)]
        sky_prism(k,pts,x0,x1,WOOD,axis="x")

# ------------------------------------------------------------------ stone parapet gables
SKY_PAR=(1.25,1.75)
SKY_SADDLE_TOP=RIDGE+0.3+0.2+0.52       # top of the flush apex stone (emblem mount height)
def sky_parapet(k,x0,x1,kind="flush",band=True):
    xc=(x0+x1)/2; w=x1-x0; ye=2.9
    if kind=="flush":
        pts=[(-ye,-0.3),(ye,-0.3),(ye,roof_z(ye)+0.3),(0.0,RIDGE+0.3),(-ye,roof_z(ye)+0.3)]
        sky_prism(k,pts,x0,x1,STONE,axis="x")
        L=math.hypot(ye,RIDGE-roof_z(ye)); ang=math.atan2(RIDGE-roof_z(ye),ye); n=6
        for s in(-1,1):
            for i in range(n):
                t=(i+0.5)/n; ym=s*ye*(1-t); zm=roof_z(abs(ym))+0.3
                k.box((xc,ym,zm+0.07),(w+0.12,L/n-0.035,0.14),ASHLAR,rot=(-s*ang,0,0),bevel=0.03,segs=1)
        k.box((xc,0,RIDGE+0.3+0.1),(w+0.2,0.62,0.4),ASHLAR,bevel=0.04,segs=2)
        _cyl(k,(xc,0,RIDGE+0.3+0.3+0.21),0.45,0.03,0.42,4,ASHLAR,rot=Matrix.Rotation(math.pi/4,4,"Z"))
    else:
        for kk in range(6):
            a0=3.0-0.5*(kk+1); a1=3.0-0.5*kk; zt=roof_z(a0)+0.3
            if kk==5:
                k.box((xc,0,(zt-0.3)/2),(w,1.0,zt+0.3),STONE,bevel=0)
                k.box((xc,0,zt+0.05),(w+0.12,1.1,0.1),ASHLAR,bevel=0.025)
            else:
                for s in(-1,1):
                    k.box((xc,s*(a0+a1)/2,(zt-0.3)/2),(w,0.5,zt+0.3),STONE,bevel=0)
                    k.box((xc,s*(a0+a1)/2+s*0.02,zt+0.05),(w+0.12,0.56,0.1),ASHLAR,bevel=0.025)
        zt=RIDGE+0.3+0.1
        k.box((xc,0,zt+0.45),(0.5,0.5,0.9),ASHLAR,bevel=0.03)
        k.box((xc,0,zt+0.93),(0.6,0.6,0.08),ASHLAR,bevel=0.02)
        _cyl(k,(xc,0,zt+0.97+0.2),0.42,0.02,0.4,4,ASHLAR,rot=Matrix.Rotation(math.pi/4,4,"Z"))
        _ico(k,(xc,0,zt+1.42),0.12,BRONZE,sub=2)
        # ox-eye window in the outer face
        zo=0.45*(RIDGE+0.3); sub=Kit()
        ring(sub,(0,0,zo),0.30,0.46,0.2,ASHLAR,n=20,axis="Y")
        vs=[sub.bm.verts.new((math.cos(2*math.pi*i/16)*0.3,-0.02,zo+math.sin(2*math.pi*i/16)*0.3)) for i in range(16)]
        f=sub.bm.faces.new(vs[::-1]); f.material_index=WINDOW
        for l in f.loops: l[sub.uv].uv=(l.vert.co.x/0.6+0.5,(l.vert.co.z-zo)/0.6+0.5)
        for a in (0.0,math.pi/2): sub.box((0,-0.03,zo),(0.62,0.03,0.04),IRON,rot=(0,a,0),bevel=0)
        sky_merge(k,sub,Matrix.Translation((x1,0,0))@Matrix.Rotation(math.pi/2,4,"Z"))
    # kneelers (skew corbels) at both eaves
    for s in(-1,1):
        pts=[(2.72,-0.35),(3.3,-0.35),(3.92,-0.2),(3.92,0.46),(3.3,0.76),(2.72,1.08)]     # underside stays inside the eave
        if s<0: pts=[(-y,z) for y,z in pts]
        sky_prism(k,pts,xc-0.36,xc+0.36,ASHLAR,axis="x",bevel=0.03)
    if band:
        k.box((xc+0.02,0,-0.02),(w+0.16,6.7,0.16),ASHLAR,bevel=0.03)

def sky_roof_gable_stone(k,kind="flush"):
    """flush (raked) or crow-stepped stone parapet gable, drop-in for Roof_Gable"""
    for s in(-1,1): roof_slab(k,-1.5,1.6,s,end_caps=(False,True)); eave_tabs(k,-1.5,1.6,s,seed=7)
    ridge(k,-1.5,1.3)
    sky_parapet(k,SKY_PAR[0],SKY_PAR[1],kind)

def sky_roof_firewall(k):
    """raised stone parapet on a unit boundary (origin on the boundary, no roof slabs)"""
    sky_parapet(k,-0.25,0.25,"flush",band=False)

# ------------------------------------------------------------------ hoist gable
def sky_roof_gable_hoist(k):
    for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s,seed=9)
    ridge(k,-1.5,GX+0.1)
    prof=roof_profile()
    for s in(-1,1): sky_barge(k,GX+0.08,prof,s)
    sky_finial(k,GX+0.08)
    XF=1.9
    sky_gable_wall(k,XF,window=False,door=True)
    # loading door
    z0,z1=0.5,2.0
    k.quad([(XF-0.04,-0.5,z0),(XF-0.04,0.5,z0),(XF-0.04,0.5,z1),(XF-0.04,-0.5,z1)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for yy in(-0.58,0.58): k.box((XF+0.02,yy,(z0+z1)/2+0.03),(0.16,0.15,z1-z0+0.2),WOOD,bevel=0.03)
    k.box((XF+0.03,0,z1+0.1),(0.2,1.4,0.18),WOOD,bevel=0.03)
    k.box((XF+0.06,0,z0-0.06),(0.3,1.3,0.12),WOOD,bevel=0.03)
    for s,a in ((1,math.radians(100)),(-1,-math.radians(100))):
        hinge=Vector((XF+0.02,s*0.5,0)); d0=Vector((0,-s,0))
        R=Matrix.Rotation(a,4,"Z"); d=(R@d0.to_4d()).to_3d()
        c=hinge+d*0.25; ang=math.atan2(d.y,d.x)
        k.box((c.x,c.y,(z0+z1)/2),(0.48,0.05,z1-z0-0.04),PLANKS,rot=(0,0,ang),bevel=0.015)
        for zz in(z0+0.25,z1-0.25): k.box((c.x-d.y*0.03,c.y+d.x*0.03,zz),(0.44,0.03,0.07),IRON,rot=(0,0,ang),bevel=0.008)
    # hood (gablet) over the hoist beam
    run=0.65; rise=0.55; Ls=math.hypot(run,rise)+0.1; a=math.atan2(rise,run)
    for s in(-1,1):
        k.box((XF+0.6,s*run/2,2.25+rise/2+0.04),(1.4,Ls,0.07),ROOF,rot=(-s*a,0,0),bevel=0.02)
    _cyl(k,(XF+0.6,0,2.84),0.07,0.07,1.45,8,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    for s in(-1,1): k.box((XF+1.3,s*run/2,2.25+rise/2),(0.06,Ls,0.12),WOOD,rot=(-s*a,0,0),bevel=0.015)
    # beam, brace, pulley, rope, sack
    k.box((XF+0.6,0,2.45),(1.6,0.2,0.2),WOOD,bevel=0.04)
    d=Vector((0.75,0,0.45)); q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    sub=Kit(); sub.box((0,0,0),(0.12,0.12,d.length),WOOD,bevel=0.02); merge_kit(k,sub,Matrix.Translation((XF+0.4,0,2.12))@q)
    px=XF+1.25
    k.box((px,0,2.3),(0.06,0.16,0.14),IRON,bevel=0.01)
    ring(k,(px,0,2.16),0.05,0.16,0.06,WOOD,n=16,axis="Y")
    _cyl(k,(px+0.14,0,(2.16-1.6)/2),0.025,0.025,2.16+1.6,6,BURLAP)
    d=Vector((XF+0.15-(px-0.14),0,1.25-2.16)); q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    sub=Kit(); _cyl(sub,(0,0,0),0.025,0.025,d.length,6,BURLAP); merge_kit(k,sub,Matrix.Translation((px-0.14+d.x/2,0,2.16+d.z/2))@q)
    k.box((px+0.14,0,-1.64),(0.08,0.05,0.1),IRON,bevel=0.01)
    _ico(k,(px+0.14,0,-1.98),0.3,BURLAP,scale=(0.85,0.7,1.05),sub=2,jit=0.02,seed=3)
    _cyl(k,(px+0.14,0,-1.72),0.08,0.12,0.12,8,BURLAP)

# ================================================================== CHIMNEYS & VENTS
def sky_chimney_gable(k,wall_top):
    """end-wall chimney, wall-local (outer -Y), origin on the ridge line at the ground"""
    zt=wall_top+RIDGE+1.0; zf=zt-0.2
    k.box((0,-0.7,0.8),(1.6,1.1,2.8),STONE,bevel=0.06,segs=2,tile=1.8)           # base z -0.6..2.2 (skirt)
    rock(k,(0,-0.75,0.1),(1.85,1.35,0.34),seed=41,tilt=0.02)
    rnd=random.Random(int(wall_top*10)); z=0.26; i=0
    while z<2.1:
        h=min(rnd.uniform(0.4,0.52),2.2-z)
        for sx in(-1,1):
            if i%2==0: rock(k,(sx*0.53,-1.12,z+h/2),(0.6,0.3,h-0.03),seed=i*7+sx+3,tilt=0.02,segs=2)
            else:      rock(k,(sx*0.66,-0.95,z+h/2),(0.34,0.62,h-0.03),seed=i*7+sx+5,tilt=0.02,segs=2)
        z+=h; i+=1
    sky_frustum(k,2.2,2.55,(-0.82,0.82,-1.28,-0.15),(-0.52,0.52,-1.08,-0.15),STONE_BLOCK)
    k.box((0,-0.6,(2.5+zf)/2),(1.0,0.9,zf-2.5),STONE,bevel=0.06,segs=2,tile=1.8)
    for j,zz in enumerate((3.4,4.9,6.3,7.9,9.6)):
        if zz>zf-1.2: break
        sx=(-1)**j*0.22
        rock(k,(sx,-1.08,zz),(0.34,0.08,0.24),seed=60+j,tilt=0.02,segs=1)
    rock(k,(0,-0.6,zf-0.85),(1.14,1.04,0.16),seed=22,tilt=0.01,segs=1)
    rock(k,(0,-0.6,zf+0.1),(1.28,1.16,0.22),seed=21,tilt=0.02)
    for dx in(-0.22,0.22): sky_pot(k,dx,-0.6,zf+0.2)

def sky_chimney_party(k):
    """ridge-straddling party-wall stack, origin at the ridge apex"""
    k.box((0,0,0.05),(1.8,1.0,2.5),STONE,bevel=0.06,segs=2,tile=1.8)            # z -1.2..1.3
    rock(k,(0,0,0.8),(1.92,1.12,0.15),seed=31,tilt=0.01,segs=1)
    rock(k,(0,0,1.4),(2.0,1.2,0.2),seed=32,tilt=0.02)
    for dx in(-0.58,0.0,0.58): sky_pot(k,dx,0,1.5)
    for sx in(-1,1): rock(k,(sx*0.55,-0.52,0.35),(0.4,0.08,0.26),seed=35+sx,tilt=0.02,segs=1)

def sky_roof_vent(k):
    """louvred ridge ventilator, origin at the ridge apex"""
    W=1.3; D=0.84
    k.box((0,0,-0.33),(W,D,0.72),PLANKS,bevel=0.03)
    k.box((0,0,0.33),(W-0.12,D-0.12,0.6),VOID,bevel=0)
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(W/2-0.06),sy*(D/2-0.06),0.33),(0.13,0.13,0.64),WOOD,bevel=0.025)
        k.box((sx*(W/2-0.04),0,0.33),(0.06,D-0.14,0.6),PLANKS,bevel=0.01)
    k.box((0,0,0.03),(W+0.08,D+0.08,0.09),WOOD,bevel=0.025)
    k.box((0,0,0.64),(W+0.06,D+0.06,0.08),WOOD,bevel=0.025)
    for sy in(-1,1):
        for i in range(4):
            k.box((0,sy*(D/2-0.03),0.14+i*0.135),(W-0.2,0.035,0.16),WOOD,rot=(sy*math.radians(40),0,0),bevel=0.008)
    a=math.radians(40); Ls=0.6
    for s in(-1,1):
        k.box((0,s*Ls/2*math.cos(a),0.95-Ls/2*math.sin(a)+0.03),(W+0.25,Ls,0.06),ROOF,rot=(-s*a,0,0),bevel=0.015)
    _cyl(k,(0,0,0.98),0.06,0.06,W+0.3,8,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    for sx in(-1,1):
        sky_prism(k,[(-0.44,0.66),(0.44,0.66),(0.0,0.94)],sx*W/2-0.03,sx*W/2+0.03,PLANKS,axis="x")
        _ico(k,(sx*(W/2+0.16),0,0.99),0.07,WOOD,sub=1)

def sky_roof_bellcote(k):
    """small ASHLAR bellcote astride the ridge, origin at the ridge apex"""
    W=1.0; D=0.6; hw=0.28; sp=1.0; top=2.0
    k.box((0,0,-0.4),(1.2,0.82,1.0),ASHLAR,bevel=0.04)                            # saddle z -0.9..0.1
    for sx in(-1,1): k.box((sx*(W/2+hw)/2,0,(0.1+top)/2),(W/2-hw,D,top-0.1),ASHLAR,bevel=0)
    k.box((0,0,(0.1+0.4)/2),(2*hw,D,0.3),ASHLAR,bevel=0)
    arch_cut_panels(k,hw,sp,top,-D/2,D/2,ASHLAR); arch_soffit(k,hw,sp,-D/2,D/2,ASHLAR)
    for s in(-1,1): k.box((0,s*(D/2+0.03),0.42),(2*hw+0.16,0.1,0.1),ASHLAR,bevel=0.02)
    k.box((0,0,top+0.06),(W+0.16,D+0.16,0.12),ASHLAR,bevel=0.03)
    k.box((0,0,sp+hw-0.02),(2*hw+0.02,0.1,0.08),WOOD,bevel=0.01)
    bell(k,(0,0,sp+hw-0.08),0.22)
    a=math.radians(45); Ls=0.62
    sky_prism(k,[(-D/2-0.05,top+0.12),(D/2+0.05,top+0.12),(0,top+0.12+D/2+0.05)],-W/2,W/2,ASHLAR,axis="x")
    for s in(-1,1):
        k.box((0,s*Ls/2*math.cos(a),top+0.12+(D/2+0.05)-Ls/2*math.sin(a)+0.05),(W+0.3,Ls,0.07),ROOF,rot=(-s*a,0,0),bevel=0.015)
    zr=top+0.12+D/2+0.12
    k.box((0,0,zr+0.3),(0.07,0.07,0.6),BRONZE,bevel=0.01)
    k.box((0,0,zr+0.42),(0.3,0.07,0.07),BRONZE,bevel=0.01)
    _ico(k,(0,0,zr+0.02),0.08,BRONZE,sub=1)

# ================================================================== RIDGE EMBLEMS
def sky_emblem_mount(k,top=1.0):
    """iron spike with a bronze collar and two scrolls; origin at the finial top"""
    k.box((0,0,top/2-0.05),(0.07,0.07,top+0.1),IRON,bevel=0.015)
    _ico(k,(0,0,0.16),0.08,BRONZE,sub=2)
    for s in(-1,1):
        pts=[]
        for i in range(14):
            t=i/13; th=math.pi+t*1.75*math.pi; r=0.13*(1-0.55*t)
            pts.append((s*(0.16+math.cos(th)*r),0,0.44+math.sin(th)*r))
        sky_tube(k,pts,0.022,IRON,segs=6,plane_n=(0,1,0))

def sky_em_anvil(k):
    sky_emblem_mount(k,1.0)
    pts=[(-0.34,0.88),(0.34,0.88),(0.34,0.97),(0.2,1.03),(0.14,1.16),(0.16,1.3),(0.28,1.36),(0.46,1.4),(0.46,1.58),
         (-0.3,1.58),(-0.68,1.53),(-0.46,1.45),(-0.3,1.38),(-0.16,1.3),(-0.14,1.16),(-0.2,1.03),(-0.34,0.97)]
    sky_prism(k,pts,-0.11,0.11,STEEL,bevel=0.02)
    k.box((0,0,1.58),(0.74,0.2,0.03),IRON,bevel=0.005)
    sub=Kit()
    sub.box((0,0,0),(0.06,0.06,0.62),WOOD,bevel=0.015)
    sub.box((0,0,0.3),(0.32,0.13,0.14),STEEL,bevel=0.03)
    sky_merge(k,sub,Matrix.Translation((0.2,0,1.78))@Matrix.Rotation(math.radians(-50),4,"Y"))

def sky_em_pretzel(k):
    sky_emblem_mount(k,0.95)
    c=[(0.32,0.12),(0.1,0.44),(0.0,0.6),(-0.12,0.72),(-0.3,0.86),(-0.47,0.76),(-0.53,0.5),(-0.45,0.22),(-0.23,0.04),(0.0,-0.01),
       (0.23,0.04),(0.45,0.22),(0.53,0.5),(0.47,0.76),(0.3,0.86),(0.12,0.72),(0.0,0.6),(-0.1,0.44),(-0.32,0.12)]
    ys=[-0.07,-0.06,-0.06,-0.03]+[0.0]*11+[0.03,0.06,0.06,-0.07]
    ctrl=[(x*1.05,y,0.88+z) for (x,z),y in zip(c,ys)]
    pts=sky_spline(ctrl,3)
    n=len(pts); radii=[0.058+0.058*math.sin(math.pi*i/(n-1))**1.5 for i in range(n)]
    sky_tube(k,pts,0.08,BREAD,segs=10,radii=radii)
    rnd=random.Random(5)
    for i in range(16):
        t=rnd.uniform(0.25,0.75); p=pts[int(t*(n-1))]; r=radii[int(t*(n-1))]
        a=rnd.uniform(0.3,2.8)
        _ico(k,(p.x+rnd.uniform(-0.03,0.03),p.y-math.sin(a)*r*0.95,p.z+math.cos(a)*r*0.95),0.022,PAPER,sub=1)

def sky_em_tankard(k):
    sky_emblem_mount(k,1.0)
    sub=Kit(); S=1.2
    _cyl(sub,(0,0,0.3*S),0.25*S,0.22*S,0.6*S,16,WOOD)
    for zz in (0.08,0.5): _cyl(sub,(0,0,zz*S),(0.25-0.05*zz)*S+0.012,(0.25-0.05*zz)*S+0.012,0.05*S,16,IRON)
    hp=[(0.21*S,0,0.5*S),(0.34*S,0,0.52*S),(0.42*S,0,0.42*S),(0.43*S,0,0.26*S),(0.36*S,0,0.15*S),(0.23*S,0,0.12*S)]
    sky_tube(sub,sky_spline(hp,3),0.045*S,WOOD,segs=8,plane_n=(0,1,0))
    rnd=random.Random(2)
    for (x,y,z,r) in ((0,0,0.62,0.17),(0.1,0.08,0.64,0.13),(-0.1,-0.06,0.63,0.14),(0.06,-0.1,0.66,0.12),(-0.08,0.1,0.61,0.12),(-0.2,-0.05,0.55,0.08),(-0.22,-0.03,0.42,0.06)):
        _ico(sub,(x*S,y*S,z*S),r*S,PAPER,scale=(1,1,0.8),sub=2,jit=0.008,seed=rnd.randrange(99))
    sky_merge(k,sub,Matrix.Translation((-0.06,0,0.92))@Matrix.Rotation(math.radians(-10),4,"Y"))

def sky_em_fish(k):
    sky_emblem_mount(k,1.15)
    _ico(k,(0,0,1.32),0.46,STEEL,scale=(1.0,0.21,0.45),sub=2)
    sky_prism(k,[(0.36,1.32),(0.72,1.6),(0.62,1.32),(0.72,1.03)],-0.035,0.035,BRONZE,bevel=0.01)
    sky_prism(k,[(-0.16,1.46),(0.18,1.45),(0.06,1.66),(-0.2,1.62)],-0.03,0.03,BRONZE,bevel=0.01)
    sky_prism(k,[(0.02,1.16),(0.2,1.18),(0.12,1.03)],-0.03,0.03,BRONZE,bevel=0.005)
    for s in(-1,1):
        _ico(k,(-0.28,s*0.07,1.37),0.065,PAPER,sub=1)
        _ico(k,(-0.29,s*0.1,1.37),0.035,VOID,sub=1)
        sky_tube(k,[(-0.16,s*0.085,1.5),(-0.12,s*0.095,1.38),(-0.16,s*0.085,1.18)],0.012,IRON,segs=5)
    k.box((-0.45,0,1.29),(0.06,0.16,0.03),VOID,bevel=0)

def sky_em_key(k):
    sky_emblem_mount(k,0.95)
    sub=Kit()
    ring(sub,(0,0,0.34),0.11,0.24,0.1,BRONZE,n=24,axis="Y")
    for a in range(4):
        sub.box((0,0,0.34),(0.05,0.08,0.24),BRONZE,rot=(0,a*math.pi/4,0),bevel=0.01)
    sub.box((0,0,-0.22),(0.1,0.1,0.72),BRONZE,bevel=0.02)
    for zz in (0.06,0.0): sub.box((0,0,zz),(0.2,0.14,0.05),BRONZE,bevel=0.012)
    sub.box((0.13,0,-0.46),(0.2,0.1,0.22),BRONZE,bevel=0.015)
    sub.box((0.19,0,-0.34),(0.08,0.1,0.06),VOID,bevel=0)
    sub.box((0.19,0,-0.52),(0.08,0.1,0.05),VOID,bevel=0)
    sky_merge(k,sub,Matrix.Translation((0,0,1.32))@Matrix.Rotation(math.radians(18),4,"Y"))

def sky_em_sheaf(k):
    sky_emblem_mount(k,0.9)
    rnd=random.Random(7); T=Vector((0,0,1.18))
    for i in range(20):
        a=(i/19-0.5)*0.75+rnd.uniform(-0.04,0.04); y=rnd.uniform(-0.09,0.09)
        d=Vector((math.sin(a),0,math.cos(a))); lo=0.42+rnd.uniform(-0.03,0.03); hi=0.5+rnd.uniform(-0.04,0.04)
        c=T+Vector((0,y,0))+d*(hi-lo)/2
        k.box(tuple(c),(0.035,0.035,lo+hi),HAY,rot=(0,a,0),bevel=0.01)
        e=T+Vector((0,y,0))+d*(hi+0.08)
        _ico(k,tuple(e),0.07,HAY,scale=(0.7,0.7,1.7),sub=1,jit=0.006,seed=i)
    _cyl(k,tuple(T),0.13,0.13,0.1,12,CLOTH_A)
    for s in(-1,1): k.box((s*0.1,-0.12,1.18),(0.16,0.04,0.1),CLOTH_A,rot=(0,s*0.5,0),bevel=0.02)

def sky_em_horseshoe(k):
    sky_emblem_mount(k,0.98)
    cz=1.34; ro,ri=0.42,0.26; a0,a1=math.radians(125),math.radians(415); n=18
    O=[];I=[]
    for i in range(n+1):
        a=a0+(a1-a0)*i/n
        O.append((math.cos(a)*ro,cz+math.sin(a)*ro)); I.append((math.cos(a)*ri,cz+math.sin(a)*ri))
    pts=O+I[::-1]
    sky_prism(k,pts,-0.06,0.06,STEEL,bevel=0.015)
    for i in (3,6,9,12,15):
        a=a0+(a1-a0)*i/n; r=(ro+ri)/2
        for s in(-1,1): k.box((math.cos(a)*r,s*0.061,cz+math.sin(a)*r),(0.05,0.01,0.05),VOID,rot=(0,-a,0),bevel=0)
    for a in (a0,a1):
        k.box((math.cos(a)*(ro+ri)/2,0,cz+math.sin(a)*(ro+ri)/2-0.02),(0.18,0.13,0.08),STEEL,rot=(0,-a,0),bevel=0.02)

def sky_em_shield(k):
    sky_emblem_mount(k,1.0)
    R=[(0.46,1.86),(0.46,1.36),(0.44,1.18),(0.38,1.02),(0.28,0.89),(0.15,0.79),(0.0,0.73)]
    pts=[(-x,z) for x,z in R[::-1]][1:]+R
    sky_prism(k,[(x*0.97,1.3+(z-1.3)*0.97) for x,z in pts],-0.05,0.05,CLOTH_A)
    sky_tube(k,[(x,0,z) for x,z in pts],0.055,BRONZE,segs=6,closed=True,plane_n=(0,1,0))
    for s in(-1,1):
        k.box((0,s*0.055,1.3),(0.14,0.02,1.0),PAPER,bevel=0.005)
        k.box((0,s*0.055,1.48),(0.86,0.02,0.14),PAPER,bevel=0.005)
    _ico(k,(0,-0.07,1.48),0.07,BRONZE,sub=1); _ico(k,(0,0.07,1.48),0.07,BRONZE,sub=1)

def sky_em_book(k):
    sky_emblem_mount(k,0.98)
    for s in(-1,1):
        sub=Kit()
        sub.box((s*0.3,0.05,0),(0.6,0.05,0.8),HIDE,bevel=0.015)
        sub.box((s*0.28,-0.03,0.0),(0.54,0.1,0.72),PAPER,bevel=0.02)
        for i in range(5):
            sub.box((s*0.28,-0.085,0.2-i*0.1),(0.36 if i!=4 else 0.24,0.01,0.025),IRON,bevel=0)
        for zz in(-0.37,0.37): sub.box((s*0.57,0.05,zz),(0.08,0.07,0.08),BRONZE,bevel=0.015)
        sky_merge(k,sub,Matrix.Translation((0,0,1.3))@Matrix.Rotation(-s*math.radians(14),4,"Z"))
    _cyl(k,(0,0.06,1.3),0.06,0.06,0.8,8,HIDE)
    k.box((0.03,-0.09,0.94),(0.06,0.012,0.44),CLOTH_A,bevel=0)

def sky_em_axe(k):
    sky_emblem_mount(k,1.0)
    for s in(-1,1):
        sub=Kit()
        sub.box((0,0,0),(0.07,0.07,1.08),WOOD,bevel=0.018)
        _ico(sub,(0,0,-0.55),0.05,WOOD,sub=1)
        head=[(-0.04,0.3),(0.1,0.3),(0.24,0.2),(0.36,0.18),(0.4,0.37),(0.37,0.58),(0.3,0.64),(0.2,0.51),(0.08,0.46),(-0.04,0.47)]
        sky_prism(sub,head,-0.045,0.045,STEEL,bevel=0.012)
        sky_prism(sub,[(0.36,0.2),(0.41,0.19),(0.45,0.38),(0.41,0.6),(0.37,0.58),(0.4,0.37)],-0.03,0.03,PAPER,bevel=0.004)
        sub.box((-0.09,0,0.385),(0.1,0.08,0.13),STEEL,bevel=0.015)
        M=Matrix.Translation((0,0,1.28))@Matrix.Rotation(s*math.radians(34),4,"Y")
        sky_merge(k,sub,M,mirror_x=(s<0))

SKY_EMBLEMS={"Anvil":sky_em_anvil,"Pretzel":sky_em_pretzel,"Tankard":sky_em_tankard,"Fish":sky_em_fish,"Key":sky_em_key,
             "Sheaf":sky_em_sheaf,"Horseshoe":sky_em_horseshoe,"Shield":sky_em_shield,"Book":sky_em_book,"Axe":sky_em_axe}

# ================================================================== BANNERS & BUNTING
def sky_banner_wall(k):
    """wall-local (outer -Y), origin at the storey top on the wall face line"""
    k.box((0,-0.26,0.0),(0.16,0.06,0.36),IRON,bevel=0.015)
    _cyl(k,(0,-0.8,0),0.035,0.035,1.1,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
    _ico(k,(0,-1.4,0),0.07,BRONZE,sub=2)
    k.box((0,-1.46,0),(0.03,0.08,0.03),BRONZE,bevel=0.005)
    a=Vector((0,-0.27,-0.62)); b=Vector((0,-0.95,-0.03)); d=b-a
    sub=Kit(); sub.box((0,0,0),(0.025,0.025,d.length),IRON,bevel=0)
    merge_kit(k,sub,Matrix.Translation((a+b)/2)@Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4())
    W=0.9; H=2.2; y0=-0.34
    def P(u,v):
        hl=H-0.3*(1-abs(2*u-1))
        z=-0.1-v*hl; y=y0-u*W
        x=0.045*math.sin(2*math.pi*(v*hl/1.2)+u*1.8)*min(1.0,v*4)+0.02*math.sin(math.pi*u)
        return Vector((x,y,z))
    sky_cloth(k,P,6,11,CLOTH_A,uvs=(0.9,2.2))
    _cyl(k,(0,y0-W/2,-0.04),0.055,0.055,W+0.05,10,CLOTH_A,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for v0,v1 in ((0.07,0.1),(0.88,0.91)):
        sky_cloth(k,lambda u,v,v0=v0,v1=v1: P(u,v0+(v1-v0)*v),6,1,YELLOW,thick=0.02)
    for s in(-1,1):                                   # PAPER disc appliqué on both faces
        vs=[]
        for i in range(16):
            a=2*math.pi*i/16; p=P(0.5+math.cos(a)*0.22/W,0.34+math.sin(a)*0.22/2.05)
            vs.append(k.bm.verts.new((p.x+s*0.013,p.y,p.z)))
        f=k.bm.faces.new(vs if s>0 else vs[::-1]); f.material_index=PAPER
    k.bm.normal_update()

def sky_banner_pole(k):
    k.box((0,0,-0.1),(0.56,0.56,1.0),STONE_BLOCK,bevel=0.05,segs=2)
    rock(k,(0,0,0.05),(0.86,0.86,0.16),seed=5,tilt=0.02)
    _cyl(k,(0,0,3.35),0.07,0.045,6.0,10,WOOD)
    _ico(k,(0,0,6.43),0.11,BRONZE,sub=2)
    for zz in (6.2,5.2): _cyl(k,(0,0,zz),0.075,0.075,0.05,10,IRON)
    def P(u,v):
        x=0.07+u*1.6; z=6.2-v*1.0-0.12*u*u
        y=0.1*math.sin(2*math.pi*(u*1.1-0.1))*u+0.03*math.sin(math.pi*v)*u
        return Vector((x,y,z))
    sky_cloth(k,P,8,4,CLOTH_A,uvs=(1.6,1.0))
    for v0,v1 in ((0.12,0.2),(0.8,0.88)):
        sky_cloth(k,lambda u,v,v0=v0,v1=v1: P(u,v0+(v1-v0)*v),8,1,YELLOW,thick=0.02)

def sky_banner_roof(k):
    """ridge pennant, origin at the ridge apex"""
    k.box((0,0,0.1),(0.26,0.5,0.14),IRON,bevel=0.02)
    for s in(-1,1):
        k.box((0,s*0.36,-0.38),(0.2,0.5,0.05),IRON,rot=(-s*PITCH,0,0),bevel=0.01)
    _cyl(k,(0,0,1.35),0.05,0.035,3.0,8,WOOD)
    _ico(k,(0,0,2.93),0.08,BRONZE,sub=2)
    def P(u,v):
        hh=0.34*(1-u)+0.03
        x=0.05+u*1.8; z=2.5-0.15*u*u+(0.5-v)*2*hh
        y=0.12*math.sin(2*math.pi*(u*1.2))*u
        return Vector((x,y,z))
    sky_cloth(k,P,10,2,CLOTH_A,uvs=(1.8,0.7))
    sky_cloth(k,lambda u,v: P(u*0.25,0.45+0.1*v)+Vector((0,0,0)),3,1,YELLOW,thick=0.02)

def sky_bunting(k,L=6.0,sag=0.5):
    """string of pennants between (-L/2,0,0) and (L/2,0,0)"""
    def C(x): t=(x+L/2)/L; return -sag*4*t*(1-t)
    pts=[(-L/2+L*i/24,0,C(-L/2+L*i/24)) for i in range(25)]
    sky_tube(k,pts,0.013,IRON,segs=4,caps=False)
    mats=[CLOTH_A,CLOTH_B,YELLOW,LEAF]; rnd=random.Random(int(L*10))
    x=-L/2+0.3; i=0
    while x<L/2-0.3:
        z=C(x); ph=rnd.uniform(-0.3,0.3); tip=Vector((x+rnd.uniform(-0.03,0.03),0.35*math.sin(ph),z-0.35*math.cos(ph)))
        a=Vector((x-0.15,0,C(x-0.15))); b=Vector((x+0.15,0,C(x+0.15)))
        for s in(-1,1):
            o=Vector((0,s*0.004,0))
            vs=[k.bm.verts.new(p+o) for p in (a,b,tip)]
            f=k.bm.faces.new(vs if s>0 else vs[::-1]); f.material_index=mats[i%4]; f.smooth=True
            for l,uv in zip(f.loops,((0,0),(0.3,0),(0.15,0.35))): l[k.uv].uv=uv
        x+=0.35; i+=1
    for s in(-1,1): k.box((s*L/2,0,0),(0.12,0.05,0.05),IRON,bevel=0.01)
    k.bm.normal_update()

# ================================================================== STREET BUILDER
def sky_compose(origin,cx,cy,rot_deg=0.0):
    """origin of a sub-building at local (cx,cy,rot_deg) inside a builder origin (ox,oy,rz)"""
    ox,oy,orz=origin; c,s=math.cos(orz),math.sin(orz)
    return (ox+cx*c-cy*s,oy+cx*s+cy*c,orz+math.radians(rot_deg))

def sky_unit(coll,O,n,stories,style,r,front=None,back=None,ends=(True,True),end_levels=(None,None),
             roofs=None,end_kinds=("W","W")):
    """one house / terrace unit centred at O (front -Y, n cells long).
    ends[i]=False -> no end wall on that side (terrace boundary); end_levels[i]=list of upper levels
    that still get an end wall + corners (taller unit next to a lower one).
    roofs: list of (piece,rot) per bay placed at the wall top. Returns the wall top z."""
    L=n*CELL
    front=front or "".join(r.choice("WW.") for _ in range(n))
    back=back or "".join(r.choice("W..") for _ in range(n))
    walls=[(-L/2+1.5+3*i,-3,0,front[i]) for i in range(n)]+[(-L/2+1.5+3*i,3,180,back[::-1][i]) for i in range(n)]
    corners=[]
    if ends[0]:
        walls+=[(-L/2,-1.5,-90,end_kinds[0]),(-L/2,1.5,-90,".")]; corners+=[(-L/2,-3,0),(-L/2,3,-90)]
    if ends[1]:
        walls+=[(L/2,1.5,90,end_kinds[1]),(L/2,-1.5,90,".")]; corners+=[(L/2,-3,90),(L/2,3,180)]
    _assemble(coll,O,walls,corners,stories,style,r)
    for side,lv in enumerate(end_levels):
        if not lv or ends[side]: continue
        x=-L/2 if side==0 else L/2; rw=-90 if side==0 else 90
        for l in lv:
            z=H1+H2*(l-1)
            for yy in (-1.5,1.5):
                place_v(coll,_upper(r,"W" if (yy<0 and r.random()<0.5) else "."),x,yy if side==0 else -yy,z,rw,O,style)
            for (cy,cr) in (((-3,0),(3,-90)) if side==0 else ((-3,90),(3,180))):
                place_v(coll,"SM_VK_Corner_Timber",x,cy,z,cr,O,style)
    top=roof_top(stories)
    for i,(pc,rot) in enumerate(roofs or []):
        if pc: place_v(coll,pc,-L/2+1.5+3*i,0,top,rot,O,style)
    return top

def sky_road(coll,origin,x0,x1,y,w=3.2):
    """dirt street strip (own mesh, reuses the kit's MC_WK_Dirt material)"""
    nm="WS_skyline_Road"; old=bpy.data.meshes.get(nm)
    if old is not None and old.users==0: bpy.data.meshes.remove(old)
    pts=[]
    for i in range(9):
        x=x0+(x1-x0)*i/8; yy=y+0.35*math.sin(i*1.3)
        c,s=math.cos(origin[2]),math.sin(origin[2])
        pts.append((origin[0]+x*c-yy*s,origin[1]+x*s+yy*c))
    return road_strip(coll,nm,pts,w=w)

def build_skyline_street(coll,origin,seed=0):
    """A street of 8 varied houses: north row (front -Y onto the street) = 1-cell cottage + a 4-unit terrace
    + thatched house; south row (front +Y) = merchant house + smithy + a small market corner.
    Built from existing kit walls + the skyline roofs / chimneys / emblems / banners / bunting.
    Local frame: north wall line y=-3, south wall line y=-12, street centre y=-7.5; houses span x 0..39,
    road x -6..42; footprint x -6..42, y -18..3.5 (16 x 7 cells)."""
    r=random.Random(seed*7919+11)
    pl=["Cream","White","Ochre","Rose","Sage","Sky","Daub"]; r.shuffle(pl)
    sh=["Teal","Red","Green","Blue","Natural"]; r.shuffle(sh)
    def S(i,ground,roof,**kw):
        d={"ground":ground,"plaster":pl[i%len(pl)],"shutter":sh[i%len(sh)],"roof":roof,"seed":seed*100+i}; d.update(kw); return d
    P=lambda n_,fb: sky_pick(n_,fb)
    def U(cx,cy,rot=0.0): return sky_compose(origin,cx,cy,rot)
    def em(O,x,top,kind): place_v(coll,"SM_VK_Emblem_Ridge_"+kind,x,0,top+RIDGE+0.9,0,O,{})
    # ---------------- north row (front -Y)
    # N1: one-cell cottage, Roof_Single, gable chimney on the west end, sheaf emblem
    st=S(0,"Plaster","Shingle",plaster="Daub"); O=U(1.5,0)
    top=sky_unit(coll,O,1,1,st,r,front="D",back=".",end_kinds=(".","W"),roofs=[("SM_VK_Roof_Single",0)])
    place_v(coll,"SM_VK_Chimney_Gable_H30",-1.5,0,0,-90,O,st)
    em(O,1.5+1.03,top,"Sheaf")
    # terrace T1..T4 (x 6..27): stepped street end | party chimney | firewall | cap vs taller flush | half-hip
    st1=S(1,"Stone","Slate",stone="Warm"); O1=U(9,0)
    top=sky_unit(coll,O1,2,2,st1,r,front="DW",ends=(True,False),
                 roofs=[("SM_VK_Roof_Gable_Stepped",180),("SM_VK_Roof_Mid_Skylight",0)])
    place_v(coll,"SM_VK_Banner_Wall",-3.2,0,H1+H2,-90,O1,dict(cloth="Blue"))              # on the street-end gable wall
    st2=S(2,"Plaster","Slate"); O2=U(13.5,0)
    sky_unit(coll,O2,1,2,st2,r,front="D",ends=(False,False),roofs=[("SM_VK_Roof_Mid_Hatch",0)])
    place_v(coll,"SM_VK_Chimney_Party",-1.5,0,top+RIDGE,0,O2,st2)                      # T1|T2 (same roof)
    st3=S(3,"Stone","Red"); O3=U(18,0)
    sky_unit(coll,O3,2,2,st3,r,front="WD",ends=(False,False),roofs=[("SM_VK_Roof_Mid",0),("SM_VK_Roof_Mid_CapR",0)])
    place_v(coll,"SM_VK_Roof_Firewall",-3,0,top,0,O3,st3)                               # T2|T3 (roofs differ)
    place_v(coll,"SM_VK_Banner_Roof",-1.5,0,top+RIDGE+0.08,0,O3,dict(cloth="Yellow"))
    st4=S(4,"Stone","Blue",plaster="White"); O4=U(24,0)
    top4=sky_unit(coll,O4,2,3,st4,r,front="DW",ends=(False,True),end_levels=([2],None),
                  roofs=[("SM_VK_Roof_Gable_Flush",180),("SM_VK_Roof_HalfHip",0)])
    place_v(coll,"SM_VK_Roof_Bellcote",0,0,top4+RIDGE,0,O4,st4)
    place_v(coll,"SM_VK_Banner_Wall",0,-3.2,H1+2*H2-1.0,0,O4,dict(cloth="Red"))            # below the eave
    # N5: thatched long house, half-hips both ends, tall gable chimney
    st5=S(5,"Plaster","Thatch"); O5=U(34.5,0)
    top=sky_unit(coll,O5,3,2,st5,r,front="WDW",end_kinds=("W","."),
                 roofs=[("SM_VK_RoofThatch_HalfHip",180),("SM_VK_RoofThatch_Mid",0),("SM_VK_RoofThatch_HalfHip",0)])
    place_v(coll,"SM_VK_Chimney_Gable_H58",4.5,0,0,90,O5,st5)
    # ---------------- south row (front +Y, onto the street)
    # S1: merchant house: hip | skylight | cross gable | hoist gable + key emblem
    st6=S(6,"Stone","Red",plaster="Cream"); O6=U(12,-15,180)
    top=sky_unit(coll,O6,4,2,st6,r,front="WDWW",end_kinds=(".","W"),
                 roofs=[("SM_VK_Roof_Hip_Plain",180),("SM_VK_Roof_Mid",0),("SM_VK_Roof_CrossGable",0),("SM_VK_Roof_Gable_Hoist",0)])
    place_v(coll,"SM_VK_Chimney_Gable_H58",-6,0,0,-90,O6,st6)
    em(O6,6+1.03,top,"Key")
    # S2: smithy, single storey, slate, vent on the ridge, gable chimney, anvil + horseshoe emblems
    st7=S(7,"Stone","Slate",stone="Dark"); O7=U(24,-15,180)
    top=sky_unit(coll,O7,2,1,st7,r,front="DW",end_kinds=(".","W"),
                 roofs=[("SM_VK_Roof_Gable",180),("SM_VK_Roof_Gable",0)])
    place_v(coll,"SM_VK_Roof_Vent",1.5,0,top+RIDGE-0.15,0,O7,st7)
    place_v(coll,"SM_VK_Chimney_Gable_H30",-3,0,0,-90,O7,st7)
    em(O7,3+1.03,top,"Anvil")
    place_v(coll,"SM_VK_Prop_Anvil",-1.2,-4.2,0,0,O7,{})
    # small market square opposite the thatched house
    place_v(coll,"SM_VK_MarketStall",31.5,-14.2,0,180,origin,{})
    place_v(coll,"SM_VK_Prop_Well",37.0,-15.0,0,r.choice((0,90)),origin,{})
    place_v(coll,"SM_VK_Prop_BarrelStack",31.2,-17.0,0,175,origin,{})            # behind the stall
    # ---------------- street dressing
    sky_road(coll,origin,-6,42,-7.5,w=3.0)
    for x in (9.0,16.5):                                   # bunting eave to eave across the street
        place_v(coll,"SM_VK_Prop_Bunting_6",x,-7.5,H1+H2+roof_z(EAVE)-0.12,90,origin,{})
    for y in (-3.0,-12.0):                                 # street gate: two banner poles 9 m apart + bunting
        place_v(coll,"SM_VK_Banner_Pole",-3.0,y,0,0,origin,dict(cloth=("Blue" if y>-7 else "Red")))
    place_v(coll,"SM_VK_Prop_Bunting_9",-3.0,-7.5,4.9,90,origin,{})
    for x in (4.5,28.5):
        place_v(coll,"SM_VK_Prop_LampPost",x,-4.3,0,0,origin,{})

# ================================================================== SPECS
SKY_NW=dict(wobble=False,grime=False); SKY_NG=dict(wobble=False,grime=True)
WS_SPECS=[
 ("SM_VK_Roof_Single",sky_roof_single,SKY_NW),
 ("SM_VK_RoofThatch_Single",sky_roof_thatch_single,SKY_NW),
 ("SM_VK_Roof_Hip_Plain",sky_roof_hip_plain,SKY_NW),
 ("SM_VK_Chimney_Gable_H30",lambda k: sky_chimney_gable(k,3.0),SKY_NG),
 ("SM_VK_Chimney_Gable_H58",lambda k: sky_chimney_gable(k,5.8),SKY_NG),
 ("SM_VK_Chimney_Gable_H24",lambda k: sky_chimney_gable(k,2.4),SKY_NG),
 ("SM_VK_Chimney_Party",sky_chimney_party,SKY_NW),
 ("SM_VK_Roof_Vent",sky_roof_vent,SKY_NW),
 ("SM_VK_Roof_Gable_Flush",lambda k: sky_roof_gable_stone(k,"flush"),SKY_NW),
 ("SM_VK_Roof_Firewall",sky_roof_firewall,SKY_NW),
 ("SM_VK_Roof_Gable_Stepped",lambda k: sky_roof_gable_stone(k,"stepped"),SKY_NW),
 ("SM_VK_Roof_Gable_Hoist",sky_roof_gable_hoist,SKY_NW),
 ("SM_VK_Roof_HalfHip",lambda k: sky_roof_halfhip(k,False),SKY_NW),
 ("SM_VK_RoofThatch_HalfHip",lambda k: sky_roof_halfhip(k,True),SKY_NW),
 ("SM_VK_Roof_CrossGable",sky_roof_crossgable,SKY_NW),
 ("SM_VK_Roof_Mid_CapL",lambda k: sky_roof_mid_cap(k,True),SKY_NW),
 ("SM_VK_Roof_Mid_CapR",lambda k: sky_roof_mid_cap(k,False),SKY_NW),
 ("SM_VK_Roof_Mid_Hatch",lambda k: sky_roof_mid_opening(k,"hatch"),SKY_NW),
 ("SM_VK_Roof_Mid_Skylight",lambda k: sky_roof_mid_opening(k,"skylight"),SKY_NW),
 ("SM_VK_Roof_Bellcote",sky_roof_bellcote,SKY_NW),
]+[("SM_VK_Emblem_Ridge_"+n_,f_,SKY_NW) for n_,f_ in SKY_EMBLEMS.items()]+[
 ("SM_VK_Banner_Wall",sky_banner_wall,SKY_NW),
 ("SM_VK_Banner_Pole",sky_banner_pole,SKY_NG),
 ("SM_VK_Banner_Roof",sky_banner_roof,SKY_NW),
 ("SM_VK_Prop_Bunting_6",lambda k: sky_bunting(k,6.0,0.5),SKY_NW),
 ("SM_VK_Prop_Bunting_9",lambda k: sky_bunting(k,9.0,0.8),SKY_NW),
]
EXTRA_SPECS+=WS_SPECS
