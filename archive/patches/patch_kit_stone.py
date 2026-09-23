import bpy, re
t=bpy.data.texts["vk_helpers"]; s=open(SRC_HELPERS,encoding="utf8").read()
def rep(a,b,count=1):
    global s
    assert s.count(a)>=1, "missing: "+a[:80]
    if count==1: assert s.count(a)==1, "ambiguous: "+a[:80]
    s=s.replace(a,b)

# A. slots
rep("MUSH_GLOW=range(45)","MUSH_GLOW,STONE_BLOCK,FIELDSTONE,WATTLE,HIDE,PIGSKIN,COAL,NET=range(52)")
# B. kit_mats tail
rep('tex_mat("M_VK_MushGlow",None,0.4,flat=(0.35,0.85,1.0),emit=(0.25,0.8,1.0))]',
    'tex_mat("M_VK_MushGlow",None,0.4,flat=(0.35,0.85,1.0),emit=(0.25,0.8,1.0)),\n'
    '            tex_mat("M_VK_StoneBlock","T_VK_StoneBlock"), tex_mat("M_VK_FieldStone","T_VK_FieldStone"), tex_mat("M_VK_Wattle","T_VK_Wattle"),\n'
    '            tex_mat("M_VK_Hide",None,0.8,flat=(0.50,0.33,0.20)), tex_mat("M_VK_Pigskin",None,0.7,flat=(0.90,0.62,0.56)),\n'
    '            tex_mat("M_VK_Coal",None,0.95,flat=(0.045,0.043,0.050)), bpy.data.materials["M_VK_Net"]]')
# C. tiles
rep("TILE={33:1.2,","TILE={45:1.2,46:3.0,47:1.0,51:1.0,33:1.2,")
rep("23:2.0,24:2.5,","23:2.0,24:3.0,")
# D. project
rep("    def project(s,faces,mi,axes=None,sizes=None,offset=(0.0,0.0)):\n        t=TILE.get(mi,1.0)",
    "    def project(s,faces,mi,axes=None,sizes=None,offset=(0.0,0.0),tile=None):\n        t=tile or TILE.get(mi,1.0)")
rep("            f.material_index=mi\n            n=f.normal\n",
    "            f.material_index=mi\n            n=f.normal\n            tt=t\n"
    "            if mi==STONE and abs(n.z)>0.7: f.material_index=STONE_BLOCK; tt=TILE[STONE_BLOCK]\n")
rep("                p=l.vert.co; l[s.uv].uv=(p.dot(U)/t+offset[0],p.dot(V)/t+offset[1])",
    "                p=l.vert.co; l[s.uv].uv=(p.dot(U)/tt+offset[0],p.dot(V)/tt+offset[1])")
# E. box
rep("    def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0,xform=None):\n",
    "    def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0,xform=None,tile=None):\n"
    "        if mi==STONE and bevel>0 and (sorted(size)[1]<0.7 or min(size)<0.25): mi=STONE_BLOCK\n")
rep("        s.project(faces,mi,axes,size,offset=((h%997)/997.0,(h//997%991)/991.0))",
    "        off=(0.0,0.0) if (mi in (STONE,ASHLAR,FIELDSTONE) and bevel==0) else ((h%997)/997.0,(h//997%991)/991.0)\n"
    "        s.project(faces,mi,axes,size,offset=off,tile=tile)")
# F. chimney texture scale
rep("k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STONE,bevel=0.06,segs=2)",
    "k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STONE,bevel=0.06,segs=2,tile=1.8)",count=2)
# G. ROCK -> STONE_BLOCK for built stonework
lines=s.split("\n")
for i,l in enumerate(lines):
    if "=range(" in l: continue
    lines[i]=re.sub(r"\bROCK\b","STONE_BLOCK",l)
s="\n".join(lines)
# H. aligned wall rocks
i0=s.index("def wall_rocks(k,x0,x1,z0,z1,face=-0.25,n=5,seed=0,avoid=()):")
i1=s.index("def wall_stone_plain(k):",i0)
s=s[:i0]+'''_STONE_META=None
def stone_meta():
    global _STONE_META
    if _STONE_META is None:
        import json
        img=bpy.data.images.get("T_VK_Stone_BC")
        p=os.path.join(os.path.dirname(bpy.path.abspath(img.filepath_raw)),"T_VK_Stone_stones.json")
        try: _STONE_META=json.load(open(p))
        except Exception: _STONE_META=[]
    return _STONE_META
def wall_rocks(k,x0,x1,z0,z1,face=-0.25,n=5,seed=0,avoid=()):
    """pop-out stones aligned with painted stones of T_VK_Stone (module at UV offset 0, facing -Y)"""
    rnd=random.Random(seed); meta=list(stone_meta()); rnd.shuffle(meta); placed=0
    for st in meta:
        if placed>=n: break
        for zoff in (0.0,3.0):
            x=((-3.0*st["u"]+1.5)%3.0)-1.5; z=3.0*st["v"]+zoff; w,h=st["w"],st["h"]
            if not (x0+0.05<x-w/2 and x+w/2<x1-0.05 and z0+0.02<z-h/2 and z+h/2<z1-0.05): continue
            if any(ax0-0.1<x+w/2 and x-w/2<ax1+0.1 and az0-0.1<z+h/2 and z-h/2<az1+0.1 for (ax0,ax1,az0,az1) in avoid): continue
            d=rnd.uniform(0.06,0.10)
            rock(k,(x,face-d/2+0.03,z),(0.9*w,d,0.9*h),seed=seed*31+placed,tilt=0.02,segs=1)
            placed+=1; break
'''+s[i1:]
rep("    wall_rocks(k,-1.5,1.5,0.5,H1,n=6,seed=3)","    wall_rocks(k,-1.5,1.5,0.5,H1,n=2,seed=3)")
rep("    wall_rocks(k,-1.5,1.5,0.5,H1,n=4,seed=5,avoid=","    wall_rocks(k,-1.5,1.5,0.5,H1,n=1,seed=5,avoid=")
rep("    wall_rocks(k,-1.5,1.5,0.5,H1,n=3,seed=7,avoid=","    wall_rocks(k,-1.5,1.5,0.5,H1,n=1,seed=7,avoid=")
rep("    wall_rocks(k,-L/2,L/2,0.1,h,face=-0.25,n=5,seed=seed)\n","    wall_rocks(k,-L/2,L/2,0.1,h,face=-0.25,n=2,seed=seed)\n")
rep("sub=Kit(); wall_rocks(sub,-L/2,L/2,0.1,h,face=-0.25,n=5,seed=seed+1)","sub=Kit(); wall_rocks(sub,-L/2,L/2,0.1,h,face=-0.25,n=2,seed=seed+1)")
# I. variants
rep(''' "roof":{"Red":None,"Blue":("T_VK_RoofBlue",None),"Green":("T_VK_RoofGreen",None),"Thatch":("T_VK_Thatch",None)},''',
    ''' "roof":{"Red":None,"Blue":("T_VK_RoofBlue",None),"Green":("T_VK_RoofGreen",None),"Thatch":("T_VK_Thatch",None),"Slate":("T_VK_RoofSlate",None),"Shingle":("T_VK_RoofShingle",None)},''')
rep(''' "plaster":{"Cream":None,"White":("T_VK_Plaster",(1.10,1.12,1.18)),"Ochre":("T_VK_Plaster",(1.05,0.86,0.58)),"Rose":("T_VK_Plaster",(1.05,0.84,0.78))},''',
    ''' "plaster":{"Cream":None,"White":("T_VK_Plaster",(1.10,1.12,1.18)),"Ochre":("T_VK_Plaster",(1.05,0.86,0.58)),"Rose":("T_VK_Plaster",(1.05,0.84,0.78)),
            "Daub":("T_VK_Plaster",(0.80,0.65,0.47)),"Sage":("T_VK_Plaster",(0.90,1.02,0.84)),"Sky":("T_VK_Plaster",(0.88,0.97,1.12))},''')
rep(''' "cloth":{"Red":None,"Blue":(None,(0.12,0.22,0.55)),"Green":(None,(0.15,0.40,0.12)),"Yellow":(None,(0.85,0.62,0.12))},''',
    ''' "cloth":{"Red":None,"Blue":(None,(0.12,0.22,0.55)),"Green":(None,(0.15,0.40,0.12)),"Yellow":(None,(0.85,0.62,0.12)),"Purple":(None,(0.35,0.12,0.45)),"White":(None,(0.92,0.90,0.85))},
 "stone":{"Rubble":None,"Field":("T_VK_FieldStone",None),"Warm":("T_VK_Stone",(1.04,1.00,0.94)),"Cool":("T_VK_Stone",(0.95,0.98,1.03)),"Dark":("T_VK_Stone",(0.88,0.88,0.88))},''')
rep('SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A}','SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A,"stone":STONE}')
rep('''base={"plaster":"M_VK_Plaster","shutter":"M_VK_Shutter_Teal","roof":"M_VK_RoofRed","cloth":"M_VK_Cloth_Red"}[kind]''',
    '''base={"plaster":"M_VK_Plaster","shutter":"M_VK_Shutter_Teal","roof":"M_VK_RoofRed","cloth":"M_VK_Cloth_Red","stone":"M_VK_Stone"}[kind]''')
t.clear(); t.write(s)

# J. MAT_MAP
t2=bpy.data.texts["vk_mat"]; m=t2.as_string()
a=' "M_VK_Stone":dict(prefix="T_VK_Stone",nstr=1.1),'
assert a in m or "M_VK_StoneBlock" in m
m=m.replace(a,''' "M_VK_Stone":dict(prefix="T_VK_Stone",nstr=1.0),
 "M_VK_StoneBlock":dict(prefix="T_VK_StoneBlock",nstr=1.0),
 "M_VK_FieldStone":dict(prefix="T_VK_FieldStone",nstr=1.1),
 "M_VK_Stone_Field":dict(prefix="T_VK_FieldStone",nstr=1.1),
 "M_VK_Stone_Warm":dict(prefix="T_VK_Stone",tint=(1.04,1.0,0.94),nstr=1.0),
 "M_VK_Stone_Cool":dict(prefix="T_VK_Stone",tint=(0.95,0.98,1.03),nstr=1.0),
 "M_VK_Stone_Dark":dict(prefix="T_VK_Stone",tint=(0.88,0.88,0.88),nstr=1.0),
 "M_VK_Wattle":dict(prefix="T_VK_Wattle",nstr=1.1,spec=0.15),
 "M_VK_Roof_Slate":dict(prefix="T_VK_RoofSlate",nstr=1.0,rough_mul=1.15,spec=0.2),
 "M_VK_Roof_Shingle":dict(prefix="T_VK_RoofShingle",nstr=1.0,rough_mul=1.2,spec=0.15),''')
t2.clear(); t2.write(m)
print("patched")
