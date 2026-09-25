from mathutils import Quaternion

# =====================  NATURE KIT  =====================
LEAF_CELLS=["broadleaf","broadleaf_dark","autumn_orange","autumn_red","birch","pine","willow","fern",
            "berry","blossom","apple","hydrangea","reeds","tallgrass","wildflowers","deadtwigs"]
UP=Vector((0,0,1)); GOLD=2.39996
def leaf_uv(cell,m=0.004):
    i=LEAF_CELLS.index(cell); cx=i%4; cy=i//4
    return cx*0.25+m,(cx+1)*0.25-m,1-(cy+1)*0.25+m,1-cy*0.25-m
class NK(Kit):
    def __init__(s):
        Kit.__init__(s); s.nfn={}; s.vinfo={}; s.wind_fn=None; s.ao_fn=None
    def lcard(s,base,right,up,w,h,cell,flip=False,bend=0.0,arch=0.0,rows=2,cols=2,nfn=None,aofn=None,anchor="bottom",vr=None):
        u0,u1,v0,v1=leaf_uv(cell)
        if vr: v0,v1=v0+(v1-v0)*vr[0],v0+(v1-v0)*vr[1]      # use only a vertical band of the cell (0=bottom)
        if flip: u0,u1=u1,u0
        B=Vector(base); R=Vector(right).normalized(); U=Vector(up).normalized(); N=R.cross(U).normalized()
        if anchor=="top": B=B-U*h
        elif anchor=="center": B=B-U*h*0.5
        vs=[];uvs=[]
        for j in range(rows+1):
            for i in range(cols+1):
                a=i/cols; t=j/rows
                p=B+R*(a-0.5)*w+U*t*h+N*(bend*w*(1-(2*a-1)**2)+arch*h*t*t)
                v=s.bm.verts.new(p); vs.append(v); uvs.append((u0+(u1-u0)*a,v0+(v1-v0)*t))
        for j in range(rows):
            for i in range(cols):
                a=j*(cols+1)+i; q=(a,a+1,a+cols+2,a+cols+1)
                f=s.bm.faces.new([vs[x] for x in q]); f.material_index=LEAVES; f.smooth=True
                for l,x in zip(f.loops,q): l[s.uv].uv=uvs[x]
        for v in vs:
            if nfn: s.nfn[v]=nfn
            if aofn: s.vinfo[v]=aofn
        return vs
    def tube(s,pts,radii,segs,mi,tileU=1.2,tileV=1.2,flare=None,cap_end=True,cap_start=False,noise_amp=0.04,seed=0.0):
        n=len(pts)
        tans=[(pts[min(i+1,n-1)]-pts[max(i-1,0)]).normalized() for i in range(n)]
        nrm=tans[0].cross(Vector((0,0,1)) if abs(tans[0].z)<0.95 else Vector((1,0,0))).normalized(); fr=[]
        for i,t in enumerate(tans):
            if i>0: nrm=(tans[i-1].rotation_difference(t)@nrm).normalized()
            nrm=(nrm-t*nrm.dot(t)).normalized(); fr.append((t,nrm,t.cross(nrm)))
        avg=sum(radii)/len(radii); urep=max(1,round(2*math.pi*avg/tileU))
        rings=[]; vco=0.0
        for i,(p,r) in enumerate(zip(pts,radii)):
            if i>0: vco+=(pts[i]-pts[i-1]).length/tileV
            t,nn,bn=fr[i]; ring=[]
            for k in range(segs+1):
                th=2*math.pi*k/segs; kk=k%segs
                rr=r*(1+noise_amp*noise.noise(Vector((math.cos(th)*1.3,math.sin(th)*1.3,p.z*1.1+seed))))
                if flare: rr*=flare(th,p)
                if k<segs: ring.append(s.bm.verts.new(p+(nn*math.cos(th)+bn*math.sin(th))*rr))
            rings.append((ring,vco))
        for i in range(n-1):
            ra,va=rings[i]; rb,vb=rings[i+1]
            for k in range(segs):
                k2=(k+1)%segs
                f=s.bm.faces.new((ra[k],ra[k2],rb[k2],rb[k])); f.material_index=mi; f.smooth=True
                for l,uu,vv in zip(f.loops,(k/segs*urep,(k+1)/segs*urep,(k+1)/segs*urep,k/segs*urep),(va,va,vb,vb)): l[s.uv].uv=(uu,vv)
        def cap(ring,v,c,flip_):
            cv=s.bm.verts.new(c)
            for k in range(segs):
                q=(ring[k],ring[(k+1)%segs],cv) if not flip_ else (ring[(k+1)%segs],ring[k],cv)
                f=s.bm.faces.new(q); f.material_index=mi; f.smooth=True
                for l,(a,b_) in zip(f.loops,((0,v),(0.2,v),(0.1,v+0.06))): l[s.uv].uv=(a,b_)
        if cap_end: cap(rings[-1][0],rings[-1][1],pts[-1]+fr[-1][0]*radii[-1]*0.6,False)
        if cap_start: cap(rings[0][0],0.0,pts[0]-fr[0][0]*radii[0]*0.3,True)
        return rings
def grow(start,d,length,r0,r1,depth,rng,up=0.1,droop=0.0,wig=0.1,step=0.3,taper=0.8,seed=0.0):
    n=max(3,int(math.ceil(length/step))); p=Vector(start); d=Vector(d).normalized(); pts=[p.copy()]; rad=[r0]
    for i in range(1,n+1):
        t=i/n
        w=Vector((noise.noise(p*0.9+Vector((seed,depth*3.1,0.0))),noise.noise(p*0.9+Vector((0.0,seed+7.7,depth))),noise.noise(p*0.9+Vector((2.2,0.0,seed+5.0)))))
        d=(d+UP*up-UP*(droop*t)+w*wig).normalized()
        p=p+d*(length/n); pts.append(p.copy()); rad.append(r0+(r1-r0)*(t**taper))
    return {"pts":pts,"rad":rad,"depth":depth}
def point_at(b,t):
    P=b["pts"]; f=t*(len(P)-1); i=min(int(f),len(P)-2); a=f-i
    return P[i].lerp(P[i+1],a), b["rad"][i]*(1-a)+b["rad"][i+1]*a, (P[i+1]-P[i]).normalized()
def child_dir(tan,angle,azim):
    perp=tan.cross(Vector((0.3,0.2,1)) if abs(tan.z)<0.9 else Vector((1,0,0))).normalized()
    perp=Quaternion(tan,azim)@perp
    return (Quaternion(perp,angle)@tan).normalized()
def root_flare(n_lobes=5,amount=0.8,height=0.45,base=0.25,phase=0.7):
    def f(th,p):
        e=math.exp(-max(p.z,0.0)/height)
        return 1+e*(base+amount*max(0.0,math.cos(n_lobes*th+phase))**3)
    return f
def canopy_fns(C,ext,clump=None,wc=0.35,ao_lo=0.56):
    def nfn(p):
        d=p-C; n=Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z))
        n=n.normalized() if n.length>1e-6 else Vector((0,0,1))
        if clump is not None:
            c=p-clump
            if c.length>1e-6: n=(n*(1-wc)+c.normalized()*wc).normalized()
        return n
    def aofn(p):
        d=p-C; q=Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z)); outer=min(1.0,q.length)
        up=0.5+0.5*(q.normalized().z if q.length>1e-6 else 0.0)
        g=ao_lo+(1-ao_lo)*min(1.0,0.55*up+0.45*outer**1.5)
        return g,min(1.0,0.35+0.65*outer)
    return nfn,aofn
_CELL_UV={}
def cell_solid_uv(cell,atlas="T_VK_Leaves_BCA"):
    """uv of an opaque texel whose colour is the cell's median leaf colour (for the solid clump cores)"""
    if cell in _CELL_UV: return _CELL_UV[cell]
    import numpy as np
    im=bpy.data.images[atlas]; W,H=im.size
    if "_px" not in _CELL_UV:
        a=np.empty(W*H*4,np.float32); im.pixels.foreach_get(a); _CELL_UV["_px"]=a.reshape(H,W,4)
    px=_CELL_UV["_px"]; u0,u1,v0,v1=leaf_uv(cell)
    sub=px[int(v0*H):int(v1*H),int(u0*W):int(u1*W)]
    ok=sub[...,3]>0.95
    if not ok.any(): uv=((u0+u1)/2,(v0+v1)/2)
    else:
        med=np.median(sub[ok][:,:3],axis=0); d=((sub[...,:3]-med)**2).sum(-1)+(~ok)*9.0
        jj,ii=np.unravel_index(np.argmin(d),d.shape)
        uv=(u0+(ii+0.5)/W,v0+(jj+0.5)/H)
    _CELL_UV[cell]=uv; return uv
def clump_core(k,c,r,cell,nfn,aofn,rng,rad=0.5,dark=0.9):
    """opaque lumpy core inside a leaf clump: hides the see-through gaps and card intersections"""
    uv=cell_solid_uv(cell)
    res=bmesh.ops.create_icosphere(k.bm,subdivisions=1,radius=r*rad)
    vs=res["verts"]; ph=rng.uniform(0,100)
    for v in vs:
        v.co=Vector(c)+v.co*(1.0+0.18*noise.noise(v.co*2.2/max(r,0.1)+Vector((ph,0,0))))
    fs={f for v in vs for f in v.link_faces}
    # textured with the cell itself (planar map of the ball into the middle of the cell), so the core reads as
    # more foliage instead of a flat-coloured ball
    u0,u1,v0,v1=leaf_uv(cell); cu,cv=(u0+u1)/2,(v0+v1)/2; su,sv=(u1-u0)*0.42,(v1-v0)*0.42
    for f in fs:
        f.material_index=LEAVES; f.smooth=True
        for l in f.loops:
            d=(l.vert.co-Vector(c)); d=d/max(d.length,1e-6)
            l[k.uv].uv=(cu+d.x*su,cv+d.z*sv) if abs(d.y)>0.5 else (cu+d.y*su,cv+d.z*sv)
    def ao2(p,aofn=aofn):
        g,wa=aofn(p); return g*dark,wa
    for v in vs: k.nfn[v]=nfn; k.vinfo[v]=ao2
def clump_cards(k,c,r,n,cells,rng,C,ext,size=(0.9,1.3),shell=(0.15,0.85),wc=0.35,ao_lo=0.56,core=False,tangent=False):
    names=[x[0] for x in cells]; wts=[x[1] for x in cells]
    nfn,aofn=canopy_fns(C,ext,c,wc,ao_lo)
    if core: clump_core(k,c,r,rng.choices(names,wts)[0],nfn,aofn,rng)
    if tangent:
        # cards lie roughly tangent to the clump ball (scales on a sphere) instead of sticking out radially
        for i in range(n):
            zf=1-2*(i+0.5)/n; az=i*GOLD+rng.uniform(-0.3,0.3); s_=math.sqrt(max(0.0,1-zf*zf))
            d=Vector((s_*math.cos(az),s_*math.sin(az),zf))
            if d.z<-0.65 and rng.random()<0.6: continue
            base=c+d*r*rng.uniform(max(shell[0],0.55),max(shell[1],0.95))
            nrm=(d*0.6+Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-0.5,1)))*0.45).normalized()
            up=Vector((0,0,1))-nrm*nrm.z
            if up.length<0.2: up=Vector((1,0,0))-nrm*nrm.x
            up=(up.normalized()+Vector((rng.uniform(-.3,.3),rng.uniform(-.3,.3),0))).normalized()
            up=(up-nrm*up.dot(nrm)).normalized(); right=up.cross(nrm)
            sz=rng.uniform(*size)*0.85; cell=rng.choices(names,wts)[0]
            k.lcard(base,right,up,sz*0.95,sz,cell,flip=rng.random()<0.5,bend=0.14,nfn=nfn,aofn=aofn,anchor="center")
        return
    for i in range(n):
        zf=1-2*(i+0.5)/n; az=i*GOLD+rng.uniform(-0.3,0.3); s_=math.sqrt(max(0.0,1-zf*zf))
        d=Vector((s_*math.cos(az),s_*math.sin(az),zf))
        if d.z<-0.65 and rng.random()<0.6: continue
        base=c+d*r*rng.uniform(*shell)
        up=(d+Vector((rng.uniform(-.35,.35),rng.uniform(-.35,.35),rng.uniform(-0.1,0.4)))).normalized()
        right=up.cross(Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1))).normalized())
        if right.length<1e-3: right=up.cross(Vector((1,0,0)))
        sz=rng.uniform(*size); cell=rng.choices(names,wts)[0]
        k.lcard(base,right.normalized(),up,sz*0.95,sz,cell,flip=rng.random()<0.5,bend=0.08,nfn=nfn,aofn=aofn)
def nk_finish(k,name,coll,sharp=None,bark_ao=(0.62,0.8),moss_alpha=1.0,wind_H=8.0):
    bm=k.bm; bm.normal_update()
    for f in bm.faces:
        for l in f.loops:
            v=l.vert
            if v in k.vinfo:
                g,wa=k.vinfo[v](v.co)
            else:
                z=v.co.z
                g=bark_ao[0]+(1-bark_ao[0])*min(1.0,max(0.0,z)/bark_ao[1]) if bark_ao else 1.0
                rr=math.hypot(v.co.x,v.co.y)
                wa=moss_alpha if k.wind_fn is None else k.wind_fn(v.co)
            l[k.cl]=(g,g*0.98,g*0.95,wa)
    if sharp is not None:
        for e in bm.edges:
            if len(e.link_faces)==2 and e.calc_face_angle(0.0)>sharp: e.smooth=False
    for f in bm.faces: f.smooth=True
    bm.verts.index_update()
    normals=[None]*len(bm.verts)
    for v,fn in k.nfn.items(): normals[v.index]=fn(v.co)
    me=bpy.data.meshes.new(name+"__new"); bm.to_mesh(me); bm.free()
    allm=kit_mats(); used=sorted({p.material_index for p in me.polygons})
    remap={u:i for i,u in enumerate(used)}
    for p in me.polygons: p.material_index=remap[p.material_index]
    for u in used: me.materials.append(allm[u])
    if any(n is not None for n in normals):
        vn=[tuple(n) if n is not None else tuple(me.vertices[i].normal) for i,n in enumerate(normals)]
        me.normals_split_custom_set_from_vertices(vn)
    obj=bpy.data.objects.get(name)
    if obj is not None and obj.type=="MESH":
        old=obj.data; old.user_remap(me)
        if old.users==0: bpy.data.meshes.remove(old)
    else:
        obj=bpy.data.objects.new(name,me); coll.objects.link(obj)
    me.name=name
    obj.hide_render=True; obj.hide_viewport=True; obj["kit"]="VillageNature"
    return obj
def tree_wind(H,axis=(0.0,0.0)):
    def w(p):
        r=math.hypot(p.x-axis[0],p.y-axis[1])
        return min(1.0,max(0.0,(p.z/H)*0.25+(r/3.0)**1.5*0.6))
    return w
def cut_branch(b,frac):
    # copy of branch b that stops at `frac` of its arc length (the skeleton itself is left untouched,
    # so leaf cards placed along b do not move)
    P=b["pts"]; R=b["rad"]; seg=[(P[i+1]-P[i]).length for i in range(len(P)-1)]
    tgt=sum(seg)*max(0.0,min(1.0,frac)); acc=0.0; pts=[P[0].copy()]; rad=[R[0]]
    for i,sl in enumerate(seg):
        if acc+sl>=tgt:
            a=(tgt-acc)/sl if sl>1e-9 else 0.0
            if a>0.08 or len(pts)<2:
                a=max(a,0.08); pts.append(P[i].lerp(P[i+1],a)); rad.append(R[i]*(1-a)+R[i+1]*a)
            break
        acc+=sl; pts.append(P[i+1].copy()); rad.append(R[i+1])
    return {"pts":pts,"rad":rad,"depth":b["depth"]}
def bark_tubes(k,branches,mi,segs=(14,9,6,4),flare=None,tile=1.2,cut=None,rscale=None,ao=None,drop=None):
    # cut / rscale / ao / drop: optional per-depth tuples (index = branch depth, the last entry repeats).
    #   cut    fraction of the branch arc length that gets a tube (twig ends hidden inside the foliage)
    #   rscale radius multiplier (thinner twigs)
    #   ao     vertex-colour AO for those tubes: a number or fn(p)->g, None = nk_finish's default bark_ao.
    #          Stored in k.vinfo so nk_finish keeps it; darkens twigs seen through the leaf cards.
    #   drop   lowers the tube by drop x its (scaled) radius, so it sits under leaf cards that cross at the branch
    #          axis (pine needle-card pairs) and is covered from above
    def pick(t,d): return None if t is None else t[min(d,len(t)-1)]
    for b in branches:
        d=b["depth"]; sg=segs[min(d,len(segs)-1)]
        mid=mi[min(d,len(mi)-1)] if isinstance(mi,(tuple,list)) else mi
        c=pick(cut,d); rs=pick(rscale,d); a=pick(ao,d); dr=pick(drop,d); bb=b
        if c is not None and c<0.999: bb=cut_branch(b,c)
        if rs is not None and rs!=1.0: bb={"pts":bb["pts"],"rad":[r*rs for r in bb["rad"]],"depth":d}
        if dr: bb={"pts":[p-UP*(r*dr) for p,r in zip(bb["pts"],bb["rad"])],"rad":bb["rad"],"depth":d}
        n0=len(k.bm.verts)
        k.tube(bb["pts"],bb["rad"],sg,mid,tileU=tile,tileV=tile,flare=flare if d==0 else None,cap_end=True,noise_amp=0.05 if d<2 else 0.02,seed=len(b["pts"])*0.37)
        if a is not None:
            gf=a if callable(a) else (lambda p,a=a: a)
            fn=lambda p,gf=gf: (gf(p), k.wind_fn(p) if k.wind_fn else 1.0)
            k.bm.verts.ensure_lookup_table()
            for i in range(n0,len(k.bm.verts)): k.vinfo[k.bm.verts[i]]=fn
def canopy_bounds(clumps):
    C=sum((c for c,r in clumps),Vector())/len(clumps)
    ext=Vector((max(abs(c.x-C.x)+r for c,r in clumps),max(abs(c.y-C.y)+r for c,r in clumps),max(abs(c.z-C.z)+r for c,r in clumps)))
    return C,ext
# ---------------- skeletons ----------------
def sk_broad(seed,trunkH=3.2,spread=1.0,nl=(3,4),limb_len=(2.6,3.4),limb_ang=(35,55),sub_len=(1.2,1.9),r0=0.48,wig=0.12,lower=True):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.4),(rng.uniform(-0.08,0.08),rng.uniform(-0.08,0.08),1),trunkH,r0,r0*0.66,0,rng,up=0.03,wig=0.06,step=0.3,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(*nl)
    for kk in range(n):
        az=kk*2*math.pi/n+rng.uniform(-0.3,0.3); d=child_dir(tt,math.radians(rng.uniform(*limb_ang)),az)
        limbs.append(grow(tp-tt*0.3,d,rng.uniform(*limb_len)*spread,tr*0.72,0.07,1,rng,up=0.07,wig=wig,step=0.3,seed=seed+kk))
    if lower:
        p,r,tan=point_at(trunk,0.66); limbs.append(grow(p,child_dir(tan,math.radians(62),rng.uniform(0,6.28)),limb_len[0]*0.85*spread,r*0.5,0.06,1,rng,up=0.1,wig=wig,seed=seed+9))
    B+=limbs; subs=[]
    for li,L in enumerate(limbs):
        for kk in range(3):
            t=0.4+0.55*(kk+rng.random()*0.5)/3; p,r,tan=point_at(L,min(t,0.95))
            d=child_dir(tan,math.radians(rng.uniform(35,60)),li*1.7+kk*GOLD)
            if d.z<-0.1: d.z=-0.1; d.normalize()
            subs.append(grow(p,d,rng.uniform(*sub_len)*spread,r*0.7,0.035,2,rng,up=0.08,wig=wig*1.2,step=0.25,seed=seed+20+li*5+kk))
    B+=subs
    return B,limbs,subs
def broad_clumps(limbs,subs,rng,scale=1.0):
    cl=[]
    for b in subs:
        cl.append((b["pts"][-1],rng.uniform(0.95,1.25)*scale)); cl.append((point_at(b,0.5)[0]+Vector((0,0,0.2)),rng.uniform(0.8,1.0)*scale))
    for b in limbs: cl.append((b["pts"][-1]+Vector((0,0,0.2)),rng.uniform(1.1,1.35)*scale))
    out=[]
    for c in cl:
        if all((c[0]-o[0]).length>0.33*(c[1]+o[1]) for o in out): out.append(c)
    return out
def make_broad_tree(k,seed,cells,bark=BARK_OAK,trunkH=3.2,spread=1.0,cards=36,size=(1.0,1.45),clump_scale=1.0,**kw):
    B,limbs,subs=sk_broad(seed,trunkH=trunkH,spread=spread,**kw)
    rng=random.Random(seed+1)
    H=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(H+1.5)
    bark_tubes(k,B,bark,flare=root_flare())
    cl=broad_clumps(limbs,subs,rng,clump_scale); C,ext=canopy_bounds(cl)
    for (c,r) in cl: clump_cards(k,c,r,cards,cells,rng,C,ext,size=size)
    return B

def make_pine(k,seed,H=10.0,Rmax_f=0.30,cards_step=0.42,size=(1.35,1.85),young=False):
    rng=random.Random(seed)
    trunk=grow((0,0,-0.3),(rng.uniform(-0.03,0.03),rng.uniform(-0.03,0.03),1),H,0.34*H/10,0.03,0,rng,up=0.02,wig=0.03,step=0.4,taper=1.0,seed=seed)
    B=[trunk]; Rmax=H*Rmax_f
    z=(1.5 if not young else 0.45)*H/10
    whorl=0
    while z<H-0.6:
        t=(z+0.3)/(H+0.3); p,r,tan=point_at(trunk,min(0.98,t))
        nb=rng.randint(6,8); az0=rng.uniform(0,6.28)
        for j in range(nb):
            az=az0+j*2*math.pi/nb+rng.uniform(-0.2,0.2)
            frac=(H-z)/H
            L=(Rmax*frac**0.85+0.4)*rng.uniform(0.85,1.1)
            dz=-0.38+0.5*(z/H)
            d=Vector((math.cos(az),math.sin(az),dz)).normalized()
            B.append(grow(p,d,L,max(0.03,r*0.45),0.015,1,rng,up=0.09,droop=0.05,wig=0.05,step=0.45,seed=seed+whorl*10+j))
        whorl+=1; z+=rng.uniform(0.42,0.58)*H/10
    top=max(p.z for p in trunk["pts"])
    k.wind_fn=tree_wind(H+1)
    # whorl branches: thinner (0.6x), tube stops at 65% of the axis (the needle cards cover the rest), dropped
    # below the axis where each branch's two rolled needle cards cross (so the cards cover it from above) and
    # darkened so the stubs that show between cards read as shadow, not as brown sticks.
    # Trunk: darkened inside the crown (it showed as an orange stripe through the gaps), down to ~0.3 just above
    # the crown base and ~0.22 at the top, and the leader stops at 90% of the trunk (inside the apex cards; it
    # showed as a red dash at every crown tip from above).
    z_cr=(1.5 if not young else 0.45)*H/10
    def trunk_ao(p):
        base=0.62+0.38*min(1.0,max(0.0,p.z)/0.8)
        a=1.0-0.7*min(1.0,max(0.0,p.z-z_cr)/(0.8*H/10))
        a-=0.08*min(1.0,max(0.0,p.z-0.6*H)/(0.3*H))
        return min(base,a)
    bark_tubes(k,B,(BARK_PINE,BARK_OAK),segs=(12,3,3,3),flare=root_flare(6,0.45,0.35,0.18),tile=1.4,
               cut=(0.9,0.65),rscale=(1.0,0.6),ao=(trunk_ao,0.34),drop=(0.0,1.6))
    def nfn(p):
        rad=Vector((p.x,p.y,0)); R=max(0.2,Rmax*max(0.05,(H-p.z)/H)+0.4)
        n=rad/R*0.85+Vector((0,0,0.5+0.45*(p.z/H)))
        return n.normalized() if n.length>1e-6 else Vector((0,0,1))
    def aofn(p):
        rad=math.hypot(p.x,p.y); R=max(0.2,Rmax*max(0.05,(H-p.z)/H)+0.4)
        g=0.56+0.44*min(1.0,0.5*min(1.0,rad/R)+0.5*(p.z/H)+0.1)
        return g,min(1.0,0.3+0.7*min(1.0,rad/R))
    for b in B[1:]:
        P=b["pts"]; Lb=sum((P[i+1]-P[i]).length for i in range(len(P)-1))
        n=max(2,int(Lb/cards_step)+1)
        for i in range(n):
            tt=0.1+0.9*i/max(1,n-1)
            p,r,tan=point_at(b,min(tt,0.999))
            side=Vector((-tan.y,tan.x,0)).normalized() if abs(tan.z)<0.99 else Vector((1,0,0))
            sz=rng.uniform(*size)*(1-0.3*tt)*(H/10)**0.5
            for roll in (rng.uniform(0.3,0.55),-rng.uniform(0.3,0.55)):
                R=Quaternion(tan,roll)@side
                k.lcard(p-tan*0.1,R,tan,sz*0.95,sz,"pine",flip=rng.random()<0.5,bend=0.12,rows=1,cols=2,nfn=nfn,aofn=aofn)
    tip=trunk["pts"][-1]
    for j in range(6):
        a=j*2*math.pi/6+rng.uniform(-0.2,0.2); up=Vector((math.cos(a)*0.3,math.sin(a)*0.3,1)).normalized()
        right=Vector((-math.sin(a),math.cos(a),0))
        k.lcard(tip-Vector((0,0,1.3*H/10)),right,up,1.0*H/10,1.7*H/10,"pine",flip=j%2==0,bend=0.1,rows=1,cols=2,nfn=nfn,aofn=aofn)
    return B

def make_birch(k,seed,H=8.5,stems=2):
    rng=random.Random(seed); B=[]; clumps=[]
    for si in range(stems):
        a=si*2*math.pi/stems+rng.uniform(-0.4,0.4); lean=rng.uniform(0.07,0.16) if stems>1 else rng.uniform(0.0,0.05)
        base=Vector((math.cos(a)*0.18*(stems>1),math.sin(a)*0.18*(stems>1),-0.3))
        d=Vector((math.cos(a)*lean,math.sin(a)*lean,1))
        Ht=H*rng.uniform(0.85,1.0)
        tr=grow(base,d,Ht,0.2,0.04,0,rng,up=0.02,wig=0.05,step=0.4,taper=0.9,seed=seed+si); B.append(tr)
        n=int(Ht/0.42)
        for j in range(n):
            t=0.32+0.64*j/max(1,n-1)
            p,r,tan=point_at(tr,t)
            az=j*GOLD+si*1.3+rng.uniform(-0.3,0.3)
            dd=child_dir(tan,math.radians(rng.uniform(32,50)),az)
            L=rng.uniform(1.0,2.2)*(1-0.55*t)+0.5
            br=grow(p,dd,L,max(0.02,r*0.35),0.01,1,rng,up=0.02,droop=0.55,wig=0.1,step=0.3,seed=seed+si*50+j); B.append(br)
            clumps.append((br["pts"][-1],rng.uniform(0.55,0.8))); clumps.append((point_at(br,0.55)[0],rng.uniform(0.45,0.65)))
    H2=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(H2+1)
    # white birch bark only on the stems; the branches get the darker oak bark (thin birch twigs are dark),
    # are thinner and stop at 80% so their tips stay inside the end leaf clump; AO 0.8 keeps them brown (at 0.6
    # they read as near-black wires under the canopy on the shade side).
    # The stems stop at 86% (inside the top clumps) and are greyed inside the crown (55%..80% of the height), so
    # they no longer show as white dashes through canopy gaps; the white bole below the crown is unchanged.
    z0=0.55*H2; z1=0.8*H2
    def stem_ao(p):
        base=0.62+0.38*min(1.0,max(0.0,p.z)/0.8)
        return min(base,1.0-0.45*min(1.0,max(0.0,p.z-z0)/(z1-z0)))
    bark_tubes(k,B,(BARK_BIRCH,BARK_OAK),segs=(10,4,4,4),flare=root_flare(4,0.3,0.3,0.12),tile=1.0,
               cut=(0.86,0.8),rscale=(1.0,0.7),ao=(stem_ao,0.8))
    C,ext=canopy_bounds(clumps)
    for (c,r) in clumps: clump_cards(k,c,r,11,[("birch",1.0)],rng,C,ext,size=(0.7,1.0),shell=(0.1,0.8),ao_lo=0.72)
    return B
def make_willow(k,seed,H=3.0,R=3.9,Rz=2.3):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.4),(rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),1),H*0.85,0.5,0.36,0,rng,up=0.02,wig=0.08,step=0.3,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(5,6)
    for j in range(n):
        az=j*2*math.pi/n+rng.uniform(-0.25,0.25); d=child_dir(tt,math.radians(rng.uniform(45,62)),az)
        L_=grow(tp-tt*0.25,d,rng.uniform(3.0,3.8),tr*0.6,0.06,1,rng,up=0.18,droop=0.3,wig=0.1,step=0.3,seed=seed+j)
        Cq=Vector((0,0,tp.z+0.2)); keep=[]
        for pp in L_["pts"]:
            dq=pp-Cq
            if (dq.x/R)**2+(dq.y/R)**2+(max(dq.z,0)/Rz)**2>0.72 and len(keep)>2: break
            keep.append(pp)
        L_["pts"]=keep; L_["rad"]=L_["rad"][:len(keep)]
        limbs.append(L_)
    B+=limbs
    k.wind_fn=tree_wind(tp.z+Rz+1)
    # limb tubes end inside their crown clumps (they poked out of the top) and are a bit darker in the canopy
    bark_tubes(k,B,BARK_OAK,segs=(14,8,5,4),flare=root_flare(5,0.7,0.4,0.2),cut=(1.0,0.82),ao=(None,0.72))
    C=Vector((0,0,tp.z+0.2))
    # ---- leaves: broad drooping leaf clumps over the dome (clump_cards style, "willow" cell = v2 weeping-clump
    # texture: rounded lit top + hanging strands) + a light curtain of hanging strands at the rim.
    # Normals: gradient of the canopy ellipsoid (R,R,Rz) (the flat dome's crown faces up, not sideways as with the
    # old normalised-q "sphere" normals), blended with the clump normal (readable lumps) plus an up bias that grows
    # towards the crown, so the far half of the crown is not on the shadow line from a high camera. Below the
    # equator the downward part is flattened so the skirt/underside faces outwards; AO floor ao_lo>=0.72 so the
    # underside never goes near-black.
    def wfns(clump=None,wc=0.6,ao_lo=0.72,upb0=0.3):
        def nfn(p):
            d=p-C; q=Vector((d.x/(R*R),d.y/(R*R),d.z/(Rz*Rz)))
            if q.z<0: q.z*=0.3
            n=q.normalized() if q.length>1e-9 else UP.copy()
            upb=upb0+0.8*max(0.0,min(1.0,d.z/Rz+0.2))                 # global dome: flatter towards the crown
            n=(n+UP*upb).normalized()
            if clump is not None:                                       # strong per-clump ball -> readable lumps
                c=p-clump
                if c.length>1e-6:
                    c=c.normalized(); c.z=max(c.z,-0.2); n=(n*(1-wc)+c.normalized()*wc).normalized()
            return (n+UP*0.12).normalized()
        def aofn(p):
            d=p-C; q=Vector((d.x/R,d.y/R,d.z/Rz)); outer=min(1.0,q.length)
            up=0.5+0.5*max(-1.0,min(1.0,d.z/Rz))
            g=ao_lo+(1-ao_lo)*min(1.0,0.5*up+0.5*outer**1.5)
            if clump is not None:                                       # crevice between clumps (floor stays 0.7)
                c=p-clump
                lc=0.5+0.5*(c.z/c.length) if c.length>1e-6 else 1.0
                g=max(0.7,g*(0.72+0.28*lc))
            return g,min(1.0,0.4+0.6*outer)
        return nfn,aofn
    def dome(th,ph,s=1.0):
        return C+Vector((math.sin(th)*math.cos(ph)*R,math.sin(th)*math.sin(ph)*R,math.cos(th)*Rz))*s
    az_l=sorted(math.atan2(L_["pts"][-1].y,L_["pts"][-1].x) for L_ in limbs)
    cl=[(C+Vector((0,0,Rz*0.48)),1.45,True)]                                     # crown
    for L_ in limbs:                                                              # over each limb end
        cl.append((L_["pts"][-1]-Vector((0,0,0.25)),rng.uniform(1.2,1.3),False))
    nsh=8
    for j in range(nsh):                                                          # shoulder ring (the dome's rim)
        cl.append((dome(math.radians(72),az_l[0]+(j+0.5)*2*math.pi/nsh+rng.uniform(-0.12,0.12),0.75),rng.uniform(1.2,1.3),False))
    nin=5
    for j in range(nin):                                                          # inner ring (closes the crown gaps)
        cl.append((dome(math.radians(40),az_l[0]+j*2*math.pi/nin+rng.uniform(-0.15,0.15),0.8),rng.uniform(1.05,1.15),True))
    def wclump(c,r,n,top=False):
        # drooping clump: weeping-clump cards laid over the upper part of a ball and hanging past its lower edge
        # (hair over a ball), card normals ~ the clump radial so each clump shades as one lump. The card top curls
        # in over the ball (negative arch) so no card edge sticks up out of the crown outline.
        # top=True (crown clumps, seen from above): shorter cards (the cell squashed vertically: stubbier strands,
        # the dense rounded top dominates) so the crown reads as solid lumps rather than hanging strands.
        # Cards hang steeply (weeping) so none sticks out sideways like a flat wing at the rim; 3 cap cards lie over
        # the top of the ball (rounded texture top at the pole, strands running out and slightly down, ends dipping
        # into the ball) so a clump seen from above is a solid lit lump, not a ring of hanging cards.
        nfn,aofn=wfns(c); hf=0.62 if top else 1.0
        a0=rng.uniform(0,6.28)
        for j in range(3):
            az=a0+j*2*math.pi/3+rng.uniform(-0.35,0.35); dh=Vector((math.cos(az),math.sin(az),0))
            tl=math.radians(rng.uniform(20,32)); down=(dh*math.cos(tl)-UP*math.sin(tl)).normalized()
            right=Vector((-math.sin(az),math.cos(az),0))
            k.lcard(c+UP*r*0.88-dh*r*0.22,right,-down,rng.uniform(1.25,1.45)*r,r*rng.uniform(1.05,1.2),"willow",
                    flip=rng.random()<0.5,bend=0.15,rows=3,cols=2,nfn=nfn,aofn=aofn,anchor="top")
        for i in range(n):
            zf=1-1.25*((i+0.5)/n)**1.25; az=i*GOLD+rng.uniform(-0.3,0.3); s_=math.sqrt(max(0.0,1-zf*zf))
            d=Vector((s_*math.cos(az),s_*math.sin(az),zf))
            t=Vector((0,0,-1))+d*d.z
            if t.length<0.35: t=Vector((math.cos(az),math.sin(az),-1.3))
            down=(t.normalized()*0.72+Vector((0,0,-0.55))+Vector((rng.uniform(-.12,.12),rng.uniform(-.12,.12),0))).normalized()
            right=Quaternion(down,rng.uniform(-0.35,0.35))@d.cross(down)
            right=(right-down*right.dot(down)).normalized()
            h=rng.uniform(1.35,1.75)*r/1.3*hf; arch=-0.12
            tp_=c+d*r*rng.uniform(0.6,0.82)-right.cross(-down).normalized()*arch*h
            k.lcard(tp_,right,-down,rng.uniform(1.45,1.8)*r/1.3,h,"willow",flip=rng.random()<0.5,
                    bend=0.18,arch=arch,rows=3,cols=2,nfn=nfn,aofn=aofn,anchor="top")
    for (c,r,top) in cl: wclump(c,r,15,top)
    # light curtain of hanging strands at the rim (lower, strand-only part of the willow cell)
    nfn_c,aofn_c=wfns(None,upb0=0.65)                                           # lighter (more up-facing) curtain
    M=44
    for i in range(M):
        if rng.random()<0.2: continue
        ph=i*2*math.pi/M+rng.uniform(-0.05,0.05)
        top=dome(math.radians(rng.uniform(72,92)),ph,rng.uniform(0.86,0.95))
        rd=Vector((math.cos(ph),math.sin(ph),0))
        rem=max(0.6,top.z-rng.uniform(0.5,1.5))
        up=(UP-rd*0.12).normalized(); right=Vector((-math.sin(ph),math.cos(ph),0))
        while rem>0.35:
            h=min(1.6,rem)
            k.lcard(top,right,up,rng.uniform(0.6,0.85),h,"willow",flip=rng.random()<0.5,bend=0.1,rows=2,cols=1,nfn=nfn_c,aofn=aofn_c,anchor="top",vr=(0.0,0.55))
            top=top-up*(h*0.88); rem-=h*0.88
            right=Quaternion(UP,rng.uniform(-0.3,0.3))@right
    return B
def make_fruit(k,seed,cells,spread=1.0,cards=34,size=(0.85,1.2)):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.3),(rng.uniform(-0.12,0.12),rng.uniform(-0.12,0.12),1),1.7,0.24,0.17,0,rng,up=0.02,wig=0.12,step=0.25,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(4,5)
    for j in range(n):
        az=j*2*math.pi/n+rng.uniform(-0.3,0.3); d=child_dir(tt,math.radians(rng.uniform(40,62)),az)
        limbs.append(grow(tp-tt*0.2,d,rng.uniform(1.6,2.2)*spread,tr*0.7,0.04,1,rng,up=0.12,wig=0.18,step=0.25,seed=seed+j))
    B+=limbs; subs=[]
    for li,L in enumerate(limbs):
        for j in range(3):
            p,r,tan=point_at(L,0.35+0.2*j+rng.uniform(0,0.1)); d=child_dir(tan,math.radians(rng.uniform(35,60)),li*1.9+j*GOLD)
            subs.append(grow(p,d,rng.uniform(0.7,1.1)*spread,r*0.65,0.02,2,rng,up=0.12,wig=0.2,step=0.22,seed=seed+20+li*4+j))
    B+=subs
    H=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(H+1)
    bark_tubes(k,B,BARK_OAK,segs=(10,7,5,4),flare=root_flare(4,0.5,0.3,0.15))
    cl=[(b["pts"][-1],rng.uniform(0.75,0.95)) for b in subs]+[(b["pts"][-1]+Vector((0,0,0.1)),0.95) for b in limbs]
    out=[]
    for c in cl:
        if all((c[0]-o[0]).length>0.3*(c[1]+o[1]) for o in out): out.append(c)
    C,ext=canopy_bounds(out)
    for (c,r) in out: clump_cards(k,c,r,cards//2,cells,rng,C,ext,size=size,ao_lo=0.64)
    return B
def make_dead(k,seed):
    rng=random.Random(seed)
    B,limbs,subs=sk_broad(seed,trunkH=2.8,spread=0.95,nl=(3,4),limb_len=(2.2,3.0),limb_ang=(30,58),sub_len=(1.0,1.6),r0=0.42,wig=0.3)
    # break a few branch ends
    for b in subs:
        if rng.random()<0.35:
            cut=max(3,int(len(b["pts"])*rng.uniform(0.4,0.7))); b["pts"]=b["pts"][:cut]; b["rad"]=b["rad"][:cut]
    H=max(p.z for bb in B for p in bb["pts"])
    k.wind_fn=tree_wind(H+1)
    bark_tubes(k,B,BARK_MOSSY,flare=root_flare(5,0.9,0.45,0.25))
    tw=[]
    for b in subs+limbs:
        p=b["pts"][-1]; tan=(b["pts"][-1]-b["pts"][-2]).normalized()
        tw.append((p,tan))
    C=sum((p for p,t in tw),Vector())/len(tw); ext=Vector((3,3,2))
    nfn,aofn=canopy_fns(C,ext,None,0.0,0.7)
    for (p,tan) in tw:
        for j in range(2):
            right=tan.cross(Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1))).normalized())
            if right.length<1e-3: continue
            k.lcard(p-tan*0.1,right.normalized(),(tan+Vector((0,0,0.3))).normalized(),rng.uniform(0.8,1.2),rng.uniform(0.9,1.3),"deadtwigs",flip=j%2==0,bend=0.05,nfn=nfn,aofn=aofn)
    return B
def make_sapling(k,seed):
    rng=random.Random(seed)
    tr=grow((0,0,-0.2),(rng.uniform(-0.05,0.05),rng.uniform(-0.05,0.05),1),2.6,0.07,0.015,0,rng,up=0.02,wig=0.08,step=0.25,seed=seed)
    B=[tr]; cl=[]
    for j in range(6):
        p,r,tan=point_at(tr,0.4+0.1*j); d=child_dir(tan,math.radians(rng.uniform(35,55)),j*GOLD)
        b=grow(p,d,rng.uniform(0.5,0.9),r*0.6,0.01,1,rng,up=0.1,wig=0.15,step=0.2,seed=seed+j); B.append(b); cl.append((b["pts"][-1],0.45))
    cl.append((tr["pts"][-1],0.5))
    k.wind_fn=tree_wind(3.5)
    bark_tubes(k,B,BARK_OAK,segs=(6,4,4,4),flare=None)
    C,ext=canopy_bounds(cl)
    for (c,r) in cl: clump_cards(k,c,r,12,[("broadleaf",1.0)],rng,C,ext,size=(0.55,0.8),ao_lo=0.65)
    # support stake + ties
    k.box((0.14,0.0,0.7),(0.05,0.05,1.6),WOOD,bevel=0.01)
    for z in (0.5,1.2): k.box((0.07,0,z),(0.16,0.04,0.04),BURLAP,bevel=0.01)
    return B

# =====================  BUSHES / PLANTS  =====================
def plant_fns(center=Vector((0,0,0)),H=1.0,ao_lo=0.76,radw=0.45):
    def nfn(p):
        rad=Vector((p.x-center.x,p.y-center.y,0))
        n=Vector((0,0,1))+ (rad.normalized()*radw if rad.length>1e-4 else Vector((0,0,0)))
        return n.normalized()
    def aofn(p):
        t=max(0.0,min(1.0,(p.z-center.z)/H)); return ao_lo+(1-ao_lo)*t, min(1.0,0.2+0.8*t)
    return nfn,aofn
def make_bush(k,seed,cells,R=0.9,H=1.1,nclump=4,cards=22,size=(0.6,0.9)):
    rng=random.Random(seed); cl=[]
    for i in range(nclump):
        a=i*GOLD+rng.uniform(-0.4,0.4); d=rng.uniform(0.15,0.5)*R if i else 0.0
        c=Vector((math.cos(a)*d,math.sin(a)*d,H*rng.uniform(0.45,0.6))); cl.append((c,rng.uniform(0.55,0.75)*R))
    for i in range(3):
        a=rng.uniform(0,6.28); k.tube([Vector((0,0,-0.1)),Vector((math.cos(a)*0.2,math.sin(a)*0.2,0.45))],[0.05,0.025],5,WOOD,cap_end=True)
    C,ext=canopy_bounds(cl); ext.z=max(ext.z,H*0.6)
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z/H))
    for (c,r) in cl: clump_cards(k,c,r,cards,cells,rng,C,ext,size=size,shell=(0.2,0.9),ao_lo=0.62)
def make_fern(k,seed,n=11,Hs=(0.9,1.3),c=(0,0,0)):
    rng=random.Random(seed); C0=Vector(c); nfn,aofn=plant_fns(center=C0,H=1.0,ao_lo=0.72,radw=0.6)
    for i in range(n):
        a=i*2*math.pi/n+rng.uniform(-0.25,0.25); out=Vector((math.cos(a),math.sin(a),0))
        up=(out*rng.uniform(0.55,0.9)+Vector((0,0,1))).normalized(); right=Vector((-math.sin(a),math.cos(a),0))
        h=rng.uniform(*Hs)
        k.lcard(C0+Vector((0,0,0.02))+out*0.05,right,up,h*0.62,h,"fern",flip=rng.random()<0.5,bend=0.04,arch=-0.28,rows=3,cols=2,nfn=nfn,aofn=aofn)
    for i in range(3):
        a=rng.uniform(0,6.28); up=Vector((math.cos(a)*0.2,math.sin(a)*0.2,1)).normalized(); right=Vector((-math.sin(a),math.cos(a),0))
        k.lcard(C0,right,up,0.45,0.75,"fern",flip=i%2==0,bend=0.04,arch=-0.1,rows=2,cols=1,nfn=nfn,aofn=aofn)
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z))
def make_tufts(k,seed,cell,n=9,R=0.6,Hs=(0.8,1.2),W=0.8,pairs=2,c0=(0,0,0)):
    rng=random.Random(seed); C0=Vector(c0); nfn,aofn=plant_fns(center=C0,H=max(Hs),ao_lo=0.78,radw=0.35)
    for i in range(n):
        a=rng.uniform(0,6.28); d=R*math.sqrt(rng.random()); c=C0+Vector((math.cos(a)*d,math.sin(a)*d,-0.02))
        h=rng.uniform(*Hs); rot=rng.uniform(0,3.14)
        for j in range(pairs):
            aa=rot+j*math.pi/pairs; right=Vector((math.cos(aa),math.sin(aa),0))
            up=Vector((rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),1)).normalized()
            k.lcard(c,right,up,W*h,h,cell,flip=rng.random()<0.5,bend=0.05,rows=2,cols=2,nfn=nfn,aofn=aofn)
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z/max(Hs)))
def mushroom(k,c,h,r,cap_mi,seed=0,spots=False,tilt=0.0,shape="dome"):
    rng=random.Random(seed); cx,cy,cz=c
    M=Matrix.Translation(Vector(c))@Matrix.Rotation(tilt,4,Vector((rng.uniform(-1,1),rng.uniform(-1,1),0)).normalized() if tilt else "Z")
    sub=Kit()
    stem=[(r*0.28,0.0),(r*0.24,h*0.4),(r*0.2,h*0.9),(r*0.22,h)]
    lathe(sub,stem,segs=10,mi=MUSH_STEM,smooth_=True)
    if shape=="dome":
        prof=[(r*0.2,h*0.92),(r*0.95,h*0.92),(r*1.0,h*1.02),(r*0.9,h*1.25),(r*0.6,h*1.42),(r*0.25,h*1.5),(0.0,h*1.52)]
    elif shape=="cone":
        prof=[(r*0.2,h*0.92),(r*0.9,h*0.9),(r*0.7,h*1.2),(r*0.35,h*1.5),(0.0,h*1.7)]
    else:
        prof=[(r*0.2,h*0.95),(r*1.0,h*0.98),(r*1.05,h*1.08),(r*0.7,h*1.16),(0.0,h*1.2)]
    lathe(sub,prof,segs=16,mi=cap_mi,smooth_=True)
    if spots:
        for i in range(9):
            a=i*GOLD; rr=r*rng.uniform(0.3,0.8); zz=h*1.52-(rr/r)**2*h*0.55
            vs=_ico(sub,(math.cos(a)*rr,math.sin(a)*rr,zz+0.005),r*0.1,MUSH_STEM,(1,1,0.4),sub=1)
    for f in sub.bm.faces: f.smooth=True
    merge_kit(k,sub,M)
def make_mushrooms(k,seed,kind="red"):
    rng=random.Random(seed)
    n={"red":4,"brown":6,"glow":7}[kind]
    for i in range(n):
        a=i*GOLD; d=rng.uniform(0.0,0.35) if i else 0.0
        c=(math.cos(a)*d,math.sin(a)*d,-0.01)
        if kind=="red": mushroom(k,c,rng.uniform(0.14,0.3),rng.uniform(0.08,0.15),MUSH_RED,seed=i,spots=True,tilt=rng.uniform(0,0.2))
        elif kind=="brown": mushroom(k,c,rng.uniform(0.08,0.18),rng.uniform(0.05,0.1),MUSH_BROWN,seed=i,tilt=rng.uniform(0,0.25),shape="flat")
        else: mushroom(k,c,rng.uniform(0.2,0.45),rng.uniform(0.05,0.09),MUSH_GLOW,seed=i,tilt=rng.uniform(0,0.3),shape="cone")
    k.wind_fn=lambda p: 0.0
def endcap(k,c,axis,r,seed=0):
    """disc with end-grain UVs facing along axis"""
    ax=Vector(axis).normalized(); t1=ax.cross(Vector((0,0,1)) if abs(ax.z)<0.9 else Vector((1,0,0))).normalized(); t2=ax.cross(t1)
    n=16; ring=[k.bm.verts.new(Vector(c)+(t1*math.cos(2*math.pi*i/n)+t2*math.sin(2*math.pi*i/n))*r) for i in range(n)]
    ctr=k.bm.verts.new(Vector(c)+ax*0.01)
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[(i+1)%n])); f.material_index=ENDGRAIN; f.smooth=True
        for l in f.loops:
            d=l.vert.co-Vector(c); l[k.uv].uv=(0.5+d.dot(t1)/r*0.44,0.5+d.dot(t2)/r*0.44)
    k.bm.normal_update()
    if f.normal.dot(ax)<0:
        for ff in ctr.link_faces: ff.normal_flip()
def bracket_fungus(k,c,out,r,seed=0):
    rng=random.Random(seed); o=Vector(out).normalized(); side=o.cross(Vector((0,0,1))).normalized()
    for j in range(3):
        cc=Vector(c)+Vector((0,0,-j*r*0.7))+side*rng.uniform(-r,r)*0.5
        prof=[]
        vs=[]
        n=9
        ring=[]
        for i in range(n+1):
            a=math.pi*i/n; p=cc+side*math.cos(a)*r*(1-0.15*j)+o*math.sin(a)*r*0.8*(1-0.15*j)
            ring.append(p)
        top=[k.bm.verts.new(p+Vector((0,0,0.03))) for p in ring]; bot=[k.bm.verts.new(p-Vector((0,0,0.02))) for p in ring]
        ct=k.bm.verts.new(cc+Vector((0,0,0.05))); cb=k.bm.verts.new(cc-Vector((0,0,0.02)))
        fs=[]
        for i in range(n):
            fs.append(k.bm.faces.new((ct,top[i],top[i+1]))); fs.append(k.bm.faces.new((cb,bot[i+1],bot[i]))); fs.append(k.bm.faces.new((top[i],bot[i],bot[i+1],top[i+1])))
        for f in fs: f.material_index=MUSH_BROWN; f.smooth=True
        k.bm.normal_update()
        for f in fs:
            if f.calc_center_median().z>cc.z+0.02 and f.normal.z<0: f.normal_flip()
def make_stump(k,seed):
    rng=random.Random(seed)
    pts=[Vector((0,0,-0.2)),Vector((0,0,0.2)),Vector((0.02,0,0.45)),Vector((0.03,0.01,0.62))]
    k.tube(pts,[0.46,0.44,0.42,0.42],14,BARK_MOSSY,tileU=1.2,tileV=1.2,flare=root_flare(5,1.1,0.25,0.3),cap_end=False,noise_amp=0.06)
    endcap(k,(0.03,0.01,0.62),(0,0,1),0.43)
    for i in range(3):
        a=i*2.1+rng.uniform(-0.3,0.3); mushroom(k,(math.cos(a)*0.62,math.sin(a)*0.62,-0.02),rng.uniform(0.08,0.14),rng.uniform(0.05,0.08),MUSH_BROWN,seed=i,shape="flat")
    bracket_fungus(k,(0.4,-0.1,0.42),(1,-0.2,0),0.14,seed)
    k.wind_fn=lambda p: 0.0
def make_log(k,seed,L=3.4,r=0.34):
    rng=random.Random(seed)
    pts=[Vector((-L/2+L*i/8,0.08*math.sin(i*0.7),r*0.85+0.03*math.sin(i*1.3))) for i in range(9)]
    k.tube(pts,[r*(1-0.1*i/8) for i in range(9)],12,BARK_MOSSY,tileU=1.2,tileV=1.2,cap_end=False,noise_amp=0.07)
    endcap(k,pts[0],(pts[0]-pts[1]).normalized(),r*0.98); endcap(k,pts[-1],(pts[-1]-pts[-2]).normalized(),r*0.88)
    stub=[pts[3],pts[3]+Vector((0.2,0.35,0.3)),pts[3]+Vector((0.3,0.55,0.45))]
    k.tube(stub,[0.1,0.07,0.06],7,BARK_MOSSY,cap_end=False)
    endcap(k,stub[-1],(stub[-1]-stub[-2]).normalized(),0.06)
    bracket_fungus(k,pts[5]+Vector((0,-r*0.9,0.05)),(0,-1,0),0.12,seed+1)
    for i in range(4): mushroom(k,(rng.uniform(-L/2,L/2),rng.uniform(0.35,0.6)*(1 if i%2 else -1),-0.02),rng.uniform(0.08,0.14),rng.uniform(0.05,0.08),MUSH_BROWN,seed=i+10,shape="flat")
    make_fern(k,seed+5,n=6,Hs=(0.6,0.9),c=(L*0.3,0.62,0))
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z-0.3))
# =====================  ROCKS  =====================
def box_uv(k,faces,tile,offset=(0.0,0.0)):
    for f in faces:
        n=f.normal; ax=max(range(3),key=lambda i: abs(n[i]))
        for l in f.loops:
            p=l.vert.co
            uv=(p.y,p.z) if ax==0 else ((p.x,p.z) if ax==1 else (p.x,p.y))
            l[k.uv].uv=(uv[0]/tile+offset[0],uv[1]/tile+offset[1])
def boulder(k,c,size,seed,mi=None,cuts=7,sub=3,flat_bottom=0.3,tile=1.5,rot=0.0,lean=0.0,extra_cuts=(),cut_range=(0.6,0.84)):
    mi=ROCK_MOSSY if mi is None else mi
    rnd=random.Random(seed)
    res=bmesh.ops.create_icosphere(k.bm,subdivisions=sub,radius=1.0); vs=res["verts"]
    sv=Vector((seed*1.7,seed*0.3,seed*2.9))
    for v in vs:
        d=v.co.normalized(); v.co=d*(1+0.2*noise.noise(d*1.2+sv)+0.06*noise.noise(d*3.3+sv*1.3))
    for i in range(cuts):
        n=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-0.2,1))).normalized(); off=rnd.uniform(*cut_range)
        for v in vs:
            dd=v.co.dot(n)
            if dd>off: v.co-=n*(dd-off)*rnd.uniform(0.9,1.0)
    for (en,eo) in extra_cuts:
        en=Vector(en).normalized()
        for v in vs:
            dd=v.co.dot(en)
            if dd>eo: v.co-=en*(dd-eo)
    for v in vs:
        if v.co.z<-flat_bottom: v.co.z=-flat_bottom+(v.co.z+flat_bottom)*0.05
    M=Matrix.Translation(Vector(c))@Matrix.Rotation(rot,4,"Z")@Matrix.Rotation(lean,4,"X")
    for v in vs:
        p=Vector((v.co.x*size[0]/2,v.co.y*size[1]/2,(v.co.z+flat_bottom)/(1+flat_bottom)*size[2]))
        v.co=M@p
    faces=list({f for v in vs for f in v.link_faces})
    for f in faces: f.material_index=mi
    k.bm.normal_update(); box_uv(k,faces,tile,(rnd.random(),rnd.random()))
    return vs
def make_rock_cluster(k,seed,n=5,R=1.2,big=1.4):
    rng=random.Random(seed)
    for i in range(n):
        a=i*GOLD+rng.uniform(-0.3,0.3); d=rng.uniform(0.2,1.0)*R if i else 0.0; s_=big*(1.0 if i==0 else rng.uniform(0.35,0.7))
        boulder(k,(math.cos(a)*d,math.sin(a)*d,-0.08*s_),(s_*rng.uniform(1.0,1.4),s_*rng.uniform(0.8,1.1),s_*rng.uniform(0.6,0.9)),seed*10+i,rot=rng.uniform(0,6.28),cuts=6)
def make_pebbles(k,seed,n=22,R=1.3):
    rng=random.Random(seed)
    for i in range(n):
        a=rng.uniform(0,6.28); d=R*math.sqrt(rng.random()); s_=rng.uniform(0.1,0.3)
        boulder(k,(math.cos(a)*d,math.sin(a)*d,-0.03),(s_*rng.uniform(1,1.5),s_,s_*rng.uniform(0.4,0.7)),seed*100+i,mi=ROCK,cuts=3,sub=2,rot=rng.uniform(0,6.28))
def make_stepstones(k,seed,n=6,L=5.0):
    rng=random.Random(seed)
    for i in range(n):
        t=i/(n-1); x=-L/2+L*t; y=0.35*math.sin(t*3.5)
        s_=rng.uniform(0.6,0.8); boulder(k,(x,y,-0.14),(s_*1.2,s_,0.3),seed*10+i,mi=ROCK,cuts=4,sub=2,flat_bottom=0.6,rot=rng.uniform(0,6.28))
def make_outcrop(k,seed):
    rng=random.Random(seed)
    layers=[(0.0,5.0,3.6,1.5,0.0),(1.2,3.6,2.9,1.3,0.12),(2.2,2.6,2.0,1.2,-0.1),(3.0,1.4,1.3,0.9,0.2)]
    for i,(z,sx,sy,sz,ln) in enumerate(layers):
        off=Vector((rng.uniform(-0.6,0.6),rng.uniform(-0.4,0.4),z-0.2))
        boulder(k,off,(sx,sy,sz*1.2),seed*10+i,cuts=11,flat_bottom=0.45,rot=rng.uniform(-0.6,0.6),lean=ln)
    for i in range(4):
        a=rng.uniform(0,6.28); boulder(k,(math.cos(a)*2.6,math.sin(a)*1.9,-0.05),(0.7,0.6,0.5),seed*20+i,cuts=5,sub=2,rot=rng.uniform(0,6.28))
def make_standing_stone(k,seed,H=3.0):
    rng=random.Random(seed)
    sl=rng.choice((-1,1))
    boulder(k,(0,0,-0.2),(1.25,0.55,H+0.2),seed,cuts=10,flat_bottom=0.9,rot=rng.uniform(0,6.28),lean=rng.uniform(-0.05,0.05),tile=1.2,
            extra_cuts=[((0,1,0),0.62),((0,-1,0),0.62),((sl*0.55,0,1),0.72),((1,0,0),0.8),((-1,0,0),0.8)],cut_range=(0.55,0.8))
    for i in range(3):
        a=rng.uniform(0,6.28); boulder(k,(math.cos(a)*0.7,math.sin(a)*0.55,-0.05),(0.35,0.3,0.25),seed*7+i,mi=ROCK,cuts=3,sub=2)
# =====================  POND  =====================
def lily_pad(k,c,r,rot,seed=0):
    rng=random.Random(seed); n=14; notch=0.35
    ctr=k.bm.verts.new(Vector(c)+Vector((0,0,0.012)))
    ring=[]
    for i in range(n+1):
        a=rot+notch/2+(2*math.pi-notch)*i/n
        rr=r*(1+0.04*math.sin(a*5+seed))
        ring.append(k.bm.verts.new(Vector(c)+Vector((math.cos(a)*rr,math.sin(a)*rr,0.0))))
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[i+1])); f.material_index=LEAF; f.smooth=True
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
def lily_flower(k,c,r,seed=0):
    rng=random.Random(seed); cx,cy,cz=c
    for layer,(n,rr,tilt) in enumerate(((8,r,0.55),(6,r*0.7,0.95))):
        for i in range(n):
            a=i*2*math.pi/n+layer*0.3
            base=Vector((cx,cy,cz+0.02+layer*0.02)); d=Vector((math.cos(a),math.sin(a),0))
            tip=base+d*rr*math.cos(tilt)+Vector((0,0,rr*math.sin(tilt)))
            side=Vector((-math.sin(a),math.cos(a),0))*rr*0.3
            vs=[k.bm.verts.new(p) for p in (base,base+d*rr*0.45+side+Vector((0,0,0.02)),tip,base+d*rr*0.45-side+Vector((0,0,0.02)))]
            f=k.bm.faces.new(vs); f.material_index=PINK; f.smooth=True
    _ico(k,(cx,cy,cz+0.06),r*0.22,YELLOW,sub=1)
def make_pond(k,seed,R=2.8):
    rng=random.Random(seed); n=32
    ctr=k.bm.verts.new((0,0,0.05)); ring=[]
    radii=[R*(1+0.12*math.sin(i*2*math.pi/n*3+seed)+0.07*math.sin(i*2*math.pi/n*5+1.7)) for i in range(n)]
    for i in range(n):
        a=2*math.pi*i/n; ring.append(k.bm.verts.new((math.cos(a)*radii[i],math.sin(a)*radii[i],0.05)))
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[(i+1)%n])); f.material_index=WATER; f.smooth=True
        for l in f.loops: l[k.uv].uv=(l.vert.co.x/2,l.vert.co.y/2)
    # muddy bank ring slightly below water edge
    for i in range(n):
        a=2*math.pi*i/n; a2=2*math.pi*(i+1)/n
        p1=Vector((math.cos(a)*radii[i],math.sin(a)*radii[i],0.05)); p2=Vector((math.cos(a2)*radii[(i+1)%n],math.sin(a2)*radii[(i+1)%n],0.05))
        q1=p1*1.12; q1.z=0.0; q2=p2*1.12; q2.z=0.0
        f=k.bm.faces.new([k.bm.verts.new(p) for p in (p1,q1,q2,p2)]); f.material_index=SOIL; f.smooth=True
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.normal.z<0: f.normal_flip()
    # stones around ~60% of the rim
    for i in range(0,n):
        if i%3==0 or (i>n*0.55 and i<n*0.8): continue
        a=2*math.pi*i/n+rng.uniform(-0.05,0.05); rr=radii[i]*rng.uniform(1.02,1.12); s_=rng.uniform(0.35,0.7)
        boulder(k,(math.cos(a)*rr,math.sin(a)*rr,-0.06),(s_*1.3,s_,s_*0.55),seed*50+i,cuts=4,sub=2,rot=a)
    for i in range(7):
        a=rng.uniform(0,6.28); d=rng.uniform(0.3,0.8)*R; lily_pad(k,(math.cos(a)*d,math.sin(a)*d,0.055),rng.uniform(0.18,0.3),rng.uniform(0,6.28),seed+i)
        if i%3==0: lily_flower(k,(math.cos(a)*d,math.sin(a)*d,0.06),0.12,seed+i)
    make_tufts(k,seed+3,"reeds",n=8,R=0.7,Hs=(1.3,1.8),W=0.7,c0=(math.cos(3.6)*R*0.95,math.sin(3.6)*R*0.95,0))
    make_tufts(k,seed+4,"reeds",n=5,R=0.5,Hs=(1.1,1.5),W=0.7,c0=(math.cos(0.9)*R*1.0,math.sin(0.9)*R*1.0,0))
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z/1.8))

def build_glade(coll,C=(700.0,0.0),seed=7):
    cx,cy=C; rng=random.Random(seed); O=(0,0,0)
    placed=[]
    def P(name,x,y,rot=None,scale=1.0,rec=True,r=1.0):
        rot=rng.uniform(0,360) if rot is None else rot
        o=place_v(coll,name,cx+x,cy+y,0,rot,O,{})
        o.scale=(scale,scale,scale)
        if rec: placed.append((x,y,r*scale))
        return o
    # pond + willow
    P("SM_VK_Pond",-6,2,rot=10,r=3.2)
    P("SM_VK_Tree_Willow",-10.5,6.5,rot=40,r=3.5)
    P("SM_VK_Rock_StepStones",-1.2,-3.2,rot=-25,r=1.0)
    # stone circle on the right
    sc=(12.0,6.0)
    for i in range(7):
        a=i*2*math.pi/7+0.3; R=4.6
        o=P("SM_VK_Rock_Standing" if i%2==0 else "SM_VK_Rock_Standing_B",sc[0]+math.cos(a)*R,sc[1]+math.sin(a)*R,rot=math.degrees(a)+90,scale=rng.uniform(0.85,1.1),r=0.8)
    P("SM_VK_Rock_Boulder_Flat",sc[0],sc[1],rot=20,scale=0.8,r=1.3)
    # outcrop + dead tree
    P("SM_VK_Rock_Outcrop",4.5,17,rot=200,r=3.2)
    P("SM_VK_Tree_Dead",9.0,15.5,rot=60,r=1.0)
    # forest layers behind
    back=[("SM_VK_Tree_Pine_B",-18,20),("SM_VK_Tree_Pine_A",-12,22),("SM_VK_Tree_Pine_A",-4,24),("SM_VK_Tree_Pine_B",14,24),("SM_VK_Tree_Pine_A",21,21),
          ("SM_VK_Tree_Pine_Young",-7,17),("SM_VK_Tree_Pine_Young",18,16),("SM_VK_Tree_Pine_B",26,14),("SM_VK_Tree_Pine_A",-24,12)]
    for n,x,y in back: P(n,x,y,r=2.5)
    mid=[("SM_VK_Tree_Oak_A",-17,10),("SM_VK_Tree_Oak_B",1,12),("SM_VK_Tree_Birch",-2,6.5),("SM_VK_Tree_Birch_Single",20,4),
         ("SM_VK_Tree_Oak_Autumn",24,-2),("SM_VK_Tree_Blossom",-19,-6),("SM_VK_Tree_Birch_Single",-15,-1),("SM_VK_Tree_Oak_A",-24,1),("SM_VK_Tree_Apple",15,-8),
         ("SM_VK_Tree_Sapling",24,-9)]
    for n,x,y in mid: P(n,x,y,r=2.2)
    # log, stump, rocks
    P("SM_VK_Log_Fallen",1.5,2.0,rot=-30,r=1.8); P("SM_VK_Stump",-3.5,9.5,r=0.7)
    P("SM_VK_Rock_Boulder_A",-13,-5,r=1.0); P("SM_VK_Rock_Boulder_B",27,6,r=1.5); P("SM_VK_Rock_Cluster",10,-6,r=1.4)
    P("SM_VK_Rock_Small_A",-3,-6); P("SM_VK_Rock_Small_B",4,-5.5); P("SM_VK_Rock_Pebbles",-9,-3,r=1.2)
    # bushes
    for n,x,y in [("SM_VK_Bush_Large",-20,6),("SM_VK_Bush_Round",-8,11),("SM_VK_Bush_Berry",5,7),("SM_VK_Bush_Hydrangea",-14,3),
                  ("SM_VK_Bush_Autumn",21,1),("SM_VK_Bush_Round",17,11),("SM_VK_Bush_Berry",-22,-4),("SM_VK_Bush_Large",8,20)]:
        P(n,x,y,r=1.3)
    # mushrooms near log / stump / trees
    for n,x,y in [("SM_VK_Mushrooms_Red",2.8,3.2),("SM_VK_Mushrooms_Brown",-3.0,10.6),("SM_VK_Mushrooms_Glow",-16.2,11.2),("SM_VK_Mushrooms_Red",-1.2,7.8),("SM_VK_Mushrooms_Glow",3.0,15.5)]:
        P(n,x,y,r=0.3)
    # ground scatter: ferns under trees, grass & flowers in the open
    def free(x,y,r):
        return all((x-px)**2+(y-py)**2>(r+pr)**2 for px,py,pr in placed)
    for kind,cnt,rad,zone in (("SM_VK_Plant_Fern",26,0.6,"shade"),("SM_VK_Plant_TallGrass",30,0.6,"open"),("SM_VK_Plant_Wildflowers",22,0.7,"open"),("SM_VK_Plant_Reeds",0,0.6,"open")):
        n=0; tries=0
        while n<cnt and tries<3000:
            tries+=1
            x=rng.uniform(-26,28); y=rng.uniform(-10,24)
            if zone=="shade" and y<5: continue
            if zone=="open" and y>14: continue
            if not free(x,y,rad): continue
            P(kind,x,y,scale=rng.uniform(0.8,1.25),r=rad); n+=1
    # reeds around the pond edge
    for i in range(6):
        a=rng.uniform(0,6.28); P("SM_VK_Plant_Reeds",-6+math.cos(a)*3.4,2+math.sin(a)*3.0,scale=rng.uniform(0.8,1.1),rec=False)

def dress_town_nature(coll,C=(200.0,0.0),seed=2029):
    import mathutils
    cx,cy=C; rng=random.Random(seed); O=(0,0,0)
    for o in [o for o in coll.objects if o.name.startswith(("VK_TTree","NT_"))]: bpy.data.objects.remove(o)
    solid=[o.matrix_world.translation.copy() for o in coll.objects if not o.name.startswith(("VK_Town","NT_","VK_TTree"))]
    kd=mathutils.kdtree.KDTree(len(solid))
    for i,p in enumerate(solid): kd.insert((p.x,p.y,0),i)
    kd.balance()
    roads=[((cx-66,cy-22),(cx+66,cy-22),3.6),((cx,cy-11),(cx,cy-64),3.0)]
    def seg_d(p,a,b):
        ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
        t=max(0.0,min(1.0,((p[0]-ax)*dx+(p[1]-ay)*dy)/L2)); return math.hypot(p[0]-(ax+t*dx),p[1]-(ay+t*dy))
    def near_road(x,y,m):
        if cx-16<x<cx+16 and cy-13<y<cy+13: return True
        return any(seg_d((x,y),a,b)<w+m for a,b,w in roads)
    placed=[]
    def clear(x,y,build_m,self_m):
        if kd.find((x,y,0))[2]<build_m: return False
        if near_road(x,y,self_m*0.5): return False
        return all((x-px)**2+(y-py)**2>(self_m+pr)**2 for px,py,pr in placed)
    cnt=[0]
    def put(name,x,y,rot=None,s=1.0,r=1.0,rec=True):
        rot=rng.uniform(0,360) if rot is None else rot
        if name=="HERO":
            for part in ("SM_Tree_Wood","SM_Tree_Foliage"):
                o=bpy.data.objects.new(f"NT_{cnt[0]}_{part}",bpy.data.objects[part].data); coll.objects.link(o)
                o.location=(x,y,0); o.rotation_euler=(0,0,math.radians(rot)); o.scale=(s,s,s)
        else:
            o=place_v(coll,name,x,y,0,rot,O,{}); o.name=f"NT_{cnt[0]}_{name[6:]}"; o.scale=(s,s,s)
        cnt[0]+=1
        if rec: placed.append((x,y,r*s))
    # --- landmarks
    pc=(cx+42,cy-53); put("SM_VK_Pond",pc[0],pc[1],rot=15,r=3.3)
    put("SM_VK_Tree_Willow",pc[0]+4.5,pc[1]+4.5,rot=40,r=3.2)
    put("SM_VK_Rock_StepStones",pc[0]-4.5,pc[1]+3.5,rot=60,r=1.0)
    for i in range(3): put("SM_VK_Plant_Reeds",pc[0]+rng.uniform(-3,3),pc[1]-3.4+rng.uniform(-0.3,0.3),rec=False)
    sc=(cx+88,cy+12)
    for i in range(7):
        a=i*2*math.pi/7+0.4
        put("SM_VK_Rock_Standing" if i%2==0 else "SM_VK_Rock_Standing_B",sc[0]+math.cos(a)*4.6,sc[1]+math.sin(a)*4.6,rot=math.degrees(a)+90,s=rng.uniform(0.85,1.1),r=1.0)
    put("SM_VK_Rock_Boulder_Flat",sc[0],sc[1],rot=30,s=0.8,r=1.4)
    put("SM_VK_Rock_Outcrop",cx-84,cy+34,rot=160,r=3.5); put("SM_VK_Tree_Dead",cx-79,cy+31,r=1.0)
    # --- orchard west of the barn
    for i in range(3):
        for j in range(4):
            x=cx-40+i*5.2+rng.uniform(-0.3,0.3); y=cy-50-j*5.2+rng.uniform(-0.3,0.3)
            if clear(x,y,5.0,2.2): put("SM_VK_Tree_Apple",x,y,s=rng.uniform(0.9,1.1),r=2.2)
    # --- blossom trees around the plaza
    n=0
    for k_ in range(80):
        a=rng.uniform(0,6.28); d=rng.uniform(18,26); x=cx+math.cos(a)*d; y=cy+math.sin(a)*d
        if clear(x,y,6.5,3.5): put("SM_VK_Tree_Blossom",x,y,r=3.0); n+=1
        if n>=4: break
    # --- tree zones
    def species(x,y):
        dy=y-cy; dx=abs(x-cx)
        if dy>24: return rng.choices(["SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Oak_A","SM_VK_Tree_Birch","HERO"],[30,25,12,12,12,9])[0]
        if dx>70: return rng.choices(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","HERO","SM_VK_Tree_Birch","SM_VK_Tree_Birch_Single","SM_VK_Tree_Pine_A","SM_VK_Tree_Oak_Autumn"],[20,18,16,14,10,14,8])[0]
        return rng.choices(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","HERO","SM_VK_Tree_Birch","SM_VK_Tree_Birch_Single","SM_VK_Tree_Oak_Autumn","SM_VK_Tree_Pine_Young","SM_VK_Tree_Dead"],[18,16,20,14,12,8,8,4])[0]
    n=0; tries=0
    while n<150 and tries<30000:
        tries+=1
        x=cx+rng.uniform(-105,105); y=cy+rng.uniform(-100,62)
        if abs(x-cx)<66 and -48<y-cy<22 and rng.random()<0.9: continue
        if not clear(x,y,8.0,3.6): continue
        sp=species(x,y); put(sp,x,y,s=rng.uniform(0.85,1.2),r=3.4 if "Pine" not in sp else 3.0); n+=1
    # --- understory: bushes, rocks, logs, stumps, plants, mushrooms
    def scatter(names,wts,count,build_m,self_m,xr=(-100,100),yr=(-95,58),scale=(0.85,1.2),inner_ok=False):
        m=0; t=0
        while m<count and t<count*80:
            t+=1
            x=cx+rng.uniform(*xr); y=cy+rng.uniform(*yr)
            if not inner_ok and abs(x-cx)<60 and -45<y-cy<18 and rng.random()<0.7: continue
            if not clear(x,y,build_m,self_m): continue
            put(rng.choices(names,wts)[0],x,y,s=rng.uniform(*scale),r=self_m); m+=1
    scatter(["SM_VK_Bush_Round","SM_VK_Bush_Large","SM_VK_Bush_Berry","SM_VK_Bush_Hydrangea","SM_VK_Bush_Autumn"],[30,20,20,15,8],70,4.0,1.4,inner_ok=True)
    scatter(["SM_VK_Rock_Boulder_A","SM_VK_Rock_Boulder_B","SM_VK_Rock_Boulder_Flat","SM_VK_Rock_Cluster","SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Pebbles"],[18,8,8,8,16,16,10],45,5.0,1.4)
    scatter(["SM_VK_Log_Fallen","SM_VK_Stump"],[1,1],14,6.0,1.8)
    scatter(["SM_VK_Plant_Fern","SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers"],[35,40,25],260,3.0,0.7,inner_ok=True)
    scatter(["SM_VK_Mushrooms_Red","SM_VK_Mushrooms_Brown","SM_VK_Mushrooms_Glow"],[40,45,15],30,4.0,0.4)
    return cnt[0]

# ================================================================ NATURE MASTERS: recipes + rebuild
# One recipe per master in VK_NaturePieces: (name, builder, nk_finish kwargs). Recovered from the build calls of
# 2026-09-23 and verified to reproduce every current master vertex-for-vertex. Change a recipe here, then
# rebuild_nature({"SM_VK_..."}) -- masters are rebuilt in place, so every placed instance updates.
_R40=math.radians(40)
NATURE_SPECS=[
 # broadleaf trees (dense card canopies, no core blobs: clump_cards(core=False, tangent=False))
 ("SM_VK_Tree_Oak_A",lambda k: make_broad_tree(k,11,[("broadleaf",0.75),("broadleaf_dark",0.25)],cards=54,size=(0.95,1.35)),{}),
 ("SM_VK_Tree_Oak_B",lambda k: make_broad_tree(k,17,[("broadleaf",0.6),("broadleaf_dark",0.4)],trunkH=3.8,spread=0.85,cards=52,size=(0.95,1.35)),{}),
 ("SM_VK_Tree_Oak_Autumn",lambda k: make_broad_tree(k,13,[("autumn_orange",0.55),("autumn_red",0.3),("broadleaf",0.15)],cards=52,size=(0.95,1.35)),{}),
 ("SM_VK_Tree_Apple",lambda k: make_fruit(k,61,[("apple",0.55),("broadleaf",0.45)],cards=56,size=(0.75,1.05)),{}),
 ("SM_VK_Tree_Blossom",lambda k: make_fruit(k,67,[("blossom",1.0)],spread=1.1,cards=76,size=(0.6,0.85)),{}),
 ("SM_VK_Tree_Birch",lambda k: make_birch(k,41),{}),
 ("SM_VK_Tree_Birch_Single",lambda k: make_birch(k,43,H=7.5,stems=1),{}),
 ("SM_VK_Tree_Willow",lambda k: make_willow(k,51),{}),
 ("SM_VK_Tree_Pine_A",lambda k: make_pine(k,21,H=10.0),{}),
 ("SM_VK_Tree_Pine_B",lambda k: make_pine(k,27,H=13.0,Rmax_f=0.26),{}),
 ("SM_VK_Tree_Pine_Young",lambda k: make_pine(k,29,H=5.0,young=True),{}),
 ("SM_VK_Tree_Dead",lambda k: make_dead(k,71),{}),
 ("SM_VK_Tree_Sapling",lambda k: make_sapling(k,81),{}),
 # bushes and plants
 ("SM_VK_Bush_Round",lambda k: make_bush(k,101,[("broadleaf",1.0)]),{}),
 ("SM_VK_Bush_Large",lambda k: make_bush(k,103,[("broadleaf",1.0)],R=1.5,H=1.8,nclump=6,cards=24,size=(0.8,1.15)),{}),
 ("SM_VK_Bush_Berry",lambda k: make_bush(k,105,[("berry",0.75),("broadleaf",0.25)]),{}),
 ("SM_VK_Bush_Hydrangea",lambda k: make_bush(k,107,[("hydrangea",0.75),("broadleaf",0.25)],R=1.0,H=1.2),{}),
 ("SM_VK_Bush_Autumn",lambda k: make_bush(k,109,[("autumn_orange",0.5),("autumn_red",0.5)]),{}),
 ("SM_VK_Plant_Fern",lambda k: make_fern(k,111),{"bark_ao":None}),
 ("SM_VK_Plant_Reeds",lambda k: make_tufts(k,113,"reeds",n=10,R=0.7,Hs=(1.3,1.9),W=0.7),{"bark_ao":None}),
 ("SM_VK_Plant_TallGrass",lambda k: make_tufts(k,115,"tallgrass",n=10,R=0.7,Hs=(0.7,1.1),W=0.9),{"bark_ao":None}),
 ("SM_VK_Plant_Wildflowers",lambda k: make_tufts(k,117,"wildflowers",n=12,R=0.9,Hs=(0.5,0.75),W=0.9),{"bark_ao":None}),
 ("SM_VK_Mushrooms_Red",lambda k: make_mushrooms(k,121,"red"),{"bark_ao":None}),
 ("SM_VK_Mushrooms_Brown",lambda k: make_mushrooms(k,123,"brown"),{"bark_ao":None}),
 ("SM_VK_Mushrooms_Glow",lambda k: make_mushrooms(k,125,"glow"),{"bark_ao":None}),
 # wood and rocks
 ("SM_VK_Stump",lambda k: make_stump(k,131),{"bark_ao":(0.7,0.4)}),
 ("SM_VK_Log_Fallen",lambda k: make_log(k,133),{"bark_ao":(0.7,0.4)}),
 ("SM_VK_Rock_Boulder_A",lambda k: boulder(k,(0,0,-0.1),(1.8,1.4,1.3),141),{"sharp":_R40,"bark_ao":(0.72,0.5)}),
 ("SM_VK_Rock_Boulder_B",lambda k: boulder(k,(0,0,-0.15),(2.8,2.2,1.9),143,cuts=9),{"sharp":_R40,"bark_ao":(0.72,0.6)}),
 ("SM_VK_Rock_Boulder_Flat",lambda k: boulder(k,(0,0,-0.1),(2.4,1.7,0.8),145,cuts=6,flat_bottom=0.5),{"sharp":_R40,"bark_ao":(0.72,0.4)}),
 ("SM_VK_Rock_Small_A",lambda k: boulder(k,(0,0,-0.05),(0.6,0.5,0.4),147,mi=ROCK,cuts=5,sub=2),{"sharp":_R40,"bark_ao":(0.75,0.3)}),
 ("SM_VK_Rock_Small_B",lambda k: boulder(k,(0,0,-0.05),(0.5,0.45,0.55),149,mi=ROCK,cuts=5,sub=2),{"sharp":_R40,"bark_ao":(0.75,0.3)}),
 ("SM_VK_Rock_Cluster",lambda k: make_rock_cluster(k,151),{"sharp":_R40,"bark_ao":(0.72,0.5)}),
 ("SM_VK_Rock_Pebbles",lambda k: make_pebbles(k,153),{"sharp":_R40,"bark_ao":(0.8,0.2)}),
 ("SM_VK_Rock_StepStones",lambda k: make_stepstones(k,155),{"sharp":_R40,"bark_ao":(0.8,0.2)}),
 ("SM_VK_Rock_Outcrop",lambda k: make_outcrop(k,157),{"sharp":_R40,"bark_ao":(0.7,1.2)}),
 ("SM_VK_Rock_Standing",lambda k: make_standing_stone(k,159),{"sharp":_R40,"bark_ao":(0.72,0.6)}),
 ("SM_VK_Rock_Standing_B",lambda k: make_standing_stone(k,163,H=2.4),{"sharp":math.radians(35),"bark_ao":(0.72,0.6)}),
 ("SM_VK_Pond",lambda k: make_pond(k,161),{"bark_ao":(0.75,0.3)}),
]
def rebuild_nature(names=None,coll_name="VK_NaturePieces"):
    """rebuild nature masters in place from NATURE_SPECS (all, or the given names); instances update automatically"""
    coll=bpy.data.collections.get(coll_name) or vcol(coll_name)
    done=[]
    for n,fn,kw in NATURE_SPECS:
        if names and n not in names: continue
        k=NK(); fn(k); nk_finish(k,n,coll,**kw); done.append(n)
    return done
def check_nature_specs(names=None,tol=1e-4):
    """compare what each recipe builds with the current master, vertex by vertex (nothing is modified)"""
    out=[]
    for n,fn,kw in NATURE_SPECS:
        if names and n not in names: continue
        o=bpy.data.objects.get(n)
        k=NK(); fn(k); vs=[v.co.copy() for v in k.bm.verts]; k.bm.free()
        if o is None: out.append((n,"missing master")); continue
        mv=o.data.vertices
        if len(mv)!=len(vs): out.append((n,f"vertex count {len(vs)} vs master {len(mv)}")); continue
        dev=max(((a-b.co).length for a,b in zip(vs,mv)),default=0.0)
        out.append((n,"ok" if dev<=tol else f"max deviation {dev:.4f} m"))
    return out
