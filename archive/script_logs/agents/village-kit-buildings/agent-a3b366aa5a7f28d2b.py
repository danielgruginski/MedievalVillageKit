# village-kit-buildings / agent-a3b366aa5a7f28d2b.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 12:54:16  blender  ok
# ==============================================================================================================
import bpy
print(bpy.app.version_string)
print([t.name for t in bpy.data.texts])
print([s.name for s in bpy.data.scenes])
names=["SM_VK_Wall_Log","SM_VK_Corner_Log","SM_VK_RoofS_Mid","SM_VK_Wall_Shed","SM_VK_Prop_StaddleStone","SM_VK_Wall_Posts"]
print({n:(bpy.data.objects.get(n) is not None) for n in names})
print([i.name for i in bpy.data.images if "Roof" in i.name or "Shingle" in i.name or "End" in i.name][:30])
# ---- result ----
# {"result":"Code executed successfully: 4.4.3\n['mc_helpers', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_leafgen', 'vk_mat', 'vk_nature', 'vk_tex
# ', 'vk_tex2', 'vk_texgen', 'wk_helpers', 'ws_common']\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n{'SM_VK_Wa
# ll_Log': False, 'SM_VK_Corner_Log': False, 'SM_VK_RoofS_Mid': False, 'SM_VK_Wall_Shed': False, 'SM_VK_Prop_StaddleStone': False, 'SM_VK_Wall_Posts': F
# alse}\n['T_VK_EndGrain_AO', 'T_VK_EndGrain_BC', 'T_VK_EndGrain_H', 'T_VK_EndGrain_N', 'T_VK_EndGrain_R', 'T_VK_RoofBlue_BC', 'T_VK_RoofBlue_N', 'T_VK_
# RoofBlue_R', 'T_VK_RoofGreen_BC', 'T_VK_RoofGreen_N', 'T_VK_RoofGreen_R', 'T_VK_RoofRed_BC', 'T_VK_RoofRed_N', 'T_VK_RoofRed_R', 'T_VK_RoofShingle_AO'
# , 'T_VK_RoofShingle_BC', 'T_VK_RoofShingle_H', 'T_VK_RoofShingle_N', 'T_VK_RoofShingle_R', 'T_VK_RoofSlate_AO', 'T_VK_RoofSlate_BC', 'T_VK_RoofSlate_H

# ==============================================================================================================
# [0002] 2026-09-23 12:56:57  blender  ok
# ==============================================================================================================
import bpy
for n in ["T_VK_EndGrain_BC","T_VK_Wood_BC","T_VK_Planks_BC","T_VK_RoofShingle_BC","T_VK_BarkPine_BC","T_VK_Thatch_BC"]:
    im=bpy.data.images.get(n)
    print(n, im and (im.filepath_raw, tuple(im.size)))
print([i.name for i in bpy.data.images if "Bark" in i.name][:20])
for m in ["M_VK_EndGrain","M_VK_BarkOak","M_VK_BarkPine","M_VK_Wood"]:
    mm=bpy.data.materials.get(m)
    if mm: print(m,[ (n.type, getattr(n,'image',None) and n.image.name) for n in mm.node_tree.nodes if n.type=='TEX_IMAGE'])
print([o.name for o in bpy.data.objects if "Stump" in o.name or "Log" in o.name][:30])
# ---- result ----
# {"result":"Code executed successfully: T_VK_EndGrain_BC ('C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-
# 4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\VillageKit\\\\Textures\\\\T_VK_EndGrain_BC.png', (512, 
# 512))\nT_VK_Wood_BC ('C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f
# 8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\VillageKit\\\\Textures\\\\T_VK_Wood_BC.png', (1024, 1024))\nT_VK_Planks_BC ('C:\\\\Users\\\
# \danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratc
# h-2026-09-23-d49817\\\\VillageKit\\\\Textures\\\\T_VK_Planks_BC.png', (1024, 1024))\nT_VK_RoofShingle_BC ('C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\

# ==============================================================================================================
# [0003] 2026-09-23 13:10:07  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_frontier") or bpy.data.texts.new("ws_frontier"); t.clear(); t.write(src)
t0=time.time()
g=ws_ns("frontier")
names=["SM_VK_Wall_Log","SM_VK_Wall_Log_Window","SM_VK_Wall_Log_Door","SM_VK_Wall_Log_B","SM_VK_Corner_Log","SM_VK_Corner_Log_B","SM_VK_Roof_Gable_Logs"]
objs=ws_build("frontier",names=names,g=g)
print(time.time()-t0)
for s in ws_stats(objs): print(s)
# ---- result ----
# {"result":"Code executed successfully: 0.4529893398284912\n{'name': 'SM_VK_Wall_Log', 'tris': 2200, 'bbox': [3.0, 0.53, 3.64], 'zmin': -0.6, 'mats': [
# 0, 1, 2, 45]}\n{'name': 'SM_VK_Wall_Log_Window', 'tris': 3318, 'bbox': [3.0, 0.9, 3.64], 'zmin': -0.6, 'mats': [0, 1, 2, 4, 5, 10, 40, 45]}\n{'name': 
# 'SM_VK_Wall_Log_Door', 'tris': 3486, 'bbox': [3.0, 1.44, 3.64], 'zmin': -0.6, 'mats': [0, 1, 2, 5, 23, 27, 40, 45]}\n{'name': 'SM_VK_Wall_Log_B', 'tri
# s': 2200, 'bbox': [3.0, 0.55, 3.8], 'zmin': -0.6, 'mats': [0, 1, 2, 45]}\n{'name': 'SM_VK_Corner_Log', 'tris': 1164, 'bbox': [0.89, 0.94, 3.8], 'zmin'
# : -0.6, 'mats': [0, 2, 40, 45]}\n{'name': 'SM_VK_Corner_Log_B', 'tris': 1164, 'bbox': [0.87, 0.95, 3.8], 'zmin': -0.6, 'mats': [0, 2, 40, 45]}\n{'name
# ': 'SM_VK_Roof_Gable_Logs', 'tris': 8292, 'bbox': [4.16, 9.04, 5.45], 'zmin': -0.7, 'mats': [1, 2, 3, 4, 40]}\n"}

# ==============================================================================================================
# [0004] 2026-09-23 13:10:37  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
sc,coll,asm=ws_scene("frontier")
ws_clear_assembly("frontier")
objs=[o for o in coll.objects]
ws_grid(objs,cols=4,sx=7,sy=7)
O=(40,0,0); st={"roof":"Shingle","stone":"Field","shutter":"Red"}
P=lambda n,x,y,z,r,s=st: g["place_v"](asm,n,x,y,z,r,O,s)
P("SM_VK_Wall_Log_Door",-1.5,-3,0,0); P("SM_VK_Wall_Log_Window",1.5,-3,0,0)
P("SM_VK_Wall_Log",1.5,3,0,180); P("SM_VK_Wall_Log_Window",-1.5,3,0,180)
P("SM_VK_Wall_Log_B",-3,-1.5,0,-90); P("SM_VK_Wall_Log_B",-3,1.5,0,-90)
P("SM_VK_Wall_Log_B",3,-1.5,0,90); P("SM_VK_Wall_Log_B",3,1.5,0,90)
for (x,y,r) in ((-3,-3,0),(3,-3,90),(3,3,180),(-3,3,-90)):
    P("SM_VK_Corner_Log" if r in (0,180) else "SM_VK_Corner_Log_B",x,y,0,r)
P("SM_VK_Roof_Gable_Logs",-1.5,0,3.0,180); P("SM_VK_Roof_Gable_Logs",1.5,0,3.0,0)
p=ws_shot("frontier","cabin_v1",(40-11,-13,6.5),(40,0,2.6),lens=35)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\frontier\\cabin_v1.png\n"}

# ==============================================================================================================
# [0005] 2026-09-23 13:11:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("frontier","cabin_v1_close",(40-2.5,-8.5,6.0),(40-1.0,-3.0,3.6),lens=45)
p=ws_shot("frontier","cabin_v1_wide",(40-14,-17,10),(40,0,3.2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0006] 2026-09-23 13:12:47  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_frontier") or bpy.data.texts.new("ws_frontier"); t.clear(); t.write(src)
t0=time.time()
g=ws_ns("frontier")
objs=ws_build("frontier",g=g)
print(round(time.time()-t0,2))
for s in ws_stats(objs): print(s["name"],s["tris"],s["bbox"],s["zmin"])
ws_grid(objs,cols=6,sx=8,sy=9)
# ---- result ----
# {"result":"Code executed successfully: 1.62\nSM_VK_Wall_Log 1512 [3.0, 0.53, 3.64] -0.6\nSM_VK_Wall_Log_Window 2502 [3.0, 0.9, 3.64] -0.6\nSM_VK_Wall_
# Log_Door 2566 [3.0, 1.44, 3.64] -0.6\nSM_VK_Wall_Log_B 1512 [3.0, 0.55, 3.81] -0.6\nSM_VK_Wall_Log_B_Window 2502 [3.0, 0.9, 3.81] -0.6\nSM_VK_Wall_Log
# _B_Door 2566 [3.0, 1.44, 3.81] -0.6\nSM_VK_Corner_Log 1106 [0.89, 0.94, 3.64] -0.6\nSM_VK_Corner_Log_B 1106 [0.87, 0.95, 3.64] -0.6\nSM_VK_Roof_Gable_
# Logs 6966 [4.16, 9.04, 5.45] -0.7\nSM_VK_Wall_Shed 1304 [3.09, 0.46, 3.21] -0.61\nSM_VK_Wall_Shed_Door 1766 [3.09, 1.02, 3.21] -0.61\nSM_VK_Wall_Shed_
# Wide 2154 [3.09, 1.25, 3.21] -0.61\nSM_VK_Wall_Shed_Window 1814 [3.09, 0.78, 3.21] -0.61\nSM_VK_Corner_Shed 272 [0.55, 0.55, 3.22] -0.61\nSM_VK_Wall_S
# hed_Raised 1012 [3.09, 0.33, 2.73] -0.13\nSM_VK_Wall_Shed_Door_Raised 1474 [3.09, 0.96, 2.73] -0.13\nSM_VK_Corner_Shed_Raised 196 [0.42, 0.42, 2.74] -

# ==============================================================================================================
# [0007] 2026-09-23 13:13:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("frontier","catalog_v1",(20,-44,26),(20,-14,1.5),lens=32)
p=ws_shot("frontier","cabin_v2",(40-14,-17,10),(40,0,3.2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0008] 2026-09-23 13:14:03  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
sc,coll,asm=ws_scene("frontier")
rz=g["roof_z"]
for o in asm.objects:
    if "Roof" in o.name: continue
    M=o.matrix_world; hits=[]
    for v in o.data.vertices:
        p=M@v.co
        lx=p.x-40; ay=abs(p.y)
        if abs(lx)<3.9 and ay<4.3 and p.z>3.0+rz(ay)-0.05:
            hits.append((round(p.x,2),round(p.y,2),round(p.z,2)))
    if hits: print(o.name,len(hits),hits[:4])
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0009] 2026-09-23 13:14:17  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
rz=g["roof_z"]
o=bpy.data.objects["SM_VK_Roof_Gable_Logs"]
me=o.data
hits={}
for p in me.polygons:
    c=p.center
    if c.x<2.3 and abs(c.y)>0.4 and abs(c.y)<4.3 and c.z>rz(abs(c.y))+0.08:
        hits.setdefault(p.material_index,[]).append((round(c.x,2),round(c.y,2),round(c.z,2)))
for k_,v in hits.items(): print(k_,len(v),v[:6])
# ---- result ----
# {"result":"Code executed successfully: 3 175 [(-1.25, -4.2, -0.15), (-0.75, -4.2, -0.15), (-0.25, -4.2, -0.14), (0.75, -4.22, -0.15), (1.25, -4.21, -0
# .16), (1.75, -4.21, -0.16)]\n"}

# ==============================================================================================================
# [0010] 2026-09-23 13:14:51  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
rz=g["roof_z"]; rs=g["roof_sag"]
o=bpy.data.objects["SM_VK_Roof_Gable_Logs"]
me=o.data
hits={}
for v in me.vertices:
    c=v.co
    if c.x<2.45 and abs(c.y)>0.5 and abs(c.y)<4.3 and c.z>rz(abs(c.y))+rs(c.x,abs(c.y))-0.03:
        hits.setdefault(round(c.x,1),[]).append((round(c.x,2),round(c.y,2),round(c.z,2)))
for k_,v in sorted(hits.items()): print(k_,len(v),v[:5])
# ---- result ----
# {"result":"Code executed successfully: -1.5 33 [(-1.5, -0.75, 3.17), (-1.5, -1.5, 2.22), (-1.5, -2.25, 1.28), (-1.5, -3.0, 0.33), (-1.5, -3.45, 0.12)]
# \n-1.4 32 [(-1.44, -4.01, -0.06), (-1.38, -4.01, -0.06), (-1.44, -3.99, -0.12), (-1.38, -3.99, -0.12), (-1.44, -3.78, 0.06)]\n-1.3 28 [(-1.31, -4.01, 
# -0.06), (-1.31, -3.99, -0.12), (-1.34, -3.78, 0.06), (-1.31, -3.78, 0.06), (-1.28, -3.78, 0.06)]\n-1.2 32 [(-1.25, -4.01, -0.06), (-1.19, -4.01, -0.06
# ), (-1.25, -3.99, -0.12), (-1.19, -3.99, -0.12), (-1.25, -3.78, 0.06)]\n-1.1 24 [(-1.12, -4.01, -0.06), (-1.06, -4.01, -0.06), (-1.12, -3.99, -0.12), 
# (-1.06, -3.99, -0.12), (-1.12, -3.78, 0.06)]\n-1.0 31 [(-1.01, -0.75, 3.19), (-1.01, -1.5, 2.24), (-1.01, -2.25, 1.28), (-1.01, -3.0, 0.33), (-1.01, -
# 3.45, 0.12)]\n-0.9 24 [(-0.94, -4.01, -0.06), (-0.88, -4.01, -0.06), (-0.94, -3.99, -0.12), (-0.88, -3.99, -0.12), (-0.94, -3.78, 0.06)]\n-0.8 32 [(-0

# ==============================================================================================================
# [0011] 2026-09-23 13:15:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("frontier","chip_probe",(41.5,-8.0,4.2),(42.0,-3.6,3.3),lens=40)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0012] 2026-09-23 13:17:00  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
rz=g["roof_z"]; rs=g["roof_sag"]
o=bpy.data.objects["SM_VK_Roof_Gable_Logs"]
for p in o.data.polygons:
    if p.material_index==40:
        c=p.center; top=rz(abs(c.y))+rs(c.x,abs(c.y))
        print(round(c.x,2),round(c.y,2),round(c.z,2),"roof",round(top,2), "POKE" if c.z+0.15>top-0.05 else "")
# ---- result ----
# {"result":"Code executed successfully: 1.59 -2.7 0.31 roof 0.7 \n1.59 2.7 0.31 roof 0.7 \n1.59 -2.46 0.62 roof 1.01 \n1.59 2.46 0.62 roof 1.01 \n1.59 
# -2.23 0.92 roof 1.3 \n1.59 2.23 0.92 roof 1.3 \n1.59 -2.0 1.21 roof 1.59 \n1.59 -0.34 1.21 roof 3.69 \n1.59 0.34 1.21 roof 3.69 \n1.59 2.0 1.21 roof 1
# .59 \n1.59 -1.76 1.51 roof 1.89 \n1.59 -0.34 1.51 roof 3.69 \n1.59 0.34 1.51 roof 3.69 \n1.59 1.76 1.51 roof 1.89 \n1.59 -1.52 1.82 roof 2.19 \n1.59 1
# .52 1.82 roof 2.19 \n1.59 -1.3 2.11 roof 2.48 \n1.59 1.3 2.11 roof 2.48 \n1.59 -1.06 2.41 roof 2.78 \n1.59 1.06 2.41 roof 2.78 \n1.59 -0.82 2.72 roof 
# 3.08 \n1.59 0.82 2.72 roof 3.08 \n1.59 -0.59 3.02 roof 3.37 \n1.59 0.59 3.02 roof 3.37 \n1.59 -0.36 3.31 roof 3.66 \n1.59 0.36 3.31 roof 3.66 \n2.57 0
# .0 3.52 roof 4.18 \n2.57 -1.56 1.53 roof 2.18 \n2.57 1.56 1.53 roof 2.18 \n"}

# ==============================================================================================================
# [0013] 2026-09-23 13:17:49  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
sc,coll,asm=ws_scene("frontier")
mine={n for n,_,_ in g["WS_SPECS"]}
def fro_clear():
    stale=set()
    for o in list(asm.objects):
        base=o.name.split("_inst")[0]
        if o.data and o.data.name.startswith("VAR_") and base in mine: stale.add(o.data.name)
        bpy.data.objects.remove(o)
    n=0
    for mn in stale:
        me=bpy.data.meshes.get(mn)
        if me and me.users==0: bpy.data.meshes.remove(me); n+=1
    return n
print("purged",fro_clear())
O=(40,0,0); st={"roof":"Shingle","stone":"Field","shutter":"Red"}
P=lambda n,x,y,z,r,s=st: g["place_v"](asm,n,x,y,z,r,O,s)
P("SM_VK_Wall_Log_Door",-1.5,-3,0,0); P("SM_VK_Wall_Log_Window",1.5,-3,0,0)
P("SM_VK_Wall_Log",1.5,3,0,180); P("SM_VK_Wall_Log_Window",-1.5,3,0,180)
P("SM_VK_Wall_Log_B",-3,-1.5,0,-90); P("SM_VK_Wall_Log_B_Window",-3,1.5,0,-90)
P("SM_VK_Wall_Log_B_Door",3,-1.5,0,90); P("SM_VK_Wall_Log_B",3,1.5,0,90)
for (x,y,r) in ((-3,-3,0),(3,-3,90),(3,3,180),(-3,3,-90)):
    P("SM_VK_Corner_Log" if r in (0,180) else "SM_VK_Corner_Log_B",x,y,0,r)
P("SM_VK_Roof_Gable_Logs",-1.5,0,3.0,180); P("SM_VK_Roof_Gable_Logs",1.5,0,3.0,0)
# a Daub-chinked variant cabin wall row for the seam test (3 modules + corners)
st2={"roof":"Shingle","stone":"Field","shutter":"Green","plaster":"Daub"}
for i,c in enumerate(["SM_VK_Wall_Log","SM_VK_Wall_Log_Window","SM_VK_Wall_Log_Door"]):
    P(c,-3+1.5+3*i+10,-3,0,0,st2)
P("SM_VK_Corner_Log",7,-3,0,0,st2); P("SM_VK_Corner_Log_B",16,-3,0,90,st2)
P("SM_VK_Wall_Log_B",7,-1.5,0,-90,st2); P("SM_VK_Wall_Log_B_Door",16,-1.5,0,90,st2)
p=ws_shot("frontier","cabin_v3",(40-14,-17,10),(40,0,3.2),lens=35)
p=ws_shot("frontier","seam_v1",(40+11.5,-12,5),(40+11.5,-3,1.6),lens=35)
# ---- result ----
# {"result":"Code executed successfully: purged 7\n"}

# ==============================================================================================================
# [0014] 2026-09-23 13:18:41  blender  ERROR
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
sc,coll,asm=ws_scene("frontier")
pv=g["place_v"]
def shed_box(O,n,faces,roof,st,H=2.6,wall="Shed",corner="SM_VK_Corner_Shed",single=None):
    L=n*3.0
    for i,c in enumerate(faces["F"]): pv(asm,wall[c],-L/2+1.5+3*i,-1.5,0,0,O,st)
    for i,c in enumerate(faces["B"]): pv(asm,wall[c],L/2-1.5-3*i,1.5,0,180,O,st)
    pv(asm,wall[faces["L"]],-L/2,0,0,-90,O,st); pv(asm,wall[faces["R"]],L/2,0,0,90,O,st)
    for (x,y,r) in ((-L/2,-1.5,0),(L/2,-1.5,90),(L/2,1.5,180),(-L/2,1.5,-90)): pv(asm,corner,x,y,0,r,O,st)
    if n==1: pv(asm,single,0,0,H,0,O,st)
    else:
        for i in range(n):
            x=-L/2+1.5+3*i
            pv(asm,roof[1] if i in (0,n-1) else roof[0],x,0,H,180 if i==0 else 0,O,st)
W={".":"SM_VK_Wall_Shed","D":"SM_VK_Wall_Shed_Door","B":"SM_VK_Wall_Shed_Wide","W":"SM_VK_Wall_Shed_Window"}
st={"roof":"Shingle"}
shed_box((62,0,0),1,{"F":"D","B":".","L":"W","R":"."},None,st,single="SM_VK_RoofS_Single")
shed_box((72,0,0),3,{"F":"BWD","B":"...","L":".","R":"W"},("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable_Planks"),{"roof":"Red"})
# open post bay 2x1 with thatch S roof
O=(84,0,0); L=6.0
for i in range(2):
    pv(asm,"SM_VK_Wall_Posts",-L/2+1.5+3*i,-1.5,0,0,O,{}); pv(asm,"SM_VK_Wall_Posts",L/2-1.5-3*i,1.5,0,180,O,{})
for (x,y,r) in ((-L/2,-1.5,0),(L/2,-1.5,90),(L/2,1.5,180),(-L/2,1.5,-90)): pv(asm,"SM_VK_Corner_Posts",x,y,0,r,O,{})
for i in range(2): pv(asm,"SM_VK_RoofThatchS_Gable",-L/2+1.5+3*i,0,3.0,180 if i==0 else 0,O,{})
# timber S gable on a 2x1 shed with thatch single next to it
shed_box((62,-9,0),2,{"F":"DW","B":"..","L":".","R":"."},("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable"),{"roof":"Blue"})
shed_box((72,-9,0),1,{"F":"D","B":".","L":".","R":"W"},None,{},single="SM_VK_RoofThatchS_Single")
p=ws_shot("frontier","sheds_v1",(58,-24,11),(74,-3,2),lens=35)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: string indices must be integers, not 'str'"}

# ==============================================================================================================
# [0015] 2026-09-23 13:19:30  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
sc,coll,asm=ws_scene("frontier")
pv=g["place_v"]
for o in list(asm.objects):
    if o.location.x>55: bpy.data.objects.remove(o)
W={".":"SM_VK_Wall_Shed","D":"SM_VK_Wall_Shed_Door","B":"SM_VK_Wall_Shed_Wide","W":"SM_VK_Wall_Shed_Window"}
def shed_box(O,n,faces,roof,st,H=2.6,corner="SM_VK_Corner_Shed",single=None):
    L=n*3.0
    for i,c in enumerate(faces["F"]): pv(asm,W[c],-L/2+1.5+3*i,-1.5,0,0,O,st)
    for i,c in enumerate(faces["B"]): pv(asm,W[c],L/2-1.5-3*i,1.5,0,180,O,st)
    pv(asm,W[faces["L"]],-L/2,0,0,-90,O,st); pv(asm,W[faces["R"]],L/2,0,0,90,O,st)
    for (x,y,r) in ((-L/2,-1.5,0),(L/2,-1.5,90),(L/2,1.5,180),(-L/2,1.5,-90)): pv(asm,corner,x,y,0,r,O,st)
    if n==1: pv(asm,single,0,0,H,0,O,st)
    else:
        for i in range(n):
            x=-L/2+1.5+3*i
            pv(asm,roof[1] if i in (0,n-1) else roof[0],x,0,H,180 if i==0 else 0,O,st)
shed_box((62,0,0),1,{"F":"D","B":".","L":"W","R":"."},None,{"roof":"Shingle"},single="SM_VK_RoofS_Single")
shed_box((72,0,0),3,{"F":"BWD","B":"...","L":".","R":"W"},("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable_Planks"),{"roof":"Red"})
O=(84,0,0); L=6.0
for i in range(2):
    pv(asm,"SM_VK_Wall_Posts",-L/2+1.5+3*i,-1.5,0,0,O,{}); pv(asm,"SM_VK_Wall_Posts",L/2-1.5-3*i,1.5,0,180,O,{})
for (x,y,r) in ((-L/2,-1.5,0),(L/2,-1.5,90),(L/2,1.5,180),(-L/2,1.5,-90)): pv(asm,"SM_VK_Corner_Posts",x,y,0,r,O,{})
for i in range(2): pv(asm,"SM_VK_RoofThatchS_Gable",-L/2+1.5+3*i,0,3.0,180 if i==0 else 0,O,{})
shed_box((62,-9,0),2,{"F":"DW","B":"..","L":".","R":"."},("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable"),{"roof":"Blue"})
shed_box((72,-9,0),1,{"F":"D","B":".","L":".","R":"W"},None,{},single="SM_VK_RoofThatchS_Single")
p=ws_shot("frontier","sheds_v1",(58,-24,11),(74,-3,2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0016] 2026-09-23 13:20:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier")
sc,coll,asm=ws_scene("frontier")
pv=g["place_v"]
mine={n for n,_,_ in g["WS_SPECS"]}
def fro_clear():
    stale=set()
    for o in list(asm.objects):
        base=o.name.split("_inst")[0]
        if o.data and o.data.name.startswith("VAR_") and base in mine: stale.add(o.data.name)
        bpy.data.objects.remove(o)
    for mn in stale:
        me=bpy.data.meshes.get(mn)
        if me and me.users==0: bpy.data.meshes.remove(me)
fro_clear()
objs=[bpy.data.objects[n] for n,_,_ in g["WS_SPECS"]]
ws_grid(objs,cols=6,sx=8,sy=9,origin=(-50,50))
W={".":"SM_VK_Wall_Shed","D":"SM_VK_Wall_Shed_Door","B":"SM_VK_Wall_Shed_Wide","W":"SM_VK_Wall_Shed_Window"}
def shed_box(O,n,faces,roof,st,H=2.6,corner="SM_VK_Corner_Shed",single=None):
    L=n*3.0
    for i,c in enumerate(faces["F"]): pv(asm,W[c],-L/2+1.5+3*i,-1.5,0,0,O,st)
    for i,c in enumerate(faces["B"]): pv(asm,W[c],L/2-1.5-3*i,1.5,0,180,O,st)
    pv(asm,W[faces["L"]],-L/2,0,0,-90,O,st); pv(asm,W[faces["R"]],L/2,0,0,90,O,st)
    for (x,y,r) in ((-L/2,-1.5,0),(L/2,-1.5,90),(L/2,1.5,180),(-L/2,1.5,-90)): pv(asm,corner,x,y,0,r,O,st)
    if n==1: pv(asm,single,0,0,H,0,O,st)
    else:
        for i in range(n):
            x=-L/2+1.5+3*i
            pv(asm,roof[1] if i in (0,n-1) else roof[0],x,0,H,180 if i==0 else 0,O,st)
X0,Y0=-30,-30
shed_box((X0,Y0,0),1,{"F":"D","B":".","L":"W","R":"."},None,{"roof":"Shingle"},single="SM_VK_RoofS_Single")
shed_box((X0+10,Y0,0),3,{"F":"BWD","B":"...","L":".","R":"W"},("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable_Planks"),{"roof":"Red"})
O=(X0+22,Y0,0); L=6.0
for i in range(2):
    pv(asm,"SM_VK_Wall_Posts",-L/2+1.5+3*i,-1.5,0,0,O,{}); pv(asm,"SM_VK_Wall_Posts",L/2-1.5-3*i,1.5,0,180,O,{})
for (x,y,r) in ((-L/2,-1.5,0),(L/2,-1.5,90),(L/2,1.5,180),(-L/2,1.5,-90)): pv(asm,"SM_VK_Corner_Posts",x,y,0,r,O,{})
for i in range(2): pv(asm,"SM_VK_RoofThatchS_Gable",-L/2+1.5+3*i,0,3.0,180 if i==0 else 0,O,{})
shed_box((X0,Y0-9,0),2,{"F":"DW","B":"..","L":".","R":"."},("SM_VK_RoofS_Mid","SM_VK_RoofS_Gable"),{"roof":"Blue"})
shed_box((X0+10,Y0-9,0),1,{"F":"D","B":".","L":".","R":"W"},None,{},single="SM_VK_RoofThatchS_Single")
p=ws_shot("frontier","sheds_v2",(X0-4,Y0-24,10),(X0+10,Y0-3,1.8),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0017] 2026-09-23 13:20:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
X0,Y0=-30,-30
p=ws_shot("frontier","shed1_close",(X0-6.5,Y0-8.5,3.8),(X0,Y0,1.7),lens=35)
p=ws_shot("frontier","shed3_close",(X0+19,Y0-8,4.2),(X0+10,Y0,1.8),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0018] 2026-09-23 13:21:26  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
X0,Y0=-30,-30
p=ws_shot("frontier","thatchS_close",(X0+17,Y0-17,4.5),(X0+13,Y0-8,1.8),lens=35)
p=ws_shot("frontier","posts_close",(X0+28,Y0-8.5,3.5),(X0+22,Y0,1.8),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0019] 2026-09-23 13:22:51  blender  ok
# ==============================================================================================================
import bpy
names=sorted({o.name for o in bpy.data.objects if o.name.startswith("SM_VK_") and "_inst" not in o.name and not o.name.startswith("SM_VK_Wall_Log") })
print(len(names))
print([n for n in names if any(s in n for s in ("Tree","Sapl","Stump","Log","Bush","Grass","Rock","Plant","Fern","Flower","Mush","Pile","Crop","Chop","Saw"))])
for n in ["SM_VK_Stump","SM_VK_Log_Fallen","SM_VK_LeanTo","SM_VK_Prop_Woodpile","SM_VK_Porch"]:
    o=bpy.data.objects.get(n)
    if o: print(n,[c.name for c in o.users_collection],[round(d,2) for d in o.dimensions], len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: 426\n['SM_VK_Bridge_Log', 'SM_VK_Bush_Autumn', 'SM_VK_Bush_Berry', 'SM_VK_Bush_Hydrangea', 'SM_VK_Bush_Large', 
# 'SM_VK_Bush_Round', 'SM_VK_Corner_Log', 'SM_VK_Corner_Log_B', 'SM_VK_Crop_Cabbage', 'SM_VK_Crop_Cabbage_cat', 'SM_VK_Crop_Carrot', 'SM_VK_Crop_Carrot_
# cat', 'SM_VK_Crop_Lavender', 'SM_VK_Crop_Lavender_cat', 'SM_VK_Crop_Pumpkin', 'SM_VK_Crop_Pumpkin_cat', 'SM_VK_Crop_Wheat', 'SM_VK_Crop_Wheat_cat', 'S
# M_VK_Deco_Bush', 'SM_VK_Deco_Bush_cat', 'SM_VK_Log_Fallen', 'SM_VK_Mushrooms_Brown', 'SM_VK_Mushrooms_Glow', 'SM_VK_Mushrooms_Red', 'SM_VK_Pile_Bricks
# _1', 'SM_VK_Pile_Bricks_2', 'SM_VK_Pile_Bricks_3', 'SM_VK_Pile_Coal_1', 'SM_VK_Pile_Coal_2', 'SM_VK_Pile_Coal_3', 'SM_VK_Pile_Fish_1', 'SM_VK_Pile_Fis
# h_2', 'SM_VK_Pile_Fish_3', 'SM_VK_Pile_Ore_1', 'SM_VK_Pile_Ore_2', 'SM_VK_Pile_Ore_3', 'SM_VK_Plant_Fern', 'SM_VK_Plant_Reeds', 'SM_VK_Plant_TallGrass

# ==============================================================================================================
# [0020] 2026-09-23 13:26:03  blender  ERROR
# ==============================================================================================================
HP=r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6\scratchpad\fro_harness.py"
exec(open(HP,encoding="utf8").read())
g,objs,dt=H_all()
print(dt)
for s in ws_stats(objs):
    if s["name"] in ("SM_VK_Roof_Gable_Logs","SM_VK_RoofS_Gable","SM_VK_RoofS_Single","SM_VK_RoofS_Gable_Planks","SM_VK_RoofThatchS_Single"): print(s["name"],s["tris"])
p=ws_shot("frontier","demos_v1",(0,-52,26),(0,-12,1.5),lens=30)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: [Errno 2] No such file or directory: 'C:\\\\Users\\\\danie\\\
# \AppData\\\\Local\\\\Temp\\\\claude\\\\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c
# 6-98db-14b97d4348ea-scratch-2026-09-23-d49817\\\\421a57cc-0ba3-43b1-888d-34ef79f58bc6\\\\scratchpad\\\\fro_harness.py'"}

# ==============================================================================================================
# [0021] 2026-09-23 13:26:53  blender  ok
# ==============================================================================================================
HP=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py"
exec(open(HP,encoding="utf8").read())
g,objs,dt=H_all()
print(dt)
for s in ws_stats(objs):
    if s["name"] in ("SM_VK_Roof_Gable_Logs","SM_VK_RoofS_Gable","SM_VK_RoofS_Single","SM_VK_RoofS_Gable_Planks","SM_VK_RoofThatchS_Single"): print(s["name"],s["tris"])
p=ws_shot("frontier","demos_v1",(0,-52,26),(0,-12,1.5),lens=30)
# ---- result ----
# {"result":"Code executed successfully: 2.44\nSM_VK_Roof_Gable_Logs 5542\nSM_VK_RoofS_Gable 4202\nSM_VK_RoofS_Gable_Planks 4292\nSM_VK_RoofS_Single 611
# 6\nSM_VK_RoofThatchS_Single 5296\n"}

# ==============================================================================================================
# [0022] 2026-09-23 13:27:57  blender  ok
# ==============================================================================================================
HP=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py"
exec(open(HP,encoding="utf8").read())
for key in ("woodcutter","forester","granary","storehouse"):
    fn,o,kw=DEMOS[key]
    ws_shot("frontier","d1_"+key,(o[0]-11,o[1]-17,10),(o[0],o[1],1.8),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0023] 2026-09-23 13:28:46  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["WS_frontier"]; asm=bpy.data.collections["WS_frontier_Assembly"]
for o in asm.objects:
    if 14<o.location.x<27 and -16<o.location.y<-5: print(o.name, tuple(round(v,2) for v in o.location), o.data.name)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Shed_Door_inst (17.0, -13.0, 0.0) VAR_3037526848936951903\nSM_VK_Wall_Shed_Window_inst (17.0, -10.0,
#  0.0) VAR_7128794848897768865\nSM_VK_Wall_Shed_inst (15.5, -11.5, 0.0) VAR_363792222211583156\nSM_VK_Wall_Shed_Window_inst.001 (18.5, -11.5, 0.0) VAR_
# 7128794848897768865\nSM_VK_Corner_Shed_inst (15.5, -13.0, 0.0) VAR_8188543508671540077\nSM_VK_Corner_Shed_inst.001 (18.5, -13.0, 0.0) VAR_818854350867
# 1540077\nSM_VK_Corner_Shed_inst.002 (18.5, -10.0, 0.0) VAR_8188543508671540077\nSM_VK_Corner_Shed_inst.003 (15.5, -10.0, 0.0) VAR_8188543508671540077\
# nSM_VK_RoofThatchS_Single_inst (17.0, -11.5, 2.6) VAR_3218238595382985158\nSM_VK_Deco_Weeds_inst.120 (17.0, -13.0, 0.0) SM_VK_Deco_Weeds\nSM_VK_Prop_G
# ardenBed_inst (20.0, -11.0, 0.0) SM_VK_Prop_GardenBed\nSM_VK_Prop_GardenBed_inst.001 (23.0, -11.0, 0.0) SM_VK_Prop_GardenBed\nSM_VK_Tree_Sapling_inst.

# ==============================================================================================================
# [0024] 2026-09-23 13:30:01  blender  ok
# ==============================================================================================================
import bpy
for n in ["SM_VK_Prop_Fence_inst.156","SM_VK_Prop_GardenBed_inst","SM_VK_Tree_Sapling_inst.001","SM_VK_Wall_Shed_Door_inst"]:
    o=bpy.data.objects.get(n)
    print(n, o.hide_render, o.hide_viewport, [c.name for c in o.users_collection], tuple(round(v,2) for v in o.dimensions), len(o.data.polygons), o.scale[:], o.parent)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Fence_inst.156 False False ['WS_frontier_Assembly'] (3.18, 0.28, 1.18) 472 (1.0, 1.0, 1.0) None\nSM_
# VK_Prop_GardenBed_inst False False ['WS_frontier_Assembly'] (2.8, 1.6, 0.47) 392 (1.0, 1.0, 1.0) None\nSM_VK_Tree_Sapling_inst.001 False False ['WS_fr
# ontier_Assembly'] (2.64, 2.85, 3.82) 570 (1.0, 1.0, 1.0) None\nSM_VK_Wall_Shed_Door_inst False False ['WS_frontier_Assembly'] (3.09, 1.02, 3.21) 1003 
# (1.0, 1.0, 1.0) None\n"}
