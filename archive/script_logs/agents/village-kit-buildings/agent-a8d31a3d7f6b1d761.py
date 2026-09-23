# village-kit-buildings / agent-a8d31a3d7f6b1d761.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:54:20  blender  ok
# ==============================================================================================================
import bpy
print(bpy.app.version_string)
print([s.name for s in bpy.data.scenes])
print([t.name for t in bpy.data.texts])
print(len(bpy.data.objects))
print(bpy.data.scenes["VillageKit"].render.engine)
# ---- result ----
# {"result":"Code executed successfully: 4.4.3\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n['mc_helpers', 'tre
# e_build', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex', 'vk_tex2', 'vk_texgen', 'wk_helpers', 'ws_common']\n3600\nBLEN
# DER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0002] 2026-09-23 12:58:43  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns(None)
names=["ROCK","ROCK_MOSSY","STONE_BLOCK","ASHLAR","FIELDSTONE","STONE","CLAY","HIDE","PIGSKIN","COAL","SOIL","STEEL","MOSS","CLOTH_A","CLOTH_B","BREAD","HAY","PAPER","BURLAP","WATTLE","PLANKS","THATCH","WOOD","IRON","BRONZE","LEAF","YELLOW","PINK","ROOF","PLASTER","ENDGRAIN","BARK_OAK"]
def sw(k):
    for i,n in enumerate(names):
        x=(i%8)*1.6; y=-(i//8)*1.6
        k.box((x,y,0.5),(1.2,1.2,1.0),g[n],bevel=0.1,segs=2)
g["WS_SPECS"]=[("SM_VK_IndTmp_Swatch",sw,dict(wobble=False,grime=False))]
objs=ws_build("industry",g=g)
sc,coll,asm=ws_scene("industry")
print([o.name for o in coll.objects])
p=ws_shot("industry","swatch",(5.6,-12,9),(5.6,-2.4,0),lens=40,res=(1280,720),samples=16)
print(p)
# ---- result ----
# {"result":"Code executed successfully: ['SM_VK_IndTmp_Swatch']\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a
# 9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\industry\\swatch.png\n"}

# ==============================================================================================================
# [0003] 2026-09-23 12:59:07  blender  ok
# ==============================================================================================================
import bpy
for mn in ["M_VK_Hide","M_VK_Leaf","M_VK_FlowerYellow","M_VK_Clay","M_VK_Steel","M_VK_Coal","M_VK_Soil","M_VK_Cloth_Red","M_VK_Glow"]:
    m=bpy.data.materials[mn]
    out=[]
    for n in m.node_tree.nodes:
        s=n.bl_idname
        if n.type=="BSDF_PRINCIPLED": s+=f" base={tuple(round(x,2) for x in n.inputs['Base Color'].default_value)} rough={n.inputs['Roughness'].default_value:.2f} emis={n.inputs['Emission Strength'].default_value}"
        if n.type=="TEX_IMAGE": s+=f" img={n.image.name if n.image else None}"
        if n.type=="MIX": s+=f" {n.blend_type} A={tuple(round(x,2) for x in n.inputs[6].default_value)} B={tuple(round(x,2) for x in n.inputs[7].default_value)}"
        if n.type=="RGB": s+=f" {tuple(round(x,2) for x in n.outputs[0].default_value)}"
        out.append(s)
    print(mn, out)
sc=bpy.data.scenes["WS_industry"]
print(sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure)
# ---- result ----
# {"result":"Code executed successfully: M_VK_Hide ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled base=(0.8, 0.8, 0.8, 1.0) rough=0.80 emis=0.0'
# , 'ShaderNodeVertexColor', 'ShaderNodeMix MULTIPLY A=(0.5, 0.33, 0.2, 1.0) B=(0.5, 0.5, 0.5, 1.0)']\nM_VK_Leaf ['ShaderNodeOutputMaterial', 'ShaderNod
# eBsdfPrincipled base=(0.8, 0.8, 0.8, 1.0) rough=0.80 emis=0.0', 'ShaderNodeVertexColor', 'ShaderNodeMix MULTIPLY A=(0.18, 0.42, 0.1, 1.0) B=(0.5, 0.5,
#  0.5, 1.0)']\nM_VK_FlowerYellow ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled base=(0.8, 0.8, 0.8, 1.0) rough=0.70 emis=0.0', 'ShaderNodeVert
# exColor', 'ShaderNodeMix MULTIPLY A=(0.95, 0.78, 0.2, 1.0) B=(0.5, 0.5, 0.5, 1.0)']\nM_VK_Clay ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled 
# base=(0.8, 0.8, 0.8, 1.0) rough=0.50 emis=0.0', 'ShaderNodeUVMap', 'ShaderNodeTexImage img=T_VK_Plaster_BC', 'ShaderNodeTexImage img=T_VK_Plaster_N', 

# ==============================================================================================================
# [0004] 2026-09-23 13:02:43  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects.get("SM_VK_IndTmp_Swatch")
if o:
    me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
print([o.name for o in bpy.data.collections["WS_industry_Pieces"].objects])
# ---- result ----
# {"result":"Code executed successfully: []\n"}

# ==============================================================================================================
# [0005] 2026-09-23 13:07:45  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry") or bpy.data.texts.new("ws_industry"); t.clear(); t.write(src)
t0=time.time()
g=ws_ns("industry")
objs=ws_build("industry",g=g)
print("built",len(objs),round(time.time()-t0,1))
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"],s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: built 18 0.6\nSM_VK_Mine_Portal 3726 [9.33, 6.85, 6.09] -0.6\nSM_VK_Rail_Straight 324 [3.0, 1.6, 0.53] -0.3\nSM
# _VK_Rail_Curve 1056 [3.84, 3.84, 0.53] -0.3\nSM_VK_Rail_End 1056 [3.79, 1.76, 1.2] -0.3\nSM_VK_Prop_Minecart 1640 [1.79, 0.98, 1.27] -0.03\nSM_VK_Pile
# _Ore_1 556 [1.76, 1.47, 0.61] -0.04\nSM_VK_Pile_Ore_2 784 [2.57, 2.03, 0.81] -0.04\nSM_VK_Pile_Ore_3 1140 [3.16, 2.62, 1.2] -0.04\nSM_VK_Pile_Coal_1 5
# 36 [2.09, 1.32, 0.68] -0.1\nSM_VK_Pile_Coal_2 860 [2.75, 2.15, 0.85] -0.05\nSM_VK_Pile_Coal_3 1412 [3.39, 2.72, 0.89] -0.04\nSM_VK_Quarry_Face_Straigh
# t 948 [3.0, 3.11, 4.12] -0.6\nSM_VK_Quarry_Face_Corner 996 [3.03, 3.16, 4.12] -0.6\nSM_VK_Quarry_Face_InnerCorner 936 [3.07, 3.07, 4.14] -0.6\nSM_VK_Q
# uarry_Floor 1204 [2.98, 2.98, 1.36] -0.62\nSM_VK_Prop_Banker 868 [1.73, 1.36, 1.35] -0.01\nSM_VK_Prop_TreadwheelCrane 1892 [9.74, 4.03, 9.26] -0.05\nS

# ==============================================================================================================
# [0006] 2026-09-23 13:08:03  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("industry")
L={"SM_VK_Mine_Portal":(0,6),"SM_VK_Rail_Straight":(0,1.5),"SM_VK_Rail_Curve":(4.5,0),"SM_VK_Rail_End":(-4.5,1.5),
   "SM_VK_Prop_Minecart":(-1,-2),"SM_VK_Pile_Ore_1":(-8,-2),"SM_VK_Pile_Ore_2":(-8,2),"SM_VK_Pile_Ore_3":(-8,7),
   "SM_VK_Pile_Coal_1":(10,-2),"SM_VK_Pile_Coal_2":(10,2),"SM_VK_Pile_Coal_3":(10,7),
   "SM_VK_Quarry_Face_Straight":(20,6),"SM_VK_Quarry_Face_Corner":(26,6),"SM_VK_Quarry_Face_InnerCorner":(32,6),"SM_VK_Quarry_Floor":(20,0),
   "SM_VK_Prop_Banker":(25,-1),"SM_VK_Prop_TreadwheelCrane":(32,-4),"SM_VK_Prop_TreadwheelCrane_Wheel":(31,-4)}
for n,(x,y) in L.items():
    o=bpy.data.objects[n]; o.location=(x,y,0)
w=bpy.data.objects["SM_VK_Prop_TreadwheelCrane_Wheel"]; w.location=(32-1.0,-4,2.2)
p=ws_shot("industry","mine_v1",(0,-9,6),(0,3,1.5),lens=32,res=(1280,720),samples=16)
p=ws_shot("industry","quarry_v1",(20,-12,9),(27,1,2),lens=30,res=(1280,720),samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0007] 2026-09-23 13:12:56  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry") or bpy.data.texts.new("ws_industry"); t.clear(); t.write(src)
g=ws_ns("industry")
locs={o.name:tuple(o.location) for o in bpy.data.collections["WS_industry_Pieces"].objects}
objs=ws_build("industry",g=g)
for o in objs:
    if o.name in locs: o.location=locs[o.name]
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"])
sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
g["build_mine"](asm,(-20,30,0))
g["build_quarry_yard"](asm,(10,30,0))
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Mine_Portal 3878 [8.94, 7.91, 5.73]\nSM_VK_Rail_Straight 324 [3.0, 1.6, 0.53]\nSM_VK_Rail_Curve 1056 [3.8
# 4, 3.84, 0.53]\nSM_VK_Rail_End 1104 [3.59, 1.69, 1.2]\nSM_VK_Prop_Minecart 1640 [1.79, 0.98, 1.27]\nSM_VK_Pile_Ore_1 556 [1.76, 1.47, 0.61]\nSM_VK_Pil
# e_Ore_2 784 [2.57, 2.03, 0.81]\nSM_VK_Pile_Ore_3 1140 [3.16, 2.62, 1.2]\nSM_VK_Pile_Coal_1 536 [2.09, 1.32, 0.68]\nSM_VK_Pile_Coal_2 860 [2.75, 2.15, 
# 0.85]\nSM_VK_Pile_Coal_3 1412 [3.39, 2.72, 0.89]\nSM_VK_Quarry_Face_Straight 1204 [3.0, 3.17, 4.15]\nSM_VK_Quarry_Face_Corner 1280 [3.08, 3.21, 4.12]\
# nSM_VK_Quarry_Face_InnerCorner 1176 [3.07, 3.12, 4.06]\nSM_VK_Quarry_Floor 1252 [2.98, 2.98, 1.37]\nSM_VK_Prop_Banker 860 [1.73, 1.36, 1.46]\nSM_VK_Pr
# op_TreadwheelCrane 1892 [9.74, 4.03, 9.26]\nSM_VK_Prop_TreadwheelCrane_Wheel 2376 [3.6, 1.4, 3.6]\n37\n"}

# ==============================================================================================================
# [0008] 2026-09-23 13:13:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("industry","mine_asm_v1",(-12,14,11),(-19,29,1.5),lens=35,res=(1280,720),samples=16)
p=ws_shot("industry","quarry_asm_v1",(18,12,14),(10,30,2),lens=32,res=(1280,720),samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0009] 2026-09-23 13:17:40  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry") or bpy.data.texts.new("ws_industry"); t.clear(); t.write(src)
g=ws_ns("industry")
locs={o.name:tuple(o.location) for o in bpy.data.collections["WS_industry_Pieces"].objects}
t0=time.time()
objs=ws_build("industry",g=g)
print(round(time.time()-t0,1))
new=[o for o in objs if o.name not in locs]
for o in objs:
    if o.name in locs: o.location=locs[o.name]
for i,o in enumerate(new): o.location=(-10+i*6.5,-14,0)
for s in ws_stats(new): print(s["name"],s["tris"],s["bbox"])
p=ws_shot("industry","ironclay_v1",(8,-30,11),(8,-13,1.8),lens=30,res=(1400,700),samples=16)
# ---- result ----
# {"result":"Code executed successfully: 1.4\nSM_VK_Prop_CharcoalMound 3288 [4.34, 4.16, 2.13]\nSM_VK_Prop_Bloomery 2197 [3.07, 3.84, 3.9]\nSM_VK_Prop_B
# ellows 700 [1.96, 0.81, 1.21]\nSM_VK_Prop_BottleKiln 3640 [5.0, 5.66, 6.9]\nSM_VK_Prop_ClayPit 824 [3.46, 3.18, 1.7]\nSM_VK_Prop_PottersWheel 1020 [1.
# 69, 1.2, 1.1]\nSM_VK_Pile_Bricks_1 1060 [1.33, 1.2, 0.64]\nSM_VK_Pile_Bricks_2 1936 [1.83, 1.29, 0.73]\nSM_VK_Pile_Bricks_3 2812 [3.28, 1.29, 0.73]\n"
# }

# ==============================================================================================================
# [0010] 2026-09-23 13:18:26  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
L={"SM_VK_Prop_CharcoalMound":(0,-16),"SM_VK_Prop_Bloomery":(6,-16),"SM_VK_Prop_Bellows":(9.2,-16.2),"SM_VK_Prop_BottleKiln":(15,-15),
   "SM_VK_Prop_ClayPit":(21.5,-16.5),"SM_VK_Prop_PottersWheel":(25.5,-17),"SM_VK_Pile_Bricks_1":(28,-16),"SM_VK_Pile_Bricks_2":(30.5,-16),"SM_VK_Pile_Bricks_3":(34,-16)}
for n,(x,y) in L.items(): bpy.data.objects[n].location=(x,y,0)
p=ws_shot("industry","iron_v1",(4,-24.5,5.5),(4.5,-16,1.5),lens=35,res=(1280,720),samples=16)
p=ws_shot("industry","clay_v1",(26,-24,5.5),(27,-16,1.0),lens=35,res=(1280,720),samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0011] 2026-09-23 13:24:22  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry") or bpy.data.texts.new("ws_industry"); t.clear(); t.write(src)
g=ws_ns("industry")
locs={o.name:tuple(o.location) for o in bpy.data.collections["WS_industry_Pieces"].objects}
t0=time.time()
objs=ws_build("industry",g=g)
print(round(time.time()-t0,1))
new=[o for o in objs if o.name not in locs]
for o in objs:
    if o.name in locs: o.location=locs[o.name]
# row layout for the new groups
row1=["SM_VK_Prop_TanningPit","SM_VK_Prop_HideFrame","SM_VK_Prop_DyeVat","SM_VK_Prop_ClothRack","SM_VK_Prop_Loom","SM_VK_Prop_SpinningWheel",
      "SM_VK_Pile_Hides_1","SM_VK_Pile_Hides_2","SM_VK_Pile_Hides_3","SM_VK_Pile_Wool_1","SM_VK_Pile_Wool_2","SM_VK_Pile_Wool_3"]
xs=[0,3,6,9.5,13.5,16.5,19.5,22,25,28.5,31,34]
for n,x in zip(row1,xs): bpy.data.objects[n].location=(x,-24,0)
row2=["SM_VK_Kiln_Oast","SM_VK_Prop_MashTun","SM_VK_Prop_CiderPress","SM_VK_Prop_Skep","SM_VK_Prop_BeeBench","SM_VK_Prop_HerbBundles","SM_VK_Prop_Cauldron","SM_VK_Prop_DryingRack_Meat","SM_VK_Prop_DryingRack_Herbs","SM_VK_Prop_Dovecote"]
xs=[0,5.5,9,11.5,14,17.5,20.5,23.5,27,31.5]
for n,x in zip(row2,xs): bpy.data.objects[n].location=(x,-33,0)
for s in ws_stats([bpy.data.objects[n] for n in row1+row2+["SM_VK_Prop_CharcoalMound","SM_VK_Prop_Bloomery"]]): print(s["name"],s["tris"],s["bbox"])
# ---- result ----
# {"result":"Code executed successfully: 2.5\nSM_VK_Prop_TanningPit 562 [2.06, 1.87, 1.07]\nSM_VK_Prop_HideFrame 556 [1.7, 0.95, 2.04]\nSM_VK_Prop_DyeVa
# t 1216 [1.62, 1.5, 1.61]\nSM_VK_Prop_ClothRack 1012 [3.4, 1.67, 3.22]\nSM_VK_Prop_Loom 1522 [1.8, 2.11, 1.83]\nSM_VK_Prop_SpinningWheel 856 [1.08, 0.5
# 2, 1.41]\nSM_VK_Pile_Hides_1 484 [1.08, 0.9, 0.4]\nSM_VK_Pile_Hides_2 968 [2.19, 0.97, 0.51]\nSM_VK_Pile_Hides_3 1668 [3.21, 0.98, 0.6]\nSM_VK_Pile_Wo
# ol_1 356 [1.3, 1.23, 0.63]\nSM_VK_Pile_Wool_2 828 [2.67, 1.33, 1.2]\nSM_VK_Pile_Wool_3 1300 [3.08, 1.32, 1.2]\nSM_VK_Kiln_Oast 1452 [5.3, 5.57, 11.27]
# \nSM_VK_Prop_MashTun 1278 [3.09, 2.7, 2.03]\nSM_VK_Prop_CiderPress 1828 [2.24, 1.61, 2.27]\nSM_VK_Prop_Skep 296 [0.66, 0.66, 0.5]\nSM_VK_Prop_BeeBench
#  1580 [2.77, 1.35, 1.81]\nSM_VK_Prop_HerbBundles 544 [2.5, 0.8, 2.1]\nSM_VK_Prop_Cauldron 1320 [1.75, 1.72, 2.12]\nSM_VK_Prop_DryingRack_Meat 1424 [2.

# ==============================================================================================================
# [0012] 2026-09-23 13:24:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","cloth_a_v1",(8,-32.5,5.0),(8,-24,1.2),lens=35,res=(1280,720),samples=16)
ws_shot("industry","cloth_b_v1",(27,-31,4.5),(27,-24,0.6),lens=35,res=(1280,720),samples=16)
ws_shot("industry","food_a_v1",(7,-45,7.5),(7,-33,3.0),lens=35,res=(1280,720),samples=16)
ws_shot("industry","food_b_v1",(25,-43,6.0),(25,-33,2.0),lens=35,res=(1280,720),samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0013] 2026-09-23 13:28:26  blender  ok
# ==============================================================================================================
import bpy, time, math
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry") or bpy.data.texts.new("ws_industry"); t.clear(); t.write(src)
g=ws_ns("industry")
locs={o.name:tuple(o.location) for o in bpy.data.collections["WS_industry_Pieces"].objects}
t0=time.time()
objs=ws_build("industry",g=g)
for o in objs:
    if o.name in locs: o.location=locs[o.name]
print("build",round(time.time()-t0,1))
sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
t0=time.time()
R=math.radians
B=[("build_mine",(-35,25,0)),("build_quarry_yard",(-10,28,0)),("build_charcoal_burner",(15,24,0)),("build_pottery",(38,24,0)),
   ("build_tannery",(-35,48,0)),("build_dyers_yard",(-12,50,0)),("build_brewery",(12,48,0)),("build_apiary",(36,48,0))]
for fn,o in B:
    n0=len(asm.objects); g[fn](asm,o); print(fn,len(asm.objects)-n0)
print("asm",round(time.time()-t0,1),len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: build 2.9\nbuild_mine 14\nbuild_quarry_yard 21\nbuild_charcoal_burner 11\nbuild_pottery 9\nbuild_tannery 37\nbu
# ild_dyers_yard 11\nbuild_brewery 51\nbuild_apiary 11\nasm 0.1 165\n"}

# ==============================================================================================================
# [0014] 2026-09-23 13:28:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
P=bpy.data.collections["WS_industry_Pieces"]
for o in P.objects: o.hide_render=True
def cam(name,tx,ty,dist=16,h=11,lens=35,az=-35):
    import math
    a=math.radians(az-90)
    loc=(tx+math.cos(a)*dist*0.0+dist*math.sin(math.radians(az)), ty-dist*math.cos(math.radians(az)), h)
    ws_shot("industry",name,loc,(tx,ty,1.2),lens=lens,res=(1280,720),samples=16)
cam("a_charcoal_v1",15,24,dist=15,h=10)
cam("a_pottery_v1",38,24,dist=17,h=11)
cam("a_tannery_v1",-35,48,dist=18,h=12)
cam("a_dyers_v1",-12,50,dist=14,h=9)
for o in P.objects: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 13:30:29  blender  ok
# ==============================================================================================================
import bpy
for mn in ["M_VK_Bronze","M_VK_MushBrown","M_VK_MushRed","M_VK_Water","M_VK_Paper"]:
    m=bpy.data.materials[mn]
    out=[]
    for n in m.node_tree.nodes:
        s=n.bl_idname
        if n.type=="BSDF_PRINCIPLED": s+=f" base={tuple(round(x,2) for x in n.inputs['Base Color'].default_value)} rough={n.inputs['Roughness'].default_value:.2f} metal={n.inputs['Metallic'].default_value:.2f}"
        if n.type=="TEX_IMAGE": s+=f" img={n.image.name if n.image else None}"
        if n.type=="MIX": s+=f" {n.blend_type} A={tuple(round(x,2) for x in n.inputs[6].default_value)} B={tuple(round(x,2) for x in n.inputs[7].default_value)}"
        out.append(s)
    print(mn,out)
# ---- result ----
# {"result":"Code executed successfully: M_VK_Bronze ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled base=(0.8, 0.8, 0.8, 1.0) rough=0.50 metal=1
# .00', 'ShaderNodeUVMap', 'ShaderNodeTexImage img=T_VK_Iron_BC', 'ShaderNodeTexImage img=T_VK_Iron_N', 'ShaderNodeTexImage img=T_VK_Iron_R', 'ShaderNod
# eVertexColor', 'ShaderNodeRGBToBW', 'ShaderNodeMix MULTIPLY A=(3.4, 2.2, 0.95, 1.0) B=(0.5, 0.5, 0.5, 1.0)', 'ShaderNodeMix MULTIPLY A=(0.5, 0.5, 0.5,
#  1.0) B=(0.5, 0.5, 0.5, 1.0)', 'ShaderNodeMath', 'ShaderNodeNormalMap']\nM_VK_MushBrown ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled base=(0
# .8, 0.8, 0.8, 1.0) rough=0.60 metal=0.00', 'ShaderNodeVertexColor', 'ShaderNodeMix MULTIPLY A=(0.52, 0.31, 0.15, 1.0) B=(0.5, 0.5, 0.5, 1.0)']\nM_VK_M
# ushRed ['ShaderNodeOutputMaterial', 'ShaderNodeBsdfPrincipled base=(0.8, 0.8, 0.8, 1.0) rough=0.45 metal=0.00', 'ShaderNodeVertexColor', 'ShaderNodeMi
