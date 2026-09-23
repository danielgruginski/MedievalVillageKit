# village-kit-buildings-continue / agent-a79552092548192bf.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:46:14  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble")
bt=t.as_string() if t else ""
print(len(src), len(bt), src==bt, src.rstrip()==bt.rstrip())
import difflib
d=list(difflib.unified_diff(bt.splitlines(), src.splitlines(), 'blender','file', n=1))
print(len(d)); print("\n".join(d[:120]))
sc=bpy.data.scenes.get("WS_humble")
print(sc, [c.name for c in sc.collection.children] if sc else None)
for cn in ("WS_humble_Pieces","WS_humble_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, len(c.objects) if c else None)
# ---- result ----
# {"result":"Code executed successfully: 56543 56336 False False\n52\n--- blender\n\n+++ file\n\n@@ -131,6 +131,8 @@\n\n rnd = random.Random(seed); C = 
# Vector(C); U = Vector(U); V = Vector(V); N = Vector(N)\n- ang = [2 * math.pi * i / n + rnd.uniform(-0.18, 0.18) for i in range(n)]\n- rad = [rnd.unifo
# rm(0.55, 1.2) if i % 3 else rnd.uniform(0.9, 1.25) for i in range(n)]\n- lip = [rnd.uniform(0.012, 0.03) for _ in range(n)]\n- wid = [rnd.uniform(1.12
# , 1.4) for _ in range(n)]\n+ n = max(n, 14)\n+ p1, p2, p3 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)\n+ ang = [2 * math.pi * i
#  / n + rnd.uniform(-0.12, 0.12) for i in range(n)]\n+ rad = [max(0.35, 1.0 + 0.3 * math.sin(2 * a + p1) + 0.18 * math.sin(3 * a + p2) + 0.1 * math.sin
# (7 * a + p3) + rnd.uniform(-0.12, 0.12)) for a in ang]\n+ lip = [rnd.uniform(0.006, 0.02) for _ in range(n)]\n+ wid = [rnd.uniform(1.08, 1.3) for _ in

# ==============================================================================================================
# [0002] 2026-09-23 15:46:58  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble") or bpy.data.texts.new("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble", g=g)
for s in ws_stats(objs): print(s)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Wall_Wattle', 'tris': 1924, 'bbox': [3.13, 0.52, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 45, 47]}
# \n{'name': 'SM_VK_Wall_Wattle_Window', 'tris': 2522, 'bbox': [3.13, 0.96, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 23, 27, 40, 45, 47]}\n{'name': 'SM_
# VK_Wall_Wattle_Door', 'tris': 2524, 'bbox': [3.13, 1.42, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 23, 27, 45, 47]}\n{'name': 'SM_VK_Wall_Wattle_Byre',
#  'tris': 2900, 'bbox': [3.13, 1.94, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 16, 23, 27, 45]}\n{'name': 'SM_VK_Wall_Wattle_Frame', 'tris': 1652, 'bbox
# ': [3.13, 0.96, 3.0], 'zmin': -0.6, 'mats': [0, 2, 25, 45, 47]}\n{'name': 'SM_VK_Corner_Wattle', 'tris': 660, 'bbox': [0.76, 0.8, 3.01], 'zmin': -0.6,
#  'mats': [0, 2, 45]}\n{'name': 'SM_VK_InnerCorner_Wattle', 'tris': 216, 'bbox': [0.45, 0.44, 2.45], 'zmin': -0.04, 'mats': [2, 45]}\n{'name': 'SM_VK_R

# ==============================================================================================================
# [0003] 2026-09-23 15:47:37  blender  ok
# ==============================================================================================================
import bpy
asm=bpy.data.collections["WS_humble_Assembly"]; pc=bpy.data.collections["WS_humble_Pieces"]
from collections import Counter
print(Counter(o.data.name if o.data else o.name for o in asm.objects).most_common(40))
for o in asm.objects:
    if o.data and o.data.name in ("SM_VK_RoofThatch_Vent","SM_VK_LeanTo_Thatch_Low","SM_VK_Prop_HayRack"): print(o.name, tuple(round(v,2) for v in o.location), round(o.rotation_euler.z,2))
print([ (o.name, tuple(round(v,1) for v in o.location), o.hide_render) for o in pc.objects])
# ---- result ----
# {"result":"Code executed successfully: [('VAR_2019548958500748217', 29), ('VAR_580170730744193806', 18), ('SM_VK_Prop_Fence', 17), ('SM_VK_Deco_Weeds'
# , 13), ('VAR_3629066345666575862', 9), ('SM_VK_Animal_Sheep', 7), ('SM_VK_LowWall_Post', 7), ('VAR_974085121561317565', 6), ('VAR_8287968679058910830'
# , 5), ('VAR_5294448870864252610', 5), ('SM_VK_LowWall', 5), ('VAR_7355131130756726397', 4), ('VAR_304092244207543486', 4), ('SM_VK_Prop_Bench', 4), ('
# SM_VK_Prop_GardenBed', 4), ('SM_VK_Animal_Chickens', 4), ('SM_VK_Prop_ChickenCoop_Wattle', 4), ('SM_VK_Prop_Planter', 3), ('SM_VK_Deco_Bush', 3), ('VA
# R_6948416494089042105', 3), ('SM_VK_Prop_FenceGate', 3), ('SM_VK_Prop_Trough.001', 3), ('SM_VK_Prop_HayBale.001', 3), ('SM_VK_Animal_Pig', 3), ('SM_VK
# _Prop_HayRack', 2), ('VAR_6603274286650841100', 1), ('VAR_5284088956782202088', 1), ('VAR_4322169419024405024', 1), ('SM_VK_Animal_Cow', 1), ('SM_VK_A

# ==============================================================================================================
# [0004] 2026-09-23 15:48:42  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble", g=g)
print("refreshed", g["hum_refresh_variants"]([n for n,_,_ in g["WS_SPECS"]]))
ws_clear_assembly("humble")
sc,coll,asm=ws_scene("humble")
g["build_hovel"](asm,(-16,22,0),seed=1,variant="cruck")
g["build_hovel"](asm,(0,22,0),seed=2,variant="hip")
g["build_hovel"](asm,(16,22,0),seed=3,variant="leanto")
g["build_longhouse"](asm,(0,40,0),seed=4)
g["build_pigsty"](asm,(-20,40,0),seed=5)
g["build_sheepfold"](asm,(26,40,0),seed=6)
print(len(asm.objects), time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: refreshed 8\n175 2.273850917816162\n"}

# ==============================================================================================================
# [0005] 2026-09-23 15:49:34  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("humble","r3_hovels",(0,4,14),(0,24,1.5),lens=30)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\r3_hovels.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:50:15  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r3_hov_cruck",(-16+11,22-13,7.5),(-15.5,22,2.0),lens=35)
ws_shot("humble","r3_hov_hip",(0-9,22-12,8),(0.5,22,2.0),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.369401216506958\n"}

# ==============================================================================================================
# [0007] 2026-09-23 15:50:40  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r3_hov_leanto",(16-13,22-8,6),(16-3.5,22,1.8),lens=35)
ws_shot("humble","r3_longhouse",(0+2,40-20,12),(3,40,1.5),lens=32)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.393944263458252\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:51:55  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r3_byre",(0+19,40-9,5.5),(7.5,40,1.6),lens=35)
ws_shot("humble","r3_pigsty",(-20+7,40-10,7),(-20,40.5,0.8),lens=35)
ws_shot("humble","r3_fold",(26+6,40-12,8),(26,40.5,0.8),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.8036198616027832\n"}

# ==============================================================================================================
# [0009] 2026-09-23 15:54:02  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("humble")
sc,coll,asm=ws_scene("humble")
st=g["HUM_STYLE"]; o=(0,-30,0)
pv=g["place_v"]
for i,nm in enumerate(["SM_VK_Wall_Wattle","SM_VK_Wall_Wattle_Window","SM_VK_Wall_Wattle_Door","SM_VK_Wall_Wattle_Byre","SM_VK_Wall_Wattle_Frame"]):
    pv(asm,nm,1.5+3*i,0,0,0,o,st)
pv(asm,"SM_VK_Corner_Wattle",0,0,0,0,o,st)
pv(asm,"SM_VK_Wall_Wattle",0,1.5,0,-90,o,st)
pv(asm,"SM_VK_Corner_Wattle",15,0,0,90,o,st)
pv(asm,"SM_VK_Wall_Wattle_Window",15,1.5,0,90,o,st)
pv(asm,"SM_VK_Animal_Cow",11,-2.2,0,200,o,{})
ws_shot("humble","r3_seam",(7.5,-30-11,3.2),(7.5,-30,1.3),lens=32)
ws_shot("humble","r3_seam_b",(-2.5,-30-5,2.6),(2.0,-30,1.2),lens=30)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.30147123336792\n"}

# ==============================================================================================================
# [0010] 2026-09-23 15:54:40  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r3_cat_roofs",(8,-22,7),(7,-7,2.2),lens=35)
ws_shot("humble","r3_vent_close",(6.5+2.2,-7-3.2,1.8),(6.5,-7,0.9),lens=40)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.3183956146240234\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:58:17  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
print(bpy.data.objects.get("SM_VK_Deco_MudWallow"))
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble", g=g)
m=bpy.data.objects["SM_VK_Deco_MudWallow"]; m.location=(22,-8,0)
print(ws_stats([m]))
print("refreshed", g["hum_refresh_variants"]([n for n,_,_ in g["WS_SPECS"]]))
ws_clear_assembly("humble")
sc,coll,asm=ws_scene("humble")
g["build_hovel"](asm,(-16,22,0),seed=1,variant="cruck")
g["build_hovel"](asm,(0,22,0),seed=2,variant="hip")
g["build_hovel"](asm,(16,22,0),seed=3,variant="leanto")
g["build_longhouse"](asm,(0,40,0),seed=4)
g["build_pigsty"](asm,(-20,40,0),seed=5)
g["build_sheepfold"](asm,(26,40,0),seed=6)
print(len(asm.objects), time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: None\n[{'name': 'SM_VK_Deco_MudWallow', 'tris': 418, 'bbox': [3.49, 2.56, 0.17], 'zmin': -0.04, 'mats': [16, 26
# ]}]\nrefreshed 9\n175 2.8914902210235596\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:58:31  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r4_pigsty",(-20+7,40-10,7),(-20,40.5,0.8),lens=35)
ws_shot("humble","r4_fold",(26+6,40-12,8),(26,40.5,0.8),lens=35)
ws_shot("humble","r4_hov_leanto",(16-12,22-9,6),(16-3.5,22,1.6),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.9624912738800049\n"}

# ==============================================================================================================
# [0013] 2026-09-23 15:59:47  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble", g=g, names=["SM_VK_Prop_ChickenCoop_Wattle"])
print(ws_stats(objs))
ws_shot("humble","r4_props",(18.5,-8-7,3.5),(18.5,-8,0.9),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Prop_ChickenCoop_Wattle', 'tris': 1535, 'bbox': [1.99, 2.58, 2.29], 'zmin': -0.03, 'mats': [2,
#  16, 22, 23, 27, 45, 47]}]\n0.9465069770812988\n"}

# ==============================================================================================================
# [0014] 2026-09-23 16:00:16  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r4_colony",(3,33-25.7,30.6),(3,33,0),lens=30)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.6981320381164551\n"}

# ==============================================================================================================
# [0015] 2026-09-23 16:01:12  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("humble")
print("refreshed", g["hum_refresh_variants"]([n for n,_,_ in g["WS_SPECS"]]))
ws_clear_assembly("humble")
sc,coll,asm=ws_scene("humble")
g["build_hovel"](asm,(-16,22,0),seed=1,variant="cruck")
g["build_hovel"](asm,(0,22,0),seed=2,variant="hip")
g["build_hovel"](asm,(16,22,0),seed=3,variant="leanto")
g["build_longhouse"](asm,(0,40,0),seed=4)
g["build_pigsty"](asm,(-16.5,38.5,0),seed=5)
g["build_sheepfold"](asm,(19.5,38.5,0),seed=6)
ws_shot("humble","r5_hero_a",(-24,4,14),(2,33,0.5),lens=30)
ws_shot("humble","r5_hip",(0-10,22-9,6.5),(0,22,2.5),lens=35)
print(len(asm.objects), time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: refreshed 9\n175 2.7117137908935547\n"}

# ==============================================================================================================
# [0016] 2026-09-23 16:03:15  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble", g=g, names=["SM_VK_Prop_HayRack","SM_VK_Animal_Chickens","SM_VK_InnerCorner_Wattle","SM_VK_LeanTo_Thatch_Low","SM_VK_Animal_Cow"])
for s in ws_stats(objs): print(s)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_InnerCorner_Wattle', 'tris': 228, 'bbox': [0.45, 0.44, 3.01], 'zmin': -0.6, 'mats': [0, 2, 45]}
# \n{'name': 'SM_VK_LeanTo_Thatch_Low', 'tris': 2330, 'bbox': [3.73, 3.44, 3.76], 'zmin': -0.6, 'mats': [0, 2, 22, 45]}\n{'name': 'SM_VK_Animal_Cow', 't
# ris': 2028, 'bbox': [2.61, 1.03, 1.57], 'zmin': 0.0, 'mats': [11, 17, 19, 27, 49, 50]}\n{'name': 'SM_VK_Animal_Chickens', 'tris': 2024, 'bbox': [1.91,
#  1.56, 0.71], 'zmin': -0.0, 'mats': [2, 7, 8, 13, 14, 15, 16, 17, 50]}\n{'name': 'SM_VK_Prop_HayRack', 'tris': 2252, 'bbox': [2.76, 2.05, 2.68], 'zmin
# ': -0.04, 'mats': [2, 16, 22, 23, 45]}\n0.4702942371368408\n"}

# ==============================================================================================================
# [0017] 2026-09-23 16:04:06  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble", g=g, names=["SM_VK_Prop_HayRack","SM_VK_Animal_Cow"])
for s in ws_stats(objs): print(s)
ws_shot("humble","r5_rack_chick",(14.5,-8-5.5,2.6),(14.5,-9,0.9),lens=35)
ws_shot("humble","r5_cow",(0+2.5,-15-4.5,2.0),(0.3,-15,0.9),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Animal_Cow', 'tris': 1992, 'bbox': [2.61, 1.03, 1.57], 'zmin': 0.0, 'mats': [11, 17, 19, 27, 49
# , 50]}\n{'name': 'SM_VK_Prop_HayRack', 'tris': 2052, 'bbox': [2.76, 2.05, 2.68], 'zmin': -0.04, 'mats': [2, 16, 22, 23, 45]}\n1.505530834197998\n"}

# ==============================================================================================================
# [0018] 2026-09-23 16:05:01  blender  ok
# ==============================================================================================================
import bpy
me=bpy.data.objects["SM_VK_Animal_Cow"].data
for i in (1,7,12,15,16,17,22,25,26,29,45,48,49,50):
    m=me.materials[i]
    imgs=[n.image.name for n in m.node_tree.nodes if n.type=="TEX_IMAGE" and n.image] if m.use_nodes else []
    bs=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
    col=tuple(round(c,2) for c in bs.inputs["Base Color"].default_value) if bs else None
    print(i, m.name, imgs, col)
# ---- result ----
# {"result":"Code executed successfully: 1 M_VK_Plaster ['T_VK_Plaster_BC', 'T_VK_Plaster_N', 'T_VK_Plaster_R'] (0.8, 0.8, 0.8, 1.0)\n7 M_VK_FlowerYello
# w [] (0.8, 0.8, 0.8, 1.0)\n12 M_VK_Cloth_Cream ['T_VK_Cloth_BC', 'T_VK_Cloth_N', 'T_VK_Cloth_R'] (0.8, 0.8, 0.8, 1.0)\n15 M_VK_Bread [] (0.8, 0.8, 0.8
# , 1.0)\n16 M_VK_Hay ['T_VK_Straw_BC', 'T_VK_Straw_N', 'T_VK_Straw_R'] (0.8, 0.8, 0.8, 1.0)\n17 M_VK_Paper ['T_VK_Paper_BC', 'T_VK_Paper_N', 'T_VK_Pape
# r_R'] (0.8, 0.8, 0.8, 1.0)\n22 M_VK_Thatch ['T_VK_Thatch_BC', 'T_VK_Thatch_N', 'T_VK_Thatch_R'] (0.8, 0.8, 0.8, 1.0)\n25 M_VK_Burlap ['T_VK_Burlap_BC'
# , 'T_VK_Burlap_N', 'T_VK_Burlap_R'] (0.8, 0.8, 0.8, 1.0)\n26 M_VK_Soil ['T_VK_Soil_BC', 'T_VK_Soil_N', 'T_VK_Soil_R'] (0.8, 0.8, 0.8, 1.0)\n29 M_VK_Cl
# ay ['T_VK_Plaster_BC', 'T_VK_Plaster_N', 'T_VK_Plaster_R'] (0.8, 0.8, 0.8, 1.0)\n45 M_VK_StoneBlock ['T_VK_StoneBlock_BC', 'T_VK_StoneBlock_N', 'T_VK_

# ==============================================================================================================
# [0019] 2026-09-23 16:06:10  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
names=["SM_VK_Prop_HayRack","SM_VK_Animal_Cow","SM_VK_Animal_Horse","SM_VK_Animal_Goat","SM_VK_Animal_Chickens","SM_VK_Animal_Sheep","SM_VK_Animal_Pig"]
objs=ws_build("humble", g=g, names=names)
for s in ws_stats(objs): print(s)
ws_shot("humble","r5_cow2",(0+2.5,-15-4.5,2.0),(0.3,-15,0.9),lens=35)
ws_shot("humble","r5_animals2",(8,-15-6.5,2.4),(8.5,-15,0.6),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Animal_Cow', 'tris': 1992, 'bbox': [2.61, 1.03, 1.57], 'zmin': 0.0, 'mats': [11, 12, 19, 27, 49
# , 50]}\n{'name': 'SM_VK_Animal_Sheep', 'tris': 1172, 'bbox': [1.45, 0.83, 1.07], 'zmin': 0.0, 'mats': [12, 27, 50]}\n{'name': 'SM_VK_Animal_Pig', 'tri
# s': 1254, 'bbox': [1.67, 0.74, 0.85], 'zmin': 0.0, 'mats': [12, 26, 27, 49, 50]}\n{'name': 'SM_VK_Animal_Goat', 'tris': 1264, 'bbox': [1.31, 0.47, 1.3
# 3], 'zmin': 0.0, 'mats': [7, 12, 48, 50]}\n{'name': 'SM_VK_Animal_Horse', 'tris': 1836, 'bbox': [2.95, 0.89, 2.52], 'zmin': 0.0, 'mats': [2, 12, 19, 2
# 7, 48, 50]}\n{'name': 'SM_VK_Animal_Chickens', 'tris': 2024, 'bbox': [1.91, 1.56, 0.71], 'zmin': -0.0, 'mats': [2, 7, 8, 12, 13, 14, 15, 16, 50]}\n{'n
# ame': 'SM_VK_Prop_HayRack', 'tris': 2092, 'bbox': [2.76, 2.05, 2.7], 'zmin': -0.06, 'mats': [2, 16, 22, 23, 45]}\n1.7635412216186523\n"}

# ==============================================================================================================
# [0020] 2026-09-23 16:07:02  blender  ok
# ==============================================================================================================
import bpy, time, hashlib
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
print("identical:", bpy.data.texts["ws_humble"].as_string()==src)
g=ws_ns("humble")
objs=ws_build("humble", g=g)
print(len(objs), "pieces built")
print("refreshed", g["hum_refresh_variants"]([n for n,_,_ in g["WS_SPECS"]]))
L={"SM_VK_Wall_Wattle":(0,0,0),"SM_VK_Wall_Wattle_Window":(3.6,0,0),"SM_VK_Wall_Wattle_Door":(7.2,0,0),"SM_VK_Wall_Wattle_Byre":(10.8,0,0),
   "SM_VK_Wall_Wattle_Frame":(14.4,0,0),"SM_VK_Corner_Wattle":(17.3,0,0),"SM_VK_InnerCorner_Wattle":(18.7,0,0),
   "SM_VK_RoofThatch_Gable_Cruck":(1.2,-8.5,2.4),"SM_VK_RoofThatch_Vent":(6.6,-7.2,1.05),"SM_VK_LeanTo_Thatch_Low":(10.6,-6.3,0),
   "SM_VK_Prop_HayRack":(15.2,-8.2,0),"SM_VK_Prop_ChickenCoop_Wattle":(18.6,-7.6,0),"SM_VK_Deco_MudWallow":(6.6,-10.6,0),
   "SM_VK_Animal_Cow":(0.2,-15,0),"SM_VK_Animal_Horse":(3.7,-15,0),"SM_VK_Animal_Sheep":(6.9,-15,0),"SM_VK_Animal_Pig":(9.2,-15,0),
   "SM_VK_Animal_Goat":(11.5,-15,0),"SM_VK_Animal_Chickens":(14.0,-15,0)}
for o in objs:
    if o.name in L: o.location=L[o.name]
    else: print("no layout", o.name)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: identical: True\n19 pieces built\nrefreshed 9\n1.5738780498504639\n"}

# ==============================================================================================================
# [0021] 2026-09-23 16:07:24  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r6_catalog",(9.5,-31,13.5),(9.5,-7.5,0.8),lens=35)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.7218618392944336\n"}

# ==============================================================================================================
# [0022] 2026-09-23 16:08:30  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
L={"SM_VK_Wall_Wattle":(0,0,0),"SM_VK_Wall_Wattle_Window":(3.6,0,0),"SM_VK_Wall_Wattle_Door":(7.2,0,0),"SM_VK_Wall_Wattle_Byre":(10.8,0,0),
   "SM_VK_Wall_Wattle_Frame":(14.4,0,0),"SM_VK_Corner_Wattle":(17.4,0,0),"SM_VK_InnerCorner_Wattle":(18.8,0,0),
   "SM_VK_RoofThatch_Gable_Cruck":(24.8,-0.6,2.4),"SM_VK_RoofThatch_Vent":(1.2,-7.2,1.05),"SM_VK_LeanTo_Thatch_Low":(5.4,-5.2,0),
   "SM_VK_Prop_HayRack":(10.2,-7.0,0),"SM_VK_Prop_ChickenCoop_Wattle":(13.8,-6.6,0),"SM_VK_Deco_MudWallow":(17.8,-7.2,0),
   "SM_VK_Animal_Cow":(0.3,-12.6,0),"SM_VK_Animal_Horse":(4.2,-12.6,0),"SM_VK_Animal_Sheep":(7.6,-12.6,0),"SM_VK_Animal_Pig":(10.0,-12.6,0),
   "SM_VK_Animal_Goat":(12.4,-12.6,0),"SM_VK_Animal_Chickens":(15.2,-12.6,0)}
for n,p in L.items():
    o=bpy.data.objects[n]; o.location=p; o.rotation_euler=(0,0,0)
bpy.data.objects["SM_VK_RoofThatch_Gable_Cruck"].rotation_euler=(0,0,math.radians(-90))
ws_shot("humble","r6_catalog2",(12.5,-31,11.5),(12.5,-5.5,1.0),lens=32)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.8091199398040771\n"}

# ==============================================================================================================
# [0023] 2026-09-23 16:08:56  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
L={"SM_VK_RoofThatch_Vent":(0.6,-9.2,1.05),"SM_VK_LeanTo_Thatch_Low":(5.0,-7.4,0),
   "SM_VK_Prop_HayRack":(10.0,-9.2,0),"SM_VK_Prop_ChickenCoop_Wattle":(13.6,-8.8,0),"SM_VK_Deco_MudWallow":(17.6,-9.4,0),
   "SM_VK_Animal_Cow":(0.6,-15.2,0),"SM_VK_Animal_Horse":(4.4,-15.2,0),"SM_VK_Animal_Sheep":(7.8,-15.2,0),"SM_VK_Animal_Pig":(10.2,-15.2,0),
   "SM_VK_Animal_Goat":(12.6,-15.2,0),"SM_VK_Animal_Chickens":(15.4,-15.2,0)}
for n,p in L.items(): bpy.data.objects[n].location=p
ws_shot("humble","r6_catalog3",(12,-37,14),(12,-7.2,0.6),lens=30)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.8330390453338623\n"}

# ==============================================================================================================
# [0024] 2026-09-23 16:09:54  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r6_catalog4",(12.5,-30.5,10.5),(12.5,-8.2,0.2),lens=33)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.8137991428375244\n"}

# ==============================================================================================================
# [0025] 2026-09-23 16:10:35  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
L={"SM_VK_RoofThatch_Vent":(2.2,-9.2,1.05),"SM_VK_LeanTo_Thatch_Low":(6.6,-7.4,0),
   "SM_VK_Prop_HayRack":(11.4,-9.2,0),"SM_VK_Prop_ChickenCoop_Wattle":(15.0,-8.8,0),"SM_VK_Deco_MudWallow":(18.9,-9.4,0),
   "SM_VK_Animal_Cow":(4.0,-15.2,0),"SM_VK_Animal_Horse":(7.7,-15.2,0),"SM_VK_Animal_Sheep":(11.0,-15.2,0),"SM_VK_Animal_Pig":(13.3,-15.2,0),
   "SM_VK_Animal_Goat":(15.6,-15.2,0),"SM_VK_Animal_Chickens":(18.3,-15.2,0)}
for n,p in L.items(): bpy.data.objects[n].location=p
ws_shot("humble","r6_catalog5",(13.2,-31.5,11),(13.2,-8.2,0.2),lens=31)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.7175281047821045\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:11:44  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r7_hero_hamlet",(29,5,15),(1,33,0),lens=30,res=(1280,720))
ws_shot("humble","r7_hero_colony",(2,33-25.7,30.6),(2,33,0),lens=30,res=(1280,720))
ws_shot("humble","r7_hero_longhouse",(21,24.5,6.5),(5,40,1.5),lens=30,res=(1280,720))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 2.017218828201294\n"}

# ==============================================================================================================
# [0027] 2026-09-23 16:12:21  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("humble","r7_hero_colony2",(2,31-27.5,32.8),(2,31,0),lens=28,res=(1280,720))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 0.8148388862609863\n"}

# ==============================================================================================================
# [0028] 2026-09-23 16:13:09  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
R=(1600,900)
print(ws_shot("humble","catalog_final",(13.2,-31.5,11),(13.2,-7.6,0.2),lens=31,res=R,samples=64))
print(ws_shot("humble","hero_hamlet",(29,5,15),(1,33,0),lens=30,res=R,samples=64))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\catalog_final.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\hero_hamlet.png\n1.642
# 289400100708\n"}

# ==============================================================================================================
# [0029] 2026-09-23 16:13:39  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
R=(1600,900)
print(ws_shot("humble","hero_colony",(2,31-27.5,32.8),(2,31,0),lens=28,res=R,samples=64))
print(ws_shot("humble","hero_longhouse",(21,24.5,6.5),(5,40,1.5),lens=30,res=R,samples=64))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\hero_colony.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspa
# ces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\hero_longhouse.png\n1.67
# 43085384368896\n"}

# ==============================================================================================================
# [0030] 2026-09-23 16:14:45  blender  ok
# ==============================================================================================================
import bpy, time, math
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
print("text identical to file:", bpy.data.texts["ws_humble"].as_string()==src)
g=ws_ns("humble")
objs=ws_build("humble", g=g)
print("built", len(objs), [o.name for o in objs if o.name not in [n for n,_,_ in g["WS_SPECS"]]])
g["hum_refresh_variants"]([n for n,_,_ in g["WS_SPECS"]])
ws_clear_assembly("humble")
sc,coll,asm=ws_scene("humble")
cnt={}
for nm,args,kw in (("build_hovel",(asm,(-16,22,0)),dict(seed=1,variant="cruck")),("build_hovel",(asm,(0,22,0)),dict(seed=2,variant="hip")),
                   ("build_hovel",(asm,(16,22,0)),dict(seed=3,variant="leanto")),("build_longhouse",(asm,(0,40,0)),dict(seed=4)),
                   ("build_pigsty",(asm,(-16.5,38.5,0)),dict(seed=5)),("build_sheepfold",(asm,(19.5,38.5,0)),dict(seed=6))):
    parts=g[nm](*args,**kw); cnt[nm+str(kw.get("variant",""))]=len(parts)
print(cnt, len(asm.objects))
cr=bpy.data.objects["SM_VK_RoofThatch_Gable_Cruck"]; rz=cr.rotation_euler.z; cr.rotation_euler.z=0
bpy.context.view_layer.update() if False else None
for o in objs: o.matrix_world=o.matrix_basis
for s in ws_stats(objs): print(s["name"], s["tris"], s["bbox"], s["zmin"])
cr.rotation_euler.z=rz
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: text identical to file: True\nbuilt 19 []\n{'build_hovelcruck': 25, 'build_hovelhip': 24, 'build_hovelleanto': 
# 27, 'build_longhouse': 48, 'build_pigsty': 26, 'build_sheepfold': 25} 175\nSM_VK_Wall_Wattle 1924 [3.13, 0.52, 3.0] -0.6\nSM_VK_Wall_Wattle_Window 252
# 2 [3.13, 0.96, 3.0] -0.6\nSM_VK_Wall_Wattle_Door 2524 [3.13, 1.42, 3.0] -0.6\nSM_VK_Wall_Wattle_Byre 2900 [3.13, 1.94, 3.0] -0.6\nSM_VK_Wall_Wattle_Fr
# ame 1652 [3.13, 0.96, 3.0] -0.6\nSM_VK_Corner_Wattle 660 [0.76, 0.8, 3.01] -0.6\nSM_VK_InnerCorner_Wattle 228 [0.45, 0.44, 3.01] -0.6\nSM_VK_RoofThatc
# h_Gable_Cruck 5148 [4.18, 9.11, 6.87] -2.47\nSM_VK_RoofThatch_Vent 808 [1.69, 1.25, 1.84] -0.64\nSM_VK_LeanTo_Thatch_Low 2330 [3.73, 3.44, 3.76] -0.6\
# nSM_VK_Animal_Cow 1992 [2.61, 1.03, 1.57] 0.0\nSM_VK_Animal_Sheep 1172 [1.45, 0.83, 1.07] 0.0\nSM_VK_Animal_Pig 1254 [1.67, 0.74, 0.85] 0.0\nSM_VK_Ani

# ==============================================================================================================
# [0031] 2026-09-23 16:16:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("humble")
print("RIDGE",g["RIDGE"],"HALF",g["HALF"],"GX",g["GX"],"under0",g["hum_under"](0),"smokehole z",g["hum_under"](0)-0.62, "XD", g["HUM_CRUCK_X"]-0.09)
# ---- result ----
# {"result":"Code executed successfully: RIDGE 4.189824896579236 HALF 3.0 GX 2.45 under0 3.6525441229344136 smokehole z 3.0325441229344134 XD 1.60999999
# 99999999\n"}
