# ================================================================ LEATHER AND CLOTH
def ind_ngon(k,pts,mi,two_sided=True,off=(0,0.012,0),uv_scale=1.0):
    """planar polygon (front + back copy), UVs from x/z"""
    fs=[]
    vs=[k.bm.verts.new(p) for p in pts]; f=k.bm.faces.new(vs); f.material_index=mi; fs.append(f)
    if two_sided:
        vb=[k.bm.verts.new(Vector(p)+Vector(off)) for p in pts]; f2=k.bm.faces.new(vb[::-1]); f2.material_index=mi; fs.append(f2)
    k.bm.normal_update()
    for ff in fs:
        for l in ff.loops: l[k.uv].uv=(l.vert.co.x*uv_scale,l.vert.co.z*uv_scale+l.vert.co.y*uv_scale)
    return fs
def ind_pelt_outline(w,h,seed=0,n=28):
    """animal-hide outline in the XZ plane, centred at 0: body with 4 leg lobes, neck and tail"""
    rnd=random.Random(seed); pts=[]
    for i in range(n):
        a=2*math.pi*i/n
        r=1.0+0.28*max(0,math.cos(2*(a-math.pi/4)))**6+0.28*max(0,math.cos(2*(a+math.pi/4)))**6   # legs on the diagonals
        r+=0.18*max(0,math.cos(a-math.pi/2))**12+0.1*max(0,math.cos(a+math.pi/2))**14            # neck (top) / tail (bottom)
        r*=1+rnd.uniform(-0.04,0.04)
        pts.append((math.cos(a)*w/2*r*0.85,math.sin(a)*h/2*r*0.85))
    return pts
def ind_tanning_pit(k):
    """one tanning pit: stone-kerbed 1.2x1.2 pit of tan liquor (HIDE), a hide soaking, pole across. Work socket at -Y"""
    rnd=random.Random(2); A=0.6; T=0.32
    for i,(x,y,sx,sy) in enumerate(((0,-A-T/2,2*A+2*T,T),(0,A+T/2,2*A+2*T,T),(-A-T/2,0,T,2*A),(A+T/2,0,T,2*A))):
        n=3 if sx>sy else 2; L=max(sx,sy)
        for j in range(n):
            c=-L/2+(j+0.5)*L/n
            k.box((x+(c if sx>sy else 0),y+(c if sy>sx else 0),0.14),((L/n-0.03) if sx>sy else sx,(L/n-0.03) if sy>sx else sy,0.3),STONE_BLOCK,
                  rot=(0,0,rnd.uniform(-.03,.03)),bevel=0.04,jitter=0.015,seed=i*5+j)
    k.box((0,0,-0.35),(2*A+0.05,2*A+0.05,0.7),VOID,bevel=0)          # dark pit well (hidden sides)
    k.quad([(-A,-A,0.14),(A,-A,0.14),(A,A,0.14),(-A,A,0.14)],HIDE,uvs=[(0,0),(1,0),(1,1),(0,1)])   # tan liquor
    # a hide soaking, one end pulled up over the kerb
    sub=Kit(); ind_ngon(sub,[(x,z,0) for (x,z) in ind_pelt_outline(0.8,1.0,seed=3)],PIGSKIN,two_sided=True,off=(0,0,-0.01))
    for v in sub.bm.verts: v.co.z+=0.155+min(0.17,max(0.0,v.co.y-0.25)*0.9)
    merge_kit(k,sub,Matrix.Translation((0.05,0.12,0))@Matrix.Rotation(0.15,4,"Z"))
    ind_beam(k,(-1.0,0.2,0.34),(1.05,-0.4,0.34),0.07,0.07,WOOD,bevel=0.01)   # stirring pole
    ind_skirt(k,-A-T,A+T,-A-T,A+T,mi=STONE_BLOCK)
def ind_hide_frame(k):
    """1.4 x 1.8 lashed pole frame with a laced, stretched hide; leans back on two props (faces -Y)"""
    W,H=1.4,1.8; tilt=0.22; z0=0.1
    M=Matrix.Translation((0,0,z0))@Matrix.Rotation(-tilt,4,"X")
    sub=Kit()
    for x in(-W/2,W/2): ind_rod(sub,(x,0,-0.12),(x,0,H+0.15),0.05,WOOD,segs=6)
    for z in(0.0,H): ind_rod(sub,(-W/2-0.15,0,z),(W/2+0.15,0,z),0.045,WOOD,segs=6)
    for x in(-W/2,W/2):
        for z in(0.0,H): _cyl(sub,(x,0,z),0.065,0.065,0.1,6,HAY,rot=Matrix.Rotation(math.pi/2,4,"X"))
    pts=[(x,-0.02,z+H/2) for (x,z) in ind_pelt_outline(W*0.82,H*0.8,seed=5)]
    ind_ngon(sub,pts,HIDE,off=(0,0.015,0),uv_scale=0.8)
    # lacing: from every 3rd outline point to the nearest frame member
    for i,(x,y,z) in enumerate(pts):
        if i%2: continue
        cands=[(-W/2,z),(W/2,z),(x,0.0),(x,H)]
        tx,tz=min(cands,key=lambda c:(c[0]-x)**2+(c[1]-z)**2)
        ind_rod(sub,(x,-0.02,z),(tx,0,tz),0.012,HAY,segs=4)
    merge_kit(k,sub,M)
    # props behind
    for x in(-W/2+0.05,W/2-0.05): ind_beam(k,(x,0.75,0.0),(x,0.28,1.75),0.07,0.07,WOOD,bevel=0.01)
    for x in(-W/2,W/2): rock(k,(x,-0.05,0.08),(0.28,0.24,0.18),seed=int(x*10)+20,mi=STONE_BLOCK,segs=1)
def ind_dye_vat(k):
    """stave vat r 0.6 x 0.8 with iron hoops; dye liquor + draped cloth in CLOTH_A (style {'cloth':'Blue'} recolours it)"""
    R=0.6; H=0.8; n=16; rnd=random.Random(1)
    for i in range(n):
        a=2*math.pi*i/n; hh=H+rnd.uniform(-0.02,0.05)
        k.box((math.cos(a)*R,math.sin(a)*R,hh/2+0.06),(0.09,2*math.pi*R/n+0.01,hh),WOOD,rot=(0,0,a),bevel=0.015)
    _cyl(k,(0,0,0.12),R-0.02,R-0.02,0.1,n,WOOD)
    for z in(0.22,0.72): ring(k,(0,0,z),R+0.035,R+0.075,0.07,IRON,n=n,axis="Z")
    lathe(k,[(R-0.03,0.74),(0.0,0.74)],segs=n,mi=CLOTH_A)
    for f in k.bm.faces:
        if f.material_index==CLOTH_A:
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    # bearers
    for y in(-0.3,0.3): k.box((0,y,0.05),(1.45,0.14,0.1),WOOD,bevel=0.02)
    # cloth draped over the rim, hanging outside (-Y side)
    pts=[(-0.3,0.76),(-0.5,0.87),(-0.62,0.91),(-0.7,0.85),(-0.72,0.6),(-0.7,0.33)]
    for side in(0,1):
        vs=[]
        for j,(y,z) in enumerate(pts):
            for x in(-0.28,0.28):
                vs.append(k.bm.verts.new((x+0.03*math.sin(j*1.3),y+(0.012 if side else 0),z-(0.012 if side else 0))))
        for j in range(len(pts)-1):
            q=[vs[2*j],vs[2*j+1],vs[2*j+3],vs[2*j+2]]
            f=k.bm.faces.new(q if side==0 else q[::-1]); f.material_index=CLOTH_A; f.smooth=True
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z+l.vert.co.y)
    k.bm.normal_update()
    # stirring pole
    ind_beam(k,(0.1,0.1,0.35),(0.55,0.6,1.6),0.05,0.05,WOOD,bevel=0.01)
    # dye splashes on the ground
    for (x,y,r) in((-0.75,-0.35,0.14),(0.5,-0.75,0.1)):
        f=k.bm.faces.new([k.bm.verts.new((x+math.cos(a)*r,y+math.sin(a)*r*0.7,0.008)) for a in [2*math.pi*i/8 for i in range(8)]])
        f.material_index=CLOTH_A
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    k.bm.normal_update()
def ind_strip(k,x,y,top,w,L,mi,seed=0,over=True,sway=0.05):
    """cloth strip folded over a pole at (x,y,top): two double-sided layers, gently waving"""
    rnd=random.Random(seed); nz=6
    layers=[(-0.045,L),(0.045,L*rnd.uniform(0.55,0.8))] if over else [(0.0,L)]
    for (dy,Lx) in layers:
        for side in(0,1):
            vs=[]
            for j in range(nz+1):
                t=j/nz; z=top-t*Lx; dx=sway*math.sin(t*2.6+seed)
                yy=y+dy*(1-0.3*t)+0.04*math.sin(t*3.1+seed*0.7)+(0.008 if side else 0.0)*(1 if dy>=0 else -1)
                vs.append((k.bm.verts.new((x-w/2+dx,yy,z)),k.bm.verts.new((x+w/2+dx,yy,z))))
            for j in range(nz):
                a_,b_=vs[j],vs[j+1]
                q=(a_[0],a_[1],b_[1],b_[0]) if side==0 else (b_[0],b_[1],a_[1],a_[0])
                f=k.bm.faces.new(q); f.material_index=mi; f.smooth=True
                for l in f.loops: l[k.uv].uv=((l.vert.co.x-x)*1.5,l.vert.co.z*1.5)
    k.bm.normal_update()
def ind_cloth_rack(k):
    """dyers' drying rack: 2 posts 3.2 m, poles at 2.2 / 2.6 / 3.0, 7 long strips (CLOTH_A, CLOTH_B, YELLOW, PAPER)"""
    for x in(-1.5,1.5):
        k.box((x,0,1.6),(0.16,0.16,3.2),WOOD,bevel=0.03)
        k.box((x,0,0.06),(0.4,0.4,0.12),STONE_BLOCK,bevel=0.03)
        for s in(-1,1): ind_beam(k,(x,s*0.8,0.0),(x,s*0.08,1.2),0.1,0.1,WOOD,bevel=0.02)
    for i,z in enumerate((2.2,2.6,3.0)):
        y=(-0.25,0.0,0.25)[i]
        for x in(-1.5,1.5): k.box((x,y,z),(0.22,0.24 if y else 0.2,0.1),WOOD,bevel=0.02)
        ind_rod(k,(-1.62,y,z+0.08),(1.62,y,z+0.08),0.04,WOOD,segs=6)
    mats=[CLOTH_A,CLOTH_B,YELLOW,CLOTH_A,PAPER,CLOTH_B,CLOTH_A]
    spots=[(-1.05,0,1.95),(-0.45,0,1.8),(0.2,0,2.0),(0.85,0,1.7),(-0.75,1,2.1),(0.5,1,2.2),(-0.1,2,2.3)]
    for i,((x,pi_,L),mi) in enumerate(zip(spots,mats)):
        z=(2.2,2.6,3.0)[pi_]+0.1; y=(-0.25,0.0,0.25)[pi_]
        ind_strip(k,x,y,z,0.5,L,mi,seed=i)
def ind_loom(k):
    """floor loom 2.0 x 1.3 x 1.8 (weaver faces -Y from the bench), 20 warp threads, CLOTH_A cloth roll"""
    W=1.6; D=1.3
    for x in(-W/2,W/2):
        for y,h in((-D/2,1.05),(D/2,1.8)): k.box((x,y,h/2),(0.12,0.12,h),WOOD,bevel=0.025)
        k.box((x,0,0.2),(0.1,D,0.1),WOOD,bevel=0.02); k.box((x,0,1.0),(0.1,D,0.1),WOOD,bevel=0.02)
        k.box((x,D/2-0.35,1.78),(0.1,0.8,0.1),WOOD,bevel=0.02)
    k.box((0,-D/2,0.98),(W+0.2,0.12,0.1),WOOD,bevel=0.02)                              # breast beam
    _cyl(k,(0,-D/2+0.18,0.62),0.14,0.14,W-0.1,12,CLOTH_A,rot=Matrix.Rotation(math.pi/2,4,"Y"))   # cloth roll
    _cyl(k,(0,D/2,0.85),0.1,0.1,W-0.05,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))         # warp beam
    ind_rod(k,(-W/2-0.1,D/2-0.35,1.8),(W/2+0.1,D/2-0.35,1.8),0.04,WOOD,segs=6)                 # top bar
    # woven cloth from the breast beam toward the reed
    k.quad([(-0.62,-D/2+0.05,1.0),(0.62,-D/2+0.05,1.0),(0.62,-0.15,1.0),(-0.62,-0.15,1.0)],CLOTH_A,uvs=[(0,0),(1.2,0),(1.2,0.5),(0,0.5)])
    # 20 warp threads from the reed to the warp beam
    for i in range(20):
        x=-0.6+i*1.2/19
        ind_beam(k,(x,-0.15,1.0),(x,D/2-0.08,0.93),0.012,0.01,CLOTH_B,bevel=0)
    # heddle frame + beater (reed)
    k.box((0,0.2,1.2),(1.35,0.05,0.05),WOOD,bevel=0.01); k.box((0,0.2,0.82),(1.35,0.05,0.05),WOOD,bevel=0.01)
    for i in range(9): k.box((-0.6+i*0.15,0.2,1.01),(0.012,0.012,0.38),IRON,bevel=0)
    ind_rod(k,(-0.35,D/2-0.35,1.78),(-0.35,0.2,1.23),0.01,HAY,segs=3); ind_rod(k,(0.35,D/2-0.35,1.78),(0.35,0.2,1.23),0.01,HAY,segs=3)
    k.box((0,-0.18,1.12),(1.4,0.08,0.28),WOOD,bevel=0.02)
    for x in(-0.72,0.72): ind_beam(k,(x,-0.18,0.98),(x,0.05,0.2),0.06,0.06,WOOD,bevel=0.01)
    # treadles and bench
    for x in(-0.18,0.18): ind_beam(k,(x,-0.2,0.08),(x,0.55,0.2),0.08,0.03,WOOD,bevel=0.01)
    k.box((0,-D/2-0.55,0.52),(1.2,0.32,0.06),PLANKS,bevel=0.01)
    for x in(-0.5,0.5):
        for y in(-0.1,0.1): k.box((x,-D/2-0.55+y,0.25),(0.06,0.06,0.5),WOOD,bevel=0.01)
    # a shuttle and a spare bobbin
    ind_tbox(k,(0.3,-D/2+0.02,1.07),(0.3,0.06,0.05),WOOD,top=(0.6,1),bevel=0.01)
def ind_spinning_wheel(k):
    """saxony spinning wheel on a slanted bench, distaff with wool. Work socket in front (-Y)"""
    k.box((0,0,0.42),(0.9,0.28,0.07),WOOD,rot=(0,-0.18,0),bevel=0.02)
    for (x,y) in((-0.38,-0.1),(-0.38,0.1),(0.38,0)):
        ind_beam(k,(x,y,0.44+0.07*(-1 if x<0 else 1)),(x*1.25,y*1.8,0.0),0.05,0.05,WOOD,bevel=0.01)
    wc=Vector((-0.22,0,0.95)); r=0.36
    ring(k,tuple(wc),r-0.04,r,0.05,WOOD,n=20,axis="Y")
    for i in range(8):
        a=i*math.pi/4
        ind_beam(k,wc,wc+Vector((math.cos(a)*r*0.95,0,math.sin(a)*r*0.95)),0.025,0.025,WOOD,bevel=0)
    _cyl(k,tuple(wc),0.06,0.06,0.12,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for y in(-0.07,0.07): ind_beam(k,(-0.3,y,0.46),(wc.x,y,wc.z),0.045,0.045,WOOD,bevel=0.01)
    # mother-of-all + flyer
    for x in(0.2,0.38): k.box((x,0,0.72),(0.04,0.04,0.5),WOOD,bevel=0.005)
    k.box((0.29,0,0.95),(0.26,0.07,0.05),WOOD,bevel=0.01)
    _cyl(k,(0.29,0,0.88),0.05,0.05,0.2,8,CLOTH_B,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # treadle + footman
    k.box((-0.05,0,0.05),(0.35,0.18,0.03),WOOD,bevel=0.005)
    ind_beam(k,(-0.05,0.02,0.07),(-0.22,0.05,0.8),0.02,0.02,WOOD,bevel=0)
    # distaff with a wool bundle
    ind_beam(k,(0.35,-0.05,0.47),(0.15,-0.2,1.3),0.03,0.03,WOOD,bevel=0)
    _ico(k,(0.18,-0.18,1.22),0.13,CLOTH_B,(1,1,1.5),sub=2,jit=0.015,seed=4)
def ind_pile_hides(k,size=1):
    """stacks of folded hides on a pallet; bigger piles add pigskins and a draped pelt"""
    rnd=random.Random(size)
    stacks=[(0,0,4)] if size==1 else ([(-0.55,0,5),(0.55,0.05,3)] if size==2 else [(-0.9,0,6),(0.2,0.0,5),(1.2,0.1,3)])
    for (sx,sy,n) in stacks:
        for i in range(n):
            mi=PIGSKIN if (i+size)%4==3 else HIDE
            k.box((sx+rnd.uniform(-.05,.05),sy+rnd.uniform(-.05,.05),0.07+i*0.09),(0.95,0.7,0.08),mi,rot=(0,0,rnd.uniform(-0.15,0.15)),bevel=0.035,segs=2,jitter=0.02,seed=size*20+i)
        top=0.07+n*0.09
        sub=Kit(); ind_ngon(sub,[(x,z,0) for (x,z) in ind_pelt_outline(1.2,0.9,seed=size+sx)],HIDE if size!=2 else PIGSKIN,two_sided=True,off=(0,0,-0.012))
        for v in sub.bm.verts:
            ov=abs(v.co.x)-0.45
            if ov>0: v.co.z-=ov*1.1
        merge_kit(k,sub,Matrix.Translation((sx,sy,top))@Matrix.Rotation(rnd.uniform(-0.3,0.3),4,"Z"))
def ind_pile_wool(k,size=1):
    """CLOTH_B wool bales 0.8x0.6x0.6 tied with rope, plus loose fleeces"""
    rnd=random.Random(size*3)
    spots={1:[(0,0,0,0.1)],2:[(-0.45,0,0,0.05),(0.45,0.05,0,-0.08),(0,0.02,0.58,0.3)],
           3:[(-0.85,0,0,0.04),(0.0,0.03,0,-0.05),(0.85,-0.02,0,0.08),(-0.42,0.0,0.58,0.1),(0.42,0.02,0.58,-0.12)]}[size]
    for (x,y,z,r) in spots:
        k.box((x,y,z+0.3),(0.8,0.6,0.58),CLOTH_B,rot=(0,0,r),bevel=0.12,segs=2,jitter=0.025,seed=int(x*10+z*7)+size)
        for dx in(-0.22,0.22):
            c,s_=math.cos(r),math.sin(r)
            k.box((x+dx*c,y+dx*s_,z+0.3),(0.05,0.63,0.61),BURLAP,rot=(0,0,r),bevel=0.02)
    for i in range(1+size):
        a=rnd.uniform(0,6.28); d=0.9+0.3*size
        _ico(k,(math.cos(a)*d*0.7,-0.55-rnd.uniform(0,0.2),0.12),0.22,CLOTH_B,(1.3,1,0.55),sub=2,jit=0.03,seed=i+size)
