# village-kit-buildings-continue / agent-aa93fbabc3acab1c2.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:45:58  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_frontier")
b=t.as_string() if t else ""
print(len(src),len(b),src==b, src.rstrip()==b.rstrip())
sc=bpy.data.scenes.get("WS_frontier")
print(sc, [c.name for c in sc.collection.children] if sc else None)
for cn in ("WS_frontier_Pieces","WS_frontier_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, len(c.objects) if c else None)
# ---- result ----
# {"result":"Code executed successfully: 46930 46930 True True\n<bpy_struct, Scene(\"WS_frontier\") at 0x000001CC9DC90088> ['WS_frontier_Pieces', 'WS_fr
# ontier_Assembly']\nWS_frontier_Pieces 31\nWS_frontier_Assembly 185\n"}

# ==============================================================================================================
# [0002] 2026-09-23 15:47:09  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["ws_common"].as_string()
import re
for m in re.finditer(r"^def (\w+)\(([^)]*)\)",s,re.M): print(m.group(1),"(",m.group(2),")")
print(len(s))
# ---- result ----
# {"result":"Code executed successfully: ws_ns ( agent=None )\n_copy_props ( dst,src )\nws_scene ( agent )\nws_owner ( objname )\nws_build ( agent,names
# =None,g=None,row_spacing=None )\nws_grid ( objs,cols=4,sx=6.0,sy=6.0,origin=(0,0 )\nws_clear_assembly ( agent )\nws_shot ( agent,name,loc,target,lens=
# 35,res=(1280,720 )\nws_stats ( objs )\n5974\n"}

# ==============================================================================================================
# [0003] 2026-09-23 15:47:54  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["ws_common"].as_string()
i=s.find("def ws_build"); print(s[i:i+1800])
i=s.find("def ws_shot"); print(s[i:i+1500])
# ---- result ----
# {"result":"Code executed successfully: def ws_build(agent,names=None,g=None,row_spacing=None):\n \"\"\"build every (name,fn,finish_kwargs) in your mod
# ule's WS_SPECS into WS_<agent>_Pieces.\n Refuses names that already exist outside your piece collection (protects the shipped kit).\"\"\"\n g=g or ws_
# ns(agent); sc,coll,asm=ws_scene(agent)\n specs=g.get(\"WS_SPECS\",[]); built=[]\n for n,fn,kw in specs:\n if names and n not in names: continue\n asse
# rt n.startswith(\"SM_VK_\"), n\n own=ws_owner(n)\n if own is not None and own!=[coll.name]:\n raise RuntimeError(f\"{n} already exists in {own}: pick 
# another name\")\n k=g[\"Kit\"](); fn(k)\n for f in k.bm.faces:\n if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)\n tmpn
# =\"__wstmp_\"+agent\n o=k.finish(tmpn,coll,**kw)\n for p in o.data.polygons:\n p.use_smooth=p.material_index in (g[\"HAY\"],g[\"APPLE\"],g[\"PUMPKIN\"

# ==============================================================================================================
# [0004] 2026-09-23 15:48:32  blender  ok
# ==============================================================================================================
import bpy
asm=bpy.data.collections["WS_frontier_Assembly"]
from collections import Counter
near=[(o.name,tuple(round(v,1) for v in o.location)) for o in asm.objects if 13<o.location.x<27 and -17<o.location.y<-3]
for n in near: print(n)
print(bpy.data.objects.get("SM_VK_Crop_Saplings"), bpy.data.objects.get("SM_VK_Prop_GardenBed"), bpy.data.objects.get("SM_VK_Tree_Sapling"),bpy.data.objects.get("SM_VK_Tree_Pine_Young"))
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Wall_Shed_Door_inst', (17.0, -13.0, 0.0))\n('SM_VK_Wall_Shed_Window_inst', (17.0, -10.0, 0.0))\n('SM_VK
# _Wall_Shed_inst', (15.5, -11.5, 0.0))\n('SM_VK_Wall_Shed_Window_inst.001', (18.5, -11.5, 0.0))\n('SM_VK_Corner_Shed_inst', (15.5, -13.0, 0.0))\n('SM_V
# K_Corner_Shed_inst.001', (18.5, -13.0, 0.0))\n('SM_VK_Corner_Shed_inst.002', (18.5, -10.0, 0.0))\n('SM_VK_Corner_Shed_inst.003', (15.5, -10.0, 0.0))\n
# ('SM_VK_RoofThatchS_Single_inst', (17.0, -11.5, 2.6))\n('SM_VK_Deco_Weeds_inst.120', (17.0, -13.0, 0.0))\n('SM_VK_Prop_GardenBed_inst', (20.0, -11.0, 
# 0.0))\n('SM_VK_Prop_GardenBed_inst.001', (23.0, -11.0, 0.0))\n('SM_VK_Tree_Sapling_inst.001', (19.0, -12.3, 0.0))\n('SM_VK_Tree_Pine_Young_inst.073', 
# (20.1, -12.3, 0.0))\n('SM_VK_Tree_Sapling_inst.002', (21.1, -12.4, 0.0))\n('SM_VK_Tree_Pine_Young_inst.074', (22.3, -12.3, 0.0))\n('SM_VK_Tree_Sapling

# ==============================================================================================================
# [0005] 2026-09-23 15:49:38  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
p=ws_shot("frontier","r2_forester",(12,-26,11),(20,-10.5,1.2),lens=35)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\frontier\\r2_forester.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:50:42  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_Prop_GardenBed_inst","SM_VK_Prop_Fence_inst.156","SM_VK_Tree_Sapling_inst.001","SM_VK_Tree_Pine_A_inst.063","SM_VK_Corner_Shed_inst"):
    o=bpy.data.objects[n]
    print(n,o.type,o.hide_render,o.hide_viewport,o.data.name if o.data else None,o.instance_type, o.instance_collection, [c.name for c in o.users_collection], tuple(round(x,2) for x in o.scale), o.parent)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_GardenBed_inst MESH False False SM_VK_Prop_GardenBed NONE None ['WS_frontier_Assembly'] (1.0, 1.0, 1
# .0) None\nSM_VK_Prop_Fence_inst.156 MESH False False SM_VK_Prop_Fence NONE None ['WS_frontier_Assembly'] (1.0, 1.0, 1.0) None\nSM_VK_Tree_Sapling_inst
# .001 MESH False False SM_VK_Tree_Sapling NONE None ['WS_frontier_Assembly'] (1.0, 1.0, 1.0) None\nSM_VK_Tree_Pine_A_inst.063 MESH False False SM_VK_Tr
# ee_Pine_A NONE None ['WS_frontier_Assembly'] (1.0, 1.0, 1.0) None\nSM_VK_Corner_Shed_inst MESH False False VAR_8188543508671540077 NONE None ['WS_fron
# tier_Assembly'] (1.0, 1.0, 1.0) None\n"}

# ==============================================================================================================
# [0007] 2026-09-23 15:51:37  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["WS_frontier"]
print(sc.camera.name, tuple(sc.camera.location), tuple(sc.camera.rotation_euler), sc.camera.data.lens, sc.camera.parent)
print(sc.render.filepath, sc.render.resolution_x)
cams=[o.name for o in sc.objects if o.type=="CAMERA"]; print(cams)
print([ (o.name, tuple(round(v,1) for v in o.location)) for o in sc.objects if o.name.startswith("SM_VK_RoofThatchS_Single")])
print(sc.frame_current, sc.camera.animation_data)
# ---- result ----
# {"result":"Code executed successfully: WS_frontier_Cam (12.0, -26.0, 11.0) (1.0589101314544678, -3.776156631829508e-08, -0.4764673709869385) 35.0 None
# \nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-
# 2026-09-23-d49817\\renders2\\frontier\\r2_forester.png 1280\n['WS_frontier_Cam']\n[('SM_VK_RoofThatchS_Single', (-18.0, 14.0, 0.0)), ('SM_VK_RoofThatc
# hS_Single_inst', (17.0, -11.5, 2.6))]\n1 None\n"}

# ==============================================================================================================
# [0008] 2026-09-23 15:52:41  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["WS_frontier"]; vl=sc.view_layers[0]
for n in ("SM_VK_Prop_GardenBed_inst","SM_VK_Prop_Fence_inst.156","SM_VK_Tree_Sapling_inst.001","SM_VK_Tree_Pine_A_inst.063","SM_VK_Corner_Shed_inst"):
    o=bpy.data.objects[n]
    print(n,o.visible_get(view_layer=vl),len(o.data.polygons),o.visible_camera, [ (m.name,m.show_render) for m in o.modifiers], tuple(round(v,1) for v in o.matrix_world.translation), o.data.materials[0].name if o.data.materials else None)
print(sc.render.use_simplify, sc.render.simplify_subdivision_render)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_GardenBed_inst True 392 True [] (0.0, 0.0, 0.0) M_VK_Stone\nSM_VK_Prop_Fence_inst.156 True 472 True 
# [] (0.0, 0.0, 0.0) M_VK_Stone\nSM_VK_Tree_Sapling_inst.001 True 570 True [] (0.0, 0.0, 0.0) M_VK_Wood\nSM_VK_Tree_Pine_A_inst.063 True 4590 True [] (0
# .0, 0.0, 0.0) M_VK_BarkOak\nSM_VK_Corner_Shed_inst True 140 True [] (0.0, 0.0, 0.0) M_VK_Stone_Field\nFalse 0\n"}

# ==============================================================================================================
# [0009] 2026-09-23 15:53:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
o=bpy.data.objects["SM_VK_Tree_Pine_A"]; print(tuple(round(d,1) for d in o.dimensions))
p=ws_shot("frontier","r2_forester_low",(21,-24,3.5),(20,-11,1.0),lens=30,samples=16)
# ---- result ----
# {"result":"Code executed successfully: (8.0, 8.0, 10.3)\n"}

# ==============================================================================================================
# [0010] 2026-09-23 15:53:30  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["WS_frontier"]
dg=bpy.context.evaluated_depsgraph_get() if bpy.context.scene==sc else None
print(bpy.context.scene.name)
asm=bpy.data.collections["WS_frontier_Assembly"]
o=bpy.data.objects["SM_VK_Prop_Fence_inst.156"]
print(o.location, o.rotation_euler, o.delta_location, o.matrix_basis.translation, o.matrix_parent_inverse.translation)
t=bpy.data.objects["SM_VK_Tree_Pine_A_inst.063"]; print(t.location, t.delta_location)
# any other objects whose location near nursery
m=bpy.data.objects["SM_VK_Prop_Fence"]; print(m.location, m.dimensions, [c.name for c in m.users_collection])
# ---- result ----
# {"result":"Code executed successfully: VillageKit\n<Vector (23.0000, -13.0000, 0.0000)> <Euler (x=0.0000, y=0.0000, z=0.0000), order='XYZ'> <Vector (0
# .0000, 0.0000, 0.0000)> <Vector (23.0000, -13.0000, 0.0000)> <Vector (0.0000, 0.0000, 0.0000)>\n<Vector (23.4000, -8.0000, 0.0000)> <Vector (0.0000, 0
# .0000, 0.0000)>\n<Vector (0.0000, 0.0000, 0.0000)> <Vector (3.1784, 0.2803, 1.1814)> ['VK_Pieces']\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:54:07  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_Tree_Sapling","SM_VK_Tree_Pine_Young","SM_VK_Tree_Pine_A","SM_VK_Prop_GardenBed","SM_VK_Prop_Fence","SM_VK_Bush_A","SM_VK_Bush_Small"):
    o=bpy.data.objects.get(n)
    print(n, tuple(round(d,2) for d in o.dimensions) if o else None)
print([o.name for o in bpy.data.objects if o.name.startswith("SM_VK_Tree_") and "_inst" not in o.name][:60])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Sapling (2.64, 2.85, 3.82)\nSM_VK_Tree_Pine_Young (4.93, 4.94, 5.33)\nSM_VK_Tree_Pine_A (8.03, 7.97,
#  10.33)\nSM_VK_Prop_GardenBed (2.8, 1.6, 0.47)\nSM_VK_Prop_Fence (3.18, 0.28, 1.18)\nSM_VK_Bush_A None\nSM_VK_Bush_Small None\n['SM_VK_Tree_Apple', 'S
# M_VK_Tree_Birch', 'SM_VK_Tree_Birch_Single', 'SM_VK_Tree_Blossom', 'SM_VK_Tree_Dead', 'SM_VK_Tree_Oak_A', 'SM_VK_Tree_Oak_Autumn', 'SM_VK_Tree_Oak_B',
#  'SM_VK_Tree_Pine_A', 'SM_VK_Tree_Pine_B', 'SM_VK_Tree_Pine_Young', 'SM_VK_Tree_Sapling', 'SM_VK_Tree_Willow']\n"}

# ==============================================================================================================
# [0012] 2026-09-23 15:55:37  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_Log_Fallen","SM_VK_Prop_Sawhorse","SM_VK_Prop_ChoppingBlock","SM_VK_Pile_Logs_3","SM_VK_Pile_Logs_2","SM_VK_Chimney_Gable_H30","SM_VK_Stockpile_Border","SM_VK_Pile_Sacks_2","SM_VK_Pile_Planks_2","SM_VK_Pile_Stone_1","SM_VK_Pile_Planks_1","SM_VK_Prop_Wheelbarrow","SM_VK_Prop_Signpost","SM_VK_LeanTo","SM_VK_Porch","SM_VK_Tree_Pine_B","SM_VK_Prop_Woodpile","SM_VK_Crop_Saplings","SM_VK_Prop_Axe","SM_VK_Prop_Lantern"):
    o=bpy.data.objects.get(n)
    print(n, tuple(round(d,2) for d in o.dimensions) if o else None, [c.name for c in o.users_collection] if o else "")
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Log_Fallen (3.48, 1.72, 0.95) ['VK_NaturePieces']\nSM_VK_Prop_Sawhorse (1.71, 0.89, 1.2) ['WS_constructio
# n_Pieces']\nSM_VK_Prop_ChoppingBlock (1.59, 1.41, 0.99) ['WS_construction_Pieces']\nSM_VK_Pile_Logs_3 (2.95, 1.85, 1.48) ['WS_construction_Pieces']\nS
# M_VK_Pile_Logs_2 (2.95, 1.85, 0.9) ['WS_construction_Pieces']\nSM_VK_Chimney_Gable_H30 (1.94, 1.49, 9.3) ['WS_skyline_Pieces']\nSM_VK_Stockpile_Border
#  (2.93, 2.92, 0.42) ['WS_construction_Pieces']\nSM_VK_Pile_Sacks_2 (1.71, 1.69, 0.71) ['WS_construction_Pieces']\nSM_VK_Pile_Planks_2 (2.9, 1.95, 0.63
# ) ['WS_construction_Pieces']\nSM_VK_Pile_Stone_1 (2.7, 1.0, 0.47) ['WS_construction_Pieces']\nSM_VK_Pile_Planks_1 (2.9, 1.95, 0.34) ['WS_construction_
# Pieces']\nSM_VK_Prop_Wheelbarrow (2.2, 0.73, 0.84) ['WS_construction_Pieces']\nSM_VK_Prop_Signpost (1.96, 1.88, 2.8) ['VK_Pieces']\nSM_VK_LeanTo (3.4,

# ==============================================================================================================
# [0013] 2026-09-23 15:57:26  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_Tree_Pine_Young","SM_VK_Tree_Sapling","SM_VK_Crop_Cabbage"):
    me=bpy.data.objects[n].data
    used=sorted({p.material_index for p in me.polygons})
    print(n,[(i,me.materials[i].name) for i in used])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Pine_Young [(0, 'M_VK_BarkOak'), (1, 'M_VK_BarkPine'), (2, 'M_VK_Leaves')]\nSM_VK_Tree_Sapling [(0, 
# 'M_VK_Wood'), (1, 'M_VK_Burlap'), (2, 'M_VK_BarkOak'), (3, 'M_VK_Leaves')]\nSM_VK_Crop_Cabbage [(8, 'M_VK_Leaf'), (26, 'M_VK_Soil'), (31, 'M_VK_Foliag
# e')]\n"}

# ==============================================================================================================
# [0014] 2026-09-23 15:59:41  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_Prop_Barrel","SM_VK_Prop_Crates","SM_VK_Prop_Sacks","SM_VK_Plant_TallGrass","SM_VK_Deco_Weeds","SM_VK_Prop_Trough","SM_VK_Stump","SM_VK_Prop_Cart","SM_VK_Prop_FlowerBox_Daisy","SM_VK_Prop_BarrelStack","SM_VK_Prop_Grindstone"):
    o=bpy.data.objects.get(n); print(n, tuple(round(d,2) for d in o.dimensions) if o else None)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Barrel None\nSM_VK_Prop_Crates (2.5, 1.76, 1.5)\nSM_VK_Prop_Sacks (1.12, 1.02, 1.27)\nSM_VK_Plant_Ta
# llGrass (1.69, 1.95, 1.06)\nSM_VK_Deco_Weeds (3.18, 0.74, 0.57)\nSM_VK_Prop_Trough (2.02, 0.9, 0.73)\nSM_VK_Stump (1.71, 1.77, 0.86)\nSM_VK_Prop_Cart 
# (3.3, 1.74, 1.42)\nSM_VK_Prop_FlowerBox_Daisy (1.45, 0.54, 0.9)\nSM_VK_Prop_BarrelStack (1.92, 1.16, 1.5)\nSM_VK_Prop_Grindstone (0.95, 0.84, 1.32)\n"
# }

# ==============================================================================================================
# [0015] 2026-09-23 16:00:18  blender  ok
# ==============================================================================================================
import bpy,time
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
t0=time.time()
H_push(); g=ws_ns("frontier")
objs=ws_build("frontier",names=["SM_VK_Crop_TreeNursery"],g=g)
print(ws_stats(objs))
H_clear(g); H_layout(g); H_demos(g)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Crop_TreeNursery', 'tris': 1772, 'bbox': [2.92, 2.9, 1.62], 'zmin': 0.0, 'mats': [2, 8, 25, 26
# , 34, 35]}]\n1.7612721920013428\n"}

# ==============================================================================================================
# [0016] 2026-09-23 16:00:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","r3_forester",(12,-24,9),(20.5,-10.5,1.0),lens=32,samples=24)
ws_shot("frontier","r3_woodcutter",(-6,-22,10),(1,-9,1.5),lens=32,samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0017] 2026-09-23 16:01:28  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
H_push(); g=ws_ns("frontier")
objs=ws_build("frontier",names=["SM_VK_Crop_TreeNursery"],g=g)
ws_shot("frontier","r3_nursery",(21.5,-17,3.2),(21.5,-11.5,0.6),lens=35,samples=24)
ws_shot("frontier","r3_woodcutter_w",(14,-20,12),(1.5,-9,1.0),lens=30,samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0018] 2026-09-23 16:02:35  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
H_push(); g=ws_ns("frontier")
objs=ws_build("frontier",names=["SM_VK_Crop_TreeNursery"],g=g)
print(ws_stats(objs))
ws_shot("frontier","r4_nursery",(21.5,-17.5,4.5),(21.5,-11.5,0.6),lens=35,samples=24)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Crop_TreeNursery', 'tris': 1964, 'bbox': [2.98, 2.94, 1.45], 'zmin': 0.0, 'mats': [2, 25, 26, 
# 31, 34, 35, 37]}]\n"}

# ==============================================================================================================
# [0019] 2026-09-23 16:02:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","r4_storehouse",(-14,-54,14),(-29,-38,1.5),lens=30,samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0020] 2026-09-23 16:03:25  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
objs=[o for o in bpy.data.collections["WS_frontier_Pieces"].objects]
print(len(objs), sorted((round(o.location.x),round(o.location.y)) for o in objs)[:3], max(o.location.x for o in objs), min(o.location.y for o in objs))
# ---- result ----
# {"result":"Code executed successfully: 32 [(-50, 5), (-50, 14), (-50, 23)] -10.0 5.0\n"}

# ==============================================================================================================
# [0021] 2026-09-23 16:03:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","catalog_v2",(-30,-14,28),(-30,27,0),lens=32,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0022] 2026-09-23 16:05:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","r4_cabins",(-27,-34,16),(-27,-9,1.5),lens=35,samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0023] 2026-09-23 16:05:47  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
asm=bpy.data.collections["WS_frontier_Assembly"]
for o in asm.objects:
    if -27<o.location.x<-21 and -15<o.location.y<-5: print(o.name, tuple(round(v,2) for v in o.location), round(o.rotation_euler.z*57.3), o.data.name)
ws_shot("frontier","r4_cabin3_gable",(-33,-19,5),(-25,-10,2.5),lens=35,samples=24)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Log_B_inst.003 (-22.5, -8.5, 0.0) -90 VAR_2439444060177573098\nSM_VK_Deco_Weeds_inst.113 (-22.5, -8.
# 5, 0.0) -90 SM_VK_Deco_Weeds\nSM_VK_Wall_Log_B_inst.004 (-22.5, -11.5, 0.0) -90 VAR_2439444060177573098\nSM_VK_Corner_Log_inst.002 (-22.5, -13.0, 0.0)
#  0 VAR_2932023380666753566\nSM_VK_Corner_Log_B_inst.003 (-22.5, -7.0, 0.0) -90 VAR_2099652382302074792\nSM_VK_Chimney_Gable_H30_inst.003 (-22.5, -10.0
# , 0.0) -90 VAR_2335659333375879813\nSM_VK_Prop_Woodpile_inst.009 (-23.5, -8.6, 0.0) -90 SM_VK_Prop_Woodpile.001\nSM_VK_Stump_inst.002 (-22.44, -14.6, 
# 0.0) 104 SM_VK_Stump\n"}

# ==============================================================================================================
# [0024] 2026-09-23 16:06:42  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
H_push(); g=ws_ns("frontier")
H_clear(g); H_layout(g); H_demos(g)
ws_shot("frontier","r5_cabins_back",(-42,6,9),(-30,-9,1.5),lens=32,samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0025] 2026-09-23 16:07:45  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g,objs,dt=H_all(build=False,demos=True)
print(dt)
# ---- result ----
# {"result":"Code executed successfully: 1.53\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:08:13  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","r6_colony",(0,-29,33),(0,2,0),lens=35,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0027] 2026-09-23 16:08:49  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g,objs,dt=H_all(build=False,demos=True)
ws_shot("frontier","r7_colony",(0,-26,32.2),(0,1,0),lens=24,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0028] 2026-09-23 16:09:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","hero_colony",(-14,-26,37),(0,2,0),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0029] 2026-09-23 16:10:31  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","hero_colony",(-12,-31,37),(1,-1.5,0),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0030] 2026-09-23 16:10:54  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","hero_hamlet",(-27,-30,13),(-2,-1,1.5),lens=32,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0031] 2026-09-23 16:11:48  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("frontier","hero_yard",(24,-20,9),(5,4,1.5),lens=32,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0032] 2026-09-23 16:12:25  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
pcs=list(bpy.data.collections["WS_frontier_Pieces"].objects)
for o in pcs: o.hide_render=True
try:
    ws_shot("frontier","hero_yard",(25,-7,9.5),(3,10,1.8),lens=30,res=(1600,900))
finally:
    for o in pcs: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0033] 2026-09-23 16:13:17  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py",encoding="utf8").read()
print("text==file:", bpy.data.texts["ws_frontier"].as_string()==src)
g=ws_ns("frontier")
objs=ws_build("frontier",g=g)
print(len(objs), round(time.time()-t0,2))
st=ws_stats(objs)
for s in st: print(s["name"],s["tris"],s["bbox"],s["zmin"])
# ---- result ----
# {"result":"Code executed successfully: text==file: True\n32 2.76\nSM_VK_Wall_Log 1512 [3.0, 0.53, 3.64] -0.6\nSM_VK_Wall_Log_Window 2502 [3.0, 0.9, 3.
# 64] -0.6\nSM_VK_Wall_Log_Door 2566 [3.0, 1.44, 3.64] -0.6\nSM_VK_Wall_Log_B 1512 [3.0, 0.55, 3.81] -0.6\nSM_VK_Wall_Log_B_Window 2502 [3.0, 0.9, 3.81]
#  -0.6\nSM_VK_Wall_Log_B_Door 2566 [3.0, 1.44, 3.81] -0.6\nSM_VK_Corner_Log 1106 [0.89, 0.94, 3.64] -0.6\nSM_VK_Corner_Log_B 1106 [0.87, 0.95, 3.64] -0
# .6\nSM_VK_Roof_Gable_Logs 5542 [4.16, 9.04, 5.44] -0.7\nSM_VK_Wall_Shed 1304 [3.09, 0.46, 3.21] -0.61\nSM_VK_Wall_Shed_Door 1766 [3.09, 1.02, 3.21] -0
# .61\nSM_VK_Wall_Shed_Wide 2154 [3.09, 1.25, 3.21] -0.61\nSM_VK_Wall_Shed_Window 1814 [3.09, 0.78, 3.21] -0.61\nSM_VK_Corner_Shed 272 [0.55, 0.55, 3.22
# ] -0.61\nSM_VK_Wall_Shed_Raised 1012 [3.09, 0.33, 2.73] -0.13\nSM_VK_Wall_Shed_Door_Raised 1474 [3.09, 0.96, 2.73] -0.13\nSM_VK_Corner_Shed_Raised 196

# ==============================================================================================================
# [0034] 2026-09-23 16:14:41  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g=ws_ns("frontier")
H_clear(g); objs=H_layout(g); H_demos(g)
print(len(objs), len(bpy.data.collections["WS_frontier_Assembly"].objects))
ws_shot("frontier","catalog_v3",(-60,6,28),(-60,44.5,0),lens=26,res=(1600,900),samples=16)
# ---- result ----
# {"result":"Code executed successfully: 32 172\n"}

# ==============================================================================================================
# [0035] 2026-09-23 16:15:40  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["WS_frontier"]
for o in sc.collection.objects: print(o.name,o.type,tuple(round(v,1) for v in o.location),tuple(round(v,1) for v in o.dimensions))
# ---- result ----
# {"result":"Code executed successfully: VK_Sun LIGHT (0.0, 0.0, 0.0) (0.0, 0.0, 0.0)\nWS_frontier_Ground MESH (0.0, 0.0, 0.0) (120.0, 120.0, 0.0)\nWS_f
# rontier_Cam CAMERA (-60.0, 6.0, 28.0) (0.0, 0.0, 0.0)\n"}

# ==============================================================================================================
# [0036] 2026-09-23 16:16:13  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g=ws_ns("frontier"); H_layout(g)
asm=list(bpy.data.collections["WS_frontier_Assembly"].objects)
for o in asm: o.hide_render=True
try:
    ws_shot("frontier","catalog_v4",(0,-8,27),(0,33.5,0),lens=26,res=(1600,900),samples=16)
finally:
    for o in asm: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0037] 2026-09-23 16:17:10  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g=ws_ns("frontier"); H_layout(g)
asm=list(bpy.data.collections["WS_frontier_Assembly"].objects)
for o in asm: o.hide_render=True
try:
    ws_shot("frontier","catalog_v5",(16,4,29),(-0.5,37,0),lens=30,res=(1600,900),samples=16)
finally:
    for o in asm: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0038] 2026-09-23 16:18:41  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g=ws_ns("frontier"); H_layout(g)
H_catalog("catalog_v6",samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0039] 2026-09-23 16:19:22  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g=ws_ns("frontier"); H_layout(g)
H_catalog("catalog_v7",samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0040] 2026-09-23 16:20:10  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
asm=list(bpy.data.collections["WS_frontier_Assembly"].objects)
for o in asm: o.hide_render=True
try: ws_shot("frontier","r8_roofs_side",(22,40,6),(8,49.5,1.8),lens=35,samples=16)
finally:
    for o in asm: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0041] 2026-09-23 16:21:31  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py",encoding="utf8").read()
print("text==file:", bpy.data.texts["ws_frontier"].as_string()==src)
g=ws_ns("frontier")
objs=ws_build("frontier",g=g)
print("built",len(objs),"of",len(g["WS_SPECS"]), round(time.time()-t0,2),"s")
# ---- result ----
# {"result":"Code executed successfully: text==file: True\nbuilt 32 of 32 3.0 s\n"}

# ==============================================================================================================
# [0042] 2026-09-23 16:22:14  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
g=ws_ns("frontier")
H_clear(g); H_layout(g)
sc,coll,asm=ws_scene("frontier")
for k_,(fn,o,kw) in DEMOS.items():
    n0=len(asm.objects); ret=g[fn](asm,o,**kw); print(k_,fn,o,kw,"->",ret,len(asm.objects)-n0,"objs")
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: cabin2 build_logcabin (-13, -8, 0) {'seed': 1, 'n': 2} -> {'wall_top': 3.0, 'footprint': (2, 2)} 27 objs\nfores
# ter build_forester_hut (0, -8, 0) {'seed': 0} -> {'wall_top': 2.6, 'footprint': (3, 2)} 22 objs\ncabin3 build_logcabin (14, -8, 0) {'seed': 4, 'n': 3}
#  -> {'wall_top': 3.0, 'footprint': (3, 2)} 31 objs\nwoodcutter build_woodcutter (-15, 8, 0) {'seed': 0} -> {'wall_top': 3.0, 'footprint': (3, 3)} 31 o
# bjs\nstorehouse build_storehouse (0, 12, 0) {'seed': 0} -> {'wall_top': 4.2, 'footprint': (3, 2), 'yard': (3, 2)} 30 objs\ngranary build_granary (13, 
# 8, 0) {'seed': 0} -> {'wall_top': 3.365, 'footprint': (2, 2)} 31 objs\n172\n"}

# ==============================================================================================================
# [0043] 2026-09-23 16:22:56  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("frontier"); sc,coll,asm=ws_scene("frontier")
before=set(asm.objects)
try:
    g["build_woodcutter"](asm,(40,40,math.pi/2),seed=0)
    g["build_forester_hut"](asm,(40,20,math.pi),seed=0)
    new=[o for o in asm.objects if o not in before]
    for o in new:
        if "Chimney" in o.name or "LeanTo" in o.name or "Wall_Shed_Door" in o.name: print(o.name, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z)))
finally:
    for o in [o for o in asm.objects if o not in before]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.name.startswith("VAR_") and me.users==0: bpy.data.meshes.remove(me)
print(len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Chimney_Gable_H30_inst.005 (38.5, 35.5, 0.0) 0\nSM_VK_LeanTo_inst.011 (38.5, 41.5, 0.0) 180\nSM_VK_Wall_S
# hed_Door_inst.002 (43.0, 23.0, 0.0) 180\n172\n"}

# ==============================================================================================================
# [0044] 2026-09-23 16:23:15  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
print(H_catalog("catalog_final"))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\frontier\\catalog_final.png\n"}

# ==============================================================================================================
# [0045] 2026-09-23 16:24:06  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
print(H_hero("hero_colony",(-12,-31,37),(1,-1.5,0),lens=30))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\frontier\\hero_colony.png\n"}

# ==============================================================================================================
# [0046] 2026-09-23 16:24:49  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
print(H_hero("hero_hamlet",(-27,-30,13),(-2,-1,1.5),lens=32))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\frontier\\hero_hamlet.png\n"}

# ==============================================================================================================
# [0047] 2026-09-23 16:24:52  blender  ok
# ==============================================================================================================
import bpy
exec(open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\frontier\_fro_harness.py",encoding="utf8").read())
print(H_hero("hero_yard",(25,-7,9.5),(3,10,1.8),lens=30))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\frontier\\hero_yard.png\n"}

# ==============================================================================================================
# [0048] 2026-09-23 16:26:03  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_frontier.py",encoding="utf8").read()
print("text==file:", bpy.data.texts["ws_frontier"].as_string()==src)
P=bpy.data.collections["WS_frontier_Pieces"].objects; A=bpy.data.collections["WS_frontier_Assembly"].objects
print(len(P),sum(o.hide_render for o in P),len(A),sum(o.hide_render for o in A))
print([m.name for m in bpy.data.materials if "WS_frontier" in m.name])
# ---- result ----
# {"result":"Code executed successfully: text==file: True\n32 0 172 0\n[]\n"}
