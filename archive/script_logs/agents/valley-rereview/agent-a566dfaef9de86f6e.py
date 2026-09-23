# valley-rereview / agent-a566dfaef9de86f6e.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 19:27:15  blender  ok
# ==============================================================================================================
import bpy, collections
c=bpy.data.collections["VK_ValleyTown"]
cnt=collections.Counter(); low=[]
for o in c.all_objects:
    n=o.name
    if n.startswith(("SM_VK_Tree_","SM_VK_Bush_Large")):
        b=n.split("_inst")[0]
        cnt[b]+=1
        if o.location.z<3.5: low.append((b,round(o.location.x,1),round(o.location.y,1),round(o.location.z,2)))
print(dict(cnt))
print(len(low))
for l in sorted(low,key=lambda t:t[2]): print(l)
# ---- result ----
# {"result":"Code executed successfully: {'SM_VK_Tree_Pine_Young': 194, 'SM_VK_Bush_Large': 2, 'SM_VK_Tree_Apple': 3, 'SM_VK_Tree_Willow': 3, 'SM_VK_Tre
# e_Birch': 21, 'SM_VK_Tree_Oak_B': 27, 'SM_VK_Tree_Oak_A': 19, 'SM_VK_Tree_Pine_B': 213, 'SM_VK_Tree_Pine_A': 197, 'SM_VK_Tree_Oak_Autumn': 28}\n12\n('
# SM_VK_Bush_Large', 1637.3, 3.6, 1.5)\n('SM_VK_Tree_Apple', 1711.3, 7.7, 1.5)\n('SM_VK_Tree_Willow', 1714.9, 22.3, 0.0)\n('SM_VK_Tree_Willow', 1662.5, 
# 30.9, 0.0)\n('SM_VK_Tree_Willow', 1504.3, 34.3, 0.0)\n('SM_VK_Tree_Birch', 1692.8, 62.2, 1.5)\n('SM_VK_Tree_Apple', 1683.9, 65.6, 1.5)\n('SM_VK_Tree_P
# ine_Young', 1541.1, 80.2, 3.0)\n('SM_VK_Tree_Birch', 1713.5, 87.5, 1.5)\n('SM_VK_Tree_Birch', 1709.0, 87.6, 1.5)\n('SM_VK_Bush_Large', 1712.3, 110.4, 
# 1.5)\n('SM_VK_Tree_Apple', 1710.8, 119.1, 1.5)\n"}

# ==============================================================================================================
# [0002] 2026-09-23 19:28:15  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
terr=[o for o in bpy.data.collections["VK_ValleyTerrain"].all_objects if o.type=="MESH"]
def hz(x,y):
    best=None
    for o in terr:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if not (min(v.x for v in bb)<=x<=max(v.x for v in bb) and min(v.y for v in bb)<=y<=max(v.y for v in bb)): continue
        oe=o.evaluated_get(dg); mi=o.matrix_world.inverted()
        ok,loc,nor,idx=oe.ray_cast(mi@Vector((x,y,50)), (mi.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            w=o.matrix_world@loc
            if best is None or w.z>best[0]: best=(w.z,o.name,idx)
    return best
out=[]
for i in range(8,24):
    x=1500+3*i+1.5
    r=hz(x,91.5)
    out.append((i,round(r[0],2) if r else None, r[1] if r else None))
print(out)
# ---- result ----
# {"result":"Code executed successfully: [(8, 3.0, 'VKV_Chunk_0_1'), (9, 3.0, 'VKV_Chunk_0_1'), (10, 3.0, 'VKV_Chunk_0_1'), (11, 6.0, 'VKV_Chunk_0_1'), 
# (12, 6.0, 'VKV_Chunk_0_1'), (13, 3.0, 'VKV_Chunk_0_1'), (14, 3.0, 'VKV_Chunk_0_1'), (15, 3.0, 'VKV_Chunk_1_1'), (16, 3.0, 'VKV_Chunk_1_1'), (17, 6.0, 
# 'VKV_Chunk_1_1'), (18, 6.0, 'VKV_Chunk_1_1'), (19, 3.0, 'VKV_Chunk_1_1'), (20, 3.0, 'VKV_Chunk_1_1'), (21, 3.0, 'VKV_Chunk_1_1'), (22, 3.0, 'VKV_Chunk
# _1_1'), (23, 3.0, 'VKV_Chunk_1_1')]\n"}

# ==============================================================================================================
# [0003] 2026-09-23 19:28:37  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_02_postern_lane", (1545,70,30), (1545,93,3), lens=32, res=(1400,800), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_02_postern_lane.png\n"}

# ==============================================================================================================
# [0004] 2026-09-23 19:29:17  blender  ok
# ==============================================================================================================
import bpy
def dump(mn):
    m=bpy.data.materials.get(mn)
    if not m: print(mn,"MISSING"); return
    print("==",mn)
    for n in m.node_tree.nodes:
        extra=""
        if n.type=="TEX_IMAGE" and n.image: extra=n.image.name
        if n.type in("HUE_SAT",): extra=[round(i.default_value,3) if not hasattr(i.default_value,'__len__') else None for i in n.inputs]
        if n.type=="MIX": extra=(n.data_type,n.blend_type)
        if n.type=="MATH": extra=n.operation
        print("  ",n.type,n.name,extra)
    for l in m.node_tree.links: print("    ",l.from_node.name,l.from_socket.name,"->",l.to_node.name,l.to_socket.name)
for mn in ("M_VK_Foliage","M_VK_Soil","M_VK_Roof_Thatch","M_VK_Thatch","M_VK_RoofRed"): dump(mn)
# ---- result ----
# {"result":"Code executed successfully: == M_VK_Foliage\n OUTPUT_MATERIAL Material Output \n BSDF_PRINCIPLED Principled BSDF \n UVMAP UV Map \n TEX_IMA
# GE Image Texture T_VK_Foliage_BCA\n VERTEX_COLOR Color Attribute \n MIX Mix ('RGBA', 'MULTIPLY')\n MATH Math GREATER_THAN\n BSDF_TRANSLUCENT Transluce
# nt BSDF \n MIX_SHADER Mix Shader \n BSDF_TRANSPARENT Transparent BSDF \n MIX_SHADER Mix Shader.001 \n UV Map UV -> Image Texture Vector\n Image Textur
# e Color -> Mix A\n Color Attribute Color -> Mix B\n Mix Result -> Principled BSDF Base Color\n Image Texture Alpha -> Math Value\n Mix Result -> Trans
# lucent BSDF Color\n Principled BSDF BSDF -> Mix Shader Shader\n Translucent BSDF BSDF -> Mix Shader Shader\n Math Value -> Mix Shader.001 Fac\n Transp
# arent BSDF BSDF -> Mix Shader.001 Shader\n Mix Shader Shader -> Mix Shader.001 Shader\n Mix Shader.001 Shader -> Material Output Surface\n== M_VK_Soil

# ==============================================================================================================
# [0005] 2026-09-23 19:30:05  blender  ok
# ==============================================================================================================
import bpy, collections
c=bpy.data.collections["VK_ValleyTown"]
res=collections.defaultdict(set); cnt=collections.Counter()
for o in c.all_objects:
    if o.type!="MESH": continue
    b=o.name.split("_inst")[0]
    mats=[m.name for m in o.data.materials if m]
    if "M_VK_Foliage" in mats: cnt[b]+=1
    if b.startswith(("SM_VK_Quarry","SM_VK_Mine","SM_VK_Deco_Hedge","SM_VK_Deco_Ivy")): res[b]|=set(mats)
print(dict(res))
print(cnt.most_common(40))
# ---- result ----
# {"result":"Code executed successfully: {'SM_VK_Deco_Ivy_B': {'M_VK_Void', 'M_VK_Bread', 'M_VK_Shutter_Teal', 'M_VK_Plaster', 'M_VK_Hide', 'M_VK_Pigski
# n', 'M_VK_Wattle', 'M_VK_Iron', 'M_VK_RockMossy', 'M_VK_Paper', 'M_VK_Coal', 'M_VK_Clock', 'M_VK_Rock', 'M_VK_BarkPine', 'M_VK_MushRed', 'M_VK_Crops',
#  'M_VK_Bronze', 'M_VK_Cloth_Cream', 'M_VK_Planks', 'M_VK_Steel', 'M_VK_BarkBirch', 'M_VK_Water', 'M_VK_RoofRed', 'M_VK_FieldStone', 'M_VK_Hay', 'M_VK_
# Cloth_Red', 'M_VK_Window', 'M_VK_Leaf', 'M_VK_Apple', 'M_VK_MushStem', 'M_VK_Leaves', 'M_VK_EndGrain', 'M_VK_MushBrown', 'M_VK_FlowerYellow', 'M_VK_St
# ained', 'M_VK_FlowerPink', 'M_VK_Soil', 'M_VK_Glow', 'M_VK_Ashlar', 'M_VK_Moss', 'M_VK_BarkOak', 'M_VK_MushGlow', 'M_VK_Clay', 'M_VK_Thatch', 'M_VK_Fo
# liage', 'M_VK_StoneBlock', 'M_VK_Net', 'M_VK_BarkMossy', 'M_VK_Pumpkin', 'M_VK_Stone', 'M_VK_Wood', 'M_VK_Burlap'}, 'SM_VK_Deco_Ivy_A': {'M_VK_Void', 

# ==============================================================================================================
# [0006] 2026-09-23 19:30:17  blender  ok
# ==============================================================================================================
import bpy, collections
for nm in ("SM_VK_Quarry_Face_Straight","SM_VK_Mine_Portal","SM_VK_Deco_Hedge"):
    o=bpy.data.objects.get(nm); me=o.data
    zmax=max(v.co.z for v in me.vertices)
    area=collections.Counter()
    for p in me.polygons:
        m=me.materials[p.material_index].name if me.materials[p.material_index] else None
        if p.normal.z>0.6: area[m]+=p.area
    print(nm, round(zmax,2), [(k,round(v,2)) for k,v in area.most_common(5)])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Quarry_Face_Straight 3.55 [('M_VK_Rock', 10.76), ('M_VK_StoneBlock', 10.48), ('M_VK_Moss', 4.62), ('M_VK_
# RockMossy', 0.39), ('M_VK_Void', 0.0)]\nSM_VK_Mine_Portal 5.15 [('M_VK_Rock', 48.83), ('M_VK_Moss', 37.79), ('M_VK_RockMossy', 29.03), ('M_VK_Soil', 9
# .18), ('M_VK_Planks', 5.97)]\nSM_VK_Deco_Hedge 1.32 [('M_VK_Foliage', 3.93), ('M_VK_Moss', 1.94), ('M_VK_Soil', 1.53)]\n"}

# ==============================================================================================================
# [0007] 2026-09-23 19:30:41  blender  ok
# ==============================================================================================================
import bpy
for mn in ("M_VK_Moss","M_VK_TerrainTown"):
    m=bpy.data.materials.get(mn)
    print("==",mn)
    for n in m.node_tree.nodes:
        extra=""
        if n.type=="TEX_IMAGE" and n.image: extra=n.image.name
        if n.type=="HUE_SAT": extra=[round(i.default_value,3) for i in n.inputs[:4]]
        if n.type=="MIX": extra=(n.data_type,n.blend_type)
        if n.type=="MATH": extra=n.operation
        if n.type=="BSDF_PRINCIPLED" and not n.inputs["Base Color"].is_linked: extra=tuple(round(v,3) for v in n.inputs["Base Color"].default_value)
        if n.type=="RGB": extra=tuple(round(v,3) for v in n.outputs[0].default_value)
        print("  ",n.type,n.name,extra)
    if mn=="M_VK_Moss":
        for l in m.node_tree.links: print("    ",l.from_node.name,l.from_socket.name,"->",l.to_node.name,l.to_socket.name)
# ---- result ----
# {"result":"Code executed successfully: == M_VK_Moss\n OUTPUT_MATERIAL Material Output \n BSDF_PRINCIPLED Principled BSDF \n UVMAP UV Map \n TEX_IMAGE 
# Image Texture T_VK_Moss_BC\n TEX_IMAGE Image Texture.001 T_VK_Moss_N\n TEX_IMAGE Image Texture.002 T_VK_Moss_R\n VERTEX_COLOR Color Attribute \n MIX M
# ix ('RGBA', 'MULTIPLY')\n MATH Math MULTIPLY\n NORMAL_MAP Normal Map \n UV Map UV -> Image Texture Vector\n UV Map UV -> Image Texture.001 Vector\n UV
#  Map UV -> Image Texture.002 Vector\n Image Texture Color -> Mix A\n Color Attribute Color -> Mix B\n Mix Result -> Principled BSDF Base Color\n Image
#  Texture.002 Color -> Math Value\n Math Value -> Principled BSDF Roughness\n Image Texture.001 Color -> Normal Map Color\n Normal Map Normal -> Princi
# pled BSDF Normal\n Principled BSDF BSDF -> Material Output Surface\n== M_VK_TerrainTown\n OUTPUT_MATERIAL Material Output \n BSDF_PRINCIPLED Principle

# ==============================================================================================================
# [0008] 2026-09-23 19:30:52  blender  ok
# ==============================================================================================================
import bpy
c=bpy.data.collections["VK_ValleyTown"]
for pre in ("SM_VK_Deco_Hedge","SM_VK_Mine_Portal","SM_VK_Quarry_Face","SM_VK_Deco_Ivy"):
    L=[(o.name,round(o.location.x,1),round(o.location.y,1),round(o.location.z,1)) for o in c.all_objects if o.name.startswith(pre)]
    print(pre,len(L),L[:12])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Deco_Hedge 10 [('SM_VK_Deco_Hedge_inst', 1653.0, 94.5, 3.0), ('SM_VK_Deco_Hedge_inst.001', 1665.0, 94.5, 
# 3.0), ('SM_VK_Deco_Hedge_inst.002', 1653.0, 97.5, 3.0), ('SM_VK_Deco_Hedge_inst.003', 1665.0, 97.5, 3.0), ('SM_VK_Deco_Hedge_inst.004', 1653.0, 100.5,
#  3.0), ('SM_VK_Deco_Hedge_inst.005', 1665.0, 100.5, 3.0), ('SM_VK_Deco_Hedge_inst.006', 1653.0, 103.5, 3.0), ('SM_VK_Deco_Hedge_inst.007', 1665.0, 103
# .5, 3.0), ('SM_VK_Deco_Hedge_inst.008', 1654.5, 105.0, 3.0), ('SM_VK_Deco_Hedge_inst.009', 1663.5, 105.0, 3.0)]\nSM_VK_Mine_Portal 1 [('SM_VK_Mine_Por
# tal_inst', 1512.0, 97.5, 3.0)]\nSM_VK_Quarry_Face 9 [('SM_VK_Quarry_Face_Straight_inst', 1545.0, 100.5, 3.0), ('SM_VK_Quarry_Face_InnerCorner_inst', 1
# 548.0, 100.5, 3.0), ('SM_VK_Quarry_Face_InnerCorner_inst.001', 1542.0, 100.5, 3.0), ('SM_VK_Quarry_Face_Straight_inst.001', 1548.0, 97.5, 3.0), ('SM_V

# ==============================================================================================================
# [0009] 2026-09-23 19:31:08  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_03_hedge", (1659,82,18), (1659,99,3), lens=35, res=(1200,700), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_03_hedge.png\n"}

# ==============================================================================================================
# [0010] 2026-09-23 19:31:42  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_04_mine", (1514,80,16), (1513,97,4), lens=35, res=(1200,700), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_04_mine.png\n"}

# ==============================================================================================================
# [0011] 2026-09-23 19:32:19  blender  ok
# ==============================================================================================================
import bpy, collections
c=bpy.data.collections["VK_ValleyTown"]
L=[]
for o in c.all_objects:
    if o.name.startswith("SM_VK_Crop_"):
        x,y=o.location.x-1500,o.location.y
        inside=(69<=x<189 and 75<=y<138)
        L.append((o.name,round(o.location.x,1),round(o.location.y,1),round(o.location.z,1),round(o.scale.x,2),inside))
ins=[l for l in L if l[5]]
print(len(L),len(ins), collections.Counter(l[0].split("_inst")[0] for l in ins))
for l in ins: print(l[:5])
# ---- result ----
# {"result":"Code executed successfully: 59 32 Counter({'SM_VK_Crop_Cabbage': 15, 'SM_VK_Crop_Lavender': 9, 'SM_VK_Crop_Carrot': 8})\n('SM_VK_Crop_Carro
# t_inst.012', 1573.5, 79.5, 3.0, 0.8)\n('SM_VK_Crop_Cabbage_inst.011', 1630.5, 91.5, 3.0, 0.8)\n('SM_VK_Crop_Carrot_inst.013', 1636.5, 91.5, 3.0, 0.8)\
# n('SM_VK_Crop_Carrot_inst.014', 1645.5, 91.5, 3.0, 0.8)\n('SM_VK_Crop_Lavender_inst.009', 1651.5, 91.5, 3.0, 0.8)\n('SM_VK_Crop_Lavender_inst.010', 16
# 54.5, 91.5, 3.0, 0.8)\n('SM_VK_Crop_Carrot_inst.015', 1669.5, 91.5, 3.0, 0.8)\n('SM_VK_Crop_Carrot_inst.016', 1594.5, 94.5, 3.0, 0.8)\n('SM_VK_Crop_Ca
# bbage_inst.012', 1600.5, 94.5, 3.0, 0.8)\n('SM_VK_Crop_Cabbage_inst.013', 1603.5, 94.5, 3.0, 0.8)\n('SM_VK_Crop_Carrot_inst.017', 1597.5, 100.5, 3.0, 
# 0.8)\n('SM_VK_Crop_Lavender_inst.011', 1585.5, 103.5, 3.0, 0.8)\n('SM_VK_Crop_Lavender_inst.012', 1597.5, 103.5, 3.0, 0.8)\n('SM_VK_Crop_Cabbage_inst.

# ==============================================================================================================
# [0012] 2026-09-23 19:32:47  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_05_gardens_colony", (1642,64,32), (1642,93,3), lens=35, res=(1400,800), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_05_gardens_colony.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 19:33:32  blender  ERROR
# ==============================================================================================================
import bpy, numpy as np, collections
im=bpy.data.images["T_VK_GroundCtl_Town"]
w,h=im.size
px=np.array(im.pixels[:]).reshape(h,w,4)
print(w,h,im.interpolation, im.colorspace_settings.name)
R=np.round(px[:,:,0]*255).astype(int)
print(collections.Counter(R.flatten().tolist()).most_common(12))
m=(R==150)
print("cells R=150:",int(m.sum()))
# list row ranges
for j in range(h):
    cols=np.nonzero(m[j])[0]
    if len(cols): print(j, cols.tolist())
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: 'Image' object has no attribute 'interpolation'"}

# ==============================================================================================================
# [0014] 2026-09-23 19:33:53  blender  ok
# ==============================================================================================================
import bpy, numpy as np, collections
im=bpy.data.images["T_VK_GroundCtl_Town"]
w,h=im.size
px=np.array(im.pixels[:]).reshape(h,w,4)
print(w,h, im.colorspace_settings.name)
R=np.round(px[:,:,0]*255).astype(int)
print(collections.Counter(R.flatten().tolist()).most_common(12))
m=(R==150)
print("cells R=150:",int(m.sum()))
for j in range(h):
    cols=np.nonzero(m[j])[0]
    if len(cols): print(j, cols.tolist())
m2=bpy.data.materials["M_VK_TerrainTown"]
for n in m2.node_tree.nodes:
    if n.type=="TEX_IMAGE" and n.image and n.image.name=="T_VK_GroundCtl_Town":
        print("interp",n.interpolation, [ (l.from_node.type,l.from_node.name) for l in n.inputs[0].links])
# ---- result ----
# {"result":"Code executed successfully: 72 56 Non-Color\n[(0, 3609), (150, 221), (255, 182), (120, 20)]\ncells R=150: 221\n0 [59, 60, 61, 62, 63, 64]\n
# 1 [59, 60, 61, 62, 63, 64]\n2 [29, 30, 31, 32, 33, 35, 36, 37, 38, 59, 60, 61, 62, 63, 64]\n3 [29, 30, 31, 32, 33, 35, 36, 37, 38, 59, 60, 61, 62, 63,
#  64]\n4 [29, 30, 31, 32, 33, 35, 36, 37, 38, 59, 60, 61, 62, 63, 64]\n5 [29, 30, 31, 32, 33]\n6 [29, 30, 31, 32, 33, 36, 37]\n7 [36, 37]\n19 [44, 45, 
# 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]\n20 [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]\n21 [44, 45, 46, 47, 48, 49, 50, 
# 51, 52, 53, 54, 55, 56, 57, 58]\n22 [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58]\n23 [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 
# 56, 57, 58]\n24 [15, 16, 17, 18, 19]\n25 [15, 16, 17, 18, 19]\n26 [15, 16, 17, 18, 19]\n30 [1, 2, 3, 4, 5, 6]\n31 [1, 2, 3, 4, 5, 6, 12, 13, 14, 15, 1

# ==============================================================================================================
# [0015] 2026-09-23 19:34:17  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials["M_VK_TerrainTown"]; nt=m.node_tree
def trace(sock,depth=0,seen=None):
    seen=seen or set()
    for l in sock.links:
        n=l.from_node
        info=n.type
        if n.type=="VECT_MATH": info+=":"+n.operation+str([tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3) for i in n.inputs if not i.is_linked][:2])
        if n.type=="TEX_NOISE": info+=" scale=%s"%round(n.inputs['Scale'].default_value,4)
        if n.type=="MAPPING": info+=" loc=%s scale=%s"%(tuple(round(v,4) for v in n.inputs['Location'].default_value),tuple(round(v,5) for v in n.inputs['Scale'].default_value))
        print("  "*depth+f"{n.name} [{info}] -> {l.to_socket.name}")
        if n.name in seen: continue
        seen.add(n.name)
        for i in n.inputs:
            if i.is_linked: trace(i,depth+1,seen)
for n in nt.nodes:
    if n.type=="TEX_IMAGE" and n.image and n.image.name=="T_VK_GroundCtl_Town":
        trace(n.inputs[0])
# ---- result ----
# {"result":"Code executed successfully: Mapping [MAPPING loc=(0.0, 0.0, 0.0) scale=(0.00463, 0.00595, 1.0)] -> Vector\n Vector Math.004 [VECT_MATH:ADD[
# (0.0, 0.0, 0.0), 1.0]] -> Vector\n Texture Coordinate [TEX_COORD] -> Vector\n Vector Math.003 [VECT_MATH:SCALE[(0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]] -> V
# ector\n Vector Math.002 [VECT_MATH:SUBTRACT[(0.5, 0.5, 0.5), (0.0, 0.0, 0.0)]] -> Vector\n Noise Texture [TEX_NOISE scale=0.35] -> Vector\n Texture Co
# ordinate [TEX_COORD] -> Vector\n"}

# ==============================================================================================================
# [0016] 2026-09-23 19:34:43  blender  ok
# ==============================================================================================================
import bpy
nt=bpy.data.materials["M_VK_TerrainTown"].node_tree
n=nt.nodes["Vector Math.003"]; print(n.operation,[(i.name,i.enabled,(tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)) for i in n.inputs])
nz=nt.nodes["Noise Texture"]; print(nz.noise_dimensions,[(i.name,round(i.default_value,3) if not hasattr(i.default_value,'__len__') else None) for i in nz.inputs])
tc=nt.nodes["Texture Coordinate"]; print([ (l.from_socket.name,l.to_node.name) for o in tc.outputs for l in o.links])
# ---- result ----
# {"result":"Code executed successfully: SCALE [('Vector', True, (0.0, 0.0, 0.0)), ('Vector', False, (0.0, 0.0, 0.0)), ('Vector', False, (0.0, 0.0, 0.0)
# ), ('Scale', True, 1.600000023841858)]\n3D [('Vector', None), ('W', 0.0), ('Scale', 0.35), ('Detail', 2.0), ('Roughness', 0.5), ('Lacunarity', 2.0), (
# 'Offset', 0.0), ('Gain', 1.0), ('Distortion', 0.0)]\n[('Object', 'Vector Math'), ('Object', 'Vector Math.001'), ('Object', 'Noise Texture'), ('Object'
# , 'Vector Math.004'), ('Object', 'Mapping.001'), ('Object', 'Separate XYZ.001'), ('Object', 'Separate XYZ.003'), ('Object', 'Vector Math.005'), ('Obje
# ct', 'Vector Math.006')]\n"}

# ==============================================================================================================
# [0017] 2026-09-23 19:35:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_06_construction_pad", (1655,34,38), (1655,64,1.5), lens=30, res=(1400,800), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_06_construction_pad.png\n"}

# ==============================================================================================================
# [0018] 2026-09-23 19:35:57  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
X0,X1,Y0,Y1=1500,1716,0,168
over=[]
for o in c.all_objects:
    if o.type!="MESH" or not o.name.startswith("SM_VK_Tree_"): continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    ov=max(X0-min(xs),max(xs)-X1,Y0-min(ys),max(ys)-Y1)
    if ov>1.0: over.append((round(ov,2),o.name,round(o.location.x,1),round(o.location.y,1),round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1)))
over.sort(reverse=True)
print(len(over))
for r in over[:8]: print(r)
for n in ("SM_VK_Tree_Willow_inst.001","SM_VK_Tree_Willow_inst.003"):
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    print(n,[round(f(v.x for v in bb),1) for f in (min,max)],[round(f(v.y for v in bb),1) for f in (min,max)])
import collections
print(collections.Counter(r[1].split("_inst")[0] for r in over))
# ---- result ----
# {"result":"Code executed successfully: 118\n(6.59, 'SM_VK_Tree_Pine_B_inst.248', 1513.5, 167.3, 1506.3, 1521.1, 159.9, 174.6)\n(6.55, 'SM_VK_Tree_Pine
# _B_inst.273', 1706.2, 167.6, 1699.4, 1713.4, 160.6, 174.5)\n(6.31, 'SM_VK_Tree_Pine_B_inst.265', 1653.3, 167.2, 1646.4, 1660.6, 160.0, 174.3)\n(6.24, 
# 'SM_VK_Tree_Pine_B_inst.268', 1666.1, 166.8, 1658.6, 1673.2, 159.6, 174.2)\n(5.93, 'SM_VK_Tree_Pine_B_inst.102', 1501.2, 137.1, 1494.1, 1508.2, 130.0,
#  143.8)\n(5.86, 'SM_VK_Tree_Pine_B_inst.262', 1624.2, 167.6, 1618.0, 1630.1, 161.5, 173.9)\n(5.44, 'SM_VK_Tree_Pine_B_inst.263', 1627.1, 167.0, 1620.7
# , 1634.0, 160.7, 173.4)\n(5.39, 'SM_VK_Tree_Pine_B_inst.188', 1501.2, 157.3, 1494.6, 1508.1, 150.8, 163.9)\nSM_VK_Tree_Willow_inst.001 [1709.2, 1720.7
# ] [16.6, 28.1]\nSM_VK_Tree_Willow_inst.003 [1498.6, 1510.1] [28.5, 40.0]\nCounter({'SM_VK_Tree_Pine_B': 50, 'SM_VK_Tree_Pine_A': 36, 'SM_VK_Tree_Pine_

# ==============================================================================================================
# [0019] 2026-09-23 19:37:00  blender  ok
# ==============================================================================================================
import bpy, numpy as np
c=bpy.data.collections["VK_ValleyTown"]
X0,X1,Y0,Y1=1500,1716,0,168
cache={}
def ext(o):
    me=o.data
    if me.name not in cache:
        co=np.empty(len(me.vertices)*3); me.vertices.foreach_get("co",co); cache[me.name]=co.reshape(-1,3)
    co=cache[me.name]
    M=np.array(o.matrix_world)
    w=co@M[:3,:3].T+M[:3,3]
    return w[:,0].min(),w[:,0].max(),w[:,1].min(),w[:,1].max()
over=[]
for o in c.all_objects:
    if o.type!="MESH" or not o.name.startswith("SM_VK_Tree_"): continue
    x0,x1,y0,y1=ext(o)
    ov=max(X0-x0,x1-X1,Y0-y0,y1-Y1)
    if ov>1.0: over.append((round(ov,2),o.name))
over.sort(reverse=True)
print(len(over), over[:6])
for n in ("SM_VK_Tree_Willow_inst.001","SM_VK_Tree_Willow_inst.003","SM_VK_Tree_Pine_B_inst.248"):
    print(n,[round(v,1) for v in ext(bpy.data.objects[n])])
# radius of mesh
for b in ("SM_VK_Tree_Willow","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_A"):
    me=bpy.data.objects[b].data; co=np.empty(len(me.vertices)*3); me.vertices.foreach_get("co",co); co=co.reshape(-1,3)
    print(b, round(float(np.hypot(co[:,0],co[:,1]).max()),2), len(me.vertices))
# ---- result ----
# {"result":"Code executed successfully: 87 [(4.77, 'SM_VK_Tree_Pine_B_inst.273'), (4.68, 'SM_VK_Tree_Pine_B_inst.248'), (4.57, 'SM_VK_Tree_Pine_B_inst.
# 265'), (4.49, 'SM_VK_Tree_Pine_B_inst.263'), (4.44, 'SM_VK_Tree_Pine_B_inst.247'), (4.1, 'SM_VK_Tree_Pine_B_inst.262')]\nSM_VK_Tree_Willow_inst.001 [1
# 710.6, 1719.4, 17.8, 26.8]\nSM_VK_Tree_Willow_inst.003 [1499.8, 1508.8, 29.8, 38.6]\nSM_VK_Tree_Pine_B_inst.248 [1508.5, 1518.4, 162.1, 172.7]\nSM_VK_
# Tree_Willow 4.59 4288\nSM_VK_Tree_Pine_B 4.99 10085\nSM_VK_Tree_Pine_A 4.42 8849\n"}

# ==============================================================================================================
# [0020] 2026-09-23 19:37:31  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_07_willow_east_edge", (1690,5,28), (1712,24,0), lens=35, res=(1200,700), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_07_willow_east_edge.png\n"}

# ==============================================================================================================
# [0021] 2026-09-23 19:38:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_08_lake_colony", (1690,-2,42), (1690,38,0), lens=30, res=(1400,800), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_08_lake_colony.png\n"}

# ==============================================================================================================
# [0022] 2026-09-23 19:39:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
R=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_art"
p=shot("va_09_hamlet_thatch", (1540,-22,32), (1540,10,1.5), lens=32, res=(1400,800), outdir=R)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_art\\va_09_hamlet_thatch.png\n"}
