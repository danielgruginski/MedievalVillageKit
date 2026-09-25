
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, noise
SC=bpy.data.scenes["VillageKit"]
CELL=3.0; H1=3.0; H2=2.8; DEPTH=6.0
TILE={45:1.2,46:3.0,47:1.0,51:1.0,33:1.2,34:1.0,35:1.4,37:1.0,38:1.5,39:1.2,40:0.6,0:3.0,1:2.2,2:1.6,3:3.0,4:1.0,5:0.5,10:1.6,16:1.2,17:0.3,18:1.0,19:0.5,21:0.5,22:3.0,23:2.0,24:3.0,25:0.8,26:1.0,11:0.5,12:0.5,28:1.5,29:1.5}
def vcol(name,parent=None):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); (parent or SC.collection).children.link(c)
    return c
def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False,tint=None):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1
    if img:
        tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images[img]
        if tint:
            tm=nt.nodes.new("ShaderNodeMix"); tm.data_type="RGBA"; tm.blend_type="MULTIPLY"; tm.inputs[0].default_value=1
            tm.inputs[7].default_value=(*tint,1); nt.links.new(tx.outputs[0],tm.inputs[6]); nt.links.new(tm.outputs[2],mix.inputs[6])
        else: nt.links.new(tx.outputs[0],mix.inputs[6])
    else: mix.inputs[6].default_value=(*flat,1)
    nt.links.new(vc.outputs[0],mix.inputs[7]); nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=rough
    if emit:
        b.inputs["Emission Color"].default_value=(*emit,1); b.inputs["Emission Strength"].default_value=4.0
    nt.links.new(b.outputs[0],o.inputs[0])
    return m
DRESS_TINT=(0.62,0.52,0.44)    # M_VK_StoneDressed: the dressed stone darkened to a warm sandstone (chapel dressings)
def kit_mats():
    return [tex_mat("M_VK_Stone","T_VK_Stone"), tex_mat("M_VK_Plaster","T_VK_Plaster",0.9), tex_mat("M_VK_Wood","T_VK_Wood",0.8),
            tex_mat("M_VK_RoofRed","T_VK_RoofRed",0.7), tex_mat("M_VK_Window","T_VK_Window",0.25), tex_mat("M_VK_Iron",None,0.5,flat=(0.08,0.08,0.09)),
            tex_mat("M_VK_FlowerPink",None,0.7,flat=(0.85,0.30,0.55)), tex_mat("M_VK_FlowerYellow",None,0.7,flat=(0.95,0.78,0.20)),
            tex_mat("M_VK_Leaf",None,0.8,flat=(0.18,0.42,0.10)), tex_mat("M_VK_Glow",None,0.5,flat=(1.0,0.75,0.35),emit=(1.0,0.62,0.25)),
            tex_mat("M_VK_Shutter_Teal","T_VK_Wood",0.8,tint=(0.55,1.25,1.25)),
            tex_mat("M_VK_Cloth_Red",None,0.9,flat=(0.62,0.10,0.08)), tex_mat("M_VK_Cloth_Cream",None,0.9,flat=(0.90,0.84,0.66)),
            tex_mat("M_VK_Apple",None,0.45,flat=(0.72,0.08,0.05)), tex_mat("M_VK_Pumpkin",None,0.6,flat=(0.90,0.45,0.08)),
            tex_mat("M_VK_Bread",None,0.8,flat=(0.72,0.48,0.22)),
            tex_mat("M_VK_Hay",None,0.95,flat=(0.86,0.68,0.30)), tex_mat("M_VK_Paper",None,0.9,flat=(0.92,0.86,0.70)),
            tex_mat("M_VK_Water",None,0.1,flat=(0.12,0.35,0.42)), tex_mat("M_VK_Bronze",None,0.35,flat=(0.72,0.48,0.20)),
            tex_mat("M_VK_Stained",None,0.3,flat=(0.9,0.5,0.2),emit=(0.9,0.35,0.15)), tex_mat("M_VK_Steel",None,0.3,flat=(0.55,0.57,0.60)),
            tex_mat("M_VK_Thatch","T_VK_Thatch",0.95), tex_mat("M_VK_Planks","T_VK_Planks",0.85),
            tex_mat("M_VK_Ashlar","T_VK_Ashlar",0.85), tex_mat("M_VK_Burlap","T_VK_Burlap",0.95), tex_mat("M_VK_Soil",None,1.0,flat=(0.20,0.13,0.08)), tex_mat("M_VK_Void",None,1.0,flat=(0.015,0.012,0.01)), tex_mat("M_VK_Rock","T_VK_Rock"), tex_mat("M_VK_Clay",None,0.8,flat=(0.7,0.35,0.2)), tex_mat("M_VK_Clock","T_VK_Clock"), bpy.data.materials["M_VK_Foliage"], bpy.data.materials["M_VK_Crops"],
            bpy.data.materials["M_VK_BarkOak"], bpy.data.materials["M_VK_BarkBirch"], bpy.data.materials["M_VK_BarkPine"],
            bpy.data.materials["M_VK_Leaves"], bpy.data.materials["M_VK_Moss"], bpy.data.materials["M_VK_RockMossy"], bpy.data.materials["M_VK_BarkMossy"],
            bpy.data.materials["M_VK_EndGrain"], tex_mat("M_VK_MushRed",None,0.45,flat=(0.74,0.07,0.05)), tex_mat("M_VK_MushBrown",None,0.6,flat=(0.52,0.31,0.15)),
            tex_mat("M_VK_MushStem",None,0.7,flat=(0.93,0.89,0.78)), tex_mat("M_VK_MushGlow",None,0.4,flat=(0.35,0.85,1.0),emit=(0.25,0.8,1.0)),
            tex_mat("M_VK_StoneBlock","T_VK_StoneBlock"), tex_mat("M_VK_FieldStone","T_VK_FieldStone"), tex_mat("M_VK_Wattle","T_VK_Wattle"),
            tex_mat("M_VK_Hide",None,0.8,flat=(0.50,0.33,0.20)), tex_mat("M_VK_Pigskin",None,0.7,flat=(0.90,0.62,0.56)),
            tex_mat("M_VK_Coal",None,0.95,flat=(0.045,0.043,0.050)), bpy.data.materials["M_VK_Net"],
            tex_mat("M_VK_Goods","T_VK_Goods_BC",0.5),
            tex_mat("M_VK_StoneDressed","T_VK_StoneBlock",tint=DRESS_TINT)]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD,HAY,PAPER,WATER,BRONZE,STAINED,STEEL,THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE,CROPS,BARK_OAK,BARK_BIRCH,BARK_PINE,LEAVES,MOSS,ROCK_MOSSY,BARK_MOSSY,ENDGRAIN,MUSH_RED,MUSH_BROWN,MUSH_STEM,MUSH_GLOW,STONE_BLOCK,FIELDSTONE,WATTLE,HIDE,PIGSKIN,COAL,NET,GOODS,DRESS=range(54)
# ---- goods atlas (T_VK_Goods, painted by vk_goods; keep the cell order in sync with vk_goods.GOODS_CELLS) ----
GOODS_CELLS=("cabbage","pumpkin","carrot","apple","bread","cheese","fish","fish_smoked",
             "hide","fur","meat","ham","sausage","turnip","herbs","pomace")
GOODS_PAD=14/512
def goods_uv(cell,u,v):
    """cell-local (u, v) in 0..1 -> atlas uv (4 x 4 cells, row 0 at the top, inset against mip bleeding)"""
    i=GOODS_CELLS.index(cell); c_,r_=i%4,i//4; s_=1-2*GOODS_PAD
    return ((c_+GOODS_PAD+min(max(u,0.0),1.0)*s_)/4,(3-r_+GOODS_PAD+min(max(v,0.0),1.0)*s_)/4)
def goods_map(k,geom,cell,axis=(0,0,1),ref=None,c=None,plane=None,caps=False):
    """put an item on the goods atlas: material GOODS, smooth, UVs in `cell`. geom: its verts or faces.
    Default: v along `axis` over the item's extent (0 = bottom / tail / tip), u = the unsigned angle around the axis
    from `ref` (0..pi -> 0..1, mirrored so there is no seam). plane=(A, B): planar u along A, v along B over the bbox.
    caps=True (cylinders): flat end faces get a top-down planar mapping instead of one stretched row."""
    fs=[g_ for g_ in geom if isinstance(g_,bmesh.types.BMFace)] or list({f for v in geom for f in v.link_faces})
    if not fs: return fs
    vs={v for f in fs for v in f.verts}
    c=sum((v.co for v in vs),Vector())/len(vs) if c is None else Vector(c)
    if plane:
        A=Vector(plane[0]).normalized(); B=Vector(plane[1]).normalized()
        a=[(v.co-c).dot(A) for v in vs]; b=[(v.co-c).dot(B) for v in vs]; a0,a1,b0,b1=min(a),max(a),min(b),max(b)
        for f in fs:
            f.material_index=GOODS; f.smooth=True
            for l in f.loops:
                p=l.vert.co-c; l[k.uv].uv=goods_uv(cell,(p.dot(A)-a0)/max(a1-a0,1e-6),(p.dot(B)-b0)/max(b1-b0,1e-6))
        return fs
    ax=Vector(axis).normalized()
    ref=Vector(ref) if ref is not None else (Vector((1,0,0)) if abs(ax.x)<0.9 else Vector((0,1,0)))
    ref=(ref-ax*ref.dot(ax)).normalized()
    t=[(v.co-c).dot(ax) for v in vs]; t0,t1=min(t),max(t)
    side=ax.cross(ref); rmax=max(((v.co-c)-ax*(v.co-c).dot(ax)).length for v in vs) or 1.0
    for f in fs:
        f.material_index=GOODS; f.smooth=True
        if caps and abs(f.normal.dot(ax))>0.85:
            f.smooth=False
            for l in f.loops:
                p=l.vert.co-c; l[k.uv].uv=goods_uv(cell,0.5+0.45*p.dot(ref)/rmax,0.5+0.45*p.dot(side)/rmax)
            continue
        for l in f.loops:
            p=l.vert.co-c; hh=p.dot(ax); r=p-ax*hh
            u=0.5 if r.length<1e-7 else math.acos(max(-1.0,min(1.0,r.normalized().dot(ref))))/math.pi
            l[k.uv].uv=goods_uv(cell,u,(hh-t0)/max(t1-t0,1e-6))
    return fs
def kit_fish(k,M,L=0.5,cell="fish",ref=None):
    """fish on the goods atlas, placed by matrix M. Local frame: head at +X, flattened in Y, back toward +Z. Lofted
    body narrowing to a tail stalk, a forked tail fin (two lobes) and a dorsal fin in the XZ plane, 6 mm thick so their
    two sides never z-fight. ref: the atlas's back direction (default the fish's back). Returns the faces."""
    prof=[(0.5,0.0),(0.44,0.055),(0.3,0.11),(0.1,0.13),(-0.15,0.11),(-0.34,0.06),(-0.45,0.032),(-0.47,0.0)]
    n=8; rings=[]; bm=k.bm
    for (x,r) in prof:
        if r==0: rings.append([bm.verts.new((x*L,0,0))]); continue
        rings.append([bm.verts.new((x*L,math.cos(2*math.pi*(i+0.5)/n)*r*L*0.42,math.sin(2*math.pi*(i+0.5)/n)*r*L)) for i in range(n)])
    body=[]
    for a,b in zip(rings[:-1],rings[1:]):
        if len(a)==1:
            for i in range(n): body.append(bm.faces.new((a[0],b[(i+1)%n],b[i])))
        elif len(b)==1:
            for i in range(n): body.append(bm.faces.new((a[i],a[(i+1)%n],b[0])))
        else:
            for i in range(n): body.append(bm.faces.new((a[i],a[(i+1)%n],b[(i+1)%n],b[i])))
    fins=[]; fv=[]
    def plate(pts,th=0.003):                            # thin triangular plate in the XZ plane
        a=[bm.verts.new((x*L,-th,z*L)) for x,z in pts]; b=[bm.verts.new((x*L,th,z*L)) for x,z in pts]
        fs_=[bm.faces.new(a),bm.faces.new(b[::-1])]+[bm.faces.new((a[i],a[(i+1)%3],b[(i+1)%3],b[i])) for i in range(3)]
        fins.extend(fs_); fv.extend(a+b)
    plate(((-0.43,0.0),(-0.67,0.2),(-0.57,0.0)))           # tail: upper lobe ...
    plate(((-0.43,0.0),(-0.57,0.0),(-0.67,-0.2)))          # ... lower lobe (the notch between them is open)
    plate(((-0.12,0.1),(0.14,0.1),(-0.1,0.2)))             # dorsal fin, its base inside the back
    bmesh.ops.transform(bm,matrix=M,verts=[v for r in rings for v in r]+fv)
    bmesh.ops.recalc_face_normals(bm,faces=body); bmesh.ops.recalc_face_normals(bm,faces=fins)
    M3=M.to_3x3()
    fs=goods_map(k,body+fins,cell,axis=M3@Vector((1,0,0)),ref=ref if ref is not None else M3@Vector((0,0,1)),c=M@Vector((0,0,0)))
    for f in fins: f.smooth=False
    return fs
VARIANT_MATS={
 "plaster":{"Cream":None,"White":("T_VK_Plaster",(1.10,1.12,1.18)),"Ochre":("T_VK_Plaster",(1.05,0.86,0.58)),"Rose":("T_VK_Plaster",(1.05,0.84,0.78)),
            "Daub":("T_VK_Plaster",(0.80,0.65,0.47)),"Sage":("T_VK_Plaster",(0.90,1.02,0.84)),"Sky":("T_VK_Plaster",(0.88,0.97,1.12))},
 "shutter":{"Teal":None,"Red":("T_VK_Wood",(1.6,0.55,0.45)),"Green":("T_VK_Wood",(0.75,1.3,0.6)),"Blue":("T_VK_Wood",(0.6,0.8,1.6)),"Natural":("T_VK_Wood",(1,1,1)),
            "TealWorn":("T_VK_Wood",(0.6,1.2,1.2)),"RedWorn":("T_VK_Wood",(1.6,0.55,0.45)),"GreenWorn":("T_VK_Wood",(0.75,1.3,0.6)),"BlueWorn":("T_VK_Wood",(0.6,0.8,1.6))},
 "roof":{"Red":None,"Blue":("T_VK_RoofBlue",None),"Green":("T_VK_RoofGreen",None),"Thatch":("T_VK_Thatch",None),"Slate":("T_VK_RoofSlate",None),"Shingle":("T_VK_RoofShingle",None)},
 "cloth":{"Red":None,"Blue":(None,(0.12,0.22,0.55)),"Green":(None,(0.15,0.40,0.12)),"Yellow":(None,(0.85,0.62,0.12)),"Purple":(None,(0.35,0.12,0.45)),"White":(None,(0.92,0.90,0.85))},
 "stone":{"Rubble":None,"Field":("T_VK_FieldStone",None),"Warm":("T_VK_Stone",(1.04,1.00,0.94)),"Cool":("T_VK_Stone",(0.95,0.98,1.03)),"Dark":("T_VK_Stone",(0.88,0.88,0.88))},
}
SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A,"stone":STONE,"window":WINDOW}
def lit_window_material(name="M_VK_Window_Lit",warm=(1.0,0.46,0.12),strength=1.4):
    """the kit window glass lit from inside: warm emission where the texture is glass (bluish), none on the wooden
    muntins (reddish) -- mask = smoothstep(blue - red)"""
    m=bpy.data.materials.get(name)
    if m is not None:                                   # update in place (meshes keep pointing at it)
        mx=next((n for n in m.node_tree.nodes if n.label=="LIT"),None)
        if mx is not None:
            mx.inputs[6].default_value=(warm[0]*0.08,warm[1]*0.08,warm[2]*0.08,1); mx.inputs[7].default_value=(*warm,1)
            next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Emission Strength"].default_value=strength
            return m
        bpy.data.materials.remove(m)
    m=bpy.data.materials["M_VK_Window"].copy(); m.name=name
    nt=m.node_tree; L=nt.links
    b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")
    bc=next((n for n in nt.nodes if n.type=="TEX_IMAGE" and n.image and n.image.name.endswith("_BC")),None)
    sep=nt.nodes.new("ShaderNodeSeparateColor"); L.new(bc.outputs[0],sep.inputs[0])
    d=nt.nodes.new("ShaderNodeMath"); d.operation="SUBTRACT"; L.new(sep.outputs[2],d.inputs[0]); L.new(sep.outputs[0],d.inputs[1])
    mr=nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type="SMOOTHSTEP"; mr.clamp=True
    mr.inputs["From Min"].default_value=-0.03; mr.inputs["From Max"].default_value=0.05; L.new(d.outputs[0],mr.inputs["Value"])
    mx=nt.nodes.new("ShaderNodeMix"); mx.data_type="RGBA"; mx.label="LIT"
    mx.inputs[6].default_value=(warm[0]*0.08,warm[1]*0.08,warm[2]*0.08,1); mx.inputs[7].default_value=(*warm,1)
    L.new(mr.outputs[0],mx.inputs[0]); L.new(mx.outputs[2],b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value=strength
    return m
def variant_mat(kind,name):
    if kind=="window": return lit_window_material() if name=="Lit" else bpy.data.materials["M_VK_Window"]
    spec=VARIANT_MATS[kind][name]
    base={"plaster":"M_VK_Plaster","shutter":"M_VK_Shutter_Teal","roof":"M_VK_RoofRed","cloth":"M_VK_Cloth_Red","stone":"M_VK_Stone"}[kind]
    if spec is None: return bpy.data.materials[base]
    img,tint=spec
    nm=f"M_VK_{kind.capitalize()}_{name}"
    if kind=="cloth": return tex_mat(nm,None,0.9,flat=tint)
    new=bpy.data.materials.get(nm) is None
    m=tex_mat(nm,img,0.8,tint=tint)
    mm=globals().get("MAT_MAP",{})
    if new and nm in mm and "pbr_material" in globals(): pbr_material(m,**mm[nm])     # e.g. painted/worn shutters
    return m
_var_cache={}
def variant_mesh(piece,style):
    """mesh copy of a kit piece with materials swapped per style dict, cached"""
    src=bpy.data.objects[piece].data
    key=(piece,)+tuple(sorted((k_,v) for k_,v in style.items()))
    me=bpy.data.meshes.get("VAR_"+str(abs(hash(key))))
    if me: return me
    me=src.copy(); me.name="VAR_"+str(abs(hash(key)))
    for kind,name in style.items():
        slot=SLOT[kind]
        if slot<len(me.materials): me.materials[slot]=variant_mat(kind,name)
    return me
class Kit:
    def __init__(s): s.bm=bmesh.new(); s.uv=s.bm.loops.layers.uv.new("UVMap"); s.cl=s.bm.loops.layers.color.new("Col")
    def project(s,faces,mi,axes=None,sizes=None,offset=(0.0,0.0),tile=None):
        t=tile or TILE.get(mi,1.0)
        for f in faces:
            if not f.is_valid: continue
            f.material_index=mi
            n=f.normal
            tt=t
            if mi==STONE and abs(n.z)>0.7: f.material_index=STONE_BLOCK; tt=TILE[STONE_BLOCK]
            if mi in (WOOD,SHUTTER) and axes:
                cand=[(sz,ax) for ax,sz in zip(axes,sizes) if abs(ax.dot(n))<0.8]
                cand.sort(key=lambda a:-a[0])
                if cand:
                    U=cand[0][1]; V=n.cross(U).normalized()
                else:
                    U=axes[0]; V=n.cross(U).normalized()
            elif abs(n.z)>0.7: U=Vector((1,0,0)); V=Vector((0,1,0))
            else:
                U=n.cross(Vector((0,0,1))); U.normalize(); V=Vector((0,0,1))
            for l in f.loops:
                p=l.vert.co; l[s.uv].uv=(p.dot(U)/tt+offset[0],p.dot(V)/tt+offset[1])
    def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0,xform=None,tile=None):
        if mi==STONE and bevel>0 and (sorted(size)[1]<0.7 or min(size)<0.25): mi=STONE_BLOCK
        r=bmesh.ops.create_cube(s.bm,size=1.0); vs=r["verts"]
        R=Matrix.Rotation(rot[2],4,"Z")@Matrix.Rotation(rot[1],4,"Y")@Matrix.Rotation(rot[0],4,"X")
        M=Matrix.Translation(Vector(center))@R@Matrix.Diagonal((*size,1))
        if xform is not None: M=xform@M; R=xform.to_3x3().to_4x4()@R
        bmesh.ops.transform(s.bm,matrix=M,verts=vs)
        if jitter:
            rnd=random.Random(seed)
            for v in vs: v.co+=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1)))*jitter
        faces=list({f for v in vs for f in v.link_faces})
        for f in faces: f.material_index=mi
        if bevel>0:
            edges=list({e for v in vs for e in v.link_edges})
            res=bmesh.ops.bevel(s.bm,geom=edges+vs,offset=min(bevel,min(size)*0.45),segments=segs,profile=0.5,affect="EDGES",clamp_overlap=True)
            faces=[f for f in faces if f.is_valid]+list(res["faces"])
            for f in faces: f.material_index=mi
        s.bm.normal_update()
        axes=[(R@Vector(a)).normalized() for a in ((1,0,0),(0,1,0),(0,0,1))]
        c=Vector(center) if xform is None else xform@Vector(center)
        h=abs(hash((round(c.x,2),round(c.y,2),round(c.z,2))))
        off=(0.0,0.0) if (mi in (STONE,ASHLAR,FIELDSTONE) and bevel==0) else ((h%997)/997.0,(h//997%991)/991.0)
        s.project(faces,mi,axes,size,offset=off,tile=tile)
        return [v for f in faces for v in f.verts]
    def quad(s,pts,mi,uvs=None):
        vs=[s.bm.verts.new(p) for p in pts]; f=s.bm.faces.new(vs); f.material_index=mi; s.bm.normal_update()
        if uvs:
            for l,u in zip(f.loops,uvs): l[s.uv].uv=u
        else: s.project([f],mi)
        return f
    def finish(s,name,coll,wobble=True,grime=True,loc=(0,0,0)):
        bm=s.bm
        if wobble:
            for v in bm.verts:
                p=v.co
                # periodic in x (period = CELL) so neighbouring modules meet exactly
                v.co.y+=0.035*math.sin(2*math.pi*p.x/CELL+0.9)*math.sin(math.pi*max(0,min(p.z,6))/6)
                v.co.x+=0.02*math.sin(2*math.pi*p.z/2.3+0.4)
        bm.normal_update()
        for f in bm.faces:
            for l in f.loops:
                z=l.vert.co.z
                g=1.0
                if grime: g=0.62+0.38*min(1,max(0,z)/0.9)
                if f.normal.z<-0.6: g*=0.72    # undersides darker (painted AO)
                l[s.cl]=(g,g*0.98,g*0.95,1)
        me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth=p.material_index in (APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF) or (p.material_index==GOODS and p.use_smooth)
        old=bpy.data.objects.get(name)
        if old: bpy.data.objects.remove(old)
        o=bpy.data.objects.new(name,me); coll.objects.link(o); o.location=loc
        for m in kit_mats(): me.materials.append(m)
        o["kit"]="VillageHouse"; o["cell_m"]=CELL
        return o

def batter(k,amt=0.08):
    for v in k.bm.verts:
        if v.co.y<-0.2 and v.co.z<0.05: v.co.y-=amt
def grid_cut(k,vs,step=0.5):
    geom=list(set(vs)|{e for v in vs for e in v.link_edges}|{f for v in vs for f in v.link_faces})
    xs=[v.co.x for v in vs]; zs=[v.co.z for v in vs]
    x=math.floor(min(xs)/step)*step+step
    while x<max(xs)-0.05:
        r=bmesh.ops.bisect_plane(k.bm,geom=geom,plane_co=(x,0,0),plane_no=(1,0,0)); geom=list(set(geom)|set(r["geom"]))
        x+=step
    z=math.floor(min(zs)/step)*step+step
    while z<max(zs)-0.05:
        r=bmesh.ops.bisect_plane(k.bm,geom=[g for g in geom if g.is_valid],plane_co=(0,0,z),plane_no=(0,0,1)); geom=list(set(geom)|set(r["geom"]))
        z+=step
def stone_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25,mi=None):
    vs=k.box(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),STONE if mi is None else mi,bevel=0)
    grid_cut(k,vs)
def plinth(k,x0=-1.5,x1=1.5):
    k.box(((x0+x1)/2,-0.05,0.18),(x1-x0,0.62,0.36),STONE,bevel=0)
def shutter(k,hx,side,z0,h,w=0.56,ang=2.1):
    # side=-1 left, +1 right; hinge at (hx, -0.3); rotate open by ang
    R=Matrix.Rotation(side*ang,4,"Z")
    def put(center,size,mi):
        k.box(center,size,mi,bevel=0.015,xform=Matrix.Translation((hx,-0.32,0))@R)
    for i in range(3): put((-side*(0.1+i*0.185),-0.03,z0+h/2),(0.17,0.05,h),SHUTTER)
    for zz in (z0+0.2,z0+h-0.2): put((-side*w/2,-0.07,zz),(w-0.04,0.04,0.1),SHUTTER)
    put((-side*w*0.95,-0.09,z0+0.3),(0.03,0.02,0.12),IRON)
def window_frame(k,x0,x1,z0,z1,depth_y=-0.02,sill=True,shutters=True,face=-0.25):
    w=x1-x0; h=z1-z0
    k.quad([(x0,depth_y,z0),(x1,depth_y,z0),(x1,depth_y,z1),(x0,depth_y,z1)],WINDOW,uvs=[(0,0),(w,0),(w,h),(0,h)])
    for sx in (x0-0.07,x1+0.07): k.box((sx,face-0.02,(z0+z1)/2),(0.16,0.3,h+0.1),WOOD,bevel=0.03)
    k.box(((x0+x1)/2,face-0.05,z1+0.12),(w+0.5,0.36,0.24),WOOD,bevel=0.04)
    k.box(((x0+x1)/2,depth_y-0.03,(z0+z1)/2),(0.07,0.06,h),WOOD,bevel=0.01)
    k.box(((x0+x1)/2,depth_y-0.03,z0+h*0.55),(w,0.06,0.07),WOOD,bevel=0.01)
    if sill: k.box(((x0+x1)/2,face-0.1,z0-0.06),(w+0.36,0.46,0.14),STONE,bevel=0.03)
    if shutters:
        shutter(k,x0-0.14,-1,z0,h); shutter(k,x1+0.14,1,z0,h)
# ---------------- ground floor stone walls
def wall_stone_plain(k):
    stone_panel(k,-1.5,1.5,0,H1); plinth(k); batter(k)
def wall_stone_window(k):
    x0,x1,z0,z1=-0.55,0.55,1.05,2.25
    stone_panel(k,-1.5,x0,0,H1); stone_panel(k,x1,1.5,0,H1)
    stone_panel(k,x0,x1,0,z0); stone_panel(k,x0,x1,z1,H1)
    plinth(k); batter(k); window_frame(k,x0,x1,z0,z1)
def wall_stone_door(k):
    hw=0.68; spring=2.0; top=spring+hw
    stone_panel(k,-1.5,-hw,0,H1); stone_panel(k,hw,1.5,0,H1); stone_panel(k,-hw,hw,top,H1)
    z=spring
    while z<top-0.01:
        dz=0.08; c=math.sqrt(max(0,hw*hw-(z+dz/2-spring)**2))
        for s in(-1,1): stone_panel(k,min(s*c,s*hw),max(s*c,s*hw),z,z+dz)
        z+=dz
    plinth(k,-1.5,-hw-0.02); plinth(k,hw+0.02,1.5); batter(k)
    # voussoirs: chunky arch stones
    n=7
    for i in range(n):
        a=math.pi*(i+0.5)/n; r=hw+0.2
        k.box((math.cos(a)*r,-0.3,spring+math.sin(a)*r),(0.34,0.16,0.42 if i!=n//2 else 0.5),STONE,rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2)
    for s in(-1,1):
        for j,zz in enumerate((0.35,1.05,1.7)):
            k.box((s*(hw+0.16),-0.3,zz),(0.34 if j%2 else 0.46,0.16,0.62),STONE,bevel=0.05,segs=2)
    # door leaf
    for i in range(5):
        x=-hw+0.02+(i+0.5)*(2*hw-0.04)/5; top_i=spring+math.sqrt(max(0,hw*hw-x*x))-0.03
        k.box((x,0.02,top_i/2),((2*hw-0.04)/5-0.015,0.1,top_i),WOOD,bevel=0.012)
    for zz in (0.45,1.55):
        k.box((0,-0.05,zz),(2*hw-0.1,0.03,0.11),IRON,bevel=0.01)
        for s in(-1,1): k.box((s*(hw-0.12),-0.07,zz),(0.08,0.03,0.08),IRON,bevel=0.01)
    k.box((0.38,-0.08,1.05),(0.06,0.06,0.16),IRON,bevel=0.01)
    k.quad([(-hw,0.075,0.0),(hw,0.075,0.0),(hw,0.075,top),(-hw,0.075,top)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])   # dark behind the board joints
    # reveal (inner surfaces of the opening)
    k.box((0,-0.02,0.08),(2*hw+0.1,0.5,0.16),STONE,bevel=0.02)
    k.box((0,-0.55,0.1),(1.7,0.6,0.2),STONE,bevel=0.05,segs=2,jitter=0.02,seed=3)
def corner_stone(k):
    # corner at origin, outer faces toward -X and -Y
    k.box((0,0,H1/2),(0.8,0.8,H1),STONE,bevel=0)
    k.box((0,0,0.2),(1.0,1.0,0.4),STONE,bevel=0.05,segs=2)
    z=0.4; i=0; rnd=random.Random(5)
    while z<H1-0.05:
        h=min(rnd.uniform(0.38,0.5),H1-z)
        long_x=(i%2==0)
        sx,sy=(1.05,0.62) if long_x else (0.62,1.05)
        cx=-0.43+sx/2; cy=-0.43+sy/2
        k.box((cx,cy,z+h/2),(sx,sy,h-0.03),STONE,bevel=0.06,segs=2,jitter=0.015,seed=i)
        z+=h; i+=1
# ---------------- upper floor timber walls (jettied)
FACE2=-0.40
def timber_frame(k,window=False,pattern='V'):
    # belt beam + joist ends
    k.box((0,-0.14,0.15),(CELL,0.52,0.3),WOOD,bevel=0.04)
    for i in range(6):
        x=-1.25+i*0.5
        k.box((x,-0.47,-0.1),(0.16,0.3,0.2),WOOD,bevel=0.03)
    # plaster infill
    if not window:
        grid_cut(k,k.box((0,-0.08,H2/2+0.15),(CELL,0.46,H2-0.3),PLASTER,bevel=0))
    else:
        for (a,b,c,d) in ((-1.5,-0.5,0.3,H2),(0.5,1.5,0.3,H2),(-0.5,0.5,0.3,0.95),(-0.5,0.5,2.15,H2)):
            grid_cut(k,k.box(((a+b)/2,-0.08,(c+d)/2),(b-a,0.46,d-c),PLASTER,bevel=0))
    # top plate
    k.box((0,-0.2,H2-0.1),(CELL,0.46,0.22),WOOD,bevel=0.04)
    # left edge post (right edge belongs to the next module / corner)
    k.box((-1.5,-0.33,H2/2),(0.26,0.2,H2-0.4),WOOD,bevel=0.03)
    if not window and pattern!="V":
        braces_pattern(k,pattern)
    elif not window:
        k.box((0,-0.33,H2/2),(0.22,0.2,H2-0.4),WOOD,bevel=0.03)
        for s in(-1,1):
            x0,z0=s*1.3,0.35; x1,z1=s*0.15,H2-0.25
            L=math.hypot(x1-x0,z1-z0); ang=math.atan2(z1-z0,x1-x0)
            k.box(((x0+x1)/2,-0.33,(z0+z1)/2),(L,0.18,0.17),WOOD,rot=(0,-ang,0),bevel=0.03)
        k.box((0,-0.33,1.35),(CELL,0.18,0.16),WOOD,bevel=0.03)
    else:
        x0,x1,z0,z1=-0.5,0.5,0.95,2.15
        window_frame(k,x0,x1,z0,z1,depth_y=-0.12,sill=False,shutters=False,face=FACE2+0.05)
        k.box((0,FACE2+0.02,z0-0.1),(1.4,0.26,0.16),WOOD,bevel=0.03)
        for s in(-1,1):
            k.box((s*0.72,-0.33,H2/2),(0.2,0.2,H2-0.4),WOOD,bevel=0.03)
            x0b,z0b=s*1.35,0.35; x1b,z1b=s*0.82,0.85
            L=math.hypot(x1b-x0b,z1b-z0b); ang=math.atan2(z1b-z0b,x1b-x0b)
            k.box(((x0b+x1b)/2,-0.33,(z0b+z1b)/2),(L,0.18,0.15),WOOD,rot=(0,-ang,0),bevel=0.03)
def corner_timber(k):
    k.box((-0.2,-0.2,0.15),(0.66,0.66,0.3),WOOD,bevel=0.04)
    k.box((-0.26,-0.26,H2/2),(0.34,0.34,H2),WOOD,bevel=0.05,segs=2)
    k.box((-0.2,-0.2,H2-0.1),(0.62,0.62,0.22),WOOD,bevel=0.04)
    # dragon beam end under the corner
    k.box((-0.45,-0.45,-0.12),(0.26,0.26,0.26),WOOD,rot=(0,0,math.pi/4),bevel=0.04)
    k.box((-0.3,-0.3,-0.6),(0.2,0.2,0.8),WOOD,rot=(0.5,-0.5,0),bevel=0.03)

PITCH=math.radians(52); KICK=math.radians(26); HALF=3.0; EAVE=4.35; RT=0.3
def roof_z(ay):
    # top surface height at |y|=ay (relative to wall top), with bell-cast eave
    if ay<=HALF: return 0.35+(HALF-ay)*math.tan(PITCH)
    return 0.35-(ay-HALF)*math.tan(KICK)
RIDGE=roof_z(0)
def roof_profile():
    ys=[0,0.75,1.5,2.25,3.0,3.45,3.9,EAVE]
    return [(y,roof_z(y)) for y in ys]
def roof_sag(x,ay):
    return -0.07*(0.5-0.5*math.cos(2*math.pi*x/CELL))*(1-ay/EAVE)   # gentle periodic sag, zero at module seams
def roof_slab(k,x0,x1,side,end_caps=(False,False)):
    prof=roof_profile(); nx=max(2,int(round((x1-x0)/0.5)))
    xs=[x0+(x1-x0)*i/nx for i in range(nx+1)]
    # accumulate along-slope distance from eave for V
    dist=[0.0]*len(prof)
    for i in range(len(prof)-2,-1,-1):
        dist[i]=dist[i+1]+math.hypot(prof[i+1][0]-prof[i][0],prof[i+1][1]-prof[i][1])
    top=[];bot=[]
    for x in xs:
        rt=[];rb=[]
        for j,(ay,z) in enumerate(prof):
            a=prof[max(j-1,0)]; b=prof[min(j+1,len(prof)-1)]
            ty,tz=b[0]-a[0],b[1]-a[1]; L=math.hypot(ty,tz); ny,nz=tz/L,-ty/L   # outward normal (in ay,z)
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
        j=len(prof)-1   # eave fascia
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
def ridge(k,x0,x1):
    n=max(1,int(round((x1-x0)/0.75)))
    for i in range(n):
        xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n; xm=(xa+xb)/2
        k.box((xm,0,RIDGE+0.1+roof_sag(xm,0)),(xb-xa+0.04,0.36,0.36),ROOF,rot=(math.pi/4,0,0),bevel=0.1,segs=2)
def roof_mid(k):
    for s in(-1,1): roof_slab(k,-1.5,1.5,s)
    ridge(k,-1.5,1.5)
GX=2.45   # gable overhang end (x)
def roof_gable(k):
    for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True))
    ridge(k,-1.5,GX+0.1)
    gable_end(k)
def gable_end(k,kind='timber',trim=True):
    # bargeboards following both slopes
    prof=roof_profile()
    for s in((-1,1) if trim else ()):
        for j in range(len(prof)-1):
            (y0,z0),(y1,z1)=prof[j],prof[j+1]
            L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,y1-y0)
            yc=s*(y0+y1)/2; zc=(z0+z1)/2-0.16
            k.box((GX+0.08,yc,zc),(0.2,L+0.2,0.46),WOOD,rot=(s*ang,0,0),bevel=0.05,segs=2)
    # finial
    if trim:
        k.box((GX+0.08,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,segs=2)
        k.box((GX+0.08,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)
    # gable triangle wall (timber framed plaster), face at x=+1.5+0.40, follows the roof underside exactly
    XF={"timber":1.5+0.40,"stone":1.5+0.30,"planks":1.5+0.26}[kind]; XB=1.5-0.05
    TRI={"timber":PLASTER,"stone":ASHLAR,"planks":PLANKS}[kind]
    def under(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.05
    YC=HALF+0.02
    ys=[YC,2.5,2.0,1.5,1.0,0.5,0.0]
    outline=[(-YC,0.0),(YC,0.0)]+[(y,under(y)) for y in ys]+[(-y,under(y)) for y in ys[::-1][1:]]
    for (xf,flip) in ((XF-0.06,False),(XB,True)):
        vs=[k.bm.verts.new((xf,y,z)) for y,z in outline]
        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=TRI
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[TRI],l.vert.co.z/TILE[TRI])
    k.bm.normal_update()
    top=under(0)
    if kind!="timber":
        gable_special(k,kind,XF,top,YC); return
    k.box((XF-0.02,0,0.12),(0.2,2*YC,0.24),WOOD,bevel=0.04)
    for i in range(6):
        k.box((XF+0.1,-2.5+i*1.0,-0.12),(0.3,0.16,0.2),WOOD,bevel=0.03)
    zc=top*0.45; half_c=YC*(1-zc/top)*0.98
    k.box((XF-0.02,0,zc),(0.18,2*half_c,0.2),WOOD,bevel=0.035)
    k.box((XF-0.02,0,top/2),(0.18,0.24,top),WOOD,bevel=0.035)
    for s_ in(-1,1):
        # raking beams: follow the underside, inset 0.12
        L=math.hypot(YC,top); ang=math.atan2(top,YC)
        k.box((XF-0.02,s_*YC/2,top/2-0.14),(0.18,L,0.2),WOOD,rot=(-s_*ang,0,0),bevel=0.035)
        k.box((XF-0.02,s_*1.6,zc/2+0.1),(0.16,0.16,zc-0.1),WOOD,bevel=0.03)
    wz=zc+0.25
    k.quad([(XF-0.04,-0.35,wz),(XF-0.04,0.35,wz),(XF-0.04,0.35,wz+0.8),(XF-0.04,-0.35,wz+0.8)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,0.8),(0,0.8)])
    for yy in(-0.42,0.42): k.box((XF+0.02,yy,wz+0.4),(0.14,0.13,0.95),WOOD,bevel=0.025)
    for zz in(wz-0.05,wz+0.85): k.box((XF+0.02,0,zz),(0.16,0.95,0.13),WOOD,bevel=0.025)
    k.box((XF+0.02,0,wz+0.4),(0.06,0.05,0.8),WOOD,bevel=0.01)
def chimney(k):
    y0=1.3
    k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STONE,bevel=0.06,segs=2,tile=1.8)
    k.box((0,y0,RIDGE+1.55),(1.25,1.25,0.22),STONE,bevel=0.07,segs=2)
    for dx in(-0.22,0.22):
        k.box((dx,y0,RIDGE+1.9),(0.3,0.3,0.5),STONE,bevel=0.06,segs=2)
    k.box((0,y0,RIDGE+1.0),(1.12,1.12,0.16),STONE,bevel=0.05)

def roof_variant(src,suffix,matname):
    o=bpy.data.objects.get(src.name+suffix)
    me=src.data.copy(); me.name=src.name+suffix
    me.materials[ROOF]=bpy.data.materials[matname]
    if o: o.data=me
    else:
        o=bpy.data.objects.new(src.name+suffix,me); vcol("VK_Pieces").objects.link(o)
    return o
def place(coll,piece,x,y,z,rot_deg,origin):
    src=bpy.data.objects[piece]
    o=bpy.data.objects.new(piece+"_inst",src.data); coll.objects.link(o)
    ox,oy,orz=origin
    c,s=math.cos(orz),math.sin(orz)
    o.location=(ox+x*c-y*s,oy+x*s+y*c,z); o.rotation_euler=(0,0,orz+math.radians(rot_deg))
    return o
def build_house(coll,origin,n,stories=2,roof="Red",front=None,back=None,upper_front=None,upper_back=None,ends="W",chimney_cell=None):
    """front/back: string per cell  D=door W=window .=plain ; ends: pattern for both gable end walls (2 cells)"""
    L=n*CELL; sfx="" if roof=="Red" else "_Blue"
    front=front or "."*n; back=back or "."*n
    upper_front=upper_front or "W"*n; upper_back=upper_back or "."*n
    gw={"D":"SM_VK_Wall_Stone_Door","W":"SM_VK_Wall_Stone_Window",".":"SM_VK_Wall_Stone"}
    uw={"W":"SM_VK_Wall_Timber_Window",".":"SM_VK_Wall_Timber"}
    for i in range(n):
        x=-L/2+1.5+3*i
        place(coll,gw[front[i]],x,-3,0,0,origin); place(coll,gw[back[::-1][i]],x,3,0,180,origin)
    for j,yy in enumerate((-1.5,1.5)):
        e=ends[j] if len(ends)>1 else ends
        place(coll,gw[e],-L/2,yy,0,-90,origin); place(coll,gw[e],L/2,-yy,0,90,origin)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
        place(coll,"SM_VK_Corner_Stone",cx,cy,0,r,origin)
    top=H1
    if stories==2:
        for i in range(n):
            x=-L/2+1.5+3*i
            place(coll,uw[upper_front[i]],x,-3,H1,0,origin); place(coll,uw[upper_back[::-1][i]],x,3,H1,180,origin)
        for yy in (-1.5,1.5):
            place(coll,"SM_VK_Wall_Timber",-L/2,yy,H1,-90,origin); place(coll,"SM_VK_Wall_Timber",L/2,-yy,H1,90,origin)
        for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
            place(coll,"SM_VK_Corner_Timber",cx,cy,H1,r,origin)
        top=H1+H2
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==n-1: place(coll,"SM_VK_Roof_Gable"+sfx,x,0,top,0,origin)
        elif i==0: place(coll,"SM_VK_Roof_Gable"+sfx,x,0,top,180,origin)
        else: place(coll,"SM_VK_Roof_Mid"+sfx,x,0,top,0,origin)
    if chimney_cell is not None:
        place(coll,"SM_VK_Chimney",-L/2+1.5+3*chimney_cell,0,top,0,origin)

def prop_flowerbox(k):
    k.box((0,0,0.12),(1.25,0.32,0.24),WOOD,bevel=0.03)
    for sx in(-0.45,0.45): k.box((sx,0.08,-0.1),(0.08,0.2,0.25),WOOD,bevel=0.02)
    rnd=random.Random(4)
    for i in range(16):
        x=-0.52+i*0.07; 
        k.box((x,rnd.uniform(-0.08,0.08),0.3+rnd.uniform(0,0.08)),(0.16,0.14,0.16),LEAF,rot=(0,0,rnd.uniform(0,3)),bevel=0.05,segs=1)
    for i in range(11):
        x=-0.5+i*0.1+rnd.uniform(-.03,.03)
        vs=bmesh.ops.create_icosphere(k.bm,subdivisions=1,radius=0.075)["verts"]
        for v in vs: v.co+=Vector((x,rnd.uniform(-0.08,0.08),0.43+rnd.uniform(0,0.1)))
        for f in {f for v in vs for f in v.link_faces}: f.material_index=PINK if i%3 else YELLOW
def prop_lantern(k):
    k.box((0,0.05,0.0),(0.1,0.1,0.35),IRON,bevel=0.02)
    k.box((0,-0.2,0.15),(0.06,0.5,0.06),IRON,bevel=0.015)
    k.box((0,-0.42,0.05),(0.03,0.03,0.2),IRON,bevel=0)
    k.box((0,-0.42,-0.22),(0.24,0.24,0.34),GLOW,bevel=0.03)
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*0.12,-0.42+sy*0.12,-0.22),(0.035,0.035,0.38),IRON,bevel=0)
    k.box((0,-0.42,-0.02),(0.32,0.32,0.07),IRON,bevel=0.02); k.box((0,-0.42,0.06),(0.2,0.2,0.1),IRON,bevel=0.03)
    k.box((0,-0.42,-0.41),(0.28,0.28,0.05),IRON,bevel=0.015)
def prop_sign(k):
    k.box((0,0.03,0),(0.14,0.1,0.5),IRON,bevel=0.02)
    k.box((0,-0.55,0.12),(0.07,1.1,0.07),IRON,bevel=0.015)
    vs=k.box((0,-0.78,-0.05),(0.04,0.04,0.7),IRON,bevel=0,rot=(0.6,0,0))
    for yy in(-0.35,-0.95): k.box((0,yy,-0.05),(0.02,0.02,0.3),IRON,bevel=0)
    k.box((0,-0.65,-0.45),(0.08,0.9,0.6),WOOD,bevel=0.04,segs=2)
    k.box((0,-0.65,-0.45),(0.1,0.3,0.3),YELLOW,rot=(math.pi/4,0,0),bevel=0.03)

def merge_kit(dst,src,M):
    """append src Kit geometry into dst Kit, transformed by matrix M"""
    me=bpy.data.meshes.new("_tmp"); src.bm.to_mesh(me); src.bm.free()
    me.transform(M)
    dst.bm.from_mesh(me); bpy.data.meshes.remove(me)
def slope_dist(ay):
    ay=min(ay,EAVE)
    if ay>=HALF: return (EAVE-ay)/math.cos(KICK)
    return (EAVE-HALF)/math.cos(KICK)+(HALF-ay)/math.cos(PITCH)
def roof_L_corner(k):
    """Junction of two wings: main wing A along +X (ridge y=0), wing B along +Y (ridge x=0).
    Covers the 2x2-cell junction square x,y in [-3,3]; A has its gable on the outer -X side,
    B joins with valleys along y=|x|. Neighbours: Roof_Mid at x>3 (rot 0) and at y>3 (rot 90)."""
    GO=-HALF-(GX-1.5)          # gable overhang edge x = -3.95
    def zA(y): return roof_z(abs(y))
    def zB(x): return roof_z(abs(x))
    def surf(x,y):
        if y<=0: return zA(y),"A"
        a,b=zA(y),zB(x)
        return (a,"A") if a>=b else (b,"B")
    xs=[GO,-3.5]+[i*0.5 for i in range(-6,7)]
    ys=[-EAVE,-3.9,-3.45]+[i*0.5 for i in range(-6,7)]
    xs=sorted(set(round(v,4) for v in xs)); ys=sorted(set(round(v,4) for v in ys))
    T=TILE[ROOF]; W=TILE[WOOD]
    top={};bot={}
    for x in xs:
        for y in ys:
            z,_=surf(x,y); top[(x,y)]=k.bm.verts.new((x,y,z)); bot[(x,y)]=k.bm.verts.new((x,y,z-RT*1.25))
    def uv_for(p,region):
        x,y,z=p
        return ((x-1.5)/T,slope_dist(abs(y))/T) if region=="A" else ((y-1.5)/T,slope_dist(abs(x))/T)
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
            q=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            # split along the valley direction where the crease runs through the quad
            if y0>=0 and x0>=0: tris=[(0,1,2),(0,2,3)]
            elif y0>=0 and x1<=0: tris=[(0,1,3),(1,2,3)]
            else: tris=[(0,1,2),(0,2,3)]
            for tr in tris:
                pts=[q[t_] for t_ in tr]
                cx=sum(p[0] for p in pts)/3; cy=sum(p[1] for p in pts)/3
                _,reg=surf(cx,cy)
                f=k.bm.faces.new([top[p] for p in pts]); f.material_index=ROOF
                for l,p in zip(f.loops,pts): l[k.uv].uv=uv_for((p[0],p[1],0),reg)
                fb=k.bm.faces.new([bot[p] for p in pts[::-1]]); fb.material_index=WOOD
                for l in fb.loops: l[k.uv].uv=(l.vert.co.x/W,l.vert.co.y/W)
    # fascia along the outer eave (y=-EAVE) and the gable edge (x=GO)
    def side(ptsa,ptsb):
        for (a_,b_) in zip(ptsa,ptsb):
            f=k.bm.faces.new((top[a_],top[b_],bot[b_],bot[a_])); f.material_index=WOOD
            for l in f.loops: l[k.uv].uv=((l.vert.co.x+l.vert.co.y)/W,l.vert.co.z/W)
    side([(xs[i+1],ys[0]) for i in range(len(xs)-1)],[(xs[i],ys[0]) for i in range(len(xs)-1)])
    side([(xs[0],ys[j]) for j in range(len(ys)-1)],[(xs[0],ys[j+1]) for j in range(len(ys)-1)])
    k.bm.normal_update()
    # ridge caps: A ridge through the whole piece, B ridge from the junction to the +Y seam
    ridge(k,GO-0.1,HALF)
    n=4
    for i in range(n):
        ya=HALF*i/n; yb=HALF*(i+1)/n
        k.box((0,(ya+yb)/2,RIDGE+0.1),(0.36,yb-ya+0.04,0.36),ROOF,rot=(0,math.pi/4,0),bevel=0.1,segs=2)
    # gable end on the outer -X side: reuse gable_end (built for wall line x=+1.5) rotated 180 and shifted
    g=Kit(); gable_end(g)
    merge_kit(k,g,Matrix.Translation((-1.5,0,0))@Matrix.Rotation(math.pi,4,"Z"))

def build_L_house(coll,origin,a,b,stories=2,roof="Red",frontA=None,frontB=None,chimney=None,upper="W"):
    """L-shaped house: junction square (2x2 cells) at origin, wing A extends +X by a cells, wing B extends +Y by b cells."""
    sfx={"Red":"","Blue":"_Blue","Green":"_Green"}[roof]
    gw={"D":"SM_VK_Wall_Stone_Door","W":"SM_VK_Wall_Stone_Window",".":"SM_VK_Wall_Stone"}
    uw={"W":"SM_VK_Wall_Timber_Window",".":"SM_VK_Wall_Timber"}
    XA=3+3*a; YB=3+3*b
    frontA=frontA or ("W"*(2+a)); frontB=frontB or ("W"*(2+b))
    runs=[]  # (x,y,rot,char) wall module centres
    for i in range(2+a): runs.append((-1.5+3*i,-3,0,frontA[i]))                 # A front (outer -Y)
    for j in range(2+b): runs.append((-3,-1.5+3*j,-90,frontB[j]))              # B outer side (-X)
    for j in range(2): runs.append((XA,-1.5+3*j,90,"W" if j==0 else "."))      # A end
    for i in range(a): runs.append((4.5+3*i,3,180,"."))                          # A back
    for i in range(2): runs.append((-1.5+3*i,YB,180,"W" if i==1 else "."))     # B end
    for j in range(b): runs.append((3,4.5+3*j,90,"W"))                           # B inner side
    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    for (x,y,r,c) in runs: place(coll,gw[c],x,y,0,r,origin)
    for (x,y,r) in corners: place(coll,"SM_VK_Corner_Stone",x,y,0,r,origin)
    top=H1
    if stories==2:
        for (x,y,r,c) in runs: place(coll,uw[upper if c!="." else "."],x,y,H1,r,origin)
        for (x,y,r) in corners: place(coll,"SM_VK_Corner_Timber",x,y,H1,r,origin)
        top=H1+H2
    place(coll,"SM_VK_Roof_LCorner"+sfx,0,0,top,0,origin)
    for i in range(a):
        x=4.5+3*i
        place(coll,("SM_VK_Roof_Gable" if i==a-1 else "SM_VK_Roof_Mid")+sfx,x,0,top,0,origin)
    for j in range(b):
        y=4.5+3*j
        place(coll,("SM_VK_Roof_Gable" if j==b-1 else "SM_VK_Roof_Mid")+sfx,0,y,top,90,origin)
    if chimney: place(coll,"SM_VK_Chimney",chimney[0],chimney[1],top,chimney[2],origin)

def brace(k,x0,z0,x1,z1,w=0.17,y=-0.33):
    L=math.hypot(x1-x0,z1-z0); ang=math.atan2(z1-z0,x1-x0)
    k.box(((x0+x1)/2,y,(z0+z1)/2),(L,0.18,w),WOOD,rot=(0,-ang,0),bevel=0.03)
def braces_pattern(k,pattern):
    zb,zt=0.3,H2-0.21
    if pattern=="X":
        k.box((0,-0.33,H2/2),(0.22,0.2,H2-0.4),WOOD,bevel=0.03)
        for s_ in(-1,1):
            brace(k,s_*1.35,zb+0.05,s_*0.12,zt-0.05); brace(k,s_*1.35,zt-0.05,s_*0.12,zb+0.05,y=-0.335)
    elif pattern=="K":
        for x in(-0.75,0,0.75): k.box((x,-0.33,H2/2),(0.2,0.2,H2-0.4),WOOD,bevel=0.03)
        k.box((0,-0.33,1.25),(CELL,0.18,0.16),WOOD,bevel=0.03)
        for x0 in(-1.5,-0.75,0,0.75):
            brace(k,x0+0.1,zt-0.45,x0+0.35,zt-0.05,w=0.13)
            brace(k,x0+0.65,zt-0.45,x0+0.4,zt-0.05,w=0.13)
            brace(k,x0+0.1,0.35,x0+0.65,1.18,w=0.14)
# ---------------- plaster ground floor (cheaper houses): stone plinth + timber frame + plaster
PL=0.75
def plaster_ground(k,kind="."):
    stone_panel(k,-1.5,1.5,0,PL,-0.28,0.25); plinth(k); batter(k,0.05)
    k.box((0,-0.2,PL+0.1),(CELL,0.4,0.2),WOOD,bevel=0.035)
    k.box((0,-0.2,H1-0.11),(CELL,0.4,0.22),WOOD,bevel=0.035)
    k.box((-1.5,-0.24,(PL+H1)/2),(0.24,0.2,H1-PL-0.2),WOOD,bevel=0.03)
    if kind==".":
        grid_cut(k,k.box((0,-0.02,(PL+H1)/2),(CELL,0.44,H1-PL),PLASTER,bevel=0))
        k.box((0,-0.24,(PL+H1)/2),(0.22,0.2,H1-PL-0.2),WOOD,bevel=0.03)
        for s_ in(-1,1): brace(k,s_*1.35,PL+0.25,s_*0.15,H1-0.3,y=-0.24)
    elif kind=="W":
        x0,x1,z0,z1=-0.55,0.55,1.1,2.25
        for (a,b,c,d) in ((-1.5,x0,PL,H1),(x1,1.5,PL,H1),(x0,x1,PL,z0),(x0,x1,z1,H1)):
            grid_cut(k,k.box(((a+b)/2,-0.02,(c+d)/2),(b-a,0.44,d-c),PLASTER,bevel=0))
        window_frame(k,x0,x1,z0,z1,depth_y=0.0,sill=False,face=-0.2)
        k.box((0,-0.3,z0-0.08),(1.5,0.3,0.16),WOOD,bevel=0.03)
        for s_ in(-1,1): k.box((s_*0.85,-0.24,(PL+H1)/2),(0.2,0.2,H1-PL-0.2),WOOD,bevel=0.03)
    elif kind=="D":
        hw=0.62; top=2.3
        for (a,b,c,d) in ((-1.5,-hw,PL,H1),(hw,1.5,PL,H1),(-hw,hw,top,H1)):
            grid_cut(k,k.box(((a+b)/2,-0.02,(c+d)/2),(b-a,0.44,d-c),PLASTER,bevel=0))
        # cut the plinth for the door
        for v in [v for v in k.bm.verts]: pass
        for s_ in(-1,1): k.box((s_*(hw+0.11),-0.24,top/2),(0.22,0.24,top),WOOD,bevel=0.035)
        k.box((0,-0.26,top+0.12),(2*hw+0.6,0.3,0.26),WOOD,bevel=0.04)
        for i in range(4):
            x=-hw+(i+0.5)*(2*hw)/4
            k.box((x,0.0,top/2),((2*hw)/4-0.015,0.1,top),WOOD,bevel=0.012)
        for zz in(0.5,1.7): k.box((0,-0.06,zz),(2*hw-0.1,0.03,0.1),IRON,bevel=0.01)
        k.box((0.35,-0.08,1.05),(0.06,0.06,0.16),IRON,bevel=0.01)
        k.box((0,-0.5,0.1),(1.5,0.55,0.2),STONE,bevel=0.05,segs=2,jitter=0.02,seed=5)
def corner_plaster(k):
    k.box((-0.05,-0.05,PL/2),(0.8,0.8,PL),STONE,bevel=0.05,segs=2,jitter=0.02,seed=2)
    k.box((-0.22,-0.22,(PL+H1)/2),(0.34,0.34,H1-PL),WOOD,bevel=0.05,segs=2)
    k.box((-0.1,-0.1,H1-0.11),(0.56,0.56,0.22),WOOD,bevel=0.04)
# ---------------- market stall (2 x 1 cells footprint, front toward -Y)
STALL_TRADES=("produce","greengrocer","baker","fishmonger","potter","draper","cheese","tinker")
STALL_SIGN={"produce":YELLOW,"greengrocer":LEAF,"baker":BREAD,"fishmonger":STEEL,"potter":CLAY,"draper":PINK,"cheese":YELLOW,"tinker":IRON}
def _rot_vs(vs,c,ang,axis="Z"):
    R=Matrix.Rotation(ang,4,axis); c=Vector(c)
    for v in vs: v.co=c+R@(v.co-c)
def _mat(vs,mi,smooth=True):
    for f in {f for v in vs for f in v.link_faces}: f.material_index=mi; f.smooth=smooth
def _stall_barrels(k,W_):
    for (x,y) in ((W_/2+0.55,-0.2),(W_/2+0.5,0.55)):
        for zz,(r0,r1) in ((0.25,(0.34,0.4)),(0.75,(0.4,0.34))):
            cyl_=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=12,radius1=r0,radius2=r1,depth=0.5)["verts"]
            for v in cyl_: v.co+=Vector((x,y,zz))
            k.project({f for v in cyl_ for f in v.link_faces},WOOD)
        for zz in(0.12,0.88):
            cyl_=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=12,radius1=0.39,radius2=0.39,depth=0.06)["verts"]
            for v in cyl_: v.co+=Vector((x,y,zz))
            _mat(cyl_,IRON,False)
def _stall_sack(k,x,y,mi=CLOTH_B,s=1.0,seed=0):
    """tied grain sack: lumpy body flat on the ground, pinched shoulders, gathered neck with a cord and a tuft"""
    rnd=random.Random(seed+int(x*10)); lean=rnd.uniform(-0.12,0.12)
    R=Matrix.Rotation(lean,4,"Y"); base=Vector((x,y,0.0)); ns,nr=14,8
    rings=[]
    for q in range(nr+1):
        t=q/nr; r=0.27*(1.0+0.12*math.sin(t*math.pi))*(1.0-0.62*max(0.0,t-0.7)/0.3)
        ring=[]
        for m in range(ns):
            a=2*math.pi*m/ns; rr=r*(1.0+0.05*math.sin(3*a+seed+q))
            ring.append(k.bm.verts.new(R@Vector((rr*math.cos(a)*0.95*s,rr*math.sin(a)*0.8*s,t*0.6*s))+base))
        rings.append(ring)
    fs=[k.bm.faces.new(rings[0][::-1])]
    for q in range(nr):
        for m in range(ns):
            m2=(m+1)%ns; fs.append(k.bm.faces.new((rings[q][m],rings[q][m2],rings[q+1][m2],rings[q+1][m])))
    fs.append(k.bm.faces.new(rings[nr]))
    for f in fs: f.material_index=mi; f.smooth=True
    k.bm.normal_update(); k.project(fs,mi)
    top=R@Vector((0,0,0.6*s))+base
    _mat(_cyl(k,(top.x,top.y,top.z+0.05*s),0.07*s,0.06*s,0.12*s,10,mi),mi)
    _cyl(k,(top.x,top.y,top.z+0.03*s),0.075*s,0.075*s,0.03*s,10,HIDE)
    _mat(_ico(k,(top.x,top.y,top.z+0.13*s),0.08*s,mi,scale=(1.2,1.0,0.6),sub=1,jit=0.012,seed=seed),mi)
def stall_wares(k,trade,W_,D_):
    """goods on the counter (top z 1.02, x -1.6..1.6, y -0.85..0.15), on the back shelf (z 1.49, y ~0.65) and beside
    the stall, per trade"""
    rnd=random.Random(sum(map(ord,trade))); z0=1.02
    Ry=Matrix.Rotation(math.pi/2,4,"Y"); Rx=Matrix.Rotation(math.pi/2,4,"X")
    def crate(cx,w=0.85,d=0.62,h=0.2,cy=-0.45):
        k.box((cx,cy,z0+h/2),(w,d,h),WOOD,bevel=0.03); return z0+h
    def basket(cx,cy,r=0.3,h=0.16,z=z0):
        _cyl(k,(cx,cy,z+h/2),r,r*1.12,h,14,WOOD); return z+h
    shelf=1.49
    if trade=="produce":
        for cx,g in zip((-1.0,0.0,1.0),("APPLE","PUMPKIN","BREAD")):
            top=crate(cx,h=0.26)
            for n_ in range(9 if g=="APPLE" else (4 if g=="PUMPKIN" else 6)):
                if g=="APPLE":
                    goods_map(k,_ico(k,(cx-0.28+(n_%3)*0.28+rnd.uniform(-.03,.03),-0.62+(n_//3)*0.17,top+0.05+rnd.uniform(0,.03)),0.09,APPLE),"apple")
                elif g=="PUMPKIN":
                    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.19)["verts"]
                    for v in vs:
                        ang=math.atan2(v.co.y,v.co.x); v.co.z*=0.72; v.co*=(1+0.06*math.cos(8*ang))
                        v.co+=Vector((cx-0.2+(n_%2)*0.4,-0.58+(n_//2)*0.3,top+0.14))
                    goods_map(k,vs,"pumpkin",ref=(math.cos(math.pi/8),math.sin(math.pi/8),0))   # atlas grooves on the lobes' grooves
                else:
                    goods_map(k,_ico(k,(cx-0.25+(n_%3)*0.25,-0.58+(n_//3)*0.25,top+0.08),0.14,BREAD,scale=(0.9,1.4,0.6)),"bread",ref=(0,1,0))
    elif trade=="greengrocer":
        top=crate(-1.05)
        for n_ in range(6): goods_map(k,_ico(k,(-1.3+(n_%3)*0.25,-0.6+(n_//3)*0.28,top+0.11),0.15,LEAF,scale=(1,1,0.85),jit=0.015,seed=n_),"cabbage")
        top=crate(0.0)
        for n_ in range(12):
            x=-0.3+(n_%6)*0.12; y=-0.58+(n_//6)*0.26; a=rnd.uniform(-0.25,0.25)
            R_=Matrix.Rotation(math.pi/2+a,4,"Z")@Ry@Rx
            vs=_cyl(k,(x,y,top+0.04),0.035,0.0,0.24,6,PUMPKIN,rot=R_)
            goods_map(k,vs,"carrot",axis=-(R_.to_3x3()@Vector((0,0,1))),c=(x,y,top+0.04))           # tip -> crown
            _mat(_ico(k,(x,y+0.14,top+0.05),0.045,LEAF,scale=(1,1.6,0.7),sub=1),LEAF)
        top=crate(1.05)
        for n_ in range(12): goods_map(k,_ico(k,(0.78+(n_%4)*0.18,-0.66+(n_//4)*0.2,top+0.06),0.075,PAPER,scale=(1,1,0.9)),"turnip")
        for cx in (-0.9,0.0,0.9):
            t=basket(cx,0.62,0.22,0.12,shelf)
            for n_ in range(5): goods_map(k,_ico(k,(cx+rnd.uniform(-.1,.1),0.62+rnd.uniform(-.08,.08),t+0.03),0.08,APPLE),"apple")
    elif trade=="baker":
        t=basket(-1.0,-0.45,0.36,0.14)
        for n_ in range(5): goods_map(k,_ico(k,(-1.18+(n_%3)*0.18,-0.55+(n_//3)*0.2,t+0.05),0.14,BREAD,scale=(0.75,1.3,0.55)),"bread",ref=(0,1,0))
        k.box((0.05,-0.45,z0+0.03),(0.85,0.6,0.05),WOOD,bevel=0.015)
        for n_ in range(4): goods_map(k,_ico(k,(-0.15+(n_%2)*0.38,-0.6+(n_//2)*0.3,z0+0.11),0.14,BREAD,scale=(1,1,0.62)),"bread")
        t=basket(1.05,-0.4,0.2,0.36)
        for n_ in range(6):
            a=n_*1.05; R_=Matrix.Rotation(0.18,4,"X")@Matrix.Rotation(a,4,"Z")
            vs=_cyl(k,(1.05+0.07*math.cos(a),-0.4+0.07*math.sin(a),t+0.12),0.04,0.035,0.72,8,BREAD,rot=R_)
            goods_map(k,vs,"bread",axis=R_.to_3x3()@Vector((0,0,1)))
        for n_ in range(7): goods_map(k,_ico(k,(-1.3+n_*0.43,0.62,shelf+0.07),0.12,BREAD,scale=(1.3,0.8,0.6)),"bread")
        for n_,(x,y) in enumerate(((W_/2+0.5,-0.3),(W_/2+0.45,0.35),(W_/2+0.95,0.05))): _stall_sack(k,x,y,BURLAP,0.95)
        _stall_sack(k,-W_/2-0.45,-0.4,BURLAP)
        return
    elif trade=="fishmonger":
        k.box((0,-0.45,z0+0.05),(2.7,0.72,0.1),WOOD,bevel=0.02)
        k.box((0,-0.45,z0+0.105),(2.55,0.6,0.03),PAPER,bevel=0.01)
        for n_ in range(10):
            x=-1.1+n_*0.245; y=-0.45+rnd.uniform(-0.12,0.12); a=rnd.uniform(0.6,1.1)*(1 if n_%2 else -1)
            # lying on its side on the ice, tail fin flat; the atlas back is turned up so the dark back runs along the
            # silver flank from above
            M_=Matrix.Translation((x,y,z0+0.145))@Matrix.Rotation(a,4,"Z")@Matrix.Rotation(-math.pi/2,4,"X")
            kit_fish(k,M_,0.5,ref=(-math.sin(a)*0.7,math.cos(a)*0.7,0.7))
        for n_,x in enumerate((-1.1,-0.4,0.4,1.1)):
            # hung by the tail from the front beam: head down, flank to the street
            M_=Matrix.Translation((x,-(D_/2-0.1),2.06))@Matrix(((0,0,1,0),(0,1,0,0),(-1,0,0,0),(0,0,0,1)))
            kit_fish(k,M_,0.5)
            k.box((x,-(D_/2-0.1),2.42),(0.012,0.012,0.12),WOOD,bevel=0)
        for n_ in range(3): _mat(_ico(k,(-1.0+n_*0.9,0.62,shelf+0.1),0.13,BURLAP,scale=(1.2,0.9,0.8)),BURLAP)
    elif trade=="potter":
        for n_,x in enumerate((-1.35,-1.02,-0.69)):
            h=0.26+0.04*(n_%2)
            _cyl(k,(x,-0.5,z0+h/2),0.1,0.15,h,14,CLAY); _cyl(k,(x,-0.5,z0+h+0.05),0.065,0.055,0.1,12,CLAY)
            _cyl(k,(x,-0.5,z0+h+0.11),0.08,0.08,0.025,12,CLAY)
        for n_ in range(3): _cyl(k,(-0.15,-0.45,z0+0.04+n_*0.055),0.1,0.19,0.07,16,CLAY)
        for n_ in range(7): _cyl(k,(0.3,-0.5,z0+0.01+n_*0.018),0.17,0.17,0.016,18,CLAY)
        for n_,x in enumerate((0.85,1.3)): _cyl(k,(x,-0.45,z0+0.18),0.2,0.14,0.36,16,CLAY); _cyl(k,(x,-0.45,z0+0.38),0.11,0.12,0.05,14,CLAY)
        for n_ in range(8): _cyl(k,(-1.3+n_*0.37,0.62,shelf+0.05),0.045,0.055,0.1,10,CLAY)
        _cyl(k,(W_/2+0.5,-0.1,0.35),0.24,0.34,0.7,16,CLAY); _cyl(k,(W_/2+0.5,-0.1,0.78),0.15,0.19,0.16,14,CLAY)
        _cyl(k,(W_/2+0.55,0.6,0.22),0.2,0.26,0.44,16,CLAY)
        _stall_sack(k,-W_/2-0.45,-0.4,HAY,0.8)
        return
    elif trade=="draper":
        cols=(CLOTH_A,PINK,YELLOW,BURLAP,CLOTH_B,SHUTTER)
        for n_ in range(6):
            x=-1.2+(n_%3)*0.2; y=-0.62+(n_//3)*0.22
            _cyl(k,(-0.8,y,z0+0.1+(n_%3)*0.19),0.095,0.095,0.85,14,cols[n_],rot=Ry)
        for r_ in range(3):
            for n_ in range(3): k.box((0.35+r_*0.45,-0.45,z0+0.03+n_*0.06),(0.38,0.46,0.055),cols[(r_*2+n_)%6],bevel=0.012)
        for n_ in range(5):
            for m_ in range(2): k.box((-1.25+n_*0.62,0.62,shelf+0.03+m_*0.05),(0.42,0.34,0.05),cols[(n_+m_)%6],bevel=0.01)
        k.box((W_/2+0.55,0.0,0.3),(0.7,0.6,0.6),WOOD,bevel=0.03)
        for n_ in range(4): _cyl(k,(W_/2+0.38+(n_%2)*0.3,-0.12+(n_//2)*0.22,0.85),0.08,0.08,0.7,12,cols[n_+1])
        _stall_sack(k,-W_/2-0.45,-0.4,CLOTH_B)
        return
    elif trade=="cheese":
        for st,(x,y) in enumerate(((-1.15,-0.45),(-0.6,-0.5))):
            for n_ in range(3-st): goods_map(k,_cyl(k,(x,y,z0+0.065+n_*0.13),0.22,0.22,0.12,20,YELLOW),"cheese",caps=True)
        k.box((0.3,-0.45,z0+0.025),(0.8,0.55,0.045),WOOD,bevel=0.015)
        for n_ in range(4): goods_map(k,_cyl(k,(0.08+(n_%2)*0.4,-0.58+(n_//2)*0.26,z0+0.1),0.12,0.12,0.1,16,YELLOW),"cheese",caps=True)
        for n_ in range(3): goods_map(k,_cyl(k,(1.15,-0.45,z0+0.04+n_*0.075),0.26-n_*0.05,0.26-n_*0.05,0.07,20,YELLOW),"cheese",caps=True)
        for n_,x in enumerate((-1.2,-0.85,-0.5,0.5,0.85,1.2)):                                   # hanging sausages
            goods_map(k,_ico(k,(x,-(D_/2-0.1),2.13),1.0,HIDE,scale=(0.045,0.045,0.2)),"sausage")
            k.box((x,-(D_/2-0.1),2.4),(0.01,0.01,0.12),BURLAP,bevel=0)
        for n_ in range(6): goods_map(k,_cyl(k,(-1.3+n_*0.52,0.62,shelf+0.06),0.12,0.12,0.1,16,YELLOW),"cheese",caps=True)
    elif trade=="tinker":
        for n_,x in enumerate((-1.3,-0.95)): _cyl(k,(x,-0.5,z0+0.08),0.15,0.12,0.16,16,IRON); k.box((x,-0.5,z0+0.2),(0.3,0.02,0.02),IRON,bevel=0)
        for n_ in range(3):
            x=-0.5+n_*0.33; _cyl(k,(x,-0.55,z0+0.02),0.14,0.14,0.035,16,IRON); k.box((x,-0.28,z0+0.03),(0.04,0.3,0.025),IRON,bevel=0)
        for n_ in range(4):
            x=0.6+n_*0.22; k.box((x,-0.45,z0+0.02),(0.04,0.45,0.035),WOOD,bevel=0.005); k.box((x,-0.66,z0+0.04),(0.14,0.07,0.06),IRON,bevel=0.01)
        for n_ in range(4):
            vs=bmesh.ops.create_circle(k.bm,cap_ends=True,segments=12,radius=0.06)["verts"]
            for v in vs: v.co+=Vector((-1.3+n_*0.2,0.62,shelf+0.01))
            _mat(vs,IRON,False)
        for n_ in range(3): _cyl(k,(0.2+n_*0.45,0.62,shelf+0.1),0.13,0.11,0.2,14,BRONZE if n_==1 else IRON)
        k.box((W_/2+0.55,-0.2,0.3),(0.65,0.55,0.6),WOOD,bevel=0.03)
        k.box((W_/2+0.55,0.55,0.25),(0.6,0.5,0.5),WOOD,bevel=0.03)
        _cyl(k,(W_/2+0.55,-0.2,0.7),0.16,0.13,0.2,14,IRON)
        _stall_sack(k,-W_/2-0.45,-0.4,BURLAP)
        return
    _stall_barrels(k,W_)
    _stall_sack(k,-W_/2-0.45,-0.4)
def market_stall(k,goods="produce"):
    W_,D_=3.2,1.8
    for sx in(-1,1):
        for sy in(-1,1):
            h=2.6 if sy<0 else 3.0
            k.box((sx*(W_/2-0.1),sy*(D_/2-0.1),h/2),(0.2,0.2,h),WOOD,bevel=0.05,segs=2)
    # counter
    k.box((0,-0.35,0.95),(W_,1.0,0.14),WOOD,bevel=0.04)
    for i in range(6): k.box((-W_/2+0.27+i*0.53,-0.84,0.47),(0.5,0.08,0.9),WOOD,bevel=0.02)
    k.box((0,-0.35,0.12),(W_-0.2,0.9,0.1),WOOD,bevel=0.02)
    # back shelf & crossbeams
    k.box((0,D_/2-0.25,1.45),(W_-0.2,0.45,0.08),WOOD,bevel=0.02)
    for sy,h in((-1,2.6),(1,3.0)): k.box((0,sy*(D_/2-0.1),h-0.1),(W_+0.1,0.16,0.18),WOOD,bevel=0.03)
    # striped awning: sagging cloth sloping from back (3.1) to front (2.55) and over the front
    nx=12; ny=6; x0=-W_/2-0.25; x1=W_/2+0.25; y0=-D_/2-0.75; y1=D_/2+0.05
    grid=[]
    for i in range(nx+1):
        row=[]
        for j in range(ny+1):
            x=x0+(x1-x0)*i/nx; y=y0+(y1-y0)*j/ny
            z=2.65+(y-y0)/(y1-y0)*0.5 - 0.12*math.sin(math.pi*(i/nx*2%1 if False else (i%3)/3))*0 - 0.10*math.sin(math.pi*j/ny)
            z-=0.06*(0.5-0.5*math.cos(2*math.pi*i/(nx/2)))
            row.append(k.bm.verts.new((x,y,z)))
        grid.append(row)
    under=[[k.bm.verts.new(v.co+Vector((0,0,-0.015))) for v in row] for row in grid]
    for i in range(nx):
        mi=CLOTH_A if (i//2)%2==0 else CLOTH_B
        for j in range(ny):
            f=k.bm.faces.new((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1])); f.material_index=mi
            f2=k.bm.faces.new((under[i][j+1],under[i+1][j+1],under[i+1][j],under[i][j])); f2.material_index=mi
    # scalloped valance hanging from the front edge
    for i in range(nx):
        mi=CLOTH_A if (i//2)%2==0 else CLOTH_B
        a=grid[i][0].co; b=grid[i+1][0].co
        m=(a+b)/2+Vector((0,0,-0.42))
        va=[k.bm.verts.new(a),k.bm.verts.new(b),k.bm.verts.new(b+Vector((0,0,-0.28))),k.bm.verts.new(m),k.bm.verts.new(a+Vector((0,0,-0.28)))]
        f=k.bm.faces.new(va); f.material_index=mi
        vb=[k.bm.verts.new(v.co+Vector((0,0.015,0))) for v in va]
        f=k.bm.faces.new(vb[::-1]); f.material_index=mi
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index in (CLOTH_A,CLOTH_B):
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    trade=goods if isinstance(goods,str) else "produce"
    stall_wares(k,trade,W_,D_)
    # hanging price sign
    k.box((-W_/2+0.35,-D_/2-0.12,2.2),(0.7,0.06,0.4),WOOD,bevel=0.03)
    for sx in(-0.2,0.2): k.box((-W_/2+0.35+sx,-D_/2-0.12,2.45),(0.02,0.02,0.2),IRON,bevel=0)
    k.box((-W_/2+0.35,-D_/2-0.16,2.2),(0.35,0.02,0.15),STALL_SIGN.get(trade,YELLOW),bevel=0)
# ---------------- one call rebuilds the whole kit
def rebuild_all():
    P=vcol("VK_Pieces")
    specs=[("SM_VK_Wall_Stone",wall_stone_plain,{}),("SM_VK_Wall_Stone_Window",wall_stone_window,{}),("SM_VK_Wall_Stone_Door",wall_stone_door,{}),
           ("SM_VK_Corner_Stone",corner_stone,{"wobble":False}),
           ("SM_VK_Wall_Plaster",lambda k: plaster_ground(k,"."),{}),("SM_VK_Wall_Plaster_Window",lambda k: plaster_ground(k,"W"),{}),
           ("SM_VK_Wall_Plaster_Door",lambda k: plaster_ground(k,"D"),{}),("SM_VK_Corner_Plaster",corner_plaster,{"wobble":False}),
           ("SM_VK_Wall_Timber",timber_frame,{"grime":False}),("SM_VK_Wall_Timber_X",lambda k: timber_frame(k,False,"X"),{"grime":False}),
           ("SM_VK_Wall_Timber_K",lambda k: timber_frame(k,False,"K"),{"grime":False}),
           ("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),{"grime":False}),
           ("SM_VK_Corner_Timber",corner_timber,{"wobble":False,"grime":False}),
           ("SM_VK_Roof_Mid",roof_mid,{"wobble":False,"grime":False}),("SM_VK_Roof_Gable",roof_gable,{"wobble":False,"grime":False}),
           ("SM_VK_Roof_LCorner",roof_L_corner,{"wobble":False,"grime":False}),("SM_VK_Chimney",chimney,{"wobble":False,"grime":False}),
           ("SM_VK_Prop_FlowerBox",prop_flowerbox,{"wobble":False,"grime":False}),("SM_VK_Prop_Lantern",prop_lantern,{"wobble":False,"grime":False}),
           ("SM_VK_Prop_Sign",prop_sign,{"wobble":False,"grime":False}),("SM_VK_MarketStall",market_stall,{"wobble":False,"grime":True})]
    for n,fn,kw in specs:
        k=Kit(); fn(k); o=k.finish(n,P,**kw); o.hide_render=True; o.hide_viewport=True
    for n in list(bpy.data.objects):
        if n.name.endswith(("_Blue","_Green")) and n.name.startswith("SM_VK_Roof"): bpy.data.objects.remove(n)
    for me in list(bpy.data.meshes):
        if me.name.startswith("VAR_") and me.users==0: bpy.data.meshes.remove(me)
    _var_cache.clear()
    return [n for n,_,_ in specs]

def place_v(coll,piece,x,y,z,rot_deg,origin,style):
    o=place(coll,piece,x,y,z,rot_deg,origin)
    st={k_:v for k_,v in style.items() if k_ in SLOT}
    if st: o.data=variant_mesh(piece,st)
    return o
def random_style(seed):
    r=random.Random(seed)
    g=r.choices(["Stone","Plaster"],[0.6,0.4])[0]
    roofs=["Red","Blue","Green","Red"]+(["Thatch","Thatch"] if g=="Plaster" else ["Thatch"])
    return {"ground":g,
            "plaster":r.choice(["Cream","White","Ochre","Rose","Cream"]),
            "shutter":_maybe_worn(r,r.choice(["Teal","Red","Green","Blue","Natural"])),
            "roof":r.choice(roofs),"seed":seed}
def _maybe_worn(r,sh,p=0.2):
    """most houses keep fresh paint on their shutters; about one in five gets the chipped, weathered look"""
    return sh+"Worn" if sh!="Natural" and r.random()<p else sh
def _pieces(style):
    g=style.get("ground","Stone")
    gw={"D":f"SM_VK_Wall_{g}_Door","W":f"SM_VK_Wall_{g}_Window",".":f"SM_VK_Wall_{g}"}
    gc=f"SM_VK_Corner_{g}"
    return gw,gc
def _upper(r,c):
    if c=="W": return "SM_VK_Wall_Timber_Window"
    return r.choice(["SM_VK_Wall_Timber","SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K"])
def _dress(coll,origin,x,y,rot,c,r,style,z0=0):
    # props in wall-local coordinates, rotated with the wall
    a=math.radians(rot); ca,sa=math.cos(a),math.sin(a)
    def loc(lx,ly): return (x+lx*ca-ly*sa,y+lx*sa+ly*ca)
    if c=="W" and r.random()<0.7:
        px,py=loc(0,-0.55 if style.get("ground")=="Stone" else -0.5)
        fb="SM_VK_Prop_FlowerBox" if r.random()<0.6 else "SM_VK_Prop_FlowerBox_Daisy"
        place_v(coll,fb,px,py,0.78 if style.get("ground")=="Stone" else 0.9,rot,origin,{})
    if r.random()<0.4: place_v(coll,"SM_VK_Deco_Weeds",x,y,0,rot,origin,{})
    if c=="." and r.random()<0.22: place_v(coll,"SM_VK_Deco_Ivy_A" if r.random()<0.5 else "SM_VK_Deco_Ivy_B",x,y,0,rot,origin,{})
    if c=="D" and r.random()<0.5:
        for sx in ((-1.05,1.05) if r.random()<0.5 else (1.05,)):
            px,py=loc(sx,-0.75); place_v(coll,"SM_VK_Prop_Planter",px,py,0,rot,origin,{})
    if c=="D":
        if r.random()<0.45: place_v(coll,"SM_VK_Porch",x,y,0,rot,origin,style)
        else:
            px,py=loc(1.0,-0.3); place_v(coll,"SM_VK_Prop_Lantern",px,py,2.55,rot,origin,{})
def build_house_v(coll,origin,n,stories,style,front=None,back=None,chimney=True):
    r=random.Random(style["seed"]); gw,gc=_pieces(style); L=n*CELL
    front=front or "".join(r.choice("WW.") for _ in range(n))
    if "D" not in front: i=r.randrange(n); front=front[:i]+"D"+front[i+1:]
    back=back or "".join(r.choice("W..") for _ in range(n))
    walls=[(-L/2+1.5+3*i,-3,0,front[i]) for i in range(n)]+[(-L/2+1.5+3*i,3,180,back[::-1][i]) for i in range(n)]
    walls+=[(-L/2,-1.5,-90,r.choice("W.")),(-L/2,1.5,-90,"."),(L/2,1.5,90,r.choice("W.")),(L/2,-1.5,90,".")]
    corners=[(-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)]
    _assemble(coll,origin,walls,corners,stories,style,r)
    top=roof_top(stories); sfx=""
    thatch=style.get("roof")=="Thatch"
    hip_p=0.55 if thatch else 0.3
    ends=[r.random()<hip_p for _ in range(2)]
    for i in range(n):
        x=-L/2+1.5+3*i
        is_end=i in (0,n-1); hip=is_end and ends[0 if i==0 else 1]
        if thatch: pc=("SM_VK_RoofThatch_Hip" if hip else "SM_VK_RoofThatch_Gable") if is_end else "SM_VK_RoofThatch_Mid"
        else: pc=("SM_VK_Roof_Hip" if hip else "SM_VK_Roof_Gable") if is_end else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)
    ci=r.randrange(n); crot=r.choice((0,180))
    if chimney:
        place_v(coll,"SM_VK_Chimney",-L/2+1.5+3*ci,0,top,crot,origin,style)
    if (stories==1 or r.random()<0.6) and not thatch:
        for i in range(n):
            if i==ci and chimney: continue
            if (i==0 and ends[0]) or (i==n-1 and ends[1]): continue
            if r.random()<(0.55 if stories==1 else 0.35):
                place_v(coll,"SM_VK_Roof_Dormer",-L/2+1.5+3*i,0,top,0,origin,style)
def _assemble(coll,origin,walls,corners,stories,style,r):
    gw,gc=_pieces(style)
    for (x,y,rot,c) in walls:
        place_v(coll,gw[c],x,y,0,rot,origin,style); _dress(coll,origin,x,y,rot,c,r,style)
    for (x,y,rot) in corners: place_v(coll,gc,x,y,0,rot,origin,style)
    if stories==2:
        for (x,y,rot,c) in walls:
            uc="W" if (c in "WD" or r.random()<0.35) else "."
            place_v(coll,_upper(r,uc),x,y,H1,rot,origin,style)
        for (x,y,rot) in corners: place_v(coll,"SM_VK_Corner_Timber",x,y,H1,rot,origin,style)
def build_L_v(coll,origin,a,b,stories,style):
    if style.get("roof")=="Thatch": style=dict(style,roof="Red")
    r=random.Random(style["seed"]); XA=3+3*a; YB=3+3*b
    fa="".join(r.choice("WW.") for _ in range(2+a)); fa=fa[:1]+"D"+fa[2:]
    walls=[(-1.5+3*i,-3,0,fa[i]) for i in range(2+a)]
    walls+=[(-3,-1.5+3*j,-90,r.choice("W.")) for j in range(2+b)]
    walls+=[(XA,-1.5,90,r.choice("W.")),(XA,1.5,90,".")]
    walls+=[(4.5+3*i,3,180,r.choice("W.")) for i in range(a)]
    walls+=[(-1.5,YB,180,"."),(1.5,YB,180,r.choice("W."))]
    walls+=[(3,4.5+3*j,90,r.choice("WD")) for j in range(b)]
    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    _assemble(coll,origin,walls,corners,stories,style,r)
    g=style.get("ground","Stone")
    place_v(coll,f"SM_VK_InnerCorner_{g}",3,3,0,0,origin,style)
    for lvl in range(1,stories): place_v(coll,"SM_VK_InnerCorner_Timber",3,3,H1+H2*(lvl-1),0,origin,style)
    top=roof_top(stories)
    place_v(coll,"SM_VK_Roof_LCorner",0,0,top,0,origin,style)
    for i in range(a): place_v(coll,"SM_VK_Roof_Gable" if i==a-1 else "SM_VK_Roof_Mid",4.5+3*i,0,top,0,origin,style)
    for j in range(b): place_v(coll,"SM_VK_Roof_Gable" if j==b-1 else "SM_VK_Roof_Mid",0,4.5+3*j,top,90,origin,style)
    place_v(coll,"SM_VK_Chimney",4.5+3*r.randrange(a),0,top,r.choice((0,180)),origin,style)

# ---------------- inner (concave) corners: concave quadrant is local +X +Y
def inner_corner_stone(k):
    rnd=random.Random(8); z=0.4; i=0
    k.box((0.32,0.32,0.2),(0.3,0.3,0.4),STONE,bevel=0.04)
    while z<H1-0.05:
        h=min(rnd.uniform(0.38,0.5),H1-z)
        if i%2==0: k.box((0.55,0.3,z+h/2),(0.6,0.14,h-0.03),STONE,bevel=0.05,segs=2,jitter=0.01,seed=i)
        else:      k.box((0.3,0.55,z+h/2),(0.14,0.6,h-0.03),STONE,bevel=0.05,segs=2,jitter=0.01,seed=i)
        z+=h; i+=1
def inner_corner_plaster(k):
    k.box((0.35,0.35,PL/2),(0.3,0.3,PL),STONE,bevel=0.04)
    k.box((0.28,0.28,(PL+H1)/2),(0.24,0.24,H1-PL),WOOD,bevel=0.04)
def inner_corner_timber(k):
    k.box((0.44,0.44,H2/2),(0.26,0.26,H2),WOOD,bevel=0.05,segs=2)
    k.box((0.3,0.3,0.15),(0.4,0.4,0.3),WOOD,bevel=0.04)
# ---------------- dormer: sits on a Roof_Mid, front slope (-Y)
def dormer(k):
    zr=lambda ay: roof_z(ay)
    yf=-2.35; hw=0.85
    # cheek walls + front wall (plaster, timber framed)
    k.box((0,(yf-0.4)/2,1.8),(2*hw,-(yf)-0.4+0.0,1.6),PLASTER,bevel=0)   # body y yf..-0.4
    zb=zr(-yf)-0.15; zt=2.75
    k.quad([(-hw+0.2,yf-0.02,zb+0.3),(hw-0.2,yf-0.02,zb+0.3),(hw-0.2,yf-0.02,zt-0.25),(-hw+0.2,yf-0.02,zt-0.25)],WINDOW,
           uvs=[(0,0),(1.3,0),(1.3,1.1),(0,1.1)])
    for sx in(-1,1): k.box((sx*(hw-0.1),yf-0.06,(zb+zt)/2),(0.2,0.2,zt-zb+0.1),WOOD,bevel=0.035)
    k.box((0,yf-0.06,zb+0.2),(2*hw,0.22,0.18),WOOD,bevel=0.03)
    k.box((0,yf-0.08,zt-0.12),(2*hw+0.1,0.24,0.2),WOOD,bevel=0.03)
    k.box((0,yf-0.1,(zb+zt)/2+0.15),(0.07,0.05,zt-zb-0.5),WOOD,bevel=0.01)
    # small gable roof along Y
    rp=math.radians(45); run=hw+0.3; rise=run*math.tan(rp)*0.8
    zr0=zt+0.02
    for sx in(-1,1):
        L=math.hypot(run,rise); ang=math.atan2(rise,run)
        k.box((sx*run/2,(yf-0.35-0.2)/2-0.4,zr0+rise/2),(L+0.1,-yf+0.45,0.16),ROOF,rot=(0,sx*ang,0),bevel=0.04)
    # gable triangle
    vs=[k.bm.verts.new(p) for p in ((-run+0.15,yf-0.05,zr0),(run-0.15,yf-0.05,zr0),(0,yf-0.05,zr0+rise-0.1))]
    f=k.bm.faces.new(vs[::-1]); f.material_index=PLASTER; k.bm.normal_update(); k.project([f],PLASTER)
    k.box((0,yf-0.4,zr0+rise*0.45),(0.12,0.12,rise*0.8),WOOD,bevel=0.02)
    for sx in(-1,1):
        L=math.hypot(run,rise); ang=math.atan2(rise,run)
        k.box((sx*run/2,yf-0.44,zr0+rise/2-0.05),(L+0.12,0.12,0.24),WOOD,rot=(0,sx*ang,0),bevel=0.03)
    k.box((0,yf-0.47,zr0+rise+0.08),(0.14,0.14,0.45),WOOD,bevel=0.04)
# ---------------- porch canopy over a door (wall-local, outer side -Y)
def porch(k):
    W_=2.6; yo=-1.75; zh=2.95; zl=2.35
    for sx in(-1,1):
        k.box((sx*(W_/2-0.2),yo+0.1,zl/2),(0.2,0.2,zl),WOOD,bevel=0.04,segs=2)
        k.box((sx*(W_/2-0.2),yo+0.1,0.06),(0.34,0.34,0.12),STONE,bevel=0.03)
        # knee braces
        k.box((sx*(W_/2-0.45),yo+0.1,zl-0.3),(0.5,0.14,0.13),WOOD,rot=(0,sx*0.7,0),bevel=0.02)
        L=math.hypot(-yo,zh-zl); ang=math.atan2(zh-zl,-yo)
        k.box((sx*(W_/2-0.2),yo/2,(zh+zl)/2+0.02),(0.16,L,0.2),WOOD,rot=(ang,0,0),bevel=0.03)
    k.box((0,yo+0.1,zl+0.05),(W_,0.2,0.22),WOOD,bevel=0.04)
    L=math.hypot(-yo+0.5,zh-zl+0.25); ang=math.atan2(zh-zl+0.25,-yo+0.5)
    k.box((0,(yo-0.5)/2,(zh+zl)/2+0.2),(W_+0.5,L,0.14),ROOF,rot=(ang,0,0),bevel=0.04)
    # step
    k.box((0,-0.75,0.1),(1.9,0.9,0.2),STONE,bevel=0.05,segs=2,jitter=0.02,seed=9)

def _cyl(k,center,r1,r2,depth,segs,mi,rot=None):
    vs=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=segs,radius1=r1,radius2=r2,depth=depth)["verts"]
    M=Matrix.Translation(Vector(center))@(rot or Matrix.Identity(4))
    bmesh.ops.transform(k.bm,matrix=M,verts=vs)
    fs=list({f for v in vs for f in v.link_faces}); k.bm.normal_update(); k.project(fs,mi); return vs
def prop_well(k):
    rnd=random.Random(2); R=1.05
    n=14
    for layer in range(3):
        for i in range(n):
            a=2*math.pi*(i+0.5*(layer%2))/n
            k.box((math.cos(a)*R,math.sin(a)*R,0.2+layer*0.3),(0.42,2*math.pi*R/n+0.04,0.3),STONE,rot=(0,0,a),bevel=0.05,segs=2,jitter=0.015,seed=layer*20+i)
    for i in range(n):
        a=2*math.pi*i/n
        k.box((math.cos(a)*R,math.sin(a)*R,0.98),(0.52,2*math.pi*R/n+0.06,0.14),STONE,rot=(0,0,a),bevel=0.04)
    _cyl(k,(0,0,0.5),0.86,0.86,0.01,16,WATER)                                  # water: a disc inside the ring
    # frame: posts standing on the rim cap (top 1.05), a tie beam on the post tops, knee braces post -> beam
    zp0,zp1=1.05,2.75; zt=zp1+0.16
    for sx in(-1,1):
        k.box((sx*1.15,0,(zp0+zp1)/2),(0.2,0.2,zp1-zp0),WOOD,bevel=0.05,segs=2)
        a=(sx*1.05,2.25); b=(sx*0.62,zp1); dx,dz=b[0]-a[0],b[1]-a[1]
        k.box(((a[0]+b[0])/2,0,(a[1]+b[1])/2),(math.hypot(dx,dz)+0.06,0.12,0.12),WOOD,rot=(0,math.atan2(-dz,dx),0),bevel=0.02)
    k.box((0,0,(zp1+zt)/2),(2.7,0.16,0.16),WOOD,bevel=0.03)                     # tie beam
    # windlass: axle between the posts, iron pins through them, crank on +X
    _cyl(k,(0,0,1.85),0.14,0.14,2.1,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(0,0,1.85),0.035,0.035,2.76,6,IRON,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((1.36,0,1.72),(0.06,0.06,0.32),IRON,bevel=0); k.box((1.36,0.14,1.59),(0.06,0.34,0.06),IRON,bevel=0)
    k.box((0,0,1.3),(0.02,0.02,1.0),IRON,bevel=0)                               # rope
    _cyl(k,(0.0,0,0.78),0.18,0.22,0.3,10,WOOD)                                  # bucket
    # roof: two slopes (38 deg) whose underside clears the tie beam's ends, ridge beam on a king post
    t=math.tan(math.radians(38)); zu=lambda x: zt+0.02+(1.35-x)*t
    x0,x1=0.02,1.65; d=Vector((x1-x0,0,zu(x1)-zu(x0))); L=d.length; d.normalize(); nrm=Vector((-d.z,0,d.x))
    for sx in(-1,1):
        c=Vector(((x0+x1)/2,0,(zu(x0)+zu(x1))/2))+nrm*0.05
        k.box((sx*c.x,0,c.z),(L,2.0,0.1),ROOF,rot=(0,sx*math.atan2(-d.z,d.x),0),bevel=0.03)
    zr=zu(x0)+0.02
    k.box((0,0,zr),(0.2,2.1,0.2),WOOD,bevel=0.04)                               # ridge beam
    k.box((0,0,(zt+zr-0.1)/2),(0.14,0.14,zr-0.1-zt),WOOD,bevel=0.02)            # king post
def prop_fence(k,length=3.0):
    rnd=random.Random(int(length*7))
    for x in(-length/2,length/2):
        k.box((x,0,0.55),(0.17,0.17,1.1),WOOD,rot=(0,0,rnd.uniform(-.2,.2)),bevel=0.04,segs=2)
        k.box((x,0,1.13),(0.12,0.12,0.1),WOOD,rot=(0,0,0.785),bevel=0.03)
    for z in(0.35,0.8):
        k.box((0,0.1,z+rnd.uniform(-.04,.04)),(length+0.1,0.07,0.12),WOOD,rot=(0,rnd.uniform(-.03,.03),0),bevel=0.02)
    n=int(length/0.3)
    for i in range(n):
        x=-length/2+0.2+i*(length-0.4)/(n-1); h=rnd.uniform(0.85,1.0)
        vs=k.box((x,0.17,h/2),(0.11,0.04,h),WOOD,rot=(0,rnd.uniform(-.05,.05),0),bevel=0.015)
def prop_fence_gate(k):
    for x in(-1.5,1.5): k.box((x,0,0.65),(0.2,0.2,1.3),WOOD,bevel=0.05,segs=2)
    for s in(-1,1):
        x0=s*1.4; 
        for z in(0.3,0.85): k.box((s*0.75,0.12,z),(1.3,0.06,0.12),WOOD,bevel=0.02)
        for i in range(4): k.box((s*(0.25+i*0.36),0.16,0.55),(0.11,0.04,0.95),WOOD,bevel=0.015)
        k.box((s*0.75,0.14,0.57),(1.35,0.05,0.1),WOOD,rot=(0,-s*0.38,0),bevel=0.015)
def prop_cart(k):
    k.box((0,0,0.85),(2.0,1.2,0.1),WOOD,bevel=0.03)
    for sy in(-1,1): k.box((0,sy*0.6,1.1),(2.0,0.08,0.45),WOOD,bevel=0.02)
    for sx in(-1,1): k.box((sx*1.0,0,1.1),(0.08,1.2,0.45),WOOD,bevel=0.02)
    for sy in(-1,1): k.box((1.5,sy*0.45,0.72),(1.6,0.09,0.09),WOOD,rot=(0,0.35,0),bevel=0.02)
    for sy in(-1,1):
        _cyl(k,(-0.15,sy*0.75,0.55),0.55,0.55,0.1,14,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
        _cyl(k,(-0.15,sy*0.81,0.55),0.12,0.12,0.12,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
        for i in range(6):
            k.box((-0.15,sy*0.75,0.55),(0.06,0.05,1.0),WOOD,rot=(0,i*math.pi/6,0),bevel=0)
    _cyl(k,(-0.15,0,0.55),0.06,0.06,1.6,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    # cargo
    for i,(x,y) in enumerate(((-0.5,-0.25),(-0.5,0.25),(0.15,0))):
        vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.3)["verts"]
        for v in vs: v.co=Vector((v.co.x*1.1,v.co.y*0.9,v.co.z*0.8))+Vector((x,y,1.18))
        for f in {f for v in vs for f in v.link_faces}: f.material_index=BURLAP
    k.box((0.6,0,1.12),(0.5,0.5,0.45),WOOD,bevel=0.03)
def prop_lamppost(k):
    k.box((0,0,0.12),(0.45,0.45,0.24),STONE,bevel=0.05,segs=2)
    k.box((0,0,1.5),(0.16,0.16,2.8),WOOD,bevel=0.04)
    k.box((0,-0.3,2.75),(0.1,0.7,0.1),WOOD,bevel=0.02)
    k.box((0,-0.2,2.5),(0.08,0.45,0.08),WOOD,rot=(0.75,0,0),bevel=0.015)
    sub=Kit(); prop_lantern(sub)
    merge_kit(k,sub,Matrix.Translation((0,-0.25,2.72)))
def prop_bench(k):
    k.box((0,0,0.48),(1.8,0.45,0.1),WOOD,bevel=0.03)
    for sx in(-0.7,0.7):
        for sy in(-0.15,0.15): k.box((sx,sy,0.22),(0.1,0.1,0.45),WOOD,rot=(sy*0.8,0,0),bevel=0.02)
    k.box((0,0.2,0.85),(1.8,0.07,0.28),WOOD,rot=(-0.2,0,0),bevel=0.02)
    for sx in(-0.7,0.7): k.box((sx,0.22,0.65),(0.08,0.07,0.4),WOOD,bevel=0.02)
def prop_crates(k):
    rnd=random.Random(6)
    for (x,y,z,s) in((0,0,0,0.8),(0.85,0.1,0,0.75),(0.4,0.05,0.8,0.7),(-0.1,0.85,0,0.7)):
        r=rnd.uniform(-.2,.2)
        k.box((x,y,z+s/2),(s,s,s),WOOD,rot=(0,0,r),bevel=0.04)
        for dz in(0.07,s-0.07): k.box((x,y,z+dz),(s+0.04,s+0.04,0.1),WOOD,rot=(0,0,r),bevel=0.02)
    for i,(x,y) in enumerate(((1.4,0.9),(1.6,0.2))):
        for zz,(r0,r1) in((0.25,(0.34,0.4)),(0.75,(0.4,0.34))): _cyl(k,(x,y,zz),r0,r1,0.5,12,WOOD)
        for zz in(0.12,0.88): _cyl(k,(x,y,zz),0.39,0.39,0.06,12,IRON)

def road_strip(coll,name,pts,w=3.2):
    bm=bmesh.new(); prev=None
    L=[]
    for i,p in enumerate(pts):
        a=Vector(pts[max(i-1,0)]); b=Vector(pts[min(i+1,len(pts)-1)]); d=(b-a).normalized(); n=Vector((-d.y,d.x))
        p=Vector(p); L.append((bm.verts.new((*(p+n*w),0.02)),bm.verts.new((*(p-n*w),0.02))))
    for i in range(len(L)-1): bm.faces.new((L[i][1],L[i+1][1],L[i+1][0],L[i][0]))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); coll.objects.link(o); me.materials.append(bpy.data.materials["MC_WK_Dirt"]); return o
def fence_run(coll,a,b,origin=(0,0,0),gate_at=None):
    a=Vector(a); b=Vector(b); L=(b-a).length; n=max(1,round(L/3)); d=(b-a)/n
    rot=math.degrees(math.atan2(d.y,d.x))
    for i in range(n):
        c=a+d*(i+0.5)
        place_v(coll,"SM_VK_Prop_FenceGate" if gate_at==i else "SM_VK_Prop_Fence",c.x,c.y,0,rot,origin,{})
def street(coll,x0,x1,yroad,seed,side_gap=9.5):
    r=random.Random(seed); placed=[]
    for side in(1,-1):
        x=x0+r.uniform(0,3)
        while True:
            kind=r.choices(["S","L"],[0.8,0.2])[0]
            n=r.choice([2,2,3,3,4]) if kind=="S" else 0
            length=n*CELL if kind=="S" else 12
            if x+length>x1: break
            st=random_style(seed*100+len(placed)+(0 if side>0 else 50))
            cx=x+length/2
            y=yroad+side*side_gap
            rot=0 if side>0 else 180
            org=(cx,y,math.radians(rot))
            if kind=="S": build_house_v(coll,org,n,r.choice([1,2,2]),st)
            else:
                # L house: junction at origin; place so front (wing A, -Y local) faces the road
                ox=x+3; org=(ox if side>0 else x+length-3,y,math.radians(rot)); build_L_v(coll,org,1,1,2,st)
            # garden behind
            if r.random()<0.7:
                gy0=y+side*3.8; gy1=y+side*(3.8+r.choice([6,9]))
                xa=x-0.3; xb=x+length+0.3
                fence_run(coll,(xa,gy1),(xb,gy1)); fence_run(coll,(xa,gy0),(xa,gy1)); fence_run(coll,(xb,gy0),(xb,gy1),gate_at=0)
                gardens.append((xa,min(gy0,gy1),xb,max(gy0,gy1)))
            # street props in front
            px=x+r.uniform(0.5,length-0.5); py=yroad+side*5.2
            pk=r.choice(["SM_VK_Prop_LampPost","SM_VK_Prop_Bench","SM_VK_Prop_Crates","SM_VK_Prop_Cart",None,"SM_VK_Prop_LampPost"])
            if pk: place_v(coll,pk,px,py,0,rot+(0 if pk!="SM_VK_Prop_Cart" else r.uniform(-30,30)),(0,0,0),{})
            placed.append((x,length)); x+=length+r.uniform(2.5,5)
gardens=[]

def prop_garden_bed(k):
    rnd=random.Random(3)
    k.box((0,0,0.1),(2.8,1.6,0.2),WOOD,bevel=0.03)
    soil=tex_mat("M_VK_Soil",None,1.0,flat=(0.20,0.13,0.08))
    k.box((0,0,0.2),(2.6,1.4,0.06),SOIL,bevel=0)
    for row in range(3):
        for i in range(6):
            x=-1.05+i*0.42+rnd.uniform(-.04,.04); y=-0.45+row*0.45
            vs=bmesh.ops.create_icosphere(k.bm,subdivisions=1,radius=0.17)["verts"]
            for v in vs:
                d=v.co.normalized(); v.co=Vector((v.co.x,v.co.y,v.co.z*0.75))*(1+0.18*noise.noise(d*3+Vector((x,y,0))))+Vector((x,y,0.33))
            for f in {f for v in vs for f in v.link_faces}: f.material_index=LEAF

def _ico(k,c,r,mi,scale=(1,1,1),sub=2,jit=0.0,seed=0):
    rnd=random.Random(seed)
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=sub,radius=r)["verts"]
    for v in vs:
        v.co=Vector((v.co.x*scale[0],v.co.y*scale[1],v.co.z*scale[2]))
        if jit: v.co+=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1)))*jit
        v.co+=Vector(c)
    for f in {f for v in vs for f in v.link_faces}: f.material_index=mi
    return vs
def barrel(k,x,y,z=0,r=0.4,h=1.0,lying=False):
    M=Matrix.Translation((x,y,z))@(Matrix.Rotation(math.pi/2,4,"X") if lying else Matrix.Identity(4))
    sub=Kit()
    for zz,(r0,r1) in((h*0.25,(r*0.86,r)),(h*0.75,(r,r*0.86))): _cyl(sub,(0,0,zz-(h/2 if lying else 0)),r0,r1,h/2,12,WOOD)
    for zz in(h*0.1,h*0.9): _cyl(sub,(0,0,zz-(h/2 if lying else 0)),r*0.9,r*0.9,0.06,12,IRON)
    merge_kit(k,sub,M)
def prop_table(k):
    k.box((0,0,0.78),(2.0,0.95,0.1),WOOD,bevel=0.03)
    for sx in(-0.8,0.8):
        k.box((sx,0,0.38),(0.12,0.75,0.1),WOOD,bevel=0.02)
        for sy in(-1,1): k.box((sx,sy*0.28,0.38),(0.1,0.1,0.8),WOOD,rot=(sy*0.35,0,0),bevel=0.02)
    k.box((0,0,0.35),(1.7,0.08,0.08),WOOD,bevel=0.01)
    rnd=random.Random(1)
    for i,(x,y) in enumerate(((-0.6,-0.2),(0.1,0.25),(0.7,-0.15))):   # tankards
        _cyl(k,(x,y,0.95),0.08,0.08,0.24,8,WOOD); _cyl(k,(x,y,1.07),0.075,0.075,0.02,8,HAY)
        k.box((x+0.1,y,0.95),(0.05,0.03,0.14),WOOD,bevel=0)
    _cyl(k,(-0.1,-0.15,0.85),0.2,0.2,0.04,12,WOOD); _ico(k,(-0.1,-0.15,0.92),0.12,BREAD,(1.3,0.9,0.6))
def prop_stool(k):
    _cyl(k,(0,0,0.5),0.25,0.25,0.08,10,WOOD)
    for i in range(3):
        a=i*2.094; k.box((math.cos(a)*0.14,math.sin(a)*0.14,0.24),(0.07,0.07,0.5),WOOD,rot=(math.sin(a)*0.2,-math.cos(a)*0.2,0),bevel=0.01)
def prop_trough(k):
    k.box((0,0,0.1),(2.0,0.8,0.2),WOOD,bevel=0.03)
    for sy in(-1,1): k.box((0,sy*0.36,0.4),(2.0,0.1,0.6),WOOD,bevel=0.03)
    for sx in(-1,1): k.box((sx*0.96,0,0.4),(0.1,0.8,0.6),WOOD,bevel=0.03)
    k.quad([(-0.9,-0.3,0.55),(0.9,-0.3,0.55),(0.9,0.3,0.55),(-0.9,0.3,0.55)],WATER,uvs=[(0,0),(1.8,0),(1.8,0.6),(0,0.6)])
    for sx in(-0.7,0.7): k.box((sx,0,0.4),(0.08,0.9,0.66),IRON,bevel=0)
def prop_haybale(k):
    k.box((0,0,0.35),(1.3,0.8,0.7),HAY,bevel=0.12,segs=3,jitter=0.03,seed=2)
    for sx in(-0.35,0.35): k.box((sx,0,0.35),(0.05,0.84,0.74),WOOD,bevel=0.02)
    k.box((0.3,0.1,0.95),(1.2,0.75,0.6),HAY,rot=(0,0,0.4),bevel=0.1,segs=3,jitter=0.03,seed=3)
def prop_haystack(k):
    rnd=random.Random(4)
    vs=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=16,radius1=1.35,radius2=1.25,depth=1.1)["verts"]
    for v in vs: v.co+=Vector((0,0,0.55))
    vs2=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=16,radius1=1.42,radius2=0.12,depth=1.9)["verts"]
    for v in vs2: v.co+=Vector((0,0,1.1+0.95))
    for v in vs+vs2:
        d=Vector((v.co.x,v.co.y,0))
        if d.length>0.2: v.co+=d.normalized()*noise.noise(v.co*1.3)*0.12
    fs=list({f for v in vs+vs2 for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=HAY
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(math.atan2(p.y,p.x)*1.4/TILE[HAY],p.z/TILE[HAY])
    for i in range(3):   # binding ropes
        _cyl(k,(0,0,1.25+i*0.45),1.36-i*0.32,1.36-i*0.32,0.06,16,WOOD)
    _cyl(k,(0,0,3.2),0.05,0.05,0.9,6,WOOD)
def prop_woodpile(k):
    rnd=random.Random(5)
    for row in range(4):
        for i in range(7-row):
            x=-1.1+i*0.34+row*0.17; z=0.17+row*0.3
            _cyl(k,(x,0,z),0.16,0.16,1.0,7,BREAD if (i+row)%3==0 else WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for sx in(-1.35,1.35): k.box((sx,0,0.6),(0.12,0.12,1.3),WOOD,bevel=0.03)
    k.box((0,0,1.35),(3.0,1.3,0.08),ROOF,rot=(0.12,0,0),bevel=0.02)
    for sx in(-1.35,1.35):
        for sy in(-0.5,0.5): k.box((sx,sy,0.7),(0.1,0.1,1.35),WOOD,bevel=0.02)
    _cyl(k,(1.9,0.3,0.25),0.3,0.32,0.5,10,WOOD); k.box((1.95,0.3,0.7),(0.05,0.05,0.5),WOOD,rot=(0,0.3,0),bevel=0)
    k.box((2.0,0.3,0.92),(0.05,0.22,0.12),STEEL,bevel=0)
def prop_noticeboard(k):
    for sx in(-0.8,0.8): k.box((sx,0,1.1),(0.14,0.14,2.2),WOOD,bevel=0.04)
    k.box((0,0,1.5),(1.5,0.08,1.0),WOOD,bevel=0.03)
    rnd=random.Random(6)
    for i in range(5):
        k.box((-0.5+i*0.25+rnd.uniform(-.05,.05),-0.05,1.5+rnd.uniform(-.25,.25)),(0.22,0.02,0.3),PAPER,rot=(0,rnd.uniform(-.2,.2),0),bevel=0)
    for sx in(-1,1): k.box((sx*0.5,0,2.35),(1.2,0.9,0.07),ROOF,rot=(0,sx*0.45,0),bevel=0.02)
def prop_signpost(k):
    k.box((0,0,1.4),(0.16,0.16,2.8),WOOD,bevel=0.04)
    k.box((0,0,0.1),(0.4,0.4,0.2),STONE,bevel=0.05)
    for i,(a,z) in enumerate(((0.3,2.4),(2.2,2.05),(4.0,1.7))):
        R=Matrix.Rotation(a,4,"Z")
        sub=Kit(); sub.box((0.55,0,0),(0.95,0.06,0.24),WOOD,bevel=0.03)
        v=[sub.bm.verts.new(p) for p in ((1.02,-0.03,-0.12),(1.02,-0.03,0.12),(1.2,-0.03,0))]; f=sub.bm.faces.new(v); f.material_index=WOOD
        merge_kit(k,sub,Matrix.Translation((0,0,z))@R)
def prop_anvil(k):
    _cyl(k,(0,0,0.3),0.32,0.36,0.6,10,WOOD)
    k.box((0,0,0.72),(0.35,0.22,0.24),STEEL,bevel=0.03)
    k.box((0,0,0.9),(0.6,0.26,0.14),STEEL,bevel=0.03)
    _cyl(k,(0.42,0,0.9),0.1,0.01,0.3,8,STEEL,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((0.05,0.05,1.0),(0.05,0.3,0.05),WOOD,bevel=0); k.box((0.05,-0.12,1.02),(0.12,0.08,0.08),IRON,bevel=0.01)
def prop_grindstone(k):
    for sx in(-0.3,0.3): k.box((sx,0,0.45),(0.1,0.1,0.9),WOOD,bevel=0.02)
    k.box((0,0,0.2),(0.8,0.1,0.1),WOOD,bevel=0.01)
    _cyl(k,(0,0,0.9),0.42,0.42,0.14,16,STONE,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(0,0,0.9),0.04,0.04,0.9,6,IRON,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((0.48,0,0.8),(0.04,0.04,0.25),IRON,bevel=0)
def prop_sacks(k):
    rnd=random.Random(7)
    for i,(x,y,z) in enumerate(((0,0,0),(0.55,0.1,0),(0.25,0.5,0),(0.3,0.2,0.55))):
        _ico(k,(x,y,z+0.32),0.3,BURLAP,(1,0.85,1.1),jit=0.02,seed=i)
        _cyl(k,(x,y,z+0.66),0.08,0.12,0.1,6,BURLAP)
def prop_weaponrack(k):
    for sx in(-0.7,0.7): k.box((sx,0,0.8),(0.12,0.3,1.6),WOOD,bevel=0.03)
    k.box((0,0,0.35),(1.5,0.3,0.08),WOOD,bevel=0.02); k.box((0,0.05,1.4),(1.5,0.1,0.1),WOOD,bevel=0.02)
    for i in range(4):
        x=-0.5+i*0.33
        k.box((x,0.05,1.0),(0.04,0.04,1.8),WOOD,rot=(0.12,0,0),bevel=0)
        if i%2: _cyl(k,(x,0.2,1.95),0.05,0,0.25,4,STEEL)
        else:   k.box((x,0.18,1.75),(0.02,0.28,0.2),STEEL,bevel=0)
    _cyl(k,(0,-0.25,0.7),0.4,0.4,0.06,12,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X")@Matrix.Rotation(0,4,"Z"))
    _cyl(k,(0,-0.29,0.7),0.12,0.12,0.06,8,STEEL,rot=Matrix.Rotation(math.pi/2,4,"X"))
def prop_barrelstack(k):
    """two barrels lying on a pair of rails (across their axes, wedged at the ends), a third in the groove on top"""
    zb=0.12+0.366                         # the barrels touch the rails at y +-0.3, where their radius is 0.366
    zt=zb+math.sqrt(0.8**2-0.45**2)       # the top barrel rests on both bulges (0.8 between centres)
    for x in (-0.45,0.45): barrel(k,x,0,zb,0.4,1.0,lying=True)
    barrel(k,0,0,zt,0.4,1.0,lying=True)
    for sy in (-0.3,0.3):
        k.box((0,sy,0.06),(1.9,0.14,0.12),WOOD,bevel=0.02)
        for sx in (-1,1): k.box((sx*0.86,sy,0.17),(0.16,0.14,0.12),WOOD,rot=(0,sx*0.35,0),bevel=0.015)   # wedges
    _cyl(k,(0,-0.53,zt),0.05,0.05,0.08,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
def prop_bellows_forge(k):   # standalone open forge hearth
    k.box((0,0,0.45),(1.6,1.2,0.9),STONE,bevel=0.05,segs=2)
    k.box((0,0,0.92),(1.2,0.8,0.06),GLOW,bevel=0.02)
    for i in range(6): _ico(k,(-0.4+i*0.16,0.05*(-1)**i,0.97),0.08,IRON if i%2 else GLOW,sub=0)
    k.box((0,0.45,1.9),(1.2,0.3,1.8),STONE,bevel=0.05,segs=2)
    k.box((0,0.2,1.3),(1.5,0.8,0.12),STONE,rot=(0.3,0,0),bevel=0.03)
    k.box((1.15,0,0.7),(0.7,0.5,0.25),CLOTH_B,rot=(0,0.2,0),bevel=0.08,segs=2)
    k.box((1.5,0,0.72),(0.35,0.4,0.05),WOOD,rot=(0,0.2,0),bevel=0.01)
    k.box((0.85,0,0.7),(0.12,0.12,0.3),WOOD,bevel=0.02)

def rebuild(n,fn,**kw):
    P=vcol("VK_Pieces"); k=Kit(); fn(k)
    for f in k.bm.faces:
        if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)
    o=k.finish(n,P,**kw)
    for p in o.data.polygons: p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP,FOLIAGE,CROPS) or (p.material_index==GOODS and p.use_smooth)
    o.hide_render=o.hide_viewport=True; return o

def all_specs():
    nw=dict(wobble=False,grime=False); ng=dict(wobble=False,grime=True)
    return [
     ("SM_VK_Wall_Stone",wall_stone_plain,{}),("SM_VK_Wall_Stone_Window",wall_stone_window,{}),("SM_VK_Wall_Stone_Door",wall_stone_door,{}),
     ("SM_VK_Corner_Stone",corner_stone,{"wobble":False}),
     ("SM_VK_Wall_Plaster",lambda k: plaster_ground(k,"."),{}),("SM_VK_Wall_Plaster_Window",lambda k: plaster_ground(k,"W"),{}),
     ("SM_VK_Wall_Plaster_Door",lambda k: plaster_ground(k,"D"),{}),("SM_VK_Corner_Plaster",corner_plaster,{"wobble":False}),
     ("SM_VK_Wall_Timber",timber_frame,{"grime":False}),("SM_VK_Wall_Timber_X",lambda k: timber_frame(k,False,"X"),{"grime":False}),
     ("SM_VK_Wall_Timber_K",lambda k: timber_frame(k,False,"K"),{"grime":False}),("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),{"grime":False}),
     ("SM_VK_Corner_Timber",corner_timber,nw),
     ("SM_VK_InnerCorner_Stone",inner_corner_stone,{"wobble":False}),("SM_VK_InnerCorner_Plaster",inner_corner_plaster,{"wobble":False}),
     ("SM_VK_InnerCorner_Timber",inner_corner_timber,nw),
     ("SM_VK_Roof_Mid",roof_mid,nw),("SM_VK_Roof_Gable",roof_gable,nw),("SM_VK_Roof_LCorner",roof_L_corner,nw),
     ("SM_VK_Roof_Dormer",dormer,nw),("SM_VK_Porch",porch,nw),("SM_VK_Chimney",chimney,nw),
     ("SM_VK_Prop_FlowerBox",prop_flowerbox,nw),("SM_VK_Prop_Lantern",prop_lantern,nw),("SM_VK_Prop_Sign",prop_sign,nw),
     ("SM_VK_MarketStall",market_stall,ng),
     *[("SM_VK_MarketStall_"+t_.capitalize(),(lambda k,t_=t_: market_stall(k,t_)),ng) for t_ in STALL_TRADES[1:]],
     ("SM_VK_Prop_Well",prop_well,ng),("SM_VK_Prop_Fence",prop_fence,ng),
     ("SM_VK_Prop_FenceGate",prop_fence_gate,ng),("SM_VK_Prop_Cart",prop_cart,ng),("SM_VK_Prop_LampPost",prop_lamppost,ng),
     ("SM_VK_Prop_Bench",prop_bench,ng),("SM_VK_Prop_Crates",prop_crates,ng),("SM_VK_Prop_GardenBed",prop_garden_bed,nw),
     ("SM_VK_Prop_Table",prop_table,ng),("SM_VK_Prop_Stool",prop_stool,ng),("SM_VK_Prop_Trough",prop_trough,ng),
     ("SM_VK_Prop_HayBale",prop_haybale,ng),("SM_VK_Prop_Haystack",prop_haystack,ng),("SM_VK_Prop_Woodpile",prop_woodpile,ng),
     ("SM_VK_Prop_NoticeBoard",prop_noticeboard,ng),("SM_VK_Prop_Signpost",prop_signpost,ng),("SM_VK_Prop_Anvil",prop_anvil,ng),
     ("SM_VK_Prop_Grindstone",prop_grindstone,ng),("SM_VK_Prop_Sacks",prop_sacks,ng),("SM_VK_Prop_WeaponRack",prop_weaponrack,ng),
     ("SM_VK_Prop_BarrelStack",prop_barrelstack,ng),("SM_VK_Prop_Forge",prop_bellows_forge,ng)] + [(n_,_late(f_),kw_) for (n_,f_,kw_) in EXTRA_SPECS]
EXTRA_SPECS=[]
def _late(fn):
    nm=getattr(fn,"__name__","")
    if nm and nm not in ("<lambda>","fn") and nm in globals(): return globals()[nm]
    return fn
def full_rebuild(names=None):
    """rebuild kit meshes in place (same mesh datablock) so every instance and variant updates"""
    old_var={}   # VAR mesh -> base piece name
    for o in bpy.data.objects:
        if o.data and o.data.name.startswith("VAR_") and "_inst" in o.name:
            old_var[o.data.name]=o.name.split("_inst")[0]
    specs=[sp for sp in all_specs() if names is None or sp[0] in names]
    for n,fn,kw in specs:
        k=Kit(); fn(k)
        for f in k.bm.faces:
            if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)
        tmp=k.finish("__tmp__",vcol("VK_Pieces"),**kw)
        for p in tmp.data.polygons: p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP,FOLIAGE,CROPS) or (p.material_index==GOODS and p.use_smooth)
        base=bpy.data.objects.get(n)
        if base is None:
            tmp.name=n; tmp.data.name=n; tmp.hide_render=tmp.hide_viewport=True; continue
        me=base.data
        # copy geometry into the existing datablock (keeps all links)
        import bmesh as _b
        bm=_b.new(); bm.from_mesh(tmp.data); bm.to_mesh(me); bm.free()
        mats=list(tmp.data.materials)
        while len(me.materials)<len(mats): me.materials.append(mats[len(me.materials)])
        for i,m in enumerate(mats): me.materials[i]=m
        tmd=tmp.data; bpy.data.objects.remove(tmp); bpy.data.meshes.remove(tmd)
    # refresh variant meshes: copy geometry from base, keep their material overrides
    for vname,piece in old_var.items():
        vm=bpy.data.meshes.get(vname); base=bpy.data.objects.get(piece)
        if not vm or not base: continue
        if names is not None and piece not in names: continue
        keep=[vm.materials[i] for i in range(len(vm.materials))]
        bm=bmesh.new(); bm.from_mesh(base.data); bm.to_mesh(vm); bm.free()
        basem=list(base.data.materials)
        while len(vm.materials)<len(basem): vm.materials.append(basem[len(vm.materials)])
        for i in range(len(basem)):
            base_default=basem[i]
            vm.materials[i]=keep[i] if i<len(keep) and keep[i] is not None and keep[i]!=base_default and i in SLOT.values() else base_default

def gable_special(k,kind,XF,top,YC):
    if kind=="stone":
        # coping stones along the rake
        for s_ in(-1,1):
            L=math.hypot(YC,top); ang=math.atan2(top,YC); n=7
            for i in range(n):
                t_=(i+0.5)/n; y=s_*YC*(1-t_); z=top*t_
                k.box((XF+0.05,y,z+0.05),(0.3,L/n-0.04,0.32),ASHLAR,rot=(-s_*ang,0,0),bevel=0.05,segs=2)
        # rose window
        zc=top*0.42; R=0.75; n=12
        vs=[k.bm.verts.new((XF-0.03,math.cos(2*math.pi*i/n)*R,zc+math.sin(2*math.pi*i/n)*R)) for i in range(n)]
        c=k.bm.verts.new((XF-0.03,0,zc))
        for i in range(n):
            f=k.bm.faces.new((c,vs[i],vs[(i+1)%n]) ); f.material_index=STAINED
        for i in range(n):
            a=2*math.pi*(i+0.5)/n
            k.box((XF+0.02,math.cos(a)*(R+0.12),zc+math.sin(a)*(R+0.12)),(0.22,0.42,0.26),ASHLAR,rot=(a,0,0),bevel=0.04)
        for i in range(6):
            a=math.pi*i/6; k.box((XF,0,zc),(0.06,0.06,2*R),IRON,rot=(a,0,0),bevel=0)
        k.box((XF+0.02,0,0.12),(0.3,2*YC,0.26),ASHLAR,bevel=0.04)
    else:  # planks: battens, hayloft door, hoist beam, hay
        for y in(-2.2,-1.1,1.1,2.2):
            h=top*(1-abs(y)/YC)-0.1
            k.box((XF+0.03,y,h/2),(0.08,0.14,h),WOOD,bevel=0.02)
        k.box((XF+0.02,0,0.12),(0.2,2*YC,0.22),WOOD,bevel=0.03)
        zd=0.35; hd=1.7
        k.quad([(XF-0.02,-0.7,zd),(XF-0.02,0.7,zd),(XF-0.02,0.7,zd+hd),(XF-0.02,-0.7,zd+hd)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        # one door leaf swung open
        k.box((XF+0.45,-0.72,zd+hd/2),(0.9,0.08,hd),PLANKS,rot=(0,0,-1.2),bevel=0.02)
        for zz in(zd,zd+hd): k.box((XF+0.03,0,zz),(0.14,1.6,0.14),WOOD,bevel=0.03)
        for yy in(-0.78,0.78): k.box((XF+0.03,yy,zd+hd/2),(0.14,0.14,hd+0.1),WOOD,bevel=0.03)
        k.box((XF+0.1,0,zd+0.2),(0.5,1.2,0.35),HAY,bevel=0.1,segs=2,jitter=0.04,seed=3)
        k.box((XF+0.6,0,top-0.35),(1.4,0.18,0.2),WOOD,bevel=0.03)
        k.box((XF+1.2,0,top-0.75),(0.02,0.02,0.7),WOOD,bevel=0)
        _cyl(k,(XF+1.2,0,top-0.45),0.1,0.1,0.06,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
def roof_gable_kind(kind):
    def fn(k):
        for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True))
        ridge(k,-1.5,GX+0.1); gable_end(k,kind)
    return fn
EXTRA_SPECS+= [("SM_VK_Roof_Gable_Stone",lambda k: roof_gable_kind("stone")(k),dict(wobble=False,grime=False)),
               ("SM_VK_Roof_Gable_Planks",lambda k: roof_gable_kind("planks")(k),dict(wobble=False,grime=False))]

HC=4.5
CH_DRESS=DRESS         # the chapel's dressings (arches, jambs, sills, courses, quoins): a darker dressed stone on pale ashlar
def lancet_pts(x0,x1,z0,zs,n=6):
    """pointed arch outline: rectangle x0..x1 from z0 to the spring zs, then two arcs (radius 0.85 w, centred on the
    spring line) meeting at the apex, n segments per arc evenly spaced along it. Returns (outline, apex z); the outline
    runs (x0,z0) (x1,z0) (x1,zs) ... apex ... (x0,zs) and closes back to (x0,z0)"""
    w=x1-x0; r=w*0.85; cR=x1-r; cL=x0+r; xa=(x0+x1)/2
    ta=math.acos((xa-cR)/r); za=zs+r*math.sin(ta)
    pts=[(x0,z0),(x1,z0),(x1,zs)]
    for i in range(1,n): t=ta*i/n; pts.append((cR+r*math.cos(t),zs+r*math.sin(t)))
    pts.append((xa,za))
    for i in range(n-1,0,-1): t=ta*i/n; pts.append((cL-r*math.cos(t),zs+r*math.sin(t)))
    pts.append((x0,zs))
    return pts,za
def lancet_surround(k,pts,y,off,t,d,mi=None,jamb_h=0.46):
    """dressed-stone surround of a lancet outline (lancet_pts), in the plane y (the stones span y-d/2..y+d/2):
    voussoirs along both arcs and alternating long/short jamb stones up both sides, the whole outline including the
    closing left jamb. off: distance from the opening edge to the stones' centre line, t: their width across it"""
    mi=CH_DRESS if mi is None else mi
    z0=pts[0][1]
    for (xa,za_),(xb,zb) in zip(pts,pts[1:]+pts[:1]):
        if abs(za_-z0)<1e-4 and abs(zb-z0)<1e-4: continue                  # sill / threshold side
        L=math.hypot(xb-xa,zb-za_); nx,nz=-(zb-za_)/L,(xb-xa)/L             # nx,nz: into the opening
        if abs(xb-xa)<1e-6:                                                  # jamb: courses of alternating stones
            zlo,zhi=min(za_,zb),max(za_,zb); m=max(1,int(round((zhi-zlo)/jamb_h))); h=(zhi-zlo)/m
            for j in range(m):
                wb=t*(1.45 if j%2==0 else 1.0); inner=off-t/2
                k.box((xa-nx*(inner+wb/2),y,zlo+h*(j+0.5)),(wb,d,h-0.03),mi,bevel=0.03)
            continue
        mx,mz=(xa+xb)/2,(za_+zb)/2; ang=math.atan2(zb-za_,xb-xa)
        k.box((mx-nx*off,y,mz-nz*off),(L+0.04,d,t),mi,rot=(0,-ang,0),bevel=0.03)
def chapel_wall(k,kind="W"):
    stone_panel(k,-1.5,1.5,0,HC,-0.3,0.3,mi=ASHLAR)
    if kind=="D":                                                         # the door's surround fills the cell: no plinth
        k.box((0,0.05,0.25),(CELL,0.5,0.5),CH_DRESS,bevel=0.04)               # in front of it, a low threshold step instead
        k.box((0,-0.55,0.07),(1.9,0.5,0.14),CH_DRESS,bevel=0.03)
    else: k.box((0,-0.05,0.25),(CELL,0.8,0.5),CH_DRESS,bevel=0.04)            # plinth
    k.box((0,-0.34,HC-0.15),(CELL,0.2,0.3),CH_DRESS,bevel=0.05,segs=2)        # cornice
    # buttress at the left edge (right edge belongs to the neighbour / corner)
    for (z0,z1,d) in ((0,2.2,0.9),(2.2,3.6,0.65)):
        k.box((-1.5,-0.3-d/2,(z0+z1)/2),(0.6,d,z1-z0),ASHLAR,bevel=0.05,segs=2)
    k.box((-1.5,-0.55,3.75),(0.6,0.5,0.4),CH_DRESS,rot=(0.6,0,0),bevel=0.05)
    if kind=="W":
        x0,x1,z0,zs=-0.45,0.45,1.3,3.1
        pts,za=lancet_pts(x0,x1,z0,zs)
        vs=[k.bm.verts.new((x,-0.33,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=STAINED
        for l in f.loops: l[k.uv].uv=(l.vert.co.x*0.55,l.vert.co.z*0.55)
        # lead cames
        k.box((0,-0.35,(z0+za)/2),(0.05,0.03,za-z0),IRON,bevel=0)
        for zz in(1.9,2.5): k.box((0,-0.35,zz),(x1-x0,0.03,0.05),IRON,bevel=0)
        lancet_surround(k,pts,-0.36,0.1,0.22,0.12)                          # voussoir frame
        k.box((0,-0.42,z0-0.08),(1.2,0.3,0.16),CH_DRESS,bevel=0.04)
    elif kind=="D":
        x0,x1,z0,zs=-0.8,0.8,0.0,2.2
        pts,za=lancet_pts(x0,x1,z0,zs,8)
        vs=[k.bm.verts.new((x,-0.33,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=PLANKS
        for l in f.loops: l[k.uv].uv=(l.vert.co.x/2,l.vert.co.z/2)
        k.box((0,-0.36,(za)/2),(0.06,0.05,za),WOOD,bevel=0)
        for zz in(0.5,1.6):
            for s_ in(-1,1): k.box((s_*0.45,-0.37,zz),(0.6,0.03,0.09),IRON,bevel=0.01)
        for s_ in(-1,1): _cyl(k,(s_*0.15,-0.4,1.1),0.07,0.07,0.03,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
        for ring in range(3): lancet_surround(k,pts,-0.36-ring*0.07,0.14+ring*0.2,0.2,0.14)   # stepped orders
        k.box((0,-0.8,0.08),(2.6,1.0,0.16),ASHLAR,bevel=0.04)
def chapel_corner(k):
    k.box((0,0,HC/2),(0.9,0.9,HC),ASHLAR,bevel=0.05,segs=2)
    k.box((0,0,0.25),(1.05,1.05,0.5),CH_DRESS,bevel=0.04)
    for (z0,z1,d) in ((0,2.4,1.1),(2.4,3.8,0.8)):
        k.box((-0.35-d/2+0.45,-0.35-d/2+0.45,(z0+z1)/2),(d,d,z1-z0),ASHLAR,rot=(0,0,0),bevel=0.05,segs=2)
    k.box((-0.05,-0.05,HC-0.15),(1.0,1.0,0.3),CH_DRESS,bevel=0.05,segs=2)
    k.box((0,0,HC+0.7),(0.35,0.35,1.2),CH_DRESS,bevel=0.05,segs=2)
    _cyl(k,(0,0,HC+1.55),0.28,0.0,0.6,4,CH_DRESS,rot=Matrix.Rotation(math.pi/4,4,"Z"))
def bell_tower(k):
    """square tower 3.6m, local origin at its base centre; front (door side) toward -Y"""
    W=3.6; h1=8.0; hb=3.0
    stone_panel(k,-W/2,W/2,0,h1,-W/2,W/2,mi=ASHLAR)
    k.box((0,0.075,0.3),(W+0.3,W+0.15,0.6),CH_DRESS,bevel=0.05,segs=2)          # plinth: the front strip is cut for the door
    for sx in (-1,1): k.box((sx*(W/2+0.15+0.98)/2,-W/2-0.075,0.3),(W/2+0.15-0.98,0.15,0.6),CH_DRESS,bevel=0.05,segs=2)
    for zz in(3.5,h1): k.box((0,0,zz),(W+0.24,W+0.24,0.28),CH_DRESS,bevel=0.05,segs=2)
    for sx in(-1,1):
        for sy in(-1,1):
            k.box((sx*(W/2+0.05),sy*(W/2+0.05),(h1)/2),(0.5,0.5,h1),CH_DRESS,bevel=0.05,segs=2)
    # slit windows
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z")
        sub=Kit(); sub.box((0,-W/2-0.02,5.5),(0.18,0.06,1.1),VOID,bevel=0); merge_kit(k,sub,R)
    # belfry: 4 open arches framed in dressed stone (corner piers with capitals, arch rings, sill and lintel bands),
    # pale ashlar spandrels set back between them; bell inside
    z0=h1+0.14; zsp=z0+1.15                       # arch spring line = top of the pier capitals
    for sx in(-1,1):
        for sy in(-1,1):
            k.box((sx*(W/2-0.3),sy*(W/2-0.3),z0+hb/2),(0.6,0.6,hb),CH_DRESS,bevel=0.05,segs=2)
            k.box((sx*(W/2-0.3),sy*(W/2-0.3),zsp-0.08),(0.74,0.74,0.16),CH_DRESS,bevel=0.03)          # capital
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z")
        sub=Kit()
        sub.box((0,-W/2+0.3,z0+hb-0.25),(W,0.6,0.5),CH_DRESS,bevel=0.05,segs=2)
        sub.box((0,-W/2+0.3,z0+0.175),(W-1.2,0.56,0.35),ASHLAR,bevel=0.03)          # breast wall under the opening ...
        sub.box((0,-W/2+0.3,z0+0.41),(W-1.1,0.66,0.13),CH_DRESS,bevel=0.03)         # ... and its sill coping
        # voussoir ring: the intrados (1.2 x 1.0) meets the piers' inner faces, the extrados (1.55 x 1.3) lands on the
        # capitals and stops just under the lintel; 9 wedge stones with thin joints, 3 cm proud of both wall faces
        n=9; ri,rzi,ro,rzo=W/2-0.6,1.0,W/2-0.25,1.3
        def ep(a_,R,Rz): return (R*math.cos(a_),zsp+Rz*math.sin(a_))
        ya,yb_=-W/2-0.03,-W/2+0.63
        for i in range(n):
            a0=math.pi*i/n+(0.012 if i else 0.0); a1=math.pi*(i+1)/n-(0.012 if i<n-1 else 0.0)
            p=[ep(a0,ri,rzi),ep(a1,ri,rzi),ep(a1,ro,rzo),ep(a0,ro,rzo)]            # inner a0, inner a1, outer a1, outer a0
            f=[(x,ya,z) for x,z in p]; bk=[(x,yb_,z) for x,z in p]
            def qd(pts,want):
                fc=sub.quad(pts,CH_DRESS)
                if fc.normal.dot(Vector(want))<0: fc.normal_flip()
            am=(a0+a1)/2
            qd([f[0],f[1],f[2],f[3]],(0,-1,0)); qd([bk[0],bk[1],bk[2],bk[3]],(0,1,0))          # wall faces
            qd([f[0],f[1],bk[1],bk[0]],(-math.cos(am),0,-math.sin(am)))                     # intrados (into the opening)
            qd([f[3],bk[3],bk[2],f[2]],(math.cos(am),0,math.sin(am)))                       # extrados
            qd([f[0],bk[0],bk[3],f[3]],(math.sin(a0),0,-math.cos(a0)))                      # joint ends
            qd([f[1],f[2],bk[2],bk[1]],(-math.sin(a1),0,math.cos(a1)))
        # solid spandrels: pale fill between the arch and the lintel/piers, set back 5 cm so the dressed frame reads
        hw=ri; zt=z0+hb-0.5; yf,yb=-W/2+0.05,-W/2+0.55; m=16
        crv=[(hw*math.cos(math.pi*i/m),zsp+(rzi+0.02)*math.sin(math.pi*i/m)) for i in range(m+1)]
        for (x0,z0_),(x1,z1_) in zip(crv[:-1],crv[1:]):
            if x0>x1: (x0,z0_),(x1,z1_)=(x1,z1_),(x0,z0_)
            sub.quad([(x0,yf,z0_),(x1,yf,z1_),(x1,yf,zt),(x0,yf,zt)],ASHLAR)          # outer face (-Y)
            sub.quad([(x0,yb,zt),(x1,yb,zt),(x1,yb,z1_),(x0,yb,z0_)],ASHLAR)          # inner face (+Y)
            sub.quad([(x0,yb,z0_),(x1,yb,z1_),(x1,yf,z1_),(x0,yf,z0_)],ASHLAR)        # soffit (faces down into the arch)
        merge_kit(k,sub,R)
    k.box((0,0,z0+0.1),(W-0.2,W-0.2,0.2),WOOD,bevel=0.03)
    # bell + yoke
    k.box((0,0,z0+hb-0.9),(2.6,0.25,0.25),WOOD,bevel=0.04)
    vs=_cyl(k,(0,0,z0+hb-1.55),0.62,0.3,1.0,16,BRONZE)
    _cyl(k,(0,0,z0+hb-2.08),0.66,0.66,0.1,16,BRONZE)
    _ico(k,(0,0,z0+hb-1.95),0.12,IRON)
    # spire
    zs=z0+hb
    k.box((0,0,zs+0.15),(W+0.4,W+0.4,0.3),CH_DRESS,bevel=0.05,segs=2)
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=8,radius1=(W+0.5)/2*1.08,radius2=0.05,depth=6.5)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zs+0.3+3.25))@Matrix.Rotation(math.pi/8,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces})
    for f in fs: f.material_index=ROOF
    k.bm.normal_update()
    for f in fs:
        n=f.normal; 
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized(); 
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],(p.z-zs)/TILE[ROOF]*1.2)
    # small lucarnes on spire
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-1.35,zs+1.4),(0.6,0.5,0.9),WOOD,bevel=0.03)
        sub.quad([(-0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.7),(-0.2,-1.61,zs+1.7)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for sx in(-1,1): sub.box((sx*0.2,-1.4,zs+2.0),(0.55,0.7,0.07),ROOF,rot=(0,sx*0.8,0),bevel=0.02)
        merge_kit(k,sub,R)
    # cross + weathervane
    top=zs+0.3+6.5
    k.box((0,0,top+0.5),(0.1,0.1,1.2),BRONZE,bevel=0.02)
    k.box((0,0,top+0.75),(0.6,0.1,0.1),BRONZE,bevel=0.02)
    # door
    x0,x1=-0.6,0.6; pts,za=lancet_pts(x0,x1,0,1.9,6)
    vs=[k.bm.verts.new((x,-W/2-0.02,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=PLANKS
    for l in f.loops: l[k.uv].uv=(l.vert.co.x/2,l.vert.co.z/2)
    lancet_surround(k,pts,-W/2-0.05,0.12,0.24,0.14)
    k.box((0,-W/2-0.3,0.07),(1.5,0.6,0.14),CH_DRESS,bevel=0.03)                 # threshold step
EXTRA_SPECS+= [("SM_VK_Chapel_Wall",lambda k: chapel_wall(k,"W"),dict(wobble=False,grime=True)),
               ("SM_VK_Chapel_Wall_Plain",lambda k: chapel_wall(k,"."),dict(wobble=False,grime=True)),
               ("SM_VK_Chapel_Wall_Door",lambda k: chapel_wall(k,"D"),dict(wobble=False,grime=True)),
               ("SM_VK_Chapel_Corner",chapel_corner,dict(wobble=False,grime=True)),
               ("SM_VK_BellTower",bell_tower,dict(wobble=False,grime=True))]

def build_chapel(coll,origin,n=4,roof="Blue",tower=True):
    L=n*CELL; st={"roof":roof}
    for i in range(n):
        x=-L/2+1.5+3*i
        place_v(coll,"SM_VK_Chapel_Wall",x,-3,0,0,origin,st)
        place_v(coll,"SM_VK_Chapel_Wall" if i!=1 else "SM_VK_Chapel_Wall_Door",x,3,0,180,origin,st)
    for yy in(-1.5,1.5):
        place_v(coll,"SM_VK_Chapel_Wall_Plain",-L/2,yy,0,-90,origin,st)
        place_v(coll,"SM_VK_Chapel_Wall_Plain",L/2,-yy,0,90,origin,st)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
        place_v(coll,"SM_VK_Chapel_Corner",cx,cy,0,r,origin,st)
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==0: place_v(coll,"SM_VK_Roof_Gable_Stone",x,0,HC,180,origin,st)
        elif i==n-1: place_v(coll,"SM_VK_Roof_Gable_Stone",x,0,HC,0,origin,st)
        else: place_v(coll,"SM_VK_Roof_Mid",x,0,HC,0,origin,st)
    if tower: place_v(coll,"SM_VK_BellTower",L/2+2.2,0,0,90,origin,st)

HB=4.2
# ---------------- barn
def barn_wall(k,kind="."):
    stone_panel(k,-1.5,1.5,0,0.7,-0.3,0.2); plinth(k)
    grid_cut(k,k.box((0,-0.02,(0.7+HB)/2),(CELL,0.36,HB-0.7),PLANKS,bevel=0))
    k.box((0,-0.24,0.8),(CELL,0.2,0.2),WOOD,bevel=0.03); k.box((0,-0.24,HB-0.12),(CELL,0.22,0.24),WOOD,bevel=0.03)
    k.box((-1.5,-0.26,(0.7+HB)/2),(0.26,0.22,HB-0.7),WOOD,bevel=0.04)
    if kind==".":
        k.box((0,-0.26,2.4),(CELL,0.18,0.16),WOOD,bevel=0.03)
        brace(k,-1.35,0.9,-0.2,2.3,y=-0.27); brace(k,1.35,0.9,0.2,2.3,y=-0.27)
        # small window slot
        k.quad([(-0.4,-0.21,2.9),(0.4,-0.21,2.9),(0.4,-0.21,3.5),(-0.4,-0.21,3.5)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for x in(-0.2,0,0.2): k.box((x,-0.25,3.2),(0.05,0.05,0.62),WOOD,bevel=0)
        k.box((0,-0.26,2.85),(1.0,0.12,0.12),WOOD,bevel=0.02); k.box((0,-0.26,3.55),(1.0,0.12,0.12),WOOD,bevel=0.02)
    elif kind=="D":
        hw=1.25; hd=3.3
        k.quad([(-hw,-0.21,0.05),(hw,-0.21,0.05),(hw,-0.21,hd),(-hw,-0.21,hd)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
        k.box((0,-0.28,hd+0.12),(2*hw+0.5,0.26,0.26),WOOD,bevel=0.04)
        for s_ in(-1,1): k.box((s_*(hw+0.12),-0.28,hd/2),(0.24,0.26,hd),WOOD,bevel=0.04)
        # left leaf closed, right leaf swung open
        def leaf(xform):
            sub=Kit()
            sub.box((hw/2,0,hd/2),(hw-0.04,0.12,hd-0.1),PLANKS,bevel=0.02)
            for zz in(0.4,hd-0.4): sub.box((hw/2,-0.08,zz),(hw-0.1,0.06,0.18),WOOD,bevel=0.02)
            L=math.hypot(hw-0.2,hd-1.0); sub.box((hw/2,-0.08,hd/2),(L,0.06,0.16),WOOD,rot=(0,-math.atan2(hd-1.0,hw-0.2),0),bevel=0.02)
            merge_kit(k,sub,xform)
        leaf(Matrix.Translation((-hw,-0.26,0.05)))
        leaf(Matrix.Translation((hw,-0.3,0.05))@Matrix.Rotation(math.pi-1.1,4,"Z"))
        k.box((0,-0.8,0.05),(2*hw+0.4,1.0,0.1),STONE,bevel=0.03)
        k.box((-0.2,-0.9,0.2),(1.2,0.8,0.25),HAY,rot=(0,0,0.3),bevel=0.12,segs=2,jitter=0.05,seed=4)
def barn_corner(k):
    k.box((-0.05,-0.05,0.35),(0.8,0.8,0.7),STONE,bevel=0.05,segs=2,jitter=0.02,seed=1)
    k.box((-0.25,-0.25,(0.7+HB)/2),(0.34,0.34,HB-0.7),WOOD,bevel=0.05,segs=2)
    k.box((-0.1,-0.1,HB-0.12),(0.5,0.5,0.24),WOOD,bevel=0.04)
# ---------------- lean-to shed (attaches to an existing wall; wall-local, outer = -Y)
def lean_to(k,open_front=True,roofmat=None):
    rm=ROOF if roofmat is None else roofmat
    D_=3.2; zh=3.0; zl=2.35
    for x in(-1.5,1.5):
        k.box((x,-D_,zl/2),(0.22,0.22,zl),WOOD,bevel=0.05,segs=2)
        k.box((x,-D_,0.08),(0.4,0.4,0.16),STONE,bevel=0.04)
    k.box((0,-D_,zl+0.05),(CELL+0.3,0.24,0.24),WOOD,bevel=0.04)
    for x in(-1.5,0,1.5):
        L=math.hypot(D_,zh-zl); ang=math.atan2(zh-zl,D_)
        k.box((x,-D_/2,(zh+zl)/2+0.12),(0.16,L+0.3,0.18),WOOD,rot=(ang,0,0),bevel=0.03)
    for x in(-1.5,1.5):
        k.box((x+(-0.35 if x>0 else 0.35),-D_+0.35,zl-0.3),(0.12,0.6,0.12),WOOD,rot=(0.75,0,0),bevel=0.02)
    L=math.hypot(D_+0.6,zh-zl+0.3); ang=math.atan2(zh-zl+0.3,D_+0.6)
    k.box((0,-(D_+0.6)/2,(zh+zl)/2+0.32),(CELL+0.35,L,0.14),rm,rot=(ang,0,0),bevel=0.03)
    k.box((0,-D_/2,0.03),(CELL,D_,0.06),PLANKS,bevel=0)
    if not open_front:
        for x in(-1.5,1.5): pass
# ---------------- tavern sign (wall-mounted bracket, big tankard emblem)
def tavern_sign(k):
    k.box((0,0.03,0),(0.18,0.1,0.7),IRON,bevel=0.02)
    k.box((0,-0.8,0.25),(0.08,1.6,0.08),IRON,bevel=0.015)
    k.box((0,-0.5,-0.05),(0.05,0.05,0.8),IRON,rot=(0.8,0,0),bevel=0)
    for yy in(-0.45,-1.35): k.box((0,yy,0.05),(0.02,0.02,0.35),IRON,bevel=0)
    k.box((0,-0.9,-0.55),(0.12,1.3,0.9),WOOD,bevel=0.05,segs=2)
    k.box((0,-0.9,-0.55),(0.14,1.1,0.72),YELLOW,bevel=0.02)
    _cyl(k,(-0.1,-0.95,-0.58),0.2,0.2,0.46,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(-0.16,-0.95,-0.33),0.18,0.18,0.06,10,HAY,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((-0.1,-0.66,-0.58),(0.06,0.12,0.3),WOOD,bevel=0.01)
# ---------------- string of festoon lights for beer garden (between two points, 6m)
def festoon(k,L=6.0,sag=0.6):
    n=12; pts=[Vector((-L/2+L*i/n,0,-sag*math.sin(math.pi*i/n))) for i in range(n+1)]
    for i in range(n):
        a,b=pts[i],pts[i+1]; m=(a+b)/2; d=b-a
        k.box(tuple(m),(d.length,0.02,0.02),IRON,rot=(0,-math.atan2(d.z,d.x),0),bevel=0)
        if i: _ico(k,tuple(pts[i]-Vector((0,0,0.1))),0.07,GLOW,sub=1)
EXTRA_SPECS+= [("SM_VK_Wall_Barn",lambda k: barn_wall(k,"."),dict(wobble=True,grime=True)),
               ("SM_VK_Wall_Barn_Door",lambda k: barn_wall(k,"D"),dict(wobble=False,grime=True)),
               ("SM_VK_Corner_Barn",barn_corner,dict(wobble=False,grime=True)),
               ("SM_VK_LeanTo",lean_to,dict(wobble=False,grime=False)),
               ("SM_VK_LeanTo_Thatch",lambda k: lean_to(k,roofmat=THATCH),dict(wobble=False,grime=False)),
               ("SM_VK_Prop_TavernSign",tavern_sign,dict(wobble=False,grime=False)),
               ("SM_VK_Prop_Festoon",festoon,dict(wobble=False,grime=False))]

def windmill(k):
    n=8; H_=8.5; r0,r1=3.0,2.2
    # tapered octagonal stone body
    vs=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=n,radius1=r0,radius2=r1,depth=H_)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,H_/2))@Matrix.Rotation(math.pi/8,4,"Z"),verts=vs)
    fs=list({f for v in vs for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=STONE; nrm=f.normal
        U=Vector((-nrm.y,nrm.x,0)).normalized() if abs(nrm.z)<0.9 else Vector((1,0,0))
        V=Vector((0,0,1)) if abs(nrm.z)<0.9 else Vector((0,1,0))
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[STONE],p.dot(V)/TILE[STONE])
    grid_cut(k,list({v for f in fs for v in f.verts}),1.5)
    # the octagon's corners are at 22.5 + 45*i degrees, its faces centred on 0, 45, 90 ... (-90 = front, -Y)
    # corner quoins on the 8 edges
    for i in range(n):
        a=2*math.pi*i/n+math.pi/n
        z=0; j=0
        while z<H_-0.3:
            t_=z/H_; r=r0+(r1-r0)*t_+0.05
            k.box((math.cos(a)*r,math.sin(a)*r,z+0.25),(0.5 if j%2 else 0.35,0.35 if j%2 else 0.5,0.46),STONE,rot=(0,0,a),bevel=0.05,segs=1,jitter=0.015,seed=i*50+j)
            z+=0.5; j+=1
    # plinth (aligned with the body), door, windows
    _cyl(k,(0,0,0.25),r0+0.25,r0+0.25,0.5,n,STONE,rot=Matrix.Rotation(math.pi/n,4,"Z"))
    lean=math.atan((r0-r1)*math.cos(math.pi/n)/H_)            # the faces lean in with the taper
    def face(deg,zc):
        """frame on the face centred at angle deg, height zc: the face plane is local y=0 (outward -y), leaning with it"""
        ap=(r0+(r1-r0)*zc/H_)*math.cos(math.pi/n)
        return Matrix.Rotation(math.radians(deg)+math.pi/2,4,"Z")@Matrix.Translation((0,-ap,zc))@Matrix.Rotation(-lean,4,"X")
    d=Kit()
    d.quad([(-0.6,-0.02,-1.0),(0.6,-0.02,-1.0),(0.6,-0.02,1.0),(-0.6,-0.02,1.0)],PLANKS,uvs=[(0,0),(0.6,0),(0.6,1),(0,1)])
    for s_ in(-1,1): d.box((s_*0.72,-0.08,0.0),(0.26,0.3,2.1),WOOD,bevel=0.04)
    d.box((0,-0.1,1.12),(1.7,0.34,0.26),WOOD,bevel=0.04)
    merge_kit(k,d,face(-90,1.5))
    k.box((0,-r0-0.45,0.35),(1.6,0.9,0.2),STONE,bevel=0.05,segs=2)
    for (deg,z) in ((-45,4.2),(45,5.8),(180,3.6),(-135,6.6)):
        w=Kit()
        w.quad([(-0.3,-0.02,-0.4),(0.3,-0.02,-0.4),(0.3,-0.02,0.4),(-0.3,-0.02,0.4)],WINDOW,uvs=[(0,0),(0.6,0),(0.6,0.8),(0,0.8)])
        for s_ in(-1,1): w.box((s_*0.38,-0.06,0.0),(0.14,0.2,0.95),WOOD,bevel=0.025)
        w.box((0,-0.06,0.5),(0.9,0.22,0.14),WOOD,bevel=0.025); w.box((0,-0.11,-0.5),(0.9,0.3,0.12),STONE,bevel=0.02)
        merge_kit(k,w,face(deg,z))
    # timber gallery / balcony
    zg=H_-0.2
    _cyl(k,(0,0,zg),r1+1.1,r1+1.1,0.14,16,PLANKS)
    for i in range(16):
        a=2*math.pi*i/16; r=r1+1.0
        k.box((math.cos(a)*r,math.sin(a)*r,zg+0.5),(0.1,0.1,1.0),WOOD,bevel=0.02)
        k.box((math.cos(a)*(r1+0.5),math.sin(a)*(r1+0.5),zg-0.45),(0.9,0.12,0.12),WOOD,rot=(0,0.7,a),bevel=0.02)
        a2=2*math.pi*(i+0.5)/16
        k.box((math.cos(a2)*r,math.sin(a2)*r,zg+0.95),(0.1,2*math.pi*r/16+0.1,0.1),WOOD,rot=(0,0,a2),bevel=0.02)
    # timber cap (boat shaped -> use a ridged dome) with shingles
    zc=H_
    k.box((0,0,zc+0.9),(r1*2.1,r1*1.9,1.8),PLANKS,bevel=0.1,segs=2)
    for s_ in(-1,1):
        k.box((0,s_*r1*0.55,zc+2.35),(r1*2.5,r1*1.45,0.18),ROOF,rot=(-s_*0.72,0,0),bevel=0.04)
    k.box((0,0,zc+2.95),(r1*2.55,0.4,0.4),ROOF,rot=(math.pi/4,0,0),bevel=0.1,segs=2)
    for s_ in(-1,1):
        v=[k.bm.verts.new(p) for p in ((s_*r1*1.05,-r1*0.95,zc+1.8),(s_*r1*1.05,r1*0.95,zc+1.8),(s_*r1*1.05,0,zc+2.75))]
        f=k.bm.faces.new(v if s_>0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    # windshaft
    _cyl(k,(0,-r1-0.4,zc+1.6),0.22,0.22,1.4,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    # tail pole + wheel
    k.box((0,r1+1.6,zc+0.4),(0.18,3.4,0.18),WOOD,rot=(-0.55,0,0),bevel=0.03)
def windmill_sails(k):
    _cyl(k,(0,0,0),0.35,0.35,0.5,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for i in range(4):
        R=Matrix.Rotation(i*math.pi/2+0.35,4,"Y"); sub=Kit()
        sub.box((0,-0.25,3.6),(0.22,0.2,7.2),WOOD,bevel=0.04)
        for j in range(9): sub.box((0.55,-0.3,1.4+j*0.68),(1.25,0.07,0.09),WOOD,bevel=0.01)
        for xx in(0.2,0.95,1.18): sub.box((xx,-0.3,4.3),(0.07,0.07,5.8),WOOD,bevel=0.01)
        sub.box((0.6,-0.33,4.4),(1.0,0.03,5.2),CLOTH_B,bevel=0)
        merge_kit(k,sub,R)
def guard_tower(k):
    W=4.0; h1=6.0
    stone_panel(k,-W/2,W/2,0,h1,-W/2,W/2)
    k.box((0,0,0.3),(W+0.5,W+0.5,0.6),STONE,bevel=0.06,segs=2)
    for sx in(-1,1):
        for sy in(-1,1):
            z=0.6;j=0
            while z<h1-0.2:
                long_x=j%2==0
                k.box((sx*(W/2-0.2),sy*(W/2-0.2),z+0.22),(1.0 if long_x else 0.55,0.55 if long_x else 1.0,0.44),STONE,bevel=0.06,segs=2,jitter=0.015,seed=j+sx*7+sy*3)
                z+=0.46; j+=1
    # arrow slits + door
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-W/2-0.02,3.6),(0.14,0.06,1.0),VOID,bevel=0)
        sub.box((0,-W/2-0.08,3.6),(0.5,0.12,1.3),STONE,bevel=0.04)
        merge_kit(k,sub,R)
    k.quad([(-0.55,-W/2-0.02,0.6),(0.55,-W/2-0.02,0.6),(0.55,-W/2-0.02,2.5),(-0.55,-W/2-0.02,2.5)],PLANKS,uvs=[(0,0),(0.55,0),(0.55,0.95),(0,0.95)])
    for zz in(1.0,2.0): k.box((0,-W/2-0.06,zz),(1.0,0.03,0.09),IRON,bevel=0.01)
    k.box((0,-W/2-0.1,2.65),(1.5,0.3,0.3),STONE,bevel=0.05,segs=2)
    for s_ in(-1,1): k.box((s_*0.7,-W/2-0.08,1.55),(0.3,0.25,1.95),STONE,bevel=0.05)
    # stairs to door
    for i in range(3): k.box((0,-W/2-0.5-i*0.3,0.5-i*0.17),(1.4,0.35,0.2),STONE,bevel=0.04)
    # overhanging timber hoarding
    z0=h1; WT=W+1.2; hh=2.4
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(WT/2-0.15),sy*(WT/2-0.15),z0+hh/2),(0.26,0.26,hh),WOOD,bevel=0.05,segs=2)
    k.box((0,0,z0+0.1),(WT,WT,0.2),PLANKS,bevel=0.03)
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-WT/2+0.08,z0+0.7),(WT-0.3,0.14,1.0),PLANKS,bevel=0.02)
        sub.box((0,-WT/2+0.08,z0+hh-0.12),(WT,0.22,0.24),WOOD,bevel=0.04)
        sub.box((0,-WT/2+0.08,z0+1.25),(WT,0.2,0.18),WOOD,bevel=0.03)
        for i in range(5): sub.box((-WT/2+0.6+i*(WT-1.2)/4,-W/2-0.3,z0-0.35),(0.18,0.8,0.18),WOOD,rot=(0.6,0,0),bevel=0.03)
        merge_kit(k,sub,R)
    # pyramid roof
    rz=z0+hh
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(WT+1.0)/math.sqrt(2),radius2=0.05,depth=3.2)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,rz+1.6))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.9)
    # flag
    k.box((0,0,rz+3.9),(0.08,0.08,2.0),WOOD,bevel=0.02)
    k.box((0,0.55,rz+4.5),(0.04,1.1,0.7),CLOTH_A,bevel=0)
EXTRA_SPECS+= [("SM_VK_Windmill",windmill,dict(wobble=False,grime=True)),("SM_VK_Windmill_Sails",windmill_sails,dict(wobble=False,grime=False)),
               ("SM_VK_GuardTower",guard_tower,dict(wobble=False,grime=True))]

def build_tavern(coll,origin,seed=31):
    st={"ground":"Stone","plaster":"Ochre","shutter":"Red","roof":"Red","seed":seed}
    build_L_v(coll,origin,2,1,2,st)
    ox,oy,orz=origin; c,s_=math.cos(orz),math.sin(orz)
    def P(n,x,y,z,r,sty={}): place_v(coll,n,x,y,z,r,origin,sty)
    P("SM_VK_Prop_TavernSign",-1.5+3*1+1.1,-3.3,3.4,0)
    P("SM_VK_Porch",1.5,-3,0,0,st)
    # beer garden in the L's inner yard (x 3..12, y 3..9) -> fenced
    for i,(x,y) in enumerate(((6.0,5.5),(9.8,6.5))):
        P("SM_VK_Prop_Table",x,y,0,90)
        for dy in(-0.75,0.75):
            for dx in(-0.6,0.6): P("SM_VK_Prop_Stool",x+dy*1.1,y+dx,0,0)
    P("SM_VK_Prop_BarrelStack",11.6,3.9,0,0)
    P("SM_VK_Prop_Festoon",8.0,4.0,3.0,0)
    for (x,y) in((4.6,4.0),(11.4,4.0)): P("SM_VK_Prop_LampPost",x,y,0,0)
    fence_run(coll,(3.2,9.4),(12.0,9.4),origin); fence_run(coll,(12.0,3.3),(12.0,9.4),origin,gate_at=1)
def build_blacksmith(coll,origin,seed=32):
    st={"ground":"Stone","plaster":"White","shutter":"Natural","roof":"Green","seed":seed}
    build_house_v(coll,origin,2,1,st,front="DW",back="..",chimney=True)
    def P(n,x,y,z,r,sty={}): place_v(coll,n,x,y,z,r,origin,sty)
    # open workshop lean-tos along the +X end wall
    for yy in(-1.5,1.5): P("SM_VK_LeanTo",3.0,-yy,0,90,st)
    P("SM_VK_Prop_Forge",4.6,1.2,0,-90)
    P("SM_VK_Prop_Anvil",4.8,-0.9,0,20)
    P("SM_VK_Prop_Grindstone",7.0,-2.4,0,90)
    P("SM_VK_Prop_WeaponRack",3.6,-2.5,0,0)
    P("SM_VK_Prop_Trough",7.1,0.9,0,90)
    P("SM_VK_Prop_BarrelStack",-1.0,4.2,0,0)
    P("SM_VK_Prop_Woodpile",-1.5,-4.9,0,0)
    P("SM_VK_Prop_Crates",7.4,-4.3,0,30)

# ================================================================ LANDMARKS: smithy + inn signature pieces
def _tube(k,a,b,r,mi,segs=8):
    a=Vector(a); b=Vector(b); d=b-a
    return _cyl(k,(a+b)/2,r,r,d.length,segs,mi,rot=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4())
def smithy_chimney(k):
    """massive forge stack 2.2 x 1.7 m, 9.2 m tall, open hearth at the front (-Y) with glowing coals under a stone hood"""
    W,D=2.2,1.7
    stone_panel(k,-W/2,W/2,0,0.85,-D/2,D/2,mi=STONE)                       # raised hearth bed
    stone_panel(k,-W/2,-0.55,0.85,2.3,-D/2,D/2,mi=STONE); stone_panel(k,0.55,W/2,0.85,2.3,-D/2,D/2,mi=STONE)
    stone_panel(k,-0.55,0.55,0.85,2.3,0.05,D/2,mi=STONE)                    # back of the fire box
    k.quad([(-0.55,0.049,0.9),(0.55,0.049,0.9),(0.55,0.049,2.25),(-0.55,0.049,2.25)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.box((0,-D/2+0.2,2.45),(W+0.3,0.75,0.35),STONE_BLOCK,bevel=0.05)      # hood lintel
    stone_panel(k,-W/2+0.1,W/2-0.1,2.62,4.2,-D/2+0.1,D/2,mi=STONE)
    stone_panel(k,-0.8,0.8,4.2,9.0,-0.65,0.65,mi=STONE)
    for z in (4.2,6.4): k.box((0,0,z),(1.75,1.45,0.22),STONE_BLOCK,bevel=0.04)
    k.box((0,0,9.05),(1.85,1.55,0.25),STONE_BLOCK,bevel=0.05)
    for sx in (-1,1): k.box((sx*0.45,0,9.45),(0.18,0.18,0.55),IRON,bevel=0.02)
    k.box((0,0,9.78),(1.4,1.1,0.08),IRON,bevel=0.02)                       # iron rain hat
    for sx in (-1,1):                                                        # sloped shoulders
        k.box((sx*(W/2-0.25),0,4.35),(0.55,1.5,0.3),STONE_BLOCK,rot=(0,sx*0.5,0),bevel=0.04)
    rnd=random.Random(5)                                                    # coal bed
    for i in range(22):
        c=(rnd.uniform(-0.45,0.45),rnd.uniform(-0.55,0.0),0.9+rnd.uniform(0,0.12))
        _mat(_ico(k,c,rnd.uniform(0.07,0.13),GLOW if i%3 else COAL,sub=1,jit=0.02,seed=i),GLOW if i%3 else COAL,False)
    k.box((0,-0.3,0.88),(1.05,0.6,0.05),GLOW,bevel=0)
    for i in range(3): k.box((-0.3+0.3*i,-D/2-0.05,0.86),(0.06,0.25,0.06),IRON,bevel=0.01)   # fire irons
def smithy_canopy(k):
    """open workshop canopy 6 x 6 m: four heavy posts, knee braces, tie beams, two slate slopes (ridge along X)"""
    H=3.2; R=4.6
    for sx in (-1,1):
        for sy in (-1,1):
            k.box((sx*2.75,sy*2.75,H/2),(0.36,0.36,H),WOOD,bevel=0.05,segs=2)
            k.box((sx*2.75,sy*2.75,0.12),(0.55,0.55,0.24),STONE_BLOCK,bevel=0.04)
    for sy in (-1,1): k.box((0,sy*2.75,H+0.12),(6.2,0.32,0.3),WOOD,bevel=0.04)
    for sx in (-1,1): k.box((sx*2.75,0,H+0.12),(0.3,6.2,0.3),WOOD,bevel=0.04)
    for sx in (-1,1):
        for sy in (-1,1):
            for ax in (0,1):
                d=Vector((0 if ax else -sx,-sy if ax else 0,0))
                a=Vector((sx*2.75,sy*2.75,H-0.75)); b=a+d*0.75+Vector((0,0,0.72))
                _tube(k,a,b,0.07,WOOD,6)
    k.box((0,0,R-0.05),(6.3,0.25,0.25),WOOD,bevel=0.04)
    k.box((0,0,(H+R)/2+0.05),(0.25,0.25,R-H),WOOD,bevel=0.03)
    for sy in (-1,1):
        ang=math.atan2(R-H,3.4)
        c=Vector((0,sy*1.7,(H+R)/2+0.22))
        k.box(tuple(c),(7.0,3.75,0.14),ROOF,rot=(-sy*ang,0,0),bevel=0.02)
        for i in range(7):
            k.box((-3.0+i,sy*1.7,(H+R)/2+0.1),(0.12,3.7,0.12),WOOD,rot=(-sy*ang,0,0),bevel=0.01)
def smith_bellows(k):
    """great leather bellows on a trestle, nozzle to -X, with its rocking lever"""
    for sx in (-0.45,0.45):
        for sy in (-0.3,0.3): k.box((sx,sy,0.35),(0.1,0.1,0.7),WOOD,bevel=0.02)
    k.box((0,0,0.72),(1.2,0.75,0.08),WOOD,bevel=0.02)
    vs=[k.bm.verts.new(p) for p in ((-0.75,0,0.95),(0.6,-0.4,0.95),(0.6,0.4,0.95),(-0.75,0,1.25),(0.6,-0.4,1.35),(0.6,0.4,1.35))]
    for f in ((0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)):
        ff=k.bm.faces.new([vs[i] for i in f]); ff.material_index=HIDE
    k.bm.normal_update(); k.project([f for f in {f for v in vs for f in v.link_faces}],HIDE)
    k.box((-0.05,0,0.93),(1.45,0.85,0.05),WOOD,bevel=0.01); k.box((-0.05,0,1.33),(1.45,0.85,0.05),WOOD,bevel=0.01)
    _tube(k,(-0.75,0,1.08),(-1.25,0,1.02),0.05,IRON,8)
    k.box((0.2,0,1.9),(0.08,0.08,1.1),WOOD,bevel=0.01); _tube(k,(0.2,0,2.4),(1.1,0,2.25),0.035,WOOD,6)
    _tube(k,(0.6,0,1.36),(1.05,0,2.25),0.02,HIDE,4)
def smith_quench(k):
    _cyl(k,(0,0,0.3),0.42,0.38,0.6,16,WOOD)
    for z in (0.12,0.5): _cyl(k,(0,0,z),0.43,0.43,0.05,16,IRON)
    _cyl(k,(0,0,0.56),0.37,0.37,0.02,16,WATER)
    _tube(k,(0.15,-0.1,0.4),(0.35,0.25,0.95),0.02,IRON,6)
def smith_toolwall(k):
    """board of hanging tools for a wall (board plane y=-0.05, facing -Y)"""
    k.box((0,-0.04,1.6),(1.8,0.06,1.0),PLANKS,bevel=0.01)
    for i,x in enumerate((-0.7,-0.35,0.0,0.35,0.7)):
        k.box((x,-0.1,2.0),(0.03,0.1,0.03),WOOD,bevel=0)
        if i%2==0:
            k.box((x,-0.1,1.65),(0.035,0.03,0.6),WOOD,bevel=0); k.box((x,-0.1,1.37),(0.16,0.07,0.08),IRON,bevel=0.01)
        else:
            for sx in (-1,1): k.box((x+sx*0.04,-0.1,1.65),(0.025,0.025,0.65),IRON,rot=(0,sx*0.08,0),bevel=0)
    for x in (-0.55,0.55):
        ring(k,(x,-0.12,1.28),0.06,0.09,0.03,IRON,n=14,axis="Y")
def coal_pile(k):
    rnd=random.Random(8)
    for i in range(26):
        a=rnd.uniform(0,6.28); d=rnd.uniform(0,0.55)
        _mat(_ico(k,(math.cos(a)*d,math.sin(a)*d,0.05+0.3*(1-d/0.6)*rnd.uniform(0.5,1)),rnd.uniform(0.09,0.16),COAL,sub=1,jit=0.02,seed=i),COAL,False)
    k.box((0.75,0.1,0.25),(0.05,0.5,0.5),WOOD,rot=(0,0.3,0),bevel=0.01)
def smith_sign(k):
    """wall bracket (wall at y=0, arm to -Y) with a hanging iron anvil and crossed hammers"""
    k.box((0,-0.05,0),(0.12,0.1,0.5),IRON,bevel=0.01)
    k.box((0,-0.55,0.18),(0.05,1.05,0.05),IRON,bevel=0)
    _tube(k,(0,-0.05,-0.2),(0,-0.7,0.16),0.02,IRON,5)
    for y in (-0.35,-0.85): k.box((0,y,0.02),(0.015,0.015,0.28),IRON,bevel=0)
    k.box((0,-0.6,-0.18),(0.06,0.7,0.14),IRON,bevel=0.01); k.box((0,-0.6,-0.32),(0.06,0.3,0.16),IRON,bevel=0.01)
    k.box((0,-0.6,-0.45),(0.06,0.5,0.1),IRON,bevel=0.01); k.box((0,-0.98,-0.18),(0.06,0.18,0.08),IRON,rot=(0.3,0,0),bevel=0.01)
    for sg in (-1,1):
        k.box((0.02,-0.6,-0.72),(0.03,0.05,0.5),WOOD,rot=(sg*0.7,0,0),bevel=0)
        k.box((0.02,-0.6+sg*0.16,-0.55),(0.05,0.14,0.07),IRON,rot=(sg*0.7,0,0),bevel=0.01)
def inn_tankard(k):
    """foaming pewter tankard for the inn sign: base at z=0, axis +Z, handle to +Y; a smooth head of foam (cream
    cloth, smooth-shaded) spills over the rim with a drip down the -Y side"""
    y0=-0.05
    _cyl(k,(0,y0,0.02),0.2,0.2,0.04,20,STEEL)                                   # foot ring
    _cyl(k,(0,y0,0.22),0.185,0.168,0.38,20,STEEL)                               # body, slightly tapered
    for z,r in ((0.12,0.184),(0.31,0.176)): _cyl(k,(0,y0,z),r+0.01,r+0.01,0.035,20,IRON)   # hoops
    _cyl(k,(0,y0,0.415),0.176,0.176,0.03,20,STEEL)                              # lip
    c=(y0+0.17,0.22); R=0.12; pts=[]                                            # C handle on the +Y side
    for i in range(9):
        a=math.radians(-75+150*i/8); pts.append((0,c[0]+R*math.cos(a),c[1]+R*math.sin(a)))
    for a,b in zip(pts[:-1],pts[1:]): _tube(k,a,b,0.026,STEEL,8)
    for p in pts[1:-1]: _ico(k,p,0.026,STEEL,sub=1)
    _ico(k,(0,y0,0.45),1.0,CLOTH_B,scale=(0.19,0.2,0.08),sub=3)                   # foam: dome over the rim ...
    for (dy,z,r) in ((-0.1,0.49,0.085),(0.02,0.52,0.1),(0.12,0.48,0.075)): _ico(k,(0,y0+dy,z),r,CLOTH_B,sub=2)
    _ico(k,(0,y0-0.175,0.39),1.0,CLOTH_B,scale=(0.05,0.045,0.08),sub=2)          # ... and a drip over the edge
    _ico(k,(0,y0-0.182,0.305),0.034,CLOTH_B,sub=2)
def inn_sign(k):
    """big inn sign: scrolled iron bracket (wall y=0, arm to -Y, 1.9 m), gilded board with a foaming tankard, lantern"""
    k.box((0,-0.05,0.0),(0.14,0.1,0.8),IRON,bevel=0.01)
    k.box((0,-1.0,0.35),(0.06,1.95,0.06),IRON,bevel=0)
    _tube(k,(0,-0.05,-0.35),(0,-1.2,0.33),0.025,IRON,6)
    for i in range(8):                                                        # scroll
        a=i/7*math.pi*1.4; k.box((0,-0.55-0.18*math.cos(a),0.12+0.15*math.sin(a)),(0.03,0.06,0.06),IRON,bevel=0)
    for y in (-0.6,-1.5): k.box((0,y,0.2),(0.02,0.02,0.3),IRON,bevel=0)
    k.box((0,-1.05,-0.4),(0.1,1.25,0.9),WOOD,bevel=0.03)
    k.box((0,-1.05,-0.4),(0.12,1.35,1.0),BRONZE,bevel=0.02)
    k.box((0,-1.05,-0.4),(0.13,1.18,0.84),PLANKS,bevel=0.01)
    for sx in (-1,1):                                                          # tankard relief on both faces
        sub=Kit(); inn_tankard(sub)
        # an upright tankard seen side-on, squashed into a relief standing out of the board face
        M=Matrix.Translation((sx*0.063,-1.05,-0.74))@Matrix.Rotation(0 if sx>0 else math.pi,4,"Z")@Matrix.Diagonal((0.42,1,1,1))
        merge_kit(k,sub,M)
    k.box((0,-2.0,0.2),(0.02,0.02,0.3),IRON,bevel=0)                            # lantern at the arm tip
    k.box((0,-2.0,-0.05),(0.22,0.22,0.3),GLOW,bevel=0.01)
    for sx in (-1,1):
        for sy in (-1,1): k.box((sx*0.12,-2.0+sy*0.12,-0.05),(0.03,0.03,0.34),IRON,bevel=0)
    k.box((0,-2.0,0.13),(0.3,0.3,0.05),IRON,bevel=0.01); k.box((0,-2.0,-0.22),(0.28,0.28,0.04),IRON,bevel=0.01)
def ale_cask(k):
    """great ale cask lying in two saddle cradles, brass tap to -Y. Staves bulge smoothly (0.55 at the ends, 0.62 in
    the middle); the heads are boards, set just inside the stave ends"""
    zc=0.8; L=0.66
    rot=Matrix.Rotation(math.pi/2,4,"X")
    rad=lambda y: 0.55+0.07*(1.0-(y/L)**2)
    ys=[-L+2*L*i/8 for i in range(9)]
    for y0,y1 in zip(ys[:-1],ys[1:]): _cyl(k,(0,(y0+y1)/2,zc),rad(y1),rad(y0),y1-y0,20,WOOD,rot=rot)
    for y in (-0.58,-0.2,0.2,0.58): _cyl(k,(0,y,zc),rad(y)+0.012,rad(y)+0.012,0.05,20,IRON,rot=rot)
    for y in (-L,L): _cyl(k,(0,y,zc),0.5,0.5,0.02,20,PLANKS,rot=rot)
    # cradles across the cask: the top follows the staves (2 cm clear), the rest is a solid block to the ground
    for yc in (-0.4,0.4):
        r=rad(yc)+0.005; xs=0.47; zs=zc-math.sqrt(r*r-xs*xs)
        prof=[(-0.58,0.0),(0.58,0.0),(0.58,zs),(xs,zs)]
        for i in range(1,8):
            a=math.asin(xs/r)*(1-2*i/8); prof.append((r*math.sin(a),zc-r*math.cos(a)))
        prof.append((-xs,zs)); prof.append((-0.58,zs))
        fr=[k.bm.verts.new((x,yc-0.08,z)) for x,z in prof]; bk=[k.bm.verts.new((x,yc+0.08,z)) for x,z in prof]
        fs=[k.bm.faces.new(fr[::-1]),k.bm.faces.new(bk)]
        for i in range(len(prof)):
            j=(i+1)%len(prof); fs.append(k.bm.faces.new((fr[i],fr[j],bk[j],bk[i])))
        for f in fs: f.material_index=WOOD
        k.bm.normal_update(); k.project(fs,WOOD)
    zt=zc-0.25
    _tube(k,(0,-L,zt),(0,-0.85,zt),0.035,BRONZE,8); k.box((0,-0.86,zt-0.08),(0.05,0.05,0.14),BRONZE,bevel=0.01)
    _cyl(k,(0,-0.95,0.12),0.14,0.12,0.24,12,WOOD)
def weathervane(k):
    k.box((0,0,0.6),(0.05,0.05,1.2),IRON,bevel=0)
    for ax in ((0.5,0),(0,0.5)): k.box((0,0,0.85),(ax[0]*2+0.03,ax[1]*2+0.03,0.03),IRON,bevel=0)
    k.box((0,0,1.3),(0.9,0.03,0.04),BRONZE,bevel=0)
    k.box((0.45,0,1.3),(0.12,0.03,0.18),BRONZE,rot=(0,0.785,0),bevel=0)
    k.box((-0.4,0,1.35),(0.18,0.025,0.25),BRONZE,bevel=0)
    _mat(_ico(k,(0.02,0,1.55),0.17,BRONZE,scale=(1.3,0.15,1.0),sub=1),BRONZE,False)          # rooster
    k.box((0.2,0,1.72),(0.08,0.025,0.14),BRONZE,bevel=0); k.box((-0.18,0,1.66),(0.14,0.025,0.2),BRONZE,rot=(0,-0.5,0),bevel=0)
def hitch_rail(k):
    for sx in (-1,1): k.box((sx*1.1,0,0.55),(0.14,0.14,1.1),WOOD,bevel=0.02)
    k.box((0,0,1.02),(2.4,0.1,0.1),WOOD,bevel=0.02)
    ring(k,(0,-0.06,0.95),0.05,0.075,0.02,IRON,n=12,axis="Y")
    _cyl(k,(1.6,0.3,0.25),0.3,0.25,0.5,14,WOOD); _cyl(k,(1.6,0.3,0.47),0.26,0.26,0.02,14,WATER)
EXTRA_SPECS+=[("SM_VK_Smithy_Chimney",smithy_chimney,dict(wobble=False,grime=True)),
              ("SM_VK_Smithy_Canopy",smithy_canopy,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_Bellows",smith_bellows,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_QuenchTub",smith_quench,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_ToolWall",smith_toolwall,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_CoalPile",coal_pile,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_SmithSign",smith_sign,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_InnSign",inn_sign,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_AleCask",ale_cask,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_Weathervane",weathervane,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_HitchRail",hitch_rail,dict(wobble=False,grime=True))]

def _sub_origin(origin,lx,ly,rdeg=0.0):
    ox,oy,rz=origin; c,s_=math.cos(rz),math.sin(rz)
    return (ox+lx*c-ly*s_,oy+lx*s_+ly*c,rz+math.radians(rdeg))
def _new_objs(coll,fn):
    before=set(coll.all_objects); fn(); return [o for o in coll.all_objects if o not in before]
def build_smithy(coll,origin,seed=33,light=True):
    """landmark smithy: stone forge house (back), open workshop canopy (front, -Y), 9 m forge stack with a glowing
    hearth, bellows, anvil, quench tub, tool wall, coal, grindstone, weapon racks and a hanging anvil sign"""
    st={"ground":"Stone","plaster":"White","shutter":"Natural","roof":"Slate","stone":"Dark","window":"Lit","seed":seed}
    new=_new_objs(coll,lambda: build_house_v(coll,_sub_origin(origin,0,3),2,1,st,front="DW",back="..",chimney=False))
    def P(n,x,y,z=0.0,r=0.0,sty=None): return place_v(coll,n,x,y,z,r,origin,sty if sty is not None else {})
    P("SM_VK_Smithy_Canopy",0,-3,0,0,{"roof":"Slate"})
    P("SM_VK_Smithy_Chimney",-1.75,-1.05,0,0,{"stone":"Dark"})
    P("SM_VK_Prop_Bellows",0.2,-1.2,0,180)
    P("SM_VK_Prop_Anvil",0.35,-3.3,0,15)
    P("SM_VK_Prop_QuenchTub",1.55,-2.4,0,0)
    P("SM_VK_Prop_ToolWall",1.6,-0.02,0,0)
    P("SM_VK_Prop_CoalPile",-2.1,-3.2,0,0)
    P("SM_VK_Prop_Grindstone",2.2,-4.9,0,90)
    P("SM_VK_Prop_WeaponRack",-2.3,-5.3,0,0)
    P("SM_VK_Prop_Crates",3.9,-5.2,0,25)
    P("SM_VK_Prop_Woodpile",3.6,1.2,0,90)
    P("SM_VK_Prop_SmithSign",2.75,-6.0,2.9,90)
    P("SM_VK_Prop_Lantern",-2.75,-5.8,2.4,0)
    if light:
        L=bpy.data.lights.new("VK_Light_Forge","POINT"); L.energy=450; L.color=(1.0,0.45,0.15); L.shadow_soft_size=0.4
        o=bpy.data.objects.new("VK_Light_Forge",L); coll.objects.link(o)
        x,y,_=_sub_origin(origin,-1.75,-1.6); o.location=(x,y,1.3)
def build_inn(coll,origin,seed=34,garden=True):
    """landmark inn: three-storey timber-framed inn, lit windows, a big iron-bracket sign with a foaming tankard,
    ale cask, door lanterns, flower boxes, weathervane, hitching rail and a beer garden on the +X side"""
    st={"ground":"Stone","plaster":"Ochre","shutter":"Red","roof":"Red","window":"Lit","seed":seed}
    new=_new_objs(coll,lambda: build_house_v(coll,origin,3,3,st,front="WDW",back="W.W",chimney=True))
    def P(n,x,y,z=0.0,r=0.0,sty=None): return place_v(coll,n,x,y,z,r,origin,sty if sty is not None else {})
    P("SM_VK_Prop_InnSign",3.9,-3.3,4.1,0)
    for x in (-1.0,1.0): P("SM_VK_Prop_Lantern",x,-3.3,2.3,0)
    P("SM_VK_Prop_AleCask",-3.3,-4.5,0,90)             # clear of the front wall (outer face at y -3.8), tap to the door
    P("SM_VK_Prop_BarrelStack",-4.62,-4.8,0,90)        # beside the cask, clear of the corner (a neighbour's door may face it)
    P("SM_VK_Prop_HitchRail",3.0,-5.0,0,0)
    zs=[o.location.z+o.dimensions.z for o in new if o.type=="MESH" and "Roof" in o.name]
    top=max(zs) if zs else 10.0
    P("SM_VK_Prop_Weathervane",-2.0,0,top-origin_z(origin),0)
    if garden:
        for i,(x,y) in enumerate(((7.0,-1.2),(9.8,1.3))):
            P("SM_VK_Prop_Table",x,y,0,90)
            for dy in(-0.75,0.75):
                for dx in(-0.6,0.6): P("SM_VK_Prop_Stool",x+dy*1.1,y+dx,0,0)
        P("SM_VK_Prop_BarrelStack",10.3,-2.3,0,0)
        P("SM_VK_Prop_Festoon",7.9,-2.4,3.0,0); P("SM_VK_Prop_Festoon",7.9,2.6,3.0,0)
        for (x,y) in ((5.2,-2.6),(10.8,2.9)): P("SM_VK_Prop_LampPost",x,y,0,0)
        fence_run(coll,(4.8,3.3),(11.4,3.3),origin); fence_run(coll,(11.4,-3.3),(11.4,3.3),origin,gate_at=1)
def origin_z(origin): return 0.0
def build_barn(coll,origin,n=3,roof="Thatch"):
    L=n*CELL; st={"roof":roof}
    def P(nm,x,y,z,r,sty=st): place_v(coll,nm,x,y,z,r,origin,sty)
    for i in range(n):
        x=-L/2+1.5+3*i
        P("SM_VK_Wall_Barn_Door" if i==n//2 else "SM_VK_Wall_Barn",x,-3,0,0)
        P("SM_VK_Wall_Barn",x,3,0,180)
    for yy in(-1.5,1.5):
        P("SM_VK_Wall_Barn",-L/2,yy,0,-90); P("SM_VK_Wall_Barn",L/2,-yy,0,90)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): P("SM_VK_Corner_Barn",cx,cy,0,r)
    for i in range(n):
        x=-L/2+1.5+3*i
        if roof=="Thatch":
            if i==0: P("SM_VK_RoofThatch_Gable_Planks",x,0,HB,180)
            elif i==n-1: P("SM_VK_RoofThatch_Gable_Planks",x,0,HB,0)
            else: P("SM_VK_RoofThatch_Mid",x,0,HB,0)
        else:
            if i==0: P("SM_VK_Roof_Gable_Planks",x,0,HB,180)
            elif i==n-1: P("SM_VK_Roof_Gable_Planks",x,0,HB,0)
            else: P("SM_VK_Roof_Mid",x,0,HB,0)
    P("SM_VK_LeanTo_Thatch",-L/2+1.5,3,0,180,{})
    P("SM_VK_Prop_Haystack",L/2+3.0,2.0,0,0,{}); P("SM_VK_Prop_HayBale",L/2+2.2,-2.4,0,20,{})
    P("SM_VK_Prop_HayBale",-2.5,-4.6,0,-10,{}); P("SM_VK_Prop_Cart",2.2,-5.2,0,-20,{})
    P("SM_VK_Prop_Trough",-L/2-1.6,-1.0,0,90,{})
    fence_run(coll,(-L/2-3.5,-6.5),(-L/2-3.5,4.0),origin); fence_run(coll,(-L/2-3.5,4.0),(-L/2+0.0,7.0),origin)
def build_windmill(coll,origin):
    place_v(coll,"SM_VK_Windmill",0,0,0,0,origin,{})
    o=place_v(coll,"SM_VK_Windmill_Sails",0,-2.2-0.75,8.5+1.6,0,origin,{})
    o["spin_axis"]="local Y"
    place_v(coll,"SM_VK_Prop_Sacks",1.8,-3.6,0,0,origin,{}); place_v(coll,"SM_VK_Prop_Cart",-2.6,-4.4,0,15,origin,{})
def build_guardtower(coll,origin):
    place_v(coll,"SM_VK_GuardTower",0,0,0,0,origin,{})
    place_v(coll,"SM_VK_Prop_WeaponRack",2.9,-1.2,0,90,origin,{})
    place_v(coll,"SM_VK_Prop_BarrelStack",-2.7,-1.8,0,90,origin,{})

exec(bpy.data.texts["vk_mat"].as_string())
_tex_mat_legacy=tex_mat
def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False,tint=None):
    m=bpy.data.materials.get(name)
    if m: return m
    if img and bpy.data.images.get(img+"_BC"):
        m=bpy.data.materials.new(name); return pbr_material(m,img,tint=tint)
    if img and img.startswith("T_VK_") and bpy.data.images.get(img.replace("T_VK_Wood","T_VK_Wood")+"_BC"):
        m=bpy.data.materials.new(name); return pbr_material(m,img,tint=tint)
    return _tex_mat_legacy(name,img,rough,flat,emit,alpha_clip,tint)

# =====================  DETAIL PASS (overrides)  =====================
def rock(k,c,size,seed,rot_z=0.0,tilt=0.12,mi=None,segs=2):
    rnd=random.Random(seed)
    k.box(c,size,STONE_BLOCK if mi is None else mi,rot=(rnd.uniform(-tilt,tilt),rnd.uniform(-tilt,tilt),rot_z+rnd.uniform(-0.12,0.12)),
          bevel=min(size)*0.3,segs=segs,jitter=min(size)*0.13,seed=seed)
def plinth(k,x0=-1.5,x1=1.5,face=-0.25,seed=None):
    """chunky foundation rocks along the wall base (replaces the plain plinth)"""
    rnd=random.Random(int((x0*13+x1*7)*100) if seed is None else seed)
    k.box(((x0+x1)/2,-0.02,0.14),(x1-x0,0.5,0.28),STONE,bevel=0)
    x=x0
    while x<x1-0.12:
        w=min(rnd.uniform(0.42,0.8),x1-x)
        if x1-(x+w)<0.3: w=x1-x
        h=rnd.uniform(0.34,0.5); d=rnd.uniform(0.3,0.42)
        rock(k,(x+w/2,face+0.02,h/2-0.07),(w-0.06,d,h),seed=rnd.randrange(1<<30))
        x+=w
_STONE_META=None
def stone_meta():
    global _STONE_META
    if _STONE_META is None:
        import json
        img=bpy.data.images.get("T_VK_Stone_BC")
        p=os.path.join(os.path.dirname(bpy.path.abspath(img.filepath_raw)),"T_VK_Stone_stones.json")
        try: _STONE_META=json.load(open(p))
        except Exception: _STONE_META=[]
    return _STONE_META
def wall_rocks(k,x0,x1,z0,z1,face=-0.25,n=5,seed=0,avoid=()):
    """pop-out stones aligned with painted stones of T_VK_Stone (module at UV offset 0, facing -Y)"""
    rnd=random.Random(seed); meta=list(stone_meta()); rnd.shuffle(meta); placed=0
    for st in meta:
        if placed>=n: break
        for zoff in (0.0,3.0):
            x=((-3.0*st["u"]+1.5)%3.0)-1.5; z=3.0*st["v"]+zoff; w,h=st["w"],st["h"]
            if not (x0+0.05<x-w/2 and x+w/2<x1-0.05 and z0+0.02<z-h/2 and z+h/2<z1-0.05): continue
            if any(ax0-0.1<x+w/2 and x-w/2<ax1+0.1 and az0-0.1<z+h/2 and z-h/2<az1+0.1 for (ax0,ax1,az0,az1) in avoid): continue
            d=rnd.uniform(0.06,0.10)
            rock(k,(x,face-d/2+0.03,z),(0.9*w,d,0.9*h),seed=seed*31+placed,tilt=0.02,segs=1)
            placed+=1; break
def wall_stone_plain(k):
    stone_panel(k,-1.5,1.5,0,H1); plinth(k); batter(k)
    wall_rocks(k,-1.5,1.5,0.5,H1,n=2,seed=3)
def wall_stone_window(k):
    x0,x1,z0,z1=-0.55,0.55,1.05,2.25
    stone_panel(k,-1.5,x0,0,H1); stone_panel(k,x1,1.5,0,H1)
    stone_panel(k,x0,x1,0,z0); stone_panel(k,x0,x1,z1,H1)
    plinth(k); batter(k); window_frame(k,x0,x1,z0,z1)
    rock(k,(0,-0.3,z1+0.42),(1.5,0.22,0.3),seed=77,tilt=0.02)      # stone lintel
    wall_rocks(k,-1.5,1.5,0.5,H1,n=1,seed=5,avoid=((x0-0.6,x1+0.6,z0-0.3,z1+0.6),))
_wall_stone_door_base=wall_stone_door
def wall_stone_door(k):
    _wall_stone_door_base(k)
    wall_rocks(k,-1.5,1.5,0.5,H1,n=1,seed=7,avoid=((-1.15,1.15,0,3.0),))
    # studs on the door straps
    for zz in (0.45,1.55):
        for i in range(9):
            k.box((-0.56+i*0.14,-0.075,zz),(0.045,0.035,0.045),IRON,bevel=0.012)
def corner_stone(k):
    k.box((0,0,H1/2),(0.8,0.8,H1),STONE,bevel=0)
    rock(k,(-0.05,-0.05,0.18),(1.05,1.05,0.42),seed=11,tilt=0.03)
    z=0.36; i=0; rnd=random.Random(5)
    while z<H1-0.05:
        h=min(rnd.uniform(0.38,0.5),H1-z)
        long_x=(i%2==0)
        sx,sy=(1.05,0.62) if long_x else (0.62,1.05)
        rock(k,(-0.43+sx/2,-0.43+sy/2,z+h/2),(sx,sy,h-0.03),seed=i*17+3,tilt=0.02,segs=2)
        z+=h; i+=1
def pegs(k,xs,zs,y=-0.44,r=0.028):
    for x in xs:
        for z in zs: _cyl(k,(x,y,z),r,r*0.85,0.04,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
_timber_frame_base=timber_frame
def timber_frame(k,window=False,pattern="V"):
    _timber_frame_base(k,window,pattern)
    xs=(-1.5,-0.72,0.72) if window else ((-1.5,0.0) if pattern!="K" else (-1.5,-0.75,0.0,0.75))
    pegs(k,xs,(0.42,H2-0.33))
    k.box((0,-0.42,0.02),(CELL,0.1,0.06),WOOD,bevel=0.02)   # drip moulding under the jetty beam
def eave_tabs(k,x0,x1,side,rows=2,L=0.46,th=0.065,w=0.5,seed=0):
    rnd=random.Random(seed+int(x0*10)+side)
    ck,sk=math.cos(KICK),math.sin(KICK)
    X=Vector((1,0,0)); D=Vector((0,side*ck,-sk)); N=Vector((0,side*sk,ck))
    def zsurf(ay): return roof_z(ay)
    NS=9
    for r in range(rows):
        ay_top=EAVE+0.09-L-r*L*0.52
        base=Vector((0,side*ay_top,zsurf(ay_top)))
        start=x0 if r==0 else x0-w/2
        i=0
        while True:
            xa=start+i*w; i+=1
            if xa>=x1-1e-4: break
            ua=max(0.0,(x0-xa)/w); ub=min(1.0,(x1-xa)/w)
            if ub-ua<0.05: continue
            c=rnd.randrange(6); jz=rnd.uniform(-0.01,0.012); jy=rnd.uniform(-0.03,0.03)
            us=[ua+(ub-ua)*j/(NS-1) for j in range(NS)]
            def bot(u): return L-0.125*(1-math.sqrt(max(0.0,1-(2*u-1)**2)))+jy
            lift0=0.01+(th*0.85 if r>0 else 0.0)*0.0
            def P(u,yl,zl):
                zz=zl+0.012+(th*0.9*(yl/L) if r>0 else 0.0)+jz
                return base+X*(xa+u*w)+D*yl+N*zz
            top=[k.bm.verts.new(P(u,0.0,th)) for u in us]+[k.bm.verts.new(P(u,bot(u),th)) for u in reversed(us)]
            btm=[k.bm.verts.new(P(u,0.0,0.0)) for u in us]+[k.bm.verts.new(P(u,bot(u),0.0)) for u in reversed(us)]
            n=len(top)
            ft=k.bm.faces.new(top); fb=k.bm.faces.new(list(reversed(btm)))
            sides=[k.bm.faces.new((top[j],btm[j],btm[(j+1)%n],top[(j+1)%n])) for j in range(n)]
            k.bm.normal_update()
            if ft.normal.dot(N)<0:
                for f in [ft,fb]+sides: f.normal_flip()
            uvs=[((c+u)/6.0,1.0-0.0) for u in us]+[((c+u)/6.0,1.0-0.118*bot(u)/L) for u in reversed(us)]
            for f in [ft,fb]+sides:
                f.material_index=ROOF
            for l in ft.loops: l[k.uv].uv=uvs[top.index(l.vert)]
            for l in fb.loops: l[k.uv].uv=uvs[btm.index(l.vert)]
            for f in sides:
                for l in f.loops:
                    j=top.index(l.vert) if l.vert in top else btm.index(l.vert)
                    l[k.uv].uv=(uvs[j][0],uvs[j][1]-(0.004 if l.vert in btm else 0.0))
def ridge(k,x0,x1):
    n=max(1,int(round((x1-x0)/0.5)))
    for i in range(n):
        xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n; xm=(xa+xb)/2
        _cyl(k,(xm,0,RIDGE+0.04+roof_sag(xm,0)),0.21,0.175,xb-xa+0.06,10,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
def roof_mid(k):
    for s in(-1,1): roof_slab(k,-1.5,1.5,s); eave_tabs(k,-1.5,1.5,s)
    ridge(k,-1.5,1.5)
def roof_gable(k):
    for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
    ridge(k,-1.5,GX+0.1); gable_end(k)
def roof_gable_kind(kind):
    def fn(k):
        for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
        ridge(k,-1.5,GX+0.1); gable_end(k,kind)
    return fn
_roof_L_corner_base=roof_L_corner
def roof_L_corner(k):
    _roof_L_corner_base(k)
    GO=-HALF-(GX-1.5)
    eave_tabs(k,GO,3.0,-1)
def chimney(k):
    y0=1.3
    k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STONE,bevel=0.06,segs=2,tile=1.8)
    rock(k,(0,y0,RIDGE+1.55),(1.25,1.25,0.22),seed=21,tilt=0.02)
    rock(k,(0,y0,RIDGE+1.0),(1.12,1.12,0.16),seed=22,tilt=0.01,segs=1)
    for dx in(-0.22,0.22):
        zb=RIDGE+1.66
        _cyl(k,(dx,y0,zb+0.22),0.15,0.115,0.44,12,CLAY)
        _cyl(k,(dx,y0,zb+0.47),0.145,0.145,0.07,12,CLAY)
        _cyl(k,(dx,y0,zb+0.505),0.1,0.1,0.01,10,VOID)

# =====================  TOWN-HALL PIECES  =====================
def arch_ring(k,hw,spring,y_front,y_back,mi=STONE_BLOCK,n=9,depth_out=0.08,seed=0):
    rnd=random.Random(seed)
    for i in range(n):
        a=math.pi*(i+0.5)/n; r=hw+0.19
        ks=(i==n//2)
        k.box((math.cos(a)*r,(y_front+y_back)/2-depth_out/2,spring+math.sin(a)*r),
              (0.3 if not ks else 0.36,(y_back-y_front)+depth_out,0.42 if not ks else 0.56),mi,
              rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2,jitter=0.012,seed=seed*10+i)
def arch_cut_panels(k,hw,spring,top,y0,y1,mi):
    z=spring
    while z<spring+hw-0.005:
        dz=0.07; zc=min(z+dz,spring+hw)
        c=math.sqrt(max(0.0,hw*hw-((z+zc)/2-spring)**2))
        for sgn in(-1,1): k.box((sgn*(c+hw)/2,(y0+y1)/2,(z+zc)/2),(hw-c+0.002,y1-y0,zc-z),mi,bevel=0)
        z=zc
    if top>spring+hw: stone_panel(k,-hw,hw,spring+hw,top,y0,y1,mi=mi)
def arch_soffit(k,hw,spring,y0,y1,mi,n=16):
    for i in range(n):
        a0=math.pi*i/n; a1=math.pi*(i+1)/n
        v=[k.bm.verts.new((math.cos(a)*hw,y,spring+math.sin(a)*hw)) for a,y in ((a0,y0),(a1,y0),(a1,y1),(a0,y1))]
        f=k.bm.faces.new(v); f.material_index=mi
        for l,(uu,vv) in zip(f.loops,((a0*hw,y0),(a1*hw,y0),(a1*hw,y1),(a0*hw,y1))): l[k.uv].uv=(uu/TILE.get(mi,1.0),vv/TILE.get(mi,1.0))
def wall_arcade(k,mi=ASHLAR):
    hw=0.95; spring=1.72; y0,y1=-0.3,0.2; D=2.6
    stone_panel(k,-1.5,-hw,0,H1,y0,y1,mi=mi); stone_panel(k,hw,1.5,0,H1,y0,y1,mi=mi)
    arch_cut_panels(k,hw,spring,H1,y0,y1,mi); arch_soffit(k,hw,spring,y0,y1,mi)
    arch_ring(k,hw,spring,y0,y1,seed=3)
    for sgn in(-1,1):
        k.box((sgn*(hw+0.12),-0.08,spring-0.09),(0.46,0.62,0.18),STONE_BLOCK,bevel=0.04,segs=2)      # impost
        rock(k,(sgn*(hw+0.26),-0.06,0.22),(0.6,0.66,0.44),seed=40+sgn,tilt=0.02)              # pier base
    k.box((0,-0.36,H1-0.12),(CELL,0.18,0.24),mi,bevel=0.04,segs=2)                            # string course
    # loggia behind the arch
    k.box((0,(y1+D)/2,0.04),(CELL,D-y1,0.08),mi,bevel=0)
    for x in (-1.5,1.5): k.box((x,(y1+D)/2,0.06),(0.02,D-y1,0.04),VOID,bevel=0)
    k.box((0,(y1+D)/2,H1-0.06),(CELL,D-y1,0.08),PLANKS,bevel=0)
    for x in (-1.1,-0.37,0.37,1.1): k.box((x,(y1+D)/2,H1-0.19),(0.16,D-y1,0.2),WOOD,bevel=0.03)
    # back (inner) facade: plaster with a door and a small window
    dx0,dx1,dz=-1.1,-0.1,2.2; wx0,wx1,wz0,wz1=0.35,1.05,1.0,2.0
    yb=D; yb1=D+0.2
    for (a,b,c,d) in ((-1.5,dx0,0,H1),(dx1,wx0,0,H1),(wx1,1.5,0,H1),(dx0,dx1,dz,H1),(wx0,wx1,0,wz0),(wx0,wx1,wz1,H1)):
        grid_cut(k,k.box(((a+b)/2,(yb+yb1)/2,(c+d)/2),(b-a,yb1-yb,d-c),PLASTER,bevel=0))
    for i in range(4):
        x=dx0+(i+0.5)*(dx1-dx0)/4; k.box((x,yb+0.1,dz/2),((dx1-dx0)/4-0.015,0.08,dz),PLANKS,bevel=0.01)
    for x in (dx0-0.07,dx1+0.07): k.box((x,yb-0.02,dz/2),(0.14,0.16,dz),WOOD,bevel=0.03)
    k.box(((dx0+dx1)/2,yb-0.02,dz+0.08),(dx1-dx0+0.3,0.18,0.16),WOOD,bevel=0.03)
    k.quad([(wx0,yb+0.06,wz0),(wx1,yb+0.06,wz0),(wx1,yb+0.06,wz1),(wx0,yb+0.06,wz1)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,1.0),(0,1.0)])
    for x in (wx0-0.06,wx1+0.06): k.box((x,yb-0.02,(wz0+wz1)/2),(0.12,0.14,wz1-wz0+0.1),WOOD,bevel=0.025)
    for z in (wz0-0.05,wz1+0.05): k.box(((wx0+wx1)/2,yb-0.03,z),(wx1-wx0+0.3,0.16,0.12),WOOD,bevel=0.025)
    # hanging lantern
    k.box((0,1.3,H1-0.45),(0.02,0.02,0.5),IRON,bevel=0)
    k.box((0,1.3,H1-0.82),(0.24,0.24,0.3),GLOW,bevel=0.03)
    k.box((0,1.3,H1-0.64),(0.32,0.32,0.06),IRON,bevel=0.015); k.box((0,1.3,H1-0.99),(0.28,0.28,0.05),IRON,bevel=0.015)
def balcony(k):
    y0=-0.43; D_=0.95; W_=2.3; zf=0.34
    k.box((0,y0-D_/2,zf),(W_,D_,0.1),PLANKS,bevel=0.02)
    for x in (-0.95,0.0,0.95):
        k.box((x,y0-D_/2,zf-0.12),(0.14,D_,0.14),WOOD,bevel=0.03)
        L=math.hypot(0.75,0.8); th=math.atan2(0.8,-0.75)
        k.box((x,y0-0.37,zf-0.55),(0.12,L,0.12),WOOD,rot=(th,0,0),bevel=0.03)
    zt=zf+0.95
    for x in (-W_/2+0.06,W_/2-0.06):
        for y in (y0-0.05,y0-D_+0.06): k.box((x,y,(zf+zt)/2+0.02),(0.12,0.12,zt-zf+0.06),WOOD,bevel=0.03)
    k.box((0,y0-D_+0.06,zt),(W_,0.12,0.1),WOOD,bevel=0.03)
    k.box((0,y0-D_+0.06,zf+0.14),(W_,0.08,0.08),WOOD,bevel=0.02)
    for sgn in(-1,1):
        k.box((sgn*(W_/2-0.06),y0-D_/2,zt),(0.12,D_,0.1),WOOD,bevel=0.03)
        k.box((sgn*(W_/2-0.06),y0-D_/2,zf+0.14),(0.08,D_,0.08),WOOD,bevel=0.02)
    n=int(W_/0.16)
    for i in range(1,n):
        x=-W_/2+i*W_/n; _cyl(k,(x,y0-D_+0.06,(zf+zt)/2+0.05),0.03,0.03,zt-zf-0.2,6,WOOD)
    for sgn in(-1,1):
        for j in range(1,5):
            y=y0-j*D_/5; _cyl(k,(sgn*(W_/2-0.06),y,(zf+zt)/2+0.05),0.03,0.03,zt-zf-0.2,6,WOOD)
    # flower pots on the rail
    for x in (-0.7,0.6):
        _cyl(k,(x,y0-D_+0.06,zt+0.12),0.1,0.13,0.18,10,CLAY)
        for j in range(5):
            _ico(k,(x+0.06*math.cos(j*1.3),y0-D_+0.06+0.06*math.sin(j*1.3),zt+0.28),0.07,PINK if j%2 else LEAF,sub=1)
def clock_face(k,c,r,y_off=0.0):
    n=28; cx,cy,cz=c
    ring=[k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*r,cy+y_off,cz+math.sin(2*math.pi*i/n)*r)) for i in range(n)]
    ctr=k.bm.verts.new((cx,cy+y_off,cz))
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[(i+1)%n])); f.material_index=CLOCK
        for l in f.loops:
            p=l.vert.co; l[k.uv].uv=(0.5-(p.x-cx)/(2*r)*0.94,0.5+(p.z-cz)/(2*r)*0.94)
    k.bm.normal_update()
def cupola(k):
    B=1.8; zb=RIDGE-1.4; zt=RIDGE+1.25
    grid_cut(k,k.box((0,0,(zb+zt)/2),(B,B,zt-zb),PLASTER,bevel=0))
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.06),sy*(B/2-0.06),(zb+zt)/2),(0.22,0.22,zt-zb),WOOD,bevel=0.04)
    k.box((0,0,zt+0.07),(B+0.36,B+0.36,0.18),WOOD,bevel=0.05,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2+0.02),zb+1.35),(B+0.1,0.12,0.14),WOOD,bevel=0.03)
        k.box((sgn*(B/2+0.02),0,zb+1.35),(0.12,B+0.1,0.14),WOOD,bevel=0.03)
    zc=RIDGE+0.42
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        clock_face(sub,(0,-B/2-0.07,zc),0.56)
        _cyl(sub,(0,-B/2-0.04,zc),0.64,0.64,0.07,28,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
        merge_kit(k,sub,R)
    # belfry
    zb2=zt+0.16; hb=1.15
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.12),sy*(B/2-0.12),zb2+hb/2),(0.2,0.2,hb),WOOD,bevel=0.04,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2-0.12),zb2+hb-0.08),(B,0.18,0.16),WOOD,bevel=0.03)
        k.box((sgn*(B/2-0.12),0,zb2+hb-0.08),(0.18,B,0.16),WOOD,bevel=0.03)
        k.box((0,sgn*(B/2-0.12),zb2+0.35),(B,0.1,0.08),WOOD,bevel=0.02)
        k.box((sgn*(B/2-0.12),0,zb2+0.35),(0.1,B,0.08),WOOD,bevel=0.02)
    k.box((0,0,zb2+0.02),(B-0.1,B-0.1,0.06),PLANKS,bevel=0)
    k.box((0,0,zb2+hb-0.3),(1.2,0.12,0.12),WOOD,bevel=0.03)
    _cyl(k,(0,0,zb2+hb-0.62),0.33,0.16,0.52,14,BRONZE); _cyl(k,(0,0,zb2+hb-0.9),0.36,0.36,0.06,14,BRONZE)
    # roof: flared pyramid + spire
    zr=zb2+hb
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(B+0.7)/math.sqrt(2),radius2=0.04,depth=2.1)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zr+1.05))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.8)
    k.box((0,0,zr+2.3),(0.1,0.1,1.0),BRONZE,bevel=0.02)
    _ico(k,(0,0,zr+2.25),0.13,BRONZE,sub=1)
    k.box((0,0,zr+2.62),(0.9,0.04,0.04),IRON,bevel=0); k.box((0.42,0,zr+2.62),(0.12,0.03,0.18),IRON,rot=(0,0.785,0),bevel=0)
    k.box((-0.42,0,zr+2.66),(0.02,0.25,0.14),IRON,bevel=0)
EXTRA_SPECS+=[("SM_VK_Wall_Arcade",wall_arcade,dict(wobble=False,grime=True)),
              ("SM_VK_Balcony",balcony,dict(wobble=False,grime=False)),
              ("SM_VK_Roof_Cupola",cupola,dict(wobble=False,grime=False))]
# ---- multi-storey assembly (1..3 floors)
def _assemble(coll,origin,walls,corners,stories,style,r):
    gw,gc=_pieces(style)
    for (x,y,rot,c) in walls:
        if c=="A": place_v(coll,"SM_VK_Wall_Arcade",x,y,0,rot,origin,style); continue
        place_v(coll,gw[c],x,y,0,rot,origin,style); _dress(coll,origin,x,y,rot,c,r,style)
    for (x,y,rot) in corners: place_v(coll,gc,x,y,0,rot,origin,style)
    for lvl in range(1,stories):
        z=H1+H2*(lvl-1)
        for (x,y,rot,c) in walls:
            uc="W" if (c in "WDA" or r.random()<0.35) else "."
            place_v(coll,_upper(r,uc),x,y,z,rot,origin,style)
        for (x,y,rot) in corners: place_v(coll,"SM_VK_Corner_Timber",x,y,z,rot,origin,style)
def roof_top(stories): return H1+H2*(stories-1)

def build_townhall(coll,origin,n=5,roof="Blue",seed=55):
    st={"ground":"Stone","plaster":"White","shutter":"Blue","roof":roof,"seed":seed}
    r=random.Random(seed); L=n*CELL
    walls=[(-L/2+1.5+3*i,-3,0,"A") for i in range(n)]
    walls+=[(-L/2+1.5+3*i,3,180,"W" if i!=n//2 else "D") for i in range(n)]
    walls+=[(-L/2,-1.5,-90,"."),(-L/2,1.5,-90,"W"),(L/2,1.5,90,"W"),(L/2,-1.5,90,".")]
    corners=[(-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)]
    gw,gc=_pieces(st)
    for (x,y,rot,c) in walls:
        if c=="A": place_v(coll,"SM_VK_Wall_Arcade",x,y,0,rot,origin,st)
        else: place_v(coll,gw[c],x,y,0,rot,origin,st)
    for (x,y,rot) in corners: place_v(coll,gc,x,y,0,rot,origin,st)
    for lvl in (1,2):
        z=H1+H2*(lvl-1)
        for (x,y,rot,c) in walls:
            if y==-3: pc="SM_VK_Wall_Timber_Window"
            elif c==".": pc=["SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K"][lvl-1]
            else: pc="SM_VK_Wall_Timber_Window" if (lvl==1 or r.random()<0.6) else "SM_VK_Wall_Timber"
            place_v(coll,pc,x,y,z,rot,origin,st)
        for (x,y,rot) in corners: place_v(coll,"SM_VK_Corner_Timber",x,y,z,rot,origin,st)
    place_v(coll,"SM_VK_Balcony",0,-3,H1,0,origin,st)
    top=roof_top(3)
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==0: place_v(coll,"SM_VK_Roof_Gable",x,0,top,180,origin,st)
        elif i==n-1: place_v(coll,"SM_VK_Roof_Gable",x,0,top,0,origin,st)
        else: place_v(coll,"SM_VK_Roof_Mid",x,0,top,0,origin,st)
    place_v(coll,"SM_VK_Roof_Cupola",0,0,top,0,origin,st)
    place_v(coll,"SM_VK_Chimney",-L/2+4.5,0,top,180,origin,st); place_v(coll,"SM_VK_Chimney",L/2-4.5,0,top,180,origin,st)
    # square in front
    place_v(coll,"SM_VK_Prop_NoticeBoard",-L/2-1.0,-5.0,0,15,origin,{})
    for x in (-L/2+0.2,L/2-0.2): place_v(coll,"SM_VK_Prop_LampPost",x,-4.2,0,0,origin,{})
    for x in (-4.5,4.5): place_v(coll,"SM_VK_Prop_Bench",x,-5.2,0,0,origin,{})

def ring(k,c,r_in,r_out,depth,mi,n=28,axis="Y"):
    """flat annulus with thickness; axis = normal direction of the ring face (Y: faces -Y)"""
    cx,cy,cz=c
    def P(r,a,d):
        if axis=="Y": return (cx+math.cos(a)*r,cy+d,cz+math.sin(a)*r)
        return (cx+math.cos(a)*r,cy+math.sin(a)*r,cz+d)
    fo=[];fi=[];bo=[];bi=[]
    for i in range(n):
        a=2*math.pi*i/n
        fo.append(k.bm.verts.new(P(r_out,a,-depth/2))); fi.append(k.bm.verts.new(P(r_in,a,-depth/2)))
        bo.append(k.bm.verts.new(P(r_out,a,depth/2))); bi.append(k.bm.verts.new(P(r_in,a,depth/2)))
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.append(k.bm.faces.new((fo[i],fo[j],fi[j],fi[i])))
        fs.append(k.bm.faces.new((bo[j],bo[i],bi[i],bi[j])))
        fs.append(k.bm.faces.new((fo[j],fo[i],bo[i],bo[j])))
        fs.append(k.bm.faces.new((fi[i],fi[j],bi[j],bi[i])))
    k.bm.normal_update()
    # make outward-facing: check front face normal against axis
    probe=fs[0].normal
    want=Vector((0,-1,0)) if axis=="Y" else Vector((0,0,-1))
    if probe.dot(want)<0:
        for f in fs: f.normal_flip()
    k.project(fs,mi)
    return fs
def cupola(k):
    B=1.8; zb=RIDGE-1.4; zt=RIDGE+1.25
    grid_cut(k,k.box((0,0,(zb+zt)/2),(B,B,zt-zb),PLASTER,bevel=0))
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.06),sy*(B/2-0.06),(zb+zt)/2),(0.22,0.22,zt-zb),WOOD,bevel=0.04)
    k.box((0,0,zt+0.07),(B+0.36,B+0.36,0.18),WOOD,bevel=0.05,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2+0.02),zb+0.75),(B+0.1,0.12,0.14),WOOD,bevel=0.03)
        k.box((sgn*(B/2+0.02),0,zb+0.75),(0.12,B+0.1,0.14),WOOD,bevel=0.03)
    zc=RIDGE+0.42
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        clock_face(sub,(0,-B/2-0.035,zc),0.5)
        ring(sub,(0,-B/2-0.05,zc),0.49,0.62,0.07,WOOD)
        for i in range(8):
            aa=2*math.pi*i/8+math.pi/8
            sub.box((math.cos(aa)*0.555,-B/2-0.095,zc+math.sin(aa)*0.555),(0.06,0.03,0.06),BRONZE,bevel=0.01)
        merge_kit(k,sub,R)
    zb2=zt+0.16; hb=1.15
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.12),sy*(B/2-0.12),zb2+hb/2),(0.2,0.2,hb),WOOD,bevel=0.04,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2-0.12),zb2+hb-0.08),(B,0.18,0.16),WOOD,bevel=0.03)
        k.box((sgn*(B/2-0.12),0,zb2+hb-0.08),(0.18,B,0.16),WOOD,bevel=0.03)
        k.box((0,sgn*(B/2-0.12),zb2+0.35),(B,0.1,0.08),WOOD,bevel=0.02)
        k.box((sgn*(B/2-0.12),0,zb2+0.35),(0.1,B,0.08),WOOD,bevel=0.02)
    k.box((0,0,zb2+0.02),(B-0.1,B-0.1,0.06),PLANKS,bevel=0)
    k.box((0,0,zb2+hb-0.3),(1.2,0.12,0.12),WOOD,bevel=0.03)
    bell(k,(0,0,zb2+hb-0.36),0.36)
    zr=zb2+hb
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(B+0.7)/math.sqrt(2),radius2=0.04,depth=2.1)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zr+1.05))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.8)
    k.box((0,0,zr+2.3),(0.1,0.1,1.0),BRONZE,bevel=0.02)
    _ico(k,(0,0,zr+2.25),0.13,BRONZE,sub=1)
    k.box((0,0,zr+2.62),(0.9,0.04,0.04),IRON,bevel=0); k.box((0.42,0,zr+2.62),(0.12,0.03,0.18),IRON,rot=(0,0.785,0),bevel=0)
    k.box((-0.42,0,zr+2.66),(0.02,0.25,0.14),IRON,bevel=0)
def bell(k,top,r):
    """proper bell profile (lathe), top = (x,y,z) of the crown"""
    prof=[(0.0,0.0),(0.34,0.0),(0.45,-0.08),(0.5,-0.3),(0.56,-0.62),(0.72,-0.9),(0.98,-1.02),(1.0,-1.1),(0.9,-1.1),(0.0,-1.0)]
    n=20; cx,cy,cz=top; rings=[]
    for (pr,pz) in prof:
        rings.append([k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*pr*r,cy+math.sin(2*math.pi*i/n)*pr*r,cz+pz*r*1.3)) for i in range(n)])
    fs=[]
    for a,b in zip(rings[:-1],rings[1:]):
        for i in range(n):
            j=(i+1)%n; fs.append(k.bm.faces.new((a[i],a[j],b[j],b[i])))
    k.bm.normal_update()
    for f in fs: f.material_index=BRONZE; f.smooth=True
    # make normals point outward (away from axis) for the outer shell
    for f in fs:
        c=f.calc_center_median(); out=Vector((c.x-cx,c.y-cy,0))
        if out.length>1e-4 and f.normal.dot(out)<0 and f.calc_area()>0: pass
    k.project(fs,BRONZE)
    _cyl(k,(cx,cy,cz+0.08*r),0.12*r,0.12*r,0.18*r,8,IRON)

# =====================  THATCH ROOF SET  =====================
TRT=0.38
def _pnoise(x,seed=0.0):
    """periodic (3 m) smooth noise for thatch bumps"""
    return (0.5*math.sin(2*math.pi*x/3.0*2+seed)+0.3*math.sin(2*math.pi*x/3.0*5+1.7*seed+1.1)+0.2*math.sin(2*math.pi*x/3.0*11+2.3*seed+0.4))
def _new_faces_since(k,before):
    return [f for f in k.bm.faces if f.index==-1 or f not in before]
def thatch_slab(k,x0,x1,side,end_caps=(False,False)):
    global RT
    before=set(k.bm.faces); old=RT; RT=TRT
    try: roof_slab(k,x0,x1,side,end_caps)
    finally: RT=old
    for f in k.bm.faces:
        if f not in before: f.material_index=THATCH
def _kick_frame(side):
    ck,sk=math.cos(KICK),math.sin(KICK)
    D=Vector((0,side*ck,-sk)); N=Vector((0,side*sk,ck))
    return D,N
def thatch_eave_roll(k,x0,x1,side,seed=0.0):
    D,N=_kick_frame(side)
    Pt=Vector((0,side*EAVE,roof_z(EAVE)))
    C=Pt-N*(TRT/2)                    # centre of the roll = middle of slab thickness at the eave
    R=TRT/2+0.05
    nx=max(2,int(round((x1-x0)/0.2))); nt=10
    rings=[]
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx
        rr=R*(1+0.12*_pnoise(x,seed))
        row=[]
        for j in range(nt+1):
            th=math.pi/2-math.pi*j/nt               # +90 (top) -> -90 (bottom)
            p=C+Vector((x,0,0))+(D*math.cos(th)+N*math.sin(th))*rr-D*0.08
            row.append(k.bm.verts.new(p))
        rings.append(row)
    fs=[]
    for i in range(nx):
        for j in range(nt):
            f=k.bm.faces.new((rings[i][j],rings[i][j+1],rings[i+1][j+1],rings[i+1][j])); fs.append(f)
    k.bm.normal_update()
    probe=fs[len(fs)//2]
    if probe.normal.dot(D)<0:
        for f in fs: f.normal_flip()
    T=TILE[THATCH]
    for i in range(nx):
        for j in range(nt):
            f=fs[i*nt+j]; f.material_index=THATCH; f.smooth=True
            for l in f.loops:
                p=l.vert.co
                jj=[r_ for r_ in rings[i]+rings[i+1]].index(l.vert) if False else None
                l[k.uv].uv=(p.x/T,(0.02+0.06*((p-C).dot(N)+R)/(2*R))/1.0)
    return fs
def thatch_rake_roll(k,xg,seed=0.0):
    """rounded roll along the gable rake at x=xg (both slopes)"""
    prof=roof_profile()
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
        row=[]
        for j in range(nt+1):
            th=math.pi/2-math.pi*j/nt
            row.append(k.bm.verts.new(C+(X*math.cos(th)+Nn*math.sin(th))*rr))
        rings.append(row)
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
    # blobs where rake roll meets the eave roll
    for s_ in(-1,1):
        _ico(k,(xg-0.08,s_*(EAVE-0.05),roof_z(EAVE)-TRT/2),R*1.05,THATCH,sub=2,jit=0.02,seed=int(seed*10)+s_)
def thatch_ridge_cap(k,x0,x1):
    nx=max(2,int(round((x1-x0)/0.1))); ny=16
    grid_=[]
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx
        yend=0.78+0.16*(0.5-0.5*math.cos(2*math.pi*x/0.6))
        row=[]
        for j in range(ny+1):
            t=-1+2*j/ny; ay=abs(t)*yend
            thick=0.16*(1-abs(t)**5)+0.03
            z=roof_z(ay)+thick+0.02*(1-t*t)
            row.append(k.bm.verts.new((x,math.copysign(ay,t) if t!=0 else 0.0,z)))
        grid_.append(row)
    fs=[]
    for i in range(nx):
        for j in range(ny): fs.append(k.bm.faces.new((grid_[i][j],grid_[i+1][j],grid_[i+1][j+1],grid_[i][j+1])))
    # lips down to the roof on both sides
    for jside in (0,ny):
        for i in range(nx):
            a=grid_[i][jside]; b=grid_[i+1][jside]
            ay=abs(a.co.y); ay2=abs(b.co.y)
            a2=k.bm.verts.new((a.co.x,a.co.y,roof_z(ay)-0.02)); b2=k.bm.verts.new((b.co.x,b.co.y,roof_z(ay2)-0.02))
            fs.append(k.bm.faces.new((a,b,b2,a2)))
    k.bm.normal_update()
    for f in fs:
        if f.normal.z<-0.2 or (abs(f.normal.z)<0.5 and f.normal.y*f.calc_center_median().y<0): f.normal_flip()
        f.material_index=THATCH; f.smooth=True
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.x/1.2,0.1+abs(p.y)/1.2)
    # liggers + zigzag spars
    for s_ in(-1,1):
        for ay in (0.36,0.66):
            _cyl(k,((x0+x1)/2,s_*ay,roof_z(ay)+0.16*(1-(ay/0.8)**5)+0.035),0.028,0.028,x1-x0,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
        n=int(round((x1-x0)/0.3))
        for i in range(n):
            xa=x0+i*(x1-x0)/n; xb=xa+(x1-x0)/n
            ya,yb=(0.36,0.66) if i%2==0 else (0.66,0.36)
            pa=Vector((xa,s_*ya,roof_z(ya)+0.17*(1-(ya/0.8)**5)+0.03)); pb=Vector((xb,s_*yb,roof_z(yb)+0.17*(1-(yb/0.8)**5)+0.03))
            d=pb-pa; L=d.length; c=(pa+pb)/2
            q=Vector((1,0,0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
            sub=Kit(); _cyl(sub,(0,0,0),0.02,0.02,L,5,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
            merge_kit(k,sub,Matrix.Translation(c)@q)
def roof_thatch_mid(k):
    for s in(-1,1): thatch_slab(k,-1.5,1.5,s); thatch_eave_roll(k,-1.5,1.5,s,seed=1.0+s)
    thatch_ridge_cap(k,-1.5,1.5)
def roof_thatch_gable_kind(kind="timber"):
    def fn(k):
        for s in(-1,1): thatch_slab(k,-1.5,GX,s,end_caps=(False,True)); thatch_eave_roll(k,-1.5,GX,s,seed=1.0+s)
        thatch_ridge_cap(k,-1.5,GX+0.05)
        thatch_rake_roll(k,GX,seed=2.0)
        gable_end(k,kind,trim=False)
    return fn
EXTRA_SPECS+=[("SM_VK_RoofThatch_Mid",lambda k: roof_thatch_mid(k),dict(wobble=False,grime=False)),
              ("SM_VK_RoofThatch_Gable",lambda k: roof_thatch_gable_kind("timber")(k),dict(wobble=False,grime=False)),
              ("SM_VK_RoofThatch_Gable_Planks",lambda k: roof_thatch_gable_kind("planks")(k),dict(wobble=False,grime=False))]

# =====================  FOLIAGE CARDS  =====================
FOL_CELLS={"ivy":(0,0),"pink":(1,0),"daisy":(0,1),"grass":(1,1),"wheat":(0,0),"leafy":(1,0),"drygrass":(0,1),"lavender":(1,1)}
CROP_SET={"wheat","leafy","drygrass","lavender"}
def fol_uv(cell):
    cx,cy=FOL_CELLS[cell]; m=0.01
    return cx*0.5+m,cx*0.5+0.5-m,1-(cy*0.5+0.5)+m,1-cy*0.5-m
def card(k,center,right,up,w,h,cell,flip=False,bend=0.0):
    u0,u1,v0,v1=fol_uv(cell)
    if flip: u0,u1=u1,u0
    C=Vector(center); R=Vector(right).normalized(); U=Vector(up).normalized(); N=R.cross(U).normalized()
    vs=[];uvs=[]
    for j in range(3):
        for i in range(3):
            s_=i/2; t_=j/2
            p=C+R*(s_-0.5)*w+U*(t_-0.5)*h+N*bend*(1-(2*s_-1)**2)
            vs.append(k.bm.verts.new(p)); uvs.append((u0+(u1-u0)*s_,v0+(v1-v0)*t_))
    for j in range(2):
        for i in range(2):
            a=j*3+i; q=(a,a+1,a+4,a+3)
            f=k.bm.faces.new([vs[x] for x in q]); f.material_index=CROPS if cell in CROP_SET else FOLIAGE; f.smooth=True
            for l,x in zip(f.loops,q): l[k.uv].uv=uvs[x]
def ivy_patch(k,seed=0,x0=-1.4,x1=1.2,top=2.6,face=-0.32,n=46,base_w=1.6):
    rnd=random.Random(seed)
    # vines
    for vi in range(3):
        x=rnd.uniform(x0+0.3,x1-0.3); z=0.05
        pts=[(x,z)]
        while z<top*rnd.uniform(0.7,1.0):
            x+=rnd.uniform(-0.25,0.25); z+=rnd.uniform(0.2,0.35); pts.append((max(x0,min(x1,x)),z))
        for (xa,za),(xb,zb) in zip(pts[:-1],pts[1:]):
            d=Vector((xb-xa,0,zb-za)); L=d.length
            q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
            sub=Kit(); _cyl(sub,(0,0,0),0.022,0.018,L+0.02,5,WOOD)
            merge_kit(k,sub,Matrix.Translation(((xa+xb)/2,face-0.02,(za+zb)/2))@q)
    for i in range(n):
        # denser at bottom, narrowing with height
        z=top*(rnd.random()**1.4); spread=base_w*(1-0.55*z/top)
        cxm=(x0+x1)/2; x=cxm+rnd.uniform(-spread/2,spread/2)
        x=max(x0+0.15,min(x1-0.15,x))
        sz=rnd.uniform(0.38,0.62)
        ang=rnd.uniform(-0.6,0.6)
        R=Vector((math.cos(ang),0,math.sin(ang))); U=Vector((-math.sin(ang),0,math.cos(ang)))
        tilt=rnd.uniform(0.15,0.5)
        U=(U+Vector((0,-tilt,0))).normalized()
        card(k,(x,face-rnd.uniform(0.03,0.14),z+0.1),R,U,sz,sz,"ivy",flip=rnd.random()<0.5,bend=-0.05)
def deco_weeds(k,seed=0,x0=-1.5,x1=1.5,y=-0.48):
    rnd=random.Random(seed); x=x0+0.1
    while x<x1-0.1:
        w=rnd.uniform(0.35,0.6); h=w*rnd.uniform(0.7,1.0)
        cell="grass" if rnd.random()<0.75 else "daisy"
        for a in (0.0,math.pi/2.5):
            aa=a+rnd.uniform(-0.4,0.4)
            R=Vector((math.cos(aa),math.sin(aa),0)); card(k,(x,y+rnd.uniform(-0.12,0.08),h/2-0.03),R,(0,0,1),w,h,cell,flip=rnd.random()<0.5)
        x+=rnd.uniform(0.18,0.4)
def deco_bush(k,seed=0,r=0.7,flowers="pink"):
    rnd=random.Random(seed); n=40
    for i in range(n):
        zf=1-2*(i+0.5)/n; az=i*2.39996
        d=Vector((math.sqrt(max(0,1-zf*zf))*math.cos(az),math.sqrt(max(0,1-zf*zf))*math.sin(az),zf))
        if d.z<-0.5: continue
        c=Vector((0,0,r*0.8))+Vector((d.x*r,d.y*r,d.z*r*0.8))*rnd.uniform(0.55,0.95)
        up=(d+Vector((0,0,0.6))).normalized(); right=up.cross(Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1))).normalized()).normalized()
        cell="ivy" if (rnd.random()<0.65 or flowers is None) else flowers
        sz=rnd.uniform(0.5,0.75)*r*1.3
        card(k,c,right,up,sz,sz,cell,flip=rnd.random()<0.5,bend=0.06)
def prop_flowerbox(k,flowers="pink"):
    rnd=random.Random(4)
    k.box((0,0,0.12),(1.25,0.32,0.24),WOOD,bevel=0.03)
    for sx in(-0.45,0.45): k.box((sx,0.08,-0.1),(0.08,0.2,0.25),WOOD,bevel=0.02)
    k.box((0,0,0.235),(1.15,0.24,0.02),SOIL,bevel=0)
    for i in range(7):
        x=-0.5+i*(1.0/6)+rnd.uniform(-0.04,0.04)
        for a in (0.3,-0.9):
            aa=a+rnd.uniform(-0.3,0.3); R=Vector((math.cos(aa),math.sin(aa),0))
            h=rnd.uniform(0.34,0.46)
            card(k,(x,rnd.uniform(-0.05,0.05),0.22+h/2),R,(rnd.uniform(-0.15,0.15),-0.25,1),h*1.05,h,flowers if rnd.random()<0.8 else "ivy",flip=rnd.random()<0.5)
    # trailing ivy over the front edge
    for i in range(4):
        x=-0.45+i*0.3; card(k,(x,-0.2,0.1),(1,0,0),(0,-0.4,1),0.32,0.36,"ivy",flip=i%2==0)
def prop_planter(k,flowers="pink"):
    _cyl(k,(0,0,0.25),0.26,0.33,0.5,14,CLAY); _cyl(k,(0,0,0.51),0.35,0.35,0.06,14,CLAY)
    _cyl(k,(0,0,0.5),0.29,0.29,0.02,12,SOIL)
    rnd=random.Random(9)
    for i in range(6):
        aa=i*math.pi/3+rnd.uniform(-0.2,0.2); R=Vector((math.cos(aa),math.sin(aa),0))
        h=rnd.uniform(0.45,0.6); card(k,(0,0,0.48+h/2),R,(0,0,1),h,h,flowers if i%3 else "ivy",flip=i%2==0)
EXTRA_SPECS+=[("SM_VK_Deco_Ivy_A",lambda k: ivy_patch(k,1),dict(wobble=False,grime=True)),
              ("SM_VK_Deco_Ivy_B",lambda k: ivy_patch(k,2,x0=-1.45,x1=0.2,top=3.6,n=55,base_w=1.2),dict(wobble=False,grime=True)),
              ("SM_VK_Deco_Weeds",lambda k: deco_weeds(k,3),dict(wobble=False,grime=True)),
              ("SM_VK_Deco_Bush",lambda k: deco_bush(k,4),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_FlowerBox_Daisy",lambda k: prop_flowerbox(k,"daisy"),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_Planter",lambda k: prop_planter(k,"pink"),dict(wobble=False,grime=False))]

# =====================  FOUNTAIN / GRAVEYARD / LOW WALLS  =====================
def lathe(k,prof,center=(0,0,0),segs=16,mi=STONE_BLOCK,smooth_=False,cap_top=False):
    cx,cy,cz=center; rings=[]
    for (r,z) in prof:
        rings.append([k.bm.verts.new((cx+math.cos(2*math.pi*i/segs)*r,cy+math.sin(2*math.pi*i/segs)*r,cz+z)) for i in range(segs)])
    fs=[]
    for a,b in zip(rings[:-1],rings[1:]):
        for i in range(segs):
            j=(i+1)%segs; fs.append(k.bm.faces.new((a[i],a[j],b[j],b[i])))
    if cap_top:
        fs.append(k.bm.faces.new(rings[-1]))
    k.bm.normal_update()
    for f in fs:
        f.material_index=mi; f.smooth=smooth_
    k.project(fs,mi)
    return fs
def prop_fountain(k):
    R=2.0; n=8
    for i in range(n):
        a=2*math.pi*(i+0.5)/n; L=2*R*math.tan(math.pi/n)+0.06
        k.box((math.cos(a)*R,math.sin(a)*R,0.42),(0.34,L,0.72),ASHLAR,rot=(0,0,a),bevel=0.04,segs=2)
        k.box((math.cos(a)*(R+0.02),math.sin(a)*(R+0.02),0.84),(0.5,L+0.1,0.14),STONE_BLOCK,rot=(0,0,a),bevel=0.05,segs=2)
        a2=2*math.pi*i/n
        k.box((math.cos(a2)*(R+0.05),math.sin(a2)*(R+0.05),0.5),(0.44,0.44,0.95),STONE_BLOCK,rot=(0,0,a2),bevel=0.06,segs=2)
        k.box((math.cos(a2)*(R+0.05),math.sin(a2)*(R+0.05),1.0),(0.5,0.5,0.1),STONE_BLOCK,rot=(0,0,a2),bevel=0.04)
    # step ring
    for i in range(n):
        a=2*math.pi*(i+0.5)/n; L=2*(R+0.45)*math.tan(math.pi/n)+0.06
        k.box((math.cos(a)*(R+0.45),math.sin(a)*(R+0.45),0.08),(0.55,L,0.16),STONE_BLOCK,rot=(0,0,a),bevel=0.04)
    # basin floor + water
    oct_=[(math.cos(2*math.pi*(i+0.5)/n)*(R-0.1)/math.cos(math.pi/n),math.sin(2*math.pi*(i+0.5)/n)*(R-0.1)/math.cos(math.pi/n)) for i in range(n)]
    f=k.bm.faces.new([k.bm.verts.new((x,y,0.62)) for x,y in oct_]); f.material_index=WATER
    for l in f.loops: l[k.uv].uv=(l.vert.co.x/1.5,l.vert.co.y/1.5)
    f=k.bm.faces.new([k.bm.verts.new((x,y,0.12)) for x,y in oct_]); f.material_index=ASHLAR
    k.bm.normal_update()
    # central pedestal
    lathe(k,[(0.5,0.0),(0.5,0.3),(0.34,0.45),(0.28,0.9),(0.3,1.2),(0.42,1.3)],segs=12,mi=STONE_BLOCK)
    lathe(k,[(0.42,1.3),(0.95,1.42),(1.05,1.6),(0.98,1.66),(0.85,1.52),(0.2,1.5)],segs=16,mi=ASHLAR)
    lathe(k,[(0.86,1.55),(0.0,1.55)],segs=16,mi=WATER)
    lathe(k,[(0.2,1.5),(0.18,2.2),(0.3,2.3),(0.42,2.42),(0.44,2.5),(0.38,2.5),(0.1,2.45)],segs=12,mi=STONE_BLOCK)
    lathe(k,[(0.36,2.47),(0.0,2.47)],segs=12,mi=WATER)
    _ico(k,(0,0,2.72),0.16,BRONZE,sub=2)
    k.box((0,0,2.58),(0.08,0.08,0.2),BRONZE,bevel=0.02)
    # falling water from upper bowl (4 streams) + ripple rings
    for i in range(4):
        a=math.pi/4+i*math.pi/2
        pts=[]
        for j in range(9):
            t=j/8; r=1.0+t*0.55; z=1.62-t*t*1.02
            pts.append(Vector((math.cos(a)*r,math.sin(a)*r,z)))
        for pa,pb in zip(pts[:-1],pts[1:]):
            d=pb-pa; q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
            sub=Kit(); _cyl(sub,(0,0,0),0.055,0.05,d.length+0.02,8,WATER)
            merge_kit(k,sub,Matrix.Translation((pa+pb)/2)@q)
        ring(k,(math.cos(a)*1.55,math.sin(a)*1.55,0.64),0.1,0.2,0.02,WATER,n=12,axis="Z")
def grave_mound(k,rnd):
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=1.0)["verts"]
    for v in vs:
        v.co=Vector((v.co.x*0.45,v.co.y*0.95,max(v.co.z,-0.05)*0.18))+Vector((0,-0.95,0))
    fs=list({f for v in vs for f in v.link_faces})
    for f in fs: f.material_index=SOIL; f.smooth=True
    k.project(fs,SOIL)
    for i in range(5):
        x=rnd.uniform(-0.3,0.3); y=-0.95+rnd.uniform(-0.7,0.7)
        aa=rnd.uniform(0,3.14); card(k,(x,y,0.14),(math.cos(aa),math.sin(aa),0),(0,0,1),0.35,0.28,"grass" if i%2 else "daisy",flip=i%2==0)
def grave_a(k):
    rnd=random.Random(1)
    w,h,t=0.62,0.75,0.14
    outline=[(-w/2,0),(w/2,0)]+[(math.cos(math.pi*j/10)*w/2,h+math.sin(math.pi*j/10)*w/2) for j in range(11)]
    outline=[(w/2,0),(w/2,h)]+[(math.cos(math.pi*j/10)*w/2,h+math.sin(math.pi*j/10)*w/2) for j in range(1,10)]+[(-w/2,h),(-w/2,0)]
    front=[k.bm.verts.new((x,-t/2,z)) for x,z in outline]; back=[k.bm.verts.new((x,t/2,z)) for x,z in outline]
    fs=[k.bm.faces.new(list(reversed(front))),k.bm.faces.new(back)]
    n=len(outline)
    for i in range(n):
        j=(i+1)%n; fs.append(k.bm.faces.new((front[i],front[j],back[j],back[i])))
    k.bm.normal_update()
    if fs[0].normal.y>0:
        for f in fs: f.normal_flip()
    k.project(fs,STONE_BLOCK)
    geom=list(set(front+back)|{e for v in front+back for e in v.link_edges})
    bmesh.ops.bevel(k.bm,geom=[e for e in geom if isinstance(e,bmesh.types.BMEdge)],offset=0.025,segments=2,affect="EDGES",clamp_overlap=True)
    for v in front+back:
        if v.is_valid: v.co=Matrix.Rotation(0.07,3,"Y")@Matrix.Rotation(-0.05,3,"X")@v.co
    k.box((0,-0.09,0.72),(0.3,0.02,0.035),VOID,bevel=0); k.box((0,-0.09,0.66),(0.034,0.02,0.2),VOID,bevel=0)
    rock(k,(0,0,0.05),(0.8,0.3,0.14),seed=3,tilt=0.02,segs=1)
    grave_mound(k,rnd)
def grave_cross(k):
    rnd=random.Random(2)
    k.box((0,0,0.62),(0.16,0.14,1.22),STONE_BLOCK,bevel=0.03,segs=2)
    k.box((0,0,0.95),(0.62,0.14,0.16),STONE_BLOCK,bevel=0.03,segs=2)
    ring(k,(0,0,0.95),0.19,0.26,0.1,STONE_BLOCK,n=18,axis="Y")
    rock(k,(0,0,0.08),(0.5,0.4,0.2),seed=5,tilt=0.02,segs=1)
    grave_mound(k,rnd)
def grave_obelisk(k):
    rnd=random.Random(3)
    rock(k,(0,0,0.12),(0.7,0.7,0.26),seed=6,tilt=0.01,segs=1)
    k.box((0,0,0.35),(0.5,0.5,0.22),ASHLAR,bevel=0.03,segs=2)
    lathe(k,[(0.2,0.45),(0.16,1.5)],segs=4,mi=ASHLAR)
    lathe(k,[(0.16,1.5),(0.0,1.75)],segs=4,mi=ASHLAR)
    grave_mound(k,rnd)
def low_wall(k,L=CELL,seed=11):
    rnd=random.Random(seed); h=0.85
    k.box((0,0,h/2),(L,0.5,h),STONE,bevel=0)
    wall_rocks(k,-L/2,L/2,0.1,h,face=-0.25,n=2,seed=seed)
    sub=Kit(); wall_rocks(sub,-L/2,L/2,0.1,h,face=-0.25,n=2,seed=seed+1); merge_kit(k,sub,Matrix.Rotation(math.pi,4,"Z"))
    x=-L/2+0.02
    while x<L/2-0.05:
        w=min(rnd.uniform(0.14,0.22),L/2-x)
        hh=rnd.uniform(0.22,0.34)
        k.box((x+w/2,0,h+hh/2-0.03),(w-0.02,0.5,hh),STONE_BLOCK,rot=(0,rnd.uniform(-0.12,0.12),0),bevel=0.03,segs=1,jitter=0.015,seed=int(x*100)+seed)
        x+=w
    for sgn in(-1,1):
        xx=-L/2+0.2
        while xx<L/2-0.2:
            ww=rnd.uniform(0.4,0.7)
            rock(k,(min(xx+ww/2,L/2-ww/2),sgn*0.2,0.14),(ww-0.05,0.3,0.3),seed=int(xx*50)+sgn*7,tilt=0.03,segs=1)
            xx+=ww
def low_wall_post(k):
    rock(k,(0,0,0.25),(0.8,0.8,0.5),seed=21,tilt=0.02)
    rock(k,(0,0,0.72),(0.7,0.7,0.46),seed=22,tilt=0.02)
    rock(k,(0,0,1.1),(0.62,0.62,0.34),seed=23,tilt=0.02)
    lathe(k,[(0.4,1.26),(0.42,1.34),(0.0,1.46)],segs=4,mi=STONE_BLOCK)
def lychgate(k):
    """roofed gate for a low wall / graveyard, spans one 3 m cell"""
    for sx in(-1,1):
        rock(k,(sx*1.35,0,0.2),(0.55,0.55,0.4),seed=30+sx,tilt=0.01)
        for sy in(-1,1): k.box((sx*1.35,sy*0.55,1.45),(0.18,0.18,2.1),WOOD,bevel=0.04,segs=2)
        k.box((sx*1.35,0,2.45),(0.2,1.5,0.2),WOOD,bevel=0.04)
        k.box((sx*1.35,0,0.55),(0.12,1.1,0.12),WOOD,bevel=0.03)
        for sy in(-1,1): k.box((sx*1.35,sy*0.35,2.2),(0.1,0.5,0.1),WOOD,rot=(sy*0.8,0,0),bevel=0.02)
    for sy in(-1,1): k.box((0,sy*0.55,2.45),(3.0,0.18,0.2),WOOD,bevel=0.04)
    # roof along x, slopes to +-y
    run=1.25; rise=1.0; L=math.hypot(run,rise); ang=math.atan2(rise,run)
    for sy in(-1,1):
        k.box((0,sy*run/2,2.55+rise/2),(3.6,L+0.1,0.12),ROOF,rot=(-sy*ang,0,0),bevel=0.03)
        k.box((0,sy*(run+0.02),2.52),(3.62,0.1,0.18),WOOD,bevel=0.03)
    for sx in(-1,1):
        v=[k.bm.verts.new(p) for p in ((sx*1.45,-run,2.55),(sx*1.45,run,2.55),(sx*1.45,0,2.55+rise))]
        f=k.bm.faces.new(v if sx>0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    _cyl(k,(0,0,2.55+rise+0.06),0.13,0.13,3.6,8,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # gates (slightly open)
    for sx in(-1,1):
        sub=Kit()
        for i in range(5): sub.box((0.13+i*0.26,0,0.62),(0.1,0.05,0.95+0.06*math.sin(i/4*math.pi)),PLANKS,bevel=0.01)
        for z in(0.35,0.95): sub.box((0.65,-0.04,z),(1.3,0.06,0.1),WOOD,bevel=0.02)
        sub.box((0.65,-0.04,0.65),(1.35,0.05,0.08),WOOD,rot=(0,-0.45,0),bevel=0.01)
        M=Matrix.Translation((sx*1.25,0,0))@Matrix.Rotation(sx*0.35+(math.pi if sx>0 else 0),4,"Z")
        merge_kit(k,sub,M)
    k.box((0,0,0.04),(2.4,1.2,0.08),STONE_BLOCK,bevel=0.03)
EXTRA_SPECS+=[("SM_VK_Prop_Fountain",lambda k: prop_fountain(k),dict(wobble=False,grime=True)),
              ("SM_VK_Grave_A",lambda k: grave_a(k),dict(wobble=False,grime=True)),
              ("SM_VK_Grave_Cross",lambda k: grave_cross(k),dict(wobble=False,grime=True)),
              ("SM_VK_Grave_Obelisk",lambda k: grave_obelisk(k),dict(wobble=False,grime=True)),
              ("SM_VK_LowWall",lambda k: low_wall(k),dict(wobble=False,grime=True)),
              ("SM_VK_LowWall_Post",lambda k: low_wall_post(k),dict(wobble=False,grime=True)),
              ("SM_VK_LowWall_Lychgate",lambda k: lychgate(k),dict(wobble=False,grime=True))]

# =====================  FARM SET  =====================
def soil_bed(k,W=2.9,D=2.9,rows=7,ridge_h=0.12):
    k.box((0,0,0.03),(W,D,0.06),SOIL,bevel=0)
    for i in range(rows):
        y=-D/2+(i+0.5)*D/rows
        k.box((0,y,0.08),(W-0.1,D/rows*0.62,ridge_h),SOIL,bevel=0.05,segs=1,jitter=0.01,seed=i)
def crop_rows(k,cell,rows=7,per=8,h=(0.8,1.05),w=0.55,seed=0,W=2.9,D=2.9,z0=0.12):
    rnd=random.Random(seed)
    for i in range(rows):
        y=-D/2+(i+0.5)*D/rows
        for j in range(per):
            x=-W/2+(j+0.5)*W/per+rnd.uniform(-0.08,0.08)
            hh=rnd.uniform(*h)
            for a in (0.0,1.2,2.3):
                aa=a+rnd.uniform(-0.3,0.3)
                card(k,(x,y+rnd.uniform(-0.05,0.05),z0+hh/2-0.02),(math.cos(aa),math.sin(aa),0),(rnd.uniform(-0.1,0.1),rnd.uniform(-0.1,0.1),1),w*rnd.uniform(0.85,1.15),hh,cell,flip=rnd.random()<0.5)
def crop_wheat(k): soil_bed(k); crop_rows(k,"wheat",rows=7,per=9,seed=1)
def crop_carrot(k): soil_bed(k); crop_rows(k,"leafy",rows=7,per=10,h=(0.35,0.5),w=0.42,seed=2)
def crop_lavender(k): soil_bed(k,rows=5); crop_rows(k,"lavender",rows=5,per=7,h=(0.6,0.8),w=0.6,seed=3)
def crop_cabbage(k):
    soil_bed(k); rnd=random.Random(4)
    for i in range(7):
        y=-1.45+(i+0.5)*2.9/7
        for j in range(7):
            x=-1.45+(j+0.5)*2.9/7+rnd.uniform(-0.05,0.05)
            goods_map(k,_ico(k,(x,y,0.3),0.19,LEAF,(1,1,0.85),sub=1,jit=0.02,seed=i*9+j),"cabbage",ref=(math.cos(i+j),math.sin(i+j),0))
            for a in range(4):
                aa=a*1.57+rnd.uniform(-0.3,0.3)
                card(k,(x+math.cos(aa)*0.16,y+math.sin(aa)*0.16,0.24),(math.cos(aa+1.57),math.sin(aa+1.57),0),(math.cos(aa)*0.8,math.sin(aa)*0.8,0.6),0.3,0.3,"ivy",flip=a%2==0)
def pumpkin(k,c,r,seed=0):
    rnd=random.Random(seed); n=16; rings=[]
    prof=[(0.0,-1.0),(0.45,-0.92),(0.8,-0.62),(1.0,-0.1),(0.95,0.35),(0.7,0.72),(0.3,0.9),(0.0,0.82)]
    cx,cy,cz=c
    for (pr,pz) in prof:
        row=[]
        for i in range(n):
            a=2*math.pi*i/n; rib=1-0.07*abs(math.cos(4*a))
            row.append(k.bm.verts.new((cx+math.cos(a)*pr*r*rib,cy+math.sin(a)*pr*r*rib,cz+pz*r*0.75)))
        rings.append(row)
    fs=[]
    for a_,b_ in zip(rings[:-1],rings[1:]):
        for i in range(n): j=(i+1)%n; fs.append(k.bm.faces.new((a_[i],a_[j],b_[j],b_[i])))
    k.bm.normal_update()
    goods_map(k,fs,"pumpkin",c=c)                    # the atlas grooves (u = k/4) sit on the modelled ribs (a = k*pi/4)
    _cyl(k,(cx,cy,cz+r*0.75),0.035,0.025,0.16,6,LEAF)
def crop_pumpkin(k):
    soil_bed(k,rows=4); rnd=random.Random(5)
    for i in range(9):
        x=rnd.uniform(-1.2,1.2); y=rnd.uniform(-1.2,1.2); r=rnd.uniform(0.2,0.34)
        pumpkin(k,(x,y,0.12+r*0.72),r,seed=i)
    for i in range(26):
        x=rnd.uniform(-1.35,1.35); y=rnd.uniform(-1.35,1.35); aa=rnd.uniform(0,6.28)
        card(k,(x,y,0.2),(math.cos(aa),math.sin(aa),0),(0,0.3,1),0.45,0.35,"ivy",flip=i%2==0)
def scarecrow(k):
    k.box((0,0,1.1),(0.1,0.1,2.2),WOOD,bevel=0.02)
    k.box((0,0,1.65),(1.5,0.09,0.09),WOOD,bevel=0.02)
    _ico(k,(0,0,2.05),0.2,BURLAP,(1,0.9,1.1),sub=2,jit=0.01,seed=1)
    for sx in(-1,1): k.box((sx*0.07,-0.19,2.08),(0.05,0.02,0.05),VOID,bevel=0)
    k.box((0,-0.19,1.98),(0.14,0.02,0.02),VOID,bevel=0)
    lathe(k,[(0.36,2.2),(0.38,2.24),(0.18,2.26),(0.15,2.45),(0.05,2.55),(0.0,2.56)],segs=12,mi=HAY)
    k.box((0,0,1.5),(0.55,0.3,0.6),CLOTH_A,bevel=0.08,segs=2,jitter=0.02,seed=2)
    for sx in(-1,1):
        k.box((sx*0.45,0,1.62),(0.45,0.22,0.22),CLOTH_A,bevel=0.06,jitter=0.02,seed=3+sx)
        lathe(k,[(0.1,0.0),(0.02,-0.22)],center=(sx*0.7,0,1.62),segs=6,mi=HAY)
    k.box((0,0,1.12),(0.5,0.28,0.25),CLOTH_B,bevel=0.05,jitter=0.02,seed=5)
    for sx in(-0.1,0.1): lathe(k,[(0.08,0.0),(0.03,-0.25)],center=(sx,0,1.0),segs=6,mi=HAY)
    _ico(k,(0.35,-0.05,2.36),0.07,VOID,(1.4,1,0.8),sub=1)   # crow
def chicken(k,c=(0,0,0),rot=0.0,col=PAPER,seed=0):
    sub=Kit()
    _ico(sub,(0,0,0.26),0.16,col,(1.25,0.9,0.95),sub=2,seed=seed)
    _ico(sub,(0.17,0,0.42),0.08,col,sub=2)
    k_=sub
    lathe(k_,[(0.03,0.0),(0.0,0.07)],center=(0.24,0,0.42),segs=6,mi=YELLOW)
    k_.box((0.17,0,0.51),(0.08,0.02,0.05),APPLE,bevel=0.01); k_.box((0.215,0,0.385),(0.02,0.02,0.04),APPLE,bevel=0)
    k_.box((-0.2,0,0.36),(0.12,0.1,0.18),col,rot=(0,-0.5,0),bevel=0.03)
    for sy in(-0.05,0.05): k_.box((0.0,sy,0.07),(0.02,0.02,0.14),YELLOW,bevel=0)
    for f in sub.bm.faces:
        if f.material_index in (PAPER,PUMPKIN): f.smooth=True
    merge_kit(k,sub,Matrix.Translation(c)@Matrix.Rotation(rot,4,"Z"))
def chickens(k):
    rnd=random.Random(7)
    for i in range(5):
        chicken(k,(rnd.uniform(-1.2,1.2),rnd.uniform(-1.2,1.2),0),rnd.uniform(0,6.28),PAPER if i%3 else PUMPKIN,seed=i)
def chicken_coop(k):
    W,D=1.6,1.2; z0=0.55; hw=1.0
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(W/2-0.05),sy*(D/2-0.05),(z0+hw)/2+0.05),(0.1,0.1,z0+hw+0.1),WOOD,bevel=0.02)
    k.box((0,0,z0),(W,D,0.08),PLANKS,bevel=0.01)
    for sy in(-1,1): k.box((0,sy*(D/2-0.02),z0+hw/2),(W,0.05,hw),PLANKS,bevel=0.01)
    for sx in(-1,1): k.box((sx*(W/2-0.02),0,z0+hw/2),(0.05,D,hw),PLANKS,bevel=0.01)
    k.quad([(-0.2,-D/2-0.03,z0+0.05),(0.2,-D/2-0.03,z0+0.05),(0.2,-D/2-0.03,z0+0.5),(-0.2,-D/2-0.03,z0+0.5)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    # ramp
    L=math.hypot(1.0,z0); ang=math.atan2(z0,1.0)
    k.box((0,-D/2-0.5,z0/2),(0.4,L,0.04),PLANKS,rot=(-ang,0,0),bevel=0.01)
    for i in range(5): k.box((0,-D/2-0.1-i*0.18,z0-0.1-i*0.1),(0.4,0.03,0.03),WOOD,bevel=0)
    # nest box
    k.box((W/2+0.25,0,z0+0.35),(0.5,0.9,0.5),PLANKS,bevel=0.01)
    k.box((W/2+0.28,0,z0+0.68),(0.6,1.0,0.06),ROOF,rot=(0,0.35,0),bevel=0.01)
    # roof
    run=D/2+0.25; rise=0.55; L2=math.hypot(run,rise); a2=math.atan2(rise,run)
    for sy in(-1,1): k.box((0,sy*run/2,z0+hw+rise/2),(W+0.4,L2+0.05,0.07),ROOF,rot=(-sy*a2,0,0),bevel=0.02)
    for sx in(-1,1):
        v=[k.bm.verts.new(p) for p in ((sx*(W/2),-D/2,z0+hw),(sx*(W/2),D/2,z0+hw),(sx*(W/2),0,z0+hw+rise))]
        f=k.bm.faces.new(v if sx>0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    _cyl(k,(0,0,z0+hw+rise+0.04),0.06,0.06,W+0.4,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((0,0,0.05),(W+0.3,D+0.3,0.1),HAY,bevel=0.04,jitter=0.03,seed=9)
EXTRA_SPECS+=[("SM_VK_Crop_Wheat",lambda k: crop_wheat(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Carrot",lambda k: crop_carrot(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Lavender",lambda k: crop_lavender(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Cabbage",lambda k: crop_cabbage(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Pumpkin",lambda k: crop_pumpkin(k),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_Scarecrow",lambda k: scarecrow(k),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_Chickens",lambda k: chickens(k),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_ChickenCoop",lambda k: chicken_coop(k),dict(wobble=False,grime=True))]

# =====================  BAKERY / STABLE  =====================
def bread_oven(k):
    """domed bread oven with its own little roof; attaches to a wall (wall-local, outer side -Y)"""
    y0=-0.3; yc=y0-1.0
    k.box((0,yc,0.45),(1.9,1.7,0.9),STONE,bevel=0.03,segs=1)
    wall_rocks(k,-0.95,0.95,0.1,0.9,face=yc-0.85,n=3,seed=12)
    k.box((0,yc,0.93),(2.0,1.8,0.1),STONE_BLOCK,bevel=0.03,segs=1)
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=3,radius=1.0)["verts"]
    for v in vs:
        v.co=Vector((v.co.x*0.82,v.co.y*0.72,max(v.co.z,0.0)*0.78))+Vector((0,yc,0.97))
    fs=list({f for v in vs for f in v.link_faces})
    for f in fs: f.material_index=CLAY; f.smooth=True
    k.project(fs,CLAY)
    # mouth: arched opening on the front
    hw=0.28; zs=1.02; ym=yc-0.73
    pts=[(-hw,zs),(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+0.18+math.sin(math.pi*j/8)*hw) for j in range(9)]
    pts=[(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+0.18+math.sin(math.pi*j/8)*hw) for j in range(9)]+[(-hw,zs)]
    vv=[k.bm.verts.new((x,ym,z)) for x,z in pts]; f=k.bm.faces.new(vv); f.material_index=VOID
    k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    arch_ring_small=[(math.cos(math.pi*(j+0.5)/7)*(hw+0.08),zs+0.18+math.sin(math.pi*(j+0.5)/7)*(hw+0.08)) for j in range(7)]
    for j,(x,z) in enumerate(arch_ring_small):
        a=math.pi*(j+0.5)/7
        k.box((x,ym-0.03,z),(0.12,0.16,0.16),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.02)
    k.box((0,ym-0.1,zs-0.03),(0.8,0.3,0.08),STONE_BLOCK,bevel=0.02)
    _ico(k,(0,ym+0.1,zs+0.12),0.1,GLOW,(1.6,1,0.5),sub=1)
    # iron door leaning, peel, flue
    k.box((0.62,ym-0.12,0.72+0.5),(0.5,0.05,0.5),IRON,rot=(0.25,0,0.3),bevel=0.02)
    _cyl(k,(0,yc+0.45,1.55),0.12,0.1,0.8,10,CLAY)
    _cyl(k,(0,yc+0.45,1.97),0.15,0.15,0.08,10,CLAY)
    k.box((-0.9,ym-0.35,1.0),(0.05,0.05,2.0),WOOD,rot=(0.25,0,0),bevel=0)
    k.box((-0.9,ym-0.58,0.1),(0.3,0.03,0.24),WOOD,rot=(0.25,0,0),bevel=0.01)
    # shelter roof on posts
    for x in (-1.1,1.1):
        k.box((x,yc-0.9,1.25),(0.16,0.16,2.5),WOOD,bevel=0.03)
    k.box((0,yc-0.9,2.45),(2.5,0.18,0.18),WOOD,bevel=0.03)
    L=math.hypot(1.4,0.5); ang=math.atan2(0.5,1.4)
    k.box((0,yc-0.35,2.72),(2.7,L+0.2,0.1),ROOF,rot=(ang,0,0),bevel=0.03)
    for x in (-1.1,1.1): k.box((x,yc-0.5,2.3),(0.12,0.6,0.12),WOOD,rot=(-0.7,0,0),bevel=0.02)
    # firewood under the oven
    for i in range(6):
        _cyl(k,(-0.55+i*0.22,yc-0.55,0.1+0.18*(i%2)),0.09,0.09,0.7,6,BREAD if i%3==0 else WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
def bread_rack(k):
    for sx in(-0.7,0.7):
        for sy in(-0.2,0.2): k.box((sx,sy,0.9),(0.07,0.07,1.8),WOOD,bevel=0.015)
    for z in (0.4,0.9,1.4):
        k.box((0,0,z),(1.5,0.5,0.05),PLANKS,bevel=0.01)
        for i in range(6):
            x=-0.6+i*0.24
            goods_map(k,_ico(k,(x,0,z+0.08),0.1,BREAD,(1.2 if i%2 else 0.9,0.8,0.55),sub=2),"bread")
    k.box((0,0.23,1.85),(1.5,0.05,0.12),WOOD,bevel=0.01)
def bakery_sign(k):
    k.box((0,0.03,0),(0.16,0.1,0.6),IRON,bevel=0.02)
    k.box((0,-0.7,0.22),(0.07,1.4,0.07),IRON,bevel=0.015)
    for yy in(-0.45,-1.15): k.box((0,yy,0.02),(0.02,0.02,0.36),IRON,bevel=0)
    # pretzel: three bread rings
    fs=[]
    for (dy,dz,r) in ((-0.62,-0.35,0.2),(-0.98,-0.35,0.2),(-0.8,-0.58,0.24)):
        fs+=ring(k,(0,dy,dz),r-0.07,r,0.09,BREAD,n=18,axis="Y")
    goods_map(k,fs,"bread",plane=((1,0,0),(0,0,1)))
def wall_stall(k):
    """stable front module (3 m, barn height): posts, half door (top half open), hay inside"""
    k.box((0,-0.02,0.35),(CELL,0.4,0.7),STONE,bevel=0)
    plinth(k)
    k.box((-1.5,-0.26,(0.7+HB)/2),(0.26,0.22,HB-0.7),WOOD,bevel=0.04)
    k.box((0,-0.24,HB-0.12),(CELL,0.22,0.24),WOOD,bevel=0.03)
    zt=2.6
    grid_cut(k,k.box((0,-0.02,(zt+HB-0.24)/2),(CELL,0.36,HB-0.24-zt),PLANKS,bevel=0))
    k.box((0,-0.26,zt+0.06),(CELL,0.22,0.2),WOOD,bevel=0.03)
    # opening back plane (interior darkness) + stall interior hints
    k.quad([(-1.35,1.2,0.7),(1.35,1.2,0.7),(1.35,1.2,zt),(-1.35,1.2,zt)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for x in (-1.37,1.37):
        v=[k.bm.verts.new(p) for p in ((x,-0.2,0.7),(x,1.2,0.7),(x,1.2,zt),(x,-0.2,zt))]
        f=k.bm.faces.new(v if x<0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    k.box((0,0.5,zt-0.02),(2.74,1.4,0.04),PLANKS,bevel=0)
    k.box((0,0.5,0.72),(2.74,1.4,0.04),HAY,bevel=0)
    # lower half-door + side boards
    k.box((0,-0.14,1.2),(1.5,0.08,1.1),PLANKS,bevel=0.01)
    for z in (0.85,1.55): k.box((0,-0.2,z),(1.45,0.05,0.12),WOOD,bevel=0.02)
    k.box((0,-0.2,1.2),(1.55,0.05,0.1),WOOD,rot=(0,0.62,0),bevel=0.015)
    for sgn in(-1,1):
        k.box((sgn*1.05,-0.1,1.2),(0.6,0.12,1.1),PLANKS,bevel=0.01)
        k.box((sgn*0.8,-0.24,(0.7+zt)/2),(0.18,0.2,zt-0.7),WOOD,bevel=0.03)
    # upper half-door swung open against the wall
    k.box((1.2,-0.46,2.0),(0.08,0.62,0.9),PLANKS,rot=(0,0,0.2),bevel=0.01)
    # hay rack + horseshoe
    k.box((0,0.9,2.0),(1.4,0.3,0.5),WOOD,bevel=0.02)
    k.box((0,0.9,2.1),(1.3,0.28,0.35),HAY,bevel=0.08,segs=2,jitter=0.03,seed=3)
    ring(k,(0,-0.26,2.4),0.07,0.1,0.03,IRON,n=12,axis="Y")
EXTRA_SPECS+=[("SM_VK_BreadOven",lambda k: bread_oven(k),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_BreadRack",lambda k: bread_rack(k),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_BakerySign",lambda k: bakery_sign(k),dict(wobble=False,grime=False)),
              ("SM_VK_Wall_Stall",lambda k: wall_stall(k),dict(wobble=False,grime=True))]
def build_bakery(coll,origin,seed=61):
    st={"ground":"Stone","plaster":"Ochre","shutter":"Green","roof":"Red","seed":seed}
    build_house_v(coll,origin,2,2,st,front="DW",back="..",chimney=True)
    place_v(coll,"SM_VK_BreadOven",3.0,1.5,0,90,origin,st)
    place_v(coll,"SM_VK_Prop_BakerySign",-2.6,-3.3,2.9,0,origin,{})
    place_v(coll,"SM_VK_Prop_BreadRack",-1.3,-4.4,0,0,origin,{})
    place_v(coll,"SM_VK_Prop_Sacks",1.8,-4.2,0,20,origin,{})
    place_v(coll,"SM_VK_Prop_Woodpile",-4.9,1.2,0,90,origin,{})
    place_v(coll,"SM_VK_Prop_Planter",-3.7,-3.7,0,0,origin,{})
def build_stable(coll,origin,n=3,roof="Thatch"):
    L=n*CELL; st={"roof":roof}
    def P(nm,x,y,z,r,sty=st): place_v(coll,nm,x,y,z,r,origin,sty)
    for i in range(n):
        x=-L/2+1.5+3*i
        P("SM_VK_Wall_Stall",x,-3,0,0); P("SM_VK_Wall_Barn",x,3,0,180)
    for yy in(-1.5,1.5):
        P("SM_VK_Wall_Barn",-L/2,yy,0,-90); P("SM_VK_Wall_Barn",L/2,-yy,0,90)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): P("SM_VK_Corner_Barn",cx,cy,0,r)
    for i in range(n):
        x=-L/2+1.5+3*i
        if roof=="Thatch":
            P("SM_VK_RoofThatch_Gable_Planks" if i in (0,n-1) else "SM_VK_RoofThatch_Mid",x,0,HB,180 if i==0 else 0)
        else:
            P("SM_VK_Roof_Gable_Planks" if i in (0,n-1) else "SM_VK_Roof_Mid",x,0,HB,180 if i==0 else 0)
    P("SM_VK_Prop_Trough",-2.5,-4.6,0,0,{}); P("SM_VK_Prop_HayBale",3.9,-4.5,0,-15,{})
    P("SM_VK_Prop_Signpost",-L/2-1.5,-4.8,0,0,{})
    fence_run(coll,(-L/2,-8.5),(L/2,-8.5),origin,gate_at=1); fence_run(coll,(-L/2,-3.4),(-L/2,-8.5),origin); fence_run(coll,(L/2,-3.4),(L/2,-8.5),origin)

# =====================  HIP ROOF END  =====================
XH=1.5          # wall line of the hipped end (local x)
def hip_z(x,y):
    return min(roof_z(abs(y)),roof_z(max(0.0,HALF+(x-XH))))
def roof_hip(k,mat=ROOF,tabs=True):
    XE=XH+(EAVE-HALF)                       # end eave x
    xs=sorted(set([round(-1.5+i*0.25,4) for i in range(int((XE+1.5)/0.25)+1)]+[XE]))
    ys=sorted(set([round(-EAVE+i*0.25,4) for i in range(int(2*EAVE/0.25)+1)]+[EAVE,-EAVE]))
    rt=RT if mat==ROOF else TRT
    top={};bot={}
    for x in xs:
        for y in ys:
            z=hip_z(x,y); top[(x,y)]=k.bm.verts.new((x,y,z)); bot[(x,y)]=k.bm.verts.new((x,y,z-rt*1.2))
    T=TILE[mat]; W=TILE[WOOD]
    def reg(cx,cy):
        a=roof_z(abs(cy)); b=roof_z(max(0.0,HALF+(cx-XH)))
        return "S" if a<=b else "E"
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
            q=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            # triangulate along the hip diagonals
            tris=[(0,1,2),(0,2,3)] if (y0>=0)==(True) else [(0,1,3),(1,2,3)]
            for tr in tris:
                pts=[q[t_] for t_ in tr]
                cx=sum(p[0] for p in pts)/3; cy=sum(p[1] for p in pts)/3
                r_=reg(cx,cy)
                f=k.bm.faces.new([top[p] for p in pts]); f.material_index=mat
                for l,p in zip(f.loops,pts):
                    if r_=="S": l[k.uv].uv=((p[0]-1.5)/T,slope_dist(abs(p[1]))/T)
                    else: l[k.uv].uv=(p[1]/T,slope_dist(HALF+(p[0]-XH))/T)
                fb=k.bm.faces.new([bot[p] for p in pts[::-1]]); fb.material_index=WOOD if mat==ROOF else mat
                for l in fb.loops: l[k.uv].uv=(l.vert.co.x/W,l.vert.co.y/W)
    def side(pa,pb):
        for (a_,b_) in zip(pa,pb):
            f=k.bm.faces.new((top[a_],top[b_],bot[b_],bot[a_])); f.material_index=WOOD if mat==ROOF else mat
            for l in f.loops: l[k.uv].uv=((l.vert.co.x+l.vert.co.y)/W,l.vert.co.z/W)
    side([(xs[i+1],ys[0]) for i in range(len(xs)-1)],[(xs[i],ys[0]) for i in range(len(xs)-1)])
    side([(xs[i],ys[-1]) for i in range(len(xs)-1)],[(xs[i+1],ys[-1]) for i in range(len(xs)-1)])
    side([(xs[-1],ys[j+1]) for j in range(len(ys)-1)],[(xs[-1],ys[j]) for j in range(len(ys)-1)])
    k.bm.normal_update()
    for f in k.bm.faces:
        pass
    # ridge (to the hip apex) + hip ridges along the diagonals
    xa=XH-HALF   # apex x (=-1.5)
    if mat==ROOF:
        ridge(k,-1.5,xa+0.001) if xa>-1.5 else None
        for s_ in(-1,1):
            n=7
            for i in range(n):
                t0=i/n; t1=(i+1)/n
                d0=HALF*t0; d1=HALF*t1          # distance from apex along the hip (in plan, on each axis)
                p0=Vector((xa+d0,s_*d0,roof_z(d0)+0.03)); p1=Vector((xa+d1,s_*d1,roof_z(d1)+0.03))
                d=p1-p0; q=Vector((1,0,0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
                sub=Kit(); _cyl(sub,(0,0,0),0.19,0.16,d.length+0.05,10,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
                merge_kit(k,sub,Matrix.Translation((p0+p1)/2)@q)
        _ico(k,(xa,0,RIDGE+0.12),0.24,ROOF,sub=1)
        k.box((xa,0,RIDGE+0.5),(0.14,0.14,0.7),WOOD,bevel=0.04,segs=2)
        _ico(k,(xa,0,RIDGE+0.9),0.14,BRONZE,sub=1)
        if tabs:
            for s_ in(-1,1): eave_tabs(k,-1.5,XH+0.05,s_)
            sub=Kit()
            for s_ in(-1,1): eave_tabs(sub,-HALF+0.05,HALF-0.05,s_)
            # end eave: build a y-running strip by rotating an x-strip 90 degrees
            sub2=Kit(); eave_tabs(sub2,-HALF+0.02,HALF-0.02,1)
            merge_kit(k,sub2,Matrix.Translation((XH-HALF,0,0))@Matrix.Rotation(-math.pi/2,4,"Z"))
    else:
        thatch_eave_roll(k,-1.5,XH+0.25,-1,seed=1.0); thatch_eave_roll(k,-1.5,XH+0.25,1,seed=2.0)
        sub2=Kit(); thatch_eave_roll(sub2,-HALF-0.25,HALF+0.25,1,seed=3.0)
        merge_kit(k,sub2,Matrix.Translation((XH-HALF,0,0))@Matrix.Rotation(-math.pi/2,4,"Z"))
        thatch_ridge_cap(k,-1.5,xa+0.35)
        for s_ in(-1,1):
            _ico(k,(XH+(EAVE-HALF)-0.1,s_*(EAVE-0.1),roof_z(EAVE)-TRT/2),TRT/2+0.1,THATCH,sub=2,jit=0.02,seed=s_+5)
EXTRA_SPECS+=[("SM_VK_Roof_Hip",lambda k: roof_hip(k,ROOF),dict(wobble=False,grime=False)),
              ("SM_VK_RoofThatch_Hip",lambda k: roof_hip(k,THATCH),dict(wobble=False,grime=False))]

# =====================  FACADE EXTRAS  =====================
def wall_timber_oriel(k):
    timber_frame(k,False,"V")
    # remove nothing: the bay sits proud of the wall, covering the centre panel
    D=0.62; W=1.7; z0=0.55; z1=2.35; yf=-0.45
    # corbel/brackets beneath
    k.box((0,yf-D/2,z0-0.08),(W+0.2,D+0.1,0.16),WOOD,bevel=0.04)
    for x in (-W/2+0.15,0,W/2-0.15):
        k.box((x,yf-0.3,z0-0.45),(0.14,0.62,0.14),WOOD,rot=(math.atan2(0.5,-0.55),0,0),bevel=0.03)
    # three-sided bay: front + two angled sides
    pts=[(-W/2,yf),(-W/2+0.3,yf-D),(W/2-0.3,yf-D),(W/2,yf)]
    for (xa,ya),(xb,yb) in zip(pts[:-1],pts[1:]):
        L=math.hypot(xb-xa,yb-ya); ang=math.atan2(yb-ya,xb-xa); cx,cy=(xa+xb)/2,(ya+yb)/2
        nx,ny=-(yb-ya)/L,(xb-xa)/L
        if ny>0: nx,ny=-nx,-ny
        # sill + head plates, posts, window pane
        k.box((cx,cy,z0+0.1),(L+0.08,0.16,0.2),WOOD,rot=(0,0,ang),bevel=0.03)
        k.box((cx,cy,z1-0.1),(L+0.08,0.16,0.2),WOOD,rot=(0,0,ang),bevel=0.03)
        k.box((cx+nx*0.03,cy+ny*0.03,z0+0.3),(L,0.1,0.2),PLASTER,rot=(0,0,ang),bevel=0)
        pv=[k.bm.verts.new((cx+math.cos(ang)*sgn*(L/2-0.07)+nx*0.02,cy+math.sin(ang)*sgn*(L/2-0.07)+ny*0.02,z)) for sgn,z in ((-1,z0+0.42),(1,z0+0.42),(1,z1-0.22),(-1,z1-0.22))]
        f=k.bm.faces.new(pv); f.material_index=WINDOW; k.bm.normal_update()
        if f.normal.x*nx+f.normal.y*ny<0: f.normal_flip()
        for l,uvv in zip(f.loops,((0,0),(L,0),(L,1.5),(0,1.5))): l[k.uv].uv=(uvv[0]*0.9,uvv[1]*0.9)
        k.box((cx+nx*0.04,cy+ny*0.04,(z0+z1)/2+0.1),(0.06,0.06,z1-z0-0.6),WOOD,rot=(0,0,ang),bevel=0.01)
        k.box((cx+nx*0.04,cy+ny*0.04,z0+1.25),(L-0.1,0.06,0.06),WOOD,rot=(0,0,ang),bevel=0.01)
    for (x,y) in pts: k.box((x,y,(z0+z1)/2),(0.14,0.14,z1-z0),WOOD,bevel=0.03)
    # little hipped cap roof
    cap=Kit()
    zc=z1
    vb=[(-W/2-0.12,yf+0.02),(-W/2+0.22,yf-D-0.14),(W/2-0.22,yf-D-0.14),(W/2+0.12,yf+0.02)]
    top_=[(-W/2+0.2,yf+0.02),(W/2-0.2,yf+0.02)]
    V=[k.bm.verts.new((x,y,zc)) for x,y in vb]; Tt=[k.bm.verts.new((x,y,zc+0.55)) for x,y in top_]
    for face in ((V[0],V[1],Tt[0]),(V[1],V[2],Tt[1],Tt[0]),(V[2],V[3],Tt[1])):
        f=k.bm.faces.new(face); f.material_index=ROOF
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index==ROOF and f.verts[0] in V+Tt:
            if f.normal.z<0: f.normal_flip()
            k.project([f],ROOF)
def wall_timber_door(k):
    timber_frame(k,True)
    # replace window with a door: plank leaf over the window area + lintel
    k.box((0,-0.3,1.3),(1.0,0.1,2.2),PLANKS,bevel=0.015)
    for z in (0.6,1.9): k.box((0,-0.36,z),(0.92,0.03,0.09),IRON,bevel=0.01)
    k.box((0.34,-0.38,1.2),(0.05,0.05,0.14),IRON,bevel=0.01)
    k.box((0,-0.4,2.47),(1.3,0.2,0.18),WOOD,bevel=0.03)
def ext_stair(k):
    """wooden exterior stair along a wall (wall-local, outer side -Y); climbs +X over one cell to an upper door at x=+3"""
    rise=H1+0.3; run=2.7; n=13; y=-0.95; w=0.9
    for i in range(n):
        z=(i+1)*rise/n; x=-1.35+(i+0.5)*run/n
        k.box((x,y,z-0.04),(run/n+0.03,w,0.07),PLANKS,bevel=0.01)
    L=math.hypot(run,rise); ang=math.atan2(rise,run)
    for sy in (y-w/2+0.04,y+w/2-0.04):
        k.box((0,sy,rise/2),(L,0.08,0.26),WOOD,rot=(0,-ang,0),bevel=0.02)
    # landing at the top (in front of the next cell's door)
    k.box((1.35+0.75,y,rise-0.04),(1.5,w+0.1,0.1),PLANKS,bevel=0.01)
    for (px,py) in ((1.4,y-w/2),(2.8,y-w/2),(1.4,y+w/2),(2.8,y+w/2)):
        k.box((px,py,(rise-0.1)/2),(0.14,0.14,rise-0.1),WOOD,bevel=0.03)
    for (px,py) in ((0.2,y-w/2),(-1.0,y-w/2)):
        k.box((px,py,(px+1.35)/run*rise/2),(0.12,0.12,(px+1.35)/run*rise),WOOD,bevel=0.02)
    # railing
    k.box((0,y-w/2,rise/2+0.9),(L,0.06,0.08),WOOD,rot=(0,-ang,0),bevel=0.015)
    for i in range(1,7):
        x=-1.35+i*run/7; z=(x+1.35)/run*rise
        k.box((x,y-w/2,z+0.45),(0.05,0.05,0.9),WOOD,bevel=0.01)
    k.box((2.1,y-w/2,rise+0.9),(1.5,0.07,0.08),WOOD,bevel=0.015)
    for x in (1.6,2.1,2.6): k.box((x,y-w/2,rise+0.45),(0.05,0.05,0.9),WOOD,bevel=0.01)
    rock(k,(-1.55,y,0.08),(0.5,w+0.1,0.16),seed=3,tilt=0.01,segs=1)
def awning(k):
    W_=2.4; D_=1.1; z0=2.35; z1=1.95
    nx_=12
    for i in range(nx_):
        x0=-W_/2+i*W_/nx_; x1=x0+W_/nx_
        mi=CLOTH_A if (i//2)%2==0 else CLOTH_B
        vs=[k.bm.verts.new(p) for p in ((x0,-0.3,z0),(x1,-0.3,z0),(x1,-0.3-D_,z1-0.04*math.sin(math.pi*(i+1)/nx_)),(x0,-0.3-D_,z1-0.04*math.sin(math.pi*i/nx_)))]
        f=k.bm.faces.new(vs); f.material_index=mi
        vb=[k.bm.verts.new(v.co+Vector((0,0,-0.012))) for v in vs]; f2=k.bm.faces.new(vb[::-1]); f2.material_index=mi
        a=vs[3].co; b=vs[2].co; m=(a+b)/2+Vector((0,0,-0.24))
        tri=[k.bm.verts.new(a),k.bm.verts.new(b),k.bm.verts.new(m)]
        f3=k.bm.faces.new(tri); f3.material_index=mi
        tb=[k.bm.verts.new(v.co+Vector((0,0.01,0))) for v in tri]; f4=k.bm.faces.new(tb[::-1]); f4.material_index=mi
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index in (CLOTH_A,CLOTH_B):
            f.smooth=True
            for l in f.loops: l[k.uv].uv=(l.vert.co.x*2,l.vert.co.y*2)
    for sx in (-1,1):
        k.box((sx*W_/2,-0.3-D_/2,(z0+z1)/2+0.02),(0.04,D_,0.04),IRON,rot=(math.atan2(z0-z1,D_),0,0),bevel=0)
        k.box((sx*W_/2,-0.35,z0),(0.08,0.1,0.08),IRON,bevel=0.01)
    k.box((0,-0.3-D_,z1),(W_+0.05,0.04,0.04),IRON,bevel=0)
def laundry(k,L=5.0):
    for sx in(-1,1):
        k.box((sx*L/2,0,1.3),(0.12,0.12,2.6),WOOD,bevel=0.03)
        k.box((sx*L/2,0,2.55),(0.1,0.5,0.08),WOOD,bevel=0.02)
    rnd=random.Random(3)
    pts=[Vector((-L/2+L*i/16,0,2.5-0.35*math.sin(math.pi*i/16))) for i in range(17)]
    for pa,pb in zip(pts[:-1],pts[1:]):
        d=pb-pa; k.box(tuple((pa+pb)/2),(d.length,0.015,0.015),IRON,rot=(0,-math.atan2(d.z,d.x),0),bevel=0)
    x=-L/2+0.4; i=0
    while x<L/2-0.6:
        w=rnd.uniform(0.45,0.9); h=rnd.uniform(0.5,0.9)
        t=(x+w/2+L/2)/L; ztop=2.5-0.35*math.sin(math.pi*t)-0.02
        mi=[CLOTH_A,CLOTH_B,PAPER,BURLAP][i%4]
        vs=[k.bm.verts.new(p) for p in ((x,0,ztop),(x+w,0,ztop),(x+w,0.02*rnd.uniform(-1,1),ztop-h),(x,0.03,ztop-h*rnd.uniform(0.85,1.0)))]
        f=k.bm.faces.new(vs); f.material_index=mi; f.smooth=True
        vb=[k.bm.verts.new(v.co+Vector((0,0.01,0))) for v in vs]; f2=k.bm.faces.new(vb[::-1]); f2.material_index=mi
        for ff in (f,f2):
            for l in ff.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
        for px in (x+0.05,x+w-0.05): k.box((px,0,ztop+0.02),(0.03,0.04,0.08),WOOD,bevel=0)
        x+=w+rnd.uniform(0.12,0.3); i+=1
def shop_sign(k,emblem="anvil"):
    k.box((0,0.03,0),(0.16,0.1,0.6),IRON,bevel=0.02)
    k.box((0,-0.7,0.22),(0.07,1.4,0.07),IRON,bevel=0.015)
    k.box((0,-0.45,0.0),(0.04,0.04,0.55),IRON,rot=(0.8,0,0),bevel=0)
    for yy in(-0.45,-1.15): k.box((0,yy,0.08),(0.02,0.02,0.24),IRON,bevel=0)
    k.box((0,-0.8,-0.35),(0.1,1.05,0.7),PLANKS,bevel=0.04,segs=2)
    k.box((0,-0.8,-0.35),(0.12,0.9,0.56),WOOD,bevel=0.02)
    if emblem=="anvil":
        k.box((-0.1,-0.8,-0.3),(0.08,0.5,0.12),STEEL,bevel=0.02); k.box((-0.1,-0.8,-0.42),(0.08,0.22,0.14),STEEL,bevel=0.02)
        k.box((-0.1,-0.8,-0.52),(0.08,0.36,0.07),STEEL,bevel=0.01)
        lathe(k,[(0.07,0.0),(0.0,0.14)],center=(-0.1,-1.05,-0.3),segs=6,mi=STEEL)
    elif emblem=="boot":
        k.box((-0.1,-0.78,-0.28),(0.08,0.18,0.38),BREAD,bevel=0.04); k.box((-0.1,-0.9,-0.47),(0.08,0.4,0.14),BREAD,bevel=0.05)
    else:
        lathe(k,[(0.0,-0.62),(0.14,-0.58),(0.2,-0.45),(0.16,-0.32),(0.06,-0.26),(0.06,-0.16),(0.08,-0.14)],center=(-0.1,-0.8,0),segs=10,mi=STAINED)
        for f in k.bm.faces:
            if f.material_index==STAINED: f.smooth=True
EXTRA_SPECS+=[("SM_VK_Wall_Timber_Oriel",lambda k: wall_timber_oriel(k),dict(grime=False)),
              ("SM_VK_Wall_Timber_Door",lambda k: wall_timber_door(k),dict(grime=False)),
              ("SM_VK_Stair_Ext",lambda k: ext_stair(k),dict(wobble=False,grime=True)),
              ("SM_VK_Awning",lambda k: awning(k),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_Laundry",lambda k: laundry(k),dict(wobble=False,grime=True)),
              ("SM_VK_Sign_Anvil",lambda k: shop_sign(k,"anvil"),dict(wobble=False,grime=False)),
              ("SM_VK_Sign_Boot",lambda k: shop_sign(k,"boot"),dict(wobble=False,grime=False)),
              ("SM_VK_Sign_Potion",lambda k: shop_sign(k,"potion"),dict(wobble=False,grime=False))]

def build_town(coll,C=(200.0,0.0),seed=2027):
    global gardens
    gardens=[]
    cx,cy=C; R=math.radians
    def O(x,y,rot=0.0): return (cx+x,cy+y,R(rot))
    def tag(fn):
        before=set(o.name for o in coll.objects); fn()
    # --- plaza
    build_townhall(coll,O(0,14,0))
    place_v(coll,"SM_VK_Prop_Fountain",cx,cy-1,0,0,(0,0,0),{})
    for (x,y,r_,c) in ((-7.5,-5.5,25,"Red"),(7.5,-5.5,-25,"Blue"),(-9,3,90,"Yellow"),(9,3,-90,"Green")):
        place_v(coll,"SM_VK_MarketStall",cx+x,cy+y,0,r_,(0,0,0),{"cloth":c})
    for (x,y) in ((-13,-9),(13,-9),(-13,9),(13,9)): place_v(coll,"SM_VK_Prop_LampPost",cx+x,cy+y,0,0,(0,0,0),{})
    for (x,y,r_) in ((-4,-9.5,0),(4,-9.5,0)): place_v(coll,"SM_VK_Prop_Bench",cx+x,cy+y,0,r_,(0,0,0),{})
    place_v(coll,"SM_VK_Prop_Cart",cx-11,cy-2,0,70,(0,0,0),{}); place_v(coll,"SM_VK_Prop_Crates",cx+11.5,cy-7,0,20,(0,0,0),{})
    place_v(coll,"SM_VK_Prop_NoticeBoard",cx-11.5,cy+9.5,0,160,(0,0,0),{})
    road_strip(coll,"VK_TownPlaza",[(cx-15,cy),(cx+15,cy)],w=11.5)
    # --- chapel + graveyard (east)
    build_chapel(coll,O(24,2,-90))
    gx0,gx1,gy0,gy1=cx+29.5,cx+41.5,cy-7.5,cy+10.5
    for j in range(6):
        y=gy0+1.5+3*j
        place_v(coll,"SM_VK_LowWall",gx1,y,0,90,(0,0,0),{})
    for i in range(4):
        x=gx0+1.5+3*i
        place_v(coll,"SM_VK_LowWall_Lychgate" if i==1 else "SM_VK_LowWall",x,gy0,0,0,(0,0,0),{})
        place_v(coll,"SM_VK_LowWall",x,gy1,0,0,(0,0,0),{})
    for (x,y) in ((gx0,gy0),(gx1,gy0),(gx1,gy1),(gx0,gy1)): place_v(coll,"SM_VK_LowWall_Post",x,y,0,0,(0,0,0),{})
    rnd=random.Random(seed)
    kinds=["SM_VK_Grave_A","SM_VK_Grave_Cross","SM_VK_Grave_A","SM_VK_Grave_Obelisk"]
    for r_ in range(3):
        for c_ in range(5):
            if rnd.random()<0.2: continue
            place_v(coll,kinds[rnd.randrange(4)],gx0+2.5+c_*2.3+rnd.uniform(-0.2,0.2),gy0+3+r_*4.5,0,rnd.uniform(-8,8),(0,0,0),{})
    place_v(coll,"SM_VK_Deco_Bush",gx1-1.2,gy1-1.3,0,0,(0,0,0),{}); place_v(coll,"SM_VK_Deco_Bush",gx0+1.0,gy1-1.2,0,90,(0,0,0),{})
    # --- tavern (west)
    build_tavern(coll,O(-22,2,90))
    # --- main street (east-west) and the south road
    yroad=cy-22
    street(coll,cx-64,cx-34,yroad,seed+1); street(coll,cx+34,cx+64,yroad,seed+2)
    for (x,nn,sd) in ((-25.5,3,seed+7),(25.5,3,seed+8)):
        st=random_style(sd); build_house_v(coll,O(x,-31.5,180),nn,2,st)
    road_strip(coll,"VK_TownMain",[(cx-64,yroad),(cx-20,yroad+0.5),(cx,yroad),(cx+20,yroad-0.4),(cx+64,yroad)],w=3.4)
    road_strip(coll,"VK_TownSouth",[(cx,cy-11),(cx+0.5,yroad),(cx-0.5,cy-45),(cx,cy-62)],w=2.8)
    # --- crafts along the south road
    build_bakery(coll,O(-9,-37,90)); build_blacksmith(coll,O(10,-37,-90))
    # --- farm quarter
    build_barn(coll,O(-14,-58,0)); build_stable(coll,O(14,-58,180))
    crops=["SM_VK_Crop_Wheat","SM_VK_Crop_Wheat","SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Lavender","SM_VK_Crop_Wheat"]
    for i,cr in enumerate(crops):
        place_v(coll,cr,cx-10.4+(i%4)*3.2,cy-70-(i//4)*3.2,0,0,(0,0,0),{})
    fence_run(coll,(cx-12.2,cy-68.2),(cx+1.6,cy-68.2),(0,0,0),gate_at=2)
    fence_run(coll,(cx-12.2,cy-77.2),(cx+1.6,cy-77.2),(0,0,0))
    fence_run(coll,(cx-12.2,cy-68.2),(cx-12.2,cy-77.2),(0,0,0)); fence_run(coll,(cx+1.6,cy-68.2),(cx+1.6,cy-77.2),(0,0,0))
    place_v(coll,"SM_VK_Prop_Scarecrow",cx-4.8,cy-73,0,25,(0,0,0),{})
    place_v(coll,"SM_VK_Prop_ChickenCoop",cx+6,cy-70,0,-20,(0,0,0),{}); place_v(coll,"SM_VK_Prop_Chickens",cx+6.5,cy-72.5,0,0,(0,0,0),{})
    build_windmill(coll,O(34,-66,-15))
    # --- guard towers at the town entrances
    build_guardtower(coll,O(-67,-26,0)); build_guardtower(coll,O(67,-26,0))
    place_v(coll,"SM_VK_Prop_Signpost",cx-64,yroad+3,0,0,(0,0,0),{}); place_v(coll,"SM_VK_Prop_Signpost",cx+64,yroad+3,0,180,(0,0,0),{})
    # --- laundry lines between some gardens
    for (xa,ya,xb,yb) in gardens[::3]:
        place_v(coll,"SM_VK_Prop_Laundry",(xa+xb)/2,(ya+yb)/2,0,0,(0,0,0),{})

def scatter_trees(coll,C=(200.0,0.0),n_trees=90,seed=11,xr=95,yr=(-100,55)):
    cx,cy=C
    for o in [o for o in coll.objects if o.name.startswith("VK_TTree")]: bpy.data.objects.remove(o)
    pts=[o.location.copy() for o in coll.objects if not o.name.startswith("VK_Town")]
    kd=mathutils.kdtree.KDTree(len(pts))
    for i,p in enumerate(pts): kd.insert(p,i)
    kd.balance()
    tw=bpy.data.objects["SM_Tree_Wood"].data; tf=bpy.data.objects["SM_Tree_Foliage"].data
    rnd=random.Random(seed); n=0; placed=[]; tries=0
    while n<n_trees and tries<20000:
        tries+=1
        x=cx+rnd.uniform(-xr,xr); y=cy+rnd.uniform(*yr)
        if abs(y-(cy-22))<6: continue
        if abs(x-cx)<5 and cy-65<y<cy-10: continue
        co,idx,dist=kd.find((x,y,0))
        if dist<8.5: continue
        if any((x-px)**2+(y-py)**2<6.5**2 for px,py in placed): continue
        s_=rnd.uniform(0.85,1.25); rz=rnd.uniform(0,6.28)
        for d,nm in ((tw,"W"),(tf,"F")):
            t_=bpy.data.objects.new(f"VK_TTree{n}{nm}",d); coll.objects.link(t_); t_.location=(x,y,0); t_.scale=(s_,s_,s_); t_.rotation_euler.z=rz
        placed.append((x,y)); n+=1
