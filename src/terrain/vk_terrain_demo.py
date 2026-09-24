# ===================== TERRAIN DEMO MAP + VILLAGE ON TERRAIN =====================
# exec after vk_helpers and vk_terrain in the same namespace
import bpy, math, random
import numpy as np
from mathutils import Vector

DEMO_W,DEMO_H=32,24

def demo_grid(seed=5):
    rng=np.random.default_rng(seed); W,H=DEMO_W,DEMO_H
    G=TGrid(W,H)
    jj,ii=np.mgrid[0:H,0:W]
    lvl=np.ones((H,W),np.int32)
    # --- river along the south (level 0 water, 2 cells wide, meandering)
    jc=np.array([2+int(round(0.7*math.sin(i/4.2+0.6))) for i in range(W)])
    for i in range(W):
        lvl[:jc[i]+2,i]=0
        G.water[max(0,jc[i]-1):jc[i]+1,i]=True
    G.ground[(lvl==0)&(~G.water)]=3
    # --- village plateau at level 2 (rows 9..18), irregular outline around a guaranteed core
    f=np.zeros((H,W))
    for _ in range(5):
        cx,cy,r=rng.uniform(10,24),rng.uniform(12,16),rng.uniform(3,6)
        f+=np.exp(-((ii-cx)**2+(jj-cy)**2)/r**2)
    lvl[(f>0.9)&(jj>=9)&(jj<=18)&(ii>=7)&(ii<=28)]=2
    lvl[9:19,8:27]=2
    # --- chapel hill (level 3) with a level-4 crown, west of the plateau
    hill=((ii-4.5)**2/9+(jj-16.5)**2/12<1.0)
    lvl[hill]=np.maximum(lvl[hill],3); lvl[13:20,2:8]=np.maximum(lvl[13:20,2:8],3)
    lvl[15:19,3:7]=4
    # --- forest ridge in the north (levels 3-5)
    for j in range(19,H):
        for i in range(W):
            n=3+int(np.clip(round(1.2*math.sin(i/3.7)+0.9*math.cos(i/2.3+j/2.0)+(j-19)*0.45),0,2))
            lvl[j,i]=max(lvl[j,i],n)
    G.level[:]=lvl
    G.ground[(G.level>=5)]=4
    # --- main road: south bank -> river (bridge later) -> meadow -> 2-wide earth ramp -> cobble plaza
    road=np.zeros((H,W),bool); road[0:12,16:18]=True
    G.ground[road&~G.water]=1
    G.ramp[8,16]=1; G.ramp[8,17]=1                  # level 1 (j=8) -> level 2 (j=9)
    G.ground[12:16,13:21]=2                          # 8x4 cobble plaza
    # --- plateau (2) -> chapel hill (3) and hill (3) -> crown (4)
    G.ramp[15,8]=4; G.stair[15,8]=True; G.ground[15,7:10]=2
    G.ramp[14,4]=1; G.ramp[14,5]=1; G.stair[14,4:6]=True; G.ground[14:16,4:6]=2
    # --- farm plots on the meadow
    G.ground[5:8,2:8]=1; G.ground[6:8,20:25]=1
    G.stiff[12:16,13:21]=True
    for (j,i) in zip(*np.nonzero(G.ramp)):
        G.stiff[j,i]=True; di,dj=((0,1),(1,0),(0,-1),(-1,0))[G.ramp[j,i]-1]; G.stiff[j+dj,i+di]=True
    return G

def demo_validate(G):
    errs=G.validate()
    for j in range(G.H):
        for i in range(G.W):
            d=G.ramp[j,i]
            if not d: continue
            di,dj=((0,1),(1,0),(0,-1),(-1,0))[d-1]
            L=G.level[j,i]
            if G.level[j+dj,i+di]!=L+1: errs.append(("ramp_high",i,j))
            if G.level[j-dj,i-di]!=L: errs.append(("ramp_low",i,j))
            for s in (-1,1):
                si,sj=i+s*dj,j+s*di        # side neighbours
                if not (0<=si<G.W and 0<=sj<G.H): continue
                ok=(G.level[sj,si]==L and G.level[sj+dj,si+di]==L+1) or (G.ramp[sj,si]==d)
                if not ok: errs.append(("ramp_side",i,j,si,sj))
    return errs

# ---------------------------------------------------------------- placing kit buildings on the grid
def cell_z(G,i,j): return float(G.level[j,i])*TIER
def fp_origin(a,b,n,d=2,rot=0):
    """snap: n x d building whose footprint min cell is (a,b); returns map-local (ox,oy,orz)"""
    if rot in (0,180): return (3*a+1.5*n,3*b+1.5*d,math.radians(rot))
    return (3*a+1.5*d,3*b+1.5*n,math.radians(rot))
def lifted(coll,oz,fn):
    before=set(coll.objects)
    fn()
    for o in coll.objects:
        if o not in before: o.location.z+=oz
def W(ox,oy,orz=0.0): return (MAP_ORIGIN[0]+ox,MAP_ORIGIN[1]+oy,orz)
def mark(G,a,b,n,d,rot):
    if rot in (90,270): n,d=d,n
    G.stiff[b:b+d,a:a+n]=True

def demo_village(G,coll,seed=2031):
    r=random.Random(seed)
    L2=cell_z(G,16,13)
    def house(a,b,n,rot,stories,style):
        ox,oy,orz=fp_origin(a,b,n,2,rot); mark(G,a,b,n,2,rot)
        lifted(coll,cell_z(G,a,b),lambda: build_house_v(coll,W(ox,oy,orz),n,stories,style))
    def rs(k,**over):
        st=random_style(seed*7+k); st.update(over); return st
    house(12,16,3,0,2,rs(1,ground="Stone",roof="Red"))          # north of the plaza, fronts face it
    house(15,16,2,0,2,rs(2,ground="Plaster",roof="Blue"))
    house(18,16,3,0,2,rs(3,ground="Stone",roof="Thatch"))
    house(9,10,3,180,2,rs(4,ground="Plaster",roof="Green"))     # south of the plaza
    house(19,10,3,180,1,rs(5,ground="Stone",roof="Red"))
    house(10,12,2,270,2,rs(6,ground="Stone",roof="Red"))        # west / east of the plaza
    house(22,12,2,90,2,rs(7,ground="Plaster",roof="Thatch"))
    ox,oy,orz=fp_origin(23,15,2,2,0); mark(G,23,15,2,2,0)
    lifted(coll,cell_z(G,23,15),lambda: build_blacksmith(coll,W(ox,oy,orz)))
    ox,oy,orz=fp_origin(5,16,3,2,90); mark(G,5,16,3,2,90)
    lifted(coll,cell_z(G,5,16),lambda: build_chapel(coll,W(ox,oy,orz),n=3,roof="Blue",tower=False))
    px,py=3*17,3*14
    def P(nm,x,y,rot=0,z=None,st={}):
        o=place_v(coll,nm,x,y,0,rot,W(0,0,0),st); o.location.z+=L2 if z is None else z; return o
    P("SM_VK_Prop_Well",px,py)
    for k,(x,y,rt) in enumerate(((px-7.0,py-2.8,0),(px-3.6,py-2.8,0),(px+4.2,py-2.8,0),(px+7.4,py+1.2,90))):
        P(r.choice(["SM_VK_MarketStall","SM_VK_MarketStall_Greengrocer","SM_VK_MarketStall_Cheese","SM_VK_MarketStall_Tinker"]),
          x,y,rt,st={"cloth":r.choice(["Red","Blue","Green","Yellow"])})
    for (x,y) in ((px-10.5,py+4.5),(px+10.5,py+4.5),(px-10.5,py-4.5),(px+10.5,py-4.5)): P("SM_VK_Prop_LampPost",x,y)
    # built edge: ashlar retaining walls along the plateau front on both sides of the ramp
    if bpy.data.objects.get("SM_VK_RetainingWall") is None: tk_build_edge_pieces()
    for i in list(range(12,16))+list(range(18,22)):
        G.stiff[8,i]=True; G.stiff[9,i]=True
        P("SM_VK_RetainingWall",3*i+1.5,27.0,z=cell_z(G,i,8))
    for x in (36.0,48.0,54.0,66.0): P("SM_VK_RetainingWall_End",x,27.0,z=cell_z(G,12,8))
    build_windmill_at=W(3*27,3*7,0)
    lifted(coll,cell_z(G,26,6),lambda: build_windmill(coll,build_windmill_at))
    ox,oy,orz=fp_origin(10,5,3,2,0); mark(G,10,5,3,2,0)
    lifted(coll,cell_z(G,10,5),lambda: build_barn(coll,W(ox,oy,orz),n=3,roof="Thatch"))
    crops=["SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Lavender","SM_VK_Crop_Wheat"]
    for j in range(5,8):
        for i in range(2,8):
            P(crops[(i//3+j)%len(crops)],3*i+1.5,3*j+1.5,z=cell_z(G,i,j))
    for i in range(20,25):
        for j in (6,7): P(crops[(i+j)%len(crops)],3*i+1.5,3*j+1.5,z=cell_z(G,i,j))
    return G

def demo_scatter(G,coll,seed=77):
    """trees on the ridge and meadow edges, seam rocks and grass at cliff toes"""
    rng=random.Random(seed)
    def P(nm,x,y,z,rot=None,s=1.0):
        o=place_v(coll,nm,x,y,0,rng.uniform(0,360) if rot is None else rot,W(0,0,0),{}); o.location.z+=z; o.scale=(s,s,s); return o
    trees_n=["SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Birch"]
    def safe(i,j,inset=0.9):
        """random point inside cell (i,j) away from borders with a level change / water"""
        l=G.level[j,i]; x0,x1,y0,y1=3*i+0.3,3*i+2.7,3*j+0.3,3*j+2.7
        for (di,dj,side) in ((-1,0,"x0"),(1,0,"x1"),(0,-1,"y0"),(0,1,"y1")):
            ii,jj=G.cell(i+di,j+dj)
            if G.level[jj,ii]!=l or G.water[jj,ii]:
                if side=="x0": x0=3*i+inset
                if side=="x1": x1=3*i+3-inset
                if side=="y0": y0=3*j+inset
                if side=="y1": y1=3*j+3-inset
        if x0>=x1 or y0>=y1: return None
        return rng.uniform(x0,x1),rng.uniform(y0,y1)
    for j in range(G.H):
        for i in range(G.W):
            if G.water[j,i] or G.stiff[j,i] or G.ground[j,i] in (1,2) or G.ramp[j,i]: continue
            z=cell_z(G,i,j)
            if j>=19:
                for _ in range(2 if rng.random()<0.6 else 1):
                    p=safe(i,j,1.1)
                    if p and rng.random()<0.85:
                        nm=rng.choice(trees_n[:3] if G.level[j,i]>=4 else trees_n)
                        P(nm,p[0],p[1],z,s=rng.uniform(0.8,1.15))
                if rng.random()<0.5:
                    p=safe(i,j,0.6)
                    if p: P(rng.choice(["SM_VK_Plant_Fern","SM_VK_Bush_Round","SM_VK_Rock_Small_A","SM_VK_Mushrooms_Brown"]),p[0],p[1],z)
            elif G.level[j,i]==1 and rng.random()<0.08:
                p=safe(i,j,1.2)
                if p: P(rng.choice(["SM_VK_Tree_Oak_A","SM_VK_Tree_Apple","SM_VK_Tree_Blossom","SM_VK_Bush_Large"]),p[0],p[1],z,s=rng.uniform(0.85,1.1))
            elif G.level[j,i]==0 and G.ground[j,i]==3 and rng.random()<0.35:
                p=safe(i,j,0.5)
                if p: P(rng.choice(["SM_VK_Plant_Reeds","SM_VK_Rock_Pebbles","SM_VK_Plant_Reeds"]),p[0],p[1],z)
            elif G.level[j,i] in (2,3,4) and rng.random()<0.12:
                p=safe(i,j,0.8)
                if p: P(rng.choice(["SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers","SM_VK_Bush_Hydrangea","SM_VK_Rock_Small_B"]),p[0],p[1],z)
    # hanging lip grass + seam rocks along straight stretches of level-change borders
    Dfn=getattr(demo_scatter,"D",None)
    def disp(x,y,z):
        if Dfn is None: return x,y
        d=Dfn(np.array([[x,y,z]],float))[0]; return x+d[0],y+d[1]
    for j in range(G.H):
        for i in range(G.W):
            for (di,dj) in ((1,0),(0,1)):
                ii,jj=i+di,j+dj
                if ii>=G.W or jj>=G.H: continue
                la,lb=G.level[j,i],G.level[jj,ii]
                if la==lb or G.water[j,i] or G.water[jj,ii] or G.ramp[j,i] or G.ramp[jj,ii]: continue
                hi_i,hi_j,lo_i,lo_j=(i,j,ii,jj) if la>lb else (ii,jj,i,j)
                # border line: along x for a vertical-neighbour pair, along y for a horizontal pair
                ox,oy=(lo_i-hi_i),(lo_j-hi_j)                     # outward direction (toward the low cell)
                tx,ty=abs(oy),abs(ox)                             # along the border
                cx=1.5*(hi_i+lo_i)+1.5; cy=1.5*(hi_j+lo_j)+1.5    # border midpoint
                def straight(sgn):
                    a_=G.cell(hi_i+sgn*tx,hi_j+sgn*ty); b_=G.cell(lo_i+sgn*tx,lo_j+sgn*ty)
                    return G.level[a_[1],a_[0]]==G.level[hi_j,hi_i] and G.level[b_[1],b_[0]]==G.level[lo_j,lo_i] and not G.water[b_[1],b_[0]]
                zt=cell_z(G,hi_i,hi_j)
                rot=math.degrees(math.atan2(oy,ox))-(-90)        # piece faces -Y
                for t in (-1.2,-0.6,0.0,0.6,1.2):
                    if (t<-0.2 and not straight(-1)) or (t>0.2 and not straight(1)): continue
                    if rng.random()<0.25: continue
                    tt=t+rng.uniform(-0.12,0.12)
                    x,y,z=lip_pos(Dfn,cx+tx*tt,cy+ty*tt,zt)
                    P("SM_VKT_LipGrass",x,y,z,rot=rot+rng.uniform(-6,6),s=rng.uniform(0.9,1.25))
    # boulders sunk into the cliff faces, rubble and plants at the toes
    tk_cliff_dress(G,lambda n,x,y,z,r,s: P(n,x,y,z,rot=r,s=s),D=Dfn,seed=seed+3,
                   free=lambda i,j: not G.stiff[j,i] and G.ground[j,i] not in (1,2))
    return
    # (legacy) edge-owned seam rocks at cliff toes (one candidate per level-change border)
    for j in range(G.H):
        for i in range(G.W):
            for (di,dj) in ((1,0),(0,1)):
                ii,jj=i+di,j+dj
                if ii>=G.W or jj>=G.H: continue
                la,lb=G.level[j,i],G.level[jj,ii]
                if la==lb or G.water[j,i] or G.water[jj,ii] or G.ramp[j,i] or G.ramp[jj,ii]: continue
                if hash32(i*2+di,j*2+dj,int(min(la,lb)),9)%100>=35: continue
                lo_i,lo_j,hi_i,hi_j=(i,j,ii,jj) if la<lb else (ii,jj,i,j)
                # border midpoint, pushed 0.55 m into the low cell
                bx=1.5*(lo_i+hi_i)+1.5+0.55*(lo_i-hi_i); by=1.5*(lo_j+hi_j)+1.5+0.55*(lo_j-hi_j)
                tx=rng.uniform(-1.0,1.0)
                bx+=tx*abs(dj); by+=tx*abs(di)
                P(rng.choice(["SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Pebbles","SM_VK_Plant_Fern"]),bx,by,cell_z(G,lo_i,lo_j)-0.05,s=rng.uniform(0.8,1.3))

def demo_ground_snap(G,coll):
    """props and fences standing on the ground follow the cell level under them"""
    for o in coll.objects:
        n=o.data.name if o.data else ""
        src=o.name.split("_inst")[0]
        if not any(k in src for k in ("Fence","Prop_","Crop_","Deco_Weeds")): continue
        lx=o.location.x-MAP_ORIGIN[0]; ly=o.location.y-MAP_ORIGIN[1]
        i=int(lx//3); j=int(ly//3)
        if not (0<=i<G.W and 0<=j<G.H): continue
        z=o.location.z; zc=cell_z(G,i,j)
        if abs(z/TIER-round(z/TIER))<0.02 and abs(z-zc)>0.01 and not G.water[j,i]: o.location.z=zc

def build_terrain_demo(seed=5,village=True,scatter=True):
    G=demo_grid(seed)
    errs=demo_validate(G)
    tcoll=tk_terrain_coll("VK_Terrain"); vcoll=tk_terrain_coll("VK_TerrainVillage")
    for c in (tcoll,vcoll):
        for o in list(c.objects): bpy.data.objects.remove(o)
    if village: demo_village(G,vcoll); demo_ground_snap(G,vcoll)
    disp=make_displace(G)
    if bpy.data.objects.get("SM_VKT_LipGrass") is None: tk_build_lipgrass()
    demo_scatter.D=disp.D
    if scatter: demo_scatter(G,vcoll)
    _CACHE.clear()
    tk_ground_ctl(G,paved=True); terrain_material(W=G.W,H=G.H)
    objs=tk_build_chunks(G,prefix="VKT",coll=tcoll,displace=disp)
    tk_ramp_shoulders(G,vcoll); tk_ramp_dress(G,vcoll)
    tk_build_paving(G,tcoll,name="VKT_Paving")
    return G,errs,objs
