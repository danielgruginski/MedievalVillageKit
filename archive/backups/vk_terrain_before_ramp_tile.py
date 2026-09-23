# ===================== VK TERRAIN : dual-grid marching-squares tile kit =====================
# Game cells carry one level (x1.5 m) and a ground type; render tiles sit on grid vertices and
# take their 4 corners from the 4 cells meeting there (marching squares on the dual grid).
# Tall height differences are stacked from binary layers, so 5 cliff shapes cover every case.
import bpy, bmesh, math, json, random
import numpy as np
from mathutils import Vector, Matrix
from mathutils.geometry import delaunay_2d_cdt

TT=3.0; TIER=1.5; Q=1.0/1024
SKIRT_Z=-3.0          # layer-local skirt bottom (= bed of water one level below)
WATER_Z=-0.6          # water surface below its cell's level   (matches the building kit water datum)
BED_Z=-1.5            # river bed below its cell's level
MAP_ORIGIN=(1200.0,0.0,0.0)
EMPTY,FULL,EDGE,OUTER,INNER,SADDLE,BEDC=range(7)
CASE_NAMES=["Empty","Full","Edge","Outer","Inner","Saddle","Bed"]
MS=[(EMPTY,0),(OUTER,1),(OUTER,2),(EDGE,2),(OUTER,3),(SADDLE,0),(EDGE,3),(INNER,2),
    (OUTER,0),(EDGE,1),(SADDLE,1),(INNER,1),(EDGE,0),(INNER,0),(INNER,3),(FULL,0)]
SHORE=list(MS); SHORE[0]=(BEDC,0); SHORE[15]=(FULL,0)
CANON={EMPTY:0,FULL:15,EDGE:12,OUTER:8,INNER:13,SADDLE:5,BEDC:0}
CORNER=[(-1.5,-1.5),(1.5,-1.5),(1.5,1.5),(-1.5,1.5)]        # bit k: SW SE NE NW
def rotl(m): return ((m<<1)|(m>>3))&15
def rot_xy(x,y,r):
    for _ in range(r&3): x,y=-y,x
    return x,y

# ---- profiles: (d, z, AO, rock, rim, wet, sharp) ; d measured from the high/land corner along a side ----
P_CLIFF=[
 (0.00, 0.000,1.00,0,0.00,0,0),
 (0.50, 0.000,1.00,0,0.00,0,0),
 (1.00, 0.000,1.00,0,0.15,0,0),
 (1.22,-0.015,1.00,0,0.60,0,0),   # 3 lip start = top-region boundary
 (1.40,-0.060,1.00,0,1.00,0,0),   # 4 sunlit crest
 (1.54,-0.150,0.90,0,0.40,0,1),   # 5 turf edge overhang (split: faces below are rock)
 (1.48,-0.240,0.45,1,0.00,0,1),   # 6 root recess
 (1.56,-0.620,0.75,1,0.00,0,0),   # 7 upper face
 (1.76,-0.680,0.95,1,0.00,0,0),   # 8 strata ledge nose
 (1.70,-0.800,0.55,1,0.00,0,0),   # 9 ledge underside
 (1.80,-1.060,0.85,1,0.00,0,0),   # 10 bulge
 (1.70,-1.340,0.70,1,0.00,0,0),   # 11
 (1.45,-1.520,0.55,1,0.00,0,0),   # 12 toe, tucked under the floor below
 (1.45,SKIRT_Z,0.45,1,0.00,0,0)]  # 13 skirt bottom (open edge)
P_SHORE=[
 (0.00, 0.000,1.00,0,0.00,0.0,0),
 (0.50, 0.000,1.00,0,0.00,0.0,0),
 (1.00, 0.000,1.00,0,0.10,0.0,0),
 (1.22,-0.015,1.00,0,0.40,0.0,0),  # 3 top boundary
 (1.40,-0.050,1.00,0,0.80,0.0,0),  # 4 turf crest
 (1.52,-0.120,0.90,0,0.30,0.0,1),  # 5 turf edge (split: faces below are sand)
 (1.48,-0.200,0.60,0,0.00,0.5,1),  # 6 turf underside, sand starts
 (1.62,-0.330,0.85,0,0.00,0.6,0),
 (1.80,-0.600,0.85,0,0.00,1.0,0),  # 8 waterline
 (2.05,-0.850,0.75,0,0.00,1.0,0),
 (2.35,-1.200,0.65,0,0.00,1.0,0),
 (2.65,-1.500,0.55,0,0.00,1.0,0),  # 11 bank foot = bed boundary
 (3.00,-1.500,0.55,0,0.00,1.0,0)]  # 12 low corner
TOP_ROW=3; CLIFF_LAST=13; SHORE_FOOT=11
FLAT_T=(1.0,0.0,0.0,0.0); BED_T=(0.55,0.0,0.0,1.0)
BELOW_CLIFF=(0.45,1.0,0.0,0.0); BELOW_SHORE=(0.60,0.0,0.0,0.5)

def _segn(a,b):
    du=b[0]-a[0]; dv=b[1]-a[1]; L=math.hypot(du,dv); return (-dv/L,du/L)
def row_normals(P,last):
    out=[]
    for i in range(last+1):
        a=_segn(P[i-1],P[i]) if i>0 else (0.0,1.0)
        b=_segn(P[i],P[i+1]) if i<last else a
        if P[i][6]: out.append((a,b))
        else:
            s=(a[0]+b[0],a[1]+b[1]); L=math.hypot(*s); s=(s[0]/L,s[1]/L); out.append((s,s))
    return out
def row_tcol(P,i,below,split_row=5):
    r=P[i]; t=(r[2],r[3],r[4],r[5])
    if i==split_row and below: return BELOW_CLIFF if P is P_CLIFF else BELOW_SHORE
    return t

# ---------------------------------------------------------------- piece builder
class TB:
    """tiny mesh builder: verts, faces with per-loop normals and TCol"""
    def __init__(s): s.v=[]; s.f=[]; s.ln=[]; s.lc=[]; s.mi=[]; s.key={}
    def vert(s,p,share=True):
        p=(float(p[0]),float(p[1]),float(p[2]))
        if abs(abs(p[0])-1.5)<1e-5 or abs(abs(p[1])-1.5)<1e-5:
            p=tuple(round(c/Q)*Q for c in p)
        k=(round(p[0],5),round(p[1],5),round(p[2],5))
        if share and k in s.key: return s.key[k]
        s.v.append(p); s.key[k]=len(s.v)-1; return len(s.v)-1
    def face(s,idx,normals,tcols,mi=0):
        s.f.append(list(idx)); s.ln.append([tuple(n) for n in normals]); s.lc.append([tuple(c) for c in tcols]); s.mi.append(mi)

def side_pos(k,d,from_bit):
    """position on tile side k at distance d from corner from_bit (which must be an end of side k)"""
    a=CORNER[from_bit]; other=(k+1)%4 if from_bit==k else k
    b=CORNER[other]; ux=(b[0]-a[0])/3.0; uy=(b[1]-a[1])/3.0
    return (a[0]+ux*d,a[1]+uy*d)

def _front_edge(ncol=13):
    xs=[ -1.5+3.0*j/(ncol-1) for j in range(ncol)]
    return [dict(pos=(lambda d,x=x:(x,1.5-d)),o=(0.0,-1.0)) for x in xs]
def _front_arc(center,th0,th1,ncol=9,inner=False):
    cols=[]
    for j in range(ncol):
        th=math.radians(th0+(th1-th0)*j/(ncol-1)); c,s_=math.cos(th),math.sin(th)
        if not inner: cols.append(dict(pos=(lambda d,c=c,s_=s_:(center[0]+d*c,center[1]+d*s_)),o=(c,s_)))
        else: cols.append(dict(pos=(lambda d,c=c,s_=s_:(center[0]+(3.0-d)*c,center[1]+(3.0-d)*s_)),o=(-c,-s_)))
    return cols

def sweep(tb,front,P,row0,row1,z0=0.0):
    """sweep profile rows row0..row1 along the front columns; returns grid of vertex ids [col][row].
       Columns carrying a variant offset (c["var"]) get normals from the displaced geometry (rows 4..row1-1);
       the end columns (on tile sides) always keep the analytic table normals."""
    RN=row_normals(P,len(P)-1)
    ids=[[tb.vert((*c["pos"](P[i][0]),z0+P[i][1])) for i in range(row0,row1+1)] for c in front]
    ncol=len(front); numeric=any(c.get("var") for c in front)
    def n3(col,nuv): return (nuv[0]*col["o"][0],nuv[0]*col["o"][1],nuv[1])
    def vn(j,ii,which):
        """normal at column j, profile index ii (row row0+ii); which: 1 = for the face below the row, 0 = above"""
        i=row0+ii; c=front[j]
        ana=n3(c,RN[i][1 if which else 0])
        if not numeric or j in (0,ncol-1) or i<=TOP_ROW or i>=row1: return ana
        V=lambda jj,kk: Vector(tb.v[ids[jj][kk]])
        Tc=V(j+1,ii)-V(j-1,ii)
        if P[i][6]: Tp=(V(j,ii+1)-V(j,ii)) if which else (V(j,ii)-V(j,ii-1))
        else: Tp=V(j,ii+1)-V(j,ii-1)
        n=Tc.cross(Tp)
        if n.length<1e-9: return ana
        n.normalize()
        if n.dot(Vector(ana))<0: n=-n
        return tuple(n)
    for j in range(ncol-1):
        for ii,i in enumerate(range(row0,row1)):
            a,b=front[j],front[j+1]
            q=[ids[j][ii],ids[j+1][ii],ids[j+1][ii+1],ids[j][ii+1]]
            ns=[vn(j,ii,1),vn(j+1,ii,1),vn(j+1,ii+1,0),vn(j,ii+1,0)]
            ts=[row_tcol(P,i,True)]*2+[row_tcol(P,i+1,False)]*2
            # orient so the face normal agrees with the analytic normal
            V=[Vector(tb.v[k]) for k in q]; fn=(V[1]-V[0]).cross(V[3]-V[0])
            nm=Vector(ns[0])+Vector(ns[2])
            if fn.length>1e-9 and fn.dot(nm)<0: q=q[::-1]; ns=ns[::-1]; ts=ts[::-1]
            tb.face(q,ns,ts)
    return ids

def _dist_seg(p,a,b):
    ax,ay=a[0],a[1]; bx,by=b[0],b[1]; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((p[0]-ax)*dx+(p[1]-ay)*dy)/L2))
    return math.hypot(p[0]-(ax+t*dx),p[1]-(ay+t*dy))
def _inside(p,poly):
    c=False; n=len(poly)
    for i in range(n):
        a=poly[i]; b=poly[(i+1)%n]
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1]+1e-30)+a[0]: c=not c
    return c
TUP=(0.0,0.0,1.0)
def region(tb,loop,zint,tint,lattice=0.5,margin=0.2):
    """flat-ish region bounded by loop entries (x,y,z,normal,tcol) in CCW order; interior lattice at zint"""
    L=[]
    for e in loop:
        if not L or math.hypot(e[0]-L[-1][0],e[1]-L[-1][1])>1e-6: L.append(e)
    if math.hypot(L[0][0]-L[-1][0],L[0][1]-L[-1][1])<1e-6: L.pop()
    nb=len(L); ents=list(L)
    g=np.arange(-1.5+lattice,1.5-1e-6,lattice)
    for x in g:
        for y in g:
            p=(float(x),float(y))
            if _inside(p,L) and min(_dist_seg(p,L[i],L[(i+1)%nb]) for i in range(nb))>=margin: ents.append((p[0],p[1],zint,TUP,tint))
    res=delaunay_2d_cdt([Vector((e[0],e[1])) for e in ents],[],[list(range(nb))],1,1e-6)
    vo,fo,orig=res[0],res[2],res[3]
    assert len(vo)==len(ents), ("steiner points",len(vo),len(ents))
    omap=[o_[0] for o_ in orig]
    ids=[tb.vert((e[0],e[1],e[2])) for e in ents]
    for f in fo:
        q=[omap[k] for k in f]
        V=[Vector(tb.v[ids[k]]) for k in q]
        if (V[1]-V[0]).cross(V[2]-V[0]).z<0: q=q[::-1]
        tb.face([ids[k] for k in q],[ents[k][3] for k in q],[ents[k][4] for k in q])

def _side_dir(k,from_bit):
    a=CORNER[from_bit]; other=(k+1)%4 if from_bit==k else k; b=CORNER[other]
    return ((b[0]-a[0])/3.0,(b[1]-a[1])/3.0)
def _n3(nuv,o): return (nuv[0]*o[0],nuv[0]*o[1],nuv[1])
def side_ents(P,RN,k,fb,rows):
    o=_side_dir(k,fb); out=[]
    for i in rows:
        x,y=side_pos(k,P[i][0],fb)
        n=TUP if i<TOP_ROW else _n3(RN[i][0],o)
        out.append((x,y,P[i][1],n,row_tcol(P,i,False)))
    return out
def flat_ents(k,fb,z=0.0,t=FLAT_T):
    return [(*side_pos(k,d,fb),z,TUP,t) for d in (0,0.5,1.0,1.5,2.0,2.5,3.0)]
def curve_ents(P,RN,front,i):
    return [(*c["pos"](P[i][0]),P[i][1],_n3(RN[i][0],c["o"]),row_tcol(P,i,False)) for c in front]

def _n1(x,s): return 0.6*math.sin(2.1*x+s)+0.4*math.sin(4.7*x+1.3*s+0.7)
def _win(sig,L): 
    def ss(a,b,x): t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
    return ss(0.25,0.75,sig)*ss(0.25,0.75,L-sig)
def variant_front(front,P,var,L,seed=0):
    """wrap a front so every column applies a seam-safe offset ds(row) (positive = toward the high side)"""
    if var=="A": return front
    rng=random.Random(hash((var,len(front),seed))&0xffffffff); n=len(front)
    blocks=[0.0]*n
    if var=="B":
        j=0; val=None
        while j<n:
            L_=rng.randint(3,5) if n>9 else rng.randint(2,3)
            bv=-rng.uniform(0.04,0.14); yaw=rng.uniform(-0.03,0.03)
            for k in range(L_):
                if j+k>=n: break
                blocks[j+k]=bv+yaw*(k/(max(1,L_-1))-0.5)*2
            if j+L_<n: blocks[j+L_-1]=-0.02
            j+=L_
    cc=L/2+rng.uniform(-0.3,0.3); cliff=P is P_CLIFF
    out=[]
    for j,c in enumerate(front):
        t=j/(n-1); sig=t*L; W=_win(sig,L)
        rowd={}
        for i,r in enumerate(P):
            ds=0.0
            if i in (4,5): ds+=0.07*_n1(sig/0.9,seed*1.7+(3 if var=="C" else 0))*W
            if 7<=i<=11 and cliff:
                wr=0.6 if i in (7,11) else 1.0
                if var=="B": ds+=blocks[j]*W*wr
                if var=="C":
                    x=(sig-cc)/0.5
                    ds+=-0.22*(0.5*(1+math.cos(math.pi*x)) if abs(x)<1 else 0.0)*W*wr
            rowd[i]=ds
        base=c["pos"]
        def pos(d,base=base,rowd=rowd):
            for i,r in enumerate(P):
                if abs(r[0]-d)<1e-9 and rowd.get(i,0.0)!=0.0: return base(d-rowd[i])
            return base(d)
        out.append(dict(pos=pos,o=c["o"],var=True))
    return out
VARIANTS={("Cliff",EDGE):("A","B","C"),("Cliff",OUTER):("A","B","Sq"),("Cliff",INNER):("A","B","Sq"),("Shore",EDGE):("A","B")}
DIAG=(1/math.sqrt(2),-1/math.sqrt(2))
def _front_sq(kind,n=7):
    """mitred square contour for stiff tiles: Outer (NW high) or Inner (SE low); mitre at (d-1.5, 1.5-d)"""
    cols=[]
    for k in range(n):                       # leg 1
        t=k/(n-1)
        if kind=="outer": f=(lambda d,t=t:(-1.5+t*d,1.5-d)); o=(0.0,-1.0)
        else:             f=(lambda d,t=t:(d-1.5,-1.5+t*(3.0-d))); o=(1.0,0.0)
        cols.append(dict(pos=f,o=DIAG if k==n-1 else o,var=True))
    for k in range(1,n):                     # leg 2
        t=k/(n-1)
        if kind=="outer": f=(lambda d,t=t:(d-1.5,1.5-d+t*d)); o=(1.0,0.0)
        else:             f=(lambda d,t=t:(d-1.5+t*(3.0-d),1.5-d)); o=(0.0,-1.0)
        cols.append(dict(pos=f,o=o,var=True))
    return cols
def gen_piece(set_,case,var="A"):
    """canonical geometry for (set, case, variant); returns TB"""
    tb=TB(); P=P_CLIFF if set_=="Cliff" else P_SHORE
    last=CLIFF_LAST if set_=="Cliff" else SHORE_FOOT
    RN=row_normals(P,len(P)-1); T3=list(range(TOP_ROW+1))
    if case in (FULL,BEDC):
        z=0.0 if case==FULL else BED_Z; t=FLAT_T if case==FULL else BED_T
        ids=[[tb.vert((-1.5+0.5*i,-1.5+0.5*j,z)) for j in range(7)] for i in range(7)]
        for i in range(6):
            for j in range(6):
                tb.face([ids[i][j],ids[i+1][j],ids[i+1][j+1],ids[i][j+1]],[TUP]*4,[t]*4)
        return tb
    if case==EDGE:
        fr=variant_front(_front_edge(),P,var,3.0,seed=11); fronts=[fr]
        loop=curve_ents(P,RN,fr,TOP_ROW)+side_ents(P,RN,1,2,T3[::-1])+flat_ents(2,2)+side_ents(P,RN,3,3,T3)
        tops=[loop]
    elif case==OUTER:
        fr=_front_sq("outer") if var=="Sq" else variant_front(_front_arc(CORNER[3],-90,0),P,var,1.5*math.pi/2,seed=12); fronts=[fr]
        loop=side_ents(P,RN,3,3,T3)+curve_ents(P,RN,fr,TOP_ROW)+side_ents(P,RN,2,3,T3[::-1])
        tops=[loop]
    elif case==INNER:
        fr=_front_sq("inner") if var=="Sq" else variant_front(_front_arc(CORNER[1],180,90,inner=True),P,var,1.5*math.pi/2,seed=13); fronts=[fr]
        loop=side_ents(P,RN,0,0,T3)+curve_ents(P,RN,fr,TOP_ROW)+side_ents(P,RN,1,2,T3[::-1])+flat_ents(2,2)+flat_ents(3,3)
        tops=[loop]
    elif case==SADDLE:
        f1=_front_arc(CORNER[0],0,90); f2=_front_arc(CORNER[2],180,270); fronts=[f1,f2]
        l1=side_ents(P,RN,0,0,T3)+curve_ents(P,RN,f1,TOP_ROW)+side_ents(P,RN,3,0,T3[::-1])
        l2=side_ents(P,RN,2,2,T3)+curve_ents(P,RN,f2,TOP_ROW)+side_ents(P,RN,1,2,T3[::-1])
        tops=[l1,l2]
    else: raise ValueError(case)
    for fr in fronts: sweep(tb,fr,P,TOP_ROW,last)
    for lp in tops: region(tb,lp,0.0,FLAT_T)
    if set_=="Shore": _shore_bed(tb,case,P,RN,fronts)
    return tb

def _shore_bed(tb,case,P,RN,fronts):
    F=SHORE_FOOT; tail=[F,F+1]; z=BED_Z
    def arc_ents(center,a0,a1,n=6):
        out=[]
        for t in range(n):
            a=math.radians(a0+(a1-a0)*t/(n-1)); c,s_=math.cos(a),math.sin(a); R=P[F][0]
            out.append((center[0]+R*c,center[1]+R*s_,z,_n3(RN[F][0],(c,s_)),row_tcol(P,F,False)))
        return out
    if case==EDGE:
        fr=fronts[0]
        loop=flat_ents(0,0,z,BED_T)+side_ents(P,RN,1,2,tail[::-1])+curve_ents(P,RN,fr,F)[::-1]+side_ents(P,RN,3,3,tail)
        loops=[loop]
    elif case==OUTER:
        fr=fronts[0]
        loop=flat_ents(0,0,z,BED_T)+flat_ents(1,1,z,BED_T)+side_ents(P,RN,2,3,tail[::-1])+curve_ents(P,RN,fr,F)[::-1]+side_ents(P,RN,3,3,tail)
        loops=[loop]
    elif case==INNER:
        fr=fronts[0]
        loop=side_ents(P,RN,0,0,tail)+side_ents(P,RN,1,2,tail[::-1])+curve_ents(P,RN,fr,F)[::-1]
        loops=[loop]
    elif case==SADDLE:
        R=P[F][0]; cx=math.sqrt(max(0.0,R*R-4.5))/math.sqrt(2)
        aNE=math.degrees(math.atan2(-cx-1.5,cx-1.5)); aSW=math.degrees(math.atan2(-cx+1.5,cx+1.5))
        l1=side_ents(P,RN,0,0,tail)+side_ents(P,RN,1,2,tail[::-1])+arc_ents(CORNER[2],-90,aNE)[1:]+arc_ents(CORNER[0],aSW,0)[1:-1]
        aSW2=math.degrees(math.atan2(cx+1.5,-cx+1.5)); aNE2=math.degrees(math.atan2(cx-1.5,-cx-1.5))
        if aNE2<0: aNE2+=360
        l2=side_ents(P,RN,2,2,tail)+side_ents(P,RN,3,0,tail[::-1])+arc_ents(CORNER[0],90,aSW2)[1:]+arc_ents(CORNER[2],aNE2,180)[1:-1]
        loops=[l1,l2]
    for lp in loops: region(tb,lp,z,BED_T,lattice=0.5,margin=0.15)

# ---------------------------------------------------------------- side tables (seam contract)
def side_type(set_,a,b):
    if a and b: return "FLAT"
    if not a and not b: return "EMPTY" if set_=="Cliff" else "BED"
    return "CLIFF" if set_=="Cliff" else "SHORE"
def side_table(t):
    """list of (d, z, normals(set of (nu,nv)), tcols(set)) for a side type"""
    if t=="FLAT": return [(d,0.0,{(0.0,1.0)},{FLAT_T}) for d in (0,0.5,1.0,1.5,2.0,2.5,3.0)]
    if t=="BED": return [(d,BED_Z,{(0.0,1.0)},{BED_T}) for d in (0,0.5,1.0,1.5,2.0,2.5,3.0)]
    if t=="EMPTY": return []
    P=P_CLIFF if t=="CLIFF" else P_SHORE; RN=row_normals(P,len(P)-1); out=[]
    for i,r in enumerate(P):
        ns={RN[i][0],RN[i][1]}
        if i<TOP_ROW: ns={(0.0,1.0)}
        tc={row_tcol(P,i,False)}
        if i==5: tc.add(row_tcol(P,i,True))
        out.append((r[0],r[1],ns,tc))
    return out

def tk_finish(tb,name,coll,props):
    me=bpy.data.meshes.get(name)
    if me is None: me=bpy.data.meshes.new(name)
    else: me.clear_geometry()
    me.from_pydata(tb.v,[],tb.f)
    me.update()
    ln=[n for fl in tb.ln for n in fl]; lc=[c for fl in tb.lc for c in fl]
    for p in me.polygons: p.use_smooth=True
    me.normals_split_custom_set([Vector(n).normalized() for n in ln])
    at=me.color_attributes.get("TCol") or me.color_attributes.new("TCol","FLOAT_COLOR","CORNER")
    at.data.foreach_set("color",[x for c in lc for x in c])
    me.polygons.foreach_set("material_index",tb.mi)
    mats=tk_mats()
    if len(me.materials)==0:
        for m in mats: me.materials.append(m)
    o=bpy.data.objects.get(name)
    if o is None:
        o=bpy.data.objects.new(name,me); coll.objects.link(o)
    o.data=me
    for k,v in props.items(): o[k]=v
    o["kit"]="VillageTerrain"
    o.hide_render=True; o.hide_viewport=True
    return o

def tk_mats():
    t=bpy.data.materials.get("M_VK_Terrain") or tk_debug_material("M_VK_Terrain")
    a=bpy.data.materials.get("M_VKT_Stair") or stair_material()
    return [t,a]
def stair_material(name="M_VKT_Stair"):
    """ashlar steps without UVs: triplanar in object space (chunks sit unrotated at MAP_ORIGIN)"""
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
    out=B.n("ShaderNodeOutputMaterial"); b=B.n("ShaderNodeBsdfPrincipled")
    tc=B.n("ShaderNodeTexCoord"); p=tc.outputs["Object"]
    sc,sv,(vT,az)=B.side_sample("T_VK_Ashlar_BC",p,1/3.0)
    _,hv,_=B.side_sample("T_VK_Ashlar_H",p,1/3.0,data=True)
    top=B.img("T_VK_Ashlar_BC",vT); topH=B.img("T_VK_Ashlar_H",vT,data=True)
    wz=B.smoothstep(az,0.55,0.8)
    col=B.mix(wz,sc,top.outputs[0]); h=B.fmix(wz,hv,topH.outputs[0])
    B.link(col,b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.85
    bp=B.n("ShaderNodeBump"); bp.inputs["Strength"].default_value=0.5; bp.inputs["Distance"].default_value=0.03
    B.link(h,bp.inputs["Height"]); B.link(bp.outputs[0],b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value=0.25
    B.link(b.outputs[0],out.inputs[0]); return m

def tk_debug_material(name="M_VKT_Debug"):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); L=nt.links
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc=nt.nodes.new("ShaderNodeTexCoord"); ch=nt.nodes.new("ShaderNodeTexChecker"); ch.inputs["Scale"].default_value=1/1.5*0.5
    ch.inputs["Color1"].default_value=(0.32,0.48,0.20,1); ch.inputs["Color2"].default_value=(0.26,0.40,0.16,1)
    L.new(tc.outputs["Object"],ch.inputs["Vector"])
    at=nt.nodes.new("ShaderNodeAttribute"); at.attribute_name="TCol"
    sep=nt.nodes.new("ShaderNodeSeparateColor"); L.new(at.outputs["Color"],sep.inputs[0])
    rock=nt.nodes.new("ShaderNodeMix"); rock.data_type="RGBA"; rock.inputs[7].default_value=(0.45,0.40,0.36,1)
    L.new(sep.outputs[1],rock.inputs[0]); L.new(ch.outputs["Color"],rock.inputs[6])
    wet=nt.nodes.new("ShaderNodeMix"); wet.data_type="RGBA"; wet.inputs[7].default_value=(0.55,0.48,0.32,1)
    L.new(at.outputs["Alpha"],wet.inputs[0]); L.new(rock.outputs[2],wet.inputs[6])
    ao=nt.nodes.new("ShaderNodeMix"); ao.data_type="RGBA"; ao.blend_type="MULTIPLY"; ao.inputs[0].default_value=1
    L.new(wet.outputs[2],ao.inputs[6]); L.new(sep.outputs[0],ao.inputs[7])
    L.new(ao.outputs[2],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.9
    L.new(b.outputs[0],o.inputs[0])
    return m

def tk_pieces_coll():
    c=bpy.data.collections.get("VK_TerrainTiles")
    if c is None:
        c=bpy.data.collections.new("VK_TerrainTiles"); bpy.data.scenes["VillageKit"].collection.children.link(c)
    return c
PIECES={}
def tk_build_pieces():
    coll=tk_pieces_coll(); out={}
    for set_ in ("Cliff","Shore"):
        for case in (FULL,EDGE,OUTER,INNER,SADDLE)+((BEDC,) if set_=="Shore" else ()):
            if set_=="Shore" and case==FULL: continue
            for var in VARIANTS.get((set_,case),("A",)):
                tb=gen_piece(set_,case,var)
                nm=f"SM_VKT_{set_}_{CASE_NAMES[case]}_{var}"
                o=tk_finish(tb,nm,coll,dict(set=set_,case=CASE_NAMES[case],var=var,mask=CANON[case]))
                out[(set_,case,var)]=o
    # water quad
    tb=TB(); ids=[tb.vert(p) for p in ((-1.5,-1.5,WATER_Z),(1.5,-1.5,WATER_Z),(1.5,1.5,WATER_Z),(-1.5,1.5,WATER_Z))]
    tb.face(ids,[(0,0,1)]*4,[(1,0,0,1)]*4)
    o=tk_finish(tb,"SM_VKT_WaterQuad",coll,dict(set="Water",case="Quad",var="A",mask=0))
    o.data.materials[0]=bpy.data.materials["M_VK_Water"]
    out[("Water",0)]=o
    return out

# ---------------------------------------------------------------- grid data
GROUNDS=["Grass","Dirt","Cobble","Sand","Rock"]
class TGrid:
    def __init__(s,W,H):
        s.W,s.H=W,H
        s.level=np.zeros((H,W),np.int32); s.water=np.zeros((H,W),bool)
        s.ground=np.zeros((H,W),np.int32); s.ramp=np.zeros((H,W),np.int32)   # ramp dir 0 none 1N 2E 3S 4W
        s.stair=np.zeros((H,W),bool); s.stiff=np.zeros((H,W),bool); s.wear=np.zeros((H,W),np.int32)
    def cell(s,i,j):
        i=min(max(i,0),s.W-1); j=min(max(j,0),s.H-1); return i,j
    def corners(s,I,J):
        cs=[s.cell(I-1,J-1),s.cell(I,J-1),s.cell(I,J),s.cell(I-1,J)]
        return [(s.level[j,i],s.water[j,i],i,j) for (i,j) in cs]
    def validate(s):
        errs=[]
        for j in range(s.H):
            for i in range(s.W):
                if s.water[j,i]:
                    for dj in (-1,0,1):
                        for di in (-1,0,1):
                            ii,jj=s.cell(i+di,j+dj)
                            if s.level[jj,ii]<s.level[j,i]: errs.append(("water_not_min",i,j))
        return errs

M32=0xffffffff
def hash32(x,y,z=0,seed=0):
    h=seed&M32
    h^=(x*0x8da6b343)&M32; h^=(y*0xd8163841)&M32; h^=(z*0xcb1ab31f)&M32
    h^=h>>16; h=(h*0x7feb352d)&M32; h^=h>>15; h=(h*0x846ca68b)&M32; h^=h>>16
    return h&M32

VAR_W={("Cliff",EDGE):(0.25,0.45,0.30),("Cliff",OUTER):(0.4,0.6,0.0),("Cliff",INNER):(0.4,0.6,0.0),("Shore",EDGE):(0.4,0.6)}
def pick_var(set_,case,h,stiff):
    vs=VARIANTS.get((set_,case))
    if not vs: return "A"
    if stiff: return "Sq" if "Sq" in vs else "A"
    w=VAR_W[(set_,case)]; x=(h>>8)%1000/1000.0; acc=0
    for v,wi in zip(vs,w):
        acc+=wi
        if x<acc: return v
    return vs[-1]
def tk_tiles(G,I0=0,J0=0,I1=None,J1=None):
    I1=G.W if I1 is None else I1; J1=G.H if J1 is None else J1
    for J in range(J0,J1+1):
        for I in range(I0,I1+1):
            c=G.corners(I,J); lv=[x[0] for x in c]; lo,hi=min(lv),max(lv)
            land=sum(1<<k for k in range(4) if not c[k][1])
            h=hash32(I,J,0)
            stiff=any(G.stiff[x[3],x[2]] for x in c)
            if land!=15:
                case,r=SHORE[land]
                if case==BEDC: r=h&3
                yield (I,J,lo,"Shore",case,r,pick_var("Shore",case,h,stiff))
                yield (I,J,lo,"Water",0,0,"A")
            else: yield (I,J,lo,"Cliff",FULL,h&3,"A")
            for l in range(lo+1,hi+1):
                m=sum(1<<k for k in range(4) if lv[k]>=l)
                case,r=MS[m]
                if case==EDGE and G.ramp.any():
                    ro=ramp_override(G,c,l,r)
                    if ro:
                        yield (I,J,l,"Stair" if _is_stair(G,c,l,r) else "Ramp",ro,r,"A"); continue
                yield (I,J,l,"Cliff",case,r,pick_var("Cliff",case,hash32(I,J,l),stiff))

# ---------------------------------------------------------------- chunk assembly (numpy)
_CACHE={}
def tk_cache(o):
    key=o.name
    if key in _CACHE: return _CACHE[key]
    me=o.data; nv=len(me.vertices); nl=len(me.loops); npo=len(me.polygons)
    co=np.empty(nv*3,np.float64); me.vertices.foreach_get("co",co); co=co.reshape(-1,3)
    vi=np.empty(nl,np.int64); me.loops.foreach_get("vertex_index",vi)
    ls=np.empty(npo,np.int64); me.polygons.foreach_get("loop_start",ls)
    lt=np.empty(npo,np.int64); me.polygons.foreach_get("loop_total",lt)
    mi=np.empty(npo,np.int64); me.polygons.foreach_get("material_index",mi)
    cn=np.array([tuple(c.vector) for c in me.corner_normals],np.float64).reshape(-1,3)
    at=me.color_attributes.get("TCol"); tc=np.empty(nl*4,np.float32)
    if at: at.data.foreach_get("color",tc)
    else: tc[:]=1
    d=dict(co=co,vi=vi,ls=ls,lt=lt,mi=mi,cn=cn,tc=tc.reshape(-1,4))
    _CACHE[key]=d; return d

def _rot(a,r):
    a=a.copy()
    for _ in range(r&3): a[:,0],a[:,1]=-a[:,1].copy(),a[:,0].copy()
    return a

def piece_name(set_,case,var="A"):
    if set_=="Water": return "SM_VKT_WaterQuad"
    if set_ in ("Ramp","Stair"): return f"SM_VKT_{set_}_{case}_{var}"
    return f"SM_VKT_{set_}_{CASE_NAMES[case]}_{var}"

def tk_assemble(records,displace=None):
    """records: iterable of (I,J,level,set,case,r,var). Returns dict of arrays for terrain and water."""
    parts={"T":[],"W":[]}
    for (I,J,l,set_,case,r,var) in records:
        if set_=="Cliff" and case==EMPTY: continue
        o=bpy.data.objects.get(piece_name(set_,case,var))
        if o is None: raise KeyError(piece_name(set_,case,var))
        parts["W" if set_=="Water" else "T"].append((tk_cache(o),I,J,l,r))
    out={}
    for key,lst in parts.items():
        if not lst: out[key]=None; continue
        V=[];VI=[];LS=[];MI=[];CN=[];TC=[]; vo=0; lo=0
        for (c,I,J,l,r) in lst:
            co=_rot(c["co"],r); co[:,0]+=3.0*I; co[:,1]+=3.0*J; co[:,2]+=l*TIER
            V.append(co); VI.append(c["vi"]+vo); LS.append(c["ls"]+lo); MI.append(c["mi"]); CN.append(_rot(c["cn"],r)); TC.append(c["tc"])
            vo+=len(co); lo+=len(c["vi"])
        out[key]=dict(co=np.concatenate(V),vi=np.concatenate(VI),ls=np.concatenate(LS),mi=np.concatenate(MI),cn=np.concatenate(CN),tc=np.concatenate(TC))
    if displace and out["T"] is not None: displace(out["T"])
    return out

def tk_mesh_from(arr,name,mats):
    me=bpy.data.meshes.get(name)
    if me is None: me=bpy.data.meshes.new(name)
    else: me.clear_geometry()
    nv=len(arr["co"]); nl=len(arr["vi"]); npo=len(arr["ls"])
    me.vertices.add(nv); me.vertices.foreach_set("co",arr["co"].astype(np.float32).ravel())
    me.loops.add(nl); me.loops.foreach_set("vertex_index",arr["vi"].astype(np.int32))
    me.polygons.add(npo); me.polygons.foreach_set("loop_start",arr["ls"].astype(np.int32))
    me.update(calc_edges=True)
    me.polygons.foreach_set("material_index",arr["mi"].astype(np.int32))
    me.polygons.foreach_set("use_smooth",np.ones(npo,bool))
    me.normals_split_custom_set(arr["cn"].astype(np.float32).tolist())
    at=me.color_attributes.get("TCol") or me.color_attributes.new("TCol","FLOAT_COLOR","CORNER")
    at.data.foreach_set("color",arr["tc"].astype(np.float32).ravel())
    me.materials.clear()
    for m in mats: me.materials.append(m)
    return me

def tk_terrain_coll(name="VK_Terrain"):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name); bpy.data.scenes["VillageKit"].collection.children.link(c)
    return c

def tk_build_chunks(G,prefix="VKT",origin=MAP_ORIGIN,chunk=16,coll=None,displace=None):
    coll=coll or tk_terrain_coll(); made=[]
    for cj in range(0,G.H+1,chunk):
        for ci in range(0,G.W+1,chunk):
            recs=list(tk_tiles(G,ci,cj,min(ci+chunk-1,G.W),min(cj+chunk-1,G.H)))
            arrs=tk_assemble(recs,displace)
            for key,mats in (("T",tk_mats()),("W",[terrain_water_material()])):
                if arrs[key] is None: continue
                nm=f"{prefix}_{'Chunk' if key=='T' else 'Water'}_{ci//chunk}_{cj//chunk}"
                me=tk_mesh_from(arrs[key],nm,mats)
                o=bpy.data.objects.get(nm)
                if o is None: o=bpy.data.objects.new(nm,me); coll.objects.link(o)
                o.data=me; o.location=origin; made.append(o)
    return made

# ---------------------------------------------------------------- verification
def _on_side(k,x,y,eps=1e-4):
    return [abs(y+1.5)<eps,abs(x-1.5)<eps,abs(y-1.5)<eps,abs(x+1.5)<eps][k]
def tk_side_signature(o,k,r=0):
    """side vertices of piece o after rotation r, on world side k: list of (d from corner bit k, z, frozenset normals, frozenset tcols)"""
    c=tk_cache(o); co=_rot(c["co"],r); cn=_rot(c["cn"],r); vi=c["vi"]; tc=c["tc"]
    a=CORNER[k]; b=CORNER[(k+1)%4]; ux,uy=(b[0]-a[0])/3,(b[1]-a[1])/3
    rows={}
    for li,v in enumerate(vi):
        x,y,z=co[v]
        if not _on_side(k,x,y): continue
        d=round((x-a[0])*ux+(y-a[1])*uy,4); key=(d,round(float(z),4))
        e=rows.setdefault(key,[set(),set()])
        e[0].add(tuple(round(float(x_),3) for x_ in cn[li])); e[1].add(tuple(round(float(x_),3) for x_ in tc[li]))
    return {k_:(frozenset(v[0]),frozenset(v[1])) for k_,v in rows.items()}
def tk_expected_side(set_,mask,k):
    a=bool(mask>>k&1); b=bool(mask>>((k+1)%4)&1)
    t=side_type(set_,a,b); tab=side_table(t)
    A=CORNER[k]; B=CORNER[(k+1)%4]; ux,uy=(B[0]-A[0])/3,(B[1]-A[1])/3
    out={}
    for (d,z,ns,tcs) in tab:
        dd=d if (a or t in ("FLAT","BED")) else 3.0-d    # table d is from the high corner
        # outward horizontal direction along the side = away from the high corner
        o=(ux,uy) if a else (-ux,-uy)
        # snap like TB.vert
        px,py=A[0]+ux*dd,A[1]+uy*dd
        qz=round(z/Q)*Q
        key=(round((round(px/Q)*Q-A[0])*ux+(round(py/Q)*Q-A[1])*uy,4),round(qz,4))
        out[key]=(frozenset(tuple(round(float(x_),3) for x_ in (n[0]*o[0],n[0]*o[1],n[1])) for n in ns),frozenset(tuple(round(float(x_),3) for x_ in t_) for t_ in tcs))
    return out,t
def tk_test_T1(verbose=False):
    fails=[]
    for set_ in ("Cliff","Shore"):
        for case,var in [(c_,v_) for c_ in (FULL,EDGE,OUTER,INNER,SADDLE,BEDC) for v_ in VARIANTS.get((set_,c_),("A",))]:
            nm=piece_name(set_,case,var)
            o=bpy.data.objects.get(nm)
            if o is None: continue
            for r in range(4):
                mask=CANON[case]
                for _ in range(r): mask=rotl(mask)
                if set_=="Cliff" and case==BEDC: continue
                for k in range(4):
                    got=tk_side_signature(o,k,r); exp,t=tk_expected_side(set_,mask,k)
                    if set(got.keys())!=set(exp.keys()):
                        fails.append((nm,r,k,t,"pos",sorted(set(got)-set(exp))[:4],sorted(set(exp)-set(got))[:4])); continue
                    for key in exp:
                        if got[key][1]!=exp[key][1]: fails.append((nm,r,k,t,"tcol",key,got[key][1],exp[key][1]))
                        gn={tuple(x) for x in got[key][0]}; en={tuple(x) for x in exp[key][0]}
                        if not all(any(np.allclose(a_,b_,atol=0.004) for b_ in en) for a_ in gn) or not all(any(np.allclose(a_,b_,atol=0.004) for b_ in gn) for a_ in en):
                            fails.append((nm,r,k,t,"normal",key,gn,en))
    return fails

_SIG={}
def _sig(set_,case,r,k,var="A"):
    key=(set_,case,r,k,var)
    if key not in _SIG:
        o=bpy.data.objects[piece_name(set_,case,var)]
        _SIG[key]=tk_side_signature(o,k,r)
    return _SIG[key]
def tk_random_grid(seed,W=12,H=12,mode=None):
    rng=np.random.default_rng(seed); G=TGrid(W,H)
    mode=mode or rng.choice(["smooth","noise","worst"],p=[0.4,0.3,0.3])
    if mode=="smooth":
        f=np.zeros((H,W))
        for _ in range(4):
            cx,cy,r=rng.uniform(0,W),rng.uniform(0,H),rng.uniform(2,6)
            yy,xx=np.mgrid[0:H,0:W]; f+=rng.uniform(1,3)*np.exp(-((xx-cx)**2+(yy-cy)**2)/r**2)
        G.level[:]=np.clip(np.round(f),0,4).astype(np.int32)
    elif mode=="noise": G.level[:]=rng.integers(0,4,(H,W))
    else:
        k=rng.integers(0,3)
        if k==0: G.level[:]=(np.indices((H,W)).sum(0)%2)*rng.integers(1,4)
        elif k==1:
            G.level[:]=rng.integers(0,2,(H,W)); G.level[H//2,W//2]=4; G.level[2,2]=0; G.level[2:4,7:9]=3
        else: G.level[:]=np.clip(rng.integers(-2,5,(H,W)),0,4)
    # water at local minima (strict validation)
    for j in range(H):
        for i in range(W):
            if rng.random()<0.25:
                l=G.level[j,i]; ok=True
                for dj in (-1,0,1):
                    for di in (-1,0,1):
                        ii,jj=G.cell(i+di,j+dj)
                        if G.level[jj,ii]<l: ok=False
                if ok: G.water[j,i]=True
    return G
def tk_test_T3(n=50,seed0=0):
    fails=[]; checked=0
    for t_ in range(n):
        G=tk_random_grid(seed0+t_)
        recs={}
        for rec in tk_tiles(G):
            I,J,l,set_,case,r,var=rec
            if set_=="Water": continue
            recs.setdefault((I,J),{})[l]=rec
        for (I,J),layers in recs.items():
            for (dI,dJ,kA,kB) in ((1,0,1,3),(0,1,2,0)):
                nb=recs.get((I+dI,J+dJ))
                if nb is None: continue
                for l in set(layers)|set(nb):
                    a=layers.get(l); b=nb.get(l)
                    sa=_sig(a[3],a[4],a[5],kA,a[6]) if a and not (a[3]=="Cliff" and a[4]==EMPTY) else {}
                    sb=_sig(b[3],b[4],b[5],kB,b[6]) if b and not (b[3]=="Cliff" and b[4]==EMPTY) else {}
                    sbm={(round(3.0-d,4),z):v for (d,z),v in sb.items()}
                    checked+=1
                    if a and b:
                        if set(sa)!=set(sbm): fails.append((t_,I,J,l,"pos",a[3:6],b[3:6])); continue
                        for key in sa:
                            if sa[key][1]!=sbm[key][1]: fails.append((t_,I,J,l,"tcol",key)); break
                            ga={tuple(x) for x in sa[key][0]}; gb={tuple(x) for x in sbm[key][0]}
                            if not all(any(np.allclose(p,q,atol=0.01) for q in gb) for p in ga): fails.append((t_,I,J,l,"normal",key)); break
                    else:
                        s_=sa or sbm
                        if any(abs(z)>1e-6 for (d,z) in s_): fails.append((t_,I,J,l,"orphan",(a or b)[3:6]))
    return fails,checked

def tk_test_T4(G,objs,step=0.25,margin=0.02):
    """vertical rays over the map: every ray must hit a front face at a plausible height"""
    from mathutils.bvhtree import BVHTree
    dg=bpy.context.evaluated_depsgraph_get()
    trees=[(BVHTree.FromObject(o,dg),o) for o in objs]
    bad=[]; n=0
    xs=np.arange(margin+1.5,3*G.W-1.5,step); ys=np.arange(margin+1.5,3*G.H-1.5,step)
    for x in xs:
        for y in ys:
            n+=1; best=None
            for tr,o in trees:
                hit=tr.ray_cast(Vector((x,y,100.0)),Vector((0,0,-1)))
                if hit[0] is not None and (best is None or hit[0].z>best[0].z): best=hit
            if best is None: bad.append((x,y,"miss")); continue
            if best[1].z<=0: bad.append((x,y,"backface",best[0].z))
    return bad,n

# ---------------------------------------------------------------- terrain material
class _NB:
    def __init__(s,nt): s.nt=nt; s.L=nt.links; s.x=-2000
    def n(s,t,**kw):
        nd=s.nt.nodes.new(t); nd.location=(s.x,0); s.x+=40
        for k,v in kw.items(): setattr(nd,k,v)
        return nd
    def link(s,a,b): s.L.new(a,b)
    def math(s,op,a,b=None,clamp=False):
        m=s.n("ShaderNodeMath",operation=op); m.use_clamp=clamp
        s._in(m.inputs[0],a)
        if b is not None: s._in(m.inputs[1],b)
        return m.outputs[0]
    def _in(s,sock,v):
        if isinstance(v,(int,float)): sock.default_value=v
        else: s.link(v,sock)
    def mix(s,fac,a,b,blend="MIX"):
        m=s.n("ShaderNodeMix",data_type="RGBA",blend_type=blend)
        s._in(m.inputs[0],fac)
        if isinstance(a,tuple): m.inputs[6].default_value=(*a,1)
        else: s.link(a,m.inputs[6])
        if isinstance(b,tuple): m.inputs[7].default_value=(*b,1)
        else: s.link(b,m.inputs[7])
        return m.outputs[2]
    def fmix(s,fac,a,b):
        m=s.n("ShaderNodeMix",data_type="FLOAT"); s._in(m.inputs[0],fac); s._in(m.inputs[2],a); s._in(m.inputs[3],b); return m.outputs[0]
    def smoothstep(s,x,e0,e1):
        m=s.n("ShaderNodeMapRange",interpolation_type="SMOOTHSTEP"); m.clamp=True
        s._in(m.inputs["Value"],x); m.inputs["From Min"].default_value=e0; m.inputs["From Max"].default_value=e1
        return m.outputs[0]
    def scale(s,vec,k):
        m=s.n("ShaderNodeVectorMath",operation="SCALE"); s.link(vec,m.inputs[0]); m.inputs["Scale"].default_value=k; return m.outputs[0]
    def img(s,name,vec,data=False,box=False,ext="REPEAT"):
        t=s.n("ShaderNodeTexImage"); t.image=bpy.data.images[name]; t.extension=ext
        if data: t.image.colorspace_settings.name="Non-Color"
        if box: t.projection="BOX"; t.projection_blend=0.2
        s.link(vec,t.inputs[0]); return t
    def sep(s,col):
        m=s.n("ShaderNodeSeparateColor"); s.link(col,m.inputs[0]); return m.outputs
    def planar_vecs(s,p,k):
        """object-space p scaled by k -> vectors (x,z), (y,z), (x,y) for side/top projections"""
        xyz=s.n("ShaderNodeSeparateXYZ"); s.link(p,xyz.inputs[0])
        out=[]
        for a,b in ((0,2),(1,2),(0,1)):
            c=s.n("ShaderNodeCombineXYZ")
            s.link(s.math("MULTIPLY",xyz.outputs[a],k),c.inputs[0]); s.link(s.math("MULTIPLY",xyz.outputs[b],k),c.inputs[1])
            out.append(c.outputs[0])
        return out
    def normal_weights(s,sharp=0.25):
        """weights (wx, wy, wz) from the world normal (chunks are unrotated, so world == object)"""
        geo=s.n("ShaderNodeNewGeometry"); nn=s.n("ShaderNodeSeparateXYZ"); s.link(geo.outputs["Normal"],nn.inputs[0])
        ax=s.math("ABSOLUTE",nn.outputs[0]); ay=s.math("ABSOLUTE",nn.outputs[1]); az=s.math("ABSOLUTE",nn.outputs[2])
        return ax,ay,az
    def side_sample(s,name,p,k,data=False):
        """biplanar side projection that keeps image v == world z on every facing (Blender's BOX rotates X faces)"""
        vA,vB,vT=s.planar_vecs(p,k)
        tA=s.img(name,vA,data=data); tB=s.img(name,vB,data=data)
        ax,ay,az=s.normal_weights()
        w=s.math("ADD",s.math("DIVIDE",s.math("SUBTRACT",ax,ay),0.35),0.5,clamp=True)   # 1 -> facing X -> use (y,z)
        col=s.mix(w,tA.outputs[0],tB.outputs[0])
        val=s.fmix(w,tA.outputs[0],tB.outputs[0])
        return col,val,(vT,az)

def terrain_material(name="M_VK_Terrain",W=32,H=24,ctl="T_VK_GroundCtl"):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
    out=B.n("ShaderNodeOutputMaterial"); bsdf=B.n("ShaderNodeBsdfPrincipled")
    tc=B.n("ShaderNodeTexCoord"); p=tc.outputs["Object"]
    geo=B.n("ShaderNodeNewGeometry"); nz=B.n("ShaderNodeSeparateXYZ"); B.link(geo.outputs["Normal"],nz.inputs[0]); Nz=nz.outputs[2]
    at=B.n("ShaderNodeAttribute",attribute_name="TCol"); tcs=B.sep(at.outputs["Color"]); A=at.outputs["Alpha"]
    AO,RK,RIM=tcs[0],tcs[1],tcs[2]
    p4=B.scale(p,0.25)
    mac=B.sep(B.img("T_VK_TerrainMacro",B.scale(p,1/48.0),data=True).outputs[0])
    # control map
    wn=B.n("ShaderNodeTexNoise"); wn.inputs["Scale"].default_value=0.35; wn.inputs["Detail"].default_value=2.0; B.link(p,wn.inputs["Vector"])
    wv=B.n("ShaderNodeVectorMath",operation="SUBTRACT"); B.link(wn.outputs["Color"],wv.inputs[0]); wv.inputs[1].default_value=(0.5,0.5,0.5)
    ws=B.n("ShaderNodeVectorMath",operation="SCALE"); B.link(wv.outputs[0],ws.inputs[0]); ws.inputs["Scale"].default_value=1.6
    pw=B.n("ShaderNodeVectorMath",operation="ADD"); B.link(p,pw.inputs[0]); B.link(ws.outputs[0],pw.inputs[1])
    mp=B.n("ShaderNodeMapping"); B.link(pw.outputs[0],mp.inputs[0]); mp.inputs["Scale"].default_value=(1/(3*W),1/(3*H),1); mp.label="CTL_MAP"
    ctl=B.img(ctl,mp.outputs[0],data=True,ext="EXTEND"); ctl.interpolation="Linear"
    cs=B.sep(ctl.outputs[0]); cA=ctl.outputs["Alpha"]
    # grass (two scales)
    g1=B.img("T_VK_Grass_BC",p4)
    mg=B.n("ShaderNodeMapping"); B.link(p,mg.inputs[0]); mg.inputs["Rotation"].default_value=(0,0,math.radians(37)); mg.inputs["Scale"].default_value=(1/13.1,1/13.1,1)
    g2=B.img("T_VK_Grass_BC",mg.outputs[0])
    gcol=B.mix(B.smoothstep(mac[2],0.3,0.7),g1.outputs[0],g2.outputs[0])
    hs=B.n("ShaderNodeHueSaturation"); hs.inputs["Hue"].default_value=0.505; hs.inputs["Saturation"].default_value=0.8; hs.inputs["Value"].default_value=0.97
    B.link(gcol,hs.inputs["Color"]); gcol=hs.outputs[0]
    gH=B.img("T_VK_Grass_H",p4,data=True).outputs[0]
    col=gcol; hgt=gH
    def layer(col,hgt,prefix,w,tau,extra=None,outline=False):
        Hk=B.img(prefix+"_H",p4,data=True).outputs[0]; Ck=B.img(prefix+"_BC",p4).outputs[0]
        v=B.math("SUBTRACT",w,tau); v=B.math("ADD",v,B.math("MULTIPLY",B.math("SUBTRACT",Hk,0.5),0.35))
        v=B.math("ADD",v,B.math("MULTIPLY",B.math("SUBTRACT",mac[2],0.5),0.15))
        mk=B.math("ADD",B.math("DIVIDE",v,0.08),0.5,clamp=True)
        if extra is not None: mk=B.math("MAXIMUM",mk,extra)
        col=B.mix(mk,col,Ck)
        if outline:
            o=B.math("MULTIPLY",B.math("MULTIPLY",mk,B.math("SUBTRACT",1.0,mk)),0.8)
            col=B.mix(o,col,(0.0,0.0,0.0),blend="MULTIPLY") if False else B.mix(B.math("MULTIPLY",o,0.25),col,(0.25,0.2,0.15))
        hgt=B.fmix(mk,hgt,Hk)
        return col,hgt
    sandx=B.smoothstep(A,0.2,0.45)
    col,hgt=layer(col,hgt,"T_VK_Sand",cs[2],0.50,extra=sandx)
    col,hgt=layer(col,hgt,"T_VK_Dirt",cs[0],0.45,outline=True)
    col,hgt=layer(col,hgt,"T_VK_Cobble",cs[1],0.45,outline=True)
    # rim highlight on the turf crest
    col=B.mix(B.math("MULTIPLY",RIM,0.2),col,(0.78,0.86,0.42))
    # cliff (box projection in map space)
    clC,_,_=B.side_sample("T_VK_Cliff_BC",p,1/6.0)
    _,clH,_=B.side_sample("T_VK_Cliff_H",p,1/6.0,data=True)
    rockW=B.math("MAXIMUM",RK,B.smoothstep(Nz,0.80,0.55))
    rockW=B.math("MAXIMUM",rockW,B.smoothstep(cA,0.45,0.65))
    # moss on up-facing rock
    mo=B.img("T_VK_Moss_BC",B.scale(p,1.0)); moH=B.img("T_VK_Moss_H",B.scale(p,1.0),data=True).outputs[0]
    mz=B.smoothstep(B.math("ADD",Nz,B.math("MULTIPLY",B.math("SUBTRACT",moH,0.5),0.75)),0.54,0.78)
    ccol=B.mix(mz,clC,mo.outputs[0])
    col=B.mix(rockW,col,ccol); hgt=B.fmix(rockW,hgt,clH)
    # AO, wet, macro tint
    col=B.mix(1.0,col,B.n("ShaderNodeCombineColor").outputs[0],blend="MULTIPLY") if False else col
    aoc=B.n("ShaderNodeCombineColor"); B.link(AO,aoc.inputs[0]); B.link(AO,aoc.inputs[1]); B.link(AO,aoc.inputs[2])
    col=B.mix(1.0,col,aoc.outputs[0],blend="MULTIPLY")
    wet=B.smoothstep(A,0.6,0.95)
    col=B.mix(B.math("MULTIPLY",wet,0.4),col,(0.0,0.0,0.0))
    mt=B.math("ADD",0.9,B.math("MULTIPLY",mac[0],0.2))
    mtc=B.n("ShaderNodeCombineColor"); B.link(mt,mtc.inputs[0]); B.link(mt,mtc.inputs[1]); B.link(mt,mtc.inputs[2])
    col=B.mix(1.0,col,mtc.outputs[0],blend="MULTIPLY")
    col=B.mix(B.math("MULTIPLY",mac[1],0.3),col,B.mix(1.0,col,(1.05,1.0,0.8),blend="MULTIPLY"))
    B.link(col,bsdf.inputs["Base Color"])
    rough=B.fmix(rockW,0.9,0.85); rough=B.fmix(wet,rough,0.35)
    B.link(rough,bsdf.inputs["Roughness"]); bsdf.inputs["Specular IOR Level"].default_value=0.25
    bump=B.n("ShaderNodeBump"); B.link(hgt,bump.inputs["Height"]); bump.inputs["Distance"].default_value=0.05
    B.link(B.fmix(rockW,0.4,0.8),bump.inputs["Strength"])
    B.link(bump.outputs[0],bsdf.inputs["Normal"])
    B.link(bsdf.outputs[0],out.inputs[0])
    return m

def tk_ground_ctl(G,name="T_VK_GroundCtl"):
    """RGBA8 one texel per cell: R dirt(+wear) G cobble B sand(water forced) A rock"""
    Wd,Hd=G.W,G.H
    arr=np.zeros((Hd,Wd,4),np.float32)
    gnd=G.ground
    arr[...,0]=np.maximum(gnd==1,G.wear/255.0); arr[...,1]=(gnd==2); arr[...,2]=np.maximum(gnd==3,G.water); arr[...,3]=(gnd==4)
    img=bpy.data.images.get(name)
    if img is None: img=bpy.data.images.new(name,Wd,Hd,alpha=True,float_buffer=False,is_data=True)
    elif tuple(img.size)!=(Wd,Hd):
        new=bpy.data.images.new(name+"_new",Wd,Hd,alpha=True,float_buffer=False,is_data=True)
        for m in bpy.data.materials:
            if m.node_tree:
                for nd in m.node_tree.nodes:
                    if nd.type=="TEX_IMAGE" and nd.image==img: nd.image=new
        bpy.data.images.remove(img); new.name=name; img=new
    img.colorspace_settings.name="Non-Color"
    img.pixels.foreach_set(arr.ravel())       # row 0 of the array = cell row j=0 = bottom of the image (v=0)
    img.update(); img.pack()
    return img
def tk_set_ctl_mapping(G,mat="M_VK_Terrain"):
    m=bpy.data.materials[mat]
    for nd in m.node_tree.nodes:
        if nd.type=="MAPPING" and nd.label=="CTL_MAP": nd.inputs["Scale"].default_value=(1/(3*G.W),1/(3*G.H),1)

# ---------------------------------------------------------------- world-space displacement D (horizontal only)
_M32=np.uint64(0xffffffff)
def _h32v(ix,iy,iz,seed):
    h=np.full(ix.shape,seed&0xffffffff,np.uint64)
    with np.errstate(over="ignore"):
        h^=(ix.astype(np.int64).astype(np.uint64)*np.uint64(0x8da6b343))&_M32
        h^=(iy.astype(np.int64).astype(np.uint64)*np.uint64(0xd8163841))&_M32
        h^=(iz.astype(np.int64).astype(np.uint64)*np.uint64(0xcb1ab31f))&_M32
        h^=h>>np.uint64(16); h=(h*np.uint64(0x7feb352d))&_M32; h^=h>>np.uint64(15); h=(h*np.uint64(0x846ca68b))&_M32; h^=h>>np.uint64(16)
    return h&_M32
def vnoise(x,y,z,seed):
    ix=np.floor(x); iy=np.floor(y); iz=np.floor(z)
    fx,fy,fz=x-ix,y-iy,z-iz
    ux,uy,uz=fx*fx*(3-2*fx),fy*fy*(3-2*fy),fz*fz*(3-2*fz)
    ix=ix.astype(np.int64); iy=iy.astype(np.int64); iz=iz.astype(np.int64)
    def v(dx,dy,dz): return _h32v(ix+dx,iy+dy,iz+dz,seed).astype(np.float64)/4294967296.0*2-1
    c00=v(0,0,0)*(1-ux)+v(1,0,0)*ux; c10=v(0,1,0)*(1-ux)+v(1,1,0)*ux
    c01=v(0,0,1)*(1-ux)+v(1,0,1)*ux; c11=v(0,1,1)*(1-ux)+v(1,1,1)*ux
    return (c00*(1-uy)+c10*uy)*(1-uz)+(c01*(1-uy)+c11*uy)*uz
def _bilinear_cells(arr,x,y):
    Hh,Ww=arr.shape; u=np.clip(x/3.0-0.5,0,Ww-1); v=np.clip(y/3.0-0.5,0,Hh-1)
    i0=np.floor(u).astype(int); j0=np.floor(v).astype(int); i1=np.minimum(i0+1,Ww-1); j1=np.minimum(j0+1,Hh-1)
    fu=u-i0; fv=v-j0
    return (arr[j0,i0]*(1-fu)+arr[j0,i1]*fu)*(1-fv)+(arr[j1,i0]*(1-fu)+arr[j1,i1]*fu)*fv
def make_displace(G,amp=1.0):
    stiff=G.stiff.astype(np.float64); XM,YM=3.0*G.W,3.0*G.H
    def D(p):
        x,y,z=p[:,0],p[:,1],p[:,2]
        s=_bilinear_cells(stiff,x,y); t=np.clip(s/0.5,0,1); A=amp*(1-t*t*(3-2*t))
        e=np.clip(np.minimum(np.minimum(x,XM-x),np.minimum(y,YM-y))/3.0,0,1); A=A*e*e*(3-2*e)
        dx=0.28*vnoise(x/6,y/6,z/4,11)+0.08*vnoise(x/1.6,y/1.6,z/1.6,13)
        dy=0.28*vnoise(x/6,y/6,z/4,12)+0.08*vnoise(x/1.6,y/1.6,z/1.6,14)
        return np.stack([A*dx,A*dy,np.zeros_like(x)],1)
    def apply(arr):
        co=arr["co"]; e=0.02
        J=np.zeros((len(co),3,3))
        for a in range(3):
            dp=np.zeros(3); dp[a]=e
            J[:,:,a]=(D(co+dp)-D(co-dp))/(2*e)
        J+=np.eye(3)[None]
        co2=co+D(co)
        # loop normals: n' = normalize(J^-T n)
        JiT=np.linalg.inv(J).transpose(0,2,1)
        n=np.einsum("lij,lj->li",JiT[arr["vi"]],arr["cn"])
        n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-12
        arr["co"]=co2; arr["cn"]=n
        arr["detJ"]=float(np.min(J[:,0,0]*J[:,1,1]-J[:,0,1]*J[:,1,0]))
    apply.D=D
    return apply

# ---------------------------------------------------------------- ramps (canonical Edge, N high; ramp on E / W / both crossing sides)
RAMP_X=0.5            # half-ramp spans x in [RAMP_X, 1.5]  (2.0 m ramp centred on the side)
RAMP_N=(0.0,-0.5/math.hypot(0.5,1.0),1.0/math.hypot(0.5,1.0))
RAMP_T=(1.0,0.0,0.0,0.0)
CHEEK_T=(0.88,1.0,0.0,0.0)     # ramp/stair cheeks: rock, light AO (they often face away from the sun)
def _ramp_z(y): return (y-1.5)*0.5
def _ramp_n(y): return TUP if (abs(y-1.5)<1e-6 or abs(y+1.5)<1e-6) else RAMP_N
def _poly_yz(tb,pts,x,normal,tcol):
    """triangulate a planar polygon in the plane x=const given as [(y,z)...] CCW as seen from +normal"""
    L=[]
    for p in pts:
        if not L or math.hypot(p[0]-L[-1][0],p[1]-L[-1][1])>1e-6: L.append(p)
    if math.hypot(L[0][0]-L[-1][0],L[0][1]-L[-1][1])<1e-6: L.pop()
    res=delaunay_2d_cdt([Vector(p) for p in L],[],[list(range(len(L)))],1,1e-7)
    omap=[o_[0] for o_ in res[3]]; ids=[tb.vert((x,p[0],p[1])) for p in L]
    for f in res[2]:
        q=[ids[omap[k]] for k in f]
        V=[Vector(tb.v[k]) for k in q]
        if (V[1]-V[0]).cross(V[2]-V[0]).dot(Vector(normal))<0: q=q[::-1]
        tb.face(q,[normal]*3,[tcol]*3)
def _ramp_surface(tb,x0,x1,ncol):
    xs=[x0+(x1-x0)*j/(ncol-1) for j in range(ncol)]; ys=[-1.5+0.5*i for i in range(7)]
    ids=[[tb.vert((x,y,_ramp_z(y))) for y in ys] for x in xs]
    for j in range(ncol-1):
        for i in range(6):
            q=[ids[j][i],ids[j+1][i],ids[j+1][i+1],ids[j][i+1]]
            ns=[_ramp_n(ys[i]),_ramp_n(ys[i]),_ramp_n(ys[i+1]),_ramp_n(ys[i+1])]
            V=[Vector(tb.v[k]) for k in q]
            if (V[1]-V[0]).cross(V[3]-V[0]).z<0: q=q[::-1]; ns=ns[::-1]
            tb.face(q,ns,[RAMP_T]*4)
def gen_ramp_half_e():
    tb=TB(); P=P_CLIFF; RN=row_normals(P,len(P)-1); T3=list(range(TOP_ROW+1))
    ncol=int(round((RAMP_X+1.5)/0.25))+1
    fr=_front_edge(13)[:ncol]                  # columns x=-1.5..RAMP_X
    sweep(tb,fr,P,TOP_ROW,CLIFF_LAST)
    # top region: row3 curve W->RAMP_X, up the cheek top edge, N side FLAT from RAMP_X to NW, W side down
    xr=RAMP_X
    top=curve_ents(P,RN,fr,TOP_ROW)
    top+=[(xr,y,0.0,TUP,FLAT_T) for y in (0.5,1.0,1.5) if y>1.5-P[TOP_ROW][0]+1e-6]
    top+=[(*side_pos(2,d,2),0.0,TUP,FLAT_T) for d in (0,0.5,1.0,1.5,2.0,2.5,3.0) if 1.5-d<=xr+1e-6]
    top+=side_ents(P,RN,3,3,T3)
    region(tb,top,0.0,FLAT_T)
    _ramp_surface(tb,xr,1.5,int(round((1.5-xr)/0.5))+1)
    # profile at column x=xr and its crossing with the ramp line
    prof=[(1.5-P[i][0],P[i][1]) for i in range(TOP_ROW,CLIFF_LAST+1)]
    cut=None
    for i in range(len(prof)-1):
        (y0,z0),(y1,z1)=prof[i],prof[i+1]
        f0=z0-_ramp_z(y0); f1=z1-_ramp_z(y1)
        if f0>=0 and f1<0: t=f0/(f0-f1); cut=(i,(y0+(y1-y0)*t,z0+(z1-z0)*t)); break
    ci,cp=cut
    ramp_ys=[-1.5+0.5*k for k in range(7)]
    # upper cheek (faces +x): top edge from N side down the profile to the cut, then back up the ramp line
    up=[(1.5,0.0),(1.0,0.0),(0.5,0.0)]; up=[p for p in up if p[0]>prof[0][0]+1e-6]
    up+=prof[:ci+1]+[cp]+[(y,_ramp_z(y)) for y in ramp_ys if y>cp[0]+1e-6]
    _poly_yz(tb,up,xr,(1.0,0.0,0.0),CHEEK_T)
    # lower cheek (faces -x): floor from the ramp foot to under the toe, up the profile to the cut, down the ramp line
    kx=None
    for k in range(ci+1,len(prof)-1):
        if prof[k][1]>=-1.5 and prof[k+1][1]<-1.5:
            t=(prof[k][1]+1.5)/(prof[k][1]-prof[k+1][1]); kx=k; yx=prof[k][0]+(prof[k+1][0]-prof[k][0])*t; break
    lo=[(-1.5,-1.5)]+[(y,-1.5) for y in (-1.0,-0.5,0.0) if y<yx-0.02]+[(yx,-1.5)]
    lo+=[prof[k] for k in range(kx,ci,-1)]+[cp]+[(y,_ramp_z(y)) for y in reversed(ramp_ys) if y<cp[0]-1e-6]
    _poly_yz(tb,lo,xr,(-1.0,0.0,0.0),CHEEK_T)
    return tb
def gen_ramp_mid():
    tb=TB(); _ramp_surface(tb,-1.5,1.5,7); return tb
def mirror_tb(tb):
    out=TB()
    idmap=[out.vert((-p[0],p[1],p[2])) for p in tb.v]
    for f,ns,cs,mi in zip(tb.f,tb.ln,tb.lc,tb.mi):
        out.face([idmap[k] for k in f][::-1],[(-n[0],n[1],n[2]) for n in ns][::-1],cs[::-1],mi)
    return out
def tk_build_ramps():
    coll=tk_pieces_coll()
    e=gen_ramp_half_e()
    tk_finish(e,"SM_VKT_Ramp_HalfE_A",coll,dict(set="Ramp",case="HalfE",var="A",mask=12))
    tk_finish(mirror_tb(e),"SM_VKT_Ramp_HalfW_A",coll,dict(set="Ramp",case="HalfW",var="A",mask=12))
    tk_finish(gen_ramp_mid(),"SM_VKT_Ramp_Mid_A",coll,dict(set="Ramp",case="Mid",var="A",mask=12))

DIRV={1:(0,1),2:(1,0),3:(0,-1),4:(-1,0)}
def _is_stair(G,c,l,r):
    for cs in (1,3):
        ws=(cs+r)%4; a=c[ws]; b=c[(ws+1)%4]
        lowc=a if a[0]<b[0] else b
        if lowc[0]==l-1 and G.ramp[lowc[3],lowc[2]] and G.stair[lowc[3],lowc[2]]: return True
    return False
def ramp_override(G,c,l,r):
    """c: corners [(level,water,i,j)] ; returns 'HalfE'/'HalfW'/'Mid' or None for an EDGE layer l with rotation r"""
    hit=set()
    for cs in (1,3):                               # canonical crossing sides
        ws=(cs+r)%4; a=c[ws]; b=c[(ws+1)%4]
        lowc,highc=(a,b) if a[0]<b[0] else (b,a)
        if lowc[0]!=l-1 or highc[0]!=l: continue
        d=G.ramp[lowc[3],lowc[2]]
        if d and DIRV[d]==(highc[2]-lowc[2],highc[3]-lowc[3]): hit.add(cs)
    if hit=={1,3}: return "Mid"
    if hit=={1}: return "HalfE"
    if hit=={3}: return "HalfW"
    return None

def terrain_water_material(name="M_VKT_Water"):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
    out=B.n("ShaderNodeOutputMaterial"); b=B.n("ShaderNodeBsdfPrincipled")
    tc=B.n("ShaderNodeTexCoord"); p=tc.outputs["Object"]
    st=B.n("ShaderNodeMapping"); B.link(p,st.inputs[0]); st.inputs["Scale"].default_value=(0.18,1.4,1.0)
    n1=B.n("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value=0.9; n1.inputs["Detail"].default_value=4.0; B.link(st.outputs[0],n1.inputs["Vector"])
    n2=B.n("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value=0.12; n2.inputs["Detail"].default_value=1.0; B.link(p,n2.inputs["Vector"])
    col=B.mix(B.smoothstep(n2.outputs["Fac"],0.35,0.65),(0.035,0.17,0.2),(0.06,0.27,0.28))
    col=B.mix(B.math("MULTIPLY",B.smoothstep(n1.outputs["Fac"],0.62,0.8),0.35),col,(0.55,0.75,0.75))
    B.link(col,b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.05; b.inputs["Specular IOR Level"].default_value=0.6
    b.inputs["Alpha"].default_value=0.9
    b.inputs["Emission Strength"].default_value=0.0
    bump=B.n("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.15; bump.inputs["Distance"].default_value=0.04
    B.link(n1.outputs["Fac"],bump.inputs["Height"]); B.link(bump.outputs[0],b.inputs["Normal"])
    B.link(b.outputs[0],out.inputs[0])
    try: m.surface_render_method="DITHERED"
    except Exception: pass
    m.use_backface_culling=False
    m.diffuse_color=(0.05,0.22,0.24,1)
    return m


def tk_build_lipgrass():
    """SM_VKT_LipGrass: 1 m fringe of grass tufts on a cliff crest (origin on the crest, facing -Y).
    The tufts grow upright and lean out over the lip; nothing hangs, so the grass/flower texture is never upside down."""
    k=NK(); rng=random.Random(5)
    nf=lambda co: Vector((0,-0.35,1)).normalized()
    ao=lambda co:(0.78+0.22*min(1.0,max(0.0,co.z/0.35)),0.6)
    for i in range(6):                                       # outer row: leans out over the edge
        x=-0.55+0.22*i+rng.uniform(-0.05,0.05)
        w=rng.uniform(0.3,0.42); h=rng.uniform(0.28,0.42)
        U=Vector((rng.uniform(-0.15,0.15),-rng.uniform(0.45,0.75),1.0))
        k.lcard((x,-0.02,-0.06),(1,0,0),U,w,h,"tallgrass",flip=rng.random()<0.5,arch=0.1,rows=2,cols=2,nfn=nf,aofn=ao)
    for i in range(4):                                       # inner row: shorter, nearly upright, reads from above
        x=-0.45+0.3*i+rng.uniform(-0.06,0.06)
        U=Vector((rng.uniform(-0.2,0.2),-0.25,1.0))
        k.lcard((x,0.12,-0.03),(1,0,0),U,0.3,rng.uniform(0.18,0.26),"tallgrass",flip=rng.random()<0.5,rows=1,cols=2,nfn=nf,aofn=ao)
    return nk_finish(k,"SM_VKT_LipGrass",tk_pieces_coll(),bark_ao=None)

def cliff_rock_material(name="M_VKT_CliffRock"):
    """the terrain's cliff stone for separate rock pieces: cliff albedo + height bump (object-space box projection),
    moss on up-facing parts like the terrain cliffs"""
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
    out=B.n("ShaderNodeOutputMaterial"); bsdf=B.n("ShaderNodeBsdfPrincipled")
    tc=B.n("ShaderNodeTexCoord"); p=B.scale(tc.outputs["Object"],1/6.0)
    bc=B.img("T_VK_Cliff_BC",p,box=True); hh=B.img("T_VK_Cliff_H",p,data=True,box=True)
    geo=B.n("ShaderNodeNewGeometry"); nz=B.n("ShaderNodeSeparateXYZ"); B.link(geo.outputs["Normal"],nz.inputs[0])
    mo=B.img("T_VK_Moss_BC",B.scale(tc.outputs["Object"],1.0),box=True)
    hs=B.n("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value=0.55; hs.inputs["Value"].default_value=0.92
    B.link(bc.outputs[0],hs.inputs["Color"])                  # the terrain darkens/greys its cliffs (AO, macro)
    col=B.mix(B.smoothstep(nz.outputs[2],0.62,0.85),hs.outputs[0],mo.outputs[0])
    vc=B.n("ShaderNodeVertexColor",layer_name="Col")
    col=B.mix(1.0,col,vc.outputs[0],blend="MULTIPLY")
    B.link(col,bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value=0.88; bsdf.inputs["Specular IOR Level"].default_value=0.25
    bump=B.n("ShaderNodeBump"); B.link(hh.outputs[0],bump.inputs["Height"]); bump.inputs["Strength"].default_value=0.6
    B.link(bump.outputs[0],bsdf.inputs["Normal"]); B.link(bsdf.outputs[0],out.inputs[0])
    return m

def tk_build_ramp_shoulder():
    """SM_VKT_RampShoulder: rock shoulder where a cliff ends beside a ramp or stair (hides the cliff's end cap and
    steps down along the ramp side). Local frame: origin on the cliff line at the cap, +Y uphill, the cliff on -X,
    the ramp on +X, z=0 = the lower level, the cliff top at z=TIER."""
    k=NK()
    # the ramp runs from y=-1.5 (foot, z 0) to y=+1.5 (top, z TIER) and cuts 1.5 m into the upper terrace, so the
    # rocks cover the whole side: the cut wall above the ramp (y 0..1.5) and the cheek below it (y -1.5..0)
    boulder(k,(0.05,1.05,0.6),(1.35,1.35,1.1),407,mi=ROCK,cuts=7,sub=2,rot=0.8)
    boulder(k,(-0.15,0.25,-0.05),(1.45,1.55,TIER+0.22),401,mi=ROCK,cuts=8,sub=2,rot=0.3)
    boulder(k,(0.0,-0.65,-0.05),(1.15,1.2,1.1),403,mi=ROCK,cuts=7,sub=2,rot=1.1)
    boulder(k,(0.1,-1.35,-0.05),(0.8,0.85,0.6),405,mi=ROCK,cuts=6,sub=2,rot=2.0)
    o=nk_finish(k,"SM_VKT_RampShoulder",tk_pieces_coll(),bark_ao=(0.72,1.4))
    o.data.materials[0]=cliff_rock_material()
    return o

def tk_ramp_shoulders(G,coll,origin=MAP_ORIGIN,name="SM_VKT_RampShoulder"):
    """place a rock shoulder at both ends of every ramp/stair run (where the cliff is cut by the ramp)"""
    src=bpy.data.objects.get(name) or tk_build_ramp_shoulder()
    out=[]
    for (j,i) in zip(*np.nonzero(G.ramp)):
        d=int(G.ramp[j,i]); fx,fy=((0,1),(1,0),(0,-1),(-1,0))[d-1]
        for sx,sy in ((fy,-fx),(-fy,fx)):
            ni,nj=i+sx,j+sy
            if 0<=ni<G.W and 0<=nj<G.H and G.ramp[nj,ni]==d: continue          # not an end of the run
            x=3*i+1.5+sx*1.0+fx*1.5; y=3*j+1.5+sy*1.0+fy*1.5; z=float(G.level[j,i])*TIER
            o=bpy.data.objects.new(name+"_inst",src.data); coll.objects.link(o)
            o.location=(origin[0]+x,origin[1]+y,origin[2]+z)
            o.rotation_euler=(0.0,0.0,math.atan2(fy,fx)-math.pi/2)
            if (fy,-fx)!=(-sx,-sy): o.scale=(-1.0,1.0,1.0)                        # mirrored for the other side
            out.append(o)
    return out

def tk_add_random_ramps(G,rng,tries=40):
    """insert valid ramps (validation rule 2) into a grid"""
    D4=((0,1),(1,0),(0,-1),(-1,0))
    for _ in range(tries):
        i=int(rng.integers(1,G.W-1)); j=int(rng.integers(1,G.H-1)); d=int(rng.integers(1,5)); di,dj=D4[d-1]
        hi,hj,li,lj=i+di,j+dj,i-di,j-dj
        if not (0<=hi<G.W and 0<=hj<G.H and 0<=li<G.W and 0<=lj<G.H): continue
        L=G.level[j,i]
        if G.water[j,i] or G.level[hj,hi]!=L+1 or G.level[lj,li]!=L or G.water[lj,li] or G.water[hj,hi] or G.ramp[j,i]: continue
        ok=True
        for s_ in (-1,1):
            si,sj=i+s_*dj,j+s_*di
            if not (0<=si<G.W and 0<=sj<G.H): ok=False; break
            if not ((G.level[sj,si]==L and 0<=si+di<G.W and 0<=sj+dj<G.H and G.level[sj+dj,si+di]==L+1) or G.ramp[sj,si]==d): ok=False
        # the high cell's other neighbours must not create a second ramp layer ambiguity
        if ok:
            fl=bool(rng.random()<0.4)
            for s_ in (-1,1):
                si,sj=i+s_*dj,j+s_*di
                if G.ramp[sj,si]==d: fl=bool(G.stair[sj,si])
            G.ramp[j,i]=d; G.stair[j,i]=fl
    return G
def tk_test_T3r(n=40,seed0=100):
    """T3 with ramps; the ramp foot (canonical S side) is the only allowed open edge"""
    fails=[]; checked=0
    for t_ in range(n):
        rng=np.random.default_rng(seed0+t_)
        G=tk_random_grid(seed0+t_,mode="smooth"); G.water[:]=False
        tk_add_random_ramps(G,rng,80)
        recs={}
        for rec in tk_tiles(G):
            I,J,l,set_,case,r,var=rec
            if set_=="Water": continue
            recs.setdefault((I,J),{})[l]=rec
        for (I,J),layers in recs.items():
            for (dI,dJ,kA,kB) in ((1,0,1,3),(0,1,2,0)):
                nb=recs.get((I+dI,J+dJ))
                if nb is None: continue
                for l in set(layers)|set(nb):
                    a=layers.get(l); b=nb.get(l)
                    sa=_sig(a[3],a[4],a[5],kA,a[6]) if a and not (a[3]=="Cliff" and a[4]==EMPTY) else {}
                    sb=_sig(b[3],b[4],b[5],kB,b[6]) if b and not (b[3]=="Cliff" and b[4]==EMPTY) else {}
                    sbm={(round(3.0-d,4),z):v for (d,z),v in sb.items()}
                    checked+=1
                    if a and b and sa and sbm:
                        if set(sa)!=set(sbm): fails.append((t_,I,J,l,"pos",a[3:6],b[3:6]))
                    else:
                        who=a if sa else b; side=kA if sa else kB
                        if who and who[3] in ("Ramp","Stair") and side==(0+who[5])%4: continue      # ramp foot
                        s_=sa or sbm
                        if any(abs(z)>1e-6 for (d,z) in s_): fails.append((t_,I,J,l,"orphan",(a or b)[3:6],side))
    return fails,checked

# ---------------------------------------------------------------- stairs (same footprint as ramps, 6 risers x 0.25 in ASHLAR)
STAIR_OUT=[(-1.5,-1.5),(-1.25,-1.5),(-1.25,-1.25),(-0.75,-1.25),(-0.75,-1.0),(-0.25,-1.0),(-0.25,-0.75),
           (0.25,-0.75),(0.25,-0.5),(0.75,-0.5),(0.75,-0.25),(1.25,-0.25),(1.25,0.0),(1.5,0.0)]
def _stair_z(y):
    z=-1.5
    for k in range(0,len(STAIR_OUT)-1):
        (y0,z0),(y1,z1)=STAIR_OUT[k],STAIR_OUT[k+1]
        if abs(z0-z1)<1e-9 and y0-1e-9<=y<=y1+1e-9: return z0
    return z
def _stairs(tb,xa,xb):
    ST=(1.0,0.0,0.0,0.0)
    ncol=int(round((xb-xa)/0.5))
    for c in range(ncol):
        _stairs_strip(tb,xa+0.5*c,xa+0.5*(c+1),ST)
def _stairs_strip(tb,x0,x1,ST):
    for k in range(len(STAIR_OUT)-1):
        (y0,z0),(y1,z1)=STAIR_OUT[k],STAIR_OUT[k+1]
        if abs(z0-z1)<1e-9:   # tread
            q=[tb.vert((x0,y0,z0)),tb.vert((x1,y0,z0)),tb.vert((x1,y1,z1)),tb.vert((x0,y1,z1))]; n=(0.0,0.0,1.0)
        else:                 # riser facing -y
            q=[tb.vert((x0,y0,z0)),tb.vert((x0,y1,z1)),tb.vert((x1,y1,z1)),tb.vert((x1,y0,z0))]; n=(0.0,-1.0,0.0)
        V=[Vector(tb.v[i]) for i in q]
        if (V[1]-V[0]).cross(V[3]-V[0]).dot(Vector(n))<0: q=q[::-1]
        tb.face(q,[n]*4,[ST]*4,mi=1)
def gen_stair_half_e():
    """like gen_ramp_half_e but the walking surface is the stepped STAIR_OUT outline"""
    tb=TB(); P=P_CLIFF; RN=row_normals(P,len(P)-1); T3=list(range(TOP_ROW+1))
    ncol=int(round((RAMP_X+1.5)/0.25))+1
    fr=_front_edge(13)[:ncol]
    sweep(tb,fr,P,TOP_ROW,CLIFF_LAST)
    xr=RAMP_X
    top=curve_ents(P,RN,fr,TOP_ROW)
    top+=[(xr,y,0.0,TUP,FLAT_T) for y in (0.5,1.0,1.5) if y>1.5-P[TOP_ROW][0]+1e-6]
    top+=[(*side_pos(2,d,2),0.0,TUP,FLAT_T) for d in (0,0.5,1.0,1.5,2.0,2.5,3.0) if 1.5-d<=xr+1e-6]
    top+=side_ents(P,RN,3,3,T3)
    region(tb,top,0.0,FLAT_T)
    _stairs(tb,xr,1.5)
    prof=[(1.5-P[i][0],P[i][1]) for i in range(TOP_ROW,CLIFF_LAST+1)]
    ci=None
    for i in range(len(prof)-1):
        (y0,z0),(y1,z1)=prof[i],prof[i+1]
        f0=z0-_stair_z(y0); f1=z1-_stair_z(y1)
        if f0>=0 and f1<0:
            lo_,hi_=0.0,1.0
            for _ in range(40):
                m=(lo_+hi_)/2; ym=y0+(y1-y0)*m; zm=z0+(z1-z0)*m
                if zm-_stair_z(ym)>=0: lo_=m
                else: hi_=m
            t=lo_; cp=(y0+(y1-y0)*t,_stair_z(y0+(y1-y0)*t)); ci=i; break
    upper=[p for p in STAIR_OUT if p[0]>cp[0]+1e-6 and p[1]<-1e-9]
    ytop=min(p[0] for p in STAIR_OUT if p[1]>=-1e-9)
    up=[(ytop,0.0)]+[(y,0.0) for y in (1.0,0.5) if prof[0][0]+1e-6<y<ytop-1e-6]
    up+=prof[:ci+1]+[cp]+upper
    _poly_yz(tb,up,xr,(1.0,0.0,0.0),CHEEK_T)
    # lower cheek: everything under the stair outline (the part inside the cliff is enclosed and never seen)
    under=[p for p in STAIR_OUT if -1.5+1e-9<p[1]<-1e-9]
    lo=[(y,-1.5) for y in (under[0][0],-1.0,-0.5,0.0,0.5,1.0,under[-1][0])]+under[::-1]
    _poly_yz(tb,lo,xr,(-1.0,0.0,0.0),CHEEK_T)
    return tb
def gen_stair_mid():
    tb=TB(); _stairs(tb,-1.5,1.5); return tb
def tk_build_stairs():
    coll=tk_pieces_coll()
    e=gen_stair_half_e()
    tk_finish(e,"SM_VKT_Stair_HalfE_A",coll,dict(set="Stair",case="HalfE",var="A",mask=12))
    tk_finish(mirror_tb(e),"SM_VKT_Stair_HalfW_A",coll,dict(set="Stair",case="HalfW",var="A",mask=12))
    tk_finish(gen_stair_mid(),"SM_VKT_Stair_Mid_A",coll,dict(set="Stair",case="Mid",var="A",mask=12))

# ---------------------------------------------------------------- built edges: retaining wall / foundation drop (Kit pieces)
# origin on the cell border at the LOW floor, face toward -Y (the low cell), covers one tier (1.5 m) of cliff
def tkp_retaining_wall(k,kind="ashlar",seed=3):
    rnd=random.Random(seed)
    face=-0.45
    k.box((0,-0.30,-0.28),(3.0,0.5,0.64),STONE_BLOCK,bevel=0)                       # hidden skirt / footing
    mi=ASHLAR if kind=="ashlar" else STONE
    vs=k.box((0,(face+0.22)/2,0.75),(3.0,0.22-face,1.5),mi,bevel=0)
    for v in vs:                                                                     # gentle batter: base 6 cm proud
        if v.co.y<face+0.01: v.co.y-=0.06*(1-min(1,max(0,v.co.z/1.5)))
    grid_cut(k,vs,0.5)
    if kind=="ashlar":
        x=-1.5
        while x<1.49:
            w=min(rnd.uniform(0.8,1.2),1.5-x)
            if 1.5-(x+w)<0.4: w=1.5-x
            k.box((x+w/2,face/2-0.02,1.57),(w-0.02,-face+0.34,0.16),STONE_BLOCK,rot=(0,0,rnd.uniform(-0.01,0.01)),bevel=0.03,segs=2,jitter=0.006,seed=int(x*100)+seed)
            x+=w
        for xx in (-0.75,0.75):                                                       # weep holes
            k.box((xx,face-0.01,0.35),(0.12,0.04,0.12),VOID,bevel=0)
    else:
        for i in range(3):
            rock(k,(-1.0+i*1.0+rnd.uniform(-0.15,0.15),face-0.04,0.18),(0.8,0.3,0.36),seed=seed*7+i,tilt=0.03,segs=1)
def tkp_retaining_end(k,seed=5):
    """pier that closes a retaining wall run (place at the run's end, x = +/-1.5)"""
    k.box((0,-0.2,-0.3),(0.8,0.9,0.6),STONE_BLOCK,bevel=0)
    k.box((0,-0.12,0.8),(0.62,0.72,1.6),ASHLAR,bevel=0.03,segs=2)
    k.box((0,-0.12,1.66),(0.76,0.86,0.16),STONE_BLOCK,bevel=0.04,segs=2)
    k.box((0,-0.12,1.82),(0.5,0.6,0.16),STONE_BLOCK,bevel=0.04,segs=2)
TKP_SPECS=[("SM_VK_RetainingWall",lambda k: tkp_retaining_wall(k,"ashlar"),dict(wobble=False,grime=True)),
           ("SM_VK_Foundation_Drop",lambda k: tkp_retaining_wall(k,"rubble"),dict(wobble=False,grime=True)),
           ("SM_VK_RetainingWall_End",tkp_retaining_end,dict(wobble=False,grime=True))]
def tk_build_edge_pieces():
    coll=bpy.data.collections["VK_Pieces"]; out=[]
    for n,fn,kw in TKP_SPECS:
        k=Kit(); fn(k)
        o=k.finish(n,coll,**kw); o.hide_render=True; o.hide_viewport=True; out.append(o)
    return out
