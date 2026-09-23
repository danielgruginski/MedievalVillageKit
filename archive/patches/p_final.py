import os
os.chdir(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code")
def patch(p,rep):
    s=open(p,encoding='utf8').read()
    for a,b in rep:
        assert s.count(a)==1,(p,a[:80],s.count(a)); s=s.replace(a,b)
    open(p,'w',encoding='utf8').write(s); print(p,"ok")

patch('vk_mod_defence.py',[
('''    for x in (-3.2,3.2): P("SM_VK_Prop_LampPost",x,-3.6,0,0)
    bunt=def_pick("SM_VK_Prop_Bunting_6",None)
    if bunt: P(bunt,0,-3.6,2.7,0)
    else: P("SM_VK_Prop_Festoon",0,-3.6,2.85,0)''','''    for x in (-1.8,1.8): P("SM_VK_Prop_LampPost",x,-4.4,0,0)      # clear of the cross plinth, stocks and gate arch
    bunt=def_pick("SM_VK_Prop_Bunting_6",None)
    b_=P(bunt,0,-4.4,2.7,0) if bunt else P("SM_VK_Prop_Festoon",0,-4.4,2.85,0)
    if b_ is not None: b_.scale.x=0.56'''),
])

patch('vk_mat.py',[
('''def apply_pbr_all():
    for mn,kw in MAT_MAP.items():
        m=bpy.data.materials.get(mn)
        if m: pbr_material(m,**kw)''','''def tone_material(name,hsv,img_hint=None):
    """insert (or update) a Hue/Saturation node labelled TONE after a material's first image texture"""
    m=bpy.data.materials.get(name)
    if m is None or not m.use_nodes: return None
    nt=m.node_tree; hs=next((n for n in nt.nodes if n.label=="TONE"),None)
    if hs is None:
        tex=next(n for n in nt.nodes if n.type=="TEX_IMAGE" and n.image and (img_hint is None or img_hint in n.image.name))
        outs=[l.to_socket for l in nt.links if l.from_socket==tex.outputs["Color"]]
        hs=nt.nodes.new("ShaderNodeHueSaturation"); hs.label="TONE"; hs.location=(tex.location.x+280,tex.location.y+200)
        for l in [l for l in nt.links if l.from_socket==tex.outputs["Color"]]: nt.links.remove(l)
        nt.links.new(tex.outputs["Color"],hs.inputs["Color"])
        for s in outs: nt.links.new(hs.outputs[0],s)
    hs.inputs["Hue"].default_value,hs.inputs["Saturation"].default_value,hs.inputs["Value"].default_value=hsv
    return hs
TONE_MAP={"M_VK_Foliage":((0.51,0.6,1.15),"Foliage")}      # kit hedges/ivy/turf toned toward the terrain grass
def apply_pbr_all():
    for mn,kw in MAT_MAP.items():
        m=bpy.data.materials.get(mn)
        if m: pbr_material(m,**kw)
    for mn,(hsv,hint) in TONE_MAP.items(): tone_material(mn,hsv,hint)'''),
])

patch('vk_town_map.py',[
# quarry shoulders one row north, flush with the pit's side walls; stair from the west ridge up to the level-4 hill
('''    L[30:34,11:13]=4; L[30:34,17:19]=4               # hill shoulders that swallow the quarry pit's rock sides''',
 '''    L[31:34,12:14]=4; L[31:34,16:18]=4               # hill shoulders flush with the quarry pit's side walls (row 30 stays level 2)'''),
('''    G.ramp[33,9]=1; G.stair[33,9]=True''','''    G.ramp[33,9]=1; G.stair[33,9]=True
    G.ramp[36,10]=2; G.stair[36,10]=True              # west ridge (level 3) up to the quarry hill (level 4, crane)'''),
('''    T.build("quarry",build_quarry_yard,45,97.5,0,seed=5,standin=False,allow_higher=True,level=2)''',
 '''    new=T.build("quarry",build_quarry_yard,45,97.5,0,seed=5,standin=False,allow_higher=True,level=2) or []
    # keep the pit mouth (x 43.6-46.4) open: banker and block pile go to the yard on the lane; the lean-to would sit in the hill
    for o in new:
        if o.name not in bpy.data.objects: continue
        b=base_name(o); x,y=o.location.x-TOWN_ORIGIN[0],o.location.y
        if "LeanTo" in b: bpy.data.objects.remove(o)
        elif b=="SM_VK_Prop_Banker": o.location.x=TOWN_ORIGIN[0]+41.5; o.location.y=91.0
        elif b.startswith("SM_VK_Pile_Stone") and 42.5<x<48.5 and 92.0<y<95.5: o.location.x=TOWN_ORIGIN[0]+48.5; o.location.y=91.0'''),
# clash test can ignore the object itself
('''    def clashes(s,objs,tag,shrink=0.12):
        out=[]
        for o in objs:
            if o.type!="MESH": continue
            a=s.obj_aabb(o); seen=set()''','''    def clashes(s,objs,tag,shrink=0.12):
        out=[]
        for o in objs:
            if o.type!="MESH": continue
            a=s.obj_aabb(o); seen={o.name}'''),
# door clear: porch-aware width, clash-checked slide, weeds off door steps
('''def town_door_clear(T,depth=2.3,half=0.65):
    """keep a 1.3 m wide x ~2 m deep corridor clear in front of every *_Door module: slide props, bushes and rocks sideways"""
    objs=list(T.coll.all_objects)
    doors=[o for o in objs if o.type=="MESH" and is_door(o)]''','''def town_door_clear(T,depth=2.3,half=0.65):
    """keep a 1.3 m wide x ~2 m deep corridor clear in front of every *_Door module (porch width when the door has a
    porch): slide props, bushes and rocks sideways to a spot that clashes with nothing, else drop them"""
    objs=list(T.coll.all_objects)
    doors=[o for o in objs if o.type=="MESH" and is_door(o)]
    porches=[o for o in objs if o.type=="MESH" and "Porch" in o.name]
    dhalf={}
    for d in doors:
        dhalf[d.name]=half
        for p in porches:
            if abs(p.location.x-d.location.x)<1.0 and abs(p.location.y-d.location.y)<1.8 and abs(p.location.z-d.location.z)<0.5: dhalf[d.name]=1.6; break
    # weed strips laid along a door module grow on its step: remove them
    dkeys={(round(d.location.x,1),round(d.location.y,1),round(d.location.z,1)) for d in doors}
    weeds=[o for o in objs if "Deco_Weeds" in o.name and (round(o.location.x,1),round(o.location.y,1),round(o.location.z,1)) in dkeys]
    for o in weeds: bpy.data.objects.remove(o)
    objs=[o for o in objs if o.name in bpy.data.objects]
    T.log.append(("door weeds removed",len(weeds)))'''),
('''    G=T.G; moved=[]
    for d in doors:
        i,j=door_front_cell(T,d)
        if 0<=i<G.W and 0<=j<G.H and G.ground[j,i]==0 and not G.water[j,i]: G.wear[j,i]=max(G.wear[j,i],120)
    for o in movable:
        for it in range(3):
            hit=None''','''    G=T.G; moved=[]; dropped=[]
    for d in doors:
        i,j=door_front_cell(T,d)
        if 0<=i<G.W and 0<=j<G.H and G.ground[j,i]==0 and not G.water[j,i]: G.wear[j,i]=max(G.wear[j,i],90)
    for o in movable:
        if o.name not in bpy.data.objects: continue
        for it in range(3):
            hit=None'''),
('''                u0=min(p[0] for p in P); u1=max(p[0] for p in P); v0=min(p[1] for p in P); v1=max(p[1] for p in P)
                if u1>-half and u0<half and v0<-0.2 and v1>-depth:
                    sh=(half-u0+0.1) if (half-u0)<(u1+half) else -(u1+half+0.1)
                    hit=(c*sh,s*sh); break
            if hit is None: break
            o.location.x+=hit[0]; o.location.y+=hit[1]; moved.append(o.name)
    T.log.append(("door_clear moved",len(moved),moved[:12]))
    return moved''','''                u0=min(p[0] for p in P); u1=max(p[0] for p in P); v0=min(p[1] for p in P); v1=max(p[1] for p in P)
                hw=dhalf[d.name]
                if u1>-hw and u0<hw and v0<-0.2 and v1>-depth:
                    a_=hw-u0+0.25; b_=-(u1+hw+0.25)
                    hit=[(c*sh,s*sh) for sh in sorted((a_,b_),key=abs)]; break
            if hit is None: break
            x0,y0=o.location.x,o.location.y; ok_=False
            for (dx,dy) in hit:
                o.location.x=x0+dx; o.location.y=y0+dy
                if not [h for h in T.clashes([o],"door_clear",shrink=0.05) if "Weeds" not in h[1] and "LipGrass" not in h[1]]: ok_=True; break
            if not ok_:
                dropped.append(o.name); bpy.data.objects.remove(o); break
            moved.append(o.name)
    T.log.append(("door_clear moved",len(moved),moved[:12])); T.log.append(("door_clear dropped",len(dropped),dropped[:12]))
    return moved'''),
# levels pass: water counts again, except for pieces that are meant to stand in it
('''            if G.level[j,i]!=k or G.ramp[j,i]: return False''','''            if G.level[j,i]!=k or G.ramp[j,i]: return False
            if G.water[j,i] and not wet_ok: return False'''),
('''    def ok(o,dx,dy,k):''','''    WET=("Lavoir","Wash","Pier","Quay","Jetty","Sluice","Wheel","Mooring","Buoy")
    def ok(o,dx,dy,k):
        wet_ok=any(w in o.name for w in WET)'''),
# softer worn pads
('''                if 0<=i<G.W and 0<=j<G.H and G.ground[j,i]==0: G.wear[j,i]=max(G.wear[j,i],150)''',
 '''                if 0<=i<G.W and 0<=j<G.H and G.ground[j,i]==0: G.wear[j,i]=max(G.wear[j,i],100)'''),
# scatter: more lowland trees, forest-edge fringe, no trees at the map border or on ramp/stair tops,
# bushes and gardens kept off street fronts
('''    no_willow=np.zeros((G.H,G.W),bool)''','''    ramp_top=np.zeros((G.H,G.W),bool)
    for (j,i) in zip(*np.nonzero(G.ramp)):
        di,dj=((0,1),(1,0),(0,-1),(-1,0))[G.ramp[j,i]-1]
        for s_ in (1,2):
            ii,jj=i+di*s_,j+dj*s_
            if 0<=ii<G.W and 0<=jj<G.H: ramp_top[jj,ii]=True
    high=(G.level>=3)
    def tree_ok(i,j): return 1<=i<G.W-1 and 1<=j<G.H-1 and not near(ramp_top,i,j,1)
    no_willow=np.zeros((G.H,G.W),bool)'''),
('''                if not T.near_occ(i,j,1):
                    for _ in range(2 if rng.random()<0.55 else 1):''','''                if not T.near_occ(i,j,1) and tree_ok(i,j):
                    for _ in range(2 if rng.random()<0.55 else 1):'''),
('''                if T.near_bld(i,j,1) and not near(roads,i,j,0) and rng.random()<0.3:
                    G.ground[j,i]=1; G.wear[j,i]=0; T.occ[j,i]=-2
                    T.P(rng.choice(["SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Lavender","SM_VK_Crop_Cabbage"]),3*i+1.5,3*j+1.5,rng.choice((0,90,180,270)),z=z,scale=0.8)
                    continue
                r_=rng.random()
                if r_<0.08 and not T.near_occ(i,j,1) and not near(roads,i,j,1):
                    p=safe(i,j,1.0)
                    if p: put_tree(rng.choice(["SM_VK_Tree_Blossom","SM_VK_Tree_Apple"]),p[0],p[1],z)
                elif r_<0.16:''','''                if T.near_bld(i,j,1) and not near(roads,i,j,1) and rng.random()<0.2:
                    G.ground[j,i]=1; G.wear[j,i]=0; T.occ[j,i]=-2
                    T.P(rng.choice(["SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot"]),3*i+1.5,3*j+1.5,rng.choice((0,90,180,270)),z=z,scale=0.8)
                    continue
                r_=rng.random()
                if r_<0.14 and not T.near_bld(i,j,1) and not roads[j,i]:
                    p=safe(i,j,1.0)
                    if p: put_tree(rng.choice(["SM_VK_Tree_Blossom","SM_VK_Tree_Apple"]),p[0],p[1],z)
                elif r_<0.22 and not near(roads,i,j,1):'''),
('''                        if pick=="SM_VK_Tree_Willow":
                            if not near(no_willow,i,j,2): put_tree(pick,p[0],p[1],z)''','''                        if pick=="SM_VK_Tree_Willow":
                            if not near(no_willow,i,j,2) and tree_ok(i,j): put_tree(pick,p[0],p[1],z)'''),
('''                r_=rng.random()
                if r_<0.07:
                    p=safe(i,j,1.2)
                    name=rng.choice(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Apple","SM_VK_Tree_Birch","SM_VK_Bush_Large"])
                    if p and not T.near_occ(i,j,2 if name in big else 1) and not near(roads,i,j,0 if name=="SM_VK_Bush_Large" else 1):
                        put_tree(name,p[0],p[1],z,scale=rng.uniform(0.85,1.1))
                elif r_<0.2:''','''                r_=rng.random(); pt=0.3 if near(high,i,j,2) else 0.13        # denser fringe at the foot of the ridges
                if r_<pt:
                    p=safe(i,j,1.2)
                    name=rng.choice(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Apple","SM_VK_Tree_Birch","SM_VK_Bush_Large"])
                    if p and tree_ok(i,j) and not T.near_bld(i,j,2 if name in big else 1) and not roads[j,i]:
                        put_tree(name,p[0],p[1],z,scale=rng.uniform(0.85,1.1))
                elif r_<pt+0.13 and not near(roads,i,j,1):'''),
])
