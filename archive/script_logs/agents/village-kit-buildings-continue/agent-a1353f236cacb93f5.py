# village-kit-buildings-continue / agent-a1353f236cacb93f5.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:45:57  blender  ok
# ==============================================================================================================
import bpy, hashlib
t=bpy.data.texts.get("ws_skyline")
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
bt=t.as_string() if t else ""
print("text exists",bool(t),"len",len(bt),"file len",len(src),"equal",bt.rstrip()==src.rstrip())
sc=bpy.data.scenes.get("WS_skyline")
print("scene",sc)
for cn in ("WS_skyline_Pieces","WS_skyline_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, len(c.objects) if c else None)
c=bpy.data.collections.get("WS_skyline_Pieces")
if c: print(sorted(o.name for o in c.objects))
# ---- result ----
# {"result":"Code executed successfully: text exists True len 46382 file len 46382 equal True\nscene <bpy_struct, Scene(\"WS_skyline\") at 0x000001CCB7A
# EC088>\nWS_skyline_Pieces 35\nWS_skyline_Assembly 81\n['SM_VK_Banner_Pole', 'SM_VK_Banner_Roof', 'SM_VK_Banner_Wall', 'SM_VK_Chimney_Gable_H24', 'SM_V
# K_Chimney_Gable_H30', 'SM_VK_Chimney_Gable_H58', 'SM_VK_Chimney_Party', 'SM_VK_Emblem_Ridge_Anvil', 'SM_VK_Emblem_Ridge_Axe', 'SM_VK_Emblem_Ridge_Book
# ', 'SM_VK_Emblem_Ridge_Fish', 'SM_VK_Emblem_Ridge_Horseshoe', 'SM_VK_Emblem_Ridge_Key', 'SM_VK_Emblem_Ridge_Pretzel', 'SM_VK_Emblem_Ridge_Sheaf', 'SM_
# VK_Emblem_Ridge_Shield', 'SM_VK_Emblem_Ridge_Tankard', 'SM_VK_Prop_Bunting_6', 'SM_VK_Prop_Bunting_9', 'SM_VK_RoofThatch_HalfHip', 'SM_VK_RoofThatch_S
# ingle', 'SM_VK_Roof_Bellcote', 'SM_VK_Roof_CrossGable', 'SM_VK_Roof_Firewall', 'SM_VK_Roof_Gable_Flush', 'SM_VK_Roof_Gable_Hoist', 'SM_VK_Roof_Gable_S

# ==============================================================================================================
# [0002] 2026-09-23 15:47:09  blender  ok
# ==============================================================================================================
import bpy
from collections import Counter
asm=bpy.data.collections["WS_skyline_Assembly"]
c=Counter(o.data.name.split(".")[0] if o.data else "none" for o in asm.objects)
print(len(asm.objects))
xs=[o.location.x for o in asm.objects]; ys=[o.location.y for o in asm.objects]
print(min(xs),max(xs),min(ys),max(ys))
print(sorted(Counter(o.name.rsplit("_inst",1)[0] for o in asm.objects).items()))
p=bpy.data.collections["WS_skyline_Pieces"]
print([(o.name,tuple(round(v,1) for v in o.location),o.hide_render) for o in p.objects][:40])
# ---- result ----
# {"result":"Code executed successfully: 81\n-3.0 62.5 -3.0 3.0\n[('SM_VK_Corner_Stone', 24), ('SM_VK_RoofThatch_Gable', 1), ('SM_VK_RoofThatch_HalfHip'
# , 1), ('SM_VK_RoofThatch_Single', 1), ('SM_VK_Roof_CrossGable', 1), ('SM_VK_Roof_Gable', 4), ('SM_VK_Roof_HalfHip', 1), ('SM_VK_Roof_Hip_Plain', 1), (
# 'SM_VK_Roof_Single', 1), ('SM_VK_Wall_Stone', 39), ('SM_VK_Wall_Stone_Window', 7)]\n[('SM_VK_Roof_Single', (0.0, 0.0, 0.0), True), ('SM_VK_RoofThatch_
# Single', (0.0, 0.0, 0.0), True), ('SM_VK_Roof_Hip_Plain', (0.0, 0.0, 0.0), True), ('SM_VK_Roof_HalfHip', (0.0, 0.0, 0.0), True), ('SM_VK_RoofThatch_Ha
# lfHip', (0.0, 0.0, 0.0), True), ('SM_VK_Roof_CrossGable', (0.0, 0.0, 0.0), True), ('SM_VK_Chimney_Gable_H30', (0.0, 0.0, 0.0), True), ('SM_VK_Chimney_
# Gable_H58', (0.0, 0.0, 0.0), True), ('SM_VK_Chimney_Gable_H24', (0.0, 0.0, 0.0), True), ('SM_VK_Chimney_Party', (0.0, 0.0, 0.0), True), ('SM_VK_Roof_V

# ==============================================================================================================
# [0003] 2026-09-23 15:47:57  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("skyline")
objs=ws_build("skyline",g=g)
print(len(objs), round(time.time()-t0,1))
for o in objs: o.hide_render=False; o.hide_viewport=False
ws_grid(objs,cols=7,sx=9,sy=11,origin=(0,-20))
st=ws_stats(objs)
for s in st: print(s["name"],s["tris"],s["bbox"],s["zmin"],len(s["mats"]))
# ---- result ----
# {"result":"Code executed successfully: 35 2.7\nSM_VK_Roof_Single 9008 [5.4, 9.04, 5.89] -0.7 4\nSM_VK_RoofThatch_Single 6600 [5.32, 9.13, 5.17] -0.77 
# 4\nSM_VK_Roof_Hip_Plain 6936 [4.68, 8.94, 5.07] -0.59 2\nSM_VK_Chimney_Gable_H30 1948 [1.94, 1.49, 9.3] -0.6 4\nSM_VK_Chimney_Gable_H58 1776 [1.94, 1.
# 49, 12.1] -0.6 4\nSM_VK_Chimney_Gable_H24 1688 [1.94, 1.49, 8.7] -0.6 4\nSM_VK_Chimney_Party 720 [2.06, 1.25, 3.21] -1.2 4\nSM_VK_Roof_Vent 932 [1.75,
#  0.94, 1.75] -0.69 4\nSM_VK_Roof_Gable_Flush 3376 [3.39, 8.88, 5.79] -0.58 5\nSM_VK_Roof_Firewall 800 [0.72, 7.84, 5.56] -0.35 3\nSM_VK_Roof_Gable_Ste
# pped 3706 [3.39, 8.88, 6.71] -0.58 8\nSM_VK_Roof_Gable_Hoist 6540 [5.08, 9.04, 7.48] -2.29 7\nSM_VK_Roof_HalfHip 6602 [4.12, 8.99, 5.2] -0.65 4\nSM_VK
# _RoofThatch_HalfHip 6142 [4.22, 9.08, 5.28] -0.76 4\nSM_VK_Roof_CrossGable 3912 [3.31, 8.8, 5.09] -0.67 4\nSM_VK_Roof_Mid_CapL 3928 [3.19, 9.02, 5.1] 

# ==============================================================================================================
# [0004] 2026-09-23 15:49:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("skyline","catalog_v2",(27,-92,40),(27,-40,2),lens=32,res=(1600,900),samples=16)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_v2.png\n"}

# ==============================================================================================================
# [0005] 2026-09-23 15:52:26  blender  ok
# ==============================================================================================================
import bpy
print(bpy.data.materials.get("MC_WK_Dirt"))
for n in ("SM_VK_Wall_Timber","SM_VK_Wall_Stone","SM_VK_Wall_Plaster","SM_VK_Corner_Timber","SM_VK_Porch","SM_VK_Prop_LampPost","SM_VK_Wall_Timber_Window"):
    o=bpy.data.objects.get(n)
    if o:
        ys=[v.co.y for v in o.data.vertices]; zs=[v.co.z for v in o.data.vertices]; xs=[v.co.x for v in o.data.vertices]
        print(n,round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2))
print([m.name for m in bpy.data.materials if "Dirt" in m.name or "Road" in m.name or "Cobble" in m.name][:20])
# ---- result ----
# {"result":"Code executed successfully: <bpy_struct, Material(\"MC_WK_Dirt\") at 0x000001CB8AE12CC8>\nSM_VK_Wall_Timber -1.61 1.52 -0.62 0.18 -0.2 2.81
# \nSM_VK_Wall_Stone -1.52 1.52 -0.53 0.28 -0.11 3.0\nSM_VK_Wall_Plaster -1.61 1.52 -0.5 0.26 -0.11 3.0\nSM_VK_Corner_Timber -0.61 0.13 -0.61 0.13 -0.97
#  2.81\nSM_VK_Porch -1.55 1.55 -2.26 0.02 -0.01 3.33\nSM_VK_Prop_LampPost -0.22 0.22 -0.83 0.22 0.0 2.9\nSM_VK_Wall_Timber_Window -1.61 1.52 -0.62 0.18
#  -0.2 2.81\n['MC_WK_Dirt']\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:54:22  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_skyline"); t.clear(); t.write(src)
g=ws_ns("skyline")
sc,coll,asm=ws_scene("skyline")
ws_clear_assembly("skyline")
g["build_skyline_street"](asm,(-18,40,0),seed=0)
print(len(asm.objects), round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: 261 0.7\n"}

# ==============================================================================================================
# [0007] 2026-09-23 15:55:13  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","street_v1",(22,2,20),(0,34,4),lens=30,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\street_v1.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:55:52  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","street_v1b",(28,14,16),(-4,36,4),lens=28,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\street_v1b.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 15:56:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","street_v1c",(-28,26,7),(0,36,5),lens=28,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\street_v1c.png\n"}

# ==============================================================================================================
# [0010] 2026-09-23 15:56:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","street_colony_v1",(4,7.5,33.6),(0,33,3),lens=35,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\street_colony_v1.png\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:57:25  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_terrace1",(-6,26,13),(-5,40,9),lens=30,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_terrace1.png\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:58:30  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_terrace2",(10,27,11),(4,40,9),lens=30,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_terrace2.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 16:00:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_south1",(3,38,9),(-6,25,6),lens=28,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_south1.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 16:00:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_south1",(5,34,10),(-7,25,5),lens=26,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_south1.png\n"}

# ==============================================================================================================
# [0015] 2026-09-23 16:01:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_south2",(-4,35.5,6.5),(-10,25,7),lens=24,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_south2.png\n"}

# ==============================================================================================================
# [0016] 2026-09-23 16:01:35  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_hoist",(-21,31,7),(-12,24.5,7),lens=26,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_hoist.png\n"}

# ==============================================================================================================
# [0017] 2026-09-23 16:02:35  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_skyline"); t.clear(); t.write(src)
g=ws_ns("skyline"); sc,coll,asm=ws_scene("skyline")
ws_clear_assembly("skyline")
g["build_skyline_street"](asm,(-18,40,0),seed=0)
objs=[bpy.data.objects[n] for n,_,_ in g["WS_SPECS"]]
ws_grid(objs,cols=7,sx=8.5,sy=11,origin=(-25.5,-8))
print(ws_shot("skyline","close_west",(-24,29,6),(-14,38,6),lens=26,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_west.png\n"}

# ==============================================================================================================
# [0018] 2026-09-23 16:03:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_east",(30,30,8),(18,38,6),lens=26,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_east.png\n"}

# ==============================================================================================================
# [0019] 2026-09-23 16:03:35  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_smithy",(17,35,7),(8,24.5,4),lens=26,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_smithy.png\n"}

# ==============================================================================================================
# [0020] 2026-09-23 16:04:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","catalog_v3",(0,-88,36),(0,-31,1),lens=30,res=(1600,900),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_v3.png\n"}

# ==============================================================================================================
# [0021] 2026-09-23 16:05:21  blender  ok
# ==============================================================================================================
import bpy
from collections import defaultdict
def seam(name,xs=-1.5):
    me=bpy.data.objects[name].data; d=defaultdict(lambda:-99)
    for v in me.vertices:
        if abs(v.co.x-xs)<0.004 and abs(v.co.y)<4.3:
            b=round(v.co.y/0.25)
            d[b]=max(d[b],v.co.z)
    return d
ref=seam("SM_VK_Roof_Mid"); refR=seam("SM_VK_Roof_Mid",1.5)
refT=seam("SM_VK_RoofThatch_Mid"); 
for n,x,r in [("SM_VK_Roof_Hip_Plain",-1.5,ref),("SM_VK_Roof_HalfHip",-1.5,ref),("SM_VK_RoofThatch_HalfHip",-1.5,refT),
              ("SM_VK_Roof_Gable_Flush",-1.5,ref),("SM_VK_Roof_Gable_Stepped",-1.5,ref),("SM_VK_Roof_Gable_Hoist",-1.5,ref),
              ("SM_VK_Roof_CrossGable",-1.5,ref),("SM_VK_Roof_CrossGable",1.5,refR),("SM_VK_Roof_Mid_CapL",1.5,refR),("SM_VK_Roof_Mid_CapR",-1.5,ref),
              ("SM_VK_Roof_Mid_Hatch",-1.5,ref),("SM_VK_Roof_Mid_Skylight",1.5,refR),("SM_VK_Roof_Gable",-1.5,ref)]:
    d=seam(n,x); common=[b for b in r if b in d]
    dev=max(abs(d[b]-r[b]) for b in common) if common else None
    miss=len([b for b in r if b not in d])
    print(n,x,"bins",len(common),"missing",miss,"maxdev",round(dev,4) if dev is not None else None)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Hip_Plain -1.5 bins 29 missing 0 maxdev 0.5299\nSM_VK_Roof_HalfHip -1.5 bins 29 missing 0 maxdev 0.5
# 299\nSM_VK_RoofThatch_HalfHip -1.5 bins 31 missing 0 maxdev 0.587\nSM_VK_Roof_Gable_Flush -1.5 bins 29 missing 0 maxdev 0.0122\nSM_VK_Roof_Gable_Stepp
# ed -1.5 bins 29 missing 0 maxdev 0.0122\nSM_VK_Roof_Gable_Hoist -1.5 bins 29 missing 0 maxdev 0.0095\nSM_VK_Roof_CrossGable -1.5 bins 26 missing 3 max
# dev 0.5299\nSM_VK_Roof_CrossGable 1.5 bins 26 missing 3 maxdev 0.5299\nSM_VK_Roof_Mid_CapL 1.5 bins 29 missing 0 maxdev 0.0\nSM_VK_Roof_Mid_CapR -1.5 
# bins 29 missing 0 maxdev 0.0\nSM_VK_Roof_Mid_Hatch -1.5 bins 29 missing 0 maxdev 0.0\nSM_VK_Roof_Mid_Skylight 1.5 bins 29 missing 0 maxdev 0.0\nSM_VK_
# Roof_Gable -1.5 bins 29 missing 0 maxdev 0.0105\n"}

# ==============================================================================================================
# [0022] 2026-09-23 16:05:44  blender  ok
# ==============================================================================================================
import bpy
from collections import defaultdict
def seam(name,xs=-1.5):
    me=bpy.data.objects[name].data; d=defaultdict(lambda:-99)
    for v in me.vertices:
        if abs(v.co.x-xs)<0.004 and abs(v.co.y)<4.3:
            b=round(v.co.y/0.25)
            d[b]=max(d[b],v.co.z)
    return d
ref=seam("SM_VK_Roof_Mid")
for n in ("SM_VK_Roof_Hip_Plain","SM_VK_Roof_CrossGable","SM_VK_RoofThatch_HalfHip"):
    d=seam(n); r=ref if "Thatch" not in n else seam("SM_VK_RoofThatch_Mid")
    print(n,[(b*0.25,round(d[b]-r[b],3)) for b in sorted(r) if b in d and abs(d[b]-r[b])>0.02])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Hip_Plain [(-4.25, 0.025), (-3.5, -0.024), (-3.25, 0.364), (-2.75, 0.53), (-2.0, 0.501), (-1.25, 0.5
# 01), (-0.5, 0.501), (-0.25, -0.131), (0.0, 0.36), (0.25, -0.131), (0.5, 0.501), (1.25, 0.501), (2.0, 0.501), (2.75, 0.53), (3.25, 0.364), (3.5, -0.024
# )]\nSM_VK_Roof_CrossGable [(-3.5, 0.222), (-3.25, 0.486), (-2.75, 0.53), (-2.0, 0.501), (-1.25, 0.501), (-0.5, 0.501), (-0.25, -0.131), (0.25, -0.131)
# , (0.5, 0.501), (1.25, 0.501), (2.0, 0.501), (2.75, 0.53), (3.25, 0.364), (3.5, -0.024)]\nSM_VK_RoofThatch_HalfHip [(-4.0, -0.047), (-3.75, 0.412), (-
# 3.5, -0.024), (-3.25, 0.436), (-2.75, 0.587), (-2.0, 0.55), (-1.25, 0.55), (1.25, 0.55), (2.0, 0.55), (2.75, 0.587), (3.25, 0.436), (3.5, -0.024), (3.
# 75, 0.412), (4.0, -0.047), (4.25, 0.389)]\n"}

# ==============================================================================================================
# [0023] 2026-09-23 16:06:10  blender  ok
# ==============================================================================================================
import bpy, math
g={}; exec(bpy.data.texts["vk_helpers"].as_string(),g)
ROOF=g["ROOF"]; THATCH=g["THATCH"]; roof_z=g["roof_z"]
def chk(name,xs):
    me=bpy.data.objects[name].data; vs=me.vertices; worst=0; n=0; wy=None
    for p in me.polygons:
        if p.material_index not in (ROOF,THATCH) or p.normal.z<0.3: continue
        for i in p.vertices:
            v=vs[i].co
            if abs(v.x-xs)<0.004 and abs(v.y)<4.35:
                dz=v.z-roof_z(abs(v.y)); n+=1
                if abs(dz)>abs(worst): worst=dz; wy=round(v.y,2)
    return n,round(worst,4),wy
for n,x in [("SM_VK_Roof_Mid",-1.5),("SM_VK_RoofThatch_Mid",-1.5),("SM_VK_Roof_Hip_Plain",-1.5),("SM_VK_Roof_HalfHip",-1.5),("SM_VK_RoofThatch_HalfHip",-1.5),
              ("SM_VK_Roof_Gable_Flush",-1.5),("SM_VK_Roof_Gable_Stepped",-1.5),("SM_VK_Roof_Gable_Hoist",-1.5),
              ("SM_VK_Roof_CrossGable",-1.5),("SM_VK_Roof_CrossGable",1.5),("SM_VK_Roof_Mid_CapL",1.5),("SM_VK_Roof_Mid_CapR",-1.5),
              ("SM_VK_Roof_Mid_Hatch",-1.5),("SM_VK_Roof_Mid_Hatch",1.5),("SM_VK_Roof_Mid_Skylight",1.5)]:
    print(n,x,chk(n,x))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Mid -1.5 (44, 0.1582, 4.21)\nSM_VK_RoofThatch_Mid -1.5 (66, -0.4228, -4.18)\nSM_VK_Roof_Hip_Plain -1
# .5 (129, 0.29, 0.0)\nSM_VK_Roof_HalfHip -1.5 (130, 0.1576, 4.21)\nSM_VK_RoofThatch_HalfHip -1.5 (148, 0.21, 0.0)\nSM_VK_Roof_Gable_Flush -1.5 (44, 0.1
# 651, -4.25)\nSM_VK_Roof_Gable_Stepped -1.5 (44, 0.1651, -4.25)\nSM_VK_Roof_Gable_Hoist -1.5 (44, 0.1546, 4.19)\nSM_VK_Roof_CrossGable -1.5 (107, 0.280
# 6, -3.6)\nSM_VK_Roof_CrossGable 1.5 (107, 0.2806, -3.6)\nSM_VK_Roof_Mid_CapL 1.5 (44, 0.1581, 4.19)\nSM_VK_Roof_Mid_CapR -1.5 (44, 0.1582, 4.21)\nSM_V
# K_Roof_Mid_Hatch -1.5 (44, 0.1582, 4.21)\nSM_VK_Roof_Mid_Hatch 1.5 (44, 0.1581, 4.19)\nSM_VK_Roof_Mid_Skylight 1.5 (44, 0.1581, 4.19)\n"}

# ==============================================================================================================
# [0024] 2026-09-23 16:06:38  blender  ok
# ==============================================================================================================
import bpy, math
g={}; exec(bpy.data.texts["vk_helpers"].as_string(),g)
ROOF=g["ROOF"]; THATCH=g["THATCH"]; roof_z=g["roof_z"]; TRT=g["TRT"]
def chk(name,xs,lo=0.45,hi=2.9):
    me=bpy.data.objects[name].data; vs=me.vertices; worst=0; n=0; wy=None; zs=[]
    for p in me.polygons:
        if p.material_index not in (ROOF,THATCH) or p.normal.z<0.3: continue
        for i in p.vertices:
            v=vs[i].co
            if abs(v.x-xs)<0.004 and lo<abs(v.y)<hi:
                dz=v.z-roof_z(abs(v.y)); n+=1; zs.append(dz)
                if abs(dz)>abs(worst): worst=dz; wy=round(v.y,2)
    return n,round(worst,4),wy,round(min(zs),3) if zs else None
for n,x in [("SM_VK_Roof_Mid",-1.5),("SM_VK_RoofThatch_Mid",-1.5),("SM_VK_Roof_Hip_Plain",-1.5),("SM_VK_Roof_HalfHip",-1.5),("SM_VK_RoofThatch_HalfHip",-1.5),
              ("SM_VK_Roof_Gable_Flush",-1.5),("SM_VK_Roof_Gable_Hoist",-1.5),
              ("SM_VK_Roof_CrossGable",-1.5),("SM_VK_Roof_CrossGable",1.5),("SM_VK_Roof_Mid_CapL",1.5),("SM_VK_Roof_Mid_CapR",-1.5)]:
    print(n,x,chk(n,x))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Mid -1.5 (12, -0.0579, -0.75, -0.058)\nSM_VK_RoofThatch_Mid -1.5 (30, 0.2, -0.47, -0.058)\nSM_VK_Roo
# f_Hip_Plain -1.5 (60, -0.062, -0.5, -0.062)\nSM_VK_Roof_HalfHip -1.5 (66, -0.062, -0.5, -0.062)\nSM_VK_RoofThatch_HalfHip -1.5 (84, 0.2, -0.47, -0.062
# )\nSM_VK_Roof_Gable_Flush -1.5 (12, -0.0579, -0.75, -0.058)\nSM_VK_Roof_Gable_Hoist -1.5 (12, -0.0579, -0.75, -0.058)\nSM_VK_Roof_CrossGable -1.5 (60,
#  -0.062, -0.5, -0.062)\nSM_VK_Roof_CrossGable 1.5 (59, -0.062, -0.5, -0.062)\nSM_VK_Roof_Mid_CapL 1.5 (12, -0.0579, -0.75, -0.058)\nSM_VK_Roof_Mid_Cap
# R -1.5 (12, -0.0579, -0.75, -0.058)\n"}

# ==============================================================================================================
# [0025] 2026-09-23 16:07:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_bellcote",(10,31,15),(6,40,13),lens=35,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_bellcote.png\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:07:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","close_firewall",(-1,31.5,6.5),(-3,37,5.8),lens=35,res=(1280,720),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\close_firewall.png\n"}

# ==============================================================================================================
# [0027] 2026-09-23 16:09:00  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_skyline"); t.clear(); t.write(src)
g=ws_ns("skyline"); sc,coll,asm=ws_scene("skyline")
objs=ws_build("skyline",g=g)
ws_clear_assembly("skyline")
g["build_skyline_street"](asm,(-18,40,0),seed=0)
rows=[["Chimney_Gable_H24","Chimney_Gable_H30","Chimney_Gable_H58","Chimney_Party","Roof_Vent","Roof_Bellcote","Banner_Pole","Banner_Roof"],
      ["Roof_Single","RoofThatch_Single","Roof_Hip_Plain","Roof_HalfHip","RoofThatch_HalfHip","Roof_CrossGable","Roof_Gable_Hoist"],
      ["Roof_Gable_Flush","Roof_Gable_Stepped","Roof_Firewall","Roof_Mid_CapL","Roof_Mid_CapR","Roof_Mid_Hatch","Roof_Mid_Skylight"],
      ["Emblem_Ridge_"+e for e in ("Anvil","Pretzel","Tankard","Fish","Key","Sheaf","Horseshoe","Shield","Book","Axe")]+["Banner_Wall"],
      ["Prop_Bunting_6","Prop_Bunting_9"]]
sp=[4.6,7.2,7.2,2.3,11]; ys=[-4,-15,-26,-33.5,-37.5]
from mathutils import Vector
done=set()
for r,(row,s,y) in enumerate(zip(rows,sp,ys)):
    x0=-s*(len(row)-1)/2
    for i,n in enumerate(row):
        o=bpy.data.objects["SM_VK_"+n]; done.add(o.name)
        zmin=min(v.co.z for v in o.data.vertices)
        o.location=(x0+s*i,y,max(0.0,-zmin)); o.hide_render=False; o.hide_viewport=False
print(len(done),len(objs),[o.name for o in objs if o.name not in done])
st=ws_stats(objs)
for s_ in st: print(s_["name"],s_["tris"],s_["bbox"])
# ---- result ----
# {"result":"Code executed successfully: 35 35 []\nSM_VK_Roof_Single 9008 [5.4, 9.04, 5.89]\nSM_VK_RoofThatch_Single 6600 [5.32, 9.13, 5.17]\nSM_VK_Roof
# _Hip_Plain 6936 [4.68, 8.94, 5.07]\nSM_VK_Chimney_Gable_H30 1948 [1.94, 1.49, 9.3]\nSM_VK_Chimney_Gable_H58 1776 [1.94, 1.49, 12.1]\nSM_VK_Chimney_Gab
# le_H24 1688 [1.94, 1.49, 8.7]\nSM_VK_Chimney_Party 720 [2.06, 1.25, 3.21]\nSM_VK_Roof_Vent 932 [1.75, 0.94, 1.75]\nSM_VK_Roof_Gable_Flush 3376 [3.39, 
# 8.88, 5.79]\nSM_VK_Roof_Firewall 800 [0.72, 7.84, 5.56]\nSM_VK_Roof_Gable_Stepped 3706 [3.39, 8.88, 6.71]\nSM_VK_Roof_Gable_Hoist 6540 [5.08, 9.04, 7.
# 48]\nSM_VK_Roof_HalfHip 6602 [4.12, 8.99, 5.2]\nSM_VK_RoofThatch_HalfHip 6142 [4.22, 9.08, 5.28]\nSM_VK_Roof_CrossGable 3912 [3.31, 8.8, 5.09]\nSM_VK_
# Roof_Mid_CapL 3032 [3.19, 9.02, 5.1]\nSM_VK_Roof_Mid_CapR 3032 [3.19, 9.02, 5.1]\nSM_VK_Roof_Mid_Hatch 2864 [3.06, 8.9, 5.0]\nSM_VK_Roof_Mid_Skylight 

# ==============================================================================================================
# [0028] 2026-09-23 16:10:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","catalog_v4",(0,-60,19),(0,-19,2.5),lens=30,res=(1600,900),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_v4.png\n"}

# ==============================================================================================================
# [0029] 2026-09-23 16:10:32  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","catalog_v5",(0,-74,34),(0,-19,0),lens=30,res=(1600,900),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_v5.png\n"}

# ==============================================================================================================
# [0030] 2026-09-23 16:11:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","catalog_v6",(30,-58,24),(-1,-20,0.5),lens=32,res=(1600,900),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_v6.png\n"}

# ==============================================================================================================
# [0031] 2026-09-23 16:11:48  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","catalog_v7",(30,-66,30),(-1,-21,0),lens=30,res=(1600,900),samples=16))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_v7.png\n"}

# ==============================================================================================================
# [0032] 2026-09-23 16:12:42  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","hero_street_34",(21,13,15),(-3,36,4.5),lens=30,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_34.png\n"}

# ==============================================================================================================
# [0033] 2026-09-23 16:13:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","hero_street_34",(31,18,14),(-6,35,4),lens=28,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_34.png\n"}

# ==============================================================================================================
# [0034] 2026-09-23 16:14:03  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
tgt=(1,33,2); d=42; p=math.radians(50); yaw=math.radians(-20)
loc=(tgt[0]+d*math.cos(p)*math.sin(yaw), tgt[1]-d*math.cos(p)*math.cos(yaw), tgt[2]+d*math.sin(p))
print(loc)
print(ws_shot("skyline","hero_street_colony",loc,tgt,lens=24,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: (-8.233545036504076, 7.631043510687743, 34.173866610997074)\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratc
# h-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_co
# lony.png\n"}

# ==============================================================================================================
# [0035] 2026-09-23 16:14:39  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","hero_street_gate",(-29,27,6.5),(0,35.5,5),lens=28,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_gate.png\n"}

# ==============================================================================================================
# [0036] 2026-09-23 16:16:36  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_skyline"); t.clear(); t.write(src)
print(t.as_string()==src, len(src))
# ---- result ----
# {"result":"Code executed successfully: True 54109\n"}

# ==============================================================================================================
# [0037] 2026-09-23 16:16:57  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("skyline")
objs=ws_build("skyline",g=g)
print("built",len(objs),len(g["WS_SPECS"]),round(time.time()-t0,1))
sc,coll,asm=ws_scene("skyline")
ws_clear_assembly("skyline")
g["build_skyline_street"](asm,(-18,40,0),seed=0)
print("street objs",len(asm.objects),round(time.time()-t0,1))
rows=[["Chimney_Gable_H24","Chimney_Gable_H30","Chimney_Gable_H58","Chimney_Party","Roof_Vent","Roof_Bellcote","Banner_Pole","Banner_Roof"],
      ["Roof_Single","RoofThatch_Single","Roof_Hip_Plain","Roof_HalfHip","RoofThatch_HalfHip","Roof_CrossGable","Roof_Gable_Hoist"],
      ["Roof_Gable_Flush","Roof_Gable_Stepped","Roof_Firewall","Roof_Mid_CapL","Roof_Mid_CapR","Roof_Mid_Hatch","Roof_Mid_Skylight"],
      ["Emblem_Ridge_"+e for e in ("Anvil","Pretzel","Tankard","Fish","Key","Sheaf","Horseshoe","Shield","Book","Axe")]+["Banner_Wall"],
      ["Prop_Bunting_6","Prop_Bunting_9"]]
sp=[4.6,7.2,7.2,2.3,11]; ys=[-4,-15,-26,-33.5,-37.5]
for row,s,y in zip(rows,sp,ys):
    x0=-s*(len(row)-1)/2
    for i,n in enumerate(row):
        o=bpy.data.objects["SM_VK_"+n]; zmin=min(v.co.z for v in o.data.vertices)
        o.location=(x0+s*i,y,max(0.0,-zmin)); o.hide_render=False; o.hide_viewport=False
print(ws_shot("skyline","catalog_final",(30,-66,30),(-1,-21,0),lens=30,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: built 35 35 3.4\nstreet objs 246 5.1\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-
# 60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_final.png\n"}

# ==============================================================================================================
# [0038] 2026-09-23 16:17:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","hero_street_34",(31,18,14),(-6,35,4),lens=28,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_34.png\n"}

# ==============================================================================================================
# [0039] 2026-09-23 16:17:58  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
tgt=(1,33,2); d=42; p=math.radians(50); yaw=math.radians(-20)
loc=(tgt[0]+d*math.cos(p)*math.sin(yaw), tgt[1]-d*math.cos(p)*math.cos(yaw), tgt[2]+d*math.sin(p))
print(ws_shot("skyline","hero_street_colony",loc,tgt,lens=24,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_colony.png\n"}

# ==============================================================================================================
# [0040] 2026-09-23 16:18:38  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_skyline"); t.clear(); t.write(src)
print(t.as_string()==src, len(src))
# ---- result ----
# {"result":"Code executed successfully: True 54139\n"}

# ==============================================================================================================
# [0041] 2026-09-23 16:19:08  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("skyline")
objs=ws_build("skyline",g=g)
print("built",len(objs),"of",len(g["WS_SPECS"]),round(time.time()-t0,1))
sc,coll,asm=ws_scene("skyline")
ws_clear_assembly("skyline")
g["build_skyline_street"](asm,(-18,40,0),seed=0)
print("street objs",len(asm.objects),round(time.time()-t0,1))
rows=[["Chimney_Gable_H24","Chimney_Gable_H30","Chimney_Gable_H58","Chimney_Party","Roof_Vent","Roof_Bellcote","Banner_Pole","Banner_Roof"],
      ["Roof_Single","RoofThatch_Single","Roof_Hip_Plain","Roof_HalfHip","RoofThatch_HalfHip","Roof_CrossGable","Roof_Gable_Hoist"],
      ["Roof_Gable_Flush","Roof_Gable_Stepped","Roof_Firewall","Roof_Mid_CapL","Roof_Mid_CapR","Roof_Mid_Hatch","Roof_Mid_Skylight"],
      ["Emblem_Ridge_"+e for e in ("Anvil","Pretzel","Tankard","Fish","Key","Sheaf","Horseshoe","Shield","Book","Axe")]+["Banner_Wall"],
      ["Prop_Bunting_6","Prop_Bunting_9"]]
sp=[4.6,7.2,7.2,2.3,11]; ys=[-4,-15,-26,-33.5,-37.5]
for row,s,y in zip(rows,sp,ys):
    x0=-s*(len(row)-1)/2
    for i,n in enumerate(row):
        o=bpy.data.objects["SM_VK_"+n]; zmin=min(v.co.z for v in o.data.vertices)
        o.location=(x0+s*i,y,max(0.0,-zmin)); o.hide_render=False; o.hide_viewport=False
import json
st=ws_stats(objs)
print(json.dumps([(s_["name"][6:],s_["tris"],s_["bbox"],s_["zmin"]) for s_ in st]))
# ---- result ----
# {"result":"Code executed successfully: built 35 of 35 3.2\nstreet objs 246 5.0\n[[\"Roof_Single\", 9008, [5.4, 9.04, 5.89], -1.4], [\"RoofThatch_Singl
# e\", 6600, [5.32, 9.13, 5.17], -1.53], [\"Roof_Hip_Plain\", 6936, [4.68, 8.94, 5.07], -1.18], [\"Chimney_Gable_H30\", 1948, [1.94, 1.49, 9.3], -1.2], 
# [\"Chimney_Gable_H58\", 1776, [1.94, 1.49, 12.1], -1.2], [\"Chimney_Gable_H24\", 1688, [1.94, 1.49, 8.7], -1.2], [\"Chimney_Party\", 720, [2.06, 1.25,
#  3.21], -2.4], [\"Roof_Vent\", 932, [1.75, 0.94, 1.75], -1.38], [\"Roof_Gable_Flush\", 3376, [3.39, 8.88, 5.79], -1.16], [\"Roof_Firewall\", 800, [0.7
# 2, 7.84, 5.56], -0.7], [\"Roof_Gable_Stepped\", 3706, [3.39, 8.88, 6.71], -1.16], [\"Roof_Gable_Hoist\", 6540, [5.08, 9.04, 7.48], -4.58], [\"Roof_Hal
# fHip\", 6602, [4.12, 8.99, 5.2], -1.29], [\"RoofThatch_HalfHip\", 6142, [4.22, 9.08, 5.28], -1.51], [\"Roof_CrossGable\", 3912, [3.31, 8.8, 5.09], -1.

# ==============================================================================================================
# [0042] 2026-09-23 16:19:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("skyline","catalog_final",(30,-66,30),(-1,-21,0),lens=30,res=(1600,900),samples=32))
print(ws_shot("skyline","hero_street_34",(31,18,14),(-6,35,4),lens=28,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\catalog_final.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-work
# spaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_34.png\n
# "}

# ==============================================================================================================
# [0043] 2026-09-23 16:20:32  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
tgt=(1,33,2); d=42; p=math.radians(50); yaw=math.radians(-20)
loc=(tgt[0]+d*math.cos(p)*math.sin(yaw), tgt[1]-d*math.cos(p)*math.cos(yaw), tgt[2]+d*math.sin(p))
print(ws_shot("skyline","hero_street_colony",loc,tgt,lens=24,res=(1600,900),samples=32))
print(ws_shot("skyline","hero_street_gate",(-29,27,6.5),(0,35.5,5),lens=28,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_colony.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch
# -workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\skyline\\hero_street_gat
# e.png\n"}

# ==============================================================================================================
# [0044] 2026-09-23 16:21:25  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_skyline.py",encoding="utf8").read()
print("identical:",bpy.data.texts["ws_skyline"].as_string()==src)
print(len(bpy.data.collections["WS_skyline_Pieces"].objects),len(bpy.data.collections["WS_skyline_Assembly"].objects))
# ---- result ----
# {"result":"Code executed successfully: identical: True\n35 246\n"}
