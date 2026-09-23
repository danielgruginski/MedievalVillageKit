# valley-rereview / agent-a32999cbfb63f790b.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 18:47:48  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["VillageKit"]
print(bpy.context.scene.name, [t.name for t in bpy.data.texts])
c=bpy.data.collections.get("VK_ValleyTown"); t=bpy.data.collections.get("VK_ValleyTerrain")
print(len(c.all_objects), len(t.all_objects))
print([o.name for o in t.all_objects][:40])
import builtins
print([k for k in bpy.app.driver_namespace.keys()][:40])
# ---- result ----
# {"result":"Code executed successfully: VillageKit ['mc_helpers', 'README_VillageKit', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_kit', 'vk_leafg
# en', 'vk_mat', 'vk_mod_construction', 'vk_mod_defence', 'vk_mod_frontier', 'vk_mod_humble', 'vk_mod_industry', 'vk_mod_skyline', 'vk_mod_town', 'vk_mo
# d_water', 'vk_nature', 'vk_render', 'vk_terrain', 'vk_terrain_demo', 'vk_tex', 'vk_tex2', 'vk_texgen', 'vk_town_map', 'wk_helpers', 'ws_common']\n4584
#  30\n['VKV_Chunk_0_0', 'VKV_Water_0_0', 'VKV_Chunk_1_0', 'VKV_Water_1_0', 'VKV_Chunk_2_0', 'VKV_Water_2_0', 'VKV_Chunk_3_0', 'VKV_Water_3_0', 'VKV_Chu
# nk_4_0', 'VKV_Water_4_0', 'VKV_Chunk_0_1', 'VKV_Water_0_1', 'VKV_Chunk_1_1', 'VKV_Water_1_1', 'VKV_Chunk_2_1', 'VKV_Water_2_1', 'VKV_Chunk_3_1', 'VKV_
# Water_3_1', 'VKV_Chunk_4_1', 'VKV_Water_4_1', 'VKV_Chunk_0_2', 'VKV_Chunk_1_2', 'VKV_Chunk_2_2', 'VKV_Chunk_3_2', 'VKV_Chunk_4_2', 'VKV_Chunk_0_3', 'V

# ==============================================================================================================
# [0002] 2026-09-23 18:48:14  blender  ok
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
# [0003] 2026-09-23 18:48:47  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
t0=time.time()
dg=bpy.context.evaluated_depsgraph_get()
def bvh_of(objs):
    V=[];F=[];off=0
    for o in objs:
        oe=o.evaluated_get(dg); me=oe.to_mesh()
        mw=o.matrix_world
        vs=[mw@v.co for v in me.vertices]
        V.extend(vs)
        for p in me.polygons: F.append([off+k for k in p.vertices])
        off+=len(vs); oe.to_mesh_clear()
    return BVHTree.FromPolygons(V,F), len(V)
terr=[o for o in bpy.data.collections["VK_ValleyTerrain"].all_objects if "Chunk" in o.name]
wat=[o for o in bpy.data.collections["VK_ValleyTerrain"].all_objects if "Water" in o.name]
bt,nv=bvh_of(terr); bw,nw=bvh_of(wat)
bpy.app.driver_namespace["_rr_play"]={"bt":bt,"bw":bw}
print(nv,nw,time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 318164 1736 0.7797324657440186\n"}

# ==============================================================================================================
# [0004] 2026-09-23 18:49:14  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; bt=S["bt"]; bw=S["bw"]
t0=time.time()
res=0.5; NX=int(216/res); NY=int(168/res)
H=np.full((NY,NX),np.nan,np.float32); Wz=np.full((NY,NX),np.nan,np.float32)
d=Vector((0,0,-1))
for jy in range(NY):
    y=(jy+0.5)*res
    for ix in range(NX):
        x=1500+(ix+0.5)*res
        h=bt.ray_cast(Vector((x,y,50)),d)
        if h[0] is not None: H[jy,ix]=h[0].z
        w=bw.ray_cast(Vector((x,y,50)),d)
        if w[0] is not None: Wz[jy,ix]=w[0].z
S["H"]=H; S["Wz"]=Wz
print(time.time()-t0, np.nanmin(H), np.nanmax(H), np.isnan(H).sum(), (~np.isnan(Wz)).sum())
# ---- result ----
# {"result":"Code executed successfully: 0.2578563690185547 -1.5000114 7.5000076 0 15534\n"}

# ==============================================================================================================
# [0005] 2026-09-23 18:49:49  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; H=S["H"]; Wz=S["Wz"]
print(H.shape)
# sample along main road x=1626 (ix=252) every 3 m
ix=int((1626-1500)/0.5)
print([ (round((jy+0.5)*0.5,1), round(float(H[jy,ix]),2), None if np.isnan(Wz[jy,ix]) else round(float(Wz[jy,ix]),2)) for jy in range(0,160,6)])
# ---- result ----
# {"result":"Code executed successfully: (336, 432)\n[(0.2, 1.5, None), (3.2, 1.5, None), (6.2, 1.5, None), (9.2, 1.5, None), (12.2, 1.5, None), (15.2, 
# 1.5, None), (18.2, 1.5, None), (21.2, 1.5, None), (24.2, 1.5, None), (27.2, 1.5, None), (30.2, 0.62, None), (33.2, 0.0, None), (36.2, -0.45, -0.6), (3
# 9.2, -1.5, -0.6), (42.2, -1.5, -0.6), (45.2, -1.5, -0.6), (48.2, -0.05, -0.6), (51.2, 0.0, None), (54.2, 0.88, None), (57.2, 1.5, None), (60.2, 1.5, N
# one), (63.2, 1.5, None), (66.2, 1.5, None), (69.2, 2.38, None), (72.2, 3.0, None), (75.2, 3.0, None), (78.2, 3.0, None)]\n"}

# ==============================================================================================================
# [0006] 2026-09-23 18:49:59  blender  ok
# ==============================================================================================================
import bpy, collections
c=bpy.data.collections["VK_ValleyTown"]
cnt=collections.Counter(o.name.split("_inst")[0] for o in c.all_objects)
print(len(cnt))
print(sorted(cnt.items()))
# ---- result ----
# {"result":"Code executed successfully: 338\n[('SM_VKT_LipGrass', 896), ('SM_VK_Animal_Chickens', 4), ('SM_VK_Animal_Cow', 1), ('SM_VK_Animal_Goat', 1)
# , ('SM_VK_Animal_Horse', 1), ('SM_VK_Animal_Pig', 3), ('SM_VK_Animal_Sheep', 7), ('SM_VK_Banner_Pole', 4), ('SM_VK_Banner_Roof', 2), ('SM_VK_Banner_Wa
# ll', 9), ('SM_VK_BellTower', 1), ('SM_VK_Bridge_Stone_Pier', 1), ('SM_VK_Bridge_Stone_Ramp', 2), ('SM_VK_Bridge_Stone_Span', 2), ('SM_VK_Bridge_Wood_B
# ent', 5), ('SM_VK_Bridge_Wood_End', 2), ('SM_VK_Bridge_Wood_Mid', 4), ('SM_VK_BuildSite_Cell', 18), ('SM_VK_Bush_Hydrangea', 3), ('SM_VK_Bush_Large', 
# 2), ('SM_VK_Bush_Round', 112), ('SM_VK_Ceiling_Cell', 4), ('SM_VK_Chapel_Corner', 4), ('SM_VK_Chapel_Wall', 7), ('SM_VK_Chapel_Wall_Door', 1), ('SM_VK
# _Chapel_Wall_Plain', 4), ('SM_VK_Chimney', 20), ('SM_VK_Chimney_Gable_H30', 4), ('SM_VK_Chimney_Gable_H58', 2), ('SM_VK_Chimney_Party', 1), ('SM_VK_Co

# ==============================================================================================================
# [0007] 2026-09-23 18:50:50  blender  ok
# ==============================================================================================================
import bpy, math
c=bpy.data.collections["VK_ValleyTown"]
out=[]
for o in c.all_objects:
    n=o.name
    if o.type!="MESH": continue
    if ("_Door" in n and not n.startswith("SM_VK_Prop")) or any(k in n for k in ("Passage","Mine_Portal","GateArch","Palisade_Gate","FenceGate","Postern","Gatehouse_Block","Quarry_Floor","Pier_","Quay_Stair","Stair_Stone_Ext","WheelPier")):
        r=o.rotation_euler.z
        out.append((n,round(o.location.x,2),round(o.location.y,2),round(o.location.z,2),round(math.degrees(r))%360))
for r in sorted(out): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Bridge_Stone_Pier_inst', 1626.0, 42.0, 0.0, 90)\n('SM_VK_Chapel_Wall_Door_inst.003', 1651.5, 117.0, 3.0
# , 0)\n('SM_VK_Gatehouse_Block_inst', 1626.0, 75.0, 3.0, 0)\n('SM_VK_LowWall_GateArch_inst', 1660.5, 93.0, 3.0, 0)\n('SM_VK_Mill_WheelPier_inst', 1579.
# 5, 44.9, 0.0, 270)\n('SM_VK_Mine_Portal_inst', 1512.0, 97.5, 3.0, 0)\n('SM_VK_Palisade_GateLeaf_inst', 1659.05, 6.35, 1.5, 72)\n('SM_VK_Palisade_GateL
# eaf_inst.001', 1661.95, 6.35, 1.5, 108)\n('SM_VK_Palisade_Gate_inst', 1660.5, 6.0, 1.5, 0)\n('SM_VK_Passage_Vault_inst', 1654.5, 84.0, 3.0, 180)\n('SM
# _VK_Pier_Deck_inst', 1693.5, 25.5, 0.0, 90)\n('SM_VK_Pier_Deck_inst.001', 1693.5, 28.5, 0.0, 90)\n('SM_VK_Pier_End_inst', 1693.5, 31.5, 0.0, 90)\n('SM
# _VK_Pier_Rail_inst', 1693.5, 25.5, 0.0, 90)\n('SM_VK_Pier_Rail_inst.001', 1693.5, 28.5, 0.0, 90)\n('SM_VK_Pier_Stairs_inst', 1693.5, 28.5, 0.0, 270)\n

# ==============================================================================================================
# [0008] 2026-09-23 18:51:56  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils.bvhtree import BVHTree
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]
c=bpy.data.collections["VK_ValleyTown"]
FLOOR=("Bridge_Stone_Span","Bridge_Stone_Ramp","Bridge_Wood_End","Bridge_Wood_Mid","Pier_Deck","Pier_End","Pier_Stairs","Quay_Straight","Quay_Stair","Stair_Stone_Ext","Quarry_Floor","Prop_GranaryStep")
SKIP=("Tree_","Plant_","LipGrass","Deco_Weeds","Deco_Ivy","Crop_","Mushrooms","Rock_Pebbles","Rock_Small","Bush_Round","Deco_Bush","Wildflowers","BuildSite_Cell","Deco_MudWallow","Banner_","Lantern","FlowerBox","Sign","Emblem","Bunting","Festoon","Chimney","Animal_","Stump","Bush_Hydrangea")
dg=bpy.context.evaluated_depsgraph_get()
cache={}
def geo(o):
    oe=o.evaluated_get(dg)
    key=(o.data.name, tuple(m.type for m in o.modifiers))
    if key not in cache:
        me=oe.to_mesh(); co=np.empty(len(me.vertices)*3); me.vertices.foreach_get("co",co)
        polys=[tuple(p.vertices) for p in me.polygons]; oe.to_mesh_clear()
        cache[key]=(co.reshape(-1,3),polys)
    return cache[key]
def build(objs):
    V=[];F=[];off=0
    for o in objs:
        co,polys=geo(o); M=np.array(o.matrix_world)
        w=co@M[:3,:3].T+M[:3,3]; V.append(w)
        F.extend([[off+k for k in p] for p in polys]); off+=len(w)
    V=np.vstack(V) if V else np.zeros((0,3))
    return BVHTree.FromPolygons([tuple(v) for v in V],F), off
fl=[];ob=[];names=[]
for o in c.all_objects:
    if o.type!="MESH": continue
    n=o.name
    if any(k in n for k in FLOOR): fl.append(o)
    elif any(k in n for k in SKIP): continue
    else: ob.append(o); 
bf,nf=build(fl); bo,no=build(ob)
S["bf"]=bf; S["bo"]=bo
print(len(fl),nf,len(ob),no,time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 27 25494 1886 1426084 3.8429932594299316\n"}

# ==============================================================================================================
# [0009] 2026-09-23 18:52:32  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]; H=S["H"]; Wz=S["Wz"]; bf=S["bf"]; bo=S["bo"]
res=0.5; NY,NX=H.shape
F=H.copy(); d=Vector((0,0,-1))
for jy in range(NY):
    y=(jy+0.5)*res
    for ix in range(NX):
        x=1500+(ix+0.5)*res
        h=bf.ray_cast(Vector((x,y,20)),d)
        if h[0] is not None and h[0].z>H[jy,ix]-0.05: F[jy,ix]=h[0].z
S["F"]=F
print("floor",time.time()-t0, int((F!=H).sum()))
# ---- result ----
# {"result":"Code executed successfully: floor 0.07517218589782715 780\n"}

# ==============================================================================================================
# [0010] 2026-09-23 18:52:59  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; H=S["H"]; F=S["F"]; Wz=S["Wz"]
def col(x,y0,y1,step=1.0):
    ix=int((x-1500)/0.5); out=[]
    y=y0
    while y<=y1:
        jy=int(y/0.5); w=Wz[jy,ix]
        out.append((y,round(float(H[jy,ix]),2),round(float(F[jy,ix]),2),None if np.isnan(w) else round(float(w),2))); y+=step
    return out
print("footbridge x1530:",col(1530.2,24,62))
print("stone x1626:",col(1626.2,24,62))
# ---- result ----
# {"result":"Code executed successfully: footbridge x1530: [(24, 1.5, 1.5, None), (25.0, 1.5, 1.5, None), (26.0, 1.5, 1.5, None), (27.0, 1.5, 1.5, None)
# , (28.0, 1.5, 1.5, None), (29.0, 1.12, 1.12, None), (30.0, 0.62, 0.62, None), (31.0, 0.12, 0.12, None), (32.0, 0.0, 0.0, None), (33.0, 0.0, 0.0, None)
# , (34.0, 0.0, 0.0, None), (35.0, -0.0, -0.0, -0.6), (36.0, -0.71, -0.71, -0.6), (37.0, -1.5, -1.5, -0.6), (38.0, -1.5, -1.5, -0.6), (39.0, -1.5, -1.5,
#  -0.6), (40.0, -1.5, -1.5, -0.6), (41.0, -1.5, -1.5, -0.6), (42.0, -1.5, -1.5, -0.6), (43.0, -1.5, -1.5, -0.6), (44.0, -1.5, -1.5, -0.6), (45.0, -1.5,
#  -1.5, -0.6), (46.0, -1.5, -1.5, -0.6), (47.0, -1.17, -1.17, -0.6), (48.0, -0.02, -0.02, -0.6), (49.0, -0.0, -0.0, -0.6), (50.0, -0.0, 0.1, None), (51
# .0, 0.0, 0.0, None), (52.0, 0.0, 0.0, None), (53.0, 0.38, 0.38, None), (54.0, 0.88, 0.88, None), (55.0, 1.38, 1.38, None), (56.0, 1.5, 1.5, None), (57

# ==============================================================================================================
# [0011] 2026-09-23 18:53:26  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in sorted(c.all_objects,key=lambda o:o.name):
    if "Bridge_Wood" in o.name or "Bridge_Stone" in o.name:
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        print(o.name, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z)), "x",round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),"y",round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),"z",round(min(w.z for w in ws),2),round(max(w.z for w in ws),2), o.data.name, len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Bridge_Stone_Pier_inst (1626.0, 42.0, 0.0) 90 x 1622.64 1629.36 y 41.05 42.95 z -2.0 1.0 SM_VK_Bridge_Sto
# ne_Pier 236\nSM_VK_Bridge_Stone_Ramp_inst (1626.0, 49.5, 0.0) 90 x 1623.12 1628.85 y 48.0 52.71 z -0.6 2.13 SM_VK_Bridge_Stone_Ramp 1264\nSM_VK_Bridge
# _Stone_Ramp_inst.001 (1626.0, 34.5, 0.0) -90 x 1623.15 1628.88 y 31.29 36.0 z -0.6 2.13 SM_VK_Bridge_Stone_Ramp 1264\nSM_VK_Bridge_Stone_Span_inst (16
# 26.0, 39.0, 0.0) 90 x 1623.87 1628.13 y 36.0 42.0 z -1.6 2.26 SM_VK_Bridge_Stone_Span 3900\nSM_VK_Bridge_Stone_Span_inst.001 (1626.0, 45.0, 0.0) 90 x 
# 1623.87 1628.13 y 42.0 48.0 z -1.6 2.26 SM_VK_Bridge_Stone_Span 3900\nSM_VK_Bridge_Wood_Bent_inst (1530.0, 36.0, 0.0) 90 x 1528.2 1531.8 y 35.77 36.23
#  z -3.0 -0.02 SM_VK_Bridge_Wood_Bent 320\nSM_VK_Bridge_Wood_Bent_inst.001 (1530.0, 39.0, 0.0) 90 x 1528.2 1531.8 y 38.77 39.23 z -3.0 -0.02 SM_VK_Brid

# ==============================================================================================================
# [0012] 2026-09-23 18:53:41  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; bf=S["bf"]
for x in (1529.0,1530.25,1531.0):
    print(x,[ (y, bf.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))[0]) for y in (34,40,44,49)])
o=bpy.data.objects["SM_VK_Bridge_Wood_Mid_inst"]
print(o.modifiers[:], o.data.name, len(o.data.vertices))
me=o.data
zs=sorted(set(round((o.matrix_world@v.co).z,2) for v in me.vertices))
print(zs[:10], zs[-10:])
# ---- result ----
# {"result":"Code executed successfully: 1529.0 [(34, Vector((1529.0, 34.0, -0.10080528259277344))), (40, None), (44, Vector((1529.0, 44.0, 0.3332176208
# 496094))), (49, Vector((1529.0, 49.0, 0.3260059356689453)))]\n1530.25 [(34, Vector((1530.25, 34.0, -0.0347137451171875))), (40, None), (44, None), (49
# , None)]\n1531.0 [(34, Vector((1531.0, 34.0, 0.14035606384277344))), (40, Vector((1531.0, 40.0, 0.33533668518066406))), (44, None), (49, None)]\n[] SM
# _VK_Bridge_Wood_Mid 712\n[-0.25, -0.22, -0.15, -0.13, -0.02, 0.08, 0.09, 0.11, 0.12, 0.13] [0.76, 0.77, 0.85, 1.23, 1.36, 1.37, 1.38, 1.39, 1.42, 1.44
# ]\n"}

# ==============================================================================================================
# [0013] 2026-09-23 18:54:00  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]; H=S["H"]; bf=S["bf"]
res=0.5; NY,NX=H.shape
F=H.copy(); d=Vector((0,0,-1))
# only the sample columns near floor-set objects matter: bounding boxes
boxes=[]
for o in bpy.data.collections["VK_ValleyTown"].all_objects:
    if o.type=="MESH" and any(k in o.name for k in ("Bridge_Stone_Span","Bridge_Stone_Ramp","Bridge_Wood_End","Bridge_Wood_Mid","Pier_Deck","Pier_End","Pier_Stairs","Quay_Straight","Quay_Stair","Stair_Stone_Ext","Quarry_Floor","Prop_GranaryStep")):
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        boxes.append((min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws)))
n=0
for (x0,x1,y0,y1) in boxes:
    for ix in range(max(0,int((x0-1500)/res)-1),min(NX,int((x1-1500)/res)+2)):
        for jy in range(max(0,int(y0/res)-1),min(NY,int(y1/res)+2)):
            x=1500+(ix+0.5)*res; y=(jy+0.5)*res; best=None
            for (dx,dy) in ((0,0),(0.2,0),(-0.2,0),(0,0.2),(0,-0.2),(0.12,0.12),(-0.12,-0.12)):
                h=bf.ray_cast(Vector((x+dx,y+dy,20)),d)
                if h[0] is not None and h[0].z>H[jy,ix]-0.05 and (best is None or h[0].z>best): best=h[0].z
            if best is not None: F[jy,ix]=best; n+=1
S["F"]=F
print(time.time()-t0,n)
ix=int((1530.2-1500)/0.5)
print([(y, round(float(F[int(y/0.5),ix]),2)) for y in range(28,58)])
# ---- result ----
# {"result":"Code executed successfully: 0.056604623794555664 1505\n[(28, 1.5), (29, 1.12), (30, 0.62), (31, 0.12), (32, 0.0), (33, 0.06), (34, 0.24), (
# 35, 0.35), (36, 0.35), (37, 0.35), (38, 0.35), (39, 0.35), (40, 0.35), (41, 0.35), (42, 0.35), (43, 0.35), (44, 0.35), (45, 0.35), (46, 0.35), (47, 0.
# 35), (48, 0.35), (49, 0.32), (50, 0.14), (51, 0.0), (52, 0.0), (53, 0.38), (54, 0.88), (55, 1.38), (56, 1.5), (57, 1.5)]\n"}

# ==============================================================================================================
# [0014] 2026-09-23 18:54:42  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; bo=S["bo"]
res=0.5; NY,NX=F.shape
B=np.zeros((NY,NX),bool)
for jy in range(NY):
    y=(jy+0.5)*res
    for ix in range(NX):
        x=1500+(ix+0.5)*res; f=float(F[jy,ix])
        if bo.find_nearest(Vector((x,y,f+0.45)),0.28)[0] is not None or bo.find_nearest(Vector((x,y,f+1.3)),0.28)[0] is not None:
            B[jy,ix]=True
S["B"]=B
print(time.time()-t0,int(B.sum()))
# ---- result ----
# {"result":"Code executed successfully: 0.26645779609680176 16937\n"}

# ==============================================================================================================
# [0015] 2026-09-23 18:55:01  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]
def prof(x,y0,y1):
    ix=int((x-1500)/0.5); return [(round((jy+0.5)*0.5,2), round(float(F[jy,ix]),2)) for jy in range(int(y0/0.5),int(y1/0.5))]
print(prof(1600.2,51,57))
print(prof(1645.2,66,78))
# histogram of max neighbour diff
D=np.maximum(np.abs(np.diff(F,axis=0))[:, :].max(), 0)
dy=np.abs(np.diff(F,axis=0)); dx=np.abs(np.diff(F,axis=1))
h,e=np.histogram(np.concatenate([dy.ravel(),dx.ravel()]),bins=[0,0.05,0.1,0.2,0.3,0.35,0.4,0.5,0.6,0.8,1.0,1.5,3,10])
print(list(zip(e[:-1].round(2),h)))
# ---- result ----
# {"result":"Code executed successfully: [(51.25, 0.0), (51.75, 0.0), (52.25, -0.0), (52.75, -0.0), (53.25, 0.0), (53.75, 0.0), (54.25, 1.45), (54.75, 1
# .5), (55.25, 1.5), (55.75, 1.5), (56.25, 1.5), (56.75, 1.5)]\n[(66.25, 1.5), (66.75, 1.5), (67.25, 1.5), (67.75, 1.5), (68.25, 1.5), (68.75, 1.5), (69
# .25, 1.5), (69.75, 1.5), (70.25, 1.5), (70.75, 1.5), (71.25, 1.5), (71.75, 2.32), (72.25, 2.98), (72.75, 3.0), (73.25, 3.0), (73.75, 3.0), (74.25, 3.0
# ), (74.75, 3.0), (75.25, 3.0), (75.75, 3.0), (76.25, 3.0), (76.75, 3.0), (77.25, 3.0), (77.75, 3.0)]\n[(0.0, 277511), (0.05, 971), (0.1, 653), (0.2, 8
# 90), (0.3, 262), (0.35, 270), (0.4, 919), (0.5, 1414), (0.6, 2538), (0.8, 2513), (1.0, 1099), (1.5, 435), (3.0, 61)]\n"}

# ==============================================================================================================
# [0016] 2026-09-23 18:55:50  blender  ok
# ==============================================================================================================
import bpy, numpy as np, math
from collections import deque
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; B=S["B"]; Wz=S["Wz"]
NY,NX=F.shape; res=0.5
wet=(~np.isnan(Wz))&(Wz>F+0.15)
walk=(~B)&(~wet)
thr=0.42
def bfs(seed):
    R=np.zeros((NY,NX),bool); q=deque([seed]); R[seed]=True
    while q:
        j,i=q.popleft()
        for dj,di in ((1,0),(-1,0),(0,1),(0,-1)):
            a,b=j+dj,i+di
            if 0<=a<NY and 0<=b<NX and not R[a,b] and walk[a,b] and abs(F[a,b]-F[j,i])<=thr:
                R[a,b]=True; q.append((a,b))
    return R
seed=(int(3.2/res),int((1626.2-1500)/res))
print(walk[seed])
R=bfs(seed); S["R"]=R; S["walk"]=walk
print("reached",int(R.sum()),"walkable",int(walk.sum()))
# ---- result ----
# {"result":"Code executed successfully: True\nreached 76176 walkable 117236\n"}

# ==============================================================================================================
# [0017] 2026-09-23 18:56:05  blender  ok
# ==============================================================================================================
import bpy, numpy as np, math
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]; B=S["B"]
NY,NX=F.shape; res=0.5
c=bpy.data.collections["VK_ValleyTown"]
def idx(x,y): return int(y/res), int((x-1500)/res)
res_=[]
for o in c.all_objects:
    n=o.name
    if o.type!="MESH": continue
    if not (("_Door" in n and not n.startswith("SM_VK_Prop")) or any(k in n for k in ("Wall_Stone_Passage","Mine_Portal","GateArch","Palisade_Gate_","Postern"))): continue
    r=o.rotation_euler.z; nx,ny=math.sin(r),-math.cos(r)
    ok=False; info=[]
    for dist in (0.8,1.2,1.6,2.0,2.5):
        x=o.location.x+nx*dist; y=o.location.y+ny*dist
        j,i=idx(x,y)
        if not (0<=j<NY and 0<=i<NX): info.append("out"); continue
        near=[(a,b) for a in range(j-1,j+2) for b in range(i-1,i+2) if 0<=a<NY and 0<=b<NX]
        hit=any(R[a,b] and abs(F[a,b]-o.location.z)<0.6 for (a,b) in near)
        info.append(("R" if hit else ("w" if walk[j,i] else "B"))+f"{F[j,i]:.1f}")
        ok|=hit
    res_.append((ok,n,round(o.location.x,1),round(o.location.y,1),round(o.location.z,1),round(math.degrees(r))%360,info))
for r in sorted(res_,key=lambda r:(r[0],r[1])): print(r)
# ---- result ----
# {"result":"Code executed successfully: (False, 'SM_VK_Wall_StoneUp_Door_inst', 1579.5, 84.0, 6.0, 0, ['w7.1', 'w7.1', 'w3.0', 'w3.0', 'w3.0'])\n(False
# , 'SM_VK_Wall_StoneUp_Door_inst.001', 1579.5, 96.0, 6.0, 0, ['w7.1', 'w7.1', 'B3.0', 'B3.0', 'B3.0'])\n(False, 'SM_VK_Wall_Stone_Door_inst.036', 1686.
# 0, 6.0, 1.5, 90, ['B1.5', 'B1.5', 'w1.5', 'w1.5', 'w1.5'])\n(False, 'SM_VK_Wall_Timber_Door_inst', 1621.5, 76.5, 9.2, 270, ['w3.0', 'w3.0', 'w3.0', 'w
# 3.0', 'w3.0'])\n(False, 'SM_VK_Wall_Timber_Door_inst.001', 1630.5, 76.5, 9.2, 90, ['w3.0', 'w3.0', 'w3.0', 'w3.0', 'w3.0'])\n(False, 'SM_VK_Wall_Timbe
# r_Door_inst.002', 1603.5, 84.0, 6.0, 0, ['w3.0', 'w3.0', 'B3.0', 'B3.0', 'B3.0'])\n(True, 'SM_VK_Chapel_Wall_Door_inst.003', 1651.5, 117.0, 3.0, 0, ['
# R3.0', 'R3.0', 'R3.0', 'R3.0', 'R3.0'])\n(True, 'SM_VK_LowWall_GateArch_inst', 1660.5, 93.0, 3.0, 0, ['R3.0', 'R3.0', 'R3.0', 'R3.0', 'R3.0'])\n(True,

# ==============================================================================================================
# [0018] 2026-09-23 18:57:08  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]; B=S["B"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        s+= "R" if R[j,i] else ("." if walk[j,i] else "#")
    return s
print("gate rows x1618-1634:")
for y in np.arange(69,82,0.5): print(f"{y:5.1f}",row_str(y,1618,1634))
# ---- result ----
# {"result":"Code executed successfully: gate rows x1618-1634:\n 69.0 RRRR.......RRRRRRRRRR.......R###\n 69.5 RRRR....#####RRRRRRR####....R###\n 70.0 RR
# RR..########RRRR#######...RRRR\n 70.5 RRRR..##....##RRRR##....##..RRRR\n 71.0 RRRR.##......##RR##......##.RRRR\n 71.5 RRRR.##########RR##########.RRRR
# \n 72.0 .....###....###RRR##....##......\n 72.5 ......##....##RRRR##....##......\n 73.0 ...#####....##RRRR##.#####.###..\n 73.5 ##############RRRR####
# ##########\n 74.0 ...##.##.##.##RRRR##.##.##.##...\n 74.5 ...##.##.##.##RRRR##.##.##.##...\n 75.0 ...##.##.##.##RRRR##.##.##.##...\n 75.5 ###########.
# #RRRRRR#.###########\n 76.0 ##########..#RRRRRR#..##########\n 76.5 RRRRRR##....#RRRRRR#....##RRRRRR\n 77.0 RRRRRR##....#RRRRRR#....##RRRRRR\n 77.5 RR
# RRRR########RRRR########RRRRRR\n 78.0 RRRRRRR######RRRRRR######RRRRRRR\n 78.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 79.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR

# ==============================================================================================================
# [0019] 2026-09-23 18:57:48  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def near(x0,x1,y0,y1,z0,z1):
    out=[]
    for o in c.all_objects:
        if o.type!="MESH": continue
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
        if bx[0]<x1 and bx[1]>x0 and bx[2]<y1 and bx[3]>y0 and bx[4]<z1 and bx[5]>z0:
            out.append((o.name,tuple(round(v,2) for v in bx)))
    return out
for r in near(1623.5,1628.5,69.5,77.5,3.2,5.0): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Gatehouse_Block_inst', (1620.69, 1631.33, 69.68, 78.25, 1.5, 12.0))\n('SM_VK_Gatehouse_GateLeaf_inst', 
# (1624.18, 1624.93, 73.69, 75.38, 3.02, 7.36))\n('SM_VK_Gatehouse_GateLeaf_inst.001', (1627.07, 1627.82, 73.69, 75.38, 3.02, 7.36))\n"}

# ==============================================================================================================
# [0020] 2026-09-23 18:58:11  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V=[];Fc=[];off=0
    for n in names:
        o=bpy.data.objects[n]; oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
        vs=[mw@v.co for v in me.vertices]; V+=vs; Fc+=[[off+k for k in p.vertices] for p in me.polygons]; off+=len(vs); oe.to_mesh_clear()
    return BVHTree.FromPolygons(V,Fc)
g=bvh(["SM_VK_Gatehouse_Block_inst"]); gl=bvh(["SM_VK_Gatehouse_GateLeaf_inst","SM_VK_Gatehouse_GateLeaf_inst.001","SM_VK_Gatehouse_Portcullis_inst"])
S=bpy.app.driver_namespace["_rr_play"]; S["g"]=g
for z in (3.5,4.5):
    for y in (69.8,70.5,71.0,72.0,73.0,74.5,76.0,77.5,78.1):
        o=Vector((1626,y,z))
        l=g.ray_cast(o,Vector((-1,0,0)),10); r=g.ray_cast(o,Vector((1,0,0)),10)
        l2=gl.ray_cast(o,Vector((-1,0,0)),10); r2=gl.ray_cast(o,Vector((1,0,0)),10)
        lx=max([h[0].x for h in (l,l2) if h[0]] or [None]) if (l[0] or l2[0]) else None
        rx=min([h[0].x for h in (r,r2) if h[0]] or [None]) if (r[0] or r2[0]) else None
        print(z,y,lx and round(lx,2),rx and round(rx,2), (round(rx-lx,2) if lx and rx else None))
# floor under passage
for y in (69.9,71,72.5,74,75.5,77,78.1):
    h=g.ray_cast(Vector((1626,y,4.0)),Vector((0,0,-1)),3)
    t=S["bt"].ray_cast(Vector((1626,y,4.0)),Vector((0,0,-1)),3)
    print("floor",y, h[0] and round(h[0].z,3), t[0] and round(t[0].z,3))
p=bpy.data.objects["SM_VK_Gatehouse_Portcullis_inst"]
print("portcullis z", [round((p.matrix_world@Vector(b)).z,2) for b in p.bound_box][:2], max(round((p.matrix_world@Vector(b)).z,2) for b in p.bound_box))
# ---- result ----
# {"result":"Code executed successfully: 3.5 69.8 None None None\n3.5 70.5 1624.25 1627.75 3.5\n3.5 71.0 1624.67 1627.33 2.66\n3.5 72.0 1624.98 1627.02 
# 2.04\n3.5 73.0 1624.67 1627.33 2.66\n3.5 74.5 1624.63 1627.37 2.74\n3.5 76.0 1624.4 1627.6 3.2\n3.5 77.5 1624.4 1627.6 3.2\n3.5 78.1 None None None\n4
# .5 69.8 None None None\n4.5 70.5 1624.01 1627.99 3.99\n4.5 71.0 1624.5 1627.5 2.99\n4.5 72.0 1624.84 1627.16 2.32\n4.5 73.0 1624.5 1627.5 2.99\n4.5 74
# .5 1624.63 1627.37 2.74\n4.5 76.0 1624.4 1627.6 3.2\n4.5 77.5 1624.48 1627.52 3.04\n4.5 78.1 None None None\nfloor 69.9 None 2.7\nfloor 71 None 3.0\nf
# loor 72.5 3.04 3.0\nfloor 74 3.04 3.0\nfloor 75.5 3.04 3.0\nfloor 77 3.04 3.0\nfloor 78.1 3.04 3.0\nportcullis z [5.16, 9.9] 9.9\n"}

# ==============================================================================================================
# [0021] 2026-09-23 18:59:04  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]
for x in (1623.2,1624.2,1626.2,1627.7,1628.7):
    ix=int((x-1500)/0.5)
    print(x,[(round((j+0.5)*0.5,2),round(float(F[j,ix]),2)) for j in range(int(64/0.5),int(72/0.5))])
# ---- result ----
# {"result":"Code executed successfully: 1623.2 [(64.25, 1.5), (64.75, 1.5), (65.25, 1.5), (65.75, 1.5), (66.25, 1.5), (66.75, 1.5), (67.25, 1.5), (67.7
# 5, 1.5), (68.25, 1.5), (68.75, 2.32), (69.25, 2.98), (69.75, 3.0), (70.25, 3.0), (70.75, 3.0), (71.25, 3.0), (71.75, 3.0)]\n1624.2 [(64.25, 1.5), (64.
# 75, 1.5), (65.25, 1.5), (65.75, 1.5), (66.25, 1.5), (66.75, 1.5), (67.25, 1.5), (67.75, 1.62), (68.25, 1.88), (68.75, 2.12), (69.25, 2.38), (69.75, 2.
# 62), (70.25, 2.88), (70.75, 3.0), (71.25, 3.0), (71.75, 3.0)]\n1626.2 [(64.25, 1.5), (64.75, 1.5), (65.25, 1.5), (65.75, 1.5), (66.25, 1.5), (66.75, 1
# .5), (67.25, 1.5), (67.75, 1.62), (68.25, 1.88), (68.75, 2.12), (69.25, 2.38), (69.75, 2.62), (70.25, 2.88), (70.75, 3.0), (71.25, 3.0), (71.75, 3.0)]
# \n1627.7 [(64.25, 1.5), (64.75, 1.5), (65.25, 1.5), (65.75, 1.5), (66.25, 1.5), (66.75, 1.5), (67.25, 1.5), (67.75, 1.62), (68.25, 1.88), (68.75, 2.12

# ==============================================================================================================
# [0022] 2026-09-23 18:59:26  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def bb(o):
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    return (round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2),round(max(w.z for w in ws),2))
for o in sorted(c.all_objects,key=lambda o:o.name):
    n=o.name
    if any(k in n for k in ("Shop","Tower_Round","Postern","ShopGoods","Turret","Stair_Stone_Ext")):
        print(n, tuple(round(v,1) for v in o.location), round(math.degrees(o.rotation_euler.z))%360, bb(o))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_ShopGoods_Bread_inst (1576.5, 90.6, 4.0) 180 (1575.55, 1577.45, 90.3, 90.8, 3.95, 4.27)\nSM_VK_Prop_
# ShopGoods_Cloth_inst (1660.5, 87.6, 4.0) 180 (1659.57, 1661.31, 87.3, 87.89, 3.5, 4.35)\nSM_VK_Prop_ShopGoods_Fish_inst (1609.5, 90.6, 4.0) 180 (1608.
# 58, 1610.43, 90.33, 90.91, 3.95, 4.24)\nSM_VK_Prop_ShopGoods_Pots_inst (1549.6, 60.9, 1.5) 270 (1549.39, 1549.88, 59.97, 61.84, 1.5, 1.92)\nSM_VK_Prop
# _ShopGoods_Pots_inst.001 (1611.6, 88.5, 4.0) 90 (1611.27, 1611.76, 87.56, 89.43, 3.95, 4.37)\nSM_VK_Prop_ShopGoods_Produce_inst (1594.5, 90.6, 4.0) 18
# 0 (1593.6, 1595.57, 90.21, 90.8, 3.95, 4.31)\nSM_VK_Prop_ShopGoods_Tools_inst (1582.5, 90.6, 4.0) 180 (1581.55, 1583.4, 90.29, 90.78, 3.95, 4.4)\nSM_V
# K_Stair_Stone_Ext_inst (1576.5, 84.0, 3.0) 0 (1574.75, 1580.2, 82.43, 83.79, 2.4, 7.14)\nSM_VK_Stair_Stone_Ext_inst.001 (1576.5, 96.0, 3.0) 0 (1574.75

# ==============================================================================================================
# [0023] 2026-09-23 19:00:07  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]
res=0.5
def row_str(y,x0,x1,step=1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res),step):
        s+= "R" if R[j,i] else ("." if walk[j,i] else "#")
    return s
print("x from 1560 to 1625 step 0.5; rows y 76..106")
for y in np.arange(76,106,0.5): print(f"{y:5.1f}",row_str(y,1560,1625))
# ---- result ----
# {"result":"Code executed successfully: x from 1560 to 1625 step 0.5; rows y 76..106\n 76.0 RRRRRRRRRRRRRRR#..#########################################
# ###################################################################..#R\n 76.5 RRRRRRRRRRRRRRR#...##RRRRRRRRRRRRRRRRRRRRRRRRRR###........##RRRRRRRRRRR
# RRRRRRRRRRRRRRRRRR###........##RRRRRRRRRRRRRRRRRRRR##....#R\n 77.0 RRRRRRRRRRRRRR##...##RRRRRRRRRRRRRRRRRRRRRRRRRRR###......###RRRRRRRRRRRRRRRRRRRRRRR
# RR##RRR###......###RRRRRRRRRRRRRRRRRRRR##....#R\n 77.5 RRRRRRRRRRRRRR#######RRRRRRRRRRRRRRRRRRRRRRRRRRRR####..####RRRRRRRRRRRRRRRRRRRRRRRR####RRRR####
# ..####RRRRRRRRRRRRRRRRRRRRR########\n 78.0 RRRRRRRRRRRRRR#######RRRRRRRRRRRRRRRRRRRRRRRRRRRRRR######RRRRRRRRRRRRRRRRRRRRRRRRRR####RRRRRR######RRRRRRRR
# RRRRRRRRRRRRRRRR######R\n 78.5 RRRRRRRRRRRRRRR#...##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR####RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR

# ==============================================================================================================
# [0024] 2026-09-23 19:00:30  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]; bf=S["bf"]; bo=S["bo"]
for y in (82.75,83.25):
    j=int(y/0.5)
    print(y,[(round(1500+(i+0.5)*0.5,2),round(float(F[j,i]),2),"R" if R[j,i] else ("." if walk[j,i] else "#")) for i in range(int((1573.5-1500)/0.5),int((1581.5-1500)/0.5))])
# direct raycast along stair centerline
for x in np.arange(1574.0,1581.0,0.5):
    h=bf.ray_cast(Vector((x,83.1,20)),Vector((0,0,-1)))
    print(round(x,2), h[0] and round(h[0].z,2))
# ---- result ----
# {"result":"Code executed successfully: 82.75 [(1573.75, 3.0, 'R'), (1574.25, 3.0, 'R'), (1574.75, 4.23, '.'), (1575.25, 4.26, '.'), (1575.75, 4.85, '.
# '), (1576.25, 5.46, '.'), (1576.75, 6.07, '.'), (1577.25, 6.69, '.'), (1577.75, 7.14, '.'), (1578.25, 7.14, '.'), (1578.75, 7.14, '.'), (1579.25, 7.14
# , '.'), (1579.75, 7.14, '.'), (1580.25, 7.14, '.'), (1580.75, 3.0, '.'), (1581.25, 3.0, '#')]\n83.25 [(1573.75, 3.0, 'R'), (1574.25, 3.0, 'R'), (1574.
# 75, 3.0, '#'), (1575.25, 3.5, '#'), (1575.75, 4.02, '.'), (1576.25, 4.78, '.'), (1576.75, 5.28, '.'), (1577.25, 6.05, '.'), (1577.75, 6.3, '.'), (1578
# .25, 6.3, '.'), (1578.75, 6.3, '.'), (1579.25, 6.3, '.'), (1579.75, 7.14, '.'), (1580.25, 7.14, '.'), (1580.75, 3.0, '.'), (1581.25, 3.0, '#')]\n1574.
# 0 None\n1574.5 None\n1575.0 3.0\n1575.5 3.5\n1576.0 4.27\n1576.5 4.78\n1577.0 5.28\n1577.5 6.05\n1578.0 6.3\n1578.5 6.3\n1579.0 6.3\n1579.5 6.3\n1580.

# ==============================================================================================================
# [0025] 2026-09-23 19:01:28  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def near(x0,x1,y0,y1,z0,z1):
    out=[]
    for o in c.all_objects:
        if o.type!="MESH": continue
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
        if bx[0]<x1 and bx[1]>x0 and bx[2]<y1 and bx[3]>y0 and bx[4]<z1 and bx[5]>z0:
            out.append((o.name,tuple(round(v,1) for v in o.location),round(math.degrees(o.rotation_euler.z))%360,tuple(round(v,2) for v in bx)))
    return out
for r in near(1601,1606,80.5,84.5,3.0,9.0): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Wall_Stone_inst.163', (1602.0, 85.5, 3.0), 270, (1601.47, 1602.28, 83.98, 87.02, 2.89, 6.0))\n('SM_VK_D
# eco_Weeds_inst.137', (1602.0, 85.5, 3.0), 270, (1601.13, 1601.87, 83.92, 87.1, 2.97, 3.54))\n('SM_VK_Wall_Timber_Window_inst.278', (1602.0, 85.5, 6.0)
# , 270, (1601.38, 1602.18, 83.98, 87.11, 5.8, 8.81))\n('SM_VK_Wall_Timber_inst.046', (1602.0, 85.5, 8.8), 270, (1601.38, 1602.18, 83.98, 87.11, 8.6, 11
# .61))\n('SM_VK_Wall_Stone_Window_inst.151', (1603.5, 84.0, 3.0), 0, (1601.98, 1605.02, 83.18, 84.28, 2.89, 6.0))\n('SM_VK_Prop_FlowerBox_inst.111', (1
# 603.5, 83.4, 3.8), 0, (1602.75, 1604.21, 83.17, 83.71, 3.56, 4.45))\n('SM_VK_Wall_Timber_Door_inst.002', (1603.5, 84.0, 6.0), 0, (1601.89, 1605.02, 83
# .38, 84.18, 5.8, 8.81))\n('SM_VK_Wall_Timber_Window_inst.279', (1603.5, 84.0, 8.8), 0, (1601.89, 1605.02, 83.38, 84.18, 8.6, 11.61))\n('SM_VK_Wall_Sto

# ==============================================================================================================
# [0026] 2026-09-23 19:02:01  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
S=bpy.app.driver_namespace["_rr_play"]; bo=S["bo"]; bt=S["bt"]
o=bpy.data.objects["SM_VK_TownWall_Postern_inst"]; oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
V=[mw@v.co for v in me.vertices]; Fc=[list(p.vertices) for p in me.polygons]; oe.to_mesh_clear()
b=BVHTree.FromPolygons(V,Fc)
for z in (3.3,4.0,4.8,5.3,5.8):
    for x in (1567.6,1568.5,1569.0,1569.6,1570.1):
        p=Vector((x,91.5,z)); l=b.ray_cast(p,Vector((0,-1,0)),5); r=b.ray_cast(p,Vector((0,1,0)),5); u=b.ray_cast(p,Vector((0,0,1)),10)
        print(z,x, l[0] and round(l[0].y,2), r[0] and round(r[0].y,2), (round(r[0].y-l[0].y,2) if l[0] and r[0] else None), "ceil", u[0] and round(u[0].z,2))
# also obstacle-sum (all obstacles) width
for z in (3.4,4.3):
    p=Vector((1569.0,91.5,z)); l=bo.ray_cast(p,Vector((0,-1,0)),5); r=bo.ray_cast(p,Vector((0,1,0)),5)
    print("all",z, l[0] and round(l[0].y,2), r[0] and round(r[0].y,2))
print("terrain at postern", [round(bt.ray_cast(Vector((x,91.5,10)),Vector((0,0,-1)))[0].z,2) for x in np.arange(1562,1576,1.0)])
# ---- result ----
# {"result":"Code executed successfully: 3.3 1567.6 90.41 92.71 2.3 ceil None\n3.3 1568.5 90.5 92.5 2.0 ceil 5.7\n3.3 1569.0 90.61 92.39 1.79 ceil 5.7\n
# 3.3 1569.6 90.61 92.39 1.79 ceil 5.7\n3.3 1570.1 None None None ceil 5.71\n4.0 1567.6 None None None ceil None\n4.0 1568.5 90.5 92.5 2.0 ceil 5.7\n4.0
#  1569.0 90.61 92.39 1.79 ceil 5.7\n4.0 1569.6 90.61 92.39 1.79 ceil 5.7\n4.0 1570.1 None None None ceil 5.71\n4.8 1567.6 None None None ceil None\n4.8
#  1568.5 90.5 92.5 2.0 ceil 5.7\n4.8 1569.0 90.61 92.39 1.79 ceil 5.7\n4.8 1569.6 90.61 92.39 1.79 ceil 5.7\n4.8 1570.1 None None None ceil 5.71\n5.3 1
# 567.6 None None None ceil None\n5.3 1568.5 90.5 92.5 2.0 ceil 5.7\n5.3 1569.0 90.61 92.39 1.79 ceil 5.7\n5.3 1569.6 90.61 92.39 1.79 ceil 5.7\n5.3 157
# 0.1 None None None ceil 5.71\n5.8 1567.6 None None None ceil None\n5.8 1568.5 90.5 92.5 2.0 ceil 9.05\n5.8 1569.0 90.5 92.5 2.0 ceil 9.05\n5.8 1569.6 

# ==============================================================================================================
# [0027] 2026-09-23 19:02:18  blender  ok
# ==============================================================================================================
import bpy, numpy as np, heapq, math, time
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; walk=S["walk"]
NY,NX=F.shape; res=0.5; thr=0.42
def dij(sx,sy):
    D=np.full((NY,NX),np.inf); P=-np.ones((NY,NX,2),np.int32)
    s=(int(sy/res),int((sx-1500)/res)); D[s]=0; h=[(0.0,s)]
    nb=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
    while h:
        d,(j,i)=heapq.heappop(h)
        if d>D[j,i]: continue
        for dj,di,w in nb:
            a,b=j+dj,i+di
            if 0<=a<NY and 0<=b<NX and walk[a,b] and abs(F[a,b]-F[j,i])<=thr*w:
                if w>1 and not (walk[j,b] and walk[a,i]): continue
                nd=d+w*res
                if nd<D[a,b]: D[a,b]=nd; P[a,b]=(j,i); heapq.heappush(h,(nd,(a,b)))
    return D,P
D,P=dij(1626,100.5); S["Dplaza"]=D; S["Pplaza"]=P
def at(x,y): return round(float(D[int(y/res),int((x-1500)/res)]),1)
pts={"forester_door":(1534.5,73.5),"logcabin":(1504.5,73.5),"woodcutter":(1516.5,76.5),"mine":(1512,95.5),"quarry_floor":(1545,96),"charcoal":(1552.5,74),"postern_out":(1566,91.5),"ridge_stair_top":(1528.5,103.5),"footbridge_mid":(1530,42),"mill_door033":(1576.5,52.5),"fisher_door":(1693.5,22.5),"tannery_door":(1509,58.5),"main_road_south":(1626,3),"chapel_door":(1651.5,115.5),"smokehouse":(1657.5,52.5)}
for k,(x,y) in pts.items(): print(k,at(x,y),"straight",round(math.hypot(x-1626,y-100.5),1))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: forester_door inf straight 95.4\nlogcabin inf straight 124.5\nwoodcutter inf straight 112.1\nmine inf straight 
# 114.1\nquarry_floor inf straight 81.1\ncharcoal inf straight 78.1\npostern_out inf straight 60.7\nridge_stair_top inf straight 97.5\nfootbridge_mid in
# f straight 112.4\nmill_door033 inf straight 69.0\nfisher_door inf straight 103.2\ntannery_door inf straight 124.3\nmain_road_south inf straight 97.5\n
# chapel_door inf straight 29.6\nsmokehouse inf straight 57.4\n0.0\n"}

# ==============================================================================================================
# [0028] 2026-09-23 19:03:27  blender  ok
# ==============================================================================================================
import bpy, numpy as np, heapq, math, time
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; walk=S["walk"]; R=S["R"]
NY,NX=F.shape; res=0.5; thr=0.42
def dij(sx,sy):
    D=np.full((NY,NX),np.inf); P=-np.ones((NY,NX,2),np.int32)
    s=(int(sy/res),int((sx-1500)/res)); D[s]=0; h=[(0.0,s)]
    nb=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
    while h:
        d,(j,i)=heapq.heappop(h)
        if d>D[j,i]: continue
        for dj,di,w in nb:
            a,b=j+dj,i+di
            if 0<=a<NY and 0<=b<NX and walk[a,b] and abs(F[a,b]-F[j,i])<=thr*w:
                if w>1 and not (walk[j,b] and walk[a,i]): continue
                nd=d+w*res
                if nd<D[a,b]: D[a,b]=nd; P[a,b]=(j,i); heapq.heappush(h,(nd,(a,b)))
    return D,P
sx,sy=1626,96.0
print("seed R",R[int(sy/res),int((sx-1500)/res)])
D,P=dij(sx,sy); S["Dplaza"]=D; S["Pplaza"]=P
def at(x,y):
    j,i=int(y/res),int((x-1500)/res); sub=D[j-1:j+2,i-1:i+2]; return round(float(sub.min()),1)
pts={"forester_door":(1534.5,73.5),"logcabin":(1504.5,73.5),"woodcutter":(1516.5,76.5),"mine":(1512,95.5),"quarry_floor":(1545,96),"charcoal":(1552.5,74),"postern_out":(1566,91.5),"ridge_stair_top":(1528.5,103.5),"footbridge_mid":(1530,42),"mill_door033":(1576.5,52.5),"fisher_door":(1693.5,22.5),"tannery_door":(1509,58.5),"main_road_south":(1626,3),"chapel_door":(1651.5,115.5),"smokehouse":(1657.5,52.5),"barracks_door":(1687.5,6)}
for k,(x,y) in pts.items(): print(k,at(x,y),"straight",round(math.hypot(x-sx,y-sy),1))
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: seed R True\nforester_door 101.9 straight 94.2\nlogcabin 130.9 straight 123.6\nwoodcutter 118.8 straight 111.2\
# nmine 119.3 straight 114.0\nquarry_floor inf straight 81.0\ncharcoal 86.0 straight 76.7\npostern_out 61.4 straight 60.2\nridge_stair_top 111.8 straigh
# t 97.8\nfootbridge_mid 136.1 straight 110.1\nmill_door033 87.0 straight 65.9\nfisher_door 134.1 straight 99.8\ntannery_door 138.4 straight 122.9\nmain
# _road_south 92.5 straight 93.0\nchapel_door 32.9 straight 32.1\nsmokehouse 166.5 straight 53.7\nbarracks_door inf straight 109.0\n1.701547622680664\n"
# }

# ==============================================================================================================
# [0029] 2026-09-23 19:03:49  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; D=S["Dplaza"]; P=S["Pplaza"]; F=S["F"]
res=0.5
def trace(x,y):
    j,i=int(y/res),int((x-1500)/res)
    sub=D[j-1:j+2,i-1:i+2]; a,b=np.unravel_index(np.argmin(sub),sub.shape); j,i=j-1+a,i-1+b
    pts=[]
    while P[j,i][0]>=0:
        pts.append((round(1500+(i+0.5)*res,1),round((j+0.5)*res,1),round(float(F[j,i]),1)))
        j,i=P[j,i]
    return pts[::-1]
p=trace(1657.5,52.5)
print(len(p)); print(p[::12])
# ---- result ----
# {"result":"Code executed successfully: 321\n[(1626.2, 95.8, 3.0), (1626.2, 89.8, 3.0), (1626.2, 83.8, 3.0), (1626.2, 77.8, 3.0), (1626.2, 71.8, 3.0), 
# (1628.2, 65.8, 1.5), (1634.2, 61.8, 1.5), (1640.2, 61.8, 1.5), (1646.2, 61.2, 1.5), (1652.2, 60.8, 1.5), (1658.2, 57.8, 1.5), (1664.2, 57.2, 1.5), (16
# 70.2, 57.2, 1.5), (1676.2, 57.2, 1.5), (1681.2, 56.8, 0.8), (1687.2, 56.8, 0.8), (1693.2, 56.8, 0.8), (1699.2, 56.8, 0.9), (1705.2, 56.8, 0.8), (1704.
# 2, 56.2, 0.0), (1698.2, 56.2, 0.0), (1692.2, 56.2, -0.0), (1686.2, 56.2, 0.0), (1680.2, 56.2, 0.0), (1674.2, 53.8, 0.0), (1668.2, 53.2, -0.0), (1662.2
# , 53.2, 0.0)]\n"}

# ==============================================================================================================
# [0030] 2026-09-23 19:04:36  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]; D=S["Dplaza"]; Wz=S["Wz"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        wet=(not np.isnan(Wz[j,i])) and Wz[j,i]>F[j,i]+0.15
        s+= "~" if wet else (("R" if D[j,i]<130 else "r") if R[j,i] else ("." if walk[j,i] else "#"))
    return s
print("x 1618..1668, 'R' = plaza dist<130, 'r' reached but >130")
for y in np.arange(46,57,0.5): print(f"{y:5.1f}",row_str(y,1618,1668))
# ---- result ----
# {"result":"Code executed successfully: x 1618..1668, 'R' = plaza dist<130, 'r' reached but >130\n 46.0 ~~~~~~~~~~~RRRRRRRRRR~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n 46.5 ~~~~~~~~~~~RRRRRRRRRR~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~\n 47.0 ~~~~~~~~~~~RRRRRRRRRR~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n 47.5 ...........RRRRRRRRRR..
# ................##....##...######RRRRRRRRRRRRRRRR###############rrrrrrrrrr~~~\n 48.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR###################RRRRRRRRR
# RRRRRRR###############rrrrrrrrrrrrr\n 48.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR##R##############RRRRRRRRRRRRRRRRRR#####....##.###rrrrrrrrrrrrr\n 49.0
#  RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR##R############RRRRRRRRRRRRRRRRRRRR#####....##.###rrrrrrrrrrrrr\n 49.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR##R#

# ==============================================================================================================
# [0031] 2026-09-23 19:05:03  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def near(x0,x1,y0,y1,z0,z1):
    out=[]
    for o in c.all_objects:
        if o.type!="MESH": continue
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
        if bx[0]<x1 and bx[1]>x0 and bx[2]<y1 and bx[3]>y0 and bx[4]<z1 and bx[5]>z0:
            out.append((o.name,tuple(round(v,2) for v in o.location),round(math.degrees(o.rotation_euler.z))%360,tuple(round(v,2) for v in bx)))
    return out
for r in near(1652.5,1657.5,50.8,53.8,0.2,1.9): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Wall_Stone_Door_inst.035', (1657.5, 51.0, 0.0), 180, (1655.98, 1659.02, 50.72, 51.84, -0.1, 3.13))\n('S
# M_VK_Wall_Stone_inst.145', (1656.0, 49.5, 0.0), 270, (1655.47, 1656.28, 47.98, 51.02, -0.11, 3.0))\n('SM_VK_Corner_Stone_inst.134', (1656.0, 51.0, 0.0
# ), 270, (1655.4, 1656.65, 50.35, 51.62, -0.06, 3.01))\n('SM_VK_Prop_FishRack_inst', (1655.09, 52.6, 0.0), 185, (1653.42, 1656.75, 51.66, 53.54, -0.22,
#  1.97))\n('SM_VK_Pile_Fish_1_inst', (1655.1, 52.1, 0.0), 210, (1654.55, 1655.66, 51.59, 52.66, -0.01, 0.36))\n('SM_VKT_LipGrass_inst.691', (1651.92, 5
# 4.04, 1.5), 354, (1651.23, 1652.56, 53.74, 54.16, 1.03, 1.67))\n"}

# ==============================================================================================================
# [0032] 2026-09-23 19:05:41  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]; D=S["Dplaza"]; Wz=S["Wz"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        s+= ("R" if R[j,i] else ("." if walk[j,i] else "#"))
    return s
def hrow(y,x0,x1):
    j=int(y/res); return "".join(str(min(9,int(round(F[j,i]/1.5*2)))) for i in range(int((x0-1500)/res),int((x1-1500)/res)))
print("x 1528..1562")
for y in np.arange(86,106,0.5): print(f"{y:5.1f}",row_str(y,1528,1562),"  ",hrow(y,1528,1562))
# ---- result ----
# {"result":"Code executed successfully: x 1528..1562\n 86.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR 4444444444444444444444
# 4444444444444444444444444444444444444444444444\n 86.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR 444444444444444444444444444
# 44444444444444444444444444444444444444444\n 87.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR 44444444444444444444444444444444
# 444444444444444444444444444444444444\n 87.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR 4444444444444444444444444444444444444
# 4444444444444444444444444444444\n 88.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR 444444444444444444444444444444444444444444
# 44444444444444444444444444\n 88.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR 44444444444444444444444444444444444444444444444

# ==============================================================================================================
# [0033] 2026-09-23 19:06:36  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def near(x0,x1,y0,y1,z0,z1,skip=("LipGrass","Weeds")):
    out=[]
    for o in c.all_objects:
        if o.type!="MESH" or any(s in o.name for s in skip): continue
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
        if bx[0]<x1 and bx[1]>x0 and bx[2]<y1 and bx[3]>y0 and bx[4]<z1 and bx[5]>z0:
            out.append((o.name,tuple(round(v,2) for v in o.location),round(math.degrees(o.rotation_euler.z))%360,tuple(round(v,2) for v in bx)))
    return out
for r in near(1536,1553,88,103,3.1,5.0): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Quarry_Face_Straight_inst', (1545.0, 100.5, 3.0), 0, (1543.5, 1546.5, 98.84, 102.0, 2.4, 6.55))\n('SM_V
# K_Quarry_Face_InnerCorner_inst', (1548.0, 100.5, 3.0), 0, (1546.43, 1549.5, 98.91, 102.03, 2.4, 6.46))\n('SM_VK_Quarry_Face_InnerCorner_inst.001', (15
# 42.0, 100.5, 3.0), 90, (1540.47, 1543.59, 98.93, 102.0, 2.4, 6.46))\n('SM_VK_Quarry_Face_Straight_inst.001', (1548.0, 97.5, 3.0), 270, (1546.34, 1549.
# 5, 96.0, 99.0, 2.4, 6.55))\n('SM_VK_Quarry_Face_Straight_inst.002', (1542.0, 97.5, 3.0), 90, (1540.5, 1543.66, 96.0, 99.0, 2.4, 6.55))\n('SM_VK_Quarry
# _Face_Corner_inst', (1548.0, 94.5, 3.0), 0, (1546.42, 1549.5, 92.88, 96.09, 2.4, 6.52))\n('SM_VK_Quarry_Face_Corner_inst.001', (1542.0, 94.5, 3.0), 90
# , (1540.41, 1543.62, 92.92, 96.0, 2.4, 6.52))\n('SM_VK_Quarry_Face_Straight_inst.003', (1551.0, 94.5, 3.0), 0, (1549.5, 1552.5, 92.84, 96.0, 2.4, 6.55

# ==============================================================================================================
# [0034] 2026-09-23 19:07:22  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R"]; walk=S["walk"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        s+= ("R" if R[j,i] else ("." if walk[j,i] else "#"))
    return s
print("x 1672..1712")
for y in np.arange(0,20,0.5): print(f"{y:5.1f}",row_str(y,1672,1712))
# ---- result ----
# {"result":"Code executed successfully: x 1672..1712\n 0.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 0.5 RRRRR
# RRRRRRRRRR##RRRRRRRRRR###################RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 1.0 RRRRRRRRRRRRRR#################################RRRRRRRRRRRRRRRRRRRRR
# RRRRRRRRRRRR\n 1.5 RRRRRRRRRRRRRR##################...####......##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 2.0 RRRRRRRRRRRRRR###..........##...#.######..#.
# .##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 2.5 RRRRRRRRRRRRRRR##..........##...########..##.##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 3.0 RRRRRRRRRRRRRRR##...
# .......##...##.......##..##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 3.5 RRRRRRRRRRRRRR###..........###..##.......##..##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 
# 4.0 RRRRRRRRRRRRRR###..........######........#...##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 4.5 RRRRRRRRRRRRRRR##..........######........##..##RRRRRRRRRRRR

# ==============================================================================================================
# [0035] 2026-09-23 19:07:53  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import deque
t0=time.time()
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; B=S["B"]; Wz=S["Wz"]
c=bpy.data.collections["VK_ValleyTown"]
dg=bpy.context.evaluated_depsgraph_get()
gates=[o for o in c.all_objects if o.type=="MESH" and "FenceGate" in o.name]
V=[];Fc=[];off=0
for o in gates:
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    vs=[mw@v.co for v in me.vertices]; V+=vs; Fc+=[[off+k for k in p.vertices] for p in me.polygons]; off+=len(vs); oe.to_mesh_clear()
bg=BVHTree.FromPolygons(V,Fc)
# recompute blocked only for samples near gates, excluding gate geometry: need obstacle bvh w/o gates -> rebuild partial: test samples blocked in B whose nearest obstacle is a gate
res=0.5; NY,NX=F.shape; bo=S["bo"]
B2=B.copy(); n=0
for o in gates:
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    x0=min(w.x for w in ws)-0.4; x1=max(w.x for w in ws)+0.4; y0=min(w.y for w in ws)-0.4; y1=max(w.y for w in ws)+0.4
    for ix in range(int((x0-1500)/res),int((x1-1500)/res)+1):
        for jy in range(int(y0/res),int(y1/res)+1):
            if not B[jy,ix]: continue
            x=1500+(ix+0.5)*res; y=(jy+0.5)*res; f=float(F[jy,ix]); blocked=False
            for z in (f+0.45,f+1.3):
                p=Vector((x,y,z)); h=bo.find_nearest(p,0.28)
                if h[0] is None: continue
                g=bg.find_nearest(p,0.28)
                if g[0] is None or g[3]>h[3]+1e-4: blocked=True
            if not blocked: B2[jy,ix]=False; n+=1
wet=(~np.isnan(Wz))&(Wz>F+0.15)
walk=(~B2)&(~wet); thr=0.42
R=np.zeros((NY,NX),bool); seed=(int(3.2/res),int((1626.2-1500)/res)); q=deque([seed]); R[seed]=True
while q:
    j,i=q.popleft()
    for dj,di in ((1,0),(-1,0),(0,1),(0,-1)):
        a,b=j+dj,i+di
        if 0<=a<NY and 0<=b<NX and not R[a,b] and walk[a,b] and abs(F[a,b]-F[j,i])<=thr: R[a,b]=True; q.append((a,b))
S["B2"]=B2; S["walk2"]=walk; S["R2"]=R
print(len(gates),n,int(R.sum()),time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 5 42 76939 0.2655150890350342\n"}

# ==============================================================================================================
# [0036] 2026-09-23 19:08:31  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from collections import deque
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R2"]; walk=S["walk2"]
res=0.5; NY,NX=F.shape; thr=0.42
j,i=int(6/res),int((1688-1500)/res); print("barracks front R2:",R[j,i])
seen=np.zeros((NY,NX),bool); comps=[]
for j0 in range(NY):
    for i0 in range(NX):
        if seen[j0,i0] or R[j0,i0] or not walk[j0,i0] or F[j0,i0]>3.3: continue
        q=deque([(j0,i0)]); seen[j0,i0]=True; cells=[]
        while q:
            j,i=q.popleft(); cells.append((j,i))
            for dj,di in ((1,0),(-1,0),(0,1),(0,-1)):
                a,b=j+dj,i+di
                if 0<=a<NY and 0<=b<NX and not seen[a,b] and not R[a,b] and walk[a,b] and abs(F[a,b]-F[j,i])<=thr:
                    seen[a,b]=True; q.append((a,b))
        if len(cells)>=16:
            js=[c[0] for c in cells]; is_=[c[1] for c in cells]
            comps.append((len(cells)*0.25, round(1500+min(is_)*res,1),round(1500+(max(is_)+1)*res,1),round(min(js)*res,1),round((max(js)+1)*res,1), round(float(np.mean([F[c] for c in cells])),2)))
comps.sort(reverse=True)
for c in comps[:60]: print(c)
# ---- result ----
# {"result":"Code executed successfully: barracks front R2: True\n(100.0, 1584.5, 1604.5, 126.5, 131.5, 3.0)\n(86.0, 1656.0, 1673.5, 81.5, 86.5, 3.0)\n(
# 67.75, 1509.5, 1523.5, 3.5, 8.5, 1.5)\n(55.0, 1680.5, 1685.5, 2.0, 13.0, 1.5)\n(55.0, 1644.5, 1655.5, 117.5, 122.5, 3.0)\n(55.0, 1602.5, 1610.5, 81.5,
#  89.5, 3.0)\n(55.0, 1584.5, 1595.5, 111.5, 116.5, 3.0)\n(54.5, 1655.5, 1664.5, 93.0, 104.5, 3.0)\n(53.5, 1673.5, 1692.0, 71.5, 96.5, 2.97)\n(41.75, 16
# 74.0, 1692.5, 119.5, 140.5, 2.99)\n(40.0, 1674.5, 1682.5, 90.5, 95.5, 3.0)\n(40.0, 1668.5, 1676.5, 114.5, 119.5, 3.0)\n(40.0, 1665.0, 1673.0, 63.5, 68
# .5, 1.5)\n(40.0, 1644.5, 1649.5, 96.5, 104.5, 3.0)\n(40.0, 1632.5, 1640.5, 108.5, 113.5, 3.0)\n(40.0, 1632.5, 1640.5, 81.5, 86.5, 3.0)\n(40.0, 1623.5,
#  1628.5, 117.5, 125.5, 3.0)\n(40.0, 1617.5, 1622.5, 81.5, 89.5, 3.0)\n(40.0, 1608.5, 1616.5, 126.5, 131.5, 3.0)\n(40.0, 1602.5, 1607.5, 99.5, 107.5, 3

# ==============================================================================================================
# [0037] 2026-09-23 19:09:25  blender  ok
# ==============================================================================================================
import bpy, numpy as np, math
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R2"]; walk=S["walk2"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        s+= ("R" if R[j,i] else ("." if walk[j,i] else "#"))
    return s
print("x 1650..1670")
for y in np.arange(89,107,0.5): print(f"{y:5.1f}",row_str(y,1650,1670))
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if o.type!="MESH" or any(s in o.name for s in ("LipGrass","Weeds","Tree_","Plant_","Rock_Small","Pebbles","Mushroom")): continue
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
    if bx[0]<1666 and bx[1]>1654 and bx[2]<106 and bx[3]>92 and bx[4]<4.8 and bx[5]>3.2:
        print(o.name, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z))%360, tuple(round(v,2) for v in bx))
# ---- result ----
# {"result":"Code executed successfully: x 1650..1670\n 89.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 89.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 
# 90.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 90.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 91.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 91.5 R
# RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 92.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 92.5 RRRRR##########################RRRRRRRRR\n 93.0 RRRR###
# #############..##########RRRRRRRR\n 93.5 RRRR###.####................###RRRRRRRRR\n 94.0 RRRR#########..............####RRRRRRRRR\n 94.5 RRRR#########
# #..........########RRRRRRRR\n 95.0 #RRR##########.#....#...########RRRRRRRR\n 95.5 ##RRR#########.#....#...##...###RRRRRRRR\n 96.0 ##RR##########.....
# ........#####RRRRRRRR\n 96.5 ##RR#########............######RRRRRRRRR\n 97.0 #RRR###.#####..........########RRRRRRRRR\n 97.5 #RRR#########...........#

# ==============================================================================================================
# [0038] 2026-09-23 19:09:46  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V=[];Fc=[];off=0
    for n in names:
        o=bpy.data.objects[n]; oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
        vs=[mw@v.co for v in me.vertices]; V+=vs; Fc+=[[off+k for k in p.vertices] for p in me.polygons]; off+=len(vs); oe.to_mesh_clear()
    return BVHTree.FromPolygons(V,Fc)
a=bvh(["SM_VK_LowWall_GateArch_inst"])
for y in (92.7,93.0,93.3):
    for z in (3.1,3.3,3.6,4.2,5.0):
        p=Vector((1660.5,y,z)); l=a.ray_cast(p,Vector((-1,0,0)),4); r=a.ray_cast(p,Vector((1,0,0)),4); d=a.ray_cast(Vector((1660.5,y,6.0)),Vector((0,0,-1)),4)
        print(y,z,l[0] and round(l[0].x,2), r[0] and round(r[0].x,2), (round(r[0].x-l[0].x,2) if l[0] and r[0] else None))
    print("down", [ (round(x,2), (lambda h: h[0] and round(h[0].z,2))(a.ray_cast(Vector((x,y,6.0)),Vector((0,0,-1)),4))) for x in np.arange(1659.0,1662.1,0.25)])
# ---- result ----
# {"result":"Code executed successfully: 92.7 3.1 1660.31 1660.69 0.38\n92.7 3.3 1660.31 1660.69 0.38\n92.7 3.6 1660.31 1660.69 0.38\n92.7 4.2 1660.31 1
# 660.69 0.38\n92.7 5.0 1659.61 1661.4 1.79\ndown [(1659.0, 4.95), (1659.25, 5.12), (1659.5, 5.51), (1659.75, 5.85), (1660.0, 5.69), (1660.25, 5.88), (1
# 660.5, 5.61), (1660.75, 5.88), (1661.0, 5.69), (1661.25, 5.85), (1661.5, 5.5), (1661.75, 5.12), (1662.0, 4.89)]\n93.0 3.1 1659.66 1661.34 1.69\n93.0 3
# .3 1659.66 1661.34 1.69\n93.0 3.6 1659.66 1661.34 1.69\n93.0 4.2 1659.66 1661.34 1.69\n93.0 5.0 1659.61 1661.4 1.79\ndown [(1659.0, 5.0), (1659.25, 5.
# 94), (1659.5, 5.94), (1659.75, 5.94), (1660.0, 5.94), (1660.25, 5.88), (1660.5, 5.61), (1660.75, 5.88), (1661.0, 5.94), (1661.25, 5.94), (1661.5, 5.94
# ), (1661.75, 5.94), (1662.0, 4.99)]\n93.3 3.1 1659.53 1661.45 1.92\n93.3 3.3 1659.5 1661.43 1.94\n93.3 3.6 1659.47 1661.53 2.06\n93.3 4.2 None None No

# ==============================================================================================================
# [0039] 2026-09-23 19:10:29  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
t0=time.time()
p=shot("play_01_gate_south",(1626,50,16),(1626,72,4),lens=35,res=(1280,720),outdir=OUT)
print(p,time.time()-t0, bpy.data.scenes["VillageKit"].render.engine)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_01_gate_south.png 3.267810821533203 BLENDER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0040] 2026-09-23 19:11:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_02_postern_street_from_west",(1548,91.5,14),(1590,91.5,3),lens=30,res=(1280,720),outdir=OUT))
print(shot("play_03_westquarter_fronts",(1592,112,22),(1592,90,3),lens=28,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_02_postern_street_from_west.png\nC:\\Users\\danie\\AppData\\Roa
# ming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rer
# eview\\play\\play_03_westquarter_fronts.png\n"}

# ==============================================================================================================
# [0041] 2026-09-23 19:12:09  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_04_postern_close_outside",(1560,91.5,5.2),(1569,91.5,4.0),lens=35,res=(1280,720),outdir=OUT))
print(shot("play_05_postern_lane_overview",(1545,70,30),(1552,91.5,3),lens=30,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_04_postern_close_outside.png\nC:\\Users\\danie\\AppData\\Roamin
# g\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rerevi
# ew\\play\\play_05_postern_lane_overview.png\n"}

# ==============================================================================================================
# [0042] 2026-09-23 19:12:48  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_06_quarry_mouth",(1545,82,11),(1545,96,3.5),lens=32,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_06_quarry_mouth.png\n"}

# ==============================================================================================================
# [0043] 2026-09-23 19:13:23  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_07_footbridge_from_east",(1556,42,18),(1530,42,0.5),lens=26,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_07_footbridge_from_east.png\n"}

# ==============================================================================================================
# [0044] 2026-09-23 19:14:29  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def bb(o):
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    return (round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2),round(max(w.z for w in ws),2))
W=[o for o in c.all_objects if "Tree_Willow" in o.name]
for o in W: print(o.name, tuple(round(v,2) for v in o.location), bb(o))
for i in range(len(W)):
    for j in range(i+1,len(W)): print(W[i].name,W[j].name, round((W[i].location.xy-W[j].location.xy).length,2))
for n in ("SM_VK_Prop_Barge_inst","SM_VK_Quay_Stair_inst"): print(n, tuple(round(v,2) for v in bpy.data.objects[n].location), bb(bpy.data.objects[n]))
for o in c.all_objects:
    if ("Reeds" in o.name or "Willow" in o.name or "Rock_Pebbles" in o.name) and 1597<o.location.x<1614 and 46<o.location.y<54: print("quay veg",o.name,tuple(round(v,2) for v in o.location))
# willows near roads/ramps: cell of each
for o in W:
    i=int((o.location.x-1500)//3); j=int(o.location.y//3); print(o.name,"cell",i,j)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Willow_inst.001 (1714.9, 22.27, 0.0) (1709.21, 1720.67, 16.58, 28.08, -0.43, 5.02)\nSM_VK_Tree_Willo
# w_inst.002 (1662.51, 30.89, 0.0) (1657.09, 1667.9, 25.53, 36.39, -0.43, 5.02)\nSM_VK_Tree_Willow_inst.003 (1504.28, 34.29, 0.0) (1498.61, 1510.07, 28.
# 53, 39.96, -0.43, 5.02)\nSM_VK_Tree_Willow_inst.001 SM_VK_Tree_Willow_inst.002 53.09\nSM_VK_Tree_Willow_inst.001 SM_VK_Tree_Willow_inst.003 210.96\nSM
# _VK_Tree_Willow_inst.002 SM_VK_Tree_Willow_inst.003 158.26\nSM_VK_Prop_Barge_inst (1605.0, 45.8, -0.6) (1598.93, 1608.78, 44.0, 47.6, -0.98, 4.6)\nSM_
# VK_Quay_Stair_inst (1606.5, 48.45, 0.0) (1605.0, 1608.0, 47.61, 48.91, -2.0, 0.08)\nquay veg SM_VK_Plant_Reeds_inst.047 (1612.98, 49.28, 0.0)\nSM_VK_T
# ree_Willow_inst.001 cell 71 7\nSM_VK_Tree_Willow_inst.002 cell 54 10\nSM_VK_Tree_Willow_inst.003 cell 1 11\n"}

# ==============================================================================================================
# [0045] 2026-09-23 19:15:09  blender  ERROR
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
S=bpy.app.driver_namespace["_rr_play"]; bt=S["bt"]
def bb(o):
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    return (round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2),round(max(w.z for w in ws),2))
def terr_under(o):
    x0,x1,y0,y1,z0,z1=bb(o); hs=[]
    for a in range(5):
        for b in range(5):
            x=x0+(x1-x0)*a/4; y=y0+(y1-y0)*b/4
            h=bt.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
            if h[0]: hs.append(h[0].z)
    return round(min(hs),2), round(max(hs),2)
for o in c.all_objects:
    n=o.name
    if any(k in n for k in ("Prop_Laundry","Prop_FishRack","Prop_Cart","Prop_Crates","Prop_DryingRack","Prop_NetRack","Pile_Fish","Prop_Creels","Prop_BarrelStack","Prop_Sacks","Prop_Woodpile","Prop_Wheelbarrow","Prop_Trough")):
        lo,hi=terr_under(o)
        if hi-lo>0.3: print("STRADDLE",n, tuple(round(v,2) for v in o.location), bb(o), lo,hi)
for n in ("SM_VK_Prop_Laundry_inst.002","SM_VK_Prop_FishRack_inst","SM_VK_Prop_Cart_inst.008","SM_VK_Prop_Crates_inst.007"):
    o=bpy.data.objects.get(n); print(n, o and (tuple(round(v,2) for v in o.location), bb(o), terr_under(o)))
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: min() arg is an empty sequence"}

# ==============================================================================================================
# [0046] 2026-09-23 19:15:59  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
S=bpy.app.driver_namespace["_rr_play"]; bt=S["bt"]
def bb(o):
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    return (round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2),round(max(w.z for w in ws),2))
def terr_under(o):
    x0,x1,y0,y1,z0,z1=bb(o); hs=[]
    for a in range(5):
        for b in range(5):
            x=x0+(x1-x0)*a/4; y=y0+(y1-y0)*b/4
            h=bt.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
            if h[0]: hs.append(h[0].z)
    return (round(min(hs),2), round(max(hs),2)) if hs else (None,None)
for o in c.all_objects:
    n=o.name
    if o.type=="MESH" and n.startswith(("SM_VK_Prop_","SM_VK_Pile_")) and not any(k in n for k in ("Barge","Rowboat","Lantern","Sign","Banner","FlowerBox","Festoon","Bunting","Crane","HoistBeam","Shelf")):
        lo,hi=terr_under(o)
        if lo is not None and hi-lo>0.3: print("STRADDLE",n, tuple(round(v,2) for v in o.location), bb(o), lo,hi)
for n in ("SM_VK_Prop_Laundry_inst.002","SM_VK_Prop_FishRack_inst","SM_VK_Prop_Cart_inst.008","SM_VK_Prop_Crates_inst.007"):
    o=bpy.data.objects.get(n); print(n, o and (tuple(round(v,2) for v in o.location), bb(o), terr_under(o)))
# ---- result ----
# {"result":"Code executed successfully: STRADDLE SM_VK_Prop_LavoirBasin_inst (1641.0, 49.5, 0.0) (1638.28, 1643.72, 47.84, 50.52, -0.35, 0.84) -0.39 0.
# 0\nSTRADDLE SM_VK_Prop_HandPump_inst (1645.2, 48.3, 0.0) (1644.39, 1646.34, 47.47, 48.85, -0.01, 2.17) -0.83 0.0\nSTRADDLE SM_VK_Prop_Woodpile_inst.00
# 4 (1660.8, 49.3, 0.0) (1660.15, 1661.45, 47.1, 50.8, -0.05, 1.47) -1.25 0.0\nSTRADDLE SM_VK_Prop_BarrelStack_inst.010 (1654.6, 48.5, 0.0) (1653.99, 16
# 55.15, 47.54, 49.46, 0.0, 1.5) -0.76 0.0\nSTRADDLE SM_VK_Pile_Fish_2_inst (1693.2, 25.2, 0.05) (1692.81, 1693.97, 23.88, 25.65, 0.04, 0.41) -1.5 -0.05
# \nSTRADDLE SM_VK_Prop_HerbBundles_inst (1571.8, 60.9, 1.5) (1570.55, 1573.05, 60.69, 61.55, 1.5, 3.6) 1.09 1.5\nSM_VK_Prop_Laundry_inst.002 ((1641.2, 
# 53.3, 0.0), (1638.63, 1643.77, 52.92, 53.68, 0.0, 2.6), (0.0, 0.0))\nSM_VK_Prop_FishRack_inst ((1655.09, 52.6, 0.0), (1653.42, 1656.75, 51.66, 53.54, 

# ==============================================================================================================
# [0047] 2026-09-23 19:16:23  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def bb(o):
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    return (round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2),round(max(w.z for w in ws),2))
for o in c.all_objects:
    if o.type=="MESH" and 1566<o.location.x<1594 and 46<o.location.y<64 and not any(k in o.name for k in ("LipGrass","Weeds","Wall_","Corner_","Roof","Chimney")):
        print(o.name, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z))%360, bb(o))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_FlowerBox_inst.102 (1577.45, 55.5, 0.78) 270 (1577.17, 1577.71, 54.79, 56.25, 0.55, 1.45)\nSM_VK_Pro
# p_Planter_inst.015 (1577.25, 51.45, 0.0) 270 (1576.9, 1577.6, 51.11, 51.79, 0.0, 1.06)\nSM_VK_Prop_Lantern_inst.024 (1577.7, 51.5, 2.55) 270 (1577.12,
#  1577.8, 51.34, 51.66, 2.12, 2.73)\nSM_VK_Prop_FlowerBox_inst.103 (1584.55, 52.5, 0.78) 90 (1584.29, 1584.83, 51.75, 53.21, 0.55, 1.45)\nSM_VK_Prop_La
# ntern_inst.025 (1584.3, 56.5, 2.55) 90 (1584.2, 1584.88, 56.34, 56.66, 2.12, 2.73)\nSM_VK_WaterWheel_inst (1579.5, 46.65, 1.3) 270 (1576.61, 1582.39, 
# 45.45, 47.75, -1.59, 4.19)\nSM_VK_Quay_Straight_inst (1576.5, 47.6, 0.0) 0 (1575.0, 1578.0, 47.04, 48.05, -2.0, 0.03)\nSM_VK_Quay_Straight_inst.001 (1
# 579.5, 47.6, 0.0) 0 (1578.0, 1581.0, 47.04, 48.05, -2.0, 0.03)\nSM_VK_Quay_Straight_inst.002 (1582.5, 47.6, 0.0) 0 (1581.0, 1584.0, 47.04, 48.05, -2.0

# ==============================================================================================================
# [0048] 2026-09-23 19:16:50  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R2"]; walk=S["walk2"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        s+= ("R" if R[j,i] else ("." if walk[j,i] else "#"))
    return s
def hrow(y,x0,x1):
    j=int(y/res); return "".join(str(min(9,max(0,int(round(F[j,i]/1.5*4))))) for i in range(int((x0-1500)/res),int((x1-1500)/res)))
print("x 1564..1592 ; height code = z/0.375")
for y in np.arange(52,70,0.5): print(f"{y:5.1f}",row_str(y,1564,1592),"  ",hrow(y,1564,1592))
# ---- result ----
# {"result":"Code executed successfully: x 1564..1592 ; height code = z/0.375\n 52.0 RRRRRRRRRRRRRRRRRRRRRRRRRR###..........#####RRRRRRRRRRRR 0000000000
# 0000000000000000000000000000000000000000000000\n 52.5 RRRRRRRRRRRRRRRRRRRRRRRRRR###..........##.##RRRRRRRRRRRR 000000000000000000000000000000000000000
# 00000000000000000\n 53.0 RRRRRRRRRRRRRRRRRRRRRRRRR####..........#####RRRRRRRRRRRR 00000000000000000000000000000000000000000000000000000000\n 53.5 ....
# .....RRRRRRRRRRRRRRRR####..........#####RRRRRRRRRRRR 22222222200000000000000000000000000000000000000000000000\n 54.0 RRRRRRRRR.RRRRRRRRRRRRRRR####....
# ......#####RRRRRRRRR.RR 44444444420000000000000000000000000000000000000000000244\n 54.5 RRRRRRRRRRRRRRRRRRRRRRRRRR###..........#####RRRRRRRR.RRR 44444
# 444442000000000000000000000000000000000000000002444\n 55.0 RRRRRRRRRRRRRRRRRRRRRRRRRRR##..........###RRRRRRRRRRRRRR 4444444444200000000000000000000000

# ==============================================================================================================
# [0049] 2026-09-23 19:17:29  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]
for x in (1573.2,1575.2,1577.2):
    ix=int((x-1500)/0.5); print(x,[(round((j+0.5)*0.5,2),round(float(F[j,ix]),2)) for j in range(int(56/0.5),int(63/0.5))])
# fisher ramp (5,66-67): x 1698-1704, y 15-18
for x in (1699.2,1701.2,1703.2):
    ix=int((x-1500)/0.5); print("fisher",x,[(round((j+0.5)*0.5,2),round(float(F[j,ix]),2)) for j in range(int(12/0.5),int(20/0.5))])
# ridge stair (33,9): x 1527-1530, y 99-102
for x in (1527.7,1528.7,1529.7):
    ix=int((x-1500)/0.5); print("stair",x,[(round((j+0.5)*0.5,2),round(float(F[j,ix]),2)) for j in range(int(97/0.5),int(106/0.5))])
# ---- result ----
# {"result":"Code executed successfully: 1573.2 [(56.25, -0.0), (56.75, 0.0), (57.25, 0.0), (57.75, 0.0), (58.25, 0.0), (58.75, 0.12), (59.25, 0.38), (5
# 9.75, 0.62), (60.25, 0.88), (60.75, 1.12), (61.25, 1.38), (61.75, 1.5), (62.25, 1.5), (62.75, 1.5)]\n1575.2 [(56.25, 0.0), (56.75, 0.0), (57.25, 0.0),
#  (57.75, 0.0), (58.25, 0.0), (58.75, 0.12), (59.25, 0.38), (59.75, 0.62), (60.25, 0.88), (60.75, 1.12), (61.25, 1.38), (61.75, 1.5), (62.25, 1.5), (62
# .75, 1.5)]\n1577.2 [(56.25, 0.0), (56.75, 0.0), (57.25, 0.0), (57.75, 0.0), (58.25, 0.0), (58.75, 0.12), (59.25, 0.38), (59.75, 0.62), (60.25, 0.88), 
# (60.75, 1.12), (61.25, 1.38), (61.75, 1.5), (62.25, 1.5), (62.75, 1.5)]\nfisher 1699.2 [(12.25, 1.5), (12.75, 1.5), (13.25, 1.5), (13.75, 1.38), (14.2
# 5, 1.12), (14.75, 0.88), (15.25, 0.62), (15.75, 0.38), (16.25, 0.12), (16.75, 0.0), (17.25, 0.0), (17.75, 0.0), (18.25, 0.0), (18.75, 0.0), (19.25, 0.

# ==============================================================================================================
# [0050] 2026-09-23 19:18:12  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_08_fisher_ramp",(1700,-4,22),(1697,20,0.5),lens=30,res=(1280,720),outdir=OUT))
print(shot("play_09_chapel_forecourt",(1640,94,20),(1650,115,4),lens=30,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_08_fisher_ramp.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\
# \scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\
# play_09_chapel_forecourt.png\n"}

# ==============================================================================================================
# [0051] 2026-09-23 19:19:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_10_smokehouse_fishrack",(1644,60,9),(1656,51.5,0.5),lens=30,res=(1280,720),outdir=OUT))
print(shot("play_11_festival_arch",(1660.5,84,8),(1660.5,96,3.5),lens=32,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_10_smokehouse_fishrack.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview
# \\play\\play_11_festival_arch.png\n"}

# ==============================================================================================================
# [0052] 2026-09-23 19:19:48  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_11_festival_arch",(1660.5,88.6,6.5),(1660.5,96,3.8),lens=28,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_11_festival_arch.png\n"}

# ==============================================================================================================
# [0053] 2026-09-23 19:20:20  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if o.type=="MESH" and 1524<o.location.x<1536 and 97<o.location.y<112 and not any(k in o.name for k in ("LipGrass",)):
        print(o.name, tuple(round(v,2) for v in o.location))
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_12_ridge_stair",(1536,86,14),(1528.5,102,4),lens=30,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Plant_Fern_inst.071 (1534.61, 98.15, 6.0)\nSM_VK_Rock_Boulder_A_inst.002 (1534.02, 101.32, 6.0)\nSM_VK_Mu
# shrooms_Brown_inst.022 (1524.42, 104.17, 4.5)\nSM_VK_Tree_Oak_B_inst.014 (1530.8, 103.44, 4.5)\nSM_VK_Tree_Pine_Young_inst.074 (1526.09, 106.75, 4.5)\
# nSM_VK_Mushrooms_Brown_inst.024 (1525.19, 105.96, 4.5)\nSM_VK_Tree_Oak_B_inst.015 (1527.65, 106.71, 4.5)\nSM_VK_Tree_Oak_A_inst.020 (1524.41, 110.7, 4
# .5)\nSM_VK_Bush_Round_inst.043 (1525.7, 108.83, 4.5)\nSM_VK_Tree_Oak_Autumn_inst.001 (1527.94, 109.48, 4.5)\nSM_VK_Tree_Pine_A_inst.064 (1531.09, 110.
# 2, 4.5)\nSM_VK_Rock_Small_A_inst.030 (1535.02, 109.52, 6.0)\nSM_VK_Mushrooms_Brown_inst.025 (1528.46, 111.68, 4.5)\nSM_VK_Rock_Pebbles_inst.058 (1532.
# 56, 108.8, 4.45)\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d

# ==============================================================================================================
# [0054] 2026-09-23 19:21:06  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R2"]
j=int(91.5/0.5)
print([(round(1500+(i+0.5)*0.5,1),round(float(F[j,i]),2),int(R[j,i])) for i in range(int((1526-1500)/0.5),int((1570-1500)/0.5),2)])
j=int(88.5/0.5)
print([(round(1500+(i+0.5)*0.5,1),round(float(F[j,i]),2),int(R[j,i])) for i in range(int((1526-1500)/0.5),int((1545-1500)/0.5),2)])
# ---- result ----
# {"result":"Code executed successfully: [(1526.2, 3.0, 1), (1527.2, 3.0, 1), (1528.2, 3.0, 1), (1529.2, 3.0, 1), (1530.2, 3.0, 1), (1531.2, 3.0, 1), (1
# 532.2, 3.0, 1), (1533.2, 5.98, 0), (1534.2, 6.0, 0), (1535.2, 6.0, 0), (1536.2, 6.0, 0), (1537.2, 6.0, 0), (1538.2, 6.0, 0), (1539.2, 5.32, 0), (1540.
# 2, 3.0, 1), (1541.2, 3.0, 1), (1542.2, 3.0, 1), (1543.2, 3.0, 1), (1544.2, 3.0, 1), (1545.2, 3.0, 1), (1546.2, 3.0, 1), (1547.2, 3.0, 1), (1548.2, 3.0
# , 1), (1549.2, 3.0, 1), (1550.2, 3.0, 1), (1551.2, 5.98, 0), (1552.2, 6.0, 0), (1553.2, 6.0, 0), (1554.2, 6.0, 0), (1555.2, 6.0, 0), (1556.2, 6.0, 0),
#  (1557.2, 5.32, 0), (1558.2, 3.0, 1), (1559.2, 3.0, 1), (1560.2, 3.0, 1), (1561.2, 3.0, 1), (1562.2, 3.0, 1), (1563.2, 3.0, 1), (1564.2, 3.0, 1), (156
# 5.2, 3.0, 1), (1566.2, 3.0, 1), (1567.2, 3.0, 1), (1568.2, 3.0, 1), (1569.2, 3.0, 1)]\n[(1526.2, 3.0, 1), (1527.2, 3.0, 1), (1528.2, 3.0, 1), (1529.2,

# ==============================================================================================================
# [0055] 2026-09-23 19:21:44  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_13_postern_lane_over_shoulders",(1545,76,16),(1545,93,4),lens=24,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_13_postern_lane_over_shoulders.png\n"}

# ==============================================================================================================
# [0056] 2026-09-23 19:22:50  blender  ok
# ==============================================================================================================
import bpy, math, numpy as np
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R2"]; walk=S["walk2"]
for n in ("SM_VK_Prop_TreadwheelCrane_inst","SM_VK_Prop_TreadwheelCrane_Wheel_inst","SM_VK_Windmill_inst","SM_VK_Prop_Beacon_inst"):
    o=bpy.data.objects.get(n)
    if not o: print(n,"missing"); continue
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    print(n, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z))%360, (round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2)))
def reg(x0,x1,y0,y1):
    j0,j1=int(y0/0.5),int(y1/0.5); i0,i1=int((x0-1500)/0.5),int((x1-1500)/0.5)
    sub=R[j0:j1,i0:i1]; w=walk[j0:j1,i0:i1]; f=F[j0:j1,i0:i1]
    return int(sub.sum()), int(w.sum()), round(float(f.min()),2), round(float(f.max()),2)
print("crane surroundings (1538-1552, 102-108):", reg(1538,1552,102.5,108))
print("level-4 ridge reach total:", int((R & (F>5.9)).sum()), "walkable lvl4:", int((walk & (F>5.9)).sum()))
print("level-3 reach:", int((R & (F>4.4)&(F<4.6)).sum()), int((walk & (F>4.4)&(F<4.6)).sum()))
print("windmill front (1596-1602, 59-62):", reg(1596,1602,59,62.5))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_TreadwheelCrane_inst (1544.4, 104.4, 6.0) 270 (1542.39, 1546.41, 97.31, 107.05, 5.95)\nSM_VK_Prop_Tr
# eadwheelCrane_Wheel_inst (1544.4, 105.4, 8.2) 270 (1543.7, 1545.1, 103.6, 107.2, 6.4)\nSM_VK_Windmill_inst (-40.0, -198.0, 0.0) 340 (-3.32, 3.32, -3.9
# , 5.28, 0.0)\nSM_VK_Prop_Beacon_inst (1653.4, 9.8, 1.5) 20 (1651.89, 1655.31, 7.99, 11.33, 0.7)\ncrane surroundings (1538-1552, 102-108): (0, 252, 6.0
# , 6.0)\nlevel-4 ridge reach total: 0 walkable lvl4: 24240\nlevel-3 reach: 2287 7359\nwindmill front (1596-1602, 59-62): (61, 62, 1.5, 1.5)\n"}

# ==============================================================================================================
# [0057] 2026-09-23 19:23:40  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
objs=[o for o in c.all_objects if o.type=="MESH"]
doors=[o for o in objs if ("_Door" in o.name and not o.name.startswith("SM_VK_Prop")) or "Wall_Stone_Passage" in o.name or "Postern" in o.name or "Chapel_Wall_Door" in o.name]
cand=[o for o in objs if any(k in o.name for k in ("Crop_","Tree_","Bush_","Plant_","Rock_Boulder","Deco_Hedge","Prop_GardenBed","Prop_Planter"))]
def corners(o):
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]; return ws
for d in doors:
    r=d.rotation_euler.z; c_,s_=math.cos(r),math.sin(r)
    for o in cand:
        if abs(o.location.x-d.location.x)>6 or abs(o.location.y-d.location.y)>6: continue
        if abs(o.location.z-d.location.z)>0.8: continue
        P=[((w.x-d.location.x)*c_+(w.y-d.location.y)*s_, -(w.x-d.location.x)*s_+(w.y-d.location.y)*c_) for w in corners(o)]
        u0=min(p[0] for p in P); u1=max(p[0] for p in P); v0=min(p[1] for p in P); v1=max(p[1] for p in P)
        # trees: use trunk only (location)
        if "Tree_" in o.name:
            lx=(o.location.x-d.location.x)*c_+(o.location.y-d.location.y)*s_; ly=-(o.location.x-d.location.x)*s_+(o.location.y-d.location.y)*c_
            u0,u1,v0,v1=lx-0.4,lx+0.4,ly-0.4,ly+0.4
        if u1>-0.65 and u0<0.65 and v0<-0.2 and v1>-2.3:
            print(d.name,(round(d.location.x,1),round(d.location.y,1)),"<-",o.name,(round(o.location.x,2),round(o.location.y,2)),"v",round(v0,2),round(v1,2),"u",round(u0,2),round(u1,2))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Wattle_Door_inst (1509.0, 7.5) <- SM_VK_Deco_Bush_inst.004 (1507.6, 8.3) v -2.7 -0.27 u -1.93 0.43\n
# "}

# ==============================================================================================================
# [0058] 2026-09-23 19:24:08  blender  ok
# ==============================================================================================================
import bpy, math, numpy as np
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
H,W=56,72
road=np.zeros((H,W),bool)
road[0:32,41:43]=True; road[31:36,36:48]=True; road[39:42,24:41]=True; road[36:39,39:41]=True; road[36:39,47:52]=True
road[29,44:62]=True; road[30,23:41]=True; road[30,11:23]=True; road[9,11:41]=True; road[9:34,9:11]=True
road[12:16,:]=False
for o in c.all_objects:
    if o.type!="MESH" or not any(k in o.name for k in ("Bush_","Rock_Boulder","Rock_Small","Plant_Fern","Plant_TallGrass","Plant_Wildflowers","Tree_","Deco_Bush","Crop_","Mushrooms")): continue
    i=int((o.location.x-1500)//3); j=int(o.location.y//3)
    if 0<=i<W and 0<=j<H and road[j,i]:
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        sx=max(w.x for w in ws)-min(w.x for w in ws); sy=max(w.y for w in ws)-min(w.y for w in ws)
        print(o.name,(round(o.location.x,2),round(o.location.y,2),round(o.location.z,2)),"cell",i,j,"size",round(sx,1),round(sy,1))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0059] 2026-09-23 19:24:23  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if o.type=="MESH" and any(k in o.name for k in ("Bush_","Rock_","Plant_","Tree_","Crop_","Deco_Bush","Hydrangea")) and 1566<o.location.x<1625 and 87<o.location.y<97:
        ws=[o.matrix_world@Vector(b) for b in o.bound_box]
        print(o.name,(round(o.location.x,2),round(o.location.y,2),round(o.location.z,2)),(round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2)))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Bush_Round_inst.038 (1585.68, 93.33, 3.0) (1583.75, 1587.54, 91.48, 95.29)\nSM_VK_Crop_Carrot_inst.016 (1
# 594.5, 94.5, 3.0) (1593.31, 1595.72, 93.25, 95.72)\nSM_VK_Crop_Cabbage_inst.012 (1600.5, 94.5, 3.0) (1599.24, 1601.76, 93.26, 95.74)\nSM_VK_Crop_Cabba
# ge_inst.013 (1603.5, 94.5, 3.0) (1602.26, 1604.74, 93.24, 95.76)\nSM_VK_Plant_Wildflowers_inst.055 (1606.88, 94.99, 3.0) (1605.92, 1608.0, 93.97, 96.1
# 2)\n"}

# ==============================================================================================================
# [0060] 2026-09-23 19:24:48  blender  ok
# ==============================================================================================================
import bpy, math, numpy as np
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
H,W=56,72
road=np.zeros((H,W),bool)
road[0:32,41:43]=True; road[31:36,36:48]=True; road[39:42,24:41]=True; road[36:39,39:41]=True; road[36:39,47:52]=True
road[29,44:62]=True; road[30,23:41]=True; road[9,11:41]=True; road[9:34,9:11]=True; road[12:16,:]=False
out=[]
for o in c.all_objects:
    if o.type!="MESH" or not any(k in o.name for k in ("Bush_","Rock_Boulder","Hydrangea","Deco_Bush","Tree_")): continue
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    x0,x1,y0,y1=min(w.x for w in ws)-1500,max(w.x for w in ws)-1500,min(w.y for w in ws),max(w.y for w in ws)
    if "Tree_" in o.name:  # trunk only
        x0,x1,y0,y1=o.location.x-1500-0.4,o.location.x-1500+0.4,o.location.y-0.4,o.location.y+0.4
    best=0
    for j in range(max(0,int(y0//3)),min(H,int(y1//3)+1)):
        for i in range(max(0,int(x0//3)),min(W,int(x1//3)+1)):
            if road[j,i]:
                ox=min(x1,3*i+3)-max(x0,3*i); oy=min(y1,3*j+3)-max(y0,3*j)
                if ox>0 and oy>0: best=max(best,min(ox,oy))
    if best>0.6: out.append((round(best,2),o.name,(round(o.location.x,2),round(o.location.y,2),round(o.location.z,1))))
for r in sorted(out,reverse=True): print(r)
# ---- result ----
# {"result":"Code executed successfully: (1.52, 'SM_VK_Bush_Round_inst.038', (1585.68, 93.33, 3.0))\n(1.23, 'SM_VK_Bush_Round_inst.025', (1582.88, 26.37
# , 1.5))\n"}

# ==============================================================================================================
# [0061] 2026-09-23 19:25:52  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; g=S["g"]
for y in (70.5,71.0,71.5,72.0,72.5,73.0,74.0,74.5,75.5,76.5,77.5):
    p=Vector((1626,y,3.6)); l=g.ray_cast(p,Vector((-1,0,0)),10); r=g.ray_cast(p,Vector((1,0,0)),10)
    print(y, l[0] and round(l[0].x,2), r[0] and round(r[0].x,2), round(r[0].x-l[0].x,2) if l[0] and r[0] else None)
for n in ("SM_VK_Gatehouse_GateLeaf_inst","SM_VK_Gatehouse_GateLeaf_inst.001"):
    o=bpy.data.objects[n]; print(n, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z),1))
# ---- result ----
# {"result":"Code executed successfully: 70.5 1624.23 1627.77 3.55\n71.0 1624.65 1627.35 2.7\n71.5 1624.87 1627.13 2.27\n72.0 1624.97 1627.03 2.07\n72.5
#  1624.87 1627.13 2.27\n73.0 1624.65 1627.35 2.7\n74.0 1624.4 1627.6 3.2\n74.5 1624.4 1627.6 3.2\n75.5 1624.4 1627.6 3.2\n76.5 1624.4 1627.6 3.2\n77.5 
# 1624.44 1627.56 3.12\nSM_VK_Gatehouse_GateLeaf_inst (1624.4, 73.8, 3.0) 78.0\nSM_VK_Gatehouse_GateLeaf_inst.001 (1627.6, 73.8, 3.0) 102.0\n"}

# ==============================================================================================================
# [0062] 2026-09-23 19:26:32  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_14_mill_inlet_ramp",(1586,46,10),(1574,60,1.0),lens=30,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_14_mill_inlet_ramp.png\n"}

# ==============================================================================================================
# [0063] 2026-09-23 19:27:18  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_14_mill_inlet_ramp",(1560,50,9),(1575,60,0.8),lens=30,res=(1280,720),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_14_mill_inlet_ramp.png\n"}

# ==============================================================================================================
# [0064] 2026-09-23 19:28:04  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; R=S["R2"]; F=S["F"]
res=0.5
def width_x(y,xc,x0,x1):
    j=int(y/res); ic=int((xc-1500)/res)
    if not R[j,ic]: return 0
    a=ic
    while a-1>=int((x0-1500)/res) and R[j,a-1]: a-=1
    b=ic
    while b+1<int((x1-1500)/res) and R[j,b+1]: b+=1
    return (b-a+1)*res
def width_y(x,yc,y0,y1):
    i=int((x-1500)/res); jc=int(yc/res)
    if not R[jc,i]: return 0
    a=jc
    while a-1>=int(y0/res) and R[a-1,i]: a-=1
    b=jc
    while b+1<int(y1/res) and R[b+1,i]: b+=1
    return (b-a+1)*res
mr=[(y,width_x(y,1626.2,1618,1634)) for y in np.arange(0.25,100,0.5)]
print("main road pinch <3m:",[(round(y,2),w) for y,w in mr if w<3.0])
wr=[(y,width_x(y,1530.2,1524,1536)) for y in np.arange(27.25,102,0.5)]
print("west road pinch <3m:",[(round(y,2),w) for y,w in wr if w<3.0])
ps=[(x,width_y(x,91.6,87,96)) for x in np.arange(1566.25,1623,0.5)]
print("postern street (y-width at y91.6):",[(round(x,2),w) for x,w in ps if w<3.0])
rr=[(x,width_y(x,28.6,24,32)) for x in np.arange(1533.25,1623,0.5)]
print("river road row9:",[(round(x,2),w) for x,w in rr if w<2.5])
# ---- result ----
# {"result":"Code executed successfully: main road pinch <3m: [(70.25, 2.0), (70.75, 2.0), (71.25, 1.0), (71.75, 1.0), (72.25, 1.5), (72.75, 2.0), (73.2
# 5, 2.0), (73.75, 2.0), (74.25, 2.0), (74.75, 2.0), (75.25, 2.0), (77.75, 2.0), (98.75, 0), (99.25, 0), (99.75, 0)]\nwest road pinch <3m: []\npostern s
# treet (y-width at y91.6): [(1567.75, 1.0), (1568.25, 1.0), (1568.75, 1.0), (1569.25, 1.0), (1569.75, 1.0), (1570.25, 1.0), (1579.25, 2.5), (1579.75, 2
# .5), (1580.25, 2.0), (1580.75, 2.0), (1581.75, 2.5), (1612.25, 0), (1612.75, 0)]\nriver road row9: []\n"}

# ==============================================================================================================
# [0065] 2026-09-23 19:28:18  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if o.type!="MESH": continue
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
    if bx[0]<1613.5 and bx[1]>1611.5 and bx[2]<93 and bx[3]>90.2 and bx[4]<4.9 and bx[5]>3.1:
        print(o.name, tuple(round(v,2) for v in o.location), round(math.degrees(o.rotation_euler.z))%360, tuple(round(v,2) for v in bx))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Corner_Stone_inst.149 (1611.0, 90.0, 3.0) 180 (1610.35, 1611.62, 89.35, 90.6, 2.94, 6.01)\nSM_VK_Turret_C
# orbel_inst.001 (1611.0, 90.0, 6.0) 180 (1610.4, 1612.8, 89.4, 91.8, 4.33, 6.14)\nSM_VK_Prop_LampPost_inst.029 (1612.6, 91.9, 3.0) 225 (1611.85, 1612.9
# 2, 91.58, 92.65, 3.0, 5.9)\n"}

# ==============================================================================================================
# [0066] 2026-09-23 19:28:56  blender  ok
# ==============================================================================================================
import bpy, numpy as np
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; R=S["R2"]; walk=S["walk2"]; Wz=S["Wz"]; D=S["Dplaza"]
res=0.5
def row_str(y,x0,x1):
    j=int(y/res); s=""
    for i in range(int((x0-1500)/res),int((x1-1500)/res)):
        wet=(not np.isnan(Wz[j,i])) and Wz[j,i]>F[j,i]+0.15
        s+= "~" if wet else ("R" if R[j,i] else ("." if walk[j,i] else "#"))
    return s
for y in np.arange(12,34,0.5): print(f"{y:5.1f}",row_str(y,1684,1712))
print("pier F", [round(float(F[int(y/0.5),int((1693.5-1500)/0.5)]),2) for y in np.arange(22,33,0.5)])
# ---- result ----
# {"result":"Code executed successfully: 12.0 ...########R####RRRRR##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 12.5 ...###.###RRR###RRRRR##RRRRRRRRRRRRRRRRRRR
# RRRRRRRRRRRRRR\n 13.0 #########RRRRR#RRRRRR##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 13.5 #######################RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 14.0 
# RRR##RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 14.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 15.0 RRRRRRRRRRRRRRRRRRRRRR
# RRRRRRRRRRRRRRRRRRRRRR............\n 15.5 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 16.0 RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
# RRRRRRRRRRRR\n 16.5 RRRRR#####RRRRRRRRRRRR#RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 17.0 RRRRR#####RRRRRRRRRRR#####RRRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 17.5 RR
# RRRR#####################RRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 18.0 RRRRRRRRR##################RRRRRRRRRRRRRRRRRRRRRRRRRRRRR\n 18.5 RRRRRRRRR##..........##R

# ==============================================================================================================
# [0067] 2026-09-23 19:29:21  blender  ok
# ==============================================================================================================
import bpy, math, numpy as np
from mathutils import Vector
S=bpy.app.driver_namespace["_rr_play"]; bo=S["bo"]
c=bpy.data.collections["VK_ValleyTown"]
doors=[o for o in c.all_objects if o.type=="MESH" and (("_Door" in o.name and not o.name.startswith("SM_VK_Prop")) or "Chapel_Wall_Door" in o.name)]
for d in doors:
    r=d.rotation_euler.z; nx,ny=math.sin(r),-math.cos(r)
    # start 0.7 m out (beyond wall thickness), cast along the normal at 3 heights, and 0.5 m to each side
    best=99
    for side in (-0.45,0,0.45):
        for dz in (0.4,1.0,1.7):
            o=Vector((d.location.x+nx*0.7-ny*side, d.location.y+ny*0.7+nx*side, d.location.z+dz))
            h=bo.ray_cast(o,Vector((nx,ny,0)),6.0)
            dist=(h[3]+0.7) if h[0] else 99
            best=min(best,dist)
    if best<2.2: print(d.name,(round(d.location.x,1),round(d.location.y,1),round(d.location.z,1)),round(math.degrees(r))%360,"free depth",round(best,2))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Timber_Door_inst.002 (1603.5, 84.0, 6.0) 0 free depth 1.45\n"}

# ==============================================================================================================
# [0068] 2026-09-23 19:29:54  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if o.type!="MESH" or "LipGrass" in o.name: continue
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    bx=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
    if bx[0]<1567 and bx[1]>1533 and bx[2]<92.7 and bx[3]>90.3 and bx[5]>3.2:
        print(o.name, tuple(round(v,2) for v in o.location), tuple(round(v,2) for v in bx))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_LeanTo_inst.010 (1539.0, 93.65, 3.0) (1537.3, 1540.7, 89.84, 93.81, 3.0, 6.53)\n"}

# ==============================================================================================================
# [0069] 2026-09-23 19:30:14  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\play"
print(shot("play_15_postern_street_topdown",(1596,97,26),(1596,91.5,3),lens=24,res=(1400,700),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\play\\play_15_postern_street_topdown.png\n"}

# ==============================================================================================================
# [0070] 2026-09-23 19:31:35  blender  ok
# ==============================================================================================================
import bpy, numpy as np, heapq
S=bpy.app.driver_namespace["_rr_play"]; F=S["F"]; walk=S["walk2"].copy(); D0=S["Dplaza"]
res=0.5; NY,NX=F.shape; thr=0.42
print("D at (1650,52.5) now:", round(float(D0[int(52.5/res),int((1650-1500)/res)]),1), " smokehouse door front now:", round(float(D0[int(52.5/res)-1:int(52.5/res)+2,int((1657.5-1500)/res)-1:int((1657.5-1500)/res)+2].min()),1))
# clear fish rack + fish pile footprint (keep smokehouse corner)
for jy in range(int(51.7/res),int(53.6/res)+1):
    for ix in range(int((1653.4-1500)/res),int((1656.8-1500)/res)+1):
        if abs(F[jy,ix])<0.05 and (1500+(ix+0.5)*res<1655.3 or (jy+0.5)*res>51.9): walk[jy,ix]=True
def dij(sx,sy,tx,ty):
    D=np.full((NY,NX),np.inf); s=(int(sy/res),int((sx-1500)/res)); D[s]=0; h=[(0.0,s)]
    t=(int(ty/res),int((tx-1500)/res))
    nb=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
    while h:
        d,(j,i)=heapq.heappop(h)
        if (j,i)==t: return d
        if d>D[j,i]: continue
        for dj,di,w in nb:
            a,b=j+dj,i+di
            if 0<=a<NY and 0<=b<NX and walk[a,b] and abs(F[a,b]-F[j,i])<=thr*w:
                if w>1 and not (walk[j,b] and walk[a,i]): continue
                nd=d+w*res
                if nd<D[a,b]: D[a,b]=nd; heapq.heappush(h,(nd,(a,b)))
    return None
print("without fish rack:", dij(1626,96.0,1657.5,52.75))
# ---- result ----
# {"result":"Code executed successfully: D at (1650,52.5) now: 66.0 smokehouse door front now: 166.5\nwithout fish rack: 73.535\n"}

# ==============================================================================================================
# [0071] 2026-09-23 19:31:54  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
ramps=[(10,41),(10,42),(17,41),(17,42),(22,41),(22,42),(10,9),(10,10),(17,9),(17,10),(23,9),(23,10),(33,9),(19,24),(19,25),(5,66),(5,67)]
cells=set(ramps)
for o in c.all_objects:
    if o.type!="MESH" or "LipGrass" in o.name or "Bridge" in o.name or "Gatehouse" in o.name: continue
    ws=[o.matrix_world@Vector(b) for b in o.bound_box]
    x0,x1,y0,y1=min(w.x for w in ws)-1500,max(w.x for w in ws)-1500,min(w.y for w in ws),max(w.y for w in ws)
    if "Tree_" in o.name: x0,x1,y0,y1=o.location.x-1500-0.4,o.location.x-1500+0.4,o.location.y-0.4,o.location.y+0.4
    hit=[]
    for (j,i) in cells:
        ox=min(x1,3*i+3)-max(x0,3*i); oy=min(y1,3*j+3)-max(y0,3*j)
        if ox>0.3 and oy>0.3: hit.append((i,j,round(ox,2),round(oy,2)))
    if hit: print(o.name,(round(o.location.x,2),round(o.location.y,2),round(o.location.z,2)),hit)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Corner_Stone_inst.129 (1578.0, 57.0, 0.0) [(25, 19, 0.6, 0.62)]\nSM_VK_Corner_Timber_inst.146 (1578.0, 57
# .0, 3.0) [(25, 19, 0.61, 0.61)]\nSM_VK_Roof_Gable_inst.068 (1581.0, 55.5, 5.8) [(25, 19, 1.52, 1.2)]\n"}

# ==============================================================================================================
# [0072] 2026-09-23 19:32:55  blender  ok
# ==============================================================================================================
import bpy
bpy.app.driver_namespace.pop("_rr_play",None)
print("_rr_play" in bpy.app.driver_namespace)
# ---- result ----
# {"result":"Code executed successfully: False\n"}
