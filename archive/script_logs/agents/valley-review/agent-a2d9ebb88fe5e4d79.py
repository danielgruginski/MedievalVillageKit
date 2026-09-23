# valley-review / agent-a2d9ebb88fe5e4d79.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 16:57:38  blender  ok
# ==============================================================================================================
import bpy
t = bpy.data.texts["vk_render"].as_string()
print(t[:3000])
print(len(bpy.data.collections["VK_ValleyTown"].all_objects))
# ---- result ----
# {"result":"Code executed successfully: import bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,len
# s=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is 
# None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.
# link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_e
# nd=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.render.

# ==============================================================================================================
# [0002] 2026-09-23 16:59:07  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
t=time.time()
p=shot("play_01_topdown",(1608,84,255),(1608,84.01,0),lens=30,res=(1600,900),outdir=OUT)
print(p, time.time()-t, bpy.data.scenes["VillageKit"].render.engine)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_01_topdown.png 3.737001419067383 BLENDER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0003] 2026-09-23 17:00:07  blender  ok
# ==============================================================================================================
import bpy, collections
c=bpy.data.collections["VK_ValleyTown"]
print([ch.name for ch in c.children])
objs=list(c.all_objects)
cnt=collections.Counter()
for o in objs:
    n=o.name.split(".")[0]
    cnt[n]+=1
print(len(cnt))
print(cnt.most_common(60))
o=objs[100]; print(o.name,o.type,o.data.name if o.data else None, o.parent, dict(o.items()) if o.keys() else {})
print([ (o.name,o.type) for o in objs[:10]])
# ---- result ----
# {"result":"Code executed successfully: []\n339\n[('SM_VKT_LipGrass_inst', 1344), ('SM_VK_Tree_Pine_Young_inst', 342), ('SM_VK_Tree_Pine_B_inst', 335),
#  ('SM_VK_Tree_Pine_A_inst', 324), ('SM_VK_Wall_Timber_Window_inst', 135), ('SM_VK_Deco_Weeds_inst', 125), ('SM_VK_Bush_Round_inst', 121), ('SM_VK_Town
# Wall_Straight_inst', 119), ('SM_VK_Rock_Small_A_inst', 113), ('SM_VK_Plant_Fern_inst', 112), ('SM_VK_Wall_Stone_inst', 101), ('SM_VK_Corner_Timber_ins
# t', 88), ('SM_VK_Rock_Pebbles_inst', 87), ('SM_VK_Rock_Small_B_inst', 86), ('SM_VK_Rock_Boulder_A_inst', 86), ('SM_VK_Corner_Stone_inst', 83), ('SM_VK
# _Mushrooms_Brown_inst', 75), ('SM_VK_Wall_Stone_Window_inst', 68), ('SM_VK_Tree_Oak_A_inst', 63), ('SM_VK_Tree_Oak_B_inst', 60), ('SM_VK_Tree_Birch_in
# st', 52), ('SM_VK_Prop_FlowerBox_inst', 41), ('SM_VK_Plant_TallGrass_inst', 39), ('SM_VK_Plant_Wildflowers_inst', 39), ('SM_VK_Prop_FlowerBox_Daisy_in

# ==============================================================================================================
# [0004] 2026-09-23 17:00:28  blender  ok
# ==============================================================================================================
import bpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W,H=72,56
L=np.ones((H,W),np.int32); water=np.zeros((H,W),bool)
jj,ii=np.mgrid[0:H,0:W]
L[10:18,:60]=0; water[12:16,:60]=True
L[5:19,58:]=0
lake=((ii-65.5)**2/40+(jj-12.5)**2/22<1.0)|((ii>=60)&(jj>=8)&(jj<=17))
water[lake&(ii>=58)]=True; water[12:16,58:60]=True
L[16:20,24:30]=0
L[24:47,20:64]=2; L[24:34,0:20]=2
L[34:47,0:20]=3; L[34:47,11:19]=4; L[39:47,0:9]=4
for j in range(47,H):
    for i in range(W):
        n=3+int(np.clip(round(1.1*math.sin(i/4.1)+0.9*math.cos(i/2.7+j/2.1)+(j-47)*0.35),0,2))
        L[j,i]=max(L[j,i],n)
# build BVH of terrain chunks
tc=bpy.data.collections["VK_ValleyTerrain"]
dg=bpy.context.evaluated_depsgraph_get()
verts=[];polys=[]
for o in tc.all_objects:
    if o.type!="MESH" or "Chunk" not in o.name: continue
    m=o.matrix_world; me=o.data; off=len(verts)
    verts+= [m@v.co for v in me.vertices]
    polys+= [[off+k for k in p.vertices] for p in me.polygons]
bvh=BVHTree.FromPolygons(verts,polys)
bpy.app.driver_namespace["_play_rev"]=dict(L=L,water=water,bvh=bvh)
mism=[]
Z=np.zeros((H,W))
for j in range(H):
    for i in range(W):
        x=1500+3*i+1.5; y=3*j+1.5
        hit=bvh.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))
        z=hit[0].z if hit[0] else -99
        Z[j,i]=z
        exp=L[j,i]*1.5-(1.5 if water[j,i] else 0)
        if abs(z-exp)>0.3: mism.append((i,j,int(L[j,i]),bool(water[j,i]),round(z,2)))
bpy.app.driver_namespace["_play_rev"]["Z"]=Z
print(len(verts),len(mism)); print(mism[:40])
# ---- result ----
# {"result":"Code executed successfully: 313035 0\n[]\n"}

# ==============================================================================================================
# [0005] 2026-09-23 17:01:04  blender  ok
# ==============================================================================================================
import bpy, time
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]
dg=bpy.context.evaluated_depsgraph_get()
print(bpy.context.scene.name)
t=time.time()
r=sc.ray_cast(dg,Vector((1626,20,10)),Vector((0,0,-1)))
print(r[0],r[4].name if r[4] else None,time.time()-t)
t=time.time()
for k in range(200):
    r=sc.ray_cast(dg,Vector((1500+k,60,4)),Vector((0,1,0)),distance=3)
print(time.time()-t)
# ---- result ----
# {"result":"Code executed successfully: VillageKit\nTrue VKV_Chunk_2_0 0.015766620635986328\n0.7065384387969971\n"}

# ==============================================================================================================
# [0006] 2026-09-23 17:01:35  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]
L=R["L"]; water=R["water"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
PASS=("Door","LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","VKV_Water","Rug","Grass","Porch","Stair","Bridge","Ramp","Puddle","Path","Moss","Leaves","Shadow","Decal","Hay_Loose","Straw")
def passable(n): return any(p in n for p in PASS)
def cast(a,b,z):
    d=(b-a); dist=d.length; d.normalize(); o=a.copy(); left=dist; hits=[]
    for _ in range(12):
        r=sc.ray_cast(dg,o,d,distance=left)
        if not r[0]: return None
        n=r[4].name
        if passable(n):
            step=(r[1]-o).length+0.02; o=r[1]+d*0.02; left-=step
            if left<=0: return None
            continue
        return n
    return None
def edge(i,j,i2,j2):
    z=L[j,i]*1.5+0.9
    a=Vector((1500+3*i+1.5,3*j+1.5,z)); b=Vector((1500+3*i2+1.5,3*j2+1.5,z))
    d=(b-a).normalized(); lat=Vector((-d.y,d.x,0))
    first=None
    for off in (0.0,-0.9,0.9):
        h=cast(a+lat*off,b+lat*off,z)
        if h is None: return None
        if first is None: first=h
    return first
if "edges" not in R: R["edges"]={}
E=R["edges"]
t=time.time()
J0,J1=0,20
for j in range(J0,J1):
    for i in range(72):
        for (di,dj) in ((1,0),(0,1)):
            i2,j2=i+di,j+dj
            if i2>=72 or j2>=56: continue
            if water[j,i] or water[j2,i2] or L[j,i]!=L[j2,i2]: continue
            E[(i,j,i2,j2)]=edge(i,j,i2,j2)
print(time.time()-t, len(E), sum(1 for v in E.values() if v))
# ---- result ----
# {"result":"Code executed successfully: 9.11345887184143 1918 156\n"}

# ==============================================================================================================
# [0007] 2026-09-23 17:02:08  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]
L=R["L"]; water=R["water"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
PASS=("Door","LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","VKV_Water","Rug","Grass","Porch","Stair","Bridge","Ramp","Puddle","Path","Moss","Leaves","Shadow","Decal","Hay_Loose","Straw")
def passable(n): return any(p in n for p in PASS)
def cast(a,b,z):
    d=(b-a); dist=d.length; d.normalize(); o=a.copy(); left=dist
    for _ in range(12):
        r=sc.ray_cast(dg,o,d,distance=left)
        if not r[0]: return None
        n=r[4].name
        if passable(n):
            step=(r[1]-o).length+0.02; o=r[1]+d*0.02; left-=step
            if left<=0: return None
            continue
        return n
    return None
def edge(i,j,i2,j2):
    z=L[j,i]*1.5+0.9
    a=Vector((1500+3*i+1.5,3*j+1.5,z)); b=Vector((1500+3*i2+1.5,3*j2+1.5,z))
    d=(b-a).normalized(); lat=Vector((-d.y,d.x,0))
    first=None
    for off in (0.0,-0.9,0.9):
        h=cast(a+lat*off,b+lat*off,z)
        if h is None: return None
        if first is None: first=h
    return first
E=R["edges"]
t=time.time()
for j in range(20,56):
    for i in range(72):
        for (di,dj) in ((1,0),(0,1)):
            i2,j2=i+di,j+dj
            if i2>=72 or j2>=56: continue
            if water[j,i] or water[j2,i2] or L[j,i]!=L[j2,i2]: continue
            E[(i,j,i2,j2)]=edge(i,j,i2,j2)
print(time.time()-t, len(E), sum(1 for v in E.values() if v))
# ---- result ----
# {"result":"Code executed successfully: 28.062544107437134 6581 1913\n"}

# ==============================================================================================================
# [0008] 2026-09-23 17:03:01  blender  ok
# ==============================================================================================================
import bpy, numpy as np, collections
R=bpy.app.driver_namespace["_play_rev"]
L=R["L"]; water=R["water"]; E=R["edges"]
W,H=72,56
adj=collections.defaultdict(list)
def isTree(n): return n and ("Tree_" in n or "Bush" in n or "Rock_Boulder" in n)
def add(a,b,tag): adj[a].append((b,tag)); adj[b].append((a,tag))
for (i,j,i2,j2),h in E.items():
    if h is None: add((i,j),(i2,j2),"ok")
    elif isTree(h): add((i,j),(i2,j2),"tree")
ramps=[((41,10),(41,9)),((42,10),(42,9)),((41,17),(41,18)),((42,17),(42,18)),((41,23),(41,24)),((42,23),(42,24)),((9,23),(9,24)),((10,23),(10,24)),((8,33),(8,34))]
for a,b in ramps: add(a,b,"ramp")
for c in (41,42):
    for j in range(11,16): add((c,j),(c,j+1),"bridge")
for j in range(11,16): add((12,j),(12,j+1),"bridge")
def bfs(start,allow_tree):
    seen={start}; q=collections.deque([start])
    while q:
        c=q.popleft()
        for (n,tag) in adj[c]:
            if tag=="tree" and not allow_tree: continue
            if n not in seen: seen.add(n); q.append(n)
    return seen
S1=bfs((41,0),False); S2=bfs((41,0),True)
R["S1"]=S1; R["S2"]=S2; R["adj"]=adj
print(len(S1),len(S2))
# print ascii map: '.' reachable, 't' reachable only via trees, '#' unreachable land, '~' water
rows=[]
for j in range(H-1,-1,-1):
    s=""
    for i in range(W):
        if water[j,i]: s+="~" if (i,j) not in S2 else "="
        elif (i,j) in S1: s+=str(L[j,i])
        elif (i,j) in S2: s+="t"
        else: s+="#"
    rows.append(f"{j:2d} "+s)
print("\n".join(rows))
# ---- result ----
# {"result":"Code executed successfully: 2588 2745\n55 ########################################################################\n54 ####################
# ####################################################\n53 ########################################################################\n52 ################
# ########################################################\n51 ########################################################################\n50 ############
# ############################################################\n49 ########################################################################\n48 ########
# ################################################################\n47 ########################################################################\n46 ####
# #####tt#########22222222####################################11111111\n45 #########tt#########22222222##22222##222222222222##22222##22222#11111111\n44 

# ==============================================================================================================
# [0009] 2026-09-23 17:03:27  blender  ok
# ==============================================================================================================
import bpy
R=bpy.app.driver_namespace["_play_rev"]; E=R["edges"]
out=[]
for (i,j,i2,j2),h in E.items():
    # crossing west wall (between col 22 and 23), east wall (62/63), south wall (rows 24/25), north (45/46)
    if (i==22 and i2==23) or (i==62 and i2==63):
        if 25<=j<=45: out.append(("WE",i,j,i2,j2,h))
    if (j==24 and j2==25) or (j==45 and j2==46):
        if 23<=i<=62: out.append(("SN",i,j,i2,j2,h))
print([o for o in out if o[5] is None or "Tree" in str(o[5])])
print(sorted(set(o[5].split('.')[0] for o in out if o[5])))
# ---- result ----
# {"result":"Code executed successfully: [('SN', 42, 24, 42, 25, None)]\n['SM_VK_Bush_Hydrangea_inst', 'SM_VK_Bush_Round_inst', 'SM_VK_Gatehouse_Block_i
# nst', 'SM_VK_TownWall_Straight_inst']\n"}

# ==============================================================================================================
# [0010] 2026-09-23 17:04:12  blender  ok
# ==============================================================================================================
import bpy
R=bpy.app.driver_namespace["_play_rev"]; E=R["edges"]
def show(cells):
    for (k,h) in E.items():
        i,j,i2,j2=k
        if (i,j) in cells or (i2,j2) in cells: print(k,h)
show({(41,25),(43,25),(41,24),(43,24)})
print("---bank")
show({(56,10),(57,10),(56,11),(57,11),(55,10),(55,11),(58,9),(58,8)})
print("---north bank 17-18")
show({(17,16),(18,16),(17,17),(18,17)})
# ---- result ----
# {"result":"Code executed successfully: (40, 24, 41, 24) SM_VK_Gatehouse_Block_inst\n(41, 24, 42, 24) SM_VK_Gatehouse_Block_inst\n(41, 24, 41, 25) SM_V
# K_Gatehouse_Block_inst\n(42, 24, 43, 24) SM_VK_Gatehouse_Block_inst\n(43, 24, 44, 24) SM_VK_TownWall_Straight_inst.039\n(43, 24, 43, 25) SM_VK_Gatehou
# se_Block_inst\n(40, 25, 41, 25) SM_VK_Gatehouse_Block_inst\n(41, 25, 42, 25) SM_VK_Gatehouse_Block_inst\n(41, 25, 41, 26) SM_VK_Gatehouse_Block_inst\n
# (42, 25, 43, 25) SM_VK_Gatehouse_Block_inst\n(43, 25, 44, 25) SM_VK_Gatehouse_Block_inst\n(43, 25, 43, 26) SM_VK_Wall_Stone_inst.206\n---bank\n(58, 7,
#  58, 8) SM_VK_Tree_Willow_inst.001\n(58, 8, 59, 8) None\n(58, 8, 58, 9) None\n(58, 9, 59, 9) SM_VK_Tree_Willow_inst.007\n(58, 9, 58, 10) SM_VK_Tree_Wi
# llow_inst.001\n(54, 10, 55, 10) None\n(55, 10, 56, 10) SM_VK_Tree_Willow_inst.006\n(55, 10, 55, 11) None\n(56, 10, 57, 10) SM_VK_Tree_Willow_inst.011\

# ==============================================================================================================
# [0011] 2026-09-23 17:04:48  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; S1=R["S1"]; S2=R["S2"]; L=R["L"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
c=bpy.data.collections["VK_ValleyTown"]
doors=[o for o in c.all_objects if "Door" in o.name]
print(len(doors))
PASS=("Door","LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","Rug","Grass","Porch","Stair","Bridge","Ramp","Puddle","Path","Moss","Leaves","Decal")
def firsthit(o_,d,dist):
    o_=o_.copy()
    for _ in range(10):
        r=sc.ray_cast(dg,o_,d,distance=dist)
        if not r[0]: return None,None
        n=r[4].name
        if any(p in n for p in PASS): 
            dist-= (r[1]-o_).length+0.02; o_=r[1]+d*0.02
            if dist<=0: return None,None
            continue
        return n,(r[1]-o_).length
    return None,None
res=[]
for o in doors:
    m=o.matrix_world; p=m.translation
    ydir=(m.to_3x3()@Vector((0,1,0))); ydir.z=0; ydir.normalize()
    sides=[]
    for s in (1,-1):
        q=p+ydir*s*1.5
        ci,cj=int((q.x-1500)//3),int(q.y//3)
        reach=(ci,cj) in S1
        zc=o.matrix_world.translation.z+0.9
        # obstacle in front (from door plane outward 2.5 m)
        # door center is at module center; find local x-center: use bound box center
        bc=m@(sum((Vector(v) for v in o.bound_box),Vector())/8)
        start=Vector((bc.x,bc.y,p.z+0.9))+ydir*s*0.35
        h,dd=firsthit(start,ydir*s,2.2)
        sides.append((s,(ci,cj),reach,h,round(dd,2) if dd else None))
    res.append((o.name,tuple(round(v,1) for v in p),round(math.degrees(o.rotation_euler.z)),sides))
bad=[]
for r_ in res:
    s1,s2=r_[3]
    if not (s1[2] or s2[2]): bad.append(("UNREACH",)+r_)
    else:
        # the reachable side(s) whose front is obstructed
        outs=[s for s in (s1,s2) if s[2]]
        if all(s[3] for s in outs): bad.append(("BLOCKED",)+r_)
for b in bad: print(b)
# ---- result ----
# {"result":"Code executed successfully: 52\n('UNREACH', 'SM_VK_Wall_Shed_Door_inst', (1693.5, 21.0, 0.0), 180, [(1, (64, 6), False, None, None), (-1, (
# 64, 7), False, None, None)])\n"}

# ==============================================================================================================
# [0012] 2026-09-23 17:05:14  blender  ok
# ==============================================================================================================
import bpy, collections, math
c=bpy.data.collections["VK_ValleyTown"]
cnt=collections.Counter(o.name.split(".")[0] for o in c.all_objects if "Door" in o.name)
print(cnt)
# list names of other candidate entry objects
cand=collections.Counter(o.name.split(".")[0] for o in c.all_objects if any(k in o.name for k in ("Gate","Portal","Entr","Arch","Mine","Stair","Ladder","Hatch")))
print(cand)
for o in c.all_objects:
    if any(k in o.name for k in ("Stair","Ladder","Portal","Mine")):
        print(o.name, tuple(round(v,1) for v in o.location), round(math.degrees(o.rotation_euler.z)))
# ---- result ----
# {"result":"Code executed successfully: Counter({'SM_VK_Wall_Stone_Door_inst': 25, 'SM_VK_Wall_Plaster_Door_inst': 11, 'SM_VK_Wall_Wattle_Door_inst': 4
# , 'SM_VK_Wall_Timber_Door_inst': 3, 'SM_VK_Wall_Shed_Door_inst': 2, 'SM_VK_Wall_Log_Door_inst': 2, 'SM_VK_Wall_StoneUp_Door_inst': 2, 'SM_VK_Wall_Shed
# _Door_Raised_inst': 1, 'SM_VK_Wall_Stone_Half_Door_inst': 1, 'SM_VK_Chapel_Wall_Door_inst': 1})\nCounter({'SM_VK_Prop_FenceGate_inst': 5, 'SM_VK_Gateh
# ouse_GateLeaf_inst': 2, 'SM_VK_Palisade_GateLeaf_inst': 2, 'SM_VK_Palisade_Ladder_inst': 2, 'SM_VK_Prop_ArcheryButt_inst': 2, 'SM_VK_Prop_Minecart_ins
# t': 2, 'SM_VK_Stair_Stone_Ext_inst': 2, 'SM_VK_Gatehouse_Block_inst': 1, 'SM_VK_Gatehouse_Portcullis_inst': 1, 'SM_VK_Quay_Stair_inst': 1, 'SM_VK_Pier
# _Stairs_inst': 1, 'SM_VK_Palisade_Gate_inst': 1, 'SM_VK_Prop_LadderLean_inst': 1, 'SM_VK_Scaffold_Ladder_inst': 1, 'SM_VK_Mine_Portal_inst': 1, 'SM_VK

# ==============================================================================================================
# [0013] 2026-09-23 17:05:43  blender  ok
# ==============================================================================================================
import bpy, math, collections
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
ws=[o for o in c.all_objects if (("Wall_" in o.name or "Corner_" in o.name) and not any(k in o.name for k in ("TownWall","LowWall","Palisade","Scaffold","Foundation","Chapel_Wall","Wall_Posts","Wall_Stone_Half","Corner_Stone_Half","Plaster_Frame","Timber_Frame"))) or "Chapel_Wall" in o.name]
pts=[(o, Vector((o.matrix_world.translation.x,o.matrix_world.translation.y))) for o in ws]
# union-find by distance < 3.2 and z similar
par=list(range(len(pts)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for a in range(len(pts)):
    for b in range(a+1,len(pts)):
        if (pts[a][1]-pts[b][1]).length<3.1: par[f(a)]=f(b)
groups=collections.defaultdict(list)
for k,(o,p) in enumerate(pts): groups[f(k)].append(o)
out=[]
for g,objs in groups.items():
    hasdoor=any("Door" in o.name for o in objs)
    xs=[o.matrix_world.translation.x for o in objs]; ys=[o.matrix_world.translation.y for o in objs]
    nd=sum(1 for o in objs if "Door" in o.name)
    out.append((round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),len(objs),nd))
out.sort(key=lambda t:(t[2],t[0]))
for t in out: print(t)
# ---- result ----
# {"result":"Code executed successfully: (1680.0, 1686.2, -0.0, 12.0, 34, 1)\n(1509.0, 1524.0, 3.0, 9.0, 18, 1)\n(1536.0, 1542.0, 3.0, 9.0, 12, 1)\n(155
# 1.0, 1557.0, 3.0, 9.0, 12, 1)\n(1566.0, 1572.0, 15.0, 21.0, 12, 1)\n(1689.0, 1695.0, 18.0, 21.0, 10, 1)\n(1536.0, 1539.0, 22.5, 22.5, 2, 0)\n(1548.0, 
# 1557.0, 24.0, 24.0, 5, 0)\n(1578.0, 1584.0, 48.0, 57.0, 28, 2)\n(1656.0, 1659.0, 48.0, 51.0, 8, 1)\n(1611.0, 1617.0, 60.0, 66.0, 12, 1)\n(1504.5, 1513
# .5, 61.0, 67.0, 14, 1)\n(1662.0, 1671.0, 63.0, 69.0, 18, 1)\n(1627.5, 1627.5, 72.0, 72.0, 1, 0)\n(1623.0, 1686.0, 73.5, 96.0, 229, 11)\n(1503.0, 1509.
# 0, 75.0, 81.0, 12, 1)\n(1533.0, 1536.0, 75.0, 78.0, 8, 1)\n(1515.0, 1521.0, 78.0, 84.0, 12, 1)\n(1575.0, 1584.0, 78.0, 84.0, 42, 2)\n(1593.0, 1599.0, 
# 78.0, 87.0, 42, 2)\n(1608.0, 1617.0, 78.0, 87.0, 55, 3)\n(1611.0, 1611.0, 81.0, 81.0, 1, 0)\n(1542.0, 1542.0, 93.0, 93.0, 1, 0)\n(1548.0, 1548.0, 93.0

# ==============================================================================================================
# [0014] 2026-09-23 17:06:22  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; S1=R["S1"]; L=R["L"]; water=R["water"]; Z=R["Z"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
c=bpy.data.collections["VK_ValleyTown"]
PASS=("LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","Rug","Grass","Puddle","Moss","Leaves","Decal")
def hits(o_,d,dist):
    o_=o_.copy(); out=[]; tot=0
    for _ in range(10):
        r=sc.ray_cast(dg,o_,d,distance=dist-tot)
        if not r[0]: break
        tot+=(r[1]-o_).length; n=r[4].name
        if not any(p in n for p in PASS): out.append((n.replace("_inst",""),round(tot,2)))
        o_=r[1]+d*0.02; tot+=0.02
        if len(out)>=2: break
    return out
rows=[]
for o in c.all_objects:
    if "Door" not in o.name: continue
    m=o.matrix_world; R3=m.to_3x3().normalized()
    outd=R3@Vector((0,-1,0)); outd.z=0; outd.normalize()
    bc=m@(sum((Vector(v) for v in o.bound_box),Vector())/8)
    zb=m.translation.z
    start=Vector((bc.x,bc.y,zb+1.0))
    h=hits(start,outd,3.0)
    q=Vector((bc.x,bc.y,0))+outd*1.6
    ci,cj=int((q.x-1500)//3),int(q.y//3)
    lv=L[cj,ci] if 0<=ci<72 and 0<=cj<56 else -1
    # ground height in front via terrain+objects raycast down
    r=sc.ray_cast(dg,Vector((q.x,q.y,zb+6)),Vector((0,0,-1)))
    gz=round(r[1].z,2) if r[0] else None; gn=r[4].name if r[0] else None
    rows.append((o.name.replace("_inst",""),round(bc.x,1),round(bc.y,1),round(zb,2),(ci,cj),lv,(ci,cj) in S1,gz,gn,h))
for r_ in rows:
    flag=""
    if r_[3] is not None and r_[7] is not None and abs(r_[7]-r_[3])>0.6: flag+=" STEP"
    if r_[9] and r_[9][0][1]<1.6: flag+=" OBST"
    if not r_[6]: flag+=" NOREACH"
    print(flag, r_)
# ---- result ----
# {"result":"Code executed successfully: STEP OBST ('SM_VK_Wall_Timber_Door', 1622.8, 76.5, 9.2, (40, 25), 2, True, 6.59, 'SM_VK_Tree_Blossom_inst.005',
#  [('SM_VK_Wall_Timber_Door', 0.02), ('SM_VK_Wall_Timber_Door', 0.13)])\n STEP OBST ('SM_VK_Wall_Timber_Door.001', 1632.2, 76.5, 9.2, (44, 25), 2, True
# , 3.0, 'VKV_Chunk_2_1', [('SM_VK_Wall_Timber_Door.001', 0.02), ('SM_VK_Wall_Timber_Door.001', 0.13)])\n ('SM_VK_Wall_Stone_Door.033', 1577.7, 52.5, 0.
# 0, (25, 17), 0, True, 0.0, 'VKV_Chunk_1_1', [])\n ('SM_VK_Wall_Stone_Door.034', 1584.3, 55.5, 0.0, (28, 18), 0, True, 0.0, 'VKV_Chunk_1_1', [])\n ('SM
# _VK_Wall_Stone_Door.035', 1657.5, 51.3, 0.0, (52, 17), 0, True, 0.0, 'VKV_Chunk_3_1', [('SM_VK_Prop_FishRack', 2.26), ('SM_VK_Prop_FishRack', 2.86)])\
# n OBST NOREACH ('SM_VK_Wall_Shed_Door', 1693.5, 21.3, 0.0, (64, 7), 0, False, 0.0, 'VKV_Chunk_4_0', [('SM_VK_Wall_Shed_Door', 0.04)])\n STEP ('SM_VK_W

# ==============================================================================================================
# [0015] 2026-09-23 17:07:46  blender  ok
# ==============================================================================================================
import bpy
R=bpy.app.driver_namespace["_play_rev"]; E=R["edges"]
for k in [(42,29,43,29),(43,29,44,29),(42,28,43,28),(43,28,44,28),(43,29,43,30),(43,28,43,29),(44,29,44,30),(44,28,44,29),(42,30,43,30),(43,30,44,30),(43,30,43,31),(42,31,43,31)]:
    print(k,E.get(k,"n/a"))
# cells around east street 29 which are free
import numpy as np
S1=R["S1"]
for j in range(31,26,-1):
    print(j," ".join(("R" if (i,j) in S1 else "#") for i in range(40,63)))
# ---- result ----
# {"result":"Code executed successfully: (42, 29, 43, 29) None\n(43, 29, 44, 29) None\n(42, 28, 43, 28) None\n(43, 28, 44, 28) None\n(43, 29, 43, 30) No
# ne\n(43, 28, 43, 29) SM_VK_Wall_Stone_inst.203\n(44, 29, 44, 30) None\n(44, 28, 44, 29) SM_VK_Wall_Stone_inst.204\n(42, 30, 43, 30) None\n(43, 30, 44,
#  30) None\n(43, 30, 43, 31) None\n(42, 31, 43, 31) None\n31 R R R R R R R R R R R R R R R R R R R R R R #\n30 R R R R R R R R R R R R R R R R R R R R 
# R R R\n29 R R R R R R R R R R R R R R R R R R R R R R R\n28 R R R R R R R R R R R R R R R R R R R R R R R\n27 R R R R R R R R R R R R R R R R R R R R 
# R R R\n"}

# ==============================================================================================================
# [0016] 2026-09-23 17:08:18  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_02_gate_colony",(1626,38,42),(1626,80,3),lens=30,res=(1600,900),outdir=OUT))
print(shot("play_03_gate_eye",(1626,63,5.2),(1626.5,80,4.8),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_02_gate_colony.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play
# _03_gate_eye.png\n"}

# ==============================================================================================================
# [0017] 2026-09-23 17:08:53  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
for n in ("SM_VK_Gatehouse_Portcullis_inst","SM_VK_Gatehouse_Block_inst","SM_VK_Gatehouse_GateLeaf_inst","SM_VK_Gatehouse_GateLeaf_inst.001"):
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n,[round(min(v[k] for v in bb),2) for k in range(3)],[round(max(v[k] for v in bb),2) for k in range(3)])
# scan passage free x-range at several y and z=3.9
for y in (70.5,73,75,77,79.5):
    free=[]
    x=1618.0
    while x<1637:
        r=sc.ray_cast(dg,Vector((x,y,3.9+0.0)),Vector((0,0,1)),distance=0.01)  # dummy
        # vertical ray from above down to 3.9: first hit z
        r=sc.ray_cast(dg,Vector((x,y,3.3)),Vector((0,0,1)),distance=2.5)
        free.append("." if not r[0] else ("P" if "Portcullis" in r[4].name else "#"))
        x+=0.5
    print(y,"".join(free))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Gatehouse_Portcullis_inst [1625.79, 72.5, 5.16] [1629.34, 72.71, 9.9]\nSM_VK_Gatehouse_Block_inst [1622.1
# 9, 69.68, 1.5] [1632.83, 78.25, 12.0]\nSM_VK_Gatehouse_GateLeaf_inst [1625.68, 73.69, 3.02] [1626.43, 75.38, 7.36]\nSM_VK_Gatehouse_GateLeaf_inst.001 
# [1628.57, 73.69, 3.02] [1629.32, 75.38, 7.36]\n70.5 ..........##...##.....##...##.........\n73 .#######..#.....#.....#.....#####.....\n75 ########....
# ....#.....#...............\n77 ..########............................\n79.5 .....####.........................##..\n"}

# ==============================================================================================================
# [0018] 2026-09-23 17:09:12  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
def allhits(o,d,dist):
    out=[];tot=0;o=o.copy()
    while tot<dist:
        r=sc.ray_cast(dg,o,d,distance=dist-tot)
        if not r[0]: break
        tot+=(r[1]-o).length; out.append((round(r[1].x,2),round(r[1].y,2),r[4].name.replace("_inst","")))
        o=r[1]+d*0.01; tot+=0.01
    return out
for y in (69.5,71,72.6,74,75.5,77,78.5):
    print(y,[h for h in allhits(Vector((1619,y,4.0)),Vector((1,0,0)),17)])
# ---- result ----
# {"result":"Code executed successfully: 69.5 []\n71 [(1622.91, 71.0, 'SM_VK_Gatehouse_Block'), (1626.09, 71.0, 'SM_VK_Gatehouse_Block'), (1628.91, 71.0
# , 'SM_VK_Gatehouse_Block'), (1632.09, 71.0, 'SM_VK_Gatehouse_Block')]\n72.6 [(1622.71, 72.6, 'SM_VK_Gatehouse_Block'), (1623.0, 72.6, 'SM_VK_Gatehouse
# _Block'), (1625.82, 72.6, 'SM_VK_Gatehouse_Block'), (1625.9, 72.6, 'SM_VK_Gatehouse_Block'), (1625.94, 72.6, 'SM_VK_Gatehouse_Block'), (1626.29, 72.6,
#  'SM_VK_Gatehouse_Block'), (1628.71, 72.6, 'SM_VK_Gatehouse_Block'), (1629.06, 72.6, 'SM_VK_Gatehouse_Block'), (1629.1, 72.6, 'SM_VK_Gatehouse_Block')
# , (1629.18, 72.6, 'SM_VK_Gatehouse_Block'), (1632.0, 72.6, 'SM_VK_Gatehouse_Block'), (1632.29, 72.6, 'SM_VK_Gatehouse_Block'), (1632.48, 72.6, 'SM_VK_
# Bush_Round.037'), (1632.78, 72.6, 'SM_VK_Bush_Round.037'), (1632.96, 72.6, 'SM_VK_Bush_Round.037'), (1633.04, 72.6, 'SM_VK_Bush_Round.037'), (1633.08,

# ==============================================================================================================
# [0019] 2026-09-23 17:09:46  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_04_gate_inside",(1627,98,16),(1627,76,5),lens=28,res=(1600,900),outdir=OUT))
print(shot("play_05_sw_quarter_wallfronts",(1597,108,34),(1597,78,3),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_04_gate_inside.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\s
# cratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play
# _05_sw_quarter_wallfronts.png\n"}

# ==============================================================================================================
# [0020] 2026-09-23 17:11:02  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def bb(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)]
IGN=("LipGrass","Weeds","Plant_","Deco_","Mushrooms","Pebbles","Rock_Small","TownWall_Straight","TownWall_Corner","Fern","Grass","Wildflowers")
objs=[o for o in c.all_objects if o.type=="MESH" and not any(k in o.name for k in IGN)]
B={o.name:bb(o) for o in objs}
towers=[o for o in objs if "Tower_Round" in o.name or "Gatehouse_Block" in o.name]
for t in towers:
    (a0,a1)=B[t.name]
    ov=[]
    for o in objs:
        if o is t or "Gatehouse" in o.name or "Tower_Round" in o.name: continue
        (b0,b1)=B[o.name]
        if all(a0[k]<b1[k]-0.05 and b0[k]<a1[k]-0.05 for k in range(3)):
            ov.append(o.name.replace("_inst",""))
    print(t.name, [round(v,1) for v in a0],[round(v,1) for v in a1], ov[:12])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Tower_Round_inst [1583.4, 71.4, 1.5] [1590.6, 78.6, 15.5] ['SM_VK_Corner_Stone.147', 'SM_VK_Corn
# er_StoneUp.002', 'SM_VK_Corner_StoneUp.006', 'SM_VK_Wall_Stone_Shop.001', 'SM_VK_Roof_Pent', 'SM_VK_Wall_Stone_Window.147', 'SM_VK_Wall_StoneUp_Twin.0
# 01', 'SM_VK_Wall_StoneUp.001', 'SM_VK_Wall_StoneUp_Window.005', 'SM_VK_Wall_StoneUp.004', 'SM_VK_Roof_Gable_Stepped.001']\nSM_VK_TownWall_Tower_Round_
# inst.001 [1583.4, 134.4, 1.5] [1590.6, 141.6, 15.5] ['SM_VK_Tree_Oak_A.043', 'SM_VK_Tree_Pine_B.163', 'SM_VK_Tree_Pine_A.155', 'SM_VK_Tree_Pine_A.156'
# , 'SM_VK_Tree_Pine_B.164', 'SM_VK_Tree_Pine_A.157', 'SM_VK_Tree_Pine_A.158', 'SM_VK_Tree_Pine_A.159', 'SM_VK_Tree_Pine_B.165', 'SM_VK_Tree_Pine_A.175'
# , 'SM_VK_Tree_Pine_A.176']\nSM_VK_TownWall_Tower_Round_inst.002 [1604.4, 71.4, 1.5] [1611.6, 78.6, 15.5] ['SM_VK_Wall_Stone_Shop.002', 'SM_VK_Prop_Sho

# ==============================================================================================================
# [0021] 2026-09-23 17:11:41  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
towers=[o for o in c.all_objects if "Tower_Round" in o.name]
# tower radius at base: measure max horizontal radius of tower mesh verts below z+4
t=towers[0]; ctr=t.matrix_world.translation
rs=[ (Vector((v.co.x,v.co.y))).length for v in t.data.vertices if v.co.z<3]
print("tower origin",tuple(round(x,2) for x in ctr),"base radius max",round(max(rs),2), "median",round(sorted(rs)[len(rs)//2],2))
IGN=("LipGrass","Weeds","Plant_","Deco_","Mushrooms","Pebbles","Rock_Small","TownWall","Fern","Grass","Wildflowers","Tree_","Bush")
for t in towers:
    ctr=t.matrix_world.translation
    hits={}
    for o in c.all_objects:
        if o.type!="MESH" or any(k in o.name for k in IGN) or o is t: continue
        if (o.matrix_world.translation.xy-ctr.xy).length>12: continue
        mw=o.matrix_world; n=0; dmin=9
        for v in o.data.vertices:
            w=mw@v.co
            d=(w.xy-ctr.xy).length
            if w.z<ctr.z+10 and d<3.0: n+=1; dmin=min(dmin,d)
        if n: hits[o.name.replace("_inst","")]=(n,round(dmin,2))
    if hits: print(t.name.replace("_inst",""),tuple(round(x,1) for x in ctr),hits)
# ---- result ----
# {"result":"Code executed successfully: tower origin (1587.0, 75.0, 3.0) base radius max 3.64 median 3.26\nSM_VK_TownWall_Tower_Round.002 (1608.0, 75.0
# , 3.0) {'SM_VK_Wall_Stone_Shop.002': (468, 2.07), 'SM_VK_Prop_ShopGoods_Fish': (243, 2.33), 'SM_VK_Wall_Timber_Window.268': (309, 2.39), 'SM_VK_Wall_T
# imber_Window.269': (309, 2.39), 'SM_VK_Wall_Stone_Shop.003': (8, 2.99), 'SM_VK_Wall_Timber_Window.273': (11, 2.98), 'SM_VK_Wall_Timber_Window.274': (1
# 1, 2.98), 'SM_VK_Corner_Stone.149': (200, 2.43), 'SM_VK_Corner_Timber.166': (128, 2.43), 'SM_VK_Corner_Timber.171': (128, 2.43), 'SM_VK_Roof_LCorner.0
# 08': (686, 1.56), 'SM_VK_Turret_Corbel.001': (236, 1.34), 'SM_VK_Turret_Seg': (575, 1.33), 'SM_VK_Turret_Seg.001': (575, 1.33), 'SM_VK_Turret_Seg.002'
# : (300, 1.33), 'SM_VK_Prop_LampPost.027': (312, 1.1)}\nSM_VK_TownWall_Tower_Round.004 (1650.0, 75.0, 3.0) {'SM_VK_Wall_Stone_Window.173': (339, 2.24),

# ==============================================================================================================
# [0022] 2026-09-23 17:12:33  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_06_tower_cornerhouse",(1620,95,12),(1608,77,6),lens=28,res=(1600,900),outdir=OUT))
print(shot("play_07_terrace_towers_outside",(1661,50,20),(1661,77,8),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_06_tower_cornerhouse.png\nC:\\Users\\danie\\AppData\\Roaming\\Cla
# ude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play
# \\play_07_terrace_towers_outside.png\n"}

# ==============================================================================================================
# [0023] 2026-09-23 17:13:16  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_08_southwall_top_west",(1598,82,48),(1598,82.01,0),lens=30,res=(1600,900),outdir=OUT))
print(shot("play_09_southwall_top_east",(1660,82,48),(1660,82.01,0),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_08_southwall_top_west.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\pla
# y\\play_09_southwall_top_east.png\n"}

# ==============================================================================================================
# [0024] 2026-09-23 17:14:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_10_footbridge_westroad",(1536,8,34),(1535,48,0),lens=28,res=(1600,900),outdir=OUT))
print(shot("play_11_lake_shore_access",(1655,4,26),(1678,26,0),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_10_footbridge_westroad.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\pl
# ay\\play_11_lake_shore_access.png\n"}

# ==============================================================================================================
# [0025] 2026-09-23 17:14:43  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for n in ("SM_VK_Wall_Stone_Door_inst.036","SM_VK_Prop_WeaponRack_inst.007"):
    o=bpy.data.objects[n]; pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n,[round(min(p[k] for p in pts),2) for k in range(3)],[round(max(p[k] for p in pts),2) for k in range(3)])
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_12_barracks_door",(1695,9,5.5),(1686,4.5,2.3),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Door_inst.036 [1685.72, 2.98, 1.4] [1686.84, 6.02, 4.63]\nSM_VK_Prop_WeaponRack_inst.007 [1686
# .33, 3.74, 1.5] [1686.97, 5.26, 3.58]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_12_barracks_door.png\n"}

# ==============================================================================================================
# [0026] 2026-09-23 17:15:17  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_13_east_street_row29",(1690,66,16),(1680,90,4),lens=28,res=(1600,900),outdir=OUT))
print(shot("play_14_ne_corner_tower",(1662,112,26),(1670,134,6),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_13_east_street_row29.png\nC:\\Users\\danie\\AppData\\Roaming\\Cla
# ude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play
# \\play_14_ne_corner_tower.png\n"}

# ==============================================================================================================
# [0027] 2026-09-23 17:16:04  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
def bb(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)]
# find building pieces whose bbox crosses the wall lines x=1569/1689 or y=75/138 (inner side intrusions) at z<12
walls=[]
for o in c.all_objects:
    if o.type!="MESH" or any(k in o.name for k in ("TownWall","Gatehouse","Tree","Bush","Grass","Weeds","Fern","Rock","Plant","Deco","Mushroom","Pebbles")): continue
    a,b=bb(o)
    if a[2]>14: continue
    hit=[]
    if a[0]<1689.9 and b[0]>1688.1 and 75<a[1]<138: hit.append("E")
    if a[0]<1569.9 and b[0]>1568.1 and 75<a[1]<138: hit.append("W")
    if a[1]<75.9 and b[1]>74.1 and 1569<a[0]<1689 and not (1620<a[0]<1635): hit.append("S")
    if a[1]<138.9 and b[1]>137.1 and 1569<a[0]<1689: hit.append("N")
    if hit: walls.append((o.name.replace("_inst",""),hit,[round(v,2) for v in a],[round(v,2) for v in b]))
for w in walls: print(w)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Prop_LampPost.027', ['S'], [1606.08, 75.35, 3.0], [1607.15, 76.42, 5.9])\n"}

# ==============================================================================================================
# [0028] 2026-09-23 17:16:52  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
wall=bpy.data.objects["SM_VK_TownWall_Straight_inst"]
pts=[wall.matrix_world@Vector(v) for v in wall.bound_box]
print("wall piece bbox",[round(min(p[k] for p in pts),2) for k in range(3)],[round(max(p[k] for p in pts),2) for k in range(3)], tuple(wall.location), wall.rotation_euler.z)
for o in c.all_objects:
    if o.type!="MESH" or "Roof" not in o.name: continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    a=[min(p[k] for p in pts) for k in range(3)]; b=[max(p[k] for p in pts) for k in range(3)]
    if b[0]>1687.0 and 75<b[1] and a[1]<138: print("E",o.name,[round(v,2) for v in a],[round(v,2) for v in b])
    if a[0]<1571.0 and 75<b[1] and a[1]<138: print("W",o.name,[round(v,2) for v in a],[round(v,2) for v in b])
    if a[1]<77.0 and 1569<b[0] and a[0]<1689: print("S",o.name,[round(v,2) for v in a],[round(v,2) for v in b])
    if b[1]>136.0 and 1569<b[0] and a[0]<1689 and a[2]<20: print("N",o.name,[round(v,2) for v in a],[round(v,2) for v in b])
# ---- result ----
# {"result":"Code executed successfully: wall piece bbox [1568.55, 73.36, 1.5] [1572.0, 76.18, 10.95] (1570.5, 75.0, 3.0) 0.0\nS SM_VK_Roof_Hip_inst.010
#  [1621.55, 70.55, 11.33] [1626.21, 79.45, 17.23]\nS SM_VK_Roof_Mid_inst.028 [1625.97, 70.55, 11.42] [1629.03, 79.45, 16.42]\nS SM_VK_Roof_Hip_inst.011
#  [1628.79, 70.55, 11.33] [1633.45, 79.45, 17.23]\nS SM_VK_Roof_Cone_R2_inst [1622.3, 69.8, 11.84] [1626.7, 74.2, 17.21]\nS SM_VK_Roof_Cone_R2_inst.001
#  [1628.3, 69.8, 11.84] [1632.7, 74.2, 17.21]\nS SM_VK_Roof_Gable_inst.068 [1576.48, 53.97, 5.1] [1585.52, 58.2, 10.99]\nS SM_VK_Roof_Mid_inst.033 [157
# 6.55, 50.97, 5.22] [1585.45, 54.03, 10.22]\nS SM_VK_Roof_Gable_inst.077 [1576.48, 46.8, 5.1] [1585.52, 51.03, 10.99]\nS SM_VK_RoofS_Gable_inst [1640.9
# 7, 46.93, 2.52] [1644.85, 52.07, 6.27]\nS SM_VK_RoofS_Gable_inst.001 [1637.15, 46.93, 2.52] [1641.03, 52.07, 6.27]\nS SM_VK_RoofS_Single_inst [1655.15

# ==============================================================================================================
# [0029] 2026-09-23 17:17:28  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_15_tower_door_west_free",(1582,99,5.5),(1570,96,5),lens=30,res=(1600,900),outdir=OUT))
print(shot("play_16_tower_1608_door_blocked",(1604,86,5.2),(1608,76,5.2),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_15_tower_door_west_free.png\nC:\\Users\\danie\\AppData\\Roaming\\
# Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\p
# lay\\play_16_tower_1608_door_blocked.png\n"}

# ==============================================================================================================
# [0030] 2026-09-23 17:18:21  blender  ok
# ==============================================================================================================
import bpy, collections, math
from mathutils import Vector
t=bpy.data.objects["SM_VK_TownWall_Tower_Round_inst.002"]
me=t.data
print([m.name for m in me.materials])
cnt=collections.defaultdict(list)
for p in me.polygons:
    cnt[p.material_index].append(p.center.copy())
for k,v in cnt.items():
    zs=[c.z for c in v]; 
    print(me.materials[k].name if me.materials[k] else None,len(v),round(min(zs),2),round(max(zs),2), round(min(c.y for c in v),2), round(max(c.y for c in v),2),round(min(c.x for c in v),2), round(max(c.x for c in v),2))
print(tuple(t.location), math.degrees(t.rotation_euler.z))
# ---- result ----
# {"result":"Code executed successfully: ['M_VK_Stone', 'M_VK_Plaster', 'M_VK_Wood', 'M_VK_Roof_Slate', 'M_VK_Window', 'M_VK_Iron', 'M_VK_FlowerPink', '
# M_VK_FlowerYellow', 'M_VK_Leaf', 'M_VK_Glow', 'M_VK_Shutter_Teal', 'M_VK_Cloth_Red', 'M_VK_Cloth_Cream', 'M_VK_Apple', 'M_VK_Pumpkin', 'M_VK_Bread', '
# M_VK_Hay', 'M_VK_Paper', 'M_VK_Water', 'M_VK_Bronze', 'M_VK_Stained', 'M_VK_Steel', 'M_VK_Thatch', 'M_VK_Planks', 'M_VK_Ashlar', 'M_VK_Burlap', 'M_VK_
# Soil', 'M_VK_Void', 'M_VK_Rock', 'M_VK_Clay', 'M_VK_Clock', 'M_VK_Foliage', 'M_VK_Crops', 'M_VK_BarkOak', 'M_VK_BarkBirch', 'M_VK_BarkPine', 'M_VK_Lea
# ves', 'M_VK_Moss', 'M_VK_RockMossy', 'M_VK_BarkMossy', 'M_VK_EndGrain', 'M_VK_MushRed', 'M_VK_MushBrown', 'M_VK_MushStem', 'M_VK_MushGlow', 'M_VK_Ston
# eBlock', 'M_VK_FieldStone', 'M_VK_Wattle', 'M_VK_Hide', 'M_VK_Pigskin', 'M_VK_Coal', 'M_VK_Net']\nM_VK_Stone 306 -0.75 8.98 -3.33 3.33 -3.33 3.33\nM_V

# ==============================================================================================================
# [0031] 2026-09-23 17:19:05  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
c=bpy.data.collections["VK_ValleyTown"]
PASS=("LipGrass","Weeds","Plant_","Deco_","Mushrooms","Pebbles","Flower","Grass","Wildflowers","Fern")
for t in sorted([o for o in c.all_objects if "Tower_Round" in o.name],key=lambda o:o.name):
    m=t.matrix_world; d=(m.to_3x3().normalized()@Vector((0,1,0))); d.z=0; d.normalize()
    door=m@Vector((0,3.35,0.9))
    res=[]
    for off in (-0.5,0,0.5):
        lat=Vector((-d.y,d.x,0))*off
        o=door+lat; left=3.0; hit=None
        for _ in range(8):
            r=sc.ray_cast(dg,o,d,distance=left)
            if not r[0]: break
            n=r[4].name
            if any(p in n for p in PASS) or n==t.name: left-=(r[1]-o).length+0.02; o=r[1]+d*0.02; continue
            hit=(n.replace("_inst",""),round((r[1]-door-lat).length,2)); break
        res.append(hit)
    print(t.name.replace("_inst",""),tuple(round(v,1) for v in door),res)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Tower_Round (1587.0, 78.3, 3.9) [None, None, None]\nSM_VK_TownWall_Tower_Round.001 (1587.0, 134.
# 6, 3.9) [('SM_VK_Wall_Stone.170', 2.39), ('SM_VK_Wall_Stone.171', 2.39), ('SM_VK_Wall_Stone.171', 2.4)]\nSM_VK_TownWall_Tower_Round.002 (1608.0, 78.3,
#  3.9) [None, ('SM_VK_Wall_Stone_Shop.003', 0.04), ('SM_VK_Wall_Stone_Shop.003', 0.04)]\nSM_VK_TownWall_Tower_Round.003 (1608.0, 134.6, 3.9) [None, ('S
# M_VK_Wall_Plaster.097', 2.27), ('SM_VK_Wall_Plaster.097', 2.24)]\nSM_VK_TownWall_Tower_Round.004 (1650.0, 78.3, 3.9) [None, None, None]\nSM_VK_TownWal
# l_Tower_Round.005 (1650.0, 134.6, 3.9) [None, None, None]\nSM_VK_TownWall_Tower_Round.006 (1671.0, 78.3, 3.9) [None, None, None]\nSM_VK_TownWall_Tower
# _Round.007 (1671.0, 134.6, 3.9) [None, None, None]\nSM_VK_TownWall_Tower_Round.008 (1572.3, 96.0, 3.9) [None, ('SM_VK_Corner_Stone.154', 2.25), ('SM_V

# ==============================================================================================================
# [0032] 2026-09-23 17:19:41  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; E=R["edges"]; L=R["L"]; water=R["water"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
PASS=("LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","VKV_Water","Rug","Grass","Porch","Stair","Bridge","Ramp","Puddle","Path","Moss","Leaves","Decal")
def cast(a,b):
    d=(b-a); left=d.length; d.normalize(); o=a.copy()
    for _ in range(12):
        r=sc.ray_cast(dg,o,d,distance=left)
        if not r[0]: return None
        n=r[4].name
        if any(p in n for p in PASS):
            left-=(r[1]-o).length+0.02; o=r[1]+d*0.02
            if left<=0: return None
            continue
        return n
    return None
# recompute only edges that were open and might cross a door
E2={}
for k,h in E.items():
    if h is not None: E2[k]=h; continue
    i,j,i2,j2=k; z=L[j,i]*1.5+0.9
    a=Vector((1500+3*i+1.5,3*j+1.5,z)); b=Vector((1500+3*i2+1.5,3*j2+1.5,z))
    d=(b-a).normalized(); lat=Vector((-d.y,d.x,0)); res=None; first=None
    for off in (0.0,-0.9,0.9):
        hh=cast(a+lat*off,b+lat*off)
        if hh is None: res=None; break
        if first is None: first=hh
        res=first
    E2[k]=res
R["edges_nodoor"]=E2
print(sum(1 for v in E2.values() if v and "Door" in v))
# ---- result ----
# {"result":"Code executed successfully: 43\n"}

# ==============================================================================================================
# [0033] 2026-09-23 17:20:29  blender  ok
# ==============================================================================================================
import bpy, collections
R=bpy.app.driver_namespace["_play_rev"]; E2=R["edges_nodoor"]; L=R["L"]; water=R["water"]
adj=collections.defaultdict(list)
def isTree(n): return n and ("Tree_" in n or "Bush" in n or "Rock_Boulder" in n)
def add(a,b,tag): adj[a].append((b,tag)); adj[b].append((a,tag))
for (i,j,i2,j2),h in E2.items():
    if h is None: add((i,j),(i2,j2),"ok")
    elif isTree(h): add((i,j),(i2,j2),"tree")
ramps=[((41,10),(41,9)),((42,10),(42,9)),((41,17),(41,18)),((42,17),(42,18)),((41,23),(41,24)),((42,23),(42,24)),((9,23),(9,24)),((10,23),(10,24)),((8,33),(8,34))]
for a,b in ramps: add(a,b,"ramp")
for c in (41,42):
    for j in range(11,16): add((c,j),(c,j+1),"bridge")
for j in range(11,16): add((12,j),(12,j+1),"bridge")
def bfs(start,allow_tree):
    seen={start}; q=collections.deque([start])
    while q:
        c=q.popleft()
        for (n,tag) in adj[c]:
            if tag=="tree" and not allow_tree: continue
            if n not in seen: seen.add(n); q.append(n)
    return seen
O1=bfs((41,0),False); R["O1"]=O1
rows=[]
for j in range(46,23,-1):
    s=""
    for i in range(18,66):
        s+= ("." if (i,j) in O1 else ("~" if water[j,i] else "#"))
    rows.append(f"{j:2d} "+s)
print("    "+"".join(str(i%10) for i in range(18,66)))
print("\n".join(rows))
for (nm,cell) in [("T001",(29,44)),("T003",(36,44)),("T008",(24,32)),("T009",(61,32)),("T010",(24,39)),("T011",(61,39)),("T000",(29,26)),("T005",(50,44)),("T007",(57,44)),("T004",(50,26)),("T006",(57,26)),("T002",(36,26))]:
    print(nm,cell,cell in O1)
# ---- result ----
# {"result":"Code executed successfully: 890123456789012345678901234567890123456789012345\n46 ##........####################################..\n45 ##...
# .....##.....##............##.....##.....#..\n44 ##....................................##.....#..\n43 ##......#.#######.###.##..............##.....#..\
# n42 ##......#.#######.###.##.....................#..\n41 ##...........................................#..\n40 ##............................####......
# .....#..\n39 ##..##.................##.....####....###...##..\n38 ##..##....####.##......##.............###...##..\n37 ##........####.##......##..###.
# ..............#..\n36 ##.........................###...............#..\n35 ##..............##...........................#..\n34 ##..............##....
# .......................#..\n33 .......##.......##............##.............#..\n32 ....##.##.....................##............##..\n31 ....##.......

# ==============================================================================================================
# [0034] 2026-09-23 17:20:56  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; O1=R["O1"]; L=R["L"]
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if "Door" not in o.name: continue
    m=o.matrix_world; outd=(m.to_3x3().normalized()@Vector((0,-1,0))); outd.z=0; outd.normalize()
    bc=m@(sum((Vector(v) for v in o.bound_box),Vector())/8)
    q=Vector((bc.x,bc.y,0))+outd*1.6
    ci,cj=int((q.x-1500)//3),int(q.y//3)
    q2=Vector((bc.x,bc.y,0))-outd*1.6
    ci2,cj2=int((q2.x-1500)//3),int(q2.y//3)
    if (ci,cj) not in O1:
        print(o.name.replace("_inst",""),tuple(round(v,1) for v in bc),"out",(ci,cj),"in",(ci2,cj2),(ci2,cj2) in O1)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Shed_Door (1693.5, 21.3, 1.0) out (64, 7) in (64, 6) False\nSM_VK_Wall_Plaster_Door.024 (1672.5, 77.
# 7, 4.4) out (57, 25) in (57, 26) False\n"}

# ==============================================================================================================
# [0035] 2026-09-23 17:21:10  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for n in ("SM_VK_Stair_Stone_Ext_inst","SM_VK_Stair_Stone_Ext_inst.001","SM_VK_Prop_Cart_inst.014","SM_VK_Prop_Woodpile_inst.015"):
    o=bpy.data.objects[n]; pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n,[round(min(p[k] for p in pts),2) for k in range(3)],[round(max(p[k] for p in pts),2) for k in range(3)])
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_15_ext_stairs_merchant_tower",(1592,92,9),(1579,90,4),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Stair_Stone_Ext_inst [1578.8, 84.21, 2.4] [1584.25, 85.57, 7.14]\nSM_VK_Stair_Stone_Ext_inst.001 [1574.75
# , 94.43, 2.4] [1580.2, 95.79, 7.14]\nSM_VK_Prop_Cart_inst.014 [1577.77, 84.95, 3.0] [1581.24, 87.02, 4.42]\nSM_VK_Prop_Woodpile_inst.015 [1579.5, 93.7
# 5, 2.95] [1583.2, 95.05, 4.47]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41
# c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_15_ext_stairs_merchant_tower.png\n"}

# ==============================================================================================================
# [0036] 2026-09-23 17:22:12  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    p=o.matrix_world.translation
    if 1570<p.x<1590 and 83.5<p.y<90.5 and o.type=="MESH" and not any(k in o.name for k in ("Grass","Weeds","Lip")):
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        print(o.name.replace("_inst",""),[round(min(q[k] for q in pts),2) for k in range(3)],[round(max(q[k] for q in pts),2) for k in range(3)],round(math.degrees(o.rotation_euler.z)))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Corner_Stone.146 [1574.4, 83.35, 2.94] [1575.65, 84.62, 6.01] -90\nSM_VK_Corner_Stone.148 [1583.35, 83.35
# , 2.94] [1584.62, 84.6, 6.01] 180\nSM_VK_Corner_StoneUp.001 [1574.48, 83.38, 5.94] [1575.65, 84.48, 8.8] -90\nSM_VK_Corner_StoneUp.003 [1583.38, 83.35
# , 5.94] [1584.48, 84.52, 8.8] 180\nSM_VK_Corner_StoneUp.005 [1574.48, 83.38, 8.74] [1575.65, 84.48, 11.6] -90\nSM_VK_Corner_StoneUp.007 [1583.38, 83.3
# 5, 8.74] [1584.48, 84.52, 11.6] 180\nSM_VK_Wall_Stone_Window.145 [1574.98, 83.72, 2.89] [1578.02, 84.82, 6.0] 180\nSM_VK_Prop_FlowerBox_Daisy.025 [157
# 5.79, 84.29, 3.56] [1577.25, 84.83, 4.45] 180\nSM_VK_Wall_Stone.158 [1577.98, 83.72, 2.89] [1581.02, 84.53, 6.0] 180\nSM_VK_Wall_Stone.159 [1580.98, 8
# 3.72, 2.89] [1584.02, 84.53, 6.0] 180\nSM_VK_Wall_StoneUp_Window [1575.0, 83.72, 5.89] [1578.0, 84.82, 8.8] 180\nSM_VK_Wall_StoneUp_Door [1578.0, 83.7

# ==============================================================================================================
# [0037] 2026-09-23 17:22:52  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_17_merchant_yard_stair_foot",(1586,93,8.5),(1580.5,85.5,3.8),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_17_merchant_yard_stair_foot.png\n"}

# ==============================================================================================================
# [0038] 2026-09-23 17:23:43  blender  ok
# ==============================================================================================================
import bpy
R=bpy.app.driver_namespace["_play_rev"]; E=R["edges"]; L=R["L"]; water=R["water"]
import numpy as np
W,H=72,56
ground=np.zeros((H,W),int)
for j in range(0,32):
    for i in (41,42):
        if not water[j,i]: ground[j,i]=1
ground[25:32,41:43]=2; ground[31:36,36:48]=2; ground[39:42,24:41]=2; ground[36:39,39:41]=2; ground[29,44:62]=2
ground[18:24,9:11]=1; ground[24:34,9:11]=1
out=[]
for (i,j,i2,j2),h in E.items():
    if h and (ground[j,i] and ground[j2,i2]):
        out.append(((i,j),(i2,j2),h.replace("_inst","")))
for o in sorted(out): print(o)
# ---- result ----
# {"result":"Code executed successfully: ((38, 31), (38, 32), 'SM_VK_MarketStall.013')\n((38, 32), (38, 33), 'SM_VK_MarketStall.013')\n((38, 34), (38, 3
# 5), 'SM_VK_MarketStall.014')\n((41, 8), (41, 9), 'SM_VK_Tree_Willow.005')\n((41, 9), (42, 9), 'SM_VK_Tree_Willow.005')\n((41, 22), (41, 23), 'SM_VK_Ga
# tehouse_Block')\n((41, 24), (41, 25), 'SM_VK_Gatehouse_Block')\n((41, 24), (42, 24), 'SM_VK_Gatehouse_Block')\n((41, 25), (41, 26), 'SM_VK_Gatehouse_B
# lock')\n((41, 25), (42, 25), 'SM_VK_Gatehouse_Block')\n((41, 33), (42, 33), 'SM_VK_Prop_MarketCross.001')\n((44, 31), (44, 32), 'SM_VK_MarketStall.015
# ')\n((44, 32), (44, 33), 'SM_VK_MarketStall.015')\n((45, 34), (46, 34), 'SM_VK_MarketStall.016')\n"}

# ==============================================================================================================
# [0039] 2026-09-23 17:24:05  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
for n in ("SM_VK_Tree_Willow_inst.005","SM_VK_Tree_Willow_inst.006","SM_VK_Tree_Willow_inst.011","SM_VK_Tree_Willow_inst.001","SM_VK_Tree_Willow_inst.007","SM_VK_Tree_Willow_inst.015","SM_VK_Tree_Willow_inst.016"):
    o=bpy.data.objects[n]; pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    p=o.matrix_world.translation
    print(n,tuple(round(v,2) for v in p),"cell",(int((p.x-1500)//3),int(p.y//3)),[round(min(q[k] for q in pts),1) for k in range(3)],[round(max(q[k] for q in pts),1) for k in range(3)])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Willow_inst.005 (1622.3, 30.85, 0.0) cell (40, 10) [1616.7, 25.1, -0.4] [1628.0, 36.5, 4.6]\nSM_VK_T
# ree_Willow_inst.006 (1663.83, 31.58, 0.0) cell (54, 10) [1659.1, 26.9, -0.4] [1668.5, 36.2, 4.6]\nSM_VK_Tree_Willow_inst.011 (1672.43, 34.41, 0.0) cel
# l (57, 11) [1667.4, 29.5, -0.4] [1677.4, 39.3, 4.6]\nSM_VK_Tree_Willow_inst.001 (1676.61, 27.34, 0.0) cell (58, 9) [1670.5, 21.2, -0.4] [1682.7, 33.5,
#  4.6]\nSM_VK_Tree_Willow_inst.007 (1674.69, 31.78, 0.0) cell (58, 10) [1669.0, 26.1, -0.4] [1680.3, 37.4, 4.6]\nSM_VK_Tree_Willow_inst.015 (1553.01, 5
# 1.68, 0.0) cell (17, 17) [1547.7, 46.5, -0.4] [1558.2, 56.8, 4.6]\nSM_VK_Tree_Willow_inst.016 (1554.34, 52.25, 0.0) cell (18, 17) [1548.5, 46.5, -0.4]
#  [1560.1, 58.0, 4.6]\n"}

# ==============================================================================================================
# [0040] 2026-09-23 17:24:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_18_west_bench_mine_quarry",(1530,62,36),(1528,96,3),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_18_west_bench_mine_quarry.png\n"}

# ==============================================================================================================
# [0041] 2026-09-23 17:25:01  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; L=R["L"]; S2=R["S2"]; O1=R["O1"]
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    p=o.matrix_world.translation
    if 1535<p.x<1560 and 88<p.y<110 and not any(k in o.name for k in ("Tree","Lip","Grass","Weeds","Fern","Rock_Small","Mushroom","Bush","Pebbles","Plant")):
        ci,cj=int((p.x-1500)//3),int(p.y//3)
        print(o.name.replace("_inst",""),tuple(round(v,1) for v in p),(ci,cj),"lvl",L[cj,ci],"reach",(ci,cj) in S2)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Quarry_Face_Straight (1545.0, 99.0, 3.0) (15, 33) lvl 2 reach True\nSM_VK_Quarry_Face_InnerCorner (1548.0
# , 99.0, 3.0) (16, 33) lvl 2 reach True\nSM_VK_Quarry_Face_InnerCorner.001 (1542.0, 99.0, 3.0) (14, 33) lvl 2 reach True\nSM_VK_Quarry_Face_Straight.00
# 1 (1548.0, 96.0, 3.0) (16, 32) lvl 2 reach True\nSM_VK_Quarry_Face_Straight.002 (1542.0, 96.0, 3.0) (14, 32) lvl 2 reach True\nSM_VK_Quarry_Face_Corne
# r (1548.0, 93.0, 3.0) (16, 31) lvl 2 reach False\nSM_VK_Quarry_Face_Corner.001 (1542.0, 93.0, 3.0) (14, 31) lvl 2 reach True\nSM_VK_Quarry_Face_Straig
# ht.003 (1551.0, 93.0, 3.0) (17, 31) lvl 2 reach True\nSM_VK_Quarry_Face_Straight.004 (1539.0, 93.0, 3.0) (13, 31) lvl 2 reach True\nSM_VK_Quarry_Floor
#  (1545.0, 96.0, 3.0) (15, 32) lvl 2 reach True\nSM_VK_Quarry_Floor.001 (1545.0, 93.0, 3.0) (15, 31) lvl 2 reach True\nSM_VK_Prop_TreadwheelCrane (1544

# ==============================================================================================================
# [0042] 2026-09-23 17:25:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_19_meadow_mill_granary",(1596,30,34),(1598,62,1.5),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_19_meadow_mill_granary.png\n"}

# ==============================================================================================================
# [0043] 2026-09-23 17:26:05  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
ws=[o for o in c.all_objects if "Willow" in o.name]
print(len(ws))
roadx=(1623,1629)
for o in ws:
    p=o.matrix_world.translation
    near=[]
    if abs(p.x-1626)<8.5: near.append("mainroad/bridge")
    if abs(p.x-1537.5)<7 : near.append("footbridge")
    if 1597<p.x<1614 and 44<p.y<56: near.append("quay")
    if 1638<p.x<1664 and 46<p.y<56: near.append("lavoir/smokehouse")
    if 1570<p.x<1592 and 44<p.y<60: near.append("watermill")
    print(o.name.replace("_inst",""),tuple(round(v,1) for v in p),(int((p.x-1500)//3),int(p.y//3)),near)
# ---- result ----
# {"result":"Code executed successfully: 18\nSM_VK_Tree_Willow.001 (1676.6, 27.3, 0.0) (58, 9) []\nSM_VK_Tree_Willow.002 (1531.6, 32.3, 0.0) (10, 10) ['
# footbridge']\nSM_VK_Tree_Willow.003 (1572.5, 30.9, 0.0) (24, 10) []\nSM_VK_Tree_Willow.004 (1594.3, 31.5, 0.0) (31, 10) []\nSM_VK_Tree_Willow.005 (162
# 2.3, 30.8, 0.0) (40, 10) ['mainroad/bridge']\nSM_VK_Tree_Willow.006 (1663.8, 31.6, 0.0) (54, 10) []\nSM_VK_Tree_Willow.007 (1674.7, 31.8, 0.0) (58, 10
# ) []\nSM_VK_Tree_Willow.008 (1516.5, 34.7, 0.0) (5, 11) []\nSM_VK_Tree_Willow.009 (1567.7, 33.3, 0.0) (22, 11) []\nSM_VK_Tree_Willow.010 (1610.2, 35.4
# , 0.0) (36, 11) []\nSM_VK_Tree_Willow.011 (1672.4, 34.4, 0.0) (57, 11) []\nSM_VK_Tree_Willow.012 (1567.8, 49.3, 0.0) (22, 16) []\nSM_VK_Tree_Willow.01
# 3 (1606.9, 49.6, 0.0) (35, 16) ['quay']\nSM_VK_Tree_Willow.014 (1671.5, 49.9, 0.0) (57, 16) []\nSM_VK_Tree_Willow.015 (1553.0, 51.7, 0.0) (17, 17) []\

# ==============================================================================================================
# [0044] 2026-09-23 17:26:24  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_20_hamlet_colony",(1540,-16,32),(1542,16,1.5),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_20_hamlet_colony.png\n"}

# ==============================================================================================================
# [0045] 2026-09-23 17:27:02  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
g=[o for o in c.all_objects if "FenceGate" in o.name or "GateArch" in o.name or "Palisade_Gate" in o.name]
for o in g:
    p=o.matrix_world.translation
    near=[]
    for q in c.all_objects:
        if q is o or q.type!="MESH" or any(k in q.name for k in ("Lip","Grass","Weeds","Fern","Pebbles","Plant","Deco","Mushroom","Fence","LowWall","Palisade")): continue
        d=(q.matrix_world.translation.xy-p.xy).length
        if d<2.2: near.append((q.name.replace("_inst",""),round(d,2)))
    print(o.name.replace("_inst",""),tuple(round(v,1) for v in p),round(o.rotation_euler.z*57.3),near)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_FenceGate.020 (1530.0, 4.5, 1.5) 90 [('SM_VK_Animal_Horse', 2.0), ('SM_VK_Animal_Sheep.001', 1.17)]\
# nSM_VK_Prop_FenceGate.021 (1539.0, 16.5, 1.5) 0 []\nSM_VK_Prop_FenceGate.022 (1552.5, 15.0, 1.5) 0 []\nSM_VK_Palisade_Gate (1660.5, 6.0, 1.5) 0 []\nSM
# _VK_Palisade_GateLeaf (1659.1, 6.3, 1.5) 72 []\nSM_VK_Palisade_GateLeaf.001 (1661.9, 6.3, 1.5) 108 []\nSM_VK_Prop_FenceGate.023 (1695.1, 7.6, 1.5) 90 
# []\nSM_VK_Prop_FenceGate.024 (1537.5, 75.0, 3.0) 0 [('SM_VK_Wall_Shed_Window.003', 2.12), ('SM_VK_Corner_Shed.005', 1.5), ('SM_VK_Crop_TreeNursery', 1
# .5)]\nSM_VK_LowWall_GateArch (1660.5, 93.0, 3.0) 0 []\n"}

# ==============================================================================================================
# [0046] 2026-09-23 17:27:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_21_ne_quarter_colony",(1658,88,40),(1660,121,3),lens=30,res=(1600,900),outdir=OUT))
print(shot("play_22_nw_skyline_colony",(1596,92,40),(1598,125,3),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_21_ne_quarter_colony.png\nC:\\Users\\danie\\AppData\\Roaming\\Cla
# ude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play
# \\play_22_nw_skyline_colony.png\n"}

# ==============================================================================================================
# [0047] 2026-09-23 17:28:19  blender  ok
# ==============================================================================================================
import bpy
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if any(k in o.name for k in ("Emblem","Anvil","Forge","Bellows","Sign","Hanging","Kiln","Brew","Mash","Vat","Bell")):
        p=o.matrix_world.translation
        print(o.name.replace("_inst",""),tuple(round(v,1) for v in p),(int((p.x-1500)//3),int(p.y//3)))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tent_Bell (1597.0, 11.2, 1.5) (32, 3)\nSM_VK_Prop_BottleKiln (1543.0, 63.1, 1.5) (14, 21)\nSM_VK_Prop_Dye
# Vat (1556.7, 57.9, 1.5) (18, 19)\nSM_VK_Prop_DyeVat.001 (1558.4, 58.2, 1.5) (19, 19)\nSM_VK_Prop_DyeVat.002 (1560.1, 57.9, 1.5) (20, 19)\nSM_VK_Prop_D
# yeVat.003 (1561.8, 58.2, 1.5) (20, 19)\nSM_VK_Prop_Bellows (1558.2, 77.3, 3.0) (19, 25)\nSM_VK_Prop_Anvil.003 (1555.4, 74.2, 3.0) (18, 24)\nSM_VK_Sign
# _Anvil (1577.8, 77.8, 6.3) (25, 25)\nSM_VK_Prop_Sign (1578.4, 77.8, 5.8) (26, 25)\nSM_VK_Emblem_Ridge_Tankard (1596.0, 77.0, 16.7) (32, 25)\nSM_VK_Pro
# p_Sign.001 (1596.3, 78.0, 6.0) (32, 26)\nSM_VK_Prop_Sign.002 (1610.8, 77.8, 6.3) (36, 25)\nSM_VK_Sign_Potion (1607.8, 78.2, 6.3) (35, 26)\nSM_VK_Emble
# m_Ridge_Sheaf (1582.0, 129.0, 11.1) (27, 43)\nSM_VK_Roof_Bellcote (1602.0, 129.0, 15.8) (34, 43)\nSM_VK_Emblem_Ridge_Key (1583.0, 114.0, 13.9) (27, 38

# ==============================================================================================================
# [0048] 2026-09-23 17:31:12  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
c=bpy.data.collections["VK_ValleyTown"]
for o in c.all_objects:
    if "Bridge" in o.name or "Quay" in o.name or "Pier" in o.name:
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        print(o.name.replace("_inst",""),[round(min(q[k] for q in pts),2) for k in range(3)],[round(max(q[k] for q in pts),2) for k in range(3)])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Bridge_Stone_Span [1623.87, 36.0, -1.6] [1628.13, 42.0, 2.26]\nSM_VK_Bridge_Stone_Span.001 [1623.87, 42.0
# , -1.6] [1628.13, 48.0, 2.26]\nSM_VK_Bridge_Stone_Pier [1622.64, 41.05, -2.0] [1629.36, 42.95, 1.0]\nSM_VK_Bridge_Stone_Ramp [1623.12, 48.0, -0.6] [16
# 28.85, 52.71, 2.13]\nSM_VK_Bridge_Stone_Ramp.001 [1623.15, 31.29, -0.6] [1628.88, 36.0, 2.13]\nSM_VK_Bridge_Wood_End [1535.46, 32.78, -0.79] [1539.54,
#  36.02, 1.49]\nSM_VK_Bridge_Wood_Mid [1535.74, 35.9, -0.25] [1539.25, 39.0, 1.44]\nSM_VK_Bridge_Wood_Mid.001 [1535.74, 38.9, -0.25] [1539.25, 42.0, 1.
# 44]\nSM_VK_Bridge_Wood_Mid.002 [1535.74, 41.9, -0.25] [1539.25, 45.0, 1.44]\nSM_VK_Bridge_Wood_Mid.003 [1535.74, 44.9, -0.25] [1539.25, 48.0, 1.44]\nS
# M_VK_Bridge_Wood_End.001 [1535.46, 47.98, -0.79] [1539.54, 51.22, 1.49]\nSM_VK_Bridge_Wood_Bent [1535.7, 35.77, -3.0] [1539.3, 36.23, -0.02]\nSM_VK_Br

# ==============================================================================================================
# [0049] 2026-09-23 17:31:39  blender  ok
# ==============================================================================================================
import bpy, collections
R=bpy.app.driver_namespace["_play_rev"]; E2=R["edges_nodoor"]
adj=collections.defaultdict(list)
def isTree(n): return n and ("Tree_" in n or "Bush" in n or "Rock_Boulder" in n)
for (i,j,i2,j2),h in E2.items():
    if h is None or isTree(h): adj[(i,j)].append((i2,j2)); adj[(i2,j2)].append((i,j))
ramps=[((41,10),(41,9)),((42,10),(42,9)),((41,17),(41,18)),((42,17),(42,18)),((41,23),(41,24)),((42,23),(42,24)),((9,23),(9,24)),((10,23),(10,24)),((8,33),(8,34))]
for a,b in ramps: adj[a].append(b); adj[b].append(a)
for c in (41,42,12):
    for j in range(11,16): adj[(c,j)].append((c,j+1)); adj[(c,j+1)].append((c,j))
def dist(s):
    D={s:0}; q=collections.deque([s])
    while q:
        c=q.popleft()
        for n in adj[c]:
            if n not in D: D[n]=D[c]+1; q.append(n)
    return D
D=dist((41,33))   # plaza
for name,cell in [("mine portal front",(4,31)),("quarry",(15,30)),("woodcutter",(6,25)),("logcabin",(1,24)),("west wall inside (24,30)",(24,30)),("west bench (19,30)",(19,30)),("hamlet longhouse",(2,2)),("fisher hut",(64,7)),("watermill",(28,18)),("barracks",(62,1)),("granary",(38,19))]:
    print(name,cell,D.get(cell),"cells ->",(D.get(cell) or 0)*3,"m")
print("straight-line plaza->mine", ((41-4)**2+(33-31)**2)**0.5*3)
# ---- result ----
# {"result":"Code executed successfully: mine portal front (4, 31) 41 cells -> 123 m\nquarry (15, 30) 29 cells -> 87 m\nwoodcutter (6, 25) 43 cells -> 1
# 29 m\nlogcabin (1, 24) 49 cells -> 147 m\nwest wall inside (24,30) (24, 30) 20 cells -> 60 m\nwest bench (19,30) (19, 30) 25 cells -> 75 m\nhamlet lon
# ghouse (2, 2) 72 cells -> 216 m\nfisher hut (64, 7) 49 cells -> 147 m\nwatermill (28, 18) 32 cells -> 96 m\nbarracks (62, 1) 55 cells -> 165 m\ngranar
# y (38, 19) 19 cells -> 57 m\nstraight-line plaza->mine 111.16204388189342\n"}

# ==============================================================================================================
# [0050] 2026-09-23 17:32:06  blender  ok
# ==============================================================================================================
import bpy, collections
R=bpy.app.driver_namespace["_play_rev"]; E=R["edges"]; E2=R["edges_nodoor"]
for j in range(23,48):
    print(j,E.get((22,j,23,j),"n/a"),E2.get((22,j,23,j),"n/a"))
# ---- result ----
# {"result":"Code executed successfully: 23 None None\n24 None None\n25 SM_VK_TownWall_Straight_inst.077 SM_VK_TownWall_Straight_inst.077\n26 SM_VK_Town
# Wall_Straight_inst.079 SM_VK_TownWall_Straight_inst.079\n27 SM_VK_TownWall_Straight_inst.081 SM_VK_TownWall_Straight_inst.081\n28 SM_VK_TownWall_Strai
# ght_inst.083 SM_VK_TownWall_Straight_inst.083\n29 SM_VK_TownWall_Straight_inst.085 SM_VK_TownWall_Straight_inst.085\n30 SM_VK_Bush_Round_inst.043 SM_V
# K_Bush_Round_inst.043\n31 SM_VK_TownWall_Straight_inst.089 SM_VK_TownWall_Straight_inst.089\n32 SM_VK_TownWall_Straight_inst.091 SM_VK_TownWall_Straig
# ht_inst.091\n33 SM_VK_TownWall_Straight_inst.093 SM_VK_TownWall_Straight_inst.093\n34 SM_VK_TownWall_Straight_inst.095 SM_VK_TownWall_Straight_inst.09
# 5\n35 SM_VK_TownWall_Straight_inst.097 SM_VK_TownWall_Straight_inst.097\n36 SM_VK_TownWall_Straight_inst.099 SM_VK_TownWall_Straight_inst.099\n37 SM_V

# ==============================================================================================================
# [0051] 2026-09-23 17:32:34  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; E2=R["edges_nodoor"]; L=R["L"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
PASS=("LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","VKV_Water","Rug","Grass","Porch","Stair","Bridge","Ramp","Puddle","Path","Moss","Leaves","Decal","Tree_","Bush","Rock_Boulder")
def cast(a,b):
    d=(b-a); left=d.length; d.normalize(); o=a.copy()
    for _ in range(16):
        r=sc.ray_cast(dg,o,d,distance=left)
        if not r[0]: return None
        n=r[4].name
        if any(p in n for p in PASS):
            left-=(r[1]-o).length+0.02; o=r[1]+d*0.02
            if left<=0: return None
            continue
        return n
    return None
E3={}
for k,h in E2.items():
    if h and ("Tree_" in h or "Bush" in h or "Rock_Boulder" in h):
        i,j,i2,j2=k; z=L[j,i]*1.5+0.9
        a=Vector((1500+3*i+1.5,3*j+1.5,z)); b=Vector((1500+3*i2+1.5,3*j2+1.5,z))
        d=(b-a).normalized(); lat=Vector((-d.y,d.x,0)); res="x"
        for off in (0.0,-0.9,0.9):
            hh=cast(a+lat*off,b+lat*off)
            if hh is None: res=None; break
            res=hh
        E3[k]=("TREE" if res is None else res)
    else: E3[k]=h
R["edges3"]=E3
print(sum(1 for v in E3.values() if v=="TREE"), [ (k,v) for k,v in E3.items() if k[0]==22 and k[2]==23])
# ---- result ----
# {"result":"Code executed successfully: 1311 [((22, 0, 23, 0), None), ((22, 1, 23, 1), None), ((22, 2, 23, 2), None), ((22, 3, 23, 3), None), ((22, 4, 
# 23, 4), None), ((22, 5, 23, 5), None), ((22, 6, 23, 6), None), ((22, 7, 23, 7), None), ((22, 8, 23, 8), None), ((22, 9, 23, 9), 'TREE'), ((22, 10, 23,
#  10), 'TREE'), ((22, 11, 23, 11), None), ((22, 16, 23, 16), None), ((22, 17, 23, 17), None), ((22, 18, 23, 18), None), ((22, 19, 23, 19), None), ((22,
#  20, 23, 20), None), ((22, 21, 23, 21), None), ((22, 22, 23, 22), None), ((22, 23, 23, 23), None), ((22, 24, 23, 24), None), ((22, 25, 23, 25), 'SM_VK
# _TownWall_Straight_inst.077'), ((22, 26, 23, 26), 'SM_VK_TownWall_Straight_inst.079'), ((22, 27, 23, 27), 'SM_VK_TownWall_Straight_inst.081'), ((22, 2
# 8, 23, 28), 'SM_VK_TownWall_Straight_inst.083'), ((22, 29, 23, 29), 'SM_VK_TownWall_Straight_inst.085'), ((22, 30, 23, 30), 'SM_VK_TownWall_Straight_i

# ==============================================================================================================
# [0052] 2026-09-23 17:33:35  blender  ok
# ==============================================================================================================
import bpy, collections
R=bpy.app.driver_namespace["_play_rev"]; E3=R["edges3"]
adj=collections.defaultdict(list)
for (i,j,i2,j2),h in E3.items():
    if h is None or h=="TREE": adj[(i,j)].append((i2,j2)); adj[(i2,j2)].append((i,j))
ramps=[((41,10),(41,9)),((42,10),(42,9)),((41,17),(41,18)),((42,17),(42,18)),((41,23),(41,24)),((42,23),(42,24)),((9,23),(9,24)),((10,23),(10,24)),((8,33),(8,34))]
for a,b in ramps: adj[a].append(b); adj[b].append(a)
for c in (41,42,12):
    for j in range(11,16): adj[(c,j)].append((c,j+1)); adj[(c,j+1)].append((c,j))
def dist(s):
    D={s:0}; q=collections.deque([s])
    while q:
        c=q.popleft()
        for n in adj[c]:
            if n not in D: D[n]=D[c]+1; q.append(n)
    return D
D=dist((41,33))
for name,cell in [("mine portal front",(4,31)),("quarry",(15,30)),("woodcutter",(6,25)),("logcabin",(1,24)),("west bench (19,30)",(19,30)),("inside west wall (24,30)",(24,30)),("hamlet longhouse",(2,2)),("fisher hut door",(64,7)),("watermill",(28,18)),("barracks door",(62,1)),("granary",(38,19)),("crane (14,34)",(14,34))]:
    d=D.get(cell); print(name,cell,d, (d*3 if d else None))
# ---- result ----
# {"result":"Code executed successfully: mine portal front (4, 31) 57 171\nquarry (15, 30) 55 165\nwoodcutter (6, 25) 49 147\nlogcabin (1, 24) 53 159\nw
# est bench (19,30) (19, 30) 59 177\ninside west wall (24,30) (24, 30) 20 60\nhamlet longhouse (2, 2) 72 216\nfisher hut door (64, 7) 49 147\nwatermill 
# (28, 18) 32 96\nbarracks door (62, 1) 55 165\ngranary (38, 19) 19 57\ncrane (14,34) (14, 34) None None\n"}

# ==============================================================================================================
# [0053] 2026-09-23 17:34:21  blender  ok
# ==============================================================================================================
import bpy
R=bpy.app.driver_namespace["_play_rev"]; E3=R["edges3"]
for k in [(39,35,39,36),(40,35,40,36),(39,36,39,37),(40,36,40,37),(39,37,39,38),(40,37,40,38),(39,38,39,39),(40,38,40,39),(39,34,39,35),(40,34,40,35),(39,34,40,34)]:
    print(k,E3.get(k))
# also: west-bench road north end and stair
for k in [(8,32,8,33),(9,33,8,33),(8,33,7,33),(7,33,8,33),(8,34,8,35),(8,34,9,34),(7,34,8,34),(8,34,7,34)]:
    kk=k if k in E3 else (k[2],k[3],k[0],k[1])
    print(k,E3.get(kk,"n/a"))
# ---- result ----
# {"result":"Code executed successfully: (39, 35, 39, 36) None\n(40, 35, 40, 36) None\n(39, 36, 39, 37) None\n(40, 36, 40, 37) None\n(39, 37, 39, 38) No
# ne\n(40, 37, 40, 38) None\n(39, 38, 39, 39) None\n(40, 38, 40, 39) None\n(39, 34, 39, 35) None\n(40, 34, 40, 35) None\n(39, 34, 40, 34) None\n(8, 32, 
# 8, 33) None\n(9, 33, 8, 33) None\n(8, 33, 7, 33) None\n(7, 33, 8, 33) None\n(8, 34, 8, 35) None\n(8, 34, 9, 34) None\n(7, 34, 8, 34) TREE\n(8, 34, 7, 
# 34) TREE\n"}

# ==============================================================================================================
# [0054] 2026-09-23 17:34:39  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for n in ("SM_VK_Wall_Stone_Door_inst.050","SM_VK_Prop_Woodpile_inst.016","SM_VK_Chapel_Wall_Door_inst.003","SM_VK_Wall_Stone_Door_inst.049"):
    o=bpy.data.objects[n]; pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n,[round(min(p[k] for p in pts),2) for k in range(3)],[round(max(p[k] for p in pts),2) for k in range(3)],round(o.rotation_euler.z*57.3))
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_23_chapel_north_blacksmith",(1650,140,14),(1660,124,4),lens=26,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Door_inst.050 [1667.98, 128.16, 2.9] [1671.02, 129.28, 6.13] 0\nSM_VK_Prop_Woodpile_inst.016 [
# 1668.0, 126.45, 2.95] [1671.7, 127.75, 4.47] 0\nSM_VK_Chapel_Wall_Door_inst.003 [1647.0, 122.65, 2.97] [1650.3, 124.3, 7.5] 180\nSM_VK_Wall_Stone_Door
# _inst.049 [1670.98, 112.66, 2.9] [1674.02, 113.78, 6.13] 0\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-df
# f3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_23_chapel_north_blacksmith.png\n"}

# ==============================================================================================================
# [0055] 2026-09-23 17:35:11  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_23_chapel_north_door",(1639,133,8),(1651,122,4),lens=26,res=(1600,900),outdir=OUT))
print(shot("play_24_blacksmith_door_woodpile",(1671.5,120.5,5.5),(1669.5,128.5,4.0),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_23_chapel_north_door.png\nC:\\Users\\danie\\AppData\\Roaming\\Cla
# ude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play
# \\play_24_blacksmith_door_woodpile.png\n"}

# ==============================================================================================================
# [0056] 2026-09-23 17:36:13  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
c=bpy.data.collections["VK_ValleyTown"]
PASS=("LipGrass","Weeds","Plant_","Crop_","Deco_","Mushrooms","Pebbles","Flower","BuildSite_Cell","Stockpile_Border","Rug","Grass","Puddle","Moss","Leaves","Decal","Porch","Step","Door")
def first(o_,d,dist):
    o_=o_.copy(); tot=0
    for _ in range(10):
        r=sc.ray_cast(dg,o_,d,distance=dist-tot)
        if not r[0]: return None
        tot+=(r[1]-o_).length; n=r[4].name
        if not any(p in n for p in PASS): return (n.replace("_inst",""),round(tot,2))
        o_=r[1]+d*0.02; tot+=0.02
    return None
for o in c.all_objects:
    if "Door" not in o.name: continue
    m=o.matrix_world; outd=(m.to_3x3().normalized()@Vector((0,-1,0))); outd.z=0; outd.normalize()
    bc=m@(sum((Vector(v) for v in o.bound_box),Vector())/8)
    zb=m.translation.z
    lat=Vector((-outd.y,outd.x,0))
    hits=[]
    for h in (0.3,0.6,1.0):
        for off in (-0.4,0,0.4):
            s=Vector((bc.x,bc.y,zb+h))+lat*off+outd*0.45
            f=first(s,outd,1.6)
            if f: hits.append(f)
    if len(hits)>=5:
        print(o.name.replace("_inst",""),tuple(round(v,1) for v in bc),len(hits),sorted(set(h[0] for h in hits)),min(h[1] for h in hits))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Door.038 (1579.5, 77.7, 4.5) 9 ['SM_VK_TownWall_Straight.006'] 1.25\nSM_VK_Wall_StoneUp_Door (
# 1579.5, 84.1, 7.3) 9 ['SM_VK_Stair_Stone_Ext'] 0.53\nSM_VK_Wall_Plaster_Door.019 (1597.5, 77.7, 4.4) 9 ['SM_VK_TownWall_Straight.018'] 1.26\nSM_VK_Wal
# l_Stone_Door.039 (1612.5, 77.7, 4.5) 9 ['SM_VK_TownWall_Straight.028'] 1.25\nSM_VK_Wall_StoneUp_Door.001 (1579.5, 95.9, 7.3) 9 ['SM_VK_Stair_Stone_Ext
# .001'] 0.53\nSM_VK_Wall_Stone_Door.046 (1603.5, 117.3, 4.5) 5 ['SM_VK_Prop_Anvil.004'] 0.14\nSM_VK_Wall_Plaster_Door.024 (1672.5, 77.7, 4.4) 9 ['SM_VK
# _TownWall_Straight.065'] 1.26\nSM_VK_Wall_Stone_Door.049 (1672.5, 113.2, 4.5) 5 ['SM_VK_Prop_BarrelStack.023'] 0.38\n"}

# ==============================================================================================================
# [0057] 2026-09-23 17:36:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_25_skyline_smith_door_anvil",(1606,124,5.8),(1603.5,117.5,3.9),lens=30,res=(1600,900),outdir=OUT))
print(shot("play_26_brewery_door_barrels",(1675,106,5.8),(1672.5,113.3,3.9),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_25_skyline_smith_door_anvil.png\nC:\\Users\\danie\\AppData\\Roami
# ng\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\revie
# w\\play\\play_26_brewery_door_barrels.png\n"}

# ==============================================================================================================
# [0058] 2026-09-23 17:37:42  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; bvh=R["bvh"]
c=bpy.data.collections["VK_ValleyTown"]
KEYS=("Wall_","Corner_","Door","Porch","Stair","Prop_Well","MarketStall","Tent","Pile_","Stockpile","Prop_")
SKIP=("TownWall","Tower_Round","Gatehouse","Bridge","Quay","Pier","Barge","Rowboat","Mill_","Roof","Chimney","StoneUp","PlasterUp","TimberUp","Sign","Lantern","FlowerBox","Banner","Emblem","Shutter","Window","Ivy","Turret","Oriel","Hoist","Upper","Balcony","Dormer","Weather","Flag","Gable","Beam","Wheel","Lamp")
out=[]
for o in c.all_objects:
    if o.type!="MESH" or not any(k in o.name for k in KEYS) or any(k in o.name for k in SKIP): continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    zmin=min(p.z for p in pts)
    cx=sum(p.x for p in pts)/8; cy=sum(p.y for p in pts)/8
    # sample ground at 5 points of the footprint
    xs=(min(p.x for p in pts),max(p.x for p in pts)); ys=(min(p.y for p in pts),max(p.y for p in pts))
    gz=[]
    for (x,y) in ((cx,cy),(xs[0]+0.2,ys[0]+0.2),(xs[1]-0.2,ys[0]+0.2),(xs[0]+0.2,ys[1]-0.2),(xs[1]-0.2,ys[1]-0.2)):
        h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)))
        if h[0]: gz.append(h[0].z)
    if not gz: continue
    gmin,gmax=min(gz),max(gz)
    if zmin-gmin>0.35 or gmax-gmin>0.9:
        out.append((o.name.replace("_inst",""),round(cx,1),round(cy,1),round(zmin,2),round(gmin,2),round(gmax,2)))
print(len(out))
for r in sorted(out,key=lambda r:-(r[3]-r[4]))[:60]: print(r)
# ---- result ----
# {"result":"Code executed successfully: 229\n('SM_VK_Parapet_Corner', 1575.0, 96.0, 13.52, 3.0, 3.0)\n('SM_VK_Parapet_Corner.001', 1581.0, 96.0, 13.52,
#  3.0, 3.0)\n('SM_VK_Parapet_Corner.002', 1581.0, 102.0, 13.52, 3.0, 3.0)\n('SM_VK_Parapet_Corner.003', 1575.0, 102.0, 13.52, 3.0, 3.0)\n('SM_VK_Wall_T
# imber.039', 1632.2, 73.5, 9.0, 2.93, 3.0)\n('SM_VK_Wall_Timber.038', 1622.8, 73.5, 9.0, 2.96, 3.0)\n('SM_VK_Wall_Timber_X.033', 1624.5, 78.2, 9.0, 3.0
# , 3.0)\n('SM_VK_Wall_Timber_K.046', 1630.5, 78.2, 9.0, 3.0, 3.0)\n('SM_VK_Wall_Timber_Door', 1622.8, 76.5, 9.0, 3.0, 3.0)\n('SM_VK_Wall_Timber_Door.00
# 1', 1632.2, 76.5, 9.0, 3.0, 3.0)\n('SM_VK_InnerCorner_Timber.007', 1614.3, 84.3, 8.8, 3.0, 3.0)\n('SM_VK_Wall_Timber_K.050', 1592.8, 85.5, 8.6, 3.0, 3
# .0)\n('SM_VK_Wall_Timber_X.037', 1599.2, 85.5, 8.6, 3.0, 3.0)\n('SM_VK_Wall_Timber.045', 1592.8, 82.5, 8.6, 3.0, 3.0)\n('SM_VK_Wall_Timber_K.051', 159

# ==============================================================================================================
# [0059] 2026-09-23 17:38:07  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; bvh=R["bvh"]
c=bpy.data.collections["VK_ValleyTown"]
SKIP=("TownWall","Tower_Round","Gatehouse","Bridge","Quay","Pier","Barge","Rowboat","Roof","Chimney","Tree","Bush","Rock","Lip","Grass","Weeds","Fern","Plant","Mushroom","Pebbles","Deco","Crop","Flower","Emblem","Sign","Lantern","Bunting","Banner")
out=[]
for o in c.all_objects:
    if o.type!="MESH" or any(k in o.name for k in SKIP): continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    zmin=min(p.z for p in pts)
    xs=(min(p.x for p in pts),max(p.x for p in pts)); ys=(min(p.y for p in pts),max(p.y for p in pts))
    if (xs[1]-xs[0])*(ys[1]-ys[0])<0.2: continue
    gz=[]
    for fx in (0.15,0.5,0.85):
        for fy in (0.15,0.5,0.85):
            x=xs[0]+(xs[1]-xs[0])*fx; y=ys[0]+(ys[1]-ys[0])*fy
            h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)))
            if h[0]: gz.append(h[0].z)
    if not gz: continue
    gmin,gmax=min(gz),max(gz)
    if gmax-gmin>0.9 and zmin<gmax+0.5:
        out.append((o.name.replace("_inst",""),round(xs[0],1),round(xs[1],1),round(ys[0],1),round(ys[1],1),round(zmin,2),round(gmin,2),round(gmax,2)))
print(len(out))
for r in out: print(r)
# ---- result ----
# {"result":"Code executed successfully: 7\n('SM_VK_Wall_Stone_Window.136', 1581.0, 1584.0, 47.2, 48.3, -0.11, -0.97, -0.05)\n('SM_VK_Prop_Cart.008', 15
# 76.1, 1579.8, 57.7, 60.5, 0.0, 0.0, 1.41)\n('SM_VK_Prop_Laundry.002', 1638.6, 1643.8, 53.3, 54.1, 0.0, 0.0, 1.36)\n('SM_VK_Prop_FishRack', 1655.2, 165
# 8.6, 52.9, 54.7, -0.22, 0.0, 1.5)\n('SM_VK_Pile_Fish_2', 1692.8, 1694.0, 23.9, 25.7, 0.04, -1.5, -0.36)\n('SM_VK_Mine_Portal', 1507.4, 1516.4, 96.1, 1
# 04.0, 2.4, 3.0, 4.5)\n('SM_VK_Prop_TreadwheelCrane', 1542.4, 1546.4, 95.8, 105.6, 5.95, 3.0, 6.0)\n"}

# ==============================================================================================================
# [0060] 2026-09-23 17:38:28  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
R=bpy.app.driver_namespace["_play_rev"]; bvh=R["bvh"]
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
def prof(x,y0,y1,step=0.5):
    s=[]
    y=y0
    while y<=y1:
        h=bvh.ray_cast(Vector((x,y,60)),Vector((0,0,-1)))
        r=sc.ray_cast(dg,Vector((x,y,60)),Vector((0,0,-1)))
        s.append((y,round(h[0].z,2) if h[0] else None, r[4].name.split("_inst")[0].replace("SM_VK_","") if r[0] and "Chunk" not in r[4].name else ""))
        y+=step
    return s
for x in (1524.5,1528.5,1531.5,1535.5):
    print("x",x,[(a,b) for a,b,c in prof(x,68,76,1.0)])
for x in (1624.0,1625.5,1627.5):
    print("x",x,prof(x,67,74,1.0))
# ---- result ----
# {"result":"Code executed successfully: x 1524.5 [(68, 1.5), (69.0, 1.5), (70.0, 1.5), (71.0, 1.5), (72.0, 2.88), (73.0, 3.0), (74.0, 3.0), (75.0, 3.0)
# , (76.0, 3.0)]\nx 1528.5 [(68, 1.5), (69.0, 1.5), (70.0, 1.5), (71.0, 1.75), (72.0, 2.25), (73.0, 2.75), (74.0, 3.0), (75.0, 3.0), (76.0, 3.0)]\nx 153
# 1.5 [(68, 1.5), (69.0, 1.5), (70.0, 1.5), (71.0, 1.75), (72.0, 2.25), (73.0, 2.75), (74.0, 3.0), (75.0, 3.0), (76.0, 3.0)]\nx 1535.5 [(68, 1.5), (69.0
# , 1.5), (70.0, 1.5), (71.0, 1.5), (72.0, 2.88), (73.0, 3.0), (74.0, 3.0), (75.0, 3.0), (76.0, 3.0)]\nx 1624.0 [(67, 1.5, ''), (68.0, 1.5, ''), (69.0, 
# 1.5, ''), (70.0, 1.5, 'Roof_Cone_R2'), (71.0, 1.75, 'Roof_Cone_R2'), (72.0, 2.25, 'Roof_Cone_R2'), (73.0, 2.75, 'Roof_Hip'), (74.0, 3.0, 'Roof_Hip')]\
# nx 1625.5 [(67, 1.5, ''), (68.0, 1.5, ''), (69.0, 1.5, ''), (70.0, 1.5, 'Gatehouse_Block'), (71.0, 1.75, 'Roof_Cone_R2'), (72.0, 2.25, 'Roof_Cone_R2')

# ==============================================================================================================
# [0061] 2026-09-23 17:38:52  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
for x in (1627.5,1626.5,1628.5):
    row=[]
    y=67.0
    while y<=80:
        r=sc.ray_cast(dg,Vector((x,y,4.9)),Vector((0,0,-1)),distance=6)
        row.append((y, round(r[1].z,2) if r[0] else None, (r[4].name.replace("_inst","").replace("SM_VK_","")[:14] if r[0] else "")))
        y+=1.0
    print(x,row)
# ---- result ----
# {"result":"Code executed successfully: 1627.5 [(67.0, 1.5, 'VKV_Chunk_2_1'), (68.0, 1.5, 'VKV_Chunk_2_1'), (69.0, 1.5, 'VKV_Chunk_2_1'), (70.0, 1.5, '
# VKV_Chunk_2_1'), (71.0, 1.75, 'VKV_Chunk_2_1'), (72.0, 3.04, 'Gatehouse_Bloc'), (73.0, 3.04, 'Gatehouse_Bloc'), (74.0, 3.04, 'Gatehouse_Bloc'), (75.0,
#  3.04, 'Gatehouse_Bloc'), (76.0, 3.04, 'Gatehouse_Bloc'), (77.0, 3.04, 'Gatehouse_Bloc'), (78.0, 3.04, 'Gatehouse_Bloc'), (79.0, 3.0, 'VKV_Chunk_2_1')
# , (80.0, 3.0, 'VKV_Chunk_2_1')]\n1626.5 [(67.0, 1.5, 'VKV_Chunk_2_1'), (68.0, 1.5, 'VKV_Chunk_2_1'), (69.0, 1.5, 'VKV_Chunk_2_1'), (70.0, 1.5, 'VKV_Ch
# unk_2_1'), (71.0, 3.24, 'Gatehouse_Bloc'), (72.0, 3.36, 'Gatehouse_Bloc'), (73.0, 3.04, 'Gatehouse_Bloc'), (74.0, 3.04, 'Gatehouse_Bloc'), (75.0, 3.04
# , 'Gatehouse_Bloc'), (76.0, 3.04, 'Gatehouse_Bloc'), (77.0, 3.04, 'Gatehouse_Bloc'), (78.0, 3.04, 'Gatehouse_Bloc'), (79.0, 3.0, 'VKV_Chunk_2_1'), (80

# ==============================================================================================================
# [0062] 2026-09-23 17:39:08  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_27_gate_threshold_step",(1628.3,65.5,2.9),(1627.5,72.5,2.4),lens=24,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_27_gate_threshold_step.png\n"}

# ==============================================================================================================
# [0063] 2026-09-23 17:39:45  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]; dg=bpy.context.evaluated_depsgraph_get()
for x in (1627.0,1627.5,1628.0):
    for h in (0.2,0.5,1.0):
        o=Vector((x,69.0,1.5+h)); 
        # follow ramp: flat until 70.5, then slope 0.5
        o2=Vector((x,70.5,1.5+h)); d=Vector((0,1,0.5)).normalized()
        r=sc.ray_cast(dg,o2,d,distance=4.0)
        print(x,h, (round(r[1].y,2),round(r[1].z,2),r[4].name.replace("_inst","")) if r[0] else None)
# the gatehouse block mesh: min z of faces near the front
o=bpy.data.objects["SM_VK_Gatehouse_Block_inst"]; mw=o.matrix_world
vs=[mw@v.co for v in o.data.vertices]
front=[v for v in vs if 1626<v.x<1629 and v.y<73.0 and v.z<3.5]
print(len(front), sorted(set((round(v.y,2),round(v.z,2)) for v in front))[:40])
# ---- result ----
# {"result":"Code executed successfully: 1627.0 0.2 (73.08, 2.99, 'SM_VK_Gatehouse_Block')\n1627.0 0.5 (72.48, 2.99, 'SM_VK_Gatehouse_Block')\n1627.0 1.
# 0 None\n1627.5 0.2 (73.08, 2.99, 'SM_VK_Gatehouse_Block')\n1627.5 0.5 (72.48, 2.99, 'SM_VK_Gatehouse_Block')\n1627.5 1.0 None\n1628.0 0.2 (73.08, 2.99
# , 'SM_VK_Gatehouse_Block')\n1628.0 0.5 (72.48, 2.99, 'SM_VK_Gatehouse_Block')\n1628.0 1.0 None\n158 [(70.28, 3.22), (70.29, 3.06), (70.29, 3.19), (70.
# 3, 3.0), (70.31, 3.05), (70.32, 3.19), (70.35, 3.08), (70.35, 3.17), (70.38, 3.18), (70.38, 3.32), (70.38, 3.36), (70.39, 3.01), (70.4, 2.94), (70.41,
#  2.89), (70.42, 2.93), (70.42, 3.32), (70.45, 3.19), (70.45, 3.23), (70.46, 2.89), (70.46, 3.0), (70.46, 3.06), (70.47, 3.31), (70.62, 3.24), (70.65, 
# 3.03), (70.66, 3.07), (70.66, 3.19), (70.77, 3.17), (70.79, 3.03), (70.8, 2.99), (70.8, 3.16), (70.8, 3.17), (70.81, 3.06), (70.81, 3.09), (70.81, 3.1

# ==============================================================================================================
# [0064] 2026-09-23 17:40:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_28_gate_threshold_from_inside",(1627.9,76.5,4.6),(1627.5,70.0,1.9),lens=24,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_28_gate_threshold_from_inside.png\n"}

# ==============================================================================================================
# [0065] 2026-09-23 17:40:40  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\play"
print(shot("play_29_bridge_south_willow",(1640,14,22),(1625,34,0.5),lens=28,res=(1600,900),outdir=OUT))
print(shot("play_30_quay_willow",(1616,62,16),(1606,48,0),lens=28,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\play\\play_29_bridge_south_willow.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\pl
# ay\\play_30_quay_willow.png\n"}

# ==============================================================================================================
# [0066] 2026-09-23 17:42:42  blender  ok
# ==============================================================================================================
import bpy
bpy.app.driver_namespace.pop("_play_rev",None)
print("_play_rev" in bpy.app.driver_namespace, bpy.data.is_dirty)
# ---- result ----
# {"result":"Code executed successfully: False False\n"}
