# village-kit-buildings-continue / agent-aca1ca98295d25113.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:46:01  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence")
bt=t.as_string() if t else None
print("local",len(src),hashlib.md5(src.encode()).hexdigest())
if bt is not None: print("blender",len(bt),hashlib.md5(bt.encode()).hexdigest(), bt==src, bt.rstrip()==src.rstrip())
sc=bpy.data.scenes.get("WS_defence"); print(sc)
for cn in ("WS_defence_Pieces","WS_defence_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, c and len(c.objects))
c=bpy.data.collections.get("WS_defence_Pieces")
if c: print(sorted(o.name for o in c.objects))
# ---- result ----
# {"result":"Code executed successfully: local 78724 c41034c427e4541d0a782def66b0a4eb\nblender 66909 c79f057995e920511cd38bcef03f215e False False\n<bpy_
# struct, Scene(\"WS_defence\") at 0x000001CBDAA60088>\nWS_defence_Pieces 39\nWS_defence_Assembly 0\n['SM_VK_Deco_Hedge', 'SM_VK_Def_Bartizan', 'SM_VK_D
# ef_CornerUp', 'SM_VK_Def_StoneUp', 'SM_VK_Def_StoneUp_Door', 'SM_VK_Def_StoneUp_Slit', 'SM_VK_Def_StoneUp_Window', 'SM_VK_Gatehouse_Block', 'SM_VK_Gat
# ehouse_GateLeaf', 'SM_VK_Gatehouse_Portcullis', 'SM_VK_LowWall_GateArch', 'SM_VK_Palisade_Diag', 'SM_VK_Palisade_Gate', 'SM_VK_Palisade_GateLeaf', 'SM
# _VK_Palisade_Ladder', 'SM_VK_Palisade_Post', 'SM_VK_Palisade_Straight', 'SM_VK_Palisade_Tower', 'SM_VK_Palisade_Walk', 'SM_VK_Parapet_Corner', 'SM_VK_
# Parapet_Crenel', 'SM_VK_Prop_ArcheryButt', 'SM_VK_Prop_ArmorStand', 'SM_VK_Prop_Beacon', 'SM_VK_Prop_MarketCross', 'SM_VK_Prop_Maypole', 'SM_VK_Prop_P

# ==============================================================================================================
# [0002] 2026-09-23 15:46:44  blender  ok
# ==============================================================================================================
import bpy, difflib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
bt=bpy.data.texts["ws_defence"].as_string()
d=list(difflib.unified_diff(bt.splitlines(),src.splitlines(),"blender","local",n=0,lineterm=""))
hdr=[l for l in d if l.startswith("@@")]
print(len(d)); print("\n".join(hdr[:80]))
# ---- result ----
# {"result":"Code executed successfully: 283\n@@ -942,5 +942,7 @@\n@@ -947,0 +950 @@\n@@ -950,0 +954 @@\n@@ -959,6 +963,8 @@\n@@ -966 +972,6 @@\n@@ -968
# ,7 +979,13 @@\n@@ -1109,2 +1126,3 @@\n@@ -1141 +1159 @@\n@@ -1143,0 +1162 @@\n@@ -1145,6 +1164,146 @@\n@@ -1152,8 +1311,47 @@\n"}

# ==============================================================================================================
# [0003] 2026-09-23 15:46:56  blender  ok
# ==============================================================================================================
import bpy, difflib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
bt=bpy.data.texts["ws_defence"].as_string()
d=list(difflib.unified_diff(bt.splitlines(),src.splitlines(),"blender","local",n=0,lineterm=""))
out=[]
for l in d[:200]:
    out.append(l[:150])
print("\n".join(out[:75]))
# ---- result ----
# {"result":"Code executed successfully: --- blender\n+++ local\n@@ -942,5 +942,7 @@\n- _ico(k,(0.3*s,0,1.52),0.15,STEEL,(1.1,1.0,0.7),sub=2)\n- k.box((
# 0.3*s,0,1.47),(0.26,0.26,0.03),BRONZE,bevel=0.01)\n- k.box((0,-0.22,1.3),(0.34,0.06,0.5),CLOTH_A,bevel=0.02) # tabard front\n- k.box((0,-0.26,1.33),(0
# .14,0.02,0.18),YELLOW,bevel=0.01)\n- ring(k,(0,0,1.05),0.19,0.27,0.07,WOOD,n=10,axis=\"Z\") # belt\n+ _ico(k,(0.31*s,0,1.53),0.17,STEEL,(1.1,1.05,0.7)
# ,sub=2)\n+ ring(k,(0.31*s,0,1.47),0.14,0.2,0.04,BRONZE,n=10,axis=\"Z\")\n+ k.box((0,-0.24,1.24),(0.4,0.06,0.62),CLOTH_A,bevel=0.02) # tabard front\n+ 
# k.box((0,-0.28,1.3),(0.16,0.02,0.2),YELLOW,bevel=0.01)\n+ ring(k,(0,0,1.05),0.19,0.28,0.08,HIDE,n=10,axis=\"Z\") # belt\n+ k.box((0,-0.28,1.05),(0.08,
# 0.02,0.08),BRONZE,bevel=0.01)\n+ ring(k,(0,0,1.56),0.16,0.25,0.05,BRONZE,n=10,axis=\"Z\") # gorget\n@@ -947,0 +950 @@\n+ ring(k,(0,0,1.74),0.165,0.185

# ==============================================================================================================
# [0004] 2026-09-23 15:47:06  blender  ok
# ==============================================================================================================
import bpy
print(bpy.data.texts["ws_common"].as_string())
# ---- result ----
# {"result":"Code executed successfully: # ===================== WORKSHOP HELPERS (shared, read-only for agents) =====================\n# Usage in any e
# xecute_blender_code call:\n# exec(bpy.data.texts[\"ws_common\"].as_string()); g=ws_ns(\"hovel\") # kit namespace + your module\nimport bpy, os, math, 
# json\nfrom mathutils import Vector\nWS_RENDERS=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56
# \\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\n\ndef ws_ns(agent=None):\n \"\"\"fresh namespace with the whole village
#  kit (vk_helpers) + your module text 'ws_<agent>' executed on top\"\"\"\n g={}\n exec(bpy.data.texts[\"vk_helpers\"].as_string(),g)\n if agent:\n t=bp
# y.data.texts.get(\"ws_\"+agent)\n if t: exec(t.as_string(),g)\n return g\n\ndef _copy_props(dst,src):\n for p in src.bl_rna.properties:\n if p.is_read

# ==============================================================================================================
# [0005] 2026-09-23 15:47:38  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
t0=time.time(); g=ws_ns("defence"); print("ns",time.time()-t0, len(g["WS_SPECS"]))
names=[s[0] for s in g["WS_SPECS"]]
t0=time.time(); objs=ws_build("defence",names=names[:12],g=g); print("build12",time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: ns 0.08660507202148438 39\nbuild12 0.9657962322235107\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:47:54  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time(); g=ws_ns("defence"); objs=ws_build("defence",g=g); print("build all",time.time()-t0,len(objs))
for s in ws_stats(objs): print(s)
# ---- result ----
# {"result":"Code executed successfully: build all 3.545768976211548 39\n{'name': 'SM_VK_Palisade_Straight', 'tris': 1338, 'bbox': [3.0, 0.5, 4.68], 'zm
# in': -0.8, 'mats': [2, 25, 33, 35, 40]}\n{'name': 'SM_VK_Palisade_Diag', 'tris': 1838, 'bbox': [4.27, 0.51, 4.7], 'zmin': -0.8, 'mats': [2, 25, 33, 35
# , 40]}\n{'name': 'SM_VK_Palisade_Post', 'tris': 654, 'bbox': [1.0, 1.0, 5.0], 'zmin': -0.8, 'mats': [25, 33, 40]}\n{'name': 'SM_VK_Palisade_Walk', 'tr
# is': 816, 'bbox': [3.11, 1.1, 2.9], 'zmin': -0.6, 'mats': [2, 23, 33, 40]}\n{'name': 'SM_VK_Palisade_Ladder', 'tris': 248, 'bbox': [0.64, 0.87, 2.91],
#  'zmin': -0.01, 'mats': [2]}\n{'name': 'SM_VK_Palisade_Gate', 'tris': 2372, 'bbox': [4.12, 0.94, 6.1], 'zmin': -0.9, 'mats': [2, 5, 7, 9, 11, 14, 25, 
# 33, 40]}\n{'name': 'SM_VK_Palisade_GateLeaf', 'tris': 820, 'bbox': [1.51, 0.55, 3.35], 'zmin': 0.05, 'mats': [2, 5, 33, 40]}\n{'name': 'SM_VK_Palisade

# ==============================================================================================================
# [0007] 2026-09-23 15:48:41  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["WS_defence"]
print([o.name for o in sc.collection.objects])
print([c.name for c in sc.collection.children])
for c in sc.collection.children: print(c.name, len(c.all_objects))
# ---- result ----
# {"result":"Code executed successfully: ['VK_Sun', 'WS_defence_Ground', 'WS_defence_Cam']\n['WS_defence_Pieces', 'WS_defence_Assembly']\nWS_defence_Pie
# ces 39\nWS_defence_Assembly 0\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:49:47  blender  ok
# ==============================================================================================================
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
ws_clear_assembly("defence")
jobs=[("build_palisade_demo",(20,60,0),{}),("build_townwall_demo",(80,60,0),{}),("build_tower_house",(135,60,0),{}),
      ("build_training_yard",(20,115,0),{}),("build_festival_green",(75,115,0),{}),("build_tower_house",(165,60,0),{"kind":"domestic"})]
for fn,org,kw in jobs:
    t0=time.time(); n0=len(asm.objects)
    try:
        g[fn](asm,org,**kw); print(fn,kw,"ok",len(asm.objects)-n0,"objs",round(time.time()-t0,2),"s")
    except Exception as e:
        print(fn,"ERR",traceback.format_exc()[-800:])
# ---- result ----
# {"result":"Code executed successfully: build_palisade_demo {} ok 42 objs 0.01 s\nbuild_townwall_demo {} ok 48 objs 0.02 s\nbuild_tower_house {} ok 71 
# objs 0.05 s\nbuild_training_yard {} ok 72 objs 0.03 s\nbuild_festival_green {} ok 33 objs 0.01 s\nbuild_tower_house {'kind': 'domestic'} ok 71 objs 0.
# 05 s\n"}

# ==============================================================================================================
# [0009] 2026-09-23 15:50:33  blender  ok
# ==============================================================================================================
import bpy
for n in ["SM_VK_Wall_StoneUp","SM_VK_Wall_StoneUp_Slit","SM_VK_Wall_StoneUp_Window","SM_VK_Wall_StoneUp_Door","SM_VK_Corner_StoneUp","SM_VK_Stair_Stone_Ext","SM_VK_Stair_Ext","SM_VK_Banner_Wall","SM_VK_Banner_Roof","SM_VK_Banner_Pole","SM_VK_Prop_Bunting_6","SM_VK_Roof_Hip_Plain","SM_VK_Turret_Seg_Stone","SM_VK_Turret_Corbel","SM_VK_Turret_Cap","SM_VK_Prop_WeaponRack","SM_VK_Prop_Festoon","SM_VK_LowWall","SM_VK_LowWall_Post","SM_VK_Deco_Ivy_A","SM_VK_Deco_Weeds","SM_VK_Prop_LampPost","SM_VK_Prop_Table","SM_VK_Prop_Stool","SM_VK_Prop_Bench"]:
    o=bpy.data.objects.get(n); print(n, None if o is None else [c.name for c in o.users_collection])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_StoneUp ['WS_town_Pieces']\nSM_VK_Wall_StoneUp_Slit ['WS_town_Pieces']\nSM_VK_Wall_StoneUp_Window ['
# WS_town_Pieces']\nSM_VK_Wall_StoneUp_Door ['WS_town_Pieces']\nSM_VK_Corner_StoneUp ['WS_town_Pieces']\nSM_VK_Stair_Stone_Ext ['WS_town_Pieces']\nSM_VK
# _Stair_Ext ['VK_Pieces']\nSM_VK_Banner_Wall ['WS_skyline_Pieces']\nSM_VK_Banner_Roof ['WS_skyline_Pieces']\nSM_VK_Banner_Pole ['WS_skyline_Pieces']\nS
# M_VK_Prop_Bunting_6 ['WS_skyline_Pieces']\nSM_VK_Roof_Hip_Plain ['WS_skyline_Pieces']\nSM_VK_Turret_Seg_Stone ['WS_town_Pieces']\nSM_VK_Turret_Corbel 
# ['WS_town_Pieces']\nSM_VK_Turret_Cap ['WS_town_Pieces']\nSM_VK_Prop_WeaponRack ['VK_Pieces']\nSM_VK_Prop_Festoon ['VK_Pieces']\nSM_VK_LowWall ['VK_Pie
# ces']\nSM_VK_LowWall_Post ['VK_Pieces']\nSM_VK_Deco_Ivy_A ['VK_Pieces']\nSM_VK_Deco_Weeds ['VK_Pieces']\nSM_VK_Prop_LampPost ['VK_Pieces']\nSM_VK_Prop

# ==============================================================================================================
# [0010] 2026-09-23 15:51:10  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("defence")
objs=sorted(coll.objects,key=lambda o:o.name)
g=ws_ns("defence"); order=[s[0] for s in g["WS_SPECS"]]
objs=[bpy.data.objects[n] for n in order]
ws_grid(objs,cols=10,sx=9,sy=12)
t0=time.time()
p=ws_shot("defence","th_v1",(150-8,60-30,22),(150,60,7),lens=35)
print(p,time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\defence\\th_v1.png 0.7924776077270508\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:51:45  blender  ok
# ==============================================================================================================
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
objs=[bpy.data.objects[s[0]] for s in g["WS_SPECS"]]
ws_grid(objs,cols=10,sx=9,sy=11,origin=(-52,-22))
ws_clear_assembly("defence")
jobs=[("build_palisade_demo",(-40,32,0),{}),("build_townwall_demo",(8,26,0),{}),("build_tower_house",(44,30,0),{}),
      ("build_training_yard",(-40,2,0),{}),("build_festival_green",(6,-2,0),{}),("build_tower_house",(44,4,0),{"kind":"domestic","seed":3})]
for fn,org,kw in jobs:
    try: g[fn](asm,org,**kw)
    except Exception as e: print(fn,"ERR",traceback.format_exc()[-800:])
print(len(asm.objects))
p=ws_shot("defence","th_v2",(44-14,30-26,20),(44,30,6.5),lens=35)
p=ws_shot("defence","th_v2b",(44+20,4-22,18),(44,4,6.5),lens=35)
# ---- result ----
# {"result":"Code executed successfully: 337\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:53:55  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
ws_shot("defence","ty_v1",(-40+14,2-24,16),(-40,1.5,1.5),lens=35)
ws_shot("defence","fg_v1",(6+12,-2-22,14),(6,-1,1.5),lens=35)
ws_shot("defence","th2_v3",(44+20,4-22,18),(44,4,6.5),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0013] 2026-09-23 15:54:27  blender  ok
# ==============================================================================================================
import bpy
asm=bpy.data.collections["WS_defence_Assembly"]
for o in asm.objects:
    if "Turret" in o.name: print(o.name, tuple(round(v,2) for v in o.location), round(o.rotation_euler.z,2))
print("z0=top-H2" in bpy.data.texts["ws_defence"].as_string())
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Turret_Corbel_inst.002 (41.0, 1.0, 8.6) 0.0\nSM_VK_Turret_Seg_Stone_inst.003 (41.0, 1.0, 8.6) 0.0\nSM_VK_
# Turret_Seg_Stone_inst.004 (41.0, 1.0, 11.4) 0.0\nSM_VK_Turret_Cap_inst.002 (41.0, 1.0, 14.2) 0.0\nSM_VK_Turret_Corbel_inst.003 (47.0, 1.0, 8.6) 1.57\n
# SM_VK_Turret_Seg_Stone_inst.005 (47.0, 1.0, 8.6) 1.57\nSM_VK_Turret_Seg_Stone_inst.006 (47.0, 1.0, 11.4) 1.57\nSM_VK_Turret_Cap_inst.003 (47.0, 1.0, 1
# 4.2) 1.57\nSM_VK_Turret_Corbel_inst.004 (47.0, 7.0, 8.6) 3.14\nSM_VK_Turret_Seg_Stone_inst.007 (47.0, 7.0, 8.6) 3.14\nSM_VK_Turret_Seg_Stone_inst.008 
# (47.0, 7.0, 11.4) 3.14\nSM_VK_Turret_Cap_inst.004 (47.0, 7.0, 14.2) 3.14\nSM_VK_Turret_Corbel_inst.005 (41.0, 7.0, 8.6) -1.57\nSM_VK_Turret_Seg_Stone_
# inst.009 (41.0, 7.0, 8.6) -1.57\nSM_VK_Turret_Seg_Stone_inst.010 (41.0, 7.0, 11.4) -1.57\nSM_VK_Turret_Cap_inst.005 (41.0, 7.0, 14.2) -1.57\nTrue\n"}

# ==============================================================================================================
# [0014] 2026-09-23 15:55:23  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string()) if False else None
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","tw_v3_front",(8+2,26-30,6),(8+2,26,4),lens=30)
ws_shot("defence","tw_v3_back",(8-4,26+26,16),(8+2,26,3),lens=32)
ws_shot("defence","cat_v3",(-10,-75,40),(-10,-35,2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 15:55:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","pr_a",(-14,-54,4.5),(-14,-44,1.2),lens=30)
ws_shot("defence","pr_b",(-44,-65,5),(-44,-55,1.5),lens=30)
ws_shot("defence","pal_v3",(-40+16,32-26,18),(-40,32,1.5),lens=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0016] 2026-09-23 15:56:36  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","pal_gate",(-40+1.5+3,32-6-11,3.5),(-40+1.5,32-6,2.0),lens=30)
ws_shot("defence","pal_in",(-40+2,32+4,6),(-40-2,32-6,2.5),lens=28)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0017] 2026-09-23 15:57:14  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ox,oy=8,26
ws_shot("defence","tw_right",(ox+30,oy-16,9),(ox+19,oy-3,3.5),lens=30)
ws_shot("defence","tw_left",(ox-22,oy-14,9),(ox-10,oy+1,3.5),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0018] 2026-09-23 15:59:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ox,oy=8,26
ws_shot("defence","gh_stair",(ox-9,oy+9,10.5),(ox-3.5,oy+1.2,6.6),lens=30)
ws_shot("defence","gh_pass",(ox+1.5,oy+11,2.2),(ox+1.5,oy-2,2.4),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0019] 2026-09-23 16:01:13  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=["SM_VK_Gatehouse_Block"])
ws_shot("defence","ty_v2",(-40+13,2-20,11),(-40,0.5,2.0),lens=32)
ox,oy=8,26
ws_shot("defence","gh_back2",(ox+1.5+6,oy+16,9),(ox+1.5,oy+2,5.5),lens=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0020] 2026-09-23 16:02:49  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=["SM_VK_Gatehouse_Block"],asm_jobs=None)
import math
tx,ty=12,26; d=40; p=math.radians(50)
ws_shot("defence","colony_tw",(tx+d*math.cos(p)*math.sin(0.35),ty-d*math.cos(p)*math.cos(0.35),d*math.sin(p)),(tx,ty,2),lens=35)
tx,ty=-20,18
ws_shot("defence","colony_pal",(tx+d*math.cos(p)*math.sin(-0.3),ty-d*math.cos(p)*math.cos(-0.3),d*math.sin(p)),(tx,ty,2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0021] 2026-09-23 16:04:40  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all()
for y,names in D_ROWS:
    o0=bpy.data.objects["SM_VK_"+names[0]]; o1=bpy.data.objects["SM_VK_"+names[-1]]; print(y, round(o0.location.x,1), round(o1.location.x,1))
ws_shot("defence","cat_v4",(0,-92,34),(0,-36,1.5),lens=35,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: -19.0 -14.5 15.0\n-31.0 -23.7 23.7\n-40.5 -25.3 23.9\n-49.5 -16.8 16.0\n"}

# ==============================================================================================================
# [0022] 2026-09-23 16:05:53  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
import math
tx,ty=14,32; d=48; p=math.radians(50); yaw=0.25
ws_shot("defence","colony_town_v1",(tx+d*math.cos(p)*math.sin(yaw),ty-d*math.cos(p)*math.cos(yaw),d*math.sin(p)),(tx,ty,2),lens=35,res=(1280,720))
ws_shot("defence","hero_town_v1",(tx+14,ty-34,13),(tx+1,ty+2,5),lens=32,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0023] 2026-09-23 16:07:02  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
import math
tx,ty=12,34; d=52; p=math.radians(50); yaw=0.3
ws_shot("defence","colony_town_v2",(tx+d*math.cos(p)*math.sin(yaw),ty-d*math.cos(p)*math.cos(yaw),d*math.sin(p)),(tx,ty,2),lens=35,res=(1280,720))
ws_shot("defence","tw_ends",(8+30,26-22,10),(8+21,26-8,4),lens=32,res=(1280,720))
ws_shot("defence","tw_pal",(8-26,26-4,9),(8-12,26+8,3),lens=32,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0024] 2026-09-23 16:09:27  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=["SM_VK_Def_Standin_Plateau","SM_VK_Def_Standin_Ramp","SM_VK_Gatehouse_Block","SM_VK_Prop_MarketCross","SM_VK_LowWall_GateArch","SM_VK_Deco_Hedge","SM_VK_Prop_Pillory","SM_VK_Prop_Stage","SM_VK_Prop_Stocks"])
ws_shot("defence","tw_ends2",(8+34,26-26,11),(8+20,26-7,3),lens=32,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0025] 2026-09-23 16:10:31  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
tx,ty=12,32; d=56; p=math.radians(50); yaw=0.2
ws_shot("defence","colony_town_v3",(tx+d*math.cos(p)*math.sin(yaw),ty-d*math.cos(p)*math.cos(yaw),d*math.sin(p)),(tx,ty,2),lens=35,res=(1280,720))
ws_shot("defence","hero_town_v2",(8-18,26-30,12),(8+4,26+3,5),lens=30,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0026] 2026-09-23 16:11:12  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for n in ("SM_VK_Prop_Stocks","SM_VK_Prop_Stage","SM_VK_Deco_Hedge","SM_VK_Def_Standin_Plateau","SM_VK_Parapet_Crenel","SM_VK_Def_StoneUp_Door"):
    o=bpy.data.objects[n]; print(n, tuple(round(v,1) for v in o.location))
ws_shot("defence","row4_a",(-8,-60.5,5),(-8,-49.5,1.2),lens=32,res=(1280,720))
ws_shot("defence","row4_b",(10,-61,6),(10,-49.5,1.2),lens=32,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Stocks (-12.5, -49.5, 0.0)\nSM_VK_Prop_Stage (0.6, -49.5, 0.0)\nSM_VK_Deco_Hedge (11.4, -49.5, 0.0)\
# nSM_VK_Def_Standin_Plateau (20.5, -49.5, 0.0)\nSM_VK_Parapet_Crenel (0.7, -40.5, 0.0)\nSM_VK_Def_StoneUp_Door (23.9, -40.5, 0.0)\n"}

# ==============================================================================================================
# [0027] 2026-09-23 16:12:08  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False,asm_jobs=("pal","tw","th","ty","fg","th2"))
ws_shot("defence","hero_frontier_v1",(-40+22,22-30,17),(-40+1,22+1,2.5),lens=32,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0028] 2026-09-23 16:13:26  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
ws_shot("defence","hero_frontier_v2",(-30+8,31-34,16),(-30,31+1,2.5),lens=30,res=(1280,720))
import math
tx,ty=-6,32; d=75; p=math.radians(50); yaw=0.1
ws_shot("defence","colony_all_v1",(tx+d*math.cos(p)*math.sin(yaw),ty-d*math.cos(p)*math.cos(yaw),d*math.sin(p)),(tx,ty,2),lens=35,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0029] 2026-09-23 16:14:41  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","th_top",(4-7,42-9,16.5),(4,42,12.2),lens=30,res=(1280,720))
ws_shot("defence","pal_tower_close",(-40-9+7,36-6-8,8),(-40-9,36-6,5),lens=30,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0030] 2026-09-23 16:18:21  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=["SM_VK_TownWall_Tower_Round"],asm_jobs=None)
print(ws_stats([bpy.data.objects["SM_VK_TownWall_Tower_Round"]]))
ox,oy=8,26
ws_shot("defence","trt_walk",(ox+12-7.5,oy+2.5,8.2),(ox+12-2,oy,7.2),lens=28,res=(1280,720))
ws_shot("defence","trt_out",(ox+12-9,oy-12,10),(ox+12,oy,7.5),lens=30,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_TownWall_Tower_Round', 'tris': 9271, 'bbox': [7.16, 7.14, 13.97], 'zmin': -1.5, 'mats': [0, 2,
#  5, 11, 19, 23, 24, 27, 45]}]\n"}

# ==============================================================================================================
# [0031] 2026-09-23 16:18:59  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","trt_walk2",(14.6,26.9,8.0),(20,26.3,7.3),lens=24,res=(1280,720))
ws_shot("defence","trt_walk3",(25.4,25.6,8.0),(20,26.3,7.3),lens=24,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0032] 2026-09-23 16:19:58  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
ws_shot("defence","fg_v2",(17+9,42-17,9),(17,42,1.5),lens=30,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0033] 2026-09-23 16:20:34  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for s in ws_stats([bpy.data.objects[n] for n in ("SM_VK_Gatehouse_Block","SM_VK_Prop_MarketCross","SM_VK_LowWall_GateArch","SM_VK_Deco_Hedge","SM_VK_Def_Standin_Plateau","SM_VK_Def_Standin_Ramp","SM_VK_Prop_Stage","SM_VK_Prop_Pillory","SM_VK_Prop_Stocks")]): print(s)
ox,oy=8,26
ws_shot("defence","gh_back3",(ox+1.5+5,oy+13,6),(ox+1.5,oy+3,3.5),lens=30,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Gatehouse_Block', 'tris': 11956, 'bbox': [10.64, 8.57, 10.5], 'zmin': -1.5, 'mats': [0, 2, 5, 7
# , 9, 14, 24, 27, 45]}\n{'name': 'SM_VK_Prop_MarketCross', 'tris': 1320, 'bbox': [3.4, 3.4, 6.64], 'zmin': -0.6, 'mats': [6, 7, 8, 9, 17, 19, 24, 27, 4
# 5]}\n{'name': 'SM_VK_LowWall_GateArch', 'tris': 3120, 'bbox': [3.38, 0.77, 4.25], 'zmin': -0.6, 'mats': [0, 5, 45]}\n{'name': 'SM_VK_Deco_Hedge', 'tri
# s': 840, 'bbox': [3.34, 1.1, 1.92], 'zmin': -0.6, 'mats': [26, 31, 37]}\n{'name': 'SM_VK_Def_Standin_Plateau', 'tris': 408, 'bbox': [3.59, 3.56, 1.55]
# , 'zmin': -1.55, 'mats': [37, 38, 45, 46]}\n{'name': 'SM_VK_Def_Standin_Ramp', 'tris': 8, 'bbox': [3.0, 3.0, 1.55], 'zmin': -1.55, 'mats': [37, 46]}\n
# {'name': 'SM_VK_Prop_Stage', 'tris': 2224, 'bbox': [6.3, 4.08, 4.63], 'zmin': -0.6, 'mats': [2, 5, 7, 11, 12, 23, 40]}\n{'name': 'SM_VK_Prop_Pillory',

# ==============================================================================================================
# [0034] 2026-09-23 16:21:31  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
print(t.as_string()==src, len(src), hashlib.md5(src.encode()).hexdigest())
# ---- result ----
# {"result":"Code executed successfully: True 84945 daf54dd778e6f1be88b3b26f4400b6ce\n"}

# ==============================================================================================================
# [0035] 2026-09-23 16:22:12  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time()
g=ws_ns("defence")
objs=ws_build("defence", g=g)
print("built",len(objs),"pieces in",round(time.time()-t0,2),"s")
st=ws_stats(objs)
for s in st: print(s["name"],s["tris"],s["bbox"],s["zmin"])
print("total tris",sum(s["tris"] for s in st))
# ---- result ----
# {"result":"Code executed successfully: built 41 pieces in 3.89 s\nSM_VK_Palisade_Straight 1338 [3.0, 0.5, 4.68] -0.8\nSM_VK_Palisade_Diag 1838 [4.27, 
# 0.51, 4.7] -0.8\nSM_VK_Palisade_Post 654 [1.0, 1.0, 5.0] -0.8\nSM_VK_Palisade_Walk 816 [3.11, 1.1, 2.9] -0.6\nSM_VK_Palisade_Ladder 248 [0.64, 0.87, 2
# .91] -0.01\nSM_VK_Palisade_Gate 2372 [4.12, 0.94, 6.1] -0.9\nSM_VK_Palisade_GateLeaf 820 [1.51, 0.55, 3.35] 0.05\nSM_VK_Palisade_Tower 4842 [4.38, 4.3
# 8, 11.66] -0.9\nSM_VK_Prop_Beacon 2027 [2.7, 2.57, 7.65] -0.8\nSM_VK_TownWall_Straight 2308 [3.45, 2.82, 9.45] -1.5\nSM_VK_TownWall_Corner_Out 1304 [2
# .69, 2.68, 9.66] -1.5\nSM_VK_TownWall_Corner_In 1036 [1.68, 1.68, 7.75] -1.5\nSM_VK_TownWall_Stair 446 [3.07, 1.17, 6.43] -4.2\nSM_VK_TownWall_Step 23
# 36 [3.45, 2.82, 10.57] -1.5\nSM_VK_TownWall_Ruin 2540 [3.53, 5.28, 6.99] -1.5\nSM_VK_TownWall_Tower_Round 9271 [7.16, 7.14, 13.97] -1.5\nSM_VK_Gatehou

# ==============================================================================================================
# [0036] 2026-09-23 16:22:56  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=["SM_VK_LowWall_GateArch"],asm_jobs=None)
print(ws_stats([bpy.data.objects["SM_VK_LowWall_GateArch"]]))
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_LowWall_GateArch', 'tris': 2608, 'bbox': [3.38, 0.77, 4.25], 'zmin': -0.6, 'mats': [0, 5, 45]}
# ]\n"}

# ==============================================================================================================
# [0037] 2026-09-23 16:23:35  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
sc,coll,asm=ws_scene("defence")
print(len(asm.objects))
asm.hide_render=True
try:
    ws_shot("defence","cat_v5",(0,-88,30),(0,-36,1.0),lens=36,res=(1600,900))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: 367\n"}

# ==============================================================================================================
# [0038] 2026-09-23 16:24:24  blender  ok
# ==============================================================================================================
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\def_run.py").read())
g=D_all(pieces=False)
sc,coll,asm=ws_scene("defence")
asm.hide_render=True
try:
    ws_shot("defence","catalog_final",(0,-88,30),(0,-36,1.0),lens=36,res=(1600,900),samples=64)
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0039] 2026-09-23 16:24:55  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","hero_town",(8-18,26-30,12),(8+4,26+3,5),lens=30,res=(1600,900),samples=64)
ws_shot("defence","hero_frontier",(-30+8,31-34,16),(-30,31+1,2.5),lens=30,res=(1600,900),samples=64)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0040] 2026-09-23 16:24:57  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
tx,ty=8,32; d=60; p=math.radians(50); yaw=0.15
ws_shot("defence","hero_colony",(tx+d*math.cos(p)*math.sin(yaw),ty-d*math.cos(p)*math.cos(yaw),d*math.sin(p)),(tx,ty,2),lens=35,res=(1600,900),samples=64)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0041] 2026-09-23 16:26:36  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
mine=[s[0] for s in g["WS_SPECS"]]
var=set()
for o in asm.objects:
    base=o.name.split("_inst")[0]
    if base in mine and o.data.name.startswith("VAR_"): var.add((base,o.data.name))
print(len(var)); print(sorted(var))
# ---- result ----
# {"result":"Code executed successfully: 6\n[('SM_VK_Def_Bartizan', 'VAR_1512350412963375573'), ('SM_VK_Palisade_Tower', 'VAR_6524895709637984545'), ('S
# M_VK_Parapet_Corner', 'VAR_6071355318410130569'), ('SM_VK_Parapet_Crenel', 'VAR_7414705513143094485'), ('SM_VK_Roof_Cone_R2', 'VAR_6070440536359195127
# '), ('SM_VK_Roof_Pyramid_6', 'VAR_8535510432928565502')]\n"}

# ==============================================================================================================
# [0042] 2026-09-23 16:26:53  blender  ok
# ==============================================================================================================
import bpy
pairs=[('SM_VK_Def_Bartizan', 'VAR_1512350412963375573'), ('SM_VK_Palisade_Tower', 'VAR_6524895709637984545'), ('SM_VK_Parapet_Corner', 'VAR_6071355318410130569'), ('SM_VK_Parapet_Crenel', 'VAR_7414705513143094485'), ('SM_VK_Roof_Cone_R2', 'VAR_6070440536359195127'), ('SM_VK_Roof_Pyramid_6', 'VAR_8535510432928565502')]
for p,v in pairs:
    a=bpy.data.objects[p].data; b=bpy.data.meshes[v]
    same=len(a.vertices)==len(b.vertices) and all((x.co-y.co).length<1e-5 for x,y in zip(a.vertices,b.vertices))
    print(p, len(a.vertices), len(b.vertices), "same" if same else "STALE", b.users)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Def_Bartizan 746 746 same 4\nSM_VK_Palisade_Tower 2708 2708 same 2\nSM_VK_Parapet_Corner 228 228 same 4\n
# SM_VK_Parapet_Crenel 514 514 same 8\nSM_VK_Roof_Cone_R2 274 274 same 2\nSM_VK_Roof_Pyramid_6 434 434 same 1\n"}

# ==============================================================================================================
# [0043] 2026-09-23 16:27:27  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
bt=bpy.data.texts["ws_defence"].as_string()
print(bt==src, len(src), hashlib.md5(src.encode()).hexdigest())
# ---- result ----
# {"result":"Code executed successfully: True 84981 b50b44cb2ce9ca44cfe69a9b94373362\n"}

# ==============================================================================================================
# [0044] 2026-09-23 16:27:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence")
objs=ws_build("defence", g=g)
st=ws_stats(objs)
print(len(objs),"pieces built, total tris",sum(s["tris"] for s in st))
for s in st: print(s["name"],s["tris"],s["bbox"],s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: 41 pieces built, total tris 71661\nSM_VK_Palisade_Straight 1338 [3.0, 0.5, 4.68] -0.8\nSM_VK_Palisade_Diag 1838
#  [4.27, 0.51, 4.7] -0.8\nSM_VK_Palisade_Post 654 [1.0, 1.0, 5.0] -0.8\nSM_VK_Palisade_Walk 816 [3.11, 1.1, 2.9] -0.6\nSM_VK_Palisade_Ladder 248 [0.64,
#  0.87, 2.91] -0.01\nSM_VK_Palisade_Gate 2372 [4.12, 0.94, 6.1] -0.9\nSM_VK_Palisade_GateLeaf 820 [1.51, 0.55, 3.35] 0.05\nSM_VK_Palisade_Tower 4842 [4
# .38, 4.38, 11.66] -0.9\nSM_VK_Prop_Beacon 2027 [2.7, 2.57, 7.65] -0.8\nSM_VK_TownWall_Straight 2308 [3.45, 2.82, 9.45] -1.5\nSM_VK_TownWall_Corner_Out
#  1304 [2.69, 2.68, 9.66] -1.5\nSM_VK_TownWall_Corner_In 1036 [1.68, 1.68, 7.75] -1.5\nSM_VK_TownWall_Stair 446 [3.07, 1.17, 6.43] -4.2\nSM_VK_TownWall
# _Step 2336 [3.45, 2.82, 10.57] -1.5\nSM_VK_TownWall_Ruin 2540 [3.53, 5.28, 6.99] -1.5\nSM_VK_TownWall_Tower_Round 9271 [7.16, 7.14, 13.97] -1.5\nSM_VK

# ==============================================================================================================
# [0045] 2026-09-23 16:28:11  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
ws_clear_assembly("defence")
jobs=[("build_palisade_demo",(-40,36,0),{}),("build_townwall_demo",(8,26,0),{}),("build_tower_house",(4,42,0),{}),
      ("build_training_yard",(-19,31,0),{}),("build_festival_green",(17,42,0),{}),("build_tower_house",(36,38,0),{"kind":"domestic","seed":3})]
for fn,org,kw in jobs:
    n0=len(asm.objects)
    try:
        g[fn](asm,org,**kw); print(fn,kw,"OK",len(asm.objects)-n0,"instances")
    except Exception:
        print(fn,"ERROR",traceback.format_exc()[-700:])
print("assembly total",len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: build_palisade_demo {} OK 42 instances\nbuild_townwall_demo {} OK 71 instances\nbuild_tower_house {} OK 71 inst
# ances\nbuild_training_yard {} OK 79 instances\nbuild_festival_green {} OK 33 instances\nbuild_tower_house {'kind': 'domestic', 'seed': 3} OK 71 instan
# ces\nassembly total 367\n"}
