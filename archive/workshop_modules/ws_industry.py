# ===================== WORKSHOP: INDUSTRY (prefix ind_) =====================
# Production chains (spec M6 minus crops): mine, quarry, iron, clay, leather/cloth, food.
# Executed after vk_helpers in the same namespace: every kit function / constant is available.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

IND_NG=dict(wobble=False,grime=True)
IND_NW=dict(wobble=False,grime=False)
IND_GAUGE=0.8          # rail gauge (rail centre to rail centre)
IND_RAIL_TOP=0.225     # top of the rail head: place Prop_Minecart at this z on rails

def ind_pick(name,fallback): return name if bpy.data.objects.get(name) else fallback

# ---------------------------------------------------------------- generic helpers
def ind_faces(vs): return list({f for v in vs if v.is_valid for f in v.link_faces})
def ind_box_uv(k,faces,tile,offset=(0.0,0.0)):
    for f in faces:
        n=f.normal; ax=max(range(3),key=lambda i: abs(n[i]))
        for l in f.loops:
            p=l.vert.co
            uv=(p.y,p.z) if ax==0 else ((p.x,p.z) if ax==1 else (p.x,p.y))
            l[k.uv].uv=(uv[0]/tile+offset[0],uv[1]/tile+offset[1])
def ind_boulder(k,c,size,seed,mi=None,cuts=7,sub=2,flat_bottom=0.3,tile=1.5,rot=0.0,lean=0.0,cut_range=(0.6,0.84)):
    """faceted boulder (copy of the nature kit boulder); c = centre of its flat base"""
    mi=ROCK_MOSSY if mi is None else mi
    rnd=random.Random(seed)
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=sub,radius=1.0)["verts"]
    sv=Vector((seed*1.7,seed*0.3,seed*2.9))
    for v in vs:
        d=v.co.normalized(); v.co=d*(1+0.2*noise.noise(d*1.2+sv)+0.06*noise.noise(d*3.3+sv*1.3))
    for i in range(cuts):
        n=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-0.2,1))).normalized(); off=rnd.uniform(*cut_range)
        for v in vs:
            dd=v.co.dot(n)
            if dd>off: v.co-=n*(dd-off)*rnd.uniform(0.9,1.0)
    for v in vs:
        if v.co.z<-flat_bottom: v.co.z=-flat_bottom+(v.co.z+flat_bottom)*0.05
    M=Matrix.Translation(Vector(c))@Matrix.Rotation(rot,4,"Z")@Matrix.Rotation(lean,4,"X")
    for v in vs:
        v.co=M@Vector((v.co.x*size[0]/2,v.co.y*size[1]/2,(v.co.z+flat_bottom)/(1+flat_bottom)*size[2]))
    fs=ind_faces(vs)
    for f in fs: f.material_index=mi
    k.bm.normal_update(); ind_box_uv(k,fs,tile,(rnd.random(),rnd.random()))
    return vs
def ind_keepout(vs,lo,hi,pad=0.0):
    """push verts out of the axis-aligned box lo..hi along the axis of least penetration (keeps tunnels clear)"""
    for v in vs:
        p=v.co
        if all(lo[i]-pad<p[i]<hi[i]+pad for i in range(3)):
            best=None
            for i in range(3):
                for tgt in (lo[i]-pad,hi[i]+pad):
                    d=abs(tgt-p[i])
                    if best is None or d<best[0]: best=(d,i,tgt)
            p[best[1]]=best[2]
def ind_carve(k,vs,lo,hi):
    """open a clean tunnel-shaped hole in a shell: verts inside the box lo..hi are pushed to its side / top walls
       (never to the y-min face), then faces still spanning the box interior are deleted"""
    for v in vs:
        if not v.is_valid: continue
        p=v.co
        if all(lo[i]<p[i]<hi[i] for i in range(3)):
            c=[(abs(p.x-lo[0]),0,lo[0]),(abs(hi[0]-p.x),0,hi[0]),(abs(hi[2]-p.z),2,hi[2]),(abs(hi[1]-p.y),1,hi[1])]
            d,i,t=min(c); p[i]=t
    e=1e-3
    fs=[f for f in {f for v in vs if v.is_valid for f in v.link_faces}
        if all(lo[i]+e<f.calc_center_median()[i]<hi[i]-e for i in range(3))]
    if fs: bmesh.ops.delete(k.bm,geom=fs,context="FACES")
def ind_cyl_uv(k,faces,tile,c=(0.0,0.0),around=None,slant=False):
    """cylindrical UVs: u runs around the axis (around = number of texture tiles per turn), v = height"""
    cx,cy=c
    for f in faces:
        n=f.normal
        if abs(n.z)>0.97:
            for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.x/tile,p.y/tile)
            continue
        ang=[math.atan2(l.vert.co.y-cy,l.vert.co.x-cx) for l in f.loops]
        if max(ang)-min(ang)>math.pi: ang=[a+2*math.pi if a<0 else a for a in ang]
        for l,a in zip(f.loops,ang):
            p=l.vert.co; r=math.hypot(p.x-cx,p.y-cy)
            u=a/(2*math.pi)*around if around else a*r/tile
            v=p.z/tile if not slant else -r/tile*1.25+p.z/tile*0.3
            l[k.uv].uv=(u,v)
def ind_lathe(k,prof,c=(0,0,0),segs=16,mi=STONE_BLOCK,tile=None,around=None,cap_top=False,smooth=False,slant=False):
    fs=lathe(k,prof,center=c,segs=segs,mi=mi,smooth_=smooth,cap_top=cap_top)
    t=tile or TILE.get(mi,1.0)
    rmax=max(p[0] for p in prof)
    ind_cyl_uv(k,fs,t,(c[0],c[1]),around if around else max(1,round(2*math.pi*rmax/t)),slant=slant)
    return fs
def ind_beam(k,a,b,w,h,mi,bevel=0.03,roll=0.0,ext=0.0,segs=1):
    """square timber from point a to point b"""
    a=Vector(a); b=Vector(b); d=b-a
    yaw=math.atan2(d.y,d.x); el=math.atan2(d.z,math.hypot(d.x,d.y))
    return k.box(tuple((a+b)/2),(d.length+ext,w,h),mi,rot=(roll,-el,yaw),bevel=bevel,segs=segs)
def ind_rod(k,a,b,r,mi,segs=8,r2=None):
    """round pole / rope from a to b"""
    a=Vector(a); b=Vector(b); d=b-a
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    return _cyl(k,tuple((a+b)/2),r,r if r2 is None else r2,d.length,segs,mi,rot=q)
def ind_tbox(k,center,size,mi,top=(1.0,1.0),rot=(0,0,0),bevel=0.03,segs=1):
    """box whose top is scaled by top=(sx,sy) (tubs, carts, bins)"""
    sub=Kit(); vs=sub.box((0,0,0),size,mi,bevel=bevel,segs=segs); h=size[2]
    for v in set(vs):
        t=(v.co.z+h/2)/h; v.co.x*=1+(top[0]-1)*t; v.co.y*=1+(top[1]-1)*t
    R=Matrix.Rotation(rot[2],4,"Z")@Matrix.Rotation(rot[1],4,"Y")@Matrix.Rotation(rot[0],4,"X")
    merge_kit(k,sub,Matrix.Translation(Vector(center))@R)
def ind_heap(k,c,rx,ry,h,mi,seed=0,sub=2,rough=0.16,tile=1.5,peak=1.0,jit=0.0):
    """noisy mound with a flat base at c.z (ore, coal, soil, spoil); jit = per-vertex lumps (faceted rubble)"""
    sv=Vector((seed*1.31,seed*0.77,seed*2.13)); rj=random.Random(seed+5)
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=sub,radius=1.0)["verts"]
    for v in vs:
        d=v.co.normalized(); f=1+rough*noise.noise(d*1.9+sv)+rough*0.4*noise.noise(d*4.7+sv)
        e=max(d.z,0.0)
        z=h*(e**peak)*f if d.z>0 else -0.04
        if jit and d.z>0.05: f+=rj.uniform(-jit,jit); z+=rj.uniform(-jit,jit)*h
        v.co=Vector((c[0]+d.x*rx*f,c[1]+d.y*ry*f,c[2]+z))
    fs=ind_faces(vs)
    for f in fs: f.material_index=mi
    k.bm.normal_update(); ind_box_uv(k,fs,tile,(seed*0.137%1,seed*0.071%1))
    return vs
def ind_chunks(k,c,rx,ry,h,n,mats,seed=0,size=(0.12,0.28),sub=1):
    """n faceted chunks scattered over a heap of radii rx,ry and height h"""
    rnd=random.Random(seed)
    for i in range(n):
        a=rnd.uniform(0,2*math.pi); t=math.sqrt(rnd.random())*0.9
        x=c[0]+math.cos(a)*rx*t; y=c[1]+math.sin(a)*ry*t
        z=c[2]+h*max(0.0,1-t*t)**0.8-0.04
        s=rnd.uniform(*size); mi=mats[i%len(mats)]
        vs=_ico(k,(x,y,z),s,mi,(rnd.uniform(0.8,1.3),rnd.uniform(0.8,1.2),rnd.uniform(0.55,0.9)),sub=sub,jit=s*0.18,seed=seed*97+i)
        ind_box_uv(k,ind_faces(vs),TILE.get(mi,1.0),(rnd.random(),rnd.random()))
def ind_tuft(k,p,h,seed=0,cell="grass",n=2):
    rnd=random.Random(seed)
    for i in range(n):
        a=rnd.uniform(0,math.pi)+i*math.pi/n
        card(k,(p[0],p[1],p[2]+h/2-0.03),(math.cos(a),math.sin(a),0),(rnd.uniform(-.1,.1),rnd.uniform(-.1,.1),1),h*1.25,h,cell,flip=i%2==0)
def ind_sweep(k,pts,w,h,mi,z0=0.0,caps=True):
    """rectangular profile (w wide, h tall, bottom at z0) swept along a 2D/3D polyline with mitred joins"""
    P=[Vector((p[0],p[1],p[2] if len(p)>2 else z0)) for p in pts]; rings=[]
    for i,p in enumerate(P):
        a=P[max(i-1,0)]; b=P[min(i+1,len(P)-1)]; t=(b-a); t.z=0; t.normalize()
        nrm=Vector((-t.y,t.x,0))
        if 0<i<len(P)-1:
            t1=(P[i]-P[i-1]); t1.z=0; t1.normalize(); n1=Vector((-t1.y,t1.x,0))
            cosh=max(0.3,nrm.dot(n1)); nrm=nrm/cosh
        hw=w/2
        rings.append([k.bm.verts.new(p+nrm*hw),k.bm.verts.new(p-nrm*hw),k.bm.verts.new(p-nrm*hw+Vector((0,0,h))),k.bm.verts.new(p+nrm*hw+Vector((0,0,h)))])
    fs=[]
    for r0,r1 in zip(rings[:-1],rings[1:]):
        for j in range(4):
            jj=(j+1)%4; fs.append(k.bm.faces.new((r0[j],r1[j],r1[jj],r0[jj])))
    if caps:
        fs.append(k.bm.faces.new(rings[0])); fs.append(k.bm.faces.new(rings[-1][::-1]))
    k.bm.normal_update()
    k.project(fs,mi)
    return fs
def ind_bvh(k):
    from mathutils.bvhtree import BVHTree
    k.bm.normal_update(); return BVHTree.FromBMesh(k.bm)
def ind_drop(bvh,x,y,z0=30.0,default=0.0):
    hit=bvh.ray_cast(Vector((x,y,z0)),Vector((0,0,-1)))
    return hit[0].z if hit[0] is not None else default
def ind_skirt(k,x0,x1,y0,y1,mi=ROCK,z1=-0.02):
    """hidden skirt under a footprint (continues down to -0.6 for uneven terrain)"""
    k.box(((x0+x1)/2,(y0+y1)/2,(z1-0.6)/2),(x1-x0,y1-y0,z1+0.6),mi,bevel=0)

# ================================================================ MINE
def ind_lagging(k,x0,x1,z0,z1,y,n=None,seed=0,vertical=True):
    """row of rough boards (PLANKS) on a plane y = const"""
    rnd=random.Random(seed); n=n or max(2,int(round((x1-x0)/0.24)))
    for i in range(n):
        x=x0+(i+0.5)*(x1-x0)/n
        k.box((x,y+rnd.uniform(-0.015,0.015),(z0+z1)/2+rnd.uniform(-0.04,0.04)),((x1-x0)/n-0.025,0.05,z1-z0-rnd.uniform(0,0.12)),PLANKS,rot=(0,rnd.uniform(-0.03,0.03),0),bevel=0.012)
def ind_timber_set(k,y,hw,h,post=0.32,cap_len=None,capz=None,seed=0,braces=True):
    rnd=random.Random(seed); cap_len=cap_len or 2*hw+0.9
    for s in(-1,1):
        ind_beam(k,(s*(hw+post/2+0.07),y,-0.05),(s*(hw+post/2-0.02),y,h+0.02),post,post,WOOD,bevel=0.05,segs=1)
        if braces:
            ind_beam(k,(s*(hw+0.05),y,h-0.55),(s*(hw-0.45),y,h+0.04),0.16,0.18,WOOD,bevel=0.03)
    ch=post+0.08
    k.box((rnd.uniform(-0.04,0.04),y,h+ch/2),(cap_len,post+0.06,ch),WOOD,rot=(0,rnd.uniform(-0.015,0.015),0),bevel=0.05,segs=1)
def ind_mine_portal(k):
    """mine entrance in a boulder mound. Origin: ground at the portal mouth, tunnel runs +Y, face -Y.
       Tunnel 2.5 wide x 2.6 high x 3 deep, rails enter along local Y (x=0)."""
    hw=1.25; yb=2.9
    # ---- tunnel interior (faces point inward)
    k.quad([(-hw-0.1,-0.5,0.03),(hw+0.1,-0.5,0.03),(hw+0.1,yb,0.03),(-hw-0.1,yb,0.03)],SOIL)
    k.quad([(-hw-0.2,yb,-0.05),(hw+0.2,yb,-0.05),(hw+0.2,yb,3.0),(-hw-0.2,yb,3.0)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for s in(-1,1):
        x=s*(hw+0.08)
        pts=[(x,1.9,0.0),(x,yb,0.0),(x,yb,3.0),(x,1.9,3.0)]
        k.quad(pts if s<0 else pts[::-1],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.quad([(-hw-0.2,1.9,2.93),(hw+0.2,1.9,2.93),(hw+0.2,yb,2.93),(-hw-0.2,yb,2.93)][::-1],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    # lagging boards on the walls and ceiling of the timbered part
    for s in(-1,1):
        sub=Kit(); ind_lagging(sub,-0.25,2.0,0.0,2.6,0.0,n=9,seed=3+s)
        merge_kit(k,sub,Matrix.Translation((s*(hw+0.08),0,0))@Matrix.Rotation(math.pi/2,4,"Z"))
    sub=Kit(); ind_lagging(sub,-0.25,2.0,-hw-0.1,hw+0.1,0.0,n=9,seed=9)
    merge_kit(k,sub,Matrix(((0,0,1,0),(1,0,0,0),(0,1,0,2.95),(0,0,0,1))))
    # inner timber sets (0.8 apart) and the chunky front portal set
    for i,y in enumerate((0.45,1.25)):
        ind_timber_set(k,y,hw-0.12,2.58,post=0.26,cap_len=2*hw+0.25,seed=i,braces=(i==0))
    ind_timber_set(k,-0.36,hw+0.02,3.0,post=0.38,cap_len=3.6,seed=7)
    k.box((0,-0.36,3.62),(2.4,0.34,0.22),WOOD,bevel=0.04)                       # second lintel
    for s in(-1,1):
        k.box((s*1.58,-0.42,0.12),(0.62,0.62,0.24),STONE_BLOCK,bevel=0.06,segs=2)  # post pads
        k.box((s*0.95,-0.36,3.68),(0.2,0.3,0.34),WOOD,bevel=0.03)               # wedges
    # sign: board with crossed picks
    k.box((0,-0.58,3.62),(1.25,0.08,0.52),PLANKS,bevel=0.03)
    for s in(-1,1):
        a=Vector((s*0.4,-0.66,3.4)); b=Vector((-s*0.34,-0.66,3.84))
        ind_beam(k,a,b,0.06,0.05,WOOD,bevel=0.01)
        d=(b-a).normalized(); pp=Vector((d.z,0,-d.x))
        ind_beam(k,b+pp*0.2+d*0.03,b-pp*0.2+d*0.03,0.07,0.08,STEEL,bevel=0.015)
    # lantern on the left post
    sub=Kit(); prop_lantern(sub); merge_kit(k,sub,Matrix.Translation((-1.62,-0.55,2.55)))
    # ---- grassy hill core + boulder outcrops (all kept out of the tunnel)
    keep_lo=(-hw-0.3,-0.9,-1.0); keep_hi=(hw+0.3,yb+0.15,3.25)
    vs=ind_heap(k,(0.0,2.9,0.0),4.3,3.5,4.3,MOSS,seed=8,sub=3,rough=0.14,peak=0.8,tile=2.0)
    ind_carve(k,vs,(keep_lo[0],-3.0,keep_lo[2]),keep_hi)      # open the hill where the tunnel runs (hidden by the portal set)
    bvh0=ind_bvh(k)
    for i,(x,y,sz) in enumerate(((1.9,3.4,1.5),(-1.7,2.6,1.3),(3.0,1.9,1.1),(0.5,5.0,1.4),(-2.9,4.4,1.2),(-0.4,3.2,1.0))):
        z=ind_drop(bvh0,x,y)
        vs=ind_boulder(k,(x,y,z-sz*0.5),(sz*1.3,sz*1.1,sz),40+i,mi=ROCK_MOSSY,sub=1,cuts=6,rot=i*1.3)
        ind_keepout(vs,keep_lo,keep_hi)
    B=[((-3.0,1.0,-0.05),(3.0,3.4,3.0),11,0.3,2),((2.9,0.9,-0.05),(2.8,3.2,2.6),12,-0.4,2),
       ((0.2,1.5,2.9),(4.2,3.0,1.5),13,0.1,2),((-0.6,4.0,2.4),(3.6,3.0,2.5),14,0.5,2),
       ((-3.6,3.4,-0.05),(2.4,2.4,2.2),15,0.8,1),((3.4,3.3,-0.05),(2.4,2.2,1.9),16,-0.6,1)]
    for (c,sz,sd,rz,sb) in B:
        vs=ind_boulder(k,c,sz,sd,mi=ROCK_MOSSY,rot=rz,sub=sb,cuts=8)
        ind_keepout(vs,keep_lo,keep_hi)
    rnd=random.Random(5)
    for i,(x,y,sz) in enumerate(((-2.1,-0.9,0.7),(2.2,-0.7,0.55),(-3.9,-0.3,0.6),(3.8,-0.2,0.5),(1.9,-1.2,0.35))):
        ind_boulder(k,(x,y,-0.05),(sz*1.3,sz,sz*0.8),30+i,mi=ROCK,sub=1,cuts=4,rot=rnd.uniform(0,6))
    bvh=ind_bvh(k)
    for i in range(22):
        a_=rnd.uniform(0,2*math.pi); d=rnd.uniform(0.35,1.0)
        x=math.cos(a_)*d*4.2; y=2.9+math.sin(a_)*d*3.4
        if abs(x)<1.9 and y<0.6: continue
        z=ind_drop(bvh,x,y)
        ind_tuft(k,(x,y,z-0.05),rnd.uniform(0.45,0.75),seed=i,cell="grass" if i%4 else "daisy")
    ind_skirt(k,-4.2,4.2,-0.3,5.4)
    # a pick leaning on the right post
    ind_beam(k,(1.95,-0.75,0.02),(1.75,-0.62,1.05),0.06,0.06,WOOD,bevel=0.01)
    ind_beam(k,(1.6,-0.6,1.02),(1.95,-0.66,1.1),0.07,0.07,STEEL,bevel=0.015)

# ---------------------------------------------------------------- rails
def ind_rail_pair(k,pts):
    for s in(-1,1):
        P=[]
        for i,p in enumerate(pts):
            a=Vector(pts[max(i-1,0)]); b=Vector(pts[min(i+1,len(pts)-1)]); t=(b-a).normalized(); n=Vector((-t.y,t.x))
            P.append(Vector(p)+n*s*IND_GAUGE/2)
        ind_sweep(k,P,0.13,0.025,STEEL,z0=0.145)
        ind_sweep(k,P,0.075,0.06,STEEL,z0=0.165)
def ind_bed(k,pts,w=1.6):
    ind_sweep(k,pts,w,0.34,ROCK,z0=-0.3)
def ind_sleeper(k,p,yaw,seed):
    rnd=random.Random(seed)
    k.box((p[0]+rnd.uniform(-0.03,0.03),p[1]+rnd.uniform(-0.03,0.03),0.09),(0.2,1.25,0.11),WOOD,rot=(0,0,yaw+rnd.uniform(-0.06,0.06)),bevel=0.025)
def ind_rail_straight(k,x0=-1.5,x1=1.5,seed=0):
    ind_bed(k,[(x0,0),(x1,0)])
    n=int(round((x1-x0)/0.5))
    for i in range(n): ind_sleeper(k,(x0+0.25+i*0.5,0),0.0,seed*31+i)
    ind_rail_pair(k,[(x0,0),(x1,0)])
def ind_rail_curve(k):
    """90 deg curve, radius 3: enters at (-1.5,0) heading +X, leaves at (1.5,3) heading +Y"""
    C=Vector((-1.5,3.0)); R=3.0; n=16
    pts=[C+R*Vector((math.cos(-math.pi/2+math.pi/2*i/n),math.sin(-math.pi/2+math.pi/2*i/n))) for i in range(n+1)]
    ind_bed(k,pts)
    m=9
    for i in range(m):
        th=-math.pi/2+math.pi/2*(i+0.5)/m; p=C+R*Vector((math.cos(th),math.sin(th)))
        ind_sleeper(k,p,th+math.pi/2,70+i)
    ind_rail_pair(k,pts)
def ind_rail_end(k):
    """straight 3 m with a buffer stop at +X"""
    ind_bed(k,[(-1.5,0),(1.5,0)])
    for i in range(6): ind_sleeper(k,(-1.25+i*0.5,0),0.0,90+i)
    ind_rail_pair(k,[(-1.5,0),(0.95,0)])
    for s in(-1,1):
        for y in(-0.45,0.45):
            pass
    for y in(-0.42,0.42):
        k.box((1.1,y,0.45),(0.24,0.24,0.9),WOOD,bevel=0.04)
        ind_beam(k,(1.55,y,0.05),(1.12,y,0.8),0.18,0.18,WOOD,bevel=0.03)
    k.box((1.0,0,0.62),(0.3,1.4,0.34),WOOD,bevel=0.05,segs=2)
    k.box((0.83,0,0.62),(0.06,1.1,0.2),IRON,bevel=0.01)
    ind_heap(k,(1.55,0,0.0),0.55,0.85,0.45,SOIL,seed=4,sub=2)
    for i,(y,h) in enumerate(((-0.4,0.45),(0.3,0.55),(0.0,0.4))): ind_tuft(k,(1.6+0.1*i,y,0.25),h,seed=60+i)
    rnd=random.Random(3)
    for i in range(3): rock(k,(1.5+rnd.uniform(-0.3,0.3),rnd.uniform(-0.7,0.7),0.1),(0.3,0.25,0.2),seed=40+i,mi=ROCK)

# ---------------------------------------------------------------- minecart + piles
def ind_ore_fill(k,c,rx,ry,h,seed,coal=False,n=None):
    """heap of broken ore / coal: noisy mound covered by low-poly chunks dropped onto its surface"""
    sub=Kit()
    ind_heap(sub,(0,0,0),rx,ry,h,COAL if coal else ROCK,seed=seed,sub=2,rough=0.2,jit=0.07 if coal else 0.04,tile=1.1)
    bvh=ind_bvh(sub); rnd=random.Random(seed+1)
    if not coal and rx>0.7:   # medium faceted lumps break the smooth boulder read
        for i in range(int(3+5*rx*ry)):
            a=rnd.uniform(0,2*math.pi); t=math.sqrt(rnd.random())*0.85
            x=math.cos(a)*rx*t; y=math.sin(a)*ry*t; z=ind_drop(bvh,x,y,default=0.0)
            s=rnd.uniform(0.2,0.32)*min(1.2,rx)
            vs=_ico(sub,(x,y,z-s*0.25),s,ROCK if i%3 else CLAY,(rnd.uniform(1.0,1.4),rnd.uniform(0.8,1.1),rnd.uniform(0.55,0.75)),sub=1,jit=s*0.18,seed=seed*31+i)
            ind_box_uv(sub,ind_faces(vs),1.1,(rnd.random(),rnd.random()))
        bvh=ind_bvh(sub)
    mats=[COAL,COAL,IRON,COAL] if coal else [ROCK,ROCK,CLAY,ROCK,COAL,STONE_BLOCK,CLAY]
    n=n or int(14+(14 if not coal and rx>0.7 else 22)*rx*ry); big=rx>0.7
    for i in range(n):
        a=rnd.uniform(0,2*math.pi); t=math.sqrt(rnd.random())*0.97
        x=math.cos(a)*rx*t; y=math.sin(a)*ry*t; z=ind_drop(bvh,x,y,default=0.0)
        s=rnd.uniform(0.1,0.21) if big else rnd.uniform(0.06,0.12)
        mi=mats[i%len(mats)]
        vs=_ico(sub,(x,y,z+s*0.05),s,mi,(rnd.uniform(0.9,1.4),rnd.uniform(0.8,1.2),rnd.uniform(0.5,0.8)),sub=0,jit=s*0.22,seed=seed*97+i)
        ind_box_uv(sub,ind_faces(vs),TILE.get(mi,1.0),(rnd.random(),rnd.random()))
    merge_kit(k,sub,Matrix.Translation(Vector(c)))
def ind_minecart(k,coal=False):
    """ore tub on 4 flanged wheels; origin at wheel bottom (place at z=IND_RAIL_TOP on rails), long axis X"""
    wr=0.16; wz=wr
    for sx in(-0.38,0.38):
        _cyl(k,(sx,0,wz),0.035,0.035,IND_GAUGE+0.18,6,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
        for sy in(-1,1):
            y=sy*IND_GAUGE/2
            _cyl(k,(sx,y,wz),wr,wr,0.07,12,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
            _cyl(k,(sx,y-sy*0.04,wz),wr+0.035,wr+0.035,0.025,12,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
            _cyl(k,(sx,y+sy*0.045,wz),0.06,0.06,0.04,8,STEEL,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for sy in(-0.3,0.3): k.box((0,sy,0.31),(1.25,0.12,0.12),WOOD,bevel=0.025)
    for sx in(-0.62,0.62): k.box((sx,0,0.31),(0.12,0.75,0.14),WOOD,bevel=0.025)
    zb,zt=0.38,0.95
    ind_tbox(k,(0,0,(zb+zt)/2),(1.0,0.66,zt-zb),PLANKS,top=(1.22,1.3),bevel=0.03)
    # iron straps and rim
    for sx in(-1,1):
        for sy in(-1,1):
            ind_beam(k,(sx*0.5,sy*0.33,zb),(sx*0.61,sy*0.43,zt+0.02),0.07,0.07,IRON,bevel=0.01)
    for (x,y,L,yaw) in ((0,-0.44,1.26,0),(0,0.44,1.26,0),(-0.62,0,0.9,math.pi/2),(0.62,0,0.9,math.pi/2)):
        k.box((x,y,zt),(L,0.07,0.08),WOOD if False else IRON,rot=(0,0,yaw),bevel=0.015)
    for sy in(-1,1):
        ind_beam(k,(-0.55,sy*0.37,0.62),(0.55,sy*0.37,0.62),0.035,0.04,IRON,bevel=0.005)
    ind_ore_fill(k,(0,0,zt-0.05),0.48,0.32,0.26,seed=21,coal=coal)
    # push handle / coupling
    for sy in(-0.25,0.25): ind_beam(k,(-0.62,sy,0.8),(-0.95,sy,0.95),0.05,0.05,WOOD,bevel=0.01)
    k.box((-0.96,0,0.95),(0.07,0.6,0.07),WOOD,bevel=0.015)
    ring(k,(0.72,0,0.34),0.04,0.07,0.03,IRON,n=8,axis="Z")
def ind_pile_ore(k,size=1):
    r=(0.8,1.1,1.4)[size-1]
    ind_ore_fill(k,(0,0,0),r,r*0.85,r*0.55*1.1,seed=40+size)
    rnd=random.Random(size)
    for i in range(2+size*2):
        a=rnd.uniform(0,6.28); d=r*rnd.uniform(0.95,1.2)
        rock(k,(math.cos(a)*d,math.sin(a)*d*0.85,0.06),(0.22,0.18,0.14),seed=50+i+size*10,mi=ROCK if i%3 else CLAY,segs=1)
    if size==3:   # a spade and a basket
        ind_beam(k,(1.1,-0.9,0.05),(0.8,-0.55,1.15),0.05,0.05,WOOD,bevel=0.01)
        k.box((1.13,-0.93,0.2),(0.22,0.05,0.3),STEEL,rot=(0,0,0.85),bevel=0.02)
def ind_pile_coal(k,size=1):
    r=(0.8,1.1,1.4)[size-1]
    if size>=2:   # plank bin behind the heap
        L=2*r+0.4
        for i in range(3): k.box((0,r*0.75+0.1,0.12+i*0.24),(L,0.08,0.22),PLANKS,bevel=0.015)
        for sx in(-1,1):
            k.box((sx*L/2,r*0.75+0.2,0.4),(0.14,0.14,0.8),WOOD,bevel=0.03)
            if size==3:
                for i in range(3): k.box((sx*(L/2-0.04),0.1,0.12+i*0.24),(0.08,2*r*0.75,0.22),PLANKS,bevel=0.015)
                k.box((sx*L/2,-r*0.6,0.35),(0.14,0.14,0.7),WOOD,bevel=0.03)
    ind_ore_fill(k,(0,0,0),r,r*0.8,r*0.55,seed=60+size,coal=True)
    rnd=random.Random(size+3)
    for i in range(3+size*2):
        a=rnd.uniform(3.14,6.28); d=r*rnd.uniform(0.95,1.25)
        _ico(k,(math.cos(a)*d,math.sin(a)*d*0.8,0.05),rnd.uniform(0.07,0.12),COAL,(1.2,1,0.7),sub=1,jit=0.02,seed=i)
    if size==1:   # a wicker basket of coal
        _cyl(k,(1.0,-0.3,0.2),0.24,0.3,0.4,10,WATTLE)
        ind_heap(k,(1.0,-0.3,0.36),0.27,0.27,0.12,COAL,seed=5,sub=1)

# ================================================================ QUARRY
IND_Q_LO=(0.0,0.75,2)     # lower bench: z0, course height, courses  (top 1.5 = 1 LVL)
IND_Q_HI=(1.5,0.6,2)      # upper bench: 1.5 .. 2.7, then a 0.3 soil band to 3.0 (2 LVL)
def ind_qrun(k,x0,x1,yf,bench,seed,depth=0.8,missing=(),pulled=(),drill=True):
    """one bench of cut blocks along X, face toward -Y at y=yf; block tops form the tread"""
    z0,ch,courses=bench; rnd=random.Random(seed)
    for c in range(courses):
        zc=z0+c*ch; xs=[x0]; x=x0
        while True:
            w=rnd.uniform(0.7,1.2)
            if x1-(x+w)<0.45: xs.append(x1); break
            x+=w; xs.append(x)
        for i,(a,b) in enumerate(zip(xs[:-1],xs[1:])):
            if (c,i) in missing: continue
            out=rnd.uniform(-0.12,0.06)
            if (c,i) in pulled: out=-0.34
            hh=ch-0.05-(rnd.uniform(0,0.1) if c==courses-1 else 0)
            k.box(((a+b)/2,yf+out+depth/2,zc+hh/2+0.025),(b-a-0.05,depth,hh),STONE_BLOCK,
                  rot=(rnd.uniform(-.015,.015),rnd.uniform(-.015,.015),rnd.uniform(-.02,.02)),bevel=0.06,segs=1)
            if drill and c==courses-1 and rnd.random()<0.22:
                xm=rnd.uniform(a+0.15,b-0.4)
                for j in range(3): k.box((xm+j*0.13,yf+out-0.002,zc+hh-0.2),(0.025,0.012,0.3),VOID,bevel=0)
def ind_qcores(k,lo_boxes,hi_boxes,band_boxes,seed=0):
    """ROCK cores behind the blocks (dark joints), a soil band 2.7..3.0 with a turf top"""
    for (x0,x1,y0,y1) in lo_boxes: k.box(((x0+x1)/2,(y0+y1)/2,(-0.6+1.45)/2),(x1-x0,y1-y0,2.05),ROCK,bevel=0)
    for (x0,x1,y0,y1) in hi_boxes: k.box(((x0+x1)/2,(y0+y1)/2,(1.45+2.7)/2),(x1-x0,y1-y0,1.25),ROCK,bevel=0)
    for (x0,x1,y0,y1) in band_boxes:
        vs=k.box(((x0+x1)/2,(y0+y1)/2,2.85),(x1-x0,y1-y0,0.3),SOIL,bevel=0)
        grid_cut(k,vs,0.5)
        vv=list({v for v in k.bm.verts if x0-0.01<=v.co.x<=x1+0.01 and y0-0.01<=v.co.y<=y1+0.01 and 2.69<v.co.z<2.71})
        for v in vv:   # ragged bottom edge of the soil band, periodic so modules meet
            v.co.z+=0.05*math.sin(2*math.pi*v.co.x/1.5+1.3)+0.04*math.sin(2*math.pi*v.co.y/1.5+0.4)-0.03
    k.bm.normal_update()
    fs=[f for f in k.bm.faces if f.material_index==SOIL and f.normal.z>0.9 and abs(f.calc_center_median().z-3.0)<0.01]
    k.project(fs,MOSS)
    k.project([f for f in k.bm.faces if f.material_index==SOIL and abs(f.normal.z)<0.5],SOIL)
def ind_qrubble(k,x0,x1,y,seed,n=6):
    rnd=random.Random(seed)
    for i in range(n):
        x=rnd.uniform(x0+0.2,x1-0.2); s=rnd.uniform(0.18,0.45)
        rock(k,(x,y+rnd.uniform(-0.35,0.25),s*0.35),(s*rnd.uniform(1,1.6),s,s*0.8),seed=seed*13+i,mi=STONE_BLOCK if i%3 else ROCK,segs=1)
def ind_qtop(k,pts,seed,edge=()):
    """turf lumps and tufts on the plateau; edge = tufts hanging over the cut edge"""
    rnd=random.Random(seed)
    for i,(x,y) in enumerate(pts):
        if i%3==0: ind_boulder(k,(x,y,2.95),(rnd.uniform(0.6,0.9),rnd.uniform(0.5,0.7),rnd.uniform(0.25,0.4)),seed*7+i,mi=ROCK_MOSSY,sub=1,cuts=4,rot=rnd.uniform(0,6))
        else: ind_tuft(k,(x,y,3.0),rnd.uniform(0.4,0.6),seed=seed+i,cell="grass" if i%4 else "daisy")
    for i,(x,y) in enumerate(edge): ind_tuft(k,(x,y,2.97),rnd.uniform(0.35,0.5),seed=seed*3+i)
def ind_quarry_face(k):
    """contour piece, 3 m, 3.0 high (2 LVL), face -Y: lower face y=-0.8 (z 0..1.5), bench tread z 1.5,
       upper face y=0 (z 1.5..2.7), soil band + turf to z 3.0 behind y=0. Pivot = segment midpoint."""
    ind_qrun(k,-1.5,1.5,-0.8,IND_Q_LO,seed=1,missing=((1,1),),pulled=((0,2),))
    ind_qrun(k,-1.5,1.5,0.0,IND_Q_HI,seed=2,pulled=((1,0),))
    ind_qcores(k,[(-1.5,1.5,-0.5,1.5)],[(-1.5,1.5,0.3,1.5)],[(-1.5,1.5,-0.04,1.5)])
    k.box((0,-0.65,-0.31),(3.0,0.3,0.58),ROCK,bevel=0)
    ind_qrubble(k,-1.5,1.5,-1.2,3)
    rock(k,(0.35,-0.35,1.62),(0.75,0.45,0.32),seed=77,mi=STONE_BLOCK,segs=1)     # loose block on the bench
    rock(k,(-0.9,-1.35,0.2),(0.8,0.5,0.4),seed=78,mi=STONE_BLOCK,segs=1)         # fallen block at the foot
    ind_qtop(k,[(-1.0,1.05),(-0.3,1.2),(0.6,0.9),(1.2,1.25),(0.1,0.6)],5,edge=((-1.2,0.02),(0.4,0.0),(1.1,0.04)))
def ind_quarry_corner(k):
    """outer (convex) corner, faces -X and -Y (like wall corners). Joins Straight at (3,0) rot 0 and (0,3) rot -90"""
    R=Matrix.Rotation(-math.pi/2,4,"Z")
    ind_qrun(k,-0.8,1.5,-0.8,IND_Q_LO,seed=11)
    sub=Kit(); ind_qrun(sub,-1.5,0.0,-0.8,IND_Q_LO,seed=12,pulled=((0,0),)); merge_kit(k,sub,R)
    ind_qrun(k,0.0,1.5,0.0,IND_Q_HI,seed=13)
    sub=Kit(); ind_qrun(sub,-1.5,-0.8,0.0,IND_Q_HI,seed=14,drill=False); merge_kit(k,sub,R)
    ind_qcores(k,[(-0.5,1.5,-0.5,1.5)],[(0.3,1.5,0.3,1.5)],[(-0.04,1.5,-0.04,1.5)])
    k.box((0.35,-0.65,-0.31),(2.3,0.3,0.58),ROCK,bevel=0); k.box((-0.65,0.5,-0.31),(0.3,2.0,0.58),ROCK,bevel=0)
    ind_qrubble(k,-0.8,1.5,-1.2,15,n=4)
    sub=Kit(); ind_qrubble(sub,-1.5,0.0,-1.2,16,n=3); merge_kit(k,sub,R)
    ind_qtop(k,[(1.0,1.1),(0.6,0.9),(0.95,0.4),(0.4,1.3)],17,edge=((0.02,0.5),(0.6,0.02),(0.05,0.05)))
def ind_quarry_innercorner(k):
    """inner (concave) corner: floor at x<-0.8,y<-0.8. Joins Straight at (-3,0) rot 0 and (0,-3) rot -90"""
    R=Matrix.Rotation(-math.pi/2,4,"Z")
    ind_qrun(k,-1.5,-0.8,-0.8,IND_Q_LO,seed=21,drill=False)
    sub=Kit(); ind_qrun(sub,0.8,1.5,-0.8,IND_Q_LO,seed=22,drill=False); merge_kit(k,sub,R)
    ind_qrun(k,-0.8,0.0,-0.8,IND_Q_LO,seed=23,drill=False)      # corner fill (only its tread shows)
    ind_qrun(k,-1.5,0.0,0.0,IND_Q_HI,seed=24)
    sub=Kit(); ind_qrun(sub,0.0,1.5,0.0,IND_Q_HI,seed=25); merge_kit(k,sub,R)
    ind_qrun(k,0.0,0.8,0.0,IND_Q_HI,seed=26,drill=False)
    ind_qcores(k,[(-1.5,1.5,-0.5,1.5),(-0.5,1.5,-1.5,-0.5)],[(-1.5,1.5,0.3,1.5),(0.3,1.5,-1.5,0.3)],
               [(-1.5,1.5,-0.04,1.5),(-0.04,1.5,-1.5,-0.04)])
    k.box((-1.15,-0.65,-0.31),(0.7,0.3,0.58),ROCK,bevel=0); k.box((-0.65,-1.15,-0.31),(0.3,0.7,0.58),ROCK,bevel=0)
    ind_qrubble(k,-1.5,-0.9,-1.2,27,n=3)
    ind_qtop(k,[(-0.8,1.2),(0.4,1.1),(1.2,1.2),(1.1,0.2),(1.2,-0.8),(0.6,0.6)],28,edge=((-1.0,0.02),(0.02,-1.0),(0.03,0.03)))
def ind_quarry_floor(k):
    """3x3 cell of quarried rock floor (top z 0.03) with a block being split by iron wedges"""
    rnd=random.Random(4)
    for i,(x0,x1,y0,y1) in enumerate(((-1.5,0.2,-1.5,-0.1),(0.2,1.5,-1.5,0.4),(-1.5,-0.3,-0.1,1.5),(-0.3,1.5,0.4,1.5))):
        k.box(((x0+x1)/2,(y0+y1)/2,-0.29+0.015*i),(x1-x0-0.05,y1-y0-0.05,0.64),STONE_BLOCK,bevel=0.03)
    k.box((0,0,-0.35),(2.98,2.98,0.5),ROCK,bevel=0)
    for s in(-1,1):
        k.box((0.1+s*0.33,-0.2,0.34),(0.6,0.75,0.62),STONE_BLOCK,rot=(0,s*0.03,0.05),bevel=0.06)
    for j in range(3):
        ind_tbox(k,(0.1,-0.45+j*0.25,0.68),(0.07,0.07,0.16),IRON,top=(2.2,1.2),bevel=0.01)
    ind_beam(k,(0.9,0.55,0.08),(1.35,1.2,0.08),0.06,0.06,WOOD,bevel=0.01)
    k.box((0.86,0.5,0.12),(0.18,0.3,0.16),IRON,rot=(0,0,0.96),bevel=0.02)
    for i in range(14):
        rock(k,(rnd.uniform(-1.3,1.3),rnd.uniform(-1.3,1.3),0.06),(rnd.uniform(0.08,0.2),rnd.uniform(0.07,0.15),0.08),seed=100+i,mi=STONE_BLOCK,segs=1)
    k.box((-0.8,0.8,0.28),(1.1,0.7,0.5),STONE_BLOCK,rot=(0,0,0.3),bevel=0.05)
    for j in range(4): k.box((-1.2+j*0.2*math.cos(0.3),0.68+j*0.2*math.sin(0.3),0.532),(0.045,0.045,0.01),VOID,bevel=0)
    for (x,y) in ((-1.3,-1.2),(1.35,-0.2),(-1.35,0.2)): ind_tuft(k,(x,y,0.02),0.3,seed=int(x*10+y*3))
def ind_banker(k):
    """mason's banker: slab on two ashlar blocks, a column drum being dressed, mallet and chisel"""
    for x in(-0.45,0.45): k.box((x,0,0.3),(0.36,0.62,0.6),ASHLAR,bevel=0.04,segs=1)
    k.box((0,0,0.7),(1.35,0.75,0.2),STONE_BLOCK,bevel=0.04,segs=1)
    # drum lying on its side: dressed round half + still-square half
    sub=Kit()
    ind_lathe(sub,[(0.0,0.0),(0.3,0.0),(0.32,0.03),(0.32,0.34),(0.0,0.34)],segs=16,mi=STONE_BLOCK)
    sub.box((0,0,0.52),(0.64,0.62,0.36),STONE_BLOCK,bevel=0.05,jitter=0.02,seed=3)
    merge_kit(k,sub,Matrix.Translation((-0.25,0,1.12))@Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(0.38,-0.2,0.88),0.08,0.08,0.18,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    ind_beam(k,(0.38,-0.2,0.88),(0.42,0.12,0.84),0.035,0.035,WOOD,bevel=0.005)
    ind_beam(k,(0.2,0.22,0.82),(0.45,0.26,0.82),0.025,0.025,STEEL,bevel=0.005)
    rnd=random.Random(2)
    for i in range(10):
        rock(k,(rnd.uniform(-0.9,0.9),rnd.uniform(-0.7,0.7),0.03),(0.1,0.08,0.06),seed=10+i,mi=STONE_BLOCK,segs=1)
IND_CRANE_AXLE=(-1.0,0.0,2.2)   # where the builder puts Prop_TreadwheelCrane_Wheel
def ind_crane(k):
    """treadwheel crane (frame + jib, 9 m). The wheel is the separate piece Prop_TreadwheelCrane_Wheel
       placed at IND_CRANE_AXLE, spin_axis local Y. Jib points +X, the hanging block sits at x ~6.6."""
    ax=Vector(IND_CRANE_AXLE); ya=1.15
    # sill cross + stone pads
    k.box((0.2,0,0.16),(5.2,0.32,0.3),WOOD,bevel=0.04)
    for x in(-1.0,1.0): k.box((x,0,0.16),(0.3,2*ya+0.5,0.28),WOOD,bevel=0.04)
    for (x,y) in((-2.4,0),(2.8,0),(-1.0,-ya-0.15),(-1.0,ya+0.15),(1.0,-ya-0.15),(1.0,ya+0.15)):
        k.box((x,y,0.06),(0.5,0.5,0.12),STONE_BLOCK,bevel=0.03)
    # A-frames holding the wheel axle
    for y in(-ya,ya):
        for x in(-2.15,0.15):
            ind_beam(k,(x,y,0.28),(ax.x+(0.12 if x>ax.x else -0.12),y,ax.z+0.15),0.2,0.2,WOOD,bevel=0.03)
        k.box((ax.x,y,ax.z+0.2),(0.5,0.26,0.22),WOOD,bevel=0.03)
        k.box((ax.x,y,1.0),(1.95,0.14,0.14),WOOD,bevel=0.02)
    _cyl(k,tuple(ax),0.1,0.1,2*ya+0.3,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
    _cyl(k,(ax.x,0.86,ax.z),0.2,0.2,0.3,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))     # rope drum
    # mast (A-frame 5.5) with front struts
    mx=1.05
    for y in(-0.35,0.35):
        ind_beam(k,(mx,y*3.4,0.3),(mx,y,5.5),0.26,0.26,WOOD,bevel=0.04)
    k.box((mx,0,5.55),(0.34,0.9,0.3),WOOD,bevel=0.04)
    for y in(-0.35,0.35): ind_beam(k,(2.8,0,0.3),(mx+0.1,y*0.8,3.3),0.18,0.18,WOOD,bevel=0.03)
    for z in(1.6,3.1): k.box((mx,0,z),(0.18,2.4-z*0.4,0.16),WOOD,bevel=0.02)
    # jib: pivot z 4.5, 7 m at 40 deg -> tip at ~9 m, braced from the mast
    piv=Vector((mx+0.05,0,4.5)); a=math.radians(40); tip=piv+Vector((7.0*math.cos(a),0,7.0*math.sin(a)))
    for y in(-0.13,0.13): ind_beam(k,piv+Vector((0,y,0)),tip+Vector((0,y,0)),0.14,0.26,WOOD,bevel=0.03)
    for t in(0.2,0.45,0.7,0.92):
        p=piv+(tip-piv)*t; k.box(tuple(p),(0.16,0.4,0.14),WOOD,rot=(0,-a,0),bevel=0.02)
    mid=piv+(tip-piv)*0.45
    for y in(-0.2,0.2): ind_beam(k,(mx+0.12,y,2.7),mid+Vector((0,y,-0.1)),0.16,0.16,WOOD,bevel=0.03)
    _cyl(k,tuple(tip+Vector((0.05,0,-0.05))),0.18,0.18,0.1,12,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    # ropes (HAY coloured): drum -> mast pulley -> along the jib -> tip -> hook
    ind_rod(k,(ax.x+0.12,0.86,ax.z+0.18),(mx-0.1,0.1,4.3),0.03,HAY,segs=5)
    ind_rod(k,(mx-0.1,0.1,4.3),piv+Vector((0.15,0,0.25)),0.03,HAY,segs=5)
    ind_rod(k,piv+Vector((0.15,0,0.25)),tip+Vector((-0.05,0,0.18)),0.03,HAY,segs=5)
    hz=2.5; hx=tip.x+0.2
    ind_rod(k,tip+Vector((0.2,0,-0.05)),(hx,0,hz+0.3),0.035,HAY,segs=5)
    k.box((hx,0,hz+0.32),(0.18,0.14,0.26),WOOD,bevel=0.03)
    ring(k,(hx,0,hz+0.1),0.06,0.12,0.05,IRON,n=10,axis="Y")
    bz=hz-0.95
    k.box((hx,0,bz),(0.8,0.6,0.5),ASHLAR,rot=(0,0,0.1),bevel=0.04)
    for s in(-1,1): ind_rod(k,(hx,0,hz+0.02),(hx+s*0.36,0,bz+0.24),0.022,HAY,segs=4)
    # back stays to ground stakes
    for s in(-1,1):
        st=Vector((-2.3,s*1.9,0.0))
        k.box(tuple(st+Vector((0,0,0.2))),(0.14,0.14,0.5),WOOD,rot=(0.2*s,0,0),bevel=0.02)
        ind_rod(k,(mx-0.05,s*0.3,5.6),st+Vector((0,0,0.4)),0.028,HAY,segs=5)
def ind_crane_wheel(k):
    """treadwheel r 1.8, origin on the axle, spins about local Y (spin_axis='local Y')"""
    for y in(-0.6,0.6):
        ring(k,(0,y,0),1.6,1.8,0.12,WOOD,n=28,axis="Y")
        for i in range(8):
            a=i*math.pi/4+0.2
            ind_beam(k,(math.cos(a)*0.22,y,math.sin(a)*0.22),(math.cos(a)*1.65,y,math.sin(a)*1.65),0.1,0.1,WOOD,bevel=0.02)
        _cyl(k,(0,y,0),0.26,0.26,0.2,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
        ring(k,(0,y+(0.07 if y>0 else -0.07),0),1.64,1.76,0.03,IRON,n=28,axis="Y")
    for i in range(16):
        a=2*math.pi*(i+0.5)/16
        k.box((math.cos(a)*1.56,0,math.sin(a)*1.56),(0.28,1.34,0.08),PLANKS,rot=(0,-(a+math.pi/2),0),bevel=0.015)

# ================================================================ IRON
def ind_log(k,a,b,r,seed=0,bark=BARK_OAK):
    """short log with end-grain caps from a to b"""
    ind_rod(k,a,b,r,bark,segs=7,r2=r*0.92)
    a=Vector(a); b=Vector(b); d=(b-a).normalized()
    q=Vector((0,0,1)).rotation_difference(d).to_matrix().to_4x4()
    for p in (a-d*0.005,b+d*0.005):
        vs=_cyl(k,tuple(p),r*0.9,r*0.9,0.012,7,ENDGRAIN,rot=q)
        ind_box_uv(k,ind_faces(vs),0.5,(seed*0.31%1,seed*0.17%1))
def ind_flames(k,c,n=3,h=0.4,r=0.1,seed=0):
    """small cluster of GLOW flame cones (toggle 'working' in Unity through the GLOW material)"""
    rnd=random.Random(seed)
    for i in range(n):
        a=2*math.pi*i/n+rnd.uniform(-.3,.3); d=r*0.9 if n>1 else 0
        hh=h*rnd.uniform(0.7,1.1)
        lathe(k,[(r*rnd.uniform(0.8,1.1),0.0),(r*0.65,hh*0.45),(0.0,hh)],center=(c[0]+math.cos(a)*d,c[1]+math.sin(a)*d,c[2]),segs=5,mi=GLOW)
def ind_charcoal_mound(k):
    """charcoal clamp: turf-patched earth dome (r 2.0, h 1.45) on a ring of stacked log ends; 4 shoulder vents + top vent glow.
       Sockets: Smoke at the vents (r 1.0 at 90 deg steps, z~1.2) and the top (0,0,1.5)."""
    vs=ind_heap(k,(0,0,0.26),1.85,1.8,1.2,SOIL,seed=3,sub=3,rough=0.06,peak=0.72,tile=1.6)
    bvh=ind_bvh(k); rnd=random.Random(7)
    # turf sods
    for i in range(15):
        a=rnd.uniform(0,2*math.pi); d=rnd.uniform(0.25,1.55)
        x,y=math.cos(a)*d,math.sin(a)*d; z=ind_drop(bvh,x,y)
        nrm=Vector((x/1.6,y/1.6,1.0)).normalized()
        sub=Kit(); sub.box((0,0,0),(rnd.uniform(0.4,0.75),rnd.uniform(0.35,0.55),0.07),MOSS,bevel=0.03,jitter=0.035,seed=i)
        q=Vector((0,0,1)).rotation_difference(nrm).to_matrix().to_4x4()
        merge_kit(k,sub,Matrix.Translation((x,y,z-0.015))@q@Matrix.Rotation(rnd.uniform(0,6),4,"Z"))
    # vents
    for i in range(5):
        if i<4: a=i*math.pi/2+0.5; x,y=math.cos(a)*0.95,math.sin(a)*0.95
        else: x,y=0.0,0.0
        z=ind_drop(bvh,x,y)
        nrm=Vector((x/1.4,y/1.4,1.0)).normalized(); q=Vector((0,0,1)).rotation_difference(nrm).to_matrix().to_4x4()
        sub=Kit(); r=0.12 if i<4 else 0.2
        ring(sub,(0,0,0.03),r,r+0.09,0.1,SOIL,n=8,axis="Z")
        _cyl(sub,(0,0,-0.01),r,r,0.04,8,VOID)
        _ico(sub,(0,0,-0.01),r*0.6,GLOW,(1,1,0.45),sub=1)
        merge_kit(k,sub,Matrix.Translation((x,y,z))@q)
    # ring of log ends round the foot (the stacked wood inside the clamp)
    for layer,(z,n,r0) in enumerate(((0.13,22,1.98),(0.34,20,1.9))):
        for i in range(n):
            a=2*math.pi*(i+0.5*layer)/n+rnd.uniform(-0.05,0.05); rr=rnd.uniform(0.1,0.13)
            p0=Vector((math.cos(a)*(r0-0.5),math.sin(a)*(r0-0.5),z)); p1=Vector((math.cos(a)*r0,math.sin(a)*r0,z-0.02))
            ind_rod(k,p0,p1,rr,BARK_OAK,segs=6)
            d=(p1-p0).normalized(); q=Vector((0,0,1)).rotation_difference(d).to_matrix().to_4x4()
            cvs=_cyl(k,tuple(p1+d*0.006),rr*0.9,rr*0.9,0.01,6,ENDGRAIN,rot=q)
            ind_box_uv(k,ind_faces(cvs),0.45,(i*0.37%1,layer*0.5))
    # ladder and rake
    for s in(-0.22,0.22): ind_beam(k,(2.35,s+0.4,0.0),(1.0,s+0.3,1.3),0.06,0.07,WOOD,bevel=0.01)
    for j in range(5):
        t=(j+0.6)/6; k.box((2.35-1.35*t,0.4-0.1*t,1.3*t),(0.05,0.5,0.05),WOOD,bevel=0.01)
    ind_beam(k,(-1.4,-2.0,0.02),(-2.2,-0.7,1.35),0.05,0.05,WOOD,bevel=0.01)
    k.box((-1.38,-2.03,0.06),(0.5,0.08,0.06),WOOD,rot=(0,0,-1.0),bevel=0.01)
    ind_skirt(k,-1.6,1.6,-1.6,1.6,mi=SOIL)
def ind_bloomery(k):
    """squat clay shaft furnace (lathe r 1.3 -> 0.55, 3.2 m) on a rubble base: glowing tap arch at -Y (Fire socket),
       flames at the throat (Smoke socket at (0,0,3.3)), clay tuyere at +X for the bellows, charging ladder at +Y"""
    ind_lathe(k,[(1.32,-0.6),(1.32,0.0),(1.3,0.5),(1.24,0.92)],segs=16,mi=STONE,tile=3.0,around=3)
    ind_lathe(k,[(1.22,0.9),(1.2,1.35),(1.05,1.95),(0.8,2.5),(0.6,2.95),(0.66,3.1),(0.7,3.2),(0.52,3.22),(0.46,3.0)],segs=16,mi=CLAY,tile=1.5)
    _cyl(k,(0,0,3.02),0.47,0.47,0.04,12,GLOW)
    ind_flames(k,(0,0,3.03),n=3,h=0.55,r=0.14,seed=2)
    ring(k,(0,0,1.28),1.2,1.26,0.1,IRON,n=16,axis="Z"); ring(k,(0,0,2.28),0.9,0.95,0.1,IRON,n=16,axis="Z")
    rnd=random.Random(4)
    for i in range(7):   # clay daub patches break the smooth silhouette
        a=rnd.uniform(0,2*math.pi); z=rnd.uniform(1.1,2.7); r=1.2-(z-1.0)*0.36
        _ico(k,(math.cos(a)*r,math.sin(a)*r,z),rnd.uniform(0.14,0.22),CLAY,(1.3,1.3,0.55),sub=1,jit=0.02,seed=i)
    for i in range(12):  # base rocks
        a=2*math.pi*(i+0.5)/12
        if abs(a-1.5*math.pi)<0.5: continue
        rock(k,(math.cos(a)*1.3,math.sin(a)*1.3,0.2+0.26*(i%2)),(0.52,0.36,0.38),seed=20+i,rot_z=a,mi=STONE_BLOCK,segs=1)
    # tap arch (front, -Y): recessed glowing mouth
    hw=0.34; zs=0.18; ya=-1.26; hz=0.32
    pts=[(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+hz+math.sin(math.pi*j/8)*hw) for j in range(9)]+[(-hw,zs)]
    f=k.bm.faces.new([k.bm.verts.new((x,ya+0.06,z)) for x,z in pts]); f.material_index=GLOW; k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    k.project([f],GLOW)
    for j in range(len(pts)-1):   # dark reveal around the glow
        (x0,z0),(x1,z1)=pts[j],pts[j+1]
        q=[k.bm.verts.new(p) for p in ((x0,ya-0.02,z0),(x1,ya-0.02,z1),(x1,ya+0.06,z1),(x0,ya+0.06,z0))]
        ff=k.bm.faces.new(q); ff.material_index=VOID
    k.bm.normal_update()
    for j in range(7):
        a=math.pi*(j+0.5)/7
        k.box((math.cos(a)*(hw+0.12),ya-0.07,zs+hz+math.sin(a)*(hw+0.12)),(0.18,0.24,0.24),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.03)
    for s in(-1,1): k.box((s*(hw+0.12),ya-0.07,zs+hz/2),(0.2,0.24,hz+0.1),STONE_BLOCK,bevel=0.03)
    # slag run and bloom lumps in front
    ind_heap(k,(0.05,-1.7,0.0),0.5,0.4,0.13,COAL,seed=9,sub=2)
    k.box((0,-1.45,0.05),(0.18,0.55,0.05),GLOW,bevel=0.02)
    for i in range(4): _ico(k,(0.7+0.2*i,-1.6+0.12*(i%2),0.09),0.11,IRON,(1.2,1,0.8),sub=1,jit=0.02,seed=i)
    # tuyere (clay pipe) at +X where the bellows attach
    _cyl(k,(1.45,0,0.62),0.11,0.14,0.5,8,CLAY,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # charging ladder at the back
    for s in(-0.25,0.25): ind_beam(k,(-0.25+s,2.0,0.0),(-0.1+s,0.75,3.05),0.07,0.07,WOOD,bevel=0.01)
    for j in range(8):
        t=(j+0.6)/9; k.box((-0.18,2.0-1.25*t,3.05*t),(0.55,0.05,0.05),WOOD,bevel=0.01)
    ind_skirt(k,-1.25,1.25,-1.25,1.25)
def ind_bellows(k):
    """pair of leather bellows on a trestle, nozzle toward -X (points at a tuyere), with a pump lever"""
    k.box((0.1,0,0.3),(1.2,0.6,0.08),PLANKS,bevel=0.02)
    for x in(-0.35,0.55):
        for y in(-0.25,0.25): k.box((x,y,0.14),(0.08,0.08,0.3),WOOD,bevel=0.02)
    # bellows body: bottom board, leather bag (pleated), top board
    zb=0.36; L=1.0
    for i,(z,s) in enumerate(((zb,1.0),(zb+0.1,1.06),(zb+0.2,1.0),(zb+0.3,1.06),(zb+0.4,1.0))):
        sub=Kit(); vs=sub.box((0,0,0),(L*s,0.62*s,0.12),HIDE,bevel=0.04,segs=1)
        for v in set(vs):   # wedge: narrow at the nozzle end (-X)
            t=(v.co.x+L/2)/L; v.co.y*=0.35+0.65*t; v.co.z*=0.3+0.7*t
        merge_kit(k,sub,Matrix.Translation((0.05,0,z+0.06-0.02*i)))
    for z in(zb-0.01,zb+0.53):
        sub=Kit(); vs=sub.box((0,0,0),(L+0.08,0.66,0.05),WOOD,bevel=0.015)
        for v in set(vs): t=(v.co.x+L/2)/L; v.co.y*=0.4+0.6*t
        merge_kit(k,sub,Matrix.Translation((0.05,0,z))@Matrix.Rotation(0.1 if z>0.5 else 0,4,"Y"))
    ind_rod(k,(-0.45,0,0.52),(-0.95,0,0.5),0.05,IRON,segs=8,r2=0.03)
    # handle + lever post
    k.box((0.72,0,0.95),(0.3,0.08,0.06),WOOD,bevel=0.01)
    k.box((0.95,0.42,0.6),(0.12,0.12,1.2),WOOD,bevel=0.02)
    ind_beam(k,(0.95,0.36,1.15),(0.2,0.0,0.96),0.07,0.07,WOOD,bevel=0.01)
    ind_rod(k,(0.62,0,0.92),(0.6,0,1.08),0.02,HAY,segs=4)

# ================================================================ CLAY
def ind_bottle_kiln(k):
    """bottle kiln (lathe 2.2 -> 0.8 at 6.0) with iron bonts, fire mouths (GLOW) and a clammins door at -Y.
       Sockets: Smoke at the top (0,0,6.3), Fire at the 5 fire mouths."""
    prof=[(2.25,-0.6),(2.25,0.0),(2.3,0.7),(2.3,1.5),(2.18,2.6),(2.0,3.5),(1.6,4.3),(1.1,5.0),(0.9,5.6),(0.8,6.0),(0.95,6.12),(0.95,6.3),(0.72,6.3),(0.7,5.9)]
    ind_lathe(k,prof,segs=20,mi=CLAY,tile=1.5)
    _cyl(k,(0,0,5.95),0.7,0.7,0.05,16,VOID)
    ind_lathe(k,[(2.5,-0.6),(2.5,0.3),(2.38,0.42),(2.22,0.42)],segs=20,mi=STONE_BLOCK,tile=1.2)   # plinth
    # iron bonts following the profile
    def rad(z):
        for (r0,z0),(r1,z1) in zip(prof[1:],prof[2:]):
            if z0<=z<=z1: return r0+(r1-r0)*(z-z0)/(z1-z0)
        return prof[1][0]
    for z in(1.0,1.9,2.8,3.6,4.4,5.2):
        r=rad(z); ring(k,(0,0,z),r-0.01,r+0.05,0.09,IRON,n=20,axis="Z")
    # fire mouths around the base: arched GLOW openings with brick surrounds
    for i in range(6):
        a=-math.pi/2+2*math.pi*i/6
        if i==0: continue
        sub=Kit(); hw=0.26; zs=0.5; ya=-2.33
        pts=[(hw,zs)]+[(math.cos(math.pi*j/6)*hw,zs+0.22+math.sin(math.pi*j/6)*hw) for j in range(7)]+[(-hw,zs)]
        f=sub.bm.faces.new([sub.bm.verts.new((x,ya,z)) for x,z in pts]); f.material_index=GLOW; sub.bm.normal_update()
        if f.normal.y>0: f.normal_flip()
        sub.project([f],GLOW)
        for j in range(5):
            aa=math.pi*(j+0.5)/5
            sub.box((math.cos(aa)*(hw+0.09),ya-0.05,zs+0.22+math.sin(aa)*(hw+0.09)),(0.15,0.16,0.14),CLAY,rot=(0,-(aa-math.pi/2),0),bevel=0.02)
        sub.box((0,ya-0.12,zs-0.06),(0.8,0.3,0.12),STONE_BLOCK,bevel=0.02)
        merge_kit(k,sub,Matrix.Rotation(a+math.pi/2,4,"Z"))
    # clammins (bricked-up loading door) with a wooden door at -Y
    hw=0.62; zs=1.35; y=-2.36
    k.quad([(-hw,y,0.42),(hw,y,0.42),(hw,y,zs),(-hw,y,zs)],PLANKS,uvs=[(0,0),(1.24,0),(1.24,0.93),(0,0.93)])
    pts=[(math.cos(math.pi*j/8)*hw,zs+math.sin(math.pi*j/8)*hw*0.8) for j in range(9)]
    f=k.bm.faces.new([k.bm.verts.new((x,y,z)) for x,z in pts]); f.material_index=PLANKS; k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    k.project([f],PLANKS)
    for j in range(9):
        aa=math.pi*(j+0.5)/9
        k.box((math.cos(aa)*(hw+0.12),y-0.04,zs+math.sin(aa)*(hw*0.8+0.12)),(0.2,0.2,0.18),CLAY,rot=(0,-(aa-math.pi/2),0),bevel=0.02)
    for s in(-1,1): k.box((s*(hw+0.12),y-0.04,0.9),(0.22,0.2,0.95),CLAY,bevel=0.02)
    for z in(0.75,1.3): k.box((0,y-0.03,z),(1.1,0.03,0.08),IRON,bevel=0.01)
    k.box((0,y-0.35,0.47),(1.5,0.7,0.1),STONE_BLOCK,bevel=0.03)
def ind_clay_pit(k):
    """3x3 cell clay digging: wet clay floor, spoil banks, puddles, spade, plank walkway, basket of lumps"""
    rnd=random.Random(3)
    vs=k.box((0,0,-0.29),(2.9,2.9,0.6),CLAY,bevel=0)
    grid_cut(k,vs,0.5)
    for v in k.bm.verts:
        if abs(v.co.z-0.01)<0.02 and abs(v.co.x)<1.4 and abs(v.co.y)<1.4:
            v.co.z-=0.06*(1-max(abs(v.co.x),abs(v.co.y))/1.45)+0.02*noise.noise(v.co*1.3)
    for v in k.bm.verts:   # ragged outline instead of a square slab
        if max(abs(v.co.x),abs(v.co.y))>1.4 and v.co.z>-0.1:
            d=0.12*noise.noise(Vector((v.co.x*1.7,v.co.y*1.7,0.3)))-0.05
            v.co.x*=1+d/1.45; v.co.y*=1+d/1.45
    # spoil banks along two edges, low turf-and-soil lips on the other two (reads as a dug hollow)
    ind_heap(k,(-0.6,1.2,0),1.2,0.4,0.42,CLAY,seed=5,sub=2,rough=0.2)
    ind_heap(k,(1.2,0.3,0),0.4,1.0,0.3,SOIL,seed=6,sub=2,rough=0.2,jit=0.05)
    ind_chunks(k,(1.2,0.3,0),0.35,0.9,0.3,7,[CLAY,SOIL,CLAY],seed=31,size=(0.08,0.14))
    for i,(x,y,rx,ry,h) in enumerate(((0.0,-1.5,1.75,0.3,0.14),(-1.5,0.0,0.3,1.7,0.13),(1.2,1.5,0.5,0.28,0.12),(1.5,-1.15,0.3,0.55,0.12))):
        ind_heap(k,(x,y,0),rx,ry,h,MOSS,seed=7+i,sub=2,rough=0.22,tile=2.0)   # turf lips hide the slab edge
    for i,(x,y) in enumerate(((0.9,-1.55),(-0.3,-1.6),(-1.6,-1.0),(-1.55,0.9),(1.55,-1.2))): ind_tuft(k,(x,y,0.08),0.4,seed=20+i)
    ind_chunks(k,(-0.6,1.2,0),1.1,0.35,0.4,6,[SOIL,CLAY],seed=12,size=(0.1,0.18))
    for i,(x,y) in enumerate(((-1.2,1.3),(0.2,1.35),(1.3,-0.4),(1.35,0.9),(-1.35,-1.3))): ind_tuft(k,(x,y,0.12),0.45,seed=i)
    # puddles (sit just above the dished clay)
    bvh=ind_bvh(k)
    for (x,y,r) in((-0.6,-0.5,0.5),(0.4,-0.9,0.3)):
        zp=max(ind_drop(bvh,x+dx,y+dy) for dx in(-r,0,r) for dy in(-r,0,r))+0.008
        f=k.bm.faces.new([k.bm.verts.new((x+math.cos(a)*r*1.3,y+math.sin(a)*r,zp)) for a in [2*math.pi*i/10 for i in range(10)]])
        f.material_index=WATER; k.bm.normal_update()
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    # cut steps (dug blocks of clay) and lumps
    for i in range(3): k.box((0.2+i*0.35,0.55,0.08),(0.3,0.3,0.22),CLAY,rot=(0,0,rnd.uniform(-.3,.3)),bevel=0.05,jitter=0.02,seed=i)
    # plank walkway + spade + basket
    for i in range(2): k.box((-0.2+i*0.02,-0.1+i*0.26,0.04),(1.95,0.24,0.05),PLANKS,rot=(0,0,0.05),bevel=0.01)
    ind_beam(k,(0.75,-0.25,-0.1),(0.62,-0.45,1.05),0.05,0.05,WOOD,bevel=0.01)
    k.box((0.62,-0.45,1.08),(0.2,0.05,0.05),WOOD,rot=(0,0,-0.9),bevel=0.01)
    k.box((0.77,-0.23,0.05),(0.22,0.04,0.3),STEEL,rot=(0.1,0,-0.9),bevel=0.02)
    _cyl(k,(-1.05,-0.95,0.18),0.24,0.3,0.36,10,WATTLE)
    for i in range(5): _ico(k,(-1.05+rnd.uniform(-.14,.14),-0.95+rnd.uniform(-.14,.14),0.37),0.1,CLAY,(1.2,1,0.8),sub=1,jit=0.02,seed=i)
def ind_potters_wheel(k):
    """kick wheel with a seat, a pot being thrown, finished pots on a board. Work socket at the seat (0,0.45)"""
    k.box((0,0.45,0.5),(0.8,0.36,0.06),PLANKS,bevel=0.015)             # seat
    for x in(-0.34,0.34):
        for y in(-0.35,0.55): k.box((x,y,0.3),(0.08,0.08,0.6),WOOD,bevel=0.015)
    for y in(-0.35,0.55): k.box((0,y,0.12),(0.76,0.07,0.07),WOOD,bevel=0.01)
    k.box((0,-0.35,0.62),(0.8,0.3,0.06),PLANKS,bevel=0.015)            # work table
    _cyl(k,(0,-0.05,0.13),0.34,0.34,0.1,16,STONE_BLOCK)                 # kick wheel
    _cyl(k,(0,-0.05,0.45),0.03,0.03,0.72,6,IRON)
    _cyl(k,(0,-0.05,0.8),0.2,0.2,0.04,14,WOOD)                          # wheel head
    ind_lathe(k,[(0.0,0.82),(0.09,0.82),(0.13,0.88),(0.14,0.95),(0.1,1.02),(0.08,1.06),(0.06,1.04)],c=(0,-0.05,0),segs=12,mi=CLAY,smooth=True)
    # finished pots on a side board
    k.box((0.75,-0.15,0.35),(0.4,0.7,0.05),PLANKS,bevel=0.01)
    for y in(-0.4,0.1): k.box((0.75,y,0.17),(0.35,0.06,0.34),WOOD,bevel=0.01)
    for i,(y,h) in enumerate(((-0.35,0.3),(-0.05,0.22),(0.15,0.26))):
        ind_lathe(k,[(0.0,0.38),(0.07,0.38),(0.11,0.38+h*0.4),(0.07,0.38+h*0.85),(0.08,0.38+h)],c=(0.75,y,0),segs=10,mi=CLAY,smooth=True)
    ind_heap(k,(-0.55,-0.4,0.0),0.22,0.2,0.2,CLAY,seed=2,sub=1)       # lump of prepared clay
def ind_brick_stack(k,c,courses,rotz=0.0,seed=0,pallet=True):
    """pallet stack of CLAY bricks 0.26x0.13x0.08, alternate courses crossed; hidden joints merged"""
    sub=Kit(); L,W,H=0.26,0.13,0.08; gp=0.012; X=3*L; Y=4*W
    rnd=random.Random(seed)
    z0=0.13 if pallet else 0.0
    if pallet:
        for y in(-Y/2+0.06,Y/2-0.06): sub.box((0,y,0.035),(X+0.1,0.1,0.07),WOOD,bevel=0)
        for i in range(4): sub.box((-X/2+0.08+i*(X-0.16)/3,0,0.09),(0.13,Y+0.08,0.03),PLANKS,bevel=0)
    for cz in range(courses):
        z=z0+cz*(H+0.006)+H/2; top=cz==courses-1
        if cz%2==0:   # bricks along X: 3 x 4 rows (inner courses: 3 full-depth blocks, joints show on the long faces)
            if not top:
                for i in range(3): sub.box((-X/2+(i+0.5)*L,0,z),(L-gp,Y-gp,H),CLAY,bevel=0)
                continue
            for j in range(4):
                y=-Y/2+(j+0.5)*W
                for i in range(3): sub.box((-X/2+(i+0.5)*L+rnd.uniform(-.008,.008),y,z),(L-gp,W-gp,H),CLAY,rot=(0,0,rnd.uniform(-.03,.03)),bevel=0)
        else:         # bricks along Y: 6 columns of 2
            for i in range(6):
                x=-X/2+(i+0.5)*X/6
                if not top: sub.box((x,0,z),(X/6-gp,Y-gp,H),CLAY,bevel=0)
                else:
                    for j in range(2): sub.box((x,-Y/4+j*Y/2,z),(X/6-gp,Y/2-gp,H),CLAY,rot=(0,0,rnd.uniform(-.03,.03)),bevel=0)
    merge_kit(k,sub,Matrix.Translation(Vector(c))@Matrix.Rotation(rotz,4,"Z"))
def ind_pile_bricks(k,size=1):
    rnd=random.Random(size*5)
    if size==1: ind_brick_stack(k,(0,0,0),6,0.05,seed=1)
    elif size==2:
        ind_brick_stack(k,(-0.45,0,0),7,0.04,seed=2); ind_brick_stack(k,(0.48,0.05,0),4,-0.06,seed=3)
    else:
        ind_brick_stack(k,(-0.9,0,0),7,0.03,seed=4); ind_brick_stack(k,(0.0,0.05,0),6,-0.05,seed=5); ind_brick_stack(k,(0.9,-0.05,0),3,0.08,seed=6)
    for i in range(2+size):   # loose and broken bricks
        k.box((rnd.uniform(-0.6,0.6)*size,-0.55-rnd.uniform(0,0.3),0.04),(0.26 if i%2 else 0.15,0.13,0.08),CLAY,rot=(0,0,rnd.uniform(0,3)),bevel=0.005)

# ================================================================ LEATHER AND CLOTH
def ind_ngon(k,pts,mi,two_sided=True,off=(0,0.012,0),uv_scale=1.0):
    """planar polygon (front + back copy), UVs from x/z"""
    fs=[]
    vs=[k.bm.verts.new(p) for p in pts]; f=k.bm.faces.new(vs); f.material_index=mi; fs.append(f)
    if two_sided:
        vb=[k.bm.verts.new(Vector(p)+Vector(off)) for p in pts]; f2=k.bm.faces.new(vb[::-1]); f2.material_index=mi; fs.append(f2)
    k.bm.normal_update()
    for ff in fs:
        for l in ff.loops: l[k.uv].uv=(l.vert.co.x*uv_scale,l.vert.co.z*uv_scale+l.vert.co.y*uv_scale)
    return fs
def ind_pelt_outline(w,h,seed=0,n=28):
    """animal-hide outline in the XZ plane, centred at 0: body with 4 leg lobes, neck and tail"""
    rnd=random.Random(seed); pts=[]
    for i in range(n):
        a=2*math.pi*i/n
        r=1.0+0.28*max(0,math.cos(2*(a-math.pi/4)))**6+0.28*max(0,math.cos(2*(a+math.pi/4)))**6   # legs on the diagonals
        r+=0.18*max(0,math.cos(a-math.pi/2))**12+0.1*max(0,math.cos(a+math.pi/2))**14            # neck (top) / tail (bottom)
        r*=1+rnd.uniform(-0.04,0.04)
        pts.append((math.cos(a)*w/2*r*0.85,math.sin(a)*h/2*r*0.85))
    return pts
def ind_pelt(k,w,h,mi,seed=0,z_fn=None,thick=0.014,M=None):
    """hide as a small radial mesh (centre + 2 rings) in the XY plane, draped by z_fn(x,y); two-sided"""
    out=ind_pelt_outline(w,h,seed); rings=[[(0.0,0.0)],[(x*0.55,y*0.55) for x,y in out],out]
    zf=z_fn or (lambda x,y: 0.0)
    sub=Kit(); n=len(out)
    for side in(0,1):
        dz=-thick if side else 0.0
        V=[[sub.bm.verts.new((x,y,zf(x,y)+dz)) for (x,y) in r] for r in rings]
        fs=[]
        for i in range(n):
            j=(i+1)%n
            q=[(V[0][0],V[1][i],V[1][j]),(V[1][i],V[2][i],V[2][j],V[1][j])]
            for t in q:
                fs.append(sub.bm.faces.new(t if side==0 else t[::-1]))
        for f in fs:
            f.material_index=mi
            for l in f.loops: l[sub.uv].uv=(l.vert.co.x*0.8,l.vert.co.y*0.8)
    sub.bm.normal_update()
    merge_kit(k,sub,M or Matrix.Identity(4))
def ind_tanning_pit(k):
    """one tanning pit: stone-kerbed 1.2x1.2 pit of tan liquor (HIDE), a hide soaking, pole across. Work socket at -Y"""
    rnd=random.Random(2); A=0.6; T=0.32
    for i,(x,y,sx,sy) in enumerate(((0,-A-T/2,2*A+2*T,T),(0,A+T/2,2*A+2*T,T),(-A-T/2,0,T,2*A),(A+T/2,0,T,2*A))):
        n=3 if sx>sy else 2; L=max(sx,sy)
        for j in range(n):
            c=-L/2+(j+0.5)*L/n
            k.box((x+(c if sx>sy else 0),y+(c if sy>sx else 0),0.14),((L/n-0.03) if sx>sy else sx,(L/n-0.03) if sy>sx else sy,0.3),STONE_BLOCK,
                  rot=(0,0,rnd.uniform(-.03,.03)),bevel=0.04,jitter=0.015,seed=i*5+j)
    k.box((0,0,-0.35),(2*A+0.05,2*A+0.05,0.7),VOID,bevel=0)          # dark pit well (hidden sides)
    k.quad([(-A,-A,0.14),(A,-A,0.14),(A,A,0.14),(-A,A,0.14)],BRONZE,uvs=[(0,0),(1,0),(1,1),(0,1)])   # tan liquor (glossy oak-bark brown)
    # a hide soaking, one end pulled up over the kerb and hanging outside
    def zf(x,y):
        if y<0.3: return 0.16
        if y<0.62: return 0.16+(y-0.3)*0.55
        return 0.34-(y-0.62)*1.4
    ind_pelt(k,0.95,1.35,HIDE,seed=3,z_fn=zf,M=Matrix.Translation((0.05,0.25,0))@Matrix.Rotation(0.12,4,"Z"))
    for i,(x,y) in enumerate(((-0.95,-0.9),(0.95,0.95),(1.0,-0.5))): ind_tuft(k,(x,y,0.0),0.4,seed=80+i)
    ind_beam(k,(-1.0,0.2,0.34),(1.05,-0.4,0.34),0.07,0.07,WOOD,bevel=0.01)   # stirring pole
    ind_skirt(k,-A-T,A+T,-A-T,A+T,mi=STONE_BLOCK)
def ind_hide_frame(k):
    """1.4 x 1.8 lashed pole frame with a laced, stretched hide; leans back on two props (faces -Y)"""
    W,H=1.4,1.8; tilt=0.22; z0=0.1
    M=Matrix.Translation((0,0,z0))@Matrix.Rotation(-tilt,4,"X")
    sub=Kit()
    for x in(-W/2,W/2): ind_rod(sub,(x,0,-0.12),(x,0,H+0.15),0.05,WOOD,segs=6)
    for z in(0.0,H): ind_rod(sub,(-W/2-0.15,0,z),(W/2+0.15,0,z),0.045,WOOD,segs=6)
    for x in(-W/2,W/2):
        for z in(0.0,H): _cyl(sub,(x,0,z),0.065,0.065,0.1,6,HAY,rot=Matrix.Rotation(math.pi/2,4,"X"))
    pts=[(x,-0.02,z+H/2) for (x,z) in ind_pelt_outline(W*0.82,H*0.8,seed=5)]
    ind_ngon(sub,pts,HIDE,off=(0,0.015,0),uv_scale=0.8)
    # lacing: from every 3rd outline point to the nearest frame member
    for i,(x,y,z) in enumerate(pts):
        if i%2: continue
        cands=[(-W/2,z),(W/2,z),(x,0.0),(x,H)]
        tx,tz=min(cands,key=lambda c:(c[0]-x)**2+(c[1]-z)**2)
        ind_rod(sub,(x,-0.02,z),(tx,0,tz),0.012,HAY,segs=4)
    merge_kit(k,sub,M)
    # props behind
    for x in(-W/2+0.05,W/2-0.05): ind_beam(k,(x,0.75,0.0),(x,0.28,1.75),0.07,0.07,WOOD,bevel=0.01)
    for x in(-W/2,W/2): rock(k,(x,-0.05,0.08),(0.28,0.24,0.18),seed=int(x*10)+20,mi=STONE_BLOCK,segs=1)
def ind_dye_vat(k):
    """stave vat r 0.6 x 0.8 with iron hoops; dye liquor + draped cloth in CLOTH_A (style {'cloth':'Blue'} recolours it)"""
    R=0.6; H=0.8; n=16; rnd=random.Random(1)
    for i in range(n):
        a=2*math.pi*i/n; hh=H+rnd.uniform(-0.02,0.05)
        k.box((math.cos(a)*R,math.sin(a)*R,hh/2+0.06),(0.09,2*math.pi*R/n+0.01,hh),WOOD,rot=(0,0,a),bevel=0.015)
    _cyl(k,(0,0,0.12),R-0.02,R-0.02,0.1,n,WOOD)
    for z in(0.22,0.72): ring(k,(0,0,z),R+0.035,R+0.075,0.07,IRON,n=n,axis="Z")
    lathe(k,[(R-0.03,0.74),(0.0,0.74)],segs=n,mi=CLOTH_A)
    for f in k.bm.faces:
        if f.material_index==CLOTH_A:
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    # bearers
    for y in(-0.3,0.3): k.box((0,y,0.05),(1.45,0.14,0.1),WOOD,bevel=0.02)
    # cloth draped over the rim, hanging outside (-Y side)
    pts=[(-0.3,0.76),(-0.5,0.87),(-0.62,0.91),(-0.7,0.85),(-0.72,0.6),(-0.7,0.33)]
    for side in(0,1):
        vs=[]
        for j,(y,z) in enumerate(pts):
            for x in(-0.28,0.28):
                vs.append(k.bm.verts.new((x+0.03*math.sin(j*1.3),y+(0.012 if side else 0),z-(0.012 if side else 0))))
        for j in range(len(pts)-1):
            q=[vs[2*j],vs[2*j+1],vs[2*j+3],vs[2*j+2]]
            f=k.bm.faces.new(q if side==0 else q[::-1]); f.material_index=CLOTH_A; f.smooth=True
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z+l.vert.co.y)
    k.bm.normal_update()
    # stirring pole
    ind_beam(k,(0.1,0.1,0.35),(0.55,0.6,1.6),0.05,0.05,WOOD,bevel=0.01)
    # dye splashes on the ground
    for (x,y,r) in((-0.75,-0.35,0.14),(0.5,-0.75,0.1)):
        f=k.bm.faces.new([k.bm.verts.new((x+math.cos(a)*r,y+math.sin(a)*r*0.7,0.008)) for a in [2*math.pi*i/8 for i in range(8)]])
        f.material_index=CLOTH_A
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    k.bm.normal_update()
def ind_strip(k,x,y,top,w,L,mi,seed=0,over=True,sway=0.05):
    """cloth strip folded over a pole at (x,y,top): two double-sided layers, gently waving"""
    rnd=random.Random(seed); nz=6
    layers=[(-0.045,L),(0.045,L*rnd.uniform(0.55,0.8))] if over else [(0.0,L)]
    for (dy,Lx) in layers:
        for side in(0,1):
            vs=[]
            for j in range(nz+1):
                t=j/nz; z=top-t*Lx; dx=sway*math.sin(t*2.6+seed)
                yy=y+dy*(1-0.3*t)+0.04*math.sin(t*3.1+seed*0.7)+(0.008 if side else 0.0)*(1 if dy>=0 else -1)
                vs.append((k.bm.verts.new((x-w/2+dx,yy,z)),k.bm.verts.new((x+w/2+dx,yy,z))))
            for j in range(nz):
                a_,b_=vs[j],vs[j+1]
                q=(a_[0],a_[1],b_[1],b_[0]) if side==0 else (b_[0],b_[1],a_[1],a_[0])
                f=k.bm.faces.new(q); f.material_index=mi; f.smooth=True
                for l in f.loops: l[k.uv].uv=((l.vert.co.x-x)*1.5,l.vert.co.z*1.5)
    k.bm.normal_update()
def ind_cloth_rack(k):
    """dyers' drying rack: 2 posts 3.2 m, poles at 2.2 / 2.6 / 3.0, 7 long strips (CLOTH_A, CLOTH_B, YELLOW, PAPER)"""
    for x in(-1.5,1.5):
        k.box((x,0,1.6),(0.16,0.16,3.2),WOOD,bevel=0.03)
        k.box((x,0,0.06),(0.4,0.4,0.12),STONE_BLOCK,bevel=0.03)
        for s in(-1,1): ind_beam(k,(x,s*0.8,0.0),(x,s*0.08,1.2),0.1,0.1,WOOD,bevel=0.02)
    for i,z in enumerate((2.2,2.6,3.0)):
        y=(-0.25,0.0,0.25)[i]
        for x in(-1.5,1.5): k.box((x,y,z),(0.22,0.24 if y else 0.2,0.1),WOOD,bevel=0.02)
        ind_rod(k,(-1.62,y,z+0.08),(1.62,y,z+0.08),0.04,WOOD,segs=6)
    mats=[CLOTH_A,CLOTH_B,YELLOW,CLOTH_A,PAPER,CLOTH_B,CLOTH_A]
    spots=[(-1.05,0,1.95),(-0.45,0,1.8),(0.2,0,2.0),(0.85,0,1.7),(-0.75,1,2.1),(0.5,1,2.2),(-0.1,2,2.3)]
    for i,((x,pi_,L),mi) in enumerate(zip(spots,mats)):
        z=(2.2,2.6,3.0)[pi_]+0.1; y=(-0.25,0.0,0.25)[pi_]
        ind_strip(k,x,y,z,0.5,L,mi,seed=i)
def ind_loom(k):
    """floor loom 2.0 x 1.3 x 1.8 (weaver faces -Y from the bench), 20 warp threads, CLOTH_A cloth roll"""
    W=1.6; D=1.3
    for x in(-W/2,W/2):
        for y,h in((-D/2,1.05),(D/2,1.8)): k.box((x,y,h/2),(0.12,0.12,h),WOOD,bevel=0.025)
        k.box((x,0,0.2),(0.1,D,0.1),WOOD,bevel=0.02); k.box((x,0,1.0),(0.1,D,0.1),WOOD,bevel=0.02)
        k.box((x,D/2-0.35,1.78),(0.1,0.8,0.1),WOOD,bevel=0.02)
    k.box((0,-D/2,0.98),(W+0.2,0.12,0.1),WOOD,bevel=0.02)                              # breast beam
    _cyl(k,(0,-D/2+0.18,0.62),0.14,0.14,W-0.1,12,CLOTH_A,rot=Matrix.Rotation(math.pi/2,4,"Y"))   # cloth roll
    _cyl(k,(0,D/2,0.85),0.1,0.1,W-0.05,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))         # warp beam
    ind_rod(k,(-W/2-0.1,D/2-0.35,1.8),(W/2+0.1,D/2-0.35,1.8),0.04,WOOD,segs=6)                 # top bar
    # woven cloth from the breast beam toward the reed
    k.quad([(-0.62,-D/2+0.05,1.0),(0.62,-D/2+0.05,1.0),(0.62,-0.15,1.0),(-0.62,-0.15,1.0)],CLOTH_A,uvs=[(0,0),(1.2,0),(1.2,0.5),(0,0.5)])
    # 20 warp threads from the reed to the warp beam
    for i in range(20):
        x=-0.6+i*1.2/19
        ind_beam(k,(x,-0.15,1.0),(x,D/2-0.08,0.93),0.012,0.01,CLOTH_B,bevel=0)
    # heddle frame + beater (reed)
    k.box((0,0.2,1.2),(1.35,0.05,0.05),WOOD,bevel=0.01); k.box((0,0.2,0.82),(1.35,0.05,0.05),WOOD,bevel=0.01)
    for i in range(9): k.box((-0.6+i*0.15,0.2,1.01),(0.012,0.012,0.38),IRON,bevel=0)
    ind_rod(k,(-0.35,D/2-0.35,1.78),(-0.35,0.2,1.23),0.01,HAY,segs=3); ind_rod(k,(0.35,D/2-0.35,1.78),(0.35,0.2,1.23),0.01,HAY,segs=3)
    k.box((0,-0.18,1.12),(1.4,0.08,0.28),WOOD,bevel=0.02)
    for x in(-0.72,0.72): ind_beam(k,(x,-0.18,0.98),(x,0.05,0.2),0.06,0.06,WOOD,bevel=0.01)
    # treadles and bench
    for x in(-0.18,0.18): ind_beam(k,(x,-0.2,0.08),(x,0.55,0.2),0.08,0.03,WOOD,bevel=0.01)
    k.box((0,-D/2-0.55,0.52),(1.2,0.32,0.06),PLANKS,bevel=0.01)
    for x in(-0.5,0.5):
        for y in(-0.1,0.1): k.box((x,-D/2-0.55+y,0.25),(0.06,0.06,0.5),WOOD,bevel=0.01)
    # a shuttle and a spare bobbin
    ind_tbox(k,(0.3,-D/2+0.02,1.07),(0.3,0.06,0.05),WOOD,top=(0.6,1),bevel=0.01)
def ind_spinning_wheel(k):
    """saxony spinning wheel on a slanted bench, distaff with wool. Work socket in front (-Y)"""
    k.box((0,0,0.42),(0.9,0.28,0.07),WOOD,rot=(0,-0.18,0),bevel=0.02)
    for (x,y) in((-0.38,-0.1),(-0.38,0.1),(0.38,0)):
        ind_beam(k,(x,y,0.44+0.07*(-1 if x<0 else 1)),(x*1.25,y*1.8,0.0),0.05,0.05,WOOD,bevel=0.01)
    wc=Vector((-0.22,0,0.95)); r=0.36
    ring(k,tuple(wc),r-0.04,r,0.05,WOOD,n=20,axis="Y")
    for i in range(8):
        a=i*math.pi/4
        ind_beam(k,wc,wc+Vector((math.cos(a)*r*0.95,0,math.sin(a)*r*0.95)),0.025,0.025,WOOD,bevel=0)
    _cyl(k,tuple(wc),0.06,0.06,0.12,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for y in(-0.07,0.07): ind_beam(k,(-0.3,y,0.46),(wc.x,y,wc.z),0.045,0.045,WOOD,bevel=0.01)
    # mother-of-all + flyer
    for x in(0.2,0.38): k.box((x,0,0.72),(0.04,0.04,0.5),WOOD,bevel=0.005)
    k.box((0.29,0,0.95),(0.26,0.07,0.05),WOOD,bevel=0.01)
    _cyl(k,(0.29,0,0.88),0.05,0.05,0.2,8,CLOTH_B,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # treadle + footman
    k.box((-0.05,0,0.05),(0.35,0.18,0.03),WOOD,bevel=0.005)
    ind_beam(k,(-0.05,0.02,0.07),(-0.22,0.05,0.8),0.02,0.02,WOOD,bevel=0)
    # distaff with a wool bundle
    ind_beam(k,(0.35,-0.05,0.47),(0.15,-0.2,1.3),0.03,0.03,WOOD,bevel=0)
    _ico(k,(0.18,-0.18,1.22),0.13,CLOTH_B,(1,1,1.5),sub=2,jit=0.015,seed=4)
def ind_pile_hides(k,size=1):
    """stacks of folded hides (HIDE / MUSH_BROWN) with a pelt draped over each stack"""
    rnd=random.Random(size)
    stacks=[(0,0,3)] if size==1 else ([(-0.6,0,4),(0.6,0.05,2)] if size==2 else [(-1.0,0,5),(0.1,0.0,3),(1.15,0.1,2)])
    for si,(sx,sy,n) in enumerate(stacks):
        for i in range(n):
            mi=(HIDE,MUSH_BROWN,HIDE,PIGSKIN)[(i+si+size)%4]
            k.box((sx+rnd.uniform(-.06,.06),sy+rnd.uniform(-.06,.06),0.06+i*0.1),(0.9,0.66,0.09),mi,rot=(0,0,rnd.uniform(-0.25,0.25)),bevel=0.04,segs=2,jitter=0.025,seed=size*20+i+si*7)
        top=0.06+n*0.1+0.02
        def zf(x,y,top=top):
            ov=max(abs(x)-0.42,0.0); ovy=max(abs(y)-0.3,0.0)
            return top-ov*1.3-ovy*1.2
        ind_pelt(k,1.25,0.95,MUSH_BROWN if (si+size)%2 else HIDE,seed=size*3+si,z_fn=zf,M=Matrix.Translation((sx,sy,0))@Matrix.Rotation(rnd.uniform(-0.3,0.3),4,"Z"))
def ind_pile_wool(k,size=1):
    """CLOTH_B wool bales 0.8x0.6x0.6 tied with rope, plus loose fleeces"""
    rnd=random.Random(size*3)
    spots={1:[(0,0,0,0.1)],2:[(-0.45,0,0,0.05),(0.45,0.05,0,-0.08),(0,0.02,0.58,0.3)],
           3:[(-0.85,0,0,0.04),(0.0,0.03,0,-0.05),(0.85,-0.02,0,0.08),(-0.42,0.0,0.58,0.1),(0.42,0.02,0.58,-0.12)]}[size]
    for (x,y,z,r) in spots:
        k.box((x,y,z+0.3),(0.8,0.6,0.58),CLOTH_B,rot=(0,0,r),bevel=0.12,segs=2,jitter=0.025,seed=int(x*10+z*7)+size)
        for dx in(-0.22,0.22):
            c,s_=math.cos(r),math.sin(r)
            k.box((x+dx*c,y+dx*s_,z+0.3),(0.05,0.63,0.61),BURLAP,rot=(0,0,r),bevel=0.02)
    for i in range(1+size):
        cx=rnd.uniform(-0.5,0.5)*size; cy=-0.6-rnd.uniform(0,0.2)
        for j in range(4):
            _ico(k,(cx+rnd.uniform(-0.18,0.18),cy+rnd.uniform(-0.12,0.12),0.1+0.03*j),rnd.uniform(0.12,0.17),CLOTH_B,(1.2,1,0.7),sub=1,jit=0.02,seed=i*7+j+size)

# ================================================================ FOOD
def ind_cone_roof(k,z0,r0,z1,r1,c=(0,0),segs=16,mi=ROOF,kick=0.25,tiles=None):
    """conical (bell-cast) roof from radius r0 at z0 to r1 at z1; ROOF uvs: u around, v down the slope"""
    prof=[(r0+0.15,z0-0.12),(r0,z0),(r0-(r0-r1)*0.18,z0+(z1-z0)*0.12+kick*0.1),(r0-(r0-r1)*0.5,z0+(z1-z0)*0.52),(r1,z1)]
    fs=lathe(k,prof,center=(c[0],c[1],0),segs=segs,mi=mi)
    tiles=tiles or max(3,round(2*math.pi*r0/TILE.get(mi,3.0)*1.4))
    sl=[0.0]
    for (a,b) in zip(prof[:-1],prof[1:]): sl.append(sl[-1]+math.hypot(a[0]-b[0],a[1]-b[1]))
    for f in fs:
        ang=[math.atan2(l.vert.co.y-c[1],l.vert.co.x-c[0]) for l in f.loops]
        if max(ang)-min(ang)>math.pi: ang=[a+2*math.pi if a<0 else a for a in ang]
        for l,a in zip(f.loops,ang):
            r=math.hypot(l.vert.co.x-c[0],l.vert.co.y-c[1])
            j=min(range(len(prof)),key=lambda i:abs(prof[i][0]-r)+abs(prof[i][1]-l.vert.co.z))
            l[k.uv].uv=(a/(2*math.pi)*tiles,-sl[j]/TILE.get(mi,3.0)*1.1)
    # underside
    lathe(k,[(r1*0.9,z1-0.1),(r0-0.05,z0-0.08)],center=(c[0],c[1],0),segs=segs,mi=WOOD)
    return fs
def ind_oast(k):
    """oast kiln: round STONE roundel r 2.2 x 5.0, conical ROOF r 2.4 x 3.6, white PLASTER cowl with a vane (top ~10.6).
       Door at -Y. Sockets: Smoke at the cowl mouth (0,0.3,9.3); Door (0,-3.1,0); the cowl can be split off as a Spin part later."""
    R=2.2
    ind_lathe(k,[(R+0.12,-0.6),(R+0.12,0.35),(R+0.04,0.5),(R,1.0),(R,5.0),(R-0.3,5.0)],segs=16,mi=STONE,tile=3.0,around=5)
    ind_lathe(k,[(R+0.2,0.0),(R+0.2,0.42),(R+0.05,0.5)],segs=16,mi=STONE_BLOCK,tile=1.2)
    ring(k,(0,0,4.95),R-0.02,R+0.12,0.16,WOOD,n=16,axis="Z")                       # wall plate
    ind_cone_roof(k,5.0,R+0.3,8.55,0.42,segs=16)
    # cowl: round collar, box body, slanted hood, vane
    _cyl(k,(0,0,8.6),0.5,0.5,0.14,12,WOOD)
    z0=8.65; W=0.8
    sub=Kit()
    sub.box((0,0,z0+0.5),(W,W,1.0),PLASTER,bevel=0.03)
    sub.quad([(-W/2+0.08,W/2+0.012,z0+0.12),(W/2-0.08,W/2+0.012,z0+0.12),(W/2-0.08,W/2+0.012,z0+0.9),(-W/2+0.08,W/2+0.012,z0+0.9)][::-1],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    L=math.hypot(W+0.3,0.55)
    sub.box((0,0.12,z0+1.25),(W+0.12,L,0.08),PLASTER,rot=(-math.atan2(0.55,W+0.3),0,0),bevel=0.02)
    for s in(-1,1):
        v=[sub.bm.verts.new(p) for p in ((s*W/2,-W/2,z0+1.0),(s*W/2,W/2+0.1,z0+1.0),(s*W/2,-W/2,z0+1.52))]
        f=sub.bm.faces.new(v if s>0 else v[::-1]); f.material_index=PLASTER
    sub.bm.normal_update()
    for i in range(4): sub.box((0,-W/2-0.01,z0+0.2+i*0.22),(W+0.02,0.03,0.05),WOOD,bevel=0.005)
    ind_beam(sub,(0,-W/2,z0+0.9),(0,-W/2-1.1,z0+1.2),0.06,0.06,WOOD,bevel=0.01)       # vane arm
    sub.box((0,-W/2-1.1,z0+1.2),(0.04,0.55,0.5),PLASTER,bevel=0.01)
    _cyl(sub,(0,0,z0+1.75),0.03,0.03,0.5,6,IRON)
    _ico(sub,(0,0,z0+1.95),0.07,BRONZE,sub=1)
    merge_kit(k,sub,Matrix.Rotation(0.35,4,"Z"))
    # door, loading hatch + small window
    hw=0.55; zt=2.1; y=-R-0.02
    k.quad([(-hw,y,0.4),(hw,y,0.4),(hw,y,zt),(-hw,y,zt)],PLANKS,uvs=[(0,0),(1.1,0),(1.1,1.7),(0,1.7)])
    for s in(-1,1): k.box((s*(hw+0.1),y,1.25),(0.2,0.2,1.75),STONE_BLOCK,bevel=0.03)
    k.box((0,y,zt+0.12),(1.45,0.24,0.26),STONE_BLOCK,bevel=0.03)
    for z in(0.8,1.7): k.box((0,y-0.02,z),(1.0,0.03,0.08),IRON,bevel=0.01)
    k.box((0,y-0.35,0.45),(1.4,0.7,0.1),STONE_BLOCK,bevel=0.03)
    a=math.radians(140); cx,cy=math.cos(a)*(R+0.01),math.sin(a)*(R+0.01)
    sub=Kit()
    sub.quad([(-0.4,0,3.0),(0.4,0,3.0),(0.4,0,3.9),(-0.4,0,3.9)],PLANKS,uvs=[(0,0),(0.8,0),(0.8,0.9),(0,0.9)])
    sub.box((0,-0.05,3.98),(1.0,0.22,0.16),WOOD,bevel=0.02); sub.box((0,-0.08,2.94),(0.95,0.26,0.1),WOOD,bevel=0.02)
    for s in(-1,1): sub.box((s*0.45,-0.03,3.45),(0.12,0.16,1.0),WOOD,bevel=0.02)
    merge_kit(k,sub,Matrix.Translation((cx,cy,0))@Matrix.Rotation(a+math.pi/2,4,"Z"))
    a=math.radians(20); sub=Kit()
    sub.box((0,0.0,2.6),(0.3,0.1,0.5),VOID,bevel=0); sub.box((0,-0.05,2.9),(0.5,0.16,0.12),STONE_BLOCK,bevel=0.02)
    merge_kit(k,sub,Matrix.Translation((math.cos(a)*R,math.sin(a)*R,0))@Matrix.Rotation(a+math.pi/2,4,"Z"))
def ind_mash_tun(k):
    """brewer's mash tun: big stave tun r 0.9 on a stone plinth, mash + paddle, spout into an underback trough, step"""
    R=0.9; n=20
    k.box((0,0,0.14),(2.0,2.0,0.28),STONE_BLOCK,bevel=0.05,segs=1)
    lathe(k,[(R*0.94,0.28),(R,0.75),(R*0.97,1.21),(R*0.89,1.21),(R*0.87,0.7)],segs=n,mi=WOOD)
    for z in(0.36,0.78,1.14): ring(k,(0,0,z),(R*0.95 if z<0.5 else R*0.985)-0.01,(R*0.95 if z<0.5 else R*0.985)+0.05,0.07,IRON,n=n,axis="Z")
    ind_heap(k,(0,0,0.98),0.8,0.8,0.1,BREAD,seed=4,sub=2,rough=0.1)
    ind_beam(k,(-0.3,-0.2,1.0),(0.5,0.5,2.0),0.06,0.06,WOOD,bevel=0.01)
    k.box((-0.37,-0.26,0.95),(0.22,0.05,0.35),WOOD,rot=(0,0,0.7),bevel=0.01)
    # spout + underback trough
    _cyl(k,(0,-R-0.15,0.42),0.05,0.05,0.35,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    k.box((0,-R-0.55,0.2),(1.1,0.5,0.4),WOOD,bevel=0.03)
    k.quad([(-0.48,-R-0.75,0.36),(0.48,-R-0.75,0.36),(0.48,-R-0.35,0.36),(-0.48,-R-0.35,0.36)],BREAD,uvs=[(0,0),(1,0),(1,0.4),(0,0.4)])
    # wooden step on the side
    k.box((R+0.45,0.2,0.2),(0.45,0.8,0.4),PLANKS,bevel=0.02); k.box((R+0.3,0.2,0.5),(0.35,0.8,0.08),PLANKS,bevel=0.02)
    # sacks of malt
    for i,(x,y) in enumerate(((-1.2,0.7),(-1.25,0.1))):
        _ico(k,(x,y,0.32),0.3,BURLAP,(0.9,0.8,1.1),jit=0.02,seed=i); _cyl(k,(x,y,0.66),0.07,0.1,0.1,6,BURLAP)
def ind_cider_press(k):
    """twin-post screw press 1.4 x 1.0 x 2.0 with a pomace cheese on the bed, juice spout and tub, apple basket"""
    for x in(-0.62,0.62):
        k.box((x,0,1.0),(0.22,0.26,2.0),WOOD,bevel=0.04)
        k.box((x,0,0.08),(0.4,0.9,0.16),WOOD,bevel=0.03)
    k.box((0,0,1.95),(1.6,0.3,0.3),WOOD,bevel=0.04)                  # head beam
    k.box((0,0,0.5),(1.1,0.95,0.16),WOOD,bevel=0.03)                 # bed
    for (x,y,sx,sy) in((0,-0.45,1.1,0.06),(0,0.45,1.1,0.06),(-0.52,0,0.06,0.95),(0.52,0,0.06,0.95)):
        k.box((x,y,0.61),(sx,sy,0.07),WOOD,bevel=0.01)
    # cheese: layers of pomace and straw
    for i in range(5):
        mi=HAY if i%2 else BREAD
        k.box((0,0,0.66+i*0.1),(0.8-i*0.01,0.7-i*0.01,0.1),mi,bevel=0.03,jitter=0.01,seed=i)
    k.box((0,0,1.2),(0.9,0.78,0.08),PLANKS,bevel=0.01)                 # pressing board
    k.box((0,0,1.3),(0.5,0.3,0.12),WOOD,bevel=0.02)
    # screw with thread rings + capstan bar
    _cyl(k,(0,0,1.62),0.1,0.1,0.7,10,WOOD)
    for j in range(6): ring(k,(0,0,1.33+j*0.1),0.09,0.14,0.04,WOOD,n=10,axis="Z")
    _cyl(k,(0,0,2.18),0.14,0.14,0.18,10,WOOD)
    ind_beam(k,(-0.9,0,2.18),(0.9,0,2.18),0.06,0.06,WOOD,bevel=0.01)
    # juice spout + tub
    k.box((0,-0.56,0.54),(0.12,0.2,0.05),WOOD,bevel=0.01)
    lathe(k,[(0.0,0.02),(0.24,0.02),(0.28,0.36),(0.25,0.36),(0.22,0.06)],center=(0,-0.82,0),segs=12,mi=WOOD)
    ring(k,(0,-0.82,0.28),0.27,0.3,0.05,IRON,n=12,axis="Z")
    lathe(k,[(0.245,0.29),(0.0,0.29)],center=(0,-0.82,0),segs=12,mi=BRONZE)
    # basket of apples
    _cyl(k,(1.05,-0.45,0.17),0.25,0.3,0.34,10,WATTLE)
    rnd=random.Random(3)
    for i in range(8):
        _ico(k,(1.05+rnd.uniform(-.17,.17),-0.45+rnd.uniform(-.17,.17),0.36+rnd.uniform(0,0.06)),0.075,APPLE,sub=1)
    for i in range(3): _ico(k,(0.8+i*0.15,-0.9+rnd.uniform(-.1,.1),0.07),0.07,APPLE,sub=1)
def ind_skep(k,c=(0,0,0),s=1.0,board=True):
    """coiled straw beehive (HAY lathe r 0.28 x 0.45) with an entrance"""
    cx,cy,cz=c; prof=[]
    n=9
    for i in range(n+1):
        t=i/n; z=0.45*s*t; r=0.28*s*math.sqrt(max(0.0,1-(t*0.92)**2.2))+0.012*s*(1 if i%2 else -1)*(1-t)
        prof.append((max(r,0.01),z))
    prof.append((0.0,0.47*s))
    fs=lathe(k,[(r,z+cz+(0.03 if board else 0)) for r,z in prof],center=(cx,cy,0),segs=12,mi=HAY)
    for f in fs: f.smooth=True
    if board: _cyl(k,(cx,cy,cz+0.015),0.33*s,0.33*s,0.03,12,WOOD)
    k.box((cx,cy-0.27*s,cz+0.07*s),(0.09*s,0.03,0.06*s),VOID,bevel=0)
def ind_bee_bench(k):
    """three skeps on a shelf under a little pent roof (2.2 m wide), open to -Y"""
    W=2.2
    for x in(-W/2+0.1,W/2-0.1):
        for y in(-0.3,0.3): k.box((x,y,0.35 if y<0 else 0.8),(0.1,0.1,0.7 if y<0 else 1.6),WOOD,bevel=0.02)
        k.box((x,0,0.3),(0.08,0.66,0.08),WOOD,bevel=0.01)
    k.box((0,0,0.58),(W,0.72,0.06),PLANKS,bevel=0.01)
    for i in range(4): k.box((0,0.33,0.75+i*0.22),(W,0.04,0.2),PLANKS,bevel=0.005)
    ang=0.42; L=math.hypot(1.05,0.45)
    k.box((0,-0.05,1.52),(W+0.3,L,0.07),ROOF,rot=(ang,0,0),bevel=0.02)
    k.box((0,0.36,1.63),(W+0.1,0.1,0.1),WOOD,bevel=0.02)
    for x in(-W/2+0.1,W/2-0.1): ind_beam(k,(x,0.3,1.15),(x,-0.42,1.36),0.07,0.07,WOOD,bevel=0.01)
    for x in(-0.7,0.0,0.7): ind_skep(k,(x,-0.02,0.61),1.0,board=True)
    for (x,y) in((-1.25,-0.5),(1.2,-0.55)): ind_tuft(k,(x,y,0.0),0.5,seed=int(x*10),cell="lavender")
def ind_herb_bundles(k):
    """drying pole on two posts with 6 bundles of herbs hanging head-down"""
    for x in(-1.1,1.1):
        k.box((x,0,1.05),(0.12,0.12,2.1),WOOD,bevel=0.02); k.box((x,0,0.05),(0.3,0.3,0.1),STONE_BLOCK,bevel=0.02)
    ind_rod(k,(-1.25,0,2.0),(1.25,0,2.0),0.045,WOOD,segs=6)
    cells=["lavender","drygrass","leafy","lavender","wheat","leafy","drygrass"]
    rnd=random.Random(5)
    for i in range(7):
        x=-0.93+i*0.31; L=rnd.uniform(0.7,0.95); top=1.95
        ind_rod(k,(x,0,1.99),(x,0,top-0.1),0.012,HAY,segs=3)
        _cyl(k,(x,0,top-0.14),0.05,0.045,0.08,6,HAY)
        for j in range(3):
            a=j*math.pi/3+rnd.uniform(-.2,.2)
            card(k,(x,0,top-0.14-L/2),(math.cos(a),math.sin(a),0),(0,0,-1),0.44,L,cells[i],flip=j%2==0)
    _cyl(k,(0.2,0.35,0.16),0.25,0.3,0.32,10,WATTLE)
def ind_cauldron(k):
    """iron cauldron on a tripod over a fire (GLOW flames = Fire socket), green brew"""
    ind_lathe(k,[(0.0,0.42),(0.22,0.43),(0.4,0.55),(0.47,0.75),(0.45,0.95),(0.4,1.05),(0.44,1.08),(0.4,1.1)],segs=16,mi=IRON)
    _cyl(k,(0,0,1.02),0.39,0.39,0.02,16,LEAF)
    for s in(-1,1): ring(k,(s*0.47,0,0.98),0.05,0.08,0.03,IRON,n=8,axis="Y")
    for i in range(3):
        a=i*2*math.pi/3+0.3
        ind_beam(k,(math.cos(a)*1.0,math.sin(a)*1.0,0.0),(0,0,2.1),0.07,0.07,WOOD,bevel=0.015)
    ind_rod(k,(0,0,2.05),(0,0,1.1),0.015,IRON,segs=4)
    ind_rod(k,(-0.44,0,1.0),(0,0,1.2),0.012,IRON,segs=4); ind_rod(k,(0.44,0,1.0),(0,0,1.2),0.012,IRON,segs=4)
    # fire: logs, stone ring, flames
    rnd=random.Random(2)
    for i in range(8):
        a=2*math.pi*i/8; rock(k,(math.cos(a)*0.62,math.sin(a)*0.62,0.08),(0.22,0.18,0.16),seed=40+i,mi=STONE_BLOCK,segs=1)
    for i in range(4):
        a=i*math.pi/2+0.4
        ind_log(k,(math.cos(a)*0.5,math.sin(a)*0.5,0.08),(math.cos(a)*0.05,math.sin(a)*0.05,0.2),0.06,seed=i)
    for i in range(5):
        a=2*math.pi*i/5; r=0.12
        lathe(k,[(0.09,0.0),(0.06,0.14),(0.0,0.3+0.08*(i%2))],center=(math.cos(a)*r,math.sin(a)*r,0.12),segs=5,mi=GLOW)
def ind_drying_rack_meat(k):
    """A-frame rack with hams, sausage strings and strips of dried meat"""
    W=2.4
    for x in(-W/2,W/2):
        for s in(-1,1): ind_beam(k,(x,s*0.55,0.0),(x,s*0.06,2.2),0.1,0.1,WOOD,bevel=0.02)
        k.box((x,0,1.0),(0.08,0.9,0.08),WOOD,bevel=0.01)
    ind_rod(k,(-W/2-0.15,0,2.1),(W/2+0.15,0,2.1),0.05,WOOD,segs=6)
    for y in(-0.28,0.28): ind_rod(k,(-W/2,y,1.3),(W/2,y,1.3),0.035,WOOD,segs=6)
    rnd=random.Random(4)
    for i in range(4):   # hams
        x=-0.85+i*0.56
        ind_rod(k,(x,0,2.06),(x,0,1.82),0.012,HAY,segs=3)
        ind_lathe(k,[(0.0,1.24),(0.1,1.26),(0.19,1.36),(0.2,1.52),(0.12,1.72),(0.03,1.8)],c=(x,0,0),segs=10,mi=CLAY,smooth=True)
        _cyl(k,(x,0,1.84),0.035,0.03,0.1,6,PAPER)
    for y in(-0.28,0.28):   # sausage strings and strips of dried meat
        for i in range(6):
            x=-1.0+i*0.4+rnd.uniform(-.05,.05)
            if (i+int(y*10))%2:
                for j in range(3): _ico(k,(x,y,1.2-j*0.17),0.07,MUSH_RED if j%2 else CLAY,(0.9,0.9,1.6),sub=1)
            else:
                k.box((x,y,1.02),(0.13,0.03,0.5),MUSH_RED,rot=(0,rnd.uniform(-.1,.1),0),bevel=0.012)
def ind_drying_rack_herbs(k):
    """four-post rack with three slatted trays of herbs and flowers, bundles hanging from the top rail"""
    W,D=1.6,0.8
    for x in(-W/2,W/2):
        for y in(-D/2,D/2): k.box((x,y,0.95),(0.08,0.08,1.9),WOOD,bevel=0.015)
    for zi,z in enumerate((0.45,0.95,1.45)):
        for y in(-D/2,D/2): k.box((0,y,z),(W,0.06,0.06),WOOD,bevel=0.01)
        for i in range(7): k.box((-W/2+0.12+i*(W-0.24)/6,0,z+0.04),(0.06,D-0.04,0.03),WOOD,bevel=0.005)
        rnd=random.Random(zi)
        for i in range(6):
            x=-W/2+0.25+i*(W-0.5)/5+rnd.uniform(-0.06,0.06); y=rnd.uniform(-0.2,0.2)
            if (i+zi)%3==0: _ico(k,(x,y,z+0.1),0.1,LEAF,(1.4,1,0.5),sub=1,jit=0.02,seed=i)
            elif (i+zi)%3==1:
                for j in range(4): _ico(k,(x+rnd.uniform(-.08,.08),y+rnd.uniform(-.08,.08),z+0.09),0.045,PINK if zi!=1 else YELLOW,sub=0)
            else: _ico(k,(x,y,z+0.09),0.09,BREAD,(1.5,1,0.4),sub=1,jit=0.02,seed=i+20)
    ind_rod(k,(-W/2,0,1.9),(W/2,0,1.9),0.03,WOOD,segs=6)
    for i in range(4):
        x=-0.55+i*0.37
        for j in range(2):
            a=j*math.pi/2+0.3
            card(k,(x,0,1.62),(math.cos(a),math.sin(a),0),(0,0,-1),0.26,0.5,"lavender" if i%2 else "leafy",flip=j==0)
def ind_dovecote(k):
    """round stone dovecote r 2.0 x 5.0 with 3 rows of nest holes, landing ledges, cone roof r 2.2 x 3.0 and an open lantern (~8.5 m)"""
    R=2.0
    ind_lathe(k,[(R+0.1,-0.6),(R+0.1,0.3),(R+0.02,0.45),(R,1.0),(R,5.0),(R-0.3,5.0)],segs=16,mi=STONE,tile=3.0,around=4)
    ind_lathe(k,[(R+0.18,0.0),(R+0.18,0.4),(R+0.05,0.48)],segs=16,mi=STONE_BLOCK,tile=1.2)
    for z in(2.55,3.45,4.35): ring(k,(0,0,z),R-0.02,R+0.16,0.08,STONE_BLOCK,n=16,axis="Z")
    for row,z in enumerate((2.75,3.65,4.55)):
        for i in range(12):
            a=2*math.pi*(i+0.5*(row%2))/12
            if row==0 and abs(math.sin(a)+1)<0.1: continue
            sub=Kit(); sub.box((0,-0.02,0),(0.17,0.08,0.22),VOID,bevel=0)
            sub.box((0,-0.05,0.14),(0.26,0.08,0.06),STONE_BLOCK,bevel=0.01)
            merge_kit(k,sub,Matrix.Translation((math.cos(a)*R,math.sin(a)*R,z))@Matrix.Rotation(a+math.pi/2,4,"Z"))
    ring(k,(0,0,4.97),R-0.05,R+0.12,0.14,WOOD,n=16,axis="Z")
    ind_cone_roof(k,5.0,R+0.25,7.75,0.55,segs=16)
    # open lantern (glover) on top + finial
    for i in range(4):
        a=i*math.pi/2+math.pi/4
        k.box((math.cos(a)*0.42,math.sin(a)*0.42,7.95),(0.1,0.1,0.55),WOOD,bevel=0.015)
    _cyl(k,(0,0,7.72),0.62,0.62,0.08,12,WOOD)
    ind_cone_roof(k,8.2,0.75,8.95,0.05,segs=12)
    _cyl(k,(0,0,9.05),0.025,0.025,0.4,6,IRON); _ico(k,(0,0,9.28),0.07,BRONZE,sub=1)
    # door + doves
    hw=0.4; y=-R-0.02
    k.quad([(-hw,y,0.45),(hw,y,0.45),(hw,y,1.9),(-hw,y,1.9)],PLANKS,uvs=[(0,0),(0.8,0),(0.8,1.45),(0,1.45)])
    for s in(-1,1): k.box((s*(hw+0.1),y,1.15),(0.2,0.2,1.5),STONE_BLOCK,bevel=0.03)
    k.box((0,y,2.0),(1.2,0.24,0.24),STONE_BLOCK,bevel=0.03)
    k.box((0,y-0.35,0.45),(1.2,0.7,0.1),STONE_BLOCK,bevel=0.03)
    rnd=random.Random(9)
    for i,(a,z) in enumerate(((0.3,3.5),(1.7,4.4),(2.6,2.6),(4.1,3.5),(5.2,4.4),(3.3,5.1))):
        rr=R+0.12 if z<5 else R+0.35
        sub=Kit(); chicken(sub,(0,0,0),0.0,PAPER,seed=i)
        merge_kit(k,sub,Matrix.Translation((math.cos(a)*rr,math.sin(a)*rr,z+0.04 if z<5 else 5.02))@Matrix.Rotation(a+math.pi/2,4,"Z")@Matrix.Scale(0.5,4))
    ind_skirt(k,-1.4,1.4,-1.4,1.4)

# ================================================================ BUILDERS
def ind_ground_block(coll,origin,x0,x1,y0,y1,z,name="IND_Standin"):
    """stand-in terrain plateau (box with top at z, scene ground material) - demo only, not a kit piece"""
    ox,oy,orz=origin; c,s=math.cos(orz),math.sin(orz)
    bm=bmesh.new(); r=bmesh.ops.create_cube(bm,size=1.0)
    bmesh.ops.transform(bm,matrix=Matrix.Translation(((x0+x1)/2,(y0+y1)/2,(z-0.6)/2))@Matrix.Diagonal((x1-x0,y1-y0,z+0.6,1)),verts=r["verts"])
    uv=bm.loops.layers.uv.new("UVMap"); cl=bm.loops.layers.color.new("Col"); bm.normal_update()
    for f in bm.faces:   # top = ground material, sides = kit ROCK (reads as a cliff, not a green wall)
        ax=max(range(3),key=lambda i: abs(f.normal[i])); f.material_index=0 if ax==2 else 1
        for l in f.loops:
            l[cl]=(0.85,0.85,0.85,1.0) if l.vert.co.z>z-0.5 else (0.6,0.6,0.6,1.0)   # kit materials multiply by 'Col'
            p=l.vert.co; l[uv].uv=((p.y,p.z) if ax==0 else ((p.x,p.z) if ax==1 else (p.x,p.y)))
            l[uv].uv=(l[uv].uv[0]/3.0,l[uv].uv[1]/3.0)
    old=bpy.data.meshes.get(name)
    if old and old.users==0: bpy.data.meshes.remove(old)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    gm=None
    for gn in ("WS_industry_Ground","VK_Ground"):
        g_=bpy.data.objects.get(gn)
        if g_ and g_.data.materials: gm=g_.data.materials[0]; break
    rm=None
    src=bpy.data.objects.get("SM_VK_Quarry_Floor")
    if src and len(src.data.materials)>ROCK: rm=src.data.materials[ROCK]
    if gm: me.materials.append(gm)
    if rm: me.materials.append(rm)
    o=bpy.data.objects.new(name,me); coll.objects.link(o)
    o.location=(ox,oy,0); o.rotation_euler=(0,0,orz)
    return o
def ind_P(coll,origin):
    def P(n,x,y,z=0.0,r=0.0,st=None): return place_v(coll,n,x,y,z,r,origin,st or {})
    return P

def build_mine(coll,origin,seed=0):
    """mine yard ~5x4 cells (x -7.5..7.5, y -6..7.5; the portal mound runs ~6 m back from local y 1.5):
       portal at local (0,1.5) facing -Y, rails out of the tunnel curving to a buffer at +X, carts, ore/coal piles,
       thatched shelter with crates/barrels, cordwood and a meat drying rack"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Mine_Portal",0,1.5)
    P("SM_VK_Rail_Straight",0,3.0,0,90); P("SM_VK_Rail_Straight",0,0.0,0,90)
    P("SM_VK_Rail_Curve",0,-3.0,0,-90)
    P("SM_VK_Rail_End",4.5,-4.5,0,0)
    o=P("SM_VK_Prop_Minecart",0,-0.6,IND_RAIL_TOP,90)
    o=P("SM_VK_Prop_Minecart",3.2,-4.5,IND_RAIL_TOP,rnd.uniform(-3,3))
    P("SM_VK_Pile_Ore_3",6.8,-2.2,0,20); P("SM_VK_Pile_Ore_1",2.6,-1.6,0,-40)
    P("SM_VK_Pile_Coal_2",-3.4,-2.0,0,-15)
    P("SM_VK_LeanTo",-3.6,1.1,0,0,{"roof":"Thatch"})
    P("SM_VK_Prop_Crates",-4.5,-0.6,0,0); P("SM_VK_Prop_BarrelStack",-2.9,-0.4,0,90)
    P("SM_VK_Prop_Woodpile",-3.6,-4.6,0,0)
    P("SM_VK_Prop_DryingRack_Meat",-6.7,-2.4,0,90)          # miners' provisions by the shelter

def build_quarry_yard(coll,origin,seed=0,standin=True):
    """3x3 quarry pit cut 2 LVL (3.0 m) into a plateau, open to -Y; crane on the rim hoists a block out of the pit.
       Contour pieces: back Straight + 2 InnerCorners, side Straights, front outer Corners (+ hill-front Straights at x=+-6)."""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Quarry_Face_Straight",0,3,0,0)
    P("SM_VK_Quarry_Face_InnerCorner",3,3,0,0); P("SM_VK_Quarry_Face_InnerCorner",-3,3,0,90)
    P("SM_VK_Quarry_Face_Straight",3,0,0,-90); P("SM_VK_Quarry_Face_Straight",-3,0,0,90)
    P("SM_VK_Quarry_Face_Corner",3,-3,0,0); P("SM_VK_Quarry_Face_Corner",-3,-3,0,90)
    P("SM_VK_Quarry_Face_Straight",6,-3,0,0); P("SM_VK_Quarry_Face_Straight",-6,-3,0,0)
    P("SM_VK_Quarry_Floor",0,0,0,0); P("SM_VK_Quarry_Floor",0,-3,0,90)
    if standin:
        ind_ground_block(coll,origin,-7.5,7.5,4.5,11.0,2.99,"IND_Standin_QuarryBack")
        ind_ground_block(coll,origin,4.5,7.5,-1.5,4.5,2.99,"IND_Standin_QuarryR")
        ind_ground_block(coll,origin,-7.5,-4.5,-1.5,4.5,2.99,"IND_Standin_QuarryL")
    # crane on the back rim, jib reaching over the pit
    P("SM_VK_Prop_TreadwheelCrane",-0.6,6.9,3.0,-90)
    w=P("SM_VK_Prop_TreadwheelCrane_Wheel",-0.6,6.9+1.0,3.0+IND_CRANE_AXLE[2],-90); w["spin_axis"]="local Y"; w["rpm"]=4.0
    # mason's corner on the floor
    P("SM_VK_Prop_Banker",-0.9,-3.4,0,10)
    P(ind_pick("SM_VK_Pile_Stone_3","SM_VK_Prop_Crates"),1.6,-4.0,0,0)
    P(ind_pick("SM_VK_Prop_Wheelbarrow","SM_VK_Prop_Cart"),1.9,-1.6,0,-30)
    P("SM_VK_Prop_Grindstone",-1.9,-1.3,0,70)
    P("SM_VK_LeanTo",-6.0,-3.85,0,0,{"roof":"Thatch"})

def ind_sub_origin(origin,x,y,rot_deg=0.0):
    ox,oy,orz=origin; c,s=math.cos(orz),math.sin(orz)
    return (ox+x*c-y*s,oy+x*s+y*c,orz+math.radians(rot_deg))
def ind_opt(P,name,*a,**kw):
    """place a piece only if it exists (other agents' pieces)"""
    if bpy.data.objects.get(name): return P(name,*a,**kw)
    return None

def build_charcoal_burner(coll,origin,seed=0):
    """5x2 cells (15 x 6 m, x -7.5..7.5, y -3..3): charcoal clamp + cordwood (x<0), bloomery + bellows + ore/coal (x>0)"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Prop_CharcoalMound",-3.6,0.35,0,rnd.uniform(0,40))
    P("SM_VK_Prop_Woodpile",-3.6,-2.72,0,0)
    ind_opt(P,"SM_VK_Pile_Logs_3",-6.75,0.3,0,90)
    P("SM_VK_Pile_Coal_1",-0.35,-2.0,0,-20)
    P("SM_VK_Prop_Bloomery",3.0,0.8,0,0)
    P("SM_VK_Prop_Bellows",5.75,0.8,0,0)
    P("SM_VK_Pile_Coal_2",0.75,2.05,0,0)
    P("SM_VK_Pile_Ore_2",6.1,-1.95,0,15)
    P("SM_VK_Prop_Anvil",2.9,-2.3,0,25)

def build_tannery(coll,origin,seed=0):
    """~5x4 cells (x -7.5..6, y -4.5..5.5): 3-cell daub workshop (y 0..6 behind the yard) with a thatch vent on the
       middle bay and two lean-to sheds on its +X end; a row of 4 tanning pits in the yard, hide frames, hide piles"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    st={"ground":"Plaster","plaster":"Daub","shutter":"Natural","roof":"Thatch","seed":seed+71}
    ho=ind_sub_origin(origin,-3.0,2.5,0)
    build_house_v(coll,ho,3,1,st,front=".DW",back="...",chimney=False)
    Ph=ind_P(coll,ho)
    for yy in(-1.5,1.5): Ph("SM_VK_LeanTo",4.5,-yy,0,90,{"roof":"Thatch"})
    vent=ind_pick("SM_VK_RoofThatch_Vent","SM_VK_Roof_Vent")
    ind_opt(Ph,vent,0.0,0,roof_top(1)+RIDGE,0,st)                  # middle bay is always a full-ridge Mid piece
    for i,x in enumerate((-6.4,-4.2,0.0,2.2)): P("SM_VK_Prop_TanningPit",x,-3.0,0,rnd.choice((0,90,180,270)))   # path to the door at x=-3
    for i,x in enumerate((4.4,5.9)): P("SM_VK_Prop_HideFrame",x,-3.3+0.3*i,0,-8+16*i)
    P("SM_VK_Prop_HideFrame",6.1,-1.3,0,90)
    P("SM_VK_Pile_Hides_3",3.4,2.8,0,90)
    P("SM_VK_Pile_Hides_1",3.7,-1.5,0,10)
    P("SM_VK_Prop_BarrelStack",-7.0,-4.7,0,0)
    P("SM_VK_Prop_Trough",-6.0,-1.35,0,0)
    P("SM_VK_Prop_Cauldron",-1.2,-1.55,0,0)

def build_dyers_yard(coll,origin,seed=0):
    """~4x2 cells (x -6..5, y -3..3): four dye vats in different cloth colours, two drying racks, laundry line, loom,
       wool bales, spinning wheel, dye cauldron"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    cols=["Red","Blue","Yellow","Purple","Green"]; rnd.shuffle(cols)
    for i,x in enumerate((-3.3,-1.6,0.1,1.8)):
        P("SM_VK_Prop_DyeVat",x,-2.1+0.25*(i%2),0,rnd.uniform(-25,25),{"cloth":cols[i]})
    P("SM_VK_Prop_ClothRack",-1.8,1.3,0,0,{"cloth":cols[0]})
    P("SM_VK_Prop_ClothRack",2.2,1.9,0,-12,{"cloth":cols[1]})
    P("SM_VK_Prop_Laundry",-1.0,-0.4,0,0)
    P("SM_VK_Prop_Cauldron",3.6,-1.7,0,0)
    P("SM_VK_Pile_Wool_2",-3.9,2.4,0,90)
    P("SM_VK_Prop_Loom",-5.0,-0.3,0,90,{"cloth":cols[2]})
    P("SM_VK_Prop_SpinningWheel",4.0,0.2,0,-120)
    P("SM_VK_Prop_Stool",3.45,0.55,0,0)

def build_brewery(coll,origin,seed=0):
    """5x3 cells (15 x 9, x -7.5..7.5, y -5..4): 3x2 stone brew-house range, round oast with a white cowl clear of its
       +X gable, mash tun at the oast door, cider press, barrels, malt sacks, cart"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    st={"ground":"Stone","plaster":"White","shutter":"Green","roof":"Red","seed":seed+13}
    ho=ind_sub_origin(origin,-3.0,1.0,0)
    build_house_v(coll,ho,3,2,st,front="WDW",back="W..",chimney=False)
    place_v(coll,"SM_VK_Chimney",3.0,0,roof_top(2),0,ho,st)          # fixed bay so the ridge emblem never collides
    P("SM_VK_Kiln_Oast",4.95,1.2,0,0,{"plaster":"White","roof":"Red"})
    P("SM_VK_Prop_MashTun",6.0,-3.7,0,0)
    P("SM_VK_Prop_CiderPress",-5.3,-3.5,0,0)
    P("SM_VK_Prop_BarrelStack",-2.5,-3.6,0,15)
    P("SM_VK_Prop_Sacks",2.2,-2.6,0,0); P("SM_VK_Prop_Cart",0.2,-4.2,0,-10)
    ind_opt(P,"SM_VK_Emblem_Ridge_Tankard",-3.0,1.0,roof_top(2)+RIDGE,0)

def build_apiary(coll,origin,seed=0):
    """3x3 cells (9 x 9, x -4.5..4.5, y -4.5..4.5): apiary + herb garden - lavender bed, two bee benches, skeps on
       stools, round dovecote (door -Y), herb drying rack and herb bundles"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Crop_Lavender",-2.6,3.0,0,0)
    P("SM_VK_Prop_Dovecote",2.5,2.35,0,0)
    P("SM_VK_Prop_BeeBench",-3.05,0.1,0,rnd.uniform(-5,5))
    P("SM_VK_Prop_BeeBench",-0.05,-0.45,0,rnd.uniform(-5,5))
    for i,x in enumerate((-3.9,-2.4,-0.9)):
        P("SM_VK_Prop_Stool",x,-2.1,0,0); P("SM_VK_Prop_Skep",x,-2.1,0.54,rnd.uniform(0,360))
    P("SM_VK_Prop_DryingRack_Herbs",4.0,-1.9,0,-90)
    P("SM_VK_Prop_HerbBundles",1.3,-3.6,0,0)
    P("SM_VK_Prop_Bench",-2.0,-3.7,0,180)

def build_pottery(coll,origin,seed=0):
    """~4x3 cells (x -6..4.5, y -4.5..4.5): bottle kiln, clay pit, potter's wheel at a work table, pots, brick and coal piles"""
    P=ind_P(coll,origin); rnd=random.Random(seed)
    P("SM_VK_Prop_BottleKiln",-2.0,1.6,0,rnd.uniform(-20,20))
    P("SM_VK_Prop_ClayPit",3.0,3.0,0,0)
    P("SM_VK_Prop_PottersWheel",2.4,-1.0,0,180)
    P("SM_VK_Prop_Table",3.4,-2.9,0,0)
    P("SM_VK_Pile_Bricks_3",-2.4,-3.4,0,0)
    P("SM_VK_Pile_Bricks_1",0.4,-3.6,0,20)
    P("SM_VK_Pile_Coal_2",-4.6,-1.6,0,70)
    P("SM_VK_Prop_Woodpile",-5.0,3.4,0,90)
    ind_opt(P,"SM_VK_Prop_ShopGoods_Pots",4.6,-0.6,0,-90)

IND_QUARTER=[("build_mine",-30,0),("build_quarry_yard",-12,0),("build_charcoal_burner",6,0),("build_pottery",22,0),
             ("build_tannery",-30,18.5),("build_dyers_yard",-14,19),("build_brewery",2,18.5),("build_apiary",18,19)]
def build_industry_quarter(coll,origin,seed=0):
    """demo: all 8 production yards in two rows (~64 x 30 m, x -37.5..26.5, y -6..24 around origin)"""
    g_=globals()
    for fn,x,y in IND_QUARTER:
        g_[fn](coll,ind_sub_origin(origin,x,y),seed=seed)

WS_SPECS=[
 ("SM_VK_Mine_Portal",ind_mine_portal,IND_NG),
 ("SM_VK_Rail_Straight",lambda k: ind_rail_straight(k),IND_NG),
 ("SM_VK_Rail_Curve",ind_rail_curve,IND_NG),
 ("SM_VK_Rail_End",ind_rail_end,IND_NG),
 ("SM_VK_Prop_Minecart",lambda k: ind_minecart(k),IND_NW),
 ("SM_VK_Pile_Ore_1",lambda k: ind_pile_ore(k,1),IND_NG),("SM_VK_Pile_Ore_2",lambda k: ind_pile_ore(k,2),IND_NG),("SM_VK_Pile_Ore_3",lambda k: ind_pile_ore(k,3),IND_NG),
 ("SM_VK_Pile_Coal_1",lambda k: ind_pile_coal(k,1),IND_NG),("SM_VK_Pile_Coal_2",lambda k: ind_pile_coal(k,2),IND_NG),("SM_VK_Pile_Coal_3",lambda k: ind_pile_coal(k,3),IND_NG),
 ("SM_VK_Quarry_Face_Straight",ind_quarry_face,IND_NG),
 ("SM_VK_Quarry_Face_Corner",ind_quarry_corner,IND_NG),
 ("SM_VK_Quarry_Face_InnerCorner",ind_quarry_innercorner,IND_NG),
 ("SM_VK_Quarry_Floor",ind_quarry_floor,IND_NG),
 ("SM_VK_Prop_Banker",ind_banker,IND_NG),
 ("SM_VK_Prop_TreadwheelCrane",ind_crane,IND_NG),
 ("SM_VK_Prop_TreadwheelCrane_Wheel",ind_crane_wheel,IND_NW),
 ("SM_VK_Prop_CharcoalMound",ind_charcoal_mound,IND_NG),
 ("SM_VK_Prop_Bloomery",ind_bloomery,IND_NG),
 ("SM_VK_Prop_Bellows",ind_bellows,IND_NG),
 ("SM_VK_Prop_BottleKiln",ind_bottle_kiln,IND_NG),
 ("SM_VK_Prop_ClayPit",ind_clay_pit,IND_NG),
 ("SM_VK_Prop_PottersWheel",ind_potters_wheel,IND_NG),
 ("SM_VK_Pile_Bricks_1",lambda k: ind_pile_bricks(k,1),IND_NG),("SM_VK_Pile_Bricks_2",lambda k: ind_pile_bricks(k,2),IND_NG),("SM_VK_Pile_Bricks_3",lambda k: ind_pile_bricks(k,3),IND_NG),
 ("SM_VK_Prop_TanningPit",ind_tanning_pit,IND_NG),
 ("SM_VK_Prop_HideFrame",ind_hide_frame,IND_NG),
 ("SM_VK_Prop_DyeVat",ind_dye_vat,IND_NG),
 ("SM_VK_Prop_ClothRack",ind_cloth_rack,IND_NG),
 ("SM_VK_Prop_Loom",ind_loom,IND_NG),
 ("SM_VK_Prop_SpinningWheel",ind_spinning_wheel,IND_NG),
 ("SM_VK_Pile_Hides_1",lambda k: ind_pile_hides(k,1),IND_NG),("SM_VK_Pile_Hides_2",lambda k: ind_pile_hides(k,2),IND_NG),("SM_VK_Pile_Hides_3",lambda k: ind_pile_hides(k,3),IND_NG),
 ("SM_VK_Pile_Wool_1",lambda k: ind_pile_wool(k,1),IND_NG),("SM_VK_Pile_Wool_2",lambda k: ind_pile_wool(k,2),IND_NG),("SM_VK_Pile_Wool_3",lambda k: ind_pile_wool(k,3),IND_NG),
 ("SM_VK_Kiln_Oast",ind_oast,IND_NG),
 ("SM_VK_Prop_MashTun",ind_mash_tun,IND_NG),
 ("SM_VK_Prop_CiderPress",ind_cider_press,IND_NG),
 ("SM_VK_Prop_Skep",lambda k: ind_skep(k),IND_NG),
 ("SM_VK_Prop_BeeBench",ind_bee_bench,IND_NG),
 ("SM_VK_Prop_HerbBundles",ind_herb_bundles,IND_NG),
 ("SM_VK_Prop_Cauldron",ind_cauldron,IND_NG),
 ("SM_VK_Prop_DryingRack_Meat",ind_drying_rack_meat,IND_NG),
 ("SM_VK_Prop_DryingRack_Herbs",ind_drying_rack_herbs,IND_NG),
 ("SM_VK_Prop_Dovecote",ind_dovecote,IND_NG),
]
EXTRA_SPECS+=WS_SPECS
