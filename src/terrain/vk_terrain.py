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
    """stair stone without UVs (object space; chunks sit unrotated at the map origin): dressed stone (the curb's
    texture) where TCol G = 1, which is every stair face; G = 0 would give the paving's cobbles. TCol R = AO.
    Vertical faces get a joint every half metre or so."""
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
    out=B.n("ShaderNodeOutputMaterial"); b=B.n("ShaderNodeBsdfPrincipled")
    tc=B.n("ShaderNodeTexCoord"); p=tc.outputs["Object"]
    at=B.n("ShaderNodeAttribute",attribute_name="TCol"); tcs=B.sep(at.outputs["Color"])
    hn=lambda img: next((img+x for x in ("_H","_R") if bpy.data.images.get(img+x)),None)
    # cobbles: top projection, as M_VKT_Paving
    pc=B.scale(p,0.25)
    cC=B.img("T_VK_Cobble_BC",pc).outputs[0]; cH=B.img(hn("T_VK_Cobble"),pc,data=True).outputs[0]
    # dressed stone: biplanar on the sides (image v = world z), top projection on the nosings
    sC,_,(vT,az)=B.side_sample("T_VK_StoneBlock_BC",p,0.8)
    _,sH,_=B.side_sample(hn("T_VK_StoneBlock"),p,0.8,data=True)
    wz=B.smoothstep(az,0.55,0.8)
    sC=B.mix(wz,sC,B.img("T_VK_StoneBlock_BC",vT).outputs[0]); sH=B.fmix(wz,sH,B.img(hn("T_VK_StoneBlock"),vT,data=True).outputs[0])
    # joints between the riser stones: 1D cells along x+y (runs along every riser, whichever way the stair faces)
    xyz=B.n("ShaderNodeSeparateXYZ"); B.link(p,xyz.inputs[0])
    vo=B.n("ShaderNodeTexVoronoi",voronoi_dimensions="1D",feature="DISTANCE_TO_EDGE")
    vo.inputs["Scale"].default_value=1.7; vo.inputs["Randomness"].default_value=0.8
    B.link(B.math("ADD",xyz.outputs[0],xyz.outputs[1]),vo.inputs["W"])
    joint=B.math("MULTIPLY",B.math("SUBTRACT",1.0,B.smoothstep(vo.outputs["Distance"],0.008,0.022)),B.math("SUBTRACT",1.0,wz))
    sC=B.mix(B.math("MULTIPLY",joint,0.75),sC,(0.16,0.14,0.12)); sH=B.fmix(joint,sH,0.0)
    stone=B.smoothstep(tcs[1],0.4,0.6)
    col=B.mix(stone,cC,sC); h=B.fmix(stone,cH,sH)
    aoc=B.n("ShaderNodeCombineColor"); B.link(tcs[0],aoc.inputs[0]); B.link(tcs[0],aoc.inputs[1]); B.link(tcs[0],aoc.inputs[2])
    col=B.mix(1.0,col,aoc.outputs[0],blend="MULTIPLY")
    B.link(col,b.inputs["Base Color"]); B.link(B.fmix(stone,0.82,0.78),b.inputs["Roughness"])
    bp=B.n("ShaderNodeBump"); B.link(B.fmix(stone,0.55,0.45),bp.inputs["Strength"]); bp.inputs["Distance"].default_value=0.04
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
        s.wear_marks=[]      # soft worn-ground patches (x, y, rx, ry, rot, strength) in map metres, painted by tk_ground_ctl
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
                        if _is_stair(G,c,l,r): yield (I,J,l,"Stair",ro,r,"A"); continue
                        yield (I,J,l,"Ramp",ro,r,"W" if ro!="Mid" and _is_paved_ramp(G,c,l,r) else "A"); continue
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
def tk_cache_noskirt(o):
    """the cached piece without its skirt (the faces below the toe, down to SKIRT_Z). A cliff layer standing on an
    identical layer has that layer's face right under its toe: the skirt is not needed there, and with the relief
    running through the seam it could poke out of the face below."""
    key=o.name+"|noskirt"
    if key in _CACHE: return _CACHE[key]
    c=tk_cache(o)
    keep=np.minimum.reduceat(c["co"][c["vi"],2],c["ls"])>SKIRT_Z+0.5
    lk=np.repeat(keep,c["lt"]); vi=c["vi"][lk]
    used=np.unique(vi); remap=np.full(len(c["co"]),-1,np.int64); remap[used]=np.arange(len(used))
    lt=c["lt"][keep]; ls=np.concatenate([[0],np.cumsum(lt)[:-1]]).astype(np.int64)
    d=dict(co=c["co"][used],vi=remap[vi],ls=ls,lt=lt,mi=c["mi"][keep],cn=c["cn"][lk],tc=c["tc"][lk])
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
    parts={"T":[],"W":[]}; prev=None
    for rec in records:
        (I,J,l,set_,case,r,var)=rec
        # a cliff layer right on top of an identical one (same tile, same case and rotation) drops its skirt
        stacked=(prev is not None and set_=="Cliff" and prev[3]=="Cliff" and case not in (EMPTY,FULL)
                 and (prev[0],prev[1],prev[2]+1,prev[4],prev[5])==(I,J,l,case,r))
        prev=rec
        if set_=="Cliff" and case==EMPTY: continue
        o=bpy.data.objects.get(piece_name(set_,case,var))
        if o is None: raise KeyError(piece_name(set_,case,var))
        parts["W" if set_=="Water" else "T"].append((tk_cache_noskirt(o) if stacked else tk_cache(o),I,J,l,r))
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
    me.polygons.foreach_set("use_smooth",np.ones(npo,bool))
    me.normals_split_custom_set(arr["cn"].astype(np.float32).tolist())
    at=me.color_attributes.get("TCol") or me.color_attributes.new("TCol","FLOAT_COLOR","CORNER")
    at.data.foreach_set("color",arr["tc"].astype(np.float32).ravel())
    me.materials.clear()                                     # (this resets every face's material index to 0,
    for m in mats: me.materials.append(m)                    #  so the indices are written afterwards)
    me.polygons.foreach_set("material_index",arr["mi"].astype(np.int32))
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
    col=B.mix(B.math("MULTIPLY",RIM,0.1),col,(0.66,0.76,0.38))
    # cliff (box projection in map space)
    clC,_,(vT,az)=B.side_sample("T_VK_Cliff_BC",p,1/6.0)
    _,clH,_=B.side_sample("T_VK_Cliff_H",p,1/6.0,data=True)
    # a second, offset sample at another scale blended in by world noise, plus slow brightness/hue drift,
    # so the rock pattern does not repeat visibly along long cliffs
    po=B.n("ShaderNodeVectorMath",operation="ADD"); B.link(p,po.inputs[0]); po.inputs[1].default_value=(17.3,5.9,11.1)
    clC2,_,_=B.side_sample("T_VK_Cliff_BC",po.outputs[0],1/9.3)
    _,clH2,_=B.side_sample("T_VK_Cliff_H",po.outputs[0],1/9.3,data=True)
    cn_=B.n("ShaderNodeTexNoise"); cn_.inputs["Scale"].default_value=0.11; cn_.inputs["Detail"].default_value=1.5; B.link(p,cn_.inputs["Vector"])
    cbl=B.smoothstep(cn_.outputs["Fac"],0.4,0.6)
    clC=B.mix(cbl,clC,clC2); clH=B.fmix(cbl,clH,clH2)
    # up-facing rock (ledges, eroded lips) gets the rock from above instead of the side projection's streaks
    wz=B.smoothstep(az,0.6,0.85)
    clC=B.mix(wz,clC,B.img("T_VK_Cliff_BC",vT).outputs[0]); clH=B.fmix(wz,clH,B.img("T_VK_Cliff_H",vT,data=True).outputs[0])
    tn_=B.n("ShaderNodeTexNoise"); tn_.inputs["Scale"].default_value=0.045; tn_.inputs["Detail"].default_value=1.0; B.link(p,tn_.inputs["Vector"])
    tv=B.smoothstep(tn_.outputs["Fac"],0.3,0.7)
    clC=B.mix(1.0,clC,B.mix(tv,(0.84,0.84,0.86),(1.08,1.03,0.95)),blend="MULTIPLY")
    rockW=B.math("MAXIMUM",RK,B.smoothstep(Nz,0.80,0.55))
    rockW=B.math("MAXIMUM",rockW,B.smoothstep(cA,0.45,0.65))
    # moss on up-facing rock
    mo=B.img("T_VK_Moss_BC",B.scale(p,1.0)); moH=B.img("T_VK_Moss_H",B.scale(p,1.0),data=True).outputs[0]
    mz=B.smoothstep(B.math("ADD",Nz,B.math("MULTIPLY",B.math("SUBTRACT",moH,0.5),0.75)),0.54,0.78)
    # ... in patches (about a third of it) and toned towards the rock, so ledges never read as a green line
    mp=B.n("ShaderNodeTexNoise"); mp.inputs["Scale"].default_value=0.55; mp.inputs["Detail"].default_value=3.0; B.link(p,mp.inputs["Vector"])
    mz=B.math("MULTIPLY",mz,B.smoothstep(mp.outputs["Fac"],0.52,0.6))
    ccol=B.mix(mz,clC,B.mix(0.3,mo.outputs[0],clC))
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

CTL_RES=5      # control-map texels per cell. Odd, so the fine texel centres include the cell centres: the cell data,
               # upsampled bilinearly, looks exactly as it did at one texel per cell
def _upsample(a,k):
    """bilinear samples of a per-cell array (values at the cell centres, clamped at the edges) at k x k texels per cell"""
    H,W=a.shape; a=np.asarray(a,np.float64)
    x=np.clip((np.arange(W*k)+0.5)/k-0.5,0,W-1); y=np.clip((np.arange(H*k)+0.5)/k-0.5,0,H-1)
    x0=np.floor(x).astype(int); y0=np.floor(y).astype(int); x1=np.minimum(x0+1,W-1); y1=np.minimum(y0+1,H-1)
    fx=(x-x0)[None,:]; fy=(y-y0)[:,None]
    return (a[y0][:,x0]*(1-fx)+a[y0][:,x1]*fx)*(1-fy)+(a[y1][:,x0]*(1-fx)+a[y1][:,x1]*fx)*fy

def _wear_field(G,k,seed=5):
    """G.wear_marks painted at k texels per cell: ellipses whose outline is broken up by world-space noise, full
    strength inside and a ragged fade outside, so trampled ground has no trace of the cell grid"""
    Hf,Wf=G.H*k,G.W*k; out=np.zeros((Hf,Wf)); cs=3.0/k
    X=(np.arange(Wf)+0.5)*cs; Y=(np.arange(Hf)+0.5)*cs
    for (x,y,rx,ry,rot,st) in G.wear_marks:
        r=1.4*max(rx,ry)+1.0
        i0=max(0,int((x-r)/cs)); i1=min(Wf,int((x+r)/cs)+1); j0=max(0,int((y-r)/cs)); j1=min(Hf,int((y+r)/cs)+1)
        if i0>=i1 or j0>=j1: continue
        xx,yy=np.meshgrid(X[i0:i1],Y[j0:j1]); c,s=math.cos(rot),math.sin(rot)
        u=((xx-x)*c+(yy-y)*s)/rx; v=(-(xx-x)*s+(yy-y)*c)/ry
        n=vnoise(xx/1.7,yy/1.7,np.zeros_like(xx),seed)+0.5*vnoise(xx/0.8,yy/0.8,np.full_like(xx,3.0),seed)
        w=st*np.clip((1.15-np.hypot(u,v)-0.28*n)/0.7,0,1)
        out[j0:j1,i0:i1]=np.maximum(out[j0:j1,i0:i1],w)
    return out

def tk_ground_ctl(G,name="T_VK_GroundCtl",paved=False,k=CTL_RES):
    """RGBA8, k texels per cell: R dirt(+wear) G cobble B sand(water forced) A rock.
    paved=True: cobble cells are covered by the separate paving mesh (tk_build_paving), so the terrain under them is
    painted as dirt (it shows through the patches of missing stones). Worn ground: G.wear (per cell) and the soft
    G.wear_marks, which only wear grass"""
    Wd,Hd=G.W*k,G.H*k
    arr=np.zeros((Hd,Wd,4),np.float32)
    gnd=G.ground
    cob=(gnd==2)
    grass=_upsample((gnd==0)&~G.water,k)
    arr[...,0]=np.maximum(_upsample(np.maximum(np.maximum(gnd==1,cob*paved),G.wear/255.0),k),_wear_field(G,k)*grass)
    arr[...,1]=_upsample(cob*(not paved),k); arr[...,2]=_upsample(np.maximum(gnd==3,G.water),k); arr[...,3]=_upsample(gnd==4,k)
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
def _ss(e0,e1,x):
    t=np.clip((x-e0)/(e1-e0),0.0,1.0); return t*t*(3-2*t)
def make_displace(G,amp=1.0,relief=0.36,relief_v=0.22,sag=0.12,talus=1.0):
    """world-space displacement of the assembled terrain (a function of position only, so the duplicated vertices of
    neighbouring tiles move together and no seam opens):
    - horizontal wobble of the contours (amp; zero on stiff cells and at the map border)
    - cliff relief (relief, relief_v): chunky 3D rock noise on the cliff faces. Zero on every flat top, at the lip and
      at the toe (it only acts between the tier heights), and switched off on ramps/stairs and next to water, whose
      surfaces also sit between tiers. Where a tier top is an intermediate ledge of a taller cliff (a cliff line
      above and below it at the same spot) the relief runs on through the seam, so stacked tiers read as one face.
    - lip sag: the lower edge of the turf lip on cliff tops droops in patches (not on intermediate ledges)
    - talus (talus): the bottom ~0.9 m of each cliff flares out into a scree apron whose size wanders along the
      run, so the turf climbs the foot to varying heights and the toe is no longer one level line. Not where the
      bottom is an intermediate ledge, on stiff cells (buildings, paving), ramps/stairs, water or the map border.
    apply() also bakes TCol: relief cavities, rock instead of turf on intermediate ledges and eroded lip patches,
    and lets the flared foot take turf (the shader then picks turf or rock by slope)."""
    stiff=G.stiff.astype(np.float64); XM,YM=3.0*G.W,3.0*G.H
    rampm=np.zeros(G.level.shape,np.float64)
    for (j,i) in zip(*np.nonzero(G.ramp)):
        rampm[j,i]=1.0; di,dj=((0,1),(1,0),(0,-1),(-1,0))[G.ramp[j,i]-1]
        rampm[min(max(j+dj,0),G.H-1),min(max(i+di,0),G.W-1)]=1.0      # the cell the ramp climbs to
    wetm=G.water.astype(np.float64)
    Lhi=int(G.level.max())+1
    ind={L:(G.level>=L).astype(np.float64) for L in range(1,Lhi+1)}
    def phi(L,x,y):
        """bilinear indicator of level >= L (L: int array); 0.5 on the tier-L cliff line"""
        out=np.where(L<=0,1.0,0.0)
        for Lv in np.unique(L):
            if 0<Lv<=Lhi:
                m=L==Lv; out[m]=_bilinear_cells(ind[int(Lv)],x[m],y[m])
        return out
    def on_line(f): return 1.0-_ss(0.12,0.25,np.abs(f-0.5))
    def fades(x,y):
        """1, falling to 0 on ramps/stairs, next to water and at the map border"""
        f=(1.0-np.clip(_bilinear_cells(rampm,x,y)/0.35,0,1))*(1.0-np.clip(_bilinear_cells(wetm,x,y)/0.3,0,1))
        e=np.clip(np.minimum(np.minimum(x,XM-x),np.minimum(y,YM-y))/3.0,0,1)
        return f*e*e*(3-2*e)
    def tiers(x,y,z):
        """d: depth below the tier top above the point (0 on flat tops); st / sb: how much that tier top / the tier
        bottom is an intermediate ledge here (the cliff lines of the tiers above and below both pass this spot)"""
        Lt=np.ceil(z/TIER-1e-6).astype(np.int64); d=Lt*TIER-z
        gt=on_line(phi(Lt,x,y))
        return d,gt*on_line(phi(Lt+1,x,y)),gt*on_line(phi(Lt-1,x,y))
    def relief_w(x,y,z):
        d,st,sb=tiers(x,y,z)
        top=_ss(0.12,0.4,d); bot=1.0-_ss(1.18,1.46,d)   # 0 at the lip and at the toe, 1 on the face between
        top=top+st*(1.0-top)*(d>0.005); bot=bot+sb*(1.0-bot)   # ... unless the seam is an intermediate ledge
        return top*bot*fades(x,y)
    def talus_off(x,y,z):
        """(offsets (N,3), amount (N,)): the foot of each tier pushed outward, most at the toe; the apron size h
        wanders along the run (2-3 m noise), from a plain rock foot to a wide turfed slope"""
        off=np.zeros((len(x),3)); amt=np.zeros(len(x))
        if talus<=0: return off,amt
        # the toe row lies 2 cm below the floor, so depth is measured 5 cm higher up; points exactly on a floor plane
        # (the flat ground tiles) never move, or their grid would fold
        d0=np.ceil(z/TIER-1e-6)*TIER-z
        d,_,_=tiers(x,y,z+0.05); t=np.clip((d-0.6)/0.87,0.0,1.0); m=(t>0)&(d0>0.004)
        if not m.any(): return off,amt
        xm,ym,zm,tm=x[m],y[m],z[m]+0.05,t[m]; Lt=np.ceil(zm/TIER-1e-6).astype(np.int64); e=0.05
        f=phi(Lt,xm,ym); gt=1.0-_ss(0.25,0.45,np.abs(f-0.5))    # only around this tier's own cliff line
        gx=(phi(Lt,xm+e,ym)-phi(Lt,xm-e,ym))/(2*e); gy=(phi(Lt,xm,ym+e)-phi(Lt,xm,ym-e))/(2*e); gl=np.hypot(gx,gy)
        # every fade below is read at the vertex's projection onto that line, so all rows of one column of the face get
        # the same strength (a flare weaker at the toe than one row up would tuck the toe under), and each changes over a
        # metre or more along the run (sharp changes shear neighbouring columns into folds where the face turns)
        glc=np.maximum(gl,1e-6); sd=np.clip((f-0.5)/glc,-0.6,0.6)          # distance to the line, at most 0.6 m
        px=xm-sd*gx/glc; py=ym-sd*gy/glc
        F=_ss(0.15,0.5,np.abs(phi(Lt-1,px,py)-0.5))              # not on intermediate ledges, nor near the next lip down
        sf=np.clip(_bilinear_cells(stiff,px,py)/0.5,0,1); F*=fades(px,py)*(1.0-sf*sf*(3-2*sf))
        h=_ss(0.2,0.8,0.5+0.9*vnoise(px/2.6,py/2.6,np.zeros_like(px),39))
        # concave corners: the outward pushes converge and would cross. Curvature of the cliff line = divergence of the
        # level map's unit gradient, over 1 m (about 0.65 in an inner corner, 0 on a straight run, negative on convex
        # ones): the talus fades out before the line bends inward
        def unit(qx,qy):
            ux=(phi(Lt,qx+e,qy)-phi(Lt,qx-e,qy))/(2*e); uy=(phi(Lt,qx,qy+e)-phi(Lt,qx,qy-e))/(2*e); ul=np.maximum(np.hypot(ux,uy),1e-6)
            return ux/ul,uy/ul
        k=1.0; kap=(unit(px+k,py)[0]-unit(px-k,py)[0]+unit(px,py+k)[1]-unit(px,py-k)[1])/(2*k)
        F*=1.0-_ss(0.05,0.25,kap)
        a=talus*F*(h*tm*tm+0.45*tm**3)*gt*_ss(0.004,0.012,d0[m])*(gl>1e-3)
        gl=np.maximum(gl,1e-9); off[m,0]=-gx/gl*a; off[m,1]=-gy/gl*a; amt[m]=a
        return off,amt
    def sag_z(x,y,z):
        d,st,_=tiers(x,y,z)
        b=_ss(0.1,0.16,d)*(1.0-_ss(0.3,0.6,d))          # the lip edge and root recess, not the crest line above
        out=np.zeros_like(x); m=b*(1.0-st)>1e-6
        if sag>0 and m.any():
            n=_ss(0.05,0.55,vnoise(x[m]/1.3,y[m]/1.3,np.zeros(m.sum()),37))
            out[m]=-sag*n*b[m]*(1.0-st[m])*fades(x[m],y[m])
        return out
    def terrace(n,k=2.5,a=0.6):                          # soft staircase: flattish facets with steeper steps
        return n+a*np.sin(2*np.pi*k*n)/(2*np.pi*k)
    def R(x,y,z):
        """relief offset (rx,ry,rz) before weighting; the envelope makes some stretches much rougher than others"""
        zz=np.zeros_like(x); env=0.55+0.45*vnoise(x/9.0,y/9.0,zz,36)
        f=lambda s1,s2: terrace(0.75*vnoise(x/1.35,y/1.35,z/0.55,s1)+0.25*vnoise(x/0.55,y/0.55,z/0.35,s2))
        return relief*env*f(31,32),relief*env*f(33,34),relief_v*vnoise(x/2.2,y/2.2,zz,35)
    def Rw(p):
        """weighted relief offsets for points p (N,3)"""
        out=np.zeros((len(p),3))
        if relief<=0 and relief_v<=0: return out
        x,y,z=p[:,0],p[:,1],p[:,2]
        w=relief_w(x,y,z); m=w>1e-6
        if m.any():
            rx,ry,rz=R(x[m],y[m],z[m]); out[m,0]=rx*w[m]; out[m,1]=ry*w[m]; out[m,2]=rz*w[m]
        return out
    def D0(p):
        x,y,z=p[:,0],p[:,1],p[:,2]
        s=_bilinear_cells(stiff,x,y); t=np.clip(s/0.5,0,1); A=amp*(1-t*t*(3-2*t))
        e=np.clip(np.minimum(np.minimum(x,XM-x),np.minimum(y,YM-y))/3.0,0,1); A=A*e*e*(3-2*e)
        dx=0.28*vnoise(x/6,y/6,z/4,11)+0.08*vnoise(x/1.6,y/1.6,z/1.6,13)
        dy=0.28*vnoise(x/6,y/6,z/4,12)+0.08*vnoise(x/1.6,y/1.6,z/1.6,14)
        return np.stack([A*dx,A*dy,sag_z(x,y,z)],1)+Rw(p)
    def D(p):
        """the displacement at any point (props): the talus direction here is the level map's, an approximation"""
        return D0(p)+talus_off(p[:,0],p[:,1],p[:,2])[0]
    def apply(arr):
        co=arr["co"]; e=0.005                   # small step: the talus must not see the floor plane 2 cm above the toe
        J=np.zeros((len(co),3,3)); ga=np.zeros((len(co),3))
        for a in range(3):
            dp=np.zeros(3); dp[a]=e
            J[:,:,a]=(D0(co+dp)-D0(co-dp))/(2*e)
            ga[:,a]=(talus_off(*(co+dp).T)[1]-talus_off(*(co-dp).T)[1])/(2*e)
        # the talus pushes each vertex along its own tile normal (horizontal part): the tiles' normals agree across
        # seams and follow the real contour, where the level map's gradient bends wrongly at junctions
        nv=np.zeros((len(co),2)); np.add.at(nv,arr["vi"],arr["cn"][:,:2]); nl_=np.linalg.norm(nv,axis=1)
        dv=np.where(nl_[:,None]>1e-6,nv/np.maximum(nl_,1e-9)[:,None],0.0)
        dv=np.concatenate([dv,np.zeros((len(co),1))],1)
        ta=talus_off(co[:,0],co[:,1],co[:,2])[1]*(nl_>1e-6)
        J+=np.einsum("ni,nj->nij",dv,ga)
        J+=np.eye(3)[None]
        rel=Rw(co)
        co2=co+D0(co)+dv*ta[:,None]
        # loop normals: n' = normalize(J^-T n)
        JiT=np.linalg.inv(J).transpose(0,2,1)
        cn0=arr["cn"]
        n=np.einsum("lij,lj->li",JiT[arr["vi"]],cn0)
        n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-12
        tc=arr["tc"].copy()
        # baked cavity: recesses of the relief darker, bulges a touch lighter (TCol R = AO)
        if relief>0:
            s=np.einsum("lj,lj->l",rel[arr["vi"],:2],cn0[:,:2])/relief
            tc[:,0]=np.clip(tc[:,0]*(1.0+0.3*np.clip(s,-1.0,0.6)),0.0,1.0)
        # lips: rock instead of turf (G) and no rim light (B) on intermediate ledges and in eroded patches along the tops
        x,y,z=co[:,0],co[:,1],co[:,2]
        d,st,_=tiers(x,y,z)
        er=_ss(0.25,0.55,vnoise(x/1.7,y/1.7,np.zeros_like(x),38))
        r=np.maximum(st,er)*fades(x,y)
        rim=((d>0.005)&(d<0.3))*r; rock=((d>0.03)&(d<0.3))*r
        tc[:,1]=np.maximum(tc[:,1],rock[arr["vi"]]); tc[:,2]*=1.0-rim[arr["vi"]]
        # the flared foot is no longer rock by definition: the terrain shader decides by slope (turf where it is gentle)
        tc[:,1]*=1.0-_ss(0.08,0.35,ta)[arr["vi"]]
        arr["tc"]=tc
        arr["co"]=co2; arr["cn"]=n
        arr["detJ"]=float(np.min(J[:,0,0]*J[:,1,1]-J[:,0,1]*J[:,1,0]))
    apply.D=D; apply.relief_w=relief_w; apply.tiers=tiers; apply.talus=talus_off
    return apply

def lip_pos(D,x,y,zt):
    """where a prop standing on a cliff lip at border point (x, y), tier top zt, goes after displacement D"""
    if D is None: return x,y,zt
    d=D(np.array([[x,y,zt-0.12]],float))[0]; return x+d[0],y+d[1],zt+d[2]

# ---------------------------------------------------------------- ramps (canonical Edge, N high; ramp on E / W / both crossing sides)
RAMP_X=0.5            # half-ramp spans x in [RAMP_X, 1.5]  (2.0 m ramp centred on the side)
RAMP_N=(0.0,-0.5/math.hypot(0.5,1.0),1.0/math.hypot(0.5,1.0))
RAMP_T=(1.0,0.0,0.0,0.0)
CHEEK_T=(0.88,1.0,0.0,0.0)     # ramp/stair cheeks: rock, light AO (they often face away from the sun)
def _ramp_z(y): return (y-1.5)*0.5
def _ramp_n(y): return TUP if (abs(y-1.5)<1e-6 or abs(y+1.5)<1e-6) else RAMP_N
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
def ramp_blend_shoulder(tb,xr,y_cut,k_run=1.3):
    """Cliff-to-ramp transition inside the half-ramp tile.
    1) Everything of the cliff above the ramp line, for x in [-1.5, xr], is lowered towards the ramp line with a
       smoothstep over the band: untouched at the tile's W side (seams stay bit-identical), lying exactly on the
       ramp surface at x=xr, so there is no vertical end cap and no slot where the ramp cuts into the terrace.
    2) The ramp's side below the ramp line becomes a sloped earth bank (run k_run per metre of height) instead of
       a vertical cheek."""
    x0=-1.5; moved={}
    for vi,(x,y,z) in enumerate(tb.v):
        if x>xr+1e-6 or x<=x0+1e-6: continue
        zr=_ramp_z(max(-1.5,min(1.5,y)))
        if z<=zr+1e-6: continue
        t=(x-x0)/(xr-x0); sm=t*t*(3-2*t)
        tb.v[vi]=(x,y,zr+(z-zr)*(1.0-sm)); moved[vi]=sm
    # smooth normals for the reshaped faces (their stored tile normals no longer fit)
    aff=[fi for fi,f in enumerate(tb.f) if any(v in moved for v in f)]
    acc={}
    for fi in aff:
        P=[Vector(tb.v[v]) for v in tb.f[fi]]; n=Vector((0.0,0.0,0.0))
        for a in range(len(P)): n+=P[a].cross(P[(a+1)%len(P)])
        for v in tb.f[fi]: acc[v]=acc.get(v,Vector((0.0,0.0,0.0)))+n
    for fi in aff:
        tb.ln[fi]=[tuple((acc[v].normalized() if acc[v].length>1e-9 else Vector(TUP))) for v in tb.f[fi]]
        # the lowered cliff turns into a turf slope: fade the rock mask and the rim as it bends down, so the
        # strata texture is never shown squashed
        lc=[]
        for v,c in zip(tb.f[fi],tb.lc[fi]):
            f_=1.0-moved.get(v,0.0)**0.6
            lc.append((max(c[0],0.8)*(1-f_)+c[0]*f_ if v in moved else c[0],c[1]*f_,c[2]*f_,c[3]))
        tb.lc[fi]=lc
    # sloped bank along the ramp side, from the ramp foot to just inside the cliff
    ys=[-1.5+0.25*q for q in range(int((y_cut+0.35+1.5)/0.25)+1)]
    top=[(xr,y,_ramp_z(y)) for y in ys]; bot=[(xr-(_ramp_z(y)+1.5)*k_run,y,-1.5-0.02) for y in ys]
    bank=(0.85,0.0,0.0,0.0)
    for a in range(len(ys)-1):
        q=[tb.vert(bot[a],share=False),tb.vert(bot[a+1],share=False),tb.vert(top[a+1],share=False),tb.vert(top[a],share=False)]
        P=[Vector(tb.v[v]) for v in q]; n=(P[1]-P[0]).cross(P[3]-P[0])
        if n.x>0 or n.z<0: q=q[::-1]; n=-n                  # faces up and away from the ramp (-x)
        tb.face(q,[tuple(n.normalized())]*4,[bank]*4)
    e=len(ys)-1                                                # end cap (inside the cliff mass)
    q=[tb.vert(bot[e],share=False),tb.vert(top[e],share=False),tb.vert((xr,ys[e],-1.5-0.02),share=False)]
    tb.face(q,[(0.0,1.0,0.0)]*3,[bank]*3)
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
    ramp_blend_shoulder(tb,xr,cp[0])
    return tb
def gen_ramp_half_e_walled():
    """half ramp for a paved road: the cliff is not blended into the ramp; a built wall (_stair_wall: sloped coping
    along the part in front of the cliff, a pier where the cliff meets the ramp, a kerb along the upper part) stands
    between them, as beside the built stairs. The ramp surface is the same as gen_ramp_half_e's."""
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
    _ramp_surface(tb,xr,1.5,int(round((1.5-xr)/0.5))+1)
    _stair_wall(tb,xr-STAIR_WALL,xr)
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
    w=gen_ramp_half_e_walled()
    tk_finish(w,"SM_VKT_Ramp_HalfE_W",coll,dict(set="Ramp",case="HalfE",var="W",mask=12))
    tk_finish(mirror_tb(w),"SM_VKT_Ramp_HalfW_W",coll,dict(set="Ramp",case="HalfW",var="W",mask=12))

DIRV={1:(0,1),2:(1,0),3:(0,-1),4:(-1,0)}
def _is_stair(G,c,l,r):
    for cs in (1,3):
        ws=(cs+r)%4; a=c[ws]; b=c[(ws+1)%4]
        lowc=a if a[0]<b[0] else b
        if lowc[0]==l-1 and G.ramp[lowc[3],lowc[2]] and G.stair[lowc[3],lowc[2]]: return True
    return False
def _is_paved_ramp(G,c,l,r):
    """the ramp crossing this layer carries a paved road (its low cell is cobbled): built walls instead of earth banks"""
    for cs in (1,3):
        ws=(cs+r)%4; a=c[ws]; b=c[(ws+1)%4]
        lowc=a if a[0]<b[0] else b
        if lowc[0]==l-1 and G.ramp[lowc[3],lowc[2]] and G.ground[lowc[3],lowc[2]]==2: return True
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

def tk_ramp_dress(G,coll,origin=MAP_ORIGIN,seed=7):
    """a few plants and stones where each ramp or stair run meets the cliffs (breaks up the joint line); beside a
    stair they move out past its flanking wall"""
    rng=random.Random(seed); out=[]
    picks=(("SM_VK_Rock_Small_A",(-0.95,-1.05),0.9),("SM_VK_Plant_Fern",(-0.55,-0.55),0.8),
           ("SM_VK_Plant_TallGrass",(-1.25,-0.25),1.0),("SM_VK_Rock_Small_B",(0.05,-1.35),0.6))
    for (j,i) in zip(*np.nonzero(G.ramp)):
        d=int(G.ramp[j,i]); fx,fy=((0,1),(1,0),(0,-1),(-1,0))[d-1]; wall=STAIR_WALL if G.stair[j,i] else 0.0
        if G.ground[j,i]==2: continue                                            # paved steps and road ramps stay clean
        for sx,sy in ((fy,-fx),(-fy,fx)):
            ni,nj=i+sx,j+sy
            if 0<=ni<G.W and 0<=nj<G.H and G.ramp[nj,ni]==d: continue
            cx=3*i+1.5+sx*1.0+fx*1.5; cy=3*j+1.5+sy*1.0+fy*1.5; z=float(G.level[j,i])*TIER
            for (nm,(lx,ly),sc) in picks:
                src=bpy.data.objects.get(nm)
                if src is None or rng.random()<0.2: continue
                lx=lx-wall
                if wall and lx>-wall-0.15: continue
                # local x points to the ramp (-side vector), local y uphill
                wx=cx-sx*lx+fx*ly; wy=cy-sy*lx+fy*ly
                o=bpy.data.objects.new(nm+"_inst",src.data); coll.objects.link(o)
                o.location=(origin[0]+wx,origin[1]+wy,origin[2]+z-0.03)
                o.rotation_euler=(0.0,0.0,rng.uniform(0,6.283)); s_=sc*rng.uniform(0.85,1.15); o.scale=(s_,s_,s_)
                out.append(o)
    return out

def tk_cliff_dress(G,place,D=None,seed=5,free=None,density=1.0):
    """Natural dressing along straight cliff runs (level-change borders without water or ramps): boulders half sunk
    into the face, rubble and plants at the toe.
    place(name, x, y, z, rot_deg, scale) puts one piece (map-local coordinates); D is the terrain's displacement
    field, so pieces follow the displaced face; free(i, j) -> False skips borders next to that cell."""
    rng=random.Random(seed); n=0
    def disp(x,y,z):
        if D is None: return x,y
        d=D(np.array([[x,y,z]],float))[0]; return x+d[0],y+d[1]
    face=("SM_VK_Rock_Boulder_A","SM_VK_Rock_Boulder_B","SM_VK_Rock_Boulder_Flat")
    rubble=("SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Pebbles","SM_VK_Rock_Small_A","SM_VK_Rock_Cluster")
    plants=("SM_VK_Plant_Fern","SM_VK_Plant_TallGrass","SM_VK_Bush_Round","SM_VK_Plant_Fern","SM_VK_Plant_TallGrass")
    lip=(("SM_VK_Plant_Fern",(0.6,0.85)),("SM_VK_Bush_Round",(0.35,0.5)),("SM_VK_Rock_Small_A",(0.6,0.95)),
         ("SM_VK_Plant_TallGrass",(0.75,1.0)),("SM_VK_Rock_Small_B",(0.6,0.9)))
    lipgrass="SM_VK_LipGrass" if bpy.data.objects.get("SM_VK_LipGrass") else "SM_VKT_LipGrass"
    for j in range(G.H):
        for i in range(G.W):
            for (di,dj) in ((1,0),(0,1)):
                ii,jj=i+di,j+dj
                if ii>=G.W or jj>=G.H: continue
                la,lb=int(G.level[j,i]),int(G.level[jj,ii])
                if la==lb or G.water[j,i] or G.water[jj,ii] or G.ramp[j,i] or G.ramp[jj,ii]: continue
                hi_i,hi_j,lo_i,lo_j=(i,j,ii,jj) if la>lb else (ii,jj,i,j)
                if free is not None and not (free(hi_i,hi_j) and free(lo_i,lo_j)): continue
                ox,oy=(lo_i-hi_i),(lo_j-hi_j); tx,ty=abs(oy),abs(ox)
                cx=1.5*(hi_i+lo_i)+1.5; cy=1.5*(hi_j+lo_j)+1.5
                def straight(sgn):
                    a_=G.cell(hi_i+sgn*tx,hi_j+sgn*ty); b_=G.cell(lo_i+sgn*tx,lo_j+sgn*ty)
                    return G.level[a_[1],a_[0]]==G.level[hi_j,hi_i] and G.level[b_[1],b_[0]]==G.level[lo_j,lo_i] and not G.water[b_[1],b_[0]]
                sl,sr=straight(-1),straight(1)
                def t_along(lim=1.1):
                    return rng.uniform(-lim if sl else -0.2,lim if sr else 0.2)
                zl=G.level[lo_j,lo_i]*TIER; H=(G.level[hi_j,hi_i]-G.level[lo_j,lo_i])*TIER
                if rng.random()<0.35*density:                              # boulder sunk into the face
                    t=t_along(); off=rng.uniform(-0.05,0.2); zb=zl+H*rng.uniform(0.12,0.4)
                    x,y=disp(cx+tx*t+ox*off,cy+ty*t+oy*off,zb+0.3)
                    place(rng.choice(face),x,y,zb,rng.uniform(0,360),rng.uniform(0.42,0.72)*(1.0 if H<=TIER else 1.35)); n+=1
                if rng.random()<0.3*density:                               # plants and stones on the lip, over the edge
                    zt=G.level[hi_j,hi_i]*TIER
                    for _ in range(rng.randint(1,2)):
                        t=t_along(); off=rng.uniform(-0.25,0.05); x,y,z=lip_pos(D,cx+tx*t+ox*off,cy+ty*t+oy*off,zt)
                        nm,(s0,s1)=lip[rng.randrange(len(lip))]
                        place(nm,x,y,z-0.03,rng.uniform(0,360),rng.uniform(s0,s1)); n+=1
                if G.level[hi_j,hi_i]-G.level[lo_j,lo_i]>=2:                # grass tufts on the middle ledges of stacked cliffs
                    rot=math.degrees(math.atan2(oy,ox))+90
                    for Lm in range(int(G.level[lo_j,lo_i])+1,int(G.level[hi_j,hi_i])):
                        for t in (-1.1,-0.4,0.3,1.0):
                            if (t<-0.2 and not sl) or (t>0.2 and not sr) or rng.random()<0.45: continue
                            tt=t+rng.uniform(-0.15,0.15); x,y,z=lip_pos(D,cx+tx*tt,cy+ty*tt,Lm*TIER)
                            place(lipgrass,x,y,z,rot+rng.uniform(-8,8),rng.uniform(0.8,1.2)); n+=1
                if rng.random()<0.6*density:                               # rubble at the toe (just above the floor, D
                    for _ in range(rng.randint(2,4)):                      # includes the talus push: the foot of the apron)
                        t=t_along(); off=rng.uniform(0.35,0.95); x,y=disp(cx+tx*t+ox*off,cy+ty*t+oy*off,zl+0.01)
                        nm=rng.choice(rubble)
                        place(nm,x,y,zl-0.05,rng.uniform(0,360),rng.uniform(0.35,0.55) if nm.endswith("Cluster") else rng.uniform(0.6,1.2)); n+=1
                if rng.random()<0.45*density:                              # plants at the toe
                    t=t_along(); off=rng.uniform(0.5,1.0); x,y=disp(cx+tx*t+ox*off,cy+ty*t+oy*off,zl+0.01)
                    nm=rng.choice(plants)
                    place(nm,x,y,zl,rng.uniform(0,360),rng.uniform(0.45,0.65) if nm.endswith("Round") else rng.uniform(0.7,1.05)); n+=1
    return n

def paving_materials():
    """M_VKT_Paving: the terrain's cobble texture (same object-space mapping as the terrain) + height bump.
    M_VKT_Curb: dressed stone (StoneBlock) box-projected in object space."""
    out=[]
    for name,img,sc,rough,bstr in (("M_VKT_Paving","T_VK_Cobble",0.25,0.82,0.55),("M_VKT_Curb","T_VK_StoneBlock",0.8,0.78,0.45)):
        m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); B=_NB(nt)
        o=B.n("ShaderNodeOutputMaterial"); bs=B.n("ShaderNodeBsdfPrincipled")
        tc=B.n("ShaderNodeTexCoord"); p=B.scale(tc.outputs["Object"],sc)
        box=(name=="M_VKT_Curb")
        c=B.img(img+"_BC",p,box=box)
        hname=next((img+x for x in ("_H","_R") if bpy.data.images.get(img+x)),None)
        h=B.img(hname,p,data=True,box=box) if hname else c
        vc=B.n("ShaderNodeVertexColor",layer_name="Col")
        col=B.mix(1.0,c.outputs[0],vc.outputs[0],blend="MULTIPLY")
        B.link(col,bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value=rough; bs.inputs["Specular IOR Level"].default_value=0.25
        bp=B.n("ShaderNodeBump"); B.link(h.outputs[0],bp.inputs["Height"]); bp.inputs["Strength"].default_value=bstr
        bp.inputs["Distance"].default_value=0.04; B.link(bp.outputs[0],bs.inputs["Normal"]); B.link(bs.outputs[0],o.inputs[0])
        out.append(m)
    return out

def tk_build_paving(G,coll,origin=MAP_ORIGIN,name="VK_Paving",lift=0.06,step=0.25,seed=3,hole_t=0.5,cliff_inset=0.35,exclude=()):
    """Cobbled cells (ground==2) as a separate mesh: stones `lift` m above the terrain, a curb of dressed stones
    where the cobbles meet grass (not towards dirt roads or ramps), and patches of missing stones that show the
    dirt painted under the paving. Hole edges are irregular and get a small side face (the paving's thickness).
    A ramp climbs half a cell into the cell above it. When both the ramp cell and the cell above are paved (a paved
    road on a ramp) the paving follows the ramp's slope (the upper half of the ramp cell and the lower half of the cell
    above, over the ramp's width); otherwise that part is left unpaved, and always for stairs (with their flanking
    walls). Curbs run along the cut walls beside a ramp instead of across it.
    exclude: map-local rectangles (x0, x1, y0, y1) left unpaved (under bridges, gate floors)."""
    from mathutils import noise as mnoise
    rng=random.Random(seed)
    cob=(G.ground==2)&(~G.water)
    n=int(round(3.0/step))
    # cut-outs: upper cell -> [(side, a0, a1)]; side 0..3 = W,E,S,N faces the ramp cell, a0..a1 along that side (m)
    cut={}; walls={}; slope={}
    for (rj,ri) in zip(*np.nonzero(G.ramp)):
        d=int(G.ramp[rj,ri]); fx,fy=((0,1),(1,0),(0,-1),(-1,0))[d-1]; hi_,hj_=ri+fx,rj+fy
        if not (0<=hi_<G.W and 0<=hj_<G.H) or not cob[hj_,hi_]: continue
        tx,ty=abs(fy),abs(fx)
        run=lambda s: 0<=ri+s*tx<G.W and 0<=rj+s*ty<G.H and G.ramp[rj+s*ty,ri+s*tx]==d
        edge=RAMP_X-(STAIR_WALL if G.stair[rj,ri] else 0.0)      # a flight's flanking walls stay unpaved too
        a0=0.0 if run(-1) else edge; a1=3.0 if run(1) else 3.0-edge
        side={(0,1):2,(0,-1):3,(1,0):0,(-1,0):1}[(fx,fy)]
        walls.setdefault((hi_,hj_),[]).append((side,a0,a1))
        if cob[rj,ri] and not G.stair[rj,ri]:                       # paved road on the ramp: pave the slope
            L=int(G.level[rj,ri])
            slope.setdefault((ri,rj),[]).append(("ramp",L,fx,fy,a0,a1))
            slope.setdefault((hi_,hj_),[]).append(("high",L,fx,fy,a0,a1))
        else: cut.setdefault((hi_,hj_),[]).append((side,a0,a1))
    def in_cut(i,j,lx,ly):
        for (sd,a0,a1) in cut.get((i,j),()):
            a=ly if sd in (0,1) else lx; dep=(lx,3-lx,ly,3-ly)[sd]
            if a0<=a<=a1 and dep<1.5: return True
        return False
    def slope_z(i,j,lx,ly):
        """(z, inside): the paving height on a paved ramp at cell-local (lx, ly), None where the spot is flat; inside
        is False in the ramp cell's upper half beside the ramp (the earth shoulder: left unpaved)"""
        for (kind,L,fx,fy,a0,a1) in slope.get((i,j),()):
            s_=ly if fy==1 else (3-ly if fy==-1 else (lx if fx==1 else 3-lx))        # along the ramp, from the cell's low edge
            a=lx if fx==0 else ly
            inw=a0-1e-6<=a<=a1+1e-6
            if kind=="ramp" and s_>1.5-1e-6: return (L*TIER+(s_-1.5)*0.5, True) if inw else (None,False)
            if kind=="high" and s_<1.5+1e-6: return (L*TIER+0.75+s_*0.5, True) if inw else (None,False)
        return None, True
    def excluded(x,y): return any(x0<=x<=x1 and y0<=y<=y1 for (x0,x1,y0,y1) in exclude)
    bm=bmesh.new(); uvl=bm.loops.layers.uv.new("UVMap"); cl=bm.loops.layers.color.new("Col")
    V={}; holes=set()
    def vert(ia,ib,z):                                  # welded by position: flat and sloped parts share their seams
        k=(ia,ib,round(z,3))
        if k not in V: V[k]=bm.verts.new((ia*step,ib*step,z+lift))
        return V[k]
    def nb(i,j):
        return (G.level[j,i],bool(cob[j,i]),int(G.ground[j,i]),int(G.ramp[j,i])) if (0<=i<G.W and 0<=j<G.H) else None
    curb_sides=[]
    for (j,i) in zip(*np.nonzero(cob)):
        lv=int(G.level[j,i]); ins=[0.0,0.0,0.0,0.0]; curb=[False]*4          # W,E,S,N
        for sd,(di,dj) in enumerate(((-1,0),(1,0),(0,-1),(0,1))):
            q=nb(i+di,j+dj)
            if q is None: continue
            l2,c2,g2,r2=q
            if l2<lv: ins[sd]=cliff_inset; curb[sd]=not G.ramp[j,i]
            elif not c2 and l2==lv and g2!=1 and not r2 and not G.ramp[j,i]: curb[sd]=True
            elif not c2 and l2==lv and g2!=1 and not r2 and G.ramp[j,i] and (di!=0)==(G.ramp[j,i] in (1,3)):
                curb[sd]=True                                   # beside a paved ramp's flat half (limited below)
        curb_sides.append((i,j,lv,ins,curb))
        for a in range(n):
            for b in range(n):
                x0,y0=3*i+a*step,3*j+b*step; cx,cy=x0+step/2,y0+step/2; lx,ly=cx-3*i,cy-3*j
                zc,inside=slope_z(i,j,lx,ly)
                if not inside or excluded(cx,cy) or in_cut(i,j,lx,ly): continue
                if zc is None and (lx<ins[0] or lx>3-ins[1] or ly<ins[2] or ly>3-ins[3]): continue
                near_curb=((curb[0] and lx<0.6) or (curb[1] and lx>2.4) or (curb[2] and ly<0.6) or (curb[3] and ly>2.4))
                hv=mnoise.noise(Vector((cx*0.42,cy*0.42,7.3)))+0.45*mnoise.noise(Vector((cx*1.4,cy*1.4,2.1)))
                ia,ib=int(round(x0/step)),int(round(y0/step))
                zs=[]
                for (da,db) in ((0,0),(1,0),(1,1),(0,1)):
                    z_=slope_z(i,j,lx-step/2+da*step,ly-step/2+db*step)[0] if zc is not None else None
                    zs.append(lv*TIER if z_ is None else z_)
                if hv>hole_t and not near_curb:
                    holes.add(tuple((ia+da,ib+db,round(z_,3)) for (da,db),z_ in zip(((0,0),(1,0),(1,1),(0,1)),zs))); continue
                f=bm.faces.new((vert(ia,ib,zs[0]),vert(ia+1,ib,zs[1]),vert(ia+1,ib+1,zs[2]),vert(ia,ib+1,zs[3]))); f.material_index=0
    # irregular hole outlines: jitter the vertices on hole edges (only in xy)
    hv_=set()
    for q in holes:
        for k in q:
            if k in V: hv_.add(k)
    for k in hv_:
        v=V[k]; v.co.x+=rng.uniform(-0.07,0.07); v.co.y+=rng.uniform(-0.07,0.07)
    # side faces on every open edge (holes, paving ends)
    for e in [e for e in bm.edges if len(e.link_faces)==1]:
        f=e.link_faces[0]; v1,v2=e.verts
        lp=[l.vert for l in f.loops]; k_=lp.index(v1)
        if lp[(k_+1)%len(lp)]!=v2: v1,v2=v2,v1
        z=v1.co.z-lift-0.03
        a_=bm.verts.new((v1.co.x,v1.co.y,z)); b_=bm.verts.new((v2.co.x,v2.co.y,z))
        sf=bm.faces.new((v2,v1,a_,b_)); sf.material_index=0
    # curb runs (cell-local (depth from the side, along the side) -> map coordinates)
    def cpt(i,j,sd,dep,a):
        return ((3*i+dep,3*j+a),(3*i+3-dep,3*j+a),(3*i+a,3*j+dep),(3*i+a,3*j+3-dep))[sd]
    runs=[]
    for (i,j,lv,ins,curb) in curb_sides:
        for sd in range(4):
            if not curb[sd]: continue
            off=ins[sd]+0.11; spans=[(0.0,3.0)]
            if G.ramp[j,i]:                                     # ramp cell: only its flat (low) half, up to the wall
                d_=int(G.ramp[j,i]); spans=[(0.0,1.45)] if d_ in (1,2) else [(1.55,3.0)]
            for (s2,a0,a1) in walls.get((i,j),()):
                if s2!=sd: continue
                spans=[q for (b0,b1) in spans for q in ((b0,min(b1,a0-0.21)),(max(b0,a1+0.21),b1)) if q[1]-q[0]>0.05]
                if (s2,a0,a1) not in cut.get((i,j),()): continue    # a walled (paved) ramp: its wall is the edge
                for ac in ((a0-0.11,) if a0>0.0 else ())+((a1+0.11,) if a1<3.0 else ()):
                    runs.append((cpt(i,j,sd,off-0.1,ac),cpt(i,j,sd,1.5,ac),lv))          # along the cut wall
            runs+=[(cpt(i,j,sd,off,b0),cpt(i,j,sd,off,b1),lv) for (b0,b1) in spans]
    # curb stones
    for (p0,p1,lv) in runs:
        zc=lv*TIER
        L=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); t=0.0; tx,ty=(p1[0]-p0[0])/L,(p1[1]-p0[1])/L
        while t<L-0.05:
            l_=min(rng.uniform(0.42,0.72),L-t)
            cxs=p0[0]+tx*(t+l_/2); cys=p0[1]+ty*(t+l_/2)
            h=0.17+rng.uniform(-0.015,0.015)
            vs=bmesh.ops.create_cube(bm,size=1.0)["verts"]
            ang=math.atan2(ty,tx)+math.radians(rng.uniform(-2.5,2.5))
            M=(Matrix.Translation((cxs,cys,zc-0.05+h/2))@Matrix.Rotation(ang,4,"Z")@Matrix.Diagonal((l_-0.03,0.2,h,1.0)))
            bmesh.ops.transform(bm,matrix=M,verts=vs)
            for f in {f for v in vs for f in v.link_faces}: f.material_index=1
            t+=l_
    # colours (darker hole sides) and box uvs
    bm.normal_update()
    for f in bm.faces:
        side=abs(f.normal.z)<0.5
        for l in f.loops:
            g=0.72 if (side and f.material_index==0) else 1.0
            l[cl]=(g,g,g,1.0)
            n_=f.normal; co=l.vert.co
            if abs(n_.z)>0.7: l[uvl].uv=(co.x,co.y)
            elif abs(n_.x)>abs(n_.y): l[uvl].uv=(co.y,co.z)
            else: l[uvl].uv=(co.x,co.z)
    me=bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    me.clear_geometry(); me.materials.clear()                # clear the slots first: that resets face material indices
    for m in paving_materials(): me.materials.append(m)
    bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.get(name)
    if ob is None: ob=bpy.data.objects.new(name,me)
    for c in list(ob.users_collection): c.objects.unlink(ob)
    coll.objects.link(ob); ob.location=origin
    return ob

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

# ---------------------------------------------------------------- stairs (same footprint as ramps, 6 risers x 0.25)
# dressed stone throughout: treads, risers and the flanking walls (material M_VKT_Stair, TCol G = 1 = stone)
STAIR_OUT=[(-1.5,-1.5),(-1.25,-1.5),(-1.25,-1.25),(-0.75,-1.25),(-0.75,-1.0),(-0.25,-1.0),(-0.25,-0.75),
           (0.25,-0.75),(0.25,-0.5),(0.75,-0.5),(0.75,-0.25),(1.25,-0.25),(1.25,0.0),(1.5,0.0)]
STAIR_STONE=(1.0,1.0,0.0,0.0); STAIR_CORNER_AO=0.6; STAIR_RISER_AO=0.84   # all one stone: shading keeps the steps legible
def _stair_z(y):
    z=-1.5
    for k in range(0,len(STAIR_OUT)-1):
        (y0,z0),(y1,z1)=STAIR_OUT[k],STAIR_OUT[k+1]
        if abs(z0-z1)<1e-9 and y0-1e-9<=y<=y1+1e-9: return z0
    return z
def _stairs(tb,xa,xb):
    ncol=int(round((xb-xa)/0.5))
    for c in range(ncol):
        _stairs_strip(tb,xa+0.5*c,xa+0.5*(c+1))
def _stairs_strip(tb,x0,x1):
    """one 0.5 m wide strip of the flight, all dressed stone. Treads are shaded darker towards the corner under the
    next riser (not the top landing, which meets the floor), so each step reads. Risers face -y."""
    last=len(STAIR_OUT)-2
    def quad(pts,n,cols):
        q=[tb.vert(p) for p in pts]; V=[Vector(tb.v[i]) for i in q]
        if (V[1]-V[0]).cross(V[3]-V[0]).dot(Vector(n))<0: q=q[::-1]; cols=cols[::-1]
        tb.face(q,[n]*4,cols,mi=1)
    ao=lambda t,a: (a,t[1],t[2],t[3])
    for k in range(last+1):
        (y0,z0),(y1,z1)=STAIR_OUT[k],STAIR_OUT[k+1]
        if abs(z0-z1)<1e-9:   # tread
            back=STAIR_STONE if k==last else ao(STAIR_STONE,STAIR_CORNER_AO)
            quad([(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1)],(0.0,0.0,1.0),[STAIR_STONE,STAIR_STONE,back,back])
        else:                 # riser
            low=ao(STAIR_STONE,STAIR_CORNER_AO); up=ao(STAIR_STONE,STAIR_RISER_AO)
            quad([(x0,y0,z0),(x0,y1,z1),(x1,y1,z1),(x1,y0,z0)],(0.0,-1.0,0.0),[low,up,up,low])
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
    _stair_wall(tb,xr-STAIR_WALL,xr)
    return tb
STAIR_WALL=0.5   # flanking wall on the cliff side of a flight: wall + 2 m flight + wall fill one 3 m cell
def _stone_block(tb,x0,x1,y0,y1,zb0,zt0,zb1,zt1,bottom=False):
    """dressed-stone block (stair material, TCol stone) whose top and bottom may slope along y (z at y0 / y1).
    Faces are wound to their normals; the loop AO darkens towards the bottom."""
    def quad(pts,n,aos):
        q=[tb.vert(p,share=False) for p in pts]; V=[Vector(tb.v[i]) for i in q]
        if (V[1]-V[0]).cross(V[2]-V[0]).dot(Vector(n))<0: q=q[::-1]; aos=aos[::-1]
        tb.face(q,[tuple(Vector(n).normalized())]*4,[(a,1.0,0.0,0.0) for a in aos],mi=1)
    lo,hi=0.72,0.95
    st=(zt1-zt0)/(y1-y0); sb=(zb1-zb0)/(y1-y0)
    quad([(x0,y0,zt0),(x1,y0,zt0),(x1,y1,zt1),(x0,y1,zt1)],(0.0,-st,1.0),[hi]*4)
    if bottom: quad([(x0,y0,zb0),(x1,y0,zb0),(x1,y1,zb1),(x0,y1,zb1)],(0.0,sb,-1.0),[lo]*4)
    for x,nx in ((x0,-1.0),(x1,1.0)):
        quad([(x,y0,zb0),(x,y1,zb1),(x,y1,zt1),(x,y0,zt0)],(nx,0.0,0.0),[lo,lo,hi,hi])
    for y,ny,zb,zt in ((y0,-1.0,zb0,zt0),(y1,1.0,zb1,zt1)):
        quad([(x0,y,zb),(x1,y,zb),(x1,y,zt),(x0,y,zt)],(0.0,ny,0.0),[lo,lo,hi,hi])
def _stair_wall(tb,x0,x1):
    """built transition between a flight (on +x of x1) and the natural cliff (on -x of x0): a cheek wall with a sloped
    coping along the part of the flight in front of the cliff, a capped pier where the cliff meets the flight (it
    swallows the cliff's end), and a kerb at terrace height along the upper flight. It stops 5 cm short of the tile's
    top side, so the tile's seam with the terrace behind it is unchanged."""
    zb=-1.55; zc=lambda y: -1.1+(y+1.5)*0.5           # coping line: 0.4 m above the treads, parallel to the pitch
    _stone_block(tb,x0,x1,-1.5,-0.5,zb,zc(-1.5),zb,zc(-0.5))
    _stone_block(tb,x0-0.04,x1+0.04,-1.5,-0.5,zc(-1.5)-0.02,zc(-1.5)+0.09,zc(-0.5)-0.02,zc(-0.5)+0.09,bottom=True)
    _stone_block(tb,x0-0.04,x1+0.03,-0.5,0.45,zb,0.30,zb,0.30)
    _stone_block(tb,x0-0.08,x1+0.07,-0.54,0.49,0.28,0.40,0.28,0.40,bottom=True)
    _stone_block(tb,x0,x1,0.45,1.45,zb,0.14,zb,0.14)
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
