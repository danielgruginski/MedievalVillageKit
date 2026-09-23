# valley-rereview / agent-ada0d012842d11eb2.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 19:29:14  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.context.scene
print(sc.name, [s.name for s in bpy.data.scenes])
print('vk_render' in bpy.data.texts)
names=['LeanTo_inst.010','LampPost_inst.032','LampPost_inst.033','Prop_MarketCross_inst','Prop_Stocks_inst','Porch_inst.031','Porch_inst.032','Prop_BarrelStack_inst.023','Prop_Cart_inst.014','Prop_Woodpile_inst.016','Prop_Woodpile_inst.015','Prop_WeaponRack_inst.009','Corner_Stone_inst.181','Wall_Stone_inst.198','Bush_Round_inst.038','Bush_Round_inst.037','LowWall_inst.035','LowWall_GateArch_inst','Stair_Stone_Ext_inst.001','Wall_Stone_Door_inst.049','Wall_Stone_Door_inst.050']
for n in names:
    o=bpy.data.objects.get(n)
    print(n, None if o is None else (tuple(round(v,2) for v in o.location), round(o.rotation_euler.z,3), o.data.name if o.data else None))
# ---- result ----
# {"result":"Code executed successfully: VillageKit ['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\nTrue\nLeanTo_in
# st.010 None\nLampPost_inst.032 None\nLampPost_inst.033 None\nProp_MarketCross_inst None\nProp_Stocks_inst None\nPorch_inst.031 None\nPorch_inst.032 No
# ne\nProp_BarrelStack_inst.023 None\nProp_Cart_inst.014 None\nProp_Woodpile_inst.016 None\nProp_Woodpile_inst.015 None\nProp_WeaponRack_inst.009 None\n
# Corner_Stone_inst.181 None\nWall_Stone_inst.198 None\nBush_Round_inst.038 None\nBush_Round_inst.037 None\nLowWall_inst.035 None\nLowWall_GateArch_inst
#  None\nStair_Stone_Ext_inst.001 None\nWall_Stone_Door_inst.049 None\nWall_Stone_Door_inst.050 None\n"}

# ==============================================================================================================
# [0002] 2026-09-23 19:29:31  blender  ok
# ==============================================================================================================
import bpy, re
c=bpy.data.collections['VK_ValleyTown']
objs=c.all_objects
print(len(objs))
keys=['LeanTo','LampPost','MarketCross','Stocks','Porch','BarrelStack','Cart','Woodpile','WeaponRack','Bush_Round','LowWall','Stair_Stone_Ext','Door','Corner_Stone']
import collections
for k in keys:
    m=[o.name for o in objs if k in o.name]
    print(k, len(m), m[:6])
# ---- result ----
# {"result":"Code executed successfully: 4584\nLeanTo 12 ['SM_VK_LeanTo_Thatch_Low_inst', 'SM_VK_LeanTo_Thatch_Low_inst.001', 'SM_VK_LeanTo_Thatch_Low_i
# nst.002', 'SM_VK_LeanTo_Thatch_Low_inst.003', 'SM_VK_LeanTo_Thatch_Low_inst.004', 'SM_VK_LeanTo_inst.004']\nLampPost 15 ['SM_VK_Prop_LampPost_inst.019
# ', 'SM_VK_Prop_LampPost_inst.024', 'SM_VK_Prop_LampPost_inst.025', 'SM_VK_Prop_LampPost_inst.026', 'SM_VK_Prop_LampPost_inst.027', 'SM_VK_Prop_LampPos
# t_inst.028']\nMarketCross 2 ['SM_VK_Prop_MarketCross_inst', 'SM_VK_Prop_MarketCross_inst.001']\nStocks 2 ['SM_VK_Prop_Stocks_inst', 'SM_VK_Prop_Stocks
# _inst.001']\nPorch 11 ['SM_VK_Porch_inst.026', 'SM_VK_Porch_inst.027', 'SM_VK_Porch_inst.028', 'SM_VK_Porch_inst.029', 'SM_VK_Porch_inst.030', 'SM_VK_
# Porch_inst.031']\nBarrelStack 17 ['SM_VK_Prop_BarrelStack_inst.007', 'SM_VK_Prop_BarrelStack_inst.009', 'SM_VK_Prop_BarrelStack_inst.010', 'SM_VK_Prop

# ==============================================================================================================
# [0003] 2026-09-23 19:29:51  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
def bb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [round(min(c[k] for c in cs),2) for k in range(3)]+[round(max(c[k] for c in cs),2) for k in range(3)]
names=['LeanTo_inst.010','Prop_LampPost_inst.032','Prop_LampPost_inst.033','Prop_MarketCross_inst','Prop_MarketCross_inst.001','Prop_Stocks_inst','Prop_Stocks_inst.001','Porch_inst.031','Porch_inst.032','Prop_BarrelStack_inst.023','Prop_Cart_inst.014','Prop_Woodpile_inst.016','Prop_Woodpile_inst.015','Prop_WeaponRack_inst.009','Corner_Stone_inst.181','Wall_Stone_inst.198','Bush_Round_inst.038','Bush_Round_inst.037','LowWall_inst.035','LowWall_GateArch_inst','Stair_Stone_Ext_inst.001','Wall_Stone_Door_inst.049','Wall_Stone_Door_inst.050','Prop_CiderPress_inst']
for n in names:
    o=bpy.data.objects.get('SM_VK_'+n)
    if o is None: print(n,'MISSING'); continue
    print(n, tuple(round(v,2) for v in o.location), round(o.rotation_euler.z,3), bb(o))
# ---- result ----
# {"result":"Code executed successfully: LeanTo_inst.010 (1539.0, 93.65, 3.0) 0.0 [1537.3, 89.84, 3.0, 1540.7, 93.81, 6.53]\nProp_LampPost_inst.032 (165
# 5.8, 95.4, 3.0) 0.0 [1655.58, 94.57, 3.0, 1656.03, 95.62, 5.9]\nProp_LampPost_inst.033 (1662.2, 95.4, 3.0) 0.0 [1661.97, 94.57, 3.0, 1662.42, 95.62, 5
# .9]\nProp_MarketCross_inst (1654.9, 95.6, 3.0) 0.0 [1653.2, 93.9, 2.4, 1656.6, 97.3, 9.04]\nProp_MarketCross_inst.001 (1626.0, 100.5, 3.0) 0.0 [1624.3
# , 98.8, 2.4, 1627.7, 102.2, 9.04]\nProp_Stocks_inst (1663.3, 94.6, 3.0) -0.262 [1662.07, 93.78, 2.4, 1664.59, 95.6, 4.05]\nProp_Stocks_inst.001 (1630.
# 0, 105.5, 3.0) 3.142 [1628.86, 104.77, 2.4, 1631.13, 106.04, 4.05]\nPorch_inst.031 (1672.5, 114.0, 3.0) 0.0 [1670.95, 111.74, 2.99, 1674.05, 114.02, 6
# .33]\nPorch_inst.032 (1669.5, 126.0, 3.0) 0.0 [1667.95, 123.74, 2.99, 1671.05, 126.02, 6.33]\nProp_BarrelStack_inst.023 (1674.32, 112.4, 3.0) 0.262 [1

# ==============================================================================================================
# [0004] 2026-09-23 19:30:11  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
chunks=[o for o in bpy.data.collections['VK_ValleyTerrain'].all_objects if o.name.startswith('VKV_Chunk') and o.type=='MESH']
def bbx(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs),min(c.y for c in cs),max(c.x for c in cs),max(c.y for c in cs))
cb=[(o,bbx(o)) for o in chunks]
dg=bpy.context.evaluated_depsgraph_get()
def ground(x,y):
    best=None
    for o,b in cb:
        if b[0]-0.1<=x<=b[2]+0.1 and b[1]-0.1<=y<=b[3]+0.1:
            mi=o.matrix_world.inverted()
            org=mi@Vector((x,y,100)); d=(mi.to_3x3()@Vector((0,0,-1))).normalized()
            ok,loc,n,idx=o.ray_cast(org,d)
            if ok:
                z=(o.matrix_world@loc).z
                if best is None or z>best: best=z
    return best
print(len(chunks))
for y in (88.5,90.5,91.5,92.5):
    print(y, [(x, round(ground(x,y),2)) for x in range(1526,1572,2)])
# ---- result ----
# {"result":"Code executed successfully: 20\n88.5 [(1526, 3.0), (1528, 3.0), (1530, 3.0), (1532, 3.0), (1534, 3.0), (1536, 3.0), (1538, 3.0), (1540, 3.0
# ), (1542, 3.0), (1544, 3.0), (1546, 3.0), (1548, 3.0), (1550, 3.0), (1552, 3.0), (1554, 3.0), (1556, 3.0), (1558, 3.0), (1560, 3.0), (1562, 3.0), (156
# 4, 3.0), (1566, 3.0), (1568, 3.0), (1570, 3.0)]\n90.5 [(1526, 3.0), (1528, 3.0), (1530, 3.0), (1532, 3.0), (1534, 6.0), (1536, 6.0), (1538, 6.0), (154
# 0, 3.0), (1542, 3.0), (1544, 3.0), (1546, 3.0), (1548, 3.0), (1550, 3.0), (1552, 6.0), (1554, 6.0), (1556, 6.0), (1558, 3.0), (1560, 3.0), (1562, 3.0)
# , (1564, 3.0), (1566, 3.0), (1568, 3.0), (1570, 3.0)]\n91.5 [(1526, 3.0), (1528, 3.0), (1530, 3.0), (1532, 3.0), (1534, 6.0), (1536, 6.0), (1538, 6.0)
# , (1540, 3.0), (1542, 3.0), (1544, 3.0), (1546, 3.0), (1548, 3.0), (1550, 3.0), (1552, 6.0), (1554, 6.0), (1556, 6.0), (1558, 3.0), (1560, 3.0), (1562

# ==============================================================================================================
# [0005] 2026-09-23 19:30:35  blender  ok
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
# [0006] 2026-09-23 19:30:46  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
p=shot("v01_postern_lane_quarry",(1552,66,26),(1548,92,4),lens=32,res=(1280,720),outdir=OD)
print(p, time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v01_postern_lane_quarry.png 3.3037540912628174\n"}

# ==============================================================================================================
# [0007] 2026-09-23 19:31:43  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def wbvh(o):
    me=o.data; M=o.matrix_world
    vs=[M@v.co for v in me.vertices]; ps=[tuple(p.vertices) for p in me.polygons]
    return BVHTree.FromPolygons(vs,ps)
def ov(a,b):
    A=bpy.data.objects['SM_VK_'+a]; B=bpy.data.objects['SM_VK_'+b]
    r=BVHTree.overlap(wbvh(A),wbvh(B))
    return len(r)
pairs=[('Prop_LampPost_inst.032','Prop_MarketCross_inst'),('Prop_LampPost_inst.033','Prop_Stocks_inst'),
('Prop_BarrelStack_inst.023','Porch_inst.031'),('Prop_CiderPress_inst','Porch_inst.031'),('Prop_Cart_inst.014','Prop_BarrelStack_inst.023'),
('Prop_Woodpile_inst.016','Porch_inst.032'),('Prop_WeaponRack_inst.009','Corner_Stone_inst.181'),('Prop_WeaponRack_inst.009','Wall_Stone_inst.198'),
('Bush_Round_inst.037','LowWall_inst.035'),('Bush_Round_inst.037','LowWall_GateArch_inst'),('Prop_Woodpile_inst.015','Stair_Stone_Ext_inst.001'),('Bush_Round_inst.038','Prop_Woodpile_inst.015')]
for a,b in pairs:
    print(a,b,ov(a,b))
# market cross plinth height under lamp
mc=bpy.data.objects['SM_VK_Prop_MarketCross_inst']
t=wbvh(mc)
for (x,y) in ((1655.8,95.4),(1655.8,95.0),(1655.58,95.4),(1656.03,95.4)):
    h=t.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))
    print('mc top at',x,y,h[0].z if h[0] else None)
st=bpy.data.objects['SM_VK_Prop_Stocks_inst']; t2=wbvh(st)
for (x,y) in ((1662.2,95.4),(1662.2,95.0),(1662.4,95.2),(1662.0,95.6)):
    h=t2.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))
    print('stocks top at',x,y,h[0].z if h[0] else None)
# ---- result ----
# {"result":"Code executed successfully: Prop_LampPost_inst.032 Prop_MarketCross_inst 84\nProp_LampPost_inst.033 Prop_Stocks_inst 15\nProp_BarrelStack_i
# nst.023 Porch_inst.031 62\nProp_CiderPress_inst Porch_inst.031 27\nProp_Cart_inst.014 Prop_BarrelStack_inst.023 23\nProp_Woodpile_inst.016 Porch_inst.
# 032 84\nProp_WeaponRack_inst.009 Corner_Stone_inst.181 191\nProp_WeaponRack_inst.009 Wall_Stone_inst.198 68\nBush_Round_inst.037 LowWall_inst.035 200\
# nBush_Round_inst.037 LowWall_GateArch_inst 0\nProp_Woodpile_inst.015 Stair_Stone_Ext_inst.001 88\nBush_Round_inst.038 Prop_Woodpile_inst.015 0\nmc top
#  at 1655.8 95.4 3.9099998474121094\nmc top at 1655.8 95.0 3.6100006103515625\nmc top at 1655.58 95.4 3.9099998474121094\nmc top at 1656.03 95.4 3.6100
# 006103515625\nstocks top at 1662.2 95.4 None\nstocks top at 1662.2 95.0 None\nstocks top at 1662.4 95.2 3.0695037841796875\nstocks top at 1662.0 95.6 

# ==============================================================================================================
# [0008] 2026-09-23 19:32:20  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v02_festival_lamps",(1659,103,9),(1659,95,3.8),lens=30,res=(1280,720),outdir=OD))
print(shot("v03_brewery_door",(1672.5,104,8),(1672.5,112.5,4),lens=32,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v02_festival_lamps.png\nC:\\Users\\danie\\AppData\\Roaming\\
# Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\
# \build_verify\\v03_brewery_door.png\n6.554494619369507\n"}

# ==============================================================================================================
# [0009] 2026-09-23 19:32:59  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v04_blacksmith_door_rack",(1672,116,8),(1671.5,125.5,4),lens=30,res=(1280,720),outdir=OD))
print(shot("v05_towerhouse_woodpile_bush",(1583,84,10),(1580,94,4),lens=30,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v04_blacksmith_door_rack.png\nC:\\Users\\danie\\AppData\\Roa
# ming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rer
# eview\\build_verify\\v05_towerhouse_woodpile_bush.png\n6.898502826690674\n"}

# ==============================================================================================================
# [0010] 2026-09-23 19:34:05  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v04_blacksmith_door_rack",(1667,119.5,11),(1671.5,125.5,3.5),lens=28,res=(1280,720),outdir=OD))
print(shot("v05_towerhouse_woodpile_bush",(1588,91.5,9),(1580.5,95,3.5),lens=30,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v04_blacksmith_door_rack.png\nC:\\Users\\danie\\AppData\\Roa
# ming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rer
# eview\\build_verify\\v05_towerhouse_woodpile_bush.png\n6.601458311080933\n"}

# ==============================================================================================================
# [0011] 2026-09-23 19:34:59  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
b=bpy.data.objects['SM_VK_Bush_Round_inst.038']
print(b.hide_render, b.hide_get(), b.data.name, len(b.data.vertices), [c.name for c in b.users_collection])
t=time.time()
print(shot("v04_blacksmith_door_rack",(1680,120,7.5),(1672,125.5,4),lens=30,res=(1280,720),outdir=OD))
print(shot("v06_towerhouse_stair_woodpile",(1581.5,90.2,5.5),(1579.5,95.5,4),lens=28,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: False False SM_VK_Bush_Round 735 ['VK_ValleyTown']\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspa
# ces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v04_blac
# ksmith_door_rack.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14
# b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v06_towerhouse_stair_woodpile.png\n6.96696400642395\n"}

# ==============================================================================================================
# [0012] 2026-09-23 19:35:53  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v07_weaponrack_corner",(1675.5,121.5,5.5),(1674.4,126.4,4.0),lens=30,res=(1280,720),outdir=OD))
print(shot("v06_towerhouse_stair_woodpile",(1585,89.5,8.5),(1579.5,95.2,4),lens=30,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v07_weaponrack_corner.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rerevi
# ew\\build_verify\\v06_towerhouse_stair_woodpile.png\n6.640774250030518\n"}

# ==============================================================================================================
# [0013] 2026-09-23 19:36:53  blender  ok
# ==============================================================================================================
import bpy, time
from mathutils import Vector
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
def bb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(c[k] for c in cs) for k in range(3)]+[max(c[k] for c in cs) for k in range(3)]
for o in bpy.data.collections['VK_ValleyTown'].all_objects:
    if o.type!='MESH': continue
    b=bb(o)
    if b[0]<1586 and b[3]>1580 and b[1]<93 and b[4]>88 and b[5]>5: print(o.name,[round(v,1) for v in b])
t=time.time()
print(shot("v06_towerhouse_stair_woodpile",(1584.5,92.5,12),(1580,95,3.5),lens=30,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Corner_Stone_inst.145 [1583.4, 89.3, 2.9, 1584.6, 90.6, 6.0]\nSM_VK_Corner_StoneUp_inst [1583.4, 89.4, 5.
# 9, 1584.5, 90.5, 8.8]\nSM_VK_Corner_StoneUp_inst.004 [1583.4, 89.4, 8.7, 1584.5, 90.5, 11.6]\nSM_VK_Wall_Stone_Shop_inst [1581.0, 89.7, 2.4, 1584.0, 9
# 1.0, 6.0]\nSM_VK_Prop_Sign_inst [1581.1, 90.2, 5.6, 1581.3, 91.3, 6.6]\nSM_VK_Wall_Stone_Door_inst.038 [1578.0, 89.7, 2.9, 1581.0, 90.8, 6.1]\nSM_VK_W
# all_Stone_Window_inst.146 [1583.7, 87.0, 2.9, 1584.8, 90.0, 6.0]\nSM_VK_Wall_StoneUp_Twin_inst [1581.0, 89.7, 5.9, 1584.0, 90.6, 8.8]\nSM_VK_Wall_Ston
# eUp_Loading_inst [1578.0, 89.7, 5.9, 1581.0, 90.9, 8.8]\nSM_VK_Wall_StoneUp_Slit_inst [1583.7, 87.0, 5.9, 1584.5, 90.0, 8.8]\nSM_VK_Wall_StoneUp_Windo
# w_inst.003 [1581.0, 89.7, 8.7, 1584.0, 90.8, 11.6]\nSM_VK_Wall_StoneUp_Loading_inst.001 [1578.0, 89.7, 8.7, 1581.0, 90.9, 11.6]\nSM_VK_Wall_StoneUp_in

# ==============================================================================================================
# [0014] 2026-09-23 19:37:34  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v08_bush038_postern_street",(1595,92.0,7),(1585.7,92.8,3.5),lens=30,res=(1280,720),outdir=OD))
print(shot("v09_bush037_lowwall",(1657.5,88.3,6.5),(1657.8,92.6,3.8),lens=28,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v08_bush038_postern_street.png\nC:\\Users\\danie\\AppData\\R
# oaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\r
# ereview\\build_verify\\v09_bush037_lowwall.png\n6.548356533050537\n"}

# ==============================================================================================================
# [0015] 2026-09-23 19:38:38  blender  ok
# ==============================================================================================================
import bpy, math
objs=list(bpy.data.collections['VK_ValleyTown'].all_objects)
weeds=[o for o in objs if o.name.startswith('SM_VK_Deco_Weeds')]
doors=[o for o in objs if '_Door' in o.name and not o.name.startswith('SM_VK_Prop') and o.type=='MESH']
print(len(weeds),len(doors))
m=weeds[0].data
xs=[v.co.x for v in m.vertices]; ys=[v.co.y for v in m.vertices]; zs=[v.co.z for v in m.vertices]
print('weed local bounds',round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2), len(m.vertices))
hits=[]
for d in doors:
    for w in weeds:
        if (w.location-d.location).length<0.05 and abs(((w.rotation_euler.z-d.rotation_euler.z+math.pi)%(2*math.pi))-math.pi)<0.01:
            hits.append((w.name,d.name,tuple(round(v,2) for v in d.location)))
print(len(hits))
for h in hits: print(h)
# door names with 'Door' but e.g. Shed/ Timber
print(sorted(set(d.data.name for d in doors)))
# ---- result ----
# {"result":"Code executed successfully: 127 53\nweed local bounds -1.6 1.58 -0.87 -0.13 -0.03 0.54 180\n16\n('SM_VK_Deco_Weeds_inst.091', 'SM_VK_Wall_S
# tone_Door_inst.033', (1578.0, 52.5, 0.0))\n('SM_VK_Deco_Weeds_inst.108', 'SM_VK_Wall_Stone_Door_inst.036', (1686.0, 6.0, 1.5))\n('SM_VK_Deco_Weeds_ins
# t.112', 'SM_VK_Wall_Plaster_Door_inst.017', (1509.0, 60.0, 1.5))\n('SM_VK_Deco_Weeds_inst.118', 'SM_VK_Wall_Log_Door_inst', (1504.5, 75.0, 3.0))\n('SM
# _VK_Deco_Weeds_inst.124', 'SM_VK_Wall_Log_Door_inst.001', (1516.5, 78.0, 3.0))\n('SM_VK_Deco_Weeds_inst.129', 'SM_VK_Wall_Shed_Door_inst.001', (1534.5
# , 75.0, 3.0))\n('SM_VK_Deco_Weeds_inst.140', 'SM_VK_Wall_Plaster_Door_inst.020', (1579.5, 126.0, 3.0))\n('SM_VK_Deco_Weeds_inst.145', 'SM_VK_Wall_Plas
# ter_Door_inst.021', (1591.5, 126.0, 3.0))\n('SM_VK_Deco_Weeds_inst.146', 'SM_VK_Wall_Stone_Door_inst.043', (1597.5, 126.0, 3.0))\n('SM_VK_Deco_Weeds_i

# ==============================================================================================================
# [0016] 2026-09-23 19:39:34  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.objects['SM_VK_Deco_Weeds_inst.168'].data
import collections
# cluster by x bins
bins=collections.Counter(round(v.co.x*2)/2 for v in m.vertices)
print(sorted(bins.items()))
# vertices within door opening |x|<0.7
inn=[v.co for v in m.vertices if abs(v.co.x)<0.7]
print(len(inn), [ (round(c.x,2),round(c.y,2),round(c.z,2)) for c in inn[:20]])
print(bpy.data.objects['SM_VK_Deco_Weeds_inst.168'].data.name, bpy.data.objects['SM_VK_Deco_Weeds_inst.173'].data.name)
# ---- result ----
# {"result":"Code executed successfully: [(-1.5, 18), (-1.0, 33), (-0.5, 24), (0.0, 33), (0.5, 21), (1.0, 33), (1.5, 18)]\n72 [(-0.57, -0.52, -0.03), (-
# 0.57, -0.52, 0.16), (-0.57, -0.52, 0.34), (-0.45, -0.51, -0.03), (-0.2, -0.45, -0.03), (-0.45, -0.51, 0.23), (-0.2, -0.45, 0.23), (-0.45, -0.51, 0.49)
# , (-0.2, -0.45, 0.49), (-0.45, -0.84, -0.03), (-0.45, -0.58, -0.03), (-0.45, -0.32, -0.03), (-0.45, -0.84, 0.23), (-0.45, -0.58, 0.23), (-0.45, -0.32,
#  0.23), (-0.45, -0.84, 0.49), (-0.45, -0.58, 0.49), (-0.45, -0.32, 0.49), (-0.52, -0.45, -0.03), (-0.22, -0.5, -0.03)]\nSM_VK_Deco_Weeds SM_VK_Deco_We
# eds\n"}

# ==============================================================================================================
# [0017] 2026-09-23 19:39:49  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v10_brewery_doorstep_weeds",(1672.5,110.6,4.8),(1672.5,113.6,3.4),lens=35,res=(1280,720),outdir=OD))
print(shot("v11_skyline_door_weeds",(1597.5,122.0,5.0),(1597.5,125.6,3.4),lens=35,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v10_brewery_doorstep_weeds.png\nC:\\Users\\danie\\AppData\\R
# oaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\r
# ereview\\build_verify\\v11_skyline_door_weeds.png\n6.426398754119873\n"}

# ==============================================================================================================
# [0018] 2026-09-23 19:40:45  blender  ok
# ==============================================================================================================
import bpy
o=[o for o in bpy.data.collections['VK_ValleyTerrain'].all_objects if o.name.startswith('VKV_Chunk')][0]
m=o.data
print(o.name, [a.name+':'+a.domain+':'+a.data_type for a in m.attributes][:30])
print([s.name if s else None for s in m.materials])
print([k for k in bpy.app.driver_namespace.keys()][:40])
print([t.name for t in bpy.data.texts])
# ---- result ----
# {"result":"Code executed successfully: VKV_Chunk_0_0 ['position:POINT:FLOAT_VECTOR', '.select_vert:POINT:BOOLEAN', '.edge_verts:EDGE:INT32_2D', '.sele
# ct_edge:EDGE:BOOLEAN', 'sharp_edge:EDGE:BOOLEAN', '.select_poly:FACE:BOOLEAN', '.corner_vert:CORNER:INT', '.corner_edge:CORNER:INT', 'custom_normal:CO
# RNER:INT16_2D', 'TCol:CORNER:FLOAT_COLOR']\n['M_VK_TerrainTown', 'M_VKT_Stair']\n['__builtins__', '__name__', '__doc__', '__package__', '__loader__', 
# '__spec__', 'acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'cbrt', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'dist', 'erf', 'erfc', '
# exp', 'exp2', 'expm1', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'gcd', 'hypot', 'isclose', 'isfinite', 'isinf', 'isnan', 'isqrt
# ', 'lcm']\n['mc_helpers', 'README_VillageKit', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_kit', 'vk_leafgen', 'vk_mat', 'vk_mod_construction', '

# ==============================================================================================================
# [0019] 2026-09-23 19:41:13  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\build_verify"
t=time.time()
print(shot("v12_ne_quarter_topdown",(1660,108,62),(1660,108.5,3),lens=35,res=(1280,720),outdir=OD))
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\build_verify\\v12_ne_quarter_topdown.png\n3.2835886478424072\n"}

# ==============================================================================================================
# [0020] 2026-09-23 19:42:06  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
chunks=[o for o in bpy.data.collections['VK_ValleyTerrain'].all_objects if o.name.startswith('VKV_Chunk') and o.type=='MESH']
def bbx(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs),min(c.y for c in cs),max(c.x for c in cs),max(c.y for c in cs))
cb=[(o,bbx(o)) for o in chunks]
def tcol(x,y):
    best=None
    for o,b in cb:
        if b[0]-0.1<=x<=b[2]+0.1 and b[1]-0.1<=y<=b[3]+0.1:
            mi=o.matrix_world.inverted()
            ok,loc,n,idx=o.ray_cast(mi@Vector((x,y,100)),Vector((0,0,-1)))
            if ok:
                z=(o.matrix_world@loc).z
                if best is None or z>best[0]:
                    p=o.data.polygons[idx]; at=o.data.color_attributes['TCol']
                    cols=[tuple(round(c,2) for c in at.data[l].color) for l in p.loop_indices]
                    best=(round(z,2),cols[0])
    return best
print('plaza',tcol(1626.5,100.5),'street',tcol(1627.5,85.5),'lawn',tcol(1680,105),'forecourt',tcol(1648,112),'terrace st',tcol(1660,88.5),'dirt lane',tcol(1545,91.5))
objs=list(bpy.data.collections['VK_ValleyTown'].all_objects)
doors=[o for o in objs if '_Door' in o.name and not o.name.startswith('SM_VK_Prop') and o.type=='MESH' and 1569<o.location.x<1689 and 75<o.location.y<138]
for d in doors:
    r=d.rotation_euler.z; nx,ny=math.sin(r),-math.cos(r)
    fx,fy=d.location.x+nx*1.6,d.location.y+ny*1.6
    print(d.name,tuple(round(v,1) for v in d.location[:2]),(int((fx-1500)//3),int(fy//3)),tcol(fx,fy))
# ---- result ----
# {"result":"Code executed successfully: plaza (3.0, (1.0, 0.0, 0.0, 0.0)) street (3.0, (1.0, 0.0, 0.0, 0.0)) lawn (3.0, (1.0, 0.0, 0.0, 0.0)) forecourt
#  (3.0, (1.0, 0.0, 0.0, 0.0)) terrace st (3.0, (1.0, 0.0, 0.0, 0.0)) dirt lane (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_Timber_Door_inst (1621.5, 76.5) 
# (39, 25) (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_Timber_Door_inst.001 (1630.5, 76.5) (44, 25) (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_Stone_Door_inst.
# 038 (1579.5, 90.0) (26, 30) (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_StoneUp_Door_inst (1579.5, 84.0) (26, 27) (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_
# Plaster_Door_inst.018 (1590.0, 85.5) (29, 28) (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_Plaster_Door_inst.019 (1591.5, 90.0) (30, 30) (3.0, (1.0, 0.0, 0
# .0, 0.0))\nSM_VK_Wall_Stone_Door_inst.039 (1606.5, 90.0) (35, 30) (3.0, (1.0, 0.0, 0.0, 0.0))\nSM_VK_Wall_Timber_Door_inst.002 (1603.5, 84.0) (34, 27)
