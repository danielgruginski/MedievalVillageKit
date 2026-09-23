# valley-rereview / agent-a606e2482c9428bb8.jsonl: Blender MCP calls  (part 1/1)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 19:35:09  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
def bb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs),min(c.z for c in cs),max(c.z for c in cs))
coll=bpy.data.collections["VK_ValleyTown"]
out=[]
for o in coll.all_objects:
    if o.type!="MESH": continue
    x,y=o.location.x,o.location.y
    if 1535<=x<=1556 and 88<=y<=106:
        b=bb(o)
        out.append((o.name,round(x,2),round(y,2),round(o.location.z,2),tuple(round(v,2) for v in b)))
for r in sorted(out,key=lambda r:(r[2],r[1])): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Pile_Stone_3_inst.001', 1546.6, 93.5, 3.0, (1545.25, 1547.95, 93.0, 94.0, 3.0, 4.18))\n('SM_VK_LeanTo_i
# nst.010', 1539.0, 93.65, 3.0, (1537.3, 1540.7, 89.84, 93.81, 3.0, 6.53))\n('SM_VK_Prop_Banker_inst', 1544.1, 94.1, 3.0, (1543.13, 1545.07, 93.34, 94.9
# 8, 2.99, 4.46))\n('SM_VK_Quarry_Face_Straight_inst.004', 1539.0, 94.5, 3.0, (1537.5, 1540.5, 92.84, 96.0, 2.4, 6.55))\n('SM_VK_Quarry_Face_Corner_inst
# .001', 1542.0, 94.5, 3.0, (1540.41, 1543.62, 92.92, 96.0, 2.4, 6.52))\n('SM_VK_Quarry_Floor_inst.001', 1545.0, 94.5, 3.0, (1543.51, 1546.49, 93.01, 95
# .99, 2.39, 3.76))\n('SM_VK_Quarry_Face_Corner_inst', 1548.0, 94.5, 3.0, (1546.42, 1549.5, 92.88, 96.09, 2.4, 6.52))\n('SM_VK_Quarry_Face_Straight_inst
# .003', 1551.0, 94.5, 3.0, (1549.5, 1552.5, 92.84, 96.0, 2.4, 6.55))\n('SM_VK_Prop_Wheelbarrow_inst.005', 1546.9, 95.9, 3.0, (1545.6, 1547.87, 95.13, 9

# ==============================================================================================================
# [0002] 2026-09-23 19:35:44  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
res=[]
for y in (93.2,93.5,93.8,94.2,94.6):
    row=[]
    x=1543.0
    while x<=1547.01:
        hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)))
        row.append((round(x,1),ob.name.replace("SM_VK_","")[:14] if ob else None,round(loc.z,2) if hit else None))
        x+=0.25
    res.append((y,row))
for y,row in res:
    print(y, [(a,b,c) for a,b,c in row])
# ---- result ----
# {"result":"Code executed successfully: 93.2 [(1543.0, 'VKV_Chunk_0_1', 3.0), (1543.2, 'VKV_Chunk_0_1', 3.0), (1543.5, 'VKV_Chunk_0_1', 3.0), (1543.8, 
# 'Quarry_Floor_i', 3.06), (1544.0, 'Quarry_Floor_i', 3.49), (1544.2, 'Quarry_Floor_i', 3.53), (1544.5, 'Quarry_Floor_i', 3.06), (1544.8, 'Quarry_Floor_
# i', 3.06), (1545.0, 'Quarry_Floor_i', 3.06), (1545.2, 'Pile_Stone_3_i', 3.12), (1545.5, 'Pile_Stone_3_i', 4.18), (1545.8, 'Pile_Stone_3_i', 4.18), (15
# 46.0, 'Pile_Stone_3_i', 4.18), (1546.2, 'Pile_Stone_3_i', 4.18), (1546.5, 'Pile_Stone_3_i', 4.16), (1546.8, 'Pile_Stone_3_i', 4.18), (1547.0, 'Pile_St
# one_3_i', 4.18)]\n93.5 [(1543.0, 'VKV_Chunk_0_1', 3.0), (1543.2, 'VKV_Chunk_0_1', 3.0), (1543.5, 'VKV_Chunk_0_1', 3.0), (1543.8, 'Quarry_Floor_i', 3.0
# 6), (1544.0, 'Quarry_Floor_i', 3.53), (1544.2, 'Quarry_Floor_i', 3.54), (1544.5, 'Quarry_Floor_i', 3.53), (1544.8, 'Quarry_Floor_i', 3.06), (1545.0, '

# ==============================================================================================================
# [0003] 2026-09-23 19:36:22  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
def code(ob,z):
    if ob is None: return '?'
    n=ob.name
    if 'Chunk' in n: return '.' if abs(z-3.0)<0.3 else ('^' if z>4 else '~')
    if 'Floor' in n: return 'f' if z<3.3 else 'r'
    if 'Face' in n: return 'F'
    if 'Banker' in n: return 'B'
    if 'Pile_Stone' in n: return 'P'
    if 'Wheelbarrow' in n: return 'W'
    if 'Grindstone' in n: return 'G'
    if 'LeanTo' in n: return 'L'
    if 'Crane' in n: return 'C'
    return 'o'
y=99.9
while y>=90.0:
    s=''
    x=1538.0
    while x<=1552.01:
        hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)))
        s+=code(ob,loc.z) if hit else ' '
        x+=0.2
    print(f"{y:6.1f} {s}")
    y-=0.3
print("x from 1538 step 0.2")
# ---- result ----
# {"result":"Code executed successfully: 99.9 ^^^^^^^......FFFFFFFFFFFFFFFFFFFCCFFFFFFFFFFFF.FFFFFFFFFFF......^^^^^^^\n 99.6 ^^^^^^^......FFFFFFFFFFF...
# F....CC....FFFFF.FFFFFFFFFFFFFF......^^^^^^^\n 99.3 ^^^^^^^......FFFFFFFFFFF.FFF.FFFCC..FFFFF..FF.FFFFFFFFFFFF......^^^^^^^\n 99.0 ^^^^^^^......FFFFFF
# FFFF....F.FFFCC..FF.....FF...FFFFFFFFFF......^^^^^^^\n 98.7 ^^^^^^^......FFFFFFFFFFFFF..ffffCCfffffffffFF.FFFFFFFFFFFF......^^^^^^^\n 98.4 ^^^^^^^....
# ..FFFFFFFFFFFFFF.rrrrCCffffffffFFF.FFFFFFFFFFFF......^^^^^^^\n 98.1 ^^^^^^^......FFFFFFFFFFFFFFFfrrCCCfffffffffFFF.FFFFFFFFFFF......^^^^^^^\n 97.8 ^^^
# ^^^^......FFFFFFFFFFF.FFFFffCCC...ffffff....FFFFFFFFFFF......^^^^^^^\n 97.5 ^^^^^^^......FFFFFFFFFFF....fffCCCrrrrrffff....FFFFFFFFFFF......^^^^^^^\n 
# 97.2 ^^^^^^^......FFFFFFFFFFF....fffffrrrrrrfffFFFF.FFFFFFFFFFF......^^^^^^^\n 96.9 ^^^^^^^......FFFFFFFFFFF.FFFffffffff.ffffffFFFFFFFFFFFFFFF......^^

# ==============================================================================================================
# [0004] 2026-09-23 19:37:36  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
# for each y, find free ground interval (hit z<3.35 terrain/floor) around x 1542-1544 west of the banker
for k in range(0,28):
    y=93.0+0.1*k
    free=[]; x=1541.5
    segs=[]
    while x<=1544.5:
        hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)))
        ok = hit and loc.z<3.35
        segs.append(('.' if ok else ('B' if 'Banker' in ob.name else ('F' if 'Face' in ob.name else 'x'))) if hit else ' ')
        x+=0.05
    s=''.join(segs)
    # longest run of '.' containing x~1543.0
    print(f"{y:5.2f} {s}")
print("x from 1541.5 step 0.05")
# ---- result ----
# {"result":"Code executed successfully: 93.00 .............................................................\n93.10 ....................................
# ...............xx........\n93.20 ..................................................xxxxxxxxx..\n93.30 ................................................
# ..xxxxxxxxxxx\n93.40 .................................................xxxxxxxxxxxx\n93.50 ................................................xxxxxxxxxxxx
# x\n93.60 ..FFFFFFF.......................................xxxxxxxxxxxxx\n93.70 FFFFFFFFFF..............................BBBBBBBBBBxxxxxxxxxxx\n93.80 FFF
# FFFFFFFFFFFFFFFFFFFFFFF..............BBBBBBBBBBBBBBBBBBBBB\n93.90 FFFFFFFFFFFFFFFFFFFFFFFFFF..............BBBBBBBBBBBBBBBBBBBBB\n94.00 FFFFFFFFFFFFFFF
# FFFFFFFFFFF.............BBBBBBBBBBBBBBBBBBBBBB\n94.10 FFFFFFFFFFFFFFFFFFFFFFFFFF.............BBBBBBBBBBBBBBBBBBBBBB\n94.20 FFFFFFFFFFFFFFFFFFFFFFFFFF.

# ==============================================================================================================
# [0005] 2026-09-23 19:38:30  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_play"
os.makedirs(OUT,exist_ok=True)
p=shot("vplay_01_quarry_mouth",(1545.0,82.0,12.0),(1545.0,95.0,3.5),lens=35,res=(1400,900),outdir=OUT)
print(p)
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_play\\vplay_01_quarry_mouth.png\n"}

# ==============================================================================================================
# [0006] 2026-09-23 19:39:26  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
def bb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs),min(c.z for c in cs),max(c.z for c in cs))
coll=bpy.data.collections["VK_ValleyTown"]
out=[]
for o in coll.all_objects:
    if o.type!="MESH": continue
    x,y=o.location.x,o.location.y
    if 1644<=x<=1668 and 44<=y<=58:
        b=bb(o)
        out.append((o.name,round(x,2),round(y,2),round(o.location.z,2),round(o.rotation_euler.z*57.2958),tuple(round(v,2) for v in b)))
for r in sorted(out,key=lambda r:(r[2],r[1])): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_Corner_Stone_inst.135', 1656.0, 48.0, 0.0, 360, (1655.38, 1656.65, 47.4, 48.65, -0.06, 3.01))\n('SM_VK_
# Wall_Stone_inst.143', 1657.5, 48.0, 0.0, 360, (1655.98, 1659.02, 47.47, 48.28, -0.11, 3.0))\n('SM_VK_Corner_Stone_inst.136', 1659.0, 48.0, 0.0, 90, (1
# 658.35, 1659.6, 47.38, 48.65, -0.06, 3.01))\n('SM_VK_Prop_HandPump_inst', 1645.2, 48.3, 0.0, -90, (1644.39, 1646.34, 47.47, 48.85, -0.01, 2.17))\n('SM
# _VK_Prop_BarrelStack_inst.010', 1654.6, 48.5, 0.0, 270, (1653.99, 1655.15, 47.54, 49.46, 0.0, 1.5))\n('SM_VK_Prop_Woodpile_inst.004', 1660.8, 49.3, 0.
# 0, 270, (1660.15, 1661.45, 47.1, 50.8, -0.05, 1.47))\n('SM_VK_Wall_Posts_inst.004', 1644.0, 49.5, 0.0, 90, (1643.79, 1644.32, 47.74, 51.0, -0.6, 3.0))
# \n('SM_VK_Wall_Stone_inst.145', 1656.0, 49.5, 0.0, 270, (1655.47, 1656.28, 47.98, 51.02, -0.11, 3.0))\n('SM_VK_RoofS_Single_inst', 1657.5, 49.5, 3.0, 

# ==============================================================================================================
# [0007] 2026-09-23 19:39:51  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
def code(ob,z):
    n=ob.name
    if 'Chunk' in n:
        if z<0.35: return '.'
        if z<1.2: return '/'
        return '^'
    if 'FishRack' in n: return 'R'
    if 'Pile_Fish' in n: return 'p'
    if 'Water' in n: return '~'
    if 'Lip' in n: return 'g'
    if 'Reeds' in n: return 'e'
    if 'Rock' in n: return 'k'
    if 'Door' in n: return 'D'
    return '#'
y=55.0
while y>=46.99:
    s=''; x=1646.0
    while x<=1666.01:
        hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)))
        s+=code(ob,loc.z) if hit else ' '
        x+=0.2
    print(f"{y:5.1f} {s}")
    y-=0.2
print("x from 1646 step 0.2")
# ---- result ----
# {"result":"Code executed successfully: 55.0 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n 54
# .8 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n 54.6 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n 54.4 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^^^\n 54.2 ^^^^^^^^^^g^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n 54.0 ^^^^^gggggg
# ggggg^^^gggggggggggggg^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^gggggggggg^gg^^^^^^^^^\n 53.8 ////ggggggggggg//gggggggggggggggg///////////////////
# //////////////////////////ggggggggggggggggggggggg\n 53.6 ............kk.....//............................................................k.........//

# ==============================================================================================================
# [0008] 2026-09-23 19:41:28  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from mathutils import Vector
from collections import deque
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
X0,X1,Y0,Y1,S=1622.0,1674.0,46.0,56.0,0.2
nx=int((X1-X0)/S)+1; ny=int((Y1-Y0)/S)+1
walk=np.zeros((ny,nx),bool); names={}
for j in range(ny):
    y=Y0+j*S
    for i in range(nx):
        x=X0+i*S; z0=20.0; ok=False
        for _ in range(4):
            hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,z0)),Vector((0,0,-1)))
            if not hit: break
            if loc.z>2.3:   # overhead (roof eaves)
                z0=loc.z-0.01; continue
            nm=ob.name
            if 'Chunk' in nm or 'LipGrass' in nm or 'Pebbles' in nm or 'Doormat' in nm:
                ok = loc.z<0.4
            else:
                ok = False
            break
        walk[j,i]=ok
# erode by agent radius 0.3 m (square, 1 cell=0.2 -> r=1 cell ~0.2-0.28)
def erode(w,r):
    e=w.copy()
    for dj in range(-r,r+1):
        for di in range(-r,r+1):
            e&=np.roll(np.roll(w,dj,0),di,1)
    return e
def bfs(w,start):
    d=np.full(w.shape,-1); q=deque([start]); d[start]=0
    while q:
        j,i=q.popleft()
        for dj,di in ((1,0),(-1,0),(0,1),(0,-1)):
            a,b=j+dj,i+di
            if 0<=a<w.shape[0] and 0<=b<w.shape[1] and w[a,b] and d[a,b]<0:
                d[a,b]=d[j,i]+1; q.append((a,b))
    return d
start=(int((51-Y0)/S),int((1627-X0)/S)); goal=(int((52.4-Y0)/S),int((1657.5-X0)/S))
for r in (0,1,2):
    w=erode(walk,r); w[start]=True
    d=bfs(w,start)
    print("erode r",r,"start walk",walk[start],"goal walk",w[goal],"dist cells",d[goal], "-> m",d[goal]*S if d[goal]>=0 else None)
import pickle
bpy.app.driver_namespace["_vplay_walk"]=walk
# ---- result ----
# {"result":"Code executed successfully: erode r 0 start walk False goal walk True dist cells 166 -> m 33.2\nerode r 1 start walk False goal walk True d
# ist cells -1 -> m None\nerode r 2 start walk False goal walk False dist cells -1 -> m None\n"}

# ==============================================================================================================
# [0009] 2026-09-23 19:42:57  blender  ok
# ==============================================================================================================
import bpy, numpy as np
from collections import deque
walk=bpy.app.driver_namespace.pop("_vplay_walk")
X0,Y0,S=1622.0,46.0,0.2
def erode(w,r):
    e=w.copy()
    for dj in range(-r,r+1):
        for di in range(-r,r+1):
            e&=np.roll(np.roll(w,dj,0),di,1)
    return e
def bfs(w,start):
    d=np.full(w.shape,-1); q=deque([start]); d[start]=0
    while q:
        j,i=q.popleft()
        for dj,di in ((1,0),(-1,0),(0,1),(0,-1)):
            a,b=j+dj,i+di
            if 0<=a<w.shape[0] and 0<=b<w.shape[1] and w[a,b] and d[a,b]<0:
                d[a,b]=d[j,i]+1; q.append((a,b))
    return d
C=lambda x,y:(int(round((y-Y0)/S)),int(round((x-X0)/S)))
w=erode(walk,1)
# find a walkable start near the ramp foot
for sx,sy in ((1627,50.0),(1627,49.5),(1630,50),(1632,51)):
    if w[C(sx,sy)]: break
print("start",sx,sy,w[C(sx,sy)])
d=bfs(w,C(sx,sy))
for (x,y) in ((1640,51),(1650,52.5),(1652.8,52.6),(1653.2,51.2),(1657.5,52.4),(1660,52.5),(1664,52)):
    print((x,y),"walk",w[C(x,y)],"dist m",d[C(x,y)]*S if d[C(x,y)]>=0 else None)
# goal-side component
d2=bfs(w,C(1657.5,52.6))
print("goal comp reaches (1664,52):",d2[C(1664,52)]*S if d2[C(1664,52)]>=0 else None, " reaches (1652.8,52.6):",d2[C(1652.8,52.6)])
# free width in column x at the rack: for each x 1653..1657 find walkable (unEroded) y-intervals in 51..54
for x in np.arange(1653.0,1657.01,0.4):
    col=[walk[C(x,y)] for y in np.arange(51.4,54.01,0.2)]
    print(round(x,1),''.join('.' if c else 'X' for c in col))
print("y from 51.4 step .2")
# ---- result ----
# {"result":"Code executed successfully: start 1630 50 True\n(1640, 51) walk False dist m None\n(1650, 52.5) walk True dist m 22.400000000000002\n(1652.
# 8, 52.6) walk True dist m 25.400000000000002\n(1653.2, 51.2) walk True dist m 26.400000000000002\n(1657.5, 52.4) walk True dist m None\n(1660, 52.5) w
# alk True dist m None\n(1664, 52) walk True dist m None\ngoal comp reaches (1664,52): 7.0 reaches (1652.8,52.6): -1\n1653.0 ............XX\n1653.4 ....
# ........XX\n1653.8 ..X.X..X....XX\n1654.2 ....X..X....XX\n1654.6 ......X.....XX\n1655.0 ..XXXXX.....XX\n1655.4 XXXXX.X.....XX\n1655.8 XXX.........XX\n
# 1656.2 XXX..X..X...XX\n1656.6 XXX..X..X...XX\n1657.0 XXX.........XX\ny from 51.4 step .2\n"}

# ==============================================================================================================
# [0010] 2026-09-23 19:43:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_play"
print(shot("vplay_02_smokehouse_rack",(1650.0,63.0,9.5),(1656.0,51.5,0.8),lens=32,res=(1400,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_play\\vplay_02_smokehouse_rack.png\n"}

# ==============================================================================================================
# [0011] 2026-09-23 19:44:13  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
for y in (88.5,90.5,91.5,92.5):
    s=[]
    x=1526.0
    while x<=1572.01:
        hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)))
        s.append(f"{loc.z:.1f}" if hit and 'Chunk' in ob.name else (ob.name.replace('SM_VK_','')[:6] if hit else '-'))
        x+=2.0
    print(y, s)
print("x 1526..1572 step 2")
# ground-control texture: check pixel value (dirt road) at cells
img=bpy.data.images.get("T_VK_GroundCtl_Town")
print(img.size if img else None)
if img:
    W,H=img.size; px=img.pixels[:]
    for (i,j) in [(10,30),(11,30),(12,30),(13,30),(16,30),(17,30),(18,30),(19,30),(22,30),(11,29),(15,29),(24,30)]:
        k=(j*W+i)*4; print((i,j),[round(v,2) for v in px[k:k+4]])
# ---- result ----
# {"result":"Code executed successfully: 88.5 ['3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', '3.0', 
# '3.0', '3.0', 'Bush_R', 'Bush_R', '3.0', '3.0', 'TownWa', 'TownWa', '3.0']\n90.5 ['3.0', '3.0', '3.0', '3.0', '6.0', '6.0', '6.0', 'LeanTo', '3.0', '3
# .0', '3.0', '3.0', '3.0', '6.0', '6.0', '6.0', '3.0', '3.0', '3.0', '3.0', '3.0', 'TownWa', 'TownWa', '3.0']\n91.5 ['3.0', '3.0', '3.0', '3.0', '6.0',
#  '6.0', 'LeanTo', 'LeanTo', '3.0', '3.0', '3.0', '3.0', '3.0', '6.0', '6.0', '6.0', '3.0', '3.0', '3.0', '3.0', '3.0', 'TownWa', 'TownWa', '3.0']\n92.
# 5 ['3.0', '3.0', '3.0', '3.0', '6.0', '6.0', 'LeanTo', 'LeanTo', '3.0', '3.0', '3.0', '3.0', '3.0', '6.0', '6.0', '6.0', '3.0', '3.0', '3.0', '3.0', '
# 3.0', 'TownWa', 'TownWa', '3.0']\nx 1526..1572 step 2\n<bpy_int[2], Image.size>\n(10, 30) [1.0, 0.0, 0.0, 0.0]\n(11, 30) [1.0, 0.0, 0.0, 0.0]\n(12, 30

# ==============================================================================================================
# [0012] 2026-09-23 19:44:33  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_play"
print(shot("vplay_03_postern_lane",(1546.0,66.0,30.0),(1546.0,91.5,3.0),lens=30,res=(1600,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_play\\vplay_03_postern_lane.png\n"}

# ==============================================================================================================
# [0013] 2026-09-23 19:45:09  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
def bb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs),min(c.z for c in cs),max(c.z for c in cs))
coll=bpy.data.collections["VK_ValleyTown"]
out=[]
for o in coll.all_objects:
    if o.type!="MESH": continue
    b=bb(o)
    # intersects street row 30 inside town x 1569..1623, y 89.5..93.5
    if b[1]>1569 and b[0]<1623 and b[3]>89.8 and b[2]<93.2:
        out.append((o.name,round(o.location.x,2),round(o.location.y,2),round(o.location.z,2),tuple(round(v,2) for v in b)))
for r in sorted(out,key=lambda r:r[1]): print(r)
# ---- result ----
# {"result":"Code executed successfully: ('SM_VK_TownWall_Straight_inst.086', 1569.0, 88.5, 3.0, (1567.36, 1570.18, 87.0, 90.45, 1.5, 10.95))\n('SM_VK_T
# ownWall_Postern_inst', 1569.0, 91.5, 3.0, (1567.51, 1570.18, 90.0, 93.0, 1.5, 10.95))\n('SM_VK_TownWall_Straight_inst.089', 1569.0, 94.5, 3.0, (1567.3
# 6, 1570.18, 93.0, 96.45, 1.5, 10.95))\n('SM_VK_Corner_Stone_inst.147', 1575.0, 90.0, 3.0, (1574.4, 1575.65, 89.35, 90.62, 2.94, 6.01))\n('SM_VK_Corner
# _StoneUp_inst.002', 1575.0, 90.0, 6.0, (1574.48, 1575.65, 89.38, 90.48, 5.94, 8.8))\n('SM_VK_Corner_StoneUp_inst.006', 1575.0, 90.0, 8.8, (1574.48, 15
# 75.65, 89.38, 90.48, 8.74, 11.6))\n('SM_VK_Wall_Stone_Window_inst.147', 1575.0, 88.5, 3.0, (1574.18, 1575.28, 86.98, 90.02, 2.89, 6.0))\n('SM_VK_Deco_
# Weeds_inst.132', 1575.0, 88.5, 3.0, (1574.13, 1574.87, 86.92, 90.1, 2.97, 3.54))\n('SM_VK_Wall_StoneUp_inst.001', 1575.0, 88.5, 6.0, (1574.51, 1575.28

# ==============================================================================================================
# [0014] 2026-09-23 19:45:42  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
def scan(x0,x1,y0,y1,st=0.25,zmax=5.0):
    y=y1
    while y>=y0-1e-6:
        s=''; x=x0
        while x<=x1+1e-6:
            z0=30.0; c=' '
            for _ in range(5):
                hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,z0)),Vector((0,0,-1)))
                if not hit: break
                if loc.z>zmax: z0=loc.z-0.01; continue
                nm=ob.name
                if 'Chunk' in nm: c='.' if loc.z<3.3 else '^'
                elif 'Lamp' in nm: c='L'
                elif 'Bush' in nm: c='b'
                elif 'Corbel' in nm: c='c'
                elif 'Plant' in nm or 'Flower' in nm or 'Weeds' in nm or 'Crop' in nm: c='p'
                else: c='#'
                break
            s+=c; x+=st
        print(f"{y:6.2f} {s}")
        y-=st
print("zmax 5.0 (ignore overhead above 2 m)")
scan(1606,1618,88,96)
print("x 1606..1618")
# ---- result ----
# {"result":"Code executed successfully: zmax 5.0 (ignore overhead above 2 m)\n 96.00 .................... ............................\n 95.75 ........
# .........................................\n 95.50 .................................................\n 95.25 ...p...p..................................
# .......\n 95.00 .....pp..........................................\n 94.75 ....p............................................\n 94.50 ..................
# ...............................\n 94.25 .................................................\n 94.00 .................................................\n 
# 93.75 .................................................\n 93.50 .................................................\n 93.25 ............................
# .....................\n 93.00 .................................................\n 92.75 .................................................\n 92.50 ....

# ==============================================================================================================
# [0015] 2026-09-23 19:46:21  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
def scan(x0,x1,y0,y1,st=0.25,zmax=5.0):
    y=y1
    while y>=y0-1e-6:
        s=''; x=x0
        while x<=x1+1e-6:
            z0=30.0; c=' '
            for _ in range(12):
                hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,z0)),Vector((0,0,-1)))
                if not hit: break
                if loc.z>zmax: z0=loc.z-0.01; continue
                nm=ob.name
                if 'Chunk' in nm: c='.' if loc.z<3.3 else '^'
                elif 'Lamp' in nm: c='L'
                elif 'Bush' in nm: c='b'
                elif 'Corbel' in nm: c='c'
                elif 'Plant' in nm or 'Flower' in nm or 'Weeds' in nm or 'Crop' in nm: c='p'
                else: c='#'
                break
            s+=c; x+=st
        print(f"{y:6.2f} {s}")
        y-=st
scan(1580,1592,88.5,96)
print("x 1580..1592 step .25")
# ---- result ----
# {"result":"Code executed successfully: 96.00 ## #..........................................\n 95.75 #..........................................\n 95.5
# 0 ..####..........................................\n 95.25 .................................................\n 95.00 ###########......................
# ................\n 94.75 #############....................................\n 94.50 #############........bbbb........................\n 94.25 #########
# ##........bbbbbbb.......................\n 94.00 ###########.........bbbbbbbb.....................\n 93.75 ...................bbbbbbbbb...............
# ......\n 93.50 ...................bbbbbbbbbb....................\n 93.25 ...................bbbbbbbbbb....................\n 93.00 ..................b
# bbbbbbbbb.....................\n 92.75 ...................bbbbbbbb......................\n 92.50 .....................bbbbb.......................\n 9

# ==============================================================================================================
# [0016] 2026-09-23 19:46:55  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
o=bpy.data.objects.get("SM_VK_Bush_Round_inst.025")
print(o.location[:], [round(v,2) for v in o.dimensions])
# actual canopy extent in y: max y of evaluated mesh vertices in world
me=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
ys=[(o.matrix_world@v.co).y for v in me.vertices]; zs=[(o.matrix_world@v.co).z for v in me.vertices]
print("y range",round(min(ys),2),round(max(ys),2))
o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
for nm in ("SM_VK_Bush_Round_inst.038",):
    o=bpy.data.objects[nm]; me=o.evaluated_get(dg).to_mesh()
    ys=[(o.matrix_world@v.co).y for v in me.vertices]; zs=[(o.matrix_world@v.co) for v in me.vertices]
    low=[p for p in zs if p.z<4.8]
    print(nm,"y range all",round(min(ys),2),round(max(ys),2),"y min below head",round(min(p.y for p in low),2))
    o.evaluated_get(dg).to_mesh_clear()
o=bpy.data.objects["SM_VK_Prop_LampPost_inst.029"]; me=o.evaluated_get(dg).to_mesh()
pts=[o.matrix_world@v.co for v in me.vertices]
low=[p for p in pts if p.z<3.0+1.9]
print("lamp low part x",round(min(p.x for p in low),2),round(max(p.x for p in low),2),"y",round(min(p.y for p in low),2),round(max(p.y for p in low),2))
o.evaluated_get(dg).to_mesh_clear()
# ---- result ----
# {"result":"Code executed successfully: (1582.8831787109375, 26.371383666992188, 1.5) [2.78, 2.65, 2.54]\ny range 25.03 27.85\nSM_VK_Bush_Round_inst.03
# 8 y range all 92.03 94.74 y min below head 92.03\nlamp low part x 1612.3 1612.9 y 91.6 92.2\n"}

# ==============================================================================================================
# [0017] 2026-09-23 19:47:34  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
def bb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs),max(c.x for c in cs),min(c.y for c in cs),max(c.y for c in cs),min(c.z for c in cs),max(c.z for c in cs))
coll=bpy.data.collections["VK_ValleyTown"]
for o in coll.all_objects:
    if o.type!="MESH": continue
    b=bb(o)
    if b[1]>1566 and b[0]<1581 and b[3]>55 and b[2]<66 and o.location.z<3:
        print(o.name,round(o.location.x,2),round(o.location.y,2),round(o.location.z,2),tuple(round(v,2) for v in b))
# terrain under HerbBundles
o=bpy.data.objects["SM_VK_Prop_HerbBundles_inst"]; b=bb(o)
import numpy as np
zs=[]
for x in np.linspace(b[0],b[1],7):
    for y in np.linspace(b[2],b[3],4):
        # cast from below the prop? cast from z 10 but skip non-chunk
        z0=10.0
        for _ in range(6):
            hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,z0)),Vector((0,0,-1)))
            if not hit: break
            if 'Chunk' in ob.name: zs.append((round(x,2),round(y,2),round(loc.z,2))); break
            z0=loc.z-0.01
print("herb terrain z min/max",min(z[2] for z in zs),max(z[2] for z in zs))
print([z for z in zs if z[2]<1.45])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone_Window_inst.132 1578.0 55.5 0.0 (1577.18, 1578.28, 53.98, 57.02, -0.11, 3.0)\nSM_VK_Prop_Flowe
# rBox_inst.102 1577.45 55.5 0.78 (1577.17, 1577.71, 54.79, 56.25, 0.55, 1.45)\nSM_VK_Deco_Weeds_inst.090 1578.0 55.5 0.0 (1577.13, 1577.87, 53.92, 57.1
# , -0.03, 0.54)\nSM_VK_Wall_Stone_Window_inst.135 1579.5 57.0 0.0 (1577.98, 1581.02, 56.72, 57.82, -0.11, 3.0)\nSM_VK_Deco_Weeds_inst.094 1579.5 57.0 0
# .0 (1577.92, 1581.1, 57.13, 57.87, -0.03, 0.54)\nSM_VK_Wall_Stone_inst.142 1582.5 57.0 0.0 (1580.98, 1584.02, 56.72, 57.53, -0.11, 3.0)\nSM_VK_Deco_We
# eds_inst.095 1582.5 57.0 0.0 (1580.92, 1584.1, 57.13, 57.87, -0.03, 0.54)\nSM_VK_Corner_Stone_inst.129 1578.0 57.0 0.0 (1577.4, 1578.65, 56.35, 57.62,
#  -0.06, 3.01)\nSM_VK_Prop_Dovecote_inst 1573.0 66.85 1.5 (1570.6, 1575.4, 64.13, 69.25, 0.9, 10.85)\nSM_VK_Prop_BeeBench_inst 1567.45 64.6 1.5 (1566.0

# ==============================================================================================================
# [0018] 2026-09-23 19:47:56  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_play"
print(shot("vplay_04_mill_ramp_head",(1576.0,50.5,5.5),(1573.5,61.5,1.4),lens=30,res=(1400,900),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_play\\vplay_04_mill_ramp_head.png\n"}

# ==============================================================================================================
# [0019] 2026-09-23 19:48:22  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
for nm in ("SM_VK_Prop_HerbBundles_inst","SM_VK_Prop_DryingRack_Herbs_inst"):
    o=bpy.data.objects[nm]; ev=o.evaluated_get(dg); me=ev.to_mesh()
    pts=[o.matrix_world@v.co for v in me.vertices]
    low=[p for p in pts if p.z<o.location.z+0.08]
    # cluster feet by x
    xs=sorted(set(round(p.x,1) for p in low))
    print(nm,"foot verts x",xs[:3],'..',xs[-3:],"y",round(min(p.y for p in low),2),round(max(p.y for p in low),2))
    ev.to_mesh_clear()
    # terrain under feet corners
    for (x,y) in [(min(p.x for p in low),min(p.y for p in low)),(max(p.x for p in low),min(p.y for p in low)),(max(p.x for p in low),max(p.y for p in low)),(min(p.x for p in low),max(p.y for p in low))]:
        z0=10.0; r=None
        for _ in range(8):
            hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,z0)),Vector((0,0,-1)))
            if not hit: break
            if 'Chunk' in ob.name: r=round(loc.z,2); break
            z0=loc.z-0.01
        print("  foot",round(x,2),round(y,2),"terrain z",r)
# the odd z0 hit at (1571.8,61.26)
z0=10.0
for _ in range(8):
    hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((1571.8,61.26,z0)),Vector((0,0,-1)))
    if not hit: print("nohit"); break
    print(ob.name,round(loc.z,2))
    if 'Chunk' in ob.name: break
    z0=loc.z-0.01
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_HerbBundles_inst foot verts x [1570.6, 1570.7, 1570.8] .. [1572.9, 1573.0, 1573.1] y 60.75 61.5\n fo
# ot 1570.55 60.75 terrain z 1.5\n foot 1573.05 60.75 terrain z 1.12\n foot 1573.05 61.5 terrain z 1.5\n foot 1570.55 61.5 terrain z 1.5\nSM_VK_Prop_Dry
# ingRack_Herbs_inst foot verts x [1574.1, 1574.9] .. [1574.1, 1574.9] y 61.76 63.44\n foot 1574.06 61.76 terrain z 1.5\n foot 1574.94 61.76 terrain z 1
# .5\n foot 1574.94 63.44 terrain z 1.5\n foot 1574.06 63.44 terrain z 1.5\nSM_VK_Prop_HerbBundles_inst 1.82\nSM_VK_Prop_HerbBundles_inst 1.5\nVKV_Chunk
# _1_1 0.0\n"}

# ==============================================================================================================
# [0020] 2026-09-23 19:48:55  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.data.scenes["VillageKit"]
o=bpy.data.objects["SM_VK_Prop_HerbBundles_inst"]; ev=o.evaluated_get(dg); me=ev.to_mesh()
pts=[o.matrix_world@v.co for v in me.vertices]
east=[p for p in pts if p.z<o.location.z+0.1 and p.x>1572.3]
print(len(east),"x",round(min(p.x for p in east),2),round(max(p.x for p in east),2),"y",round(min(p.y for p in east),2),round(max(p.y for p in east),2))
ev.to_mesh_clear()
import numpy as np
for x in np.linspace(min(p.x for p in east),max(p.x for p in east),4):
    for y in np.linspace(min(p.y for p in east),max(p.y for p in east),3):
        z0=1.45; # cast from just below prop base down? no - cast from 10 and filter to terrain objects only by iterating
        hit,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((x,y,1.49)),Vector((0,0,-1)))
        print(round(x,2),round(y,2), ob.name if hit else None, round(loc.z,2) if hit else None)
# ---- result ----
# {"result":"Code executed successfully: 32 x 1572.75 1573.05 y 60.75 61.05\n1572.75 60.75 VKV_Chunk_1_1 1.12\n1572.75 60.9 VKV_Chunk_1_1 1.2\n1572.75 6
# 1.05 VKV_Chunk_1_1 1.28\n1572.85 60.75 VKV_Chunk_1_1 1.12\n1572.85 60.9 VKV_Chunk_1_1 1.2\n1572.85 61.05 VKV_Chunk_1_1 1.28\n1572.95 60.75 VKV_Chunk_1
# _1 1.12\n1572.95 60.9 VKV_Chunk_1_1 1.2\n1572.95 61.05 VKV_Chunk_1_1 1.28\n1573.05 60.75 VKV_Chunk_1_1 1.12\n1573.05 60.9 VKV_Chunk_1_1 1.2\n1573.05 6
# 1.05 VKV_Chunk_1_1 1.28\n"}

# ==============================================================================================================
# [0021] 2026-09-23 19:49:18  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_render"].as_string())
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2\rereview\verify_play"
print(shot("vplay_05_herb_post_closeup",(1576.5,58.0,2.2),(1572.9,60.9,1.4),lens=40,res=(1200,800),outdir=OUT))
# ---- result ----
# {"result":"Code executed successfully: C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-
# f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\renders2\\rereview\\verify_play\\vplay_05_herb_post_closeup.png\n"}
