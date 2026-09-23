# ===================== WORKSHOP HELPERS (shared, read-only for agents) =====================
# Usage in any execute_blender_code call:
#   exec(bpy.data.texts["ws_common"].as_string()); g=ws_ns("hovel")   # kit namespace + your module
import bpy, os, math, json
from mathutils import Vector
VK_ROOT=r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"     # project folder (see HANDOFF.md)
WS_RENDERS=os.path.join(VK_ROOT,"renders","modules")                   # workshop agents render into <WS_RENDERS>/<agent>/

def ws_ns(agent=None):
    """fresh namespace with the whole village kit (vk_helpers) + your module text 'ws_<agent>' executed on top"""
    g={}
    exec(bpy.data.texts["vk_helpers"].as_string(),g)
    if agent:
        t=bpy.data.texts.get("ws_"+agent)
        if t: exec(t.as_string(),g)
    return g

def _copy_props(dst,src):
    for p in src.bl_rna.properties:
        if p.is_readonly or p.identifier in ("rna_type",): continue
        try: setattr(dst,p.identifier,getattr(src,p.identifier))
        except Exception: pass

def ws_scene(agent):
    """your private scene WS_<agent> (same world, sun, render settings as VillageKit) + piece collection"""
    name="WS_"+agent; src=bpy.data.scenes["VillageKit"]
    sc=bpy.data.scenes.get(name)
    if sc is None:
        sc=bpy.data.scenes.new(name); sc.world=src.world
        sc.render.engine=src.render.engine
        _copy_props(sc.eevee,src.eevee)
        sc.view_settings.view_transform=src.view_settings.view_transform
        sc.view_settings.look=src.view_settings.look; sc.view_settings.exposure=src.view_settings.exposure
        sc.render.film_transparent=False
        sun=bpy.data.objects.get("VK_Sun")
        if sun: sc.collection.objects.link(sun)
        gm=bpy.data.objects.get("VK_Ground")
        me=bpy.data.meshes.new(name+"_GroundMesh")
        S=60.0; me.from_pydata([(-S,-S,0),(S,-S,0),(S,S,0),(-S,S,0)],[],[(0,1,2,3)])
        if gm and gm.data.materials: me.materials.append(gm.data.materials[0])
        go=bpy.data.objects.new(name+"_Ground",me); sc.collection.objects.link(go)
    coll=bpy.data.collections.get(name+"_Pieces")
    if coll is None:
        coll=bpy.data.collections.new(name+"_Pieces"); sc.collection.children.link(coll)
    asm=bpy.data.collections.get(name+"_Assembly")
    if asm is None:
        asm=bpy.data.collections.new(name+"_Assembly"); sc.collection.children.link(asm)
    return sc,coll,asm

def ws_owner(objname):
    o=bpy.data.objects.get(objname)
    if o is None: return None
    return [c.name for c in o.users_collection]

def ws_build(agent,names=None,g=None,row_spacing=None):
    """build every (name,fn,finish_kwargs) in your module's WS_SPECS into WS_<agent>_Pieces.
       Refuses names that already exist outside your piece collection (protects the shipped kit)."""
    g=g or ws_ns(agent); sc,coll,asm=ws_scene(agent)
    specs=g.get("WS_SPECS",[]); built=[]
    for n,fn,kw in specs:
        if names and n not in names: continue
        assert n.startswith("SM_VK_"), n
        own=ws_owner(n)
        if own is not None and own!=[coll.name]:
            raise RuntimeError(f"{n} already exists in {own}: pick another name")
        k=g["Kit"](); fn(k)
        for f in k.bm.faces:
            if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)
        tmpn="__wstmp_"+agent
        o=k.finish(tmpn,coll,**kw)
        for p in o.data.polygons:
            p.use_smooth=p.material_index in (g["HAY"],g["APPLE"],g["PUMPKIN"],g["BREAD"],g["CLOTH_A"],g["CLOTH_B"],g["LEAF"],g["BURLAP"],g["FOLIAGE"],g["CROPS"])
        base=bpy.data.objects.get(n)
        if base is None:
            o.name=n; o.data.name=n
        else:
            # update in place so every placed instance picks up the new geometry
            import bmesh as _bm
            bm=_bm.new(); bm.from_mesh(o.data); bm.to_mesh(base.data); bm.free()
            mats=list(o.data.materials)
            while len(base.data.materials)<len(mats): base.data.materials.append(mats[len(base.data.materials)])
            for i,m in enumerate(mats): base.data.materials[i]=m
            for k_,v_ in o.items(): base[k_]=v_
            md=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(md); o=base
        built.append(o)
    if row_spacing:
        for i,o in enumerate(built): o.location=(i*row_spacing,0,0)
    return built

def ws_grid(objs,cols=4,sx=6.0,sy=6.0,origin=(0,0)):
    for i,o in enumerate(objs): o.location=(origin[0]+(i%cols)*sx,origin[1]-(i//cols)*sy,0)

def ws_clear_assembly(agent):
    sc,coll,asm=ws_scene(agent)
    for o in list(asm.objects): bpy.data.objects.remove(o)

def ws_shot(agent,name,loc,target,lens=35,res=(1280,720),samples=32):
    """render your scene to renders2/<agent>/<name>.png and return the path (Read it to look at it)"""
    sc,coll,asm=ws_scene(agent)
    cn="WS_"+agent+"_Cam"; cam=bpy.data.objects.get(cn)
    if cam is None:
        cam=bpy.data.objects.new(cn,bpy.data.cameras.new(cn)); sc.collection.objects.link(cam)
    cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens; cam.data.clip_end=1000
    sc.camera=cam; sc.render.resolution_x,sc.render.resolution_y=res; sc.render.resolution_percentage=100
    sc.eevee.taa_render_samples=samples
    d=os.path.join(WS_RENDERS,agent); os.makedirs(d,exist_ok=True)
    sc.render.filepath=os.path.join(d,name+".png")
    bpy.ops.render.render(write_still=True,scene=sc.name)
    return sc.render.filepath

def ws_stats(objs):
    out=[]
    for o in objs:
        me=o.data; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
        used=sorted({p.material_index for p in me.polygons})
        out.append(dict(name=o.name,tris=sum(len(p.vertices)-2 for p in me.polygons),
                        bbox=[round(mx[i]-mn[i],2) for i in range(3)],zmin=round(mn[2]-o.location.z,2),mats=used))
    return out
