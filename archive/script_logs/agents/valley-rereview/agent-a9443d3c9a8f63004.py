# valley-rereview / agent-a9443d3c9a8f63004.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 19:31:29  blender  ok
# ==============================================================================================================
import bpy, mathutils
sc=bpy.context.scene
dg=bpy.context.evaluated_depsgraph_get()
def h(x,y,ztop=60):
    ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,ztop)),mathutils.Vector((0,0,-1)))
    return (round(loc.z,2),ob.name) if ok else None
def hterr(x,y):
    # terrain only: iterate
    z=60; out=[]
    for k in range(8):
        ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,z)),mathutils.Vector((0,0,-1)))
        if not ok: break
        out.append((round(loc.z,2),ob.name[:28]))
        if ob.name.startswith("VKV_"): break
        z=loc.z-0.01
    return out
res=[]
for x in [1531,1534,1537,1539.5,1541,1545,1549,1552,1555,1558,1561,1565,1568]:
    res.append((x,hterr(x,91.5)))
for r in res: print(r)
# ---- result ----
# {"result":"Code executed successfully: (1531, [(3.0, 'VKV_Chunk_0_1')])\n(1534, [(6.0, 'VKV_Chunk_0_1')])\n(1537, [(6.0, 'VKV_Chunk_0_1')])\n(1539.5, 
# [(6.0, 'SM_VK_LeanTo_inst.010'), (5.86, 'SM_VK_LeanTo_inst.010'), (3.06, 'SM_VK_LeanTo_inst.010'), (3.0, 'VKV_Chunk_0_1')])\n(1541, [(3.0, 'VKV_Chunk_
# 0_1')])\n(1545, [(3.0, 'VKV_Chunk_0_1')])\n(1549, [(3.0, 'VKV_Chunk_1_1')])\n(1552, [(6.0, 'VKV_Chunk_1_1')])\n(1555, [(6.0, 'VKV_Chunk_1_1')])\n(1558
# , [(3.0, 'VKV_Chunk_1_1')])\n(1561, [(3.0, 'VKV_Chunk_1_1')])\n(1565, [(3.0, 'VKV_Chunk_1_1')])\n(1568, [(10.22, 'SM_VK_TownWall_Postern_inst'), (10.1
# , 'SM_VK_TownWall_Postern_inst'), (9.05, 'SM_VK_TownWall_Postern_inst'), (8.72, 'SM_VK_TownWall_Postern_inst'), (8.48, 'SM_VK_TownWall_Postern_inst'),
#  (6.03, 'SM_VK_TownWall_Postern_inst'), (5.7, 'SM_VK_TownWall_Postern_inst'), (3.06, 'SM_VK_TownWall_Postern_inst')])\n"}

# ==============================================================================================================
# [0002] 2026-09-23 19:31:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
p=shot("v01_postern_lane_top",(1548,62,40),(1548,92,4),lens=32,res=(1400,800),outdir=OUT)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v01_postern_lane_top.png\n"}

# ==============================================================================================================
# [0003] 2026-09-23 19:33:05  blender  ok
# ==============================================================================================================
import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects["SM_VK_LeanTo_inst.010"]
cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
print(o.location[:], o.rotation_euler.z, "x",min(c.x for c in cs),max(c.x for c in cs),"y",min(c.y for c in cs),max(c.y for c in cs),"z",min(c.z for c in cs),max(c.z for c in cs))
print(o.parent, o.data.name)
def stack(x,y):
    z=60; out=[]
    for k in range(10):
        ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,z)),mathutils.Vector((0,0,-1)))
        if not ok: break
        out.append((round(loc.z,2),ob.name[:26]))
        if ob.name.startswith("VKV_"): break
        z=loc.z-0.01
    return out
for (x,y) in [(1537.6,92),(1538,92),(1538.5,93),(1538.5,91),(1539.3,91),(1539.3,93.5),(1540.3,92),(1538,90.2)]:
    print((x,y),stack(x,y))
# what quarry objects
q=[ob for ob in bpy.data.collections["VK_ValleyTown"].all_objects if 1530<ob.location.x<1560 and 88<ob.location.y<104]
print(len(q))
for ob in sorted(q,key=lambda a:a.location.y):
    if ob.type=="MESH" and not ob.name.startswith(("SM_VK_Tree","SM_VK_LipGrass","SM_VKT_Lip")): print(ob.name, tuple(round(v,2) for v in ob.location))
# ---- result ----
# {"result":"Code executed successfully: (1539.0, 93.6500015258789, 3.0) 0.0 x 1537.300048828125 1540.699951171875 y 89.84030151367188 93.80894470214844
#  z 3.0 6.530633926391602\nNone VAR_8602771980882169322\n(1537.6, 92) [(6.13, 'SM_VK_LeanTo_inst.010'), (6.0, 'VKV_Chunk_0_1')]\n(1538, 92) [(6.13, 'SM
# _VK_LeanTo_inst.010'), (6.0, 'VKV_Chunk_0_1')]\n(1538.5, 93) [(6.38, 'SM_VK_LeanTo_inst.010'), (6.24, 'SM_VK_LeanTo_inst.010'), (6.0, 'VKV_Chunk_0_1')
# ]\n(1538.5, 91) [(6.0, 'VKV_Chunk_0_1')]\n(1539.3, 91) [(5.88, 'SM_VK_LeanTo_inst.010'), (5.74, 'SM_VK_LeanTo_inst.010'), (3.06, 'SM_VK_LeanTo_inst.01
# 0'), (3.0, 'VKV_Chunk_0_1')]\n(1539.3, 93.5) [(6.5, 'SM_VK_LeanTo_inst.010'), (6.36, 'SM_VK_LeanTo_inst.010'), (3.18, 'SM_VK_Quarry_Face_Straight'), (
# 3.06, 'SM_VK_LeanTo_inst.010'), (3.0, 'VKV_Chunk_0_1')]\n(1540.3, 92) [(6.13, 'SM_VK_LeanTo_inst.010'), (5.99, 'SM_VK_LeanTo_inst.010'), (3.06, 'SM_VK

# ==============================================================================================================
# [0004] 2026-09-23 19:33:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v02_leanto_shoulder",(1546,80,10),(1539,92,4.5),lens=35,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v02_leanto_shoulder.png\n"}

# ==============================================================================================================
# [0005] 2026-09-23 19:34:51  blender  ok
# ==============================================================================================================
import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return (round(min(c.x for c in cs),2),round(max(c.x for c in cs),2),round(min(c.y for c in cs),2),round(max(c.y for c in cs),2),round(min(c.z for c in cs),2),round(max(c.z for c in cs),2))
def stack(x,y):
    z=60; out=[]
    for k in range(10):
        ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,z)),mathutils.Vector((0,0,-1)))
        if not ok: break
        out.append((round(loc.z,2),ob.name[:24]))
        if ob.name.startswith("VKV_Chunk"): break
        z=loc.z-0.01
    return out
for n in ["SM_VK_Prop_BarrelStack_inst.010","SM_VK_Prop_Woodpile_inst.004","SM_VK_Prop_HandPump_inst"]:
    o=bpy.data.objects.get(n)
    if not o: print(n,"missing"); continue
    b=bb(o); print(n,tuple(round(v,2) for v in o.location),b)
    cx=(b[0]+b[1])/2
    for y in [b[2]+0.05,(b[2]+b[3])/2,b[3]-0.05]:
        print("   y",round(y,2),stack(cx,y))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_BarrelStack_inst.010 (1654.6, 48.5, 0.0) (1653.99, 1655.15, 47.54, 49.46, 0.0, 1.5)\n y 47.59 [(0.2,
#  'SM_VK_Prop_BarrelStack_i'), (0.0, 'SM_VK_Prop_BarrelStack_i'), (-0.6, 'VKV_Water_3_1'), (-0.71, 'VKV_Chunk_3_1')]\n y 48.5 [(1.5, 'SM_VK_Prop_Barrel
# Stack_i'), (0.7, 'SM_VK_Prop_BarrelStack_i'), (0.0, 'VKV_Chunk_3_1')]\n y 49.41 [(0.2, 'SM_VK_Prop_BarrelStack_i'), (0.0, 'VKV_Chunk_3_1')]\nSM_VK_Pro
# p_Woodpile_inst.004 (1660.8, 49.3, 0.0) (1660.15, 1661.45, 47.1, 50.8, -0.05, 1.47)\n y 47.15 [(-0.6, 'VKV_Water_3_1'), (-1.2, 'VKV_Chunk_3_1')]\n y 4
# 8.95 [(1.39, 'SM_VK_Prop_Woodpile_inst'), (1.31, 'SM_VK_Prop_Woodpile_inst'), (1.19, 'SM_VK_Prop_Woodpile_inst'), (0.94, 'SM_VK_Prop_Woodpile_inst'), 
# (0.89, 'SM_VK_Prop_Woodpile_inst'), (0.65, 'SM_VK_Prop_Woodpile_inst'), (0.59, 'SM_VK_Prop_Woodpile_inst'), (0.34, 'SM_VK_Prop_Woodpile_inst'), (0.29,

# ==============================================================================================================
# [0006] 2026-09-23 19:35:41  blender  ok
# ==============================================================================================================
import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def first(x,y):
    ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,30)),mathutils.Vector((0,0,-1)))
    return (round(loc.z,2),ob.name[:22]) if ok else None
def terr(x,y):
    z=30
    for k in range(30):
        ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,z)),mathutils.Vector((0,0,-1)))
        if not ok: return None
        if ob.name.startswith("VKV_"): return (round(loc.z,2),ob.name[:12])
        z=loc.z-0.01
for x in [1654.6,1660.8,1645.2,1644.8]:
    row=[]
    for k in range(0,16):
        y=47.0+0.2*k
        row.append((round(y,1),first(x,y),terr(x,y)))
    print(x)
    for r in row: print("  ",r)
# ---- result ----
# {"result":"Code executed successfully: 1654.6\n (47.0, (-0.6, 'VKV_Water_3_1'), (-0.6, 'VKV_Water_3_'))\n (47.2, (-0.6, 'VKV_Water_3_1'), (-0.6, 'VKV_
# Water_3_'))\n (47.4, (-0.6, 'VKV_Water_3_1'), (-0.6, 'VKV_Water_3_'))\n (47.6, (0.2, 'SM_VK_Prop_BarrelStack'), (-0.6, 'VKV_Water_3_'))\n (47.8, (0.7,
#  'SM_VK_Prop_BarrelStack'), (-0.45, 'VKV_Chunk_3_'))\n (48.0, (0.79, 'SM_VK_Prop_BarrelStack'), (-0.11, 'VKV_Chunk_3_'))\n (48.2, (1.35, 'SM_VK_Prop_B
# arrelStack'), (-0.03, 'VKV_Chunk_3_'))\n (48.4, (1.47, 'SM_VK_Prop_BarrelStack'), (-0.01, 'VKV_Chunk_3_'))\n (48.6, (1.47, 'SM_VK_Prop_BarrelStack'), 
# (0.0, 'VKV_Chunk_3_'))\n (48.8, (1.35, 'SM_VK_Prop_BarrelStack'), (-0.0, 'VKV_Chunk_3_'))\n (49.0, (0.79, 'SM_VK_Prop_BarrelStack'), (0.0, 'VKV_Chunk_
# 3_'))\n (49.2, (0.7, 'SM_VK_Prop_BarrelStack'), (0.0, 'VKV_Chunk_3_'))\n (49.4, (0.2, 'SM_VK_Prop_BarrelStack'), (-0.0, 'VKV_Chunk_3_'))\n (49.6, (0.0

# ==============================================================================================================
# [0007] 2026-09-23 19:36:00  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v03_north_bank_props",(1652,38,4.5),(1653,49,0.3),lens=30,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v03_north_bank_props.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 19:37:00  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v04_north_bank_side",(1666,41,2.5),(1656,48.5,0.2),lens=35,res=(1400,800),outdir=OUT))
print(shot("v05_handpump_side",(1640,42,2.2),(1645.2,48.2,0.3),lens=35,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v04_north_bank_side.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rerevie
# w\\verify_ground\\v05_handpump_side.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 19:37:46  blender  ok
# ==============================================================================================================
import bpy, mathutils
tc=bpy.data.collections["VK_ValleyTerrain"]
xs=[];ys=[]
for o in tc.all_objects:
    if o.type!="MESH": continue
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    xs+= [c.x for c in cs]; ys+=[c.y for c in cs]
print("terrain bbox", min(xs),max(xs),min(ys),max(ys))
X0,X1,Y0,Y1=1500,1716,0,168
trees=[o for o in bpy.data.collections["VK_ValleyTown"].all_objects if o.type=="MESH" and o.name.startswith("SM_VK_Tree_")]
res=[]
for o in trees:
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    x0=min(c.x for c in cs);x1=max(c.x for c in cs);y0=min(c.y for c in cs);y1=max(c.y for c in cs)
    ov=max(X0-x0,x1-X1,Y0-y0,y1-Y1)
    tr=min(o.location.x-X0,X1-o.location.x,o.location.y-Y0,Y1-o.location.y)
    res.append((round(ov,2),round(tr,2),o.name,round(o.location.x,2),round(o.location.y,2)))
res.sort(reverse=True)
print(len(trees),"trees; overhang>1:",sum(1 for r in res if r[0]>1),"overhang>0:",sum(1 for r in res if r[0]>0),"trunk<1.5m from edge:",sum(1 for r in res if r[1]<1.5))
for r in res[:12]: print(r)
for r in res:
    if "Willow" in r[2]: print(r)
# ---- result ----
# {"result":"Code executed successfully: terrain bbox 1498.5 1717.5 -1.5 169.5\n705 trees; overhang>1: 118 overhang>0: 140 trunk<1.5m from edge: 59\n(6.
# 59, 0.73, 'SM_VK_Tree_Pine_B_inst.248', 1513.51, 167.27)\n(6.55, 0.4, 'SM_VK_Tree_Pine_B_inst.273', 1706.25, 167.6)\n(6.31, 0.77, 'SM_VK_Tree_Pine_B_i
# nst.265', 1653.33, 167.23)\n(6.24, 1.15, 'SM_VK_Tree_Pine_B_inst.268', 1666.09, 166.85)\n(5.93, 1.21, 'SM_VK_Tree_Pine_B_inst.102', 1501.21, 137.07)\n
# (5.86, 0.37, 'SM_VK_Tree_Pine_B_inst.262', 1624.16, 167.63)\n(5.44, 0.98, 'SM_VK_Tree_Pine_B_inst.263', 1627.13, 167.02)\n(5.39, 1.16, 'SM_VK_Tree_Pin
# e_B_inst.188', 1501.16, 157.33)\n(5.25, 0.82, 'SM_VK_Tree_Pine_A_inst.244', 1501.21, 167.18)\n(5.14, 1.01, 'SM_VK_Tree_Pine_B_inst.081', 1501.01, 124.
# 67)\n(5.1, 1.74, 'SM_VK_Tree_Pine_B_inst.272', 1697.27, 166.26)\n(5.09, 1.2, 'SM_VK_Tree_Pine_B_inst.250', 1522.06, 166.8)\n(4.67, 1.1, 'SM_VK_Tree_Wi

# ==============================================================================================================
# [0010] 2026-09-23 19:38:29  blender  ok
# ==============================================================================================================
import bpy, mathutils
X0,X1,Y0,Y1=1498.5,1717.5,-1.5,169.5
trees=[o for o in bpy.data.collections["VK_ValleyTown"].all_objects if o.type=="MESH" and o.name.startswith("SM_VK_Tree_")]
res=[]
from collections import Counter
for o in trees:
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    x0=min(c.x for c in cs);x1=max(c.x for c in cs);y0=min(c.y for c in cs);y1=max(c.y for c in cs)
    ov=max(X0-x0,x1-X1,Y0-y0,y1-Y1)
    res.append((round(ov,2),o.name))
print("overhang>1 vs terrain edge:",sum(1 for r in res if r[0]>1), Counter(r[1].split("_inst")[0] for r in res if r[0]>1))
for n in ["SM_VK_Tree_Pine_B","SM_VK_Tree_Willow","SM_VK_Tree_Pine_A"]:
    o=bpy.data.objects.get(n)
    if o: print(n,[round(v,2) for v in o.dimensions])
o=bpy.data.objects["SM_VK_Tree_Willow_inst.001"]; print("willow1 scale",o.scale[:],o.dimensions[:], o.location[:])
o=bpy.data.objects["SM_VK_Tree_Pine_B_inst.248"]; print("pineB248",o.scale[:],o.dimensions[:], o.location[:], o.data.name)
# ---- result ----
# {"result":"Code executed successfully: overhang>1 vs terrain edge: 66 Counter({'SM_VK_Tree_Pine_B': 34, 'SM_VK_Tree_Pine_A': 24, 'SM_VK_Tree_Pine_Youn
# g': 3, 'SM_VK_Tree_Oak_B': 2, 'SM_VK_Tree_Willow': 1, 'SM_VK_Tree_Oak_A': 1, 'SM_VK_Tree_Oak_Autumn': 1})\nSM_VK_Tree_Pine_B [8.84, 9.58, 13.42]\nSM_V
# K_Tree_Willow [8.63, 8.56, 5.45]\nSM_VK_Tree_Pine_A [8.03, 7.97, 10.33]\nwillow1 scale (1.0, 1.0, 1.0) (8.63470458984375, 8.564515113830566, 5.4506411
# 5524292) (1714.89794921875, 22.272289276123047, 0.0)\npineB248 (1.1360453367233276, 1.1360453367233276, 1.1360453367233276) (10.045690536499023, 10.88
# 2810592651367, 15.248611450195312) (1513.5107421875, 167.2670440673828, 7.5) SM_VK_Tree_Pine_B\n"}

# ==============================================================================================================
# [0011] 2026-09-23 19:39:02  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v06_east_edge_willow",(1735,10,14),(1714,22,2),lens=35,res=(1400,800),outdir=OUT))
print(shot("v07_north_edge_pines",(1515,195,25),(1515,165,8),lens=30,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v06_east_edge_willow.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rerevi
# ew\\verify_ground\\v07_north_edge_pines.png\n"}

# ==============================================================================================================
# [0012] 2026-09-23 19:39:51  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v08_east_edge_willow_top",(1712,21.9,40),(1712,22,0),lens=35,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v08_east_edge_willow_top.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 19:41:15  blender  ok
# ==============================================================================================================
import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def terr(x,y):
    z=30
    for k in range(30):
        ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,z)),mathutils.Vector((0,0,-1)))
        if not ok: return None
        if ob.name.startswith("VKV_"): return round(loc.z,2)
        z=loc.z-0.01
o=bpy.data.objects["SM_VK_Prop_DryingRack_Herbs_inst"]
cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
print(o.location[:], [round(v,2) for v in (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs))], round(math.degrees(o.rotation_euler.z),1) if False else o.rotation_euler.z)
for y in [56.5,57.5,58.5,59.5,60.5,61,61.5,62,62.5,63]:
    print(y,[terr(x,y) for x in [1571.5,1572.5,1573.2,1574,1575,1576,1577,1577.8,1578.5]])
# neighbours near the ramp top
for ob in bpy.data.collections["VK_ValleyTown"].all_objects:
    if ob.type=="MESH" and 1568<ob.location.x<1582 and 58<ob.location.y<68:
        print(ob.name, tuple(round(v,2) for v in ob.location))
# ---- result ----
# {"result":"Code executed successfully: (1574.5, 62.599998474121094, 1.5) [1574.06, 1574.94, 61.76, 63.44] -1.5707963705062866\n56.5 [0.0, -0.0, 0.0, 0
# .0, 0.0, 0.0, 0.0, 0.0, 0.0]\n57.5 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]\n58.5 [-0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]\n59.5 [0.0, 0.5,
#  0.5, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0]\n60.5 [1.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 1.5]\n61 [1.5, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.5, 1.5]\n61.5 
# [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\n62 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\n62.5 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\n6
# 3 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\nSM_VK_Prop_Dovecote_inst (1573.0, 66.85, 1.5)\nSM_VK_Prop_BeeBench_inst.001 (1570.45, 64.05, 1.5)\nSM
# _VK_Prop_Stool_inst.018 (1568.1, 62.4, 1.5)\nSM_VK_Prop_Skep_inst.001 (1568.1, 62.4, 2.04)\nSM_VK_Prop_Stool_inst.019 (1569.6, 62.4, 1.5)\nSM_VK_Prop_

# ==============================================================================================================
# [0014] 2026-09-23 19:42:51  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v09_mill_ramp_mouth",(1575,49,7),(1575,61,1.2),lens=30,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v09_mill_ramp_mouth.png\n"}

# ==============================================================================================================
# [0015] 2026-09-23 19:43:27  blender  ok
# ==============================================================================================================
import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def first(x,y):
    ok,loc,n,idx,ob,m=sc.ray_cast(dg,mathutils.Vector((x,y,40)),mathutils.Vector((0,0,-1)))
    return (round(loc.z,2),ob.name[:24]) if ok else None
for n in ["SM_VK_Bush_Round_inst.038","SM_VK_Bush_Round_inst.025"]:
    o=bpy.data.objects[n]
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    print(n,tuple(round(v,2) for v in o.location),o.scale[:],[round(v,2) for v in (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs),max(c.z for c in cs))])
o=bpy.data.objects.get("SM_VK_Bush_Round"); print("master dims",o.dimensions[:] if o else None)
print("street row30 hits for bush038:")
for y in [90.5,91.0,91.5,92.0,92.5,93.0]:
    print(y,[ (x,first(x,y)) for x in [1584.0,1584.8,1585.7,1586.5,1587.2]])
print("river road row9 hits for bush025:")
o=bpy.data.objects["SM_VK_Bush_Round_inst.025"]
for y in [27.0,27.4,27.8,28.2,28.6]:
    print(y,[(x,first(x,y)) for x in [1581.5,1582.3,1582.9,1583.6,1584.3]])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Bush_Round_inst.038 (1585.68, 93.33, 3.0) (1.0, 1.0, 1.0) [1583.75, 1587.54, 91.48, 95.29, 4.86]\nSM_VK_B
# ush_Round_inst.025 (1582.88, 26.37, 1.5) (1.0, 1.0, 1.0) [1581.06, 1584.61, 24.61, 28.23, 3.36]\nmaster dims (2.7767176628112793, 2.6462526321411133, 
# 2.5448999404907227)\nstreet row30 hits for bush038:\n90.5 [(1584.0, (15.91, 'SM_VK_Turret_Cap_inst')), (1584.8, (16.73, 'SM_VK_Turret_Cap_inst')), (15
# 85.7, (14.88, 'SM_VK_Turret_Cap_inst')), (1586.5, (3.0, 'VKV_Chunk_1_1')), (1587.2, (3.0, 'VKV_Chunk_1_1'))]\n91.0 [(1584.0, (15.68, 'SM_VK_Turret_Cap
# _inst')), (1584.8, (16.26, 'SM_VK_Turret_Cap_inst')), (1585.7, (14.75, 'SM_VK_Turret_Cap_inst')), (1586.5, (3.0, 'VKV_Chunk_1_1')), (1587.2, (3.0, 'VK
# V_Chunk_1_1'))]\n91.5 [(1584.0, (14.91, 'SM_VK_Turret_Cap_inst')), (1584.8, (15.25, 'SM_VK_Turret_Cap_inst')), (1585.7, (14.35, 'SM_VK_Turret_Cap_inst

# ==============================================================================================================
# [0016] 2026-09-23 19:44:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v10_bush_postern_street",(1592,84,12),(1585.5,92.5,3.2),lens=32,res=(1400,800),outdir=OUT))
print(shot("v11_bush_river_road",(1583,18,9),(1583,27.5,1.6),lens=32,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v10_bush_postern_street.png\nC:\\Users\\danie\\AppData\\Roa
# ming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rer
# eview\\verify_ground\\v11_bush_river_road.png\n"}

# ==============================================================================================================
# [0017] 2026-09-23 19:44:36  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_ground"
print(shot("v12_bush_postern_street_top",(1585.5,101,22),(1585.5,92,3),lens=32,res=(1400,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_ground\\v12_bush_postern_street_top.png\n"}

# ==============================================================================================================
# [0018] 2026-09-23 19:45:29  blender  ok
# ==============================================================================================================
import bpy, mathutils, numpy as np
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects["SM_VK_Bush_Round_inst.038"]
# evaluated mesh vertices in world
ev=o.evaluated_get(dg); me=ev.to_mesh()
V=np.array([o.matrix_world@v.co for v in me.vertices]); ev.to_mesh_clear()
print("bush038 mesh x",V[:,0].min().round(2),V[:,0].max().round(2),"y",V[:,1].min().round(2),V[:,1].max().round(2),"z",V[:,2].min().round(2),V[:,2].max().round(2))
print("verts with y<93:",int((V[:,1]<93).sum()),"of",len(V), " y<92.5:",int((V[:,1]<92.5).sum()))
o=bpy.data.objects["SM_VK_Bush_Round_inst.025"]
ev=o.evaluated_get(dg); me=ev.to_mesh()
V=np.array([o.matrix_world@v.co for v in me.vertices]); ev.to_mesh_clear()
print("bush025 mesh y max",V[:,1].max().round(2), "verts y>27:",int((V[:,1]>27).sum()),"of",len(V))
# roads mask reconstruction (ground 1/2 from town_grid lines) for scatter bushes overlapping roads
W,H=72,56
R=np.zeros((H,W),bool)
R[0:32,41:43]=True; R[31:36,36:48]=True; R[39:42,24:41]=True; R[36:39,39:41]=True; R[36:39,47:52]=True; R[29,44:62]=True
R[30,23:41]=True; R[30,11:23]=True; R[9,11:41]=True; R[9:34,9:11]=True
R[12:16,:]=R[12:16,:]&False  # rough; water rows excluded
cnt=[]
for b in bpy.data.collections["VK_ValleyTown"].all_objects:
    n=b.name.split("_inst")[0]
    if n not in ("SM_VK_Bush_Round","SM_VK_Bush_Large","SM_VK_Bush_Hydrangea"): continue
    x=b.location.x-1500; y=b.location.y; r=1.3 if n=="SM_VK_Bush_Round" else 1.6
    worst=0
    for jj in range(int((y-r)//3),int((y+r)//3)+1):
        for ii in range(int((x-r)//3),int((x+r)//3)+1):
            if 0<=ii<W and 0<=jj<H and R[jj,ii]:
                dx=max(3*ii-x,0,x-(3*ii+3)); dy=max(3*jj-y,0,y-(3*jj+3))
                d=(dx*dx+dy*dy)**0.5
                if d<r: worst=max(worst,r-d)
    if worst>0.5: cnt.append((round(worst,2),b.name,round(b.location.x,1),round(y,1)))
cnt.sort(reverse=True); print(len(cnt)); print(cnt[:12])
# ---- result ----
# {"result":"Code executed successfully: bush038 mesh x 1584.34 1587.22 y 92.03 94.74 z 2.31 4.86\nverts with y<93: 170 of 735 y<92.5: 38\nbush025 mesh 
# y max 27.85 verts y>27: 99 of 735\n2\n[(0.97, 'SM_VK_Bush_Round_inst.038', 1585.7, 93.3), (0.67, 'SM_VK_Bush_Round_inst.025', 1582.9, 26.4)]\n"}
