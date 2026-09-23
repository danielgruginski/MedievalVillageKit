# valley-rereview / agent-ac910b8221bab24cf.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 18:47:35  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts.get("vk_render")
print(t.as_string()[:3000] if t else "none")
print(bpy.context.scene.name, bpy.context.scene.render.engine)
# ---- result ----
# {"result":"Code executed successfully: import bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,len
# s=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is 
# None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.
# link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_e
# nd=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.render.

# ==============================================================================================================
# [0002] 2026-09-23 18:48:12  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
t=time.time()
p=shot("art_00_overview",(1608,-60,150),(1608,84,0),lens=30,res=(1600,900),outdir=OD)
print(p, time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_00_overview.png 3.3992934226989746\n"}

# ==============================================================================================================
# [0003] 2026-09-23 18:48:40  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials["M_VK_TerrainTown"]
for n in m.node_tree.nodes:
    s=f"{n.name}|{n.type}|{n.label}"
    if n.type=="TEX_IMAGE": s+=f" img={n.image.name if n.image else None}"
    if n.type in("HUE_SAT",): s+=" "+str([ (i.name, i.default_value if not i.is_linked and hasattr(i,'default_value') and not hasattr(i.default_value,'__len__') else ('L' if i.is_linked else tuple(i.default_value))) for i in n.inputs])
    if n.type=="MIX": s+=f" blend={n.blend_type} dt={n.data_type} fac={n.inputs[0].default_value if not n.inputs[0].is_linked else 'L'}"
    if n.type=="TEX_NOISE": s+=f" scale={n.inputs['Scale'].default_value}"
    if n.type=="RGB": s+=f" col={tuple(round(c,3) for c in n.outputs[0].default_value)}"
    print(s)
# ---- result ----
# {"result":"Code executed successfully: Material Output|OUTPUT_MATERIAL|\nPrincipled BSDF|BSDF_PRINCIPLED|\nTexture Coordinate|TEX_COORD|\nGeometry|NEW
# _GEOMETRY|\nSeparate XYZ|SEPXYZ|\nAttribute|ATTRIBUTE|\nSeparate Color|SEPARATE_COLOR|\nVector Math|VECT_MATH|\nVector Math.001|VECT_MATH|\nImage Text
# ure|TEX_IMAGE| img=T_VK_TerrainMacro\nSeparate Color.001|SEPARATE_COLOR|\nNoise Texture|TEX_NOISE| scale=0.3499999940395355\nVector Math.002|VECT_MATH
# |\nVector Math.003|VECT_MATH|\nVector Math.004|VECT_MATH|\nMapping|MAPPING|CTL_MAP\nImage Texture.001|TEX_IMAGE| img=T_VK_GroundCtl_Town\nSeparate Col
# or.002|SEPARATE_COLOR|\nImage Texture.002|TEX_IMAGE| img=T_VK_Grass_BC\nMapping.001|MAPPING|\nImage Texture.003|TEX_IMAGE| img=T_VK_Grass_BC\nMap Rang
# e|MAP_RANGE|\nMix|MIX| blend=MIX dt=RGBA fac=L\nHue/Saturation/Value|HUE_SAT| [('Hue', 0.5049999952316284), ('Saturation', 0.800000011920929), ('Value

# ==============================================================================================================
# [0004] 2026-09-23 18:50:10  blender  ok
# ==============================================================================================================
import bpy
def desc(mn):
    m=bpy.data.materials.get(mn)
    if not m: print(mn,"MISSING"); return
    print("==",mn, "users",m.users)
    for n in m.node_tree.nodes:
        if n.type=="BSDF_PRINCIPLED":
            d={}
            for k in ("Base Color","Emission Color","Emission Strength","Alpha","Roughness","Transmission Weight","Metallic"):
                i=n.inputs.get(k)
                if i is None: continue
                d[k]="L" if i.is_linked else (tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3))
            print(" BSDF",d)
        elif n.type=="EMISSION": print(" EMIT",n.inputs[1].default_value)
        elif n.type=="RGB": print(" RGB",n.name,tuple(round(c,3) for c in n.outputs[0].default_value))
        elif n.type=="HUE_SAT": print(" HSV",[round(i.default_value,3) for i in n.inputs[:4]])
        elif n.type=="TEX_IMAGE": print(" IMG",n.image.name if n.image else None)
        elif n.type in ("VALTORGB",): print(" RAMP",[ (round(e.position,2),tuple(round(c,3) for c in e.color)) for e in n.color_ramp.elements])
        elif n.type=="ATTRIBUTE": print(" ATTR",n.attribute_type,n.attribute_name)
        elif n.type=="OBJECT_INFO": print(" OBJINFO")
        elif n.type=="MIX": print(" MIX",n.name,n.blend_type,n.data_type)
        elif n.type=="TEX_NOISE": print(" NOISE",n.name,[round(i.default_value,3) for i in n.inputs if not i.is_linked and not hasattr(i.default_value,'__len__')])
        elif n.type=="TEX_WAVE": print(" WAVE",n.name,n.wave_type,[round(i.default_value,3) for i in n.inputs if not i.is_linked and not hasattr(i.default_value,'__len__')])
        elif n.type not in ("OUTPUT_MATERIAL","MATH","TEX_COORD","MAPPING","SEPXYZ","COMBXYZ","VECT_MATH"): print(" ",n.type,n.name)
    print(" blend",getattr(m,'blend_method',None), getattr(m,'surface_render_method',None))
for mn in ("M_VKT_Water","M_VK_RoofRed","M_VK_RoofBlue","M_VK_Clay","M_VK_Stained"):
    desc(mn)
print([m.name for m in bpy.data.materials if "Roof" in m.name or "Water" in m.name or "Hydr" in m.name or "Flower" in m.name])
# ---- result ----
# {"result":"Code executed successfully: == M_VKT_Water users 14\n BSDF {'Base Color': 'L', 'Emission Color': (1.0, 1.0, 1.0, 1.0), 'Emission Strength':
#  0.0, 'Alpha': 0.9, 'Roughness': 0.05, 'Transmission Weight': 0.0, 'Metallic': 0.0}\n NOISE Noise Texture [0.0, 0.9, 4.0, 0.5, 2.0, 0.0, 1.0, 0.0]\n N
# OISE Noise Texture.001 [0.0, 0.12, 1.0, 0.5, 2.0, 0.0, 1.0, 0.0]\n MAP_RANGE Map Range\n MIX Mix MIX RGBA\n MAP_RANGE Map Range.001\n MIX Mix.001 MIX 
# RGBA\n BUMP Bump\n blend HASHED DITHERED\n== M_VK_RoofRed users 827\n BSDF {'Base Color': 'L', 'Emission Color': (1.0, 1.0, 1.0, 1.0), 'Emission Stren
# gth': 0.0, 'Alpha': 1.0, 'Roughness': 'L', 'Transmission Weight': 0.0, 'Metallic': 0.0}\n UVMAP UV Map\n IMG T_VK_RoofRed_BC\n IMG T_VK_RoofRed_N\n IM
# G T_VK_RoofRed_R\n VERTEX_COLOR Color Attribute\n HSV [0.5, 0.78, 0.93, 1.0]\n OBJINFO\n MAP_RANGE Map Range\n MIX Mix MULTIPLY RGBA\n MIX Mix.001 MUL

# ==============================================================================================================
# [0005] 2026-09-23 18:50:53  blender  ok
# ==============================================================================================================
import bpy
def links(mn):
    m=bpy.data.materials[mn]; nt=m.node_tree
    print("==",mn)
    for l in nt.links:
        print(f"  {l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")
    for n in nt.nodes:
        if n.type in("MAP_RANGE",):
            print("  MR",n.name,[ (i.name,round(i.default_value,3)) for i in n.inputs[:5] if not i.is_linked and not hasattr(i.default_value,'__len__')])
        if n.type=="MIX":
            print("  MIX",n.name,n.blend_type,[ (i.name, tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if i.enabled and not i.is_linked])
        if n.type=="MAPPING": print("  MAP",n.name,[tuple(round(x,3) for x in i.default_value) for i in n.inputs[1:] if not i.is_linked])
        if n.type=="BUMP": print("  BUMP",[round(i.default_value,3) for i in n.inputs[:2]])
        if n.type=="TEX_NOISE": print("  NOISE",n.name,n.noise_dimensions, getattr(n,'noise_type',None))
links("M_VKT_Water")
for mn in ("M_VK_Roof_Blue","M_VK_Roof_Slate","M_VK_Roof_Green","M_VK_Roof_Shingle","M_VK_Roof_Thatch"):
    m=bpy.data.materials[mn]
    print(mn,"users",m.users,[ (n.type, [round(i.default_value,3) for i in n.inputs[:4]] if n.type=="HUE_SAT" else "") for n in m.node_tree.nodes if n.type in("HUE_SAT","OBJECT_INFO","TEX_IMAGE","RGB")])
# ---- result ----
# {"result":"Code executed successfully: == M_VKT_Water\n Texture Coordinate.Object -> Mapping.Vector\n Mapping.Vector -> Noise Texture.Vector\n Texture
#  Coordinate.Object -> Noise Texture.001.Vector\n Noise Texture.001.Fac -> Map Range.Value\n Map Range.Result -> Mix.Factor\n Noise Texture.Fac -> Map 
# Range.001.Value\n Map Range.001.Result -> Math.Value\n Math.Value -> Mix.001.Factor\n Mix.Result -> Mix.001.A\n Mix.001.Result -> Principled BSDF.Base
#  Color\n Noise Texture.Fac -> Bump.Height\n Bump.Normal -> Principled BSDF.Normal\n Principled BSDF.BSDF -> Material Output.Surface\n MAP Mapping [(0.
# 0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.18, 1.4, 1.0)]\n NOISE Noise Texture 3D FBM\n NOISE Noise Texture.001 3D FBM\n MR Map Range [('From Min', 0.35), ('F
# rom Max', 0.65), ('To Min', 0.0), ('To Max', 1.0)]\n MIX Mix MIX [('A', (0.035, 0.17, 0.2, 1.0)), ('B', (0.06, 0.27, 0.28, 1.0))]\n MR Map Range.001 [

# ==============================================================================================================
# [0006] 2026-09-23 18:51:12  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
rows=[]
for o in coll.all_objects:
    if o.type!="MESH" or "Roof" not in o.name: continue
    x,y=o.location.x,o.location.y
    mats=[s.material.name for s in o.material_slots if s.material and ("Roof" in s.material.name or "Thatch" in s.material.name)]
    rows.append((round(x,1),round(y,1),round(o.location.z,1),o.name,mats))
inside=[r for r in rows if 1569<r[0]<1689 and 75<r[1]<138]
cnt=collections.Counter(tuple(r[4]) for r in inside)
print(len(rows),len(inside),cnt)
# group by 6m grid
for r in sorted(inside,key=lambda r:(r[1],r[0])):
    if r[4] and r[4][0] in ("M_VK_Roof_Blue","M_VK_Roof_Thatch","M_VK_Roof_Green","M_VK_RoofRed"):
        print(r)
# ---- result ----
# {"result":"Code executed successfully: 134 85 Counter({('M_VK_Roof_Slate', 'M_VK_Thatch'): 26, ('M_VK_Roof_Shingle', 'M_VK_Thatch'): 26, ('M_VK_RoofRe
# d', 'M_VK_Thatch'): 16, ('M_VK_Roof_Blue', 'M_VK_Thatch'): 9, ('M_VK_Roof_Green', 'M_VK_Thatch'): 5, ('M_VK_Roof_Thatch', 'M_VK_Thatch'): 3})\n(1608.0
# , 82.5, 11.6, 'SM_VK_Roof_Gable_inst.081', ['M_VK_Roof_Green', 'M_VK_Thatch'])\n(1657.5, 84.0, 8.8, 'SM_VK_Roof_Mid_CapR_inst.001', ['M_VK_RoofRed', '
# M_VK_Thatch'])\n(1660.5, 84.0, 8.8, 'SM_VK_Roof_Mid_inst.040', ['M_VK_RoofRed', 'M_VK_Thatch'])\n(1663.5, 84.0, 8.8, 'SM_VK_Roof_Mid_CapL_inst', ['M_V
# K_RoofRed', 'M_VK_Thatch'])\n(1666.5, 84.0, 11.6, 'SM_VK_Roof_Gable_Flush_inst.001', ['M_VK_Roof_Blue', 'M_VK_Thatch'])\n(1669.5, 84.0, 11.6, 'SM_VK_R
# oof_Mid_inst.039', ['M_VK_Roof_Blue', 'M_VK_Thatch'])\n(1671.0, 84.0, 11.6, 'SM_VK_Roof_Firewall_inst.001', ['M_VK_RoofRed', 'M_VK_Thatch'])\n(1603.5,

# ==============================================================================================================
# [0007] 2026-09-23 18:51:37  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    # yaw 0 = camera south of target looking north
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_01_skyline",1605,125,3))
print(colony("art_02_terrace_se",1660,88,3))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_01_skyline.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scrat
# ch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_02_
# terrace_se.png\n"}

# ==============================================================================================================
# [0008] 2026-09-23 18:52:59  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_03_chapel",1650,112,3))
print(colony("art_04_westquarter",1590,92,3))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_03_chapel.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratc
# h-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_04_w
# estquarter.png\n"}

# ==============================================================================================================
# [0009] 2026-09-23 18:53:55  blender  ok
# ==============================================================================================================
import bpy
nt=bpy.data.materials["M_VK_TerrainTown"].node_tree
def ins(n): return [(i.name, (l.from_node.name+"."+l.from_socket.name) if (l:=next((l for l in nt.links if l.to_socket==i),None)) else (round(i.default_value,3) if not hasattr(i.default_value,'__len__') else tuple(round(x,3) for x in i.default_value))) for i in n.inputs if i.enabled]
for nm in ("Hue/Saturation/Value","Mix","Map Range","Image Texture.002","Image Texture.003","Mapping.001","Mix.017","Combine Color","Map Range.005","Math.066","Mix.018","Mix.019","Combine Color.001","Math.069","Mix.020","Mix.021","Math.067","Math.068","Separate Color.001","Image Texture","Noise Texture","Vector Math.002"):
    n=nt.nodes.get(nm)
    if n: print(nm, n.type, getattr(n,'operation',''), ins(n))
print([ (l.from_node.name, l.to_node.name, l.to_socket.name) for l in nt.links if l.from_node.name in("Separate Color.001","Separate Color.002","Image Texture")])
# ---- result ----
# {"result":"Code executed successfully: Hue/Saturation/Value HUE_SAT [('Hue', 0.505), ('Saturation', 0.8), ('Value', 0.97), ('Fac', 1.0), ('Color', 'Mi
# x.Result')]\nMix MIX [('Factor', 'Map Range.Result'), ('A', 'Image Texture.002.Color'), ('B', 'Image Texture.003.Color')]\nMap Range MAP_RANGE [('Valu
# e', 'Separate Color.001.Blue'), ('From Min', 0.3), ('From Max', 0.7), ('To Min', 0.0), ('To Max', 1.0)]\nImage Texture.002 TEX_IMAGE [('Vector', 'Vect
# or Math.Vector')]\nImage Texture.003 TEX_IMAGE [('Vector', 'Mapping.001.Vector')]\nMapping.001 MAPPING [('Vector', 'Texture Coordinate.Object'), ('Loc
# ation', (0.0, 0.0, 0.0)), ('Rotation', (0.0, 0.0, 0.646)), ('Scale', (0.076, 0.076, 1.0))]\nMix.017 MIX [('Factor', 1.0), ('A', 'Mix.015.Result'), ('B
# ', 'Combine Color.Color')]\nCombine Color COMBINE_COLOR [('Red', 'Separate Color.Red'), ('Green', 'Separate Color.Red'), ('Blue', 'Separate Color.Red'

# ==============================================================================================================
# [0010] 2026-09-23 18:54:23  blender  ok
# ==============================================================================================================
import bpy, math
coll=bpy.data.collections["VK_ValleyTown"]
tr=[]
for o in coll.all_objects:
    if o.type=="MESH" and ("Tree_" in o.name or "Bush_Large" in o.name):
        x,y=o.location.x,o.location.y
        if 1580<x<1615 and -5<y<30: tr.append((o.name,round(x,1),round(y,1)))
print(tr)
for n in ("SM_VK_Tree_Oak_A_inst.017","SM_VK_Tree_Oak_B_inst.015","SM_VK_Tent_Bell_inst"):
    o=bpy.data.objects.get(n); print(n, o and tuple(round(c,1) for c in o.location))
camp=[(o.name,round(o.location.x,1),round(o.location.y,1)) for o in coll.all_objects if o.type=="MESH" and ("Tent" in o.name or "Campfire" in o.name or "Fire" in o.name)]
print(camp)
# ---- result ----
# {"result":"Code executed successfully: []\nSM_VK_Tree_Oak_A_inst.017 (1558.7, 104.0, 4.5)\nSM_VK_Tree_Oak_B_inst.015 (1527.7, 106.7, 4.5)\nSM_VK_Tent_
# Bell_inst (1597.0, 11.2, 1.5)\n[('SM_VK_Prop_Campfire_inst', 1594.5, 13.5), ('SM_VK_Tent_A_inst', 1593.9, 16.7), ('SM_VK_Tent_A_inst.001', 1591.5, 12.
# 2), ('SM_VK_Tent_Bell_inst', 1597.0, 11.2), ('SM_VK_Roof_Firewall_inst', 1593.0, 129.0), ('SM_VK_Roof_Firewall_inst.001', 1671.0, 84.0)]\n"}

# ==============================================================================================================
# [0011] 2026-09-23 18:55:00  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_05_camp",1596,13,1.5))
print(colony("art_06_construction",1655,64,1.5))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_05_camp.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-
# workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_06_con
# struction.png\n"}

# ==============================================================================================================
# [0012] 2026-09-23 18:55:36  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
c=collections.Counter()
for o in coll.all_objects:
    if o.type=="MESH" and "Scaffold" in o.name:
        me=o.data
        used=collections.Counter(p.material_index for p in me.polygons)
        mats=tuple((o.material_slots[i].material.name if i<len(o.material_slots) and o.material_slots[i].material else None, n) for i,n in sorted(used.items()))
        c[(me.name,mats)]+=1
for k,v in c.items(): print(v,k)
print(sum(1 for o in bpy.data.objects if o.type=="MESH" and any(s.material and "Birch" in s.material.name for s in o.material_slots) and "Scaffold" in o.name))
# ---- result ----
# {"result":"Code executed successfully: 10 ('SM_VK_Scaffold_Wall', (('M_VK_Wood', 52), ('M_VK_Planks', 52), ('M_VK_Burlap', 48), ('M_VK_BarkOak', 46), 
# ('M_VK_EndGrain', 4)))\n4 ('SM_VK_Scaffold_Corner', (('M_VK_Wood', 52), ('M_VK_Planks', 104), ('M_VK_Burlap', 64), ('M_VK_BarkOak', 86), ('M_VK_EndGra
# in', 8)))\n5 ('SM_VK_Scaffold_Wall_Top', (('M_VK_Wood', 52), ('M_VK_Planks', 52), ('M_VK_Burlap', 48), ('M_VK_BarkOak', 46), ('M_VK_EndGrain', 4)))\n2
#  ('SM_VK_Scaffold_Corner_Top', (('M_VK_Wood', 52), ('M_VK_Planks', 104), ('M_VK_Burlap', 64), ('M_VK_BarkOak', 86), ('M_VK_EndGrain', 8)))\n1 ('SM_VK_
# Scaffold_Ladder', (('M_VK_Wood', 97),))\n27\n"}

# ==============================================================================================================
# [0013] 2026-09-23 18:55:58  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_07_river_mill",1580,42,0))
print(colony("art_08_lake",1695,38,0))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_07_river_mill.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\sc
# ratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_
# 08_lake.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 18:57:11  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
k=[o for o in coll.all_objects if "BottleKiln" in o.name]
for o in k: print(o.name, tuple(round(c,1) for c in o.location), [s.material.name for s in o.material_slots if s.material])
h=[o for o in coll.all_objects if "Hydrangea" in o.name]
print("hydrangea",len(h),[ (o.name,round(o.location.x,1),round(o.location.y,1)) for o in h][:20])
if h:
    o=h[0]; print([s.material.name for s in o.material_slots if s.material])
    src=bpy.data.objects.get("SM_VK_Bush_Hydrangea")
    print("src mats",[s.material.name for s in src.material_slots] if src else None, src.data.name if src else None, h[0].data.name)
# chapel windows / stained
st=[o for o in coll.all_objects if o.type=="MESH" and any(s.material and s.material.name=="M_VK_Stained" for s in o.material_slots)]
print("stained objs",len(st),[o.name for o in st][:10])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_BottleKiln_inst (1543.0, 63.1, 1.5) ['M_VK_Stone', 'M_VK_Plaster', 'M_VK_Wood', 'M_VK_RoofRed', 'M_V
# K_Window', 'M_VK_Iron', 'M_VK_FlowerPink', 'M_VK_FlowerYellow', 'M_VK_Leaf', 'M_VK_Glow', 'M_VK_Shutter_Teal', 'M_VK_Cloth_Red', 'M_VK_Cloth_Cream', '
# M_VK_Apple', 'M_VK_Pumpkin', 'M_VK_Bread', 'M_VK_Hay', 'M_VK_Paper', 'M_VK_Water', 'M_VK_Bronze', 'M_VK_Stained', 'M_VK_Steel', 'M_VK_Thatch', 'M_VK_P
# lanks', 'M_VK_Ashlar', 'M_VK_Burlap', 'M_VK_Soil', 'M_VK_Void', 'M_VK_Rock', 'M_VK_Clay', 'M_VK_Clock', 'M_VK_Foliage', 'M_VK_Crops', 'M_VK_BarkOak', 
# 'M_VK_BarkBirch', 'M_VK_BarkPine', 'M_VK_Leaves', 'M_VK_Moss', 'M_VK_RockMossy', 'M_VK_BarkMossy', 'M_VK_EndGrain', 'M_VK_MushRed', 'M_VK_MushBrown', 
# 'M_VK_MushStem', 'M_VK_MushGlow', 'M_VK_StoneBlock', 'M_VK_FieldStone', 'M_VK_Wattle', 'M_VK_Hide', 'M_VK_Pigskin', 'M_VK_Coal', 'M_VK_Net']\nhydrange

# ==============================================================================================================
# [0015] 2026-09-23 18:58:08  blender  ok
# ==============================================================================================================
import bpy, collections, colorsys
o=bpy.data.objects["SM_VK_Prop_BottleKiln_inst"]; me=o.data
used=collections.Counter(p.material_index for p in me.polygons)
print([(o.material_slots[i].material.name,n) for i,n in used.most_common()])
# vertex colours on clay faces
ca=me.color_attributes.active_color
print("attr",ca and (ca.name,ca.domain,ca.data_type))
if ca:
    idx=[i for i,s in enumerate(o.material_slots) if s.material and s.material.name=="M_VK_Clay"][0]
    cols=[]
    if ca.domain=="CORNER":
        for p in me.polygons:
            if p.material_index==idx:
                for li in p.loop_indices: cols.append(tuple(ca.data[li].color[:3]))
    else:
        for p in me.polygons:
            if p.material_index==idx:
                for vi in p.vertices: cols.append(tuple(ca.data[vi].color[:3]))
    import statistics
    avg=[statistics.mean(c[k] for c in cols) for k in range(3)]
    print("clay vcol avg lin",[round(a,3) for a in avg], "hsv",[round(x,2) for x in colorsys.rgb_to_hsv(*avg)])
m=bpy.data.materials["M_VK_Clay"]
for n in m.node_tree.nodes:
    if n.type=="MIX": print(n.name,n.blend_type,[(i.name,tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if i.enabled and not i.is_linked])
print(bpy.data.materials["M_VK_Clay"].node_tree.nodes.get("Image Texture").image.name if bpy.data.materials["M_VK_Clay"].node_tree.nodes.get("Image Texture") else [n.image.name for n in m.node_tree.nodes if n.type=="TEX_IMAGE"])
# ---- result ----
# {"result":"Code executed successfully: [('M_VK_Clay', 1196), ('M_VK_Iron', 532), ('M_VK_StoneBlock', 216), ('M_VK_Void', 18), ('M_VK_Glow', 5), ('M_VK
# _Planks', 2)]\nattr None\nMix MULTIPLY [('Factor', 1.0), ('B', (0.56, 0.42, 0.35, 1.0))]\nMix.001 MULTIPLY [('Factor', 1.0)]\nT_VK_Plaster_BC\n"}

# ==============================================================================================================
# [0016] 2026-09-23 18:58:41  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_09_pottery_kiln",1545,63,1.5))
print(colony("art_10_chapel_front",1650,108,4,dist=22,pitch=30,yaw=180,lens=35))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_09_pottery_kiln.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\
# scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\ar
# t_10_chapel_front.png\n"}

# ==============================================================================================================
# [0017] 2026-09-23 18:59:44  blender  ok
# ==============================================================================================================
import bpy
coll=bpy.data.collections["VK_ValleyTown"]
for o in coll.all_objects:
    n=o.name
    if any(k in n for k in ("Anvil","Forge","Sign_","Emblem","Bellows","Grindstone")):
        print(n, tuple(round(c,1) for c in o.location), round(o.rotation_euler.z*57.3))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Bellows_inst (1558.2, 77.3, 3.0) 0\nSM_VK_Prop_Anvil_inst.003 (1555.4, 74.2, 3.0) 25\nSM_VK_Prop_Gri
# ndstone_inst.002 (1543.1, 96.2, 3.0) 70\nSM_VK_Prop_Sign_inst (1581.2, 90.2, 6.3) 180\nSM_VK_Prop_Sign_inst.001 (1580.6, 90.2, 5.8) 180\nSM_VK_Emblem_
# Ridge_Tankard_inst (1593.0, 91.0, 16.7) 90\nSM_VK_Prop_Sign_inst.002 (1592.7, 90.0, 6.0) 180\nSM_VK_Prop_Sign_inst.003 (1608.2, 90.2, 6.3) 180\nSM_VK_
# Sign_Potion_inst (1611.2, 89.8, 6.3) 90\nSM_VK_Emblem_Ridge_Sheaf_inst (1582.0, 129.0, 11.1) 0\nSM_VK_Emblem_Ridge_Key_inst (1583.0, 114.0, 13.9) 180\
# nSM_VK_Emblem_Ridge_Anvil_inst (1598.0, 114.0, 11.1) 180\nSM_VK_Prop_Anvil_inst.004 (1601.2, 118.2, 3.0) 180\nSM_VK_Emblem_Ridge_Tankard_inst.001 (167
# 2.5, 117.0, 13.0) 0\nSM_VK_Prop_Forge_inst.003 (1675.6, 130.2, 3.0) -90\nSM_VK_Prop_Anvil_inst.005 (1675.8, 128.1, 3.0) 20\nSM_VK_Prop_Grindstone_inst

# ==============================================================================================================
# [0018] 2026-09-23 19:00:33  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_11_skyline_anvil",1600,114,4,dist=28))
print(colony("art_12_blacksmith",1672,126,3,dist=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_11_skyline_anvil.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\
# \scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\a
# rt_12_blacksmith.png\n"}

# ==============================================================================================================
# [0019] 2026-09-23 19:02:14  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["VillageKit"]
for o in sc.objects:
    if o.type=="LIGHT":
        L=o.data
        print(o.name,L.type,round(L.energy,3),tuple(round(c,3) for c in L.color),"shadow",L.use_shadow,"angle",round(getattr(L,'angle',0),3),"rot",tuple(round(r*57.3,1) for r in o.rotation_euler), "hide_render",o.hide_render, [c.name for c in o.users_collection])
w=sc.world
print("world",w and w.name)
if w and w.use_nodes:
    for n in w.node_tree.nodes:
        if n.type=="BACKGROUND": print(" bg",[ (i.name, "L" if i.is_linked else (tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3))) for i in n.inputs])
        elif n.type not in("OUTPUT_WORLD",): print(" ",n.type,n.name)
print("view transform",sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure,sc.view_settings.gamma)
print("eevee",sc.eevee.use_shadows if hasattr(sc.eevee,'use_shadows') else None, getattr(sc.eevee,'use_gtao',None))
# ---- result ----
# {"result":"Code executed successfully: VK_Fill SUN 1.5 (0.85, 0.9, 1.0) shadow False angle 0.009 rot (52.3, -0.0, 129.3) hide_render False ['Scene Col
# lection']\nVK_Sun SUN 3.2 (1.0, 0.88, 0.72) shadow True angle 0.044 rot (52.0, 6.0, -30.0) hide_render False ['VK_Staging']\nworld MC_World\n bg [('Co
# lor', 'L'), ('Strength', 0.22), ('Weight', 0.0)]\n TEX_SKY Sky Texture\n LIGHT_PATH Light Path\n bg [('Color', 'L'), ('Strength', 1.0), ('Weight', 0.0
# )]\n TEX_COORD Texture Coordinate\n VALTORGB Color Ramp\n MIX_SHADER Mix Shader\n SEPXYZ Separate XYZ\nview transform AgX AgX - Medium High Contrast -
# 0.20000000298023224 1.0\neevee False True\n"}

# ==============================================================================================================
# [0020] 2026-09-23 19:03:02  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_13_gate",1626,70,2))
print(colony("art_14_postern",1566,90,3,yaw=-60))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_13_gate.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-
# workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_14_pos
# tern.png\n"}

# ==============================================================================================================
# [0021] 2026-09-23 19:03:41  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_14b_postern_west",1566,91.5,3,yaw=90))
print(colony("art_15_quarry",1545,96,4))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_14b_postern_west.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\
# \scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\a
# rt_15_quarry.png\n"}

# ==============================================================================================================
# [0022] 2026-09-23 19:05:01  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
terr=bpy.data.collections["VK_ValleyTerrain"]
def ground_z(x,y):
    # ray cast only against terrain chunks
    best=None
    for o in terr.all_objects:
        if o.type!="MESH" or "Chunk" not in o.name: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if not (min(b.x for b in bb)-0.1<=x<=max(b.x for b in bb)+0.1 and min(b.y for b in bb)-0.1<=y<=max(b.y for b in bb)+0.1): continue
        mw=o.matrix_world; inv=mw.inverted()
        ok,loc,nor,idx=o.ray_cast(inv@Vector((x,y,50)), (inv.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(mw@loc).z
            if best is None or z>best[0]: best=(z,o.data.materials[o.data.polygons[idx].material_index].name if o.data.materials else None)
    return best
for i in range(9,24):
    x=1500+3*i+1.5; y=91.5
    print(i, x, ground_z(x,y))
# ---- result ----
# {"result":"Code executed successfully: 9 1528.5 (3.0, 'M_VK_TerrainTown')\n10 1531.5 (3.0000038146972656, 'M_VK_TerrainTown')\n11 1534.5 (6.0, 'M_VK_T
# errainTown')\n12 1537.5 (6.0, 'M_VK_TerrainTown')\n13 1540.5 (3.0, 'M_VK_TerrainTown')\n14 1543.5 (3.0, 'M_VK_TerrainTown')\n15 1546.5 (3.0, 'M_VK_Ter
# rainTown')\n16 1549.5 (3.0, 'M_VK_TerrainTown')\n17 1552.5 (6.0, 'M_VK_TerrainTown')\n18 1555.5 (6.0, 'M_VK_TerrainTown')\n19 1558.5 (3.0, 'M_VK_Terra
# inTown')\n20 1561.5 (3.0, 'M_VK_TerrainTown')\n21 1564.5 (3.0, 'M_VK_TerrainTown')\n22 1567.5 (3.0, 'M_VK_TerrainTown')\n23 1570.5 (3.0, 'M_VK_Terrain
# Town')\n"}

# ==============================================================================================================
# [0023] 2026-09-23 19:05:36  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
res=collections.Counter()
for o in coll.all_objects:
    if o.type!="MESH": continue
    x,y=o.location.x,o.location.y
    if 1535<x<1556 and 90<y<104:
        used=collections.Counter(p.material_index for p in o.data.polygons)
        mats=[o.material_slots[i].material.name for i,_ in used.most_common(3) if i<len(o.material_slots) and o.material_slots[i].material]
        res[(o.name.split("_inst")[0],tuple(mats))]+=1
for k,v in sorted(res.items()): print(v,k)
# ---- result ----
# {"result":"Code executed successfully: 1 ('SM_VK_LeanTo', ('M_VK_Wood', 'M_VK_StoneBlock', 'M_VK_Roof_Thatch'))\n1 ('SM_VK_Pile_Stone_3', ('M_VK_Ashla
# r', 'M_VK_Wood', 'M_VK_Planks'))\n1 ('SM_VK_Plant_Fern', ('M_VK_Leaves',))\n1 ('SM_VK_Prop_Banker', ('M_VK_StoneBlock', 'M_VK_Ashlar', 'M_VK_Wood'))\n
# 1 ('SM_VK_Prop_Grindstone', ('M_VK_Wood', 'M_VK_Iron', 'M_VK_Stone'))\n1 ('SM_VK_Prop_Wheelbarrow', ('M_VK_Wood', 'M_VK_StoneBlock', 'M_VK_Iron'))\n2 
# ('SM_VK_Quarry_Face_Corner', ('M_VK_StoneBlock', 'M_VK_Rock', 'M_VK_RockMossy'))\n2 ('SM_VK_Quarry_Face_InnerCorner', ('M_VK_StoneBlock', 'M_VK_Rock',
#  'M_VK_Foliage'))\n5 ('SM_VK_Quarry_Face_Straight', ('M_VK_StoneBlock', 'M_VK_Rock', 'M_VK_Foliage'))\n2 ('SM_VK_Quarry_Floor', ('M_VK_StoneBlock', 'M
# _VK_Iron', 'M_VK_Wood'))\n1 ('SM_VK_Rock_Boulder_A', ('M_VK_RockMossy',))\n1 ('SM_VK_Rock_Small_A', ('M_VK_Rock',))\n"}

# ==============================================================================================================
# [0024] 2026-09-23 19:06:53  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
meshes={}
for o in coll.all_objects:
    if o.type!="MESH": continue
    me=o.data
    if me.name not in meshes:
        idx=[i for i,s in enumerate(o.material_slots) if s.material and s.material.name=="M_VK_Foliage"]
        n=sum(1 for p in me.polygons if p.material_index in idx) if idx else 0
        meshes[me.name]=[n,0]
    meshes[me.name][1]+=1
print(sorted([(k,v) for k,v in meshes.items() if v[0]>0],key=lambda kv:-kv[1][0]*kv[1][1])[:20])
m=bpy.data.materials["M_VK_Foliage"]
print([(n.type,n.name,[ (i.name,tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if i.enabled and not i.is_linked][:4]) for n in m.node_tree.nodes if n.type in("MIX","HUE_SAT","RGB","TEX_IMAGE")])
# ---- result ----
# {"result":"Code executed successfully: [('SM_VK_Crop_Cabbage', [784, 17]), ('SM_VK_Deco_Weeds', [80, 127]), ('SM_VK_Deco_Hedge', [344, 10]), ('SM_VK_P
# rop_FlowerBox.002', [72, 42]), ('SM_VK_Prop_FlowerBox_Daisy', [72, 38]), ('SM_VK_Deco_Ivy_B', [220, 11]), ('SM_VK_Deco_Ivy_A', [184, 12]), ('SM_VK_Cro
# p_Pumpkin', [104, 6]), ('SM_VK_Prop_Planter', [24, 23]), ('SM_VK_Deco_Bush', [120, 4]), ('SM_VK_Quarry_Face_Straight', [48, 5]), ('SM_VK_Crop_TreeNurs
# ery', [96, 2]), ('SM_VK_Mine_Portal', [168, 1]), ('SM_VK_Quarry_Face_InnerCorner', [56, 2]), ('SM_VK_Prop_TanningPit', [24, 4]), ('SM_VK_Prop_ClayPit'
# , [80, 1]), ('SM_VK_Quarry_Face_Corner', [40, 2]), ('SM_VK_Quarry_Floor', [24, 2]), ('SM_VK_Prop_Maypole', [40, 1]), ('SM_VK_Rail_End', [24, 1])]\n[('
# TEX_IMAGE', 'Image Texture', []), ('MIX', 'Mix', [('Factor', 1.0)])]\n"}

# ==============================================================================================================
# [0025] 2026-09-23 19:07:48  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
reg=collections.Counter(); willow=[]
for o in coll.all_objects:
    if o.type!="MESH": continue
    b=o.name.split("_inst")[0]
    if not (b.startswith("SM_VK_Tree_") or b=="SM_VK_Bush_Large"): continue
    x,y=o.location.x-1500,o.location.y
    j=int(y//3); i=int(x//3)
    if b=="SM_VK_Tree_Willow": willow.append((o.name,round(o.location.x,1),round(y,1)))
    if j<=9: r="south_land"
    elif j<=17: r="river_banks"
    elif j<=23: r="meadow"
    elif j>=47: r="north_ridge"
    elif i<20 and j>=34: r="west_ridge"
    elif i<20: r="west_bench"
    elif 23<=i<63 and 25<=j<46: r="town"
    else: r="other_l2"
    reg[(r,b.replace("SM_VK_",""))]+=1
tot=collections.Counter()
for (r,b),n in reg.items(): tot[r]+=n
print(tot)
print(sorted([(k,v) for k,v in reg.items() if k[0] in("south_land","meadow","river_banks","town","other_l2","west_bench")]))
print("willows",willow)
# ---- result ----
# {"result":"Code executed successfully: Counter({'north_ridge': 512, 'west_ridge': 183, 'other_l2': 4, 'south_land': 3, 'river_banks': 2, 'meadow': 2, 
# 'west_bench': 1})\n[(('meadow', 'Tree_Apple'), 1), (('meadow', 'Tree_Birch'), 1), (('other_l2', 'Bush_Large'), 1), (('other_l2', 'Tree_Apple'), 1), ((
# 'other_l2', 'Tree_Birch'), 2), (('river_banks', 'Tree_Willow'), 2), (('south_land', 'Bush_Large'), 1), (('south_land', 'Tree_Apple'), 1), (('south_lan
# d', 'Tree_Willow'), 1), (('west_bench', 'Tree_Pine_Young'), 1)]\nwillows [('SM_VK_Tree_Willow_inst.001', 1714.9, 22.3), ('SM_VK_Tree_Willow_inst.002',
#  1662.5, 30.9), ('SM_VK_Tree_Willow_inst.003', 1504.3, 34.3)]\n"}

# ==============================================================================================================
# [0026] 2026-09-23 19:08:39  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
c=collections.Counter(); lowz=collections.Counter()
for o in coll.all_objects:
    if o.type!="MESH": continue
    b=o.name.split("_inst")[0]
    if b.startswith("SM_VK_Tree_") or b.startswith("SM_VK_Bush") or b.startswith("SM_VK_Plant") :
        c[b]+=1
        if o.location.z<3.5: lowz[b]+=1
print("all",sorted(c.items()))
print("z<3.5",sorted(lowz.items()))
print(len(coll.all_objects))
# ---- result ----
# {"result":"Code executed successfully: all [('SM_VK_Bush_Hydrangea', 3), ('SM_VK_Bush_Large', 2), ('SM_VK_Bush_Round', 112), ('SM_VK_Plant_Fern', 114)
# , ('SM_VK_Plant_Reeds', 35), ('SM_VK_Plant_TallGrass', 44), ('SM_VK_Plant_Wildflowers', 41), ('SM_VK_Tree_Apple', 3), ('SM_VK_Tree_Birch', 21), ('SM_V
# K_Tree_Oak_A', 19), ('SM_VK_Tree_Oak_Autumn', 28), ('SM_VK_Tree_Oak_B', 27), ('SM_VK_Tree_Pine_A', 197), ('SM_VK_Tree_Pine_B', 213), ('SM_VK_Tree_Pine
# _Young', 194), ('SM_VK_Tree_Willow', 3)]\nz<3.5 [('SM_VK_Bush_Hydrangea', 3), ('SM_VK_Bush_Large', 2), ('SM_VK_Bush_Round', 28), ('SM_VK_Plant_Fern', 
# 14), ('SM_VK_Plant_Reeds', 35), ('SM_VK_Plant_TallGrass', 44), ('SM_VK_Plant_Wildflowers', 41), ('SM_VK_Tree_Apple', 3), ('SM_VK_Tree_Birch', 3), ('SM
# _VK_Tree_Pine_Young', 1), ('SM_VK_Tree_Willow', 3)]\n4584\n"}

# ==============================================================================================================
# [0027] 2026-09-23 19:09:47  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_16_town_roofs",1629,108,3,dist=95,pitch=55,lens=35))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_16_town_roofs.png\n"}

# ==============================================================================================================
# [0028] 2026-09-23 19:10:40  blender  ok
# ==============================================================================================================
import bpy, collections
coll=bpy.data.collections["VK_ValleyTown"]
kg=[]
for o in coll.all_objects:
    if o.type=="MESH" and o.name.startswith("SM_VK_Crop_") and 1569<o.location.x<1689 and 75<o.location.y<138:
        kg.append((o.name.split("_inst")[0].replace("SM_VK_Crop_",""),round(o.location.x,1),round(o.location.y,1),round(o.scale.x,2)))
print(len(kg), collections.Counter(k[0] for k in kg))
print(sorted(kg,key=lambda k:(k[2],k[1])))
m=bpy.data.materials.get("M_VK_Crops")
# Which materials on carrot / lavender
for n in ("SM_VK_Crop_Carrot","SM_VK_Crop_Lavender","SM_VK_Crop_Cabbage"):
    o=bpy.data.objects.get(n)
    if o:
        used=collections.Counter(p.material_index for p in o.data.polygons)
        print(n,[(o.material_slots[i].material.name,c) for i,c in used.most_common(4)])
# ---- result ----
# {"result":"Code executed successfully: 32 Counter({'Cabbage': 15, 'Lavender': 9, 'Carrot': 8})\n[('Carrot', 1573.5, 79.5, 0.8), ('Cabbage', 1630.5, 91
# .5, 0.8), ('Carrot', 1636.5, 91.5, 0.8), ('Carrot', 1645.5, 91.5, 0.8), ('Lavender', 1651.5, 91.5, 0.8), ('Lavender', 1654.5, 91.5, 0.8), ('Carrot', 1
# 669.5, 91.5, 0.8), ('Carrot', 1594.5, 94.5, 0.8), ('Cabbage', 1600.5, 94.5, 0.8), ('Cabbage', 1603.5, 94.5, 0.8), ('Carrot', 1597.5, 100.5, 0.8), ('La
# vender', 1585.5, 103.5, 0.8), ('Lavender', 1597.5, 103.5, 0.8), ('Cabbage', 1573.5, 106.5, 0.8), ('Lavender', 1579.5, 106.5, 0.8), ('Cabbage', 1582.5,
#  106.5, 0.8), ('Cabbage', 1588.5, 106.5, 0.8), ('Cabbage', 1594.5, 106.5, 0.8), ('Cabbage', 1597.5, 106.5, 0.8), ('Cabbage', 1669.5, 106.5, 0.8), ('La
# vender', 1633.5, 121.5, 0.8), ('Cabbage', 1663.5, 124.5, 0.8), ('Lavender', 1684.5, 124.5, 0.8), ('Cabbage', 1636.5, 127.5, 0.8), ('Carrot', 1642.5, 1

# ==============================================================================================================
# [0029] 2026-09-23 19:11:16  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_17_terrace_street_gardens",1645,92,3))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_17_terrace_street_gardens.png\n"}

# ==============================================================================================================
# [0030] 2026-09-23 19:12:17  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
print(shot("art_18_carrot_close",(1636.5,84.5,9),(1636.5,91.5,3),lens=35,res=(1200,675),outdir=OD))
o=bpy.data.objects["SM_VK_Crop_Carrot"]
print([ (s.material.name) for s in o.material_slots])
inst=[x for x in bpy.data.collections["VK_ValleyTown"].all_objects if x.name.startswith("SM_VK_Crop_Carrot") and abs(x.location.x-1636.5)<0.1 and abs(x.location.y-91.5)<0.1][0]
print(inst.name, tuple(inst.location), tuple(round(r,2) for r in inst.rotation_euler), tuple(inst.scale), inst.data.name, [s.link for s in inst.material_slots][:3], [s.material.name for s in inst.material_slots][:5])
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_18_carrot_close.png\n['M_VK_Stone', 'M_VK_Plaster', 'M_VK_Wood', 
# 'M_VK_RoofRed', 'M_VK_Window', 'M_VK_Iron', 'M_VK_FlowerPink', 'M_VK_FlowerYellow', 'M_VK_Leaf', 'M_VK_Glow', 'M_VK_Shutter_Teal', 'M_VK_Cloth_Red', '
# M_VK_Cloth_Cream', 'M_VK_Apple', 'M_VK_Pumpkin', 'M_VK_Bread', 'M_VK_Hay', 'M_VK_Paper', 'M_VK_Water', 'M_VK_Bronze', 'M_VK_Stained', 'M_VK_Steel', 'M
# _VK_Thatch', 'M_VK_Planks', 'M_VK_Ashlar', 'M_VK_Burlap', 'M_VK_Soil', 'M_VK_Void', 'M_VK_Rock', 'M_VK_Clay', 'M_VK_Clock', 'M_VK_Foliage', 'M_VK_Crop
# s', 'M_VK_BarkOak', 'M_VK_BarkBirch', 'M_VK_BarkPine', 'M_VK_Leaves', 'M_VK_Moss', 'M_VK_RockMossy', 'M_VK_BarkMossy', 'M_VK_EndGrain', 'M_VK_MushRed'

# ==============================================================================================================
# [0031] 2026-09-23 19:13:24  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
print(shot("art_18_carrot_close",(1640,96,11),(1636.5,91.5,3),lens=35,res=(1200,675),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_18_carrot_close.png\n"}

# ==============================================================================================================
# [0032] 2026-09-23 19:14:35  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
print(shot("art_19_lake_top",(1690,38,120),(1690,38.01,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_19_lake_top.png\n"}

# ==============================================================================================================
# [0033] 2026-09-23 19:15:18  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_20_footbridge",1530,42,0))
print(shot("art_21_west_top",(1545,40,120),(1545,40.01,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_20_footbridge.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\sc
# ratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_
# 21_west_top.png\n"}

# ==============================================================================================================
# [0034] 2026-09-23 19:16:12  blender  ok
# ==============================================================================================================
import bpy
coll=bpy.data.collections["VK_ValleyTown"]
for o in coll.all_objects:
    if o.type=="MESH" and 1563<o.location.x<1573 and 64<o.location.y<72:
        print(o.name, tuple(round(c,1) for c in o.location))
for n in ("SM_VK_Tree_Willow_inst.001","SM_VK_Tree_Willow_inst.003","SM_VK_Tree_Willow_inst.002"):
    o=bpy.data.objects[n]
    from mathutils import Vector
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n, "x",round(min(b.x for b in bb),1),round(max(b.x for b in bb),1),"y",round(min(b.y for b in bb),1),round(max(b.y for b in bb),1))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Crop_Lavender_inst.008 (1567.9, 67.5, 1.5)\nSM_VK_Prop_BeeBench_inst (1567.4, 64.6, 1.5)\nSM_VK_Prop_BeeB
# ench_inst.001 (1570.4, 64.1, 1.5)\nSM_VK_Rock_Pebbles_inst.057 (1564.7, 71.6, 1.5)\nSM_VK_Tree_Willow_inst.001 x 1709.2 1720.7 y 16.6 28.1\nSM_VK_Tree
# _Willow_inst.003 x 1498.6 1510.1 y 28.5 40.0\nSM_VK_Tree_Willow_inst.002 x 1657.1 1667.9 y 25.5 36.4\n"}

# ==============================================================================================================
# [0035] 2026-09-23 19:16:33  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_22_westquarter_north",1592,88,3,yaw=180))
print(colony("art_23_terrace_north",1660,86,3,yaw=180))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_22_westquarter_north.png\nC:\\Users\\danie\\AppData\\Roaming\\Cla
# ude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\ar
# t\\art_23_terrace_north.png\n"}

# ==============================================================================================================
# [0036] 2026-09-23 19:17:53  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
coll=bpy.data.collections["VK_ValleyTown"]
veg=("SM_VK_Tree_","SM_VK_Bush","SM_VK_Plant","SM_VK_Rock","SM_VK_LipGrass","SM_VKT_LipGrass","SM_VK_Mushrooms","SM_VK_Crop","SM_VK_Deco_Weeds","SM_VK_Pile","SM_VK_Prop_")
H={}
for o in coll.all_objects:
    if o.type!="MESH" or o.name.startswith(veg): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(b.x for b in bb),max(b.x for b in bb); y0,y1=min(b.y for b in bb),max(b.y for b in bb); z0,z1=min(b.z for b in bb),max(b.z for b in bb)
    if (x1-x0)*(y1-y0)<0.5: continue
    for ci in range(int(x0//6),int(x1//6)+1):
        for cj in range(int(y0//6),int(y1//6)+1): H.setdefault((ci,cj),[]).append((x0,x1,y0,y1,z0,z1,o.name))
hits=[]
for o in coll.all_objects:
    if o.type!="MESH" or not (o.name.startswith("SM_VK_Tree_") or o.name.startswith("SM_VK_Bush_Large")): continue
    x,y,z=o.location
    for e in H.get((int(x//6),int(y//6)),()):
        if e[0]+0.2<x<e[1]-0.2 and e[2]+0.2<y<e[3]-0.2 and e[4]<z+2<e[5]:
            hits.append((o.name,round(x,1),round(y,1),e[6])); break
print(len(hits)); print(hits[:30])
# ---- result ----
# {"result":"Code executed successfully: 0\n[]\n"}

# ==============================================================================================================
# [0037] 2026-09-23 19:18:12  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
coll=bpy.data.collections["VK_ValleyTown"]
towers=[(o.name,o.location.x,o.location.y) for o in coll.all_objects if "Tower_Round" in o.name]
print(len(towers))
near=[]
for o in coll.all_objects:
    if o.type!="MESH" or not o.name.startswith("SM_VK_Tree_"): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    r=0.5*max(max(b.x for b in bb)-min(b.x for b in bb),max(b.y for b in bb)-min(b.y for b in bb))
    for (tn,tx,ty) in towers:
        d=math.hypot(o.location.x-tx,o.location.y-ty)
        if d<r+2.8: near.append((o.name,round(o.location.x,1),round(o.location.y,1),tn,round(d,1),round(r,1)))
    # canopy over wall lines
    x,y=o.location.x,o.location.y
    if 1569<=x<=1689 and abs(y-138)<r-0.5 and o.location.z>3: near.append((o.name,round(x,1),round(y,1),"N-wall",round(abs(y-138),1),round(r,1)))
    if 75<=y<=138 and (abs(x-1569)<r-0.5 or abs(x-1689)<r-0.5): near.append((o.name,round(x,1),round(y,1),"EW-wall",round(min(abs(x-1569),abs(x-1689)),1),round(r,1)))
print(len(near)); 
for n in near[:40]: print(n)
# ---- result ----
# {"result":"Code executed successfully: 12\n0\n"}

# ==============================================================================================================
# [0038] 2026-09-23 19:19:15  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
coll=bpy.data.collections["VK_ValleyTown"]
out=[]
for o in coll.all_objects:
    if o.type!="MESH" or not (o.name.startswith("SM_VK_Tree_") or o.name.startswith("SM_VK_Bush_Large")): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(b.x for b in bb),max(b.x for b in bb); y0,y1=min(b.y for b in bb),max(b.y for b in bb)
    ov=max(1500-x0,x1-1716,0-y0,y1-168)
    if ov>1.0: out.append((round(ov,1),o.name.split("_inst")[0][6:],round(o.location.x,1),round(o.location.y,1)))
out.sort(reverse=True)
print(len(out)); print(out[:25])
# ---- result ----
# {"result":"Code executed successfully: 118\n[(6.6, 'Tree_Pine_B', 1513.5, 167.3), (6.5, 'Tree_Pine_B', 1706.2, 167.6), (6.3, 'Tree_Pine_B', 1653.3, 16
# 7.2), (6.2, 'Tree_Pine_B', 1666.1, 166.8), (5.9, 'Tree_Pine_B', 1624.2, 167.6), (5.9, 'Tree_Pine_B', 1501.2, 137.1), (5.4, 'Tree_Pine_B', 1627.1, 167.
# 0), (5.4, 'Tree_Pine_B', 1501.2, 157.3), (5.2, 'Tree_Pine_A', 1501.2, 167.2), (5.1, 'Tree_Pine_B', 1697.3, 166.3), (5.1, 'Tree_Pine_B', 1522.1, 166.8)
# , (5.1, 'Tree_Pine_B', 1501.0, 124.7), (5.0, 'Tree_Pine_B', 1658.5, 166.5), (5.0, 'Tree_Pine_B', 1507.7, 167.3), (5.0, 'Tree_Pine_A', 1559.2, 167.0), 
# (5.0, 'Tree_Pine_A', 1500.4, 128.3), (4.9, 'Tree_Pine_B', 1715.5, 151.5), (4.9, 'Tree_Pine_B', 1563.5, 167.1), (4.9, 'Tree_Pine_A', 1501.1, 154.6), (4
# .8, 'Tree_Pine_B', 1526.5, 167.1), (4.8, 'Tree_Pine_A', 1715.1, 154.9), (4.8, 'Tree_Pine_A', 1671.3, 166.9), (4.7, 'Tree_Willow', 1714.9, 22.3), (4.7,

# ==============================================================================================================
# [0039] 2026-09-23 19:19:51  blender  ok
# ==============================================================================================================
import bpy, numpy as np
im=bpy.data.images["T_VK_GroundCtl_Town"]
W,H=im.size; px=np.array(im.pixels[:]).reshape(H,W,4)
print(W,H, im.colorspace_settings.name, im.filepath, [ (k,round(float(px[...,k].min()),2),round(float(px[...,k].max()),2)) for k in range(4)])
# print alpha channel map coarse for rows 0..10
for c in range(4):
    vals=np.unique(np.round(px[...,c],2))
    print(c, vals[:20], len(vals))
nt=bpy.data.materials["M_VK_TerrainTown"].node_tree
print([ (l.from_socket.name,l.to_node.name,l.to_node.type, getattr(l.to_node,'operation','')) for l in nt.links if l.from_node.name=="Separate Color.002"])
print([ (l.from_socket.name,l.to_node.name) for l in nt.links if l.from_node.name=="Image Texture.001"])
# ---- result ----
# {"result":"Code executed successfully: 72 56 Non-Color [(0, 0.0, 1.0), (1, 0.0, 1.0), (2, 0.0, 1.0), (3, 0.0, 1.0)]\n0 [0. 0.47 0.59 1. ] 4\n1 [0. 1.]
#  2\n2 [0. 1.] 2\n3 [0. 1.] 2\n[('Blue', 'Math', 'MATH', 'SUBTRACT'), ('Red', 'Math.010', 'MATH', 'SUBTRACT'), ('Green', 'Math.023', 'MATH', 'SUBTRACT'
# )]\n[('Color', 'Separate Color.002'), ('Alpha', 'Map Range.003')]\n"}

# ==============================================================================================================
# [0040] 2026-09-23 19:20:30  blender  ok
# ==============================================================================================================
import bpy, numpy as np
im=bpy.data.images["T_VK_GroundCtl_Town"]
W,H=im.size; px=np.array(im.pixels[:]).reshape(H,W,4)
R=np.round(px[...,0],2)
print("wear120",int((R==0.47).sum()),"wear150",int((R==0.59).sum()),"road",int((R==1).sum()))
nt=bpy.data.materials["M_VK_TerrainTown"].node_tree
n=nt.nodes["Image Texture.001"]; print(n.interpolation, n.extension)
# print a map of rows 0..23 around camp/sites: '.' grass, 'w' 120, 'W' 150, '#' road
for j in range(23,-1,-1):
    print(f"{j:2d} "+"".join({0.0:'.',0.47:'w',0.59:'W',1.0:'#'}.get(float(R[j,i]),'?') for i in range(72)))
# ---- result ----
# {"result":"Code executed successfully: wear120 20 wear150 221 road 182\nLinear EXTEND\n23 .........##..............................##.WWWWWWWWWWWWWWW.
# ............\n22 .........##..............................##.WWWWWWWWWWWWWWW.............\n21 .........##..............................##.WWWWWWWWWWWW
# WWW.............\n20 .........##..............................##.WWWWWWWWWWWWWWW.............\n19 ...w.....##...........................w..##.WWWWWWWW
# WWWWWWW.............\n18 .........##..............................##.............................\n17 .........##..............................##.....
# ........................\n16 .........##..............................##.............................\n15 ............................................
# ............................\n14 ........................................................................\n13 ........................................

# ==============================================================================================================
# [0041] 2026-09-23 19:21:16  blender  ok
# ==============================================================================================================
import bpy
for mn in ("M_VK_RoofRed","M_VK_Roof_Slate","M_VK_Roof_Shingle"):
    nt=bpy.data.materials[mn].node_tree
    print("==",mn)
    for l in nt.links:
        if l.from_node.type in ("OBJECT_INFO","MAP_RANGE","HUE_SAT") or l.to_node.type in("MAP_RANGE","HUE_SAT"):
            print(f"  {l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")
    for n in nt.nodes:
        if n.type=="MAP_RANGE": print("  MR",[(i.name,round(i.default_value,3)) for i in n.inputs[1:5]])
        if n.type=="MIX": print("  MIX",n.name,n.blend_type,[(i.name, (tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) if not i.is_linked else 'L') for i in n.inputs if i.enabled])
# ---- result ----
# {"result":"Code executed successfully: == M_VK_RoofRed\n Image Texture.Color -> Hue/Saturation/Value.Color\n Object Info.Random -> Map Range.Value\n H
# ue/Saturation/Value.Color -> Mix.A\n Map Range.Result -> Mix.B\n MR [('From Min', 0.0), ('From Max', 1.0), ('To Min', 0.94), ('To Max', 1.06)]\n MIX M
# ix MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n MIX Mix.001 MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n== M_VK_Roof_Slate\n Object In
# fo.Random -> Map Range.Value\n Map Range.Result -> Mix.B\n MR [('From Min', 0.0), ('From Max', 1.0), ('To Min', 0.94), ('To Max', 1.06)]\n MIX Mix MUL
# TIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n MIX Mix.001 MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n== M_VK_Roof_Shingle\n Object Info.R
# andom -> Map Range.Value\n Map Range.Result -> Mix.B\n MR [('From Min', 0.0), ('From Max', 1.0), ('To Min', 0.94), ('To Max', 1.06)]\n MIX Mix MULTIPL

# ==============================================================================================================
# [0042] 2026-09-23 19:22:44  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
def colony(name,tx,ty,tz,dist=40,pitch=50,yaw=0,lens=30):
    h=dist*math.cos(math.radians(pitch)); v=dist*math.sin(math.radians(pitch))
    cx=tx-h*math.sin(math.radians(yaw)); cy=ty-h*math.cos(math.radians(yaw))
    return shot(name,(cx,cy,tz+v),(tx,ty,tz),lens=lens,res=(1600,900),outdir=OD)
print(colony("art_24_mine_quarry_bench",1528,96,4,dist=45))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_24_mine_quarry_bench.png\n"}

# ==============================================================================================================
# [0043] 2026-09-23 19:23:38  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\art"
print(shot("art_25_shore_close",(1690,40,10),(1690,50,0),lens=35,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\art\\art_25_shore_close.png\n"}

# ==============================================================================================================
# [0044] 2026-09-23 19:25:14  blender  ok
# ==============================================================================================================
import bpy
for mn in ("M_VK_Soil","M_VK_Foliage","M_VK_Crops","M_VK_Roof_Thatch"):
    m=bpy.data.materials[mn]; nt=m.node_tree
    print("==",mn,"users",m.users)
    for n in nt.nodes:
        if n.type=="MIX": print("  MIX",n.blend_type,[(i.name,(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) if not i.is_linked else 'L') for i in n.inputs if i.enabled])
        if n.type=="TEX_IMAGE": print("  IMG",n.image.name if n.image else None)
        if n.type=="HUE_SAT": print("  HSV",[round(i.default_value,3) for i in n.inputs[:3]])
# ---- result ----
# {"result":"Code executed successfully: == M_VK_Soil users 1800\n IMG T_VK_Soil_BC\n IMG T_VK_Soil_N\n IMG T_VK_Soil_R\n MIX MULTIPLY [('Factor', 1.0),
#  ('A', 'L'), ('B', 'L')]\n== M_VK_Foliage users 1799\n IMG T_VK_Foliage_BCA\n MIX MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n== M_VK_Crops us
# ers 1799\n IMG T_VK_Crops_BCA\n MIX MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n== M_VK_Roof_Thatch users 150\n IMG T_VK_Thatch_BC\n IMG T_VK_
# Thatch_N\n IMG T_VK_Thatch_R\n MIX MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n MIX MULTIPLY [('Factor', 1.0), ('A', 'L'), ('B', 'L')]\n"}
