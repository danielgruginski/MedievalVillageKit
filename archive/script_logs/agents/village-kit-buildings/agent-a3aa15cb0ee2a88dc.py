# village-kit-buildings / agent-a3aa15cb0ee2a88dc.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:53:55  blender  ok
# ==============================================================================================================
import bpy
print([t.name for t in bpy.data.texts])
print([s.name for s in bpy.data.scenes])
print(bpy.app.version_string)
print([o.name for o in bpy.data.objects if o.name.startswith("SM_VK_") and ("Up" in o.name or "Shop" in o.name or "Turret" in o.name or "Stepped" in o.name or "Pent" in o.name)])
sc=bpy.data.scenes["VillageKit"]; print(sc.render.engine)
# ---- result ----
# {"result":"Code executed successfully: ['mc_helpers', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex', 'vk_
# tex2', 'vk_texgen', 'wk_helpers', 'ws_common']\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n4.4.3\n[]\nBLENDE
# R_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0002] 2026-09-23 12:55:42  blender  ok
# ==============================================================================================================
import bpy
print(sorted(i.name for i in bpy.data.images if i.name.startswith("T_VK")))
print(sorted(m.name for m in bpy.data.materials if m.name.startswith("M_VK_Roof")))
print([o.name for o in bpy.data.collections["VK_Pieces"].objects][:400] if bpy.data.collections.get("VK_Pieces") else None)
# ---- result ----
# {"result":"Code executed successfully: ['T_VK_Ashlar_AO', 'T_VK_Ashlar_BC', 'T_VK_Ashlar_H', 'T_VK_Ashlar_N', 'T_VK_Ashlar_R', 'T_VK_BarkBirch_AO', 'T
# _VK_BarkBirch_BC', 'T_VK_BarkBirch_H', 'T_VK_BarkBirch_N', 'T_VK_BarkBirch_R', 'T_VK_BarkOak_AO', 'T_VK_BarkOak_BC', 'T_VK_BarkOak_H', 'T_VK_BarkOak_N
# ', 'T_VK_BarkOak_R', 'T_VK_BarkPine_AO', 'T_VK_BarkPine_BC', 'T_VK_BarkPine_H', 'T_VK_BarkPine_N', 'T_VK_BarkPine_R', 'T_VK_Burlap_BC', 'T_VK_Burlap_N
# ', 'T_VK_Burlap_R', 'T_VK_Clock_BC', 'T_VK_Clock_N', 'T_VK_Clock_R', 'T_VK_Cloth_BC', 'T_VK_Cloth_N', 'T_VK_Cloth_R', 'T_VK_Crops_BCA', 'T_VK_EndGrain
# _AO', 'T_VK_EndGrain_BC', 'T_VK_EndGrain_H', 'T_VK_EndGrain_N', 'T_VK_EndGrain_R', 'T_VK_FieldStone_AO', 'T_VK_FieldStone_BC', 'T_VK_FieldStone_H', 'T
# _VK_FieldStone_N', 'T_VK_FieldStone_R', 'T_VK_Foliage_BCA', 'T_VK_Iron_BC', 'T_VK_Iron_M', 'T_VK_Iron_N', 'T_VK_Iron_R', 'T_VK_Leaves_BCA', 'T_VK_Leav

# ==============================================================================================================
# [0003] 2026-09-23 13:00:12  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
t0=time.time()
g=ws_ns("town"); print("ns",time.time()-t0)
objs=ws_build("town",g=g)
print("build",time.time()-t0)
ws_grid(objs,cols=5,sx=4.5,sy=5)
for s in ws_stats(objs): print(s)
# ---- result ----
# {"result":"Code executed successfully: ns 0.08117532730102539\nbuild 0.4954371452331543\n{'name': 'SM_VK_Wall_StoneUp', 'tris': 812, 'bbox': [3.0, 0.7
# 2, 2.86], 'zmin': -0.06, 'mats': [0, 45]}\n{'name': 'SM_VK_Wall_StoneUp_Window', 'tris': 2518, 'bbox': [3.0, 1.1, 2.86], 'zmin': -0.06, 'mats': [0, 2,
#  4, 5, 10, 45]}\n{'name': 'SM_VK_Wall_StoneUp_Twin', 'tris': 3808, 'bbox': [3.0, 0.84, 2.86], 'zmin': -0.06, 'mats': [0, 2, 4, 45]}\n{'name': 'SM_VK_W
# all_StoneUp_Slit', 'tris': 1516, 'bbox': [3.0, 0.73, 2.86], 'zmin': -0.06, 'mats': [0, 27, 45]}\n{'name': 'SM_VK_Wall_StoneUp_Loading', 'tris': 2822, 
# 'bbox': [3.0, 1.22, 2.86], 'zmin': -0.06, 'mats': [0, 2, 5, 23, 25, 27, 45]}\n{'name': 'SM_VK_Wall_StoneUp_Door', 'tris': 3484, 'bbox': [3.0, 0.81, 2.
# 86], 'zmin': -0.06, 'mats': [0, 5, 23, 45]}\n{'name': 'SM_VK_Corner_StoneUp', 'tris': 768, 'bbox': [1.11, 1.16, 2.86], 'zmin': -0.06, 'mats': [0, 45]}

# ==============================================================================================================
# [0004] 2026-09-23 13:00:39  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("town"); sc,coll,asm=ws_scene("town"); ws_clear_assembly("town")
P=lambda n,x,y,z,r,st={}: g["place_v"](asm,n,x,y,z,r,(40,0,0),st)
# stone block: 3 cells front, 2 deep, 3 storeys
L=9
front0=["SM_VK_Wall_Stone_Window","SM_VK_Wall_Stone_Door","SM_VK_Wall_Stone"]
front1=["SM_VK_Wall_StoneUp_Window","SM_VK_Wall_StoneUp_Twin","SM_VK_Wall_StoneUp_Slit"]
front2=["SM_VK_Wall_StoneUp_Loading","SM_VK_Wall_StoneUp","SM_VK_Wall_StoneUp_Door"]
for i in range(3):
    x=-L/2+1.5+3*i
    P(front0[i],x,-3,0,0); P(front1[i],x,-3,3.0,0); P(front2[i],x,-3,5.8,0)
    P("SM_VK_Wall_Stone",x,3,0,180); P("SM_VK_Wall_StoneUp",x,3,3.0,180); P("SM_VK_Wall_StoneUp",x,3,5.8,180)
for j,yy in enumerate((-1.5,1.5)):
    P("SM_VK_Wall_Stone",-L/2,yy,0,-90); P("SM_VK_Wall_StoneUp_Window" if j==0 else "SM_VK_Wall_StoneUp",-L/2,yy,3.0,-90); P("SM_VK_Wall_StoneUp_Twin",-L/2,yy,5.8,-90)
    P("SM_VK_Wall_Stone",L/2,-yy,0,90); P("SM_VK_Wall_StoneUp",L/2,-yy,3.0,90); P("SM_VK_Wall_StoneUp",L/2,-yy,5.8,90)
for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
    P("SM_VK_Corner_Stone",cx,cy,0,r); P("SM_VK_Corner_StoneUp",cx,cy,3.0,r); P("SM_VK_Corner_StoneUp",cx,cy,5.8,r)
for i in range(3):
    x=-L/2+1.5+3*i
    P("SM_VK_Roof_Gable_Stone" if i in (0,2) else "SM_VK_Roof_Mid",x,0,8.6,180 if i==0 else 0,{"roof":"Slate"})
# plaster block next to it (x +10.5)
ox=11
st={"plaster":"Ochre","shutter":"Green"}
f0=["SM_VK_Wall_Plaster_Window","SM_VK_Wall_Plaster_Door"]; f1=["SM_VK_Wall_PlasterUp_Window","SM_VK_Wall_PlasterUp_Oxeye"]; f2=["SM_VK_Wall_PlasterUp","SM_VK_Wall_PlasterUp_Window"]
for i in range(2):
    x=ox-3+1.5+3*i
    P(f0[i],x,-3,0,0,st); P(f1[i],x,-3,3.0,0,st); P(f2[i],x,-3,5.8,0,st)
    P("SM_VK_Wall_Plaster",x,3,0,180,st); P("SM_VK_Wall_PlasterUp",x,3,3.0,180,st); P("SM_VK_Wall_PlasterUp",x,3,5.8,180,st)
for yy in (-1.5,1.5):
    P("SM_VK_Wall_Plaster",ox-3,yy,0,-90,st); P("SM_VK_Wall_PlasterUp_Window",ox-3,yy,3.0,-90,st); P("SM_VK_Wall_PlasterUp",ox-3,yy,5.8,-90,st)
    P("SM_VK_Wall_Plaster",ox+3,-yy,0,90,st); P("SM_VK_Wall_PlasterUp",ox+3,-yy,3.0,90,st); P("SM_VK_Wall_PlasterUp_Oxeye",ox+3,-yy,5.8,90,st)
for (cx,cy,r) in ((ox-3,-3,0),(ox+3,-3,90),(ox+3,3,180),(ox-3,3,-90)):
    P("SM_VK_Corner_Plaster",cx,cy,0,r,st); P("SM_VK_Corner_PlasterUp",cx,cy,3.0,r,st); P("SM_VK_Corner_PlasterUp",cx,cy,5.8,r,st)
for i in range(2):
    x=ox-3+1.5+3*i
    P("SM_VK_Roof_Gable",x,0,8.6,180 if i==0 else 0,{"roof":"Red"})
p=ws_shot("town","seam_v1",(40-12,-19,9),(40+2,0,4.5),lens=35)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\town\\seam_v1.png\n"}

# ==============================================================================================================
# [0005] 2026-09-23 13:00:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("town","seam_v1_close",(40-2,-10.5,5.2),(40-1.5,-3,4.3),lens=35)
p2=ws_shot("town","seam_v1_plaster",(51-3,-10,5.5),(51+0.5,-3,4.2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0006] 2026-09-23 13:02:25  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town"); objs=ws_build("town",g=g)
ws_grid(objs,cols=5,sx=4.5,sy=5)
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
p=ws_shot("town","cat_v2",(9,-19,7),(9,-4,1.6),lens=32)
p=ws_shot("town","seam_v2_close",(40-2,-10.5,5.2),(40-1.5,-3,4.3),lens=35)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_StoneUp 732 [3.0, 0.77, 2.91]\nSM_VK_Wall_StoneUp_Window 1806 [3.0, 1.1, 2.91]\nSM_VK_Wall_StoneUp_T
# win 2396 [3.0, 0.84, 2.91]\nSM_VK_Wall_StoneUp_Slit 1436 [3.0, 0.77, 2.91]\nSM_VK_Wall_StoneUp_Loading 2742 [3.0, 1.22, 2.91]\nSM_VK_Wall_StoneUp_Door
#  3404 [3.0, 0.81, 2.91]\nSM_VK_Corner_StoneUp 768 [1.11, 1.16, 2.86]\nSM_VK_InnerCorner_StoneUp 648 [0.63, 0.63, 2.58]\nSM_VK_Wall_PlasterUp 1260 [3.0
# , 0.72, 2.92]\nSM_VK_Wall_PlasterUp_Window 1486 [3.0, 1.05, 2.92]\nSM_VK_Wall_PlasterUp_Oxeye 1328 [3.0, 0.73, 2.92]\nSM_VK_Corner_PlasterUp 284 [0.74
# , 0.74, 3.03]\nSM_VK_InnerCorner_PlasterUp 88 [0.3, 0.3, 2.82]\n"}

# ==============================================================================================================
# [0007] 2026-09-23 13:08:58  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town"); t0=time.time(); objs=ws_build("town",g=g); print("build",time.time()-t0)
ws_grid(objs,cols=6,sx=4.5,sy=5)
for s in ws_stats(objs)[13:]: print(s["name"],s["tris"],s["bbox"],s["zmin"])
sc,coll,asm=ws_scene("town"); ws_clear_assembly("town")
P=lambda n,x,y,z,r,st={}: g["place_v"](asm,n,x,y,z,r,(40,0,0),st)
st={"plaster":"Rose","shutter":"Red"}
# row of shops: stone shop, plaster shop, stone shop, with upper floors
row=[("SM_VK_Wall_Stone_Shop","SM_VK_Wall_StoneUp_Window","SM_VK_Prop_ShopGoods_Bread"),
     ("SM_VK_Wall_Stone","SM_VK_Wall_StoneUp_Twin",None),
     ("SM_VK_Wall_Stone_Shop","SM_VK_Wall_StoneUp_Window","SM_VK_Prop_ShopGoods_Pots"),
     ("SM_VK_Wall_Plaster_Shop","SM_VK_Wall_PlasterUp_Window","SM_VK_Prop_ShopGoods_Cloth"),
     ("SM_VK_Wall_Plaster_Shop","SM_VK_Wall_PlasterUp_Oxeye","SM_VK_Prop_ShopGoods_Produce")]
for i,(a,b,gd) in enumerate(row):
    x=-6+3*i
    P(a,x,-3,0,0,st); P(b,x,-3,3.0,0,st)
    if gd: P(gd,x,-3-0.55,0.95,0,st)
    if i in (2,4): P("SM_VK_Roof_Pent",x,-3,3.4,0,{"roof":"Red"})
p=ws_shot("town","shops_v1",(40-3,-12.5,4.0),(40-1,-3,1.8),lens=32)
# ---- result ----
# {"result":"Code executed successfully: build 0.9116804599761963\nSM_VK_Wall_Stone_Shop 2556 [3.04, 1.25, 3.63] -0.6\nSM_VK_Wall_Plaster_Shop 2280 [3.1
# 3, 1.27, 3.6] -0.6\nSM_VK_Prop_ShopGoods_Bread 1984 [1.9, 0.5, 0.32] 0.0\nSM_VK_Prop_ShopGoods_Produce 1312 [1.97, 0.59, 0.36] 0.0\nSM_VK_Prop_ShopGoo
# ds_Cloth 472 [1.74, 0.59, 0.85] -0.45\nSM_VK_Prop_ShopGoods_Pots 1448 [1.88, 0.49, 0.42] 0.0\nSM_VK_Prop_ShopGoods_Tools 1004 [1.85, 0.49, 0.37] 0.0\n
# SM_VK_Prop_ShopGoods_Meat 600 [1.8, 0.44, 0.26] 0.0\nSM_VK_Prop_ShopGoods_Candles 768 [1.9, 0.41, 0.46] 0.0\nSM_VK_Prop_ShopGoods_Fish 522 [1.85, 0.58
# , 0.29] 0.0\nSM_VK_Roof_Pent 1612 [3.24, 1.72, 1.05] -1.0\n"}

# ==============================================================================================================
# [0008] 2026-09-23 13:09:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("town","shops_v1_high",(40+1,-15,12),(40+1,-3,1.5),lens=35)
p=ws_shot("town","goods_v1",(11.25,-14.5,3.2),(11.25,-10,0.2),lens=40)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0009] 2026-09-23 13:14:46  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town"); t0=time.time(); objs=ws_build("town",g=g); print("build",time.time()-t0)
new=objs[24:]
for o in objs[:24]: o.location=(-100,0,0)
for i,o in enumerate(new): o.location=((i%5)*6.0,-(i//5)*7.0,0)
for s in ws_stats(new): print(s["name"],s["tris"],s["bbox"],s["zmin"])
p=ws_shot("town","cat_new_v1",(12,-26,14),(12,-7,1.5),lens=35)
# ---- result ----
# {"result":"Code executed successfully: build 1.3546862602233887\nSM_VK_Wall_Stone_Passage 2260 [3.23, 1.0, 3.68] -0.6\nSM_VK_Passage_Vault 1828 [2.92,
#  5.5, 3.26] -0.6\nSM_VK_Gallery_Timber 1256 [3.22, 1.55, 4.75] -0.6\nSM_VK_Gallery_End 1808 [3.47, 1.55, 4.97] -0.6\nSM_VK_Gallery_Side 144 [0.12, 1.3
# , 0.97] 3.08\nSM_VK_Turret_Corbel 476 [2.4, 2.4, 1.81] -1.67\nSM_VK_Turret_Seg 1124 [2.58, 2.4, 2.8] 0.0\nSM_VK_Turret_Seg_Stone 552 [2.48, 2.4, 2.84]
#  -0.04\nSM_VK_Turret_Cap 440 [3.28, 3.28, 4.01] -0.24\nSM_VK_Stoop_Stone 448 [2.46, 1.13, 1.26] -0.6\nSM_VK_Stair_Stone_Ext 1293 [5.45, 1.36, 4.74] -0
# .6\nSM_VK_Prop_CellarHatch 852 [1.54, 1.56, 1.29] -0.6\n"}

# ==============================================================================================================
# [0010] 2026-09-23 13:20:39  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town"); objs=ws_build("town",g=g)
for i,o in enumerate(objs): o.location=(-200+(i%8)*6,-(i//8)*7,0)
sc,coll,asm=ws_scene("town"); ws_clear_assembly("town")
t0=time.time()
print(g["build_merchant_house"](asm,(40,0,0),seed=0))
print("t",time.time()-t0, len(asm.objects))
p=ws_shot("town","merchant_v1",(40-16,-20,11),(40,0,4.5),lens=35)
p=ws_shot("town","merchant_v1_back",(40+14,19,9),(40,2,3.5),lens=35)
# ---- result ----
# {"result":"Code executed successfully: {'footprint': (3, 2), 'lot': (3, 3), 'wall_top': 8.6}\nt 0.040395498275756836 78\n"}

# ==============================================================================================================
# [0011] 2026-09-23 13:21:33  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town")
sc,coll,asm=ws_scene("town"); ws_clear_assembly("town")
t0=time.time()
print(g["build_merchant_house"](asm,(-30,22,0),seed=0))
print(g["build_townhouse_gablefront"](asm,(-12,22,0),seed=0))
print(g["build_corner_house"](asm,(8,22,0),seed=0))
res=g["build_terrace"](asm,(0,-10,0),units=4,seed=0)
print([(u["w"],u["s"],u["g"],u["u"],u["st"]["plaster"],u["st"]["roof"]) for u in res["units"]])
print("t",time.time()-t0, len(asm.objects))
p=ws_shot("town","all_v1_aerial",(0,-58,42),(0,5,2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: {'footprint': (3, 2), 'lot': (3, 3), 'wall_top': 8.6}\n{'footprint': (2, 3), 'lot': (4, 3), 'wall_top': 8.6}\n{
# 'footprint': (3, 3), 'lot': (4, 4), 'wall_top': 8.6}\n[(2, 4, 'Stone', 'StoneUp', 'Sage', 'Shingle'), (3, 2, 'Stone', 'PlasterUp', 'Cream', 'Shingle')
# , (3, 2, 'Plaster', 'Timber', 'Rose', 'Shingle'), (2, 3, 'Stone', 'Timber', 'White', 'Slate')]\nt 0.2282395362854004 365\n"}

# ==============================================================================================================
# [0012] 2026-09-23 13:22:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("town","terrace_v1",(-6,-30,6.5),(0,-10,4.5),lens=30)
ws_shot("town","townhouse_v1",(-19,6,6),(-12,20,5.5),lens=32)
ws_shot("town","corner_v1",(-4,6,7),(7,21,6),lens=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0013] 2026-09-23 13:23:18  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("town","turretcap_v1",(-6,10,14),(5,19,11.5),lens=40)
ws_shot("town","stair_v1",(-38,33,5),(-29,25.5,2.2),lens=32)
ws_shot("town","passage_v1",(9,-17,2.2),(12.5,-10,1.8),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0014] 2026-09-23 13:25:29  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town"); objs=ws_build("town",g=g)
for i,o in enumerate(objs): o.location=(-200+(i%8)*6,-(i//8)*7,0)
sc,coll,asm=ws_scene("town"); ws_clear_assembly("town")
g["build_merchant_house"](asm,(-30,22,0),seed=0)
g["build_townhouse_gablefront"](asm,(-12,22,0),seed=0)
g["build_corner_house"](asm,(8,22,0),seed=0)
g["build_terrace"](asm,(0,-10,0),units=4,seed=0)
ws_shot("town","stair_v2",(-19,33,6),(-29,25.5,2.2),lens=30)
ws_shot("town","passage_v2",(9,-17,2.2),(12.5,-10,1.8),lens=30)
ws_shot("town","corner_yard_v1",(22,34,9),(13,24,3.5),lens=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 13:27:13  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials.get("M_VK_Stone"); print("cull",m.use_backface_culling, getattr(m,"use_backface_culling_shadow",None))
o=bpy.data.objects["SM_VK_Stair_Stone_Ext"]; me=o.data
import bmesh
from mathutils import Vector
ng=[p for p in me.polygons if len(p.vertices)>4]
for p in ng: print(len(p.vertices), p.material_index, tuple(round(c,2) for c in p.normal), round(p.area,2))
# ---- result ----
# {"result":"Code executed successfully: cull False False\n6 0 (0.0, -1.0, 0.0) 5.85\n6 0 (0.0, 1.0, 0.0) 5.85\n11 27 (0.0, -1.0, 0.0) 1.67\n"}

# ==============================================================================================================
# [0016] 2026-09-23 13:28:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
o=bpy.data.objects["SM_VK_Stair_Stone_Ext"]; old=tuple(o.location); o.location=(0,45,0)
ws_shot("town","dbg_stair",(4,37,4),(1,45,1.8),lens=30)
o.location=old
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0017] 2026-09-23 13:29:16  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_town.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_town") or bpy.data.texts.new("ws_town"); t.clear(); t.write(src)
g=ws_ns("town"); objs=ws_build("town",g=g)
for i,o in enumerate(objs): o.location=(-200+(i%8)*6,-(i//8)*7,0)
sc,coll,asm=ws_scene("town"); g["twn_clear_assembly"](asm)
g["build_merchant_house"](asm,(-30,22,0),seed=0)
g["build_townhouse_gablefront"](asm,(-12,22,0),seed=0)
g["build_corner_house"](asm,(8,22,0),seed=0)
g["build_terrace"](asm,(0,-10,0),units=4,seed=0)
ws_shot("town","passage_v3",(9,-17,2.2),(12.5,-10,1.8),lens=30)
ws_shot("town","merchant_v2_left",(-44,12,7),(-32,22,5),lens=32)
ws_shot("town","stair_v3",(-19,33,6),(-29,25.5,2.2),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0018] 2026-09-23 13:30:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
o=bpy.data.objects["SM_VK_Wall_Stone_Passage"]; old=tuple(o.location); o.location=(0,45,0)
ws_shot("town","dbg_passage",(1.2,40.5,1.0),(0.3,45,2.0),lens=30)
o.location=old
# which objects are near the terrace passage?
asm=bpy.data.collections["WS_town_Assembly"]
for ob in asm.objects:
    if "Passage" in ob.name: print(ob.name, ob.data.name, tuple(round(v,2) for v in ob.location))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Passage_inst VAR_2192951210336977933 (10.5, -13.0, 0.0)\nSM_VK_Wall_Stone_Passage_inst.001 VAR
# _2192951210336977933 (10.5, -7.0, 0.0)\nSM_VK_Passage_Vault_inst SM_VK_Passage_Vault (10.5, -10.0, 0.0)\n"}
