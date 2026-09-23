IND_Q_LO=(0.0,0.75,2)     # lower bench: z0, course height, courses  (top 1.5 = 1 LVL)
IND_Q_HI=(1.5,0.6,2)      # upper bench: 1.5 .. 2.7, then a 0.3 soil band to 3.0 (2 LVL)
def ind_qrun(k,x0,x1,yf,bench,seed,depth=0.8,missing=(),pulled=(),drill=True):
    """one bench of cut blocks along X, face toward -Y at y=yf; block tops form the tread"""
    z0,ch,courses=bench; rnd=random.Random(seed)
    for c in range(courses):
        zc=z0+c*ch; xs=[x0]; x=x0
        while True:
            w=rnd.uniform(0.7,1.2)
            if x1-(x+w)<0.45: xs.append(x1); break
            x+=w; xs.append(x)
        for i,(a,b) in enumerate(zip(xs[:-1],xs[1:])):
            if (c,i) in missing: continue
            out=rnd.uniform(-0.12,0.06)
            if (c,i) in pulled: out=-0.34
            hh=ch-0.05-(rnd.uniform(0,0.1) if c==courses-1 else 0)
            k.box(((a+b)/2,yf+out+depth/2,zc+hh/2+0.025),(b-a-0.05,depth,hh),STONE_BLOCK,
                  rot=(rnd.uniform(-.015,.015),rnd.uniform(-.015,.015),rnd.uniform(-.02,.02)),bevel=0.06,segs=1)
            if drill and c==courses-1 and rnd.random()<0.5:
                xm=rnd.uniform(a+0.15,b-0.4)
                for j in range(3): k.box((xm+j*0.12,yf+out-0.004,zc+hh-0.22),(0.035,0.02,0.36),VOID,bevel=0)
def ind_qcores(k,lo_boxes,hi_boxes,band_boxes,seed=0):
    """ROCK cores behind the blocks (dark joints), a soil band 2.7..3.0 with a turf top"""
    for (x0,x1,y0,y1) in lo_boxes: k.box(((x0+x1)/2,(y0+y1)/2,(-0.6+1.45)/2),(x1-x0,y1-y0,2.05),ROCK,bevel=0)
    for (x0,x1,y0,y1) in hi_boxes: k.box(((x0+x1)/2,(y0+y1)/2,(1.45+2.7)/2),(x1-x0,y1-y0,1.25),ROCK,bevel=0)
    for (x0,x1,y0,y1) in band_boxes:
        vs=k.box(((x0+x1)/2,(y0+y1)/2,2.85),(x1-x0,y1-y0,0.3),SOIL,bevel=0)
        grid_cut(k,vs,0.5)
        vv=list({v for v in k.bm.verts if x0-0.01<=v.co.x<=x1+0.01 and y0-0.01<=v.co.y<=y1+0.01 and 2.69<v.co.z<2.71})
        for v in vv:   # ragged bottom edge of the soil band, periodic so modules meet
            v.co.z+=0.05*math.sin(2*math.pi*v.co.x/1.5+1.3)+0.04*math.sin(2*math.pi*v.co.y/1.5+0.4)-0.03
    k.bm.normal_update()
    fs=[f for f in k.bm.faces if f.material_index==SOIL and f.normal.z>0.9 and abs(f.calc_center_median().z-3.0)<0.01]
    k.project(fs,MOSS)
    k.project([f for f in k.bm.faces if f.material_index==SOIL and abs(f.normal.z)<0.5],SOIL)
def ind_qrubble(k,x0,x1,y,seed,n=6):
    rnd=random.Random(seed)
    for i in range(n):
        x=rnd.uniform(x0+0.2,x1-0.2); s=rnd.uniform(0.18,0.45)
        rock(k,(x,y+rnd.uniform(-0.35,0.25),s*0.35),(s*rnd.uniform(1,1.6),s,s*0.8),seed=seed*13+i,mi=STONE_BLOCK if i%3 else ROCK,segs=1)
def ind_qtop(k,pts,seed,edge=()):
    """turf lumps and tufts on the plateau; edge = tufts hanging over the cut edge"""
    rnd=random.Random(seed)
    for i,(x,y) in enumerate(pts):
        if i%3==0: ind_boulder(k,(x,y,2.95),(rnd.uniform(0.6,0.9),rnd.uniform(0.5,0.7),rnd.uniform(0.25,0.4)),seed*7+i,mi=ROCK_MOSSY,sub=1,cuts=4,rot=rnd.uniform(0,6))
        else: ind_tuft(k,(x,y,3.0),rnd.uniform(0.4,0.6),seed=seed+i,cell="grass" if i%4 else "daisy")
    for i,(x,y) in enumerate(edge): ind_tuft(k,(x,y,2.97),rnd.uniform(0.35,0.5),seed=seed*3+i)
def ind_quarry_face(k):
    """contour piece, 3 m, 3.0 high (2 LVL), face -Y: lower face y=-0.8 (z 0..1.5), bench tread z 1.5,
       upper face y=0 (z 1.5..2.7), soil band + turf to z 3.0 behind y=0. Pivot = segment midpoint."""
    ind_qrun(k,-1.5,1.5,-0.8,IND_Q_LO,seed=1,missing=((1,1),),pulled=((0,2),))
    ind_qrun(k,-1.5,1.5,0.0,IND_Q_HI,seed=2,pulled=((1,0),))
    ind_qcores(k,[(-1.5,1.5,-0.5,1.5)],[(-1.5,1.5,0.3,1.5)],[(-1.5,1.5,-0.04,1.5)])
    k.box((0,-0.65,-0.31),(3.0,0.3,0.58),ROCK,bevel=0)
    ind_qrubble(k,-1.5,1.5,-1.2,3)
    rock(k,(0.35,-0.35,1.62),(0.75,0.45,0.32),seed=77,mi=STONE_BLOCK,segs=1)     # loose block on the bench
    rock(k,(-0.9,-1.35,0.2),(0.8,0.5,0.4),seed=78,mi=STONE_BLOCK,segs=1)         # fallen block at the foot
    ind_qtop(k,[(-1.0,1.05),(-0.3,1.2),(0.6,0.9),(1.2,1.25),(0.1,0.6)],5,edge=((-1.2,0.02),(0.4,0.0),(1.1,0.04)))
def ind_quarry_corner(k):
    """outer (convex) corner, faces -X and -Y (like wall corners). Joins Straight at (3,0) rot 0 and (0,3) rot -90"""
    R=Matrix.Rotation(-math.pi/2,4,"Z")
    ind_qrun(k,-0.8,1.5,-0.8,IND_Q_LO,seed=11)
    sub=Kit(); ind_qrun(sub,-1.5,0.0,-0.8,IND_Q_LO,seed=12,pulled=((0,0),)); merge_kit(k,sub,R)
    ind_qrun(k,0.0,1.5,0.0,IND_Q_HI,seed=13)
    sub=Kit(); ind_qrun(sub,-1.5,-0.8,0.0,IND_Q_HI,seed=14,drill=False); merge_kit(k,sub,R)
    ind_qcores(k,[(-0.5,1.5,-0.5,1.5)],[(0.3,1.5,0.3,1.5)],[(-0.04,1.5,-0.04,1.5)])
    k.box((0.35,-0.65,-0.31),(2.3,0.3,0.58),ROCK,bevel=0); k.box((-0.65,0.5,-0.31),(0.3,2.0,0.58),ROCK,bevel=0)
    ind_qrubble(k,-0.8,1.5,-1.2,15,n=4)
    sub=Kit(); ind_qrubble(sub,-1.5,0.0,-1.2,16,n=3); merge_kit(k,sub,R)
    ind_qtop(k,[(1.0,1.1),(0.6,0.9),(0.95,0.4),(0.4,1.3)],17,edge=((0.02,0.5),(0.6,0.02),(0.05,0.05)))
def ind_quarry_innercorner(k):
    """inner (concave) corner: floor at x<-0.8,y<-0.8. Joins Straight at (-3,0) rot 0 and (0,-3) rot -90"""
    R=Matrix.Rotation(-math.pi/2,4,"Z")
    ind_qrun(k,-1.5,-0.8,-0.8,IND_Q_LO,seed=21,drill=False)
    sub=Kit(); ind_qrun(sub,0.8,1.5,-0.8,IND_Q_LO,seed=22,drill=False); merge_kit(k,sub,R)
    ind_qrun(k,-0.8,0.0,-0.8,IND_Q_LO,seed=23,drill=False)      # corner fill (only its tread shows)
    ind_qrun(k,-1.5,0.0,0.0,IND_Q_HI,seed=24)
    sub=Kit(); ind_qrun(sub,0.0,1.5,0.0,IND_Q_HI,seed=25); merge_kit(k,sub,R)
    ind_qrun(k,0.0,0.8,0.0,IND_Q_HI,seed=26,drill=False)
    ind_qcores(k,[(-1.5,1.5,-0.5,1.5),(-0.5,1.5,-1.5,-0.5)],[(-1.5,1.5,0.3,1.5),(0.3,1.5,-1.5,0.3)],
               [(-1.5,1.5,-0.04,1.5),(-0.04,1.5,-1.5,-0.04)])
    k.box((-1.15,-0.65,-0.31),(0.7,0.3,0.58),ROCK,bevel=0); k.box((-0.65,-1.15,-0.31),(0.3,0.7,0.58),ROCK,bevel=0)
    ind_qrubble(k,-1.5,-0.9,-1.2,27,n=3)
    ind_qtop(k,[(-0.8,1.2),(0.4,1.1),(1.2,1.2),(1.1,0.2),(1.2,-0.8),(0.6,0.6)],28,edge=((-1.0,0.02),(0.02,-1.0),(0.03,0.03)))
def ind_quarry_floor(k):
    """3x3 cell of quarried rock floor (top z 0.03) with a block being split by iron wedges"""
    rnd=random.Random(4)
    for i,(x0,x1,y0,y1) in enumerate(((-1.5,0.2,-1.5,-0.1),(0.2,1.5,-1.5,0.4),(-1.5,-0.3,-0.1,1.5),(-0.3,1.5,0.4,1.5))):
        k.box(((x0+x1)/2,(y0+y1)/2,-0.29+0.015*i),(x1-x0-0.05,y1-y0-0.05,0.64),STONE_BLOCK,bevel=0.03)
    k.box((0,0,-0.35),(2.98,2.98,0.5),ROCK,bevel=0)
    for s in(-1,1):
        k.box((0.1+s*0.33,-0.2,0.34),(0.6,0.75,0.62),STONE_BLOCK,rot=(0,s*0.03,0.05),bevel=0.06)
    for j in range(3):
        ind_tbox(k,(0.1,-0.45+j*0.25,0.68),(0.07,0.07,0.16),IRON,top=(2.2,1.2),bevel=0.01)
    ind_beam(k,(0.9,0.55,0.08),(1.35,1.2,0.08),0.06,0.06,WOOD,bevel=0.01)
    k.box((0.86,0.5,0.12),(0.18,0.3,0.16),IRON,rot=(0,0,0.96),bevel=0.02)
    for i in range(14):
        rock(k,(rnd.uniform(-1.3,1.3),rnd.uniform(-1.3,1.3),0.06),(rnd.uniform(0.08,0.2),rnd.uniform(0.07,0.15),0.08),seed=100+i,mi=STONE_BLOCK,segs=1)
    k.box((-0.8,0.8,0.28),(1.1,0.7,0.5),STONE_BLOCK,rot=(0,0,0.3),bevel=0.05)
    for j in range(4): k.box((-1.2+j*0.2*math.cos(0.3),0.68+j*0.2*math.sin(0.3),0.532),(0.045,0.045,0.01),VOID,bevel=0)
    for (x,y) in ((-1.3,-1.2),(1.35,-0.2),(-1.35,0.2)): ind_tuft(k,(x,y,0.02),0.3,seed=int(x*10+y*3))
def ind_banker(k):
    """mason's banker: slab on two ashlar blocks, a column drum being dressed, mallet and chisel"""
    for x in(-0.45,0.45): k.box((x,0,0.3),(0.36,0.62,0.6),ASHLAR,bevel=0.04,segs=1)
    k.box((0,0,0.7),(1.35,0.75,0.2),STONE_BLOCK,bevel=0.04,segs=1)
    # drum lying on its side: dressed round half + still-square half
    sub=Kit()
    ind_lathe(sub,[(0.0,0.0),(0.3,0.0),(0.32,0.03),(0.32,0.34),(0.0,0.34)],segs=16,mi=STONE_BLOCK)
    sub.box((0,0,0.52),(0.64,0.62,0.36),STONE_BLOCK,bevel=0.05,jitter=0.02,seed=3)
    merge_kit(k,sub,Matrix.Translation((-0.25,0,1.12))@Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(0.38,-0.2,0.88),0.08,0.08,0.18,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    ind_beam(k,(0.38,-0.2,0.88),(0.42,0.12,0.84),0.035,0.035,WOOD,bevel=0.005)
    ind_beam(k,(0.2,0.22,0.82),(0.45,0.26,0.82),0.025,0.025,STEEL,bevel=0.005)
    rnd=random.Random(2)
    for i in range(10):
        rock(k,(rnd.uniform(-0.9,0.9),rnd.uniform(-0.7,0.7),0.03),(0.1,0.08,0.06),seed=10+i,mi=STONE_BLOCK,segs=1)
