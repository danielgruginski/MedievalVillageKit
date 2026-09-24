# ===================== VALLEY TOWN: the whole kit on marching-squares terrain =====================
# exec inside vk_kit_ns() (kit core + expansion modules + terrain)
import bpy, math, random, re
import numpy as np
from mathutils import Vector

TOWN_W,TOWN_H=72,56
TOWN_ORIGIN=(1500.0,0.0,0.0)              # map-local (0,0) in world
TOWN_COLL="VK_ValleyTown"; TOWN_TERR="VK_ValleyTerrain"
WALL_S,WALL_N,WALL_W,WALL_E=25,46,23,63    # wall lines on vertex rows/cols (y=3*WALL_S ...)
GATE_I=42                                  # gatehouse centred on vertex column 42 = the axis of the road cells 41-42
ROAD_I=(41,42)                             # main road cell columns
POSTERN_J=30                               # west postern: cell row of the opening in the west wall

def town_grid(seed=11):
    rng=np.random.default_rng(seed); W,H=TOWN_W,TOWN_H
    G=TGrid(W,H); L=np.ones((H,W),np.int32)
    jj,ii=np.mgrid[0:H,0:W]
    # --- river (level 0): water rows 12..15, sandy banks 10..11 and 16..17
    L[10:18,:60]=0; G.water[12:16,:60]=True
    # --- lake to the east: rounded (superellipse) level-0 basin and water, so no square notches where the banks meet it
    basin=(np.abs((ii-65.5)/8.5)**4+np.abs((jj-11.8)/7.2)**4)<1.0
    L[basin]=0
    lake=(np.abs((ii-64.5)/6.5)**4+np.abs((jj-12.5)/5.0)**4)<1.0     # ends one sand cell short of the map edge
    G.water[lake]=True
    G.water[12:16,58:60]=True
    # mill inlet (level-0 pad north of the river; col 23 keeps the ramp at cols 24-25 legal)
    L[16:20,23:30]=0
    # --- town plateau (level 2) and the west bench
    L[24:47,20:64]=2
    L[24:34,0:20]=2
    L[23,40:44]=2                                     # level-2 apron under the gatehouse front
    # --- west ridge: level 3 (quarry hill level 4 at i 11..18)
    L[34:47,0:20]=3
    L[34:47,11:19]=4
    L[39:47,0:9]=4
    L[31:34,12:14]=4; L[31:34,16:18]=4               # hill shoulders flush with the quarry pit's side walls (row 30 stays level 2)
    # --- north ridge rows 47.. (levels 3..5 noise)
    for j in range(47,H):
        for i in range(W):
            n=3+int(np.clip(round(1.1*math.sin(i/4.1)+0.9*math.cos(i/2.7+j/2.1)+(j-47)*0.35),0,2))
            L[j,i]=max(L[j,i],n)
    G.level[:]=L
    G.ground[(G.level==0)&(~G.water)]=3
    G.ground[G.level>=5]=4
    # --- roads
    r0,r1=ROAD_I
    for j in range(0,32):
        for i in (r0,r1):
            if not G.water[j,i]: G.ground[j,i]=1
    G.ground[25:32,r0:r1+1]=2                         # cobbled main street inside the gate
    G.ground[31:36,35:48]=2                           # plaza (col 35: in front of the inn)
    G.ground[39:42,24:41]=2                           # skyline street (between its house rows)
    G.ground[36:39,39:41]=2                           # lane from the plaza up to the skyline street
    G.ground[36:39,47:52]=2                           # chapel forecourt, open to the plaza's north-east corner
    G.ground[29,44:62]=2                              # street in front of the terrace
    G.ground[POSTERN_J,WALL_W:r0]=2                   # west-quarter street: postern -> main street (houses face it)
    G.ground[POSTERN_J,11:WALL_W]=1                   # lane from the west bench road to the postern
    G.ground[9,11:r0]=1                               # river road on the south land: footbridge lane -> main road
    # ramps: south land -> bank, bank -> meadow, meadow -> gate apron (all 2 wide on the road)
    for i in (r0,r1):
        G.ramp[10,i]=3                                # (level 0 at j 10) up to j 9 (level 1), going south
        G.ramp[17,i]=1                                # bank (j 17) up to meadow j 18
        G.ramp[22,i]=1                                # meadow (j 22) up to the gate apron j 23
    # west road: bank ramps on both sides of the footbridge, meadow -> bench ramp, bench -> ridge stair
    for i in (9,10):
        G.ramp[10,i]=3; G.ramp[17,i]=1; G.ramp[23,i]=1
        for j in range(9,34):
            if not G.water[j,i]: G.ground[j,i]=1
    G.ramp[33,9]=1; G.stair[33,9]=True
    G.ramp[36,10]=2; G.stair[36,10]=True              # west ridge (level 3) up to the quarry hill (level 4, crane)
    G.ramp[19,24]=1; G.ramp[19,25]=1                  # mill inlet pad up to the meadow (west of the mill house)
    G.ramp[5,66]=3; G.ramp[5,67]=3                    # lake shore up to the south land (fisher-hut path)
    # farm plots on the south land
    G.ground[6:9,2:10]=1
    # stiff: ramps (R and H), plaza, roads in town, gate apron, postern lane
    for (j,i) in zip(*np.nonzero(G.ramp)):
        G.stiff[j,i]=True; di,dj=((0,1),(1,0),(0,-1),(-1,0))[G.ramp[j,i]-1]; G.stiff[j+dj,i+di]=True
    G.stiff[G.ground==2]=True
    G.stiff[23,40:44]=True; G.stiff[POSTERN_J,11:WALL_W]=True
    return G

# ---------------------------------------------------------------- placement with footprint checks
PROP_RE=re.compile(r"^SM_VK_(Prop_|Pile_)")
WALL_MOUNTED=("Prop_Sign","Prop_Lantern","Prop_Festoon","Prop_Banner","Prop_Bunting","Prop_Wreath","Prop_Shelf","FlowerBox","Window","Hanging","Awning","Chimney")
DOOR_PARTS=("Step","Stair","Doormat","Porch","Mat","Planter","FlowerPot")      # belong in front of a door: never slid away
SPANNING=("TreadwheelCrane","Crane","Bridge","Pier","Jetty","Chute","Sluice")   # deliberately span levels
FLOATING=("Barge","Rowboat","Boat","Buoy","Raft")
def base_name(o): return o.name.split("_inst")[0]

class TownPlacer:
    def __init__(s,G,coll):
        s.G=G; s.coll=coll; s.occ=np.zeros((G.H,G.W),np.int32); s.log=[]; s.n=0; s.boxes=[]; s._mb={}; s.hash={}; s.tags={}
        s.vl=bpy.data.scenes["VillageKit"].view_layers[0]
    def world(s,x,y,rot=0.0): return (TOWN_ORIGIN[0]+x,TOWN_ORIGIN[1]+y,math.radians(rot))
    def cells_of_bbox(s,x0,x1,y0,y1,shrink=0.45):
        i0=int(math.floor((x0+shrink)/3)); i1=int(math.floor((x1-shrink)/3)); j0=int(math.floor((y0+shrink)/3)); j1=int(math.floor((y1-shrink)/3))
        return [(i,j) for j in range(j0,j1+1) for i in range(i0,i1+1)]
    def mesh_bounds(s,me):
        if me.name not in s._mb:
            co=np.empty(len(me.vertices)*3); me.vertices.foreach_get("co",co); co=co.reshape(-1,3)
            s._mb[me.name]=tuple(co.min(0))+tuple(co.max(0)) if len(co) else (0,)*6
        return s._mb[me.name]
    def obj_corners(s,o):
        """map-local XY corners of an instance's mesh bbox (no depsgraph update needed)"""
        x0,y0,_,x1,y1,_=s.mesh_bounds(o.data); c,sn=math.cos(o.rotation_euler.z),math.sin(o.rotation_euler.z)
        kx,ky=o.scale.x,o.scale.y; ox,oy=o.location.x-TOWN_ORIGIN[0],o.location.y-TOWN_ORIGIN[1]
        return [(ox+x*kx*c-y*ky*sn,oy+x*kx*sn+y*ky*c) for x in (x0,x1) for y in (y0,y1)]
    def obj_bbox(s,o):
        P=s.obj_corners(o); xs=[p[0] for p in P]; ys=[p[1] for p in P]
        return (min(xs),max(xs),min(ys),max(ys))
    def obj_zrange(s,o):
        b=s.mesh_bounds(o.data); return (o.location.z+b[2]*o.scale.z,o.location.z+b[5]*o.scale.z)
    def obj_aabb(s,o):
        x0,x1,y0,y1=s.obj_bbox(o); z0,z1=s.obj_zrange(o); return (x0,x1,y0,y1,z0,z1)
    def hash_add(s,objs,tag):
        """per-object AABBs in a 3 m spatial hash: the precise clash test between buildings, walls and placed pieces"""
        for o in objs:
            if o.type!="MESH": continue
            b=s.obj_aabb(o)
            for ci in range(int(b[0]//3),int(b[1]//3)+1):
                for cj in range(int(b[2]//3),int(b[3]//3)+1): s.hash.setdefault((ci,cj),[]).append(b+(tag,o.name))
    def clashes(s,objs,tag,shrink=0.12):
        out=[]
        for o in objs:
            if o.type!="MESH": continue
            a=s.obj_aabb(o); seen={o.name}
            for ci in range(int(a[0]//3),int(a[1]//3)+1):
                for cj in range(int(a[2]//3),int(a[3]//3)+1):
                    for e in s.hash.get((ci,cj),()):
                        if e[6]==tag or e[7] in seen: continue
                        if a[0]+shrink<e[1] and e[0]<a[1]-shrink and a[2]+shrink<e[3] and e[2]<a[3]-shrink and a[4]+0.05<e[5] and e[4]<a[5]-0.05:
                            seen.add(e[7]); out.append((o.name,e[7],e[6]))
        return out
    def occupy(s,box,tag=-1,shrink=0.3):
        for (i,j) in s.cells_of_bbox(*box,shrink=shrink):
            if 0<=i<s.G.W and 0<=j<s.G.H and not s.occ[j,i]: s.occ[j,i]=tag
    def near_occ(s,i,j,r):
        G=s.G; return bool(s.occ[max(0,j-r):min(G.H,j+r+1),max(0,i-r):min(G.W,i+r+1)].any())
    def near_bld(s,i,j,r):
        G=s.G; return bool((s.occ[max(0,j-r):min(G.H,j+r+1),max(0,i-r):min(G.W,i+r+1)]>0).any())
    def build(s,label,fn,x,y,rot=0.0,level=None,allow_higher=False,allow_water=False,check=True,z=None,undo_on_clash=False,**kw):
        """run a builder at map-local (x,y) (origin) with rotation; lift to the cell level; check and register the footprint"""
        G=s.G; ci,cj=int(x//3),int(y//3)
        lv=G.level[min(max(cj,0),G.H-1),min(max(ci,0),G.W-1)] if level is None else level
        zz=lv*TIER if z is None else z
        before=set(s.coll.all_objects)
        try: fn(s.coll,s.world(x,y,rot),**kw)
        except Exception as e:
            s.log.append((label,"ERROR",str(e)[:160])); return None
        new=[o for o in s.coll.all_objects if o not in before]
        for o in new: o.location.z+=zz
        s.vl.update()
        xs=[];ys=[]
        for o in new:
            if o.type!="MESH": continue
            for c in o.bound_box:
                w=o.matrix_world@Vector(c); xs.append(w.x-TOWN_ORIGIN[0]); ys.append(w.y-TOWN_ORIGIN[1])
        if check and xs:
            box=(min(xs),max(xs),min(ys),max(ys)); cells=s.cells_of_bbox(*box)
            bad=[]
            for (i,j) in cells:
                if not (0<=i<G.W and 0<=j<G.H): bad.append(("out",i,j)); continue
                if G.water[j,i] and not allow_water: bad.append(("water",i,j))
                elif G.level[j,i]!=lv and not (allow_higher and G.level[j,i]>lv): bad.append(("lvl",i,j,int(G.level[j,i])))
                elif s.occ[j,i]: bad.append(("occ",i,j,int(s.occ[j,i])))
            hits=s.clashes(new,label)
            if undo_on_clash and (hits or any(b[0] in ("out","lvl","water") for b in bad)):
                for o in new: bpy.data.objects.remove(o)
                return None
            s.n+=1; s.tags[label]=s.n
            s.hash_add(new,label)
            if hits: s.log.append((label,"CLASH",len(hits),hits[:8]))
            for (i,j) in cells:
                if 0<=i<G.W and 0<=j<G.H: s.occ[j,i]=s.n; G.stiff[j,i]=True
            s.boxes.append((label,)+box)
            bad=[b for b in bad if b[0]!="occ"]
            if bad: s.log.append((label,len(bad),bad[:6]))
        return new
    def P(s,piece,x,y,rot=0.0,z=None,style=None,scale=1.0,occupy=False):
        G=s.G; ci,cj=int(x//3),int(y//3)
        zz=(G.level[min(max(cj,0),G.H-1),min(max(ci,0),G.W-1)]*TIER) if z is None else z
        if piece is None or bpy.data.objects.get(piece) is None: s.log.append((piece,"missing")); return None
        o=place_v(s.coll,piece,x,y,0,rot,s.world(0,0,0),style or {}); o.location.z+=zz
        if scale!=1.0: o.scale=(scale,scale,scale)
        if occupy: s.occupy(s.obj_bbox(o))
        s.hash_add([o],"P")
        return o

def door_front_cell(T,o,dist=1.6):
    """cell just outside a *_Door wall module (wall modules face local -Y)"""
    r=o.rotation_euler.z; nx,ny=math.sin(r),-math.cos(r)
    x=o.location.x-TOWN_ORIGIN[0]+nx*dist; y=o.location.y-TOWN_ORIGIN[1]+ny*dist
    return int(x//3),int(y//3)
def is_door(o): return "_Door" in o.name and not o.name.startswith("SM_VK_Prop")
def pave(T,a,b,ground=2,own=None):
    """L-shaped street from cell a to cell b through free cells or cells of the building `own` (tries both elbow orders)"""
    G=T.G; ok_tags={0}|({T.tags[own]} if own in T.tags else set())
    def path(first_i):
        (i,j),(bi,bj)=a,b; cells=[(i,j)]
        seq=(("i",bi),("j",bj)) if first_i else (("j",bj),("i",bi))
        for ax,t in seq:
            while (i if ax=="i" else j)!=t:
                if ax=="i": i+=1 if t>i else -1
                else: j+=1 if t>j else -1
                cells.append((i,j))
        return cells
    for first_i in (True,False):
        cells=path(first_i)
        if all(0<=i<G.W and 0<=j<G.H and T.occ[j,i] in ok_tags and G.level[j,i]==G.level[a[1],a[0]] for (i,j) in cells):
            for (i,j) in cells: G.ground[j,i]=ground; G.stiff[j,i]=True
            return cells
    T.log.append(("pave failed",a,b)); return None

# ---------------------------------------------------------------- districts
def town_walls(T):
    Wm="SM_VK_TownWall_Straight"; zt=2*TIER
    ys,yn,xw,xe=3*WALL_S,3*WALL_N,3*WALL_W,3*WALL_E
    gx=3*GATE_I                                       # gate centred on the road (cells 41-42)
    towers_x=[3*i for i in (29,36,50,57)]; towers_y=[3*j for j in (33,39)]
    for i in range(WALL_W,WALL_E):
        x=3*i+1.5
        if abs(x-gx)>3: T.P(Wm,x,ys,0,z=zt,occupy=True)
        T.P(Wm,x,yn,180,z=zt,occupy=True)
    for j in range(WALL_S,WALL_N):
        y=3*j+1.5
        T.P("SM_VK_TownWall_Postern" if j==POSTERN_J else Wm,xw,y,-90,z=zt,occupy=True); T.P(Wm,xe,y,90,z=zt,occupy=True)
    T.P("SM_VK_TownWall_Corner_Out",xw,ys,0,z=zt,occupy=True); T.P("SM_VK_TownWall_Corner_Out",xe,ys,90,z=zt,occupy=True)
    T.P("SM_VK_TownWall_Corner_Out",xe,yn,180,z=zt,occupy=True); T.P("SM_VK_TownWall_Corner_Out",xw,yn,-90,z=zt,occupy=True)
    for x in towers_x: T.P("SM_VK_TownWall_Tower_Round",x,ys,0,z=zt,style={"roof":"Slate"},occupy=True); T.P("SM_VK_TownWall_Tower_Round",x,yn,180,z=zt,style={"roof":"Slate"},occupy=True)
    for y in towers_y: T.P("SM_VK_TownWall_Tower_Round",xw,y,-90,z=zt,style={"roof":"Slate"},occupy=True); T.P("SM_VK_TownWall_Tower_Round",xe,y,90,z=zt,style={"roof":"Slate"},occupy=True)
    # the whole wall band (both sides of every wall line) stays free of houses, trees and grass tufts
    for i in range(WALL_W-1,WALL_E+1):
        for j in (WALL_S-1,WALL_S,WALL_N-1,WALL_N):
            if not T.occ[j,i]: T.occ[j,i]=-1
    for j in range(WALL_S-1,WALL_N+1):
        for i in (WALL_W-1,WALL_W,WALL_E-1,WALL_E):
            if not T.occ[j,i]: T.occ[j,i]=-1
    # gatehouse with its timber storey, roofs, portcullis and leaves (defence module helper)
    T.P("SM_VK_Gatehouse_Block",gx,ys,0,z=zt,occupy=True)
    P=def_placer(T.coll,T.world(0,0,0),{"roof":"Slate"})
    before=set(T.coll.all_objects)
    def_dress_gatehouse(lambda n,x,y,z=0.0,r=0.0,st=None,**pr: P(n,x,y,z,r,st,**pr),gx,{"roof":"Slate"})
    # def_dress_gatehouse works in wall-local coordinates with the wall on y=0: shift the new objects onto the wall line
    for o in T.coll.all_objects:
        if o not in before: o.location.y+=ys; o.location.z+=zt
    for i in range(GATE_I-3,GATE_I+3):
        for j in range(WALL_S-2,WALL_S+2): T.occ[j,i]=T.occ[j,i] or -1
    # lantern pair inside the postern
    for s_ in (-1,1): T.P("SM_VK_Prop_LampPost",xw+2.6,3*POSTERN_J+1.5+s_*2.1,-90,z=zt)

def town_river(T):
    G=T.G
    # stone bridge on the main road (spans over water rows 12..15, ramps on bank rows 11 and 16)
    bx=3*GATE_I; by=3*14
    T.occupy((bx-4,bx+4,by-10,by+10))
    for y in (by-3,by+3): T.P("SM_VK_Bridge_Stone_Span",bx,y,90,z=0.0)
    T.P("SM_VK_Bridge_Stone_Pier",bx,by,90,z=0.0)
    T.P("SM_VK_Bridge_Stone_Ramp",bx,by+7.5,90,z=0.0); T.P("SM_VK_Bridge_Stone_Ramp",bx,by-7.5,-90,z=0.0)
    for s_ in (-1,1):
        for x in (-3.3,3.3): T.P("SM_VK_Prop_LampPost",bx+x,by+s_*8.4,90 if x<0 else -90,z=0.0)
    # wooden footbridge on the west road (cells 9-10), bank ramps at rows 10 and 17
    wx=3*10
    T.occupy((wx-3,wx+3,by-10,by+10))
    for (p,dy,rot) in (("SM_VK_Bridge_Wood_End",-7.5,90),("SM_VK_Bridge_Wood_Mid",-4.5,90),("SM_VK_Bridge_Wood_Mid",-1.5,90),
                       ("SM_VK_Bridge_Wood_Mid",1.5,90),("SM_VK_Bridge_Wood_Mid",4.5,90),("SM_VK_Bridge_Wood_End",7.5,-90)):
        T.P(p,wx,by+dy,rot,z=0.0)
    for dy in (-6.0,-3.0,0.0,3.0,6.0): T.P("SM_VK_Bridge_Wood_Bent",wx,by+dy,90,z=0.0)
    # watermill on the inlet pad: end wall on the bank line y=48, wheel over the river
    T.build("watermill",build_watermill,3*27,48+4.5,-90,level=0,allow_water=True,seed=4)
    # quay with a moored barge west of the bridge (north bank)
    for k,x in enumerate((3*33+1.5,3*34+1.5,3*35+1.5,3*36+1.5)):
        T.P("SM_VK_Quay_Stair" if k==2 else "SM_VK_Quay_Straight",x,48.45,0,z=0.0)
    for x in (3*33,3*37): T.P("SM_VK_Quay_Post",x,48.75,0,z=0.0)
    T.occupy((3*33,3*37,47.5,53.0))
    T.P("SM_VK_Prop_Barge",3*35,45.8,0,z=-0.6,style={"shutter":"Red"})
    T.P("SM_VK_Prop_Crates",3*33+2,50.4,10,z=0.0); T.P("SM_VK_Prop_Sacks",3*35,50.2,0,z=0.0); T.P("SM_VK_Prop_BarrelStack",3*37-1,50.6,-5,z=0.0)
    # lavoir and smokehouse on the north bank east of the bridge
    T.build("lavoir",build_lavoir,3*47,49.5,0,level=0,allow_water=True,seed=5)
    T.build("smokehouse",build_smokehouse,3*52+1.5,49.5,180,level=0,allow_water=True,seed=6)
    # fisher hut on the lake's south shore, pier into the lake
    T.build("fisher_hut",build_fisher_hut,3*64,24.0,180,level=0,allow_water=True,seed=7)
    T.P("SM_VK_Prop_Rowboat",3*62,36.0,20,z=-0.6,style={"shutter":"Green"})
    T.P("SM_VK_Prop_Rowboat",3*68,42.0,-70,z=-0.6,style={"shutter":"Blue"})

def town_south(T):
    G=T.G
    T.build("longhouse",build_longhouse,3*5+1.5,3*2,0,seed=1)
    T.build("hovel_a",build_hovel,3*13,3*2,0,seed=2)
    T.build("hovel_b",build_hovel,3*18,3*2,0,seed=3,variant="hip")
    T.build("hovel_c",build_hovel,3*23,3*6,0,seed=4,variant="leanto")
    T.build("pigsty",build_pigsty,3*12+1.5,3*6+1.5,0,seed=5)
    T.build("sheepfold",build_sheepfold,3*17+1.5,3*6+1.5,0,seed=6)
    crops=["SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Wheat","SM_VK_Crop_Lavender"]
    for j in range(6,9):
        for i in range(2,10): T.P(crops[(i//2+j)%len(crops)],3*i+1.5,3*j+1.5)
    T.occupy((6.0,30.0,18.0,27.0))
    T.build("camp",build_camp,3*31+1.5,3*4+1.5,0,seed=1)
    T.build("sawpit",build_sawpit_yard,3*37,3*3,0,seed=2)
    T.build("stockpile",build_stockpile,3*37,3*7,0,seed=3,w=2,d=2)
    T.build("palisade",build_palisade_demo,3*53,3*4,0,seed=1)
    T.build("training",build_training_yard,187.5,7.5,90,seed=2)

def town_meadow(T):
    G=T.G
    T.build("tannery",build_tannery,3*4,60.5,0,seed=1)
    T.build("pottery",build_pottery,3*15,3*20+1.5,0,seed=2)
    T.build("dyers",build_dyers_yard,3*20,3*20,0,seed=3)
    T.build("apiary",build_apiary,3*23+1.5,3*21+1.5,0,seed=4)
    T.build("windmill",build_windmill,3*33,3*22,0)
    T.build("granary",build_granary,3*38,3*21,0,seed=5)
    for k,(x,stage) in enumerate(((138.0,0),(153.5,1),(169.0,2))):
        T.build(f"site{stage}",build_construction_site,x,3*22,0,stage=stage,seed=10+k)

def town_west(T):
    G=T.G
    T.build("logcabin",build_logcabin,6,78,0,seed=1)
    T.build("woodcutter",build_woodcutter,19.5,79.5,0,seed=2)
    T.build("forester",build_forester_hut,37.5,78,0,seed=3)
    T.build("charcoal",build_charcoal_burner,52.5,76.5,0,seed=6)
    T.build("mine",build_mine,12,96,0,seed=4,allow_higher=True)
    new=T.build("quarry",build_quarry_yard,45,97.5,0,seed=5,standin=False,allow_higher=True,level=2) or []
    # keep the pit mouth (x 43.6-46.4) open: banker and block pile go to the yard on the lane; the lean-to would sit in the hill
    for o in new:
        b=base_name(o); x,y=o.location.x-TOWN_ORIGIN[0],o.location.y
        if "LeanTo" in b: bpy.data.objects.remove(o)
        elif b=="SM_VK_Prop_Banker": o.location.x=TOWN_ORIGIN[0]+41.5; o.location.y=91.0
        elif b.startswith("SM_VK_Pile_Stone") and 42.5<x<48.5 and 92.0<y<95.5: o.location.x=TOWN_ORIGIN[0]+48.5; o.location.y=91.0

def town_inside(T):
    G=T.G
    # west quarter: fronts face north onto the postern street (row 30), yards toward the south wall
    T.build("merchant",build_merchant_house,3*26+1.5,87,180,seed=1)
    T.build("gablefront",build_townhouse_gablefront,3*31,85.5,180,seed=2)
    T.build("corner_house",build_corner_house,3*36,87,180,seed=3)
    T.build("tower_house",build_tower_house,3*26,3*33,0,seed=4,kind="fortified")
    # skyline street block along the north (its street runs along rows 39..41)
    T.build("skyline",build_skyline_street,3*24+6,3*43,0,seed=5)
    for o in list(T.coll.all_objects):                 # the terrain paints the street: drop the builder's flat road strip
        if o.type=="MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name=="MC_WK_Dirt": bpy.data.objects.remove(o)
    # east quarter: terrace with its back to the south wall, facing the street at row 29
    T.build("terrace",build_terrace,3*53+1.5,84,180,seed=2,units=4)
    T.build("festival",build_festival_green,3*53,3*33,0,seed=6)
    T.build("brewery",build_brewery,3*58+1.5,116.0,0,seed=7)
    # chapel faces the plaza; a cobbled path runs from its door to the plaza's north-east corner
    ox,oy,orz=fp_origin(48,39,4,2,180)
    new=T.build("chapel",lambda c,o: build_chapel(c,o,n=4,roof="Blue",tower=True),ox,oy,180) or []
    doors=sorted((o for o in new if is_door(o)),key=lambda o: math.dist(door_front_cell(T,o),(47,35)))
    if doors: pave(T,door_front_cell(T,doors[0]),(47,35),own="chapel")
    # landmarks: the smithy's glowing forge greets you right inside the gate, the inn fronts the plaza
    T.build("smithy",build_smithy,135.0,83.5,-90,seed=33)
    T.build("inn",build_inn,102.0,97.5,90,seed=34)
    # plaza dressing (lamps come after the infill so they can dodge porches and eaves)
    px,py=3*GATE_I,3*33+1.5
    T.P("SM_VK_Prop_MarketCross",px,py,0,occupy=True)
    T.P("SM_VK_Prop_NoticeBoard",px-6,py+2.5,180)
    for k,(x,y,rt) in enumerate(((px-10,py-3,0),(px-10,py+3.5,180),(px+8,py-3,0),(px+11,py+2.5,90))):
        T.P(("SM_VK_MarketStall_Baker","SM_VK_MarketStall_Fishmonger","SM_VK_MarketStall_Potter","SM_VK_MarketStall_Draper")[k],
            x,y,rt,style={"cloth":("Red","Blue","Green","Yellow")[k]})
    T.P("SM_VK_Prop_Stocks",px+4,py+5,180); T.P("SM_VK_Banner_Pole",px+14,py+1)
    T.plaza=(px,py)

def town_plaza_lamps(T):
    if not hasattr(T,"plaza"): return
    px,py=T.plaza
    for (x,y) in ((px-15,py-3.9),(px+15,py-3.9),(px-15,py+3.9),(px+15,py+3.9)):
        if any(b[1]-0.6<x<b[2]+0.6 and b[3]-0.6<y<b[4]+0.6 for b in T.boxes): T.log.append(("lamp skipped",x,y)); continue
        T.P("SM_VK_Prop_LampPost",x,y)

def district_roofs(i,j):
    """roof palette per district: terracotta + slate in the west, slate + shingle in the east; Blue only on landmarks"""
    if j>=38: return ["Slate","Slate","Red","Shingle"]
    if i<=GATE_I-2: return ["Red","Red","Slate","Shingle"]
    return ["Slate","Shingle","Shingle","Green"]

def town_infill(T,seed=23,max_houses=40):
    """fill free town cells with kit houses that face a street or the plaza"""
    G=T.G; rng=random.Random(seed)
    roads=(G.ground==1)|(G.ground==2)
    def free(i,j):
        return (WALL_W+1<=i<WALL_E-1 and WALL_S+1<=j<WALL_N-1 and G.level[j,i]==2 and not T.occ[j,i] and not roads[j,i] and not G.ramp[j,i])
    cands=[]
    for j0 in range(WALL_S+1,WALL_N-1):
        for i0 in range(WALL_W+1,WALL_E-1):
            for n in (3,2):
                for rot in (0,90,180,270):
                    w,d=(n,2) if rot in (0,180) else (2,n)
                    cells=[(i,j) for j in range(j0,j0+d) for i in range(i0,i0+w)]
                    if not all(free(i,j) for (i,j) in cells): continue
                    # front row (outside the -Y face after rotation) must touch a road
                    if rot==0:   front=[(i,j0-1) for i in range(i0,i0+w)]
                    elif rot==180: front=[(i,j0+d) for i in range(i0,i0+w)]
                    elif rot==90: front=[(i0+w,j) for j in range(j0,j0+d)]
                    else: front=[(i0-1,j) for j in range(j0,j0+d)]
                    score=sum(1 for (i,j) in front if 0<=i<G.W and 0<=j<G.H and roads[j,i])
                    if score==0: continue
                    cands.append((score+rng.random(),i0,j0,n,rot))
    cands.sort(reverse=True)
    placed=0
    for (sc,i0,j0,n,rot) in cands:
        if placed>=max_houses: break
        w,d=(n,2) if rot in (0,180) else (2,n)
        cells=[(i,j) for j in range(j0,j0+d) for i in range(i0,i0+w)]
        if not all(free(i,j) for (i,j) in cells): continue
        ox,oy,orz=fp_origin(i0,j0,n,2,rot)
        st=random_style(seed*13+placed)
        st["roof"]=rng.choice(district_roofs(i0,j0))
        stories=rng.choice([2,2,2,1,3]) if n==3 else rng.choice([1,2,2])
        stories=min(stories,2)
        new=T.build(f"infill{placed}",lambda c,o,n=n,stories=stories,st=st: build_house_v(c,o,n,stories,st),ox,oy,rot,check=True,undo_on_clash=True)
        if new is None: continue
        for (i,j) in cells: T.occ[j,i]=T.occ[j,i] or 999
        placed+=1
    return placed

def town_scatter(T,seed=19,disp=None):
    G=T.G; rng=random.Random(seed)
    def D(x,y,z):
        if disp is None: return x,y
        d=disp(np.array([[x,y,z]],float))[0]; return x+d[0],y+d[1]
    def safe(i,j,inset):
        l=G.level[j,i]; x0,x1,y0,y1=3*i+0.3,3*i+2.7,3*j+0.3,3*j+2.7
        for (di,dj,side) in ((-1,0,0),(1,0,1),(0,-1,2),(0,1,3)):
            ii,jj=G.cell(i+di,j+dj)
            if G.level[jj,ii]!=l or G.water[jj,ii]:
                if side==0: x0=3*i+inset
                if side==1: x1=3*i+3-inset
                if side==2: y0=3*j+inset
                if side==3: y1=3*j+3-inset
        if x0>=x1 or y0>=y1: return None
        return rng.uniform(x0,x1),rng.uniform(y0,y1)
    roads=(G.ground==1)|(G.ground==2)
    def near(mask,i,j,r): return bool(mask[max(0,j-r):min(G.H,j+r+1),max(0,i-r):min(G.W,i+r+1)].any())
    # tree spacing: >=1.5 m between any trees, >=2.5 m between the same model, >=12 m between willows
    tgrid={}; willows=[]
    def put_tree(name,x,y,z,scale=1.0):
        ci,cj=int(x//3),int(y//3)
        for di in (-1,0,1):
            for dj in (-1,0,1):
                for (tx,ty,tn) in tgrid.get((ci+di,cj+dj),()):
                    d=math.hypot(tx-x,ty-y)
                    if d<1.5 or (tn==name and d<2.5): return None
        if name=="SM_VK_Tree_Willow":
            if any(math.hypot(wx-x,wy-y)<12.0 for (wx,wy) in willows): return None
            willows.append((x,y))
        o=T.P(name,x,y,rng.uniform(0,360),z=z,scale=scale)
        if o: tgrid.setdefault((ci,cj),[]).append((x,y,name))
        return o
    forest_n=["SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Birch","SM_VK_Tree_Oak_Autumn"]
    big=("SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Apple","SM_VK_Tree_Birch")
    ramp_top=np.zeros((G.H,G.W),bool)
    for (j,i) in zip(*np.nonzero(G.ramp)):
        di,dj=((0,1),(1,0),(0,-1),(-1,0))[G.ramp[j,i]-1]
        for s_ in (1,2):
            ii,jj=i+di*s_,j+dj*s_
            if 0<=ii<G.W and 0<=jj<G.H: ramp_top[jj,ii]=True
    high=(G.level>=3)
    def tree_ok(i,j): return 1<=i<G.W-1 and 1<=j<G.H-1 and not near(ramp_top,i,j,1)
    no_willow=np.zeros((G.H,G.W),bool)
    no_willow|=roads; no_willow|=(G.ramp>0); no_willow|=(T.occ!=0)
    no_willow[:,39:45]=True; no_willow[:,8:12]=True; no_willow[15:18,32:39]=True
    for j in range(G.H):
        for i in range(G.W):
            if G.water[j,i] or G.stiff[j,i] or T.occ[j,i] or G.ground[j,i] in (1,2) or G.ramp[j,i]: continue
            z=G.level[j,i]*TIER
            inside_town=(WALL_W<=i<WALL_E and WALL_S<=j<WALL_N)
            if G.level[j,i]>=3 or j>=47:
                if not T.near_occ(i,j,1) and tree_ok(i,j):
                    for _ in range(2 if rng.random()<0.55 else 1):
                        p=safe(i,j,1.1)
                        if p and rng.random()<0.85:
                            put_tree(rng.choice(forest_n[:3] if G.level[j,i]>=4 else forest_n),p[0],p[1],z,scale=rng.uniform(0.8,1.15))
                if rng.random()<0.45:
                    p=safe(i,j,0.6)
                    if p: T.P(rng.choice(["SM_VK_Plant_Fern","SM_VK_Bush_Round","SM_VK_Rock_Small_A","SM_VK_Mushrooms_Brown","SM_VK_Rock_Boulder_A"]),p[0],p[1],rng.uniform(0,360),z=z)
            elif inside_town:
                # kitchen gardens behind and beside the houses, a few trees and flowers elsewhere
                if T.near_bld(i,j,1) and not near(roads,i,j,1) and rng.random()<0.2:
                    G.ground[j,i]=1; G.wear[j,i]=0; T.occ[j,i]=-2
                    T.P(rng.choice(["SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot"]),3*i+1.5,3*j+1.5,rng.choice((0,90,180,270)),z=z,scale=0.8)
                    continue
                r_=rng.random()
                if r_<0.14 and not T.near_bld(i,j,1) and not roads[j,i]:
                    p=safe(i,j,1.0)
                    if p: put_tree(rng.choice(["SM_VK_Tree_Blossom","SM_VK_Tree_Apple"]),p[0],p[1],z)
                elif r_<0.22 and not near(roads,i,j,1):
                    p=safe(i,j,0.8)
                    if p: T.P(rng.choice(["SM_VK_Bush_Hydrangea","SM_VK_Plant_Wildflowers","SM_VK_Bush_Round"]),p[0],p[1],rng.uniform(0,360),z=z)
            elif G.level[j,i]==0 and G.ground[j,i]==3:
                if rng.random()<0.35:
                    p=safe(i,j,0.5)
                    if p:
                        pick=rng.choice(["SM_VK_Plant_Reeds","SM_VK_Rock_Pebbles","SM_VK_Plant_Reeds","SM_VK_Tree_Willow"])
                        if pick=="SM_VK_Tree_Willow":
                            if not near(no_willow,i,j,2) and tree_ok(i,j): put_tree(pick,p[0],p[1],z)
                        else: T.P(pick,p[0],p[1],rng.uniform(0,360),z=z)
            else:
                r_=rng.random(); pt=0.3 if near(high,i,j,2) else 0.13        # denser fringe at the foot of the ridges
                if r_<pt:
                    p=safe(i,j,1.2)
                    name=rng.choice(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Apple","SM_VK_Tree_Birch","SM_VK_Bush_Large"])
                    if p and tree_ok(i,j) and not T.near_bld(i,j,2 if name in big else 1) and not roads[j,i]:
                        put_tree(name,p[0],p[1],z,scale=rng.uniform(0.85,1.1))
                elif r_<pt+0.13 and not near(roads,i,j,1):
                    p=safe(i,j,0.6)
                    if p: T.P(rng.choice(["SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers","SM_VK_Bush_Round","SM_VK_Rock_Small_B"]),p[0],p[1],rng.uniform(0,360),z=z)
    # lip grass and seam rocks along straight level-change borders
    for j in range(G.H):
        for i in range(G.W):
            for (di,dj) in ((1,0),(0,1)):
                ii,jj=i+di,j+dj
                if ii>=G.W or jj>=G.H: continue
                la,lb=G.level[j,i],G.level[jj,ii]
                if la==lb or G.water[j,i] or G.water[jj,ii] or G.ramp[j,i] or G.ramp[jj,ii]: continue
                hi_i,hi_j,lo_i,lo_j=(i,j,ii,jj) if la>lb else (ii,jj,i,j)
                if T.occ[hi_j,hi_i] or T.occ[lo_j,lo_i] or roads[hi_j,hi_i]: continue
                ox,oy=(lo_i-hi_i),(lo_j-hi_j); tx,ty=abs(oy),abs(ox)
                cx=1.5*(hi_i+lo_i)+1.5; cy=1.5*(hi_j+lo_j)+1.5
                def straight(sgn):
                    a_=G.cell(hi_i+sgn*tx,hi_j+sgn*ty); b_=G.cell(lo_i+sgn*tx,lo_j+sgn*ty)
                    return G.level[a_[1],a_[0]]==G.level[hi_j,hi_i] and G.level[b_[1],b_[0]]==G.level[lo_j,lo_i] and not G.water[b_[1],b_[0]]
                zt=G.level[hi_j,hi_i]*TIER; rot=math.degrees(math.atan2(oy,ox))+90
                for t in (-1.2,-0.6,0.0,0.6,1.2):
                    if (t<-0.2 and not straight(-1)) or (t>0.2 and not straight(1)): continue
                    if rng.random()<0.3: continue
                    tt=t+rng.uniform(-0.12,0.12); x,y,z=lip_pos(disp,cx+tx*tt,cy+ty*tt,zt)
                    T.P("SM_VK_LipGrass" if bpy.data.objects.get("SM_VK_LipGrass") else "SM_VKT_LipGrass",x,y,rot+rng.uniform(-6,6),z=z,scale=rng.uniform(0.9,1.25))
    # boulders sunk into the cliff faces, rubble and plants at the toes
    tk_cliff_dress(G,lambda n,x,y,z,r,s: T.P(n,x,y,r,z=z,scale=s),D=disp,seed=seed+3,
                   free=lambda i,j: not T.occ[j,i] and not roads[j,i])

# ---------------------------------------------------------------- post passes
def town_door_clear(T,depth=2.3,half=0.65):
    """keep a 1.3 m wide x ~2 m deep corridor clear in front of every *_Door module (porch width when the door has a
    porch): slide props, bushes and rocks sideways to a spot that clashes with nothing, else drop them"""
    objs=list(T.coll.all_objects)
    doors=[o for o in objs if o.type=="MESH" and is_door(o)]
    porches=[o for o in objs if o.type=="MESH" and "Porch" in o.name]
    dhalf={}
    for d in doors:
        dhalf[d.name]=half
        for p in porches:
            if abs(p.location.x-d.location.x)<1.0 and abs(p.location.y-d.location.y)<1.8 and abs(p.location.z-d.location.z)<0.5: dhalf[d.name]=1.6; break
    # weed strips laid along a door module grow on its step: remove them
    dkeys={(round(d.location.x,1),round(d.location.y,1),round(d.location.z,1)) for d in doors}
    weeds=[o for o in objs if "Deco_Weeds" in o.name and (round(o.location.x,1),round(o.location.y,1),round(o.location.z,1)) in dkeys]
    wn={o.name for o in weeds}; objs=[o for o in objs if o.name not in wn]
    for o in weeds: bpy.data.objects.remove(o)
    T.log.append(("door weeds removed",len(weeds)))
    movable=[o for o in objs if o.type=="MESH" and (PROP_RE.match(base_name(o)) or base_name(o).startswith(("SM_VK_Bush_","SM_VK_Plant_","SM_VK_Rock_","SM_VK_Mushrooms_")))
             and not any(w in o.name for w in WALL_MOUNTED+FLOATING+DOOR_PARTS+SPANNING+("LampPost",))]
    G=T.G; moved=[]; dropped=[]
    for d in doors:
        i,j=door_front_cell(T,d)
        if 0<=i<G.W and 0<=j<G.H and G.ground[j,i]==0 and not G.water[j,i]: G.wear[j,i]=max(G.wear[j,i],90)
    for o in movable:
        for it in range(3):
            hit=None
            cx,cy=o.location.x,o.location.y; z0,z1=T.obj_zrange(o)
            for d in doors:
                if abs(d.location.x-cx)>4.5 or abs(d.location.y-cy)>4.5: continue
                if z1<d.location.z+0.1 or z0>d.location.z+1.9: continue
                r=d.rotation_euler.z; c,s=math.cos(r),math.sin(r)
                P=[((x+TOWN_ORIGIN[0]-d.location.x)*c+(y+TOWN_ORIGIN[1]-d.location.y)*s,-(x+TOWN_ORIGIN[0]-d.location.x)*s+(y+TOWN_ORIGIN[1]-d.location.y)*c) for (x,y) in T.obj_corners(o)]
                u0=min(p[0] for p in P); u1=max(p[0] for p in P); v0=min(p[1] for p in P); v1=max(p[1] for p in P)
                hw=dhalf[d.name]
                if u1>-hw and u0<hw and v0<-0.2 and v1>-depth:
                    cand=[hw-u0+e for e in (0.25,1.0,1.8)]+[-(u1+hw+e) for e in (0.25,1.0,1.8)]
                    hit=[(c*sh,s*sh) for sh in sorted(cand,key=abs)]; break
            if hit is None: break
            x0,y0=o.location.x,o.location.y; ok_=False
            for (dx,dy) in hit:
                o.location.x=x0+dx; o.location.y=y0+dy
                if not [h for h in T.clashes([o],"door_clear",shrink=0.05) if "Weeds" not in h[1] and "LipGrass" not in h[1]]: ok_=True; break
            if not ok_:
                dropped.append(o.name); bpy.data.objects.remove(o); break
            moved.append(o.name)
    T.log.append(("door_clear moved",len(moved),moved[:12])); T.log.append(("door_clear dropped",len(dropped),dropped[:12]))
    return moved

def town_fix_levels(T,disp=None,margin=0.3):
    """props standing on a terrace level must not straddle a cliff, a ramp or water: nudge them (<= 2 m) or drop them"""
    G=T.G; moved=[]; dropped=[]
    skip=[b for b in T.boxes if b[0] in ("quarry","mine")]
    props=[o for o in T.coll.all_objects if o.type=="MESH" and PROP_RE.match(base_name(o)) and not any(w in o.name for w in WALL_MOUNTED+FLOATING+SPANNING)
           and not any(b[1]<=o.location.x-TOWN_ORIGIN[0]<=b[2] and b[3]<=o.location.y-TOWN_ORIGIN[1]<=b[4] for b in skip)]
    WET=("Lavoir","Wash","Pier","Quay","Jetty","Sluice","Wheel","Mooring","Buoy")
    def ok(o,dx,dy,k):
        wet_ok=any(w in o.name for w in WET)
        x0,x1,y0,y1=T.obj_bbox(o); x0+=dx-margin; x1+=dx+margin; y0+=dy-margin; y1+=dy+margin
        nx=max(2,int((x1-x0)/0.8)+1); ny=max(2,int((y1-y0)/0.8)+1)
        pts=np.array([[x0+(x1-x0)*a/(nx-1),y0+(y1-y0)*b/(ny-1),k*TIER] for a in range(nx) for b in range(ny)],float)
        if disp is not None: pts[:,:2]-=disp(pts)[:,:2]
        for (x,y,_) in pts:
            i,j=int(x//3),int(y//3)
            if not (0<=i<G.W and 0<=j<G.H): continue       # the map edge is not a cliff
            if G.level[j,i]!=k or G.ramp[j,i]: return False
            if G.water[j,i] and not wet_ok: return False
        return True
    ring=[(r*math.cos(a*math.pi/4),r*math.sin(a*math.pi/4)) for r in (0.4,0.8,1.2,1.6,2.0) for a in range(8)]
    for o in props:
        z=o.location.z; k=int(round(z/TIER))
        if k<0 or abs(z-k*TIER)>0.25: continue
        if ok(o,0,0,k): continue
        for (dx,dy) in ring:
            if ok(o,dx,dy,k):
                o.location.x+=dx; o.location.y+=dy; moved.append(o.name); break
        else:
            dropped.append(o.name); bpy.data.objects.remove(o)
    T.log.append(("fix_levels moved",len(moved),moved[:12])); T.log.append(("fix_levels dropped",len(dropped),dropped[:20]))
    return moved,dropped

def town_wear(T):
    """trampled ground around the busy places: camp, plaza stalls, the market cross, well-used yards"""
    G=T.G
    for (label,x0,x1,y0,y1) in T.boxes:
        if label in ("camp","sawpit","stockpile","training","site0","site1","site2","charcoal","quarry","mine"):
            for (i,j) in T.cells_of_bbox(x0,x1,y0,y1,shrink=0.8):
                if 0<=i<G.W and 0<=j<G.H and G.ground[j,i]==0: G.wear[j,i]=max(G.wear[j,i],100)

def town_lift_on_paving(T,lift=0.06):
    """props standing on cobbled cells go up onto the paving"""
    G=T.G
    for o in T.coll.all_objects:
        if o.type!="MESH": continue
        x,y=o.location.x-TOWN_ORIGIN[0],o.location.y-TOWN_ORIGIN[1]; i,j=int(x//3),int(y//3)
        if not (0<=i<G.W and 0<=j<G.H) or G.ground[j,i]!=2: continue
        if abs(o.location.z-G.level[j,i]*TIER)<0.03: o.location.z+=lift

def build_valley_town(seed=11,districts=("walls","river","south","meadow","west","inside"),scatter=True):
    G=town_grid(seed)
    errs=demo_validate(G)
    if errs: print("town_grid validate:",errs[:10])
    tcoll=tk_terrain_coll(TOWN_TERR); vcoll=tk_terrain_coll(TOWN_COLL)
    for c in (tcoll,vcoll):
        for o in list(c.all_objects): bpy.data.objects.remove(o)
    T=TownPlacer(G,vcoll)
    fns=dict(walls=town_walls,river=town_river,south=town_south,meadow=town_meadow,west=town_west,inside=town_inside)
    for d in districts: fns[d](T)
    if "inside" in districts:
        T.infilled=town_infill(T); town_plaza_lamps(T)
    disp=make_displace(G)
    if scatter: town_scatter(T,disp=disp.D)
    town_door_clear(T); town_fix_levels(T,disp=disp.D); town_wear(T)
    _CACHE.clear()
    tk_ground_ctl(G,"T_VK_GroundCtl_Town",paved=True)
    terrain_material("M_VK_TerrainTown",W=G.W,H=G.H,ctl="T_VK_GroundCtl_Town")
    objs=tk_build_chunks(G,prefix="VKV",origin=TOWN_ORIGIN,coll=tcoll,displace=disp)
    for o in objs:
        if "Chunk" in o.name: o.data.materials[0]=bpy.data.materials["M_VK_TerrainTown"]
    tk_ramp_shoulders(G,vcoll,origin=TOWN_ORIGIN); tk_ramp_dress(G,vcoll,origin=TOWN_ORIGIN)
    tk_build_paving(G,tcoll,origin=TOWN_ORIGIN,name="VKV_Paving"); town_lift_on_paving(T)
    return G,T,objs
