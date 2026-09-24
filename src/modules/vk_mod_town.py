# ===================== WS_TOWN: town-tier pieces (spec M4) =====================
# agent "town", prefix twn_. Executed after vk_helpers in the same namespace.
# Upper-floor families (StoneUp / PlasterUp) use a FLAT wobble (applied here, finish wobble=False)
# so they meet the fade-wobbled 3.0 m ground walls exactly at z=3.0 and stack on each other.

TWN_SF=-0.25          # stone wall face (y)
TWN_PF=-0.24          # plaster wall face (y)

def twn_pick(name,fallback):
    """use another agent's piece only if it exists, else a kit / own fallback"""
    return name if bpy.data.objects.get(name) else fallback

def twn_flat_wobble(k,amp=0.035):
    """'flat' wobble envelope (spec 5.3): same y offset as a fade-wobbled ground wall at z=3.0, at every z"""
    for v in k.bm.verts:
        v.co.y+=amp*math.sin(2*math.pi*v.co.x/CELL+0.9)

def twn_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25,mi=STONE):
    if x1-x0<0.004 or z1-z0<0.004: return
    stone_panel(k,x0,x1,z0,z1,y0,y1,mi=mi)

def twn_hole(k,x0,x1,z0,z1,hx0,hx1,hz0,hz1,y0=-0.25,y1=0.25,mi=STONE):
    """rectangular wall x0..x1 / z0..z1 with a rectangular hole hx0..hx1 / hz0..hz1"""
    twn_panel(k,x0,hx0,z0,z1,y0,y1,mi); twn_panel(k,hx1,x1,z0,z1,y0,y1,mi)
    twn_panel(k,hx0,hx1,z0,hz0,y0,y1,mi); twn_panel(k,hx0,hx1,hz1,z1,y0,y1,mi)

def twn_arch_fill(k,cx,hw,spring,top,y0,y1,mi=STONE,n=10):
    """fill the spandrels above a semicircular head (centre cx) up to z=top: exact n-gon faces front and back
       (the soffit supplies the curved inner surface, so nothing pokes into the opening)"""
    for s in(-1,1):
        pts=[(cx+s*hw*math.cos(math.pi/2*i/n),spring+hw*math.sin(math.pi/2*i/n)) for i in range(n+1)]+[(cx+s*hw,spring+hw)]
        for y,front in ((y0,True),(y1,False)):
            vs=[k.bm.verts.new((x,y,z)) for x,z in pts]
            f=k.bm.faces.new(vs); f.material_index=mi
            k.bm.normal_update()
            if (f.normal.y<0)!=front: f.normal_flip()
            t=TILE.get(mi,1.0)
            for l in f.loops: l[k.uv].uv=(-l.vert.co.x/t if front else l.vert.co.x/t,l.vert.co.z/t)
    if top>spring+hw+0.004: twn_panel(k,cx-hw,cx+hw,spring+hw,top,y0,y1,mi)

def twn_arch_soffit(k,cx,hw,spring,y0,y1,mi,n=12):
    for i in range(n):
        a0=math.pi*i/n; a1=math.pi*(i+1)/n
        v=[k.bm.verts.new((cx+math.cos(a)*hw,y,spring+math.sin(a)*hw)) for a,y in ((a0,y0),(a1,y0),(a1,y1),(a0,y1))]
        f=k.bm.faces.new(v); f.material_index=mi
        t=TILE.get(mi,1.0)
        for l,(uu,vv) in zip(f.loops,((a0*hw,y0),(a1*hw,y0),(a1*hw,y1),(a0*hw,y1))): l[k.uv].uv=(uu/t,vv/t)
    k.bm.normal_update()

def twn_voussoirs(k,cx,hw,spring,y0,y1,n=7,th=0.2,mi=STONE_BLOCK,seed=0,key=1.25,out=0.05,segs=2):
    """chunky arch stones around a semicircular head (centre cx), protruding 'out' in front of y0"""
    for i in range(n):
        a=math.pi*(i+0.5)/n; r=hw+th/2; ks=(i==n//2)
        tw=2*math.pi*(hw+th/2)/(2*n)*1.9
        k.box((cx+math.cos(a)*r,(y0+y1)/2-out/2,spring+math.sin(a)*r),
              (tw if not ks else tw*1.15,(y1-y0)+out,th if not ks else th*key),mi,
              rot=(0,-(a-math.pi/2),0),bevel=0.035,segs=segs,jitter=0.01,seed=seed*10+i)

def twn_fan(k,cx,hw,spring,y,mi=WINDOW,n=10):
    """semicircular glass fan (faces -Y)"""
    c=k.bm.verts.new((cx,y,spring))
    arc=[k.bm.verts.new((cx+math.cos(math.pi*i/n)*hw,y,spring+math.sin(math.pi*i/n)*hw)) for i in range(n+1)]
    for i in range(n):
        f=k.bm.faces.new((c,arc[i],arc[i+1])); f.material_index=mi
        for l in f.loops: l[k.uv].uv=(l.vert.co.x-cx+hw,l.vert.co.z)
    k.bm.normal_update()

def twn_glass(k,x0,x1,z0,z1,y):
    k.quad([(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)],WINDOW,uvs=[(x0,z0),(x1,z0),(x1,z1),(x0,z1)])

def twn_jambs(k,x0,x1,z0,z1,face=-0.25,gap=0.15,seed=0,long_=0.36,short_=0.24,out=0.07):
    """alternating dressed jamb stones either side of an opening"""
    n=max(2,int(round((z1-z0)/0.42))); h=(z1-z0)/n
    for s,xe in((-1,x0),(1,x1)):
        for j in range(n):
            w=long_ if (j+(s>0))%2==0 else short_
            xa=xe+s*gap
            k.box((xa+s*w/2,face-out+0.1,z0+h*(j+0.5)),(w,0.2,h-0.035),STONE_BLOCK,bevel=0.04,segs=2,jitter=0.008,seed=seed*7+j*3+(s>0))

def twn_jack_arch(k,cx,zb,hw,n=5,h=0.38,face=-0.25,seed=0):
    """flat arch of wedge voussoirs (fanning from a point below) with a proud keystone"""
    w=2*hw/n
    for i in range(n):
        xc=cx-hw+w*(i+0.5); ang=math.atan2(xc-cx,1.7); ks=(i==n//2)
        hh=h*(1.22 if ks else 1.0)
        k.box((xc,face-0.02-(0.05 if ks else 0.0),zb+hh/2),(w-0.03,0.2+(0.1 if ks else 0.0),hh),STONE_BLOCK,rot=(0,ang,0),bevel=0.04,segs=1,jitter=0.006,seed=seed*9+i)
    k.box((cx,face+0.06,zb+h/2),(2*hw,0.14,h-0.04),STONE_BLOCK,bevel=0)

def twn_belt(k,z=0.07,h=0.26,face=-0.25,out=0.2,x0=-1.5,x1=1.5,mi=STONE_BLOCK,n=4,seed=0):
    """belt course hiding the storey seam; blocks so the joints read"""
    L=(x1-x0)/n
    for i in range(n):
        xa=x0+i*L
        k.box((xa+L/2,face-out/2+0.06,z),(L-0.025,out+0.12,h),mi,bevel=0.05,segs=1,jitter=0.006,seed=seed*11+i)
        k.box((xa+L/2,face-out+0.05,z-h/2-0.02),(L-0.07,0.12,0.07),mi,bevel=0.025,segs=1)      # drip under the belt
    k.box(((x0+x1)/2,face+0.02,z),(x1-x0,0.1,h-0.03),mi,bevel=0)     # joint backing (no see-through gaps)

# ---------------- stone upper floors (H2, face -0.25, flat wobble) ----------------
def twn_stoneup_base(k,seed=0):
    twn_belt(k,seed=seed)

def twn_wall_stoneup(k):
    twn_panel(k,-1.5,1.5,0,H2)
    twn_stoneup_base(k,1)
    wall_rocks(k,-1.5,1.5,0.4,2.6,n=4,seed=13)
    twn_flat_wobble(k)

def twn_wall_stoneup_window(k,shutters=True):
    x0,x1,z0,z1=-0.45,0.45,0.75,1.95
    twn_hole(k,-1.5,1.5,0,H2,x0,x1,z0,z1)
    twn_stoneup_base(k,2)
    window_frame(k,x0,x1,z0,z1,depth_y=-0.04,sill=False,shutters=shutters,face=-0.25)
    k.box((0,-0.36,z0-0.07),(1.25,0.36,0.16),STONE_BLOCK,bevel=0.04,segs=2)            # sill
    for s in(-1,1): k.box((s*0.52,-0.4,z0-0.2),(0.14,0.16,0.14),STONE_BLOCK,bevel=0.03)   # sill corbels
    twn_jack_arch(k,0,z1+0.24,0.86,seed=4)
    wall_rocks(k,-1.5,1.5,0.4,2.6,n=1,seed=9,avoid=((x0-0.8,x1+0.8,z0-0.4,z1+0.8),))
    twn_flat_wobble(k)

def twn_wall_stoneup_twin(k):
    """paired round-headed lights with a colonnette (Romanesque twin window)"""
    hw=0.27; sp=1.82; cxs=(-0.39,0.39); zb=0.72
    X0,X1=-0.66,0.66; ZT=sp+hw
    twn_hole(k,-1.5,1.5,0,H2,X0,X1,zb,ZT)
    twn_panel(k,-0.12,0.12,zb,ZT)                                   # mullion
    for cx in cxs:
        twn_arch_fill(k,cx,hw,sp,ZT,-0.25,0.25)
        yg=-0.05
        twn_glass(k,cx-hw,cx+hw,zb,sp,yg); twn_fan(k,cx,hw,sp,yg)
        # reveals (dressed stone) so the recess reads
        for s in(-1,1):
            v=[k.bm.verts.new(p) for p in ((cx+s*hw,-0.25,zb),(cx+s*hw,yg,zb),(cx+s*hw,yg,sp),(cx+s*hw,-0.25,sp))]
            f=k.bm.faces.new(v if s<0 else v[::-1]); f.material_index=STONE_BLOCK
        twn_arch_soffit(k,cx,hw,sp,-0.25,yg,STONE_BLOCK,n=10)
        k.box((cx,-0.15,zb+0.01),(2*hw,0.2,0.02),STONE_BLOCK,bevel=0)
        twn_voussoirs(k,cx,hw,sp,-0.27,-0.13,n=7,th=0.18,seed=int(cx*10)+5,out=0.06,segs=1)
        k.box((cx,-0.05-0.012,(zb+sp)/2),(0.035,0.02,sp-zb),WOOD,bevel=0.005)          # glazing bar
        k.box((cx,-0.05-0.012,zb+0.55),(2*hw,0.02,0.035),WOOD,bevel=0.005)
    # colonnette with base and capital in front of the mullion
    lathe(k,[(0.11,0.0),(0.11,0.07),(0.075,0.1),(0.07,0.5),(0.068,0.95),(0.075,sp-zb-0.14),(0.12,sp-zb-0.06),(0.13,sp-zb)],center=(0,-0.3,zb),segs=10,mi=STONE_BLOCK)
    k.box((0,-0.3,sp+0.03),(0.34,0.28,0.08),STONE_BLOCK,bevel=0.025)
    # jambs outside the pair + sill
    for s in(-1,1):
        for j,(zc,w) in enumerate(((zb+0.22,0.3),(zb+0.62,0.2),(zb+0.98,0.3))):
            k.box((s*(X1+w/2-0.03),-0.29,zc),(w,0.2,0.36),STONE_BLOCK,bevel=0.04,segs=1,jitter=0.008,seed=40+j+(s>0)*5)
    k.box((0,-0.36,zb-0.07),(1.7,0.34,0.16),STONE_BLOCK,bevel=0.04,segs=1)
    k.box((0,-0.33,ZT+0.3),(2.0,0.16,0.14),STONE_BLOCK,bevel=0.035)                    # hood mould
    for s in(-1,1): k.box((s*1.0,-0.33,ZT+0.19),(0.16,0.16,0.3),STONE_BLOCK,bevel=0.035)
    wall_rocks(k,-1.5,1.5,0.4,2.6,n=1,seed=21,avoid=((X0-0.6,X1+0.6,zb-0.4,ZT+0.8),))
    twn_stoneup_base(k,3)
    twn_flat_wobble(k)

def twn_wall_stoneup_slit(k):
    zc=1.4
    twn_hole(k,-1.5,1.5,0,H2,-0.3,0.3,zc-0.7,zc+0.7)
    # dressed surround: jamb blocks with the cross slit cut between them
    B=STONE_BLOCK; y=-0.2; d=0.26
    k.box((0,y,zc-0.62),(0.62,d,0.18),B,bevel=0.04,segs=2)                 # sill block
    k.box((0,y,zc+0.62),(0.66,d,0.2),B,bevel=0.04,segs=2)                  # head block
    for s in(-1,1):
        k.box((s*0.19,y,zc-0.29),(0.24,d,0.5),B,bevel=0.03,segs=2,jitter=0.006,seed=2+s)
        k.box((s*0.19,y,zc+0.3),(0.24,d,0.46),B,bevel=0.03,segs=2,jitter=0.006,seed=5+s)
        k.box((s*0.235,y,zc),(0.15,d,0.1),B,bevel=0.01)                    # arm edges
    k.box((0,0.04,zc),(0.36,0.2,1.2),VOID,bevel=0)
    k.box((0,-0.36,zc-0.62),(0.5,0.08,0.06),B,bevel=0.02)
    twn_stoneup_base(k,4)
    wall_rocks(k,-1.5,1.5,0.4,2.6,n=3,seed=17,avoid=((-0.6,0.6,0,2.8),))
    twn_flat_wobble(k)

def twn_door_leaf(k,x,y,z0,z1,w,ang,hinge_side,mi=PLANKS,boards=4,straps=True,seed=0):
    """plank leaf hinged at (x,y), width w, swung by ang (rad) outward (-Y)"""
    R=Matrix.Translation((x,y,0))@Matrix.Rotation(hinge_side*ang,4,"Z")
    bw=w/boards
    for i in range(boards):
        k.box((-hinge_side*(bw*(i+0.5)),0,(z0+z1)/2),(bw-0.012,0.07,z1-z0-0.01*(i%2)),mi,bevel=0.01,xform=R)
    for zz in (z0+0.35,z1-0.35):
        k.box((-hinge_side*w*0.5,-0.05,zz),(w-0.06,0.035,0.1),IRON if straps else WOOD,bevel=0.01,xform=R)
    if straps:
        for zz in (z0+0.35,z1-0.35):
            _cyl(k,(x,y,zz),0.045,0.045,0.16,8,IRON)
    k.box((-hinge_side*w*0.5,-0.06,(z0+z1)/2),(0.08,0.03,z1-z0-0.8),WOOD,rot=(0,hinge_side*0.55,0),bevel=0.01,xform=R)

def twn_wall_stoneup_loading(k):
    hw=0.65; z0=0.16; z1=2.1
    twn_hole(k,-1.5,1.5,0,H2,-hw,hw,0,z1)
    twn_belt(k,x0=-1.5,x1=-hw-0.02,n=2,seed=5); twn_belt(k,x0=hw+0.02,x1=1.5,n=2,seed=6)
    k.box((0,-0.2,0.08),(1.6,0.4,0.16),WOOD,bevel=0.03)                                  # sill beam
    k.box((0,-0.3,z1+0.13),(1.75,0.3,0.26),WOOD,bevel=0.04,segs=2)                          # lintel beam
    rock(k,(0,-0.3,z1+0.45),(1.9,0.24,0.3),seed=91,tilt=0.02)
    twn_jambs(k,-hw,hw,0.18,z1,gap=0.02,seed=7,long_=0.34,short_=0.22)
    # interior darkness + floor + a sack
    k.quad([(-hw,0.2,z0),(hw,0.2,z0),(hw,0.2,z1),(-hw,0.2,z1)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for s in(-1,1):
        v=[k.bm.verts.new(p) for p in ((s*hw,-0.25,z0),(s*hw,0.2,z0),(s*hw,0.2,z1),(s*hw,-0.25,z1))]
        f=k.bm.faces.new(v if s<0 else v[::-1]); f.material_index=STONE_BLOCK
    k.box((0,0.0,z0+0.02),(2*hw,0.45,0.04),PLANKS,bevel=0)
    k.box((0.25,0.05,z0+0.3),(0.4,0.3,0.55),BURLAP,bevel=0.1,segs=2,jitter=0.03,seed=4)
    k.box((-0.3,0.05,z0+0.22),(0.45,0.4,0.4),WOOD,bevel=0.03)
    # two leaves thrown open ~100 deg
    for s in(-1,1): twn_door_leaf(k,s*hw,-0.3,z0+0.04,z1-0.04,hw-0.02,math.radians(100),s,boards=3,seed=s)
    twn_flat_wobble(k)

def twn_wall_stoneup_door(k):
    hw=0.55; sp=1.8; zt=0.3
    twn_hole(k,-1.5,1.5,0,H2,-hw,hw,0,sp)
    twn_arch_fill(k,0,hw,sp,H2,-0.25,0.25)
    twn_belt(k,x0=-1.5,x1=-hw-0.12,n=2,seed=7); twn_belt(k,x0=hw+0.12,x1=1.5,n=2,seed=8)
    k.box((0,-0.2,zt/2),(2*hw+0.3,0.62,zt),STONE_BLOCK,bevel=0.04,segs=2)                     # threshold slab
    twn_voussoirs(k,0,hw,sp,-0.27,-0.1,n=7,th=0.24,seed=12)
    for s in(-1,1):
        for j,(zc,w) in enumerate(((zt+0.3,0.38),(zt+0.8,0.26),(zt+1.25,0.38))):
            k.box((s*(hw+w/2),-0.24,zc),(w,0.2,0.42),STONE_BLOCK,bevel=0.04,segs=1,jitter=0.008,seed=60+j+(s>0)*4)
    twn_arch_soffit(k,0,hw,sp,-0.25,0.02,STONE_BLOCK,n=12)
    for s in(-1,1):
        v=[k.bm.verts.new(p) for p in ((s*hw,-0.25,zt),(s*hw,0.02,zt),(s*hw,0.02,sp),(s*hw,-0.25,sp))]
        f=k.bm.faces.new(v if s<0 else v[::-1]); f.material_index=STONE_BLOCK
    # door leaf (boards follow the arch)
    nb=5
    for i in range(nb):
        x=-hw+(i+0.5)*(2*hw)/nb; top_i=sp+math.sqrt(max(0,hw*hw-x*x))-0.03
        k.box((x,0.03,(zt+top_i)/2),((2*hw)/nb-0.014,0.1,top_i-zt),PLANKS,bevel=0.012)
    for zz in (zt+0.35,zt+1.35):
        k.box((0,-0.04,zz),(2*hw-0.1,0.03,0.1),IRON,bevel=0.01)
        for i in range(4): k.box((-hw+0.16+i*(2*hw-0.32)/3,-0.06,zz),(0.05,0.03,0.05),IRON,bevel=0)
    ring(k,(0.3,-0.05,zt+0.95),0.05,0.08,0.03,IRON,n=10,axis="Y")
    twn_flat_wobble(k)

def twn_corner_stoneup(k):
    """outer corner, faces toward -X and -Y (H2); belt wraps the corner, quoins above"""
    k.box((0,0,H2/2),(0.8,0.8,H2),STONE,bevel=0)
    k.box((-0.02,-0.02,0.07),(0.9,0.9,0.26),STONE_BLOCK,bevel=0.045,segs=2)
    z=0.2; i=0; rnd=random.Random(15)
    while z<H2-0.05:
        h=min(rnd.uniform(0.38,0.48),H2-z)
        if H2-(z+h)<0.2: h=H2-z
        sx,sy=(1.05,0.62) if i%2==0 else (0.62,1.05)
        rock(k,(-0.43+sx/2,-0.43+sy/2,z+h/2),(sx,sy,h-0.03),seed=i*19+7,tilt=0.02,segs=2)
        z+=h; i+=1

def twn_inner_corner_stoneup(k):
    rnd=random.Random(9); z=0.2; i=0
    while z<H2-0.05:
        h=min(rnd.uniform(0.38,0.48),H2-z)
        if H2-(z+h)<0.2: h=H2-z
        if i%2==0: k.box((0.55,0.3,z+h/2),(0.6,0.14,h-0.03),STONE_BLOCK,bevel=0.04,segs=2,jitter=0.01,seed=i)
        else:      k.box((0.3,0.55,z+h/2),(0.14,0.6,h-0.03),STONE_BLOCK,bevel=0.04,segs=2,jitter=0.01,seed=i)
        z+=h; i+=1

# ---------------- plaster (rendered) upper floors (H2, face -0.24, flat wobble) ----------------
def twn_plasterup_bands(k,x0=-1.5,x1=1.5):
    k.box(((x0+x1)/2,-0.3,0.08),(x1-x0,0.22,0.17),WOOD,bevel=0.035)                   # sole band
    k.box(((x0+x1)/2,-0.28,H2-0.09),(x1-x0,0.18,0.18),WOOD,bevel=0.035)               # top plate
    for i in range(6):                                                                 # joist ends under the band
        k.box((-1.25+i*0.5,-0.38,-0.05),(0.15,0.14,0.14),WOOD,bevel=0.03)

def twn_bare_patch(k,cx,cz,w,h,seed=0,face=TWN_PF):
    """patch where the render has fallen off: stone behind a jagged plaster lip"""
    rnd=random.Random(seed); n=8
    pts=[]
    for i in range(n):
        a=2*math.pi*i/n; r=1.0+rnd.uniform(-0.18,0.12)
        pts.append((cx+math.cos(a)*w/2*r,cz+math.sin(a)*h/2*r))
    y=face-0.004
    v=[k.bm.verts.new((x,y,z)) for x,z in pts]
    f=k.bm.faces.new(v[::-1]); f.material_index=STONE
    for l in f.loops: l[k.uv].uv=(-l.vert.co.x/1.4+0.37,l.vert.co.z/1.4+0.21)
    for i in range(n):
        (xa,za),(xb,zb)=pts[i],pts[(i+1)%n]
        L=math.hypot(xb-xa,zb-za); ang=math.atan2(zb-za,xb-xa)
        k.box(((xa+xb)/2,y-0.012,(za+zb)/2),(L+0.05,0.03,0.05),PLASTER,rot=(0,-ang,0),bevel=0.01)
    k.bm.normal_update()

def twn_wall_plasterup(k):
    twn_panel(k,-1.5,1.5,0.0,H2,-0.24,0.2,mi=PLASTER)
    twn_plasterup_bands(k)
    twn_bare_patch(k,-0.75,1.2,0.62,0.44,seed=3)
    twn_bare_patch(k,0.9,2.1,0.35,0.28,seed=8)
    twn_flat_wobble(k)

def twn_wall_plasterup_window(k):
    x0,x1,z0,z1=-0.45,0.45,0.8,2.0
    twn_hole(k,-1.5,1.5,0.0,H2,x0,x1,z0,z1,-0.24,0.2,mi=PLASTER)
    twn_plasterup_bands(k)
    window_frame(k,x0,x1,z0,z1,depth_y=-0.02,sill=False,shutters=True,face=-0.2)
    k.box((0,-0.34,z0-0.08),(1.3,0.3,0.14),WOOD,bevel=0.035)                          # sill board
    for s in(-1,1): k.box((s*0.5,-0.33,z0-0.28),(0.1,0.12,0.3),WOOD,rot=(0.5,0,0),bevel=0.02)
    twn_flat_wobble(k)

def twn_wall_plasterup_oxeye(k):
    zc=1.55; R=0.36
    twn_hole(k,-1.5,1.5,0.0,H2,-R,R,zc-R,zc+R,-0.24,0.2,mi=PLASTER)
    twn_plasterup_bands(k)
    # glass disc (recessed) + deep dressed ring
    n=16; c=k.bm.verts.new((0,-0.02,zc))
    rim=[k.bm.verts.new((math.cos(2*math.pi*i/n)*(R+0.02),-0.02,zc+math.sin(2*math.pi*i/n)*(R+0.02))) for i in range(n)]
    for i in range(n):
        f=k.bm.faces.new((c,rim[i],rim[(i+1)%n])); f.material_index=WINDOW
        for l in f.loops: l[k.uv].uv=(l.vert.co.x*1.2,l.vert.co.z*1.2)
    k.bm.normal_update()
    ring(k,(0,-0.02,zc),R-0.05,R+0.2,0.46,STONE_BLOCK,n=16,axis="Y")
    nv=10; rm=R+0.08
    for i in range(nv):
        a=2*math.pi*i/nv+math.pi/2; ks=(i==0)
        tw=2*math.pi*rm/nv-0.025
        k.box((math.cos(a)*(rm+(0.03 if ks else 0)),-0.29-(0.03 if ks else 0),zc+math.sin(a)*(rm+(0.03 if ks else 0))),(tw*(1.15 if ks else 1),0.14+(0.06 if ks else 0),0.2+(0.08 if ks else 0)),STONE_BLOCK,rot=(0,-(a-math.pi/2),0),bevel=0.03,segs=1,jitter=0.005,seed=i)
    k.box((0,-0.05,zc),(0.04,0.03,2*R),WOOD,bevel=0.005); k.box((0,-0.05,zc),(2*R,0.03,0.04),WOOD,bevel=0.005)
    twn_flat_wobble(k)

def twn_corner_plasterup(k):
    k.box((-0.22,-0.22,H2/2),(0.34,0.34,H2),WOOD,bevel=0.05,segs=2)
    k.box((-0.12,-0.12,0.08),(0.58,0.58,0.2),WOOD,bevel=0.04)
    k.box((-0.1,-0.1,H2-0.09),(0.56,0.56,0.2),WOOD,bevel=0.04)
    k.box((-0.42,-0.42,-0.1),(0.24,0.24,0.24),WOOD,rot=(0,0,math.pi/4),bevel=0.04)      # dragon beam end
    k.box((-0.22,-0.22,H2-0.32),(0.42,0.42,0.14),WOOD,bevel=0.03)                        # capital

def twn_inner_corner_plasterup(k):
    k.box((0.3,0.3,H2/2),(0.24,0.24,H2),WOOD,bevel=0.04)
    k.box((0.32,0.32,0.08),(0.3,0.3,0.2),WOOD,bevel=0.03)

# ---------------- shop fronts (ground, 3.0 m, std) ----------------
TWN_CZ=0.95           # counter top (Stock socket at wall-local (0,-0.55,TWN_CZ))

def twn_skirt(k,x0=-1.5,x1=1.5,y0=-0.3,y1=0.25,z0=-0.6,mi=STONE):
    """hidden skirt so the piece never floats on uneven terrain"""
    k.box(((x0+x1)/2,(y0+y1)/2,z0/2),(x1-x0,y1-y0,-z0),mi,bevel=0)

def twn_reveal(k,x0,x1,z0,z1,yf,yb,mi=STONE_BLOCK,top=True,bottom=False):
    for s,x in((-1,x0),(1,x1)):
        v=[k.bm.verts.new(p) for p in ((x,yf,z0),(x,yb,z0),(x,yb,z1),(x,yf,z1))]
        f=k.bm.faces.new(v if s<0 else v[::-1]); f.material_index=mi
    if top:
        v=[k.bm.verts.new(p) for p in ((x0,yf,z1),(x0,yb,z1),(x1,yb,z1),(x1,yf,z1))]
        f=k.bm.faces.new(v); f.material_index=mi
    if bottom:
        v=[k.bm.verts.new(p) for p in ((x0,yf,z0),(x1,yf,z0),(x1,yb,z0),(x0,yb,z0))]
        f=k.bm.faces.new(v); f.material_index=mi
    k.bm.normal_update()

def twn_shop_inside(k,hw,z0,z1,yf,yb=0.2,seed=0):
    """dark shop interior behind the opening: back plane, reveals, shelf with wares"""
    k.quad([(-hw,yb,z0),(hw,yb,z0),(hw,yb,z1),(-hw,yb,z1)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    twn_reveal(k,-hw,hw,z0,z1,yf,yb,mi=PLANKS)
    k.box((0,(yf+yb)/2,z0-0.02),(2*hw,yb-yf,0.05),PLANKS,bevel=0.01)                        # inner sill board
    zs=1.62
    k.box((0,yb-0.13,zs),(2*hw-0.04,0.26,0.05),PLANKS,bevel=0.01)                            # shelf
    for x in (-hw+0.25,hw-0.25): k.box((x,yb-0.08,zs-0.12),(0.05,0.14,0.2),WOOD,bevel=0.01)
    rnd=random.Random(seed)
    x=-hw+0.15
    while x<hw-0.2:
        kind=rnd.randrange(3); r=rnd.uniform(0.07,0.11)
        if kind==0: _cyl(k,(x,yb-0.13,zs+0.025+r*1.1),r,r*0.8,r*2.2,8,CLAY)
        elif kind==1: k.box((x,yb-0.13,zs+0.025+r),(r*2.2,0.18,r*2),WOOD,bevel=0.01)
        else: _ico(k,(x,yb-0.13,zs+0.025+r*0.6),r,BREAD,(1.2,0.9,0.6),sub=1)
        x+=r*2.2+rnd.uniform(0.05,0.14)
    k.box((0.55*hw,yb-0.2,z1-0.28),(0.012,0.012,0.3),IRON,bevel=0)                         # hanging bunch
    _ico(k,(0.55*hw,yb-0.2,z1-0.5),0.09,HAY,(1,1,1.6),sub=1)

def twn_counter(k,hw=1.1,face=-0.25):
    """lowered lower shutter = the counter, on two diagonal brackets"""
    zt=TWN_CZ; D=0.6
    k.box((0,face-D/2,zt-0.035),(2*hw,D,0.07),PLANKS,bevel=0.015)
    k.box((0,face-D+0.03,zt-0.075),(2*hw,0.06,0.07),WOOD,bevel=0.015)                   # front batten
    for x in (-hw+0.3,hw-0.3):
        L=math.hypot(D-0.1,0.45); ang=math.atan2(0.45,D-0.1)
        k.box((x,face-(D-0.1)/2,zt-0.07-0.225),(0.09,L,0.09),WOOD,rot=(-ang,0,0),bevel=0.02)
        k.box((x,face-0.02,zt-0.5),(0.12,0.06,0.12),IRON,bevel=0.015)
    for x in (-hw+0.35,hw-0.35): k.box((x,face-0.06,zt-0.03),(0.18,0.1,0.04),IRON,bevel=0.01)  # hinges

def twn_canopy(k,hw=1.15,zh=2.36,yh=-0.42,L=0.78,ang=50):
    """upper shutter propped open (raised 'ang' deg above horizontal) on two iron stays"""
    a=math.radians(ang); d=Vector((0,-math.cos(a),math.sin(a)))
    c=Vector((0,yh,zh))+d*(L/2)
    k.box(tuple(c),(2*hw,L,0.06),PLANKS,rot=(-a,0,0),bevel=0.015)
    n=Vector((0,-math.sin(a),-math.cos(a)))                     # underside normal
    for t in (0.2,0.8):
        k.box(tuple(Vector((0,yh,zh))+d*(L*t)+n*0.05),(2*hw-0.1,0.07,0.05),WOOD,rot=(-a,0,0),bevel=0.012)
    for x in (-hw+0.12,hw-0.12):
        p0=Vector((x,yh+0.12,zh-0.62)); p1=Vector((x,yh,zh))+d*(L*0.78)+n*0.04
        dd=p1-p0; q=Vector((0,0,1)).rotation_difference(dd.normalized()).to_matrix().to_4x4()
        sub=Kit(); sub.box((0,0,0),(0.03,0.03,dd.length),IRON,bevel=0); merge_kit(k,sub,Matrix.Translation((p0+p1)/2)@q)
    for x in (-hw+0.4,hw-0.4): _cyl(k,(x,yh+0.02,zh),0.035,0.035,0.2,6,IRON,rot=Matrix.Rotation(math.pi/2,4,"Y"))

def twn_wall_stone_shop(k):
    hw=1.1; z0=TWN_CZ-0.02; z1=2.35
    twn_hole(k,-1.5,1.5,0,H1,-hw,hw,z0,z1)
    plinth(k); batter(k)
    twn_skirt(k)
    k.box((0,-0.2,z0-0.06),(2*hw+0.14,0.44,0.14),STONE_BLOCK,bevel=0.03)                     # stone sill
    k.box((0,-0.28,z1+0.125),(2.6,0.34,0.26),WOOD,bevel=0.04,segs=2)                          # lintel
    twn_jack_arch(k,0,z1+0.26,1.0,n=7,h=0.34,seed=5)
    for s in(-1,1):
        for j,(zc,w) in enumerate(((z0+0.22,0.34),(z0+0.66,0.26),(z0+1.08,0.34))):
            k.box((s*(hw+w/2-0.02),-0.28,zc),(w,0.16,0.4),STONE_BLOCK,bevel=0.035,segs=1,jitter=0.008,seed=80+j+(s>0)*3)
    twn_shop_inside(k,hw,z0,z1,-0.25,seed=1)
    twn_counter(k,hw)
    twn_canopy(k)
    wall_rocks(k,-1.5,1.5,0.4,H1,n=1,seed=31,avoid=((-1.6,1.6,0.3,3.0),))

def twn_wall_plaster_shop(k):
    hw=1.1; z0=TWN_CZ-0.02; z1=2.35
    stone_panel(k,-1.5,1.5,0,PL,-0.28,0.25); plinth(k); batter(k,0.05)
    twn_skirt(k)
    k.box((0,-0.2,PL+0.08),(CELL,0.4,0.2),WOOD,bevel=0.035)                                 # sill beam (top 0.93)
    k.box((0,-0.2,H1-0.11),(CELL,0.4,0.22),WOOD,bevel=0.035)                                # top plate
    k.box((-1.5,-0.24,(PL+H1)/2),(0.24,0.2,H1-PL-0.2),WOOD,bevel=0.03)                     # module post
    for s in(-1,1):
        k.box((s*1.25,-0.25,(PL+H1)/2),(0.2,0.22,H1-PL-0.3),WOOD,bevel=0.03)
        twn_panel(k,*((-1.5,-hw) if s<0 else (hw,1.5)),z0,H1-0.2,-0.24,0.2,mi=PLASTER)
        brace(k,s*1.12,z1-0.3,s*0.8,z1+0.02,w=0.12,y=-0.3)
    twn_panel(k,-hw,hw,z1+0.25,H1-0.2,-0.24,0.2,mi=PLASTER)
    k.box((0,-0.3,z1+0.125),(2.6,0.3,0.26),WOOD,bevel=0.04,segs=2)                           # lintel
    pegs(k,(-1.25,1.25),(1.2,2.2),y=-0.37)
    twn_shop_inside(k,hw,z0,z1,-0.24,seed=2)
    twn_counter(k,hw)
    twn_canopy(k,yh=-0.46)

# ---------------- goods for the counters (origin at the counter top, fit 2.0 x 0.5 x 0.45) ----------------
def twn_basket(k,c,r,h,mi=HAY):
    lathe(k,[(r*0.8,0),(r,h*0.6),(r*1.05,h),(r*0.92,h)],center=c,segs=12,mi=mi)
    lathe(k,[(r*0.92,h*0.85),(0.0,h*0.85)],center=c,segs=12,mi=WOOD)

def twn_goods_bread(k):
    rnd=random.Random(1)
    k.box((0,0,0.02),(1.9,0.46,0.04),PLANKS,bevel=0.01)
    for cx in (-0.62,0.62):
        twn_basket(k,(cx,0,0.04),0.24,0.14)
        for i in range(5):
            a=i*1.26+rnd.uniform(-0.2,0.2); rr=0.0 if i==0 else 0.12
            goods_map(k,_ico(k,(cx+math.cos(a)*rr,math.sin(a)*rr,0.2+(0.04 if i==0 else 0)),0.1,BREAD,(1.2,0.9,0.65),sub=2,jit=0.01,seed=i),"bread")
    for i in range(3):                                   # long loaves
        goods_map(k,_ico(k,(-0.12+i*0.12,-0.02,0.1),0.075,BREAD,(0.9,3.0,0.8),sub=2,seed=i+7),"bread",ref=(0,1,0))
        for j in range(3): k.box((-0.12+i*0.12,-0.02-0.14+j*0.14,0.155),(0.06,0.02,0.015),PAPER,rot=(0,0,0.5),bevel=0)
    for (x,y) in ((0.3,0.12),(-0.3,0.14)):               # pretzels standing on a peg
        k.box((x,y,0.14),(0.02,0.02,0.24),WOOD,bevel=0)
        fs=[]
        for (dx,dz,r) in ((-0.05,0.2,0.07),(0.05,0.2,0.07),(0,0.13,0.08)):
            fs+=ring(k,(x+dx,y,dz+0.05),r-0.03,r,0.05,BREAD,n=12,axis="Y")
        goods_map(k,fs,"bread",plane=((1,0,0),(0,0,1)))

def twn_goods_produce(k):
    rnd=random.Random(2)
    for cx,kind in ((-0.62,"apple"),(0.0,"cabbage"),(0.62,"carrot")):
        k.box((cx,0,0.08),(0.56,0.44,0.16),WOOD,bevel=0.02)
        k.box((cx,0,0.155),(0.5,0.38,0.01),VOID,bevel=0)
        if kind=="apple":
            for i in range(12):
                x=cx-0.18+(i%4)*0.12; y=-0.12+(i//4)*0.12
                vs=_ico(k,(x+rnd.uniform(-.02,.02),y,0.2+rnd.uniform(0,.03)),0.065,APPLE if i%5 else YELLOW,sub=2)
                if i%5: goods_map(k,vs,"apple",ref=(math.cos(i*2.1),math.sin(i*2.1),0))
        elif kind=="cabbage":
            for i in range(4):
                x=cx-0.12+(i%2)*0.24; y=-0.09+(i//2)*0.18
                goods_map(k,_ico(k,(x,y,0.24),0.12,LEAF,(1,1,0.85),sub=2,jit=0.015,seed=i),"cabbage",ref=(math.cos(i),math.sin(i),0))
        else:
            for i in range(9):
                x=cx-0.16+(i%3)*0.16; y=-0.12+(i//3)*0.12
                R_=Matrix.Rotation(math.pi/2,4,"X")@Matrix.Rotation(rnd.uniform(-0.3,0.3),4,"Y")
                vs=_cyl(k,(x,y,0.2),0.035,0.004,0.26,6,PUMPKIN,rot=R_)
                goods_map(k,vs,"carrot",axis=-(R_.to_3x3()@Vector((0,0,1))),c=(x,y,0.2))           # tip -> crown (leaves at +y)
                for j in range(3): k.box((x+(j-1)*0.02,y+0.16,0.22+j*0.01),(0.02,0.12,0.02),LEAF,rot=(0.6,0,(j-1)*0.4),bevel=0)
    goods_map(k,_ico(k,(-0.95,0.1,0.12),0.13,PUMPKIN,(1,1,0.8),sub=2,seed=4),"pumpkin")

def twn_goods_cloth(k):
    for i,(x,mi) in enumerate(((-0.72,CLOTH_A),(-0.52,CLOTH_B),(-0.32,CLOTH_A))):     # bolts lying across
        _cyl(k,(x,0,0.09),0.09,0.09,0.46,12,mi,rot=Matrix.Rotation(math.pi/2,4,"X"))
        _cyl(k,(x,0,0.09),0.02,0.02,0.5,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    stack=((PAPER,0.06),(CLOTH_B,0.07),(CLOTH_A,0.06),(BURLAP,0.07)); z=0.0
    for j,(mi,h) in enumerate(stack):
        k.box((0.2,0.02,z+h/2),(0.5-j*0.02,0.34,h),mi,rot=(0,0,0.05*(j%2)),bevel=0.02); z+=h
    _cyl(k,(0.72,0.05,0.2),0.07,0.07,0.4,10,CLOTH_B)                                   # standing bolts
    _cyl(k,(0.86,0.1,0.17),0.07,0.07,0.34,10,CLOTH_A)
    n=8; x0,x1=-0.1,0.55                                                              # drape over the front edge
    for i in range(n):
        xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n
        wa=0.02*math.sin(i*1.7); wb=0.02*math.sin((i+1)*1.7)
        v=[k.bm.verts.new(p) for p in ((xa,-0.2,0.012),(xb,-0.2,0.012),(xb,-0.31+wb,0.0),(xa,-0.31+wa,0.0))]
        f=k.bm.faces.new(v[::-1]); f.material_index=CLOTH_A
        v2=[k.bm.verts.new(p) for p in ((xa,-0.31+wa,0.0),(xb,-0.31+wb,0.0),(xb,-0.32+wb,-0.42-0.03*(i%2)),(xa,-0.32+wa,-0.42-0.03*((i+1)%2)))]
        f=k.bm.faces.new(v2[::-1]); f.material_index=CLOTH_A
    k.bm.normal_update()

def twn_goods_pots(k):
    prof_jug=[(0.0,0),(0.08,0),(0.11,0.06),(0.12,0.14),(0.08,0.24),(0.05,0.27),(0.065,0.3),(0.05,0.3)]
    prof_amph=[(0.0,0),(0.05,0),(0.1,0.1),(0.14,0.24),(0.11,0.34),(0.06,0.38),(0.07,0.42),(0.055,0.42)]
    prof_bowl=[(0.0,0),(0.06,0),(0.13,0.05),(0.16,0.09),(0.145,0.09),(0.0,0.03)]
    for i,x in enumerate((-0.8,-0.52,0.52,0.8)):
        lathe(k,prof_jug if i%2 else prof_amph,center=(x,0.05*(i%2),0),segs=10,mi=CLAY)
        if i%2: k.box((x+0.12,0.05*(i%2),0.18),(0.03,0.03,0.1),CLAY,bevel=0.01)
    for j in range(4): lathe(k,prof_bowl,center=(-0.16,-0.05,j*0.045),segs=12,mi=CLAY)
    for j in range(3): lathe(k,[(0.0,0),(0.1,0),(0.12,0.08),(0.1,0.08),(0.0,0.02)],center=(0.18,0.02,j*0.05),segs=10,mi=CLAY)
    lathe(k,[(0.0,0),(0.1,0),(0.13,0.1),(0.12,0.16),(0.1,0.16)],center=(0.02,0.16,0),segs=10,mi=PAPER)

def twn_goods_tools(k):
    k.box((0,0,0.01),(1.8,0.46,0.02),BURLAP,bevel=0)
    def axe(x,y,a):
        R=Matrix.Translation((x,y,0.035))@Matrix.Rotation(a,4,"Z")
        sub=Kit(); sub.box((0,0,0),(0.6,0.045,0.035),WOOD,bevel=0.01)
        sub.box((0.28,0.06,0),(0.08,0.14,0.03),STEEL,bevel=0.01); sub.box((0.28,0.14,0),(0.14,0.05,0.028),STEEL,bevel=0.01)
        merge_kit(k,sub,R)
    def hammer(x,y,a):
        R=Matrix.Translation((x,y,0.035))@Matrix.Rotation(a,4,"Z")
        sub=Kit(); sub.box((0,0,0),(0.4,0.035,0.03),WOOD,bevel=0.008); sub.box((0.19,0,0.015),(0.06,0.16,0.06),IRON,bevel=0.01)
        merge_kit(k,sub,R)
    axe(-0.55,-0.08,0.2); axe(-0.5,0.12,-0.1); hammer(0.05,-0.1,0.4); hammer(0.1,0.1,-0.2)
    for i in range(3): ring(k,(0.5+i*0.13,-0.1,0.07),0.035,0.06,0.02,IRON,n=10,axis="Y")            # horseshoes
    k.box((0.75,0.08,0.03),(0.4,0.18,0.06),WOOD,bevel=0.01)
    for i in range(4): k.box((0.6+i*0.1,0.08,0.09),(0.02,0.1,0.06),STEEL,bevel=0.005)                # knives
    k.box((0.25,0.1,0.1),(0.2,0.12,0.2),WOOD,bevel=0.015)
    for i in range(3): _cyl(k,(0.2+i*0.05,0.1,0.28),0.012,0.012,0.18,5,WOOD)
    # upright pegboard at the back so the stall reads from the street: saw, sickles, hanging hammers
    for x in (-0.86,0.86): k.box((x,0.2,0.225),(0.05,0.05,0.45),WOOD,bevel=0.01)
    k.box((0,0.2,0.425),(1.78,0.05,0.05),WOOD,bevel=0.01)
    k.box((0,0.215,0.24),(1.68,0.02,0.34),PLANKS,bevel=0)
    k.box((-0.5,0.19,0.3),(0.5,0.012,0.11),STEEL,bevel=0.004); k.box((-0.2,0.185,0.31),(0.12,0.03,0.1),WOOD,bevel=0.01)   # saw
    for sx in (0.05,0.3):                                                                             # sickles
        for j in range(5):
            a=math.radians(200-j*40); k.box((sx+math.cos(a)*0.08,0.19,0.3+math.sin(a)*0.08),(0.05,0.012,0.022),STEEL,rot=(0,-(a+math.pi/2),0),bevel=0)
        k.box((sx+0.075,0.19,0.2),(0.03,0.025,0.12),WOOD,bevel=0.005)
    for x in (0.58,0.72):                                                                             # hanging hammers
        k.box((x,0.19,0.25),(0.025,0.02,0.2),WOOD,bevel=0.004); k.box((x,0.19,0.15),(0.1,0.04,0.045),IRON,bevel=0.008)

def twn_goods_meat(k):
    k.box((0,0,0.03),(1.8,0.44,0.06),WOOD,bevel=0.015)
    for i,(x,a) in enumerate(((-0.62,0.3),(-0.25,-0.4))):
        goods_map(k,_ico(k,(x,0.0,0.16),0.12,PIGSKIN,(1.5,1.0,0.85),sub=2,seed=i),"ham",axis=(1,0,0),ref=(0,0,1))
        _cyl(k,(x+math.cos(a)*0.2,math.sin(a)*0.2,0.15),0.035,0.03,0.12,8,PAPER,rot=Matrix.Rotation(math.pi/2,4,"Y")@Matrix.Rotation(a,4,"X"))
    goods_map(k,lathe(k,[(0.0,0.0),(0.14,0.0),(0.15,0.05),(0.0,0.07)],center=(0.1,0.05,0.06),segs=12,mi=APPLE),"meat",
              plane=((1,0,0),(0,1,0)))                                                            # cut roast
    for j in range(5):                                                                            # sausage coil
        a0=j*1.25; r=0.05+0.018*j; R_=Matrix.Rotation(math.pi/2,4,"X")@Matrix.Rotation(a0,4,"Y")
        goods_map(k,_cyl(k,(0.55+math.cos(a0)*r,math.sin(a0)*r,0.1),0.03,0.03,0.12,6,APPLE,rot=R_),"sausage",axis=R_.to_3x3()@Vector((0,0,1)))
    for i in range(4): goods_map(k,_ico(k,(0.82,-0.12+i*0.08,0.1),0.035,APPLE,(2.5,1,1),sub=1),"sausage",axis=(1,0,0))
    k.box((0.3,-0.14,0.07),(0.22,0.08,0.015),STEEL,bevel=0.004); k.box((0.45,-0.14,0.07),(0.12,0.03,0.025),WOOD,bevel=0.006)  # cleaver

def twn_goods_candles(k):
    rnd=random.Random(8)
    k.box((0,0.02,0.04),(1.2,0.36,0.08),WOOD,bevel=0.015)
    x=-0.52
    while x<0.55:
        h=rnd.uniform(0.12,0.3); r=rnd.uniform(0.025,0.045)
        _cyl(k,(x,rnd.uniform(-0.08,0.1),0.08+h/2),r,r,h,8,PAPER)
        if rnd.random()<0.45: _ico(k,(x,0,0.08+h+0.03),0.022,GLOW,(1,1,1.8),sub=1)
        x+=r*2+rnd.uniform(0.02,0.07)
    for sx in (-0.85,0.85):                                                                         # tallow bundles
        for j in range(5): _cyl(k,(sx+(j-2)*0.035,0.0,0.05),0.017,0.017,0.4,6,PAPER,rot=Matrix.Rotation(math.pi/2,4,"X"))
        k.box((sx,0.0,0.07),(0.2,0.02,0.02),BURLAP,bevel=0)
    lathe(k,[(0.0,0),(0.07,0),(0.03,0.02),(0.025,0.2),(0.06,0.22),(0.05,0.24)],center=(0.7,0.14,0),segs=8,mi=IRON)
    _cyl(k,(0.7,0.14,0.32),0.02,0.02,0.14,6,PAPER); _ico(k,(0.7,0.14,0.42),0.022,GLOW,(1,1,1.8),sub=1)

def twn_goods_fish(k):
    rnd=random.Random(9)
    def fish(x,y,z,a,L=0.3):
        R=Matrix.Translation((x,y,z))@Matrix.Rotation(a,4,"Z")
        sub=Kit(); vs=_ico(sub,(0,0,0),L/2,STEEL,(1,0.3,0.18),sub=2,seed=int(x*100))
        v=[sub.bm.verts.new(p) for p in ((-L*0.45,0,0),(-L*0.72,0.07,0.0),(-L*0.72,-0.07,0.0))]
        f=sub.bm.faces.new(v); f.material_index=STEEL; v2=[sub.bm.verts.new(q.co+Vector((0,0,-0.004))) for q in v]; f2=sub.bm.faces.new(v2[::-1]); f2.material_index=STEEL
        sub.bm.normal_update()
        # lying on its side (flat in z): the back points to +y, so the flank faces up; head at +x
        goods_map(sub,list({ff for vv in vs for ff in vv.link_faces})+[f,f2],"fish",axis=(1,0,0),ref=(0,1,0),c=(0,0,0))
        merge_kit(k,sub,R)
    for cx in (-0.55,0.35):
        k.box((cx,0,0.06),(0.62,0.42,0.12),PLANKS,bevel=0.015)
        k.box((cx,0,0.121),(0.56,0.36,0.004),PAPER,bevel=0)
        for i in range(6):
            fish(cx-0.14+(i%2)*0.26+rnd.uniform(-0.02,0.02),-0.12+(i//2)*0.12,0.15+0.02*(i%2),rnd.uniform(-0.3,0.3)+(math.pi if i%2 else 0))
    fish(0.85,-0.05,0.04,1.3,L=0.42)
    k.box((-0.12,0.14,0.1),(0.12,0.12,0.2),WOOD,bevel=0.01)
    ring(k,(-0.12,0.14,0.28),0.05,0.08,0.02,IRON,n=10,axis="Z")

# ---------------- pent roof over a shop (wall-local; origin on the wall line at the top back edge) ----------------
def twn_roof_pent(k):
    W=3.2; D=1.5; ang=math.radians(22); th=0.08
    y0=-0.18; y1=-0.3-D
    z=lambda y: -(-0.3-y)*math.tan(ang)
    nx=8; ny=4; T=TILE[ROOF]; Wt=TILE[WOOD]
    xs=[-W/2+W*i/nx for i in range(nx+1)]; ys=[y0+(y1-y0)*j/ny for j in range(ny+1)]
    sag=lambda x: -0.03*(0.5-0.5*math.cos(2*math.pi*(x+W/2)/(W/2)))
    top=[[k.bm.verts.new((x,y,z(y)+sag(x)*(abs(y-y0)/D))) for y in ys] for x in xs]
    bot=[[k.bm.verts.new((x,y,z(y)+sag(x)*(abs(y-y0)/D)-th)) for y in ys] for x in xs]
    for i in range(nx):
        for j in range(ny):
            f=k.bm.faces.new((top[i][j+1],top[i+1][j+1],top[i+1][j],top[i][j])); f.material_index=ROOF
            for l in f.loops: l[k.uv].uv=(l.vert.co.x/T,(-(l.vert.co.y-y1)/math.cos(ang))/T+0.12)
            f=k.bm.faces.new((bot[i][j],bot[i+1][j],bot[i+1][j+1],bot[i][j+1])); f.material_index=WOOD
            for l in f.loops: l[k.uv].uv=(l.vert.co.x/Wt,l.vert.co.y/Wt)
        f=k.bm.faces.new((top[i][ny],bot[i][ny],bot[i+1][ny],top[i+1][ny])); f.material_index=WOOD      # front edge
        f=k.bm.faces.new((top[i+1][0],bot[i+1][0],bot[i][0],top[i][0])); f.material_index=WOOD          # back edge
    for i in (0,nx):
        for j in range(ny):
            vs=(top[i][j],bot[i][j],bot[i][j+1],top[i][j+1])
            f=k.bm.faces.new(vs if i==0 else vs[::-1]); f.material_index=WOOD
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index==WOOD and all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],WOOD)
    # scalloped tile edge: the kit's eave tabs moved from the main-roof kick plane onto the pent plane
    sub=Kit(); eave_tabs(sub,-W/2,W/2,-1,rows=2)
    ay=EAVE+0.09-0.46; kz=roof_z(ay)
    ye=y1+0.46*math.cos(ang)-0.05
    M=Matrix.Translation((0,ye,z(ye+0.05)+0.005))@Matrix.Rotation(ang-KICK,4,"X")@Matrix.Translation((0,ay,-kz))
    merge_kit(k,sub,M)
    k.box((0,y1+0.02,z(y1)-0.1),(W+0.04,0.12,0.22),WOOD,bevel=0.03)                          # fascia beam
    for s in(-1,1):                                                                          # curved brackets
        pts=[(-0.28,-0.9),(-0.55,-0.72),(-0.9,-0.56),(-1.22,-0.46)]
        for (ya,za),(yb,zb) in zip(pts[:-1],pts[1:]):
            L=math.hypot(yb-ya,zb-za); a_=math.atan2(zb-za,yb-ya)
            k.box((s*1.2,(ya+yb)/2,(za+zb)/2),(0.14,L+0.06,0.14),WOOD,rot=(a_,0,0),bevel=0.03)
        k.box((s*1.2,-0.3,-0.75),(0.16,0.1,0.5),WOOD,bevel=0.03)
        ym=(-0.3+y1)/2-0.1
        k.box((s*1.2,ym,z(ym)-th-0.07),(0.14,-y1-0.2,0.12),WOOD,rot=(ang,0,0),bevel=0.025)

# ---------------- cart passage (ground wall) + vault ----------------
TWN_PHW=1.2; TWN_PSP=1.4          # passage half width / spring (crown 2.6, ring top 2.97 <= 3.0)

def twn_passage_ring(k,hw,sp,y_front,y_back,n=9,seed=0,out=0.08):
    """the kit arch_ring, slimmed so the keystone top stays under the storey seam (spring+hw+0.37)"""
    rnd=random.Random(seed); r=hw+0.17
    for i in range(n):
        a=math.pi*(i+0.5)/n; ks=(i==n//2)
        rr=r+(0.03 if ks else 0.0); o_=out+(0.07 if ks else 0.0)
        k.box((math.cos(a)*rr,(y_front+y_back)/2-o_/2,sp+math.sin(a)*rr),
              (0.3 if not ks else 0.38,(y_back-y_front)+o_,0.34),STONE_BLOCK,
              rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2,jitter=0.008,seed=seed*10+i)

def twn_wall_stone_passage(k):
    hw=TWN_PHW; sp=TWN_PSP; y0,y1=-0.25,0.25
    twn_panel(k,-1.5,-hw,0,H1,y0,y1); twn_panel(k,hw,1.5,0,H1,y0,y1)
    twn_arch_fill(k,0,hw,sp,H1,y0,y1,STONE,n=12)
    arch_soffit(k,hw,sp,y0,y1,STONE_BLOCK)
    twn_passage_ring(k,hw,sp,y0,0.2,n=9,seed=4)
    for s in(-1,1):
        k.box((s*(hw+0.12),-0.08,sp-0.08),(0.44,0.58,0.16),STONE_BLOCK,bevel=0.03)             # impost
        rock(k,(s*(hw+0.14),-0.1,0.3),(0.5,0.62,0.6),seed=44+s,tilt=0.02)                     # guard stones
    plinth(k,-1.5,-hw-0.02); plinth(k,hw+0.02,1.5); batter(k)
    twn_skirt(k,-1.5,-hw); twn_skirt(k,hw,1.5)
    k.box((0,-0.2,0.02),(2*hw,1.0,0.04),FIELDSTONE,bevel=0)                                   # cobbles
    for s in(-1,1): k.box((s*(hw-0.18),-0.2,0.035),(0.14,1.0,0.03),STONE_BLOCK,bevel=0.01)   # wheel-guide kerbs

def twn_passage_vault(k):
    """barrel vault between the front and back passage walls (house-local y -2.75..2.75)"""
    hw=TWN_PHW; sp=TWN_PSP; Y=2.75
    arch_soffit(k,hw,sp,-Y,Y,STONE,n=14)
    for s in(-1,1):
        grid_cut(k,k.box((s*(hw+0.13),0,(sp+0.45)/2),(0.26,2*Y,sp-0.45),PLASTER,bevel=0))
        k.box((s*(hw+0.1),0,0.225),(0.24,2*Y,0.45),STONE,bevel=0)                          # stone dado
        k.box((s*(hw+0.02),0,sp-0.04),(0.14,2*Y,0.1),STONE_BLOCK,bevel=0.02)                # impost string
    for yy in (-1.6,0.0,1.6):                                                                 # transverse ribs + pilasters
        twn_voussoirs(k,0,hw-0.16,sp,yy-0.15,yy+0.15,n=9,th=0.17,seed=int(yy*10)+30,out=0.0,segs=1,key=1.1)
        for s in(-1,1): k.box((s*(hw-0.05),yy,sp/2),(0.14,0.32,sp),STONE_BLOCK,bevel=0.03)
    k.box((0,0,0.02),(2*hw,2*Y,0.04),FIELDSTONE,bevel=0)
    k.box((0,0,0.041),(0.22,2*Y,0.01),STONE_BLOCK,bevel=0)                                  # central gutter
    twn_skirt(k,-hw-0.25,hw+0.25,-Y,Y)
    # hanging lantern at the crown
    zc=sp+hw
    k.box((0,0.8,zc-0.25),(0.02,0.02,0.5),IRON,bevel=0)
    k.box((0,0.8,zc-0.62),(0.24,0.24,0.3),GLOW,bevel=0.03)
    k.box((0,0.8,zc-0.44),(0.32,0.32,0.06),IRON,bevel=0.015); k.box((0,0.8,zc-0.79),(0.28,0.28,0.05),IRON,bevel=0.015)

# ---------------- timber galleries (first floor walkway along a wall; deck top at H1) ----------------
def twn_gallery(k,end=False):
    Z=H1; y0,y1=-0.2,-1.6; yp=-1.5
    nb=5; bw=(y0-y1)/nb
    for i in range(nb):                                                              # deck boards along x
        k.box((0,y0-bw*(i+0.5),Z-0.04),(3.0-0.01,bw-0.015,0.08),PLANKS,bevel=0.008)
    for x in (-1.125,-0.375,0.375,1.125):
        k.box((x,(y0+y1)/2,Z-0.17),(0.12,y0-y1,0.18),WOOD,bevel=0.02)                     # joists
    k.box((0,yp,Z-0.2),(3.0,0.22,0.26),WOOD,bevel=0.03)                                      # edge beam
    k.box((0,-0.3,Z-0.2),(3.0,0.14,0.22),WOOD,bevel=0.03)                                    # ledger on the wall
    posts=[-1.5]+([1.5] if end else [])
    for px in posts:
        k.box((px,yp,(Z+1.05)/2),(0.22,0.22,Z+1.05),WOOD,bevel=0.035,segs=2)
        k.box((px,yp,Z+1.1),(0.28,0.28,0.1),WOOD,bevel=0.03)
        rock(k,(px,yp,0.1),(0.46,0.46,0.3),seed=int(px*10)+5,tilt=0.02)
        k.box((px,yp,-0.3),(0.36,0.36,0.6),STONE,bevel=0)                                   # skirt
    for s in(-1,1):                                                                         # knee braces
        brace(k,s*1.45,Z-0.95,s*0.75,Z-0.3,w=0.13,y=yp)
    L=math.hypot(1.0,0.7); a=math.atan2(0.7,1.0)
    k.box((-1.5,yp+0.5,Z-0.62),(0.12,L,0.12),WOOD,rot=(a,0,0),bevel=0.02)                   # brace post->wall
    k.box((0,yp-0.02,Z+1.0),(3.0,0.14,0.1),WOOD,bevel=0.025)                                # handrail
    k.box((0,yp-0.02,Z+0.12),(3.0,0.1,0.08),WOOD,bevel=0.02)                                # bottom rail
    for i in range(14):
        x=-1.3+i*0.2
        _cyl(k,(x,yp-0.02,Z+0.56),0.03,0.03,0.8,6,WOOD)
    if end:
        k.box((1.5,(y0+yp)/2,Z+1.0),(0.12,yp-y0,0.1),WOOD,bevel=0.025)
        k.box((1.5,(y0+yp)/2,Z+0.12),(0.1,yp-y0,0.08),WOOD,bevel=0.02)
        for j in range(6): _cyl(k,(1.5,y0-0.1-j*0.2,Z+0.56),0.03,0.03,0.8,6,WOOD)
    # flower pot on the rail
    if end:
        _cyl(k,(0.9,yp-0.02,Z+1.14),0.1,0.13,0.18,10,CLAY)
        for j in range(5): _ico(k,(0.9+0.06*math.cos(j*1.3),yp-0.02+0.06*math.sin(j*1.3),Z+1.3),0.07,PINK if j%2 else LEAF,sub=1)

def twn_gallery_side(k):
    """side rail for the open (left) end of a gallery run; place at the run's left seam"""
    Z=H1; y0=-0.2; yp=-1.5
    k.box((0,(y0+yp)/2,Z+1.0),(0.12,yp-y0,0.1),WOOD,bevel=0.025)
    k.box((0,(y0+yp)/2,Z+0.12),(0.1,yp-y0,0.08),WOOD,bevel=0.02)
    for j in range(6): _cyl(k,(0,y0-0.1-j*0.2,Z+0.56),0.03,0.03,0.8,6,WOOD)

# ---------------- corner turret stack (axis at corner-local (-0.6,-0.6), r 1.1, 12 sides) ----------------
TWN_TC=(-0.6,-0.6); TWN_TR=1.1; TWN_TN=12

def twn_polar(r,a,z):
    return (TWN_TC[0]+math.cos(a)*r,TWN_TC[1]+math.sin(a)*r,z)

def twn_ring_band(k,r_in,r_out,z0,z1,mi,n=TWN_TN):
    lathe(k,[(r_in,z0),(r_out,z0),(r_out,z1),(r_in,z1)],center=(TWN_TC[0],TWN_TC[1],0),segs=n,mi=mi)

def twn_turret_corbel(k):
    c=(TWN_TC[0],TWN_TC[1],0)
    lathe(k,[(0.0,-1.42),(0.12,-1.4),(0.22,-1.22),(0.45,-0.9),(0.7,-0.6),(0.9,-0.3),(1.1,0.0),(0.2,0.0)],center=c,segs=TWN_TN,mi=STONE_BLOCK)
    for (r,z) in ((0.5,-0.9),(0.76,-0.6),(0.97,-0.3)):                                       # moulded rings
        twn_ring_band(k,r-0.1,r+0.05,z-0.05,z+0.05,ASHLAR)
    twn_ring_band(k,0.8,TWN_TR+0.1,-0.02,0.14,STONE_BLOCK)
    _ico(k,(c[0],c[1],-1.5),0.12,STONE_BLOCK,(1,1,1.4),sub=1)

def twn_turret_faces(k,z0,z1,mi,window_idx=(),win=(0.44,0.95,1.0),uv_cyl=False,rmi=WOOD):
    """12-gon wall shell; faces listed in window_idx get a recessed window (w, z_bottom, h)"""
    R=TWN_TR; n=TWN_TN; T=TILE.get(mi,1.0)
    for i in range(n):
        a0=2*math.pi*i/n; a1=2*math.pi*(i+1)/n; am=(a0+a1)/2
        P0=Vector(twn_polar(R,a0,0)); P1=Vector(twn_polar(R,a1,0))
        t=(P1-P0); L=t.length; t.normalize(); nrm=Vector((math.cos(am),math.sin(am),0))
        def pt(u,z,d=0.0): return P0+t*u-nrm*d+Vector((0,0,z))
        def quad(u0,u1,za,zb,m,d=0.0):
            vs=[k.bm.verts.new(pt(u,z,d)) for u,z in ((u0,za),(u1,za),(u1,zb),(u0,zb))]
            f=k.bm.faces.new(vs); f.material_index=m
            for l,(u,z) in zip(f.loops,((u0,za),(u1,za),(u1,zb),(u0,zb))):
                if uv_cyl: l[k.uv].uv=((a0*R+u)/T,z/T)
                else: l[k.uv].uv=(u/T,z/T)
            return f
        if i in window_idx:
            w,wb,wh=win; u0=(L-w)/2; u1=u0+w; wt=wb+wh
            quad(0,L,z0,wb,mi); quad(0,L,wt,z1,mi); quad(0,u0,wb,wt,mi); quad(u1,L,wb,wt,mi)
            gf=quad(u0,u1,wb,wt,WINDOW,d=0.09)
            for l in gf.loops: l[k.uv].uv=(l[k.uv].uv[0]*T,l[k.uv].uv[1]*T)
            for (ua,ub,za,zb) in ((u0,u0,wb,wt),(u1,u1,wb,wt)):
                vs=[k.bm.verts.new(pt(ua,za,0)),k.bm.verts.new(pt(ua,zb,0)),k.bm.verts.new(pt(ua,zb,0.09)),k.bm.verts.new(pt(ua,za,0.09))]
                f=k.bm.faces.new(vs[::-1] if ua==u0 else vs); f.material_index=rmi
            for zz,flip in ((wt,True),(wb,False)):
                vs=[k.bm.verts.new(pt(u0,zz,0)),k.bm.verts.new(pt(u1,zz,0)),k.bm.verts.new(pt(u1,zz,0.09)),k.bm.verts.new(pt(u0,zz,0.09))]
                f=k.bm.faces.new(vs[::-1] if flip else vs); f.material_index=rmi
            yield (i,pt,L,u0,u1,wb,wt,nrm,t)
        else:
            quad(0,L,z0,z1,mi)
    k.bm.normal_update()

def twn_turret_seg(k):
    """timber-framed plaster turret storey (H2): 6 posts, sill/head rings, 3 windows facing -X/-Y"""
    wins=(5,7,9)             # face centres at 165, 225, 285 deg
    for (i,pt,L,u0,u1,wb,wt,nrm,t) in list(twn_turret_faces(k,0.0,H2,PLASTER,window_idx=wins)):
        c=(pt(u0,wb,-0.05)+pt(u1,wb,-0.05))/2
        a=math.atan2(nrm.y,nrm.x)
        k.box(tuple(c+Vector((0,0,-0.06))),(0.2,L+0.02,0.12),WOOD,rot=(0,0,a),bevel=0.02)          # window sill
        c2=(pt(u0,wt,-0.04)+pt(u1,wt,-0.04))/2
        k.box(tuple(c2+Vector((0,0,0.06))),(0.16,L,0.12),WOOD,rot=(0,0,a),bevel=0.02)
        cm=(pt(u0,(wb+wt)/2,0.07)+pt(u1,(wb+wt)/2,0.07))/2
        k.box(tuple(cm),(0.03,0.04,wt-wb),WOOD,rot=(0,0,a),bevel=0.005)
    for i in range(0,TWN_TN,2):                                                               # 6 posts at vertices
        a=2*math.pi*i/TWN_TN
        k.box(twn_polar(TWN_TR+0.02,a,H2/2),(0.17,0.17,H2),WOOD,rot=(0,0,a),bevel=0.03)
    twn_ring_band(k,TWN_TR-0.12,TWN_TR+0.1,0.0,0.2,WOOD)
    twn_ring_band(k,TWN_TR-0.12,TWN_TR+0.08,H2-0.18,H2,WOOD)
    twn_ring_band(k,TWN_TR-0.05,TWN_TR+0.05,0.82,0.9,WOOD)
    for i in (6,8,4,10):                                                                       # braces on plain faces
        a0=2*math.pi*i/TWN_TN; a1=2*math.pi*(i+1)/TWN_TN
        p0=Vector(twn_polar(TWN_TR+0.03,a0,0.95)); p1=Vector(twn_polar(TWN_TR+0.03,a1,H2-0.2))
        if i%4==0: p0,p1=Vector(twn_polar(TWN_TR+0.03,a1,0.95)),Vector(twn_polar(TWN_TR+0.03,a0,H2-0.2))
        d=p1-p0; q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        sub=Kit(); sub.box((0,0,0),(0.12,0.1,d.length),WOOD,bevel=0.02); merge_kit(k,sub,Matrix.Translation((p0+p1)/2)@q)

def twn_turret_seg_stone(k):
    """stone turret storey (H2) with one arrow slit on the diagonal"""
    for (i,pt,L,u0,u1,wb,wt,nrm,t) in list(twn_turret_faces(k,0.0,H2,STONE,window_idx=(7,),win=(0.16,0.9,1.1),uv_cyl=True,rmi=STONE_BLOCK)):
        a=math.atan2(nrm.y,nrm.x)
        for (u,z,w,h) in ((u0-0.13,wb+0.28,0.2,0.56),(u0-0.12,wt-0.26,0.18,0.52),(u1+0.13,wb+0.28,0.2,0.56),(u1+0.12,wt-0.26,0.18,0.52)):
            k.box(tuple(pt(u,z,-0.04)),(0.12,w,h),STONE_BLOCK,rot=(0,0,a),bevel=0.025)
        k.box(tuple((pt(u0,wb-0.08,-0.04)+pt(u1,wb-0.08,-0.04))/2),(0.14,0.52,0.16),STONE_BLOCK,rot=(0,0,a),bevel=0.025)
        k.box(tuple((pt(u0,wt+0.08,-0.04)+pt(u1,wt+0.08,-0.04))/2),(0.14,0.52,0.16),STONE_BLOCK,rot=(0,0,a),bevel=0.025)
    for f in k.bm.faces:
        if f.material_index==WINDOW: f.material_index=VOID
    twn_ring_band(k,TWN_TR-0.1,TWN_TR+0.1,-0.04,0.2,STONE_BLOCK)
    rnd=random.Random(3)
    for j in range(5):                                                                          # pop-out stones
        a=math.radians(rnd.uniform(140,310)); z=rnd.uniform(0.5,2.5)
        if abs(math.degrees(a)-225)<22: continue
        rock(k,twn_polar(TWN_TR+0.02,a,z),(0.08,0.4,0.24),seed=j+3,rot_z=a,tilt=0.02,segs=1)

def twn_turret_cap(k):
    """conical cap r 1.35 x h 2.8 with a bell-cast skirt, finial and bronze ball (origin at the seg top)"""
    n=16; T=TILE[ROOF]; W=TILE[WOOD]; cx,cy=TWN_TC
    Rb=1.35; Hc=2.8; sk=0.32
    prof=[(Rb+sk*math.cos(KICK),-sk*math.sin(KICK)),(Rb,0.0)]+[(Rb*(1-t),Hc*t) for t in (0.25,0.5,0.75,0.93)]
    S=[0.0]
    for j in range(1,len(prof)): S.append(S[-1]+math.hypot(prof[j][0]-prof[j-1][0],prof[j][1]-prof[j-1][1]))
    top=[[k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*r,cy+math.sin(2*math.pi*i/n)*r,z)) for i in range(n+1)] for (r,z) in prof]
    for j in range(len(prof)-1):
        for i in range(n):
            f=k.bm.faces.new((top[j][i],top[j][i+1],top[j+1][i+1],top[j+1][i])); f.material_index=ROOF
            for l in f.loops:
                jj=j if l.vert in top[j] else j+1; ii=top[jj].index(l.vert)
                r=prof[jj][0]; a=2*math.pi*ii/n
                l[k.uv].uv=(a*max(r,0.3)/T,S[jj]/T)
    # merge the seam column (i=n duplicates i=0 positions) is fine: separate UV island
    ra,za=prof[0]
    bot=[k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*ra,cy+math.sin(2*math.pi*i/n)*ra,za-0.1)) for i in range(n+1)]
    inn=[k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*(TWN_TR-0.1),cy+math.sin(2*math.pi*i/n)*(TWN_TR-0.1),0.02)) for i in range(n+1)]
    for i in range(n):
        f=k.bm.faces.new((top[0][i+1],top[0][i],bot[i],bot[i+1])); f.material_index=WOOD        # fascia
        f=k.bm.faces.new((bot[i+1],bot[i],inn[i],inn[i+1])); f.material_index=WOOD              # soffit
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index==WOOD and all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],WOOD)
    zt=prof[-1][1]
    lathe(k,[(Rb*0.07+0.06,zt-0.12),(0.16,zt+0.02),(0.1,zt+0.14),(0.0,zt+0.16)],center=(cx,cy,0),segs=10,mi=ROOF)
    k.box((cx,cy,zt+0.45),(0.1,0.1,0.6),WOOD,bevel=0.025)
    _ico(k,(cx,cy,zt+0.28),0.1,WOOD,(1,1,0.7),sub=1)
    _ico(k,(cx,cy,zt+0.82),0.13,BRONZE,sub=2)
    k.box((cx,cy,zt+1.02),(0.03,0.03,0.3),IRON,bevel=0)

# ---------------- steps ----------------
def twn_prism_xz(k,pts,y0,y1,mi):
    """extrude a convex XZ outline between y0 (front, -Y) and y1"""
    F=[k.bm.verts.new((x,y0,z)) for x,z in pts]; B=[k.bm.verts.new((x,y1,z)) for x,z in pts]
    fs=[k.bm.faces.new(F[::-1]),k.bm.faces.new(B)]
    n=len(pts)
    for i in range(n):
        j=(i+1)%n; fs.append(k.bm.faces.new((F[i],F[j],B[j],B[i])))
    k.bm.normal_update()
    c=Vector((sum(p[0] for p in pts)/n,(y0+y1)/2,sum(p[1] for p in pts)/n))
    for f in fs:
        if f.normal.dot(f.calc_center_median()-c)<0: f.normal_flip()
    k.bm.normal_update(); k.project(fs,mi)
    return fs

def twn_stair_stone_ext(k):
    """stone external stair along a wall (wall-local, outer -Y): 13 steps climbing +X to a landing at z 3.3"""
    rise=H1+0.3; run=2.7; n=13; x0=-1.35; xL=3.65
    y0,yw,y1=-0.22,-1.1,-1.4; h=rise/n; t=run/n
    twn_prism_xz(k,[(x0,0.0),(xL,0.0),(xL,rise-0.28),(x0+run,rise-0.28)],y1,y0,ASHLAR)
    for i in range(n):
        k.box((x0+t*(i+0.5),(y0+yw)/2,(i+1)*h-0.2),(t+0.03,y0-yw,0.4),STONE_BLOCK,bevel=0.025,segs=1,jitter=0.006,seed=i)
    k.box(((x0+run+xL)/2,(y0+y1)/2,rise-0.12),(xL-x0-run,y0-y1,0.24),STONE_BLOCK,bevel=0.03)   # landing slab
    # parapet: sloped band then level along the landing, capped
    twn_prism_xz(k,[(x0,-0.45),(x0+run,rise-0.45),(x0+run,rise+0.72),(x0,0.72)],y1-0.03,yw,ASHLAR)
    twn_prism_xz(k,[(x0+run,rise-0.45),(xL,rise-0.45),(xL,rise+0.72),(x0+run,rise+0.72)],y1-0.03,yw,ASHLAR)
    L=math.hypot(run,rise); a=math.atan2(rise,run)
    k.box((x0+run/2,(yw+y1)/2-0.015,rise/2+0.78),(L+0.1,0.42,0.12),STONE_BLOCK,rot=(0,-a,0),bevel=0.03)
    k.box(((x0+run+xL)/2,(yw+y1)/2-0.015,rise+0.78),(xL-x0-run+0.1,0.42,0.12),STONE_BLOCK,bevel=0.03)
    k.box((xL-0.2,(y0+y1)/2,rise+0.36),(0.4,y0-y1,0.72),ASHLAR,bevel=0)                     # landing end wall
    k.box((xL-0.2,(y0+y1)/2,rise+0.78),(0.42,y0-y1+0.02,0.12),STONE_BLOCK,bevel=0.03)
    k.box((x0-0.12,(yw+y1)/2-0.03,0.5),(0.5,0.5,1.0),STONE_BLOCK,bevel=0.05,segs=2)          # newel
    _ico(k,(x0-0.12,(yw+y1)/2-0.03,1.12),0.17,STONE_BLOCK,sub=1)
    # arched store under the landing
    hw=0.6; sp=0.95; cxa=2.45; yf=y1-0.035
    pts=[(cxa+hw,0.02)]+[(cxa+math.cos(math.pi*i/8)*hw,sp+math.sin(math.pi*i/8)*hw) for i in range(9)]+[(cxa-hw,0.02)]
    vv=[k.bm.verts.new((x,yf-0.005,z)) for x,z in pts]; f=k.bm.faces.new(vv); f.material_index=VOID
    k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    twn_voussoirs(k,cxa,hw,sp,yf-0.03,yf+0.05,n=7,th=0.2,seed=77,out=0.04,segs=1)
    k.box((cxa,yf-0.03,0.06),(2*hw+0.3,0.2,0.12),STONE_BLOCK,bevel=0.02)
    twn_skirt(k,x0-0.4,xL,y1,y0)

def twn_stoop_stone(k):
    """3 dressed steps (rise 0.18, tread 0.35, top 0.54) with cheek blocks, against a wall (outer -Y)"""
    W=1.8
    for j in range(3):
        top=0.18*(3-j); yf=-0.25-0.35*(j+1)
        k.box((0,(yf-0.2)/2,top/2),(W,-yf-0.2,top),STONE_BLOCK,bevel=0.03,segs=1,jitter=0.005,seed=j)
    for s in(-1,1):
        k.box((s*(W/2+0.15),-0.25-0.525,0.3),(0.3,1.05,0.6),STONE_BLOCK,bevel=0.04,segs=2,jitter=0.006,seed=5+s)
        k.box((s*(W/2+0.15),-0.25-0.525,0.62),(0.36,1.1,0.08),STONE_BLOCK,bevel=0.02)
    twn_skirt(k,-W/2-0.3,W/2+0.3,-1.3,-0.2)

def twn_cellar_hatch(k):
    """sloping cellar hatch against a wall (outer -Y): stone curb, two plank leaves with iron straps"""
    W=1.5; ya,yb=-0.22,-1.62; za,zb=0.58,0.12
    z=lambda y: zb+(za-zb)*(y-yb)/(ya-yb)
    # curb as a sloped-top block
    pts=[(ya,0.0),(yb,0.0),(yb,zb),(ya,za)]
    F=[k.bm.verts.new((-W/2,y,zz)) for y,zz in pts]; B=[k.bm.verts.new((W/2,y,zz)) for y,zz in pts]
    fs=[k.bm.faces.new(F),k.bm.faces.new(B[::-1])]
    for i in range(4):
        j=(i+1)%4; fs.append(k.bm.faces.new((F[j],F[i],B[i],B[j])))
    k.bm.normal_update()
    cc=Vector((0,(ya+yb)/2,za/3))
    for f in fs:
        if f.normal.dot(f.calc_center_median()-cc)<0: f.normal_flip()
    k.bm.normal_update(); k.project(fs,STONE)
    ang=math.atan2(za-zb,ya-yb)
    for s in(-1,1):                                                                           # curb stones on the sides
        k.box((s*(W/2-0.06),(ya+yb)/2,(za+zb)/2+0.04),(0.16,math.hypot(ya-yb,za-zb)+0.1,0.14),STONE_BLOCK,rot=(ang,0,0),bevel=0.03)
    k.box((0,yb-0.02,zb-0.02),(W+0.04,0.16,0.18),STONE_BLOCK,bevel=0.03)
    Lh=math.hypot(ya-yb,za-zb)-0.12
    for s in(-1,1):                                                                           # leaves
        cxl=s*(W/2-0.06-0.36)
        M=Matrix.Translation((cxl,(ya+yb)/2,(za+zb)/2+0.07))@Matrix.Rotation(ang,4,"X")
        sub=Kit()
        for b in range(4): sub.box((-0.27+b*0.18,0,0),(0.17,Lh,0.05),PLANKS,bevel=0.008)
        for yy in (-Lh*0.32,Lh*0.32): sub.box((0,yy,0.035),(0.7,0.07,0.02),IRON,bevel=0.006)
        sub.box((-s*0.3,0,0.04),(0.05,0.1,0.03),IRON,bevel=0.005)
        merge_kit(k,sub,M)
    ring(k,(-0.14,(ya+yb)/2,z((ya+yb)/2)+0.13),0.04,0.065,0.02,IRON,n=10,axis="Z")
    twn_skirt(k,-W/2,W/2,yb-0.1,ya)

def twn_hoist_beam(k):
    """hoist beam for a cross-gable face (helper for the merchant house). Origin on the wall line at the wall top;
       the beam leaves the gable triangle (y -0.34) at z 1.42 above the wall top; the rope drops 5.1 m so, on a
       3-storey house (top 8.6), the sack hangs at z ~3.9 in front of the level-1 loading door (rope at x 0, y -1.7)."""
    k.box((0,-1.0,1.42),(0.2,1.56,0.2),WOOD,bevel=0.04,segs=2)                                    # beam
    k.box((0,-1.8,1.42),(0.26,0.06,0.26),WOOD,bevel=0.02)                                         # end cap
    # iron tie from the beam tip back to the king post
    p0=Vector((0,-1.62,1.52)); p1=Vector((0,-0.36,1.88)); d=p1-p0
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    sub=Kit(); sub.box((0,0,0),(0.035,0.035,d.length),IRON,bevel=0); merge_kit(k,sub,Matrix.Translation((p0+p1)/2)@q)
    k.box((0,-0.36,1.88),(0.1,0.06,0.1),IRON,bevel=0.01)
    # pulley block + wheel
    k.box((0,-1.55,1.24),(0.1,0.12,0.18),IRON,bevel=0.015)
    ring(k,(0,-1.55,1.12),0.04,0.15,0.07,WOOD,n=12,axis="X")
    _cyl(k,(0,-1.55,1.12),0.035,0.035,0.14,6,IRON,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # rope (outer fall) + hook + sack
    zr0=1.1; zr1=-4.0
    _cyl(k,(0,-1.7,(zr0+zr1)/2),0.022,0.022,zr0-zr1,6,HAY)
    _cyl(k,(0,-1.4,1.1-0.35),0.022,0.022,0.7,6,HAY)                                                 # inner fall, tied off
    ring(k,(0,-1.7,zr1-0.06),0.03,0.06,0.025,IRON,n=8,axis="X")
    for s in(-1,1):
        p0=Vector((0,-1.7,zr1-0.1)); p1=Vector((s*0.16,-1.7,zr1-0.42)); d=p1-p0
        q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        sub=Kit(); sub.box((0,0,0),(0.03,0.03,d.length),HAY,bevel=0); merge_kit(k,sub,Matrix.Translation((p0+p1)/2)@q)
    _ico(k,(0,-1.7,zr1-0.72),0.3,BURLAP,(0.95,0.8,1.15),sub=2,jit=0.03,seed=3)
    k.box((0,-1.7,zr1-0.4),(0.3,0.24,0.06),BURLAP,bevel=0.02)

# =============================== builders ===============================
def twn_demo_paving(coll,x0,x1,y0,y1,name="WS_town_DemoPaving"):
    """stand-in cobbled street slab for demo renders only (not a kit piece; terrain replaces it)"""
    old=bpy.data.objects.get(name)
    if old and coll in old.users_collection: bpy.data.objects.remove(old)
    k=Kit(); k.box(((x0+x1)/2,(y0+y1)/2,0.0),(x1-x0,y1-y0,0.06),FIELDSTONE,bevel=0)
    return k.finish(name,coll,wobble=False,grime=False)

def twn_clear_assembly(asm):
    """empty the assembly and drop the style-variant meshes (VAR_*) of OUR pieces that it used, so a rebuilt
       piece is not shadowed by a stale cached variant. Never touches variants of kit / other agents' pieces."""
    mine={n for n,_,_ in WS_SPECS}; stale=set()
    for o in list(asm.objects):
        if o.type=="MESH" and o.data.name.startswith("VAR_") and o.name.split("_inst")[0] in mine: stale.add(o.data.name)
        bpy.data.objects.remove(o)
    for vn in stale:
        me=bpy.data.meshes.get(vn)
        if me and me.users==0: bpy.data.meshes.remove(me)

TWN_FAM={
 "Stone":{".":"SM_VK_Wall_Stone","W":"SM_VK_Wall_Stone_Window","D":"SM_VK_Wall_Stone_Door","S":"SM_VK_Wall_Stone_Shop","P":"SM_VK_Wall_Stone_Passage","C":"SM_VK_Corner_Stone","I":"SM_VK_InnerCorner_Stone"},
 "Plaster":{".":"SM_VK_Wall_Plaster","W":"SM_VK_Wall_Plaster_Window","D":"SM_VK_Wall_Plaster_Door","S":"SM_VK_Wall_Plaster_Shop","P":"SM_VK_Wall_Stone_Passage","C":"SM_VK_Corner_Plaster","I":"SM_VK_InnerCorner_Plaster"},
 "Timber":{".":"SM_VK_Wall_Timber","W":"SM_VK_Wall_Timber_Window","O":"SM_VK_Wall_Timber_Oriel","D":"SM_VK_Wall_Timber_Door","C":"SM_VK_Corner_Timber","I":"SM_VK_InnerCorner_Timber"},
 "PlasterUp":{".":"SM_VK_Wall_PlasterUp","W":"SM_VK_Wall_PlasterUp_Window","O":"SM_VK_Wall_PlasterUp_Oxeye","D":"SM_VK_Wall_PlasterUp_Window","C":"SM_VK_Corner_PlasterUp","I":"SM_VK_InnerCorner_PlasterUp"},
 "StoneUp":{".":"SM_VK_Wall_StoneUp","W":"SM_VK_Wall_StoneUp_Window","T":"SM_VK_Wall_StoneUp_Twin","X":"SM_VK_Wall_StoneUp_Slit","L":"SM_VK_Wall_StoneUp_Loading","D":"SM_VK_Wall_StoneUp_Door","O":"SM_VK_Wall_StoneUp_Twin","C":"SM_VK_Corner_StoneUp","I":"SM_VK_InnerCorner_StoneUp"},
}
TWN_GOODS=["Bread","Produce","Cloth","Pots","Tools","Meat","Candles","Fish"]
TWN_SIGN={"Bread":"SM_VK_Prop_BakerySign","Tools":"SM_VK_Prop_Sign","Candles":"SM_VK_Sign_Potion","Pots":"SM_VK_Sign_Potion","Cloth":"SM_VK_Prop_Sign"}

def twn_lvz(lv): return 0.0 if lv==0 else H1+H2*(lv-1)
def twn_top(storeys): return H1+H2*(storeys-1)

def twn_piece(fam,c,r):
    if fam=="Timber" and c==".": return r.choice(["SM_VK_Wall_Timber","SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K"])
    t=TWN_FAM[fam]
    return t.get(c,t["W"] if c in "WTOL" else t["."])

def twn_placer(coll,origin,style):
    def P(n,x,y,z,rot,st=None):
        if not n or not bpy.data.objects.get(n): return None
        return place_v(coll,n,x,y,z,rot,origin,style if st is None else st)
    return P

def twn_wl(x,y,rot,lx,ly):
    """wall-local offset -> block coords"""
    a=math.radians(rot); return (x+lx*math.cos(a)-ly*math.sin(a),y+lx*math.sin(a)+ly*math.cos(a))

def twn_dress_wall(P,x,y,rot,lv,fam,c,r,goods=None,pent=True,stone_up=False,lamp=True):
    """props that belong to one wall module (wall-local placement)"""
    z=twn_lvz(lv)
    if lv==0 and c=="S":
        gk=goods or r.choice(TWN_GOODS)
        gx,gy=twn_wl(x,y,rot,0,-0.55); P("SM_VK_Prop_ShopGoods_"+gk,gx,gy,TWN_CZ,rot,{})
        if pent: P("SM_VK_Roof_Pent",x,y,3.35,rot)
        sx,sy=twn_wl(x,y,rot,1.3,-0.25)
        if not pent: P(TWN_SIGN.get(gk,"SM_VK_Prop_Sign"),sx,sy,3.3,rot,{})
        return gk
    if lv==0 and c=="D":
        if lamp: lx,ly=twn_wl(x,y,rot,1.05,-0.3); P("SM_VK_Prop_Lantern",lx,ly,2.55,rot,{})
        if r.random()<0.5:
            px,py=twn_wl(x,y,rot,-1.05,-0.75); P("SM_VK_Prop_Planter",px,py,0,rot,{})
    if lv==0 and c=="W" and r.random()<0.75:
        fx,fy=twn_wl(x,y,rot,0,-0.55 if fam=="Stone" else -0.5)
        P("SM_VK_Prop_FlowerBox" if r.random()<0.6 else "SM_VK_Prop_FlowerBox_Daisy",fx,fy,0.78 if fam=="Stone" else 0.9,rot,{})
    if lv>0 and c=="W" and fam in ("StoneUp","PlasterUp") and r.random()<0.45:
        fx,fy=twn_wl(x,y,rot,0,-0.62)
        P("SM_VK_Prop_FlowerBox" if r.random()<0.5 else "SM_VK_Prop_FlowerBox_Daisy",fx,fy,z+(0.55 if fam=="StoneUp" else 0.6),rot,{})
    if lv==0 and c in ".W" and r.random()<0.35:
        P("SM_VK_Deco_Weeds",x,y,0,rot,{})
    return None

def twn_box_house(P,xc,n,levels,F,B,Lf,Rf,r,ends=(True,True),dress=True,goods=(),pent_skip=(),corners=True,back_lamps=True):
    """rectangular block n cells long (local X) x 2 deep, centred at xc.
       levels: wall family per level (bottom first); F/B: strings per level (n chars, read from outside);
       Lf/Rf: 2-char strings per level for the end walls (None = no end wall on that level).
       back_lamps=False drops the door lanterns on the back (+Y) ground walls (e.g. under a gallery)."""
    L=n*CELL; x0=xc-L/2; gi=list(goods)
    walls=[]
    for lv,fam in enumerate(levels):
        z=twn_lvz(lv)
        for i in range(n):
            x=x0+1.5+3*i
            if F and F[lv]: walls.append((x,-3,0,lv,fam,F[lv][i]))
            if B and B[lv]: walls.append((x,3,180,lv,fam,B[lv][n-1-i]))
        if ends[0] and Lf and Lf[lv]:
            for j,yy in enumerate((1.5,-1.5)): walls.append((x0,yy,-90,lv,fam,Lf[lv][j]))
        if ends[1] and Rf and Rf[lv]:
            for j,yy in enumerate((-1.5,1.5)): walls.append((x0+L,yy,90,lv,fam,Rf[lv][j]))
        if corners:
            cs=[]
            if ends[0] and Lf and Lf[lv]: cs+=[(x0,-3,0),(x0,3,-90)]
            if ends[1] and Rf and Rf[lv]: cs+=[(x0+L,-3,90),(x0+L,3,180)]
            for (cx,cy,cr) in cs: P(TWN_FAM[fam]["C"],cx,cy,z,cr)
    for (x,y,rot,lv,fam,c) in walls:
        if c=="-": continue
        P(twn_piece(fam,c,r),x,y,twn_lvz(lv),rot)
        if dress:
            g_=twn_dress_wall(P,x,y,rot,lv,fam,c,r,goods=(gi.pop(0) if (gi and lv==0 and c=="S") else None),pent=(x,y) not in pent_skip,
                              lamp=back_lamps or rot!=180)
    return walls

def twn_roof_row(P,xc,n,top,left,right,mid="SM_VK_Roof_Mid",over=None):
    """roof bays along X: left/right = end piece names (None -> Roof_Mid). over: {bay: piece}"""
    L=n*CELL; x0=xc-L/2
    for i in range(n):
        x=x0+1.5+3*i
        if over and i in over: pc,rt=over[i],0
        elif n==1: pc,rt=(right or left or mid),0
        elif i==0: pc,rt=(left or mid),180 if left else 0
        elif i==n-1: pc,rt=(right or mid),0
        else: pc,rt=mid,0
        P(pc,x,0,top,rt)

def twn_turret_stack(P,cx,cy,rot,z0,top,stone=False,style=None):
    """corbel at the first upper floor, one segment per upper storey + one above the wall top, cap"""
    seg="SM_VK_Turret_Seg_Stone" if stone else "SM_VK_Turret_Seg"
    P("SM_VK_Turret_Corbel",cx,cy,z0,rot)
    z=z0
    while z<top+H2-0.01:
        P(seg,cx,cy,z,rot); z+=H2
    P("SM_VK_Turret_Cap",cx,cy,z,rot)
    return z

def build_merchant_house(coll,origin,seed=0):
    """Stone merchant house (T4): 3x2 cells, Stone + 2 x StoneUp (wall top 8.6), slate roof with stepped gables,
       shops + stacked loading doors to the street (-Y), external stone stair and walled 3x1 yard behind (+Y)."""
    r=random.Random(seed)
    st={"roof":"Slate","stone":r.choice(["Rubble","Warm","Cool"]),"shutter":r.choice(["Red","Blue","Green","Teal"]),"seed":seed}
    P=twn_placer(coll,origin,st)
    n=3; levels=["Stone","StoneUp","StoneUp"]; top=twn_top(3)
    F=["SDS","TLT","WLW"]; B=["..W",".DW","W.W"]
    Lf=[".W","WX","T."]; Rf=["W.",".W",".T"]
    goods=r.sample(TWN_GOODS,2)
    turret=r.random()<0.5 or seed==0
    twn_box_house(P,0,n,levels,F,B,Lf,Rf,r,goods=goods,pent_skip={(-3,-3)} if turret else set())
    stepped=twn_pick("SM_VK_Roof_Gable_Stepped","SM_VK_Roof_Gable_Stone")
    cross=twn_pick("SM_VK_Roof_CrossGable_Hoist",twn_pick("SM_VK_Roof_CrossGable","SM_VK_Roof_Mid"))
    twn_roof_row(P,0,n,top,stepped,stepped,over={1:cross})
    if cross=="SM_VK_Roof_CrossGable": P("SM_VK_Prop_HoistBeam",0,-3,top,0,{})     # rope over the stacked loading doors
    P("SM_VK_Chimney",-3,0,top,180)
    if turret: twn_turret_stack(P,-4.5,-3,0,H1,top,stone=True)
    # back: stone stair from bay j=0 (x=+3) up to the door in bay j=1 (x=0), cellar hatch under the window of j=2
    P("SM_VK_Stair_Stone_Ext",3,3,0,180,{})
    P("SM_VK_Prop_CellarHatch",-3,3,0,180,{})
    # walled yard 3x1 behind
    for x in (-3.0,3.0): P("SM_VK_LowWall",x,6.0,0,0,{})
    for yy in (4.5,): P("SM_VK_LowWall",-4.5,yy,0,90,{}); P("SM_VK_LowWall",4.5,yy,0,90,{})
    for (x,y) in ((-4.5,6.0),(4.5,6.0),(-1.5,6.0),(1.5,6.0)): P("SM_VK_LowWall_Post",x,y,0,0,{})
    P("SM_VK_Prop_BarrelStack",-2.5,4.85,0,180,{})
    P("SM_VK_Prop_Crates",-3.6,4.55,0,15,{}); P("SM_VK_Prop_Sacks",-1.4,4.9,0,30,{})
    P("SM_VK_Prop_Sign",-1.05,-3.25,2.85,0,{})
    return dict(footprint=(3,2),lot=(3,3),wall_top=top)

def build_townhouse_gablefront(coll,origin,seed=0):
    """Gable-front townhouse (T3): 3 cells deep x 2 wide, Plaster + 2 x Timber (wall top 8.6); the 6 m gable faces
       the street (-Y in the builder frame): shop + door, oriel, hoist gable. Keep one empty cell to each neighbour."""
    r=random.Random(seed+101)
    st={"roof":r.choice(["Red","Green","Shingle"]),"plaster":r.choice(["Cream","Ochre","Rose","White","Sage"]),
        "shutter":r.choice(["Teal","Red","Green","Blue"]),"seed":seed}
    ox,oy,orz=origin
    P=twn_placer(coll,(ox,oy,orz-math.pi/2),st)            # block X (length) -> street at the R end = -Y
    n=3; levels=["Plaster","Timber","Timber"]; top=twn_top(3)
    F=["W.W","W.W","..W"]; B=["WD.","W.W","W.."]
    Lf=[".W","W.","W."]; Rf=["SD","OW","WW"]
    goods=[r.choice(TWN_GOODS)]
    twn_box_house(P,0,n,levels,F,B,Lf,Rf,r,goods=goods,pent_skip=set())
    hoist=twn_pick("SM_VK_Roof_Gable_Hoist","SM_VK_Roof_Gable_Planks")
    twn_roof_row(P,0,n,top,"SM_VK_Roof_Gable",hoist)
    P("SM_VK_Chimney",-3,0,top,0)
    em=[o for o in ("SM_VK_Emblem_Ridge_Key","SM_VK_Emblem_Ridge_Pretzel","SM_VK_Emblem_Ridge_Tankard") if bpy.data.objects.get(o)]
    if em: P(r.choice(em),4.5+0.95+0.08,0,top+RIDGE+0.9,0,{})
    kind=goods[0]
    P(TWN_SIGN.get(kind,"SM_VK_Prop_Sign"),4.5,0.35,3.0,90,{})
    P("SM_VK_Prop_Planter",5.25,2.75,0,90,{}); P("SM_VK_Prop_BarrelStack",2.8,-4.1,0,0,{})
    return dict(footprint=(2,3),lot=(4,3),wall_top=top)

def build_corner_house(coll,origin,seed=0):
    """Corner house (T3-4): L-plan (junction 2x2 + 1 cell on each wing), Stone + 2 x Timber (wall top 8.6),
       one shop on each street face (-Y and -X) and a plaster turret on the convex corner (tip 14.2)."""
    r=random.Random(seed+202)
    st={"roof":r.choice(["Red","Green","Slate"]),"plaster":r.choice(["Cream","White","Ochre","Sky"]),
        "shutter":r.choice(["Teal","Red","Blue"]),"stone":r.choice(["Rubble","Warm"]),"seed":seed}
    P=twn_placer(coll,origin,st)
    levels=["Stone","Timber","Timber"]; top=twn_top(3); a=1; b=1; XA=3+3*a; YB=3+3*b
    g=r.sample(TWN_GOODS,2)
    # (x, y, rot, chars per level) ; street faces: A front (-Y) and B outer side (-X)
    runs=[(-1.5,-3,0,"SWW"),(1.5,-3,0,"DOW"),(4.5,-3,0,"WWW"),
          (-3,-1.5,-90,"SWW"),(-3,1.5,-90,"WOW"),(-3,4.5,-90,".W."),
          (XA,-1.5,90,"WW."),(XA,1.5,90,".W."),(4.5,3,180,"WDW"),
          (-1.5,YB,180,".W."),(1.5,YB,180,"DW."),(3,4.5,90,"WW.")]
    gi=list(g)
    for (x,y,rot,cs) in runs:
        for lv,fam in enumerate(levels):
            c=cs[lv]
            P(twn_piece(fam,c,r),x,y,twn_lvz(lv),rot)
            if lv==0 and c=="S":
                twn_dress_wall(P,x,y,rot,0,fam,c,r,goods=gi.pop(0),pent=False)
            else: twn_dress_wall(P,x,y,rot,lv,fam,c,r)
    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    for lv,fam in enumerate(levels):
        for (cx,cy,cr) in corners: P(TWN_FAM[fam]["C"],cx,cy,twn_lvz(lv),cr)
        P(TWN_FAM[fam]["I"],3,3,twn_lvz(lv),0)
    P("SM_VK_Roof_LCorner",0,0,top,0)
    P("SM_VK_Roof_Gable",4.5,0,top,0); P("SM_VK_Roof_Gable",0,4.5,top,90)
    P("SM_VK_Chimney",4.5,0,top,180)
    twn_turret_stack(P,-3,-3,0,H1,top,stone=False)
    ban=twn_pick("SM_VK_Banner_Wall",None)
    if ban: P(ban,-3.0,-0.9,H1+H2,-90,{"cloth":"Red"})
    P("SM_VK_Prop_LampPost",-4.6,-4.9,0,45,{})
    # first-floor gallery in the inner yard (A back wall), open end closed with a side rail
    P("SM_VK_Gallery_Timber",4.5,3,0,180); P("SM_VK_Gallery_Side",6.0,3,0,180)
    P("SM_VK_Prop_BarrelStack",4.6,5.4,0,90,{}); P("SM_VK_Prop_Woodpile",5.4,7.6,0,90,{})
    return dict(footprint=(3,3),lot=(4,4),wall_top=top)

def build_terrace(coll,origin,units=4,seed=0):
    """Rowhouse terrace (T3): `units` houses along +X, fronts to the street (-Y). Varied widths (1-3 cells),
       storeys (2-4), families and colours; shops with pents, a cart passage + vault, stepped heights with gable
       ends against lower neighbours, party chimneys / firewalls on equal-height boundaries."""
    r=random.Random(seed+303)
    plasters=["Cream","White","Ochre","Rose","Sage","Sky"]
    roofs=["Red","Slate","Shingle","Red","Slate","Shingle","Green","Blue"]          # no 'field of orange wedges'
    U=[]; prev=None
    for u in range(units):
        w=r.choices([1,2,3],[.2,.5,.3])[0]
        s=r.choices([2,3,4],[.25,.5,.25])[0]
        if prev and s==prev["s"] and r.random()<0.6: s=max(2,min(4,s+r.choice((-1,1))))
        ground=r.choices(["Stone","Plaster"],[.55,.45])[0]
        upper=r.choices(["Timber","PlasterUp","StoneUp"],[.45,.35,.2] if ground=="Stone" else [.55,.45,0])[0]
        pl=r.choice([p for p in plasters if not prev or p!=prev["st"]["plaster"]])
        rf=r.choice(roofs)
        if prev and rf==prev["st"]["roof"] and r.random()<0.5: rf=r.choice(roofs)
        st={"plaster":pl,"shutter":r.choice(["Teal","Red","Green","Blue","Natural"]),"roof":rf,
            "stone":r.choice(["Rubble","Warm","Cool"]),"seed":seed*10+u}
        U.append(dict(w=w,s=s,g=ground,u=upper,st=st)); prev=U[-1]
    # a 1-cell unit may not need two gable ends
    for i,un in enumerate(U):
        lo_l=(i==0) or U[i-1]["s"]<un["s"]; lo_r=(i==units-1) or U[i+1]["s"]<un["s"]
        if un["w"]==1 and lo_l and lo_r: un["w"]=2
    total=sum(un["w"] for un in U)*CELL; x=-total/2
    for un in U: un["x0"]=x; x+=un["w"]*CELL
    pu=[i for i in range(units) if i%4==3 and U[i]["w"]>=2]
    if not pu:
        cand=[i for i in range(units) if U[i]["w"]>=2]
        pu=cand[-1:] if cand else []
    street_end=lambda: r.choices(["stepped","flush","gable","halfhip"],[.3,.3,.2,.2])[0]
    endpiece={"stepped":twn_pick("SM_VK_Roof_Gable_Stepped","SM_VK_Roof_Gable_Stone"),
              "flush":twn_pick("SM_VK_Roof_Gable_Flush","SM_VK_Roof_Gable_Stone"),
              "gable":"SM_VK_Roof_Gable","halfhip":twn_pick("SM_VK_Roof_HalfHip","SM_VK_Roof_Hip")}
    for i,un in enumerate(U):
        P=twn_placer(coll,origin,un["st"]); n=un["w"]; xc=un["x0"]+n*CELL/2
        levels=[un["g"]]+[un["u"]]*(un["s"]-1)
        # ground string: S .45 / D .3 / W .25, at least one D; every 4th unit (w>=2) gets a passage
        gs=[r.choices("SDW",[.45,.3,.25])[0] for _ in range(n)]
        if "D" not in gs: gs[r.randrange(n)]="D"
        if i in pu:
            k_=[j for j in range(n) if gs[j]!="D"] or [0]
            gs[k_[0]]="P"
            if "D" not in gs: gs[(k_[0]+1)%n]="D"
        up=lambda: "".join(r.choice("WW.O" if un["u"]!="StoneUp" else "WWT.") for _ in range(n))
        F=["".join(gs)]+[up() for _ in range(un["s"]-1)]
        B=["".join(("P" if gs[n-1-j]=="P" else r.choice("W.D" if j==0 else "W.")) for j in range(n))]+["".join(r.choice("W..") for _ in range(n)) for _ in range(un["s"]-1)]
        # ends: street end -> all levels; boundary with a lower neighbour -> only the levels above it
        def end_levels(nb):
            if nb is None: return list(range(un["s"]))
            return list(range(nb["s"],un["s"]))
        Ln=U[i-1] if i>0 else None; Rn=U[i+1] if i<units-1 else None
        Lv=end_levels(Ln); Rv=end_levels(Rn)
        Lf=[(("W." if lv>0 else ".W") if lv in Lv else None) for lv in range(un["s"])]
        Rf=[((".W" if lv>0 else "W.") if lv in Rv else None) for lv in range(un["s"])]
        # back gallery on timber units (never on two neighbours, never over a passage)
        gal=(un["u"]=="Timber" and n>=2 and "P" not in gs and not (i>0 and U[i-1].get("gal")) and r.random()<0.45)
        un["gal"]=gal
        if gal:
            b1=list(B[1]); b1[r.randrange(n)]="D"; B[1]="".join(b1)
        twn_box_house(P,xc,n,levels,F,B,Lf,Rf,r,ends=(True,True),corners=True,back_lamps=not gal)
        if gal:
            for j in range(n):
                P("SM_VK_Gallery_End" if j==0 else "SM_VK_Gallery_Timber",un["x0"]+1.5+3*j,3,0,180)
            P("SM_VK_Gallery_Side",un["x0"]+n*CELL,3,0,180)
        # party pilasters where the neighbour differs on a shared level
        if Ln:
            for lv in range(min(un["s"],Ln["s"])):
                fa=levels[lv]; fb=([Ln["g"]]+[Ln["u"]]*3)[lv]
                if fa!=fb or Ln["st"]["plaster"]!=un["st"]["plaster"]:
                    pc=TWN_FAM[fa]["C"] if fa!="Timber" else (TWN_FAM[fb]["C"] if fb!="Timber" else None)
                    if pc:
                        P(pc,un["x0"],-3,twn_lvz(lv),0); P(pc,un["x0"],3,twn_lvz(lv),-90)
        # roof
        top=twn_top(un["s"])
        def end_kind(nb,side):
            if nb is None: return endpiece[street_end()]
            if nb["s"]<un["s"]: return endpiece["flush"]
            if nb["s"]>un["s"]: return twn_pick("SM_VK_Roof_Mid_Cap"+side,"SM_VK_Roof_Mid")
            return "SM_VK_Roof_Mid"
        lk=end_kind(Ln,"L"); rk=end_kind(Rn,"R")
        L=n*CELL; x0=un["x0"]
        for b in range(n):
            xb=x0+1.5+3*b
            if n==1:
                pc,rt=(lk,180) if lk!="SM_VK_Roof_Mid" and not lk.startswith("SM_VK_Roof_Mid_Cap") else (rk,0)
            elif b==0: pc,rt=lk,(180 if lk not in ("SM_VK_Roof_Mid",) else 0)
            elif b==n-1: pc,rt=rk,0
            else: pc,rt="SM_VK_Roof_Mid",0
            if pc.startswith("SM_VK_Roof_Mid_Cap"): rt=0
            P(pc,xb,0,top,rt)
        # boundary with an equal-height right neighbour: firewall (even) or party chimney (odd)
        if Rn and Rn["s"]==un["s"]:
            xbd=x0+L
            if (i%2==0) or Rn["st"]["roof"]!=un["st"]["roof"]:
                fw=twn_pick("SM_VK_Roof_Firewall",None)
                if fw: P(fw,xbd,0,top,0,{})
                else: P("SM_VK_Chimney",xbd,0,top,0)
            else:
                cp=twn_pick("SM_VK_Chimney_Party",None)
                if cp: P(cp,xbd,0,top+RIDGE,0,{})
                else: P("SM_VK_Chimney",xbd,0,top,180)
        elif r.random()<0.6:
            P("SM_VK_Chimney",x0+1.5+3*r.randrange(n),0,top,r.choice((0,180)))
        # passage vault behind any P
        for j,c in enumerate(gs):
            if c=="P": P("SM_VK_Passage_Vault",x0+1.5+3*j,0,0,0,{})
        ban=twn_pick("SM_VK_Banner_Wall",None)
        if ban and i%2==1: P(ban,x0+0.4,-3,H1+H2,0,{})
    return dict(footprint=(int(total/CELL),2),units=U)

# ================================ specs ================================
twn_fw=dict(wobble=False,grime=False)
twn_nw=dict(wobble=False,grime=False)
twn_ng=dict(wobble=False,grime=True)
WS_SPECS=[
 ("SM_VK_Wall_StoneUp",twn_wall_stoneup,twn_fw),
 ("SM_VK_Wall_StoneUp_Window",twn_wall_stoneup_window,twn_fw),
 ("SM_VK_Wall_StoneUp_Twin",twn_wall_stoneup_twin,twn_fw),
 ("SM_VK_Wall_StoneUp_Slit",twn_wall_stoneup_slit,twn_fw),
 ("SM_VK_Wall_StoneUp_Loading",twn_wall_stoneup_loading,twn_fw),
 ("SM_VK_Wall_StoneUp_Door",twn_wall_stoneup_door,twn_fw),
 ("SM_VK_Corner_StoneUp",twn_corner_stoneup,twn_nw),
 ("SM_VK_InnerCorner_StoneUp",twn_inner_corner_stoneup,twn_nw),
 ("SM_VK_Wall_PlasterUp",twn_wall_plasterup,twn_fw),
 ("SM_VK_Wall_PlasterUp_Window",twn_wall_plasterup_window,twn_fw),
 ("SM_VK_Wall_PlasterUp_Oxeye",twn_wall_plasterup_oxeye,twn_fw),
 ("SM_VK_Corner_PlasterUp",twn_corner_plasterup,twn_nw),
 ("SM_VK_InnerCorner_PlasterUp",twn_inner_corner_plasterup,twn_nw),
 ("SM_VK_Wall_Stone_Shop",twn_wall_stone_shop,{}),
 ("SM_VK_Wall_Plaster_Shop",twn_wall_plaster_shop,{}),
 ("SM_VK_Prop_ShopGoods_Bread",twn_goods_bread,twn_ng),
 ("SM_VK_Prop_ShopGoods_Produce",twn_goods_produce,twn_ng),
 ("SM_VK_Prop_ShopGoods_Cloth",twn_goods_cloth,twn_ng),
 ("SM_VK_Prop_ShopGoods_Pots",twn_goods_pots,twn_ng),
 ("SM_VK_Prop_ShopGoods_Tools",twn_goods_tools,twn_ng),
 ("SM_VK_Prop_ShopGoods_Meat",twn_goods_meat,twn_ng),
 ("SM_VK_Prop_ShopGoods_Candles",twn_goods_candles,twn_ng),
 ("SM_VK_Prop_ShopGoods_Fish",twn_goods_fish,twn_ng),
 ("SM_VK_Roof_Pent",twn_roof_pent,twn_nw),
 ("SM_VK_Wall_Stone_Passage",twn_wall_stone_passage,{}),
 ("SM_VK_Passage_Vault",twn_passage_vault,twn_ng),
 ("SM_VK_Gallery_Timber",lambda k: twn_gallery(k,False),twn_nw),
 ("SM_VK_Gallery_End",lambda k: twn_gallery(k,True),twn_nw),
 ("SM_VK_Gallery_Side",twn_gallery_side,twn_nw),
 ("SM_VK_Turret_Corbel",twn_turret_corbel,twn_nw),
 ("SM_VK_Turret_Seg",twn_turret_seg,twn_nw),
 ("SM_VK_Turret_Seg_Stone",twn_turret_seg_stone,twn_nw),
 ("SM_VK_Turret_Cap",twn_turret_cap,twn_nw),
 ("SM_VK_Stoop_Stone",twn_stoop_stone,twn_ng),
 ("SM_VK_Stair_Stone_Ext",twn_stair_stone_ext,twn_ng),
 ("SM_VK_Prop_CellarHatch",twn_cellar_hatch,twn_ng),
 ("SM_VK_Prop_HoistBeam",twn_hoist_beam,twn_nw),
]
EXTRA_SPECS+=WS_SPECS
