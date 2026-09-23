# village-kit-buildings / agent-aecc8c98edd38702a.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:54:05  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"].as_string()
print(len(t.splitlines()), len(t))
local=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_helpers.py",encoding="utf8").read()
print(len(local.splitlines()), t==local)
print([s.name for s in bpy.data.scenes])
print([x.name for x in bpy.data.texts])
# ---- result ----
# {"result":"Code executed successfully: 3041 174915\n3041 True\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n['
# mc_helpers', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex', 'vk_tex2', 'vk_texgen', 'wk_helpers', 'ws_com
# mon']\n"}

# ==============================================================================================================
# [0002] 2026-09-23 13:03:02  blender  ok
# ==============================================================================================================
import bpy
for n in ["T_VK_Planks_BC","T_VK_Planks","T_VK_Wood_BC","T_VK_Ashlar_BC","T_VK_Burlap_BC","T_VK_StoneBlock_BC","T_VK_Wattle_BC","T_VK_Thatch_BC"]:
    im=bpy.data.images.get(n)
    print(n, im and (im.filepath_raw, im.size[:]))
m=bpy.data.materials["M_VK_Planks"]
print([ (n.type, getattr(n,'image',None) and n.image.name) for n in m.node_tree.nodes])
for mn in ["M_VK_BarkBirch","M_VK_BarkOak","M_VK_EndGrain","M_VK_Cloth_Cream","M_VK_Hide"]:
    m=bpy.data.materials[mn]; print(mn,[ (n.type, getattr(n,'image',None) and n.image.name) for n in m.node_tree.nodes if n.type in('TEX_IMAGE','BSDF_PRINCIPLED')], m.use_backface_culling)
# ---- result ----
# {"result":"Code executed successfully: T_VK_Planks_BC ('C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d
# 5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\VillageKit\\\\Textures\\\\T_VK_Planks_BC.png', (1024, 102
# 4))\nT_VK_Planks None\nT_VK_Wood_BC ('C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f
# 56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\VillageKit\\\\Textures\\\\T_VK_Wood_BC.png', (1024, 1024))\nT_VK_Ashlar_BC 
# ('C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d
# 4348ea\\\\scratch-2026-09-23-d49817\\\\VillageKit\\\\Textures\\\\T_VK_Ashlar_BC.png', (1024, 1024))\nT_VK_Burlap_BC ('C:\\\\Users\\\\danie\\\\AppData\

# ==============================================================================================================
# [0003] 2026-09-23 13:04:00  blender  ok
# ==============================================================================================================
import bpy
for mn in ["M_VK_Soil","M_VK_Paper","M_VK_Clay","M_VK_Void","M_VK_Coal","M_VK_Glow","M_VK_Iron","M_VK_Steel","M_VK_Hay","M_VK_Rock","M_VK_Ashlar","M_VK_StoneBlock","M_VK_Burlap","M_VK_Cloth_Red","M_VK_Cloth_Cream"]:
    m=bpy.data.materials.get(mn)
    if not m: print(mn,"MISSING"); continue
    ims=[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    print(mn, ims, b and tuple(round(x,2) for x in b.inputs['Base Color'].default_value), b and round(b.inputs['Emission Strength'].default_value,2))
sc=bpy.data.scenes["VillageKit"]; print(sc.render.engine, sc.view_settings.view_transform, sc.view_settings.look)
# ---- result ----
# {"result":"Code executed successfully: M_VK_Soil ['T_VK_Soil_BC', 'T_VK_Soil_N', 'T_VK_Soil_R'] (0.8, 0.8, 0.8, 1.0) 0.0\nM_VK_Paper ['T_VK_Paper_BC',
#  'T_VK_Paper_N', 'T_VK_Paper_R'] (0.8, 0.8, 0.8, 1.0) 0.0\nM_VK_Clay ['T_VK_Plaster_BC', 'T_VK_Plaster_N', 'T_VK_Plaster_R'] (0.8, 0.8, 0.8, 1.0) 0.0\
# nM_VK_Void [] (0.01, 0.01, 0.01, 1.0) 0.0\nM_VK_Coal [] (0.8, 0.8, 0.8, 1.0) 0.0\nM_VK_Glow [] (0.8, 0.8, 0.8, 1.0) 3.0\nM_VK_Iron ['T_VK_Iron_BC', 'T
# _VK_Iron_N', 'T_VK_Iron_R', 'T_VK_Iron_M'] (0.8, 0.8, 0.8, 1.0) 0.0\nM_VK_Steel ['T_VK_Iron_BC', 'T_VK_Iron_N', 'T_VK_Iron_R'] (0.8, 0.8, 0.8, 1.0) 0.
# 0\nM_VK_Hay ['T_VK_Straw_BC', 'T_VK_Straw_N', 'T_VK_Straw_R'] (0.8, 0.8, 0.8, 1.0) 0.0\nM_VK_Rock ['T_VK_Rock_BC', 'T_VK_Rock_N', 'T_VK_Rock_R'] (0.8,
#  0.8, 0.8, 1.0) 0.0\nM_VK_Ashlar ['T_VK_Ashlar_BC', 'T_VK_Ashlar_N', 'T_VK_Ashlar_R'] (0.8, 0.8, 0.8, 1.0) 0.0\nM_VK_StoneBlock ['T_VK_StoneBlock_BC',

# ==============================================================================================================
# [0004] 2026-09-23 13:10:51  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_construction") or bpy.data.texts.new("ws_construction"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
try:
    g=ws_ns("construction")
    objs=ws_build("construction", g=g)
    ws_grid(objs, cols=5, sx=8, sy=9)
    for s in ws_stats(objs): print(s)
except Exception:
    traceback.print_exc()
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_BuildSite_Cell', 'tris': 736, 'bbox': [2.95, 2.92, 0.99], 'zmin': -0.6, 'mats': [2, 11, 26, 28]
# }\n{'name': 'SM_VK_Foundation_Wall', 'tris': 2092, 'bbox': [3.04, 1.87, 1.24], 'zmin': -0.6, 'mats': [0, 2, 17, 26, 45]}\n{'name': 'SM_VK_Foundation_C
# orner', 'tris': 484, 'bbox': [1.54, 1.54, 1.24], 'zmin': -0.6, 'mats': [0, 2, 17, 26, 45]}\n{'name': 'SM_VK_Wall_Stone_Half', 'tris': 1264, 'bbox': [3
# .04, 1.38, 2.37], 'zmin': -0.6, 'mats': [0, 1, 2, 21, 24, 45]}\n{'name': 'SM_VK_Wall_Stone_Half_Door', 'tris': 2164, 'bbox': [3.12, 1.65, 3.39], 'zmin
# ': -0.6, 'mats': [0, 1, 2, 21, 24, 45]}\n{'name': 'SM_VK_Corner_Stone_Half', 'tris': 596, 'bbox': [1.92, 1.74, 2.4], 'zmin': -0.6, 'mats': [0, 45]}\n{
# 'name': 'SM_VK_Wall_Plaster_Frame', 'tris': 1108, 'bbox': [3.13, 0.77, 3.6], 'zmin': -0.6, 'mats': [0, 2, 45, 47]}\n{'name': 'SM_VK_Wall_Plaster_Frame

# ==============================================================================================================
# [0005] 2026-09-23 13:11:05  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("construction","dev_catalog_a",(16,-40,24),(16,-9,1.0),lens=32,res=(1600,900))
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\construction\\dev_catalog_a.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 13:11:29  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("construction","dev_row1",(16,-13,6.5),(16,0,0.8),lens=30,res=(1600,900))
p=ws_shot("construction","dev_row2",(16,-22,6.5),(16,-9,1.2),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0007] 2026-09-23 13:12:18  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("construction")
sc,coll,asm=ws_scene("construction")
ws_clear_assembly("construction")
pv=g["place_v"]
O=(0,40,0)
# overlay test: finished roof + frame at same spot
for i,(fin,frm,rot) in enumerate([("SM_VK_Roof_Gable","SM_VK_Roof_Gable_Frame",180),("SM_VK_Roof_Mid","SM_VK_Roof_Mid_Frame",0),("SM_VK_Roof_Hip","SM_VK_Roof_Hip_Frame",0)]):
    x=-3+3*i
    pv(asm,fin,x,0,0,rot,O,{}); pv(asm,frm,x,0,0,rot,O,{})
# frames alone next to it
O2=(0,52,0)
for i,(frm,rot) in enumerate([("SM_VK_Roof_Gable_Frame",180),("SM_VK_Roof_Mid_Frame",0),("SM_VK_Roof_Hip_Frame",0)]):
    pv(asm,frm,-3+3*i,0,0,rot,O2,{})
p=ws_shot("construction","dev_roof_overlay",(-2,20,4.0),(1,40,2.5),lens=40,res=(1600,900))
p=ws_shot("construction","dev_roof_overlay_top",(-9,33,14),(1,40,2.5),lens=35,res=(1600,900))
p=ws_shot("construction","dev_roof_frames",(-9,43,10),(1,52,2.0),lens=35,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0008] 2026-09-23 13:12:44  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
frames=[o for o in asm.objects if "Frame" in o.name and o.location.y<45]
for o in frames: o.hide_render=True
p=ws_shot("construction","dev_roof_finished_only",(-2,20,4.0),(1,40,2.5),lens=40,res=(1200,675))
for o in frames: o.hide_render=False
p=ws_shot("construction","dev_roof_overlay_end",(-14,33,3.5),(-3,40,2.5),lens=35,res=(1200,675))
p=ws_shot("construction","dev_roof_frames_low",(-10,44,3.0),(0,52,2.5),lens=32,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0009] 2026-09-23 13:14:47  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_construction") or bpy.data.texts.new("ws_construction"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
try:
    g=ws_ns("construction")
    objs=ws_build("construction", g=g, names=["SM_VK_Roof_Mid_Frame","SM_VK_Roof_Gable_Frame","SM_VK_Roof_Hip_Frame"])
    for s in ws_stats(objs): print(s)
    sc,coll,asm=ws_scene("construction")
    for o in coll.objects: o.hide_render=True
    ws_clear_assembly("construction")
    for st in range(4):
        g["build_construction_site"](asm,(-24+st*16,0,0),st,seed=1)
    print(len(asm.objects))
except Exception:
    traceback.print_exc()
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Roof_Mid_Frame', 'tris': 1684, 'bbox': [3.0, 8.39, 4.44], 'zmin': -0.48, 'mats': [2, 23]}\n{'na
# me': 'SM_VK_Roof_Gable_Frame', 'tris': 3268, 'bbox': [4.11, 8.93, 4.8], 'zmin': -0.64, 'mats': [2, 23]}\n{'name': 'SM_VK_Roof_Hip_Frame', 'tris': 2592
# , 'bbox': [4.31, 8.42, 4.5], 'zmin': -0.53, 'mats': [2, 23]}\n133\n"}

# ==============================================================================================================
# [0010] 2026-09-23 13:15:33  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev_stages_34",(-30,-34,17),(0,0,2.5),lens=35,res=(1600,900))
ws_shot("construction","dev_stages_colony",(0,-25.7,30.6),(0,0,0),lens=35,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0011] 2026-09-23 13:16:39  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("construction","dev_stage1_close",(-17,-11,5.0),(-8,-2,1.2),lens=35,res=(1600,900))
ws_shot("construction","dev_stage0_close",(-31,-10,5.0),(-24,-2,0.4),lens=35,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0012] 2026-09-23 13:23:33  blender  ok
# ==============================================================================================================
import bpy, traceback, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_construction") or bpy.data.texts.new("ws_construction"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
t0=time.time()
try:
    g=ws_ns("construction")
    names=[n for n,_,_ in g["WS_SPECS"]][15:]+["SM_VK_BuildSite_Cell"]
    objs=ws_build("construction", g=g, names=names)
    for s in ws_stats(objs): print(s)
except Exception:
    traceback.print_exc()
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_BuildSite_Cell', 'tris': 736, 'bbox': [3.0, 3.0, 0.99], 'zmin': -0.6, 'mats': [2, 11, 26, 28]}\
# n{'name': 'SM_VK_Prop_Wheelbarrow', 'tris': 780, 'bbox': [2.2, 0.73, 0.84], 'zmin': -0.0, 'mats': [2, 5, 23, 45]}\n{'name': 'SM_VK_Prop_MortarTub', 't
# ris': 520, 'bbox': [1.85, 0.93, 0.97], 'zmin': -0.01, 'mats': [1, 2, 5, 21, 23, 25]}\n{'name': 'SM_VK_Prop_LadderLean', 'tris': 168, 'bbox': [0.5, 0.7
# 7, 2.79], 'zmin': -0.0, 'mats': [2]}\n{'name': 'SM_VK_Prop_ShearLegs', 'tris': 580, 'bbox': [3.01, 2.76, 5.23], 'zmin': -0.08, 'mats': [2, 5, 16, 24, 
# 25, 28, 34, 40]}\n{'name': 'SM_VK_Pile_Logs_1', 'tris': 368, 'bbox': [2.94, 1.46, 0.56], 'zmin': -0.1, 'mats': [33, 40]}\n{'name': 'SM_VK_Pile_Logs_2'
# , 'tris': 792, 'bbox': [2.95, 1.85, 0.9], 'zmin': -0.1, 'mats': [33, 40]}\n{'name': 'SM_VK_Pile_Logs_3', 'tris': 1080, 'bbox': [2.95, 1.85, 1.48], 'zm

# ==============================================================================================================
# [0013] 2026-09-23 13:25:02  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
sc,coll,asm=ws_scene("construction")
g=ws_ns("construction")
names=[n for n,_,_ in g["WS_SPECS"]]
objs=[bpy.data.objects[n] for n in names]
for o in objs: o.hide_render=False; o.hide_viewport=False
# rows by category
rows=[["SM_VK_BuildSite_Cell","SM_VK_Foundation_Wall","SM_VK_Foundation_Corner","SM_VK_Wall_Stone_Half","SM_VK_Wall_Stone_Half_Door","SM_VK_Corner_Stone_Half","SM_VK_Wall_Plaster_Frame","SM_VK_Wall_Plaster_Frame_Door","SM_VK_Wall_Timber_Frame"],
      ["SM_VK_Roof_Mid_Frame","SM_VK_Roof_Gable_Frame","SM_VK_Roof_Hip_Frame","SM_VK_Scaffold_Wall","SM_VK_Scaffold_Corner","SM_VK_Scaffold_Ladder","SM_VK_Prop_ShearLegs"],
      ["SM_VK_Pile_Logs_1","SM_VK_Pile_Logs_2","SM_VK_Pile_Logs_3","SM_VK_Pile_Planks_1","SM_VK_Pile_Planks_2","SM_VK_Pile_Planks_3","SM_VK_Stockpile_Border"],
      ["SM_VK_Pile_Stone_1","SM_VK_Pile_Stone_2","SM_VK_Pile_Stone_3","SM_VK_Pile_Sacks_1","SM_VK_Pile_Sacks_2","SM_VK_Pile_Sacks_3","SM_VK_Prop_Wheelbarrow","SM_VK_Prop_MortarTub","SM_VK_Prop_LadderLean"],
      ["SM_VK_Tent_A","SM_VK_Tent_Bell","SM_VK_Prop_Campfire","SM_VK_Prop_Bedroll","SM_VK_Prop_Wagon_Covered"],
      ["SM_VK_Prop_ChoppingBlock","SM_VK_Prop_Sawhorse","SM_VK_Prop_SawPit","SM_VK_Prop_Privy","SM_VK_Prop_WaysideShrine"]]
sp={0:4.2,1:6.0,2:3.6,3:3.4,4:6.0,5:4.2}
y=-24
for ri,row in enumerate(rows):
    x=-22
    for n in row:
        o=bpy.data.objects[n]; o.location=(x,y,0); x+=sp[ri]
    y-= {0:6,1:11,2:5,3:5,4:7,5:6}[ri]
print(set(names)-set(sum(rows,[])))
ws_shot("construction","dev_cat_piles",(-10,-52,9),(-10,-40,0.5),lens=40,res=(1600,900))
ws_shot("construction","dev_cat_camp",(-10,-66,7),(-10,-54,1.0),lens=40,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: set()\n"}

# ==============================================================================================================
# [0014] 2026-09-23 13:26:07  blender  ok
# ==============================================================================================================
exec(bpy.data.texts["ws_common"].as_string())
from mathutils import Vector
def shot(name, off, tgt_off=(0,0,0.8), lens=40, res=(960,540)):
    o=bpy.data.objects[name]; L=o.location
    return ws_shot("construction","dev_"+name.replace("SM_VK_",""),tuple(L+Vector(off)),tuple(L+Vector(tgt_off)),lens=lens,res=res)
shot("SM_VK_Tent_A",(-5,-6,3.5),(0,0,1.0))
shot("SM_VK_Prop_Wagon_Covered",(-4,-6,3.5),(0.4,0,1.0))
shot("SM_VK_Prop_SawPit",(-4,-5,3.5),(0,0,0.6))
shot("SM_VK_Prop_WaysideShrine",(-2.5,-3.5,2.8),(0,0,1.6))
shot("SM_VK_Prop_ShearLegs",(-6,-8,4),(0,0,2.2))
shot("SM_VK_Prop_ChoppingBlock",(-2.2,-2.8,1.8),(0,0,0.4))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 13:28:26  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py",encoding="utf8").read()
t=bpy.data.texts["ws_construction"]; t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
from mathutils import Vector
try:
    g=ws_ns("construction")
    names=["SM_VK_Pile_Stone_3","SM_VK_Pile_Stone_2","SM_VK_Pile_Stone_1","SM_VK_Pile_Sacks_1","SM_VK_Pile_Sacks_2","SM_VK_Pile_Sacks_3","SM_VK_Prop_Campfire","SM_VK_Tent_Bell","SM_VK_Tent_A","SM_VK_Prop_Wagon_Covered","SM_VK_Prop_SawPit","SM_VK_Prop_ShearLegs","SM_VK_Prop_WaysideShrine","SM_VK_Wall_Stone_Half","SM_VK_Wall_Stone_Half_Door"]
    objs=ws_build("construction", g=g, names=names)
    for s in ws_stats(objs): print(s['name'],s['tris'],s['bbox'])
except Exception: traceback.print_exc()
def shot(name, off, tgt_off=(0,0,0.8), lens=40, res=(960,540), tag=""):
    o=bpy.data.objects[name]; L=o.location
    return ws_shot("construction","dev_"+name.replace("SM_VK_","")+tag,tuple(L+Vector(off)),tuple(L+Vector(tgt_off)),lens=lens,res=res)
shot("SM_VK_Pile_Stone_2",(-3.5,-5.5,4.5),(3.4,0,0.4),lens=35,tag="_b")
shot("SM_VK_Tent_A",(-5,-6,3.5),(0,0,1.0),tag="_b")
shot("SM_VK_Prop_WaysideShrine",(-4,-5.5,3.4),(0,0,1.6),tag="_b")
shot("SM_VK_Prop_Campfire",(-2.2,-3,2.2),(0,0,0.5),tag="_b")
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Half 1264 [3.04, 1.38, 2.37]\nSM_VK_Wall_Stone_Half_Door 2164 [3.12, 1.65, 3.39]\nSM_VK_Prop_S
# hearLegs 580 [3.01, 2.76, 5.23]\nSM_VK_Pile_Stone_1 624 [2.7, 1.0, 0.47]\nSM_VK_Pile_Stone_2 976 [2.7, 1.0, 0.82]\nSM_VK_Pile_Stone_3 1416 [2.7, 1.0, 
# 1.18]\nSM_VK_Pile_Sacks_1 660 [1.7, 1.6, 0.45]\nSM_VK_Pile_Sacks_2 1260 [1.71, 1.69, 0.71]\nSM_VK_Pile_Sacks_3 2100 [1.72, 1.68, 0.96]\nSM_VK_Tent_A 8
# 71 [2.88, 5.42, 2.27]\nSM_VK_Tent_Bell 718 [4.95, 4.33, 3.44]\nSM_VK_Prop_Campfire 1344 [1.53, 1.6, 1.73]\nSM_VK_Prop_Wagon_Covered 2906 [5.16, 1.92, 
# 1.81]\nSM_VK_Prop_SawPit 960 [4.06, 2.81, 2.85]\nSM_VK_Prop_WaysideShrine 1775 [1.21, 1.23, 3.22]\n"}
