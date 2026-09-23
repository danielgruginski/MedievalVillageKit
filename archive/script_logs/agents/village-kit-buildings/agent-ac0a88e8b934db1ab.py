# village-kit-buildings / agent-ac0a88e8b934db1ab.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:54:12  blender  ok
# ==============================================================================================================
import bpy
print([s.name for s in bpy.data.scenes])
print([t.name for t in bpy.data.texts])
print(bpy.data.texts.get("ws_defence"))
for n in ["SM_VK_Roof_Hip","SM_VK_GuardTower","SM_VK_Wall_Stone","SM_VK_Corner_Stone","SM_VK_LowWall","SM_VK_Wall_StoneUp","SM_VK_Turret_Seg_Stone","SM_VK_Banner_Roof","SM_VK_Roof_Hip_Plain","SM_VK_Stair_Stone_Ext","SM_VK_Prop_Bunting_6"]:
    o=bpy.data.objects.get(n); print(n, o and [c.name for c in o.users_collection])
print(bpy.app.version_string)
# ---- result ----
# {"result":"Code executed successfully: ['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n['mc_helpers', 'tree_build
# ', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex', 'vk_tex2', 'vk_texgen', 'wk_helpers', 'ws_common']\nNone\nSM_VK_Roof_
# Hip ['VK_Pieces']\nSM_VK_GuardTower ['VK_Pieces']\nSM_VK_Wall_Stone ['VK_Pieces']\nSM_VK_Corner_Stone ['VK_Pieces']\nSM_VK_LowWall ['VK_Pieces']\nSM_V
# K_Wall_StoneUp None\nSM_VK_Turret_Seg_Stone None\nSM_VK_Banner_Roof None\nSM_VK_Roof_Hip_Plain None\nSM_VK_Stair_Stone_Ext None\nSM_VK_Prop_Bunting_6 
# None\n4.4.3\n"}

# ==============================================================================================================
# [0002] 2026-09-23 12:59:48  blender  ok
# ==============================================================================================================
import bpy
print(sorted(i.name for i in bpy.data.images if i.name.startswith("T_VK")))
for m in ["M_VK_BarkOak","M_VK_Leaves","M_VK_Foliage","M_VK_EndGrain","M_VK_Moss"]:
    mm=bpy.data.materials.get(m)
    if mm and mm.use_nodes:
        print(m,[ (n.type, getattr(getattr(n,'image',None),'name',None)) for n in mm.node_tree.nodes if n.type in ('TEX_IMAGE','BSDF_PRINCIPLED')])
sc=bpy.data.scenes["VillageKit"]; print(sc.render.engine, sc.render.resolution_x, sc.render.resolution_y)
# ---- result ----
# {"result":"Code executed successfully: ['T_VK_Ashlar_AO', 'T_VK_Ashlar_BC', 'T_VK_Ashlar_H', 'T_VK_Ashlar_N', 'T_VK_Ashlar_R', 'T_VK_BarkBirch_AO', 'T
# _VK_BarkBirch_BC', 'T_VK_BarkBirch_H', 'T_VK_BarkBirch_N', 'T_VK_BarkBirch_R', 'T_VK_BarkOak_AO', 'T_VK_BarkOak_BC', 'T_VK_BarkOak_H', 'T_VK_BarkOak_N
# ', 'T_VK_BarkOak_R', 'T_VK_BarkPine_AO', 'T_VK_BarkPine_BC', 'T_VK_BarkPine_H', 'T_VK_BarkPine_N', 'T_VK_BarkPine_R', 'T_VK_Burlap_BC', 'T_VK_Burlap_N
# ', 'T_VK_Burlap_R', 'T_VK_Clock_BC', 'T_VK_Clock_N', 'T_VK_Clock_R', 'T_VK_Cloth_BC', 'T_VK_Cloth_N', 'T_VK_Cloth_R', 'T_VK_Crops_BCA', 'T_VK_EndGrain
# _AO', 'T_VK_EndGrain_BC', 'T_VK_EndGrain_H', 'T_VK_EndGrain_N', 'T_VK_EndGrain_R', 'T_VK_FieldStone_AO', 'T_VK_FieldStone_BC', 'T_VK_FieldStone_H', 'T
# _VK_FieldStone_N', 'T_VK_FieldStone_R', 'T_VK_Foliage_BCA', 'T_VK_Iron_BC', 'T_VK_Iron_M', 'T_VK_Iron_N', 'T_VK_Iron_R', 'T_VK_Leaves_BCA', 'T_VK_Leav

# ==============================================================================================================
# [0003] 2026-09-23 13:03:42  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
g=ws_ns("defence")
t0=time.time()
objs=ws_build("defence",g=g)
ws_grid(objs,cols=5,sx=7,sy=9)
for s in ws_stats(objs): print(s)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Palisade_Straight', 'tris': 1338, 'bbox': [3.02, 0.51, 4.68], 'zmin': -0.8, 'mats': [2, 25, 33]
# }\n{'name': 'SM_VK_Palisade_Diag', 'tris': 1838, 'bbox': [4.25, 0.49, 4.67], 'zmin': -0.8, 'mats': [2, 25, 33]}\n{'name': 'SM_VK_Palisade_Post', 'tris
# ': 654, 'bbox': [1.0, 1.0, 5.0], 'zmin': -0.8, 'mats': [2, 25, 33]}\n{'name': 'SM_VK_Palisade_Walk', 'tris': 816, 'bbox': [3.11, 1.1, 2.9], 'zmin': -0
# .6, 'mats': [2, 23, 33, 40]}\n{'name': 'SM_VK_Palisade_Ladder', 'tris': 248, 'bbox': [0.64, 0.87, 2.91], 'zmin': -0.01, 'mats': [2]}\n{'name': 'SM_VK_
# Palisade_Gate', 'tris': 1828, 'bbox': [4.12, 0.91, 6.1], 'zmin': -0.9, 'mats': [2, 5, 9, 11, 25, 33, 40]}\n{'name': 'SM_VK_Palisade_GateLeaf', 'tris':
#  820, 'bbox': [1.51, 0.55, 3.35], 'zmin': 0.05, 'mats': [2, 5, 33]}\n{'name': 'SM_VK_Palisade_Tower', 'tris': 3634, 'bbox': [4.17, 4.17, 10.75], 'zmin

# ==============================================================================================================
# [0004] 2026-09-23 13:03:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("defence","pal_v1",(14,-30,13),(14,-4.5,2.2),lens=32)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\defence\\pal_v1.png\n"}

# ==============================================================================================================
# [0005] 2026-09-23 13:04:31  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
ws_clear_assembly("defence")
O=(0,30,0); P=lambda n,x,y,z,r: g["place_v"](asm,n,x,y,z,r,O,{})
for x in (-4.5,-1.5,4.5,7.5): P("SM_VK_Palisade_Straight",x,0,0,0)
P("SM_VK_Palisade_Gate",1.5,0,0,0)
l=P("SM_VK_Palisade_GateLeaf",1.5-1.45,0.35,0,-70); r=P("SM_VK_Palisade_GateLeaf",1.5+1.45,0.35,0,180+25)
for x in (-4.5,-1.5,4.5): P("SM_VK_Palisade_Walk",x,0,0,0)
P("SM_VK_Palisade_Ladder",-3.5,0,0,0)
P("SM_VK_Palisade_Tower",-6,0,0,0)
P("SM_VK_Palisade_Post",9,0,0,0)
P("SM_VK_Palisade_Straight",9,1.5,0,90)
P("SM_VK_Palisade_Straight",-6,1.5,0,-90)
P("SM_VK_Prop_Beacon",6,4,0,0)
p=ws_shot("defence","pal_asm_v1",(4,12,7),(0,30,2.2),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0006] 2026-09-23 13:05:02  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
K=g["Kit"]; k=K()
mats=[("BARK_OAK","WOOD"),("BARK_OAK","ENDGRAIN"),("BARK_PINE","ENDGRAIN"),("BARK_MOSSY","ENDGRAIN"),("BARK_PINE","PLANKS"),("BARK_OAK","BREAD"),("BARK_BIRCH","ENDGRAIN")]
for i,(b,t) in enumerate(mats):
    for j in range(3):
        x=i*1.2+j*0.32
        g["def_log"](k,(x,0,-0.5),(x,0,3.2),0.15,segs=9,mi=g[b],tip=0.45,tip_mi=g[t],seed=i*5+j,bend=0.03)
o=k.finish("DEFTEST_logs",coll,wobble=False,grime=True)
o.location=(0,60,0)
for p in o.data.polygons: p.use_smooth=False
p=ws_shot("defence","logtest",(4,54,2.8),(4,60,2.2),lens=45)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0007] 2026-09-23 13:05:33  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects.get("DEFTEST_logs")
if o:
    me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0008] 2026-09-23 13:06:56  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
g=ws_ns("defence")
objs=ws_build("defence",g=g)
ws_grid(objs,cols=5,sx=7,sy=9)
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
p=ws_shot("defence","pal_asm_v2",(4,12,7),(0,30,2.2),lens=30)
p=ws_shot("defence","pal_asm_v2b",(-12,40,9),(-3,29,3.5),lens=35)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Palisade_Straight 1338 [3.0, 0.5, 4.68]\nSM_VK_Palisade_Diag 1838 [4.27, 0.51, 4.7]\nSM_VK_Palisade_Post 
# 654 [1.0, 1.0, 5.0]\nSM_VK_Palisade_Walk 816 [3.11, 1.1, 2.9]\nSM_VK_Palisade_Ladder 248 [0.64, 0.87, 2.91]\nSM_VK_Palisade_Gate 2372 [4.12, 0.94, 6.1
# ]\nSM_VK_Palisade_GateLeaf 820 [1.51, 0.55, 3.35]\nSM_VK_Palisade_Tower 4842 [4.38, 4.38, 11.66]\nSM_VK_Prop_Beacon 2027 [2.7, 2.57, 7.65]\n"}

# ==============================================================================================================
# [0009] 2026-09-23 13:14:15  blender  ok
# ==============================================================================================================
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
g=ws_ns("defence")
names=[n for n,_,_ in g["WS_SPECS"]][9:]
t0=time.time()
for n in names:
    try:
        o=ws_build("defence",names=[n],g=g)
        s=ws_stats(o)[0]; print(n,s["tris"],s["bbox"],s["zmin"], round(time.time()-t0,2))
    except Exception as e:
        print("FAIL",n,traceback.format_exc()[-800:])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Straight 2292 [3.0, 2.7, 9.45] -1.5 0.06\nSM_VK_TownWall_Corner_Out 2200 [2.69, 2.68, 9.66] -1.5
#  0.1\nSM_VK_TownWall_Corner_In 1804 [1.68, 1.68, 7.75] -1.5 0.12\nSM_VK_TownWall_Stair 446 [3.07, 1.17, 6.43] -4.2 0.13\nSM_VK_TownWall_Step 2384 [3.0
# , 2.69, 10.57] -1.5 0.19\nSM_VK_TownWall_Ruin 4632 [3.15, 5.28, 6.99] -1.5 0.3\nSM_VK_TownWall_Tower_Round 10827 [7.16, 7.14, 13.97] -1.5 0.71\nSM_VK_
# Gatehouse_Block 16508 [10.64, 8.57, 10.5] -1.5 1.42\nSM_VK_Gatehouse_Portcullis 1392 [3.55, 0.21, 4.74] -0.04 1.45\nSM_VK_Gatehouse_GateLeaf 2012 [1.6
# 4, 0.42, 4.34] 0.02 1.5\nSM_VK_Parapet_Crenel 932 [3.0, 1.68, 2.37] -0.63 1.52\nSM_VK_Parapet_Corner 424 [1.4, 1.39, 2.81] -0.88 1.53\nSM_VK_Roof_Pyra
# mid_6 772 [4.21, 4.21, 4.14] -0.25 1.64\nSM_VK_Roof_Cone_R2 532 [4.4, 4.4, 5.37] -0.16 1.65\n"}

# ==============================================================================================================
# [0010] 2026-09-23 13:15:13  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("defence"); sc,coll,asm=ws_scene("defence")
for o in list(asm.objects):
    if o.location.y<-20: bpy.data.objects.remove(o)
O=(0,-60,0)
def P(n,x,y,z,r,st={}): return g["place_v"](asm,n,x,y,z,r,O,st)
P("SM_VK_TownWall_Corner_Out",-9,0,0,0)
for y in (1.5,4.5): P("SM_VK_TownWall_Straight",-9,y,0,-90)
for i,x in enumerate((-7.5,-4.5,-1.5)):
    P("SM_VK_TownWall_Straight",x,0,0,0); P("SM_VK_TownWall_Stair",x,0,i*2.067,0)
gx=4.5
P("SM_VK_Gatehouse_Block",gx,0,0,0)
P("SM_VK_Gatehouse_Portcullis",gx,-2.4,2.2,0)
P("SM_VK_Gatehouse_GateLeaf",gx-1.6,-1.2,0,75); P("SM_VK_Gatehouse_GateLeaf",gx+1.6,-1.2,0,105)
st={"roof":"Slate"}
H1=6.2
P("SM_VK_Wall_Timber_Window",gx,-3,H1,0,st)
for i,x in enumerate((gx-3,gx,gx+3)): P(("SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_Window","SM_VK_Wall_Timber")[i],x,3,H1,180,st)
P("SM_VK_Wall_Timber_Door",gx-4.5,1.5,H1,-90,st); P("SM_VK_Wall_Timber",gx-4.5,-1.5,H1,-90,st)
P("SM_VK_Wall_Timber_Door",gx+4.5,1.5,H1,90,st); P("SM_VK_Wall_Timber",gx+4.5,-1.5,H1,90,st)
P("SM_VK_Corner_Timber",gx-4.5,3,H1,-90,st); P("SM_VK_Corner_Timber",gx+4.5,3,H1,180,st)
P("SM_VK_Roof_Hip",gx-3,0,9.0,180,st); P("SM_VK_Roof_Mid",gx,0,9.0,0,st); P("SM_VK_Roof_Hip",gx+3,0,9.0,0,st)
for s in (-1,1): P("SM_VK_Roof_Cone_R2",gx+3*s,-3,9.0,0,st)
for x in (10.5,13.5,16.5,19.5): P("SM_VK_TownWall_Straight",x,0,0,0)
P("SM_VK_TownWall_Tower_Round",15,0,0,0)
P("SM_VK_TownWall_Ruin",22.5,0,0,0)
P("SM_VK_TownWall_Corner_In",24,0,0,180)
for y in (-1.5,-4.5): P("SM_VK_TownWall_Straight",24,y,0,-90)
p=ws_shot("defence","tw_asm_v1",(-8,-92,22),(8,-60,4),lens=30,res=(1600,900))
p=ws_shot("defence","tw_asm_v1b",(-20,-36,16),(0,-60,4),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0011] 2026-09-23 13:16:03  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
O=(0,-60)
def S(name,cam,tgt,lens=35):
    ws_shot("defence",name,(O[0]+cam[0],O[1]+cam[1],cam[2]),(O[0]+tgt[0],O[1]+tgt[1],tgt[2]),lens=lens,res=(1280,720))
S("tw_corner_out",(-15,-9,12),(-8,1,5),40)
S("tw_corner_in",(30,-10,13),(23,-1,5),40)
S("tw_walk_top",(-6,2.5,11),(0,0,6.5),35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0012] 2026-09-23 13:19:28  blender  ok
# ==============================================================================================================
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
g=ws_ns("defence")
objs=ws_build("defence",g=g)
for s in ws_stats(objs)[9:]: print(s["name"],s["tris"],s["bbox"])
O=(0,-60)
def S(name,cam,tgt,lens=35):
    ws_shot("defence",name,(O[0]+cam[0],O[1]+cam[1],cam[2]),(O[0]+tgt[0],O[1]+tgt[1],tgt[2]),lens=lens,res=(1280,720))
S("tw_front_v2",(0,-26,9),(3,0,4),32)
S("tw_ruin_v2",(22,-12,5),(22,0,3),35)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Straight 2308 [3.45, 2.82, 9.45]\nSM_VK_TownWall_Corner_Out 1304 [2.69, 2.68, 9.66]\nSM_VK_TownW
# all_Corner_In 1036 [1.68, 1.68, 7.75]\nSM_VK_TownWall_Stair 446 [3.07, 1.17, 6.43]\nSM_VK_TownWall_Step 2336 [3.45, 2.82, 10.57]\nSM_VK_TownWall_Ruin 
# 2540 [3.53, 5.28, 6.99]\nSM_VK_TownWall_Tower_Round 9547 [7.16, 7.14, 13.97]\nSM_VK_Gatehouse_Block 11856 [10.64, 8.57, 10.5]\nSM_VK_Gatehouse_Portcul
# lis 1392 [3.55, 0.21, 4.74]\nSM_VK_Gatehouse_GateLeaf 2012 [1.64, 0.42, 4.34]\nSM_VK_Parapet_Crenel 932 [3.0, 1.68, 2.37]\nSM_VK_Parapet_Corner 424 [1
# .4, 1.39, 2.81]\nSM_VK_Roof_Pyramid_6 772 [4.21, 4.21, 4.14]\nSM_VK_Roof_Cone_R2 532 [4.4, 4.4, 5.37]\n"}

# ==============================================================================================================
# [0013] 2026-09-23 13:23:12  blender  ok
# ==============================================================================================================
import bpy, time, traceback
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_defence.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_defence") or bpy.data.texts.new("ws_defence"); t.clear(); t.write(src)
g=ws_ns("defence")
names=[n for n,_,_ in g["WS_SPECS"]][23:]
built=[]
for n in names:
    try:
        o=ws_build("defence",names=[n],g=g)[0]; built.append(o)
        s=ws_stats([o])[0]; print(n,s["tris"],s["bbox"],s["zmin"])
    except Exception as e:
        print("FAIL",n,traceback.format_exc()[-900:])
ws_clear_assembly("defence")
ws_grid(built,cols=6,sx=5.5,sy=7,origin=(-14,12))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_TrainingDummy 984 [1.85, 1.16, 2.12] 0.0\nSM_VK_Prop_ArcheryButt 1176 [1.33, 1.73, 1.87] -0.01\nSM_V
# K_Prop_ArmorStand 1208 [1.64, 0.94, 2.36] 0.0\nSM_VK_Prop_MarketCross 598 [3.38, 3.38, 5.53] 0.0\nSM_VK_Prop_Maypole 1896 [6.09, 6.09, 9.73] -0.4\nSM_
# VK_Prop_Stage 2224 [6.3, 4.08, 4.05] -0.02\nSM_VK_Prop_Stocks 804 [2.27, 1.27, 1.07] -0.02\nSM_VK_Prop_Pillory 736 [1.52, 1.91, 2.85] 0.0\nSM_VK_LowWa
# ll_GateArch 3096 [3.38, 0.77, 3.68] -0.03\nSM_VK_Deco_Hedge 552 [3.13, 1.05, 1.32] -0.0\nSM_VK_Def_StoneUp 324 [3.0, 0.68, 2.8] 0.0\nSM_VK_Def_StoneUp
# _Slit 458 [3.0, 0.68, 2.8] 0.0\nSM_VK_Def_StoneUp_Window 1146 [3.0, 1.1, 2.8] 0.0\nSM_VK_Def_StoneUp_Door 1211 [3.0, 1.01, 2.8] 0.0\nSM_VK_Def_CornerU
# p 320 [1.17, 1.19, 2.82] 0.0\nSM_VK_Def_Bartizan 1362 [2.24, 2.24, 7.03] -1.7\n"}

# ==============================================================================================================
# [0014] 2026-09-23 13:24:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","props_v1",(0,-16,10),(0,6,1.6),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 13:25:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("defence")
rows=[
 (38,["SM_VK_Palisade_Straight","SM_VK_Palisade_Diag","SM_VK_Palisade_Post","SM_VK_Palisade_Walk","SM_VK_Palisade_Ladder","SM_VK_Palisade_Gate","SM_VK_Palisade_GateLeaf","SM_VK_Palisade_Tower","SM_VK_Prop_Beacon"],[0,5.5,10,13.5,17.5,21.5,26.5,31,37]),
 (22,["SM_VK_TownWall_Straight","SM_VK_TownWall_Corner_Out","SM_VK_TownWall_Corner_In","SM_VK_TownWall_Stair","SM_VK_TownWall_Step","SM_VK_TownWall_Ruin","SM_VK_TownWall_Tower_Round","SM_VK_Gatehouse_Block","SM_VK_Gatehouse_Portcullis","SM_VK_Gatehouse_GateLeaf"],[0,5,9,13,18,23,30,41,49,53]),
 (8,["SM_VK_Parapet_Crenel","SM_VK_Parapet_Corner","SM_VK_Roof_Pyramid_6","SM_VK_Roof_Cone_R2","SM_VK_Def_StoneUp","SM_VK_Def_StoneUp_Slit","SM_VK_Def_StoneUp_Window","SM_VK_Def_StoneUp_Door","SM_VK_Def_CornerUp","SM_VK_Def_Bartizan"],[0,4,8.5,14,19,23,27,31,35,39]),
 (-4,["SM_VK_Prop_TrainingDummy","SM_VK_Prop_ArcheryButt","SM_VK_Prop_ArmorStand","SM_VK_Prop_MarketCross","SM_VK_Prop_Maypole","SM_VK_Prop_Stage","SM_VK_Prop_Stocks","SM_VK_Prop_Pillory","SM_VK_LowWall_GateArch","SM_VK_Deco_Hedge"],[0,3,6,10.5,17.5,26,32,35.5,40,45]),
]
X0=-24
for y,names,xs in rows:
    for n,x in zip(names,xs):
        o=bpy.data.objects.get(n)
        if o: o.location=(X0+x,y,0)
ws_shot("defence","props_v1",(X0+22,-24,9),(X0+22,-3,1.6),lens=40,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0016] 2026-09-23 13:25:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","props_left",(-17,-14,5.5),(-17,-4,1.2),lens=30,res=(1600,900))
ws_shot("defence","props_right",(15,-15,5.5),(15,-4,1.3),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0017] 2026-09-23 13:26:53  blender  ok
# ==============================================================================================================
import bpy
for n in ["M_VK_Steel","M_VK_Iron","M_VK_Bronze","M_VK_Leaf","M_VK_Moss"]:
    m=bpy.data.materials.get(n)
    b=next((x for x in m.node_tree.nodes if x.type=="BSDF_PRINCIPLED"),None)
    ins={k:(b.inputs[k].default_value if not b.inputs[k].is_linked else "linked") for k in ("Metallic","Roughness")}
    bc=b.inputs["Base Color"]
    print(n, ins, "BC linked" if bc.is_linked else tuple(bc.default_value), [x.type for x in m.node_tree.nodes])
# ---- result ----
# {"result":"Code executed successfully: M_VK_Steel {'Metallic': 0.8999999761581421, 'Roughness': 'linked'} BC linked ['OUTPUT_MATERIAL', 'BSDF_PRINCIPL
# ED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', 'TEX_IMAGE', 'VERTEX_COLOR', 'RGBTOBW', 'MIX', 'MIX', 'MATH', 'NORMAL_MAP']\nM_VK_Iron {'Metallic': 'linked', 
# 'Roughness': 'linked'} BC linked ['OUTPUT_MATERIAL', 'BSDF_PRINCIPLED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', 'TEX_IMAGE', 'VERTEX_COLOR', 'MIX', 'MATH',
#  'NORMAL_MAP', 'TEX_IMAGE']\nM_VK_Bronze {'Metallic': 1.0, 'Roughness': 'linked'} BC linked ['OUTPUT_MATERIAL', 'BSDF_PRINCIPLED', 'UVMAP', 'TEX_IMAGE
# ', 'TEX_IMAGE', 'TEX_IMAGE', 'VERTEX_COLOR', 'RGBTOBW', 'MIX', 'MIX', 'MATH', 'NORMAL_MAP']\nM_VK_Leaf {'Metallic': 0.0, 'Roughness': 0.80000001192092
# 9} BC linked ['OUTPUT_MATERIAL', 'BSDF_PRINCIPLED', 'VERTEX_COLOR', 'MIX']\nM_VK_Moss {'Metallic': 0.0, 'Roughness': 'linked'} BC linked ['OUTPUT_MATE

# ==============================================================================================================
# [0018] 2026-09-23 13:28:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("defence","props_dummy",(-23,-9.5,3.0),(-22.5,-4,1.2),lens=35,res=(1280,720))
ws_shot("defence","props_cross",(-11,-13,6),(-13.5,-4,3.2),lens=35,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: "}
