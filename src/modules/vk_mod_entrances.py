# ===================== WORKSHOP: ENTRANCES (prefix ent_) =====================
# The valley's ways underground (docs/WORLD_GRAPH.md): the dwarves' gate in the west ridge, the spring cave at the
# river's head, a sewer grate in the main street and the lock-up on the market place. With the mine portal
# (vk_mod_industry) they are the valley's five scene links:
#   ENT_TOWN_LINKS  (link id, kind, target scene, piece) for each, the valley being level ENT_TOWN_SCENE
#   ENT_META        each piece's link data (trigger box, spawn, prompt), written on the masters by ent_stamp_meta()
#   ent_link(o,...) tags a placed instance (the interior kit's link props) and puts its SPN_<id> spawn
# vk_town_map places them (town_entrances, town_spring) and tags them (town_links).
# Executed after vk_helpers and vk_mod_industry in the same namespace (it uses the ind_ rock helpers).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

ENT_NG=dict(wobble=False,grime=True)
ENT_TOWN_SCENE="VK_ValleyTown"      # the valley's level id in the world graph (its collection in the VillageKit scene)
# A link into a scene lands at that scene's link whose target is the scene left (on its SPN_<id> spawn).
ENT_TOWN_LINKS=[("mine_adit","passage","VKI_Mine_M1","SM_VK_Mine_Portal"),
                ("dwarf_gate","passage","VKI_Dwarf_Hall","SM_VK_Entrance_DwarfGate"),
                ("spring_cave","passage","VKI_Cave_Falls","SM_VK_Entrance_SpringCave"),
                ("sewer_grate","passage","VKI_Sewer_S1","SM_VK_Entrance_SewerGrate"),
                ("gaol_lockup","stair_down","VKI_Dungeon_B1","SM_VK_Entrance_LockUp")]
# Per piece, in piece-local metres: the trigger box [cx, cy, cz, sx, sy, sz], the spawn [x, y, z] and its facing (a
# bearing: 0 = local +Y, 180 = local -Y, clockwise), the prompt, and how squarely the walker must face the link (deg;
# 180 = any way, for the grate one stands on).
ENT_META={
 "SM_VK_Mine_Portal":dict(trigger=[0.0,1.75,1.3,2.0,1.3,2.6],spawn=[0.0,0.05,0.03],facing=180,
                          prompt="Go into the mine",facing_min=60),
 "SM_VK_Entrance_DwarfGate":dict(trigger=[0.0,1.2,1.45,2.4,0.9,2.0],spawn=[0.0,-1.05,0.45],facing=180,
                                 prompt="Enter the dwarven halls",facing_min=60),
 "SM_VK_Entrance_SpringCave":dict(trigger=[0.0,1.25,1.0,1.8,0.8,2.0],spawn=[0.0,-1.4,0.0],facing=180,
                                  prompt="Go into the cave",facing_min=60),
 "SM_VK_Entrance_CaveMouth":dict(trigger=[0.0,1.25,1.0,1.8,0.8,2.0],spawn=[0.0,-1.4,0.0],facing=180,
                                 prompt="Go into the cave",facing_min=60),
 "SM_VK_Entrance_SewerGrate":dict(trigger=[0.0,0.0,1.0,1.1,1.1,2.0],spawn=[0.0,-1.25,0.0],facing=180,
                                  prompt="Climb down",facing_min=180),
 "SM_VK_Entrance_LockUp":dict(trigger=[0.0,-1.95,1.0,0.9,0.7,2.0],spawn=[0.0,-2.75,0.0],facing=180,
                              prompt="Go down to the gaol",facing_min=60),
}

# ---------------------------------------------------------------- helpers
def ent_prism(k,pts,y0,y1,mi,tile=None):
    """a convex polygon pts [(x, z)] in the XZ plane, extruded from y0 to y1 (corbels, steps, lozenges)"""
    F=[k.bm.verts.new((x,y0,z)) for x,z in pts]; B=[k.bm.verts.new((x,y1,z)) for x,z in pts]
    fs=[k.bm.faces.new(F),k.bm.faces.new(B[::-1])]
    n=len(pts)
    for i in range(n):
        j=(i+1)%n; fs.append(k.bm.faces.new((F[j],F[i],B[i],B[j])))
    k.bm.normal_update()
    c=Vector((sum(p[0] for p in pts)/n,(y0+y1)/2,sum(p[1] for p in pts)/n))
    for f in fs:
        if f.normal.dot(f.calc_center_median()-c)<0: f.normal_flip()
    k.bm.normal_update(); k.project(fs,mi,tile=tile)
    return fs
def ent_void(k,pts):
    """a darkness card (VOID); the point order sets the face it shows (counter-clockwise seen from the viewer)"""
    return k.quad(pts,VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
def ent_keep(vs,boxes,it=4):
    """push verts out of a union of boxes [(lo, hi)] (ind_keepout box by box, repeated: nested boxes settle)"""
    for _ in range(it):
        for lo,hi in boxes: ind_keepout(vs,lo,hi)
def ent_cut(k,vs,boxes,it=2):
    """carve openings out of a rock shell (ind_carve box by box: verts pushed to the box's sides, top or back, faces
    left spanning its inside deleted); boxes [(lo, hi)] open toward -y, the widest first when they nest"""
    for _ in range(it):
        for lo,hi in boxes: ind_carve(k,vs,lo,hi)
def ent_roughen(vs,boxes,amt,seed):
    """verts left on a carved box's side, top or back face move outward by up to amt (never into the opening), so a
    carved mouth has ragged edges instead of ruled ones"""
    rnd=random.Random(seed); e=1e-4
    for v in vs:
        if not v.is_valid: continue
        p=v.co
        for lo,hi in boxes:
            if not (lo[0]-e<=p.x<=hi[0]+e and lo[1]-e<=p.y<=hi[1]+e and lo[2]-e<=p.z<=hi[2]+e): continue
            if abs(p.x-lo[0])<e: p.x-=rnd.uniform(0,amt)
            elif abs(p.x-hi[0])<e: p.x+=rnd.uniform(0,amt)
            elif abs(p.z-hi[2])<e: p.z+=rnd.uniform(0,amt)
            elif abs(p.y-hi[1])<e: p.y+=rnd.uniform(0,amt)
def ent_rocks(k,specs,boxes,rough=0.0):
    """boulders [(base centre, size, seed, rot, material, subdivisions)] carved out of boxes (ent_cut), their carved
    faces roughened by up to rough"""
    for (c,sz,sd,rz,mi,sb) in specs:
        vs=ind_boulder(k,c,sz,sd,mi=mi,rot=rz,sub=sb,cuts=8)
        ent_cut(k,vs,boxes)
        if rough: ent_roughen(vs,boxes,rough,sd)
def ent_tufts(k,pts,seed,boxes=()):
    """grass tufts dropped onto the piece's own surfaces at [(x, y)], skipping points inside boxes"""
    bvh=ind_bvh(k); rnd=random.Random(seed)
    for i,(x,y) in enumerate(pts):
        z=ind_drop(bvh,x,y)
        if any(lo[0]<x<hi[0] and lo[1]<y<hi[1] and z<hi[2] for lo,hi in boxes): continue
        ind_tuft(k,(x,y,z-0.05),rnd.uniform(0.4,0.7),seed=seed+i,cell="grass" if i%5 else "daisy")
def ent_oct(k,prof,mi,c=(0.0,0.0),cap_top=False):
    """an octagonal lathe with a face toward -Y: prof [(apothem, z)] from the bottom up"""
    rings=[]
    for (a,z) in prof:
        R=a/math.cos(math.pi/8)
        rings.append([k.bm.verts.new((c[0]+R*math.cos(math.pi/8+i*math.pi/4),c[1]+R*math.sin(math.pi/8+i*math.pi/4),z)) for i in range(8)])
    fs=[]
    for r0,r1 in zip(rings[:-1],rings[1:]):
        for i in range(8):
            j=(i+1)%8; fs.append(k.bm.faces.new((r0[i],r0[j],r1[j],r1[i])))
    if cap_top: fs.append(k.bm.faces.new(rings[-1]))
    k.bm.normal_update(); k.project(fs,mi)
    return fs

# ---------------------------------------------------------------- the dwarves' gate
def ent_dg_leaf(k,d,ang,hx,hy,z0):
    """one stone leaf of the dwarves' gate, hinged at (hx, hy) on the gate floor z0 and swung ang degrees into the
    passage; d=+1 the left leaf (it closes toward +x), -1 the right. Built hinge-local: the leaf runs along d*x, its
    face (raised panel, lozenge, a stone boss, bronze hinge bands) toward -y, its top corner cut to the jamb's corbel.
    (Bronze is metallic: a bronze disc facing the camera mirrored the dark ground and read as a hole.)"""
    sub=Kit(); W,H,c,T=1.29,3.48,0.45,0.16
    X=lambda u: d*u
    ent_prism(sub,[(X(0.0),0.02),(X(W),0.02),(X(W),H),(X(c),H),(X(0.0),H-c)],-T/2,T/2,STONE_BLOCK)
    sub.box((X(0.745),-T/2-0.015,1.62),(0.85,0.03,2.5),DRESS,bevel=0.01)              # panel u 0.32-1.17, z 0.37-2.87
    ent_prism(sub,[(X(0.745),0.72),(X(1.07),1.62),(X(0.745),2.52),(X(0.42),1.62)],-T/2-0.05,-T/2-0.02,STONE_BLOCK)
    _cyl(sub,(X(0.745),-T/2-0.06,1.62),0.13,0.11,0.03,10,DRESS,rot=Matrix.Rotation(math.pi/2,4,"X"))  # a boss
    for z in (0.45,1.75,3.0): sub.box((X(0.14),-T/2-0.006,z),(0.28,0.012,0.08),BRONZE,bevel=0.0)
    merge_kit(k,sub,Matrix.Translation((hx,hy,z0))@Matrix.Rotation(math.radians(d*ang),4,"Z"))

def ent_dwarf_gate(k):
    """the dwarves' gate (VKI_Dwarf_Hall's way out): a corbelled doorway cut into a crag -- dark dressed jambs, a
    massive lintel with a bronze band and a line of bronze runes, a stepped crest with a glowing rune stone -- its two
    stone leaves swung in
    on a dark passage, braziers burning on two piers, three steps up to its platform. Origin: the ground at the foot of
    the facade's centre, face -Y; the facade's rock face at y 0.25, the passage runs +Y to 2.2 (keep the facade 2.5 m
    or more in front of a cliff behind it, or the ground above shows in the passage). Gate floor 0.45; clear opening
    2.6 x 3.5 (x +-1.3, z 0.45-3.95)."""
    hw,z0,top,cor,deep=1.3,0.45,3.95,0.45,2.2
    # ---- platform and steps (dressed stone), the passage floor running into darkness
    k.box((0,-0.7,-0.03),(7.0,2.0,0.96),STONE_BLOCK,bevel=0.04)                      # x +-3.5, y -1.7..0.3, top 0.45
    k.box((0,-1.9,-0.1),(4.8,0.4,0.8),STONE_BLOCK,bevel=0.03)                        # step: top 0.30
    k.box((0,-2.3,-0.175),(4.5,0.4,0.65),STONE_BLOCK,bevel=0.03)                     # step: top 0.15
    k.box((0,0.9,z0-0.3),(2*hw+0.64,1.2,0.6),STONE_BLOCK,bevel=0.02)                  # passage floor y 0.3..1.5
    ent_void(k,[(-1.62,1.5,z0+0.002),(1.62,1.5,z0+0.002),(1.62,deep,z0+0.002),(-1.62,deep,z0+0.002)])
    ent_void(k,[(-1.62,deep,z0-0.05),(1.62,deep,z0-0.05),(1.62,deep,top+0.1),(-1.62,deep,top+0.1)])   # back
    ent_void(k,[(-1.62,0.38,top+0.02),(-1.62,deep,top+0.02),(1.62,deep,top+0.02),(1.62,0.38,top+0.02)])  # ceiling
    for s in (-1,1):                                                                  # side walls: dressed, then dark
        x=s*1.62; pd=[(x,0.36,z0),(x,1.0,z0),(x,1.0,top+0.05),(x,0.36,top+0.05)]
        pv=[(x,1.0,z0),(x,deep,z0),(x,deep,top+0.05),(x,1.0,top+0.05)]
        k.quad(pd if s<0 else [pd[1],pd[0],pd[3],pd[2]],DRESS)
        ent_void(k,pv if s<0 else [pv[1],pv[0],pv[3],pv[2]])
    # ---- the carved rock face round the doorway (panels of uneven height, a little out of true)
    for (x,w,zt,ry) in ((-2.56,1.88,5.9,0.03),(2.56,1.88,6.45,-0.04),(0.0,3.3,6.1,0.0)):
        z_=-0.3 if abs(x)>0.1 else 4.2
        k.box((x,0.6,(z_+zt)/2),(w,0.7,zt-z_),ROCK,rot=(0,ry,0),bevel=0.06)
    # ---- jambs on plinths, corbels, lintel, gold, runes, the stepped crest (dark dressed stone)
    for s in (-1,1):
        k.box((s*1.6,-0.035,z0+0.15),(0.7,0.83,0.3),DRESS,bevel=0.04)                # plinth
        k.box((s*1.6,-0.025,(z0+top)/2),(0.6,0.75,top-z0),DRESS,bevel=0.04)           # jamb x 1.3..1.9
        k.box((s*1.6,-0.025,3.3),(0.62,0.77,0.06),BRONZE,bevel=0.0)                  # gold ring
        ent_prism(k,[(s*hw,top-cor),(s*(hw-cor),top),(s*hw,top)],-0.38,0.33,DRESS)   # corbel
    k.box((0,-0.025,4.4),(4.5,0.85,0.9),DRESS,bevel=0.05)                             # lintel z 3.95..4.85, front y -0.45
    k.box((0,-0.455,4.16),(3.7,0.02,0.09),BRONZE,bevel=0.0)                           # gold band
    rnd=random.Random(17)
    for gi in range(8):                                                               # runes: a stem and one or two twigs
        gx=-1.68+0.48*gi
        k.box((gx,-0.455,4.52),(0.045,0.02,0.30),BRONZE,bevel=0.0)
        for b in range(rnd.choice((1,2))):
            s=rnd.choice((-1,1)); zz=4.52+rnd.choice((-0.08,0.0,0.08))
            k.box((gx+s*0.055,-0.455,zz),(0.04,0.02,0.16),BRONZE,rot=(0,s*0.75,0),bevel=0.0)
    for (w,z,y0_) in ((3.6,4.85,-0.35),(2.4,5.2,-0.3),(1.2,5.55,-0.25)):             # stepped crest
        k.box((0,(y0_+0.3)/2,z+0.175),(w,0.3-y0_,0.35),DRESS,bevel=0.04)
    _cyl(k,(0,-0.315,5.375),0.15,0.15,0.03,12,DRESS,rot=Matrix.Rotation(math.pi/2,4,"X"))       # a lit rune stone:
    _cyl(k,(0,-0.335,5.375),0.10,0.10,0.012,10,GLOW,rot=Matrix.Rotation(math.pi/2,4,"X"))       # a boss, its rune glowing
    # ---- the leaves, swung in
    for d in (1,-1): ent_dg_leaf(k,d,70.0,-d*hw,0.43,z0)
    # ---- piers with braziers
    for s in (-1,1):
        x,y=s*2.85,-1.0
        k.box((x,y,z0+0.15),(0.95,0.95,0.3),DRESS,bevel=0.04)
        k.box((x,y,1.95),(0.72,0.72,2.4),DRESS,bevel=0.05)                          # z 0.75..3.15
        k.box((x,y,2.85),(0.75,0.75,0.07),BRONZE,bevel=0.0)
        k.box((x,y,3.225),(0.84,0.84,0.15),DRESS,bevel=0.03)
        k.box((x,y,3.375),(0.96,0.96,0.15),DRESS,bevel=0.03)                        # top 3.45
        ind_lathe(k,[(0.14,0.0),(0.18,0.06),(0.30,0.14),(0.42,0.30),(0.44,0.37)],c=(x,y,3.45),segs=10,mi=BRONZE)
        _cyl(k,(x,y,3.77),0.41,0.41,0.04,10,COAL)
        _cyl(k,(x,y,4.09),0.30,0.02,0.6,6,GLOW)
        for (dx,dy,r,h) in ((0.17,0.08,0.15,0.42),(-0.14,-0.1,0.14,0.36)):
            _cyl(k,(x+dx,y+dy,4.0),r,0.01,h,6,GLOW)
    # ---- the crag: cheeks, the mass over the crest, a mossy hill behind, stones at the foot
    keeps=[((-3.55,-9.0,-1.0),(3.55,0.32,6.3)),                                      # the facade bay
           ((-1.75,-9.0,-1.0),(1.75,deep+0.15,4.15))]                                # the passage
    ent_rocks(k,[((-4.15,0.7,-0.4),(2.0,3.2,5.6),21,0.25,ROCK,2),
                 ((4.15,0.6,-0.4),(1.9,3.0,5.2),22,-0.3,ROCK,2),
                 ((0.0,1.5,5.7),(6.6,3.0,2.2),23,0.05,ROCK_MOSSY,2),
                 ((-2.5,3.0,4.6),(3.6,3.0,3.2),24,0.6,ROCK_MOSSY,1),
                 ((2.6,3.1,4.4),(3.3,2.9,3.0),25,-0.5,ROCK_MOSSY,1),
                 ((0.3,3.7,6.6),(3.0,2.4,1.6),26,0.9,ROCK_MOSSY,1),
                 ((-4.55,-1.1,-0.1),(0.95,0.85,0.75),31,0.4,ROCK,1),
                 ((4.5,-1.25,-0.1),(0.8,0.7,0.6),32,1.1,ROCK,1),
                 ((-3.85,-2.1,-0.1),(0.5,0.45,0.35),33,2.0,ROCK,1)],keeps)
    vs=ind_heap(k,(0.0,3.6,-0.3),4.7,2.9,7.2,ROCK_MOSSY,seed=27,sub=3,rough=0.18,peak=0.9,tile=2.0)
    ent_cut(k,vs,keeps)
    rnd=random.Random(29)
    ent_tufts(k,[(rnd.uniform(-4.4,4.4),rnd.uniform(1.0,5.6)) for _ in range(18)],seed=29,
              boxes=[((-3.6,-9.0,-1.0),(3.6,0.6,6.4))])
    ind_skirt(k,-4.6,4.6,-2.5,6.0)

# ---------------------------------------------------------------- the spring cave
def ent_spring_cave(k,water=True):
    """the spring cave (VKI_Cave_Falls's way out): a dark mouth between mossy boulders under a lintel rock, water
    trickling out of the dark over pebbles, a mossy hill over it. Origin: the floor at the mouth, face -Y; the cave
    runs +Y to 1.9 (keep the mouth 2.2 m or more in front of a cliff behind it). A rough arch ~2.3 wide x 2.45 high.
    water=False: dry (SM_VK_Entrance_CaveMouth: a cave mouth on open ground, no spring), a few loose stones instead."""
    hw,deep=1.15,1.9
    arch=[((-a,-9.0,-1.0),(a,deep+0.1,z)) for a,z in ((hw,1.5),(1.05,1.95),(0.9,2.2),(0.65,2.38),(0.35,2.48))]
    # ---- floor: rock in the mouth, darkness further in; dark walls and roof inside the rock's faces
    f=k.bm.faces.new([k.bm.verts.new((x,y,0.03)) for x,y in ((-hw,0.25),(-0.62,-0.12),(0.05,-0.3),(0.72,-0.08),
                                                              (hw,0.3),(hw,0.75),(-hw,0.75))])
    k.bm.normal_update(); k.project([f],ROCK)
    ent_void(k,[(-hw,0.75,0.032),(hw,0.75,0.032),(hw,deep,0.032),(-hw,deep,0.032)])
    ent_void(k,[(-hw-0.3,deep,-0.05),(hw+0.3,deep,-0.05),(hw+0.3,deep,2.6),(-hw-0.3,deep,2.6)])
    ent_void(k,[(-hw+0.05,1.3,-0.05),(-hw+0.05,deep,-0.05),(-hw+0.05,deep,2.6),(-hw+0.05,1.3,2.6)])   # the ragged
    ent_void(k,[(hw-0.05,deep,-0.05),(hw-0.05,1.3,-0.05),(hw-0.05,1.3,2.6),(hw-0.05,deep,2.6)])      # rock shapes
    ent_void(k,[(-hw,1.0,2.43),(-hw,deep,2.43),(hw,deep,2.43),(hw,1.0,2.43)])                      # the mouth
    # behind the jamb rocks, to the mouth, and under them: dark (in the valley a cliff stood behind; on open ground the
    # gaps between the rocks showed the grass and whatever stood behind)
    xo=hw+0.08
    ent_void(k,[(-xo,0.35,-0.05),(-xo,deep,-0.05),(-xo,deep,2.6),(-xo,0.35,2.6)])
    ent_void(k,[(xo,deep,-0.05),(xo,0.35,-0.05),(xo,0.35,2.6),(xo,deep,2.6)])
    ent_void(k,[(-1.7,0.35,0.025),(1.7,0.35,0.025),(1.7,deep,0.025),(-1.7,deep,0.025)])
    for (c,sz,sd,rz) in (((-0.95,0.1,-0.05),(0.55,0.5,0.38),51,0.4),((1.0,0.35,-0.05),(0.5,0.45,0.3),52,1.2)):
        vs=ind_boulder(k,c,sz,sd,mi=ROCK,rot=rz,sub=1,cuts=5)                        # stones at the mouth's foot
    # ---- the mouth: jamb boulders, the lintel rock, side masses, the hill behind
    ent_rocks(k,[((-2.0,0.35,-0.25),(2.0,2.2,2.9),41,0.35,ROCK_MOSSY,2),
                 ((1.95,0.55,-0.25),(1.9,2.1,2.6),42,-0.5,ROCK_MOSSY,2),
                 ((0.1,0.85,1.55),(4.2,2.6,1.9),43,0.1,ROCK_MOSSY,2),
                 ((-3.1,1.9,-0.3),(2.4,2.8,3.2),44,0.9,ROCK,1),
                 ((3.2,2.1,-0.3),(2.2,2.6,2.8),45,-0.7,ROCK,1),
                 ((0.4,2.9,2.3),(3.6,2.8,2.2),46,1.4,ROCK_MOSSY,1),
                 ((-2.7,-0.9,-0.1),(0.7,0.6,0.5),47,0.6,ROCK,1)],arch,rough=0.13)
    vs=ind_heap(k,(0.0,2.5,-0.2),3.6,2.7,4.3,MOSS,seed=48,sub=3,rough=0.2,peak=0.85,tile=2.0)
    ent_cut(k,vs,arch); ent_roughen(vs,arch,0.13,48)
    if not water:                                                                     # dry: a few stones in the mouth
        rnd=random.Random(49)
        for i in range(7):
            p=(rnd.uniform(-0.8,0.8),rnd.uniform(-0.6,0.6)); r=rnd.uniform(0.05,0.11)
            vs=_ico(k,(p[0],p[1],0.02),r,ROCK,(rnd.uniform(0.9,1.3),rnd.uniform(0.8,1.1),rnd.uniform(0.45,0.7)),
                    sub=1,jit=r*0.15,seed=490+i)
            ind_box_uv(k,ind_faces(vs),1.5,(rnd.random(),rnd.random()))
        rnd=random.Random(50)
        ent_tufts(k,[(rnd.uniform(-3.6,3.6),rnd.uniform(0.6,4.6)) for _ in range(14)],seed=50,
                  boxes=[((-1.4,-9.0,-1.0),(1.4,deep+0.2,2.6))])
        return
    # ---- the trickle: a ribbon of water out of the dark, pebbles along it
    P=[(0.42,1.75),(0.48,0.9),(0.62,0.1),(0.8,-0.5)]                                # ends on the floor in front
    W=[0.12,0.15,0.17,0.15]                                                           # (sand slopes to water past it)
    L=[];Rr=[]
    for i,(p,w) in enumerate(zip(P,W)):
        a=Vector(P[max(i-1,0)]); b=Vector(P[min(i+1,len(P)-1)]); t=(b-a).normalized(); n=Vector((-t.y,t.x))
        L.append(Vector(p)+n*w); Rr.append(Vector(p)-n*w)
    for i in range(len(P)-1):
        z0,z1=0.045-0.004*i,0.045-0.004*(i+1)
        f=k.quad([(Rr[i].x,Rr[i].y,z0),(Rr[i+1].x,Rr[i+1].y,z1),(L[i+1].x,L[i+1].y,z1),(L[i].x,L[i].y,z0)],WATER)
        if f.normal.z<0: f.normal_flip()
    rnd=random.Random(49)
    for i in range(14):
        j=rnd.randrange(1,len(P)); side=rnd.choice((L,Rr)); p=side[j]; r=rnd.uniform(0.05,0.10)
        vs=_ico(k,(p.x+rnd.uniform(-0.06,0.06),p.y+rnd.uniform(-0.06,0.06),0.02),r,ROCK,
                (rnd.uniform(0.9,1.3),rnd.uniform(0.8,1.1),rnd.uniform(0.45,0.7)),sub=1,jit=r*0.15,seed=490+i)
        ind_box_uv(k,ind_faces(vs),1.5,(rnd.random(),rnd.random()))
    rnd=random.Random(50)
    ent_tufts(k,[(rnd.uniform(-3.6,3.6),rnd.uniform(0.6,4.6)) for _ in range(14)],seed=50,
              boxes=[((-1.4,-9.0,-1.0),(1.4,deep+0.2,2.6))])
    # no skirt: the cave stands by water (a skirt's top would show over a pool 0.6 m down)

def ent_cave_mouth(k):
    """the spring cave's mouth, dry: a dark way into a hill between mossy boulders, on open ground (a camp's cave)"""
    ent_spring_cave(k,water=False)

# ---------------------------------------------------------------- the sewer grate
def ent_sewer_grate(k):
    """a sewer grate in a street (VKI_Sewer_S1's ladder up): an iron grate over darkness in a kerb of four dressed
    stones, hinged on its north side, a ring to lift it by. Origin: the street surface at its centre (z 0; on paving,
    the paving top); the kerb stands 4 cm proud and goes 0.12 down. 1.44 m square."""
    for s in (-1,1):
        k.box((0,s*0.61,-0.04),(1.44,0.22,0.16),STONE_BLOCK,bevel=0.025)            # north / south kerb stones
        k.box((s*0.61,0,-0.04),(0.22,1.0,0.16),STONE_BLOCK,bevel=0.025)              # east / west, between them
    ent_void(k,[(-0.5,-0.5,0.006),(0.5,-0.5,0.006),(0.5,0.5,0.006),(-0.5,0.5,0.006)])
    for s in (-1,1):                                                                   # frame
        k.box((0,s*0.47,0.025),(1.0,0.06,0.03),IRON,bevel=0.006)
        k.box((s*0.47,0,0.025),(0.06,0.88,0.03),IRON,bevel=0.006)
    for i in range(7): k.box((-0.36+0.12*i,0,0.022),(0.035,0.9,0.025),IRON,bevel=0.0)
    for y in (-0.18,0.18): k.box((0,y,0.038),(0.9,0.035,0.02),IRON,bevel=0.0)
    for x in (-0.3,0.3):                                                               # hinges on the north side
        _cyl(k,(x,0.5,0.035),0.028,0.028,0.16,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    ring(k,(0.0,-0.36,0.055),0.045,0.07,0.016,IRON,n=10,axis="Z")

# ---------------------------------------------------------------- the lock-up
def ent_lockup(k):
    """the town lock-up over the gaol (VKI_Dungeon_B1's way out): a little octagonal stone house with a stepped
    stone dome and a ball finial, an iron-strapped plank door with a barred grille in a dressed surround, a step, a
    lantern on the next face and a barred vent on the other. Origin: the ground at its centre, door face -Y (the wall
    face at y -1.45). 3.2 m across the plinth."""
    ent_oct(k,[(1.58,-0.35),(1.58,0.18),(1.50,0.27),(1.45,0.27)],STONE_BLOCK)          # plinth
    ent_oct(k,[(1.45,0.27),(1.45,2.62)],STONE)                                          # walls
    ent_oct(k,[(1.45,2.62),(1.55,2.70),(1.55,2.86),(1.40,2.86)],STONE_BLOCK)            # cornice
    ent_oct(k,[(1.40,2.86),(1.34,3.12),(1.24,3.12),(1.14,3.38),(1.02,3.38),(0.88,3.60),(0.74,3.60),
               (0.54,3.78),(0.40,3.78),(0.16,3.90)],DRESS,cap_top=True)                 # stepped dome, dark stone
    _cyl(k,(0,0,3.97),0.10,0.08,0.16,8,DRESS)
    vs=_ico(k,(0,0,4.18),0.17,DRESS,sub=2); ind_box_uv(k,ind_faces(vs),0.6)
    yf=-1.45
    # ---- the door: dressed surround, plank leaf, iron straps, barred grille, ring
    for s in (-1,1): k.box((s*0.47,yf-0.05,1.22),(0.14,0.16,1.9),DRESS,bevel=0.025)    # jambs x 0.40-0.54
    k.box((0,yf-0.06,2.30),(1.16,0.18,0.28),DRESS,bevel=0.03)                          # lintel x +-0.58
    k.box((0,yf-0.08,2.33),(0.22,0.2,0.36),DRESS,bevel=0.02)                           # keystone
    for i in range(3): k.box((-0.267+0.267*i,yf-0.03,1.20),(0.262,0.05,1.86),PLANKS,bevel=0.01)
    for z in (0.55,1.05,1.95): k.box((0,yf-0.062,z),(0.8,0.016,0.07),IRON,bevel=0.0)
    ent_void(k,[(-0.15,yf-0.058,1.36),(0.15,yf-0.058,1.36),(0.15,yf-0.058,1.74),(-0.15,yf-0.058,1.74)])
    for (x,z,sx,sz) in ((0,1.35,0.36,0.03),(0,1.75,0.36,0.03),(-0.165,1.55,0.03,0.43),(0.165,1.55,0.03,0.43)):
        k.box((x,yf-0.068,z),(sx,0.02,sz),IRON,bevel=0.0)
    for x in (-0.075,0.0,0.075): k.box((x,yf-0.07,1.55),(0.022,0.022,0.40),IRON,bevel=0.0)
    ring(k,(0.25,yf-0.085,1.02),0.04,0.065,0.015,IRON,n=10,axis="Y")
    k.box((0,-1.78,0.06),(1.1,0.42,0.24),STONE_BLOCK,bevel=0.03)                       # step, top 0.18
    # ---- a lantern on the south-east face, a barred vent on the south-west face
    ap=1.45*math.cos(math.pi/4)
    sub=Kit(); prop_lantern(sub); merge_kit(k,sub,Matrix.Translation((ap,-ap,2.2))@Matrix.Rotation(math.pi/4,4,"Z"))
    sub=Kit()
    ent_void(sub,[(-0.16,-0.012,-0.11),(0.16,-0.012,-0.11),(0.16,-0.012,0.11),(-0.16,-0.012,0.11)])
    for (x,z,sx,sz) in ((0,-0.15,0.44,0.08),(0,0.15,0.44,0.08),(-0.19,0,0.06,0.22),(0.19,0,0.06,0.22)):
        sub.box((x,-0.03,z),(sx,0.07,sz),DRESS,bevel=0.012)
    for x in (-0.06,0.06): sub.box((x,-0.025,0),(0.024,0.024,0.24),IRON,bevel=0.0)
    merge_kit(k,sub,Matrix.Translation((-ap,-ap,2.05))@Matrix.Rotation(-math.pi/4,4,"Z"))

# ---------------------------------------------------------------- link data
def ent_stamp_meta():
    """write ENT_META on the masters: vki_trigger, vki_spawn_local, vki_spawn_facing, vki_prompt_text, vki_facing_min
    and vk_entrance 1 (the link data a placed entrance copies)"""
    for n,m in ENT_META.items():
        o=bpy.data.objects.get(n)
        if o is None: continue
        o["vk_entrance"]=1; o["vki_trigger"]=list(m["trigger"]); o["vki_spawn_local"]=list(m["spawn"])
        o["vki_spawn_facing"]=float(m["facing"]); o["vki_prompt_text"]=m["prompt"]; o["vki_facing_min"]=float(m["facing_min"])

def ent_link(o,lid,coll,scene=ENT_TOWN_SCENE):
    """tag a placed entrance with ENT_TOWN_LINKS entry lid -- vki_link (kind), vki_link_id, vki_target, vki_prompt,
    vki_trigger, vki_facing_min, vki_level -- and put its spawn SPN_<lid> (an arrow empty, world position and
    facing; vki_spawn_id, vki_facing_deg, vki_link_obj) in coll; returns the spawn"""
    lk=next(l for l in ENT_TOWN_LINKS if l[0]==lid)
    m=ENT_META[lk[3]]
    o["vki_link"]=lk[1]; o["vki_link_id"]=lid; o["vki_target"]=lk[2]; o["vki_prompt"]=m["prompt"]
    o["vki_trigger"]=list(m["trigger"]); o["vki_facing_min"]=float(m["facing_min"]); o["vki_level"]=scene
    r=o.rotation_euler.z; c,s=math.cos(r),math.sin(r); sx,sy,sz=m["spawn"]
    old=bpy.data.objects.get("SPN_"+lid)
    if old is not None and any(u.name==coll.name for u in old.users_collection): bpy.data.objects.remove(old)
    sp=bpy.data.objects.new("SPN_"+lid,None); coll.objects.link(sp)
    sp.location=(o.location.x+sx*c-sy*s,o.location.y+sx*s+sy*c,o.location.z+sz)
    face=(float(m["facing"])-math.degrees(r))%360
    sp.empty_display_type="SINGLE_ARROW"; sp.empty_display_size=0.8
    sp.rotation_euler=(-math.pi/2,0.0,-math.radians(face))                            # the arrow points along the facing
    sp["vki_spawn_id"]=lid; sp["vki_facing_deg"]=round(face,3); sp["vki_link_obj"]=o.name; sp["vki_level"]=scene
    return sp

WS_SPECS=[
 ("SM_VK_Entrance_DwarfGate",ent_dwarf_gate,ENT_NG),
 ("SM_VK_Entrance_SpringCave",ent_spring_cave,ENT_NG),
 ("SM_VK_Entrance_CaveMouth",ent_cave_mouth,ENT_NG),
 ("SM_VK_Entrance_SewerGrate",ent_sewer_grate,ENT_NG),
 ("SM_VK_Entrance_LockUp",ent_lockup,ENT_NG),
]
ENT_NAMES=[n for n,_,_ in WS_SPECS]
EXTRA_SPECS+=WS_SPECS
