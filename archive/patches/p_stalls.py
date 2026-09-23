import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
p='vk_helpers.py'; s=open(p,encoding='utf8').read()
lines=s.split("\n")
i0=next(i for i,l in enumerate(lines) if l=="    # goods: crates with produce on the counter")
i1=next(i for i,l in enumerate(lines) if l=="    # hanging price sign")
sign_i=[i for i in range(i1,i1+5) if "YELLOW,bevel=0)" in lines[i]][0]
lines[sign_i]=lines[sign_i].replace("YELLOW,bevel=0)","STALL_SIGN.get(trade,YELLOW),bevel=0)")
lines[i0:i1]=["    trade=goods if isinstance(goods,str) else \"produce\"",
              "    stall_wares(k,trade,W_,D_)"]
s="\n".join(lines)
s=s.replace('def market_stall(k,goods=("APPLE","PUMPKIN","BREAD")):','def market_stall(k,goods="produce"):',1)

wares='''STALL_TRADES=("produce","greengrocer","baker","fishmonger","potter","draper","cheese","tinker")
STALL_SIGN={"produce":YELLOW,"greengrocer":LEAF,"baker":BREAD,"fishmonger":STEEL,"potter":CLAY,"draper":PINK,"cheese":YELLOW,"tinker":IRON}
def _rot_vs(vs,c,ang,axis="Z"):
    R=Matrix.Rotation(ang,4,axis); c=Vector(c)
    for v in vs: v.co=c+R@(v.co-c)
def _mat(vs,mi,smooth=True):
    for f in {f for v in vs for f in v.link_faces}: f.material_index=mi; f.smooth=smooth
def _stall_barrels(k,W_):
    for (x,y) in ((W_/2+0.55,-0.2),(W_/2+0.5,0.55)):
        for zz,(r0,r1) in ((0.25,(0.34,0.4)),(0.75,(0.4,0.34))):
            cyl_=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=12,radius1=r0,radius2=r1,depth=0.5)["verts"]
            for v in cyl_: v.co+=Vector((x,y,zz))
            k.project({f for v in cyl_ for f in v.link_faces},WOOD)
        for zz in(0.12,0.88):
            cyl_=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=12,radius1=0.39,radius2=0.39,depth=0.06)["verts"]
            for v in cyl_: v.co+=Vector((x,y,zz))
            _mat(cyl_,IRON,False)
def _stall_sack(k,x,y,mi=CLOTH_B,s=1.0):
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.32*s)["verts"]
    for v in vs: v.co=Vector((v.co.x,v.co.y*0.85,v.co.z*1.2))+Vector((x,y,0.35*s))
    _mat(vs,mi)
def stall_wares(k,trade,W_,D_):
    """goods on the counter (top z 1.02, x -1.6..1.6, y -0.85..0.15), on the back shelf (z 1.49, y ~0.65) and beside
    the stall, per trade"""
    rnd=random.Random(sum(map(ord,trade))); z0=1.02
    Ry=Matrix.Rotation(math.pi/2,4,"Y"); Rx=Matrix.Rotation(math.pi/2,4,"X")
    def crate(cx,w=0.85,d=0.62,h=0.2,cy=-0.45):
        k.box((cx,cy,z0+h/2),(w,d,h),WOOD,bevel=0.03); return z0+h
    def basket(cx,cy,r=0.3,h=0.16,z=z0):
        _cyl(k,(cx,cy,z+h/2),r,r*1.12,h,14,WOOD); return z+h
    shelf=1.49
    if trade=="produce":
        for cx,g in zip((-1.0,0.0,1.0),("APPLE","PUMPKIN","BREAD")):
            top=crate(cx,h=0.26)
            for n_ in range(9 if g=="APPLE" else (4 if g=="PUMPKIN" else 6)):
                if g=="APPLE":
                    vs=_ico(k,(cx-0.28+(n_%3)*0.28+rnd.uniform(-.03,.03),-0.62+(n_//3)*0.17,top+0.05+rnd.uniform(0,.03)),0.09,APPLE)
                elif g=="PUMPKIN":
                    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.19)["verts"]
                    for v in vs:
                        ang=math.atan2(v.co.y,v.co.x); v.co.z*=0.72; v.co*=(1+0.06*math.cos(8*ang))
                        v.co+=Vector((cx-0.2+(n_%2)*0.4,-0.58+(n_//2)*0.3,top+0.14))
                    _mat(vs,PUMPKIN)
                else:
                    vs=_ico(k,(cx-0.25+(n_%3)*0.25,-0.58+(n_//3)*0.25,top+0.08),0.14,BREAD,scale=(0.9,1.4,0.6))
                _mat(vs,{"APPLE":APPLE,"PUMPKIN":PUMPKIN,"BREAD":BREAD}[g])
    elif trade=="greengrocer":
        top=crate(-1.05)
        for n_ in range(6): _mat(_ico(k,(-1.3+(n_%3)*0.25,-0.6+(n_//3)*0.28,top+0.11),0.15,LEAF,scale=(1,1,0.85),jit=0.015,seed=n_),LEAF)
        top=crate(0.0)
        for n_ in range(12):
            x=-0.3+(n_%6)*0.12; y=-0.58+(n_//6)*0.26; a=rnd.uniform(-0.25,0.25)
            vs=_cyl(k,(x,y,top+0.04),0.035,0.0,0.24,6,PUMPKIN,rot=Matrix.Rotation(math.pi/2+a,4,"Z")@Ry@Rx); _mat(vs,PUMPKIN)
            _mat(_ico(k,(x,y+0.14,top+0.05),0.045,LEAF,scale=(1,1.6,0.7),sub=1),LEAF)
        top=crate(1.05)
        for n_ in range(12): _mat(_ico(k,(0.78+(n_%4)*0.18,-0.66+(n_//4)*0.2,top+0.06),0.075,PAPER if n_%3 else PINK,scale=(1,1,0.9)),PAPER if n_%3 else PINK)
        for cx in (-0.9,0.0,0.9):
            t=basket(cx,0.62,0.22,0.12,shelf)
            for n_ in range(5): _mat(_ico(k,(cx+rnd.uniform(-.1,.1),0.62+rnd.uniform(-.08,.08),t+0.03),0.08,APPLE),APPLE)
    elif trade=="baker":
        t=basket(-1.0,-0.45,0.36,0.14)
        for n_ in range(5): _mat(_ico(k,(-1.18+(n_%3)*0.18,-0.55+(n_//3)*0.2,t+0.05),0.14,BREAD,scale=(0.75,1.3,0.55)),BREAD)
        k.box((0.05,-0.45,z0+0.03),(0.85,0.6,0.05),WOOD,bevel=0.015)
        for n_ in range(4): _mat(_ico(k,(-0.15+(n_%2)*0.38,-0.6+(n_//2)*0.3,z0+0.11),0.14,BREAD,scale=(1,1,0.62)),BREAD)
        t=basket(1.05,-0.4,0.2,0.36)
        for n_ in range(6):
            a=n_*1.05; vs=_cyl(k,(1.05+0.07*math.cos(a),-0.4+0.07*math.sin(a),t+0.12),0.04,0.035,0.72,8,BREAD,
                               rot=Matrix.Rotation(0.18,4,"X")@Matrix.Rotation(a,4,"Z")); _mat(vs,BREAD)
        for n_ in range(7): _mat(_ico(k,(-1.3+n_*0.43,0.62,shelf+0.07),0.12,BREAD,scale=(1.3,0.8,0.6)),BREAD)
        for n_,(x,y) in enumerate(((W_/2+0.5,-0.3),(W_/2+0.45,0.35),(W_/2+0.95,0.05))): _stall_sack(k,x,y,BURLAP,0.95)
        _stall_sack(k,-W_/2-0.45,-0.4,BURLAP)
        return
    elif trade=="fishmonger":
        k.box((0,-0.45,z0+0.05),(2.7,0.72,0.1),WOOD,bevel=0.02)
        k.box((0,-0.45,z0+0.105),(2.55,0.6,0.03),PAPER,bevel=0.01)
        for n_ in range(10):
            x=-1.1+n_*0.245; y=-0.45+rnd.uniform(-0.12,0.12); a=rnd.uniform(0.6,1.1)*(1 if n_%2 else -1)
            vs=_ico(k,(x,y,z0+0.16),1.0,STEEL,scale=(0.25,0.075,0.065)); _rot_vs(vs,(x,y,z0+0.16),a); _mat(vs,STEEL)
            tx,ty=x-0.27*math.cos(a),y-0.27*math.sin(a)
            k.box((tx,ty,z0+0.16),(0.1,0.02,0.12),STEEL,rot=(0,0,a),bevel=0.0)
        for n_,x in enumerate((-1.1,-0.4,0.4,1.1)):
            vs=_ico(k,(x,-(D_/2-0.1),2.1),1.0,STEEL,scale=(0.07,0.055,0.26)); _mat(vs,STEEL)
            k.box((x,-(D_/2-0.1),2.42),(0.012,0.012,0.12),WOOD,bevel=0)
        for n_ in range(3): _mat(_ico(k,(-1.0+n_*0.9,0.62,shelf+0.1),0.13,BURLAP,scale=(1.2,0.9,0.8)),BURLAP)
    elif trade=="potter":
        for n_,x in enumerate((-1.35,-1.02,-0.69)):
            h=0.26+0.04*(n_%2)
            _cyl(k,(x,-0.5,z0+h/2),0.1,0.15,h,14,CLAY); _cyl(k,(x,-0.5,z0+h+0.05),0.065,0.055,0.1,12,CLAY)
            _cyl(k,(x,-0.5,z0+h+0.11),0.08,0.08,0.025,12,CLAY)
        for n_ in range(3): _cyl(k,(-0.15,-0.45,z0+0.04+n_*0.055),0.1,0.19,0.07,16,CLAY)
        for n_ in range(7): _cyl(k,(0.3,-0.5,z0+0.01+n_*0.018),0.17,0.17,0.016,18,CLAY)
        for n_,x in enumerate((0.85,1.3)): _cyl(k,(x,-0.45,z0+0.18),0.2,0.14,0.36,16,CLAY); _cyl(k,(x,-0.45,z0+0.38),0.11,0.12,0.05,14,CLAY)
        for n_ in range(8): _cyl(k,(-1.3+n_*0.37,0.62,shelf+0.05),0.045,0.055,0.1,10,CLAY)
        _cyl(k,(W_/2+0.5,-0.1,0.35),0.24,0.34,0.7,16,CLAY); _cyl(k,(W_/2+0.5,-0.1,0.78),0.15,0.19,0.16,14,CLAY)
        _cyl(k,(W_/2+0.55,0.6,0.22),0.2,0.26,0.44,16,CLAY)
        _stall_sack(k,-W_/2-0.45,-0.4,HAY,0.8)
        return
    elif trade=="draper":
        cols=(CLOTH_A,PINK,YELLOW,BURLAP,CLOTH_B,SHUTTER)
        for n_ in range(6):
            x=-1.2+(n_%3)*0.2; y=-0.62+(n_//3)*0.22
            _cyl(k,(-0.8,y,z0+0.1+(n_%3)*0.19),0.095,0.095,0.85,14,cols[n_],rot=Ry)
        for r_ in range(3):
            for n_ in range(3): k.box((0.35+r_*0.45,-0.45,z0+0.03+n_*0.06),(0.38,0.46,0.055),cols[(r_*2+n_)%6],bevel=0.012)
        for n_ in range(5):
            for m_ in range(2): k.box((-1.25+n_*0.62,0.62,shelf+0.03+m_*0.05),(0.42,0.34,0.05),cols[(n_+m_)%6],bevel=0.01)
        k.box((W_/2+0.55,0.0,0.3),(0.7,0.6,0.6),WOOD,bevel=0.03)
        for n_ in range(4): _cyl(k,(W_/2+0.38+(n_%2)*0.3,-0.12+(n_//2)*0.22,0.85),0.08,0.08,0.7,12,cols[n_+1])
        _stall_sack(k,-W_/2-0.45,-0.4,CLOTH_B)
        return
    elif trade=="cheese":
        for st,(x,y) in enumerate(((-1.15,-0.45),(-0.6,-0.5))):
            for n_ in range(3-st): _cyl(k,(x,y,z0+0.065+n_*0.13),0.22,0.22,0.12,20,YELLOW)
        k.box((0.3,-0.45,z0+0.025),(0.8,0.55,0.045),WOOD,bevel=0.015)
        for n_ in range(4): _cyl(k,(0.08+(n_%2)*0.4,-0.58+(n_//2)*0.26,z0+0.1),0.12,0.12,0.1,16,YELLOW)
        for n_ in range(3): _cyl(k,(1.15,-0.45,z0+0.04+n_*0.075),0.26-n_*0.05,0.26-n_*0.05,0.07,20,YELLOW)
        for n_,x in enumerate((-1.2,-0.85,-0.5,0.5,0.85,1.2)):
            vs=_ico(k,(x,-(D_/2-0.1),2.13),1.0,HIDE,scale=(0.045,0.045,0.2)); _mat(vs,HIDE)
            k.box((x,-(D_/2-0.1),2.4),(0.01,0.01,0.12),BURLAP,bevel=0)
        for n_ in range(6): _cyl(k,(-1.3+n_*0.52,0.62,shelf+0.06),0.12,0.12,0.1,16,YELLOW)
    elif trade=="tinker":
        for n_,x in enumerate((-1.3,-0.95)): _cyl(k,(x,-0.5,z0+0.08),0.15,0.12,0.16,16,IRON); k.box((x,-0.5,z0+0.2),(0.3,0.02,0.02),IRON,bevel=0)
        for n_ in range(3):
            x=-0.5+n_*0.33; _cyl(k,(x,-0.55,z0+0.02),0.14,0.14,0.035,16,IRON); k.box((x,-0.28,z0+0.03),(0.04,0.3,0.025),IRON,bevel=0)
        for n_ in range(4):
            x=0.6+n_*0.22; k.box((x,-0.45,z0+0.02),(0.04,0.45,0.035),WOOD,bevel=0.005); k.box((x,-0.66,z0+0.04),(0.14,0.07,0.06),IRON,bevel=0.01)
        for n_ in range(4):
            vs=bmesh.ops.create_circle(k.bm,cap_ends=True,segments=12,radius=0.06)["verts"]
            for v in vs: v.co+=Vector((-1.3+n_*0.2,0.62,shelf+0.01))
            _mat(vs,IRON,False)
        for n_ in range(3): _cyl(k,(0.2+n_*0.45,0.62,shelf+0.1),0.13,0.11,0.2,14,BRONZE if n_==1 else IRON)
        k.box((W_/2+0.55,-0.2,0.3),(0.65,0.55,0.6),WOOD,bevel=0.03)
        k.box((W_/2+0.55,0.55,0.25),(0.6,0.5,0.5),WOOD,bevel=0.03)
        _cyl(k,(W_/2+0.55,-0.2,0.7),0.16,0.13,0.2,14,IRON)
        _stall_sack(k,-W_/2-0.45,-0.4,BURLAP)
        return
    _stall_barrels(k,W_)
    _stall_sack(k,-W_/2-0.45,-0.4)
'''
a="def market_stall(k,goods=\"produce\"):"
assert s.count(a)==1; s=s.replace(a,wares+a)
# register the variants
a='''     ("SM_VK_MarketStall",market_stall,ng),("SM_VK_Prop_Well",prop_well,ng),'''
b='''     ("SM_VK_MarketStall",market_stall,ng),
     *[("SM_VK_MarketStall_"+t_.capitalize(),(lambda k,t_=t_: market_stall(k,t_)),ng) for t_ in STALL_TRADES[1:]],
     ("SM_VK_Prop_Well",prop_well,ng),'''
assert s.count(a)==1; s=s.replace(a,b)
open(p,'w',encoding='utf8').write(s)
import ast; ast.parse(s)

p='vk_town_map.py'; t=open(p,encoding='utf8').read()
a='''        T.P("SM_VK_MarketStall",x,y,rt,style={"cloth":("Red","Blue","Green","Yellow")[k]})'''
b='''        T.P(("SM_VK_MarketStall_Baker","SM_VK_MarketStall_Fishmonger","SM_VK_MarketStall_Potter","SM_VK_MarketStall_Draper")[k],
            x,y,rt,style={"cloth":("Red","Blue","Green","Yellow")[k]})'''
assert t.count(a)==1; t=t.replace(a,b); open(p,'w',encoding='utf8').write(t)
p='vk_terrain_demo.py'; t=open(p,encoding='utf8').read()
a='''        P("SM_VK_MarketStall",x,y,rt,st={"cloth":r.choice(["Red","Blue","Green","Yellow"])})'''
b='''        P(r.choice(["SM_VK_MarketStall","SM_VK_MarketStall_Greengrocer","SM_VK_MarketStall_Cheese","SM_VK_MarketStall_Tinker"]),
          x,y,rt,st={"cloth":r.choice(["Red","Blue","Green","Yellow"])})'''
assert t.count(a)==1; t=t.replace(a,b); open(p,'w',encoding='utf8').write(t)
print("ok")
