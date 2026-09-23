# ================================================================ IRON
def ind_log(k,a,b,r,seed=0,bark=BARK_OAK):
    """short log with end-grain caps from a to b"""
    ind_rod(k,a,b,r,bark,segs=7,r2=r*0.92)
    a=Vector(a); b=Vector(b); d=(b-a).normalized()
    q=Vector((0,0,1)).rotation_difference(d).to_matrix().to_4x4()
    for p in (a-d*0.005,b+d*0.005):
        vs=_cyl(k,tuple(p),r*0.9,r*0.9,0.012,7,ENDGRAIN,rot=q)
        ind_box_uv(k,ind_faces(vs),0.5,(seed*0.31%1,seed*0.17%1))
def ind_charcoal_mound(k):
    """turf-covered charcoal clamp, r 2.0 x h 1.4; log ends show at the foot, glowing smoke vents (Smoke sockets at the 4 vents + top)"""
    vs=ind_heap(k,(0,0,0),2.05,2.0,1.45,SOIL,seed=3,sub=3,rough=0.07,peak=0.75,tile=1.6)
    bvh=ind_bvh(k); rnd=random.Random(7)
    # turf sods and burnt patches on the surface
    for i in range(16):
        a=rnd.uniform(0,2*math.pi); d=rnd.uniform(0.2,1.7)
        x,y=math.cos(a)*d,math.sin(a)*d; z=ind_drop(bvh,x,y)
        nrm=Vector((x/2.0,y/2.0,1.0)).normalized()
        mi=MOSS if i%3 else COAL
        sub=Kit(); sub.box((0,0,0),(rnd.uniform(0.35,0.6),rnd.uniform(0.3,0.5),0.08),mi,bevel=0.03,jitter=0.02,seed=i)
        q=Vector((0,0,1)).rotation_difference(nrm).to_matrix().to_4x4()
        merge_kit(k,sub,Matrix.Translation((x,y,z-0.01))@q@Matrix.Rotation(rnd.uniform(0,6),4,"Z"))
    # vents: 4 around the shoulder + one at the top, each a dark hole with embers
    for i in range(5):
        if i<4: a=i*math.pi/2+0.5; x,y=math.cos(a)*1.05,math.sin(a)*1.05
        else: x,y=0.0,0.0
        z=ind_drop(bvh,x,y)
        nrm=Vector((x/1.6,y/1.6,1.0)).normalized(); q=Vector((0,0,1)).rotation_difference(nrm).to_matrix().to_4x4()
        sub=Kit(); r=0.16 if i<4 else 0.24
        ring(sub,(0,0,0.02),r,r+0.1,0.1,SOIL,n=8,axis="Z")
        _cyl(sub,(0,0,-0.02),r,r,0.04,8,VOID)
        _ico(sub,(0,0,0.0),r*0.55,GLOW,(1,1,0.5),sub=1)
        merge_kit(k,sub,Matrix.Translation((x,y,z))@q)
    # log ends peeking out at the foot
    for i in range(18):
        a=2*math.pi*i/18+rnd.uniform(-0.08,0.08); r0=1.72+rnd.uniform(-0.05,0.08)
        z=0.12+0.14*(i%2)
        ind_log(k,(math.cos(a)*(r0-0.4),math.sin(a)*(r0-0.4),z),(math.cos(a)*(r0+0.12),math.sin(a)*(r0+0.12),z-0.03),rnd.uniform(0.09,0.12),seed=i)
    # ladder and rake
    for s in(-0.22,0.22): ind_beam(k,(2.2,s,0.0),(0.9,s,1.25),0.06,0.07,WOOD,bevel=0.01)
    for j in range(5):
        t=(j+0.6)/6; k.box((2.2-1.3*t,0,1.25*t),(0.05,0.5,0.05),WOOD,bevel=0.01)
    ind_beam(k,(-1.2,-1.9,0.02),(-2.1,-0.6,1.3),0.05,0.05,WOOD,bevel=0.01)
    k.box((-1.18,-1.93,0.06),(0.5,0.08,0.06),WOOD,rot=(0,0,-0.95),bevel=0.01)
    ind_skirt(k,-1.7,1.7,-1.7,1.7,mi=SOIL)
def ind_bloomery(k):
    """clay shaft furnace on a stone base; glowing tap arch at -Y (Fire), glowing throat at the top (Smoke), tuyere at +X"""
    ind_lathe(k,[(1.25,-0.6),(1.25,0.0),(1.2,0.55),(1.12,0.95)],segs=16,mi=STONE,tile=3.0,around=3)
    ind_lathe(k,[(1.12,0.95),(1.02,1.6),(0.92,2.2),(0.78,2.9),(0.72,3.15),(0.8,3.25),(0.7,3.3),(0.55,3.2)],segs=16,mi=CLAY,tile=1.5)
    ind_lathe(k,[(0.55,3.2),(0.5,2.9)],segs=16,mi=VOID)
    _cyl(k,(0,0,2.95),0.5,0.5,0.04,16,GLOW)
    for z,r in((1.25,1.08),(2.35,0.9)): ring(k,(0,0,z),r,r+0.05,0.1,IRON,n=16,axis="Z")
    # base rocks
    rnd=random.Random(4)
    for i in range(12):
        a=2*math.pi*(i+0.5)/12
        if abs(a-1.5*math.pi)<0.45: continue
        rock(k,(math.cos(a)*1.22,math.sin(a)*1.22,0.22+0.28*(i%2)),(0.5,0.35,0.36),seed=20+i,rot_z=a,mi=STONE_BLOCK,segs=1)
    # tap arch (front, -Y)
    hw=0.24; zs=0.25; ya=-1.16
    pts=[(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+0.28+math.sin(math.pi*j/8)*hw) for j in range(9)]+[(-hw,zs)]
    f=k.bm.faces.new([k.bm.verts.new((x,ya,z)) for x,z in pts]); f.material_index=GLOW; k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    k.project([f],GLOW)
    for j in range(7):
        a=math.pi*(j+0.5)/7
        k.box((math.cos(a)*(hw+0.1),ya-0.06,zs+0.28+math.sin(a)*(hw+0.1)),(0.14,0.2,0.2),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.02)
    for s in(-1,1): k.box((s*(hw+0.1),ya-0.06,zs+0.14),(0.16,0.2,0.3),STONE_BLOCK,bevel=0.02)
    # slag run and bloom lumps in front
    ind_heap(k,(0.05,-1.55,0.0),0.45,0.35,0.12,COAL,seed=9,sub=2)
    k.box((0,-1.35,0.06),(0.16,0.5,0.05),GLOW,bevel=0.02)
    for i in range(4): _ico(k,(0.6+0.18*i,-1.55+0.12*(i%2),0.08),0.1,IRON,(1.2,1,0.8),sub=1,jit=0.02,seed=i)
    # tuyere (clay pipe) at +X where the bellows attach
    _cyl(k,(1.35,0,0.55),0.1,0.13,0.5,8,CLAY,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # charging ladder at the back
    for s in(-0.25,0.25): ind_beam(k,(-0.25+s,1.9,0.0),(-0.1+s,0.95,3.1),0.07,0.07,WOOD,bevel=0.01)
    for j in range(8):
        t=(j+0.6)/9; k.box((-0.18,1.9-0.95*t,3.1*t),(0.55,0.05,0.05),WOOD,bevel=0.01)
    ind_skirt(k,-1.2,1.2,-1.2,1.2)
def ind_bellows(k):
    """pair of leather bellows on a trestle, nozzle toward -X (points at a tuyere), with a pump lever"""
    k.box((0.1,0,0.3),(1.2,0.6,0.08),PLANKS,bevel=0.02)
    for x in(-0.35,0.55):
        for y in(-0.25,0.25): k.box((x,y,0.14),(0.08,0.08,0.3),WOOD,bevel=0.02)
    # bellows body: bottom board, leather bag (pleated), top board
    zb=0.36; L=1.0
    for i,(z,s) in enumerate(((zb,1.0),(zb+0.1,1.06),(zb+0.2,1.0),(zb+0.3,1.06),(zb+0.4,1.0))):
        sub=Kit(); vs=sub.box((0,0,0),(L*s,0.62*s,0.12),HIDE,bevel=0.04,segs=1)
        for v in set(vs):   # wedge: narrow at the nozzle end (-X)
            t=(v.co.x+L/2)/L; v.co.y*=0.35+0.65*t; v.co.z*=0.3+0.7*t
        merge_kit(k,sub,Matrix.Translation((0.05,0,z+0.06-0.02*i)))
    for z in(zb-0.01,zb+0.53):
        sub=Kit(); vs=sub.box((0,0,0),(L+0.08,0.66,0.05),WOOD,bevel=0.015)
        for v in set(vs): t=(v.co.x+L/2)/L; v.co.y*=0.4+0.6*t
        merge_kit(k,sub,Matrix.Translation((0.05,0,z))@Matrix.Rotation(0.1 if z>0.5 else 0,4,"Y"))
    ind_rod(k,(-0.45,0,0.52),(-0.95,0,0.5),0.05,IRON,segs=8,r2=0.03)
    # handle + lever post
    k.box((0.72,0,0.95),(0.3,0.08,0.06),WOOD,bevel=0.01)
    k.box((0.95,0.42,0.6),(0.12,0.12,1.2),WOOD,bevel=0.02)
    ind_beam(k,(0.95,0.36,1.15),(0.2,0.0,0.96),0.07,0.07,WOOD,bevel=0.01)
    ind_rod(k,(0.62,0,0.92),(0.6,0,1.08),0.02,HAY,segs=4)

# ================================================================ CLAY
def ind_bottle_kiln(k):
    """bottle kiln (lathe 2.2 -> 0.8 at 6.0) with iron bonts, fire mouths (GLOW) and a clammins door at -Y.
       Sockets: Smoke at the top (0,0,6.3), Fire at the 5 fire mouths."""
    prof=[(2.25,-0.6),(2.25,0.0),(2.3,0.7),(2.3,1.5),(2.18,2.6),(2.0,3.5),(1.6,4.3),(1.1,5.0),(0.9,5.6),(0.8,6.0),(0.95,6.12),(0.95,6.3),(0.72,6.3),(0.7,5.9)]
    ind_lathe(k,prof,segs=20,mi=CLAY,tile=1.5)
    _cyl(k,(0,0,5.95),0.7,0.7,0.05,16,VOID)
    ind_lathe(k,[(2.5,-0.6),(2.5,0.3),(2.38,0.42),(0.0,0.42)],segs=20,mi=STONE_BLOCK,tile=1.2)   # plinth
    # iron bonts following the profile
    def rad(z):
        for (r0,z0),(r1,z1) in zip(prof[1:],prof[2:]):
            if z0<=z<=z1: return r0+(r1-r0)*(z-z0)/(z1-z0)
        return prof[1][0]
    for z in(1.0,1.9,2.8,3.6,4.4,5.2):
        r=rad(z); ring(k,(0,0,z),r-0.01,r+0.05,0.09,IRON,n=20,axis="Z")
    # fire mouths around the base: arched GLOW openings with brick surrounds
    for i in range(6):
        a=-math.pi/2+2*math.pi*i/6
        if i==0: continue
        sub=Kit(); hw=0.26; zs=0.5; ya=-2.33
        pts=[(hw,zs)]+[(math.cos(math.pi*j/6)*hw,zs+0.22+math.sin(math.pi*j/6)*hw) for j in range(7)]+[(-hw,zs)]
        f=sub.bm.faces.new([sub.bm.verts.new((x,ya,z)) for x,z in pts]); f.material_index=GLOW; sub.bm.normal_update()
        if f.normal.y>0: f.normal_flip()
        sub.project([f],GLOW)
        for j in range(5):
            aa=math.pi*(j+0.5)/5
            sub.box((math.cos(aa)*(hw+0.09),ya-0.05,zs+0.22+math.sin(aa)*(hw+0.09)),(0.15,0.16,0.14),CLAY,rot=(0,-(aa-math.pi/2),0),bevel=0.02)
        sub.box((0,ya-0.12,zs-0.06),(0.8,0.3,0.12),STONE_BLOCK,bevel=0.02)
        merge_kit(k,sub,Matrix.Rotation(a+math.pi/2,4,"Z"))
    # clammins (bricked-up loading door) with a wooden door at -Y
    hw=0.62; zs=1.35; y=-2.36
    k.quad([(-hw,y,0.42),(hw,y,0.42),(hw,y,zs),(-hw,y,zs)],PLANKS,uvs=[(0,0),(1.24,0),(1.24,0.93),(0,0.93)])
    pts=[(math.cos(math.pi*j/8)*hw,zs+math.sin(math.pi*j/8)*hw*0.8) for j in range(9)]
    f=k.bm.faces.new([k.bm.verts.new((x,y,z)) for x,z in pts]); f.material_index=PLANKS; k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    k.project([f],PLANKS)
    for j in range(9):
        aa=math.pi*(j+0.5)/9
        k.box((math.cos(aa)*(hw+0.12),y-0.04,zs+math.sin(aa)*(hw*0.8+0.12)),(0.2,0.2,0.18),CLAY,rot=(0,-(aa-math.pi/2),0),bevel=0.02)
    for s in(-1,1): k.box((s*(hw+0.12),y-0.04,0.9),(0.22,0.2,0.95),CLAY,bevel=0.02)
    for z in(0.75,1.3): k.box((0,y-0.03,z),(1.1,0.03,0.08),IRON,bevel=0.01)
    k.box((0,y-0.35,0.47),(1.5,0.7,0.1),STONE_BLOCK,bevel=0.03)
def ind_clay_pit(k):
    """3x3 cell clay digging: wet clay floor, spoil banks, puddles, spade, plank walkway, basket of lumps"""
    rnd=random.Random(3)
    vs=k.box((0,0,-0.29),(2.9,2.9,0.6),CLAY,bevel=0)
    grid_cut(k,vs,0.5)
    for v in k.bm.verts:
        if abs(v.co.z-0.01)<0.02 and abs(v.co.x)<1.4 and abs(v.co.y)<1.4:
            v.co.z-=0.06*(1-max(abs(v.co.x),abs(v.co.y))/1.45)+0.02*noise.noise(v.co*1.3)
    # spoil banks along two edges
    ind_heap(k,(-0.6,1.2,0),1.2,0.4,0.42,SOIL,seed=5,sub=2,rough=0.2)
    ind_heap(k,(1.2,0.3,0),0.4,1.0,0.35,SOIL,seed=6,sub=2,rough=0.2)
    for i,(x,y) in enumerate(((-1.2,1.3),(0.2,1.35),(1.3,-0.4),(1.35,0.9),(-1.35,-1.3))): ind_tuft(k,(x,y,0.12),0.45,seed=i)
    # puddles
    for (x,y,r) in((-0.6,-0.5,0.5),(0.4,-0.9,0.3)):
        f=k.bm.faces.new([k.bm.verts.new((x+math.cos(a)*r*1.3,y+math.sin(a)*r,-0.02)) for a in [2*math.pi*i/10 for i in range(10)]])
        f.material_index=WATER; k.bm.normal_update()
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    # cut steps (dug blocks of clay) and lumps
    for i in range(3): k.box((0.2+i*0.35,0.55,0.08),(0.3,0.3,0.22),CLAY,rot=(0,0,rnd.uniform(-.3,.3)),bevel=0.05,jitter=0.02,seed=i)
    # plank walkway + spade + basket
    for i in range(2): k.box((-0.5+i*0.02,-0.1+i*0.26,0.04),(2.2,0.24,0.05),PLANKS,rot=(0,0,0.05),bevel=0.01)
    ind_beam(k,(0.75,-0.25,-0.1),(0.62,-0.45,1.05),0.05,0.05,WOOD,bevel=0.01)
    k.box((0.62,-0.45,1.08),(0.2,0.05,0.05),WOOD,rot=(0,0,-0.9),bevel=0.01)
    k.box((0.77,-0.23,0.05),(0.22,0.04,0.3),STEEL,rot=(0.1,0,-0.9),bevel=0.02)
    _cyl(k,(-1.05,-0.95,0.18),0.24,0.3,0.36,10,WATTLE)
    for i in range(5): _ico(k,(-1.05+rnd.uniform(-.14,.14),-0.95+rnd.uniform(-.14,.14),0.37),0.1,CLAY,(1.2,1,0.8),sub=1,jit=0.02,seed=i)
def ind_potters_wheel(k):
    """kick wheel with a seat, a pot being thrown, finished pots on a board. Work socket at the seat (0,0.45)"""
    k.box((0,0.45,0.5),(0.8,0.36,0.06),PLANKS,bevel=0.015)             # seat
    for x in(-0.34,0.34):
        for y in(-0.35,0.55): k.box((x,y,0.3),(0.08,0.08,0.6),WOOD,bevel=0.015)
    for y in(-0.35,0.55): k.box((0,y,0.12),(0.76,0.07,0.07),WOOD,bevel=0.01)
    k.box((0,-0.35,0.62),(0.8,0.3,0.06),PLANKS,bevel=0.015)            # work table
    _cyl(k,(0,-0.05,0.13),0.34,0.34,0.1,16,STONE_BLOCK)                 # kick wheel
    _cyl(k,(0,-0.05,0.45),0.03,0.03,0.72,6,IRON)
    _cyl(k,(0,-0.05,0.8),0.2,0.2,0.04,14,WOOD)                          # wheel head
    ind_lathe(k,[(0.0,0.82),(0.09,0.82),(0.13,0.88),(0.14,0.95),(0.1,1.02),(0.08,1.06),(0.06,1.04)],c=(0,-0.05,0),segs=12,mi=CLAY,smooth=True)
    # finished pots on a side board
    k.box((0.75,-0.15,0.35),(0.4,0.7,0.05),PLANKS,bevel=0.01)
    for y in(-0.4,0.1): k.box((0.75,y,0.17),(0.35,0.06,0.34),WOOD,bevel=0.01)
    for i,(y,h) in enumerate(((-0.35,0.3),(-0.05,0.22),(0.15,0.26))):
        ind_lathe(k,[(0.0,0.38),(0.07,0.38),(0.11,0.38+h*0.4),(0.07,0.38+h*0.85),(0.08,0.38+h)],c=(0.75,y,0),segs=10,mi=CLAY,smooth=True)
    ind_heap(k,(-0.55,-0.4,0.0),0.22,0.2,0.2,CLAY,seed=2,sub=1)       # lump of prepared clay
def ind_brick_stack(k,c,courses,rotz=0.0,seed=0,pallet=True):
    """pallet stack of CLAY bricks 0.26x0.13x0.08, alternate courses crossed; hidden joints merged"""
    sub=Kit(); L,W,H=0.26,0.13,0.08; gp=0.012; X=3*L; Y=4*W
    rnd=random.Random(seed)
    z0=0.13 if pallet else 0.0
    if pallet:
        for y in(-Y/2+0.06,0,Y/2-0.06): sub.box((0,y,0.035),(X+0.1,0.1,0.07),WOOD,bevel=0.01)
        for i in range(5): sub.box((-X/2+0.08+i*(X-0.16)/4,0,0.09),(0.12,Y+0.08,0.03),PLANKS,bevel=0.005)
    for cz in range(courses):
        z=z0+cz*(H+0.006)+H/2; top=cz==courses-1
        if cz%2==0:   # bricks along X: 3 x 4 rows
            for j in range(4):
                y=-Y/2+(j+0.5)*W
                if 0<j<3 and not top: sub.box((0,y,z),(X-gp,W-gp,H),CLAY,bevel=0)
                else:
                    for i in range(3): sub.box((-X/2+(i+0.5)*L+rnd.uniform(-.008,.008),y,z),(L-gp,W-gp,H),CLAY,rot=(0,0,rnd.uniform(-.03,.03)),bevel=0)
        else:         # bricks along Y: 6 columns of 2
            for i in range(6):
                x=-X/2+(i+0.5)*X/6
                if not top: sub.box((x,0,z),(X/6-gp,Y-gp,H),CLAY,bevel=0)
                else:
                    for j in range(2): sub.box((x,-Y/4+j*Y/2,z),(X/6-gp,Y/2-gp,H),CLAY,rot=(0,0,rnd.uniform(-.03,.03)),bevel=0)
    merge_kit(k,sub,Matrix.Translation(Vector(c))@Matrix.Rotation(rotz,4,"Z"))
def ind_pile_bricks(k,size=1):
    rnd=random.Random(size*5)
    if size==1: ind_brick_stack(k,(0,0,0),6,0.05,seed=1)
    elif size==2:
        ind_brick_stack(k,(-0.45,0,0),7,0.04,seed=2); ind_brick_stack(k,(0.48,0.05,0),4,-0.06,seed=3)
    else:
        ind_brick_stack(k,(-0.9,0,0),7,0.03,seed=4); ind_brick_stack(k,(0.0,0.05,0),6,-0.05,seed=5); ind_brick_stack(k,(0.9,-0.05,0),3,0.08,seed=6)
    for i in range(2+size):   # loose and broken bricks
        k.box((rnd.uniform(-0.6,0.6)*size,-0.55-rnd.uniform(0,0.3),0.04),(0.26 if i%2 else 0.15,0.13,0.08),CLAY,rot=(0,0,rnd.uniform(0,3)),bevel=0.005)
