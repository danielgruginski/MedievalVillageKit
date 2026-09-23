# village-kit-buildings-continue / agent-a0dbc47a9891e1abd.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:46:03  blender  ok
# ==============================================================================================================
import bpy, hashlib
t=bpy.data.texts.get("ws_town")
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
bs=t.as_string() if t else ""
print(len(src),len(bs),src==bs, src.rstrip()==bs.rstrip())
import difflib
if src!=bs:
    d=list(difflib.unified_diff(bs.splitlines(),src.splitlines(),"blender","file",n=1,lineterm=""))
    print(len(d)); print("\n".join(d[:120]))
sc=bpy.data.scenes.get("WS_town"); print(sc)
for cn in ("WS_town_Pieces","WS_town_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, len(c.objects) if c else None)
# ---- result ----
# {"result":"Code executed successfully: 71618 71618 True True\n<bpy_struct, Scene(\"WS_town\") at 0x000001CBCBE84088>\nWS_town_Pieces 36\nWS_town_Assem
# bly 373\n"}

# ==============================================================================================================
# [0002] 2026-09-23 15:48:16  blender  ok
# ==============================================================================================================
import bpy
names=["SM_VK_Roof_Gable_Stepped","SM_VK_Roof_CrossGable_Hoist","SM_VK_Roof_CrossGable","SM_VK_Roof_Gable_Flush","SM_VK_Roof_Firewall","SM_VK_Roof_HalfHip","SM_VK_Roof_Mid_CapL","SM_VK_Roof_Mid_CapR","SM_VK_Chimney_Party","SM_VK_Banner_Wall","SM_VK_Emblem_Ridge_Key","SM_VK_Emblem_Ridge_Pretzel","SM_VK_Emblem_Ridge_Tankard","SM_VK_Roof_Gable_Hoist","SM_VK_Chimney_Gable_H30","SM_VK_LowWall","SM_VK_LowWall_Post","SM_VK_Prop_Sign","SM_VK_Sign_Anvil","SM_VK_Prop_BakerySign","SM_VK_Sign_Potion","SM_VK_Wall_Timber_Oriel","SM_VK_Roof_LCorner","SM_VK_Deco_Weeds"]
for n in names:
    o=bpy.data.objects.get(n)
    print(n, bool(o), (o.users_collection[0].name if o and o.users_collection else None))
print([s.name for s in bpy.data.scenes])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Gable_Stepped True WS_skyline_Pieces\nSM_VK_Roof_CrossGable_Hoist False None\nSM_VK_Roof_CrossGable 
# True WS_skyline_Pieces\nSM_VK_Roof_Gable_Flush True WS_skyline_Pieces\nSM_VK_Roof_Firewall True WS_skyline_Pieces\nSM_VK_Roof_HalfHip True WS_skyline_
# Pieces\nSM_VK_Roof_Mid_CapL True WS_skyline_Pieces\nSM_VK_Roof_Mid_CapR True WS_skyline_Pieces\nSM_VK_Chimney_Party True WS_skyline_Pieces\nSM_VK_Bann
# er_Wall True WS_skyline_Pieces\nSM_VK_Emblem_Ridge_Key True WS_skyline_Pieces\nSM_VK_Emblem_Ridge_Pretzel True WS_skyline_Pieces\nSM_VK_Emblem_Ridge_T
# ankard True WS_skyline_Pieces\nSM_VK_Roof_Gable_Hoist True WS_skyline_Pieces\nSM_VK_Chimney_Gable_H30 True WS_skyline_Pieces\nSM_VK_LowWall True VK_Pi
# eces\nSM_VK_LowWall_Post True VK_Pieces\nSM_VK_Prop_Sign True VK_Pieces\nSM_VK_Sign_Anvil True VK_Pieces\nSM_VK_Prop_BakerySign True VK_Pieces\nSM_VK_

# ==============================================================================================================
# [0003] 2026-09-23 15:49:43  blender  ok
# ==============================================================================================================
import bpy,re
s=bpy.data.texts["ws_common"].as_string()
for m in re.finditer(r"^def .*$",s,re.M): print(m.group(0))
i=s.find("def ws_shot"); print(s[i:i+1500])
# ---- result ----
# {"result":"Code executed successfully: def ws_ns(agent=None):\ndef _copy_props(dst,src):\ndef ws_scene(agent):\ndef ws_owner(objname):\ndef ws_build(a
# gent,names=None,g=None,row_spacing=None):\ndef ws_grid(objs,cols=4,sx=6.0,sy=6.0,origin=(0,0)):\ndef ws_clear_assembly(agent):\ndef ws_shot(agent,name
# ,loc,target,lens=35,res=(1280,720),samples=32):\ndef ws_stats(objs):\ndef ws_shot(agent,name,loc,target,lens=35,res=(1280,720),samples=32):\n \"\"\"re
# nder your scene to renders2/<agent>/<name>.png and return the path (Read it to look at it)\"\"\"\n sc,coll,asm=ws_scene(agent)\n cn=\"WS_\"+agent+\"_C
# am\"; cam=bpy.data.objects.get(cn)\n if cam is None:\n cam=bpy.data.objects.new(cn,bpy.data.cameras.new(cn)); sc.collection.objects.link(cam)\n cam.lo
# cation=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_end=1000\n sc.camer

# ==============================================================================================================
# [0004] 2026-09-23 15:50:32  blender  ok
# ==============================================================================================================
import bpy,re
s=bpy.data.texts["ws_common"].as_string()
i=s.find("def ws_build"); print(s[i:i+2600])
i=s.find("def ws_clear_assembly"); print(s[i:i+700])
# ---- result ----
# {"result":"Code executed successfully: def ws_build(agent,names=None,g=None,row_spacing=None):\n \"\"\"build every (name,fn,finish_kwargs) in your mod
# ule's WS_SPECS into WS_<agent>_Pieces.\n Refuses names that already exist outside your piece collection (protects the shipped kit).\"\"\"\n g=g or ws_
# ns(agent); sc,coll,asm=ws_scene(agent)\n specs=g.get(\"WS_SPECS\",[]); built=[]\n for n,fn,kw in specs:\n if names and n not in names: continue\n asse
# rt n.startswith(\"SM_VK_\"), n\n own=ws_owner(n)\n if own is not None and own!=[coll.name]:\n raise RuntimeError(f\"{n} already exists in {own}: pick 
# another name\")\n k=g[\"Kit\"](); fn(k)\n for f in k.bm.faces:\n if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)\n tmpn
# =\"__wstmp_\"+agent\n o=k.finish(tmpn,coll,**kw)\n for p in o.data.polygons:\n p.use_smooth=p.material_index in (g[\"HAY\"],g[\"APPLE\"],g[\"PUMPKIN\"

# ==============================================================================================================
# [0005] 2026-09-23 15:50:58  blender  ok
# ==============================================================================================================
import bpy
c=bpy.data.collections["WS_town_Assembly"]
xs=[o.location.x for o in c.objects]; ys=[o.location.y for o in c.objects]
print(min(xs),max(xs),min(ys),max(ys))
# cluster by 20m
from collections import Counter
print(Counter((round(o.location.x/20)*20,round(o.location.y/20)*20) for o in c.objects))
p=bpy.data.collections["WS_town_Pieces"]
print([(o.name,tuple(round(v,1) for v in o.location)) for o in p.objects][:40])
print([o.name for o in bpy.data.scenes["WS_town"].collection.objects])
# ---- result ----
# {"result":"Code executed successfully: -35.04999923706055 15.550000190734863 -13.75 29.600000381469727\nCounter({(-20, 20): 72, (0, 20): 63, (-40, 20)
# : 48, (20, 20): 40, (0, 0): 39, (0, -20): 32, (-20, 0): 25, (-20, -20): 22, (20, -20): 16, (20, 0): 16})\n[('SM_VK_Wall_StoneUp', (-200.0, 0.0, 0.0)),
#  ('SM_VK_Wall_StoneUp_Window', (-194.0, 0.0, 0.0)), ('SM_VK_Wall_StoneUp_Twin', (-188.0, 0.0, 0.0)), ('SM_VK_Wall_StoneUp_Slit', (-182.0, 0.0, 0.0)), 
# ('SM_VK_Wall_StoneUp_Loading', (-176.0, 0.0, 0.0)), ('SM_VK_Wall_StoneUp_Door', (-170.0, 0.0, 0.0)), ('SM_VK_Corner_StoneUp', (-164.0, 0.0, 0.0)), ('S
# M_VK_InnerCorner_StoneUp', (-158.0, 0.0, 0.0)), ('SM_VK_Wall_PlasterUp', (-200.0, -7.0, 0.0)), ('SM_VK_Wall_PlasterUp_Window', (-194.0, -7.0, 0.0)), (
# 'SM_VK_Wall_PlasterUp_Oxeye', (-188.0, -7.0, 0.0)), ('SM_VK_Corner_PlasterUp', (-182.0, -7.0, 0.0)), ('SM_VK_InnerCorner_PlasterUp', (-176.0, -7.0, 0.

# ==============================================================================================================
# [0006] 2026-09-23 15:51:47  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
objs=ws_build("town", g=g)
ws_grid(objs, cols=8, sx=6, sy=7, origin=(-200,0))
st=ws_stats(objs)
for s in st: print(s["name"][6:],s["tris"],s["bbox"],s["zmin"])
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: Wall_StoneUp 732 [3.0, 0.77, 2.91] -0.11\nWall_StoneUp_Window 1806 [3.0, 1.1, 2.91] -0.11\nWall_StoneUp_Twin 22
# 84 [3.0, 0.84, 2.91] -0.11\nWall_StoneUp_Slit 1436 [3.0, 0.77, 2.91] -0.11\nWall_StoneUp_Loading 2742 [3.0, 1.22, 2.91] -0.11\nWall_StoneUp_Door 3252 
# [3.0, 0.81, 2.91] -0.11\nCorner_StoneUp 768 [1.11, 1.16, 2.86] -0.06\nInnerCorner_StoneUp 648 [0.63, 0.63, 2.58] 0.21\nWall_PlasterUp 1260 [3.0, 0.72,
#  2.92] -0.12\nWall_PlasterUp_Window 1486 [3.0, 1.05, 2.92] -0.12\nWall_PlasterUp_Oxeye 1328 [3.0, 0.73, 2.92] -0.12\nCorner_PlasterUp 284 [0.74, 0.74,
#  3.03] -0.22\nInnerCorner_PlasterUp 88 [0.3, 0.3, 2.82] -0.02\nWall_Stone_Shop 2556 [3.04, 1.25, 3.63] -0.6\nWall_Plaster_Shop 2280 [3.13, 1.27, 3.6] 
# -0.6\nProp_ShopGoods_Bread 1984 [1.9, 0.5, 0.32] 0.0\nProp_ShopGoods_Produce 1312 [1.97, 0.59, 0.36] 0.0\nProp_ShopGoods_Cloth 472 [1.74, 0.59, 0.85] 

# ==============================================================================================================
# [0007] 2026-09-23 15:52:59  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("town","cat_v3",(-179,-50,24),(-179,-13,0.5),lens=30)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\cat_v3.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:53:18  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects["WS_town_Ground"]; print(o.location[:], o.scale[:], o.dimensions[:], [m.name for m in o.data.materials])
s=bpy.data.texts["ws_common"].as_string(); i=s.find("def ws_scene"); print(s[i:i+1500])
# ---- result ----
# {"result":"Code executed successfully: (0.0, 0.0, 0.0) (1.0, 1.0, 1.0) (120.0, 120.0, 0.0) ['MC_WK_Grass']\ndef ws_scene(agent):\n \"\"\"your private 
# scene WS_<agent> (same world, sun, render settings as VillageKit) + piece collection\"\"\"\n name=\"WS_\"+agent; src=bpy.data.scenes[\"VillageKit\"]\n
#  sc=bpy.data.scenes.get(name)\n if sc is None:\n sc=bpy.data.scenes.new(name); sc.world=src.world\n sc.render.engine=src.render.engine\n _copy_props(s
# c.eevee,src.eevee)\n sc.view_settings.view_transform=src.view_settings.view_transform\n sc.view_settings.look=src.view_settings.look; sc.view_settings
# .exposure=src.view_settings.exposure\n sc.render.film_transparent=False\n sun=bpy.data.objects.get(\"VK_Sun\")\n if sun: sc.collection.objects.link(su
# n)\n gm=bpy.data.objects.get(\"VK_Ground\")\n me=bpy.data.meshes.new(name+\"_GroundMesh\")\n S=60.0; me.from_pydata([(-S,-S,0),(S,-S,0),(S,S,0),(-S,S,

# ==============================================================================================================
# [0009] 2026-09-23 15:55:42  blender  ok
# ==============================================================================================================
import bpy
P=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py"
src=open(P,encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
objs=ws_build("town", g=g, names=["SM_VK_Wall_Stone_Passage","SM_VK_Wall_StoneUp_Door","SM_VK_Prop_HoistBeam"])
for s in ws_stats(objs): print(s)
o=bpy.data.objects["SM_VK_Wall_Stone_Passage"]
print(max((o.matrix_world@v.co).z-o.location.z for v in o.data.vertices))
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Wall_StoneUp_Door', 'tris': 2348, 'bbox': [3.0, 0.81, 2.91], 'zmin': -0.11, 'mats': [0, 5, 23, 
# 45]}\n{'name': 'SM_VK_Wall_Stone_Passage', 'tris': 1876, 'bbox': [3.21, 1.0, 3.6], 'zmin': -0.6, 'mats': [0, 45, 46]}\n{'name': 'SM_VK_Prop_HoistBeam'
# , 'tris': 620, 'bbox': [0.59, 1.7, 7.0], 'zmin': -5.07, 'mats': [2, 5, 16, 25]}\n3.0\n"}

# ==============================================================================================================
# [0010] 2026-09-23 15:56:28  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
g["twn_clear_assembly"](asm)
objs=[o for o in coll.objects]
order=[n for n,_,_ in g["WS_SPECS"]]
objs=sorted(objs,key=lambda o: order.index(o.name) if o.name in order else 999)
ws_grid(objs, cols=8, sx=7, sy=8, origin=(-24.5,-14))
r=[]
r.append(g["build_terrace"](asm,(0,6,0),units=6,seed=0))
r.append(g["build_merchant_house"](asm,(-20,26,0),seed=0))
r.append(g["build_townhouse_gablefront"](asm,(-3,26,0),seed=0))
r.append(g["build_corner_house"](asm,(14,26,0),seed=0))
print([ (x.get("footprint")) for x in r], len(asm.objects), time.time()-t0)
print([(u["w"],u["s"],u["g"],u["u"]) for u in r[0]["units"]])
# ---- result ----
# {"result":"Code executed successfully: [(15, 2), (3, 2), (2, 3), (3, 3)] 432 2.8053860664367676\n[(2, 4, 'Stone', 'StoneUp'), (3, 2, 'Stone', 'Plaster
# Up'), (3, 2, 'Plaster', 'Timber'), (2, 3, 'Stone', 'Timber'), (2, 2, 'Stone', 'PlasterUp'), (3, 3, 'Plaster', 'PlasterUp')]\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:56:59  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("town","overview_v2",(0,-30,42),(-1,16,2),lens=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\overview_v2.png\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:57:47  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("town","merchant_v3",(-13,11.5,13.5),(-20,23,5.5),lens=35))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\merchant_v3.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 15:58:35  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("town","terr_eq_v1",(-3,-6,13),(-7.5,6,6.2),lens=35))
print(ws_shot("town","terr_uneq_v1",(7,-5,14),(1.5,6,7.5),lens=35))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\terr_eq_v1.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces
# \\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\terr_uneq_v1.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 15:59:24  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("town","passage_v4",(6.5,-4.5,2.6),(3.8,3,2.2),lens=28))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\passage_v4.png\n"}

# ==============================================================================================================
# [0015] 2026-09-23 16:00:33  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
before=set(o.name for o in asm.objects)
res=[]
for i,s in enumerate((1,2,3)):
    r=g["build_terrace"](asm,(200,-20*i,0),units=8,seed=s)
    res.append([(u["w"],u["s"]) for u in r["units"]])
print(res, time.time()-t0)
print(ws_shot("town","terr8_test",(200,-75,55),(200,-20,3),lens=30))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: [[(1, 3), (3, 4), (1, 4), (2, 2), (2, 2), (2, 4), (2, 2), (3, 3)], [(2, 3), (2, 2), (2, 4), (2, 4), (2, 2), (2,
#  2), (2, 2), (2, 4)], [(2, 3), (2, 4), (3, 3), (3, 2), (2, 3), (2, 2), (2, 4), (2, 3)]] 0.7857975959777832\nC:\\Users\\danie\\AppData\\Roaming\\Claude
# \\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\terr8_tes
# t.png\n2.1020352840423584\n"}

# ==============================================================================================================
# [0016] 2026-09-23 16:01:31  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.collections["WS_town_Assembly"]
rm=[o for o in sc.objects if o.location.x>150]
for o in rm: bpy.data.objects.remove(o)
print(len(rm), len(sc.objects))
for n in ("SM_VK_Prop_Lantern","SM_VK_Wall_Timber_Door","SM_VK_Wall_Timber","SM_VK_Prop_FlowerBox"):
    o=bpy.data.objects[n]; from mathutils import Vector
    bb=[Vector(c) for c in o.bound_box]; print(n,[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])
# ---- result ----
# {"result":"Code executed successfully: 770 432\nSM_VK_Prop_Lantern [-0.16, -0.58, -0.44] [0.16, 0.1, 0.18]\nSM_VK_Wall_Timber_Door [-1.61, -0.62, -0.2
# ] [1.52, 0.18, 2.81]\nSM_VK_Wall_Timber [-1.61, -0.62, -0.2] [1.52, 0.18, 2.81]\nSM_VK_Prop_FlowerBox [-0.75, -0.28, -0.22] [0.71, 0.26, 0.67]\n"}

# ==============================================================================================================
# [0017] 2026-09-23 16:03:35  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py"
src=open(P_,encoding="utf8").read()
t=bpy.data.texts.get("ws_town"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
g["twn_clear_assembly"](asm)
import math
r=[]
r.append(g["build_terrace"](asm,(0,10,math.pi),units=6,seed=0))
r.append(g["build_merchant_house"](asm,(-20,26,0),seed=0))
r.append(g["build_townhouse_gablefront"](asm,(-3,26,0),seed=0))
r.append(g["build_corner_house"](asm,(14,26,0),seed=0))
print([(u["w"],u["s"],u["g"],u["u"],u["st"]["roof"],u.get("gal")) for u in r[0]["units"]], len(asm.objects), time.time()-t0)
print(ws_shot("town","overview_v3",(-4,-12,40),(-2,17,2),lens=30))
# ---- result ----
# {"result":"Code executed successfully: [(2, 4, 'Stone', 'StoneUp', 'Slate', False), (3, 2, 'Stone', 'PlasterUp', 'Slate', False), (3, 3, 'Stone', 'Tim
# ber', 'Green', False), (3, 2, 'Stone', 'Timber', 'Slate', False), (2, 3, 'Stone', 'StoneUp', 'Red', False), (3, 4, 'Plaster', 'PlasterUp', 'Shingle', 
# False)] 463 3.3116748332977295\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41
# c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\overview_v3.png\n"}

# ==============================================================================================================
# [0018] 2026-09-23 16:04:03  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
before=set(o.name for o in asm.objects)
out={}
for s in range(1,9):
    r=g["build_terrace"](asm,(300,0,0),units=6,seed=s)
    out[s]=[(u["w"],u["s"],u["g"][0],u["u"][:2],u["st"]["roof"][:2],int(bool(u.get("gal")))) for u in r["units"]]
    for o in [o for o in asm.objects if o.name not in before]: bpy.data.objects.remove(o)
for s,v in out.items(): print(s,sum(u[0] for u in v),v)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1 12 [(1, 3, 'P', 'Ti', 'Sl', 0), (3, 4, 'P', 'Ti', 'Sh', 0), (2, 3, 'P', 'Ti', 'Bl', 1), (2, 4, 'P', 'Ti', 'Re
# ', 0), (2, 3, 'S', 'Ti', 'Gr', 0), (2, 4, 'P', 'Pl', 'Bl', 0)]\n2 13 [(1, 3, 'P', 'Ti', 'Sh', 0), (2, 3, 'P', 'Pl', 'Bl', 0), (3, 2, 'S', 'St', 'Re', 
# 0), (3, 4, 'S', 'Pl', 'Sl', 0), (2, 3, 'S', 'Ti', 'Sh', 0), (2, 4, 'S', 'Ti', 'Sh', 1)]\n3 12 [(2, 3, 'S', 'Pl', 'Gr', 0), (2, 4, 'S', 'St', 'Sh', 0),
#  (2, 3, 'P', 'Pl', 'Re', 0), (2, 4, 'S', 'St', 'Sl', 0), (2, 2, 'P', 'Pl', 'Sh', 0), (2, 3, 'S', 'St', 'Re', 0)]\n4 13 [(2, 3, 'P', 'Ti', 'Sl', 1), (2
# , 4, 'S', 'Pl', 'Sl', 0), (2, 2, 'S', 'Ti', 'Sl', 0), (2, 4, 'S', 'Ti', 'Bl', 0), (2, 2, 'P', 'Ti', 'Sh', 1), (3, 3, 'P', 'Ti', 'Sl', 0)]\n5 11 [(1, 4
# , 'S', 'St', 'Sh', 0), (3, 4, 'S', 'Ti', 'Sl', 1), (1, 2, 'P', 'Pl', 'Re', 0), (2, 4, 'S', 'Pl', 'Gr', 0), (2, 3, 'S', 'St', 'Re', 0), (2, 4, 'P', 'Pl

# ==============================================================================================================
# [0019] 2026-09-23 16:04:50  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
for o in [o for o in asm.objects if 5<o.location.y<15 or o.location.y<5]: pass
# remove only terrace instances: rebuild everything for simplicity
g["twn_clear_assembly"](asm)
g["build_terrace"](asm,(0,10,math.pi),units=6,seed=2)
g["build_merchant_house"](asm,(-20,26,0),seed=0)
g["build_townhouse_gablefront"](asm,(-3,26,0),seed=0)
g["build_corner_house"](asm,(14,26,0),seed=0)
print(len(asm.objects), time.time()-t0)
print(ws_shot("town","terr_back_v1",(-6,-10,22),(-2,8,4),lens=30))
# ---- result ----
# {"result":"Code executed successfully: 439 3.5624594688415527\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9
# -dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\terr_back_v1.png\n"}

# ==============================================================================================================
# [0020] 2026-09-23 16:05:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("town","street_v1",(-30,15.5,5.5),(-4,18.5,5),lens=28))
print(ws_shot("town","street_v2",(22,16,6),(-2,18,5.5),lens=28))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\street_v1.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\
# \ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\street_v2.png\n"}

# ==============================================================================================================
# [0021] 2026-09-23 16:06:06  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("town","gallery_terr_v1",(-11,-1.5,5.5),(-16.5,6.2,3.2),lens=30))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\gallery_terr_v1.png\n"}

# ==============================================================================================================
# [0022] 2026-09-23 16:07:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
L={
 "SM_VK_Wall_StoneUp":(-17,-14,0),"SM_VK_Wall_StoneUp_Window":(-13,-14,0),"SM_VK_Wall_StoneUp_Twin":(-9,-14,0),
 "SM_VK_Wall_StoneUp_Slit":(-5,-14,0),"SM_VK_Wall_StoneUp_Loading":(-1,-14,0),"SM_VK_Wall_StoneUp_Door":(3,-14,0),
 "SM_VK_Corner_StoneUp":(6.6,-14,0),"SM_VK_InnerCorner_StoneUp":(8.6,-14.4,0),
 "SM_VK_Wall_PlasterUp":(-17,-21,0),"SM_VK_Wall_PlasterUp_Window":(-13,-21,0),"SM_VK_Wall_PlasterUp_Oxeye":(-9,-21,0),
 "SM_VK_Corner_PlasterUp":(-6.3,-21,0),"SM_VK_InnerCorner_PlasterUp":(-5.2,-21.4,0),
 "SM_VK_Wall_Stone_Shop":(-1.5,-21,0),"SM_VK_Wall_Plaster_Shop":(2.5,-21,0),"SM_VK_Roof_Pent":(7.2,-21,0.9),
 "SM_VK_Wall_Stone_Passage":(-16,-33,0),"SM_VK_Passage_Vault":(-11,-33,0),
 "SM_VK_Gallery_Timber":(-4.5,-33,0),"SM_VK_Gallery_Side":(-6.0,-33,0),"SM_VK_Gallery_End":(0.5,-33,0),
 "SM_VK_Turret_Corbel":(-15.4,-42,1.75),"SM_VK_Turret_Seg":(-11.4,-42,0),"SM_VK_Turret_Seg_Stone":(-7.4,-42,0),"SM_VK_Turret_Cap":(-2.9,-42,0.25),
 "SM_VK_Stoop_Stone":(1.5,-42,0),"SM_VK_Stair_Stone_Ext":(5.4,-42,0),"SM_VK_Prop_CellarHatch":(11.6,-42,0),"SM_VK_Prop_HoistBeam":(10.6,-33,5.1),
}
goods=["Bread","Produce","Cloth","Pots","Tools","Meat","Candles","Fish"]
for i,gn in enumerate(goods): L["SM_VK_Prop_ShopGoods_"+gn]=(-17+2.35*i,-26.5,0.45 if gn=="Cloth" else 0)
miss=[o.name for o in coll.objects if o.name not in L]
for o in coll.objects:
    if o.name in L: o.location=L[o.name]; o.rotation_euler=(0,0,0)
print("missing",miss)
asm.hide_render=True
try:
    print(ws_shot("town","cat_v4",(-2,-70,27),(-2,-27,0.5),lens=30))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: missing []\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f5
# 6\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\cat_v4.png\n"}

# ==============================================================================================================
# [0023] 2026-09-23 16:08:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
L={
 "SM_VK_Wall_StoneUp":(-16,-15,0),"SM_VK_Wall_StoneUp_Window":(-12,-15,0),"SM_VK_Wall_StoneUp_Twin":(-8,-15,0),
 "SM_VK_Wall_StoneUp_Slit":(-4,-15,0),"SM_VK_Wall_StoneUp_Loading":(0,-15,0),"SM_VK_Wall_StoneUp_Door":(4,-15,0),
 "SM_VK_Corner_StoneUp":(7.6,-15,0),"SM_VK_InnerCorner_StoneUp":(9.6,-15.4,0),
 "SM_VK_Wall_PlasterUp":(-16,-22,0),"SM_VK_Wall_PlasterUp_Window":(-12,-22,0),"SM_VK_Wall_PlasterUp_Oxeye":(-8,-22,0),
 "SM_VK_Corner_PlasterUp":(-5.3,-22,0),"SM_VK_InnerCorner_PlasterUp":(-4.2,-22.4,0),
 "SM_VK_Wall_Stone_Shop":(-0.5,-22,0),"SM_VK_Wall_Plaster_Shop":(3.5,-22,0),"SM_VK_Roof_Pent":(8.2,-22,0.9),
 "SM_VK_Wall_Stone_Passage":(-15,-31,0),"SM_VK_Passage_Vault":(-10,-31,0),
 "SM_VK_Gallery_Timber":(-3.5,-31,0),"SM_VK_Gallery_Side":(-5.0,-31,0),"SM_VK_Gallery_End":(1.5,-31,0),"SM_VK_Prop_HoistBeam":(6.0,-30,5.1),
 "SM_VK_Turret_Corbel":(-14.4,-37.5,1.75),"SM_VK_Turret_Seg":(-10.4,-37.5,0),"SM_VK_Turret_Seg_Stone":(-6.4,-37.5,0),"SM_VK_Turret_Cap":(-1.9,-37.5,0.25),
 "SM_VK_Stoop_Stone":(2.8,-37.5,0),"SM_VK_Stair_Stone_Ext":(7.0,-37.5,0),"SM_VK_Prop_CellarHatch":(12.6,-37.5,0),
}
goods=["Bread","Produce","Cloth","Pots","Tools","Meat","Candles","Fish"]
for i,gn in enumerate(goods): L["SM_VK_Prop_ShopGoods_"+gn]=(-9.4+2.3*i,-43,0.45 if gn=="Cloth" else 0)
for o in coll.objects:
    if o.name in L: o.location=L[o.name]; o.rotation_euler=(0,0,0)
asm.hide_render=True
try:
    print(ws_shot("town","cat_v5",(-1.5,-62,19),(-1.5,-29,1.0),lens=30,res=(1600,900)))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\cat_v5.png\n"}

# ==============================================================================================================
# [0024] 2026-09-23 16:09:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
asm.hide_render=True
try:
    print(ws_shot("town","cat_v6",(-1.5,-57.5,17.5),(-1.5,-28.5,1.2),lens=33,res=(1600,900)))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\cat_v6.png\n"}

# ==============================================================================================================
# [0025] 2026-09-23 16:10:24  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
asm.hide_render=True
try:
    print(ws_shot("town","cat_v7",(-1.5,-61,19.5),(-1.5,-31.5,0.3),lens=31,res=(1600,900)))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\cat_v7.png\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:10:53  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","colA",(14,-3,35.2),(-3,18,3),lens=30))
    print(ws_shot("town","colB",(14,39,35.2),(-3,18,3),lens=30))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\colA.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03
# f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\colB.png\n"}

# ==============================================================================================================
# [0027] 2026-09-23 16:11:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","colC",(31.5,6,45),(-3,17,3),lens=30))
    print(ws_shot("town","colD",(18.2,-11.3,45.1),(-3,17,3),lens=30))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\colC.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03
# f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\colD.png\n"}

# ==============================================================================================================
# [0028] 2026-09-23 16:13:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","streetE_v1",(21,12.5,8.5),(-1,19.5,5.0),lens=26))
    print(ws_shot("town","merchant34_v1",(-40,9,11),(-20,24.5,6.2),lens=32))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\streetE_v1.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces
# \\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\merchant34_v1.png\n"}

# ==============================================================================================================
# [0029] 2026-09-23 16:13:44  blender  ok
# ==============================================================================================================
import bpy
vk=[o.name for o in bpy.data.collections["VK_Pieces"].objects]
print(len(vk))
print([n for n in vk if any(s in n.lower() for s in ("road","cobble","pav","street","plaza","path","ground","floor","tile","square"))])
# ---- result ----
# {"result":"Code executed successfully: 110\n[]\n"}

# ==============================================================================================================
# [0030] 2026-09-23 16:14:49  blender  ok
# ==============================================================================================================
import bpy
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py"
src=open(P_,encoding="utf8").read()
t=bpy.data.texts.get("ws_town"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
o=g["twn_demo_paving"](asm,-27,21,13.0,22.8)
print(o.name, o.dimensions[:])
coll.hide_render=True
try:
    print(ws_shot("town","streetE_v2",(27,16.5,8.5),(0,18.5,4.5),lens=27))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: WS_town_DemoPaving (48.0, 9.799999237060547, 0.05999999865889549)\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\
# scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\streetE_v2.
# png\n"}

# ==============================================================================================================
# [0031] 2026-09-23 16:16:09  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","turret_eave_v1",(3.5,15.5,11.5),(10.6,22.5,9.2),lens=35))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\turret_eave_v1.png\n"}

# ==============================================================================================================
# [0032] 2026-09-23 16:17:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
asm.hide_render=True
try:
    print(ws_shot("town","goods_v2",(-1.3,-51,4.2),(-1.3,-43,0.2),lens=22))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\goods_v2.png\n"}

# ==============================================================================================================
# [0033] 2026-09-23 16:18:22  blender  ok
# ==============================================================================================================
import bpy
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py"
src=open(P_,encoding="utf8").read()
t=bpy.data.texts.get("ws_town"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
objs=ws_build("town",g=g,names=["SM_VK_Prop_ShopGoods_Tools"])
print(ws_stats(objs))
sc,coll,asm=ws_scene("town")
asm.hide_render=True
try:
    print(ws_shot("town","goods_tools_v1",(4.5,-46.5,2.0),(5.1,-43,0.2),lens=35))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Prop_ShopGoods_Tools', 'tris': 1620, 'bbox': [1.85, 0.49, 0.45], 'zmin': 0.0, 'mats': [2, 5, 2
# 1, 23, 25]}]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348
# ea\\scratch-2026-09-23-d49817\\renders2\\town\\goods_tools_v1.png\n"}

# ==============================================================================================================
# [0034] 2026-09-23 16:18:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
asm.hide_render=True
try:
    print(ws_shot("town","goods_tools_v1",(-0.6,-46.3,1.9),(-0.2,-43,0.25),lens=35))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\goods_tools_v1.png\n"}

# ==============================================================================================================
# [0035] 2026-09-23 16:19:33  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects["SM_VK_Prop_ShopGoods_Tools"]
for i,m in enumerate(o.data.materials):
    if i in (5,21,25,18,16,23):
        b=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None) if m.use_nodes else None
        tex=[n.image.name for n in m.node_tree.nodes if n.type=="TEX_IMAGE" and n.image] if m.use_nodes else []
        print(i,m.name, b.inputs["Metallic"].default_value if b else None, tuple(round(v,2) for v in b.inputs["Base Color"].default_value) if b else None, tex[:2])
# ---- result ----
# {"result":"Code executed successfully: 5 M_VK_Iron 0.0 (0.8, 0.8, 0.8, 1.0) ['T_VK_Iron_BC', 'T_VK_Iron_N']\n16 M_VK_Hay 0.0 (0.8, 0.8, 0.8, 1.0) ['T_
# VK_Straw_BC', 'T_VK_Straw_N']\n18 M_VK_Water 0.0 (0.8, 0.8, 0.8, 1.0) ['T_VK_Water_BC', 'T_VK_Water_N']\n21 M_VK_Steel 0.8999999761581421 (0.8, 0.8, 0
# .8, 1.0) ['T_VK_Iron_BC', 'T_VK_Iron_N']\n23 M_VK_Planks 0.0 (0.8, 0.8, 0.8, 1.0) ['T_VK_Planks_BC', 'T_VK_Planks_N']\n25 M_VK_Burlap 0.0 (0.8, 0.8, 0
# .8, 1.0) ['T_VK_Burlap_BC', 'T_VK_Burlap_N']\n"}

# ==============================================================================================================
# [0036] 2026-09-23 16:20:04  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
objs=ws_build("town", g=g)
print(len(objs), len(g["WS_SPECS"]), time.time()-t0)
st=ws_stats(objs)
for s in st: print(s["name"][6:],s["tris"],s["bbox"],s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: 37 37 2.1444902420043945\nWall_StoneUp 732 [3.0, 0.77, 2.91] -0.11\nWall_StoneUp_Window 1806 [3.0, 1.1, 2.91] -
# 0.11\nWall_StoneUp_Twin 2284 [3.0, 0.84, 2.91] -0.11\nWall_StoneUp_Slit 1436 [3.0, 0.77, 2.91] -0.11\nWall_StoneUp_Loading 2742 [3.0, 1.22, 2.91] -0.1
# 1\nWall_StoneUp_Door 2348 [3.0, 0.81, 2.91] -0.11\nCorner_StoneUp 768 [1.11, 1.16, 2.86] -0.06\nInnerCorner_StoneUp 648 [0.63, 0.63, 2.58] 0.21\nWall_
# PlasterUp 1260 [3.0, 0.72, 2.92] -0.12\nWall_PlasterUp_Window 1486 [3.0, 1.05, 2.92] -0.12\nWall_PlasterUp_Oxeye 1328 [3.0, 0.73, 2.92] -0.12\nCorner_
# PlasterUp 284 [0.74, 0.74, 3.03] -0.22\nInnerCorner_PlasterUp 88 [0.3, 0.3, 2.82] -0.02\nWall_Stone_Shop 2556 [3.04, 1.25, 3.63] -0.6\nWall_Plaster_Sh
# op 2280 [3.13, 1.27, 3.6] -0.6\nProp_ShopGoods_Bread 1984 [1.9, 0.5, 0.32] 0.0\nProp_ShopGoods_Produce 1312 [1.97, 0.59, 0.36] 0.0\nProp_ShopGoods_Clo

# ==============================================================================================================
# [0037] 2026-09-23 16:20:49  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town")
sc,coll,asm=ws_scene("town")
g["twn_clear_assembly"](asm)
out={}
out["terrace"]=g["build_terrace"](asm,(0,10,math.pi),units=6,seed=2)
out["merchant"]=g["build_merchant_house"](asm,(-20,26,0),seed=0)
out["townhouse"]=g["build_townhouse_gablefront"](asm,(-3,26,0),seed=0)
out["corner"]=g["build_corner_house"](asm,(14,26,0),seed=0)
g["twn_demo_paving"](asm,-27,21,13.0,22.8)
print({k:{kk:vv for kk,vv in v.items() if kk!="units"} for k,v in out.items()})
print([(u["w"],u["s"],u["g"],u["u"],u["st"]["roof"],u["st"]["plaster"],u.get("gal")) for u in out["terrace"]["units"]])
print(len(asm.objects), time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'terrace': {'footprint': (13, 2)}, 'merchant': {'footprint': (3, 2), 'lot': (3, 3), 'wall_top': 8.6}, 'townhou
# se': {'footprint': (2, 3), 'lot': (4, 3), 'wall_top': 8.6}, 'corner': {'footprint': (3, 3), 'lot': (4, 4), 'wall_top': 8.6}}\n[(1, 3, 'Plaster', 'Timb
# er', 'Shingle', 'White', False), (2, 3, 'Plaster', 'PlasterUp', 'Blue', 'Sage', False), (3, 2, 'Stone', 'StoneUp', 'Red', 'Sky', False), (3, 4, 'Stone
# ', 'PlasterUp', 'Slate', 'Sage', False), (2, 3, 'Stone', 'Timber', 'Shingle', 'Sky', False), (2, 4, 'Stone', 'Timber', 'Shingle', 'Ochre', True)]\n440
#  3.5975799560546875\n"}

# ==============================================================================================================
# [0038] 2026-09-23 16:21:18  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
asm.hide_render=True
try:
    print(ws_shot("town","catalog_final",(-1.5,-61,19.5),(-1.5,-31.5,0.3),lens=31,res=(1600,900)))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\catalog_final.png\n"}

# ==============================================================================================================
# [0039] 2026-09-23 16:21:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","hero_street",(30,15.8,9.5),(-2,19.2,4.6),lens=28,res=(1600,900)))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\hero_street.png\n"}

# ==============================================================================================================
# [0040] 2026-09-23 16:22:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","hero_street",(41,11.5,14),(0,19,4.2),lens=32,res=(1600,900)))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\hero_street.png\n"}

# ==============================================================================================================
# [0041] 2026-09-23 16:23:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","hero_merchant",(-41,8.5,11.5),(-19.5,24.5,6.0),lens=32,res=(1600,900)))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\hero_merchant.png\n"}

# ==============================================================================================================
# [0042] 2026-09-23 16:24:03  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","hero_colony",(18.2,-11.3,45.1),(-3,17,3),lens=30,res=(1600,900)))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\hero_colony.png\n"}

# ==============================================================================================================
# [0043] 2026-09-23 16:24:41  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("town")
coll.hide_render=True
try:
    print(ws_shot("town","hero_colony",(19.5,-13.5,47),(-1.5,15.5,3),lens=28,res=(1600,900)))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\hero_colony.png\n"}

# ==============================================================================================================
# [0044] 2026-09-23 16:25:04  blender  ok
# ==============================================================================================================
import bpy
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py"
src=open(P_,encoding="utf8").read()
print(src==bpy.data.texts["ws_town"].as_string(), len(src))
print(len(bpy.data.collections["WS_town_Pieces"].objects), len(bpy.data.collections["WS_town_Assembly"].objects))
# ---- result ----
# {"result":"Code executed successfully: True 76593\n37 440\n"}
