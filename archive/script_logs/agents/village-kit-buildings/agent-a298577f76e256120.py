# village-kit-buildings / agent-a298577f76e256120.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:53:58  blender  ok
# ==============================================================================================================
import bpy
print(bpy.app.version_string)
print([s.name for s in bpy.data.scenes])
print([t.name for t in bpy.data.texts])
src=bpy.data.texts["vk_helpers"].as_string()
print(len(src.splitlines()))
for fn in ["def rock(","def lathe(","def ring(","def _cyl(","def arch_ring(","def arch_soffit(","def wall_rocks(","def roof_hip(","def laundry(","NET"]:
    print(fn, src.count(fn))
print(bpy.data.objects.get("SM_VK_Wall_Stone"), bpy.data.materials.get("M_VK_Net"))
# ---- result ----
# {"result":"Code executed successfully: 4.4.3\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n['mc_helpers', 'tre
# e_build', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex', 'vk_tex2', 'vk_texgen', 'wk_helpers', 'ws_common']\n3041\ndef 
# rock( 1\ndef lathe( 1\ndef ring( 1\ndef _cyl( 1\ndef arch_ring( 1\ndef arch_soffit( 1\ndef wall_rocks( 1\ndef roof_hip( 1\ndef laundry( 1\nNET 1\n<bpy
# _struct, Object(\"SM_VK_Wall_Stone\") at 0x000001CB8435F908> <bpy_struct, Material(\"M_VK_Net\") at 0x000001CC687BFE48>\n"}

# ==============================================================================================================
# [0002] 2026-09-23 12:54:42  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials["M_VK_Net"]
print(m.blend_method if hasattr(m,'blend_method') else None, getattr(m,'surface_render_method',None))
for n in m.node_tree.nodes:
    print(n.type, n.name, getattr(n,'image',None) and n.image.name, getattr(n,'image',None) and tuple(n.image.size))
w=bpy.data.materials["M_VK_Water"]
for n in w.node_tree.nodes: print("W",n.type,n.name)
b=next(n for n in w.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
print([ (i.name, i.default_value if not hasattr(i.default_value,'__len__') else tuple(i.default_value)) for i in b.inputs if i.name in ("Base Color","Roughness","Alpha","Transmission Weight","Metallic")])
# who uses NET already?
users=[o.name for o in bpy.data.objects if o.type=='MESH' and o.data.materials and len(o.data.materials)>51 and any(p.material_index==51 for p in o.data.polygons)]
print(users[:10])
# ---- result ----
# {"result":"Code executed successfully: HASHED DITHERED\nOUTPUT_MATERIAL Material Output None None\nBSDF_PRINCIPLED Principled BSDF None None\nUVMAP UV
#  Map None None\nTEX_IMAGE Image Texture T_VK_Net_BC (512, 512)\nTEX_IMAGE Image Texture.001 T_VK_Net_N (512, 512)\nTEX_IMAGE Image Texture.002 T_VK_Ne
# t_R (512, 512)\nVERTEX_COLOR Color Attribute None None\nMIX Mix None None\nMATH Math None None\nNORMAL_MAP Normal Map None None\nTEX_IMAGE Image Textu
# re.003 T_VK_Net_A (512, 512)\nMATH Math.001 None None\nBSDF_TRANSPARENT Transparent BSDF None None\nMIX_SHADER Mix Shader None None\nW OUTPUT_MATERIAL
#  Material Output\nW BSDF_PRINCIPLED Principled BSDF\nW UVMAP UV Map\nW TEX_IMAGE Image Texture\nW TEX_IMAGE Image Texture.001\nW TEX_IMAGE Image Textu
# re.002\nW VERTEX_COLOR Color Attribute\nW MIX Mix\nW MATH Math\nW NORMAL_MAP Normal Map\n[('Base Color', (0.800000011920929, 0.800000011920929, 0.8000

# ==============================================================================================================
# [0003] 2026-09-23 13:05:30  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
P=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py"
src=open(P,encoding="utf8").read()
t=bpy.data.texts.get("ws_water") or bpy.data.texts.new("ws_water"); t.clear(); t.write(src)
try:
    g=ws_ns("water")
    objs=ws_build("water",g=g)
    for s in ws_stats(objs): print(s)
except Exception as e:
    traceback.print_exc()
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Pier_Deck', 'tris': 1168, 'bbox': [3.26, 3.3, 3.38], 'zmin': -3.0, 'mats': [2, 5, 23, 39, 40]}\
# n{'name': 'SM_VK_Pier_End', 'tris': 2928, 'bbox': [3.52, 3.3, 5.52], 'zmin': -3.01, 'mats': [2, 5, 9, 16, 23, 39, 40]}\n{'name': 'SM_VK_Pier_Stairs', 
# 'tris': 544, 'bbox': [1.68, 1.52, 4.05], 'zmin': -3.0, 'mats': [2, 23, 39, 40]}\n{'name': 'SM_VK_Pier_Rail', 'tris': 752, 'bbox': [3.09, 0.18, 1.15], 
# 'zmin': -0.1, 'mats': [2, 16]}\n{'name': 'SM_VK_Prop_Rowboat', 'tris': 3632, 'bbox': [4.28, 1.49, 0.93], 'zmin': -0.25, 'mats': [2, 5, 10, 16, 23]}\n{
# 'name': 'SM_VK_Prop_Barge', 'tris': 5660, 'bbox': [9.84, 3.61, 5.58], 'zmin': -0.38, 'mats': [2, 5, 10, 12, 23, 25, 40]}\n"}

# ==============================================================================================================
# [0004] 2026-09-23 13:05:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
sc,coll,asm=ws_scene("water")
ws_clear_assembly("water")
# hide masters from renders during tests (they sit at the origin)
for o in coll.objects: o.hide_render=True
g["wat_env"](asm,"WS_water_Env_A",land=[(60,80,-40,30),(140,170,-40,30)],water=[(80,140,-40,30)])
O=(0,0,0); P=g["place_v"]
for i,x in enumerate((81.5,84.5)): P(asm,"SM_VK_Pier_Deck",x,0,0,0,O,{})
P(asm,"SM_VK_Pier_End",87.5,0,0,0,O,{})
P(asm,"SM_VK_Pier_Stairs",84.5,0,0,0,O,{})
P(asm,"SM_VK_Pier_Rail",81.5,0,0,0,O,{})
P(asm,"SM_VK_Pier_Rail",81.5,0,0,180,O,{})
P(asm,"SM_VK_Pier_Rail",84.5,0,0,180,O,{})
P(asm,"SM_VK_Prop_Rowboat",85,-4.2,-0.6,8,O,{})
P(asm,"SM_VK_Prop_Barge",92,5.5,-0.6,-10,O,{})
P(asm,"SM_VK_Prop_Crates",77.5,2,0,0,O,{})
p=ws_shot("water","t01_pier",(97,-13,6.5),(85,0,0),lens=35)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\water\\t01_pier.png\n"}

# ==============================================================================================================
# [0005] 2026-09-23 13:06:24  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects["WS_water_Env_A"]; me=o.data
print([m.name for m in me.materials])
from collections import Counter
print(Counter(p.material_index for p in me.polygons))
print([ (p.material_index, tuple(round(c,1) for c in p.center), tuple(round(c,2) for c in p.normal)) for p in me.polygons][:14])
w=bpy.data.materials["M_VK_Water"]
for n in w.node_tree.nodes:
    if n.type=="TEX_IMAGE": print(n.name, n.image.name if n.image else None)
# ---- result ----
# {"result":"Code executed successfully: ['MC_WK_Grass', 'M_VK_Soil', 'M_VK_Water', 'M_VK_RockMossy']\nCounter({0: 12})\n[(0, (70.0, -5.0, 0.0), (0.0, 0
# .0, 1.0)), (0, (70.0, -40.0, -0.8), (0.0, -1.0, -0.0)), (0, (70.0, 30.0, -0.8), (0.0, 1.0, 0.0)), (0, (80.0, -5.0, -0.8), (1.0, 0.0, 0.0)), (0, (60.0,
#  -5.0, -0.8), (-1.0, 0.0, -0.0)), (0, (155.0, -5.0, 0.0), (0.0, 0.0, 1.0)), (0, (155.0, -40.0, -0.8), (0.0, -1.0, -0.0)), (0, (155.0, 30.0, -0.8), (0.
# 0, 1.0, 0.0)), (0, (170.0, -5.0, -0.8), (1.0, 0.0, 0.0)), (0, (140.0, -5.0, -0.8), (-1.0, 0.0, -0.0)), (0, (110.0, -5.0, -0.6), (0.0, 0.0, 1.0)), (0, 
# (110.0, -5.0, -1.5), (0.0, 0.0, 1.0))]\nImage Texture T_VK_Water_BC\nImage Texture.001 T_VK_Water_N\nImage Texture.002 T_VK_Water_R\n"}

# ==============================================================================================================
# [0006] 2026-09-23 13:06:51  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py"
t=bpy.data.texts["ws_water"]; t.clear(); t.write(open(P_,encoding="utf8").read())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
g["wat_env"](asm,"WS_water_Env_A",land=[(60,80,-40,30),(140,170,-40,30)],water=[(80,140,-40,30)])
p=ws_shot("water","t02_pier",(97,-13,6.5),(85,0,0),lens=35)
p=ws_shot("water","t02_boats",(95,-8,4.0),(89,1.5,-0.3),lens=40)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0007] 2026-09-23 13:12:32  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py"
t=bpy.data.texts["ws_water"]; t.clear(); t.write(open(P_,encoding="utf8").read())
try:
    g=ws_ns("water"); objs=ws_build("water",g=g)
    sc,coll,asm=ws_scene("water")
    for o in coll.objects: o.hide_render=True
    for s in ws_stats(objs): print(s)
    ws_clear_assembly("water")
    E=g["wat_env"]
    E(asm,"WS_water_Env_A",land=[(60,80,-40,15),(140,170,-40,15)],water=[(80,140,-40,15)])
    E(asm,"WS_water_Env_B",land=[(60,112,15,60),(118,170,15,60)],water=[(112,118,15,60)])
    O=(0,0,0); Pv=g["place_v"]
    for x in (81.5,84.5): Pv(asm,"SM_VK_Pier_Deck",x,0,0,0,O,{})
    Pv(asm,"SM_VK_Pier_End",87.5,0,0,0,O,{}); Pv(asm,"SM_VK_Pier_Stairs",84.5,0,0,0,O,{})
    Pv(asm,"SM_VK_Pier_Rail",81.5,0,0,0,O,{}); Pv(asm,"SM_VK_Pier_Rail",81.5,0,0,180,O,{}); Pv(asm,"SM_VK_Pier_Rail",84.5,0,0,180,O,{})
    Pv(asm,"SM_VK_Prop_Rowboat",85,-4.2,-0.6,8,O,{}); Pv(asm,"SM_VK_Prop_Barge",94,-2,-0.6,-10,O,{})
    # stone bridge across river B (x 112..118) at y=28
    Pv(asm,"SM_VK_Bridge_Stone_Span",115,28,0,0,O,{})
    Pv(asm,"SM_VK_Bridge_Stone_Ramp",119.5,28,0,0,O,{}); Pv(asm,"SM_VK_Bridge_Stone_Ramp",110.5,28,0,180,O,{})
    # wood bridge at y=45
    Pv(asm,"SM_VK_Bridge_Wood_End",110.5,45,0,0,O,{}); Pv(asm,"SM_VK_Bridge_Wood_Mid",113.5,45,0,0,O,{})
    Pv(asm,"SM_VK_Bridge_Wood_Mid",116.5,45,0,0,O,{}); Pv(asm,"SM_VK_Bridge_Wood_End",119.5,45,0,180,O,{})
    for x in (112,115,118): Pv(asm,"SM_VK_Bridge_Wood_Bent",x,45,0,0,O,{})
    Pv(asm,"SM_VK_Bridge_Log",115,55,0,0,O,{})
except Exception: traceback.print_exc()
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Pier_Deck', 'tris': 1168, 'bbox': [3.26, 3.3, 3.38], 'zmin': -3.0, 'mats': [2, 5, 23, 39, 40]}\
# n{'name': 'SM_VK_Pier_End', 'tris': 2818, 'bbox': [3.52, 3.3, 5.52], 'zmin': -3.01, 'mats': [2, 5, 9, 16, 23, 39, 40]}\n{'name': 'SM_VK_Pier_Stairs', 
# 'tris': 544, 'bbox': [1.68, 1.52, 4.05], 'zmin': -3.0, 'mats': [2, 23, 39, 40]}\n{'name': 'SM_VK_Pier_Rail', 'tris': 536, 'bbox': [3.09, 0.18, 1.15], 
# 'zmin': -0.1, 'mats': [2, 16]}\n{'name': 'SM_VK_Prop_Rowboat', 'tris': 2148, 'bbox': [4.28, 1.42, 0.93], 'zmin': -0.25, 'mats': [2, 5, 10, 16, 23]}\n{
# 'name': 'SM_VK_Prop_Barge', 'tris': 3968, 'bbox': [9.85, 3.6, 5.58], 'zmin': -0.38, 'mats': [2, 5, 10, 12, 23, 25, 40]}\n{'name': 'SM_VK_Bridge_Wood_M
# id', 'tris': 1284, 'bbox': [3.1, 3.51, 1.69], 'zmin': -0.25, 'mats': [2, 23]}\n{'name': 'SM_VK_Bridge_Wood_End', 'tris': 2200, 'bbox': [3.24, 4.07, 2.

# ==============================================================================================================
# [0008] 2026-09-23 13:12:44  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","t03_stonebridge",(106,17,6.0),(115,28,0.4),lens=35)
ws_shot("water","t03_woodbridge",(106,36,5.5),(115,46,0.2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0009] 2026-09-23 13:13:18  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","t04_arch_front",(115,18.5,0.8),(115,28,0.3),lens=40)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0010] 2026-09-23 13:13:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water")
print({m.name:(m.use_backface_culling, getattr(m,'use_backface_culling_shadow',None)) for m in bpy.data.materials if m.name in ("M_VK_StoneBlock","M_VK_Stone","M_VK_Wood","M_VK_Planks")})
k=g["Kit"]()
R,zc,th=g["wat_sb_arc"]()
import math
a0,a1=math.pi/2+0.1,math.pi/2-0.1
def P(sx,sy,sz):
    a=a0 if sx<0 else a1; r=R if sz<0 else R+0.45
    return (math.cos(a)*r,-2.0 if sy<0 else -1.6,zc+math.sin(a)*r)
fs=g["wat_blk"](k,P,g["STONE_BLOCK"],bevel=0.045,segs=2)
k.bm.normal_update()
big=[f for f in k.bm.faces if f.calc_area()>0.05]
print(len(k.bm.faces), [(round(f.calc_area(),3), tuple(round(c,2) for c in f.normal)) for f in big])
# check centroid-outward
c=sum((v.co for v in k.bm.verts),__import__('mathutils').Vector())/len(k.bm.verts)
print([round(f.normal.dot(f.calc_center_median()-c),3) for f in big])
k.bm.free()
# ---- result ----
# {"result":"Code executed successfully: {'M_VK_Planks': (False, False), 'M_VK_Stone': (False, False), 'M_VK_StoneBlock': (False, False), 'M_VK_Wood': (
# False, False)}\n54 [(0.163, (0.0, -1.0, 0.0)), (0.112, (1.0, 0.0, -0.1)), (0.155, (0.0, -0.0, 1.0)), (0.112, (-1.0, 0.0, -0.1)), (0.163, (0.0, 1.0, 0.
# 0)), (0.127, (0.0, 0.0, -1.0))]\n[0.2, 0.271, 0.224, 0.271, 0.2, 0.224]\n"}

# ==============================================================================================================
# [0011] 2026-09-23 13:14:23  blender  ok
# ==============================================================================================================
import bpy
me=bpy.data.objects["SM_VK_Bridge_Stone_Span"].data
fr=[p for p in me.polygons if abs(p.center.y+2.01)<0.02 and p.normal.y<-0.9]
print(len(fr), [ (round(p.area,3), p.material_index, tuple(round(c,2) for c in p.center)) for p in fr[:8]])
fr2=[p for p in me.polygons if abs(p.center.y+2.01)<0.02]
print(len(fr2), [ (round(p.area,3), tuple(round(c,2) for c in p.normal)) for p in fr2[:8]])
print(len(me.polygons), len(me.vertices))
# ---- result ----
# {"result":"Code executed successfully: 71 [(0.135, 0, (-2.32, -2.01, -0.31)), (0.014, 45, (-2.41, -2.0, -0.47)), (0.014, 45, (-2.22, -2.0, -0.15)), (0
# .011, 45, (-2.14, -2.0, -0.42)), (0.013, 45, (-2.5, -2.0, -0.2)), (0.166, 0, (-2.07, -2.01, 0.09)), (0.013, 45, (-2.27, -2.0, 0.26)), (0.011, 45, (-1.
# 88, -2.0, -0.07))]\n155 [(0.135, (0.0, -1.0, 0.0)), (0.001, (0.13, -0.88, -0.45)), (0.001, (-0.43, -0.9, -0.12)), (0.001, (0.46, -0.88, 0.1)), (0.001,
#  (-0.09, -0.9, 0.44)), (0.014, (-0.17, -0.92, -0.34)), (0.014, (0.22, -0.92, 0.31)), (0.011, (0.33, -0.92, -0.2))]\n3900 4114\n"}

# ==============================================================================================================
# [0012] 2026-09-23 13:15:36  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py"
t=bpy.data.texts["ws_water"]; t.clear(); t.write(open(P_,encoding="utf8").read())
try:
    g=ws_ns("water"); objs=ws_build("water",g=g,names=["SM_VK_Bridge_Stone_Span","SM_VK_Bridge_Stone_Ramp","SM_VK_Bridge_Stone_Pier"])
    for o in objs: o.hide_render=True
    for s in ws_stats(objs): print(s)
    ws_shot("water","t05_arch_front",(115,18.5,0.8),(115,28,0.3),lens=40)
    ws_shot("water","t05_stonebridge",(106,17,6.0),(115,28,0.4),lens=35)
except Exception: traceback.print_exc()
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Bridge_Stone_Span', 'tris': 7480, 'bbox': [6.0, 4.2, 3.86], 'zmin': -1.6, 'mats': [0, 24, 38, 4
# 5]}\n{'name': 'SM_VK_Bridge_Stone_Ramp', 'tris': 2304, 'bbox': [4.71, 5.72, 2.73], 'zmin': -0.6, 'mats': [0, 24, 45]}\n{'name': 'SM_VK_Bridge_Stone_Pi
# er', 'tris': 466, 'bbox': [1.9, 6.72, 3.0], 'zmin': -2.0, 'mats': [0, 38, 45]}\n"}

# ==============================================================================================================
# [0013] 2026-09-23 13:21:37  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
P_=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_water.py"
t=bpy.data.texts["ws_water"]; t.clear(); t.write(open(P_,encoding="utf8").read())
try:
    g=ws_ns("water")
    new=[n for n,f,kw in g["WS_SPECS"] if not bpy.data.objects.get(n)]+["SM_VK_Bridge_Stone_Span"]
    objs=ws_build("water",g=g,names=new)
    for o in objs: o.hide_render=True
    for s in ws_stats(objs): print(s)
    sc,coll,asm=ws_scene("water")
    g["wat_env"](asm,"WS_water_Env_C",land=[(60,170,-80,-40)],water=[])
    O=(0,0,0); Pv=g["place_v"]
    for x in (100.5,103.5,109.5): Pv(asm,"SM_VK_Quay_Straight",x,-40.45,0,180,O,{})
    Pv(asm,"SM_VK_Quay_Stair",106.5,-40.45,0,180,O,{})
    Pv(asm,"SM_VK_Quay_Post",98.7,-40.4,0,180,O,{}); Pv(asm,"SM_VK_Quay_Post",111.3,-40.4,0,180,O,{})
    Pv(asm,"SM_VK_Wall_Stone_Axle",116.5,-40.25,0,180,O,{})
    Pv(asm,"SM_VK_Wall_Stone",119.5,-40.25,0,180,O,{})
    Pv(asm,"SM_VK_Wall_Timber",116.5,-40.25,3.0,180,O,{})
    w=Pv(asm,"SM_VK_WaterWheel",116.5,-38.9,1.3,90,O,{})
    Pv(asm,"SM_VK_Mill_WheelPier",116.5,-37.15,0,90,O,{})
    row=[("SM_VK_Prop_Millstone",0),("SM_VK_Prop_NetRack",0),("SM_VK_Prop_FishRack",0),("SM_VK_Prop_Creels",0),("SM_VK_Pile_Fish_1",0),("SM_VK_Pile_Fish_2",0),("SM_VK_Pile_Fish_3",0),("SM_VK_Prop_LavoirBasin",0),("SM_VK_Prop_HandPump",0)]
    x=92
    for n,r in row:
        Pv(asm,n,x,-48,0,r,O,{}); x+= 7 if "Lavoir" in n or "Rack" in n else 4.5
    Pv(asm,"SM_VK_Wall_Stone",x+1.5,-48,0,0,O,{}); Pv(asm,"SM_VK_Prop_WallFountain",x+1.5,-48,0,0,O,{})
except Exception: traceback.print_exc()
# ---- result ----
# {"result":"Code executed successfully: {'name': 'SM_VK_Bridge_Stone_Span', 'tris': 7480, 'bbox': [6.0, 4.26, 3.86], 'zmin': -1.6, 'mats': [0, 24, 38, 
# 45]}\n{'name': 'SM_VK_Quay_Straight', 'tris': 720, 'bbox': [3.0, 1.01, 2.03], 'zmin': -2.0, 'mats': [0, 5, 38, 45]}\n{'name': 'SM_VK_Quay_Post', 'tris
# ': 372, 'bbox': [0.67, 0.7, 1.21], 'zmin': -0.03, 'mats': [5, 45]}\n{'name': 'SM_VK_Quay_Stair', 'tris': 1040, 'bbox': [3.0, 1.3, 2.08], 'zmin': -2.0,
#  'mats': [0, 5, 38, 45]}\n{'name': 'SM_VK_WaterWheel', 'tris': 3248, 'bbox': [2.3, 5.2, 5.2], 'zmin': -2.6, 'mats': [2, 5, 23, 40]}\n{'name': 'SM_VK_W
# all_Stone_Axle', 'tris': 1136, 'bbox': [3.04, 0.89, 4.6], 'zmin': -1.6, 'mats': [0, 5, 27, 38, 45]}\n{'name': 'SM_VK_Mill_WheelPier', 'tris': 2086, 'b
# box': [1.19, 1.96, 3.23], 'zmin': -1.6, 'mats': [0, 5, 27, 38, 45]}\n{'name': 'SM_VK_Prop_Millstone', 'tris': 724, 'bbox': [2.22, 1.67, 1.33], 'zmin':

# ==============================================================================================================
# [0014] 2026-09-23 13:22:25  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("water","t06_quay_mill",(106,-28,7),(111,-40,0.5),lens=35)
ws_shot("water","t06_props",(118,-58,7.5),(114,-48,0.6),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0015] 2026-09-23 13:23:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("water"); sc,coll,asm=ws_scene("water")
for o in list(asm.objects):
    if o.name.split("_inst")[0] in ("SM_VK_Prop_Millstone","SM_VK_Prop_NetRack","SM_VK_Prop_FishRack","SM_VK_Prop_Creels","SM_VK_Pile_Fish_1","SM_VK_Pile_Fish_2","SM_VK_Pile_Fish_3","SM_VK_Prop_LavoirBasin","SM_VK_Prop_HandPump","SM_VK_Prop_WallFountain") or (o.name.startswith("SM_VK_Wall_Stone_inst") and o.location.y<-45):
        bpy.data.objects.remove(o)
O=(0,0,0); Pv=g["place_v"]
L=[("SM_VK_Prop_NetRack",92,-50,0),("SM_VK_Prop_FishRack",97,-50,0),("SM_VK_Prop_Creels",101,-50,0),("SM_VK_Prop_Millstone",104,-50,0),
   ("SM_VK_Pile_Fish_1",92,-55,0),("SM_VK_Pile_Fish_2",94.5,-55,0),("SM_VK_Pile_Fish_3",97.5,-55,0),("SM_VK_Prop_HandPump",101,-55,0),
   ("SM_VK_Prop_LavoirBasin",94,-61,0)]
for n,x,y,r in L: Pv(asm,n,x,y,0,r,O,{})
Pv(asm,"SM_VK_Wall_Stone",102,-60,0,0,O,{}); Pv(asm,"SM_VK_Prop_WallFountain",102,-60,0,0,O,{})
ws_shot("water","t07_props_a",(98,-61,5.5),(97,-51.5,0.8),lens=35)
ws_shot("water","t07_props_b",(99,-68.5,4.5),(98,-58.5,0.5),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0016] 2026-09-23 13:25:10  blender  ok
# ==============================================================================================================
import bpy
for nm in ("M_VK_Steel","M_VK_Paper","M_VK_Iron","M_VK_Bronze"):
    m=bpy.data.materials[nm]; b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    print(nm, [(i.name, round(i.default_value,2) if isinstance(i.default_value,float) else tuple(round(c,2) for c in i.default_value)) for i in b.inputs if i.name in ("Base Color","Metallic","Roughness")], [n.type for n in m.node_tree.nodes])
# ---- result ----
# {"result":"Code executed successfully: M_VK_Steel [('Base Color', (0.8, 0.8, 0.8, 1.0)), ('Metallic', 0.9), ('Roughness', 0.5)] ['OUTPUT_MATERIAL', 'B
# SDF_PRINCIPLED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', 'TEX_IMAGE', 'VERTEX_COLOR', 'RGBTOBW', 'MIX', 'MIX', 'MATH', 'NORMAL_MAP']\nM_VK_Paper [('Base Co
# lor', (0.8, 0.8, 0.8, 1.0)), ('Metallic', 0.0), ('Roughness', 0.5)] ['OUTPUT_MATERIAL', 'BSDF_PRINCIPLED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', 'TEX_IMA
# GE', 'VERTEX_COLOR', 'MIX', 'MATH', 'NORMAL_MAP']\nM_VK_Iron [('Base Color', (0.8, 0.8, 0.8, 1.0)), ('Metallic', 0.0), ('Roughness', 0.5)] ['OUTPUT_MA
# TERIAL', 'BSDF_PRINCIPLED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', 'TEX_IMAGE', 'VERTEX_COLOR', 'MIX', 'MATH', 'NORMAL_MAP', 'TEX_IMAGE']\nM_VK_Bronze [('
# Base Color', (0.8, 0.8, 0.8, 1.0)), ('Metallic', 1.0), ('Roughness', 0.5)] ['OUTPUT_MATERIAL', 'BSDF_PRINCIPLED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', '
