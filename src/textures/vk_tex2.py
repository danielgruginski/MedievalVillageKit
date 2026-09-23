# ===================== STONE v2 : coursed rubble (spec_stone.md) =====================
import json
STONE_PAL=dict(S1="#9B9384",S2="#B0A792",S3="#8E8F91",S4="#A99682",S5="#9D8A86",S6="#74767A")
STONE_SHARE=dict(S1=0.38,S2=0.16,S3=0.20,S4=0.12,S5=0.06,S6=0.08)
ST_HI,ST_SH,ST_MO="#F4E9CC","#3E3A4C","#6E6557"
LICHEN_C=("#A9B38C","#C8963E","#DAD5BD"); MOSS_C=("#3A5226","#5F7F34","#93AE52")
PAL_KEYS=list(STONE_PAL.keys())
def _luma3(c): return float(0.2126*c[0]+0.7152*c[1]+0.0722*c[2])
HUEMIX=0.35
def _pal(k):
    c=hx(STONE_PAL[k]); b=hx(STONE_PAL['S1']); return (c+(b*_luma3(c)/_luma3(b)-c)*HUEMIX).astype(f32)
def _stone_rgb(pid,val,warm): return _pal(PAL_KEYS[pid])*val*np.array([1+0.02*warm,1,1-0.025*warm],f32)

def _course_label(c,x,y,yc,T):
    s=wrapd(x[:,None]-c['J'][None,:]-c['t'][None,:]*(y[:,None]-yc),T)
    sp=np.where(s>=0,s,np.inf); return sp.argmin(1)

def stone_layout(seed,T=3.0,lacing=True,NC=7):
    rng=np.random.default_rng(seed)
    for _outer in range(20):
        H=rng.uniform(0.34,0.54,NC)
        nL=int(rng.choice([3,4])) if lacing else -1
        if lacing:
            H[nL]=rng.uniform(0.20,0.24); o=[i for i in range(NC) if i!=nL]; H[o]*=(T-H[nL])/H[o].sum()
        else: H*=T/H.sum()
        y0=np.concatenate([[0.0],np.cumsum(H)]); y0[-1]=T; yc=(y0[:-1]+y0[1:])/2
        beds=[]
        for r in range(NC):
            xp=np.sort(((np.arange(5)+rng.uniform(-0.2,0.2,5))*T/5)%T); a=0.008 if r==0 else 0.025
            beds.append((xp,rng.uniform(-a,a,5)))
        xs=np.arange(512)*T/512
        B=np.stack([y0[r]+np.interp(xs,beds[r][0],beds[r][1],period=T) for r in range(NC)]+[y0[0]+np.interp(xs,beds[0][0],beds[0][1],period=T)+T])
        if any((B[r+1]-B[r]).min()<0.7*H[r] for r in range(NC)): continue
        courses=[]; ok=True; min_stag=9.0
        for r in range(NC):
            lac=(r==nL); med=3.0*H[r] if lac else 1.45*H[r]
            lo,hi=(0.45,1.20) if lac else (max(0.28,0.75*H[r]),min(1.20,2.6*H[r]))
            tmax=0.15 if lac else 0.30; best=None
            for attempt in range(60):
                ws=[]
                while sum(ws)<T: ws.append(float(np.clip(rng.lognormal(math.log(med),0.30),lo,hi)))
                ws=np.array(ws)*T/sum(ws)
                if ws.min()<0.25 or ws.max()>1.30 or len(ws)<3: continue
                t=rng.uniform(-tmax,tmax,len(ws)); rel=np.concatenate([[0.0],np.cumsum(ws)[:-1]])
                X0=np.linspace(0,T,180,endpoint=False)+rng.uniform(0,T/180)
                J=(X0[:,None]+rel[None,:])%T; score=np.full(len(X0),9.0)
                if r>0:
                    pr=courses[r-1]; jb=J+t[None,:]*(y0[r]-yc[r]); pb=pr['J']+pr['t']*(y0[r]-yc[r-1])
                    score=np.minimum(score,np.abs(wrapd(jb[:,:,None]-pb[None,None,:],T)).min(axis=(1,2)))
                if r==NC-1:
                    c0=courses[0]; jt=J+t[None,:]*(T-yc[r]); p0=c0['J']+c0['t']*(0-yc[0])
                    score=np.minimum(score,np.abs(wrapd(jt[:,:,None]-p0[None,None,:],T)).min(axis=(1,2)))
                good=np.where(score>=0.12)[0]
                i=int(rng.choice(good)) if len(good) else int(np.argmax(score))
                if best is None or score[i]>best[0]: best=(score[i],J[i],t,ws)
                if best[0]>=0.12: break
            if best is None or best[0]<0.09: ok=False; break
            sc,J,t,ws=best; min_stag=min(min_stag,sc)
            o=np.argsort(J); courses.append(dict(J=J[o].astype(f32),t=t[o].astype(f32),w=ws[o].astype(f32),H=float(H[r]),lac=lac))
        if ok: break
    # ---- stones list ----
    stones=[]; base=[]
    for r,c in enumerate(courses):
        base.append(len(stones))
        for k in range(len(c['J'])):
            stones.append(dict(r=r,k=k,w=float(c['w'][k]),H=float(H[r]),cx=float((c['J'][k]+c['w'][k]/2)%T),cy=float(yc[r]),lac=c['lac']))
    N=len(stones)
    # ---- adjacency (design values, with wrap) ----
    adj=[set() for _ in range(N)]
    for r,c in enumerate(courses):
        n=len(c['J'])
        for k in range(n): a=base[r]+k; b=base[r]+(k+1)%n; adj[a].add(b); adj[b].add(a)
    xsamp=(np.arange(900)+0.5)*T/900
    for r in range(NC):
        rl=(r-1)%NC; ybed=y0[r]
        up=_course_label(courses[r],xsamp,np.full_like(xsamp,ybed),yc[r],T)+base[r]
        ylow=ybed if r>0 else T
        lw=_course_label(courses[rl],xsamp,np.full_like(xsamp,ylow),yc[rl],T)+base[rl]
        for a,b in set(zip(up.tolist(),lw.tolist())): adj[a].add(b); adj[b].add(a)
    # ---- per-stone random params ----
    for s in stones:
        w,Hh=s['w'],s['H']; m=min(w,Hh)
        s['k']=rng.uniform(0.012,0.035)
        cors=[]
        for ci in range(4):
            en=rng.random()<0.5; a,b,cc=rng.uniform(0.6,1.4),rng.uniform(0.6,1.4),rng.uniform(0.03,0.10)
            lim=0.3*m; cc=min(cc,lim*a,lim*b)
            cors.append([en,a,b,cc])
        s['corners']=cors
        nb=rng.choice([0,1,2],p=[0.4,0.4,0.2]); bites=[]
        for _ in range(nb):
            u=rng.random()
            if u<0.65:
                e=0; al=rng.uniform(-0.5,0.5)*w if rng.random()<0.6 else rng.choice([-1,1])*rng.uniform(0.38,0.5)*w
            else:
                e=int(rng.choice([1,2,3])); al=rng.uniform(-0.45,0.45)*(w if e==1 else Hh)
            bites.append([e,al,rng.uniform(0.0075,0.0175),rng.uniform(0.005,0.01)])
        s['bites']=bites
        s['p']=rng.uniform(0.028,0.036); s['tx'],s['ty']=rng.uniform(-0.035,0.035,2)
        th=np.radians(90*np.arange(4)+rng.uniform(-35,35,4)); sk=rng.uniform(0.08,0.15,4); ak=rng.uniform(0.3,0.7,4); fs=rng.uniform(-1,1,4)
        s['fac']=np.stack([th,sk,ak,fs],1)
        s['rb']=float(np.clip(0.12*m,0.03,0.06)); s['inr']=0.5*m-0.0085
        nc=rng.choice([0,1,2],p=[0.4,0.45,0.15]); chips=[]
        for _ in range(nc):
            e=0 if rng.random()<0.6 else int(rng.choice([2,3]))
            al=rng.uniform(-0.45,0.45)*(w if e==0 else Hh); chips.append([e,al,rng.uniform(0.02,0.045)])
        s['chips']=chips; s['crack']=bool(rng.random()<1/6)
    # ---- packers ----
    packers=[]
    for i,s in enumerate(stones):
        for ci,(en,a,b,cc) in enumerate(s['corners']):
            if not en: continue
            l1,l2=cc/a,cc/b
            if l1<0.06 or l2<0.06 or rng.random()>=0.25: continue
            # approx corner world pos
            px_=s['cx']+(-0.5 if ci in (0,2) else 0.5)*s['w']; py_=s['cy']+(-0.5 if ci in (0,1) else 0.5)*s['H']
            if any(math.hypot(wrapd(px_-q['x'],T),wrapd(py_-q['y'],T))<0.10 for q in packers): continue
            rx=0.45*min(l1,l2)
            packers.append(dict(parent=i,ci=ci,a=a,b=b,c=cc,rx=rx,ry=0.75*rx,x=px_,y=py_,p=rng.uniform(0.018,0.022),
                                pid=5 if rng.random()<0.5 else 2))
    # ---- colour assignment ----
    samp=[]; keys=PAL_KEYS; shares=np.array([STONE_SHARE[k] for k in keys])
    r2=np.random.default_rng(seed+999)
    for _ in range(4000):
        pid=r2.choice(6,p=shares); samp.append(_luma3(_stone_rgb(pid,r2.uniform(0.93,1.06),r2.uniform(-1,1))))
    lm,ls=float(np.mean(samp)),float(np.std(samp))
    order=rng.permutation(N); viol=0
    for i in order:
        s=stones[i]; bestc=None
        for tr in range(50):
            if s['lac'] and rng.random()<0.6: pid=5
            else: pid=int(rng.choice(6,p=shares))
            val=rng.uniform(0.93,1.06); warm=rng.uniform(-1,1); l=_luma3(_stone_rgb(pid,val,warm))
            bad=0
            if abs(l-lm)>1.8*ls: bad+=1
            for j in adj[i]:
                q=stones[j]
                if 'pid' not in q: continue
                if pid in (3,4,5) and q['pid']==pid: bad+=2
                if abs(l-q['luma'])<0.04*max(l,q['luma']): bad+=1
            if bestc is None or bad<bestc[0]: bestc=(bad,pid,val,warm,l)
            if bad==0: break
        viol+=bestc[0]; s['pid'],s['val'],s['warm'],s['luma']=bestc[1],bestc[2],bestc[3],bestc[4]
    areas=np.array([s['w']*s['H'] for s in stones])
    return dict(seed=seed,T=T,H=H,y0=y0,yc=yc,beds=beds,courses=courses,stones=stones,base=base,N=N,adj=adj,
                packers=packers,nL=nL,viol=viol,min_stag=min_stag,area_ratio=float(areas.max()/np.median(areas)),
                wmin=float(min(s['w'] for s in stones)),wmax=float(max(s['w'] for s in stones)))

def stone_layout_score(L):
    ok=30<=L['N']<=36 and 6<=len(L['packers'])<=10 and L['area_ratio']<=2.5 and L['viol']==0 and L['wmin']>=0.25 and L['wmax']<=1.30
    return ok, abs(L['N']-33)+abs(len(L['packers'])-8)*0.5+L['area_ratio']

def gen_stone(S=2048,seed=9,T=3.0,depth=0.06,lacing=True,L=None,out_prefix="T_VK_Stone",write=True,GAP=0.0095,GRAIN=0.00035,PITS=0.001,HIG=0.22):
    import time; t0=time.time()
    if L is None: L=stone_layout(seed,T,lacing)
    rng=np.random.default_rng(seed+500)
    stones,packers,courses=L['stones'],L['packers'],L['courses']; N=L['N']; P=len(packers); NS=N+P
    y0,yc=L['y0'],L['yc']; px=T/S
    x,y=grid(S); X=(x*T).astype(f32); Y=(T*(1-y)).astype(f32); del x,y
    xs=(np.arange(S)*T/S).astype(f32)
    B=np.stack([y0[r]+np.interp(xs,L['beds'][r][0],L['beds'][r][1],period=T) for r in range(7)]+
               [y0[0]+np.interp(xs,L['beds'][0][0],L['beds'][0][1],period=T)+T]).astype(f32)
    B0=B[0][None,:]; Yw=(B0+(Y-B0)%T).astype(f32)
    R=np.zeros((S,S),np.int32)
    for j in range(1,7): R+=(Yw>=B[j][None,:])
    cols=np.broadcast_to(np.arange(S)[None,:],(S,S))
    dB=(Yw-B[R,cols]-0.0025).astype(f32); dT=(B[R+1,cols]-Yw-0.0025).astype(f32)
    lab=np.zeros((S,S),np.int32); dL=np.zeros((S,S),f32); dR=np.zeros((S,S),f32); lx=np.zeros((S,S),f32); ly=np.zeros((S,S),f32)
    for r,c in enumerate(courses):
        m=R==r; Xm=X[m]; Ym=Yw[m]
        s=(wrapd(Xm[:,None]-c['J'][None,:]-c['t'][None,:]*(Ym[:,None]-yc[r]),T)/np.sqrt(1+c['t']**2)[None,:]).astype(f32)
        sp=np.where(s>=0,s,np.inf); kL=sp.argmin(1); dL[m]=sp.min(1)
        dR[m]=np.where(s<0,-s,np.inf).min(1)
        lab[m]=L['base'][r]+kL
        cx=(c['J'][kL]+c['w'][kL]/2)%T; lx[m]=wrapd(Xm-cx,T); ly[m]=Ym-yc[r]
        del s,sp
    # per-stone arrays (NS)
    def arr(fn,dflt=0.0):
        a=np.full(NS,dflt,f32)
        for i,s in enumerate(stones): a[i]=fn(s)
        return a
    kk=arr(lambda s:s['k']); kk[N:]=0.004
    # silhouette
    k=kk[lab]
    d=smin(smin(smin(dB,dT,k),dL,k),dR,k)
    cA=np.zeros((NS,4),f32); cB=np.ones((NS,4),f32); cC=np.zeros((NS,4),f32); cE=np.zeros((NS,4),bool)
    for i,s in enumerate(stones):
        for ci,(en,a,b,cc) in enumerate(s['corners']): cE[i,ci]=en; cA[i,ci]=a; cB[i,ci]=b; cC[i,ci]=cc
    pairs=((dL,dB),(dR,dB),(dL,dT),(dR,dT))
    for ci,(d1,d2) in enumerate(pairs):
        a=cA[lab,ci]; b=cB[lab,ci]; cc=cC[lab,ci]
        dC=np.where(cE[lab,ci],(a*d1+b*d2-cc)/np.sqrt(a*a+b*b+1e-9),9.0).astype(f32)
        d=smin(d,dC,k)
    d=(d+0.002*fbm(S,2.0,seed+3,fmin=10,fmax=40)).astype(f32)
    g=np.clip(GAP+0.0025*fbm(S,2.0,seed+4,fmin=6,fmax=30),0.005,0.013).astype(f32)
    # bites (max 2 per stone)
    for bi in range(2):
        be=np.full(NS,-1,np.int32); ba=np.zeros(NS,f32); bra=np.ones(NS,f32); brb=np.ones(NS,f32)
        for i,s in enumerate(stones):
            if len(s['bites'])>bi: e,al,ra,rb_=s['bites'][bi]; be[i]=e; ba[i]=al; bra[i]=ra; brb[i]=rb_
        E=be[lab]
        if (E<0).all(): continue
        along=np.where(E<=1,lx,ly); across=np.select([E==0,E==1,E==2],[dT,dB,dL],dR)-g
        esd=(np.sqrt(((along-ba[lab])/bra[lab])**2+(across/brb[lab])**2)-1)*np.minimum(bra[lab],brb[lab])
        d=np.where(E>=0,np.minimum(d,g+esd),d).astype(f32)
    # packers
    plx=lx.copy(); ply=ly.copy()
    for pi,q in enumerate(packers):
        m=lab==q['parent']; d1,d2=pairs[q['ci']]
        e1=d1[m]-q['c']/(3*q['a']); e2=d2[m]-q['c']/(3*q['b'])
        dp_=-(np.sqrt((e1/q['rx'])**2+(e2/q['ry'])**2)-1)*q['ry']
        take=dp_>d[m]
        idx=np.where(m)[0] if False else None
        sub=d[m]; sub[take]=dp_[take]; d[m]=sub
        sl=lab[m]; sl[take]=N+pi; lab[m]=sl
        sx=plx[m]; sx[take]=e1[take]; plx[m]=sx
        sy=ply[m]; sy[take]=e2[take]; ply[m]=sy
    lx,ly=plx,ply; del plx,ply
    dp=(d-g).astype(f32); stone=smooth(-0.0012,0.0012,dp)
    ispk=lab>=N
    # ---- height ----
    pp=arr(lambda s:s['p']); txa=arr(lambda s:s['tx']); tya=arr(lambda s:s['ty'])
    rb=arr(lambda s:s['rb']); inr=arr(lambda s:s['inr'])
    ww=arr(lambda s:s['w']); HH=arr(lambda s:s['H'])
    for pi,q in enumerate(packers):
        pp[N+pi]=q['p']; rb[N+pi]=0.5*q['ry']; inr[N+pi]=0.5*q['ry']; ww[N+pi]=2*q['rx']; HH[N+pi]=2*q['ry']
    FAC=np.zeros((NS,4,4),f32)
    for i,s in enumerate(stones): FAC[i]=s['fac']
    hm=(0.004+0.003*smooth(-0.006,0,dp)+0.0006*fbm(S,1.2,seed+6,fmin=120)).astype(f32)
    facet=np.zeros((S,S),f32); kst=np.zeros((S,S),np.int8); best=np.full((S,S),np.inf,f32)
    for kq in range(4):
        th=FAC[lab,kq,0]; sk=FAC[lab,kq,1]; ak=FAC[lab,kq,2]
        Rk=0.5*(np.abs(np.cos(th))*ww[lab]+np.abs(np.sin(th))*HH[lab])
        v=sk*(ak*Rk-(lx*np.cos(th)+ly*np.sin(th)))
        v=np.where(ispk,np.inf,v).astype(f32)
        mm=v<best; best=np.where(mm,v,best); kst[mm]=kq
    facet=np.minimum(0,np.where(np.isinf(best),0,best)).astype(f32); del best
    fs_act=np.where(facet<-0.002,np.take_along_axis(FAC[lab,:,3],kst[...,None].astype(np.int64),-1)[...,0],0).astype(f32)
    gp=(GRAIN*fbm(S,1.8,seed+13,fmin=60,fmax=300)-PITS*smooth(2.5,2.9,fbm(S,2.0,seed+14,fmin=40,fmax=200))).astype(f32)
    hface=(pp[lab]+txa[lab]*lx+tya[lab]*ly+facet+0.006*smooth(0,0.85*np.maximum(inr[lab],0.005),dp)**0.7+gp).astype(f32)
    hface=np.maximum(hface,hm+0.012)
    sb=np.clip(dp/rb[lab],0,1); prof=1-(1-sb)**2
    h_st=(hm+(hface-hm)*prof).astype(f32); gp=(gp*prof*(dp>0)).astype(f32); del hface,sb,prof
    # chips
    chip=np.zeros((S,S),f32)
    for ci in range(2):
        ce=np.full(NS,-1,np.int32); ca=np.zeros(NS,f32); cr=np.ones(NS,f32)
        for i,s in enumerate(stones):
            if len(s['chips'])>ci: e,al,rr=s['chips'][ci]; ce[i]=e; ca[i]=al; cr[i]=rr
        E=ce[lab]
        if (E<0).all(): continue
        along=np.where(E==0,lx,ly); across=np.select([E==0,E==2],[dT,dL],dR)-g
        rr=np.sqrt((along-ca[lab])**2+across**2); disc=(1-smooth(cr[lab]-0.003,cr[lab],rr))*(E>=0)*(1-ispk)
        plane=hm+0.006+0.577*dp
        cut=disc*smooth(0.0,0.0015,h_st-plane)
        h_st=np.where(disc>0,lerp(h_st,np.minimum(h_st,plane),disc),h_st).astype(f32)
        chip=np.maximum(chip,cut*(dp>0))
    # cracks
    starts=[]; cracked=[]
    for i,s in enumerate(stones):
        if not s['crack']: continue
        cracked.append(i); r=s['r']; e=rng.integers(0,3)
        if e==0:   wx=s['cx']+rng.uniform(-0.3,0.3)*s['w']; wy=y0[r+1]-0.0025-0.0085-0.01; a=math.pi/2
        elif e==1: wx=s['cx']-0.5*s['w']+0.02; wy=s['cy']+rng.uniform(-0.3,0.3)*s['H']; a=0.0
        else:      wx=s['cx']+0.5*s['w']-0.02; wy=s['cy']+rng.uniform(-0.3,0.3)*s['H']; a=math.pi
        a+=math.radians(rng.uniform(-30,30)); stepm=11.5*px
        n=max(3,int(0.6*s['w']/stepm*rng.uniform(0.45,0.9)))
        starts.append(((wx%T)/T*S,(1-(wy%T)/T)*S,a,n))
    crack=np.zeros((S,S),f32)
    if starts:
        segs=crack_segments(S,rng,starts=starts,step_px=(8,15),w0=3.0,branch=0.07,jit=0.45)
        crack=draw_segments(S,segs)*(stone>0.5)*np.isin(lab,cracked)
    h_st-=0.012*crack
    h=np.where(dp>0,h_st,hm).astype(f32); del h_st
    # ---- colour ----
    PAL=np.stack([_pal(kq) for kq in PAL_KEYS])
    pid=np.zeros(NS,np.int32); val=np.ones(NS,f32); warm=np.zeros(NS,f32)
    for i,s in enumerate(stones): pid[i]=s['pid']; val[i]=s['val']; warm[i]=s['warm']
    for pi,q in enumerate(packers): pid[N+pi]=q['pid']; val[N+pi]=rng.uniform(0.9,1.0); warm[N+pi]=rng.uniform(-1,1)
    wm=np.stack([1+0.02*warm,np.ones(NS,f32),1-0.025*warm],1)
    stone_rgb=PAL[pid]*val[:,None]*wm
    col=stone_rgb[lab].astype(f32)                                             # 1 local colour
    col*=(1+0.035*fs_act)[...,None]                                            # 2 facet tint
    vloc=np.clip(dB/np.maximum(dB+dT,1e-4),0,1).astype(f32)
    col*=(0.94+0.09*vloc)[...,None]                                            # 3 per-stone gradient
    for j,ang in enumerate((0.35,1.40,2.44)):                                  # 4 strokes
        st=fbm(S,2.2,seed+40+j,fmin=12,fmax=70,ax=2.5,angle=ang)
        col*=np.where(lab%3==j,1+0.018*st,1.0)[...,None]
    mort=hx(ST_MO)*(1+0.05*fbm(S,1.5,seed+15,fmin=20,fmax=150))[...,None]      # 5 mortar
    ledge=((1-stone)*np.roll(stone,-8,0)).astype(f32)
    mort=mort*(1+0.06*ledge)[...,None]
    col=lerp(mort,col,stone[...,None]).astype(f32); del mort
    h01=np.clip(h/0.06,0,1).astype(f32)
    Ln=np.array([-0.12,0.80,0.58],f32); Ln/=np.linalg.norm(Ln)                 # 6 form light
    n_s=normal_from_height(blur(np.clip((h-gp)/0.06,0,1),4.0),0.06*2.0,T)
    s_=painted_light(n_s,Ln)-Ln[2]
    q=s_/0.10; s_=lerp(s_,(np.floor(q)+smooth(0.3,0.7,q-np.floor(q)))*0.10,0.35)
    HI=hx(ST_HI); SH=hx(ST_SH)
    hi=np.clip(s_/0.35,0,1)[...,None]; col=lerp(col*(1+HIG*hi),HI,0.18*hi)
    lo=np.clip(-s_/0.45,0,1)[...,None]; col=lerp(col*(1-0.30*lo),SH,0.28*lo)
    band=(smooth(0,0.004,dp)-smooth(0.012,0.024,dp)).astype(f32)                # 7 top rim
    rim=(band*smooth(0.20,0.50,n_s[...,1])).astype(f32)
    col=lerp(col*(1+0.10*rim[...,None]),HI,0.40*rim[...,None])
    under=(band*smooth(0.15,0.45,-n_s[...,1]))[...,None]                        # 8 underside
    col=lerp(col*(1-0.20*under),SH,0.25*under)
    occ=np.zeros((S,S),f32)                                                    # 9 cast shadow
    for kq in range(1,21): occ=np.maximum(occ,np.roll(h,(kq,int(round(0.15*kq))),(0,1))-h-kq*px*1.43)
    sh=blur(smooth(0,0.004,occ),1.2)[...,None]; del occ
    col=lerp(col*(1-0.45*sh),SH,0.30*sh)
    lc=luma(col)[...,None]                                                      # 10 chips
    col=lerp(col,lerp(col,lc,0.5)*1.12,0.7*chip[...,None])
    line=np.clip(np.roll(chip,2,0)-chip,0,1)[...,None]; col=lerp(col,SH,0.5*line)
    cr3=crack[...,None]                                                         # 11 cracks
    col=lerp(col,lerp(col*0.5,SH,0.4),cr3); col*=1+0.08*np.roll(cr3,3,0)*(1-cr3)
    # 12 lichen
    lich=[np.zeros((S,S),f32) for _ in range(3)]
    ncol=rng.integers(3,6); stone_area=float((stone>0.5).mean())
    for _ in range(ncol):
        for tries in range(30):
            cxp,cyp=rng.uniform(0,S),rng.uniform(0,S); ix,iy=int(cxp)%S,int(cyp)%S
            if stone[iy,ix]>0.5 and vloc[iy,ix]>0.5 and not ispk[iy,ix]: break
        patch=rng.uniform(0.06,0.12)/px*0.5; segs=[[],[],[]]
        for _d in range(rng.integers(8,26)):
            rr=rng.uniform(0.004,0.012)/px; ang=rng.uniform(0,2*math.pi); dd=patch*math.sqrt(rng.random())
            xx_,yy_=cxp+math.cos(ang)*dd,cyp+math.sin(ang)*dd*0.6
            ci=rng.choice(3,p=[0.6,0.3,0.1]); segs[ci].append((xx_,yy_,xx_+0.01,yy_,2*rr))
        for ci in range(3):
            if segs[ci]: lich[ci]=np.maximum(lich[ci],draw_segments(S,segs[ci]))
    gate=((stone>0.5)&(vloc>0.4)).astype(f32)
    lichen=np.zeros((S,S),f32)
    for ci in range(3):
        a=lich[ci]*gate*0.85; lichen=np.maximum(lichen,a)
        col=lerp(col,hx(LICHEN_C[ci])*(1+0.06*blur(fbm(S,1.5,seed+60+ci,fmin=60),0.5))[...,None],a[...,None])
    del lich
    # 13 ledge moss
    mf1=fbm(S,3.0,seed+30,fmin=2,fmax=12); mf2=smooth(-0.3,0.5,fbm(S,1.8,seed+31,fmin=10,fmax=60))
    mbase=mf2*np.maximum(ledge,0.6*rim)
    thr=0.8
    for _ in range(12):
        moss=smooth(thr,thr+0.8,mf1)*mbase; cov=float((moss>0.5).mean())
        if cov>0.025: thr+=0.12
        elif cov<0.015: thr-=0.12
        else: break
    moss=moss.astype(f32)
    mt=fbm(S,1.6,seed+32,fmin=60)*0.5+0.5
    mc=ramp3(mt,hx(MOSS_C[0]),hx(MOSS_C[1]),hx(MOSS_C[2]))
    col=lerp(col,mc,np.clip(moss*1.2,0,1)[...,None]); del mc
    col*=(1+0.03*fbm(S,2.0,seed+50,fmin=1.5,fmax=5))[...,None]                 # 14 macro breakup
    h=h+0.001*lichen+0.003*moss
    h01=blur(np.clip(h/0.06,0,1),1.0)
    Rgh=np.clip(0.82+0.03*fs_act-0.06*rim-0.08*chip+0.11*(1-stone)+0.04*lichen+0.10*moss,0.60,0.97).astype(f32)
    col=np.clip(col,0,1).astype(f32)
    stats=dict(t_layout_to_paint=time.time()-t0)
    bc,h1,R1=down2(col),down2(h01),down2(Rgh); st1=down2(stone)
    lab1=lab[::2,::2]
    ao=cavity_ao(h1,radii=(3,10,30),k=(2.0,1.5,0.9),floor=0.40)
    if write:
        write_set(out_prefix,bc,h1,R1,0.06,T,ao=ao,ao_in_albedo=0.30)
        PBR_SETS[out_prefix]=dict(depth=0.06,tile=T)
        meta=[dict(u=s['cx']/T,v=s['cy']/T,w=s['w'],h=s['H'],lab=i) for i,s in enumerate(stones) if s['w']*s['H']>0.25]
        with open(os.path.join(TEXDIR,out_prefix+"_stones.json"),"w") as f: json.dump(meta,f)
    stats['time']=time.time()-t0
    return dict(bc=bc*(0.70+0.30*ao)[...,None],h=h1,R=R1,stone=st1,lab=lab1,ao=ao,moss=float((moss>0.5).mean()),stats=stats,L=L)


def lichen_dots(S,rng,px,gate_fn,ncol,colors=LICHEN_C,probs=(0.6,0.3,0.1)):
    lich=[np.zeros((S,S),f32) for _ in range(3)]
    for _ in range(ncol):
        for tries in range(40):
            cxp,cyp=rng.uniform(0,S),rng.uniform(0,S)
            if gate_fn(int(cyp)%S,int(cxp)%S): break
        patch=rng.uniform(0.06,0.12)/px*0.5; segs=[[],[],[]]
        for _d in range(rng.integers(8,26)):
            rr=rng.uniform(0.004,0.012)/px; ang=rng.uniform(0,2*math.pi); dd=patch*math.sqrt(rng.random())
            xx_,yy_=cxp+math.cos(ang)*dd,cyp+math.sin(ang)*dd*0.6
            ci=rng.choice(3,p=list(probs)); segs[ci].append((xx_,yy_,xx_+0.01,yy_,2*rr))
        for ci in range(3):
            if segs[ci]: lich[ci]=np.maximum(lich[ci],draw_segments(S,segs[ci]))
    return lich

def paint_form_light(col,h01,depth,T,hig=0.22,log=0.30,post=0.35,ex=2.0):
    Ln=np.array([-0.12,0.80,0.58],f32); Ln/=np.linalg.norm(Ln)
    n_s=normal_from_height(blur(h01,4.0),depth*ex,T)
    s_=painted_light(n_s,Ln)-Ln[2]
    q=s_/0.10; s_=lerp(s_,(np.floor(q)+smooth(0.3,0.7,q-np.floor(q)))*0.10,post)
    HI=hx(ST_HI); SH=hx(ST_SH)
    hi=np.clip(s_/0.35,0,1)[...,None]; col=lerp(col*(1+hig*hi),HI,0.18*hi)
    lo=np.clip(-s_/0.45,0,1)[...,None]; col=lerp(col*(1-log*lo),SH,0.28*lo)
    return col.astype(f32),n_s

def gen_stoneblock(S=2048,seed=17,T=1.2,depth=0.05,out_prefix="T_VK_StoneBlock",write=True):
    rng=np.random.default_rng(seed); px=T/S
    pts=[]
    for j in range(3):
        for i in range(3):
            pts.append(((i+0.5+rng.uniform(-0.3,0.3)+0.5*(j%2))/3,(j+0.5+rng.uniform(-0.3,0.3))/3))
    pts=np.array(pts,f32)%1; n=len(pts)
    x,y=grid(S)
    off=rng.uniform(-0.002,0.002,n).astype(f32); sl=rng.uniform(0.015,0.035,n).astype(f32); th=rng.uniform(0,2*math.pi,n)
    tau=0.006
    Dmin=np.full((S,S),np.inf,f32); ID1=np.zeros((S,S),np.int32)
    for i,(cx_,cy_) in enumerate(pts):
        dx=wrapd(x-cx_)*T; dy=wrapd(y-cy_)*T; D=dx*dx+dy*dy; m=D<Dmin; Dmin=np.where(m,D,Dmin); ID1[m]=i
    num=np.zeros((S,S),f32); den=np.zeros((S,S),f32); wmax=np.zeros((S,S),f32)
    for i,(cx_,cy_) in enumerate(pts):
        dx=wrapd(x-cx_)*T; dy=wrapd(y-cy_)*T; w=np.exp(-(dx*dx+dy*dy-Dmin)/tau).astype(f32)
        num+=w*(off[i]+sl[i]*(dx*math.cos(th[i])+dy*math.sin(th[i]))); den+=w; wmax=np.maximum(wmax,w)
    h=(num/den).astype(f32); crease=(1-wmax/den).astype(f32); del num,den
    pits=smooth(2.2,2.7,fbm(S,1.5,seed+9,fmin=60,fmax=400)).astype(f32)
    grain=(0.00015*fbm(S,1.8,seed+2,fmin=60,fmax=300)-0.0008*pits).astype(f32)
    segs=crack_segments(S,rng,n=1,steps=(30,55),step_px=(8,14),w0=2.2,branch=0.12,jit=0.45)
    crack=draw_segments(S,segs); h=h-0.004*crack
    h01=np.clip(0.5+h/depth,0,1).astype(f32)
    h01g=np.clip(0.5+(h+grain)/depth,0,1).astype(f32)
    fval=rng.uniform(-1,1,n).astype(f32)
    t_=smooth(-0.6,0.6,fbm(S,2.5,seed+1,fmin=1.5,fmax=6))[...,None]
    col=lerp(_pal('S1')*0.93,_pal('S2')*0.90,t_)*(1+0.04*fval[ID1])[...,None]*(1+0.045*fbm(S,1.0,seed+8,fmin=80,fmax=500))[...,None]*(1-0.22*pits)[...,None]
    col*=(1+0.02*fbm(S,2.2,seed+5,fmin=12,fmax=70,ax=2.5,angle=0.4))[...,None]
    col,n_s=paint_form_light(col.astype(f32),h01,depth,T,hig=0.12,log=0.16,post=0.2,ex=1.0)
    col*=(1-0.05*smooth(0.3,0.5,crease))[...,None]
    SH=hx(ST_SH); cr3=crack[...,None]
    col=lerp(col,lerp(col*0.5,SH,0.4),cr3); col*=1+0.08*np.roll(cr3,3,0)*(1-cr3)
    lich=lichen_dots(S,rng,px,lambda r,c:True,int(rng.integers(1,3)))
    lichen=np.zeros((S,S),f32)
    for ci in range(3):
        a=lich[ci]*0.85; lichen=np.maximum(lichen,a)
        col=lerp(col,hx(LICHEN_C[ci]),a[...,None])
    col*=(1+0.03*fbm(S,2.0,seed+50,fmin=1.5,fmax=5))[...,None]
    h01=np.clip(h01g+lichen*0.001/depth,0,1)
    R=np.clip(0.86+0.03*fbm(S,2.0,seed+7,fmin=4,fmax=60)+0.04*lichen,0.6,0.97).astype(f32)
    bc,h1,R1=down2(np.clip(col,0,1)),down2(h01),down2(R)
    ao=cavity_ao(h1,radii=(3,10,30),k=(2.0,1.5,0.9),floor=0.5)
    if write:
        write_set(out_prefix,bc,h1,R1,depth,T,ao=ao,ao_in_albedo=0.25); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return dict(bc=bc*(0.75+0.25*ao)[...,None],h=h1)


# ===================== FIELD STONE (rural dry-stone / rough rubble) =====================
FIELD_PAL=dict(S1=0.30,S4=0.25,BR=0.15,S3=0.15,S2=0.10,S6=0.05)
def _fpal(k):
    if k=="BR":
        c=hx("#85766A"); b=hx(STONE_PAL['S1']); return (c+(b*_luma3(c)/_luma3(b)-c)*HUEMIX).astype(f32)
    return _pal(k)
def voronoi_edge2(x,y,pts,w=None,sx=1.0,sy=1.0):
    """like voronoi_edge but also returns the 2nd-nearest border distance (for rounded corners)"""
    pts=np.asarray(pts,f32); N=len(pts); w=np.zeros(N,f32) if w is None else np.asarray(w,f32)
    P1=np.full(x.shape,np.inf,f32); ID1=np.zeros(x.shape,np.int32)
    for i,(px_,py_) in enumerate(pts):
        dx=wrapd(x-px_)*sx; dy=wrapd(y-py_)*sy; P=dx*dx+dy*dy-w[i]
        m=P<P1; P1=np.where(m,P,P1); ID1[m]=i
    ax,ay=pts[ID1,0],pts[ID1,1]; ox,oy=wrapd(x-ax),wrapd(y-ay)
    E1=np.full(x.shape,np.inf,f32); E2=np.full(x.shape,np.inf,f32)
    for j,(bx,by) in enumerate(pts):
        abx=wrapd(bx-ax)*sx; aby=wrapd(by-ay)*sy; L=np.hypot(abx,aby)+1e-9
        dbx=ox*sx-abx; dby=oy*sy-aby; Pb=dbx*dbx+dby*dby-w[j]
        e=((Pb-P1)/(2*L)/np.hypot(abx/L*sx,aby/L*sy)).astype(f32)
        e=np.where(ID1==j,np.inf,e)
        m1=e<E1; E2=np.where(m1,E1,np.minimum(E2,e)); E1=np.where(m1,e,E1)
    return ID1,E1,E2,ox.astype(f32),oy.astype(f32)

def fieldstone_seeds(seed,T=3.0):
    rng=np.random.default_rng(seed)
    rows=[]; s_=0
    while s_<T: p=rng.uniform(0.28,0.40); rows.append(p); s_+=p
    rows=np.array(rows)*T/s_; y0=np.concatenate([[0],np.cumsum(rows)])
    pts=[]
    for r in range(len(rows)):
        xs=[]; s_=0
        while s_<T: p=rng.uniform(0.35,0.65); xs.append(p); s_+=p
        xs=np.array(xs)*T/s_; xc=np.concatenate([[0],np.cumsum(xs)])[:-1]+xs/2+rng.uniform(0,T)
        for i,xx in enumerate(xc):
            pts.append(((xx+rng.uniform(-0.25,0.25)*xs[i])%T/T,((y0[r]+rows[r]/2+rng.uniform(-0.15,0.15)*rows[r])%T)/T))
    pts=np.array(pts,f32)
    s4=256; x,y=grid(s4); F1,F2,ID=voronoi(x,y,pts,1.0,1.35)
    n=len(pts); ang_x=2*np.pi*x; ang_y=2*np.pi*y
    cx=np.arctan2(np.bincount(ID.ravel(),np.sin(ang_x).ravel(),n),np.bincount(ID.ravel(),np.cos(ang_x).ravel(),n))/(2*np.pi)%1
    cy=np.arctan2(np.bincount(ID.ravel(),np.sin(ang_y).ravel(),n),np.bincount(ID.ravel(),np.cos(ang_y).ravel(),n))/(2*np.pi)%1
    pts=np.stack([cx,cy],1).astype(f32)
    F1,F2,ID=voronoi(x,y,pts,1.0,1.35)
    a=ID; b=np.roll(ID,-1,1); c=np.roll(ID,-1,0); d=np.roll(b,-1,0)
    trip=((a!=b)&(a!=c)&(b!=c))|((a!=b)&(a!=d)&(b!=d))
    ty,tx=np.nonzero(trip); cand=np.stack([(tx+1)/s4,(ty+1)/s4],1)
    rng.shuffle(cand); pk=[]
    for q in cand:
        if len(pk)>=int(0.12*n): break
        if all(math.hypot(wrapd(q[0]-p[0])*T,wrapd(q[1]-p[1])*T)>0.3 for p in pk): pk.append(q)
    w=np.concatenate([np.zeros(n,f32),np.full(len(pk),-(0.05/T)**2,f32)])
    return np.concatenate([pts,np.array(pk,f32).reshape(-1,2)]).astype(f32),w,n

def gen_fieldstone(S=2048,seed=31,T=3.0,depth=0.08,out_prefix="T_VK_FieldStone",write=True):
    rng=np.random.default_rng(seed+7); px=T/S
    pts,w,nmain=fieldstone_seeds(seed,T); N=len(pts)
    x,y=grid(S)
    ID,E1,E2,ox,oy=voronoi_edge2(x,y,pts,w,1.0,1.35)
    del x,y
    E1m=E1*T; E2m=E2*T
    kk=rng.uniform(0.02,0.05,N).astype(f32)
    d=smin(E1m,E2m,kk[ID])+0.004*fbm(S,2.0,seed+3,fmin=8,fmax=40)
    g=np.clip(0.012+0.005*fbm(S,2.0,seed+4,fmin=6,fmax=30),0.006,0.02).astype(f32)
    dp=(d-g).astype(f32); stone=smooth(-0.0015,0.0015,dp)
    area=np.bincount(ID.ravel(),minlength=N).astype(f32)*px*px
    rb=np.clip(0.4*np.sqrt(area/np.pi),0.04,0.09).astype(f32)
    prot=rng.uniform(0.035,0.050,N).astype(f32); prot[nmain:]=rng.uniform(0.022,0.03,N-nmain)
    tx_,ty_=rng.uniform(-0.04,0.04,(2,N)).astype(f32)
    lx=ox*T; ly=-oy*T
    th=np.radians(90*np.arange(4)[None,:]+rng.uniform(-35,35,(N,4))).astype(f32)
    sk=rng.uniform(0.04,0.08,(N,4)).astype(f32); ak=rng.uniform(0.35,0.75,(N,4)).astype(f32); fs=rng.uniform(-1,1,(N,4)).astype(f32)
    Rst=np.sqrt(area/np.pi).astype(f32)
    best=np.full((S,S),np.inf,f32); kst=np.zeros((S,S),np.int8)
    for q in range(4):
        v=sk[ID,q]*(ak[ID,q]*Rst[ID]-(lx*np.cos(th[ID,q])+ly*np.sin(th[ID,q])))
        m=v<best; best=np.where(m,v,best); kst[m]=q
    facet=np.minimum(0,best).astype(f32); del best
    fs_act=np.where(facet<-0.002,np.take_along_axis(fs[ID],kst[...,None].astype(np.int64),-1)[...,0],0).astype(f32)
    hm=(0.002+0.0012*fbm(S,1.5,seed+6,fmin=40)).astype(f32)
    gp=(0.0005*fbm(S,1.8,seed+13,fmin=60,fmax=300)).astype(f32)
    hface=np.maximum(prot[ID]+tx_[ID]*lx+ty_[ID]*ly+facet+0.008*smooth(0,0.1,dp)**0.7+gp,hm+0.015)
    sb=np.clip(dp/rb[ID],0,1); prof=1-(1-sb)**2
    h=np.where(dp>0,hm+(hface-hm)*prof,hm).astype(f32); gpp=(gp*prof*(dp>0)).astype(f32); del hface,prof,sb
    peb=np.zeros((S,S),f32); segs=[]
    gapy,gapx=np.nonzero((dp[::8,::8]<-0.004))
    sel=rng.choice(len(gapy),size=min(len(gapy),int(len(gapy)*0.02)),replace=False)
    for i in sel:
        r_=rng.uniform(0.004,0.0075)/px; cx_,cy_=gapx[i]*8+rng.uniform(0,8),gapy[i]*8+rng.uniform(0,8)
        segs.append((cx_,cy_,cx_+rng.uniform(-0.3,0.3)*r_,cy_+rng.uniform(-0.2,0.2)*r_,2*r_))
    if segs: peb=draw_segments(S,segs)*(1-stone)
    h=np.maximum(h,peb*(0.008-0.002*(1-blur(peb,2.0))))
    keys=list(FIELD_PAL.keys()); pr=np.array([FIELD_PAL[k_] for k_ in keys]); pr/=pr.sum()
    PAL=np.stack([_fpal(k_) for k_ in keys])
    pid=rng.choice(len(keys),N,p=pr)
    for i in range(nmain,N): pid[i]=keys.index("S6") if rng.random()<0.5 else keys.index("S3")
    val=rng.uniform(0.9,1.07,N).astype(f32); warm=rng.uniform(-1,1,N).astype(f32)
    wm=np.stack([1+0.02*warm,np.ones(N,f32),1-0.025*warm],1)
    col=(PAL[pid]*val[:,None]*wm)[ID].astype(f32)
    col*=(1+0.035*fs_act)[...,None]
    col*=(1+0.02*fbm(S,2.2,seed+40,fmin=12,fmax=70,ax=2.5,angle=0.5))[...,None]
    speck_st=rng.random(N)<0.30
    sp=fbm(S,0.5,seed+41,fmin=300)
    dark=(sp>1.9)&speck_st[ID]; light_=(sp<-1.9)&speck_st[ID]
    col=np.where(dark[...,None],lerp(col,hx("#5A5652"),0.8),col); col=np.where(light_[...,None],lerp(col,hx("#C9C3B6"),0.8),col)
    soil=hx("#3A3029")*(1+0.06*fbm(S,1.8,seed+15,fmin=10,fmax=200))[...,None]
    soil=lerp(soil,hx("#7A7066")*(0.85+0.3*blur(peb,1.5))[...,None],peb[...,None])
    col=lerp(soil,col,stone[...,None]).astype(f32)
    col,n_s=paint_form_light(col,np.clip((h-gpp)/depth,0,1),depth,T,hig=0.22,log=0.30)
    band=(smooth(0,0.005,dp)-smooth(0.015,0.03,dp)).astype(f32)
    rim=(band*smooth(0.20,0.50,n_s[...,1])).astype(f32)
    HI=hx(ST_HI); SH=hx(ST_SH)
    col=lerp(col*(1+0.10*rim[...,None]),HI,0.35*rim[...,None])
    under=(band*smooth(0.15,0.45,-n_s[...,1]))[...,None]; col=lerp(col*(1-0.2*under),SH,0.25*under)
    occ=np.zeros((S,S),f32)
    for q in range(1,24): occ=np.maximum(occ,np.roll(h,(q,int(round(0.15*q))),(0,1))-h-q*px*1.43)
    sh=blur(smooth(0,0.005,occ),1.2)[...,None]; del occ
    col=lerp(col*(1-0.45*sh),SH,0.30*sh)
    lich=lichen_dots(S,rng,px,lambda r,c:stone[r,c]>0.5,int(rng.integers(8,12)))
    lichen=np.zeros((S,S),f32)
    for ci in range(3):
        a=lich[ci]*(stone>0.5)*0.85; lichen=np.maximum(lichen,a); col=lerp(col,hx(LICHEN_C[ci]),a[...,None])
    ledge=((1-stone)*np.roll(stone,-10,0)).astype(f32)
    mf1=fbm(S,3.0,seed+30,fmin=2,fmax=14); mf2=smooth(-0.4,0.5,fbm(S,1.8,seed+31,fmin=10,fmax=60))
    mbase=mf2*np.maximum.reduce([ledge,smooth(0.45,0.7,n_s[...,1])*band*1.4,(1-stone)*0.8])
    thr=0.4
    for _ in range(14):
        moss=smooth(thr,thr+0.8,mf1)*np.clip(mbase,0,1); cov=float((moss>0.5).mean())
        if cov>0.08: thr+=0.1
        elif cov<0.06: thr-=0.1
        else: break
    moss=moss.astype(f32)
    mc=ramp3(fbm(S,1.6,seed+32,fmin=60)*0.5+0.5,hx(MOSS_C[0]),hx(MOSS_C[1]),hx(MOSS_C[2]))
    col=lerp(col,mc,np.clip(moss*1.2,0,1)[...,None])
    col*=(1+0.03*fbm(S,2.0,seed+50,fmin=1.5,fmax=5))[...,None]
    h=h+0.001*lichen+0.004*moss; h01=blur(np.clip(h/depth,0,1),1.0)
    R=np.clip(0.86*stone+0.95*(1-stone)+0.03*fs_act-0.05*rim+0.06*moss,0.6,0.98).astype(f32)
    bc,h1,R1=down2(np.clip(col,0,1).astype(f32)),down2(h01),down2(R)
    ao=cavity_ao(h1,radii=(3,10,30),k=(2.0,1.5,0.9),floor=0.40)
    if write:
        write_set(out_prefix,bc,h1,R1,depth,T,ao=ao,ao_in_albedo=0.35); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    st1=down2(stone)
    return dict(bc=bc*(0.65+0.35*ao)[...,None],h=h1,stone=st1,moss=float((moss>0.5).mean()))

# ===================== WATTLE, NET =====================
def gen_wattle(S=1024,seed=251,T=1.0,depth=0.035,out_prefix="T_VK_Wattle",write=True):
    rng=np.random.default_rng(seed); px=T/S
    x,y=grid(S); X=x*T; Y=(1-y)*T
    nst=4; sp=T/nst; nrod=18; pitch=T/nrod
    Yw=(Y+0.005*fbm(S,3.0,seed+1,fmin=1,fmax=4))%T
    row=np.floor(Yw/pitch).astype(np.int32)%nrod; v=(Yw/pitch)%1
    thick=rng.uniform(0.78,0.98,nrod).astype(f32)
    vv=(v-0.5)/(0.5*thick[row]); prof=np.sqrt(np.clip(1-vv*vv,0,1)).astype(f32)
    wz=np.cos(np.pi*(X/sp-0.5)+np.pi*row).astype(f32)
    rod=np.where(prof>0,0.30+0.22*wz+0.40*prof**0.8,0.05).astype(f32)
    streak=fbm(S,1.6,seed+3,fmin=15,fmax=250,ax=8)
    rod=rod+0.02*streak*prof
    su=((X/sp)%1-0.5)*sp/0.018; sprof=np.sqrt(np.clip(1-su*su,0,1)).astype(f32)
    stake=np.where(sprof>0,0.42+0.18*sprof,0).astype(f32)*(wz<0.2)
    isstake=stake>rod
    h=blur(np.clip(np.maximum(rod,stake),0,1).astype(f32),0.8)
    tone=rng.uniform(0,1,nrod).astype(f32)
    c0=np.array([0.36,0.26,0.16],f32); c1=np.array([0.58,0.45,0.28],f32)
    col=lerp(c0,c1,(0.3+0.5*tone[row])[...,None]*(0.6+0.4*prof[...,None]))
    col=col*(1+0.08*streak)[...,None]*(0.72+0.38*(wz*0.5+0.5))[...,None]
    col=np.where(isstake[...,None],np.array([0.40,0.31,0.20],f32)*(0.8+0.3*sprof[...,None]),col)
    grey=smooth(0.6,1.6,fbm(S,2.6,seed+4,fmin=2,fmax=20))
    col=lerp(col,np.array([0.52,0.50,0.44],f32)*(0.7+0.3*prof[...,None]),0.45*grey[...,None])
    col,n_s=paint_form_light(col.astype(f32),h,depth,T,hig=0.20,log=0.30)
    gapm=((prof<=0)&~isstake)
    col=np.where(gapm[...,None],col*0.5,col)
    R=np.clip(0.82+0.02*streak+0.1*gapm,0,1).astype(f32)
    ao=cavity_ao(h,radii=(2,6,16),k=(2.0,1.5,1.0),floor=0.3)
    if write:
        write_set(out_prefix,np.clip(col,0,1).astype(f32),h,R,depth,T,ao=ao,ao_in_albedo=0.45); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return dict(bc=col*(0.55+0.45*ao)[...,None],h=h)

def gen_net(S=512,seed=261,T=1.0,out_prefix="T_VK_Net",write=True):
    x,y,lead,ia,ib=lattice(S,8)
    cord=1-smooth(0.035,0.055,lead)
    a=(x+y)*8; b=(x-y)*8
    knot=np.exp(-((a-np.round(a))**2+(b-np.round(b))**2)/0.004).astype(f32)
    al=np.clip(cord+knot,0,1).astype(f32)
    col=np.array([0.55,0.47,0.34],f32)*(0.8+0.25*fbm(S,2.2,seed,fmin=3,fmax=60)[...,None]*0.4)*(0.85+0.2*(1-knot[...,None]))
    h=blur(np.clip(0.3*cord+0.5*knot,0,1),0.6)
    if write:
        write_set(out_prefix,col.astype(f32),h,np.full((S,S),0.9,f32),0.004,T,ao_in_albedo=0.2,extra={"A":al})
        PBR_SETS[out_prefix]=dict(depth=0.004,tile=T)
    return al

def net_material(name="M_VK_Net",prefix="T_VK_Net"):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    pbr_material(m,prefix,nstr=0.6,spec=0.1)
    nt=m.node_tree; L=nt.links
    out=next(n for n in nt.nodes if n.type=="OUTPUT_MATERIAL"); b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")
    uv=next(n for n in nt.nodes if n.type=="UVMAP")
    ta=nt.nodes.new("ShaderNodeTexImage"); ta.image=bpy.data.images[prefix+"_A"]; L.new(uv.outputs[0],ta.inputs[0])
    gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5; L.new(ta.outputs[0],gt.inputs[0])
    tp=nt.nodes.new("ShaderNodeBsdfTransparent"); ms=nt.nodes.new("ShaderNodeMixShader")
    L.new(gt.outputs[0],ms.inputs[0]); L.new(tp.outputs[0],ms.inputs[1]); L.new(b.outputs[0],ms.inputs[2]); L.new(ms.outputs[0],out.inputs[0])
    m.use_backface_culling=False
    try: m.surface_render_method="DITHERED"
    except: pass
    return m

# ===================== ROOF VARIANTS (slate, shingle) =====================
def shingle_layout2(S,seed,nrow=8,ncol=6,round_amt=0.27,chip_amt=0.012,bl=(0.9,0.97)):
    rng=np.random.default_rng(seed); x,y=grid(S)
    row=np.minimum((y*nrow).astype(int),nrow-1); v=(y*nrow)%1
    xo=(x*ncol+0.5*(row%2))%ncol; c=np.minimum(xo.astype(int),ncol-1); u=xo%1
    blv=rng.uniform(bl[0],bl[1],(nrow,ncol)).astype(f32)
    chip=fbm(S,2.6,seed+1,fmin=8,fmax=80)*chip_amt
    bottom=blv[row,c]-round_amt*(1-np.sqrt(np.clip(1-(2*u-1)**2,0,1)))+chip
    inside=v<bottom
    t=np.clip(v/np.maximum(bottom,0.05),0,1)
    tv=rng.uniform(-1,1,(nrow,ncol)).astype(f32)
    row2=(row+1)%nrow; xo2=(x*ncol+0.5*(row2%2))%ncol; c2=np.minimum(xo2.astype(int),ncol-1); u2=xo2%1
    return dict(row=row,c=c,u=u,v=v,bottom=bottom,inside=inside,t=t,tilt=tv,rng=rng,row2=row2,c2=c2,u2=u2,nrow=nrow,ncol=ncol)
def gen_roof_variant(name,nrow,ncol,round_amt,chip_amt,bl,pal,moss,depth,seed,S=1024,tile=3.0,grain=0.0,gap=0.035,tiltv=0.03):
    L=shingle_layout2(S,seed,nrow,ncol,round_amt,chip_amt,bl)
    u,t,inside=L["u"],L["t"],L["inside"]
    across=1-((2*u-1)**2)*0.25
    gapm=smooth(0.0,gap,np.minimum(u,1-u))
    hin=(0.18+0.72*t**0.85*across+L["tilt"][L["row"],L["c"]]*(u-0.5)*0.18)*(0.55+0.45*gapm)
    if grain: hin=hin+grain*fbm(S,1.6,seed+9,fmin=20,fmax=300,ay=8)
    gap2=smooth(0.0,gap,np.minimum(L["u2"],1-L["u2"]))
    hout=0.18*(0.55+0.45*gap2)*(1-((2*L["u2"]-1)**2)*0.25)
    h=blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.8)
    ao=cavity_ao(h,radii=(3,10,24),k=(2.5,1.8,1.0),floor=0.3)
    shadow=np.where(inside,1.0,0.55+0.45*smooth(0,0.25,L["v"]-L["bottom"])).astype(f32); ao=np.minimum(ao,shadow)
    rng=L["rng"]; row,c=L["row"],L["c"]
    light=painted_light(normal_from_height(blur(h,2.5),depth*3,tile))
    pal=np.array(pal,f32); pick=rng.integers(0,len(pal),(nrow,ncol)); tint=rng.uniform(0.88,1.10,(nrow,ncol)).astype(f32)
    hue=rng.uniform(-1,1,(nrow,ncol)).astype(f32)
    huev=np.array([tiltv,-tiltv*0.5,tiltv],f32)
    ins=inside[...,None]
    c_in=pal[pick[row,c]]*tint[row,c][...,None]*(1+hue[row,c][...,None]*huev)
    c_out=pal[pick[L["row2"],L["c2"]]]*tint[L["row2"],L["c2"]][...,None]
    col=np.where(ins,c_in,c_out)
    teff=np.where(inside,t,0.0)[...,None]
    col=col*(0.72+0.4*teff**0.8)*(0.85+0.25*light[...,None])
    if grain: col=col*(0.9+0.1*fbm(S,1.8,seed+10,fmin=10,fmax=200,ay=8)[...,None])
    col=col*(1+0.05*fbm(S,2.6,seed+5,fmin=3,fmax=90)[...,None])
    rough=np.clip(0.70+0.08*fbm(S,2.4,seed+6,fmin=6)+0.2*(1-inside),0,1).astype(f32)
    if moss>0:
        mz=smooth(0.6,1.6,fbm(S,3.0,seed+7,fmin=2))*moss*(0.6+0.4*(1-np.where(inside,t,0.0)))
        mcol=np.array([0.30,0.42,0.12],f32)
        col=col*(1-mz[...,None])+mcol*mz[...,None]; rough=np.clip(rough+0.2*mz,0,1)
    PBR_SETS[name]=dict(depth=depth,tile=tile)
    bc=(col*(0.45+0.55*ao)[...,None]).astype(f32)
    write_map(name+"_BC",bc); write_map(name+"_R",rough,True)
    write_map(name+"_N",normal_from_height(h,depth,tile)*0.5+0.5,True); write_map(name+"_H",h,True); write_map(name+"_AO",ao,True)
    return bc
def gen_roof_slate(): return gen_roof_variant("T_VK_RoofSlate",10,7,0.02,0.02,(0.93,0.97),
        [(0.26,0.29,0.34),(0.30,0.33,0.38),(0.23,0.26,0.31),(0.33,0.33,0.37)],0.15,0.035,301,gap=0.025)
def gen_roof_shingle(): return gen_roof_variant("T_VK_RoofShingle",9,10,0.0,0.035,(0.9,0.97),
        [(0.42,0.36,0.29),(0.47,0.41,0.33),(0.38,0.33,0.27),(0.52,0.49,0.44)],0.3,0.04,311,grain=0.05,gap=0.05,tiltv=0.0)

# ===================== ASHLAR re-tiled to 3.0 m (6 courses x 0.5 m) =====================
def gen_ashlar(S=1024,seed=13,tile=3.0,depth=0.03):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.0015)%1; Y=(y+fbm(S,3.5,seed+2)*0.0015)%1
    nrow=6; row=np.minimum((Y*nrow).astype(int),nrow-1); v=(Y*nrow)%1
    blocks=np.array([4,5,4,5,4,5]); offs=rng.uniform(0,1,nrow)
    nb=blocks[row]; xo=(X+offs[row])%1; c=np.minimum((xo*nb).astype(int),nb-1); u=(xo*nb)%1
    d=np.minimum(np.minimum(u,1-u)*S/nb,np.minimum(v,1-v)*S/nrow)
    d=d+fbm(S,2.6,seed+3,fmin=6,fmax=80)*1.5; gap=2.6
    mask=smooth(gap,gap+1.3,d); cham=smooth(gap,gap+14,d)
    sid=row*8+c; tv=rng.uniform(-1,1,(nrow*8,2)).astype(f32)
    chip=smooth(1.5,2.0,fbm(S,2.6,seed+5,fmin=6,fmax=60))*(1-smooth(gap+2,gap+22,d))
    hs=0.45+0.42*cham+(tv[sid,0]*(u-0.5)+tv[sid,1]*(v-0.5))*0.08*cham+0.004*fbm(S,1.8,seed+4,fmin=60,fmax=300)*cham-0.3*chip
    h=blur(np.clip(mask*hs+(1-mask)*0.12,0,1),0.7).astype(f32)
    val=rng.uniform(0.92,1.06,nrow*8).astype(f32); warm=rng.uniform(-1,1,nrow*8).astype(f32)
    base=_pal('S2')*1.02*val[sid][...,None]*(1+warm[sid][...,None]*np.array([0.02,0.0,-0.025],f32))
    base=base*(1+0.018*fbm(S,2.2,seed+7,fmin=12,fmax=70,ax=2.5,angle=0.4))[...,None]
    col=lerp(hx("#736A5E")*(1+0.05*fbm(S,1.5,seed+8,fmin=20,fmax=150))[...,None],base,mask[...,None]).astype(f32)
    col,n_s=paint_form_light(col,h,depth,tile,hig=0.22,log=0.28)
    dp=(d-gap)*tile/S
    band=(smooth(0,0.003,dp)-smooth(0.008,0.016,dp)).astype(f32)
    rim=(band*smooth(0.2,0.5,n_s[...,1])).astype(f32)
    col=lerp(col*(1+0.08*rim[...,None]),hx(ST_HI),0.35*rim[...,None])
    under=(band*smooth(0.15,0.45,-n_s[...,1]))[...,None]; col=lerp(col*(1-0.2*under),hx(ST_SH),0.25*under)
    col=lerp(col,lerp(col,luma(col)[...,None],0.5)*1.1,0.6*chip[...,None])
    col*=(1+0.03*fbm(S,2.0,seed+50,fmin=1.5,fmax=5))[...,None]
    rough=np.clip(0.8+0.04*fbm(S,2.4,seed+9,fmin=6)+0.12*(1-mask)-0.05*rim,0,1).astype(f32)
    ao=cavity_ao(h,radii=(3,10,30),k=(2.0,1.5,0.9),floor=0.4)
    PBR_SETS["T_VK_Ashlar"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Ashlar",np.clip(col,0,1).astype(f32),h,rough,depth,tile,ao=ao,ao_in_albedo=0.3)

# ===================== TERRAIN TEXTURES =====================
def gen_grass(S=1024,seed=401,T=4.0,depth=0.02,out_prefix="T_VK_Grass",write=True):
    rng=np.random.default_rng(seed); px=T/S
    t=smooth(-2.4,2.4,fbm(S,2.4,seed,fmin=1.5))
    col=ramp3(t,hx("#3E6A1A"),hx("#5E9028"),hx("#8DB240"),0.5)
    dry=smooth(1.3,2.2,fbm(S,3.0,seed+1,fmin=1,fmax=8))[...,None]
    col=lerp(col,hx("#A39A55")*(0.9+0.2*t[...,None]),0.45*dry)
    # clumps: blades oriented around a per-clump angle
    x,y=grid(S); cp=rng.uniform(0,1,(120,2)); F1,F2,ID=voronoi(x,y,cp)
    ang_c=rng.uniform(0,2*math.pi,120)
    blades=np.zeros((S,S),f32); tips=np.zeros((S,S),f32)
    for layer in range(2):
        segs=[]; tsegs=[]
        for _ in range(1400):
            bx,by=rng.uniform(0,S),rng.uniform(0,S)
            cid=ID[int(by)%S,int(bx)%S]; a=ang_c[cid]+rng.uniform(-0.6,0.6)
            L=rng.uniform(10,22); w=rng.uniform(2.0,3.0)
            ex,ey=bx+math.cos(a)*L,by+math.sin(a)*L
            segs.append((bx,by,ex,ey,w)); tsegs.append((bx+math.cos(a)*L*0.7,by+math.sin(a)*L*0.7,ex,ey,w*0.8))
        blades=np.maximum(blades,draw_segments(S,segs)*(0.6+0.4*layer)); tips=np.maximum(tips,draw_segments(S,tsegs))
    lush=(1-dry[...,0])
    col=col*(1-0.22*blades[...,None])+hx("#A2C84A")*0.22*blades[...,None]*(0.7+0.3*lush[...,None])
    col=col*(1-0.10*blur(blades,2.0)[...,None])*(1+0.16*tips[...,None])
    # flowers
    fl=np.zeros((S,S),f32); fsegs=[[],[]]
    for _ in range(int(S*S*0.003/40)):
        fx,fy=rng.uniform(0,S),rng.uniform(0,S)
        if lush[int(fy)%S,int(fx)%S]<0.7: continue
        fsegs[rng.integers(0,2)].append((fx,fy,fx+0.01,fy,rng.uniform(3,5)))
    for ci,c in enumerate(("#F2EEDC","#F2D450")):
        if fsegs[ci]:
            m=draw_segments(S,fsegs[ci]); col=lerp(col,hx(c),m[...,None]); fl=np.maximum(fl,m)
    h=np.clip(0.5+0.25*blades+0.15*tips+0.1*fbm(S,2.0,seed+5,fmin=4,fmax=80)*0.3+0.2*fl,0,1).astype(f32)
    light=painted_light(normal_from_height(blur(h,1.5),depth*3,T))
    col=col*(0.82+0.3*light[...,None])
    R=np.clip(0.9-0.05*fl,0,1).astype(f32)
    col=np.clip(col,0,1).astype(f32)
    if write:
        write_set(out_prefix,col,h,R,depth,T,ao_in_albedo=0.35); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return col

def gen_cliff(S=2048,seed=421,T=6.0,depth=0.10,out_prefix="T_VK_Cliff",write=True):
    """layered natural rock: 4 bands per 6 m repeat, band boundaries at world z = 1.5k (tier boundaries)"""
    rng=np.random.default_rng(seed); px=T/S
    x,y=grid(S); vz=(1-y)*4.0                 # band coordinate (0..4) from image bottom
    band=np.minimum(vz.astype(np.int32),3); b=(vz-band).astype(f32)
    pals=[hx("#A98A62"),hx("#8F8C86"),hx("#B39C76"),hx("#7B7280")]
    h=np.zeros((S,S),f32); col=np.zeros((S,S,3),f32); edge=np.zeros((S,S),f32); blockv=np.zeros((S,S),f32)
    xw=(x+0.012*fbm(S,2.5,seed+1,fmin=3,fmax=30))%1
    for k in range(4):
        for half,(b0,b1) in enumerate(((0.0,0.5),(0.5,0.9))):
            m=(band==k)&(b>=b0)&(b<b1)
            if not m.any(): continue
            n=int(rng.integers(6,10)); xs=(np.arange(n)+rng.uniform(-0.3,0.3,n))/n
            ys=np.full(n,(k+(b0+b1)/2)/4.0)+rng.uniform(-0.003,0.003,n)
            pts=np.stack([xs%1,1-ys],1).astype(f32)
            F1,F2,ID=voronoi(xw[m],y[m],pts,1.0,2.6)
            e=np.clip((F2-F1)/0.02,0,1)
            dome=np.sqrt(np.clip((F2-F1)/0.06,0,1))
            vv=rng.uniform(0.9,1.1,n).astype(f32)
            h[m]=0.55+0.3*dome; edge[m]=e; blockv[m]=vv[ID]
            col[m]=pals[k]*vv[ID][:,None]*(0.97+0.06*half)
    fac=facets(S,seed+3,3,20,0.20)+0.3*facets(S,seed+4,6,40,0.08)
    h=h+fac*0.45
    # grooves: primary at b=0 (and b=1), secondary at 0.5, soil band above 0.86
    g1=np.minimum(b,1-b)*T/4/px; groove1=1-smooth(0,10,g1)
    g2=np.abs(b-0.5)*T/4/px; groove2=1-smooth(0,6,g2)
    soil=smooth(0.895,0.915,b)*(1-smooth(0.99,1.0,b))
    h=h*(1-0.8*groove1)*(1-0.5*groove2)
    h=np.where(soil>0.5,0.35+0.1*fbm(S,2.0,seed+5,fmin=10,fmax=100),h)
    h=blur(np.clip(h,0,1).astype(f32),1.2)
    # roots in soil band
    roots=draw_segments(S,crack_segments(S,rng,n=60,steps=(6,14),step_px=(4,8),w0=2.0,branch=0.2,dirbias=math.pi/2,jit=0.4))
    col=np.where((soil>0.5)[...,None],hx("#5A4230")*(1+0.1*fbm(S,2.0,seed+6,fmin=10)[...,None]),col)
    col=lerp(col,hx("#5A4028"),(roots*soil*0.8)[...,None])
    # painted light with no lateral component (box projection flips u)
    n_=normal_from_height(blur(h,3.0),depth*2.5,T)
    lt=painted_light(n_,(0.0,0.85,0.5))
    col=col*(0.72+0.42*lt[...,None])
    rimt=smooth(0.25,0.6,n_[...,1])*(1-soil); col=lerp(col,col*1.15+0.03,0.6*rimt[...,None])
    und=smooth(0.2,0.5,-n_[...,1]); col=col*(1-0.25*und[...,None])
    col=col*(1-0.55*groove1[...,None])*(1-0.3*groove2[...,None])*(0.75+0.25*edge[...,None])
    # drips below seams
    drip=smooth(0.5,1.5,fbm(S,2.0,seed+7,fmin=6,fmax=60,ay=8))*(smooth(0.0,0.25,b)*(1-smooth(0.25,0.45,b))+smooth(0.5,0.6,b)*(1-smooth(0.6,0.8,b)))
    col=col*(1-0.12*drip[...,None])
    # moss on up-facing block tops
    moss=smooth(0.45,0.8,n_[...,1])*smooth(0.3,1.2,fbm(S,2.8,seed+8,fmin=3,fmax=40))*(1-soil)
    mc=ramp3(fbm(S,1.6,seed+9,fmin=60)*0.5+0.5,hx(MOSS_C[0]),hx(MOSS_C[1]),hx(MOSS_C[2]))
    col=lerp(col,mc,np.clip(moss*1.1,0,1)[...,None])
    col=col*(1+0.04*fbm(S,2.0,seed+10,fmin=1.5,fmax=6))[...,None]
    R=np.clip(0.85+0.05*soil+0.05*moss-0.05*rimt,0,1).astype(f32)
    bc,h1,R1=down2(np.clip(col,0,1).astype(f32)),down2(h),down2(R)
    ao=cavity_ao(h1,radii=(3,10,30),k=(2.0,1.5,0.9),floor=0.4)
    if write:
        write_set(out_prefix,bc,h1,R1,depth,T,ao=ao,ao_in_albedo=0.35); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return bc*(0.65+0.35*ao)[...,None]

def gen_terrain_macro(S=512,seed=441,out="T_VK_TerrainMacro",write=True):
    r=fbm(S,2.6,seed,fmin=1,fmax=24)*0.5+0.5
    g=fbm(S,2.4,seed+1,fmin=1,fmax=12)*0.5+0.5
    b=fbm(S,2.2,seed+2,fmin=2,fmax=60)*0.5+0.5
    m=np.clip(np.stack([r,g,b],-1)*0.5+0.25,0,1).astype(f32)
    if write: write_map(out,m,True)
    return m

def gen_dirt(S=1024,seed=451,T=4.0,depth=0.03,out_prefix="T_VK_Dirt",write=True):
    rng=np.random.default_rng(seed); px=T/S; x,y=grid(S)
    t=smooth(-2.0,2.0,fbm(S,2.4,seed,fmin=1.5))
    col=ramp3(t,hx("#5A3F28"),hx("#7A5A3A"),hx("#9A7C56"),0.5)
    pts=rng.uniform(0,1,(300,2)); F1,F2,ID=voronoi(x,y,pts)
    show=(rng.random(300)<0.25)[ID]; r=rng.uniform(0.004,0.012,300)[ID]/T
    peb=(1-smooth(r*0.6,r,F1))*show
    h=0.45+0.08*fbm(S,2.2,seed+1,fmin=4,fmax=120)+0.4*np.sqrt(np.clip(peb,0,1))
    col=lerp(col,hx("#8C857A")*(0.8+0.3*fbm(S,1.5,seed+2,fmin=40)[...,None]*0.3),(peb*0.95)[...,None])
    cr=draw_segments(S,crack_segments(S,rng,n=6,w0=1.5))
    h=h-0.15*cr; col=col*(1-0.3*cr[...,None])
    sprig=smooth(1.6,2.2,fbm(S,2.0,seed+3,fmin=6,fmax=60))
    segs=[]
    for _ in range(500):
        bx,by=rng.uniform(0,S),rng.uniform(0,S)
        if sprig[int(by)%S,int(bx)%S]<0.3: continue
        a=rng.uniform(0,2*math.pi); L=rng.uniform(6,14); segs.append((bx,by,bx+math.cos(a)*L,by+math.sin(a)*L,2.0))
    if segs:
        sp=draw_segments(S,segs); col=lerp(col,hx("#6E8A2C"),(sp*0.85)[...,None]); h=h+0.1*sp
    h=blur(np.clip(h,0,1).astype(f32),0.8)
    lt=painted_light(normal_from_height(blur(h,1.5),depth*3,T)); col=col*(0.8+0.32*lt[...,None])
    R=np.clip(0.95-0.1*peb,0,1).astype(f32)
    if write: write_set(out_prefix,np.clip(col,0,1).astype(f32),h,R,depth,T,ao_in_albedo=0.4); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return col

def gen_cobble(S=1024,seed=461,T=4.0,depth=0.05,out_prefix="T_VK_Cobble",write=True):
    rng=np.random.default_rng(seed); x,y=grid(S)
    pts=rng.uniform(0,1,(110,2)).astype(f32)
    s4=256; xs,ys=grid(s4)
    for _ in range(2):
        F1,F2,ID=voronoi(xs,ys,pts); n=len(pts)
        cx=np.arctan2(np.bincount(ID.ravel(),np.sin(2*np.pi*xs).ravel(),n),np.bincount(ID.ravel(),np.cos(2*np.pi*xs).ravel(),n))/(2*np.pi)%1
        cy=np.arctan2(np.bincount(ID.ravel(),np.sin(2*np.pi*ys).ravel(),n),np.bincount(ID.ravel(),np.cos(2*np.pi*ys).ravel(),n))/(2*np.pi)%1
        pts=np.stack([cx,cy],1).astype(f32)
    xw=(x+0.004*fbm(S,2.5,seed+1,fmin=4,fmax=40))%1; yw=(y+0.004*fbm(S,2.5,seed+2,fmin=4,fmax=40))%1
    F1,F2,ID=voronoi(xw,yw,pts)
    e=F2-F1
    dome=np.sqrt(np.clip(e/0.05,0,1))
    joint=1-smooth(0.006,0.018,e)
    n=len(pts); keys=["S1","S2","S3","S4","S1","S3"]
    PAL=np.stack([_pal(k) for k in keys]); pid=rng.integers(0,len(keys),n); val=rng.uniform(0.88,1.08,n).astype(f32)
    col=(PAL[pid]*val[:,None])[ID]
    h=0.3+0.55*dome+facets(S,seed+3,6,60,0.08)*dome
    h=np.where(joint>0.5,0.18+0.05*fbm(S,2.0,seed+4,fmin=20),h)
    h=blur(np.clip(h,0,1).astype(f32),0.8)
    col,n_s=paint_form_light(col.astype(f32),h,depth,T,hig=0.25,log=0.30)
    grassj=smooth(0.2,0.8,fbm(S,2.0,seed+5,fmin=3,fmax=30))*(rng.random() if False else 1.0)
    jc=lerp(hx("#33291F"),hx("#4E7020"),(grassj>0.5)[...,None]*0.9)
    col=lerp(col,jc,joint[...,None])
    col*=(1+0.03*fbm(S,2.0,seed+6,fmin=1.5,fmax=5))[...,None]
    R=np.clip(0.82+0.1*joint,0,1).astype(f32)
    ao=cavity_ao(h,radii=(2,6,18),k=(2.0,1.5,0.9),floor=0.4)
    if write: write_set(out_prefix,np.clip(col,0,1).astype(f32),h,R,depth,T,ao=ao,ao_in_albedo=0.35); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return col

def gen_sand(S=1024,seed=471,T=4.0,depth=0.015,out_prefix="T_VK_Sand",write=True):
    rng=np.random.default_rng(seed); x,y=grid(S)
    t=smooth(-2,2,fbm(S,2.4,seed,fmin=1.5))
    col=lerp(hx("#B8A37A"),hx("#D2BC8C"),t[...,None])
    rip=fbm(S,2.0,seed+1,fmin=8,fmax=40,ax=6,angle=0.3)
    pts=rng.uniform(0,1,(150,2)); F1,F2,ID=voronoi(x,y,pts); r=rng.uniform(0.003,0.008,150)[ID]/T
    peb=1-smooth(r*0.6,r,F1)
    col=lerp(col,hx("#8A8274")*(0.8+0.4*rng.random(150)[ID][...,None]),(peb*0.9)[...,None])
    h=blur(np.clip(0.5+0.12*rip+0.35*peb,0,1).astype(f32),0.8)
    lt=painted_light(normal_from_height(blur(h,1.5),depth*3,T)); col=col*(0.85+0.25*lt[...,None])
    if write: write_set(out_prefix,np.clip(col,0,1).astype(f32),h,np.full((S,S),0.8,f32),depth,T,ao_in_albedo=0.3); PBR_SETS[out_prefix]=dict(depth=depth,tile=T)
    return col
