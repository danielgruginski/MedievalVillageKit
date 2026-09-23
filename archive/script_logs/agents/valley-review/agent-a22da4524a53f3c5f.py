# valley-review / agent-a22da4524a53f3c5f.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 16:57:39  blender  ok
# ==============================================================================================================
import bpy, collections
col = bpy.data.collections.get("VK_ValleyTown")
objs = list(col.all_objects)
print(len(objs))
pref = collections.Counter()
for o in objs:
    n = o.name.split('.')[0]
    parts = n.split('_')
    pref['_'.join(parts[:2])] += 1
print(pref.most_common(80))
print([c.name for c in col.children_recursive][:50])
print("vk_render" in bpy.data.texts)
# ---- result ----
# {"result":"Code executed successfully: 5568\n[('SM_VK', 4224), ('SM_VKT', 1344)]\n[]\nTrue\n"}

# ==============================================================================================================
# [0002] 2026-09-23 16:58:02  blender  ok
# ==============================================================================================================
import bpy, collections
col = bpy.data.collections.get("VK_ValleyTown")
objs = list(col.all_objects)
pref = collections.Counter()
for o in objs:
    n = o.name.split('.')[0]
    pref[n] += 1
print(len(pref))
print(sorted(pref.items(), key=lambda x:-x[1])[:200])
o=objs[0]
print(o.name, o.type, o.data.name if o.data else None, o.instance_type, o.instance_collection, list(o.keys()))
# ---- result ----
# {"result":"Code executed successfully: 339\n[('SM_VKT_LipGrass_inst', 1344), ('SM_VK_Tree_Pine_Young_inst', 342), ('SM_VK_Tree_Pine_B_inst', 335), ('S
# M_VK_Tree_Pine_A_inst', 324), ('SM_VK_Wall_Timber_Window_inst', 135), ('SM_VK_Deco_Weeds_inst', 125), ('SM_VK_Bush_Round_inst', 121), ('SM_VK_TownWall
# _Straight_inst', 119), ('SM_VK_Rock_Small_A_inst', 113), ('SM_VK_Plant_Fern_inst', 112), ('SM_VK_Wall_Stone_inst', 101), ('SM_VK_Corner_Timber_inst', 
# 88), ('SM_VK_Rock_Pebbles_inst', 87), ('SM_VK_Rock_Small_B_inst', 86), ('SM_VK_Rock_Boulder_A_inst', 86), ('SM_VK_Corner_Stone_inst', 83), ('SM_VK_Mus
# hrooms_Brown_inst', 75), ('SM_VK_Wall_Stone_Window_inst', 68), ('SM_VK_Tree_Oak_A_inst', 63), ('SM_VK_Tree_Oak_B_inst', 60), ('SM_VK_Tree_Birch_inst',
#  52), ('SM_VK_Prop_FlowerBox_inst', 41), ('SM_VK_Plant_TallGrass_inst', 39), ('SM_VK_Plant_Wildflowers_inst', 39), ('SM_VK_Prop_FlowerBox_Daisy_inst',

# ==============================================================================================================
# [0003] 2026-09-23 16:58:39  blender  ok
# ==============================================================================================================
import bpy
print(bpy.data.texts["vk_render"].as_string()[:3000])
# ---- result ----
# {"result":"Code executed successfully: import bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,len
# s=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is 
# None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.
# link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_e
# nd=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.render.

# ==============================================================================================================
# [0004] 2026-09-23 16:58:56  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
import time; t=time.time()
p=shot("review_build_00_town_top",(1628,40,150),(1628,108,0),lens=30,res=(1600,900),outdir=OD)
print(p, time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_00_town_top.png 3.6547110080718994\n"}

# ==============================================================================================================
# [0005] 2026-09-23 16:59:32  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
col = bpy.data.collections["VK_ValleyTown"]
seen={}
for o in col.all_objects:
    if o.type!='MESH': continue
    m=o.data.name
    if m in seen: continue
    bb=[Vector(c) for c in o.bound_box]
    mn=[min(v[k] for v in bb) for k in range(3)]; mx=[max(v[k] for v in bb) for k in range(3)]
    seen[m]=(tuple(round(a,2) for a in mn),tuple(round(a,2) for a in mx))
for k in sorted(seen):
    if any(s in k for s in ("Wall","Corner","Roof","Chimney","Gate","Tower","Porch","Chapel","Parapet","Foundation","Scaffold","Gallery","Ceiling","LeanTo","Turret","Bartizan")):
        print(k, seen[k])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Banner_Wall ((-0.08, -1.5, -2.3), (0.08, -0.23, 0.18))\nSM_VK_Ceiling_Cell ((-1.5, -1.5, 2.48), (1.49, 1.
# 5, 2.76))\nSM_VK_Deco_MudWallow ((-1.89, -1.37, -0.04), (1.6, 1.19, 0.13))\nSM_VK_Gallery_End ((-1.72, -1.75, -0.6), (1.75, -0.2, 4.37))\nSM_VK_Galler
# y_Side ((-0.06, -1.5, 3.08), (0.06, -0.2, 4.05))\nSM_VK_Gallery_Timber ((-1.72, -1.75, -0.6), (1.5, -0.2, 4.15))\nSM_VK_Gatehouse_Block ((-5.31, -5.32
# , -1.5), (5.33, 3.25, 9.0))\nSM_VK_LowWall ((-1.5, -0.38, -0.04), (1.51, 0.4, 1.17))\nSM_VK_LowWall_GateArch ((-1.71, -0.39, -0.6), (1.67, 0.38, 3.65)
# )\nSM_VK_LowWall_Post ((-0.42, -0.43, 0.01), (0.43, 0.42, 1.46))\nSM_VK_Palisade_Gate ((-2.06, -0.61, -0.9), (2.06, 0.33, 5.2))\nSM_VK_Palisade_GateLe
# af ((-0.06, -0.28, 0.05), (1.45, 0.27, 3.4))\nSM_VK_Prop_FenceGate ((-1.6, -0.1, 0.0), (1.6, 0.18, 1.3))\nSM_VK_Quarry_Face_Corner ((-1.58, -1.62, -0.

# ==============================================================================================================
# [0006] 2026-09-23 16:59:42  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
col = bpy.data.collections["VK_ValleyTown"]
c=collections.Counter(o.data.name for o in col.all_objects if o.type=='MESH')
print(len(c)); print(list(c.items())[:60])
o=[o for o in col.all_objects if o.name.startswith("SM_VK_Wall_Timber_Window")][0]
print(o.name,o.data.name,o.data.users, o.parent, len(o.children), o.modifiers[:])
# ---- result ----
# {"result":"Code executed successfully: 672\n[('SM_VK_TownWall_Straight', 119), ('SM_VK_TownWall_Corner_Out', 4), ('VAR_5484851763361861047', 12), ('SM
# _VK_Gatehouse_Block', 1), ('VAR_1954227020950619817', 1), ('VAR_7628507698833271038', 2), ('VAR_2752242913129725541', 2), ('VAR_2410497256820385090', 
# 1), ('VAR_8835755335372175174', 1), ('VAR_8995024156451832954', 2), ('VAR_6178247103157526480', 2), ('VAR_4577962874921537654', 2), ('VAR_114903950886
# 8753848', 2), ('VAR_7313916915456892218', 1), ('VAR_4670401938046358351', 2), ('VAR_2814092422175201302', 6), ('SM_VK_Bridge_Stone_Span', 2), ('SM_VK_
# Bridge_Stone_Pier', 1), ('SM_VK_Bridge_Stone_Ramp', 2), ('SM_VK_Prop_LampPost', 13), ('SM_VK_Bridge_Wood_End', 2), ('SM_VK_Bridge_Wood_Mid', 4), ('SM_
# VK_Bridge_Wood_Bent', 5), ('VAR_1551938828901740622', 5), ('SM_VK_Prop_FlowerBox.002', 41), ('SM_VK_Deco_Weeds', 125), ('VAR_3616255822520852611', 2),

# ==============================================================================================================
# [0007] 2026-09-23 17:00:23  blender  ok
# ==============================================================================================================
import bpy, re, math
from mathutils import Vector
col = bpy.data.collections["VK_ValleyTown"]
def base(o): return re.sub(r'_inst(\.\d+)?$','',o.name)
D=[]
for o in col.all_objects:
    if o.type!='MESH': continue
    M=o.matrix_world
    ws=[M@Vector(c) for c in o.bound_box]
    mn=Vector((min(v.x for v in ws),min(v.y for v in ws),min(v.z for v in ws)))
    mx=Vector((max(v.x for v in ws),max(v.y for v in ws),max(v.z for v in ws)))
    D.append((o.name,base(o),mn,mx,o.matrix_world.translation.copy(),round(math.degrees(o.matrix_world.to_euler().z))%360))
bpy.app.driver_namespace["_rv_build_D"]=D
# duplicates: same base, loc within 5cm, same rot
from collections import defaultdict
g=defaultdict(list)
for d in D:
    k=(d[1],round(d[4].x*10),round(d[4].y*10),round(d[4].z*10))
    g[k].append(d[0])
dups=[(k,v) for k,v in g.items() if len(v)>1]
print(len(dups))
for k,v in dups[:40]: print(k,v)
# ---- result ----
# {"result":"Code executed successfully: 0\n"}

# ==============================================================================================================
# [0008] 2026-09-23 17:00:36  blender  ok
# ==============================================================================================================
import bpy, re
D=bpy.app.driver_namespace["_rv_build_D"]
WALLISH=("TownWall_","Gatehouse_Block")
BLD=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Scaffold|Ceiling|Def_Bartizan|Wall_Stone|Prop_|MarketStall|Tree_|Bush_|Banner_Wall|Deco_Ivy|Stockpile|Tent)')
walls=[d for d in D if any(w in d[1] for w in WALLISH)]
res=[]
for d in D:
    if any(w in d[1] for w in WALLISH): continue
    if not BLD.match(d[1]): continue
    for w in walls:
        ox=min(d[3].x,w[3].x)-max(d[2].x,w[2].x)
        oy=min(d[3].y,w[3].y)-max(d[2].y,w[2].y)
        oz=min(d[3].z,w[3].z)-max(d[2].z,w[2].z)
        if ox>0.15 and oy>0.15 and oz>0.15:
            res.append((round(min(ox,oy),2),d[0],w[0],tuple(round(a,1) for a in d[4]),tuple(round(a,1) for a in w[4])))
res.sort(reverse=True)
print(len(res))
for r in res[:80]: print(r)
# ---- result ----
# {"result":"Code executed successfully: 544\n(6.93, 'SM_VK_Tree_Oak_A_inst.036', 'SM_VK_TownWall_Tower_Round_inst.010', (1567.5, 117.5, 3.0), (1569.0, 
# 117.0, 3.0))\n(6.74, 'SM_VK_Tree_Birch_inst.016', 'SM_VK_TownWall_Tower_Round_inst.006', (1670.2, 74.0, 3.0), (1671.0, 75.0, 3.0))\n(5.71, 'SM_VK_Tree
# _Pine_B_inst.169', 'SM_VK_TownWall_Tower_Round_inst.007', (1669.7, 143.3, 7.5), (1671.0, 138.0, 3.0))\n(5.2, 'SM_VK_Tree_Oak_A_inst.053', 'SM_VK_TownW
# all_Tower_Round_inst.005', (1645.2, 143.6, 4.5), (1650.0, 138.0, 3.0))\n(5.14, 'SM_VK_Tree_Pine_B_inst.170', 'SM_VK_TownWall_Tower_Round_inst.007', (1
# 672.1, 142.5, 7.5), (1671.0, 138.0, 3.0))\n(5.12, 'SM_VK_Tree_Pine_B_inst.172', 'SM_VK_TownWall_Tower_Round_inst.007', (1675.9, 143.3, 7.5), (1671.0, 
# 138.0, 3.0))\n(4.7, 'SM_VK_Tree_Pine_A_inst.158', 'SM_VK_TownWall_Tower_Round_inst.001', (1589.6, 142.2, 6.0), (1587.0, 138.0, 3.0))\n(4.56, 'SM_VK_Tr

# ==============================================================================================================
# [0009] 2026-09-23 17:00:52  blender  ok
# ==============================================================================================================
import bpy, re
D=bpy.app.driver_namespace["_rv_build_D"]
WALLISH=("TownWall_","Gatehouse_Block")
walls=[d for d in D if any(w in d[1] for w in WALLISH)]
res=[]
for d in D:
    if any(w in d[1] for w in WALLISH) or 'LipGrass' in d[1]: continue
    p=d[4]
    for w in walls:
        if w[2].x+0.2<p.x<w[3].x-0.2 and w[2].y+0.2<p.y<w[3].y-0.2 and w[2].z-0.5<p.z<w[3].z:
            res.append((d[0],tuple(round(a,2) for a in p),w[0],tuple(round(a,1) for a in w[4]))); break
print(len(res))
for r in res: print(r)
# ---- result ----
# {"result":"Code executed successfully: 97\n('SM_VK_Gatehouse_Portcullis_inst', (1627.5, 72.6, 5.2), 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0))
# \n('SM_VK_Gatehouse_GateLeaf_inst', (1625.9, 73.8, 3.0), 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0))\n('SM_VK_Gatehouse_GateLeaf_inst.001', (16
# 29.1, 73.8, 3.0), 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0))\n('SM_VK_Wall_Timber_Window_inst.241', (1627.5, 72.0, 9.2), 'SM_VK_Gatehouse_Bloc
# k_inst', (1627.5, 75.0, 3.0))\n('SM_VK_Wall_Timber_X_inst.033', (1624.5, 78.0, 9.2), 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0))\n('SM_VK_Wall_
# Timber_Window_inst.242', (1627.5, 78.0, 9.2), 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0))\n('SM_VK_Wall_Timber_K_inst.046', (1630.5, 78.0, 9.2)
# , 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0, 3.0))\n('SM_VK_Wall_Timber_Door_inst', (1623.0, 76.5, 9.2), 'SM_VK_Gatehouse_Block_inst', (1627.5, 75.0

# ==============================================================================================================
# [0010] 2026-09-23 17:01:27  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for n in ("SM_VK_TownWall_Tower_Round_inst","SM_VK_Gatehouse_Block_inst","SM_VK_TownWall_Straight_inst","SM_VK_Wall_Stone_inst.206","SM_VK_Corner_Stone_inst.185"):
    o=bpy.data.objects[n]
    bb=[Vector(c) for c in o.bound_box]
    print(n, o.data.name, [round(min(v[k] for v in bb),2) for k in range(3)],[round(max(v[k] for v in bb),2) for k in range(3)], tuple(round(a,2) for a in o.location), round(o.rotation_euler.z,3), tuple(o.scale))
# tower mesh vertex extents at different z bands
o=bpy.data.objects["SM_VK_TownWall_Tower_Round_inst"]
import collections
vs=[v.co for v in o.data.vertices]
for z0 in (-1.5,0,1,3,5,7,9,11):
    band=[v for v in vs if z0<=v.z<z0+1]
    if band: print(z0, round(min(v.y for v in band),2), round(max(v.y for v in band),2), round(min(v.x for v in band),2), round(max(v.x for v in band),2))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Tower_Round_inst VAR_5484851763361861047 [-3.59, -3.57, -1.5] [3.57, 3.57, 12.47] (1587.0, 75.0,
#  3.0) 0.0 (1.0, 1.0, 1.0)\nSM_VK_Gatehouse_Block_inst SM_VK_Gatehouse_Block [-5.31, -5.32, -1.5] [5.33, 3.25, 9.0] (1627.5, 75.0, 3.0) 0.0 (1.0, 1.0, 
# 1.0)\nSM_VK_TownWall_Straight_inst SM_VK_TownWall_Straight [-1.95, -1.64, -1.5] [1.5, 1.18, 7.95] (1570.5, 75.0, 3.0) 0.0 (1.0, 1.0, 1.0)\nSM_VK_Wall_
# Stone_inst.206 VAR_5690991354041337471 [-1.52, -0.53, -0.11] [1.52, 0.28, 3.0] (1630.5, 78.0, 3.0) 6.283 (1.0, 1.0, 1.0)\nSM_VK_Corner_Stone_inst.185 
# VAR_243081928192398136 [-0.62, -0.6, -0.06] [0.65, 0.65, 3.01] (1629.0, 78.0, 3.0) 6.283 (1.0, 1.0, 1.0)\n-1.5 -3.32 3.32 -3.32 3.32\n0 -3.57 3.57 -3.
# 57 3.57\n1 -3.09 3.3 -3.09 3.09\n3 -3.08 3.08 -3.0 3.0\n5 -3.13 3.13 -3.13 3.13\n7 -3.33 3.33 -3.13 3.13\n9 -3.44 3.44 -3.44 3.44\n11 0.07 1.67 -0.03 

# ==============================================================================================================
# [0011] 2026-09-23 17:02:15  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=bpy.app.driver_namespace["_rv_build_D"]
cache={}
def bvh(name):
    if name in cache: return cache[name]
    o=bpy.data.objects[name]; M=o.matrix_world
    me=o.data
    vs=[M@v.co for v in me.vertices]
    t=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in me.polygons])
    cache[name]=(t,vs); return cache[name]
WALLISH=("TownWall_","Gatehouse_Block")
walls=[d for d in D if any(w in d[1] for w in WALLISH)]
STRUCT=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Scaffold|Def_Bartizan|Tree_|Prop_|MarketStall|Banner|Sign)')
hits=[]
for d in D:
    if any(w in d[1] for w in WALLISH) or not STRUCT.match(d[1]): continue
    for w in walls:
        if min(d[3].x,w[3].x)>max(d[2].x,w[2].x) and min(d[3].y,w[3].y)>max(d[2].y,w[2].y) and min(d[3].z,w[3].z)>max(d[2].z,w[2].z):
            a,va=bvh(d[0]); b,vb=bvh(w[0])
            ov=a.overlap(b)
            if ov:
                # depth estimate: max distance of d's verts inside... approximate by counting
                hits.append((d[0],w[0],len(ov),tuple(round(x,1) for x in d[4])))
print(len(hits))
import collections
byw=collections.defaultdict(list)
for h in hits: byw[h[1]].append(h)
for w,hs in byw.items():
    print("==",w, bpy.data.objects[w].location[:])
    for h in hs: print("   ",h[0],h[2],h[3])
# ---- result ----
# {"result":"Code executed successfully: 216\n== SM_VK_Gatehouse_Block_inst (1627.5, 75.0, 3.0)\n SM_VK_Wall_Timber_Window_inst.241 187 (1627.5, 72.0, 9
# .2)\n SM_VK_Wall_Timber_Door_inst 45 (1623.0, 76.5, 9.2)\n SM_VK_Wall_Timber_inst.038 104 (1623.0, 73.5, 9.2)\n SM_VK_Wall_Timber_Door_inst.001 45 (16
# 32.0, 76.5, 9.2)\n SM_VK_Wall_Timber_inst.039 111 (1632.0, 73.5, 9.2)\n SM_VK_Roof_Hip_inst.010 234 (1624.5, 75.0, 12.0)\n SM_VK_Roof_Mid_inst.028 113
#  (1627.5, 75.0, 12.0)\n SM_VK_Roof_Hip_inst.011 232 (1630.5, 75.0, 12.0)\n SM_VK_Roof_Cone_R2_inst 96 (1624.5, 72.0, 12.0)\n SM_VK_Roof_Cone_R2_inst.0
# 01 95 (1630.5, 72.0, 12.0)\n SM_VK_Wall_Stone_inst.200 149 (1629.0, 79.5, 3.0)\n SM_VK_Wall_Stone_inst.205 61 (1633.5, 78.0, 3.0)\n SM_VK_Wall_Stone_i
# nst.206 404 (1630.5, 78.0, 3.0)\n SM_VK_Corner_Stone_inst.185 469 (1629.0, 78.0, 3.0)\n SM_VK_Wall_Timber_Window_inst.331 239 (1629.0, 79.5, 6.0)\n SM

# ==============================================================================================================
# [0012] 2026-09-23 17:03:32  blender  ok
# ==============================================================================================================
import bpy, re, math
D=bpy.app.driver_namespace["_rv_build_D"]
W=[d for d in D if re.match(r'^SM_VK_(Wall_|Chapel_Wall)',d[1]) and not d[1].startswith('SM_VK_Wall_Posts')]
print(len(W))
pairs=[]
for a in range(len(W)):
    for b in range(a+1,len(W)):
        A=W[a];B=W[b]
        pa,pb=A[4],B[4]
        if abs(pa.z-pb.z)>1.0: continue
        dx,dy=abs(pa.x-pb.x),abs(pa.y-pb.y)
        if dx<1.2 and dy<1.2:
            ra,rb=A[5]%180,B[5]%180
            pairs.append((A[0],B[0],tuple(round(v,2) for v in pa),tuple(round(v,2) for v in pb),A[5],B[5]))
print(len(pairs))
for p in pairs: print(p)
# ---- result ----
# {"result":"Code executed successfully: 679\n0\n"}

# ==============================================================================================================
# [0013] 2026-09-23 17:04:16  blender  ERROR
# ==============================================================================================================
import bpy, re
from mathutils.bvhtree import BVHTree
D=bpy.app.driver_namespace["_rv_build_D"]
cache={}
def bvh(name):
    if name in cache: return cache[name]
    o=bpy.data.objects[name]; M=o.matrix_world; me=o.data
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); cache[name]=t; return t
STR=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Def_|Wall_Stone|Palisade|Scaffold|Gatehouse|TownWall|Mill|Windmill|Granary|Quay|Bridge)')
TREE=re.compile(r'^SM_VK_(Tree_|Bush_Large|Bush_Hydrangea)')
S=[d for d in D if STR.match(d[1])]
T=[d for d in D if TREE.match(d[1])]
# spatial hash
from collections import defaultdict
grid=defaultdict(list)
for s in S:
    for gx in range(int(s[2].x//6),int(s[3].x//6)+1):
        for gy in range(int(s[2].y//6),int(s[3].y//6)+1): grid[(gx,gy)].append(s)
res=defaultdict(list)
for t in T:
    cand=set()
    for gx in range(int(t[2].x//6),int(t[3].x//6)+1):
        for gy in range(int(t[2].y//6),int(t[3].y//6)+1):
            for s in grid[(gx,gy)]: cand.add(s)
    for s in cand:
        if 'TownWall' in s[1] or 'Gatehouse_Block' in s[1]: continue
        if min(t[3].x,s[3].x)>max(t[2].x,s[2].x) and min(t[3].y,s[3].y)>max(t[2].y,s[2].y) and min(t[3].z,s[3].z)>max(t[2].z,s[2].z):
            ov=bvh(t[0]).overlap(bvh(s[0]))
            if len(ov)>5: res[t[0]].append((s[0],len(ov)))
for k,v in sorted(res.items(), key=lambda kv:-sum(x[1] for x in kv[1])):
    o=bpy.data.objects[k]
    print(k, tuple(round(a,1) for a in o.location), round(o.scale.x,2), sorted(v,key=lambda x:-x[1])[:5])
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: Vector is not frozen (mutable), call freeze first"}

# ==============================================================================================================
# [0014] 2026-09-23 17:04:53  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils.bvhtree import BVHTree
D=bpy.app.driver_namespace["_rv_build_D"]
byname={d[0]:d for d in D}
cache={}
def bvh(name):
    if name in cache: return cache[name]
    o=bpy.data.objects[name]; M=o.matrix_world; me=o.data
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); cache[name]=t; return t
STR=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Def_|Wall_Stone|Palisade|Scaffold|Gatehouse|Mill|Windmill|Granary|Quay|Bridge|Watermill|Tower)')
TREE=re.compile(r'^SM_VK_(Tree_|Bush_Large|Bush_Hydrangea)')
S=[d for d in D if STR.match(d[1])]
T=[d for d in D if TREE.match(d[1])]
from collections import defaultdict
grid=defaultdict(list)
for s in S:
    for gx in range(int(s[2].x//6),int(s[3].x//6)+1):
        for gy in range(int(s[2].y//6),int(s[3].y//6)+1): grid[(gx,gy)].append(s[0])
res=defaultdict(list)
for t in T:
    cand=set()
    for gx in range(int(t[2].x//6),int(t[3].x//6)+1):
        for gy in range(int(t[2].y//6),int(t[3].y//6)+1): cand.update(grid[(gx,gy)])
    for sn in cand:
        s=byname[sn]
        if min(t[3].x,s[3].x)>max(t[2].x,s[2].x) and min(t[3].y,s[3].y)>max(t[2].y,s[2].y) and min(t[3].z,s[3].z)>max(t[2].z,s[2].z):
            ov=bvh(t[0]).overlap(bvh(sn))
            if len(ov)>5: res[t[0]].append((sn,len(ov)))
for k,v in sorted(res.items(), key=lambda kv:-sum(x[1] for x in kv[1])):
    o=bpy.data.objects[k]
    print(k, tuple(round(a,1) for a in o.location), round(o.scale.x,2), sorted(v,key=lambda x:-x[1])[:4])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Blossom_inst.009 (1664.7, 136.0, 3.0) 1.0 [('SM_VK_Roof_Gable_inst.084', 125)]\nSM_VK_Tree_Willow_in
# st.002 (1531.6, 32.3, 0.0) 1.0 [('SM_VK_Bridge_Wood_End_inst', 64)]\nSM_VK_Tree_Willow_inst.005 (1622.3, 30.8, 0.0) 1.0 [('SM_VK_Bridge_Stone_Ramp_ins
# t.001', 64)]\nSM_VK_Tree_Blossom_inst.005 (1620.7, 77.2, 3.0) 1.0 [('SM_VK_Gatehouse_Block_inst', 52)]\nSM_VK_Tree_Willow_inst.013 (1606.9, 49.6, 0.0)
#  1.0 [('SM_VK_Quay_Post_inst.002', 28), ('SM_VK_Quay_Stair_inst', 10)]\nSM_VK_Tree_Blossom_inst.007 (1667.6, 124.7, 3.0) 1.0 [('SM_VK_Porch_inst.032',
#  19)]\nSM_VK_Tree_Blossom_inst.008 (1664.4, 132.3, 3.0) 1.0 [('SM_VK_Wall_Stone_Window_inst.180', 6)]\n"}

# ==============================================================================================================
# [0015] 2026-09-23 17:05:13  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils.bvhtree import BVHTree
D=bpy.app.driver_namespace["_rv_build_D"]
byname={d[0]:d for d in D}
cache={}
def bvh(name):
    if name in cache: return cache[name]
    o=bpy.data.objects[name]; M=o.matrix_world; me=o.data
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); cache[name]=t; return t
STR=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Def_|Palisade|Scaffold|Gatehouse|TownWall|Mill|Windmill|Granary|Quay|Bridge|Tower|LowWall|Stockpile_Border|MarketStall|Tent)')
PROP=re.compile(r'^SM_VK_(Prop_|Pile_|Animal_|Crop_|MarketStall|Tent|Stump|Rock_Boulder|Tree_|Bush_)')
ATT=('FlowerBox','Lantern','Sign','Banner','ShopGoods','Laundry','Bunting','Planter')
S=[d for d in D if STR.match(d[1])]
P=[d for d in D if PROP.match(d[1]) and not any(a in d[1] for a in ATT)]
from collections import defaultdict
grid=defaultdict(list)
for s in S:
    for gx in range(int(s[2].x//6),int(s[3].x//6)+1):
        for gy in range(int(s[2].y//6),int(s[3].y//6)+1): grid[(gx,gy)].append(s[0])
res=defaultdict(list)
for t in P:
    cand=set()
    for gx in range(int(t[2].x//6),int(t[3].x//6)+1):
        for gy in range(int(t[2].y//6),int(t[3].y//6)+1): cand.update(grid[(gx,gy)])
    cand.discard(t[0])
    for sn in cand:
        s=byname[sn]
        if 'Tree_' in t[1] and ('TownWall' in sn or 'Gatehouse_Block' in sn): continue
        if min(t[3].x,s[3].x)>max(t[2].x,s[2].x) and min(t[3].y,s[3].y)>max(t[2].y,s[2].y) and min(t[3].z,s[3].z)>max(t[2].z,s[2].z):
            ov=bvh(t[0]).overlap(bvh(sn))
            if len(ov)>3: res[t[0]].append((sn,len(ov)))
out=sorted(res.items(), key=lambda kv:-sum(x[1] for x in kv[1]))
print(len(out))
for k,v in out[:70]:
    o=bpy.data.objects[k]
    print(k, tuple(round(a,1) for a in o.location), sorted(v,key=lambda x:-x[1])[:3])
# ---- result ----
# {"result":"Code executed successfully: 80\nSM_VK_Prop_Crates_inst.014 (1576.1, 86.2, 3.0) [('SM_VK_LowWall_inst.030', 881), ('SM_VK_LowWall_Post_inst.
# 019', 99), ('SM_VK_LowWall_Post_inst.017', 36)]\nSM_VK_Prop_Fence_inst.162 (1524.0, 1.5, 1.5) [('SM_VK_Corner_Wattle_inst.001', 196), ('SM_VK_Wall_Wat
# tle_inst.002', 190), ('SM_VK_Wall_Wattle_Byre_inst', 177)]\nSM_VK_Prop_Fence_inst.158 (1525.5, 9.0, 1.5) [('SM_VK_Corner_Wattle_inst.002', 277), ('SM_
# VK_Wall_Wattle_inst.003', 176), ('SM_VK_Wall_Wattle_inst.008', 96)]\nSM_VK_Prop_FenceGate_inst.021 (1539.0, 16.5, 1.5) [('SM_VK_LowWall_Post_inst.014'
# , 143), ('SM_VK_LowWall_Post_inst.013', 141), ('SM_VK_LowWall_inst.028', 116)]\nSM_VK_Prop_Fence_inst.183 (1537.5, 78.0, 3.0) [('SM_VK_Wall_Shed_Windo
# w_inst.002', 166), ('SM_VK_Wall_Shed_Window_inst.003', 150), ('SM_VK_Corner_Shed_inst.006', 90)]\nSM_VK_Bush_Round_inst.043 (1567.8, 91.0, 3.0) [('SM_

# ==============================================================================================================
# [0016] 2026-09-23 17:05:54  blender  ok
# ==============================================================================================================
import bpy
col=bpy.data.collections["VK_ValleyTown"]
L=list(col.objects)
print(len(L), len(col.children))
# print segments where consecutive objects jump > 12m
prev=None; segs=[]; start=0
for k,o in enumerate(L):
    p=o.location
    if prev is not None and (p.xy-prev.xy).length>14:
        segs.append((start,k-1)); start=k
    prev=p.copy()
segs.append((start,len(L)-1))
print(len(segs))
for s,e in segs[:400]:
    if e-s<3: continue
    xs=[L[k].location.x for k in range(s,e+1)]; ys=[L[k].location.y for k in range(s,e+1)]
    print(s,e,L[s].name,L[e].name, round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)))
# ---- result ----
# {"result":"Code executed successfully: 5568 0\n481\n35 38 SM_VK_TownWall_Straight_inst.035 SM_VK_TownWall_Straight_inst.038 1622 1630 138 138\n135 155
#  SM_VK_Gatehouse_Block_inst SM_VK_Banner_Wall_inst.001 1623 1632 72 78\n156 159 SM_VK_Bridge_Stone_Span_inst SM_VK_Bridge_Stone_Ramp_inst 1626 1626 39
#  50\n165 175 SM_VK_Bridge_Wood_End_inst SM_VK_Bridge_Wood_Bent_inst.004 1538 1538 34 50\n176 231 SM_VK_Wall_Stone_Window_inst.132 SM_VK_Prop_BarrelSta
# ck_inst.007 1575 1586 45 59\n232 241 SM_VK_Quay_Straight_inst.004 SM_VK_Prop_BarrelStack_inst.009 1599 1611 46 51\n242 253 SM_VK_Wall_Posts_inst SM_VK
# _Prop_Bench_inst.011 1637 1645 48 54\n254 267 SM_VK_Wall_Stone_Door_inst.035 SM_VK_Prop_BarrelStack_inst.010 1655 1661 48 54\n268 293 SM_VK_Wall_Shed_
# Door_inst SM_VK_Prop_BarrelStack_inst.011 1686 1698 17 32\n296 307 SM_VK_Wall_Wattle_inst SM_VK_Wall_Wattle_inst.007 1509 1522 3 9\n313 335 SM_VK_Corn

# ==============================================================================================================
# [0017] 2026-09-23 17:06:19  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils.bvhtree import BVHTree
from collections import defaultdict
col=bpy.data.collections["VK_ValleyTown"]
L=list(col.objects)
seg={}; sid=0; prev=None
for k,o in enumerate(L):
    p=o.location
    if prev is not None and (p.xy-prev.xy).length>14: sid+=1
    seg[o.name]=sid; prev=p.copy()
bpy.app.driver_namespace["_rv_seg"]=seg
D=bpy.app.driver_namespace["_rv_build_D"]
byname={d[0]:d for d in D}
STR=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Def_|Palisade|Scaffold|Gatehouse|Mill|Windmill|Granary|Quay|Bridge|Tower|BellTower|Dormer|Emblem|Wall_Stone)')
S=[d for d in D if STR.match(d[1]) and 'TownWall' not in d[1] and 'Gatehouse_Block' not in d[1]]
cache={}
def bvh(name):
    if name in cache: return cache[name]
    o=bpy.data.objects[name]; M=o.matrix_world; me=o.data
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); cache[name]=t; return t
grid=defaultdict(list)
for s in S:
    for gx in range(int(s[2].x//6),int(s[3].x//6)+1):
        for gy in range(int(s[2].y//6),int(s[3].y//6)+1): grid[(gx,gy)].append(s[0])
done=set(); res=defaultdict(int); ex={}
for cell,names in grid.items():
    for a in range(len(names)):
        for b in range(a+1,len(names)):
            na,nb=names[a],names[b]
            if seg[na]==seg[nb]: continue
            key=(na,nb) if na<nb else (nb,na)
            if key in done: continue
            done.add(key)
            A=byname[na];B=byname[nb]
            if min(A[3].x,B[3].x)>max(A[2].x,B[2].x) and min(A[3].y,B[3].y)>max(A[2].y,B[2].y) and min(A[3].z,B[3].z)>max(A[2].z,B[2].z):
                ov=bvh(na).overlap(bvh(nb))
                if len(ov)>3:
                    sk=(seg[na],seg[nb]) if seg[na]<seg[nb] else (seg[nb],seg[na])
                    res[sk]+=len(ov); ex.setdefault(sk,[]).append((na,nb,len(ov)))
for sk,v in sorted(res.items(), key=lambda kv:-kv[1]):
    e=sorted(ex[sk],key=lambda x:-x[2])[:4]
    print(sk, v, [(x[0],x[1],x[2], tuple(round(c,1) for c in bpy.data.objects[x[0]].location)) for x in e])
# ---- result ----
# {"result":"Code executed successfully: (184, 185) 2491 [('SM_VK_Roof_Mid_CapR_inst.001', 'SM_VK_Wall_PlasterUp_Window_inst.015', 368, (1657.5, 81.0, 8
# .8)), ('SM_VK_Wall_Stone_Window_inst.171', 'SM_VK_Corner_Stone_inst.174', 249, (1657.5, 84.0, 3.0)), ('SM_VK_Wall_Stone_inst.187', 'SM_VK_Corner_Stone
# _inst.175', 220, (1657.5, 78.0, 3.0)), ('SM_VK_Wall_StoneUp_inst.013', 'SM_VK_Corner_PlasterUp_inst.017', 178, (1657.5, 78.0, 6.0))]\n(144, 148) 2093 
# [('SM_VK_Wall_Wattle_Door_inst', 'SM_VK_Corner_Wattle_inst.003', 393, (1509.0, 7.5, 1.5)), ('SM_VK_Wall_Wattle_Door_inst', 'SM_VK_RoofThatch_Gable_Cru
# ck_inst', 313, (1509.0, 7.5, 1.5)), ('SM_VK_Wall_Wattle_Window_inst.002', 'SM_VK_Corner_Wattle_inst.003', 288, (1510.5, 9.0, 1.5)), ('SM_VK_Wall_Wattl
# e_inst.007', 'SM_VK_RoofThatch_Gable_Cruck_inst', 270, (1509.0, 4.5, 1.5))]\n(159, 162) 861 [('SM_VK_Palisade_Straight_inst.004', 'SM_VK_Palisade_Post

# ==============================================================================================================
# [0018] 2026-09-23 17:07:03  blender  ok
# ==============================================================================================================
import bpy
col=bpy.data.collections["VK_ValleyTown"]
L=list(col.objects)
for k in range(1824,2210):
    o=L[k]
    if k<1840 or 'Chimney' in o.name or k>2175:
        print(k,o.name,tuple(round(a,1) for a in o.location))
# ---- result ----
# {"result":"Code executed successfully: 1824 SM_VK_Prop_MarketCross_inst.001 (1626.0, 100.5, 3.0)\n1825 SM_VK_Prop_Well_inst.003 (1620.0, 102.0, 3.0)\n
# 1826 SM_VK_MarketStall_inst.013 (1616.0, 97.5, 3.0)\n1827 SM_VK_MarketStall_inst.014 (1616.0, 104.0, 3.0)\n1828 SM_VK_MarketStall_inst.015 (1634.0, 97
# .5, 3.0)\n1829 SM_VK_MarketStall_inst.016 (1637.0, 103.0, 3.0)\n1830 SM_VK_Prop_LampPost_inst.032 (1609.5, 96.0, 3.0)\n1831 SM_VK_Prop_LampPost_inst.0
# 33 (1642.5, 96.0, 3.0)\n1832 SM_VK_Prop_LampPost_inst.034 (1609.5, 105.0, 3.0)\n1833 SM_VK_Prop_LampPost_inst.035 (1642.5, 105.0, 3.0)\n1834 SM_VK_Pro
# p_Stocks_inst.001 (1630.0, 105.5, 3.0)\n1835 SM_VK_Banner_Pole_inst.003 (1640.0, 101.5, 3.0)\n1836 SM_VK_Wall_Stone_Door_inst.051 (1629.0, 85.5, 3.0)\
# n1837 SM_VK_Porch_inst.033 (1629.0, 85.5, 3.0)\n1838 SM_VK_Wall_Stone_inst.199 (1629.0, 82.5, 3.0)\n1839 SM_VK_Deco_Weeds_inst.178 (1629.0, 82.5, 3.0)

# ==============================================================================================================
# [0019] 2026-09-23 17:07:36  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils.bvhtree import BVHTree
from collections import defaultdict
col=bpy.data.collections["VK_ValleyTown"]
L=list(col.objects)
R=[("gatehouse",135,155),("watermill",176,231),("quay",232,241),("lavoir",242,253),("smokehouse",254,267),("fisher",268,295),
("south_hamlet",296,469),("camp",494,509),("sawpit",510,525),("palisade",526,560),("training",561,644),("tannery",645,688),("pottery_dyers_apiary",689,722),
("windmill",723,726),("granary",727,757),("sites",758,874),("logcabin_woodcutter",875,932),("forester",933,963),("mine",964,978),("quarry",979,996),
("merchant",997,1078),("gablefront",1079,1139),("corner_house",1140,1222),("tower_house",1223,1293),("skyline",1294,1527),("terrace",1529,1683),
("festival",1684,1716),("brewery",1717,1768),("chapel",1769,1789),("blacksmith",1790,1823),("plaza",1824,1835)]
ends=[1874,1916,1955,1996,2029,2074,2112,2146,2179]; s=1836
for k,e in enumerate(ends): R.append((f"infill{k}",s,e)); s=e+1
bid={}
for name,a,b in R:
    for k in range(a,b+1): bid[L[k].name]=name
bpy.app.driver_namespace["_rv_bid"]=bid
for name,a,b in R:
    if name.startswith("infill"):
        xs=[L[k].location.x for k in range(a,b+1)]; ys=[L[k].location.y for k in range(a,b+1)]
        print(name, round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1))
D=bpy.app.driver_namespace["_rv_build_D"]; byname={d[0]:d for d in D}
STR=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chimney|Chapel_|Porch|Gallery|Turret|Foundation|LeanTo|Def_|Palisade|Scaffold|Gatehouse|Mill|Windmill|Granary|Quay|Bridge|Tower|BellTower|Dormer|Emblem)')
S=[d for d in D if d[0] in bid and STR.match(d[1])]
cache={}
def bvh(name):
    if name in cache: return cache[name]
    o=bpy.data.objects[name]; M=o.matrix_world; me=o.data
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); cache[name]=t; return t
grid=defaultdict(list)
for d in S:
    for gx in range(int(d[2].x//6),int(d[3].x//6)+1):
        for gy in range(int(d[2].y//6),int(d[3].y//6)+1): grid[(gx,gy)].append(d[0])
done=set(); res=defaultdict(int); ex=defaultdict(list)
for cell,names in grid.items():
    for a in range(len(names)):
        for b in range(a+1,len(names)):
            na,nb=names[a],names[b]
            if bid[na]==bid[nb]: continue
            key=tuple(sorted((na,nb)))
            if key in done: continue
            done.add(key); A=byname[na];B=byname[nb]
            if min(A[3].x,B[3].x)>max(A[2].x,B[2].x) and min(A[3].y,B[3].y)>max(A[2].y,B[2].y) and min(A[3].z,B[3].z)>max(A[2].z,B[2].z):
                ov=len(bvh(na).overlap(bvh(nb)))
                if ov>0:
                    sk=tuple(sorted((bid[na],bid[nb]))); res[sk]+=ov; ex[sk].append((na,nb,ov))
for sk,v in sorted(res.items(), key=lambda kv:-kv[1]):
    e=sorted(ex[sk],key=lambda x:-x[2])[:5]
    print(sk,v,[(x[0],x[1],x[2],tuple(round(c,1) for c in bpy.data.objects[x[0]].location)) for x in e])
# ---- result ----
# {"result":"Code executed successfully: infill0 1629.0 1635.0 78.0 87.0\ninfill1 1622.2 1629.0 110.4 120.0\ninfill2 1674.0 1683.0 89.7 96.6\ninfill3 16
# 35.0 1644.0 107.7 114.5\ninfill4 1601.4 1642.5 99.0 111.0\ninfill5 1643.2 1650.6 92.4 102.0\ninfill6 1676.4 1686.0 81.0 87.6\ninfill7 1638.0 1644.6 81
# .0 87.8\ninfill8 1620.0 1626.0 125.7 132.0\n('gatehouse', 'infill0') 3981 [('SM_VK_Gatehouse_Block_inst', 'SM_VK_Wall_Timber_inst.054', 1006, (1627.5,
#  75.0, 3.0)), ('SM_VK_Gatehouse_Block_inst', 'SM_VK_Roof_Hip_inst.015', 531, (1627.5, 75.0, 3.0)), ('SM_VK_Gatehouse_Block_inst', 'SM_VK_Corner_Stone_
# inst.185', 469, (1627.5, 75.0, 3.0)), ('SM_VK_Gatehouse_Block_inst', 'SM_VK_Wall_Stone_inst.206', 404, (1627.5, 75.0, 3.0)), ('SM_VK_Gatehouse_Block_i
# nst', 'SM_VK_Corner_Timber_inst.201', 401, (1627.5, 75.0, 3.0))]\n('infill3', 'infill4') 228 [('SM_VK_Roof_Mid_inst.047', 'SM_VK_Roof_Dormer_inst.014'

# ==============================================================================================================
# [0020] 2026-09-23 17:07:58  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[o for o in tc.all_objects if o.type=='MESH' and 'Chunk' in o.name]
print(len(chunks), [o.name for o in chunks[:5]])
trees=[]
for o in chunks:
    M=o.matrix_world; me=o.data
    trees.append(BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]))
def h(x,y):
    best=None
    for t in trees:
        r=t.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)
        if r[0] is not None and (best is None or r[0].z>best): best=r[0].z
    return best
bpy.app.driver_namespace["_rv_h"]=h
print(h(1626,100), h(1626,60), h(1520,5))
# ---- result ----
# {"result":"Code executed successfully: 20 ['VKV_Chunk_0_0', 'VKV_Chunk_1_0', 'VKV_Chunk_2_0', 'VKV_Chunk_3_0', 'VKV_Chunk_4_0']\n3.0 1.5 1.5\n"}

# ==============================================================================================================
# [0021] 2026-09-23 17:08:21  blender  ok
# ==============================================================================================================
import bpy, re
from collections import defaultdict
h=bpy.app.driver_namespace["_rv_h"]
bid=bpy.app.driver_namespace["_rv_bid"]
D=bpy.app.driver_namespace["_rv_build_D"]
GR=re.compile(r'^SM_VK_(Wall_|Corner_|Porch|Foundation|Chapel_|Wall_Stone|Palisade_Straight|Palisade_Tower|LowWall|Quay|Gatehouse_Block|TownWall|Prop_|MarketStall|Tent|Crop_|Pile_|Stockpile|BuildSite|Windmill|Granary|Mill)')
out=[]
for d in D:
    if not GR.match(d[1]): continue
    o=bpy.data.objects[d[0]]
    base=o.location.z
    if base>d[2].z+0.8: continue  # skip upper storeys? (origin well above bbox min means hanging geometry)
    # only ground-floor pieces: origin z equal to a level multiple
    lv=round(base/1.5,3)
    if abs(lv-round(lv))>0.02: continue
    mn,mx=d[2],d[3]
    pts=[(o.location.x,o.location.y)]
    for x in (mn.x+0.25,mx.x-0.25):
        for y in (mn.y+0.25,mx.y-0.25): pts.append((x,y))
    hs=[h(x,y) for x,y in pts]
    hs=[v for v in hs if v is not None]
    if not hs: continue
    up=max(hs)-base; dn=base-min(hs)
    if up>0.3 or dn>0.45:
        out.append((round(up,2),round(dn,2),d[0],bid.get(d[0],'-'),tuple(round(a,1) for a in o.location)))
print(len(out))
byb=defaultdict(list)
for r in out: byb[r[3]].append(r)
for b,v in byb.items():
    print("==",b,len(v))
    for r in sorted(v,key=lambda r:-max(r[0],r[1]))[:8]: print("   ",r)
# ---- result ----
# {"result":"Code executed successfully: 252\n== watermill 16\n (-3.11, 3.67, 'SM_VK_Wall_Timber_Window_inst.249', 'watermill', (1582.5, 48.0, 3.0))\n (
# -3.11, 3.67, 'SM_VK_Wall_Timber_Window_inst.250', 'watermill', (1579.5, 48.0, 3.0))\n (-3.0, 3.04, 'SM_VK_Wall_Timber_inst.040', 'watermill', (1584.0,
#  49.5, 3.0))\n (-3.0, 3.02, 'SM_VK_Wall_Timber_Window_inst.245', 'watermill', (1578.0, 49.5, 3.0))\n (-3.0, 3.0, 'SM_VK_Wall_Timber_Window_inst.243', 
# 'watermill', (1578.0, 55.5, 3.0))\n (-3.0, 3.0, 'SM_VK_Wall_Timber_Window_inst.244', 'watermill', (1578.0, 52.5, 3.0))\n (-3.0, 3.0, 'SM_VK_Wall_Timbe
# r_Window_inst.246', 'watermill', (1584.0, 52.5, 3.0))\n (-3.0, 3.0, 'SM_VK_Wall_Timber_Window_inst.247', 'watermill', (1584.0, 55.5, 3.0))\n== lavoir 
# 2\n (0.85, 0.0, 'SM_VK_Prop_Laundry_inst.002', 'lavoir', (1641.2, 53.7, 0.0))\n (0.0, 0.58, 'SM_VK_Prop_HandPump_inst', 'lavoir', (1645.2, 48.3, 0.0))

# ==============================================================================================================
# [0022] 2026-09-23 17:08:55  blender  ok
# ==============================================================================================================
import bpy, re
from collections import defaultdict
h=bpy.app.driver_namespace["_rv_h"]
bid=bpy.app.driver_namespace["_rv_bid"]
D=bpy.app.driver_namespace["_rv_build_D"]
GR=re.compile(r'^SM_VK_(Wall_|Corner_|Porch|Foundation|Chapel_|Palisade_Straight|Palisade_Tower|LowWall|Quay|Gatehouse_Block|Windmill|Granary|Mill|BuildSite|Stockpile)')
bmin=defaultdict(lambda:1e9)
for d in D:
    if d[0] in bid and GR.match(d[1]): bmin[bid[d[0]]]=min(bmin[bid[d[0]]],bpy.data.objects[d[0]].location.z)
out=[]
for d in D:
    if d[0] not in bid or not GR.match(d[1]): continue
    o=bpy.data.objects[d[0]]; base=o.location.z
    if base>bmin[bid[d[0]]]+0.1: continue
    mn,mx=d[2],d[3]
    pts=[(o.location.x,o.location.y)]+[(x,y) for x in (mn.x+0.25,mx.x-0.25) for y in (mn.y+0.25,mx.y-0.25)]
    hs=[v for v in (h(x,y) for x,y in pts) if v is not None]
    if not hs: continue
    up=max(hs)-base; dn=base-min(hs)
    if up>0.3 or dn>0.45: out.append((round(up,2),round(dn,2),d[0],bid[d[0]],tuple(round(a,1) for a in o.location)))
byb=defaultdict(list)
for r in out: byb[r[3]].append(r)
for b,v in byb.items():
    print("==",b,len(v))
    for r in sorted(v,key=lambda r:-max(r[0],r[1]))[:6]: print("   ",r)
# ---- result ----
# {"result":"Code executed successfully: == gatehouse 1\n (0.0, 1.5, 'SM_VK_Gatehouse_Block_inst', 'gatehouse', (1627.5, 75.0, 3.0))\n== watermill 10\n 
# (-1.5, 1.5, 'SM_VK_Mill_WheelPier_inst', 'watermill', (1579.5, 44.9, 0.0))\n (-0.45, 1.03, 'SM_VK_Quay_Straight_inst', 'watermill', (1576.5, 47.6, 0.0
# ))\n (-0.45, 1.03, 'SM_VK_Quay_Straight_inst.001', 'watermill', (1579.5, 47.6, 0.0))\n (-0.45, 1.03, 'SM_VK_Quay_Straight_inst.002', 'watermill', (158
# 2.5, 47.6, 0.0))\n (-0.45, 1.03, 'SM_VK_Quay_Straight_inst.003', 'watermill', (1585.5, 47.6, 0.0))\n (-0.74, 0.96, 'SM_VK_Quay_Post_inst', 'watermill'
# , (1575.1, 47.5, 0.0))\n== smokehouse 3\n (-0.01, 0.67, 'SM_VK_Corner_Stone_inst.136', 'smokehouse', (1659.0, 48.0, 0.0))\n (-0.01, 0.65, 'SM_VK_Corne
# r_Stone_inst.135', 'smokehouse', (1656.0, 48.0, 0.0))\n (-0.09, 0.58, 'SM_VK_Wall_Stone_inst.143', 'smokehouse', (1657.5, 48.0, 0.0))\n== granary 12\n

# ==============================================================================================================
# [0023] 2026-09-23 17:09:34  blender  ok
# ==============================================================================================================
import bpy, re
from collections import defaultdict
h=bpy.app.driver_namespace["_rv_h"]
bid=bpy.app.driver_namespace["_rv_bid"]
D=bpy.app.driver_namespace["_rv_build_D"]
PR=re.compile(r'^SM_VK_(Prop_|MarketStall|Tent|Crop_|Pile_|Animal_|Stump|Rock_Boulder|Tree_|Bush_)')
out=[]
for d in D:
    if not PR.match(d[1]): continue
    if any(a in d[1] for a in ('FlowerBox','Lantern','Sign','Banner','ShopGoods','Laundry','Bunting','Planter','HoistBeam','Festoon','Rowboat','Barge')): continue
    o=bpy.data.objects[d[0]]; base=o.location.z
    lv=base/1.5
    if abs(lv-round(lv))>0.05: continue
    hc=h(o.location.x,o.location.y)
    if hc is None: continue
    if abs(hc-base)>0.3: out.append((round(hc-base,2),d[0],bid.get(d[0],'-'),tuple(round(a,1) for a in o.location)))
out.sort(key=lambda r:-abs(r[0]))
print(len(out))
for r in out[:60]: print(r)
# ---- result ----
# {"result":"Code executed successfully: 3\n(-1.55, 'SM_VK_Prop_Creels_inst', 'fisher', (1694.0, 32.0, 0.1))\n(-1.55, 'SM_VK_Pile_Fish_2_inst', 'fisher'
# , (1693.2, 25.2, 0.1))\n(0.84, 'SM_VK_Prop_FishRack_inst', 'smokehouse', (1656.9, 53.8, 0.0))\n"}

# ==============================================================================================================
# [0024] 2026-09-23 17:09:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_01_gate_inside",(1643,97,14),(1629,80,6),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_02_gate_outside",(1616,50,16),(1628,75,8),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_01_gate_inside.png\nC:\\Users\\danie\\AppData\\Roaming\\
# Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\b
# uild\\review_build_02_gate_outside.png\n"}

# ==============================================================================================================
# [0025] 2026-09-23 17:10:50  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_03_gate_infill_top",(1619,94,24),(1630,78,8),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_04_corner_tower",(1597,94,13),(1609,78,7),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_03_gate_infill_top.png\nC:\\Users\\danie\\AppData\\Roami
# ng\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revie
# w\\build\\review_build_04_corner_tower.png\n"}

# ==============================================================================================================
# [0026] 2026-09-23 17:11:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_05_corner_tower_top",(1604,88,30),(1609,77,6),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_06_terrace_towers",(1660,62,22),(1660,79,8),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_05_corner_tower_top.png\nC:\\Users\\danie\\AppData\\Roam
# ing\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revi
# ew\\build\\review_build_06_terrace_towers.png\n"}

# ==============================================================================================================
# [0027] 2026-09-23 17:12:36  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_07_terrace_back_top",(1664,98,30),(1661,78,8),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_08_blacksmith_NEtower",(1660,118,16),(1671,135,5),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_07_terrace_back_top.png\nC:\\Users\\danie\\AppData\\Roam
# ing\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revi
# ew\\build\\review_build_08_blacksmith_NEtower.png\n"}

# ==============================================================================================================
# [0028] 2026-09-23 17:13:43  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_09_blacksmith_side",(1685,126,7),(1671,134,5),lens=28,res=(1600,900),outdir=OD))
print(shot("review_build_10_northwall_trees",(1588,124,14),(1591,140,5),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_09_blacksmith_side.png\nC:\\Users\\danie\\AppData\\Roami
# ng\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revie
# w\\build\\review_build_10_northwall_trees.png\n"}

# ==============================================================================================================
# [0029] 2026-09-23 17:14:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_10_northwall_trees",(1586,116,30),(1590,139,4),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_11_NE_corner_trees",(1676,122,26),(1684,139,4),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_10_northwall_trees.png\nC:\\Users\\danie\\AppData\\Roami
# ng\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revie
# w\\build\\review_build_11_NE_corner_trees.png\n"}

# ==============================================================================================================
# [0030] 2026-09-23 17:15:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_12_merchant_yard",(1586,94,7),(1578,85,3),lens=28,res=(1600,900),outdir=OD))
print(shot("review_build_13_forester",(1545,68,8),(1537.5,77,2),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_12_merchant_yard.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\
# \build\\review_build_13_forester.png\n"}

# ==============================================================================================================
# [0031] 2026-09-23 17:15:49  blender  ok
# ==============================================================================================================
import bpy
D={d[0]:d for d in bpy.app.driver_namespace["_rv_build_D"]}
for n in ["SM_VK_Crop_TreeNursery_inst","SM_VK_Prop_Fence_inst.183","SM_VK_Prop_FenceGate_inst.024","SM_VK_Wall_Shed_Window_inst.002","SM_VK_Wall_Shed_Window_inst.003","SM_VK_Corner_Shed_inst.006","SM_VK_Corner_Shed_inst.005","SM_VK_Wall_Shed_Door_inst.001"]:
    d=D[n]; print(n, tuple(round(a,2) for a in d[2]), tuple(round(a,2) for a in d[3]), d[5])
import re
bid=bpy.app.driver_namespace["_rv_bid"]
col=bpy.data.collections["VK_ValleyTown"]; L=list(col.objects)
for k in range(933,964):
    o=L[k]; print(k,o.name,tuple(round(a,2) for a in o.location), round(o.rotation_euler.z*57.3))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Crop_TreeNursery_inst (1536.0, 75.05, 3.0) (1538.98, 77.99, 4.45) 0\nSM_VK_Prop_Fence_inst.183 (1535.91, 
# 77.81, 3.0) (1539.09, 78.09, 4.18) 180\nSM_VK_Prop_FenceGate_inst.024 (1535.9, 74.9, 3.0) (1539.1, 75.18, 4.3) 0\nSM_VK_Wall_Shed_Window_inst.002 (153
# 2.98, 77.76, 2.39) (1536.07, 78.53, 5.6) 180\nSM_VK_Wall_Shed_Window_inst.003 (1535.76, 74.93, 2.39) (1536.53, 78.02, 5.6) 90\nSM_VK_Corner_Shed_inst.
# 006 (1535.79, 77.78, 2.39) (1536.34, 78.33, 5.61) 180\nSM_VK_Corner_Shed_inst.005 (1535.78, 74.66, 2.39) (1536.33, 75.21, 5.61) 90\nSM_VK_Wall_Shed_Do
# or_inst.001 (1532.93, 74.22, 2.39) (1536.02, 75.24, 5.6) 0\n933 SM_VK_Wall_Shed_Door_inst.001 (1534.5, 75.0, 3.0) 0\n934 SM_VK_Wall_Shed_Window_inst.0
# 02 (1534.5, 78.0, 3.0) 180\n935 SM_VK_Wall_Shed_inst.003 (1533.0, 76.5, 3.0) -90\n936 SM_VK_Wall_Shed_Window_inst.003 (1536.0, 76.5, 3.0) 90\n937 SM_V

# ==============================================================================================================
# [0032] 2026-09-23 17:16:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_14_longhouse",(1533,-8,10),(1520,5,2),lens=28,res=(1600,900),outdir=OD))
print(shot("review_build_15_hamlet_wide",(1540,-22,38),(1540,12,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_14_longhouse.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\bui
# ld\\review_build_15_hamlet_wide.png\n"}

# ==============================================================================================================
# [0033] 2026-09-23 17:17:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
col=bpy.data.collections["VK_ValleyTown"]; L=list(col.objects)
for k in range(561,645):
    o=L[k]
    if any(s in o.name for s in ("Fence","Wall_","Corner_","Rack","Barrel","Porch","Gallery","Armor")): print(k,o.name,tuple(round(a,2) for a in o.location), round(o.rotation_euler.z*57.3))
print(shot("review_build_16_barracks",(1672,-8,14),(1686,6,3),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: 561 SM_VK_Prop_BarrelStack_inst.013 (1651.7, 15.8, 1.5) 90\n568 SM_VK_Wall_Stone_inst.146 (1686.0, 1.5, 1.5) 90
# \n571 SM_VK_Wall_Stone_Door_inst.036 (1686.0, 4.5, 1.5) 90\n574 SM_VK_Porch_inst.026 (1686.0, 4.5, 1.5) 90\n575 SM_VK_Wall_Stone_Window_inst.137 (1686
# .0, 7.5, 1.5) 90\n576 SM_VK_Wall_Stone_inst.147 (1686.0, 10.5, 1.5) 90\n578 SM_VK_Wall_Stone_Window_inst.138 (1680.0, 1.5, 1.5) 270\n579 SM_VK_Wall_St
# one_inst.148 (1680.0, 4.5, 1.5) 270\n582 SM_VK_Wall_Stone_inst.149 (1680.0, 7.5, 1.5) 270\n583 SM_VK_Wall_Stone_Window_inst.139 (1680.0, 10.5, 1.5) 27
# 0\n585 SM_VK_Wall_Stone_inst.150 (1684.5, -0.0, 1.5) 0\n586 SM_VK_Wall_Stone_inst.151 (1681.5, 0.0, 1.5) 0\n588 SM_VK_Wall_Stone_inst.152 (1681.5, 12.
# 0, 1.5) 180\n589 SM_VK_Wall_Stone_inst.153 (1684.5, 12.0, 1.5) 180\n590 SM_VK_Corner_Stone_inst.137 (1686.0, -0.0, 1.5) 90\n591 SM_VK_Corner_Stone_ins

# ==============================================================================================================
# [0034] 2026-09-23 17:18:19  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_17_barracks_gallery",(1696,9,4.5),(1686,5,3),lens=26,res=(1600,900),outdir=OD))
print(shot("review_build_18_lamppost_roof",(1600,112,12),(1609.5,105,6),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_17_barracks_gallery.png\nC:\\Users\\danie\\AppData\\Roam
# ing\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revi
# ew\\build\\review_build_18_lamppost_roof.png\n"}

# ==============================================================================================================
# [0035] 2026-09-23 17:18:57  blender  ok
# ==============================================================================================================
import bpy
D={d[0]:d for d in bpy.app.driver_namespace["_rv_build_D"]}
for n in ["SM_VK_Prop_LampPost_inst.034","SM_VK_Roof_Mid_inst.048","SM_VK_Prop_LampPost_inst.033","SM_VK_Porch_inst.036","SM_VK_Prop_LampPost_inst.032","SM_VK_Prop_LampPost_inst.035"]:
    d=D[n]; print(n, tuple(round(a,2) for a in d[2]), tuple(round(a,2) for a in d[3]), d[5])
col=bpy.data.collections["VK_ValleyTown"]; L=list(col.objects)
for k in range(1999,2030):
    o=L[k]; print(k,o.name,tuple(round(a,2) for a in o.location), round(o.rotation_euler.z*57.3))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_LampPost_inst.034 (1609.28, 104.17, 3.0) (1609.72, 105.22, 5.9) 0\nSM_VK_Roof_Mid_inst.048 (1600.55,
#  101.97, 5.42) (1609.45, 105.03, 10.42) 90\nSM_VK_Prop_LampPost_inst.033 (1642.28, 95.17, 3.0) (1642.72, 96.22, 5.9) 0\nSM_VK_Porch_inst.036 (1641.74,
#  92.95, 2.99) (1644.02, 96.05, 6.33) 270\nSM_VK_Prop_LampPost_inst.032 (1609.28, 95.17, 3.0) (1609.72, 96.22, 5.9) 0\nSM_VK_Prop_LampPost_inst.035 (16
# 42.28, 104.17, 3.0) (1642.72, 105.22, 5.9) 0\n1999 SM_VK_Wall_Stone_Door_inst.054 (1608.0, 100.5, 3.0) 90\n2000 SM_VK_Deco_Weeds_inst.194 (1608.0, 100
# .5, 3.0) 90\n2001 SM_VK_Prop_Planter_inst.032 (1608.75, 101.55, 3.0) 90\n2002 SM_VK_Porch_inst.035 (1608.0, 100.5, 3.0) 90\n2003 SM_VK_Wall_Stone_Wind
# ow_inst.189 (1608.0, 103.5, 3.0) 90\n2004 SM_VK_Prop_FlowerBox_Daisy_inst.054 (1608.55, 103.5, 3.78) 90\n2005 SM_VK_Deco_Weeds_inst.195 (1608.0, 103.5

# ==============================================================================================================
# [0036] 2026-09-23 17:19:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_19_lamp_porch",(1636,101,5),(1643.5,95,3.5),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_20_brewery",(1664,105,7),(1672,113,3),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_19_lamp_porch.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\bu
# ild\\review_build_20_brewery.png\n"}

# ==============================================================================================================
# [0037] 2026-09-23 17:20:06  blender  ok
# ==============================================================================================================
import bpy
bid=bpy.app.driver_namespace["_rv_bid"]
D={d[0]:d for d in bpy.app.driver_namespace["_rv_build_D"]}
names=["SM_VK_Prop_Anvil_inst.004","SM_VK_Porch_inst.030","SM_VK_Prop_Woodpile_inst.016","SM_VK_Porch_inst.032","SM_VK_Prop_BarrelStack_inst.023","SM_VK_Prop_CiderPress_inst","SM_VK_Porch_inst.031","SM_VK_Prop_WeaponRack_inst.009","SM_VK_Corner_Stone_inst.181","SM_VK_Prop_Forge_inst.003","SM_VK_LeanTo_inst.011","SM_VK_Prop_Crates_inst.013","SM_VK_LeanTo_inst.009","SM_VK_Prop_Sacks_inst.005","SM_VK_Wall_Stone_Door_inst.033","SM_VK_Prop_Trough_inst.013","SM_VK_Wall_Plaster_inst.083","SM_VK_Prop_Cauldron_inst","SM_VK_Wall_Plaster_Door_inst.017","SM_VK_Prop_Crates_inst.012","SM_VK_Palisade_Tower_inst.001","SM_VK_Prop_ChickenCoop_Wattle_inst.002","SM_VK_RoofThatch_Hip_inst.006"]
for n in names:
    d=D[n]; print(n, bid.get(n,'-'), tuple(round(a,2) for a in bpy.data.objects[n].location), tuple(round(a,2) for a in d[2]), tuple(round(a,2) for a in d[3]), d[5])
# doors near
import re
doors=[d for d in D.values() if 'Door' in d[1]]
for n in ["SM_VK_Prop_Anvil_inst.004","SM_VK_Prop_Woodpile_inst.016","SM_VK_Prop_BarrelStack_inst.023","SM_VK_Prop_Sacks_inst.005","SM_VK_Prop_Cauldron_inst","SM_VK_Prop_WeaponRack_inst.007"]:
    p=bpy.data.objects[n].location
    near=[(dd[0],round((dd[4].xy-p.xy).length,2)) for dd in doors if (dd[4].xy-p.xy).length<2.2 and abs(dd[4].z-p.z)<1]
    print(n,near)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Anvil_inst.004 skyline (1603.2, 118.2, 3.0) (1602.63, 117.84, 3.0) (1603.54, 118.56, 4.06) 180\nSM_V
# K_Porch_inst.030 skyline (1603.5, 117.0, 3.0) (1601.95, 116.98, 2.99) (1605.05, 119.26, 6.33) 180\nSM_VK_Prop_Woodpile_inst.016 blacksmith (1669.5, 12
# 7.1, 3.0) (1668.0, 126.45, 2.95) (1671.7, 127.75, 4.47) 0\nSM_VK_Porch_inst.032 blacksmith (1669.5, 129.0, 3.0) (1667.95, 126.74, 2.99) (1671.05, 129.
# 02, 6.33) 0\nSM_VK_Prop_BarrelStack_inst.023 brewery (1673.0, 111.9, 3.0) (1671.93, 111.06, 3.0) (1674.09, 112.68, 4.5) 15\nSM_VK_Prop_CiderPress_inst
#  brewery (1670.2, 112.0, 3.0) (1669.3, 110.88, 3.0) (1671.54, 112.48, 5.27) 0\nSM_VK_Porch_inst.031 brewery (1672.5, 113.5, 3.0) (1670.95, 111.24, 2.9
# 9) (1674.05, 113.52, 6.33) 0\nSM_VK_Prop_WeaponRack_inst.009 blacksmith (1674.6, 129.5, 3.0) (1673.84, 129.18, 3.0) (1675.36, 129.82, 5.07) 0\nSM_VK_C

# ==============================================================================================================
# [0038] 2026-09-23 17:20:58  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
# colony camera: 40 m away, 50 deg pitch -> height 30.6, horizontal 25.7
print(shot("review_build_21_skyline_colony",(1596,96,31),(1596,122,0),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_22_chapel_colony",(1652,94,31),(1652,120,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_21_skyline_colony.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review
# \\build\\review_build_22_chapel_colony.png\n"}

# ==============================================================================================================
# [0039] 2026-09-23 17:21:44  blender  ok
# ==============================================================================================================
import bpy
col=bpy.data.collections["VK_ValleyTown"]; L=list(col.objects)
for k in range(1769,1790):
    o=L[k]; print(k,o.name,tuple(round(a,2) for a in o.location), round(o.rotation_euler.z*57.3))
# ---- result ----
# {"result":"Code executed successfully: 1769 SM_VK_Chapel_Wall_inst.019 (1645.5, 117.0, 3.0) 0\n1770 SM_VK_Chapel_Wall_inst.020 (1645.5, 123.0, 3.0) 18
# 0\n1771 SM_VK_Chapel_Wall_inst.021 (1648.5, 117.0, 3.0) 0\n1772 SM_VK_Chapel_Wall_Door_inst.003 (1648.5, 123.0, 3.0) 180\n1773 SM_VK_Chapel_Wall_inst.
# 022 (1651.5, 117.0, 3.0) 0\n1774 SM_VK_Chapel_Wall_inst.023 (1651.5, 123.0, 3.0) 180\n1775 SM_VK_Chapel_Wall_inst.024 (1654.5, 117.0, 3.0) 0\n1776 SM_
# VK_Chapel_Wall_inst.025 (1654.5, 123.0, 3.0) 180\n1777 SM_VK_Chapel_Wall_Plain_inst.012 (1644.0, 118.5, 3.0) -90\n1778 SM_VK_Chapel_Wall_Plain_inst.01
# 3 (1656.0, 121.5, 3.0) 90\n1779 SM_VK_Chapel_Wall_Plain_inst.014 (1644.0, 121.5, 3.0) -90\n1780 SM_VK_Chapel_Wall_Plain_inst.015 (1656.0, 118.5, 3.0) 
# 90\n1781 SM_VK_Chapel_Corner_inst.012 (1644.0, 117.0, 3.0) 0\n1782 SM_VK_Chapel_Corner_inst.013 (1656.0, 117.0, 3.0) 90\n1783 SM_VK_Chapel_Corner_inst

# ==============================================================================================================
# [0040] 2026-09-23 17:22:12  blender  ok
# ==============================================================================================================
import bpy, math, re
from mathutils import Vector
D=bpy.app.driver_namespace["_rv_build_D"]; bid=bpy.app.driver_namespace["_rv_bid"]
doors=[d for d in D if re.search(r'Door',d[1]) and not 'Trap' in d[1]]
STR=re.compile(r'^SM_VK_(Wall_|Corner_|Chapel_|TownWall|Gatehouse_Block|LowWall|Palisade|Prop_|MarketStall|Tree_|Bush_|Pile_|Crop_|Stockpile|Tent|Animal)')
obs=[d for d in D if STR.match(d[1]) and not any(a in d[1] for a in ('FlowerBox','Lantern','Sign','Banner','Planter','Laundry','Bunting'))]
from collections import defaultdict
grid=defaultdict(list)
for d in obs:
    for gx in range(int(d[2].x//4),int(d[3].x//4)+1):
        for gy in range(int(d[2].y//4),int(d[3].y//4)+1): grid[(gx,gy)].append(d)
out=[]
for d in doors:
    o=bpy.data.objects[d[0]]; rz=o.matrix_world.to_euler().z
    n=Vector((math.sin(rz), -math.cos(rz)))   # rotate (0,-1)
    p=o.location
    hits=[]
    for dist in (0.9,1.6,2.4):
        q=p.xy+n*dist
        for od in grid[(int(q.x//4),int(q.y//4))]:
            if od[0]==d[0]: continue
            if od[2].x<q.x<od[3].x and od[2].y<q.y<od[3].y and od[2].z<p.z+1.5 and od[3].z>p.z+0.2:
                if 'Porch' in od[1]: continue
                hits.append((dist,od[0]))
    if hits:
        # dedupe
        seen=[];
        for hh in hits:
            if hh[1] not in [s[1] for s in seen]: seen.append(hh)
        out.append((d[0],bid.get(d[0],'-'),tuple(round(a,1) for a in p),(round(n.x,2),round(n.y,2)),seen[:4]))
for r in out: print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Wall_Stone_Door_inst.034', 'watermill', (1584.0, 55.5, 0.0), (1.0, 0.0), [(0.9, 'SM_VK_Prop_BarrelStack
# _inst.007')])\n('SM_VK_Wall_Stone_Door_inst.035', 'smokehouse', (1657.5, 51.0, 0.0), (-0.0, 1.0), [(2.4, 'SM_VK_Prop_FishRack_inst')])\n('SM_VK_Wall_S
# tone_Door_inst.036', 'training', (1686.0, 4.5, 1.5), (1.0, 0.0), [(0.9, 'SM_VK_Prop_WeaponRack_inst.007')])\n('SM_VK_Wall_Plaster_Door_inst.017', 'tan
# nery', (1509.0, 61.0, 1.5), (0.0, -1.0), [(1.6, 'SM_VK_Prop_TanningPit_inst.001')])\n('SM_VK_Wall_Stone_Door_inst.038', 'merchant', (1579.5, 78.0, 3.0
# ), (0.0, -1.0), [(2.4, 'SM_VK_TownWall_Straight_inst.006')])\n('SM_VK_Wall_Plaster_Door_inst.019', 'gablefront', (1597.5, 78.0, 3.0), (0.0, -1.0), [(0
# .9, 'SM_VK_Tree_Oak_B_inst.023'), (2.4, 'SM_VK_TownWall_Straight_inst.018')])\n('SM_VK_Wall_Stone_Door_inst.039', 'corner_house', (1612.5, 78.0, 3.0),

# ==============================================================================================================
# [0041] 2026-09-23 17:22:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_23_southwall_gap",(1590,68,16),(1597,79,4),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_24_westquarter_colony",(1596,58,31),(1596,84,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_23_southwall_gap.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\
# \build\\review_build_24_westquarter_colony.png\n"}

# ==============================================================================================================
# [0042] 2026-09-23 17:23:50  blender  ok
# ==============================================================================================================
import bpy, re
D=bpy.app.driver_namespace["_rv_build_D"]; bid=bpy.app.driver_namespace["_rv_bid"]
R=re.compile(r'^SM_VK_(Wall_|Corner_|Roof|Chapel_|TownWall|Foundation|Scaffold_Wall|Scaffold_Corner|Palisade_Straight|LowWall)')
from collections import defaultdict
off=defaultdict(list)
for d in D:
    if not R.match(d[1]): continue
    p=bpy.data.objects[d[0]].location
    x=(p.x-1500)/1.5; y=p.y/1.5
    ex=abs(x-round(x)); ey=abs(y-round(y))
    if ex>0.03 or ey>0.03 or d[5]%90!=0:
        off[bid.get(d[0],'-')].append((d[0],tuple(round(a,2) for a in p),d[5]))
for b,v in off.items():
    print(b,len(v),v[:6])
# ---- result ----
# {"result":"Code executed successfully: tannery 18 [('SM_VK_Wall_Plaster_inst.083', (1506.0, 61.0, 1.5), 0), ('SM_VK_Wall_Plaster_Door_inst.017', (1509
# .0, 61.0, 1.5), 0), ('SM_VK_Wall_Plaster_Window_inst.054', (1512.0, 61.0, 1.5), 0), ('SM_VK_Wall_Plaster_inst.084', (1506.0, 67.0, 1.5), 180), ('SM_VK
# _Wall_Plaster_inst.085', (1509.0, 67.0, 1.5), 180), ('SM_VK_Wall_Plaster_inst.086', (1512.0, 67.0, 1.5), 180)]\nbrewery 31 [('SM_VK_Wall_Stone_Window_
# inst.175', (1669.5, 113.5, 3.0), 0), ('SM_VK_Wall_Stone_Door_inst.049', (1672.5, 113.5, 3.0), 0), ('SM_VK_Wall_Stone_Window_inst.176', (1675.5, 113.5,
#  3.0), 0), ('SM_VK_Wall_Stone_inst.190', (1669.5, 119.5, 3.0), 180), ('SM_VK_Wall_Stone_inst.191', (1672.5, 119.5, 3.0), 180), ('SM_VK_Wall_Stone_Wind
# ow_inst.177', (1675.5, 119.5, 3.0), 180)]\n"}

# ==============================================================================================================
# [0043] 2026-09-23 17:24:12  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_25_gate_wallwalk",(1612,77.5,12.5),(1623,76,10),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_26_tannery_brewery_grid",(1512,48,24),(1510,64,1.5),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_25_gate_wallwalk.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\
# \build\\review_build_26_tannery_brewery_grid.png\n"}

# ==============================================================================================================
# [0044] 2026-09-23 17:24:52  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_27_sites_colony",(1652,38,31),(1652,64,0),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_28_plaza_colony",(1626,74,31),(1626,100,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_27_sites_colony.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# build\\review_build_28_plaza_colony.png\n"}

# ==============================================================================================================
# [0045] 2026-09-23 17:25:39  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_29_terrace_tower_walk",(1641,75.5,12.5),(1650,77.5,11),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_30_terrace_tower_east",(1680,74,17),(1671,78,11),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_29_terrace_tower_walk.png\nC:\\Users\\danie\\AppData\\Ro
# aming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\re
# view\\build\\review_build_30_terrace_tower_east.png\n"}

# ==============================================================================================================
# [0046] 2026-09-23 17:26:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_31_skyline_anvil_door",(1606,124,4.2),(1603.5,117.5,4),lens=30,res=(1600,900),outdir=OD))
print(shot("review_build_32_watermill",(1592,58,6),(1583,53,2),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_31_skyline_anvil_door.png\nC:\\Users\\danie\\AppData\\Ro
# aming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\re
# view\\build\\review_build_32_watermill.png\n"}

# ==============================================================================================================
# [0047] 2026-09-23 17:27:15  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
col=bpy.data.collections["VK_ValleyTown"]; L=list(col.objects)
for k in range(419,470):
    o=L[k]
    if any(s in o.name for s in ("Fence","Wall_","Corner_","LeanTo","LowWall","Gate")): print(k,o.name,tuple(round(a,2) for a in o.location), round(o.rotation_euler.z*57.3))
print(shot("review_build_33_sheepfold",(1561,12,9),(1552,21,2),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: 419 SM_VK_Wall_Wattle_inst.024 (1536.0, 22.5, 1.5) 0\n420 SM_VK_LeanTo_Thatch_Low_inst.001 (1536.0, 22.5, 1.5) 
# 0\n421 SM_VK_Wall_Wattle_inst.025 (1539.0, 22.5, 1.5) 0\n422 SM_VK_LeanTo_Thatch_Low_inst.002 (1539.0, 22.5, 1.5) 0\n423 SM_VK_LowWall_inst.025 (1534.
# 5, 21.0, 1.5) 90\n424 SM_VK_LowWall_inst.026 (1534.5, 18.0, 1.5) 90\n425 SM_VK_LowWall_inst.027 (1540.5, 21.0, 1.5) 90\n426 SM_VK_LowWall_inst.028 (15
# 40.5, 18.0, 1.5) 90\n427 SM_VK_LowWall_inst.029 (1536.0, 16.5, 1.5) 0\n428 SM_VK_Prop_FenceGate_inst.021 (1539.0, 16.5, 1.5) 0\n429 SM_VK_LowWall_Post
# _inst.010 (1534.5, 22.5, 1.5) 0\n430 SM_VK_LowWall_Post_inst.011 (1540.5, 22.5, 1.5) 0\n431 SM_VK_LowWall_Post_inst.012 (1534.5, 16.5, 1.5) 0\n432 SM_
# VK_LowWall_Post_inst.013 (1540.5, 16.5, 1.5) 0\n433 SM_VK_LowWall_Post_inst.014 (1537.5, 16.5, 1.5) 0\n434 SM_VK_LowWall_Post_inst.015 (1534.5, 19.5, 

# ==============================================================================================================
# [0048] 2026-09-23 17:28:11  blender  ok
# ==============================================================================================================
import bpy, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=bpy.app.driver_namespace["_rv_build_D"]; bid=bpy.app.driver_namespace["_rv_bid"]
from collections import defaultdict
byb=defaultdict(list)
for d in D:
    if d[0] in bid: byb[bid[d[0]]].append(d)
ROOF=re.compile(r'^SM_VK_(Roof|RoofS|RoofThatch|Ceiling|Turret|BellTower|Chimney|Gatehouse|Dormer|Emblem|Windmill|Tent|Scaffold)')
WALL=re.compile(r'^SM_VK_(Wall_|Corner_|Chapel_Wall|Chapel_Corner)')
res={}
for b,ds in byb.items():
    walls=[d for d in ds if WALL.match(d[1])]
    roofs=[d for d in ds if ROOF.match(d[1])]
    if not walls: continue
    vs=[];fs=[]
    for d in roofs:
        o=bpy.data.objects[d[0]]; M=o.matrix_world; off=len(vs)
        vs+= [M@v.co for v in o.data.vertices]; fs+=[tuple(off+i for i in p.vertices) for p in o.data.polygons]
    if not fs: res[b]="NO ROOF PIECES"; continue
    t=BVHTree.FromPolygons(vs,fs)
    # footprint: union of wall piece origins -> use bbox of wall origins
    xs=[bpy.data.objects[d[0]].location.x for d in walls]; ys=[bpy.data.objects[d[0]].location.y for d in walls]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    misses=[]
    # only sample points that are enclosed: within 1.6m of some wall line both in x and y ranges; simple grid
    x=x0+0.7
    while x<x1-0.6:
        y=y0+0.7
        while y<y1-0.6:
            # point is inside a building if there are wall origins on both sides in x within same row... approximate: require wall with |y-wy|<1.6 on left & right
            left=any(abs(bpy.data.objects[d[0]].location.y-y)<1.6 and bpy.data.objects[d[0]].location.x<x for d in walls)
            right=any(abs(bpy.data.objects[d[0]].location.y-y)<1.6 and bpy.data.objects[d[0]].location.x>x for d in walls)
            down=any(abs(bpy.data.objects[d[0]].location.x-x)<1.6 and bpy.data.objects[d[0]].location.y<y for d in walls)
            up=any(abs(bpy.data.objects[d[0]].location.x-x)<1.6 and bpy.data.objects[d[0]].location.y>y for d in walls)
            if left and right and up and down:
                r=t.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),100)
                if r[0] is None: misses.append((round(x,1),round(y,1)))
            y+=1.0
        x+=1.0
    if misses: res[b]=(len(misses),misses[:10])
for k,v in res.items(): print(k,v)
# ---- result ----
# {"result":"Code executed successfully: south_hamlet (28, [(1534.7, 3.7), (1534.7, 4.7), (1534.7, 5.7), (1534.7, 6.7), (1534.7, 7.7), (1534.7, 8.7), (1
# 534.7, 9.7), (1536.7, 21.7), (1537.7, 21.7), (1538.7, 21.7)])\nsites (78, [(1647.7, 63.7), (1647.7, 64.7), (1647.7, 65.7), (1647.7, 66.7), (1647.7, 67
# .7), (1648.7, 63.7), (1648.7, 64.7), (1648.7, 65.7), (1648.7, 66.7), (1648.7, 67.7)])\nlogcabin_woodcutter (2, [(1513.7, 78.7), (1513.7, 79.7)])\ntowe
# r_house (9, [(1575.7, 96.7), (1575.7, 97.7), (1575.7, 98.7), (1575.7, 99.7), (1575.7, 100.7), (1576.7, 96.7), (1577.7, 96.7), (1578.7, 96.7), (1579.7,
#  96.7)])\nskyline (20, [(1582.7, 124.7), (1582.7, 125.7), (1582.7, 126.7), (1582.7, 127.7), (1582.7, 128.7), (1582.7, 129.7), (1582.7, 130.7), (1583.7
# , 124.7), (1597.7, 111.7), (1597.7, 112.7)])\n"}

# ==============================================================================================================
# [0049] 2026-09-23 17:30:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_34_skyline_north_row",(1584,104,28),(1586,128,5),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_34_skyline_north_row.png\n"}

# ==============================================================================================================
# [0050] 2026-09-23 17:31:34  blender  ok
# ==============================================================================================================
import bpy, math, re
from mathutils import Vector
D=bpy.app.driver_namespace["_rv_build_D"]; bid=bpy.app.driver_namespace["_rv_bid"]
from collections import defaultdict
out=defaultdict(list)
for d in D:
    if d[0] not in bid: continue
    if re.search(r'(Door|Shop|Loading|Gate)',d[1]) and re.match(r'^SM_VK_(Wall_|Chapel_Wall)',d[1]):
        o=bpy.data.objects[d[0]]; rz=o.matrix_world.to_euler().z
        n=(round(math.sin(rz),1), round(-math.cos(rz),1))
        out[bid[d[0]]].append((d[1].replace('SM_VK_',''),tuple(round(a,1) for a in o.location[:2]),round(o.location.z,1),n))
for b in ["merchant","gablefront","corner_house","tower_house","terrace","brewery","chapel","blacksmith"]+[f"infill{i}" for i in range(9)]:
    print(b,out.get(b))
# ---- result ----
# {"result":"Code executed successfully: merchant [('Wall_Stone_Shop', (1576.5, 78.0), 3.0, (0.0, -1.0)), ('Wall_Stone_Door', (1579.5, 78.0), 3.0, (0.0,
#  -1.0)), ('Wall_Stone_Shop', (1582.5, 78.0), 3.0, (0.0, -1.0)), ('Wall_StoneUp_Loading', (1579.5, 78.0), 6.0, (0.0, -1.0)), ('Wall_StoneUp_Door', (157
# 9.5, 84.0), 6.0, (-0.0, 1.0)), ('Wall_StoneUp_Loading', (1579.5, 78.0), 8.8, (0.0, -1.0))]\ngablefront [('Wall_Plaster_Door', (1599.0, 82.5), 3.0, (1.
# 0, 0.0)), ('Wall_Plaster_Shop', (1594.5, 78.0), 3.0, (0.0, -1.0)), ('Wall_Plaster_Door', (1597.5, 78.0), 3.0, (0.0, -1.0))]\ncorner_house [('Wall_Ston
# e_Shop', (1609.5, 78.0), 3.0, (0.0, -1.0)), ('Wall_Stone_Door', (1612.5, 78.0), 3.0, (0.0, -1.0)), ('Wall_Stone_Shop', (1608.0, 79.5), 3.0, (-1.0, 0.0
# )), ('Wall_Timber_Door', (1615.5, 84.0), 6.0, (-0.0, 1.0)), ('Wall_Stone_Door', (1612.5, 87.0), 3.0, (-0.0, 1.0))]\ntower_house [('Wall_Stone_Door', (

# ==============================================================================================================
# [0051] 2026-09-23 17:32:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_35_smokehouse_river",(1662,39,4),(1657.5,48.5,1),lens=28,res=(1600,900),outdir=OD))
h=bpy.app.driver_namespace["_rv_h"]
for x in (1655.5,1656,1657.5,1659,1659.5):
    print(x,[ (y,round(h(x,y),2)) for y in (47.3,47.6,47.9,48.2,48.5)])
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_35_smokehouse_river.png\n1655.5 [(47.3, -1.02), (47.6, -
# 0.7), (47.9, -0.31), (48.2, -0.03), (48.5, 0.0)]\n1656 [(47.3, -1.02), (47.6, -0.7), (47.9, -0.31), (48.2, -0.03), (48.5, 0.0)]\n1657.5 [(47.3, -1.03)
# , (47.6, -0.7), (47.9, -0.31), (48.2, -0.03), (48.5, 0.0)]\n1659 [(47.3, -1.02), (47.6, -0.7), (47.9, -0.31), (48.2, -0.03), (48.5, 0.0)]\n1659.5 [(47
# .3, -1.02), (47.6, -0.7), (47.9, -0.31), (48.2, -0.03), (48.5, 0.0)]\n"}

# ==============================================================================================================
# [0052] 2026-09-23 17:32:58  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
tc=bpy.data.collections["VK_ValleyTerrain"]
mny=1e9
for o in tc.all_objects:
    if o.type=='MESH' and 'Chunk' in o.name:
        for c in o.bound_box:
            w=o.matrix_world@Vector(c); mny=min(mny,w.y)
print("terrain min y",mny)
D={d[0]:d for d in bpy.app.driver_namespace["_rv_build_D"]}
for n in ["SM_VK_Prop_Fence_inst.174","SM_VK_Prop_Fence_inst.175","SM_VK_Prop_Fence_inst.176","SM_VK_Wall_Stone_inst.150","SM_VK_Corner_Stone_inst.137","SM_VK_Wall_Timber_X_inst.036","SM_VK_Gallery_Side_inst"]:
    d=D[n]; print(n, round(d[2].y,2), round(d[3].y,2))
# any objects with bbox min y < -0.2 or beyond map
bad=[(d[0],round(d[2].y,2)) for d in D.values() if d[2].y<-0.3 and 'LipGrass' not in d[1]]
print(len(bad), bad[:30])
h=bpy.app.driver_namespace["_rv_h"]
print(h(1690,-0.2), h(1690,0.1), h(1684.5,-0.4))
# ---- result ----
# {"result":"Code executed successfully: terrain min y -1.7329074144363403\nSM_VK_Prop_Fence_inst.174 -0.49 -0.21\nSM_VK_Prop_Fence_inst.175 -0.49 -0.21
# \nSM_VK_Prop_Fence_inst.176 -0.49 -0.21\nSM_VK_Wall_Stone_inst.150 -0.53 0.28\nSM_VK_Corner_Stone_inst.137 -0.62 0.65\nSM_VK_Wall_Timber_X_inst.036 -0
# .62 0.18\nSM_VK_Gallery_Side_inst -0.06 0.06\n18 [('SM_VK_Deco_Bush_inst.006', -0.35), ('SM_VK_Wall_Stone_inst.150', -0.53), ('SM_VK_Wall_Stone_inst.1
# 51', -0.53), ('SM_VK_Deco_Weeds_inst.110', -0.87), ('SM_VK_Corner_Stone_inst.137', -0.62), ('SM_VK_Corner_Stone_inst.140', -0.6), ('SM_VK_Wall_Timber_
# X_inst.036', -0.62), ('SM_VK_Wall_Timber_Window_inst.255', -0.62), ('SM_VK_Corner_Timber_inst.150', -0.61), ('SM_VK_Corner_Timber_inst.153', -0.61), (
# 'SM_VK_Roof_Gable_inst.078', -1.2), ('SM_VK_Prop_Fence_inst.171', -0.32), ('SM_VK_Prop_Fence_inst.174', -0.49), ('SM_VK_Prop_Fence_inst.175', -0.49), 

# ==============================================================================================================
# [0053] 2026-09-23 17:34:03  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_36_lamp_in_porch",(1637.5,96.5,5.5),(1642.6,95.7,4.8),lens=35,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_36_lamp_in_porch.png\n"}

# ==============================================================================================================
# [0054] 2026-09-23 17:34:40  blender  ok
# ==============================================================================================================
import bpy, math
D=bpy.app.driver_namespace["_rv_build_D"]; bid=bpy.app.driver_namespace["_rv_bid"]
towers=[d for d in D if 'Tower_Round' in d[1]]
for t in towers:
    tp=t[4]
    near=[]
    for d in D:
        if d[0] in bid and ('Chimney' in d[1] or 'Roof' in d[1] or 'Turret' in d[1]):
            # horizontal distance from tower axis to bbox
            dx=max(d[2].x-tp.x,0,tp.x-d[3].x); dy=max(d[2].y-tp.y,0,tp.y-d[3].y)
            dist=math.hypot(dx,dy)
            if dist<3.3 and d[3].z>tp.z+3:
                near.append((d[0],bid[d[0]],round(dist,2),round(d[2].z,1),round(d[3].z,1)))
    if near: print(t[0],tuple(round(a,1) for a in tp),near)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Tower_Round_inst (1587.0, 75.0, 3.0) [('SM_VK_Roof_Pent_inst', 'merchant', 3.08, 5.3, 6.4), ('SM
# _VK_Roof_Gable_Stepped_inst.001', 'merchant', 3.07, 11.0, 17.7)]\nSM_VK_TownWall_Tower_Round_inst.002 (1608.0, 75.0, 3.0) [('SM_VK_Roof_LCorner_inst.0
# 08', 'corner_house', 1.48, 10.9, 16.8), ('SM_VK_Turret_Corbel_inst.001', 'corner_house', 1.2, 4.3, 6.1), ('SM_VK_Turret_Seg_inst', 'corner_house', 1.2
# , 6.0, 8.8), ('SM_VK_Turret_Seg_inst.001', 'corner_house', 1.2, 8.8, 11.6), ('SM_VK_Turret_Seg_inst.002', 'corner_house', 1.2, 11.6, 14.4), ('SM_VK_Tu
# rret_Cap_inst.001', 'corner_house', 0.76, 14.2, 18.2)]\nSM_VK_TownWall_Tower_Round_inst.004 (1650.0, 75.0, 3.0) [('SM_VK_Roof_Mid_inst.041', 'terrace'
# , 1.55, 13.8, 18.8), ('SM_VK_Roof_Gable_Stepped_inst.004', 'terrace', 1.55, 13.8, 20.5)]\nSM_VK_TownWall_Tower_Round_inst.006 (1671.0, 75.0, 3.0) [('S

# ==============================================================================================================
# [0055] 2026-09-23 17:35:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_37_meadow_workshops",(1545,36,34),(1545,64,0),lens=28,res=(1600,900),outdir=OD))
print(shot("review_build_38_palisade_outpost",(1660,-14,30),(1660,10,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_37_meadow_workshops.png\nC:\\Users\\danie\\AppData\\Roam
# ing\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revi
# ew\\build\\review_build_38_palisade_outpost.png\n"}

# ==============================================================================================================
# [0056] 2026-09-23 17:36:04  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\build"
print(shot("review_build_39_bridge_willow",(1614,26,6),(1624,33,2),lens=28,res=(1600,900),outdir=OD))
D={d[0]:d for d in bpy.app.driver_namespace["_rv_build_D"]}
for n in ["SM_VK_Tree_Willow_inst.005","SM_VK_Bridge_Stone_Ramp_inst.001","SM_VK_Tree_Willow_inst.002","SM_VK_Bridge_Wood_End_inst"]:
    d=D[n]; print(n, tuple(round(a,2) for a in d[2]), tuple(round(a,2) for a in d[3]))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\build\\review_build_39_bridge_willow.png\nSM_VK_Tree_Willow_inst.005 (1616.6
# 7, 25.11, -0.43) (1627.97, 36.52, 4.6)\nSM_VK_Bridge_Stone_Ramp_inst.001 (1623.15, 31.29, -0.6) (1628.88, 36.0, 2.13)\nSM_VK_Tree_Willow_inst.002 (152
# 5.84, 26.56, -0.43) (1537.36, 37.98, 4.6)\nSM_VK_Bridge_Wood_End_inst (1535.46, 32.78, -0.79) (1539.54, 36.02, 1.49)\n"}

# ==============================================================================================================
# [0057] 2026-09-23 17:37:18  blender  ok
# ==============================================================================================================
import bpy, math, re
D=bpy.app.driver_namespace["_rv_build_D"]
for d in D:
    if re.search(r'Door',d[1]) and d[4].y<30 and d[4].x<1600:
        o=bpy.data.objects[d[0]]; rz=o.matrix_world.to_euler().z
        print(d[0], tuple(round(a,1) for a in d[4]), (round(math.sin(rz),1), round(-math.cos(rz),1)))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Wattle_Door_inst (1509.0, 7.5, 1.5) (-1.0, 0.0)\nSM_VK_Wall_Wattle_Door_inst.001 (1542.0, 4.5, 1.5) 
# (1.0, 0.0)\nSM_VK_Wall_Wattle_Door_inst.002 (1557.0, 4.5, 1.5) (1.0, 0.0)\nSM_VK_Wall_Wattle_Door_inst.003 (1572.0, 16.5, 1.5) (1.0, 0.0)\n"}

# ==============================================================================================================
# [0058] 2026-09-23 17:37:48  blender  ok
# ==============================================================================================================
import bpy
for k in ("_rv_build_D","_rv_seg","_rv_bid","_rv_h"):
    bpy.app.driver_namespace.pop(k,None)
print("cleaned")
# ---- result ----
# {"result":"Code executed successfully: cleaned\n"}
