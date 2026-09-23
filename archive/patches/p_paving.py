import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
p='vk_terrain.py'; s=open(p,encoding='utf8').read()
a='''def tk_ground_ctl(G,name="T_VK_GroundCtl"):
    """RGBA8 one texel per cell: R dirt(+wear) G cobble B sand(water forced) A rock"""
    Wd,Hd=G.W,G.H
    arr=np.zeros((Hd,Wd,4),np.float32)
    gnd=G.ground
    arr[...,0]=np.maximum(gnd==1,G.wear/255.0); arr[...,1]=(gnd==2); arr[...,2]=np.maximum(gnd==3,G.water); arr[...,3]=(gnd==4)'''
b='''def tk_ground_ctl(G,name="T_VK_GroundCtl",paved=False):
    """RGBA8 one texel per cell: R dirt(+wear) G cobble B sand(water forced) A rock.
    paved=True: cobble cells are covered by the separate paving mesh (tk_build_paving), so the terrain under them is
    painted as dirt (it shows through the patches of missing stones)"""
    Wd,Hd=G.W,G.H
    arr=np.zeros((Hd,Wd,4),np.float32)
    gnd=G.ground
    cob=(gnd==2)
    arr[...,0]=np.maximum(np.maximum(gnd==1,cob*paved),G.wear/255.0); arr[...,1]=cob*(not paved); arr[...,2]=np.maximum(gnd==3,G.water); arr[...,3]=(gnd==4)'''
assert s.count(a)==1; s=s.replace(a,b)
anchor="def tk_add_random_ramps(G,rng,tries=40):"
new='''def paving_materials():
    """M_VKT_Paving: the terrain's cobble texture (same object-space mapping as the terrain) + height bump.
    M_VKT_Curb: dressed stone (StoneBlock) box-projected in object space."""
    out=[]
    for name,img,sc,rough,bstr in (("M_VKT_Paving","T_VK_Cobble",0.25,0.82,0.55),("M_VKT_Curb","T_VK_StoneBlock",0.8,0.78,0.45)):
        m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
        o=B.n("ShaderNodeOutputMaterial"); bs=B.n("ShaderNodeBsdfPrincipled")
        tc=B.n("ShaderNodeTexCoord"); p=B.scale(tc.outputs["Object"],sc)
        box=(name=="M_VKT_Curb")
        c=B.img(img+"_BC",p,box=box); h=B.img(img+"_H",p,data=True,box=box)
        vc=B.n("ShaderNodeVertexColor",layer_name="Col")
        col=B.mix(1.0,c.outputs[0],vc.outputs[0],blend="MULTIPLY")
        B.link(col,bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value=rough; bs.inputs["Specular IOR Level"].default_value=0.25
        bp=B.n("ShaderNodeBump"); B.link(h.outputs[0],bp.inputs["Height"]); bp.inputs["Strength"].default_value=bstr
        bp.inputs["Distance"].default_value=0.04; B.link(bp.outputs[0],bs.inputs["Normal"]); B.link(bs.outputs[0],o.inputs[0])
        out.append(m)
    return out

def tk_build_paving(G,coll,origin=MAP_ORIGIN,name="VK_Paving",lift=0.06,step=0.25,seed=3,hole_t=0.5,cliff_inset=0.35):
    """Cobbled cells (ground==2) as a separate mesh: stones `lift` m above the terrain, a curb of dressed stones
    where the cobbles meet grass (not towards dirt roads or ramps), and patches of missing stones that show the
    dirt painted under the paving. Hole edges are irregular and get a small side face (the paving's thickness)."""
    from mathutils import noise as mnoise
    rng=random.Random(seed)
    cob=(G.ground==2)&(~G.water)
    n=int(round(3.0/step))
    bm=bmesh.new(); uvl=bm.loops.layers.uv.new("UVMap"); cl=bm.loops.layers.color.new("Col")
    V={}; holes=set()
    def vert(ia,ib,lv):
        k=(ia,ib,lv)
        if k not in V: V[k]=bm.verts.new((ia*step,ib*step,lv*TIER+lift))
        return V[k]
    def nb(i,j):
        return (G.level[j,i],bool(cob[j,i]),int(G.ground[j,i]),int(G.ramp[j,i])) if (0<=i<G.W and 0<=j<G.H) else None
    curb_sides=[]
    for (j,i) in zip(*np.nonzero(cob)):
        lv=int(G.level[j,i]); ins=[0.0,0.0,0.0,0.0]; curb=[False]*4          # W,E,S,N
        for sd,(di,dj) in enumerate(((-1,0),(1,0),(0,-1),(0,1))):
            q=nb(i+di,j+dj)
            if q is None: continue
            l2,c2,g2,r2=q
            if l2<lv: ins[sd]=cliff_inset; curb[sd]=not G.ramp[j,i]
            elif not c2 and l2==lv and g2!=1 and not r2 and not G.ramp[j,i]: curb[sd]=True
        curb_sides.append((i,j,lv,ins,curb))
        for a in range(n):
            for b in range(n):
                x0,y0=3*i+a*step,3*j+b*step; cx,cy=x0+step/2,y0+step/2; lx,ly=cx-3*i,cy-3*j
                if lx<ins[0] or lx>3-ins[1] or ly<ins[2] or ly>3-ins[3]: continue
                near_curb=((curb[0] and lx<0.6) or (curb[1] and lx>2.4) or (curb[2] and ly<0.6) or (curb[3] and ly>2.4))
                hv=mnoise.noise(Vector((cx*0.42,cy*0.42,7.3)))+0.45*mnoise.noise(Vector((cx*1.4,cy*1.4,2.1)))
                ia,ib=int(round(x0/step)),int(round(y0/step))
                if hv>hole_t and not near_curb:
                    holes.add((ia,ib,lv)); continue
                f=bm.faces.new((vert(ia,ib,lv),vert(ia+1,ib,lv),vert(ia+1,ib+1,lv),vert(ia,ib+1,lv))); f.material_index=0
    # irregular hole outlines: jitter the vertices on hole edges (only in xy)
    hv_=set()
    for (ia,ib,lv) in holes:
        for (da,db) in ((0,0),(1,0),(1,1),(0,1)):
            k=(ia+da,ib+db,lv)
            if k in V: hv_.add(k)
    for k in hv_:
        v=V[k]; v.co.x+=rng.uniform(-0.07,0.07); v.co.y+=rng.uniform(-0.07,0.07)
    # side faces on every open edge (holes, paving ends)
    for e in [e for e in bm.edges if len(e.link_faces)==1]:
        f=e.link_faces[0]; v1,v2=e.verts
        lp=[l.vert for l in f.loops]; k_=lp.index(v1)
        if lp[(k_+1)%len(lp)]!=v2: v1,v2=v2,v1
        z=v1.co.z-lift-0.03
        a_=bm.verts.new((v1.co.x,v1.co.y,z)); b_=bm.verts.new((v2.co.x,v2.co.y,z))
        sf=bm.faces.new((v2,v1,a_,b_)); sf.material_index=0
    # curb stones
    for (i,j,lv,ins,curb) in curb_sides:
        zc=lv*TIER
        for sd in range(4):
            if not curb[sd]: continue
            off=ins[sd]+0.11
            if sd==0: p0,p1=(3*i+off,3*j),(3*i+off,3*j+3)
            elif sd==1: p0,p1=(3*i+3-off,3*j),(3*i+3-off,3*j+3)
            elif sd==2: p0,p1=(3*i,3*j+off),(3*i+3,3*j+off)
            else: p0,p1=(3*i,3*j+3-off),(3*i+3,3*j+3-off)
            L=3.0; t=0.0; tx,ty=(p1[0]-p0[0])/L,(p1[1]-p0[1])/L
            while t<L-0.05:
                l_=min(rng.uniform(0.42,0.72),L-t)
                cxs=p0[0]+tx*(t+l_/2); cys=p0[1]+ty*(t+l_/2)
                h=0.17+rng.uniform(-0.015,0.015)
                vs=bmesh.ops.create_cube(bm,size=1.0)["verts"]
                ang=math.atan2(ty,tx)+math.radians(rng.uniform(-2.5,2.5))
                M=(Matrix.Translation((cxs,cys,zc-0.05+h/2))@Matrix.Rotation(ang,4,"Z")@Matrix.Diagonal((l_-0.03,0.2,h,1.0)))
                bmesh.ops.transform(bm,matrix=M,verts=vs)
                for f in {f for v in vs for f in v.link_faces}: f.material_index=1
                t+=l_
    # colours (darker hole sides) and box uvs
    bm.normal_update()
    for f in bm.faces:
        side=abs(f.normal.z)<0.5
        for l in f.loops:
            g=0.72 if (side and f.material_index==0) else 1.0
            l[cl]=(g,g,g,1.0)
            n_=f.normal; co=l.vert.co
            if abs(n_.z)>0.7: l[uvl].uv=(co.x,co.y)
            elif abs(n_.x)>abs(n_.y): l[uvl].uv=(co.y,co.z)
            else: l[uvl].uv=(co.x,co.z)
    me=bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    me.clear_geometry(); bm.to_mesh(me); bm.free()
    me.materials.clear()
    for m in paving_materials(): me.materials.append(m)
    ob=bpy.data.objects.get(name)
    if ob is None: ob=bpy.data.objects.new(name,me)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob); ob.location=origin
    return ob

'''
assert s.count(anchor)==1; s=s.replace(anchor,new+anchor)
open(p,'w',encoding='utf8').write(s)

p='vk_town_map.py'; t=open(p,encoding='utf8').read()
a='    tk_ground_ctl(G,"T_VK_GroundCtl_Town")'
assert t.count(a)==1; t=t.replace(a,'    tk_ground_ctl(G,"T_VK_GroundCtl_Town",paved=True)')
a='    tk_ramp_shoulders(G,vcoll,origin=TOWN_ORIGIN); tk_ramp_dress(G,vcoll,origin=TOWN_ORIGIN)\n'
assert t.count(a)==1
t=t.replace(a,a+'    tk_build_paving(G,tcoll,origin=TOWN_ORIGIN,name="VKV_Paving"); town_lift_on_paving(T)\n')
t=t.replace("def build_valley_town(",'''def town_lift_on_paving(T,lift=0.06):
    """props standing on cobbled cells go up onto the paving"""
    G=T.G
    for o in T.coll.all_objects:
        if o.type!="MESH": continue
        x,y=o.location.x-TOWN_ORIGIN[0],o.location.y-TOWN_ORIGIN[1]; i,j=int(x//3),int(y//3)
        if not (0<=i<G.W and 0<=j<G.H) or G.ground[j,i]!=2: continue
        if abs(o.location.z-G.level[j,i]*TIER)<0.03: o.location.z+=lift

def build_valley_town(''',1)
open(p,'w',encoding='utf8').write(t)

p='vk_terrain_demo.py'; t=open(p,encoding='utf8').read()
a="    tk_ground_ctl(G); terrain_material(W=G.W,H=G.H)"
assert t.count(a)==1; t=t.replace(a,"    tk_ground_ctl(G,paved=True); terrain_material(W=G.W,H=G.H)")
a="    tk_ramp_shoulders(G,vcoll); tk_ramp_dress(G,vcoll)\n"
assert t.count(a)==1; t=t.replace(a,a+'    tk_build_paving(G,tcoll,name="VKT_Paving")\n')
open(p,'w',encoding='utf8').write(t)
import ast
for f in ('vk_terrain.py','vk_town_map.py','vk_terrain_demo.py'): ast.parse(open(f,encoding='utf8').read())
print("ok")
