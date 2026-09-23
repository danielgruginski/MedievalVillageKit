# valley-review / agent-ac1830a198e7e92a0.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 17:45:59  blender  ok
# ==============================================================================================================
import bpy
sc = bpy.context.scene
print(sc.name, bpy.data.filepath, bpy.data.is_dirty)
print('vk_render' in bpy.data.texts)
print(bpy.data.texts["vk_render"].as_string()[:3000])
col = bpy.data.collections.get("VK_ValleyTown")
print(len(col.all_objects))
# ---- result ----
# {"result":"Code executed successfully: VillageKit E:\\Unity\\Projects\\Cube Sorter\\Art\\WallKit\\medievalDiorama.blend False\nTrue\nimport bpy, os\nf
# rom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8
# a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,lens=35,res=(1280,720),scene=\"VillageKit\",samples=None,ou
# tdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.
# cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)\n cam.location=loc; cam.rotation_euler=(Vector
# (target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_end=3000\n old=(sc.camera,sc.render.resolution_x,sc.rende

# ==============================================================================================================
# [0002] 2026-09-23 17:46:20  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
def bb(o):
    ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return tuple(round(min(w[k] for w in ws),2) for k in range(3))+tuple(round(max(w[k] for w in ws),2) for k in range(3))
for n in ["SM_VK_Gatehouse_Block_inst","SM_VK_Gatehouse_GateLeaf_inst","SM_VK_Gatehouse_GateLeaf_inst.001"]:
    o=bpy.data.objects.get(n); print(n, o and bb(o))
def down(x,y):
    r=sc.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name if r[0] else None)
for x in (1623.5,1624.5,1625.5,1626.5,1627.5,1628.5,1629.5,1630.5):
    print(x,[ (y,)+down(x,y) for y in (69.0,70.5,71.5,72.5,73.5,74.5,76,78)])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Gatehouse_Block_inst (1622.19, 69.68, 1.5, 1632.83, 78.25, 12.0)\nSM_VK_Gatehouse_GateLeaf_inst (1625.68,
#  73.69, 3.02, 1626.43, 75.38, 7.36)\nSM_VK_Gatehouse_GateLeaf_inst.001 (1628.57, 73.69, 3.02, 1629.32, 75.38, 7.36)\n1623.5 [(69.0, 1.5, 'VKV_Chunk_2_
# 1'), (70.5, 12.18, 'SM_VK_Roof_Cone_R2_inst'), (71.5, 13.26, 'SM_VK_Roof_Cone_R2_inst'), (72.5, 13.26, 'SM_VK_Roof_Cone_R2_inst'), (73.5, 12.99, 'SM_V
# K_Roof_Hip_inst.010'), (74.5, 12.99, 'SM_VK_Roof_Hip_inst.010'), (76, 12.99, 'SM_VK_Roof_Hip_inst.010'), (78, 12.4, 'SM_VK_Roof_Hip_inst.010')]\n1624.
# 5 [(69.0, 1.5, 'VKV_Chunk_2_1'), (70.5, 12.54, 'SM_VK_Roof_Cone_R2_inst'), (71.5, 14.81, 'SM_VK_Roof_Cone_R2_inst'), (72.5, 14.81, 'SM_VK_Roof_Cone_R2
# _inst'), (73.5, 14.54, 'SM_VK_Roof_Hip_inst.010'), (74.5, 14.27, 'SM_VK_Roof_Hip_inst.010'), (76, 14.27, 'SM_VK_Roof_Hip_inst.010'), (78, 12.4, 'SM_VK

# ==============================================================================================================
# [0003] 2026-09-23 17:46:30  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
def down(x,y,z0=4.6):
    r=sc.ray_cast(dg,Vector((x,y,z0)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name[:22] if r[0] else None)
for x in (1623.5,1624.5,1625.5,1626.2,1627.0,1627.5,1628.0,1628.8,1629.5):
    print(x,[ (y,)+down(x,y) for y in (70.0,70.75,71.5,72.0,72.5,73.0,73.5,74.5,77)])
# horizontal rays at z=2.4 heading north along x in passage from y=68
for x in (1623.5,1624.5,1625.5,1626.2,1627.0,1628.0,1628.8,1629.5):
    for z in (1.8,2.4,3.5):
        r=sc.ray_cast(dg,Vector((x,66,z)),Vector((0,1,0)),distance=15)
        print('H',x,z,round(r[1].y,2) if r[0] else None, r[4].name[:24] if r[0] else None)
# ---- result ----
# {"result":"Code executed successfully: 1623.5 [(70.0, 3.28, 'SM_VK_Gatehouse_Block_'), (70.75, 1.62, 'VKV_Chunk_2_1'), (71.5, 2.0, 'VKV_Chunk_2_1'), (
# 72.0, 2.25, 'VKV_Chunk_2_1'), (72.5, 2.5, 'VKV_Chunk_2_1'), (73.0, 2.75, 'VKV_Chunk_2_1'), (73.5, 4.53, 'SM_VK_Gatehouse_Block_'), (74.5, 3.0, 'VKV_Ch
# unk_2_1'), (77, 3.0, 'VKV_Chunk_2_1')]\n1624.5 [(70.0, 3.36, 'SM_VK_Gatehouse_Block_'), (70.75, 1.62, 'VKV_Chunk_2_1'), (71.5, 2.0, 'VKV_Chunk_2_1'), 
# (72.0, 2.25, 'VKV_Chunk_2_1'), (72.5, 2.5, 'VKV_Chunk_2_1'), (73.0, 2.75, 'VKV_Chunk_2_1'), (73.5, 3.0, 'VKV_Chunk_2_1'), (74.5, 3.0, 'VKV_Chunk_2_1')
# , (77, 3.0, 'VKV_Chunk_2_1')]\n1625.5 [(70.0, 3.33, 'SM_VK_Gatehouse_Block_'), (70.75, 1.62, 'VKV_Chunk_2_1'), (71.5, 2.0, 'VKV_Chunk_2_1'), (72.0, 2.
# 25, 'VKV_Chunk_2_1'), (72.5, 2.5, 'VKV_Chunk_2_1'), (73.0, 2.75, 'VKV_Chunk_2_1'), (73.5, 4.53, 'SM_VK_Gatehouse_Block_'), (74.5, 3.0, 'VKV_Chunk_2_1'

# ==============================================================================================================
# [0004] 2026-09-23 17:46:42  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
import time; t=time.time()
p=shot("verify_01_gate_ramp", (1626.0,58.0,6.5),(1626.5,73.0,3.0),lens=35,res=(1280,720),outdir=OD)
print(p, time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\verify\\verify_01_gate_ramp.png 3.3773727416992188\n"}

# ==============================================================================================================
# [0005] 2026-09-23 17:47:00  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
col=bpy.data.collections["VK_ValleyTown"]
objs=list(col.all_objects)
def bb(o):
    ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(w[k] for w in ws) for k in range(3)],[max(w[k] for w in ws) for k in range(3)]
walls=[o for o in objs if o.name.startswith(("SM_VK_TownWall","SM_VK_Gatehouse_Block"))]
wb=[(o.name,)+tuple(bb(o)) for o in walls]
nat=[o for o in objs if any(k in o.name for k in ("Tree_","Bush_","Plant_"))]
hits=[]
for o in nat:
    p=o.location
    for (n,mn,mx) in wb:
        if mn[0]<=p.x<=mx[0] and mn[1]<=p.y<=mx[1]:
            hits.append((o.name,round(p.x,1),round(p.y,1),round(p.z,1),n)); break
print(len(hits))
for h in hits: print(h)
# ---- result ----
# {"result":"Code executed successfully: 23\n('SM_VK_Plant_Wildflowers_inst.044', 1569.8, 73.7, 3.0, 'SM_VK_TownWall_Straight_inst')\n('SM_VK_Plant_Wild
# flowers_inst.046', 1581.8, 73.9, 3.0, 'SM_VK_TownWall_Straight_inst.008')\n('SM_VK_Tree_Oak_B_inst.023', 1601.3, 74.4, 3.0, 'SM_VK_TownWall_Straight_i
# nst.020')\n('SM_VK_Tree_Apple_inst.009', 1619.4, 74.0, 3.0, 'SM_VK_TownWall_Straight_inst.032')\n('SM_VK_Bush_Round_inst.038', 1645.3, 73.7, 3.0, 'SM_
# VK_TownWall_Straight_inst.047')\n('SM_VK_Tree_Birch_inst.014', 1655.0, 73.4, 3.0, 'SM_VK_TownWall_Straight_inst.053')\n('SM_VK_Tree_Birch_inst.016', 1
# 670.2, 74.0, 3.0, 'SM_VK_TownWall_Straight_inst.063')\n('SM_VK_Bush_Round_inst.043', 1567.8, 91.0, 3.0, 'SM_VK_TownWall_Straight_inst.087')\n('SM_VK_B
# ush_Round_inst.045', 1566.6, 97.7, 3.0, 'SM_VK_TownWall_Tower_Round_inst.008')\n('SM_VK_Bush_Hydrangea_inst.007', 1688.5, 106.3, 3.0, 'SM_VK_TownWall_

# ==============================================================================================================
# [0006] 2026-09-23 17:47:14  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
cache={}
def bvh(n):
    if n in cache: return cache[n]
    o=bpy.data.objects[n]; t=BVHTree.FromObject(o,dg,deform=False); 
    # FromObject gives local coords; transform: build from world verts instead
    me=o.evaluated_get(dg).to_mesh(); M=o.matrix_world
    vs=[M@v.co for v in me.vertices]; fs=[tuple(p.vertices) for p in me.polygons]
    o.evaluated_get(dg).to_mesh_clear()
    t=BVHTree.FromPolygons(vs,fs); cache[n]=t; return t
def ov(a,b): return len(bvh(a).overlap(bvh(b)))
pairs=[("SM_VK_TownWall_Tower_Round_inst.002",["SM_VK_Turret_Seg_inst","SM_VK_Turret_Seg_inst.001","SM_VK_Wall_Stone_Shop_inst.002","SM_VK_Prop_LampPost_inst.027"]),
("SM_VK_TownWall_Tower_Round_inst.004",["SM_VK_Wall_Stone_inst.188","SM_VK_Wall_Stone_Window_inst.173","SM_VK_Roof_Mid_inst.041","SM_VK_Roof_Gable_Stepped_inst.004"]),
("SM_VK_TownWall_Tower_Round_inst.006",["SM_VK_Wall_Plaster_Door_inst.024","SM_VK_Roof_Gable_Stepped_inst.003","SM_VK_Roof_Mid_inst.039"]),
("SM_VK_TownWall_Tower_Round_inst.007",["SM_VK_Wall_Stone_inst.195","SM_VK_Wall_Stone_inst.196","SM_VK_Roof_Gable_inst.084","SM_VK_Roof_Gable_inst.085"]),
("SM_VK_Gatehouse_Block_inst",["SM_VK_Corner_Stone_inst.185","SM_VK_Wall_Stone_inst.206","SM_VK_Wall_Stone_inst.200","SM_VK_Wall_Timber_inst.054","SM_VK_Roof_Hip_inst.015"]),
("SM_VK_Wall_Timber_K_inst.046",["SM_VK_Wall_Timber_inst.054","SM_VK_Roof_Hip_inst.015"]),
]
for a,bs in pairs:
    for b in bs:
        if bpy.data.objects.get(b) is None: print('missing',b); continue
        print(a[-14:],b,ov(a,b))
# ---- result ----
# {"result":"Code executed successfully: Round_inst.002 SM_VK_Turret_Seg_inst 125\nRound_inst.002 SM_VK_Turret_Seg_inst.001 215\nRound_inst.002 SM_VK_Wa
# ll_Stone_Shop_inst.002 660\nRound_inst.002 SM_VK_Prop_LampPost_inst.027 0\nRound_inst.004 SM_VK_Wall_Stone_inst.188 411\nRound_inst.004 SM_VK_Wall_Sto
# ne_Window_inst.173 437\nRound_inst.004 SM_VK_Roof_Mid_inst.041 2\nRound_inst.004 SM_VK_Roof_Gable_Stepped_inst.004 2\nRound_inst.006 SM_VK_Wall_Plaste
# r_Door_inst.024 578\nRound_inst.006 SM_VK_Roof_Gable_Stepped_inst.003 211\nRound_inst.006 SM_VK_Roof_Mid_inst.039 205\nRound_inst.007 SM_VK_Wall_Stone
# _inst.195 367\nRound_inst.007 SM_VK_Wall_Stone_inst.196 411\nRound_inst.007 SM_VK_Roof_Gable_inst.084 54\nRound_inst.007 SM_VK_Roof_Gable_inst.085 54\
# nuse_Block_inst SM_VK_Corner_Stone_inst.185 469\nuse_Block_inst SM_VK_Wall_Stone_inst.206 404\nuse_Block_inst SM_VK_Wall_Stone_inst.200 149\nuse_Block

# ==============================================================================================================
# [0007] 2026-09-23 17:47:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
out=[]
out.append(shot("verify_02_cornerhouse_tower", (1616.0,92.0,17.0),(1608.0,76.5,8.0),lens=35,outdir=OD))
out.append(shot("verify_03_terrace_towers", (1661.0,96.0,20.0),(1660.5,77.0,8.0),lens=30,outdir=OD))
out.append(shot("verify_04_blacksmith_tower", (1662.0,120.0,15.0),(1671.0,135.0,6.0),lens=32,outdir=OD))
out.append(shot("verify_05_gate_infill", (1641.0,94.0,20.0),(1629.0,78.0,7.0),lens=32,outdir=OD))
out.append(shot("verify_06_wall_trees_outside", (1610.0,58.0,7.0),(1616.0,74.0,6.0),lens=30,outdir=OD))
print(out)
# ---- result ----
# {"result":"Code executed successfully: ['C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56
# c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\renders2\\\\review\\\\verify\\\\verify_02_cornerhouse_tower.png', 'C:\\\
# \Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\
# \\\scratch-2026-09-23-d49817\\\\renders2\\\\review\\\\verify\\\\verify_03_terrace_towers.png', 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\
# \\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\renders2\\\\revie
# w\\\\verify\\\\verify_04_blacksmith_tower.png', 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9

# ==============================================================================================================
# [0008] 2026-09-23 17:48:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
out=[]
out.append(shot("verify_02_cornerhouse_tower", (1600.0,62.0,26.0),(1608.0,78.0,8.0),lens=35,outdir=OD))
out.append(shot("verify_03_terrace_towers", (1660.5,56.0,28.0),(1660.5,78.0,8.0),lens=30,outdir=OD))
out.append(shot("verify_06_wall_trees_outside", (1611.0,66.5,5.0),(1619.0,74.5,5.0),lens=26,outdir=OD))
print(out)
# ---- result ----
# {"result":"Code executed successfully: ['C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56
# c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\renders2\\\\review\\\\verify\\\\verify_02_cornerhouse_tower.png', 'C:\\\
# \Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\
# \\\scratch-2026-09-23-d49817\\\\renders2\\\\review\\\\verify\\\\verify_03_terrace_towers.png', 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\
# \\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\renders2\\\\revie
# w\\\\verify\\\\verify_06_wall_trees_outside.png']\n"}

# ==============================================================================================================
# [0009] 2026-09-23 17:48:42  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
col=bpy.data.collections["VK_ValleyTown"]
for o in col.all_objects:
    n=o.name
    if ("Door" in n or "Shop" in n or "Loading" in n) and 1570<o.location.x<1625 and 76<o.location.y<88:
        print(n, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z)))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Timber_Door_inst (1623.0, 76.5, 9.2) -90\nSM_VK_Wall_Stone_Shop_inst (1576.5, 78.0, 3.0) 0\nSM_VK_Pr
# op_ShopGoods_Tools_inst (1576.5, 77.45, 3.95) 0\nSM_VK_Wall_Stone_Door_inst.038 (1579.5, 78.0, 3.0) 0\nSM_VK_Wall_Stone_Shop_inst.001 (1582.5, 78.0, 3
# .0) 0\nSM_VK_Prop_ShopGoods_Bread_inst (1582.5, 77.45, 3.95) 0\nSM_VK_Wall_StoneUp_Loading_inst (1579.5, 78.0, 6.0) 0\nSM_VK_Wall_StoneUp_Door_inst (1
# 579.5, 84.0, 6.0) 180\nSM_VK_Wall_StoneUp_Loading_inst.001 (1579.5, 78.0, 8.8) 0\nSM_VK_Wall_Plaster_Door_inst.018 (1599.0, 82.5, 3.0) 90\nSM_VK_Wall_
# Plaster_Shop_inst (1594.5, 78.0, 3.0) 0\nSM_VK_Prop_ShopGoods_Produce_inst (1594.5, 77.45, 3.95) 0\nSM_VK_Wall_Plaster_Door_inst.019 (1597.5, 78.0, 3.
# 0) 0\nSM_VK_Wall_Stone_Shop_inst.002 (1609.5, 78.0, 3.0) 0\nSM_VK_Prop_ShopGoods_Fish_inst (1609.5, 77.45, 3.95) 0\nSM_VK_Wall_Stone_Door_inst.039 (16

# ==============================================================================================================
# [0010] 2026-09-23 17:49:03  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
cache={}
def bvh(n):
    if n in cache: return cache[n]
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); cache[n]=t; return t
def ov(a,b):
    if not bpy.data.objects.get(a) or not bpy.data.objects.get(b): return 'missing'
    return len(bvh(a).overlap(bvh(b)))
P=[("SM_VK_Prop_Barge_inst","SM_VK_Quay_Stair_inst"),
("SM_VK_Tree_Willow_inst.013","SM_VK_Quay_Stair_inst"),("SM_VK_Tree_Willow_inst.013","SM_VK_Quay_Post_inst.002"),
("SM_VK_Prop_WeaponRack_inst.007","SM_VK_Wall_Stone_Door_inst.036"),
("SM_VK_Prop_Woodpile_inst.016","SM_VK_Porch_inst.032"),
("SM_VK_Prop_BarrelStack_inst.023","SM_VK_Porch_inst.031"),
("SM_VK_Prop_Anvil_inst.004","SM_VK_Porch_inst.030"),
("SM_VK_Prop_Crates_inst.014","SM_VK_LowWall_inst.030"),("SM_VK_Prop_Cart_inst.014","SM_VK_LowWall_Post_inst.019"),
("SM_VK_Prop_BarrelStack_inst.017","SM_VK_LowWall_inst.031"),("SM_VK_Prop_Sacks_inst.013","SM_VK_LowWall_inst.031"),
("SM_VK_Prop_LampPost_inst.033","SM_VK_Porch_inst.036"),("SM_VK_Prop_LampPost_inst.034","SM_VK_Roof_Mid_inst.048"),
("SM_VK_Prop_LampPost_inst.027","SM_VK_TownWall_Straight_inst.024"),
("SM_VK_Crop_TreeNursery_inst","SM_VK_Wall_Shed_Window_inst.003"),("SM_VK_Prop_Fence_inst.183","SM_VK_Wall_Shed_Window_inst.003"),
("SM_VK_Prop_Rowboat_inst","SM_VK_Pier_Stairs_inst"),
("SM_VK_Tree_Blossom_inst.009","SM_VK_Roof_Gable_inst.084"),("SM_VK_Tree_Blossom_inst.005","SM_VK_Gatehouse_Block_inst"),
("SM_VK_Tree_Blossom_inst.007","SM_VK_Porch_inst.032"),
("SM_VK_Tree_Pine_A_inst.157","SM_VK_TownWall_Tower_Round_inst.001"),("SM_VK_Tree_Pine_A_inst.158","SM_VK_TownWall_Tower_Round_inst.001"),
("SM_VK_Tree_Pine_B_inst.170","SM_VK_TownWall_Tower_Round_inst.007"),("SM_VK_Tree_Pine_A_inst.161","SM_VK_TownWall_Tower_Round_inst.005"),
("SM_VK_Prop_ChickenCoop_Wattle_inst.002","SM_VK_RoofThatch_Hip_inst.006"),("SM_VK_Prop_Trough_inst.013","SM_VK_Wall_Plaster_inst.083"),
]
for a,b in P: print(a[6:],'|',b[6:],ov(a,b))
# ---- result ----
# {"result":"Code executed successfully: Prop_Barge_inst | Quay_Stair_inst 6\nTree_Willow_inst.013 | Quay_Stair_inst 10\nTree_Willow_inst.013 | Quay_Pos
# t_inst.002 28\nProp_WeaponRack_inst.007 | Wall_Stone_Door_inst.036 44\nProp_Woodpile_inst.016 | Porch_inst.032 150\nProp_BarrelStack_inst.023 | Porch_
# inst.031 87\nProp_Anvil_inst.004 | Porch_inst.030 22\nProp_Crates_inst.014 | LowWall_inst.030 881\nProp_Cart_inst.014 | LowWall_Post_inst.019 116\nPro
# p_BarrelStack_inst.017 | LowWall_inst.031 91\nProp_Sacks_inst.013 | LowWall_inst.031 219\nProp_LampPost_inst.033 | Porch_inst.036 161\nProp_LampPost_i
# nst.034 | Roof_Mid_inst.048 40\nProp_LampPost_inst.027 | TownWall_Straight_inst.024 128\nCrop_TreeNursery_inst | Wall_Shed_Window_inst.003 298\nProp_F
# ence_inst.183 | Wall_Shed_Window_inst.003 150\nProp_Rowboat_inst | Pier_Stairs_inst 221\nTree_Blossom_inst.009 | Roof_Gable_inst.084 125\nTree_Blossom

# ==============================================================================================================
# [0011] 2026-09-23 17:49:17  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
L=[("verify_07_southwall_shopbacks",(1595,106,30),(1595,80,4),30),
("verify_08_alley_from_wall",(1586,75.5,10.5),(1600,78.5,4.5),28),
("verify_09_north_tower_pines",(1592,126,17),(1587,139,9),30),
("verify_10_footbridge",(1548,20,12),(1537.5,42,0),30),
("verify_11_quarry",(1562,95,12),(1545,100,4),30),
("verify_12_barracks_door",(1692.5,4.5,3.6),(1686,4.5,2.6),35),
("verify_13_blacksmith_door",(1669.5,120,5),(1669.5,128,3.8),35),
("verify_14_merchant_yard",(1580,95,10),(1580,86,3.5),30)]
for n,a,b,l in L: shot(n,a,b,lens=l,outdir=OD)
print('ok')
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0012] 2026-09-23 17:50:31  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
col=bpy.data.collections["VK_ValleyTown"]
ob=bpy.data.objects
def loc(n): o=ob.get(n); return o and (tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z)))
for n in ["SM_VK_Chapel_Wall_Door_inst.003","SM_VK_Wall_Plaster_inst.083","SM_VK_Wall_Plaster_Door_inst.017","SM_VK_Wall_Stone_Door_inst.049","SM_VK_Wall_Stone_inst.190","SM_VK_Tree_Oak_A_inst.017","SM_VK_Tree_Oak_B_inst.015","SM_VK_Tent_Bell_inst","SM_VK_Wall_Shed_Door_inst","SM_VK_Prop_TreadwheelCrane_inst"]:
    print(n,loc(n))
# chapel door list
print([ (o.name,loc(o.name)) for o in col.all_objects if o.name.startswith("SM_VK_Chapel_Wall_Door")])
# scaffold materials
s=ob.get("SM_VK_Scaffold_Wall")
print('scaffold mats', s and [m.name for m in s.data.materials])
# water material
m=bpy.data.materials.get("M_VKT_Water")
if m:
    for nd in m.node_tree.nodes:
        if nd.type=="BSDF_PRINCIPLED":
            print('emis', [ (i.name, (tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)) for i in nd.inputs if 'Emission' in i.name or i.name in ('Alpha','Roughness')])
    print(m.blend_method if hasattr(m,'blend_method') else None, getattr(m,'surface_render_method',None))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Chapel_Wall_Door_inst.003 ((1648.5, 123.0, 3.0), 180)\nSM_VK_Wall_Plaster_inst.083 ((1506.0, 61.0, 1.5), 
# 0)\nSM_VK_Wall_Plaster_Door_inst.017 ((1509.0, 61.0, 1.5), 0)\nSM_VK_Wall_Stone_Door_inst.049 ((1672.5, 113.5, 3.0), 0)\nSM_VK_Wall_Stone_inst.190 ((1
# 669.5, 119.5, 3.0), 180)\nSM_VK_Tree_Oak_A_inst.017 ((1602.76, 6.9, 1.5), 212)\nSM_VK_Tree_Oak_B_inst.015 ((1595.16, 4.87, 1.5), 23)\nSM_VK_Tent_Bell_
# inst ((1597.03, 11.22, 1.5), 225)\nSM_VK_Wall_Shed_Door_inst ((1693.5, 21.0, 0.0), 180)\nSM_VK_Prop_TreadwheelCrane_inst ((1544.4, 102.9, 6.0), -90)\n
# [('SM_VK_Chapel_Wall_Door_inst.003', ((1648.5, 123.0, 3.0), 180))]\nscaffold mats ['M_VK_Stone', 'M_VK_Plaster', 'M_VK_Wood', 'M_VK_RoofRed', 'M_VK_Wi
# ndow', 'M_VK_Iron', 'M_VK_FlowerPink', 'M_VK_FlowerYellow', 'M_VK_Leaf', 'M_VK_Glow', 'M_VK_Shutter_Teal', 'M_VK_Cloth_Red', 'M_VK_Cloth_Cream', 'M_VK

# ==============================================================================================================
# [0013] 2026-09-23 17:50:47  blender  ok
# ==============================================================================================================
import bpy
from collections import Counter
from mathutils import Vector
for n in ["SM_VK_Scaffold_Wall","SM_VK_Scaffold_Wall_Top"]:
    o=bpy.data.objects.get(n)
    if not o: print('no',n); continue
    c=Counter(o.data.materials[p.material_index].name for p in o.data.polygons)
    print(n,c.most_common())
def bb(n):
    o=bpy.data.objects[n]; ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [round(min(w[k] for w in ws),1) for k in range(3)],[round(max(w[k] for w in ws),1) for k in range(3)]
for n in ["SM_VK_Tree_Oak_A_inst.017","SM_VK_Tree_Oak_B_inst.015","SM_VK_Tent_Bell_inst"]: print(n,bb(n))
print([o.name for o in bpy.data.collections["VK_ValleyTown"].all_objects if 'Scaffold' in o.name][:20])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Scaffold_Wall [('M_VK_Wood', 52), ('M_VK_Planks', 52), ('M_VK_Burlap', 48), ('M_VK_BarkBirch', 46), ('M_V
# K_EndGrain', 4)]\nSM_VK_Scaffold_Wall_Top [('M_VK_Wood', 52), ('M_VK_Planks', 52), ('M_VK_Burlap', 48), ('M_VK_BarkBirch', 46), ('M_VK_EndGrain', 4)]\
# nSM_VK_Tree_Oak_A_inst.017 ([1596.1, 1.2, 1.1], [1608.4, 13.7, 8.9])\nSM_VK_Tree_Oak_B_inst.015 ([1590.2, 0.7, 1.1], [1600.1, 10.1, 9.0])\nSM_VK_Tent_
# Bell_inst ([1594.0, 7.7, 1.4], [1600.5, 14.3, 4.9])\n['SM_VK_Scaffold_Wall_inst', 'SM_VK_Scaffold_Wall_inst.001', 'SM_VK_Scaffold_Wall_inst.002', 'SM_
# VK_Scaffold_Wall_inst.003', 'SM_VK_Scaffold_Wall_inst.004', 'SM_VK_Scaffold_Corner_inst', 'SM_VK_Scaffold_Corner_inst.001', 'SM_VK_Scaffold_Wall_inst.
# 005', 'SM_VK_Scaffold_Wall_inst.006', 'SM_VK_Scaffold_Wall_inst.007', 'SM_VK_Scaffold_Wall_inst.008', 'SM_VK_Scaffold_Wall_inst.009', 'SM_VK_Scaffold_

# ==============================================================================================================
# [0014] 2026-09-23 17:51:02  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
L=[("verify_15_overview",(1605,-45,135),(1608,80,0),30),
("verify_16_town_colony",(1640,72,33),(1640,100,3),30),
("verify_17_construction",(1655,44,30),(1655,66,2),30),
("verify_18_camp",(1598,-14,30),(1598,8,1.5),30),
("verify_19_river_mill",(1585,28,30),(1585,50,0),30),
("verify_20_laundry",(1641,45,4.5),(1641,54,2),30),
("verify_21_millcart",(1575,52,4.5),(1578,59.5,1.2),30),
("verify_22_quay",(1600,37,9),(1607,48,0.5),30)]
for n,a,b,l in L: shot(n,a,b,lens=l,outdir=OD)
print('ok')
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0015] 2026-09-23 17:52:27  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
terr=[o for o in bpy.data.collections["VK_ValleyTerrain"].all_objects if o.name.startswith("VKV_Chunk")]
from mathutils.bvhtree import BVHTree
def tb(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return t
T=[tb(o) for o in terr]
def th(x,y):
    best=None
    for t in T:
        h=t.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
        if h[0] and (best is None or h[0].z>best): best=h[0].z
    return best
def bb(n):
    o=bpy.data.objects[n]; ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(w[k] for w in ws) for k in range(3)],[max(w[k] for w in ws) for k in range(3)]
for n in ["SM_VK_Prop_Laundry_inst.002","SM_VK_Prop_FishRack_inst","SM_VK_Prop_Cart_inst.008","SM_VK_Prop_Crates_inst.007"]:
    mn,mx=bb(n); hs=[]
    for fx in (0.1,0.5,0.9):
        for fy in (0.1,0.5,0.9):
            hs.append(round(th(mn[0]+fx*(mx[0]-mn[0]),mn[1]+fy*(mx[1]-mn[1])),2))
    print(n,[round(v,1) for v in mn],[round(v,1) for v in mx],hs)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Laundry_inst.002 [1638.6, 53.3, 0.0] [1643.8, 54.1, 2.6] [0.0, 0.44, 1.38, 0.0, 0.44, 1.38, 0.0, 0.4
# 4, 1.38]\nSM_VK_Prop_FishRack_inst [1655.2, 52.9, -0.2] [1658.6, 54.7, 2.0] [0.0, 0.84, 1.5, 0.0, 0.84, 1.5, 0.0, 0.84, 1.5]\nSM_VK_Prop_Cart_inst.008
#  [1576.1, 57.7, 0.0] [1579.8, 60.5, 1.4] [0.0, 0.0, 1.46, 0.0, 0.0, 1.46, 0.0, 0.0, 1.46]\nSM_VK_Prop_Crates_inst.007 [1583.0, 58.2, 0.0] [1585.6, 60.
# 2, 1.5] [0.0, 0.0, 1.36, 0.0, 0.0, 1.36, 0.0, 0.0, 1.36]\n"}

# ==============================================================================================================
# [0016] 2026-09-23 17:52:39  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
L=[("verify_20_laundry_fishrack",(1649,38,9),(1649,53,1.2),30),
("verify_23_lamp_porch",(1646,101,6),(1642.5,95.5,4.2),30),
("verify_24_forester",(1542,70,7),(1536.5,76.5,3.8),30),
("verify_25_chapel",(1640,104,25),(1650,121,4),30),
("verify_26_gate_threshold_side",(1621.5,69,4.2),(1627.5,72.5,2.4),24)]
for n,a,b,l in L: shot(n,a,b,lens=l,outdir=OD)
print('ok')
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0017] 2026-09-23 17:53:52  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
L=[("verify_26_gate_threshold_inside",(1627.5,76.5,4.4),(1627.5,70.5,1.6),28),
("verify_27_west_ramp_side",(1538,67,5.5),(1530,72,2.2),28),
("verify_28_west_stair_road",(1533,86,13),(1527,101,4.5),30),
("verify_29_fisher_access",(1668,12,20),(1686,26,0),28),
("verify_30_lake_east_edge",(1700,30,9),(1716,38,-0.5),30),
("verify_31_bridge_south_willow",(1626,16,9),(1625,31,1),30)]
for n,a,b,l in L: shot(n,a,b,lens=l,outdir=OD)
print('ok')
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0018] 2026-09-23 17:55:27  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
terr=[o for o in bpy.data.collections["VK_ValleyTerrain"].all_objects if o.name.startswith("VKV_Chunk")]
def tb(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return t
T=[tb(o) for o in terr]
def th(x,y):
    best=None
    for t in T:
        h=t.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
        if h[0] and (best is None or h[0].z>best): best=h[0].z
    return best
def bb(n):
    o=bpy.data.objects[n]; ws=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(w[k] for w in ws) for k in range(3)],[max(w[k] for w in ws) for k in range(3)]
for n in ["SM_VK_Corner_Stone_inst.135","SM_VK_Corner_Stone_inst.136","SM_VK_Wall_Stone_Window_inst.136","SM_VK_Prop_Woodpile_inst.004"]:
    if not bpy.data.objects.get(n): print('miss',n); continue
    mn,mx=bb(n); hs=[round(th(mn[0]+fx*(mx[0]-mn[0]),mn[1]+fy*(mx[1]-mn[1])),2) for fx in (0.1,0.5,0.9) for fy in (0.1,0.5,0.9)]
    print(n,[round(v,2) for v in mn],[round(v,2) for v in mx],'minground',min(hs))
# duplicate trees
col=bpy.data.collections["VK_ValleyTown"]
trees=[o for o in col.all_objects if o.name.startswith("SM_VK_Tree_")]
import collections
by=collections.defaultdict(list)
for o in trees: by[o.name.split('_inst')[0]].append(o)
pairs=0; ex=[]
for k,L in by.items():
    for a in range(len(L)):
        for b in range(a+1,len(L)):
            d=(L[a].location.xy-L[b].location.xy).length
            if d<1.0: pairs+=1; ex.append((L[a].name,L[b].name,round(d,2)))
print('trees',len(trees),'same-model pairs<1m',pairs, ex[:6])
q=bpy.data.objects.get("SM_VK_Plant_Reeds_inst.046"); print('reeds046', q and bb(q.name))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Corner_Stone_inst.135 [1655.38, 47.4, -0.06] [1656.65, 48.65, 3.01] minground -0.78\nSM_VK_Corner_Stone_i
# nst.136 [1658.35, 47.38, -0.06] [1659.6, 48.65, 3.01] minground -0.8\nSM_VK_Wall_Stone_Window_inst.136 [1580.98, 47.18, -0.11] [1584.02, 48.28, 3.0] m
# inground -1.04\nSM_VK_Prop_Woodpile_inst.004 [1660.15, 47.1, -0.05] [1661.45, 50.8, 1.47] minground -0.83\ntrees 1241 same-model pairs<1m 43 [('SM_VK_
# Tree_Pine_Young_inst.123', 'SM_VK_Tree_Pine_Young_inst.124', 0.6), ('SM_VK_Tree_Pine_Young_inst.143', 'SM_VK_Tree_Pine_Young_inst.144', 0.48), ('SM_VK
# _Tree_Pine_Young_inst.152', 'SM_VK_Tree_Pine_Young_inst.153', 0.39), ('SM_VK_Tree_Pine_Young_inst.157', 'SM_VK_Tree_Pine_Young_inst.158', 0.38), ('SM_
# VK_Tree_Pine_Young_inst.168', 'SM_VK_Tree_Pine_Young_inst.169', 0.38), ('SM_VK_Tree_Pine_Young_inst.184', 'SM_VK_Tree_Pine_Young_inst.185', 0.53)]\nre

# ==============================================================================================================
# [0019] 2026-09-23 17:55:48  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\verify"
L=[("verify_23_lamp_porch",(1637.5,100.5,5.2),(1642.5,95.5,3.6),30),
("verify_32_smokehouse_corner",(1663,41.5,2.2),(1657.5,48,0.2),30),
("verify_33_brewery_door",(1672.5,106,5),(1672.5,113,2.5),30)]
for n,a,b,l in L: shot(n,a,b,lens=l,outdir=OD)
print('ok')
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0020] 2026-09-23 17:56:31  blender  ok
# ==============================================================================================================
import bpy
print(bpy.data.is_dirty, bpy.data.scenes["VillageKit"].camera and bpy.data.scenes["VillageKit"].camera.name, len(bpy.data.collections["VK_ValleyTown"].all_objects))
# ---- result ----
# {"result":"Code executed successfully: False VK_CameraTown 5568\n"}
