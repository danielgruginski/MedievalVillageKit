# ===================== VK TERRAIN QUAY : harbour-wall tiles for the dual-grid terrain =====================
# Executed after vk_terrain in the kit namespace (vk_kit TERRAIN_TEXTS). Where land cells flagged G.quay stand one level
# above sea cells (water), tk_tiles puts a Quay tile on the land's layer instead of a Shore at the sea's level plus a
# Cliff layer: a dressed-stone sea wall standing on the cell edge, its coping a kerb above the land, its face down to the
# sea bed. Tile frame as a cliff layer's: land top z 0, the sea cell's level -1.5, its water QY_WATER -2.1 (WATER_Z below
# its level), its bed QY_BED -3.0 (= SKIRT_Z: a layer's skirt). Slot 0 M_VK_Terrain (the land behind the coping and
# the sea bed: the map's ground), slot 1 M_VKT_Stair (object space, no UVs, so it survives the terrain merge: TCol G 1
# dressed stone for the coping, wall and steps, G 0 its cobbles for the slipway; TCol R AO darkens the tide band and the
# wet stone under the water). G.quay on a land cell: 1 wall, 2 water stairs, 3 slipway (an Edge vertex whose two
# land cells both carry 2 or 3 gets the stairs or the slip).
QY_COP=0.08        # coping top above the land (a kerb)
QY_CD=0.6          # coping depth behind the face
QY_OV=0.07         # coping overhang in front of the face
QY_CB=-0.22        # coping bottom (the face starts under it)
QY_WATER=-TIER+WATER_Z
QY_BED=SKIRT_Z
QY_COURSES=(QY_CB,-0.66,-1.1,-1.54,-1.98,-2.42,QY_BED)   # the face's courses (the AO reads by height)
QY_RELIEF=0.012    # every other course stands this proud: the stone's horizontal joints
QY_QUAD={"NE":(1,1),"NW":(-1,1),"SW":(-1,-1),"SE":(1,-1)}
# half-lines from the tile centre: direction, the quadrant on its left (z x dir), the one on its right
QY_HALF={"N":((0,1),"NW","NE"),"S":((0,-1),"SE","SW"),"E":((1,0),"NE","SE"),"W":((-1,0),"SW","NW")}
QY_OF={"NE":("N","E"),"NW":("N","W"),"SW":("S","W"),"SE":("S","E")}     # each quadrant's two centre half-lines
QY_OPP={"NE":"SW","SW":"NE","NW":"SE","SE":"NW"}
QY_SLIP_N=Vector((0,-0.45,1)).normalized()

def qy_tc(z,stone=1.0):
    """TCol: AO 1 above the tide line, darkening through the band at the water to the wet stone under it; A wet"""
    if z>=-1.6: ao=1.0
    elif z>=-2.1: ao=1.0-0.5*(-1.6-z)/0.5
    else: ao=0.5
    return (ao,stone,0.0,1.0 if z<-1.7 else 0.0)

def qy_poly(tb,pts,n,mi=1,tc=None,stone=1.0):
    """flat polygon facing n (its winding follows n); TCol by each vertex's height (qy_tc) unless tc is given"""
    n=Vector(n).normalized(); P=[Vector(p) for p in pts]; nn=Vector((0.0,0.0,0.0))
    for i in range(len(P)):                                   # Newell normal of the winding as given
        a,b=P[i],P[(i+1)%len(P)]
        nn+=Vector(((a.y-b.y)*(a.z+b.z),(a.z-b.z)*(a.x+b.x),(a.x-b.x)*(a.y+b.y)))
    if nn.dot(n)<0: P=P[::-1]
    ids=[tb.vert(tuple(p)) for p in P]
    tb.face(ids,[tuple(n)]*len(P),[tc if tc is not None else qy_tc(p.z,stone) for p in P],mi)

def qy_box(tb,a,b,mi=1,tc=None):
    """axis box between corners a and b; an end lying on the tile's side is left out (the neighbour's stone covers
       it)"""
    x0,x1=sorted((a[0],b[0])); y0,y1=sorted((a[1],b[1])); z0,z1=sorted((a[2],b[2]))
    F={"-x":((x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)),"+x":((x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)),
       "-y":((x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)),"+y":((x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)),
       "-z":((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)),"+z":((x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))}
    N={"-x":(-1,0,0),"+x":(1,0,0),"-y":(0,-1,0),"+y":(0,1,0),"-z":(0,0,-1),"+z":(0,0,1)}
    for key,pts in F.items():
        if key[1]=="x" and abs(abs(pts[0][0])-1.5)<1e-6: continue
        if key[1]=="y" and abs(abs(pts[0][1])-1.5)<1e-6: continue
        qy_poly(tb,pts,N[key],mi,tc)

def qy_jit(x,y,k=0):
    """a coping stone's height wobble (+-8 mm), fixed by its place in the tile"""
    return ((hash32(int(round(x*100))+5000,int(round(y*100))+5000,k)%1000)/1000.0-0.5)*0.016

def qy_walls(land):
    """the centre half-lines between a land and a water quadrant: name -> (land quadrant, water quadrant)"""
    out={}
    for name,(d,qa,qb) in QY_HALF.items():
        if (qa in land)!=(qb in land): out[name]=(qa,qb) if qa in land else (qb,qa)
    return out

def qy_tile(land,cut=None):
    """a quay tile: land = its land quadrants; a wall on each centre half-line between land and water (face on the
       line, coping stones on top), a corner stone and quoins at a convex corner, the land tops and the sea bed.
       cut=(x0,x1): an Edge tile's wall, coping and land left open there for a slipway"""
    tb=TB(); walls=qy_walls(land)
    convex=[q for q in land if all(h in walls for h in QY_OF[q])]
    concave=[q for q in QY_QUAD if q not in land and all(h in walls for h in QY_OF[q]) and QY_OPP[q] in land]
    for name,(lq,wq) in walls.items():
        d=Vector((*QY_HALF[name][0],0.0)); sx,sy=QY_QUAD[wq]
        out=Vector((sx,0,0)) if d.x==0 else Vector((0,sy,0))             # toward the water
        def P(s,t,z,d=d,out=out): return tuple(d*s-out*t+Vector((0,0,z)))   # s along from the centre, t into the land
        s0=0.0; a=0.0
        if cut:
            s0=max(-cut[0],cut[1]); a=s0-QY_OV                           # the stub beside the slipway; its coping
        elif lq in convex: a=QY_CD                                       # overhangs into the cut
        elif wq in concave: a=-QY_CD if d.x==0 else QY_OV
        for k,(z0,z1) in enumerate(zip(QY_COURSES[:-1],QY_COURSES[1:])):  # the face, course by course
            o=QY_RELIEF*(k%2)
            qy_poly(tb,(P(s0,-o,z0),P(1.5,-o,z0),P(1.5,-o,z1),P(s0,-o,z1)),out)
            if k>0:                                                     # the ledge on the joint above
                ob=QY_RELIEF*((k-1)%2)
                qy_poly(tb,(P(s0,-ob,z0),P(1.5,-ob,z0),P(1.5,-o,z0),P(s0,-o,z0)),(0,0,1) if o>ob else (0,0,-1))
        n=max(1,int(round((1.5-a)/0.75)))
        for i in range(n):                                               # coping stones
            c0=a+(1.5-a)*i/n; c1=a+(1.5-a)*(i+1)/n; m=P((c0+c1)/2,0,0)
            qy_box(tb,P(c0,-QY_OV,QY_CB),P(c1,QY_CD,QY_COP+qy_jit(m[0],m[1])))
    for j,q in enumerate(convex):                                        # corner stone and quoins
        sx,sy=QY_QUAD[q]
        qy_box(tb,(-QY_OV*sx,-QY_OV*sy,QY_CB),(QY_CD*sx,QY_CD*sy,QY_COP+0.006+qy_jit(sx,sy,1)))
        zo=-0.27*j                                                       # a second corner (a saddle) on other courses
        for i,(z0,z1) in enumerate(((QY_CB,-0.75),(-0.75,-1.3),(-1.3,-1.85),(-1.85,-2.4))):
            lx,ly=(0.55,0.32) if i%2==0 else (0.32,0.55)
            qy_box(tb,(-0.025*sx,-0.025*sy,max(z0+zo,QY_CB)+0.01),(lx*sx,ly*sy,z1+zo-0.01))
    for q in land:                                                       # the land tops (the map's ground)
        sx,sy=QY_QUAD[q]; x0,x1=sorted((0.0,1.5*sx)); y0,y1=sorted((0.0,1.5*sy))
        spans=[(x0,x1)]
        if cut: spans=[(a_,b_) for a_,b_ in ((x0,min(x1,cut[0])),(max(x0,cut[1]),x1)) if b_-a_>1e-6]
        for a_,b_ in spans: qy_poly(tb,((a_,y0,0),(b_,y0,0),(b_,y1,0),(a_,y1,0)),(0,0,1),0,FLAT_T)
    for q in QY_QUAD:                                                    # the sea bed
        if q in land: continue
        sx,sy=QY_QUAD[q]; x0,x1=sorted((0.0,1.5*sx)); y0,y1=sorted((0.0,1.5*sy))
        qy_poly(tb,((x0,y0,QY_BED),(x1,y0,QY_BED),(x1,y1,QY_BED),(x0,y1,QY_BED)),(0,0,1),0,BED_T)
    return tb

def qy_stair(tb):
    """water stairs on an Edge tile, against its face (y -1.0..0): a landing at the land's height, seven steps down
       toward -x, a landing 0.25 above the water"""
    y0=-1.0; top=0.0; land=-1.85
    xs=[1.5,0.85]+[0.85-1.8*k/7 for k in range(1,8)]+[-1.5]
    zs=[top]+[top-0.25*k for k in range(1,8)]+[land]
    def yb(z): return -QY_OV if z>QY_CB else 0.0                         # up top the coping's lip, below it the face
    for i,z in enumerate(zs):
        xa,xb=sorted((xs[i],xs[i+1]))
        qy_poly(tb,((xa,y0,z),(xb,y0,z),(xb,yb(z),z),(xa,yb(z),z)),(0,0,1))                    # tread
        if i+1<len(zs):
            z2=zs[i+1]; x=xs[i+1]
            qy_poly(tb,((x,y0,z2),(x,yb(z2),z2),(x,yb(z2),z),(x,y0,z)),(-1,0,0))              # riser
        qy_poly(tb,((xa,y0,QY_BED),(xb,y0,QY_BED),(xb,y0,z),(xa,y0,z)),(0,-1,0))               # outer side
    for x,z in ((1.5,top),(-1.5,land)):                                  # the flight's ends
        qy_poly(tb,((x,y0,QY_BED),(x,0.0,QY_BED),(x,0.0,z),(x,y0,z)),(1 if x>0 else -1,0,0))

def qy_slip(tb,hw=1.0,y_end=-4.5):
    """slipway through an Edge tile: setts (the stair stone's cobbles, TCol G 0) from the tile's land edge at z 0 down
       0.45 a metre into the sea, past the tile to y_end; the cut's walls in the land, the slip's sides in the water,
       a kerb along each side of the cut"""
    def zr(y): return -0.45*(1.5-y)
    ys=[1.5,0.75,0.0,-1.5,-3.0,y_end]
    for ya,yb in zip(ys[:-1],ys[1:]):
        qy_poly(tb,((-hw,ya,zr(ya)),(hw,ya,zr(ya)),(hw,yb,zr(yb)),(-hw,yb,zr(yb))),QY_SLIP_N,1,None,0.0)
    for s in(-1,1):
        x=s*hw
        qy_poly(tb,((x,1.5,0.0),(x,0.0,0.0),(x,0.0,zr(0.0))),(-s,0,0))                         # the cut's wall
        qy_poly(tb,[(x,0.0,QY_BED)]+[(x,y,zr(y)) for y in ys[2:]]+[(x,y_end,QY_BED)],(s,0,0))  # the slip's side
        k0=x-s*QY_OV; k1=x+s*0.35
        qy_box(tb,(k0,QY_CD,QY_CB),(k1,1.5,QY_COP+qy_jit(x,1.0,2)))                             # kerb
    qy_poly(tb,((-hw,y_end,QY_BED),(hw,y_end,QY_BED),(hw,y_end,zr(y_end)),(-hw,y_end,zr(y_end))),(0,-1,0))

def gen_quay(case,var="A"):
    land={EDGE:("NE","NW"),OUTER:("NW",),INNER:("SW","NE","NW"),SADDLE:("SW","NE")}[case]
    if var=="Slip":
        tb=qy_tile(land,cut=(-1.0,1.0)); qy_slip(tb); return tb
    tb=qy_tile(land)
    if var=="Stair": qy_stair(tb)
    return tb

QUAY_TILES=[(EDGE,"A"),(EDGE,"Stair"),(EDGE,"Slip"),(OUTER,"A"),(INNER,"A"),(SADDLE,"A")]
def tk_build_quays():
    coll=tk_pieces_coll(); out={}
    for case,var in QUAY_TILES:
        nm=f"SM_VKT_Quay_{CASE_NAMES[case]}_{var}"
        out[nm]=tk_finish(gen_quay(case,var),nm,coll,dict(set="Quay",case=CASE_NAMES[case],var=var,mask=CANON[case]))
    return out

def qy_pick(G,c,lo,hi):
    """tk_tiles' hook: a quay vertex (land one level above sea, a land corner flagged) -> (case, r, var), else None"""
    if hi!=lo+1: return None
    if any(x[1] and x[0]!=lo for x in c) or any((not x[1]) and x[0]!=hi for x in c): return None
    if not any(x[1] for x in c) or all(x[1] for x in c): return None
    flags=[int(G.quay[x[3],x[2]]) for x in c if not x[1]]
    if not any(flags): return None
    case,r=MS[sum(1<<k for k in range(4) if not c[k][1])]
    var="A"
    if case==EDGE and all(f==3 for f in flags): var="Slip"           # both land cells flagged: the vertex between
    elif case==EDGE and all(f==2 for f in flags): var="Stair"        # them carries it
    return case,r,var

def qy_demo(coll=None,origin=(300.0,300.0,0.0)):
    """a sample harbour from the grid: a straight quay with water stairs and a slipway, a pier head, an island touching
       the quay at a corner (saddles), two notches; the harbour props on it (vk_mod_harbour) and a jetty, a mole with
       its light. Returns the made objects (the terrain chunk, its water and the props)"""
    W,H,S=14,10,6
    G=TGrid(W,H); G.level[:,:]=1
    for j in range(S):
        for i in range(W): G.level[j,i]=0; G.water[j,i]=True
    for (i,j) in ((3,4),(4,4),(3,5),(4,5),(6,5)): G.level[j,i]=1; G.water[j,i]=False
    for (i,j) in ((6,6),(10,6)): G.level[j,i]=0; G.water[j,i]=True
    for j in range(H):
        for i in range(W):
            if not G.water[j,i] and G.water[max(0,j-1):j+2,max(0,i-1):i+2].any(): G.quay[j,i]=1
    for i in (1,2): G.quay[S,i]=2
    for i in (8,9): G.quay[S,i]=3
    if coll is None:
        coll=bpy.data.collections.get("__harbour_preview") or bpy.data.collections.new("__harbour_preview")
        if coll.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(coll)
    made=tk_build_chunks(G,prefix="QYDEMO",origin=origin,chunk=16,coll=coll)
    ox,oy,oz=origin; L=oz+TIER; Q=oy+3*S
    def put(piece,x,y,rot):
        src=bpy.data.objects.get(piece)
        if src is None: return
        o=bpy.data.objects.new("__hb_"+piece[6:],src.data); coll.objects.link(o)
        o.location=(ox+x,y,L if piece!="SM_VK_Prop_Rowboat" else L+QY_WATER+0.25); o.rotation_euler.z=math.radians(rot)
        made.append(o)
    for x in(1.0,8.0,34.8,39.0): put("SM_VK_Harbour_Bollard",x,Q,0)
    for x in(0.6,3.4,33.0,36.5,40.5): put("SM_VK_Harbour_Fender",x,Q,0)
    for x in(2.0,38.0): put("SM_VK_Harbour_Ring",x,Q,0)
    put("SM_VK_Harbour_Ladder",9.0,Q-3.0,-90)
    put("SM_VK_Jetty_Deck",12.0,Q-7.5,-90); put("SM_VK_Jetty_Landing",12.0,Q-7.5,-90); put("SM_VK_Jetty_End",12.0,Q-10.5,-90)
    for y in(Q-1.5,Q-4.5,Q-7.5): put("SM_VK_Breakwater",37.5,y,-90)
    put("SM_VK_Breakwater_End",37.5,Q-10.5,-90)
    put("SM_VK_Prop_Rowboat",15.5,Q-11.5,80)
    return made
