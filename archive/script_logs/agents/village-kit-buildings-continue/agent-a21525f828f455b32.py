# village-kit-buildings-continue / agent-a21525f828f455b32.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:46:09  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_water")
ts=t.as_string() if t else ""
print(len(src),len(ts),src==ts, src.rstrip()==ts.rstrip())
import difflib
d=list(difflib.unified_diff(ts.splitlines(),src.splitlines(),'blender','file',n=0,lineterm=''))
print(len(d)); print("\n".join(d[:120]))
sc=bpy.data.scenes.get("WS_water"); print(sc)
for cn in ("WS_water_Pieces","WS_water_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, len(c.objects) if c else None)
# ---- result ----
# {"result":"Code executed successfully: 72637 56171 False False\n317\n--- blender\n+++ file\n@@ -760,2 +760,2 @@\n-def wat_fish(k,M,L=0.42,mi=STEEL):\n
# - \"\"\"low-poly fish along local +X (head), flattened in Y\"\"\"\n+def wat_fish(k,M,L=0.42,mi=STEEL,belly=PAPER):\n+ \"\"\"low-poly fish along local 
# +X (head), flattened in Y; dark back (mi) over a pale belly\"\"\"\n@@ -765,2 +765,2 @@\n- if r==0: rings.append([k.bm.verts.new(M@Vector((x*L,0,0)))])
# ; continue\n- rings.append([k.bm.verts.new(M@Vector((x*L,math.cos(2*math.pi*i/n)*r*L*0.42,math.sin(2*math.pi*i/n)*r*L))) for i in range(n)])\n+ if r==
# 0: rings.append([k.bm.verts.new(Vector((x*L,0,0)))]); continue\n+ rings.append([k.bm.verts.new(Vector((x*L,math.cos(2*math.pi*(i+0.5)/n)*r*L*0.42,math
# .sin(2*math.pi*(i+0.5)/n)*r*L))) for i in range(n)])\n@@ -775,2 +775,10 @@\n- tail=[M@Vector(p) for p in ((-0.46*L,0,0),(-0.72*L,0,0.2*L),(-0.64*L,0,0

# ==============================================================================================================
# [0002] 2026-09-23 15:47:17  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_water") or bpy.data.texts.new("ws_water"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time()
g=ws_ns("water")
objs=ws_build("water",g=g)
print(len(objs), round(time.time()-t0,1))
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"],s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: 32 2.1\nSM_VK_Pier_Deck 1168 [3.26, 3.3, 3.38] -3.0\nSM_VK_Pier_End 2818 [3.52, 3.3, 5.52] -3.01\nSM_VK_Pier_St
# airs 544 [1.68, 1.52, 4.05] -3.0\nSM_VK_Pier_Rail 536 [3.09, 0.18, 1.15] -0.1\nSM_VK_Prop_Rowboat 2148 [4.28, 1.42, 0.93] -0.25\nSM_VK_Prop_Barge 3968
#  [9.85, 3.6, 5.58] -0.38\nSM_VK_Bridge_Wood_Mid 1284 [3.1, 3.51, 1.69] -0.25\nSM_VK_Bridge_Wood_End 2200 [3.24, 4.07, 2.28] -0.79\nSM_VK_Bridge_Wood_B
# ent 608 [0.46, 3.6, 2.98] -3.0\nSM_VK_Bridge_Stone_Span 7480 [6.0, 4.26, 3.86] -1.6\nSM_VK_Bridge_Stone_Ramp 2304 [4.71, 5.72, 2.73] -0.6\nSM_VK_Bridg
# e_Stone_Pier 466 [1.9, 6.72, 3.0] -2.0\nSM_VK_Bridge_Log 344 [4.51, 0.88, 1.98] -0.9\nSM_VK_Quay_Straight 720 [3.0, 1.01, 2.03] -2.0\nSM_VK_Quay_Post 
# 372 [0.67, 0.7, 1.21] -0.03\nSM_VK_Quay_Stair 1040 [3.0, 1.3, 2.08] -2.0\nSM_VK_WaterWheel 3248 [2.3, 5.2, 5.2] -2.6\nSM_VK_Wall_Stone_Axle 1136 [3.04

# ==============================================================================================================
# [0003] 2026-09-23 15:48:00  blender  ok
# ==============================================================================================================
import bpy
asm=bpy.data.collections["WS_water_Assembly"]
from collections import Counter
c=Counter((o.data.name.split(".")[0] if o.data else o.name) for o in asm.objects)
print(c)
print(sorted({(round(o.location.x),round(o.location.y)) for o in asm.objects})[:60])
for n in ("SM_VK_RoofS_Gable","SM_VK_RoofS_Single","SM_VK_Wall_Posts","SM_VK_Wall_Shed","SM_VK_Wall_Shed_Door","SM_VK_Wall_Shed_Window","SM_VK_Corner_Shed","SM_VK_Roof_Vent","SM_VK_Prop_Laundry","SM_VK_Prop_Bench","SM_VK_Prop_LampPost","SM_VK_Prop_Woodpile","SM_VK_Prop_Sacks","SM_VK_Prop_Cart","SM_VK_Prop_Crates","SM_VK_Prop_BarrelStack","SM_VK_Chimney","SM_VK_Wall_Timber_Window","SM_VK_RoofThatchS_Single","SM_VK_Chimney_Gable_H30"):
    o=bpy.data.objects.get(n); print(n, None if o is None else [c.name for c in o.users_collection])
# ---- result ----
# {"result":"Code executed successfully: Counter({'SM_VK_Pier_Rail': 3, 'SM_VK_Bridge_Wood_Bent': 3, 'SM_VK_Quay_Straight': 3, 'SM_VK_Pier_Deck': 2, 'SM
# _VK_Bridge_Stone_Ramp': 2, 'SM_VK_Bridge_Wood_End': 2, 'SM_VK_Bridge_Wood_Mid': 2, 'SM_VK_Quay_Post': 2, 'SM_VK_Wall_Stone': 2, 'WS_water_Env_A': 1, '
# WS_water_Env_B': 1, 'SM_VK_Pier_End': 1, 'SM_VK_Pier_Stairs': 1, 'SM_VK_Prop_Rowboat': 1, 'SM_VK_Prop_Barge': 1, 'SM_VK_Bridge_Stone_Span': 1, 'SM_VK_
# Bridge_Log': 1, 'WS_water_Env_C': 1, 'SM_VK_Quay_Stair': 1, 'SM_VK_Wall_Stone_Axle': 1, 'SM_VK_Wall_Timber': 1, 'SM_VK_WaterWheel': 1, 'SM_VK_Mill_Whe
# elPier': 1, 'SM_VK_Prop_NetRack': 1, 'SM_VK_Prop_FishRack': 1, 'SM_VK_Prop_Creels': 1, 'SM_VK_Prop_Millstone': 1, 'SM_VK_Pile_Fish_1': 1, 'SM_VK_Pile_
# Fish_2': 1, 'SM_VK_Pile_Fish_3': 1, 'SM_VK_Prop_HandPump': 1, 'SM_VK_Prop_LavoirBasin': 1, 'SM_VK_Prop_WallFountain': 1})\n[(0, 0), (82, 0), (84, 0), 

# ==============================================================================================================
# [0004] 2026-09-23 15:49:29  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
ws_clear_assembly("water")
for me in list(bpy.data.meshes):
    if me.name.startswith("WS_water_Env") and me.users==0: bpy.data.meshes.remove(me)
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
t0=time.time()
g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
print(len(asm.objects), round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: 141 0.1\n"}

# ==============================================================================================================
# [0005] 2026-09-23 15:49:45  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("water","r01_demo_over",(196,-58,52),(196,0,0),lens=28)
p2=ws_shot("water","r01_demo_mill",(226,-18,14),(214,10,1.5),lens=30)
print(p,p2)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\r01_demo_over.png C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspa
# ces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\r01_demo_mill.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:50:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
# fisher hut is at world (188,-6) rot 180: hut body at y -9..-12, pier toward +y
ws_shot("water","r02_fisher",(176,-24,11),(188,-5,0.5),lens=30)
ws_shot("water","r02_smoke_lavoir",(200,-30,13),(200,-11,1),lens=24)
ws_shot("water","r02_woodbridge",(222,-12,6),(234,0,0),lens=30)
ws_shot("water","r02_quay_barge",(170,-6,7),(178,6,0),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0007] 2026-09-23 15:54:17  blender  ok
# ==============================================================================================================
import bpy, time, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
ws_clear_assembly("water")
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
rows=[["Pier_Deck","Pier_End","Pier_Stairs","Pier_Rail","Prop_Rowboat","Prop_Barge"],
      ["Bridge_Wood_Mid","Bridge_Wood_End","Bridge_Wood_Bent","Bridge_Stone_Span","Bridge_Stone_Ramp","Bridge_Stone_Pier","Bridge_Log"],
      ["Quay_Straight","Quay_Post","Quay_Stair","WaterWheel","Wall_Stone_Axle","Mill_WheelPier","Prop_Millstone"],
      ["Prop_NetRack","Prop_FishRack","Prop_Creels","Pile_Fish_1","Pile_Fish_2","Pile_Fish_3","Prop_LavoirBasin","Prop_WallFountain","Prop_HandPump"],
      ["WatRoofS_Gable","WatRoofS_Single","WatPosts"]]
zoff={"WaterWheel":2.6,"Prop_Rowboat":0.25,"Prop_Barge":0.38}
ys=[0,-9,-18,-27,-35]
for r,ys_ in zip(rows,ys):
    x=0.0
    for n in r:
        o=bpy.data.objects["SM_VK_"+n]
        bb=[o.matrix_world.to_3x3()@__import__("mathutils").Vector(c) for c in o.bound_box]
        mn=min(v.x for v in bb); mx=max(v.x for v in bb)
        o.rotation_euler=(0,0,0)
        o.location=(x-mn,ys_,zoff.get(n,0.0)); x+= (mx-mn)+1.6
    print(r[-1],round(x,1))
# ---- result ----
# {"result":"Code executed successfully: Prop_Barge 35.3\nBridge_Log 35.1\nProp_Millstone 26.6\nProp_HandPump 36.4\nWatPosts 17.0\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:55:12  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("water","r03_catalog",(18,-66,30),(18,-17,0),lens=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\r03_catalog.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 15:55:34  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
c=bpy.data.collections["WS_water_Pieces"]
print(c.hide_render, [ (o.name,o.hide_render,o.hide_viewport, o.hide_get()) for o in c.objects if o.hide_render or o.hide_viewport][:5])
for o in c.objects: o.hide_render=False; o.hide_viewport=False
print(ws_shot("water","r03_catalog",(18,-66,30),(18,-17,0),lens=32))
# ---- result ----
# {"result":"Code executed successfully: False [('SM_VK_Pier_Deck', True, False, False), ('SM_VK_Pier_End', True, False, False), ('SM_VK_Pier_Stairs', T
# rue, False, False), ('SM_VK_Pier_Rail', True, False, False), ('SM_VK_Prop_Rowboat', True, False, False)]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\
# scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\r03_catalo
# g.png\n"}

# ==============================================================================================================
# [0010] 2026-09-23 15:56:16  blender  ok
# ==============================================================================================================
import bpy
print([m.name for m in bpy.data.materials if "ater" in m.name or "Sand" in m.name or "Bank" in m.name or m.name.startswith("M_VT") or m.name.startswith("M_T")][:40])
print([s.name for s in bpy.data.scenes])
# ---- result ----
# {"result":"Code executed successfully: ['M_Tree_Bark', 'M_Tree_Canopy', 'M_Tree_Impostor_0', 'M_Tree_Impostor_1', 'M_Tree_Leaves
# ', 'M_VK_Water', 'M_VKT_Water', 'MC_Water']\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit', 'WS_construction', 'W
# S_defence', 'WS_frontier', 'WS_humble', 'WS_industry', 'WS_skyline', 'WS_town', 'WS_water']\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:57:22  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
ws_clear_assembly("water")
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
w=[o for o in asm.objects if o.data and o.data.name=="SM_VK_WaterWheel"][0]
print(w.animation_data.drivers[0].driver.expression if w.animation_data else None, sc.frame_current)
ws_shot("water","r04_mill",(226,-14,10),(214,8,0.5),lens=30)
ws_shot("water","r04_pier",(180,8,5),(188,-3,-0.3),lens=30)
# ---- result ----
# {"result":"Code executed successfully: 0.3700-frame*0.026180 1\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:58:36  blender  ok
# ==============================================================================================================
import bpy
o=[o for o in bpy.data.collections["WS_water_Assembly"].objects if o.name.startswith("WS_water_DemoTerrain")][0]
me=o.data
from collections import Counter
print(o.name, len(me.polygons), Counter(p.material_index for p in me.polygons), [m.name for m in me.materials])
for p in me.polygons:
    if p.material_index==1 and abs(p.normal.z)<0.99: print([tuple(round(c,2) for c in me.vertices[v].co) for v in p.vertices], tuple(round(c,2) for c in p.normal))
m=bpy.data.materials["M_VK_Soil"]; print(m.use_backface_culling, m.blend_method)
# ---- result ----
# {"result":"Code executed successfully: WS_water_DemoTerrain_200_0 36 Counter({3: 24, 0: 6, 1: 5, 2: 1}) ['MC_WK_Grass', 'M_VK_Soil', 'M_VKT_Water', 'M
# _VK_RockMossy']\n[(-60.0, 4.6, -1.5), (-27.0, 4.6, -1.5), (-27.0, 6.0, 0.0), (-60.0, 6.0, 0.0)] (0.0, -0.73, 0.68)\n[(-15.0, 4.6, -1.5), (8.0, 4.6, -1
# .5), (8.0, 6.0, 0.0), (-15.0, 6.0, 0.0)] (0.0, -0.73, 0.68)\n[(20.0, 4.6, -1.5), (60.0, 4.6, -1.5), (60.0, 6.0, 0.0), (20.0, 6.0, 0.0)] (0.0, -0.73, 0
# .68)\n[(-60.0, -6.0, 0.0), (60.0, -6.0, 0.0), (60.0, -4.6, -1.5), (-60.0, -4.6, -1.5)] (0.0, 0.73, 0.68)\nFalse HASHED\n"}

# ==============================================================================================================
# [0013] 2026-09-23 15:59:25  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
# lavoir at world (213.5,-12) rot 180; smokehouse at (178,-11.5) rot 180
ws_shot("water","r05_lavoir",(207,-21,5.5),(213.5,-12,1.0),lens=30)
ws_shot("water","r05_smoke",(172,-20,5.5),(178,-11.5,1.5),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0014] 2026-09-23 16:00:38  blender  ok
# ==============================================================================================================
import bpy
names=sorted(o.name for o in bpy.data.objects if o.name.startswith("SM_VK") and any(s in o.name for s in ("Smoke","Reed","Rock","Plant","Stone","Bush","Grass","Lily","Weed","Cattail")))
print(len(names)); print(names[:80])
# ---- result ----
# {"result":"Code executed successfully: 2058\n['SM_VKT_LipGrass', 'SM_VKT_LipGrass_board', 'SM_VKT_LipGrass_inst', 'SM_VKT_LipGrass_inst.001', 'SM_VKT_
# LipGrass_inst.002', 'SM_VKT_LipGrass_inst.003', 'SM_VKT_LipGrass_inst.004', 'SM_VKT_LipGrass_inst.005', 'SM_VKT_LipGrass_inst.006', 'SM_VKT_LipGrass_i
# nst.007', 'SM_VKT_LipGrass_inst.008', 'SM_VKT_LipGrass_inst.009', 'SM_VKT_LipGrass_inst.010', 'SM_VKT_LipGrass_inst.011', 'SM_VKT_LipGrass_inst.012', 
# 'SM_VKT_LipGrass_inst.013', 'SM_VKT_LipGrass_inst.014', 'SM_VKT_LipGrass_inst.015', 'SM_VKT_LipGrass_inst.016', 'SM_VKT_LipGrass_inst.017', 'SM_VKT_Li
# pGrass_inst.018', 'SM_VKT_LipGrass_inst.019', 'SM_VKT_LipGrass_inst.020', 'SM_VKT_LipGrass_inst.021', 'SM_VKT_LipGrass_inst.022', 'SM_VKT_LipGrass_ins
# t.023', 'SM_VKT_LipGrass_inst.024', 'SM_VKT_LipGrass_inst.025', 'SM_VKT_LipGrass_inst.026', 'SM_VKT_LipGrass_inst.027', 'SM_VKT_LipGrass_inst.028', 'S

# ==============================================================================================================
# [0015] 2026-09-23 16:00:57  blender  ok
# ==============================================================================================================
import bpy
vp=bpy.data.collections.get("VK_Pieces")
names=sorted(o.name for o in vp.all_objects if any(s in o.name for s in ("Smoke","Reed","Rock","Plant","Bush","Grass","Lily","Weed","Cattail","Deco","Tree","Flower","Mush","Log")))
print(len(names)); print(names)
# ---- result ----
# {"result":"Code executed successfully: 7\n['SM_VK_Deco_Bush', 'SM_VK_Deco_Ivy_A', 'SM_VK_Deco_Ivy_B', 'SM_VK_Deco_Weeds', 'SM_VK_Prop_FlowerBox', 'SM_
# VK_Prop_FlowerBox_Daisy', 'SM_VK_Prop_Planter']\n"}

# ==============================================================================================================
# [0016] 2026-09-23 16:01:12  blender  ok
# ==============================================================================================================
import bpy
names=sorted(o.name for o in bpy.data.objects if o.name.startswith(("SM_VK_Plant","SM_VK_Rock","SM_VK_Tree","SM_VK_Reed","SM_VK_Smoke","SM_VK_Stump","SM_VK_Log","SM_VK_Bush","SM_VK_Mush","SM_VK_Fx","SM_VK_FX")) and "." not in o.name and "_inst" not in o.name)
print(len(names)); print(names)
# ---- result ----
# {"result":"Code executed successfully: 38\n['SM_VK_Bush_Autumn', 'SM_VK_Bush_Berry', 'SM_VK_Bush_Hydrangea', 'SM_VK_Bush_Large', 'SM_VK_Bush_Round', '
# SM_VK_Log_Fallen', 'SM_VK_Mushrooms_Brown', 'SM_VK_Mushrooms_Glow', 'SM_VK_Mushrooms_Red', 'SM_VK_Plant_Fern', 'SM_VK_Plant_Reeds', 'SM_VK_Plant_TallG
# rass', 'SM_VK_Plant_Wildflowers', 'SM_VK_Rock_Boulder_A', 'SM_VK_Rock_Boulder_B', 'SM_VK_Rock_Boulder_Flat', 'SM_VK_Rock_Cluster', 'SM_VK_Rock_Outcrop
# ', 'SM_VK_Rock_Pebbles', 'SM_VK_Rock_Small_A', 'SM_VK_Rock_Small_B', 'SM_VK_Rock_Standing', 'SM_VK_Rock_Standing_B', 'SM_VK_Rock_StepStones', 'SM_VK_S
# tump', 'SM_VK_Tree_Apple', 'SM_VK_Tree_Birch', 'SM_VK_Tree_Birch_Single', 'SM_VK_Tree_Blossom', 'SM_VK_Tree_Dead', 'SM_VK_Tree_Oak_A', 'SM_VK_Tree_Oak
# _Autumn', 'SM_VK_Tree_Oak_B', 'SM_VK_Tree_Pine_A', 'SM_VK_Tree_Pine_B', 'SM_VK_Tree_Pine_Young', 'SM_VK_Tree_Sapling', 'SM_VK_Tree_Willow']\n"}

# ==============================================================================================================
# [0017] 2026-09-23 16:02:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for n in ("Prop_NetRack","Prop_FishRack","Prop_Creels","Pile_Fish_1","Pile_Fish_2","Pile_Fish_3"):
    o=bpy.data.objects["SM_VK_"+n]; print(n, tuple(round(c,1) for c in o.location))
ws_shot("water","r06_fishprops",(9,-36.5,4.2),(9,-27,0.9),lens=30)
ws_shot("water","r06_washprops",(29,-36,4.5),(29,-27,0.6),lens=30)
# ---- result ----
# {"result":"Code executed successfully: Prop_NetRack (1.9, -27.0, 0.0)\nProp_FishRack (6.9, -27.0, 0.0)\nProp_Creels (11.0, -27.0, 0.0)\nPile_Fish_1 (1
# 4.2, -27.0, 0.0)\nPile_Fish_2 (16.6, -27.0, 0.0)\nPile_Fish_3 (20.0, -27.0, 0.0)\n"}

# ==============================================================================================================
# [0018] 2026-09-23 16:02:36  blender  ok
# ==============================================================================================================
import bpy
print(sorted(o.name for o in bpy.data.objects if any(s in o.name.lower() for s in ("person","villager","human","figure","scale","dummy","npc","peasant","man_","char")) and "_inst" not in o.name)[:30])
# ---- result ----
# {"result":"Code executed successfully: [third-party character assets from another scene removed], 'Colonist_Villager_0', 'Colonist_Villager_1',
#  'Colonist_Villager_2', 'Colonist_Villager_3', 'Colonist_Villager_4', 'SM_VK_Prop_CharcoalMound', 'SM_VK_Prop_TrainingDummy']\n"}

# ==============================================================================================================
# [0019] 2026-09-23 16:03:19  blender  ok
# ==============================================================================================================
import bpy
for n in ("Colonist_Villager_0","Colonist_Villager_1"):
    o=bpy.data.objects[n]; print(n,o.type,tuple(round(d,2) for d in o.dimensions),[m.type for m in o.modifiers], o.parent.name if o.parent else None, [c.name for c in o.users_collection], o.data.name if o.data else None)
# ---- result ----
# {"result":"Code executed successfully: Colonist_Villager_0 MESH (0.92, 0.66, 1.69) [] None ['Colonists'] Colonist_Villager_0\nColonist_Villager_1 MESH
#  (0.92, 0.66, 1.69) [] None ['Colonists'] Colonist_Villager_1\n"}

# ==============================================================================================================
# [0020] 2026-09-23 16:05:13  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for n in ("SM_VK_Rock_StepStones","SM_VK_Plant_Reeds","SM_VK_Tree_Willow","SM_VK_Bush_Round","SM_VK_Plant_TallGrass","SM_VK_Rock_Cluster","SM_VK_Rock_Pebbles","SM_VK_Plant_Wildflowers","SM_VK_Bush_Large","SM_VK_Log_Fallen","SM_VK_Rock_Boulder_Flat"):
    o=bpy.data.objects[n]; bb=[Vector(c) for c in o.bound_box]
    print(n, tuple(round(d,2) for d in o.dimensions), "zmin",round(min(v.z for v in bb),2), "tris", sum(len(p.vertices)-2 for p in o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Rock_StepStones (5.83, 1.14, 0.3) zmin -0.14 tris 480\nSM_VK_Plant_Reeds (2.29, 2.27, 1.86) zmin -0.02 tr
# is 160\nSM_VK_Tree_Willow (8.55, 8.75, 5.02) zmin -0.43 tris 2246\nSM_VK_Bush_Round (2.78, 2.65, 2.54) zmin -0.69 tris 669\nSM_VK_Plant_TallGrass (1.6
# 9, 1.95, 1.06) zmin -0.02 tris 160\nSM_VK_Rock_Cluster (2.02, 2.25, 0.93) zmin -0.15 tris 1600\nSM_VK_Rock_Pebbles (1.97, 2.38, 0.2) zmin -0.04 tris 1
# 760\nSM_VK_Plant_Wildflowers (2.06, 2.13, 0.75) zmin -0.02 tris 192\nSM_VK_Bush_Large (3.99, 4.17, 3.97) zmin -1.13 tris 1101\nSM_VK_Log_Fallen (3.48,
#  1.72, 0.95) zmin -0.07 tris 1212\nSM_VK_Rock_Boulder_Flat (2.38, 1.5, 0.8) zmin -0.11 tris 320\n"}

# ==============================================================================================================
# [0021] 2026-09-23 16:07:24  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
keep={o.name:(tuple(o.location),tuple(o.rotation_euler)) for o in bpy.data.collections["WS_water_Pieces"].objects}
objs=ws_build("water",g=g,names=["SM_VK_Prop_Barge","SM_VK_Pile_Fish_1","SM_VK_Pile_Fish_2","SM_VK_Pile_Fish_3","SM_VK_Prop_Creels","SM_VK_Prop_LavoirBasin"])
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
for o in objs: o.location,o.rotation_euler=keep[o.name]
ws_clear_assembly("water")
sc,coll,asm=ws_scene("water")
t0=time.time(); g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0); print(len(asm.objects), round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Barge 3616 [9.85, 3.6, 5.58]\nSM_VK_Prop_Creels 1970 [2.02, 1.52, 0.67]\nSM_VK_Pile_Fish_1 572 [0.86
# , 0.74, 0.37]\nSM_VK_Pile_Fish_2 1188 [1.77, 1.16, 0.37]\nSM_VK_Pile_Fish_3 1922 [1.8, 1.59, 0.68]\nSM_VK_Prop_LavoirBasin 1378 [5.44, 2.69, 1.19]\n18
# 3 0.1\n"}

# ==============================================================================================================
# [0022] 2026-09-23 16:08:14  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
o=bpy.data.objects["SM_VK_Prop_Barge"]; me=o.data
from collections import Counter
c=Counter()
for p in me.polygons: c[me.materials[p.material_index].name]+=len(p.vertices)-2
print(c)
# ---- result ----
# {"result":"Code executed successfully: Counter({'M_VK_Planks': 1268, 'M_VK_Wood': 1240, 'M_VK_Shutter_Teal': 400, 'M_VK_Iron': 352, 'M_VK_Burlap': 252
# , 'M_VK_Cloth_Cream': 80, 'M_VK_EndGrain': 24})\n"}

# ==============================================================================================================
# [0023] 2026-09-23 16:08:54  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
keep={o.name:(tuple(o.location),tuple(o.rotation_euler)) for o in bpy.data.collections["WS_water_Pieces"].objects}
objs=ws_build("water",g=g,names=["SM_VK_Prop_Barge"])
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
for o in objs: o.location,o.rotation_euler=keep[o.name]
ws_shot("water","r07_over",(196,-60,50),(200,-2,0),lens=28)
ws_shot("water","r07_brook",(236,-36,9),(245,-20,0),lens=30)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Barge 2956 [9.85, 3.6, 5.58]\n"}

# ==============================================================================================================
# [0024] 2026-09-23 16:09:59  blender  ok
# ==============================================================================================================
import bpy, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
ws_clear_assembly("water"); g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
# colony camera: 50 deg pitch, ~40 m from target
tx,ty=202,0; d=40; p=math.radians(50)
ws_shot("water","r08_colony",(tx,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=32)
ws_shot("water","r08_mill34",(229,-10,9),(214,9,1.8),lens=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0025] 2026-09-23 16:12:10  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
g["wat_catalog_stage"](asm,(150.0,-90.0,0.0))
print(len(asm.objects))
ws_shot("water","r09_catalog",(179,-150,36),(179,-97,0),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: 247\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:13:50  blender  ok
# ==============================================================================================================
import bpy, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
ws_clear_assembly("water")
g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
print(len(asm.objects))
ws_shot("water","r10_catalog",(167,-205,36),(167,-160,0),lens=32,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: 247\n"}

# ==============================================================================================================
# [0027] 2026-09-23 16:14:51  blender  ok
# ==============================================================================================================
import bpy, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
for o in list(asm.objects):
    if o.location.y<-100 and not o.name.startswith("WS_water_CatalogTerrain"): bpy.data.objects.remove(o)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
print(len(asm.objects))
ws_shot("water","r11_catalog",(172,-194,27),(172,-161,-1),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: 247\n"}

# ==============================================================================================================
# [0028] 2026-09-23 16:16:00  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","r12_catalog",(171,-222,44),(171,-160,-1.5),lens=42,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0029] 2026-09-23 16:16:34  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","r13_fisher",(176,6,9),(186,-8,0.5),lens=28)
ws_shot("water","r13_mill",(224,-13,7.5),(210,9,2.0),lens=28)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0030] 2026-09-23 16:17:07  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for i in range(5):
    o=bpy.data.objects["Colonist_Villager_%d"%i]; bb=[Vector(c) for c in o.bound_box]
    print(o.name, round(min(v.z for v in bb),2), round(max(v.z for v in bb),2), tuple(round(a,2) for a in o.rotation_euler), tuple(round(a,2) for a in o.scale), len(o.data.polygons), [m.name for m in o.data.materials])
# ---- result ----
# {"result":"Code executed successfully: Colonist_Villager_0 -0.0 1.68 (0.0, 0.0, -2.36) (1.0, 1.0, 1.0) 278 ['MC_Skin1', 'MC_HairBlond', 'MC_TunicRed',
#  'MC_Pants', 'MC_Boots', 'MC_Timber', 'MC_Iron', 'MC_Apron']\nColonist_Villager_1 -0.0 1.68 (0.0, 0.0, -0.71) (1.0, 1.0, 1.0) 278 ['MC_Skin3', 'MC_Hai
# rBlack', 'MC_TunicOchre', 'MC_Pants', 'MC_Boots', 'MC_Timber', 'MC_Iron', 'MC_Apron']\nColonist_Villager_2 -0.0 1.68 (0.0, 0.0, 1.26) (1.0, 1.0, 1.0) 
# 278 ['MC_Skin2', 'MC_HairRed', 'MC_TunicGreen', 'MC_Pants', 'MC_Boots', 'MC_Timber', 'MC_Iron', 'MC_Apron']\nColonist_Villager_3 0.0 2.03 (0.0, 0.0, -
# 0.9) (1.0, 1.0, 1.0) 266 ['MC_Skin1', 'MC_HairBrown', 'MC_TunicBlue', 'MC_Pants', 'MC_Boots', 'MC_Timber', 'MC_Iron', 'MC_Apron']\nColonist_Villager_4
#  0.0 2.12 (0.0, 0.0, 2.25) (1.0, 1.0, 1.0) 276 ['MC_Skin2', 'MC_HairBlond', 'MC_TunicRed', 'MC_Pants', 'MC_Boots', 'MC_Timber', 'MC_Iron', 'MC_Apron']

# ==============================================================================================================
# [0031] 2026-09-23 16:18:39  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("water")
spots=[(188.3,-2.2,0.05,0.4,0),(200.4,-4.2,1.24,1.9,1),(210.4,10.6,0.0,-1.4,2),(214.7,-10.4,0.0,3.3,3),(182.4,-7.2,0.0,-0.3,4),(179.5,7.7,0.0,2.8,0),(186.0,-14.5,0.0,1.0,2)]
for i,(x,y,z,r,v) in enumerate(spots):
    n="WS_water_Scale_%d"%i
    o=bpy.data.objects.get(n)
    if o is None:
        o=bpy.data.objects.new(n,bpy.data.objects["Colonist_Villager_%d"%v].data); asm.objects.link(o)
    o.location=(x,y,z); o.rotation_euler=(0,0,r)
ws_shot("water","r14_fisher",(176,6,9),(186,-8,0.5),lens=28)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0032] 2026-09-23 16:19:13  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","r15_river34",(171,-31,17),(198,-1,0),lens=26)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0033] 2026-09-23 16:20:08  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
o=bpy.data.objects.get("WS_water_Scale_6")
if o: bpy.data.objects.remove(o)
ws_shot("water","r16_river34",(163,-36,21),(195,-2,0),lens=26)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0034] 2026-09-23 16:21:22  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
# catalog stage origin (150,-150): pier x0, barge quay 6..15, mill 18..27, stone bridge 35, wood bridge 46
ws_shot("water","r17_cat_pier",(147,-163,4.5),(153,-153,0),lens=30)
ws_shot("water","r17_cat_mill",(166,-162,3.2),(172.5,-150.5,1.0),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0035] 2026-09-23 16:23:16  blender  ok
# ==============================================================================================================
import bpy, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
ws_clear_assembly("water")
g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
spots=[(189.5,-2.2,0.05,0.4,0),(200.4,-4.2,1.24,1.9,1),(211.2,10.3,0.0,-1.4,2),(214.7,-10.4,0.0,3.3,3),(182.4,-7.2,0.0,-0.3,4),(179.5,7.7,0.0,2.8,0)]
for i,(x,y,z,r,v) in enumerate(spots):
    o=bpy.data.objects.new("WS_water_Scale_%d"%i,bpy.data.objects["Colonist_Villager_%d"%v].data); asm.objects.link(o)
    o.location=(x,y,z); o.rotation_euler=(0,0,r)
print(len(asm.objects))
ws_shot("water","r18_river34",(163,-36,21),(195,-2,0),lens=26)
ws_shot("water","r18_mill",(225,-12,7.5),(211,9,2.0),lens=28)
# ---- result ----
# {"result":"Code executed successfully: 253\n"}

# ==============================================================================================================
# [0036] 2026-09-23 16:24:55  blender  ERROR
# ==============================================================================================================
import bpy, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
g["wat_pick"]=lambda n,f: f
g["wat_hut_set"]=lambda: dict(W="SM_VK_Wall_Plaster",D="SM_VK_Wall_Plaster_Door",Wi="SM_VK_Wall_Plaster_Window",C="SM_VK_Corner_Plaster",top=3.0)
before=set(asm.objects.keys())
print(g["build_fisher_hut"](asm,(-40.0,40.0,0.0),seed=2))
print(g["build_lavoir"](asm,(-25.0,40.0,0.0),seed=4))
print(g["build_smokehouse"](asm,(-14.0,40.0,0.0),seed=3))
new=[n for n in asm.objects.keys() if n not in before]
bpy.types.Scene  # noop
import json; open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\fallback_objs.json","w").write(json.dumps(new))
print(len(new))
ws_shot("water","r19_fallbacks",(-27,18,12),(-27,42,1.5),lens=32)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: [Errno 2] No such file or directory: 'C:\\\\Users\\\\danie\\\
# \AppData\\\\Local\\\\Temp\\\\claude\\\\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c
# 6-98db-14b97d4348ea-scratch-2026-09-23-d49817\\\\421a57cc-0ba3-43b1-888d-34ef79f58bc6\\\\scratchpad\\\\fallback_objs.json'"}

# ==============================================================================================================
# [0037] 2026-09-23 16:25:13  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("water")
n=[o.name for o in asm.objects if o.location.x<0 and o.location.y>30]
print(len(n))
ws_shot("water","r19_fallbacks",(-27,18,12),(-27,42,1.5),lens=32)
# ---- result ----
# {"result":"Code executed successfully: 51\n"}

# ==============================================================================================================
# [0038] 2026-09-23 16:25:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("water")
for o in [o for o in asm.objects if o.location.x<0 and o.location.y>30]: bpy.data.objects.remove(o)
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: 253\n"}

# ==============================================================================================================
# [0039] 2026-09-23 16:26:17  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_RoofS_Gable","SM_VK_RoofS_Single","SM_VK_WatRoofS_Gable","SM_VK_WatRoofS_Single","SM_VK_Roof_Gable","SM_VK_Roof_Mid","SM_VK_Wall_Posts","SM_VK_WatPosts"):
    o=bpy.data.objects.get(n)
    if o: print(n, sum(len(p.vertices)-2 for p in o.data.polygons), tuple(round(d,2) for d in o.dimensions))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_RoofS_Gable 4202 (3.88, 5.14, 3.75)\nSM_VK_RoofS_Single 6116 (4.7, 5.14, 3.75)\nSM_VK_WatRoofS_Gable 4460
#  (3.86, 5.1, 3.56)\nSM_VK_WatRoofS_Single 6414 (4.66, 5.1, 3.56)\nSM_VK_Roof_Gable 5688 (4.23, 9.04, 5.89)\nSM_VK_Roof_Mid 2368 (3.06, 8.9, 5.0)\nSM_V
# K_Wall_Posts 360 (3.26, 0.53, 3.6)\nSM_VK_WatPosts 392 (3.66, 0.56, 3.6)\n"}

# ==============================================================================================================
# [0040] 2026-09-23 16:26:55  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
print("text==file", bpy.data.texts["ws_water"].as_string()==src)
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
objs=ws_build("water", g=g)
print(len(objs), len(g["WS_SPECS"]), round(time.time()-t0,1))
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"],s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: text==file True\n32 32 2.2\nSM_VK_Pier_Deck 1168 [3.26, 3.3, 3.38] -3.0\nSM_VK_Pier_End 2818 [3.52, 3.3, 5.52] 
# -3.01\nSM_VK_Pier_Stairs 544 [1.68, 1.52, 4.05] -3.0\nSM_VK_Pier_Rail 536 [3.09, 0.18, 1.15] -0.1\nSM_VK_Prop_Rowboat 2148 [4.28, 1.42, 0.93] -0.5\nSM
# _VK_Prop_Barge 2956 [9.85, 3.6, 5.58] -0.76\nSM_VK_Bridge_Wood_Mid 1284 [3.1, 3.51, 1.69] -0.25\nSM_VK_Bridge_Wood_End 2200 [3.24, 4.07, 2.28] -0.79\n
# SM_VK_Bridge_Wood_Bent 608 [0.46, 3.6, 2.98] -3.0\nSM_VK_Bridge_Stone_Span 7480 [6.0, 4.26, 3.86] -1.6\nSM_VK_Bridge_Stone_Ramp 2304 [4.71, 5.72, 2.73
# ] -0.6\nSM_VK_Bridge_Stone_Pier 466 [1.9, 6.72, 3.0] -2.0\nSM_VK_Bridge_Log 344 [4.51, 0.88, 1.98] -0.9\nSM_VK_Quay_Straight 720 [3.0, 1.01, 2.03] -2.
# 0\nSM_VK_Quay_Post 384 [0.67, 0.7, 1.78] -0.6\nSM_VK_Quay_Stair 1040 [3.0, 1.3, 2.08] -2.0\nSM_VK_WaterWheel 3248 [2.3, 5.2, 5.2] -5.2\nSM_VK_Wall_Sto

# ==============================================================================================================
# [0041] 2026-09-23 16:27:35  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
ws_clear_assembly("water")
t0=time.time()
r=g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
n1=len(asm.objects)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
print(n1, len(asm.objects), round(time.time()-t0,1))
spots=[(189.5,-2.2,0.05,0.4,0),(200.4,-4.2,1.24,1.9,1),(211.2,10.3,0.0,-1.4,2),(214.7,-10.4,0.0,3.3,3),(182.4,-7.2,0.0,-0.3,4),(179.5,7.7,0.0,2.8,0),
       (152.4,-152.2,0.05,0.5,1),(163.0,-150.6,0.0,0.3,3),(185.4,-155.0,1.25,2.0,2),(151.0,-166.0,0.0,0.2,4)]
for i,(x,y,z,rz,v) in enumerate(spots):
    o=bpy.data.objects.new("WS_water_Scale_%d"%i,bpy.data.objects["Colonist_Villager_%d"%v].data); asm.objects.link(o)
    o.location=(x,y,z); o.rotation_euler=(0,0,rz)
sc.frame_set(1)
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: 186 250 0.1\n260\n"}

# ==============================================================================================================
# [0042] 2026-09-23 16:28:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for i,p in ((6,(150.4,-152.6,0.05)),(7,(163.0,-149.4,0.0)),(9,(148.2,-165.6,0.0))):
    bpy.data.objects["WS_water_Scale_%d"%i].location=p
ws_shot("water","r20_catalog",(172,-218,40),(172,-161,-1.0),lens=40,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0043] 2026-09-23 16:28:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","r21_catalog",(171.5,-212,36),(171.5,-161.5,0.2),lens=44,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0044] 2026-09-23 16:29:40  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
for o in list(asm.objects):
    if o.location.y<-100 and not o.name.startswith(("WS_water_CatalogTerrain","WS_water_Scale")): bpy.data.objects.remove(o)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
for i,p in ((6,(150.4,-152.6,0.05)),(7,(160.0,-149.4,0.0)),(8,(182.4,-155.0,1.25)),(9,(155.0,-173.2,0.0))):
    bpy.data.objects["WS_water_Scale_%d"%i].location=p
print(len(asm.objects))
ws_shot("water","r22_catalog",(170.5,-200,38),(170.5,-161,0),lens=34,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: 260\n"}

# ==============================================================================================================
# [0045] 2026-09-23 16:30:10  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
print("text==file", bpy.data.texts["ws_water"].as_string()==src)
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
objs=ws_build("water", g=g)
print("built",len(objs),"of",len(g["WS_SPECS"]), round(time.time()-t0,1))
sc,coll,asm=ws_scene("water")
ws_clear_assembly("water")
res={}
res["riverside"]=g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
n_demo=len(asm.objects)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
print("demo objs",n_demo,"total",len(asm.objects), round(time.time()-t0,1))
spots=[(189.5,-2.2,0.05,0.4,0),(200.4,-4.2,1.24,1.9,1),(211.2,10.3,0.0,-1.4,2),(214.7,-10.4,0.0,3.3,3),(182.4,-7.2,0.0,-0.3,4),(179.5,7.7,0.0,2.8,0),
       (150.4,-152.6,0.05,0.5,1),(160.0,-149.4,0.0,0.3,3),(182.4,-155.0,1.25,2.0,2),(155.0,-173.2,0.0,0.2,4)]
for i,(x,y,z,rz,v) in enumerate(spots):
    o=bpy.data.objects.new("WS_water_Scale_%d"%i,bpy.data.objects["Colonist_Villager_%d"%v].data); asm.objects.link(o)
    o.location=(x,y,z); o.rotation_euler=(0,0,rz)
sc.frame_set(1)
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: text==file True\nbuilt 32 of 32 2.2\ndemo objs 186 total 250 3.9\n260\n"}

# ==============================================================================================================
# [0046] 2026-09-23 16:30:24  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("water","catalog_final",(170.5,-200,38),(170.5,-161,0),lens=35,res=(1600,900),samples=48))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\catalog_final.png\n"}

# ==============================================================================================================
# [0047] 2026-09-23 16:30:26  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
tx,ty=202.0,0.5; d=40.0; p=math.radians(50)
print(ws_shot("water","hero_colony",(tx,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=30,res=(1600,900),samples=48))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\hero_colony.png\n"}

# ==============================================================================================================
# [0048] 2026-09-23 16:30:49  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("water","hero_riverside",(163,-36,21),(195,-2,0),lens=26,res=(1600,900),samples=48))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\hero_riverside.png\n"}

# ==============================================================================================================
# [0049] 2026-09-23 16:30:51  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("water","hero_mill",(225,-12,7.5),(211,9,2.0),lens=28,res=(1600,900),samples=48))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\hero_mill.png\n"}

# ==============================================================================================================
# [0050] 2026-09-23 16:31:15  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("water","hero_mill",(229,-16,8.5),(211,9,3.0),lens=26,res=(1600,900),samples=48))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\hero_mill.png\n"}

# ==============================================================================================================
# [0051] 2026-09-23 16:31:36  blender  ok
# ==============================================================================================================
import bpy, hashlib
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("water")
for o in [o for o in asm.objects if o.name.startswith("WS_water_Scale_")]: bpy.data.objects.remove(o)
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
ts=bpy.data.texts["ws_water"].as_string()
print("identical", ts==src, hashlib.md5(src.encode()).hexdigest(), len(src))
print("assembly", len(asm.objects), "pieces", len(coll.objects))
print(sorted({o.name for o in asm.objects if o.data and o.data.name.startswith("WS_water")}))
# ---- result ----
# {"result":"Code executed successfully: identical True 1a7531268896cc24a0c80e7f4de447fd 80186\nassembly 250 pieces 32\n['WS_water_CatalogTerrain', 'WS_
# water_DemoTerrain_200_0']\n"}

# ==============================================================================================================
# [0052] 2026-09-23 16:32:12  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py",encoding="utf8").read()
t=bpy.data.texts["ws_water"]; t.clear(); t.write(src)
print("text==file", bpy.data.texts["ws_water"].as_string()==src)
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
objs=ws_build("water", g=g)
print("built",len(objs),"of",len(g["WS_SPECS"]), round(time.time()-t0,1))
sc,coll,asm=ws_scene("water")
ws_clear_assembly("water")
out={}
out["riverside"]=g["build_riverside_demo"](asm,(200.0,0.0,0.0),seed=0)
g["wat_catalog_stage"](asm,(150.0,-150.0,0.0))
print("assembly",len(asm.objects), round(time.time()-t0,1))
# also exercise each sub-builder's return value via a throwaway namespace call count
print([k for k in g if k.startswith("build_")])
# ---- result ----
# {"result":"Code executed successfully: text==file True\nbuilt 32 of 32 2.1\nassembly 250 3.9\n['build_house', 'build_L_house', 'build_house_v', 'build
# _L_v', 'build_chapel', 'build_tavern', 'build_blacksmith', 'build_barn', 'build_windmill', 'build_guardtower', 'build_townhall', 'build_bakery', 'buil
# d_stable', 'build_town', 'build_watermill', 'build_fisher_hut', 'build_smokehouse', 'build_lavoir', 'build_riverside_demo']\n"}
