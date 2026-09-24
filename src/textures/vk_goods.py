# ===================== VK GOODS ATLAS : hand-painted small goods (food, hides, ...) =====================
# One 2048 atlas T_VK_Goods (4 x 4 cells of 512 px) for the material M_VK_Goods (kit slot GOODS).
# Run after vk_tex, vk_texgen, vk_tex2 (helpers) and vk_mat (pbr_material, for M_VK_Goods):
#   g={}; [exec(bpy.data.texts[t].as_string(),g) for t in ("vk_tex","vk_texgen","vk_tex2","vk_mat","vk_goods")]
#   g["gen_goods_atlas"]()
# Cell coordinates (see goods_map in vk_helpers): u = around the item (0 = its reference side, 1 = the opposite side,
# mirrored so there is no seam), v = along the item (0 = bottom / tail / root tip, 1 = top / head / crown).
# Flat items (hides, pelts, pulp) use u, v as plain planar coordinates.
GOODS_CELLS=("cabbage","pumpkin","carrot","apple","bread","cheese","fish","fish_smoked",
             "hide","fur","meat","ham","sausage","turnip","herbs","pomace")
GOODS_ROUGH=dict(cabbage=0.55,pumpkin=0.45,carrot=0.55,apple=0.32,bread=0.78,cheese=0.5,fish=0.28,fish_smoked=0.42,
                 hide=0.7,fur=0.92,meat=0.34,ham=0.42,sausage=0.4,turnip=0.45,herbs=0.88,pomace=0.45)

def _uv(S):
    U,Y=grid(S); return U,(1.0-Y).astype(f32)
def _lines(S,pts_uv,w_px):
    """polyline in cell uv (v up) -> coverage"""
    segs=[(a[0]*S,(1-a[1])*S,b[0]*S,(1-b[1])*S,w_px) for a,b in zip(pts_uv[:-1],pts_uv[1:])]
    return draw_segments(S,segs,wrap=False)
def _dots(S,rng,n,r_px,region=None,aspect=1.0):
    """n small round dots (coverage), optionally only where region(u,v) is true"""
    items=[]
    for _ in range(n*3):
        if len(items)>=n: break
        u,v=rng.uniform(0,1,2)
        if region is not None and not region(u,v): continue
        r=rng.uniform(*r_px); items.append((u*S,(1-v)*S,r,r*aspect,0.0,1.0))
    _,C,_=_stamp_domes(S,items,wrap=False)
    return C

def _p_cabbage(S,rng):
    U,V=_uv(S)
    col=lerp(hx("#58874A"),hx("#B4CF86"),smooth(0.1,0.95,V)[...,None])*(1+0.05*fbm(S,2.2,11,fmin=3,fmax=30))[...,None]
    h=0.5+0.03*fbm(S,2.0,12,fmin=4,fmax=60)
    for i,v0 in enumerate((0.28,0.46,0.61,0.74,0.85)):            # overlapping leaf edges, inner leaves above
        e=v0+0.045*np.sin(U*math.pi*rng.uniform(1.4,2.6)+rng.uniform(0,6))
        d=V-e
        col=col*(1-0.28*(smooth(0.06,0.0,d)*(d>0))[...,None])     # shadow of the outer leaf on the one above
        rim=np.exp(-(d/0.01)**2); col=lerp(col,hx("#D6E6B0"),0.45*rim[...,None]); h=h+0.2*smooth(-0.1,0.0,-d)*0.3
    vein=np.zeros((S,S),f32)
    for j in range(5):                                            # curved midribs rising from the stem, fading out
        u0=(j+0.5)/5+rng.uniform(-0.05,0.05); ph=rng.uniform(0,6); top=rng.uniform(0.55,0.8); bend=rng.uniform(0.08,0.16)*rng.choice([-1,1])
        path=lambda t: (u0+bend*math.sin(t*2.2+ph)*t,t*top)
        for a,b in zip(np.linspace(0,1,14)[:-1],np.linspace(0,1,14)[1:]):
            vein=np.maximum(vein,_lines(S,[path(a),path(b)],max(2.0,8*(1-a)))*(1-0.6*a))
        for t in np.linspace(0.15,0.85,5):                        # side veins curving up and out
            x0,y0=path(t)
            for s_ in (-1,1):
                vein=np.maximum(vein,_lines(S,[(x0,y0),(x0+s_*0.05,y0+0.04),(x0+s_*0.09,y0+0.1)],3.0)*0.7*(1-0.5*t))
    vein=blur(vein,2.0)
    col=lerp(col,hx("#E1EDC6"),0.6*vein[...,None]); h=h+0.12*vein
    return col,h

def _p_pumpkin(S,rng):
    U,V=_uv(S)
    q=(U*4)%1.0; rib=np.sin(np.pi*q).astype(f32)                 # grooves at u = k/4 (they match the modelled ribs)
    col=hx("#D46E1A")*(0.72+0.34*rib**0.5)[...,None]
    groove=np.exp(-((np.minimum(q,1-q))/0.045)**2)
    col=lerp(col,hx("#7A3610"),0.55*groove[...,None])
    col=lerp(col,hx("#F3A94E"),(0.22*rib**6)[...,None])
    col=col*(1+0.07*fbm(S,2.0,21,fmin=3,fmax=80,ay=8))[...,None]    # streaks along the ribs
    sp=_dots(S,rng,160,(1.5,3.0)); col=lerp(col,hx("#F0C27A"),0.5*sp[...,None])
    col=lerp(col,hx("#6B4A1E"),(0.7*smooth(0.9,1.0,V))[...,None]); col=lerp(col,hx("#5E5020"),(0.6*smooth(0.07,0.0,V))[...,None])
    h=0.3+0.55*rib**0.6+0.03*fbm(S,2.0,22,fmin=8,fmax=100)
    return col,h

def _p_carrot(S,rng):
    U,V=_uv(S)
    col=hx("#DE6B24")*(1+0.07*fbm(S,2.0,31,fmin=3,fmax=60,ay=6))[...,None]
    h=0.5+0.02*fbm(S,2.0,32,fmin=6,fmax=90)
    for _ in range(26):                                            # growth rings, broken around the root
        v0=rng.uniform(0.04,0.93); part=smooth(0.1,0.5,fbm(S,2.0,int(rng.integers(0,1e6)),fmin=2,fmax=6))
        rr=np.exp(-((V-v0)/0.005)**2)*part
        col=lerp(col,hx("#A8531C"),0.55*rr[...,None]); col=col*(1+0.1*np.exp(-((V-v0-0.01)/0.005)**2)*part)[...,None]; h=h-0.15*rr
    col=lerp(col,hx("#8A8A2C"),(0.8*smooth(0.9,1.0,V))[...,None]); col=lerp(col,hx("#E9A060"),(0.4*smooth(0.06,0.0,V))[...,None])
    return col,h

def _p_apple(S,rng):
    U,V=_uv(S)
    col=hx("#A4221A")*(1+0.06*fbm(S,2.2,41,fmin=2,fmax=40))[...,None]
    fl=smooth(0.2,1.3,fbm(S,2.0,42,fmin=3,fmax=50,ay=7))*smooth(0.05,0.7,V)     # flames from the stem down
    col=lerp(col,hx("#D65A26"),0.55*fl[...,None])
    col=lerp(col,hx("#C9A13A"),(0.4*smooth(0.55,1.0,U)*(1-fl))[...,None])        # blush side
    lt=_dots(S,rng,260,(1.2,2.4)); col=lerp(col,hx("#EBC98A"),0.55*lt[...,None])
    col=lerp(col,hx("#6A5222"),(0.75*smooth(0.9,1.0,V))[...,None]); col=lerp(col,hx("#5A3A1C"),(0.7*smooth(0.07,0.0,V))[...,None])
    h=0.5+0.02*fbm(S,2.0,43,fmin=4,fmax=60)-0.2*smooth(0.9,1.0,V)
    return col,h

def _p_bread(S,rng):
    U,V=_uv(S)
    col=lerp(hx("#DDB67A"),hx("#C4843C"),smooth(0.18,0.45,V)[...,None])
    col=lerp(col,hx("#94541E"),smooth(0.65,0.98,V)[...,None])
    col=col*(1+0.07*fbm(S,2.0,51,fmin=3,fmax=60))[...,None]
    h=0.5+0.05*fbm(S,2.0,52,fmin=6,fmax=90)
    for uc in (0.22,0.5,0.78):                                     # three scored slashes on top, the crumb showing
        items=[(uc*S,(1-0.74)*S,0.16*S,0.035*S,math.radians(rng.uniform(55,70)),1.0)]
        _,cut,_=_stamp_domes(S,items,wrap=False,irr=0.25,rng=rng)
        ear=np.clip(blur(cut,4.0)-cut,0,1)*3
        col=lerp(col,hx("#6E3A14"),np.clip(ear,0,1)[...,None]*0.8); col=lerp(col,hx("#EAD19C"),cut[...,None]); h=h-0.35*cut+0.1*np.clip(ear,0,1)
    fl=smooth(1.2,2.2,fbm(S,1.2,53,fmin=30,fmax=300))*smooth(0.5,0.9,V)
    col=lerp(col,hx("#F3E9D3"),0.7*fl[...,None])
    return col,h

def _p_cheese(S,rng):
    U,V=_uv(S)
    # waxed rind: calm pale yellow (the side mapping stretches u ~5x, so any strong pattern turns into streaks)
    col=lerp(hx("#E6BA4C"),hx("#D5A13A"),smooth(-0.8,2.2,fbm(S,2.8,61,fmin=1,fmax=6))[...,None])
    col=col*(1+0.03*fbm(S,1.5,63,fmin=20,fmax=200))[...,None]
    col=col*(1-0.14*(smooth(0.08,0.0,V)+smooth(0.92,1.0,V)))[...,None]              # rounded rim of the wheel
    sp=_dots(S,rng,90,(1.4,2.4)); col=lerp(col,hx("#B98A34"),0.35*sp[...,None])
    h=0.5+0.02*fbm(S,2.0,62,fmin=6,fmax=80)
    return col,h

def _fish(S,rng,back,flank,belly,dark,eye_iris,smoked=False):
    U,V=_uv(S)
    col=lerp(hx(back),hx(flank),smooth(0.22,0.42,U)[...,None]); col=lerp(col,hx(belly),smooth(0.62,0.82,U)[...,None])
    col=col*(1+0.05*fbm(S,2.0,71,fmin=3,fmax=40))[...,None]
    sp=_dots(S,rng,90,(2.0,4.0),region=lambda u,v: u<0.3 and 0.2<v<0.85)
    col=lerp(col,hx(dark),0.6*sp[...,None])
    # scales: crescents in offset rows over the flank
    kU,kV=28.0,34.0
    gu=U*kU; gv=V*kV+0.5*(np.floor(gu)%2)
    du=(gu%1.0)-0.5; dv=(gv%1.0)-0.2; d=np.sqrt(du*du+dv*dv)
    sc=np.exp(-((d-0.5)/0.07)**2)*(dv<0.3)*smooth(0.15,0.3,U)*smooth(0.9,0.7,U)*smooth(0.16,0.25,V)*smooth(0.8,0.72,V)
    col=col*(1+(0.12 if not smoked else 0.07)*sc)[...,None]
    ll=np.exp(-((U-(0.42+0.015*np.sin(V*9)))/0.006)**2)*smooth(0.18,0.25,V)*smooth(0.82,0.76,V)
    col=lerp(col,hx(dark),0.55*ll[...,None])
    gill=np.exp(-((V-(0.8+0.035*np.sin(np.clip(U,0,1)*np.pi)))/0.006)**2)*smooth(0.05,0.15,U)*smooth(0.95,0.8,U)
    col=lerp(col,hx(dark),0.7*gill[...,None])
    ex,ey=0.33,0.9; er=np.sqrt(((U-ex)/0.05)**2+((V-ey)/0.022)**2)
    col=lerp(col,hx(eye_iris),smooth(1.0,0.85,er)[...,None]); col=lerp(col,hx("#0E0E10"),smooth(0.6,0.45,er)[...,None])
    col=lerp(col,hx("#F4F4EE"),(smooth(0.25,0.1,np.sqrt(((U-ex+0.012)/0.05)**2+((V-ey-0.006)/0.022)**2))*(0 if smoked else 0.9))[...,None])
    col=col*(1-0.3*smooth(0.95,1.0,V))[...,None]
    tail=smooth(0.17,0.1,V); rays=0.5+0.5*np.sin(U*np.pi*26)
    col=lerp(col,hx(dark)*(0.9+0.3*rays[...,None]),0.75*tail[...,None])
    h=0.5+0.15*sc-0.2*gill-0.1*ll+0.05*rays*tail+0.2*smooth(0.85,0.45,er)
    return col,h

def _p_fish(S,rng): return _fish(S,rng,"#2C4557","#8D9FA8","#DCE1DC","#1E2A33","#D8C37E")
def _p_fish_smoked(S,rng):
    col,h=_fish(S,rng,"#5E3A1C","#B2783A","#D9AF6E","#3A2412","#3A2A1A",smoked=True)
    col=col*(1-0.12*smooth(0.4,1.5,fbm(S,2.0,74,fmin=3,fmax=30,ay=5)))[...,None]
    return col,h

def _p_hide(S,rng):
    U,V=_uv(S)
    r=np.sqrt(((U-0.5)/0.5)**2+((V-0.5)/0.5)**2)
    col=lerp(hx("#C08A55"),hx("#734826"),smooth(0.35,1.05,r)[...,None])
    col=col*(1+0.1*fbm(S,2.3,81,fmin=2,fmax=20))[...,None]*(1+0.04*fbm(S,1.5,82,fmin=60,fmax=400))[...,None]
    cr=draw_segments(S,crack_segments(S,rng,n=9,steps=(10,24),step_px=(10,20),w0=3.0,branch=0.2,jit=0.35))
    cr=blur(cr,1.5); col=col*(1-0.18*cr[...,None])
    spine=np.exp(-((U-0.5-0.01*np.sin(V*7))/0.03)**2)*smooth(0.1,0.3,V)*smooth(0.9,0.7,V)
    col=col*(1-0.12*spine[...,None])
    h=0.5+0.05*fbm(S,2.0,83,fmin=4,fmax=80)-0.15*cr
    return col,h

def _p_fur(S,rng):
    U,V=_uv(S)
    col=hx("#4E3522")*(1+0.12*fbm(S,2.3,91,fmin=2,fmax=16))[...,None]
    flow=fbm(S,2.5,92,fmin=1,fmax=5)*0.6
    tip=np.zeros((S,S),f32); root=np.zeros((S,S),f32)
    for layer in range(2):
        segs=[]; tsegs=[]
        for _ in range(5200):
            x,y=rng.uniform(0,S,2); a=math.pi/2+float(flow[int(y)%S,int(x)%S])+rng.uniform(-0.25,0.25)
            L=rng.uniform(14,26); ex,ey=x+math.cos(a)*L,y+math.sin(a)*L
            segs.append((x,y,ex,ey,rng.uniform(2.2,3.4))); tsegs.append((x+math.cos(a)*L*0.6,y+math.sin(a)*L*0.6,ex,ey,1.8))
        root=np.maximum(root,draw_segments(S,segs)); tip=np.maximum(tip,draw_segments(S,tsegs))
    col=col*(1-0.25*root[...,None]); col=lerp(col,hx("#A07A52"),0.55*tip[...,None])
    h=0.4+0.3*root+0.2*tip
    return col,h

def _p_meat(S,rng):
    U,V=_uv(S)
    col=hx("#A6342C")*(1+0.08*fbm(S,2.2,101,fmin=2,fmax=30))[...,None]
    fat=draw_segments(S,crack_segments(S,rng,n=16,steps=(10,22),step_px=(12,20),w0=9.0,branch=0.1,jit=0.3))
    fat=np.clip(blur(fat,4.0)*1.3,0,1)*smooth(-0.2,0.6,fbm(S,2.0,103,fmin=3,fmax=12))
    col=lerp(col,hx("#EBCBBE"),0.8*fat[...,None])
    cap=smooth(0.8,0.86,V+0.03*np.sin(U*9)); col=lerp(col,hx("#E8D3B8"),cap[...,None])
    h=0.5+0.08*fat+0.1*cap+0.03*fbm(S,2.0,102,fmin=6,fmax=80)
    return col,h

def _p_ham(S,rng):
    U,V=_uv(S)
    col=lerp(hx("#8A4428"),hx("#B8703F"),smooth(0.3,1.5,fbm(S,2.2,111,fmin=2,fmax=20))[...,None])
    col=lerp(col,hx("#D9A877"),(smooth(0.75,0.88,V)*0.8)[...,None]); col=lerp(col,hx("#C9956A"),(smooth(0.15,0.0,V)*0.7)[...,None])
    net=np.maximum(np.exp(-(np.sin(np.pi*(U*9+V*7))/0.08)**2),np.exp(-(np.sin(np.pi*(U*9-V*7))/0.08)**2))
    col=lerp(col,hx("#4A2A18"),0.45*net[...,None])
    h=0.5+0.04*fbm(S,2.0,112,fmin=4,fmax=60)-0.08*net
    return col,h

def _p_sausage(S,rng):
    U,V=_uv(S)
    col=hx("#7A2B21")*(1+0.08*fbm(S,2.2,121,fmin=2,fmax=24))[...,None]
    sp=_dots(S,rng,700,(1.4,3.2)); col=lerp(col,hx("#E6CBBE"),0.75*sp[...,None])
    wr=0.5+0.5*np.sin(V*np.pi*60+fbm(S,2.0,122,fmin=2,fmax=8)*2)
    col=col*(1+0.06*wr)[...,None]
    tie=np.exp(-((V-0.03)/0.012)**2)+np.exp(-((V-0.97)/0.012)**2)
    col=lerp(col,hx("#D8C49A"),np.clip(tie,0,1)[...,None])
    h=0.5+0.1*sp+0.04*wr+0.15*tie
    return col,h

def _p_turnip(S,rng):
    U,V=_uv(S)
    edge=0.6+0.035*blur(fbm(S,2.6,131,fmin=1,fmax=4),8.0)
    col=lerp(hx("#EEE6D6"),hx("#8B3C78"),smooth(-0.14,0.16,V-edge)[...,None])
    col=col*(1+0.04*np.sin(V*np.pi*80))[...,None]*(1+0.04*fbm(S,2.0,132,fmin=4,fmax=60))[...,None]
    hairs=np.zeros((S,S),f32)
    for _ in range(40):
        u0=rng.uniform(0,1); v0=rng.uniform(0.0,0.18); hairs=np.maximum(hairs,_lines(S,[(u0,v0),(u0+rng.uniform(-0.05,0.05),v0-0.05)],1.5))
    col=lerp(col,hx("#B7A98A"),0.6*hairs[...,None])
    col=lerp(col,hx("#6C8A32"),smooth(0.94,0.99,V)[...,None])
    h=0.5+0.02*np.sin(V*np.pi*80)
    return col,h

def _p_herbs(S,rng):
    U,V=_uv(S)
    col=hx("#5F6A3C")*(1+0.08*fbm(S,2.0,141,fmin=2,fmax=20))[...,None]
    h=np.full((S,S),0.3,f32)
    stems=draw_segments(S,[(x,y,x+math.cos(a)*L,y+math.sin(a)*L,2.2) for x,y,a,L in
                           [(*rng.uniform(0,S,2),rng.uniform(0,6.28),rng.uniform(30,70)) for _ in range(120)]])
    col=lerp(col,hx("#8C7A4A"),0.8*stems[...,None])
    PAL=[hx(c_) for c_ in ("#7E8B4C","#98A35C","#5C6939","#B7A758","#6F7F46")]
    items=[(*rng.uniform(0,S,2),rng.uniform(6,12),rng.uniform(3,5.5),rng.uniform(0,math.pi),1.0) for _ in range(1500)]
    Hl,Cl,IDl=_stamp_domes(S,items,flat=0.6,rng=rng)
    pid=rng.integers(0,len(PAL),len(items)); lc=np.stack(PAL)[pid][np.maximum(IDl,0)]
    col=lerp(col,lc,Cl[...,None]); h=h+0.4*Hl
    fl=_dots(S,rng,90,(2.5,4.0)); col=lerp(col,hx("#8C6A9E"),0.85*fl[...,None])
    return col,h

def _p_pomace(S,rng):
    U,V=_uv(S)
    col=hx("#9A7038")*(1+0.1*fbm(S,2.2,151,fmin=2,fmax=30))[...,None]
    items=[(*rng.uniform(0,S,2),rng.uniform(6,16),rng.uniform(4,10),rng.uniform(0,math.pi),1.0) for _ in range(700)]
    Hp,Cp,IDp=_stamp_domes(S,items,flat=0.7,irr=0.4,rng=rng)
    PAL=np.stack([hx(c_) for c_ in ("#D2AE5E","#C29A48","#B8893C","#7E3A22")])
    pid=rng.integers(0,len(PAL),len(items)); col=lerp(col,PAL[pid][np.maximum(IDp,0)],Cp[...,None])
    seeds=_dots(S,rng,120,(2.0,3.2),aspect=0.55); col=lerp(col,hx("#3A2412"),0.9*seeds[...,None])
    h=0.4+0.4*Hp+0.1*seeds
    return col,h

_PAINTERS=dict(cabbage=_p_cabbage,pumpkin=_p_pumpkin,carrot=_p_carrot,apple=_p_apple,bread=_p_bread,cheese=_p_cheese,
               fish=_p_fish,fish_smoked=_p_fish_smoked,hide=_p_hide,fur=_p_fur,meat=_p_meat,ham=_p_ham,
               sausage=_p_sausage,turnip=_p_turnip,herbs=_p_herbs,pomace=_p_pomace)

def gen_goods_atlas(S=2048,seed=900,depth=0.006,tile=1.2,out_prefix="T_VK_Goods",write=True,cells=None):
    """paint every cell at 2x and store the 4 x 4 atlas at S; also (re)builds the material M_VK_Goods"""
    C=S//4; BC=np.zeros((S,S,3),f32); H=np.zeros((S,S),f32); R=np.zeros((S,S),f32)
    if cells is not None and bpy.data.images.get(out_prefix+"_BC") is not None:   # repaint only some cells
        prev=bpy.data.images[out_prefix+"_BC"]; a=np.array(prev.pixels[:],f32).reshape(S,S,4)[::-1]; BC[:]=a[...,:3]
        H[:]=np.array(bpy.data.images[out_prefix+"_H"].pixels[:],f32).reshape(S,S,4)[::-1][...,0]
        R[:]=np.array(bpy.data.images[out_prefix+"_R"].pixels[:],f32).reshape(S,S,4)[::-1][...,0]
    for i,name in enumerate(GOODS_CELLS):
        if cells is not None and name not in cells: continue
        rng=np.random.default_rng(seed+i*17)
        col,h=_PAINTERS[name](2*C,rng)
        h01=np.clip(h,0,1).astype(f32)
        col,_=paint_form_light(np.clip(col,0,1).astype(f32),h01,depth,tile/2,hig=0.1,log=0.16,post=0.0,ex=1.5)
        r0,c0=(i//4)*C,(i%4)*C
        BC[r0:r0+C,c0:c0+C]=down2(np.clip(col,0,1).astype(f32)); H[r0:r0+C,c0:c0+C]=down2(h01)
        R[r0:r0+C,c0:c0+C]=GOODS_ROUGH[name]*(1+0.06*down2(fbm(2*C,2.0,seed+i,fmin=4,fmax=60)))
    R=np.clip(R,0.05,1).astype(f32)
    ao=cavity_ao(H,radii=(2,5,12),k=(1.6,1.0,0.5),floor=0.55)
    if write:
        write_set(out_prefix,BC,H,R,depth,tile,ao=ao,ao_in_albedo=0.35); PBR_SETS[out_prefix]=dict(depth=depth,tile=tile)
        m=bpy.data.materials.get("M_VK_Goods") or bpy.data.materials.new("M_VK_Goods")
        if "pbr_material" in globals(): pbr_material(m,out_prefix,nstr=0.6,spec=0.3)
    return BC
