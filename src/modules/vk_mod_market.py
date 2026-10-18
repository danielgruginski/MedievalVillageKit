# ===================== WS_MARKET: the capital's market square (Saltmere) =====================
# prefix mkt_. Executed last, after vk_helpers and the other modules, in the same namespace: it borrows the town
# agent's arch helpers (twn_arch_fill / twn_arch_soffit / twn_voussoirs) and def_beam from the defence module.
# The market hall reuses the kit's upper timber walls (timber_frame) so it matches the houses round the square; its
# roof is one light hipped roof on the kit's profile (roof_z) instead of the dense Roof_Hip / Roof_Mid tiles.

MKT_GH=3.8              # market hall: arcade storey height (its wall top; the timber storey stands on it)
MKT_A=4.5               # half length (end wall lines at x = +-4.5, 3 cells); the depth is the kit's 6 m (2 x HALF)
MKT_T=0.3               # half thickness of the arcade walls
MKT_HW=1.05             # long-side arch half width (2.1 m openings; spring MKT_SP, crown 3.35)
MKT_SP=2.3

def mkt_put(k,fn,x,y,z,rot=0.0):
    """build fn's geometry (a kit piece builder) into k at (x,y,z), turned rot degrees about Z"""
    sub=Kit(); fn(sub)
    merge_kit(k,sub,Matrix.Translation((x,y,z))@Matrix.Rotation(math.radians(rot),4,"Z"))

def mkt_limb(k,a,b,r0,r1,mi,segs=8):
    """tapered round rod from a (radius r0) to b (radius r1)"""
    a=Vector(a); b=Vector(b); d=b-a
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    return _cyl(k,tuple((a+b)/2),r0,r1,d.length,segs,mi,rot=q)

def mkt_ridge_beam(k,a,b,s=0.28,mi=ROOF):
    """square ridge tile run from a to b, turned 45 deg about its axis (a diamond, like the kit's ridge)"""
    a=Vector(a); b=Vector(b); X=(b-a).normalized()
    Y=Vector((0,0,1)).cross(X).normalized(); Z=X.cross(Y)
    def_beam(k,a,b,s,s,mi,bevel=0.08,up=tuple((Z+Y).normalized()))

# ================================================================ MARKET HALL
def mkt_voussoirs(k,cx,hw,sp,y0,y1,n=9,th=0.26,out=0.06,seed=0):
    """plain arch stones round a semicircular head (centre cx), protruding 'out' in front of y0: unbevelled, 12 tris a
       stone (the town agent's bevelled twn_voussoirs cost 44), the keystone a little proud"""
    rnd=random.Random(seed); r=hw+th/2; L=math.pi*r/n
    for i in range(n):
        a=math.pi*(i+0.5)/n; ks=(i==n//2); h=th*(1.25 if ks else 1.0)+rnd.uniform(-0.02,0.02)
        k.box((cx+math.cos(a)*r,(y0+y1)/2-out/2,sp+math.sin(a)*r+(h-th)/2*math.sin(a)),
              (L*(1.08 if ks else 0.95),(y1-y0)+out,h),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0)

def mkt_arcade(k,L,d,centres,hw,ends=True,seed=0):
    """open arcade along x (-L/2..L/2) on the wall line y=-d: ashlar piers, round arches with voussoirs, imposts and
       pier bases. ends=False: the wall runs between the long sides' corner piers, its end bases stop short of theirs"""
    y0,y1=-d-MKT_T,-d+MKT_T; top=MKT_GH; sp=MKT_SP if hw>=MKT_HW else MKT_SP+MKT_HW-hw
    edges=[-L/2]+[e for c in centres for e in (c-hw,c+hw)]+[L/2]
    segs=list(zip(edges[0::2],edges[1::2]))
    for i,(x0,x1) in enumerate(segs):
        k.box(((x0+x1)/2,-d,(top-0.6)/2),(x1-x0,2*MKT_T,top+0.6),ASHLAR,bevel=0)              # pier, footing to -0.6
        e0=0.06 if (ends or i>0) else -0.06; e1=0.06 if (ends or i<len(segs)-1) else -0.06
        k.box(((x0-e0+x1+e1)/2,-d,0.16),(x1-x0+e0+e1,2*MKT_T+0.12,0.32),STONE_BLOCK,bevel=0.04)  # pier base
    for i,c in enumerate(centres):
        twn_arch_fill(k,c,hw,sp,top,y0,y1,ASHLAR,n=8)
        twn_arch_soffit(k,c,hw,sp,y0,y1,ASHLAR,n=10)
        mkt_voussoirs(k,c,hw,sp,y0,y1,seed=seed*5+i)
        for s in(-1,1): k.box((c+s*(hw+0.04),-d,sp-0.07),(0.3,2*MKT_T+0.1,0.14),STONE_BLOCK,bevel=0.03)   # imposts

def mkt_roof(k,A):
    """hipped tile roof over a 2A x 6 m block, wall top at z=0: the kit's profile (roof_z: 52 deg pitch, 26 deg
       bell-cast kick, planar between the ridge, wall-line and eave rows), hips at 45 deg in plan, WOOD underside and
       fascia, diamond ridge and hip tiles, finials at the hip apexes"""
    a=A-HALF; ts=(0.0,HALF/2,HALF,EAVE); T=TILE[ROOF]; W=TILE[WOOD]; drop=RT*1.2
    def slope(sub,n,pt,along):
        top=[];bot=[]
        for t in ts:
            p0,p1=pt(t,0.0),pt(t,1.0)
            if (Vector(p0)-Vector(p1)).length<1e-6:     # the hip apex row collapses to one point
                v=sub.bm.verts.new((*p0,roof_z(t))); w=sub.bm.verts.new((*p0,roof_z(t)-drop))
                top.append([v]*(n+1)); bot.append([w]*(n+1))
            else:
                top.append([sub.bm.verts.new((*pt(t,j/n),roof_z(t))) for j in range(n+1)])
                bot.append([sub.bm.verts.new((*pt(t,j/n),roof_z(t)-drop)) for j in range(n+1)])
        fs=[]
        for i in range(len(ts)-1):
            for j in range(n):
                for rows,mi in ((top,ROOF),(bot,WOOD)):
                    q=list(dict.fromkeys((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j])))
                    f=sub.bm.faces.new(q); f.material_index=mi; fs.append(f)
        for j in range(n):   # eave fascia
            f=sub.bm.faces.new((top[-1][j],top[-1][j+1],bot[-1][j+1],bot[-1][j])); f.material_index=WOOD; fs.append(f)
        sub.bm.normal_update()
        for f in fs:
            c=f.calc_center_median()
            if f.material_index==ROOF:
                if f.normal.z<0: f.normal_flip()
                for l in f.loops:
                    p=l.vert.co; t=max(0.0,min(EAVE,abs(p.y) if along=="x" else abs(p.x)-a))
                    l[sub.uv].uv=((p.x if along=="x" else p.y)/T,slope_dist(t)/T)
            else:
                if abs(f.normal.z)>0.2:
                    if f.normal.z>0: f.normal_flip()
                elif f.normal.dot(Vector((c.x,c.y,0)))<0: f.normal_flip()
                for l in f.loops:
                    p=l.vert.co; l[sub.uv].uv=((p.x+p.y)/W,(p.z if abs(f.normal.z)<0.2 else p.y)/W)
    def half(sub):
        slope(sub,8,lambda t,u: (-(a+t)+2*(a+t)*u,-t),"x")                 # long side (-y)
        slope(sub,6,lambda t,u: (a+t,-t+2*t*u),"y")                        # hipped end (+x)
        for s in(-1,1):                                                    # hip tiles: apex -> wall corner -> eave
            p0=Vector((a,0,RIDGE+0.05)); p1=Vector((a+HALF,s*HALF,roof_z(HALF)+0.05))
            p2=Vector((a+EAVE-0.12,s*(EAVE-0.12),roof_z(EAVE-0.12)+0.05))
            mkt_ridge_beam(sub,p0,p1); mkt_ridge_beam(sub,p1,p2)
        _ico(sub,(a,0,RIDGE+0.14),0.22,ROOF,sub=1)
        n=max(1,int(round(a/0.75)))
        for i in range(n):                                                 # half the ridge
            x0=a*i/n; x1=a*(i+1)/n
            sub.box(((x0+x1)/2,0,RIDGE+0.1),(x1-x0+0.04,0.36,0.36),ROOF,rot=(math.pi/4,0,0),bevel=0.1,segs=2)
    for r in(0,180): mkt_put(k,half,0,0,0,r)

def mkt_lantern(k):
    """the hall's clock lantern astride the ridge (wall top at z=0): plastered base with four clock faces, an open
       belfry with a bell, a tiled spire, ball and weathervane"""
    B=1.4; zb=RIDGE-1.1; zt=RIDGE+0.95; zc=RIDGE+0.45
    k.box((0,0,(zb+zt)/2),(B,B,zt-zb),PLASTER,bevel=0)
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.05),sy*(B/2-0.05),(zb+zt)/2),(0.18,0.18,zt-zb),WOOD,bevel=0.03)
    k.box((0,0,zt+0.07),(B+0.3,B+0.3,0.14),WOOD,bevel=0.04)
    for a in range(4):
        sub=Kit(); clock_face(sub,(0,-B/2-0.03,zc),0.4)
        _cyl(sub,(0,-B/2-0.005,zc),0.47,0.47,0.04,16,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
        merge_kit(k,sub,Matrix.Rotation(a*math.pi/2,4,"Z"))
    zb2=zt+0.14; hb=1.0
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.1),sy*(B/2-0.1),zb2+hb/2),(0.16,0.16,hb),WOOD,bevel=0.03)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2-0.1),zb2+hb-0.07),(B,0.14,0.14),WOOD,bevel=0.03)
        k.box((sgn*(B/2-0.1),0,zb2+hb-0.07),(0.14,B-0.28,0.14),WOOD,bevel=0.03)
        k.box((0,sgn*(B/2-0.1),zb2+0.3),(B-0.36,0.08,0.07),WOOD,bevel=0.02)                     # rails
        k.box((sgn*(B/2-0.1),0,zb2+0.3),(0.08,B-0.36,0.07),WOOD,bevel=0.02)
    k.box((0,0,zb2+0.02),(B-0.1,B-0.1,0.04),PLANKS,bevel=0)
    k.box((0,0,zb2+hb-0.22),(0.9,0.1,0.1),WOOD,bevel=0.02)                                     # headstock
    _cyl(k,(0,0,zb2+hb-0.45),0.27,0.12,0.36,12,BRONZE); _cyl(k,(0,0,zb2+hb-0.65),0.29,0.29,0.05,12,BRONZE)
    zr=zb2+hb
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(B+0.6)/math.sqrt(2),radius2=0.03,depth=1.7)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zr+0.85))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.8)
    k.box((0,0,zr+1.95),(0.07,0.07,0.75),BRONZE,bevel=0.02)
    _ico(k,(0,0,zr+1.8),0.11,BRONZE,sub=1)
    k.box((0,0,zr+2.2),(0.75,0.035,0.035),IRON,bevel=0); k.box((0.34,0,zr+2.2),(0.11,0.03,0.15),IRON,rot=(0,0.785,0),bevel=0)
    k.box((-0.35,0,zr+2.23),(0.02,0.22,0.13),IRON,bevel=0)

def mkt_corner_post(k):
    """the upper storey's corner post (Corner_Timber without its dragon-beam bracket: here it stands on stone)"""
    k.box((-0.2,-0.2,0.15),(0.66,0.66,0.3),WOOD,bevel=0.04)
    k.box((-0.26,-0.26,H2/2),(0.34,0.34,H2),WOOD,bevel=0.05,segs=2)
    k.box((-0.2,-0.2,H2-0.1),(0.62,0.62,0.22),WOOD,bevel=0.04)

def mkt_market_hall(k):
    """Saltmere's covered market: an open ashlar arcade (three round arches on each long side, two on each end, a
       flagged floor one step up, a planked ceiling on beams, two lanterns) under a timber-framed upper storey (the
       kit's own walls), a hipped tile roof and a clock lantern with a bell. Wall lines 9 x 6 m, front -Y."""
    A=MKT_A; D=HALF; GH=MKT_GH
    k.box((0,0,-0.24),(2*A+0.9,2*D+0.9,0.72),ASHLAR,bevel=0.04)                 # floor: top 0.12, footing to -0.6
    for s,r in ((-1,0),(1,180)):
        mkt_put(k,lambda sb: mkt_arcade(sb,2*A+2*MKT_T,D,(-3.0,0.0,3.0),MKT_HW,True,seed=2+s),0,0,0,r)
        mkt_put(k,lambda sb: mkt_arcade(sb,2*D-2*MKT_T,A,(-1.45,1.45),1.0,False,seed=6+s),0,0,0,r-90)
    zc=GH-0.1                                                                     # string course, top GH+0.02
    for s in(-1,1):
        k.box((0,s*D,zc),(2*A+0.8,0.8,0.24),STONE_BLOCK,bevel=0.04)
        k.box((s*A,0,zc),(0.8,2*D-0.8,0.24),STONE_BLOCK,bevel=0.04)
    k.box((0,0,GH-0.1),(2*A-2*MKT_T,2*D-2*MKT_T,0.2),PLANKS,bevel=0)            # ceiling
    for x in(-1.5,1.5): k.box((x,0,GH-0.34),(0.3,2*D-0.6,0.28),WOOD,bevel=0.03)
    k.box((0,0,GH-0.3),(2*A-0.6,0.24,0.2),WOOD,bevel=0.03)
    for i in range(13):
        x=-3.6+i*0.6
        if abs(abs(x)-1.5)>0.2: k.box((x,0,GH-0.26),(0.12,2*D-0.6,0.12),WOOD,bevel=0)
    for x in(-1.5,1.5):                                                           # hanging lanterns
        k.box((x,0,GH-0.74),(0.02,0.02,0.5),IRON,bevel=0)
        k.box((x,0,GH-1.1),(0.24,0.24,0.3),GLOW,bevel=0.03)
        k.box((x,0,GH-0.92),(0.32,0.32,0.06),IRON,bevel=0.015); k.box((x,0,GH-1.27),(0.28,0.28,0.05),IRON,bevel=0.015)
    W=lambda sb: timber_frame(sb,True); P_=lambda sb: timber_frame(sb); X=lambda sb: timber_frame(sb,False,"X")
    for x in(-3.0,0.0,3.0): mkt_put(k,W,x,-D,GH,0)
    for x,f in ((-3.0,W),(0.0,P_),(3.0,W)): mkt_put(k,f,x,D,GH,180)
    mkt_put(k,X,-A,-1.5,GH,-90); mkt_put(k,W,-A,1.5,GH,-90)
    mkt_put(k,W,A,-1.5,GH,90); mkt_put(k,X,A,1.5,GH,90)
    for (x,y,r) in ((-A,-D,0),(A,-D,90),(A,D,180),(-A,D,-90)): mkt_put(k,mkt_corner_post,x,y,GH,r)
    mkt_put(k,lambda sb: mkt_roof(sb,A),0,0,GH+H2,0)
    mkt_put(k,mkt_lantern,0,0,GH+H2,0)

# ================================================================ MONUMENT
def mkt_statue_king(k):
    """bronze king, soles at z=0, 2.25 m to the crown's points: gown, cloak, both hands on the pommel of a sword
       standing point down in front of him (the caller squeezes y)"""
    B=BRONZE
    lathe(k,[(0.37,0.0),(0.39,0.05),(0.35,0.45),(0.29,0.9),(0.25,1.1)],segs=12,mi=B)                 # gown
    lathe(k,[(0.25,1.1),(0.27,1.32),(0.29,1.56),(0.27,1.72),(0.13,1.84),(0.07,1.9)],segs=12,mi=B)     # body to the neck
    _cyl(k,(0,0,1.1),0.265,0.265,0.06,12,B)                                                          # belt
    for s in(-1,1):
        k.box((s*0.12,-0.43,0.04),(0.1,0.16,0.08),B,bevel=0.03)                                      # toes
        _ico(k,(s*0.25,0,1.7),0.11,B,scale=(1.1,1,0.8),sub=1)                                        # shoulders
        sh=(s*0.27,0.0,1.69); el=(s*0.3,-0.13,1.37); ha=(s*0.05,-0.37,1.21)
        mkt_limb(k,sh,el,0.085,0.075,B); mkt_limb(k,el,ha,0.07,0.055,B); _ico(k,el,0.074,B,sub=1)
        _ico(k,(s*0.045,-0.4,1.2),0.055,B,scale=(1,1.2,0.9),sub=1)                                 # hands
    _ico(k,(0,0.01,2.0),0.125,B,scale=(0.92,1,1.12),sub=2)                                         # head
    mkt_limb(k,(0,-0.06,1.95),(0,-0.1,1.8),0.08,0.015,B,6)                                         # beard
    _cyl(k,(0,0.01,2.12),0.125,0.14,0.07,10,B)                                                    # crown
    for i in range(5):
        a=-math.pi/2+2*math.pi*i/5
        mkt_limb(k,(math.cos(a)*0.13,0.01+math.sin(a)*0.13,2.15),(math.cos(a)*0.145,0.01+math.sin(a)*0.145,2.25),0.03,0.006,B,4)
    rows=[(1.8,0.31),(1.5,0.37),(0.9,0.45),(0.1,0.52)]; n=8                                      # cloak (two skins)
    for off,flip in ((0.0,False),(-0.03,True)):
        g=[[k.bm.verts.new((math.cos(a)*(r+off),0.02+math.sin(a)*(r+off),z))
            for a in [math.radians(-15+210*j/n) for j in range(n+1)]] for z,r in rows]
        for i in range(len(rows)-1):
            for j in range(n):
                q=(g[i][j],g[i+1][j],g[i+1][j+1],g[i][j+1])
                f=k.bm.faces.new(q[::-1] if flip else q); f.material_index=B
    k.bm.normal_update()
    for f in k.bm.faces: f.smooth=True     # cast bronze (smooth BRONZE survives the rebuild); the sword stays crisp
    k.box((0,-0.4,0.57),(0.07,0.02,1.06),B,bevel=0.005)                                           # blade
    k.box((0,-0.4,1.12),(0.36,0.05,0.05),B,bevel=0.01)                                            # cross-guard
    _cyl(k,(0,-0.4,1.2),0.025,0.025,0.14,6,B); _ico(k,(0,-0.4,1.3),0.045,B,sub=1)

def mkt_monument(k):
    """the founder's monument: three square steps, an ashlar pedestal with four bronze plaques and a laurel, a bronze
       king with his sword point down; flowers left on the steps. 5.4 m, front -Y"""
    for i,w in enumerate((3.4,2.8,2.2)):
        if i==0: k.box((0,0,-0.175),(w,w,0.85),STONE_BLOCK,bevel=0.03)                          # bottom step + footing
        else: k.box((0,0,0.25*i+0.125),(w,w,0.25),STONE_BLOCK,bevel=0.03)
    k.box((0,0,0.87),(1.7,1.7,0.24),ASHLAR,bevel=0.05,segs=2)                                    # base moulding
    k.box((0,0,1.79),(1.4,1.4,1.6),ASHLAR,bevel=0.03)                                            # die
    k.box((0,0,2.68),(1.75,1.75,0.18),ASHLAR,bevel=0.05,segs=2)                                  # cornice
    k.box((0,0,2.82),(1.45,1.45,0.1),ASHLAR,bevel=0.03)
    for a in range(4):
        sub=Kit(); sub.box((0,-0.715,1.85),(0.8,0.04,0.55),BRONZE,bevel=0.01)
        if a==0: ring(sub,(0,-0.735,2.33),0.12,0.18,0.04,BRONZE,n=14,axis="Y")
        merge_kit(k,sub,Matrix.Rotation(a*math.pi/2,4,"Z"))
    k.box((0,0,2.9),(0.95,0.95,0.06),BRONZE,bevel=0.02)
    sub=Kit(); mkt_statue_king(sub)
    merge_kit(k,sub,Matrix.Translation((0,0,2.93))@Matrix.Diagonal((1.1,0.88,1.1,1.0)))
    rnd=random.Random(17)
    for x,y,z in ((-0.6,-1.25,0.5),(0.75,-1.22,0.5),(-1.45,-1.55,0.25),(1.2,-1.6,0.25)):         # posies on the steps
        for j in range(3):
            _ico(k,(x+rnd.uniform(-0.1,0.1),y+rnd.uniform(-0.06,0.06),z+0.06),0.07,(PINK,YELLOW,PINK)[j],sub=1)
        _ico(k,(x+0.05,y+0.08,z+0.04),0.08,LEAF,scale=(1.4,1,0.6),sub=1)

# ================================================================ WEIGH BEAM
def mkt_weigh_beam(k):
    """the town's weighing beam (the tron): a gallows frame under a little tiled hood, a 1.9 m balance on an iron hook,
       chained pans (a wool sack weighed against iron weights), the weigher's bench with his ledger, sacks waiting"""
    for x in(-1.5,1.5):
        k.box((x,0,1.15),(0.2,0.2,3.5),WOOD,bevel=0.03)                                           # posts, sunk to -0.6
        k.box((x,0,0.1),(0.44,0.44,0.2),STONE_BLOCK,bevel=0.04)
        def_beam(k,(x,0,2.2),(x*0.6,0,2.87),0.12,0.12,WOOD)
    k.box((0,0,2.98),(3.4,0.24,0.24),WOOD,bevel=0.03)
    for x in(-1.5,1.5): k.box((x,0,3.29),(0.1,0.1,0.38),WOOD,bevel=0.02)
    k.box((0,0,3.47),(3.8,0.1,0.1),WOOD,bevel=0.02)
    for s in(-1,1): k.box((0,s*0.26,3.3),(3.8,0.62,0.06),ROOF,rot=(-s*0.6,0,0),bevel=0.015)
    k.box((0,0,2.72),(0.04,0.04,0.28),IRON,bevel=0)
    ring(k,(0,0,2.55),0.03,0.06,0.03,IRON,n=8,axis="Y")
    R=Matrix.Rotation(math.radians(5),4,"Y"); piv=Vector((0,0,2.47))                            # the +x end is down
    sub=Kit(); sub.box((0,0,0),(1.9,0.09,0.14),WOOD,bevel=0.02); sub.box((0,0,0.06),(0.14,0.12,0.22),IRON,bevel=0.01)
    for s in(-1,1): sub.box((s*0.9,0,0),(0.1,0.12,0.18),IRON,bevel=0.01)
    merge_kit(k,sub,Matrix.Translation(piv)@R)
    for s in(-1,1):
        end=piv+R.to_3x3()@Vector((s*0.88,0,-0.08)); pan=Vector((end.x,0,end.z-1.45))
        for i in range(3):
            a=2*math.pi*i/3+0.5
            def_beam(k,end,pan+Vector((math.cos(a)*0.29,math.sin(a)*0.29,0.06)),0.014,0.014,IRON,bevel=0)
        _cyl(k,tuple(pan),0.26,0.33,0.08,12,IRON)
        if s>0:                                                                                    # a wool sack
            sub=Kit(); _stall_sack(sub,0,0,BURLAP,0.85,seed=3); merge_kit(k,sub,Matrix.Translation((pan.x,0,pan.z+0.04)))
        else:
            for j,(r,h) in enumerate(((0.13,0.1),(0.11,0.09),(0.08,0.08))):
                _cyl(k,(pan.x,0,pan.z+0.04+0.1*j+h/2),r,r*0.92,h,10,IRON)
    k.box((0,1.05,0.76),(1.4,0.55,0.07),PLANKS,bevel=0.02)                                        # the weigher's bench
    for sx in(-0.6,0.6):
        for sy in(0.85,1.25): k.box((sx,sy,0.36),(0.07,0.07,0.72),WOOD,bevel=0.01)
    _book(k,-0.3,1.05,0.795,0.38,0.27,0.05,CLOTH_A,0.12)
    for j,(r,h) in enumerate(((0.07,0.06),(0.055,0.05),(0.04,0.04))):
        _cyl(k,(0.35,1.0,0.795+0.055*j+h/2),r,r,h,8,IRON)
    _cyl(k,(0.1,1.15,0.84),0.035,0.03,0.07,8,CLAY)
    for i,(x,y) in enumerate(((-2.0,0.45),(-2.1,-0.2),(-1.95,1.05))):                              # sacks waiting
        _stall_sack(k,x,y,BURLAP,1.0,seed=10+i)

# ================================================================ PENS
def mkt_hurdle(k,a,b,h=1.0):
    """one wattle hurdle from a to b ((x,y) on the ground): woven panel, two end stakes, a top binding rod"""
    a=Vector((a[0],a[1],0)); b=Vector((b[0],b[1],0)); d=b-a; L=d.length
    sub=Kit()
    sub.box((0,0,0.12+(h-0.12)/2),(L-0.08,0.06,h-0.12),WATTLE,bevel=0.01)
    for s in(-1,1): _cyl(sub,(s*(L/2-0.03),0,(h+0.12-0.4)/2),0.035,0.03,h+0.52,6,WOOD)          # stakes, -0.4..h+0.12
    _cyl(sub,(0,0,h+0.01),0.03,0.03,L-0.1,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    merge_kit(k,sub,Matrix.Translation((a+b)/2)@Matrix.Rotation(math.atan2(d.y,d.x),4,"Z"))

def mkt_hurdle_piece(k): mkt_hurdle(k,(-1.0,0.0),(1.0,0.0))

def mkt_pen(k):
    """a 4 x 3 m livestock pen of hurdles for the market's sheep and pigs: the gate hurdle swung open at the front
       right, straw down, a water trough, a chalked tally board on the front"""
    X,Y=2.0,1.5
    mkt_hurdle(k,(-X,Y),(0,Y)); mkt_hurdle(k,(0,Y),(X,Y))
    mkt_hurdle(k,(-X,-Y),(-X,Y)); mkt_hurdle(k,(X,-Y),(X,Y))
    mkt_hurdle(k,(-X,-Y),(0,-Y))
    g=math.radians(40); mkt_hurdle(k,(X,-Y),(X-2.0*math.cos(g),-Y-2.0*math.sin(g)))
    k.box((0,0,0.015),(2*X-0.2,2*Y-0.2,0.03),HAY,bevel=0.01)
    rnd=random.Random(23)
    for i in range(5):
        _ico(k,(rnd.uniform(-1.5,1.5),rnd.uniform(-1.0,1.0),0.04),rnd.uniform(0.25,0.4),HAY,scale=(1.3,1,0.3),sub=1,
             jit=0.03,seed=30+i)
    tx,ty=-1.1,1.05                                                                               # trough
    k.box((tx,ty,0.08),(1.3,0.5,0.08),WOOD,bevel=0.02)
    for s in(-1,1):
        k.box((tx,ty+s*0.22,0.2),(1.3,0.06,0.32),WOOD,bevel=0.015)
        k.box((tx+s*0.62,ty,0.2),(0.06,0.38,0.32),WOOD,bevel=0.015)
    k.quad([(tx-0.59,ty-0.19,0.3),(tx+0.59,ty-0.19,0.3),(tx+0.59,ty+0.19,0.3),(tx-0.59,ty+0.19,0.3)],WATER,
           uvs=[(0,0),(1.2,0),(1.2,0.4),(0,0.4)])
    k.box((-1.0,-Y-0.06,0.78),(0.42,0.03,0.3),WOOD,bevel=0.01)                                  # tally board
    k.box((-1.0,-Y-0.08,0.78),(0.34,0.01,0.22),PAPER,bevel=0)

# ================================================================ CRIER'S STAND
def mkt_crier_stand(k):
    """the town crier's stand: a 1.7 m plank platform 1.1 m up on four posts, steps at the back, rails on three sides,
       the city's cloth on the front rail, a hand bell on an iron arm, a rolled proclamation and a notice. Front -Y"""
    Z=1.1; p=0.75
    k.box((0,0,Z-0.05),(1.7,1.7,0.1),PLANKS,bevel=0.02)
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*p,sy*p,(Z+1.0-0.6)/2),(0.12,0.12,Z+1.6),WOOD,bevel=0.02)        # posts, -0.6..2.1
    k.box((0,-p-0.07,Z-0.2),(1.7,0.04,0.3),PLANKS,bevel=0.01)                                     # skirt boards
    for sx in(-1,1): k.box((sx*(p+0.07),0,Z-0.2),(0.04,1.7,0.3),PLANKS,bevel=0.01)
    for sx in(-1,1):
        def_beam(k,(sx*p,-p+0.08,0.25),(sx*p,p-0.08,Z-0.2),0.08,0.08,WOOD)                         # side braces
    for z in(Z+0.98,Z+0.5):
        k.box((0,-p,z),(1.5-0.02,0.08,0.08),WOOD,bevel=0.02)
        for sx in(-1,1): k.box((sx*p,0,z),(0.08,1.5-0.02,0.08),WOOD,bevel=0.02)
    for i in range(4):                                                                           # steps at the back
        z=0.22*(i+1); y=1.75-0.25*i
        k.box((0,y,z-0.025),(0.8,0.26,0.05),PLANKS,bevel=0.01)
    for sx in(-1,1): def_beam(k,(sx*0.43,1.95,0.0),(sx*0.43,p+0.05,Z-0.1),0.06,0.18,WOOD)
    k.box((0,-p-0.06,Z+1.01),(1.12,0.2,0.04),CLOTH_A,bevel=0.01)                                  # the city's cloth,
    k.box((0,-p-0.16,Z+0.38),(1.1,0.03,1.26),CLOTH_A,bevel=0.005)                                 # over the front rail
    k.box((0,-p-0.165,Z-0.2),(1.1,0.035,0.1),YELLOW,bevel=0.005)
    _cyl(k,(0,-p-0.185,Z+0.5),0.17,0.17,0.012,12,YELLOW,rot=Matrix.Rotation(math.pi/2,4,"X"))
    k.box((p+0.2,-p,Z+0.96),(0.38,0.04,0.04),IRON,bevel=0)                                        # bell arm + bell
    _cyl(k,(p+0.33,-p,Z+0.8),0.11,0.05,0.16,8,BRONZE); _cyl(k,(p+0.33,-p,Z+0.93),0.02,0.02,0.1,6,WOOD)
    _cyl(k,(-0.35,-p,Z+1.07),0.035,0.035,0.38,8,PAPER,rot=Matrix.Rotation(math.pi/2,4,"Y"))      # rolled proclamation
    k.box((-p,-p-0.07,Z+0.25),(0.1,0.02,0.32),PAPER,bevel=0)                                      # notice on the post

# ================================================================ SPECS
WS_SPECS=[
    ("SM_VK_MarketHall",mkt_market_hall,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Monument",mkt_monument,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_WeighBeam",mkt_weigh_beam,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Hurdle",mkt_hurdle_piece,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_Pen",mkt_pen,dict(wobble=False,grime=True)),
    ("SM_VK_Prop_CrierStand",mkt_crier_stand,dict(wobble=False,grime=True)),
]
EXTRA_SPECS+=WS_SPECS
