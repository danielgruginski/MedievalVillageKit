
import bpy, numpy as np, os, math
VK_ROOT=r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"     # project folder (see HANDOFF.md)
TEXDIR=os.path.join(VK_ROOT,"assets","textures")                       # generated textures are written here, then packed
os.makedirs(TEXDIR,exist_ok=True)
f32=np.float32
def grid(S):
    y,x=np.mgrid[0:S,0:S].astype(f32)/S
    return x,y
def fbm(S,beta=2.0,seed=0,fmin=1.0,fmax=None,ax=1.0,ay=1.0,angle=0.0):
    """tileable fractal noise, zero mean / unit std. ax>1 elongates along x, ay>1 along y"""
    rng=np.random.default_rng(seed)
    F=np.fft.fft2(rng.standard_normal((S,S)))
    f=np.fft.fftfreq(S)*S
    FX,FY=np.meshgrid(f,f)
    if angle:
        c,s=math.cos(angle),math.sin(angle); FX,FY=FX*c+FY*s,-FX*s+FY*c
    r=np.sqrt((FX*ax)**2+(FY*ay)**2); r[0,0]=1.0
    amp=r**(-beta/2.0); amp[r<fmin]=0.0
    if fmax is not None: amp[r>fmax]=0.0
    amp[0,0]=0.0
    o=np.real(np.fft.ifft2(F*amp)).astype(f32)
    return (o-o.mean())/(o.std()+1e-8)
def blur(a,sigma):
    S=a.shape[0]; f=np.fft.fftfreq(S); FX,FY=np.meshgrid(f,f)
    g=np.exp(-2.0*(np.pi*sigma)**2*(FX**2+FY**2))
    if a.ndim==2: return np.real(np.fft.ifft2(np.fft.fft2(a)*g)).astype(f32)
    return np.stack([np.real(np.fft.ifft2(np.fft.fft2(a[...,i])*g)) for i in range(a.shape[2])],-1).astype(f32)
def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1); return (t*t*(3-2*t)).astype(f32)
def voronoi(x,y,pts,sx=1.0,sy=1.0):
    F1=np.full(x.shape,9.0,f32); F2=F1.copy(); ID=np.zeros(x.shape,np.int32)
    for i,(px,py) in enumerate(pts):
        dx=np.abs(x-px); dx=np.minimum(dx,1-dx)*sx
        dy=np.abs(y-py); dy=np.minimum(dy,1-dy)*sy
        d=np.sqrt(dx*dx+dy*dy)
        m=d<F1
        F2=np.where(m,F1,np.minimum(F2,d)); ID[m]=i; F1=np.where(m,d,F1)
    return F1,F2,ID
def normal_from_height(h,depth_m,tile_m):
    """tangent-space normal (OpenGL / Y+), array row 0 = top of image"""
    S=h.shape[0]; px=tile_m/S; hm=h*depth_m
    gx=(np.roll(hm,-1,1)-np.roll(hm,1,1))/(2*px)
    gr=(np.roll(hm,-1,0)-np.roll(hm,1,0))/(2*px)
    L=np.sqrt(gx*gx+gr*gr+1)
    return np.stack([-gx/L,gr/L,1/L],-1).astype(f32)
def cavity_ao(h,radii=(3,10,30),k=(3.0,2.0,1.2),floor=0.25):
    occ=np.zeros_like(h)
    for r,kk in zip(radii,k): occ+=np.maximum(blur(h,r)-h,0)*kk
    return np.clip(1-occ,floor,1).astype(f32)
def painted_light(n,L=(-0.35,0.75,0.55)):
    L=np.array(L,f32); L/=np.linalg.norm(L)
    return np.clip(n[...,0]*L[0]+n[...,1]*L[1]+n[...,2]*L[2],0,1).astype(f32)
def write_map(name,arr,data=False):
    S=arr.shape[0]
    if arr.ndim==2: arr=np.stack([arr,arr,arr],-1)
    rgba=np.concatenate([np.clip(arr,0,1).astype(f32),np.ones(arr.shape[:2]+(1,),f32)],-1)
    img=bpy.data.images.get(name)
    if img is None:
        img=bpy.data.images.new(name,S,S,alpha=False,is_data=data)
    else:
        if img.packed_file: img.unpack(method="REMOVE") if False else None
        if tuple(img.size)!=(S,S): img.scale(S,S)
    if data and img.colorspace_settings.name!="Non-Color": img.colorspace_settings.name="Non-Color"
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    img.update()
    img.filepath_raw=os.path.join(TEXDIR,name+".png"); img.file_format="PNG"; img.save(); img.pack()
    return img
def write_set(prefix,albedo,height,rough,depth_m,tile_m,ao=None,ao_in_albedo=0.55,extra=None):
    if ao is None: ao=cavity_ao(height)
    bc=albedo*(1-ao_in_albedo+ao_in_albedo*ao)[...,None]
    write_map(prefix+"_BC",bc)
    write_map(prefix+"_N",normal_from_height(height,depth_m,tile_m)*0.5+0.5,True)
    write_map(prefix+"_H",height,True)
    write_map(prefix+"_R",rough,True)
    write_map(prefix+"_AO",ao,True)
    if extra:
        for k_,v_ in extra.items(): write_map(prefix+"_"+k_,v_,True)
    return bc
PBR_SETS={}   # prefix -> dict(depth,tile)

def draw_segments(S,segs,wrap=True):
    """segs: list of (x0,y0,x1,y1,width_px) in pixel coords. returns coverage field (0..1), tileable if wrap"""
    out=np.zeros((S,S),f32)
    offs=(-S,0,S) if wrap else (0,)
    for (x0,y0,x1,y1,w) in segs:
        for ox in offs:
            for oy in offs:
                ax,ay,bx,by=x0+ox,y0+oy,x1+ox,y1+oy
                r=w+2
                lx=int(max(0,math.floor(min(ax,bx)-r))); hx=int(min(S,math.ceil(max(ax,bx)+r)))
                ly=int(max(0,math.floor(min(ay,by)-r))); hy=int(min(S,math.ceil(max(ay,by)+r)))
                if lx>=hx or ly>=hy: continue
                yy,xx=np.mgrid[ly:hy,lx:hx].astype(f32)
                dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy+1e-6
                t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/L2,0,1)
                d=np.hypot(xx-(ax+t*dx),yy-(ay+t*dy))
                cov=np.clip(w*0.5-d+0.5,0,1)
                out[ly:hy,lx:hx]=np.maximum(out[ly:hy,lx:hx],cov)
    return out
def crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None,jit=0.55,starts=None):
    segs=[]
    def walk(x,y,a,nsteps,w,depth):
        for i in range(nsteps):
            a+=rng.uniform(-jit,jit)
            if dirbias is not None: a=a*0.7+dirbias*0.3
            st=rng.uniform(*step_px); nx,ny=x+math.cos(a)*st,y+math.sin(a)*st
            ww=max(0.5,w*(1-i/nsteps*0.7))
            segs.append((x,y,nx,ny,ww)); x,y=nx,ny
            if depth<2 and rng.random()<branch: walk(x,y,a+rng.choice([-1,1])*rng.uniform(0.6,1.1),int(nsteps*0.4),ww*0.8,depth+1)
    if starts is not None:
        for (sx_,sy_,sa_,sn_) in starts: walk(sx_,sy_,sa_,int(sn_),w0,0)
        return segs
    for _ in range(n):
        a0=rng.uniform(0,2*math.pi) if dirbias is None else dirbias+rng.uniform(-0.2,0.2)
        walk(rng.uniform(0,S),rng.uniform(0,S),a0,int(rng.uniform(*steps)),w0,0)
    return segs

# ---- helpers for the stone rework ----
def wrapd(d,P=1.0): return (d+P*0.5)%P-P*0.5
def lerp(a,b,t): return a+(b-a)*t
def smin(a,b,k):
    h=np.clip(0.5+0.5*(b-a)/k,0,1); return b+(a-b)*h-k*h*(1-h)
def down2(a):
    S=a.shape[0]//2; return a.reshape(S,2,S,2,*a.shape[2:]).mean(axis=(1,3)).astype(f32)
def hx(s_): return np.array([int(s_[i:i+2],16) for i in (1,3,5)],f32)/255.0
def luma(c): return (0.2126*c[...,0]+0.7152*c[...,1]+0.0722*c[...,2]).astype(f32)
def voronoi_edge(x,y,pts,w=None,sx=1.0,sy=1.0):
    pts=np.asarray(pts,f32); N=len(pts); w=np.zeros(N,f32) if w is None else np.asarray(w,f32)
    P1=np.full(x.shape,np.inf,f32); ID1=np.zeros(x.shape,np.int32)
    for i,(px_,py_) in enumerate(pts):
        dx=wrapd(x-px_)*sx; dy=wrapd(y-py_)*sy; P=dx*dx+dy*dy-w[i]
        m=P<P1; P1=np.where(m,P,P1); ID1[m]=i
    ax,ay=pts[ID1,0],pts[ID1,1]; ox,oy=wrapd(x-ax),wrapd(y-ay)
    E=np.full(x.shape,np.inf,f32); ID2=np.zeros_like(ID1)
    for j,(bx,by) in enumerate(pts):
        abx=wrapd(bx-ax)*sx; aby=wrapd(by-ay)*sy; L=np.hypot(abx,aby)+1e-9
        dbx=ox*sx-abx; dby=oy*sy-aby; Pb=dbx*dbx+dby*dby-w[j]
        e=(Pb-P1)/(2*L)/np.hypot(abx/L*sx,aby/L*sy)
        e=np.where(ID1==j,np.inf,e); m=e<E; E=np.where(m,e,E); ID2[m]=j
    return ID1,ID2,E.astype(f32),ox.astype(f32),oy.astype(f32)
