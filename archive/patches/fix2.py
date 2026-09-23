import sys
p=sys.argv[1]; s=open(p,encoding="utf8").read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)>=1, "MISSING: "+a[:80]
    s=s.replace(a,b)
def func(name,new):
    global s
    a=s.index("def "+name+"(")
    # function ends at the next top-level def / comment banner / assignment
    import re
    m=re.compile(r"\n(def |# ====|[A-Z_]+ *=|WS_SPECS)").search(s,a+10)
    s=s[:a]+new.rstrip("\n")+"\n"+s[m.start()+1:]

# ---------- pelt mesh (replaces concave n-gons for draped hides)
rep('''def ind_tanning_pit(k):''','''def ind_pelt(k,w,h,mi,seed=0,z_fn=None,thick=0.014,M=None):
    """hide as a small radial mesh (centre + 2 rings) in the XY plane, draped by z_fn(x,y); two-sided"""
    out=ind_pelt_outline(w,h,seed); rings=[[(0.0,0.0)],[(x*0.55,y*0.55) for x,y in out],out]
    zf=z_fn or (lambda x,y: 0.0)
    sub=Kit(); n=len(out)
    for side in(0,1):
        dz=-thick if side else 0.0
        V=[[sub.bm.verts.new((x,y,zf(x,y)+dz)) for (x,y) in r] for r in rings]
        fs=[]
        for i in range(n):
            j=(i+1)%n
            q=[(V[0][0],V[1][i],V[1][j]),(V[1][i],V[2][i],V[2][j],V[1][j])]
            for t in q:
                fs.append(sub.bm.faces.new(t if side==0 else t[::-1]))
        for f in fs:
            f.material_index=mi
            for l in f.loops: l[sub.uv].uv=(l.vert.co.x*0.8,l.vert.co.y*0.8)
    sub.bm.normal_update()
    merge_kit(k,sub,M or Matrix.Identity(4))
def ind_tanning_pit(k):''')
rep('''    k.quad([(-A,-A,0.14),(A,-A,0.14),(A,A,0.14),(-A,A,0.14)],HIDE,uvs=[(0,0),(1,0),(1,1),(0,1)])   # tan liquor
    # a hide soaking, one end pulled up over the kerb
    sub=Kit(); ind_ngon(sub,[(x,z,0) for (x,z) in ind_pelt_outline(0.8,1.0,seed=3)],PIGSKIN,two_sided=True,off=(0,0,-0.01))
    for v in sub.bm.verts: v.co.z+=0.155+min(0.17,max(0.0,v.co.y-0.25)*0.9)
    merge_kit(k,sub,Matrix.Translation((0.05,0.12,0))@Matrix.Rotation(0.15,4,"Z"))''','''    k.quad([(-A,-A,0.14),(A,-A,0.14),(A,A,0.14),(-A,A,0.14)],BRONZE,uvs=[(0,0),(1,0),(1,1),(0,1)])   # tan liquor (glossy oak-bark brown)
    # a hide soaking, one end pulled up over the kerb and hanging outside
    def zf(x,y):
        if y<0.3: return 0.16
        if y<0.62: return 0.16+(y-0.3)*0.55
        return 0.34-(y-0.62)*1.4
    ind_pelt(k,0.95,1.35,HIDE,seed=3,z_fn=zf,M=Matrix.Translation((0.05,0.25,0))@Matrix.Rotation(0.12,4,"Z"))
    for i,(x,y) in enumerate(((-0.95,-0.9),(0.95,0.95),(1.0,-0.5))): ind_tuft(k,(x,y,0.0),0.4,seed=80+i)''')

# ---------- hides pile
func("ind_pile_hides",'''def ind_pile_hides(k,size=1):
    """stacks of folded hides (HIDE / MUSH_BROWN) with a pelt draped over each stack"""
    rnd=random.Random(size)
    stacks=[(0,0,3)] if size==1 else ([(-0.6,0,4),(0.6,0.05,2)] if size==2 else [(-1.0,0,5),(0.1,0.0,3),(1.15,0.1,2)])
    for si,(sx,sy,n) in enumerate(stacks):
        for i in range(n):
            mi=(HIDE,MUSH_BROWN,HIDE,PIGSKIN)[(i+si+size)%4]
            k.box((sx+rnd.uniform(-.06,.06),sy+rnd.uniform(-.06,.06),0.06+i*0.1),(0.9,0.66,0.09),mi,rot=(0,0,rnd.uniform(-0.25,0.25)),bevel=0.04,segs=2,jitter=0.025,seed=size*20+i+si*7)
        top=0.06+n*0.1+0.02
        def zf(x,y,top=top):
            ov=max(abs(x)-0.42,0.0); ovy=max(abs(y)-0.3,0.0)
            return top-ov*1.3-ovy*1.2
        ind_pelt(k,1.25,0.95,MUSH_BROWN if (si+size)%2 else HIDE,seed=size*3+si,z_fn=zf,M=Matrix.Translation((sx,sy,0))@Matrix.Rotation(rnd.uniform(-0.3,0.3),4,"Z"))''')

# ---------- wool: fluffy fleeces
rep('''    for i in range(1+size):
        a=rnd.uniform(0,6.28); d=0.9+0.3*size
        _ico(k,(math.cos(a)*d*0.7,-0.55-rnd.uniform(0,0.2),0.12),0.22,CLOTH_B,(1.3,1,0.55),sub=2,jit=0.03,seed=i+size)''','''    for i in range(1+size):
        cx=rnd.uniform(-0.5,0.5)*size; cy=-0.6-rnd.uniform(0,0.2)
        for j in range(4):
            _ico(k,(cx+rnd.uniform(-0.18,0.18),cy+rnd.uniform(-0.12,0.12),0.1+0.03*j),rnd.uniform(0.12,0.17),CLOTH_B,(1.2,1,0.7),sub=1,jit=0.02,seed=i*7+j+size)''')

# ---------- mash tun: open tun
rep('''    for zz,(r0,r1) in((0.52,(R*0.95,R)),(0.98,(R,R*0.97))): _cyl(k,(0,0,zz),r0,r1,0.46,n,WOOD)
    for z in(0.36,0.78,1.14): ring(k,(0,0,z),R+0.005,R+0.05,0.07,IRON,n=n,axis="Z")
    lathe(k,[(R*0.97,1.21),(R*0.9,1.21),(R*0.88,1.1)],segs=n,mi=WOOD)
    ind_heap(k,(0,0,1.02),0.85,0.85,0.12,BREAD,seed=4,sub=2,rough=0.1)''','''    lathe(k,[(R*0.94,0.28),(R,0.75),(R*0.97,1.21),(R*0.89,1.21),(R*0.87,0.7)],segs=n,mi=WOOD)
    for z in(0.36,0.78,1.14): ring(k,(0,0,z),(R*0.95 if z<0.5 else R*0.985)-0.01,(R*0.95 if z<0.5 else R*0.985)+0.05,0.07,IRON,n=n,axis="Z")
    ind_heap(k,(0,0,0.98),0.8,0.8,0.1,BREAD,seed=4,sub=2,rough=0.1)''')
rep('''    _cyl(k,(0,-0.82,0.18),0.24,0.28,0.36,12,WOOD); ring(k,(0,-0.82,0.28),0.28,0.31,0.05,IRON,n=12,axis="Z")
    _cyl(k,(0,-0.82,0.32),0.25,0.25,0.02,12,YELLOW)''','''    lathe(k,[(0.0,0.02),(0.24,0.02),(0.28,0.36),(0.25,0.36),(0.22,0.06)],center=(0,-0.82,0),segs=12,mi=WOOD)
    ring(k,(0,-0.82,0.28),0.27,0.3,0.05,IRON,n=12,axis="Z")
    lathe(k,[(0.245,0.29),(0.0,0.29)],center=(0,-0.82,0),segs=12,mi=BRONZE)''')

# ---------- meat rack colours
rep('''        ind_lathe(k,[(0.0,1.28),(0.09,1.3),(0.16,1.38),(0.17,1.52),(0.1,1.72),(0.03,1.8)],c=(x,0,0),segs=10,mi=PIGSKIN if i%2 else HIDE,smooth=True)''','''        ind_lathe(k,[(0.0,1.28),(0.09,1.3),(0.16,1.38),(0.17,1.52),(0.1,1.72),(0.03,1.8)],c=(x,0,0),segs=10,mi=CLAY if i%2 else MUSH_BROWN,smooth=True)
        _cyl(k,(x,0,1.84),0.035,0.03,0.1,6,PAPER)''')
rep('''                for j in range(3): _ico(k,(x,y,1.2-j*0.16),0.06,BREAD,(0.9,0.9,1.6),sub=1)
            else:
                k.box((x,y,1.02),(0.12,0.025,0.5),HIDE,rot=(0,rnd.uniform(-.1,.1),0),bevel=0.01)
    k.box((0,0,0.03),(1.6,0.6,0.06),SOIL,bevel=0.02)''','''                for j in range(3): _ico(k,(x,y,1.2-j*0.16),0.06,MUSH_RED if j%2 else MUSH_BROWN,(0.9,0.9,1.6),sub=1)
            else:
                k.box((x,y,1.02),(0.12,0.025,0.5),MUSH_BROWN,rot=(0,rnd.uniform(-.1,.1),0),bevel=0.01)''')

# ---------- herb rack: fewer items
rep('''        for i in range(9):
            x=rnd.uniform(-W/2+0.2,W/2-0.2); y=rnd.uniform(-0.25,0.25)''','''        for i in range(6):
            x=-W/2+0.25+i*(W-0.5)/5+rnd.uniform(-0.06,0.06); y=rnd.uniform(-0.2,0.2)''')

# ---------- clay pit spoil heaps: dug clay + soil
rep('''    ind_heap(k,(-0.6,1.2,0),1.2,0.4,0.42,SOIL,seed=5,sub=2,rough=0.2)
    ind_heap(k,(1.2,0.3,0),0.4,1.0,0.35,SOIL,seed=6,sub=2,rough=0.2)''','''    ind_heap(k,(-0.6,1.2,0),1.2,0.4,0.42,CLAY,seed=5,sub=2,rough=0.2)
    ind_heap(k,(1.2,0.3,0),0.4,1.0,0.35,SOIL,seed=6,sub=2,rough=0.2)
    ind_chunks(k,(-0.6,1.2,0),1.1,0.35,0.4,6,[SOIL,CLAY],seed=12,size=(0.1,0.18))''')
open(p,"w",encoding="utf8").write(s); print("ok")
