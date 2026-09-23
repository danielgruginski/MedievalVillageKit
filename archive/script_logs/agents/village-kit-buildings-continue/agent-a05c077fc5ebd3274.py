# village-kit-buildings-continue / agent-a05c077fc5ebd3274.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:45:59  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_construction")
bt=t.as_string() if t else None
print(len(src), None if bt is None else len(bt), src==bt, (bt or "").rstrip()==src.rstrip())
if bt and bt!=src:
    import difflib
    d=list(difflib.unified_diff(bt.splitlines(), src.splitlines(), "blender","file", n=1, lineterm=""))
    print(len(d)); print("\n".join(d[:120]))
sc=bpy.data.scenes.get("WS_construction")
print(sc)
for cn in ("WS_construction_Pieces","WS_construction_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, None if c is None else len(c.objects))
# ---- result ----
# {"result":"Code executed successfully: 78752 74681 False False\n73\n--- blender\n+++ file\n@@ -1145,3 +1145,70 @@\n if c == \"W\" and rot == 0: P(\"SM
# _VK_Prop_FlowerBox\", x, y - 0.55, 0.78, rot, {})\n+ # site dressing (stock cell on the lot in front, left of the door path; tools by the door)\n+ E =
#  {}\n+ if stage < 3:\n+ P(\"SM_VK_Stockpile_Border\", -3.0, -7.0, 0, 0, {})\n+ pile = {0: \"SM_VK_Pile_Stone_3\", 1: \"SM_VK_Pile_Stone_2\", 2: \"SM_V
# K_Pile_Planks_2\"}[stage]\n+ P(pile, -3.0, -7.0, 0, 180 if r.random() < 0.5 else 0, {})\n+ P(\"SM_VK_Prop_Wheelbarrow\", 1.9, -6.6, 0, 150 + r.uniform
# (-15, 15), {})\n+ if stage == 0:\n+ P(\"SM_VK_Pile_Logs_1\", 7.4, -1.2, 0, 90, {})\n+ P(\"SM_VK_Prop_ChoppingBlock\", 6.9, 2.2, 0, r.uniform(0, 360), 
# {})\n+ elif stage == 1:\n+ P(\"SM_VK_Prop_MortarTub\", 2.6, -5.35, 0, 10, {})\n+ P(\"SM_VK_Prop_ShearLegs\", 6.6, 0.4, 0, 0, {})\n+ P(\"SM_VK_Pile_Sto

# ==============================================================================================================
# [0002] 2026-09-23 15:47:02  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["ws_common"].as_string()
print(len(s)); print(s[:6000])
# ---- result ----
# {"result":"Code executed successfully: 5974\n# ===================== WORKSHOP HELPERS (shared, read-only for agents) =====================\n# Usage in
#  any execute_blender_code call:\n# exec(bpy.data.texts[\"ws_common\"].as_string()); g=ws_ns(\"hovel\") # kit namespace + your module\nimport bpy, os, 
# math, json\nfrom mathutils import Vector\nWS_RENDERS=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a5
# 6c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\n\ndef ws_ns(agent=None):\n \"\"\"fresh namespace with the whole v
# illage kit (vk_helpers) + your module text 'ws_<agent>' executed on top\"\"\"\n g={}\n exec(bpy.data.texts[\"vk_helpers\"].as_string(),g)\n if agent:\
# n t=bpy.data.texts.get(\"ws_\"+agent)\n if t: exec(t.as_string(),g)\n return g\n\ndef _copy_props(dst,src):\n for p in src.bl_rna.properties:\n if p.i

# ==============================================================================================================
# [0003] 2026-09-23 15:47:51  blender  ok
# ==============================================================================================================
import bpy, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_construction") or bpy.data.texts.new("ws_construction"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time()
g=ws_ns("construction")
objs=ws_build("construction", g=g)
print(len(objs), round(time.time()-t0,2))
for s in ws_stats(objs): print(s["name"][6:], s["tris"], s["bbox"], s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: 42 2.32\nBuildSite_Cell 736 [3.0, 3.0, 0.99] -0.6\nFoundation_Wall 2092 [3.04, 1.87, 1.24] -0.6\nFoundation_Cor
# ner 484 [1.54, 1.54, 1.24] -0.6\nWall_Stone_Half 1264 [3.04, 1.38, 2.37] -0.6\nWall_Stone_Half_Door 2164 [3.12, 1.65, 3.39] -0.6\nCorner_Stone_Half 59
# 6 [1.92, 1.74, 2.4] -0.6\nWall_Plaster_Frame 1108 [3.13, 0.77, 3.6] -0.6\nWall_Plaster_Frame_Door 1452 [3.13, 1.43, 3.6] -0.6\nWall_Timber_Frame 784 [
# 3.13, 0.74, 3.01] -0.2\nRoof_Mid_Frame 1684 [3.0, 8.39, 4.44] -0.48\nRoof_Gable_Frame 3268 [4.11, 8.93, 4.8] -0.64\nRoof_Hip_Frame 2592 [4.31, 8.42, 4
# .5] -0.53\nScaffold_Wall 388 [3.24, 0.93, 3.0] 0.0\nScaffold_Corner 612 [1.76, 1.76, 3.0] 0.0\nScaffold_Ladder 178 [0.49, 0.8, 3.01] -0.0\nProp_Wheelb
# arrow 780 [2.2, 0.73, 0.84] -0.0\nProp_MortarTub 520 [1.85, 0.93, 0.97] -0.01\nProp_LadderLean 168 [0.5, 0.77, 2.79] -0.0\nProp_ShearLegs 580 [3.01, 2

# ==============================================================================================================
# [0004] 2026-09-23 15:48:17  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["WS_construction_Pieces"]
xs=[o.location[:] for o in c.objects]
print(min(x[0] for x in xs),max(x[0] for x in xs),min(x[1] for x in xs),max(x[1] for x in xs))
a=bpy.data.collections["WS_construction_Assembly"]
from collections import Counter
print(Counter(o.data.name for o in a.objects).most_common(50))
ys=[o.location[:] for o in a.objects]
print(min(x[0] for x in ys),max(x[0] for x in ys),min(x[1] for x in ys),max(x[1] for x in ys))
# ---- result ----
# {"result":"Code executed successfully: -22.0 14.0 -58.0 -24.0\n[('SM_VK_BuildSite_Cell', 18), ('SM_VK_Scaffold_Wall', 15), ('VAR_8601140401084027909',
#  10), ('VAR_3825705752519829956', 10), ('VAR_4923331775504545237', 10), ('VAR_2418275944548451817', 9), ('VAR_2252441350276304555', 8), ('VAR_29195895
# 33451061666', 8), ('VAR_7074798156193440906', 8), ('SM_VK_Scaffold_Corner', 6), ('VAR_8325031246302665942', 6), ('VAR_781895790422986741', 4), ('VAR_2
# 146452035886024102', 4), ('VAR_8720119066239477241', 2), ('VAR_565700177750185938', 2), ('VAR_4004551923032059068', 2), ('VAR_6633497470163219913', 2)
# , ('VAR_5972977137762862698', 2), ('VAR_1921926886111082264', 2), ('SM_VK_Prop_FlowerBox.002', 2), ('VAR_5993481685232179950', 1), ('VAR_5314725831350
# 939419', 1), ('VAR_541429699451183831', 1)]\n-28.5 28.5 -3.549999952316284 3.0\n"}

# ==============================================================================================================
# [0005] 2026-09-23 15:50:02  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
def tri(fn):
    k=g["Kit"](); fn(k)
    return sum(len(f.verts)-2 for f in k.bm.faces)
W=g
print("box bev", tri(lambda k: k.box((0,0,0),(1,1,1),W["WOOD"],bevel=0.02)))
print("box nobev", tri(lambda k: k.box((0,0,0),(1,1,1),W["WOOD"],bevel=0)))
print("wheel", tri(lambda k: W["con_wheel"](k,(0,0,0.5),0.5,0.08,6,tyre_n=10)))
print("cover", tri(lambda k: None))
print("barrel", tri(lambda k: W["barrel"](k,0,0,0,0.26,0.62)))
print("board", tri(lambda k: W["con_board"](k,(0,0,0),(3,0.16,0.05))))
print("rock1", tri(lambda k: W["rock"](k,(0,0,0),(1,1,1),seed=1,segs=1)))
print("rock2", tri(lambda k: W["rock"](k,(0,0,0),(1,1,1),seed=1,segs=2)))
print("ashlar", tri(lambda k: W["con_ashlar_block"](k,(0,0,0),(0.6,0.4,0.35))))
print("sack", tri(lambda k: W["con_sack"](k,(0,0,0))))
print("rafter", tri(lambda k: W["con_rafter"](k,0,1)))
print("gable truss", tri(lambda k: W["con_gable_truss"](k,1.9)))
print("barge", tri(lambda k: W["con_bargeboards"](k)))
print("bay", tri(lambda k: W["con_roof_frame_bay"](k,-1.5,W["GX"],W["CON_XS"])))
print("slope_x", tri(lambda k: W["con_slope_x"](k,-1.5,1.5,1,1.0,0.1,0.14,0.18,W["WOOD"],bevel=0.025)))
print("slope_x planks", tri(lambda k: W["con_slope_x"](k,-1.5,1.5,1,1.0,0.1,0.09,0.05,W["PLANKS"],bevel=0.0)))
# ---- result ----
# {"result":"Code executed successfully: box bev 44\nbox nobev 12\nwheel 260\ncover 0\nbarrel 176\nboard 12\nrock1 44\nrock2 108\nashlar 44\nsack 120\nr
# after 88\ngable truss 748\nbarge 616\nbay 1684\nslope_x 44\nslope_x planks 12\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:51:08  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
# drop stale variant meshes of MY pieces only (key includes my piece name), unused after clearing
mine=[n for n,_,_ in g["WS_SPECS"]]
styles=[("cloth",c) for c in ("Red","Blue","Green","Yellow","Purple","White")]
rm=0
for n in mine:
    for st in styles:
        key=(n,)+tuple(sorted([st]))
        me=bpy.data.meshes.get("VAR_"+str(abs(hash(key))))
        if me and me.users==0: bpy.data.meshes.remove(me); rm+=1
print("removed",rm)
import math
out=[]
for i,st in enumerate((0,1,2,3)):
    out.append(g["build_construction_site"](asm,(-24+16*i,0,0),st,seed=4))
out.append(g["build_camp"](asm,(-20,18,0),seed=1))
out.append(g["build_stockpile"](asm,(-4,18,0),w=3,d=2,seed=2))
out.append(g["build_sawpit_yard"](asm,(10,18,0),seed=3))
print(out, len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: removed 0\n[{'footprint': (3, 2), 'wall_top': 5.8}, {'footprint': (3, 2), 'wall_top': 5.8}, {'footprint': (3, 2
# ), 'wall_top': 5.8}, {'footprint': (3, 2), 'wall_top': 5.8}, {'footprint': (3, 3), 'beds': 6}, {'footprint': (3, 2), 'storage': 6}, {'footprint': (2, 
# 2), 'jobs': 2}] 185\n"}

# ==============================================================================================================
# [0007] 2026-09-23 15:51:33  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("construction","dev2_overview",(-6,-42,30),(-4,6,0),lens=30,res=(1600,900),samples=24)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\dev2_overview.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:52:32  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("construction","dev2_camp",(-20+9,18-14,10),(-20,18,0.5),lens=35,res=(1280,720),samples=24)
p=ws_shot("construction","dev2_yards",(3,18-17,14),(3,19,0),lens=32,res=(1280,720),samples=24)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\dev2_yards.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 15:54:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev2_st01",(-17,-19,11),(-15,-2,0.5),lens=30,res=(1280,720),samples=24)
ws_shot("construction","dev2_st2",(15,-17,9),(9,-1,2.5),lens=30,res=(1280,720),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0010] 2026-09-23 15:56:45  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts["ws_construction"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
objs=ws_build("construction", g=g, names=["SM_VK_Roof_Gable_Frame","SM_VK_Prop_Wagon_Covered","SM_VK_Pile_Sacks_1","SM_VK_Pile_Sacks_2","SM_VK_Pile_Sacks_3"])
for s in ws_stats(objs): print(s["name"][6:], s["tris"], s["bbox"])
sc,coll,asm=ws_scene("construction")
# remove camp instances only (objects near the camp origin), then rebuild the camp
for o in list(asm.objects):
    if abs(o.location.x+20)<7 and abs(o.location.y-18)<7: bpy.data.objects.remove(o)
g["build_camp"](asm,(-20,18,0),seed=1)
ws_shot("construction","dev2_camp_b",(-20+9,18-14,10),(-20,18,0.5),lens=35,res=(1280,720),samples=24)
# ---- result ----
# {"result":"Code executed successfully: Roof_Gable_Frame 2828 [4.11, 8.93, 4.8]\nPile_Sacks_1 628 [1.7, 1.6, 0.45]\nPile_Sacks_2 1188 [1.71, 1.69, 0.71
# ]\nPile_Sacks_3 1972 [1.72, 1.68, 0.96]\nProp_Wagon_Covered 1990 [5.16, 1.94, 1.8]\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:57:10  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
w=bpy.data.objects["SM_VK_Prop_Wagon_Covered"].location.copy()
r=bpy.data.objects["SM_VK_Roof_Gable_Frame"].location.copy()
print(w,r)
ws_shot("construction","dev2_wagon",(w.x+4.5,w.y-4.5,2.6),(w.x,w.y,0.8),lens=35,res=(960,540),samples=24)
ws_shot("construction","dev2_gableframe",(r.x+9,r.y-7,4),(r.x,r.y,2.2),lens=35,res=(960,540),samples=24)
# ---- result ----
# {"result":"Code executed successfully: <Vector (2.0000, -51.0000, 0.0000)> <Vector (-16.0000, -30.0000, 0.0000)>\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:58:09  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev2_st0_close",(-24+2,-9,4.5),(-24-0.5,0,0),lens=30,res=(1280,720),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0013] 2026-09-23 15:58:42  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
rows=[["BuildSite_Cell","Foundation_Wall","Foundation_Corner","Wall_Stone_Half","Wall_Stone_Half_Door","Corner_Stone_Half","Wall_Plaster_Frame","Wall_Plaster_Frame_Door","Wall_Timber_Frame"],
["Roof_Mid_Frame","Roof_Gable_Frame","Roof_Hip_Frame","Scaffold_Wall","Scaffold_Corner","Scaffold_Ladder","Prop_ShearLegs","Prop_LadderLean"],
["Pile_Logs_1","Pile_Logs_2","Pile_Logs_3","Pile_Planks_1","Pile_Planks_2","Pile_Planks_3","Pile_Stone_1","Pile_Stone_2","Pile_Stone_3"],
["Pile_Sacks_1","Pile_Sacks_2","Pile_Sacks_3","Stockpile_Border","Prop_Wheelbarrow","Prop_MortarTub","Prop_ChoppingBlock","Prop_Sawhorse"],
["Tent_A","Tent_Bell","Prop_Campfire","Prop_Bedroll","Prop_Wagon_Covered","Prop_SawPit","Prop_Privy","Prop_WaysideShrine"]]
def bb(o):
    cs=[Vector(c) for c in o.bound_box]
    return min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs)
y=-30.0; allx=[]
for row in rows:
    obs=[bpy.data.objects["SM_VK_"+n] for n in row]
    bbs=[bb(o) for o in obs]
    wid=sum(b[1]-b[0] for b in bbs)+1.2*(len(obs)-1)
    x=-wid/2; ymax=max(b[3] for b in bbs); ymin=min(b[2] for b in bbs)
    for o,b in zip(obs,bbs):
        o.location=(x-b[0], y-ymax, 0); x+= (b[1]-b[0])+1.2
    allx.append(wid)
    print(round(wid,1), round(y,1), round(y-ymax+ymin,1))
    y=y-(ymax-ymin)-1.6
print("done", y)
# ---- result ----
# {"result":"Code executed successfully: 34.7 -30.0 -33.0\n28.8 -34.6 -43.5\n35.2 -45.1 -47.1\n23.8 -48.7 -51.6\n30.4 -53.2 -58.6\ndone -60.219297945499
# 43\n"}

# ==============================================================================================================
# [0014] 2026-09-23 15:59:14  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev2_catalog",(0,-80,30),(0,-45.5,0),lens=38,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 15:59:54  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
rows=[["Roof_Mid_Frame","Roof_Gable_Frame","Roof_Hip_Frame","Scaffold_Wall","Scaffold_Corner","Scaffold_Ladder","Prop_ShearLegs","Prop_LadderLean"],
["BuildSite_Cell","Foundation_Wall","Foundation_Corner","Wall_Stone_Half","Wall_Stone_Half_Door","Corner_Stone_Half","Wall_Plaster_Frame","Wall_Plaster_Frame_Door","Wall_Timber_Frame"],
["Pile_Logs_1","Pile_Logs_2","Pile_Logs_3","Pile_Planks_1","Pile_Planks_2","Pile_Planks_3","Pile_Stone_1","Pile_Stone_2","Pile_Stone_3"],
["Pile_Sacks_1","Pile_Sacks_2","Pile_Sacks_3","Stockpile_Border","Prop_Wheelbarrow","Prop_MortarTub","Prop_ChoppingBlock","Prop_Sawhorse"],
["Tent_A","Tent_Bell","Prop_Campfire","Prop_Bedroll","Prop_Wagon_Covered","Prop_SawPit","Prop_Privy","Prop_WaysideShrine"]]
def bb(o):
    cs=[Vector(c) for c in o.bound_box]
    return min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs)
y=-30.0
for ri,row in enumerate(rows):
    obs=[bpy.data.objects["SM_VK_"+n] for n in row]
    bbs=[bb(o) for o in obs]
    gap=1.3
    wid=sum(b[1]-b[0] for b in bbs)+gap*(len(obs)-1)
    x=-wid/2; ymax=max(b[3] for b in bbs); ymin=min(b[2] for b in bbs)
    for o,b in zip(obs,bbs):
        o.location=(x-b[0], y-ymax, 0); x+= (b[1]-b[0])+gap
    print(round(wid,1), round(y,1), round(y-ymax+ymin,1))
    y=y-(ymax-ymin)-(3.0 if ri<2 else 2.0)
ws_shot("construction","dev2_catalog",(0,-84,31),(0,-46.5,0),lens=37,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: 29.5 -30.0 -38.9\n35.5 -41.9 -44.9\n36.0 -47.9 -49.9\n24.5 -51.9 -54.8\n31.1 -56.8 -62.2\n"}

# ==============================================================================================================
# [0016] 2026-09-23 16:00:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for o in bpy.data.collections["WS_construction_Pieces"].objects: o.location.y+=17.5
ws_shot("construction","dev2_catalog",(0,-64,27),(0,-29.5,0),lens=36,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0017] 2026-09-23 16:03:44  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts["ws_construction"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
objs=ws_build("construction", g=g, names=["SM_VK_Scaffold_Wall","SM_VK_Scaffold_Corner","SM_VK_Scaffold_Ladder"])
for s in ws_stats(objs): print(s["name"][6:], s["tris"], s["bbox"])
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
mine=[n for n,_,_ in g["WS_SPECS"]]
for n in mine:
    for c in ("Red","Blue","Green","Yellow","Purple","White"):
        me=bpy.data.meshes.get("VAR_"+str(abs(hash((n,("cloth",c))))))
        if me and me.users==0: bpy.data.meshes.remove(me)
B=g["build_construction_site"]
for i,st in enumerate((0,1,2,3)): B(asm,(-24+16*i,0,0),st,seed=4)
B(asm,(-16,36,0),1,seed=7,style={"ground":"Plaster","ends":("hip","gable"),"plaster":"Ochre","shutter":"Green","roof":"Red"})
B(asm,(0,36,0),2,seed=7,style={"ground":"Plaster","ends":("hip","gable"),"plaster":"Ochre","shutter":"Green","roof":"Red"})
B(asm,(16,36,0),2,seed=8,style={"ground":"Stone","ends":("hip","hip"),"roof":"Slate"})
B(asm,(32,36,0),3,seed=7,style={"ground":"Plaster","ends":("hip","gable"),"plaster":"Ochre","shutter":"Green","roof":"Red"})
g["build_camp"](asm,(-20,18,0),seed=1)
g["build_stockpile"](asm,(-4,18,0),w=3,d=2,seed=2)
g["build_sawpit_yard"](asm,(10,18,0),seed=3)
print(len(asm.objects), round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: Scaffold_Wall 388 [3.24, 0.91, 3.0]\nScaffold_Corner 612 [1.83, 1.8, 3.0]\nScaffold_Ladder 178 [0.49, 0.76, 3.0
# 1]\n372 1.7\n"}

# ==============================================================================================================
# [0018] 2026-09-23 16:04:43  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev3_rowC",(8,6,20),(8,37,1.5),lens=30,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0019] 2026-09-23 16:07:50  blender  ok
# ==============================================================================================================
REBUILD=["SM_VK_Scaffold_Wall","SM_VK_Scaffold_Corner","SM_VK_Scaffold_Wall_Top","SM_VK_Scaffold_Corner_Top"]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
ws_shot("construction","dev3_rowC_b",(10,23,9),(9,35,4.5),lens=30,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: Scaffold_Wall 388 [3.24, 0.91, 3.0] 0.0\nScaffold_Corner 612 [1.83, 1.8, 3.0] 0.0\nScaffold_Wall_Top 388 [3.24,
#  0.91, 2.3] 0.0\nScaffold_Corner_Top 612 [1.83, 1.8, 2.3] 0.0\nassembly 372 2.9 s\n"}

# ==============================================================================================================
# [0020] 2026-09-23 16:08:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev3_plaster1",(-9,24,8),(-16,36,1.5),lens=30,res=(1280,720),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0021] 2026-09-23 16:08:53  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
rows=[["Roof_Mid_Frame","Roof_Gable_Frame","Roof_Hip_Frame","Scaffold_Wall","Scaffold_Corner","Scaffold_Wall_Top","Scaffold_Corner_Top","Scaffold_Ladder","Prop_ShearLegs","Prop_LadderLean"],
["BuildSite_Cell","Foundation_Wall","Foundation_Corner","Wall_Stone_Half","Wall_Stone_Half_Door","Corner_Stone_Half","Wall_Plaster_Frame","Wall_Plaster_Frame_Door","Wall_Timber_Frame"],
["Pile_Logs_1","Pile_Logs_2","Pile_Logs_3","Pile_Planks_1","Pile_Planks_2","Pile_Planks_3","Pile_Stone_1","Pile_Stone_2","Pile_Stone_3"],
["Pile_Sacks_1","Pile_Sacks_2","Pile_Sacks_3","Stockpile_Border","Prop_Wheelbarrow","Prop_MortarTub","Prop_ChoppingBlock","Prop_Sawhorse"],
["Tent_A","Tent_Bell","Prop_Campfire","Prop_Bedroll","Prop_Wagon_Covered","Prop_SawPit","Prop_Privy","Prop_WaysideShrine"]]
def bb(o):
    cs=[Vector(c) for c in o.bound_box]
    return min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs)
y=-12.5
for ri,row in enumerate(rows):
    obs=[bpy.data.objects["SM_VK_"+n] for n in row]
    bbs=[bb(o) for o in obs]
    gap=1.3
    wid=sum(b[1]-b[0] for b in bbs)+gap*(len(obs)-1)
    x=-wid/2; ymax=max(b[3] for b in bbs); ymin=min(b[2] for b in bbs)
    for o,b in zip(obs,bbs):
        o.location=(x-b[0], y-ymax, 0); x+= (b[1]-b[0])+gap
    print(round(wid,1), round(y,1), round(y-ymax+ymin,1))
    y=y-(ymax-ymin)-(3.0 if ri<2 else 2.0)
sc,coll,asm=ws_scene("construction")
print(len(coll.objects))
asm.hide_render=True
try:
    ws_shot("construction","dev3_catalog",(0,-64,27),(0,-29.5,0),lens=34,res=(1600,900),samples=24)
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: 37.3 -12.5 -21.4\n35.5 -24.4 -27.4\n36.0 -30.4 -32.4\n24.5 -34.4 -37.3\n31.1 -39.3 -44.7\n44\n"}

# ==============================================================================================================
# [0022] 2026-09-23 16:09:29  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
# colony camera: 50 deg pitch, ~42 m from the target
tx,ty=2.0,14.0; d=44.0; p=math.radians(50)
ws_shot("construction","dev3_colony",(tx,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=30,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0023] 2026-09-23 16:10:43  blender  ok
# ==============================================================================================================
import math
REBUILD=[]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
tx,ty=-2.0,7.0; d=46.0; p=math.radians(50)
ws_shot("construction","dev3_colony",(tx,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=32,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: assembly 372 2.7 s\n"}

# ==============================================================================================================
# [0024] 2026-09-23 16:11:49  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
asm.hide_render=True
try:
    ws_shot("construction","dev3_row2",(0,-37,7),(0,-25.5,1.2),lens=30,res=(1600,900),samples=24)
    ws_shot("construction","dev3_row4",(-2,-43.5,4.5),(-2,-35.8,0.4),lens=30,res=(1600,900),samples=24)
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0025] 2026-09-23 16:13:17  blender  ok
# ==============================================================================================================
import math
REBUILD=[]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
ws_shot("construction","dev3_camp",(-11,-1,11),(-19,13,0.8),lens=32,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: assembly 374 2.8 s\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:14:38  blender  ok
# ==============================================================================================================
import math
REBUILD=[]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
ws_shot("construction","dev3_camp_b",(-12,-2,10),(-19.5,13,0.8),lens=30,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: assembly 374 2.6 s\n"}

# ==============================================================================================================
# [0027] 2026-09-23 16:15:27  blender  ok
# ==============================================================================================================
import math
REBUILD=[]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
ws_shot("construction","dev3_camp_c",(-12,-2,10),(-19.5,13,0.8),lens=30,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: assembly 374 3.4 s\n"}

# ==============================================================================================================
# [0028] 2026-09-23 16:16:19  blender  ERROR
# ==============================================================================================================
import bpy, itertools
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
mine=[n for n,_,_ in g["WS_SPECS"]]
PL=["Cream","White","Ochre","Rose","Daub","Sage","Sky"]; SH=["Teal","Red","Green","Blue","Natural"]; RF=["Red","Blue","Green","Thatch","Slate","Shingle"]
rm=0
for n in mine:
    for p_,s_,r_ in itertools.product(PL,SH,RF):
        me=bpy.data.meshes.get("VAR_"+str(abs(hash((n,("plaster",p_),("roof",r_),("shutter",s_)))))))
        if me and me.users==0: bpy.data.meshes.remove(me); rm+=1
print("removed stale variants of my pieces:",rm)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: unmatched ')' (<string>, line 11)"}

# ==============================================================================================================
# [0029] 2026-09-23 16:16:49  blender  ok
# ==============================================================================================================
import bpy, itertools
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
mine=[n for n,_,_ in g["WS_SPECS"]]
PL=["Cream","White","Ochre","Rose","Daub","Sage","Sky"]; SH=["Teal","Red","Green","Blue","Natural"]; RF=["Red","Blue","Green","Thatch","Slate","Shingle"]
rm=0
for n in mine:
    for p_,s_,r_ in itertools.product(PL,SH,RF):
        key=(n,("plaster",p_),("roof",r_),("shutter",s_))
        me=bpy.data.meshes.get("VAR_"+str(abs(hash(key))))
        if me and me.users==0:
            bpy.data.meshes.remove(me); rm+=1
print("removed stale variants of my pieces:",rm)
# ---- result ----
# {"result":"Code executed successfully: removed stale variants of my pieces: 25\n"}

# ==============================================================================================================
# [0030] 2026-09-23 16:17:07  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts["ws_construction"]; t.clear(); t.write(src)
g=ws_ns("construction")
objs=ws_build("construction", g=g)
print(len(objs), "pieces built", round(time.time()-t0,2), "s", t.as_string()==src)
for s in ws_stats(objs): print(s["name"], s["tris"], s["bbox"], s["zmin"], s["mats"])
# ---- result ----
# {"result":"Code executed successfully: 44 pieces built 2.46 s True\nSM_VK_BuildSite_Cell 736 [3.0, 3.0, 0.99] -0.6 [2, 11, 26, 28]\nSM_VK_Foundation_W
# all 2092 [3.04, 1.87, 1.24] -0.6 [0, 2, 17, 26, 45]\nSM_VK_Foundation_Corner 484 [1.54, 1.54, 1.24] -0.6 [0, 2, 17, 26, 45]\nSM_VK_Wall_Stone_Half 126
# 4 [3.04, 1.38, 2.37] -0.6 [0, 1, 2, 21, 24, 45]\nSM_VK_Wall_Stone_Half_Door 2164 [3.12, 1.65, 3.39] -0.6 [0, 1, 2, 21, 24, 45]\nSM_VK_Corner_Stone_Hal
# f 596 [1.92, 1.74, 2.4] -0.6 [0, 45]\nSM_VK_Wall_Plaster_Frame 1108 [3.13, 0.77, 3.6] -0.6 [0, 2, 45, 47]\nSM_VK_Wall_Plaster_Frame_Door 1452 [3.13, 1
# .43, 3.6] -0.6 [0, 2, 45]\nSM_VK_Wall_Timber_Frame 784 [3.13, 0.74, 3.01] -0.2 [2]\nSM_VK_Roof_Mid_Frame 1684 [3.0, 8.39, 4.44] -0.48 [2, 23]\nSM_VK_R
# oof_Gable_Frame 2828 [4.11, 8.93, 4.8] -0.64 [2, 23]\nSM_VK_Roof_Hip_Frame 2592 [4.31, 8.42, 4.5] -0.53 [2, 23]\nSM_VK_Scaffold_Wall 388 [3.24, 0.91, 

# ==============================================================================================================
# [0031] 2026-09-23 16:17:35  blender  ok
# ==============================================================================================================
REBUILD=[]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
ws_shot("construction","dev4_stages34",(-30,-26,15),(-4,1,2.0),lens=30,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: assembly 374 0.3 s\n"}

# ==============================================================================================================
# [0032] 2026-09-23 16:17:56  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_stages",(-40,-21,13),(-3,1.5,2.2),lens=34,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0033] 2026-09-23 16:18:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_stages",(-27,-33,15),(-1,2,1.5),lens=33,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0034] 2026-09-23 16:19:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_stages",(-17,-38,15),(-2,0,1.5),lens=31,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0035] 2026-09-23 16:20:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_stages",(-15,-31,13),(-1,6,0.5),lens=31,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0036] 2026-09-23 16:21:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_stages_b",(-50,-31,16),(-2,1,1.0),lens=38,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0037] 2026-09-23 16:21:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_stages_b",(-50,-29,15),(-8,6,1.0),lens=38,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0038] 2026-09-23 16:22:06  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    tx,ty=-4.0,7.0; d=46.0; p=math.radians(50)
    print(ws_shot("construction","hero_colony",(tx-8,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=30,res=(1600,900),samples=48))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\hero_colony.png\n"}

# ==============================================================================================================
# [0039] 2026-09-23 16:22:34  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    tx,ty=0.0,8.0; d=52.0; p=math.radians(50)
    print(ws_shot("construction","hero_colony",(tx,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=30,res=(1600,900),samples=48))
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\hero_colony.png\n"}

# ==============================================================================================================
# [0040] 2026-09-23 16:23:01  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_yards",(-36,-3,12),(-7,14,0.3),lens=34,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0041] 2026-09-23 16:23:44  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_yards",(-44,-14,18),(-5,13,0.3),lens=40,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0042] 2026-09-23 16:24:06  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_camp",(-33,0,9.5),(-13,14.5,0.3),lens=36,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0043] 2026-09-23 16:25:03  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_hero_camp",(-13,-8,14),(-12,13,0.3),lens=32,res=(1600,900),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0044] 2026-09-23 16:25:59  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    ws_shot("construction","dev4_sawpit",(15,4,6.5),(9.5,13.5,0.5),lens=30,res=(1280,720),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0045] 2026-09-23 16:26:52  blender  ok
# ==============================================================================================================
REBUILD=["SM_VK_Prop_Sawhorse"]
exec(open(r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\con_asm.py",encoding="utf8").read())
coll.hide_render=True
try:
    ws_shot("construction","dev4_sawpit",(15,4,6.5),(9.5,13.5,0.5),lens=30,res=(1280,720),samples=24)
finally:
    coll.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: Prop_Sawhorse 696 [1.71, 0.83, 1.22] -0.04\nassembly 374 2.7 s\n"}

# ==============================================================================================================
# [0046] 2026-09-23 16:27:20  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time()
g=ws_ns("construction")
objs=ws_build("construction", g=g)
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
print(len(objs), "pieces, no error,", round(time.time()-t0,2), "s; file==text:", bpy.data.texts["ws_construction"].as_string()==src, len(g["WS_SPECS"]))
# ---- result ----
# {"result":"Code executed successfully: 44 pieces, no error, 2.52 s; file==text: True 44\n"}

# ==============================================================================================================
# [0047] 2026-09-23 16:27:44  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
for n in [n for n,_,_ in g["WS_SPECS"]]:
    for c in ("Red","Blue","Green","Yellow","Purple","White"):
        me=bpy.data.meshes.get("VAR_"+str(abs(hash((n,("cloth",c))))))
        if me and me.users==0: bpy.data.meshes.remove(me)
res=[]
B=g["build_construction_site"]
for i,st in enumerate((0,1,2,3)): res.append(("site",st,B(asm,(-24+16*i,0,0),st,seed=4)))
PL={"ground":"Plaster","ends":("hip","gable"),"plaster":"Ochre","shutter":"Green","roof":"Red"}
res.append(("site_pl",1,B(asm,(-16,30,0),1,seed=7,style=PL)))
res.append(("site_pl",2,B(asm,(0,30,0),2,seed=7,style=PL)))
res.append(("site_hip",2,B(asm,(16,30,0),2,seed=8,style={"ground":"Stone","ends":("hip","hip"),"roof":"Slate"})))
res.append(("site_pl",3,B(asm,(32,30,0),3,seed=7,style=PL)))
res.append(("camp",g["build_camp"](asm,(-20,13,0),seed=1)))
res.append(("stock",g["build_stockpile"](asm,(-4,13,0),w=3,d=2,seed=2)))
res.append(("sawpit",g["build_sawpit_yard"](asm,(10,13,0),seed=3)))
for r_ in res: print(r_)
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: ('site', 0, {'footprint': (3, 2), 'lot': (4, 3), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('gable', 'gable')
# })\n('site', 1, {'footprint': (3, 2), 'lot': (4, 3), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('gable', 'gable')})\n('site', 2, {'footprint': (3, 2
# ), 'lot': (4, 3), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('gable', 'gable')})\n('site', 3, {'footprint': (3, 2), 'lot': (4, 3), 'wall_top': 5.8, 
# 'ground': 'Stone', 'ends': ('gable', 'gable')})\n('site_pl', 1, {'footprint': (3, 2), 'lot': (4, 3), 'wall_top': 5.8, 'ground': 'Plaster', 'ends': ('h
# ip', 'gable')})\n('site_pl', 2, {'footprint': (3, 2), 'lot': (4, 3), 'wall_top': 5.8, 'ground': 'Plaster', 'ends': ('hip', 'gable')})\n('site_hip', 2,
#  {'footprint': (3, 2), 'lot': (4, 3), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('hip', 'hip')})\n('site_pl', 3, {'footprint': (3, 2), 'lot': (4, 3)

# ==============================================================================================================
# [0048] 2026-09-23 16:28:19  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts["ws_construction"]; t.clear(); t.write(src)
print(t.as_string()==src)
# ---- result ----
# {"result":"Code executed successfully: True\n"}

# ==============================================================================================================
# [0049] 2026-09-23 16:28:21  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time()
g=ws_ns("construction")
objs=ws_build("construction", g=g)
print(len(objs), "pieces built without error in", round(time.time()-t0,2), "s")
for s in ws_stats(objs): print(s["name"][6:], s["tris"], s["bbox"], s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: 44 pieces built without error in 2.49 s\nBuildSite_Cell 736 [3.0, 3.0, 0.99] -0.6\nFoundation_Wall 2092 [3.04, 
# 1.87, 1.24] -0.6\nFoundation_Corner 484 [1.54, 1.54, 1.24] -0.6\nWall_Stone_Half 1264 [3.04, 1.38, 2.37] -0.6\nWall_Stone_Half_Door 2164 [3.12, 1.65, 
# 3.39] -0.6\nCorner_Stone_Half 596 [1.92, 1.74, 2.4] -0.6\nWall_Plaster_Frame 1108 [3.13, 0.77, 3.6] -0.6\nWall_Plaster_Frame_Door 1452 [3.13, 1.43, 3.
# 6] -0.6\nWall_Timber_Frame 784 [3.13, 0.74, 3.01] -0.2\nRoof_Mid_Frame 1684 [3.0, 8.39, 4.44] -0.48\nRoof_Gable_Frame 2828 [4.11, 8.93, 4.8] -0.64\nRo
# of_Hip_Frame 2592 [4.31, 8.42, 4.5] -0.53\nScaffold_Wall 388 [3.24, 0.91, 3.0] 0.0\nScaffold_Corner 612 [1.83, 1.8, 3.0] 0.0\nScaffold_Wall_Top 388 [3
# .24, 0.91, 2.3] 0.0\nScaffold_Corner_Top 612 [1.83, 1.8, 2.3] 0.0\nScaffold_Ladder 178 [0.49, 0.76, 3.01] -0.0\nProp_Wheelbarrow 780 [2.2, 0.73, 0.84]

# ==============================================================================================================
# [0050] 2026-09-23 16:28:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
for n in [n for n,_,_ in g["WS_SPECS"]]:
    for c in ("Red","Blue","Green","Yellow","Purple","White"):
        me=bpy.data.meshes.get("VAR_"+str(abs(hash((n,("cloth",c))))))
        if me and me.users==0: bpy.data.meshes.remove(me)
B=g["build_construction_site"]
for i,st in enumerate((0,1,2,3)): print(B(asm,(-24+16*i,0,0),st,seed=4))
PL={"ground":"Plaster","ends":("hip","gable"),"plaster":"Ochre","shutter":"Green","roof":"Red"}
print(B(asm,(-16,30,0),1,seed=7,style=PL)); print(B(asm,(0,30,0),2,seed=7,style=PL))
print(B(asm,(16,30,0),2,seed=8,style={"ground":"Stone","ends":("hip","hip"),"roof":"Slate"})); print(B(asm,(32,30,0),3,seed=7,style=PL))
print(g["build_camp"](asm,(-20,13,0),seed=1))
print(g["build_stockpile"](asm,(-4,13,0),w=3,d=2,seed=2))
print(g["build_sawpit_yard"](asm,(10,13,0),seed=3))
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: {'footprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('gable', 'gable')}\n{'footpri
# nt': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('gable', 'gable')}\n{'footprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'gr
# ound': 'Stone', 'ends': ('gable', 'gable')}\n{'footprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('gable', 'gable')}\n{'f
# ootprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'ground': 'Plaster', 'ends': ('hip', 'gable')}\n{'footprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.
# 8, 'ground': 'Plaster', 'ends': ('hip', 'gable')}\n{'footprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'ground': 'Stone', 'ends': ('hip', 'hip')}\n{
# 'footprint': (3, 2), 'lot': (5, 4), 'wall_top': 5.8, 'ground': 'Plaster', 'ends': ('hip', 'gable')}\n{'footprint': (3, 3), 'beds': 6}\n{'footprint': (

# ==============================================================================================================
# [0051] 2026-09-23 16:29:08  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
asm.hide_render=True
try:
    print(ws_shot("construction","catalog_final",(0,-64,27),(0,-29.5,0),lens=34,res=(1600,900),samples=48))
finally:
    asm.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\catalog_final.png\n"}

# ==============================================================================================================
# [0052] 2026-09-23 16:29:26  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
out=[]
try:
    out.append(ws_shot("construction","hero_stages",(-50,-29,15),(-8,6,1.0),lens=38,res=(1600,900),samples=48))
    out.append(ws_shot("construction","hero_camp",(-12,-2,10),(-19.5,13,0.8),lens=30,res=(1600,900),samples=48))
finally:
    coll.hide_render=False
print(out)
# ---- result ----
# {"result":"Code executed successfully: ['C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56
# c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\renders2\\\\construction\\\\hero_stages.png', 'C:\\\\Users\\\\danie\\\\A
# ppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-2
# 3-d49817\\\\renders2\\\\construction\\\\hero_camp.png']\n"}

# ==============================================================================================================
# [0053] 2026-09-23 16:29:49  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
coll.hide_render=True
try:
    tx,ty=0.0,8.0; d=52.0; p=math.radians(50)
    print(ws_shot("construction","hero_colony",(tx,ty-d*math.cos(p),d*math.sin(p)),(tx,ty,0),lens=30,res=(1600,900),samples=48))
finally:
    coll.hide_render=False
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
print("file==text", bpy.data.texts["ws_construction"].as_string()==src, "pieces", len(coll.objects), "asm", len(asm.objects), coll.hide_render, asm.hide_render)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\hero_colony.png\nfile==text True pieces 44 asm 374 False False\n"}
