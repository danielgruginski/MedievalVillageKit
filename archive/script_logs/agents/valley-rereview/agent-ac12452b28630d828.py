# valley-rereview / agent-ac12452b28630d828.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 18:47:37  blender  ok
# ==============================================================================================================
import bpy
c=bpy.data.collections.get("VK_ValleyTown")
print(len(c.all_objects))
print([t.name for t in bpy.data.texts])
import collections
cnt=collections.Counter(o.name.split("_inst")[0] for o in c.all_objects)
print(len(cnt))
print(bpy.context.scene.name, [s.name for s in bpy.data.scenes])
# ---- result ----
# {"result":"Code executed successfully: 4584\n['mc_helpers', 'README_VillageKit', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_kit', 'vk_leafgen', 
# 'vk_mat', 'vk_mod_construction', 'vk_mod_defence', 'vk_mod_frontier', 'vk_mod_humble', 'vk_mod_industry', 'vk_mod_skyline', 'vk_mod_town', 'vk_mod_wat
# er', 'vk_nature', 'vk_render', 'vk_terrain', 'vk_terrain_demo', 'vk_tex', 'vk_tex2', 'vk_texgen', 'vk_town_map', 'wk_helpers', 'ws_common']\n338\nVill
# ageKit ['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n"}

# ==============================================================================================================
# [0002] 2026-09-23 18:48:15  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_town_map"].as_string()
print(len(t.splitlines()), "POSTERN_J" in t, "town_door_clear" in t)
ns=bpy.app.driver_namespace
print([k for k in ns.keys()][:50])
# ---- result ----
# {"result":"Code executed successfully: 604 True True\n['__builtins__', '__name__', '__doc__', '__package__', '__loader__', '__spec__', 'acos', 'acosh'
# , 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'cbrt', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'dist', 'erf', 'erfc', 'exp', 'exp2', 'expm1', 'fab
# s', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'gcd', 'hypot', 'isclose', 'isfinite', 'isinf', 'isnan', 'isqrt', 'lcm', 'ldexp', 'lgamma'
# , 'log', 'log1p', 'log10', 'log2', 'modf', 'pow', 'radians', 'remainder']\n"}

# ==============================================================================================================
# [0003] 2026-09-23 18:49:01  blender  ok
# ==============================================================================================================
import bpy
c=bpy.data.collections.get("VK_ValleyTown")
objs=list(c.all_objects)
o=objs[0]
print(o.name, o.keys(), o.parent, [ch.name for ch in c.children][:20])
import collections
print(collections.Counter(o.type for o in objs))
print(sum(1 for o in objs if o.parent))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Straight_inst <IDPropertyGroupViewKeys> None []\nCounter({'MESH': 4584})\n0\n"}

# ==============================================================================================================
# [0004] 2026-09-23 18:49:16  blender  ok
# ==============================================================================================================
import bpy, json, numpy as np
from mathutils import Vector
c=bpy.data.collections.get("VK_ValleyTown")
out=[]
for o in c.all_objects:
    M=o.matrix_world
    pts=[M@Vector(v) for v in o.bound_box]
    xs=[p.x for p in pts]; ys=[p.y for p in pts]; zs=[p.z for p in pts]
    out.append([o.name,o.data.name,round(o.location.x,3),round(o.location.y,3),round(o.location.z,3),round(o.rotation_euler.z*57.29578,1),round(o.scale.x,3),round(min(xs),3),round(max(xs),3),round(min(ys),3),round(max(ys),3),round(min(zs),3),round(max(zs),3)])
p=r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\objs.json"
import os; os.makedirs(os.path.dirname(p),exist_ok=True)
json.dump(out,open(p,"w"))
print(len(out))
# ---- result ----
# {"result":"Code executed successfully: 4584\n"}

# ==============================================================================================================
# [0005] 2026-09-23 18:50:05  blender  ok
# ==============================================================================================================
import bpy
print(bpy.data.texts["vk_render"].as_string()[:3000])
# ---- result ----
# {"result":"Code executed successfully: import bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,len
# s=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is 
# None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.
# link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_e
# nd=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.render.

# ==============================================================================================================
# [0006] 2026-09-23 18:57:27  blender  ok
# ==============================================================================================================
import bpy, json
from mathutils import Vector
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[o for o in tc.all_objects if o.type=="MESH" and "Chunk" in o.name]
print(len(chunks), [o.name for o in tc.all_objects][:5])
info=[]
for c in chunks:
    pts=[c.matrix_world@Vector(v) for v in c.bound_box]
    info.append((c,min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)))
print([(i[0].name,round(i[1]),round(i[2]),round(i[3]),round(i[4])) for i in info][:6])
# ---- result ----
# {"result":"Code executed successfully: 20 ['VKV_Chunk_0_0', 'VKV_Water_0_0', 'VKV_Chunk_1_0', 'VKV_Water_1_0', 'VKV_Chunk_2_0']\n[('VKV_Chunk_0_0', 14
# 98, 1547, -2, 47), ('VKV_Chunk_1_0', 1546, 1595, -2, 47), ('VKV_Chunk_2_0', 1594, 1643, -2, 47), ('VKV_Chunk_3_0', 1642, 1691, -2, 47), ('VKV_Chunk_4_
# 0', 1690, 1718, -2, 47), ('VKV_Chunk_0_1', 1498, 1547, 46, 95)]\n"}

# ==============================================================================================================
# [0007] 2026-09-23 18:58:11  blender  ok
# ==============================================================================================================
import bpy, json, re
from mathutils import Vector
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[]
for c in tc.all_objects:
    if c.type=="MESH" and "Chunk" in c.name:
        pts=[c.matrix_world@Vector(v) for v in c.bound_box]
        chunks.append((c,c.matrix_world.inverted(),min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)))
def ground(x,y):
    best=None
    for c,mi,x0,x1,y0,y1 in chunks:
        if x0-0.01<=x<=x1+0.01 and y0-0.01<=y<=y1+0.01:
            o=mi@Vector((x,y,60.0)); dvec=(mi.to_3x3()@Vector((0,0,-1))).normalized()
            hit,loc,nor,idx=c.ray_cast(o,dvec)
            if hit:
                z=(c.matrix_world@loc).z
                if best is None or z>best: best=z
    return best
c=bpy.data.collections["VK_ValleyTown"]
skip=("Sign","Lantern","Festoon","Banner","Bunting","Wreath","Shelf","FlowerBox","Window","Chimney","Roof","Up","Timber","Turret","Parapet","Bartizan","Emblem","Ivy","Barge","Rowboat","Bridge","Pier","Quay","WaterWheel","Wheel","Sails","Ceiling","Gallery","Crane","LipGrass","Weeds","Tree_","Bush","Plant","Rock","Mushroom","Scaffold","Cap","Corbel","Seg","Dormer","Vent","Beacon","HoistBeam","Cone","Bellcote","Pent","Stair_Stone_Ext","ShopGoods","Planter","Awning")
res=[]
for o in c.all_objects:
    n=o.name
    if any(s in n for s in skip): continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    x0=min(p.x for p in pts);x1=max(p.x for p in pts);y0=min(p.y for p in pts);y1=max(p.y for p in pts);z0=min(p.z for p in pts)
    samples=[(o.location.x,o.location.y)]+[(x0+0.2,y0+0.2),(x1-0.2,y0+0.2),(x0+0.2,y1-0.2),(x1-0.2,y1-0.2)]
    gs=[ground(x,y) for (x,y) in samples]
    if gs[0] is None: continue
    gz=[g for g in gs if g is not None]
    res.append((n,round(o.location.x,2),round(o.location.y,2),round(o.location.z,2),round(z0,2),[round(g,2) if g is not None else None for g in gs]))
p=r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\ground.json"
json.dump(res,open(p,"w")); print(len(res))
# ---- result ----
# {"result":"Code executed successfully: 1093\n"}

# ==============================================================================================================
# [0008] 2026-09-23 18:59:44  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
t=time.time()
p=shot("b01_town_overview",(1628,40,95),(1628,106,3),lens=28,res=(1600,900),outdir=OUT)
print(p, round(time.time()-t,1), bpy.data.scenes["VillageKit"].render.engine)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b01_town_overview.png 3.5 BLENDER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0009] 2026-09-23 19:00:39  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b02_west_quarter_fronts",(1595,118,30),(1593,88,3),lens=30,res=(1600,900),outdir=OUT))
print(shot("b03_west_quarter_backs",(1592,60,24),(1593,84,3),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b02_west_quarter_fronts.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\b
# uild\\b03_west_quarter_backs.png\n"}

# ==============================================================================================================
# [0010] 2026-09-23 19:02:15  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b04_gate_outside",(1626,52,12),(1626,76,5),lens=30,res=(1600,900),outdir=OUT))
print(shot("b05_gate_inside",(1626,100,16),(1626,78,4),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b04_gate_outside.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b
# 05_gate_inside.png\n"}

# ==============================================================================================================
# [0011] 2026-09-23 19:03:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b06_chapel_from_plaza",(1640,92,18),(1650,116,4),lens=30,res=(1600,900),outdir=OUT))
print(shot("b07_festival_green",(1659,86,14),(1659,99,3),lens=32,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b06_chapel_from_plaza.png\nC:\\Users\\danie\\AppData\\Roaming\\Clau
# de\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\bui
# ld\\b07_festival_green.png\n"}

# ==============================================================================================================
# [0012] 2026-09-23 19:04:44  blender  ok
# ==============================================================================================================
import bpy, re
for t in bpy.data.texts:
    s=t.as_string()
    i=s.find("def build_festival_green")
    if i>=0:
        print(t.name); print(s[i:i+3500]); break
# ---- result ----
# {"result":"Code executed successfully: vk_mod_defence\ndef build_festival_green(coll,origin,seed=0):\n \"\"\"4x4-cell village green: maypole centre, s
# tage on the north edge, market cross, stocks + pillory,\n hedges east/west, low wall with the gate arch on the south edge, benches, tables, festoon li
# ghts.\"\"\"\n P=def_placer(coll,origin)\n rnd=random.Random(seed)\n P(\"SM_VK_Prop_Maypole\",0,-0.5,0,0)\n P(\"SM_VK_Prop_Stage\",0,4.5,0,0)\n P(\"SM_
# VK_Prop_MarketCross\",-4.1,-3.4,0,0)\n P(\"SM_VK_Prop_Stocks\",4.3,-4.4,0,-15); P(\"SM_VK_Prop_Pillory\",4.4,-1.7,0,-100)\n for y in (-4.5,-1.5,1.5,4.
# 5):\n P(\"SM_VK_Deco_Hedge\",-6,y,0,90); P(\"SM_VK_Deco_Hedge\",6,y,0,90)\n for x in (-4.5,4.5): P(\"SM_VK_Deco_Hedge\",x,6,0,0)\n for x in (-4.5,-1.5
# ,4.5): P(\"SM_VK_LowWall\",x,-6,0,0)\n P(\"SM_VK_LowWall_GateArch\",1.5,-6,0,0)\n for x in (-6,6): P(\"SM_VK_LowWall_Post\",x,-6,0,0)\n P(\"SM_VK_Prop

# ==============================================================================================================
# [0013] 2026-09-23 19:05:41  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b08_brewery_door",(1672.5,104.5,8.5),(1673,113,3.5),lens=30,res=(1600,900),outdir=OUT))
print(shot("b09_blacksmith_door",(1670.5,116.5,8.5),(1670.5,125,3.5),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b08_brewery_door.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b
# 09_blacksmith_door.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 19:06:53  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b09_blacksmith_door",(1662.0,120.5,6.5),(1670.5,125,3.8),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b09_blacksmith_door.png\n"}

# ==============================================================================================================
# [0015] 2026-09-23 19:07:35  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b10_merchant_yard",(1579.5,72.5,14.0),(1579.5,83,3.5),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b10_merchant_yard.png\n"}

# ==============================================================================================================
# [0016] 2026-09-23 19:08:45  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b11_forester_pen",(1543.5,70.0,9.0),(1537.5,76.5,3.5),lens=30,res=(1600,900),outdir=OUT))
print(shot("b12_quarry_leanto",(1545,84,12),(1540,94,4),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b11_forester_pen.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b
# 12_quarry_leanto.png\n"}

# ==============================================================================================================
# [0017] 2026-09-23 19:09:42  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b13_postern_outside",(1552,88,12),(1569,91.5,4.5),lens=30,res=(1600,900),outdir=OUT))
print(shot("b14_postern_inside",(1586,94,12),(1569,91.5,4.5),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b13_postern_outside.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude
# \\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build
# \\b14_postern_inside.png\n"}

# ==============================================================================================================
# [0018] 2026-09-23 19:11:29  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b15_cornerhouse_street_lamp",(1622,100,11),(1610,90.5,3.5),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b15_cornerhouse_street_lamp.png\n"}

# ==============================================================================================================
# [0019] 2026-09-23 19:12:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b16_plaza",(1626,82,26),(1626,101,3),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b16_plaza.png\n"}

# ==============================================================================================================
# [0020] 2026-09-23 19:13:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b17_stockpile",(1611,5,10),(1611,17,1.5),lens=30,res=(1600,900),outdir=OUT))
print(shot("b18_tannery_yard",(1510,48,9),(1510,60,2),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b17_stockpile.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scra
# tch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b18_
# tannery_yard.png\n"}

# ==============================================================================================================
# [0021] 2026-09-23 19:15:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b19_north_wall_from_inside",(1640,118,26),(1640,140,6),lens=24,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b19_north_wall_from_inside.png\n"}

# ==============================================================================================================
# [0022] 2026-09-23 19:16:33  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b20_towerhouse_stair_woodpile",(1584.5,88.5,9.0),(1579,95.5,4.0),lens=30,res=(1600,900),outdir=OUT))
print(shot("b21_blacksmith_east",(1682,121,8.5),(1675,127.5,3.8),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b20_towerhouse_stair_woodpile.png\nC:\\Users\\danie\\AppData\\Roami
# ng\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rerev
# iew\\build\\b21_blacksmith_east.png\n"}

# ==============================================================================================================
# [0023] 2026-09-23 19:17:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b20_towerhouse_stair_woodpile",(1589,91.5,8.0),(1579.5,95.3,4.0),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b20_towerhouse_stair_woodpile.png\n"}

# ==============================================================================================================
# [0024] 2026-09-23 19:18:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b22_smokehouse_woodpile",(1666,41,5.5),(1659.5,49,0.5),lens=30,res=(1600,900),outdir=OUT))
print(shot("b23_barracks",(1672,-6,16),(1684,8,2),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b22_smokehouse_woodpile.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\b
# uild\\b23_barracks.png\n"}

# ==============================================================================================================
# [0025] 2026-09-23 19:20:33  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b24_postern_lane_quarry",(1546,70,30),(1548,93,3),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b24_postern_lane_quarry.png\n"}

# ==============================================================================================================
# [0026] 2026-09-23 19:21:41  blender  ok
# ==============================================================================================================
import bpy, re
for t in bpy.data.texts:
    s=t.as_string()
    for m in re.finditer(r".*Deco_Weeds.*", s):
        ln=s[:m.start()].count("\n")+1
        print(t.name, ln, m.group(0).strip()[:200])
# ---- result ----
# {"result":"Code executed successfully: vk_helpers 765 if r.random()<0.4: place_v(coll,\"SM_VK_Deco_Weeds\",x,y,0,rot,origin,{})\nvk_helpers 2344 (\"SM
# _VK_Deco_Weeds\",lambda k: deco_weeds(k,3),dict(wobble=False,grime=True)),\nvk_mod_defence 1419 P(\"SM_VK_Deco_Weeds\",1.5,-3,0,0,{}); P(\"SM_VK_Deco_
# Ivy_B\",3.0,1.5,0,90,{})\nvk_mod_frontier 688 if r.random()<0.5: place_v(coll,\"SM_VK_Deco_Weeds\",x,y-0.0,0,rot,origin,{})\nvk_mod_frontier 769 place
# _v(coll,\"SM_VK_Deco_Weeds\",0,-1.5,0,0,hut,{})\nvk_mod_humble 922 o = place_v(coll, \"SM_VK_Deco_Weeds\", x, y, 0, rot, origin, {})\nvk_mod_town 990 
# P(\"SM_VK_Deco_Weeds\",x,y,0,rot,{})\nvk_terrain_demo 227 if not any(k in src for k in (\"Fence\",\"Prop_\",\"Crop_\",\"Deco_Weeds\")): continue\n"}

# ==============================================================================================================
# [0027] 2026-09-23 19:22:02  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["vk_helpers"].as_string().splitlines()
print("\n".join(s[750:770]))
s=bpy.data.texts["vk_mod_town"].as_string().splitlines()
print("----"); print("\n".join(s[978:993]))
# ---- result ----
# {"result":"Code executed successfully: gw={\"D\":f\"SM_VK_Wall_{g}_Door\",\"W\":f\"SM_VK_Wall_{g}_Window\",\".\":f\"SM_VK_Wall_{g}\"}\n gc=f\"SM_VK_Co
# rner_{g}\"\n return gw,gc\ndef _upper(r,c):\n if c==\"W\": return \"SM_VK_Wall_Timber_Window\"\n return r.choice([\"SM_VK_Wall_Timber\",\"SM_VK_Wall_T
# imber_X\",\"SM_VK_Wall_Timber_K\"])\ndef _dress(coll,origin,x,y,rot,c,r,style,z0=0):\n # props in wall-local coordinates, rotated with the wall\n a=ma
# th.radians(rot); ca,sa=math.cos(a),math.sin(a)\n def loc(lx,ly): return (x+lx*ca-ly*sa,y+lx*sa+ly*ca)\n if c==\"W\" and r.random()<0.7:\n px,py=loc(0,
# -0.55 if style.get(\"ground\")==\"Stone\" else -0.5)\n fb=\"SM_VK_Prop_FlowerBox\" if r.random()<0.6 else \"SM_VK_Prop_FlowerBox_Daisy\"\n place_v(col
# l,fb,px,py,0.78 if style.get(\"ground\")==\"Stone\" else 0.9,rot,origin,{})\n if r.random()<0.4: place_v(coll,\"SM_VK_Deco_Weeds\",x,y,0,rot,origin,{}

# ==============================================================================================================
# [0028] 2026-09-23 19:22:42  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
o=bpy.data.objects["SM_VK_Porch_inst.031"]
me=o.data
low=[o.matrix_world@v.co for v in me.vertices if v.co.z<0.5]
# cluster by 0.5 m
cl=[]
for p in low:
    for c in cl:
        if (c[0]-p).length<0.6: c[1].append(p); break
    else: cl.append([p,[p]])
for c in cl:
    xs=[p.x for p in c[1]]; ys=[p.y for p in c[1]]
    print(round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),len(c[1]))
for n in ["SM_VK_Prop_BarrelStack_inst.023","SM_VK_Prop_CiderPress_inst","SM_VK_Prop_Cart_inst.014","SM_VK_Prop_Woodpile_inst.016","SM_VK_Prop_ArmorStand_inst.001"]:
    ob=bpy.data.objects[n]; pts=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    print(n, round(min(p.x for p in pts),2),round(max(p.x for p in pts),2),round(min(p.y for p in pts),2),round(max(p.y for p in pts),2))
o=bpy.data.objects["SM_VK_Porch_inst.032"]
low=[o.matrix_world@v.co for v in o.data.vertices if v.co.z<0.5]
print("porch032 low x",sorted(set(round(p.x,1) for p in low)), "y", sorted(set(round(p.y,1) for p in low)))
o=bpy.data.objects["SM_VK_Porch_inst.026"]
low=[o.matrix_world@v.co for v in o.data.vertices if v.co.z<0.5]
print("porch026 low x",sorted(set(round(p.x,1) for p in low)), "y", sorted(set(round(p.y,1) for p in low)))
# ---- result ----
# {"result":"Code executed successfully: 1671.23 1671.61 112.18 112.82 56\n1673.41 1673.77 112.18 112.83 66\n1673.4 1673.46 113.63 113.69 14\n1671.54 16
# 71.61 113.64 113.7 14\n1671.55 1671.61 112.81 112.87 10\nSM_VK_Prop_BarrelStack_inst.023 1673.25 1675.4 111.56 113.18\nSM_VK_Prop_CiderPress_inst 1669
# .3 1671.54 111.38 112.98\nSM_VK_Prop_Cart_inst.014 1674.52 1678.08 110.55 112.84\nSM_VK_Prop_Woodpile_inst.016 1670.25 1673.95 123.45 124.75\nSM_VK_Pr
# op_ArmorStand_inst.001 1687.52 1688.85 3.24 5.07\nporch032 low x [1668.2, 1668.3, 1668.5, 1668.6, 1670.4, 1670.5, 1670.7, 1670.8] y [124.2, 124.3, 124
# .4, 124.5, 124.8, 124.9, 125.6, 125.7]\nporch026 low x [1686.3, 1686.4, 1687.1, 1687.2, 1687.5, 1687.6, 1687.7, 1687.8] y [4.7, 4.8, 5.0, 5.1, 6.9, 7.
# 0, 7.2, 7.3]\n"}

# ==============================================================================================================
# [0029] 2026-09-23 19:25:00  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[]
for c in tc.all_objects:
    if c.type=="MESH" and "Chunk" in c.name:
        pts=[c.matrix_world@Vector(v) for v in c.bound_box]
        chunks.append((c,c.matrix_world.inverted(),min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)))
def ground(x,y):
    best=None
    for c,mi,x0,x1,y0,y1 in chunks:
        if x0<=x<=x1 and y0<=y<=y1:
            o=mi@Vector((x,y,60.0)); dv=(mi.to_3x3()@Vector((0,0,-1))).normalized()
            hit,loc,nor,idx=c.ray_cast(o,dv)
            if hit:
                z=(c.matrix_world@loc).z; best=z if best is None or z>best else best
    return best
print("row30 lane y=91.5:",[(x,round(ground(x,91.5),2)) for x in range(1528,1570,2)])
print("row29 y=88.5:",[(x,round(ground(x,88.5),2)) for x in range(1528,1570,4)])
# ---- result ----
# {"result":"Code executed successfully: row30 lane y=91.5: [(1528, 3.0), (1530, 3.0), (1532, 3.0), (1534, 6.0), (1536, 6.0), (1538, 6.0), (1540, 3.0), 
# (1542, 3.0), (1544, 3.0), (1546, 3.0), (1548, 3.0), (1550, 3.0), (1552, 6.0), (1554, 6.0), (1556, 6.0), (1558, 3.0), (1560, 3.0), (1562, 3.0), (1564, 
# 3.0), (1566, 3.0), (1568, 3.0)]\nrow29 y=88.5: [(1528, 3.0), (1532, 3.0), (1536, 3.0), (1540, 3.0), (1544, 3.0), (1548, 3.0), (1552, 3.0), (1556, 3.0)
# , (1560, 3.0), (1564, 3.0), (1568, 3.0)]\n"}

# ==============================================================================================================
# [0030] 2026-09-23 19:25:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b25_ridge_stair_oak",(1530,78,26),(1529,101,4),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b25_ridge_stair_oak.png\n"}

# ==============================================================================================================
# [0031] 2026-09-23 19:26:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build"
print(shot("b26_barracks_door",(1694.5,6.0,7.0),(1686.5,6.0,2.8),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build\\b26_barracks_door.png\n"}
