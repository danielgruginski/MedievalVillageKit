# village-kit-buildings-continue / agent-a727ba2132fe4f265.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 15:46:07  blender  ok
# ==============================================================================================================
import bpy, hashlib
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry")
ts=t.as_string() if t else None
print("file",len(src),hashlib.md5(src.encode()).hexdigest())
print("text",len(ts) if ts else None,hashlib.md5(ts.encode()).hexdigest() if ts else None, ts==src if ts else None)
sc=bpy.data.scenes.get("WS_industry"); print(sc)
for cn in ("WS_industry_Pieces","WS_industry_Assembly"):
    c=bpy.data.collections.get(cn); print(cn, len(c.objects) if c else None)
c=bpy.data.collections.get("WS_industry_Pieces")
print(sorted(o.name for o in c.objects) if c else None)
# ---- result ----
# {"result":"Code executed successfully: file 87228 d5663e83e9e4a7208c3e8bdda4f14de7\ntext 87228 d5663e83e9e4a7208c3e8bdda4f14de7 True\n<bpy_struct, Sce
# ne(\"WS_industry\") at 0x000001CC5FCF0088>\nWS_industry_Pieces 49\nWS_industry_Assembly 165\n['SM_VK_Kiln_Oast', 'SM_VK_Mine_Portal', 'SM_VK_Pile_Bric
# ks_1', 'SM_VK_Pile_Bricks_2', 'SM_VK_Pile_Bricks_3', 'SM_VK_Pile_Coal_1', 'SM_VK_Pile_Coal_2', 'SM_VK_Pile_Coal_3', 'SM_VK_Pile_Hides_1', 'SM_VK_Pile_
# Hides_2', 'SM_VK_Pile_Hides_3', 'SM_VK_Pile_Ore_1', 'SM_VK_Pile_Ore_2', 'SM_VK_Pile_Ore_3', 'SM_VK_Pile_Wool_1', 'SM_VK_Pile_Wool_2', 'SM_VK_Pile_Wool
# _3', 'SM_VK_Prop_Banker', 'SM_VK_Prop_BeeBench', 'SM_VK_Prop_Bellows', 'SM_VK_Prop_Bloomery', 'SM_VK_Prop_BottleKiln', 'SM_VK_Prop_Cauldron', 'SM_VK_P
# rop_CharcoalMound', 'SM_VK_Prop_CiderPress', 'SM_VK_Prop_ClayPit', 'SM_VK_Prop_ClothRack', 'SM_VK_Prop_Dovecote', 'SM_VK_Prop_DryingRack_Herbs', 'SM_V

# ==============================================================================================================
# [0002] 2026-09-23 15:47:09  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["ws_common"].as_string()
print(len(s)); print(s[:6000])
# ---- result ----
# {"result":"Code executed successfully: 5974\n# ===================== WORKSHOP HELPERS (shared, read-only for agents) =====================\n# Usage in
#  any execute_blender_code call:\n# exec(bpy.data.texts[\"ws_common\"].as_string()); g=ws_ns(\"hovel\") # kit namespace + your module\nimport bpy, os, 
# math, json\nfrom mathutils import Vector\nWS_RENDERS=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a5
# 6c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\n\ndef ws_ns(agent=None):\n \"\"\"fresh namespace with the whole v
# illage kit (vk_helpers) + your module text 'ws_<agent>' executed on top\"\"\"\n g={}\n exec(bpy.data.texts[\"vk_helpers\"].as_string(),g)\n if agent:\
# n t=bpy.data.texts.get(\"ws_\"+agent)\n if t: exec(t.as_string(),g)\n return g\n\ndef _copy_props(dst,src):\n for p in src.bl_rna.properties:\n if p.i

# ==============================================================================================================
# [0003] 2026-09-23 15:47:55  blender  ok
# ==============================================================================================================
import bpy
from collections import defaultdict
c=bpy.data.collections["WS_industry_Assembly"]
objs=list(c.objects)
# cluster by rough location
cl=defaultdict(list)
for o in objs:
    key=(round(o.location.x/20)*20, round(o.location.y/20)*20)
    cl[key].append(o.name)
for k,v in sorted(cl.items()):
    print(k,len(v),sorted(set(n.split('.')[0] for n in v))[:12])
p=bpy.data.collections["WS_industry_Pieces"]
print([(o.name,tuple(round(x,1) for x in o.location),o.hide_render) for o in list(p.objects)[:5]])
# ---- result ----
# {"result":"Code executed successfully: (-40, 20) 13 ['SM_VK_LeanTo_inst', 'SM_VK_Mine_Portal_inst', 'SM_VK_Pile_Coal_2_inst', 'SM_VK_Pile_Ore_1_inst',
#  'SM_VK_Prop_BarrelStack_inst', 'SM_VK_Prop_Crates_inst', 'SM_VK_Prop_Minecart_inst', 'SM_VK_Prop_Woodpile_inst', 'SM_VK_Rail_Curve_inst', 'SM_VK_Rail
# _End_inst', 'SM_VK_Rail_Straight_inst']\n(-40, 40) 25 ['SM_VK_Corner_Plaster_inst', 'SM_VK_Deco_Ivy_B_inst', 'SM_VK_Deco_Weeds_inst', 'SM_VK_LeanTo_in
# st', 'SM_VK_Pile_Hides_3_inst', 'SM_VK_Porch_inst', 'SM_VK_Prop_Cauldron_inst', 'SM_VK_Prop_FlowerBox_inst', 'SM_VK_Prop_HideFrame_inst', 'SM_VK_Prop_
# Planter_inst', 'SM_VK_Prop_TanningPit_inst', 'SM_VK_Prop_Trough_inst']\n(-40, 60) 11 ['SM_VK_Corner_Plaster_inst', 'SM_VK_Deco_Weeds_inst', 'SM_VK_Lea
# nTo_inst', 'SM_VK_Pile_Hides_1_inst', 'SM_VK_Prop_BarrelStack_inst', 'SM_VK_Prop_FlowerBox_inst', 'SM_VK_Wall_Plaster_Window_inst', 'SM_VK_Wall_Plaste

# ==============================================================================================================
# [0004] 2026-09-23 15:49:05  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry", g=g)
print(len(objs), round(time.time()-t0,1))
st=ws_stats(objs)
for s in st: print(s['name'],s['tris'],s['bbox'],s['zmin'])
# ---- result ----
# {"result":"Code executed successfully: 49 3.2\nSM_VK_Mine_Portal 3998 [8.94, 7.91, 6.15] -1.0\nSM_VK_Rail_Straight 324 [3.0, 1.6, 0.53] -0.3\nSM_VK_Ra
# il_Curve 1056 [3.84, 3.84, 0.53] -0.3\nSM_VK_Rail_End 1104 [3.59, 1.69, 1.2] -0.3\nSM_VK_Prop_Minecart 1640 [1.79, 0.98, 1.27] -0.03\nSM_VK_Pile_Ore_1
#  556 [1.76, 1.47, 0.61] -0.04\nSM_VK_Pile_Ore_2 784 [2.57, 2.03, 0.81] -0.04\nSM_VK_Pile_Ore_3 1140 [3.16, 2.62, 1.2] -0.04\nSM_VK_Pile_Coal_1 536 [2.
# 09, 1.32, 0.68] -0.1\nSM_VK_Pile_Coal_2 860 [2.75, 2.15, 0.85] -0.05\nSM_VK_Pile_Coal_3 1412 [3.39, 2.72, 0.89] -0.04\nSM_VK_Quarry_Face_Straight 1096
#  [3.0, 3.17, 4.15] -0.6\nSM_VK_Quarry_Face_Corner 1244 [3.08, 3.21, 4.12] -0.6\nSM_VK_Quarry_Face_InnerCorner 1104 [3.07, 3.12, 4.06] -0.6\nSM_VK_Quar
# ry_Floor 1252 [2.98, 2.98, 1.37] -0.61\nSM_VK_Prop_Banker 860 [1.73, 1.36, 1.46] -0.01\nSM_VK_Prop_TreadwheelCrane 1892 [9.74, 4.03, 9.26] -0.05\nSM_V

# ==============================================================================================================
# [0005] 2026-09-23 15:49:37  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
c=bpy.data.collections["WS_industry_Pieces"]
g=ws_ns("industry")
names=[s[0] for s in g["WS_SPECS"]]
objs=[bpy.data.objects[n] for n in names]
ws_grid(objs,cols=7,sx=9,sy=9,origin=(-27,-6))
p=ws_shot("industry","cat_check_a",(0,-78,40),(0,-30,0),lens=32)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\industry\\cat_check_a.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 15:50:29  blender  ok
# ==============================================================================================================
import bpy, time, math, traceback
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
L=[("build_mine",(-36,24,0)),("build_quarry_yard",(-12,26,0)),("build_charcoal_burner",(12,24,0)),("build_pottery",(36,24,0)),
   ("build_tannery",(-36,52,0)),("build_dyers_yard",(-12,52,0)),("build_brewery",(12,52,0)),("build_apiary",(38,52,0))]
t0=time.time()
for fn,o in L:
    try:
        g[fn](asm,o,seed=0); print(fn,"ok",len(asm.objects))
    except Exception as e:
        print(fn,"ERR",traceback.format_exc()[-600:])
print(round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: build_mine ok 14\nbuild_quarry_yard ok 35\nbuild_charcoal_burner ok 46\nbuild_pottery ok 55\nbuild_tannery ok 9
# 2\nbuild_dyers_yard ok 103\nbuild_brewery ok 154\nbuild_apiary ok 165\n0.1\n"}

# ==============================================================================================================
# [0007] 2026-09-23 15:50:45  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
p=ws_shot("industry","mine_asm_v2",(-36+13,24-19,11),(-36+1.5,24-0.5,1.2),lens=35)
p=ws_shot("industry","quarry_asm_v2",(-12+15,26-20,14),(-12,26+1.5,1.0),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0008] 2026-09-23 15:52:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","a_brewery_v1",(12+14,52-22,15),(12+1.5,52,2.0),lens=35)
ws_shot("industry","a_apiary_v1",(38+7,52-10,6),(38,52-0.5,0.8),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0009] 2026-09-23 15:53:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for n in ["SM_VK_Roof_Vent","SM_VK_Pile_Logs_3","SM_VK_Pile_Stone_3","SM_VK_Prop_Wheelbarrow","SM_VK_Emblem_Ridge_Tankard","SM_VK_Prop_ShopGoods_Pots","SM_VK_Crop_Hops","SM_VK_Prop_Woodpile","SM_VK_LeanTo","SM_VK_Prop_Trough","SM_VK_Crop_Lavender","SM_VK_Prop_Laundry","SM_VK_RoofThatch_Vent"]:
    o=bpy.data.objects.get(n)
    if o: print(n, ws_stats([o])[0], [c.name for c in o.users_collection])
    else: print(n,"MISSING")
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Vent {'name': 'SM_VK_Roof_Vent', 'tris': 932, 'bbox': [1.75, 0.94, 1.75], 'zmin': -0.69, 'mats': [2,
#  3, 23, 27]} ['WS_skyline_Pieces']\nSM_VK_Pile_Logs_3 {'name': 'SM_VK_Pile_Logs_3', 'tris': 1080, 'bbox': [2.95, 1.85, 1.48], 'zmin': -0.1, 'mats': [3
# 3, 40]} ['WS_construction_Pieces']\nSM_VK_Pile_Stone_3 {'name': 'SM_VK_Pile_Stone_3', 'tris': 1416, 'bbox': [2.7, 1.0, 1.18], 'zmin': 0.0, 'mats': [2,
#  23, 24]} ['WS_construction_Pieces']\nSM_VK_Prop_Wheelbarrow {'name': 'SM_VK_Prop_Wheelbarrow', 'tris': 780, 'bbox': [2.2, 0.73, 0.84], 'zmin': -0.0, 
# 'mats': [2, 5, 23, 45]} ['WS_construction_Pieces']\nSM_VK_Emblem_Ridge_Tankard {'name': 'SM_VK_Emblem_Ridge_Tankard', 'tris': 1444, 'bbox': [0.95, 0.6
# 1, 1.93], 'zmin': -0.1, 'mats': [2, 5, 17, 19]} ['WS_skyline_Pieces']\nSM_VK_Prop_ShopGoods_Pots {'name': 'SM_VK_Prop_ShopGoods_Pots', 'tris': 1448, '

# ==============================================================================================================
# [0010] 2026-09-23 15:54:04  blender  ok
# ==============================================================================================================
import bpy,re
for tn in ("ws_humble","ws_skyline"):
    t=bpy.data.texts.get(tn)
    if not t: print(tn,"none"); continue
    s=t.as_string()
    for m in re.finditer(r".*(RoofThatch_Vent|Roof_Vent\b).*",s):
        print(tn,":",m.group(0)[:220])
# ---- result ----
# {"result":"Code executed successfully: ws_humble : for i in vents: P(\"SM_VK_RoofThatch_Vent\", -L / 2 + 1.5 + 3 * i, 0, HUM_HW + RIDGE, 0)\nws_humble
#  : (\"SM_VK_RoofThatch_Vent\", hum_roof_thatch_vent, _hum_nw),\nws_skyline : (\"SM_VK_Roof_Vent\",sky_roof_vent,SKY_NW),\n"}

# ==============================================================================================================
# [0011] 2026-09-23 15:54:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
for nm,(x,y) in [("charcoal",(12,24)),("tannery",(-36,52))]:
    ws_shot("industry","top_"+nm,(x,y-0.01,24),(x,y,0),lens=35,res=(960,540),samples=16)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0012] 2026-09-23 15:55:36  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
from mathutils import Vector
def studio(names,shot,y0=-100.0,gap=0.8,h=None,lens=40,dist=1.0,res=(1280,720)):
    objs=[bpy.data.objects[n] for n in names]
    ws=[max(o.dimensions.x,1.0) for o in objs]
    tot=sum(ws)+gap*(len(ws)-1); x=-tot/2
    for o,w in zip(objs,ws):
        o.location=(x+w/2,y0,0); x+=w+gap
    H=max(o.dimensions.z for o in objs)
    d=max(tot*0.95,H*2.2)*dist
    return ws_shot("industry",shot,(tot*0.12,y0-d*0.9,d*0.45+H*0.3),(0,y0,H*0.3),lens=lens,res=res)
studio(["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3"],"g_mine_props")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0013] 2026-09-23 15:56:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
def studio(names,shot,cx=45.0,y0=-30.0,gap=0.6,lens=40,dist=0.75,res=(1280,720),el=0.5):
    objs=[bpy.data.objects[n] for n in names]
    ws=[max(o.dimensions.x,1.0) for o in objs]
    tot=sum(ws)+gap*(len(ws)-1); x=cx-tot/2
    for o,w in zip(objs,ws):
        o.location=(x+w/2,y0,0); x+=w+gap
    H=max(o.dimensions.z for o in objs)
    d=max(tot*0.95,H*2.2)*dist
    return ws_shot("industry",shot,(cx+tot*0.1,y0-d*0.9,d*el+H*0.3),(cx,y0,H*0.3),lens=lens,res=res)
bpy.app.driver_namespace["ind_studio"]=studio
studio(["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_3"],"g_mine_props")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0014] 2026-09-23 15:57:23  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
names=["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3"]
objs=ws_build("industry",names=names,g=g)
for s in ws_stats(objs): print(s['name'],s['tris'],s['bbox'])
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_3"],"g_mine_props",dist=0.62)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Minecart 1780 [1.79, 0.98, 1.24]\nSM_VK_Pile_Ore_1 756 [1.82, 1.55, 0.69]\nSM_VK_Pile_Ore_2 1064 [2.
# 6, 2.09, 0.75]\nSM_VK_Pile_Ore_3 1520 [3.18, 2.63, 1.26]\nSM_VK_Pile_Coal_1 736 [2.09, 1.43, 0.71]\nSM_VK_Pile_Coal_2 1140 [2.75, 2.15, 0.93]\nSM_VK_P
# ile_Coal_3 1792 [3.39, 2.72, 1.02]\n"}

# ==============================================================================================================
# [0015] 2026-09-23 15:58:51  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
names=["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3"]
objs=ws_build("industry",names=names,g=g)
for s in ws_stats(objs): print(s['name'],s['tris'],s['bbox'])
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_2"],"g_mine_props",dist=1.0)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Minecart 1780 [1.79, 0.98, 1.25]\nSM_VK_Pile_Ore_1 756 [1.82, 1.55, 0.68]\nSM_VK_Pile_Ore_2 1064 [2.
# 6, 2.07, 0.8]\nSM_VK_Pile_Ore_3 1520 [3.16, 2.62, 1.26]\nSM_VK_Pile_Coal_1 736 [2.09, 1.43, 0.68]\nSM_VK_Pile_Coal_2 1140 [2.75, 2.15, 0.93]\nSM_VK_Pi
# le_Coal_3 1792 [3.39, 2.72, 1.03]\n"}

# ==============================================================================================================
# [0016] 2026-09-23 15:59:34  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
names=["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3"]
objs=ws_build("industry",names=names,g=g)
for s in ws_stats(objs): print(s['name'],s['tris'],s['bbox'])
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_Minecart","SM_VK_Pile_Ore_3","SM_VK_Pile_Ore_1"],"g_mine_props",dist=1.0)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Minecart 1780 [1.79, 0.98, 1.24]\nSM_VK_Pile_Ore_1 776 [1.89, 1.55, 0.68]\nSM_VK_Pile_Ore_2 1064 [2.
# 65, 2.08, 0.81]\nSM_VK_Pile_Ore_3 1480 [3.16, 2.62, 1.23]\nSM_VK_Pile_Coal_1 736 [2.09, 1.43, 0.68]\nSM_VK_Pile_Coal_2 1140 [2.75, 2.15, 0.93]\nSM_VK_
# Pile_Coal_3 1792 [3.39, 2.72, 1.03]\n"}

# ==============================================================================================================
# [0017] 2026-09-23 16:01:58  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
L=[("build_mine",(-36,24,0)),("build_quarry_yard",(-12,26,0)),("build_charcoal_burner",(12,24,0)),("build_pottery",(36,24,0)),
   ("build_tannery",(-36,52,0)),("build_dyers_yard",(-12,52,0)),("build_brewery",(12,52,0)),("build_apiary",(38,52,0))]
for fn,o in L:
    try: g[fn](asm,o,seed=0)
    except Exception: print(fn,traceback.format_exc()[-500:])
print(len(asm.objects))
ws_shot("industry","top_charcoal",(12,24-0.01,22),(12,24,0),lens=35,res=(960,540),samples=16)
ws_shot("industry","top_tannery",(-36,52-0.01,24),(-36,52,0),lens=35,res=(960,540),samples=16)
# ---- result ----
# {"result":"Code executed successfully: 166\n"}

# ==============================================================================================================
# [0018] 2026-09-23 16:02:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","a_brewery_v2",(12+13,52-21,13),(12+0.5,52-0.5,2.0),lens=35)
ws_shot("industry","a_tannery_v2",(-36+12,52-19,11),(-36-0.5,52+0.5,1.2),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0019] 2026-09-23 16:02:49  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","a_pottery_v2",(36+9,24-14,8),(36+0.5,24-0.5,1.0),lens=35)
for o in bpy.data.collections["WS_industry_Assembly"].objects:
    if "ShopGoods" in o.name or "Table" in o.name: print(o.name,tuple(round(v,2) for v in o.location), round(o.rotation_euler.z,2))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Table_inst.004 (39.4, 21.1, 0.0) 0.0\nSM_VK_Prop_ShopGoods_Pots_inst.001 (40.6, 23.4, 0.0) -1.57\n"}

# ==============================================================================================================
# [0020] 2026-09-23 16:03:45  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry",names=["SM_VK_Prop_ClayPit"],g=g)
print(ws_stats(objs))
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_ClayPit","SM_VK_Prop_PottersWheel","SM_VK_Pile_Bricks_2"],"g_clay",dist=0.9)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Prop_ClayPit', 'tris': 1204, 'bbox': [3.58, 3.42, 1.7], 'zmin': -0.59, 'mats': [2, 18, 21, 23,
#  26, 29, 31, 47]}]\n"}

# ==============================================================================================================
# [0021] 2026-09-23 16:04:52  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
def studio(names,shot,cx=45.0,y0=-30.0,gap=0.6,lens=40,dist=0.75,res=(1280,720),el=0.5,look=None):
    g=bpy.app.driver_namespace.get("ind_names")
    allp=[o for o in bpy.data.collections["WS_industry_Pieces"].objects]
    allp.sort(key=lambda o:o.name)
    ws_grid(allp,cols=7,sx=9,sy=9,origin=(-27,-6))
    objs=[bpy.data.objects[n] for n in names]
    ws=[max(o.dimensions.x,1.0) for o in objs]
    tot=sum(ws)+gap*(len(ws)-1); x=cx-tot/2
    for o,w in zip(objs,ws):
        o.location=(x+w/2,y0,0); x+=w+gap
    H=max(o.dimensions.z for o in objs)
    d=max(tot*0.95,H*2.2)*dist
    return ws_shot("industry",shot,(cx+tot*0.1,y0-d*0.9,d*el+H*0.3),(cx,y0,H*0.3),lens=lens,res=res)
bpy.app.driver_namespace["ind_studio"]=studio
studio(["SM_VK_Prop_ClayPit","SM_VK_Prop_PottersWheel","SM_VK_Pile_Bricks_2"],"g_clay",dist=1.0)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0022] 2026-09-23 16:06:04  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry",names=["SM_VK_Prop_ClayPit"],g=g)
print(ws_stats(objs))
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_ClayPit","SM_VK_Prop_TanningPit"],"g_clay",dist=1.0,lens=35)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Prop_ClayPit', 'tris': 1344, 'bbox': [3.7, 3.6, 1.7], 'zmin': -0.59, 'mats': [2, 18, 21, 23, 2
# 6, 29, 31, 37, 47]}]\n"}

# ==============================================================================================================
# [0023] 2026-09-23 16:06:39  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry",names=["SM_VK_Prop_ClayPit"],g=g)
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_HideFrame","SM_VK_Prop_DyeVat","SM_VK_Prop_Loom","SM_VK_Prop_SpinningWheel","SM_VK_Pile_Hides_2","SM_VK_Pile_Wool_3"],"g_cloth",dist=0.8,lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0024] 2026-09-23 16:07:08  blender  ok
# ==============================================================================================================
import bpy
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Prop_CiderPress","SM_VK_Prop_HerbBundles","SM_VK_Prop_Cauldron","SM_VK_Prop_DryingRack_Meat","SM_VK_Prop_DryingRack_Herbs"],"g_food",dist=0.8,lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0025] 2026-09-23 16:09:12  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
objs=ws_build("industry",names=["SM_VK_Prop_HerbBundles","SM_VK_Prop_DryingRack_Meat"],g=g)
print(ws_stats(objs))
ws_clear_assembly("industry")
L=[("build_mine",(-36,24,0)),("build_quarry_yard",(-12,26,0)),("build_charcoal_burner",(12,24,0)),("build_pottery",(36,24,0)),
   ("build_tannery",(-36,52,0)),("build_dyers_yard",(-12,52,0)),("build_brewery",(12,52,0)),("build_apiary",(38,52,0))]
for fn,o in L:
    try: g[fn](asm,o,seed=0)
    except Exception: print(fn,traceback.format_exc()[-500:])
ws_shot("industry","a_apiary_v2",(38+10,52-15,10),(38+0.3,52,1.5),lens=35)
ws_shot("industry","top_dyers",(-12,52-0.01,20),(-12,52,0),lens=35,res=(960,540),samples=16)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Prop_HerbBundles', 'tris': 596, 'bbox': [2.5, 0.86, 2.1], 'zmin': 0.0, 'mats': [2, 16, 32, 45,
#  47]}, {'name': 'SM_VK_Prop_DryingRack_Meat', 'tris': 1460, 'bbox': [2.7, 1.19, 2.21], 'zmin': -0.01, 'mats': [2, 16, 17, 29, 41]}]\n"}

# ==============================================================================================================
# [0026] 2026-09-23 16:11:11  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
L=[("build_mine",(-36,24,0)),("build_quarry_yard",(-12,26,0)),("build_charcoal_burner",(12,24,0)),("build_pottery",(36,24,0)),
   ("build_tannery",(-36,52,0)),("build_dyers_yard",(-12,52,0)),("build_brewery",(12,52,0)),("build_apiary",(38,52,0))]
for fn,o in L:
    try: g[fn](asm,o,seed=0)
    except Exception: print(fn,traceback.format_exc()[-500:])
ws_shot("industry","mine_front",(-36+3,24-9,3.2),(-36,24+1,1.6),lens=30)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0027] 2026-09-23 16:12:25  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry",names=["SM_VK_Mine_Portal"],g=g)
print(ws_stats(objs))
ws_shot("industry","mine_front",(-36+3,24-9,3.2),(-36,24+1,1.6),lens=30)
ws_shot("industry","mine_high",(-36+6,24-16,17),(-36,24+1,1.0),lens=35)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Mine_Portal', 'tris': 3927, 'bbox': [8.94, 7.91, 5.75], 'zmin': -0.6, 'mats': [2, 5, 9, 21, 23
# , 26, 27, 28, 31, 37, 38, 45]}]\n"}

# ==============================================================================================================
# [0028] 2026-09-23 16:13:31  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry",names=["SM_VK_Mine_Portal"],g=g)
print(ws_stats(objs))
ws_shot("industry","mine_front",(-36+3,24-9,3.2),(-36,24+1,1.6),lens=30,res=(960,540))
ws_shot("industry","mine_high",(-36+6,24-16,17),(-36,24+1,1.0),lens=35,res=(960,540))
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_Mine_Portal', 'tris': 3976, 'bbox': [8.94, 7.91, 5.75], 'zmin': -0.6, 'mats': [2, 5, 9, 21, 23
# , 26, 27, 28, 31, 37, 38, 45]}]\n"}

# ==============================================================================================================
# [0029] 2026-09-23 16:14:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","a_charcoal_v2",(12+8,24-15,9),(12+0.5,24,1.0),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0030] 2026-09-23 16:15:30  blender  ok
# ==============================================================================================================
import bpy
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry")
objs=ws_build("industry",names=["SM_VK_Pile_Bricks_1","SM_VK_Pile_Bricks_2","SM_VK_Pile_Bricks_3"],g=g)
for s in ws_stats(objs): print(s['name'],s['tris'],s['bbox'])
studio=bpy.app.driver_namespace["ind_studio"]
studio(["SM_VK_Pile_Bricks_1","SM_VK_Pile_Bricks_3"],"g_bricks",dist=0.9,lens=35,res=(960,540))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Pile_Bricks_1 600 [1.33, 1.2, 0.64]\nSM_VK_Pile_Bricks_2 1076 [1.83, 1.29, 0.73]\nSM_VK_Pile_Bricks_3 155
# 2 [3.28, 1.29, 0.73]\n"}

# ==============================================================================================================
# [0031] 2026-09-23 16:16:25  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
L=[("build_mine",(-36,24,0)),("build_quarry_yard",(-12,26,0)),("build_charcoal_burner",(12,24,0)),("build_pottery",(36,24,0)),
   ("build_tannery",(-36,52,0)),("build_dyers_yard",(-12,52,0)),("build_brewery",(12,52,0)),("build_apiary",(38,52,0))]
for fn,o in L:
    try: g[fn](asm,o,seed=0)
    except Exception: print(fn,traceback.format_exc()[-500:])
e=[o for o in asm.objects if "Emblem" in o.name]
print([(o.name,tuple(round(v,2) for v in o.location)) for o in e])
ch=[o for o in asm.objects if "Chimney" in o.name and abs(o.location.x-9)<6]
print([(o.name,tuple(round(v,2) for v in o.location)) for o in ch])
ws_shot("industry","a_brewery_v3",(12-4,52-24,18),(12+0.5,52,3.0),lens=35,res=(960,540))
# ---- result ----
# {"result":"Code executed successfully: [('SM_VK_Emblem_Ridge_Tankard_inst', (9.0, 53.0, 9.99))]\n[('SM_VK_Chimney_inst.057', (12.0, 53.0, 5.8))]\n"}

# ==============================================================================================================
# [0032] 2026-09-23 16:18:16  blender  ok
# ==============================================================================================================
import bpy, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
try: g["build_industry_quarter"](asm,(4,26,0),seed=0)
except Exception: print(traceback.format_exc()[-800:])
print(len(asm.objects))
# colony camera: 50 deg pitch, ~40 m distance
import math
tgt=(0,36,0); d=42; p=math.radians(50)
loc=(tgt[0]+4, tgt[1]-d*math.cos(p), d*math.sin(p))
ws_shot("industry","colony_test",loc,tgt,lens=30,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: 170\n"}

# ==============================================================================================================
# [0033] 2026-09-23 16:19:03  blender  ok
# ==============================================================================================================
import bpy, traceback, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
try: g["build_industry_quarter"](asm,(4,26,0),seed=0)
except Exception: print(traceback.format_exc()[-800:])
print(len(asm.objects))
tgt=(-4,34,0); d=44; p=math.radians(50)
loc=(tgt[0]+6, tgt[1]-d*math.cos(p), d*math.sin(p))
ws_shot("industry","colony_test",loc,tgt,lens=28,res=(1280,720))
# ---- result ----
# {"result":"Code executed successfully: 170\n"}

# ==============================================================================================================
# [0034] 2026-09-23 16:20:05  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
rows=[
 ["SM_VK_Prop_ClayPit","SM_VK_Prop_PottersWheel","SM_VK_Pile_Bricks_1","SM_VK_Pile_Bricks_2","SM_VK_Pile_Bricks_3","SM_VK_Prop_TanningPit","SM_VK_Prop_HideFrame","SM_VK_Prop_DyeVat","SM_VK_Prop_ClothRack","SM_VK_Prop_Loom","SM_VK_Prop_SpinningWheel"],
 ["SM_VK_Pile_Hides_1","SM_VK_Pile_Hides_2","SM_VK_Pile_Hides_3","SM_VK_Pile_Wool_1","SM_VK_Pile_Wool_2","SM_VK_Pile_Wool_3","SM_VK_Prop_MashTun","SM_VK_Prop_CiderPress","SM_VK_Prop_Skep","SM_VK_Prop_BeeBench","SM_VK_Prop_Cauldron"],
 ["SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Prop_Minecart","SM_VK_Prop_Banker","SM_VK_Prop_Bellows","SM_VK_Prop_HerbBundles","SM_VK_Prop_DryingRack_Meat","SM_VK_Prop_DryingRack_Herbs"],
 ["SM_VK_Rail_Straight","SM_VK_Rail_Curve","SM_VK_Rail_End","SM_VK_Quarry_Floor","SM_VK_Quarry_Face_Straight","SM_VK_Quarry_Face_Corner","SM_VK_Quarry_Face_InnerCorner","SM_VK_Prop_CharcoalMound","SM_VK_Prop_Bloomery"],
 ["SM_VK_Mine_Portal","SM_VK_Prop_TreadwheelCrane","SM_VK_Prop_TreadwheelCrane_Wheel","SM_VK_Prop_BottleKiln","SM_VK_Kiln_Oast","SM_VK_Prop_Dovecote"],
]
gap=1.0; y=-10.0; allw=[]
placed=set()
for r in rows:
    objs=[bpy.data.objects[n] for n in r]
    for o in objs: o.location=(0,0,0); o.rotation_euler=(0,0,0)
    bpy.context.view_layer.update() if False else None
    def bb(o):
        cs=[Vector(c) for c in o.bound_box]; return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs))
    ws_=[bb(o) for o in objs]
    tot=sum(b[1]-b[0] for b in ws_)+gap*(len(objs)-1)
    depth=max(b[3]-b[2] for b in ws_)
    x=-tot/2
    for o,b in zip(objs,ws_):
        o.location=(x-b[0], y-(b[2]+b[3])/2, 0); x+=b[1]-b[0]+gap
        placed.add(o.name)
    w=bpy.data.objects["SM_VK_Prop_TreadwheelCrane_Wheel"]
    allw.append((round(tot,1),round(depth,1),y))
    y-=depth+2.0
wh=bpy.data.objects["SM_VK_Prop_TreadwheelCrane_Wheel"]; wh.location.z=1.82
missing=[o.name for o in bpy.data.collections["WS_industry_Pieces"].objects if o.name not in placed]
print(allw, "missing:",missing)
# ---- result ----
# {"result":"Code executed successfully: [(33.8, 3.6, -10.0), (32.9, 2.7, -15.601822018623352), (39.3, 2.7, -20.301822066307068), (38.4, 4.2, -25.019729
# 97188568), (42.4, 7.9, -31.25473463535309)] missing: []\n"}

# ==============================================================================================================
# [0035] 2026-09-23 16:21:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","catalog_test",(0,-62,30),(0,-24,0),lens=32,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0036] 2026-09-23 16:21:34  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
rows=[
 ["SM_VK_Mine_Portal","SM_VK_Prop_TreadwheelCrane","SM_VK_Prop_TreadwheelCrane_Wheel","SM_VK_Prop_BottleKiln","SM_VK_Kiln_Oast","SM_VK_Prop_Dovecote"],
 ["SM_VK_Rail_Straight","SM_VK_Rail_Curve","SM_VK_Rail_End","SM_VK_Quarry_Floor","SM_VK_Quarry_Face_Straight","SM_VK_Quarry_Face_Corner","SM_VK_Quarry_Face_InnerCorner","SM_VK_Prop_CharcoalMound","SM_VK_Prop_Bloomery"],
 ["SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Prop_Minecart","SM_VK_Prop_Banker","SM_VK_Prop_Bellows","SM_VK_Prop_HerbBundles","SM_VK_Prop_DryingRack_Meat","SM_VK_Prop_DryingRack_Herbs"],
 ["SM_VK_Pile_Hides_1","SM_VK_Pile_Hides_2","SM_VK_Pile_Hides_3","SM_VK_Pile_Wool_1","SM_VK_Pile_Wool_2","SM_VK_Pile_Wool_3","SM_VK_Prop_MashTun","SM_VK_Prop_CiderPress","SM_VK_Prop_Skep","SM_VK_Prop_BeeBench","SM_VK_Prop_Cauldron"],
 ["SM_VK_Prop_ClayPit","SM_VK_Prop_PottersWheel","SM_VK_Pile_Bricks_1","SM_VK_Pile_Bricks_2","SM_VK_Pile_Bricks_3","SM_VK_Prop_TanningPit","SM_VK_Prop_HideFrame","SM_VK_Prop_DyeVat","SM_VK_Prop_ClothRack","SM_VK_Prop_Loom","SM_VK_Prop_SpinningWheel"],
]
def bb(o):
    cs=[Vector(c) for c in o.bound_box]; return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs))
gap=1.0; y=-8.0; info=[]
for r in rows:
    objs=[bpy.data.objects[n] for n in r]
    for o in objs: o.rotation_euler=(0,0,0)
    ws_=[bb(o) for o in objs]
    tot=sum(b[1]-b[0] for b in ws_)+gap*(len(objs)-1)
    depth=max(b[3]-b[2] for b in ws_)
    x=-tot/2
    for o,b in zip(objs,ws_):
        o.location=(x-b[0], y-(b[2]+b[3])/2, 0); x+=b[1]-b[0]+gap
    info.append((round(tot,1),round(depth,1),round(y,1)))
    y-=depth/2+ (3.0 if len(info)==1 else 1.6)
    if len(info)<len(rows): y-=0  
bpy.data.objects["SM_VK_Prop_TreadwheelCrane_Wheel"].location.z=1.82
print(info)
ws_shot("industry","catalog_test",(0,-58,26),(0,-20,0),lens=33,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: [(42.4, 7.9, -8.0), (38.4, 4.2, -15.0), (39.3, 2.7, -18.7), (32.9, 2.7, -21.6), (33.8, 3.6, -24.6)]\n"}

# ==============================================================================================================
# [0037] 2026-09-23 16:22:26  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
exec(bpy.data.texts["ws_common"].as_string())
rows=[
 ["SM_VK_Mine_Portal","SM_VK_Prop_TreadwheelCrane","SM_VK_Prop_TreadwheelCrane_Wheel","SM_VK_Prop_BottleKiln","SM_VK_Kiln_Oast","SM_VK_Prop_Dovecote"],
 ["SM_VK_Rail_Straight","SM_VK_Rail_Curve","SM_VK_Rail_End","SM_VK_Quarry_Floor","SM_VK_Quarry_Face_Straight","SM_VK_Quarry_Face_Corner","SM_VK_Quarry_Face_InnerCorner","SM_VK_Prop_CharcoalMound","SM_VK_Prop_Bloomery"],
 ["SM_VK_Pile_Coal_1","SM_VK_Pile_Coal_2","SM_VK_Pile_Coal_3","SM_VK_Pile_Ore_1","SM_VK_Pile_Ore_2","SM_VK_Pile_Ore_3","SM_VK_Prop_Minecart","SM_VK_Prop_Banker","SM_VK_Prop_Bellows","SM_VK_Prop_HerbBundles","SM_VK_Prop_DryingRack_Meat","SM_VK_Prop_DryingRack_Herbs"],
 ["SM_VK_Pile_Hides_1","SM_VK_Pile_Hides_2","SM_VK_Pile_Hides_3","SM_VK_Pile_Wool_1","SM_VK_Pile_Wool_2","SM_VK_Pile_Wool_3","SM_VK_Prop_MashTun","SM_VK_Prop_CiderPress","SM_VK_Prop_Skep","SM_VK_Prop_BeeBench","SM_VK_Prop_Cauldron"],
 ["SM_VK_Prop_ClayPit","SM_VK_Prop_PottersWheel","SM_VK_Pile_Bricks_1","SM_VK_Pile_Bricks_2","SM_VK_Pile_Bricks_3","SM_VK_Prop_TanningPit","SM_VK_Prop_HideFrame","SM_VK_Prop_DyeVat","SM_VK_Prop_ClothRack","SM_VK_Prop_Loom","SM_VK_Prop_SpinningWheel"],
]
def bb(o):
    cs=[Vector(c) for c in o.bound_box]; return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs))
gap=1.2; rgap=2.2; y=None; prev=None; info=[]
for r in rows:
    objs=[bpy.data.objects[n] for n in r]
    for o in objs: o.rotation_euler=(0,0,0)
    ws_=[bb(o) for o in objs]
    tot=sum(b[1]-b[0] for b in ws_)+gap*(len(objs)-1)
    depth=max(b[3]-b[2] for b in ws_)
    y=-8.0 if prev is None else y-prev/2-rgap-depth/2
    x=-tot/2
    for o,b in zip(objs,ws_):
        o.location=(x-b[0], y-(b[2]+b[3])/2, 0); x+=b[1]-b[0]+gap
    info.append((round(tot,1),round(depth,1),round(y,1))); prev=depth
bpy.data.objects["SM_VK_Prop_TreadwheelCrane_Wheel"].location.z=1.82
print(info)
ws_shot("industry","catalog_test",(0,-52,27),(0,-18.5,0.5),lens=33,res=(1600,900),samples=24)
# ---- result ----
# {"result":"Code executed successfully: [(43.4, 7.9, -8.0), (40.0, 4.2, -16.3), (41.5, 2.7, -21.9), (34.9, 2.7, -26.9), (35.8, 3.6, -32.2)]\n"}

# ==============================================================================================================
# [0038] 2026-09-23 16:23:09  blender  ok
# ==============================================================================================================
import bpy, hashlib, time
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
print("identical:",t.as_string()==src, hashlib.md5(src.encode()).hexdigest())
t0=time.time()
exec(bpy.data.texts["ws_common"].as_string()); g=ws_ns("industry"); objs=ws_build("industry", g=g)
print("built",len(objs),"in",round(time.time()-t0,1),"s")
for s in ws_stats(objs): print(s['name'],s['tris'],s['bbox'],s['zmin'])
# ---- result ----
# {"result":"Code executed successfully: identical: True 1d8bd27e8d976527cb5ce031e636cf50\nbuilt 49 in 3.6 s\nSM_VK_Mine_Portal 3976 [8.94, 7.91, 5.75] 
# -0.6\nSM_VK_Rail_Straight 324 [3.0, 1.6, 0.53] -0.3\nSM_VK_Rail_Curve 1056 [3.84, 3.84, 0.53] -0.3\nSM_VK_Rail_End 1104 [3.59, 1.69, 1.2] -0.3\nSM_VK_
# Prop_Minecart 1780 [1.79, 0.98, 1.24] -0.03\nSM_VK_Pile_Ore_1 776 [1.89, 1.55, 0.68] -0.06\nSM_VK_Pile_Ore_2 1064 [2.65, 2.08, 0.81] -0.08\nSM_VK_Pile
# _Ore_3 1480 [3.16, 2.62, 1.23] -0.07\nSM_VK_Pile_Coal_1 736 [2.09, 1.43, 0.68] -0.13\nSM_VK_Pile_Coal_2 1140 [2.75, 2.15, 0.93] -0.13\nSM_VK_Pile_Coal
# _3 1792 [3.39, 2.72, 1.03] -0.14\nSM_VK_Quarry_Face_Straight 1096 [3.0, 3.17, 4.15] -0.6\nSM_VK_Quarry_Face_Corner 1244 [3.08, 3.21, 4.12] -0.6\nSM_VK
# _Quarry_Face_InnerCorner 1104 [3.07, 3.12, 4.06] -0.6\nSM_VK_Quarry_Floor 1252 [2.98, 2.98, 1.37] -0.61\nSM_VK_Prop_Banker 860 [1.73, 1.36, 1.46] -0.0

# ==============================================================================================================
# [0039] 2026-09-23 16:24:03  blender  ok
# ==============================================================================================================
import bpy, traceback
exec(bpy.data.texts["ws_common"].as_string()); g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
ok=[]
for fn,x,y in g["IND_QUARTER"]:
    try:
        n0=len(asm.objects); g[fn](asm,g["ind_sub_origin"]((4,26,0),x,y),seed=0); ok.append((fn,len(asm.objects)-n0))
    except Exception: print(fn,"ERROR",traceback.format_exc()[-600:])
print(ok, "total",len(asm.objects))
# quarter builder itself (into a throw-away check: build then remove its objects)
before=set(o.name for o in asm.objects)
try:
    g["build_industry_quarter"](asm,(4,-200,0),seed=0)
    new=[o for o in asm.objects if o.name not in before]; print("quarter ok",len(new))
    for o in new: bpy.data.objects.remove(o)
except Exception: print("quarter ERROR",traceback.format_exc()[-600:])
print("final asm objects",len(asm.objects))
# ---- result ----
# {"result":"Code executed successfully: [('build_mine', 15), ('build_quarry_yard', 21), ('build_charcoal_burner', 9), ('build_pottery', 9), ('build_tan
# nery', 42), ('build_dyers_yard', 12), ('build_brewery', 49), ('build_apiary', 13)] total 170\nquarter ok 170\nfinal asm objects 170\n"}

# ==============================================================================================================
# [0040] 2026-09-23 16:24:26  blender  ok
# ==============================================================================================================
import bpy
for me in list(bpy.data.meshes):
    if me.name.startswith("IND_Standin_") and me.users==0: bpy.data.meshes.remove(me)
print([m.name for m in bpy.data.meshes if m.name.startswith("IND_Standin")])
exec(bpy.data.texts["ws_common"].as_string())
print(ws_shot("industry","catalog_final",(0,-57,30),(0,-19.8,0.3),lens=31,res=(1600,900),samples=32))
# ---- result ----
# {"result":"Code executed successfully: ['IND_Standin_QuarryBack', 'IND_Standin_QuarryL', 'IND_Standin_QuarryR']\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\industry\\
# catalog_final.png\n"}

# ==============================================================================================================
# [0041] 2026-09-23 16:24:56  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
# 1) colony camera: 50 deg pitch, ~44 m from the target
tgt=(-2,36,0); d=44; p=math.radians(50)
ws_shot("industry","hero_colony",(tgt[0]+5,tgt[1]-d*math.cos(p),d*math.sin(p)),tgt,lens=28,res=(1600,900),samples=32)
# 2) mine + quarry 3/4
ws_shot("industry","hero_mine_quarry",(-33,5,15),(-16,28,1.2),lens=33,res=(1600,900),samples=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0042] 2026-09-23 16:26:05  blender  ok
# ==============================================================================================================
import bpy, traceback, math
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_industry"); t.clear(); t.write(src)
exec(bpy.data.texts["ws_common"].as_string()); g=ws_ns("industry"); sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
for me in list(bpy.data.meshes):
    if me.name.startswith("IND_Standin_") and me.users==0: bpy.data.meshes.remove(me)
try: g["build_industry_quarter"](asm,(4,26,0),seed=0)
except Exception: print(traceback.format_exc()[-600:])
print(len(asm.objects))
ws_shot("industry","hero_mine_quarry",(-33,5,15),(-16,28,1.2),lens=33,res=(1600,900),samples=32)
# ---- result ----
# {"result":"Code executed successfully: 170\n"}

# ==============================================================================================================
# [0043] 2026-09-23 16:26:32  blender  ok
# ==============================================================================================================
import bpy, math
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","hero_mine_quarry",(-29,-1,18),(-15,29,0.5),lens=33,res=(1600,900),samples=32)
tgt=(-2,36,0); d=44; p=math.radians(50)
ws_shot("industry","hero_colony",(tgt[0]+5,tgt[1]-d*math.cos(p),d*math.sin(p)),tgt,lens=28,res=(1600,900),samples=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0044] 2026-09-23 16:26:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","hero_workshops",(9,20,15),(-10,45,1.5),lens=32,res=(1600,900),samples=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0045] 2026-09-23 16:27:31  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["ws_common"].as_string())
ws_shot("industry","hero_workshops",(-2,16,26),(-12,45,0.5),lens=30,res=(1600,900),samples=32)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0046] 2026-09-23 16:28:17  blender  ok
# ==============================================================================================================
import bpy, hashlib, traceback
src=open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_industry.py",encoding="utf8").read()
ts=bpy.data.texts["ws_industry"].as_string()
print("identical:",ts==src,hashlib.md5(src.encode()).hexdigest(),len(src))
exec(bpy.data.texts["ws_common"].as_string()); g=ws_ns("industry"); objs=ws_build("industry", g=g)
print("ws_build ok:",len(objs))
sc,coll,asm=ws_scene("industry")
ws_clear_assembly("industry")
for me in list(bpy.data.meshes):
    if me.name.startswith("IND_Standin_") and me.users==0: bpy.data.meshes.remove(me)
res=[]
for fn,x,y in g["IND_QUARTER"]:
    try: n0=len(asm.objects); g[fn](asm,g["ind_sub_origin"]((4,26,0),x,y),seed=0); res.append((fn,len(asm.objects)-n0))
    except Exception: res.append((fn,"ERR "+traceback.format_exc()[-300:]))
print(res,len(asm.objects))
print(sorted(set(o.name.split("_inst")[0] for o in asm.objects if not o.name.startswith("SM_VK_") )))
# ---- result ----
# {"result":"Code executed successfully: identical: True e0404d547b1df19073a9b6f457305b8b 92499\nws_build ok: 49\n[('build_mine', 15), ('build_quarry_ya
# rd', 21), ('build_charcoal_burner', 9), ('build_pottery', 9), ('build_tannery', 42), ('build_dyers_yard', 12), ('build_brewery', 49), ('build_apiary',
#  13)] 170\n['IND_Standin_QuarryBack', 'IND_Standin_QuarryL', 'IND_Standin_QuarryR']\n"}
