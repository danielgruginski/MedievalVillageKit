# village-kit-buildings / agent-a5d0a1f38c90e2f32.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:54:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
print(bpy.app.version_string)
print([s.name for s in bpy.data.scenes])
print([t.name for t in bpy.data.texts])
print(bpy.data.scenes.get("WS_humble"))
g=ws_ns(None)
print("RIDGE",g["RIDGE"],"EAVE",g["EAVE"],"roofz eave",g["roof_z"](g["EAVE"]),"GX",g["GX"],"TRT",g["TRT"])
for n in ["SM_VK_LeanTo_Thatch","SM_VK_Prop_ChickenCoop","SM_VK_Prop_Chickens","SM_VK_RoofThatch_Gable","SM_VK_Prop_Fence","SM_VK_LowWall"]:
    o=bpy.data.objects.get(n); print(n, o and [c.name for c in o.users_collection])
# ---- result ----
# {"result":"Code executed successfully: 4.4.3\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n['mc_helpers', 'tre
# e_build', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex', 'vk_tex2', 'vk_texgen', 'wk_helpers', 'ws_common']\nNone\nRIDG
# E 4.189824896579236 EAVE 4.35 roofz eave -0.30843899456391277 GX 2.45 TRT 0.38\nSM_VK_LeanTo_Thatch ['VK_Pieces']\nSM_VK_Prop_ChickenCoop ['VK_Pieces'
# ]\nSM_VK_Prop_Chickens ['VK_Pieces']\nSM_VK_RoofThatch_Gable ['VK_Pieces']\nSM_VK_Prop_Fence ['VK_Pieces']\nSM_VK_LowWall ['VK_Pieces']\n"}

# ==============================================================================================================
# [0002] 2026-09-23 13:09:26  blender  ERROR
# ==============================================================================================================
import bpy, bmesh
bm=bmesh.new()
for s in (1,2):
    r=bmesh.ops.create_icosphere(bm,subdivisions=s,radius=1.0); print("ico sub",s,len({f for v in r['verts'] for f in v.link_faces}))
bm.free()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns(None)
rz=g["roof_z"]; import math
for ay in (0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.35):
    print(ay, round(rz(ay),3), "thatch underside~", round(rz(ay)-0.38/math.cos(g['PITCH']),3))
o=bpy.data.objects["SM_VK_RoofThatch_Gable"]; import mathutils
zs=[v.co.z for v in o.data.vertices]; print("thatch gable zmin",min(zs),"zmax",max(zs))
o=bpy.data.objects["SM_VK_RoofThatch_Mid"]
vs=[v.co for v in o.data.vertices if abs(v.co.y)>4.0]; print("mid eave zmin",min(v.z for v in vs), "ymax", max(abs(v.y) for v in o.data.vertices))
print(g["TILE"].get(22), g["TILE"].get(47), g["TILE"].get(2), g["TILE"].get(1))
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: 'MeshVertex' object has no attribute 'y'"}

# ==============================================================================================================
# [0003] 2026-09-23 13:09:42  blender  ok
# ==============================================================================================================
import bpy, bmesh, math
bm=bmesh.new()
for s in (1,2):
    r=bmesh.ops.create_icosphere(bm,subdivisions=s,radius=1.0); print("ico sub",s,len({f for v in r['verts'] for f in v.link_faces}))
bm.free()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns(None)
rz=g["roof_z"]
for ay in (0,1.5,3.0,3.5,4.0,4.35):
    print(ay, round(rz(ay),3), "thatch underside~", round(rz(ay)-0.38/math.cos(g['PITCH']),3))
o=bpy.data.objects["SM_VK_RoofThatch_Mid"]
vs=[v.co for v in o.data.vertices if abs(v.co.y)>4.0]; print("mid eave zmin",min(v.z for v in vs), "ymax", max(abs(v.co.y) for v in o.data.vertices))
print(g["TILE"].get(22), g["TILE"].get(47), g["TILE"].get(2), g["TILE"].get(1))
# ---- result ----
# {"result":"Code executed successfully: ico sub 1 20\nico sub 2 80\n0 4.19 thatch underside~ 3.573\n1.5 2.27 thatch underside~ 1.653\n3.0 0.35 thatch u
# nderside~ -0.267\n3.5 0.106 thatch underside~ -0.511\n4.0 -0.138 thatch underside~ -0.755\n4.35 -0.308 thatch underside~ -0.926\nmid eave zmin -0.7086
# 042165756226 ymax 4.4592695236206055\n3.0 1.0 1.6 2.2\n"}

# ==============================================================================================================
# [0004] 2026-09-23 13:14:23  blender  ok
# ==============================================================================================================
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble") or bpy.data.texts.new("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
t0=time.time()
objs=[]
for n,fn,kw in g["WS_SPECS"]:
    try:
        objs+=ws_build("humble",names=[n],g=g)
    except Exception as e:
        print("FAIL",n,repr(e)); traceback.print_exc()
print("time",round(time.time()-t0,2))
for s in ws_stats(objs): print(s)
# ---- result ----
# {"result":"Code executed successfully: time 0.74\n{'name': 'SM_VK_Wall_Wattle', 'tris': 1854, 'bbox': [3.13, 0.52, 3.0], 'zmin': -0.6, 'mats': [0, 1, 
# 2, 45, 47]}\n{'name': 'SM_VK_Wall_Wattle_Window', 'tris': 2487, 'bbox': [3.13, 0.96, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 23, 27, 40, 45, 47]}\n{'
# name': 'SM_VK_Wall_Wattle_Door', 'tris': 2489, 'bbox': [3.13, 1.42, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 23, 27, 45, 47]}\n{'name': 'SM_VK_Wall_Wa
# ttle_Byre', 'tris': 3408, 'bbox': [3.13, 1.94, 3.0], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 16, 23, 26, 27, 45]}\n{'name': 'SM_VK_Wall_Wattle_Frame', 'tri
# s': 1652, 'bbox': [3.13, 0.96, 3.0], 'zmin': -0.6, 'mats': [0, 2, 25, 45, 47]}\n{'name': 'SM_VK_Corner_Wattle', 'tris': 660, 'bbox': [0.76, 0.8, 3.01]
# , 'zmin': -0.6, 'mats': [0, 2, 45]}\n{'name': 'SM_VK_InnerCorner_Wattle', 'tris': 216, 'bbox': [0.45, 0.44, 2.45], 'zmin': -0.04, 'mats': [2, 45]}\n{'

# ==============================================================================================================
# [0005] 2026-09-23 13:15:29  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("humble")
pos={"SM_VK_Wall_Wattle":(0,0,0),"SM_VK_Wall_Wattle_Window":(3.6,0,0),"SM_VK_Wall_Wattle_Door":(7.2,0,0),"SM_VK_Wall_Wattle_Byre":(10.8,0,0),
"SM_VK_Wall_Wattle_Frame":(14.4,0,0),"SM_VK_Corner_Wattle":(17.2,0,0),"SM_VK_InnerCorner_Wattle":(18.6,0,0),
"SM_VK_RoofThatch_Gable_Cruck":(1.5,-9,2.4),"SM_VK_RoofThatch_Vent":(6.5,-7,0.4),"SM_VK_LeanTo_Thatch_Low":(10.5,-6.5,0),
"SM_VK_Prop_HayRack":(15,-8,0),"SM_VK_Prop_ChickenCoop_Wattle":(18.5,-8,0),
"SM_VK_Animal_Cow":(0,-15,0),"SM_VK_Animal_Horse":(4,-15,0),"SM_VK_Animal_Sheep":(8,-15,0),"SM_VK_Animal_Pig":(10.5,-15,0),
"SM_VK_Animal_Goat":(13,-15,0),"SM_VK_Animal_Chickens":(16,-15,0)}
for n,p in pos.items(): bpy.data.objects[n].location=p
p=ws_shot("humble","catalog_v1",(9,-34,16),(9.5,-7,0.8),lens=32)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\catalog_v1.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 13:16:03  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects["SM_VK_Animal_Cow"]
for i in (17,27,48,49,50,12,15,14):
    m=o.data.materials[i]
    nt=m.node_tree
    info=[]
    for nd in nt.nodes:
        if nd.type=="MIX": info.append(("mix",tuple(round(x,3) for x in nd.inputs[6].default_value),tuple(round(x,3) for x in nd.inputs[7].default_value), nd.blend_type))
        if nd.type=="BSDF_PRINCIPLED": info.append(("bsdf",tuple(round(x,3) for x in nd.inputs["Base Color"].default_value), [l.from_node.type for l in nd.inputs["Base Color"].links]))
        if nd.type=="TEX_IMAGE": info.append(("img",nd.image.name if nd.image else None))
    print(i,m.name,info)
# ---- result ----
# {"result":"Code executed successfully: 17 M_VK_Paper [('bsdf', (0.8, 0.8, 0.8, 1.0), ['MIX']), ('img', 'T_VK_Paper_BC'), ('img', 'T_VK_Paper_N'), ('im
# g', 'T_VK_Paper_R'), ('mix', (0.5, 0.5, 0.5, 1.0), (0.5, 0.5, 0.5, 1.0), 'MULTIPLY')]\n27 M_VK_Void [('bsdf', (0.015, 0.012, 0.01, 1.0), [])]\n48 M_VK
# _Hide [('bsdf', (0.8, 0.8, 0.8, 1.0), ['MIX']), ('mix', (0.5, 0.33, 0.2, 1.0), (0.5, 0.5, 0.5, 1.0), 'MULTIPLY')]\n49 M_VK_Pigskin [('bsdf', (0.8, 0.8
# , 0.8, 1.0), ['MIX']), ('mix', (0.9, 0.62, 0.56, 1.0), (0.5, 0.5, 0.5, 1.0), 'MULTIPLY')]\n50 M_VK_Coal [('bsdf', (0.8, 0.8, 0.8, 1.0), ['MIX']), ('mi
# x', (0.045, 0.043, 0.05, 1.0), (0.5, 0.5, 0.5, 1.0), 'MULTIPLY')]\n12 M_VK_Cloth_Cream [('bsdf', (0.8, 0.8, 0.8, 1.0), ['MIX']), ('img', 'T_VK_Cloth_B
# C'), ('img', 'T_VK_Cloth_N'), ('img', 'T_VK_Cloth_R'), ('mix', (0.5, 0.5, 0.5, 1.0), (1.0, 0.93, 0.74, 1.0), 'MULTIPLY'), ('mix', (0.5, 0.5, 0.5, 1.0)

# ==============================================================================================================
# [0007] 2026-09-23 13:16:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("humble","walls_v1",(7.5,-7.5,2.6),(7.3,0,1.2),lens=30)
p2=ws_shot("humble","animals_v1",(8,-19.5,2.2),(8,-15,0.7),lens=30)
print(p,p2)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\walls_v1.png C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\
# \ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\animals_v1.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 13:17:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
# put a wall pair under the roof master to judge the gable in context
sc,coll,asm=ws_scene("humble")
ws_clear_assembly("humble")
g=ws_ns("humble")
o=(40,0,0)
g["hum_block"](asm,o,2,{"F":".W","B":"..","L":"..","R":"DW"},vents=(0,))
p=ws_shot("humble","gable_v1",(52,-6,4.5),(43,0,2.8),lens=35)
p2=ws_shot("humble","hovel_v1",(52,-14,11),(40,0,2.0),lens=35)
print(p,p2)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\gable_v1.png C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\
# \ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\hovel_v1.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 13:18:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
a=ws_shot("humble","cowhorse_v1",(2.5,-20.5,2.4),(2.3,-15,0.9),lens=35)
b=ws_shot("humble","goatchick_v1",(14.5,-18.6,1.8),(14.6,-15,0.4),lens=35)
c=ws_shot("humble","props_v1",(14,-15,4.5),(14,-7.5,1.2),lens=35)
print(a,b,c)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\cowhorse_v1.png C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspac
# es\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\goatchick_v1.png C:\\User
# s\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23
# -d49817\\renders2\\humble\\props_v1.png\n"}

# ==============================================================================================================
# [0010] 2026-09-23 13:23:41  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble",g=g)
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
# animals line-up for closeups
lay={"SM_VK_Animal_Cow":(0,-15,0),"SM_VK_Animal_Horse":(3.2,-15,0),"SM_VK_Animal_Sheep":(6.2,-15,0),"SM_VK_Animal_Pig":(8.2,-15,0),
"SM_VK_Animal_Goat":(10.2,-15,0),"SM_VK_Animal_Chickens":(12.4,-15,0)}
for n,p in lay.items(): bpy.data.objects[n].location=p
for o in objs:
    if o.name.startswith("SM_VK_Animal"): o.rotation_euler=(0,0,0.5)
a=ws_shot("humble","animals_v2a",(3.2,-21.5,2.6),(2.6,-15,1.0),lens=35)
b=ws_shot("humble","animals_v2b",(10.2,-19.5,1.9),(10.4,-15,0.5),lens=35)
print(a,b)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Wattle 1894 [3.13, 0.52, 3.0]\nSM_VK_Wall_Wattle_Window 2507 [3.13, 0.96, 3.0]\nSM_VK_Wall_Wattle_Do
# or 2509 [3.13, 1.42, 3.0]\nSM_VK_Wall_Wattle_Byre 2900 [3.13, 1.94, 3.0]\nSM_VK_Wall_Wattle_Frame 1652 [3.13, 0.96, 3.0]\nSM_VK_Corner_Wattle 660 [0.7
# 6, 0.8, 3.01]\nSM_VK_InnerCorner_Wattle 216 [0.45, 0.44, 2.45]\nSM_VK_RoofThatch_Gable_Cruck 5118 [4.18, 9.11, 6.87]\nSM_VK_RoofThatch_Vent 808 [1.73,
#  1.29, 2.04]\nSM_VK_LeanTo_Thatch_Low 2330 [3.73, 3.44, 3.66]\nSM_VK_Animal_Cow 2224 [2.61, 0.88, 1.52]\nSM_VK_Animal_Sheep 1172 [1.45, 0.83, 1.07]\nS
# M_VK_Animal_Pig 1254 [1.67, 0.74, 0.85]\nSM_VK_Animal_Goat 1264 [1.31, 0.47, 1.33]\nSM_VK_Animal_Horse 2168 [2.91, 0.82, 2.46]\nSM_VK_Animal_Chickens 
# 2840 [1.96, 1.66, 0.71]\nSM_VK_Prop_HayRack 3396 [2.79, 2.06, 2.69]\nSM_VK_Prop_ChickenCoop_Wattle 1535 [1.99, 2.58, 2.29]\nC:\\Users\\danie\\AppData\

# ==============================================================================================================
# [0011] 2026-09-23 13:26:41  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
objs=ws_build("humble",g=g)
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
a=ws_shot("humble","animals_v3a",(3.4,-21.0,2.4),(2.4,-15,1.0),lens=35)
b=ws_shot("humble","animals_v3b",(10.8,-19.0,1.7),(11.0,-15,0.45),lens=35)
print(a,b)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Wattle 1894 [3.13, 0.52, 3.0]\nSM_VK_Wall_Wattle_Window 2507 [3.13, 0.96, 3.0]\nSM_VK_Wall_Wattle_Do
# or 2509 [3.13, 1.42, 3.0]\nSM_VK_Wall_Wattle_Byre 2900 [3.13, 1.94, 3.0]\nSM_VK_Wall_Wattle_Frame 1652 [3.13, 0.96, 3.0]\nSM_VK_Corner_Wattle 660 [0.7
# 6, 0.8, 3.01]\nSM_VK_InnerCorner_Wattle 216 [0.45, 0.44, 2.45]\nSM_VK_RoofThatch_Gable_Cruck 5118 [4.18, 9.11, 6.87]\nSM_VK_RoofThatch_Vent 808 [1.73,
#  1.29, 2.04]\nSM_VK_LeanTo_Thatch_Low 2330 [3.73, 3.44, 3.66]\nSM_VK_Animal_Cow 2028 [2.61, 1.03, 1.57]\nSM_VK_Animal_Sheep 1172 [1.45, 0.83, 1.07]\nS
# M_VK_Animal_Pig 1254 [1.67, 0.74, 0.85]\nSM_VK_Animal_Goat 1264 [1.31, 0.47, 1.33]\nSM_VK_Animal_Horse 1836 [2.95, 0.89, 2.52]\nSM_VK_Animal_Chickens 
# 2414 [1.91, 1.56, 0.71]\nSM_VK_Prop_HayRack 2940 [2.79, 2.06, 2.69]\nSM_VK_Prop_ChickenCoop_Wattle 1535 [1.99, 2.58, 2.29]\nC:\\Users\\danie\\AppData\

# ==============================================================================================================
# [0012] 2026-09-23 13:27:23  blender  ok
# ==============================================================================================================
import bpy, math, traceback
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("humble")
sc,coll,asm=ws_scene("humble")
ws_clear_assembly("humble")
try:
    g["build_hovel"](asm,(40,0,0),seed=1,variant="cruck")
    g["build_hovel"](asm,(40,17,0),seed=2,variant="leanto")
    g["build_hovel"](asm,(40,34,0),seed=3,variant="hip")
    g["build_longhouse"](asm,(72,0,0),seed=4)
    g["build_pigsty"](asm,(40,-18,0),seed=5)
    g["build_sheepfold"](asm,(56,-18,0),seed=6)
except Exception as e:
    traceback.print_exc()
print(len(asm.objects))
a=ws_shot("humble","asm_v1",(28,-40,34),(58,5,0),lens=30)
print(a)
# ---- result ----
# {"result":"Code executed successfully: 175\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8dd
# c2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\asm_v1.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 13:28:30  blender  ok
# ==============================================================================================================
import bpy, math, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_humble.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_humble"); t.clear(); t.write(src)
g=ws_ns("humble")
sc,coll,asm=ws_scene("humble")
ws_clear_assembly("humble")
g["build_hovel"](asm,(0,18,0),seed=1,variant="cruck")
g["build_hovel"](asm,(16,18,0),seed=2,variant="leanto")
g["build_hovel"](asm,(32,18,0),seed=3,variant="hip")
g["build_longhouse"](asm,(8,38,0),seed=4)
g["build_pigsty"](asm,(-18,18,0),seed=5)
g["build_sheepfold"](asm,(-18,34,0),seed=6)
a=ws_shot("humble","hovel_v2",(14,4,9),(1.5,18.5,1.8),lens=35)
b=ws_shot("humble","hovel_leanto_v2",(5,8,5.5),(14,18,2.0),lens=35)
print(a,b)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\hovel_v2.png C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\
# \ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\hovel_leanto_v2.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 13:29:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
a=ws_shot("humble","longhouse_v1",(24,22,13),(14,38,1.5),lens=32)
b=ws_shot("humble","pens_v1",(-6,8,11),(-18,26,0.8),lens=32)
print(a,b)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\longhouse_v1.png C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspa
# ces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\humble\\pens_v1.png\n"}
