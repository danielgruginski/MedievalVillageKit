# valley-rereview / agent-ad3b9a1ab2e178f2e.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 18:47:35  blender  ok
# ==============================================================================================================
import bpy
print(bpy.app.version_string)
t=bpy.data.texts.get("vk_render")
print(t.as_string()[:3000] if t else "no vk_render")
# ---- result ----
# {"result":"Code executed successfully: 4.4.3\nimport bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratc
# h-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,tar
# get,lens=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if 
# cam is None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.o
# bjects.link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data
# .clip_end=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.

# ==============================================================================================================
# [0002] 2026-09-23 18:47:58  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace
print([k for k in ns.keys()][:80])
for c in ("VK_ValleyTown","VK_ValleyTerrain"):
    cc=bpy.data.collections.get(c); print(c, len(cc.all_objects) if cc else None)
g=[o for o in bpy.data.objects if o.name.startswith("SM_VK_Gatehouse_Block_inst")]
for o in g: print(o.name,tuple(round(v,2) for v in o.location), o.rotation_euler.z)
# ---- result ----
# {"result":"Code executed successfully: ['__builtins__', '__name__', '__doc__', '__package__', '__loader__', '__spec__', 'acos', 'acosh', 'asin', 'asin
# h', 'atan', 'atan2', 'atanh', 'cbrt', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'dist', 'erf', 'erfc', 'exp', 'exp2', 'expm1', 'fabs', 'factorial'
# , 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'gcd', 'hypot', 'isclose', 'isfinite', 'isinf', 'isnan', 'isqrt', 'lcm', 'ldexp', 'lgamma', 'log', 'log1p
# ', 'log10', 'log2', 'modf', 'pow', 'radians', 'remainder', 'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'trunc', 'prod', 'perm', 'comb', 'nextafter', 'ulp', 
# 'pi', 'e', 'tau', 'inf', 'nan', 'bpy', 'noise', 'clamp', 'lerp', 'smoothstep', 'builder_bounds', 'town', 'shot', 'rv_ground_bvh', 'rv_water_bvh', 'rv_
# res', 'colony', 'rv_nat', 'rv_natrows']\nVK_ValleyTown 4584\nVK_ValleyTerrain 30\nSM_VK_Gatehouse_Block_inst (1626.0, 75.0, 3.0) 0.0\n"}

# ==============================================================================================================
# [0003] 2026-09-23 18:48:15  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace
t=ns['town']; print(type(t))
try:
    print(len(t)); print([type(x) for x in t])
except Exception as e: print(e)
for k in ('rv_ground_bvh','rv_water_bvh','rv_res','rv_nat','rv_natrows','builder_bounds','colony'):
    print(k,type(ns[k]))
# ---- result ----
# {"result":"Code executed successfully: <class 'tuple'>\n2\n[<class 'TGrid'>, <class 'TownPlacer'>]\nrv_ground_bvh <class 'BVHTree'>\nrv_water_bvh <cla
# ss 'BVHTree'>\nrv_res <class 'dict'>\nrv_nat <class 'dict'>\nrv_natrows <class 'list'>\nbuilder_bounds <class 'dict'>\ncolony <class 'function'>\n"}

# ==============================================================================================================
# [0004] 2026-09-23 18:49:13  blender  ok
# ==============================================================================================================
import bpy, numpy as np
G,T=bpy.app.driver_namespace['town']
print(G.level[23,38:46], G.ramp[22,38:46], G.ramp[10,8:12], G.ramp[17,8:12], G.ramp[33,8:11], G.stair[33,8:11], G.ramp[19,22:28], G.ramp[5,64:69])
print(len(T.log))
for l in T.log: print(str(l)[:300])
# ---- result ----
# {"result":"Code executed successfully: [1 1 1 1 1 1 1 1] [0 0 0 0 0 0 0 0] [0 0 0 0] [0 0 0 0] [0 0 0] [False False False] [0 0 0 0 0 0] [0 0 0 0 0]\n
# 10\n('watermill', 8, [('lvl', 25, 19, 1), ('lvl', 26, 19, 1), ('lvl', 27, 19, 1), ('lvl', 28, 19, 1), ('lvl', 25, 20, 1), ('lvl', 26, 20, 1)])\n('smok
# ehouse', 3, [('lvl', 51, 18, 1), ('lvl', 52, 18, 1), ('lvl', 53, 18, 1)])\n('fisher_hut', 6, [('lvl', 61, 5, 1), ('lvl', 62, 5, 1), ('lvl', 63, 5, 1),
#  ('lvl', 64, 5, 1), ('lvl', 65, 5, 1), ('lvl', 66, 5, 1)])\n('training', 2, [('occ', 61, 5, 4), ('occ', 62, 5, 4)])\n('windmill', 7, [('occ', 27, 19, 
# 1), ('occ', 28, 19, 1), ('occ', 27, 20, 1), ('occ', 28, 20, 1), ('occ', 32, 20, 19), ('occ', 32, 21, 19)])\n('site1', 5, [('occ', 48, 19, 22), ('occ',
#  48, 20, 22), ('occ', 48, 21, 22), ('occ', 48, 22, 22), ('occ', 48, 23, 22)])\n('site2', 5, [('occ', 53, 19, 23), ('occ', 53, 20, 23), ('occ', 53, 21,

# ==============================================================================================================
# [0005] 2026-09-23 18:49:35  blender  ok
# ==============================================================================================================
import bpy, numpy as np, math, re
G0,T0=bpy.app.driver_namespace['town']
TG=type(G0)
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_town_map.py").read()
s=src.index("TOWN_W,TOWN_H"); e=src.index("# ---------------------------------------------------------------- placement")
ns={"np":np,"math":math,"TGrid":TG,"bpy":bpy,"random":__import__("random"),"re":re}
exec(src[s:e],ns)
G=ns['town_grid'](11)
bpy.app.driver_namespace['rr_ground_G']=G
print(G.level[23,38:46], G.ramp[22,38:46], G.ramp[10,8:12], G.ramp[17,8:12], G.ramp[33,8:11], G.stair[33,8:11], G.ramp[19,22:28], G.ramp[5,64:69])
tc=bpy.data.collections["VK_ValleyTerrain"]
for o in tc.all_objects: print(o.name, o.type, len(o.data.polygons) if o.type=='MESH' else '', [round(v,1) for v in o.location])
# ---- result ----
# {"result":"Code executed successfully: [1 1 2 2 2 2 1 1] [0 0 0 1 1 0 0 0] [0 3 3 0] [0 1 1 0] [0 1 0] [False True False] [0 0 1 1 0 0] [0 0 3 3 0]\nV
# KV_Chunk_0_0 MESH 13558 [1500.0, 0.0, 0.0]\nVKV_Water_0_0 MESH 64 [1500.0, 0.0, 0.0]\nVKV_Chunk_1_0 MESH 13728 [1500.0, 0.0, 0.0]\nVKV_Water_1_0 MESH 
# 64 [1500.0, 0.0, 0.0]\nVKV_Chunk_2_0 MESH 13558 [1500.0, 0.0, 0.0]\nVKV_Water_2_0 MESH 64 [1500.0, 0.0, 0.0]\nVKV_Chunk_3_0 MESH 14640 [1500.0, 0.0, 0
# .0]\nVKV_Water_3_0 MESH 83 [1500.0, 0.0, 0.0]\nVKV_Chunk_4_0 MESH 8174 [1500.0, 0.0, 0.0]\nVKV_Water_4_0 MESH 63 [1500.0, 0.0, 0.0]\nVKV_Chunk_0_1 MES
# H 17528 [1500.0, 0.0, 0.0]\nVKV_Water_0_1 MESH 16 [1500.0, 0.0, 0.0]\nVKV_Chunk_1_1 MESH 18246 [1500.0, 0.0, 0.0]\nVKV_Water_1_1 MESH 16 [1500.0, 0.0,
#  0.0]\nVKV_Chunk_2_1 MESH 16304 [1500.0, 0.0, 0.0]\nVKV_Water_2_1 MESH 16 [1500.0, 0.0, 0.0]\nVKV_Chunk_3_1 MESH 16528 [1500.0, 0.0, 0.0]\nVKV_Water_3

# ==============================================================================================================
# [0006] 2026-09-23 18:50:02  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils.bvhtree import BVHTree
tc=bpy.data.collections["VK_ValleyTerrain"]
def bvh(objs):
    V=[];F=[];off=0
    for o in objs:
        me=o.data; mw=o.matrix_world
        co=np.empty(len(me.vertices)*3); me.vertices.foreach_get("co",co); co=co.reshape(-1,3)
        co=co+np.array(mw.translation)
        V.extend(map(tuple,co))
        for p in me.polygons: F.append([v+off for v in p.vertices])
        off+=len(co)
    return BVHTree.FromPolygons(V,F)
ch=[o for o in tc.all_objects if "Chunk" in o.name]; wa=[o for o in tc.all_objects if "Water" in o.name]
bpy.app.driver_namespace['rr_gb']=bvh(ch); bpy.app.driver_namespace['rr_wb']=bvh(wa)
print("ok", all(o.matrix_world.to_3x3().is_identity for o in ch+wa) if hasattr(ch[0].matrix_world.to_3x3(),'is_identity') else [tuple(o.matrix_world.to_3x3()[0]) for o in ch[:1]])
# ---- result ----
# {"result":"Code executed successfully: ok True\n"}

# ==============================================================================================================
# [0007] 2026-09-23 18:50:30  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace
gb=ns['rr_gb']
def h(x,y,z0=60):
    r=gb.ray_cast(Vector((x,y,z0)),Vector((0,0,-1)),200)
    return round(r[0].z,2) if r[0] else None
ns['rr_h']=h
for x in (1623.3,1624.5,1626,1627.5,1628.7):
    print(x,[h(x,y) for y in [63,65,66,66.5,67,67.5,68,68.5,69,69.5,70,71,72,73,74,76,78]])
gh=[o for o in bpy.data.collections['VK_ValleyTown'].all_objects if 'Gate' in o.name or 'Portcullis' in o.name]
for o in gh:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(o.name,[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])
# ---- result ----
# {"result":"Code executed successfully: 1623.3 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2.88, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]\n1624.5 [1.5, 1.5
# , 1.5, 1.5, 1.5, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]\n1626 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 
# 3.0, 3.0, 3.0, 3.0, 3.0]\n1627.5 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]\n1628.7 [1.5, 1.5, 1.5, 1.5,
#  1.5, 1.5, 1.5, 1.5, 2.88, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Gatehouse_Block_inst [1620.69, 69.68, 1.5] [1631.33, 78.25, 12.0]\nSM_VK_Gat
# ehouse_Portcullis_inst [1624.29, 72.5, 5.16] [1627.84, 72.71, 9.9]\nSM_VK_Gatehouse_GateLeaf_inst [1624.18, 73.69, 3.02] [1624.93, 75.38, 7.36]\nSM_VK
# _Gatehouse_GateLeaf_inst.001 [1627.07, 73.69, 3.02] [1627.82, 75.38, 7.36]\nSM_VK_Prop_FenceGate_inst.020 [1529.82, 2.9, 1.5] [1530.1, 6.1, 2.8]\nSM_V

# ==============================================================================================================
# [0008] 2026-09-23 18:51:02  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ns=bpy.app.driver_namespace; h=ns['rr_h']
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['SM_VK_Gatehouse_Block_inst']
b=BVHTree.FromObject(o,dg)
mwi=o.matrix_world.inverted()
def hitdown(x,y,z0):
    p=mwi@Vector((x,y,z0)); r=b.ray_cast(p,Vector((0,0,-1)),20)
    return round((o.matrix_world@r[0]).z,2) if r[0] else None
for x in (1625,1626,1627):
    print(x,[(y,hitdown(x,y,5.0),h(x,y)) for y in (69.5,69.8,70.2,70.6,71,71.5,72,73,75,77,78)])
# passage width at z=4, y=75
def hitside(y,z):
    out=[]
    for d in (Vector((1,0,0)),Vector((-1,0,0))):
        p=mwi@Vector((1626,y,z)); r=b.ray_cast(p,o.matrix_world.inverted().to_3x3()@d,20)
        out.append(round((o.matrix_world@r[0]).x,2) if r[0] else None)
    return out
for y in (70,71,72,74,76,78): print('side',y,hitside(y,4.0))
# ---- result ----
# {"result":"Code executed successfully: 1625 [(69.5, None, 2.5), (69.8, None, 2.65), (70.2, None, 2.85), (70.6, None, 3.0), (71, 3.24, 3.0), (71.5, 3.3
# 1, 3.0), (72, 3.36, 3.0), (73, 3.04, 3.0), (75, 3.04, 3.0), (77, 3.04, 3.0), (78, 3.04, 3.0)]\n1626 [(69.5, None, 2.5), (69.8, None, 2.65), (70.2, Non
# e, 2.85), (70.6, None, 3.0), (71, None, 3.0), (71.5, None, 3.0), (72, 3.04, 3.0), (73, 3.04, 3.0), (75, 3.04, 3.0), (77, 3.04, 3.0), (78, 3.04, 3.0)]\
# n1627 [(69.5, None, 2.5), (69.8, None, 2.65), (70.2, None, 2.85), (70.6, None, 3.0), (71, 3.29, 3.0), (71.5, 3.33, 3.0), (72, 3.36, 3.0), (73, 3.04, 3
# .0), (75, 3.04, 3.0), (77, 3.04, 3.0), (78, 3.04, 3.0)]\nside 70 [None, None]\nside 71 [1627.41, 1624.59]\nside 72 [1627.09, 1624.91]\nside 74 [1627.6
# , 1624.4]\nside 76 [1627.6, 1624.4]\nside 78 [None, None]\n"}

# ==============================================================================================================
# [0009] 2026-09-23 18:51:27  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
t=time.time()
p=shot("g01_gate",(1638,52,14),(1626,71,3.5),lens=30,res=(1280,720),outdir=OD)
print(p, time.time()-t, bpy.data.scenes['VillageKit'].render.engine)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g01_gate.png 3.358121633529663 BLENDER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0010] 2026-09-23 18:51:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g02_gate_ramp_east",(1634,62,5.5),(1628.5,69.5,2.2),lens=35,res=(1280,720),outdir=OD))
print(shot("g03_gate_ramp_west",(1617,62,5.5),(1623.3,69.5,2.2),lens=35,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g02_gate_ramp_east.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude
# \\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\groun
# d\\g03_gate_ramp_west.png\n"}

# ==============================================================================================================
# [0011] 2026-09-23 18:52:43  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g04_gate_ramp_topcorners",(1626,63.5,7.5),(1626,70.3,2.8),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g04_gate_ramp_topcorners.png\n"}

# ==============================================================================================================
# [0012] 2026-09-23 18:53:36  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; h=ns['rr_h']
for x in (1527.5,1530,1532.5):
    print(x,[(y,h(x,y)) for y in range(24,60,1)])
vt=bpy.data.collections['VK_ValleyTown']
for o in vt.all_objects:
    if 'Bridge_Wood' in o.name:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print(o.name,[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])
# ---- result ----
# {"result":"Code executed successfully: 1527.5 [(24, 1.5), (25, 1.5), (26, 1.5), (27, 1.5), (28, 1.5), (29, 1.25), (30, 0.75), (31, 0.25), (32, 0.0), (
# 33, 0.0), (34, -0.0), (35, 0.0), (36, -0.27), (37, -1.32), (38, -1.5), (39, -1.5), (40, -1.5), (41, -1.5), (42, -1.5), (43, -1.5), (44, -1.5), (45, -1
# .5), (46, -1.5), (47, -1.5), (48, -0.35), (49, 0.0), (50, 0.0), (51, -0.0), (52, 0.0), (53, 0.25), (54, 0.75), (55, 1.25), (56, 1.5), (57, 1.5), (58, 
# 1.5), (59, 1.5)]\n1530 [(24, 1.5), (25, 1.5), (26, 1.5), (27, 1.5), (28, 1.5), (29, 1.25), (30, 0.75), (31, 0.25), (32, 0.0), (33, 0.0), (34, 0.0), (3
# 5, 0.0), (36, -0.38), (37, -1.47), (38, -1.5), (39, -1.5), (40, -1.5), (41, -1.5), (42, -1.5), (43, -1.5), (44, -1.5), (45, -1.5), (46, -1.5), (47, -1
# .45), (48, -0.24), (49, 0.0), (50, 0.0), (51, 0.0), (52, 0.0), (53, 0.25), (54, 0.75), (55, 1.25), (56, 1.5), (57, 1.5), (58, 1.5), (59, 1.5)]\n1532.5

# ==============================================================================================================
# [0013] 2026-09-23 18:54:03  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g05_footbridge_overview",(1552,20,28),(1530,43,0),lens=30,res=(1280,720),outdir=OD))
print(shot("g06_footbridge_southramp",(1541,24,6),(1530,32,0.5),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g05_footbridge_overview.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\
# ground\\g06_footbridge_southramp.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 18:55:08  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g07_footbridge_sramp_westcorner",(1534,27,3.5),(1526.8,30.5,0.8),lens=35,res=(1280,720),outdir=OD))
print(shot("g08_footbridge_sramp_from_river",(1531,40,3.0),(1529,30,0.5),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g07_footbridge_sramp_westcorner.png\nC:\\Users\\danie\\AppData\\Ro
# aming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\re
# review\\ground\\g08_footbridge_sramp_from_river.png\n"}

# ==============================================================================================================
# [0015] 2026-09-23 18:56:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g09_bench_ramp_row23",(1536,60,6),(1530,70.5,2.0),lens=30,res=(1280,720),outdir=OD))
print(shot("g10_bench_ramp_row23_west",(1522,62,4.5),(1527.5,70.5,2.0),lens=35,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g09_bench_ramp_row23.png\nC:\\Users\\danie\\AppData\\Roaming\\Clau
# de\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\gro
# und\\g10_bench_ramp_row23_west.png\n"}

# ==============================================================================================================
# [0016] 2026-09-23 18:57:03  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; gb=ns['rr_gb']
def hits(x,y):
    out=[];z=60.0
    for _ in range(6):
        r=gb.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),200)
        if not r[0]: break
        out.append((round(r[0].z,2),round(r[1].z,2))); z=r[0].z-0.001
    return out
for x in (1526.6,1526.9,1527.2,1527.5,1532.5,1532.8,1533.1,1533.4):
    print(x,[(y,hits(x,y)) for y in (70.5,71.0,71.5,72.0,72.5,73.0)])
# ---- result ----
# {"result":"Code executed successfully: 1526.6 [(70.5, [(1.5, 1.0)]), (71.0, [(1.5, 1.0)]), (71.5, [(1.5, 1.0)]), (72.0, [(2.88, 0.84), (2.79, -0.55), 
# (2.67, 0.21), (1.52, -0.81), (1.5, 1.0)]), (72.5, [(3.0, 1.0), (1.5, 1.0)]), (73.0, [(3.0, 1.0), (1.5, 1.0)])]\n1526.9 [(70.5, [(1.5, 1.0)]), (71.0, [
# (1.5, 1.0)]), (71.5, [(1.5, 1.0)]), (72.0, [(2.88, 0.84), (2.79, -0.55), (2.67, 0.21), (1.52, -0.81), (1.5, 1.0)]), (72.5, [(3.0, 1.0), (1.5, 1.0)]), 
# (73.0, [(3.0, 1.0), (1.5, 1.0)])]\n1527.2 [(70.5, [(1.5, 1.0)]), (71.0, [(1.5, 1.0)]), (71.5, [(1.5, 1.0)]), (72.0, [(2.88, 0.84), (2.79, -0.55), (2.6
# 7, 0.21), (1.52, -0.81), (1.5, 1.0)]), (72.5, [(3.0, 1.0), (1.5, 1.0)]), (73.0, [(3.0, 1.0), (1.5, 1.0)])]\n1527.5 [(70.5, [(1.5, 1.0)]), (71.0, [(1.7
# 5, 0.89), (1.5, 1.0)]), (71.5, [(2.0, 0.89), (1.5, 1.0)]), (72.0, [(2.25, 0.89), (1.5, 1.0)]), (72.5, [(2.5, 0.89), (1.5, 1.0)]), (73.0, [(2.75, 0.89)

# ==============================================================================================================
# [0017] 2026-09-23 18:57:29  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace; h=ns['rr_h']
import numpy as np
for y in (70.8,71.5,72.2,73.0,73.6):
    print('bench',y,[(round(x,1),h(x,y)) for x in np.arange(1526,1534.1,0.5)])
for y in (67.5,68.5,69.5,70.5):
    print('gate',y,[(round(x,1),h(x,y)) for x in np.arange(1622,1630.1,0.5)])
# ---- result ----
# {"result":"Code executed successfully: bench 70.8 [(1526.0, 1.5), (1526.5, 1.5), (1527.0, 1.5), (1527.5, 1.65), (1528.0, 1.65), (1528.5, 1.65), (1529.
# 0, 1.65), (1529.5, 1.65), (1530.0, 1.65), (1530.5, 1.65), (1531.0, 1.65), (1531.5, 1.65), (1532.0, 1.65), (1532.5, 1.5), (1533.0, 1.5), (1533.5, 1.5),
#  (1534.0, 1.5)]\nbench 71.5 [(1526.0, 1.5), (1526.5, 1.5), (1527.0, 1.5), (1527.5, 2.0), (1528.0, 2.0), (1528.5, 2.0), (1529.0, 2.0), (1529.5, 2.0), (
# 1530.0, 2.0), (1530.5, 2.0), (1531.0, 2.0), (1531.5, 2.0), (1532.0, 2.0), (1532.5, 1.5), (1533.0, 1.5), (1533.5, 1.5), (1534.0, 1.5)]\nbench 72.2 [(15
# 26.0, 2.97), (1526.5, 2.97), (1527.0, 2.97), (1527.5, 2.35), (1528.0, 2.35), (1528.5, 2.35), (1529.0, 2.35), (1529.5, 2.35), (1530.0, 2.35), (1530.5, 
# 2.35), (1531.0, 2.35), (1531.5, 2.35), (1532.0, 2.35), (1532.5, 2.97), (1533.0, 2.97), (1533.5, 2.97), (1534.0, 2.97)]\nbench 73.0 [(1526.0, 3.0), (15

# ==============================================================================================================
# [0018] 2026-09-23 18:58:06  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
ns=bpy.app.driver_namespace; h=ns['rr_h']
import numpy as np
for x in (1526.5,1527.5,1528.5,1529.5,1530.5,1531.5):
    print(x,[(y,h(x,y)) for y in (96,98,99,100,100.5,101,101.5,102,102.5,103,104,105)])
vt=bpy.data.collections['VK_ValleyTown']
near=[]
for o in vt.all_objects:
    if o.type!='MESH': continue
    x,y=o.location.x,o.location.y
    if 1522<x<1537 and 96<y<110: near.append((o.name,round(x,2),round(y,2),round(o.location.z,2)))
for n in sorted(near,key=lambda t:t[2]): print(n)
# ---- result ----
# {"result":"Code executed successfully: 1526.5 [(96, 3.0), (98, 3.0), (99, 3.0), (100, 3.0), (100.5, 3.0), (101, 3.0), (101.5, 3.0), (102, 4.38), (102.
# 5, 4.5), (103, 4.5), (104, 4.5), (105, 4.5)]\n1527.5 [(96, 3.0), (98, 3.0), (99, 3.0), (100, 3.0), (100.5, 3.0), (101, 3.25), (101.5, 3.5), (102, 3.75
# ), (102.5, 4.0), (103, 4.25), (104, 4.5), (105, 4.5)]\n1528.5 [(96, 3.0), (98, 3.0), (99, 3.0), (100, 3.0), (100.5, 3.0), (101, 3.25), (101.5, 3.5), (
# 102, 3.75), (102.5, 4.0), (103, 4.25), (104, 4.5), (105, 4.5)]\n1529.5 [(96, 3.0), (98, 3.0), (99, 3.0), (100, 3.0), (100.5, 3.0), (101, 3.0), (101.5,
#  3.0), (102, 4.38), (102.5, 4.5), (103, 4.5), (104, 4.5), (105, 4.5)]\n1530.5 [(96, 3.0), (98, 3.0), (99, 3.0), (100, 3.0), (100.5, 3.0), (101, 3.0), 
# (101.5, 3.0), (102, 4.37), (102.5, 4.5), (103, 4.5), (104, 4.5), (105, 4.5)]\n1531.5 [(96, 3.0), (98, 3.0), (99, 3.0), (100, 3.0), (100.5, 3.0), (101,

# ==============================================================================================================
# [0019] 2026-09-23 18:58:29  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g11_ridge_stair",(1533,90,9),(1528.5,102,3.8),lens=30,res=(1280,720),outdir=OD))
print(shot("g12_ridge_stair_top",(1529,96,14),(1528.5,105,4.5),lens=26,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g11_ridge_stair.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\
# g12_ridge_stair_top.png\n"}

# ==============================================================================================================
# [0020] 2026-09-23 18:59:24  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
vt=bpy.data.collections['VK_ValleyTown']
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [round(min(v[i] for v in b),2) for i in range(3)],[round(max(v[i] for v in b),2) for i in range(3)]
for o in vt.all_objects:
    if o.type=='MESH' and (1530<o.location.x<1560 and 86<o.location.y<106) and not any(k in o.name for k in ('LipGrass','Rock_Small','Fern','Pebbles','Mushroom')):
        print(o.name,[round(v,2) for v in o.location],round(o.rotation_euler.z*57.3),bb(o))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Quarry_Face_Straight_inst [1545.0, 100.5, 3.0] 0 ([1543.5, 98.84, 2.4], [1546.5, 102.0, 6.55])\nSM_VK_Qua
# rry_Face_InnerCorner_inst [1548.0, 100.5, 3.0] 0 ([1546.43, 98.91, 2.4], [1549.5, 102.03, 6.46])\nSM_VK_Quarry_Face_InnerCorner_inst.001 [1542.0, 100.
# 5, 3.0] 90 ([1540.47, 98.93, 2.4], [1543.59, 102.0, 6.46])\nSM_VK_Quarry_Face_Straight_inst.001 [1548.0, 97.5, 3.0] -90 ([1546.34, 96.0, 2.4], [1549.5
# , 99.0, 6.55])\nSM_VK_Quarry_Face_Straight_inst.002 [1542.0, 97.5, 3.0] 90 ([1540.5, 96.0, 2.4], [1543.66, 99.0, 6.55])\nSM_VK_Quarry_Face_Corner_inst
#  [1548.0, 94.5, 3.0] 0 ([1546.42, 92.88, 2.4], [1549.5, 96.09, 6.52])\nSM_VK_Quarry_Face_Corner_inst.001 [1542.0, 94.5, 3.0] 90 ([1540.41, 92.92, 2.4]
# , [1543.62, 96.0, 6.52])\nSM_VK_Quarry_Face_Straight_inst.003 [1551.0, 94.5, 3.0] 0 ([1549.5, 92.84, 2.4], [1552.5, 96.0, 6.55])\nSM_VK_Quarry_Face_St

# ==============================================================================================================
# [0021] 2026-09-23 19:00:00  blender  ok
# ==============================================================================================================
import bpy, numpy as np
ns=bpy.app.driver_namespace; h=ns['rr_h']
o=bpy.data.objects['SM_VK_Prop_TreadwheelCrane_inst']
me=o.data; co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
low=w[w[:,2]<6.4]
print(len(low), low[:,0].min(),low[:,0].max(),low[:,1].min(),low[:,1].max())
# ground under low verts
import collections
bad=[(round(p[0],2),round(p[1],2),round(p[2],2),h(p[0],p[1])) for p in low[::max(1,len(low)//40)]]
print(bad)
# jib part over the pit
print('min y overall',w[:,1].min(),'z at min y', w[w[:,1].argmin(),2])
# rim vs terrain
for x in (1536,1538,1541,1545,1549,1552,1554):
    print(x,[(y,h(x,y)) for y in (89,90.5,92,93.5,95,97,99,101,102.5)])
# ---- result ----
# {"result":"Code executed successfully: 341 1542.3857260733873 1546.4143229558101 101.35000156394612 107.05000163086284\n[(1544.28, 106.76, 6.01, 6.0),
#  (1544.56, 106.76, 6.05, 6.0), (1544.24, 101.64, 6.27, 3.0), (1545.76, 105.29, 6.3, 6.0), (1543.04, 105.25, 6.26, 6.0), (1545.76, 105.55, 6.06, 6.0), 
# (1545.76, 103.29, 6.3, 6.0), (1543.04, 103.25, 6.26, 6.0), (1545.76, 103.55, 6.06, 6.0), (1544.62, 106.58, 6.12, 6.0), (1544.18, 106.55, 6.09, 6.0), (
# 1544.62, 107.05, 6.03, 6.0), (1544.62, 101.38, 6.12, 3.0), (1544.18, 101.35, 6.09, 3.0), (1544.62, 101.85, 6.03, 5.35), (1543.32, 105.18, 6.12, 6.0), 
# (1542.88, 105.15, 6.09, 6.0), (1543.32, 105.65, 6.03, 6.0), (1545.92, 105.18, 6.12, 6.0), (1545.48, 105.15, 6.09, 6.0), (1545.92, 105.65, 6.03, 6.0), 
# (1543.32, 103.18, 6.12, 6.0), (1542.88, 103.15, 6.09, 6.0), (1543.32, 103.65, 6.03, 6.0), (1545.92, 103.18, 6.12, 6.0), (1545.48, 103.15, 6.09, 6.0), 

# ==============================================================================================================
# [0022] 2026-09-23 19:00:31  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g13_quarry_front",(1545,74,16),(1545,97,4),lens=30,res=(1280,720),outdir=OD))
print(shot("g14_quarry_se",(1562,80,12),(1545,96,4.5),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g13_quarry_front.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\
# scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\
# \g14_quarry_se.png\n"}

# ==============================================================================================================
# [0023] 2026-09-23 19:02:13  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes['VillageKit']; dg=bpy.context.evaluated_depsgraph_get()
def top(x,y):
    r=sc.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name[:32]) if r[0] else None
for x in (1538.5,1539.3,1539.8,1540.3,1540.8,1549.2,1549.8,1550.4,1551.2):
    print(x,[(y,top(x,y)) for y in (91,93,95,97,99,101,101.8,102.5)])
# ---- result ----
# {"result":"Code executed successfully: 1538.5 [(91, (6.0, 'VKV_Chunk_0_1')), (93, (6.38, 'SM_VK_LeanTo_inst.010')), (95, (6.0, 'VKV_Chunk_0_2')), (97,
#  (6.0, 'VKV_Chunk_0_2')), (99, (6.0, 'VKV_Chunk_0_2')), (101, (6.0, 'VKV_Chunk_0_2')), (101.8, (6.0, 'VKV_Chunk_0_2')), (102.5, (6.0, 'VKV_Chunk_0_2')
# )]\n1539.3 [(91, (5.88, 'SM_VK_LeanTo_inst.010')), (93, (6.38, 'SM_VK_LeanTo_inst.010')), (95, (6.0, 'SM_VK_Quarry_Face_Straight_inst.')), (97, (3.0, 
# 'VKV_Chunk_0_2')), (99, (3.0, 'VKV_Chunk_0_2')), (101, (3.0, 'VKV_Chunk_0_2')), (101.8, (5.34, 'VKV_Chunk_0_2')), (102.5, (6.0, 'VKV_Chunk_0_2'))]\n15
# 39.8 [(91, (5.88, 'SM_VK_LeanTo_inst.010')), (93, (6.38, 'SM_VK_LeanTo_inst.010')), (95, (6.0, 'SM_VK_Quarry_Face_Straight_inst.')), (97, (3.0, 'VKV_C
# hunk_0_2')), (99, (3.0, 'VKV_Chunk_0_2')), (101, (3.0, 'VKV_Chunk_0_2')), (101.8, (5.34, 'VKV_Chunk_0_2')), (102.5, (6.0, 'VKV_Chunk_0_2'))]\n1540.3 [

# ==============================================================================================================
# [0024] 2026-09-23 19:02:44  blender  ok
# ==============================================================================================================
import bpy, collections
vt=bpy.data.collections['VK_ValleyTown']
c=collections.Counter()
for o in vt.all_objects:
    if o.type=='MESH': c[o.name.split('_inst')[0]]+=1
print(len(c))
print(sorted(c.items(), key=lambda t:-t[1])[:400])
# ---- result ----
# {"result":"Code executed successfully: 338\n[('SM_VKT_LipGrass', 896), ('SM_VK_Tree_Pine_B', 213), ('SM_VK_Tree_Pine_A', 197), ('SM_VK_Tree_Pine_Young
# ', 194), ('SM_VK_Wall_Timber_Window', 127), ('SM_VK_Deco_Weeds', 127), ('SM_VK_TownWall_Straight', 119), ('SM_VK_Plant_Fern', 114), ('SM_VK_Bush_Round
# ', 112), ('SM_VK_Rock_Small_A', 111), ('SM_VK_Wall_Stone', 106), ('SM_VK_Rock_Boulder_A', 95), ('SM_VK_Corner_Timber', 88), ('SM_VK_Corner_Stone', 87)
# , ('SM_VK_Mushrooms_Brown', 75), ('SM_VK_Wall_Stone_Window', 70), ('SM_VK_Rock_Small_B', 60), ('SM_VK_Rock_Pebbles', 60), ('SM_VK_Plant_TallGrass', 44
# ), ('SM_VK_Prop_FlowerBox', 42), ('SM_VK_Plant_Wildflowers', 41), ('SM_VK_Prop_FlowerBox_Daisy', 38), ('SM_VK_Plant_Reeds', 35), ('SM_VK_Wall_Plaster'
# , 34), ('SM_VK_Wall_Timber_K', 33), ('SM_VK_Wall_Wattle', 29), ('SM_VK_Prop_Fence', 28), ('SM_VK_Corner_Plaster', 28), ('SM_VK_Tree_Oak_Autumn', 28), 

# ==============================================================================================================
# [0025] 2026-09-23 19:03:31  blender  ok
# ==============================================================================================================
import bpy, re, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; gb=ns['rr_gb']
def h(x,y):
    r=gb.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return r[0].z if r[0] else None
vt=bpy.data.collections['VK_ValleyTown']
FREE=re.compile(r"^SM_VKT?_(Prop_|Pile_|Crop_|Bush_|Plant_|Rock_|Mushrooms|Animal_|Stump|Log_Fallen|Tent|MarketStall|LeanTo|Deco_Weeds|Deco_Bush|Deco_Hedge|Deco_MudWallow|Stockpile_Border|BuildSite_Cell|Banner_Pole)")
SKIP=("Prop_Sign","Prop_Lantern","Prop_Festoon","Prop_Banner","Prop_Bunting","Prop_Wreath","Prop_Shelf","FlowerBox","Window","Hanging","Awning","Chimney","TreadwheelCrane","Barge","Rowboat","Prop_ShopGoods","Prop_Planter")
out=[]
mb={}
for o in vt.all_objects:
    if o.type!='MESH': continue
    b=o.name.split('_inst')[0]
    if not FREE.match(b) or any(s in b for s in SKIP): continue
    me=o.data
    if me.name not in mb:
        co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); mb[me.name]=(co.min(0),co.max(0))
    lo,hi=mb[me.name]
    M=o.matrix_world
    xs=np.linspace(lo[0],hi[0],4); ys=np.linspace(lo[1],hi[1],4)
    xs=lo[0]+(xs-lo[0])*0.8+(hi[0]-lo[0])*0.1; ys=lo[1]+(ys-lo[1])*0.8+(hi[1]-lo[1])*0.1
    H=[]
    for x in xs:
        for y in ys:
            p=M@Vector((x,y,0)); z=h(p.x,p.y)
            if z is not None: H.append(z)
    if not H: continue
    zb=o.location.z+lo[2]*o.scale.z
    rng=max(H)-min(H)
    if rng>0.6 or zb-max(H)>0.4 or min(H)-zb>0.9:
        out.append((o.name,round(o.location.x,1),round(o.location.y,1),round(o.location.z,2),round(min(H),2),round(max(H),2)))
ns['rr_straddle']=out
print(len(out))
for t in out: print(t)
# ---- result ----
# {"result":"Code executed successfully: 163\n('SM_VK_Prop_HandPump_inst', 1645.2, 48.3, 0.0, -0.7, 0.0)\n('SM_VK_Prop_Woodpile_inst.004', 1660.8, 49.3,
#  0.0, -0.83, 0.0)\n('SM_VK_Prop_Creels_inst', 1694.0, 32.0, 0.05, -1.5, -1.5)\n('SM_VK_Pile_Fish_2_inst', 1693.2, 25.2, 0.05, -1.5, -0.27)\n('SM_VK_Pr
# op_SawPit_inst', 1611.0, 9.0, 1.5, 1.5, 1.5)\n('SM_VK_Prop_Skep_inst', 1566.6, 62.4, 2.04, 1.5, 1.5)\n('SM_VK_Prop_Skep_inst.001', 1568.1, 62.4, 2.04,
#  1.5, 1.5)\n('SM_VK_Prop_Skep_inst.002', 1569.6, 62.4, 2.04, 1.5, 1.5)\n('SM_VK_LeanTo_inst.010', 1539.0, 93.7, 3.0, 3.0, 6.0)\n('SM_VK_Prop_HoistBeam
# _inst', 1579.5, 90.0, 11.6, 3.0, 3.0)\n('SM_VK_Bush_Large_inst.006', 1637.3, 3.6, 1.5, 1.5, 1.5)\n('SM_VK_Plant_Reeds_inst.021', 1681.1, 17.5, 0.0, -0
# .0, 1.04)\n('SM_VK_Bush_Round_inst.028', 1648.7, 29.1, 1.5, -0.0, 1.5)\n('SM_VK_Plant_Reeds_inst.027', 1674.6, 28.9, 0.0, -0.0, 1.47)\n('SM_VK_Plant_R

# ==============================================================================================================
# [0026] 2026-09-23 19:04:15  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
ns=bpy.app.driver_namespace; gb=ns['rr_gb']; G=ns['rr_ground_G']
def h(x,y):
    r=gb.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return r[0].z if r[0] else None
vt=bpy.data.collections['VK_ValleyTown']
bad=[];onroad=[]
for o in vt.all_objects:
    if o.type!='MESH' or '_Tree_' not in o.name: continue
    x,y,z=o.location
    ring=[h(x+0.7*math.cos(a*math.pi/4),y+0.7*math.sin(a*math.pi/4)) for a in range(8)]
    ring=[r for r in ring if r is not None]
    hc=h(x,y)
    if hc is None or abs(hc-z)>0.2 or max(abs(r-z) for r in ring)>0.3:
        bad.append((o.name,round(x,1),round(y,1),round(z,2),hc and round(hc,2),round(min(ring),2),round(max(ring),2)))
    i,j=int((x-1500)//3),int(y//3)
    if 0<=i<72 and 0<=j<56 and (G.ground[j,i] in (1,2) or G.ramp[j,i]):
        onroad.append((o.name,round(x,1),round(y,1),int(G.ground[j,i]),int(G.ramp[j,i])))
print(len(bad)); [print(b) for b in bad]
print('onroad',onroad)
# ---- result ----
# {"result":"Code executed successfully: 2\n('SM_VK_Tree_Willow_inst.002', 1662.5, 30.9, 0.0, 0.0, -0.0, 0.86)\n('SM_VK_Tree_Pine_A_inst.177', 1645.8, 1
# 54.8, 4.5, 4.5, 4.5, 5.08)\nonroad []\n"}

# ==============================================================================================================
# [0027] 2026-09-23 19:04:36  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; gb=ns['rr_gb']
def h(x,y):
    r=gb.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return round(r[0].z,2) if r[0] else None
vt=bpy.data.collections['VK_ValleyTown']
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [round(min(v[i] for v in b),2) for i in range(3)],[round(max(v[i] for v in b),2) for i in range(3)]
for o in vt.all_objects:
    n=o.name
    if any(k in n for k in ('Prop_Laundry','Prop_FishRack','Prop_Cart','Prop_Crates','Prop_BarrelStack','Prop_Sacks','WaterWheel','Mill_','Wall_Stone_Axle','Prop_Millstone','Prop_HandPump','Woodpile_inst.004','LavoirBasin')) and o.location.y<75:
        lo,hi=bb(o)
        H=[h(x,y) for x in np.linspace(lo[0]+0.1,hi[0]-0.1,4) for y in np.linspace(lo[1]+0.1,hi[1]-0.1,4)]
        print(n,[round(v,2) for v in o.location],lo,hi,'ground',min(H),max(H))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Axle_inst [1579.5, 48.0, 0.0] [1577.98, 47.39, -1.6] [1581.02, 48.28, 3.0] ground -0.81 -0.03\
# nSM_VK_WaterWheel_inst [1579.5, 46.65, 1.3] [1576.61, 45.45, -1.59] [1582.39, 47.75, 4.19] ground -1.5 -0.65\nSM_VK_Mill_WheelPier_inst [1579.5, 44.9,
#  0.0] [1578.52, 44.41, -1.6] [1580.48, 45.6, 1.63] ground -1.5 -1.5\nSM_VK_Prop_Millstone_inst [1576.4, 50.5, 0.0] [1575.36, 48.73, -0.03] [1577.55, 5
# 1.31, 1.3] ground 0.0 0.0\nSM_VK_Prop_Sacks_inst.005 [1576.9, 54.13, 0.0] [1576.61, 53.25, -0.01] [1577.8, 54.53, 1.26] ground 0.0 0.0\nSM_VK_Prop_Sac
# ks_inst.006 [1585.3, 51.5, 0.0] [1584.48, 51.16, -0.01] [1585.82, 52.56, 1.26] ground 0.0 0.0\nSM_VK_Prop_Crates_inst.007 [1583.03, 58.13, 0.0] [1582.
# 42, 57.63, 0.0] [1585.07, 59.6, 1.5] ground 0.0 0.0\nSM_VK_Prop_BarrelStack_inst.007 [1585.4, 53.79, 0.0] [1584.85, 52.83, 0.0] [1586.01, 54.75, 1.5] 

# ==============================================================================================================
# [0028] 2026-09-23 19:05:14  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
ns=bpy.app.driver_namespace; h=ns['rr_h']
for x in (1572.3,1573.5,1575,1576.5,1577.7,1579):
    print(x,[(y,h(x,y)) for y in (55,56,57,58,59,60,61,62,63)])
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g15_mill_inlet",(1596,38,16),(1578,56,1.0),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: 1572.3 [(55, 0.0), (56, 0.0), (57, 0.0), (58, 0.0), (59, 0.0), (60, 1.38), (61, 1.5), (62, 1.5), (63, 1.5)]\n15
# 73.5 [(55, 0.0), (56, -0.0), (57, 0.0), (58, 0.0), (59, 0.25), (60, 0.75), (61, 1.25), (62, 1.5), (63, 1.5)]\n1575 [(55, 0.0), (56, 0.0), (57, 0.0), (
# 58, 0.0), (59, 0.25), (60, 0.75), (61, 1.25), (62, 1.5), (63, 1.5)]\n1576.5 [(55, 0.0), (56, 0.0), (57, 0.0), (58, 0.0), (59, 0.25), (60, 0.75), (61, 
# 1.25), (62, 1.5), (63, 1.5)]\n1577.7 [(55, 0.0), (56, 0.0), (57, 0.0), (58, 0.0), (59, 0.0), (60, 1.38), (61, 1.5), (62, 1.5), (63, 1.5)]\n1579 [(55, 
# 0.0), (56, 0.0), (57, 0.0), (58, 0.0), (59, 0.0), (60, 1.38), (61, 1.5), (62, 1.5), (63, 1.5)]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-wo
# rkspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g15_mill_

# ==============================================================================================================
# [0029] 2026-09-23 19:05:42  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["vk_render"].as_string())
vt=bpy.data.collections['VK_ValleyTown']
xs=[];ys=[]
for o in vt.all_objects:
    if o.type=='MESH' and 1570<o.location.x<1592 and 48<o.location.y<64 and any(k in o.name for k in ('Wall_','Corner_','Roof','Foundation')):
        for c in o.bound_box:
            w=o.matrix_world@Vector(c); xs.append(w.x); ys.append(w.y)
print('mill house bbox',min(xs),max(xs),min(ys),max(ys))
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g16_mill_ramp_nw",(1563,70,9),(1575,58,1.0),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: mill house bbox 1576.4788818359375 1585.5211181640625 46.79928970336914 58.20071029663086\nC:\\Users\\danie\\Ap
# pData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\ren
# ders2\\rereview\\ground\\g16_mill_ramp_nw.png\n"}

# ==============================================================================================================
# [0030] 2026-09-23 19:06:44  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; h=ns['rr_h']
vt=bpy.data.collections['VK_ValleyTown']
for o in vt.all_objects:
    if o.type!='MESH': continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    if x1>1572 and x0<1578 and y1>57.5 and y0<62.5:
        print(o.name,[round(v,2) for v in o.location],round(x0,2),round(x1,2),round(y0,2),round(y1,2),round(min(v.z for v in b),2))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Window_inst.135 [1579.5, 57.0, 0.0] 1577.98 1581.02 56.72 57.82 -0.11\nSM_VK_Deco_Weeds_inst.0
# 94 [1579.5, 57.0, 0.0] 1577.92 1581.1 57.13 57.87 -0.03\nSM_VK_Corner_Stone_inst.129 [1578.0, 57.0, 0.0] 1577.4 1578.65 56.35 57.62 -0.06\nSM_VK_Wall_
# Timber_Window_inst.248 [1579.5, 57.0, 3.0] 1577.98 1581.11 56.82 57.62 2.8\nSM_VK_Corner_Timber_inst.146 [1578.0, 57.0, 3.0] 1577.39 1578.13 56.87 57.
# 61 2.03\nSM_VK_Roof_Gable_inst.068 [1581.0, 55.5, 5.8] 1576.48 1585.52 53.97 58.2 5.1\nSM_VK_Prop_DryingRack_Herbs_inst [1574.5, 62.6, 1.5] 1574.06 15
# 74.94 61.76 63.44 1.5\nSM_VK_Prop_HerbBundles_inst [1571.8, 60.9, 1.5] 1570.55 1573.05 60.69 61.55 1.5\n"}

# ==============================================================================================================
# [0031] 2026-09-23 19:07:34  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g17_mill_ramp_top",(1575,50,12),(1575,61,1.0),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g17_mill_ramp_top.png\n"}

# ==============================================================================================================
# [0032] 2026-09-23 19:08:34  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g18_lake_east_edge",(1735,20,14),(1712,38,0),lens=30,res=(1280,720),outdir=OD))
print(shot("g19_river_west_edge",(1484,30,10),(1503,42,-0.5),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g18_lake_east_edge.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude
# \\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\groun
# d\\g19_river_west_edge.png\n"}

# ==============================================================================================================
# [0033] 2026-09-23 19:09:30  blender  ok
# ==============================================================================================================
import bpy, numpy as np
tc=bpy.data.collections["VK_ValleyTerrain"]
def verts(o):
    me=o.data; co=np.empty(len(me.vertices)*3); me.vertices.foreach_get("co",co); return co.reshape(-1,3)+np.array(o.matrix_world.translation)
for o in tc.all_objects:
    if 'Water' in o.name:
        v=verts(o); print(o.name, v[:,0].min().round(2), v[:,0].max().round(2), v[:,1].min().round(2), v[:,1].max().round(2), np.unique(v[:,2].round(2)))
ch=[o for o in tc.all_objects if 'Chunk' in o.name]
V=np.concatenate([verts(o) for o in ch])
sel=(V[:,1]>33)&(V[:,1]<51)
print('terrain minx in river band', V[sel,0].min().round(2))
sel2=(V[:,0]<1501)&(V[:,1]>33)&(V[:,1]<51)
print('west edge verts y,z sample', np.unique(V[sel2][:,[0,1,2]].round(1),axis=0)[:40])
selE=(V[:,1]>10)&(V[:,1]<60)
print('terrain maxx in lake band', V[selE,0].max().round(2))
# ---- result ----
# {"result":"Code executed successfully: VKV_Water_0_0 1498.5 1546.5 34.5 46.5 [-0.6]\nVKV_Water_1_0 1546.5 1594.5 34.5 46.5 [-0.6]\nVKV_Water_2_0 1594.
# 5 1642.5 34.5 46.5 [-0.6]\nVKV_Water_3_0 1642.5 1690.5 22.5 46.5 [-0.6]\nVKV_Water_4_0 1690.5 1714.5 22.5 46.5 [-0.6]\nVKV_Water_0_1 1498.5 1546.5 46.
# 5 49.5 [-0.6]\nVKV_Water_1_1 1546.5 1594.5 46.5 49.5 [-0.6]\nVKV_Water_2_1 1594.5 1642.5 46.5 49.5 [-0.6]\nVKV_Water_3_1 1642.5 1690.5 46.5 55.5 [-0.6
# ]\nVKV_Water_4_1 1690.5 1714.5 46.5 55.5 [-0.6]\nterrain minx in river band 1498.5\nwest edge verts y,z sample [[ 1.4985e+03 3.3500e+01 0.0000e+00]\n 
# [ 1.4985e+03 3.4000e+01 0.0000e+00]\n [ 1.4985e+03 3.4500e+01 0.0000e+00]\n [ 1.4985e+03 3.5000e+01 0.0000e+00]\n [ 1.4985e+03 3.5500e+01 0.0000e+00]\
# n [ 1.4985e+03 3.5700e+01 -0.0000e+00]\n [ 1.4985e+03 3.5900e+01 -0.0000e+00]\n [ 1.4985e+03 3.6000e+01 -2.0000e-01]\n [ 1.4985e+03 3.6000e+01 -1.0000

# ==============================================================================================================
# [0034] 2026-09-23 19:10:23  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; h=ns['rr_h']; G=ns['rr_ground_G']
for x in (1697.5,1698.5,1700,1701.5,1703,1704.5):
    print(x,[(y,h(x,y)) for y in (9,10,11,12,13,14,15,16,17,18,19,20)])
print(G.level[3:8,56:72])
print(G.water[3:10,56:72].astype(int))
vt=bpy.data.collections['VK_ValleyTown']
for o in vt.all_objects:
    if o.type!='MESH': continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    if x1>1697 and x0<1705 and y1>9 and y0<21:
        print(o.name,[round(v,2) for v in o.location],round(x0,2),round(x1,2),round(y0,2),round(y1,2))
# ---- result ----
# {"result":"Code executed successfully: 1697.5 [(9, 1.5), (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.5), (15, 1.38), (16, 0.0), (17, 0.0), (18,
#  0.0), (19, 0.0), (20, 0.0)]\n1698.5 [(9, 1.5), (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.25), (15, 0.75), (16, 0.25), (17, 0.0), (18, 0.0), 
# (19, 0.0), (20, 0.0)]\n1700 [(9, 1.5), (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.25), (15, 0.75), (16, 0.25), (17, 0.0), (18, 0.0), (19, 0.0)
# , (20, 0.0)]\n1701.5 [(9, 1.5), (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.25), (15, 0.75), (16, 0.25), (17, 0.0), (18, 0.0), (19, 0.0), (20, 
# 0.0)]\n1703 [(9, 1.5), (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.25), (15, 0.75), (16, 0.25), (17, 0.0), (18, 0.0), (19, -0.0), (20, -0.0)]\n
# 1704.5 [(9, 1.5), (10, 1.5), (11, 1.5), (12, 1.5), (13, 1.5), (14, 1.5), (15, 1.37), (16, 0.0), (17, 0.0), (18, 0.0), (19, 0.0), (20, 0.0)]\n[[1 1 1 1

# ==============================================================================================================
# [0035] 2026-09-23 19:10:46  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g20_lake_top",(1693,10,70),(1693,36,0),lens=26,res=(1280,900),outdir=OD))
print(shot("g21_fisher_ramp",(1712,4,10),(1698,20,0.5),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g20_lake_top.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scra
# tch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g21
# _fisher_ramp.png\n"}

# ==============================================================================================================
# [0036] 2026-09-23 19:11:28  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
vt=bpy.data.collections['VK_ValleyTown']
for o in vt.all_objects:
    if 'Willow' in o.name or 'Shed_Door' in o.name or 'Pier_' in o.name or 'Rowboat' in o.name or 'Creels' in o.name or 'Pile_Fish' in o.name or 'NetRack' in o.name:
        b=[o.matrix_world@Vector(c) for c in o.bound_box]
        print(o.name,[round(v,2) for v in o.location],round(o.rotation_euler.z*57.3), [round(min(v[i] for v in b),2) for i in range(3)],[round(max(v[i] for v in b),2) for i in range(3)])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Bridge_Stone_Pier_inst [1626.0, 42.0, 0.0] 90 [1622.64, 41.05, -2.0] [1629.36, 42.95, 1.0]\nSM_VK_Mill_Wh
# eelPier_inst [1579.5, 44.9, 0.0] -90 [1578.52, 44.41, -1.6] [1580.48, 45.6, 1.63]\nSM_VK_Pile_Fish_1_inst [1655.1, 52.1, 0.0] 210 [1654.55, 51.59, -0.
# 01] [1655.66, 52.66, 0.36]\nSM_VK_Wall_Shed_Door_inst [1693.5, 21.0, 0.0] 180 [1691.98, 20.76, -0.61] [1695.07, 21.78, 2.6]\nSM_VK_Pier_Deck_inst [169
# 3.5, 25.5, 0.0] 90 [1691.85, 23.74, -3.0] [1695.15, 27.0, 0.37]\nSM_VK_Pier_Deck_inst.001 [1693.5, 28.5, 0.0] 90 [1691.85, 26.74, -3.0] [1695.15, 30.0
# , 0.37]\nSM_VK_Pier_End_inst [1693.5, 31.5, 0.0] 90 [1691.85, 29.74, -3.01] [1695.15, 33.26, 2.51]\nSM_VK_Pier_Rail_inst [1693.5, 25.5, 0.0] 90 [1694.
# 81, 23.92, -0.1] [1694.99, 27.0, 1.05]\nSM_VK_Pier_Rail_inst.001 [1693.5, 28.5, 0.0] 90 [1694.81, 26.92, -0.1] [1694.99, 30.0, 1.05]\nSM_VK_Pier_Stair

# ==============================================================================================================
# [0037] 2026-09-23 19:12:13  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
vt=bpy.data.collections['VK_ValleyTown']
tc=bpy.data.collections['VK_ValleyTerrain']
import numpy as np
out=[]
for o in vt.all_objects:
    if o.type!='MESH' or '_Tree_' not in o.name: continue
    x,y=o.location.x,o.location.y
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    ov=max(1498.5-x0, x1-1717.5, -1.5-y0, y1-169.5)
    if ov>1.0: out.append((o.name,round(x,1),round(y,1),round(ov,1)))
print(len(out)); print(sorted(out,key=lambda t:-t[3])[:30])
# ---- result ----
# {"result":"Code executed successfully: 66\n[('SM_VK_Tree_Pine_B_inst.248', 1513.5, 167.3, 5.1), ('SM_VK_Tree_Pine_B_inst.273', 1706.2, 167.6, 5.0), ('
# SM_VK_Tree_Pine_B_inst.265', 1653.3, 167.2, 4.8), ('SM_VK_Tree_Pine_B_inst.268', 1666.1, 166.8, 4.7), ('SM_VK_Tree_Pine_B_inst.102', 1501.2, 137.1, 4.
# 4), ('SM_VK_Tree_Pine_B_inst.262', 1624.2, 167.6, 4.4), ('SM_VK_Tree_Pine_B_inst.188', 1501.2, 157.3, 3.9), ('SM_VK_Tree_Pine_B_inst.263', 1627.1, 167
# .0, 3.9), ('SM_VK_Tree_Pine_A_inst.244', 1501.2, 167.2, 3.7), ('SM_VK_Tree_Pine_B_inst.081', 1501.0, 124.7, 3.6), ('SM_VK_Tree_Pine_B_inst.250', 1522.
# 1, 166.8, 3.6), ('SM_VK_Tree_Pine_B_inst.272', 1697.3, 166.3, 3.6), ('SM_VK_Tree_Pine_A_inst.092', 1500.4, 128.3, 3.5), ('SM_VK_Tree_Pine_B_inst.247',
#  1507.7, 167.3, 3.5), ('SM_VK_Tree_Pine_A_inst.250', 1559.2, 167.0, 3.5), ('SM_VK_Tree_Pine_B_inst.266', 1658.5, 166.5, 3.5), ('SM_VK_Tree_Pine_B_inst

# ==============================================================================================================
# [0038] 2026-09-23 19:13:15  blender  ok
# ==============================================================================================================
import bpy
im=bpy.data.images.get("T_VK_GroundCtl_Town"); print(im and (im.size[:], im.source))
m=bpy.data.materials["M_VK_TerrainTown"]
nt=m.node_tree
for n in nt.nodes:
    extra=''
    if n.type=='TEX_IMAGE': extra=n.image.name if n.image else None
    if n.type=='TEX_NOISE': extra=(n.inputs['Scale'].default_value, n.noise_dimensions)
    print(n.name,n.type,n.label,extra)
# ---- result ----
# {"result":"Code executed successfully: ((72, 56), 'FILE')\nMaterial Output OUTPUT_MATERIAL \nPrincipled BSDF BSDF_PRINCIPLED \nTexture Coordinate TEX_
# COORD \nGeometry NEW_GEOMETRY \nSeparate XYZ SEPXYZ \nAttribute ATTRIBUTE \nSeparate Color SEPARATE_COLOR \nVector Math VECT_MATH \nVector Math.001 VE
# CT_MATH \nImage Texture TEX_IMAGE T_VK_TerrainMacro\nSeparate Color.001 SEPARATE_COLOR \nNoise Texture TEX_NOISE (0.3499999940395355, '3D')\nVector Ma
# th.002 VECT_MATH \nVector Math.003 VECT_MATH \nVector Math.004 VECT_MATH \nMapping MAPPING CTL_MAP \nImage Texture.001 TEX_IMAGE T_VK_GroundCtl_Town\n
# Separate Color.002 SEPARATE_COLOR \nImage Texture.002 TEX_IMAGE T_VK_Grass_BC\nMapping.001 MAPPING \nImage Texture.003 TEX_IMAGE T_VK_Grass_BC\nMap Ra
# nge MAP_RANGE \nMix MIX \nHue/Saturation/Value HUE_SAT \nImage Texture.004 TEX_IMAGE T_VK_Grass_H\nMap Range.001 MAP_RANGE \nImage Texture.005 TEX_IMA

# ==============================================================================================================
# [0039] 2026-09-23 19:13:40  blender  ok
# ==============================================================================================================
import bpy
nt=bpy.data.materials["M_VK_TerrainTown"].node_tree
def src(node,depth=0,maxd=5):
    for i in node.inputs:
        for l in i.links:
            f=l.from_node
            extra=''
            if f.type=='VECT_MATH': extra=f.operation+str([tuple(round(x,3) for x in s.default_value) if hasattr(s.default_value,'__len__') else round(s.default_value,3) for s in f.inputs if not s.is_linked and s.enabled])
            if f.type=='MATH': extra=f.operation+str([round(s.default_value,3) for s in f.inputs if not s.is_linked and s.enabled])
            if f.type=='TEX_NOISE': extra=str([(s.name,round(s.default_value,3)) for s in f.inputs if not s.is_linked and s.enabled and not hasattr(s.default_value,'__len__')])
            print('  '*depth+f"{node.name}.{i.name} <- {f.name}({f.type}) {extra}")
            if depth<maxd: src(f,depth+1,maxd)
t=nt.nodes['Image Texture.001']; print(t.interpolation, t.extension)
src(t,0,6)
# ---- result ----
# {"result":"Code executed successfully: Linear EXTEND\nImage Texture.001.Vector <- Mapping(MAPPING) \n Mapping.Vector <- Vector Math.004(VECT_MATH) ADD
# []\n Vector Math.004.Vector <- Texture Coordinate(TEX_COORD) \n Vector Math.004.Vector <- Vector Math.003(VECT_MATH) SCALE[1.6]\n Vector Math.003.Vect
# or <- Vector Math.002(VECT_MATH) SUBTRACT[(0.5, 0.5, 0.5)]\n Vector Math.002.Vector <- Noise Texture(TEX_NOISE) [('Scale', 0.35), ('Detail', 2.0), ('R
# oughness', 0.5), ('Lacunarity', 2.0), ('Distortion', 0.0)]\n Noise Texture.Vector <- Texture Coordinate(TEX_COORD) \n"}

# ==============================================================================================================
# [0040] 2026-09-23 19:14:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g22_mainroad_colonycam",(1640,-8,33),(1626,20,1.5),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g22_mainroad_colonycam.png\n"}

# ==============================================================================================================
# [0041] 2026-09-23 19:15:07  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; h=ns['rr_h']
sc=bpy.data.scenes['VillageKit']; dg=bpy.context.evaluated_depsgraph_get()
def top(x,y):
    r=sc.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name[:28]) if r[0] else None
for x in (1624,1626,1628):
    print(x,[(y,h(x,y),top(x,y)) for y in (26,27,28,29,30,31,32,33,34,35,36,37)])
for n in ('SM_VK_Bridge_Stone_Ramp_inst','SM_VK_Bridge_Stone_Ramp_inst.001','SM_VK_Bridge_Stone_Span_inst','SM_VK_Bridge_Stone_Span_inst.001'):
    o=bpy.data.objects[n]; b=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n,[round(min(v[i] for v in b),2) for i in range(3)],[round(max(v[i] for v in b),2) for i in range(3)])
# ---- result ----
# {"result":"Code executed successfully: 1624 [(26, 1.5, (1.5, 'VKV_Chunk_2_0')), (27, 1.5, (1.5, 'VKV_Chunk_2_0')), (28, 1.5, (1.5, 'VKV_Chunk_2_0')), 
# (29, 1.25, (1.25, 'VKV_Chunk_2_0')), (30, 0.75, (0.75, 'VKV_Chunk_2_0')), (31, 0.25, (0.25, 'VKV_Chunk_2_0')), (32, 0.0, (0.0, 'VKV_Chunk_2_0')), (33,
#  0.0, (1.22, 'SM_VK_Bridge_Stone_Ramp_inst')), (34, -0.0, (1.3, 'SM_VK_Bridge_Stone_Ramp_inst')), (35, 0.0, (0.86, 'SM_VK_Bridge_Stone_Ramp_inst')), (
# 36, -0.11, (-0.11, 'VKV_Chunk_2_0')), (37, -1.36, (1.31, 'SM_VK_Bridge_Stone_Span_inst'))]\n1626 [(26, 1.5, (1.5, 'VKV_Chunk_2_0')), (27, 1.5, (1.5, '
# VKV_Chunk_2_0')), (28, 1.5, (1.5, 'VKV_Chunk_2_0')), (29, 1.25, (1.25, 'VKV_Chunk_2_0')), (30, 0.75, (0.75, 'VKV_Chunk_2_0')), (31, 0.25, (0.25, 'VKV_
# Chunk_2_0')), (32, 0.0, (0.0, 'VKV_Chunk_2_0')), (33, 0.0, (0.03, 'SM_VK_Bridge_Stone_Ramp_inst')), (34, 0.0, (0.44, 'SM_VK_Bridge_Stone_Ramp_inst')),

# ==============================================================================================================
# [0042] 2026-09-23 19:15:55  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; h=ns['rr_h']; G=ns['rr_ground_G']
sc=bpy.data.scenes['VillageKit']; dg=bpy.context.evaluated_depsgraph_get()
def top(x,y):
    r=sc.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name[:26]) if r[0] else None
print('level row30', G.level[30,5:26]); print('ground row30', G.ground[30,5:26]); print('level row29', G.level[29,5:26])
for x in range(1527,1576,2):
    print(x, h(x,91.5), top(x,91.5))
# ---- result ----
# {"result":"Code executed successfully: level row30 [2 2 2 2 2 2 4 4 2 2 2 2 4 4 2 2 2 2 2 2 2]\nground row30 [0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 2 2 
# 2]\nlevel row29 [2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2]\n1527 3.0 (3.0, 'VKV_Chunk_0_1')\n1529 3.0 (3.0, 'VKV_Chunk_0_1')\n1531 3.0 (3.0, 'VKV_Chu
# nk_0_1')\n1533 5.88 (5.88, 'VKV_Chunk_0_1')\n1535 6.0 (6.0, 'VKV_Chunk_0_1')\n1537 6.0 (6.0, 'VKV_Chunk_0_1')\n1539 5.88 (6.0, 'SM_VK_LeanTo_inst.010'
# )\n1541 3.0 (3.0, 'VKV_Chunk_0_1')\n1543 3.0 (3.0, 'VKV_Chunk_0_1')\n1545 3.0 (3.0, 'VKV_Chunk_0_1')\n1547 3.0 (3.0, 'VKV_Chunk_1_1')\n1549 3.0 (3.0, 
# 'VKV_Chunk_1_1')\n1551 5.88 (5.88, 'VKV_Chunk_1_1')\n1553 6.0 (6.0, 'VKV_Chunk_1_1')\n1555 6.0 (6.0, 'VKV_Chunk_1_1')\n1557 5.88 (5.88, 'VKV_Chunk_1_1
# ')\n1559 3.0 (3.0, 'VKV_Chunk_1_1')\n1561 3.0 (3.0, 'VKV_Chunk_1_1')\n1563 3.0 (3.0, 'VKV_Chunk_1_1')\n1565 3.0 (3.0, 'VKV_Chunk_1_1')\n1567 3.0 (3.0,

# ==============================================================================================================
# [0043] 2026-09-23 19:16:25  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["vk_render"].as_string())
vt=bpy.data.collections['VK_ValleyTown']
hits=[]
for o in vt.all_objects:
    if o.type!='MESH' or 'LipGrass' in o.name: continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    if x1>1533 and x0<1569 and y1>87 and y0<90: hits.append((o.name,round(x0,1),round(x1,1),round(y0,1),round(y1,1)))
print(hits)
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g23_postern_lane",(1548,62,34),(1550,92,3),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: [('SM_VK_TownWall_Straight_inst.084', 1567.4, 1570.2, 84.0, 87.4), ('SM_VK_TownWall_Straight_inst.086', 1567.4,
#  1570.2, 87.0, 90.4), ('SM_VK_LeanTo_inst.010', 1537.3, 1540.7, 89.8, 93.8), ('SM_VK_Plant_Wildflowers_inst.053', 1554.3, 1557.3, 86.6, 89.6), ('SM_VK
# _Bush_Round_inst.035', 1559.5, 1562.6, 86.1, 89.3)]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5
# f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g23_postern_lane.png\n"}

# ==============================================================================================================
# [0044] 2026-09-23 19:17:25  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
exec(bpy.data.texts["vk_render"].as_string())
o=bpy.data.objects['SM_VK_TownWall_Postern_inst']
b=[o.matrix_world@Vector(c) for c in o.bound_box]
print([round(v,2) for v in o.location], round(o.rotation_euler.z*57.3), [round(min(v[i] for v in b),2) for i in range(3)],[round(max(v[i] for v in b),2) for i in range(3)])
dg=bpy.context.evaluated_depsgraph_get(); bv=BVHTree.FromObject(o,dg); mi=o.matrix_world.inverted()
# find opening: cast horizontal rays along x through the wall at various y,z
for z in (3.3,4.0,5.0):
    row=[]
    for y in [88.5+0.25*k for k in range(25)]:
        p=mi@Vector((1560,y,z)); d=mi.to_3x3()@Vector((1,0,0))
        r=bv.ray_cast(p,d,20); row.append('#' if r[0] else '.')
    print(z,''.join(row))
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g24_postern_west",(1556,86,7),(1569,91.5,4),lens=35,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: [1569.0, 91.5, 3.0] -90 [1567.51, 90.0, 1.5] [1570.18, 93.0, 10.95]\n3.3 .......##.......###......\n4.0 .......
# ##.......###......\n5.0 .......##.......###......\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f5
# 6\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g24_postern_west.png\n"}

# ==============================================================================================================
# [0045] 2026-09-23 19:18:09  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["vk_render"].as_string())
vt=bpy.data.collections['VK_ValleyTown']
rows=[]
for o in vt.all_objects:
    if o.type!='MESH' or 'LipGrass' in o.name: continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    if x1>1570.5 and x0<1623 and y1>86.5 and y0<93.5 and not o.name.startswith('SM_VK_TownWall'):
        rows.append((o.name,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(min(v.z for v in b),2)))
for r in sorted(rows,key=lambda t:t[1]): print(r)
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g25_west_quarter_street",(1596,112,30),(1596,88,3),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Prop_LampPost_inst.019', 1570.8, 1571.8, 89.2, 89.6, 3.0)\n('SM_VK_Prop_LampPost_inst.024', 1570.8, 157
# 1.8, 93.4, 93.8, 3.0)\n('SM_VK_Deco_Weeds_inst.132', 1574.1, 1574.9, 86.9, 90.1, 2.97)\n('SM_VK_Wall_Stone_Window_inst.147', 1574.2, 1575.3, 87.0, 90.
# 0, 2.89)\n('SM_VK_Prop_FlowerBox_Daisy_inst.026', 1574.2, 1574.7, 87.8, 89.2, 3.56)\n('SM_VK_Wall_StoneUp_Window_inst.002', 1574.2, 1575.3, 84.0, 87.0
# , 5.89)\n('SM_VK_Corner_Stone_inst.147', 1574.4, 1575.7, 89.4, 90.6, 2.94)\n('SM_VK_Wall_StoneUp_Twin_inst.003', 1574.4, 1575.3, 84.0, 87.0, 8.69)\n('
# SM_VK_Corner_StoneUp_inst.002', 1574.5, 1575.6, 89.4, 90.5, 5.94)\n('SM_VK_Corner_StoneUp_inst.006', 1574.5, 1575.6, 89.4, 90.5, 8.74)\n('SM_VK_Wall_S
# tone_inst.161', 1574.5, 1575.3, 84.0, 87.0, 2.89)\n('SM_VK_Wall_StoneUp_inst.001', 1574.5, 1575.3, 87.0, 90.0, 5.89)\n('SM_VK_Wall_StoneUp_inst.004', 

# ==============================================================================================================
# [0046] 2026-09-23 19:18:44  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g26_chapel_forecourt",(1660,88,32),(1646,112,3),lens=30,res=(1600,900),outdir=OD))
print(shot("g27_terrace_street",(1665,100,26),(1665,82,3),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g26_chapel_forecourt.png\nC:\\Users\\danie\\AppData\\Roaming\\Clau
# de\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\gro
# und\\g27_terrace_street.png\n"}

# ==============================================================================================================
# [0047] 2026-09-23 19:19:22  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
vt=bpy.data.collections['VK_ValleyTown']
xs=[];ys=[];names=[]
for o in vt.all_objects:
    if o.type!='MESH': continue
    x,y=o.location.x,o.location.y
    if 1672<x<1700 and -3<y<16 and not any(k in o.name for k in ('LipGrass','Tree','Bush','Plant','Rock','Mushroom')):
        b=[o.matrix_world@Vector(c) for c in o.bound_box]
        xs+= [v.x for v in b]; ys+=[v.y for v in b]; names.append(o.name)
print(min(xs),max(xs),min(ys),max(ys)); print(len(names))
print([n for n in names if 'Fence' in n or 'Gate' in n][:40])
# ---- result ----
# {"result":"Code executed successfully: 1678.4788818359375 1695.199951171875 0.29928964376449585 14.948182106018066\n76\n['SM_VK_Prop_Fence_inst.171', 
# 'SM_VK_Prop_Fence_inst.172', 'SM_VK_Prop_FenceGate_inst.023', 'SM_VK_Prop_Fence_inst.173', 'SM_VK_Prop_Fence_inst.174', 'SM_VK_Prop_Fence_inst.175', '
# SM_VK_Prop_Fence_inst.176', 'SM_VK_Prop_Fence_inst.177', 'SM_VK_Prop_Fence_inst.178', 'SM_VK_Prop_Fence_inst.179']\n"}

# ==============================================================================================================
# [0048] 2026-09-23 19:19:50  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns['rr_ground_G']
vt=bpy.data.collections['VK_ValleyTown']
cells=[(i,j) for (j,i) in zip(*np.nonzero(G.ramp))]
print(cells)
rects=[(1500+3*i,1500+3*i+3,3*j,3*j+3,(i,j)) for (i,j) in cells]
out=[]
for o in vt.all_objects:
    if o.type!='MESH' or 'Bridge' in o.name: continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    for (a0,a1,b0,b1,c) in rects:
        ox=min(x1,a1)-max(x0,a0); oy=min(y1,b1)-max(y0,b0)
        if ox>0.3 and oy>0.3: out.append((o.name,c,round(ox,2),round(oy,2),round(x0,1),round(x1,1),round(y0,1),round(y1,1)))
for t in out: print(t)
# ---- result ----
# {"result":"Code executed successfully: [(66, 5), (67, 5), (9, 10), (10, 10), (41, 10), (42, 10), (9, 17), (10, 17), (41, 17), (42, 17), (24, 19), (25,
#  19), (41, 22), (42, 22), (9, 23), (10, 23), (9, 33)]\n('SM_VK_Corner_Stone_inst.129', (25, 19), 0.6, 0.62, 1577.4, 1578.7, 56.4, 57.6)\n('SM_VK_Corne
# r_Timber_inst.146', (25, 19), 0.61, 0.61, 1577.4, 1578.1, 56.9, 57.6)\n('SM_VK_Roof_Gable_inst.068', (25, 19), 1.52, 1.2, 1576.5, 1585.5, 54.0, 58.2)\
# n('SM_VK_Tree_Oak_B_inst.014', (9, 33), 3, 3, 1525.9, 1535.0, 98.9, 107.3)\n('SM_VKT_LipGrass_inst.500', (67, 5), 0.59, 0.39, 1703.4, 1705.2, 14.8, 15
# .4)\n('SM_VKT_LipGrass_inst.556', (9, 10), 0.58, 0.34, 1525.9, 1527.6, 29.9, 30.3)\n('SM_VKT_LipGrass_inst.620', (10, 17), 0.32, 0.3, 1532.7, 1534.1, 
# 53.7, 54.1)\n"}

# ==============================================================================================================
# [0049] 2026-09-23 19:20:30  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes['VillageKit']; dg=bpy.context.evaluated_depsgraph_get()
def hits(x,y,z=10):
    out=[]; 
    for _ in range(5):
        r=sc.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)))
        if not r[0]: break
        out.append((round(r[1].z,2),r[4].name[:24])); z=r[1].z-0.001
    return out
for (x,y) in ((1693.2,25.2),(1693.4,24.5),(1694,32),(1693.5,31.5),(1693.5,27),(1645.2,48.3),(1645.6,47.8),(1660.8,48),(1660.8,47.4)):
    print((x,y),hits(x,y))
# ---- result ----
# {"result":"Code executed successfully: (1693.2, 25.2) [(0.4, 'SM_VK_Pile_Fish_2_inst'), (0.38, 'SM_VK_Pile_Fish_2_inst'), (0.37, 'SM_VK_Pile_Fish_2_in
# st'), (0.34, 'SM_VK_Pile_Fish_2_inst'), (0.29, 'SM_VK_Pile_Fish_2_inst')]\n(1693.4, 24.5) [(0.29, 'SM_VK_Pile_Fish_2_inst'), (0.25, 'SM_VK_Pile_Fish_2
# _inst'), (0.11, 'SM_VK_Pile_Fish_2_inst'), (0.05, 'SM_VK_Pier_Deck_inst'), (0.05, 'SM_VK_Pile_Fish_2_inst')]\n(1694, 32) [(0.39, 'SM_VK_Prop_Creels_in
# st'), (0.38, 'SM_VK_Prop_Creels_inst'), (0.36, 'SM_VK_Prop_Creels_inst'), (0.35, 'SM_VK_Prop_Creels_inst'), (0.11, 'SM_VK_Prop_Creels_inst')]\n(1693.5
# , 31.5) [(0.06, 'SM_VK_Pier_End_inst'), (-0.01, 'SM_VK_Pier_End_inst'), (-0.02, 'SM_VK_Pier_End_inst'), (-0.32, 'SM_VK_Pier_End_inst'), (-0.6, 'VKV_Wa
# ter_4_0')]\n(1693.5, 27) [(-0.05, 'SM_VK_Pier_Deck_inst.001'), (-0.29, 'SM_VK_Pier_Deck_inst'), (-0.6, 'VKV_Water_4_0'), (-1.5, 'VKV_Chunk_4_0')]\n(16

# ==============================================================================================================
# [0050] 2026-09-23 19:21:09  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g28_smokehouse_bank",(1656,38,4),(1659,49,0.3),lens=32,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g28_smokehouse_bank.png\n"}

# ==============================================================================================================
# [0051] 2026-09-23 19:22:06  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns['rr_ground_G']
vt=bpy.data.collections['VK_ValleyTown']
road=np.zeros_like(G.ground,bool); road|=(G.ground==1)|(G.ground==2)
# exclude town interior streets? include all; list objects (non-flat) sitting mostly on road cells outside the walls
out=[]
for o in vt.all_objects:
    if o.type!='MESH' or 'LipGrass' in o.name or 'Bridge' in o.name or 'Quay' in o.name: continue
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in b);x1=max(v.x for v in b);y0=min(v.y for v in b);y1=max(v.y for v in b)
    cx,cy=o.location.x,o.location.y
    i,j=int((cx-1500)//3),int(cy//3)
    if not(0<=i<72 and 0<=j<56): continue
    inside=(23<=i<63 and 25<=j<46)
    if road[j,i] and not inside:
        out.append((o.name,round(cx,1),round(cy,1),(i,j),int(G.ground[j,i]),round(x1-x0,1),round(y1-y0,1)))
for t in out: print(t)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Gatehouse_Portcullis_inst', 1626.0, 72.6, (42, 24), 1, 3.6, 0.2)\n('SM_VK_Gatehouse_GateLeaf_inst', 162
# 4.4, 73.8, (41, 24), 1, 0.8, 1.7)\n('SM_VK_Gatehouse_GateLeaf_inst.001', 1627.6, 73.8, (42, 24), 1, 0.8, 1.7)\n('SM_VK_Wall_Timber_Window_inst.241', 1
# 626.0, 72.0, (42, 24), 1, 3.1, 0.8)\n('SM_VK_Roof_Cone_R2_inst', 1623.0, 72.0, (41, 24), 1, 4.4, 4.4)\n('SM_VK_Crop_Cabbage_inst.009', 1507.5, 19.5, (
# 2, 6), 1, 3.2, 3.1)\n('SM_VK_Crop_Cabbage_inst.010', 1510.5, 19.5, (3, 6), 1, 3.2, 3.1)\n('SM_VK_Crop_Carrot_inst.008', 1513.5, 19.5, (4, 6), 1, 3.1, 
# 3.0)\n('SM_VK_Crop_Carrot_inst.009', 1516.5, 19.5, (5, 6), 1, 3.1, 3.0)\n('SM_VK_Crop_Pumpkin_inst.006', 1519.5, 19.5, (6, 6), 1, 2.9, 3.1)\n('SM_VK_C
# rop_Pumpkin_inst.007', 1522.5, 19.5, (7, 6), 1, 2.9, 3.1)\n('SM_VK_Crop_Wheat_inst.015', 1525.5, 19.5, (8, 6), 1, 3.4, 3.1)\n('SM_VK_Crop_Wheat_inst.0

# ==============================================================================================================
# [0052] 2026-09-23 19:22:42  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
tc=bpy.data.collections["VK_ValleyTerrain"]
sc=bpy.data.scenes['VillageKit']; dg=bpy.context.evaluated_depsgraph_get()
def info(x,y,z=20,d=(0,0,-1)):
    r=sc.ray_cast(dg,Vector((x,y,z)),Vector(d))
    if not r[0]: return None
    o=r[4]; 
    ev=o.evaluated_get(dg); me=ev.data
    p=me.polygons[r[3]]
    mat=o.material_slots[p.material_index].material.name if o.material_slots else None
    return (round(r[1].x,2),round(r[1].y,2),round(r[1].z,2),tuple(round(v,2) for v in r[2]),o.name,mat,p.material_index)
for x in (1526.4,1526.7,1527.0,1527.2,1527.4):
    print(x,[info(x,y) for y in (29.6,30.0,30.3,30.6,31.0)])
# ---- result ----
# {"result":"Code executed successfully: 1526.4 [(1526.4, 29.6, 1.5, (0.01, 0.07, 1.0), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0), (1526.4, 30.0, 1.63, (-
# 0.03, 0.89, -0.45), 'SM_VKT_LipGrass_inst.556', 'M_VK_Leaves', 0), (1526.4, 30.3, 0.51, (0.05, 0.94, 0.34), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0), (
# 1526.4, 30.6, 0.0, (0.0, 0.0, 1.0), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0), (1526.4, 31.0, 0.0, (0.0, 0.0, 1.0), 'VKV_Chunk_0_0', 'M_VK_TerrainTown',
#  0)]\n1526.7 [(1526.7, 29.6, 1.49, (0.0, 0.07, 1.0), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0), (1526.7, 30.0, 1.61, (-0.03, 0.89, -0.45), 'SM_VKT_LipGr
# ass_inst.556', 'M_VK_Leaves', 0), (1526.7, 30.3, 0.46, (0.05, 0.93, 0.35), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0), (1526.7, 30.6, 0.0, (0.0, 0.0, 1.0
# ), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0), (1526.7, 31.0, 0.0, (0.0, 0.0, 1.0), 'VKV_Chunk_0_0', 'M_VK_TerrainTown', 0)]\n1527.0 [(1527.0, 29.6, 1.49

# ==============================================================================================================
# [0053] 2026-09-23 19:23:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g29_bench_ramp_topwest_slot",(1529.5,67.5,5.2),(1527.2,72.2,2.6),lens=40,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g29_bench_ramp_topwest_slot.png\n"}

# ==============================================================================================================
# [0054] 2026-09-23 19:24:03  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; gb=ns['rr_gb']
def h(x,y):
    r=gb.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return r[0].z if r[0] else None
vt=bpy.data.collections['VK_ValleyTown']
out=[]
for o in vt.all_objects:
    if o.type!='MESH': continue
    b=o.name.split('_inst')[0]
    if not any(k in b for k in ('_Wall_','_Corner_','Foundation')) or 'TownWall' in b or 'Up' in b or 'LowWall' in b: continue
    z=o.location.z
    if abs(z/1.5-round(z/1.5))>0.05: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    zmin=min(v.z for v in bb)
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    pts=[(np.mean(xs),np.mean(ys))]+[(x,y) for x in (min(xs)+0.15,max(xs)-0.15) for y in (min(ys)+0.15,max(ys)-0.15)]
    H=[h(x,y) for (x,y) in pts]; H=[v for v in H if v is not None]
    if not H: continue
    if max(H)>z+0.35 or min(H)<zmin-0.3:
        out.append((o.name,round(o.location.x,1),round(o.location.y,1),round(z,2),round(zmin,2),round(min(H),2),round(max(H),2)))
print(len(out))
for t in out[:80]: print(t)
# ---- result ----
# {"result":"Code executed successfully: 266\n('SM_VK_Wall_Stone_Window_inst.136', 1582.5, 48.0, 0.0, -0.11, -0.99, -0.04)\n('SM_VK_Corner_Stone_inst.13
# 0', 1578.0, 48.0, 0.0, -0.06, -0.75, 0.0)\n('SM_VK_Corner_Stone_inst.131', 1584.0, 48.0, 0.0, -0.06, -0.77, -0.0)\n('SM_VK_Wall_Timber_Window_inst.243
# ', 1578.0, 55.5, 3.0, 2.8, 0.0, 0.0)\n('SM_VK_Wall_Timber_Window_inst.244', 1578.0, 52.5, 3.0, 2.8, 0.0, 0.0)\n('SM_VK_Wall_Timber_Window_inst.245', 1
# 578.0, 49.5, 3.0, 2.8, -0.04, 0.0)\n('SM_VK_Wall_Timber_inst.040', 1584.0, 49.5, 3.0, 2.8, -0.09, 0.0)\n('SM_VK_Wall_Timber_Window_inst.246', 1584.0, 
# 52.5, 3.0, 2.8, 0.0, 0.0)\n('SM_VK_Wall_Timber_Window_inst.247', 1584.0, 55.5, 3.0, 2.8, 0.0, 0.0)\n('SM_VK_Wall_Timber_Window_inst.248', 1579.5, 57.0
# , 3.0, 2.8, 0.0, 0.0)\n('SM_VK_Wall_Timber_X_inst.034', 1582.5, 57.0, 3.0, 2.8, 0.0, 0.0)\n('SM_VK_Wall_Timber_Window_inst.249', 1582.5, 48.0, 3.0, 2.

# ==============================================================================================================
# [0055] 2026-09-23 19:24:20  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; gb=ns['rr_gb']
def h(x,y):
    r=gb.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return r[0].z if r[0] else None
vt=bpy.data.collections['VK_ValleyTown']
out=[]
for o in vt.all_objects:
    if o.type!='MESH': continue
    b=o.name.split('_inst')[0]
    if not any(k in b for k in ('_Wall_','_Corner_','Foundation','Porch','Stair_Stone_Ext','LowWall')) or 'TownWall' in b: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    zmin=min(v.z for v in bb); z=o.location.z
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    hc=h(np.mean(xs),np.mean(ys))
    if hc is None or abs(z-hc)>0.8: continue
    pts=[(x,y) for x in (min(xs)+0.15,max(xs)-0.15) for y in (min(ys)+0.15,max(ys)-0.15)]
    H=[h(x,y) for (x,y) in pts]+[hc]; H=[v for v in H if v is not None]
    if max(H)>z+0.35 or min(H)<zmin-0.25:
        out.append((o.name,round(o.location.x,1),round(o.location.y,1),round(z,2),round(zmin,2),round(min(H),2),round(max(H),2)))
print(len(out))
for t in out: print(t)
# ---- result ----
# {"result":"Code executed successfully: 18\n('SM_VK_Wall_Stone_Window_inst.136', 1582.5, 48.0, 0.0, -0.11, -0.99, -0.04)\n('SM_VK_Corner_Stone_inst.130
# ', 1578.0, 48.0, 0.0, -0.06, -0.75, 0.0)\n('SM_VK_Corner_Stone_inst.131', 1584.0, 48.0, 0.0, -0.06, -0.77, -0.0)\n('SM_VK_Wall_Stone_inst.143', 1657.5
# , 48.0, 0.0, -0.11, -0.68, -0.04)\n('SM_VK_Corner_Stone_inst.135', 1656.0, 48.0, 0.0, -0.06, -0.75, 0.0)\n('SM_VK_Corner_Stone_inst.136', 1659.0, 48.0
# , 0.0, -0.06, -0.77, -0.0)\n('SM_VK_Wall_Shed_Raised_inst', 1612.5, 60.0, 2.26, 2.13, 1.5, 1.5)\n('SM_VK_Wall_Shed_Door_Raised_inst', 1615.5, 60.0, 2.
# 26, 2.13, 1.5, 1.5)\n('SM_VK_Wall_Shed_Raised_inst.001', 1615.5, 66.0, 2.26, 2.13, 1.5, 1.5)\n('SM_VK_Wall_Shed_Raised_inst.002', 1612.5, 66.0, 2.26, 
# 2.13, 1.5, 1.5)\n('SM_VK_Wall_Shed_Raised_inst.003', 1611.0, 64.5, 2.26, 2.13, 1.5, 1.5)\n('SM_VK_Wall_Shed_Raised_inst.004', 1611.0, 61.5, 2.26, 2.13

# ==============================================================================================================
# [0056] 2026-09-23 19:24:47  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g30_overview_west",(1555,-30,120),(1555,60,0),lens=28,res=(1600,1000),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g30_overview_west.png\n"}

# ==============================================================================================================
# [0057] 2026-09-23 19:25:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g31_overview_east",(1665,-30,120),(1665,60,0),lens=28,res=(1600,1000),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g31_overview_east.png\n"}

# ==============================================================================================================
# [0058] 2026-09-23 19:25:59  blender  ok
# ==============================================================================================================
import bpy, numpy as np, math
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns['rr_ground_G']
vt=bpy.data.collections['VK_ValleyTown']
trees=[(o.name,o.location.x,o.location.y) for o in vt.all_objects if o.type=='MESH' and ('_Tree_' in o.name or 'Bush_Large' in o.name)]
res=[]
for (j,i) in zip(*np.nonzero(G.ramp)):
    d=int(G.ramp[j,i]); di,dj=((0,1),(1,0),(0,-1),(-1,0))[d-1]
    # ramp axis endpoints: low side cell centre and high side cell centre
    cx,cy=1500+3*i+1.5,3*j+1.5
    for (ex,ey,lab) in ((cx+di*3,cy+dj*3,'top'),(cx-di*3,cy-dj*3,'bottom')):
        for (n,x,y) in trees:
            dd=math.hypot(x-ex,y-ey)
            if dd<2.6: res.append(((i,j),lab,n,round(x,1),round(y,1),round(dd,2)))
for r in res: print(r)
# ---- result ----
# {"result":"Code executed successfully: ((9, 33), 'top', 'SM_VK_Tree_Oak_B_inst.014', 1530.8, 103.4, 2.3)\n"}

# ==============================================================================================================
# [0059] 2026-09-23 19:26:32  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
vt=bpy.data.collections['VK_ValleyTown']
def bb(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(v.x for v in b),max(v.x for v in b),min(v.y for v in b),max(v.y for v in b),min(v.z for v in b),max(v.z for v in b))
walls=[(o.name,bb(o)) for o in vt.all_objects if o.type=='MESH' and ('TownWall' in o.name or 'Gatehouse' in o.name)]
trees=[o for o in vt.all_objects if o.type=='MESH' and '_Tree_' in o.name]
hits=[]
for t in trees:
    x,y=t.location.x,t.location.y
    for (n,w) in walls:
        # trunk inside wall bbox (expanded 0.5) or canopy centre within 2.5 m of wall bbox
        dx=max(w[0]-x,0,x-w[1]); dy=max(w[2]-y,0,y-w[3])
        d=math.hypot(dx,dy)
        if d<2.0: hits.append((t.name,round(x,1),round(y,1),n,round(d,2)))
print(len(hits))
for hh in sorted(hits,key=lambda t:t[4])[:30]: print(hh)
# ---- result ----
# {"result":"Code executed successfully: 0\n"}

# ==============================================================================================================
# [0060] 2026-09-23 19:26:55  blender  ok
# ==============================================================================================================
import bpy, math, numpy as np
vt=bpy.data.collections['VK_ValleyTown']
T=[(o.name,o.location.x,o.location.y) for o in vt.all_objects if o.type=='MESH' and '_Tree_' in o.name]
P=np.array([(x,y) for _,x,y in T])
from itertools import combinations
bad=[]
for a in range(len(T)):
    d=np.hypot(P[:,0]-P[a,0],P[:,1]-P[a,1]); d[a]=99
    for b in np.nonzero(d<1.5)[0]:
        if b>a: bad.append((T[a][0],T[b][0],round(float(d[b]),2)))
print(len(T),len(bad),bad[:10])
# ---- result ----
# {"result":"Code executed successfully: 705 0 []\n"}

# ==============================================================================================================
# [0061] 2026-09-23 19:27:15  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\ground"
print(shot("g32_postern_lane_blocked",(1524,86,6.5),(1540,92,4.0),lens=30,res=(1280,720),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ground\\g32_postern_lane_blocked.png\n"}

# ==============================================================================================================
# [0062] 2026-09-23 19:28:25  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns['rr_ground_G']
vt=bpy.data.collections['VK_ValleyTown']
road=(G.ground==1)|(G.ground==2)|(G.ramp>0)
out=[]
for o in vt.all_objects:
    if o.type!='MESH': continue
    b=o.name.split('_inst')[0]
    if not any(k in b for k in ('Bush_','Plant_','Rock_Boulder','Tree_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in bb)-1500;x1=max(v.x for v in bb)-1500;y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    if 'Tree_' in b:  # trunk only
        x0=x1=o.location.x-1500; y0=y1=o.location.y; pad=0.6
        x0-=pad;x1+=pad;y0-=pad;y1+=pad
    worst=0
    for j in range(max(0,int(y0//3)),min(56,int(y1//3)+1)):
        for i in range(max(0,int(x0//3)),min(72,int(x1//3)+1)):
            if road[j,i]:
                ox=min(x1,3*i+3)-max(x0,3*i); oy=min(y1,3*j+3)-max(y0,3*j)
                worst=max(worst,min(ox,oy))
    if worst>0.8: out.append((o.name,round(o.location.x,1),round(o.location.y,1),round(worst,2)))
print(len(out))
for t in out: print(t)
# ---- result ----
# {"result":"Code executed successfully: 2\n('SM_VK_Bush_Round_inst.025', 1582.9, 26.4, 1.23)\n('SM_VK_Bush_Round_inst.038', 1585.7, 93.3, 1.52)\n"}

# ==============================================================================================================
# [0063] 2026-09-23 19:28:46  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes['VillageKit']; dg=bpy.context.evaluated_depsgraph_get()
def top(x,y):
    r=sc.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name[:30]) if r[0] else None
for (x,y) in ((1545,101.5),(1545,101.0),(1543,101.5),(1547,101.5),(1541.0,98),(1541.0,100),(1549,98),(1549,100),(1541,95.5),(1549,95.5),(1538,95),(1552,95),(1545,102.3),(1545,103)):
    print((x,y),top(x,y))
# ---- result ----
# {"result":"Code executed successfully: (1545, 101.5) (6.0, 'SM_VK_Quarry_Face_Straight_ins')\n(1545, 101.0) (6.0, 'SM_VK_Quarry_Face_Straight_ins')\n(
# 1543, 101.5) (6.0, 'SM_VK_Quarry_Face_InnerCorner_')\n(1547, 101.5) (6.0, 'SM_VK_Quarry_Face_InnerCorner_')\n(1541.0, 98) (6.0, 'SM_VK_Quarry_Face_Str
# aight_ins')\n(1541.0, 100) (6.0, 'SM_VK_Quarry_Face_InnerCorner_')\n(1549, 98) (6.0, 'SM_VK_Quarry_Face_Straight_ins')\n(1549, 100) (6.0, 'SM_VK_Quarr
# y_Face_InnerCorner_')\n(1541, 95.5) (6.27, 'SM_VK_Quarry_Face_Corner_inst.')\n(1549, 95.5) (6.27, 'SM_VK_Quarry_Face_Corner_inst')\n(1538, 95) (6.0, '
# VKV_Chunk_0_2')\n(1552, 95) (6.0, 'VKV_Chunk_1_2')\n(1545, 102.3) (5.99, 'VKV_Chunk_0_2')\n(1545, 103) (6.0, 'VKV_Chunk_0_2')\n"}
