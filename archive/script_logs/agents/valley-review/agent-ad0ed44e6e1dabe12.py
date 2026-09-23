# valley-review / agent-ad0ed44e6e1dabe12.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 16:57:38  blender  ok
# ==============================================================================================================
import bpy
t = bpy.data.texts["vk_render"].as_string()
print(t[:3000])
sc = bpy.context.scene
print(sc.name, sc.render.engine)
print(len(bpy.data.collections['VK_ValleyTown'].all_objects))
# ---- result ----
# {"result":"Code executed successfully: import bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,len
# s=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is 
# None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.
# link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_e
# nd=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.render.

# ==============================================================================================================
# [0002] 2026-09-23 16:58:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
import time; t=time.time()
p=shot("review_art_00_overview",(1608,-95,150),(1608,84,0),lens=30,res=(1600,900),outdir=OUT)
print(p, time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_00_overview.png 3.608243942260742\n"}

# ==============================================================================================================
# [0003] 2026-09-23 16:58:33  blender  ok
# ==============================================================================================================
import bpy, collections
col=bpy.data.collections['VK_ValleyTown']
print([c.name for c in col.children_recursive][:80])
cnt=collections.Counter()
for o in col.all_objects:
    n=o.name.split('.')[0]
    import re
    n=re.sub(r'_\d+$','',n)
    cnt[n]+=1
print(len(cnt))
print(sorted(cnt.items(), key=lambda x:-x[1])[:120])
# ---- result ----
# {"result":"Code executed successfully: []\n339\n[('SM_VKT_LipGrass_inst', 1344), ('SM_VK_Tree_Pine_Young_inst', 342), ('SM_VK_Tree_Pine_B_inst', 335),
#  ('SM_VK_Tree_Pine_A_inst', 324), ('SM_VK_Wall_Timber_Window_inst', 135), ('SM_VK_Deco_Weeds_inst', 125), ('SM_VK_Bush_Round_inst', 121), ('SM_VK_Town
# Wall_Straight_inst', 119), ('SM_VK_Rock_Small_A_inst', 113), ('SM_VK_Plant_Fern_inst', 112), ('SM_VK_Wall_Stone_inst', 101), ('SM_VK_Corner_Timber_ins
# t', 88), ('SM_VK_Rock_Pebbles_inst', 87), ('SM_VK_Rock_Small_B_inst', 86), ('SM_VK_Rock_Boulder_A_inst', 86), ('SM_VK_Corner_Stone_inst', 83), ('SM_VK
# _Mushrooms_Brown_inst', 75), ('SM_VK_Wall_Stone_Window_inst', 68), ('SM_VK_Tree_Oak_A_inst', 63), ('SM_VK_Tree_Oak_B_inst', 60), ('SM_VK_Tree_Birch_in
# st', 52), ('SM_VK_Prop_FlowerBox_inst', 41), ('SM_VK_Plant_TallGrass_inst', 39), ('SM_VK_Plant_Wildflowers_inst', 39), ('SM_VK_Prop_FlowerBox_Daisy_in

# ==============================================================================================================
# [0004] 2026-09-23 16:58:46  blender  ok
# ==============================================================================================================
import bpy
col=bpy.data.collections['VK_ValleyTown']
keys=['MarketCross','Windmill','Chapel_Wall','Watermill','Barge','Lavoir','Smokehouse','Mine','Tower_House','Brewery','Blacksmith','Granary','Apiary','Pottery','Tannery','Dye','Fisher','Pier','Treadwheel','Gatehouse','Longhouse','Kiln','Stall','Pillory','Well']
res={}
for o in col.all_objects:
    for k in keys:
        if k.lower() in o.name.lower():
            res.setdefault(k,[]).append((o.name,tuple(round(v,1) for v in o.matrix_world.translation)))
for k,v in res.items(): print(k, v[:4])
# ---- result ----
# {"result":"Code executed successfully: Gatehouse [('SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0)), ('SM_VK_Gatehouse_Portcullis_inst', (1627.5, 72
# .6, 5.2)), ('SM_VK_Gatehouse_GateLeaf_inst', (1625.9, 73.8, 3.0)), ('SM_VK_Gatehouse_GateLeaf_inst.001', (1629.1, 73.8, 3.0))]\nPier [('SM_VK_Bridge_S
# tone_Pier_inst', (1626.0, 42.0, 0.0)), ('SM_VK_Mill_WheelPier_inst', (1579.5, 44.9, 0.0)), ('SM_VK_Pier_Deck_inst', (1693.5, 25.5, 0.0)), ('SM_VK_Pier
# _Deck_inst.001', (1693.5, 28.5, 0.0))]\nBarge [('SM_VK_Prop_Barge_inst', (1605.0, 46.2, -0.6))]\nLavoir [('SM_VK_Prop_LavoirBasin_inst', (1641.0, 49.5
# , 0.0))]\nKiln [('SM_VK_Prop_BottleKiln_inst', (1543.0, 63.1, 1.5)), ('SM_VK_Kiln_Oast_inst', (1680.4, 116.7, 3.0))]\nDye [('SM_VK_Prop_DyeVat_inst', 
# (1556.7, 57.9, 1.5)), ('SM_VK_Prop_DyeVat_inst.001', (1558.4, 58.2, 1.5)), ('SM_VK_Prop_DyeVat_inst.002', (1560.1, 57.9, 1.5)), ('SM_VK_Prop_DyeVat_in

# ==============================================================================================================
# [0005] 2026-09-23 16:59:01  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
def colony(name,tx,ty,tz,yaw=0,dist=40,pitch=50,lens=30):
    h=dist*math.sin(math.radians(pitch)); d=dist*math.cos(math.radians(pitch))
    a=math.radians(yaw)
    cx=tx-d*math.sin(a); cy=ty-d*math.cos(a)
    return shot(name,(cx,cy,tz+h),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OUT)
bpy.app.driver_namespace['colony']=colony
print(colony("review_art_01_plaza",1626,102,3))
print(colony("review_art_02_southwall_gate",1627,80,3))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_01_plaza.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\sc
# ratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review
# _art_02_southwall_gate.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 16:59:46  blender  ok
# ==============================================================================================================
import bpy
colony=bpy.app.driver_namespace['colony']
print(colony("review_art_03_hamlet",1540,15,1.5))
print(colony("review_art_04_watermill_river",1580,45,0.5))
print(colony("review_art_05_town_nw",1590,120,3))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_03_hamlet.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\revie
# w_art_04_watermill_river.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6
# -98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_05_town_nw.png\n"}

# ==============================================================================================================
# [0007] 2026-09-23 17:00:36  blender  ok
# ==============================================================================================================
import bpy
colony=bpy.app.driver_namespace['colony']
print(colony("review_art_06_outpost_barracks",1668,18,1.5))
print(colony("review_art_07_lake_fisher",1700,30,0.5))
print(colony("review_art_08_meadow_construction",1655,62,1.5))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_06_outpost_barracks.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# art\\review_art_07_lake_fisher.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a
# 4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_08_meadow_construction.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 17:01:20  blender  ok
# ==============================================================================================================
import bpy
colony=bpy.app.driver_namespace['colony']
print(colony("review_art_09_westbench_mine",1525,95,3))
print(colony("review_art_10_town_ne_chapel",1655,118,3))
print(colony("review_art_11_camp_sawpit",1600,15,1.5))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_09_westbench_mine.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ar
# t\\review_art_10_town_ne_chapel.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8
# a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_11_camp_sawpit.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 17:02:05  blender  ok
# ==============================================================================================================
import bpy
mats=set()
for c in ['VK_ValleyTown','VK_ValleyTerrain']:
    for o in bpy.data.collections[c].all_objects:
        if o.type=='MESH':
            for s in o.material_slots:
                if s.material: mats.add(s.material)
        elif o.instance_type=='COLLECTION' and o.instance_collection:
            for oo in o.instance_collection.all_objects:
                if oo.type=='MESH':
                    for s in oo.material_slots:
                        if s.material: mats.add(s.material)
print(len(mats))
for m in sorted(mats,key=lambda m:m.name):
    if not m.use_nodes: print(m.name,'nonodes'); continue
    b=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']
    imgs=[n.image.name+('%dx%d'%tuple(n.image.size) if n.image else '') for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    s=''
    if b:
        b=b[0]
        def v(nm):
            i=b.inputs.get(nm)
            if i is None: return None
            if i.is_linked: return 'L'
            dv=i.default_value
            try: return tuple(round(x,2) for x in dv)
            except: return round(dv,2)
        s='bc=%s r=%s m=%s spec=%s em=%s es=%s'%(v('Base Color'),v('Roughness'),v('Metallic'),v('Specular IOR Level'),v('Emission Color'),v('Emission Strength'))
    print(m.name, s, imgs[:3])
# ---- result ----
# {"result":"Code executed successfully: 77\nM_VKT_Stair bc=L r=L m=0.0 spec=0.25 em=(1.0, 1.0, 1.0, 1.0) es=0.0 ['T_VK_Ashlar_BC1024x1024', 'T_VK_Ashla
# r_H1024x1024', 'T_VK_Ashlar_R1024x1024']\nM_VKT_Water bc=L r=0.06 m=0.0 spec=0.6 em=(0.04, 0.16, 0.17, 1.0) es=0.35 []\nM_VK_Apple bc=L r=0.45 m=0.0 s
# pec=0.5 em=(1.0, 1.0, 1.0, 1.0) es=0.0 []\nM_VK_Ashlar bc=L r=L m=0.0 spec=0.3 em=(1.0, 1.0, 1.0, 1.0) es=0.0 ['T_VK_Ashlar_BC1024x1024', 'T_VK_Ashlar
# _N1024x1024', 'T_VK_Ashlar_R1024x1024']\nM_VK_BarkBirch bc=L r=L m=0.0 spec=0.2 em=(1.0, 1.0, 1.0, 1.0) es=0.0 ['T_VK_BarkBirch_BC1024x1024', 'T_VK_Ba
# rkBirch_N1024x1024', 'T_VK_BarkBirch_R1024x1024']\nM_VK_BarkMossy bc=L r=L m=0.0 spec=0.2 em=(1.0, 1.0, 1.0, 1.0) es=0.0 ['T_VK_BarkOak_BC1024x1024', 
# 'T_VK_BarkOak_N1024x1024', 'T_VK_BarkOak_R1024x1024']\nM_VK_BarkOak bc=L r=L m=0.0 spec=0.15 em=(1.0, 1.0, 1.0, 1.0) es=0.0 ['T_VK_BarkOak_BC1024x1024

# ==============================================================================================================
# [0010] 2026-09-23 17:02:19  blender  ok
# ==============================================================================================================
import bpy
def mats_of(prefix):
    out={}
    for o in bpy.data.collections['VK_ValleyTown'].all_objects:
        if o.name.startswith(prefix):
            src=[o] if o.type=='MESH' else (list(o.instance_collection.all_objects) if o.instance_type=='COLLECTION' and o.instance_collection else [])
            for oo in src:
                if oo.type=='MESH':
                    out[oo.name]=[s.material.name for s in oo.material_slots if s.material]
                    out[oo.name+'_dims']=tuple(round(v,2) for v in oo.dimensions)
            break
    return out
for p in ['SM_VK_Scaffold_Wall_inst','SM_VK_Tree_Willow_inst','SM_VK_Bush_Hydrangea_inst','SM_VK_Tree_Oak_A_inst','SM_VK_Tree_Pine_A_inst','SM_VK_BuildSite_Cell_inst']:
    print(p, mats_of(p))
o=bpy.data.objects['SM_VK_Scaffold_Wall_inst']
print(o.type,o.instance_type, o.data.name if o.data else None)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Scaffold_Wall_inst {'SM_VK_Scaffold_Wall_inst': ['M_VK_Stone', 'M_VK_Plaster', 'M_VK_Wood', 'M_VK_RoofRed
# ', 'M_VK_Window', 'M_VK_Iron', 'M_VK_FlowerPink', 'M_VK_FlowerYellow', 'M_VK_Leaf', 'M_VK_Glow', 'M_VK_Shutter_Teal', 'M_VK_Cloth_Red', 'M_VK_Cloth_Cr
# eam', 'M_VK_Apple', 'M_VK_Pumpkin', 'M_VK_Bread', 'M_VK_Hay', 'M_VK_Paper', 'M_VK_Water', 'M_VK_Bronze', 'M_VK_Stained', 'M_VK_Steel', 'M_VK_Thatch', 
# 'M_VK_Planks', 'M_VK_Ashlar', 'M_VK_Burlap', 'M_VK_Soil', 'M_VK_Void', 'M_VK_Rock', 'M_VK_Clay', 'M_VK_Clock', 'M_VK_Foliage', 'M_VK_Crops', 'M_VK_Bar
# kOak', 'M_VK_BarkBirch', 'M_VK_BarkPine', 'M_VK_Leaves', 'M_VK_Moss', 'M_VK_RockMossy', 'M_VK_BarkMossy', 'M_VK_EndGrain', 'M_VK_MushRed', 'M_VK_MushB
# rown', 'M_VK_MushStem', 'M_VK_MushGlow', 'M_VK_StoneBlock', 'M_VK_FieldStone', 'M_VK_Wattle', 'M_VK_Hide', 'M_VK_Pigskin', 'M_VK_Coal', 'M_VK_Net'], '

# ==============================================================================================================
# [0011] 2026-09-23 17:03:08  blender  ok
# ==============================================================================================================
import bpy, collections
for mn in ['SM_VK_Scaffold_Wall','SM_VK_Scaffold_Wall_Top']:
    me=bpy.data.meshes.get(mn)
    if not me: print('no',mn); continue
    o=bpy.data.objects['SM_VK_Scaffold_Wall_inst']
    c=collections.Counter(p.material_index for p in me.polygons)
    print(mn, [(me.materials[i].name if me.materials[i] else None,n) for i,n in c.items()])
# wood material color
m=bpy.data.materials['M_VK_Wood']
for n in m.node_tree.nodes: print(n.type,n.name, getattr(n,'image',None) and n.image.name)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Scaffold_Wall [('M_VK_BarkBirch', 46), ('M_VK_EndGrain', 4), ('M_VK_Burlap', 48), ('M_VK_Wood', 52), ('M_
# VK_Planks', 52)]\nSM_VK_Scaffold_Wall_Top [('M_VK_BarkBirch', 46), ('M_VK_EndGrain', 4), ('M_VK_Burlap', 48), ('M_VK_Wood', 52), ('M_VK_Planks', 52)]\
# nOUTPUT_MATERIAL Material Output None\nBSDF_PRINCIPLED Principled BSDF None\nUVMAP UV Map None\nTEX_IMAGE Image Texture T_VK_Wood_BC\nTEX_IMAGE Image 
# Texture.001 T_VK_Wood_N\nTEX_IMAGE Image Texture.002 T_VK_Wood_R\nVERTEX_COLOR Color Attribute None\nMIX Mix None\nMATH Math None\nNORMAL_MAP Normal M
# ap None\n"}

# ==============================================================================================================
# [0012] 2026-09-23 17:03:29  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
print(shot("review_art_12_eye_mainstreet",(1627.5,79,4.8),(1627,100,4.5),lens=26,res=(1600,900),outdir=OUT))
print(shot("review_art_13_eye_bridge_bank",(1612,33,1.8),(1626,44,2.0),lens=26,res=(1600,900),outdir=OUT))
print(shot("review_art_14_eye_gate_outside",(1627.5,55,3.4),(1627.5,75,5.0),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_12_eye_mainstreet.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ar
# t\\review_art_13_eye_bridge_bank.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f
# 8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_14_eye_gate_outside.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 17:04:24  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
wl=[tuple(round(v,1) for v in o.matrix_world.translation) for o in bpy.data.collections['VK_ValleyTown'].all_objects if 'Willow' in o.name]
print(wl)
print(shot("review_art_13b_eye_river_bridge",(1640,27,3.2),(1626,44,1.5),lens=24,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: [(1676.6, 27.3, 0.0), (1531.6, 32.3, 0.0), (1572.5, 30.9, 0.0), (1594.3, 31.5, 0.0), (1622.3, 30.8, 0.0), (1663
# .8, 31.6, 0.0), (1674.7, 31.8, 0.0), (1516.5, 34.7, 0.0), (1567.7, 33.3, 0.0), (1610.2, 35.4, 0.0), (1672.4, 34.4, 0.0), (1567.8, 49.3, 0.0), (1606.9,
#  49.6, 0.0), (1671.5, 49.9, 0.0), (1553.0, 51.7, 0.0), (1554.3, 52.3, 0.0), (1593.8, 53.5, 0.0), (1675.0, 56.0, 0.0)]\nC:\\Users\\danie\\AppData\\Roam
# ing\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revi
# ew\\art\\review_art_13b_eye_river_bridge.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 17:05:02  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials['M_VK_TerrainTown']
nt=m.node_tree
for n in nt.nodes:
    extra=''
    if n.type=='TEX_IMAGE': extra=(n.image.name if n.image else '')+' interp=%s'%n.interpolation
    if n.type=='MAPPING': extra=str([tuple(round(x,3) for x in n.inputs[k].default_value) for k in ('Location','Rotation','Scale')])
    if n.type in('TEX_NOISE','TEX_VORONOI','TEX_WAVE'): extra=str([(i.name,round(i.default_value,3) if isinstance(i.default_value,float) else None) for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and isinstance(i.default_value,float)])
    if n.type=='MATH' or n.type=='VECT_MATH': extra=n.operation+str([ (round(i.default_value,3) if isinstance(i.default_value,float) else tuple(round(x,3) for x in i.default_value)) for i in n.inputs if not i.is_linked])
    print(n.name,n.type,n.label,extra)
print('---links')
for l in nt.links: print(l.from_node.name,'.',l.from_socket.name,'->',l.to_node.name,'.',l.to_socket.name)
# ---- result ----
# {"result":"Code executed successfully: Material Output OUTPUT_MATERIAL \nPrincipled BSDF BSDF_PRINCIPLED \nTexture Coordinate TEX_COORD \nGeometry NEW
# _GEOMETRY \nSeparate XYZ SEPXYZ \nAttribute ATTRIBUTE \nSeparate Color SEPARATE_COLOR \nVector Math VECT_MATH SCALE[(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 
# 0.25]\nVector Math.001 VECT_MATH SCALE[(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.021]\nImage Texture TEX_IMAGE T_VK_TerrainMacro interp=Linear\nSeparate Col
# or.001 SEPARATE_COLOR \nMapping MAPPING CTL_MAP [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.005, 0.006, 1.0)]\nImage Texture.001 TEX_IMAGE T_VK_GroundCtl_To
# wn interp=Linear\nSeparate Color.002 SEPARATE_COLOR \nImage Texture.002 TEX_IMAGE T_VK_Grass_BC interp=Linear\nMapping.001 MAPPING [(0.0, 0.0, 0.0), (
# 0.0, 0.0, 0.646), (0.076, 0.076, 1.0)]\nImage Texture.003 TEX_IMAGE T_VK_Grass_BC interp=Linear\nMap Range MAP_RANGE \nMix MIX \nImage Texture.004 TEX

# ==============================================================================================================
# [0015] 2026-09-23 17:05:36  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials['M_VK_TerrainTown']
for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE': print(n.name,n.image.name,n.projection,n.projection_blend,n.extension)
for n in m.node_tree.nodes:
    if n.type=='MAP_RANGE': print(n.name,[(i.name,round(i.default_value,3)) for i in n.inputs if not i.is_linked and isinstance(getattr(i,'default_value',None),float)])
print(bpy.data.images['T_VK_GroundCtl_Town'].size, bpy.data.images['T_VK_GroundCtl_Town'].colorspace_settings.name)
# ---- result ----
# {"result":"Code executed successfully: Image Texture T_VK_TerrainMacro FLAT 0.0 REPEAT\nImage Texture.001 T_VK_GroundCtl_Town FLAT 0.0 EXTEND\nImage T
# exture.002 T_VK_Grass_BC FLAT 0.0 REPEAT\nImage Texture.003 T_VK_Grass_BC FLAT 0.0 REPEAT\nImage Texture.004 T_VK_Grass_H FLAT 0.0 REPEAT\nImage Textu
# re.005 T_VK_Sand_H FLAT 0.0 REPEAT\nImage Texture.006 T_VK_Sand_BC FLAT 0.0 REPEAT\nImage Texture.007 T_VK_Dirt_H FLAT 0.0 REPEAT\nImage Texture.008 T
# _VK_Dirt_BC FLAT 0.0 REPEAT\nImage Texture.009 T_VK_Cobble_H FLAT 0.0 REPEAT\nImage Texture.010 T_VK_Cobble_BC FLAT 0.0 REPEAT\nImage Texture.011 T_VK
# _Cliff_BC BOX 0.20000000298023224 REPEAT\nImage Texture.012 T_VK_Cliff_H BOX 0.20000000298023224 REPEAT\nImage Texture.013 T_VK_Moss_BC FLAT 0.0 REPEA
# T\nImage Texture.014 T_VK_Moss_H FLAT 0.0 REPEAT\nMap Range [('From Min', 0.3), ('From Max', 0.7), ('To Min', 0.0), ('To Max', 1.0), ('Steps', 4.0)]\n

# ==============================================================================================================
# [0016] 2026-09-23 17:06:15  blender  ok
# ==============================================================================================================
import bpy
tc=bpy.data.collections['VK_ValleyTerrain']
obs=list(tc.all_objects)
print(len(obs), [o.name for o in obs][:10])
import collections
print(collections.Counter(o.type for o in obs))
tot=sum(len(o.data.polygons) for o in obs if o.type=='MESH')
print(tot)
# ---- result ----
# {"result":"Code executed successfully: 30 ['VKV_Chunk_0_0', 'VKV_Water_0_0', 'VKV_Chunk_1_0', 'VKV_Water_1_0', 'VKV_Chunk_2_0', 'VKV_Water_2_0', 'VKV_
# Chunk_3_0', 'VKV_Water_3_0', 'VKV_Chunk_4_0', 'VKV_Water_4_0']\nCounter({'MESH': 30})\n261639\n"}

# ==============================================================================================================
# [0017] 2026-09-23 17:06:42  blender  ok
# ==============================================================================================================
import bpy, bmesh, time
from mathutils.bvhtree import BVHTree
from mathutils import Vector
t=time.time()
verts=[];polys=[]
for o in bpy.data.collections['VK_ValleyTerrain'].all_objects:
    if not o.name.startswith('VKV_Chunk'): continue
    mw=o.matrix_world; me=o.data; off=len(verts)
    verts.extend([mw@v.co for v in me.vertices])
    polys.extend([[off+i for i in p.vertices] for p in me.polygons])
bvh=BVHTree.FromPolygons(verts,polys)
bpy.app.driver_namespace['vk_terrain_bvh']=bvh
print(len(verts),len(polys),time.time()-t)
def ground(x,y):
    h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return h[0].z if h[0] else None
print(ground(1626,100), ground(1540,15), ground(1626,42))
# ---- result ----
# {"result":"Code executed successfully: 313035 261196 0.5670011043548584\n3.0 1.5 -1.4999961853027344\n"}

# ==============================================================================================================
# [0018] 2026-09-23 17:06:58  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils import Vector
bvh=bpy.app.driver_namespace['vk_terrain_bvh']
def ground(x,y):
    h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return h[0].z if h[0] else None
float_=[];sunk=[]
skip=('LipGrass',)
for o in bpy.data.collections['VK_ValleyTown'].all_objects:
    if any(s in o.name for s in skip) or o.type!='MESH': continue
    if o.parent: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    zmin=min(v.z for v in bb)
    cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
    # sample ground at center and corners inset
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    pts=[(cx,cy)]
    gs=[ground(px,py) for px,py in pts]
    gs=[g for g in gs if g is not None]
    if not gs: continue
    g=max(gs)
    d=zmin-g
    if d>0.12: float_.append((round(d,2),o.name,round(cx,1),round(cy,1),round(zmin,2),round(g,2)))
    elif d<-0.8 and 'Tree' not in o.name: sunk.append((round(d,2),o.name,round(cx,1),round(cy,1),round(zmin,2),round(g,2)))
float_.sort(reverse=True); sunk.sort()
print('FLOAT',len(float_)); 
for f in float_[:45]: print(f)
print('SUNK',len(sunk))
for s in sunk[:30]: print(s)
# ---- result ----
# {"result":"Code executed successfully: FLOAT 796\n(13.67, 'SM_VK_Banner_Roof_inst', 1578.9, 99.0, 16.67, 3.0)\n(13.59, 'SM_VK_Emblem_Ridge_Tankard_ins
# t', 1596.0, 77.0, 16.59, 3.0)\n(11.89, 'SM_VK_Roof_Bellcote_inst', 1602.0, 129.0, 14.89, 3.0)\n(11.16, 'SM_VK_Turret_Cap_inst.001', 1607.4, 77.4, 14.1
# 6, 3.0)\n(11.16, 'SM_VK_Turret_Cap_inst', 1574.4, 77.4, 14.16, 3.0)\n(11.15, 'SM_VK_Roof_Pyramid_6_inst', 1578.0, 99.0, 14.15, 3.0)\n(10.82, 'SM_VK_Ro
# of_Mid_inst.041', 1651.5, 81.0, 13.82, 3.0)\n(10.82, 'SM_VK_Roof_Gable_Stepped_inst.004', 1648.3, 81.0, 13.82, 3.0)\n(10.82, 'SM_VK_Roof_Gable_Flush_i
# nst.002', 1654.7, 81.0, 13.82, 3.0)\n(10.79, 'SM_VK_Emblem_Ridge_Key_inst', 1582.9, 114.0, 13.79, 3.0)\n(10.77, 'SM_VK_Parapet_Crenel_inst.007', 1575.
# 2, 97.5, 13.77, 3.0)\n(10.77, 'SM_VK_Parapet_Crenel_inst.006', 1575.2, 100.5, 13.77, 3.0)\n(10.77, 'SM_VK_Parapet_Crenel_inst.005', 1576.5, 101.8, 13.

# ==============================================================================================================
# [0019] 2026-09-23 17:07:19  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils import Vector
bvh=bpy.app.driver_namespace['vk_terrain_bvh']
def ground(x,y):
    h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return h[0].z if h[0] else None
keep=('Prop_','Tree_','Bush_','Rock_','Plant_','Deco_Weeds','Mushrooms','Animal_','Crop_','MarketStall','LowWall','Prop_Fence','Palisade_Straight','Stockpile','Foundation','BuildSite','Well','Porch','LeanTo')
excl=('FlowerBox','Planter','Lantern','Banner','Sign','Ivy','Hanging','Shelf','Bracket','Emblem','Window')
res=[]
for o in bpy.data.collections['VK_ValleyTown'].all_objects:
    n=o.name
    if not any(k in n for k in keep) or any(e in n for e in excl): continue
    if o.parent: continue
    oz=o.matrix_world.translation.z
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zmin=min(v.z for v in bb)
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    hx=(max(xs)-min(xs))*0.3; hy=(max(ys)-min(ys))*0.3
    if 'Tree' in n or 'Bush' in n: hx=hy=0.15
    samp=[(cx,cy),(cx-hx,cy-hy),(cx+hx,cy-hy),(cx-hx,cy+hy),(cx+hx,cy+hy)]
    gs=[ground(*p) for p in samp]; gs=[g for g in gs if g is not None]
    if not gs: continue
    base=zmin if not ('Tree' in n or 'Bush' in n) else oz
    gmin=min(gs); gmax=max(gs)
    # floating: base above highest ground sample
    if base-gmax>0.25: res.append(('FLOAT',round(base-gmax,2),n,round(cx,1),round(cy,1),round(base,2),[round(g,2) for g in gs]))
    elif gmin-base>0.6 and 'Tree' not in n and 'Rock' not in n: res.append(('SUNK',round(gmin-base,2),n,round(cx,1),round(cy,1),round(base,2),[round(g,2) for g in gs]))
res.sort(key=lambda r:-r[1])
print(len(res))
for r in res[:60]: print(r)
# ---- result ----
# {"result":"Code executed successfully: 83\n('FLOAT', 4.53, 'SM_VK_Prop_Bunting_6_inst', 1587.0, 121.5, 7.53, [3.0, 3.0, 3.0, 3.0, 3.0])\n('FLOAT', 4.5
# 3, 'SM_VK_Prop_Bunting_6_inst.001', 1594.5, 121.5, 7.53, [3.0, 3.0, 3.0, 3.0, 3.0])\n('FLOAT', 3.75, 'SM_VK_Prop_Bunting_9_inst', 1575.0, 121.5, 6.75,
#  [3.0, 3.0, 3.0, 3.0, 3.0])\n('FLOAT', 3.53, 'SM_VK_Prop_HoistBeam_inst', 1579.5, 76.9, 6.53, [3.0, 3.0, 3.0, 3.0, 3.0])\n('FLOAT', 2.58, 'SM_VK_Prop_
# Festoon_inst.002', 1659.0, 101.9, 5.58, [3.0, 3.0, 3.0, 3.0, 3.0])\n('FLOAT', 1.86, 'SM_VK_Prop_Bunting_6_inst.002', 1659.0, 95.4, 4.86, [3.0, 3.0, 3.
# 0, 3.0, 3.0])\n('FLOAT', 1.54, 'SM_VK_Prop_Creels_inst', 1693.9, 31.8, 0.04, [-1.5, -1.5, -1.5, -1.5, -1.5])\n('SUNK', 1.2, 'SM_VK_Prop_SawPit_inst', 
# 1611.0, 8.7, 0.3, [1.5, 1.5, 1.5, 1.5, 1.5])\n('FLOAT', 0.95, 'SM_VK_Prop_ShopGoods_Tools_inst', 1576.5, 77.5, 3.95, [3.0, 3.0, 3.0, 3.0, 3.0])\n('FLO

# ==============================================================================================================
# [0020] 2026-09-23 17:07:40  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
col=bpy.data.collections['VK_ValleyTown']
def bb(o):
    c=[o.matrix_world@Vector(v) for v in o.bound_box]
    return (min(v.x for v in c),max(v.x for v in c),min(v.y for v in c),max(v.y for v in c),min(v.z for v in c),max(v.z for v in c))
trees=[o for o in col.all_objects if ('Tree_' in o.name) and not o.parent]
struct=[o for o in col.all_objects if not o.parent and any(k in o.name for k in ('Roof','Wall_','Corner_','Tent','Stall','Chapel','Gatehouse','TownWall','Windmill','LeanTo','Porch','Prop_Wagon','Prop_Well'))]
print(len(trees),len(struct))
# spatial hash
import collections
grid=collections.defaultdict(list)
sb={}
for s in struct:
    b=bb(s); sb[s.name]=b
    for gx in range(int(b[0]//6),int(b[1]//6)+1):
        for gy in range(int(b[2]//6),int(b[3]//6)+1):
            grid[(gx,gy)].append(s.name)
hits=[]
for t in trees:
    tl=t.matrix_world.translation
    b=bb(t)
    # canopy as inner 60% footprint
    cx=(b[0]+b[1])/2; cy=(b[2]+b[3])/2; rx=(b[1]-b[0])*0.3; ry=(b[3]-b[2])*0.3
    cz0=b[4]+(b[5]-b[4])*0.3
    cand=set()
    for gx in range(int((cx-rx)//6),int((cx+rx)//6)+1):
        for gy in range(int((cy-ry)//6),int((cy+ry)//6)+1):
            cand.update(grid[(gx,gy)])
    ov=[]
    for n in cand:
        s=sb[n]
        ox=min(cx+rx,s[1])-max(cx-rx,s[0]); oy=min(cy+ry,s[3])-max(cy-ry,s[2])
        if ox>0.3 and oy>0.3 and s[5]>cz0 and s[4]<b[5]:
            ov.append((n,round(ox*oy,1)))
    if ov:
        ov.sort(key=lambda x:-x[1])
        hits.append((t.name,round(tl.x,1),round(tl.y,1),round(tl.z,1),round(b[1]-b[0],1),ov[:3]))
print(len(hits))
for h in hits[:50]: print(h)
# ---- result ----
# {"result":"Code executed successfully: 1241 1356\n47\n('SM_VK_Tree_Oak_B_inst.015', 1595.2, 4.9, 1.5, 10.0, [('SM_VK_Tent_Bell_inst', 1.9)])\n('SM_VK_
# Tree_Oak_A_inst.017', 1602.8, 6.9, 1.5, 12.3, [('SM_VK_Tent_Bell_inst', 6.8)])\n('SM_VK_Tree_Apple_inst.006', 1586.6, 16.1, 1.5, 6.9, [('SM_VK_Tent_A_
# inst.001', 0.1)])\n('SM_VK_Tree_Oak_B_inst.023', 1601.3, 74.4, 3.0, 9.3, [('SM_VK_TownWall_Straight_inst.020', 9.4), ('SM_VK_TownWall_Straight_inst.02
# 2', 7.5), ('SM_VK_Roof_Gable_Hoist_inst', 2.6)])\n('SM_VK_Tree_Apple_inst.009', 1619.4, 74.0, 3.0, 7.0, [('SM_VK_TownWall_Straight_inst.032', 7.7), ('
# SM_VK_TownWall_Straight_inst.034', 5.0)])\n('SM_VK_Tree_Birch_inst.014', 1655.0, 73.4, 3.0, 6.6, [('SM_VK_TownWall_Straight_inst.053', 6.7), ('SM_VK_T
# ownWall_Straight_inst.055', 3.0), ('SM_VK_TownWall_Tower_Round_inst.004', 2.5)])\n('SM_VK_Tree_Birch_inst.015', 1659.5, 73.3, 3.0, 7.9, [('SM_VK_TownW

# ==============================================================================================================
# [0021] 2026-09-23 17:08:19  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
col=bpy.data.collections['VK_ValleyTown']
def bb(o):
    c=[o.matrix_world@Vector(v) for v in o.bound_box]
    return (min(v.x for v in c),max(v.x for v in c),min(v.y for v in c),max(v.y for v in c),min(v.z for v in c),max(v.z for v in c))
roofs=[o for o in col.all_objects if not o.parent and ('Roof' in o.name) and 'Emblem' not in o.name and 'Banner' not in o.name]
print(len(roofs))
B={o.name:bb(o) for o in roofs}
names=list(B)
res=[]
for i in range(len(names)):
    a=B[names[i]]
    for j in range(i+1,len(names)):
        b=B[names[j]]
        ox=min(a[1],b[1])-max(a[0],b[0]); oy=min(a[3],b[3])-max(a[2],b[2]); oz=min(a[5],b[5])-max(a[4],b[4])
        if ox>0.5 and oy>0.5 and oz>0.5:
            va=(a[1]-a[0])*(a[3]-a[2])*(a[5]-a[4]); vb=(b[1]-b[0])*(b[3]-b[2])*(b[5]-b[4])
            f=ox*oy*oz/min(va,vb)
            if f>0.35: res.append((round(f,2),names[i],names[j],round((max(a[0],b[0])+min(a[1],b[1]))/2,1),round((max(a[2],b[2])+min(a[3],b[3]))/2,1),round(a[4],1),round(b[4],1)))
res.sort(reverse=True)
print(len(res))
for r in res[:40]: print(r)
# ---- result ----
# {"result":"Code executed successfully: 128\n13\n(1.0, 'SM_VK_Roof_Mid_inst.047', 'SM_VK_Roof_Dormer_inst.014', 1639.5, 109.2, 8.2, 9.8)\n(1.0, 'SM_VK_
# Roof_Mid_inst.035', 'SM_VK_Roof_Dormer_inst.013', 1684.8, 7.5, 6.7, 8.3)\n(1.0, 'SM_VK_Roof_Gable_inst.088', 'SM_VK_Roof_Dormer_inst.015', 1642.5, 109
# .2, 8.1, 9.8)\n(1.0, 'SM_VK_Roof_Gable_inst.083', 'SM_VK_Roof_Vent_inst.001', 1600.5, 114.0, 5.3, 9.3)\n(1.0, 'SM_VK_RoofS_Single_inst', 'SM_VK_Roof_V
# ent_inst', 1657.5, 49.5, 2.5, 4.4)\n(0.74, 'SM_VK_Roof_Hip_inst.011', 'SM_VK_Roof_Cone_R2_inst.001', 1630.7, 72.4, 11.3, 11.8)\n(0.74, 'SM_VK_Roof_Hip
# _inst.010', 'SM_VK_Roof_Cone_R2_inst', 1624.3, 72.4, 11.3, 11.8)\n(0.46, 'SM_VK_RoofThatch_Mid_inst.012', 'SM_VK_RoofThatch_Vent_inst.005', 1509.0, 64
# .0, 3.8, 8.1)\n(0.46, 'SM_VK_RoofThatch_Mid_inst.011', 'SM_VK_RoofThatch_Vent_inst.001', 1519.5, 6.0, 3.2, 7.5)\n(0.46, 'SM_VK_RoofThatch_Mid_inst.009

# ==============================================================================================================
# [0022] 2026-09-23 17:08:57  blender  ok
# ==============================================================================================================
import bpy, collections
col=bpy.data.collections['VK_ValleyTown']
cnt=collections.Counter()
pos=collections.defaultdict(list)
for o in col.all_objects:
    if o.parent or o.type!='MESH': continue
    if not ('Roof' in o.name): continue
    me=o.data
    ms=collections.Counter(me.materials[p.material_index].name if me.materials[p.material_index] else None for p in me.polygons)
    # material override via object slots?
    slots=[s.link for s in o.material_slots]
    top=ms.most_common(1)[0][0]
    if 'OBJECT' in slots:
        top='OBJ:'+','.join(s.material.name for s in o.material_slots if s.link=='OBJECT' and s.material)
    cnt[top]+=1
    pos[top].append((round(o.location.x),round(o.location.y)))
print(cnt)
for k,v in pos.items(): print(k, v[:40])
# ---- result ----
# {"result":"Code executed successfully: Counter({'M_VK_Wood': 46, 'M_VK_Thatch': 30, 'M_VK_Roof_Slate': 17, 'M_VK_RoofRed': 17, 'M_VK_Roof_Blue': 6, 'M
# _VK_Roof_Shingle': 4, 'M_VK_Ashlar': 4, 'M_VK_Bronze': 3, 'M_VK_Roof_Green': 3})\nM_VK_Roof_Slate [(1624, 75), (1628, 75), (1630, 75), (1683, 4), (168
# 3, 8), (1683, 10), (1576, 81), (1582, 81), (1578, 99), (1586, 129), (1588, 129), (1592, 129), (1654, 81), (1652, 81), (1648, 81), (1636, 111), (1640, 
# 111)]\nM_VK_Wood [(1624, 72), (1630, 72), (1581, 56), (1581, 50), (1642, 50), (1640, 50), (1658, 50), (1658, 50), (1690, 20), (1694, 20), (1683, 2), (
# 1683, 8), (1664, 66), (1666, 66), (1670, 66), (1504, 78), (1508, 78), (1516, 81), (1520, 81), (1534, 76), (1582, 78), (1580, 81), (1594, 78), (1596, 8
# 6), (1596, 80), (1611, 81), (1616, 81), (1611, 86), (1580, 129), (1588, 114), (1586, 114), (1604, 114), (1600, 114), (1600, 114), (1660, 84), (1670, 1

# ==============================================================================================================
# [0023] 2026-09-23 17:09:41  blender  ok
# ==============================================================================================================
import bpy, numpy as np, colorsys
names=['T_VK_Grass_BC','T_VK_Sand_BC','T_VK_Dirt_BC','T_VK_Cobble_BC','T_VK_RoofRed_BC','T_VK_RoofBlue_BC','T_VK_RoofGreen_BC','T_VK_RoofSlate_BC','T_VK_Thatch_BC','T_VK_Leaves_BCA','T_VK_Foliage_BCA','T_VK_Water_BC','T_VK_TerrainMacro','T_VK_Cliff_BC','T_VK_Plaster_BC','T_VK_Stone_BC']
for n in names:
    im=bpy.data.images.get(n)
    if not im: print('missing',n); continue
    a=np.array(im.pixels[:],dtype=np.float32).reshape(-1,im.channels)
    if im.channels==4 and n.endswith('BCA'):
        a=a[a[:,3]>0.5]
    m=a[:,:3].mean(0)
    # if colorspace is sRGB the pixels are linear floats? pixels in bpy are linear for sRGB images? they are stored as-is (sRGB values)
    h,s,v=colorsys.rgb_to_hsv(*m)
    sd=a[:,:3].std(0).mean()
    print(n, im.colorspace_settings.name, 'mean', np.round(m,3), 'hsv', round(h*360),round(s,2),round(v,2),'std',round(float(sd),3))
# ---- result ----
# {"result":"Code executed successfully: T_VK_Grass_BC sRGB mean [0.366 0.529 0.161] hsv 87 0.7 0.53 std 0.069\nT_VK_Sand_BC sRGB mean [0.741 0.66 0.493
# ] hsv 40 0.33 0.74 std 0.038\nT_VK_Dirt_BC sRGB mean [0.444 0.335 0.221] hsv 31 0.5 0.44 std 0.067\nT_VK_Cobble_BC sRGB mean [0.482 0.465 0.411] hsv 4
# 5 0.15 0.48 std 0.186\nT_VK_RoofRed_BC sRGB mean [0.582 0.23 0.131] hsv 13 0.77 0.58 std 0.084\nT_VK_RoofBlue_BC sRGB mean [0.208 0.296 0.465] hsv 219
#  0.55 0.46 std 0.083\nT_VK_RoofGreen_BC sRGB mean [0.235 0.298 0.238] hsv 123 0.21 0.3 std 0.064\nT_VK_RoofSlate_BC sRGB mean [0.238 0.261 0.298] hsv 
# 217 0.2 0.3 std 0.068\nT_VK_Thatch_BC sRGB mean [0.497 0.393 0.214] hsv 38 0.57 0.5 std 0.107\nT_VK_Leaves_BCA sRGB mean [0.423 0.44 0.21 ] hsv 64 0.5
# 2 0.44 std 0.214\nT_VK_Foliage_BCA sRGB mean [0.323 0.371 0.173] hsv 75 0.53 0.37 std 0.226\nT_VK_Water_BC sRGB mean [0.09 0.243 0.279] hsv 191 0.68 0

# ==============================================================================================================
# [0024] 2026-09-23 17:10:11  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes['VillageKit']
vs=sc.view_settings
print(vs.view_transform, vs.look, vs.exposure, vs.gamma, sc.display_settings.display_device)
w=sc.world
print(w.name if w else None)
if w and w.use_nodes:
    for n in w.node_tree.nodes: 
        print(n.type,n.name,[(i.name, (tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3))) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked][:6])
for o in sc.objects:
    if o.type=='LIGHT': print(o.name,o.data.type,round(o.data.energy,2),tuple(round(c,2) for c in o.data.color),tuple(round(r,2) for r in o.rotation_euler), getattr(o.data,'angle',None))
e=sc.eevee
for a in ['use_gtao','gtao_distance','use_shadows','shadow_ray_count','use_raytracing','taa_render_samples','use_bloom','volumetric_end']:
    print(a,getattr(e,a,None))
# ---- result ----
# {"result":"Code executed successfully: AgX AgX - Medium High Contrast -0.20000000298023224 1.0 sRGB\nMC_World\nBACKGROUND Background [('Strength', 0.2
# 2), ('Weight', 0.0)]\nOUTPUT_WORLD World Output []\nTEX_SKY Sky Texture [('Vector', (0.0, 0.0, 0.0))]\nLIGHT_PATH Light Path []\nBACKGROUND Background
# .001 [('Strength', 1.0), ('Weight', 0.0)]\nTEX_COORD Texture Coordinate []\nVALTORGB Color Ramp []\nMIX_SHADER Mix Shader []\nSEPXYZ Separate XYZ []\n
# VK_Sun SUN 3.2 (1.0, 0.88, 0.72) (0.91, 0.1, -0.52) 0.04363323003053665\nuse_gtao True\ngtao_distance 0.20000000298023224\nuse_shadows False\nshadow_r
# ay_count 1\nuse_raytracing True\ntaa_render_samples 64\nuse_bloom None\nvolumetric_end 100.0\n"}

# ==============================================================================================================
# [0025] 2026-09-23 17:10:43  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
colony=bpy.app.driver_namespace['colony']
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
print(shot("review_art_15_eye_southwall_east",(1662,58,3.4),(1664,75,7),lens=24,res=(1600,900),outdir=OUT))
print(colony("review_art_16_northwall_forest",1625,140,4.5))
print(shot("review_art_17_eye_hamlet_hovels",(1546,-4,3.2),(1540,8,3.0),lens=24,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_15_eye_southwall_east.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review
# \\art\\review_art_16_northwall_forest.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc
# 2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_17_eye_hamlet_hovels.png\n"}

# ==============================================================================================================
# [0026] 2026-09-23 17:11:34  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
print(shot("review_art_18_eye_wall_trees_east",(1684,63,3.3),(1667,75,6.5),lens=26,res=(1600,900),outdir=OUT))
print(shot("review_art_19_eye_wall_tree_gate",(1612,63,2.8),(1619.5,75,5.5),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_18_eye_wall_trees_east.png\nC:\\Users\\danie\\AppData\\Roami
# ng\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revie
# w\\art\\review_art_19_eye_wall_tree_gate.png\n"}

# ==============================================================================================================
# [0027] 2026-09-23 17:12:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
from mathutils import Vector
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
print(shot("review_art_19b_eye_wall_tree_gate",(1609,70,3.4),(1619.5,75,5.5),lens=26,res=(1600,900),outdir=OUT))
col=bpy.data.collections['VK_ValleyTown']
for o in col.all_objects:
    if 'Tree_' in o.name and 1660<o.location.x<1690 and 55<o.location.y<76:
        print(o.name, tuple(round(v,1) for v in o.location), tuple(round(v,1) for v in o.dimensions))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_19b_eye_wall_tree_gate.png\nSM_VK_Tree_Willow_inst.018 (1675
# .0, 56.0, 0.0) (8.6, 8.8, 5.0)\nSM_VK_Tree_Oak_A_inst.020 (1682.2, 61.5, 1.5) (9.7, 10.4, 8.8)\nSM_VK_Tree_Birch_inst.016 (1670.2, 74.0, 3.0) (6.3, 5.
# 5, 9.5)\n"}

# ==============================================================================================================
# [0028] 2026-09-23 17:12:53  blender  ok
# ==============================================================================================================
import bpy, re, collections, math
col=bpy.data.collections['VK_ValleyTown']
groups=collections.defaultdict(list)
for o in col.all_objects:
    if o.parent or 'LipGrass' in o.name: continue
    base=re.sub(r'(\.\d+)$','',o.name)
    groups[base].append(o)
dups=[]
for base,obs in groups.items():
    if len(obs)<2: continue
    thr=1.5 if ('Tree' in base) else 0.4
    if 'Tree' not in base and not any(k in base for k in ('Prop_','Bush','Rock_Boulder','MarketStall','Animal')): continue
    pts=[(o.matrix_world.translation,o.name) for o in obs]
    for i in range(len(pts)):
        for j in range(i+1,len(pts)):
            d=(pts[i][0]-pts[j][0]).length
            if d<thr: dups.append((round(d,2),pts[i][1],pts[j][1],tuple(round(v,1) for v in pts[i][0])))
dups.sort()
print(len(dups))
for d in dups[:40]: print(d)
# also cross-type tree pairs very close
trees=[o for o in col.all_objects if 'Tree_' in o.name and not o.parent]
close=[]
for i in range(len(trees)):
    for j in range(i+1,len(trees)):
        a=trees[i].matrix_world.translation; b=trees[j].matrix_world.translation
        d=math.hypot(a.x-b.x,a.y-b.y)
        if d<1.6 and not ('Pine' in trees[i].name and 'Pine' in trees[j].name): close.append((round(d,2),trees[i].name,trees[j].name,(round(a.x,1),round(a.y,1),round(a.z,1))))
close.sort(); print(len(close))
for c in close[:30]: print(c)
# ---- result ----
# {"result":"Code executed successfully: 108\n(0.16, 'SM_VK_Tree_Pine_A_inst.345', 'SM_VK_Tree_Pine_A_inst.346', (1600.7, 162.8, 7.5))\n(0.18, 'SM_VK_Tr
# ee_Pine_A_inst.282', 'SM_VK_Tree_Pine_A_inst.283', (1595.3, 158.3, 7.5))\n(0.18, 'SM_VK_Tree_Pine_B_inst.258', 'SM_VK_Tree_Pine_B_inst.259', (1548.9, 
# 154.5, 6.0))\n(0.2, 'SM_VK_Tree_Pine_A_inst.285', 'SM_VK_Tree_Pine_A_inst.286', (1613.1, 158.6, 7.5))\n(0.23, 'SM_VK_Tree_Pine_Young_inst.406', 'SM_VK
# _Tree_Pine_Young_inst.407', (1680.4, 167.1, 7.5))\n(0.27, 'SM_VK_Tree_Pine_A_inst.311', 'SM_VK_Tree_Pine_A_inst.312', (1578.9, 160.6, 6.0))\n(0.38, 'S
# M_VK_Tree_Pine_Young_inst.157', 'SM_VK_Tree_Pine_Young_inst.158', (1512.9, 142.0, 6.0))\n(0.38, 'SM_VK_Tree_Pine_Young_inst.168', 'SM_VK_Tree_Pine_You
# ng_inst.169', (1665.7, 142.1, 6.0))\n(0.38, 'SM_VK_Tree_Pine_Young_inst.341', 'SM_VK_Tree_Pine_Young_inst.342', (1514.3, 163.4, 7.5))\n(0.39, 'SM_VK_T

# ==============================================================================================================
# [0029] 2026-09-23 17:13:23  blender  ok
# ==============================================================================================================
import bpy
colony=bpy.app.driver_namespace['colony']
print(colony("review_art_20_westridge_forest",1528,118,5))
print(colony("review_art_21_town_east_terrace",1675,95,3))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_20_westridge_forest.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# art\\review_art_21_town_east_terrace.png\n"}

# ==============================================================================================================
# [0030] 2026-09-23 17:14:37  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials['M_VKT_Water']
nt=m.node_tree
for n in nt.nodes:
    extra=''
    if n.type=='VALTORGB': extra=[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in n.color_ramp.elements]
    if n.type in ('TEX_NOISE','TEX_VORONOI','TEX_WAVE','MAPPING','MATH','MIX','RGB','ATTRIBUTE'): 
        extra=[(i.name, (round(i.default_value,3) if isinstance(i.default_value,float) else (tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else i.default_value))) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:8]
        if n.type=='ATTRIBUTE': extra=n.attribute_name
    print(n.name,n.type,extra)
for l in nt.links: print(l.from_node.name,'.',l.from_socket.name,'->',l.to_node.name,'.',l.to_socket.name)
b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
print([(i.name, i.default_value if isinstance(i.default_value,float) else None) for i in b.inputs if not i.is_linked and isinstance(getattr(i,'default_value',None),float)])
print(m.surface_render_method if hasattr(m,'surface_render_method') else m.blend_method)
# ---- result ----
# {"result":"Code executed successfully: Material Output OUTPUT_MATERIAL \nPrincipled BSDF BSDF_PRINCIPLED \nTexture Coordinate TEX_COORD \nNoise Textur
# e TEX_NOISE [('W', 0.0), ('Scale', 0.35), ('Detail', 3.0), ('Roughness', 0.5), ('Lacunarity', 2.0), ('Offset', 0.0), ('Gain', 1.0), ('Distortion', 0.0
# )]\nNoise Texture.001 TEX_NOISE [('W', 0.0), ('Scale', 1.6), ('Detail', 2.0), ('Roughness', 0.5), ('Lacunarity', 2.0), ('Offset', 0.0), ('Gain', 1.0),
#  ('Distortion', 0.0)]\nMath MATH [('Value', 0.5), ('Value', 0.5)]\nMath.001 MATH [('Value', 0.5)]\nMap Range MAP_RANGE \nMix MIX [('Factor', (0.5, 0.5
# , 0.5)), ('A', 0.0), ('B', 0.0), ('A', (0.0, 0.0, 0.0)), ('B', (0.0, 0.0, 0.0)), ('A', (0.05, 0.24, 0.27, 1.0)), ('B', (0.09, 0.36, 0.36, 1.0)), ('A',
#  (0.0, 0.0, 0.0))]\nBump BUMP \nTexture Coordinate . Object -> Noise Texture . Vector\nTexture Coordinate . Object -> Noise Texture.001 . Vector\nNois

# ==============================================================================================================
# [0031] 2026-09-23 17:15:15  blender  ok
# ==============================================================================================================
import bpy, math
col=bpy.data.collections['VK_ValleyTown']
for o in col.all_objects:
    if ('RoofThatch' in o.name) and not o.parent:
        print(o.name, tuple(round(v,1) for v in o.location), round(math.degrees(o.rotation_euler.z)), tuple(round(v,2) for v in o.scale))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_RoofThatch_Gable_Cruck_inst (1510.5, 6.0, 3.9) 180 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Mid_inst.009 (1513.5
# , 6.0, 3.9) 0 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Mid_inst.010 (1516.5, 6.0, 3.9) 0 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Mid_inst.011 (1519.5, 6.0, 3.9) 0 
# (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Gable_Planks_inst.010 (1522.5, 6.0, 3.9) 0 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Vent_inst (1513.5, 6.0, 8.1) 0 (1.0, 1.
# 0, 1.0)\nSM_VK_RoofThatch_Vent_inst.001 (1519.5, 6.0, 8.1) 0 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Gable_Cruck_inst.001 (1537.5, 6.0, 3.9) 180 (1.0, 1.0, 
# 1.0)\nSM_VK_RoofThatch_Gable_Cruck_inst.002 (1540.5, 6.0, 3.9) 0 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Vent_inst.002 (1537.5, 6.0, 8.1) 0 (1.0, 1.0, 1.0)\
# nSM_VK_RoofThatch_Hip_inst.006 (1552.5, 6.0, 3.9) 180 (1.0, 1.0, 1.0)\nSM_VK_RoofThatch_Gable_Cruck_inst.003 (1555.5, 6.0, 3.9) 0 (1.0, 1.0, 1.0)\nSM_

# ==============================================================================================================
# [0032] 2026-09-23 17:15:59  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
colony=bpy.app.driver_namespace['colony']
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
print(colony("review_art_22_lake_east_edge",1710,40,0,yaw=60))
print(shot("review_art_23_eye_plaza_skyline",(1633,93,4.7),(1612,122,7),lens=24,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_22_lake_east_edge.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ar
# t\\review_art_23_eye_plaza_skyline.png\n"}

# ==============================================================================================================
# [0033] 2026-09-23 17:17:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
print(shot("review_art_24_grass_tiling_south",(1650,-2,14),(1668,24,1.5),lens=35,res=(1600,900),outdir=OUT))
print(shot("review_art_25_eye_westbench_path",(1526,80,4.9),(1526,100,5.0),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_24_grass_tiling_south.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review
# \\art\\review_art_25_eye_westbench_path.png\n"}

# ==============================================================================================================
# [0034] 2026-09-23 17:18:12  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
res=[]
for o in bpy.data.collections['VK_ValleyTerrain'].all_objects:
    if not o.name.startswith('VKV_Chunk'): continue
    me=o.data
    idx=[i for i,m in enumerate(me.materials) if m and m.name=='M_VKT_Stair']
    if not idx: continue
    mw=o.matrix_world
    xs=[];ys=[];zs=[]
    for p in me.polygons:
        if p.material_index in idx:
            c=mw@p.center; xs.append(c.x); ys.append(c.y); zs.append(c.z)
    if xs:
        # cluster by rough position
        import collections
        cl=collections.defaultdict(list)
        for x,y,z in zip(xs,ys,zs): cl[(int((x-1500)//3),int(y//3))].append(z)
        res.append((o.name, sorted((k,round(min(v),1),round(max(v),1)) for k,v in cl.items())))
for r in res: print(r)
# ground control: which cells are dirt near i 6-11, j 26-33
im=bpy.data.images['T_VK_GroundCtl_Town']
w,h=im.size
px=im.pixels[:]
def ctl(i,j):
    k=(j*w+i)*4
    return tuple(round(px[k+c],2) for c in range(4))
for j in range(33,24,-1):
    print(j,[ ('D' if ctl(i,j)[0]>0.5 else ('C' if ctl(i,j)[1]>0.5 else '.')) for i in range(3,14)])
# ---- result ----
# {"result":"Code executed successfully: 33 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.', '.']\n32 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.
# ', '.']\n31 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.', '.']\n30 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.', '.']\n29 ['.', '.', '.', '.
# ', '.', '.', 'D', 'D', '.', '.', '.']\n28 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.', '.']\n27 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.
# ', '.']\n26 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.', '.']\n25 ['.', '.', '.', '.', '.', '.', 'D', 'D', '.', '.', '.']\n"}

# ==============================================================================================================
# [0035] 2026-09-23 17:18:27  blender  ok
# ==============================================================================================================
import bpy, collections
for o in bpy.data.collections['VK_ValleyTerrain'].all_objects:
    if o.name.startswith('VKV_Chunk'):
        print(o.name,[m.name if m else None for m in o.data.materials])
        break
bvh=bpy.app.driver_namespace['vk_terrain_bvh']
from mathutils import Vector
# probe heights across x at y 100..106 to find stair
for y in [101.0,102.0,103.0,104.0,105.0]:
    row=[]
    for x in [1519.5,1521,1522.5,1524,1525.5,1527,1528.5,1530,1531.5,1533]:
        h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
        row.append(round(h[0].z,2) if h[0] else None)
    print(y,row)
# ---- result ----
# {"result":"Code executed successfully: VKV_Chunk_0_0 ['M_VK_TerrainTown', 'M_VKT_Stair']\n101.0 [3.0, 3.0, 3.0, 3.0, 3.25, 3.0, 3.0, 3.0, 3.0, 3.0]\n1
# 02.0 [4.38, 4.38, 4.39, 4.38, 3.75, 4.38, 3.87, 4.05, 4.37, 4.41]\n103.0 [4.5, 4.5, 4.5, 4.5, 4.25, 4.5, 4.5, 4.5, 4.5, 5.37]\n104.0 [4.5, 4.5, 4.5, 4
# .5, 4.5, 4.5, 4.5, 4.5, 4.5, 5.93]\n105.0 [4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 5.92]\n"}

# ==============================================================================================================
# [0036] 2026-09-23 17:19:19  blender  ok
# ==============================================================================================================
import bpy, collections, math
from mathutils import Vector
col=bpy.data.collections['VK_ValleyTown']
bvh=bpy.app.driver_namespace['vk_terrain_bvh']
def ground(x,y):
    h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
    return h[0].z if h[0] else -99
walls=[]
for o in col.all_objects:
    if o.parent: continue
    n=o.name
    if (n.startswith('SM_VK_Wall_') or n.startswith('SM_VK_Corner_') or n.startswith('SM_VK_Chapel_Wall')) and 'Up' not in n.split('_inst')[0]:
        p=o.matrix_world.translation
        g=ground(p.x,p.y)
        if abs(p.z-round(p.z/1.5)*1.5)<0.05 and abs(p.z-g)<0.3:
            walls.append(o)
print(len(walls))
# union-find clusters
par=list(range(len(walls)))
def f(i):
    while par[i]!=i: par[i]=par[par[i]]; i=par[i]
    return i
P=[w.matrix_world.translation for w in walls]
for i in range(len(walls)):
    for j in range(i+1,len(walls)):
        if abs(P[i].x-P[j].x)<=3.3 and abs(P[i].y-P[j].y)<=3.3 and abs(P[i].z-P[j].z)<0.1: par[f(i)]=f(j)
cl=collections.defaultdict(list)
for i in range(len(walls)): cl[f(i)].append(i)
fps=[]
for k,v in cl.items():
    xs=[P[i].x for i in v]; ys=[P[i].y for i in v]
    fps.append((min(xs),max(xs),min(ys),max(ys),P[v[0]].z,len(v)))
print('buildings',len(fps))
bpy.app.driver_namespace['vk_fps']=fps
# props inside footprints
hits=[]
for o in col.all_objects:
    if o.parent: continue
    n=o.name
    if not any(k in n for k in ('Prop_','MarketStall','Tree_','Bush_','Rock_Boulder','Animal_','Tent','Stockpile')): continue
    p=o.matrix_world.translation
    for fp in fps:
        if fp[0]+0.6<p.x<fp[1]-0.6 and fp[2]+0.6<p.y<fp[3]-0.6 and abs(p.z-fp[4])<1.0 and fp[5]>=4:
            hits.append((n,round(p.x,1),round(p.y,1),round(p.z,1),[round(v,1) for v in fp[:5]]))
print(len(hits))
for h in hits[:60]: print(h)
# ---- result ----
# {"result":"Code executed successfully: 512\nbuildings 29\n25\n('SM_VK_Prop_LavoirBasin_inst', 1641.0, 49.5, 0.0, [1638.0, 1644.0, 48.0, 51.0, 0.0])\n(
# 'SM_VK_Prop_FlowerBox_inst.111', 1615.5, 84.6, 3.8, [1608.0, 1617.0, 78.0, 87.0, 3.0])\n('SM_VK_Prop_FlowerBox_inst.112', 1614.6, 85.5, 3.8, [1608.0, 
# 1617.0, 78.0, 87.0, 3.0])\n('SM_VK_Prop_FlowerBox_inst.116', 1605.6, 130.5, 3.8, [1578.0, 1626.0, 126.0, 132.0, 3.0])\n('SM_VK_Prop_FlowerBox_inst.119
# ', 1594.5, 110.4, 3.8, [1584.0, 1608.0, 99.0, 117.0, 3.0])\n('SM_VK_Prop_FlowerBox_inst.120', 1591.5, 110.4, 3.8, [1584.0, 1608.0, 99.0, 117.0, 3.0])\
# n('SM_VK_Prop_FlowerBox_Daisy_inst.034', 1598.4, 112.5, 3.8, [1584.0, 1608.0, 99.0, 117.0, 3.0])\n('SM_VK_Prop_Planter_inst.029', 1673.6, 84.8, 3.0, [
# 1629.0, 1686.0, 78.0, 96.0, 3.0])\n('SM_VK_Prop_FlowerBox_inst.123', 1674.5, 82.5, 3.9, [1629.0, 1686.0, 78.0, 96.0, 3.0])\n('SM_VK_Prop_FlowerBox_ins

# ==============================================================================================================
# [0037] 2026-09-23 17:19:50  blender  ok
# ==============================================================================================================
import bpy
colony=bpy.app.driver_namespace['colony']
print(colony("review_art_26_meadow_west_crafts",1525,60,1.5))
print(colony("review_art_27_mainroad_bridge",1627,30,1.0))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_26_meadow_west_crafts.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review
# \\art\\review_art_27_mainroad_bridge.png\n"}

# ==============================================================================================================
# [0038] 2026-09-23 17:21:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\art"
bvh=bpy.app.driver_namespace['vk_terrain_bvh']
from mathutils import Vector
for y in [50,51,52,53,54,54.5,55,56]:
    h=bvh.ray_cast(Vector((1530,y,60)),Vector((0,0,-1)),200); print(y, round(h[0].z,2), tuple(round(v,2) for v in h[1]))
print(shot("review_art_28_eye_lip_meadow_sand",(1532,47,1.4),(1536,54,1.0),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: 50 0.0 (0.0, 0.0, 1.0)\n51 0.0 (0.0, 0.0, 1.0)\n52 0.0 (0.0, 0.0, 1.0)\n53 -0.0 (0.0, 0.0, 1.0)\n54 0.85 (0.04,
#  -0.27, 0.96)\n54.5 1.49 (-0.0, -0.07, 1.0)\n55 1.5 (0.0, 0.0, 1.0)\n56 1.5 (0.0, 0.0, 1.0)\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\art\\review_art_28_eye
# _lip_meadow_sand.png\n"}

# ==============================================================================================================
# [0039] 2026-09-23 17:22:08  blender  ok
# ==============================================================================================================
import bpy
for base in ['SM_VK_Tree_Willow','SM_VK_Tree_Oak_A','SM_VK_Tree_Pine_A','SM_VK_Tree_Birch','SM_VK_Bush_Round','SM_VK_Tree_Pine_Young']:
    me=bpy.data.meshes.get(base)
    if not me:
        o=next((o for o in bpy.data.objects if o.name.startswith(base+'_inst')),None); me=o.data if o else None
    if not me: print('none',base); continue
    print(base, me.name, len(me.polygons), 'custom_normals',me.has_custom_normals, [a.name for a in me.attributes if a.domain in('CORNER','POINT')][:8])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Willow SM_VK_Tree_Willow 1150 custom_normals True ['position', '.corner_vert', '.corner_edge', 'Col'
# , 'custom_normal', 'UVMap']\nSM_VK_Tree_Oak_A SM_VK_Tree_Oak_A 4355 custom_normals True ['position', '.corner_vert', '.corner_edge', 'Col', 'custom_no
# rmal', 'UVMap']\nSM_VK_Tree_Pine_A SM_VK_Tree_Pine_A 4590 custom_normals True ['position', '.corner_vert', '.corner_edge', 'Col', 'custom_normal', 'UV
# Map']\nSM_VK_Tree_Birch SM_VK_Tree_Birch 4172 custom_normals True ['position', '.corner_vert', '.corner_edge', 'Col', 'custom_normal', 'UVMap']\nSM_VK
# _Bush_Round SM_VK_Bush_Round 342 custom_normals True ['position', '.corner_vert', '.corner_edge', 'Col', 'custom_normal', 'UVMap']\nSM_VK_Tree_Pine_Yo
# ung SM_VK_Tree_Pine_Young 3663 custom_normals True ['position', '.corner_vert', '.corner_edge', 'Col', 'custom_normal', 'UVMap']\n"}

# ==============================================================================================================
# [0040] 2026-09-23 17:23:17  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
col=bpy.data.collections['VK_ValleyTown']
w=bpy.data.objects['SM_VK_TownWall_Straight_inst']
c=[w.matrix_world@Vector(v) for v in w.bound_box]
print('wall bb y',round(min(v.y for v in c),2),round(max(v.y for v in c),2),'z',round(min(v.z for v in c),2),round(max(v.z for v in c),2))
walls=[o for o in col.all_objects if o.name.startswith('SM_VK_TownWall') or o.name.startswith('SM_VK_Gatehouse_Block')]
bbs=[]
for o in walls:
    c=[o.matrix_world@Vector(v) for v in o.bound_box]
    bbs.append((o.name,min(v.x for v in c),max(v.x for v in c),min(v.y for v in c),max(v.y for v in c)))
out=[]
for t in col.all_objects:
    if 'Tree_' not in t.name and 'Bush_' not in t.name: continue
    p=t.matrix_world.translation
    for n,x0,x1,y0,y1 in bbs:
        if x0-0.3<p.x<x1+0.3 and y0-0.3<p.y<y1+0.3:
            out.append((t.name,round(p.x,1),round(p.y,1),round(p.z,1),n)); break
print(len(out))
for o in out: print(o)
# ---- result ----
# {"result":"Code executed successfully: wall bb y 73.36 76.18 z 1.5 10.95\n16\n('SM_VK_Tree_Oak_B_inst.023', 1601.3, 74.4, 3.0, 'SM_VK_TownWall_Straigh
# t_inst.020')\n('SM_VK_Tree_Apple_inst.009', 1619.4, 74.0, 3.0, 'SM_VK_TownWall_Straight_inst.032')\n('SM_VK_Bush_Round_inst.037', 1633.1, 72.9, 3.0, '
# SM_VK_Gatehouse_Block_inst')\n('SM_VK_Bush_Round_inst.038', 1645.3, 73.7, 3.0, 'SM_VK_TownWall_Straight_inst.047')\n('SM_VK_Tree_Birch_inst.014', 1655
# .0, 73.4, 3.0, 'SM_VK_TownWall_Straight_inst.053')\n('SM_VK_Tree_Birch_inst.015', 1659.5, 73.3, 3.0, 'SM_VK_TownWall_Straight_inst.057')\n('SM_VK_Tree
# _Birch_inst.016', 1670.2, 74.0, 3.0, 'SM_VK_TownWall_Straight_inst.063')\n('SM_VK_Bush_Round_inst.043', 1567.8, 91.0, 3.0, 'SM_VK_TownWall_Straight_in
# st.087')\n('SM_VK_Bush_Round_inst.045', 1566.6, 97.7, 3.0, 'SM_VK_TownWall_Tower_Round_inst.008')\n('SM_VK_Bush_Hydrangea_inst.007', 1688.5, 106.3, 3.
