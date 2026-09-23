def ind_flames(k,c,n=3,h=0.4,r=0.1,seed=0):
    """small cluster of GLOW flame cones (toggle 'working' in Unity through the GLOW material)"""
    rnd=random.Random(seed)
    for i in range(n):
        a=2*math.pi*i/n+rnd.uniform(-.3,.3); d=r*0.9 if n>1 else 0
        hh=h*rnd.uniform(0.7,1.1)
        lathe(k,[(r*rnd.uniform(0.8,1.1),0.0),(r*0.65,hh*0.45),(0.0,hh)],center=(c[0]+math.cos(a)*d,c[1]+math.sin(a)*d,c[2]),segs=5,mi=GLOW)
def ind_charcoal_mound(k):
    """charcoal clamp: turf-patched earth dome (r 2.0, h 1.45) on a ring of stacked log ends; 4 shoulder vents + top vent glow.
       Sockets: Smoke at the vents (r 1.0 at 90 deg steps, z~1.2) and the top (0,0,1.5)."""
    vs=ind_heap(k,(0,0,0.26),1.85,1.8,1.2,SOIL,seed=3,sub=3,rough=0.06,peak=0.72,tile=1.6)
    bvh=ind_bvh(k); rnd=random.Random(7)
    # turf sods
    for i in range(15):
        a=rnd.uniform(0,2*math.pi); d=rnd.uniform(0.25,1.55)
        x,y=math.cos(a)*d,math.sin(a)*d; z=ind_drop(bvh,x,y)
        nrm=Vector((x/1.6,y/1.6,1.0)).normalized()
        sub=Kit(); sub.box((0,0,0),(rnd.uniform(0.4,0.75),rnd.uniform(0.35,0.55),0.07),MOSS,bevel=0.03,jitter=0.035,seed=i)
        q=Vector((0,0,1)).rotation_difference(nrm).to_matrix().to_4x4()
        merge_kit(k,sub,Matrix.Translation((x,y,z-0.015))@q@Matrix.Rotation(rnd.uniform(0,6),4,"Z"))
    # vents
    for i in range(5):
        if i<4: a=i*math.pi/2+0.5; x,y=math.cos(a)*0.95,math.sin(a)*0.95
        else: x,y=0.0,0.0
        z=ind_drop(bvh,x,y)
        nrm=Vector((x/1.4,y/1.4,1.0)).normalized(); q=Vector((0,0,1)).rotation_difference(nrm).to_matrix().to_4x4()
        sub=Kit(); r=0.12 if i<4 else 0.2
        ring(sub,(0,0,0.03),r,r+0.09,0.1,SOIL,n=8,axis="Z")
        _cyl(sub,(0,0,-0.01),r,r,0.04,8,VOID)
        _ico(sub,(0,0,-0.01),r*0.6,GLOW,(1,1,0.45),sub=1)
        merge_kit(k,sub,Matrix.Translation((x,y,z))@q)
    # ring of log ends round the foot (the stacked wood inside the clamp)
    for layer,(z,n,r0) in enumerate(((0.13,22,1.98),(0.34,20,1.9))):
        for i in range(n):
            a=2*math.pi*(i+0.5*layer)/n+rnd.uniform(-0.05,0.05); rr=rnd.uniform(0.1,0.13)
            p0=Vector((math.cos(a)*(r0-0.5),math.sin(a)*(r0-0.5),z)); p1=Vector((math.cos(a)*r0,math.sin(a)*r0,z-0.02))
            ind_rod(k,p0,p1,rr,BARK_OAK,segs=6)
            d=(p1-p0).normalized(); q=Vector((0,0,1)).rotation_difference(d).to_matrix().to_4x4()
            cvs=_cyl(k,tuple(p1+d*0.006),rr*0.9,rr*0.9,0.01,6,ENDGRAIN,rot=q)
            ind_box_uv(k,ind_faces(cvs),0.45,(i*0.37%1,layer*0.5))
    # ladder and rake
    for s in(-0.22,0.22): ind_beam(k,(2.35,s+0.4,0.0),(1.0,s+0.3,1.3),0.06,0.07,WOOD,bevel=0.01)
    for j in range(5):
        t=(j+0.6)/6; k.box((2.35-1.35*t,0.4-0.1*t,1.3*t),(0.05,0.5,0.05),WOOD,bevel=0.01)
    ind_beam(k,(-1.4,-2.0,0.02),(-2.2,-0.7,1.35),0.05,0.05,WOOD,bevel=0.01)
    k.box((-1.38,-2.03,0.06),(0.5,0.08,0.06),WOOD,rot=(0,0,-1.0),bevel=0.01)
    ind_skirt(k,-1.6,1.6,-1.6,1.6,mi=SOIL)
def ind_bloomery(k):
    """squat clay shaft furnace (lathe r 1.3 -> 0.55, 3.2 m) on a rubble base: glowing tap arch at -Y (Fire socket),
       flames at the throat (Smoke socket at (0,0,3.3)), clay tuyere at +X for the bellows, charging ladder at +Y"""
    ind_lathe(k,[(1.32,-0.6),(1.32,0.0),(1.3,0.5),(1.24,0.92)],segs=16,mi=STONE,tile=3.0,around=3)
    ind_lathe(k,[(1.22,0.9),(1.2,1.35),(1.05,1.95),(0.8,2.5),(0.6,2.95),(0.66,3.1),(0.7,3.2),(0.52,3.22),(0.46,3.0)],segs=16,mi=CLAY,tile=1.5)
    _cyl(k,(0,0,3.02),0.47,0.47,0.04,12,GLOW)
    ind_flames(k,(0,0,3.03),n=3,h=0.55,r=0.14,seed=2)
    ring(k,(0,0,1.28),1.2,1.26,0.1,IRON,n=16,axis="Z"); ring(k,(0,0,2.28),0.9,0.95,0.1,IRON,n=16,axis="Z")
    rnd=random.Random(4)
    for i in range(7):   # clay daub patches break the smooth silhouette
        a=rnd.uniform(0,2*math.pi); z=rnd.uniform(1.1,2.7); r=1.2-(z-1.0)*0.36
        _ico(k,(math.cos(a)*r,math.sin(a)*r,z),rnd.uniform(0.14,0.22),CLAY,(1.3,1.3,0.55),sub=1,jit=0.02,seed=i)
    for i in range(12):  # base rocks
        a=2*math.pi*(i+0.5)/12
        if abs(a-1.5*math.pi)<0.5: continue
        rock(k,(math.cos(a)*1.3,math.sin(a)*1.3,0.2+0.26*(i%2)),(0.52,0.36,0.38),seed=20+i,rot_z=a,mi=STONE_BLOCK,segs=1)
    # tap arch (front, -Y): recessed glowing mouth
    hw=0.34; zs=0.18; ya=-1.26; hz=0.32
    pts=[(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+hz+math.sin(math.pi*j/8)*hw) for j in range(9)]+[(-hw,zs)]
    f=k.bm.faces.new([k.bm.verts.new((x,ya+0.06,z)) for x,z in pts]); f.material_index=GLOW; k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    k.project([f],GLOW)
    for j in range(len(pts)-1):   # dark reveal around the glow
        (x0,z0),(x1,z1)=pts[j],pts[j+1]
        q=[k.bm.verts.new(p) for p in ((x0,ya-0.02,z0),(x1,ya-0.02,z1),(x1,ya+0.06,z1),(x0,ya+0.06,z0))]
        ff=k.bm.faces.new(q); ff.material_index=VOID
    k.bm.normal_update()
    for j in range(7):
        a=math.pi*(j+0.5)/7
        k.box((math.cos(a)*(hw+0.12),ya-0.07,zs+hz+math.sin(a)*(hw+0.12)),(0.18,0.24,0.24),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.03)
    for s in(-1,1): k.box((s*(hw+0.12),ya-0.07,zs+hz/2),(0.2,0.24,hz+0.1),STONE_BLOCK,bevel=0.03)
    # slag run and bloom lumps in front
    ind_heap(k,(0.05,-1.7,0.0),0.5,0.4,0.13,COAL,seed=9,sub=2)
    k.box((0,-1.45,0.05),(0.18,0.55,0.05),GLOW,bevel=0.02)
    for i in range(4): _ico(k,(0.7+0.2*i,-1.6+0.12*(i%2),0.09),0.11,IRON,(1.2,1,0.8),sub=1,jit=0.02,seed=i)
    # tuyere (clay pipe) at +X where the bellows attach
    _cyl(k,(1.45,0,0.62),0.11,0.14,0.5,8,CLAY,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # charging ladder at the back
    for s in(-0.25,0.25): ind_beam(k,(-0.25+s,2.0,0.0),(-0.1+s,0.75,3.05),0.07,0.07,WOOD,bevel=0.01)
    for j in range(8):
        t=(j+0.6)/9; k.box((-0.18,2.0-1.25*t,3.05*t),(0.55,0.05,0.05),WOOD,bevel=0.01)
    ind_skirt(k,-1.25,1.25,-1.25,1.25)
