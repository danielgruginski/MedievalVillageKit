import bpy, math
from mathutils import Vector
ROOT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
CODE=ROOT+r"\code"; OUTN=ROOT+r"\renders2\nature"
SC=bpy.data.scenes["VillageKit"]
def ns(local=True):
    exec(bpy.data.texts["vk_kit"].as_string(),globals()); g=vk_kit_ns()
    if local: exec(open(CODE+r"\vk_nature.py",encoding="utf8").read(),g)
    return g
def tcoll():
    c=bpy.data.collections.get("VK_TmpNature")
    if c is None:
        c=bpy.data.collections.new("VK_TmpNature"); SC.collection.children.link(c)
    return c
def ground():
    if bpy.data.objects.get("TMPN_Ground"): return
    me=bpy.data.meshes.new("TMPN_Ground"); s=90
    me.from_pydata([(930-s,-320-s,0),(930+s,-320-s,0),(930+s,-320+s,0),(930-s,-320+s,0)],[],[(0,1,2,3)])
    m=bpy.data.materials.new("TMPN_Ground"); m.use_nodes=True
    b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value=(0.18,0.28,0.10,1); b.inputs["Roughness"].default_value=1.0
    me.materials.append(m); o=bpy.data.objects.new("TMPN_Ground",me); tcoll().objects.link(o)
def inst(master,loc,name=None,rot=0.0):
    src=bpy.data.objects[master]; name=name or "TMPN_"+master
    o=bpy.data.objects.get(name)
    if o is None:
        o=bpy.data.objects.new(name,src.data); tcoll().objects.link(o)
    o.data=src.data; o.location=loc; o.rotation_euler=(0,0,rot); o.hide_render=False; o.hide_viewport=False
    return o
def build(g,fn,args,kw,tmpname,loc):
    old=bpy.data.objects.get(tmpname)
    if old is not None:
        me=old.data; bpy.data.objects.remove(old)
        if me.users==0: bpy.data.meshes.remove(me)
    k=g["NK"](); g[fn](k,*args,**kw); o=g["nk_finish"](k,tmpname,tcoll())
    o.location=loc; o.hide_render=False; o.hide_viewport=False; o.pop("kit",None)
    return o
def snap(name,loc,target,lens=35,res=(1280,720),samples=32):
    R={}; exec(bpy.data.texts["vk_render"].as_string(),R)
    return R["shot"](name,loc,target,lens=lens,res=res,samples=samples,outdir=OUTN)
def colony(name,target,lens=60,dist=40.0,pitch=50.0,az=-90.0,res=(1280,720),samples=32):
    t=Vector(target); p=math.radians(pitch); a=math.radians(az)
    loc=t+Vector((math.cos(a)*math.cos(p),math.sin(a)*math.cos(p),math.sin(p)))*dist
    return snap(name,tuple(loc),tuple(t),lens=lens,res=res,samples=samples)
def cleanup():
    c=bpy.data.collections.get("VK_TmpNature")
    if c:
        for o in list(c.objects):
            me=o.data if o.type=="MESH" else None
            bpy.data.objects.remove(o)
            if me is not None and me.users==0 and me.name.startswith("TMPN"): bpy.data.meshes.remove(me)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith("TMPN") and m.users==0]: bpy.data.meshes.remove(me)
    for m in [m for m in bpy.data.materials if m.name.startswith("TMPN") and m.users==0]: bpy.data.materials.remove(m)
