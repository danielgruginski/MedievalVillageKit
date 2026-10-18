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
    k.box((x,0,-2.0),(0.5,2.9,0.16),BARK_MOSSY,bevel=0.02)                                        # mid-tier waling

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
    _cyl(k,(cx,0,-0.108),R,R,0.24,n,STONE_BLOCK)                                                  # its crest, 12 mm
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
        k.box((cx+math.cos(am)*(R-0.3),math.sin(am)*(R-0.3),0.97),(0.72,L+0.04,0.14),STONE_BLOCK,rot=(0,0,am),bevel=0.03)
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
]
EXTRA_SPECS+=WS_SPECS
