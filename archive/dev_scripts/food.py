# ================================================================ FOOD
def ind_cone_roof(k,z0,r0,z1,r1,c=(0,0),segs=16,mi=ROOF,kick=0.25,tiles=None):
    """conical (bell-cast) roof from radius r0 at z0 to r1 at z1; ROOF uvs: u around, v down the slope"""
    prof=[(r0+0.15,z0-0.12),(r0,z0),(r0-(r0-r1)*0.18,z0+(z1-z0)*0.12+kick*0.1),(r0-(r0-r1)*0.5,z0+(z1-z0)*0.52),(r1,z1)]
    fs=lathe(k,prof,center=(c[0],c[1],0),segs=segs,mi=mi)
    tiles=tiles or max(3,round(2*math.pi*r0/TILE.get(mi,3.0)*1.4))
    sl=[0.0]
    for (a,b) in zip(prof[:-1],prof[1:]): sl.append(sl[-1]+math.hypot(a[0]-b[0],a[1]-b[1]))
    for f in fs:
        ang=[math.atan2(l.vert.co.y-c[1],l.vert.co.x-c[0]) for l in f.loops]
        if max(ang)-min(ang)>math.pi: ang=[a+2*math.pi if a<0 else a for a in ang]
        for l,a in zip(f.loops,ang):
            r=math.hypot(l.vert.co.x-c[0],l.vert.co.y-c[1])
            j=min(range(len(prof)),key=lambda i:abs(prof[i][0]-r)+abs(prof[i][1]-l.vert.co.z))
            l[k.uv].uv=(a/(2*math.pi)*tiles,-sl[j]/TILE.get(mi,3.0)*1.1)
    # underside
    lathe(k,[(r1*0.9,z1-0.1),(r0-0.05,z0-0.08)],center=(c[0],c[1],0),segs=segs,mi=WOOD)
    return fs
def ind_oast(k):
    """oast kiln: round STONE roundel r 2.2 x 5.0, conical ROOF r 2.4 x 3.6, white PLASTER cowl with a vane (top ~10.6).
       Door at -Y. Sockets: Smoke at the cowl mouth (0,0.3,9.3); Door (0,-3.1,0); the cowl can be split off as a Spin part later."""
    R=2.2
    ind_lathe(k,[(R+0.12,-0.6),(R+0.12,0.35),(R+0.04,0.5),(R,1.0),(R,5.0),(R-0.3,5.0)],segs=16,mi=STONE,tile=3.0,around=5)
    ind_lathe(k,[(R+0.2,0.0),(R+0.2,0.42),(R+0.05,0.5)],segs=16,mi=STONE_BLOCK,tile=1.2)
    ring(k,(0,0,4.95),R-0.02,R+0.12,0.16,WOOD,n=16,axis="Z")                       # wall plate
    ind_cone_roof(k,5.0,R+0.3,8.55,0.42,segs=16)
    # cowl: round collar, box body, slanted hood, vane
    _cyl(k,(0,0,8.6),0.5,0.5,0.14,12,WOOD)
    z0=8.65; W=0.8
    sub=Kit()
    sub.box((0,0,z0+0.5),(W,W,1.0),PLASTER,bevel=0.03)
    sub.quad([(-W/2+0.08,W/2+0.012,z0+0.12),(W/2-0.08,W/2+0.012,z0+0.12),(W/2-0.08,W/2+0.012,z0+0.9),(-W/2+0.08,W/2+0.012,z0+0.9)][::-1],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    L=math.hypot(W+0.3,0.55)
    sub.box((0,0.12,z0+1.25),(W+0.12,L,0.08),PLASTER,rot=(-math.atan2(0.55,W+0.3),0,0),bevel=0.02)
    for s in(-1,1):
        v=[sub.bm.verts.new(p) for p in ((s*W/2,-W/2,z0+1.0),(s*W/2,W/2+0.1,z0+1.0),(s*W/2,-W/2,z0+1.52))]
        f=sub.bm.faces.new(v if s>0 else v[::-1]); f.material_index=PLASTER
    sub.bm.normal_update()
    for i in range(4): sub.box((0,-W/2-0.01,z0+0.2+i*0.22),(W+0.02,0.03,0.05),WOOD,bevel=0.005)
    ind_beam(sub,(0,-W/2,z0+0.9),(0,-W/2-1.1,z0+1.2),0.06,0.06,WOOD,bevel=0.01)       # vane arm
    sub.box((0,-W/2-1.1,z0+1.2),(0.04,0.55,0.5),PLASTER,bevel=0.01)
    _cyl(sub,(0,0,z0+1.75),0.03,0.03,0.5,6,IRON)
    _ico(sub,(0,0,z0+1.95),0.07,BRONZE,sub=1)
    merge_kit(k,sub,Matrix.Rotation(0.35,4,"Z"))
    # door, loading hatch + small window
    hw=0.55; zt=2.1; y=-R-0.02
    k.quad([(-hw,y,0.4),(hw,y,0.4),(hw,y,zt),(-hw,y,zt)],PLANKS,uvs=[(0,0),(1.1,0),(1.1,1.7),(0,1.7)])
    for s in(-1,1): k.box((s*(hw+0.1),y,1.25),(0.2,0.2,1.75),STONE_BLOCK,bevel=0.03)
    k.box((0,y,zt+0.12),(1.45,0.24,0.26),STONE_BLOCK,bevel=0.03)
    for z in(0.8,1.7): k.box((0,y-0.02,z),(1.0,0.03,0.08),IRON,bevel=0.01)
    k.box((0,y-0.35,0.45),(1.4,0.7,0.1),STONE_BLOCK,bevel=0.03)
    a=math.radians(140); cx,cy=math.cos(a)*(R+0.01),math.sin(a)*(R+0.01)
    sub=Kit()
    sub.quad([(-0.4,0,3.0),(0.4,0,3.0),(0.4,0,3.9),(-0.4,0,3.9)],PLANKS,uvs=[(0,0),(0.8,0),(0.8,0.9),(0,0.9)])
    sub.box((0,-0.05,3.98),(1.0,0.22,0.16),WOOD,bevel=0.02); sub.box((0,-0.08,2.94),(0.95,0.26,0.1),WOOD,bevel=0.02)
    for s in(-1,1): sub.box((s*0.45,-0.03,3.45),(0.12,0.16,1.0),WOOD,bevel=0.02)
    merge_kit(k,sub,Matrix.Translation((cx,cy,0))@Matrix.Rotation(a+math.pi/2,4,"Z"))
    a=math.radians(20); sub=Kit()
    sub.box((0,0.0,2.6),(0.3,0.1,0.5),VOID,bevel=0); sub.box((0,-0.05,2.9),(0.5,0.16,0.12),STONE_BLOCK,bevel=0.02)
    merge_kit(k,sub,Matrix.Translation((math.cos(a)*R,math.sin(a)*R,0))@Matrix.Rotation(a+math.pi/2,4,"Z"))
def ind_mash_tun(k):
    """brewer's mash tun: big stave tun r 0.9 on a stone plinth, mash + paddle, spout into an underback trough, step"""
    R=0.9; n=20
    k.box((0,0,0.14),(2.0,2.0,0.28),STONE_BLOCK,bevel=0.05,segs=1)
    for zz,(r0,r1) in((0.52,(R*0.95,R)),(0.98,(R,R*0.97))): _cyl(k,(0,0,zz),r0,r1,0.46,n,WOOD)
    for z in(0.36,0.78,1.14): ring(k,(0,0,z),R+0.005,R+0.05,0.07,IRON,n=n,axis="Z")
    lathe(k,[(R*0.97,1.21),(R*0.9,1.21),(R*0.88,1.1)],segs=n,mi=WOOD)
    ind_heap(k,(0,0,1.02),0.85,0.85,0.12,BREAD,seed=4,sub=2,rough=0.1)
    ind_beam(k,(-0.3,-0.2,1.0),(0.5,0.5,2.0),0.06,0.06,WOOD,bevel=0.01)
    k.box((-0.37,-0.26,0.95),(0.22,0.05,0.35),WOOD,rot=(0,0,0.7),bevel=0.01)
    # spout + underback trough
    _cyl(k,(0,-R-0.15,0.42),0.05,0.05,0.35,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    k.box((0,-R-0.55,0.2),(1.1,0.5,0.4),WOOD,bevel=0.03)
    k.quad([(-0.48,-R-0.75,0.36),(0.48,-R-0.75,0.36),(0.48,-R-0.35,0.36),(-0.48,-R-0.35,0.36)],BREAD,uvs=[(0,0),(1,0),(1,0.4),(0,0.4)])
    # wooden step on the side
    k.box((R+0.45,0.2,0.2),(0.45,0.8,0.4),PLANKS,bevel=0.02); k.box((R+0.3,0.2,0.5),(0.35,0.8,0.08),PLANKS,bevel=0.02)
    # sacks of malt
    for i,(x,y) in enumerate(((-1.2,0.7),(-1.25,0.1))):
        _ico(k,(x,y,0.32),0.3,BURLAP,(0.9,0.8,1.1),jit=0.02,seed=i); _cyl(k,(x,y,0.66),0.07,0.1,0.1,6,BURLAP)
def ind_cider_press(k):
    """twin-post screw press 1.4 x 1.0 x 2.0 with a pomace cheese on the bed, juice spout and tub, apple basket"""
    for x in(-0.62,0.62):
        k.box((x,0,1.0),(0.22,0.26,2.0),WOOD,bevel=0.04)
        k.box((x,0,0.08),(0.4,0.9,0.16),WOOD,bevel=0.03)
    k.box((0,0,1.95),(1.6,0.3,0.3),WOOD,bevel=0.04)                  # head beam
    k.box((0,0,0.5),(1.1,0.95,0.16),WOOD,bevel=0.03)                 # bed
    for (x,y,sx,sy) in((0,-0.45,1.1,0.06),(0,0.45,1.1,0.06),(-0.52,0,0.06,0.95),(0.52,0,0.06,0.95)):
        k.box((x,y,0.61),(sx,sy,0.07),WOOD,bevel=0.01)
    # cheese: layers of pomace and straw
    for i in range(5):
        mi=HAY if i%2 else BREAD
        k.box((0,0,0.66+i*0.1),(0.8-i*0.01,0.7-i*0.01,0.1),mi,bevel=0.03,jitter=0.01,seed=i)
    k.box((0,0,1.2),(0.9,0.78,0.08),PLANKS,bevel=0.01)                 # pressing board
    k.box((0,0,1.3),(0.5,0.3,0.12),WOOD,bevel=0.02)
    # screw with thread rings + capstan bar
    _cyl(k,(0,0,1.62),0.1,0.1,0.7,10,WOOD)
    for j in range(6): ring(k,(0,0,1.33+j*0.1),0.09,0.14,0.04,WOOD,n=10,axis="Z")
    _cyl(k,(0,0,2.18),0.14,0.14,0.18,10,WOOD)
    ind_beam(k,(-0.9,0,2.18),(0.9,0,2.18),0.06,0.06,WOOD,bevel=0.01)
    # juice spout + tub
    k.box((0,-0.56,0.54),(0.12,0.2,0.05),WOOD,bevel=0.01)
    _cyl(k,(0,-0.82,0.18),0.24,0.28,0.36,12,WOOD); ring(k,(0,-0.82,0.28),0.28,0.31,0.05,IRON,n=12,axis="Z")
    _cyl(k,(0,-0.82,0.32),0.25,0.25,0.02,12,YELLOW)
    # basket of apples
    _cyl(k,(1.05,-0.45,0.17),0.25,0.3,0.34,10,WATTLE)
    rnd=random.Random(3)
    for i in range(8):
        _ico(k,(1.05+rnd.uniform(-.17,.17),-0.45+rnd.uniform(-.17,.17),0.36+rnd.uniform(0,0.06)),0.075,APPLE,sub=1)
    for i in range(3): _ico(k,(0.8+i*0.15,-0.9+rnd.uniform(-.1,.1),0.07),0.07,APPLE,sub=1)
def ind_skep(k,c=(0,0,0),s=1.0,board=True):
    """coiled straw beehive (HAY lathe r 0.28 x 0.45) with an entrance"""
    cx,cy,cz=c; prof=[]
    n=9
    for i in range(n+1):
        t=i/n; z=0.45*s*t; r=0.28*s*math.sqrt(max(0.0,1-(t*0.92)**2.2))+0.012*s*(1 if i%2 else -1)*(1-t)
        prof.append((max(r,0.01),z))
    prof.append((0.0,0.47*s))
    fs=lathe(k,[(r,z+cz+(0.03 if board else 0)) for r,z in prof],center=(cx,cy,0),segs=12,mi=HAY)
    for f in fs: f.smooth=True
    if board: _cyl(k,(cx,cy,cz+0.015),0.33*s,0.33*s,0.03,12,WOOD)
    k.box((cx,cy-0.27*s,cz+0.07*s),(0.09*s,0.03,0.06*s),VOID,bevel=0)
def ind_bee_bench(k):
    """three skeps on a shelf under a little pent roof (2.2 m wide), open to -Y"""
    W=2.2
    for x in(-W/2+0.1,W/2-0.1):
        for y in(-0.3,0.3): k.box((x,y,0.35 if y<0 else 0.8),(0.1,0.1,0.7 if y<0 else 1.6),WOOD,bevel=0.02)
        k.box((x,0,0.3),(0.08,0.66,0.08),WOOD,bevel=0.01)
    k.box((0,0,0.58),(W,0.72,0.06),PLANKS,bevel=0.01)
    for i in range(4): k.box((0,0.33,0.75+i*0.22),(W,0.04,0.2),PLANKS,bevel=0.005)
    ang=0.42; L=math.hypot(1.05,0.45)
    k.box((0,-0.05,1.52),(W+0.3,L,0.07),ROOF,rot=(ang,0,0),bevel=0.02)
    k.box((0,0.36,1.63),(W+0.1,0.1,0.1),WOOD,bevel=0.02)
    for x in(-0.7,0.0,0.7): ind_skep(k,(x,-0.02,0.61),1.0,board=True)
    for (x,y) in((-1.25,-0.5),(1.2,-0.55)): ind_tuft(k,(x,y,0.0),0.5,seed=int(x*10),cell="lavender")
def ind_herb_bundles(k):
    """drying pole on two posts with 6 bundles of herbs hanging head-down"""
    for x in(-1.1,1.1):
        k.box((x,0,1.05),(0.12,0.12,2.1),WOOD,bevel=0.02); k.box((x,0,0.05),(0.3,0.3,0.1),STONE_BLOCK,bevel=0.02)
    ind_rod(k,(-1.25,0,2.0),(1.25,0,2.0),0.045,WOOD,segs=6)
    cells=["lavender","drygrass","leafy","lavender","wheat","leafy"]
    rnd=random.Random(5)
    for i in range(6):
        x=-0.85+i*0.34; L=rnd.uniform(0.5,0.7); top=1.95
        ind_rod(k,(x,0,1.99),(x,0,top-0.12),0.01,HAY,segs=3)
        _cyl(k,(x,0,top-0.15),0.035,0.035,0.06,6,HAY)
        for j in range(3):
            a=j*math.pi/3+rnd.uniform(-.2,.2)
            card(k,(x,0,top-0.15-L/2),(math.cos(a),math.sin(a),0),(0,0,-1),0.32,L,cells[i],flip=j%2==0)
    _cyl(k,(0.2,0.35,0.16),0.25,0.3,0.32,10,WATTLE)
def ind_cauldron(k):
    """iron cauldron on a tripod over a fire (GLOW flames = Fire socket), green brew"""
    ind_lathe(k,[(0.0,0.42),(0.22,0.43),(0.4,0.55),(0.47,0.75),(0.45,0.95),(0.4,1.05),(0.44,1.08),(0.4,1.1)],segs=16,mi=IRON)
    _cyl(k,(0,0,1.02),0.39,0.39,0.02,16,LEAF)
    for s in(-1,1): ring(k,(s*0.47,0,0.98),0.05,0.08,0.03,IRON,n=8,axis="X" if False else "Y")
    for i in range(3):
        a=i*2*math.pi/3+0.3
        ind_beam(k,(math.cos(a)*1.0,math.sin(a)*1.0,0.0),(0,0,2.1),0.07,0.07,WOOD,bevel=0.015)
    ind_rod(k,(0,0,2.05),(0,0,1.1),0.015,IRON,segs=4)
    ind_rod(k,(-0.44,0,1.0),(0,0,1.2),0.012,IRON,segs=4); ind_rod(k,(0.44,0,1.0),(0,0,1.2),0.012,IRON,segs=4)
    # fire: logs, stone ring, flames
    rnd=random.Random(2)
    for i in range(8):
        a=2*math.pi*i/8; rock(k,(math.cos(a)*0.62,math.sin(a)*0.62,0.08),(0.22,0.18,0.16),seed=40+i,mi=STONE_BLOCK,segs=1)
    for i in range(4):
        a=i*math.pi/2+0.4
        ind_log(k,(math.cos(a)*0.5,math.sin(a)*0.5,0.08),(math.cos(a)*0.05,math.sin(a)*0.05,0.2),0.06,seed=i)
    for i in range(5):
        a=2*math.pi*i/5; r=0.12
        lathe(k,[(0.09,0.0),(0.06,0.14),(0.0,0.3+0.08*(i%2))],center=(math.cos(a)*r,math.sin(a)*r,0.12),segs=5,mi=GLOW)
def ind_drying_rack_meat(k):
    """A-frame rack with hams, sausage strings and strips of dried meat"""
    W=2.4
    for x in(-W/2,W/2):
        for s in(-1,1): ind_beam(k,(x,s*0.55,0.0),(x,s*0.06,2.2),0.1,0.1,WOOD,bevel=0.02)
        k.box((x,0,1.0),(0.08,0.9,0.08),WOOD,bevel=0.01)
    ind_rod(k,(-W/2-0.15,0,2.1),(W/2+0.15,0,2.1),0.05,WOOD,segs=6)
    for y in(-0.28,0.28): ind_rod(k,(-W/2,y,1.3),(W/2,y,1.3),0.035,WOOD,segs=6)
    rnd=random.Random(4)
    for i in range(4):   # hams
        x=-0.85+i*0.56
        ind_rod(k,(x,0,2.06),(x,0,1.82),0.012,HAY,segs=3)
        ind_lathe(k,[(0.03,1.8),(0.1,1.72),(0.17,1.52),(0.16,1.38),(0.09,1.3),(0.0,1.28)],c=(x,0,0),segs=10,mi=PIGSKIN if i%2 else HIDE,smooth=True)
    for y in(-0.28,0.28):   # sausages and strips
        for i in range(6):
            x=-1.0+i*0.4+rnd.uniform(-.05,.05)
            if (i+int(y*10))%2:
                for j in range(3): _ico(k,(x,y,1.2-j*0.16),0.06,BREAD,(0.9,0.9,1.6),sub=1)
            else:
                k.box((x,y,1.02),(0.12,0.025,0.5),HIDE,rot=(0,rnd.uniform(-.1,.1),0),bevel=0.01)
    k.box((0,0,0.03),(1.6,0.6,0.06),SOIL,bevel=0.02)
def ind_drying_rack_herbs(k):
    """four-post rack with three slatted trays of herbs and flowers, bundles hanging from the top rail"""
    W,D=1.6,0.8
    for x in(-W/2,W/2):
        for y in(-D/2,D/2): k.box((x,y,0.95),(0.08,0.08,1.9),WOOD,bevel=0.015)
    for zi,z in enumerate((0.45,0.95,1.45)):
        for y in(-D/2,D/2): k.box((0,y,z),(W,0.06,0.06),WOOD,bevel=0.01)
        for i in range(7): k.box((-W/2+0.12+i*(W-0.24)/6,0,z+0.04),(0.06,D-0.04,0.03),WOOD,bevel=0.005)
        rnd=random.Random(zi)
        for i in range(9):
            x=rnd.uniform(-W/2+0.2,W/2-0.2); y=rnd.uniform(-0.25,0.25)
            if (i+zi)%3==0: _ico(k,(x,y,z+0.1),0.1,LEAF,(1.4,1,0.5),sub=1,jit=0.02,seed=i)
            elif (i+zi)%3==1:
                for j in range(4): _ico(k,(x+rnd.uniform(-.08,.08),y+rnd.uniform(-.08,.08),z+0.09),0.045,PINK if zi!=1 else YELLOW,sub=0)
            else: _ico(k,(x,y,z+0.09),0.09,BREAD,(1.5,1,0.4),sub=1,jit=0.02,seed=i+20)
    ind_rod(k,(-W/2,0,1.9),(W/2,0,1.9),0.03,WOOD,segs=6)
    for i in range(4):
        x=-0.55+i*0.37
        for j in range(2):
            a=j*math.pi/2+0.3
            card(k,(x,0,1.62),(math.cos(a),math.sin(a),0),(0,0,-1),0.26,0.5,"lavender" if i%2 else "leafy",flip=j==0)
def ind_dovecote(k):
    """round stone dovecote r 2.0 x 5.0 with 3 rows of nest holes, landing ledges, cone roof r 2.2 x 3.0 and an open lantern (~8.5 m)"""
    R=2.0
    ind_lathe(k,[(R+0.1,-0.6),(R+0.1,0.3),(R+0.02,0.45),(R,1.0),(R,5.0),(R-0.3,5.0)],segs=16,mi=STONE,tile=3.0,around=4)
    ind_lathe(k,[(R+0.18,0.0),(R+0.18,0.4),(R+0.05,0.48)],segs=16,mi=STONE_BLOCK,tile=1.2)
    for z in(2.55,3.45,4.35): ring(k,(0,0,z),R-0.02,R+0.16,0.08,STONE_BLOCK,n=16,axis="Z")
    for row,z in enumerate((2.75,3.65,4.55)):
        for i in range(12):
            a=2*math.pi*(i+0.5*(row%2))/12
            if row==0 and abs(math.sin(a)+1)<0.1: continue
            sub=Kit(); sub.box((0,-0.02,0),(0.17,0.08,0.22),VOID,bevel=0)
            sub.box((0,-0.05,0.14),(0.26,0.08,0.06),STONE_BLOCK,bevel=0.01)
            merge_kit(k,sub,Matrix.Translation((math.cos(a)*R,math.sin(a)*R,z))@Matrix.Rotation(a+math.pi/2,4,"Z"))
    ring(k,(0,0,4.97),R-0.05,R+0.12,0.14,WOOD,n=16,axis="Z")
    ind_cone_roof(k,5.0,R+0.25,7.75,0.55,segs=16)
    # open lantern (glover) on top + finial
    for i in range(4):
        a=i*math.pi/2+math.pi/4
        k.box((math.cos(a)*0.42,math.sin(a)*0.42,7.95),(0.1,0.1,0.55),WOOD,bevel=0.015)
    _cyl(k,(0,0,7.72),0.62,0.62,0.08,12,WOOD)
    ind_cone_roof(k,8.2,0.75,8.95,0.05,segs=12)
    _cyl(k,(0,0,9.05),0.025,0.025,0.4,6,IRON); _ico(k,(0,0,9.28),0.07,BRONZE,sub=1)
    # door + doves
    hw=0.4; y=-R-0.02
    k.quad([(-hw,y,0.45),(hw,y,0.45),(hw,y,1.9),(-hw,y,1.9)],PLANKS,uvs=[(0,0),(0.8,0),(0.8,1.45),(0,1.45)])
    for s in(-1,1): k.box((s*(hw+0.1),y,1.15),(0.2,0.2,1.5),STONE_BLOCK,bevel=0.03)
    k.box((0,y,2.0),(1.2,0.24,0.24),STONE_BLOCK,bevel=0.03)
    k.box((0,y-0.35,0.45),(1.2,0.7,0.1),STONE_BLOCK,bevel=0.03)
    rnd=random.Random(9)
    for i,(a,z) in enumerate(((0.3,3.5),(1.7,4.4),(2.6,2.6),(4.1,3.5),(5.2,4.4),(3.3,5.1))):
        rr=R+0.12 if z<5 else R+0.35
        chicken(k,(math.cos(a)*rr,math.sin(a)*rr,z-0.14 if z<5 else 5.0+0.25),a+math.pi/2,PAPER,seed=i)
    ind_skirt(k,-1.4,1.4,-1.4,1.4)
