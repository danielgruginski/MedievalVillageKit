# valley-review / agent-a1dc3749fd3f86fcb.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 16:57:37  blender  ok
# ==============================================================================================================
import bpy
t = bpy.data.texts["vk_render"].as_string()
print(t[:3000])
sc = bpy.data.scenes.get("VillageKit")
print(bpy.context.scene.name)
print(len(bpy.data.collections["VK_ValleyTerrain"].objects), len(bpy.data.collections["VK_ValleyTown"].all_objects))
# ---- result ----
# {"result":"Code executed successfully: import bpy, os\nfrom mathutils import Vector\nOUTD=r\"C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-works
# paces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\"\ndef shot(name,loc,target,len
# s=35,res=(1280,720),scene=\"VillageKit\",samples=None,outdir=None):\n sc=bpy.data.scenes[scene]\n cam=bpy.data.objects.get(\"VK_CamTmp\")\n if cam is 
# None:\n cam=bpy.data.objects.new(\"VK_CamTmp\",bpy.data.cameras.new(\"VK_CamTmp\"))\n if cam.name not in sc.collection.objects: sc.collection.objects.
# link(cam)\n cam.location=loc; cam.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()\n cam.data.lens=lens; cam.data.clip_e
# nd=3000\n old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)\n sc.camera=cam; sc.render.

# ==============================================================================================================
# [0002] 2026-09-23 16:58:02  blender  ok
# ==============================================================================================================
import bpy, collections
c=bpy.data.collections["VK_ValleyTown"]
print([ch.name for ch in c.children][:20])
types=collections.Counter(o.type for o in c.all_objects)
print(types)
par=collections.Counter(o.parent is None for o in c.all_objects)
print("toplevel", par)
names=collections.Counter(o.name.split('.')[0] for o in c.all_objects if o.parent is None)
print(len(names)); print(names.most_common(80))
tc=bpy.data.collections["VK_ValleyTerrain"]
print([(o.name,o.type,len(o.data.vertices) if o.type=='MESH' else 0, [m.type for m in o.modifiers]) for o in tc.objects])
# ---- result ----
# {"result":"Code executed successfully: []\nCounter({'MESH': 5568})\ntoplevel Counter({True: 5568})\n339\n[('SM_VKT_LipGrass_inst', 1344), ('SM_VK_Tree
# _Pine_Young_inst', 342), ('SM_VK_Tree_Pine_B_inst', 335), ('SM_VK_Tree_Pine_A_inst', 324), ('SM_VK_Wall_Timber_Window_inst', 135), ('SM_VK_Deco_Weeds_
# inst', 125), ('SM_VK_Bush_Round_inst', 121), ('SM_VK_TownWall_Straight_inst', 119), ('SM_VK_Rock_Small_A_inst', 113), ('SM_VK_Plant_Fern_inst', 112), 
# ('SM_VK_Wall_Stone_inst', 101), ('SM_VK_Corner_Timber_inst', 88), ('SM_VK_Rock_Pebbles_inst', 87), ('SM_VK_Rock_Small_B_inst', 86), ('SM_VK_Rock_Bould
# er_A_inst', 86), ('SM_VK_Corner_Stone_inst', 83), ('SM_VK_Mushrooms_Brown_inst', 75), ('SM_VK_Wall_Stone_Window_inst', 68), ('SM_VK_Tree_Oak_A_inst', 
# 63), ('SM_VK_Tree_Oak_B_inst', 60), ('SM_VK_Tree_Birch_inst', 52), ('SM_VK_Prop_FlowerBox_inst', 41), ('SM_VK_Plant_TallGrass_inst', 39), ('SM_VK_Plan

# ==============================================================================================================
# [0003] 2026-09-23 16:58:22  blender  ok
# ==============================================================================================================
import bpy, time
from mathutils.bvhtree import BVHTree
from mathutils import Vector
t0=time.time()
def mkbvh(objs):
    verts=[];polys=[];off=0
    for o in objs:
        mw=o.matrix_world; me=o.data
        verts.extend([mw@v.co for v in me.vertices])
        polys.extend([[off+i for i in p.vertices] for p in me.polygons])
        off+=len(me.vertices)
    return BVHTree.FromPolygons(verts,polys)
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[o for o in tc.objects if "Chunk" in o.name]; waters=[o for o in tc.objects if "Water" in o.name]
ns=bpy.app.driver_namespace
ns["rv_ground_bvh"]=mkbvh(chunks); ns["rv_water_bvh"]=mkbvh(waters)
print(time.time()-t0)
o=bpy.data.objects[next(iter(bpy.data.collections["VK_ValleyTown"].all_objects)).name]
print(o.name, list(o.keys()), o.data.name)
ks=set()
for o in bpy.data.collections["VK_ValleyTown"].all_objects: ks|=set(o.keys())
print(ks)
# ---- result ----
# {"result":"Code executed successfully: 0.6268637180328369\nSM_VK_TownWall_Straight_inst [] SM_VK_TownWall_Straight\n{'hinge_axis', 'travel', 'rpm', 's
# lide_axis', 'spin_axis'}\n"}

# ==============================================================================================================
# [0004] 2026-09-23 16:58:39  blender  ok
# ==============================================================================================================
import bpy, time
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; W=ns["rv_water_bvh"]
down=Vector((0,0,-1))
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
def wz(x,y):
    h=W.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
t0=time.time(); res={}
for o in bpy.data.collections["VK_ValleyTown"].all_objects:
    mw=o.matrix_world; bb=[mw@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys); cx,cy=(x0+x1)/2,(y0+y1)/2
    ix=min(0.35*(x1-x0),1.0); iy=min(0.35*(y1-y0),1.0)
    pts=[(cx,cy),(cx-ix,cy-iy),(cx+ix,cy-iy),(cx-ix,cy+iy),(cx+ix,cy+iy)]
    g=[gz(*p) for p in pts]
    res[o.name]=dict(bb=(x0,x1,y0,y1,min(zs),max(zs)),loc=tuple(o.location),g=g,w=wz(cx,cy),data=o.data.name)
ns["rv_res"]=res
print(time.time()-t0, len(res))
# ---- result ----
# {"result":"Code executed successfully: 0.14554953575134277 5568\n"}

# ==============================================================================================================
# [0005] 2026-09-23 16:59:04  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; res=ns["rv_res"]
down=Vector((0,0,-1))
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
nat=("Tree_","Bush_","Plant_","Rock_","Mushrooms","LipGrass","Deco_Weeds","Crop_")
out=collections.defaultdict(list)
for n,r in res.items():
    if not any(k in n for k in nat): continue
    x,y,z=r["loc"]; g=gz(x,y)
    if g is None: out["noground"].append(n); continue
    d=z-g
    # ring around trunk for trees 
    rad=0.5 if "Tree" in n else 0.3
    ring=[gz(x+dx,y+dy) for dx,dy in ((rad,0),(-rad,0),(0,rad),(0,-rad))]
    ring=[q for q in ring if q is not None]
    rng=max(ring+[g])-min(ring+[g])
    if d>0.12: out["float"].append((n,round(d,2),round(x-1500,1),round(y,1),round(z,2)))
    if d<-0.25: out["sunk"].append((n,round(d,2),round(x-1500,1),round(y,1),round(z,2)))
    if rng>0.6: out["slope"].append((n,round(rng,2),round(x-1500,1),round(y,1),round(z,2),round(g,2)))
for k,v in out.items():
    print(k,len(v))
    kinds=collections.Counter(e[0].split('_inst')[0] if isinstance(e,tuple) else e for e in v)
    print("  ",kinds.most_common(12))
ns["rv_nat"]=dict(out)
# ---- result ----
# {"result":"Code executed successfully: slope 1483\n [('SM_VKT_LipGrass', 1344), ('SM_VK_Rock_Pebbles', 42), ('SM_VK_Rock_Small_B', 41), ('SM_VK_Rock_S
# mall_A', 29), ('SM_VK_Plant_Fern', 25), ('SM_VK_Tree_Willow', 1), ('SM_VK_Mushrooms_Brown', 1)]\nfloat 894\n [('SM_VKT_LipGrass', 894)]\n"}

# ==============================================================================================================
# [0006] 2026-09-23 16:59:41  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; res=ns["rv_res"]
lg=[n for n in res if "LipGrass" in n]
ds=[]
for n in lg:
    o=bpy.data.objects[n]; p=o.location
    co,no,idx,dist=G.find_nearest(p)
    ds.append((dist,n,tuple(round(v,2) for v in p),tuple(round(v,2) for v in co)))
ds.sort(reverse=True)
import statistics
print(statistics.quantiles([d[0] for d in ds],n=10))
for d in ds[:25]: print(round(d[0],2),d[1],d[2],d[3])
print(sum(1 for d in ds if d[0]>0.4), sum(1 for d in ds if d[0]>0.8))
o=bpy.data.objects[lg[0]]; print(o.dimensions, [tuple(v) for v in o.bound_box][:2], o.data.name)
# ---- result ----
# {"result":"Code executed successfully: [0.08568738028407097, 0.0950053259730339, 0.10002287477254868, 0.10231795907020569, 0.10437943786382675, 0.1062
# 5755041837692, 0.10896981135010719, 0.113807313144207, 0.11964831501245499]\n0.15 SM_VKT_LipGrass_inst.3287 (1560.37, 149.96, 6.0) (1560.36, 150.04, 5
# .88)\n0.14 SM_VKT_LipGrass_inst.674 (1637.44, 30.02, 1.5) (1637.45, 29.94, 1.38)\n0.14 SM_VKT_LipGrass_inst.619 (1577.65, 30.12, 1.5) (1577.67, 30.04,
#  1.38)\n0.14 SM_VKT_LipGrass_inst.589 (1550.68, 30.0, 1.5) (1550.69, 29.92, 1.39)\n0.14 SM_VKT_LipGrass_inst.545 (1511.69, 29.93, 1.5) (1511.7, 29.86,
#  1.38)\n0.14 SM_VKT_LipGrass_inst.793 (1602.27, 54.2, 1.5) (1602.26, 54.27, 1.38)\n0.14 SM_VKT_LipGrass_inst.3288 (1560.81, 149.95, 6.0) (1560.82, 150
# .04, 5.89)\n0.14 SM_VKT_LipGrass_inst.520 (1673.81, 18.35, 1.5) (1673.73, 18.34, 1.39)\n0.14 SM_VKT_LipGrass_inst.833 (1668.42, 53.73, 1.5) (1668.4, 5

# ==============================================================================================================
# [0007] 2026-09-23 17:00:01  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; res=ns["rv_res"]; W=ns["rv_water_bvh"]
down=Vector((0,0,-1))
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
def wz(x,y):
    h=W.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
nat=("Tree_","Bush_","Plant_","Rock_","Mushrooms","Deco_Weeds","Crop_")
rows=[]
for n,r in res.items():
    if not any(k in n for k in nat): continue
    o=bpy.data.objects[n]; p=o.location
    g=gz(p.x,p.y); co,no,idx,dist=G.find_nearest(p)
    w=wz(p.x,p.y)
    rows.append((n,p.x,p.y,p.z,g,dist,no.z,w))
ns["rv_natrows"]=rows
# floating: origin more than 0.25 above nearest surface
fl=[r for r in rows if r[5]>0.25 and r[4] is not None and r[3]>r[4]+0.1]
print("float",len(fl))
for r in sorted(fl,key=lambda r:-r[5])[:30]: print(r[0],"xyz",round(r[1],1),round(r[2],1),round(r[3],2),"g",round(r[4],2),"dist",round(r[5],2),"nz",round(r[6],2))
# embedded in cliff: nearest surface normal steep and origin below ground
sk=[r for r in rows if r[4] is not None and r[4]-r[3]>0.3]
print("sunk",len(sk))
for r in sorted(sk,key=lambda r:r[3]-r[4])[:30]: print(r[0],"xyz",round(r[1],1),round(r[2],1),round(r[3],2),"g",round(r[4],2),"dist",round(r[5],2))
# in water
iw=[r for r in rows if r[7] is not None and r[7]>r[4]+0.05 and r[7]>r[3]]
print("inwater",len(iw))
for r in iw[:30]: print(r[0],round(r[1],1),round(r[2],1),round(r[3],2),"g",round(r[4],2),"w",round(r[7],2))
# ---- result ----
# {"result":"Code executed successfully: float 0\nsunk 0\ninwater 0\n"}

# ==============================================================================================================
# [0008] 2026-09-23 17:00:37  blender  ok
# ==============================================================================================================
import bpy, collections
ns=bpy.app.driver_namespace; res=ns["rv_res"]
nat=("Tree_","Bush_","Plant_","Rock_","Mushrooms","Deco_Weeds","Crop_","LipGrass")
hang=[];bur=[];flt=collections.defaultdict(list);nog=[]
for n,r in res.items():
    if any(k in n for k in nat): continue
    g=[q for q in r["g"] if q is not None]
    if len(g)<5: nog.append((n,r["bb"])); 
    if not g: continue
    x0,x1,y0,y1,z0,z1=r["bb"]; gmax,gmin=max(g),min(g)
    if abs(z0-gmax)<0.4 and gmax-gmin>0.8: hang.append((n,round((x0+x1)/2-1500,1),round((y0+y1)/2,1),round(z0,2),[round(q,2) for q in r["g"] if q is not None]))
    if gmax-z0>0.5 and (z1-z0)<gmax-z0+3: bur.append((n,round((x0+x1)/2-1500,1),round((y0+y1)/2,1),round(z0,2),round(z1,2),[round(q,2) for q in r["g"] if q is not None]))
    d=z0-gmax
    if 0.1<d<1.2: flt[n.split("_inst")[0]].append((n,round((x0+x1)/2-1500,1),round((y0+y1)/2,1),round(z0,2),round(d,2)))
print("nog",len(nog)); 
for e in nog[:10]: print(e)
print("hang",len(hang))
for e in hang: print(e)
print("buried",len(bur))
for e in bur[:60]: print(e)
# ---- result ----
# {"result":"Code executed successfully: nog 0\nhang 1\n('SM_VK_Wall_Stone_Window_inst.136', 82.5, 47.7, -0.11, [-0.55, -0.97, -0.97, -0.05, -0.05])\nbu
# ried 192\n('SM_VK_Bridge_Stone_Pier_inst', 126.0, 42.0, -2.0, 1.0, [-1.5, -1.5, -1.5, -1.5, -1.5])\n('SM_VK_Bridge_Stone_Ramp_inst', 126.0, 50.4, -0.6
# , 2.13, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Bridge_Stone_Ramp_inst.001', 126.0, 33.6, -0.6, 2.13, [0.0, 0.0, 0.0, 0.0, -0.0])\n('SM_VK_Bridge_Wood_End
# _inst', 37.5, 34.4, -0.79, 1.49, [0.0, -0.0, 0.0, -0.0, -0.0])\n('SM_VK_Bridge_Wood_End_inst.001', 37.5, 49.6, -0.79, 1.49, [-0.0, -0.01, -0.0, 0.0, 0
# .0])\n('SM_VK_Bridge_Wood_Bent_inst', 37.5, 36.0, -3.0, -0.02, [-0.09, -0.03, -0.04, -0.33, -0.45])\n('SM_VK_Bridge_Wood_Bent_inst.001', 37.5, 39.0, -
# 3.0, -0.02, [-1.5, -1.5, -1.5, -1.5, -1.5])\n('SM_VK_Bridge_Wood_Bent_inst.002', 37.5, 42.0, -3.0, -0.02, [-1.5, -1.5, -1.5, -1.5, -1.5])\n('SM_VK_Bri

# ==============================================================================================================
# [0009] 2026-09-23 17:01:21  blender  ok
# ==============================================================================================================
import bpy, collections
ns=bpy.app.driver_namespace; res=ns["rv_res"]
nat=("Tree_","Bush_","Plant_","Rock_","Mushrooms","Deco_Weeds","Crop_","LipGrass")
out=[]
for n,r in res.items():
    if any(k in n for k in nat): continue
    g=[q for q in r["g"] if q is not None]
    x0,x1,y0,y1,z0,z1=r["bb"]; gmax,gmin=max(g),min(g)
    if gmax-z0>0.5 and (z1-z0)<gmax-z0+3:
        if gmax-gmin<0.15 and gmax-z0<=0.66: continue
        if "Bridge" in n or "Pier" in n or "Quay" in n: continue
        out.append((n,round((x0+x1)/2-1500,1),round((y0+y1)/2,1),round(z0,2),round(z1,2),[round(q,2) for q in g]))
print(len(out))
for e in out: print(e)
# ---- result ----
# {"result":"Code executed successfully: 9\n('SM_VK_Prop_Cart_inst.008', 78.0, 59.1, 0.0, 1.42, [0.0, 0.0, 0.0, 1.41, 1.41])\n('SM_VK_Prop_Crates_inst.0
# 07', 84.3, 59.2, 0.0, 1.5, [0.0, 0.0, 0.0, 0.86, 0.86])\n('SM_VK_Prop_Laundry_inst.002', 141.2, 53.7, 0.0, 2.6, [0.44, 0.0, 0.0, 1.36, 1.36])\n('SM_VK
# _Prop_FishRack_inst', 156.9, 53.8, -0.22, 1.97, [0.84, 0.0, 0.0, 1.5, 1.5])\n('SM_VK_Prop_SawPit_inst', 111.0, 8.7, 0.3, 3.15, [1.5, 1.5, 1.5, 1.5, 1.
# 5])\n('SM_VK_Prop_TanningPit_inst', 5.6, 58.6, 0.8, 1.88, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_Prop_TanningPit_inst.001', 7.9, 58.5, 0.8, 1.88, [1.5, 1
# .5, 1.5, 1.5, 1.5])\n('SM_VK_Prop_TanningPit_inst.002', 11.9, 58.5, 0.8, 1.88, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_Prop_TanningPit_inst.003', 14.3, 58
# .5, 0.8, 1.88, [1.5, 1.5, 1.5, 1.5, 1.5])\n"}

# ==============================================================================================================
# [0010] 2026-09-23 17:02:10  blender  ok
# ==============================================================================================================
import bpy, collections
ns=bpy.app.driver_namespace; res=ns["rv_res"]
nat=("Tree_","Bush_","Plant_","Rock_","Mushrooms","Deco_Weeds","Crop_","LipGrass")
flt=collections.defaultdict(list)
for n,r in res.items():
    if any(k in n for k in nat): continue
    g=[q for q in r["g"] if q is not None]
    x0,x1,y0,y1,z0,z1=r["bb"]; gmax,gmin=max(g),min(g)
    d=z0-gmax
    if 0.08<d<1.0: flt[n.split("_inst")[0]].append((n.split("_inst")[1] or "-",round((x0+x1)/2-1500,1),round((y0+y1)/2,1),round(z0,2),round(d,2),round(gmax-gmin,2)))
for k,v in sorted(flt.items(),key=lambda kv:-len(kv[1])):
    print(k,len(v),v[:6])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_FlowerBox 33 [('.102', 77.4, 55.5, 0.55, 0.55, 0.0), ('.103', 84.6, 52.5, 0.55, 0.55, 0.0), ('.104',
#  14.0, 65.5, 2.18, 0.68, 0.0), ('.105', 16.5, 84.5, 3.78, 0.78, 0.0), ('.110', 92.5, 79.5, 3.68, 0.68, 0.0), ('.111', 115.5, 84.6, 3.56, 0.56, 0.0)]\n
# SM_VK_Prop_FlowerBox_Daisy 27 [('.021', 179.4, 10.5, 2.06, 0.56, 0.0), ('.022', 12.0, 60.5, 2.18, 0.68, 0.0), ('.023', 4.0, 62.5, 2.18, 0.68, 0.0), ('
# .024', 9.5, 79.5, 3.93, 0.93, 0.0), ('.025', 76.5, 84.6, 3.56, 0.56, 0.0), ('.026', 84.6, 79.5, 3.56, 0.56, 0.0)]\nSM_VK_Wall_Shed_Raised 7 [('-', 112
# .5, 60.0, 2.13, 0.63, 0.0), ('.001', 115.5, 66.0, 2.13, 0.63, 0.0), ('.002', 112.5, 66.0, 2.13, 0.63, 0.0), ('.003', 111.0, 64.5, 2.13, 0.63, 0.0), ('
# .004', 111.0, 61.5, 2.13, 0.63, 0.0), ('.005', 117.0, 61.5, 2.13, 0.63, 0.0)]\nSM_VK_Ceiling_Cell 4 [('-', 112.5, 61.5, 2.14, 0.64, 0.0), ('.001', 115

# ==============================================================================================================
# [0011] 2026-09-23 17:03:13  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; res=ns["rv_res"]; G=ns["rv_ground_bvh"]
down=Vector((0,0,-1))
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
nat=("Tree_","Bush_","Plant_","Rock_","Mushrooms","Deco_Weeds","Crop_","LipGrass")
out=[]
for n,r in res.items():
    if any(k in n for k in ("LipGrass",)): continue
    x0,x1,y0,y1,z0,z1=r["bb"]
    # dense sample of footprint (inset 0.15)
    pts=[]
    for fx in (0.1,0.3,0.5,0.7,0.9):
        for fy in (0.1,0.3,0.5,0.7,0.9):
            pts.append((x0+(x1-x0)*fx,y0+(y1-y0)*fy))
    g=[gz(*p) for p in pts]; g=[q for q in g if q is not None]
    gmax,gmin=max(g),min(g)
    ref=r["loc"][2]
    if z0<=gmax+0.3 and z0>=gmax-0.75 and gmin<z0-0.7:
        out.append((n,round((x0+x1)/2-1500,1),round((y0+y1)/2,1),round(z0,2),round(gmax,2),round(gmin,2),round(x1-x0,1),round(y1-y0,1)))
ns["rv_hang"]=out
print(len(out))
c=collections.Counter(e[0].split("_inst")[0] for e in out); print(c.most_common(40))
for e in out:
    if not any(k in e[0] for k in nat): print(e)
# ---- result ----
# {"result":"Code executed successfully: 323\n[('SM_VK_Tree_Pine_B', 104), ('SM_VK_Tree_Pine_A', 101), ('SM_VK_Tree_Pine_Young', 58), ('SM_VK_Bush_Round
# ', 9), ('SM_VK_Tree_Oak_B', 8), ('SM_VK_Tree_Oak_A', 8), ('SM_VK_Tree_Oak_Autumn', 8), ('SM_VK_Tree_Birch', 6), ('SM_VK_Plant_Reeds', 5), ('SM_VK_Corn
# er_Stone', 4), ('SM_VK_Tree_Willow', 3), ('SM_VK_Tree_Apple', 3), ('SM_VK_Bridge_Wood_Mid', 1), ('SM_VK_Wall_Stone_Window', 1), ('SM_VK_Prop_Woodpile'
# , 1), ('SM_VK_Prop_TreadwheelCrane', 1), ('SM_VK_Plant_TallGrass', 1), ('SM_VK_Rock_Pebbles', 1)]\n('SM_VK_Bridge_Wood_Mid_inst', 37.5, 37.5, -0.25, -
# 0.42, -1.5, 3.5, 3.1)\n('SM_VK_Wall_Stone_Window_inst.136', 82.5, 47.7, -0.11, -0.04, -1.04, 3.0, 1.1)\n('SM_VK_Corner_Stone_inst.130', 78.0, 48.0, -0
# .06, 0.0, -0.78, 1.3, 1.3)\n('SM_VK_Corner_Stone_inst.131', 84.0, 48.0, -0.06, 0.0, -0.8, 1.3, 1.3)\n('SM_VK_Corner_Stone_inst.135', 156.0, 48.0, -0.0

# ==============================================================================================================
# [0012] 2026-09-23 17:03:39  blender  ok
# ==============================================================================================================
import bpy, time
exec(bpy.data.texts["vk_render"].as_string())
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
t0=time.time()
p=shot("ground_01_mill_colony",(1581,22,30),(1581,52,0),lens=30,res=(1600,900),outdir=OD)
print(p,time.time()-t0, bpy.context.scene.render.engine)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_01_mill_colony.png 3.4530508518218994 BLENDER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0013] 2026-09-23 17:04:15  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_02_mill_sw_eye",(1573,41,1.2),(1582,49,0.0),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_03_mill_back_cart",(1570,50,4.5),(1580,59,0.5),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_02_mill_sw_eye.png\nC:\\Users\\danie\\AppData\\Roaming\\Claud
# e\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground
# \\ground_03_mill_back_cart.png\n"}

# ==============================================================================================================
# [0014] 2026-09-23 17:05:01  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_04_mill_back_crates",(1590,50,3.5),(1584,59.5,0.7),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_05_lavoir_smokehouse",(1649,40,5.5),(1649,53,0.8),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_04_mill_back_crates.png\nC:\\Users\\danie\\AppData\\Roaming\\
# Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\g
# round\\ground_05_lavoir_smokehouse.png\n"}

# ==============================================================================================================
# [0015] 2026-09-23 17:05:38  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
for n in ("SM_VK_Prop_Laundry_inst.002","SM_VK_Prop_FishRack_inst","SM_VK_Prop_Cart_inst.008","SM_VK_Prop_Crates_inst.007"):
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n, tuple(round(v,2) for v in o.location), round(o.rotation_euler.z*57.3), [round(min(v[k] for v in bb),2) for k in range(3)],[round(max(v[k] for v in bb),2) for k in range(3)])
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_06_laundry_side",(1634.5,51,2.2),(1642,54.5,1.0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Laundry_inst.002 (1641.2, 53.7, 0.0) 3 [1638.63, 53.32, 0.0] [1643.77, 54.08, 2.6]\nSM_VK_Prop_FishR
# ack_inst (1656.9, 53.8, 0.0) 185 [1655.24, 52.86, -0.22] [1658.56, 54.74, 1.97]\nSM_VK_Prop_Cart_inst.008 (1577.4, 59.3, 0.0) -20 [1576.13, 57.71, 0.0
# ] [1579.82, 60.47, 1.42]\nSM_VK_Prop_Crates_inst.007 (1583.6, 58.7, 0.0) 5 [1582.99, 58.19, 0.0] [1585.63, 60.17, 1.5]\nC:\\Users\\danie\\AppData\\Roa
# ming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rev
# iew\\ground\\ground_06_laundry_side.png\n"}

# ==============================================================================================================
# [0016] 2026-09-23 17:06:18  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_07_stonebridge_side",(1612,36,3.0),(1626,42,0.3),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_08_stonebridge_colony",(1645,20,28),(1626,44,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_07_stonebridge_side.png\nC:\\Users\\danie\\AppData\\Roaming\\
# Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\g
# round\\ground_08_stonebridge_colony.png\n"}

# ==============================================================================================================
# [0017] 2026-09-23 17:07:01  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_09_footbridge_side",(1524,42,1.6),(1537.5,42,-0.3),lens=24,res=(1600,900),outdir=OD))
print(shot("ground_10_footbridge_colony",(1556,26,26),(1537.5,42,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_09_footbridge_side.png\nC:\\Users\\danie\\AppData\\Roaming\\C
# laude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\gr
# ound\\ground_10_footbridge_colony.png\n"}

# ==============================================================================================================
# [0018] 2026-09-23 17:07:42  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_11_gate_ramp_eye",(1636,62,3.2),(1627,72,2.0),lens=26,res=(1600,900),outdir=OD))
print(shot("ground_12_ramp17_eye",(1636,46,1.8),(1627,54,0.8),lens=26,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_11_gate_ramp_eye.png\nC:\\Users\\danie\\AppData\\Roaming\\Cla
# ude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\grou
# nd\\ground_12_ramp17_eye.png\n"}

# ==============================================================================================================
# [0019] 2026-09-23 17:08:31  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; res=ns["rv_res"]
rows=[]
for n,r in res.items():
    x0,x1,y0,y1,z0,z1=r["bb"]
    if 1616<x1 and x0<1640 and 66<y1 and y0<80 and z0<4.0 and not any(k in n for k in ("LipGrass","Tree","Plant","Rock","Bush")):
        rows.append((n,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(z0,2),round(z1,2),[round(q,2) for q in r["g"]]))
for e in sorted(rows,key=lambda e:e[3]): print(e)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Wall_Shed_Raised_inst.006', 1616.8, 1617.1, 62.9, 66.0, 2.13, 4.86, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK
# _Foundation_Wall_inst.006', 1631.1, 1632.9, 63.0, 66.0, 0.9, 2.14, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_Prop_StaddleStone_inst.008', 1616.3, 1617.3, 65
# .3, 66.3, 0.9, 2.15, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_Wall_Shed_Raised_inst.001', 1614.0, 1617.1, 65.8, 66.1, 2.13, 4.86, [1.5, 1.5, 1.5, 1.5, 1.5]
# )\n('SM_VK_Corner_Shed_Raised_inst.002', 1616.8, 1617.3, 65.8, 66.3, 2.13, 4.88, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_BuildSite_Cell_inst.001', 1632.0,
#  1635.0, 66.0, 69.0, 0.9, 1.89, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_BuildSite_Cell_inst.003', 1635.0, 1638.0, 66.0, 69.0, 0.9, 1.89, [1.5, 1.5, 1.5, 1
# .5, 1.5])\n('SM_VK_BuildSite_Cell_inst.005', 1638.0, 1641.0, 66.0, 69.0, 0.9, 1.89, [1.5, 1.5, 1.5, 1.5, 1.5])\n('SM_VK_Foundation_Wall_inst.007', 163

# ==============================================================================================================
# [0020] 2026-09-23 17:09:05  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_13_gate_ramp_axis",(1626,59,3.4),(1626.5,74,3.6),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_14_gate_colony",(1640,48,26),(1627,72,2),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_13_gate_ramp_axis.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\gro
# und\\ground_14_gate_colony.png\n"}

# ==============================================================================================================
# [0021] 2026-09-23 17:09:49  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_15_westbench_wide",(1530,50,45),(1530,90,3),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_16_mine_colony",(1512,74,28),(1512,97,4),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_15_westbench_wide.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\gro
# und\\ground_16_mine_colony.png\n"}

# ==============================================================================================================
# [0022] 2026-09-23 17:11:04  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace; res=ns["rv_res"]
def area(xa,xb,ya,yb,excl=("LipGrass","Tree","Plant","Rock_Small","Rock_Pebbles","Bush","Mushroom","Fern","Weeds")):
    rows=[]
    for n,r in res.items():
        x0,x1,y0,y1,z0,z1=r["bb"]
        if xa<x1 and x0<xb and ya<y1 and y0<yb and not any(k in n for k in excl):
            rows.append((n,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(z0,2),round(z1,2),[round(q,2) for q in r["g"]]))
    return sorted(rows,key=lambda e:e[3])
for e in area(1536,1556,88,110): print(e)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_LeanTo_inst.010', 1537.3, 1540.7, 88.3, 92.3, 3.0, 6.53, [3.0, 3.0, 3.0, 3.0, 3.0])\n('SM_VK_Quarry_Fac
# e_Straight_inst.003', 1549.5, 1552.5, 91.3, 94.5, 2.4, 6.55, [3.0, 3.0, 3.0, 3.0, 3.0])\n('SM_VK_Quarry_Face_Straight_inst.004', 1537.5, 1540.5, 91.3,
#  94.5, 2.4, 6.55, [3.0, 3.0, 3.0, 3.0, 3.0])\n('SM_VK_Quarry_Face_Corner_inst', 1546.4, 1549.5, 91.4, 94.6, 2.4, 6.52, [3.0, 3.0, 3.0, 3.0, 3.0])\n('S
# M_VK_Quarry_Face_Corner_inst.001', 1540.4, 1543.6, 91.4, 94.5, 2.4, 6.52, [3.0, 3.0, 3.0, 3.0, 3.0])\n('SM_VK_Quarry_Floor_inst.001', 1543.5, 1546.5, 
# 91.5, 94.5, 2.39, 3.76, [3.0, 3.0, 3.0, 3.0, 3.0])\n('SM_VK_Pile_Stone_3_inst.001', 1545.2, 1547.9, 91.5, 92.5, 3.0, 4.18, [3.0, 3.0, 3.0, 3.0, 3.0])\
# n('SM_VK_Prop_Banker_inst', 1543.1, 1545.1, 91.8, 93.5, 2.99, 4.46, [3.0, 3.0, 3.0, 3.0, 3.0])\n('SM_VK_Prop_Wheelbarrow_inst.005', 1545.6, 1547.9, 93

# ==============================================================================================================
# [0023] 2026-09-23 17:11:37  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_17_quarry_crane_side",(1560,97,5.5),(1544.5,100,5.0),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_18_quarry_front",(1545,80,6.5),(1545,97,4.5),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_17_quarry_crane_side.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# ground\\ground_18_quarry_front.png\n"}

# ==============================================================================================================
# [0024] 2026-09-23 17:12:40  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace; res=ns["rv_res"]
for n,r in res.items():
    x0,x1,y0,y1,z0,z1=r["bb"]
    if 1503<x1 and x0<1522 and 90<y1 and y0<106 and not any(k in n for k in ("LipGrass","Tree","Plant","Rock_Small","Rock_Pebbles","Bush","Mushroom","Fern","Weeds")):
        print(n,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(z0,2),round(z1,2),[round(q,2) for q in r["g"]])
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_19_mine_eye",(1522,86,5.0),(1512,98,4.5),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Mine_Portal_inst 1507.4 1516.4 96.1 104.0 2.4 8.15 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Rail_Straight_inst 15
# 11.2 1512.8 97.5 100.5 2.7 3.22 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Rail_Straight_inst.001 1511.2 1512.8 94.5 97.5 2.7 3.22 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM
# _VK_Rail_Curve_inst 1511.2 1515.0 90.7 94.5 2.7 3.22 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Rail_End_inst 1515.0 1518.6 90.6 92.3 2.7 3.9 [3.0, 3.0, 3.0, 3.
# 0, 3.0]\nSM_VK_Prop_Minecart_inst 1511.5 1512.5 94.4 96.2 3.19 4.43 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Prop_Minecart_inst.001 1514.2 1516.0 91.0 92.0 3.
# 19 4.43 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Pile_Ore_3_inst 1517.0 1520.8 92.2 95.7 2.93 4.16 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Pile_Ore_1_inst 1513.3 151
# 5.8 93.2 95.6 2.94 3.62 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_Pile_Coal_2_inst.002 1507.0 1510.2 92.6 95.4 2.87 3.8 [3.0, 3.0, 3.0, 3.0, 3.0]\nSM_VK_LeanTo

# ==============================================================================================================
# [0025] 2026-09-23 17:13:40  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; res=ns["rv_res"]; G=ns["rv_ground_bvh"]
down=Vector((0,0,-1))
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),down,200)
    return h[0].z if h[0] else None
nat=("LipGrass","Tree_","Plant_","Rock_","Bush_","Mushrooms","Deco_Weeds","Crop_")
out=[]
for n,r in res.items():
    if any(k in n for k in nat): continue
    x0,x1,y0,y1,z0,z1=r["bb"]
    if z1-z0<0.05: continue
    g=[]
    for fx in (0.05,0.25,0.5,0.75,0.95):
        for fy in (0.05,0.25,0.5,0.75,0.95):
            q=gz(x0+(x1-x0)*fx,y0+(y1-y0)*fy)
            if q is not None: g.append(q)
    gmax=max(g); gmin=min(g)
    # piece bottom rests near the lower ground, but some footprint is >0.9 above its base and below its top => cliff intersects piece
    if gmax>z0+1.1 and gmax<z1 and gmin<z0+0.7:
        out.append((round(gmax-z0,2),n,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(z0,2),round(z1,2),round(gmin,2),round(gmax,2)))
out.sort(key=lambda e:(e[4],e[2]))
print(len(out))
for e in out: print(e)
# ---- result ----
# {"result":"Code executed successfully: 7\n(1.72, 'SM_VK_Prop_FishRack_inst', 1655.2, 1658.6, 52.9, 54.7, -0.22, 1.97, 0.0, 1.5)\n(1.41, 'SM_VK_Prop_La
# undry_inst.002', 1638.6, 1643.8, 53.3, 54.1, 0.0, 2.6, 0.0, 1.41)\n(1.42, 'SM_VK_Prop_Crates_inst.007', 1583.0, 1585.6, 58.2, 60.2, 0.0, 1.5, 0.0, 1.4
# 2)\n(1.5, 'SM_VK_Gatehouse_Block_inst', 1622.2, 1632.8, 69.7, 78.2, 1.5, 12.0, 1.5, 3.0)\n(1.5, 'SM_VK_TownWall_Tower_Round_inst', 1583.4, 1590.6, 71.
# 4, 78.6, 1.5, 15.47, 1.5, 3.0)\n(2.1, 'SM_VK_Mine_Portal_inst', 1507.4, 1516.4, 96.1, 104.0, 2.4, 8.15, 3.0, 4.5)\n(1.5, 'SM_VK_TownWall_Tower_Round_i
# nst.011', 1685.4, 1692.6, 113.4, 120.6, 1.5, 15.47, 1.5, 3.0)\n"}

# ==============================================================================================================
# [0026] 2026-09-23 17:14:20  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_20_lake_wide",(1690,-12,40),(1695,36,0),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_21_fisher_pier",(1702,16,6),(1693,26,0),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_20_lake_wide.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\
# \scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\
# ground_21_fisher_pier.png\n"}

# ==============================================================================================================
# [0027] 2026-09-23 17:15:26  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; res=ns["rv_res"]
for n,r in res.items():
    x0,x1,y0,y1,z0,z1=r["bb"]
    if 1686<x1 and x0<1700 and 22<y1 and y0<34 and not any(k in n for k in ("LipGrass","Tree","Plant","Rock","Bush","Mushroom","Weeds")):
        print(n,round(x0,2),round(x1,2),round(y0,2),round(y1,2),round(z0,2),round(z1,2))
# deck top surface: ray cast on pier deck objects
dg=bpy.context.evaluated_depsgraph_get()
sc=bpy.data.scenes["VillageKit"]
for (x,y) in ((1693.4,24.8),(1693.5,26.0),(1693.5,29.0),(1691.0,30.2)):
    hit=sc.ray_cast(dg,Vector((x,y,5)),Vector((0,0,-1)))
    print((x,y),hit[0],tuple(round(v,2) for v in hit[1]) if hit[0] else None, hit[4].name if hit[0] else None)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_RoofS_Gable_inst.002 1688.15 1692.03 16.93 22.07 2.12 5.87\nSM_VK_RoofS_Gable_inst.003 1691.97 1695.85 16
# .93 22.07 2.12 5.87\nSM_VK_Pier_Deck_inst 1691.85 1695.15 23.74 27.0 -3.0 0.37\nSM_VK_Pier_Deck_inst.001 1691.85 1695.15 26.74 30.0 -3.0 0.37\nSM_VK_P
# ier_End_inst 1691.85 1695.15 29.74 33.26 -3.01 2.51\nSM_VK_Pier_Rail_inst 1694.81 1694.99 23.92 27.0 -0.1 1.05\nSM_VK_Pier_Rail_inst.001 1694.81 1694.
# 99 26.92 30.0 -0.1 1.05\nSM_VK_Pier_Stairs_inst 1690.58 1692.1 27.66 29.34 -3.0 1.05\nSM_VK_Prop_Rowboat_inst 1689.62 1691.48 28.02 32.42 -0.86 0.08\n
# SM_VK_Prop_Creels_inst 1692.72 1695.13 30.74 32.86 0.04 0.71\nSM_VK_Pile_Fish_2_inst 1692.81 1693.97 23.88 25.65 0.04 0.41\nSM_VK_Prop_NetRack_inst 16
# 96.16 1700.01 20.51 22.47 -0.3 2.51\nSM_VK_Prop_FishRack_inst.001 1684.68 1688.12 20.33 22.47 -0.22 1.97\nSM_VK_Pile_Fish_1_inst.001 1690.09 1691.16 2

# ==============================================================================================================
# [0028] 2026-09-23 17:15:59  blender  ok
# ==============================================================================================================
import bpy, bmesh, collections
from mathutils import Vector
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[o for o in tc.objects if "Chunk" in o.name]
allb=[]
for o in chunks:
    me=o.data; mw=o.matrix_world
    cnt=collections.Counter()
    for p in me.polygons:
        for ek in p.edge_keys: cnt[ek]+=1
    bed=[ek for ek,c in cnt.items() if c==1]
    nm=[ek for ek,c in cnt.items() if c>2]
    xs=[ (mw@v.co).x for v in me.vertices]; ys=[(mw@v.co).y for v in me.vertices]
    bx=(min(xs),max(xs),min(ys),max(ys))
    interior=[]
    for (a,b) in bed:
        pa=mw@me.vertices[a].co; pb=mw@me.vertices[b].co
        m=(pa+pb)/2
        if min(abs(m.x-bx[0]),abs(m.x-bx[1]),abs(m.y-bx[2]),abs(m.y-bx[3]))>0.05:
            interior.append((round(m.x,2),round(m.y,2),round(m.z,2)))
    allb.append((o.name,len(bed),len(nm),len(interior),tuple(round(v,1) for v in bx)))
    if interior: bpy.app.driver_namespace.setdefault("rv_holes",{})[o.name]=interior
for a in allb: print(a)
# ---- result ----
# {"result":"Code executed successfully: ('VKV_Chunk_0_0', 7040, 0, 6986, (1498.3, 1546.7, -1.7, 46.7))\n('VKV_Chunk_1_0', 7040, 0, 7004, (1546.3, 1594.
# 7, -1.7, 46.7))\n('VKV_Chunk_2_0', 7028, 0, 6977, (1594.2, 1642.5, -1.7, 46.8))\n('VKV_Chunk_3_0', 7300, 0, 7281, (1642.3, 1690.6, -1.7, 46.7))\n('VKV
# _Chunk_4_0', 3960, 0, 3915, (1690.4, 1717.7, -1.5, 46.7))\n('VKV_Chunk_0_1', 7732, 0, 7686, (1498.3, 1546.6, 46.3, 94.7))\n('VKV_Chunk_1_1', 7912, 0, 
# 7878, (1546.4, 1594.7, 46.4, 94.7))\n('VKV_Chunk_2_1', 7720, 0, 7691, (1594.4, 1642.7, 46.4, 94.7))\n('VKV_Chunk_3_1', 7808, 0, 7603, (1642.5, 1690.7,
#  46.3, 94.5))\n('VKV_Chunk_4_1', 4302, 0, 4263, (1690.3, 1717.7, 46.4, 94.5))\n('VKV_Chunk_0_2', 9092, 8, 9073, (1498.3, 1546.7, 94.3, 142.7))\n('VKV_
# Chunk_1_2', 8560, 0, 8510, (1546.3, 1594.7, 94.3, 142.7))\n('VKV_Chunk_2_2', 6848, 0, 6702, (1594.3, 1642.5, 94.5, 142.8))\n('VKV_Chunk_3_2', 7512, 0,

# ==============================================================================================================
# [0029] 2026-09-23 17:16:28  blender  ok
# ==============================================================================================================
import bpy, collections, time
from mathutils import Vector
t0=time.time()
tc=bpy.data.collections["VK_ValleyTerrain"]
chunks=[o for o in tc.objects if "Chunk" in o.name]
cnt=collections.Counter()
def key(v): return (round(v.x,2),round(v.y,2),round(v.z,2))
for o in chunks:
    me=o.data; mw=o.matrix_world
    wv=[key(mw@v.co) for v in me.vertices]
    for p in me.polygons:
        for (a,b) in p.edge_keys:
            ka,kb=wv[a],wv[b]
            if ka==kb: continue
            cnt[(ka,kb) if ka<kb else (kb,ka)]+=1
bed=[e for e,c in cnt.items() if c==1]
over=[e for e,c in cnt.items() if c>2]
# exclude outer map boundary
def inner(e):
    m=((e[0][0]+e[1][0])/2,(e[0][1]+e[1][1])/2)
    return 1500.3<m[0]<1715.7 and 0.3<m[1]<167.7
ib=[e for e in bed if inner(e)]
print(len(cnt),len(bed),len(ib),len(over),time.time()-t0)
# cluster interior boundary edges into 3m cells
cl=collections.Counter()
for e in ib:
    m=((e[0][0]+e[1][0])/2,(e[0][1]+e[1][1])/2,(e[0][2]+e[1][2])/2)
    cl[(int((m[0]-1500)//3),int(m[1]//3))]+=1
print(len(cl)); print(cl.most_common(60))
bpy.app.driver_namespace["rv_ib"]=ib
# ---- result ----
# {"result":"Code executed successfully: 511545 12386 10375 84 1.7268397808074951\n739\n[((59, 47), 49), ((60, 47), 45), ((18, 34), 44), ((54, 47), 40),
#  ((56, 47), 39), ((30, 47), 38), ((28, 47), 37), ((58, 47), 37), ((66, 47), 37), ((12, 34), 36), ((13, 34), 36), ((14, 34), 36), ((15, 34), 36), ((16,
#  34), 36), ((17, 34), 36), ((25, 47), 36), ((27, 47), 36), ((29, 47), 36), ((57, 47), 35), ((62, 47), 35), ((65, 47), 35), ((26, 47), 34), ((55, 47), 
# 34), ((9, 47), 32), ((67, 51), 30), ((11, 34), 29), ((33, 47), 29), ((2, 49), 28), ((53, 49), 28), ((19, 41), 27), ((61, 47), 27), ((57, 18), 26), ((2
# 4, 47), 26), ((1, 50), 26), ((57, 9), 25), ((30, 18), 25), ((19, 34), 25), ((31, 47), 25), ((32, 47), 25), ((34, 47), 25), ((35, 47), 25), ((36, 47), 
# 25), ((41, 48), 25), ((52, 50), 25), ((49, 51), 25), ((68, 51), 25), ((63, 24), 24), ((8, 34), 24), ((67, 47), 24), ((69, 47), 24), ((66, 51), 24), ((

# ==============================================================================================================
# [0030] 2026-09-23 17:16:57  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_22_north_edge_e",(1700,132,9),(1682,143,4.5),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_23_west_ridge_cliff",(1547,90,8),(1540,104,4.5),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_22_north_edge_e.png\nC:\\Users\\danie\\AppData\\Roaming\\Clau
# de\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\groun
# d\\ground_23_west_ridge_cliff.png\n"}

# ==============================================================================================================
# [0031] 2026-09-23 17:17:43  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_24_north_edge_colony",(1680,118,30),(1680,146,5),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_25_nw_corner_colony",(1560,112,32),(1555,140,6),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_24_north_edge_colony.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# ground\\ground_25_nw_corner_colony.png\n"}

# ==============================================================================================================
# [0032] 2026-09-23 17:18:29  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; res=ns["rv_res"]
trees=[]; blds=[]
for n,r in res.items():
    if "Tree_" in n: trees.append((n,r))
    elif any(k in n for k in ("Wall","Corner","Roof","Tower","Gatehouse","Chimney","Porch","Mill","Windmill","Granary","LeanTo","Shed","Quarry","Mine","Stall","Palisade","Pottery","Kiln")) and not any(k in n for k in ("Ivy","Deco","Banner","FlowerBox","Lantern")):
        blds.append((n,r))
print(len(trees),len(blds))
import numpy as np
B=np.array([r["bb"] for n,r in blds])
trunk=[];canopy=collections.defaultdict(list)
for n,r in trees:
    o=bpy.data.objects[n]; x,y,z=o.location
    x0,x1,y0,y1,z0,z1=r["bb"]; h=z1-z0; rad=0.5*min(x1-x0,y1-y0)
    # trunk: point column from z+0.3 to z+0.35h
    m=(B[:,0]<x)&(B[:,1]>x)&(B[:,2]<y)&(B[:,3]>y)&(B[:,4]<z+0.35*h)&(B[:,5]>z+0.3)
    if m.any(): trunk.append((n,round(x,1),round(y,1),round(z,1),[blds[k][0] for k in np.nonzero(m)[0]][:3]))
    s=0.45*rad
    m2=(B[:,0]<x+s)&(B[:,1]>x-s)&(B[:,2]<y+s)&(B[:,3]>y-s)&(B[:,4]<z+0.85*h)&(B[:,5]>z+0.45*h)
    if m2.any():
        for k in np.nonzero(m2)[0]: canopy[n].append(blds[k][0])
print("trunk in building:",len(trunk))
for t in trunk: print(t)
print("canopy core in building:",len(canopy))
for n,v in list(canopy.items())[:60]:
    o=bpy.data.objects[n]; print(n,tuple(round(c,1) for c in o.location),sorted(set(k.split('_inst')[0] for k in v))[:4])
# ---- result ----
# {"result":"Code executed successfully: 1241 1414\ntrunk in building: 9\n('SM_VK_Tree_Oak_B_inst.023', 1601.3, 74.4, 3.0, ['SM_VK_TownWall_Straight_ins
# t.020'])\n('SM_VK_Tree_Apple_inst.009', 1619.4, 74.0, 3.0, ['SM_VK_TownWall_Straight_inst.032'])\n('SM_VK_Tree_Birch_inst.014', 1655.0, 73.4, 3.0, ['S
# M_VK_TownWall_Straight_inst.053'])\n('SM_VK_Tree_Birch_inst.016', 1670.2, 74.0, 3.0, ['SM_VK_TownWall_Straight_inst.063', 'SM_VK_TownWall_Tower_Round_
# inst.006'])\n('SM_VK_Tree_Oak_A_inst.036', 1567.5, 117.5, 3.0, ['SM_VK_TownWall_Straight_inst.105', 'SM_VK_TownWall_Tower_Round_inst.010'])\n('SM_VK_T
# ree_Oak_A_inst.042', 1570.3, 139.2, 3.0, ['SM_VK_TownWall_Straight_inst.001'])\n('SM_VK_Tree_Oak_A_inst.043', 1592.6, 138.8, 3.0, ['SM_VK_TownWall_Str
# aight_inst.015'])\n('SM_VK_Tree_Birch_inst.033', 1679.4, 139.2, 3.0, ['SM_VK_TownWall_Straight_inst.070'])\n('SM_VK_Tree_Oak_A_inst.044', 1687.8, 138.

# ==============================================================================================================
# [0033] 2026-09-23 17:19:07  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_26_southwall_tree_oak",(1596,64,4.5),(1601.3,74.4,4.5),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_27_southwall_trees_birch",(1662,62,5.0),(1657,74,5.0),lens=26,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_26_southwall_tree_oak.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\
# \ground\\ground_27_southwall_trees_birch.png\n"}

# ==============================================================================================================
# [0034] 2026-09-23 17:20:01  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_26_southwall_tree_oak",(1609,62,13),(1601.3,74.4,5),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_27_southwall_trees_birch",(1664,60,15),(1657,74,5.0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_26_southwall_tree_oak.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\
# \ground\\ground_27_southwall_trees_birch.png\n"}

# ==============================================================================================================
# [0035] 2026-09-23 17:20:59  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_28_west_stair_eye",(1530,90,5.2),(1525.5,101,4.0),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_29_west_ramp23_eye",(1538,62,3.2),(1530,71,2.2),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_28_west_stair_eye.png\nC:\\Users\\danie\\AppData\\Roaming\\Cl
# aude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\gro
# und\\ground_29_west_ramp23_eye.png\n"}

# ==============================================================================================================
# [0036] 2026-09-23 17:22:06  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_30_west_ramp23_close",(1533,66,2.6),(1530,71.5,2.2),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_31_west_stair_top",(1527,95,6.5),(1525.5,101.5,4.2),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_30_west_ramp23_close.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# ground\\ground_31_west_stair_top.png\n"}

# ==============================================================================================================
# [0037] 2026-09-23 17:22:48  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace; res=ns["rv_res"]
for n in ("SM_VK_Prop_SawPit_inst","SM_VK_Prop_TanningPit_inst","SM_VK_Prop_TanningPit_inst.002"):
    r=res[n]; print(n,[round(v,2) for v in r["bb"]])
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_32_sawpit",(1616,2,5.5),(1611,8.7,1.6),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_33_tanning_pits",(1510,52,5.5),(1510,58.5,1.6),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_SawPit_inst [1608.97, 1613.03, 7.31, 10.11, 0.3, 3.15]\nSM_VK_Prop_TanningPit_inst [1504.4, 1506.75,
#  57.38, 59.73, 0.8, 1.88]\nSM_VK_Prop_TanningPit_inst.002 [1510.78, 1513.12, 57.3, 59.65, 0.8, 1.88]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scra
# tch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\groun
# d_32_sawpit.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4
# 348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_33_tanning_pits.png\n"}

# ==============================================================================================================
# [0038] 2026-09-23 17:23:31  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_34_south_east_colony",(1668,-10,30),(1668,18,0),lens=30,res=(1600,900),outdir=OD))
print(shot("ground_35_hamlet_colony",(1530,-14,30),(1530,14,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_34_south_east_colony.png\nC:\\Users\\danie\\AppData\\Roaming\
# \Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\
# ground\\ground_35_hamlet_colony.png\n"}

# ==============================================================================================================
# [0039] 2026-09-23 17:24:14  blender  ok
# ==============================================================================================================
import bpy
ns=bpy.app.driver_namespace; res=ns["rv_res"]
import collections
rows=[]
for n,r in res.items():
    x0,x1,y0,y1,z0,z1=r["bb"]
    if 1672<x1 and x0<1700 and -1<y1 and y0<20 and not any(k in n for k in ("LipGrass","Tree","Plant","Rock","Bush","Mushroom","Weeds","Roof")):
        g=[q for q in r["g"]]
        rows.append((n,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(z0,2),round(z1,2),[round(q,2) for q in g]))
for e in sorted(rows,key=lambda e:(e[3],e[1])): 
    if min(e[7])<1.2 or e[5]<0.9: print(e)
print(len(rows))
# level grid lookup of ground at a few points
from mathutils import Vector
G=ns["rv_ground_bvh"]
for y in (12,14,15,16,17,18):
    print(y,[round(G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200)[0].z,1) for x in range(1672,1700,2)])
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Prop_BarrelStack_inst.011', 1686.8, 1688.8, 16.5, 17.6, 0.0, 1.5, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_P
# rop_Crates_inst.010', 1695.9, 1698.7, 16.9, 19.0, 0.0, 1.5, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Corner_Shed_inst.002', 1688.7, 1689.2, 17.7, 18.2, -0.
# 61, 2.61, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Corner_Shed_inst.003', 1694.8, 1695.3, 17.7, 18.2, -0.61, 2.61, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Wall
# _Shed_inst', 1688.9, 1692.0, 17.8, 18.2, -0.61, 2.6, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Wall_Shed_inst.001', 1691.9, 1695.0, 17.8, 18.2, -0.61, 2.6, 
# [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Wall_Shed_Window_inst.001', 1694.8, 1695.5, 17.9, 21.0, -0.61, 2.6, [0.0, 0.0, 0.0, 0.0, 0.0])\n('SM_VK_Wall_Shed_
# inst.002', 1688.8, 1689.2, 18.0, 21.1, -0.61, 2.6, [0.0, 0.0, 0.0, 0.0, 0.0])\n75\n12 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5

# ==============================================================================================================
# [0040] 2026-09-23 17:24:50  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; W=ns["rv_water_bvh"]
down=Vector((0,0,-1))
Lg=[];Wg=[]
for j in range(56):
    row="";
    for i in range(72):
        x=1500+3*i+1.5; y=3*j+1.5
        h=G.ray_cast(Vector((x,y,60)),down,200); w=W.ray_cast(Vector((x,y,60)),down,200)
        z=h[0].z if h[0] else None
        if w[0] and (z is None or w[0].z>z+0.05): row+="~"
        elif z is None: row+="?"
        else:
            l=z/1.5
            row+= str(int(round(l))) if abs(l-round(l))<0.05 else "/"
    Lg.append(row)
ns["rv_levelmap"]=Lg
for j in range(55,-1,-1): print("%2d %s"%(j,Lg[j]))
# ---- result ----
# {"result":"Code executed successfully: 55 555555555555555555544444555555555555555554455555555555555555555555555544\n54 5555555555555555555544444455555
# 55555555544444455555555555555555555555554\n53 555555555555555555554444444555555555555544333444555555555555555555555554\n52 555555555554445555544444444
# 455555555555544333334455555555555555555555544\n51 555555555544444444444444444444555555555544333333344555555555544444444444\n50 45555555554433333344444
# 4444444445555555544333333334455555555544433333444\n49 345555555544333333333444444444444455555544333333333345555555544333333333\n48 3344555555443333333
# 33334444444444444444444333333333334455555544333333333\n47 333445555544333333333333344444433333333333333333333333445555544333333333\n46 444444444334444
# 444432222222222222222222222222222222222222222222211111111\n45 444444444334444444432222222222222222222222222222222222222222222211111111\n44 44444444433

# ==============================================================================================================
# [0041] 2026-09-23 17:25:19  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; W=ns["rv_water_bvh"]
down=Vector((0,0,-1))
dry=collections.Counter(); ex=[]
x=1500.1
while x<1716:
    y=0.1
    while y<60:
        h=G.ray_cast(Vector((x,y,60)),down,200); w=W.ray_cast(Vector((x,y,60)),down,200)
        if h[0] and h[0].z< -0.65 and not w[0]:
            dry[(int((x-1500)//3),int(y//3))]+=1
            if len(ex)<30: ex.append((round(x,1),round(y,1),round(h[0].z,2)))
        y+=0.25
    x+=0.25
print(len(dry), dry.most_common(40)); print(ex)
# water level stats
zs=collections.Counter()
for o in [o for o in bpy.data.collections["VK_ValleyTerrain"].objects if "Water" in o.name]:
    for v in o.data.vertices: zs[round((o.matrix_world@v.co).z,2)]+=1
print(zs.most_common(8))
# ---- result ----
# {"result":"Code executed successfully: 0 []\n[]\n[(-0.6, 1772)]\n"}

# ==============================================================================================================
# [0042] 2026-09-23 17:25:35  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_36_river_west_mapedge",(1492,28,9),(1503,42,-0.5),lens=26,res=(1600,900),outdir=OD))
print(shot("ground_37_lake_east_mapedge",(1726,22,7),(1714,36,-0.5),lens=26,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_36_river_west_mapedge.png\nC:\\Users\\danie\\AppData\\Roaming
# \\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\
# \ground\\ground_37_lake_east_mapedge.png\n"}

# ==============================================================================================================
# [0043] 2026-09-23 17:26:29  blender  ok
# ==============================================================================================================
import bpy, collections
ns=bpy.app.driver_namespace; res=ns["rv_res"]
out=collections.defaultdict(list)
for n,r in res.items():
    if not any(k in n for k in ("Prop_","Pile_","Stall","Cart","Crate","Barrel","Well","Market","Lamp","Bench","Trough","Fence","Palisade","LowWall","Hedge","Stockpile","BuildSite","Scaffold","Banner_Pole","Stocks")): continue
    x0,x1,y0,y1,z0,z1=r["bb"]; g=[q for q in r["g"] if q is not None]
    gmin=min(g); gmax=max(g)
    d=z0-gmin
    if d< -0.12 and gmax-gmin<0.2: out["sunk"].append((n,round(x0-1500,1),round(y0,1),round(z0,2),round(gmin,2),round(z1-z0,2)))
for k,v in out.items():
    c=collections.Counter(e[0].split("_inst")[0] for e in v)
    print(k,len(v),c.most_common(40))
    for e in v[:80]: print(e)
# ---- result ----
# {"result":"Code executed successfully: sunk 99 [('SM_VK_BuildSite_Cell', 18), ('SM_VK_Palisade_Straight', 17), ('SM_VK_Deco_Hedge', 10), ('SM_VK_Prop_
# StaddleStone', 9), ('SM_VK_Palisade_Walk', 5), ('SM_VK_Banner_Pole', 4), ('SM_VK_Prop_TanningPit', 4), ('SM_VK_Palisade_Post', 3), ('SM_VK_Pile_Coal_2
# ', 3), ('SM_VK_Palisade_Tower', 2), ('SM_VK_Prop_MarketCross', 2), ('SM_VK_Prop_Stocks', 2), ('SM_VK_Prop_LavoirBasin', 1), ('SM_VK_Prop_NetRack', 1),
#  ('SM_VK_Prop_FishRack', 1), ('SM_VK_Prop_Privy', 1), ('SM_VK_Prop_SawPit', 1), ('SM_VK_Palisade_Gate', 1), ('SM_VK_Palisade_Diag', 1), ('SM_VK_Prop_B
# eacon', 1), ('SM_VK_Prop_BottleKiln', 1), ('SM_VK_Prop_ClayPit', 1), ('SM_VK_Prop_Dovecote', 1), ('SM_VK_Prop_GranaryStep', 1), ('SM_VK_Prop_CharcoalM
# ound', 1), ('SM_VK_Pile_Coal_1', 1), ('SM_VK_Prop_Bloomery', 1), ('SM_VK_Prop_CellarHatch', 1), ('SM_VK_Prop_Maypole', 1), ('SM_VK_Prop_Stage', 1), ('

# ==============================================================================================================
# [0044] 2026-09-23 17:27:03  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; nat=ns["rv_nat"]
for e in nat.get("slope",[]):
    if "Willow" in e[0] or "Mushroom" in e[0]: print(e)
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return round(h[0].z,2) if h[0] else None
# trees whose trunk is within 0.9 m (ring) of a >1m drop or rise
out=[]
for n,r in ns["rv_res"].items():
    if "Tree_" not in n: continue
    o=bpy.data.objects[n]; x,y,z=o.location
    ring=[gz(x+dx,y+dy) for dx,dy in ((0.9,0),(-0.9,0),(0,0.9),(0,-0.9),(0.64,0.64),(-0.64,0.64),(0.64,-0.64),(-0.64,-0.64))]
    ring=[q for q in ring if q is not None]
    hi=max(ring)-z; lo=z-min(ring)
    if hi>0.9 or lo>0.9: out.append((n,round(x,1),round(y,1),round(z,1),round(hi,2),round(lo,2)))
print(len(out))
for e in out[:40]: print(e)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Tree_Willow_inst.017', 1.03, 93.8, 53.5, 0.0, 0.0)\n('SM_VK_Mushrooms_Brown_inst.080', 0.86, 120.6, 161
# .5, 6.0, 6.0)\n5\n('SM_VK_Tree_Willow_inst.005', 1622.3, 30.8, 0.0, 1.36, 0.0)\n('SM_VK_Tree_Willow_inst.017', 1593.8, 53.5, 0.0, 1.49, 0.0)\n('SM_VK_
# Tree_Willow_inst.018', 1675.0, 56.0, 0.0, 1.36, 0.0)\n('SM_VK_Tree_Oak_B_inst.041', 1528.5, 139.7, 4.5, 2.32, 0.0)\n('SM_VK_Tree_Oak_A_inst.040', 1529
# .2, 139.9, 4.5, 2.32, 0.0)\n"}

# ==============================================================================================================
# [0045] 2026-09-23 17:27:34  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_38_quay_eye",(1597,38,1.3),(1605,48,0.0),lens=26,res=(1600,900),outdir=OD))
print(shot("ground_39_willow_cliff",(1590,47,2.6),(1593.8,53.8,1.0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_38_quay_eye.png\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\
# scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\g
# round_39_willow_cliff.png\n"}

# ==============================================================================================================
# [0046] 2026-09-23 17:28:16  blender  ok
# ==============================================================================================================
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ns=bpy.app.driver_namespace; res=ns["rv_res"]
b=res["SM_VK_Prop_Barge_inst"]["bb"]; print("barge",[round(v,2) for v in b])
for n,r in res.items():
    if "Quay" in n or "Willow" in n:
        x0,x1,y0,y1,z0,z1=r["bb"]
        if x1>1595 and x0<1615: print(n,[round(v,2) for v in r["bb"]])
def wbvh(o):
    mw=o.matrix_world; me=o.data
    return BVHTree.FromPolygons([mw@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
bg=wbvh(bpy.data.objects["SM_VK_Prop_Barge_inst"])
for n in [k for k in res if "Quay_Straight" in k or "Quay_Stair" in k]:
    ov=bg.overlap(wbvh(bpy.data.objects[n]))
    if ov: print("overlap",n,len(ov))
# ---- result ----
# {"result":"Code executed successfully: barge [1598.84, 1608.87, 44.13, 48.25, -0.98, 4.6]\nSM_VK_Quay_Straight_inst.004 [1599.0, 1602.0, 47.89, 48.9, 
# -2.0, 0.03]\nSM_VK_Quay_Straight_inst.005 [1602.0, 1605.0, 47.89, 48.9, -2.0, 0.03]\nSM_VK_Quay_Stair_inst [1605.0, 1608.0, 47.61, 48.91, -2.0, 0.08]\
# nSM_VK_Quay_Straight_inst.006 [1608.0, 1611.0, 47.89, 48.9, -2.0, 0.03]\nSM_VK_Quay_Post_inst.001 [1598.67, 1599.34, 48.4, 49.11, -0.6, 1.18]\nSM_VK_Q
# uay_Post_inst.002 [1610.67, 1611.34, 48.4, 49.11, -0.6, 1.18]\nSM_VK_Tree_Willow_inst.004 [1588.54, 1600.01, 25.67, 37.23, -0.43, 4.6]\nSM_VK_Tree_Wil
# low_inst.010 [1605.29, 1615.26, 30.47, 40.28, -0.43, 4.6]\nSM_VK_Tree_Willow_inst.013 [1602.35, 1611.33, 45.2, 53.98, -0.43, 4.6]\nSM_VK_Tree_Willow_i
# nst.017 [1588.06, 1599.57, 47.69, 59.28, -0.43, 4.6]\noverlap SM_VK_Quay_Stair_inst 6\n"}

# ==============================================================================================================
# [0047] 2026-09-23 17:31:01  blender  ok
# ==============================================================================================================
import bpy
for n in ("SM_VK_Tree_Willow_inst.013","SM_VK_Tree_Willow_inst.017","SM_VK_Tree_Willow_inst.005","SM_VK_Tree_Willow_inst.018"):
    o=bpy.data.objects[n]; print(n,tuple(round(v,2) for v in o.location), tuple(round(v,2) for v in o.scale))
# props near the quay apron
ns=bpy.app.driver_namespace; res=ns["rv_res"]
for n,r in res.items():
    x0,x1,y0,y1,z0,z1=r["bb"]
    if 1597<x1 and x0<1612 and 48.9<y1 and y0<54 and "LipGrass" not in n: print(n,[round(v,2) for v in r["bb"]])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Willow_inst.013 (1606.87, 49.59, 0.0) (1.0, 1.0, 1.0)\nSM_VK_Tree_Willow_inst.017 (1593.8, 53.45, 0.
# 0) (1.0, 1.0, 1.0)\nSM_VK_Tree_Willow_inst.005 (1622.3, 30.85, 0.0) (1.0, 1.0, 1.0)\nSM_VK_Tree_Willow_inst.018 (1674.98, 56.04, 0.0) (1.0, 1.0, 1.0)\
# nSM_VK_Quay_Straight_inst.004 [1599.0, 1602.0, 47.89, 48.9, -2.0, 0.03]\nSM_VK_Quay_Straight_inst.005 [1602.0, 1605.0, 47.89, 48.9, -2.0, 0.03]\nSM_VK
# _Quay_Stair_inst [1605.0, 1608.0, 47.61, 48.91, -2.0, 0.08]\nSM_VK_Quay_Straight_inst.006 [1608.0, 1611.0, 47.89, 48.9, -2.0, 0.03]\nSM_VK_Quay_Post_i
# nst.001 [1598.67, 1599.34, 48.4, 49.11, -0.6, 1.18]\nSM_VK_Quay_Post_inst.002 [1610.67, 1611.34, 48.4, 49.11, -0.6, 1.18]\nSM_VK_Prop_Crates_inst.008 
# [1600.28, 1603.05, 49.86, 52.03, 0.0, 1.5]\nSM_VK_Prop_Sacks_inst.007 [1604.73, 1605.85, 49.95, 50.97, -0.01, 1.26]\nSM_VK_Prop_BarrelStack_inst.009 [

# ==============================================================================================================
# [0048] 2026-09-23 17:31:26  blender  ok
# ==============================================================================================================
import bpy, collections
import numpy as np
ns=bpy.app.driver_namespace; res=ns["rv_res"]
natk=("Tree_","Bush_","Plant_","Rock_","Mushrooms","LipGrass")
nat=[(n,r) for n,r in res.items() if any(k in n for k in natk)]
oth=[(n,r) for n,r in res.items() if not any(k in n for k in natk) and not any(k in n for k in ("Deco_Weeds","Crop_","Ivy","FlowerBox","Banner_Wall","Lantern"))]
B=np.array([r["bb"] for n,r in oth]); sh=0.15
hits=collections.defaultdict(list)
for n,r in nat:
    o=bpy.data.objects[n]; x,y,z=o.location
    m=(B[:,0]+sh<x)&(B[:,1]-sh>x)&(B[:,2]+sh<y)&(B[:,3]-sh>y)&(B[:,4]<z+0.4)&(B[:,5]>z+0.1)
    if m.any():
        hits[n.split("_inst")[0]].append((n,round(x,1),round(y,1),round(z,1),[oth[k][0] for k in np.nonzero(m)[0]][:3]))
tot=sum(len(v) for v in hits.values()); print(tot)
for k,v in sorted(hits.items(),key=lambda kv:-len(kv[1])):
    print(k,len(v))
    for e in v[:12]: print("   ",e)
# ---- result ----
# {"result":"Code executed successfully: 90\nSM_VKT_LipGrass 64\n ('SM_VKT_LipGrass_inst.925', 1583.8, 72.1, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n
#  ('SM_VKT_LipGrass_inst.926', 1584.9, 72.1, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n ('SM_VKT_LipGrass_inst.927', 1585.5, 72.1, 3.0, ['SM_VK_TownWa
# ll_Tower_Round_inst'])\n ('SM_VKT_LipGrass_inst.928', 1586.9, 72.1, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n ('SM_VKT_LipGrass_inst.929', 1587.3, 7
# 2.1, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n ('SM_VKT_LipGrass_inst.930', 1588.1, 72.2, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n ('SM_VKT_LipGr
# ass_inst.931', 1588.8, 72.2, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n ('SM_VKT_LipGrass_inst.932', 1589.3, 72.2, 3.0, ['SM_VK_TownWall_Tower_Round_
# inst'])\n ('SM_VKT_LipGrass_inst.933', 1589.9, 72.1, 3.0, ['SM_VK_TownWall_Tower_Round_inst'])\n ('SM_VKT_LipGrass_inst.934', 1608.2, 72.1, 3.0, ['SM_

# ==============================================================================================================
# [0049] 2026-09-23 17:31:43  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_40_tower_on_lip",(1593,65.5,3.3),(1587,72,2.4),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_40_tower_on_lip.png\n"}

# ==============================================================================================================
# [0050] 2026-09-23 17:32:20  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_41_smokehouse_river",(1652,40,0.6),(1658,48.5,0.3),lens=28,res=(1600,900),outdir=OD))
print(shot("ground_42_mill_se_corner",(1590,41,0.6),(1584,48.3,0.0),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_41_smokehouse_river.png\nC:\\Users\\danie\\AppData\\Roaming\\
# Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\g
# round\\ground_42_mill_se_corner.png\n"}

# ==============================================================================================================
# [0051] 2026-09-23 17:33:03  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return round(h[0].z,2) if h[0] else None
for x in (1534.5,1537.5,1540.5):
    print(x,"S",[gz(x,y/2) for y in range(54,72)])
    print(x,"N",[gz(x,y/2) for y in range(96,114)])
# road ramps for comparison at x=1626
print("road S",[gz(1626,y/2) for y in range(54,72)])
print("road N",[gz(1626,y/2) for y in range(96,114)])
print("road 23",[gz(1626,y/2) for y in range(132,150)])
print("gate x-profile y=71",[ (x/2,gz(x/2,71)) for x in range(3240,3270)])
# ---- result ----
# {"result":"Code executed successfully: 1534.5 S [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.42, -0.0, 0.0, 0.0, 0.0, -0.0, 0.0, -0.0, -0.0, -0.0, 0.0, -0.0]\n153
# 4.5 N [-0.47, -0.02, -0.0, 0.0, -0.0, 0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.49, 1.46, 1.5, 1.5, 1.5, 1.5, 1.5]\n1537.5 S [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1
# .42, -0.0, 0.0, 0.0, -0.0, -0.0, -0.0, 0.0, -0.0, 0.0, -0.0, 0.0]\n1537.5 N [-0.4, -0.01, 0.0, 0.0, -0.0, 0.0, -0.0, -0.0, 0.0, -0.0, 0.0, 0.5, 1.46, 
# 1.5, 1.5, 1.5, 1.5, 1.5]\n1540.5 S [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.43, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, -0.01]\n1540.5 N [-0.29, -0
# .0, 0.0, -0.0, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.51, 1.45, 1.5, 1.5, 1.5, 1.5, 1.5]\nroad S [1.5, 1.5, 1.5, 1.5, 1.25, 1.0, 0.75, 0.5, 0.25, 0.0,
#  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]\nroad N [-0.4, -0.01, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.5, 1.5]\nr

# ==============================================================================================================
# [0052] 2026-09-23 17:33:51  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return round(h[0].z,2) if h[0] else None
for x in (1624.0,1625.0,1626.0,1627.5,1628.5,1629.0):
    print(x,[gz(x,y/2) for y in range(138,152)])
# what's hit first from above along the gate axis (scene ray cast, all objects)
for x in (1624.0,1625.5,1627.0,1628.5,1629.5):
    row=[]
    for y in (70.0,71.0,72.0,73.0):
        hit=sc.ray_cast(dg,Vector((x,y,6.0)),Vector((0,0,-1)))
        row.append((y,round(hit[1].z,2) if hit[0] else None, hit[4].name[:22] if hit[0] else None))
    print(x,row)
# ---- result ----
# {"result":"Code executed successfully: 1624.0 [1.5, 1.5, 1.5, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0]\n1625.0 [1.5, 1.5, 1.5, 1.5, 1
# .75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0]\n1626.0 [1.5, 1.5, 1.5, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0]\n1627.5 [1.5, 1.
# 5, 1.5, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0]\n1628.5 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2.88, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]\n162
# 9.0 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2.88, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]\n1624.0 [(70.0, 3.34, 'SM_VK_Gatehouse_Block_'), (71.0, 1.75, 'VKV_Chunk_2
# _1'), (72.0, 2.25, 'VKV_Chunk_2_1'), (73.0, 2.75, 'VKV_Chunk_2_1')]\n1625.5 [(70.0, 3.33, 'SM_VK_Gatehouse_Block_'), (71.0, 1.75, 'VKV_Chunk_2_1'), (7
# 2.0, 2.25, 'VKV_Chunk_2_1'), (73.0, 2.75, 'VKV_Chunk_2_1')]\n1627.0 [(70.0, 1.5, 'VKV_Chunk_2_1'), (71.0, 1.75, 'VKV_Chunk_2_1'), (72.0, 3.04, 'SM_VK_

# ==============================================================================================================
# [0053] 2026-09-23 17:34:09  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_43_gate_threshold",(1630.5,66.5,3.4),(1626.8,72.3,2.3),lens=32,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_43_gate_threshold.png\n"}

# ==============================================================================================================
# [0054] 2026-09-23 17:34:44  blender  ok
# ==============================================================================================================
import bpy, collections
ns=bpy.app.driver_namespace; res=ns["rv_res"]
out=[]
for n,r in res.items():
    x0,x1,y0,y1,z0,z1=r["bb"]
    o=bpy.data.objects[n]; x,y,z=o.location
    if x0<1499.5 or x1>1716.5 or y0<-0.5 or y1>168.5:
        out.append((n,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(x,1),round(y,1)))
print(len(out))
c=collections.Counter(e[0].split("_inst")[0] for e in out); print(c.most_common(20))
for e in out:
    if not any(k in e[0] for k in ("Tree","LipGrass","Bush","Rock","Plant","Fern","Mushroom")): print(e)
# ---- result ----
# {"result":"Code executed successfully: 199\n[('SM_VK_Tree_Pine_B', 67), ('SM_VK_Tree_Pine_A', 55), ('SM_VK_Tree_Pine_Young', 42), ('SM_VK_Bush_Round',
#  6), ('SM_VK_Tree_Oak_B', 6), ('SM_VK_Tree_Oak_A', 5), ('SM_VKT_LipGrass', 4), ('SM_VK_Tree_Oak_Autumn', 3), ('SM_VK_Wall_Stone', 2), ('SM_VK_Corner_S
# tone', 2), ('SM_VK_Corner_Timber', 2), ('SM_VK_Deco_Weeds', 1), ('SM_VK_Wall_Timber_X', 1), ('SM_VK_Wall_Timber_Window', 1), ('SM_VK_Roof_Gable', 1), 
# ('SM_VK_Tree_Birch', 1)]\n('SM_VK_Wall_Stone_inst.150', 1683.0, 1686.0, -0.5, 0.3, 1684.5, -0.0)\n('SM_VK_Wall_Stone_inst.151', 1680.0, 1683.0, -0.5, 
# 0.3, 1681.5, 0.0)\n('SM_VK_Deco_Weeds_inst.110', 1679.9, 1683.1, -0.9, -0.1, 1681.5, 0.0)\n('SM_VK_Corner_Stone_inst.137', 1685.3, 1686.6, -0.6, 0.6, 
# 1686.0, -0.0)\n('SM_VK_Corner_Stone_inst.140', 1679.4, 1680.6, -0.6, 0.7, 1680.0, 0.0)\n('SM_VK_Wall_Timber_X_inst.036', 1682.9, 1686.0, -0.6, 0.2, 16

# ==============================================================================================================
# [0055] 2026-09-23 17:35:12  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return round(h[0].z,2) if h[0] else None
for y in (-1.0,-0.5,-0.2,0.0,0.3):
    print(y,[gz(x,y) for x in range(1678,1690)])
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_44_barracks_mapedge",(1676,-9,4.0),(1684,1,1.8),lens=28,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: -1.0 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\n-0.5 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5
# , 1.5, 1.5, 1.5, 1.5]\n-0.2 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\n0.0 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 
# 1.5]\n0.3 [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]\nC:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-
# 4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_44_barracks_mapedge.png\n"}

# ==============================================================================================================
# [0056] 2026-09-23 17:36:10  blender  ok
# ==============================================================================================================
import bpy, time
import numpy as np
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]
t0=time.time()
s=0.3
xs=np.arange(1500.05,1716,s); ys=np.arange(0.05,168,s)
Z=np.full((len(ys),len(xs)),np.nan,np.float32)
down=Vector((0,0,-1)); rc=G.ray_cast
for a,y in enumerate(ys):
    for b,x in enumerate(xs):
        h=rc(Vector((x,y,40.0)),down,100)
        if h[0] is not None: Z[a,b]=h[0].z
ns["rv_Z"]=(Z,xs,ys)
print(time.time()-t0, np.isnan(Z).sum())
# ---- result ----
# {"result":"Code executed successfully: 0.4770171642303467 0\n"}

# ==============================================================================================================
# [0057] 2026-09-23 17:36:39  blender  ok
# ==============================================================================================================
import bpy
import numpy as np
ns=bpy.app.driver_namespace; Z,xs,ys=ns["rv_Z"]
print(Z.shape)
c=Z[1:-1,1:-1]
l=Z[1:-1,:-2]; r=Z[1:-1,2:]; u=Z[2:,1:-1]; d=Z[:-2,1:-1]
pitx=(c<l-0.5)&(c<r-0.5); pity=(c<u-0.5)&(c<d-0.5)
spx=(c>l+0.5)&(c>r+0.5); spy=(c>u+0.5)&(c>d+0.5)
for nm,m in (("pitx",pitx),("pity",pity),("spikex",spx),("spikey",spy)):
    idx=np.argwhere(m)
    print(nm,len(idx))
    for a,b in idx[:15]:
        print("   ",round(float(xs[b+1]),2),round(float(ys[a+1]),2),"z",round(float(c[a,b]),2),"nb",round(float(l[a,b]),2),round(float(r[a,b]),2),round(float(u[a,b]),2),round(float(d[a,b]),2))
# ---- result ----
# {"result":"Code executed successfully: (560, 720)\npitx 1\n 1539.05 141.35 z 4.5 nb 5.32 5.0 4.5 5.86\npity 1\n 1692.35 134.45 z 1.5 nb 2.91 1.5 2.33 
# 2.33\nspikex 17\n 1509.05 30.35 z 0.83 nb 0.0 0.0 -0.0 1.0\n 1512.05 30.35 z 0.82 nb 0.0 0.0 0.0 0.93\n 1550.75 30.35 z 0.82 nb 0.0 0.0 0.0 0.98\n 155
# 7.05 30.35 z 0.82 nb 0.0 0.0 0.0 0.94\n 1637.75 30.35 z 0.83 nb 0.0 0.0 0.0 1.05\n 1670.75 30.35 z 0.53 nb -0.0 0.0 0.0 0.88\n 1584.05 30.65 z 0.52 nb
#  0.0 0.0 0.0 0.91\n 1613.75 30.65 z 0.57 nb 0.0 0.0 -0.0 0.88\n 1643.75 30.65 z 0.83 nb 0.0 0.0 0.0 0.99\n 1602.05 53.75 z 0.82 nb 0.0 0.0 0.92 0.0\n 
# 1611.05 53.75 z 0.51 nb 0.0 0.0 0.88 0.0\n 1578.35 71.45 z 2.32 nb 1.5 1.5 2.43 1.5\n 1527.05 140.45 z 6.56 nb 5.99 5.88 6.89 5.92\n 1704.05 140.75 z 
# 3.55 nb 1.99 2.05 3.95 1.5\n 1539.35 141.35 z 5.0 nb 4.5 4.5 4.5 5.85\nspikey 7\n 1692.35 75.35 z 2.34 nb 2.6 1.5 1.5 1.5\n 1692.65 99.05 z 2.32 nb 2.

# ==============================================================================================================
# [0058] 2026-09-23 17:37:14  blender  ok
# ==============================================================================================================
import bpy, collections
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; res=ns["rv_res"]
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return h[0].z if h[0] else None
out=collections.defaultdict(list)
for n,r in res.items():
    if not any(k in n for k in ("Bush_","Rock_","Plant_","Mushrooms","Tree_")) : continue
    o=bpy.data.objects[n]; x,y,z=o.location
    x0,x1,y0,y1,z0,z1=r["bb"]
    rad=min(0.45*min(x1-x0,y1-y0),1.0) if "Tree" not in n else 0.6
    ring=[gz(x+dx*rad,y+dy*rad) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(.7,.7),(-.7,.7),(.7,-.7),(-.7,-.7))]
    ring=[q for q in ring if q is not None]
    drop=z-min(ring)
    if drop>0.8: out[n.split("_inst")[0]].append((n,round(x,1),round(y,1),round(z,1),round(drop,2),round(rad,2)))
for k,v in out.items():
    print(k,len(v))
    for e in v[:8]: print("  ",e)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Plant_TallGrass 1\n ('SM_VK_Plant_TallGrass_inst.042', 1702.7, 14.4, 1.5, 1.5, 1.0)\nSM_VK_Plant_Reeds 2\
# n ('SM_VK_Plant_Reeds_inst.029', 1679.5, 31.6, 0.0, 0.93, 1.0)\n ('SM_VK_Plant_Reeds_inst.037', 1657.3, 35.4, 0.0, 0.84, 1.0)\nSM_VK_Bush_Round 6\n ('
# SM_VK_Bush_Round_inst.084', 1624.6, 144.6, 6.0, 1.5, 1.0)\n ('SM_VK_Bush_Round_inst.096', 1503.7, 151.9, 7.5, 1.5, 1.0)\n ('SM_VK_Bush_Round_inst.104'
# , 1545.5, 153.8, 6.0, 1.01, 1.0)\n ('SM_VK_Bush_Round_inst.106', 1654.5, 153.7, 7.5, 1.5, 1.0)\n ('SM_VK_Bush_Round_inst.115', 1619.2, 156.9, 7.5, 1.5
# , 1.0)\n ('SM_VK_Bush_Round_inst.129', 1642.3, 162.6, 7.5, 1.04, 1.0)\n"}

# ==============================================================================================================
# [0059] 2026-09-23 17:37:46  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_45_footbridge_to_westroad_top",(1534,38,48),(1534,56,0),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_45_footbridge_to_westroad_top.png\n"}

# ==============================================================================================================
# [0060] 2026-09-23 17:38:27  blender  ok
# ==============================================================================================================
import bpy, collections
import numpy as np
ns=bpy.app.driver_namespace; res=ns["rv_res"]
walls=[(n,r["bb"]) for n,r in res.items() if "TownWall" in n or "Gatehouse_Block" in n]
bld=[(n,r["bb"]) for n,r in res.items() if any(k in n for k in ("Wall_","Corner_","Roof","Porch","Chimney","Stall","LeanTo")) and "TownWall" not in n and "LowWall" not in n]
out=collections.defaultdict(list)
for bn,b in bld:
    for wn,w in walls:
        ox=min(b[1],w[1])-max(b[0],w[0]); oy=min(b[3],w[3])-max(b[2],w[2]); oz=min(b[5],w[5])-max(b[4],w[4])
        if ox>0.3 and oy>0.3 and oz>0.3:
            out[wn].append((bn,round(ox,2),round(oy,2),[round(v,1) for v in b[:4]]))
print(len(out))
for k,v in out.items():
    print(k,[round(x,1) for x in dict(walls)[k][:4]])
    for e in v[:6]: print("   ",e)
# ---- result ----
# {"result":"Code executed successfully: 8\nSM_VK_Gatehouse_Block_inst [1622.2, 1632.8, 69.7, 78.2]\n ('SM_VK_Wall_Timber_Window_inst.241', 3.13, 0.8, [
# 1625.9, 1629.0, 71.4, 72.2])\n ('SM_VK_Wall_Timber_X_inst.033', 3.13, 0.43, [1623.0, 1626.1, 77.8, 78.6])\n ('SM_VK_Wall_Timber_Window_inst.242', 3.13
# , 0.43, [1626.0, 1629.1, 77.8, 78.6])\n ('SM_VK_Wall_Timber_K_inst.046', 3.13, 0.43, [1629.0, 1632.1, 77.8, 78.6])\n ('SM_VK_Wall_Timber_Door_inst', 0
# .8, 3.13, [1622.4, 1623.2, 75.0, 78.1])\n ('SM_VK_Wall_Timber_inst.038', 0.8, 3.13, [1622.4, 1623.2, 72.0, 75.1])\nSM_VK_TownWall_Straight_inst.034 [1
# 619.6, 1623.0, 73.4, 76.2]\n ('SM_VK_Wall_Timber_Door_inst', 0.62, 1.2, [1622.4, 1623.2, 75.0, 78.1])\n ('SM_VK_Wall_Timber_inst.038', 0.62, 1.76, [16
# 22.4, 1623.2, 72.0, 75.1])\nSM_VK_TownWall_Straight_inst.039 [1631.6, 1635.0, 73.4, 76.2]\n ('SM_VK_Wall_Timber_Door_inst.001', 0.8, 1.29, [1631.8, 16

# ==============================================================================================================
# [0061] 2026-09-23 17:39:11  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return round(h[0].z,2) if h[0] else None
print("terrain y-profile x=1544.4:",[(y/2,gz(1544.4,y/2)) for y in range(190,212)])
cr=bpy.data.objects["SM_VK_Prop_TreadwheelCrane_inst"]
me=cr.data; mw=cr.matrix_world
vs=[mw@v.co for v in me.vertices]
low=[v for v in vs if v.z<6.3]
print(len(vs),len(low))
import collections
by=collections.defaultdict(list)
for v in low: by[round(v.y)].append(round(v.z,2))
for k in sorted(by): print(k, min(by[k]), len(by[k]))
print("crane rot",[round(a*57.3) for a in cr.rotation_euler], tuple(round(c,2) for c in cr.location))
# ---- result ----
# {"result":"Code executed successfully: terrain y-profile x=1544.4: [(95.0, 3.0), (95.5, 3.0), (96.0, 3.0), (96.5, 3.0), (97.0, 3.0), (97.5, 3.0), (98.
# 0, 3.0), (98.5, 3.0), (99.0, 3.0), (99.5, 3.0), (100.0, 3.0), (100.5, 3.0), (101.0, 3.0), (101.5, 3.0), (102.0, 5.88), (102.5, 6.0), (103.0, 6.0), (10
# 3.5, 6.0), (104.0, 6.0), (104.5, 6.0), (105.0, 6.0), (105.5, 6.0)]\n1040 268\n100 6.0 46\n102 6.0 72\n103 6.25 12\n104 6.0 68\n105 5.95 58\n106 6.0 12
# \ncrane rot [0, 0, -90] (1544.4, 102.9, 6.0)\n"}

# ==============================================================================================================
# [0062] 2026-09-23 17:39:37  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_46_quarry_ridge_gap",(1537.0,100.0,7.8),(1546,101.3,4.2),lens=26,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_46_quarry_ridge_gap.png\n"}

# ==============================================================================================================
# [0063] 2026-09-23 17:40:22  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_47_gully_oaks",(1529.5,131,6.2),(1529,141,6.0),lens=26,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_47_gully_oaks.png\n"}

# ==============================================================================================================
# [0064] 2026-09-23 17:40:50  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_48_north_tower_pines",(1664,127,19),(1671,139,13),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_48_north_tower_pines.png\n"}

# ==============================================================================================================
# [0065] 2026-09-23 17:41:25  blender  ok
# ==============================================================================================================
import bpy, collections
import numpy as np
ns=bpy.app.driver_namespace; res=ns["rv_res"]
oth=[(n,r) for n,r in res.items() if any(k in n for k in ("TownWall","Gatehouse","Bridge","Quay","Pier","Wall_","Corner_","Mine","Quarry"))]
B=np.array([r["bb"] for n,r in oth]); sh=0.15
c=collections.Counter()
for n,r in res.items():
    if "LipGrass" not in n: continue
    o=bpy.data.objects[n]; x,y,z=o.location
    m=(B[:,0]+sh<x)&(B[:,1]-sh>x)&(B[:,2]+sh<y)&(B[:,3]-sh>y)&(B[:,4]<z+0.4)&(B[:,5]>z+0.1)
    for k in np.nonzero(m)[0]: c[oth[k][0]]+=1
for k,v in c.most_common(): print(k,v,[round(q,1) for q in res[k]["bb"][:4]])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_TownWall_Tower_Round_inst.003 11 [1604.4, 1611.6, 134.4, 141.6]\nSM_VK_TownWall_Tower_Round_inst 9 [1583.
# 4, 1590.6, 71.4, 78.6]\nSM_VK_TownWall_Tower_Round_inst.005 9 [1646.4, 1653.6, 134.4, 141.6]\nSM_VK_TownWall_Tower_Round_inst.009 8 [1685.4, 1692.6, 9
# 2.4, 99.6]\nSM_VK_TownWall_Tower_Round_inst.011 8 [1685.4, 1692.6, 113.4, 120.6]\nSM_VK_TownWall_Tower_Round_inst.001 8 [1583.4, 1590.6, 134.4, 141.6]
# \nSM_VK_TownWall_Tower_Round_inst.007 6 [1667.4, 1674.6, 134.4, 141.6]\nSM_VK_TownWall_Tower_Round_inst.002 4 [1604.4, 1611.6, 71.4, 78.6]\nSM_VK_Gate
# house_Block_inst 1 [1622.2, 1632.8, 69.7, 78.2]\n"}

# ==============================================================================================================
# [0066] 2026-09-23 17:42:34  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
ns=bpy.app.driver_namespace; G=ns["rv_ground_bvh"]; res=ns["rv_res"]
def gz(x,y):
    h=G.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),200); return round(h[0].z,2) if h[0] else None
for x in (1580.0,1603.0,1609.5,1657.5):
    print(x,[(y/4,gz(x,y/4)) for y in range(184,198)])
for n in ("SM_VK_Quay_Straight_inst","SM_VK_Quay_Straight_inst.004"):
    print(n,[round(v,2) for v in res[n]["bb"]])
# ---- result ----
# {"result":"Code executed successfully: 1580.0 [(46.0, -1.5), (46.25, -1.5), (46.5, -1.5), (46.75, -1.5), (47.0, -1.35), (47.25, -1.08), (47.5, -0.8), 
# (47.75, -0.53), (48.0, -0.11), (48.25, -0.02), (48.5, 0.0), (48.75, 0.0), (49.0, 0.0), (49.25, 0.0)]\n1603.0 [(46.0, -1.5), (46.25, -1.5), (46.5, -1.5
# ), (46.75, -1.5), (47.0, -1.5), (47.25, -1.3), (47.5, -1.02), (47.75, -0.75), (48.0, -0.45), (48.25, -0.08), (48.5, -0.01), (48.75, 0.0), (49.0, -0.0)
# , (49.25, 0.0)]\n1609.5 [(46.0, -1.5), (46.25, -1.5), (46.5, -1.5), (46.75, -1.49), (47.0, -1.24), (47.25, -0.95), (47.5, -0.69), (47.75, -0.37), (48.
# 0, -0.05), (48.25, -0.01), (48.5, 0.0), (48.75, 0.0), (49.0, 0.0), (49.25, 0.0)]\n1657.5 [(46.0, -1.5), (46.25, -1.5), (46.5, -1.5), (46.75, -1.5), (4
# 7.0, -1.35), (47.25, -1.08), (47.5, -0.8), (47.75, -0.52), (48.0, -0.11), (48.25, -0.02), (48.5, 0.0), (48.75, 0.0), (49.0, 0.0), (49.25, 0.0)]\nSM_VK

# ==============================================================================================================
# [0067] 2026-09-23 17:42:56  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace["shot"]
OD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\review\ground"
print(shot("ground_49_smokehouse_corner_low",(1653.2,44.2,-0.25),(1656.3,47.9,-0.3),lens=30,res=(1600,900),outdir=OD))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\review\\ground\\ground_49_smokehouse_corner_low.png\n"}
