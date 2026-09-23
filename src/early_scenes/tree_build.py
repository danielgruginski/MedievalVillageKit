CARD_R=(0.45,0.7)

import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise, Quaternion
SC=bpy.data.scenes["TreeAsset"]
UP=Vector((0,0,1)); GOLD=2.39996
def tcol(name,parent=None):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); (parent or SC.collection).children.link(c)
    return c
# ---------------- skeleton
def build_skeleton(seed=12):
    rnd=random.Random(seed); branches=[]
    def grow(start,direction,length,r0,r1,depth,trop=0.12,wig=0.10,step=None):
        step=step or (0.3 if depth<2 else 0.25)
        n=max(3,int(length/step)); d=direction.normalized(); p=start.copy()
        pts=[p.copy()]; radii=[r0]
        for i in range(1,n+1):
            t=i/n
            w=Vector((noise.noise(p*0.8+Vector((depth*3.1,seed,0))),noise.noise(p*0.8+Vector((0,7.7,depth))),noise.noise(p*0.8+Vector((2.2,0,5+seed)))))
            d=(d+UP*trop*(1 if depth>0 else 0.3)+w*wig).normalized()
            if depth>=2: d=(d-UP*0.06*t).normalized()
            p=p+d*(length/n); pts.append(p.copy()); radii.append(r0+(r1-r0)*(t**0.75))
        b={"pts":pts,"radii":radii,"depth":depth,"phase":rnd.random(),"kids":[]}
        branches.append(b); return b
    def point_at(b,t):
        f=t*(len(b["pts"])-1); i=min(int(f),len(b["pts"])-2); a=f-i
        return b["pts"][i].lerp(b["pts"][i+1],a), b["radii"][i]*(1-a)+b["radii"][i+1]*a, (b["pts"][i+1]-b["pts"][i]).normalized()
    def child_dir(tan,angle,azim):
        perp=tan.cross(Vector((0.3,0.2,1)) if abs(tan.z)<0.9 else Vector((1,0,0))).normalized()
        perp=Quaternion(tan,azim)@perp
        return (Quaternion(perp,angle)@tan).normalized()
    trunk=grow(Vector((0,0,-0.45)),Vector((0.10,0.04,1)),3.5,0.52,0.33,0,wig=0.07,step=0.28)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    for k in range(3):
        az=k*2*math.pi/3+rnd.uniform(-0.3,0.3)
        d=child_dir(tt,math.radians(rnd.uniform(34,48)),az)
        limbs.append(grow(tp-tt*0.35,d,rnd.uniform(3.4,4.1),tr*0.74,0.07,1,trop=0.07,wig=0.12))
    for k,(t,ang) in enumerate([(0.62,60),(0.8,55)]):
        p,r,tan=point_at(trunk,t); d=child_dir(tan,math.radians(ang),k*2.6+1.0)
        limbs.append(grow(p,d,rnd.uniform(2.5,3.0),r*0.5,0.06,1,trop=0.11,wig=0.12))
    sub=[]
    for li,L in enumerate(limbs):
        nk=4 if li<3 else 3
        for k in range(nk):
            t=0.35+0.6*(k+rnd.uniform(0,0.6))/nk
            p,r,tan=point_at(L,min(t,0.95))
            d=child_dir(tan,math.radians(rnd.uniform(38,62)),li*1.7+k*GOLD)
            if d.z<-0.1: d.z=-0.1
            sub.append(grow(p,d,rnd.uniform(1.4,2.1),r*0.72,0.04,2,trop=0.09,wig=0.16))
    for S in sub+limbs:
        for k in range(3):
            t=0.45+0.25*k+rnd.uniform(-0.05,0.05)
            p,r,tan=point_at(S,min(t,0.97))
            d=child_dir(tan,math.radians(rnd.uniform(35,65)),k*GOLD+rnd.uniform(0,6))
            grow(p,d,rnd.uniform(0.6,0.9),max(r*0.7,0.02),0.012,3,trop=0.05,wig=0.2,step=0.4)
    return branches
# ---------------- wood mesh
def frames(pts):
    tans=[(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized() for i in range(len(pts))]
    n=tans[0].cross(Vector((0,0,1)) if abs(tans[0].z)<0.95 else Vector((1,0,0))).normalized(); out=[]
    for i,t in enumerate(tans):
        if i>0: n=(tans[i-1].rotation_difference(t)@n).normalized()
        n=(n-t*n.dot(t)).normalized(); out.append((t,n,t.cross(n)))
    return out
def build_wood(name,branches,segs_map,ring_skip=1,max_depth=3,top=8.5,coll=None):
    bm=bmesh.new(); uv=bm.loops.layers.uv.new("UVMap"); uv2=bm.loops.layers.uv.new("Wind"); cl=bm.loops.layers.color.new("Col")
    for bi,b in enumerate(branches):
        depth=b["depth"]
        if depth>max_depth: continue
        idx=list(range(0,len(b["pts"]),ring_skip))
        if idx[-1]!=len(b["pts"])-1: idx.append(len(b["pts"])-1)
        pts=[b["pts"][i] for i in idx]; radii=[b["radii"][i] for i in idx]; segs=segs_map[depth]
        fr=frames(pts); avg_r=sum(radii)/len(radii)
        urep=max(1,round(2*math.pi*avg_r/0.9)); tile_h=2*(2*math.pi*avg_r/urep)
        rings=[]; vco=0.0
        for i,(p,r) in enumerate(zip(pts,radii)):
            if i>0: vco+=(pts[i]-pts[i-1]).length/tile_h
            t,n,bn=fr[i]; ring=[]
            for k in range(segs):
                th=2*math.pi*k/segs; rr=r
                if depth==0:
                    fl=math.exp(-max(p.z,0)*2.4); lobe=max(0,math.cos(5*th+0.7))**3
                    rr=r*(1+fl*(0.25+0.9*lobe))*(1+0.05*noise.noise(Vector((math.cos(th)*1.5,math.sin(th)*1.5,p.z*1.3))))
                elif depth==1: rr*=1+0.05*noise.noise(Vector((math.cos(th)*1.5,math.sin(th)*1.5,i*0.4+bi)))
                ring.append(bm.verts.new(p+(n*math.cos(th)+bn*math.sin(th))*rr))
            rings.append((ring,vco))
        def paint(f,capped=False):
            for l in f.loops:
                h=max(0,l.vert.co.z)/top; sway=min(1,h*h*0.8+0.12*depth)
                ao=1.0 if l.vert.co.z>0.6 else 0.55+0.45*max(0,l.vert.co.z)/0.6
                l[cl]=(ao,ao,ao,sway); l[uv2].uv=(b["phase"],0.0)
        for i in range(len(rings)-1):
            ra,va=rings[i]; rb,vb=rings[i+1]
            for k in range(segs):
                k2=(k+1)%segs; f=bm.faces.new((ra[k],ra[k2],rb[k2],rb[k]))
                for l,u_,v_ in zip(f.loops,[k/segs*urep,(k+1)/segs*urep,(k+1)/segs*urep,k/segs*urep],[va,va,vb,vb]): l[uv].uv=(u_,v_)
                paint(f)
        ring0,v0=rings[0]
        c0=bm.verts.new(pts[0]-fr[0][0]*radii[0]*0.3)
        for k in range(segs):
            f=bm.faces.new((ring0[(k+1)%segs],ring0[k],c0))
            for l,(a,bb) in zip(f.loops,((0,v0),(0.25,v0),(0.125,v0+0.08))): l[uv].uv=(a,bb)
            paint(f)
        if True:
            ring,v=rings[-1]; c=bm.verts.new(pts[-1]+fr[-1][0]*radii[-1]*0.8)
            for k in range(segs):
                f=bm.faces.new((ring[k],ring[(k+1)%segs],c))
                for l,(a,bb) in zip(f.loops,((0,v),(0.25,v),(0.125,v+0.08))): l[uv].uv=(a,bb)
                paint(f)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old)
    o=bpy.data.objects.new(name,me); (coll or SC.collection).objects.link(o)
    me.materials.append(bpy.data.materials["M_Tree_Bark"])
    return o

def clump_centers(branches,rnd):
    cs=[]
    for b in branches:
        if b["depth"]==2:
            n=len(b["pts"])
            cs.append((b["pts"][-1],rnd.uniform(1.05,1.3),b["phase"]))
            cs.append((b["pts"][int(n*0.5)]+Vector((0,0,0.25)),rnd.uniform(0.9,1.1),b["phase"]))
        elif b["depth"]==1:
            cs.append((b["pts"][-1]+Vector((0,0,0.2)),rnd.uniform(1.2,1.45),b["phase"]))
    # thin out clumps that nearly coincide
    out=[]
    for c in cs:
        if all((c[0]-o[0]).length>0.55*(c[1]+o[1])*0.6 for o in out): out.append(c)
    return out
ATLAS=[((q%2)*512,(q//2)*512) for q in range(4)]
def cell_uv(q):
    ox,oy=ATLAS[q]
    u0,u1=(ox+124)/1024,(ox+388)/1024
    v_top=1-(oy+74)/1024; v_bot=1-(oy+508)/1024
    return u0,u1,v_bot,v_top
def build_foliage(name,branches,blob_sub=1,cards_per=16,card_size=(0.95,1.35),seed=3,coll=None,blob=True,top=8.5):
    rnd=random.Random(seed)
    cs=clump_centers(branches,rnd)
    cen=sum((c[0] for c in cs),Vector())/len(cs)
    ext=Vector((max(abs(c[0].x-cen.x)+c[1] for c in cs),max(abs(c[0].y-cen.y)+c[1] for c in cs),max(abs(c[0].z-cen.z)+c[1] for c in cs)))
    def canopy_n(p):
        d=p-cen; return Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z)).normalized()
    def canopy_t(p):
        d=p-cen; return min(1.0,Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z)).length)
    bm=bmesh.new(); uv=bm.loops.layers.uv.new("UVMap"); uv2=bm.loops.layers.uv.new("Wind"); cl=bm.loops.layers.color.new("Col")
    vnorm={}; vinfo={}
    def shade(v,clump_c,phase,flutter):
        cn=canopy_n(v.co); ln=(v.co-clump_c).normalized()
        vnorm[v]=(cn*0.6+ln*0.4).normalized()
        up=0.5+0.5*cn.z; outer=canopy_t(v.co)
        g=0.52+0.48*min(1,0.6*up+0.4*outer**1.5)
        h=max(0,v.co.z)/top; sway=min(1,h*h*0.8+0.3)
        vinfo[v]=((min(1,g*1.02),g,g*0.86,sway),(phase,flutter))
    if blob:
        for (c,r,ph) in cs:
            res=bmesh.ops.create_icosphere(bm,subdivisions=blob_sub,radius=r*0.62)
            for v in res["verts"]:
                d=v.co.normalized()
                disp=1+0.22*noise.noise(Vector(c)+d*1.7)+0.08*noise.noise(Vector(c)*3+d*4)
                v.co=Vector(c)+Vector((d.x,d.y,d.z*(0.8 if d.z<0 else 0.95)))*r*0.62*disp
                shade(v,Vector(c),ph,0.3)
            for f in {f for v in res["verts"] for f in v.link_faces}: f.material_index=0
    ncards=0
    for (c,r,ph) in cs:
        k=cards_per
        for i in range(k):
            # fibonacci sphere, biased upward/outward
            zf=1-2*(i+0.5)/k; az=i*GOLD+rnd.uniform(-0.3,0.3)
            d=Vector((math.sqrt(max(0,1-zf*zf))*math.cos(az),math.sqrt(max(0,1-zf*zf))*math.sin(az),zf))
            d=(d+canopy_n(Vector(c)+d*r)*0.6).normalized()
            if d.z<-0.6 and rnd.random()<0.6: continue
            s=rnd.uniform(*card_size)
            base=Vector(c)+d*r*rnd.uniform(*CARD_R)
            upv=(d+Vector((rnd.uniform(-.35,.35),rnd.uniform(-.35,.35),rnd.uniform(-0.1,0.35)))).normalized()
            side=upv.cross(Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1))).normalized()).normalized()
            w=s*0.62; L=s
            normal=side.cross(upv).normalized()
            bend=normal*(0.12*s)*(1 if normal.dot(d)>0 else -1)
            P=[base-side*w/2, base+side*w/2, base+upv*L*0.5-side*w/2+bend, base+upv*L*0.5+side*w/2+bend, base+upv*L-side*w/2-bend*0.3, base+upv*L+side*w/2-bend*0.3]
            vs=[bm.verts.new(p) for p in P]
            q=rnd.randrange(4); u0,u1,vb,vt=cell_uv(q)
            if rnd.random()<0.5: u0,u1=u1,u0   # mirror for variety
            UV=[(u0,vb),(u1,vb),(u0,(vb+vt)/2),(u1,(vb+vt)/2),(u0,vt),(u1,vt)]
            FL=[0.15,0.15,0.6,0.6,1.0,1.0]
            for v,f_ in zip(vs,FL): shade(v,Vector(c),ph,f_)
            for (a,b_,c_,d_) in ((0,1,3,2),(2,3,5,4)):
                f=bm.faces.new((vs[a],vs[b_],vs[c_],vs[d_])); f.material_index=1
                for l in f.loops:
                    j=vs.index(l.vert); l[uv].uv=UV[j]
            ncards+=1
    for f in bm.faces:
        for l in f.loops:
            col,w=vinfo[l.vert]; l[cl]=col
            if f.material_index==0: l[uv].uv=(0.5,0.5)
            l[uv2].uv=w
    bm.normal_update()
    verts=list(bm.verts)
    me=bpy.data.meshes.new(name); bm.to_mesh(me)
    nlist=[vnorm[v] for v in verts]
    bm.free()
    for p in me.polygons: p.use_smooth=True
    me.normals_split_custom_set_from_vertices([tuple(n) for n in nlist])
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old)
    o=bpy.data.objects.new(name,me); (coll or SC.collection).objects.link(o)
    me.materials.append(bpy.data.materials["M_Tree_Canopy"]); me.materials.append(bpy.data.materials["M_Tree_Leaves"])
    return o,len(cs),ncards
def make_foliage_materials():
    atlas=bpy.data.images["T_Leaves_Atlas"]
    # canopy volume
    m=bpy.data.materials.get("M_Tree_Canopy") or bpy.data.materials.new("M_Tree_Canopy"); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1
    mix.inputs[6].default_value=(0.20,0.38,0.08,1)
    nt.links.new(vc.outputs[0],mix.inputs[7]); nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.75
    b.inputs["Subsurface Weight"].default_value=0.0
    nt.links.new(b.outputs[0],o.inputs[0])
    # cards
    m=bpy.data.materials.get("M_Tree_Leaves") or bpy.data.materials.new("M_Tree_Leaves"); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=atlas
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1
    nt.links.new(tx.outputs["Color"],mix.inputs[6]); nt.links.new(vc.outputs[0],mix.inputs[7])
    gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5
    nt.links.new(tx.outputs["Alpha"],gt.inputs[0]); nt.links.new(gt.outputs[0],b.inputs["Alpha"])
    nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.6
    tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); nt.links.new(mix.outputs[2],tr.inputs["Color"])
    ms=nt.nodes.new("ShaderNodeMixShader"); ms.inputs[0].default_value=0.22
    nt.links.new(b.outputs[0],ms.inputs[1]); nt.links.new(tr.outputs[0],ms.inputs[2])
    # keep alpha cut on the mix: multiply via transparent shader
    tp=nt.nodes.new("ShaderNodeBsdfTransparent"); ms2=nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gt.outputs[0],ms2.inputs[0]); nt.links.new(tp.outputs[0],ms2.inputs[1]); nt.links.new(ms.outputs[0],ms2.inputs[2])
    nt.links.new(ms2.outputs[0],o.inputs[0])
    m.use_backface_culling=False
    try: m.surface_render_method="DITHERED"
    except: pass
