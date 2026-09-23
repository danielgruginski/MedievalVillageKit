import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
p='vk_helpers.py'; s=open(p,encoding='utf8').read()

# ---- lit windows as a style
a='SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A,"stone":STONE}'
assert s.count(a)==1
s=s.replace(a,'SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A,"stone":STONE,"window":WINDOW}')
a='''def variant_mat(kind,name):
    spec=VARIANT_MATS[kind][name]'''
assert s.count(a)==1
s=s.replace(a,'''def lit_window_material(name="M_VK_Window_Lit",warm=(1.0,0.58,0.22),strength=2.2):
    """the kit window glass lit from inside: emission = window albedo x warm colour (muntins stay dark)"""
    m=bpy.data.materials.get(name)
    if m is None:
        m=bpy.data.materials["M_VK_Window"].copy(); m.name=name
    nt=m.node_tree; L=nt.links
    b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")
    bc=next((n for n in nt.nodes if n.type=="TEX_IMAGE" and n.image and n.image.name.endswith("_BC")),None)
    mx=next((n for n in nt.nodes if n.label=="LIT"),None)
    if mx is None:
        mx=nt.nodes.new("ShaderNodeMix"); mx.data_type="RGBA"; mx.blend_type="MULTIPLY"; mx.label="LIT"; mx.inputs[0].default_value=1.0
        if bc: L.new(bc.outputs[0],mx.inputs[6])
        L.new(mx.outputs[2],b.inputs["Emission Color"])
    mx.inputs[7].default_value=(*warm,1.0); b.inputs["Emission Strength"].default_value=strength
    return m
def variant_mat(kind,name):
    if kind=="window": return lit_window_material() if name=="Lit" else bpy.data.materials["M_VK_Window"]
    spec=VARIANT_MATS[kind][name]''')

pieces='''
# ================================================================ LANDMARKS: smithy + inn signature pieces
def _tube(k,a,b,r,mi,segs=8):
    a=Vector(a); b=Vector(b); d=b-a
    return _cyl(k,(a+b)/2,r,r,d.length,segs,mi,rot=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4())
def smithy_chimney(k):
    """massive forge stack 2.2 x 1.7 m, 9.2 m tall, open hearth at the front (-Y) with glowing coals under a stone hood"""
    W,D=2.2,1.7
    stone_panel(k,-W/2,W/2,0,0.85,-D/2,D/2,mi=STONE)                       # raised hearth bed
    stone_panel(k,-W/2,-0.55,0.85,2.3,-D/2,D/2,mi=STONE); stone_panel(k,0.55,W/2,0.85,2.3,-D/2,D/2,mi=STONE)
    stone_panel(k,-0.55,0.55,0.85,2.3,0.05,D/2,mi=STONE)                    # back of the fire box
    k.quad([(-0.55,0.049,0.9),(0.55,0.049,0.9),(0.55,0.049,2.25),(-0.55,0.049,2.25)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    k.box((0,-D/2+0.2,2.45),(W+0.3,0.75,0.35),STONE_BLOCK,bevel=0.05)      # hood lintel
    stone_panel(k,-W/2+0.1,W/2-0.1,2.62,4.2,-D/2+0.1,D/2,mi=STONE)
    stone_panel(k,-0.8,0.8,4.2,9.0,-0.65,0.65,mi=STONE)
    for z in (4.2,6.4): k.box((0,0,z),(1.75,1.45,0.22),STONE_BLOCK,bevel=0.04)
    k.box((0,0,9.05),(1.85,1.55,0.25),STONE_BLOCK,bevel=0.05)
    for sx in (-1,1): k.box((sx*0.45,0,9.45),(0.18,0.18,0.55),IRON,bevel=0.02)
    k.box((0,0,9.78),(1.4,1.1,0.08),IRON,bevel=0.02)                       # iron rain hat
    for sx in (-1,1):                                                        # sloped shoulders
        k.box((sx*(W/2-0.25),0,4.35),(0.55,1.5,0.3),STONE_BLOCK,rot=(0,sx*0.5,0),bevel=0.04)
    rnd=random.Random(5)                                                    # coal bed
    for i in range(22):
        c=(rnd.uniform(-0.45,0.45),rnd.uniform(-0.55,0.0),0.9+rnd.uniform(0,0.12))
        _mat(_ico(k,c,rnd.uniform(0.07,0.13),GLOW if i%3 else COAL,sub=1,jit=0.02,seed=i),GLOW if i%3 else COAL,False)
    k.box((0,-0.3,0.88),(1.05,0.6,0.05),GLOW,bevel=0)
    for i in range(3): k.box((-0.3+0.3*i,-D/2-0.05,0.86),(0.06,0.25,0.06),IRON,bevel=0.01)   # fire irons
def smithy_canopy(k):
    """open workshop canopy 6 x 6 m: four heavy posts, knee braces, tie beams, two slate slopes (ridge along X)"""
    H=3.2; R=4.6
    for sx in (-1,1):
        for sy in (-1,1):
            k.box((sx*2.75,sy*2.75,H/2),(0.36,0.36,H),WOOD,bevel=0.05,segs=2)
            k.box((sx*2.75,sy*2.75,0.12),(0.55,0.55,0.24),STONE_BLOCK,bevel=0.04)
    for sy in (-1,1): k.box((0,sy*2.75,H+0.12),(6.2,0.32,0.3),WOOD,bevel=0.04)
    for sx in (-1,1): k.box((sx*2.75,0,H+0.12),(0.3,6.2,0.3),WOOD,bevel=0.04)
    for sx in (-1,1):
        for sy in (-1,1):
            for ax in (0,1):
                d=Vector((0 if ax else -sx,-sy if ax else 0,0))
                a=Vector((sx*2.75,sy*2.75,H-0.75)); b=a+d*0.75+Vector((0,0,0.72))
                _tube(k,a,b,0.07,WOOD,6)
    k.box((0,0,R-0.05),(6.3,0.25,0.25),WOOD,bevel=0.04)
    k.box((0,0,(H+R)/2+0.05),(0.25,0.25,R-H),WOOD,bevel=0.03)
    for sy in (-1,1):
        ang=math.atan2(R-H,3.4)
        c=Vector((0,sy*1.7,(H+R)/2+0.22))
        k.box(tuple(c),(7.0,3.75,0.14),ROOF,rot=(-sy*ang,0,0),bevel=0.02)
        for i in range(7):
            k.box((-3.0+i,sy*1.7,(H+R)/2+0.1),(0.12,3.7,0.12),WOOD,rot=(-sy*ang,0,0),bevel=0.01)
def smith_bellows(k):
    """great leather bellows on a trestle, nozzle to -X, with its rocking lever"""
    for sx in (-0.45,0.45):
        for sy in (-0.3,0.3): k.box((sx,sy,0.35),(0.1,0.1,0.7),WOOD,bevel=0.02)
    k.box((0,0,0.72),(1.2,0.75,0.08),WOOD,bevel=0.02)
    vs=[k.bm.verts.new(p) for p in ((-0.75,0,0.95),(0.6,-0.4,0.95),(0.6,0.4,0.95),(-0.75,0,1.25),(0.6,-0.4,1.35),(0.6,0.4,1.35))]
    for f in ((0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)):
        ff=k.bm.faces.new([vs[i] for i in f]); ff.material_index=HIDE
    k.bm.normal_update(); k.project([f for f in {f for v in vs for f in v.link_faces}],HIDE)
    k.box((-0.05,0,0.93),(1.45,0.85,0.05),WOOD,bevel=0.01); k.box((-0.05,0,1.33),(1.45,0.85,0.05),WOOD,bevel=0.01)
    _tube(k,(-0.75,0,1.08),(-1.25,0,1.02),0.05,IRON,8)
    k.box((0.2,0,1.9),(0.08,0.08,1.1),WOOD,bevel=0.01); _tube(k,(0.2,0,2.4),(1.1,0,2.25),0.035,WOOD,6)
    _tube(k,(0.6,0,1.36),(1.05,0,2.25),0.02,HIDE,4)
def smith_quench(k):
    _cyl(k,(0,0,0.3),0.42,0.38,0.6,16,WOOD)
    for z in (0.12,0.5): _cyl(k,(0,0,z),0.43,0.43,0.05,16,IRON)
    _cyl(k,(0,0,0.56),0.37,0.37,0.02,16,WATER)
    _tube(k,(0.15,-0.1,0.4),(0.35,0.25,0.95),0.02,IRON,6)
def smith_toolwall(k):
    """board of hanging tools for a wall (board plane y=-0.05, facing -Y)"""
    k.box((0,-0.04,1.6),(1.8,0.06,1.0),PLANKS,bevel=0.01)
    for i,x in enumerate((-0.7,-0.35,0.0,0.35,0.7)):
        k.box((x,-0.1,2.0),(0.03,0.1,0.03),WOOD,bevel=0)
        if i%2==0:
            k.box((x,-0.1,1.65),(0.035,0.03,0.6),WOOD,bevel=0); k.box((x,-0.1,1.37),(0.16,0.07,0.08),IRON,bevel=0.01)
        else:
            for sx in (-1,1): k.box((x+sx*0.04,-0.1,1.65),(0.025,0.025,0.65),IRON,rot=(0,sx*0.08,0),bevel=0)
    for x in (-0.55,0.55):
        ring(k,(x,-0.12,1.28),0.06,0.09,0.03,IRON,n=14,axis="Y")
def coal_pile(k):
    rnd=random.Random(8)
    for i in range(26):
        a=rnd.uniform(0,6.28); d=rnd.uniform(0,0.55)
        _mat(_ico(k,(math.cos(a)*d,math.sin(a)*d,0.05+0.3*(1-d/0.6)*rnd.uniform(0.5,1)),rnd.uniform(0.09,0.16),COAL,sub=1,jit=0.02,seed=i),COAL,False)
    k.box((0.75,0.1,0.25),(0.05,0.5,0.5),WOOD,rot=(0,0.3,0),bevel=0.01)
def smith_sign(k):
    """wall bracket (wall at y=0, arm to -Y) with a hanging iron anvil and crossed hammers"""
    k.box((0,-0.05,0),(0.12,0.1,0.5),IRON,bevel=0.01)
    k.box((0,-0.55,0.18),(0.05,1.05,0.05),IRON,bevel=0)
    _tube(k,(0,-0.05,-0.2),(0,-0.7,0.16),0.02,IRON,5)
    for y in (-0.35,-0.85): k.box((0,y,0.02),(0.015,0.015,0.28),IRON,bevel=0)
    k.box((0,-0.6,-0.18),(0.06,0.7,0.14),IRON,bevel=0.01); k.box((0,-0.6,-0.32),(0.06,0.3,0.16),IRON,bevel=0.01)
    k.box((0,-0.6,-0.45),(0.06,0.5,0.1),IRON,bevel=0.01); k.box((0,-0.98,-0.18),(0.06,0.18,0.08),IRON,rot=(0.3,0,0),bevel=0.01)
    for sg in (-1,1):
        k.box((0.02,-0.6,-0.72),(0.03,0.05,0.5),WOOD,rot=(sg*0.7,0,0),bevel=0)
        k.box((0.02,-0.6+sg*0.16,-0.55),(0.05,0.14,0.07),IRON,rot=(sg*0.7,0,0),bevel=0.01)
def inn_sign(k):
    """big inn sign: scrolled iron bracket (wall y=0, arm to -Y, 1.9 m), gilded board with a foaming tankard, lantern"""
    k.box((0,-0.05,0.0),(0.14,0.1,0.8),IRON,bevel=0.01)
    k.box((0,-1.0,0.35),(0.06,1.95,0.06),IRON,bevel=0)
    _tube(k,(0,-0.05,-0.35),(0,-1.2,0.33),0.025,IRON,6)
    for i in range(8):                                                        # scroll
        a=i/7*math.pi*1.4; k.box((0,-0.55-0.18*math.cos(a),0.12+0.15*math.sin(a)),(0.03,0.06,0.06),IRON,bevel=0)
    for y in (-0.6,-1.5): k.box((0,y,0.2),(0.02,0.02,0.3),IRON,bevel=0)
    k.box((0,-1.05,-0.4),(0.1,1.25,0.9),WOOD,bevel=0.03)
    k.box((0,-1.05,-0.4),(0.12,1.35,1.0),BRONZE,bevel=0.02)
    k.box((0,-1.05,-0.4),(0.13,1.18,0.84),PLANKS,bevel=0.01)
    for sx in (-1,1):                                                          # tankard relief on both faces
        x=sx*0.1
        _cyl(k,(x,-1.05,-0.47),0.2,0.22,0.46,14,BRONZE,rot=Matrix.Rotation(math.pi/2,4,"Y"))
        for j in range(5): _mat(_ico(k,(x,-1.05+(j-2)*0.09,-0.2+0.03*(j%2)),0.09,PAPER,sub=1,seed=j),PAPER)
        ring(k,(x,-0.8,-0.47),0.09,0.14,0.05,BRONZE,n=12,axis="X")
    k.box((0,-2.0,0.2),(0.02,0.02,0.3),IRON,bevel=0)                            # lantern at the arm tip
    k.box((0,-2.0,-0.05),(0.22,0.22,0.3),GLOW,bevel=0.01)
    for sx in (-1,1):
        for sy in (-1,1): k.box((sx*0.12,-2.0+sy*0.12,-0.05),(0.03,0.03,0.34),IRON,bevel=0)
    k.box((0,-2.0,0.13),(0.3,0.3,0.05),IRON,bevel=0.01); k.box((0,-2.0,-0.22),(0.28,0.28,0.04),IRON,bevel=0.01)
def ale_cask(k):
    """great ale cask lying on a cradle, brass tap to -Y"""
    for sx in (-0.45,0.45):
        k.box((sx,0,0.2),(0.14,1.1,0.4),WOOD,bevel=0.02)
    rot=Matrix.Rotation(math.pi/2,4,"X")
    _cyl(k,(0,0,0.95),0.62,0.62,0.02,20,WOOD,rot=rot)
    for (y,r0,r1,d) in ((-0.33,0.55,0.62,0.66),(0.33,0.62,0.55,0.66)): _cyl(k,(0,y,0.95),r0,r1,d,20,WOOD,rot=rot)
    for y in (-0.62,-0.2,0.2,0.62): _cyl(k,(0,y,0.95),0.6 if abs(y)<0.5 else 0.56,0.6 if abs(y)<0.5 else 0.56,0.05,20,IRON,rot=rot)
    for y in (-0.66,0.66): _cyl(k,(0,y,0.95),0.5,0.5,0.02,20,ENDGRAIN if "ENDGRAIN" in globals() else WOOD,rot=rot)
    _tube(k,(0,-0.66,0.7),(0,-0.85,0.7),0.035,BRONZE,8); k.box((0,-0.86,0.62),(0.05,0.05,0.14),BRONZE,bevel=0.01)
    _cyl(k,(0,-0.95,0.12),0.14,0.12,0.24,12,WOOD)
def weathervane(k):
    k.box((0,0,0.6),(0.05,0.05,1.2),IRON,bevel=0)
    for ax in ((0.5,0),(0,0.5)): k.box((0,0,0.85),(ax[0]*2+0.03,ax[1]*2+0.03,0.03),IRON,bevel=0)
    k.box((0,0,1.3),(0.9,0.03,0.04),BRONZE,bevel=0)
    k.box((0.45,0,1.3),(0.12,0.03,0.18),BRONZE,rot=(0,0.785,0),bevel=0)
    k.box((-0.4,0,1.35),(0.18,0.025,0.25),BRONZE,bevel=0)
    _mat(_ico(k,(0.02,0,1.55),0.17,BRONZE,scale=(1.3,0.15,1.0),sub=1),BRONZE,False)          # rooster
    k.box((0.2,0,1.72),(0.08,0.025,0.14),BRONZE,bevel=0); k.box((-0.18,0,1.66),(0.14,0.025,0.2),BRONZE,rot=(0,-0.5,0),bevel=0)
def hitch_rail(k):
    for sx in (-1,1): k.box((sx*1.1,0,0.55),(0.14,0.14,1.1),WOOD,bevel=0.02)
    k.box((0,0,1.02),(2.4,0.1,0.1),WOOD,bevel=0.02)
    ring(k,(0,-0.06,0.95),0.05,0.075,0.02,IRON,n=12,axis="Y")
    _cyl(k,(1.6,0.3,0.25),0.3,0.25,0.5,14,WOOD); _cyl(k,(1.6,0.3,0.47),0.26,0.26,0.02,14,WATER)
EXTRA_SPECS+=[("SM_VK_Smithy_Chimney",smithy_chimney,dict(wobble=False,grime=True)),
              ("SM_VK_Smithy_Canopy",smithy_canopy,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_Bellows",smith_bellows,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_QuenchTub",smith_quench,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_ToolWall",smith_toolwall,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_CoalPile",coal_pile,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_SmithSign",smith_sign,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_InnSign",inn_sign,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_AleCask",ale_cask,dict(wobble=False,grime=True)),
              ("SM_VK_Prop_Weathervane",weathervane,dict(wobble=False,grime=False)),
              ("SM_VK_Prop_HitchRail",hitch_rail,dict(wobble=False,grime=True))]

def _sub_origin(origin,lx,ly,rdeg=0.0):
    ox,oy,rz=origin; c,s_=math.cos(rz),math.sin(rz)
    return (ox+lx*c-ly*s_,oy+lx*s_+ly*c,rz+math.radians(rdeg))
def _new_objs(coll,fn):
    before=set(coll.all_objects); fn(); return [o for o in coll.all_objects if o not in before]
def build_smithy(coll,origin,seed=33,light=True):
    """landmark smithy: stone forge house (back), open workshop canopy (front, -Y), 9 m forge stack with a glowing
    hearth, bellows, anvil, quench tub, tool wall, coal, grindstone, weapon racks and a hanging anvil sign"""
    st={"ground":"Stone","plaster":"White","shutter":"Natural","roof":"Slate","stone":"Dark","window":"Lit","seed":seed}
    new=_new_objs(coll,lambda: build_house_v(coll,_sub_origin(origin,0,3),2,1,st,front="DW",back="..",chimney=False))
    def P(n,x,y,z=0.0,r=0.0,sty=None): return place_v(coll,n,x,y,z,r,origin,sty if sty is not None else {})
    P("SM_VK_Smithy_Canopy",0,-3,0,0,{"roof":"Slate"})
    P("SM_VK_Smithy_Chimney",-1.75,-1.05,0,0,{"stone":"Dark"})
    P("SM_VK_Prop_Bellows",0.2,-1.2,0,180)
    P("SM_VK_Prop_Anvil",0.35,-3.3,0,15)
    P("SM_VK_Prop_QuenchTub",1.55,-2.4,0,0)
    P("SM_VK_Prop_ToolWall",1.6,-0.02,0,0)
    P("SM_VK_Prop_CoalPile",-2.1,-3.2,0,0)
    P("SM_VK_Prop_Grindstone",2.2,-4.9,0,90)
    P("SM_VK_Prop_WeaponRack",-2.3,-5.3,0,0)
    P("SM_VK_Prop_Crates",3.9,-5.2,0,25)
    P("SM_VK_Prop_Woodpile",3.6,1.2,0,90)
    P("SM_VK_Prop_SmithSign",2.75,-6.0,2.9,90)
    P("SM_VK_Prop_Lantern",-2.75,-5.8,2.4,0)
    if light:
        L=bpy.data.lights.new("VK_Light_Forge","POINT"); L.energy=260; L.color=(1.0,0.45,0.15); L.shadow_soft_size=0.4
        o=bpy.data.objects.new("VK_Light_Forge",L); coll.objects.link(o)
        x,y,_=_sub_origin(origin,-1.75,-1.6); o.location=(x,y,1.3)
def build_inn(coll,origin,seed=34,garden=True):
    """landmark inn: three-storey timber-framed inn, lit windows, a big iron-bracket sign with a foaming tankard,
    ale cask, door lanterns, flower boxes, weathervane, hitching rail and a beer garden on the +X side"""
    st={"ground":"Stone","plaster":"Ochre","shutter":"Red","roof":"Red","window":"Lit","seed":seed}
    new=_new_objs(coll,lambda: build_house_v(coll,origin,3,3,st,front="WDW",back="W.W",chimney=True))
    def P(n,x,y,z=0.0,r=0.0,sty=None): return place_v(coll,n,x,y,z,r,origin,sty if sty is not None else {})
    P("SM_VK_Prop_InnSign",1.5,-3.3,3.6,0)
    for x in (-1.0,1.0): P("SM_VK_Prop_Lantern",x,-3.3,2.3,0)
    P("SM_VK_Prop_AleCask",-3.3,-4.3,0,90)
    P("SM_VK_Prop_BarrelStack",-4.3,-3.7,0,0)
    P("SM_VK_Prop_HitchRail",3.0,-5.0,0,0)
    zs=[o.matrix_world.to_translation().z+o.dimensions.z for o in new if o.type=="MESH" and "Roof" in o.name]
    top=max(zs) if zs else 10.0
    P("SM_VK_Prop_Weathervane",-2.0,0,top-origin_z(origin),0)
    if garden:
        for i,(x,y) in enumerate(((7.0,-1.2),(9.8,1.3))):
            P("SM_VK_Prop_Table",x,y,0,90)
            for dy in(-0.75,0.75):
                for dx in(-0.6,0.6): P("SM_VK_Prop_Stool",x+dy*1.1,y+dx,0,0)
        P("SM_VK_Prop_BarrelStack",10.3,-2.3,0,0)
        P("SM_VK_Prop_Festoon",7.9,-2.4,3.0,0); P("SM_VK_Prop_Festoon",7.9,2.6,3.0,0)
        for (x,y) in ((5.2,-2.6),(10.8,2.9)): P("SM_VK_Prop_LampPost",x,y,0,0)
        fence_run(coll,(4.8,3.3),(11.4,3.3),origin); fence_run(coll,(11.4,-3.3),(11.4,3.3),origin,gate_at=1)
def origin_z(origin): return 0.0
'''
anchor="def build_barn(coll,origin,n=3,roof=\"Thatch\"):"
assert s.count(anchor)==1; s=s.replace(anchor,pieces+anchor)
open(p,'w',encoding='utf8').write(s)
import ast; ast.parse(s)

# ---- map: smithy inside the gate, inn on the plaza's west side
p='vk_town_map.py'; t=open(p,encoding='utf8').read()
a='''    ox,oy,orz=fp_origin(56,42,2,2,0)
    T.build("blacksmith",build_blacksmith,ox,oy,0)'''
assert t.count(a)==1
t=t.replace(a,'''    # landmarks: the smithy's glowing forge greets you right inside the gate, the inn fronts the plaza
    T.build("smithy",build_smithy,135.0,81.5,-90,seed=33)
    T.build("inn",build_inn,102.0,97.5,90,seed=34)''')
a='''    G.ground[31:36,36:48]=2                           # plaza'''
assert t.count(a)==1
t=t.replace(a,'''    G.ground[31:36,35:48]=2                           # plaza (col 35: in front of the inn)''')
open(p,'w',encoding='utf8').write(t)
print("ok")
