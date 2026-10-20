# ===================== WS_HARBOUR: the sea harbour (Saltmere's docks) =====================
# prefix hbr_. Executed after the other modules in the same namespace: borrows the water set's helpers (wat_rod,
# wat_seg, wat_deck_planks, wat_annulus, wat_rope, wat_sag) and the market's mkt_put.
# Sea datum, as the quay tiles (vk_terrain_quay): the quay's land at z 0 on the wall line y 0, the water at -2.1, the
# bed at -3.0 (the sea one terrain level below the land). Wall props stand on that line facing -Y (the water); the
# jetty modules run along local +X with the deck top at +0.05 (the river piers' convention), on piles to -4.0.
HBR_Z=-2.1; HBR_BED=-3.0; HBR_PILE=-4.0
HBR_COP=0.08       # the quay's coping top (vk_terrain_quay QY_COP)
HBR_OV=0.07        # its overhang in front of the face

def hbr_pile(k,x,y,z0,z1,r,lean=(0.0,0.0),segs=8):
    """a driven pile, top at (x,y,z1) with an endgrain cap; slimy from the bed to just above the sea's water line"""
    top=Vector((x,y,z1)); bot=Vector((x-lean[0],y-lean[1],z0)); zs=HBR_Z+0.25
    t=(zs-z0)/(z1-z0); mid=bot.lerp(top,t)
    wat_rod(k,bot,mid,r*0.9,r*(0.9+0.1*t),segs,BARK_MOSSY)
    wat_rod(k,mid,top,r*(0.9+0.1*t),r,segs,WOOD,caps="top")

# ================================================================ QUAY-SIDE PROPS (on the wall line, facing -Y)
def hbr_bollard(k):
    """cast-iron bollard set in the coping, 0.3 back from the face"""
    lathe(k,[(0.18,0.0),(0.18,0.04),(0.12,0.08),(0.1,0.32),(0.11,0.42),(0.17,0.47),(0.17,0.53),(0.12,0.57),(0.0,0.6)],
          center=(0,0.3,HBR_COP-0.02),segs=12,mi=IRON)
    k.box((0,0.3,HBR_COP-0.01),(0.42,0.42,0.03),IRON,bevel=0.01)

def hbr_ring(k):
    """iron mooring ring on the wall face, its staple under the coping"""
    k.box((0,-0.015,-0.5),(0.16,0.03,0.2),IRON,bevel=0.01)
    k.box((0,-0.05,-0.47),(0.05,0.07,0.06),IRON,bevel=0.01)
    wat_annulus(k,(0,-0.06,-0.66),0.1,0.14,0.03,IRON,n=14,axis="Y")

def hbr_fender(k):
    """an oak fender down the wall face, iron straps, slimy where the tide reaches"""
    y=-0.12
    k.box((0,y,-0.95),(0.28,0.22,1.4),WOOD,bevel=0.03)                                           # -0.25..-1.65
    k.box((0,y,-2.15),(0.28,0.22,1.0),BARK_MOSSY,bevel=0.03)                                     # -1.65..-2.65
    k.box((0,y,-0.23),(0.3,0.24,0.04),IRON,bevel=0.01)
    for z in(-0.6,-1.4,-2.2):
        k.box((0,y-0.112,z),(0.32,0.02,0.06),IRON,bevel=0.005)
        for s in(-1,1): k.box((s*0.11,y-0.12,z),(0.04,0.02,0.04),IRON,bevel=0.005)

def hbr_ladder(k):
    """iron ladder down the wall face into the water, its grab hoops over the coping"""
    y=-0.12
    for s in(-1,1):
        x=s*0.22
        wat_rod(k,(x,y,-2.7),(x,y,HBR_COP+0.75),0.02,0.02,6,IRON)
        wat_rod(k,(x,y,HBR_COP+0.75),(x,0.42,HBR_COP+0.75),0.02,0.02,6,IRON)
        wat_rod(k,(x,0.42,HBR_COP+0.75),(x,0.42,HBR_COP),0.02,0.02,6,IRON)
        for z in(-0.6,-1.6,-2.5): wat_seg(k,(x,y,z),(x,-0.005,z),0.04,0.04,IRON,bevel=0)          # brackets
    z=-2.55
    while z<-0.05:
        wat_rod(k,(-0.22,y,z),(0.22,y,z),0.016,0.016,6,IRON); z+=0.3

# ================================================================ JETTY (along +X, deck top +0.05)
def hbr_bent(k,x,seed=0,top=0.35):
    """two tall piles at (x, +-1.35), walings under the deck, two tiers of cross braces"""
    rnd=random.Random(seed)
    for y in(-1.35,1.35):
        hbr_pile(k,x+rnd.uniform(-0.03,0.03),y,HBR_PILE,top+rnd.uniform(-0.04,0.03),0.17,
                 lean=(rnd.uniform(-0.1,0.1),rnd.uniform(-0.08,0.08)))
    for dx in(-0.2,0.2): k.box((x+dx,0,-0.47),(0.12,3.3,0.3),WOOD,bevel=0.03)
    for (za,zb) in ((-2.0,-0.5),(-3.2,-2.0)):
        wat_seg(k,(x-0.2,-1.3,za),(x-0.2,1.3,zb),0.1,0.18,WOOD if za>-2.5 else BARK_MOSSY,bevel=0.02)
        wat_seg(k,(x+0.2,-1.3,zb),(x+0.2,1.3,za),0.1,0.18,WOOD if za>-2.5 else BARK_MOSSY,bevel=0.02)
    k.box((x,0,-2.0),(0.44,2.9,0.16),BARK_MOSSY,bevel=0.02)                                        # mid-tier waling

def hbr_jetty_deck(k,seed=1):
    wat_deck_planks(k,-1.5,1.5,seed=seed)
    for y in(-1.2,0.0,1.2): k.box((0,y,-0.17),(3.0,0.18 if y else 0.14,0.3),WOOD,bevel=0.03)
    hbr_bent(k,-1.5,seed=seed)

def hbr_jetty_end(k):
    """the jetty's head: a second bent, bollards with a rope, a ladder down to the water, a lantern on a post"""
    hbr_jetty_deck(k,seed=2); hbr_bent(k,1.5,seed=7)
    for y in(-0.9,0.9):
        lathe(k,[(0.2,0.0),(0.2,0.06),(0.15,0.1),(0.13,0.36),(0.19,0.42),(0.19,0.5),(0.0,0.52)],center=(1.05,y,0.05),segs=10,mi=WOOD)
    wat_rope(k,[Vector((1.05+0.17*math.cos(a),0.9+0.17*math.sin(a),0.22+0.03*a)) for a in [i*0.7 for i in range(12)]],0.03)
    for y in(-0.3,0.3): wat_seg(k,(1.74,y,-2.6),(1.74,y,0.8),0.07,0.06,WOOD,bevel=0.015)
    z=-2.5
    while z<0.75: k.box((1.74,0,z),(0.05,0.62,0.05),WOOD if z>-1.8 else BARK_MOSSY,bevel=0.01); z+=0.3
    wat_rod(k,(1.5,1.35,0.3),(1.5,1.35,2.6),0.1,0.085,8,WOOD,caps="top")
    k.box((1.5,1.0,2.45),(0.08,0.8,0.08),WOOD,bevel=0.02)
    wat_seg(k,(1.5,1.35,2.0),(1.5,0.95,2.42),0.06,0.06,WOOD,bevel=0.01)
    sub=Kit(); prop_lantern(sub); merge_kit(k,sub,Matrix.Translation((1.5,1.44,2.43)))

def hbr_jetty_landing(k):
    """side attachment off a deck module's -Y edge: seven steps down to a landing stage 0.35 above the water,
       handrails, the landing on its own piles"""
    rnd=random.Random(4); zl=HBR_Z+0.35
    for i in range(7):
        z=0.05-0.225*(i+1); y=-1.62-0.3*i
        k.box((0,y,z-0.035),(1.4,0.3,0.07),PLANKS,rot=(0,0,rnd.uniform(-0.02,0.02)),bevel=0.012)
    for x in(-0.72,0.72):
        wat_seg(k,(x,-1.45,-0.02),(x,-3.75,zl-0.1),0.07,0.24,WOOD,bevel=0.02)                     # stringers
        wat_rod(k,(x,-1.45,0.02),(x,-1.45,1.05),0.05,0.045,6,WOOD,caps="top")
        wat_rod(k,(x,-3.65,zl),(x,-3.65,zl+1.0),0.05,0.045,6,WOOD,caps="top")
        wat_seg(k,(x,-3.65,zl+0.95),(x,-1.45,1.0),0.06,0.06,WOOD,bevel=0.01)                       # handrails
    y0,y1=-3.6,-5.3
    sub=Kit(); wat_deck_planks(sub,-1.0,1.0,top=0.0,W=abs(y1-y0),n=8,seed=9)                          # landing stage
    merge_kit(k,sub,Matrix.Translation((0,(y0+y1)/2,zl)))
    for y in(y0-0.15,y1+0.15): k.box((0,y,zl-0.17),(2.1,0.16,0.26),WOOD,bevel=0.03)
    for x in(-0.9,0.9):
        for y in(y0-0.1,y1+0.1): hbr_pile(k,x,y,HBR_PILE,zl+0.3,0.13)
    lathe(k,[(0.14,0.0),(0.14,0.05),(0.1,0.08),(0.09,0.3),(0.13,0.35),(0.0,0.37)],center=(0.6,y1+0.35,zl),segs=8,mi=WOOD)

# ================================================================ BREAKWATER (along X, harbour side -Y, sea side +Y)
def hbr_mole(k,x0,x1,seed=0,par1=None):
    """the mole's run x0..x1: a paved crest at z 0 (y -1.2..1.2), a quay face on the harbour side, a parapet and
       armour rock down to the bed on the sea side"""
    L=x1-x0; xc=(x0+x1)/2; rnd=random.Random(seed)
    k.box((xc,0,-0.12),(L,2.4,0.24),STONE_BLOCK,bevel=0)                                          # crest slabs
    for i in range(int(round(L/0.75))):
        xa=x0+0.75*i; k.box((xa+0.375,-0.6,0.005+rnd.uniform(-0.004,0.004)),(0.73,1.17,0.02),STONE_BLOCK,bevel=0.01)
        k.box((xa+0.375,0.6,0.005+rnd.uniform(-0.004,0.004)),(0.73,1.17,0.02),STONE_BLOCK,bevel=0.01)
    k.box((xc,-1.25,-0.95),(L,0.1,1.9),ASHLAR,bevel=0)                                            # harbour face
    k.box((xc,-1.25,-2.45),(L,0.1,1.1),ROCK_MOSSY,bevel=0)
    for i in range(int(round(L/0.75))):
        xa=x0+0.75*i
        k.box((xa+0.375,-1.23,0.04+rnd.uniform(-0.008,0.008)),(0.74,0.2,0.16),STONE_BLOCK,bevel=0.03)   # kerb
    p1=x1 if par1 is None else par1; Lp=p1-x0
    k.box(((x0+p1)/2,1.5,0.15),(Lp,0.6,1.5),ASHLAR,bevel=0)                                        # parapet -0.6..0.9
    for i in range(max(1,int(round(Lp/0.75)))):
        n_=max(1,int(round(Lp/0.75))); xa=x0+Lp*i/n_
        k.box((xa+Lp/n_/2,1.5,0.97+rnd.uniform(-0.01,0.01)),(Lp/n_-0.01,0.72,0.14),STONE_BLOCK,bevel=0.03)
    k.box((xc,1.8,-1.8),(L,0.1,2.4),ROCK_MOSSY,bevel=0)                                           # parapet's foot
    for row,(y,z,s) in enumerate(((2.3,-0.55,1.0),(3.3,-1.35,1.15),(4.3,-2.15,1.25),(5.2,-2.8,1.1))):
        n=max(2,int(L/(s*0.95)))
        for i in range(n):
            x=x0+(i+0.5)*L/n+rnd.uniform(-0.2,0.2)
            mi=ROCK if z>-1.6 else ROCK_MOSSY
            rock(k,(x,y+rnd.uniform(-0.2,0.2),z+rnd.uniform(-0.1,0.1)),(s*rnd.uniform(0.85,1.1),s*rnd.uniform(0.8,1.0),s*0.75),
                 seed=seed*50+row*10+i,rot_z=rnd.uniform(-0.5,0.5),tilt=0.25,mi=mi,segs=1)

def hbr_breakwater(k): hbr_mole(k,-1.5,1.5,seed=3)

def hbr_breakwater_end(k):
    """the mole's last 3 m (x -1.5..1.5) and its round head at x 3.0 (r 3.0): masonry drum to the bed, armour rock
       round its sea side, a parapet, and the harbour light: a stone tower with a door to the mole, a railed gallery,
       an iron fire basket burning in an open iron lantern, a conical tiled cap"""
    hbr_mole(k,-1.5,0.3,seed=4,par1=0.75)                                                         # into the head
    cx=3.0; R=3.0; n=20
    lathe(k,[(R,HBR_BED),(R,0.0)],center=(cx,0,0),segs=n,mi=ASHLAR)                                # drum
    lathe(k,[(R+0.02,HBR_BED),(R+0.02,-1.7)],center=(cx,0,0),segs=n,mi=ROCK_MOSSY)
    _cyl(k,(cx,0,-0.108),R+0.03,R+0.03,0.24,n,STONE_BLOCK)                                                  # its crest, 12 mm
    rnd=random.Random(8)
    for i in range(12):                                                                           # armour rock,
        a=math.radians(-60+150*i/11)                                                              # the sea side
        for (r,z,s) in ((R+0.9,-1.0,1.05),(R+1.9,-2.2,1.2)):
            rock(k,(cx+math.cos(a)*r,math.sin(a)*r,z+rnd.uniform(-0.1,0.1)),(s,s*0.9,s*0.75),seed=700+i*3+int(r),
                 rot_z=a,tilt=0.25,mi=ROCK if z>-1.6 else ROCK_MOSSY,segs=1)
    for i in range(14):                                                                           # parapet round
        a0=math.radians(-80+226*i/14); a1=math.radians(-80+226*(i+1)/14); am=(a0+a1)/2           # the sea side, to the mole's
        L=2*(R-0.3)*math.sin((a1-a0)/2)
        k.box((cx+math.cos(am)*(R-0.3),math.sin(am)*(R-0.3),0.45),(0.6,L+0.02,0.9),ASHLAR,rot=(0,0,am),bevel=0)
        k.box((cx+math.cos(am)*(R-0.3),math.sin(am)*(R-0.3),0.97+0.012*(i%2)),(0.72,L+0.04,0.14),STONE_BLOCK,rot=(0,0,am),bevel=0.03)
    # the light tower
    tx=cx+0.6; Rt=1.15; H=4.6
    lathe(k,[(Rt+0.12,0.0),(Rt+0.12,0.35),(Rt,0.45),(Rt*0.92,H)],center=(tx,0,0),segs=14,mi=ASHLAR)
    for z in(1.6,3.1):                                                                            # string courses
        rz=Rt-0.08*Rt*(z-0.45)/(H-0.45)
        lathe(k,[(rz-0.01,z),(rz+0.07,z+0.05),(rz+0.07,z+0.11),(rz-0.01,z+0.16)],center=(tx,0,0),segs=14,mi=STONE_BLOCK)
    sub=Kit()                                                                                      # door to the mole
    sub.box((-Rt-0.01,0,1.0),(0.12,0.9,1.9),PLANKS,bevel=0.01)
    sub.box((-Rt-0.03,0,2.02),(0.16,1.1,0.18),STONE_BLOCK,bevel=0.03)
    for y in(-0.5,0.5): sub.box((-Rt-0.03,y,1.0),(0.16,0.14,2.0),STONE_BLOCK,bevel=0.03)
    for z in(0.5,1.5): sub.box((-Rt-0.075,0,z),(0.02,0.8,0.05),IRON,bevel=0)
    merge_kit(k,sub,Matrix.Translation((tx,0,0)))
    for a in(0.6,2.6): k.box((tx+math.cos(a)*(Rt*0.95),math.sin(a)*(Rt*0.95),2.4),(0.1,0.18,0.5),VOID,rot=(0,0,a),bevel=0)   # slits
    _cyl(k,(tx,0,H+0.1),Rt+0.35,Rt+0.35,0.2,16,STONE_BLOCK)                                       # gallery
    for i in range(16):
        a=2*math.pi*i/16; wat_rod(k,(tx+math.cos(a)*(Rt+0.28),math.sin(a)*(Rt+0.28),H+0.2),(tx+math.cos(a)*(Rt+0.28),math.sin(a)*(Rt+0.28),H+1.05),0.025,0.025,5,IRON)
    wat_annulus(k,(tx,0,H+1.05),Rt+0.25,Rt+0.31,0.05,IRON,n=16,axis="Z")
    zl=H+0.2; Rl=0.62                                                                              # the lantern
    _cyl(k,(tx,0,zl+0.06),Rl+0.08,Rl+0.08,0.12,8,STONE_BLOCK)
    for i in range(8):
        a=2*math.pi*(i+0.5)/8; wat_rod(k,(tx+math.cos(a)*Rl,math.sin(a)*Rl,zl+0.12),(tx+math.cos(a)*Rl,math.sin(a)*Rl,zl+1.28),0.035,0.035,4,IRON)
    _cyl(k,(tx,0,zl+0.45),0.3,0.38,0.22,8,IRON); _ico(k,(tx,0,zl+0.62),0.3,GLOW,scale=(1,1,0.8),sub=1)   # the fire
    _cyl(k,(tx,0,zl+1.3),Rl+0.12,Rl+0.12,0.08,8,IRON)
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=8,radius1=Rl+0.18,radius2=0.02,depth=0.95)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((tx,0,zl+1.8)),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update(); k.project(fs,ROOF)
    for f in fs: f.material_index=ROOF
    _ico(k,(tx,0,zl+2.32),0.09,BRONZE,sub=1)

# ================================================================ ROUND 2: SHIPS (origin at the waterline, bow +X)
def hbr_y_at(H,t,z):
    """the hull's inner half width at height z on station t (for decks fitted inside it)"""
    pts=H["sec"](t,True)
    for (y0,z0),(y1,z1) in zip(pts[:-1],pts[1:]):
        if z0<=z<=z1 and z1>z0: return y0+(y1-y0)*(z-z0)/(z1-z0)
    return pts[-1][0] if z>pts[-1][1] else pts[0][0]

def hbr_deck(k,H,L,z,t0,t1,n=14,mi=PLANKS):
    """a deck polygon at height z between stations t0 and t1, following the hull's inner skin"""
    ts=[t0+(t1-t0)*i/n for i in range(n+1)]
    left=[(-L/2+L*t,-hbr_y_at(H,t,z)+0.01,z) for t in ts]; right=[(-L/2+L*t,hbr_y_at(H,t,z)-0.01,z) for t in ts]
    vs=[k.bm.verts.new(p) for p in left+right[::-1]]
    f=k.bm.faces.new(vs); f.material_index=mi; k.bm.normal_update()
    if f.normal.z<0: f.normal_flip()
    for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[mi],l.vert.co.x/TILE[mi])

def hbr_furled(k,x,y0,y1,z,r=0.3,mi=CLOTH_B,n=4):
    """a sail furled on its yard: stretched bundles between rope gaskets"""
    for i in range(n):
        a=y0+(y1-y0)*(i+0.5)/n; s=abs(y1-y0)/n/0.42
        _ico(k,(x,a,z-r*0.6),r,mi,(1.0,s,0.9),sub=1,jit=0.02,seed=i)
    for i in range(1,n): ring(k,(x,y0+(y1-y0)*i/n,z-r*0.6),r*0.85,r*1.1,0.05,BURLAP,n=8,axis="Y")

def hbr_anchor_geo(k,M,s=1.0):
    """an iron anchor (shank along +Z from the crown at the origin, arms in XZ, a wooden stock at the ring)"""
    sub=Kit()
    wat_rod(sub,(0,0,0.0),(0,0,2.0*s),0.06*s,0.05*s,8,IRON)
    for sx in(-1,1):
        arc=[(sx*0.75*s*math.sin(a),0,0.75*s*(1-math.cos(a))) for a in [i*math.pi/12 for i in range(5)]]
        wat_tube(sub,arc,wat_circ(0.055*s,6),IRON)
        tip=Vector(arc[-1])
        sub.box(tuple(tip+Vector((sx*0.06*s,0,-0.05*s))),(0.12*s,0.3*s,0.32*s),IRON,rot=(0,sx*0.5,0),bevel=0.01)
    sub.box((0,0,1.75*s),(0.12*s,1.6*s,0.12*s),WOOD,bevel=0.02)
    wat_annulus(sub,(0,0,2.12*s),0.09*s,0.14*s,0.04*s,IRON,n=10,axis="Y")
    merge_kit(k,sub,M)

def hbr_cog(k):
    """a merchant cog moored in the harbour, 17 m: high clinker sides, a deck with a cargo hatch, castles fore and
       aft, a 16 m mast with a furled square sail and a crow's nest, shrouds and stays, a stern rudder and tiller,
       a bowsprit, an anchor at the bow. Origin at the waterline, bow +X"""
    L=17.0; B2=2.8
    def bfn(t):
        if t<=0.55: return B2*(1-0.33*((0.55-t)/0.55)**2)
        return B2*max(0.0,1-((t-0.55)/0.45)**2)**0.5
    def kfn(t): return -1.5+1.0*max(0.0,(t-0.78)/0.22)**2+0.6*max(0.0,(0.1-t)/0.1)**2
    def sfn(t): return 2.1+0.7*abs(2*t-1)**2.5+0.4*t**4
    H=wat_hull(k,L,22,bfn,kfn,sfn,lambda t:0.0,p=0.35,q=1.6,m=5,th=0.08,bow="point",stern="transom",nin=20)
    wat_gunwale(k,H,w=0.12,h=0.16,upto=22)
    zd=1.35; hbr_deck(k,H,L,zd,0.02,0.9)
    for s in(-1,1):                                                                              # wales
        pts=[(H["xs"][i],s*(abs(H["outer"][i][-1][0])+0.05),zd+0.1) for i in range(1,21)]
        pts=[(x,s*(hbr_y_at(H,(x+L/2)/L,zd+0.1)+0.13),z) for (x,_,z) in pts]
        wat_tube(k,pts,wat_rect(0.1,0.14),WOOD)
    k.box((-0.9,0,zd+0.12),(3.0,2.0,0.24),WOOD,bevel=0.03)                                     # hatch
    k.box((-0.9,0,zd+0.25),(2.7,1.7,0.04),PLANKS,bevel=0.005)
    for (x,y,sz,r) in ((-1.5,-0.35,0.7,0.1),(-0.7,0.4,0.65,-0.2),(-0.6,-0.3,0.6,0.3)):
        k.box((x,y,zd+0.27+sz/2),(sz,sz,sz),WOOD,rot=(0,0,r),bevel=0.03)
    for (x,y) in ((1.8,-1.4),(2.5,-1.3),(1.9,1.4)): barrel(k,x,y,zd,0.32,0.85)
    # aftcastle
    xa0=-L/2+0.25; xa1=-L/2+4.0; za=zd+2.0; ya=hbr_y_at(H,(xa1+L/2)/L,za)-0.05
    k.box(((xa0+xa1)/2,0,za-0.06),(xa1-xa0,2*ya-0.02,0.12),PLANKS,bevel=0.01)
    k.box((xa1,0,zd+1.0),(0.12,2*ya,2.0),PLANKS,bevel=0.01)
    k.box((xa1-0.02,0,zd+0.9),(0.14,0.8,1.8),WOOD,bevel=0.01)                                   # its door
    for s in(-1,1):                                                   # side rails between the end rails
        k.box(((xa0+xa1)/2,s*(ya-0.06),za+0.45),(xa1-xa0-0.24,0.12,0.9),PLANKS,bevel=0.01)
        for i in range(5): k.box((xa0+0.3+i*(xa1-xa0-0.6)/4,s*(ya-0.06),za+1.0),(0.3,0.16,0.22),PLANKS,bevel=0.01)
    k.box((xa1-0.06,0,za+0.45),(0.12,2*ya,0.9),PLANKS,bevel=0.01)
    k.box((xa0+0.06,0,za+0.45),(0.12,2*ya,0.9),PLANKS,bevel=0.01)
    for i in range(5): k.box((xa1-0.06,-ya+0.4+i*(2*ya-0.8)/4,za+1.0),(0.16,0.3,0.22),PLANKS,bevel=0.01)
    # forecastle
    xf0=L/2-4.6; xf1=L/2-2.0; zf=zd+1.6; yf=hbr_y_at(H,(xf0+L/2)/L,zf)-0.05; yf1=hbr_y_at(H,(xf1+L/2)/L,zf)-0.05
    vs=[k.bm.verts.new(p) for p in ((xf0,-yf,zf),(xf1,-yf1,zf),(xf1,yf1,zf),(xf0,yf,zf))]
    f=k.bm.faces.new(vs); f.material_index=PLANKS; k.bm.normal_update()
    if f.normal.z<0: f.normal_flip()
    k.box((xf0,0,zd+0.8),(0.12,2*yf,1.6),PLANKS,bevel=0.01)
    k.box((xf0,0,zf+0.4),(0.12,2*yf,0.8),PLANKS,bevel=0.01)
    for s in(-1,1):
        wat_seg(k,(xf0+0.07,s*(yf-0.06),zf+0.39),(xf1,s*(yf1-0.06),zf+0.39),0.12,0.78,PLANKS,bevel=0.01)
    # mast, crow's nest, yard and sail
    xm=0.6; zt=16.0
    wat_rod(k,(xm,0,zd),(xm,0,zt),0.26,0.14,12,WOOD,caps="top")
    k.box((xm,0,zd+0.12),(0.7,0.7,0.24),WOOD,bevel=0.04)
    for z in(3.5,6.0,8.5): k.box((xm,0,z),(0.42,0.42,0.08),IRON,bevel=0.01)
    lathe(k,[(0.2,12.3),(0.75,12.4),(0.8,12.45),(0.8,13.2),(0.7,13.25)],center=(xm,0,0),segs=12,mi=PLANKS)
    wat_rod(k,(xm+0.3,-4.6,13.9),(xm+0.3,4.6,13.9),0.11,0.11,8,WOOD,caps="end")
    hbr_furled(k,xm+0.3,-4.3,4.3,13.9,r=0.42,n=6)
    for s in(-1,1):                                                                              # shrouds, stays
        for x in(-0.8,0.2,1.2):
            yb=hbr_y_at(H,(x+L/2)/L,sfn((x+L/2)/L))+0.15
            wat_rope(k,[(xm,0,12.0),(x,s*yb,sfn((x+L/2)/L)+0.1)],0.025,WOOD)
        wat_rope(k,[(xm+0.3,s*4.5,13.9),(xa0+0.3,s*(ya-0.1),za+0.9)],0.02,WOOD)                  # braces
    wat_rope(k,[(xm,0,15.0),(L/2+2.6,0,4.15)],0.03,WOOD)                                         # forestay
    wat_rope(k,[(xm,0,15.2),(xa0+0.2,0,za+0.9)],0.03,WOOD)                                       # backstay
    wat_rod(k,(L/2-0.4,0,sfn(1)-0.1),(L/2+2.8,0,4.2),0.16,0.09,8,WOOD,caps="top")                # bowsprit
    # rudder + tiller
    k.box((-L/2-0.18,0,0.4),(0.3,0.14,3.4),WOOD,bevel=0.03)
    for z in(-0.6,0.6,1.6): k.box((-L/2-0.06,0,z),(0.36,0.18,0.06),IRON,bevel=0.01)
    wat_seg(k,(-L/2-0.15,0,za-0.3),(-L/2+1.6,0,za-0.25),0.1,0.1,WOOD,bevel=0.02)
    hbr_anchor_geo(k,Matrix.Translation((L/2-1.8,2.05,1.3))@Matrix.Rotation(-0.25,4,"X")@Matrix.Rotation(math.pi/2,4,"Z")@Matrix.Rotation(math.pi,4,"X"),0.7)

def hbr_fishing_boat(k):
    """a fishing boat, 7.5 m: a short mast with a furled sail, nets heaped amidships, baskets of fish, oars.
       Origin at the waterline, bow +X"""
    L=7.5; B2=1.25
    def bfn(t):
        if t<=0.45: return B2*(1-0.45*((0.45-t)/0.45)**2)
        return B2*max(0.0,1-((t-0.45)/0.55)**2)**0.55
    def kfn(t): return -0.5+0.6*max(0.0,(t-0.72)/0.28)**2+0.25*max(0.0,(0.15-t)/0.15)**2
    def sfn(t): return 0.75+0.35*abs(2*t-1)**2.4+0.1*t**4
    H=wat_hull(k,L,16,bfn,kfn,sfn,lambda t:0.0,p=0.6,q=1.2,m=4,th=0.05,bow="point",stern="transom",nin=14)
    wat_gunwale(k,H,upto=16)
    hb,zs,zk=wat_inner_at(H,0.5)
    k.box((-0.1,0,zk+0.05),(4.4,2*hb*0.55,0.04),PLANKS,bevel=0.005)
    for t in(0.25,0.62):
        hb,zs,zk=wat_inner_at(H,t); x=-L/2+L*t
        k.box((x,0,zs-0.2),(0.3,2*hb+0.02,0.06),WOOD,bevel=0.015)
    xm=-L/2+L*0.62
    wat_rod(k,(xm,0,zk),(xm,0,6.2),0.1,0.06,8,WOOD,caps="top")
    wat_rod(k,(xm+0.12,-2.0,5.6),(xm+0.12,2.0,5.6),0.05,0.05,6,WOOD,caps="end")
    hbr_furled(k,xm+0.12,-1.85,1.85,5.6,r=0.2,n=3)
    for s in(-1,1): wat_rope(k,[(xm,0,6.0),(xm-0.6,s*(B2-0.05),sfn(0.55)+0.03)],0.016,WOOD)
    wat_rope(k,[(xm,0,6.0),(L/2-0.1,0,sfn(1)+0.05)],0.016,WOOD)
    hb,zs,zk=wat_inner_at(H,0.42)
    for i,(x,y,s) in enumerate(((-0.6,0.1,1.0),(-0.2,-0.25,0.8),(-0.9,-0.3,0.7))):              # nets heaped
        _ico(k,(x,y,zk+0.25),0.45*s,NET,(1.4,0.9,0.45),sub=1,jit=0.04,seed=40+i)
        _ico(k,(x,y,zk+0.2),0.42*s,BURLAP,(1.35,0.85,0.4),sub=1,jit=0.03,seed=50+i)
    for i,(x,y) in enumerate(((-2.2,0.35),(-2.3,-0.35))): wat_basket(k,Matrix.Translation((x,y,zk+0.08)),seed=i)
    for s in(-1,1): wat_oar(k,(-2.6,s*0.35,zs-0.1),(1.6,s*0.5,zs-0.05))
    k.box((-L/2-0.1,0,0.1),(0.16,0.08,1.2),WOOD,bevel=0.02)                                     # rudder
    wat_seg(k,(-L/2-0.1,0,sfn(0)+0.1),(-L/2+1.0,0,sfn(0)+0.15),0.06,0.06,WOOD,bevel=0.01)

def hbr_gangplank(k):
    """a cleated gangplank from the quay's edge (origin, z 0) down 0.8 to a ship's deck 4.2 out (-Y)"""
    a=Vector((0,0.3,0.1)); b=Vector((0,-4.2,-0.75)); d=(b-a); L=d.length; pitch=math.atan2(d.z,-d.y)
    k.box(tuple((a+b)/2),(0.75,L,0.08),PLANKS,rot=(pitch,0,0),bevel=0.015)
    n=11
    for i in range(1,n):
        p=a+d*(i/n); k.box((p.x,p.y,p.z+0.06),(0.7,0.05,0.04),WOOD,rot=(pitch,0,0),bevel=0.008)
    for s in(-1,1): k.box((s*0.33,b.y+0.25,b.z-0.02),(0.06,0.5,0.08),WOOD,rot=(pitch,0,0),bevel=0.01)

# ================================================================ ROUND 2: QUAY-SIDE WORKS (on the quay, front -Y)
def hbr_crane(k):
    """a wharf crane on the quay's edge: a braced oak post on a stone footing, a jib reaching 3.4 m over the water,
       a windlass with crank handles, the rope over the jib's sheave down to a hook with a cargo net of sacks"""
    k.box((0,0.6,0.1),(1.6,1.6,0.2),STONE_BLOCK,bevel=0.04)
    k.box((0,0.6,-0.3),(1.5,1.5,0.6),STONE_BLOCK,bevel=0)
    P=Vector((0,0.6,0))
    k.box(tuple(P+Vector((0,0,3.3))),(0.36,0.36,6.6),WOOD,bevel=0.04)
    for z in(1.2,3.0,5.0): k.box(tuple(P+Vector((0,0,z))),(0.42,0.42,0.08),IRON,bevel=0.01)
    for (dx,dy) in ((1,0),(-1,0),(0,1),(0,-1)):
        wat_seg(k,P+Vector((dx*0.7,dy*0.7,0.2)),P+Vector((dx*0.1,dy*0.1,1.7)),0.14,0.14,WOOD,bevel=0.02)
    tip=Vector((0,-2.8,6.3))
    wat_seg(k,P+Vector((0,-0.1,2.6)),tip,0.24,0.24,WOOD,bevel=0.03)                              # jib
    wat_seg(k,P+Vector((0,0,6.5)),tip+Vector((0,0,0.1)),0.16,0.16,WOOD,bevel=0.02)                # its tie
    k.box(tuple(P+Vector((0,0,6.65))),(0.5,0.5,0.1),WOOD,bevel=0.02)
    _cyl(k,tuple(tip+Vector((0,-0.12,-0.05))),0.22,0.22,0.08,12,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))   # sheave
    for s in(-1,1): k.box(tuple(tip+Vector((s*0.08,-0.1,0))),(0.03,0.4,0.36),IRON,bevel=0)
    # windlass on the landward side
    for s in(-1,1):
        k.box((s*0.65,1.5,0.6),(0.12,0.3,1.2),WOOD,bevel=0.02)
        wat_seg(k,(s*0.65,1.2,0.05),(s*0.65,1.45,1.1),0.08,0.08,WOOD,bevel=0.01)
    wat_rod(k,(-0.75,1.5,1.0),(0.75,1.5,1.0),0.16,0.16,10,WOOD,caps="end")
    ring(k,(0,1.5,1.0),0.16,0.22,0.5,HAY,n=12,axis="X")                                          # rope on the drum
    for s in(-1,1):
        wat_seg(k,(s*0.8,1.5,1.0),(s*0.8,1.5,0.62),0.05,0.05,IRON,bevel=0)
        wat_rod(k,(s*0.8,1.5,0.62),(s*1.05,1.5,0.62),0.025,0.025,6,WOOD)
    wat_rope(k,[(0,1.5,1.2),(0,0.45,6.2),tip+Vector((0,0.1,0.15))],0.022,HAY)
    hook=tip+Vector((0,-0.12,-3.4))
    wat_rope(k,[tip+Vector((0,-0.3,-0.05)),hook+Vector((0,0,0.25))],0.022,HAY)
    k.box(tuple(hook+Vector((0,0,0.15))),(0.08,0.06,0.2),IRON,bevel=0.01)
    wat_annulus(k,tuple(hook),0.06,0.1,0.03,IRON,n=10,axis="Y")
    for i in range(4):                                                                           # the sling
        a=2*math.pi*i/4+0.4
        wat_rope(k,[hook,hook+Vector((math.cos(a)*0.45,math.sin(a)*0.45,-0.75))],0.015,HAY)
    for i,(dx,dy,dz) in enumerate(((0,0,-0.95),(0.25,0.15,-1.0),(-0.2,0.2,-1.0),(0.05,-0.2,-0.75))):
        _ico(k,tuple(hook+Vector((dx,dy,dz))),0.3,BURLAP,(1,0.85,1.05),sub=1,jit=0.02,seed=60+i)
    _ico(k,tuple(hook+Vector((0,0,-0.95))),0.6,NET,(1,1,0.8),sub=1,seed=64)

def hbr_cargo_crates(k):
    """crates stacked two high under a rope cargo net, ready for the crane"""
    rnd=random.Random(5)
    for i,(x,y,z,s) in enumerate(((-0.6,0,0,0.85),(0.3,0.05,0,0.85),(-0.15,0.85,0,0.8),(-0.3,0.2,0.85,0.8),(0.45,0.6,0,0.75))):
        r=rnd.uniform(-0.08,0.08)
        k.box((x,y,z+s/2),(s,s,s),WOOD,rot=(0,0,r),bevel=0.03)
        for zz in(z+0.06,z+s-0.06): k.box((x,y,zz),(s+0.02,s+0.02,0.06),PLANKS,rot=(0,0,r),bevel=0.01)
    sub=Kit(); sub.box((0,0,0),(1.0,1.0,1.0),NET,bevel=0.0)
    for f in list(sub.bm.faces):
        if f.normal.z<-0.5: sub.bm.faces.remove(f)
    merge_kit(k,sub,Matrix.Translation((-0.15,0.42,0.86))@Matrix.Diagonal((1.95,1.85,1.74,1)))
    wat_annulus(k,(-0.15,0.42,1.78),0.07,0.11,0.04,IRON,n=10,axis="Y")

def hbr_cargo_bales(k):
    """wool bales, corded, stacked three and two"""
    rnd=random.Random(9)
    for i,(x,y,z) in enumerate(((-0.75,0,0),(0,0.02,0),(0.75,0,0),(-0.37,0.05,0.62),(0.37,0.0,0.62))):
        r=rnd.uniform(-0.06,0.06)
        k.box((x,y,z+0.3),(0.72,1.05,0.6),BURLAP,rot=(0,0,r),bevel=0.1,segs=2)
        for dy in(-0.28,0.28): k.box((x,y+dy,z+0.3),(0.74,0.04,0.62),HAY,rot=(0,0,r),bevel=0.01)

def hbr_capstan(k):
    """a capstan for warping ships in: a waisted drum with whelps on a stone pad, four bars through its head"""
    k.box((0,0,0.05),(1.3,1.3,0.1),STONE_BLOCK,bevel=0.03)
    lathe(k,[(0.45,0.1),(0.45,0.2),(0.32,0.3),(0.28,0.6),(0.32,0.85),(0.45,0.9),(0.45,1.08),(0.0,1.12)],segs=12,mi=WOOD)
    for i in range(8):
        a=2*math.pi*i/8; k.box((math.cos(a)*0.31,math.sin(a)*0.31,0.58),(0.08,0.08,0.55),WOOD,rot=(0,0,a),bevel=0.01)
    for i in range(4):
        a=math.pi*i/4+0.2
        wat_rod(k,(math.cos(a)*-1.25,math.sin(a)*-1.25,1.0),(math.cos(a)*1.25,math.sin(a)*1.25,1.0),0.045,0.045,6,WOOD,caps="end")
    ring(k,(0,0,0.45),0.29,0.35,0.22,HAY,n=12,axis="Z")

def hbr_anchor(k):
    """a spare anchor lying on the quay with its chain"""
    hbr_anchor_geo(k,Matrix.Translation((0,0,0.08))@Matrix.Rotation(-math.pi/2,4,"Y")@Matrix.Rotation(0.15,4,"Z"),0.85)
    for i in range(7):
        x=1.95+i*0.15; wat_annulus(k,(x,0.1*math.sin(i),0.04),0.04,0.07,0.03,IRON,n=8,axis="Y" if i%2 else "Z")

def hbr_rope_coils(k):
    """three coils of hawser on the quay, one tipped against the others"""
    for j,(cx,cy,r0,turns,tilt) in enumerate(((0,0,0.42,3,0.0),(0.85,0.15,0.36,3,0.0),(0.4,0.65,0.34,2,0.6))):
        pts=[]
        for i in range(turns*14+1):
            a=2*math.pi*i/14; rr=r0-0.035*(i/14)
            pts.append(Vector((rr*math.cos(a),rr*math.sin(a),0.04+0.065*(i/14))))
        R=Matrix.Translation((cx,cy,0.0))@Matrix.Rotation(tilt,4,"X")
        sub=Kit(); wat_tube(sub,pts,wat_circ(0.035,5),HAY,caps=True,smooth=True,uscale=0.3); merge_kit(k,sub,R)

def hbr_buoy(k):
    """a mooring buoy, painted, its ring on top and a chain down; origin at the waterline"""
    lathe(k,[(0.0,-0.55),(0.32,-0.5),(0.45,-0.2),(0.48,0.15),(0.4,0.42),(0.12,0.5),(0.0,0.52)],segs=12,mi=CLOTH_A)
    lathe(k,[(0.47,-0.02),(0.5,0.0),(0.5,0.12),(0.48,0.14)],segs=12,mi=YELLOW)
    k.box((0,0,0.56),(0.06,0.06,0.1),IRON,bevel=0.01)
    wat_annulus(k,(0,0,0.68),0.06,0.1,0.03,IRON,n=10,axis="Y")
    for i in range(4): wat_annulus(k,(0,0,-0.62-i*0.13),0.035,0.06,0.025,IRON,n=8,axis="Y" if i%2 else "X")

def hbr_tar_cauldron(k):
    """boiling tar for the caulkers: an iron cauldron on a ring of stones over a fire, a ladle, tar barrels"""
    for i in range(8):
        a=2*math.pi*i/8; rock(k,(math.cos(a)*0.62,math.sin(a)*0.62,0.12),(0.32,0.28,0.24),seed=900+i,rot_z=a,tilt=0.15,segs=1)
    for i in range(5):
        a=2*math.pi*i/5; wat_rod(k,(math.cos(a)*0.45,math.sin(a)*0.45,0.05),(math.cos(a+2.4)*0.25,math.sin(a+2.4)*0.25,0.12),0.05,0.05,6,COAL)
    _ico(k,(0,0,0.18),0.32,GLOW,(1,1,0.6),sub=1,jit=0.04,seed=7)
    lathe(k,[(0.0,0.32),(0.3,0.36),(0.48,0.55),(0.52,0.85),(0.5,0.95),(0.54,1.0)],segs=14,mi=IRON)
    lathe(k,[(0.49,0.95),(0.0,0.93)],segs=14,mi=COAL)
    for i in range(3):
        a=2*math.pi*i/3+0.3; wat_rod(k,(math.cos(a)*0.4,math.sin(a)*0.4,0.36),(math.cos(a)*0.55,math.sin(a)*0.55,0.0),0.03,0.03,5,IRON)
    wat_rod(k,(0.15,0.1,0.95),(0.85,0.55,1.45),0.02,0.02,5,WOOD); _cyl(k,(0.12,0.08,0.93),0.08,0.06,0.06,8,IRON)
    for (x,y) in ((1.2,-0.2),(1.3,0.5)): barrel(k,x,y,0,0.3,0.8)
    lathe(k,[(0.27,0.79),(0.0,0.79)],center=(1.2,-0.2,0),segs=12,mi=COAL)
    barrel(k,-1.05,0.35,0.3,0.3,0.8,lying=True)

def hbr_hull_stocks(k):
    """a ship's hull being built (or rebuilt) on stocks: keel blocks, stem and sternpost, ribs to the sheer, the lower
       strakes planked, shores on both sides, a staging plank on trestles, timber stacked. 9 m, keel 0.8 up"""
    L=9.0; B2=1.6; zk=0.8
    def bfn(t):
        if t<=0.45: return B2*(1-0.4*((0.45-t)/0.45)**2)
        return B2*max(0.0,1-((t-0.45)/0.55)**2)**0.55
    def kfn(t): return zk+0.7*max(0.0,(t-0.75)/0.25)**2+0.4*max(0.0,(0.12-t)/0.12)**2
    def sfn(t): return zk+1.9+0.4*abs(2*t-1)**2.4
    def sfn_p(t): return zk+0.9+0.25*abs(2*t-1)**2.4                                           # planked up to here
    wat_hull(k,L,16,bfn,kfn,sfn_p,lambda t:0.0,p=0.55,q=1.2,m=3,th=0.05,bow="point",stern="transom",nin=14)
    wat_rod(k,(-L/2,0,zk-0.1),(L/2,0,zk-0.1),0.12,0.12,4,WOOD)                                   # keel
    wat_seg(k,(L/2-0.05,0,zk+0.6),(L/2+0.5,0,sfn(1)+0.4),0.16,0.18,WOOD,bevel=0.02)             # stem
    k.box((-L/2-0.05,0,(zk+sfn(0))/2),(0.16,0.18,sfn(0)-zk+0.3),WOOD,bevel=0.02)                 # sternpost
    for i in range(1,12):                                                                        # ribs
        t=i/12; b=bfn(t); kz=kfn(t); sz=sfn(t); fb=0.3*b/B2; x=-L/2+L*t
        pts=[]
        for j in range(7):
            a=(j/6)*math.pi/2; pts.append((fb+(b-fb)*(math.sin(a)**0.65),kz+(sz-kz)*((1-math.cos(a))**1.2)))
        row=[(x,-y,z) for (y,z) in reversed(pts[1:])]+[(x,y,z) for (y,z) in pts]
        wat_tube(k,row,wat_rect(0.09,0.07),WOOD,up=(1,0,0))
    for s in(-1,1):                                                                              # sheer clamp
        wat_tube(k,[(-L/2+L*t,s*(bfn(t)+0.02),sfn(t)-0.05) for t in [i/12 for i in range(1,12)]],wat_rect(0.08,0.1),WOOD)
    for x in(-3.0,-1.0,1.0,3.0):                                                                  # keel blocks
        for z in(0.15,0.45): k.box((x,0,z),(0.4,0.9 if z<0.3 else 0.7,0.3),WOOD,bevel=0.02)
    for s in(-1,1):                                                                              # shores
        for x in(-2.5,0.0,2.5):
            t=(x+L/2)/L; wat_seg(k,(x,s*(bfn(t)+1.3),0.0),(x,s*(bfn(t)-0.05),zk+1.1),0.12,0.12,WOOD,bevel=0.02)
    for x in(-2.2,2.2):                                                                          # staging
        for dx in(-0.35,0.35): wat_seg(k,(x+dx,-2.6+dx*0.15,0),(x,-2.6+dx*0.15,1.2),0.08,0.08,WOOD,bevel=0.01)
    k.box((0,-2.6,1.25),(5.2,0.4,0.06),PLANKS,bevel=0.01)
    for i in range(4): k.box((0,3.0,0.06+0.11*i),(4.5,0.3+0.02*(i%2),0.1),PLANKS,rot=(0,0,0.02*(i-1.5)),bevel=0.01)

def hbr_booth(k):
    """the harbourmaster's booth: a plank hut with a pent roof, its counter flap propped open as an awning, the
       ledger and a balance on the counter, a lantern, an anchor painted on its sign"""
    W,D,H=2.4,1.8,2.4
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(W/2-0.06),sy*(D/2-0.06),(H+0.25*(-sy))/2),(0.12,0.12,H+0.25*(-sy)),WOOD,bevel=0.02)
    k.box((0,D/2-0.09,H/2),(W-0.24,0.05,H),PLANKS,bevel=0.01)                                      # back (walls between
    for sx in(-1,1):                                                                              # the posts, off
        k.box((sx*(W/2-0.09),0,1.05),(0.05,D-0.24,2.1),PLANKS,bevel=0.01)                         # their faces)
    k.box((W/2-0.045,-0.2,0.95),(0.04,0.8,1.85),WOOD,bevel=0.01)                                   # side door
    k.box((0,-D/2+0.09,0.5),(W-0.24,0.05,1.0),PLANKS,bevel=0.01)                                   # front below the counter
    k.box((0,-D/2-0.08,1.03),(W+0.1,0.42,0.06),PLANKS,bevel=0.01)                                  # counter
    k.box((0,-D/2+0.09,2.35),(W-0.24,0.05,0.5),PLANKS,bevel=0.01)                                  # over the hatch
    flap=Vector((0,-D/2-0.35,2.0))
    k.box(tuple(flap),(W,0.9,0.05),PLANKS,rot=(-0.45,0,0),bevel=0.01)
    for sx in(-1,1): wat_seg(k,(sx*(W/2-0.15),-D/2-0.02,1.06),(sx*(W/2-0.15),-D/2-0.72,1.8),0.04,0.04,WOOD,bevel=0)
    k.box((0,0,2.72),(W+0.4,D+0.5,0.06),ROOF,rot=(0.12,0,0),bevel=0.015)                           # pent roof
    k.box((0,-D/2-0.12,2.62),(W+0.4,0.08,0.12),WOOD,bevel=0.02)
    _book(k,-0.5,-D/2-0.08,1.06,0.36,0.26,0.05,CLOTH_A,0.1)
    _cyl(k,(0.35,-D/2-0.1,1.07),0.05,0.06,0.04,8,BRONZE)
    k.box((0.35,-D/2-0.1,1.25),(0.02,0.02,0.36),BRONZE,bevel=0)
    k.box((0.35,-D/2-0.1,1.42),(0.4,0.02,0.02),BRONZE,bevel=0)
    for s in(-1,1): _cyl(k,(0.35+s*0.19,-D/2-0.1,1.28),0.08,0.08,0.02,8,BRONZE)
    k.box((0,-D/2-0.05,2.25),(1.0,0.04,0.36),WOOD,bevel=0.01)                                     # sign
    hbr_anchor_geo(k,Matrix.Translation((0,-D/2-0.09,2.1)),0.12)
    sub=Kit(); prop_lantern(sub); merge_kit(k,sub,Matrix.Translation((-W/2-0.05,-D/2-0.2,1.9)))

# ================================================================ ROUND 3: DOCK BUILDINGS (single pieces, front -Y)
# Built from the kit's own walls (wall_stone_* / twn_wall_stoneup_* / twn_wall_stone_shop / timber_frame and their
# corners) through mkt_put, as the market hall, so they match the houses round them; light roofs of their own on the
# kit profile (roof_z).
def hbr_face(k,pts,mi,want,uvs=None):
    """one polygon facing roughly `want`; uvs: one per point (else projected)"""
    vs=[k.bm.verts.new(p) for p in pts]; f=k.bm.faces.new(vs); f.material_index=mi; k.bm.normal_update()
    if f.normal.dot(Vector(want))<0: f.normal_flip()
    if uvs:
        m={v:uv for v,uv in zip(vs,uvs)}
        for l in f.loops: l[k.uv].uv=m[l.vert]
    else: k.project([f],mi)
    return f

def hbr_roof_gable(k,A,ov=0.45,gable=STONE):
    """gabled tile roof over a 2A x 6 m block (wall top at z 0, ridge along X) on the kit's profile (roof_z), the gables
       overhanging ov with verge boards; gable: the triangle walls' material at x +-A (None: open gables)"""
    T=TILE[ROOF]; W=TILE[WOOD]; drop=RT*1.2; ts=(0.0,HALF/2,HALF,EAVE); x0,x1=-A-ov,A+ov
    nx=max(2,int(round((x1-x0)/1.5))); xs=[x0+(x1-x0)*i/nx for i in range(nx+1)]
    for s in(-1,1):
        for xa,xb in zip(xs[:-1],xs[1:]):
            for ta,tb in zip(ts[:-1],ts[1:]):
                za,zb=roof_z(ta),roof_z(tb)
                hbr_face(k,((xa,s*ta,za),(xb,s*ta,za),(xb,s*tb,zb),(xa,s*tb,zb)),ROOF,(0,s*0.6,1),
                         [(xa/T,slope_dist(ta)/T),(xb/T,slope_dist(ta)/T),(xb/T,slope_dist(tb)/T),(xa/T,slope_dist(tb)/T)])
                hbr_face(k,((xa,s*ta,za-drop),(xb,s*ta,za-drop),(xb,s*tb,zb-drop),(xa,s*tb,zb-drop)),WOOD,(0,0,-1),
                         [(xa/W,ta/W),(xb/W,ta/W),(xb/W,tb/W),(xa/W,tb/W)])
            ze=roof_z(EAVE)
            hbr_face(k,((xa,s*EAVE,ze),(xb,s*EAVE,ze),(xb,s*EAVE,ze-drop),(xa,s*EAVE,ze-drop)),WOOD,(0,s,0))
        for x,sx in ((x0,-1),(x1,1)):                                     # the slab's ends, verge boards
            for ta,tb in zip(ts[:-1],ts[1:]):
                za,zb=roof_z(ta),roof_z(tb)
                hbr_face(k,((x,s*ta,za),(x,s*tb,zb),(x,s*tb,zb-drop),(x,s*ta,za-drop)),WOOD,(sx,0,0))
            xv=x+sx*(0.03+(0.012 if s>0 else 0.0))                         # the two boards cross at the apex: apart
            def_beam(k,(xv,s*(EAVE+0.04),roof_z(EAVE)+0.04),(xv,0,RIDGE+0.06),0.07,0.3,WOOD,bevel=0.02)
    n=max(1,int(round((x1-x0)/0.75)))
    for i in range(n):
        xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n
        k.box(((xa+xb)/2,0,RIDGE+0.1),(xb-xa+0.04,0.36,0.36),ROOF,rot=(math.pi/4,0,0),bevel=0.1,segs=2)
    if gable is not None:
        prof=[(-HALF,0.0)]+[(y,max(0.0,roof_z(abs(y))-drop-0.03)) for y in (-HALF/2,0.0,HALF/2)]+[(HALF,0.0)]
        for x in(-A,A):
            for xf,want in ((x+0.25*(1 if x>0 else -1),(1 if x>0 else -1,0,0)),(x-0.25*(1 if x>0 else -1),(-1 if x>0 else 1,0,0))):
                hbr_face(k,[(xf,y,z) for (y,z) in prof],gable,want)

def hbr_hoist(k,drop=1.7):
    """a hoist beam out of a gable (origin on the wall line at the wall top, out -Y), its rope and a hanging bale
       `drop` below the wall top"""
    k.box((0,-0.95,1.42),(0.2,1.6,0.2),WOOD,bevel=0.04,segs=2)
    k.box((0,-1.78,1.42),(0.26,0.06,0.26),WOOD,bevel=0.02)
    def_beam(k,(0,-1.62,1.52),(0,-0.3,1.95),0.035,0.035,IRON,bevel=0)
    k.box((0,-1.55,1.24),(0.1,0.12,0.18),IRON,bevel=0.015)
    ring(k,(0,-1.55,1.12),0.04,0.15,0.07,WOOD,n=12,axis="X")
    wat_rope(k,[(0,-1.7,1.1),(0,-1.7,-drop+0.35)],0.022,HAY)
    wat_rope(k,[(0,-1.4,1.1),(0,-1.4,0.4)],0.022,HAY)
    wat_annulus(k,(0,-1.7,-drop+0.3),0.03,0.06,0.025,IRON,n=8,axis="X")
    k.box((0,-1.7,-drop-0.05),(0.7,0.55,0.55),BURLAP,bevel=0.08,segs=2)
    for dx in(-0.18,0.18): k.box((dx,-1.7,-drop-0.05),(0.04,0.57,0.57),HAY,bevel=0.01)
    for s in(-1,1): wat_rope(k,[(0,-1.7,-drop+0.28),(s*0.3,-1.7,-drop+0.22)],0.015,HAY)

def hbr_corners(k,L,D,z,fn):
    for (x,y,r) in ((-L/2,-D/2,0),(L/2,-D/2,90),(L/2,D/2,180),(-L/2,D/2,-90)): mkt_put(k,fn,x,y,z,r)

def hbr_warehouse(k):
    """a two-storey stone warehouse, its gable to the quay (-Y): the cart door below, the loading door above with the
       hoist beam out of the gable and a bale on the rope, small windows; 6 x 9 m, ridge 9.6 m"""
    L,D=6.0,9.0; top=H1+H2
    mkt_put(k,wall_stone_door,-1.5,-D/2,0,0); mkt_put(k,wall_stone_window,1.5,-D/2,0,0)
    mkt_put(k,twn_wall_stoneup_loading,-1.5,-D/2,H1,0); mkt_put(k,lambda sb: twn_wall_stoneup_window(sb,False),1.5,-D/2,H1,0)
    mkt_put(k,wall_stone_plain,-1.5,D/2,0,180); mkt_put(k,wall_stone_window,1.5,D/2,0,180)
    mkt_put(k,twn_wall_stoneup,-1.5,D/2,H1,180); mkt_put(k,twn_wall_stoneup_slit,1.5,D/2,H1,180)
    for sx,r in ((-1,-90),(1,90)):
        for y,g,u in ((-3.0,wall_stone_plain,twn_wall_stoneup),(0.0,wall_stone_window,twn_wall_stoneup_slit),(3.0,wall_stone_plain,twn_wall_stoneup)):
            mkt_put(k,g,sx*L/2,y,0,r); mkt_put(k,u,sx*L/2,y,H1,r)
    hbr_corners(k,L,D,0,corner_stone); hbr_corners(k,L,D,H1,twn_corner_stoneup)
    mkt_put(k,lambda sb: hbr_roof_gable(sb,D/2),0,0,top,90)
    mkt_put(k,lambda sb: hbr_hoist(sb,drop=1.9),-1.5,-D/2,top,0)
    k.box((-1.5,-D/2-0.55,0.06),(2.4,0.7,0.12),STONE_BLOCK,bevel=0.03)                          # the door's stoop

def hbr_fish_market(k):
    """the covered fish market: an open timber shed on stone pads (9 x 6), a flagged floor, a gabled tile roof, two rows
       of stone-topped tables with crates and baskets of fish, a hanging balance, a trough, a fish sign on the gable"""
    A=4.5; zt=3.2
    k.box((0,0,-0.24),(9.8,6.8,0.72),ASHLAR,bevel=0.04)                                        # floor 0.12
    for x in(-4.5,-1.5,1.5,4.5):
        for y in(-3.0,3.0):
            k.box((x,y,0.22),(0.5,0.5,0.2),STONE_BLOCK,bevel=0.04)
            k.box((x,y,(0.32+zt)/2),(0.26,0.26,zt-0.32),WOOD,bevel=0.04)
            for s in(-1,1):
                if abs(x+s*1.0)<=4.5: def_beam(k,(x,y,zt-0.9),(x+s*0.85,y,zt-0.12),0.12,0.12,WOOD)
        k.box((x,0,zt-0.08),(0.22,6.4,0.24),WOOD,bevel=0.03)                                      # tie beams
    for y in(-3.0,3.0): k.box((0,y,zt+0.06),(9.4,0.3,0.3),WOOD,bevel=0.04)                       # wall plates
    mkt_put(k,lambda sb: hbr_roof_gable(sb,A,ov=0.6,gable=None),0,0,zt+0.2,0)
    rnd=random.Random(12)
    for y in(-1.25,1.25):                                                                         # tables
        for x in(-3.0,0.0,3.0):
            k.box((x,y,0.9),(2.6,0.9,0.1),STONE_BLOCK,bevel=0.02)
            for dx in(-1.0,1.0):
                for dy in(-0.3,0.3): k.box((x+dx,y+dy,0.5),(0.1,0.1,0.75),WOOD,bevel=0.01)
            for j in range(2):
                wat_fish_crate(k,Matrix.Translation((x-0.6+1.2*j,y+rnd.uniform(-0.1,0.1),0.95))@Matrix.Rotation(rnd.uniform(-0.2,0.2),4,"Z"),seed=int(x*10+y*3+j),n=3)
        for x in(-4.0,1.6): wat_basket(k,Matrix.Translation((x,y*1.55,0.12)),fish=x<0,seed=int(x))
    for i in range(3):                                                                            # loose fish
        wat_fish(k,Matrix.Translation((-0.3+0.12*i,-1.3,0.99))@Matrix.Rotation(rnd.uniform(0,6.28),4,"Z")@Matrix.Rotation(math.pi/2,4,"X"),0.4)
    def_beam(k,(1.5,0,zt-0.2),(1.5,0,zt-0.9),0.025,0.025,IRON,bevel=0)                            # the balance
    k.box((1.5,0,zt-0.92),(0.9,0.05,0.05),IRON,bevel=0)
    for s in(-1,1):
        wat_rope(k,[(1.5+s*0.44,0,zt-0.92),(1.5+s*0.44,0,zt-1.45)],0.01,IRON)
        _cyl(k,(1.5+s*0.44,0,zt-1.47),0.16,0.18,0.04,10,BRONZE)
    mkt_put(k,prop_trough,-3.6,2.8,0.12,0)
    for sx in(-1,1): k.box((sx*A,0,zt+(0.2+RIDGE)/2),(0.2,0.2,0.2+RIDGE),WOOD,bevel=0.03)        # gable king posts
    k.box((A+0.13,0,zt+1.4),(0.06,1.4,0.6),WOOD,bevel=0.02)                                      # the sign
    wat_fish(k,Matrix.Translation((A+0.2,0,zt+1.4))@Matrix.Rotation(math.pi/2,4,"Z"),1.1)

def hbr_chandlery(k):
    """the ship chandler's: a stone shop below (its counter down, the shutter up as an awning) with rope, lanterns and
       a small anchor on the counter, a timber storey above, a gabled roof, an anchor sign on an iron bracket, barrels,
       a coil and oars outside; 6 x 6 m"""
    L,D=6.0,6.0; top=H1+H2
    mkt_put(k,twn_wall_stone_shop,-1.5,-D/2,0,0); mkt_put(k,wall_stone_door,1.5,-D/2,0,0)
    mkt_put(k,wall_stone_plain,-1.5,D/2,0,180); mkt_put(k,wall_stone_window,1.5,D/2,0,180)
    for sx,r in ((-1,-90),(1,90)):
        mkt_put(k,wall_stone_window,sx*L/2,-1.5,0,r); mkt_put(k,wall_stone_plain,sx*L/2,1.5,0,r)
    W_=lambda sb: timber_frame(sb,True); P_=lambda sb: timber_frame(sb); X_=lambda sb: timber_frame(sb,False,"X")
    mkt_put(k,W_,-1.5,-D/2,H1,0); mkt_put(k,W_,1.5,-D/2,H1,0)
    mkt_put(k,P_,-1.5,D/2,H1,180); mkt_put(k,W_,1.5,D/2,H1,180)
    for sx,r in ((-1,-90),(1,90)): mkt_put(k,X_,sx*L/2,-1.5,H1,r); mkt_put(k,W_,sx*L/2,1.5,H1,r)
    hbr_corners(k,L,D,0,corner_stone); hbr_corners(k,L,D,H1,mkt_corner_post)
    mkt_put(k,lambda sb: hbr_roof_gable(sb,L/2,gable=PLASTER),0,0,top,0)
    yc=-D/2-0.55; zc=TWN_CZ                                                                       # the counter's wares
    for i,x in enumerate((-2.3,-1.85)): ring(k,(x,yc,zc+0.05+0.06*i),0.06,0.17,0.06,HAY,n=12,axis="Z")
    ring(k,(-2.05,yc,zc+0.2),0.06,0.16,0.06,HAY,n=12,axis="Z")
    for x in(-1.3,-1.0):                                                                          # lanterns
        k.box((x,yc,zc+0.13),(0.13,0.13,0.2),GLOW,bevel=0.01)
        for z in(zc+0.02,zc+0.25): k.box((x,yc,z),(0.17,0.17,0.04),IRON,bevel=0.01)
        wat_annulus(k,(x,yc,zc+0.31),0.03,0.05,0.015,IRON,n=8,axis="Y")
    hbr_anchor_geo(k,Matrix.Translation((-0.65,yc,zc+0.02))@Matrix.Rotation(math.pi/2,4,"Y")@Matrix.Rotation(0.3,4,"X"),0.22)
    def_beam(k,(0.2,-D/2-0.25,3.5),(0.2,-D/2-1.25,3.5),0.05,0.05,IRON,bevel=0)                   # sign bracket
    def_beam(k,(0.2,-D/2-0.25,3.0),(0.2,-D/2-0.95,3.48),0.035,0.035,IRON,bevel=0)
    k.box((0.2,-D/2-0.8,3.05),(0.05,0.8,0.62),WOOD,bevel=0.015)
    for y in(-D/2-0.5,-D/2-1.1): wat_rope(k,[(0.2,y,3.48),(0.2,y,3.36)],0.012,IRON)
    hbr_anchor_geo(k,Matrix.Translation((0.23,-D/2-0.8,2.83))@Matrix.Rotation(math.pi/2,4,"Z"),0.2)
    for (x,y) in ((2.6,-3.6),(2.5,-4.25)): barrel(k,x,y,0,0.32,0.85)
    for i in range(3):
        a=i*0.55; ring(k,(-2.5+0.05*i,-D/2-1.5,0.04+0.06*i),0.12,0.32,0.07,HAY,n=14,axis="Z")
    for x in(0.6,0.85): wat_oar(k,(x,-D/2-0.32,0.0),(x+0.05,-D/2-0.12,2.4))

def hbr_customs_house(k):
    """the customs house: an open ashlar loggia of three arches on the quay side where goods are declared (a table with
       the ledger and a balance, bales and crates under declaration), a stone upper storey with windows, the city's
       banners on iron poles, a hipped tile roof; 9 x 6 m"""
    A=4.5; D=3.0; GH=MKT_GH; top=GH+H2
    k.box((0,0,-0.24),(2*A+0.9,2*D+0.9,0.72),ASHLAR,bevel=0.04)
    mkt_put(k,lambda sb: mkt_arcade(sb,2*A+2*MKT_T,D,(-3.0,0.0,3.0),MKT_HW,True,seed=11),0,0,0,0)
    k.box((0,-D,GH-0.1),(2*A+0.8,0.8,0.24),STONE_BLOCK,bevel=0.04)                              # string course
    for x,fn in ((-3.0,wall_stone_window),(0.0,wall_stone_door),(3.0,wall_stone_window)):       # the loggia's back
        mkt_put(k,fn,x,-0.5,0,0); mkt_put(k,fn if fn is not wall_stone_door else wall_stone_window,x,D,0,180)
    for sx,r in ((-1,-90),(1,90)):
        mkt_put(k,wall_stone_plain,sx*A,-1.5,0,r); mkt_put(k,wall_stone_window,sx*A,1.5,0,r)
    for y0,y1 in ((-0.75,-0.25),(D-0.25,D+0.25)): k.box((0,(y0+y1)/2,(H1+GH)/2),(2*A,y1-y0,GH-H1),STONE,bevel=0)
    for sx in(-1,1): k.box((sx*A,0,(H1+GH)/2),(0.5,2*D-0.6,GH-H1),STONE,bevel=0)
    for (x,y,r) in ((A,D,180),(-A,D,-90)): mkt_put(k,corner_stone,x,y,0,r)
    for (x,y) in ((A,D),(-A,D)): k.box((x-0.0,y,(H1+GH)/2),(0.8,0.8,GH-H1),STONE,bevel=0)
    k.box((0,-1.6,GH-0.1),(2*A-0.6,1.8,0.2),PLANKS,bevel=0)                                     # loggia ceiling
    for x in(-1.5,1.5): k.box((x,-1.6,GH-0.32),(0.28,1.9,0.26),WOOD,bevel=0.03)
    for x in(-3.0,0.0,3.0): mkt_put(k,lambda sb: twn_wall_stoneup_window(sb,True),x,-D,GH,0)
    mkt_put(k,twn_wall_stoneup,-3.0,D,GH,180); mkt_put(k,twn_wall_stoneup_window,0.0,D,GH,180); mkt_put(k,twn_wall_stoneup,3.0,D,GH,180)
    for sx,r in ((-1,-90),(1,90)): mkt_put(k,twn_wall_stoneup_window,sx*A,-1.5,GH,r); mkt_put(k,twn_wall_stoneup,sx*A,1.5,GH,r)
    hbr_corners(k,2*A,2*D,GH,twn_corner_stoneup)
    mkt_put(k,lambda sb: mkt_roof(sb,A),0,0,top,0)
    for x in(-1.5,1.5):                                                                           # banners
        wat_rod(k,(x,-D-0.2,GH+2.3),(x,-D-0.95,GH+2.3),0.03,0.03,6,IRON)
        k.box((x,-D-0.85,GH+1.45),(0.7,0.03,1.6),CLOTH_A,bevel=0.01)
        k.box((x,-D-0.87,GH+0.68),(0.7,0.035,0.08),YELLOW,bevel=0.005)
        _cyl(k,(x,-D-0.88,GH+1.55),0.17,0.17,0.012,12,YELLOW,rot=Matrix.Rotation(math.pi/2,4,"X"))
    k.box((0,-1.4,0.85),(1.8,0.8,0.08),PLANKS,bevel=0.02)                                        # the officer's table
    for sx in(-0.8,0.8):
        for sy in(-1.75,-1.05): k.box((sx,sy,0.47),(0.08,0.08,0.75),WOOD,bevel=0.01)
    _book(k,-0.4,-1.45,0.89,0.4,0.28,0.06,CLOTH_A,0.15)
    _cyl(k,(0.45,-1.4,0.91),0.05,0.06,0.04,8,BRONZE); k.box((0.45,-1.4,1.1),(0.02,0.02,0.36),BRONZE,bevel=0)
    k.box((0.45,-1.4,1.27),(0.4,0.02,0.02),BRONZE,bevel=0)
    for s in(-1,1): _cyl(k,(0.45+s*0.19,-1.4,1.13),0.08,0.08,0.02,8,BRONZE)
    _cyl(k,(0,-0.9,0.45),0.22,0.24,0.06,10,WOOD)
    for i in range(3): k.box((math.cos(i*2.1)*0.15,-0.9+math.sin(i*2.1)*0.15,0.22),(0.05,0.05,0.44),WOOD,bevel=0.01)
    for i,(x,y) in enumerate(((-3.2,-1.6),(-2.6,-1.3),(3.0,-1.6))):
        k.box((x,y,0.42),(0.72,1.0,0.6),BURLAP,rot=(0,0,0.2*i),bevel=0.1,segs=2)
    for (x,y,s) in ((2.4,-1.2,0.7),(2.6,-2.0,0.6)): k.box((x,y,0.12+s/2),(s,s,s),WOOD,bevel=0.03)

# ================================================================ SPECS
WS_SPECS=[
    ("SM_VK_Harbour_Bollard",hbr_bollard,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_Ring",hbr_ring,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_Fender",hbr_fender,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_Ladder",hbr_ladder,dict(wobble=False,grime=False)),
    ("SM_VK_Jetty_Deck",hbr_jetty_deck,dict(wobble=False,grime=False)),
    ("SM_VK_Jetty_End",hbr_jetty_end,dict(wobble=False,grime=False)),
    ("SM_VK_Jetty_Landing",hbr_jetty_landing,dict(wobble=False,grime=False)),
    ("SM_VK_Breakwater",hbr_breakwater,dict(wobble=False,grime=False)),
    ("SM_VK_Breakwater_End",hbr_breakwater_end,dict(wobble=False,grime=False)),
    ("SM_VK_Ship_Cog",hbr_cog,dict(wobble=False,grime=False)),
    ("SM_VK_Boat_Fishing",hbr_fishing_boat,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_Gangplank",hbr_gangplank,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_Crane",hbr_crane,dict(wobble=False,grime=True)),
    ("SM_VK_Cargo_Crates",hbr_cargo_crates,dict(wobble=False,grime=True)),
    ("SM_VK_Cargo_Bales",hbr_cargo_bales,dict(wobble=False,grime=True)),
    ("SM_VK_Harbour_Capstan",hbr_capstan,dict(wobble=False,grime=True)),
    ("SM_VK_Harbour_Anchor",hbr_anchor,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_RopeCoils",hbr_rope_coils,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_Buoy",hbr_buoy,dict(wobble=False,grime=False)),
    ("SM_VK_Harbour_TarCauldron",hbr_tar_cauldron,dict(wobble=False,grime=True)),
    ("SM_VK_Ship_Hull_Stocks",hbr_hull_stocks,dict(wobble=False,grime=True)),
    ("SM_VK_Harbour_Booth",hbr_booth,dict(wobble=False,grime=True)),
    ("SM_VK_Dock_Warehouse",hbr_warehouse,dict(wobble=False,grime=True)),
    ("SM_VK_Dock_FishMarket",hbr_fish_market,dict(wobble=False,grime=True)),
    ("SM_VK_Dock_Chandlery",hbr_chandlery,dict(wobble=False,grime=True)),
    ("SM_VK_Dock_CustomsHouse",hbr_customs_house,dict(wobble=False,grime=True)),
]
EXTRA_SPECS+=WS_SPECS
