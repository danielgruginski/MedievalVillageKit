# Main session: Blender MCP calls  (part 1/2)
# Chronological log, extracted from the session transcript. NOT meant to be run as a whole:
# each block was one call; later blocks often supersede earlier ones. The maintained code lives in src/.

# ==============================================================================================================
# [0001] 2026-09-23 01:15:06  blender  ok
# ==============================================================================================================
import bpy
print(bpy.app.version_string, bpy.context.scene.render.engine, [s.name for s in bpy.data.scenes], bpy.data.filepath)
# ---- result ----
# {"result":"Code executed successfully: 4.4.3 BLENDER_EEVEE_NEXT ['Scene', 'SpriteRig'] E:\\Unity\\Projects\\Cube Sorter\\Art\\WallKit\\WallKit.blend\n
# "}

# ==============================================================================================================
# [0002] 2026-09-23 01:15:28  blender  ok
# ==============================================================================================================
import bpy
helpers = r'''
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise
SC = bpy.data.scenes["MedievalColony"]
def col(name, parent=None):
    if name in bpy.data.collections: return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    (parent or SC.collection).children.link(c)
    return c
def mat(name, color, rough=0.8, metal=0.0, emit=None, emit_str=0.0, alpha=1.0, trans=0.0):
    m = bpy.data.materials.get("MC_"+name)
    if m: return m
    m = bpy.data.materials.new("MC_"+name); m.use_nodes=True
    b = next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color,1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value=(*emit,1); b.inputs["Emission Strength"].default_value=emit_str
    if trans: b.inputs["Transmission Weight"].default_value = trans
    if alpha<1: b.inputs["Alpha"].default_value = alpha
    m.diffuse_color=(*color,1)
    return m
def obj_from_bm(name, bm, material=None, collection=None, loc=(0,0,0), rot=(0,0,0), smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    (collection or SC.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    if material:
        mats = material if isinstance(material,(list,tuple)) else [material]
        for mm in mats: me.materials.append(mm)
    for p in me.polygons: p.use_smooth = smooth
    return o
def box(bm, center, size, rot_z=0.0, mat_index=0):
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r["verts"]
    M = Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z,4,"Z") @ Matrix.Diagonal((*size,1))
    bmesh.ops.transform(bm, matrix=M, verts=vs)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mat_index
    return vs
def cyl(bm, center, r1, r2, depth, segs=8, rot=None, mat_index=0):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
    vs = res["verts"]
    M = Matrix.Translation(Vector(center)) @ (rot if rot else Matrix.Identity(4))
    bmesh.ops.transform(bm, matrix=M, verts=vs)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mat_index
    return vs
def ico(bm, center, radius, sub=1, scale=(1,1,1), jitter=0.0, mat_index=0, seed=0):
    res = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=radius)
    vs = res["verts"]
    rnd = random.Random(seed)
    for v in vs:
        v.co = Vector((v.co.x*scale[0], v.co.y*scale[1], v.co.z*scale[2]))
        if jitter: v.co += Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1)))*jitter
        v.co += Vector(center)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mat_index
    return vs
def prism_roof(bm, center, w, d, h, over=0.15, thick=0.12, rot_z=0.0, mat_index=0):
    # gable roof along X, ridge height h above center
    x=w/2+over; y=d/2+over
    pts=[(-x,-y,0),(x,-y,0),(x,0,h),(-x,0,h),(-x,y,0),(x,y,0)]
    M = Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z,4,"Z")
    vv=[bm.verts.new(M@Vector(p)) for p in pts]
    vb=[bm.verts.new(M@Vector((p[0],p[1],p[2]-thick))) for p in pts]
    faces=[(0,1,2,3),(3,2,5,4)]
    for f in faces:
        bm.faces.new([vv[i] for i in f]).material_index=mat_index
        bm.faces.new([vb[i] for i in reversed(f)]).material_index=mat_index
    for a,b in [(0,1),(1,2),(2,5),(5,4),(4,3),(3,0)]:
        bm.faces.new([vv[a],vb[a],vb[b],vv[b]]).material_index=mat_index
def ground_h(x,y):
    return SC["hfunc"](x,y) if False else _gh(x,y)
'''
t = bpy.data.texts.get("mc_helpers") or bpy.data.texts.new("mc_helpers")
t.clear(); t.write(helpers)
sc = bpy.data.scenes.get("MedievalColony") or bpy.data.scenes.new("MedievalColony")
bpy.context.window.scene = sc
print("ok", sc.render.engine)
# ---- result ----
# {"result":"Code executed successfully: ok BLENDER_EEVEE_NEXT\n"}

# ==============================================================================================================
# [0003] 2026-09-23 01:15:42  blender  ok
# ==============================================================================================================
import bpy
t = bpy.data.texts["mc_helpers"]
s = t.as_string().replace('''def ground_h(x,y):
    return SC["hfunc"](x,y) if False else _gh(x,y)
''','''HALF=30.0
def river_y(x): return -15.0 + 3.0*math.sin(x*0.12) + 1.2*math.sin(x*0.31+1.0)
def smooth(a,b,x):
    t=max(0.0,min(1.0,(x-a)/(b-a))); return t*t*(3-2*t)
def ground_h(x,y):
    n = noise.noise(Vector((x*0.06,y*0.06,0.3)))
    n2 = noise.noise(Vector((x*0.18,y*0.18,2.1)))
    h = 0.35*n + 0.12*n2
    # hills to the north / north-east
    hill = smooth(8,26,y+0.35*x) 
    h += hill*(3.5 + 2.5*noise.noise(Vector((x*0.09,y*0.09,5.0))))
    # flatten village core
    d = math.hypot(x+1,y-1)
    h *= 0.25 + 0.75*smooth(7,15,d)
    # river carve
    dr = abs(y-river_y(x))
    h = h*smooth(2.5,6,dr) - 1.1*(1-smooth(1.5,3.2,dr))
    return h
''')
t.clear(); t.write(s)
exec(s)
print(ground_h(0,0), ground_h(0,-15), ground_h(20,25))
# ---- result ----
# {"result":"Code executed successfully: 0.0013399353623390197 -1.1 2.609760165810585\n"}

# ==============================================================================================================
# [0004] 2026-09-23 01:16:10  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
PATHS=[[(-1,1),(0,-8),(0.5,-15),(1,-24),(2,-30)],
       [(-1,1),(9,3),(17,3.5),(24,5)],
       [(-1,1),(-6,8),(-11,15),(-13,19)],
       [(-1,1),(-12,-1),(-20,-3),(-30,-3.5)]]
def seg_d(p,a,b):
    p=Vector(p);a=Vector(a);b=Vector(b);ab=b-a
    t=max(0,min(1,(p-a).dot(ab)/ab.length_squared)); return (p-(a+ab*t)).length
def path_d(x,y):
    return min(seg_d((x,y),pl[i],pl[i+1]) for pl in PATHS for i in range(len(pl)-1))
t=bpy.data.texts["mc_helpers"]
if "PATHS" not in t.as_string():
    t.write("\nPATHS="+repr(PATHS)+"\n"+'''def seg_d(p,a,b):
    p=Vector(p);a=Vector(a);b=Vector(b);ab=b-a
    t=max(0,min(1,(p-a).dot(ab)/ab.length_squared)); return (p-(a+ab*t)).length
def path_d(x,y):
    return min(seg_d((x,y),pl[i],pl[i+1]) for pl in PATHS for i in range(len(pl)-1))
def place_z(x,y): return ground_h(x,y)
''')
C=col("Terrain")
N=150; step=2*HALF/N
bm=bmesh.new()
grid=[[bm.verts.new((-HALF+i*step,-HALF+j*step,ground_h(-HALF+i*step,-HALF+j*step))) for j in range(N+1)] for i in range(N+1)]
bm.verts.ensure_lookup_table()
faces=[]
for i in range(N):
    for j in range(N):
        faces.append(bm.faces.new((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1])))
# skirt
BOT=-5.0
def edge_loop():
    L=[grid[i][0] for i in range(N+1)]+[grid[N][j] for j in range(1,N+1)]+[grid[i][N] for i in range(N-1,-1,-1)]+[grid[0][j] for j in range(N-1,0,-1)]
    return L
loop=edge_loop()
bots=[bm.verts.new((v.co.x,v.co.y,BOT)) for v in loop]
skirt=[]
for k in range(len(loop)):
    a,b=loop[k],loop[(k+1)%len(loop)]; ba,bb=bots[k],bots[(k+1)%len(loop)]
    f=bm.faces.new((b,a,ba,bb)); f.material_index=1; skirt.append(f)
bm.faces.new(list(reversed(bots))).material_index=1
bm.normal_update()
# vertex colors
cl=bm.loops.layers.color.new("Col")
rnd=random.Random(3)
grass1=Vector((0.23,0.42,0.10));grass2=Vector((0.40,0.52,0.14));dry=Vector((0.55,0.52,0.22))
dirt=Vector((0.40,0.28,0.15));sand=Vector((0.62,0.55,0.38));rock=Vector((0.38,0.37,0.35));mud=Vector((0.22,0.17,0.11))
vcol={}
for v in bm.verts:
    x,y,z=v.co
    if z<=BOT+0.01: continue
    n=noise.noise(Vector((x*0.15,y*0.15,7.7)))*0.5+0.5
    n2=noise.noise(Vector((x*0.6,y*0.6,1.3)))*0.5+0.5
    c=grass1.lerp(grass2,n); c=c.lerp(dry,max(0,n2-0.7)*1.5)
    slope=1-(v.normal.z if v.normal.length>0 else 1)
    if slope>0.25: c=c.lerp(rock,min(1,(slope-0.25)*4))
    dr=abs(y-river_y(x))
    if dr<4.5: c=c.lerp(sand,1-smooth(2.5,4.5,dr))
    if dr<2.2: c=c.lerp(mud,1-smooth(1.2,2.2,dr))
    pd=path_d(x,y); w=1.1+0.3*n2
    if pd<w+0.6 and dr>2.0: c=c.lerp(dirt,1-smooth(w-0.3,w+0.6,pd))
    # village square
    dc=math.hypot(x+1,y-1)
    if dc<5: c=c.lerp(dirt*1.1,1-smooth(3.5,5,dc+1.5*n2))
    vcol[v.index]=c
for f in bm.faces:
    for l in f.loops:
        if f.material_index==1:
            z=l.vert.co.z
            band=0.5+0.5*math.sin(z*2.2+noise.noise(Vector((l.vert.co.x*0.3,l.vert.co.y*0.3,0)))*2)
            c=Vector((0.30,0.20,0.12)).lerp(Vector((0.42,0.30,0.18)),band)
            if z<-3.2: c=Vector((0.33,0.32,0.30))*(0.8+0.3*band)
            l[cl]=(*c,1)
        else:
            c=vcol[l.vert.index]; l[cl]=(*c,1)
terr_m=bpy.data.materials.get("MC_TerrainVC") or bpy.data.materials.new("MC_TerrainVC")
terr_m.use_nodes=True
nt=terr_m.node_tree
b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Roughness"].default_value=0.95
a=next((n for n in nt.nodes if n.type=="ATTRIBUTE"),None) or nt.nodes.new("ShaderNodeAttribute")
a.attribute_name="Col"; a.location=(-300,300)
nt.links.new(a.outputs["Color"],b.inputs["Base Color"])
o=obj_from_bm("Terrain",bm,[terr_m,terr_m],C)
print(len(o.data.vertices))
# ---- result ----
# {"result":"Code executed successfully: 23401\n"}

# ==============================================================================================================
# [0005] 2026-09-23 01:16:27  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Terrain")
# water: strip following river, thin slab
wm=mat("Water",(0.10,0.30,0.38),rough=0.05)
b=next(n for n in wm.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
b.inputs["Alpha"].default_value=0.8; wm.blend_method="BLEND" if hasattr(wm,"blend_method") else None
try: wm.surface_render_method="BLENDED"
except: pass
bm=bmesh.new()
WZ=-0.55; N=80
tops=[];bots=[]
for i in range(N+1):
    x=-HALF+i*2*HALF/N; yc=river_y(x)
    row=[bm.verts.new((x,yc-3.6,WZ)),bm.verts.new((x,yc+3.6,WZ))]
    tops.append(row)
for i in range(N):
    bm.faces.new((tops[i][0],tops[i+1][0],tops[i+1][1],tops[i][1]))
# end caps down to base so river cutaway shows water at diorama edges
for idx in (0,N):
    a,bb=tops[idx]
    a2=bm.verts.new((a.co.x,a.co.y,-1.25)); b2=bm.verts.new((bb.co.x,bb.co.y,-1.25))
    f=bm.faces.new((a,bb,b2,a2) if idx==0 else (bb,a,a2,b2))
wo=obj_from_bm("River",bm,wm,C)
# world + sun
w=SC.world or bpy.data.worlds.new("MC_World"); SC.world=w; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=="BACKGROUND")
sky=next((n for n in w.node_tree.nodes if n.type=="TEX_SKY"),None) or w.node_tree.nodes.new("ShaderNodeTexSky")
print([i.identifier for i in sky.bl_rna.properties["sky_type"].enum_items])
w.node_tree.links.new(sky.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.35
sky.sun_elevation=math.radians(28); sky.sun_rotation=math.radians(215)
LC=col("Lighting")
sd=bpy.data.lights.get("MC_Sun") or bpy.data.lights.new("MC_Sun","SUN")
sd.energy=4.0; sd.color=(1.0,0.88,0.72); sd.angle=math.radians(2.5)
so=bpy.data.objects.get("Sun") or bpy.data.objects.new("Sun",sd)
if so.name not in LC.objects: LC.objects.link(so)
so.rotation_euler=(math.radians(58),0,math.radians(215-180+90))
cd=bpy.data.cameras.get("MC_Cam") or bpy.data.cameras.new("MC_Cam"); cd.lens=50
cam=bpy.data.objects.get("Camera_Hero") or bpy.data.objects.new("Camera_Hero",cd)
if cam.name not in LC.objects: LC.objects.link(cam)
cam.location=(52,-58,42)
d=Vector((0,0,-1))-cam.location
cam.rotation_euler=d.to_track_quat("-Z","Y").to_euler()
SC.camera=cam
SC.render.resolution_x=1920; SC.render.resolution_y=1080
print("done")
# ---- result ----
# {"result":"Code executed successfully: ['PREETHAM', 'HOSEK_WILKIE', 'NISHITA']\ndone\n"}

# ==============================================================================================================
# [0006] 2026-09-23 01:16:32  blender  ok
# ==============================================================================================================
import bpy
for area in bpy.context.window.screen.areas:
    if area.type=="VIEW_3D":
        sp=area.spaces.active
        sp.shading.type="RENDERED"
        sp.region_3d.view_perspective="CAMERA"
        sp.overlay.show_overlays=False
sc=bpy.context.scene
sc.eevee.use_shadows=True if hasattr(sc.eevee,"use_shadows") else None
print(sc.name)
# ---- result ----
# {"result":"Code executed successfully: MedievalColony\n"}

# ==============================================================================================================
# [0007] 2026-09-23 01:16:50  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
o=bpy.data.objects["Terrain"]
bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
cl=bm.loops.layers.color.get("Col")
grass1=Vector((0.16,0.36,0.07));grass2=Vector((0.34,0.50,0.12));dry=Vector((0.55,0.52,0.22))
dirt=Vector((0.42,0.29,0.15));sand=Vector((0.62,0.55,0.38));rock=Vector((0.36,0.35,0.33));mud=Vector((0.22,0.17,0.11))
vcol={}
for v in bm.verts:
    x,y,z=v.co
    if z<=-4.99: continue
    n=noise.noise(Vector((x*0.15,y*0.15,7.7)))*0.5+0.5
    n2=noise.noise(Vector((x*0.6,y*0.6,1.3)))*0.5+0.5
    c=grass1.lerp(grass2,n); c=c.lerp(dry,max(0,n2-0.65)*1.6)
    ntop=max((f.normal.z for f in v.link_faces if f.material_index==0),default=1)
    slope=1-ntop
    if slope>0.12: c=c.lerp(rock,min(1,(slope-0.12)*5))
    dr=abs(y-river_y(x))
    if dr<4.5: c=c.lerp(sand,1-smooth(2.5,4.5,dr))
    if dr<2.2: c=c.lerp(mud,1-smooth(1.2,2.2,dr))
    pd=path_d(x,y); w=1.0+0.3*n2
    if dr>2.0: c=c.lerp(dirt,1-smooth(w-0.3,w+0.5,pd))
    dc=math.hypot(x+1,y-1)
    c=c.lerp(dirt*1.1,1-smooth(3.5,5,dc+1.5*n2))
    vcol[v]=c
for f in bm.faces:
    for l in f.loops:
        if f.material_index==1:
            z=l.vert.co.z
            band=0.5+0.5*math.sin(z*2.2+noise.noise(Vector((l.vert.co.x*0.3,l.vert.co.y*0.3,0)))*2)
            c=Vector((0.30,0.20,0.12)).lerp(Vector((0.42,0.30,0.18)),band)
            if z<-3.2: c=Vector((0.33,0.32,0.30))*(0.8+0.3*band)
        else: c=vcol.get(l.vert,Vector((0.3,0.2,0.1)))
        l[cl]=(*c,1)
bm.to_mesh(o.data); bm.free()
cam=bpy.data.objects["Camera_Hero"]; cam.data.lens=35
cam.location=(44,-50,36)
cam.rotation_euler=(Vector((0,0,-2))-cam.location).to_track_quat("-Z","Y").to_euler()
# softer world: blend sky with flat color for below horizon
w=SC.world; nt=w.node_tree
bg=next(n for n in nt.nodes if n.type=="BACKGROUND"); bg.inputs[1].default_value=0.5
print(len(vcol))
# ---- result ----
# {"result":"Code executed successfully: 22801\n"}

# ==============================================================================================================
# [0008] 2026-09-23 01:17:30  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
code = r'''
def M_house():
    return [mat("Stone",(0.42,0.40,0.37),0.9), mat("Plaster",(0.82,0.76,0.62),0.9), mat("Timber",(0.18,0.11,0.06),0.8),
            mat("Thatch",(0.60,0.47,0.24),1.0), mat("RoofTile",(0.50,0.20,0.12),0.7), mat("DoorWood",(0.33,0.20,0.10),0.8),
            mat("WindowGlow",(1.0,0.7,0.3),0.5,emit=(1.0,0.62,0.25),emit_str=3.0)]
def face_rot(x,y,tx,ty): return math.atan2(tx-x, -(ty-y))
def build_house(name,x,y,w,d,wall_h,roof="thatch",rz=0.0,seed=0,coll=None,chimney=True,stories=1):
    rnd=random.Random(seed); bm=bmesh.new()
    z0=min(ground_h(x+dx,y+dy) for dx in(-w/2,w/2) for dy in(-d/2,d/2))
    zc=ground_h(x,y); top_found=max(zc,z0)+0.35
    box(bm,(0,0,(z0-1.0+top_found)/2-zc),(w+0.3,d+0.3,top_found-(z0-1.0)),mat_index=0)
    base=top_found-zc
    H=wall_h*stories
    box(bm,(0,0,base+H/2),(w,d,H),mat_index=1)
    t=0.16; o=0.03
    # corner posts
    for sx in(-1,1):
        for sy in(-1,1): box(bm,(sx*(w/2-t/2+o),sy*(d/2-t/2+o),base+H/2),(t,t,H),mat_index=2)
    # horizontal beams per story
    for s in range(stories+1):
        zz=base+min(H-t/2,s*wall_h+ (t/2 if s==0 else 0))
        box(bm,(0,-d/2-o+0.02,zz),(w+0.02,t,t),mat_index=2); box(bm,(0,d/2+o-0.02,zz),(w+0.02,t,t),mat_index=2)
        box(bm,(-w/2-o+0.02,0,zz),(t,d+0.02,t),mat_index=2); box(bm,(w/2+o-0.02,0,zz),(t,d+0.02,t),mat_index=2)
    # intermediate posts + braces on long walls
    nposts=max(1,int(w/1.6))
    for s in range(stories):
        zb=base+s*wall_h
        for k in range(1,nposts+1):
            px=-w/2+k*w/(nposts+1)
            for sy in(-1,1): box(bm,(px,sy*(d/2+o),zb+wall_h/2),(t*0.8,t*0.8,wall_h),mat_index=2)
        for sy in(-1,1):
            L=math.hypot(w/(nposts+1),wall_h)*0.55
            for sx in(-1,1):
                vs=box(bm,(sx*(w/2-w/(nposts+1)/2),sy*(d/2+o+0.01),zb+wall_h/2),(L,t*0.7,t*0.7))
                ang=math.atan2(wall_h,w/(nposts+1))*sx
                bmesh.ops.rotate(bm,verts=vs,cent=Vector((sx*(w/2-w/(nposts+1)/2),sy*(d/2+o+0.01),zb+wall_h/2)),matrix=Matrix.Rotation(ang,3,"Y"))
                for f in {f for v in vs for f in v.link_faces}: f.material_index=2
        # side braces
        for sx in(-1,1):
            box(bm,(sx*(w/2+o),0,zb+wall_h/2),(t*0.8,t*0.8,wall_h),mat_index=2)
    # gable triangle walls
    rh=d*0.62 if roof=="thatch" else d*0.5
    for sx in(-1,1):
        X=sx*w/2*0.999
        v=[bm.verts.new((X,-d/2,base+H)),bm.verts.new((X,d/2,base+H)),bm.verts.new((X,0,base+H+rh))]
        f=bm.faces.new(v if sx>0 else list(reversed(v))); f.material_index=1
        box(bm,(X+sx*o,0,base+H+rh*0.45),(t,t*0.8,rh*0.9),mat_index=2)
    # door (on -Y)
    dx=rnd.uniform(-w*0.2,w*0.2)
    box(bm,(dx,-d/2-0.04,base+0.95),(0.9,0.12,1.9),mat_index=5)
    box(bm,(dx,-d/2-0.07,base+1.95),(1.1,0.14,0.14),mat_index=2)
    box(bm,(dx,-d/2-0.35,base-0.12),(1.2,0.6,0.25),mat_index=0)  # step
    # windows
    for s in range(stories):
        zw=base+s*wall_h+wall_h*0.58
        for sy in(-1,1):
            for k in range(nposts+1):
                px=-w/2+(k+0.5)*w/(nposts+1)
                if sy<0 and s==0 and abs(px-dx)<1.0: continue
                if rnd.random()<0.25: continue
                box(bm,(px,sy*(d/2+0.02),zw),(0.55,0.08,0.6),mat_index=6)
                box(bm,(px,sy*(d/2+0.06),zw),(0.08,0.06,0.62),mat_index=2)
                box(bm,(px,sy*(d/2+0.08),zw-0.34),(0.75,0.14,0.08),mat_index=2)
    # roof
    rm=3 if roof=="thatch" else 4
    thick=0.38 if roof=="thatch" else 0.14
    prism_roof(bm,(0,0,base+H-0.05),w,d,rh,over=0.45 if roof=="thatch" else 0.3,thick=thick,mat_index=rm)
    if roof=="thatch":
        box(bm,(0,0,base+H+rh-0.02),(w+0.95,0.5,0.28),mat_index=3)
    else:
        box(bm,(0,0,base+H+rh+0.02),(w+0.65,0.22,0.18),mat_index=4)
        for k in range(int((d/2+0.3)/0.3)):
            yy=-(d/2+0.3)+k*0.3
            zz=base+H-0.05+rh*(1-abs(yy)/(d/2+0.3))
            for sgn in(-1,1): box(bm,(0,sgn*abs(yy),zz+0.02),(w+0.62,0.05,0.05),mat_index=4)
    if chimney:
        cx=rnd.choice([-1,1])*(w/2-0.5)
        box(bm,(cx,d*0.18,base+H+rh*0.5+0.3),(0.6,0.6,rh+1.1),mat_index=0)
        box(bm,(cx,d*0.18,base+H+rh*1.05+0.55+0.1),(0.72,0.72,0.14),mat_index=0)
    o=obj_from_bm(name,bm,M_house(),coll,loc=(x,y,zc),rot=(0,0,rz))
    o["chimney_top"]=(cx if chimney else 0, d*0.18, base+H+rh+0.8)
    return o
'''
t=bpy.data.texts["mc_helpers"]
if "def build_house" not in t.as_string(): t.write(code)
exec(code)
C=col("Buildings")
for ob in list(C.objects): bpy.data.objects.remove(ob)
cx,cy=-1,1
HOUSES=[("Cottage_A",6,-4,5,3.6,2.4,"thatch",1),("Cottage_B",-8,-6,4.5,3.4,2.3,"thatch",1),
        ("Cottage_C",5,8,5.5,3.8,2.4,"tile",1),("Cottage_D",-12,5,4.6,3.4,2.3,"thatch",1),
        ("Cottage_E",11,-3,4.2,3.2,2.3,"thatch",1),("Cottage_F",-5,-12,4.8,3.5,2.3,"tile",1),
        ("Tavern",12,9,7,4.6,2.5,"tile",2),("GreatHall",-3,13,9,5.5,3.2,"thatch",1)]
for i,(n,x,y,w,d,h,r,st) in enumerate(HOUSES):
    rz=face_rot(x,y,cx,cy)+ (0 if n!="GreatHall" else 0)
    build_house(n,x,y,w,d,h,r,rz,seed=i*7+1,coll=C,stories=st)
print("houses", len(C.objects))
# ---- result ----
# {"result":"Code executed successfully: houses 8\n"}

# ==============================================================================================================
# [0009] 2026-09-23 01:17:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
LC=col("Lighting")
cd=bpy.data.cameras.get("MC_CamClose") or bpy.data.cameras.new("MC_CamClose"); cd.lens=35
cam=bpy.data.objects.get("Camera_Close") or bpy.data.objects.new("Camera_Close",cd)
if cam.name not in LC.objects: LC.objects.link(cam)
cam.location=(16,-22,12)
cam.rotation_euler=(Vector((0,1,0))-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0010] 2026-09-23 01:17:50  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Buildings")
for n,(x,y) in {"Cottage_A":(5.5,-5.5),"Cottage_E":(14,-6.5)}.items():
    o=bpy.data.objects[n]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
HOUSES={"Cottage_A":(5.5,-5.5,5,3.6,2.4,"thatch",1,1),"Cottage_E":(14,-6.5,4.2,3.2,2.3,"thatch",1,29)}
for n,(x,y,w,d,h,r,st,sd) in HOUSES.items():
    build_house(n,x,y,w,d,h,r,face_rot(x,y,-1,1),seed=sd,coll=C,stories=st)
sun=bpy.data.objects["Sun"]; sun.data.energy=3.2
bg=next(n for n in SC.world.node_tree.nodes if n.type=="BACKGROUND"); bg.inputs[1].default_value=0.22
vs=SC.view_settings
print([i.identifier for i in vs.bl_rna.properties["view_transform"].enum_items])
vs.exposure=-0.3
try: vs.look="AgX - Medium High Contrast"
except Exception as e: print(e)
# ---- result ----
# {"result":"Code executed successfully: ['NONE']\n"}

# ==============================================================================================================
# [0011] 2026-09-23 01:18:15  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Landmarks")
for ob in list(C.objects): bpy.data.objects.remove(ob)
MH=M_house()  # 0 stone 1 plaster 2 timber 3 thatch 4 tile 5 doorwood 6 glow
sail_m=mat("SailCloth",(0.85,0.80,0.68),0.9)
mats=MH+[sail_m]
# ---- Windmill
wx,wy=-13.5,19.5; wz=min(ground_h(wx+a,wy+b) for a in(-2,2) for b in(-2,2))
bm=bmesh.new()
cyl(bm,(0,0,-0.5+1.0),2.6,2.6,2.0,segs=10,mat_index=0)
cyl(bm,(0,0,1.8+3.5),2.3,1.6,7.0,segs=10,mat_index=1)
for zz in (1.9,5.3,8.7): cyl(bm,(0,0,zz),2.35-(zz-1.8)*0.1,2.35-(zz-1.8)*0.1,0.22,segs=10,mat_index=2)
cyl(bm,(0,0,8.8+1.3),1.95,0.15,2.8,segs=10,mat_index=3)
box(bm,(0,-2.2,2.9),(1.0,0.4,2.0),mat_index=5)
for zz,ang in ((5.2,0.6),(7.4,-0.4),(4.2,2.6)):
    r=2.3-(zz-1.8)*0.1
    box(bm,(math.sin(ang)*r,-math.cos(ang)*r,zz),(0.45,0.3,0.6),rot_z=ang,mat_index=6)
wm_body=obj_from_bm("Windmill",bm,mats,C,loc=(wx,wy,wz),rot=(0,0,math.radians(-35)))
# sails (separate object so it can spin in-game)
bm=bmesh.new()
cyl(bm,(0,0,0),0.28,0.28,0.9,segs=8,rot=Matrix.Rotation(math.pi/2,4,"X"),mat_index=2)
for k in range(4):
    R=Matrix.Rotation(k*math.pi/2+0.3,4,"Y")
    vs=box(bm,(0,-0.3,4.2),(0.18,0.14,8.4),mat_index=2)
    bmesh.ops.transform(bm,matrix=R,verts=vs)
    vs=box(bm,(0.75,-0.38,5.0),(1.2,0.04,6.2),mat_index=7)
    bmesh.ops.transform(bm,matrix=R,verts=vs)
    for j in range(7):
        vs=box(bm,(0.75,-0.42,2.1+j*0.95),(1.35,0.07,0.07),mat_index=2)
        bmesh.ops.transform(bm,matrix=R,verts=vs)
sails=obj_from_bm("Windmill_Sails",bm,mats,C)
sails.parent=wm_body; sails.location=(0,-2.05,8.6)
sails["spin_axis"]="local Y"
# ---- Bridge
bx=0.6; by=river_y(bx)
bm=bmesh.new(); L=11.0; W=2.6; nP=22
for i in range(nP):
    yy=-L/2+(i+0.5)*L/nP
    zz=0.55*math.cos(yy/L*math.pi)
    box(bm,(0,yy,zz),(W+random.uniform(-0.1,0.25),L/nP*0.9,0.14),rot_z=random.uniform(-0.03,0.03),mat_index=5)
for sx in(-1,1):
    for k in range(5):
        yy=-L/2+0.6+k*(L-1.2)/4; zz=0.55*math.cos(yy/L*math.pi)
        box(bm,(sx*(W/2+0.05),yy,zz+0.0-0.3),(0.2,0.2,2.4),mat_index=2)
        box(bm,(sx*(W/2+0.05),yy,zz+1.0),(0.24,0.24,0.1),mat_index=2)
    for k in range(4):
        y0=-L/2+0.6+k*(L-1.2)/4; y1=y0+(L-1.2)/4
        z0=0.55*math.cos(y0/L*math.pi)+0.85; z1=0.55*math.cos(y1/L*math.pi)+0.85
        vs=box(bm,(sx*(W/2+0.05),(y0+y1)/2,(z0+z1)/2),(0.12,y1-y0,0.12),mat_index=2)
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((sx*(W/2+0.05),(y0+y1)/2,(z0+z1)/2)),matrix=Matrix.Rotation(math.atan2(z1-z0,y1-y0),3,"X"))
# stone abutments
for sy in(-1,1): box(bm,(0,sy*(L/2-0.3),-0.9),(W+0.8,1.6,1.8),mat_index=0)
ang=math.atan2(-(1-0.5),(-24+15)*-1)
obj_from_bm("Bridge",bm,mats,C,loc=(bx,by,-0.15),rot=(0,0,0.05))
# ---- Well
bm=bmesh.new()
cyl(bm,(0,0,0.35),1.0,1.0,1.1,segs=12,mat_index=0)
cyl(bm,(0,0,0.85),0.78,0.78,0.2,segs=12,mat_index=2)
for sx in(-1,1): box(bm,(sx*0.95,0,1.4),(0.16,0.16,2.2),mat_index=2)
box(bm,(0,0,2.05),(2.1,0.12,0.12),mat_index=2)
prism_roof(bm,(0,0,2.45),2.1,1.6,0.8,over=0.2,thick=0.12,mat_index=3)
box(bm,(0,0,1.45),(0.35,0.35,0.35),mat_index=5)
obj_from_bm("Well",bm,mats,C,loc=(-1,1,ground_h(-1,1)),rot=(0,0,0.4))
print("ok", by)
# ---- result ----
# {"result":"Code executed successfully: ok -13.67193668989384\n"}

# ==============================================================================================================
# [0012] 2026-09-23 01:18:50  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Farms")
for ob in list(C.objects): bpy.data.objects.remove(ob)
wheat=mat("Wheat",(0.80,0.62,0.22),0.8); wheat2=mat("WheatStem",(0.62,0.52,0.20),0.9)
cab=mat("Cabbage",(0.30,0.55,0.18),0.6); soil=mat("TilledSoil",(0.26,0.17,0.09),1.0)
timber=mat("Timber",(0.18,0.11,0.06),0.8); hay=mat("Hay",(0.78,0.66,0.33),1.0)
carrot=mat("CarrotLeaf",(0.22,0.45,0.10),0.8)
mats=[soil,wheat,wheat2,cab,timber,hay,carrot]
PLOTS=[("Field_Wheat",(18,-8.5),(23.5,1.8),1),("Field_Cabbage",(24.5,-8.5),(28.8,1.8),3),("Field_Plowed",(19,-17.0+6.6),(0,0),0)]
def soil_strip(bm,x0,x1,y0,y1,row_step):
    # furrow ridges following terrain
    y=y0+row_step/2
    while y<y1:
        n=int((x1-x0)/0.5)+1
        pts=[]
        for i in range(n+1):
            x=x0+(x1-x0)*i/n; pts.append((x,y,ground_h(x,y)))
        for i in range(n):
            a=Vector(pts[i]);b=Vector(pts[i+1]);w=row_step*0.45
            vs=[bm.verts.new(a+Vector((0,-w,0.02))),bm.verts.new(b+Vector((0,-w,0.02))),bm.verts.new(b+Vector((0,0,0.14))),bm.verts.new(a+Vector((0,0,0.14))),
                bm.verts.new(a+Vector((0,w,0.02))),bm.verts.new(b+Vector((0,w,0.02)))]
            bm.faces.new((vs[0],vs[1],vs[2],vs[3])).material_index=0
            bm.faces.new((vs[3],vs[2],vs[5],vs[4])).material_index=0
        y+=row_step
rnd=random.Random(11)
# wheat field
x0,y0,x1,y1=18,-8.5,23.5,1.8
bm=bmesh.new(); soil_strip(bm,x0,x1,y0,y1,0.7)
y=y0+0.35
while y<y1:
    x=x0+0.25
    while x<x1-0.2:
        z=ground_h(x,y)+0.1; h=rnd.uniform(0.75,1.05)
        vs=cyl(bm,(x+rnd.uniform(-.08,.08),y+rnd.uniform(-.08,.08),z+h/2),0.2,0.1,h,segs=5,mat_index=2)
        vs=ico(bm,(x,y,z+h+0.05),0.2,sub=0,scale=(1,1,1.4),jitter=0.04,mat_index=1,seed=int(x*100+y*10))
        x+=0.36
    y+=0.7
obj_from_bm("Field_Wheat",bm,mats,C)
# cabbage field
x0,y0,x1,y1=24.5,-8.5,28.8,1.8
bm=bmesh.new(); soil_strip(bm,x0,x1,y0,y1,0.8)
y=y0+0.4
while y<y1:
    x=x0+0.3
    while x<x1-0.2:
        z=ground_h(x,y)+0.18
        ico(bm,(x,y,z+0.1),0.26,sub=1,scale=(1,1,0.8),jitter=0.05,mat_index=3,seed=int(x*37+y*11))
        x+=0.62
    y+=0.8
obj_from_bm("Field_Cabbage",bm,mats,C)
# plowed + sprouting field (carrots) west of village
x0,y0,x1,y1=-24,-10.5,-15.5,-6.5
bm=bmesh.new(); soil_strip(bm,x0,x1,y0,y1,0.65)
y=y0+0.325
while y<y1:
    x=x0+0.2
    while x<x1-2.5:
        z=ground_h(x,y)+0.14
        for k in range(3):
            a=k*2.1+rnd.random()
            vs=box(bm,(x+math.cos(a)*0.06,y+math.sin(a)*0.06,z+0.12),(0.05,0.05,0.26),mat_index=6)
        x+=0.4
    y+=0.65
obj_from_bm("Field_Carrots",bm,mats,C)
# fences
def fence(name,pts,closed=True,gap=None):
    bm=bmesh.new()
    P=pts+([pts[0]] if closed else [])
    for i in range(len(P)-1):
        a=Vector((*P[i],0));b=Vector((*P[i+1],0));L=(b-a).length;n=max(1,int(L/2.0))
        ang=math.atan2(b.y-a.y,b.x-a.x)
        for k in range(n+1):
            p=a+(b-a)*k/n; z=ground_h(p.x,p.y)
            box(bm,(p.x,p.y,z+0.5),(0.14,0.14,1.1),rot_z=rnd.uniform(0,.3),mat_index=4)
        for k in range(n):
            if gap and i==gap[0] and k==gap[1]: continue
            p=a+(b-a)*(k+0.5)/n; 
            p0=a+(b-a)*k/n;p1=a+(b-a)*(k+1)/n
            z0=ground_h(p0.x,p0.y);z1=ground_h(p1.x,p1.y)
            for hh in(0.45,0.85):
                vs=box(bm,(p.x,p.y,(z0+z1)/2+hh),(L/n+0.1,0.07,0.1),mat_index=4)
                c=Vector((p.x,p.y,(z0+z1)/2+hh))
                bmesh.ops.rotate(bm,verts=vs,cent=c,matrix=Matrix.Rotation(ang,3,"Z")@Matrix.Rotation(-math.atan2(z1-z0,L/n),3,"Y"))
    return obj_from_bm(name,bm,mats,C)
fence("Fence_Fields",[(17.4,-9.1),(29.4,-9.1),(29.4,2.4),(17.4,2.4)],gap=(3,1))
fence("Fence_Carrots",[(-24.6,-11.1),(-15.0,-11.1),(-15.0,-5.9),(-24.6,-5.9)],gap=(2,1))
# hay bales
bm=bmesh.new()
for (x,y) in [(20,3.6),(21.3,3.8),(20.6,4.9),(-17,-12.3),(-15.8,-12.6)]:
    z=ground_h(x,y)
    cyl(bm,(x,y,z+0.55),0.6,0.6,1.1,segs=12,rot=Matrix.Rotation(math.pi/2,4,"X")@Matrix.Rotation(rnd.uniform(0,3),4,"Y"),mat_index=5)
obj_from_bm("HayBales",bm,mats,C)
print("farms ok")
# ---- result ----
# {"result":"Code executed successfully: farms ok\n"}

# ==============================================================================================================
# [0013] 2026-09-23 01:19:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
bpy.data.objects["Windmill"].rotation_euler.z=math.radians(35)
p=bpy.data.materials["MC_Plaster"]; next(n for n in p.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(0.70,0.62,0.48,1)
st=bpy.data.materials["MC_Stone"]; next(n for n in st.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(0.33,0.31,0.29,1)
# world: camera sees soft gradient; lighting from sky
w=SC.world; nt=w.node_tree
out=next(n for n in nt.nodes if n.type=="OUTPUT_WORLD")
bg=next(n for n in nt.nodes if n.type=="BACKGROUND")
lp=nt.nodes.new("ShaderNodeLightPath")
bg2=nt.nodes.new("ShaderNodeBackground")
grad=nt.nodes.new("ShaderNodeTexGradient"); grad.gradient_type="LINEAR"
tc=nt.nodes.new("ShaderNodeTexCoord"); mp=nt.nodes.new("ShaderNodeMapping")
mp.inputs["Rotation"].default_value=(0,math.radians(-90),0)
mp.inputs["Location"].default_value=(0,0,0)
ramp=nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=0.45; ramp.color_ramp.elements[0].color=(0.72,0.66,0.55,1)
ramp.color_ramp.elements[1].position=0.85; ramp.color_ramp.elements[1].color=(0.36,0.52,0.72,1)
nt.links.new(tc.outputs["Window"],mp.inputs["Vector"])
mix=nt.nodes.new("ShaderNodeMixShader")
# use window coords: vertical gradient via separate
sep=nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Window"],sep.inputs[0])
nt.links.new(sep.outputs["Y"],ramp.inputs[0])
nt.links.new(ramp.outputs[0],bg2.inputs[0]); bg2.inputs[1].default_value=1.0
nt.links.new(lp.outputs["Is Camera Ray"],mix.inputs[0])
nt.links.new(bg.outputs[0],mix.inputs[1]); nt.links.new(bg2.outputs[0],mix.inputs[2])
nt.links.new(mix.outputs[0],out.inputs[0])
for n in (grad,mp): nt.nodes.remove(n)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0014] 2026-09-23 01:19:48  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
A=col("MC_Assets")
for lc in bpy.context.view_layer.layer_collection.children:
    if lc.name=="MC_Assets": lc.exclude=True
for ob in list(A.objects): bpy.data.objects.remove(ob)
bark=mat("Bark",(0.24,0.16,0.10),0.9)
leaf=[mat("LeafOak1",(0.18,0.38,0.10),0.8),mat("LeafOak2",(0.30,0.45,0.12),0.8),mat("LeafAutumn",(0.70,0.42,0.12),0.8)]
pine=mat("LeafPine",(0.08,0.24,0.12),0.8)
rockm=mat("Rock",(0.40,0.39,0.37),0.9); moss=mat("Moss",(0.25,0.36,0.12),0.9)
variants={}
def make(name,bm,mats):
    o=obj_from_bm(name,bm,mats,A); variants[name]=o; return o
for v in range(3):
    rnd=random.Random(v+50); bm=bmesh.new()
    H=rnd.uniform(4.5,6.5)
    cyl(bm,(0,0,H*0.15),0.28,0.2,H*0.35,segs=6,mat_index=0)
    tiers=4
    for k in range(tiers):
        r=1.7*(1-k/tiers*0.75); z=H*0.2+k*H*0.19
        vs=cyl(bm,(0,0,z+H*0.14),r,0.05,H*0.32,segs=7,mat_index=1)
        for vv in vs: vv.co.x+=rnd.uniform(-.08,.08); vv.co.y+=rnd.uniform(-.08,.08)
    make(f"Tree_Pine_{v}",bm,[bark,pine])
for v in range(3):
    rnd=random.Random(v+80); bm=bmesh.new()
    H=rnd.uniform(2.2,3.0)
    cyl(bm,(0,0,H/2-0.2),0.3,0.2,H+0.4,segs=6,mat_index=0)
    for k in range(2):
        a=rnd.uniform(0,6.28)
        vs=cyl(bm,(0,0,0),0.12,0.08,1.4,segs=5,mat_index=0)
        bmesh.ops.transform(bm,verts=vs,matrix=Matrix.Translation((math.cos(a)*0.4,math.sin(a)*0.4,H-0.1))@Matrix.Rotation(0.8,4,Vector((-math.sin(a),math.cos(a),0))))
    blobs=[(0,0,H+1.2,1.6)]+[(math.cos(a)*1.1,math.sin(a)*1.1,H+0.6+rnd.uniform(0,.7),rnd.uniform(1.0,1.3)) for a in [i*2.1+rnd.random() for i in range(3)]]
    for i,(x,y,z,r) in enumerate(blobs):
        ico(bm,(x,y,z),r,sub=1,jitter=0.12,mat_index=1,seed=v*10+i)
    for li,lm in enumerate(leaf):
        make(f"Tree_Oak_{v}_{li}",bm.copy(),[bark,lm])
    bm.free()
for v in range(4):
    rnd=random.Random(v+120); bm=bmesh.new()
    ico(bm,(0,0,0.2),1.0,sub=1,scale=(rnd.uniform(1,1.6),rnd.uniform(0.8,1.2),rnd.uniform(0.6,0.9)),jitter=0.18,mat_index=0,seed=v+3)
    make(f"Rock_{v}",bm,[rockm])
for v in range(2):
    bm=bmesh.new()
    for i in range(5):
        rnd=random.Random(v*9+i); a=i*1.3
        ico(bm,(math.cos(a)*0.45,math.sin(a)*0.45,0.25),rnd.uniform(0.35,0.55),sub=1,jitter=0.06,mat_index=0,seed=i)
    make(f"Bush_{v}",bm,[leaf[v]])
for o in variants.values():
    for f in o.data.polygons: f.use_smooth=False
# scatter
F=col("Nature")
for ob in list(F.objects): bpy.data.objects.remove(ob)
HOUSES=[(o.location.x,o.location.y) for o in col("Buildings").objects]+[(-13.5,19.5),(-1,1)]
RECTS=[(17,-9.6,30,3),(-25,-11.6,-14.5,-5.4)]
def blocked(x,y,r):
    if abs(x)>HALF-1 or abs(y)>HALF-1: return True
    if abs(y-river_y(x))<3.8+r*0.3: return True
    if path_d(x,y)<1.8+r*0.4: return True
    for hx,hy in HOUSES:
        if math.hypot(x-hx,y-hy)<5.0+r*0.4: return True
    for x0,y0,x1,y1 in RECTS:
        if x0-1<x<x1+1 and y0-1<y<y1+1: return True
    if math.hypot(x+1,y-1)<14 and not (y<-18): return True
    return False
rnd=random.Random(2024); placed=[]
def place(kind,names,count,rmin,dens_fn,scale=(0.8,1.3)):
    tries=0; n=0
    while n<count and tries<count*60:
        tries+=1
        x=rnd.uniform(-HALF,HALF); y=rnd.uniform(-HALF,HALF)
        if rnd.random()>dens_fn(x,y): continue
        if blocked(x,y,rmin): continue
        if any((x-px)**2+(y-py)**2<(rmin+pr)**2 for px,py,pr in placed): continue
        nm=rnd.choice(names); src=variants[nm]
        o=bpy.data.objects.new(f"{kind}_{n:03d}",src.data); F.objects.link(o)
        s=rnd.uniform(*scale)
        z=min(ground_h(x+dx,y+dy) for dx in(-.4,.4) for dy in(-.4,.4))
        o.location=(x,y,z-0.1); o.rotation_euler=(rnd.uniform(-.05,.05),rnd.uniform(-.05,.05),rnd.uniform(0,6.28)); o.scale=(s,s,s*rnd.uniform(0.9,1.15))
        placed.append((x,y,rmin*s)); n+=1
def forest(x,y):
    n=noise.noise(Vector((x*0.07,y*0.07,9.0)))*0.5+0.5
    edge=max(abs(x),abs(y))/HALF
    return min(1,n*1.3+smooth(8,24,y+0.35*x)*0.5+(edge-0.6)*1.2)
place("Pine",[f"Tree_Pine_{i}" for i in range(3)],110,1.3,lambda x,y:forest(x,y)*(0.4+smooth(4,20,y+0.35*x)))
place("Oak",[k for k in variants if k.startswith("Tree_Oak")],80,1.7,lambda x,y:forest(x,y)*(1.0-0.5*smooth(10,20,y+0.35*x)))
place("Bush",["Bush_0","Bush_1"],70,0.8,lambda x,y:0.7)
place("Rock",[f"Rock_{i}" for i in range(4)],45,0.9,lambda x,y:0.3+smooth(6,20,y+0.35*x),scale=(0.4,1.4))
print(len(F.objects))
# ---- result ----
# {"result":"Code executed successfully: 216\n"}

# ==============================================================================================================
# [0015] 2026-09-23 01:19:55  blender  ok
# ==============================================================================================================
import bpy
bpy.context.scene.camera=bpy.data.objects["Camera_Hero"]
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0016] 2026-09-23 01:20:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
rnd=random.Random(5)
rem=0
for o in list(col("Nature").objects):
    x,y=o.location.x,o.location.y
    kill=False
    if y<-18 and -2<x<18 and not o.name.startswith("Rock"): kill=math.hypot(x-8,y-24*-1)<7 or rnd.random()<0.45
    if y<-18 and x>18 and o.name.startswith("Pine") and rnd.random()<0.5: kill=True
    if kill: bpy.data.objects.remove(o); rem+=1
print("removed",rem)
# ---- Lumber camp at (8,-24)
C=col("LumberCamp")
for ob in list(C.objects): bpy.data.objects.remove(ob)
bark=mat("Bark",(0.24,0.16,0.10),0.9); cut=mat("CutWood",(0.78,0.60,0.38),0.8)
tent=mat("TentCanvas",(0.70,0.60,0.45),1.0); timber=mat("Timber",(0.18,0.11,0.06),0.8)
iron=mat("Iron",(0.25,0.25,0.27),0.4,metal=0.8)
mats=[bark,cut,tent,timber,iron]
bm=bmesh.new()
cx,cy=8,-24
def gz(x,y): return ground_h(x,y)
# stumps
for i in range(9):
    a=rnd.uniform(0,6.28); r=rnd.uniform(3.5,7); x,y=cx+math.cos(a)*r,cy+math.sin(a)*r
    if abs(y-river_y(x))<4: continue
    z=gz(x,y); h=rnd.uniform(0.35,0.6); rr=rnd.uniform(0.3,0.45)
    cyl(bm,(x,y,z+h/2-0.1),rr*1.15,rr,h,segs=8,mat_index=0)
    cyl(bm,(x,y,z+h-0.09),rr*0.96,rr*0.96,0.02,segs=8,mat_index=1)
# log pile (pyramid)
lx,ly=cx+2.5,cy+1.5; lz=gz(lx,ly)
row=0
for layer,count in enumerate([5,4,3,2]):
    for k in range(count):
        yy=ly+(k-(count-1)/2)*0.62; zz=lz+0.3+layer*0.52
        R=Matrix.Rotation(math.pi/2,4,"Y")
        cyl(bm,(lx,yy,zz),0.3,0.3,4.2+rnd.uniform(-.3,.3),segs=8,rot=R,mat_index=0)
        for sx in(-1,1): cyl(bm,(lx+sx*(2.1+0.005),yy,zz),0.27,0.27,0.03,segs=8,rot=R,mat_index=1)
for sx in(-1,1):
    for sy in(-1,1): box(bm,(lx+sx*1.2,ly+sy*1.7,lz+0.9),(0.15,0.15,1.9),mat_index=3)
# split firewood stack
fx,fy=cx-2.5,cy+2.8; fz=gz(fx,fy)
for layer in range(5):
    for k in range(7):
        cyl(bm,(fx+(k-3)*0.26,fy,fz+0.15+layer*0.24),0.13,0.13,0.9,segs=5,rot=Matrix.Rotation(math.pi/2,4,"X"),mat_index=0 if (k+layer)%3 else 1)
# chopping block + axe
bx,by=cx-0.5,cy-0.5; bz=gz(bx,by)
cyl(bm,(bx,by,bz+0.3),0.4,0.4,0.6,segs=8,mat_index=0)
vs=box(bm,(bx+0.1,by,bz+0.95),(0.06,0.06,0.9),mat_index=3)
box(bm,(bx+0.1,by+0.12,bz+0.62),(0.04,0.28,0.18),mat_index=4)
# sawhorse
sx0,sy0=cx+0.5,cy+3.2; sz=gz(sx0,sy0)
for d in(-0.8,0.8):
    for a in(-0.35,0.35):
        vs=box(bm,(sx0+d,sy0,sz+0.45),(0.1,0.1,1.0),mat_index=3)
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((sx0+d,sy0,sz+0.9)),matrix=Matrix.Rotation(a,3,"X"))
cyl(bm,(sx0,sy0,sz+1.0),0.25,0.25,3.0,segs=8,rot=Matrix.Rotation(math.pi/2,4,"Y"),mat_index=0)
obj_from_bm("LumberCamp_Props",bm,mats,C)
# tent
bm=bmesh.new(); tx,ty=cx-3.2,cy-1.5; tz=gz(tx,ty)
prism_roof(bm,(0,0,0),2.6,2.2,1.9,over=0.05,thick=0.05,mat_index=2)
for sx in(-1,1): box(bm,(sx*1.35,0,1.0),(0.1,0.1,2.1),mat_index=3)
box(bm,(0,0,1.95),(3.0,0.08,0.08),mat_index=3)
obj_from_bm("LumberCamp_Tent",bm,mats,C,loc=(tx,ty,tz),rot=(0,0,0.5))
print("camp ok")
# ---- result ----
# {"result":"Code executed successfully: removed 15\ncamp ok\n"}

# ==============================================================================================================
# [0017] 2026-09-23 01:20:51  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Defenses")
for ob in list(C.objects): bpy.data.objects.remove(ob)
bark=mat("Bark",(0.24,0.16,0.10),0.9); cut=mat("CutWood",(0.78,0.60,0.38),0.8); timber=mat("Timber",(0.18,0.11,0.06),0.8)
thatch=mat("Thatch",(0.60,0.47,0.24),1.0); stone=mat("Stone",(0.33,0.31,0.29),0.9)
banner=mat("Banner",(0.55,0.08,0.07),0.8); gold=mat("BannerGold",(0.85,0.65,0.15),0.5,metal=0.3)
mats=[bark,cut,timber,thatch,stone,banner,gold]
rnd=random.Random(77)
cx,cy,R=-1,1,15.0
bm=bmesh.new()
a0,a1=math.radians(135),math.radians(248)
gate=math.radians(186); gw=math.radians(10)
step=0.42/R
a=a0; logs=[]
while a<a1:
    if abs(a-gate)>gw/2:
        x,y=cx+math.cos(a)*R,cy+math.sin(a)*R
        z=ground_h(x,y); h=rnd.uniform(3.0,3.6); r=0.22
        cyl(bm,(x,y,z+h/2-0.5),r,r,h,segs=7,mat_index=0)
        cyl(bm,(x,y,z+h-0.5+0.35),r,0.02,0.7,segs=7,mat_index=1)
        logs.append((a,x,y,z))
    a+=step
# horizontal braces on the inside
for i in range(len(logs)-1):
    a,x,y,z=logs[i]; a2,x2,y2,z2=logs[i+1]
    if a2-a>step*1.5: continue
    for hh in(0.6,2.0):
        p=Vector(((x+x2)/2,(y+y2)/2,(z+z2)/2+hh)); inward=Vector((-math.cos(a),-math.sin(a),0))*0.25
        vs=box(bm,p+inward,(0.1,0.52,0.14),rot_z=a,mat_index=2)
# gate towers & gate
for s in(-1,1):
    ga=gate+s*(gw/2+step*0.5)
    x,y=cx+math.cos(ga)*R,cy+math.sin(ga)*R; z=ground_h(x,y)
    cyl(bm,(x,y,z+2.1),0.35,0.35,5.0,segs=8,mat_index=0)
xa,ya=cx+math.cos(gate)*R,cy+math.sin(gate)*R; za=ground_h(xa,ya)
box(bm,(xa,ya,za+4.35),(0.3,2*R*math.sin(gw/2)+1.2,0.35),rot_z=gate,mat_index=2)
# open gate doors, swung inward
for s in(-1,1):
    ga=gate+s*(gw/2)
    hx,hy=cx+math.cos(ga)*(R-0.1),cy+math.sin(ga)*(R-0.1)
    inward=Vector((-math.cos(gate),-math.sin(gate),0))
    p=Vector((hx,hy,za+1.6))+inward*0.9
    vs=box(bm,p,(1.8,0.14,3.0),rot_z=gate,mat_index=1)
    vs=box(bm,p+Vector((0,0,0.8)),(1.8,0.2,0.18),rot_z=gate,mat_index=2)
obj_from_bm("Palisade",bm,mats,C)
# watchtower
tx,ty=cx+math.cos(math.radians(207))*12.8,cy+math.sin(math.radians(207))*12.8
tz=min(ground_h(tx+a,ty+b) for a in(-1.5,1.5) for b in(-1.5,1.5))
bm=bmesh.new()
for sx in(-1,1):
    for sy in(-1,1):
        box(bm,(sx*1.3,sy*1.3,3.5),(0.3,0.3,7.4),mat_index=0)
for zz in (1.5,4.0):
    for sx in(-1,1):
        vs=box(bm,(sx*1.3,0,zz+1.2),(0.14,3.2,0.14),mat_index=2)
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((sx*1.3,0,zz+1.2)),matrix=Matrix.Rotation(0.75*sx,3,"X"))
        vs=box(bm,(0,sx*1.3,zz+1.2),(3.2,0.14,0.14),mat_index=2)
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((0,sx*1.3,zz+1.2)),matrix=Matrix.Rotation(0.75*sx,3,"Y"))
box(bm,(0,0,6.3),(3.6,3.6,0.2),mat_index=1)
for sx in(-1,1):
    box(bm,(sx*1.75,0,6.9),(0.12,3.6,1.0),mat_index=1); box(bm,(0,sx*1.75,6.9),(3.6,0.12,1.0),mat_index=1)
for sx in(-1,1):
    for sy in(-1,1): box(bm,(sx*1.65,sy*1.65,7.9),(0.16,0.16,2.2),mat_index=2)
cyl(bm,(0,0,9.8),3.1,0.1,1.9,segs=4,rot=Matrix.Rotation(math.pi/4,4,"Z"),mat_index=3)
# ladder
for sx in(-0.35,0.35):
    vs=box(bm,(sx,-2.0,3.2),(0.1,0.1,6.6),mat_index=2)
    bmesh.ops.rotate(bm,verts=vs,cent=Vector((sx,-2.0,3.2)),matrix=Matrix.Rotation(-0.12,3,"X"))
for k in range(14):
    zz=0.4+k*0.45; box(bm,(0,-2.0+ (zz-3.2)*0.12,zz),(0.8,0.07,0.07),mat_index=2)
# flag
box(bm,(1.65,1.65,11.2),(0.07,0.07,2.6),mat_index=2)
box(bm,(1.65,2.25,11.8),(0.04,1.1,0.8),mat_index=5)
box(bm,(1.66,2.25,11.8),(0.05,0.4,0.3),mat_index=6)
obj_from_bm("Watchtower",bm,mats,C,loc=(tx,ty,tz),rot=(0,0,math.radians(207-90)))
# clear trees overlapping walls
rm=0
for o in list(col("Nature").objects):
    d=math.hypot(o.location.x-cx,o.location.y-cy); ang=math.atan2(o.location.y-cy,o.location.x-cx)%(2*math.pi)
    if abs(d-R)<2.2 and a0-0.1<ang<a1+0.1: bpy.data.objects.remove(o); rm+=1
    elif math.hypot(o.location.x-tx,o.location.y-ty)<3.5: bpy.data.objects.remove(o); rm+=1
print("defenses ok, trees removed",rm)
# ---- result ----
# {"result":"Code executed successfully: defenses ok, trees removed 7\n"}

# ==============================================================================================================
# [0018] 2026-09-23 01:21:44  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Props")
for ob in list(C.objects): bpy.data.objects.remove(ob)
for l in [o for o in bpy.data.objects if o.type=="LIGHT" and o.name.startswith("PL_")]: bpy.data.objects.remove(l)
wood=mat("CrateWood",(0.52,0.36,0.20),0.8); timber=mat("Timber",(0.18,0.11,0.06),0.8)
iron=mat("Iron",(0.25,0.25,0.27),0.4,metal=0.8); sack=mat("Sack",(0.72,0.63,0.45),1.0)
stone=mat("Stone",(0.33,0.31,0.29),0.9); fire=mat("Fire",(1,0.5,0.1),0.5,emit=(1.0,0.45,0.08),emit_str=12)
cloth=[mat("ClothRed",(0.60,0.12,0.10),0.9),mat("ClothBlue",(0.15,0.25,0.55),0.9),mat("ClothStripe",(0.85,0.75,0.45),0.9)]
apple=mat("Apples",(0.70,0.12,0.08),0.5); veg=mat("Cabbage",(0.30,0.55,0.18),0.6); bark=mat("Bark",(0.24,0.16,0.10),0.9)
coal=mat("Coal",(0.05,0.05,0.05),0.9); wool=mat("Wool",(0.92,0.90,0.84),1.0); sheepface=mat("SheepFace",(0.12,0.10,0.09),0.8)
mats=[wood,timber,iron,sack,stone,fire,cloth[0],cloth[1],cloth[2],apple,veg,bark,coal,wool,sheepface]
MI={m.name[3:]:i for i,m in enumerate(mats)}
rnd=random.Random(9)
def gz(x,y): return ground_h(x,y)
def crate(bm,x,y,z,s=0.8,rz=0):
    box(bm,(x,y,z+s/2),(s,s,s),rot_z=rz,mat_index=MI["CrateWood"])
    for dz in(0.06,s-0.06):
        box(bm,(x,y,z+dz),(s+0.04,s+0.04,0.1),rot_z=rz,mat_index=MI["Timber"])
def barrel(bm,x,y,z,r=0.38,h=0.95):
    cyl(bm,(x,y,z+h*0.25),r*0.88,r,h*0.5,segs=10,mat_index=MI["CrateWood"])
    cyl(bm,(x,y,z+h*0.75),r,r*0.88,h*0.5,segs=10,mat_index=MI["CrateWood"])
    for zz in(0.12,h-0.12): cyl(bm,(x,y,z+zz),r*0.92,r*0.92,0.07,segs=10,mat_index=MI["Iron"])
def sackf(bm,x,y,z):
    ico(bm,(x,y,z+0.3),0.35,sub=1,scale=(1,0.8,1.0),jitter=0.04,mat_index=MI["Sack"],seed=int(x*50+y))
# ---- stockpile zone
bm=bmesh.new(); sx,sy=-5.0,-3.3; z=gz(sx,sy)
for i in range(3):
    for j in range(2): crate(bm,sx-1.2+i*0.9,sy+j*0.9,gz(sx-1.2+i*0.9,sy+j*0.9)-0.05,rz=rnd.uniform(-.1,.1))
crate(bm,sx-0.75,sy+0.45,gz(sx,sy)+0.72,rz=0.3)
for i in range(4): barrel(bm,sx+1.6+(i%2)*0.8,sy+(i//2)*0.8-0.3,gz(sx+1.6,sy)-0.05)
for i in range(6): sackf(bm,sx-1.4+i*0.55,sy-1.3,gz(sx,sy-1.3)-0.05)
# zone corner markers (colony sim stockpile)
for cxs in(-2.2,2.9):
    for cys in(-2.0,1.7): box(bm,(sx+cxs,sy+cys,gz(sx+cxs,sy+cys)+0.3),(0.12,0.12,0.7),mat_index=MI["Timber"])
obj_from_bm("Stockpile",bm,mats,C)
# ---- campfire
fx,fy=3.0,-1.3; fz=gz(fx,fy); bm=bmesh.new()
for k in range(9):
    a=k/9*6.28; ico(bm,(fx+math.cos(a)*0.75,fy+math.sin(a)*0.75,fz+0.1),0.22,sub=0,jitter=0.04,mat_index=MI["Stone"],seed=k)
for k in range(5):
    a=k/5*6.28; vs=cyl(bm,(0,0,0),0.09,0.07,1.1,segs=5,mat_index=MI["Bark"])
    bmesh.ops.transform(bm,verts=vs,matrix=Matrix.Translation((fx+math.cos(a)*0.25,fy+math.sin(a)*0.25,fz+0.35))@Matrix.Rotation(0.75,4,Vector((-math.sin(a),math.cos(a),0))))
ico(bm,(fx,fy,fz+0.45),0.3,sub=1,scale=(1,1,1.8),jitter=0.06,mat_index=MI["Fire"],seed=3)
ico(bm,(fx+0.1,fy-0.05,fz+0.35),0.22,sub=1,scale=(1,1,1.5),jitter=0.05,mat_index=MI["Fire"],seed=4)
# log benches
for a in (0.9,2.6,4.4):
    bx,by=fx+math.cos(a)*2.0,fy+math.sin(a)*2.0
    cyl(bm,(bx,by,gz(bx,by)+0.22),0.25,0.25,1.6,segs=8,rot=Matrix.Rotation(a,4,"Z")@Matrix.Rotation(math.pi/2,4,"X"),mat_index=MI["Bark"])
obj_from_bm("Campfire",bm,mats,C)
ld=bpy.data.lights.new("PL_Campfire","POINT"); ld.energy=180; ld.color=(1,0.55,0.2); ld.shadow_soft_size=0.3
lo=bpy.data.objects.new("PL_Campfire",ld); col("Lighting").objects.link(lo); lo.location=(fx,fy,fz+1.0)
# ---- market stalls
def stall(name,x,y,cl,goods,rz):
    bm=bmesh.new()
    for sx in(-1,1):
        for sy in(-1,1): box(bm,(sx*1.3,sy*0.8,1.2 if sy<0 else 1.4),(0.12,0.12,2.4 if sy<0 else 2.8),mat_index=MI["Timber"])
    box(bm,(0,-0.4,0.9),(2.7,1.0,0.12),mat_index=MI["CrateWood"])
    box(bm,(0,-0.85,0.5),(2.7,0.08,0.8),mat_index=MI["CrateWood"])
    # striped awning
    for k in range(6):
        vs=box(bm,(-1.35+0.225+k*0.45,-0.1,2.55),(0.45,2.2,0.05),mat_index=cl if k%2 else MI["ClothStripe"])
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((0,-0.1,2.55)),matrix=Matrix.Rotation(-0.25,3,"X"))
    for i in range(5):
        for j in range(2):
            ico(bm,(-1.0+i*0.5,-0.6+j*0.35,1.07),0.15 if goods=="Apples" else 0.2,sub=1,jitter=0.02,mat_index=MI[goods],seed=i*3+j)
    crate(bm,1.8,0.2,0,0.6); barrel(bm,-1.9,0.3,0,0.3,0.8)
    return obj_from_bm(name,bm,mats,C,loc=(x,y,gz(x,y)),rot=(0,0,rz))
stall("MarketStall_A",3.6,4.6,MI["ClothRed"],"Apples",face_rot(3.6,4.6,-1,1))
stall("MarketStall_B",-6.4,2.6,MI["ClothBlue"],"Cabbage",face_rot(-6.4,2.6,-1,1))
# ---- blacksmith forge
fx,fy=10.2,-9.0; fz=min(gz(fx+a,fy+b) for a in(-2,2) for b in(-2,2)); bm=bmesh.new()
box(bm,(0,0,-0.4),(4.6,3.6,1.0),mat_index=MI["Stone"])
for sx in(-1,1):
    for sy in(-1,1): box(bm,(sx*2.0,sy*1.5,1.6),(0.2,0.2,3.2),mat_index=MI["Timber"])
prism_roof(bm,(0,0,3.1),4.2,3.2,1.3,over=0.3,thick=0.14,mat_index=MI["Timber"])
box(bm,(-1.2,0.8,0.7),(1.4,1.3,1.1),mat_index=MI["Stone"])
box(bm,(-1.2,0.8,1.28),(1.0,0.9,0.06),mat_index=MI["Fire"])
box(bm,(-1.2,1.1,3.0),(0.7,0.7,4.0),mat_index=MI["Stone"])
box(bm,(0.8,-0.2,0.55),(0.5,0.5,0.7),mat_index=MI["Bark"])
box(bm,(0.8,-0.2,1.02),(0.8,0.3,0.25),mat_index=MI["Iron"])
cyl(bm,(0.8,-0.2,1.15),0.12,0.02,0.4,segs=6,rot=Matrix.Rotation(math.pi/2,4,"Y")@Matrix.Translation((0,0,0.5)),mat_index=MI["Iron"])
barrel(bm,1.5,1.0,0.1,0.35,0.8)
for k in range(4): box(bm,(-1.9,-0.8+k*0.3,1.6),(0.05,0.08,0.9),mat_index=MI["Iron"])
obj_from_bm("Blacksmith",bm,mats,C,loc=(fx,fy,fz+0.1),rot=(0,0,face_rot(fx,fy,-1,1)))
ld=bpy.data.lights.new("PL_Forge","POINT"); ld.energy=90; ld.color=(1,0.45,0.15)
lo=bpy.data.objects.new("PL_Forge",ld); col("Lighting").objects.link(lo)
lo.parent=bpy.data.objects["Blacksmith"]; lo.location=(-1.2,0.8,1.9)
# ---- sheep pen + sheep
px,py=6.0,15.5
for o in list(col("Nature").objects):
    if abs(o.location.x-px)<5 and abs(o.location.y-py)<4.2: bpy.data.objects.remove(o)
bm=bmesh.new()
pts=[(px-3.5,py-2.8),(px+3.5,py-2.8),(px+3.5,py+2.8),(px-3.5,py+2.8)]
for i in range(4):
    a=Vector((*pts[i],0)); b=Vector((*pts[(i+1)%4],0)); n=int((b-a).length/1.75)
    ang=math.atan2(b.y-a.y,b.x-a.x)
    for k in range(n+1):
        p=a+(b-a)*k/n; box(bm,(p.x,p.y,gz(p.x,p.y)+0.45),(0.13,0.13,1.0),mat_index=MI["Timber"])
    for k in range(n):
        if i==0 and k==1: continue
        p=a+(b-a)*(k+0.5)/n; z=gz(p.x,p.y)
        for hh in(0.35,0.75): box(bm,(p.x,p.y,z+hh),((b-a).length/n+0.1,0.07,0.09),rot_z=ang,mat_index=MI["Timber"])
box(bm,(px+2.7,py+2.0,gz(px+2.7,py+2.0)+0.25),(1.6,0.5,0.4),mat_index=MI["CrateWood"])
obj_from_bm("SheepPen",bm,mats,C)
for i in range(6):
    bm=bmesh.new(); r2=random.Random(i+300)
    ico(bm,(0,0,0.55),0.5,sub=1,scale=(1.35,0.9,0.85),jitter=0.06,mat_index=MI["Wool"],seed=i)
    box(bm,(0.68,0,0.62),(0.35,0.26,0.3),mat_index=MI["SheepFace"])
    for ex in(-1,1): box(bm,(0.62,ex*0.17,0.72),(0.08,0.16,0.06),mat_index=MI["SheepFace"])
    for lx in(-0.35,0.35):
        for ly in(-0.2,0.2): box(bm,(lx,ly,0.15),(0.09,0.09,0.32),mat_index=MI["SheepFace"])
    x=px+r2.uniform(-2.6,2.6); y=py+r2.uniform(-1.9,1.9)
    obj_from_bm(f"Sheep_{i}",bm,mats,C,loc=(x,y,gz(x,y)-0.03),rot=(0,0,r2.uniform(0,6.28)))
print("props ok")
# ---- result ----
# {"result":"Code executed successfully: props ok\n"}

# ==============================================================================================================
# [0019] 2026-09-23 01:22:17  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
C=col("Colonists")
for ob in list(C.objects): bpy.data.objects.remove(ob)
skin=[mat("Skin1",(0.85,0.62,0.48),0.6),mat("Skin2",(0.62,0.42,0.30),0.6),mat("Skin3",(0.40,0.26,0.18),0.6)]
hair=[mat("HairBrown",(0.22,0.13,0.07),0.8),mat("HairBlond",(0.75,0.58,0.30),0.8),mat("HairBlack",(0.05,0.04,0.04),0.8),mat("HairRed",(0.55,0.22,0.08),0.8)]
tun={k:mat("Tunic"+k,c,0.9) for k,c in {"Green":(0.22,0.35,0.15),"Red":(0.55,0.15,0.10),"Blue":(0.18,0.28,0.50),"Brown":(0.40,0.28,0.16),"Ochre":(0.72,0.55,0.20),"Grey":(0.45,0.45,0.43)}.items()}
pants=mat("Pants",(0.20,0.17,0.14),0.9); boots=mat("Boots",(0.12,0.08,0.05),0.8)
timber=mat("Timber",(0.18,0.11,0.06),0.8); iron=mat("Iron",(0.25,0.25,0.27),0.4,metal=0.8); apron=mat("Apron",(0.30,0.22,0.15),0.8)
def colonist(name,x,y,rz,tunic,sk=0,hr=0,tool=None,pose="stand",hat=False,seed=0):
    ms=[skin[sk],hair[hr],tun[tunic],pants,boots,timber,iron,apron]
    bm=bmesh.new(); sit=pose=="sit"
    hip=0.45 if sit else 0.8
    # legs
    for s in(-1,1):
        if sit:
            box(bm,(0.22,s*0.11,0.45),(0.45,0.14,0.14),mat_index=3); box(bm,(0.45,s*0.11,0.22),(0.14,0.14,0.45),mat_index=3)
            box(bm,(0.5,s*0.11,0.04),(0.24,0.14,0.08),mat_index=4)
        else:
            box(bm,(0,s*0.11,0.42),(0.15,0.15,0.75),mat_index=3); box(bm,(0.04,s*0.11,0.06),(0.24,0.16,0.12),mat_index=4)
    # torso tunic (flared)
    cyl(bm,(0,0,hip+0.35),0.30,0.21,0.72,segs=8,mat_index=2)
    cyl(bm,(0,0,hip+0.72),0.12,0.12,0.14,segs=6,mat_index=2)
    box(bm,(0,0,hip+0.05),(0.36,0.4,0.06),mat_index=4)   # belt
    if tool=="hammer": cyl(bm,(0.1,0,hip+0.25),0.29,0.2,0.6,segs=8,mat_index=7)
    # head
    ico(bm,(0,0,hip+0.98),0.2,sub=2,scale=(1,0.95,1.1),mat_index=0)
    ico(bm,(-0.03,0,hip+1.05),0.205,sub=2,scale=(1,1,0.9),mat_index=1)
    box(bm,(0.19,0,hip+0.97),(0.05,0.06,0.07),mat_index=0) #nose
    if hat: cyl(bm,(0,0,hip+1.2),0.24,0.1,0.25,segs=8,mat_index=2)
    # arms
    arm_up=tool in("axe","hoe","spear","rod")
    for s in(-1,1):
        if arm_up and s<0:
            vs=box(bm,(0.18,s*0.27,hip+0.55),(0.12,0.12,0.5),mat_index=2)
            bmesh.ops.rotate(bm,verts=vs,cent=Vector((0,s*0.27,hip+0.68)),matrix=Matrix.Rotation(-1.1,3,"Y"))
            ico(bm,(0.42,s*0.27,hip+0.5),0.065,sub=1,mat_index=0)
        else:
            box(bm,(0,s*0.27,hip+0.45),(0.12,0.12,0.5),mat_index=2); ico(bm,(0,s*0.27,hip+0.17),0.065,sub=1,mat_index=0)
    # tools
    if tool=="axe":
        vs=box(bm,(0.5,-0.27,hip+0.8),(0.06,0.06,1.0),mat_index=5); box(bm,(0.5,-0.36,hip+1.25),(0.05,0.22,0.18),mat_index=6)
    elif tool=="hoe":
        box(bm,(0.45,-0.27,hip+0.4),(0.05,0.05,1.7),mat_index=5); box(bm,(0.55,-0.27,hip-0.43),(0.22,0.18,0.04),mat_index=6)
    elif tool=="spear":
        box(bm,(0.42,-0.27,hip+0.6),(0.05,0.05,2.3),mat_index=5); cyl(bm,(0.42,-0.27,hip+1.85),0.06,0.0,0.3,segs=4,mat_index=6)
    elif tool=="rod":
        vs=box(bm,(0.42,-0.27,hip+0.5),(0.04,0.04,2.6),mat_index=5)
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((0.42,-0.27,hip+0.5)),matrix=Matrix.Rotation(0.9,3,"Y"))
    elif tool=="hammer":
        box(bm,(0.1,-0.3,hip+0.3),(0.04,0.04,0.4),mat_index=5)
    o=obj_from_bm(name,bm,ms,C,loc=(x,y,ground_h(x,y)+(0.0)),rot=(0,0,rz))
    o["job"]=name.split("_")[1]
    return o
def look(x,y,tx,ty): return math.atan2(ty-y,tx-x)
fx,fy=3.0,-1.3
people=[
 ("Colonist_Woodcutter_0",6.8,-22.8,None,"Green",0,0,"axe","stand",False),
 ("Colonist_Woodcutter_1",10.0,-21.5,None,"Brown",1,2,"axe","stand",True),
 ("Colonist_Farmer_0",20.2,-3.6,None,"Ochre",0,1,"hoe","stand",True),
 ("Colonist_Farmer_1",26.5,-1.0,None,"Brown",2,2,"hoe","stand",False),
 ("Colonist_Farmer_2",-20.5,-8.4,None,"Green",0,3,"hoe","stand",True),
 ("Colonist_Smith_0",10.8,-8.3,None,"Grey",1,2,"hammer","stand",False),
 ("Colonist_Merchant_0",3.9,5.9,None,"Red",0,1,None,"stand",True),
 ("Colonist_Merchant_1",-7.6,2.9,None,"Blue",2,0,None,"stand",False),
 ("Colonist_Fisher_0",-8.0,-12.0,None,"Blue",0,3,"rod","stand",True),
 ("Colonist_Hauler_0",-3.0,-2.0,None,"Brown",1,0,None,"stand",False),
 ("Colonist_Villager_0",fx+1.4,fy+1.4,"fire","Red",0,1,None,"sit",False),
 ("Colonist_Villager_1",fx-1.5,fy+1.3,"fire","Ochre",2,2,None,"sit",False),
 ("Colonist_Villager_2",fx-0.6,fy-1.9,"fire","Green",1,3,None,"sit",False),
 ("Colonist_Villager_3",-0.2,-4.8,None,"Blue",0,0,None,"stand",False),
 ("Colonist_Villager_4",0.2,-5.3,None,"Red",1,1,None,"stand",True),
 ("Colonist_Shepherd_0",8.8,13.3,None,"Ochre",0,0,"spear","stand",True),
]
rnd=random.Random(4)
for n,x,y,tg,tc,sk,hr,tool,pose,hat in people:
    if tg=="fire": rz=look(x,y,fx,fy)
    elif "Fisher" in n: rz=math.atan2(river_y(x)-y,0)  # face the river
    elif "Merchant_0" in n: rz=look(x,y,3.6,4.6)+math.pi
    elif "Merchant_1" in n: rz=look(x,y,-6.4,2.6)+math.pi
    elif "Villager_3" in n: rz=look(x,y,0.2,-5.3)
    elif "Villager_4" in n: rz=look(x,y,-0.2,-4.8)
    elif "Smith" in n: rz=look(x,y,10.2,-9.0)
    else: rz=rnd.uniform(0,6.28)
    colonist(n,x,y,rz,tc,sk,hr,tool,pose,hat)
# guard on the watchtower
wt=bpy.data.objects["Watchtower"]
g=colonist("Colonist_Guard_0",0,0,0,"Red",1,2,"spear","stand",True)
g.parent=wt; g.location=(0.6,0.4,6.4); g.rotation_euler=(0,0,-math.pi/2)
print(len(C.objects))
# ---- result ----
# {"result":"Code executed successfully: 17\n"}

# ==============================================================================================================
# [0020] 2026-09-23 01:22:26  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
f=bpy.data.objects["Colonist_Fisher_0"]; x=-9.5; y=river_y(x)+2.9
f.location=(x,y,ground_h(x,y)); f.rotation_euler.z=-math.pi/2
cam=bpy.data.objects["Camera_Close"]; cam.location=(14,-20,10)
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0021] 2026-09-23 01:22:55  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["mc_helpers"].as_string())
# ---- smoke
C=col("FX")
for ob in list(C.objects): bpy.data.objects.remove(ob)
sm=mat("Smoke",(0.75,0.74,0.72),1.0)
b=next(n for n in sm.node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Alpha"].default_value=0.55
try: sm.surface_render_method="BLENDED"
except: pass
bm=bmesh.new(); rnd=random.Random(1)
for o in col("Buildings").objects:
    if "chimney_top" not in o: continue
    p=o.matrix_world@Vector(tuple(o["chimney_top"]))
    for k in range(5):
        r=0.25+k*0.13
        ico(bm,(p.x+k*0.35+rnd.uniform(-.1,.1),p.y+k*0.25,p.z+0.2+k*0.55),r,sub=1,jitter=0.04,seed=k)
# forge smoke
bs=bpy.data.objects["Blacksmith"]; p=bs.matrix_world@Vector((-1.2,1.1,5.1))
for k in range(4): ico(bm,(p.x+k*0.3,p.y+k*0.2,p.z+k*0.5),0.25+k*0.12,sub=1,jitter=0.04,seed=k+9)
obj_from_bm("ChimneySmoke",bm,sm,C)
# ---- construction site
C=col("Construction")
for ob in list(C.objects): bpy.data.objects.remove(ob)
x,y=-16.0,11.5
for o in list(col("Nature").objects):
    if math.hypot(o.location.x-x,o.location.y-y)<5.5: bpy.data.objects.remove(o)
MH=M_house(); cut=mat("CutWood",(0.78,0.60,0.38),0.8); rope=mat("Rope",(0.6,0.5,0.3),1)
mats=MH+[cut]
rz=face_rot(x,y,-1,1)
w,d,H=5.0,3.6,2.4
z0=min(ground_h(x+a,y+b) for a in(-3,3) for b in(-2,2)); zc=ground_h(x,y); base=max(zc,z0)+0.35-zc
bm=bmesh.new()
box(bm,(0,0,(z0-1.0-zc+base)/2),(w+0.3,d+0.3,base-(z0-1.0-zc)),mat_index=0)
t=0.16
for sx in(-1,0,1):
    for sy in(-1,1): box(bm,(sx*(w/2-t/2),sy*(d/2-t/2),base+H/2),(t,t,H),mat_index=7)
for sy in(-1,1): box(bm,(0,sy*(d/2-t/2),base+H),(w,t,t),mat_index=7)
for sx in(-1,1): box(bm,(sx*(w/2-t/2),0,base+H),(t,d,t),mat_index=7)
# rafters (half done)
for k in range(4):
    xx=-w/2+0.2+k*1.2
    for sy in(-1,1):
        vs=box(bm,(xx,sy*d/4,base+H+d*0.31),(0.12,math.hypot(d/2,d*0.62)+0.2,0.12),mat_index=7)
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((xx,sy*d/4,base+H+d*0.31)),matrix=Matrix.Rotation(-sy*math.atan2(d*0.62,d/2),3,"X"))
box(bm,(-w/2+0.2+1.8,0,base+H+d*0.62),(3.8,0.14,0.14),mat_index=7)
# partial back wall (plaster infill)
box(bm,(-0.6,d/2-0.08,base+H*0.35),(w*0.7,0.12,H*0.7),mat_index=1)
# scaffold
for k in range(3):
    xx=-w/2+k*w/2
    box(bm,(xx,-d/2-0.9,base+1.6),(0.1,0.1,3.4),mat_index=2)
box(bm,(0,-d/2-0.9,base+1.9),(w+0.4,0.12,0.12),mat_index=2)
box(bm,(0,-d/2-0.65,base+1.95),(w+0.4,0.6,0.06),mat_index=7)
# plank pile & stone pile
for k in range(6):
    box(bm,(w/2+1.6,-1.0+k*0.02,base-0.2+k*0.09),(0.35+0.0,3.2,0.08),rot_z=0.02*k,mat_index=7)
for k in range(10):
    r=random.Random(k)
    ico(bm,(-w/2-1.4+r.uniform(-.5,.5),r.uniform(-.8,.8),base-0.2+r.uniform(0,.3)),0.3,sub=0,jitter=0.05,mat_index=0,seed=k)
obj_from_bm("ConstructionSite_House",bm,mats,C,loc=(x,y,zc),rot=(0,0,rz))
# builder colonist (reuse smith mesh style)
src=bpy.data.objects["Colonist_Smith_0"]
bld=src.copy(); bld.data=src.data; bld.name="Colonist_Builder_0"; col("Colonists").objects.link(bld)
bx,by=x+math.sin(rz)*3.0,y-math.cos(rz)*3.0
bld.location=(bx,by,ground_h(bx,by)); bld.rotation_euler=(0,0,rz+math.pi/2); bld["job"]="Builder"
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0022] 2026-09-23 01:23:08  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["mc_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
e=SC.eevee
for k,v in {"taa_render_samples":48,"use_raytracing":True,"use_shadows":True,"shadow_ray_count":2,"use_gtao":True}.items():
    if hasattr(e,k):
        try: setattr(e,k,v)
        except Exception as ex: print(k,ex)
cam=bpy.data.objects["Camera_Hero"]; cam.data.lens=40
cam.location=(46,-52,38)
cam.rotation_euler=(Vector((0,-1.5,-3))-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam
SC.render.resolution_percentage=40
SC.render.filepath=os.path.join(out,"test_hero.png")
bpy.ops.render.render(write_still=True, scene=SC.name)
print("rendered")
# ---- result ----
# {"result":"Code executed successfully: rendered\n"}

# ==============================================================================================================
# [0023] 2026-09-23 01:23:27  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["mc_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cam=bpy.data.objects["Camera_Hero"]; cam.data.lens=29
cam.location=(50,-56,44)
cam.rotation_euler=(Vector((0,-1,-3.5))-cam.location).to_track_quat("-Z","Y").to_euler()
cc=bpy.data.objects["Camera_Close"]; cc.data.lens=32
cc.location=(13,-17,7.5)
cc.rotation_euler=(Vector((-1,1,1.0))-cc.location).to_track_quat("-Z","Y").to_euler()
SC.render.resolution_percentage=100
for camname,fn in (("Camera_Hero","colony_overview.png"),("Camera_Close","colony_closeup.png")):
    SC.camera=bpy.data.objects[camname]
    SC.render.filepath=os.path.join(out,fn)
    bpy.ops.render.render(write_still=True, scene=SC.name)
SC.camera=cam
os.remove(os.path.join(out,"test_hero.png"))
print("done")
# ---- result ----
# {"result":"Code executed successfully: done\n"}

# ==============================================================================================================
# [0024] 2026-09-23 01:23:49  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["mc_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cc=bpy.data.objects["Camera_Close"]; cc.data.lens=26
cc.location=(10.5,-4.5,4.2)
cc.rotation_euler=(Vector((-3,2,1.6))-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.resolution_percentage=40
SC.render.filepath=os.path.join(out,"colony_closeup.png")
bpy.ops.render.render(write_still=True, scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0025] 2026-09-23 01:24:03  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["mc_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cc=bpy.data.objects["Camera_Close"]; cc.data.lens=38
cc.location=(-4,-22,15)
cc.rotation_euler=(Vector((-1.5,0,0.5))-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.resolution_percentage=40
SC.render.filepath=os.path.join(out,"colony_closeup.png")
bpy.ops.render.render(write_still=True, scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0026] 2026-09-23 01:24:15  blender  ok
# ==============================================================================================================
import bpy, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC=bpy.data.scenes["MedievalColony"]
sm=bpy.data.objects["ChimneySmoke"]; sm.hide_render=True
SC.render.resolution_percentage=100
SC.camera=bpy.data.objects["Camera_Close"]
SC.render.filepath=os.path.join(out,"colony_closeup.png")
bpy.ops.render.render(write_still=True, scene=SC.name)
sm.hide_render=False
SC.camera=bpy.data.objects["Camera_Hero"]
# summary
print({c.name:len(c.all_objects) for c in SC.collection.children})
# ---- result ----
# {"result":"Code executed successfully: {'Terrain': 2, 'Lighting': 5, 'Buildings': 8, 'Landmarks': 4, 'Farms': 6, 'MC_Assets': 18, 'Nature': 183, 'Lumb
# erCamp': 2, 'Defenses': 2, 'Props': 12, 'Colonists': 18, 'FX': 1, 'Construction': 1}\n"}

# ==============================================================================================================
# [0027] 2026-09-23 01:27:37  blender  ok
# ==============================================================================================================
import bpy
code = r'''
exec(bpy.data.texts["mc_helpers"].as_string())
SC = bpy.data.scenes["StoneWallKit"]
def col(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); (parent or SC.collection).children.link(c)
    return c
CELL=4.0; H=4.0; T=1.4; PAR=0.45; MERL_H=0.8; PAR_H=0.55
def kit_mats():
    return [mat("WK_StoneA",(0.46,0.44,0.40),0.85), mat("WK_StoneB",(0.38,0.37,0.35),0.9), mat("WK_StoneC",(0.52,0.48,0.42),0.85),
            mat("WK_Mortar",(0.16,0.15,0.14),1.0), mat("WK_Walkway",(0.40,0.38,0.35),0.9), mat("WK_Moss",(0.26,0.34,0.14),0.9),
            mat("WK_Wood",(0.33,0.21,0.11),0.8), mat("WK_Iron",(0.20,0.20,0.22),0.45,metal=0.8), mat("WK_WoodDark",(0.18,0.11,0.06),0.8),
            mat("WK_Banner",(0.55,0.08,0.07),0.8), mat("WK_Roof",(0.40,0.17,0.10),0.7)]
STONE=(0,1,2); MORTAR=3; WALK=4; MOSS=5; WOOD=6; IRON=7; WOODD=8; BANNER=9; ROOF=10
def xf_verts(bm,vs,M):
    bmesh.ops.transform(bm,matrix=M,verts=vs)
def block_face(bm,M,length,z0,z1,seed,course_h=0.42,depth=0.14,moss_h=0.9,block_len=(0.55,0.95),u0=0.0):
    """Stone blocks on a vertical face. Local frame: u along +X from 0..length, face plane y=0, blocks protrude to -Y.
    u0 = global offset along the run so staggering matches across modules."""
    rnd=random.Random(seed)
    z=z0; i=0
    while z<z1-0.05:
        ch=min(course_h*rnd.uniform(0.85,1.15), z1-z)
        if z1-(z+ch)<0.15: ch=z1-z
        # stagger based on global u so neighbours line up
        crs=random.Random(int(z*1000)+7)
        u=-((u0+crs.uniform(0,0.8)) % 0.9)
        while u<length:
            bl=rnd.uniform(*block_len)
            a=max(0.0,u+0.025); b=min(length,u+bl-0.025)
            if b-a>0.08:
                dd=depth*rnd.uniform(0.75,1.15)
                mi=rnd.choice(STONE)
                if z<moss_h and rnd.random()<0.35*(1-z/moss_h): mi=MOSS
                vs=box(bm,((a+b)/2,-dd/2+0.02,z+ch/2),(b-a,dd,ch-0.05),mat_index=mi)
                # slight random tilt / bulge for hand-cut look
                for v in vs:
                    if v.co.y<-dd/2: v.co.y-=rnd.uniform(0,0.03); v.co.z+=rnd.uniform(-0.015,0.015)
                xf_verts(bm,vs,M)
            u+=bl
        z+=ch; i+=1
def frame(origin,direction,normal):
    """Matrix mapping local (u along direction, -Y toward normal, z up) to world."""
    d=Vector(direction).normalized(); n=Vector(normal).normalized()
    # local -Y must map to n  -> local Y maps to -n
    m=Matrix(((d.x,-n.x,0,origin[0]),(d.y,-n.y,0,origin[1]),(0,0,1,origin[2] if len(origin)>2 else 0),(0,0,0,1)))
    return m
def wall_arm(bm,a,b,outer,height=H,seed=0,crenel=True,top=True,plinth=True):
    """Wall run from a to b (2D), outer side normal 'outer'. Core + stone facing + parapet + merlons."""
    a=Vector((*a,0)); b=Vector((*b,0)); d=(b-a); L=d.length; d.normalize()
    n=Vector((*outer,0)).normalized(); side=d.cross(Vector((0,0,1)))  # right side
    mid=(a+b)/2
    ang=math.atan2(d.y,d.x)
    u0=a.dot(d)  # global position along run for stagger
    # core (mortar)
    box(bm,(mid.x,mid.y,height/2),(L,T-0.2,height),rot_z=ang,mat_index=MORTAR)
    # plinth
    if plinth:
        box(bm,(mid.x,mid.y,0.2),(L,T+0.35,0.6),rot_z=ang,mat_index=1)
        box(bm,(mid.x,mid.y,-0.4),(L,T+0.35,0.6),rot_z=ang,mat_index=MORTAR)
    # stone facing both sides
    for s in(1,-1):
        nn=side*s
        o=a+nn*(T/2-0.1)
        # direction must keep local frame right-handed-ish: use d, normal nn
        M=frame((o.x,o.y,0),d,nn)
        block_face(bm,M,L,0.5 if plinth else 0.0,height,seed*13+(1 if s>0 else 2)+int(u0*10),u0=u0)
    if top:
        # walkway
        box(bm,(mid.x,mid.y,height+0.06),(L,T,0.12),rot_z=ang,mat_index=WALK)
        # inner curb
        ci=mid-n*(T/2-0.1)
        box(bm,(ci.x,ci.y,height+0.2),(L,0.2,0.28),rot_z=ang,mat_index=1)
        # outer parapet
        po=mid+n*(T/2-PAR/2)
        box(bm,(po.x,po.y,height+PAR_H/2+0.06),(L,PAR,PAR_H),rot_z=ang,mat_index=0)
        if crenel:
            rnd=random.Random(seed+99)
            k=math.floor(u0)
            # merlons centred on global half-metres (x.5) so modules tile
            c=math.floor(u0)+0.5
            while c<u0+L:
                if c-0.3>=u0-1e-6 and c+0.3<=u0+L+1e-6:
                    p=a+d*(c-u0)+n*(T/2-PAR/2)
                    box(bm,(p.x,p.y,height+0.06+PAR_H+MERL_H/2),(0.62,PAR,MERL_H),rot_z=ang,mat_index=rnd.choice(STONE))
                    box(bm,(p.x,p.y,height+0.06+PAR_H+MERL_H+0.04),(0.7,PAR+0.08,0.08),rot_z=ang,mat_index=1)
                c+=1.0
def pillar(bm,x,y,w=1.9,height=H+0.9,seed=0,cap=True):
    box(bm,(x,y,height/2),(w-0.2,w-0.2,height),mat_index=MORTAR)
    box(bm,(x,y,0.2),(w+0.35,w+0.35,0.6),mat_index=1)
    box(bm,(x,y,-0.4),(w+0.35,w+0.35,0.6),mat_index=MORTAR)
    for k,(dx,dy) in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
        n=Vector((dx,dy,0)); d=Vector((-dy,dx,0))
        o=Vector((x,y,0))+n*(w/2)-d*(w/2)
        M=frame((o.x,o.y,0),-d,n) if False else frame((o.x,o.y,0),d,n)
        block_face(bm,M,w,0.5,height,seed*7+k,block_len=(0.45,0.8),u0=k*0.37)
    if cap:
        box(bm,(x,y,height+0.1),(w+0.15,w+0.15,0.2),mat_index=1)
        rnd=random.Random(seed)
        for cx in(-1,1):
            for cy in(-1,1):
                box(bm,(x+cx*(w/2-0.3),y+cy*(w/2-0.3),height+0.2+0.45),(0.55,0.55,0.9),mat_index=rnd.choice(STONE))
                box(bm,(x+cx*(w/2-0.3),y+cy*(w/2-0.3),height+1.12),(0.65,0.65,0.08),mat_index=1)
def finish(name,bm,coll,loc=(0,0,0)):
    o=obj_from_bm(name,bm,kit_mats(),coll,loc=loc)
    o["kit"]="StoneWall"; o["cell_size_m"]=CELL
    return o
'''
t = bpy.data.texts.get("wk_helpers") or bpy.data.texts.new("wk_helpers")
t.clear(); t.write(code)
sc = bpy.data.scenes.get("StoneWallKit") or bpy.data.scenes.new("StoneWallKit")
bpy.context.window.scene = sc
exec(code)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0028] 2026-09-23 01:27:55  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["wk_helpers"]; s=t.as_string()
s=s.replace("""                xf_verts(bm,vs,M)
            u+=bl""","""                xf_verts(bm,vs,M)
                if M.to_3x3().determinant()<0:
                    bmesh.ops.reverse_faces(bm,faces=list({f for v in vs for f in v.link_faces}))
            u+=bl""")
t.clear(); t.write(s)
exec(s)
K=col("Kit_Pieces")
for o in list(K.objects): bpy.data.objects.remove(o)
pieces={}
def P(name,fn):
    bm=bmesh.new(); fn(bm); pieces[name]=finish(name,bm,K)
# Straight
P("SM_Wall_Straight", lambda bm: wall_arm(bm,(-2,0),(2,0),(0,-1),seed=1))
# Corner: interior toward +X+Y
def corner(bm):
    wall_arm(bm,(0,0),(2,0),(0,-1),seed=2); wall_arm(bm,(0,0),(0,2),(-1,0),seed=3); pillar(bm,0,0,seed=4)
P("SM_Wall_Corner",corner)
def tee(bm):
    wall_arm(bm,(-2,0),(2,0),(0,-1),seed=5); wall_arm(bm,(0,0),(0,2),(-1,0),seed=6); pillar(bm,0,0,seed=7)
P("SM_Wall_T",tee)
def cross(bm):
    wall_arm(bm,(-2,0),(2,0),(0,-1),seed=8); wall_arm(bm,(0,-2),(0,2),(-1,0),seed=9); pillar(bm,0,0,seed=10)
P("SM_Wall_Cross",cross)
def endcap(bm):
    wall_arm(bm,(-2,0),(0,0),(0,-1),seed=11); pillar(bm,0,0,w=1.9,seed=12)
P("SM_Wall_End",endcap)
print(list(pieces))
# ---- result ----
# {"result":"Code executed successfully: ['SM_Wall_Straight', 'SM_Wall_Corner', 'SM_Wall_T', 'SM_Wall_Cross', 'SM_Wall_End']\n"}

# ==============================================================================================================
# [0029] 2026-09-23 01:28:07  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
SC.world=bpy.data.worlds[bpy.data.scenes["MedievalColony"].world.name]
L=col("WK_Lighting")
if "WK_Sun" not in bpy.data.objects:
    so=bpy.data.objects.new("WK_Sun",bpy.data.lights["MC_Sun"]); L.objects.link(so)
    so.rotation_euler=bpy.data.objects["Sun"].rotation_euler.copy()
cd=bpy.data.cameras.get("WK_Cam") or bpy.data.cameras.new("WK_Cam")
cam=bpy.data.objects.get("WK_Camera_Kit") or bpy.data.objects.new("WK_Camera_Kit",cd)
if cam.name not in L.objects: L.objects.link(cam)
SC.camera=cam
SC.view_settings.look=bpy.data.scenes["MedievalColony"].view_settings.look
SC.view_settings.exposure=-0.3
SC.render.resolution_x=1920; SC.render.resolution_y=1080
for k,v in {"taa_render_samples":48,"use_raytracing":True,"use_gtao":True}.items():
    if hasattr(SC.eevee,k): setattr(SC.eevee,k,v)
for i,o in enumerate(col("Kit_Pieces").objects): o.location=(i*6.5,0,0)
cd.lens=35; cam.location=(13,-20,13)
cam.rotation_euler=(Vector((13,0,2))-cam.location).to_track_quat("-Z","Y").to_euler()
for area in bpy.context.window.screen.areas:
    if area.type=="VIEW_3D":
        area.spaces.active.shading.type="RENDERED"; area.spaces.active.region_3d.view_perspective="CAMERA"
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0030] 2026-09-23 01:28:17  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
cam=bpy.data.objects["WK_Camera_Kit"]; cam.data.lens=35
cam.location=(9,-9,7)
cam.rotation_euler=(Vector((4,0,2.2))-cam.location).to_track_quat("-Z","Y").to_euler()
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0031] 2026-09-23 01:29:20  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
for n,c in {"WK_StoneA":(0.40,0.37,0.33),"WK_StoneB":(0.32,0.30,0.28),"WK_StoneC":(0.46,0.41,0.35)}.items():
    next(x for x in bpy.data.materials["MC_"+n].node_tree.nodes if x.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(*c,1)
K=col("Kit_Pieces")
for n in ["SM_Wall_Gatehouse","SM_Tower_Round","SM_Tower_Round_Roofed","SM_Wall_Stairs","SM_Wall_Ruined"]:
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
def flipfix(bm,vs):
    pass
# ---------- Gatehouse
def gatehouse(bm):
    GH=6.6; D=3.2; ow=1.15; spring=2.3
    # core: piers + top
    for sx in(-1,1): box(bm,(sx*(2-(2-ow)/2),0,GH/2),(2-ow,D-0.2,GH),mat_index=MORTAR)
    box(bm,(0,0,(spring+ow+GH)/2),(2*ow,D-0.2,GH-(spring+ow)),mat_index=MORTAR)
    # spandrel fill (stepped under arch ring)
    z=spring
    while z<spring+ow:
        hw=math.sqrt(max(0,ow**2-(z+0.1-spring)**2))
        for sx in(-1,1): box(bm,(sx*(hw+(ow-hw)/2),0,z+0.1),(ow-hw+0.01,D-0.2,0.2),mat_index=MORTAR)
        z+=0.2
    box(bm,(0,0,0.2),(4.35,D+0.35,0.6),mat_index=1); box(bm,(0,0,-0.4),(4.35,D+0.35,0.6),mat_index=MORTAR)
    for sy in(-1,1):
        n=Vector((0,sy,0)); d=Vector((1,0,0))
        # piers
        for x0,x1 in((-2,-ow),(ow,2)):
            block_face(bm,frame((x0,sy*(D/2-0.1),0),d,n),x1-x0,0.5,GH,seed=int(x0*10)+sy*5,u0=x0+2)
        block_face(bm,frame((-ow,sy*(D/2-0.1),0),d,n),2*ow,spring+ow+0.45,GH,seed=40+sy,u0=2-ow)
        # voussoirs
        nv=11
        for k in range(nv):
            a0=math.pi*k/nv; a1=math.pi*(k+1)/nv; am=(a0+a1)/2
            r0,r1=ow,ow+0.45
            pts=[]
            for (r,a) in((r0,a0+0.012),(r0,a1-0.012),(r1,a1-0.012),(r1,a0+0.012)):
                pts.append((math.cos(a)*r,math.sin(a)*r+spring))
            yf=sy*(D/2+0.04); yb=sy*(D/2-0.4)
            vf=[bm.verts.new((x,yf,z)) for x,z in pts]; vb=[bm.verts.new((x,yb,z)) for x,z in pts]
            mi=2 if k%2 else 0
            fs=[bm.faces.new(vf),bm.faces.new(list(reversed(vb)))]
            for i in range(4): fs.append(bm.faces.new((vf[i],vb[i],vb[(i+1)%4],vf[(i+1)%4])))
            for f in fs: f.material_index=mi
            if sy>0: bmesh.ops.reverse_faces(bm,faces=fs)
    # arch soffit (underside)
    for k in range(12):
        a0=math.pi*k/12; a1=math.pi*(k+1)/12
        v=[bm.verts.new((math.cos(a)*ow,y,math.sin(a)*ow+spring)) for a,y in((a0,-D/2),(a1,-D/2),(a1,D/2),(a0,D/2))]
        f=bm.faces.new(v); f.material_index=MORTAR
    for sx in(-1,1):
        v=[bm.verts.new((sx*ow,y,z)) for y,z in((-D/2,0),(D/2,0),(D/2,spring),(-D/2,spring))]
        f=bm.faces.new(v if sx>0 else list(reversed(v))); f.material_index=MORTAR
    # wooden doors (arched tops), set back
    for sx in(-1,1):
        for k in range(5):
            x=sx*(0.11+k*0.21)
            top=spring+math.sqrt(max(0,ow**2-(abs(x)+0.1)**2))-0.05
            box(bm,(x,-0.3,top/2),(0.2,0.12,top),mat_index=WOOD if k%2 else WOODD)
        for zz in(0.6,1.8): box(bm,(sx*0.55,-0.38,zz),(1.0,0.05,0.12),mat_index=IRON)
        cyl(bm,(sx*0.18,-0.42,1.2),0.08,0.08,0.03,segs=8,rot=Matrix.Rotation(math.pi/2,4,"X"),mat_index=IRON)
    # top: floor + merlons on all edges
    box(bm,(0,0,GH+0.06),(4.0,D,0.12),mat_index=WALK)
    for (cx,cy,lx,ly) in((0,-D/2+PAR/2,4.0,PAR),(0,D/2-PAR/2,4.0,PAR),(-2+PAR/2,0,PAR,D),(2-PAR/2,0,PAR,D)):
        box(bm,(cx,cy,GH+PAR_H/2+0.06),(lx,ly,PAR_H),mat_index=0)
    for c in(-1.5,-0.5,0.5,1.5):
        for sy in(-1,1):
            box(bm,(c,sy*(D/2-PAR/2),GH+0.06+PAR_H+MERL_H/2),(0.62,PAR,MERL_H),mat_index=STONE[int(c*2)%3])
    for c in(-0.9,0.9):
        for sx in(-1,1): box(bm,(sx*(2-PAR/2),c,GH+0.06+PAR_H+MERL_H/2),(PAR,0.62,MERL_H),mat_index=1)
    # corbels under parapet front
    for c in [-1.75+i*0.5 for i in range(8)]:
        for sy in(-1,1): box(bm,(c,sy*(D/2+0.12),GH-0.25),(0.22,0.3,0.4),mat_index=1)
    # banner on front
    box(bm,(0,-D/2-0.08,GH-1.2),(1.0,0.04,1.6),mat_index=BANNER)
    box(bm,(0,-D/2-0.1,GH-0.38),(1.2,0.08,0.08),mat_index=WOODD)
    vs=[bm.verts.new(p) for p in((-0.5,-D/2-0.1,GH-2.0),(0.5,-D/2-0.1,GH-2.0),(0,-D/2-0.1,GH-2.45))]
    f=bm.faces.new(vs); f.material_index=BANNER
    # arrow slits
    for sx in(-1,1): box(bm,(sx*1.55,-D/2-0.03,4.6),(0.12,0.1,0.9),mat_index=MORTAR)
bm=bmesh.new(); gatehouse(bm); finish("SM_Wall_Gatehouse",bm,K)
# ---------- Round tower
def tower(bm,roof=False):
    R=2.35; TH=7.2; seg=18
    cyl(bm,(0,0,TH/2),R-0.1,R-0.1,TH,segs=seg,mat_index=MORTAR)
    cyl(bm,(0,0,0.2),R+0.3,R+0.3,0.6,segs=seg,mat_index=1)
    cyl(bm,(0,0,-0.4),R+0.3,R+0.3,0.6,segs=seg,mat_index=MORTAR)
    rnd=random.Random(5); z=0.5
    while z<TH-0.05:
        ch=min(0.42*rnd.uniform(0.85,1.15),TH-z)
        n=int(2*math.pi*R/rnd.uniform(0.65,0.8)); off=rnd.uniform(0,1)
        for k in range(n):
            a=(k+off)/n*2*math.pi; wlen=2*math.pi*R/n-0.05
            mi=rnd.choice(STONE)
            if z<0.9 and rnd.random()<0.35: mi=MOSS
            dd=0.14*rnd.uniform(0.8,1.15)
            box(bm,(math.cos(a)*(R-0.02+dd/2),math.sin(a)*(R-0.02+dd/2),z+ch/2),(dd,wlen,ch-0.05),rot_z=a,mat_index=mi)
        z+=ch
    # arrow slits
    for a in (math.radians(-90),math.radians(-30),math.radians(-150),math.radians(90)):
        for zz in (2.6,5.2):
            box(bm,(math.cos(a)*(R+0.12),math.sin(a)*(R+0.12),zz),(0.14,0.14,0.95),rot_z=a,mat_index=MORTAR)
    # corbel ring + parapet
    for k in range(24):
        a=k/24*2*math.pi
        box(bm,(math.cos(a)*(R+0.2),math.sin(a)*(R+0.2),TH-0.2),(0.4,0.26,0.4),rot_z=a,mat_index=1)
    cyl(bm,(0,0,TH+0.05),R+0.4,R+0.4,0.2,segs=seg,mat_index=1)
    cyl(bm,(0,0,TH+0.07),R-0.1,R-0.1,0.2,segs=seg,mat_index=WALK)
    if roof:
        cyl(bm,(0,0,TH+0.55),R+0.25,R+0.25,0.8,segs=seg,mat_index=0)
        cyl(bm,(0,0,TH+0.95+2.4),R+0.55,0.05,4.8,segs=seg,mat_index=ROOF)
        box(bm,(0,0,TH+6.0),(0.06,0.06,1.4),mat_index=WOODD)
        box(bm,(0,0.35,TH+6.4),(0.03,0.7,0.45),mat_index=BANNER)
    else:
        n=14
        for k in range(n):
            a=k/n*2*math.pi
            box(bm,(math.cos(a)*(R+0.2),math.sin(a)*(R+0.2),TH+0.15+PAR_H/2),(PAR,2*math.pi*(R+0.2)/n+0.02,PAR_H),rot_z=a,mat_index=0)
            if k%2==0:
                box(bm,(math.cos(a)*(R+0.2),math.sin(a)*(R+0.2),TH+0.15+PAR_H+MERL_H/2),(PAR,2*math.pi*(R+0.2)/n*0.95,MERL_H),rot_z=a,mat_index=STONE[k%3])
        # hatch
        box(bm,(0.8,0.8,TH+0.2),(0.9,0.9,0.1),mat_index=WOOD)
bm=bmesh.new(); tower(bm); finish("SM_Tower_Round",bm,K)
bm=bmesh.new(); tower(bm,roof=True); finish("SM_Tower_Round_Roofed",bm,K)
# ---------- Stairs
def stairs(bm):
    wall_arm(bm,(-2,0),(2,0),(0,-1),seed=21)
    n=12; run=3.6/n
    for k in range(n):
        h=(k+1)*H/n; x=-1.8+k*run+run/2
        box(bm,(x,1.2,h/2),(run+0.01,1.0,h),mat_index=MORTAR)
        box(bm,(x,1.2,h-0.1),(run+0.04,1.05,0.2),mat_index=STONE[k%3])
        box(bm,(x,1.72,h/2),(run-0.03,0.08,h-0.25),mat_index=STONE[(k+1)%3])
bm=bmesh.new(); stairs(bm); finish("SM_Wall_Stairs",bm,K)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0032] 2026-09-23 01:29:51  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
K=col("Kit_Pieces")
for n in ["SM_Wall_Ruined","SM_Wall_Straight_Build01","SM_Wall_Straight_Build02"]:
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
def components(bm):
    bm.verts.ensure_lookup_table(); seen=set(); comps=[]
    for v in bm.verts:
        if v in seen: continue
        stack=[v]; comp=[]; seen.add(v)
        while stack:
            x=stack.pop(); comp.append(x)
            for e in x.link_edges:
                o=e.other_vert(x)
                if o not in seen: seen.add(o); stack.append(o)
        comps.append(comp)
    return comps
def cull_above(bm,hfn,keep_mat=None):
    kill=[]
    for comp in components(bm):
        c=sum((v.co for v in comp),Vector())/len(comp)
        size=max(v.co.z for v in comp)-min(v.co.z for v in comp)
        if size>3.0: continue  # core boxes handled separately
        if c.z>hfn(c.x): kill+=comp
    bmesh.ops.delete(bm,geom=kill,context="VERTS")
def core_slices(bm,hfn,x0=-2,x1=2,step=0.25,thick=T-0.2):
    x=x0
    while x<x1-1e-6:
        h=hfn(x+step/2)-0.25
        if h>0.1: box(bm,(x+step/2,0,h/2),(step,thick,h),mat_index=MORTAR)
        x+=step
def rubble(bm,n,seed,area=((-2,2),(-2,2)),z=0.0,avoid_core=True):
    rnd=random.Random(seed)
    for k in range(n):
        x=rnd.uniform(*area[0]); y=rnd.uniform(*area[1])
        if avoid_core and abs(y)<T/2+0.25: y=math.copysign(T/2+0.25+rnd.uniform(0,0.8),y if y!=0 else 1)
        s=rnd.uniform(0.25,0.5)
        vs=box(bm,(x,y,z+s*0.35),(s*rnd.uniform(1,1.6),s,s*0.7),rot_z=rnd.uniform(0,3),mat_index=rnd.choice(STONE+(MOSS,)))
        bmesh.ops.rotate(bm,verts=vs,cent=Vector((x,y,z)),matrix=Matrix.Rotation(rnd.uniform(-.3,.3),3,"X"))
# ---------- Ruined
def ruin_h(x): return 2.2+1.2*math.sin(x*1.7+0.5)+0.6*math.sin(x*4.3)+0.3*noise.noise(Vector((x*2,0.3,0.7)))
bm=bmesh.new()
wall_arm(bm,(-2,0),(2,0),(0,-1),seed=31,top=False)
# remove the monolithic core & cull blocks above jagged line
comps=components(bm)
big=[c for c in comps if max(v.co.z for v in c)-min(v.co.z for v in c)>3.0]
bmesh.ops.delete(bm,geom=[v for c in big for v in c],context="VERTS")
cull_above(bm,ruin_h)
core_slices(bm,ruin_h)
rubble(bm,26,5)
finish("SM_Wall_Ruined",bm,K)
# ---------- Construction stage 1: foundation, one course, stakes & string line, stone pile
def stakes_line(bm):
    for x in(-2,2):
        for y in(-1.2,1.2):
            box(bm,(x*0.98,y,0.35),(0.06,0.06,0.8),mat_index=WOOD)
    for y in(-1.2,1.2): box(bm,(0,y,0.62),(3.9,0.015,0.015),mat_index=WOOD)
def stone_pile(bm,cx,cy,seed,n=14):
    rnd=random.Random(seed)
    for k in range(n):
        lay=k//6
        x=cx+rnd.uniform(-0.6,0.6); y=cy+rnd.uniform(-0.35,0.35)
        box(bm,(x,y,0.14+lay*0.26),(rnd.uniform(0.45,0.7),0.32,0.25),rot_z=rnd.uniform(-.3,.3),mat_index=rnd.choice(STONE))
def scaffold(bm,y,height,lifts):
    for x in(-1.8,0,1.8):
        box(bm,(x,y,height/2+0.1),(0.1,0.1,height+0.4),mat_index=WOOD)
        box(bm,(x,y+math.copysign(0.7,y),height/2+0.1),(0.1,0.1,height+0.4),mat_index=WOOD)
    for zl in lifts:
        box(bm,(0,y+math.copysign(0.35,y),zl),(4.0,0.85,0.06),mat_index=WOODD)
        for yy in(y,y+math.copysign(0.7,y)): box(bm,(0,yy,zl+0.9),(3.9,0.06,0.06),mat_index=WOOD)
    # diagonal brace
    vs=box(bm,(0.9,y+math.copysign(0.75,y),height/2),(math.hypot(1.8,height),0.06,0.08),mat_index=WOOD)
    bmesh.ops.rotate(bm,verts=vs,cent=Vector((0.9,y+math.copysign(0.75,y),height/2)),matrix=Matrix.Rotation(-math.atan2(height,1.8),3,"Y"))
bm=bmesh.new()
wall_arm(bm,(-2,0),(2,0),(0,-1),seed=41,height=0.95,top=False)
stakes_line(bm)
stone_pile(bm,1.2,1.7,3); stone_pile(bm,-1.1,-1.8,4,10)
# mortar tub + trowel
box(bm,(-1.4,1.6,0.2),(0.7,0.5,0.4),mat_index=WOOD); box(bm,(-1.4,1.6,0.38),(0.6,0.4,0.05),mat_index=MORTAR)
finish("SM_Wall_Straight_Build01",bm,K)
# ---------- Construction stage 2: half height with scaffolding, ladder, pulley
bm=bmesh.new()
wall_arm(bm,(-2,0),(2,0),(0,-1),seed=1,height=2.4,top=False)
scaffold(bm,1.05,3.0,[1.3,2.5]); scaffold(bm,-1.05,3.0,[2.5])
# ladder
for x in(-1.2,-0.75): 
    vs=box(bm,(x,2.2,1.4),(0.07,0.07,3.0),mat_index=WOOD)
    bmesh.ops.rotate(bm,verts=vs,cent=Vector((x,2.2,1.4)),matrix=Matrix.Rotation(0.2,3,"X"))
for k in range(8): box(bm,(-0.975,2.2-(0.35+k*0.35-1.4)*0.2,0.35+k*0.35),(0.5,0.05,0.05),mat_index=WOOD)
# pulley beam + bucket
box(bm,(1.8,1.05,3.4),(0.1,1.4,0.1),mat_index=WOODD)
box(bm,(1.8,1.7,2.2),(0.02,0.02,2.4),mat_index=WOOD)
cyl(bm,(1.8,1.7,0.95),0.18,0.22,0.3,segs=8,mat_index=WOOD)
# loose course being laid on top
rnd=random.Random(9)
for k in range(3):
    box(bm,(-1.6+k*0.75,rnd.choice((-0.55,0.55)),2.62),(0.65,0.14,0.38),mat_index=rnd.choice(STONE))
stone_pile(bm,0.6,-2.0,7,12)
finish("SM_Wall_Straight_Build02",bm,K)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0033] 2026-09-23 01:30:13  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
K=col("Kit_Pieces"); D=col("Kit_Display")
for o in list(D.objects): bpy.data.objects.remove(o)
rows=[["SM_Wall_Straight","SM_Wall_Corner","SM_Wall_T","SM_Wall_Cross","SM_Wall_End","SM_Wall_Stairs"],
      ["SM_Wall_Gatehouse","SM_Tower_Round","SM_Tower_Round_Roofed","SM_Wall_Ruined"],
      ["SM_Wall_Straight_Build01","SM_Wall_Straight_Build02"]]
labels={"SM_Wall_Straight_Build01":"Build stage 1","SM_Wall_Straight_Build02":"Build stage 2"}
S=7.5
tile_m=mat("WK_Tile",(0.24,0.36,0.14),0.95); edge_m=mat("WK_TileEdge",(0.55,0.50,0.42),0.9)
txt_m=mat("WK_Text",(0.08,0.07,0.06),0.6)
for r,row in enumerate(rows):
    for c,n in enumerate(row):
        x=c*S; y=-r*(S+1.5)
        bpy.data.objects[n].location=(x,y,0)
        bm=bmesh.new()
        box(bm,(0,0,-0.15),(4,4,0.3),mat_index=0)
        for sx in(-1,1):
            box(bm,(sx*2,0,-0.12),(0.06,4.06,0.3),mat_index=1); box(bm,(0,sx*2,-0.12),(4.06,0.06,0.3),mat_index=1)
        obj_from_bm("Tile_"+n,bm,[tile_m,edge_m],D,loc=(x,y,-0.35))
        cu=bpy.data.curves.new("Lbl_"+n,"FONT"); cu.body=labels.get(n,n.replace("SM_","").replace("_"," "))
        cu.size=0.55; cu.align_x="CENTER"; cu.extrude=0.02
        t=bpy.data.objects.new("Lbl_"+n,cu); D.objects.link(t); t.data.materials.append(txt_m)
        t.location=(x,y-2.9,-0.3); t.rotation_euler=(math.radians(0),0,0)
# complete stage beside build stages
src=bpy.data.objects["SM_Wall_Straight"]
st3=bpy.data.objects.new("Display_Build03",src.data); D.objects.link(st3); st3.location=(2*S,-2*(S+1.5),0)
bm=bmesh.new(); box(bm,(0,0,-0.15),(4,4,0.3),mat_index=0); obj_from_bm("Tile_B3",bm,[tile_m],D,loc=(2*S,-2*(S+1.5),-0.35))
cu=bpy.data.curves.new("Lbl_B3","FONT"); cu.body="Build stage 3 (done)"; cu.size=0.55; cu.align_x="CENTER"; cu.extrude=0.02
t=bpy.data.objects.new("Lbl_B3",cu); D.objects.link(t); t.data.materials.append(txt_m); t.location=(2*S,-2*(S+1.5)-2.9,-0.3)
# big ground
bm=bmesh.new(); box(bm,(0,0,0),(120,120,0.1)); g=obj_from_bm("Ground",bm,[mat("WK_Ground",(0.55,0.52,0.46),1.0)],D,loc=(18,-8,-0.55))
cam=bpy.data.objects["WK_Camera_Kit"]; cam.data.lens=32
cam.location=(18.75,-40,30)
cam.rotation_euler=(Vector((18.75,-8.5,0))-cam.location).to_track_quat("-Z","Y").to_euler()
SC.render.resolution_percentage=40
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"wallkit_sheet.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0034] 2026-09-23 01:30:34  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["wk_helpers"].as_string())
rows=[["SM_Wall_Straight","SM_Wall_Corner","SM_Wall_T","SM_Wall_Cross","SM_Wall_End"],
      ["SM_Wall_Stairs","SM_Wall_Gatehouse","SM_Tower_Round","SM_Tower_Round_Roofed","SM_Wall_Ruined"],
      ["SM_Wall_Straight_Build01","SM_Wall_Straight_Build02","Display_Build03"]]
SX,SY=7.0,9.5
for r,row in enumerate(rows):
    for c,n in enumerate(row):
        x=c*SX+(SX if r==2 else 0); y=-r*SY
        bpy.data.objects[n].location=(x,y,0)
        key=n if n!="Display_Build03" else "B3"
        bpy.data.objects["Tile_"+key].location=(x,y,-0.35)
        lb=bpy.data.objects["Lbl_"+key]; lb.location=(x,y-3.0,-0.3); lb.data.size=0.6
g=bpy.data.materials["MC_WK_Ground"]; next(n for n in g.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(0.20,0.19,0.17,1)
tm=bpy.data.materials["MC_WK_Text"]; next(n for n in tm.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(0.85,0.80,0.70,1)
bpy.data.objects["Ground"].location=(14,-9.5,-0.55)
cam=bpy.data.objects["WK_Camera_Kit"]; cam.data.lens=35
tgt=Vector((14,-10.5,0))
cam.location=tgt+Vector((0,-30,34))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"wallkit_sheet.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0035] 2026-09-23 01:30:52  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["wk_helpers"].as_string())
rows=[["SM_Wall_Stairs","SM_Wall_Gatehouse","SM_Tower_Round","SM_Tower_Round_Roofed","SM_Wall_Ruined"],
      ["SM_Wall_Straight","SM_Wall_Corner","SM_Wall_T","SM_Wall_Cross","SM_Wall_End"],
      ["SM_Wall_Straight_Build01","SM_Wall_Straight_Build02","Display_Build03"]]
SX,SY=7.0,9.5
for r,row in enumerate(rows):
    for c,n in enumerate(row):
        x=c*SX+(SX if r==2 else 0); y=-r*SY
        bpy.data.objects[n].location=(x,y,0)
        key=n if n!="Display_Build03" else "B3"
        bpy.data.objects["Tile_"+key].location=(x,y-0,-0.35)
        bpy.data.objects["Lbl_"+key].location=(x,y-3.0,-0.3)
bpy.data.objects["SM_Wall_Stairs"].rotation_euler.z=math.pi
bpy.data.objects["SM_Wall_Corner"].rotation_euler.z=-math.pi/2  # show the L opening toward camera
for lk in ["AgX - Medium High Contrast","AgX - High Contrast","AgX - Punchy"]:
    try: SC.view_settings.look=lk
    except: pass
    if SC.view_settings.look==lk and lk=="AgX - High Contrast": break
print(SC.view_settings.look)
SC.view_settings.exposure=-0.15
cam=bpy.data.objects["WK_Camera_Kit"]
tgt=Vector((14,-10,0.5)); cam.location=tgt+Vector((0,-31,30))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"wallkit_sheet.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: AgX - High Contrast\n"}

# ==============================================================================================================
# [0036] 2026-09-23 01:31:19  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["wk_helpers"].as_string())
ends={"SM_Wall_Straight":[(1,0),(-1,0)],"SM_Wall_Corner":[(1,0),(0,1)],"SM_Wall_T":[(1,0),(-1,0),(0,1)],
      "SM_Wall_Cross":[(1,0),(-1,0),(0,1),(0,-1)],"SM_Wall_End":[(-1,0)],"SM_Wall_Stairs":[(1,0),(-1,0)],
      "SM_Wall_Straight_Build01":[(1,0),(-1,0)],"SM_Wall_Straight_Build02":[(1,0),(-1,0)]}
hts={"SM_Wall_Straight_Build01":0.95,"SM_Wall_Straight_Build02":2.4}
for n,dirs in ends.items():
    o=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(o.data)
    h=hts.get(n,H)
    for dx,dy in dirs:
        rnd=random.Random(hash(n)%1000+dx*3+dy)
        # coursed end cap: blocks in rows, flush with cell edge
        z=0.5
        while z<h-0.05:
            ch=min(0.42*rnd.uniform(0.85,1.15),h-z)
            if h-(z+ch)<0.15: ch=h-z
            split=rnd.uniform(-0.25,0.25)
            for a,b in ((-(T/2-0.12),split),(split,T/2-0.12)):
                c=(a+b)/2; w=b-a-0.04
                pos=(dx*(2-0.03),dy*(2-0.03),z+ch/2)
                if dx: box(bm,(pos[0],c,pos[2]),(0.05,w,ch-0.05),mat_index=rnd.choice(STONE))
                else:  box(bm,(c,pos[1],pos[2]),(w,0.05,ch-0.05),mat_index=rnd.choice(STONE))
            z+=ch
    bm.to_mesh(o.data); bm.free()
bpy.data.objects["SM_Wall_Corner"].rotation_euler.z=0
cam=bpy.data.objects["WK_Camera_Kit"]; cam.data.lens=33
tgt=Vector((14,-8.3,1.0)); cam.location=tgt+Vector((0,-31,27))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"wallkit_sheet.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0037] 2026-09-23 01:31:32  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
o=bpy.data.objects["SM_Wall_Cross"]
me=o.data
# find faces near y=-2 end
import collections
cnt=collections.Counter()
for p in me.polygons:
    c=p.center
    if c.y<-1.9 and abs(c.x)<0.8: cnt[(me.materials[p.material_index].name, round(p.normal.y,2))]+=1
print(cnt)
e=bpy.data.objects["SM_Wall_End"].data
cnt=collections.Counter()
for p in e.polygons:
    c=p.center
    if c.x<-1.9 and abs(c.y)<0.8: cnt[(e.materials[p.material_index].name, round(p.normal.x,2))]+=1
print(cnt)
# ---- result ----
# {"result":"Code executed successfully: Counter({('MC_WK_StoneB', 0.0): 41, ('MC_WK_StoneC', -0.0): 20, ('MC_WK_StoneB', -1.0): 18, ('MC_WK_StoneA', -0
# .0): 15, ('MC_WK_StoneA', -1.0): 11, ('MC_WK_StoneB', 1.0): 10, ('MC_WK_StoneC', -1.0): 8, ('MC_WK_StoneC', 1.0): 5, ('MC_WK_StoneA', 1.0): 3, ('MC_WK
# _Mortar', -1.0): 2, ('MC_WK_StoneA', -0.08): 1, ('MC_WK_StoneA', -0.04): 1, ('MC_WK_StoneA', 0.03): 1, ('MC_WK_StoneA', 0.02): 1, ('MC_WK_StoneA', -0.
# 01): 1, ('MC_WK_Moss', -1.0): 1, ('MC_WK_StoneB', 0.06): 1, ('MC_WK_StoneB', 0.04): 1, ('MC_WK_StoneB', -0.05): 1, ('MC_WK_Walkway', -1.0): 1})\nCount
# er({('MC_WK_StoneC', 0.0): 32, ('MC_WK_StoneB', 0.0): 28, ('MC_WK_StoneC', -1.0): 15, ('MC_WK_StoneB', -1.0): 11, ('MC_WK_StoneA', -1.0): 9, ('MC_WK_S
# toneC', 1.0): 8, ('MC_WK_StoneB', 1.0): 7, ('MC_WK_StoneA', 0.0): 5, ('MC_WK_Mortar', -1.0): 2, ('MC_WK_StoneA', 0.11): 1, ('MC_WK_StoneA', 0.01): 1, 

# ==============================================================================================================
# [0038] 2026-09-23 01:31:57  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
cam=bpy.data.objects["WK_Camera_Kit"]; cam.data.lens=31
tgt=Vector((14,-9.6,0.8)); cam.location=tgt+Vector((0,-31,27))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
# ---------- Assembled fort demo, snapped to the 4 m grid, using linked instances of the kit
F=col("Demo_Fort")
for o in list(F.objects): bpy.data.objects.remove(o)
OX,OY=80,0   # fort origin, away from the kit sheet
def put(piece,gx,gy,rot=0,name=None):
    src=bpy.data.objects[piece]
    o=bpy.data.objects.new(name or f"{piece}_{gx}_{gy}",src.data); F.objects.link(o)
    o.location=(OX+gx*CELL,OY+gy*CELL,0); o.rotation_euler=(0,0,math.radians(rot)); return o
# 7 x 5 cell courtyard: towers on corners, gatehouse south, stairs inside, one ruined + one under construction on the east wall
W,Hh=6,4
for gx,gy,r in ((0,0,0),(W,0,0),(0,Hh,0),(W,Hh,0)):
    put("SM_Tower_Round_Roofed" if (gx+gy)%2==0 else "SM_Tower_Round",gx,gy)
for gx in range(1,W):
    if gx==3: put("SM_Wall_Gatehouse",gx,0,0)
    elif gx==5: put("SM_Wall_Stairs",gx,0,0)
    else: put("SM_Wall_Straight",gx,0,0)
    put("SM_Wall_Straight" if gx!=2 else "SM_Wall_T",gx,Hh,180)
for gy in range(1,Hh):
    put("SM_Wall_Straight",0,gy,-90)          # west wall, outer side faces -X
    piece={1:"SM_Wall_Straight_Build02",2:"SM_Wall_Ruined",3:"SM_Wall_Straight_Build01"}[gy]
    put(piece,W,gy,90)                          # east wall, outer faces +X
# a T on the north wall with a spur going outward to an end cap
put("SM_Wall_Straight",2,Hh+1,90); put("SM_Wall_End",2,Hh+2,-90)
# ground + courtyard
bm=bmesh.new(); box(bm,(0,0,0),(W*CELL+30,Hh*CELL+34,0.6))
obj_from_bm("Fort_Ground",bm,[mat("WK_Grass",(0.22,0.36,0.11),0.95)],F,loc=(OX+W*CELL/2,OY+Hh*CELL/2+2,-0.35))
bm=bmesh.new(); box(bm,(0,0,0),((W-1)*CELL,(Hh-1)*CELL,0.1))
obj_from_bm("Fort_Courtyard",bm,[mat("WK_Dirt",(0.36,0.26,0.15),1.0)],F,loc=(OX+W*CELL/2,OY+Hh*CELL/2,0.0))
# road out of the gate
bm=bmesh.new(); box(bm,(0,0,0),(3.0,14,0.1))
obj_from_bm("Fort_Road",bm,[bpy.data.materials["MC_WK_Dirt"]],F,loc=(OX+3*CELL,OY-8.5,0.0))
cd=bpy.data.cameras.get("WK_CamFort") or bpy.data.cameras.new("WK_CamFort"); cd.lens=30
cf=bpy.data.objects.get("WK_Camera_Fort") or bpy.data.objects.new("WK_Camera_Fort",cd)
if cf.name not in col("WK_Lighting").objects: col("WK_Lighting").objects.link(cf)
tgt=Vector((OX+12,OY+8.5,1.5)); cf.location=tgt+Vector((22,-32,24))
cf.rotation_euler=(tgt-cf.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cf
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"wallkit_fort.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0039] 2026-09-23 01:32:19  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["wk_helpers"].as_string())
F=col("Demo_Fort")
OX,OY=80,0
def put(piece,gx,gy,rot=0,name=None):
    src=bpy.data.objects[piece]
    o=bpy.data.objects.new(name or f"{piece}_{gx}_{gy}",src.data); F.objects.link(o)
    o.location=(OX+gx*CELL,OY+gy*CELL,0); o.rotation_euler=(0,0,math.radians(rot)); return o
for o in list(F.objects):
    if o.name.startswith(("SM_Tower","SM_Wall_Straight_2_5","SM_Wall_End_2_6")): bpy.data.objects.remove(o)
for gx,gy,p in ((0,0,"SM_Tower_Round"),(6,0,"SM_Tower_Round"),(0,4,"SM_Tower_Round_Roofed"),(6,4,"SM_Tower_Round_Roofed")):
    put(p,gx,gy)
put("SM_Wall_Straight",2,3,90); put("SM_Wall_End",2,2,-90)
g=bpy.data.objects["Fort_Ground"]; g.scale=(4,4,1)
cf=bpy.data.objects["WK_Camera_Fort"]; cf.data.lens=30
tgt=Vector((OX+13,OY+8,1.0)); cf.location=tgt+Vector((33,-26,25))
cf.rotation_euler=(tgt-cf.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cf
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"wallkit_fort.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0040] 2026-09-23 01:32:35  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["wk_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=100
# fort shot: hide kit sheet
kit_objs=list(col("Kit_Pieces").objects)+list(col("Kit_Display").objects)
for o in kit_objs: o.hide_render=True
SC.camera=bpy.data.objects["WK_Camera_Fort"]; SC.render.filepath=os.path.join(out,"wallkit_fort.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
for o in kit_objs: o.hide_render=False
fort=list(col("Demo_Fort").objects)
for o in fort: o.hide_render=True
SC.camera=bpy.data.objects["WK_Camera_Kit"]; SC.render.filepath=os.path.join(out,"wallkit_sheet.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
for o in fort: o.hide_render=False
# ---- FBX export: one file per piece, pivot at cell centre / ground
fbx_dir=os.path.join(out,"StoneWallKit_FBX"); os.makedirs(fbx_dir,exist_ok=True)
vl=bpy.context.view_layer
stats={}
for o in col("Kit_Pieces").objects:
    loc,rot=o.location.copy(),o.rotation_euler.copy()
    o.location=(0,0,0); o.rotation_euler=(0,0,0)
    for x in SC.objects: x.select_set(False)
    o.select_set(True); vl.objects.active=o
    bpy.ops.export_scene.fbx(filepath=os.path.join(fbx_dir,o.name+".fbx"),use_selection=True,object_types={"MESH"},
        apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",axis_up="Y",bake_space_transform=True,
        mesh_smooth_type="FACE",use_mesh_modifiers=True,add_leaf_bones=False,path_mode="COPY")
    o.location,o.rotation_euler=loc,rot
    stats[o.name]=len(o.data.polygons)
print(stats)
# ---- result ----
# {"result":"Code executed successfully: \nFBX export starting... 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06
# b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\StoneWallKit_FBX\\\\SM_Wall_Straight.fbx'\nexpor
# t finished in 0.0963 sec.\n\nFBX export starting... 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-
# 94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\StoneWallKit_FBX\\\\SM_Wall_Corner.fbx'\nexport finished in 
# 0.0093 sec.\n\nFBX export starting... 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06b-60f5-4d5d-94a9-dff3a56c5
# f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\StoneWallKit_FBX\\\\SM_Wall_T.fbx'\nexport finished in 0.0116 sec.\n\nFBX 

# ==============================================================================================================
# [0041] 2026-09-23 01:33:20  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
SC=bpy.data.scenes["StoneWallKit"]
g=bpy.data.objects["SM_Wall_Gatehouse"]
cd=bpy.data.cameras.get("WK_CamInspect") or bpy.data.cameras.new("WK_CamInspect"); cd.lens=40
c=bpy.data.objects.get("WK_Camera_Inspect") or bpy.data.objects.new("WK_Camera_Inspect",cd)
if c.name not in SC.collection.objects: SC.collection.objects.link(c)
tgt=g.location+Vector((0,0,3.2))
c.location=tgt+Vector((11,-6,3.5))
c.rotation_euler=(tgt-c.location).to_track_quat("-Z","Y").to_euler()
SC.camera=c
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=40
SC.render.filepath=os.path.join(out,"_inspect.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0042] 2026-09-23 01:34:13  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["wk_helpers"].as_string())
def gatehouse(bm):
    GH=6.6; D=3.2; ow=1.15; spring=2.3; SI=1.86   # SI = side core plane, facing blocks bring it to the 2.0 cell edge
    WZ=H+0.1; DW=0.55; DT=WZ+1.95                  # side walkway doorway: z WZ..DT, |y|<DW
    for sx in(-1,1): box(bm,(sx*(ow+(SI-ow)/2),0,GH/2),(SI-ow,D-0.2,GH),mat_index=MORTAR)
    box(bm,(0,0,(spring+ow+GH)/2),(2*ow,D-0.2,GH-(spring+ow)),mat_index=MORTAR)
    z=spring
    while z<spring+ow:
        hw=math.sqrt(max(0,ow**2-(z+0.1-spring)**2))
        for sx in(-1,1): box(bm,(sx*(hw+(ow-hw)/2),0,z+0.1),(ow-hw+0.01,D-0.2,0.2),mat_index=MORTAR)
        z+=0.2
    box(bm,(0,0,0.2),(4.35,D+0.35,0.6),mat_index=1); box(bm,(0,0,-0.4),(4.35,D+0.35,0.6),mat_index=MORTAR)
    # ---- front / back faces
    for sy in(-1,1):
        n=Vector((0,sy,0)); d=Vector((1,0,0))
        for x0,x1 in((-2,-ow),(ow,2)):
            block_face(bm,frame((x0,sy*(D/2-0.1),0),d,n),x1-x0,0.5,GH,seed=int(x0*10)+sy*5,u0=x0+2)
        block_face(bm,frame((-ow,sy*(D/2-0.1),0),d,n),2*ow,spring+ow+0.45,GH,seed=40+sy,u0=2-ow)
        nv=11
        for k in range(nv):
            a0=math.pi*k/nv; a1=math.pi*(k+1)/nv; r0,r1=ow,ow+0.45
            pts=[(math.cos(a)*r,math.sin(a)*r+spring) for (r,a) in((r0,a0+0.012),(r0,a1-0.012),(r1,a1-0.012),(r1,a0+0.012))]
            yf=sy*(D/2+0.04); yb=sy*(D/2-0.4)
            vf=[bm.verts.new((x,yf,z)) for x,z in pts]; vb=[bm.verts.new((x,yb,z)) for x,z in pts]
            fs=[bm.faces.new(vf),bm.faces.new(list(reversed(vb)))]
            for i in range(4): fs.append(bm.faces.new((vf[i],vb[i],vb[(i+1)%4],vf[(i+1)%4])))
            for f in fs: f.material_index=2 if k%2 else 0
            if sy>0: bmesh.ops.reverse_faces(bm,faces=fs)
    # ---- side faces (new): blocks around the walkway doorway
    for sx in(-1,1):
        n=Vector((sx,0,0)); d=Vector((0,-sx,0))          # run along the face, u=0 at the front/back corner
        y0=sx*(D/2+0.04)                                  # start corner
        L=D+0.08
        def run(ua,ub,za,zb,seed):
            o=Vector((SI*sx,y0,0))+d*ua
            block_face(bm,frame((o.x,o.y,0),d,n),ub-ua,za,zb,seed=seed,u0=ua)
        a=L/2-DW-0.2; b=L/2+DW+0.2
        run(0,a,0.5,GH,60+sx); run(b,L,0.5,GH,62+sx)
        run(a,b,0.5,WZ-0.05,64+sx); run(a,b,DT+0.35,GH,66+sx)
        # doorway: dark recess, plank door, stone jambs + lintel
        X=sx*2.0
        box(bm,(sx*(SI+0.01),0,(WZ+DT)/2),(0.04,2*DW+0.3,DT-WZ),mat_index=MORTAR)
        for k in range(4):
            yy=-DW+0.14+k*(2*DW-0.28)/3
            box(bm,(sx*(SI+0.04),yy,(WZ+DT)/2-0.02),(0.05,(2*DW)/4-0.02,DT-WZ-0.08),mat_index=WOOD if k%2 else WOODD)
        for zz in(WZ+0.45,DT-0.45): box(bm,(sx*(SI+0.08),0,zz),(0.03,2*DW-0.1,0.08),mat_index=IRON)
        for s in(-1,1):
            zz=WZ
            while zz<DT-0.05:
                hgt=min(0.45,DT-zz)
                box(bm,(sx*(SI+0.05),s*(DW+0.14),zz+hgt/2),(0.3,0.3 if int(zz*10)%2 else 0.4,hgt-0.04),mat_index=2)
                zz+=hgt
        box(bm,(sx*(SI+0.07),0,DT+0.17),(0.34,2*DW+0.75,0.34),mat_index=2)
        # arrow slits flanking the doorway, below the wall-walk only on the outer half (above neighbouring walls' parapet)
        box(bm,(sx*(SI+0.02),-sx*0+1.15,5.9),(0.1,0.12,0.8),mat_index=MORTAR)
        box(bm,(sx*(SI+0.02),-1.15,5.9),(0.1,0.12,0.8),mat_index=MORTAR)
        # corbels
        for c in(-1.25,-0.75,0.75,1.25): box(bm,(sx*2.1,c,GH-0.25),(0.3,0.22,0.4),mat_index=1)
    # ---- quoins on the 4 vertical corners
    rnd=random.Random(3)
    for sx in(-1,1):
        for sy in(-1,1):
            z=0.5; k=0
            while z<GH-0.1:
                ch=min(0.45,GH-z); long_x=(k%2==0)
                lx,ly=(0.75,0.36) if long_x else (0.36,0.75)
                box(bm,(sx*(2.0+0.03-lx/2),sy*(D/2+0.07-ly/2),z+ch/2),(lx,ly,ch-0.04),mat_index=2 if k%3 else 0)
                z+=ch; k+=1
    # arrow slits front
    for sx in(-1,1): box(bm,(sx*1.5,-D/2-0.07,4.6),(0.12,0.1,0.9),mat_index=MORTAR)
    # top
    box(bm,(0,0,GH+0.06),(4.0,D,0.12),mat_index=WALK)
    for (cx,cy,lx,ly) in((0,-D/2+PAR/2,4.0,PAR),(0,D/2-PAR/2,4.0,PAR),(-2+PAR/2,0,PAR,D),(2-PAR/2,0,PAR,D)):
        box(bm,(cx,cy,GH+PAR_H/2+0.06),(lx,ly,PAR_H),mat_index=0)
    for c in(-1.5,-0.5,0.5,1.5):
        for sy in(-1,1): box(bm,(c,sy*(D/2-PAR/2),GH+0.06+PAR_H+MERL_H/2),(0.62,PAR,MERL_H),mat_index=STONE[int(c*2)%3])
    for c in(-0.9,0.9):
        for sx in(-1,1): box(bm,(sx*(2-PAR/2),c,GH+0.06+PAR_H+MERL_H/2),(PAR,0.62,MERL_H),mat_index=1)
    box(bm,(0,0,GH+0.1),(4.3,D+0.3,0.14),mat_index=1)   # string course under parapet, all sides
    for c in [-1.75+i*0.5 for i in range(8)]:
        for sy in(-1,1): box(bm,(c,sy*(D/2+0.12),GH-0.25),(0.22,0.3,0.4),mat_index=1)
    # gate doors
    for sx in(-1,1):
        for k in range(5):
            x=sx*(0.11+k*0.21); top=spring+math.sqrt(max(0,ow**2-(abs(x)+0.1)**2))-0.05
            box(bm,(x,-0.3,top/2),(0.2,0.12,top),mat_index=WOOD if k%2 else WOODD)
        for zz in(0.6,1.8): box(bm,(sx*0.55,-0.38,zz),(1.0,0.05,0.12),mat_index=IRON)
        cyl(bm,(sx*0.18,-0.42,1.2),0.08,0.08,0.03,segs=8,rot=Matrix.Rotation(math.pi/2,4,"X"),mat_index=IRON)
    for k in range(12):
        a0=math.pi*k/12; a1=math.pi*(k+1)/12
        v=[bm.verts.new((math.cos(a)*ow,y,math.sin(a)*ow+spring)) for a,y in((a0,-D/2),(a1,-D/2),(a1,D/2),(a0,D/2))]
        bm.faces.new(v).material_index=MORTAR
    for sx in(-1,1):
        v=[bm.verts.new((sx*ow,y,z)) for y,z in((-D/2,0),(D/2,0),(D/2,spring),(-D/2,spring))]
        bm.faces.new(v if sx>0 else list(reversed(v))).material_index=MORTAR
    # banner
    box(bm,(0,-D/2-0.08,GH-1.2),(1.0,0.04,1.6),mat_index=BANNER)
    box(bm,(0,-D/2-0.1,GH-0.38),(1.2,0.08,0.08),mat_index=WOODD)
    vs=[bm.verts.new(p) for p in((-0.5,-D/2-0.1,GH-2.0),(0.5,-D/2-0.1,GH-2.0),(0,-D/2-0.1,GH-2.45))]
    bm.faces.new(vs).material_index=BANNER
bm=bmesh.new(); gatehouse(bm)
o=bpy.data.objects["SM_Wall_Gatehouse"]
bm.to_mesh(o.data); bm.free()
o.data.update()
print(len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: 3197\n"}

# ==============================================================================================================
# [0043] 2026-09-23 01:34:26  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["StoneWallKit"]
g=bpy.data.objects["SM_Wall_Gatehouse"]
hidden=[o for o in SC.objects if o.type in("MESH","FONT") and o.name not in("SM_Wall_Gatehouse","Ground") and not o.hide_render]
for o in hidden: o.hide_render=True
c=bpy.data.objects["WK_Camera_Inspect"]; c.data.lens=35
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
for i,off in enumerate([Vector((10,-7,4)),Vector((-9,5,5))]):
    tgt=g.location+Vector((0,0,3.3)); c.location=tgt+off
    c.rotation_euler=(tgt-c.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=c; SC.render.filepath=os.path.join(out,f"_inspect{i}.png")
    bpy.ops.render.render(write_still=True,scene=SC.name)
for o in hidden: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0044] 2026-09-23 01:34:43  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["StoneWallKit"]
g=bpy.data.objects["SM_Wall_Gatehouse_3_0"]
c=bpy.data.objects["WK_Camera_Inspect"]; c.data.lens=30
tgt=g.location+Vector((0,0.8,4.0)); c.location=tgt+Vector((7,7,5.5))
c.rotation_euler=(tgt-c.location).to_track_quat("-Z","Y").to_euler()
SC.camera=c
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_inspect2.png")
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0045] 2026-09-23 01:34:59  blender  ok
# ==============================================================================================================
import bpy, os
SC=bpy.data.scenes["StoneWallKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
o=bpy.data.objects["SM_Wall_Gatehouse"]
loc,rot=o.location.copy(),o.rotation_euler.copy()
o.location=(0,0,0); o.rotation_euler=(0,0,0)
for x in SC.objects: x.select_set(False)
o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=os.path.join(out,"StoneWallKit_FBX","SM_Wall_Gatehouse.fbx"),use_selection=True,object_types={"MESH"},
    apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",axis_up="Y",bake_space_transform=True,mesh_smooth_type="FACE",add_leaf_bones=False)
o.location,o.rotation_euler=loc,rot
SC.render.resolution_percentage=100
kit=[x for c in ("Kit_Pieces","Kit_Display") for x in bpy.data.collections[c].objects]; fort=list(bpy.data.collections["Demo_Fort"].objects)
for x in kit: x.hide_render=True
SC.camera=bpy.data.objects["WK_Camera_Fort"]; SC.render.filepath=os.path.join(out,"wallkit_fort.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for x in kit: x.hide_render=False
for x in fort: x.hide_render=True
SC.camera=bpy.data.objects["WK_Camera_Kit"]; SC.render.filepath=os.path.join(out,"wallkit_sheet.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for x in fort: x.hide_render=False
# full-res gatehouse detail shot
SC.camera=bpy.data.objects["WK_Camera_Inspect"]; SC.render.filepath=os.path.join(out,"wallkit_gatehouse_side.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
SC.camera=bpy.data.objects["WK_Camera_Kit"]
for f in ("_inspect.png","_inspect0.png","_inspect1.png","_inspect2.png"):
    p=os.path.join(out,f)
    if os.path.exists(p): os.remove(p)
print(len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: \nFBX export starting... 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06
# b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\StoneWallKit_FBX\\\\SM_Wall_Gatehouse.fbx'\nexpo
# rt finished in 0.0163 sec.\n3197\n"}

# ==============================================================================================================
# [0046] 2026-09-23 01:36:09  blender  ok
# ==============================================================================================================
import bpy, numpy
sc = bpy.data.scenes.get("TreeAsset") or bpy.data.scenes.new("TreeAsset")
bpy.context.window.scene = sc
print(numpy.__version__)
# ---- result ----
# {"result":"Code executed successfully: 1.26.4\n"}

# ==============================================================================================================
# [0047] 2026-09-23 01:36:53  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os, math
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tdir=os.path.join(out,"TreeAsset","Textures"); os.makedirs(tdir,exist_ok=True)
rng=np.random.default_rng(7)
def save_img(name,arr,noncolor=False):
    h,w,_=arr.shape
    img=bpy.data.images.get(name)
    if img and (img.size[0]!=w or img.size[1]!=h): bpy.data.images.remove(img); img=None
    if not img: img=bpy.data.images.new(name,w,h,alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).astype(np.float32).ravel())  # blender rows bottom-up
    if noncolor: img.colorspace_settings.name="Non-Color"
    img.filepath_raw=os.path.join(tdir,name+".png"); img.file_format="PNG"; img.save()
    img.filepath=img.filepath_raw
    return img
# ---------------- BARK (tileable) 512 x 1024
W,H=512,1024
x=np.linspace(0,1,W,endpoint=False)[None,:]; y=np.linspace(0,1,H,endpoint=False)[:,None]
def pnoise(fx_max,fy_max,n,amp_decay=1.0,seed=0):
    r=np.random.default_rng(seed); acc=np.zeros((H,W))
    for _ in range(n):
        fx=r.integers(1,fx_max+1); fy=r.integers(0,fy_max+1)
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/(fx+fy)**amp_decay
    return acc/np.abs(acc).max()
warp=pnoise(3,6,30,0.8,1)*0.035
# vertical plates separated by fissures
plates=np.zeros((H,W))
for k,(f,a) in enumerate([(9,1.0),(17,0.45),(31,0.2)]):
    ph=np.random.default_rng(k).uniform(0,6.28)
    wob=pnoise(2,8,20,0.9,10+k)*0.05
    plates+=a*np.abs(np.sin(np.pi*(f*(x+warp+wob))+ph))
plates/=plates.max()
cross=0.5+0.5*pnoise(20,40,60,1.2,5)   # horizontal breaks in plates
fine=pnoise(64,64,120,0.6,6)
height=np.clip(plates**0.6*(0.75+0.25*cross)+0.08*fine,0,1)
dark=np.array([0.10,0.065,0.045]); mid=np.array([0.30,0.21,0.14]); light=np.array([0.46,0.37,0.28])
col=np.where(height[...,None]<0.5, dark+(mid-dark)*(height[...,None]/0.5), mid+(light-mid)*((height[...,None]-0.5)/0.5))
lichen=np.clip((pnoise(4,6,25,0.7,9)-0.35)*3,0,1)[...,None]*np.clip(height-0.55,0,1)[...,None]*1.6
col=col*(1-lichen*0.6)+np.array([0.42,0.46,0.30])*lichen*0.6
bark=np.dstack([col,np.ones((H,W))])
save_img("T_Bark_BaseColor",bark)
# normal map from height (tileable gradient via roll)
s=4.0
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*s; dy=(np.roll(height,-1,0)-np.roll(height,1,0))*s
n=np.dstack([-dx,dy,np.ones_like(dx)]); n/=np.linalg.norm(n,axis=2,keepdims=True)
save_img("T_Bark_Normal",np.dstack([n*0.5+0.5,np.ones((H,W))]),noncolor=True)
# ---------------- LEAF ATLAS 1024 x 1024, 2x2 twig clusters
S=1024; img=np.zeros((S,S,4))
yy,xx=np.mgrid[0:S,0:S].astype(np.float64)
greens=[np.array(c) for c in [(0.20,0.40,0.09),(0.27,0.47,0.11),(0.34,0.53,0.14),(0.16,0.34,0.08),(0.40,0.56,0.16)]]
def draw_line(p0,p1,wd,c):
    p0=np.array(p0);p1=np.array(p1);d=p1-p0;L2=(d**2).sum()
    x0,x1=int(max(0,min(p0[0],p1[0])-wd-2)),int(min(S,max(p0[0],p1[0])+wd+2))
    y0,y1=int(max(0,min(p0[1],p1[1])-wd-2)),int(min(S,max(p0[1],p1[1])+wd+2))
    X=xx[y0:y1,x0:x1];Y=yy[y0:y1,x0:x1]
    t=np.clip(((X-p0[0])*d[0]+(Y-p0[1])*d[1])/L2,0,1)
    dist=np.hypot(X-(p0[0]+t*d[0]),Y-(p0[1]+t*d[1]))
    a=np.clip(wd-dist+0.5,0,1)[...,None]
    reg=img[y0:y1,x0:x1]
    reg[...,:3]=reg[...,:3]*(1-a)+np.array(c)*a; reg[...,3:]=np.maximum(reg[...,3:],a)
def draw_leaf(cx,cy,ang,L,Wd,base):
    ca,sa=math.cos(ang),math.sin(ang)
    r=int(L+4); x0,x1=int(max(0,cx-r)),int(min(S,cx+r)); y0,y1=int(max(0,cy-r)),int(min(S,cy+r))
    X=xx[y0:y1,x0:x1]-cx; Y=yy[y0:y1,x0:x1]-cy
    s=(X*ca+Y*sa)/L; t=(-X*sa+Y*ca)
    bend=0.08*L*np.sin(np.pi*np.clip(s,0,1))*rng.uniform(-1,1)
    t=t-bend
    wprof=Wd*np.power(np.clip(np.sin(np.pi*np.clip(s,0,1)),0,1),0.75)*(1-0.35*np.clip(s,0,1))
    inside=np.clip(wprof-np.abs(t)+0.7,0,1)*((s>0)&(s<1))
    # shading: lighter toward tip & one half, darker midrib & veins
    shade=0.85+0.25*s+0.10*np.sign(t)*rng.uniform(0.5,1)
    vein=1-0.25*np.clip(1.6-np.abs(t),0,1)
    side_vein=1-0.10*(np.abs(np.sin((s*9-np.abs(t)/Wd*1.5)*np.pi))<0.15)*(np.abs(t)<wprof*0.8)
    edge=1-0.18*np.clip(1-(wprof-np.abs(t))/2.5,0,1)
    c=base[None,None,:]*(shade*vein*side_vein*edge)[...,None]
    a=inside[...,None]
    reg=img[y0:y1,x0:x1]
    reg[...,:3]=reg[...,:3]*(1-a)+c*a; reg[...,3:]=np.maximum(reg[...,3:],a)
stem=(0.24,0.17,0.08)
for q in range(4):
    ox,oy=(q%2)*512,(q//2)*512
    r2=np.random.default_rng(q+20)
    # twig from bottom-centre curving upward, leaves alternate
    base=np.array([ox+256+r2.uniform(-30,30),oy+500.0]); ang=-math.pi/2+r2.uniform(-0.25,0.25)
    pts=[base.copy()]; p=base.copy()
    for k in range(10):
        ang+=r2.uniform(-0.12,0.12); p=p+np.array([math.cos(ang),math.sin(ang)])*40; pts.append(p.copy())
    leaves=[]
    for k in range(1,11):
        p=pts[k]; side=1 if k%2 else -1
        la=ang_k=math.atan2(pts[k][1]-pts[k-1][1],pts[k][0]-pts[k-1][0])+side*r2.uniform(0.5,1.0)
        L=r2.uniform(95,140)*(1.0 if k<9 else 0.8); Wd=L*r2.uniform(0.26,0.34)
        leaves.append((p,la,L,Wd,greens[r2.integers(0,5)]))
    # tip leaf
    leaves.append((pts[-1],ang,120,38,greens[2]))
    for i in range(len(pts)-1): draw_line(pts[i],pts[i+1],5.5-i*0.4,stem)
    for (p,la,L,Wd,g) in leaves:
        tip=p+np.array([math.cos(la),math.sin(la)])*12
        draw_line(p,tip,2.2,stem)
        draw_leaf(tip[0],tip[1],la,L,Wd,g*r2.uniform(0.9,1.1))
# dilate colour into transparent areas (avoids dark fringes with mipmaps)
rgb=img[...,:3].copy(); a=img[...,3]
for _ in range(8):
    m=a>0.5
    for sh in((1,0),(-1,0),(0,1),(0,-1)):
        rr=np.roll(rgb,sh,(0,1)); ma=np.roll(m,sh,(0,1))
        fill=(~m)&ma; rgb[fill]=rr[fill]
    a2=np.maximum(a,np.roll(a>0.5,1,0)*0.0)
    m2=m.copy()
    for sh in((1,0),(-1,0),(0,1),(0,-1)): m2|=np.roll(m,sh,(0,1))
    a=np.where(m2&~m,0.01,a)  # mark as filled
img[...,:3]=rgb
save_img("T_Leaves_Atlas",img)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0048] 2026-09-23 01:37:31  blender  ok
# ==============================================================================================================
import bpy, numpy as np, math
S=1024; img=np.zeros((S,S,4)); rng=np.random.default_rng(3)
yy,xx=np.mgrid[0:S,0:S].astype(np.float64)
greens=[np.array(c) for c in [(0.20,0.40,0.09),(0.27,0.47,0.11),(0.34,0.53,0.14),(0.16,0.34,0.08),(0.40,0.56,0.16)]]
def draw_line(p0,p1,wd,c):
    p0=np.array(p0);p1=np.array(p1);d=p1-p0;L2=max((d**2).sum(),1e-6)
    x0,x1=int(max(0,min(p0[0],p1[0])-wd-2)),int(min(S,max(p0[0],p1[0])+wd+2))
    y0,y1=int(max(0,min(p0[1],p1[1])-wd-2)),int(min(S,max(p0[1],p1[1])+wd+2))
    X=xx[y0:y1,x0:x1];Y=yy[y0:y1,x0:x1]
    t=np.clip(((X-p0[0])*d[0]+(Y-p0[1])*d[1])/L2,0,1)
    dist=np.hypot(X-(p0[0]+t*d[0]),Y-(p0[1]+t*d[1]))
    a=np.clip(wd-dist+0.5,0,1)[...,None]; reg=img[y0:y1,x0:x1]
    reg[...,:3]=reg[...,:3]*(1-a)+np.array(c)*a; reg[...,3:]=np.maximum(reg[...,3:],a)
def draw_leaf(cx,cy,ang,L,Wd,base):
    ca,sa=math.cos(ang),math.sin(ang); r=int(L+4)
    x0,x1=int(max(0,cx-r)),int(min(S,cx+r)); y0,y1=int(max(0,cy-r)),int(min(S,cy+r))
    X=xx[y0:y1,x0:x1]-cx; Y=yy[y0:y1,x0:x1]-cy
    s=(X*ca+Y*sa)/L; t=(-X*sa+Y*ca)
    t=t-0.08*L*np.sin(np.pi*np.clip(s,0,1))*rng.uniform(-1,1)
    wprof=Wd*np.power(np.clip(np.sin(np.pi*np.clip(s,0,1)),0,1),0.75)*(1-0.35*np.clip(s,0,1))
    inside=np.clip(wprof-np.abs(t)+0.7,0,1)*((s>0)&(s<1))
    shade=0.85+0.25*s+0.10*np.sign(t)*rng.uniform(0.5,1)
    vein=1-0.25*np.clip(1.6-np.abs(t),0,1)
    side_vein=1-0.10*(np.abs(np.sin((s*9-np.abs(t)/Wd*1.5)*np.pi))<0.15)*(np.abs(t)<wprof*0.8)
    edge=1-0.18*np.clip(1-(wprof-np.abs(t))/2.5,0,1)
    c=base[None,None,:]*(shade*vein*side_vein*edge)[...,None]; a=inside[...,None]; reg=img[y0:y1,x0:x1]
    reg[...,:3]=reg[...,:3]*(1-a)+c*a; reg[...,3:]=np.maximum(reg[...,3:],a)
stem=(0.24,0.17,0.08)
for q in range(4):
    ox,oy=(q%2)*512,(q//2)*512; r2=np.random.default_rng(q+20)
    p=np.array([ox+256+r2.uniform(-20,20),oy+498.0]); ang=-math.pi/2+r2.uniform(-0.15,0.15); pts=[p.copy()]
    for k in range(9):
        ang+=r2.uniform(-0.1,0.1); ang=min(max(ang,-math.pi/2-0.25),-math.pi/2+0.25)
        p=p+np.array([math.cos(ang),math.sin(ang)])*34; pts.append(p.copy())
    leaves=[]
    for k in range(1,10):
        side=1 if k%2 else -1
        la=math.atan2(pts[k][1]-pts[k-1][1],pts[k][0]-pts[k-1][0])+side*r2.uniform(0.55,1.0)
        L=r2.uniform(90,125)*(1.0 if k<8 else 0.8); leaves.append((pts[k],la,L,L*r2.uniform(0.27,0.34),greens[r2.integers(0,5)]))
    leaves.append((pts[-1],ang,105,34,greens[2]))
    for i in range(len(pts)-1): draw_line(pts[i],pts[i+1],5.5-i*0.4,stem)
    for (pp,la,L,Wd,g) in leaves:
        tip=pp+np.array([math.cos(la),math.sin(la)])*10; draw_line(pp,tip,2.2,stem)
        draw_leaf(tip[0],tip[1],la,L,Wd,g*r2.uniform(0.9,1.1))
    # hard-clip to own cell with 6px margin
    cell=img[oy:oy+512,ox:ox+512]
    cell[:6,:,3]=0; cell[-6:,:,3]=0; cell[:,:6,3]=0; cell[:,-6:,3]=0
# proper colour dilation (edge padding) for mip-mapping
rgb=img[...,:3].copy(); m=img[...,3]>0.3
for _ in range(16):
    grow=m.copy()
    for sh in((1,0),(-1,0),(0,1),(0,-1)):
        ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
        rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
    m=grow
img[...,:3]=rgb
bpy.data.images["T_Leaves_Atlas"].pixels.foreach_set(np.ascontiguousarray(img[::-1]).astype(np.float32).ravel())
bpy.data.images["T_Leaves_Atlas"].save()
ys=np.where(img[...,3]>0.1)[0]; print(ys.min(),ys.max())
for q in range(4):
    ox,oy=(q%2)*512,(q//2)*512
    sub=img[oy:oy+512,ox:ox+512,3]>0.1; r=np.where(sub.any(1))[0]; c=np.where(sub.any(0))[0]; print(q,r.min(),r.max(),c.min(),c.max())
# ---- result ----
# {"result":"Code executed successfully: 79 1015\n0 81 503 134 306\n1 79 503 187 380\n2 79 503 141 324\n3 79 503 139 343\n"}

# ==============================================================================================================
# [0049] 2026-09-23 01:38:10  blender  ok
# ==============================================================================================================
import bpy, bmesh, math, random, json
from mathutils import Vector, Matrix, noise, Quaternion
SC=bpy.data.scenes["TreeAsset"]
UP=Vector((0,0,1))
branches=[]   # dict: pts, radii, depth, phase
def grow(start,direction,length,r0,r1,depth,rnd,trop=0.12,wig=0.10,step=None):
    step=step or (0.3 if depth<2 else 0.22)
    n=max(3,int(length/step)); d=direction.normalized(); p=start.copy()
    pts=[p.copy()]; radii=[r0]
    for i in range(1,n+1):
        t=i/n
        w=Vector((noise.noise(p*0.8+Vector((depth*3.1,0,0))),noise.noise(p*0.8+Vector((0,7.7,depth))),noise.noise(p*0.8+Vector((2.2,0,5)))))
        d=(d+UP*trop*(1 if depth>0 else 0.3)+w*wig).normalized()
        if depth>=2: d=(d-UP*0.05*t).normalized()   # outer branches droop slightly
        p=p+d*(length/n); pts.append(p.copy())
        radii.append(r0+(r1-r0)*(t**0.8))
    b={"pts":pts,"radii":radii,"depth":depth,"phase":rnd.random()}
    branches.append(b); return b
def point_at(b,t):
    f=t*(len(b["pts"])-1); i=min(int(f),len(b["pts"])-2); a=f-i
    p=b["pts"][i].lerp(b["pts"][i+1],a); r=b["radii"][i]*(1-a)+b["radii"][i+1]*a
    tan=(b["pts"][i+1]-b["pts"][i]).normalized(); return p,r,tan
def child_dir(tan,angle,azim):
    # rotate tangent away by 'angle' around a perpendicular set by azimuth
    perp=tan.cross(Vector((0.3,0.2,1)) if abs(tan.z)<0.9 else Vector((1,0,0))).normalized()
    perp=Quaternion(tan,azim)@perp
    return (Quaternion(perp,angle)@tan).normalized()
rnd=random.Random(12)
GOLD=2.39996
trunk=grow(Vector((0,0,-0.45)),Vector((0.05,0.02,1)),3.9,0.40,0.26,0,rnd,wig=0.05,step=0.3)
tips=[]
# 3 main limbs from the trunk top + 2 lower limbs
tp,tr,tt=point_at(trunk,1.0)
limbs=[]
for k in range(3):
    az=k*2*math.pi/3+rnd.uniform(-0.3,0.3)
    d=child_dir(tt,math.radians(rnd.uniform(32,46)),az)
    limbs.append(grow(tp-tt*0.3,d,rnd.uniform(3.6,4.4),tr*0.78,0.06,1,rnd,trop=0.06,wig=0.12))
for k,(t,ang) in enumerate([(0.62,58),(0.8,52)]):
    p,r,tan=point_at(trunk,t)
    d=child_dir(tan,math.radians(ang),k*2.6+1.0)
    limbs.append(grow(p,d,rnd.uniform(2.6,3.2),r*0.55,0.05,1,rnd,trop=0.10,wig=0.12))
sub=[]
for li,L in enumerate(limbs):
    nkids=4 if li<3 else 3
    for k in range(nkids):
        t=0.35+0.6*(k+rnd.uniform(0,0.6))/nkids
        p,r,tan=point_at(L,min(t,0.95))
        d=child_dir(tan,math.radians(rnd.uniform(38,62)),li*1.7+k*GOLD)
        if d.z< -0.1: d.z=-0.1
        sub.append(grow(p,d,rnd.uniform(1.5,2.3),r*0.72,0.035,2,rnd,trop=0.09,wig=0.16))
twigs=[]
for S in sub+limbs:
    for k in range(3):
        t=0.45+0.5*k/2+rnd.uniform(-0.05,0.05)
        p,r,tan=point_at(S,min(t,0.97))
        d=child_dir(tan,math.radians(rnd.uniform(35,65)),k*GOLD+rnd.uniform(0,6))
        twigs.append(grow(p,d,rnd.uniform(0.6,1.0),max(r*0.7,0.02),0.012,3,rnd,trop=0.05,wig=0.2,step=0.25))
print(len(branches), "limbs",len(limbs),"sub",len(sub),"twigs",len(twigs))
# bounds
allp=[p for b in branches for p in b["pts"]]
print("height",max(p.z for p in allp),"width",max(p.x for p in allp)-min(p.x for p in allp),max(p.y for p in allp)-min(p.y for p in allp))
data=[{"pts":[tuple(p) for p in b["pts"]],"radii":b["radii"],"depth":b["depth"],"phase":b["phase"]} for b in branches]
t=bpy.data.texts.get("tree_skeleton") or bpy.data.texts.new("tree_skeleton"); t.clear(); t.write(json.dumps(data))
# ---- result ----
# {"result":"Code executed successfully: 93 limbs 5 sub 18 twigs 69\nheight 8.240191459655762 width 6.308237075805664 5.967570066452026\n"}

# ==============================================================================================================
# [0050] 2026-09-23 01:38:34  blender  ok
# ==============================================================================================================
import bpy, bmesh, math, random, json
from mathutils import Vector, Matrix, noise, Quaternion
SC=bpy.data.scenes["TreeAsset"]
data=json.loads(bpy.data.texts["tree_skeleton"].as_string())
def tcol(name):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); SC.collection.children.link(c)
    return c
C=tcol("Tree_LOD0")
for o in list(C.objects):
    if o.name.startswith("SM_Tree_Wood"): bpy.data.objects.remove(o)
SEGS={0:16,1:10,2:6,3:4}
TOP=8.3
bm=bmesh.new()
uv=bm.loops.layers.uv.new("UVMap"); uv2=bm.loops.layers.uv.new("Wind")
colL=bm.loops.layers.color.new("Col")
def frames(pts):
    tans=[]
    for i in range(len(pts)):
        a=pts[max(i-1,0)]; b=pts[min(i+1,len(pts)-1)]; tans.append((b-a).normalized())
    n=tans[0].cross(Vector((0,0,1)) if abs(tans[0].z)<0.95 else Vector((1,0,0))).normalized()
    out=[]
    for i,t in enumerate(tans):
        if i>0:
            q=tans[i-1].rotation_difference(t); n=(q@n).normalized()
        n=(n-t*n.dot(t)).normalized(); out.append((t,n,t.cross(n)))
    return out
tri_by_depth={}
for bi,b in enumerate(data):
    pts=[Vector(p) for p in b["pts"]]; radii=b["radii"]; depth=b["depth"]; segs=SEGS[depth]
    fr=frames(pts)
    avg_r=sum(radii)/len(radii)
    urep=max(1,round(2*math.pi*avg_r/0.9))
    tile_w=2*math.pi*avg_r/urep; tile_h=tile_w*2
    rings=[]; vcoord=0.0; vs_list=[]
    for i,(p,r) in enumerate(zip(pts,radii)):
        if i>0: vcoord+=(pts[i]-pts[i-1]).length/tile_h
        t,n,bn=fr[i]
        ring=[]
        for k in range(segs):
            th=2*math.pi*k/segs
            rr=r
            if depth==0:
                z=p.z
                fl=math.exp(-max(z,0)*2.6)
                lobe=max(0,math.cos(5*th+0.7))**3
                rr=r*(1+fl*(0.22+0.75*lobe))
                rr*=1+0.045*noise.noise(Vector((math.cos(th)*1.5,math.sin(th)*1.5,z*1.3)))
            elif depth==1:
                rr*=1+0.05*noise.noise(Vector((math.cos(th)*1.5,math.sin(th)*1.5,i*0.4+bi)))
            off=n*math.cos(th)+bn*math.sin(th)
            v=bm.verts.new(p+off*rr)
            ring.append(v)
        rings.append((ring,vcoord))
    # wind weight per vertex: height based + depth
    for i in range(len(rings)-1):
        ra,va=rings[i]; rb,vb=rings[i+1]
        for k in range(segs):
            k2=(k+1)%segs
            f=bm.faces.new((ra[k],ra[k2],rb[k2],rb[k]))
            us=[k/segs*urep,(k+1)/segs*urep,(k+1)/segs*urep,k/segs*urep]; vv=[va,va,vb,vb]
            for l,u_,v_ in zip(f.loops,us,vv):
                l[uv].uv=(u_,v_)
                h=max(0,l.vert.co.z)/TOP
                sway=min(1,h*h*0.8+0.15*depth)
                l[uv2].uv=(b["phase"],0.0)
                ao=1.0 if l.vert.co.z>0.6 else 0.55+0.45*max(0,l.vert.co.z)/0.6
                l[colL]=(ao,ao,ao,sway)
            tri_by_depth[depth]=tri_by_depth.get(depth,0)+2
    # tip cap
    ring,_=rings[-1]
    if depth>0:
        c=bm.verts.new(pts[-1]+fr[-1][0]*radii[-1]*0.8)
        for k in range(segs):
            f=bm.faces.new((ring[k],ring[(k+1)%segs],c))
            for l in f.loops:
                l[uv].uv=(0.5,rings[-1][1]); l[uv2].uv=(b["phase"],0); h=max(0,l.vert.co.z)/TOP; l[colL]=(1,1,1,min(1,h*h*0.8+0.15*depth))
bm.normal_update()
me=bpy.data.meshes.new("SM_Tree_Wood"); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
o=bpy.data.objects.new("SM_Tree_Wood",me); C.objects.link(o)
# bark material
m=bpy.data.materials.get("M_Tree_Bark") or bpy.data.materials.new("M_Tree_Bark"); m.use_nodes=True
nt=m.node_tree; nt.nodes.clear()
out=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images["T_Bark_BaseColor"]
tn=nt.nodes.new("ShaderNodeTexImage"); tn.image=bpy.data.images["T_Bark_Normal"]; tn.image.colorspace_settings.name="Non-Color"
nm=nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value=1.2
va=nt.nodes.new("ShaderNodeVertexColor"); va.layer_name="Col"
mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1.0
nt.links.new(tx.outputs[0],mix.inputs[6]); nt.links.new(va.outputs[0],mix.inputs[7])
nt.links.new(mix.outputs[2],b.inputs["Base Color"])
nt.links.new(tn.outputs[0],nm.inputs["Color"]); nt.links.new(nm.outputs[0],b.inputs["Normal"])
b.inputs["Roughness"].default_value=0.9
nt.links.new(b.outputs[0],out.inputs[0])
me.materials.append(m)
print(tri_by_depth, sum(tri_by_depth.values()), len(me.polygons))
# ---- result ----
# {"result":"Code executed successfully: {0: 416, 1: 1160, 2: 1752, 3: 1656} 4984 2926\n"}

# ==============================================================================================================
# [0051] 2026-09-23 01:38:47  blender  ok
# ==============================================================================================================
import bpy, math
from mathutils import Vector
SC=bpy.data.scenes["TreeAsset"]
SC.world=bpy.data.scenes["MedievalColony"].world
SC.view_settings.look="AgX - Medium High Contrast"; SC.view_settings.exposure=-0.2
for k,v in {"taa_render_samples":64,"use_raytracing":True,"use_gtao":True}.items():
    if hasattr(SC.eevee,k): setattr(SC.eevee,k,v)
SC.render.resolution_x=1920; SC.render.resolution_y=1080
def tcol(name):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); SC.collection.children.link(c)
    return c
L=tcol("Tree_Staging")
if "TA_Sun" not in bpy.data.objects:
    s=bpy.data.objects.new("TA_Sun",bpy.data.lights["MC_Sun"]); L.objects.link(s)
    s.rotation_euler=(math.radians(50),math.radians(8),math.radians(35))
cd=bpy.data.cameras.get("TA_Cam") or bpy.data.cameras.new("TA_Cam"); cd.lens=50
cam=bpy.data.objects.get("TA_Camera") or bpy.data.objects.new("TA_Camera",cd)
if cam.name not in L.objects: L.objects.link(cam)
tgt=Vector((0,0,4.2)); cam.location=tgt+Vector((9,-17,1.5))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam
if "TA_Ground" not in bpy.data.objects:
    bpy.ops.mesh.primitive_circle_add(vertices=48,radius=7,fill_type="NGON",location=(0,0,0))
    g=bpy.context.active_object; g.name="TA_Ground"
    for c in g.users_collection: c.objects.unlink(g)
    L.objects.link(g)
    gm=bpy.data.materials.get("MC_WK_Grass"); g.data.materials.append(gm)
for area in bpy.context.window.screen.areas:
    if area.type=="VIEW_3D":
        area.spaces.active.shading.type="RENDERED"; area.spaces.active.region_3d.view_perspective="CAMERA"
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0052] 2026-09-23 01:39:01  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["TreeAsset"]
cam=bpy.data.objects["TA_Camera"]; cam.data.lens=35
tgt=Vector((0,0,3.8)); cam.location=tgt+Vector((6,-11,1.0))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
sun=bpy.data.objects["TA_Sun"]; print(tuple(sun.matrix_world.to_3x3()@Vector((0,0,-1))))
SC.render.resolution_percentage=40
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_tree_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: (-0.512665331363678, 0.5761954188346863, -0.6365320682525635)\n"}

# ==============================================================================================================
# [0053] 2026-09-23 01:39:13  blender  ok
# ==============================================================================================================
import bpy
me=bpy.data.objects["SM_Tree_Wood"].data
print([ (a.name,a.domain,a.data_type) for a in me.attributes])
print(me.color_attributes.active_color_name, me.uv_layers.keys())
ca=me.color_attributes["Col"]; print([tuple(ca.data[i].color) for i in range(0,3000,700)])
m=bpy.data.materials["M_Tree_Bark"]
for n in m.node_tree.nodes: print(n.bl_idname, [ (i.name, i.is_linked) for i in n.inputs if i.is_linked])
img=bpy.data.images["T_Bark_BaseColor"]; print(img.size[:], img.has_data, img.pixels[0:4] if img.has_data else None)
# ---- result ----
# {"result":"Code executed successfully: [('position', 'POINT', 'FLOAT_VECTOR'), ('.edge_verts', 'EDGE', 'INT32_2D'), ('sharp_face', 'FACE', 'BOOLEAN'),
#  ('.corner_vert', 'CORNER', 'INT'), ('.corner_edge', 'CORNER', 'INT'), ('Col', 'CORNER', 'BYTE_COLOR'), ('UVMap', 'CORNER', 'FLOAT2'), ('Wind', 'CORNE
# R', 'FLOAT2')]\n ['UVMap', 'Wind']\n[(0.26225072145462036, 0.26225072145462036, 0.26225072145462036, 0.0), (1.0, 1.0, 1.0, 0.07450980693101883), (1.0,
#  1.0, 1.0, 0.30588236451148987), (1.0, 1.0, 1.0, 0.3450980484485626), (1.0, 1.0, 1.0, 0.3294117748737335)]\nShaderNodeOutputMaterial [('Surface', True
# )]\nShaderNodeBsdfPrincipled [('Base Color', True), ('Normal', True)]\nShaderNodeTexImage []\nShaderNodeTexImage []\nShaderNodeNormalMap [('Color', Tr
# ue)]\nShaderNodeVertexColor []\nShaderNodeMix [('A', True), ('B', True)]\n(512, 1024) True (0.3450980484485626, 0.2549019753932953, 0.1764705926179886

# ==============================================================================================================
# [0054] 2026-09-23 01:39:22  blender  ok
# ==============================================================================================================
import bpy, os
m=bpy.data.materials["M_Tree_Bark"]; nt=m.node_tree
b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")
for l in list(b.inputs["Normal"].links): nt.links.remove(l)
SC=bpy.data.scenes["TreeAsset"]
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0055] 2026-09-23 01:39:37  blender  ok
# ==============================================================================================================
import bpy, os
me=bpy.data.objects["SM_Tree_Wood"].data
uv=me.uv_layers["UVMap"].data
for p in me.polygons:
    if p.loop_total==3:
        v=uv[p.loop_start].uv[1]
        for j,(a,b) in enumerate(((0,v),(0.25,v),(0.125,v+0.08))): uv[p.loop_start+j].uv=(a,b)
m=bpy.data.materials["M_Tree_Bark"]; nt=m.node_tree
b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"); nm=next(n for n in nt.nodes if n.type=="NORMAL_MAP")
nm.uv_map="UVMap"; nm.inputs["Strength"].default_value=0.8
nt.links.new(nm.outputs[0],b.inputs["Normal"])
SC=bpy.data.scenes["TreeAsset"]
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0056] 2026-09-23 01:39:45  blender  ok
# ==============================================================================================================
import bpy, numpy as np
img=bpy.data.images["T_Bark_Normal"]
a=np.array(img.pixels[:]).reshape(-1,4)
print(img.colorspace_settings.name, img.source, img.filepath, a.min(0), a.max(0), a.mean(0))
# ---- result ----
# {"result":"Code executed successfully: Non-Color FILE C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c
# 5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817\\TreeAsset\\Textures\\T_Bark_Normal.png [0. 0. 0. 1.] [0. 0. 0. 1.] [0. 0. 0. 1.
# ]\n"}

# ==============================================================================================================
# [0057] 2026-09-23 01:39:58  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
W,H=512,1024
x=np.linspace(0,1,W,endpoint=False)[None,:]; y=np.linspace(0,1,H,endpoint=False)[:,None]
def pnoise(fx_max,fy_max,n,amp_decay=1.0,seed=0):
    r=np.random.default_rng(seed); acc=np.zeros((H,W))
    for _ in range(n):
        fx=r.integers(1,fx_max+1); fy=r.integers(0,fy_max+1)
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/(fx+fy)**amp_decay
    return acc/np.abs(acc).max()
warp=pnoise(3,6,30,0.8,1)*0.035
plates=np.zeros((H,W))
for k,(f,a) in enumerate([(9,1.0),(17,0.45),(31,0.2)]):
    ph=np.random.default_rng(k).uniform(0,6.28); wob=pnoise(2,8,20,0.9,10+k)*0.05
    plates+=a*np.abs(np.sin(np.pi*(f*(x+warp+wob))+ph))
plates/=plates.max()
cross=0.5+0.5*pnoise(20,40,60,1.2,5); fine=pnoise(64,64,120,0.6,6)
height=np.clip(plates**0.6*(0.75+0.25*cross)+0.08*fine,0,1)
s=5.0
dx=(np.roll(height,-1,1)-np.roll(height,1,1))*s; dy=(np.roll(height,-1,0)-np.roll(height,1,0))*s
n=np.dstack([-dx,dy,np.ones_like(dx)]); n/=np.linalg.norm(n,axis=2,keepdims=True)
arr=np.dstack([n*0.5+0.5,np.ones((H,W))])
img=bpy.data.images["T_Bark_Normal"]; path=img.filepath
bpy.data.images.remove(img)
img=bpy.data.images.new("T_Bark_Normal",W,H,alpha=False,is_data=True)
img.colorspace_settings.name="Non-Color"
img.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).astype(np.float32).ravel())
img.filepath_raw=path; img.file_format="PNG"; img.save()
a=np.array(img.pixels[:]).reshape(-1,4); print(a.mean(0))
m=bpy.data.materials["M_Tree_Bark"]
tn=[nd for nd in m.node_tree.nodes if nd.type=="TEX_IMAGE" and nd.image is None or (nd.type=="TEX_IMAGE" and nd.image.name.startswith("T_Bark_Normal"))]
for nd in tn: nd.image=img
bpy.ops.render.render(write_still=True,scene="TreeAsset")
# ---- result ----
# {"result":"Code executed successfully: [0.50011691 0.49999711 0.98662567 1. ]\n"}

# ==============================================================================================================
# [0058] 2026-09-23 01:40:44  blender  ok
# ==============================================================================================================
import bpy
code=r'''
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise, Quaternion
SC=bpy.data.scenes["TreeAsset"]
UP=Vector((0,0,1)); GOLD=2.39996
def tcol(name,parent=None):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); (parent or SC.collection).children.link(c)
    return c
# ---------------- skeleton
def build_skeleton(seed=12):
    rnd=random.Random(seed); branches=[]
    def grow(start,direction,length,r0,r1,depth,trop=0.12,wig=0.10,step=None):
        step=step or (0.3 if depth<2 else 0.25)
        n=max(3,int(length/step)); d=direction.normalized(); p=start.copy()
        pts=[p.copy()]; radii=[r0]
        for i in range(1,n+1):
            t=i/n
            w=Vector((noise.noise(p*0.8+Vector((depth*3.1,seed,0))),noise.noise(p*0.8+Vector((0,7.7,depth))),noise.noise(p*0.8+Vector((2.2,0,5+seed)))))
            d=(d+UP*trop*(1 if depth>0 else 0.3)+w*wig).normalized()
            if depth>=2: d=(d-UP*0.06*t).normalized()
            p=p+d*(length/n); pts.append(p.copy()); radii.append(r0+(r1-r0)*(t**0.75))
        b={"pts":pts,"radii":radii,"depth":depth,"phase":rnd.random(),"kids":[]}
        branches.append(b); return b
    def point_at(b,t):
        f=t*(len(b["pts"])-1); i=min(int(f),len(b["pts"])-2); a=f-i
        return b["pts"][i].lerp(b["pts"][i+1],a), b["radii"][i]*(1-a)+b["radii"][i+1]*a, (b["pts"][i+1]-b["pts"][i]).normalized()
    def child_dir(tan,angle,azim):
        perp=tan.cross(Vector((0.3,0.2,1)) if abs(tan.z)<0.9 else Vector((1,0,0))).normalized()
        perp=Quaternion(tan,azim)@perp
        return (Quaternion(perp,angle)@tan).normalized()
    trunk=grow(Vector((0,0,-0.45)),Vector((0.10,0.04,1)),3.5,0.52,0.33,0,wig=0.07,step=0.28)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    for k in range(3):
        az=k*2*math.pi/3+rnd.uniform(-0.3,0.3)
        d=child_dir(tt,math.radians(rnd.uniform(34,48)),az)
        limbs.append(grow(tp-tt*0.35,d,rnd.uniform(3.4,4.1),tr*0.74,0.07,1,trop=0.07,wig=0.12))
    for k,(t,ang) in enumerate([(0.62,60),(0.8,55)]):
        p,r,tan=point_at(trunk,t); d=child_dir(tan,math.radians(ang),k*2.6+1.0)
        limbs.append(grow(p,d,rnd.uniform(2.5,3.0),r*0.5,0.06,1,trop=0.11,wig=0.12))
    sub=[]
    for li,L in enumerate(limbs):
        nk=4 if li<3 else 3
        for k in range(nk):
            t=0.35+0.6*(k+rnd.uniform(0,0.6))/nk
            p,r,tan=point_at(L,min(t,0.95))
            d=child_dir(tan,math.radians(rnd.uniform(38,62)),li*1.7+k*GOLD)
            if d.z<-0.1: d.z=-0.1
            sub.append(grow(p,d,rnd.uniform(1.4,2.1),r*0.72,0.04,2,trop=0.09,wig=0.16))
    for S in sub+limbs:
        for k in range(3):
            t=0.45+0.25*k+rnd.uniform(-0.05,0.05)
            p,r,tan=point_at(S,min(t,0.97))
            d=child_dir(tan,math.radians(rnd.uniform(35,65)),k*GOLD+rnd.uniform(0,6))
            grow(p,d,rnd.uniform(0.6,0.9),max(r*0.7,0.02),0.012,3,trop=0.05,wig=0.2,step=0.4)
    return branches
# ---------------- wood mesh
def frames(pts):
    tans=[(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized() for i in range(len(pts))]
    n=tans[0].cross(Vector((0,0,1)) if abs(tans[0].z)<0.95 else Vector((1,0,0))).normalized(); out=[]
    for i,t in enumerate(tans):
        if i>0: n=(tans[i-1].rotation_difference(t)@n).normalized()
        n=(n-t*n.dot(t)).normalized(); out.append((t,n,t.cross(n)))
    return out
def build_wood(name,branches,segs_map,ring_skip=1,max_depth=3,top=8.5,coll=None):
    bm=bmesh.new(); uv=bm.loops.layers.uv.new("UVMap"); uv2=bm.loops.layers.uv.new("Wind"); cl=bm.loops.layers.color.new("Col")
    for bi,b in enumerate(branches):
        depth=b["depth"]
        if depth>max_depth: continue
        idx=list(range(0,len(b["pts"]),ring_skip))
        if idx[-1]!=len(b["pts"])-1: idx.append(len(b["pts"])-1)
        pts=[b["pts"][i] for i in idx]; radii=[b["radii"][i] for i in idx]; segs=segs_map[depth]
        fr=frames(pts); avg_r=sum(radii)/len(radii)
        urep=max(1,round(2*math.pi*avg_r/0.9)); tile_h=2*(2*math.pi*avg_r/urep)
        rings=[]; vco=0.0
        for i,(p,r) in enumerate(zip(pts,radii)):
            if i>0: vco+=(pts[i]-pts[i-1]).length/tile_h
            t,n,bn=fr[i]; ring=[]
            for k in range(segs):
                th=2*math.pi*k/segs; rr=r
                if depth==0:
                    fl=math.exp(-max(p.z,0)*2.4); lobe=max(0,math.cos(5*th+0.7))**3
                    rr=r*(1+fl*(0.25+0.9*lobe))*(1+0.05*noise.noise(Vector((math.cos(th)*1.5,math.sin(th)*1.5,p.z*1.3))))
                elif depth==1: rr*=1+0.05*noise.noise(Vector((math.cos(th)*1.5,math.sin(th)*1.5,i*0.4+bi)))
                ring.append(bm.verts.new(p+(n*math.cos(th)+bn*math.sin(th))*rr))
            rings.append((ring,vco))
        def paint(f,capped=False):
            for l in f.loops:
                h=max(0,l.vert.co.z)/top; sway=min(1,h*h*0.8+0.12*depth)
                ao=1.0 if l.vert.co.z>0.6 else 0.55+0.45*max(0,l.vert.co.z)/0.6
                l[cl]=(ao,ao,ao,sway); l[uv2].uv=(b["phase"],0.0)
        for i in range(len(rings)-1):
            ra,va=rings[i]; rb,vb=rings[i+1]
            for k in range(segs):
                k2=(k+1)%segs; f=bm.faces.new((ra[k],ra[k2],rb[k2],rb[k]))
                for l,u_,v_ in zip(f.loops,[k/segs*urep,(k+1)/segs*urep,(k+1)/segs*urep,k/segs*urep],[va,va,vb,vb]): l[uv].uv=(u_,v_)
                paint(f)
        if depth>0:
            ring,v=rings[-1]; c=bm.verts.new(pts[-1]+fr[-1][0]*radii[-1]*0.8)
            for k in range(segs):
                f=bm.faces.new((ring[k],ring[(k+1)%segs],c))
                for l,(a,bb) in zip(f.loops,((0,v),(0.25,v),(0.125,v+0.08))): l[uv].uv=(a,bb)
                paint(f)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old)
    o=bpy.data.objects.new(name,me); (coll or SC.collection).objects.link(o)
    me.materials.append(bpy.data.materials["M_Tree_Bark"])
    return o
'''
t=bpy.data.texts.get("tree_build") or bpy.data.texts.new("tree_build"); t.clear(); t.write(code)
exec(code)
B=build_skeleton(12)
C=tcol("Tree_LOD0")
o=build_wood("SM_Tree_Wood",B,{0:16,1:10,2:6,3:4},coll=C)
allp=[p for b in B for p in b["pts"]]
print(len(B),"tris",sum(len(p.vertices)-2 for p in o.data.polygons),"h",max(p.z for p in allp))
# ---- result ----
# {"result":"Code executed successfully: 93 tris 4958 h 7.456225395202637\n"}

# ==============================================================================================================
# [0059] 2026-09-23 01:41:35  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def clump_centers(branches,rnd):
    cs=[]
    for b in branches:
        if b["depth"]==2:
            n=len(b["pts"])
            cs.append((b["pts"][-1],rnd.uniform(1.05,1.3),b["phase"]))
            cs.append((b["pts"][int(n*0.5)]+Vector((0,0,0.25)),rnd.uniform(0.9,1.1),b["phase"]))
        elif b["depth"]==1:
            cs.append((b["pts"][-1]+Vector((0,0,0.2)),rnd.uniform(1.2,1.45),b["phase"]))
    # thin out clumps that nearly coincide
    out=[]
    for c in cs:
        if all((c[0]-o[0]).length>0.55*(c[1]+o[1])*0.6 for o in out): out.append(c)
    return out
ATLAS=[((q%2)*512,(q//2)*512) for q in range(4)]
def cell_uv(q):
    ox,oy=ATLAS[q]
    u0,u1=(ox+124)/1024,(ox+388)/1024
    v_top=1-(oy+74)/1024; v_bot=1-(oy+508)/1024
    return u0,u1,v_bot,v_top
def build_foliage(name,branches,blob_sub=1,cards_per=16,card_size=(0.95,1.35),seed=3,coll=None,blob=True,top=8.5):
    rnd=random.Random(seed)
    cs=clump_centers(branches,rnd)
    cen=sum((c[0] for c in cs),Vector())/len(cs)
    ext=Vector((max(abs(c[0].x-cen.x)+c[1] for c in cs),max(abs(c[0].y-cen.y)+c[1] for c in cs),max(abs(c[0].z-cen.z)+c[1] for c in cs)))
    def canopy_n(p):
        d=p-cen; return Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z)).normalized()
    def canopy_t(p):
        d=p-cen; return min(1.0,Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z)).length)
    bm=bmesh.new(); uv=bm.loops.layers.uv.new("UVMap"); uv2=bm.loops.layers.uv.new("Wind"); cl=bm.loops.layers.color.new("Col")
    vnorm={}; vinfo={}
    def shade(v,clump_c,phase,flutter):
        cn=canopy_n(v.co); ln=(v.co-clump_c).normalized()
        vnorm[v]=(cn*0.6+ln*0.4).normalized()
        up=0.5+0.5*cn.z; outer=canopy_t(v.co)
        g=0.42+0.58*min(1,0.55*up+0.45*outer**1.5)
        h=max(0,v.co.z)/top; sway=min(1,h*h*0.8+0.3)
        vinfo[v]=((min(1,g*1.02),g,g*0.86,sway),(phase,flutter))
    if blob:
        for (c,r,ph) in cs:
            res=bmesh.ops.create_icosphere(bm,subdivisions=blob_sub,radius=r*0.82)
            for v in res["verts"]:
                d=v.co.normalized()
                disp=1+0.22*noise.noise(Vector(c)+d*1.7)+0.08*noise.noise(Vector(c)*3+d*4)
                v.co=Vector(c)+Vector((d.x,d.y,d.z*(0.8 if d.z<0 else 0.95)))*r*0.82*disp
                shade(v,Vector(c),ph,0.3)
            for f in {f for v in res["verts"] for f in v.link_faces}: f.material_index=0
    ncards=0
    for (c,r,ph) in cs:
        k=cards_per
        for i in range(k):
            # fibonacci sphere, biased upward/outward
            zf=1-2*(i+0.5)/k; az=i*GOLD+rnd.uniform(-0.3,0.3)
            d=Vector((math.sqrt(max(0,1-zf*zf))*math.cos(az),math.sqrt(max(0,1-zf*zf))*math.sin(az),zf))
            d=(d+canopy_n(Vector(c)+d*r)*0.6).normalized()
            if d.z<-0.6 and rnd.random()<0.6: continue
            s=rnd.uniform(*card_size)
            base=Vector(c)+d*r*rnd.uniform(0.45,0.7)
            upv=(d+Vector((rnd.uniform(-.35,.35),rnd.uniform(-.35,.35),rnd.uniform(-0.1,0.35)))).normalized()
            side=upv.cross(Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1))).normalized()).normalized()
            w=s*0.62; L=s
            normal=side.cross(upv).normalized()
            bend=normal*(0.12*s)*(1 if normal.dot(d)>0 else -1)
            P=[base-side*w/2, base+side*w/2, base+upv*L*0.5-side*w/2+bend, base+upv*L*0.5+side*w/2+bend, base+upv*L-side*w/2-bend*0.3, base+upv*L+side*w/2-bend*0.3]
            vs=[bm.verts.new(p) for p in P]
            q=rnd.randrange(4); u0,u1,vb,vt=cell_uv(q)
            if rnd.random()<0.5: u0,u1=u1,u0   # mirror for variety
            UV=[(u0,vb),(u1,vb),(u0,(vb+vt)/2),(u1,(vb+vt)/2),(u0,vt),(u1,vt)]
            FL=[0.15,0.15,0.6,0.6,1.0,1.0]
            for v,f_ in zip(vs,FL): shade(v,Vector(c),ph,f_)
            for (a,b_,c_,d_) in ((0,1,3,2),(2,3,5,4)):
                f=bm.faces.new((vs[a],vs[b_],vs[c_],vs[d_])); f.material_index=1
                for l in f.loops:
                    j=vs.index(l.vert); l[uv].uv=UV[j]
            ncards+=1
    for f in bm.faces:
        for l in f.loops:
            col,w=vinfo[l.vert]; l[cl]=col
            if f.material_index==0: l[uv].uv=(0.5,0.5)
            l[uv2].uv=w
    bm.normal_update()
    verts=list(bm.verts)
    me=bpy.data.meshes.new(name); bm.to_mesh(me)
    nlist=[vnorm[v] for v in verts]
    bm.free()
    for p in me.polygons: p.use_smooth=True
    me.normals_split_custom_set_from_vertices([tuple(n) for n in nlist])
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old)
    o=bpy.data.objects.new(name,me); (coll or SC.collection).objects.link(o)
    me.materials.append(bpy.data.materials["M_Tree_Canopy"]); me.materials.append(bpy.data.materials["M_Tree_Leaves"])
    return o,len(cs),ncards
def make_foliage_materials():
    atlas=bpy.data.images["T_Leaves_Atlas"]
    # canopy volume
    m=bpy.data.materials.get("M_Tree_Canopy") or bpy.data.materials.new("M_Tree_Canopy"); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1
    mix.inputs[6].default_value=(0.20,0.38,0.08,1)
    nt.links.new(vc.outputs[0],mix.inputs[7]); nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.75
    b.inputs["Subsurface Weight"].default_value=0.0
    nt.links.new(b.outputs[0],o.inputs[0])
    # cards
    m=bpy.data.materials.get("M_Tree_Leaves") or bpy.data.materials.new("M_Tree_Leaves"); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=atlas
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1
    nt.links.new(tx.outputs["Color"],mix.inputs[6]); nt.links.new(vc.outputs[0],mix.inputs[7])
    gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5
    nt.links.new(tx.outputs["Alpha"],gt.inputs[0]); nt.links.new(gt.outputs[0],b.inputs["Alpha"])
    nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.6
    tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); nt.links.new(mix.outputs[2],tr.inputs["Color"])
    ms=nt.nodes.new("ShaderNodeMixShader"); ms.inputs[0].default_value=0.22
    nt.links.new(b.outputs[0],ms.inputs[1]); nt.links.new(tr.outputs[0],ms.inputs[2])
    # keep alpha cut on the mix: multiply via transparent shader
    tp=nt.nodes.new("ShaderNodeBsdfTransparent"); ms2=nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gt.outputs[0],ms2.inputs[0]); nt.links.new(tp.outputs[0],ms2.inputs[1]); nt.links.new(ms.outputs[0],ms2.inputs[2])
    nt.links.new(ms2.outputs[0],o.inputs[0])
    m.use_backface_culling=False
    try: m.surface_render_method="DITHERED"
    except: pass
'''
t=bpy.data.texts["tree_build"]
s=t.as_string()
if "def build_foliage" not in s: t.write(code)
exec(t.as_string())
make_foliage_materials()
B=build_skeleton(12)
o,nc,ncards=build_foliage("SM_Tree_Foliage",B,coll=tcol("Tree_LOD0"))
print(nc,ncards,sum(len(p.vertices)-2 for p in o.data.polygons))
bpy.ops.render.render(write_still=True,scene="TreeAsset")
# ---- result ----
# {"result":"Code executed successfully: 23 331 1784\n"}

# ==============================================================================================================
# [0060] 2026-09-23 01:42:05  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["tree_build"].as_string())
# --- leaves: two-sided with un-flipped custom normals
m=bpy.data.materials["M_Tree_Leaves"]; nt=m.node_tree
geo=nt.nodes.new("ShaderNodeNewGeometry")
mul=nt.nodes.new("ShaderNodeMath"); mul.operation="MULTIPLY_ADD"; mul.inputs[1].default_value=-2; mul.inputs[2].default_value=1
nt.links.new(geo.outputs["Backfacing"],mul.inputs[0])
sc=nt.nodes.new("ShaderNodeVectorMath"); sc.operation="SCALE"
nt.links.new(geo.outputs["Normal"],sc.inputs[0]); nt.links.new(mul.outputs[0],sc.inputs["Scale"])
b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"); tr=next(n for n in nt.nodes if n.type=="BSDF_TRANSLUCENT")
nt.links.new(sc.outputs[0],b.inputs["Normal"])
# translucent side uses the opposite normal so light passing through shows on the far side
neg=nt.nodes.new("ShaderNodeVectorMath"); neg.operation="SCALE"; neg.inputs["Scale"].default_value=-1
nt.links.new(sc.outputs[0],neg.inputs[0]); nt.links.new(neg.outputs[0],tr.inputs["Normal"])
# --- canopy: colour matched to the (linear) leaf texture average
m=bpy.data.materials["M_Tree_Canopy"]; mx=next(n for n in m.node_tree.nodes if n.type=="MIX")
mx.inputs[6].default_value=(0.045,0.13,0.018,1)
next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Roughness"].default_value=0.85
# rebuild foliage: smaller inner volume, more / larger cards
s=bpy.data.texts["tree_build"].as_string()
s=s.replace("radius=r*0.82","radius=r*0.62").replace("*r*0.82*disp","*r*0.62*disp")
bpy.data.texts["tree_build"].clear(); bpy.data.texts["tree_build"].write(s)
exec(s)
B=build_skeleton(12)
o,nc,ncards=build_foliage("SM_Tree_Foliage",B,cards_per=22,card_size=(1.1,1.55),coll=tcol("Tree_LOD0"))
print(nc,ncards,sum(len(p.vertices)-2 for p in o.data.polygons))
bpy.ops.render.render(write_still=True,scene="TreeAsset")
# ---- result ----
# {"result":"Code executed successfully: 23 432 2188\n"}

# ==============================================================================================================
# [0061] 2026-09-23 01:42:21  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
from mathutils import Vector
img=bpy.data.images["T_Leaves_Atlas"]
a=np.array(img.pixels[:],dtype=np.float32).reshape(img.size[1],img.size[0],4)
a[...,0]*=1.30; a[...,1]*=1.32; a[...,2]*=1.10
a[...,:3]=np.clip(a[...,:3],0,1)
img.pixels.foreach_set(a.ravel()); img.save()
m=bpy.data.materials["M_Tree_Canopy"]; mx=next(n for n in m.node_tree.nodes if n.type=="MIX")
mx.inputs[6].default_value=(0.07,0.20,0.025,1)
SC=bpy.data.scenes["TreeAsset"]
cam=bpy.data.objects["TA_Camera"]; cam.data.lens=35
tgt=Vector((0,0,4.0)); cam.location=tgt+Vector((8,-15.5,0.8))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.render.render(write_still=True,scene="TreeAsset")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0062] 2026-09-23 01:42:38  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["tree_build"].as_string())
m=bpy.data.materials["M_Tree_Canopy"]; mx=next(n for n in m.node_tree.nodes if n.type=="MIX")
mx.inputs[6].default_value=(0.035,0.10,0.014,1)
B=build_skeleton(12)
C=tcol("Tree_LOD0")
w=build_wood("SM_Tree_Wood",B,{0:14,1:9,2:5,3:3},coll=C)
f,nc,ncards=build_foliage("SM_Tree_Foliage",B,cards_per=26,card_size=(1.1,1.55),coll=C)
tw=sum(len(p.vertices)-2 for p in w.data.polygons); tf=sum(len(p.vertices)-2 for p in f.data.polygons)
print("wood",tw,"foliage",tf,"cards",ncards,"total",tw+tf)
bpy.ops.render.render(write_still=True,scene="TreeAsset")
# ---- result ----
# {"result":"Code executed successfully: wood 4062 foliage 2520 cards 515 total 6582\n"}

# ==============================================================================================================
# [0063] 2026-09-23 01:43:08  blender  ok
# ==============================================================================================================
import bpy, os, math
exec(bpy.data.texts["tree_build"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
B=build_skeleton(12)
C1=tcol("Tree_LOD1"); C2=tcol("Tree_LOD2"); C3=tcol("Tree_LOD3")
w1=build_wood("SM_Tree_Wood_LOD1",B,{0:10,1:6,2:4},ring_skip=2,max_depth=2,coll=C1)
f1,_,c1=build_foliage("SM_Tree_Foliage_LOD1",B,cards_per=13,card_size=(1.45,1.95),coll=C1)
w2=build_wood("SM_Tree_Wood_LOD2",B,{0:7,1:5},ring_skip=3,max_depth=1,coll=C2)
f2,_,c2=build_foliage("SM_Tree_Foliage_LOD2",B,cards_per=5,card_size=(2.1,2.7),coll=C2)
tri=lambda o: sum(len(p.vertices)-2 for p in o.data.polygons)
print("LOD1",tri(w1)+tri(f1),"LOD2",tri(w2)+tri(f2))
# ---------- impostor render (orthographic, transparent) from LOD0
SC.render.film_transparent=True
hide=[o for o in SC.objects if o.type=="MESH" and o.name not in("SM_Tree_Wood","SM_Tree_Foliage")]
for o in hide: o.hide_render=True
allp=[p for b in B for p in b["pts"]]
f0=bpy.data.objects["SM_Tree_Foliage"]; ws=[f0.matrix_world@v.co for v in f0.data.vertices]
xmin=min(min(v.x for v in ws),min(p.x for p in allp)); xmax=max(max(v.x for v in ws),max(p.x for p in allp))
ymin=min(v.y for v in ws); ymax=max(v.y for v in ws); zmax=max(v.z for v in ws)
half=max(xmax-xmin,ymax-ymin,zmax)/2*1.02
cx=(xmin+xmax)/2; cy=(ymin+ymax)/2
cdi=bpy.data.cameras.get("TA_ImpCam") or bpy.data.cameras.new("TA_ImpCam"); cdi.type="ORTHO"; cdi.ortho_scale=half*2
ci=bpy.data.objects.get("TA_ImpostorCam") or bpy.data.objects.new("TA_ImpostorCam",cdi)
if ci.name not in SC.collection.objects: SC.collection.objects.link(ci)
prev=SC.camera; rx,ry,pct=SC.render.resolution_x,SC.render.resolution_y,SC.render.resolution_percentage
SC.render.resolution_x=SC.render.resolution_y=1024; SC.render.resolution_percentage=100
tdir=os.path.join(out,"TreeAsset","Textures")
imgs=[]
for i,(ang) in enumerate((0,90)):
    a=math.radians(ang)
    ci.location=(cx+math.sin(a)*30, cy-math.cos(a)*30, half-0.02)
    ci.rotation_euler=(math.radians(90),0,a)
    SC.camera=ci; SC.render.filepath=os.path.join(tdir,f"T_Tree_Impostor_{i}.png")
    bpy.ops.render.render(write_still=True,scene=SC.name)
SC.camera=prev; SC.render.resolution_x,SC.render.resolution_y,SC.render.resolution_percentage=rx,ry,pct
SC.render.film_transparent=False
for o in hide: o.hide_render=False
# cross-billboard mesh (2 quads, each its own texture half via two materials)
bm=bmesh.new(); uvl=bm.loops.layers.uv.new("UVMap")
for i,ang in enumerate((0,90)):
    a=math.radians(ang); d=Vector((math.cos(a),math.sin(a),0))
    c0=Vector((cx,cy,0))
    P=[c0-d*half+Vector((0,0,-0.02)),c0+d*half+Vector((0,0,-0.02)),c0+d*half+Vector((0,0,2*half-0.02)),c0-d*half+Vector((0,0,2*half-0.02))]
    f=bm.faces.new([bm.verts.new(p) for p in P]); f.material_index=i
    for l,uvv in zip(f.loops,((0,0),(1,0),(1,1),(0,1))): l[uvl].uv=uvv
me=bpy.data.meshes.new("SM_Tree_LOD3_Impostor"); bm.to_mesh(me); bm.free()
old=bpy.data.objects.get("SM_Tree_LOD3_Impostor")
if old: bpy.data.objects.remove(old)
imp=bpy.data.objects.new("SM_Tree_LOD3_Impostor",me); C3.objects.link(imp)
for i in range(2):
    im=bpy.data.images.load(os.path.join(tdir,f"T_Tree_Impostor_{i}.png"),check_existing=True); im.reload()
    m=bpy.data.materials.get(f"M_Tree_Impostor_{i}") or bpy.data.materials.new(f"M_Tree_Impostor_{i}"); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear()
    o_=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled"); tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=im
    gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5
    nt.links.new(tx.outputs[0],b.inputs["Base Color"]); nt.links.new(tx.outputs["Alpha"],gt.inputs[0]); nt.links.new(gt.outputs[0],b.inputs["Alpha"])
    b.inputs["Roughness"].default_value=1.0; nt.links.new(b.outputs[0],o_.inputs[0])
    m.use_backface_culling=False
    try: m.surface_render_method="DITHERED"
    except: pass
    me.materials.append(m)
# ---------- collider: 8-sided trunk cylinder (convex)
bm=bmesh.new()
bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.62,radius2=0.42,depth=3.6,matrix=Matrix.Translation((0.08,0.03,1.8)))
me=bpy.data.meshes.new("SM_Tree_Collider"); bm.to_mesh(me); bm.free()
old=bpy.data.objects.get("SM_Tree_Collider")
if old: bpy.data.objects.remove(old)
col=bpy.data.objects.new("SM_Tree_Collider",me); tcol("Tree_Collision").objects.link(col); col.display_type="WIRE"; col.hide_render=True
print("impostor half",half,"done")
# ---- result ----
# {"result":"Code executed successfully: LOD1 2546 LOD2 1139\nimpostor half 4.801530089378357 done\n"}

# ==============================================================================================================
# [0064] 2026-09-23 01:43:35  blender  ok
# ==============================================================================================================
import bpy, os, math
exec(bpy.data.texts["tree_build"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tdir=os.path.join(out,"TreeAsset","Textures")
sun=bpy.data.objects["TA_Sun"]; e0=sun.data.energy
w=SC.world; bg=next(n for n in w.node_tree.nodes if n.type=="BACKGROUND"); b0=bg.inputs[1].default_value
# temporary even lighting: sun from above-front of each view, stronger sky
SC.render.film_transparent=True
hide=[o for o in SC.objects if o.type=="MESH" and o.name not in("SM_Tree_Wood","SM_Tree_Foliage")]
for o in hide: o.hide_render=True
ci=bpy.data.objects["TA_ImpostorCam"]; prev=SC.camera
rx,ry,pct=SC.render.resolution_x,SC.render.resolution_y,SC.render.resolution_percentage
SC.render.resolution_x=SC.render.resolution_y=1024; SC.render.resolution_percentage=100
srot=sun.rotation_euler.copy()
sun.data.energy=2.2; bg.inputs[1].default_value=0.9
cx=ci.location.x if False else None
half=ci.data.ortho_scale/2
locs=[]
for i,ang in enumerate((0,90)):
    a=math.radians(ang)
    ci.rotation_euler=(math.radians(90),0,a)
    # keep previous centre: recompute from object positions stored in mesh of impostor
    imp=bpy.data.objects["SM_Tree_LOD3_Impostor"].data
    c=sum((v.co for v in imp.vertices),Vector())/len(imp.vertices)
    ci.location=(c.x+math.sin(a)*30,c.y-math.cos(a)*30,half-0.02)
    sun.rotation_euler=(math.radians(35),0,a)   # light comes from the camera side, from above
    SC.camera=ci; SC.render.filepath=os.path.join(tdir,f"T_Tree_Impostor_{i}.png")
    bpy.ops.render.render(write_still=True,scene=SC.name)
    bpy.data.images[f"T_Tree_Impostor_{i}.png"].reload()
sun.rotation_euler=srot; sun.data.energy=e0; bg.inputs[1].default_value=b0
SC.camera=prev; SC.render.resolution_x,SC.render.resolution_y,SC.render.resolution_percentage=rx,ry,pct
SC.render.film_transparent=False
for o in hide: o.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0065] 2026-09-23 01:43:54  blender  ok
# ==============================================================================================================
import bpy, os, math
exec(bpy.data.texts["tree_build"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=100
g=bpy.data.objects["TA_Ground"]; g.scale=(6,6,1)
# hero
cam=bpy.data.objects["TA_Camera"]; cam.data.lens=40
tgt=Vector((0,0,4.1)); cam.location=tgt+Vector((10,-16,-1.2))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
lods=["Tree_LOD1","Tree_LOD2","Tree_LOD3"]
for c in lods:
    for o in bpy.data.collections[c].objects: o.hide_render=True
SC.camera=cam; SC.render.filepath=os.path.join(out,"tree_hero.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# lineup
for c in lods:
    for o in bpy.data.collections[c].objects: o.hide_render=False
for i,c in enumerate(["Tree_LOD0"]+lods):
    for o in bpy.data.collections[c].objects: o.location.x=i*11
txt_m=bpy.data.materials.get("MC_WK_Text")
tri=lambda o: sum(len(p.vertices)-2 for p in o.data.polygons)
labels=[]
for i,c in enumerate(["Tree_LOD0"]+lods):
    n=sum(tri(o) for o in bpy.data.collections[c].objects)
    cu=bpy.data.curves.new(f"TA_Lbl{i}","FONT"); cu.body=f"LOD{i}  {n:,} tris"; cu.size=0.75; cu.align_x="CENTER"
    t=bpy.data.objects.new(f"TA_Lbl{i}",cu); tcol("Tree_Staging").objects.link(t); t.data.materials.append(txt_m)
    t.location=(i*11,-5.5,0.05); labels.append(t)
    print(c,n)
cd=bpy.data.cameras.get("TA_CamLine") or bpy.data.cameras.new("TA_CamLine"); cd.lens=35
cl=bpy.data.objects.get("TA_CameraLineup") or bpy.data.objects.new("TA_CameraLineup",cd)
if cl.name not in tcol("Tree_Staging").objects: tcol("Tree_Staging").objects.link(cl)
tgt=Vector((16.5,0,3.2)); cl.location=tgt+Vector((0,-40,7))
cl.rotation_euler=(tgt-cl.location).to_track_quat("-Z","Y").to_euler()
g.location.x=16.5
SC.camera=cl; SC.render.filepath=os.path.join(out,"tree_lods.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
g.location.x=0
SC.camera=cam
# ---- result ----
# {"result":"Code executed successfully: Tree_LOD0 6582\nTree_LOD1 2546\nTree_LOD2 1139\nTree_LOD3 4\n"}

# ==============================================================================================================
# [0066] 2026-09-23 01:44:15  blender  ok
# ==============================================================================================================
import bpy, os, numpy as np
exec(bpy.data.texts["tree_build"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
bpy.data.objects["SM_Tree_Collider"].hide_render=True
for i in range(2):
    im=bpy.data.images[f"T_Tree_Impostor_{i}.png"]
    a=np.array(im.pixels[:],dtype=np.float32).reshape(-1,4); a[:,:3]*=0.70
    im.pixels.foreach_set(a.ravel()); im.save()
cl=bpy.data.objects["TA_CameraLineup"]; cl.data.lens=30
tgt=Vector((16.5,0,3.4)); cl.location=tgt+Vector((0,-44,6))
cl.rotation_euler=(tgt-cl.location).to_track_quat("-Z","Y").to_euler()
for i in range(4): bpy.data.objects[f"TA_Lbl{i}"].location.y=-6.5
g=bpy.data.objects["TA_Ground"]; g.location.x=16.5
SC.camera=cl; SC.render.filepath=os.path.join(out,"tree_lods.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
g.location.x=0
for c in ["Tree_LOD1","Tree_LOD2","Tree_LOD3"]:
    for o in bpy.data.collections[c].objects: o.hide_render=True
for t in [f"TA_Lbl{i}" for i in range(4)]: bpy.data.objects[t].hide_render=True
SC.camera=bpy.data.objects["TA_Camera"]; SC.render.filepath=os.path.join(out,"tree_hero.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for c in ["Tree_LOD1","Tree_LOD2","Tree_LOD3"]:
    for o in bpy.data.collections[c].objects: o.hide_render=False
for t in [f"TA_Lbl{i}" for i in range(4)]: bpy.data.objects[t].hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0067] 2026-09-23 01:44:45  blender  ok
# ==============================================================================================================
import bpy, os, shutil
t=bpy.data.texts["tree_build"]; s=t.as_string()
s=s.replace("        if depth>0:\n            ring,v=rings[-1]","        if True:\n            ring,v=rings[-1]")
t.clear(); t.write(s); exec(s)
B=build_skeleton(12)
build_wood("SM_Tree_Wood",B,{0:14,1:9,2:5,3:3},coll=tcol("Tree_LOD0"))
w1=build_wood("SM_Tree_Wood_LOD1",B,{0:10,1:6,2:4},ring_skip=2,max_depth=2,coll=tcol("Tree_LOD1"))
w2=build_wood("SM_Tree_Wood_LOD2",B,{0:7,1:5},ring_skip=3,max_depth=1,coll=tcol("Tree_LOD2"))
w1.location.x=11; w2.location.x=22
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
adir=os.path.join(out,"TreeAsset"); fbx=os.path.join(adir,"SM_Tree_Oak.fbx")
# build joined export copies at origin
vl=bpy.context.view_layer
tmp=bpy.data.collections.new("_export"); SC.collection.children.link(tmp)
groups={"SM_Tree_Oak_LOD0":["SM_Tree_Wood","SM_Tree_Foliage"],"SM_Tree_Oak_LOD1":["SM_Tree_Wood_LOD1","SM_Tree_Foliage_LOD1"],
        "SM_Tree_Oak_LOD2":["SM_Tree_Wood_LOD2","SM_Tree_Foliage_LOD2"],"SM_Tree_Oak_LOD3":["SM_Tree_LOD3_Impostor"],"SM_Tree_Oak_Collider":["SM_Tree_Collider"]}
made=[]
bpy.ops.object.select_all(action="DESELECT")
for gname,parts in groups.items():
    copies=[]
    for p in parts:
        src=bpy.data.objects[p]; c=src.copy(); c.data=src.data.copy(); c.location=(0,0,0); tmp.objects.link(c); copies.append(c)
    bpy.ops.object.select_all(action="DESELECT")
    for c in copies: c.select_set(True)
    vl.objects.active=copies[0]
    if len(copies)>1: bpy.ops.object.join()
    o=vl.objects.active; o.name=gname; o.data.name=gname; made.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in made: o.select_set(True)
bpy.ops.export_scene.fbx(filepath=fbx,use_selection=True,object_types={"MESH"},apply_scale_options="FBX_SCALE_UNITS",
    axis_forward="-Z",axis_up="Y",bake_space_transform=True,mesh_smooth_type="OFF",use_tspace=True,colors_type="SRGB",
    add_leaf_bones=False,path_mode="STRIP")
stats={o.name:sum(len(p.vertices)-2 for p in o.data.polygons) for o in made}
for o in made:
    me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
bpy.data.collections.remove(tmp)
print(stats, os.path.getsize(fbx))
# ---- result ----
# {"result":"Code executed successfully: \nFBX export starting... 'C:\\\\Users\\\\danie\\\\AppData\\\\Roaming\\\\Claude\\\\scratch-workspaces\\\\ec03f06
# b-60f5-4d5d-94a9-dff3a56c5f56\\\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\\\scratch-2026-09-23-d49817\\\\TreeAsset\\\\SM_Tree_Oak.fbx'\nexport finished i
# n 0.0504 sec.\n{'SM_Tree_Oak_LOD0': 6596, 'SM_Tree_Oak_LOD1': 2556, 'SM_Tree_Oak_LOD2': 1146, 'SM_Tree_Oak_LOD3': 4, 'SM_Tree_Oak_Collider': 28} 76582
# 0\n"}

# ==============================================================================================================
# [0068] 2026-09-23 01:44:58  blender  ok
# ==============================================================================================================
import bpy, os
SC=bpy.data.scenes["TreeAsset"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tri={"0":6596,"1":2556,"2":1146,"3":4}
for i in range(4): bpy.data.objects[f"TA_Lbl{i}"].data.body=f"LOD{i}  {tri[str(i)]:,} tris"
g=bpy.data.objects["TA_Ground"]; g.location.x=16.5
SC.camera=bpy.data.objects["TA_CameraLineup"]; SC.render.filepath=os.path.join(out,"tree_lods.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
g.location.x=0; SC.camera=bpy.data.objects["TA_Camera"]
p=os.path.join(out,"_tree_test.png")
if os.path.exists(p): os.remove(p)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0069] 2026-09-23 01:45:16  blender  ok
# ==============================================================================================================
import bpy, os
t=bpy.data.texts["tree_build"]; s=t.as_string()
anchor="        if True:\n            ring,v=rings[-1]"
cap_start='''        ring0,v0=rings[0]
        c0=bm.verts.new(pts[0]-fr[0][0]*radii[0]*0.3)
        for k in range(segs):
            f=bm.faces.new((ring0[(k+1)%segs],ring0[k],c0))
            for l,(a,bb) in zip(f.loops,((0,v0),(0.25,v0),(0.125,v0+0.08))): l[uv].uv=(a,bb)
            paint(f)
'''
if "c0=bm.verts.new" not in s: s=s.replace(anchor,cap_start+anchor)
t.clear(); t.write(s); exec(s)
B=build_skeleton(12)
build_wood("SM_Tree_Wood",B,{0:14,1:9,2:5,3:3},coll=tcol("Tree_LOD0"))
w1=build_wood("SM_Tree_Wood_LOD1",B,{0:10,1:6,2:4},ring_skip=2,max_depth=2,coll=tcol("Tree_LOD1")); w1.location.x=11
w2=build_wood("SM_Tree_Wood_LOD2",B,{0:7,1:5},ring_skip=3,max_depth=1,coll=tcol("Tree_LOD2")); w2.location.x=22
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
g=bpy.data.objects["TA_Ground"]; g.location.x=16.5
SC.camera=bpy.data.objects["TA_CameraLineup"]; SC.render.resolution_percentage=100
SC.render.filepath=os.path.join(out,"tree_lods.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
g.location.x=0; SC.camera=bpy.data.objects["TA_Camera"]
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0070] 2026-09-23 01:45:31  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["TreeAsset"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cd=bpy.data.cameras.new("tmpc"); cd.lens=50; c=bpy.data.objects.new("tmpc",cd); SC.collection.objects.link(c)
cl=bpy.data.objects["TA_CameraLineup"]
tgt=Vector((22.5,0,4.3)); c.location=tgt+(cl.location-Vector((16.5,0,3.4))).normalized()*14
c.rotation_euler=(tgt-c.location).to_track_quat("-Z","Y").to_euler()
SC.camera=c; SC.render.resolution_percentage=30
f2=bpy.data.objects["SM_Tree_Foliage_LOD2"]
for i,hide in enumerate((False,True)):
    f2.hide_render=hide
    SC.render.filepath=os.path.join(out,f"_dbg{i}.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
f2.hide_render=False
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0071] 2026-09-23 01:45:46  blender  ok
# ==============================================================================================================
import bpy, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC=bpy.data.scenes["TreeAsset"]
c=bpy.data.objects.get("tmpc")
if c: cd=c.data; bpy.data.objects.remove(c); bpy.data.cameras.remove(cd)
SC.camera=bpy.data.objects["TA_Camera"]; SC.render.resolution_percentage=100
for f in ("_dbg0.png","_dbg1.png","_tree_test.png"):
    p=os.path.join(out,f)
    if os.path.exists(p): os.remove(p)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0072] 2026-09-23 01:47:37  blender  ok
# ==============================================================================================================
import bpy, os
t=bpy.data.texts["tree_build"]; s=t.as_string()
if "CARD_R" not in s:
    s=s.replace("base=Vector(c)+d*r*rnd.uniform(0.45,0.7)","base=Vector(c)+d*r*rnd.uniform(*CARD_R)")
    s="CARD_R=(0.45,0.7)\n"+s
    t.clear(); t.write(s)
exec(s)
CARD_R=(0.15,0.85)
B=build_skeleton(12)
f,nc,ncards=build_foliage("SM_Tree_Foliage",B,blob=False,cards_per=48,card_size=(1.15,1.6),coll=tcol("Tree_LOD0"))
print(nc,ncards,sum(len(p.vertices)-2 for p in f.data.polygons))
for cname in ("Tree_LOD1","Tree_LOD2","Tree_LOD3"):
    for o in bpy.data.collections[cname].objects: o.hide_render=True; o.hide_viewport=True
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.camera=bpy.data.objects["TA_Camera"]; SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_tree_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 23 960 3840\n"}

# ==============================================================================================================
# [0073] 2026-09-23 01:47:53  blender  ok
# ==============================================================================================================
import bpy, os
t=bpy.data.texts["tree_build"]; s=t.as_string()
s=s.replace("g=0.42+0.58*min(1,0.55*up+0.45*outer**1.5)","g=0.52+0.48*min(1,0.6*up+0.4*outer**1.5)")
t.clear(); t.write(s); exec(s)
CARD_R=(0.15,0.85)
B=build_skeleton(12)
f,nc,ncards=build_foliage("SM_Tree_Foliage",B,blob=False,cards_per=48,card_size=(1.15,1.6),coll=tcol("Tree_LOD0"))
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=100
SC.render.filepath=os.path.join(out,"tree_hero.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
os.remove(os.path.join(out,"_tree_test.png"))
w=bpy.data.objects["SM_Tree_Wood"]
print(ncards, sum(len(p.vertices)-2 for p in f.data.polygons)+sum(len(p.vertices)-2 for p in w.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: 960 8272\n"}

# ==============================================================================================================
# [0074] 2026-09-23 01:51:53  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os, math
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tdir=os.path.join(out,"VillageKit","Textures"); os.makedirs(tdir,exist_ok=True)
def save(name,arr):
    h,w=arr.shape[:2]
    if arr.shape[2]==3: arr=np.dstack([arr,np.ones((h,w))])
    img=bpy.data.images.get(name)
    if img: bpy.data.images.remove(img)
    img=bpy.data.images.new(name,w,h,alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(np.clip(arr,0,1)[::-1]).astype(np.float32).ravel())
    img.filepath_raw=os.path.join(tdir,name+".png"); img.file_format="PNG"; img.save(); img.filepath=img.filepath_raw
    return img
def tnoise(S,fmax,n,decay,seed,aspect=1):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,fmax+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y*aspect)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
def smooth(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
# ---------------- STONE (hand-painted coursed rubble), 1024 = 1.5 m
S=1024; rng=np.random.default_rng(4)
rows=rng.uniform(0.15,0.24,7); rows/=rows.sum(); rcum=np.concatenate([[0],np.cumsum(rows)])
yy,xx=np.mgrid[0:S,0:S]/S
warp_x=tnoise(S,4,30,1.0,11)*0.012; warp_y=tnoise(S,4,30,1.0,12)*0.012
X=(xx+warp_x)%1; Y=(yy+warp_y)%1
ri=np.clip(np.searchsorted(rcum,Y,side="right")-1,0,len(rows)-1)
color=np.zeros((S,S,3)); height=np.zeros((S,S)); sid=np.zeros((S,S),int)
pal=np.array([(0.62,0.57,0.49),(0.55,0.51,0.45),(0.66,0.60,0.50),(0.50,0.47,0.43),(0.60,0.53,0.44),(0.57,0.55,0.50)])
gap=5.0; rad=22.0
for r in range(len(rows)):
    m=ri==r
    widths=rng.uniform(0.17,0.34,12); widths=widths[:max(3,int(1/widths.mean()))]; widths/=widths.sum()
    wc=np.concatenate([[0],np.cumsum(widths)]); off=rng.uniform(0,1)
    xs=(X[m]+off)%1; si=np.clip(np.searchsorted(wc,xs,side="right")-1,0,len(widths)-1)
    u=(xs-wc[si])/widths[si]; v=(Y[m]-rcum[r])/rows[r]
    wpx=widths[si]*S; hpx=rows[r]*S
    dx=np.minimum(u,1-u)*wpx; dy=np.minimum(v,1-v)*hpx
    qx=np.maximum(rad-dx,0); qy=np.maximum(rad-dy,0)
    d=np.minimum(dx,dy); corner=(qx>0)&(qy>0); d=np.where(corner,rad-np.hypot(qx,qy),d)
    height[m]=d; sid[m]=r*100+si
    stone_col=pal[(r*7+si*3)%len(pal)]*rng.uniform(0.92,1.08,(len(widths),1))[si]
    color[m]=stone_col
edge_n=tnoise(S,24,80,0.8,13)*4.0
d=height+edge_n
mask=smooth(gap,gap+2.5,d)
h=smooth(gap,gap+30,d)**0.7
# painted lighting from top-left
gy,gx=np.gradient(h)
nx,ny=-gx*40,gy*40
L=np.array([-0.45,0.75,0.5]); L/=np.linalg.norm(L)
nz=np.ones_like(nx); nl=np.sqrt(nx**2+ny**2+nz**2)
shade=(nx*L[0]+ny*L[1]+nz*L[2])/nl
mott=tnoise(S,20,80,0.7,14)*0.07+tnoise(S,60,120,0.5,15)*0.04
col=color*(0.78+0.42*shade[...,None]+mott[...,None])
# soft top-lit gradient per stone (value brighter near top)
col*= (0.92+0.12*np.clip(1-(h),0,1)[...,None]*0)  # keep
mortar=np.array([0.20,0.17,0.14])*(1+mott[...,None])
col=col*mask[...,None]+mortar*(1-mask[...,None])
# dark inner outline & crisp rim highlight
rim=smooth(gap+2,gap+7,d)-smooth(gap+7,gap+14,d)
col=col*(1-0.25*rim[...,None]*(shade[...,None]<0.6))+0.10*rim[...,None]*(shade[...,None]>0.8)
save("T_VK_Stone",col)
# ---------------- PLASTER, 1024 = 1.5 m
base=np.array([0.88,0.82,0.67])
b1=tnoise(S,5,40,1.0,21); b2=tnoise(S,24,120,0.6,22); b3=tnoise(S,90,160,0.3,23)
col=base*(1+0.06*b1[...,None]+0.035*b2[...,None]+0.02*b3[...,None])
col=col*(1-0.08*np.clip(b1-0.4,0,1)[...,None]*np.array([1,1.2,1.6]))
save("T_VK_Plaster",col)
# ---------------- WOOD (grain along U), 512 x 512 = 1 m
S2=512; y,x=np.mgrid[0:S2,0:S2]/S2
warp=tnoise(S2,3,30,1.0,31)*0.06
grain=np.sin(2*np.pi*(y*14+warp*6+tnoise(S2,2,10,1,32)*0.3))
fine=tnoise(S2,40,150,0.4,33)
streak=np.abs(np.sin(2*np.pi*(y*5+warp*2)))
wd=np.array([0.36,0.22,0.13]); wl=np.array([0.52,0.34,0.20])
t=np.clip(0.5+0.35*grain+0.15*fine,0,1)[...,None]
col=wd+(wl-wd)*t
col*=(0.92+0.12*streak[...,None])
# knots
for k in range(3):
    kx,ky=rng.uniform(0,1,2); dd=np.hypot(((x-kx+0.5)%1-0.5)*1.0,((y-ky+0.5)%1-0.5)*3)
    col*= (1-0.35*np.exp(-(dd/0.02)**2))[...,None]
save("T_VK_Wood",col)
# ---------------- ROOF TILES (rounded shingles), 1024 = 1.5 m (8 rows)
def roof(palette,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S
    nrow=8; ncol=6
    row=(y*nrow).astype(int); v=(y*nrow)%1
    xo=(x*ncol+0.5*(row%2))%ncol; c=xo.astype(int); u=xo%1
    # rounded bottom: visible shape ends at v < 1 - k*(1-sqrt(1-(2u-1)^2))
    bottom=1-0.28*(1-np.sqrt(np.clip(1-(2*u-1)**2,0,1)))
    inside=v<bottom
    # next row below overlaps: pixels beyond bottom belong to the row below (its top part), darker (shadow)
    tint=r.uniform(0.85,1.12,(nrow,ncol))
    pick=r.integers(0,len(palette),(nrow,ncol))
    colr=np.array(palette)[pick[row,c]]*tint[row,c][...,None]
    # below-row info
    row2=(row+1)%nrow; xo2=(x*ncol+0.5*(row2%2))%ncol; c2=xo2.astype(int)
    col2=np.array(palette)[pick[row2,c2]]*tint[row2,c2][...,None]
    # shading: light at bottom of the shingle's exposed face, shadow band at top under previous row
    lv=np.clip(v/bottom,0,1)
    sh=0.62+0.5*lv-0.25*np.clip((lv-0.85)/0.15,0,1)
    side=0.92+0.12*np.cos((u-0.35)*np.pi)
    edge=1-0.35*np.clip(1-(bottom-v)*40,0,1)
    colA=colr*(sh*side*edge)[...,None]
    shadow=0.45+0.25*np.clip((v-bottom)/(1-bottom+1e-4),0,1)
    colB=col2*shadow[...,None]*0.8
    col=np.where(inside[...,None],colA,colB)
    # vertical gap between shingles
    gapm=np.clip(np.minimum(u,1-u)*S/ncol/3.0,0,1)
    col*=(0.55+0.45*gapm)[...,None]
    col*=(1+0.05*tnoise(S,30,100,0.5,seed+1)[...,None])
    return col
save("T_VK_RoofRed",roof([(0.70,0.26,0.15),(0.62,0.22,0.12),(0.74,0.32,0.18),(0.58,0.25,0.15)],41))
save("T_VK_RoofBlue",roof([(0.22,0.33,0.55),(0.26,0.38,0.60),(0.19,0.29,0.48),(0.28,0.36,0.52)],42))
# ---------------- WINDOW leaded glass, 512
S3=512; y,x=np.mgrid[0:S3,0:S3]/S3
a=(x+y)*6; b=(x-y)*6
lead=np.minimum(np.abs(a-np.round(a)),np.abs(b-np.round(b)))
glass=np.array([0.20,0.40,0.48])+np.array([0.25,0.30,0.25])*np.clip(1-y,0,1)[...,None]*0.6
glint=np.exp(-((x-y*0.6-0.15)%1-0.1)**2/0.004)*0.35
pane_var=(np.sin(np.floor(a)*12.9+np.floor(b)*7.3)*0.5+0.5)*0.12
col=glass*(0.85+pane_var[...,None])+glint[...,None]
col=np.where((lead<0.045)[...,None],np.array([0.12,0.12,0.14]),col)
save("T_VK_Window",col)
print(sorted(os.listdir(tdir)))
# ---- result ----
# {"result":"Code executed successfully: ['T_VK_Plaster.png', 'T_VK_RoofBlue.png', 'T_VK_RoofRed.png', 'T_VK_Stone.png', 'T_VK_Window.png', 'T_VK_Wood.p
# ng']\n"}

# ==============================================================================================================
# [0075] 2026-09-23 01:52:41  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tdir=os.path.join(out,"VillageKit","Textures")
def tnoise(S,fmax,n,decay,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,fmax+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
def smooth(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
S=1024; rng=np.random.default_rng(9)
rows=rng.uniform(0.12,0.27,6); rows/=rows.sum(); rcum=np.concatenate([[0],np.cumsum(rows)])
yy,xx=np.mgrid[0:S,0:S]/S
X=(xx+tnoise(S,3,30,1.0,11)*0.02)%1; Y=(yy+tnoise(S,3,30,1.0,12)*0.015)%1
ri=np.clip(np.searchsorted(rcum,Y,side="right")-1,0,len(rows)-1)
dist=np.zeros((S,S)); color=np.zeros((S,S,3)); tilt=np.zeros((S,S))
pal=np.array([(0.66,0.60,0.50),(0.56,0.53,0.48),(0.70,0.62,0.50),(0.52,0.50,0.47),(0.63,0.55,0.45),(0.60,0.58,0.54),(0.58,0.52,0.44)])
rad=38.0
for r in range(len(rows)):
    m=ri==r
    widths=rng.uniform(0.16,0.42,10); k=1; 
    while widths[:k].sum()<1: k+=1
    widths=widths[:k]; widths/=widths.sum()
    wc=np.concatenate([[0],np.cumsum(widths)]); off=rng.uniform(0,1)
    xs=(X[m]+off)%1; si=np.clip(np.searchsorted(wc,xs,side="right")-1,0,len(widths)-1)
    u=(xs-wc[si])/widths[si]; v=(Y[m]-rcum[r])/rows[r]
    # some stones split horizontally into two smaller ones
    split=rng.random(len(widths))<0.35
    sp=split[si]
    v2=np.where(sp,np.where(v<0.5,v*2,(v-0.5)*2),v); hsc=np.where(sp,0.5,1.0)
    wpx=widths[si]*S; hpx=rows[r]*S*hsc
    dx=np.minimum(u,1-u)*wpx; dy=np.minimum(v2,1-v2)*hpx
    qx=np.maximum(rad-dx,0); qy=np.maximum(rad-dy,0)
    d=np.minimum(dx,dy); c=(qx>0)&(qy>0); d=np.where(c,rad-np.hypot(qx,qy),d)
    dist[m]=d
    sub=np.where(sp&(v>=0.5),1,0)
    idx=(r*13+si*5+sub*3)%len(pal)
    tint=rng.uniform(0.9,1.1,(len(widths),2))
    color[m]=pal[idx]*tint[si,sub][:,None]
    tilt[m]=rng.uniform(-1,1,(len(widths),2))[si,sub]
d=dist+tnoise(S,10,60,0.9,13)*9+tnoise(S,40,120,0.6,17)*3
gap=7.0
mask=smooth(gap,gap+3,d)
h=smooth(gap,gap+45,d)**0.6+0.08*tnoise(S,16,80,0.8,18)
gy,gx=np.gradient(h)
nx,ny=-gx*45,gy*45; nz=np.ones_like(nx)
L=np.array([-0.4,0.8,0.45]); L/=np.linalg.norm(L)
shade=(nx*L[0]+ny*L[1]+nz*L[2])/np.sqrt(nx**2+ny**2+1)
mott=tnoise(S,12,60,0.8,14)*0.08+tnoise(S,50,120,0.5,15)*0.05
col=color*(0.72+0.48*shade[...,None]+mott[...,None])
# painted strokes: faint darker cracks
crack=np.abs(tnoise(S,20,50,0.7,19))<0.012
col*=np.where(crack[...,None]&(mask[...,None]>0.5),0.8,1.0)
rim=smooth(gap+1,gap+5,d)-smooth(gap+5,gap+12,d)
col=col+0.12*rim[...,None]*np.clip(shade[...,None]-0.6,0,1)*3
mortar=np.array([0.24,0.20,0.16])*(1+mott[...,None])
col=col*mask[...,None]+mortar*(1-mask[...,None])*(0.7+0.3*smooth(0,gap,d))[...,None]
img=bpy.data.images["T_VK_Stone"]
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel()); img.save()
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0076] 2026-09-23 01:53:08  blender  ok
# ==============================================================================================================
import bpy, numpy as np
def tnoise(S,fmax,n,decay,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,fmax+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
def smooth(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
S=1024; rng=np.random.default_rng(9)
rows=rng.uniform(0.12,0.27,6); rows/=rows.sum(); rcum=np.concatenate([[0],np.cumsum(rows)])
yy,xx=np.mgrid[0:S,0:S]/S
X=(xx+tnoise(S,3,30,1.0,11)*0.02)%1; Y=(yy+tnoise(S,3,30,1.0,12)*0.015)%1
ri=np.clip(np.searchsorted(rcum,Y,side="right")-1,0,len(rows)-1)
dist=np.zeros((S,S)); color=np.zeros((S,S,3))
pal=np.array([(0.66,0.60,0.50),(0.56,0.53,0.48),(0.70,0.62,0.50),(0.52,0.50,0.47),(0.63,0.55,0.45),(0.60,0.58,0.54),(0.58,0.52,0.44)])
rad=38.0
for r in range(len(rows)):
    m=ri==r
    widths=rng.uniform(0.16,0.42,10); k=1
    while widths[:k].sum()<1: k+=1
    widths=widths[:k]; widths/=widths.sum()
    wc=np.concatenate([[0],np.cumsum(widths)]); off=rng.uniform(0,1)
    xs=(X[m]+off)%1; si=np.clip(np.searchsorted(wc,xs,side="right")-1,0,len(widths)-1)
    u=(xs-wc[si])/widths[si]; v=(Y[m]-rcum[r])/rows[r]
    split=rng.random(len(widths))<0.35; sp=split[si]
    v2=np.where(sp,np.where(v<0.5,v*2,(v-0.5)*2),v); hsc=np.where(sp,0.5,1.0)
    dx=np.minimum(u,1-u)*widths[si]*S; dy=np.minimum(v2,1-v2)*rows[r]*S*hsc
    qx=np.maximum(rad-dx,0); qy=np.maximum(rad-dy,0)
    d=np.minimum(dx,dy); c=(qx>0)&(qy>0); d=np.where(c,rad-np.hypot(qx,qy),d)
    dist[m]=d
    sub=np.where(sp&(v>=0.5),1,0); idx=(r*13+si*5+sub*3)%len(pal)
    tint=rng.uniform(0.9,1.1,(len(widths),2)); color[m]=pal[idx]*tint[si,sub][:,None]
    rng.uniform(-1,1,(len(widths),2))
d=dist+tnoise(S,10,60,0.9,13)*9+tnoise(S,40,120,0.6,17)*3
gap=7.0; mask=smooth(gap,gap+3,d)
h=smooth(gap,gap+45,d)**0.6+0.08*tnoise(S,16,80,0.8,18)
gy,gx=np.gradient(h); nx,ny=-gx*45,gy*45
L=np.array([-0.4,0.8,0.45]); L/=np.linalg.norm(L)
shade=(nx*L[0]+ny*L[1]+L[2])/np.sqrt(nx**2+ny**2+1)
mott=tnoise(S,12,60,0.8,14)*0.08+tnoise(S,50,120,0.5,15)*0.05
# soft painted speckle instead of line cracks
speck=np.clip(tnoise(S,80,200,0.3,19),0,1)**3*0.12
col=color*(0.72+0.48*shade[...,None]+mott[...,None]-speck[...,None])
rim=smooth(gap+1,gap+5,d)-smooth(gap+5,gap+12,d)
col=col+0.12*rim[...,None]*np.clip(shade[...,None]-0.6,0,1)*3
mortar=np.array([0.24,0.20,0.16])*(1+mott[...,None])
col=col*mask[...,None]+mortar*(1-mask[...,None])*(0.7+0.3*smooth(0,gap,d))[...,None]
img=bpy.data.images["T_VK_Stone"]
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel()); img.save()
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0077] 2026-09-23 01:54:31  blender  ok
# ==============================================================================================================
import bpy
code=r'''
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, noise
SC=bpy.data.scenes["VillageKit"]
CELL=3.0; H1=3.0; H2=2.8; DEPTH=6.0
TILE={0:1.5,1:1.5,2:1.0,3:1.5,4:1.0,5:1.0}
def vcol(name,parent=None):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); (parent or SC.collection).children.link(c)
    return c
def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type="RGBA"; mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=1
    if img:
        tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images[img]; nt.links.new(tx.outputs[0],mix.inputs[6])
    else: mix.inputs[6].default_value=(*flat,1)
    nt.links.new(vc.outputs[0],mix.inputs[7]); nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=rough
    if emit:
        b.inputs["Emission Color"].default_value=(*emit,1); b.inputs["Emission Strength"].default_value=4.0
    nt.links.new(b.outputs[0],o.inputs[0])
    return m
def kit_mats():
    return [tex_mat("M_VK_Stone","T_VK_Stone"), tex_mat("M_VK_Plaster","T_VK_Plaster",0.9), tex_mat("M_VK_Wood","T_VK_Wood",0.8),
            tex_mat("M_VK_RoofRed","T_VK_RoofRed",0.7), tex_mat("M_VK_Window","T_VK_Window",0.25), tex_mat("M_VK_Iron",None,0.5,flat=(0.08,0.08,0.09)),
            tex_mat("M_VK_FlowerPink",None,0.7,flat=(0.85,0.30,0.55)), tex_mat("M_VK_FlowerYellow",None,0.7,flat=(0.95,0.78,0.20)),
            tex_mat("M_VK_Leaf",None,0.8,flat=(0.18,0.42,0.10)), tex_mat("M_VK_Glow",None,0.5,flat=(1.0,0.75,0.35),emit=(1.0,0.62,0.25))]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW=range(10)
class Kit:
    def __init__(s): s.bm=bmesh.new(); s.uv=s.bm.loops.layers.uv.new("UVMap"); s.cl=s.bm.loops.layers.color.new("Col")
    def project(s,faces,mi,axes=None,sizes=None):
        t=TILE.get(mi,1.0)
        for f in faces:
            f.material_index=mi
            n=f.normal
            if mi==WOOD and axes:
                # grain along the longest box axis lying in this face
                cand=[(sz,ax) for ax,sz in zip(axes,sizes) if abs(ax.dot(n))<0.5]
                cand.sort(key=lambda a:-a[0])
                U=cand[0][1]; V=cand[1][1] if len(cand)>1 else n.cross(U)
            elif abs(n.z)>0.7: U=Vector((1,0,0)); V=Vector((0,1,0))
            else:
                U=n.cross(Vector((0,0,1))); U.normalize(); V=Vector((0,0,1))
            for l in f.loops:
                p=l.vert.co; l[s.uv].uv=(p.dot(U)/t,p.dot(V)/t)
    def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0):
        r=bmesh.ops.create_cube(s.bm,size=1.0); vs=r["verts"]
        R=Matrix.Rotation(rot[2],4,"Z")@Matrix.Rotation(rot[1],4,"Y")@Matrix.Rotation(rot[0],4,"X")
        M=Matrix.Translation(Vector(center))@R@Matrix.Diagonal((*size,1))
        bmesh.ops.transform(s.bm,matrix=M,verts=vs)
        if jitter:
            rnd=random.Random(seed)
            for v in vs: v.co+=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1)))*jitter
        faces=list({f for v in vs for f in v.link_faces}); s.bm.normal_update()
        axes=[(R@Vector(a)).normalized() for a in ((1,0,0),(0,1,0),(0,0,1))]
        s.project(faces,mi,axes,size)
        if bevel>0:
            edges=list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(s.bm,geom=edges+vs,offset=min(bevel,min(size)*0.45),segments=segs,profile=0.5,affect="EDGES",clamp_overlap=True)
        return vs
    def quad(s,pts,mi,uvs=None):
        vs=[s.bm.verts.new(p) for p in pts]; f=s.bm.faces.new(vs); f.material_index=mi; s.bm.normal_update()
        if uvs:
            for l,u in zip(f.loops,uvs): l[s.uv].uv=u
        else: s.project([f],mi)
        return f
    def finish(s,name,coll,wobble=True,grime=True,loc=(0,0,0)):
        bm=s.bm
        if wobble:
            for v in bm.verts:
                p=v.co
                # periodic in x (period = CELL) so neighbouring modules meet exactly
                v.co.y+=0.035*math.sin(2*math.pi*p.x/CELL+0.9)*math.sin(math.pi*max(0,min(p.z,6))/6)
                v.co.x+=0.02*math.sin(2*math.pi*p.z/2.3+0.4)
        bm.normal_update()
        for f in bm.faces:
            for l in f.loops:
                z=l.vert.co.z
                g=1.0
                if grime: g=0.62+0.38*min(1,max(0,z)/0.9)
                if f.normal.z<-0.6: g*=0.72    # undersides darker (painted AO)
                l[s.cl]=(g,g*0.98,g*0.95,1)
        me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth=False
        old=bpy.data.objects.get(name)
        if old: bpy.data.objects.remove(old)
        o=bpy.data.objects.new(name,me); coll.objects.link(o); o.location=loc
        for m in kit_mats(): me.materials.append(m)
        o["kit"]="VillageHouse"; o["cell_m"]=CELL
        return o
'''
t=bpy.data.texts.get("vk_helpers") or bpy.data.texts.new("vk_helpers"); t.clear(); t.write(code)
sc=bpy.data.scenes.get("VillageKit") or bpy.data.scenes.new("VillageKit")
bpy.context.window.scene=sc
exec(code)
kit_mats(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0078] 2026-09-23 01:55:36  blender  ERROR
# ==============================================================================================================
import bpy
code=r'''
def batter(k,amt=0.08):
    for v in k.bm.verts:
        if v.co.y<-0.2 and v.co.z<0.05: v.co.y-=amt
def stone_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25):
    k.box(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),STONE,bevel=0)
def plinth(k,x0=-1.5,x1=1.5):
    k.box(((x0+x1)/2,-0.05,0.18),(x1-x0,0.62,0.36),STONE,bevel=0)
def shutter(k,hx,side,z0,h,w=0.56,ang=2.1):
    # side=-1 left, +1 right; hinge at (hx, -0.3); rotate open by ang
    R=Matrix.Rotation(-side*ang,4,"Z")
    def put(center,size,mi):
        vs=k.box((0,0,0),size,mi,bevel=0.015)
        bmesh.ops.transform(k.bm,matrix=Matrix.Translation((hx,-0.32,0))@R@Matrix.Translation(Vector(center)),verts=vs)
    for i in range(3): put((-side*(0.1+i*0.185),-0.03,z0+h/2),(0.17,0.05,h),WOOD)
    for zz in (z0+0.2,z0+h-0.2): put((-side*w/2,-0.07,zz),(w-0.04,0.04,0.1),WOOD)
    put((-side*w*0.95,-0.09,z0+0.3),(0.03,0.02,0.12),IRON)
def window_frame(k,x0,x1,z0,z1,depth_y=-0.02,sill=True,shutters=True,face=-0.25):
    w=x1-x0; h=z1-z0
    k.quad([(x0,depth_y,z0),(x1,depth_y,z0),(x1,depth_y,z1),(x0,depth_y,z1)],WINDOW,uvs=[(0,0),(w,0),(w,h),(0,h)])
    for sx in (x0-0.07,x1+0.07): k.box((sx,face-0.02,(z0+z1)/2),(0.16,0.3,h+0.1),WOOD,bevel=0.03)
    k.box(((x0+x1)/2,face-0.05,z1+0.12),(w+0.5,0.36,0.24),WOOD,bevel=0.04)
    k.box(((x0+x1)/2,depth_y-0.03,(z0+z1)/2),(0.07,0.06,h),WOOD,bevel=0.01)
    k.box(((x0+x1)/2,depth_y-0.03,z0+h*0.55),(w,0.06,0.07),WOOD,bevel=0.01)
    if sill: k.box(((x0+x1)/2,face-0.1,z0-0.06),(w+0.36,0.46,0.14),STONE,bevel=0.03)
    if shutters:
        shutter(k,x0-0.14,-1,z0,h); shutter(k,x1+0.14,1,z0,h)
# ---------------- ground floor stone walls
def wall_stone_plain(k):
    stone_panel(k,-1.5,1.5,0,H1); plinth(k); batter(k)
def wall_stone_window(k):
    x0,x1,z0,z1=-0.55,0.55,1.05,2.25
    stone_panel(k,-1.5,x0,0,H1); stone_panel(k,x1,1.5,0,H1)
    stone_panel(k,x0,x1,0,z0); stone_panel(k,x0,x1,z1,H1)
    plinth(k); batter(k); window_frame(k,x0,x1,z0,z1)
def wall_stone_door(k):
    hw=0.68; spring=2.0; top=spring+hw
    stone_panel(k,-1.5,-hw,0,H1); stone_panel(k,hw,1.5,0,H1); stone_panel(k,-hw,hw,top,H1)
    z=spring
    while z<top-0.01:
        dz=0.08; c=math.sqrt(max(0,hw*hw-(z+dz/2-spring)**2))
        for s in(-1,1): stone_panel(k,min(s*c,s*hw),max(s*c,s*hw),z,z+dz)
        z+=dz
    plinth(k,-1.5,-hw-0.02); plinth(k,hw+0.02,1.5); batter(k)
    # voussoirs: chunky arch stones
    n=7
    for i in range(n):
        a=math.pi*(i+0.5)/n; r=hw+0.2
        k.box((math.cos(a)*r,-0.3,spring+math.sin(a)*r),(0.34,0.16,0.42 if i!=n//2 else 0.5),STONE,rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2)
    for s in(-1,1):
        for j,zz in enumerate((0.35,1.05,1.7)):
            k.box((s*(hw+0.16),-0.3,zz),(0.34 if j%2 else 0.46,0.16,0.62),STONE,bevel=0.05,segs=2)
    # door leaf
    for i in range(5):
        x=-hw+0.02+(i+0.5)*(2*hw-0.04)/5; top_i=spring+math.sqrt(max(0,hw*hw-x*x))-0.03
        k.box((x,0.02,top_i/2),((2*hw-0.04)/5-0.015,0.1,top_i),WOOD,bevel=0.012)
    for zz in (0.45,1.55):
        k.box((0,-0.05,zz),(2*hw-0.1,0.03,0.11),IRON,bevel=0.01)
        for s in(-1,1): k.box((s*(hw-0.12),-0.07,zz),(0.08,0.03,0.08),IRON,bevel=0.01)
    k.box((0.38,-0.08,1.05),(0.06,0.06,0.16),IRON,bevel=0.01)
    # reveal (inner surfaces of the opening)
    k.box((0,-0.02,0.08),(2*hw+0.1,0.5,0.16),STONE,bevel=0.02)
    k.box((0,-0.55,0.1),(1.7,0.6,0.2),STONE,bevel=0.05,segs=2,jitter=0.02,seed=3)
def corner_stone(k):
    # corner at origin, outer faces toward -X and -Y
    k.box((0,0,H1/2),(0.8,0.8,H1),STONE,bevel=0)
    k.box((0,0,0.2),(1.0,1.0,0.4),STONE,bevel=0.05,segs=2)
    z=0.4; i=0; rnd=random.Random(5)
    while z<H1-0.05:
        h=min(rnd.uniform(0.38,0.5),H1-z)
        long_x=(i%2==0)
        sx,sy=(1.05,0.62) if long_x else (0.62,1.05)
        cx=-0.43+sx/2; cy=-0.43+sy/2
        k.box((cx,cy,z+h/2),(sx,sy,h-0.03),STONE,bevel=0.06,segs=2,jitter=0.015,seed=i)
        z+=h; i+=1
# ---------------- upper floor timber walls (jettied)
FACE2=-0.40
def timber_frame(k,window=False):
    # belt beam + joist ends
    k.box((0,-0.14,0.15),(CELL,0.52,0.3),WOOD,bevel=0.04)
    for i in range(6):
        x=-1.25+i*0.5
        k.box((x,-0.47,-0.1),(0.16,0.3,0.2),WOOD,bevel=0.03)
    # plaster infill
    k.box((0,-0.08,H2/2+0.15),(CELL,0.46,H2-0.3),PLASTER,bevel=0)
    # top plate
    k.box((0,-0.2,H2-0.1),(CELL,0.46,0.22),WOOD,bevel=0.04)
    # left edge post (right edge belongs to the next module / corner)
    k.box((-1.5,-0.33,H2/2),(0.26,0.2,H2-0.4),WOOD,bevel=0.03)
    if not window:
        k.box((0,-0.33,H2/2),(0.22,0.2,H2-0.4),WOOD,bevel=0.03)
        for s in(-1,1):
            x0,z0=s*1.3,0.35; x1,z1=s*0.15,H2-0.25
            L=math.hypot(x1-x0,z1-z0); ang=math.atan2(z1-z0,x1-x0)
            k.box(((x0+x1)/2,-0.33,(z0+z1)/2),(L,0.18,0.17),WOOD,rot=(0,-ang,0),bevel=0.03)
        k.box((0,-0.33,1.35),(CELL,0.18,0.16),WOOD,bevel=0.03)
    else:
        x0,x1,z0,z1=-0.5,0.5,0.95,2.15
        window_frame(k,x0,x1,z0,z1,depth_y=-0.25,sill=False,shutters=False,face=FACE2+0.05)
        k.box((0,FACE2+0.02,z0-0.1),(1.4,0.26,0.16),WOOD,bevel=0.03)
        for s in(-1,1):
            k.box((s*0.72,-0.33,H2/2),(0.2,0.2,H2-0.4),WOOD,bevel=0.03)
            x0b,z0b=s*1.35,0.35; x1b,z1b=s*0.82,0.85
            L=math.hypot(x1b-x0b,z1b-z0b); ang=math.atan2(z1b-z0b,x1b-x0b)
            k.box(((x0b+x1b)/2,-0.33,(z0b+z1b)/2),(L,0.18,0.15),WOOD,rot=(0,-ang,0),bevel=0.03)
            L2=math.hypot(0.55,H2-1.0); k.box((s*1.1,-0.33,1.45),(0.16,0.18,1.05),WOOD,bevel=0.03)
def corner_timber(k):
    k.box((-0.2,-0.2,0.15),(0.66,0.66,0.3),WOOD,bevel=0.04)
    k.box((-0.26,-0.26,H2/2),(0.34,0.34,H2),WOOD,bevel=0.05,segs=2)
    k.box((-0.2,-0.2,H2-0.1),(0.62,0.62,0.22),WOOD,bevel=0.04)
    # dragon beam end under the corner
    k.box((-0.45,-0.45,-0.12),(0.26,0.26,0.26),WOOD,rot=(0,0,math.pi/4),bevel=0.04)
    k.box((-0.3,-0.3,-0.6),(0.2,0.2,0.8),WOOD,rot=(0.5,-0.5,0),bevel=0.03)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
for o in list(P.objects): bpy.data.objects.remove(o)
def make(name,fn,**kw):
    k=Kit(); fn(k); return k.finish(name,P,**kw)
make("SM_VK_Wall_Stone",wall_stone_plain)
make("SM_VK_Wall_Stone_Window",wall_stone_window)
make("SM_VK_Wall_Stone_Door",wall_stone_door)
make("SM_VK_Corner_Stone",corner_stone,wobble=False)
make("SM_VK_Wall_Timber",timber_frame,grime=False)
make("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),grime=False)
make("SM_VK_Corner_Timber",corner_timber,wobble=False,grime=False)
for o in P.objects: print(o.name,len(o.data.polygons))
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: verts: 0 BMVert has been removed"}

# ==============================================================================================================
# [0079] 2026-09-23 01:55:49  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0):",
            "def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0,xform=None):")
s=s.replace("        M=Matrix.Translation(Vector(center))@R@Matrix.Diagonal((*size,1))\n",
            "        M=Matrix.Translation(Vector(center))@R@Matrix.Diagonal((*size,1))\n        if xform is not None: M=xform@M; R=xform.to_3x3().to_4x4()@R\n")
s=s.replace('''    def put(center,size,mi):
        vs=k.box((0,0,0),size,mi,bevel=0.015)
        bmesh.ops.transform(k.bm,matrix=Matrix.Translation((hx,-0.32,0))@R@Matrix.Translation(Vector(center)),verts=vs)''',
'''    def put(center,size,mi):
        k.box(center,size,mi,bevel=0.015,xform=Matrix.Translation((hx,-0.32,0))@R)''')
t.clear(); t.write(s); exec(s)
P=vcol("VK_Pieces")
for o in list(P.objects): bpy.data.objects.remove(o)
def make(name,fn,**kw):
    k=Kit(); fn(k); return k.finish(name,P,**kw)
make("SM_VK_Wall_Stone",wall_stone_plain)
make("SM_VK_Wall_Stone_Window",wall_stone_window)
make("SM_VK_Wall_Stone_Door",wall_stone_door)
make("SM_VK_Corner_Stone",corner_stone,wobble=False)
make("SM_VK_Wall_Timber",timber_frame,grime=False)
make("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),grime=False)
make("SM_VK_Corner_Timber",corner_timber,wobble=False,grime=False)
for o in P.objects: print(o.name,len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone 12\nSM_VK_Wall_Stone_Window 499\nSM_VK_Wall_Stone_Door 1232\nSM_VK_Corner_Stone 384\nSM_VK_Wal
# l_Timber 344\nSM_VK_Wall_Timber_Window 553\nSM_VK_Corner_Timber 158\n"}

# ==============================================================================================================
# [0080] 2026-09-23 01:56:17  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
old='''def stone_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25):
    k.box(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),STONE,bevel=0)'''
new='''def grid_cut(k,vs,step=0.5):
    geom=list(set(vs)|{e for v in vs for e in v.link_edges}|{f for v in vs for f in v.link_faces})
    xs=[v.co.x for v in vs]; zs=[v.co.z for v in vs]
    x=math.floor(min(xs)/step)*step+step
    while x<max(xs)-0.05:
        r=bmesh.ops.bisect_plane(k.bm,geom=geom,plane_co=(x,0,0),plane_no=(1,0,0)); geom=list(set(geom)|set(r["geom"]))
        x+=step
    z=math.floor(min(zs)/step)*step+step
    while z<max(zs)-0.05:
        r=bmesh.ops.bisect_plane(k.bm,geom=[g for g in geom if g.is_valid],plane_co=(0,0,z),plane_no=(0,0,1)); geom=list(set(geom)|set(r["geom"]))
        z+=step
def stone_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25,mi=None):
    vs=k.box(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),STONE if mi is None else mi,bevel=0)
    grid_cut(k,vs)'''
s=s.replace(old,new)
s=s.replace("    k.box((0,-0.08,H2/2+0.15),(CELL,0.46,H2-0.3),PLASTER,bevel=0)","    grid_cut(k,k.box((0,-0.08,H2/2+0.15),(CELL,0.46,H2-0.3),PLASTER,bevel=0))")
t.clear(); t.write(s); exec(s)
P=vcol("VK_Pieces")
def make(name,fn,**kw):
    k=Kit(); fn(k); return k.finish(name,P,**kw)
make("SM_VK_Wall_Stone",wall_stone_plain)
make("SM_VK_Wall_Stone_Window",wall_stone_window)
make("SM_VK_Wall_Stone_Door",wall_stone_door)
make("SM_VK_Wall_Timber",timber_frame,grime=False)
make("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),grime=False)
# ---- staging
SC.world=bpy.data.scenes["MedievalColony"].world
SC.view_settings.look="AgX - Medium High Contrast"; SC.view_settings.exposure=-0.2
for kk,v in {"taa_render_samples":48,"use_raytracing":True,"use_gtao":True}.items():
    if hasattr(SC.eevee,kk): setattr(SC.eevee,kk,v)
SC.render.resolution_x=1920; SC.render.resolution_y=1080
S=vcol("VK_Staging")
if "VK_Sun" not in bpy.data.objects:
    so=bpy.data.objects.new("VK_Sun",bpy.data.lights["MC_Sun"]); S.objects.link(so)
    so.rotation_euler=(math.radians(52),math.radians(6),math.radians(-30))
cd=bpy.data.cameras.get("VK_Cam") or bpy.data.cameras.new("VK_Cam"); cd.lens=35
cam=bpy.data.objects.get("VK_Camera") or bpy.data.objects.new("VK_Camera",cd)
if cam.name not in S.objects: S.objects.link(cam)
SC.camera=cam
# lay out pieces in a row for a look
order=["SM_VK_Corner_Stone","SM_VK_Wall_Stone","SM_VK_Wall_Stone_Window","SM_VK_Wall_Stone_Door"]
for i,n in enumerate(order): bpy.data.objects[n].location=(-1.5+ (i-1)*3.0 + (0 if i else 1.5) ,0,0)
bpy.data.objects["SM_VK_Corner_Stone"].location=(-3.0,0,0)
for i,n in enumerate(["SM_VK_Wall_Timber","SM_VK_Wall_Timber_Window","SM_VK_Wall_Timber"]):
    o=bpy.data.objects[n] if i<2 else bpy.data.objects.get("tmp_tw") or bpy.data.objects.new("tmp_tw",bpy.data.objects[n].data)
    if o.name=="tmp_tw" and o.name not in P.objects: P.objects.link(o)
    o.location=(-1.5+i*3.0,0,H1)
bpy.data.objects["SM_VK_Corner_Timber"].location=(-3.0,0,H1)
cam.location=(4,-9,3.8); cam.rotation_euler=(Vector((1.2,0,2.8))-cam.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0081] 2026-09-23 01:56:52  blender  ok
# ==============================================================================================================
import bpy, numpy as np
# --- repaint wood: darker, calmer grain, painted plank streaks
def tnoise(S,fmax,n,decay,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,fmax+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
S=512; y,x=np.mgrid[0:S,0:S]/S
warp=tnoise(S,2,20,1.0,31)
grain=np.sin(2*np.pi*(y*6+warp*0.8))*0.5+0.5
fine=np.sin(2*np.pi*(y*38+warp*2+tnoise(S,6,30,0.8,34)*0.6))*0.5+0.5
blot=tnoise(S,4,30,1.0,35)
wd=np.array([0.23,0.14,0.08]); wl=np.array([0.40,0.26,0.15])
t=np.clip(0.45+0.25*(grain-0.5)+0.12*(fine-0.5)+0.15*blot,0,1)[...,None]
col=wd+(wl-wd)*t
img=bpy.data.images["T_VK_Wood"]
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([col,np.ones((S,S))])[::-1]).astype(np.float32).ravel()); img.save()
# --- plaster: more painted variation, warm
S=1024; y,x=np.mgrid[0:S,0:S]/S
b1=tnoise(S,4,40,1.0,21); b2=tnoise(S,16,120,0.6,22); b3=tnoise(S,70,160,0.35,23)
base=np.array([0.86,0.79,0.63])
col=base*(1+0.09*b1[...,None]+0.05*b2[...,None]+0.025*b3[...,None])
col=col*(1-0.12*np.clip(b2-0.3,0,1)[...,None]*np.array([0.8,1.0,1.4]))
img=bpy.data.images["T_VK_Plaster"]
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel()); img.save()
# --- code fixes
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("TILE={0:1.5,1:1.5,2:1.0,3:1.5,4:1.0,5:1.0}","TILE={0:2.4,1:2.0,2:1.6,3:1.5,4:1.0,5:1.0}")
s=s.replace('R=Matrix.Rotation(-side*ang,4,"Z")','R=Matrix.Rotation(side*ang,4,"Z")')
old_win='''    else:
        x0,x1,z0,z1=-0.5,0.5,0.95,2.15
        window_frame(k,x0,x1,z0,z1,depth_y=-0.25,sill=False,shutters=False,face=FACE2+0.05)'''
new_win='''    else:
        x0,x1,z0,z1=-0.5,0.5,0.95,2.15
        window_frame(k,x0,x1,z0,z1,depth_y=-0.12,sill=False,shutters=False,face=FACE2+0.05)'''
s=s.replace(old_win,new_win)
s=s.replace("    grid_cut(k,k.box((0,-0.08,H2/2+0.15),(CELL,0.46,H2-0.3),PLASTER,bevel=0))",
'''    if not window:
        grid_cut(k,k.box((0,-0.08,H2/2+0.15),(CELL,0.46,H2-0.3),PLASTER,bevel=0))
    else:
        for (a,b,c,d) in ((-1.5,-0.5,0.3,H2),(0.5,1.5,0.3,H2),(-0.5,0.5,0.3,0.95),(-0.5,0.5,2.15,H2)):
            grid_cut(k,k.box(((a+b)/2,-0.08,(c+d)/2),(b-a,0.46,d-c),PLASTER,bevel=0))''')
s=s.replace("            L2=math.hypot(0.55,H2-1.0); k.box((s*1.1,-0.33,1.45),(0.16,0.18,1.05),WOOD,bevel=0.03)\n","")
t.clear(); t.write(s); exec(s)
P=vcol("VK_Pieces")
def make(name,fn,**kw):
    k=Kit(); fn(k); o=k.finish(name,P,**kw); return o
locs={o.name:o.location.copy() for o in P.objects}
for n,fn,kw in [("SM_VK_Wall_Stone",wall_stone_plain,{}),("SM_VK_Wall_Stone_Window",wall_stone_window,{}),("SM_VK_Wall_Stone_Door",wall_stone_door,{}),
                ("SM_VK_Corner_Stone",corner_stone,{"wobble":False}),("SM_VK_Wall_Timber",timber_frame,{"grime":False}),
                ("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),{"grime":False}),("SM_VK_Corner_Timber",corner_timber,{"wobble":False,"grime":False})]:
    o=make(n,fn,**kw); o.location=locs.get(n,(0,0,0))
tw=bpy.data.objects.get("tmp_tw"); tw.data=bpy.data.objects["SM_VK_Wall_Timber"].data
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0082] 2026-09-23 01:57:57  blender  ok
# ==============================================================================================================
import bpy
code=r'''
PITCH=math.radians(52); KICK=math.radians(26); HALF=3.0; EAVE=4.35; RT=0.3
def roof_z(ay):
    # top surface height at |y|=ay (relative to wall top), with bell-cast eave
    if ay<=HALF: return 0.35+(HALF-ay)*math.tan(PITCH)
    return 0.35-(ay-HALF)*math.tan(KICK)
RIDGE=roof_z(0)
def roof_profile():
    ys=[0,0.75,1.5,2.25,3.0,3.45,3.9,EAVE]
    return [(y,roof_z(y)) for y in ys]
def roof_sag(x,ay):
    return -0.07*(0.5-0.5*math.cos(2*math.pi*x/CELL))*(1-ay/EAVE)   # gentle periodic sag, zero at module seams
def roof_slab(k,x0,x1,side,end_caps=(False,False)):
    prof=roof_profile(); nx=max(2,int(round((x1-x0)/0.5)))
    xs=[x0+(x1-x0)*i/nx for i in range(nx+1)]
    # accumulate along-slope distance from eave for V
    dist=[0.0]*len(prof)
    for i in range(len(prof)-2,-1,-1):
        dist[i]=dist[i+1]+math.hypot(prof[i+1][0]-prof[i][0],prof[i+1][1]-prof[i][1])
    top=[];bot=[]
    for x in xs:
        rt=[];rb=[]
        for j,(ay,z) in enumerate(prof):
            a=prof[max(j-1,0)]; b=prof[min(j+1,len(prof)-1)]
            ty,tz=b[0]-a[0],b[1]-a[1]; L=math.hypot(ty,tz); ny,nz=tz/L,-ty/L   # outward normal (in ay,z)
            if nz<0: ny,nz=-ny,-nz
            zz=z+roof_sag(x,ay)
            rt.append(k.bm.verts.new((x,side*ay,zz)))
            rb.append(k.bm.verts.new((x,side*(ay-ny*RT),zz-nz*RT)))
        top.append(rt); bot.append(rb)
    def F(vs,mi,uvs):
        if side>0: vs=vs[::-1]; uvs=uvs[::-1]
        f=k.bm.faces.new(vs); f.material_index=mi
        for l,u in zip(f.loops,uvs): l[k.uv].uv=u
        return f
    T=TILE[ROOF]; W=TILE[WOOD]
    for i in range(nx):
        for j in range(len(prof)-1):
            F([top[i][j],top[i][j+1],top[i+1][j+1],top[i+1][j]],ROOF,
              [(xs[i]/T,dist[j]/T),(xs[i]/T,dist[j+1]/T),(xs[i+1]/T,dist[j+1]/T),(xs[i+1]/T,dist[j]/T)])
            F([bot[i+1][j],bot[i+1][j+1],bot[i][j+1],bot[i][j]],WOOD,
              [(xs[i+1]/W,dist[j]/W),(xs[i+1]/W,dist[j+1]/W),(xs[i]/W,dist[j+1]/W),(xs[i]/W,dist[j]/W)])
        j=len(prof)-1   # eave fascia
        F([top[i][j],top[i+1][j],bot[i+1][j],bot[i][j]],WOOD,[(xs[i]/W,0),(xs[i+1]/W,0),(xs[i+1]/W,RT/W),(xs[i]/W,RT/W)])
        F([bot[i][0],bot[i+1][0],top[i+1][0],top[i][0]],WOOD,[(0,0),(1,0),(1,0.2),(0,0.2)])
    for ci,(cap,xi) in enumerate(zip(end_caps,(0,nx))):
        if not cap: continue
        for j in range(len(prof)-1):
            vs=[top[xi][j],top[xi][j+1],bot[xi][j+1],bot[xi][j]]
            if (ci==0)==(side>0): vs=vs[::-1]
            f=k.bm.faces.new(vs); f.material_index=WOOD
            for l in f.loops: l[k.uv].uv=(l.vert.co.y/W,l.vert.co.z/W)
    k.bm.normal_update()
def ridge(k,x0,x1):
    n=max(1,int(round((x1-x0)/0.75)))
    for i in range(n):
        xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n; xm=(xa+xb)/2
        k.box((xm,0,RIDGE+0.1+roof_sag(xm,0)),(xb-xa+0.04,0.36,0.36),ROOF,rot=(math.pi/4,0,0),bevel=0.1,segs=2)
def roof_mid(k):
    for s in(-1,1): roof_slab(k,-1.5,1.5,s)
    ridge(k,-1.5,1.5)
GX=2.45   # gable overhang end (x)
def roof_gable(k):
    for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True))
    ridge(k,-1.5,GX+0.1)
    # bargeboards following both slopes
    prof=roof_profile()
    for s in(-1,1):
        for j in range(len(prof)-1):
            (y0,z0),(y1,z1)=prof[j],prof[j+1]
            L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,y1-y0)
            yc=s*(y0+y1)/2; zc=(z0+z1)/2-0.12
            k.box((GX+0.06,yc,zc),(0.14,L+0.06,0.42),WOOD,rot=(s*ang,0,0),bevel=0.035)
    # finial
    k.box((GX+0.08,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,segs=2)
    k.box((GX+0.08,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)
    # gable triangle wall (timber framed plaster), face at x=+1.5+0.40
    XF=1.5+0.40; XB=1.5-0.05
    def tri_z(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.02
    pts=[(-HALF-0.4,0.0),(HALF+0.4,0.0),(0.0,tri_z(0))]
    for (xf,flip) in ((XF-0.06,False),(XB,True)):
        vs=[k.bm.verts.new((xf,y,z)) for y,z in pts]
        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=PLASTER
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[PLASTER],l.vert.co.z/TILE[PLASTER])
    k.bm.normal_update()
    # sole beam, collar, king post, rafters
    k.box((XF-0.02,0,0.12),(0.2,2*HALF+0.9,0.26),WOOD,bevel=0.04)
    for i in range(6):
        k.box((XF+0.1,-1.25*2+i*1.0,-0.12),(0.3,0.16,0.2),WOOD,bevel=0.03)
    zc=tri_z(0)*0.45; half_c=HALF+0.4-(zc/ tri_z(0))*(HALF+0.4)
    k.box((XF-0.02,0,zc),(0.18,2*half_c,0.2),WOOD,bevel=0.035)
    k.box((XF-0.02,0,tri_z(0)/2),(0.18,0.24,tri_z(0)),WOOD,bevel=0.035)
    for s in(-1,1):
        L=math.hypot(HALF+0.4,tri_z(0)); ang=math.atan2(tri_z(0),HALF+0.4)
        k.box((XF-0.02,s*(HALF+0.4)/2,tri_z(0)/2-0.05),(0.18,L,0.2),WOOD,rot=(-s*ang,0,0),bevel=0.035)
        # lower braces
        k.box((XF-0.02,s*1.6,zc/2+0.1),(0.16,0.16,zc-0.1),WOOD,bevel=0.03)
    # small attic window
    wz=zc+0.25
    k.quad([(XF-0.04,-0.35,wz),(XF-0.04,0.35,wz),(XF-0.04,0.35,wz+0.8),(XF-0.04,-0.35,wz+0.8)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,0.8),(0,0.8)])
    for yy in(-0.42,0.42): k.box((XF+0.02,yy,wz+0.4),(0.14,0.13,0.95),WOOD,bevel=0.025)
    for zz in(wz-0.05,wz+0.85): k.box((XF+0.02,0,zz),(0.16,0.95,0.13),WOOD,bevel=0.025)
    k.box((XF+0.02,0,wz+0.4),(0.06,0.05,0.8),WOOD,bevel=0.01)
def chimney(k):
    y0=1.3
    k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STONE,bevel=0.06,segs=2)
    k.box((0,y0,RIDGE+1.55),(1.25,1.25,0.22),STONE,bevel=0.07,segs=2)
    for dx in(-0.22,0.22):
        k.box((dx,y0,RIDGE+1.9),(0.3,0.3,0.5),STONE,bevel=0.06,segs=2)
    k.box((0,y0,RIDGE+1.0),(1.12,1.12,0.16),STONE,bevel=0.05)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
def make(name,fn,**kw):
    k=Kit(); fn(k); return k.finish(name,P,**kw)
for n,fn in [("SM_VK_Roof_Mid",roof_mid),("SM_VK_Roof_Gable",roof_gable),("SM_VK_Chimney",chimney)]:
    o=make(n,fn,wobble=False,grime=False); print(n,len(o.data.polygons))
print("ridge",RIDGE)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Mid 408\nSM_VK_Roof_Gable 1483\nSM_VK_Chimney 242\nridge 4.189824896579236\n"}

# ==============================================================================================================
# [0083] 2026-09-23 01:58:33  blender  ERROR
# ==============================================================================================================
import bpy
code=r'''
def roof_variant(src,suffix,matname):
    o=bpy.data.objects.get(src.name+suffix)
    me=src.data.copy(); me.name=src.name+suffix
    me.materials[ROOF]=bpy.data.materials[matname]
    if o: o.data=me
    else:
        o=bpy.data.objects.new(src.name+suffix,me); vcol("VK_Pieces").objects.link(o)
    return o
def place(coll,piece,x,y,z,rot_deg,origin):
    src=bpy.data.objects[piece]
    o=bpy.data.objects.new(piece+"_inst",src.data); coll.objects.link(o)
    ox,oy,orz=origin
    c,s=math.cos(orz),math.sin(orz)
    o.location=(ox+x*c-y*s,oy+x*s+y*c,z); o.rotation_euler=(0,0,orz+math.radians(rot_deg))
    return o
def build_house(coll,origin,n,stories=2,roof="Red",front=None,back=None,upper_front=None,upper_back=None,ends="W",chimney_cell=None):
    """front/back: string per cell  D=door W=window .=plain ; ends: pattern for both gable end walls (2 cells)"""
    L=n*CELL; sfx="" if roof=="Red" else "_Blue"
    front=front or "."*n; back=back or "."*n
    upper_front=upper_front or "W"*n; upper_back=upper_back or "."*n
    gw={"D":"SM_VK_Wall_Stone_Door","W":"SM_VK_Wall_Stone_Window",".":"SM_VK_Wall_Stone"}
    uw={"W":"SM_VK_Wall_Timber_Window",".":"SM_VK_Wall_Timber"}
    for i in range(n):
        x=-L/2+1.5+3*i
        place(coll,gw[front[i]],x,-3,0,0,origin); place(coll,gw[back[::-1][i]],x,3,0,180,origin)
    for j,yy in enumerate((-1.5,1.5)):
        e=ends[j] if len(ends)>1 else ends
        place(coll,gw[e],-L/2,yy,0,-90,origin); place(coll,gw[e],L/2,-yy,0,90,origin)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
        place(coll,"SM_VK_Corner_Stone",cx,cy,0,r,origin)
    top=H1
    if stories==2:
        for i in range(n):
            x=-L/2+1.5+3*i
            place(coll,uw[upper_front[i]],x,-3,H1,0,origin); place(coll,uw[upper_back[::-1][i]],x,3,H1,180,origin)
        for yy in (-1.5,1.5):
            place(coll,"SM_VK_Wall_Timber",-L/2,yy,H1,-90,origin); place(coll,"SM_VK_Wall_Timber",L/2,-yy,H1,90,origin)
        for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
            place(coll,"SM_VK_Corner_Timber",cx,cy,H1,r,origin)
        top=H1+H2
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==n-1: place(coll,"SM_VK_Roof_Gable"+sfx,x,0,top,0,origin)
        elif i==0: place(coll,"SM_VK_Roof_Gable"+sfx,x,0,top,180,origin)
        else: place(coll,"SM_VK_Roof_Mid"+sfx,x,0,top,0,origin)
    if chimney_cell is not None:
        place(coll,"SM_VK_Chimney",-L/2+1.5+3*chimney_cell,0,top,0,origin)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
for n in ("SM_VK_Roof_Mid","SM_VK_Roof_Gable"): roof_variant(bpy.data.objects[n],"_Blue","M_VK_RoofBlue")
tex_mat("M_VK_RoofBlue","T_VK_RoofBlue",0.7)
for n in ("SM_VK_Roof_Mid","SM_VK_Roof_Gable"): roof_variant(bpy.data.objects[n],"_Blue","M_VK_RoofBlue")
# hide piece layout, build a test house
for o in vcol("VK_Pieces").objects: o.hide_render=True; o.hide_viewport=True
D=vcol("VK_Demo")
for o in list(D.objects): bpy.data.objects.remove(o)
build_house(D,(0,0,0),3,2,"Red",front="WDW",back=".W.",upper_front="WWW",upper_back="W.W",ends="W.",chimney_cell=0)
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=32
tgt=Vector((0,0,3.6)); cam.location=tgt+Vector((11,-15,4.5))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
if "VK_Ground" not in bpy.data.objects:
    bm=bmesh.new(); bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=60)
    me=bpy.data.meshes.new("VK_Ground"); bm.to_mesh(me); bm.free()
    g=bpy.data.objects.new("VK_Ground",me); vcol("VK_Staging").objects.link(g); me.materials.append(bpy.data.materials["MC_WK_Grass"])
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: 'bpy_prop_collection[key]: key \"M_VK_RoofBlue\" not found'"}

# ==============================================================================================================
# [0084] 2026-09-23 01:58:47  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
tex_mat("M_VK_RoofBlue","T_VK_RoofBlue",0.7)
for n in ("SM_VK_Roof_Mid","SM_VK_Roof_Gable"): roof_variant(bpy.data.objects[n],"_Blue","M_VK_RoofBlue")
for o in vcol("VK_Pieces").objects: o.hide_render=True; o.hide_viewport=True
D=vcol("VK_Demo")
for o in list(D.objects): bpy.data.objects.remove(o)
build_house(D,(0,0,0),3,2,"Red",front="WDW",back=".W.",upper_front="WWW",upper_back="W.W",ends="W.",chimney_cell=0)
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=32
tgt=Vector((0,0,3.6)); cam.location=tgt+Vector((11,-15,4.5))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
if "VK_Ground" not in bpy.data.objects:
    bm=bmesh.new(); bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=60)
    me=bpy.data.meshes.new("VK_Ground"); bm.to_mesh(me); bm.free()
    g=bpy.data.objects.new("VK_Ground",me); vcol("VK_Staging").objects.link(g); me.materials.append(bpy.data.materials["MC_WK_Grass"])
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0085] 2026-09-23 01:59:10  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string().replace("TILE={0:2.4,1:2.0,2:1.6,3:1.5,4:1.0,5:1.0}","TILE={0:2.4,1:2.0,2:1.6,3:2.6,4:1.0,5:1.0}")
t.clear(); t.write(s); exec(s)
P=vcol("VK_Pieces")
for n,fn in [("SM_VK_Roof_Mid",roof_mid),("SM_VK_Roof_Gable",roof_gable),("SM_VK_Chimney",chimney)]:
    k=Kit(); fn(k); o=k.finish(n,P,wobble=False,grime=False); o.hide_viewport=o.hide_render=True
for n in ("SM_VK_Roof_Mid","SM_VK_Roof_Gable"): roof_variant(bpy.data.objects[n],"_Blue","M_VK_RoofBlue").hide_render=True
# relink demo instances to the rebuilt meshes
for o in vcol("VK_Demo").objects:
    base=o.name.split("_inst")[0]
    if base in bpy.data.objects: o.data=bpy.data.objects[base].data
cam=bpy.data.objects["VK_Camera"]
tgt=Vector((4.5,0,6.5)); cam.location=tgt+Vector((9,-7,1.5))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0086] 2026-09-23 01:59:43  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def prop_flowerbox(k):
    k.box((0,0,0.12),(1.25,0.32,0.24),WOOD,bevel=0.03)
    for sx in(-0.45,0.45): k.box((sx,0.08,-0.1),(0.08,0.2,0.25),WOOD,bevel=0.02)
    rnd=random.Random(4)
    for i in range(16):
        x=-0.52+i*0.07; 
        k.box((x,rnd.uniform(-0.08,0.08),0.3+rnd.uniform(0,0.08)),(0.16,0.14,0.16),LEAF,rot=(0,0,rnd.uniform(0,3)),bevel=0.05,segs=1)
    for i in range(11):
        x=-0.5+i*0.1+rnd.uniform(-.03,.03)
        vs=bmesh.ops.create_icosphere(k.bm,subdivisions=1,radius=0.075)["verts"]
        for v in vs: v.co+=Vector((x,rnd.uniform(-0.08,0.08),0.43+rnd.uniform(0,0.1)))
        for f in {f for v in vs for f in v.link_faces}: f.material_index=PINK if i%3 else YELLOW
def prop_lantern(k):
    k.box((0,0.05,0.0),(0.1,0.1,0.35),IRON,bevel=0.02)
    k.box((0,-0.2,0.15),(0.06,0.5,0.06),IRON,bevel=0.015)
    k.box((0,-0.42,0.05),(0.03,0.03,0.2),IRON,bevel=0)
    k.box((0,-0.42,-0.22),(0.24,0.24,0.34),GLOW,bevel=0.03)
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*0.12,-0.42+sy*0.12,-0.22),(0.035,0.035,0.38),IRON,bevel=0)
    k.box((0,-0.42,-0.02),(0.32,0.32,0.07),IRON,bevel=0.02); k.box((0,-0.42,0.06),(0.2,0.2,0.1),IRON,bevel=0.03)
    k.box((0,-0.42,-0.41),(0.28,0.28,0.05),IRON,bevel=0.015)
def prop_sign(k):
    k.box((0,0.03,0),(0.14,0.1,0.5),IRON,bevel=0.02)
    k.box((0,-0.55,0.12),(0.07,1.1,0.07),IRON,bevel=0.015)
    vs=k.box((0,-0.78,-0.05),(0.04,0.04,0.7),IRON,bevel=0,rot=(0.6,0,0))
    for yy in(-0.35,-0.95): k.box((0,yy,-0.05),(0.02,0.02,0.3),IRON,bevel=0)
    k.box((0,-0.65,-0.45),(0.08,0.9,0.6),WOOD,bevel=0.04,segs=2)
    k.box((0,-0.65,-0.45),(0.1,0.3,0.3),YELLOW,rot=(math.pi/4,0,0),bevel=0.03)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
for n,fn in [("SM_VK_Prop_FlowerBox",prop_flowerbox),("SM_VK_Prop_Lantern",prop_lantern),("SM_VK_Prop_Sign",prop_sign)]:
    k=Kit(); fn(k); o=k.finish(n,P,wobble=False,grime=False); o.hide_viewport=o.hide_render=True; print(n,len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_FlowerBox 714\nSM_VK_Prop_Lantern 186\nSM_VK_Prop_Sign 150\n"}

# ==============================================================================================================
# [0087] 2026-09-23 02:00:06  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
D=vcol("VK_Demo")
for o in list(D.objects): bpy.data.objects.remove(o)
def dress(coll,origin,n,front,sign=False,stories=2):
    L=n*CELL
    for i,ch in enumerate(front):
        x=-L/2+1.5+3*i
        if ch=="W": place(coll,"SM_VK_Prop_FlowerBox",x,-3.55,0.78,0,origin)
        if ch=="D":
            place(coll,"SM_VK_Prop_Lantern",x+1.0,-3.3,2.55,0,origin)
            if sign: place(coll,"SM_VK_Prop_Sign",x-1.05,-3.3,2.85,0,origin)
R=math.radians
houses=[((-10,-8.5,R(180)),3,2,"Red","WDW","WWW",0,True),
        ((1.5,-8.0,R(180)),2,1,"Blue","DW","..",None,False),
        ((11,-9.0,R(180)),3,2,"Blue","WWD","W.W",2,False),
        ((-7.5,8.5,0),4,2,"Blue","WDWW","WWWW",3,False),
        ((6.5,8.0,0),2,2,"Red","WD","WW",0,False),
        ((16,7.5,R(-8)),2,1,"Red","DW","..",1,False)]
for (org,n,st,roof,front,ufront,chim,sign) in houses:
    build_house(D,org,n,st,roof,front=front,back="."*(n-1)+"W",upper_front=ufront,ends="W.",chimney_cell=chim)
    dress(D,org,n,front,sign)
# street
bm=bmesh.new()
pts=[(-26,0.3),(-12,-0.4),(0,0.4),(12,-0.3),(26,0.5)]
w=3.4
for i in range(len(pts)-1):
    (x0,y0),(x1,y1)=pts[i],pts[i+1]
    vs=[bm.verts.new(p) for p in ((x0,y0-w,0.02),(x1,y1-w,0.02),(x1,y1+w,0.02),(x0,y0+w,0.02))]
    bm.faces.new(vs)
me=bpy.data.meshes.new("VK_Street"); bm.to_mesh(me); bm.free()
old=bpy.data.objects.get("VK_Street")
if old: bpy.data.objects.remove(old)
st=bpy.data.objects.new("VK_Street",me); D.objects.link(st); me.materials.append(bpy.data.materials["MC_WK_Dirt"])
# trees from the TreeAsset scene (instances)
tw=bpy.data.objects["SM_Tree_Wood"].data; tf=bpy.data.objects["SM_Tree_Foliage"].data
for i,(x,y,s,r) in enumerate([(-19,-11,1.0,0.3),(-19,12,1.1,2.0),(21,-12,0.9,4.0),(0,15,1.15,1.1),(22,13.5,0.85,5.2)]):
    for d,nm in ((tw,"W"),(tf,"F")):
        o=bpy.data.objects.new(f"VK_Tree{i}{nm}",d); D.objects.link(o); o.location=(x,y,0); o.scale=(s,s,s); o.rotation_euler.z=r
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=30
tgt=Vector((1,0,2.5)); cam.location=tgt+Vector((16,-30,17))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
bpy.data.objects["VK_Ground"].scale=(2,2,1)
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0088] 2026-09-23 02:00:35  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
cd=bpy.data.cameras.new("dbg"); cd.lens=40; c=bpy.data.objects.new("dbgcam",cd); SC.collection.objects.link(c)
tgt=Vector((6.5,8.0,7.5)); c.location=tgt+Vector((-4,-9,6))
c.rotation_euler=(tgt-c.location).to_track_quat("-Z","Y").to_euler()
SC.camera=c
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_dbg.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0089] 2026-09-23 02:01:09  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
start=s.index("    # gable triangle wall (timber framed plaster)")
end=s.index("def chimney(k):")
new_gable='''    # gable triangle wall (timber framed plaster), face at x=+1.5+0.40, follows the roof underside exactly
    XF=1.5+0.40; XB=1.5-0.05
    def under(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.05
    YC=HALF+0.02
    ys=[YC,2.5,2.0,1.5,1.0,0.5,0.0]
    outline=[(-YC,0.0),(YC,0.0)]+[(y,under(y)) for y in ys]+[(-y,under(y)) for y in ys[::-1][1:]]
    for (xf,flip) in ((XF-0.06,False),(XB,True)):
        vs=[k.bm.verts.new((xf,y,z)) for y,z in outline]
        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=PLASTER
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[PLASTER],l.vert.co.z/TILE[PLASTER])
    k.bm.normal_update()
    top=under(0)
    k.box((XF-0.02,0,0.12),(0.2,2*YC,0.24),WOOD,bevel=0.04)
    for i in range(6):
        k.box((XF+0.1,-2.5+i*1.0,-0.12),(0.3,0.16,0.2),WOOD,bevel=0.03)
    zc=top*0.45; half_c=YC*(1-zc/top)*0.98
    k.box((XF-0.02,0,zc),(0.18,2*half_c,0.2),WOOD,bevel=0.035)
    k.box((XF-0.02,0,top/2),(0.18,0.24,top),WOOD,bevel=0.035)
    for s_ in(-1,1):
        # raking beams: follow the underside, inset 0.12
        L=math.hypot(YC,top); ang=math.atan2(top,YC)
        k.box((XF-0.02,s_*YC/2,top/2-0.14),(0.18,L,0.2),WOOD,rot=(-s_*ang,0,0),bevel=0.035)
        k.box((XF-0.02,s_*1.6,zc/2+0.1),(0.16,0.16,zc-0.1),WOOD,bevel=0.03)
    wz=zc+0.25
    k.quad([(XF-0.04,-0.35,wz),(XF-0.04,0.35,wz),(XF-0.04,0.35,wz+0.8),(XF-0.04,-0.35,wz+0.8)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,0.8),(0,0.8)])
    for yy in(-0.42,0.42): k.box((XF+0.02,yy,wz+0.4),(0.14,0.13,0.95),WOOD,bevel=0.025)
    for zz in(wz-0.05,wz+0.85): k.box((XF+0.02,0,zz),(0.16,0.95,0.13),WOOD,bevel=0.025)
    k.box((XF+0.02,0,wz+0.4),(0.06,0.05,0.8),WOOD,bevel=0.01)
'''
s=s[:start]+new_gable+s[end:]
# chunkier, continuous bargeboards sitting just proud of the roof surface
s=s.replace('''            yc=s*(y0+y1)/2; zc=(z0+z1)/2-0.12
            k.box((GX+0.06,yc,zc),(0.14,L+0.06,0.42),WOOD,rot=(s*ang,0,0),bevel=0.035)''',
'''            yc=s*(y0+y1)/2; zc=(z0+z1)/2-0.16
            k.box((GX+0.08,yc,zc),(0.2,L+0.2,0.46),WOOD,rot=(s*ang,0,0),bevel=0.05,segs=2)''')
t.clear(); t.write(s); exec(s)
P=vcol("VK_Pieces")
k=Kit(); roof_gable(k); o=k.finish("SM_VK_Roof_Gable",P,wobble=False,grime=False); o.hide_viewport=o.hide_render=True
roof_variant(o,"_Blue","M_VK_RoofBlue").hide_render=True
for inst in vcol("VK_Demo").objects:
    base=inst.name.split("_inst")[0]
    if base in ("SM_VK_Roof_Gable","SM_VK_Roof_Gable_Blue"): inst.data=bpy.data.objects[base].data
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0090] 2026-09-23 02:01:25  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
c=bpy.data.objects.get("dbgcam")
if c: cd=c.data; bpy.data.objects.remove(c); bpy.data.cameras.remove(cd)
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=28
tgt=Vector((4,0.5,2.0)); cam.location=Vector((-21,-3.5,12.5))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0091] 2026-09-23 02:01:40  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=32
tgt=Vector((2,0,2.5)); cam.location=Vector((-33,-13,13))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=100
SC.render.filepath=os.path.join(out,"village_street.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# close-up of one house front
cd=bpy.data.cameras.get("VK_CamClose") or bpy.data.cameras.new("VK_CamClose"); cd.lens=35
cc=bpy.data.objects.get("VK_CameraClose") or bpy.data.objects.new("VK_CameraClose",cd)
if cc.name not in SC.collection.objects: SC.collection.objects.link(cc)
tgt=Vector((-10,-4.5,3.6)); cc.location=Vector((-2.5,2.5,2.4))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.filepath=os.path.join(out,"village_house_closeup.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
SC.camera=cam
os.remove(os.path.join(out,"_vk_test.png")); os.remove(os.path.join(out,"_vk_dbg.png"))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0092] 2026-09-23 02:02:12  blender  ok
# ==============================================================================================================
import bpy, os
exec(bpy.data.texts["vk_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
for nm in ("VK_Tree0W","VK_Tree0F"): bpy.data.objects[nm].location=(-22,-19,0)
SC.camera=bpy.data.objects["VK_Camera"]; SC.render.resolution_percentage=100
SC.render.filepath=os.path.join(out,"village_street.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- kit lineup at y=-60 (hide demo during this render)
demo=list(vcol("VK_Demo").objects)
for o in demo: o.hide_render=True
row1=["SM_VK_Corner_Stone","SM_VK_Wall_Stone","SM_VK_Wall_Stone_Window","SM_VK_Wall_Stone_Door"]
row2=["SM_VK_Corner_Timber","SM_VK_Wall_Timber","SM_VK_Wall_Timber_Window"]
row3=["SM_VK_Roof_Gable","SM_VK_Roof_Mid","SM_VK_Roof_Mid_Blue","SM_VK_Roof_Gable_Blue"]
props=["SM_VK_Chimney","SM_VK_Prop_FlowerBox","SM_VK_Prop_Lantern","SM_VK_Prop_Sign"]
shown=[]
def show(n,loc,rz=0):
    o=bpy.data.objects[n]; o.hide_render=False; o.hide_viewport=False; o.location=loc; o.rotation_euler=(0,0,rz); shown.append(o)
Y=-60
for i,n in enumerate(row1): show(n,(-6+i*4.2+(0.8 if i==0 else 0),Y,0))
for i,n in enumerate(row2): show(n,(-6+i*4.2+(0.8 if i==0 else 0),Y+6,0))
for i,n in enumerate(row3): show(n,(-7+i*6.2,Y+16,-2.0))
show("SM_VK_Chimney",(13,Y+4,-4.0)); show("SM_VK_Prop_FlowerBox",(12,Y-2,0.4)); show("SM_VK_Prop_Lantern",(14.5,Y-2,1.2)); show("SM_VK_Prop_Sign",(16.5,Y-2,1.8))
cd=bpy.data.cameras.get("VK_CamKit") or bpy.data.cameras.new("VK_CamKit"); cd.lens=30
ck=bpy.data.objects.get("VK_CameraKit") or bpy.data.objects.new("VK_CameraKit",cd)
if ck.name not in SC.collection.objects: SC.collection.objects.link(ck)
tgt=Vector((4.5,Y+6,2.2)); ck.location=tgt+Vector((4,-30,17))
ck.rotation_euler=(tgt-ck.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ck; SC.render.filepath=os.path.join(out,"village_kit_pieces.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for o in demo: o.hide_render=False
for o in shown: o.hide_render=True
SC.camera=bpy.data.objects["VK_Camera"]
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0093] 2026-09-23 02:12:21  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
# split roof_gable into slab part + reusable gable_end(k)
a=s.index("def roof_gable(k):")
b=s.index("    # bargeboards following both slopes",a)
s=s[:a]+'''def roof_gable(k):
    for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True))
    ridge(k,-1.5,GX+0.1)
    gable_end(k)
def gable_end(k):
'''+s[b:]
t.clear(); t.write(s)
code=r'''
def merge_kit(dst,src,M):
    """append src Kit geometry into dst Kit, transformed by matrix M"""
    me=bpy.data.meshes.new("_tmp"); src.bm.to_mesh(me); src.bm.free()
    me.transform(M)
    dst.bm.from_mesh(me); bpy.data.meshes.remove(me)
def slope_dist(ay):
    ay=min(ay,EAVE)
    if ay>=HALF: return (EAVE-ay)/math.cos(KICK)
    return (EAVE-HALF)/math.cos(KICK)+(HALF-ay)/math.cos(PITCH)
def roof_L_corner(k):
    """Junction of two wings: main wing A along +X (ridge y=0), wing B along +Y (ridge x=0).
    Covers the 2x2-cell junction square x,y in [-3,3]; A has its gable on the outer -X side,
    B joins with valleys along y=|x|. Neighbours: Roof_Mid at x>3 (rot 0) and at y>3 (rot 90)."""
    GO=-HALF-(GX-1.5)          # gable overhang edge x = -3.95
    def zA(y): return roof_z(abs(y))
    def zB(x): return roof_z(abs(x))
    def surf(x,y):
        if y<=0: return zA(y),"A"
        a,b=zA(y),zB(x)
        return (a,"A") if a>=b else (b,"B")
    xs=[GO,-3.5]+[i*0.5 for i in range(-6,7)]
    ys=[-EAVE,-3.9,-3.45]+[i*0.5 for i in range(-6,7)]
    xs=sorted(set(round(v,4) for v in xs)); ys=sorted(set(round(v,4) for v in ys))
    T=TILE[ROOF]; W=TILE[WOOD]
    top={};bot={}
    for x in xs:
        for y in ys:
            z,_=surf(x,y); top[(x,y)]=k.bm.verts.new((x,y,z)); bot[(x,y)]=k.bm.verts.new((x,y,z-RT*1.25))
    def uv_for(p,region):
        x,y,z=p
        return (x/T,slope_dist(abs(y))/T) if region=="A" else (y/T,slope_dist(abs(x))/T)
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
            q=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            # split along the valley direction where the crease runs through the quad
            if y0>=0 and x0>=0: tris=[(0,1,2),(0,2,3)]
            elif y0>=0 and x1<=0: tris=[(0,1,3),(1,2,3)]
            else: tris=[(0,1,2),(0,2,3)]
            for tr in tris:
                pts=[q[t_] for t_ in tr]
                cx=sum(p[0] for p in pts)/3; cy=sum(p[1] for p in pts)/3
                _,reg=surf(cx,cy)
                f=k.bm.faces.new([top[p] for p in pts]); f.material_index=ROOF
                for l,p in zip(f.loops,pts): l[k.uv].uv=uv_for((p[0],p[1],0),reg)
                fb=k.bm.faces.new([bot[p] for p in pts[::-1]]); fb.material_index=WOOD
                for l in fb.loops: l[k.uv].uv=(l.vert.co.x/W,l.vert.co.y/W)
    # fascia along the outer eave (y=-EAVE) and the gable edge (x=GO)
    def side(ptsa,ptsb):
        for (a_,b_) in zip(ptsa,ptsb):
            f=k.bm.faces.new((top[a_],top[b_],bot[b_],bot[a_])); f.material_index=WOOD
            for l in f.loops: l[k.uv].uv=((l.vert.co.x+l.vert.co.y)/W,l.vert.co.z/W)
    side([(xs[i+1],ys[0]) for i in range(len(xs)-1)],[(xs[i],ys[0]) for i in range(len(xs)-1)])
    side([(xs[0],ys[j]) for j in range(len(ys)-1)],[(xs[0],ys[j+1]) for j in range(len(ys)-1)])
    k.bm.normal_update()
    # ridge caps: A ridge through the whole piece, B ridge from the junction to the +Y seam
    ridge(k,GO-0.1,HALF)
    n=4
    for i in range(n):
        ya=HALF*i/n; yb=HALF*(i+1)/n
        k.box((0,(ya+yb)/2,RIDGE+0.1),(0.36,yb-ya+0.04,0.36),ROOF,rot=(0,math.pi/4,0),bevel=0.1,segs=2)
    # valley boards (dark wood strip under the crease reads as a painted valley)
    for sgn in(-1,1):
        L=math.hypot(HALF,HALF); 
        k.box((sgn*HALF/2,HALF/2,(RIDGE+0.35)/2+0.02),(0.12,L,0.05),WOOD,
              rot=(0,0,0),bevel=0,xform=Matrix.Translation((0,0,0)))
    # gable end on the outer -X side: reuse gable_end (built for wall line x=+1.5) rotated 180 and shifted
    g=Kit(); gable_end(g)
    merge_kit(k,g,Matrix.Translation((-1.5,0,0))@Matrix.Rotation(math.pi,4,"Z"))
'''
t.write(code); exec(t.as_string())
P=vcol("VK_Pieces")
k=Kit(); roof_gable(k); o=k.finish("SM_VK_Roof_Gable",P,wobble=False,grime=False); o.hide_viewport=o.hide_render=True
roof_variant(o,"_Blue","M_VK_RoofBlue").hide_render=True
print("gable ok", len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: gable ok 1875\n"}

# ==============================================================================================================
# [0094] 2026-09-23 02:12:46  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
a=s.index("    # valley boards"); b=s.index("    # gable end on the outer -X side")
s=s[:a]+s[b:]
code=r'''
def build_L_house(coll,origin,a,b,stories=2,roof="Red",frontA=None,frontB=None,chimney=None,upper="W"):
    """L-shaped house: junction square (2x2 cells) at origin, wing A extends +X by a cells, wing B extends +Y by b cells."""
    sfx={"Red":"","Blue":"_Blue","Green":"_Green"}[roof]
    gw={"D":"SM_VK_Wall_Stone_Door","W":"SM_VK_Wall_Stone_Window",".":"SM_VK_Wall_Stone"}
    uw={"W":"SM_VK_Wall_Timber_Window",".":"SM_VK_Wall_Timber"}
    XA=3+3*a; YB=3+3*b
    frontA=frontA or ("W"*(2+a)); frontB=frontB or ("W"*(2+b))
    runs=[]  # (x,y,rot,char) wall module centres
    for i in range(2+a): runs.append((-1.5+3*i,-3,0,frontA[i]))                 # A front (outer -Y)
    for j in range(2+b): runs.append((-3,-1.5+3*j,-90,frontB[j]))              # B outer side (-X)
    for j in range(2): runs.append((XA,-1.5+3*j,90,"W" if j==0 else "."))      # A end
    for i in range(a): runs.append((4.5+3*i,3,180,"."))                          # A back
    for i in range(2): runs.append((-1.5+3*i,YB,180,"W" if i==1 else "."))     # B end
    for j in range(b): runs.append((3,4.5+3*j,90,"W"))                           # B inner side
    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    for (x,y,r,c) in runs: place(coll,gw[c],x,y,0,r,origin)
    for (x,y,r) in corners: place(coll,"SM_VK_Corner_Stone",x,y,0,r,origin)
    top=H1
    if stories==2:
        for (x,y,r,c) in runs: place(coll,uw[upper if c!="." else "."],x,y,H1,r,origin)
        for (x,y,r) in corners: place(coll,"SM_VK_Corner_Timber",x,y,H1,r,origin)
        top=H1+H2
    place(coll,"SM_VK_Roof_LCorner"+sfx,0,0,top,0,origin)
    for i in range(a):
        x=4.5+3*i
        place(coll,("SM_VK_Roof_Gable" if i==a-1 else "SM_VK_Roof_Mid")+sfx,x,0,top,0,origin)
    for j in range(b):
        y=4.5+3*j
        place(coll,("SM_VK_Roof_Gable" if j==b-1 else "SM_VK_Roof_Mid")+sfx,0,y,top,90,origin)
    if chimney: place(coll,"SM_VK_Chimney",chimney[0],chimney[1],top,chimney[2],origin)
'''
t.clear(); t.write(s+code); exec(t.as_string())
P=vcol("VK_Pieces")
k=Kit(); roof_L_corner(k); o=k.finish("SM_VK_Roof_LCorner",P,wobble=False,grime=False); o.hide_viewport=o.hide_render=True
roof_variant(o,"_Blue","M_VK_RoofBlue").hide_render=True
print(len(o.data.polygons))
# test scene: hide demo, build an L house alone
for ob in vcol("VK_Demo").objects: ob.hide_render=True; ob.hide_viewport=True
T=vcol("VK_Test")
for ob in list(T.objects): bpy.data.objects.remove(ob)
build_L_house(T,(0,40,0),2,1,2,"Red",frontA="WDWW",frontB="W.W",chimney=(4.5,0,0))
cd=bpy.data.cameras.get("VK_CamT") or bpy.data.cameras.new("VK_CamT"); cd.lens=30
ct=bpy.data.objects.get("VK_CameraT") or bpy.data.objects.new("VK_CameraT",cd)
if ct.name not in SC.collection.objects: SC.collection.objects.link(ct)
tgt=Vector((2,43,3.5)); ct.location=tgt+Vector((-14,-17,13))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ct; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 2906\n"}

# ==============================================================================================================
# [0095] 2026-09-23 02:12:57  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; ct=bpy.data.objects["VK_CameraT"]
tgt=Vector((2,43,4.5)); ct.location=tgt+Vector((15,13,9))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0096] 2026-09-23 02:13:53  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("TILE={0:2.4,1:2.0,2:1.6,3:2.6,4:1.0,5:1.0}","TILE={0:3.0,1:1.5,2:1.6,3:3.0,4:1.0,5:1.0,10:1.6}")
s=s.replace('''        return (x/T,slope_dist(abs(y))/T) if region=="A" else (y/T,slope_dist(abs(x))/T)''',
'''        return ((x-1.5)/T,slope_dist(abs(y))/T) if region=="A" else ((y-1.5)/T,slope_dist(abs(x))/T)''')
# tinted texture materials + extended material list
s=s.replace("def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False):",
            "def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False,tint=None):")
s=s.replace('''        tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images[img]; nt.links.new(tx.outputs[0],mix.inputs[6])''',
'''        tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images[img]
        if tint:
            tm=nt.nodes.new("ShaderNodeMix"); tm.data_type="RGBA"; tm.blend_type="MULTIPLY"; tm.inputs[0].default_value=1
            tm.inputs[7].default_value=(*tint,1); nt.links.new(tx.outputs[0],tm.inputs[6]); nt.links.new(tm.outputs[2],mix.inputs[6])
        else: nt.links.new(tx.outputs[0],mix.inputs[6])''')
s=s.replace('''            tex_mat("M_VK_Leaf",None,0.8,flat=(0.18,0.42,0.10)), tex_mat("M_VK_Glow",None,0.5,flat=(1.0,0.75,0.35),emit=(1.0,0.62,0.25))]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW=range(10)''',
'''            tex_mat("M_VK_Leaf",None,0.8,flat=(0.18,0.42,0.10)), tex_mat("M_VK_Glow",None,0.5,flat=(1.0,0.75,0.35),emit=(1.0,0.62,0.25)),
            tex_mat("M_VK_Shutter_Teal","T_VK_Wood",0.8,tint=(0.55,1.25,1.25)),
            tex_mat("M_VK_Cloth_Red",None,0.9,flat=(0.62,0.10,0.08)), tex_mat("M_VK_Cloth_Cream",None,0.9,flat=(0.90,0.84,0.66)),
            tex_mat("M_VK_Apple",None,0.45,flat=(0.72,0.08,0.05)), tex_mat("M_VK_Pumpkin",None,0.6,flat=(0.90,0.45,0.08)),
            tex_mat("M_VK_Bread",None,0.8,flat=(0.72,0.48,0.22))]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD=range(16)
VARIANT_MATS={
 "plaster":{"Cream":None,"White":("T_VK_Plaster",(1.10,1.12,1.18)),"Ochre":("T_VK_Plaster",(1.05,0.86,0.58)),"Rose":("T_VK_Plaster",(1.05,0.84,0.78))},
 "shutter":{"Teal":None,"Red":("T_VK_Wood",(1.6,0.55,0.45)),"Green":("T_VK_Wood",(0.75,1.3,0.6)),"Blue":("T_VK_Wood",(0.6,0.8,1.6)),"Natural":("T_VK_Wood",(1,1,1))},
 "roof":{"Red":None,"Blue":("T_VK_RoofBlue",None),"Green":("T_VK_RoofGreen",None)},
 "cloth":{"Red":None,"Blue":(None,(0.12,0.22,0.55)),"Green":(None,(0.15,0.40,0.12)),"Yellow":(None,(0.85,0.62,0.12))},
}
SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A}
def variant_mat(kind,name):
    spec=VARIANT_MATS[kind][name]
    base={"plaster":"M_VK_Plaster","shutter":"M_VK_Shutter_Teal","roof":"M_VK_RoofRed","cloth":"M_VK_Cloth_Red"}[kind]
    if spec is None: return bpy.data.materials[base]
    img,tint=spec
    nm=f"M_VK_{kind.capitalize()}_{name}"
    if kind=="cloth": return tex_mat(nm,None,0.9,flat=tint)
    return tex_mat(nm,img,0.8,tint=tint)
_var_cache={}
def variant_mesh(piece,style):
    """mesh copy of a kit piece with materials swapped per style dict, cached"""
    src=bpy.data.objects[piece].data
    key=(piece,)+tuple(sorted((k_,v) for k_,v in style.items()))
    me=bpy.data.meshes.get("VAR_"+str(abs(hash(key))))
    if me: return me
    me=src.copy(); me.name="VAR_"+str(abs(hash(key)))
    for kind,name in style.items():
        slot=SLOT[kind]
        if slot<len(me.materials): me.materials[slot]=variant_mat(kind,name)
    return me''')
t.clear(); t.write(s)
# green mossy slate roof texture (same shingle generator, different palette + moss)
exec(s)
def tnoise(S,fmax,n,decay,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,fmax+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
S=1024
def roof(palette,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S
    nrow=8; ncol=6
    row=(y*nrow).astype(int); v=(y*nrow)%1
    xo=(x*ncol+0.5*(row%2))%ncol; c=xo.astype(int); u=xo%1
    bottom=1-0.28*(1-np.sqrt(np.clip(1-(2*u-1)**2,0,1))); inside=v<bottom
    tint=r.uniform(0.85,1.12,(nrow,ncol)); pick=r.integers(0,len(palette),(nrow,ncol))
    colr=np.array(palette)[pick[row,c]]*tint[row,c][...,None]
    row2=(row+1)%nrow; xo2=(x*ncol+0.5*(row2%2))%ncol; c2=xo2.astype(int)
    col2=np.array(palette)[pick[row2,c2]]*tint[row2,c2][...,None]
    lv=np.clip(v/bottom,0,1); sh=0.62+0.5*lv-0.25*np.clip((lv-0.85)/0.15,0,1)
    side=0.92+0.12*np.cos((u-0.35)*np.pi); edge=1-0.35*np.clip(1-(bottom-v)*40,0,1)
    colA=colr*(sh*side*edge)[...,None]
    shadow=0.45+0.25*np.clip((v-bottom)/(1-bottom+1e-4),0,1)
    col=np.where(inside[...,None],colA,col2*shadow[...,None]*0.8)
    gapm=np.clip(np.minimum(u,1-u)*S/ncol/3.0,0,1); col*=(0.55+0.45*gapm)[...,None]
    col*=(1+0.05*tnoise(S,30,100,0.5,seed+1)[...,None])
    return col
col=roof([(0.30,0.38,0.30),(0.26,0.34,0.28),(0.34,0.40,0.32),(0.24,0.30,0.27)],43)
moss=np.clip(tnoise(S,6,40,0.9,44)*1.4-0.2,0,1)[...,None]*np.clip(tnoise(S,30,80,0.5,45)+0.6,0,1)[...,None]
col=col*(1-moss*0.55)+np.array([0.38,0.50,0.14])*moss*0.55*(col.mean(2,keepdims=True)*2.2)
img=bpy.data.images.get("T_VK_RoofGreen")
if img: bpy.data.images.remove(img)
img=bpy.data.images.new("T_VK_RoofGreen",S,S,alpha=True)
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
img.filepath_raw=os.path.join(out,"VillageKit","Textures","T_VK_RoofGreen.png"); img.file_format="PNG"; img.save()
kit_mats()
for kind in VARIANT_MATS:
    for nm in VARIANT_MATS[kind]: variant_mat(kind,nm)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0097] 2026-09-23 02:15:01  blender  ERROR
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
# shutters use the paintable SHUTTER slot
s=s.replace('''    for i in range(3): put((-side*(0.1+i*0.185),-0.03,z0+h/2),(0.17,0.05,h),WOOD)
    for zz in (z0+0.2,z0+h-0.2): put((-side*w/2,-0.07,zz),(w-0.04,0.04,0.1),WOOD)''',
'''    for i in range(3): put((-side*(0.1+i*0.185),-0.03,z0+h/2),(0.17,0.05,h),SHUTTER)
    for zz in (z0+0.2,z0+h-0.2): put((-side*w/2,-0.07,zz),(w-0.04,0.04,0.1),SHUTTER)''')
s=s.replace("def timber_frame(k,window=False):","def timber_frame(k,window=False,pattern='V'):")
s=s.replace('''    if not window:
        k.box((0,-0.33,H2/2),(0.22,0.2,H2-0.4),WOOD,bevel=0.03)
        for s in(-1,1):''','''    if not window and pattern!="V":
        braces_pattern(k,pattern)
    elif not window:
        k.box((0,-0.33,H2/2),(0.22,0.2,H2-0.4),WOOD,bevel=0.03)
        for s in(-1,1):''')
code=r'''
def brace(k,x0,z0,x1,z1,w=0.17,y=-0.33):
    L=math.hypot(x1-x0,z1-z0); ang=math.atan2(z1-z0,x1-x0)
    k.box(((x0+x1)/2,y,(z0+z1)/2),(L,0.18,w),WOOD,rot=(0,-ang,0),bevel=0.03)
def braces_pattern(k,pattern):
    zb,zt=0.3,H2-0.21
    if pattern=="X":
        k.box((0,-0.33,H2/2),(0.22,0.2,H2-0.4),WOOD,bevel=0.03)
        for s_ in(-1,1):
            brace(k,s_*1.35,zb+0.05,s_*0.12,zt-0.05); brace(k,s_*1.35,zt-0.05,s_*0.12,zb+0.05,y=-0.335)
    elif pattern=="K":
        for x in(-0.75,0,0.75): k.box((x,-0.33,H2/2),(0.2,0.2,H2-0.4),WOOD,bevel=0.03)
        k.box((0,-0.33,1.25),(CELL,0.18,0.16),WOOD,bevel=0.03)
        for x0 in(-1.5,-0.75,0,0.75):
            brace(k,x0+0.1,zt-0.45,x0+0.35,zt-0.05,w=0.13)
            brace(k,x0+0.65,zt-0.45,x0+0.4,zt-0.05,w=0.13)
            brace(k,x0+0.1,0.35,x0+0.65,1.18,w=0.14)
# ---------------- plaster ground floor (cheaper houses): stone plinth + timber frame + plaster
PL=0.75
def plaster_ground(k,kind="."):
    stone_panel(k,-1.5,1.5,0,PL,-0.28,0.25); plinth(k); batter(k,0.05)
    k.box((0,-0.2,PL+0.1),(CELL,0.4,0.2),WOOD,bevel=0.035)
    k.box((0,-0.2,H1-0.11),(CELL,0.4,0.22),WOOD,bevel=0.035)
    k.box((-1.5,-0.24,(PL+H1)/2),(0.24,0.2,H1-PL-0.2),WOOD,bevel=0.03)
    if kind==".":
        grid_cut(k,k.box((0,-0.02,(PL+H1)/2),(CELL,0.44,H1-PL),PLASTER,bevel=0))
        k.box((0,-0.24,(PL+H1)/2),(0.22,0.2,H1-PL-0.2),WOOD,bevel=0.03)
        for s_ in(-1,1): brace(k,s_*1.35,PL+0.25,s_*0.15,H1-0.3,y=-0.24)
    elif kind=="W":
        x0,x1,z0,z1=-0.55,0.55,1.1,2.25
        for (a,b,c,d) in ((-1.5,x0,PL,H1),(x1,1.5,PL,H1),(x0,x1,PL,z0),(x0,x1,z1,H1)):
            grid_cut(k,k.box(((a+b)/2,-0.02,(c+d)/2),(b-a,0.44,d-c),PLASTER,bevel=0))
        window_frame(k,x0,x1,z0,z1,depth_y=0.0,sill=False,face=-0.2)
        k.box((0,-0.3,z0-0.08),(1.5,0.3,0.16),WOOD,bevel=0.03)
        for s_ in(-1,1): k.box((s_*0.85,-0.24,(PL+H1)/2),(0.2,0.2,H1-PL-0.2),WOOD,bevel=0.03)
    elif kind=="D":
        hw=0.62; top=2.3
        for (a,b,c,d) in ((-1.5,-hw,PL,H1),(hw,1.5,PL,H1),(-hw,hw,top,H1)):
            grid_cut(k,k.box(((a+b)/2,-0.02,(c+d)/2),(b-a,0.44,d-c),PLASTER,bevel=0))
        # cut the plinth for the door
        for v in [v for v in k.bm.verts]: pass
        for s_ in(-1,1): k.box((s_*(hw+0.11),-0.24,top/2),(0.22,0.24,top),WOOD,bevel=0.035)
        k.box((0,-0.26,top+0.12),(2*hw+0.6,0.3,0.26),WOOD,bevel=0.04)
        for i in range(4):
            x=-hw+(i+0.5)*(2*hw)/4
            k.box((x,0.0,top/2),((2*hw)/4-0.015,0.1,top),WOOD,bevel=0.012)
        for zz in(0.5,1.7): k.box((0,-0.06,zz),(2*hw-0.1,0.03,0.1),IRON,bevel=0.01)
        k.box((0.35,-0.08,1.05),(0.06,0.06,0.16),IRON,bevel=0.01)
        k.box((0,-0.5,0.1),(1.5,0.55,0.2),STONE,bevel=0.05,segs=2,jitter=0.02,seed=5)
def corner_plaster(k):
    k.box((-0.05,-0.05,PL/2),(0.8,0.8,PL),STONE,bevel=0.05,segs=2,jitter=0.02,seed=2)
    k.box((-0.22,-0.22,(PL+H1)/2),(0.34,0.34,H1-PL),WOOD,bevel=0.05,segs=2)
    k.box((-0.1,-0.1,H1-0.11),(0.56,0.56,0.22),WOOD,bevel=0.04)
# ---------------- market stall (2 x 1 cells footprint, front toward -Y)
def market_stall(k,goods=("APPLE","PUMPKIN","BREAD")):
    W_,D_=3.2,1.8
    for sx in(-1,1):
        for sy in(-1,1):
            h=2.6 if sy<0 else 3.0
            k.box((sx*(W_/2-0.1),sy*(D_/2-0.1),h/2),(0.2,0.2,h),WOOD,bevel=0.05,segs=2)
    # counter
    k.box((0,-0.35,0.95),(W_,1.0,0.14),WOOD,bevel=0.04)
    for i in range(6): k.box((-W_/2+0.27+i*0.53,-0.84,0.47),(0.5,0.08,0.9),WOOD,bevel=0.02)
    k.box((0,-0.35,0.12),(W_-0.2,0.9,0.1),WOOD,bevel=0.02)
    # back shelf & crossbeams
    k.box((0,D_/2-0.25,1.45),(W_-0.2,0.45,0.08),WOOD,bevel=0.02)
    for sy,h in((-1,2.6),(1,3.0)): k.box((0,sy*(D_/2-0.1),h-0.1),(W_+0.1,0.16,0.18),WOOD,bevel=0.03)
    # striped awning: sagging cloth sloping from back (3.1) to front (2.55) and over the front
    nx=12; ny=6; x0=-W_/2-0.25; x1=W_/2+0.25; y0=-D_/2-0.75; y1=D_/2+0.05
    grid=[]
    for i in range(nx+1):
        row=[]
        for j in range(ny+1):
            x=x0+(x1-x0)*i/nx; y=y0+(y1-y0)*j/ny
            z=2.65+(y-y0)/(y1-y0)*0.5 - 0.12*math.sin(math.pi*(i/nx*2%1 if False else (i%3)/3))*0 - 0.10*math.sin(math.pi*j/ny)
            z-=0.06*(0.5-0.5*math.cos(2*math.pi*i/(nx/2)))
            row.append(k.bm.verts.new((x,y,z)))
        grid.append(row)
    for i in range(nx):
        mi=CLOTH_A if (i//2)%2==0 else CLOTH_B
        for j in range(ny):
            f=k.bm.faces.new((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1])); f.material_index=mi
            f2=k.bm.faces.new((grid[i][j+1],grid[i+1][j+1],grid[i+1][j],grid[i][j])); f2.material_index=mi
    # scalloped valance hanging from the front edge
    for i in range(nx):
        mi=CLOTH_A if (i//2)%2==0 else CLOTH_B
        a=grid[i][0].co; b=grid[i+1][0].co
        m=(a+b)/2+Vector((0,0,-0.42))
        va=[k.bm.verts.new(a),k.bm.verts.new(b),k.bm.verts.new(b+Vector((0,0,-0.28))),k.bm.verts.new(m),k.bm.verts.new(a+Vector((0,0,-0.28)))]
        for vv in (va,va[::-1]):
            f=k.bm.faces.new(vv); f.material_index=mi
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index in (CLOTH_A,CLOTH_B):
            for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    # goods: crates with produce on the counter
    rnd=random.Random(3)
    mats={"APPLE":APPLE,"PUMPKIN":PUMPKIN,"BREAD":BREAD}
    for ci,(cx,g) in enumerate(zip((-1.0,0.0,1.0),goods)):
        k.box((cx,-0.45,1.15),(0.85,0.62,0.26),WOOD,bevel=0.03)
        for n_ in range(9 if g=="APPLE" else (4 if g=="PUMPKIN" else 6)):
            if g=="APPLE":
                r_=0.09; x=cx-0.28+(n_%3)*0.28; y=-0.62+(n_//3)*0.17; z=1.33
                vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=r_)["verts"]
                for v in vs: v.co+=Vector((x+rnd.uniform(-.03,.03),y,z+rnd.uniform(0,.03)))
            elif g=="PUMPKIN":
                r_=0.19; x=cx-0.2+(n_%2)*0.4; y=-0.58+(n_//2)*0.3; z=1.42
                vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=r_)["verts"]
                for v in vs:
                    ang=math.atan2(v.co.y,v.co.x); v.co.z*=0.72; v.co*= (1+0.06*math.cos(8*ang)); v.co+=Vector((x,y,z))
            else:
                x=cx-0.25+(n_%3)*0.25; y=-0.58+(n_//3)*0.25; z=1.36
                vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.14)["verts"]
                for v in vs: v.co=Vector((v.co.x*0.9,v.co.y*1.4,v.co.z*0.6))+Vector((x,y,z))
            for f in {f for v in vs for f in v.link_faces}: f.material_index=mats[g]; f.smooth=True
    # barrels, baskets and a sack beside the stall
    for (x,y) in ((W_/2+0.55,-0.2),(W_/2+0.5,0.55)):
        for zz,(r0,r1) in ((0.25,(0.34,0.4)),(0.75,(0.4,0.34))):
            cyl_=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=12,radius1=r0,radius2=r1,depth=0.5)["verts"]
            for v in cyl_: v.co+=Vector((x,y,zz))
            fs={f for v in cyl_ for f in v.link_faces}
            k.project(fs,WOOD)
        for zz in(0.12,0.88):
            cyl_=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=12,radius1=0.39,radius2=0.39,depth=0.06)["verts"]
            for v in cyl_: v.co+=Vector((x,y,zz))
            for f in {f for v in cyl_ for f in v.link_faces}: f.material_index=IRON
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.32)["verts"]
    for v in vs: v.co=Vector((v.co.x,v.co.y*0.85,v.co.z*1.2))+Vector((-W_/2-0.45,-0.4,0.35))
    for f in {f for v in vs for f in v.link_faces}: f.material_index=CLOTH_B
    # hanging price sign
    k.box((-W_/2+0.35,-D_/2-0.12,2.2),(0.7,0.06,0.4),WOOD,bevel=0.03)
    for sx in(-0.2,0.2): k.box((-W_/2+0.35+sx,-D_/2-0.12,2.45),(0.02,0.02,0.2),IRON,bevel=0)
    k.box((-W_/2+0.35,-D_/2-0.16,2.2),(0.35,0.02,0.15),YELLOW,bevel=0)
# ---------------- one call rebuilds the whole kit
def rebuild_all():
    P=vcol("VK_Pieces")
    specs=[("SM_VK_Wall_Stone",wall_stone_plain,{}),("SM_VK_Wall_Stone_Window",wall_stone_window,{}),("SM_VK_Wall_Stone_Door",wall_stone_door,{}),
           ("SM_VK_Corner_Stone",corner_stone,{"wobble":False}),
           ("SM_VK_Wall_Plaster",lambda k: plaster_ground(k,"."),{}),("SM_VK_Wall_Plaster_Window",lambda k: plaster_ground(k,"W"),{}),
           ("SM_VK_Wall_Plaster_Door",lambda k: plaster_ground(k,"D"),{}),("SM_VK_Corner_Plaster",corner_plaster,{"wobble":False}),
           ("SM_VK_Wall_Timber",timber_frame,{"grime":False}),("SM_VK_Wall_Timber_X",lambda k: timber_frame(k,False,"X"),{"grime":False}),
           ("SM_VK_Wall_Timber_K",lambda k: timber_frame(k,False,"K"),{"grime":False}),
           ("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),{"grime":False}),
           ("SM_VK_Corner_Timber",corner_timber,{"wobble":False,"grime":False}),
           ("SM_VK_Roof_Mid",roof_mid,{"wobble":False,"grime":False}),("SM_VK_Roof_Gable",roof_gable,{"wobble":False,"grime":False}),
           ("SM_VK_Roof_LCorner",roof_L_corner,{"wobble":False,"grime":False}),("SM_VK_Chimney",chimney,{"wobble":False,"grime":False}),
           ("SM_VK_Prop_FlowerBox",prop_flowerbox,{"wobble":False,"grime":False}),("SM_VK_Prop_Lantern",prop_lantern,{"wobble":False,"grime":False}),
           ("SM_VK_Prop_Sign",prop_sign,{"wobble":False,"grime":False}),("SM_VK_MarketStall",market_stall,{"wobble":False,"grime":True})]
    for n,fn,kw in specs:
        k=Kit(); fn(k); o=k.finish(n,P,**kw); o.hide_render=True; o.hide_viewport=True
    for n in list(bpy.data.objects):
        if n.name.endswith(("_Blue","_Green")) and n.name.startswith("SM_VK_Roof"): bpy.data.objects.remove(n)
    for me in list(bpy.data.meshes):
        if me.name.startswith("VAR_") and me.users==0: bpy.data.meshes.remove(me)
    _var_cache.clear()
    return [n for n,_,_ in specs]
'''
t.clear(); t.write(s+code); exec(t.as_string())
names=rebuild_all()
for n in names: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: faces.new(verts): face already exists"}

# ==============================================================================================================
# [0098] 2026-09-23 02:15:14  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''            f=k.bm.faces.new((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1])); f.material_index=mi
            f2=k.bm.faces.new((grid[i][j+1],grid[i+1][j+1],grid[i+1][j],grid[i][j])); f2.material_index=mi''',
'''            f=k.bm.faces.new((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1])); f.material_index=mi
            f2=k.bm.faces.new((under[i][j+1],under[i+1][j+1],under[i+1][j],under[i][j])); f2.material_index=mi''')
s=s.replace('''        grid.append(row)
    for i in range(nx):
        mi=CLOTH_A''','''        grid.append(row)
    under=[[k.bm.verts.new(v.co+Vector((0,0,-0.015))) for v in row] for row in grid]
    for i in range(nx):
        mi=CLOTH_A''',1)
s=s.replace('''        for vv in (va,va[::-1]):
            f=k.bm.faces.new(vv); f.material_index=mi''','''        f=k.bm.faces.new(va); f.material_index=mi
        vb=[k.bm.verts.new(v.co+Vector((0,0.015,0))) for v in va]
        f=k.bm.faces.new(vb[::-1]); f.material_index=mi''')
t.clear(); t.write(s); exec(s)
names=rebuild_all()
for n in names: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Stone 102\nSM_VK_Wall_Stone_Window 611\nSM_VK_Wall_Stone_Door 1348\nSM_VK_Corner_Stone 384\nSM_VK_Wa
# ll_Plaster 284\nSM_VK_Wall_Plaster_Window 769\nSM_VK_Wall_Plaster_Door 534\nSM_VK_Corner_Plaster 134\nSM_VK_Wall_Timber 434\nSM_VK_Wall_Timber_X 460\n
# SM_VK_Wall_Timber_K 746\nSM_VK_Wall_Timber_Window 607\nSM_VK_Corner_Timber 158\nSM_VK_Roof_Mid 408\nSM_VK_Roof_Gable 1875\nSM_VK_Roof_LCorner 2906\nSM
# _VK_Chimney 242\nSM_VK_Prop_FlowerBox 714\nSM_VK_Prop_Lantern 186\nSM_VK_Prop_Sign 150\nSM_VK_MarketStall 2504\n"}

# ==============================================================================================================
# [0099] 2026-09-23 02:15:53  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def place_v(coll,piece,x,y,z,rot_deg,origin,style):
    o=place(coll,piece,x,y,z,rot_deg,origin)
    st={k_:v for k_,v in style.items() if k_ in SLOT}
    if st: o.data=variant_mesh(piece,st)
    return o
def random_style(seed):
    r=random.Random(seed)
    return {"ground":r.choices(["Stone","Plaster"],[0.6,0.4])[0],
            "plaster":r.choice(["Cream","White","Ochre","Rose","Cream"]),
            "shutter":r.choice(["Teal","Red","Green","Blue","Natural"]),
            "roof":r.choice(["Red","Blue","Green","Red"]),"seed":seed}
def _pieces(style):
    g=style.get("ground","Stone")
    gw={"D":f"SM_VK_Wall_{g}_Door","W":f"SM_VK_Wall_{g}_Window",".":f"SM_VK_Wall_{g}"}
    gc=f"SM_VK_Corner_{g}"
    return gw,gc
def _upper(r,c):
    if c=="W": return "SM_VK_Wall_Timber_Window"
    return r.choice(["SM_VK_Wall_Timber","SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K"])
def _dress(coll,origin,x,y,rot,c,r,style,z0=0):
    # props in wall-local coordinates, rotated with the wall
    a=math.radians(rot); ca,sa=math.cos(a),math.sin(a)
    def loc(lx,ly): return (x+lx*ca-ly*sa,y+lx*sa+ly*ca)
    if c=="W" and r.random()<0.7:
        px,py=loc(0,-0.55 if style.get("ground")=="Stone" else -0.5)
        place_v(coll,"SM_VK_Prop_FlowerBox",px,py,0.78 if style.get("ground")=="Stone" else 0.9,rot,origin,{})
    if c=="D":
        px,py=loc(1.0,-0.3); place_v(coll,"SM_VK_Prop_Lantern",px,py,2.55,rot,origin,{})
def build_house_v(coll,origin,n,stories,style,front=None,back=None,chimney=True):
    r=random.Random(style["seed"]); gw,gc=_pieces(style); L=n*CELL
    front=front or "".join(r.choice("WW.") for _ in range(n))
    if "D" not in front: i=r.randrange(n); front=front[:i]+"D"+front[i+1:]
    back=back or "".join(r.choice("W..") for _ in range(n))
    walls=[(-L/2+1.5+3*i,-3,0,front[i]) for i in range(n)]+[(-L/2+1.5+3*i,3,180,back[::-1][i]) for i in range(n)]
    walls+=[(-L/2,-1.5,-90,r.choice("W.")),(-L/2,1.5,-90,"."),(L/2,1.5,90,r.choice("W.")),(L/2,-1.5,90,".")]
    corners=[(-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)]
    _assemble(coll,origin,walls,corners,stories,style,r)
    top=H1+(H2 if stories==2 else 0); sfx=""
    for i in range(n):
        x=-L/2+1.5+3*i
        pc="SM_VK_Roof_Gable" if i in (0,n-1) else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)
    if chimney:
        place_v(coll,"SM_VK_Chimney",-L/2+1.5+3*r.randrange(n),0,top,r.choice((0,180)),origin,style)
def _assemble(coll,origin,walls,corners,stories,style,r):
    gw,gc=_pieces(style)
    for (x,y,rot,c) in walls:
        place_v(coll,gw[c],x,y,0,rot,origin,style); _dress(coll,origin,x,y,rot,c,r,style)
    for (x,y,rot) in corners: place_v(coll,gc,x,y,0,rot,origin,style)
    if stories==2:
        for (x,y,rot,c) in walls:
            uc="W" if (c in "WD" or r.random()<0.35) else "."
            place_v(coll,_upper(r,uc),x,y,H1,rot,origin,style)
        for (x,y,rot) in corners: place_v(coll,"SM_VK_Corner_Timber",x,y,H1,rot,origin,style)
def build_L_v(coll,origin,a,b,stories,style):
    r=random.Random(style["seed"]); XA=3+3*a; YB=3+3*b
    fa="".join(r.choice("WW.") for _ in range(2+a)); fa=fa[:1]+"D"+fa[2:]
    walls=[(-1.5+3*i,-3,0,fa[i]) for i in range(2+a)]
    walls+=[(-3,-1.5+3*j,-90,r.choice("W.")) for j in range(2+b)]
    walls+=[(XA,-1.5,90,r.choice("W.")),(XA,1.5,90,".")]
    walls+=[(4.5+3*i,3,180,r.choice("W.")) for i in range(a)]
    walls+=[(-1.5,YB,180,"."),(1.5,YB,180,r.choice("W."))]
    walls+=[(3,4.5+3*j,90,r.choice("WD")) for j in range(b)]
    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    _assemble(coll,origin,walls,corners,stories,style,r)
    top=H1+(H2 if stories==2 else 0)
    place_v(coll,"SM_VK_Roof_LCorner",0,0,top,0,origin,style)
    for i in range(a): place_v(coll,"SM_VK_Roof_Gable" if i==a-1 else "SM_VK_Roof_Mid",4.5+3*i,0,top,0,origin,style)
    for j in range(b): place_v(coll,"SM_VK_Roof_Gable" if j==b-1 else "SM_VK_Roof_Mid",0,4.5+3*j,top,90,origin,style)
    place_v(coll,"SM_VK_Chimney",4.5+3*r.randrange(a),0,top,r.choice((0,180)),origin,style)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
# clear old demo/test
for cname in ("VK_Demo","VK_Test"):
    for o in list(vcol(cname).objects): bpy.data.objects.remove(o)
D=vcol("VK_Demo")
R=math.radians
plan=[ # (kind, origin, params, seed)
 ("S",(-9,15,0),(3,2),11),("S",(3,15.5,0),(2,1),12),
 ("L",(13,10,0),(2,1),13),
 ("S",(-18,1,R(90)),(3,2),14),
 ("L",(-13,-11,R(180)),(1,2),15),
 ("S",(0,-15,R(180)),(3,2),16),("S",(11,-15.5,R(180)),(2,2),17),
 ("S",(19,-3,R(-90)),(2,1),18),
]
for kind,org,prm,seed in plan:
    st=random_style(seed)
    if kind=="S": build_house_v(D,org,prm[0],prm[1],st)
    else: build_L_v(D,org,prm[0],prm[1],2,st)
    print(kind,seed,st)
print(len(D.objects))
# ---- result ----
# {"result":"Code executed successfully: S 11 {'ground': 'Stone', 'plaster': 'Cream', 'shutter': 'Blue', 'roof': 'Red', 'seed': 11}\nS 12 {'ground': 'St
# one', 'plaster': 'Cream', 'shutter': 'Green', 'roof': 'Blue', 'seed': 12}\nL 13 {'ground': 'Stone', 'plaster': 'White', 'shutter': 'Red', 'roof': 'Blu
# e', 'seed': 13}\nS 14 {'ground': 'Stone', 'plaster': 'Cream', 'shutter': 'Red', 'roof': 'Green', 'seed': 14}\nL 15 {'ground': 'Plaster', 'plaster': 'C
# ream', 'shutter': 'Natural', 'roof': 'Red', 'seed': 15}\nS 16 {'ground': 'Stone', 'plaster': 'Rose', 'shutter': 'Green', 'roof': 'Red', 'seed': 16}\nS
#  17 {'ground': 'Stone', 'plaster': 'Ochre', 'shutter': 'Green', 'roof': 'Green', 'seed': 17}\nS 18 {'ground': 'Stone', 'plaster': 'Rose', 'shutter': '
# Green', 'roof': 'Blue', 'seed': 18}\n269\n"}

# ==============================================================================================================
# [0100] 2026-09-23 02:16:22  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
D=vcol("VK_Demo")
for o in list(D.objects): bpy.data.objects.remove(o)
R=math.radians
plan=[("S",(-9,15,0),(3,2),11,{}),("S",(3,15.5,0),(2,1),12,{"ground":"Plaster","plaster":"Ochre"}),
      ("L",(13,10,0),(2,1),13,{}),("S",(-18,1,R(90)),(3,2),14,{}),
      ("L",(-13,-11,R(180)),(1,2),15,{"roof":"Blue","plaster":"White"}),
      ("S",(0,-15,R(180)),(3,2),16,{}),("S",(11,-15.5,R(180)),(2,2),17,{"ground":"Plaster"}),
      ("S",(19,-3,R(-90)),(2,1),18,{"ground":"Plaster","roof":"Red"})]
for kind,org,prm,seed,ov in plan:
    st=random_style(seed); st.update(ov)
    if kind=="S": build_house_v(D,org,prm[0],prm[1],st)
    else: build_L_v(D,org,prm[0],prm[1],2,st)
# market stalls
for i,(x,y,rot,cl) in enumerate([(-4,3.5,0,"Red"),(1.5,4,8,"Blue"),(-3.5,-4.5,180,"Yellow"),(3,-5,172,"Green")]):
    place_v(D,"SM_VK_MarketStall",x,y,0,rot,(0,0,0),{"cloth":cl})
# plaza ground: irregular dirt patch
bm=bmesh.new(); n=40; rnd=random.Random(2)
c=bm.verts.new((1,0,0.015)); ring=[]
for i in range(n):
    a=2*math.pi*i/n; rr=1+0.08*math.sin(3*a)+0.05*rnd.uniform(-1,1)
    ring.append(bm.verts.new((1+math.cos(a)*14.5*rr,math.sin(a)*11.5*rr,0.015)))
for i in range(n): bm.faces.new((c,ring[i],ring[(i+1)%n]))
me=bpy.data.meshes.new("VK_Plaza"); bm.to_mesh(me); bm.free()
pl=bpy.data.objects.new("VK_Plaza",me); D.objects.link(pl); me.materials.append(bpy.data.materials["MC_WK_Dirt"])
# trees
tw=bpy.data.objects["SM_Tree_Wood"].data; tf=bpy.data.objects["SM_Tree_Foliage"].data
for i,(x,y,s_,r_) in enumerate([(-22,14,1.0,0.3),(-26,-6,1.1,2.0),(25,12,0.9,4.0),(24,-14,1.05,1.1),(-3,24,0.95,5.2),(18,22,1.1,2.4),(-24,-19,0.9,0.8)]):
    for d,nm in ((tw,"W"),(tf,"F")):
        o=bpy.data.objects.new(f"VK_Tree{i}{nm}",d); D.objects.link(o); o.location=(x,y,0); o.scale=(s_,s_,s_); o.rotation_euler.z=r_
bpy.data.objects["VK_Ground"].scale=(3,3,1)
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=28
tgt=Vector((1,0,1.5)); cam.location=Vector((-6,-38,27))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0101] 2026-09-23 02:16:41  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=100
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=30
tgt=Vector((1,1,0)); cam.location=Vector((24,-30,40))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam; SC.render.filepath=os.path.join(out,"village_plaza.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# street-level market shot
cc=bpy.data.objects["VK_CameraClose"]; cc.data.lens=30
tgt=Vector((-1,6,2.4)); cc.location=Vector((6.5,-7.5,2.3))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.filepath=os.path.join(out,"village_market.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
SC.camera=cam
for f in ("_vk_test.png",):
    p=os.path.join(out,f)
    if os.path.exists(p): os.remove(p)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0102] 2026-09-23 02:17:07  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("        for p in me.polygons: p.use_smooth=False\n        old=bpy.data.objects.get(name)",
"        for p in me.polygons: p.use_smooth=p.material_index in (APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF)\n        old=bpy.data.objects.get(name)")
t.clear(); t.write(s); exec(s)
P=vcol("VK_Pieces")
k=Kit(); market_stall(k); o=k.finish("SM_VK_MarketStall",P,wobble=False,grime=True); o.hide_render=o.hide_viewport=True
for me in list(bpy.data.meshes):
    if me.name.startswith("VAR_") and "SM_VK_MarketStall" in [ob.name.split("_inst")[0] for ob in bpy.data.objects if ob.data==me]:
        pass
# refresh stall variants
for ob in vcol("VK_Demo").objects:
    if ob.name.startswith("SM_VK_MarketStall"):
        cl=ob.data.materials[CLOTH_A].name.replace("M_VK_Cloth_","")
        cl="Red" if cl=="Red" else cl
        old=ob.data; me=o.data.copy(); me.materials[CLOTH_A]=variant_mat("cloth",cl); ob.data=me
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cc=bpy.data.objects["VK_CameraClose"]; cc.data.lens=32
tgt=Vector((-1,1.5,1.6)); cc.location=Vector((9,-10,3.6))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.filepath=os.path.join(out,"village_market.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
SC.camera=bpy.data.objects["VK_Camera"]
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0103] 2026-09-23 02:17:21  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
for ob in SC.objects:
    if ob.name.startswith("SM_VK_MarketStall") and abs(ob.rotation_euler.z)>1.5: ob.hide_render=True
cc=bpy.data.objects["VK_CameraClose"]; cc.data.lens=35
tgt=Vector((-1.2,3.8,1.7)); cc.location=Vector((3.5,-6.5,3.2))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.filepath=os.path.join(out,"village_market.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for ob in SC.objects:
    if ob.name.startswith("SM_VK_MarketStall"): ob.hide_render=False
SC.camera=bpy.data.objects["VK_Camera"]
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0104] 2026-09-23 02:51:17  blender  ok
# ==============================================================================================================
import bpy
print(bpy.data.filepath, bpy.data.is_dirty)
# ---- result ----
# {"result":"Code executed successfully: E:\\Unity\\Projects\\Cube Sorter\\Art\\WallKit\\medievalDiorama.blend False\n"}

# ==============================================================================================================
# [0105] 2026-09-23 02:51:29  blender  ok
# ==============================================================================================================
import bpy
n=0
for img in bpy.data.images:
    if img.source=="FILE" and not img.packed_file and img.has_data:
        try: img.pack(); n+=1
        except Exception as e: print(img.name,e)
bpy.ops.wm.save_mainfile()
print("packed",n,"saved",bpy.data.filepath,bpy.data.is_dirty)
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\npacked 10 saved E:\\Unity\\Projects\\Cube Sorter\\Art\\WallKit\\medieval
# Diorama.blend False\n"}

# ==============================================================================================================
# [0106] 2026-09-23 02:52:20  blender  ok
# ==============================================================================================================
import bpy
code=r'''
# ---------------- inner (concave) corners: concave quadrant is local +X +Y
def inner_corner_stone(k):
    rnd=random.Random(8); z=0.4; i=0
    k.box((0.32,0.32,0.2),(0.3,0.3,0.4),STONE,bevel=0.04)
    while z<H1-0.05:
        h=min(rnd.uniform(0.38,0.5),H1-z)
        if i%2==0: k.box((0.55,0.3,z+h/2),(0.6,0.14,h-0.03),STONE,bevel=0.05,segs=2,jitter=0.01,seed=i)
        else:      k.box((0.3,0.55,z+h/2),(0.14,0.6,h-0.03),STONE,bevel=0.05,segs=2,jitter=0.01,seed=i)
        z+=h; i+=1
def inner_corner_plaster(k):
    k.box((0.35,0.35,PL/2),(0.3,0.3,PL),STONE,bevel=0.04)
    k.box((0.28,0.28,(PL+H1)/2),(0.24,0.24,H1-PL),WOOD,bevel=0.04)
def inner_corner_timber(k):
    k.box((0.44,0.44,H2/2),(0.26,0.26,H2),WOOD,bevel=0.05,segs=2)
    k.box((0.3,0.3,0.15),(0.4,0.4,0.3),WOOD,bevel=0.04)
# ---------------- dormer: sits on a Roof_Mid, front slope (-Y)
def dormer(k):
    zr=lambda ay: roof_z(ay)
    yf=-2.35; hw=0.85
    # cheek walls + front wall (plaster, timber framed)
    k.box((0,(yf-0.4)/2,1.8),(2*hw,-(yf)-0.4+0.0,1.6),PLASTER,bevel=0)   # body y yf..-0.4
    zb=zr(-yf)-0.15; zt=2.75
    k.quad([(-hw+0.2,yf-0.02,zb+0.3),(hw-0.2,yf-0.02,zb+0.3),(hw-0.2,yf-0.02,zt-0.25),(-hw+0.2,yf-0.02,zt-0.25)],WINDOW,
           uvs=[(0,0),(1.3,0),(1.3,1.1),(0,1.1)])
    for sx in(-1,1): k.box((sx*(hw-0.1),yf-0.06,(zb+zt)/2),(0.2,0.2,zt-zb+0.1),WOOD,bevel=0.035)
    k.box((0,yf-0.06,zb+0.2),(2*hw,0.22,0.18),WOOD,bevel=0.03)
    k.box((0,yf-0.08,zt-0.12),(2*hw+0.1,0.24,0.2),WOOD,bevel=0.03)
    k.box((0,yf-0.1,(zb+zt)/2+0.15),(0.07,0.05,zt-zb-0.5),WOOD,bevel=0.01)
    # small gable roof along Y
    rp=math.radians(45); run=hw+0.3; rise=run*math.tan(rp)*0.8
    zr0=zt+0.02
    for sx in(-1,1):
        L=math.hypot(run,rise); ang=math.atan2(rise,run)
        k.box((sx*run/2,(yf-0.35-0.2)/2-0.4,zr0+rise/2),(L+0.1,-yf+0.45,0.16),ROOF,rot=(0,sx*ang,0),bevel=0.04)
    # gable triangle
    vs=[k.bm.verts.new(p) for p in ((-run+0.15,yf-0.05,zr0),(run-0.15,yf-0.05,zr0),(0,yf-0.05,zr0+rise-0.1))]
    f=k.bm.faces.new(vs[::-1]); f.material_index=PLASTER; k.bm.normal_update(); k.project([f],PLASTER)
    k.box((0,yf-0.4,zr0+rise*0.45),(0.12,0.12,rise*0.8),WOOD,bevel=0.02)
    for sx in(-1,1):
        L=math.hypot(run,rise); ang=math.atan2(rise,run)
        k.box((sx*run/2,yf-0.44,zr0+rise/2-0.05),(L+0.12,0.12,0.24),WOOD,rot=(0,sx*ang,0),bevel=0.03)
    k.box((0,yf-0.47,zr0+rise+0.08),(0.14,0.14,0.45),WOOD,bevel=0.04)
# ---------------- porch canopy over a door (wall-local, outer side -Y)
def porch(k):
    W_=2.6; yo=-1.75; zh=2.95; zl=2.35
    for sx in(-1,1):
        k.box((sx*(W_/2-0.2),yo+0.1,zl/2),(0.2,0.2,zl),WOOD,bevel=0.04,segs=2)
        k.box((sx*(W_/2-0.2),yo+0.1,0.06),(0.34,0.34,0.12),STONE,bevel=0.03)
        # knee braces
        k.box((sx*(W_/2-0.45),yo+0.1,zl-0.3),(0.5,0.14,0.13),WOOD,rot=(0,sx*0.7,0),bevel=0.02)
        L=math.hypot(-yo,zh-zl); ang=math.atan2(zh-zl,-yo)
        k.box((sx*(W_/2-0.2),yo/2,(zh+zl)/2+0.02),(0.16,L,0.2),WOOD,rot=(ang,0,0),bevel=0.03)
    k.box((0,yo+0.1,zl+0.05),(W_,0.2,0.22),WOOD,bevel=0.04)
    L=math.hypot(-yo+0.5,zh-zl+0.25); ang=math.atan2(zh-zl+0.25,-yo+0.5)
    k.box((0,(yo-0.5)/2,(zh+zl)/2+0.2),(W_+0.5,L,0.14),ROOF,rot=(ang,0,0),bevel=0.04)
    # step
    k.box((0,-0.75,0.1),(1.9,0.9,0.2),STONE,bevel=0.05,segs=2,jitter=0.02,seed=9)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
for n,fn,kw in [("SM_VK_InnerCorner_Stone",inner_corner_stone,{"wobble":False}),("SM_VK_InnerCorner_Plaster",inner_corner_plaster,{"wobble":False}),
                ("SM_VK_InnerCorner_Timber",inner_corner_timber,{"wobble":False,"grime":False}),
                ("SM_VK_Roof_Dormer",dormer,{"wobble":False,"grime":False}),("SM_VK_Porch",porch,{"wobble":False,"grime":False})]:
    k=Kit(); fn(k); o=k.finish(n,P,**kw); o.hide_render=o.hide_viewport=True; print(n,len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_InnerCorner_Stone 350\nSM_VK_InnerCorner_Plaster 52\nSM_VK_InnerCorner_Timber 80\nSM_VK_Roof_Dormer 294\n
# SM_VK_Porch 370\n"}

# ==============================================================================================================
# [0107] 2026-09-23 02:52:57  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def _cyl(k,center,r1,r2,depth,segs,mi,rot=None):
    vs=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=segs,radius1=r1,radius2=r2,depth=depth)["verts"]
    M=Matrix.Translation(Vector(center))@(rot or Matrix.Identity(4))
    bmesh.ops.transform(k.bm,matrix=M,verts=vs)
    fs=list({f for v in vs for f in v.link_faces}); k.bm.normal_update(); k.project(fs,mi); return vs
def prop_well(k):
    rnd=random.Random(2); R=1.05
    n=14
    for layer in range(3):
        for i in range(n):
            a=2*math.pi*(i+0.5*(layer%2))/n
            k.box((math.cos(a)*R,math.sin(a)*R,0.2+layer*0.3),(0.42,2*math.pi*R/n+0.04,0.3),STONE,rot=(0,0,a),bevel=0.05,segs=2,jitter=0.015,seed=layer*20+i)
    for i in range(n):
        a=2*math.pi*i/n
        k.box((math.cos(a)*R,math.sin(a)*R,0.98),(0.52,2*math.pi*R/n+0.06,0.14),STONE,rot=(0,0,a),bevel=0.04)
    k.quad([(-0.9,-0.9,0.5),(0.9,-0.9,0.5),(0.9,0.9,0.5),(-0.9,0.9,0.5)],WINDOW,uvs=[(0,0),(0.3,0),(0.3,0.3),(0,0.3)])  # dark water
    for sx in(-1,1):
        k.box((sx*1.15,0,1.9),(0.2,0.2,2.1),WOOD,bevel=0.05,segs=2)
        k.box((sx*1.0,0,2.35),(0.35,0.12,0.12),WOOD,rot=(0,sx*0.8,0),bevel=0.02)
    _cyl(k,(0,0,1.85),0.14,0.14,2.1,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((1.35,0,1.85),(0.06,0.06,0.35),IRON,bevel=0); k.box((1.35,0.15,1.7),(0.06,0.35,0.06),IRON,bevel=0)
    k.box((0,0,1.3),(0.02,0.02,1.0),IRON,bevel=0)
    _cyl(k,(0.0,0,0.78),0.18,0.22,0.3,10,WOOD)
    for sx in(-1,1):
        k.box((sx*0.75,0,3.2),(1.7,2.0,0.1),ROOF,rot=(0,sx*0.72,0),bevel=0.03)
    k.box((0,0,3.72),(0.2,2.1,0.2),WOOD,bevel=0.04)
    k.box((0,0,2.95),(2.5,0.16,0.16),WOOD,bevel=0.03)
def prop_fence(k,length=3.0):
    rnd=random.Random(int(length*7))
    for x in(-length/2,length/2):
        k.box((x,0,0.55),(0.17,0.17,1.1),WOOD,rot=(0,0,rnd.uniform(-.2,.2)),bevel=0.04,segs=2)
        k.box((x,0,1.13),(0.12,0.12,0.1),WOOD,rot=(0,0,0.785),bevel=0.03)
    for z in(0.35,0.8):
        k.box((0,0.1,z+rnd.uniform(-.04,.04)),(length+0.1,0.07,0.12),WOOD,rot=(0,rnd.uniform(-.03,.03),0),bevel=0.02)
    n=int(length/0.3)
    for i in range(n):
        x=-length/2+0.2+i*(length-0.4)/(n-1); h=rnd.uniform(0.85,1.0)
        vs=k.box((x,0.17,h/2),(0.11,0.04,h),WOOD,rot=(0,rnd.uniform(-.05,.05),0),bevel=0.015)
def prop_fence_gate(k):
    for x in(-1.5,1.5): k.box((x,0,0.65),(0.2,0.2,1.3),WOOD,bevel=0.05,segs=2)
    for s in(-1,1):
        x0=s*1.4; 
        for z in(0.3,0.85): k.box((s*0.75,0.12,z),(1.3,0.06,0.12),WOOD,bevel=0.02)
        for i in range(4): k.box((s*(0.25+i*0.36),0.16,0.55),(0.11,0.04,0.95),WOOD,bevel=0.015)
        k.box((s*0.75,0.14,0.57),(1.35,0.05,0.1),WOOD,rot=(0,-s*0.38,0),bevel=0.015)
def prop_cart(k):
    k.box((0,0,0.85),(2.0,1.2,0.1),WOOD,bevel=0.03)
    for sy in(-1,1): k.box((0,sy*0.6,1.1),(2.0,0.08,0.45),WOOD,bevel=0.02)
    for sx in(-1,1): k.box((sx*1.0,0,1.1),(0.08,1.2,0.45),WOOD,bevel=0.02)
    for sy in(-1,1): k.box((1.5,sy*0.45,0.72),(1.6,0.09,0.09),WOOD,rot=(0,0.35,0),bevel=0.02)
    for sy in(-1,1):
        _cyl(k,(-0.15,sy*0.75,0.55),0.55,0.55,0.1,14,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
        _cyl(k,(-0.15,sy*0.81,0.55),0.12,0.12,0.12,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
        for i in range(6):
            k.box((-0.15,sy*0.75,0.55),(0.06,0.05,1.0),WOOD,rot=(0,i*math.pi/6,0),bevel=0)
    _cyl(k,(-0.15,0,0.55),0.06,0.06,1.6,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    # cargo
    for i,(x,y) in enumerate(((-0.5,-0.25),(-0.5,0.25),(0.15,0))):
        vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=0.3)["verts"]
        for v in vs: v.co=Vector((v.co.x*1.1,v.co.y*0.9,v.co.z*0.8))+Vector((x,y,1.18))
        for f in {f for v in vs for f in v.link_faces}: f.material_index=CLOTH_B
    k.box((0.6,0,1.12),(0.5,0.5,0.45),WOOD,bevel=0.03)
def prop_lamppost(k):
    k.box((0,0,0.12),(0.45,0.45,0.24),STONE,bevel=0.05,segs=2)
    k.box((0,0,1.5),(0.16,0.16,2.8),WOOD,bevel=0.04)
    k.box((0,-0.3,2.75),(0.1,0.7,0.1),WOOD,bevel=0.02)
    k.box((0,-0.2,2.5),(0.08,0.45,0.08),WOOD,rot=(0.75,0,0),bevel=0.015)
    sub=Kit(); prop_lantern(sub)
    merge_kit(k,sub,Matrix.Translation((0,-0.25,2.72)))
def prop_bench(k):
    k.box((0,0,0.48),(1.8,0.45,0.1),WOOD,bevel=0.03)
    for sx in(-0.7,0.7):
        for sy in(-0.15,0.15): k.box((sx,sy,0.22),(0.1,0.1,0.45),WOOD,rot=(sy*0.8,0,0),bevel=0.02)
    k.box((0,0.2,0.85),(1.8,0.07,0.28),WOOD,rot=(-0.2,0,0),bevel=0.02)
    for sx in(-0.7,0.7): k.box((sx,0.22,0.65),(0.08,0.07,0.4),WOOD,bevel=0.02)
def prop_crates(k):
    rnd=random.Random(6)
    for (x,y,z,s) in((0,0,0,0.8),(0.85,0.1,0,0.75),(0.4,0.05,0.8,0.7),(-0.1,0.85,0,0.7)):
        r=rnd.uniform(-.2,.2)
        k.box((x,y,z+s/2),(s,s,s),WOOD,rot=(0,0,r),bevel=0.04)
        for dz in(0.07,s-0.07): k.box((x,y,z+dz),(s+0.04,s+0.04,0.1),WOOD,rot=(0,0,r),bevel=0.02)
    for i,(x,y) in enumerate(((1.4,0.9),(1.6,0.2))):
        for zz,(r0,r1) in((0.25,(0.34,0.4)),(0.75,(0.4,0.34))): _cyl(k,(x,y,zz),r0,r1,0.5,12,WOOD)
        for zz in(0.12,0.88): _cyl(k,(x,y,zz),0.39,0.39,0.06,12,IRON)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
for n,fn in [("SM_VK_Prop_Well",prop_well),("SM_VK_Prop_Fence",prop_fence),("SM_VK_Prop_FenceGate",prop_fence_gate),
             ("SM_VK_Prop_Cart",prop_cart),("SM_VK_Prop_LampPost",prop_lamppost),("SM_VK_Prop_Bench",prop_bench),("SM_VK_Prop_Crates",prop_crates)]:
    k=Kit(); fn(k); o=k.finish(n,P,wobble=False,grime=True); o.hide_render=o.hide_viewport=True; print(n,len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Well 2937\nSM_VK_Prop_Fence 472\nSM_VK_Prop_FenceGate 472\nSM_VK_Prop_Cart 580\nSM_VK_Prop_LampPost 
# 318\nSM_VK_Prop_Bench 208\nSM_VK_Prop_Crates 424\n"}

# ==============================================================================================================
# [0108] 2026-09-23 02:53:24  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
# door porch in _dress
s=s.replace('''    if c=="D":
        px,py=loc(1.0,-0.3); place_v(coll,"SM_VK_Prop_Lantern",px,py,2.55,rot,origin,{})''',
'''    if c=="D":
        if r.random()<0.45: place_v(coll,"SM_VK_Porch",x,y,0,rot,origin,style)
        else:
            px,py=loc(1.0,-0.3); place_v(coll,"SM_VK_Prop_Lantern",px,py,2.55,rot,origin,{})''')
# dormers on straight houses
s=s.replace('''        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)
    if chimney:
        place_v(coll,"SM_VK_Chimney",-L/2+1.5+3*r.randrange(n),0,top,r.choice((0,180)),origin,style)''',
'''        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)
    ci=r.randrange(n); crot=r.choice((0,180))
    if chimney:
        place_v(coll,"SM_VK_Chimney",-L/2+1.5+3*ci,0,top,crot,origin,style)
    if stories==1 or r.random()<0.6:
        for i in range(n):
            if i==ci and chimney: continue
            if r.random()<(0.55 if stories==1 else 0.35):
                place_v(coll,"SM_VK_Roof_Dormer",-L/2+1.5+3*i,0,top,0,origin,style)''')
# L house inner corners
s=s.replace('''    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    _assemble(coll,origin,walls,corners,stories,style,r)
    top=H1+(H2 if stories==2 else 0)
    place_v(coll,"SM_VK_Roof_LCorner",0,0,top,0,origin,style)''',
'''    corners=[(-3,-3,0),(XA,-3,90),(XA,3,180),(3,YB,180),(-3,YB,-90)]
    _assemble(coll,origin,walls,corners,stories,style,r)
    g=style.get("ground","Stone")
    place_v(coll,f"SM_VK_InnerCorner_{g}",3,3,0,0,origin,style)
    if stories==2: place_v(coll,"SM_VK_InnerCorner_Timber",3,3,H1,0,origin,style)
    top=H1+(H2 if stories==2 else 0)
    place_v(coll,"SM_VK_Roof_LCorner",0,0,top,0,origin,style)''')
t.clear(); t.write(s); exec(s)
# test: one of each, near origin y=40
T=vcol("VK_Test")
for o in list(T.objects): bpy.data.objects.remove(o)
for o in vcol("VK_Demo").objects: o.hide_render=True
st=random_style(21); st.update({"ground":"Plaster","roof":"Green"})
build_house_v(T,(0,40,0),3,1,st,front="WDW")
st=random_style(22); st.update({"ground":"Stone","roof":"Red"})
build_L_v(T,(-16,40,0),1,1,2,st)
for i,n in enumerate(["SM_VK_Prop_Well","SM_VK_Prop_Cart","SM_VK_Prop_LampPost","SM_VK_Prop_Bench","SM_VK_Prop_Crates","SM_VK_Prop_Fence","SM_VK_Prop_FenceGate"]):
    place_v(T,n,-18+i*4.2,31,0,0,(0,0,0),{})
ct=bpy.data.objects["VK_CameraT"]; ct.data.lens=28
tgt=Vector((-7,38,2)); ct.location=tgt+Vector((6,-24,13))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ct; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0109] 2026-09-23 02:54:01  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
for o in list(vcol("VK_Test").objects): bpy.data.objects.remove(o)
for o in vcol("VK_Demo").objects: o.hide_render=False
bpy.ops.wm.save_mainfile()
code=r'''
def road_strip(coll,name,pts,w=3.2):
    bm=bmesh.new(); prev=None
    L=[]
    for i,p in enumerate(pts):
        a=Vector(pts[max(i-1,0)]); b=Vector(pts[min(i+1,len(pts)-1)]); d=(b-a).normalized(); n=Vector((-d.y,d.x))
        p=Vector(p); L.append((bm.verts.new((*(p+n*w),0.02)),bm.verts.new((*(p-n*w),0.02))))
    for i in range(len(L)-1): bm.faces.new((L[i][1],L[i+1][1],L[i+1][0],L[i][0]))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); coll.objects.link(o); me.materials.append(bpy.data.materials["MC_WK_Dirt"]); return o
def fence_run(coll,a,b,origin=(0,0,0),gate_at=None):
    a=Vector(a); b=Vector(b); L=(b-a).length; n=max(1,round(L/3)); d=(b-a)/n
    rot=math.degrees(math.atan2(d.y,d.x))
    for i in range(n):
        c=a+d*(i+0.5)
        place_v(coll,"SM_VK_Prop_FenceGate" if gate_at==i else "SM_VK_Prop_Fence",c.x,c.y,0,rot,origin,{})
def street(coll,x0,x1,yroad,seed,side_gap=9.5):
    r=random.Random(seed); placed=[]
    for side in(1,-1):
        x=x0+r.uniform(0,3)
        while True:
            kind=r.choices(["S","L"],[0.8,0.2])[0]
            n=r.choice([2,2,3,3,4]) if kind=="S" else 0
            length=n*CELL if kind=="S" else 12
            if x+length>x1: break
            st=random_style(seed*100+len(placed)+(0 if side>0 else 50))
            cx=x+length/2
            y=yroad+side*side_gap
            rot=0 if side>0 else 180
            org=(cx,y,math.radians(rot))
            if kind=="S": build_house_v(coll,org,n,r.choice([1,2,2]),st)
            else:
                # L house: junction at origin; place so front (wing A, -Y local) faces the road
                ox=x+3; org=(ox if side>0 else x+length-3,y,math.radians(rot)); build_L_v(coll,org,1,1,2,st)
            # garden behind
            if r.random()<0.7:
                gy0=y+side*3.8; gy1=y+side*(3.8+r.choice([6,9]))
                xa=x-0.3; xb=x+length+0.3
                fence_run(coll,(xa,gy1),(xb,gy1)); fence_run(coll,(xa,gy0),(xa,gy1)); fence_run(coll,(xb,gy0),(xb,gy1),gate_at=0)
                gardens.append((xa,min(gy0,gy1),xb,max(gy0,gy1)))
            # street props in front
            px=x+r.uniform(0.5,length-0.5); py=yroad+side*5.2
            pk=r.choice(["SM_VK_Prop_LampPost","SM_VK_Prop_Bench","SM_VK_Prop_Crates","SM_VK_Prop_Cart",None,"SM_VK_Prop_LampPost"])
            if pk: place_v(coll,pk,px,py,0,rot+(0 if pk!="SM_VK_Prop_Cart" else r.uniform(-30,30)),(0,0,0),{})
            placed.append((x,length)); x+=length+r.uniform(2.5,5)
gardens=[]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
V=vcol("VK_Village")
for o in list(V.objects): bpy.data.objects.remove(o)
gardens.clear()
street(V,23,72,3.5,7)
street(V,-72,-23,8.5,8)
road_strip(V,"VK_RoadEast",[(12,2.5),(24,3.5),(45,3.8),(72,3.2)])
road_strip(V,"VK_RoadWest",[(-12,5),(-24,8.5),(-45,8.2),(-72,9)])
# plaza well + lamp posts
place_v(V,"SM_VK_Prop_Well",-1,-0.5,0,20,(0,0,0),{})
for (x,y) in((-9,-5),(10,5),(-8,6.5),(9,-6)): place_v(V,"SM_VK_Prop_LampPost",x,y,0,r_ if (r_:=0) else 0,(0,0,0),{})
print(len(V.objects), len(gardens))
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n493 9\n"}

# ==============================================================================================================
# [0110] 2026-09-23 02:54:24  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def prop_garden_bed(k):
    rnd=random.Random(3)
    k.box((0,0,0.1),(2.8,1.6,0.2),WOOD,bevel=0.03)
    soil=tex_mat("M_VK_Soil",None,1.0,flat=(0.20,0.13,0.08))
    k.box((0,0,0.2),(2.6,1.4,0.06),BREAD,bevel=0)   # re-tinted to soil below
    for row in range(3):
        for i in range(6):
            x=-1.05+i*0.42+rnd.uniform(-.04,.04); y=-0.45+row*0.45
            vs=bmesh.ops.create_icosphere(k.bm,subdivisions=1,radius=0.17)["verts"]
            for v in vs:
                d=v.co.normalized(); v.co=Vector((v.co.x,v.co.y,v.co.z*0.75))*(1+0.18*noise.noise(d*3+Vector((x,y,0))))+Vector((x,y,0.33))
            for f in {f for v in vs for f in v.link_faces}: f.material_index=LEAF
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
k=Kit(); prop_garden_bed(k); o=k.finish("SM_VK_Prop_GardenBed",P,wobble=False,grime=False); o.hide_render=o.hide_viewport=True
o.data.materials[BREAD]=bpy.data.materials["M_VK_Soil"]
for p in o.data.polygons: p.use_smooth = p.material_index==LEAF
V=vcol("VK_Village"); rnd=random.Random(5)
for (xa,ya,xb,yb) in gardens:
    nx=int((xb-xa-0.8)/3.2); ny=int((yb-ya-0.6)/2.2)
    for i in range(nx):
        for j in range(ny):
            if rnd.random()<0.8:
                place_v(V,"SM_VK_Prop_GardenBed",xa+1.9+i*3.2,ya+1.4+j*2.2,0,0,(0,0,0),{})
# trees: ring around the village avoiding built areas
built=[(ob.matrix_world.translation.x,ob.matrix_world.translation.y) for ob in list(V.objects)+list(vcol("VK_Demo").objects) if ob.type=="MESH" and not ob.name.startswith("VK_Road")]
tw=bpy.data.objects["SM_Tree_Wood"].data; tf=bpy.data.objects["SM_Tree_Foliage"].data
n=0; tries=0
for ob in list(V.objects):
    if ob.name.startswith("VK_VTree"): bpy.data.objects.remove(ob)
while n<45 and tries<3000:
    tries+=1
    x=rnd.uniform(-80,80); y=rnd.uniform(-40,45)
    if abs(y-6)<5.5 and abs(x)>12: continue
    if math.hypot(x-1,y)<17: continue
    if min((x-bx)**2+(y-by)**2 for bx,by in built)<7.5**2: continue
    s_=rnd.uniform(0.8,1.2); rz=rnd.uniform(0,6.28)
    for d,nm in ((tw,"W"),(tf,"F")):
        t_=bpy.data.objects.new(f"VK_VTree{n}{nm}",d); V.objects.link(t_); t_.location=(x,y,0); t_.scale=(s_,s_,s_); t_.rotation_euler.z=rz
    built.append((x,y)); n+=1
g=bpy.data.objects["VK_Ground"]; g.scale=(6,6,1)
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=24
tgt=Vector((0,3,0)); cam.location=Vector((20,-72,58))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.clip_end=500
SC.camera=cam; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
print(n)
# ---- result ----
# {"result":"Code executed successfully: 45\n"}

# ==============================================================================================================
# [0111] 2026-09-23 02:54:43  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
V=bpy.data.collections["VK_Village"]; D=bpy.data.collections["VK_Demo"]
walls=[o for o in list(V.objects)+list(D.objects) if "_Wall_" in o.name or "Corner" in o.name]
rm=[]
for o in list(D.objects)+list(V.objects):
    if "Tree" in o.name:
        p=o.location
        if any((w.location.xy-p.xy).length<4.5 for w in walls): rm.append(o.name)
print(rm)
# check wall pieces from different houses overlapping: group by house via name suffix not available -> check any two wall centres < 1.0 apart
pos=[(w.name,w.location.copy()) for w in walls if "_Wall_" in w.name and w.location.z<1]
clash=set()
for i in range(len(pos)):
    for j in range(i+1,len(pos)):
        if (pos[i][1]-pos[j][1]).length<1.2: clash.add((round(pos[i][1].x),round(pos[i][1].y)))
print(sorted(clash)[:40], len(clash))
# ---- result ----
# {"result":"Code executed successfully: ['VK_Tree1W', 'VK_Tree1F', 'VK_Tree2W', 'VK_Tree2F']\n[] 0\n"}

# ==============================================================================================================
# [0112] 2026-09-23 02:54:56  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
for n in ['VK_Tree1W','VK_Tree1F','VK_Tree2W','VK_Tree2F']: bpy.data.objects.remove(bpy.data.objects[n])
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=100
cam=bpy.data.objects["VK_Camera"]; cam.data.lens=26
tgt=Vector((-2,4,0)); cam.location=Vector((28,-64,48))
cam.rotation_euler=(tgt-cam.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cam; SC.render.filepath=os.path.join(out,"village_overview.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# street-level: east street looking east
cc=bpy.data.objects["VK_CameraClose"]; cc.data.lens=26
cc.location=Vector((24,1.5,2.2)); tgt=Vector((50,4.5,3.2))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.filepath=os.path.join(out,"village_street_east.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
SC.camera=cam
os.remove(os.path.join(out,"_vk_test.png"))
bpy.ops.wm.save_mainfile()
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n"}

# ==============================================================================================================
# [0113] 2026-09-23 02:57:06  blender  ERROR
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''            tex_mat("M_VK_Bread",None,0.8,flat=(0.72,0.48,0.22))]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD=range(16)''',
'''            tex_mat("M_VK_Bread",None,0.8,flat=(0.72,0.48,0.22)),
            tex_mat("M_VK_Hay",None,0.95,flat=(0.86,0.68,0.30)), tex_mat("M_VK_Paper",None,0.9,flat=(0.92,0.86,0.70)),
            tex_mat("M_VK_Water",None,0.1,flat=(0.12,0.35,0.42)), tex_mat("M_VK_Bronze",None,0.35,flat=(0.72,0.48,0.20)),
            tex_mat("M_VK_Stained",None,0.3,flat=(0.9,0.5,0.2),emit=(0.9,0.35,0.15)), tex_mat("M_VK_Steel",None,0.3,flat=(0.55,0.57,0.60))]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD,HAY,PAPER,WATER,BRONZE,STAINED,STEEL=range(22)''')
t.clear(); t.write(s); exec(s)
for m in ("M_VK_Bronze","M_VK_Steel"):
    b=next(n for n in bpy.data.materials[m].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Metallic"].default_value=0.8
b=next(n for n in bpy.data.materials["M_VK_Stained"].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Emission Strength"].default_value=1.5
print(len(kit_mats()))
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: 'bpy_prop_collection[key]: key \"M_VK_Bronze\" not found'"}

# ==============================================================================================================
# [0114] 2026-09-23 02:57:15  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["vk_helpers"].as_string()
i=s.find("M_VK_Bread"); print("Hay" in s, repr(s[i-60:i+200]))
# ---- result ----
# {"result":"Code executed successfully: True 'pkin\",None,0.6,flat=(0.90,0.45,0.08)),\\n tex_mat(\"M_VK_Bread\",None,0.8,flat=(0.72,0.48,0.22)),\\n tex
# _mat(\"M_VK_Hay\",None,0.95,flat=(0.86,0.68,0.30)), tex_mat(\"M_VK_Paper\",None,0.9,flat=(0.92,0.86,0.70)),\\n tex_mat(\"M_VK_Water\",Non'\n"}

# ==============================================================================================================
# [0115] 2026-09-23 02:57:24  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
print(len(kit_mats()))
for m in ("M_VK_Bronze","M_VK_Steel"):
    b=next(n for n in bpy.data.materials[m].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Metallic"].default_value=0.8
b=next(n for n in bpy.data.materials["M_VK_Stained"].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Emission Strength"].default_value=1.5
# ---- result ----
# {"result":"Code executed successfully: 22\n"}

# ==============================================================================================================
# [0116] 2026-09-23 02:58:10  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def _ico(k,c,r,mi,scale=(1,1,1),sub=2,jit=0.0,seed=0):
    rnd=random.Random(seed)
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=sub,radius=r)["verts"]
    for v in vs:
        v.co=Vector((v.co.x*scale[0],v.co.y*scale[1],v.co.z*scale[2]))
        if jit: v.co+=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1)))*jit
        v.co+=Vector(c)
    for f in {f for v in vs for f in v.link_faces}: f.material_index=mi
    return vs
def barrel(k,x,y,z=0,r=0.4,h=1.0,lying=False):
    M=Matrix.Translation((x,y,z))@(Matrix.Rotation(math.pi/2,4,"X") if lying else Matrix.Identity(4))
    sub=Kit()
    for zz,(r0,r1) in((h*0.25,(r*0.86,r)),(h*0.75,(r,r*0.86))): _cyl(sub,(0,0,zz-(h/2 if lying else 0)),r0,r1,h/2,12,WOOD)
    for zz in(h*0.1,h*0.9): _cyl(sub,(0,0,zz-(h/2 if lying else 0)),r*0.9,r*0.9,0.06,12,IRON)
    merge_kit(k,sub,M)
def prop_table(k):
    k.box((0,0,0.78),(2.0,0.95,0.1),WOOD,bevel=0.03)
    for sx in(-0.8,0.8):
        k.box((sx,0,0.38),(0.12,0.75,0.1),WOOD,bevel=0.02)
        for sy in(-1,1): k.box((sx,sy*0.28,0.38),(0.1,0.1,0.8),WOOD,rot=(sy*0.35,0,0),bevel=0.02)
    k.box((0,0,0.35),(1.7,0.08,0.08),WOOD,bevel=0.01)
    rnd=random.Random(1)
    for i,(x,y) in enumerate(((-0.6,-0.2),(0.1,0.25),(0.7,-0.15))):   # tankards
        _cyl(k,(x,y,0.95),0.08,0.08,0.24,8,WOOD); _cyl(k,(x,y,1.07),0.075,0.075,0.02,8,HAY)
        k.box((x+0.1,y,0.95),(0.05,0.03,0.14),WOOD,bevel=0)
    _cyl(k,(-0.1,-0.15,0.85),0.2,0.2,0.04,12,WOOD); _ico(k,(-0.1,-0.15,0.92),0.12,BREAD,(1.3,0.9,0.6))
def prop_stool(k):
    _cyl(k,(0,0,0.5),0.25,0.25,0.08,10,WOOD)
    for i in range(3):
        a=i*2.094; k.box((math.cos(a)*0.14,math.sin(a)*0.14,0.24),(0.07,0.07,0.5),WOOD,rot=(math.sin(a)*0.2,-math.cos(a)*0.2,0),bevel=0.01)
def prop_trough(k):
    k.box((0,0,0.1),(2.0,0.8,0.2),WOOD,bevel=0.03)
    for sy in(-1,1): k.box((0,sy*0.36,0.4),(2.0,0.1,0.6),WOOD,bevel=0.03)
    for sx in(-1,1): k.box((sx*0.96,0,0.4),(0.1,0.8,0.6),WOOD,bevel=0.03)
    k.quad([(-0.9,-0.3,0.55),(0.9,-0.3,0.55),(0.9,0.3,0.55),(-0.9,0.3,0.55)],WATER,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for sx in(-0.7,0.7): k.box((sx,0,0.4),(0.08,0.9,0.66),IRON,bevel=0)
def prop_haybale(k):
    k.box((0,0,0.35),(1.3,0.8,0.7),HAY,bevel=0.12,segs=3,jitter=0.03,seed=2)
    for sx in(-0.35,0.35): k.box((sx,0,0.35),(0.05,0.84,0.74),WOOD,bevel=0.02)
    k.box((0.3,0.1,0.95),(1.2,0.75,0.6),HAY,rot=(0,0,0.4),bevel=0.1,segs=3,jitter=0.03,seed=3)
def prop_haystack(k):
    _ico(k,(0,0,0.9),1.3,HAY,(1,1,1.1),sub=2,jit=0.08,seed=4)
    _cyl(k,(0,0,2.2),0.06,0.06,0.9,6,WOOD)
def prop_woodpile(k):
    rnd=random.Random(5)
    for row in range(4):
        for i in range(7-row):
            x=-1.1+i*0.34+row*0.17; z=0.17+row*0.3
            _cyl(k,(x,0,z),0.16,0.16,1.0,7,BREAD if (i+row)%3==0 else WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for sx in(-1.35,1.35): k.box((sx,0,0.6),(0.12,0.12,1.3),WOOD,bevel=0.03)
    k.box((0,0,1.35),(3.0,1.3,0.08),ROOF,rot=(0.12,0,0),bevel=0.02)
    for sx in(-1.35,1.35):
        for sy in(-0.5,0.5): k.box((sx,sy,0.7),(0.1,0.1,1.35),WOOD,bevel=0.02)
    _cyl(k,(1.9,0.3,0.25),0.3,0.32,0.5,10,WOOD); k.box((1.95,0.3,0.7),(0.05,0.05,0.5),WOOD,rot=(0,0.3,0),bevel=0)
    k.box((2.0,0.3,0.92),(0.05,0.22,0.12),STEEL,bevel=0)
def prop_noticeboard(k):
    for sx in(-0.8,0.8): k.box((sx,0,1.1),(0.14,0.14,2.2),WOOD,bevel=0.04)
    k.box((0,0,1.5),(1.5,0.08,1.0),WOOD,bevel=0.03)
    rnd=random.Random(6)
    for i in range(5):
        k.box((-0.5+i*0.25+rnd.uniform(-.05,.05),-0.05,1.5+rnd.uniform(-.25,.25)),(0.22,0.02,0.3),PAPER,rot=(0,rnd.uniform(-.2,.2),0),bevel=0)
    for sx in(-1,1): k.box((sx*0.5,0,2.35),(1.2,0.9,0.07),ROOF,rot=(0,sx*0.45,0),bevel=0.02)
def prop_signpost(k):
    k.box((0,0,1.4),(0.16,0.16,2.8),WOOD,bevel=0.04)
    k.box((0,0,0.1),(0.4,0.4,0.2),STONE,bevel=0.05)
    for i,(a,z) in enumerate(((0.3,2.4),(2.2,2.05),(4.0,1.7))):
        R=Matrix.Rotation(a,4,"Z")
        sub=Kit(); sub.box((0.55,0,0),(0.95,0.06,0.24),WOOD,bevel=0.03)
        v=[sub.bm.verts.new(p) for p in ((1.02,-0.03,-0.12),(1.02,-0.03,0.12),(1.2,-0.03,0))]; f=sub.bm.faces.new(v); f.material_index=WOOD
        merge_kit(k,sub,Matrix.Translation((0,0,z))@R)
def prop_anvil(k):
    _cyl(k,(0,0,0.3),0.32,0.36,0.6,10,WOOD)
    k.box((0,0,0.72),(0.35,0.22,0.24),STEEL,bevel=0.03)
    k.box((0,0,0.9),(0.6,0.26,0.14),STEEL,bevel=0.03)
    _cyl(k,(0.42,0,0.9),0.1,0.01,0.3,8,STEEL,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((0.05,0.05,1.0),(0.05,0.3,0.05),WOOD,bevel=0); k.box((0.05,-0.12,1.02),(0.12,0.08,0.08),IRON,bevel=0.01)
def prop_grindstone(k):
    for sx in(-0.3,0.3): k.box((sx,0,0.45),(0.1,0.1,0.9),WOOD,bevel=0.02)
    k.box((0,0,0.2),(0.8,0.1,0.1),WOOD,bevel=0.01)
    _cyl(k,(0,0,0.9),0.42,0.42,0.14,16,STONE,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(0,0,0.9),0.04,0.04,0.9,6,IRON,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((0.48,0,0.8),(0.04,0.04,0.25),IRON,bevel=0)
def prop_sacks(k):
    rnd=random.Random(7)
    for i,(x,y,z) in enumerate(((0,0,0),(0.55,0.1,0),(0.25,0.5,0),(0.3,0.2,0.55))):
        _ico(k,(x,y,z+0.32),0.3,CLOTH_B,(1,0.85,1.1),jit=0.02,seed=i)
        _cyl(k,(x,y,z+0.66),0.08,0.12,0.1,6,CLOTH_B)
def prop_weaponrack(k):
    for sx in(-0.7,0.7): k.box((sx,0,0.8),(0.12,0.3,1.6),WOOD,bevel=0.03)
    k.box((0,0,0.35),(1.5,0.3,0.08),WOOD,bevel=0.02); k.box((0,0.05,1.4),(1.5,0.1,0.1),WOOD,bevel=0.02)
    for i in range(4):
        x=-0.5+i*0.33
        k.box((x,0.05,1.0),(0.04,0.04,1.8),WOOD,rot=(0.12,0,0),bevel=0)
        if i%2: _cyl(k,(x,0.2,1.95),0.05,0,0.25,4,STEEL)
        else:   k.box((x,0.18,1.75),(0.02,0.28,0.2),STEEL,bevel=0)
    _cyl(k,(0,-0.25,0.7),0.4,0.4,0.06,12,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X")@Matrix.Rotation(0,4,"Z"))
    _cyl(k,(0,-0.29,0.7),0.12,0.12,0.06,8,STEEL,rot=Matrix.Rotation(math.pi/2,4,"X"))
def prop_barrelstack(k):
    for i,x in enumerate((-0.45,0.45)): barrel(k,x,0,0.4,0.4,1.0,lying=True)
    barrel(k,0,0,1.1,0.4,1.0,lying=True)
    for sx in(-0.9,0.9): k.box((sx,0,0.1),(0.12,1.1,0.2),WOOD,bevel=0.02)
    _cyl(k,(0,-0.55,1.1),0.05,0.05,0.12,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
def prop_bellows_forge(k):   # standalone open forge hearth
    k.box((0,0,0.45),(1.6,1.2,0.9),STONE,bevel=0.05,segs=2)
    k.box((0,0,0.92),(1.2,0.8,0.06),GLOW,bevel=0.02)
    for i in range(6): _ico(k,(-0.4+i*0.16,0.05*(-1)**i,0.97),0.08,IRON if i%2 else GLOW,sub=0)
    k.box((0,0.45,1.9),(1.2,0.3,1.8),STONE,bevel=0.05,segs=2)
    k.box((0,0.2,1.3),(1.5,0.8,0.12),STONE,rot=(0.3,0,0),bevel=0.03)
    k.box((1.15,0,0.7),(0.7,0.5,0.25),CLOTH_B,rot=(0,0.2,0),bevel=0.08,segs=2)
    k.box((1.5,0,0.72),(0.35,0.4,0.05),WOOD,rot=(0,0.2,0),bevel=0.01)
    k.box((0.85,0,0.7),(0.12,0.12,0.3),WOOD,bevel=0.02)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
P=vcol("VK_Pieces")
props=[("Table",prop_table),("Stool",prop_stool),("Trough",prop_trough),("HayBale",prop_haybale),("Haystack",prop_haystack),
       ("Woodpile",prop_woodpile),("NoticeBoard",prop_noticeboard),("Signpost",prop_signpost),("Anvil",prop_anvil),
       ("Grindstone",prop_grindstone),("Sacks",prop_sacks),("WeaponRack",prop_weaponrack),("BarrelStack",prop_barrelstack),("Forge",prop_bellows_forge)]
for n,fn in props:
    k=Kit(); fn(k); o=k.finish("SM_VK_Prop_"+n,P,wobble=False,grime=True)
    for p in o.data.polygons: p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF)
    o.hide_render=o.hide_viewport=True; print(n,len(o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: Table 380\nStool 90\nTrough 143\nHayBale 248\nHaystack 88\nWoodpile 404\nNoticeBoard 160\nSignpost 133\nAnvil 1
# 06\nGrindstone 110\nSacks 352\nWeaponRack 174\nBarrelStack 228\nForge 386\n"}

# ==============================================================================================================
# [0117] 2026-09-23 02:58:26  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
T=vcol("VK_Test")
for o in list(T.objects): bpy.data.objects.remove(o)
for c in ("VK_Demo","VK_Village"):
    for o in vcol(c).objects: o.hide_render=True
names=["Table","Stool","Trough","HayBale","Haystack","Woodpile","NoticeBoard","Signpost","Anvil","Grindstone","Sacks","WeaponRack","BarrelStack","Forge","Well","Cart","Fence","FenceGate"]
for i,n in enumerate(names):
    place_v(T,"SM_VK_Prop_"+n,(i%6)*4.0,-120-(i//6)*4.5,0,0,(0,0,0),{})
cd=bpy.data.cameras.get("VK_CamP") or bpy.data.cameras.new("VK_CamP"); cd.lens=32
cp=bpy.data.objects.get("VK_CameraProps") or bpy.data.objects.new("VK_CameraProps",cd)
if cp.name not in SC.collection.objects: SC.collection.objects.link(cp)
tgt=Vector((10,-124.5,0.6)); cp.location=tgt+Vector((0,-17,11))
cp.rotation_euler=(tgt-cp.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cp; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0118] 2026-09-23 02:59:00  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tdir=os.path.join(out,"VillageKit","Textures")
def tnoise(S,fmax,n,decay,seed):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,fmax+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
def smooth(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def save(name,col):
    S=col.shape[0]
    img=bpy.data.images.get(name)
    if img: bpy.data.images.remove(img)
    img=bpy.data.images.new(name,col.shape[1],S,alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones(col.shape[:2])])[::-1]).astype(np.float32).ravel())
    img.filepath_raw=os.path.join(tdir,name+".png"); img.file_format="PNG"; img.save(); img.pack()
S=1024; y,x=np.mgrid[0:S,0:S]/S
# ---- THATCH: 6 overlapping courses of straw bundles, strokes point down-slope (V)
nrow=6; row=(y*nrow).astype(int); v=(y*nrow)%1
wob=tnoise(S,6,40,0.9,1)*0.04
strands=np.sin(2*np.pi*(x*90+wob*20+row*0.37))*0.5+0.5
strands2=np.sin(2*np.pi*(x*37+tnoise(S,10,40,0.8,2)*0.8))*0.5+0.5
edge=0.88+0.08*np.sin(2*np.pi*(x*14+row*0.5))+0.04*tnoise(S,40,80,0.5,3)
inside=v<edge
lum=0.55+0.45*np.clip(v/edge,0,1)**0.8              # lit bottom of each course
lum*=0.78+0.14*strands+0.08*strands2
lum=np.where(inside,lum,0.35+0.2*strands)          # shadowed band under the next course
base=np.array([0.78,0.60,0.30]); dark=np.array([0.45,0.32,0.16])
tint=(tnoise(S,4,30,1.0,4)*0.5+0.5)[...,None]
col=(base*(0.9+0.2*tint)+(dark-base)*0.25*(1-tint))*lum[...,None]
grey=np.clip(tnoise(S,5,40,0.9,5),0,1)[...,None]*0.35   # weathered grey patches
col=col*(1-grey)+np.array([0.48,0.44,0.36])*lum[...,None]*grey
save("T_VK_Thatch",col)
# ---- PLANKS: vertical boards, 8 per tile (tile = 2m -> 25cm boards)
nb=8; b=(x*nb).astype(int); u=(x*nb)%1
rnd=np.random.default_rng(6); btint=rnd.uniform(0.82,1.12,nb); boff=rnd.uniform(0,1,nb)
grain=np.sin(2*np.pi*(u*3+ (y+boff[b])*1.3+tnoise(S,3,30,0.9,7)*0.5))*0.5+0.5
fine=np.sin(2*np.pi*(u*11+tnoise(S,8,50,0.7,8)*1.5))*0.5+0.5
wd=np.array([0.30,0.19,0.11]); wl=np.array([0.50,0.34,0.20])
t=np.clip(0.35+0.35*grain+0.2*fine,0,1)[...,None]
col=(wd+(wl-wd)*t)*btint[b][...,None]
gap=smooth(0.0,0.04,u)*smooth(0.0,0.04,1-u)
col*= (0.3+0.7*gap)[...,None]*(0.88+0.12*smooth(0.04,0.2,u)[...,None])   # left edge highlight falloff
# nails
for bi in range(nb):
    for yy in (0.1,0.6):
        d=np.hypot((x-(bi+0.5)/nb)*S,(y-yy-boff[bi]*0.05)*S); col*=(1-0.6*np.exp(-(d/4)**2))[...,None]
save("T_VK_Planks",col)
# ---- STRAW (hay): dense crossing strokes
a1=np.sin(2*np.pi*(x*60+y*14+tnoise(S,8,40,0.8,9)*2)); a2=np.sin(2*np.pi*(x*-50+y*20+tnoise(S,8,40,0.8,10)*2))
s_=np.maximum(a1,a2)*0.5+0.5
lum=0.62+0.38*s_**2+0.08*tnoise(S,30,100,0.5,11)
col=np.array([0.86,0.68,0.32])*lum[...,None]*(0.92+0.1*tnoise(S,4,30,1,12))[...,None]
save("T_VK_Straw",col)
# ---- ASHLAR: regular dressed blocks, 5 courses
nrow=5; row=(y*nrow).astype(int); v=(y*nrow)%1
bl=np.where(row%2==0,3,4)
xo=(x+np.where(row%2==0,0,0.125)); c=(xo*bl).astype(int); u=(xo*bl)%1
wpx=S/bl; hpx=S/nrow
d=np.minimum(np.minimum(u,1-u)*wpx,np.minimum(v,1-v)*hpx)
mask=smooth(3,5,d); h=smooth(3,25,d)
gy,gx=np.gradient(h); shade=(-gx*40*-0.4+gy*40*0.8+0.45)/np.sqrt((gx*40)**2+(gy*40)**2+1)
rng=np.random.default_rng(13); tint=rng.uniform(0.9,1.08,(nrow,5))
colb=np.array([0.66,0.62,0.55])*tint[row,np.clip(c,0,4)][...,None]
mott=tnoise(S,20,80,0.7,14)*0.06+tnoise(S,70,120,0.4,15)*0.04
col=colb*(0.72+0.5*shade[...,None]+mott[...,None])
col=col*mask[...,None]+np.array([0.28,0.25,0.22])*(1-mask[...,None])
save("T_VK_Ashlar",col)
# ---- BURLAP
wv=(np.sin(2*np.pi*x*120)*np.sin(2*np.pi*y*120))*0.5+0.5
col=np.array([0.62,0.50,0.33])*(0.8+0.25*wv+0.08*tnoise(S,10,60,0.7,16))[...,None]
save("T_VK_Burlap",col)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0119] 2026-09-23 02:59:37  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''tex_mat("M_VK_Steel",None,0.3,flat=(0.55,0.57,0.60))]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD,HAY,PAPER,WATER,BRONZE,STAINED,STEEL=range(22)''',
'''tex_mat("M_VK_Steel",None,0.3,flat=(0.55,0.57,0.60)),
            tex_mat("M_VK_Thatch","T_VK_Thatch",0.95), tex_mat("M_VK_Planks","T_VK_Planks",0.85),
            tex_mat("M_VK_Ashlar","T_VK_Ashlar",0.85), tex_mat("M_VK_Burlap","T_VK_Burlap",0.95)]
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD,HAY,PAPER,WATER,BRONZE,STAINED,STEEL,THATCH,PLANKS,ASHLAR,BURLAP=range(26)''')
s=s.replace("TILE={0:3.0,1:1.5,2:1.6,3:3.0,4:1.0,5:1.0,10:1.6}","TILE={0:3.0,1:1.5,2:1.6,3:3.0,4:1.0,5:1.0,10:1.6,16:1.2,22:3.0,23:2.0,24:2.5,25:0.8}")
# roof variants: allow a thatch option
s=s.replace(''' "roof":{"Red":None,"Blue":("T_VK_RoofBlue",None),"Green":("T_VK_RoofGreen",None)},''',
''' "roof":{"Red":None,"Blue":("T_VK_RoofBlue",None),"Green":("T_VK_RoofGreen",None),"Thatch":("T_VK_Thatch",None)},''')
# sacks -> burlap
s=s.replace("        _ico(k,(x,y,z+0.32),0.3,CLOTH_B,(1,0.85,1.1),jit=0.02,seed=i)\n        _cyl(k,(x,y,z+0.66),0.08,0.12,0.1,6,CLOTH_B)",
            "        _ico(k,(x,y,z+0.32),0.3,BURLAP,(1,0.85,1.1),jit=0.02,seed=i)\n        _cyl(k,(x,y,z+0.66),0.08,0.12,0.1,6,BURLAP)")
s=s.replace("        for f in {f for v in vs for f in v.link_faces}: f.material_index=CLOTH_B\n    k.box((0.6,0,1.12)","        for f in {f for v in vs for f in v.link_faces}: f.material_index=BURLAP\n    k.box((0.6,0,1.12)")
t.clear(); t.write(s); exec(s)
kit_mats()
# hay material -> straw texture
m=bpy.data.materials["M_VK_Hay"]; nt=m.node_tree
mix=next(n for n in nt.nodes if n.type=="MIX")
tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images["T_VK_Straw"]; nt.links.new(tx.outputs[0],mix.inputs[6])
# thatch roof variant material
variant_mat("roof","Thatch")
# projection: Kit.project for icospheres etc uses face normal projection; hay/burlap on smooth shapes need box projection - reuse project (already planar per-face)
P=vcol("VK_Pieces")
def rebuild(n,fn,**kw):
    k=Kit(); fn(k)
    # planar-project any faces lacking UVs (spheres/cones created without project)
    for f in k.bm.faces:
        if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)
    o=k.finish(n,P,**kw)
    for p in o.data.polygons: p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP)
    o.hide_render=o.hide_viewport=True; return o
for n,fn in [("Table",prop_table),("Stool",prop_stool),("Trough",prop_trough),("HayBale",prop_haybale),("Haystack",prop_haystack),
       ("Woodpile",prop_woodpile),("NoticeBoard",prop_noticeboard),("Signpost",prop_signpost),("Anvil",prop_anvil),
       ("Grindstone",prop_grindstone),("Sacks",prop_sacks),("WeaponRack",prop_weaponrack),("BarrelStack",prop_barrelstack),("Forge",prop_bellows_forge),("Cart",prop_cart)]:
    rebuild("SM_VK_Prop_"+n,fn,wobble=False,grime=True)
t.write("\n"+'''def rebuild(n,fn,**kw):
    P=vcol("VK_Pieces"); k=Kit(); fn(k)
    for f in k.bm.faces:
        if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)
    o=k.finish(n,P,**kw)
    for p in o.data.polygons: p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP)
    o.hide_render=o.hide_viewport=True; return o
''')
# glow brighter for forge embers
b=next(n for n in bpy.data.materials["M_VK_Glow"].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Emission Strength"].default_value=8
# relink test instances
for o in vcol("VK_Test").objects:
    base=o.name.split("_inst")[0]
    if base in bpy.data.objects: o.data=bpy.data.objects[base].data
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0120] 2026-09-23 03:00:14  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
def tnoise(S,fmax,n,decay,seed,fy_max=None):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,(fy_max if fy_max is not None else fmax)+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
S=1024; y,x=np.mgrid[0:S,0:S]/S
# grain runs along U (x). Low frequency in x, high in y.
warp=tnoise(S,2,30,0.9,41,fy_max=3)*0.05
g1=np.sin(2*np.pi*(y*9+warp*4+tnoise(S,3,20,1.0,42,fy_max=2)*0.25))
g2=np.sin(2*np.pi*(y*31+warp*9+tnoise(S,4,30,0.8,43,fy_max=4)*0.4))
streak=tnoise(S,3,60,0.6,44,fy_max=40)      # long painted strokes along x
lum=0.62+0.14*g1+0.07*g2+0.12*streak
# painted dark grain lines (thin, occasional)
lines=np.abs(np.sin(2*np.pi*(y*14+warp*6+tnoise(S,2,20,0.9,45,fy_max=3)*0.35)))
lum-=0.22*np.clip(1-lines/0.05,0,1)
# cracks: a few long dark splits
crack=np.abs(tnoise(S,2,15,0.8,46,fy_max=12))
lum-=0.25*np.clip(1-crack/0.015,0,1)*np.clip(tnoise(S,2,10,1,47)+0.3,0,1)
# knots
rng=np.random.default_rng(48)
for kx,ky in rng.uniform(0,1,(4,2)):
    dx=((x-kx+0.5)%1-0.5)*2.2; dy=((y-ky+0.5)%1-0.5)*6
    d=np.hypot(dx,dy); lum-=0.35*np.exp(-(d/0.05)**2); lum+=0.08*np.sin(d*120)*np.exp(-(d/0.12)**2)
lum=np.clip(lum,0.15,1.0)
dark=np.array([0.20,0.12,0.07]); mid=np.array([0.46,0.30,0.17]); light=np.array([0.66,0.47,0.28])
L=lum[...,None]
col=np.where(L<0.6, dark+(mid-dark)*(L/0.6), mid+(light-mid)*((L-0.6)/0.4))
col*= (0.93+0.1*tnoise(S,3,20,1.0,49))[...,None]   # large-scale colour drift
img=bpy.data.images["T_VK_Wood"]
if img.size[0]!=S:
    img.scale(S,S)
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel())
img.filepath_raw=os.path.join(out,"VillageKit","Textures","T_VK_Wood.png"); img.file_format="PNG"; img.save(); img.pack()
print(img.size[:])
# ---- result ----
# {"result":"Code executed successfully: (1024, 1024)\n"}

# ==============================================================================================================
# [0121] 2026-09-23 03:00:36  blender  ok
# ==============================================================================================================
import bpy, numpy as np
def tnoise(S,fmax,n,decay,seed,fy_max=None):
    r=np.random.default_rng(seed); y,x=np.mgrid[0:S,0:S]/S; acc=np.zeros((S,S))
    for _ in range(n):
        fx=r.integers(0,fmax+1); fy=r.integers(0,(fy_max if fy_max is not None else fmax)+1)
        if fx==0 and fy==0: fx=1
        acc+=np.sin(2*np.pi*(fx*x+fy*y)+r.uniform(0,6.28))/((fx+fy)**decay)
    return acc/np.abs(acc).max()
S=1024; y,x=np.mgrid[0:S,0:S]/S
warp=tnoise(S,2,30,0.9,41,fy_max=3)*0.04
g1=np.sin(2*np.pi*(y*7+warp*4))
g2=np.sin(2*np.pi*(y*23+warp*9+tnoise(S,3,30,0.8,43,fy_max=3)*0.25))
strokes=tnoise(S,2,80,0.5,44,fy_max=60)
lum=0.60+0.13*g1+0.06*g2+0.16*strokes
lines=np.abs(np.sin(2*np.pi*(y*11+warp*6)))
lum-=0.20*np.clip(1-lines/0.04,0,1)*(0.6+0.4*np.clip(tnoise(S,3,20,1,50),0,1))
# cracks along grain: thin horizontal splits that fade in and out along x
for i,(yc,seed) in enumerate(((0.18,51),(0.47,52),(0.81,53))):
    yy=yc+warp*1.5+0.006*np.sin(2*np.pi*x*3+i)
    d=np.abs(((y-yy+0.5)%1)-0.5)*S
    gate=np.clip(tnoise(S,2,10,1.0,seed,fy_max=0)*1.5,0,1)
    lum-=0.35*np.clip(1-d/2.2,0,1)*gate
    lum+=0.10*np.clip(1-np.abs(d-3.5)/1.5,0,1)*gate      # lit lip under the crack
rng=np.random.default_rng(48)
for kx,ky in rng.uniform(0,1,(3,2)):
    dx=((x-kx+0.5)%1-0.5)*2.2; dy=((y-ky+0.5)%1-0.5)*6
    d=np.hypot(dx,dy); lum-=0.35*np.exp(-(d/0.045)**2); lum+=0.07*np.sin(d*110)*np.exp(-(d/0.11)**2)
lum=np.clip(lum,0.12,1.0)
dark=np.array([0.19,0.11,0.06]); mid=np.array([0.45,0.29,0.16]); light=np.array([0.68,0.49,0.29])
L=lum[...,None]
col=np.where(L<0.6, dark+(mid-dark)*(L/0.6), mid+(light-mid)*((L-0.6)/0.4))
col*= (0.93+0.1*tnoise(S,3,20,1.0,49))[...,None]
img=bpy.data.images["T_VK_Wood"]
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel())
img.save(); img.pack()
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0122] 2026-09-23 03:00:57  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
old_start=s.index("    def project(s,faces,mi,axes=None,sizes=None):")
old_end=s.index("    def quad(s,pts,mi,uvs=None):")
new=r'''    def project(s,faces,mi,axes=None,sizes=None,offset=(0.0,0.0)):
        t=TILE.get(mi,1.0)
        for f in faces:
            if not f.is_valid: continue
            f.material_index=mi
            n=f.normal
            if mi in (WOOD,SHUTTER) and axes:
                cand=[(sz,ax) for ax,sz in zip(axes,sizes) if abs(ax.dot(n))<0.8]
                cand.sort(key=lambda a:-a[0])
                if cand:
                    U=cand[0][1]; V=n.cross(U).normalized()
                else:
                    U=axes[0]; V=n.cross(U).normalized()
            elif abs(n.z)>0.7: U=Vector((1,0,0)); V=Vector((0,1,0))
            else:
                U=n.cross(Vector((0,0,1))); U.normalize(); V=Vector((0,0,1))
            for l in f.loops:
                p=l.vert.co; l[s.uv].uv=(p.dot(U)/t+offset[0],p.dot(V)/t+offset[1])
    def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0,xform=None):
        r=bmesh.ops.create_cube(s.bm,size=1.0); vs=r["verts"]
        R=Matrix.Rotation(rot[2],4,"Z")@Matrix.Rotation(rot[1],4,"Y")@Matrix.Rotation(rot[0],4,"X")
        M=Matrix.Translation(Vector(center))@R@Matrix.Diagonal((*size,1))
        if xform is not None: M=xform@M; R=xform.to_3x3().to_4x4()@R
        bmesh.ops.transform(s.bm,matrix=M,verts=vs)
        if jitter:
            rnd=random.Random(seed)
            for v in vs: v.co+=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1)))*jitter
        faces=list({f for v in vs for f in v.link_faces})
        for f in faces: f.material_index=mi
        if bevel>0:
            edges=list({e for v in vs for e in v.link_edges})
            res=bmesh.ops.bevel(s.bm,geom=edges+vs,offset=min(bevel,min(size)*0.45),segments=segs,profile=0.5,affect="EDGES",clamp_overlap=True)
            faces=[f for f in faces if f.is_valid]+list(res["faces"])
            for f in faces: f.material_index=mi
        s.bm.normal_update()
        axes=[(R@Vector(a)).normalized() for a in ((1,0,0),(0,1,0),(0,0,1))]
        c=Vector(center) if xform is None else xform@Vector(center)
        h=abs(hash((round(c.x,2),round(c.y,2),round(c.z,2))))
        s.project(faces,mi,axes,size,offset=((h%997)/997.0,(h//997%991)/991.0))
        return [v for f in faces for v in f.verts]
'''
s=s[:old_start]+new+s[old_end:]
t.clear(); t.write(s); exec(s)
for mn in ["M_VK_Wood","M_VK_Planks","M_VK_Shutter_Teal"]+[m.name for m in bpy.data.materials if m.name.startswith("M_VK_Shutter_")]:
    m=bpy.data.materials.get(mn)
    if not m: continue
    b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    b.inputs["Roughness"].default_value=0.95; b.inputs["Specular IOR Level"].default_value=0.12
for mn in ("M_VK_Stone","M_VK_Plaster","M_VK_Ashlar","M_VK_Thatch"):
    b=next(n for n in bpy.data.materials[mn].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Specular IOR Level"].default_value=0.2
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0123] 2026-09-23 03:01:24  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def all_specs():
    nw=dict(wobble=False,grime=False); ng=dict(wobble=False,grime=True)
    return [
     ("SM_VK_Wall_Stone",wall_stone_plain,{}),("SM_VK_Wall_Stone_Window",wall_stone_window,{}),("SM_VK_Wall_Stone_Door",wall_stone_door,{}),
     ("SM_VK_Corner_Stone",corner_stone,{"wobble":False}),
     ("SM_VK_Wall_Plaster",lambda k: plaster_ground(k,"."),{}),("SM_VK_Wall_Plaster_Window",lambda k: plaster_ground(k,"W"),{}),
     ("SM_VK_Wall_Plaster_Door",lambda k: plaster_ground(k,"D"),{}),("SM_VK_Corner_Plaster",corner_plaster,{"wobble":False}),
     ("SM_VK_Wall_Timber",timber_frame,{"grime":False}),("SM_VK_Wall_Timber_X",lambda k: timber_frame(k,False,"X"),{"grime":False}),
     ("SM_VK_Wall_Timber_K",lambda k: timber_frame(k,False,"K"),{"grime":False}),("SM_VK_Wall_Timber_Window",lambda k: timber_frame(k,True),{"grime":False}),
     ("SM_VK_Corner_Timber",corner_timber,nw),
     ("SM_VK_InnerCorner_Stone",inner_corner_stone,{"wobble":False}),("SM_VK_InnerCorner_Plaster",inner_corner_plaster,{"wobble":False}),
     ("SM_VK_InnerCorner_Timber",inner_corner_timber,nw),
     ("SM_VK_Roof_Mid",roof_mid,nw),("SM_VK_Roof_Gable",roof_gable,nw),("SM_VK_Roof_LCorner",roof_L_corner,nw),
     ("SM_VK_Roof_Dormer",dormer,nw),("SM_VK_Porch",porch,nw),("SM_VK_Chimney",chimney,nw),
     ("SM_VK_Prop_FlowerBox",prop_flowerbox,nw),("SM_VK_Prop_Lantern",prop_lantern,nw),("SM_VK_Prop_Sign",prop_sign,nw),
     ("SM_VK_MarketStall",market_stall,ng),("SM_VK_Prop_Well",prop_well,ng),("SM_VK_Prop_Fence",prop_fence,ng),
     ("SM_VK_Prop_FenceGate",prop_fence_gate,ng),("SM_VK_Prop_Cart",prop_cart,ng),("SM_VK_Prop_LampPost",prop_lamppost,ng),
     ("SM_VK_Prop_Bench",prop_bench,ng),("SM_VK_Prop_Crates",prop_crates,ng),("SM_VK_Prop_GardenBed",prop_garden_bed,nw),
     ("SM_VK_Prop_Table",prop_table,ng),("SM_VK_Prop_Stool",prop_stool,ng),("SM_VK_Prop_Trough",prop_trough,ng),
     ("SM_VK_Prop_HayBale",prop_haybale,ng),("SM_VK_Prop_Haystack",prop_haystack,ng),("SM_VK_Prop_Woodpile",prop_woodpile,ng),
     ("SM_VK_Prop_NoticeBoard",prop_noticeboard,ng),("SM_VK_Prop_Signpost",prop_signpost,ng),("SM_VK_Prop_Anvil",prop_anvil,ng),
     ("SM_VK_Prop_Grindstone",prop_grindstone,ng),("SM_VK_Prop_Sacks",prop_sacks,ng),("SM_VK_Prop_WeaponRack",prop_weaponrack,ng),
     ("SM_VK_Prop_BarrelStack",prop_barrelstack,ng),("SM_VK_Prop_Forge",prop_bellows_forge,ng)] + EXTRA_SPECS
EXTRA_SPECS=[]
def full_rebuild(names=None):
    """rebuild kit meshes in place (same mesh datablock) so every instance and variant updates"""
    old_var={}   # VAR mesh -> base piece name
    for o in bpy.data.objects:
        if o.data and o.data.name.startswith("VAR_") and "_inst" in o.name:
            old_var[o.data.name]=o.name.split("_inst")[0]
    specs=[sp for sp in all_specs() if names is None or sp[0] in names]
    for n,fn,kw in specs:
        k=Kit(); fn(k)
        for f in k.bm.faces:
            if all(l[k.uv].uv.length==0 for l in f.loops): k.project([f],f.material_index)
        tmp=k.finish("__tmp__",vcol("VK_Pieces"),**kw)
        for p in tmp.data.polygons: p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP)
        base=bpy.data.objects.get(n)
        if base is None:
            tmp.name=n; tmp.data.name=n; tmp.hide_render=tmp.hide_viewport=True; continue
        me=base.data
        # copy geometry into the existing datablock (keeps all links)
        import bmesh as _b
        bm=_b.new(); bm.from_mesh(tmp.data); bm.to_mesh(me); bm.free()
        mats=list(tmp.data.materials)
        while len(me.materials)<len(mats): me.materials.append(mats[len(me.materials)])
        for i,m in enumerate(mats): me.materials[i]=m
        tmd=tmp.data; bpy.data.objects.remove(tmp); bpy.data.meshes.remove(tmd)
    # refresh variant meshes: copy geometry from base, keep their material overrides
    for vname,piece in old_var.items():
        vm=bpy.data.meshes.get(vname); base=bpy.data.objects.get(piece)
        if not vm or not base: continue
        if names is not None and piece not in names: continue
        keep=[vm.materials[i] for i in range(len(vm.materials))]
        bm=bmesh.new(); bm.from_mesh(base.data); bm.to_mesh(vm); bm.free()
        basem=list(base.data.materials)
        while len(vm.materials)<len(basem): vm.materials.append(basem[len(vm.materials)])
        for i in range(len(basem)):
            base_default=basem[i]
            vm.materials[i]=keep[i] if i<len(keep) and keep[i] is not None and keep[i]!=base_default and i in SLOT.values() else base_default
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
full_rebuild()
print("rebuilt")
# ---- result ----
# {"result":"Code executed successfully: rebuilt\n"}

# ==============================================================================================================
# [0124] 2026-09-23 03:01:38  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
for c in ("VK_Demo","VK_Village"):
    for o in bpy.data.collections[c].objects: o.hide_render=False
for o in bpy.data.collections["VK_Test"].objects: o.hide_render=True
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cc=bpy.data.objects["VK_CameraClose"]; cc.data.lens=35
# house at (3,15.5) faces -Y (plaza); look at its upper floor
tgt=Vector((1,12.2,3.6)); cc.location=Vector((6.5,6.5,3.0))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0125] 2026-09-23 03:01:48  blender  ok
# ==============================================================================================================
import bpy
for img in bpy.data.images:
    if img.source=="FILE" and not img.packed_file and img.has_data:
        try: img.pack()
        except: pass
bpy.ops.wm.save_mainfile()
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n"}

# ==============================================================================================================
# [0126] 2026-09-23 03:02:07  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["vk_helpers"].as_string()
a=s.index("def gable_end(k):"); b=s.index("def chimney(k):")
print(s[a:b])
# ---- result ----
# {"result":"Code executed successfully: def gable_end(k):\n # bargeboards following both slopes\n prof=roof_profile()\n for s in(-1,1):\n for j in rang
# e(len(prof)-1):\n (y0,z0),(y1,z1)=prof[j],prof[j+1]\n L=math.hypot(y1-y0,z1-z0); ang=math.atan2(z1-z0,y1-y0)\n yc=s*(y0+y1)/2; zc=(z0+z1)/2-0.16\n k.b
# ox((GX+0.08,yc,zc),(0.2,L+0.2,0.46),WOOD,rot=(s*ang,0,0),bevel=0.05,segs=2)\n # finial\n k.box((GX+0.08,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,se
# gs=2)\n k.box((GX+0.08,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)\n # gable triangle wall (timber framed plaster), face at
#  x=+1.5+0.40, follows the roof underside exactly\n XF=1.5+0.40; XB=1.5-0.05\n def under(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.05\n YC=HALF+0.02\
# n ys=[YC,2.5,2.0,1.5,1.0,0.5,0.0]\n outline=[(-YC,0.0),(YC,0.0)]+[(y,under(y)) for y in ys]+[(-y,under(y)) for y in ys[::-1][1:]]\n for (xf,flip) in (

# ==============================================================================================================
# [0127] 2026-09-23 03:02:35  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("def gable_end(k):","def gable_end(k,kind='timber'):")
s=s.replace('''    XF=1.5+0.40; XB=1.5-0.05
    def under(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.05''','''    XF={"timber":1.5+0.40,"stone":1.5+0.30,"planks":1.5+0.26}[kind]; XB=1.5-0.05
    TRI={"timber":PLASTER,"stone":ASHLAR,"planks":PLANKS}[kind]
    def under(ay): return roof_z(ay)-RT/math.cos(PITCH)-0.05''')
s=s.replace('''        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=PLASTER
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[PLASTER],l.vert.co.z/TILE[PLASTER])
    k.bm.normal_update()
    top=under(0)''','''        f=k.bm.faces.new(vs if not flip else vs[::-1]); f.material_index=TRI
        for l in f.loops: l[k.uv].uv=(l.vert.co.y/TILE[TRI],l.vert.co.z/TILE[TRI])
    k.bm.normal_update()
    top=under(0)
    if kind!="timber":
        gable_special(k,kind,XF,top,YC); return''')
code=r'''
def gable_special(k,kind,XF,top,YC):
    if kind=="stone":
        # coping stones along the rake
        for s_ in(-1,1):
            L=math.hypot(YC,top); ang=math.atan2(top,YC); n=7
            for i in range(n):
                t_=(i+0.5)/n; y=s_*YC*(1-t_); z=top*t_
                k.box((XF+0.05,y,z+0.05),(0.3,L/n-0.04,0.32),ASHLAR,rot=(-s_*ang,0,0),bevel=0.05,segs=2)
        # rose window
        zc=top*0.42; R=0.75; n=12
        vs=[k.bm.verts.new((XF-0.03,math.cos(2*math.pi*i/n)*R,zc+math.sin(2*math.pi*i/n)*R)) for i in range(n)]
        c=k.bm.verts.new((XF-0.03,0,zc))
        for i in range(n):
            f=k.bm.faces.new((c,vs[i],vs[(i+1)%n]) ); f.material_index=STAINED
        for i in range(n):
            a=2*math.pi*(i+0.5)/n
            k.box((XF+0.02,math.cos(a)*(R+0.12),zc+math.sin(a)*(R+0.12)),(0.22,0.42,0.26),ASHLAR,rot=(a,0,0),bevel=0.04)
        for i in range(6):
            a=math.pi*i/6; k.box((XF,0,zc),(0.06,0.06,2*R),IRON,rot=(a,0,0),bevel=0)
        k.box((XF+0.02,0,0.12),(0.3,2*YC,0.26),ASHLAR,bevel=0.04)
    else:  # planks: battens, hayloft door, hoist beam, hay
        for y in(-2.2,-1.1,1.1,2.2):
            h=top*(1-abs(y)/YC)-0.1
            k.box((XF+0.03,y,h/2),(0.08,0.14,h),WOOD,bevel=0.02)
        k.box((XF+0.02,0,0.12),(0.2,2*YC,0.22),WOOD,bevel=0.03)
        zd=0.35; hd=1.7
        k.quad([(XF-0.02,-0.7,zd),(XF-0.02,0.7,zd),(XF-0.02,0.7,zd+hd),(XF-0.02,-0.7,zd+hd)],IRON,uvs=[(0,0),(1,0),(1,1),(0,1)])
        # one door leaf swung open
        k.box((XF+0.45,-0.72,zd+hd/2),(0.9,0.08,hd),PLANKS,rot=(0,0,-1.2),bevel=0.02)
        for zz in(zd,zd+hd): k.box((XF+0.03,0,zz),(0.14,1.6,0.14),WOOD,bevel=0.03)
        for yy in(-0.78,0.78): k.box((XF+0.03,yy,zd+hd/2),(0.14,0.14,hd+0.1),WOOD,bevel=0.03)
        k.box((XF+0.1,0,zd+0.2),(0.5,1.2,0.35),HAY,bevel=0.1,segs=2,jitter=0.04,seed=3)
        k.box((XF+0.6,0,top-0.35),(1.4,0.18,0.2),WOOD,bevel=0.03)
        k.box((XF+1.2,0,top-0.75),(0.02,0.02,0.7),WOOD,bevel=0)
        _cyl(k,(XF+1.2,0,top-0.45),0.1,0.1,0.06,8,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
def roof_gable_kind(kind):
    def fn(k):
        for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True))
        ridge(k,-1.5,GX+0.1); gable_end(k,kind)
    return fn
EXTRA_SPECS+= [("SM_VK_Roof_Gable_Stone",roof_gable_kind("stone"),dict(wobble=False,grime=False)),
               ("SM_VK_Roof_Gable_Planks",roof_gable_kind("planks"),dict(wobble=False,grime=False))]
'''
t.clear(); t.write(s+code); exec(t.as_string())
full_rebuild(["SM_VK_Roof_Gable_Stone","SM_VK_Roof_Gable_Planks","SM_VK_Roof_Gable","SM_VK_Roof_LCorner"])
print([o.name for o in bpy.data.objects if o.name.startswith("SM_VK_Roof_Gable")])
# ---- result ----
# {"result":"Code executed successfully: ['SM_VK_Roof_Gable', 'SM_VK_Roof_Gable_inst', 'SM_VK_Roof_Gable_inst.001', 'SM_VK_Roof_Gable_inst.002', 'SM_VK_
# Roof_Gable_inst.003', 'SM_VK_Roof_Gable_inst.004', 'SM_VK_Roof_Gable_inst.005', 'SM_VK_Roof_Gable_inst.006', 'SM_VK_Roof_Gable_inst.007', 'SM_VK_Roof_
# Gable_inst.008', 'SM_VK_Roof_Gable_inst.009', 'SM_VK_Roof_Gable_inst.010', 'SM_VK_Roof_Gable_inst.011', 'SM_VK_Roof_Gable_inst.012', 'SM_VK_Roof_Gable
# _inst.013', 'SM_VK_Roof_Gable_inst.014', 'SM_VK_Roof_Gable_inst.015', 'SM_VK_Roof_Gable_inst.016', 'SM_VK_Roof_Gable_inst.017', 'SM_VK_Roof_Gable_inst
# .018', 'SM_VK_Roof_Gable_inst.019', 'SM_VK_Roof_Gable_inst.020', 'SM_VK_Roof_Gable_inst.021', 'SM_VK_Roof_Gable_inst.022', 'SM_VK_Roof_Gable_inst.023'
# , 'SM_VK_Roof_Gable_inst.024', 'SM_VK_Roof_Gable_inst.025', 'SM_VK_Roof_Gable_inst.026', 'SM_VK_Roof_Gable_inst.027', 'SM_VK_Roof_Gable_inst.028', 'SM

# ==============================================================================================================
# [0128] 2026-09-23 03:03:31  blender  ok
# ==============================================================================================================
import bpy
code=r'''
HC=4.5
def lancet_pts(x0,x1,z0,zs,n=6):
    """pointed arch outline: rectangle x0..x1 from z0 to spring zs, then two arcs meeting at apex"""
    w=x1-x0; r=w*0.85; pts=[(x0,z0),(x1,z0),(x1,zs)]
    cxL=x1-r; cxR=x0+r
    apex_z=zs+math.sqrt(r*r-(w/2 - (x1-cxL-r)+ (r-w/2))**2) if False else None
    # right arc centred at x0+r? use standard equilateral-ish arch
    cL=x0+r; cR=x1-r
    xa=(x0+x1)/2; za=zs+math.sqrt(max(r*r-(xa-cR)**2,0))
    for i in range(1,n):
        t=i/n; x=x1+(xa-x1)*t; pts.append((x,zs+math.sqrt(max(r*r-(x-cR)**2,0))))
    pts.append((xa,za))
    for i in range(1,n):
        t=i/n; x=xa+(x0-xa)*t; pts.append((x,zs+math.sqrt(max(r*r-(x-cL)**2,0))))
    pts.append((x0,zs))
    return pts,za
def chapel_wall(k,kind="W"):
    stone_panel(k,-1.5,1.5,0,HC,-0.3,0.3,mi=ASHLAR)
    k.box((0,-0.05,0.25),(CELL,0.8,0.5),ASHLAR,bevel=0.04)                  # plinth
    k.box((0,-0.34,HC-0.15),(CELL,0.2,0.3),ASHLAR,bevel=0.05,segs=2)        # cornice
    # buttress at the left edge (right edge belongs to the neighbour / corner)
    for (z0,z1,d) in ((0,2.2,0.9),(2.2,3.6,0.65)):
        k.box((-1.5,-0.3-d/2,(z0+z1)/2),(0.6,d,z1-z0),ASHLAR,bevel=0.05,segs=2)
    k.box((-1.5,-0.55,3.75),(0.6,0.5,0.4),ASHLAR,rot=(0.6,0,0),bevel=0.05)
    if kind=="W":
        x0,x1,z0,zs=-0.45,0.45,1.3,3.1
        pts,za=lancet_pts(x0,x1,z0,zs)
        vs=[k.bm.verts.new((x,-0.33,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=STAINED
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
        # lead cames
        k.box((0,-0.35,(z0+za)/2),(0.05,0.03,za-z0),IRON,bevel=0)
        for zz in(1.9,2.5): k.box((0,-0.35,zz),(x1-x0,0.03,0.05),IRON,bevel=0)
        # voussoir frame
        for i in range(len(pts)-1):
            (xa,za_),(xb,zb)=pts[i],pts[i+1]
            if zb<=z0+0.01 and za_<=z0+0.01: continue
            mx,mz=(xa+xb)/2,(za_+zb)/2; L=math.hypot(xb-xa,zb-za_); ang=math.atan2(zb-za_,xb-xa)
            nx,nz=-(zb-za_)/L,(xb-xa)/L
            k.box((mx-nx*0.1,-0.36,mz-nz*0.1),(L+0.05,0.12,0.22),ASHLAR,rot=(0,-ang,0),bevel=0.03)
        k.box((0,-0.42,z0-0.08),(1.2,0.3,0.16),ASHLAR,bevel=0.04)
    elif kind=="D":
        x0,x1,z0,zs=-0.8,0.8,0.0,2.2
        pts,za=lancet_pts(x0,x1,z0,zs,8)
        vs=[k.bm.verts.new((x,-0.33,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=PLANKS
        for l in f.loops: l[k.uv].uv=(l.vert.co.x/2,l.vert.co.z/2)
        k.box((0,-0.36,(za)/2),(0.06,0.05,za),WOOD,bevel=0)
        for zz in(0.5,1.6):
            for s_ in(-1,1): k.box((s_*0.45,-0.37,zz),(0.6,0.03,0.09),IRON,bevel=0.01)
        for s_ in(-1,1): _cyl(k,(s_*0.15,-0.4,1.1),0.07,0.07,0.03,8,IRON,rot=Matrix.Rotation(math.pi/2,4,"X"))
        for ring in range(3):
            off=0.14+ring*0.2
            for i in range(len(pts)-1):
                (xa,za_),(xb,zb)=pts[i],pts[i+1]
                if abs(zb-za_)<1e-4 and zb<0.01: continue
                mx,mz=(xa+xb)/2,(za_+zb)/2; L=math.hypot(xb-xa,zb-za_); ang=math.atan2(zb-za_,xb-xa)
                nx,nz=-(zb-za_)/L,(xb-xa)/L
                k.box((mx-nx*off,-0.36-ring*0.07,mz-nz*off),(L+0.06,0.14,0.2),ASHLAR,rot=(0,-ang,0),bevel=0.03)
        k.box((0,-0.8,0.08),(2.6,1.0,0.16),ASHLAR,bevel=0.04)
def chapel_corner(k):
    k.box((0,0,HC/2),(0.9,0.9,HC),ASHLAR,bevel=0.05,segs=2)
    k.box((0,0,0.25),(1.05,1.05,0.5),ASHLAR,bevel=0.04)
    for (z0,z1,d) in ((0,2.4,1.1),(2.4,3.8,0.8)):
        k.box((-0.35-d/2+0.45,-0.35-d/2+0.45,(z0+z1)/2),(d,d,z1-z0),ASHLAR,rot=(0,0,0),bevel=0.05,segs=2)
    k.box((-0.05,-0.05,HC-0.15),(1.0,1.0,0.3),ASHLAR,bevel=0.05,segs=2)
    k.box((0,0,HC+0.7),(0.35,0.35,1.2),ASHLAR,bevel=0.05,segs=2)
    _cyl(k,(0,0,HC+1.55),0.28,0.0,0.6,4,ASHLAR,rot=Matrix.Rotation(math.pi/4,4,"Z"))
def bell_tower(k):
    """square tower 3.6m, local origin at its base centre; front (door side) toward -Y"""
    W=3.6; h1=8.0; hb=3.0
    stone_panel(k,-W/2,W/2,0,h1,-W/2,W/2,mi=ASHLAR)
    k.box((0,0,0.3),(W+0.3,W+0.3,0.6),ASHLAR,bevel=0.05,segs=2)
    for zz in(3.5,h1): k.box((0,0,zz),(W+0.24,W+0.24,0.28),ASHLAR,bevel=0.05,segs=2)
    for sx in(-1,1):
        for sy in(-1,1):
            k.box((sx*(W/2+0.05),sy*(W/2+0.05),(h1)/2),(0.5,0.5,h1),ASHLAR,bevel=0.05,segs=2)
    # slit windows
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z")
        sub=Kit(); sub.box((0,-W/2-0.02,5.5),(0.18,0.06,1.1),IRON,bevel=0); merge_kit(k,sub,R)
    # belfry: 4 open arches (pillars + lintels), bell inside
    z0=h1+0.14
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(W/2-0.3),sy*(W/2-0.3),z0+hb/2),(0.6,0.6,hb),ASHLAR,bevel=0.05,segs=2)
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z")
        sub=Kit()
        sub.box((0,-W/2+0.3,z0+hb-0.25),(W,0.6,0.5),ASHLAR,bevel=0.05,segs=2)
        sub.box((0,-W/2+0.3,z0+0.35),(W,0.6,0.25),ASHLAR,bevel=0.04)
        n=7
        for i in range(n):
            ang=math.pi*(i+0.5)/n; r=(W-1.2)/2
            sub.box((math.cos(ang)*r,-W/2+0.3,z0+hb-0.7-r+math.sin(ang)*r*0.9),(0.4,0.6,0.25),ASHLAR,rot=(0,-(ang-math.pi/2),0),bevel=0.03)
        merge_kit(k,sub,R)
    k.box((0,0,z0+0.1),(W-0.2,W-0.2,0.2),WOOD,bevel=0.03)
    # bell + yoke
    k.box((0,0,z0+hb-0.9),(2.6,0.25,0.25),WOOD,bevel=0.04)
    vs=_cyl(k,(0,0,z0+hb-1.55),0.62,0.3,1.0,16,BRONZE)
    _cyl(k,(0,0,z0+hb-2.08),0.66,0.66,0.1,16,BRONZE)
    _ico(k,(0,0,z0+hb-1.95),0.12,IRON)
    # spire
    zs=z0+hb
    k.box((0,0,zs+0.15),(W+0.4,W+0.4,0.3),ASHLAR,bevel=0.05,segs=2)
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=8,radius1=(W+0.5)/2*1.08,radius2=0.05,depth=6.5)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zs+0.3+3.25))@Matrix.Rotation(math.pi/8,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces})
    for f in fs: f.material_index=ROOF
    k.bm.normal_update()
    for f in fs:
        n=f.normal; 
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized(); 
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],(p.z-zs)/TILE[ROOF]*1.2)
    # small lucarnes on spire
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-1.35,zs+1.4),(0.6,0.5,0.9),WOOD,bevel=0.03)
        sub.quad([(-0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.7),(-0.2,-1.61,zs+1.7)],IRON,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for sx in(-1,1): sub.box((sx*0.2,-1.4,zs+2.0),(0.55,0.7,0.07),ROOF,rot=(0,sx*0.8,0),bevel=0.02)
        merge_kit(k,sub,R)
    # cross + weathervane
    top=zs+0.3+6.5
    k.box((0,0,top+0.5),(0.1,0.1,1.2),BRONZE,bevel=0.02)
    k.box((0,0,top+0.75),(0.6,0.1,0.1),BRONZE,bevel=0.02)
    # door
    x0,x1=-0.6,0.6; pts,za=lancet_pts(x0,x1,0,1.9,6)
    vs=[k.bm.verts.new((x,-W/2-0.02,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=PLANKS
    for l in f.loops: l[k.uv].uv=(l.vert.co.x/2,l.vert.co.z/2)
    for i in range(len(pts)-1):
        (xa,za_),(xb,zb)=pts[i],pts[i+1]
        if zb<0.01 and za_<0.01: continue
        mx,mz=(xa+xb)/2,(za_+zb)/2; L=math.hypot(xb-xa,zb-za_); ang=math.atan2(zb-za_,xb-xa); nx,nz=-(zb-za_)/L,(xb-xa)/L
        k.box((mx-nx*0.12,-W/2-0.05,mz-nz*0.12),(L+0.06,0.14,0.24),ASHLAR,rot=(0,-ang,0),bevel=0.03)
EXTRA_SPECS+= [("SM_VK_Chapel_Wall",lambda k: chapel_wall(k,"W"),dict(wobble=False,grime=True)),
               ("SM_VK_Chapel_Wall_Plain",lambda k: chapel_wall(k,"."),dict(wobble=False,grime=True)),
               ("SM_VK_Chapel_Wall_Door",lambda k: chapel_wall(k,"D"),dict(wobble=False,grime=True)),
               ("SM_VK_Chapel_Corner",chapel_corner,dict(wobble=False,grime=True)),
               ("SM_VK_BellTower",bell_tower,dict(wobble=False,grime=True))]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
full_rebuild(["SM_VK_Chapel_Wall","SM_VK_Chapel_Wall_Plain","SM_VK_Chapel_Wall_Door","SM_VK_Chapel_Corner","SM_VK_BellTower"])
for n in ["SM_VK_Chapel_Wall","SM_VK_Chapel_Wall_Door","SM_VK_Chapel_Corner","SM_VK_BellTower"]: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Chapel_Wall 735\nSM_VK_Chapel_Wall_Door 1835\nSM_VK_Chapel_Corner 301\nSM_VK_BellTower 2909\n"}

# ==============================================================================================================
# [0129] 2026-09-23 03:03:54  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def build_chapel(coll,origin,n=4,roof="Blue",tower=True):
    L=n*CELL; st={"roof":roof}
    for i in range(n):
        x=-L/2+1.5+3*i
        place_v(coll,"SM_VK_Chapel_Wall",x,-3,0,0,origin,st)
        place_v(coll,"SM_VK_Chapel_Wall" if i!=1 else "SM_VK_Chapel_Wall_Door",x,3,0,180,origin,st)
    for yy in(-1.5,1.5):
        place_v(coll,"SM_VK_Chapel_Wall_Plain",-L/2,yy,0,-90,origin,st)
        place_v(coll,"SM_VK_Chapel_Wall_Plain",L/2,-yy,0,90,origin,st)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
        place_v(coll,"SM_VK_Chapel_Corner",cx,cy,0,r,origin,st)
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==0: place_v(coll,"SM_VK_Roof_Gable_Stone",x,0,HC,180,origin,st)
        elif i==n-1: place_v(coll,"SM_VK_Roof_Gable_Stone",x,0,HC,0,origin,st)
        else: place_v(coll,"SM_VK_Roof_Mid",x,0,HC,0,origin,st)
    if tower: place_v(coll,"SM_VK_BellTower",L/2+2.2,0,0,90,origin,st)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
S=vcol("VK_Showcase")
for o in list(S.objects): bpy.data.objects.remove(o)
for c in ("VK_Demo","VK_Village","VK_Test"):
    for o in vcol(c).objects: o.hide_render=True
build_chapel(S,(0,-170,0))
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((2,-170,5)); cs.location=tgt+Vector((14,-22,8))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0130] 2026-09-23 03:04:14  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
S=512; y,x=np.mgrid[0:S,0:S]/S
a=(x+y)*5; b=(x-y)*5
ia=np.floor(a).astype(int); ib=np.floor(b).astype(int)
lead=np.minimum(np.minimum(np.abs(a-np.round(a)),np.abs(b-np.round(b))),1)
pal=np.array([(0.75,0.10,0.10),(0.10,0.25,0.75),(0.85,0.65,0.10),(0.10,0.55,0.25),(0.55,0.15,0.60),(0.15,0.45,0.75)])
h=(ia*7+ib*13)%len(pal)
col=pal[h]
fa=(a%1); fb=(b%1)
col=col*(0.75+0.35*(1-np.abs(fa-0.5)*1.2)[...,None]*(1-np.abs(fb-0.5)*1.2)[...,None])
col=np.where((lead<0.05)[...,None],np.array([0.05,0.05,0.06]),col)
img=bpy.data.images.get("T_VK_Stained")
if img: bpy.data.images.remove(img)
img=bpy.data.images.new("T_VK_Stained",S,S,alpha=True)
img.pixels.foreach_set(np.ascontiguousarray(np.dstack([np.clip(col,0,1),np.ones((S,S))])[::-1]).astype(np.float32).ravel())
img.filepath_raw=os.path.join(out,"VillageKit","Textures","T_VK_Stained.png"); img.file_format="PNG"; img.save(); img.pack()
m=bpy.data.materials["M_VK_Stained"]; nt=m.node_tree
b_=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"); mix=next(n for n in nt.nodes if n.type=="MIX")
tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=img
nt.links.new(tx.outputs[0],mix.inputs[6]); nt.links.new(tx.outputs[0],b_.inputs["Emission Color"])
b_.inputs["Emission Strength"].default_value=1.2
SC=bpy.data.scenes["VillageKit"]
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0131] 2026-09-23 03:04:50  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("vs=[k.bm.verts.new((x,-0.33,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=STAINED\n        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)",
            "vs=[k.bm.verts.new((x,-0.33,z)) for x,z in pts]; f=k.bm.faces.new(vs[::-1]); f.material_index=STAINED\n        for l in f.loops: l[k.uv].uv=(l.vert.co.x*0.55,l.vert.co.z*0.55)")
t.clear(); t.write(s)
code=r'''
HB=4.2
# ---------------- barn
def barn_wall(k,kind="."):
    stone_panel(k,-1.5,1.5,0,0.7,-0.3,0.2); plinth(k)
    grid_cut(k,k.box((0,-0.02,(0.7+HB)/2),(CELL,0.36,HB-0.7),PLANKS,bevel=0))
    k.box((0,-0.24,0.8),(CELL,0.2,0.2),WOOD,bevel=0.03); k.box((0,-0.24,HB-0.12),(CELL,0.22,0.24),WOOD,bevel=0.03)
    k.box((-1.5,-0.26,(0.7+HB)/2),(0.26,0.22,HB-0.7),WOOD,bevel=0.04)
    if kind==".":
        k.box((0,-0.26,2.4),(CELL,0.18,0.16),WOOD,bevel=0.03)
        brace(k,-1.35,0.9,-0.2,2.3,y=-0.27); brace(k,1.35,0.9,0.2,2.3,y=-0.27)
        # small window slot
        k.quad([(-0.4,-0.21,2.9),(0.4,-0.21,2.9),(0.4,-0.21,3.5),(-0.4,-0.21,3.5)],IRON,uvs=[(0,0),(1,0),(1,1),(0,1)])
        for x in(-0.2,0,0.2): k.box((x,-0.25,3.2),(0.05,0.05,0.62),WOOD,bevel=0)
        k.box((0,-0.26,2.85),(1.0,0.12,0.12),WOOD,bevel=0.02); k.box((0,-0.26,3.55),(1.0,0.12,0.12),WOOD,bevel=0.02)
    elif kind=="D":
        hw=1.25; hd=3.3
        k.quad([(-hw,-0.21,0.05),(hw,-0.21,0.05),(hw,-0.21,hd),(-hw,-0.21,hd)],IRON,uvs=[(0,0),(1,0),(1,1),(0,1)])
        k.box((0,-0.28,hd+0.12),(2*hw+0.5,0.26,0.26),WOOD,bevel=0.04)
        for s_ in(-1,1): k.box((s_*(hw+0.12),-0.28,hd/2),(0.24,0.26,hd),WOOD,bevel=0.04)
        # left leaf closed, right leaf swung open
        def leaf(xform):
            sub=Kit()
            sub.box((hw/2,0,hd/2),(hw-0.04,0.12,hd-0.1),PLANKS,bevel=0.02)
            for zz in(0.4,hd-0.4): sub.box((hw/2,-0.08,zz),(hw-0.1,0.06,0.18),WOOD,bevel=0.02)
            L=math.hypot(hw-0.2,hd-1.0); sub.box((hw/2,-0.08,hd/2),(L,0.06,0.16),WOOD,rot=(0,-math.atan2(hd-1.0,hw-0.2),0),bevel=0.02)
            merge_kit(k,sub,xform)
        leaf(Matrix.Translation((-hw,-0.26,0.05)))
        leaf(Matrix.Translation((hw,-0.3,0.05))@Matrix.Rotation(math.pi-1.1,4,"Z"))
        k.box((0,-0.8,0.05),(2*hw+0.4,1.0,0.1),STONE,bevel=0.03)
        k.box((-0.2,-0.9,0.2),(1.2,0.8,0.25),HAY,rot=(0,0,0.3),bevel=0.12,segs=2,jitter=0.05,seed=4)
def barn_corner(k):
    k.box((-0.05,-0.05,0.35),(0.8,0.8,0.7),STONE,bevel=0.05,segs=2,jitter=0.02,seed=1)
    k.box((-0.25,-0.25,(0.7+HB)/2),(0.34,0.34,HB-0.7),WOOD,bevel=0.05,segs=2)
    k.box((-0.1,-0.1,HB-0.12),(0.5,0.5,0.24),WOOD,bevel=0.04)
# ---------------- lean-to shed (attaches to an existing wall; wall-local, outer = -Y)
def lean_to(k,open_front=True,roofmat=None):
    rm=ROOF if roofmat is None else roofmat
    D_=3.2; zh=3.0; zl=2.35
    for x in(-1.5,1.5):
        k.box((x,-D_,zl/2),(0.22,0.22,zl),WOOD,bevel=0.05,segs=2)
        k.box((x,-D_,0.08),(0.4,0.4,0.16),STONE,bevel=0.04)
    k.box((0,-D_,zl+0.05),(CELL+0.3,0.24,0.24),WOOD,bevel=0.04)
    for x in(-1.5,0,1.5):
        L=math.hypot(D_,zh-zl); ang=math.atan2(zh-zl,D_)
        k.box((x,-D_/2,(zh+zl)/2+0.12),(0.16,L+0.3,0.18),WOOD,rot=(ang,0,0),bevel=0.03)
    for x in(-1.5,1.5):
        k.box((x+(-0.35 if x>0 else 0.35),-D_+0.35,zl-0.3),(0.12,0.6,0.12),WOOD,rot=(0.75,0,0),bevel=0.02)
    L=math.hypot(D_+0.6,zh-zl+0.3); ang=math.atan2(zh-zl+0.3,D_+0.6)
    k.box((0,-(D_+0.6)/2,(zh+zl)/2+0.32),(CELL+0.35,L,0.14),rm,rot=(ang,0,0),bevel=0.03)
    k.box((0,-D_/2,0.03),(CELL,D_,0.06),PLANKS,bevel=0)
    if not open_front:
        for x in(-1.5,1.5): pass
# ---------------- tavern sign (wall-mounted bracket, big tankard emblem)
def tavern_sign(k):
    k.box((0,0.03,0),(0.18,0.1,0.7),IRON,bevel=0.02)
    k.box((0,-0.8,0.25),(0.08,1.6,0.08),IRON,bevel=0.015)
    k.box((0,-0.5,-0.05),(0.05,0.05,0.8),IRON,rot=(0.8,0,0),bevel=0)
    for yy in(-0.45,-1.35): k.box((0,yy,0.05),(0.02,0.02,0.35),IRON,bevel=0)
    k.box((0,-0.9,-0.55),(0.12,1.3,0.9),WOOD,bevel=0.05,segs=2)
    k.box((0,-0.9,-0.55),(0.14,1.1,0.72),YELLOW,bevel=0.02)
    _cyl(k,(-0.1,-0.95,-0.58),0.2,0.2,0.46,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    _cyl(k,(-0.16,-0.95,-0.33),0.18,0.18,0.06,10,HAY,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((-0.1,-0.66,-0.58),(0.06,0.12,0.3),WOOD,bevel=0.01)
# ---------------- string of festoon lights for beer garden (between two points, 6m)
def festoon(k,L=6.0,sag=0.6):
    n=12; pts=[Vector((-L/2+L*i/n,0,-sag*math.sin(math.pi*i/n))) for i in range(n+1)]
    for i in range(n):
        a,b=pts[i],pts[i+1]; m=(a+b)/2; d=b-a
        k.box(tuple(m),(d.length,0.02,0.02),IRON,rot=(0,-math.atan2(d.z,d.x),0),bevel=0)
        if i: _ico(k,tuple(pts[i]-Vector((0,0,0.1))),0.07,GLOW,sub=1)
EXTRA_SPECS+= [("SM_VK_Wall_Barn",lambda k: barn_wall(k,"."),dict(wobble=True,grime=True)),
               ("SM_VK_Wall_Barn_Door",lambda k: barn_wall(k,"D"),dict(wobble=False,grime=True)),
               ("SM_VK_Corner_Barn",barn_corner,dict(wobble=False,grime=True)),
               ("SM_VK_LeanTo",lean_to,dict(wobble=False,grime=False)),
               ("SM_VK_LeanTo_Thatch",lambda k: lean_to(k,roofmat=THATCH),dict(wobble=False,grime=False)),
               ("SM_VK_Prop_TavernSign",tavern_sign,dict(wobble=False,grime=False)),
               ("SM_VK_Prop_Festoon",festoon,dict(wobble=False,grime=False))]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
new=["SM_VK_Wall_Barn","SM_VK_Wall_Barn_Door","SM_VK_Corner_Barn","SM_VK_LeanTo","SM_VK_LeanTo_Thatch","SM_VK_Prop_TavernSign","SM_VK_Prop_Festoon","SM_VK_Chapel_Wall"]
full_rebuild(new)
for n in new: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Barn 397\nSM_VK_Wall_Barn_Door 615\nSM_VK_Corner_Barn 134\nSM_VK_LeanTo 348\nSM_VK_LeanTo_Thatch 348
# \nSM_VK_Prop_TavernSign 200\nSM_VK_Prop_Festoon 292\nSM_VK_Chapel_Wall 735\n"}

# ==============================================================================================================
# [0132] 2026-09-23 03:05:36  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def windmill(k):
    n=8; H_=8.5; r0,r1=3.0,2.2
    # tapered octagonal stone body
    vs=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=n,radius1=r0,radius2=r1,depth=H_)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,H_/2))@Matrix.Rotation(math.pi/8,4,"Z"),verts=vs)
    fs=list({f for v in vs for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=STONE; nrm=f.normal
        U=Vector((-nrm.y,nrm.x,0)).normalized() if abs(nrm.z)<0.9 else Vector((1,0,0))
        V=Vector((0,0,1)) if abs(nrm.z)<0.9 else Vector((0,1,0))
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[STONE],p.dot(V)/TILE[STONE])
    grid_cut(k,list({v for f in fs for v in f.verts}),1.0)
    # corner quoins on the 8 edges
    for i in range(n):
        a=2*math.pi*i/n
        z=0; j=0
        while z<H_-0.3:
            t_=z/H_; r=r0+(r1-r0)*t_+0.05
            k.box((math.cos(a)*r,math.sin(a)*r,z+0.25),(0.5 if j%2 else 0.35,0.35 if j%2 else 0.5,0.46),STONE,rot=(0,0,a),bevel=0.05,segs=2,jitter=0.015,seed=i*50+j)
            z+=0.5; j+=1
    # plinth, door, windows
    _cyl(k,(0,0,0.25),r0+0.25,r0+0.25,0.5,n,STONE)
    sub=Kit(); wall_door=Kit()
    k.quad([(-0.6,-r0+0.08,0.5),(0.6,-r0+0.08,0.5),(0.6,-r0+0.08,2.5),(-0.6,-r0+0.08,2.5)],PLANKS,uvs=[(0,0),(0.6,0),(0.6,1),(0,1)])
    for s_ in(-1,1): k.box((s_*0.72,-r0+0.02,1.5),(0.26,0.3,2.1),WOOD,bevel=0.04)
    k.box((0,-r0,2.62),(1.7,0.34,0.26),WOOD,bevel=0.04)
    k.box((0,-r0-0.45,0.35),(1.6,0.9,0.2),STONE,bevel=0.05,segs=2)
    for (a,z) in ((math.radians(-50),4.2),(math.radians(40),5.8),(math.radians(160),3.6),(math.radians(-110),6.6)):
        r=r0+(r1-r0)*z/H_
        R=Matrix.Translation((0,0,0))@Matrix.Rotation(a+math.pi/2,4,"Z")
        w=Kit()
        w.quad([(-0.3,-r+0.05,z-0.4),(0.3,-r+0.05,z-0.4),(0.3,-r+0.05,z+0.4),(-0.3,-r+0.05,z+0.4)],WINDOW,uvs=[(0,0),(0.6,0),(0.6,0.8),(0,0.8)])
        for s_ in(-1,1): w.box((s_*0.38,-r,z),(0.14,0.2,0.95),WOOD,bevel=0.025)
        w.box((0,-r,z+0.5),(0.9,0.22,0.14),WOOD,bevel=0.025); w.box((0,-r-0.05,z-0.5),(0.9,0.3,0.12),STONE,bevel=0.02)
        merge_kit(k,w,R)
    # timber gallery / balcony
    zg=H_-0.2
    _cyl(k,(0,0,zg),r1+1.1,r1+1.1,0.14,16,PLANKS)
    for i in range(16):
        a=2*math.pi*i/16; r=r1+1.0
        k.box((math.cos(a)*r,math.sin(a)*r,zg+0.5),(0.1,0.1,1.0),WOOD,bevel=0.02)
        k.box((math.cos(a)*(r1+0.5),math.sin(a)*(r1+0.5),zg-0.45),(0.9,0.12,0.12),WOOD,rot=(0,0.7,a),bevel=0.02)
        a2=2*math.pi*(i+0.5)/16
        k.box((math.cos(a2)*r,math.sin(a2)*r,zg+0.95),(0.1,2*math.pi*r/16+0.1,0.1),WOOD,rot=(0,0,a2),bevel=0.02)
    # timber cap (boat shaped -> use a ridged dome) with shingles
    zc=H_
    k.box((0,0,zc+0.9),(r1*2.1,r1*1.9,1.8),PLANKS,bevel=0.1,segs=2)
    for s_ in(-1,1):
        k.box((0,s_*r1*0.55,zc+2.45),(r1*2.5,r1*1.3,0.18),ROOF,rot=(s_*0.72,0,0),bevel=0.04)
    k.box((0,0,zc+2.95),(r1*2.55,0.4,0.4),ROOF,rot=(math.pi/4,0,0),bevel=0.1,segs=2)
    for s_ in(-1,1):
        v=[k.bm.verts.new(p) for p in ((s_*r1*1.05,-r1*0.95,zc+1.8),(s_*r1*1.05,r1*0.95,zc+1.8),(s_*r1*1.05,0,zc+3.0))]
        f=k.bm.faces.new(v if s_>0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    # windshaft
    _cyl(k,(0,-r1-0.4,zc+1.6),0.22,0.22,1.4,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    # tail pole + wheel
    k.box((0,r1+1.6,zc+0.4),(0.18,3.4,0.18),WOOD,rot=(-0.55,0,0),bevel=0.03)
def windmill_sails(k):
    _cyl(k,(0,0,0),0.35,0.35,0.5,10,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
    for i in range(4):
        R=Matrix.Rotation(i*math.pi/2+0.35,4,"Y"); sub=Kit()
        sub.box((0,-0.25,3.6),(0.22,0.2,7.2),WOOD,bevel=0.04)
        for j in range(9): sub.box((0.55,-0.3,1.4+j*0.68),(1.25,0.07,0.09),WOOD,bevel=0.01)
        for xx in(0.2,0.95,1.18): sub.box((xx,-0.3,4.3),(0.07,0.07,5.8),WOOD,bevel=0.01)
        sub.box((0.6,-0.33,4.4),(1.0,0.03,5.2),CLOTH_B,bevel=0)
        merge_kit(k,sub,R)
def guard_tower(k):
    W=4.0; h1=6.0
    stone_panel(k,-W/2,W/2,0,h1,-W/2,W/2)
    k.box((0,0,0.3),(W+0.5,W+0.5,0.6),STONE,bevel=0.06,segs=2)
    for sx in(-1,1):
        for sy in(-1,1):
            z=0.6;j=0
            while z<h1-0.2:
                long_x=j%2==0
                k.box((sx*(W/2-0.2),sy*(W/2-0.2),z+0.22),(1.0 if long_x else 0.55,0.55 if long_x else 1.0,0.44),STONE,bevel=0.06,segs=2,jitter=0.015,seed=j+sx*7+sy*3)
                z+=0.46; j+=1
    # arrow slits + door
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-W/2-0.02,3.6),(0.14,0.06,1.0),IRON,bevel=0)
        sub.box((0,-W/2-0.08,3.6),(0.5,0.12,1.3),STONE,bevel=0.04)
        merge_kit(k,sub,R)
    k.quad([(-0.55,-W/2-0.02,0.6),(0.55,-W/2-0.02,0.6),(0.55,-W/2-0.02,2.5),(-0.55,-W/2-0.02,2.5)],PLANKS,uvs=[(0,0),(0.55,0),(0.55,0.95),(0,0.95)])
    for zz in(1.0,2.0): k.box((0,-W/2-0.06,zz),(1.0,0.03,0.09),IRON,bevel=0.01)
    k.box((0,-W/2-0.1,2.65),(1.5,0.3,0.3),STONE,bevel=0.05,segs=2)
    for s_ in(-1,1): k.box((s_*0.7,-W/2-0.08,1.55),(0.3,0.25,1.95),STONE,bevel=0.05)
    # stairs to door
    for i in range(3): k.box((0,-W/2-0.5-i*0.3,0.5-i*0.17),(1.4,0.35,0.2),STONE,bevel=0.04)
    # overhanging timber hoarding
    z0=h1; WT=W+1.2; hh=2.4
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(WT/2-0.15),sy*(WT/2-0.15),z0+hh/2),(0.26,0.26,hh),WOOD,bevel=0.05,segs=2)
    k.box((0,0,z0+0.1),(WT,WT,0.2),PLANKS,bevel=0.03)
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        sub.box((0,-WT/2+0.08,z0+0.7),(WT-0.3,0.14,1.0),PLANKS,bevel=0.02)
        sub.box((0,-WT/2+0.08,z0+hh-0.12),(WT,0.22,0.24),WOOD,bevel=0.04)
        sub.box((0,-WT/2+0.08,z0+1.25),(WT,0.2,0.18),WOOD,bevel=0.03)
        for i in range(5): sub.box((-WT/2+0.6+i*(WT-1.2)/4,-W/2-0.3,z0-0.35),(0.18,0.8,0.18),WOOD,rot=(0.6,0,0),bevel=0.03)
        merge_kit(k,sub,R)
    # pyramid roof
    rz=z0+hh
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(WT+1.0)/math.sqrt(2),radius2=0.05,depth=3.2)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,rz+1.6))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.9)
    # flag
    k.box((0,0,rz+3.9),(0.08,0.08,2.0),WOOD,bevel=0.02)
    k.box((0,0.55,rz+4.5),(0.04,1.1,0.7),CLOTH_A,bevel=0)
EXTRA_SPECS+= [("SM_VK_Windmill",windmill,dict(wobble=False,grime=True)),("SM_VK_Windmill_Sails",windmill_sails,dict(wobble=False,grime=False)),
               ("SM_VK_GuardTower",guard_tower,dict(wobble=False,grime=True))]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
new=["SM_VK_Windmill","SM_VK_Windmill_Sails","SM_VK_GuardTower"]
full_rebuild(new)
for n in new: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Windmill 9551\nSM_VK_Windmill_Sails 1388\nSM_VK_GuardTower 4355\n"}

# ==============================================================================================================
# [0133] 2026-09-23 03:06:09  blender  ok
# ==============================================================================================================
import bpy
code=r'''
def build_tavern(coll,origin,seed=31):
    st={"ground":"Stone","plaster":"Ochre","shutter":"Red","roof":"Red","seed":seed}
    build_L_v(coll,origin,2,1,2,st)
    ox,oy,orz=origin; c,s_=math.cos(orz),math.sin(orz)
    def P(n,x,y,z,r,sty={}): place_v(coll,n,x,y,z,r,origin,sty)
    P("SM_VK_Prop_TavernSign",-1.5+3*1+1.1,-3.3,3.4,0)
    P("SM_VK_Porch",1.5,-3,0,0,st)
    # beer garden in the L's inner yard (x 3..12, y 3..9) -> fenced
    for i,(x,y) in enumerate(((6.0,5.5),(9.8,6.5))):
        P("SM_VK_Prop_Table",x,y,0,90)
        for dy in(-0.75,0.75):
            for dx in(-0.6,0.6): P("SM_VK_Prop_Stool",x+dy*1.1,y+dx,0,0)
    P("SM_VK_Prop_BarrelStack",11.6,3.9,0,0)
    P("SM_VK_Prop_Festoon",8.0,4.0,3.0,0)
    for (x,y) in((4.6,4.0),(11.4,4.0)): P("SM_VK_Prop_LampPost",x,y,0,0)
    fence_run(coll,(3.2,9.4),(12.0,9.4),origin); fence_run(coll,(12.0,3.3),(12.0,9.4),origin,gate_at=1)
def build_blacksmith(coll,origin,seed=32):
    st={"ground":"Stone","plaster":"White","shutter":"Natural","roof":"Green","seed":seed}
    build_house_v(coll,origin,2,1,st,front="DW",back="..",chimney=True)
    def P(n,x,y,z,r,sty={}): place_v(coll,n,x,y,z,r,origin,sty)
    # open workshop lean-tos along the +X end wall
    for yy in(-1.5,1.5): P("SM_VK_LeanTo",3.0,-yy,0,90,st)
    P("SM_VK_Prop_Forge",4.6,1.2,0,-90)
    P("SM_VK_Prop_Anvil",4.8,-0.9,0,20)
    P("SM_VK_Prop_Grindstone",7.0,-2.4,0,90)
    P("SM_VK_Prop_WeaponRack",3.6,-2.5,0,0)
    P("SM_VK_Prop_Trough",7.1,0.9,0,90)
    P("SM_VK_Prop_BarrelStack",-1.0,4.2,0,0)
    P("SM_VK_Prop_Woodpile",-1.5,-4.9,0,0)
    P("SM_VK_Prop_Crates",7.4,-4.3,0,30)
def build_barn(coll,origin,n=3,roof="Thatch"):
    L=n*CELL; st={"roof":roof}
    def P(nm,x,y,z,r,sty=st): place_v(coll,nm,x,y,z,r,origin,sty)
    for i in range(n):
        x=-L/2+1.5+3*i
        P("SM_VK_Wall_Barn_Door" if i==n//2 else "SM_VK_Wall_Barn",x,-3,0,0)
        P("SM_VK_Wall_Barn",x,3,0,180)
    for yy in(-1.5,1.5):
        P("SM_VK_Wall_Barn",-L/2,yy,0,-90); P("SM_VK_Wall_Barn",L/2,-yy,0,90)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): P("SM_VK_Corner_Barn",cx,cy,0,r)
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==0: P("SM_VK_Roof_Gable_Planks",x,0,HB,180)
        elif i==n-1: P("SM_VK_Roof_Gable_Planks",x,0,HB,0)
        else: P("SM_VK_Roof_Mid",x,0,HB,0)
    P("SM_VK_LeanTo_Thatch",-L/2+1.5,3,0,180,{})
    P("SM_VK_Prop_Haystack",L/2+3.0,2.0,0,0,{}); P("SM_VK_Prop_HayBale",L/2+2.2,-2.4,0,20,{})
    P("SM_VK_Prop_HayBale",-2.5,-4.6,0,-10,{}); P("SM_VK_Prop_Cart",2.2,-5.2,0,-20,{})
    P("SM_VK_Prop_Trough",-L/2-1.6,-1.0,0,90,{})
    fence_run(coll,(-L/2-3.5,-6.5),(-L/2-3.5,4.0),origin); fence_run(coll,(-L/2-3.5,4.0),(-L/2+0.0,7.0),origin)
def build_windmill(coll,origin):
    place_v(coll,"SM_VK_Windmill",0,0,0,0,origin,{})
    o=place_v(coll,"SM_VK_Windmill_Sails",0,-2.2-0.75,8.5+1.6,0,origin,{})
    o["spin_axis"]="local Y"
    place_v(coll,"SM_VK_Prop_Sacks",1.8,-3.6,0,0,origin,{}); place_v(coll,"SM_VK_Prop_Cart",-2.6,-4.4,0,15,origin,{})
def build_guardtower(coll,origin):
    place_v(coll,"SM_VK_GuardTower",0,0,0,0,origin,{})
    place_v(coll,"SM_VK_Prop_WeaponRack",2.9,-1.2,0,90,origin,{})
    place_v(coll,"SM_VK_Prop_BarrelStack",-2.7,-1.8,0,90,origin,{})
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
S=vcol("VK_Showcase")
for o in list(S.objects): bpy.data.objects.remove(o)
R=math.radians
build_chapel(S,(0,-170,0))
build_tavern(S,(-32,-176,0))
build_blacksmith(S,(24,-172,0))
build_barn(S,(-14,-196,R(0)))
build_windmill(S,(-40,-198,R(-20)))
build_guardtower(S,(18,-194,R(10)))
print(len(S.objects))
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=24
tgt=Vector((-6,-182,0)); cs.location=tgt+Vector((10,48,34))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
cs.data.clip_end=400
SC.camera=cs; SC.render.resolution_percentage=50
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 163\n"}

# ==============================================================================================================
# [0134] 2026-09-23 03:06:31  blender  ok
# ==============================================================================================================
import bpy, os, numpy as np
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=32
shots=[("chapel",(3,-170,5.5),(16,-24,9)),("tavern",(-27,-172,3.5),(13,-19,9)),("blacksmith",(26,-172,2.5),(12,-15,8)),
       ("barn",(-14,-196,3),(11,-17,8)),("windmill",(-40,-198,6),(10,-18,4)),("guardtower",(18,-194,5),(9,-13,4))]
SC.render.resolution_x=960; SC.render.resolution_y=640; SC.render.resolution_percentage=100
files=[]
for name,tgt,off in shots:
    tgt=Vector(tgt); cs.location=tgt+Vector(off)
    cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=cs; fp=os.path.join(out,f"_b_{name}.png"); SC.render.filepath=fp
    bpy.ops.render.render(write_still=True,scene=SC.name); files.append(fp)
SC.render.resolution_x=1920; SC.render.resolution_y=1080
# contact sheet 3x2
tiles=[]
for fp in files:
    im=bpy.data.images.load(fp); a=np.array(im.pixels[:],dtype=np.float32).reshape(640,960,4); tiles.append(a); bpy.data.images.remove(im)
rows=[np.concatenate(tiles[i*3:(i+1)*3],axis=1) for i in range(2)]
sheet=np.concatenate(rows[::-1],axis=0)   # blender images are bottom-up
img=bpy.data.images.new("_sheet",2880,1280,alpha=True); img.pixels.foreach_set(sheet.ravel())
img.filepath_raw=os.path.join(out,"village_special_buildings.png"); img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
for fp in files: os.remove(fp)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0135] 2026-09-23 03:07:08  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
# windmill cap: correct slope direction, lighter quoins
s=s.replace("        k.box((0,s_*r1*0.55,zc+2.45),(r1*2.5,r1*1.3,0.18),ROOF,rot=(s_*0.72,0,0),bevel=0.04)",
            "        k.box((0,s_*r1*0.55,zc+2.35),(r1*2.5,r1*1.45,0.18),ROOF,rot=(-s_*0.72,0,0),bevel=0.04)")
s=s.replace("            k.box((math.cos(a)*r,math.sin(a)*r,z+0.25),(0.5 if j%2 else 0.35,0.35 if j%2 else 0.5,0.46),STONE,rot=(0,0,a),bevel=0.05,segs=2,jitter=0.015,seed=i*50+j)",
            "            k.box((math.cos(a)*r,math.sin(a)*r,z+0.25),(0.5 if j%2 else 0.35,0.35 if j%2 else 0.5,0.46),STONE,rot=(0,0,a),bevel=0.05,segs=1,jitter=0.015,seed=i*50+j)")
s=s.replace("    grid_cut(k,list({v for f in fs for v in f.verts}),1.0)\n    # corner quoins","    grid_cut(k,list({v for f in fs for v in f.verts}),1.5)\n    # corner quoins")
# gable triangles of the cap: correct heights to match the slopes
s=s.replace("        v=[k.bm.verts.new(p) for p in ((s_*r1*1.05,-r1*0.95,zc+1.8),(s_*r1*1.05,r1*0.95,zc+1.8),(s_*r1*1.05,0,zc+3.0))]",
            "        v=[k.bm.verts.new(p) for p in ((s_*r1*1.05,-r1*0.95,zc+1.8),(s_*r1*1.05,r1*0.95,zc+1.8),(s_*r1*1.05,0,zc+2.75))]")
# haystack: proper conical rick
s=s.replace('''def prop_haystack(k):
    _ico(k,(0,0,0.9),1.3,HAY,(1,1,1.1),sub=2,jit=0.08,seed=4)
    _cyl(k,(0,0,2.2),0.06,0.06,0.9,6,WOOD)''','''def prop_haystack(k):
    rnd=random.Random(4)
    vs=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=16,radius1=1.35,radius2=1.25,depth=1.1)["verts"]
    for v in vs: v.co+=Vector((0,0,0.55))
    vs2=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=16,radius1=1.42,radius2=0.12,depth=1.9)["verts"]
    for v in vs2: v.co+=Vector((0,0,1.1+0.95))
    for v in vs+vs2:
        d=Vector((v.co.x,v.co.y,0))
        if d.length>0.2: v.co+=d.normalized()*noise.noise(v.co*1.3)*0.12
    fs=list({f for v in vs+vs2 for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=HAY
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(math.atan2(p.y,p.x)*1.4/TILE[HAY],p.z/TILE[HAY])
    for i in range(3):   # binding ropes
        _cyl(k,(0,0,1.25+i*0.45),1.36-i*0.32,1.36-i*0.32,0.06,16,WOOD)
    _cyl(k,(0,0,3.2),0.05,0.05,0.9,6,WOOD)''')
t.clear(); t.write(s); exec(s)
full_rebuild(["SM_VK_Windmill","SM_VK_Prop_Haystack"])
m=bpy.data.materials["M_VK_Iron"]; b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
b.inputs["Roughness"].default_value=1.0; b.inputs["Specular IOR Level"].default_value=0.05
mx=next(n for n in m.node_tree.nodes if n.type=="MIX"); mx.inputs[6].default_value=(0.03,0.03,0.035,1)
print(len(bpy.data.objects["SM_VK_Windmill"].data.polygons))
# re-render barn + windmill tiles
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; cs=bpy.data.objects["VK_CameraProps"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_x=1920; SC.render.resolution_y=640; SC.render.resolution_percentage=50
tgt=Vector((-27,-198,4)); cs.data.lens=30; cs.location=tgt+Vector((0,-30,7))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_vk_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
SC.render.resolution_y=1080
# ---- result ----
# {"result":"Code executed successfully: 5657\n"}

# ==============================================================================================================
# [0136] 2026-09-23 03:07:23  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; cs=bpy.data.objects["VK_CameraProps"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=50
tgt=Vector((-34,-198,6)); cs.data.lens=26; cs.location=tgt+Vector((12,-22,6))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0137] 2026-09-23 03:07:44  blender  ok
# ==============================================================================================================
import bpy, os, numpy as np
exec(bpy.data.texts["vk_helpers"].as_string())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=32
shots=[("chapel",(3,-170,5.5),(16,-24,9)),("tavern",(-27,-172,3.5),(13,-19,9)),("blacksmith",(26,-172,2.5),(12,-15,8)),
       ("barn",(-14,-196,3),(11,-17,8)),("windmill",(-40,-198,6.5),(9,-20,3)),("guardtower",(18,-194,5),(9,-13,4))]
def sheet(shots,fname,cols=3,w=960,h=640):
    SC.render.resolution_x=w; SC.render.resolution_y=h; SC.render.resolution_percentage=100
    tiles=[]
    for name,tgt,off in shots:
        tgt=Vector(tgt); cs.location=tgt+Vector(off)
        cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
        SC.camera=cs; fp=os.path.join(out,f"_t.png"); SC.render.filepath=fp
        bpy.ops.render.render(write_still=True,scene=SC.name)
        im=bpy.data.images.load(fp); tiles.append(np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)); bpy.data.images.remove(im); os.remove(fp)
    rows=[np.concatenate(tiles[i*cols:(i+1)*cols],axis=1) for i in range(len(tiles)//cols)]
    sh=np.concatenate(rows[::-1],axis=0)
    img=bpy.data.images.new("_sheet",sh.shape[1],sh.shape[0],alpha=True); img.pixels.foreach_set(sh.ravel())
    img.filepath_raw=os.path.join(out,fname); img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
sheet(shots,"village_special_buildings.png")
# props lineup
T=vcol("VK_Test")
for o in list(T.objects): bpy.data.objects.remove(o)
names=["Well","Fence","FenceGate","Cart","LampPost","Bench","Crates","GardenBed","Table","Stool","Trough","HayBale","Haystack","Woodpile",
       "NoticeBoard","Signpost","Anvil","Grindstone","Sacks","WeaponRack","BarrelStack","Forge"]
for i,n in enumerate(names):
    place_v(T,"SM_VK_Prop_"+n,(i%6)*4.6,-120-(i//6)*5.0,0,0,(0,0,0),{})
place_v(T,"SM_VK_MarketStall",27.5,-128,0,0,(0,0,0),{"cloth":"Green"})
place_v(T,"SM_VK_Prop_TavernSign",27,-134.5,2.2,90,(0,0,0),{})
for o in T.objects: o.hide_render=False
cs.data.lens=28
SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=100
tgt=Vector((13,-128.5,0.5)); cs.location=tgt+Vector((0,-24,16))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"village_props.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for f in ("_vk_test.png",):
    p=os.path.join(out,f)
    if os.path.exists(p): os.remove(p)
for img in bpy.data.images:
    if img.source=="FILE" and not img.packed_file and img.has_data:
        try: img.pack()
        except: pass
bpy.ops.wm.save_mainfile()
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n"}

# ==============================================================================================================
# [0138] 2026-09-23 03:08:09  blender  ok
# ==============================================================================================================
import bpy, os
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''tex_mat("M_VK_Burlap","T_VK_Burlap",0.95)]
STONE,''','''tex_mat("M_VK_Burlap","T_VK_Burlap",0.95), tex_mat("M_VK_Soil",None,1.0,flat=(0.20,0.13,0.08))]
STONE,''')
s=s.replace("THATCH,PLANKS,ASHLAR,BURLAP=range(26)","THATCH,PLANKS,ASHLAR,BURLAP,SOIL=range(27)")
s=s.replace("    k.box((0,0,0.2),(2.6,1.4,0.06),BREAD,bevel=0)   # re-tinted to soil below","    k.box((0,0,0.2),(2.6,1.4,0.06),SOIL,bevel=0)")
t.clear(); t.write(s); exec(s)
full_rebuild(["SM_VK_Prop_GardenBed"])
m=bpy.data.materials["M_VK_Glow"]; b=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
b.inputs["Emission Strength"].default_value=3.0; b.inputs["Emission Color"].default_value=(1.0,0.42,0.08,1)
mx=next(n for n in m.node_tree.nodes if n.type=="MIX"); mx.inputs[6].default_value=(1.0,0.5,0.15,1)
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.camera=bpy.data.objects["VK_CameraProps"]
SC.render.filepath=os.path.join(out,"village_props.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
bpy.ops.wm.save_mainfile()
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n"}

# ==============================================================================================================
# [0139] 2026-09-23 03:18:07  blender  ok
# ==============================================================================================================
import bpy, os
src=bpy.data.filepath
bak=os.path.join(os.path.dirname(src),"medievalDiorama_backup_before_PBR.blend")
bpy.ops.wm.save_mainfile()
bpy.ops.wm.save_as_mainfile(filepath=bak,copy=True)
print(src, os.path.exists(bak), round(os.path.getsize(src)/1e6,1),"MB")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nInfo: Saved \"medievalDiorama_backup_before_PBR.blend\"\nE:\\Unity\\Proj
# ects\\Cube Sorter\\Art\\WallKit\\medievalDiorama.blend True 70.6 MB\n"}

# ==============================================================================================================
# [0140] 2026-09-23 03:18:32  blender  ok
# ==============================================================================================================
import bpy
code = r'''
import bpy, numpy as np, os, math
TEXDIR=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\VillageKit\Textures"
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
    if img: bpy.data.images.remove(img)
    img=bpy.data.images.new(name,S,S,alpha=False,is_data=data)
    if data and img.colorspace_settings.name!="Non-Color": img.colorspace_settings.name="Non-Color"
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
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
'''
t=bpy.data.texts.get("vk_tex") or bpy.data.texts.new("vk_tex"); t.clear(); t.write(code)
exec(code)
import time; t0=time.time(); n=fbm(1024,2.0,1); print("fbm 1024:",round(time.time()-t0,2),"s", n.std())
# ---- result ----
# {"result":"Code executed successfully: fbm 1024: 0.1 s 0.99999845\n"}

# ==============================================================================================================
# [0141] 2026-09-23 03:19:08  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def gen_stone(S=1024,seed=9,tile=3.0,depth=0.05):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.006)%1; Y=(y+fbm(S,3.5,seed+2)*0.005)%1
    rows=rng.uniform(0.12,0.27,6); rows/=rows.sum(); rcum=np.concatenate([[0],np.cumsum(rows)])
    ri=np.clip(np.searchsorted(rcum,Y,side="right")-1,0,len(rows)-1)
    dist=np.zeros((S,S),f32); sid=np.zeros((S,S),np.int32); cu=np.zeros((S,S),f32); cv=np.zeros((S,S),f32)
    rad=38.0; nid=0
    for r in range(len(rows)):
        m=ri==r
        widths=rng.uniform(0.16,0.42,12); k=1
        while widths[:k].sum()<1: k+=1
        widths=widths[:k]; widths/=widths.sum()
        wc=np.concatenate([[0],np.cumsum(widths)]); off=rng.uniform(0,1)
        xs=(X[m]+off)%1; si=np.clip(np.searchsorted(wc,xs,side="right")-1,0,len(widths)-1)
        u=(xs-wc[si])/widths[si]; v=(Y[m]-rcum[r])/rows[r]
        split=rng.random(len(widths))<0.35; sp=split[si]
        v2=np.where(sp,np.where(v<0.5,v*2,(v-0.5)*2),v); hsc=np.where(sp,0.5,1.0)
        dx=np.minimum(u,1-u)*widths[si]*S; dy=np.minimum(v2,1-v2)*rows[r]*S*hsc
        qx=np.maximum(rad-dx,0); qy=np.maximum(rad-dy,0)
        d=np.minimum(dx,dy); c=(qx>0)&(qy>0); d=np.where(c,rad-np.hypot(qx,qy),d)
        dist[m]=d; sub=np.where(sp&(v>=0.5),1,0)
        sid[m]=nid+si*2+sub; cu[m]=u-0.5; cv[m]=v2-0.5
        nid+=len(widths)*2
    en=fbm(S,2.2,seed+3,fmin=6)*5.0+fbm(S,1.8,seed+4,fmin=40)*2.0
    d=dist+en; gap=6.5
    mask=smooth(gap,gap+2.5,d)
    prof=smooth(gap,gap+42,d)**0.5
    tv=rng.uniform(-1,1,(nid,2)).astype(f32)
    tilt=tv[sid,0]*cu*0.22+tv[sid,1]*cv*0.18
    dome=1-np.clip(np.abs(cu)*2,0,1)**2*0.15-np.clip(np.abs(cv)*2,0,1)**2*0.22
    chips=np.clip(fbm(S,2.0,seed+5,fmin=20),-2,2)*0.05
    stone_h=0.38+0.52*prof*dome+tilt*prof+chips*prof
    mortar_h=0.10+0.03*fbm(S,1.5,seed+6,fmin=60)
    h=blur(np.clip(mask*stone_h+(1-mask)*mortar_h,0,1),0.7)
    pal=np.array([(0.66,0.60,0.50),(0.56,0.53,0.48),(0.70,0.62,0.50),(0.52,0.50,0.47),(0.63,0.55,0.45),(0.60,0.58,0.54),(0.58,0.52,0.44)],f32)
    pid=rng.integers(0,len(pal),nid); tint=rng.uniform(0.88,1.1,nid).astype(f32)
    base=pal[pid[sid]]*tint[sid][...,None]
    light=painted_light(normal_from_height(h,depth*2.5,tile))
    mott=fbm(S,2.2,seed+7,fmin=4)*0.05+fbm(S,1.5,seed+8,fmin=50)*0.035
    col=base*(0.78+0.34*light[...,None]+mott[...,None])
    rim=smooth(gap+0.5,gap+4,d)-smooth(gap+4,gap+11,d)
    col=col+0.07*rim[...,None]
    lich=smooth(1.2,1.8,fbm(S,2.8,seed+9,fmin=3))*mask*(0.5+0.5*smooth(-0.5,1,fbm(S,1.5,seed+10,fmin=30)))
    col=col*(1-0.45*lich[...,None])+np.array([0.52,0.56,0.36],f32)*0.45*lich[...,None]
    mortar=np.array([0.27,0.23,0.19],f32)*(1+mott[...,None]*1.5)
    col=col*mask[...,None]+mortar*(1-mask[...,None])
    rough=np.clip(0.78+0.06*fbm(S,2,seed+11,fmin=10)+0.15*(1-mask)+0.08*lich,0,1)
    PBR_SETS["T_VK_Stone"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Stone",col,h,rough,depth,tile)
def gen_ashlar(S=1024,seed=13,tile=2.5,depth=0.03):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.002)%1; Y=(y+fbm(S,3.5,seed+2)*0.002)%1
    nrow=5; row=np.minimum((Y*nrow).astype(int),nrow-1); v=(Y*nrow)%1
    blocks=np.array([3,4,3,4,3]); offs=rng.uniform(0,1,nrow)
    nb=blocks[row]; xo=(X+offs[row])%1; c=np.minimum((xo*nb).astype(int),nb-1); u=(xo*nb)%1
    d=np.minimum(np.minimum(u,1-u)*S/nb,np.minimum(v,1-v)*S/nrow)
    d=d+fbm(S,2.0,seed+3,fmin=20)*1.5; gap=3.0
    mask=smooth(gap,gap+1.5,d); cham=smooth(gap,gap+14,d)
    sid=row*8+c; tv=rng.uniform(-1,1,(nrow*8,2)).astype(f32)
    tool=np.sin(2*np.pi*(146*x+37*y)).astype(f32)
    chip=smooth(1.3,1.8,fbm(S,2.2,seed+5,fmin=10))*(1-smooth(gap+2,gap+22,d))
    hs=0.45+0.42*cham+(tv[sid,0]*(u-0.5)+tv[sid,1]*(v-0.5))*0.08*cham+0.012*tool*cham+0.04*fbm(S,1.8,seed+4,fmin=20)*cham-0.28*chip
    h=blur(np.clip(mask*hs+(1-mask)*0.12,0,1),0.6)
    tint=rng.uniform(0.9,1.08,(nrow*8,3)).astype(f32)*np.array([1,0.99,0.97],f32)
    base=np.array([0.74,0.70,0.62],f32)*tint[sid]
    light=painted_light(normal_from_height(h,depth*2.5,tile))
    mott=fbm(S,2.4,seed+6,fmin=4)*0.04+fbm(S,1.4,seed+7,fmin=80)*0.04
    col=base*(0.8+0.3*light[...,None]+mott[...,None])
    col=col*mask[...,None]+np.array([0.36,0.32,0.28],f32)*(1-mask[...,None])
    stain=smooth(0.8,2.2,fbm(S,2.0,seed+8,fmin=2,ay=5))
    col=col*(1-0.12*stain[...,None])
    rough=np.clip(0.8+0.05*fbm(S,2,seed+9,fmin=10)+0.12*(1-mask),0,1)
    PBR_SETS["T_VK_Ashlar"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Ashlar",col,h,rough,depth,tile)
def gen_plaster(S=1024,seed=21,tile=1.5,depth=0.02):
    rng=np.random.default_rng(seed); x,y=grid(S)
    lumps=fbm(S,3.2,seed,fmin=2); strokes=fbm(S,2.4,seed+1,fmin=3,ax=3.5); fine=fbm(S,1.3,seed+2,fmin=80)
    hp=0.62+0.10*lumps+0.06*strokes+0.02*fine
    pts=rng.uniform(0,1,(70,2)); F1,F2,ID=voronoi(x,y,pts)
    e=F2-F1; cm=smooth(0.6,1.3,fbm(S,3.0,seed+3,fmin=2))
    crack=(1-smooth(0.0008,0.0028,e))*cm
    pm=fbm(S,3.3,seed+4,fmin=2)+fbm(S,1.6,seed+5,fmin=30)*0.12
    patch=smooth(1.45,1.56,pm)
    nr=21; nbk=6
    br=(y*nr).astype(int); bv=(y*nr)%1; bxo=(x*nbk+0.5*(br%2))%nbk; bci=bxo.astype(int); bu=bxo%1
    bd=np.minimum(np.minimum(bu,1-bu)*S/nbk,np.minimum(bv,1-bv)*S/nr)
    bmask=smooth(2.0,3.5,bd); bprof=smooth(2,9,bd)
    hb=0.2+0.16*bmask*bprof+0.02*fine
    h=hp*(1-patch)+hb*patch-0.22*crack*(1-patch)
    h=blur(np.clip(h,0,1),0.6)
    base=np.array([0.90,0.85,0.72],f32)
    col=base*(1+0.045*lumps[...,None])[...]
    blot=smooth(0.3,1.6,fbm(S,3.0,seed+6,fmin=2))
    col=col*(1-blot[...,None])+np.array([0.84,0.77,0.62],f32)*blot[...,None]
    streak=smooth(0.8,2.2,fbm(S,2.0,seed+7,fmin=3,ay=7))
    col=col*(1-0.13*streak[...,None])
    bid=br*nbk+bci; bpal=np.array([(0.60,0.33,0.22),(0.52,0.29,0.20),(0.64,0.40,0.27),(0.56,0.36,0.25)],f32)
    bcol=bpal[(bid*7)%4]*(0.9+0.2*bprof[...,None])
    bcol=bcol*bmask[...,None]+np.array([0.62,0.58,0.52],f32)*(1-bmask[...,None])
    col=col*(1-patch[...,None])+bcol*patch[...,None]
    col=col*(1-0.55*crack[...,None]*(1-patch[...,None]))
    rough=np.clip(0.92-0.05*patch+0.03*fbm(S,2,seed+8,fmin=10),0,1)
    PBR_SETS["T_VK_Plaster"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Plaster",col,h,rough,depth,tile,ao_in_albedo=0.45)
'''
t=bpy.data.texts.get("vk_texgen") or bpy.data.texts.new("vk_texgen"); t.clear(); t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(code)
import time
for fn in (gen_stone,gen_ashlar,gen_plaster):
    t0=time.time(); fn(); print(fn.__name__, round(time.time()-t0,1),"s")
# ---- result ----
# {"result":"Code executed successfully: gen_stone 1.9 s\ngen_ashlar 1.6 s\ngen_plaster 1.9 s\n"}

# ==============================================================================================================
# [0142] 2026-09-23 03:20:28  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def facets(S,seed,fmin=5,fmax=48,amp=1.0):
    """broad chiselled facets: creases where low-freq noise crosses zero"""
    return (-np.abs(fbm(S,3.0,seed,fmin=fmin,fmax=fmax))*amp).astype(f32)
def gen_stone(S=1024,seed=9,tile=3.0,depth=0.05):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.006)%1; Y=(y+fbm(S,3.5,seed+2)*0.005)%1
    rows=rng.uniform(0.12,0.27,6); rows/=rows.sum(); rcum=np.concatenate([[0],np.cumsum(rows)])
    ri=np.clip(np.searchsorted(rcum,Y,side="right")-1,0,len(rows)-1)
    dist=np.zeros((S,S),f32); sid=np.zeros((S,S),np.int32); cu=np.zeros((S,S),f32); cv=np.zeros((S,S),f32)
    rad=40.0; nid=0
    for r in range(len(rows)):
        m=ri==r
        widths=rng.uniform(0.16,0.42,12); k=1
        while widths[:k].sum()<1: k+=1
        widths=widths[:k]; widths/=widths.sum()
        wc=np.concatenate([[0],np.cumsum(widths)]); off=rng.uniform(0,1)
        xs=(X[m]+off)%1; si=np.clip(np.searchsorted(wc,xs,side="right")-1,0,len(widths)-1)
        u=(xs-wc[si])/widths[si]; v=(Y[m]-rcum[r])/rows[r]
        split=rng.random(len(widths))<0.35; sp=split[si]
        v2=np.where(sp,np.where(v<0.5,v*2,(v-0.5)*2),v); hsc=np.where(sp,0.5,1.0)
        dx=np.minimum(u,1-u)*widths[si]*S; dy=np.minimum(v2,1-v2)*rows[r]*S*hsc
        qx=np.maximum(rad-dx,0); qy=np.maximum(rad-dy,0)
        d=np.minimum(dx,dy); c=(qx>0)&(qy>0); d=np.where(c,rad-np.hypot(qx,qy),d)
        dist[m]=d; sub=np.where(sp&(v>=0.5),1,0)
        sid[m]=nid+si*2+sub; cu[m]=u-0.5; cv[m]=v2-0.5
        nid+=len(widths)*2
    en=fbm(S,2.6,seed+3,fmin=4,fmax=60)*4.5
    d=dist+en; gap=6.5
    mask=smooth(gap,gap+2.0,d)
    prof=smooth(gap,gap+46,d)**0.5
    tv=rng.uniform(-1,1,(nid,2)).astype(f32)
    tilt=tv[sid,0]*cu*0.22+tv[sid,1]*cv*0.18
    dome=1-np.clip(np.abs(cu)*2,0,1)**2*0.15-np.clip(np.abs(cv)*2,0,1)**2*0.22
    fac=facets(S,seed+5,6,40,0.10)+facets(S,seed+12,14,90,0.04)
    grain=fbm(S,1.6,seed+13,fmin=120)*0.006
    stone_h=0.36+0.5*prof*dome+tilt*prof+fac*prof+grain
    mortar_h=0.09+0.02*fbm(S,2.0,seed+6,fmin=20,fmax=200)
    h=blur(np.clip(mask*stone_h+(1-mask)*mortar_h,0,1),0.8)
    pal=np.array([(0.66,0.60,0.50),(0.56,0.53,0.48),(0.70,0.62,0.50),(0.52,0.50,0.47),(0.63,0.55,0.45),(0.60,0.58,0.54),(0.58,0.52,0.44)],f32)
    pid=rng.integers(0,len(pal),nid); tint=rng.uniform(0.9,1.08,nid).astype(f32)
    base=pal[pid[sid]]*tint[sid][...,None]
    light=painted_light(normal_from_height(blur(h,2.5),depth*3.0,tile))
    mott=fbm(S,2.6,seed+7,fmin=3,fmax=80)*0.05
    col=base*(0.76+0.36*light[...,None]+mott[...,None])
    rim=smooth(gap+0.5,gap+4,d)-smooth(gap+4,gap+12,d)
    col=col+0.06*rim[...,None]
    lich=smooth(1.25,1.9,fbm(S,2.8,seed+9,fmin=3))*mask*smooth(-0.4,0.8,fbm(S,2.2,seed+10,fmin=20))
    col=col*(1-0.5*lich[...,None])+np.array([0.50,0.56,0.33],f32)*0.5*lich[...,None]
    mortar=np.array([0.26,0.22,0.18],f32)*(1+mott[...,None])
    col=col*mask[...,None]+mortar*(1-mask[...,None])
    rough=np.clip(0.8+0.05*fbm(S,2.4,seed+11,fmin=6)+0.14*(1-mask)+0.06*lich,0,1)
    PBR_SETS["T_VK_Stone"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Stone",col,h,rough,depth,tile)
def gen_ashlar(S=1024,seed=13,tile=2.5,depth=0.03):
    rng=np.random.default_rng(seed); x,y=grid(S)
    X=(x+fbm(S,3.5,seed+1)*0.002)%1; Y=(y+fbm(S,3.5,seed+2)*0.002)%1
    nrow=5; row=np.minimum((Y*nrow).astype(int),nrow-1); v=(Y*nrow)%1
    blocks=np.array([3,4,3,4,3]); offs=rng.uniform(0,1,nrow)
    nb=blocks[row]; xo=(X+offs[row])%1; c=np.minimum((xo*nb).astype(int),nb-1); u=(xo*nb)%1
    d=np.minimum(np.minimum(u,1-u)*S/nb,np.minimum(v,1-v)*S/nrow)
    d=d+fbm(S,2.6,seed+3,fmin=6,fmax=80)*1.8; gap=3.0
    mask=smooth(gap,gap+1.5,d); cham=smooth(gap,gap+16,d)
    sid=row*8+c; tv=rng.uniform(-1,1,(nrow*8,2)).astype(f32)
    tool=np.sin(2*np.pi*(146*x+37*y)).astype(f32)
    chip=smooth(1.4,1.9,fbm(S,2.6,seed+5,fmin=6,fmax=60))*(1-smooth(gap+2,gap+26,d))
    hs=0.45+0.42*cham+(tv[sid,0]*(u-0.5)+tv[sid,1]*(v-0.5))*0.08*cham+0.008*tool*cham+facets(S,seed+4,6,50,0.05)*cham-0.3*chip
    h=blur(np.clip(mask*hs+(1-mask)*0.12,0,1),0.7)
    val=rng.uniform(0.9,1.07,nrow*8).astype(f32); warm=rng.uniform(-1,1,nrow*8).astype(f32)
    base=np.array([0.74,0.70,0.62],f32)*val[sid][...,None]*(1+warm[sid][...,None]*np.array([0.025,0.0,-0.03],f32))
    light=painted_light(normal_from_height(blur(h,2.0),depth*3,tile))
    mott=fbm(S,2.6,seed+6,fmin=3,fmax=90)*0.045
    col=base*(0.8+0.3*light[...,None]+mott[...,None])
    col=col*mask[...,None]+np.array([0.36,0.32,0.28],f32)*(1-mask[...,None])
    stain=smooth(0.8,2.2,fbm(S,2.0,seed+8,fmin=2,ay=5))
    col=col*(1-0.12*stain[...,None])
    rough=np.clip(0.8+0.05*fbm(S,2.4,seed+9,fmin=6)+0.12*(1-mask),0,1)
    PBR_SETS["T_VK_Ashlar"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Ashlar",col,h,rough,depth,tile)
def gen_plaster(S=1024,seed=21,tile=1.5,depth=0.02):
    rng=np.random.default_rng(seed); x,y=grid(S)
    lumps=fbm(S,3.2,seed,fmin=2); strokes=fbm(S,2.8,seed+1,fmin=3,fmax=60,ax=3.5)
    hp=0.62+0.10*lumps+0.05*strokes+0.004*fbm(S,1.5,seed+2,fmin=150)
    # wiggly hairline cracks: domain-warped voronoi edges, only in a few zones
    wx=(x+fbm(S,2.6,seed+11,fmin=4)*0.012)%1; wy=(y+fbm(S,2.6,seed+12,fmin=4)*0.012)%1
    pts=rng.uniform(0,1,(40,2)); F1,F2,ID=voronoi(wx,wy,pts)
    e=F2-F1; cm=smooth(1.0,1.6,fbm(S,3.2,seed+3,fmin=2))
    crack=(1-smooth(0.0006,0.0022,e))*cm
    # a few larger patches of fallen plaster showing brick
    pm=fbm(S,3.6,seed+4,fmin=1.5)+fbm(S,2.6,seed+5,fmin=8,fmax=60)*0.10
    patch=smooth(1.9,1.97,pm)
    rimz=smooth(1.75,1.9,pm)*(1-patch)
    nr=21; nbk=6
    br=(y*nr).astype(int); bv=(y*nr)%1; bxo=(x*nbk+0.5*(br%2))%nbk; bci=bxo.astype(int); bu=bxo%1
    bd=np.minimum(np.minimum(bu,1-bu)*S/nbk,np.minimum(bv,1-bv)*S/nr)
    bmask=smooth(2.0,3.5,bd); bprof=smooth(2,10,bd)
    hb=0.2+0.16*bmask*bprof
    h=hp*(1-patch)+hb*patch-0.2*crack*(1-patch)+0.03*rimz
    h=blur(np.clip(h,0,1),0.7)
    base=np.array([0.90,0.85,0.72],f32)
    col=base*(1+0.045*lumps[...,None])
    blot=smooth(0.3,1.6,fbm(S,3.0,seed+6,fmin=2))
    col=col*(1-blot[...,None])+np.array([0.84,0.77,0.62],f32)*blot[...,None]
    streak=smooth(0.9,2.3,fbm(S,2.4,seed+7,fmin=3,fmax=120,ay=7))
    col=col*(1-0.12*streak[...,None])
    bid=br*nbk+bci; bpal=np.array([(0.60,0.33,0.22),(0.52,0.29,0.20),(0.64,0.40,0.27),(0.56,0.36,0.25)],f32)
    bcol=bpal[(bid*7)%4]*(0.88+0.2*bprof[...,None])
    bcol=bcol*bmask[...,None]+np.array([0.62,0.58,0.52],f32)*(1-bmask[...,None])
    col=col*(1-patch[...,None])+bcol*patch[...,None]
    col=col*(1-0.12*rimz[...,None])
    col=col*(1-0.5*crack[...,None]*(1-patch[...,None]))
    rough=np.clip(0.92-0.05*patch+0.03*fbm(S,2.4,seed+8,fmin=6),0,1)
    PBR_SETS["T_VK_Plaster"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Plaster",col,h,rough,depth,tile,ao_in_albedo=0.45)
'''
t=bpy.data.texts["vk_texgen"]; t.clear(); t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(code)
for fn in (gen_stone,gen_ashlar,gen_plaster): fn()
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0143] 2026-09-23 03:20:54  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_texgen"]; s=t.as_string()
s=s.replace("    crack=(1-smooth(0.0006,0.0022,e))*cm","    crack=(1-smooth(0.0016,0.0042,e))*cm")
s=s.replace("    e=F2-F1; cm=smooth(1.0,1.6,fbm(S,3.2,seed+3,fmin=2))","    e=F2-F1; cm=smooth(1.2,1.7,fbm(S,3.4,seed+3,fmin=2))")
s=s.replace("    streak=smooth(0.9,2.3,fbm(S,2.4,seed+7,fmin=3,fmax=120,ay=7))\n    col=col*(1-0.12*streak[...,None])",
            "    streak=smooth(1.3,2.6,fbm(S,3.0,seed+7,fmin=2,fmax=60,ay=6))\n    col=col*(1-0.08*streak[...,None])")
s=s.replace("    return write_set(\"T_VK_Plaster\",col,h,rough,depth,tile,ao_in_albedo=0.45)",
            "    ao=cavity_ao(blur(h,2.5),radii=(6,24),k=(1.5,1.0),floor=0.5)\n    ao=np.minimum(ao,1-0.6*crack*(1-patch))\n    return write_set(\"T_VK_Plaster\",col,h,rough,depth,tile,ao=ao,ao_in_albedo=0.35)")
# softer, warmer painted variation instead of grey grunge
s=s.replace("    blot=smooth(0.3,1.6,fbm(S,3.0,seed+6,fmin=2))\n    col=col*(1-blot[...,None])+np.array([0.84,0.77,0.62],f32)*blot[...,None]",
            "    blot=smooth(0.2,1.8,fbm(S,3.2,seed+6,fmin=1.5))\n    col=col*(1-0.7*blot[...,None])+np.array([0.86,0.78,0.62],f32)*0.7*blot[...,None]\n    hi=smooth(0.5,2.0,fbm(S,3.2,seed+14,fmin=1.5))\n    col=col*(1-0.5*hi[...,None])+np.array([0.95,0.91,0.80],f32)*0.5*hi[...,None]")
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(s)
gen_plaster(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0144] 2026-09-23 03:21:18  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def draw_segments(S,segs):
    """segs: list of (x0,y0,x1,y1,width_px) in pixel coords. returns coverage field (0..1), tileable"""
    out=np.zeros((S,S),f32)
    for (x0,y0,x1,y1,w) in segs:
        for ox in (-S,0,S):
            for oy in (-S,0,S):
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
def crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None):
    segs=[]
    def walk(x,y,a,nsteps,w,depth):
        for i in range(nsteps):
            a+=rng.uniform(-0.55,0.55)
            if dirbias is not None: a=a*0.8+dirbias*0.2
            st=rng.uniform(*step_px); nx,ny=x+math.cos(a)*st,y+math.sin(a)*st
            ww=max(0.5,w*(1-i/nsteps*0.7))
            segs.append((x,y,nx,ny,ww)); x,y=nx,ny
            if depth<2 and rng.random()<branch: walk(x,y,a+rng.choice([-1,1])*rng.uniform(0.6,1.1),int(nsteps*0.4),ww*0.8,depth+1)
    for _ in range(n):
        walk(rng.uniform(0,S),rng.uniform(0,S),rng.uniform(0,2*math.pi),int(rng.uniform(*steps)),w0,0)
    return segs
'''
bpy.data.texts["vk_tex"].write(code)
t=bpy.data.texts["vk_texgen"]; s=t.as_string()
old_a=s.index("    # wiggly hairline cracks"); old_b=s.index("    # a few larger patches")
s=s[:old_a]+'''    # hairline cracks: branching random walks
    crack=draw_segments(S,crack_segments(S,rng,n=6,steps=(20,45),step_px=(5,10),w0=2.0,branch=0.12))
'''+s[old_b:]
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(s)
gen_plaster(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0145] 2026-09-23 03:21:47  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def gen_wood(S=1024,seed=41,tile=1.6,depth=0.022):
    rng=np.random.default_rng(seed); x,y=grid(S)
    warp=fbm(S,3.2,seed,fmin=1,ax=5)*0.035
    rings=np.sin(2*np.pi*(y*8+warp*4+fbm(S,2.8,seed+1,fmin=1,ax=7)*0.1)).astype(f32)
    fib=fbm(S,1.7,seed+2,fmin=6,ax=12)
    fib2=fbm(S,1.4,seed+3,fmin=30,ax=18)
    h=0.55+0.10*rings+0.09*fib+0.03*fib2
    # cracks along the grain (random walks biased to the x axis)
    cr=draw_segments(S,crack_segments(S,rng,n=5,steps=(25,50),step_px=(8,14),w0=3.0,branch=0.05,dirbias=0.0))
    cr=np.maximum(cr,draw_segments(S,crack_segments(S,rng,n=4,steps=(25,50),step_px=(8,14),w0=3.0,branch=0.05,dirbias=math.pi)))
    h-=0.35*cr
    # knots
    kn=np.zeros((S,S),f32); knr=np.zeros((S,S),f32)
    for kx,ky in rng.uniform(0,1,(3,2)):
        dx=((x-kx+0.5)%1-0.5)*2.4; dy=((y-ky+0.5)%1-0.5)*7.0
        d=np.hypot(dx,dy); kn=np.maximum(kn,np.exp(-(d/0.035)**2)); knr+=np.sin(d*150)*np.exp(-(d/0.1)**2)
    h+=0.05*knr-0.12*kn
    h=blur(np.clip(h,0,1),0.6)
    lum=0.58+0.14*rings+0.13*fib+0.05*fib2+0.06*knr-0.35*kn
    lum=np.clip(lum,0.1,1)[...,None]
    dark=np.array([0.19,0.11,0.06],f32); mid=np.array([0.44,0.28,0.15],f32); light=np.array([0.66,0.47,0.28],f32)
    col=np.where(lum<0.6,dark+(mid-dark)*(lum/0.6),mid+(light-mid)*((lum-0.6)/0.4))
    col*= (0.93+0.08*fbm(S,3.0,seed+4,fmin=1.5))[...,None]
    col*= (1-0.6*cr[...,None])
    light_=painted_light(normal_from_height(blur(h,2),depth*3,tile))
    col*= (0.85+0.28*light_[...,None])
    rough=np.clip(0.84+0.05*fib+0.1*cr,0,1)
    PBR_SETS["T_VK_Wood"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Wood",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.4)
def gen_planks(S=1024,seed=61,tile=2.0,depth=0.025):
    rng=np.random.default_rng(seed); x,y=grid(S)
    nb=8; b=np.minimum((x*nb).astype(int),nb-1); u=(x*nb)%1
    G=fbm(S,1.8,seed,fmin=4,ay=12); G2=fbm(S,1.5,seed+1,fmin=30,ay=18)
    rings=np.sin(2*np.pi*(x*37+fbm(S,3.0,seed+2,fmin=1,ay=6)*0.25)).astype(f32)
    shifts=rng.integers(0,S,nb); gr=np.empty_like(G); gr2=np.empty_like(G2)
    for i in range(nb):
        cols=slice(i*S//nb,(i+1)*S//nb)
        gr[:,cols]=np.roll(G,shifts[i],0)[:,cols]; gr2[:,cols]=np.roll(G2,shifts[i],0)[:,cols]
    btint=rng.uniform(0.82,1.1,nb).astype(f32); bgrey=(rng.random(nb)<0.3).astype(f32)
    edge=np.minimum(u,1-u)*S/nb
    gapm=smooth(1.5,4.0,edge)
    bow=1-((2*u-1)**2)*0.25
    h=gapm*(0.5+0.3*bow+0.07*gr+0.03*gr2+0.03*rings)+(1-gapm)*0.05
    # nails
    nail=np.zeros((S,S),f32)
    for i in range(nb):
        for yy in (0.06,0.56):
            cx=(i+0.5)/nb*S; cy=(yy+0.02*rng.uniform(-1,1))*S
            d=np.hypot(x*S-cx,y*S-cy); nail=np.maximum(nail,smooth(6,4,d))
    h=np.maximum(h,nail*0.9)
    cr=draw_segments(S,crack_segments(S,rng,n=6,steps=(15,35),step_px=(8,14),w0=2.2,branch=0.03,dirbias=math.pi/2))
    h-=0.3*cr*gapm
    h=blur(np.clip(h,0,1),0.6)
    lum=np.clip(0.58+0.13*gr+0.05*gr2+0.04*rings,0.1,1)[...,None]
    dark=np.array([0.22,0.13,0.07],f32); mid=np.array([0.46,0.30,0.17],f32); light=np.array([0.64,0.46,0.28],f32)
    col=np.where(lum<0.6,dark+(mid-dark)*(lum/0.6),mid+(light-mid)*((lum-0.6)/0.4))*btint[b][...,None]
    grey=np.array([0.46,0.43,0.38],f32)*(0.8+0.3*lum)
    col=col*(1-0.55*bgrey[b][...,None])+grey*0.55*bgrey[b][...,None]
    col=col*(0.35+0.65*gapm[...,None])*(1-0.5*cr[...,None])
    col=col*(1-nail[...,None])+np.array([0.16,0.16,0.18],f32)*nail[...,None]
    light_=painted_light(normal_from_height(blur(h,2),depth*3,tile))
    col*= (0.85+0.28*light_[...,None])
    rough=np.clip(0.86+0.04*gr-0.3*nail,0,1)
    PBR_SETS["T_VK_Planks"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Planks",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.4)
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
gen_wood(); gen_planks(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0146] 2026-09-23 03:22:13  blender  ok
# ==============================================================================================================
import bpy
tx=bpy.data.texts["vk_tex"]; s=tx.as_string()
s=s.replace("def crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None):",
            "def crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None,jit=0.55):")
s=s.replace("            a+=rng.uniform(-0.55,0.55)\n            if dirbias is not None: a=a*0.8+dirbias*0.2",
            "            a+=rng.uniform(-jit,jit)\n            if dirbias is not None: a=a*0.7+dirbias*0.3")
s=s.replace("        walk(rng.uniform(0,S),rng.uniform(0,S),rng.uniform(0,2*math.pi),int(rng.uniform(*steps)),w0,0)",
            "        a0=rng.uniform(0,2*math.pi) if dirbias is None else dirbias+rng.uniform(-0.2,0.2)\n        walk(rng.uniform(0,S),rng.uniform(0,S),a0,int(rng.uniform(*steps)),w0,0)")
tx.clear(); tx.write(s)
t=bpy.data.texts["vk_texgen"]; g=t.as_string()
g=g.replace('''    fib=fbm(S,1.7,seed+2,fmin=6,ax=12)
    fib2=fbm(S,1.4,seed+3,fmin=30,ax=18)
    h=0.55+0.10*rings+0.09*fib+0.03*fib2''','''    fib=fbm(S,2.2,seed+2,fmin=4,fmax=90,ax=10)
    fib2=fbm(S,1.8,seed+3,fmin=20,fmax=200,ax=16)
    h=0.55+0.10*rings+0.08*fib+0.015*fib2''')
g=g.replace('''    cr=draw_segments(S,crack_segments(S,rng,n=5,steps=(25,50),step_px=(8,14),w0=3.0,branch=0.05,dirbias=0.0))
    cr=np.maximum(cr,draw_segments(S,crack_segments(S,rng,n=4,steps=(25,50),step_px=(8,14),w0=3.0,branch=0.05,dirbias=math.pi)))''',
'''    cr=draw_segments(S,crack_segments(S,rng,n=7,steps=(20,45),step_px=(8,14),w0=2.6,branch=0.04,dirbias=0.0,jit=0.12))''')
g=g.replace("    lum=0.58+0.14*rings+0.13*fib+0.05*fib2+0.06*knr-0.35*kn","    lum=0.62+0.13*rings+0.12*fib+0.025*fib2+0.06*knr-0.35*kn")
g=g.replace("    cr=draw_segments(S,crack_segments(S,rng,n=6,steps=(15,35),step_px=(8,14),w0=2.2,branch=0.03,dirbias=math.pi/2))",
            "    cr=draw_segments(S,crack_segments(S,rng,n=6,steps=(15,35),step_px=(8,14),w0=2.2,branch=0.03,dirbias=math.pi/2,jit=0.12))")
t.clear(); t.write(g)
exec(bpy.data.texts["vk_tex"].as_string()); exec(g)
gen_wood(); gen_planks(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0147] 2026-09-23 03:22:49  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_texgen"]; g=t.as_string()
g=g.replace("    h+=0.05*knr-0.12*kn\n    h=blur(np.clip(h,0,1),0.6)\n    lum=0.62+0.13*rings+0.12*fib+0.025*fib2+0.06*knr-0.35*kn",
"""    gl=np.abs(np.sin(2*np.pi*(y*13+warp*6+fbm(S,3.0,seed+6,fmin=1,ax=8)*0.08)))
    gline=(1-smooth(0.02,0.07,gl))*smooth(-0.3,0.6,fbm(S,2.6,seed+7,fmin=2,ay=6))
    h+=0.05*knr-0.12*kn-0.06*gline
    h=blur(np.clip(h,0,1),0.6)
    lum=0.62+0.13*rings+0.12*fib+0.025*fib2+0.06*knr-0.35*kn-0.22*gline""")
code = r'''
def shingle_layout(S,seed,nrow=8,ncol=6):
    rng=np.random.default_rng(seed); x,y=grid(S)
    row=np.minimum((y*nrow).astype(int),nrow-1); v=(y*nrow)%1
    xo=(x*ncol+0.5*(row%2))%ncol; c=np.minimum(xo.astype(int),ncol-1); u=xo%1
    bl=rng.uniform(0.9,0.97,(nrow,ncol)).astype(f32)
    chip=fbm(S,2.6,seed+1,fmin=8,fmax=80)*0.012
    bottom=bl[row,c]-0.27*(1-np.sqrt(np.clip(1-(2*u-1)**2,0,1)))+chip
    inside=v<bottom
    t=np.clip(v/np.maximum(bottom,0.05),0,1)
    tv=rng.uniform(-1,1,(nrow,ncol)).astype(f32)
    return dict(row=row,c=c,u=u,v=v,bottom=bottom,inside=inside,t=t,tilt=tv,rng=rng)
def shingle_height(L,S,seed):
    u,t,inside=L["u"],L["t"],L["inside"]
    across=1-((2*u-1)**2)*0.35
    gapm=smooth(0.0,0.035,np.minimum(u,1-u))
    hin=(0.18+0.72*t**0.85*across+L["tilt"][L["row"],L["c"]]*(u-0.5)*0.18)*(0.55+0.45*gapm)
    hin+=facets(S,seed+3,8,60,0.035)
    hout=0.1+0.05*smooth(0.9,1.0,L["v"])
    return blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.8)
def gen_roofs(S=1024,seed=71,tile=3.0,depth=0.045):
    L=shingle_layout(S,seed); h=shingle_height(L,S,seed)
    ao=cavity_ao(h,radii=(3,10,24),k=(2.5,1.8,1.0),floor=0.3)
    # shadow band just below each rounded edge
    shadow=np.where(L["inside"],1.0,0.55+0.45*smooth(0,0.25,L["v"]-L["bottom"])).astype(f32)
    ao=np.minimum(ao,shadow)
    rng=L["rng"]; row,c,t,u=L["row"],L["c"],L["t"],L["u"]
    light=painted_light(normal_from_height(blur(h,2.5),depth*3,tile))
    def paint(pal,name,moss=0.0,mseed=0):
        pal=np.array(pal,f32); pick=rng.integers(0,len(pal),(8,6)); tint=rng.uniform(0.86,1.12,(8,6)).astype(f32)
        col=pal[pick[row,c]]*tint[row,c][...,None]
        col=col*(0.72+0.4*t[...,None]**0.8)*(0.85+0.25*light[...,None])
        col=col*(1+0.05*fbm(S,2.6,mseed+5,fmin=3,fmax=90)[...,None])
        rough=np.clip(0.68+0.08*fbm(S,2.4,mseed+6,fmin=6)+0.2*(1-L["inside"]),0,1).astype(f32)
        if moss>0:
            mz=smooth(0.6,1.6,fbm(S,3.0,mseed+7,fmin=2))*moss
            mz=mz*(0.6+0.4*(1-t))            # moss gathers at the top of each shingle / in overlaps
            mcol=np.array([0.30,0.42,0.12],f32)*(0.8+0.4*fbm(S,2.0,mseed+8,fmin=20)[...,None]*0.3)
            col=col*(1-mz[...,None])+mcol*mz[...,None]
            rough=np.clip(rough+0.2*mz,0,1)
        PBR_SETS[name]=dict(depth=depth,tile=tile)
        write_map(name+"_BC",col*(0.45+0.55*ao)[...,None])
        write_map(name+"_R",rough,True)
    paint([(0.70,0.26,0.15),(0.62,0.22,0.12),(0.74,0.32,0.18),(0.58,0.25,0.15)],"T_VK_RoofRed",0.0,71)
    paint([(0.22,0.33,0.55),(0.26,0.38,0.60),(0.19,0.29,0.48),(0.28,0.36,0.52)],"T_VK_RoofBlue",0.0,72)
    paint([(0.30,0.38,0.30),(0.26,0.34,0.28),(0.34,0.40,0.32),(0.24,0.30,0.27)],"T_VK_RoofGreen",0.55,73)
    for name in ("T_VK_RoofRed","T_VK_RoofBlue","T_VK_RoofGreen"):
        write_map(name+"_N",normal_from_height(h,depth,tile)*0.5+0.5,True)
        write_map(name+"_H",h,True); write_map(name+"_AO",ao,True)
def gen_thatch(S=1024,seed=81,tile=3.0,depth=0.07):
    rng=np.random.default_rng(seed); x,y=grid(S)
    nrow=6; row=np.minimum((y*nrow).astype(int),nrow-1); v=(y*nrow)%1
    edge=0.86+0.06*np.sin(2*np.pi*(x*9+row*0.37)).astype(f32)+0.05*fbm(S,2.4,seed,fmin=4,fmax=60)
    inside=v<edge
    t=np.clip(v/edge,0,1)
    strands=fbm(S,1.6,seed+1,fmin=20,fmax=300,ay=16)
    bundles=fbm(S,2.6,seed+2,fmin=3,fmax=40,ay=5)
    hin=0.25+0.62*t**0.7+0.07*strands+0.06*bundles
    hout=0.18+0.05*strands
    h=blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.7)
    ao=cavity_ao(h,radii=(3,10,30),k=(2.0,1.6,1.0),floor=0.3)
    shadow=np.where(inside,1.0,0.5+0.3*smooth(0,0.2,v-edge)).astype(f32); ao=np.minimum(ao,shadow)
    base=np.array([0.78,0.61,0.32],f32)
    col=base*(0.62+0.42*t[...,None]**0.8)*(0.85+0.15*strands[...,None]*0.5+0.1*bundles[...,None])
    grey=smooth(0.5,1.6,fbm(S,3.2,seed+3,fmin=1.5))
    col=col*(1-0.5*grey[...,None])+np.array([0.52,0.47,0.38],f32)*(0.6+0.4*t[...,None])*0.5*grey[...,None]
    moss=smooth(1.4,2.0,fbm(S,3.2,seed+4,fmin=2))*(1-t)
    col=col*(1-0.6*moss[...,None])+np.array([0.34,0.42,0.14],f32)*0.6*moss[...,None]
    rough=np.clip(0.9+0.05*strands,0,1)
    PBR_SETS["T_VK_Thatch"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Thatch",col.astype(f32),h,rough,depth,tile,ao=ao,ao_in_albedo=0.6)
'''
g=g+code; t.clear(); t.write(g)
exec(bpy.data.texts["vk_tex"].as_string()); exec(g)
gen_wood(); gen_roofs(); gen_thatch(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0148] 2026-09-23 03:23:24  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_texgen"]; g=t.as_string()
g=g.replace('''    tv=rng.uniform(-1,1,(nrow,ncol)).astype(f32)
    return dict(row=row,c=c,u=u,v=v,bottom=bottom,inside=inside,t=t,tilt=tv,rng=rng)''','''    tv=rng.uniform(-1,1,(nrow,ncol)).astype(f32)
    row2=(row+1)%nrow; xo2=(x*ncol+0.5*(row2%2))%ncol; c2=np.minimum(xo2.astype(int),ncol-1); u2=xo2%1
    return dict(row=row,c=c,u=u,v=v,bottom=bottom,inside=inside,t=t,tilt=tv,rng=rng,row2=row2,c2=c2,u2=u2)''')
g=g.replace('''    hout=0.1+0.05*smooth(0.9,1.0,L["v"])
    return blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.8)''','''    gap2=smooth(0.0,0.035,np.minimum(L["u2"],1-L["u2"]))
    hout=0.18*(0.55+0.45*gap2)*(1-((2*L["u2"]-1)**2)*0.35)
    return blur(np.clip(np.where(inside,hin,hout),0,1).astype(f32),0.8)''')
g=g.replace('''        col=pal[pick[row,c]]*tint[row,c][...,None]
        col=col*(0.72+0.4*t[...,None]**0.8)*(0.85+0.25*light[...,None])''','''        ins=L["inside"][...,None]
        col=np.where(ins,pal[pick[row,c]]*tint[row,c][...,None],pal[pick[L["row2"],L["c2"]]]*tint[L["row2"],L["c2"]][...,None])
        teff=np.where(L["inside"],t,0.0)[...,None]
        col=col*(0.72+0.4*teff**0.8)*(0.85+0.25*light[...,None])''')
g=g.replace("            mz=mz*(0.6+0.4*(1-t))","            mz=mz*(0.6+0.4*(1-np.where(L[\"inside\"],t,0.0)))")
# thatch continuity + calmer edge
g=g.replace("    edge=0.86+0.06*np.sin(2*np.pi*(x*9+row*0.37)).astype(f32)+0.05*fbm(S,2.4,seed,fmin=4,fmax=60)",
            "    edge=0.87+0.05*np.sin(2*np.pi*(x*9+row*0.37)).astype(f32)+0.03*fbm(S,2.8,seed,fmin=4,fmax=30)")
g=g.replace("    hout=0.18+0.05*strands","    hout=0.25+0.07*strands+0.06*bundles")
g=g.replace("    col=base*(0.62+0.42*t[...,None]**0.8)*(0.85+0.15*strands[...,None]*0.5+0.1*bundles[...,None])",
            "    teff=np.where(inside,t,0.0)[...,None]\n    col=base*(0.62+0.42*teff**0.8)*(0.85+0.15*strands[...,None]*0.5+0.1*bundles[...,None])")
g=g.replace("    moss=smooth(1.4,2.0,fbm(S,3.2,seed+4,fmin=2))*(1-t)","    moss=smooth(1.4,2.0,fbm(S,3.2,seed+4,fmin=2))*(1-teff[...,0])")
t.clear(); t.write(g)
exec(bpy.data.texts["vk_tex"].as_string()); exec(g)
gen_roofs(); gen_thatch(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0149] 2026-09-23 03:24:15  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def lattice(S,n=5):
    x,y=grid(S); a=(x+y)*n; b=(x-y)*n
    da=np.abs(a-np.round(a)); db=np.abs(b-np.round(b))
    lead=np.minimum(da,db); ia=np.floor(a).astype(int); ib=np.floor(b).astype(int)
    pane=np.minimum(da,db)   # distance to lead (in diamond units)
    return x,y,lead,ia,ib
def gen_window(S=512,seed=91,tile=1.0,depth=0.008):
    x,y,lead,ia,ib=lattice(S,5)
    lm=1-smooth(0.03,0.05,lead)
    bulge=smooth(0.04,0.3,lead)
    h=np.clip(0.35+0.25*bulge+0.02*fbm(S,3.0,seed,fmin=3,fmax=40)+0.55*lm,0,1)
    h=blur(h,0.6)
    glass=np.array([0.09,0.20,0.24],f32)+np.array([0.20,0.26,0.24],f32)*np.clip(1-y,0,1)[...,None]*0.7
    refl=np.exp(-(((x-y*0.6+0.35)%1-0.25)**2)/0.004)*0.35+np.exp(-(((x-y*0.6+0.35)%1-0.36)**2)/0.0008)*0.25
    pv=(np.sin(ia*12.9+ib*7.3)*0.5+0.5).astype(f32)*0.12
    col=glass*(0.85+pv[...,None])+refl[...,None]*np.array([0.85,0.95,1.0],f32)
    col=col*(1-lm[...,None])+np.array([0.13,0.13,0.14],f32)*lm[...,None]
    rough=np.clip(0.06+0.5*lm,0,1)
    PBR_SETS["T_VK_Window"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Window",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.2)
def gen_stained(S=512,seed=92,tile=1.0,depth=0.008):
    x,y,lead,ia,ib=lattice(S,5)
    lm=1-smooth(0.035,0.055,lead)
    pal=np.array([(0.80,0.12,0.10),(0.12,0.28,0.80),(0.90,0.68,0.12),(0.12,0.58,0.26),(0.58,0.16,0.62),(0.16,0.48,0.80)],f32)
    hsh=(ia*7+ib*13)%len(pal)
    glow=0.75+0.35*smooth(0.05,0.3,lead)
    col=pal[hsh]*glow[...,None]*(0.9+0.12*fbm(S,2.6,seed,fmin=3,fmax=60)[...,None])
    col=col*(1-lm[...,None])+np.array([0.06,0.06,0.07],f32)*lm[...,None]
    h=blur(np.clip(0.4+0.2*smooth(0.04,0.3,lead)+0.55*lm,0,1),0.6)
    rough=np.clip(0.12+0.5*lm,0,1)
    PBR_SETS["T_VK_Stained"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Stained",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.15)
def gen_iron(S=512,seed=93,tile=0.5,depth=0.004):
    rng=np.random.default_rng(seed); x,y=grid(S)
    F1,F2,ID=voronoi(x,y,rng.uniform(0,1,(60,2)))
    dent=np.clip(F1/0.08,0,1)**0.7
    h=blur(np.clip(0.4+0.4*dent+0.05*fbm(S,2.4,seed+1,fmin=6),0,1),0.8)
    rust=smooth(0.7,1.5,fbm(S,2.8,seed+2,fmin=2))*(1-dent*0.6)
    base=np.array([0.20,0.20,0.23],f32)*(0.8+0.3*dent[...,None])
    col=base*(1-rust[...,None])+np.array([0.34,0.17,0.08],f32)*(0.8+0.3*fbm(S,2,seed+3,fmin=10)[...,None]*0.3)*rust[...,None]
    rough=np.clip(0.45+0.45*rust+0.05*fbm(S,2,seed+4,fmin=10),0,1)
    PBR_SETS["T_VK_Iron"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Iron",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.3,extra={"M":np.clip(0.85-0.8*rust,0,1)})
def gen_straw(S=1024,seed=94,tile=1.2,depth=0.02):
    h=np.zeros((S,S),f32)
    for i,ang in enumerate((0.35,1.2,2.1,2.75,-0.4)):
        st=fbm(S,1.5,seed+i,fmin=30,fmax=400,ax=18,angle=ang)
        h=np.maximum(h,np.clip(st*0.35+0.4,0,1))
    h=blur(h,0.6)
    base=np.array([0.86,0.68,0.32],f32)
    col=base*(0.55+0.55*h[...,None])*(0.95+0.08*fbm(S,3,seed+9,fmin=2)[...,None])
    dry=smooth(0.6,1.6,fbm(S,3,seed+10,fmin=2))
    col=col*(1-0.35*dry[...,None])+np.array([0.62,0.55,0.38],f32)*0.35*dry[...,None]*(0.55+0.55*h[...,None])
    rough=np.full((S,S),0.9,f32)
    PBR_SETS["T_VK_Straw"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Straw",col.astype(f32),h,rough,depth,tile,ao_in_albedo=0.5)
def weave(S,f,seed,irr=0.15):
    x,y=grid(S)
    xw=(x+fbm(S,3.0,seed,fmin=2)*0.002)%1; yw=(y+fbm(S,3.0,seed+1,fmin=2)*0.002)%1
    cx=(xw*f)%1; cy=(yw*f)%1; ix=(xw*f).astype(int); iy=(yw*f).astype(int)
    over=((ix+iy)%2==0)
    tx=np.sin(np.pi*cy)**0.7; ty=np.sin(np.pi*cx)**0.7
    alongx=0.75+0.25*np.cos(np.pi*(cx-0.5)); alongy=0.75+0.25*np.cos(np.pi*(cy-0.5))
    h=np.where(over,0.45+0.5*tx*alongx,0.45+0.5*ty*alongy).astype(f32)
    h=h*(1-irr+irr*(0.5+0.5*fbm(S,2.0,seed+2,fmin=f/4)))
    return blur(np.clip(h,0,1),0.5)
def gen_burlap(S=512,seed=95,tile=0.8,depth=0.004):
    h=weave(S,48,seed,0.25)
    col=np.array([0.64,0.52,0.34],f32)*(0.62+0.5*h[...,None])*(0.92+0.1*fbm(S,2.6,seed+5,fmin=2)[...,None])
    PBR_SETS["T_VK_Burlap"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Burlap",col.astype(f32),h,np.full((S,S),0.95,f32),depth,tile,ao_in_albedo=0.4)
def gen_cloth(S=512,seed=96,tile=0.5,depth=0.002):
    h=weave(S,64,seed,0.1)
    col=np.full((S,S,3),0.93,f32)*(0.84+0.18*h[...,None])*(0.96+0.05*fbm(S,2.6,seed+5,fmin=2)[...,None])
    PBR_SETS["T_VK_Cloth"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Cloth",col.astype(f32),h,np.full((S,S),0.85,f32),depth,tile,ao_in_albedo=0.3)
def gen_soil(S=512,seed=97,tile=1.0,depth=0.03):
    rng=np.random.default_rng(seed); x,y=grid(S)
    F1,F2,ID=voronoi(x,y,rng.uniform(0,1,(90,2)))
    clod=np.clip((F2-F1)/0.04,0,1)**0.5
    pF1,pF2,pID=voronoi(x,y,rng.uniform(0,1,(160,2)))
    peb=smooth(0.012,0.006,pF1)*(rng.random(160)<0.35)[pID]
    h=blur(np.clip(0.3+0.35*clod+0.1*fbm(S,2.4,seed+1,fmin=4)+0.35*peb,0,1),0.7)
    col=np.array([0.22,0.15,0.09],f32)*(0.75+0.45*clod[...,None])
    col=col*(1-peb[...,None])+np.array([0.48,0.44,0.38],f32)*peb[...,None]
    PBR_SETS["T_VK_Soil"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Soil",col.astype(f32),h,np.clip(0.95-0.2*peb,0,1),depth,tile,ao_in_albedo=0.5)
def gen_paper(S=512,seed=98,tile=0.3,depth=0.001):
    rng=np.random.default_rng(seed); x,y=grid(S)
    fib=fbm(S,1.6,seed,fmin=40)
    col=np.array([0.92,0.86,0.70],f32)*(0.95+0.04*fib[...,None])
    ink=np.zeros((S,S),f32)
    for r in range(9):
        yy=0.1+r*0.09
        segs=[]; xx=0.08+rng.uniform(0,0.05)
        while xx<0.9:
            L=rng.uniform(0.04,0.12); 
            pts=[(xx+i*L/6,yy+0.006*math.sin(i*2.1+r)+rng.uniform(-0.002,0.002)) for i in range(7)]
            for a,b in zip(pts[:-1],pts[1:]): segs.append((a[0]*S,a[1]*S,b[0]*S,b[1]*S,1.4))
            xx+=L+rng.uniform(0.02,0.04)
        ink=np.maximum(ink,draw_segments(S,segs))
    col=col*(1-0.8*ink[...,None])+np.array([0.12,0.09,0.07],f32)*0.8*ink[...,None]
    h=0.5+0.05*fib
    PBR_SETS["T_VK_Paper"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Paper",col.astype(f32),h.astype(f32),np.full((S,S),0.9,f32),depth,tile,ao_in_albedo=0.1)
def gen_water(S=512,seed=99,tile=1.0,depth=0.01):
    h=np.clip(0.5+0.2*fbm(S,3.2,seed,fmin=3),0,1)
    col=np.array([0.10,0.27,0.31],f32)*(0.9+0.2*fbm(S,3,seed+1,fmin=2)[...,None])*np.ones((S,S,1),f32)
    PBR_SETS["T_VK_Water"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Water",col.astype(f32),h.astype(f32),np.full((S,S),0.04,f32),depth,tile,ao_in_albedo=0.0)
def gen_paintedwood(S=1024,seed=100,tile=1.6,depth=0.02):
    # reuse the beam-wood generator for the bare wood, paint layer on top, chipped where the mask is low
    rng=np.random.default_rng(seed); x,y=grid(S)
    wood=bpy.data.images["T_VK_Wood_BC"]; wa=np.array(wood.pixels[:],f32).reshape(S,S,4)[::-1,:,:3]
    wh=np.array(bpy.data.images["T_VK_Wood_H"].pixels[:],f32).reshape(S,S,4)[::-1,:,0]
    chip=smooth(1.0,1.25,fbm(S,2.6,seed,fmin=3,fmax=80)+0.25*fbm(S,1.8,seed+1,fmin=30))
    paint=1-chip
    brush=fbm(S,2.2,seed+2,fmin=4,fmax=120,ax=8)
    pcol=np.full((S,S,3),0.86,f32)*(0.92+0.06*brush[...,None])
    col=wa*(1-paint[...,None])+pcol*paint[...,None]
    h=np.clip(wh*0.7+0.25*paint+0.02*brush*paint,0,1)
    rough=np.clip(0.55*paint+0.88*(1-paint),0,1)
    PBR_SETS["T_VK_PaintedWood"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_PaintedWood",col.astype(f32),h.astype(f32),rough.astype(f32),depth,tile,ao_in_albedo=0.35,extra={"Mask":paint})
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
import time
for fn in (gen_window,gen_stained,gen_iron,gen_straw,gen_burlap,gen_cloth,gen_soil,gen_paper,gen_water,gen_paintedwood):
    t0=time.time(); fn(); print(fn.__name__,round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: gen_window 0.3\ngen_stained 0.2\ngen_iron 0.3\ngen_straw 1.3\ngen_burlap 0.3\ngen_cloth 0.3\ngen_soil 0.4\ngen_
# paper 0.2\ngen_water 0.2\ngen_paintedwood 1.4\n"}

# ==============================================================================================================
# [0150] 2026-09-23 03:24:36  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
names=["Stone","Ashlar","Plaster","Wood","Planks","RoofRed","RoofBlue","RoofGreen","Thatch","Window","Stained","Iron","Straw","Burlap","Cloth","Soil","Paper","Water","PaintedWood"]
T=256; cols=10
def thumb(name):
    im=bpy.data.images[name]; W,H=im.size
    a=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1,:,:3]
    step=max(1,W//T); a=a[::step,::step][:T,:T]
    if a.shape[0]<T: a=np.pad(a,((0,T-a.shape[0]),(0,T-a.shape[1]),(0,0)))
    return a
tiles=[]
for n in names:
    tiles.append(thumb(f"T_VK_{n}_BC"))
for n in names:
    tiles.append(thumb(f"T_VK_{n}_N"))
rows=[]
per=len(names)
grid=[]
for block in range(2):
    items=tiles[block*per:(block+1)*per]
    for r in range(0,per,cols):
        row=items[r:r+cols]
        while len(row)<cols: row.append(np.zeros((T,T,3),np.float32))
        grid.append(np.concatenate(row,1))
sheet=np.concatenate(grid,0)
H,W=sheet.shape[:2]
img=bpy.data.images.new("_texsheet",W,H,alpha=False)
img.pixels.foreach_set(np.concatenate([sheet[::-1],np.ones((H,W,1),np.float32)],-1).ravel())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\_texsheet.png"
img.filepath_raw=out; img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
print(W,H)
# ---- result ----
# {"result":"Code executed successfully: 2560 1024\n"}

# ==============================================================================================================
# [0151] 2026-09-23 03:24:55  blender  ok
# ==============================================================================================================
import bpy
print(sorted([m.name for m in bpy.data.materials if m.name.startswith("M_VK")]))
# ---- result ----
# {"result":"Code executed successfully: ['M_VK_Apple', 'M_VK_Ashlar', 'M_VK_Bread', 'M_VK_Bronze', 'M_VK_Burlap', 'M_VK_Cloth_Blue', 'M_VK_Cloth_Cream'
# , 'M_VK_Cloth_Green', 'M_VK_Cloth_Red', 'M_VK_Cloth_Yellow', 'M_VK_FlowerPink', 'M_VK_FlowerYellow', 'M_VK_Glow', 'M_VK_Hay', 'M_VK_Iron', 'M_VK_Leaf'
# , 'M_VK_Paper', 'M_VK_Planks', 'M_VK_Plaster', 'M_VK_Plaster_Ochre', 'M_VK_Plaster_Rose', 'M_VK_Plaster_White', 'M_VK_Pumpkin', 'M_VK_RoofBlue', 'M_VK
# _RoofRed', 'M_VK_Roof_Blue', 'M_VK_Roof_Green', 'M_VK_Roof_Thatch', 'M_VK_Shutter_Blue', 'M_VK_Shutter_Green', 'M_VK_Shutter_Natural', 'M_VK_Shutter_R
# ed', 'M_VK_Shutter_Teal', 'M_VK_Soil', 'M_VK_Stained', 'M_VK_Steel', 'M_VK_Stone', 'M_VK_Thatch', 'M_VK_Water', 'M_VK_Window', 'M_VK_Wood']\n"}

# ==============================================================================================================
# [0152] 2026-09-23 03:25:51  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def pbr_material(mat,prefix,tint=None,nstr=1.0,metallic=0.0,rough_mul=1.0,emission=0.0,flat=None,paint=None,spec=0.3,metal_map=False):
    mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear(); L=nt.links
    out=nt.nodes.new("ShaderNodeOutputMaterial"); out.location=(900,0)
    b=nt.nodes.new("ShaderNodeBsdfPrincipled"); b.location=(550,0)
    uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"; uv.location=(-900,0)
    def tex(suffix,y):
        n=nt.nodes.new("ShaderNodeTexImage"); n.image=bpy.data.images[prefix+suffix]; n.location=(-650,y)
        L.new(uv.outputs[0],n.inputs[0]); return n
    bc=tex("_BC",300); nm=tex("_N",-300); rg=tex("_R",0)
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"; vc.location=(-300,500)
    col_out=bc.outputs[0]
    if flat is not None:
        # flat colour, modulated by the texture's value so the painted shading survives
        bw=nt.nodes.new("ShaderNodeRGBToBW"); bw.location=(-350,300); L.new(bc.outputs[0],bw.inputs[0])
        mf=nt.nodes.new("ShaderNodeMix"); mf.data_type="RGBA"; mf.blend_type="MULTIPLY"; mf.inputs[0].default_value=1.0
        mf.inputs[6].default_value=(*flat,1); L.new(bw.outputs[0],mf.inputs[7]); mf.location=(-150,300)
        col_out=mf.outputs[2]
    elif paint is not None:
        mk=tex("_Mask",600)
        mp=nt.nodes.new("ShaderNodeMix"); mp.data_type="RGBA"; mp.blend_type="MULTIPLY"; mp.inputs[0].default_value=1.0
        L.new(bc.outputs[0],mp.inputs[6]); mp.inputs[7].default_value=(*paint,1); mp.location=(-300,300)
        mm=nt.nodes.new("ShaderNodeMix"); mm.data_type="RGBA"; mm.blend_type="MIX"; mm.location=(-120,300)
        L.new(mk.outputs[0],mm.inputs[0]); L.new(bc.outputs[0],mm.inputs[6]); L.new(mp.outputs[2],mm.inputs[7])
        col_out=mm.outputs[2]
    elif tint is not None:
        mt=nt.nodes.new("ShaderNodeMix"); mt.data_type="RGBA"; mt.blend_type="MULTIPLY"; mt.inputs[0].default_value=1.0
        L.new(bc.outputs[0],mt.inputs[6]); mt.inputs[7].default_value=(*tint,1); mt.location=(-150,300)
        col_out=mt.outputs[2]
    mv=nt.nodes.new("ShaderNodeMix"); mv.data_type="RGBA"; mv.blend_type="MULTIPLY"; mv.inputs[0].default_value=1.0; mv.location=(150,300)
    L.new(col_out,mv.inputs[6]); L.new(vc.outputs[0],mv.inputs[7]); L.new(mv.outputs[2],b.inputs["Base Color"])
    rm=nt.nodes.new("ShaderNodeMath"); rm.operation="MULTIPLY"; rm.inputs[1].default_value=rough_mul; rm.location=(150,0)
    L.new(rg.outputs[0],rm.inputs[0]); L.new(rm.outputs[0],b.inputs["Roughness"])
    nmap=nt.nodes.new("ShaderNodeNormalMap"); nmap.uv_map="UVMap"; nmap.inputs["Strength"].default_value=nstr; nmap.location=(150,-300)
    L.new(nm.outputs[0],nmap.inputs["Color"]); L.new(nmap.outputs[0],b.inputs["Normal"])
    if metal_map:
        mm_=tex("_M",-600); L.new(mm_.outputs[0],b.inputs["Metallic"])
    else: b.inputs["Metallic"].default_value=metallic
    b.inputs["Specular IOR Level"].default_value=spec
    if emission>0:
        L.new(col_out,b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value=emission
    L.new(b.outputs[0],out.inputs[0])
    return mat
MAT_MAP={
 "M_VK_Stone":dict(prefix="T_VK_Stone",nstr=1.1),
 "M_VK_Ashlar":dict(prefix="T_VK_Ashlar",nstr=1.1),
 "M_VK_Plaster":dict(prefix="T_VK_Plaster"),
 "M_VK_Plaster_White":dict(prefix="T_VK_Plaster",tint=(1.06,1.08,1.12)),
 "M_VK_Plaster_Ochre":dict(prefix="T_VK_Plaster",tint=(1.03,0.84,0.56)),
 "M_VK_Plaster_Rose":dict(prefix="T_VK_Plaster",tint=(1.03,0.82,0.76)),
 "M_VK_Wood":dict(prefix="T_VK_Wood",nstr=1.2,spec=0.15),
 "M_VK_Planks":dict(prefix="T_VK_Planks",nstr=1.2,spec=0.15),
 "M_VK_RoofRed":dict(prefix="T_VK_RoofRed",nstr=1.1),
 "M_VK_RoofBlue":dict(prefix="T_VK_RoofBlue",nstr=1.1),
 "M_VK_Roof_Blue":dict(prefix="T_VK_RoofBlue",nstr=1.1),
 "M_VK_Roof_Green":dict(prefix="T_VK_RoofGreen",nstr=1.1),
 "M_VK_Roof_Thatch":dict(prefix="T_VK_Thatch",nstr=0.9,spec=0.1),
 "M_VK_Thatch":dict(prefix="T_VK_Thatch",nstr=0.9,spec=0.1),
 "M_VK_Window":dict(prefix="T_VK_Window",spec=0.5),
 "M_VK_Stained":dict(prefix="T_VK_Stained",emission=1.4,spec=0.5),
 "M_VK_Iron":dict(prefix="T_VK_Iron",metal_map=True),
 "M_VK_Bronze":dict(prefix="T_VK_Iron",flat=(1.9,1.25,0.55),metallic=0.9,rough_mul=0.7),
 "M_VK_Steel":dict(prefix="T_VK_Iron",flat=(1.6,1.65,1.75),metallic=0.9,rough_mul=0.6),
 "M_VK_Shutter_Teal":dict(prefix="T_VK_PaintedWood",paint=(0.24,0.52,0.52),spec=0.2),
 "M_VK_Shutter_Red":dict(prefix="T_VK_PaintedWood",paint=(0.66,0.16,0.11),spec=0.2),
 "M_VK_Shutter_Green":dict(prefix="T_VK_PaintedWood",paint=(0.27,0.48,0.18),spec=0.2),
 "M_VK_Shutter_Blue":dict(prefix="T_VK_PaintedWood",paint=(0.20,0.32,0.62),spec=0.2),
 "M_VK_Shutter_Natural":dict(prefix="T_VK_Wood",nstr=1.2,spec=0.15),
 "M_VK_Cloth_Red":dict(prefix="T_VK_Cloth",tint=(0.70,0.12,0.09),spec=0.2),
 "M_VK_Cloth_Cream":dict(prefix="T_VK_Cloth",tint=(1.0,0.93,0.74),spec=0.2),
 "M_VK_Cloth_Blue":dict(prefix="T_VK_Cloth",tint=(0.14,0.25,0.62),spec=0.2),
 "M_VK_Cloth_Green":dict(prefix="T_VK_Cloth",tint=(0.17,0.45,0.14),spec=0.2),
 "M_VK_Cloth_Yellow":dict(prefix="T_VK_Cloth",tint=(0.95,0.70,0.14),spec=0.2),
 "M_VK_Burlap":dict(prefix="T_VK_Burlap",spec=0.1),
 "M_VK_Hay":dict(prefix="T_VK_Straw",spec=0.1),
 "M_VK_Soil":dict(prefix="T_VK_Soil",spec=0.1),
 "M_VK_Paper":dict(prefix="T_VK_Paper",spec=0.1),
 "M_VK_Water":dict(prefix="T_VK_Water",nstr=0.6,spec=0.6),
}
def apply_pbr_all():
    for mn,kw in MAT_MAP.items():
        m=bpy.data.materials.get(mn)
        if m: pbr_material(m,**kw)
    v=bpy.data.materials.get("M_VK_Void") or bpy.data.materials.new("M_VK_Void")
    v.use_nodes=True; nt=v.node_tree; nt.nodes.clear()
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value=(0.015,0.012,0.01,1); b.inputs["Roughness"].default_value=1.0; b.inputs["Specular IOR Level"].default_value=0.0
    nt.links.new(b.outputs[0],o.inputs[0]); v.diffuse_color=(0.015,0.012,0.01,1)
'''
t=bpy.data.texts.get("vk_mat") or bpy.data.texts.new("vk_mat"); t.clear(); t.write(code)
exec(code); apply_pbr_all()
print("materials rebuilt")
# ---- result ----
# {"result":"Code executed successfully: materials rebuilt\n"}

# ==============================================================================================================
# [0153] 2026-09-23 03:26:26  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
def patch(s,old,new,count=1):
    n=s.count(old)
    assert n>=1, ("missing",old[:60])
    return s.replace(old,new) if count=="all" else s.replace(old,new,count)
s=patch(s,'''tex_mat("M_VK_Soil",None,1.0,flat=(0.20,0.13,0.08))]''','''tex_mat("M_VK_Soil",None,1.0,flat=(0.20,0.13,0.08)), tex_mat("M_VK_Void",None,1.0,flat=(0.015,0.012,0.01))]''')
s=patch(s,"THATCH,PLANKS,ASHLAR,BURLAP,SOIL=range(27)","THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID=range(28)")
# openings -> VOID
s=patch(s,"k.quad([(-0.4,-0.21,2.9),(0.4,-0.21,2.9),(0.4,-0.21,3.5),(-0.4,-0.21,3.5)],IRON,","k.quad([(-0.4,-0.21,2.9),(0.4,-0.21,2.9),(0.4,-0.21,3.5),(-0.4,-0.21,3.5)],VOID,")
s=patch(s,"k.quad([(-hw,-0.21,0.05),(hw,-0.21,0.05),(hw,-0.21,hd),(-hw,-0.21,hd)],IRON,","k.quad([(-hw,-0.21,0.05),(hw,-0.21,0.05),(hw,-0.21,hd),(-hw,-0.21,hd)],VOID,")
s=patch(s,"k.quad([(XF-0.02,-0.7,zd),(XF-0.02,0.7,zd),(XF-0.02,0.7,zd+hd),(XF-0.02,-0.7,zd+hd)],IRON,","k.quad([(XF-0.02,-0.7,zd),(XF-0.02,0.7,zd),(XF-0.02,0.7,zd+hd),(XF-0.02,-0.7,zd+hd)],VOID,")
s=patch(s,"sub.box((0,-W/2-0.02,3.6),(0.14,0.06,1.0),IRON,bevel=0)","sub.box((0,-W/2-0.02,3.6),(0.14,0.06,1.0),VOID,bevel=0)")
s=patch(s,"sub=Kit(); sub.box((0,-W/2-0.02,5.5),(0.18,0.06,1.1),IRON,bevel=0); merge_kit(k,sub,R)","sub=Kit(); sub.box((0,-W/2-0.02,5.5),(0.18,0.06,1.1),VOID,bevel=0); merge_kit(k,sub,R)")
s=patch(s,"sub.quad([(-0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.7),(-0.2,-1.61,zs+1.7)],IRON,","sub.quad([(-0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.2),(0.2,-1.61,zs+1.7),(-0.2,-1.61,zs+1.7)],VOID,")
s=patch(s,"k.quad([(-0.9,-0.9,0.5),(0.9,-0.9,0.5),(0.9,0.9,0.5),(-0.9,0.9,0.5)],WINDOW,uvs=[(0,0),(0.3,0),(0.3,0.3),(0,0.3)])  # dark water",
          "k.quad([(-0.9,-0.9,0.5),(0.9,-0.9,0.5),(0.9,0.9,0.5),(-0.9,0.9,0.5)],WATER,uvs=[(0,0),(1.8,0),(1.8,1.8),(0,1.8)])")
s=patch(s,"k.quad([(-0.9,-0.3,0.55),(0.9,-0.3,0.55),(0.9,0.3,0.55),(-0.9,0.3,0.55)],WATER,uvs=[(0,0),(1,0),(1,1),(0,1)])",
          "k.quad([(-0.9,-0.3,0.55),(0.9,-0.3,0.55),(0.9,0.3,0.55),(-0.9,0.3,0.55)],WATER,uvs=[(0,0),(1.8,0),(1.8,0.6),(0,0.6)])")
# tile sizes for the new sets
s=patch(s,"TILE={0:3.0,1:1.5,2:1.6,3:3.0,4:1.0,5:1.0,10:1.6,16:1.2,22:3.0,23:2.0,24:2.5,25:0.8}",
          "TILE={0:3.0,1:1.5,2:1.6,3:3.0,4:1.0,5:0.5,10:1.6,16:1.2,17:0.3,18:1.0,19:0.5,21:0.5,22:3.0,23:2.0,24:2.5,25:0.8,26:1.0,11:0.5,12:0.5}")
s+='''
exec(bpy.data.texts["vk_mat"].as_string())
_tex_mat_legacy=tex_mat
def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False,tint=None):
    m=bpy.data.materials.get(name)
    if m: return m
    if img and bpy.data.images.get(img+"_BC"):
        m=bpy.data.materials.new(name); return pbr_material(m,img,tint=tint)
    if img and img.startswith("T_VK_") and bpy.data.images.get(img.replace("T_VK_Wood","T_VK_Wood")+"_BC"):
        m=bpy.data.materials.new(name); return pbr_material(m,img,tint=tint)
    return _tex_mat_legacy(name,img,rough,flat,emit,alpha_clip,tint)
'''
t.clear(); t.write(s)
exec(s)
import time; t0=time.time()
full_rebuild()
print("rebuilt all in",round(time.time()-t0,1),"s")
# ---- result ----
# {"result":"Code executed successfully: rebuilt all in 2.8 s\n"}

# ==============================================================================================================
# [0154] 2026-09-23 03:26:46  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
for c in ("VK_Demo","VK_Village"):
    for o in bpy.data.collections[c].objects: o.hide_render=False
for c in ("VK_Test","VK_Showcase"):
    for o in bpy.data.collections[c].objects: o.hide_render=True
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cc=bpy.data.objects["VK_CameraClose"]; cc.data.lens=35
tgt=Vector((1,12.2,3.2)); cc.location=Vector((7.5,5.5,2.6))
cc.rotation_euler=(tgt-cc.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cc; SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=60
SC.render.filepath=os.path.join(out,"_pbr_test1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0155] 2026-09-23 03:27:32  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_texgen"]; g=t.as_string()
g=g.replace("    lum=0.62+0.13*rings+0.12*fib+0.025*fib2+0.06*knr-0.35*kn-0.22*gline",
            "    lum=0.55+0.06*rings+0.07*fib+0.02*fib2+0.05*knr-0.3*kn-0.16*gline")
g=g.replace('''    dark=np.array([0.19,0.11,0.06],f32); mid=np.array([0.44,0.28,0.15],f32); light=np.array([0.66,0.47,0.28],f32)
    col=np.where(lum<0.6,dark+(mid-dark)*(lum/0.6),mid+(light-mid)*((lum-0.6)/0.4))
    col*= (0.93+0.08*fbm(S,3.0,seed+4,fmin=1.5))[...,None]
    col*= (1-0.6*cr[...,None])''','''    dark=np.array([0.13,0.075,0.045],f32); mid=np.array([0.32,0.20,0.115],f32); light=np.array([0.50,0.35,0.21],f32)
    col=np.where(lum<0.6,dark+(mid-dark)*(lum/0.6),mid+(light-mid)*((lum-0.6)/0.4))
    col*= (0.93+0.08*fbm(S,3.0,seed+4,fmin=1.5))[...,None]
    grey=smooth(0.4,1.6,fbm(S,3.2,seed+8,fmin=1.5,ax=3))[...,None]*0.35
    col=col*(1-grey)+col.mean(-1,keepdims=True)*np.array([1.05,1.0,0.95],f32)*grey
    col*= (1-0.6*cr[...,None])''')
# plaster: warm, rarer patches
g=g.replace("    patch=smooth(1.9,1.97,pm)\n    rimz=smooth(1.75,1.9,pm)*(1-patch)",
            "    patch=smooth(2.25,2.32,pm)\n    rimz=smooth(2.1,2.25,pm)*(1-patch)")
g=g.replace("    base=np.array([0.90,0.85,0.72],f32)\n    col=base*(1+0.045*lumps[...,None])",
            "    base=np.array([0.93,0.85,0.67],f32)\n    col=base*(1+0.045*lumps[...,None])")
g=g.replace("    col=col*(1-0.7*blot[...,None])+np.array([0.86,0.78,0.62],f32)*0.7*blot[...,None]",
            "    col=col*(1-0.7*blot[...,None])+np.array([0.88,0.76,0.56],f32)*0.7*blot[...,None]")
t.clear(); t.write(g)
exec(bpy.data.texts["vk_tex"].as_string()); exec(g)
gen_wood(); gen_paintedwood(); gen_plaster()
# plaster tile a bit larger (less visible repeats)
h=bpy.data.texts["vk_helpers"]; s=h.as_string()
s=s.replace("TILE={0:3.0,1:1.5,","TILE={0:3.0,1:2.2,"); h.clear(); h.write(s)
exec(s); full_rebuild()
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_pbr_test1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0156] 2026-09-23 03:27:59  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_tex"]; s=t.as_string()
old='''    img=bpy.data.images.get(name)
    if img: bpy.data.images.remove(img)
    img=bpy.data.images.new(name,S,S,alpha=False,is_data=data)
    if data and img.colorspace_settings.name!="Non-Color": img.colorspace_settings.name="Non-Color"
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())'''
new='''    img=bpy.data.images.get(name)
    if img is None:
        img=bpy.data.images.new(name,S,S,alpha=False,is_data=data)
    else:
        if img.packed_file: img.unpack(method="REMOVE") if False else None
        if tuple(img.size)!=(S,S): img.scale(S,S)
    if data and img.colorspace_settings.name!="Non-Color": img.colorspace_settings.name="Non-Color"
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    img.update()'''
assert old in s
s=s.replace(old,new); t.clear(); t.write(s)
exec(s); exec(bpy.data.texts["vk_texgen"].as_string())
gen_wood(); gen_paintedwood(); gen_plaster()
exec(bpy.data.texts["vk_mat"].as_string()); apply_pbr_all()
# check every image node has an image
bad=[(m.name,n.name) for m in bpy.data.materials if m.use_nodes and m.name.startswith("M_VK") for n in m.node_tree.nodes if n.type=="TEX_IMAGE" and n.image is None]
print("broken nodes:",bad)
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_pbr_test1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: broken nodes: []\n"}

# ==============================================================================================================
# [0157] 2026-09-23 03:28:32  blender  ok
# ==============================================================================================================
import bpy
for img in bpy.data.images:
    if img.source in ("FILE","GENERATED") and img.name.startswith("T_VK") and img.has_data:
        try: img.pack()
        except Exception as e: print(img.name,e)
# drop orphan images (old single-texture versions no longer referenced)
orph=[i.name for i in bpy.data.images if i.users==0]
for n in orph: bpy.data.images.remove(bpy.data.images[n])
bpy.ops.wm.save_mainfile()
import os; print("orphans removed",len(orph), round(os.path.getsize(bpy.data.filepath)/1e6,1),"MB")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\norphans removed 51 107.2 MB\n"}

# ==============================================================================================================
# [0158] 2026-09-23 03:28:42  blender  ok
# ==============================================================================================================
import bpy
s=bpy.data.texts["vk_helpers"].as_string()
def show(name):
    a=s.index("def "+name+"(")
    b=s.find("\ndef ",a+5)
    print(s[a:b])
for n in ["plinth","batter","stone_panel","wall_stone_plain","wall_stone_window","ridge","chimney","roof_mid"]:
    show(n)
# ---- result ----
# {"result":"Code executed successfully: def plinth(k,x0=-1.5,x1=1.5):\n k.box(((x0+x1)/2,-0.05,0.18),(x1-x0,0.62,0.36),STONE,bevel=0)\ndef batter(k,amt
# =0.08):\n for v in k.bm.verts:\n if v.co.y<-0.2 and v.co.z<0.05: v.co.y-=amt\ndef stone_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25,mi=None):\n vs=k.box(((x0
# +x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),STONE if mi is None else mi,bevel=0)\n grid_cut(k,vs)\ndef wall_stone_plain(k):\n stone_panel(k,-1.5,1
# .5,0,H1); plinth(k); batter(k)\ndef wall_stone_window(k):\n x0,x1,z0,z1=-0.55,0.55,1.05,2.25\n stone_panel(k,-1.5,x0,0,H1); stone_panel(k,x1,1.5,0,H1)
# \n stone_panel(k,x0,x1,0,z0); stone_panel(k,x0,x1,z1,H1)\n plinth(k); batter(k); window_frame(k,x0,x1,z0,z1)\ndef ridge(k,x0,x1):\n n=max(1,int(round(
# (x1-x0)/0.75)))\n for i in range(n):\n xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n; xm=(xa+xb)/2\n k.box((xm,0,RIDGE+0.1+roof_sag(xm,0)),(xb-xa+0.04,0.36

# ==============================================================================================================
# [0159] 2026-09-23 03:31:09  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def gen_rock(S=1024,seed=111,tile=1.5,depth=0.05):
    rng=np.random.default_rng(seed); x,y=grid(S)
    h=0.5+0.16*fbm(S,3.0,seed,fmin=2)+facets(S,seed+1,3,30,0.20)+facets(S,seed+2,8,80,0.08)+0.006*fbm(S,1.6,seed+3,fmin=120)
    pits=smooth(1.7,2.3,fbm(S,2.2,seed+4,fmin=30,fmax=200))
    h=blur(np.clip(h-0.08*pits,0,1),0.7)
    n=normal_from_height(blur(h,2),depth*3,tile); light=painted_light(n)
    warm=smooth(-1,1,fbm(S,3.2,seed+5,fmin=1.5))[...,None]
    base=np.array([0.55,0.54,0.52],f32)*(1-warm)+np.array([0.68,0.61,0.50],f32)*warm
    col=base*(0.72+0.42*light[...,None])*(1+0.05*fbm(S,2.4,seed+6,fmin=4,fmax=100)[...,None])
    # crevices darker
    ao=cavity_ao(h,radii=(3,12,30),k=(3.0,2.2,1.4),floor=0.3)
    lich=smooth(1.6,2.1,fbm(S,2.4,seed+7,fmin=12,fmax=160))
    col=col*(1-0.6*lich[...,None])+np.array([0.80,0.70,0.36],f32)*0.6*lich[...,None]
    moss=smooth(1.2,1.9,fbm(S,3.0,seed+8,fmin=2))*smooth(0.3,0.7,n[...,1])
    col=col*(1-0.55*moss[...,None])+np.array([0.34,0.44,0.16],f32)*0.55*moss[...,None]
    rough=np.clip(0.82+0.06*fbm(S,2.4,seed+9,fmin=6)+0.08*moss,0,1)
    PBR_SETS["T_VK_Rock"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Rock",col.astype(f32),h,rough,depth,tile,ao=ao,ao_in_albedo=0.5)
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
gen_rock()
m=bpy.data.materials.get("M_VK_Rock") or bpy.data.materials.new("M_VK_Rock")
mc=bpy.data.materials.get("M_VK_Clay") or bpy.data.materials.new("M_VK_Clay")
exec(bpy.data.texts["vk_mat"].as_string())
pbr_material(m,"T_VK_Rock",nstr=1.2)
pbr_material(mc,"T_VK_Plaster",tint=(0.86,0.42,0.26),nstr=0.8)
mt=bpy.data.texts["vk_mat"]; ms=mt.as_string()
if '"M_VK_Rock"' not in ms:
    ms=ms.replace(' "M_VK_Water":dict(prefix="T_VK_Water",nstr=0.6,spec=0.6),',
                  ' "M_VK_Water":dict(prefix="T_VK_Water",nstr=0.6,spec=0.6),\n "M_VK_Rock":dict(prefix="T_VK_Rock",nstr=1.2),\n "M_VK_Clay":dict(prefix="T_VK_Plaster",tint=(0.86,0.42,0.26),nstr=0.8),')
    mt.clear(); mt.write(ms)
print("rock ok")
# ---- result ----
# {"result":"Code executed successfully: rock ok\n"}

# ==============================================================================================================
# [0160] 2026-09-23 03:31:53  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''tex_mat("M_VK_Void",None,1.0,flat=(0.015,0.012,0.01))]''','''tex_mat("M_VK_Void",None,1.0,flat=(0.015,0.012,0.01)), tex_mat("M_VK_Rock","T_VK_Rock"), tex_mat("M_VK_Clay",None,0.8,flat=(0.7,0.35,0.2))]''')
s=s.replace("THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID=range(28)","THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY=range(30)")
s=s.replace("22:3.0,23:2.0,24:2.5,25:0.8,26:1.0,11:0.5,12:0.5}","22:3.0,23:2.0,24:2.5,25:0.8,26:1.0,11:0.5,12:0.5,28:1.5,29:1.5}")
code = r'''
# =====================  DETAIL PASS (overrides)  =====================
def rock(k,c,size,seed,rot_z=0.0,tilt=0.12,mi=None,segs=2):
    rnd=random.Random(seed)
    k.box(c,size,ROCK if mi is None else mi,rot=(rnd.uniform(-tilt,tilt),rnd.uniform(-tilt,tilt),rot_z+rnd.uniform(-0.12,0.12)),
          bevel=min(size)*0.3,segs=segs,jitter=min(size)*0.13,seed=seed)
def plinth(k,x0=-1.5,x1=1.5,face=-0.25,seed=None):
    """chunky foundation rocks along the wall base (replaces the plain plinth)"""
    rnd=random.Random(int((x0*13+x1*7)*100) if seed is None else seed)
    k.box(((x0+x1)/2,-0.02,0.14),(x1-x0,0.5,0.28),STONE,bevel=0)
    x=x0
    while x<x1-0.12:
        w=min(rnd.uniform(0.42,0.8),x1-x)
        if x1-(x+w)<0.3: w=x1-x
        h=rnd.uniform(0.34,0.5); d=rnd.uniform(0.3,0.42)
        rock(k,(x+w/2,face+0.02,h/2-0.07),(w-0.06,d,h),seed=rnd.randrange(1<<30))
        x+=w
def wall_rocks(k,x0,x1,z0,z1,face=-0.25,n=5,seed=0,avoid=()):
    rnd=random.Random(seed); placed=0; tries=0
    while placed<n and tries<n*30:
        tries+=1
        w=rnd.uniform(0.28,0.55); h=rnd.uniform(0.17,0.3)
        x=rnd.uniform(x0+w/2+0.05,x1-w/2-0.05); z=rnd.uniform(z0+h/2+0.1,z1-h/2-0.1)
        if any(ax0-0.2<x<ax1+0.2 and az0-0.2<z<az1+0.2 for (ax0,ax1,az0,az1) in avoid): continue
        d=rnd.uniform(0.09,0.15)
        rock(k,(x,face-d/2+0.045,z),(w,d,h),seed=seed*31+tries,tilt=0.05,segs=1)
        placed+=1
def wall_stone_plain(k):
    stone_panel(k,-1.5,1.5,0,H1); plinth(k); batter(k)
    wall_rocks(k,-1.5,1.5,0.5,H1,n=6,seed=3)
def wall_stone_window(k):
    x0,x1,z0,z1=-0.55,0.55,1.05,2.25
    stone_panel(k,-1.5,x0,0,H1); stone_panel(k,x1,1.5,0,H1)
    stone_panel(k,x0,x1,0,z0); stone_panel(k,x0,x1,z1,H1)
    plinth(k); batter(k); window_frame(k,x0,x1,z0,z1)
    rock(k,(0,-0.3,z1+0.42),(1.5,0.22,0.3),seed=77,tilt=0.02)      # stone lintel
    wall_rocks(k,-1.5,1.5,0.5,H1,n=4,seed=5,avoid=((x0-0.6,x1+0.6,z0-0.3,z1+0.6),))
_wall_stone_door_base=wall_stone_door
def wall_stone_door(k):
    _wall_stone_door_base(k)
    wall_rocks(k,-1.5,1.5,0.5,H1,n=3,seed=7,avoid=((-1.15,1.15,0,3.0),))
    # studs on the door straps
    for zz in (0.45,1.55):
        for i in range(9):
            k.box((-0.56+i*0.14,-0.075,zz),(0.045,0.035,0.045),IRON,bevel=0.012)
def corner_stone(k):
    k.box((0,0,H1/2),(0.8,0.8,H1),STONE,bevel=0)
    rock(k,(-0.05,-0.05,0.18),(1.05,1.05,0.42),seed=11,tilt=0.03)
    z=0.36; i=0; rnd=random.Random(5)
    while z<H1-0.05:
        h=min(rnd.uniform(0.38,0.5),H1-z)
        long_x=(i%2==0)
        sx,sy=(1.05,0.62) if long_x else (0.62,1.05)
        rock(k,(-0.43+sx/2,-0.43+sy/2,z+h/2),(sx,sy,h-0.03),seed=i*17+3,tilt=0.02,segs=2)
        z+=h; i+=1
def pegs(k,xs,zs,y=-0.44,r=0.028):
    for x in xs:
        for z in zs: _cyl(k,(x,y,z),r,r*0.85,0.04,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
_timber_frame_base=timber_frame
def timber_frame(k,window=False,pattern="V"):
    _timber_frame_base(k,window,pattern)
    xs=(-1.5,-0.72,0.72) if window else ((-1.5,0.0) if pattern!="K" else (-1.5,-0.75,0.0,0.75))
    pegs(k,xs,(0.42,H2-0.33))
    k.box((0,-0.42,0.02),(CELL,0.1,0.06),WOOD,bevel=0.02)   # drip moulding under the jetty beam
def eave_tabs(k,x0,x1,side,rows=2,L=0.46,th=0.065,w=0.5,seed=0):
    rnd=random.Random(seed+int(x0*10)+side)
    ck,sk=math.cos(KICK),math.sin(KICK)
    X=Vector((1,0,0)); D=Vector((0,side*ck,-sk)); N=Vector((0,side*sk,ck))
    def zsurf(ay): return roof_z(ay)
    NS=9
    for r in range(rows):
        ay_top=EAVE+0.09-L-r*L*0.52
        base=Vector((0,side*ay_top,zsurf(ay_top)))
        start=x0 if r==0 else x0-w/2
        i=0
        while True:
            xa=start+i*w; i+=1
            if xa>=x1-1e-4: break
            ua=max(0.0,(x0-xa)/w); ub=min(1.0,(x1-xa)/w)
            if ub-ua<0.05: continue
            c=rnd.randrange(6); jz=rnd.uniform(-0.01,0.012); jy=rnd.uniform(-0.03,0.03)
            us=[ua+(ub-ua)*j/(NS-1) for j in range(NS)]
            def bot(u): return L-0.125*(1-math.sqrt(max(0.0,1-(2*u-1)**2)))+jy
            lift0=0.01+(th*0.85 if r>0 else 0.0)*0.0
            def P(u,yl,zl):
                zz=zl+0.012+(th*0.9*(yl/L) if r>0 else 0.0)+jz
                return base+X*(xa+u*w)+D*yl+N*zz
            top=[k.bm.verts.new(P(u,0.0,th)) for u in us]+[k.bm.verts.new(P(u,bot(u),th)) for u in reversed(us)]
            btm=[k.bm.verts.new(P(u,0.0,0.0)) for u in us]+[k.bm.verts.new(P(u,bot(u),0.0)) for u in reversed(us)]
            n=len(top)
            ft=k.bm.faces.new(top); fb=k.bm.faces.new(list(reversed(btm)))
            sides=[k.bm.faces.new((top[j],btm[j],btm[(j+1)%n],top[(j+1)%n])) for j in range(n)]
            k.bm.normal_update()
            if ft.normal.dot(N)<0:
                for f in [ft,fb]+sides: f.normal_flip()
            uvs=[((c+u)/6.0,1.0-0.0) for u in us]+[((c+u)/6.0,1.0-0.118*bot(u)/L) for u in reversed(us)]
            for f in [ft,fb]+sides:
                f.material_index=ROOF
            for l in ft.loops: l[k.uv].uv=uvs[top.index(l.vert)]
            for l in fb.loops: l[k.uv].uv=uvs[btm.index(l.vert)]
            for f in sides:
                for l in f.loops:
                    j=top.index(l.vert) if l.vert in top else btm.index(l.vert)
                    l[k.uv].uv=(uvs[j][0],uvs[j][1]-(0.004 if l.vert in btm else 0.0))
def ridge(k,x0,x1):
    n=max(1,int(round((x1-x0)/0.5)))
    for i in range(n):
        xa=x0+(x1-x0)*i/n; xb=x0+(x1-x0)*(i+1)/n; xm=(xa+xb)/2
        _cyl(k,(xm,0,RIDGE+0.04+roof_sag(xm,0)),0.21,0.175,xb-xa+0.06,10,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
def roof_mid(k):
    for s in(-1,1): roof_slab(k,-1.5,1.5,s); eave_tabs(k,-1.5,1.5,s)
    ridge(k,-1.5,1.5)
def roof_gable(k):
    for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
    ridge(k,-1.5,GX+0.1); gable_end(k)
def roof_gable_kind(kind):
    def fn(k):
        for s in(-1,1): roof_slab(k,-1.5,GX,s,end_caps=(False,True)); eave_tabs(k,-1.5,GX,s)
        ridge(k,-1.5,GX+0.1); gable_end(k,kind)
    return fn
_roof_L_corner_base=roof_L_corner
def roof_L_corner(k):
    _roof_L_corner_base(k)
    GO=-HALF-(GX-1.5)
    eave_tabs(k,GO,3.0,-1)
def chimney(k):
    y0=1.3
    k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STONE,bevel=0.06,segs=2)
    rock(k,(0,y0,RIDGE+1.55),(1.25,1.25,0.22),seed=21,tilt=0.02)
    rock(k,(0,y0,RIDGE+1.0),(1.12,1.12,0.16),seed=22,tilt=0.01,segs=1)
    for dx in(-0.22,0.22):
        zb=RIDGE+1.66
        _cyl(k,(dx,y0,zb+0.22),0.15,0.115,0.44,12,CLAY)
        _cyl(k,(dx,y0,zb+0.47),0.145,0.145,0.07,12,CLAY)
        _cyl(k,(dx,y0,zb+0.505),0.1,0.1,0.01,10,VOID)
'''
t.clear(); t.write(s+code)
exec(bpy.data.texts["vk_helpers"].as_string())
import time; t0=time.time()
full_rebuild(); print("rebuilt",round(time.time()-t0,1))
for n in ["SM_VK_Wall_Stone","SM_VK_Wall_Stone_Window","SM_VK_Corner_Stone","SM_VK_Roof_Mid","SM_VK_Roof_Gable","SM_VK_Chimney","SM_VK_Wall_Timber"]:
    print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: rebuilt 2.9\nSM_VK_Wall_Stone 528\nSM_VK_Wall_Stone_Window 935\nSM_VK_Corner_Stone 384\nSM_VK_Roof_Mid 784\nSM_
# VK_Roof_Gable 2381\nSM_VK_Chimney 214\nSM_VK_Wall_Timber 492\n"}

# ==============================================================================================================
# [0161] 2026-09-23 03:32:11  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.camera=bpy.data.objects["VK_CameraClose"]; SC.render.resolution_percentage=60
SC.render.filepath=os.path.join(out,"_pbr_test1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
cam=bpy.data.objects["VK_Camera"]
# mid shot of plaza
cm=bpy.data.cameras.get("VK_CamMid") or bpy.data.cameras.new("VK_CamMid"); cm.lens=30
co=bpy.data.objects.get("VK_CameraMid") or bpy.data.objects.new("VK_CameraMid",cm)
if co.name not in SC.collection.objects: SC.collection.objects.link(co)
tgt=Vector((-6,10,3.0)); co.location=Vector((8,-7,7.5))
co.rotation_euler=(tgt-co.location).to_track_quat("-Z","Y").to_euler()
SC.camera=co; SC.render.filepath=os.path.join(out,"_pbr_test2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0162] 2026-09-23 03:32:41  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
bpy.ops.wm.save_mainfile()
SC=bpy.data.scenes["VillageKit"]
for o in bpy.data.collections["VK_Showcase"].objects: o.hide_render=False
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=32
SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=50
tgt=Vector((-14,-196,3)); cs.location=tgt+Vector((11,-17,8))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_pbr_test3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
tgt=Vector((3,-170,5.5)); cs.location=tgt+Vector((16,-24,9))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_pbr_test4.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n"}

# ==============================================================================================================
# [0163] 2026-09-23 03:34:26  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def gen_clock(S=512,seed=121):
    x,y=grid(S); cx=x-0.5; cy=y-0.5; r=np.sqrt(cx*cx+cy*cy); a=np.arctan2(cx,-cy)   # a=0 at 12 o'clock
    col=np.zeros((S,S,3),f32)+np.array([0.93,0.87,0.68],f32)*(0.95+0.05*fbm(S,2.5,seed,fmin=3)[...,None])
    ring=(smooth(0.415,0.425,r)-smooth(0.455,0.465,r))
    outer=smooth(0.465,0.475,r)
    col=col*(1-ring[...,None])+np.array([0.10,0.09,0.08],f32)*ring[...,None]
    col=col*(1-outer[...,None])+np.array([0.20,0.13,0.07],f32)*outer[...,None]
    h=np.full((S,S),0.5,f32)
    segs=[]
    for i in range(12):
        ang=2*math.pi*i/12; L0=0.34 if i%3 else 0.30; w=5.0 if i%3 else 9.0
        segs.append((S*(0.5+math.sin(ang)*L0),S*(0.5-math.cos(ang)*L0),S*(0.5+math.sin(ang)*0.40),S*(0.5-math.cos(ang)*0.40),w))
    # hands at 10:10
    for ang,L,w in ((2*math.pi*(10/12+10/720),0.2,11.0),(2*math.pi*(10/60),0.33,7.0)):
        segs.append((S*0.5,S*0.5,S*(0.5+math.sin(ang)*L),S*(0.5-math.cos(ang)*L),w))
    ink=draw_segments(S,segs)
    hub=smooth(0.025,0.018,r)
    ink=np.maximum(ink,hub)
    col=col*(1-ink[...,None])+np.array([0.08,0.07,0.06],f32)*ink[...,None]
    h=h+0.25*ink+0.15*ring-0.2*outer
    rough=np.clip(0.7-0.3*ink,0,1).astype(f32)
    PBR_SETS["T_VK_Clock"]=dict(depth=0.01,tile=1.1)
    return write_set("T_VK_Clock",col,h.astype(f32),rough,0.01,1.1,ao_in_albedo=0.2)
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
gen_clock()
m=bpy.data.materials.get("M_VK_Clock") or bpy.data.materials.new("M_VK_Clock")
exec(bpy.data.texts["vk_mat"].as_string()); pbr_material(m,"T_VK_Clock",nstr=0.8)
mt=bpy.data.texts["vk_mat"]; ms=mt.as_string()
if '"M_VK_Clock"' not in ms:
    ms=ms.replace(' "M_VK_Rock":dict(prefix="T_VK_Rock",nstr=1.2),',' "M_VK_Rock":dict(prefix="T_VK_Rock",nstr=1.2),\n "M_VK_Clock":dict(prefix="T_VK_Clock",nstr=0.8),')
    mt.clear(); mt.write(ms)
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0164] 2026-09-23 03:35:20  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''tex_mat("M_VK_Rock","T_VK_Rock"), tex_mat("M_VK_Clay",None,0.8,flat=(0.7,0.35,0.2))]''',
            '''tex_mat("M_VK_Rock","T_VK_Rock"), tex_mat("M_VK_Clay",None,0.8,flat=(0.7,0.35,0.2)), tex_mat("M_VK_Clock","T_VK_Clock")]''')
s=s.replace("THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY=range(30)","THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK=range(31)")
code = r'''
# =====================  TOWN-HALL PIECES  =====================
def arch_ring(k,hw,spring,y_front,y_back,mi=ROCK,n=9,depth_out=0.08,seed=0):
    rnd=random.Random(seed)
    for i in range(n):
        a=math.pi*(i+0.5)/n; r=hw+0.19
        ks=(i==n//2)
        k.box((math.cos(a)*r,(y_front+y_back)/2-depth_out/2,spring+math.sin(a)*r),
              (0.3 if not ks else 0.36,(y_back-y_front)+depth_out,0.42 if not ks else 0.56),mi,
              rot=(0,-(a-math.pi/2),0),bevel=0.05,segs=2,jitter=0.012,seed=seed*10+i)
def arch_cut_panels(k,hw,spring,top,y0,y1,mi):
    z=spring
    while z<spring+hw-0.005:
        dz=0.07; zc=min(z+dz,spring+hw)
        c=math.sqrt(max(0.0,hw*hw-((z+zc)/2-spring)**2))
        for sgn in(-1,1): k.box((sgn*(c+hw)/2,(y0+y1)/2,(z+zc)/2),(hw-c+0.002,y1-y0,zc-z),mi,bevel=0)
        z=zc
    if top>spring+hw: stone_panel(k,-hw,hw,spring+hw,top,y0,y1,mi=mi)
def arch_soffit(k,hw,spring,y0,y1,mi,n=16):
    for i in range(n):
        a0=math.pi*i/n; a1=math.pi*(i+1)/n
        v=[k.bm.verts.new((math.cos(a)*hw,y,spring+math.sin(a)*hw)) for a,y in ((a0,y0),(a1,y0),(a1,y1),(a0,y1))]
        f=k.bm.faces.new(v); f.material_index=mi
        for l,(uu,vv) in zip(f.loops,((a0*hw,y0),(a1*hw,y0),(a1*hw,y1),(a0*hw,y1))): l[k.uv].uv=(uu/TILE.get(mi,1.0),vv/TILE.get(mi,1.0))
def wall_arcade(k,mi=ASHLAR):
    hw=0.95; spring=1.72; y0,y1=-0.3,0.2; D=2.6
    stone_panel(k,-1.5,-hw,0,H1,y0,y1,mi=mi); stone_panel(k,hw,1.5,0,H1,y0,y1,mi=mi)
    arch_cut_panels(k,hw,spring,H1,y0,y1,mi); arch_soffit(k,hw,spring,y0,y1,mi)
    arch_ring(k,hw,spring,y0,y1,seed=3)
    for sgn in(-1,1):
        k.box((sgn*(hw+0.12),-0.08,spring-0.09),(0.46,0.62,0.18),ROCK,bevel=0.04,segs=2)      # impost
        rock(k,(sgn*(hw+0.26),-0.06,0.22),(0.6,0.66,0.44),seed=40+sgn,tilt=0.02)              # pier base
    k.box((0,-0.36,H1-0.12),(CELL,0.18,0.24),mi,bevel=0.04,segs=2)                            # string course
    # loggia behind the arch
    k.box((0,(y1+D)/2,0.04),(CELL,D-y1,0.08),mi,bevel=0)
    for x in (-1.5,1.5): k.box((x,(y1+D)/2,0.06),(0.02,D-y1,0.04),VOID,bevel=0)
    k.box((0,(y1+D)/2,H1-0.06),(CELL,D-y1,0.08),PLANKS,bevel=0)
    for x in (-1.1,-0.37,0.37,1.1): k.box((x,(y1+D)/2,H1-0.19),(0.16,D-y1,0.2),WOOD,bevel=0.03)
    # back (inner) facade: plaster with a door and a small window
    dx0,dx1,dz=-1.1,-0.1,2.2; wx0,wx1,wz0,wz1=0.35,1.05,1.0,2.0
    yb=D; yb1=D+0.2
    for (a,b,c,d) in ((-1.5,dx0,0,H1),(dx1,wx0,0,H1),(wx1,1.5,0,H1),(dx0,dx1,dz,H1),(wx0,wx1,0,wz0),(wx0,wx1,wz1,H1)):
        grid_cut(k,k.box(((a+b)/2,(yb+yb1)/2,(c+d)/2),(b-a,yb1-yb,d-c),PLASTER,bevel=0))
    for i in range(4):
        x=dx0+(i+0.5)*(dx1-dx0)/4; k.box((x,yb+0.1,dz/2),((dx1-dx0)/4-0.015,0.08,dz),PLANKS,bevel=0.01)
    for x in (dx0-0.07,dx1+0.07): k.box((x,yb-0.02,dz/2),(0.14,0.16,dz),WOOD,bevel=0.03)
    k.box(((dx0+dx1)/2,yb-0.02,dz+0.08),(dx1-dx0+0.3,0.18,0.16),WOOD,bevel=0.03)
    k.quad([(wx0,yb+0.06,wz0),(wx1,yb+0.06,wz0),(wx1,yb+0.06,wz1),(wx0,yb+0.06,wz1)],WINDOW,uvs=[(0,0),(0.7,0),(0.7,1.0),(0,1.0)])
    for x in (wx0-0.06,wx1+0.06): k.box((x,yb-0.02,(wz0+wz1)/2),(0.12,0.14,wz1-wz0+0.1),WOOD,bevel=0.025)
    for z in (wz0-0.05,wz1+0.05): k.box(((wx0+wx1)/2,yb-0.03,z),(wx1-wx0+0.3,0.16,0.12),WOOD,bevel=0.025)
    # hanging lantern
    k.box((0,1.3,H1-0.45),(0.02,0.02,0.5),IRON,bevel=0)
    k.box((0,1.3,H1-0.82),(0.24,0.24,0.3),GLOW,bevel=0.03)
    k.box((0,1.3,H1-0.64),(0.32,0.32,0.06),IRON,bevel=0.015); k.box((0,1.3,H1-0.99),(0.28,0.28,0.05),IRON,bevel=0.015)
def balcony(k):
    y0=-0.43; D_=0.95; W_=2.3; zf=0.34
    k.box((0,y0-D_/2,zf),(W_,D_,0.1),PLANKS,bevel=0.02)
    for x in (-0.95,0.0,0.95):
        k.box((x,y0-D_/2,zf-0.12),(0.14,D_,0.14),WOOD,bevel=0.03)
        L=math.hypot(0.75,0.8); th=math.atan2(0.8,-0.75)
        k.box((x,y0-0.37,zf-0.55),(0.12,L,0.12),WOOD,rot=(th,0,0),bevel=0.03)
    zt=zf+0.95
    for x in (-W_/2+0.06,W_/2-0.06):
        for y in (y0-0.05,y0-D_+0.06): k.box((x,y,(zf+zt)/2+0.02),(0.12,0.12,zt-zf+0.06),WOOD,bevel=0.03)
    k.box((0,y0-D_+0.06,zt),(W_,0.12,0.1),WOOD,bevel=0.03)
    k.box((0,y0-D_+0.06,zf+0.14),(W_,0.08,0.08),WOOD,bevel=0.02)
    for sgn in(-1,1):
        k.box((sgn*(W_/2-0.06),y0-D_/2,zt),(0.12,D_,0.1),WOOD,bevel=0.03)
        k.box((sgn*(W_/2-0.06),y0-D_/2,zf+0.14),(0.08,D_,0.08),WOOD,bevel=0.02)
    n=int(W_/0.16)
    for i in range(1,n):
        x=-W_/2+i*W_/n; _cyl(k,(x,y0-D_+0.06,(zf+zt)/2+0.05),0.03,0.03,zt-zf-0.2,6,WOOD)
    for sgn in(-1,1):
        for j in range(1,5):
            y=y0-j*D_/5; _cyl(k,(sgn*(W_/2-0.06),y,(zf+zt)/2+0.05),0.03,0.03,zt-zf-0.2,6,WOOD)
    # flower pots on the rail
    for x in (-0.7,0.6):
        _cyl(k,(x,y0-D_+0.06,zt+0.12),0.1,0.13,0.18,10,CLAY)
        for j in range(5):
            _ico(k,(x+0.06*math.cos(j*1.3),y0-D_+0.06+0.06*math.sin(j*1.3),zt+0.28),0.07,PINK if j%2 else LEAF,sub=1)
def clock_face(k,c,r,y_off=0.0):
    n=28; cx,cy,cz=c
    ring=[k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*r,cy+y_off,cz+math.sin(2*math.pi*i/n)*r)) for i in range(n)]
    ctr=k.bm.verts.new((cx,cy+y_off,cz))
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[(i+1)%n],ring[i])); f.material_index=CLOCK
        for l in f.loops:
            p=l.vert.co; l[k.uv].uv=(0.5-(p.x-cx)/(2*r)*0.94,0.5+(p.z-cz)/(2*r)*0.94)
    k.bm.normal_update()
def cupola(k):
    B=1.8; zb=RIDGE-1.4; zt=RIDGE+1.25
    grid_cut(k,k.box((0,0,(zb+zt)/2),(B,B,zt-zb),PLASTER,bevel=0))
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.06),sy*(B/2-0.06),(zb+zt)/2),(0.22,0.22,zt-zb),WOOD,bevel=0.04)
    k.box((0,0,zt+0.07),(B+0.36,B+0.36,0.18),WOOD,bevel=0.05,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2+0.02),zb+1.35),(B+0.1,0.12,0.14),WOOD,bevel=0.03)
        k.box((sgn*(B/2+0.02),0,zb+1.35),(0.12,B+0.1,0.14),WOOD,bevel=0.03)
    zc=RIDGE+0.42
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        clock_face(sub,(0,-B/2-0.07,zc),0.56)
        _cyl(sub,(0,-B/2-0.04,zc),0.64,0.64,0.07,28,WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
        merge_kit(k,sub,R)
    # belfry
    zb2=zt+0.16; hb=1.15
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.12),sy*(B/2-0.12),zb2+hb/2),(0.2,0.2,hb),WOOD,bevel=0.04,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2-0.12),zb2+hb-0.08),(B,0.18,0.16),WOOD,bevel=0.03)
        k.box((sgn*(B/2-0.12),0,zb2+hb-0.08),(0.18,B,0.16),WOOD,bevel=0.03)
        k.box((0,sgn*(B/2-0.12),zb2+0.35),(B,0.1,0.08),WOOD,bevel=0.02)
        k.box((sgn*(B/2-0.12),0,zb2+0.35),(0.1,B,0.08),WOOD,bevel=0.02)
    k.box((0,0,zb2+0.02),(B-0.1,B-0.1,0.06),PLANKS,bevel=0)
    k.box((0,0,zb2+hb-0.3),(1.2,0.12,0.12),WOOD,bevel=0.03)
    _cyl(k,(0,0,zb2+hb-0.62),0.33,0.16,0.52,14,BRONZE); _cyl(k,(0,0,zb2+hb-0.9),0.36,0.36,0.06,14,BRONZE)
    # roof: flared pyramid + spire
    zr=zb2+hb
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(B+0.7)/math.sqrt(2),radius2=0.04,depth=2.1)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zr+1.05))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.8)
    k.box((0,0,zr+2.3),(0.1,0.1,1.0),BRONZE,bevel=0.02)
    _ico(k,(0,0,zr+2.25),0.13,BRONZE,sub=1)
    k.box((0,0,zr+2.62),(0.9,0.04,0.04),IRON,bevel=0); k.box((0.42,0,zr+2.62),(0.12,0.03,0.18),IRON,rot=(0,0.785,0),bevel=0)
    k.box((-0.42,0,zr+2.66),(0.02,0.25,0.14),IRON,bevel=0)
EXTRA_SPECS+=[("SM_VK_Wall_Arcade",wall_arcade,dict(wobble=False,grime=True)),
              ("SM_VK_Balcony",balcony,dict(wobble=False,grime=False)),
              ("SM_VK_Roof_Cupola",cupola,dict(wobble=False,grime=False))]
# ---- multi-storey assembly (1..3 floors)
def _assemble(coll,origin,walls,corners,stories,style,r):
    gw,gc=_pieces(style)
    for (x,y,rot,c) in walls:
        if c=="A": place_v(coll,"SM_VK_Wall_Arcade",x,y,0,rot,origin,style); continue
        place_v(coll,gw[c],x,y,0,rot,origin,style); _dress(coll,origin,x,y,rot,c,r,style)
    for (x,y,rot) in corners: place_v(coll,gc,x,y,0,rot,origin,style)
    for lvl in range(1,stories):
        z=H1+H2*(lvl-1)
        for (x,y,rot,c) in walls:
            uc="W" if (c in "WDA" or r.random()<0.35) else "."
            place_v(coll,_upper(r,uc),x,y,z,rot,origin,style)
        for (x,y,rot) in corners: place_v(coll,"SM_VK_Corner_Timber",x,y,z,rot,origin,style)
def roof_top(stories): return H1+H2*(stories-1)
'''
t.clear(); t.write(s+code)
s=t.as_string()
# generalise the existing builders to use roof_top()
s=s.replace("    top=H1+(H2 if stories==2 else 0); sfx=\"\"","    top=roof_top(stories); sfx=\"\"")
s=s.replace('''    place_v(coll,f"SM_VK_InnerCorner_{g}",3,3,0,0,origin,style)
    if stories==2: place_v(coll,"SM_VK_InnerCorner_Timber",3,3,H1,0,origin,style)
    top=H1+(H2 if stories==2 else 0)''','''    place_v(coll,f"SM_VK_InnerCorner_{g}",3,3,0,0,origin,style)
    for lvl in range(1,stories): place_v(coll,"SM_VK_InnerCorner_Timber",3,3,H1+H2*(lvl-1),0,origin,style)
    top=roof_top(stories)''')
t.clear(); t.write(s)
exec(s)
full_rebuild(["SM_VK_Wall_Arcade","SM_VK_Balcony","SM_VK_Roof_Cupola"])
for n in ["SM_VK_Wall_Arcade","SM_VK_Balcony","SM_VK_Roof_Cupola"]: print(n,len(bpy.data.objects[n].data.polygons))
print("roof_top(3)" in s, s.count("roof_top(stories)"))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Arcade 1669\nSM_VK_Balcony 834\nSM_VK_Roof_Cupola 1120\nFalse 3\n"}

# ==============================================================================================================
# [0165] 2026-09-23 03:35:46  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def build_townhall(coll,origin,n=5,roof="Blue",seed=55):
    st={"ground":"Stone","plaster":"White","shutter":"Blue","roof":roof,"seed":seed}
    r=random.Random(seed); L=n*CELL
    walls=[(-L/2+1.5+3*i,-3,0,"A") for i in range(n)]
    walls+=[(-L/2+1.5+3*i,3,180,"W" if i!=n//2 else "D") for i in range(n)]
    walls+=[(-L/2,-1.5,-90,"."),(-L/2,1.5,-90,"W"),(L/2,1.5,90,"W"),(L/2,-1.5,90,".")]
    corners=[(-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)]
    gw,gc=_pieces(st)
    for (x,y,rot,c) in walls:
        if c=="A": place_v(coll,"SM_VK_Wall_Arcade",x,y,0,rot,origin,st)
        else: place_v(coll,gw[c],x,y,0,rot,origin,st)
    for (x,y,rot) in corners: place_v(coll,gc,x,y,0,rot,origin,st)
    for lvl in (1,2):
        z=H1+H2*(lvl-1)
        for (x,y,rot,c) in walls:
            if y==-3: pc="SM_VK_Wall_Timber_Window"
            elif c==".": pc=["SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K"][lvl-1]
            else: pc="SM_VK_Wall_Timber_Window" if (lvl==1 or r.random()<0.6) else "SM_VK_Wall_Timber"
            place_v(coll,pc,x,y,z,rot,origin,st)
        for (x,y,rot) in corners: place_v(coll,"SM_VK_Corner_Timber",x,y,z,rot,origin,st)
    place_v(coll,"SM_VK_Balcony",0,-3,H1,0,origin,st)
    top=roof_top(3)
    for i in range(n):
        x=-L/2+1.5+3*i
        if i==0: place_v(coll,"SM_VK_Roof_Gable",x,0,top,180,origin,st)
        elif i==n-1: place_v(coll,"SM_VK_Roof_Gable",x,0,top,0,origin,st)
        else: place_v(coll,"SM_VK_Roof_Mid",x,0,top,0,origin,st)
    place_v(coll,"SM_VK_Roof_Cupola",0,0,top,0,origin,st)
    place_v(coll,"SM_VK_Chimney",-L/2+4.5,0,top,180,origin,st); place_v(coll,"SM_VK_Chimney",L/2-4.5,0,top,180,origin,st)
    # square in front
    place_v(coll,"SM_VK_Prop_NoticeBoard",-L/2-1.0,-5.0,0,15,origin,{})
    for x in (-L/2+0.2,L/2-0.2): place_v(coll,"SM_VK_Prop_LampPost",x,-4.2,0,0,origin,{})
    for x in (-4.5,4.5): place_v(coll,"SM_VK_Prop_Bench",x,-5.2,0,0,origin,{})
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
S=vcol("VK_Showcase")
for o in [o for o in S.objects if o.get("bld")=="townhall"]: bpy.data.objects.remove(o)
before=set(o.name for o in S.objects)
build_townhall(S,(52,-172,0))
for o in S.objects:
    if o.name not in before: o["bld"]="townhall"
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((52,-172,5.5)); cs.location=tgt+Vector((13,-22,4))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.resolution_percentage=60
SC.render.filepath=os.path.join(out,"_th1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0166] 2026-09-23 03:36:08  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=28
tgt=Vector((52,-172,8.0)); cs.location=tgt+Vector((-14,-24,5))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_th2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
cs.data.lens=55
tgt=Vector((52,-172,15.5)); cs.location=tgt+Vector((5,-11,1.5))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_th3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0167] 2026-09-23 03:36:52  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def ring(k,c,r_in,r_out,depth,mi,n=28,axis="Y"):
    """flat annulus with thickness; axis = normal direction of the ring face (Y: faces -Y)"""
    cx,cy,cz=c
    def P(r,a,d):
        if axis=="Y": return (cx+math.cos(a)*r,cy+d,cz+math.sin(a)*r)
        return (cx+math.cos(a)*r,cy+math.sin(a)*r,cz+d)
    fo=[];fi=[];bo=[];bi=[]
    for i in range(n):
        a=2*math.pi*i/n
        fo.append(k.bm.verts.new(P(r_out,a,-depth/2))); fi.append(k.bm.verts.new(P(r_in,a,-depth/2)))
        bo.append(k.bm.verts.new(P(r_out,a,depth/2))); bi.append(k.bm.verts.new(P(r_in,a,depth/2)))
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.append(k.bm.faces.new((fo[i],fo[j],fi[j],fi[i])))
        fs.append(k.bm.faces.new((bo[j],bo[i],bi[i],bi[j])))
        fs.append(k.bm.faces.new((fo[j],fo[i],bo[i],bo[j])))
        fs.append(k.bm.faces.new((fi[i],fi[j],bi[j],bi[i])))
    k.bm.normal_update()
    # make outward-facing: check front face normal against axis
    probe=fs[0].normal
    want=Vector((0,-1,0)) if axis=="Y" else Vector((0,0,-1))
    if probe.dot(want)<0:
        for f in fs: f.normal_flip()
    k.project(fs,mi)
    return fs
def cupola(k):
    B=1.8; zb=RIDGE-1.4; zt=RIDGE+1.25
    grid_cut(k,k.box((0,0,(zb+zt)/2),(B,B,zt-zb),PLASTER,bevel=0))
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.06),sy*(B/2-0.06),(zb+zt)/2),(0.22,0.22,zt-zb),WOOD,bevel=0.04)
    k.box((0,0,zt+0.07),(B+0.36,B+0.36,0.18),WOOD,bevel=0.05,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2+0.02),zb+1.35),(B+0.1,0.12,0.14),WOOD,bevel=0.03)
        k.box((sgn*(B/2+0.02),0,zb+1.35),(0.12,B+0.1,0.14),WOOD,bevel=0.03)
    zc=RIDGE+0.42
    for a in range(4):
        R=Matrix.Rotation(a*math.pi/2,4,"Z"); sub=Kit()
        clock_face(sub,(0,-B/2-0.035,zc),0.5)
        ring(sub,(0,-B/2-0.05,zc),0.49,0.62,0.07,WOOD)
        for i in range(8):
            aa=2*math.pi*i/8+math.pi/8
            sub.box((math.cos(aa)*0.555,-B/2-0.095,zc+math.sin(aa)*0.555),(0.06,0.03,0.06),BRONZE,bevel=0.01)
        merge_kit(k,sub,R)
    zb2=zt+0.16; hb=1.15
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(B/2-0.12),sy*(B/2-0.12),zb2+hb/2),(0.2,0.2,hb),WOOD,bevel=0.04,segs=2)
    for sgn in(-1,1):
        k.box((0,sgn*(B/2-0.12),zb2+hb-0.08),(B,0.18,0.16),WOOD,bevel=0.03)
        k.box((sgn*(B/2-0.12),0,zb2+hb-0.08),(0.18,B,0.16),WOOD,bevel=0.03)
        k.box((0,sgn*(B/2-0.12),zb2+0.35),(B,0.1,0.08),WOOD,bevel=0.02)
        k.box((sgn*(B/2-0.12),0,zb2+0.35),(0.1,B,0.08),WOOD,bevel=0.02)
    k.box((0,0,zb2+0.02),(B-0.1,B-0.1,0.06),PLANKS,bevel=0)
    k.box((0,0,zb2+hb-0.3),(1.2,0.12,0.12),WOOD,bevel=0.03)
    bell(k,(0,0,zb2+hb-0.36),0.36)
    zr=zb2+hb
    sp=bmesh.ops.create_cone(k.bm,cap_ends=True,segments=4,radius1=(B+0.7)/math.sqrt(2),radius2=0.04,depth=2.1)["verts"]
    bmesh.ops.transform(k.bm,matrix=Matrix.Translation((0,0,zr+1.05))@Matrix.Rotation(math.pi/4,4,"Z"),verts=sp)
    fs=list({f for v in sp for f in v.link_faces}); k.bm.normal_update()
    for f in fs:
        f.material_index=ROOF; n=f.normal
        if abs(n.z)>0.99: continue
        U=Vector((-n.y,n.x,0)).normalized()
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.dot(U)/TILE[ROOF],-(abs(p.x)+abs(p.y))/TILE[ROOF]*0.8)
    k.box((0,0,zr+2.3),(0.1,0.1,1.0),BRONZE,bevel=0.02)
    _ico(k,(0,0,zr+2.25),0.13,BRONZE,sub=1)
    k.box((0,0,zr+2.62),(0.9,0.04,0.04),IRON,bevel=0); k.box((0.42,0,zr+2.62),(0.12,0.03,0.18),IRON,rot=(0,0.785,0),bevel=0)
    k.box((-0.42,0,zr+2.66),(0.02,0.25,0.14),IRON,bevel=0)
def bell(k,top,r):
    """proper bell profile (lathe), top = (x,y,z) of the crown"""
    prof=[(0.0,0.0),(0.34,0.0),(0.45,-0.08),(0.5,-0.3),(0.56,-0.62),(0.72,-0.9),(0.98,-1.02),(1.0,-1.1),(0.9,-1.1),(0.0,-1.0)]
    n=20; cx,cy,cz=top; rings=[]
    for (pr,pz) in prof:
        rings.append([k.bm.verts.new((cx+math.cos(2*math.pi*i/n)*pr*r,cy+math.sin(2*math.pi*i/n)*pr*r,cz+pz*r*1.3)) for i in range(n)])
    fs=[]
    for a,b in zip(rings[:-1],rings[1:]):
        for i in range(n):
            j=(i+1)%n; fs.append(k.bm.faces.new((a[i],a[j],b[j],b[i])))
    k.bm.normal_update()
    for f in fs: f.material_index=BRONZE; f.smooth=True
    # make normals point outward (away from axis) for the outer shell
    for f in fs:
        c=f.calc_center_median(); out=Vector((c.x-cx,c.y-cy,0))
        if out.length>1e-4 and f.normal.dot(out)<0 and f.calc_area()>0: pass
    k.project(fs,BRONZE)
    _cyl(k,(cx,cy,cz+0.08*r),0.12*r,0.12*r,0.18*r,8,IRON)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
exec(bpy.data.texts["vk_mat"].as_string())
pbr_material(bpy.data.materials["M_VK_Bronze"],"T_VK_Iron",flat=(3.4,2.2,0.95),metallic=1.0,rough_mul=0.75)
mt=bpy.data.texts["vk_mat"]; ms=mt.as_string()
ms=ms.replace(' "M_VK_Bronze":dict(prefix="T_VK_Iron",flat=(1.9,1.25,0.55),metallic=0.9,rough_mul=0.7),',' "M_VK_Bronze":dict(prefix="T_VK_Iron",flat=(3.4,2.2,0.95),metallic=1.0,rough_mul=0.75),')
mt.clear(); mt.write(ms)
full_rebuild(["SM_VK_Roof_Cupola"])
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=45
tgt=Vector((52,-172,14.5)); cs.location=tgt+Vector((6,-13,0.5))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_th3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0168] 2026-09-23 03:37:16  blender  ok
# ==============================================================================================================
import bpy, collections
o=[ob for ob in bpy.data.objects if ob.name.startswith("SM_VK_Roof_Cupola")]
for ob in o:
    me=ob.data
    cnt=collections.Counter(p.material_index for p in me.polygons)
    print(ob.name, me.name, len(me.materials), {me.materials[k].name if k<len(me.materials) else k:v for k,v in cnt.items() if k in (2,30)})
    faces30=[p for p in me.polygons if p.material_index==30]
    if faces30:
        import statistics
        print("clock face y range", min(me.vertices[v].co.y for p in faces30 for v in p.vertices), max(me.vertices[v].co.y for p in faces30 for v in p.vertices))
        print("normal sample", tuple(round(c,2) for c in faces30[0].normal))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Cupola SM_VK_Roof_Cupola 31 {'M_VK_Wood': 832, 'M_VK_Clock': 112}\nclock face y range -0.97000002861
# 02295 0.9700000882148743\nnormal sample (0.0, 1.0, 0.0)\nSM_VK_Roof_Cupola_inst VAR_5528802846007759055 31 {'M_VK_Wood': 832, 'M_VK_Clock': 112}\ncloc
# k face y range -0.9700000286102295 0.9700000882148743\nnormal sample (0.0, 1.0, 0.0)\n"}

# ==============================================================================================================
# [0169] 2026-09-23 03:37:52  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
old='''     ("SM_VK_Prop_BarrelStack",prop_barrelstack,ng),("SM_VK_Prop_Forge",prop_bellows_forge,ng)] + EXTRA_SPECS'''
assert old in s
s=s.replace(old,'''     ("SM_VK_Prop_BarrelStack",prop_barrelstack,ng),("SM_VK_Prop_Forge",prop_bellows_forge,ng)] + [(n_,_late(f_),kw_) for (n_,f_,kw_) in EXTRA_SPECS]''')
s=s.replace('''EXTRA_SPECS+= [("SM_VK_Roof_Gable_Stone",roof_gable_kind("stone"),dict(wobble=False,grime=False)),
               ("SM_VK_Roof_Gable_Planks",roof_gable_kind("planks"),dict(wobble=False,grime=False))]''',
'''EXTRA_SPECS+= [("SM_VK_Roof_Gable_Stone",lambda k: roof_gable_kind("stone")(k),dict(wobble=False,grime=False)),
               ("SM_VK_Roof_Gable_Planks",lambda k: roof_gable_kind("planks")(k),dict(wobble=False,grime=False))]''')
s=s.replace('''def full_rebuild(names=None):''','''def _late(fn):
    nm=getattr(fn,"__name__","")
    if nm and nm not in ("<lambda>","fn") and nm in globals(): return globals()[nm]
    return fn
def full_rebuild(names=None):''')
s=s.replace('''    for i in range(n):
        f=k.bm.faces.new((ctr,ring[(i+1)%n],ring[i])); f.material_index=CLOCK''','''    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[(i+1)%n])); f.material_index=CLOCK''')
t.clear(); t.write(s); exec(s)
full_rebuild()
import collections
me=bpy.data.objects["SM_VK_Roof_Cupola"].data
f30=[p for p in me.polygons if p.material_index==30]
print("clock normal", tuple(round(c,2) for c in f30[0].normal), "stone gable faces", len(bpy.data.objects["SM_VK_Roof_Gable_Stone"].data.polygons))
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.camera=bpy.data.objects["VK_CameraProps"]
SC.render.filepath=os.path.join(out,"_th3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: clock normal (-0.0, -1.0, -0.0) stone gable faces 3054\n"}

# ==============================================================================================================
# [0170] 2026-09-23 03:38:12  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
a=s.rindex("def cupola(k):"); b=s.index("\ndef ",a+10)
body=s[a:b].replace("zb+1.35","zb+0.75")
s=s[:a]+body+s[b:]
t.clear(); t.write(s); exec(s)
full_rebuild(["SM_VK_Roof_Cupola"])
bpy.ops.wm.save_mainfile(); print("saved")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nsaved\n"}

# ==============================================================================================================
# [0171] 2026-09-23 03:39:28  blender  ok
# ==============================================================================================================
import bpy
code = r'''
# =====================  THATCH ROOF SET  =====================
TRT=0.5
def _pnoise(x,seed=0.0):
    """periodic (3 m) smooth noise for thatch bumps"""
    return (0.5*math.sin(2*math.pi*x/3.0*2+seed)+0.3*math.sin(2*math.pi*x/3.0*5+1.7*seed+1.1)+0.2*math.sin(2*math.pi*x/3.0*11+2.3*seed+0.4))
def _new_faces_since(k,before):
    return [f for f in k.bm.faces if f.index==-1 or f not in before]
def thatch_slab(k,x0,x1,side,end_caps=(False,False)):
    global RT
    before=set(k.bm.faces); old=RT; RT=TRT
    try: roof_slab(k,x0,x1,side,end_caps)
    finally: RT=old
    for f in k.bm.faces:
        if f not in before: f.material_index=THATCH
def _kick_frame(side):
    ck,sk=math.cos(KICK),math.sin(KICK)
    D=Vector((0,side*ck,-sk)); N=Vector((0,side*sk,ck))
    return D,N
def thatch_eave_roll(k,x0,x1,side,seed=0.0):
    D,N=_kick_frame(side)
    Pt=Vector((0,side*EAVE,roof_z(EAVE)))
    C=Pt-N*(TRT/2)                    # centre of the roll = middle of slab thickness at the eave
    R=TRT/2+0.05
    nx=max(2,int(round((x1-x0)/0.2))); nt=10
    rings=[]
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx
        rr=R*(1+0.12*_pnoise(x,seed))
        row=[]
        for j in range(nt+1):
            th=math.pi/2-math.pi*j/nt               # +90 (top) -> -90 (bottom)
            p=C+Vector((x,0,0))+(D*math.cos(th)+N*math.sin(th))*rr-D*0.08
            row.append(k.bm.verts.new(p))
        rings.append(row)
    fs=[]
    for i in range(nx):
        for j in range(nt):
            f=k.bm.faces.new((rings[i][j],rings[i][j+1],rings[i+1][j+1],rings[i+1][j])); fs.append(f)
    k.bm.normal_update()
    probe=fs[len(fs)//2]
    if probe.normal.dot(D)<0:
        for f in fs: f.normal_flip()
    T=TILE[THATCH]
    for i in range(nx):
        for j in range(nt):
            f=fs[i*nt+j]; f.material_index=THATCH; f.smooth=True
            for l in f.loops:
                p=l.vert.co
                jj=[r_ for r_ in rings[i]+rings[i+1]].index(l.vert) if False else None
                l[k.uv].uv=(p.x/T,(0.02+0.06*((p-C).dot(N)+R)/(2*R))/1.0)
    return fs
def thatch_rake_roll(k,xg,seed=0.0):
    """rounded roll along the gable rake at x=xg (both slopes)"""
    prof=roof_profile()
    pts=[(-y,z) for (y,z) in reversed(prof)]+[(y,z) for (y,z) in prof[1:]]
    R=TRT/2+0.06; nt=10; rings=[]
    for idx,(y,z) in enumerate(pts):
        a=pts[max(idx-1,0)]; b=pts[min(idx+1,len(pts)-1)]
        ty,tz=b[0]-a[0],b[1]-a[1]; L=math.hypot(ty,tz); ty/=L; tz/=L
        ny,nz=-tz,ty
        if nz<0: ny,nz=-ny,-nz
        Nn=Vector((0,ny,nz)); X=Vector((1,0,0))
        C=Vector((xg-0.06,y,z))-Nn*(TRT/2)
        rr=R*(1+0.1*_pnoise(y*1.3,seed))
        row=[]
        for j in range(nt+1):
            th=math.pi/2-math.pi*j/nt
            row.append(k.bm.verts.new(C+(X*math.cos(th)+Nn*math.sin(th))*rr))
        rings.append(row)
    fs=[]
    for i in range(len(rings)-1):
        for j in range(nt):
            fs.append(k.bm.faces.new((rings[i][j],rings[i][j+1],rings[i+1][j+1],rings[i+1][j])))
    k.bm.normal_update()
    if fs[len(fs)//2].normal.x<0:
        for f in fs: f.normal_flip()
    T=TILE[THATCH]
    for f in fs:
        f.material_index=THATCH; f.smooth=True
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.y/T*0.5,0.03+0.05*((p.z%1.0)))
    # blobs where rake roll meets the eave roll
    for s_ in(-1,1):
        _ico(k,(xg-0.08,s_*(EAVE-0.05),roof_z(EAVE)-TRT/2),R*1.05,THATCH,sub=2,jit=0.02,seed=int(seed*10)+s_)
def thatch_ridge_cap(k,x0,x1):
    nx=max(2,int(round((x1-x0)/0.1))); ny=16
    grid_=[]
    for i in range(nx+1):
        x=x0+(x1-x0)*i/nx
        yend=0.78+0.16*(0.5-0.5*math.cos(2*math.pi*x/0.6))
        row=[]
        for j in range(ny+1):
            t=-1+2*j/ny; ay=abs(t)*yend
            thick=0.16*(1-abs(t)**5)+0.03
            z=roof_z(ay)+thick+0.02*(1-t*t)
            row.append(k.bm.verts.new((x,math.copysign(ay,t) if t!=0 else 0.0,z)))
        grid_.append(row)
    fs=[]
    for i in range(nx):
        for j in range(ny): fs.append(k.bm.faces.new((grid_[i][j],grid_[i+1][j],grid_[i+1][j+1],grid_[i][j+1])))
    # lips down to the roof on both sides
    for jside in (0,ny):
        for i in range(nx):
            a=grid_[i][jside]; b=grid_[i+1][jside]
            ay=abs(a.co.y); ay2=abs(b.co.y)
            a2=k.bm.verts.new((a.co.x,a.co.y,roof_z(ay)-0.02)); b2=k.bm.verts.new((b.co.x,b.co.y,roof_z(ay2)-0.02))
            fs.append(k.bm.faces.new((a,b,b2,a2)))
    k.bm.normal_update()
    for f in fs:
        if f.normal.z<-0.2 or (abs(f.normal.z)<0.5 and f.normal.y*f.calc_center_median().y<0): f.normal_flip()
        f.material_index=THATCH; f.smooth=True
        for l in f.loops: p=l.vert.co; l[k.uv].uv=(p.x/1.2,0.1+abs(p.y)/1.2)
    # liggers + zigzag spars
    for s_ in(-1,1):
        for ay in (0.36,0.66):
            _cyl(k,((x0+x1)/2,s_*ay,roof_z(ay)+0.16*(1-(ay/0.8)**5)+0.035),0.028,0.028,x1-x0,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
        n=int(round((x1-x0)/0.3))
        for i in range(n):
            xa=x0+i*(x1-x0)/n; xb=xa+(x1-x0)/n
            ya,yb=(0.36,0.66) if i%2==0 else (0.66,0.36)
            pa=Vector((xa,s_*ya,roof_z(ya)+0.17*(1-(ya/0.8)**5)+0.03)); pb=Vector((xb,s_*yb,roof_z(yb)+0.17*(1-(yb/0.8)**5)+0.03))
            d=pb-pa; L=d.length; c=(pa+pb)/2
            q=Vector((1,0,0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
            sub=Kit(); _cyl(sub,(0,0,0),0.02,0.02,L,5,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
            merge_kit(k,sub,Matrix.Translation(c)@q)
def roof_thatch_mid(k):
    for s in(-1,1): thatch_slab(k,-1.5,1.5,s); thatch_eave_roll(k,-1.5,1.5,s,seed=1.0+s)
    thatch_ridge_cap(k,-1.5,1.5)
def roof_thatch_gable_kind(kind="timber"):
    def fn(k):
        for s in(-1,1): thatch_slab(k,-1.5,GX,s,end_caps=(False,True)); thatch_eave_roll(k,-1.5,GX,s,seed=1.0+s)
        thatch_ridge_cap(k,-1.5,GX+0.05)
        thatch_rake_roll(k,GX,seed=2.0)
        gable_end(k,kind)
    return fn
EXTRA_SPECS+=[("SM_VK_RoofThatch_Mid",lambda k: roof_thatch_mid(k),dict(wobble=False,grime=False)),
              ("SM_VK_RoofThatch_Gable",lambda k: roof_thatch_gable_kind("timber")(k),dict(wobble=False,grime=False)),
              ("SM_VK_RoofThatch_Gable_Planks",lambda k: roof_thatch_gable_kind("planks")(k),dict(wobble=False,grime=False))]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
full_rebuild(["SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Gable","SM_VK_RoofThatch_Gable_Planks"])
for n in ["SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Gable"]: print(n,len(bpy.data.objects[n].data.polygons))
# quick test house
T=vcol("VK_Test")
for o in list(T.objects): bpy.data.objects.remove(o)
org=(80,-172,0)
st={"ground":"Plaster","plaster":"Cream","shutter":"Green","roof":"Red","seed":90}
L=3*CELL
for i in range(3):
    x=-L/2+1.5+3*i
    place_v(T,["SM_VK_Wall_Plaster_Window","SM_VK_Wall_Plaster_Door","SM_VK_Wall_Plaster_Window"][i],x,-3,0,0,org,st)
    place_v(T,"SM_VK_Wall_Plaster",x,3,0,180,org,st)
for yy in(-1.5,1.5):
    place_v(T,"SM_VK_Wall_Plaster_Window",-L/2,yy,0,-90,org,st); place_v(T,"SM_VK_Wall_Plaster",L/2,-yy,0,90,org,st)
for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): place_v(T,"SM_VK_Corner_Plaster",cx,cy,0,r,org,st)
for i in range(3):
    x=-L/2+1.5+3*i
    if i==0: place_v(T,"SM_VK_RoofThatch_Gable",x,0,H1,180,org,st)
    elif i==2: place_v(T,"SM_VK_RoofThatch_Gable",x,0,H1,0,org,st)
    else: place_v(T,"SM_VK_RoofThatch_Mid",x,0,H1,0,org,st)
place_v(T,"SM_VK_Chimney",-3,0,H1,0,org,st)
for o in T.objects: o.hide_render=False
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=32
tgt=Vector((80,-172,3.2)); cs.location=tgt+Vector((9,-13,4.5))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_th4.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_RoofThatch_Mid 1204\nSM_VK_RoofThatch_Gable 3239\n"}

# ==============================================================================================================
# [0172] 2026-09-23 03:40:02  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
old_head='''def gable_end(k,kind='timber'):
    # bargeboards following both slopes
    prof=roof_profile()
    for s in(-1,1):'''
assert old_head in s
s=s.replace(old_head,'''def gable_end(k,kind='timber',trim=True):
    # bargeboards following both slopes
    prof=roof_profile()
    for s in((-1,1) if trim else ()):''')
old_fin='''    # finial
    k.box((GX+0.08,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,segs=2)
    k.box((GX+0.08,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)'''
assert old_fin in s
s=s.replace(old_fin,'''    # finial
    if trim:
        k.box((GX+0.08,0,RIDGE+0.35),(0.2,0.2,0.9),WOOD,bevel=0.06,segs=2)
        k.box((GX+0.08,0,RIDGE+0.85),(0.3,0.3,0.3),WOOD,rot=(0,0,math.pi/4),bevel=0.1,segs=2)''')
s=s.replace('''        thatch_rake_roll(k,GX,seed=2.0)
        gable_end(k,kind)''','''        thatch_rake_roll(k,GX,seed=2.0)
        gable_end(k,kind,trim=False)''')
# --- builder: thatch support
old_roof='''    for i in range(n):
        x=-L/2+1.5+3*i
        pc="SM_VK_Roof_Gable" if i in (0,n-1) else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)'''
assert old_roof in s
s=s.replace(old_roof,'''    thatch=style.get("roof")=="Thatch"
    for i in range(n):
        x=-L/2+1.5+3*i
        if thatch: pc="SM_VK_RoofThatch_Gable" if i in (0,n-1) else "SM_VK_RoofThatch_Mid"
        else: pc="SM_VK_Roof_Gable" if i in (0,n-1) else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)''')
s=s.replace('''    if stories==1 or r.random()<0.6:
        for i in range(n):''','''    if (stories==1 or r.random()<0.6) and not thatch:
        for i in range(n):''')
old_rs='''    return {"ground":r.choices(["Stone","Plaster"],[0.6,0.4])[0],
            "plaster":r.choice(["Cream","White","Ochre","Rose","Cream"]),
            "shutter":r.choice(["Teal","Red","Green","Blue","Natural"]),
            "roof":r.choice(["Red","Blue","Green","Red"]),"seed":seed}'''
assert old_rs in s
s=s.replace(old_rs,'''    g=r.choices(["Stone","Plaster"],[0.6,0.4])[0]
    roofs=["Red","Blue","Green","Red"]+(["Thatch","Thatch"] if g=="Plaster" else ["Thatch"])
    return {"ground":g,
            "plaster":r.choice(["Cream","White","Ochre","Rose","Cream"]),
            "shutter":r.choice(["Teal","Red","Green","Blue","Natural"]),
            "roof":r.choice(roofs),"seed":seed}''')
s=s.replace('''def build_L_v(coll,origin,a,b,stories,style):
    r=random.Random(style["seed"]); XA=3+3*a; YB=3+3*b''','''def build_L_v(coll,origin,a,b,stories,style):
    if style.get("roof")=="Thatch": style=dict(style,roof="Red")
    r=random.Random(style["seed"]); XA=3+3*a; YB=3+3*b''')
# barn uses the thatch set
old_barn='''    for i in range(n):
        x=-L/2+1.5+3*i
        if i==0: P("SM_VK_Roof_Gable_Planks",x,0,HB,180)
        elif i==n-1: P("SM_VK_Roof_Gable_Planks",x,0,HB,0)
        else: P("SM_VK_Roof_Mid",x,0,HB,0)'''
assert old_barn in s
s=s.replace(old_barn,'''    for i in range(n):
        x=-L/2+1.5+3*i
        if roof=="Thatch":
            if i==0: P("SM_VK_RoofThatch_Gable_Planks",x,0,HB,180)
            elif i==n-1: P("SM_VK_RoofThatch_Gable_Planks",x,0,HB,0)
            else: P("SM_VK_RoofThatch_Mid",x,0,HB,0)
        else:
            if i==0: P("SM_VK_Roof_Gable_Planks",x,0,HB,180)
            elif i==n-1: P("SM_VK_Roof_Gable_Planks",x,0,HB,0)
            else: P("SM_VK_Roof_Mid",x,0,HB,0)''')
t.clear(); t.write(s); exec(s)
full_rebuild(["SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Gable","SM_VK_RoofThatch_Gable_Planks"])
# rebuild barn in showcase
S=vcol("VK_Showcase")
for o in [o for o in S.objects if (o.location.x+14)**2+(o.location.y+196)**2<15**2]: bpy.data.objects.remove(o)
build_barn(S,(-14,-196,0))
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=32
tgt=Vector((-14,-196,3)); cs.location=tgt+Vector((11,-17,7))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_th5.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0173] 2026-09-23 03:40:57  blender  ok
# ==============================================================================================================
import bpy
bpy.ops.wm.save_mainfile()
code = r'''
def _poly_fill(S,img,alpha,shape_fn,cx,cy,rad,ang,color_fn):
    x0=int(max(0,cx-rad-2)); x1=int(min(S,cx+rad+2)); y0=int(max(0,cy-rad-2)); y1=int(min(S,cy+rad+2))
    if x0>=x1 or y0>=y1: return
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
    dx=(xx-cx)/rad; dy=(yy-cy)/rad
    ca,sa=math.cos(ang),math.sin(ang)
    u=dx*ca+dy*sa; v=-dx*sa+dy*ca
    inside,shade=shape_fn(u,v)
    a=np.clip(inside,0,1)
    c=color_fn(u,v,shade)
    reg=img[y0:y1,x0:x1]; ar=alpha[y0:y1,x0:x1]
    reg[:]=reg*(1-a[...,None])+c*a[...,None]; ar[:]=np.maximum(ar,a)
def ivy_leaf(u,v):
    th=np.arctan2(u,-v); r=np.hypot(u,v)
    R=0.62+0.3*np.abs(np.cos(1.5*th))**0.6-0.12*(np.cos(th)<-0.3)
    inside=np.clip((R-r)*14,0,1)
    vein=np.minimum(np.abs(th),np.minimum(np.abs(th-2.1),np.abs(th+2.1)))
    shade=0.8+0.25*(-v)*0.5-0.18*np.exp(-(vein*r*6)**2)*(r<R)
    return inside,shade
def petal_flower(n=5,inner=0.28):
    def f(u,v):
        th=np.arctan2(v,u); r=np.hypot(u,v)
        R=0.55+0.45*np.abs(np.cos(n*th/2))**0.8
        inside=np.clip((R-r)*10,0,1)
        center=(r<inner).astype(f32)
        return inside,np.stack([center,r],-1)
    return f
def gen_foliage(S=1024,seed=141):
    rng=np.random.default_rng(seed)
    img=np.zeros((S,S,3),f32); alpha=np.zeros((S,S),f32); H=S//2
    greens=[np.array(c,f32) for c in [(0.16,0.36,0.08),(0.22,0.44,0.10),(0.28,0.50,0.12),(0.13,0.30,0.08),(0.34,0.52,0.16)]]
    def green_col(g):
        return lambda u,v,sh: (g[None,None,:]*sh[...,None]).astype(f32)
    # ---- cell (0,0): ivy
    ox,oy=0,0
    segs=[]
    for _ in range(4):
        x=ox+rng.uniform(60,H-60); y=oy+H-10; a=-math.pi/2+rng.uniform(-0.5,0.5)
        for i in range(22):
            a+=rng.uniform(-0.35,0.35); nx=x+math.cos(a)*20; ny=y+math.sin(a)*20
            if not (ox+20<nx<ox+H-20 and oy+20<ny<oy+H-20): break
            segs.append((x,y,nx,ny,3.0)); x,y=nx,ny
    stem=draw_segments(S,segs)
    img=img*(1-stem[...,None])+np.array([0.28,0.2,0.1],f32)*stem[...,None]; alpha=np.maximum(alpha,stem)
    for _ in range(95):
        cx=ox+rng.uniform(35,H-35); cy=oy+rng.uniform(35,H-35)
        _poly_fill(S,img,alpha,ivy_leaf,cx,cy,rng.uniform(22,36),rng.uniform(-0.9,0.9),green_col(greens[rng.integers(0,5)]*rng.uniform(0.85,1.15)))
    # ---- cell (1,0): pink flower cluster
    ox,oy=H,0
    for _ in range(40):
        cx=ox+rng.uniform(40,H-40); cy=oy+rng.uniform(H*0.35,H-30)
        _poly_fill(S,img,alpha,ivy_leaf,cx,cy,rng.uniform(22,32),rng.uniform(-1.2,1.2),green_col(greens[rng.integers(0,5)]))
    pinks=[np.array(c,f32) for c in [(0.92,0.35,0.62),(0.85,0.22,0.48),(0.98,0.55,0.75),(0.75,0.18,0.55)]]
    for _ in range(30):
        cx=ox+rng.uniform(45,H-45); cy=oy+rng.uniform(40,H*0.8)
        pc=pinks[rng.integers(0,4)]
        def colf(u,v,sh,pc=pc):
            center=sh[...,0]; r=sh[...,1]
            c=pc[None,None,:]*(0.75+0.35*np.clip(r,0,1))[...,None]
            return (c*(1-center[...,None])+np.array([0.98,0.85,0.25],f32)*center[...,None]).astype(f32)
        _poly_fill(S,img,alpha,petal_flower(5,0.22),cx,cy,rng.uniform(20,30),rng.uniform(0,6.28),colf)
    # ---- cell (0,1): white daisies + yellow
    ox,oy=0,H
    for _ in range(40):
        cx=ox+rng.uniform(40,H-40); cy=oy+rng.uniform(H*0.35,H-30)
        _poly_fill(S,img,alpha,ivy_leaf,cx,cy,rng.uniform(22,32),rng.uniform(-1.2,1.2),green_col(greens[rng.integers(0,5)]))
    for _ in range(30):
        cx=ox+rng.uniform(45,H-45); cy=oy+rng.uniform(40,H*0.8)
        pc=np.array([0.96,0.95,0.9],f32) if rng.random()<0.6 else np.array([0.98,0.8,0.2],f32)
        def colf(u,v,sh,pc=pc):
            center=sh[...,0]; r=sh[...,1]
            c=pc[None,None,:]*(0.8+0.25*np.clip(r,0,1))[...,None]
            return (c*(1-center[...,None])+np.array([0.95,0.65,0.1],f32)*center[...,None]).astype(f32)
        _poly_fill(S,img,alpha,petal_flower(8,0.3),cx,cy,rng.uniform(18,26),rng.uniform(0,6.28),colf)
    # ---- cell (1,1): grass tuft (blades from the bottom)
    ox,oy=H,H
    segs=[]
    blades=np.zeros((S,S),f32); bcol=np.zeros((S,S,3),f32)
    for _ in range(70):
        x=ox+rng.uniform(40,H-40); y=oy+H-8; a=-math.pi/2+rng.uniform(-0.45,0.45); L=rng.uniform(150,330); w=rng.uniform(6,11)
        pts=[]
        for i in range(10):
            t=i/9; pts.append((x+math.cos(a)*L*t+rng.uniform(-2,2),y+math.sin(a)*L*t)); a+=rng.uniform(-0.06,0.06)
        sg=[(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],w*(1-i/10)+1) for i in range(9)]
        cov=draw_segments(S,sg)
        g=greens[rng.integers(0,5)]*rng.uniform(0.9,1.25)
        tip=np.clip((oy+H-np.mgrid[0:S,0:S][0])/400.0,0,1)[...,None]
        c=g*(0.7+0.5*tip)
        img=img*(1-cov[...,None])+c*cov[...,None]; alpha=np.maximum(alpha,cov)
    # colour dilation for mips
    rgb=img.copy(); m=alpha>0.5
    for _ in range(12):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    rgba=np.concatenate([np.clip(rgb,0,1),alpha[...,None]],-1).astype(f32)
    name="T_VK_Foliage_BCA"
    im=bpy.data.images.get(name)
    if im is None: im=bpy.data.images.new(name,S,S,alpha=True)
    im.alpha_mode="STRAIGHT"
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel()); im.update()
    im.filepath_raw=os.path.join(TEXDIR,name+".png"); im.file_format="PNG"; im.save(); im.pack()
    return im
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
import time; t0=time.time(); gen_foliage(); print(round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n3.2\n"}

# ==============================================================================================================
# [0174] 2026-09-23 03:41:26  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_tex"]; s=t.as_string()
s=s.replace('''def draw_segments(S,segs):
    """segs: list of (x0,y0,x1,y1,width_px) in pixel coords. returns coverage field (0..1), tileable"""
    out=np.zeros((S,S),f32)
    for (x0,y0,x1,y1,w) in segs:
        for ox in (-S,0,S):
            for oy in (-S,0,S):''','''def draw_segments(S,segs,wrap=True):
    """segs: list of (x0,y0,x1,y1,width_px) in pixel coords. returns coverage field (0..1), tileable if wrap"""
    out=np.zeros((S,S),f32)
    offs=(-S,0,S) if wrap else (0,)
    for (x0,y0,x1,y1,w) in segs:
        for ox in offs:
            for oy in offs:''')
t.clear(); t.write(s)
g=bpy.data.texts["vk_texgen"]; gs=g.as_string()
a=gs.index("def gen_foliage(")
body=gs[a:]
body=body.replace("stem=draw_segments(S,segs)","stem=draw_segments(S,segs,wrap=False)").replace("cov=draw_segments(S,sg)","cov=draw_segments(S,sg,wrap=False)")
body=body.replace("x=ox+rng.uniform(40,H-40); y=oy+H-8; a=-math.pi/2+rng.uniform(-0.45,0.45); L=rng.uniform(150,330)",
                  "x=ox+rng.uniform(70,H-70); y=oy+H-8; a=-math.pi/2+rng.uniform(-0.3,0.3); L=rng.uniform(150,320)")
gs=gs[:a]+body; g.clear(); g.write(gs)
exec(s); exec(gs)
gen_foliage()
# foliage material: alpha clip, translucency, two-sided
m=bpy.data.materials.get("M_VK_Foliage") or bpy.data.materials.new("M_VK_Foliage")
m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); L=nt.links
o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"
tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images["T_VK_Foliage_BCA"]; L.new(uv.outputs[0],tx.inputs[0])
vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
mx=nt.nodes.new("ShaderNodeMix"); mx.data_type="RGBA"; mx.blend_type="MULTIPLY"; mx.inputs[0].default_value=1
L.new(tx.outputs["Color"],mx.inputs[6]); L.new(vc.outputs[0],mx.inputs[7]); L.new(mx.outputs[2],b.inputs["Base Color"])
gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5
L.new(tx.outputs["Alpha"],gt.inputs[0])
b.inputs["Roughness"].default_value=0.7; b.inputs["Specular IOR Level"].default_value=0.2
tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); L.new(mx.outputs[2],tr.inputs["Color"])
ms=nt.nodes.new("ShaderNodeMixShader"); ms.inputs[0].default_value=0.25
L.new(b.outputs[0],ms.inputs[1]); L.new(tr.outputs[0],ms.inputs[2])
tp=nt.nodes.new("ShaderNodeBsdfTransparent"); ms2=nt.nodes.new("ShaderNodeMixShader")
L.new(gt.outputs[0],ms2.inputs[0]); L.new(tp.outputs[0],ms2.inputs[1]); L.new(ms.outputs[0],ms2.inputs[2]); L.new(ms2.outputs[0],o.inputs[0])
m.use_backface_culling=False
try: m.surface_render_method="DITHERED"
except: pass
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0175] 2026-09-23 03:42:19  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''tex_mat("M_VK_Clock","T_VK_Clock")]''','''tex_mat("M_VK_Clock","T_VK_Clock"), bpy.data.materials["M_VK_Foliage"]]''')
s=s.replace("THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK=range(31)","THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE=range(32)")
code = r'''
# =====================  FOLIAGE CARDS  =====================
FOL_CELLS={"ivy":(0,0),"pink":(1,0),"daisy":(0,1),"grass":(1,1)}
def fol_uv(cell):
    cx,cy=FOL_CELLS[cell]; m=0.01
    return cx*0.5+m,cx*0.5+0.5-m,1-(cy*0.5+0.5)+m,1-cy*0.5-m
def card(k,center,right,up,w,h,cell,flip=False,bend=0.0):
    u0,u1,v0,v1=fol_uv(cell)
    if flip: u0,u1=u1,u0
    C=Vector(center); R=Vector(right).normalized(); U=Vector(up).normalized(); N=R.cross(U).normalized()
    vs=[];uvs=[]
    for j in range(3):
        for i in range(3):
            s_=i/2; t_=j/2
            p=C+R*(s_-0.5)*w+U*(t_-0.5)*h+N*bend*(1-(2*s_-1)**2)
            vs.append(k.bm.verts.new(p)); uvs.append((u0+(u1-u0)*s_,v0+(v1-v0)*t_))
    for j in range(2):
        for i in range(2):
            a=j*3+i; q=(a,a+1,a+4,a+3)
            f=k.bm.faces.new([vs[x] for x in q]); f.material_index=FOLIAGE; f.smooth=True
            for l,x in zip(f.loops,q): l[k.uv].uv=uvs[x]
def ivy_patch(k,seed=0,x0=-1.4,x1=1.2,top=2.6,face=-0.32,n=46,base_w=1.6):
    rnd=random.Random(seed)
    # vines
    for vi in range(3):
        x=rnd.uniform(x0+0.3,x1-0.3); z=0.05
        pts=[(x,z)]
        while z<top*rnd.uniform(0.7,1.0):
            x+=rnd.uniform(-0.25,0.25); z+=rnd.uniform(0.2,0.35); pts.append((max(x0,min(x1,x)),z))
        for (xa,za),(xb,zb) in zip(pts[:-1],pts[1:]):
            d=Vector((xb-xa,0,zb-za)); L=d.length
            q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
            sub=Kit(); _cyl(sub,(0,0,0),0.022,0.018,L+0.02,5,WOOD)
            merge_kit(k,sub,Matrix.Translation(((xa+xb)/2,face-0.02,(za+zb)/2))@q)
    for i in range(n):
        # denser at bottom, narrowing with height
        z=top*(rnd.random()**1.4); spread=base_w*(1-0.55*z/top)
        cxm=(x0+x1)/2; x=cxm+rnd.uniform(-spread/2,spread/2)
        x=max(x0+0.15,min(x1-0.15,x))
        sz=rnd.uniform(0.38,0.62)
        ang=rnd.uniform(-0.6,0.6)
        R=Vector((math.cos(ang),0,math.sin(ang))); U=Vector((-math.sin(ang),0,math.cos(ang)))
        tilt=rnd.uniform(0.15,0.5)
        U=(U+Vector((0,-tilt,0))).normalized()
        card(k,(x,face-rnd.uniform(0.03,0.14),z+0.1),R,U,sz,sz,"ivy",flip=rnd.random()<0.5,bend=-0.05)
def deco_weeds(k,seed=0,x0=-1.5,x1=1.5,y=-0.48):
    rnd=random.Random(seed); x=x0+0.1
    while x<x1-0.1:
        w=rnd.uniform(0.35,0.6); h=w*rnd.uniform(0.7,1.0)
        cell="grass" if rnd.random()<0.75 else "daisy"
        for a in (0.0,math.pi/2.5):
            aa=a+rnd.uniform(-0.4,0.4)
            R=Vector((math.cos(aa),math.sin(aa),0)); card(k,(x,y+rnd.uniform(-0.12,0.08),h/2-0.03),R,(0,0,1),w,h,cell,flip=rnd.random()<0.5)
        x+=rnd.uniform(0.18,0.4)
def deco_bush(k,seed=0,r=0.7,flowers="pink"):
    rnd=random.Random(seed); n=40
    for i in range(n):
        zf=1-2*(i+0.5)/n; az=i*2.39996
        d=Vector((math.sqrt(max(0,1-zf*zf))*math.cos(az),math.sqrt(max(0,1-zf*zf))*math.sin(az),zf))
        if d.z<-0.5: continue
        c=Vector((0,0,r*0.8))+Vector((d.x*r,d.y*r,d.z*r*0.8))*rnd.uniform(0.55,0.95)
        up=(d+Vector((0,0,0.6))).normalized(); right=up.cross(Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-1,1))).normalized()).normalized()
        cell="ivy" if (rnd.random()<0.65 or flowers is None) else flowers
        sz=rnd.uniform(0.5,0.75)*r*1.3
        card(k,c,right,up,sz,sz,cell,flip=rnd.random()<0.5,bend=0.06)
def prop_flowerbox(k,flowers="pink"):
    rnd=random.Random(4)
    k.box((0,0,0.12),(1.25,0.32,0.24),WOOD,bevel=0.03)
    for sx in(-0.45,0.45): k.box((sx,0.08,-0.1),(0.08,0.2,0.25),WOOD,bevel=0.02)
    k.box((0,0,0.235),(1.15,0.24,0.02),SOIL,bevel=0)
    for i in range(7):
        x=-0.5+i*(1.0/6)+rnd.uniform(-0.04,0.04)
        for a in (0.3,-0.9):
            aa=a+rnd.uniform(-0.3,0.3); R=Vector((math.cos(aa),math.sin(aa),0))
            h=rnd.uniform(0.34,0.46)
            card(k,(x,rnd.uniform(-0.05,0.05),0.22+h/2),R,(rnd.uniform(-0.15,0.15),-0.25,1),h*1.05,h,flowers if rnd.random()<0.8 else "ivy",flip=rnd.random()<0.5)
    # trailing ivy over the front edge
    for i in range(4):
        x=-0.45+i*0.3; card(k,(x,-0.2,0.1),(1,0,0),(0,-0.4,1),0.32,0.36,"ivy",flip=i%2==0)
def prop_planter(k,flowers="pink"):
    _cyl(k,(0,0,0.25),0.26,0.33,0.5,14,CLAY); _cyl(k,(0,0,0.51),0.35,0.35,0.06,14,CLAY)
    _cyl(k,(0,0,0.5),0.29,0.29,0.02,12,SOIL)
    rnd=random.Random(9)
    for i in range(6):
        aa=i*math.pi/3+rnd.uniform(-0.2,0.2); R=Vector((math.cos(aa),math.sin(aa),0))
        h=rnd.uniform(0.45,0.6); card(k,(0,0,0.48+h/2),R,(0,0,1),h,h,flowers if i%3 else "ivy",flip=i%2==0)
EXTRA_SPECS+=[("SM_VK_Deco_Ivy_A",lambda k: ivy_patch(k,1),dict(wobble=False,grime=True)),
              ("SM_VK_Deco_Ivy_B",lambda k: ivy_patch(k,2,x0=-1.45,x1=0.2,top=3.6,n=55,base_w=1.2),dict(wobble=False,grime=True)),
              ("SM_VK_Deco_Weeds",lambda k: deco_weeds(k,3),dict(wobble=False,grime=True)),
              ("SM_VK_Deco_Bush",lambda k: deco_bush(k,4),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_FlowerBox_Daisy",lambda k: prop_flowerbox(k,"daisy"),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_Planter",lambda k: prop_planter(k,"pink"),dict(wobble=False,grime=False))]
'''
t.clear(); t.write(s+code); exec(t.as_string())
full_rebuild(["SM_VK_Deco_Ivy_A","SM_VK_Deco_Ivy_B","SM_VK_Deco_Weeds","SM_VK_Deco_Bush","SM_VK_Prop_FlowerBox","SM_VK_Prop_FlowerBox_Daisy","SM_VK_Prop_Planter"])
for n in ["SM_VK_Deco_Ivy_A","SM_VK_Deco_Weeds","SM_VK_Deco_Bush","SM_VK_Prop_FlowerBox"]: print(n,len(bpy.data.objects[n].data.polygons))
for o in bpy.data.objects:
    if o.name.startswith(("SM_VK_Deco","SM_VK_Prop_FlowerBox","SM_VK_Prop_Planter")) and "_inst" not in o.name:
        for p in o.data.polygons:
            if p.material_index==FOLIAGE: p.use_smooth=True
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Deco_Ivy_A 352\nSM_VK_Deco_Weeds 80\nSM_VK_Deco_Bush 120\nSM_VK_Prop_FlowerBox 156\n"}

# ==============================================================================================================
# [0176] 2026-09-23 03:42:38  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP)","p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP,FOLIAGE)")
t.clear(); t.write(s); exec(s)
T=vcol("VK_Test"); org=(80,-172,0)
place_v(T,"SM_VK_Deco_Ivy_B",-4.5,-3,0,0,org,{})
place_v(T,"SM_VK_Deco_Weeds",4.5,-3,0,0,org,{})
place_v(T,"SM_VK_Deco_Weeds",-4.5,-3,0,0,org,{})
place_v(T,"SM_VK_Deco_Ivy_A",4.5,-1.5,0,90,org,{})
place_v(T,"SM_VK_Prop_Planter",-1.1,-3.7,0,0,org,{}); place_v(T,"SM_VK_Prop_Planter",1.1,-3.7,0,0,org,{})
place_v(T,"SM_VK_Deco_Bush",6.2,-4.2,0,0,org,{})
place_v(T,"SM_VK_Prop_FlowerBox",-3.0,-3.55,0.9,0,org,{}); place_v(T,"SM_VK_Prop_FlowerBox_Daisy",3.0,-3.55,0.9,0,org,{})
for o in T.objects: o.hide_render=False
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((80,-172,2.2)); cs.location=tgt+Vector((6,-11,2.2))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_fol1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0177] 2026-09-23 03:43:00  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("TRT=0.5\n","TRT=0.38\n"); t.clear(); t.write(s); exec(s)
full_rebuild(["SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Gable","SM_VK_RoofThatch_Gable_Planks"])
bpy.ops.wm.save_mainfile(); print("ok")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nok\n"}

# ==============================================================================================================
# [0178] 2026-09-23 03:44:20  blender  ok
# ==============================================================================================================
import bpy
code = r'''
# =====================  FOUNTAIN / GRAVEYARD / LOW WALLS  =====================
def lathe(k,prof,center=(0,0,0),segs=16,mi=ROCK,smooth_=False,cap_top=False):
    cx,cy,cz=center; rings=[]
    for (r,z) in prof:
        rings.append([k.bm.verts.new((cx+math.cos(2*math.pi*i/segs)*r,cy+math.sin(2*math.pi*i/segs)*r,cz+z)) for i in range(segs)])
    fs=[]
    for a,b in zip(rings[:-1],rings[1:]):
        for i in range(segs):
            j=(i+1)%segs; fs.append(k.bm.faces.new((a[i],a[j],b[j],b[i])))
    if cap_top:
        fs.append(k.bm.faces.new(rings[-1]))
    k.bm.normal_update()
    for f in fs:
        f.material_index=mi; f.smooth=smooth_
    k.project(fs,mi)
    return fs
def prop_fountain(k):
    R=2.0; n=8
    for i in range(n):
        a=2*math.pi*(i+0.5)/n; L=2*R*math.tan(math.pi/n)+0.06
        k.box((math.cos(a)*R,math.sin(a)*R,0.42),(0.34,L,0.72),ASHLAR,rot=(0,0,a),bevel=0.04,segs=2)
        k.box((math.cos(a)*(R+0.02),math.sin(a)*(R+0.02),0.84),(0.5,L+0.1,0.14),ROCK,rot=(0,0,a),bevel=0.05,segs=2)
        a2=2*math.pi*i/n
        k.box((math.cos(a2)*(R+0.05),math.sin(a2)*(R+0.05),0.5),(0.44,0.44,0.95),ROCK,rot=(0,0,a2),bevel=0.06,segs=2)
        k.box((math.cos(a2)*(R+0.05),math.sin(a2)*(R+0.05),1.0),(0.5,0.5,0.1),ROCK,rot=(0,0,a2),bevel=0.04)
    # step ring
    for i in range(n):
        a=2*math.pi*(i+0.5)/n; L=2*(R+0.45)*math.tan(math.pi/n)+0.06
        k.box((math.cos(a)*(R+0.45),math.sin(a)*(R+0.45),0.08),(0.55,L,0.16),ROCK,rot=(0,0,a),bevel=0.04)
    # basin floor + water
    oct_=[(math.cos(2*math.pi*(i+0.5)/n)*(R-0.1)/math.cos(math.pi/n),math.sin(2*math.pi*(i+0.5)/n)*(R-0.1)/math.cos(math.pi/n)) for i in range(n)]
    f=k.bm.faces.new([k.bm.verts.new((x,y,0.62)) for x,y in oct_]); f.material_index=WATER
    for l in f.loops: l[k.uv].uv=(l.vert.co.x/1.5,l.vert.co.y/1.5)
    f=k.bm.faces.new([k.bm.verts.new((x,y,0.12)) for x,y in oct_]); f.material_index=ASHLAR
    k.bm.normal_update()
    # central pedestal
    lathe(k,[(0.5,0.0),(0.5,0.3),(0.34,0.45),(0.28,0.9),(0.3,1.2),(0.42,1.3)],segs=12,mi=ROCK)
    lathe(k,[(0.42,1.3),(0.95,1.42),(1.05,1.6),(0.98,1.66),(0.85,1.52),(0.2,1.5)],segs=16,mi=ASHLAR)
    lathe(k,[(0.86,1.55),(0.0,1.55)],segs=16,mi=WATER)
    lathe(k,[(0.2,1.5),(0.18,2.2),(0.3,2.3),(0.42,2.42),(0.44,2.5),(0.38,2.5),(0.1,2.45)],segs=12,mi=ROCK)
    lathe(k,[(0.36,2.47),(0.0,2.47)],segs=12,mi=WATER)
    _ico(k,(0,0,2.72),0.16,BRONZE,sub=2)
    k.box((0,0,2.58),(0.08,0.08,0.2),BRONZE,bevel=0.02)
    # falling water from upper bowl (4 streams) + ripple rings
    for i in range(4):
        a=math.pi/4+i*math.pi/2
        pts=[]
        for j in range(9):
            t=j/8; r=1.0+t*0.55; z=1.62-t*t*1.02
            pts.append(Vector((math.cos(a)*r,math.sin(a)*r,z)))
        for pa,pb in zip(pts[:-1],pts[1:]):
            d=pb-pa; q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
            sub=Kit(); _cyl(sub,(0,0,0),0.055,0.05,d.length+0.02,8,WATER)
            merge_kit(k,sub,Matrix.Translation((pa+pb)/2)@q)
        ring(k,(math.cos(a)*1.55,math.sin(a)*1.55,0.64),0.1,0.2,0.02,WATER,n=12,axis="Z")
def grave_mound(k,rnd):
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=2,radius=1.0)["verts"]
    for v in vs:
        v.co=Vector((v.co.x*0.45,v.co.y*0.95,max(v.co.z,-0.05)*0.18))+Vector((0,-0.95,0))
    fs=list({f for v in vs for f in v.link_faces})
    for f in fs: f.material_index=SOIL; f.smooth=True
    k.project(fs,SOIL)
    for i in range(5):
        x=rnd.uniform(-0.3,0.3); y=-0.95+rnd.uniform(-0.7,0.7)
        aa=rnd.uniform(0,3.14); card(k,(x,y,0.14),(math.cos(aa),math.sin(aa),0),(0,0,1),0.35,0.28,"grass" if i%2 else "daisy",flip=i%2==0)
def grave_a(k):
    rnd=random.Random(1)
    w,h,t=0.62,0.75,0.14
    outline=[(-w/2,0),(w/2,0)]+[(math.cos(math.pi*j/10)*w/2,h+math.sin(math.pi*j/10)*w/2) for j in range(11)]
    outline=[(w/2,0),(w/2,h)]+[(math.cos(math.pi*j/10)*w/2,h+math.sin(math.pi*j/10)*w/2) for j in range(1,10)]+[(-w/2,h),(-w/2,0)]
    front=[k.bm.verts.new((x,-t/2,z)) for x,z in outline]; back=[k.bm.verts.new((x,t/2,z)) for x,z in outline]
    fs=[k.bm.faces.new(list(reversed(front))),k.bm.faces.new(back)]
    n=len(outline)
    for i in range(n):
        j=(i+1)%n; fs.append(k.bm.faces.new((front[i],front[j],back[j],back[i])))
    k.bm.normal_update()
    if fs[0].normal.y>0:
        for f in fs: f.normal_flip()
    k.project(fs,ROCK)
    geom=list(set(front+back)|{e for v in front+back for e in v.link_edges})
    bmesh.ops.bevel(k.bm,geom=[e for e in geom if isinstance(e,bmesh.types.BMEdge)],offset=0.025,segments=2,affect="EDGES",clamp_overlap=True)
    for v in front+back:
        if v.is_valid: v.co=Matrix.Rotation(0.07,3,"Y")@Matrix.Rotation(-0.05,3,"X")@v.co
    k.box((0,-0.09,0.72),(0.3,0.02,0.035),VOID,bevel=0); k.box((0,-0.09,0.66),(0.034,0.02,0.2),VOID,bevel=0)
    rock(k,(0,0,0.05),(0.8,0.3,0.14),seed=3,tilt=0.02,segs=1)
    grave_mound(k,rnd)
def grave_cross(k):
    rnd=random.Random(2)
    k.box((0,0,0.62),(0.16,0.14,1.22),ROCK,bevel=0.03,segs=2)
    k.box((0,0,0.95),(0.62,0.14,0.16),ROCK,bevel=0.03,segs=2)
    ring(k,(0,0,0.95),0.19,0.26,0.1,ROCK,n=18,axis="Y")
    rock(k,(0,0,0.08),(0.5,0.4,0.2),seed=5,tilt=0.02,segs=1)
    grave_mound(k,rnd)
def grave_obelisk(k):
    rnd=random.Random(3)
    rock(k,(0,0,0.12),(0.7,0.7,0.26),seed=6,tilt=0.01,segs=1)
    k.box((0,0,0.35),(0.5,0.5,0.22),ASHLAR,bevel=0.03,segs=2)
    lathe(k,[(0.2,0.45),(0.16,1.5)],segs=4,mi=ASHLAR)
    lathe(k,[(0.16,1.5),(0.0,1.75)],segs=4,mi=ASHLAR)
    grave_mound(k,rnd)
def low_wall(k,L=CELL,seed=11):
    rnd=random.Random(seed); h=0.85
    k.box((0,0,h/2),(L,0.5,h),STONE,bevel=0)
    wall_rocks(k,-L/2,L/2,0.1,h,face=-0.25,n=5,seed=seed)
    sub=Kit(); wall_rocks(sub,-L/2,L/2,0.1,h,face=-0.25,n=5,seed=seed+1); merge_kit(k,sub,Matrix.Rotation(math.pi,4,"Z"))
    x=-L/2+0.02
    while x<L/2-0.05:
        w=min(rnd.uniform(0.14,0.22),L/2-x)
        hh=rnd.uniform(0.22,0.34)
        k.box((x+w/2,0,h+hh/2-0.03),(w-0.02,0.5,hh),ROCK,rot=(0,rnd.uniform(-0.12,0.12),0),bevel=0.03,segs=1,jitter=0.015,seed=int(x*100)+seed)
        x+=w
    for sgn in(-1,1):
        xx=-L/2+0.2
        while xx<L/2-0.2:
            ww=rnd.uniform(0.4,0.7)
            rock(k,(min(xx+ww/2,L/2-ww/2),sgn*0.2,0.14),(ww-0.05,0.3,0.3),seed=int(xx*50)+sgn*7,tilt=0.03,segs=1)
            xx+=ww
def low_wall_post(k):
    rock(k,(0,0,0.25),(0.8,0.8,0.5),seed=21,tilt=0.02)
    rock(k,(0,0,0.72),(0.7,0.7,0.46),seed=22,tilt=0.02)
    rock(k,(0,0,1.1),(0.62,0.62,0.34),seed=23,tilt=0.02)
    lathe(k,[(0.4,1.26),(0.42,1.34),(0.0,1.46)],segs=4,mi=ROCK)
def lychgate(k):
    """roofed gate for a low wall / graveyard, spans one 3 m cell"""
    for sx in(-1,1):
        rock(k,(sx*1.35,0,0.2),(0.55,0.55,0.4),seed=30+sx,tilt=0.01)
        for sy in(-1,1): k.box((sx*1.35,sy*0.55,1.45),(0.18,0.18,2.1),WOOD,bevel=0.04,segs=2)
        k.box((sx*1.35,0,2.45),(0.2,1.5,0.2),WOOD,bevel=0.04)
        k.box((sx*1.35,0,0.55),(0.12,1.1,0.12),WOOD,bevel=0.03)
        for sy in(-1,1): k.box((sx*1.35,sy*0.35,2.2),(0.1,0.5,0.1),WOOD,rot=(sy*0.8,0,0),bevel=0.02)
    for sy in(-1,1): k.box((0,sy*0.55,2.45),(3.0,0.18,0.2),WOOD,bevel=0.04)
    # roof along x, slopes to +-y
    run=1.25; rise=1.0; L=math.hypot(run,rise); ang=math.atan2(rise,run)
    for sy in(-1,1):
        k.box((0,sy*run/2,2.55+rise/2),(3.6,L+0.1,0.12),ROOF,rot=(-sy*ang,0,0),bevel=0.03)
        k.box((0,sy*(run+0.02),2.52),(3.62,0.1,0.18),WOOD,bevel=0.03)
    for sx in(-1,1):
        v=[k.bm.verts.new(p) for p in ((sx*1.45,-run,2.55),(sx*1.45,run,2.55),(sx*1.45,0,2.55+rise))]
        f=k.bm.faces.new(v if sx>0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    _cyl(k,(0,0,2.55+rise+0.06),0.13,0.13,3.6,8,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    # gates (slightly open)
    for sx in(-1,1):
        sub=Kit()
        for i in range(5): sub.box((0.13+i*0.26,0,0.62),(0.1,0.05,0.95+0.06*math.sin(i/4*math.pi)),PLANKS,bevel=0.01)
        for z in(0.35,0.95): sub.box((0.65,-0.04,z),(1.3,0.06,0.1),WOOD,bevel=0.02)
        sub.box((0.65,-0.04,0.65),(1.35,0.05,0.08),WOOD,rot=(0,-0.45,0),bevel=0.01)
        M=Matrix.Translation((sx*1.25,0,0))@Matrix.Rotation(sx*0.35+(math.pi if sx>0 else 0),4,"Z")
        merge_kit(k,sub,M)
    k.box((0,0,0.04),(2.4,1.2,0.08),ROCK,bevel=0.03)
EXTRA_SPECS+=[("SM_VK_Prop_Fountain",lambda k: prop_fountain(k),dict(wobble=False,grime=True)),
              ("SM_VK_Grave_A",lambda k: grave_a(k),dict(wobble=False,grime=True)),
              ("SM_VK_Grave_Cross",lambda k: grave_cross(k),dict(wobble=False,grime=True)),
              ("SM_VK_Grave_Obelisk",lambda k: grave_obelisk(k),dict(wobble=False,grime=True)),
              ("SM_VK_LowWall",lambda k: low_wall(k),dict(wobble=False,grime=True)),
              ("SM_VK_LowWall_Post",lambda k: low_wall_post(k),dict(wobble=False,grime=True)),
              ("SM_VK_LowWall_Lychgate",lambda k: lychgate(k),dict(wobble=False,grime=True))]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
new=["SM_VK_Prop_Fountain","SM_VK_Grave_A","SM_VK_Grave_Cross","SM_VK_Grave_Obelisk","SM_VK_LowWall","SM_VK_LowWall_Post","SM_VK_LowWall_Lychgate"]
full_rebuild(new)
for n in new: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Prop_Fountain 2572\nSM_VK_Grave_A 297\nSM_VK_Grave_Cross 306\nSM_VK_Grave_Obelisk 188\nSM_VK_LowWall 994\
# nSM_VK_LowWall_Post 170\nSM_VK_LowWall_Lychgate 1142\n"}

# ==============================================================================================================
# [0179] 2026-09-23 03:44:47  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
S=vcol("VK_Showcase")
for o in [o for o in S.objects if o.get("bld") in ("graveyard","fountain")]: bpy.data.objects.remove(o)
before=set(o.name for o in S.objects)
O=(0,0,0)
# graveyard south of the chapel
x0,x1,yS,yN=-7.5,7.5,-187.0,-176.0
for i in range(5):
    x=x0+1.5+3*i
    if i==2: place_v(S,"SM_VK_LowWall_Lychgate",x,yS,0,0,O,{})
    else: place_v(S,"SM_VK_LowWall",x,yS,0,0,O,{})
for j in range(int((yN-yS)/3)+1):
    y=yS+1.5+3*j
    if y>yN: break
    place_v(S,"SM_VK_LowWall",x0,y,0,90,O,{}); place_v(S,"SM_VK_LowWall",x1,y,0,90,O,{})
for (x,y) in ((x0,yS),(x1,yS),(x0,yS+12),(x1,yS+12),(x0+6,yS),(x1-6,yS)):
    place_v(S,"SM_VK_LowWall_Post",x,y,0,0,O,{})
rnd=random.Random(5)
kinds=["SM_VK_Grave_A","SM_VK_Grave_Cross","SM_VK_Grave_A","SM_VK_Grave_Obelisk"]
for row,y in enumerate((-178.6,-181.8)):
    for c in range(6):
        x=-5.6+c*2.25+rnd.uniform(-0.25,0.25)
        if row==1 and c in (2,3): continue
        o=place_v(S,kinds[(row*3+c)%4],x,y,0,180+rnd.uniform(-6,6),O,{})
place_v(S,"SM_VK_Deco_Bush",-6.2,-185.6,0,0,O,{}); place_v(S,"SM_VK_Deco_Bush",6.0,-177.0,0,40,O,{})
place_v(S,"SM_VK_Prop_LampPost",-2.0,-188.0,0,0,O,{})
for o in S.objects:
    if o.name not in before: o["bld"]="graveyard"
before=set(o.name for o in S.objects)
place_v(S,"SM_VK_Prop_Fountain",52,-182.5,0,0,O,{})
for o in S.objects:
    if o.name not in before: o["bld"]="fountain"
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=28
tgt=Vector((1,-178,2.5)); cs.location=tgt+Vector((10,-20,9))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_gy1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
tgt=Vector((52,-181,1.5)); cs.location=tgt+Vector((5,-9,4.5)); cs.data.lens=30
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_ft1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0180] 2026-09-23 03:45:31  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def gen_crops(S=1024,seed=151):
    rng=np.random.default_rng(seed); H=S//2
    img=np.zeros((S,S,3),f32); alpha=np.zeros((S,S),f32)
    def blades(ox,oy,n,cols,L=(180,330),w=(6,10),spread=0.3,ears=None,tipcol=None):
        nonlocal img,alpha
        for _ in range(n):
            x=ox+rng.uniform(70,H-70); y=oy+H-8; a=-math.pi/2+rng.uniform(-spread,spread); Ll=rng.uniform(*L); ww=rng.uniform(*w)
            pts=[]
            for i in range(10):
                t=i/9; pts.append((x+math.cos(a)*Ll*t,y+math.sin(a)*Ll*t)); a+=rng.uniform(-0.05,0.05)
            sg=[(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],ww*(1-i/11)+1) for i in range(9)]
            cov=draw_segments(S,sg,wrap=False)
            c=cols[rng.integers(0,len(cols))]*rng.uniform(0.85,1.15)
            img=img*(1-cov[...,None])+c*cov[...,None]; alpha=np.maximum(alpha,cov)
            if ears is not None:
                ex,ey=pts[-1]; ang=math.atan2(pts[-1][1]-pts[-3][1],pts[-1][0]-pts[-3][0])
                for j in range(7):
                    px=ex-math.cos(ang)*j*9; py=ey-math.sin(ang)*j*9
                    for sgn in(-1,1):
                        qx=px+math.cos(ang+sgn*0.6)*9; qy=py+math.sin(ang+sgn*0.6)*9
                        cv=draw_segments(S,[(px,py,qx,qy,8.0)],wrap=False)
                        ec=ears*rng.uniform(0.85,1.15)*(0.85+0.03*j)
                        img=img*(1-cv[...,None])+ec*cv[...,None]; alpha=np.maximum(alpha,cv)
    gold=[np.array(c,f32) for c in [(0.80,0.62,0.26),(0.72,0.55,0.22),(0.86,0.70,0.32)]]
    blades(0,0,45,gold,ears=np.array([0.90,0.72,0.30],f32))
    greens=[np.array(c,f32) for c in [(0.20,0.45,0.10),(0.28,0.52,0.14),(0.16,0.38,0.08)]]
    # leafy tops (carrot / beet): short wide feathery blades
    blades(H,0,60,greens,L=(90,200),w=(10,16),spread=0.8)
    dry=[np.array(c,f32) for c in [(0.70,0.62,0.36),(0.62,0.55,0.30),(0.78,0.70,0.42)]]
    blades(0,H,60,dry,L=(150,300),w=(4,7),spread=0.45)
    # lavender: grey-green stems with purple spikes
    blades(H,H,40,[np.array((0.42,0.5,0.36),f32)],L=(200,320),w=(4,6),spread=0.35,ears=np.array([0.52,0.36,0.78],f32))
    rgb=img.copy(); m=alpha>0.5
    for _ in range(12):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    rgba=np.concatenate([np.clip(rgb,0,1),alpha[...,None]],-1).astype(f32)
    name="T_VK_Crops_BCA"; im=bpy.data.images.get(name)
    if im is None: im=bpy.data.images.new(name,S,S,alpha=True)
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel()); im.update()
    im.filepath_raw=os.path.join(TEXDIR,name+".png"); im.file_format="PNG"; im.save(); im.pack()
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
gen_crops()
# crops material: copy of foliage material with the crops atlas
fm=bpy.data.materials["M_VK_Foliage"]; cm=bpy.data.materials.get("M_VK_Crops")
if cm: bpy.data.materials.remove(cm)
cm=fm.copy(); cm.name="M_VK_Crops"
for n in cm.node_tree.nodes:
    if n.type=="TEX_IMAGE": n.image=bpy.data.images["T_VK_Crops_BCA"]
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0181] 2026-09-23 03:46:59  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''tex_mat("M_VK_Clock","T_VK_Clock"), bpy.data.materials["M_VK_Foliage"]]''','''tex_mat("M_VK_Clock","T_VK_Clock"), bpy.data.materials["M_VK_Foliage"], bpy.data.materials["M_VK_Crops"]]''')
s=s.replace("THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE=range(32)","THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE,CROPS=range(33)")
s=s.replace('''FOL_CELLS={"ivy":(0,0),"pink":(1,0),"daisy":(0,1),"grass":(1,1)}
def fol_uv(cell):
    cx,cy=FOL_CELLS[cell]; m=0.01''','''FOL_CELLS={"ivy":(0,0),"pink":(1,0),"daisy":(0,1),"grass":(1,1),"wheat":(0,0),"leafy":(1,0),"drygrass":(0,1),"lavender":(1,1)}
CROP_SET={"wheat","leafy","drygrass","lavender"}
def fol_uv(cell):
    cx,cy=FOL_CELLS[cell]; m=0.01''')
s=s.replace('''            f=k.bm.faces.new([vs[x] for x in q]); f.material_index=FOLIAGE; f.smooth=True''','''            f=k.bm.faces.new([vs[x] for x in q]); f.material_index=CROPS if cell in CROP_SET else FOLIAGE; f.smooth=True''')
s=s.replace("p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP,FOLIAGE)","p.use_smooth=p.material_index in (HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP,FOLIAGE,CROPS)")
code = r'''
# =====================  FARM SET  =====================
def soil_bed(k,W=2.9,D=2.9,rows=7,ridge_h=0.12):
    k.box((0,0,0.03),(W,D,0.06),SOIL,bevel=0)
    for i in range(rows):
        y=-D/2+(i+0.5)*D/rows
        k.box((0,y,0.08),(W-0.1,D/rows*0.62,ridge_h),SOIL,bevel=0.05,segs=1,jitter=0.01,seed=i)
def crop_rows(k,cell,rows=7,per=8,h=(0.8,1.05),w=0.55,seed=0,W=2.9,D=2.9,z0=0.12):
    rnd=random.Random(seed)
    for i in range(rows):
        y=-D/2+(i+0.5)*D/rows
        for j in range(per):
            x=-W/2+(j+0.5)*W/per+rnd.uniform(-0.08,0.08)
            hh=rnd.uniform(*h)
            for a in (0.0,1.2,2.3):
                aa=a+rnd.uniform(-0.3,0.3)
                card(k,(x,y+rnd.uniform(-0.05,0.05),z0+hh/2-0.02),(math.cos(aa),math.sin(aa),0),(rnd.uniform(-0.1,0.1),rnd.uniform(-0.1,0.1),1),w*rnd.uniform(0.85,1.15),hh,cell,flip=rnd.random()<0.5)
def crop_wheat(k): soil_bed(k); crop_rows(k,"wheat",rows=7,per=9,seed=1)
def crop_carrot(k): soil_bed(k); crop_rows(k,"leafy",rows=7,per=10,h=(0.35,0.5),w=0.42,seed=2)
def crop_lavender(k): soil_bed(k,rows=5); crop_rows(k,"lavender",rows=5,per=7,h=(0.6,0.8),w=0.6,seed=3)
def crop_cabbage(k):
    soil_bed(k); rnd=random.Random(4)
    for i in range(7):
        y=-1.45+(i+0.5)*2.9/7
        for j in range(7):
            x=-1.45+(j+0.5)*2.9/7+rnd.uniform(-0.05,0.05)
            vs=_ico(k,(x,y,0.3),0.19,LEAF,(1,1,0.85),sub=2,jit=0.03,seed=i*9+j)
            for f in {f for v in vs for f in v.link_faces}: f.smooth=True
            for a in range(4):
                aa=a*1.57+rnd.uniform(-0.3,0.3)
                card(k,(x+math.cos(aa)*0.16,y+math.sin(aa)*0.16,0.24),(math.cos(aa+1.57),math.sin(aa+1.57),0),(math.cos(aa)*0.8,math.sin(aa)*0.8,0.6),0.3,0.3,"ivy",flip=a%2==0)
def pumpkin(k,c,r,seed=0):
    rnd=random.Random(seed); n=16; rings=[]
    prof=[(0.0,-1.0),(0.45,-0.92),(0.8,-0.62),(1.0,-0.1),(0.95,0.35),(0.7,0.72),(0.3,0.9),(0.0,0.82)]
    cx,cy,cz=c
    for (pr,pz) in prof:
        row=[]
        for i in range(n):
            a=2*math.pi*i/n; rib=1-0.07*abs(math.cos(4*a))
            row.append(k.bm.verts.new((cx+math.cos(a)*pr*r*rib,cy+math.sin(a)*pr*r*rib,cz+pz*r*0.75)))
        rings.append(row)
    fs=[]
    for a_,b_ in zip(rings[:-1],rings[1:]):
        for i in range(n): j=(i+1)%n; fs.append(k.bm.faces.new((a_[i],a_[j],b_[j],b_[i])))
    k.bm.normal_update()
    for f in fs: f.material_index=PUMPKIN; f.smooth=True
    k.project(fs,PUMPKIN)
    _cyl(k,(cx,cy,cz+r*0.75),0.035,0.025,0.16,6,LEAF)
def crop_pumpkin(k):
    soil_bed(k,rows=4); rnd=random.Random(5)
    for i in range(9):
        x=rnd.uniform(-1.2,1.2); y=rnd.uniform(-1.2,1.2); r=rnd.uniform(0.2,0.34)
        pumpkin(k,(x,y,0.12+r*0.72),r,seed=i)
    for i in range(26):
        x=rnd.uniform(-1.35,1.35); y=rnd.uniform(-1.35,1.35); aa=rnd.uniform(0,6.28)
        card(k,(x,y,0.2),(math.cos(aa),math.sin(aa),0),(0,0.3,1),0.45,0.35,"ivy",flip=i%2==0)
def scarecrow(k):
    k.box((0,0,1.1),(0.1,0.1,2.2),WOOD,bevel=0.02)
    k.box((0,0,1.65),(1.5,0.09,0.09),WOOD,bevel=0.02)
    _ico(k,(0,0,2.05),0.2,BURLAP,(1,0.9,1.1),sub=2,jit=0.01,seed=1)
    for sx in(-1,1): k.box((sx*0.07,-0.19,2.08),(0.05,0.02,0.05),VOID,bevel=0)
    k.box((0,-0.19,1.98),(0.14,0.02,0.02),VOID,bevel=0)
    lathe(k,[(0.36,2.2),(0.38,2.24),(0.18,2.26),(0.15,2.45),(0.05,2.55),(0.0,2.56)],segs=12,mi=HAY)
    k.box((0,0,1.5),(0.55,0.3,0.6),CLOTH_A,bevel=0.08,segs=2,jitter=0.02,seed=2)
    for sx in(-1,1):
        k.box((sx*0.45,0,1.62),(0.45,0.22,0.22),CLOTH_A,bevel=0.06,jitter=0.02,seed=3+sx)
        lathe(k,[(0.1,0.0),(0.02,-0.22)],center=(sx*0.7,0,1.62),segs=6,mi=HAY)
    k.box((0,0,1.12),(0.5,0.28,0.25),CLOTH_B,bevel=0.05,jitter=0.02,seed=5)
    for sx in(-0.1,0.1): lathe(k,[(0.08,0.0),(0.03,-0.25)],center=(sx,0,1.0),segs=6,mi=HAY)
    _ico(k,(0.35,-0.05,2.36),0.07,VOID,(1.4,1,0.8),sub=1)   # crow
def chicken(k,c=(0,0,0),rot=0.0,col=PAPER,seed=0):
    sub=Kit()
    _ico(sub,(0,0,0.26),0.16,col,(1.25,0.9,0.95),sub=2,seed=seed)
    _ico(sub,(0.17,0,0.42),0.08,col,sub=2)
    k_=sub
    lathe(k_,[(0.03,0.0),(0.0,0.07)],center=(0.24,0,0.42),segs=6,mi=YELLOW)
    k_.box((0.17,0,0.51),(0.08,0.02,0.05),APPLE,bevel=0.01); k_.box((0.215,0,0.385),(0.02,0.02,0.04),APPLE,bevel=0)
    k_.box((-0.2,0,0.36),(0.12,0.1,0.18),col,rot=(0,-0.5,0),bevel=0.03)
    for sy in(-0.05,0.05): k_.box((0.0,sy,0.07),(0.02,0.02,0.14),YELLOW,bevel=0)
    for f in sub.bm.faces:
        if f.material_index in (PAPER,PUMPKIN): f.smooth=True
    merge_kit(k,sub,Matrix.Translation(c)@Matrix.Rotation(rot,4,"Z"))
def chickens(k):
    rnd=random.Random(7)
    for i in range(5):
        chicken(k,(rnd.uniform(-1.2,1.2),rnd.uniform(-1.2,1.2),0),rnd.uniform(0,6.28),PAPER if i%3 else PUMPKIN,seed=i)
def chicken_coop(k):
    W,D=1.6,1.2; z0=0.55; hw=1.0
    for sx in(-1,1):
        for sy in(-1,1): k.box((sx*(W/2-0.05),sy*(D/2-0.05),(z0+hw)/2+0.05),(0.1,0.1,z0+hw+0.1),WOOD,bevel=0.02)
    k.box((0,0,z0),(W,D,0.08),PLANKS,bevel=0.01)
    for sy in(-1,1): k.box((0,sy*(D/2-0.02),z0+hw/2),(W,0.05,hw),PLANKS,bevel=0.01)
    for sx in(-1,1): k.box((sx*(W/2-0.02),0,z0+hw/2),(0.05,D,hw),PLANKS,bevel=0.01)
    k.quad([(-0.2,-D/2-0.03,z0+0.05),(0.2,-D/2-0.03,z0+0.05),(0.2,-D/2-0.03,z0+0.5),(-0.2,-D/2-0.03,z0+0.5)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    # ramp
    L=math.hypot(1.0,z0); ang=math.atan2(z0,1.0)
    k.box((0,-D/2-0.5,z0/2),(0.4,L,0.04),PLANKS,rot=(-ang,0,0),bevel=0.01)
    for i in range(5): k.box((0,-D/2-0.1-i*0.18,z0-0.1-i*0.1),(0.4,0.03,0.03),WOOD,bevel=0)
    # nest box
    k.box((W/2+0.25,0,z0+0.35),(0.5,0.9,0.5),PLANKS,bevel=0.01)
    k.box((W/2+0.28,0,z0+0.68),(0.6,1.0,0.06),ROOF,rot=(0,0.35,0),bevel=0.01)
    # roof
    run=D/2+0.25; rise=0.55; L2=math.hypot(run,rise); a2=math.atan2(rise,run)
    for sy in(-1,1): k.box((0,sy*run/2,z0+hw+rise/2),(W+0.4,L2+0.05,0.07),ROOF,rot=(-sy*a2,0,0),bevel=0.02)
    for sx in(-1,1):
        v=[k.bm.verts.new(p) for p in ((sx*(W/2),-D/2,z0+hw),(sx*(W/2),D/2,z0+hw),(sx*(W/2),0,z0+hw+rise))]
        f=k.bm.faces.new(v if sx>0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    _cyl(k,(0,0,z0+hw+rise+0.04),0.06,0.06,W+0.4,6,WOOD,rot=Matrix.Rotation(math.pi/2,4,"Y"))
    k.box((0,0,0.05),(W+0.3,D+0.3,0.1),HAY,bevel=0.04,jitter=0.03,seed=9)
EXTRA_SPECS+=[("SM_VK_Crop_Wheat",lambda k: crop_wheat(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Carrot",lambda k: crop_carrot(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Lavender",lambda k: crop_lavender(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Cabbage",lambda k: crop_cabbage(k),dict(wobble=False,grime=True)),
              ("SM_VK_Crop_Pumpkin",lambda k: crop_pumpkin(k),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_Scarecrow",lambda k: scarecrow(k),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_Chickens",lambda k: chickens(k),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_ChickenCoop",lambda k: chicken_coop(k),dict(wobble=False,grime=True))]
'''
t.clear(); t.write(s+code); exec(t.as_string())
new=["SM_VK_Crop_Wheat","SM_VK_Crop_Carrot","SM_VK_Crop_Lavender","SM_VK_Crop_Cabbage","SM_VK_Crop_Pumpkin","SM_VK_Prop_Scarecrow","SM_VK_Prop_Chickens","SM_VK_Prop_ChickenCoop"]
full_rebuild(new)
for n in new: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Crop_Wheat 944\nSM_VK_Crop_Carrot 1028\nSM_VK_Crop_Lavender 556\nSM_VK_Crop_Cabbage 4892\nSM_VK_Crop_Pump
# kin 1294\nSM_VK_Prop_Scarecrow 386\nSM_VK_Prop_Chickens 1180\nSM_VK_Prop_ChickenCoop 431\n"}

# ==============================================================================================================
# [0182] 2026-09-23 03:47:20  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace("            vs=_ico(k,(x,y,0.3),0.19,LEAF,(1,1,0.85),sub=2,jit=0.03,seed=i*9+j)","            vs=_ico(k,(x,y,0.3),0.19,LEAF,(1,1,0.85),sub=1,jit=0.02,seed=i*9+j)")
t.clear(); t.write(s); exec(s)
full_rebuild(["SM_VK_Crop_Cabbage"]); print(len(bpy.data.objects["SM_VK_Crop_Cabbage"].data.polygons))
S=vcol("VK_Showcase")
for o in [o for o in S.objects if o.get("bld")=="farm"]: bpy.data.objects.remove(o)
before=set(o.name for o in S.objects); O=(0,0,0)
crops=["SM_VK_Crop_Wheat","SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Lavender"]
for i,c in enumerate(crops):
    gx=i%3; gy=i//3
    place_v(S,c,-3.0+gx*3.2,-201.0-gy*3.2,0,0,O,{})
fence_run(S,(-4.8,-199.2),(5.0,-199.2),O,gate_at=1)
fence_run(S,(-4.8,-208.2),(5.0,-208.2),O)
fence_run(S,(5.0,-208.2),(5.0,-199.2),O)
place_v(S,"SM_VK_Prop_Scarecrow",0.2,-202.6,0,20,O,{})
place_v(S,"SM_VK_Prop_ChickenCoop",-8.0,-203.5,0,20,O,{})
place_v(S,"SM_VK_Prop_Chickens",-8.3,-205.6,0,0,O,{})
for o in S.objects:
    if o.name not in before: o["bld"]="farm"
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((-3,-202,1.0)); cs.location=tgt+Vector((6,-14,7))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_farm1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 1952\n"}

# ==============================================================================================================
# [0183] 2026-09-23 03:48:16  blender  ok
# ==============================================================================================================
import bpy
m=bpy.data.materials["M_VK_Pumpkin"]
for n in m.node_tree.nodes:
    if n.type=="MIX" and n.data_type=="RGBA": n.inputs[6].default_value=(0.82,0.30,0.035,1)
code = r'''
# =====================  BAKERY / STABLE  =====================
def bread_oven(k):
    """domed bread oven with its own little roof; attaches to a wall (wall-local, outer side -Y)"""
    y0=-0.3; yc=y0-1.0
    k.box((0,yc,0.45),(1.9,1.7,0.9),STONE,bevel=0.03,segs=1)
    wall_rocks(k,-0.95,0.95,0.1,0.9,face=yc-0.85,n=3,seed=12)
    k.box((0,yc,0.93),(2.0,1.8,0.1),ROCK,bevel=0.03,segs=1)
    vs=bmesh.ops.create_icosphere(k.bm,subdivisions=3,radius=1.0)["verts"]
    for v in vs:
        v.co=Vector((v.co.x*0.82,v.co.y*0.72,max(v.co.z,0.0)*0.78))+Vector((0,yc,0.97))
    fs=list({f for v in vs for f in v.link_faces})
    for f in fs: f.material_index=CLAY; f.smooth=True
    k.project(fs,CLAY)
    # mouth: arched opening on the front
    hw=0.28; zs=1.02; ym=yc-0.73
    pts=[(-hw,zs),(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+0.18+math.sin(math.pi*j/8)*hw) for j in range(9)]
    pts=[(hw,zs)]+[(math.cos(math.pi*j/8)*hw,zs+0.18+math.sin(math.pi*j/8)*hw) for j in range(9)]+[(-hw,zs)]
    vv=[k.bm.verts.new((x,ym,z)) for x,z in pts]; f=k.bm.faces.new(vv); f.material_index=VOID
    k.bm.normal_update()
    if f.normal.y>0: f.normal_flip()
    arch_ring_small=[(math.cos(math.pi*(j+0.5)/7)*(hw+0.08),zs+0.18+math.sin(math.pi*(j+0.5)/7)*(hw+0.08)) for j in range(7)]
    for j,(x,z) in enumerate(arch_ring_small):
        a=math.pi*(j+0.5)/7
        k.box((x,ym-0.03,z),(0.12,0.16,0.16),ROCK,rot=(0,-(a-math.pi/2),0),bevel=0.02)
    k.box((0,ym-0.1,zs-0.03),(0.8,0.3,0.08),ROCK,bevel=0.02)
    _ico(k,(0,ym+0.1,zs+0.12),0.1,GLOW,(1.6,1,0.5),sub=1)
    # iron door leaning, peel, flue
    k.box((0.62,ym-0.12,0.72+0.5),(0.5,0.05,0.5),IRON,rot=(0.25,0,0.3),bevel=0.02)
    _cyl(k,(0,yc+0.45,1.55),0.12,0.1,0.8,10,CLAY)
    _cyl(k,(0,yc+0.45,1.97),0.15,0.15,0.08,10,CLAY)
    k.box((-0.9,ym-0.35,1.0),(0.05,0.05,2.0),WOOD,rot=(0.25,0,0),bevel=0)
    k.box((-0.9,ym-0.58,0.1),(0.3,0.03,0.24),WOOD,rot=(0.25,0,0),bevel=0.01)
    # shelter roof on posts
    for x in (-1.1,1.1):
        k.box((x,yc-0.9,1.25),(0.16,0.16,2.5),WOOD,bevel=0.03)
    k.box((0,yc-0.9,2.45),(2.5,0.18,0.18),WOOD,bevel=0.03)
    L=math.hypot(1.4,0.5); ang=math.atan2(0.5,1.4)
    k.box((0,yc-0.35,2.72),(2.7,L+0.2,0.1),ROOF,rot=(ang,0,0),bevel=0.03)
    for x in (-1.1,1.1): k.box((x,yc-0.5,2.3),(0.12,0.6,0.12),WOOD,rot=(-0.7,0,0),bevel=0.02)
    # firewood under the oven
    for i in range(6):
        _cyl(k,(-0.55+i*0.22,yc-0.55,0.1+0.18*(i%2)),0.09,0.09,0.7,6,BREAD if i%3==0 else WOOD,rot=Matrix.Rotation(math.pi/2,4,"X"))
def bread_rack(k):
    for sx in(-0.7,0.7):
        for sy in(-0.2,0.2): k.box((sx,sy,0.9),(0.07,0.07,1.8),WOOD,bevel=0.015)
    for z in (0.4,0.9,1.4):
        k.box((0,0,z),(1.5,0.5,0.05),PLANKS,bevel=0.01)
        for i in range(6):
            x=-0.6+i*0.24
            _ico(k,(x,0,z+0.08),0.1,BREAD,(1.2 if i%2 else 0.9,0.8,0.55),sub=2)
    k.box((0,0.23,1.85),(1.5,0.05,0.12),WOOD,bevel=0.01)
def bakery_sign(k):
    k.box((0,0.03,0),(0.16,0.1,0.6),IRON,bevel=0.02)
    k.box((0,-0.7,0.22),(0.07,1.4,0.07),IRON,bevel=0.015)
    for yy in(-0.45,-1.15): k.box((0,yy,0.02),(0.02,0.02,0.36),IRON,bevel=0)
    # pretzel: three bread rings
    for (dy,dz,r) in ((-0.62,-0.35,0.2),(-0.98,-0.35,0.2),(-0.8,-0.58,0.24)):
        ring(k,(0,dy,dz),r-0.07,r,0.09,BREAD,n=18,axis="Y")
    for f in k.bm.faces:
        if f.material_index==BREAD: f.smooth=True
def wall_stall(k):
    """stable front module (3 m, barn height): posts, half door (top half open), hay inside"""
    k.box((0,-0.02,0.35),(CELL,0.4,0.7),STONE,bevel=0)
    plinth(k)
    k.box((-1.5,-0.26,(0.7+HB)/2),(0.26,0.22,HB-0.7),WOOD,bevel=0.04)
    k.box((0,-0.24,HB-0.12),(CELL,0.22,0.24),WOOD,bevel=0.03)
    zt=2.6
    grid_cut(k,k.box((0,-0.02,(zt+HB-0.24)/2),(CELL,0.36,HB-0.24-zt),PLANKS,bevel=0))
    k.box((0,-0.26,zt+0.06),(CELL,0.22,0.2),WOOD,bevel=0.03)
    # opening back plane (interior darkness) + stall interior hints
    k.quad([(-1.35,1.2,0.7),(1.35,1.2,0.7),(1.35,1.2,zt),(-1.35,1.2,zt)],VOID,uvs=[(0,0),(1,0),(1,1),(0,1)])
    for x in (-1.37,1.37):
        v=[k.bm.verts.new(p) for p in ((x,-0.2,0.7),(x,1.2,0.7),(x,1.2,zt),(x,-0.2,zt))]
        f=k.bm.faces.new(v if x<0 else v[::-1]); f.material_index=PLANKS; k.bm.normal_update(); k.project([f],PLANKS)
    k.box((0,0.5,zt-0.02),(2.74,1.4,0.04),PLANKS,bevel=0)
    k.box((0,0.5,0.72),(2.74,1.4,0.04),HAY,bevel=0)
    # lower half-door + side boards
    k.box((0,-0.14,1.2),(1.5,0.08,1.1),PLANKS,bevel=0.01)
    for z in (0.85,1.55): k.box((0,-0.2,z),(1.45,0.05,0.12),WOOD,bevel=0.02)
    k.box((0,-0.2,1.2),(1.55,0.05,0.1),WOOD,rot=(0,0.62,0),bevel=0.015)
    for sgn in(-1,1):
        k.box((sgn*1.05,-0.1,1.2),(0.6,0.12,1.1),PLANKS,bevel=0.01)
        k.box((sgn*0.8,-0.24,(0.7+zt)/2),(0.18,0.2,zt-0.7),WOOD,bevel=0.03)
    # upper half-door swung open against the wall
    k.box((1.2,-0.46,2.0),(0.08,0.62,0.9),PLANKS,rot=(0,0,0.2),bevel=0.01)
    # hay rack + horseshoe
    k.box((0,0.9,2.0),(1.4,0.3,0.5),WOOD,bevel=0.02)
    k.box((0,0.9,2.1),(1.3,0.28,0.35),HAY,bevel=0.08,segs=2,jitter=0.03,seed=3)
    ring(k,(0,-0.26,2.4),0.07,0.1,0.03,IRON,n=12,axis="Y")
EXTRA_SPECS+=[("SM_VK_BreadOven",lambda k: bread_oven(k),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_BreadRack",lambda k: bread_rack(k),dict(wobble=False,grime=True)),
              ("SM_VK_Prop_BakerySign",lambda k: bakery_sign(k),dict(wobble=False,grime=False)),
              ("SM_VK_Wall_Stall",lambda k: wall_stall(k),dict(wobble=False,grime=True))]
def build_bakery(coll,origin,seed=61):
    st={"ground":"Stone","plaster":"Ochre","shutter":"Green","roof":"Red","seed":seed}
    build_house_v(coll,origin,2,2,st,front="DW",back="..",chimney=True)
    place_v(coll,"SM_VK_BreadOven",3.0,1.5,0,90,origin,st)
    place_v(coll,"SM_VK_Prop_BakerySign",-2.6,-3.3,2.9,0,origin,{})
    place_v(coll,"SM_VK_Prop_BreadRack",-1.3,-4.4,0,0,origin,{})
    place_v(coll,"SM_VK_Prop_Sacks",1.8,-4.2,0,20,origin,{})
    place_v(coll,"SM_VK_Prop_Woodpile",5.4,-1.5,0,90,origin,{})
    place_v(coll,"SM_VK_Prop_Planter",-3.7,-3.7,0,0,origin,{})
def build_stable(coll,origin,n=3,roof="Thatch"):
    L=n*CELL; st={"roof":roof}
    def P(nm,x,y,z,r,sty=st): place_v(coll,nm,x,y,z,r,origin,sty)
    for i in range(n):
        x=-L/2+1.5+3*i
        P("SM_VK_Wall_Stall",x,-3,0,0); P("SM_VK_Wall_Barn",x,3,0,180)
    for yy in(-1.5,1.5):
        P("SM_VK_Wall_Barn",-L/2,yy,0,-90); P("SM_VK_Wall_Barn",L/2,-yy,0,90)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): P("SM_VK_Corner_Barn",cx,cy,0,r)
    for i in range(n):
        x=-L/2+1.5+3*i
        if roof=="Thatch":
            P("SM_VK_RoofThatch_Gable_Planks" if i in (0,n-1) else "SM_VK_RoofThatch_Mid",x,0,HB,180 if i==0 else 0)
        else:
            P("SM_VK_Roof_Gable_Planks" if i in (0,n-1) else "SM_VK_Roof_Mid",x,0,HB,180 if i==0 else 0)
    P("SM_VK_Prop_Trough",-2.5,-4.6,0,0,{}); P("SM_VK_Prop_HayBale",3.9,-4.5,0,-15,{})
    P("SM_VK_Prop_Signpost",-L/2-1.5,-4.8,0,0,{})
    fence_run(coll,(-L/2,-8.5),(L/2,-8.5),origin,gate_at=1); fence_run(coll,(-L/2,-3.4),(-L/2,-8.5),origin); fence_run(coll,(L/2,-3.4),(L/2,-8.5),origin)
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
new=["SM_VK_BreadOven","SM_VK_Prop_BreadRack","SM_VK_Prop_BakerySign","SM_VK_Wall_Stall"]
full_rebuild(new)
for n in new: print(n,len(bpy.data.objects[n].data.polygons))
S=vcol("VK_Showcase")
for o in [o for o in S.objects if o.get("bld") in ("bakery","stable")]: bpy.data.objects.remove(o)
for tag,fn,org in (("bakery",build_bakery,(78,-172,0)),("stable",build_stable,(78,-196,0))):
    before=set(o.name for o in S.objects); fn(S,org)
    for o in S.objects:
        if o.name not in before: o["bld"]=tag
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((79,-172,3)); cs.location=tgt+Vector((12,-15,7))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_bk1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
tgt=Vector((78,-197,2.5)); cs.location=tgt+Vector((7,-16,6))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_st1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_BreadOven 965\nSM_VK_Prop_BreadRack 1648\nSM_VK_Prop_BakerySign 280\nSM_VK_Wall_Stall 791\n"}

# ==============================================================================================================
# [0184] 2026-09-23 03:48:36  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
for o in list(bpy.data.collections["VK_Test"].objects): bpy.data.objects.remove(o)
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((80.5,-172,2.4)); cs.location=tgt+Vector((11,-10,5))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_bk1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0185] 2026-09-23 03:49:38  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
s=s.replace('''    place_v(coll,"SM_VK_Prop_Woodpile",5.4,-1.5,0,90,origin,{})''','''    place_v(coll,"SM_VK_Prop_Woodpile",-4.9,1.2,0,90,origin,{})''')
code = r'''
# =====================  HIP ROOF END  =====================
XH=1.5          # wall line of the hipped end (local x)
def hip_z(x,y):
    return min(roof_z(abs(y)),roof_z(max(0.0,HALF+(x-XH))))
def roof_hip(k,mat=ROOF,tabs=True):
    XE=XH+(EAVE-HALF)                       # end eave x
    xs=sorted(set([round(-1.5+i*0.25,4) for i in range(int((XE+1.5)/0.25)+1)]+[XE]))
    ys=sorted(set([round(-EAVE+i*0.25,4) for i in range(int(2*EAVE/0.25)+1)]+[EAVE,-EAVE]))
    rt=RT if mat==ROOF else TRT
    top={};bot={}
    for x in xs:
        for y in ys:
            z=hip_z(x,y); top[(x,y)]=k.bm.verts.new((x,y,z)); bot[(x,y)]=k.bm.verts.new((x,y,z-rt*1.2))
    T=TILE[mat]; W=TILE[WOOD]
    def reg(cx,cy):
        a=roof_z(abs(cy)); b=roof_z(max(0.0,HALF+(cx-XH)))
        return "S" if a<=b else "E"
    for i in range(len(xs)-1):
        for j in range(len(ys)-1):
            x0,x1,y0,y1=xs[i],xs[i+1],ys[j],ys[j+1]
            q=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            # triangulate along the hip diagonals
            tris=[(0,1,2),(0,2,3)] if (y0>=0)==(True) else [(0,1,3),(1,2,3)]
            for tr in tris:
                pts=[q[t_] for t_ in tr]
                cx=sum(p[0] for p in pts)/3; cy=sum(p[1] for p in pts)/3
                r_=reg(cx,cy)
                f=k.bm.faces.new([top[p] for p in pts]); f.material_index=mat
                for l,p in zip(f.loops,pts):
                    if r_=="S": l[k.uv].uv=((p[0]-1.5)/T,slope_dist(abs(p[1]))/T)
                    else: l[k.uv].uv=(p[1]/T,slope_dist(HALF+(p[0]-XH))/T)
                fb=k.bm.faces.new([bot[p] for p in pts[::-1]]); fb.material_index=WOOD if mat==ROOF else mat
                for l in fb.loops: l[k.uv].uv=(l.vert.co.x/W,l.vert.co.y/W)
    def side(pa,pb):
        for (a_,b_) in zip(pa,pb):
            f=k.bm.faces.new((top[a_],top[b_],bot[b_],bot[a_])); f.material_index=WOOD if mat==ROOF else mat
            for l in f.loops: l[k.uv].uv=((l.vert.co.x+l.vert.co.y)/W,l.vert.co.z/W)
    side([(xs[i+1],ys[0]) for i in range(len(xs)-1)],[(xs[i],ys[0]) for i in range(len(xs)-1)])
    side([(xs[i],ys[-1]) for i in range(len(xs)-1)],[(xs[i+1],ys[-1]) for i in range(len(xs)-1)])
    side([(xs[-1],ys[j+1]) for j in range(len(ys)-1)],[(xs[-1],ys[j]) for j in range(len(ys)-1)])
    k.bm.normal_update()
    for f in k.bm.faces:
        pass
    # ridge (to the hip apex) + hip ridges along the diagonals
    xa=XH-HALF   # apex x (=-1.5)
    if mat==ROOF:
        ridge(k,-1.5,xa+0.001) if xa>-1.5 else None
        for s_ in(-1,1):
            n=7
            for i in range(n):
                t0=i/n; t1=(i+1)/n
                d0=HALF*t0; d1=HALF*t1          # distance from apex along the hip (in plan, on each axis)
                p0=Vector((xa+d0,s_*d0,roof_z(d0)+0.03)); p1=Vector((xa+d1,s_*d1,roof_z(d1)+0.03))
                d=p1-p0; q=Vector((1,0,0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
                sub=Kit(); _cyl(sub,(0,0,0),0.19,0.16,d.length+0.05,10,ROOF,rot=Matrix.Rotation(math.pi/2,4,"Y"))
                merge_kit(k,sub,Matrix.Translation((p0+p1)/2)@q)
        _ico(k,(xa,0,RIDGE+0.12),0.24,ROOF,sub=1)
        k.box((xa,0,RIDGE+0.5),(0.14,0.14,0.7),WOOD,bevel=0.04,segs=2)
        _ico(k,(xa,0,RIDGE+0.9),0.14,BRONZE,sub=1)
        if tabs:
            for s_ in(-1,1): eave_tabs(k,-1.5,XH+0.05,s_)
            sub=Kit()
            for s_ in(-1,1): eave_tabs(sub,-HALF+0.05,HALF-0.05,s_)
            # end eave: build a y-running strip by rotating an x-strip 90 degrees
            sub2=Kit(); eave_tabs(sub2,-HALF+0.02,HALF-0.02,1)
            merge_kit(k,sub2,Matrix.Translation((XH-HALF,0,0))@Matrix.Rotation(-math.pi/2,4,"Z"))
    else:
        thatch_eave_roll(k,-1.5,XH+0.25,-1,seed=1.0); thatch_eave_roll(k,-1.5,XH+0.25,1,seed=2.0)
        sub2=Kit(); thatch_eave_roll(sub2,-HALF-0.25,HALF+0.25,1,seed=3.0)
        merge_kit(k,sub2,Matrix.Translation((XH-HALF,0,0))@Matrix.Rotation(-math.pi/2,4,"Z"))
        thatch_ridge_cap(k,-1.5,xa+0.35)
        for s_ in(-1,1):
            _ico(k,(XH+(EAVE-HALF)-0.1,s_*(EAVE-0.1),roof_z(EAVE)-TRT/2),TRT/2+0.1,THATCH,sub=2,jit=0.02,seed=s_+5)
EXTRA_SPECS+=[("SM_VK_Roof_Hip",lambda k: roof_hip(k,ROOF),dict(wobble=False,grime=False)),
              ("SM_VK_RoofThatch_Hip",lambda k: roof_hip(k,THATCH),dict(wobble=False,grime=False))]
'''
t.clear(); t.write(s+code); exec(t.as_string())
full_rebuild(["SM_VK_Roof_Hip","SM_VK_RoofThatch_Hip"])
for n in ["SM_VK_Roof_Hip","SM_VK_RoofThatch_Hip"]: print(n,len(bpy.data.objects[n].data.polygons))
# test: two houses with hip ends
T=vcol("VK_Test")
for o in list(T.objects): bpy.data.objects.remove(o)
for (org,roofk,mid,hipn) in (((100,-172,0),"Red","SM_VK_Roof_Mid","SM_VK_Roof_Hip"),((100,-188,0),"Thatch","SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Hip")):
    st={"ground":"Plaster","plaster":"Cream","shutter":"Red","roof":roofk,"seed":7}
    L=9
    for i in range(3):
        x=-L/2+1.5+3*i
        place_v(T,["SM_VK_Wall_Plaster_Window","SM_VK_Wall_Plaster_Door","SM_VK_Wall_Plaster_Window"][i],x,-3,0,0,org,st); place_v(T,"SM_VK_Wall_Plaster",x,3,0,180,org,st)
    for yy in(-1.5,1.5):
        place_v(T,"SM_VK_Wall_Plaster_Window",-L/2,yy,0,-90,org,st); place_v(T,"SM_VK_Wall_Plaster",L/2,-yy,0,90,org,st)
    for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)): place_v(T,"SM_VK_Corner_Plaster",cx,cy,0,r,org,st)
    place_v(T,hipn,-3,0,H1,180,org,st); place_v(T,mid,0,0,H1,0,org,st); place_v(T,hipn,3,0,H1,0,org,st)
for o in T.objects: o.hide_render=False
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((100,-180,2.5)); cs.location=tgt+Vector((16,-19,12))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_hip1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Roof_Hip 3913\nSM_VK_RoofThatch_Hip 3509\n"}

# ==============================================================================================================
# [0186] 2026-09-23 03:50:08  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
old_roof='''    thatch=style.get("roof")=="Thatch"
    for i in range(n):
        x=-L/2+1.5+3*i
        if thatch: pc="SM_VK_RoofThatch_Gable" if i in (0,n-1) else "SM_VK_RoofThatch_Mid"
        else: pc="SM_VK_Roof_Gable" if i in (0,n-1) else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)'''
assert old_roof in s
s=s.replace(old_roof,'''    thatch=style.get("roof")=="Thatch"
    hip_p=0.55 if thatch else 0.3
    ends=[r.random()<hip_p for _ in range(2)]
    for i in range(n):
        x=-L/2+1.5+3*i
        is_end=i in (0,n-1); hip=is_end and ends[0 if i==0 else 1]
        if thatch: pc=("SM_VK_RoofThatch_Hip" if hip else "SM_VK_RoofThatch_Gable") if is_end else "SM_VK_RoofThatch_Mid"
        else: pc=("SM_VK_Roof_Hip" if hip else "SM_VK_Roof_Gable") if is_end else "SM_VK_Roof_Mid"
        place_v(coll,pc,x,0,top,180 if i==0 else 0,origin,style)''')
s=s.replace('''            if i==ci and chimney: continue
            if r.random()<(0.55 if stories==1 else 0.35):''','''            if i==ci and chimney: continue
            if (i==0 and ends[0]) or (i==n-1 and ends[1]): continue
            if r.random()<(0.55 if stories==1 else 0.35):''')
old_dress='''    if c=="W" and r.random()<0.7:
        px,py=loc(0,-0.55 if style.get("ground")=="Stone" else -0.5)
        place_v(coll,"SM_VK_Prop_FlowerBox",px,py,0.78 if style.get("ground")=="Stone" else 0.9,rot,origin,{})'''
assert old_dress in s
s=s.replace(old_dress,'''    if c=="W" and r.random()<0.7:
        px,py=loc(0,-0.55 if style.get("ground")=="Stone" else -0.5)
        fb="SM_VK_Prop_FlowerBox" if r.random()<0.6 else "SM_VK_Prop_FlowerBox_Daisy"
        place_v(coll,fb,px,py,0.78 if style.get("ground")=="Stone" else 0.9,rot,origin,{})
    if r.random()<0.4: place_v(coll,"SM_VK_Deco_Weeds",x,y,0,rot,origin,{})
    if c=="." and r.random()<0.22: place_v(coll,"SM_VK_Deco_Ivy_A" if r.random()<0.5 else "SM_VK_Deco_Ivy_B",x,y,0,rot,origin,{})
    if c=="D" and r.random()<0.5:
        for sx in ((-1.05,1.05) if r.random()<0.5 else (1.05,)):
            px,py=loc(sx,-0.75); place_v(coll,"SM_VK_Prop_Planter",px,py,0,rot,origin,{})''')
t.clear(); t.write(s); exec(s)
# rebuild the showcase bakery (woodpile moved)
S=vcol("VK_Showcase")
for o in [o for o in S.objects if o.get("bld")=="bakery"]: bpy.data.objects.remove(o)
before=set(o.name for o in S.objects); build_bakery(S,(78,-172,0))
for o in S.objects:
    if o.name not in before: o["bld"]="bakery"
for o in list(bpy.data.collections["VK_Test"].objects): bpy.data.objects.remove(o)
bpy.ops.wm.save_mainfile(); print("saved")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nsaved\n"}

# ==============================================================================================================
# [0187] 2026-09-23 03:51:08  blender  ok
# ==============================================================================================================
import bpy
code = r'''
# =====================  FACADE EXTRAS  =====================
def wall_timber_oriel(k):
    timber_frame(k,False,"V")
    # remove nothing: the bay sits proud of the wall, covering the centre panel
    D=0.62; W=1.7; z0=0.55; z1=2.35; yf=-0.45
    # corbel/brackets beneath
    k.box((0,yf-D/2,z0-0.08),(W+0.2,D+0.1,0.16),WOOD,bevel=0.04)
    for x in (-W/2+0.15,0,W/2-0.15):
        k.box((x,yf-0.3,z0-0.45),(0.14,0.62,0.14),WOOD,rot=(math.atan2(0.5,-0.55),0,0),bevel=0.03)
    # three-sided bay: front + two angled sides
    pts=[(-W/2,yf),(-W/2+0.3,yf-D),(W/2-0.3,yf-D),(W/2,yf)]
    for (xa,ya),(xb,yb) in zip(pts[:-1],pts[1:]):
        L=math.hypot(xb-xa,yb-ya); ang=math.atan2(yb-ya,xb-xa); cx,cy=(xa+xb)/2,(ya+yb)/2
        nx,ny=-(yb-ya)/L,(xb-xa)/L
        if ny>0: nx,ny=-nx,-ny
        # sill + head plates, posts, window pane
        k.box((cx,cy,z0+0.1),(L+0.08,0.16,0.2),WOOD,rot=(0,0,ang),bevel=0.03)
        k.box((cx,cy,z1-0.1),(L+0.08,0.16,0.2),WOOD,rot=(0,0,ang),bevel=0.03)
        k.box((cx+nx*0.03,cy+ny*0.03,z0+0.3),(L,0.1,0.2),PLASTER,rot=(0,0,ang),bevel=0)
        pv=[k.bm.verts.new((cx+math.cos(ang)*sgn*(L/2-0.07)+nx*0.02,cy+math.sin(ang)*sgn*(L/2-0.07)+ny*0.02,z)) for sgn,z in ((-1,z0+0.42),(1,z0+0.42),(1,z1-0.22),(-1,z1-0.22))]
        f=k.bm.faces.new(pv); f.material_index=WINDOW; k.bm.normal_update()
        if f.normal.x*nx+f.normal.y*ny<0: f.normal_flip()
        for l,uvv in zip(f.loops,((0,0),(L,0),(L,1.5),(0,1.5))): l[k.uv].uv=(uvv[0]*0.9,uvv[1]*0.9)
        k.box((cx+nx*0.04,cy+ny*0.04,(z0+z1)/2+0.1),(0.06,0.06,z1-z0-0.6),WOOD,rot=(0,0,ang),bevel=0.01)
        k.box((cx+nx*0.04,cy+ny*0.04,z0+1.25),(L-0.1,0.06,0.06),WOOD,rot=(0,0,ang),bevel=0.01)
    for (x,y) in pts: k.box((x,y,(z0+z1)/2),(0.14,0.14,z1-z0),WOOD,bevel=0.03)
    # little hipped cap roof
    cap=Kit()
    zc=z1
    vb=[(-W/2-0.12,yf+0.02),(-W/2+0.22,yf-D-0.14),(W/2-0.22,yf-D-0.14),(W/2+0.12,yf+0.02)]
    top_=[(-W/2+0.2,yf+0.02),(W/2-0.2,yf+0.02)]
    V=[k.bm.verts.new((x,y,zc)) for x,y in vb]; Tt=[k.bm.verts.new((x,y,zc+0.55)) for x,y in top_]
    for face in ((V[0],V[1],Tt[0]),(V[1],V[2],Tt[1],Tt[0]),(V[2],V[3],Tt[1])):
        f=k.bm.faces.new(face); f.material_index=ROOF
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index==ROOF and f.verts[0] in V+Tt:
            if f.normal.z<0: f.normal_flip()
            k.project([f],ROOF)
def wall_timber_door(k):
    timber_frame(k,True)
    # replace window with a door: plank leaf over the window area + lintel
    k.box((0,-0.3,1.3),(1.0,0.1,2.2),PLANKS,bevel=0.015)
    for z in (0.6,1.9): k.box((0,-0.36,z),(0.92,0.03,0.09),IRON,bevel=0.01)
    k.box((0.34,-0.38,1.2),(0.05,0.05,0.14),IRON,bevel=0.01)
    k.box((0,-0.4,2.47),(1.3,0.2,0.18),WOOD,bevel=0.03)
def ext_stair(k):
    """wooden exterior stair along a wall (wall-local, outer side -Y); climbs +X over one cell to an upper door at x=+3"""
    rise=H1+0.3; run=2.7; n=13; y=-0.95; w=0.9
    for i in range(n):
        z=(i+1)*rise/n; x=-1.35+(i+0.5)*run/n
        k.box((x,y,z-0.04),(run/n+0.03,w,0.07),PLANKS,bevel=0.01)
    L=math.hypot(run,rise); ang=math.atan2(rise,run)
    for sy in (y-w/2+0.04,y+w/2-0.04):
        k.box((0,sy,rise/2),(L,0.08,0.26),WOOD,rot=(0,-ang,0),bevel=0.02)
    # landing at the top (in front of the next cell's door)
    k.box((1.35+0.75,y,rise-0.04),(1.5,w+0.1,0.1),PLANKS,bevel=0.01)
    for (px,py) in ((1.4,y-w/2),(2.8,y-w/2),(1.4,y+w/2),(2.8,y+w/2)):
        k.box((px,py,(rise-0.1)/2),(0.14,0.14,rise-0.1),WOOD,bevel=0.03)
    for (px,py) in ((0.2,y-w/2),(-1.0,y-w/2)):
        k.box((px,py,(px+1.35)/run*rise/2),(0.12,0.12,(px+1.35)/run*rise),WOOD,bevel=0.02)
    # railing
    k.box((0,y-w/2,rise/2+0.9),(L,0.06,0.08),WOOD,rot=(0,-ang,0),bevel=0.015)
    for i in range(1,7):
        x=-1.35+i*run/7; z=(x+1.35)/run*rise
        k.box((x,y-w/2,z+0.45),(0.05,0.05,0.9),WOOD,bevel=0.01)
    k.box((2.1,y-w/2,rise+0.9),(1.5,0.07,0.08),WOOD,bevel=0.015)
    for x in (1.6,2.1,2.6): k.box((x,y-w/2,rise+0.45),(0.05,0.05,0.9),WOOD,bevel=0.01)
    rock(k,(-1.55,y,0.08),(0.5,w+0.1,0.16),seed=3,tilt=0.01,segs=1)
def awning(k):
    W_=2.4; D_=1.1; z0=2.35; z1=1.95
    nx_=12
    for i in range(nx_):
        x0=-W_/2+i*W_/nx_; x1=x0+W_/nx_
        mi=CLOTH_A if (i//2)%2==0 else CLOTH_B
        vs=[k.bm.verts.new(p) for p in ((x0,-0.3,z0),(x1,-0.3,z0),(x1,-0.3-D_,z1-0.04*math.sin(math.pi*(i+1)/nx_)),(x0,-0.3-D_,z1-0.04*math.sin(math.pi*i/nx_)))]
        f=k.bm.faces.new(vs); f.material_index=mi
        vb=[k.bm.verts.new(v.co+Vector((0,0,-0.012))) for v in vs]; f2=k.bm.faces.new(vb[::-1]); f2.material_index=mi
        a=vs[3].co; b=vs[2].co; m=(a+b)/2+Vector((0,0,-0.24))
        tri=[k.bm.verts.new(a),k.bm.verts.new(b),k.bm.verts.new(m)]
        f3=k.bm.faces.new(tri); f3.material_index=mi
        tb=[k.bm.verts.new(v.co+Vector((0,0.01,0))) for v in tri]; f4=k.bm.faces.new(tb[::-1]); f4.material_index=mi
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.material_index in (CLOTH_A,CLOTH_B):
            f.smooth=True
            for l in f.loops: l[k.uv].uv=(l.vert.co.x*2,l.vert.co.y*2)
    for sx in (-1,1):
        k.box((sx*W_/2,-0.3-D_/2,(z0+z1)/2+0.02),(0.04,D_,0.04),IRON,rot=(math.atan2(z0-z1,D_),0,0),bevel=0)
        k.box((sx*W_/2,-0.35,z0),(0.08,0.1,0.08),IRON,bevel=0.01)
    k.box((0,-0.3-D_,z1),(W_+0.05,0.04,0.04),IRON,bevel=0)
def laundry(k,L=5.0):
    for sx in(-1,1):
        k.box((sx*L/2,0,1.3),(0.12,0.12,2.6),WOOD,bevel=0.03)
        k.box((sx*L/2,0,2.55),(0.1,0.5,0.08),WOOD,bevel=0.02)
    rnd=random.Random(3)
    pts=[Vector((-L/2+L*i/16,0,2.5-0.35*math.sin(math.pi*i/16))) for i in range(17)]
    for pa,pb in zip(pts[:-1],pts[1:]):
        d=pb-pa; k.box(tuple((pa+pb)/2),(d.length,0.015,0.015),IRON,rot=(0,-math.atan2(d.z,d.x),0),bevel=0)
    x=-L/2+0.4; i=0
    while x<L/2-0.6:
        w=rnd.uniform(0.45,0.9); h=rnd.uniform(0.5,0.9)
        t=(x+w/2+L/2)/L; ztop=2.5-0.35*math.sin(math.pi*t)-0.02
        mi=[CLOTH_A,CLOTH_B,PAPER,BURLAP][i%4]
        vs=[k.bm.verts.new(p) for p in ((x,0,ztop),(x+w,0,ztop),(x+w,0.02*rnd.uniform(-1,1),ztop-h),(x,0.03,ztop-h*rnd.uniform(0.85,1.0)))]
        f=k.bm.faces.new(vs); f.material_index=mi; f.smooth=True
        vb=[k.bm.verts.new(v.co+Vector((0,0.01,0))) for v in vs]; f2=k.bm.faces.new(vb[::-1]); f2.material_index=mi
        for ff in (f,f2):
            for l in ff.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.z)
        for px in (x+0.05,x+w-0.05): k.box((px,0,ztop+0.02),(0.03,0.04,0.08),WOOD,bevel=0)
        x+=w+rnd.uniform(0.12,0.3); i+=1
def shop_sign(k,emblem="anvil"):
    k.box((0,0.03,0),(0.16,0.1,0.6),IRON,bevel=0.02)
    k.box((0,-0.7,0.22),(0.07,1.4,0.07),IRON,bevel=0.015)
    k.box((0,-0.45,0.0),(0.04,0.04,0.55),IRON,rot=(0.8,0,0),bevel=0)
    for yy in(-0.45,-1.15): k.box((0,yy,0.08),(0.02,0.02,0.24),IRON,bevel=0)
    k.box((0,-0.8,-0.35),(0.1,1.05,0.7),PLANKS,bevel=0.04,segs=2)
    k.box((0,-0.8,-0.35),(0.12,0.9,0.56),WOOD,bevel=0.02)
    if emblem=="anvil":
        k.box((-0.1,-0.8,-0.3),(0.08,0.5,0.12),STEEL,bevel=0.02); k.box((-0.1,-0.8,-0.42),(0.08,0.22,0.14),STEEL,bevel=0.02)
        k.box((-0.1,-0.8,-0.52),(0.08,0.36,0.07),STEEL,bevel=0.01)
        lathe(k,[(0.07,0.0),(0.0,0.14)],center=(-0.1,-1.05,-0.3),segs=6,mi=STEEL)
    elif emblem=="boot":
        k.box((-0.1,-0.78,-0.28),(0.08,0.18,0.38),BREAD,bevel=0.04); k.box((-0.1,-0.9,-0.47),(0.08,0.4,0.14),BREAD,bevel=0.05)
    else:
        lathe(k,[(0.0,-0.62),(0.14,-0.58),(0.2,-0.45),(0.16,-0.32),(0.06,-0.26),(0.06,-0.16),(0.08,-0.14)],center=(-0.1,-0.8,0),segs=10,mi=STAINED)
        for f in k.bm.faces:
            if f.material_index==STAINED: f.smooth=True
EXTRA_SPECS+=[("SM_VK_Wall_Timber_Oriel",lambda k: wall_timber_oriel(k),dict(grime=False)),
              ("SM_VK_Wall_Timber_Door",lambda k: wall_timber_door(k),dict(grime=False)),
              ("SM_VK_Stair_Ext",lambda k: ext_stair(k),dict(wobble=False,grime=True)),
              ("SM_VK_Awning",lambda k: awning(k),dict(wobble=False,grime=False)),
              ("SM_VK_Prop_Laundry",lambda k: laundry(k),dict(wobble=False,grime=True)),
              ("SM_VK_Sign_Anvil",lambda k: shop_sign(k,"anvil"),dict(wobble=False,grime=False)),
              ("SM_VK_Sign_Boot",lambda k: shop_sign(k,"boot"),dict(wobble=False,grime=False)),
              ("SM_VK_Sign_Potion",lambda k: shop_sign(k,"potion"),dict(wobble=False,grime=False))]
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
new=["SM_VK_Wall_Timber_Oriel","SM_VK_Wall_Timber_Door","SM_VK_Stair_Ext","SM_VK_Awning","SM_VK_Prop_Laundry","SM_VK_Sign_Anvil","SM_VK_Sign_Boot","SM_VK_Sign_Potion"]
full_rebuild(new)
for n in new: print(n,len(bpy.data.objects[n].data.polygons))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Wall_Timber_Oriel 1036\nSM_VK_Wall_Timber_Door 811\nSM_VK_Stair_Ext 884\nSM_VK_Awning 118\nSM_VK_Prop_Lau
# ndry 270\nSM_VK_Sign_Anvil 234\nSM_VK_Sign_Boot 202\nSM_VK_Sign_Potion 210\n"}

# ==============================================================================================================
# [0188] 2026-09-23 03:51:36  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
T=vcol("VK_Test")
for o in list(T.objects): bpy.data.objects.remove(o)
org=(100,-172,0); st={"ground":"Stone","plaster":"Rose","shutter":"Blue","roof":"Green","seed":3}
L=9
g={"W":"SM_VK_Wall_Stone_Window","D":"SM_VK_Wall_Stone_Door",".":"SM_VK_Wall_Stone"}
for i,(gc,uc) in enumerate((("W","SM_VK_Wall_Timber_Window"),("D","SM_VK_Wall_Timber_Oriel"),("W","SM_VK_Wall_Timber_Window"))):
    x=-L/2+1.5+3*i
    place_v(T,g[gc],x,-3,0,0,org,st); place_v(T,uc,x,-3,H1,0,org,st)
    place_v(T,"SM_VK_Wall_Stone",x,3,0,180,org,st); place_v(T,"SM_VK_Wall_Timber",x,3,H1,180,org,st)
place_v(T,"SM_VK_Wall_Stone_Window",-L/2,-1.5,0,-90,org,st); place_v(T,"SM_VK_Wall_Stone",-L/2,1.5,0,-90,org,st)
place_v(T,"SM_VK_Wall_Timber_Window",-L/2,-1.5,H1,-90,org,st); place_v(T,"SM_VK_Wall_Timber_X",-L/2,1.5,H1,-90,org,st)
place_v(T,"SM_VK_Wall_Stone",L/2,-1.5,0,90,org,st); place_v(T,"SM_VK_Wall_Stone",L/2,1.5,0,90,org,st)
place_v(T,"SM_VK_Wall_Timber_K",L/2,-1.5,H1,90,org,st); place_v(T,"SM_VK_Wall_Timber_Door",L/2,1.5,H1,90,org,st)
place_v(T,"SM_VK_Stair_Ext",L/2,-1.5,0,90,org,st)
for (cx,cy,r) in ((-L/2,-3,0),(L/2,-3,90),(L/2,3,180),(-L/2,3,-90)):
    place_v(T,"SM_VK_Corner_Stone",cx,cy,0,r,org,st); place_v(T,"SM_VK_Corner_Timber",cx,cy,H1,r,org,st)
top=roof_top(2)
place_v(T,"SM_VK_Roof_Hip",-3,0,top,180,org,st); place_v(T,"SM_VK_Roof_Mid",0,0,top,0,org,st); place_v(T,"SM_VK_Roof_Gable",3,0,top,0,org,st)
place_v(T,"SM_VK_Chimney",-3,0,top,0,org,st)
place_v(T,"SM_VK_Awning",-3,-3,0,0,org,{"cloth":"Green"})
place_v(T,"SM_VK_Sign_Potion",-1.2,-3.3,2.95,0,org,{})
place_v(T,"SM_VK_Prop_Laundry",-9.5,-2,0,90,org,{})
place_v(T,"SM_VK_Deco_Weeds",3,-3,0,0,org,{}); place_v(T,"SM_VK_Deco_Ivy_A",3,-3,0,0,org,{})
place_v(T,"SM_VK_Prop_Planter",-1.05,-3.75,0,0,org,{}); place_v(T,"SM_VK_Prop_Crates",4.2,-5.0,0,15,org,{})
for o in T.objects: o.hide_render=False
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cs=bpy.data.objects["VK_CameraProps"]; cs.data.lens=30
tgt=Vector((100.5,-172,3.8)); cs.location=tgt+Vector((12,-15,3.5))
cs.rotation_euler=(tgt-cs.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cs; SC.render.filepath=os.path.join(out,"_fx1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0189] 2026-09-23 03:52:11  blender  ok
# ==============================================================================================================
import bpy
for o in list(bpy.data.collections["VK_Test"].objects): bpy.data.objects.remove(o)
bpy.ops.wm.save_mainfile()
s=bpy.data.texts["vk_helpers"].as_string()
for fn in ("def street(","def fence_run(","def road_strip(","def build_chapel(","def build_windmill(","def build_guardtower(","def build_tavern(","def build_blacksmith("):
    a=s.index(fn); print(s[a:a+60].splitlines()[0])
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\ndef street(coll,x0,x1,yroad,seed,side_gap=9.5):\ndef fence_run(coll,a,b,
# origin=(0,0,0),gate_at=None):\ndef road_strip(coll,name,pts,w=3.2):\ndef build_chapel(coll,origin,n=4,roof=\"Blue\",tower=True):\ndef build_windmill(c
# oll,origin):\ndef build_guardtower(coll,origin):\ndef build_tavern(coll,origin,seed=31):\ndef build_blacksmith(coll,origin,seed=32):\n"}

# ==============================================================================================================
# [0190] 2026-09-23 03:53:06  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def build_town(coll,C=(200.0,0.0),seed=2027):
    global gardens
    gardens=[]
    cx,cy=C; R=math.radians
    def O(x,y,rot=0.0): return (cx+x,cy+y,R(rot))
    def tag(fn):
        before=set(o.name for o in coll.objects); fn()
    # --- plaza
    build_townhall(coll,O(0,14,0))
    place_v(coll,"SM_VK_Prop_Fountain",cx,cy-1,0,0,(0,0,0),{})
    for (x,y,r_,c) in ((-7.5,-5.5,25,"Red"),(7.5,-5.5,-25,"Blue"),(-9,3,90,"Yellow"),(9,3,-90,"Green")):
        place_v(coll,"SM_VK_MarketStall",cx+x,cy+y,0,r_,(0,0,0),{"cloth":c})
    for (x,y) in ((-13,-9),(13,-9),(-13,9),(13,9)): place_v(coll,"SM_VK_Prop_LampPost",cx+x,cy+y,0,0,(0,0,0),{})
    for (x,y,r_) in ((-4,-9.5,0),(4,-9.5,0)): place_v(coll,"SM_VK_Prop_Bench",cx+x,cy+y,0,r_,(0,0,0),{})
    place_v(coll,"SM_VK_Prop_Cart",cx-11,cy-2,0,70,(0,0,0),{}); place_v(coll,"SM_VK_Prop_Crates",cx+11.5,cy-7,0,20,(0,0,0),{})
    place_v(coll,"SM_VK_Prop_NoticeBoard",cx-11.5,cy+9.5,0,160,(0,0,0),{})
    road_strip(coll,"VK_TownPlaza",[(cx-15,cy),(cx+15,cy)],w=11.5)
    # --- chapel + graveyard (east)
    build_chapel(coll,O(24,2,-90))
    gx0,gx1,gy0,gy1=cx+29.5,cx+41.5,cy-7.5,cy+10.5
    for j in range(6):
        y=gy0+1.5+3*j
        place_v(coll,"SM_VK_LowWall",gx1,y,0,90,(0,0,0),{})
    for i in range(4):
        x=gx0+1.5+3*i
        place_v(coll,"SM_VK_LowWall_Lychgate" if i==1 else "SM_VK_LowWall",x,gy0,0,0,(0,0,0),{})
        place_v(coll,"SM_VK_LowWall",x,gy1,0,0,(0,0,0),{})
    for (x,y) in ((gx0,gy0),(gx1,gy0),(gx1,gy1),(gx0,gy1)): place_v(coll,"SM_VK_LowWall_Post",x,y,0,0,(0,0,0),{})
    rnd=random.Random(seed)
    kinds=["SM_VK_Grave_A","SM_VK_Grave_Cross","SM_VK_Grave_A","SM_VK_Grave_Obelisk"]
    for r_ in range(3):
        for c_ in range(5):
            if rnd.random()<0.2: continue
            place_v(coll,kinds[rnd.randrange(4)],gx0+2.5+c_*2.3+rnd.uniform(-0.2,0.2),gy0+3+r_*4.5,0,rnd.uniform(-8,8),(0,0,0),{})
    place_v(coll,"SM_VK_Deco_Bush",gx1-1.2,gy1-1.3,0,0,(0,0,0),{}); place_v(coll,"SM_VK_Deco_Bush",gx0+1.0,gy1-1.2,0,90,(0,0,0),{})
    # --- tavern (west)
    build_tavern(coll,O(-22,2,90))
    # --- main street (east-west) and the south road
    yroad=cy-22
    street(coll,cx-60,cx-17,yroad,seed+1); street(coll,cx+17,cx+60,yroad,seed+2)
    road_strip(coll,"VK_TownMain",[(cx-64,yroad),(cx-20,yroad+0.5),(cx,yroad),(cx+20,yroad-0.4),(cx+64,yroad)],w=3.4)
    road_strip(coll,"VK_TownSouth",[(cx,cy-11),(cx+0.5,yroad),(cx-0.5,cy-45),(cx,cy-62)],w=2.8)
    # --- crafts along the south road
    build_bakery(coll,O(-9,-37,90)); build_blacksmith(coll,O(10,-37,-90))
    # --- farm quarter
    build_barn(coll,O(-14,-58,0)); build_stable(coll,O(14,-58,180))
    crops=["SM_VK_Crop_Wheat","SM_VK_Crop_Wheat","SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Lavender","SM_VK_Crop_Wheat"]
    for i,cr in enumerate(crops):
        place_v(coll,cr,cx-10.4+(i%4)*3.2,cy-70-(i//4)*3.2,0,0,(0,0,0),{})
    fence_run(coll,(cx-12.2,cy-68.2),(cx+1.6,cy-68.2),(0,0,0),gate_at=2)
    fence_run(coll,(cx-12.2,cy-77.2),(cx+1.6,cy-77.2),(0,0,0))
    fence_run(coll,(cx-12.2,cy-68.2),(cx-12.2,cy-77.2),(0,0,0)); fence_run(coll,(cx+1.6,cy-68.2),(cx+1.6,cy-77.2),(0,0,0))
    place_v(coll,"SM_VK_Prop_Scarecrow",cx-4.8,cy-73,0,25,(0,0,0),{})
    place_v(coll,"SM_VK_Prop_ChickenCoop",cx+6,cy-70,0,-20,(0,0,0),{}); place_v(coll,"SM_VK_Prop_Chickens",cx+6.5,cy-72.5,0,0,(0,0,0),{})
    build_windmill(coll,O(34,-66,-15))
    # --- guard towers at the town entrances
    build_guardtower(coll,O(-67,-26,0)); build_guardtower(coll,O(67,-26,0))
    place_v(coll,"SM_VK_Prop_Signpost",cx-64,yroad+3,0,0,(0,0,0),{}); place_v(coll,"SM_VK_Prop_Signpost",cx+64,yroad+3,0,180,(0,0,0),{})
    # --- laundry lines between some gardens
    for (xa,ya,xb,yb) in gardens[::3]:
        place_v(coll,"SM_VK_Prop_Laundry",(xa+xb)/2,(ya+yb)/2,0,0,(0,0,0),{})
'''
bpy.data.texts["vk_helpers"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string())
# hide old demo collections
for cname in ("VK_Demo","VK_Village","VK_Showcase"):
    c=bpy.data.collections.get(cname)
    if c:
        for o in c.objects: o.hide_render=True; o.hide_viewport=True
V=vcol("VK_Town")
for o in list(V.objects): bpy.data.objects.remove(o)
import time; t0=time.time()
build_town(V)
print("objects",len(V.objects),"time",round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: objects 914 time 0.1\n"}

# ==============================================================================================================
# [0191] 2026-09-23 03:53:30  blender  ok
# ==============================================================================================================
import bpy, mathutils, os
exec(bpy.data.texts["vk_helpers"].as_string())
V=vcol("VK_Town"); cx,cy=200.0,0.0
for o in [o for o in V.objects if o.name.startswith("VK_TTree")]: bpy.data.objects.remove(o)
pts=[o.location.copy() for o in V.objects if not o.name.startswith(("VK_Town",))]
kd=mathutils.kdtree.KDTree(len(pts))
for i,p in enumerate(pts): kd.insert(p,i)
kd.balance()
tw=bpy.data.objects["SM_Tree_Wood"].data; tf=bpy.data.objects["SM_Tree_Foliage"].data
rnd=random.Random(11); n=0; placed=[]
while n<90:
    x=cx+rnd.uniform(-95,95); y=cy+rnd.uniform(-100,55)
    if abs(y-(cy-22))<6: continue
    if abs(x-cx)<5 and cy-65<y<cy-10: continue
    co,idx,dist=kd.find((x,y,0))
    if dist<8.5: continue
    if any((x-px)**2+(y-py)**2<6.5**2 for px,py in placed): continue
    s_=rnd.uniform(0.85,1.25); rz=rnd.uniform(0,6.28)
    for d,nm in ((tw,"W"),(tf,"F")):
        t_=bpy.data.objects.new(f"VK_TTree{n}{nm}",d); V.objects.link(t_); t_.location=(x,y,0); t_.scale=(s_,s_,s_); t_.rotation_euler.z=rz
    placed.append((x,y)); n+=1
for o in V.objects: o.hide_render=False
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cd=bpy.data.cameras.get("VK_CamTown") or bpy.data.cameras.new("VK_CamTown"); cd.lens=24; cd.clip_end=800
ct=bpy.data.objects.get("VK_CameraTown") or bpy.data.objects.new("VK_CameraTown",cd)
if ct.name not in SC.collection.objects: SC.collection.objects.link(ct)
tgt=Vector((cx,cy-22,0)); ct.location=tgt+Vector((45,-95,75))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ct; SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_town1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0192] 2026-09-23 03:53:52  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
SC.render.resolution_percentage=50
ct.data.lens=26
tgt=Vector((cx+2,cy+4,4)); ct.location=Vector((cx-10,cy-24,9))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_town2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
tgt=Vector((cx+22,cy-8,3)); ct.location=Vector((cx+6,cy-26,6))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_town3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0193] 2026-09-23 03:54:24  blender  ok
# ==============================================================================================================
import bpy, mathutils
t=bpy.data.texts["vk_helpers"]; s=t.as_string()
old="    street(coll,cx-60,cx-17,yroad,seed+1); street(coll,cx+17,cx+60,yroad,seed+2)"
assert old in s
s=s.replace(old,'''    street(coll,cx-64,cx-34,yroad,seed+1); street(coll,cx+34,cx+64,yroad,seed+2)
    for (x,nn,sd) in ((-25.5,3,seed+7),(25.5,3,seed+8)):
        st=random_style(sd); build_house_v(coll,O(x,-31.5,180),nn,2,st)''')
code = r'''
def scatter_trees(coll,C=(200.0,0.0),n_trees=90,seed=11,xr=95,yr=(-100,55)):
    cx,cy=C
    for o in [o for o in coll.objects if o.name.startswith("VK_TTree")]: bpy.data.objects.remove(o)
    pts=[o.location.copy() for o in coll.objects if not o.name.startswith("VK_Town")]
    kd=mathutils.kdtree.KDTree(len(pts))
    for i,p in enumerate(pts): kd.insert(p,i)
    kd.balance()
    tw=bpy.data.objects["SM_Tree_Wood"].data; tf=bpy.data.objects["SM_Tree_Foliage"].data
    rnd=random.Random(seed); n=0; placed=[]; tries=0
    while n<n_trees and tries<20000:
        tries+=1
        x=cx+rnd.uniform(-xr,xr); y=cy+rnd.uniform(*yr)
        if abs(y-(cy-22))<6: continue
        if abs(x-cx)<5 and cy-65<y<cy-10: continue
        co,idx,dist=kd.find((x,y,0))
        if dist<8.5: continue
        if any((x-px)**2+(y-py)**2<6.5**2 for px,py in placed): continue
        s_=rnd.uniform(0.85,1.25); rz=rnd.uniform(0,6.28)
        for d,nm in ((tw,"W"),(tf,"F")):
            t_=bpy.data.objects.new(f"VK_TTree{n}{nm}",d); coll.objects.link(t_); t_.location=(x,y,0); t_.scale=(s_,s_,s_); t_.rotation_euler.z=rz
        placed.append((x,y)); n+=1
'''
t.clear(); t.write(s+code); exec(t.as_string())
V=vcol("VK_Town")
for o in list(V.objects): bpy.data.objects.remove(o)
build_town(V); scatter_trees(V)
for o in V.objects: o.hide_render=False
# overlap check: roof/wall pieces from different buildings closer than 1 m in plan
walls=[o for o in V.objects if ("_Wall_" in o.name or "Corner" in o.name) and "_inst" in o.name]
print("objects",len(V.objects),"walls",len(walls))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0; ct.data.lens=24
tgt=Vector((cx,cy-24,0)); ct.location=tgt+Vector((45,-95,75))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_town1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: objects 982 walls 404\n"}

# ==============================================================================================================
# [0194] 2026-09-23 03:54:48  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
ct.data.lens=24
ct.location=Vector((cx-36,cy-24.5,1.8)); tgt=Vector((cx-60,cy-19,3.2))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_town4.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0195] 2026-09-23 03:55:14  blender  ok
# ==============================================================================================================
import bpy, os
n0=len(bpy.data.meshes), len(bpy.data.images), len(bpy.data.materials)
try:
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
except Exception as e: print("purge",e)
print("before",n0,"after",(len(bpy.data.meshes),len(bpy.data.images),len(bpy.data.materials)))
bpy.ops.wm.save_mainfile()
print(round(os.path.getsize(bpy.data.filepath)/1e6,1),"MB")
# ---- result ----
# {"result":"Code executed successfully: before (947, 80, 143) after (729, 76, 139)\nInfo: Saved \"medievalDiorama.blend\"\n140.7 MB\n"}

# ==============================================================================================================
# [0196] 2026-09-23 03:55:30  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=100
if hasattr(SC.eevee,"taa_render_samples"): SC.eevee.taa_render_samples=64
shots=[("town_aerial",(cx+2,cy-22,0),(cx+52,cy-98,58),26),
       ("town_plaza",(cx+2,cy+4,4),(cx-10,cy-24,9),26),
       ("town_street",(cx-60,cy-19,3.2),(cx-36,cy-24.5,1.8),24),
       ("town_farm",(cx+8,cy-66,3.5),(cx-20,cy-95,13),26)]
import time
for name,tgt,loc,lens in shots:
    t0=time.time()
    ct.data.lens=lens; ct.location=Vector(loc); ct.rotation_euler=(Vector(tgt)-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
    print(name,round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: town_aerial 1.3\ntown_plaza 1.1\ntown_street 1.0\ntown_farm 1.1\n"}

# ==============================================================================================================
# [0197] 2026-09-23 03:56:04  blender  ok
# ==============================================================================================================
import bpy
P=bpy.data.collections["VK_Pieces"]
names=sorted(o.name for o in P.objects if o.name.startswith("SM_VK") and "_inst" not in o.name)
print(len(names)); print(names)
# ---- result ----
# {"result":"Code executed successfully: 106\n['SM_VK_Awning', 'SM_VK_Balcony', 'SM_VK_BellTower', 'SM_VK_BreadOven', 'SM_VK_Chapel_Corner', 'SM_VK_Chap
# el_Wall', 'SM_VK_Chapel_Wall_Door', 'SM_VK_Chapel_Wall_Plain', 'SM_VK_Chimney', 'SM_VK_Corner_Barn', 'SM_VK_Corner_Plaster', 'SM_VK_Corner_Stone', 'SM
# _VK_Corner_Timber', 'SM_VK_Crop_Cabbage', 'SM_VK_Crop_Carrot', 'SM_VK_Crop_Lavender', 'SM_VK_Crop_Pumpkin', 'SM_VK_Crop_Wheat', 'SM_VK_Deco_Bush', 'SM
# _VK_Deco_Ivy_A', 'SM_VK_Deco_Ivy_B', 'SM_VK_Deco_Weeds', 'SM_VK_Grave_A', 'SM_VK_Grave_Cross', 'SM_VK_Grave_Obelisk', 'SM_VK_GuardTower', 'SM_VK_Inner
# Corner_Plaster', 'SM_VK_InnerCorner_Stone', 'SM_VK_InnerCorner_Timber', 'SM_VK_LeanTo', 'SM_VK_LeanTo_Thatch', 'SM_VK_LowWall', 'SM_VK_LowWall_Lychgat
# e', 'SM_VK_LowWall_Post', 'SM_VK_MarketStall', 'SM_VK_Porch', 'SM_VK_Prop_Anvil', 'SM_VK_Prop_BakerySign', 'SM_VK_Prop_BarrelStack', 'SM_VK_Prop_Bench

# ==============================================================================================================
# [0198] 2026-09-23 03:56:39  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
exec(bpy.data.texts["vk_helpers"].as_string())
Cc=vcol("VK_Catalog")
for o in list(Cc.objects): bpy.data.objects.remove(o)
for c in ("VK_Town",):
    for o in bpy.data.collections[c].objects: o.hide_render=True
sheets={
 "catalog_walls":["SM_VK_Wall_Stone","SM_VK_Wall_Stone_Window","SM_VK_Wall_Stone_Door","SM_VK_Corner_Stone","SM_VK_InnerCorner_Stone",
   "SM_VK_Wall_Plaster","SM_VK_Wall_Plaster_Window","SM_VK_Wall_Plaster_Door","SM_VK_Corner_Plaster","SM_VK_InnerCorner_Plaster",
   "SM_VK_Wall_Timber","SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K","SM_VK_Wall_Timber_Window","SM_VK_Wall_Timber_Oriel","SM_VK_Wall_Timber_Door","SM_VK_Corner_Timber","SM_VK_InnerCorner_Timber",
   "SM_VK_Wall_Barn","SM_VK_Wall_Barn_Door","SM_VK_Wall_Stall","SM_VK_Corner_Barn","SM_VK_Wall_Arcade",
   "SM_VK_Chapel_Wall","SM_VK_Chapel_Wall_Plain","SM_VK_Chapel_Wall_Door","SM_VK_Chapel_Corner"],
 "catalog_roofs":["SM_VK_Roof_Mid","SM_VK_Roof_Gable","SM_VK_Roof_Hip","SM_VK_Roof_LCorner","SM_VK_Roof_Gable_Stone","SM_VK_Roof_Gable_Planks",
   "SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Gable","SM_VK_RoofThatch_Hip","SM_VK_RoofThatch_Gable_Planks",
   "SM_VK_Roof_Dormer","SM_VK_Roof_Cupola","SM_VK_Chimney","SM_VK_Porch","SM_VK_Balcony","SM_VK_Awning","SM_VK_LeanTo","SM_VK_LeanTo_Thatch","SM_VK_Stair_Ext","SM_VK_BreadOven"],
 "catalog_props":["SM_VK_Prop_Well","SM_VK_Prop_Fountain","SM_VK_MarketStall","SM_VK_Prop_Cart","SM_VK_Prop_LampPost","SM_VK_Prop_Bench","SM_VK_Prop_Table","SM_VK_Prop_Stool",
   "SM_VK_Prop_Crates","SM_VK_Prop_BarrelStack","SM_VK_Prop_Sacks","SM_VK_Prop_Trough","SM_VK_Prop_NoticeBoard","SM_VK_Prop_Signpost","SM_VK_Prop_Woodpile",
   "SM_VK_Prop_Forge","SM_VK_Prop_Anvil","SM_VK_Prop_Grindstone","SM_VK_Prop_WeaponRack","SM_VK_Prop_BreadRack","SM_VK_Prop_Laundry",
   "SM_VK_Prop_FlowerBox","SM_VK_Prop_FlowerBox_Daisy","SM_VK_Prop_Planter","SM_VK_Prop_Lantern","SM_VK_Prop_Sign","SM_VK_Prop_TavernSign","SM_VK_Prop_BakerySign","SM_VK_Sign_Anvil","SM_VK_Sign_Boot","SM_VK_Sign_Potion","SM_VK_Prop_Festoon"],
 "catalog_nature":["SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Lavender","SM_VK_Prop_GardenBed",
   "SM_VK_Prop_Scarecrow","SM_VK_Prop_ChickenCoop","SM_VK_Prop_Chickens","SM_VK_Prop_HayBale","SM_VK_Prop_Haystack","SM_VK_Prop_Fence","SM_VK_Prop_FenceGate",
   "SM_VK_LowWall","SM_VK_LowWall_Post","SM_VK_LowWall_Lychgate","SM_VK_Grave_A","SM_VK_Grave_Cross","SM_VK_Grave_Obelisk",
   "SM_VK_Deco_Ivy_A","SM_VK_Deco_Ivy_B","SM_VK_Deco_Weeds","SM_VK_Deco_Bush"],
 "catalog_landmarks":["SM_VK_BellTower","SM_VK_Windmill","SM_VK_GuardTower"],
}
def dims(n):
    o=bpy.data.objects[n]; me=o.data
    xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
frames={}
Y0=-420.0; gap=1.6
for si,(sheet,names) in enumerate(sheets.items()):
    y0=Y0-si*60; maxw=40.0 if sheet!="catalog_landmarks" else 60
    x=500.0; y=y0; rowh=0; zmax=0; minx=1e9; maxx=-1e9; miny=1e9; maxy=-1e9
    for n in names:
        mnx,mxx,mny,mxy,mnz,mxz=dims(n)
        w=mxx-mnx; d=mxy-mny
        if x-500.0+w>maxw: x=500.0; y-=rowh+gap; rowh=0
        o=bpy.data.objects.new(n+"_cat",bpy.data.objects[n].data); Cc.objects.link(o)
        o.location=(x-mnx,y-mxy,0.0)
        minx=min(minx,x); maxx=max(maxx,x+w); miny=min(miny,y-d); maxy=max(maxy,y); zmax=max(zmax,mxz)
        x+=w+gap; rowh=max(rowh,d)
    frames[sheet]=(minx,maxx,miny,maxy,zmax)
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]
g=bpy.data.objects["VK_Ground"]; gloc=g.location.copy(); gsc=g.scale.copy()
for sheet,(minx,maxx,miny,maxy,zmax) in frames.items():
    c=Vector(((minx+maxx)/2,(miny+maxy)/2,zmax*0.3)); W=maxx-minx; D=maxy-miny
    g.location=(c.x,c.y,0); g.scale=(4,4,1)
    ct.data.lens=35
    dist=max(W,D*1.6,zmax*2.2)*1.05
    ct.location=c+Vector((0,-dist*0.78,dist*0.62))
    ct.rotation_euler=(c-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,sheet+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
g.location=gloc; g.scale=gsc
print(frames)
# ---- result ----
# {"result":"Code executed successfully: {'catalog_walls': (500.0, 536.0413662433626, -429.11219830513005, -420.0, 6.350000381469727), 'catalog_roofs': 
# (500.0, 536.9453082203867, -505.3246527433396, -480.0, 9.549824714660645), 'catalog_props': (500.0, 536.840226429701, -552.5606065660716, -540.0, 3.81
# 9999933242798), 'catalog_nature': (500.0, 539.8948434084656, -611.0285586833954, -600.0, 4.012880802154541), 'catalog_landmarks': (500.0, 520.23196763
# 99231, -669.1806526184082, -660.0, 19.040000915527344)}\n"}

# ==============================================================================================================
# [0199] 2026-09-23 03:57:20  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
exec(bpy.data.texts["vk_helpers"].as_string())
Cc=vcol("VK_Catalog")
for o in list(Cc.objects): bpy.data.objects.remove(o)
# (reuse the sheets dict from the previous step by rebuilding it)
sheets={
 "catalog_walls":["SM_VK_Wall_Stone","SM_VK_Wall_Stone_Window","SM_VK_Wall_Stone_Door","SM_VK_Corner_Stone","SM_VK_InnerCorner_Stone",
   "SM_VK_Wall_Plaster","SM_VK_Wall_Plaster_Window","SM_VK_Wall_Plaster_Door","SM_VK_Corner_Plaster","SM_VK_InnerCorner_Plaster",
   "SM_VK_Wall_Timber","SM_VK_Wall_Timber_X","SM_VK_Wall_Timber_K","SM_VK_Wall_Timber_Window","SM_VK_Wall_Timber_Oriel","SM_VK_Wall_Timber_Door","SM_VK_Corner_Timber","SM_VK_InnerCorner_Timber",
   "SM_VK_Wall_Barn","SM_VK_Wall_Barn_Door","SM_VK_Wall_Stall","SM_VK_Corner_Barn","SM_VK_Wall_Arcade",
   "SM_VK_Chapel_Wall","SM_VK_Chapel_Wall_Plain","SM_VK_Chapel_Wall_Door","SM_VK_Chapel_Corner"],
 "catalog_roofs":["SM_VK_Roof_Mid","SM_VK_Roof_Gable","SM_VK_Roof_Hip","SM_VK_Roof_LCorner","SM_VK_Roof_Gable_Stone","SM_VK_Roof_Gable_Planks",
   "SM_VK_RoofThatch_Mid","SM_VK_RoofThatch_Gable","SM_VK_RoofThatch_Hip","SM_VK_RoofThatch_Gable_Planks",
   "SM_VK_Roof_Dormer","SM_VK_Roof_Cupola","SM_VK_Chimney","SM_VK_Porch","SM_VK_Balcony","SM_VK_Awning","SM_VK_LeanTo","SM_VK_LeanTo_Thatch","SM_VK_Stair_Ext","SM_VK_BreadOven"],
 "catalog_props":["SM_VK_Prop_Well","SM_VK_Prop_Fountain","SM_VK_MarketStall","SM_VK_Prop_Cart","SM_VK_Prop_LampPost","SM_VK_Prop_Bench","SM_VK_Prop_Table","SM_VK_Prop_Stool",
   "SM_VK_Prop_Crates","SM_VK_Prop_BarrelStack","SM_VK_Prop_Sacks","SM_VK_Prop_Trough","SM_VK_Prop_NoticeBoard","SM_VK_Prop_Signpost","SM_VK_Prop_Woodpile",
   "SM_VK_Prop_Forge","SM_VK_Prop_Anvil","SM_VK_Prop_Grindstone","SM_VK_Prop_WeaponRack","SM_VK_Prop_BreadRack","SM_VK_Prop_Laundry",
   "SM_VK_Prop_FlowerBox","SM_VK_Prop_FlowerBox_Daisy","SM_VK_Prop_Planter","SM_VK_Prop_Lantern","SM_VK_Prop_Sign","SM_VK_Prop_TavernSign","SM_VK_Prop_BakerySign","SM_VK_Sign_Anvil","SM_VK_Sign_Boot","SM_VK_Sign_Potion","SM_VK_Prop_Festoon"],
 "catalog_nature":["SM_VK_Crop_Wheat","SM_VK_Crop_Cabbage","SM_VK_Crop_Carrot","SM_VK_Crop_Pumpkin","SM_VK_Crop_Lavender","SM_VK_Prop_GardenBed",
   "SM_VK_Prop_Scarecrow","SM_VK_Prop_ChickenCoop","SM_VK_Prop_Chickens","SM_VK_Prop_HayBale","SM_VK_Prop_Haystack","SM_VK_Prop_Fence","SM_VK_Prop_FenceGate",
   "SM_VK_LowWall","SM_VK_LowWall_Post","SM_VK_LowWall_Lychgate","SM_VK_Grave_A","SM_VK_Grave_Cross","SM_VK_Grave_Obelisk",
   "SM_VK_Deco_Ivy_A","SM_VK_Deco_Ivy_B","SM_VK_Deco_Weeds","SM_VK_Deco_Bush"],
}
def dims(n):
    me=bpy.data.objects[n].data
    xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
frames={}; gap=1.4
for si,(sheet,names) in enumerate(sheets.items()):
    y0=-420.0-si*80; maxw=34.0 if sheet!="catalog_props" else 30.0
    x=500.0; y=y0; rowh=0; zmax=0; minx=1e9; maxx=-1e9; miny=1e9; maxy=-1e9
    for n in names:
        mnx,mxx,mny,mxy,mnz,mxz=dims(n); w=mxx-mnx; d=mxy-mny
        if x-500.0+w>maxw: x=500.0; y-=rowh+gap; rowh=0
        o=bpy.data.objects.new(n+"_cat",bpy.data.objects[n].data); Cc.objects.link(o)
        o.location=(x-mnx,y-mxy,0.0)
        minx=min(minx,x); maxx=max(maxx,x+w); miny=min(miny,y-d); maxy=max(maxy,y); zmax=max(zmax,mxz)
        x+=w+gap; rowh=max(rowh,d,mxz*0.95)
    frames[sheet]=(minx,maxx,miny,maxy,zmax)
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; g=bpy.data.objects["VK_Ground"]; gloc=g.location.copy(); gsc=g.scale.copy()
for sheet,(minx,maxx,miny,maxy,zmax) in frames.items():
    c=Vector(((minx+maxx)/2,(miny+maxy)/2,zmax*0.25)); W=maxx-minx; D=maxy-miny
    g.location=(c.x,c.y,0); g.scale=(3,3,1)
    ct.data.lens=32
    # fit: horizontal FOV for 16:9 at lens 32 ~ 58 deg
    dist=max(W*0.95,D*1.75)
    ct.location=c+Vector((0,-dist*0.72,dist*0.72))
    ct.rotation_euler=(c-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,sheet+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
g.location=gloc; g.scale=gsc
print({k:(round(v[1]-v[0],1),round(v[3]-v[2],1)) for k,v in frames.items()})
# ---- result ----
# {"result":"Code executed successfully: {'catalog_walls': (33.0, 15.8), 'catalog_roofs': (33.0, 33.7), 'catalog_props': (29.5, 16.6), 'catalog_nature':
#  (34.0, 11.7)}\n"}

# ==============================================================================================================
# [0200] 2026-09-23 03:57:52  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
exec(bpy.data.texts["vk_helpers"].as_string())
Cc=vcol("VK_Catalog")
def dims(n):
    me=bpy.data.objects[n].data
    xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
# lift pieces that extend below ground
for o in Cc.objects:
    n=o.name[:-4]
    mnx,mxx,mny,mxy,mnz,mxz=dims(n)
    if mnz<-0.05: o.location.z=-mnz
# recompute frames per sheet from actual object bounds
sheets={}
for o in Cc.objects:
    key=round(o.location.y/80)
    sheets.setdefault(key,[]).append(o)
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; g=bpy.data.objects["VK_Ground"]; gloc=g.location.copy(); gsc=g.scale.copy()
names={-5:"catalog_walls",-6:"catalog_roofs",-7:"catalog_props",-8:"catalog_nature"}
for key,objs in sorted(sheets.items(),reverse=True):
    pts=[]
    for o in objs:
        n=o.name[:-4]; mnx,mxx,mny,mxy,mnz,mxz=dims(n)
        pts+= [o.location+Vector((mnx,mny,0)),o.location+Vector((mxx,mxy,mxz+max(0,-mnz)))]
    minx=min(p.x for p in pts); maxx=max(p.x for p in pts); miny=min(p.y for p in pts); maxy=max(p.y for p in pts); zmax=max(p.z for p in pts)
    c=Vector(((minx+maxx)/2,(miny+maxy)/2,zmax*0.2)); W=maxx-minx; D=maxy-miny
    g.location=(c.x,c.y,0); g.scale=(3,3,1)
    ct.data.lens=32
    dist=max(W*0.9,D*1.55)
    ct.location=c+Vector((0,-dist*0.75,dist*0.7))
    ct.rotation_euler=(c-ct.location).to_track_quat("-Z","Y").to_euler()
    nm=names.get(key,f"catalog_{key}")
    SC.camera=ct; SC.render.filepath=os.path.join(out,nm+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
    print(nm,key,len(objs),round(W,1),round(D,1))
g.location=gloc; g.scale=gsc
# ---- result ----
# {"result":"Code executed successfully: catalog_walls -5 27 33.0 15.8\ncatalog_roofs -6 11 30.4 19.6\ncatalog_props -7 41 33.0 75.7\ncatalog_nature -8 
# 23 34.0 11.7\n"}

# ==============================================================================================================
# [0201] 2026-09-23 03:58:19  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
exec(bpy.data.texts["vk_helpers"].as_string())
Cc=vcol("VK_Catalog")
def dims(n):
    me=bpy.data.objects[n].data
    xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
groups={
 "catalog_walls":lambda n: n.startswith(("SM_VK_Wall","SM_VK_Corner","SM_VK_InnerCorner","SM_VK_Chapel")),
 "catalog_roofs":lambda n: n.startswith(("SM_VK_Roof","SM_VK_Chimney","SM_VK_Porch","SM_VK_Balcony","SM_VK_Awning","SM_VK_LeanTo","SM_VK_Stair_Ext","SM_VK_BreadOven")),
 "catalog_nature":lambda n: n.startswith(("SM_VK_Crop","SM_VK_Deco","SM_VK_Grave","SM_VK_LowWall","SM_VK_Prop_Scarecrow","SM_VK_Prop_Chicken","SM_VK_Prop_Hay","SM_VK_Prop_Fence","SM_VK_Prop_GardenBed")),
}
def grp(n):
    for k,f in groups.items():
        if f(n): return k
    return "catalog_props"
sheets={}
for o in Cc.objects: sheets.setdefault(grp(o.name[:-4]),[]).append(o)
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; g=bpy.data.objects["VK_Ground"]; gloc=g.location.copy(); gsc=g.scale.copy()
for nm,objs in sheets.items():
    pts=[]
    for o in objs:
        n=o.name[:-4]; mnx,mxx,mny,mxy,mnz,mxz=dims(n)
        pts+= [o.location+Vector((mnx,mny,0)),o.location+Vector((mxx,mxy,mxz-min(0,mnz)))]
    minx=min(p.x for p in pts); maxx=max(p.x for p in pts); miny=min(p.y for p in pts); maxy=max(p.y for p in pts); zmax=max(p.z for p in pts)
    c=Vector(((minx+maxx)/2,(miny+maxy)/2,zmax*0.2)); W=maxx-minx; D=maxy-miny
    g.location=(c.x,c.y,0); g.scale=(3,3,1)
    ct.data.lens=32
    dist=max(W*0.9,D*1.55)
    ct.location=c+Vector((0,-dist*0.75,dist*0.7))
    ct.rotation_euler=(c-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,nm+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
    print(nm,len(objs),round(W,1),round(D,1))
g.location=gloc; g.scale=gsc
# ---- result ----
# {"result":"Code executed successfully: catalog_walls 27 33.0 15.8\ncatalog_roofs 20 33.0 33.7\ncatalog_props 32 29.5 16.6\ncatalog_nature 23 34.0 11.7
# \n"}

# ==============================================================================================================
# [0202] 2026-09-23 03:58:40  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
for o in bpy.data.collections["VK_Town"].objects: o.hide_render=False
for o in bpy.data.collections["VK_Catalog"].objects: o.hide_render=True
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=100
ct.data.lens=24
tgt=Vector((cx+4,cy-30,0)); ct.location=Vector((cx+60,cy-128,70))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ct; SC.render.filepath=os.path.join(out,"town_aerial.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# material close-up: a south-row house facade
ct.data.lens=40
tgt=Vector((cx+25.5,cy-28.4,2.6)); ct.location=Vector((cx+31,cy-20.5,2.3))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"town_detail.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0203] 2026-09-23 03:59:09  blender  ok
# ==============================================================================================================
import bpy
SC=bpy.data.scenes["VillageKit"]
keep={"VK_Town","VK_Staging"}
stray=[]
for o in SC.objects:
    if o.type!="MESH" or o.hide_render: continue
    cols={c.name for c in o.users_collection}
    if not (cols & keep): stray.append((o.name,[c for c in cols],tuple(round(v,1) for v in o.location)))
print(stray[:20], len(stray))
# ---- result ----
# {"result":"Code executed successfully: [('SM_VK_MarketStall', ['VK_Pieces'], (0.0, 0.0, 0.0))] 1\n"}

# ==============================================================================================================
# [0204] 2026-09-23 03:59:26  blender  ERROR
# ==============================================================================================================
import bpy, os
from mathutils import Vector
# 1) hide every kit master piece from render (they live at the origin)
for o in bpy.data.collections["VK_Pieces"].objects: o.hide_render=True; o.hide_viewport=True
# 2) roofs: rougher, less specular -> no frosty sheen
exec(bpy.data.texts["vk_mat"].as_string())
mt=bpy.data.texts["vk_mat"]; ms=mt.as_string()
for key in ('"M_VK_RoofRed"','"M_VK_RoofBlue"','"M_VK_Roof_Blue"','"M_VK_Roof_Green"'):
    pass
ms=ms.replace(' "M_VK_RoofRed":dict(prefix="T_VK_RoofRed",nstr=1.1),',' "M_VK_RoofRed":dict(prefix="T_VK_RoofRed",nstr=1.0,rough_mul=1.25,spec=0.18),')
ms=ms.replace(' "M_VK_RoofBlue":dict(prefix="T_VK_RoofBlue",nstr=1.1),',' "M_VK_RoofBlue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18),')
ms=ms.replace(' "M_VK_Roof_Blue":dict(prefix="T_VK_RoofBlue",nstr=1.1),',' "M_VK_Roof_Blue":dict(prefix="T_VK_RoofBlue",nstr=1.0,rough_mul=1.25,spec=0.18),')
ms=ms.replace(' "M_VK_Roof_Green":dict(prefix="T_VK_RoofGreen",nstr=1.1),',' "M_VK_Roof_Green":dict(prefix="T_VK_RoofGreen",nstr=1.0,rough_mul=1.2,spec=0.18),')
mt.clear(); mt.write(ms); exec(ms)
for mn in ("M_VK_RoofRed","M_VK_RoofBlue","M_VK_Roof_Blue","M_VK_Roof_Green"):
    pbr_material(bpy.data.materials[mn],**MAT_MAP[mn])
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
SC.render.filepath=os.path.join(out,"town_detail.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
ct.data.lens=24
tgt=Vector((cx+4,cy-30,0)); ct.location=Vector((cx+60,cy-128,70))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"town_aerial.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: 'bpy_prop_collection[key]: key \"M_VK_RoofBlue\" not found'"}

# ==============================================================================================================
# [0205] 2026-09-23 03:59:42  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
exec(bpy.data.texts["vk_mat"].as_string())
done=[]
for mn in ("M_VK_RoofRed","M_VK_RoofBlue","M_VK_Roof_Blue","M_VK_Roof_Green"):
    m=bpy.data.materials.get(mn)
    if m: pbr_material(m,**MAT_MAP[mn]); done.append(mn)
print(done)
# check the red roof roughness map range
import numpy as np
im=bpy.data.images["T_VK_RoofRed_R"]; a=np.array(im.pixels[:],np.float32).reshape(-1,4)[:,0]
print("roof R min/mean/max",a.min(),a.mean(),a.max())
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
ct.data.lens=40
tgt=Vector((cx+25.5,cy-28.4,2.6)); ct.location=Vector((cx+31,cy-20.5,2.3))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ct; SC.render.resolution_percentage=50
SC.render.filepath=os.path.join(out,"_detail_test.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: ['M_VK_RoofRed', 'M_VK_Roof_Blue', 'M_VK_Roof_Green']\nroof R min/mean/max 0.2901961 0.7032465 1.0\n"}

# ==============================================================================================================
# [0206] 2026-09-23 03:59:57  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
SC.render.resolution_percentage=100
shots=[("town_detail",(cx+25.5,cy-28.4,2.6),(cx+31,cy-20.5,2.3),40),
       ("town_aerial",(cx+4,cy-30,0),(cx+60,cy-128,70),24),
       ("town_plaza",(cx+2,cy+4,4),(cx-10,cy-24,9),26),
       ("town_street",(cx-60,cy-19,3.2),(cx-36,cy-24.5,1.8),24),
       ("town_farm",(cx+8,cy-66,3.5),(cx-20,cy-95,13),26)]
for name,tgt,loc,lens in shots:
    ct.data.lens=lens; ct.location=Vector(loc); ct.rotation_euler=(Vector(tgt)-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
for f in os.listdir(out):
    if f.startswith("_") and f.endswith(".png"): os.remove(os.path.join(out,f))
for img in bpy.data.images:
    if img.name.startswith("T_VK") and img.has_data and not img.packed_file:
        try: img.pack()
        except Exception as e: print(img.name,e)
bpy.ops.wm.save_mainfile()
print(round(os.path.getsize(bpy.data.filepath)/1e6,1),"MB")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n140.8 MB\n"}

# ==============================================================================================================
# [0207] 2026-09-23 10:47:37  blender  ok
# ==============================================================================================================
import bpy
exec(bpy.data.texts["vk_helpers"].as_string())
print("kit mats:",len(kit_mats()), "CROPS=",CROPS)
print(sorted(t.name for t in bpy.data.texts))
print("driver ns ok:", "vk" in bpy.app.driver_namespace or True)
# ---- result ----
# {"result":"Code executed successfully: kit mats: 33 CROPS= 32\n['mc_helpers', 'tree_build', 'tree_skeleton', 'vk_helpers', 'vk_mat', 'vk_tex', 'vk_tex
# gen', 'wk_helpers']\ndriver ns ok: True\n"}

# ==============================================================================================================
# [0208] 2026-09-23 10:48:23  blender  ok
# ==============================================================================================================
import bpy
code = r'''
# =====================  NATURE TEXTURES  =====================
def warp(field,du,dv):
    S=field.shape[0]
    yy,xx=np.mgrid[0:S,0:S].astype(f32)
    X=(xx+du*S)%S; Y=(yy+dv*S)%S
    x0=np.floor(X).astype(np.int32); y0=np.floor(Y).astype(np.int32); fx=X-x0; fy=Y-y0
    x1=(x0+1)%S; y1=(y0+1)%S; x0%=S; y0%=S
    return (field[y0,x0]*(1-fx)*(1-fy)+field[y0,x1]*fx*(1-fy)+field[y1,x0]*(1-fx)*fy+field[y1,x1]*fx*fy).astype(f32)
def ramp3(t,c0,c1,c2,mid=0.5):
    t=np.clip(t,0,1)[...,None]; c0=np.array(c0,f32); c1=np.array(c1,f32); c2=np.array(c2,f32)
    return np.where(t<mid,c0+(c1-c0)*(t/mid),c1+(c2-c1)*((t-mid)/(1-mid))).astype(f32)
def gen_bark_oak(S=1024,seed=201,tile=1.2,depth=0.07):
    x,y=grid(S)
    n1=fbm(S,2.4,seed+1,fmin=3,fmax=40,ay=5.0)
    n1=warp(n1,fbm(S,3.0,seed+7,fmin=1.5)*0.03,np.zeros((S,S),f32))
    plates=smooth(0.1,0.6,np.abs(n1))
    n2=fbm(S,2.2,seed+2,fmin=3,fmax=40,ax=4.0)
    gate=smooth(0.2,0.9,fbm(S,2.2,seed+3,fmin=2,fmax=30))
    breaks=(1-smooth(0.0,0.14,np.abs(n2)))*gate
    fine=fbm(S,1.8,seed+4,fmin=40,fmax=300,ay=3.0)
    h=0.12+0.72*plates*(1-0.6*breaks)+0.05*fine*plates+facets(S,seed+8,6,50,0.05)*plates
    h=blur(np.clip(h,0,1),0.8)
    n=normal_from_height(blur(h,2.0),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.09,0.07,0.055),(0.29,0.23,0.18),(0.47,0.40,0.32),0.45)
    col=col*(0.8+0.35*light[...,None])*(1+0.05*fbm(S,3,seed+9,fmin=2)[...,None])
    lich=smooth(1.35,1.9,fbm(S,2.6,seed+5,fmin=5,fmax=80))*plates
    col=col*(1-0.55*lich[...,None])+np.array([0.56,0.60,0.46],f32)*0.55*lich[...,None]*(0.8+0.3*light[...,None])
    moss=smooth(0.9,1.8,fbm(S,3.0,seed+6,fmin=2))*(1-plates)
    col=col*(1-0.5*moss[...,None])+np.array([0.20,0.30,0.09],f32)*0.5*moss[...,None]
    rough=np.clip(0.84+0.12*(1-plates),0,1)
    PBR_SETS["T_VK_BarkOak"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkOak",col,h,rough,depth,tile,ao_in_albedo=0.6)
def gen_bark_birch(S=1024,seed=211,tile=1.0,depth=0.02):
    x,y=grid(S)
    base=np.array([0.88,0.86,0.80],f32)*(0.93+0.06*fbm(S,3.0,seed,fmin=2)[...,None]+0.04*fbm(S,2.0,seed+1,fmin=4,ax=8)[...,None])
    lent=smooth(1.45,2.0,fbm(S,1.6,seed+2,fmin=25,fmax=220,ax=7.0))
    patch=smooth(1.75,2.25,fbm(S,2.9,seed+3,fmin=2,fmax=30,ax=1.7))
    rim=smooth(1.45,1.75,fbm(S,2.9,seed+3,fmin=2,fmax=30,ax=1.7))*(1-patch)
    peel=smooth(1.55,1.95,fbm(S,2.4,seed+4,fmin=6,fmax=60,ax=3.0))*(1-patch)
    h=0.5+0.03*fbm(S,2.0,seed+5,fmin=8,ax=5)-0.22*lent-0.12*patch+0.08*fbm(S,1.5,seed+6,fmin=60)*patch+0.1*peel
    h=blur(np.clip(h,0,1),0.6)
    col=base*(1-0.8*lent[...,None])+np.array([0.16,0.14,0.13],f32)*0.8*lent[...,None]
    col=col*(1-0.25*rim[...,None])
    col=col*(1-patch[...,None])+np.array([0.09,0.08,0.08],f32)*(0.8+0.3*fbm(S,2,seed+7,fmin=10)[...,None])*patch[...,None]
    col=col*(1-0.6*peel[...,None])+np.array([0.84,0.70,0.56],f32)*0.6*peel[...,None]
    rough=np.clip(0.68+0.25*patch+0.1*lent,0,1)
    PBR_SETS["T_VK_BarkBirch"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkBirch",col,h,rough,depth,tile,ao_in_albedo=0.35)
def gen_bark_pine(S=1024,seed=221,tile=1.4,depth=0.08):
    rng=np.random.default_rng(seed); x,y=grid(S)
    xw=(x+fbm(S,3.0,seed,fmin=2)*0.015)%1; yw=(y+fbm(S,3.0,seed+1,fmin=2)*0.015)%1
    npts=80; pts=rng.uniform(0,1,(npts,2))
    F1,F2,ID=voronoi(xw,yw,pts,sx=1.0,sy=0.42)
    e=F2-F1; plate=smooth(0.003,0.028,e)
    rid=rng.uniform(0.55,1.0,npts).astype(f32); grey=(rng.random(npts)<0.3).astype(f32)
    step=smooth(0.02,0.05,e)*0.12
    h=plate*(0.45+0.3*rid[ID]+step+0.05*fbm(S,1.8,seed+2,fmin=30,ay=3))+(1-plate)*0.08
    h=blur(np.clip(h,0,1),0.7)
    n=normal_from_height(blur(h,2.0),depth*2.5,tile); light=painted_light(n)
    tint=rng.uniform(0.85,1.12,npts).astype(f32)
    pc=np.array([0.50,0.27,0.15],f32)*tint[ID][...,None]
    pc=pc*(1-0.5*grey[ID][...,None])+np.array([0.44,0.38,0.33],f32)*0.5*grey[ID][...,None]
    col=pc*(0.72+0.45*light[...,None])+np.array([0.10,0.04,0.0],f32)*smooth(0.6,0.9,light)[...,None]
    col=col*plate[...,None]+np.array([0.13,0.10,0.085],f32)*(1-plate[...,None])
    rough=np.clip(0.82+0.12*(1-plate),0,1)
    PBR_SETS["T_VK_BarkPine"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkPine",col,h,rough,depth,tile,ao_in_albedo=0.55)
def gen_endgrain(S=512,seed=231):
    rng=np.random.default_rng(seed); x,y=grid(S); cx=x-0.5; cy=y-0.5
    r=np.sqrt(cx*cx+cy*cy)*2.0; ang=np.arctan2(cy,cx)
    wr=r+0.025*fbm(S,3.2,seed,fmin=2)+0.012*np.sin(ang*3+1.3)
    rings=(np.sin(2*np.pi*wr*15)*0.5+0.5)**1.6
    col=ramp3(1-rings*0.8,(0.56,0.38,0.22),(0.72,0.54,0.34),(0.84,0.68,0.46),0.5)
    col=col*(0.85+0.15*smooth(0.1,0.45,r))[...,None]
    sap=smooth(0.72,0.8,r)*(1-smooth(0.88,0.9,r))
    col=col*(1-0.3*sap[...,None])+np.array([0.9,0.78,0.58],f32)*0.3*sap[...,None]
    barkm=smooth(0.88,0.91,r)
    bark=np.array([0.22,0.15,0.10],f32)*(0.8+0.4*(fbm(S,2,seed+1,fmin=20)*0.5+0.5))[...,None]
    col=col*(1-barkm[...,None])+bark*barkm[...,None]
    crack=np.zeros((S,S),f32)
    for i in range(6):
        a0=rng.uniform(-math.pi,math.pi); L=rng.uniform(0.25,0.7)
        da=np.abs(((ang-a0)+math.pi)%(2*math.pi)-math.pi)
        w=0.02*(1-np.clip(r/L,0,1))+0.004
        crack=np.maximum(crack,(1-smooth(0,w,da*r))*(r<L)*(r>0.02))
    pith=1-smooth(0.02,0.045,r)
    col=col*(1-0.75*crack[...,None])*(1-0.6*pith[...,None])
    outside=smooth(0.985,1.0,r)
    h=np.clip(0.55-0.05*rings-0.35*crack+0.15*barkm*(0.7+0.3*fbm(S,2,seed+2,fmin=20)),0,1)
    rough=np.clip(0.8+0.15*barkm,0,1)
    PBR_SETS["T_VK_EndGrain"]=dict(depth=0.01,tile=0.6)
    return write_set("T_VK_EndGrain",col.astype(f32),h.astype(f32),rough.astype(f32),0.01,0.6,ao_in_albedo=0.3)
def gen_moss(S=1024,seed=241,tile=1.0,depth=0.035):
    rng=np.random.default_rng(seed); x,y=grid(S)
    pts=rng.uniform(0,1,(140,2)); F1,F2,ID=voronoi(x,y,pts)
    cush=np.clip(1-F1/0.06,0,1)**0.6
    clumps=fbm(S,2.6,seed,fmin=3,fmax=60); fuzz=fbm(S,1.1,seed+1,fmin=150)
    h=np.clip(0.35+0.35*cush+0.12*clumps+0.06*fuzz,0,1)
    h=blur(h,0.6)
    n=normal_from_height(blur(h,1.5),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.10,0.17,0.04),(0.26,0.42,0.09),(0.52,0.64,0.18),0.55)
    col=col*(0.78+0.35*light[...,None])
    spr=smooth(1.9,2.4,fbm(S,1.0,seed+2,fmin=90))
    col=col*(1-spr[...,None])+np.array([0.72,0.74,0.30],f32)*spr[...,None]
    tintz=fbm(S,3.0,seed+3,fmin=1.5)[...,None]
    col=col*(1+0.06*tintz*np.array([1.0,0.6,-0.5],f32))
    rough=np.clip(0.92+0.05*fuzz,0,1)
    PBR_SETS["T_VK_Moss"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_Moss",col.astype(f32),h,rough.astype(f32),depth,tile,ao_in_albedo=0.5)
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
import time
for fn in (gen_bark_oak,gen_bark_birch,gen_bark_pine,gen_endgrain,gen_moss):
    t0=time.time(); fn(); print(fn.__name__,round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: gen_bark_oak 1.7\ngen_bark_birch 1.3\ngen_bark_pine 1.8\ngen_endgrain 0.3\ngen_moss 2.5\n"}

# ==============================================================================================================
# [0209] 2026-09-23 10:48:42  blender  ok
# ==============================================================================================================
import bpy, numpy as np
names=["BarkOak","BarkBirch","BarkPine","EndGrain","Moss"]
T=384
def thumb(name):
    im=bpy.data.images[name]; W,H=im.size
    a=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1,:,:3]
    step=max(1,W//T); a=a[::step,::step][:T,:T]
    return a
rows=[np.concatenate([thumb(f"T_VK_{n}_BC") for n in names],1),np.concatenate([thumb(f"T_VK_{n}_N") for n in names],1)]
sheet=np.concatenate(rows,0); H,W=sheet.shape[:2]
img=bpy.data.images.new("_texsheet2",W,H,alpha=False)
img.pixels.foreach_set(np.concatenate([sheet[::-1],np.ones((H,W,1),np.float32)],-1).ravel())
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\_texsheet2.png"
img.filepath_raw=out; img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0210] 2026-09-23 10:49:32  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def gen_bark_oak(S=1024,seed=201,tile=1.2,depth=0.07):
    rng=np.random.default_rng(seed); x,y=grid(S)
    N=7
    wv=fbm(S,2.8,seed,fmin=1,fmax=10,ay=3.0)*0.32+fbm(S,2.2,seed+11,fmin=4,fmax=30,ay=4.0)*0.07
    u=x*N+wv
    cell=np.floor(u).astype(np.int32); f=u-cell; cid=cell%N
    M=rng.integers(2,5,N); ph=rng.uniform(0,1,N).astype(f32)
    v=y*M[cid]+ph[cid]; g=v-np.floor(v)
    brk=(1-smooth(0.0,0.045,np.minimum(g,1-g)))
    brk_gate=(rng.random(N*6)<0.75).astype(f32)[(cid*6+np.floor(v).astype(np.int32)%6)]
    brk=brk*brk_gate
    split=(rng.random(N)<0.5).astype(f32)[cid]
    sv=y*2+ph[cid]*1.7; sg=sv-np.floor(sv)
    split_mask=split*smooth(0.25,0.35,sg)*(1-smooth(0.65,0.75,sg))
    dome=np.clip(np.sin(np.pi*np.clip(f,0,1)),0,1)**0.55
    dome=dome*(1-split_mask*(1-smooth(0.0,0.09,np.abs(f-0.5))))
    fib=fbm(S,1.5,seed+2,fmin=20,fmax=260,ay=6.0)
    h=0.1+0.75*dome*(1-0.7*brk)+0.035*fib*dome+facets(S,seed+8,6,50,0.04)*dome
    h=blur(np.clip(h,0,1),0.8)
    n=normal_from_height(blur(h,2.5),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.07,0.055,0.045),(0.27,0.21,0.16),(0.46,0.39,0.31),0.45)
    col=col*(0.78+0.38*light[...,None])*(1+0.05*fbm(S,3,seed+9,fmin=2)[...,None])
    lich=smooth(1.45,2.0,fbm(S,2.6,seed+5,fmin=5,fmax=80))*smooth(0.4,0.7,h)
    col=col*(1-0.55*lich[...,None])+np.array([0.57,0.61,0.47],f32)*0.55*lich[...,None]*(0.8+0.3*light[...,None])
    moss=smooth(1.0,1.9,fbm(S,3.0,seed+6,fmin=2))*(1-smooth(0.2,0.45,h))
    col=col*(1-0.6*moss[...,None])+np.array([0.20,0.31,0.08],f32)*0.6*moss[...,None]
    rough=np.clip(0.84+0.12*(1-dome),0,1)
    PBR_SETS["T_VK_BarkOak"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkOak",col,h,rough,depth,tile,ao_in_albedo=0.6)
def gen_endgrain(S=512,seed=231):
    rng=np.random.default_rng(seed); x,y=grid(S); cx=x-0.5; cy=y-0.5
    r=np.sqrt(cx*cx+cy*cy)*2.0; ang=np.arctan2(cy,cx)
    wr=r*(1+0.03*np.sin(ang*2+0.7)+0.02*np.sin(ang*5+2.1))+0.008*fbm(S,3.2,seed,fmin=2)
    nr=11.5
    rr=wr*nr; fr=rr-np.floor(rr)
    late=smooth(0.72,0.9,fr)*(1-smooth(0.93,1.0,fr))
    wood=ramp3(smooth(0.05,0.85,r),(0.62,0.44,0.26),(0.78,0.60,0.38),(0.86,0.70,0.48),0.5)
    col=wood*(1-0.42*late[...,None])
    col=col*(1+0.05*fbm(S,2.4,seed+3,fmin=6)[...,None])
    barkm=smooth(0.885,0.905,r)
    bark=np.array([0.24,0.16,0.10],f32)*(0.75+0.45*(fbm(S,2,seed+1,fmin=20)*0.5+0.5))[...,None]
    cambium=smooth(0.86,0.88,r)*(1-barkm)
    col=col*(1-0.35*cambium[...,None])
    col=col*(1-barkm[...,None])+bark*barkm[...,None]
    crack=np.zeros((S,S),f32)
    for i in range(4):
        a0=rng.uniform(-math.pi,math.pi); r_in=rng.uniform(0.35,0.6)
        da=np.abs(((ang-a0)+math.pi)%(2*math.pi)-math.pi)
        wid=0.012+0.05*np.clip((r-r_in)/(0.9-r_in),0,1)
        crack=np.maximum(crack,(1-smooth(0.0,wid,da*np.maximum(r,1e-3)*1.0))*(r>r_in)*(r<0.9))
    pith=1-smooth(0.015,0.04,r)
    col=col*(1-0.8*crack[...,None])*(1-0.5*pith[...,None])
    h=np.clip(0.55-0.04*late-0.4*crack+0.18*barkm*(0.6+0.4*(fbm(S,2,seed+2,fmin=20)*0.5+0.5)),0,1)
    rough=np.clip(0.8+0.15*barkm,0,1)
    PBR_SETS["T_VK_EndGrain"]=dict(depth=0.01,tile=0.6)
    return write_set("T_VK_EndGrain",col.astype(f32),h.astype(f32),rough.astype(f32),0.01,0.6,ao_in_albedo=0.3)
'''
t=bpy.data.texts["vk_texgen"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(t.as_string())
gen_bark_oak(); gen_endgrain()
import numpy as np
T=512
def thumb(name,T=512):
    im=bpy.data.images[name]; W,H=im.size
    a=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1,:,:3]
    step=max(1,W//T); return a[::step,::step][:T,:T]
sheet=np.concatenate([thumb("T_VK_BarkOak_BC"),thumb("T_VK_BarkOak_N"),thumb("T_VK_EndGrain_BC")],1)
H,W=sheet.shape[:2]
img=bpy.data.images.new("_ts",W,H,alpha=False); img.pixels.foreach_set(np.concatenate([sheet[::-1],np.ones((H,W,1),np.float32)],-1).ravel())
img.filepath_raw=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\_texsheet2.png"
img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0211] 2026-09-23 10:49:58  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_texgen"]; s=t.as_string()
a=s.rindex("def gen_bark_oak("); b=s.index("def gen_endgrain(",a)
new='''def gen_bark_oak(S=1024,seed=201,tile=1.2,depth=0.07):
    rng=np.random.default_rng(seed); x,y=grid(S)
    N=7
    wv=fbm(S,2.8,seed,fmin=1,fmax=10,ay=3.0)*0.32+fbm(S,2.2,seed+11,fmin=4,fmax=30,ay=4.0)*0.07
    u=x*N+wv
    cell=np.floor(u).astype(np.int32); f=u-cell; cid=cell%N
    M=rng.integers(2,5,N); ph=rng.uniform(0,1,N).astype(f32); tilt=rng.uniform(-0.35,0.35,N).astype(f32)
    v=y*M[cid]+ph[cid]+tilt[cid]*(f-0.5)+0.05*fbm(S,2.4,seed+12,fmin=3,fmax=40)
    g=v-np.floor(v)
    wid=0.03+0.02*(fbm(S,2.0,seed+13,fmin=3,fmax=30)*0.5+0.5)
    brk=(1-smooth(0.0,1.0,np.minimum(g,1-g)/wid))
    seg=np.floor(v).astype(np.int32)%6
    brk_gate=(rng.random(N*6)<0.7).astype(f32)[cid*6+seg]
    brk=brk*brk_gate*smooth(0.08,0.3,np.minimum(f,1-f))
    dome=np.clip(np.sin(np.pi*np.clip(f,0,1)),0,1)**0.55
    fib=fbm(S,1.5,seed+2,fmin=20,fmax=260,ay=6.0)
    h=0.1+0.75*dome*(1-0.65*brk)+0.035*fib*dome+facets(S,seed+8,6,50,0.04)*dome
    h=blur(np.clip(h,0,1),0.8)
    n=normal_from_height(blur(h,2.5),depth*2.5,tile); light=painted_light(n)
    col=ramp3(h,(0.07,0.055,0.045),(0.27,0.21,0.16),(0.46,0.39,0.31),0.45)
    col=col*(0.78+0.38*light[...,None])*(1+0.05*fbm(S,3,seed+9,fmin=2)[...,None])
    lich=smooth(1.45,2.0,fbm(S,2.6,seed+5,fmin=5,fmax=80))*smooth(0.4,0.7,h)
    col=col*(1-0.55*lich[...,None])+np.array([0.57,0.61,0.47],f32)*0.55*lich[...,None]*(0.8+0.3*light[...,None])
    moss=smooth(1.0,1.9,fbm(S,3.0,seed+6,fmin=2))*(1-smooth(0.2,0.45,h))
    col=col*(1-0.6*moss[...,None])+np.array([0.20,0.31,0.08],f32)*0.6*moss[...,None]
    rough=np.clip(0.84+0.12*(1-dome),0,1)
    PBR_SETS["T_VK_BarkOak"]=dict(depth=depth,tile=tile)
    return write_set("T_VK_BarkOak",col,h,rough,depth,tile,ao_in_albedo=0.6)
'''
s=s[:a]+new+s[b:]; t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(s)
gen_bark_oak()
import numpy as np
def thumb(name,T=512):
    im=bpy.data.images[name]; W,H=im.size
    a=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1,:,:3]
    step=max(1,W//T); return a[::step,::step][:T,:T]
sheet=np.concatenate([thumb("T_VK_BarkOak_BC"),thumb("T_VK_BarkOak_N")],1); H,W=sheet.shape[:2]
img=bpy.data.images.new("_ts",W,H,alpha=False); img.pixels.foreach_set(np.concatenate([sheet[::-1],np.ones((H,W,1),np.float32)],-1).ravel())
img.filepath_raw=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\_texsheet2.png"
img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0212] 2026-09-23 10:52:59  blender  ERROR
# ==============================================================================================================
import bpy
code = r'''
LEAF_CELLS=["broadleaf","broadleaf_dark","autumn_orange","autumn_red",
            "birch","pine","willow","fern",
            "berry","blossom","apple","hydrangea",
            "reeds","tallgrass","wildflowers","deadtwigs"]
AT=2048; CS=AT//4
def cell_bounds(name,m=6):
    i=LEAF_CELLS.index(name); cx=i%4; cy=i//4
    return (cx*CS+m, cy*CS+m, (cx+1)*CS-m, (cy+1)*CS-m)
class Painter:
    def __init__(s,S):
        s.S=S; s.img=np.zeros((S,S,3),f32); s.a=np.zeros((S,S),f32); s.h=np.zeros((S,S),f32)
    def _box(s,B,x0,y0,x1,y1):
        x0=int(max(B[0],math.floor(x0))); x1=int(min(B[2],math.ceil(x1))); y0=int(max(B[1],math.floor(y0))); y1=int(min(B[3],math.ceil(y1)))
        return (x0,y0,x1,y1) if (x1>x0 and y1>y0) else None
    def put(s,bx,cov,col,h):
        x0,y0,x1,y1=bx
        reg=s.img[y0:y1,x0:x1]; a=cov[...,None]
        reg[:]=reg*(1-a)+col*a
        ar=s.a[y0:y1,x0:x1]; ar[:]=np.maximum(ar,cov)
        hr=s.h[y0:y1,x0:x1]; hr[:]=hr*(1-cov)+h*cov
    def inside(s,B,x,y,m=0):
        return B[0]+m<=x<=B[2]-m and B[1]+m<=y<=B[3]-m
    def seg(s,B,ax,ay,bx_,by,w,col,h=0.35,col2=None):
        r=w*0.5+2
        bb=s._box(B,min(ax,bx_)-r,min(ay,by)-r,max(ax,bx_)+r,max(ay,by)+r)
        if not bb: return
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        dx,dy=bx_-ax,by-ay; L2=dx*dx+dy*dy+1e-6
        t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/L2,0,1)
        d=np.hypot(xx-(ax+t*dx),yy-(ay+t*dy))
        cov=np.clip(w*0.5-d+0.5,0,1)
        if cov.max()<=0: return
        q=np.clip(1-d/(w*0.5+1e-3),0,1)
        c0=np.array(col,f32)[None,None,:]
        if col2 is not None: c0=c0*(1-t[...,None])+np.array(col2,f32)[None,None,:]*t[...,None]
        c=c0*(0.72+0.34*q)[...,None]
        s.put(bb,cov,c,h*(0.6+0.4*q))
    def poly(s,B,pts,w0,w1,col,h=0.35,col2=None):
        n=len(pts)-1
        for i in range(n):
            w=w0+(w1-w0)*i/max(1,n-1)
            c=col if col2 is None else tuple(np.array(col)+(np.array(col2)-np.array(col))*i/max(1,n-1))
            s.seg(B,pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],w,c,h)
    def fitL(s,B,x,y,ang,L,W):
        ca,sa=math.cos(ang),math.sin(ang); m=W+3; lim=L
        if ca>1e-4: lim=min(lim,(B[2]-m-x)/ca)
        if ca<-1e-4: lim=min(lim,(B[0]+m-x)/ca)
        if sa>1e-4: lim=min(lim,(B[3]-m-y)/sa)
        if sa<-1e-4: lim=min(lim,(B[1]+m-y)/sa)
        return lim
    def leaf(s,B,x,y,ang,L,W,col,kind=0,bend=0.0,side=1.0,fit=True,minL=18):
        if not s.inside(B,x,y,W*0.5): return
        if fit:
            L2=s.fitL(B,x,y,ang,L,W)
            if L2<minL: return
            if L2<L: W=W*(0.6+0.4*L2/L); L=L2
        ca,sa=math.cos(ang),math.sin(ang)
        mx=x+ca*L/2; my=y+sa*L/2; R=L/2+W+3
        bb=s._box(B,mx-R,my-R,mx+R,my+R)
        if not bb: return
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        dx=xx-x; dy=yy-y
        sl=(dx*ca+dy*sa)/L; tt=(-dx*sa+dy*ca)
        slc=np.clip(sl,0,1)
        tt=tt-bend*L*np.sin(np.pi*slc)
        if kind==2: prof=W*np.sqrt(np.clip(1-(2*slc-1)**2,0,1))
        elif kind==3: prof=W*np.clip(1-slc,0,1)**0.8*np.clip(slc*8,0,1)
        else:
            prof=W*np.clip(np.sin(np.pi*slc),0,1)**0.7*(1-0.3*slc)
            if kind==1: prof=prof*(0.66+0.34*np.abs(np.cos(3.5*np.pi*slc)))
        cov=np.clip(prof-np.abs(tt)+0.7,0,1)*((sl>0)&(sl<1))
        if cov.max()<=0: return
        rel=np.abs(tt)/np.maximum(prof,1e-3)
        shade=0.74+0.36*slc+0.07*np.sign(tt)*side
        mid=1-0.25*np.exp(-(tt/1.3)**2)*(slc<0.95)
        vein=1-0.08*((np.abs(np.sin((slc*7-rel*1.3)*np.pi))<0.14)&(rel<0.85))
        edge=1-0.18*np.clip(1-(prof-np.abs(tt))/2.5,0,1)
        c=np.array(col,f32)[None,None,:]*(shade*mid*vein*edge)[...,None]
        hh=0.45+0.4*np.sqrt(np.clip(1-rel**2,0,1))*np.clip(np.sin(np.pi*slc),0,1)**0.4-0.1*(1-mid)
        s.put(bb,cov,c,hh)
    def disc(s,B,x,y,r,col,h=0.7,hl=True):
        if not s.inside(B,x,y,r+1): return
        bb=s._box(B,x-r-2,y-r-2,x+r+2,y+r+2)
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        d=np.hypot(xx-x,yy-y); cov=np.clip(r-d+0.7,0,1)
        q=np.clip(1-d/r,0,1)
        c=np.array(col,f32)[None,None,:]*(0.6+0.48*np.sqrt(q))[...,None]
        if hl:
            hd=np.hypot(xx-(x-r*0.35),yy-(y-r*0.38)); hi=np.clip(1-hd/(r*0.32),0,1)**1.5
            c=c*(1-hi[...,None]*0.75)+np.array([1,0.98,0.92],f32)*hi[...,None]*0.75
        s.put(bb,cov,c,h*np.sqrt(np.clip(1-(d/r)**2,0,1)))
    def flower(s,B,x,y,r,n,col,ccol,rot=0.0,inner=0.25,sharp=0.8,h=0.6,ragged=0.0):
        if not s.inside(B,x,y,r+1): return
        bb=s._box(B,x-r-2,y-r-2,x+r+2,y+r+2)
        x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32)
        dx=xx-x; dy=yy-y; d=np.hypot(dx,dy); th=np.arctan2(dy,dx)+rot
        R=r*(0.5+0.5*np.abs(np.cos(n*th/2))**sharp)
        if ragged: R=R*(1-ragged*np.abs(np.sin(n*3*th)))
        cov=np.clip(R-d+0.7,0,1)
        if cov.max()<=0: return
        q=np.clip(d/r,0,1)
        c=np.array(col,f32)[None,None,:]*(0.7+0.4*q)[...,None]
        sep=np.abs(np.cos(n*th/2))<0.1
        c=c*(1-0.22*(sep&(q>inner))[...,None])
        ci=np.clip((inner*r-d)*0.8+0.5,0,1)
        c=c*(1-ci[...,None])+np.array(ccol,f32)[None,None,:]*(0.75+0.35*np.clip(1-d/(inner*r+1e-3),0,1))[...,None]*ci[...,None]
        s.put(bb,cov,c,h*(0.6+0.4*(1-q)))
def twig(P,B,rng,x0,y0,ang,L,w,col,depth,maxd,out,leaf_step=18,nkids=2,curl=0.12,kid_ang=(0.45,0.85),kid_len=(0.5,0.7)):
    n=max(3,int(L/10)); pts=[(x0,y0)]; a=ang; x,y=x0,y0
    for i in range(n):
        a+=rng.uniform(-curl,curl); nx=x+math.cos(a)*L/n; ny=y+math.sin(a)*L/n
        if not P.inside(B,nx,ny,26): break
        x,y=nx,ny; pts.append((x,y))
    if len(pts)<2: return
    P.poly(B,pts,w,max(1.2,w*0.45),col)
    acc=0.0
    for i in range(1,len(pts)):
        (xa,ya),(xb,yb)=pts[i-1],pts[i]; acc+=math.hypot(xb-xa,yb-ya)
        if acc>=leaf_step: acc=0.0; out.append((xb,yb,math.atan2(yb-ya,xb-xa),depth,False))
    xa,ya=pts[-2]; out.append((pts[-1][0],pts[-1][1],math.atan2(pts[-1][1]-ya,pts[-1][0]-xa),depth,True))
    if depth<maxd:
        for kk in range(nkids):
            t=rng.uniform(0.3,0.85); i=max(1,int(t*(len(pts)-1))); bx,by=pts[i]
            sd=1 if kk%2==0 else -1
            twig(P,B,rng,bx,by,a+sd*rng.uniform(*kid_ang),L*rng.uniform(*kid_len),w*0.6,col,depth+1,maxd,out,leaf_step,nkids,curl,kid_ang,kid_len)
def cell_broad(P,name,rng,pal,kind=0,dens=1.0,Lr=(70,105),Wr=(0.28,0.36),stem=(0.30,0.21,0.12),maxd=2,twigL=0.62):
    B=cell_bounds(name); cx=(B[0]+B[2])/2; bot=B[3]-4; H=B[3]-B[1]
    pts=[]
    twig(P,B,rng,cx+rng.uniform(-15,15),bot,-math.pi/2+rng.uniform(-0.12,0.12),H*twigL,7,stem,0,maxd,pts,leaf_step=22/dens)
    order=list(range(len(pts))); rng.shuffle(order)
    for j in order:
        x,y,a,d,tip=pts[j]
        for sd in ((0,) if tip else (-1,1)):
            aa=a+rng.uniform(-0.2,0.2) if sd==0 else a+sd*rng.uniform(0.5,1.1)
            L=rng.uniform(*Lr)*(0.85 if d>=2 else 1.0); W=L*rng.uniform(*Wr)
            col=np.array(pal[rng.integers(0,len(pal))],f32)*rng.uniform(0.88,1.12)
            P.leaf(B,x,y,aa,L,W,col,kind=kind,bend=rng.uniform(-0.1,0.1),side=sd or 1)
    return B,pts
def cell_pine(P,rng):
    B=cell_bounds("pine"); cx=(B[0]+B[2])/2; bot=B[3]-4
    dark=np.array((0.08,0.24,0.16),f32); tipc=np.array((0.22,0.44,0.26),f32)
    def spray(x0,y0,ang,L,w,nl):
        pts=[(x0,y0)]; a=ang; x,y=x0,y0; n=max(4,int(L/7))
        for i in range(n):
            a+=rng.uniform(-0.04,0.04); nx=x+math.cos(a)*L/n; ny=y+math.sin(a)*L/n
            if not P.inside(B,nx,ny,18): break
            x,y=nx,ny; pts.append((x,y))
        P.poly(B,pts,w,max(1.5,w*0.4),(0.32,0.22,0.13))
        return pts
    def needles(pts,Lmax,taper=True):
        N=len(pts)
        for i in range(1,N):
            (xa,ya),(xb,yb)=pts[i-1],pts[i]; a=math.atan2(yb-ya,xb-xa)
            f=i/(N-1); Ln=Lmax*((1-0.55*f) if taper else 1.0)
            for sd in (-1,1):
                for rep in range(2):
                    na=a+sd*rng.uniform(0.45,0.85); Lr=Ln*rng.uniform(0.8,1.1)
                    ex=xb+math.cos(na)*Lr; ey=yb+math.sin(na)*Lr
                    if not P.inside(B,ex,ey,4): continue
                    c1=dark*rng.uniform(0.85,1.15); c2=tipc*rng.uniform(0.85,1.15)
                    P.seg(B,xb,yb,ex,ey,rng.uniform(3.0,4.2),c1,0.5,col2=c2)
    main=spray(cx+rng.uniform(-10,10),bot,-math.pi/2+rng.uniform(-0.06,0.06),(B[3]-B[1])*0.92,8,0)
    for k in range(7):
        t=rng.uniform(0.12,0.7); i=max(1,int(t*(len(main)-1))); bx,by=main[i]
        sd=1 if k%2==0 else -1
        br=spray(bx,by,-math.pi/2+sd*rng.uniform(0.55,0.9),rng.uniform(90,150)*(1-0.5*t),4,0)
        needles(br,rng.uniform(30,40))
    needles(main,rng.uniform(40,50))
def cell_willow(P,rng):
    B=cell_bounds("willow"); pal=[(0.46,0.62,0.18),(0.37,0.53,0.14),(0.56,0.67,0.24),(0.30,0.46,0.12)]
    for k in range(5):
        x0=B[0]+55+k*(B[2]-B[0]-110)/4+rng.uniform(-12,12); ph=rng.uniform(0,6.28); amp=rng.uniform(8,22)
        pts=[]
        for i in range(34):
            t=i/33; y=B[1]+4+t*(B[3]-B[1]-10); x=x0+amp*math.sin(t*math.pi*1.2+ph)+t*t*rng.uniform(-10,10)
            pts.append((x,y))
        P.poly(B,pts,2.8,1.4,(0.34,0.36,0.14))
        acc=0
        for i in range(1,len(pts)):
            (xa,ya),(xb,yb)=pts[i-1],pts[i]
            for sd in (-1,1):
                if rng.random()<0.85:
                    a=math.pi/2+sd*rng.uniform(0.3,0.65)
                    L=rng.uniform(40,58); col=np.array(pal[rng.integers(0,4)],f32)*rng.uniform(0.88,1.12)
                    P.leaf(B,xb,yb,a,L,rng.uniform(7,9.5),col,kind=0,bend=rng.uniform(-0.12,0.12),side=sd)
def cell_fern(P,rng):
    B=cell_bounds("fern"); pal=[(0.22,0.48,0.13),(0.28,0.55,0.16),(0.18,0.42,0.11),(0.34,0.60,0.2)]
    x0=B[0]+215; y0=B[3]-4; H=B[3]-B[1]-10
    pts=[]
    for i in range(60):
        t=i/59; pts.append((x0+95*t**1.6, y0-H*t))
    P.poly(B,pts,7,2,(0.30,0.36,0.14))
    for i in range(3,len(pts)-1,2):
        t=i/59; (xa,ya),(xb,yb)=pts[i-1],pts[i]; a=math.atan2(yb-ya,xb-xa)
        Lp=175*(1-t)**0.75*min(1,t*6)
        for sd in (-1,1):
            col=np.array(pal[rng.integers(0,4)],f32)*rng.uniform(0.9,1.1)
            P.leaf(B,xb,yb,a+sd*rng.uniform(1.05,1.3),Lp,Lp*0.17,col,kind=1,bend=0.05*sd,side=sd,minL=10)
def cell_berry(P,rng):
    pal=[(0.10,0.28,0.08),(0.14,0.33,0.10),(0.18,0.38,0.12),(0.08,0.24,0.08)]
    B,pts=cell_broad(P,"berry",rng,pal,kind=0,dens=0.9,Lr=(62,92))
    for k in range(9):
        x,y,a,d,tip=pts[rng.integers(0,len(pts))]
        cx=x+rng.uniform(-25,25); cy=y+rng.uniform(-25,10)
        for j in range(rng.integers(4,8)):
            bx=cx+rng.uniform(-18,18); by=cy+rng.uniform(-16,16)
            col=(0.80,0.07,0.10) if rng.random()<0.75 else (0.52,0.04,0.12)
            P.disc(B,bx,by,rng.uniform(9,12.5),col,0.8)
def cell_blossom(P,rng):
    B=cell_bounds("blossom"); cx=(B[0]+B[2])/2; bot=B[3]-4; H=B[3]-B[1]
    pts=[]
    twig(P,B,rng,cx,bot,-math.pi/2+rng.uniform(-0.1,0.1),H*0.6,7,(0.30,0.19,0.13),0,2,pts,leaf_step=20)
    for (x,y,a,d,tip) in pts[::2]:
        for sd in (-1,1):
            if rng.random()<0.5: P.leaf(B,x,y,a+sd*rng.uniform(0.6,1.0),rng.uniform(40,55),rng.uniform(13,17),np.array((0.42,0.62,0.2),f32)*rng.uniform(0.9,1.1),kind=0,side=sd)
    pinks=[(0.98,0.72,0.82),(0.95,0.60,0.74),(1.0,0.84,0.90),(0.90,0.52,0.68)]
    for (x,y,a,d,tip) in pts:
        for j in range(3 if tip else 1):
            fx=x+rng.uniform(-24,24); fy=y+rng.uniform(-24,24)
            P.flower(B,fx,fy,rng.uniform(19,27),5,pinks[rng.integers(0,4)],(0.98,0.85,0.35),rot=rng.uniform(0,6.28),inner=0.22,sharp=0.6)
def cell_apple(P,rng):
    pal=[(0.26,0.50,0.12),(0.33,0.56,0.15),(0.22,0.44,0.10),(0.40,0.60,0.18)]
    B,pts=cell_broad(P,"apple",rng,pal,kind=0,dens=0.9,Lr=(65,95))
    picks=rng.choice(len(pts),min(6,len(pts)),replace=False)
    for j in picks:
        x,y,a,d,tip=pts[j]; ax=x+rng.uniform(-10,10); ay=y+rng.uniform(8,22); r=rng.uniform(22,29)
        if not P.inside(B,ax,ay,r+2): continue
        P.seg(B,ax,ay-r*0.7,ax+rng.uniform(-6,6),ay-r*1.25,3,(0.28,0.2,0.1))
        P.disc(B,ax,ay,r,(0.80,0.12,0.08),0.9)
        bb=P._box(B,ax-r,ay-r,ax+r,ay+r); x0,y0,x1,y1=bb
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(f32); d=np.hypot(xx-ax,yy-ay)
        blush=np.clip((yy-(ay-r*0.2))/(r*1.2),0,1)*np.clip(r-d,0,1)*0.6
        reg=P.img[y0:y1,x0:x1]; reg[:]=reg*(1-blush[...,None])+np.array((0.85,0.62,0.16),f32)*blush[...,None]
def cell_hydrangea(P,rng):
    B=cell_bounds("hydrangea"); cx=(B[0]+B[2])/2; bot=B[3]-4
    pal=[(0.12,0.30,0.10),(0.16,0.36,0.12),(0.20,0.40,0.14)]
    for k in range(12):
        a=-math.pi/2+rng.uniform(-1.3,1.3); x=cx+rng.uniform(-60,60); y=bot-rng.uniform(10,120)
        P.leaf(B,x,y,a,rng.uniform(105,145),rng.uniform(42,55),np.array(pal[rng.integers(0,3)],f32)*rng.uniform(0.9,1.1),kind=0,bend=rng.uniform(-0.1,0.1))
    balls=[(cx-95,B[1]+170,95),(cx+95,B[1]+150,100),(cx+5,B[1]+300,105)]
    cols=[(0.44,0.55,0.92),(0.60,0.50,0.88),(0.50,0.66,0.95),(0.70,0.55,0.90),(0.40,0.48,0.85)]
    for (bx,by,br) in balls:
        base_i=rng.integers(0,5)
        for j in range(95):
            rr=br*math.sqrt(rng.random()); aa=rng.uniform(0,6.28); fx=bx+math.cos(aa)*rr; fy=by+math.sin(aa)*rr
            shade=0.8+0.3*(1-(fy-by+br)/(2*br))
            c=np.array(cols[(base_i+rng.integers(0,2))%5],f32)*shade*rng.uniform(0.92,1.08)
            P.flower(B,fx,fy,rng.uniform(12,16),4,c,(0.95,0.95,0.85),rot=rng.uniform(0,6.28),inner=0.16,sharp=0.5)
def blades(P,B,rng,n,Lr,wr,spread,cols,tipc=None,xmargin=40):
    for i in range(n):
        x=rng.uniform(B[0]+xmargin,B[2]-xmargin); y=B[3]-4; a=-math.pi/2+rng.uniform(-spread,spread); L=rng.uniform(*Lr); w=rng.uniform(*wr)
        pts=[(x,y)]
        for j in range(12):
            a+=rng.uniform(-0.03,0.03)+0.012*(1 if a>-math.pi/2 else -1)
            nx=pts[-1][0]+math.cos(a)*L/12; ny=pts[-1][1]+math.sin(a)*L/12
            if not P.inside(B,nx,ny,6): break
            pts.append((nx,ny))
        c=np.array(cols[rng.integers(0,len(cols))],f32)*rng.uniform(0.88,1.15)
        P.poly(B,pts,w,1.2,tuple(c),0.45,col2=tuple(c*1.25) if tipc is None else tipc)
    return
def cell_reeds(P,rng):
    B=cell_bounds("reeds")
    blades(P,B,rng,34,(300,490),(7,11),0.14,[(0.26,0.40,0.18),(0.32,0.46,0.20),(0.22,0.36,0.16)])
    for k in range(6):
        x=rng.uniform(B[0]+60,B[2]-60); ytop=B[1]+rng.uniform(40,130)
        P.seg(B,x,B[3]-4,x+rng.uniform(-8,8),ytop,3.5,(0.36,0.42,0.2))
        P.seg(B,x,ytop+20,x,ytop-30,2.0,(0.4,0.36,0.22))
        P.seg(B,x,ytop+25,x,ytop+85,15,(0.38,0.21,0.10),0.8)
def cell_tallgrass(P,rng):
    B=cell_bounds("tallgrass")
    cols=[(0.40,0.56,0.17),(0.52,0.60,0.24),(0.60,0.64,0.30),(0.32,0.50,0.14)]
    blades(P,B,rng,60,(180,420),(5,9),0.36,cols)
    for k in range(12):
        x=rng.uniform(B[0]+60,B[2]-60); ytop=B[1]+rng.uniform(30,160)
        P.seg(B,x,B[3]-4,x+rng.uniform(-15,15),ytop,2.5,(0.5,0.56,0.26))
        for j in range(7):
            yy=ytop+j*10; 
            for sd in (-1,1): P.leaf(B,x,yy,-math.pi/2+sd*0.35,20,4.5,(0.78,0.72,0.46),kind=2,fit=True,minL=8)
def cell_wildflowers(P,rng):
    B=cell_bounds("wildflowers")
    blades(P,B,rng,30,(90,260),(5,8),0.45,[(0.30,0.50,0.14),(0.38,0.56,0.18)])
    kinds=[("poppy",(0.90,0.12,0.08),(0.12,0.08,0.06),5,(20,26),0.2,0.5,0.0),
           ("corn",(0.28,0.42,0.92),(0.2,0.22,0.5),10,(16,21),0.18,1.5,0.25),
           ("butter",(0.98,0.84,0.16),(0.9,0.6,0.1),5,(12,15),0.22,0.5,0.0),
           ("daisy",(0.97,0.96,0.92),(0.96,0.72,0.12),12,(14,18),0.3,1.2,0.0)]
    for k in range(26):
        kd=kinds[rng.integers(0,4)]
        x=rng.uniform(B[0]+40,B[2]-40); y=B[1]+rng.uniform(40,(B[3]-B[1])*0.62)
        P.seg(B,x+rng.uniform(-15,15),B[3]-4,x,y+kd[4][0],2.4,(0.30,0.46,0.14))
        P.flower(B,x,y,rng.uniform(*kd[4]),kd[3],kd[1],kd[2],rot=rng.uniform(0,6.28),inner=kd[5],sharp=kd[6],ragged=kd[7])
def cell_deadtwigs(P,rng):
    B=cell_bounds("deadtwigs"); cx=(B[0]+B[2])/2
    def rec(x,y,a,L,w,d):
        pts=[(x,y)]; n=max(3,int(L/12))
        for i in range(n):
            a+=rng.uniform(-0.18,0.18); nx=pts[-1][0]+math.cos(a)*L/n; ny=pts[-1][1]+math.sin(a)*L/n
            if not P.inside(B,nx,ny,8): break
            pts.append((nx,ny))
        c=np.array((0.34,0.27,0.20),f32)*rng.uniform(0.85,1.2)
        P.poly(B,pts,w,max(1.2,w*0.55),tuple(c),0.4,col2=tuple(c*1.25))
        if d<5 and len(pts)>2:
            for kk in range(2 if d<2 else rng.integers(1,3)):
                i=rng.integers(1,len(pts)); bx,by=pts[i]
                rec(bx,by,a+(1 if kk%2==0 else -1)*rng.uniform(0.35,0.8),L*rng.uniform(0.5,0.72),w*0.62,d+1)
    rec(cx,B[3]-4,-math.pi/2,(B[3]-B[1])*0.5,10,0)
def paint_leaf_atlas(seed=301):
    P=Painter(AT); rng=np.random.default_rng(seed)
    broad=[(0.20,0.42,0.10),(0.27,0.49,0.12),(0.34,0.56,0.15),(0.16,0.36,0.08),(0.40,0.60,0.18)]
    dark=[(0.10,0.26,0.07),(0.14,0.32,0.09),(0.18,0.36,0.11),(0.08,0.22,0.08)]
    aor=[(0.86,0.46,0.08),(0.95,0.62,0.12),(0.78,0.32,0.06),(0.92,0.74,0.20),(0.70,0.40,0.08)]
    ard=[(0.72,0.14,0.07),(0.86,0.26,0.08),(0.58,0.10,0.07),(0.90,0.46,0.10),(0.80,0.20,0.10)]
    birch=[(0.45,0.62,0.16),(0.55,0.68,0.20),(0.38,0.55,0.12),(0.62,0.72,0.26)]
    cell_broad(P,"broadleaf",rng,broad,kind=0,dens=1.1)
    cell_broad(P,"broadleaf_dark",rng,dark,kind=0,dens=1.2)
    cell_broad(P,"autumn_orange",rng,aor,kind=1,dens=1.05,Wr=(0.34,0.42))
    cell_broad(P,"autumn_red",rng,ard,kind=1,dens=1.05,Wr=(0.34,0.42))
    cell_broad(P,"birch",rng,birch,kind=2,dens=1.2,Lr=(40,56),Wr=(0.55,0.7),stem=(0.36,0.30,0.24),maxd=3,twigL=0.55)
    cell_pine(P,rng); cell_willow(P,rng); cell_fern(P,rng)
    cell_berry(P,rng); cell_blossom(P,rng); cell_apple(P,rng); cell_hydrangea(P,rng)
    cell_reeds(P,rng); cell_tallgrass(P,rng); cell_wildflowers(P,rng); cell_deadtwigs(P,rng)
    return P
def save_leaf_atlas(P,name="T_VK_Leaves"):
    img=P.img.copy(); a=P.a.copy()
    rgb=img.copy(); m=a>0.5
    for _ in range(10):
        grow=m.copy()
        for sh in((1,0),(-1,0),(0,1),(0,-1)):
            ma=np.roll(m,sh,(0,1)); fill=(~grow)&ma
            rgb[fill]=np.roll(rgb,sh,(0,1))[fill]; grow|=fill
        m=grow
    S=P.S
    rgba=np.concatenate([np.clip(rgb,0,1),a[...,None]],-1).astype(f32)
    im=bpy.data.images.get(name+"_BCA")
    if im is None: im=bpy.data.images.new(name+"_BCA",S,S,alpha=True)
    elif tuple(im.size)!=(S,S): im.scale(S,S)
    im.alpha_mode="STRAIGHT"
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel()); im.update()
    im.filepath_raw=os.path.join(TEXDIR,name+"_BCA.png"); im.file_format="PNG"; im.save(); im.pack()
    nrm=normal_from_height(blur(P.h,0.8),0.012,3.0)*0.5+0.5
    write_map(name+"_N",nrm,True)
'''
t=bpy.data.texts.get("vk_leafgen") or bpy.data.texts.new("vk_leafgen"); t.clear(); t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(code)
import time; t0=time.time()
P=paint_leaf_atlas(); t1=time.time()
save_leaf_atlas(P); print("paint",round(t1-t0,1),"save",round(time.time()-t1,1))
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: list index out of range"}

# ==============================================================================================================
# [0213] 2026-09-23 10:53:27  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_leafgen"]; s=t.as_string()
s=s.replace('''    def inside(s,B,x,y,m=0):
        return B[0]+m<=x<=B[2]-m and B[1]+m<=y<=B[3]-m''','''    def inside(s,B,x,y,m=0,mb=None):
        mb=m if mb is None else mb
        return B[0]+m<=x<=B[2]-m and B[1]+m<=y<=B[3]-mb''')
s=s.replace("        if not P.inside(B,nx,ny,26): break\n        x,y=nx,ny; pts.append((x,y))\n    if len(pts)<2: return",
            "        if not P.inside(B,nx,ny,26,2): break\n        x,y=nx,ny; pts.append((x,y))\n    if len(pts)<2: return")
s=s.replace("            if not P.inside(B,nx,ny,18): break\n            x,y=nx,ny; pts.append((x,y))\n        P.poly(B,pts,w,max(1.5,w*0.4),(0.32,0.22,0.13))",
            "            if not P.inside(B,nx,ny,18,2): break\n            x,y=nx,ny; pts.append((x,y))\n        P.poly(B,pts,w,max(1.5,w*0.4),(0.32,0.22,0.13))")
s=s.replace("            if not P.inside(B,nx,ny,8): break\n            pts.append((nx,ny))\n        c=np.array((0.34,0.27,0.20),f32)",
            "            if not P.inside(B,nx,ny,8,2): break\n            pts.append((nx,ny))\n        c=np.array((0.34,0.27,0.20),f32)")
s=s.replace("        t=rng.uniform(0.12,0.7); i=max(1,int(t*(len(main)-1))); bx,by=main[i]",
            "        if len(main)<3: break\n        t=rng.uniform(0.12,0.7); i=max(1,int(t*(len(main)-1))); bx,by=main[i]")
s=s.replace("    for k in range(9):\n        x,y,a,d,tip=pts[rng.integers(0,len(pts))]","    for k in range(9 if pts else 0):\n        x,y,a,d,tip=pts[rng.integers(0,len(pts))]")
s=s.replace("    picks=rng.choice(len(pts),min(6,len(pts)),replace=False)","    picks=rng.choice(len(pts),min(6,len(pts)),replace=False) if pts else []")
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(s)
import time; t0=time.time()
P=paint_leaf_atlas(); t1=time.time()
save_leaf_atlas(P); print("paint",round(t1-t0,1),"save",round(time.time()-t1,1))
# ---- result ----
# {"result":"Code executed successfully: paint 2.0 save 2.0\n"}

# ==============================================================================================================
# [0214] 2026-09-23 10:53:46  blender  ok
# ==============================================================================================================
import bpy, numpy as np
im=bpy.data.images["T_VK_Leaves_BCA"]; W,H=im.size
a=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1]
# composite over a mid-grey checker so transparency is visible
yy,xx=np.mgrid[0:H,0:W]; chk=(((yy//64)+(xx//64))%2)*0.08+0.2
bg=np.stack([chk,chk,chk],-1)
out=a[...,:3]*a[...,3:4]+bg*(1-a[...,3:4])
out=out[::2,::2]
h,w=out.shape[:2]
img=bpy.data.images.new("_la",w,h,alpha=False); img.pixels.foreach_set(np.concatenate([out[::-1],np.ones((h,w,1),np.float32)],-1).astype(np.float32).ravel())
img.filepath_raw=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\_leafatlas.png"
img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0215] 2026-09-23 10:54:33  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_leafgen"]; s=t.as_string()
a=s.index("def cell_broad("); b=s.index("def cell_pine(")
new_broad='''def fan_twigs(P,B,rng,nt=5,spread=1.0,Lf=(0.42,0.58),w=6,stem=(0.30,0.21,0.12),maxd=2,leaf_step=20,kid_ang=(0.55,1.1),kid_len=(0.45,0.65),curl=0.1,droop=0.0):
    cx=(B[0]+B[2])/2; bot=B[3]-4; H=B[3]-B[1]; pts=[]
    for i in range(nt):
        f=(i/(nt-1)-0.5) if nt>1 else 0.0
        ang=-math.pi/2+f*2*spread+rng.uniform(-0.12,0.12)
        L=H*rng.uniform(*Lf)*(1-0.25*abs(f)*2)
        twig(P,B,rng,cx+rng.uniform(-8,8),bot,ang,L,w,stem,0,maxd,pts,leaf_step=leaf_step,nkids=2,curl=curl,kid_ang=kid_ang,kid_len=kid_len)
    return pts
def draw_leaves(P,B,rng,pts,pal,kind=0,Lr=(70,105),Wr=(0.28,0.36),ang_off=(0.5,1.1),droop=0.0):
    order=list(range(len(pts))); rng.shuffle(order)
    for j in order:
        x,y,a,d,tip=pts[j]
        for sd in ((0,) if tip else (-1,1)):
            aa=a+rng.uniform(-0.2,0.2) if sd==0 else a+sd*rng.uniform(*ang_off)
            if droop: aa=aa+(math.pi/2-aa)*droop*rng.uniform(0.5,1.0) if abs(((aa-math.pi/2)+math.pi)%(2*math.pi)-math.pi)<2.2 else aa
            L=rng.uniform(*Lr)*(0.85 if d>=2 else 1.0); W=L*rng.uniform(*Wr)
            col=np.array(pal[rng.integers(0,len(pal))],f32)*rng.uniform(0.88,1.12)
            P.leaf(B,x,y,aa,L,W,col,kind=kind,bend=rng.uniform(-0.1,0.1),side=sd or 1)
def cell_broad(P,name,rng,pal,kind=0,dens=1.0,Lr=(70,105),Wr=(0.28,0.36),stem=(0.30,0.21,0.12),maxd=2,nt=5,spread=1.0,Lf=(0.42,0.58)):
    B=cell_bounds(name)
    pts=fan_twigs(P,B,rng,nt=nt,spread=spread,Lf=Lf,stem=stem,maxd=maxd,leaf_step=22/dens)
    draw_leaves(P,B,rng,pts,pal,kind,Lr,Wr)
    return B,pts
'''
s=s[:a]+new_broad+s[b:]
# pine: fuller
s=s.replace("    for k in range(7):\n        if len(main)<3: break\n        t=rng.uniform(0.12,0.7); i=max(1,int(t*(len(main)-1))); bx,by=main[i]\n        sd=1 if k%2==0 else -1\n        br=spray(bx,by,-math.pi/2+sd*rng.uniform(0.55,0.9),rng.uniform(90,150)*(1-0.5*t),4,0)\n        needles(br,rng.uniform(30,40))\n    needles(main,rng.uniform(40,50))",
            "    for k in range(12):\n        if len(main)<3: break\n        t=0.08+0.72*k/11+rng.uniform(-0.03,0.03); i=max(1,int(t*(len(main)-1))); bx,by=main[i]\n        sd=1 if k%2==0 else -1\n        br=spray(bx,by,-math.pi/2+sd*rng.uniform(0.7,1.05),rng.uniform(170,230)*(1-0.6*t),5,0)\n        needles(br,rng.uniform(38,50))\n    needles(main,rng.uniform(48,60))")
# birch: airy drooping fan
s=s.replace('''    cell_broad(P,"birch",rng,birch,kind=2,dens=1.2,Lr=(40,56),Wr=(0.55,0.7),stem=(0.36,0.30,0.24),maxd=3,twigL=0.55)''',
'''    Bb=cell_bounds("birch")
    ptsb=fan_twigs(P,Bb,rng,nt=5,spread=1.15,Lf=(0.4,0.55),w=4,stem=(0.36,0.30,0.24),maxd=2,leaf_step=15,kid_ang=(0.7,1.3),kid_len=(0.5,0.75),curl=0.14)
    draw_leaves(P,Bb,rng,ptsb,birch,kind=0,Lr=(36,50),Wr=(0.45,0.58),ang_off=(0.7,1.3))''')
s=s.replace('''    cell_broad(P,"broadleaf",rng,broad,kind=0,dens=1.1)
    cell_broad(P,"broadleaf_dark",rng,dark,kind=0,dens=1.2)
    cell_broad(P,"autumn_orange",rng,aor,kind=1,dens=1.05,Wr=(0.34,0.42))
    cell_broad(P,"autumn_red",rng,ard,kind=1,dens=1.05,Wr=(0.34,0.42))''','''    cell_broad(P,"broadleaf",rng,broad,kind=0,dens=1.15)
    cell_broad(P,"broadleaf_dark",rng,dark,kind=0,dens=1.25)
    cell_broad(P,"autumn_orange",rng,aor,kind=1,dens=1.1,Wr=(0.36,0.44))
    cell_broad(P,"autumn_red",rng,ard,kind=1,dens=1.1,Wr=(0.36,0.44))''')
# blossom: fan + denser flowers
s=s.replace('''    pts=[]
    twig(P,B,rng,cx,bot,-math.pi/2+rng.uniform(-0.1,0.1),H*0.6,7,(0.30,0.19,0.13),0,2,pts,leaf_step=20)
    for (x,y,a,d,tip) in pts[::2]:''','''    pts=fan_twigs(P,B,rng,nt=5,spread=1.0,Lf=(0.42,0.58),w=6,stem=(0.30,0.19,0.13),maxd=2,leaf_step=18)
    for (x,y,a,d,tip) in pts[::2]:''')
s=s.replace("        for j in range(3 if tip else 1):\n            fx=x+rng.uniform(-24,24); fy=y+rng.uniform(-24,24)",
            "        for j in range(3 if tip else 2):\n            fx=x+rng.uniform(-24,24); fy=y+rng.uniform(-24,24)")
# dead twigs: bigger, bushier
s=s.replace("    rec(cx,B[3]-4,-math.pi/2,(B[3]-B[1])*0.5,10,0)",
            "    for a0 in (-math.pi/2-0.5,-math.pi/2,-math.pi/2+0.5):\n        rec(cx+rng.uniform(-10,10),B[3]-4,a0+rng.uniform(-0.1,0.1),(B[3]-B[1])*rng.uniform(0.45,0.6),11,0)")
s=s.replace("        if d<5 and len(pts)>2:\n            for kk in range(2 if d<2 else rng.integers(1,3)):",
            "        if d<5 and len(pts)>2:\n            for kk in range(2 if d<3 else rng.integers(1,3)):")
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(s)
P=paint_leaf_atlas(); save_leaf_atlas(P)
import numpy as np
im=bpy.data.images["T_VK_Leaves_BCA"]; W,H=im.size
a=np.array(im.pixels[:],np.float32).reshape(H,W,4)[::-1]
yy,xx=np.mgrid[0:H,0:W]; chk=(((yy//64)+(xx//64))%2)*0.08+0.2
out=a[...,:3]*a[...,3:4]+np.stack([chk,chk,chk],-1)*(1-a[...,3:4]); out=out[::2,::2]; h,w=out.shape[:2]
img=bpy.data.images.new("_la",w,h,alpha=False); img.pixels.foreach_set(np.concatenate([out[::-1],np.ones((h,w,1),np.float32)],-1).astype(np.float32).ravel())
img.filepath_raw=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\_leafatlas.png"
img.file_format="PNG"; img.save(); bpy.data.images.remove(img)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0216] 2026-09-23 10:55:53  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def leaf_material(name="M_VK_Leaves",atlas="T_VK_Leaves"):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); L=nt.links
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"
    tx=nt.nodes.new("ShaderNodeTexImage"); tx.image=bpy.data.images[atlas+"_BCA"]; L.new(uv.outputs[0],tx.inputs[0])
    th=nt.nodes.new("ShaderNodeTexImage"); th.image=bpy.data.images[atlas+"_H"]; th.image.colorspace_settings.name="Non-Color"; L.new(uv.outputs[0],th.inputs[0])
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    mx=nt.nodes.new("ShaderNodeMix"); mx.data_type="RGBA"; mx.blend_type="MULTIPLY"; mx.inputs[0].default_value=1
    L.new(tx.outputs["Color"],mx.inputs[6]); L.new(vc.outputs[0],mx.inputs[7]); L.new(mx.outputs[2],b.inputs["Base Color"])
    geo=nt.nodes.new("ShaderNodeNewGeometry")
    mul=nt.nodes.new("ShaderNodeMath"); mul.operation="MULTIPLY_ADD"; mul.inputs[1].default_value=-2; mul.inputs[2].default_value=1
    L.new(geo.outputs["Backfacing"],mul.inputs[0])
    sc=nt.nodes.new("ShaderNodeVectorMath"); sc.operation="SCALE"
    L.new(geo.outputs["Normal"],sc.inputs[0]); L.new(mul.outputs[0],sc.inputs["Scale"])
    bump=nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.35; bump.inputs["Distance"].default_value=0.02
    L.new(th.outputs["Color"],bump.inputs["Height"]); L.new(sc.outputs[0],bump.inputs["Normal"])
    L.new(bump.outputs[0],b.inputs["Normal"])
    b.inputs["Roughness"].default_value=0.62; b.inputs["Specular IOR Level"].default_value=0.25
    tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); L.new(mx.outputs[2],tr.inputs["Color"])
    neg=nt.nodes.new("ShaderNodeVectorMath"); neg.operation="SCALE"; neg.inputs["Scale"].default_value=-1
    L.new(bump.outputs[0],neg.inputs[0]); L.new(neg.outputs[0],tr.inputs["Normal"])
    ms=nt.nodes.new("ShaderNodeMixShader"); ms.inputs[0].default_value=0.28
    L.new(b.outputs[0],ms.inputs[1]); L.new(tr.outputs[0],ms.inputs[2])
    gt=nt.nodes.new("ShaderNodeMath"); gt.operation="GREATER_THAN"; gt.inputs[1].default_value=0.5
    L.new(tx.outputs["Alpha"],gt.inputs[0])
    tp=nt.nodes.new("ShaderNodeBsdfTransparent"); ms2=nt.nodes.new("ShaderNodeMixShader")
    L.new(gt.outputs[0],ms2.inputs[0]); L.new(tp.outputs[0],ms2.inputs[1]); L.new(ms.outputs[0],ms2.inputs[2]); L.new(ms2.outputs[0],o.inputs[0])
    m.use_backface_culling=False
    try: m.surface_render_method="DITHERED"
    except: pass
    return m
def mossy_material(name,base_prefix,moss_prefix="T_VK_Moss",base_tile=1.5,moss_tile=1.0,thresh=0.52,soft=0.14,noise_amt=0.5,nstr=1.1):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); L=nt.links
    o=nt.nodes.new("ShaderNodeOutputMaterial"); b=nt.nodes.new("ShaderNodeBsdfPrincipled")
    uv=nt.nodes.new("ShaderNodeUVMap"); uv.uv_map="UVMap"
    mp=nt.nodes.new("ShaderNodeMapping"); s_=base_tile/moss_tile; mp.inputs["Scale"].default_value=(s_,s_,1)
    L.new(uv.outputs[0],mp.inputs[0])
    def tex(img,src,data=False):
        n=nt.nodes.new("ShaderNodeTexImage"); n.image=bpy.data.images[img]
        if data: n.image.colorspace_settings.name="Non-Color"
        L.new(src,n.inputs[0]); return n
    bbc=tex(base_prefix+"_BC",uv.outputs[0]); bn=tex(base_prefix+"_N",uv.outputs[0],True); br=tex(base_prefix+"_R",uv.outputs[0],True)
    mbc=tex(moss_prefix+"_BC",mp.outputs[0]); mn=tex(moss_prefix+"_N",mp.outputs[0],True); mr=tex(moss_prefix+"_R",mp.outputs[0],True); mh=tex(moss_prefix+"_H",mp.outputs[0],True)
    geo=nt.nodes.new("ShaderNodeNewGeometry"); sep=nt.nodes.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"],sep.inputs[0])
    hh=nt.nodes.new("ShaderNodeMath"); hh.operation="MULTIPLY_ADD"; hh.inputs[1].default_value=noise_amt; hh.inputs[2].default_value=-0.5*noise_amt
    L.new(mh.outputs["Color"],hh.inputs[0])
    add=nt.nodes.new("ShaderNodeMath"); add.operation="ADD"; L.new(sep.outputs["Z"],add.inputs[0]); L.new(hh.outputs[0],add.inputs[1])
    mr_=nt.nodes.new("ShaderNodeMapRange"); mr_.interpolation_type="SMOOTHSTEP"
    mr_.inputs["From Min"].default_value=thresh-soft; mr_.inputs["From Max"].default_value=thresh+soft
    L.new(add.outputs[0],mr_.inputs["Value"])
    vc=nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name="Col"
    gate=nt.nodes.new("ShaderNodeMath"); gate.operation="MULTIPLY"; L.new(mr_.outputs["Result"],gate.inputs[0]); L.new(vc.outputs["Alpha"],gate.inputs[1])
    def mix(a,bb_,dtype="RGBA"):
        n=nt.nodes.new("ShaderNodeMix"); n.data_type=dtype; L.new(gate.outputs[0],n.inputs[0])
        if dtype=="RGBA": L.new(a,n.inputs[6]); L.new(bb_,n.inputs[7]); return n.outputs[2]
        L.new(a,n.inputs[2]); L.new(bb_,n.inputs[3]); return n.outputs[0]
    col=mix(bbc.outputs[0],mbc.outputs[0])
    mv=nt.nodes.new("ShaderNodeMix"); mv.data_type="RGBA"; mv.blend_type="MULTIPLY"; mv.inputs[0].default_value=1
    L.new(col,mv.inputs[6]); L.new(vc.outputs[0],mv.inputs[7]); L.new(mv.outputs[2],b.inputs["Base Color"])
    rough=mix(br.outputs[0],mr.outputs[0]); L.new(rough,b.inputs["Roughness"])
    ncol=mix(bn.outputs[0],mn.outputs[0])
    nm=nt.nodes.new("ShaderNodeNormalMap"); nm.uv_map="UVMap"; nm.inputs["Strength"].default_value=nstr
    L.new(ncol,nm.inputs["Color"]); L.new(nm.outputs[0],b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value=0.2
    L.new(b.outputs[0],o.inputs[0])
    return m
def nature_materials():
    for mn,prefix,kw in (("M_VK_BarkOak","T_VK_BarkOak",dict(nstr=1.2,spec=0.15)),("M_VK_BarkBirch","T_VK_BarkBirch",dict(nstr=1.0,spec=0.2)),
                         ("M_VK_BarkPine","T_VK_BarkPine",dict(nstr=1.25,spec=0.15)),("M_VK_Moss","T_VK_Moss",dict(nstr=1.0,spec=0.1)),
                         ("M_VK_EndGrain","T_VK_EndGrain",dict(nstr=0.8,spec=0.15))):
        m=bpy.data.materials.get(mn) or bpy.data.materials.new(mn); pbr_material(m,prefix,**kw); MAT_MAP[mn]=dict(prefix=prefix,**kw)
    leaf_material()
    mossy_material("M_VK_RockMossy","T_VK_Rock",base_tile=1.5)
    mossy_material("M_VK_BarkMossy","T_VK_BarkOak",base_tile=1.2,thresh=0.45)
'''
t=bpy.data.texts["vk_mat"]; t.write(code)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(bpy.data.texts["vk_leafgen"].as_string())
# save leaf height map (needed for the bump)
P=paint_leaf_atlas(); save_leaf_atlas(P); write_map("T_VK_Leaves_H",blur(P.h,0.8),True)
exec(t.as_string())
nature_materials()
# extend kit material list
h=bpy.data.texts["vk_helpers"]; s=h.as_string()
old='''bpy.data.materials["M_VK_Foliage"], bpy.data.materials["M_VK_Crops"]]'''
assert old in s
s=s.replace(old,'''bpy.data.materials["M_VK_Foliage"], bpy.data.materials["M_VK_Crops"],
            bpy.data.materials["M_VK_BarkOak"], bpy.data.materials["M_VK_BarkBirch"], bpy.data.materials["M_VK_BarkPine"],
            bpy.data.materials["M_VK_Leaves"], bpy.data.materials["M_VK_Moss"], bpy.data.materials["M_VK_RockMossy"], bpy.data.materials["M_VK_BarkMossy"],
            bpy.data.materials["M_VK_EndGrain"], tex_mat("M_VK_MushRed",None,0.45,flat=(0.74,0.07,0.05)), tex_mat("M_VK_MushBrown",None,0.6,flat=(0.52,0.31,0.15)),
            tex_mat("M_VK_MushStem",None,0.7,flat=(0.93,0.89,0.78)), tex_mat("M_VK_MushGlow",None,0.4,flat=(0.35,0.85,1.0),emit=(0.25,0.8,1.0))]''')
s=s.replace("THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE,CROPS=range(33)",
            "THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE,CROPS,BARK_OAK,BARK_BIRCH,BARK_PINE,LEAVES,MOSS,ROCK_MOSSY,BARK_MOSSY,ENDGRAIN,MUSH_RED,MUSH_BROWN,MUSH_STEM,MUSH_GLOW=range(45)")
s=s.replace("TILE={0:3.0,1:2.2,","TILE={33:1.2,34:1.0,35:1.4,37:1.0,38:1.5,39:1.2,40:0.6,0:3.0,1:2.2,")
h.clear(); h.write(s); exec(s)
mm=kit_mats(); print(len(mm), mm[BARK_OAK].name, mm[LEAVES].name, mm[MUSH_GLOW].name)
b=next(n for n in bpy.data.materials["M_VK_MushGlow"].node_tree.nodes if n.type=="BSDF_PRINCIPLED"); b.inputs["Emission Strength"].default_value=5.0
# ---- result ----
# {"result":"Code executed successfully: 45 M_VK_BarkOak M_VK_Leaves M_VK_MushGlow\n"}

# ==============================================================================================================
# [0217] 2026-09-23 10:58:06  blender  ERROR
# ==============================================================================================================
import bpy
code = r'''
# =====================  NATURE KIT  =====================
LEAF_CELLS=["broadleaf","broadleaf_dark","autumn_orange","autumn_red","birch","pine","willow","fern",
            "berry","blossom","apple","hydrangea","reeds","tallgrass","wildflowers","deadtwigs"]
UP=Vector((0,0,1)); GOLD=2.39996
def leaf_uv(cell,m=0.004):
    i=LEAF_CELLS.index(cell); cx=i%4; cy=i//4
    return cx*0.25+m,(cx+1)*0.25-m,1-(cy+1)*0.25+m,1-cy*0.25-m
class NK(Kit):
    def __init__(s):
        Kit.__init__(s); s.nfn={}; s.vinfo={}; s.wind_fn=None; s.ao_fn=None
    def lcard(s,base,right,up,w,h,cell,flip=False,bend=0.0,arch=0.0,rows=2,cols=2,nfn=None,aofn=None,anchor="bottom"):
        u0,u1,v0,v1=leaf_uv(cell)
        if flip: u0,u1=u1,u0
        B=Vector(base); R=Vector(right).normalized(); U=Vector(up).normalized(); N=R.cross(U).normalized()
        if anchor=="top": B=B-U*h
        elif anchor=="center": B=B-U*h*0.5
        vs=[];uvs=[]
        for j in range(rows+1):
            for i in range(cols+1):
                a=i/cols; t=j/rows
                p=B+R*(a-0.5)*w+U*t*h+N*(bend*w*(1-(2*a-1)**2)+arch*h*t*t)
                v=s.bm.verts.new(p); vs.append(v); uvs.append((u0+(u1-u0)*a,v0+(v1-v0)*t))
        for j in range(rows):
            for i in range(cols):
                a=j*(cols+1)+i; q=(a,a+1,a+cols+2,a+cols+1)
                f=s.bm.faces.new([vs[x] for x in q]); f.material_index=LEAVES; f.smooth=True
                for l,x in zip(f.loops,q): l[s.uv].uv=uvs[x]
        for v in vs:
            if nfn: s.nfn[v]=nfn
            if aofn: s.vinfo[v]=aofn
        return vs
    def tube(s,pts,radii,segs,mi,tileU=1.2,tileV=1.2,flare=None,cap_end=True,cap_start=False,noise_amp=0.04,seed=0.0):
        n=len(pts)
        tans=[(pts[min(i+1,n-1)]-pts[max(i-1,0)]).normalized() for i in range(n)]
        nrm=tans[0].cross(Vector((0,0,1)) if abs(tans[0].z)<0.95 else Vector((1,0,0))).normalized(); fr=[]
        for i,t in enumerate(tans):
            if i>0: nrm=(tans[i-1].rotation_difference(t)@nrm).normalized()
            nrm=(nrm-t*nrm.dot(t)).normalized(); fr.append((t,nrm,t.cross(nrm)))
        avg=sum(radii)/len(radii); urep=max(1,round(2*math.pi*avg/tileU))
        rings=[]; vco=0.0
        for i,(p,r) in enumerate(zip(pts,radii)):
            if i>0: vco+=(pts[i]-pts[i-1]).length/tileV
            t,nn,bn=fr[i]; ring=[]
            for k in range(segs+1):
                th=2*math.pi*k/segs; kk=k%segs
                rr=r*(1+noise_amp*noise.noise(Vector((math.cos(th)*1.3,math.sin(th)*1.3,p.z*1.1+seed))))
                if flare: rr*=flare(th,p)
                if k<segs: ring.append(s.bm.verts.new(p+(nn*math.cos(th)+bn*math.sin(th))*rr))
            rings.append((ring,vco))
        for i in range(n-1):
            ra,va=rings[i]; rb,vb=rings[i+1]
            for k in range(segs):
                k2=(k+1)%segs
                f=s.bm.faces.new((ra[k],ra[k2],rb[k2],rb[k])); f.material_index=mi; f.smooth=True
                for l,uu,vv in zip(f.loops,(k/segs*urep,(k+1)/segs*urep,(k+1)/segs*urep,k/segs*urep),(va,va,vb,vb)): l[s.uv].uv=(uu,vv)
        def cap(ring,v,c,flip_):
            cv=s.bm.verts.new(c)
            for k in range(segs):
                q=(ring[k],ring[(k+1)%segs],cv) if not flip_ else (ring[(k+1)%segs],ring[k],cv)
                f=s.bm.faces.new(q); f.material_index=mi; f.smooth=True
                for l,(a,b_) in zip(f.loops,((0,v),(0.2,v),(0.1,v+0.06))): l[s.uv].uv=(a,b_)
        if cap_end: cap(rings[-1][0],rings[-1][1],pts[-1]+fr[-1][0]*radii[-1]*0.6,False)
        if cap_start: cap(rings[0][0],0.0,pts[0]-fr[0][0]*radii[0]*0.3,True)
        return rings
def grow(start,d,length,r0,r1,depth,rng,up=0.1,droop=0.0,wig=0.1,step=0.3,taper=0.8,seed=0.0):
    n=max(3,int(math.ceil(length/step))); p=Vector(start); d=Vector(d).normalized(); pts=[p.copy()]; rad=[r0]
    for i in range(1,n+1):
        t=i/n
        w=Vector((noise.noise(p*0.9+Vector((seed,depth*3.1,0.0))),noise.noise(p*0.9+Vector((0.0,seed+7.7,depth))),noise.noise(p*0.9+Vector((2.2,0.0,seed+5.0)))))
        d=(d+UP*up-UP*(droop*t)+w*wig).normalized()
        p=p+d*(length/n); pts.append(p.copy()); rad.append(r0+(r1-r0)*(t**taper))
    return {"pts":pts,"rad":rad,"depth":depth}
def point_at(b,t):
    P=b["pts"]; f=t*(len(P)-1); i=min(int(f),len(P)-2); a=f-i
    return P[i].lerp(P[i+1],a), b["rad"][i]*(1-a)+b["rad"][i+1]*a, (P[i+1]-P[i]).normalized()
def child_dir(tan,angle,azim):
    perp=tan.cross(Vector((0.3,0.2,1)) if abs(tan.z)<0.9 else Vector((1,0,0))).normalized()
    perp=Quaternion(tan,azim)@perp
    return (Quaternion(perp,angle)@tan).normalized()
def root_flare(n_lobes=5,amount=0.8,height=0.45,base=0.25,phase=0.7):
    def f(th,p):
        e=math.exp(-max(p.z,0.0)/height)
        return 1+e*(base+amount*max(0.0,math.cos(n_lobes*th+phase))**3)
    return f
def canopy_fns(C,ext,clump=None,wc=0.35,ao_lo=0.46):
    def nfn(p):
        d=p-C; n=Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z))
        n=n.normalized() if n.length>1e-6 else Vector((0,0,1))
        if clump is not None:
            c=p-clump
            if c.length>1e-6: n=(n*(1-wc)+c.normalized()*wc).normalized()
        return n
    def aofn(p):
        d=p-C; q=Vector((d.x/ext.x,d.y/ext.y,d.z/ext.z)); outer=min(1.0,q.length)
        up=0.5+0.5*(q.normalized().z if q.length>1e-6 else 0.0)
        g=ao_lo+(1-ao_lo)*min(1.0,0.55*up+0.45*outer**1.5)
        return g,min(1.0,0.35+0.65*outer)
    return nfn,aofn
def clump_cards(k,c,r,n,cells,rng,C,ext,size=(0.9,1.3),shell=(0.3,0.85),wc=0.35,ao_lo=0.46):
    names=[x[0] for x in cells]; wts=[x[1] for x in cells]
    nfn,aofn=canopy_fns(C,ext,c,wc,ao_lo)
    for i in range(n):
        zf=1-2*(i+0.5)/n; az=i*GOLD+rng.uniform(-0.3,0.3); s_=math.sqrt(max(0.0,1-zf*zf))
        d=Vector((s_*math.cos(az),s_*math.sin(az),zf))
        if d.z<-0.65 and rng.random()<0.6: continue
        base=c+d*r*rng.uniform(*shell)
        up=(d+Vector((rng.uniform(-.35,.35),rng.uniform(-.35,.35),rng.uniform(-0.1,0.4)))).normalized()
        right=up.cross(Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1))).normalized())
        if right.length<1e-3: right=up.cross(Vector((1,0,0)))
        sz=rng.uniform(*size); cell=rng.choices(names,wts)[0]
        k.lcard(base,right.normalized(),up,sz*0.95,sz,cell,flip=rng.random()<0.5,bend=0.08,nfn=nfn,aofn=aofn)
def nk_finish(k,name,coll,sharp=None,bark_ao=(0.62,0.8),moss_alpha=1.0,wind_H=8.0):
    bm=k.bm; bm.normal_update()
    for f in bm.faces:
        for l in f.loops:
            v=l.vert
            if v in k.vinfo:
                g,wa=k.vinfo[v](v.co)
            else:
                z=v.co.z
                g=bark_ao[0]+(1-bark_ao[0])*min(1.0,max(0.0,z)/bark_ao[1]) if bark_ao else 1.0
                rr=math.hypot(v.co.x,v.co.y)
                wa=moss_alpha if k.wind_fn is None else k.wind_fn(v.co)
            l[k.cl]=(g,g*0.98,g*0.95,wa)
    if sharp is not None:
        for e in bm.edges:
            if len(e.link_faces)==2 and e.calc_face_angle(0.0)>sharp: e.smooth=False
    for f in bm.faces: f.smooth=True
    bm.verts.index_update()
    normals=[None]*len(bm.verts)
    for v,fn in k.nfn.items(): normals[v.index]=fn(v.co)
    me=bpy.data.meshes.new(name+"__new"); bm.to_mesh(me); bm.free()
    allm=kit_mats(); used=sorted({p.material_index for p in me.polygons})
    remap={u:i for i,u in enumerate(used)}
    for p in me.polygons: p.material_index=remap[p.material_index]
    for u in used: me.materials.append(allm[u])
    if any(n is not None for n in normals):
        vn=[tuple(n) if n is not None else tuple(me.vertices[i].normal) for i,n in enumerate(normals)]
        me.normals_split_custom_set_from_vertices(vn)
    obj=bpy.data.objects.get(name)
    if obj is not None and obj.type=="MESH":
        old=obj.data; old.user_remap(me)
        if old.users==0: bpy.data.meshes.remove(old)
    else:
        obj=bpy.data.objects.new(name,me); coll.objects.link(obj)
    me.name=name
    obj.hide_render=True; obj.hide_viewport=True; obj["kit"]="VillageNature"
    return obj
def tree_wind(H,axis=(0.0,0.0)):
    def w(p):
        r=math.hypot(p.x-axis[0],p.y-axis[1])
        return min(1.0,max(0.0,(p.z/H)*0.25+(r/3.0)**1.5*0.6))
    return w
def bark_tubes(k,branches,mi,segs=(14,9,6,4),flare=None,tile=1.2):
    for b in branches:
        d=b["depth"]; sg=segs[min(d,len(segs)-1)]
        k.tube(b["pts"],b["rad"],sg,mi,tileU=tile,tileV=tile,flare=flare if d==0 else None,cap_end=True,noise_amp=0.05 if d<2 else 0.02,seed=len(b["pts"])*0.37)
def canopy_bounds(clumps):
    C=sum((c for c,r in clumps),Vector())/len(clumps)
    ext=Vector((max(abs(c.x-C.x)+r for c,r in clumps),max(abs(c.y-C.y)+r for c,r in clumps),max(abs(c.z-C.z)+r for c,r in clumps)))
    return C,ext
# ---------------- skeletons ----------------
def sk_broad(seed,trunkH=3.2,spread=1.0,nl=(3,4),limb_len=(2.6,3.4),limb_ang=(35,55),sub_len=(1.2,1.9),r0=0.48,wig=0.12,lower=True):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.4),(rng.uniform(-0.08,0.08),rng.uniform(-0.08,0.08),1),trunkH,r0,r0*0.66,0,rng,up=0.03,wig=0.06,step=0.3,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(*nl)
    for kk in range(n):
        az=kk*2*math.pi/n+rng.uniform(-0.3,0.3); d=child_dir(tt,math.radians(rng.uniform(*limb_ang)),az)
        limbs.append(grow(tp-tt*0.3,d,rng.uniform(*limb_len)*spread,tr*0.72,0.07,1,rng,up=0.07,wig=wig,step=0.3,seed=seed+kk))
    if lower:
        p,r,tan=point_at(trunk,0.66); limbs.append(grow(p,child_dir(tan,math.radians(62),rng.uniform(0,6.28)),limb_len[0]*0.85*spread,r*0.5,0.06,1,rng,up=0.1,wig=wig,seed=seed+9))
    B+=limbs; subs=[]
    for li,L in enumerate(limbs):
        for kk in range(3):
            t=0.4+0.55*(kk+rng.random()*0.5)/3; p,r,tan=point_at(L,min(t,0.95))
            d=child_dir(tan,math.radians(rng.uniform(35,60)),li*1.7+kk*GOLD)
            if d.z<-0.1: d.z=-0.1; d.normalize()
            subs.append(grow(p,d,rng.uniform(*sub_len)*spread,r*0.7,0.035,2,rng,up=0.08,wig=wig*1.2,step=0.25,seed=seed+20+li*5+kk))
    B+=subs
    return B,limbs,subs
def broad_clumps(limbs,subs,rng,scale=1.0):
    cl=[]
    for b in subs:
        cl.append((b["pts"][-1],rng.uniform(0.95,1.25)*scale)); cl.append((point_at(b,0.5)[0]+Vector((0,0,0.2)),rng.uniform(0.8,1.0)*scale))
    for b in limbs: cl.append((b["pts"][-1]+Vector((0,0,0.2)),rng.uniform(1.1,1.35)*scale))
    out=[]
    for c in cl:
        if all((c[0]-o[0]).length>0.33*(c[1]+o[1]) for o in out): out.append(c)
    return out
def make_broad_tree(k,seed,cells,bark=BARK_OAK,trunkH=3.2,spread=1.0,cards=26,size=(0.95,1.35),clump_scale=1.0,**kw):
    B,limbs,subs=sk_broad(seed,trunkH=trunkH,spread=spread,**kw)
    rng=random.Random(seed+1)
    H=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(H+1.5)
    bark_tubes(k,B,bark,flare=root_flare())
    cl=broad_clumps(limbs,subs,rng,clump_scale); C,ext=canopy_bounds(cl)
    for (c,r) in cl: clump_cards(k,c,r,cards,cells,rng,C,ext,size=size)
    return B
'''
t=bpy.data.texts.get("vk_nature") or bpy.data.texts.new("vk_nature"); t.clear(); t.write(code)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(code)
NC=vcol("VK_NaturePieces")
k=NK(); make_broad_tree(k,11,[("broadleaf",0.6),("broadleaf_dark",0.4)])
o=nk_finish(k,"SM_VK_Tree_Oak_A",NC)
print(len(o.data.polygons),[m.name for m in o.data.materials])
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: name 'Quaternion' is not defined"}

# ==============================================================================================================
# [0218] 2026-09-23 10:58:20  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_nature"]; s=t.as_string()
s="from mathutils import Quaternion\n"+s
t.clear(); t.write(s)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(s)
NC=vcol("VK_NaturePieces")
k=NK(); make_broad_tree(k,11,[("broadleaf",0.6),("broadleaf_dark",0.4)])
o=nk_finish(k,"SM_VK_Tree_Oak_A",NC)
print(len(o.data.polygons),[m.name for m in o.data.materials])
# staging area for nature at x=600
S=vcol("VK_NatureTest")
for ob in list(S.objects): bpy.data.objects.remove(ob)
inst=bpy.data.objects.new("test_oak",o.data); S.objects.link(inst); inst.location=(600,0,0)
SC=bpy.data.scenes["VillageKit"]
cd=bpy.data.cameras.get("VK_CamNature") or bpy.data.cameras.new("VK_CamNature"); cd.lens=35; cd.clip_end=600
cn=bpy.data.objects.get("VK_CameraNature") or bpy.data.objects.new("VK_CameraNature",cd)
if cn.name not in SC.collection.objects: SC.collection.objects.link(cn)
tgt=Vector((600,0,3.6)); cn.location=tgt+Vector((7,-12,0.5))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
for c in ("VK_Town","VK_Catalog"):
    for ob in bpy.data.collections[c].objects: ob.hide_render=True
g=bpy.data.objects["VK_Ground"]; g.location=(600,0,0); g.scale=(3,3,1)
SC.camera=cn; SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=50
import os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_nat1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 3255 ['M_VK_BarkOak', 'M_VK_Leaves']\n"}

# ==============================================================================================================
# [0219] 2026-09-23 10:59:06  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_leafgen"]; s=t.as_string()
s=s.replace("    broad=[(0.20,0.42,0.10),(0.27,0.49,0.12),(0.34,0.56,0.15),(0.16,0.36,0.08),(0.40,0.60,0.18)]",
            "    broad=[(0.26,0.53,0.12),(0.34,0.61,0.15),(0.43,0.68,0.19),(0.21,0.46,0.10),(0.50,0.72,0.22)]")
s=s.replace("    dark=[(0.10,0.26,0.07),(0.14,0.32,0.09),(0.18,0.36,0.11),(0.08,0.22,0.08)]",
            "    dark=[(0.14,0.35,0.10),(0.19,0.42,0.12),(0.24,0.46,0.14),(0.12,0.30,0.10)]")
s=s.replace("    birch=[(0.45,0.62,0.16),(0.55,0.68,0.20),(0.38,0.55,0.12),(0.62,0.72,0.26)]",
            "    birch=[(0.52,0.70,0.18),(0.62,0.76,0.23),(0.44,0.63,0.14),(0.70,0.80,0.30)]")
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(s)
P=paint_leaf_atlas(); save_leaf_atlas(P); write_map("T_VK_Leaves_H",blur(P.h,0.8),True)
m=bpy.data.materials["M_VK_Leaves"]
for n in m.node_tree.nodes:
    if n.type=="BUMP": n.inputs["Strength"].default_value=0.25
    if n.type=="MIX_SHADER" and abs(n.inputs[0].default_value-0.28)<1e-3: n.inputs[0].default_value=0.32
exec(bpy.data.texts["vk_helpers"].as_string()); exec(bpy.data.texts["vk_nature"].as_string())
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace("def canopy_fns(C,ext,clump=None,wc=0.35,ao_lo=0.46):","def canopy_fns(C,ext,clump=None,wc=0.35,ao_lo=0.56):")
ns=ns.replace("def clump_cards(k,c,r,n,cells,rng,C,ext,size=(0.9,1.3),shell=(0.3,0.85),wc=0.35,ao_lo=0.46):","def clump_cards(k,c,r,n,cells,rng,C,ext,size=(0.9,1.3),shell=(0.15,0.85),wc=0.35,ao_lo=0.56):")
ns=ns.replace("def make_broad_tree(k,seed,cells,bark=BARK_OAK,trunkH=3.2,spread=1.0,cards=26,size=(0.95,1.35),clump_scale=1.0,**kw):",
              "def make_broad_tree(k,seed,cells,bark=BARK_OAK,trunkH=3.2,spread=1.0,cards=36,size=(1.0,1.45),clump_scale=1.0,**kw):")
tn.clear(); tn.write(ns); exec(ns)
NC=vcol("VK_NaturePieces")
k=NK(); make_broad_tree(k,11,[("broadleaf",0.72),("broadleaf_dark",0.28)])
o=nk_finish(k,"SM_VK_Tree_Oak_A",NC); print(len(o.data.polygons))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.camera=bpy.data.objects["VK_CameraNature"]
SC.render.filepath=os.path.join(out,"_nat1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 4075\n"}

# ==============================================================================================================
# [0220] 2026-09-23 10:59:32  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
S=bpy.data.collections["VK_NatureTest"]
for nm,d in (("test_heroW","SM_Tree_Wood"),("test_heroF","SM_Tree_Foliage")):
    ob=bpy.data.objects.get(nm) or bpy.data.objects.new(nm,bpy.data.objects[d].data)
    if ob.name not in S.objects: S.objects.link(ob)
    ob.location=(609,0,0)
SC=bpy.data.scenes["VillageKit"]
cn=bpy.data.objects["VK_CameraNature"]
tgt=Vector((604.5,0,3.8)); cn.location=tgt+Vector((6,-20,0.8)); cn.data.lens=35
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_nat2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# report material setups
for mn in ("M_Tree_Leaves","M_VK_Leaves"):
    m=bpy.data.materials[mn]; print(mn,[n.type for n in m.node_tree.nodes])
me=bpy.data.objects["SM_Tree_Foliage"].data
print("hero foliage mats",[m.name for m in me.materials], "polys",len(me.polygons))
# ---- result ----
# {"result":"Code executed successfully: M_Tree_Leaves ['OUTPUT_MATERIAL', 'BSDF_PRINCIPLED', 'TEX_IMAGE', 'VERTEX_COLOR', 'MIX', 'MATH', 'BSDF_TRANSLUC
# ENT', 'MIX_SHADER', 'BSDF_TRANSPARENT', 'MIX_SHADER', 'NEW_GEOMETRY', 'MATH', 'VECT_MATH', 'VECT_MATH']\nM_VK_Leaves ['OUTPUT_MATERIAL', 'BSDF_PRINCIP
# LED', 'UVMAP', 'TEX_IMAGE', 'TEX_IMAGE', 'VERTEX_COLOR', 'MIX', 'NEW_GEOMETRY', 'MATH', 'VECT_MATH', 'BUMP', 'BSDF_TRANSLUCENT', 'VECT_MATH', 'MIX_SHA
# DER', 'MATH', 'BSDF_TRANSPARENT', 'MIX_SHADER']\nhero foliage mats ['M_Tree_Canopy', 'M_Tree_Leaves'] polys 1920\n"}

# ==============================================================================================================
# [0221] 2026-09-23 11:00:05  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_leafgen"]; s=t.as_string()
old='''    cell_broad(P,"broadleaf",rng,broad,kind=0,dens=1.15)
    cell_broad(P,"broadleaf_dark",rng,dark,kind=0,dens=1.25)
    cell_broad(P,"autumn_orange",rng,aor,kind=1,dens=1.1,Wr=(0.36,0.44))
    cell_broad(P,"autumn_red",rng,ard,kind=1,dens=1.1,Wr=(0.36,0.44))'''
assert old in s
s=s.replace(old,'''    cell_broad(P,"broadleaf",rng,broad,kind=0,dens=0.72,Lr=(95,135),nt=3,spread=0.75,Lf=(0.5,0.7))
    cell_broad(P,"broadleaf_dark",rng,dark,kind=0,dens=0.95,Lr=(85,120),nt=4,spread=0.9)
    cell_broad(P,"autumn_orange",rng,aor,kind=1,dens=0.75,Lr=(95,130),Wr=(0.36,0.44),nt=3,spread=0.75,Lf=(0.5,0.7))
    cell_broad(P,"autumn_red",rng,ard,kind=1,dens=0.75,Lr=(95,130),Wr=(0.36,0.44),nt=3,spread=0.75,Lf=(0.5,0.7))''')
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(s)
P=paint_leaf_atlas(); save_leaf_atlas(P); write_map("T_VK_Leaves_H",blur(P.h,0.8),True)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(bpy.data.texts["vk_nature"].as_string())
NC=vcol("VK_NaturePieces")
k=NK(); make_broad_tree(k,11,[("broadleaf",0.75),("broadleaf_dark",0.25)],cards=40,size=(1.05,1.5))
o=nk_finish(k,"SM_VK_Tree_Oak_A",NC); print(len(o.data.polygons))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_nat2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 4355\n"}

# ==============================================================================================================
# [0222] 2026-09-23 11:00:41  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def make_pine(k,seed,H=10.0,Rmax_f=0.30,cards_step=0.32,size=(1.0,1.35),young=False):
    rng=random.Random(seed)
    trunk=grow((0,0,-0.3),(rng.uniform(-0.03,0.03),rng.uniform(-0.03,0.03),1),H,0.34*H/10,0.03,0,rng,up=0.02,wig=0.03,step=0.4,taper=1.0,seed=seed)
    B=[trunk]; Rmax=H*Rmax_f
    z=1.6 if not young else 0.5
    whorl=0
    while z<H-0.7:
        t=(z+0.3)/(H+0.3); p,r,tan=point_at(trunk,min(0.98,t))
        nb=rng.randint(5,6); az0=rng.uniform(0,6.28)
        for j in range(nb):
            az=az0+j*2*math.pi/nb+rng.uniform(-0.25,0.25)
            frac=(H-z)/H
            L=(Rmax*frac**0.9+0.35)*rng.uniform(0.85,1.1)
            dz=-0.28+0.45*(z/H)
            d=Vector((math.cos(az),math.sin(az),dz)).normalized()
            B.append(grow(p,d,L,max(0.03,r*0.45),0.015,1,rng,up=0.0,droop=0.22*(1-z/H)+0.05,wig=0.05,step=0.3,seed=seed+whorl*10+j))
        whorl+=1; z+=rng.uniform(0.5,0.72)*(1 if not young else 0.7)
    top=max(p.z for p in trunk["pts"])
    k.wind_fn=tree_wind(H+1)
    bark_tubes(k,B,BARK_PINE,segs=(12,6,5,4),flare=root_flare(6,0.45,0.35,0.18),tile=1.4)
    axis=Vector((0,0,0))
    def nfn(p):
        rad=Vector((p.x,p.y,0)); R=max(0.2,Rmax*max(0.05,(H-p.z)/H)+0.4)
        n=rad/R*0.9+Vector((0,0,0.45+0.5*(p.z/H)))
        return n.normalized() if n.length>1e-6 else Vector((0,0,1))
    def aofn(p):
        rad=math.hypot(p.x,p.y); R=max(0.2,Rmax*max(0.05,(H-p.z)/H)+0.4)
        g=0.5+0.5*min(1.0,0.45*min(1.0,rad/R)+0.55*(p.z/H)+0.15)
        return g,min(1.0,0.3+0.7*min(1.0,rad/R))
    for b in B[1:]:
        P=b["pts"]; Lb=sum((P[i+1]-P[i]).length for i in range(len(P)-1))
        n=max(2,int(Lb/cards_step))
        for i in range(n):
            tt=0.12+0.88*i/max(1,n-1)
            p,r,tan=point_at(b,min(tt,0.999))
            side=Vector((-tan.y,tan.x,0)).normalized() if abs(tan.z)<0.99 else Vector((1,0,0))
            sz=rng.uniform(*size)*(1-0.35*tt)*(0.7 if young else 1.0)
            for roll in (rng.uniform(0.25,0.5),-rng.uniform(0.25,0.5)):
                R=Quaternion(tan,roll)@side
                k.lcard(p-tan*0.05,R,tan,sz*0.9,sz,"pine",flip=rng.random()<0.5,bend=0.1,nfn=nfn,aofn=aofn)
    # leader + crown
    tip=trunk["pts"][-1]
    for j in range(5):
        a=j*2*math.pi/5+rng.uniform(-0.2,0.2); up=Vector((math.cos(a)*0.35,math.sin(a)*0.35,1)).normalized()
        right=Vector((-math.sin(a),math.cos(a),0))
        k.lcard(tip-Vector((0,0,1.2)),right,up,0.9,1.5,"pine",flip=j%2==0,bend=0.1,nfn=nfn,aofn=aofn)
    for j in range(8):
        zc=top-0.4-j*0.3; a=j*GOLD
        d=Vector((math.cos(a),math.sin(a),0.5)).normalized(); right=Vector((-math.sin(a),math.cos(a),0))
        k.lcard(Vector((0,0,zc)),right,d,0.8,1.1,"pine",flip=j%2==0,bend=0.1,nfn=nfn,aofn=aofn)
    return B
'''
t=bpy.data.texts["vk_nature"]; t.write(code)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(t.as_string())
NC=vcol("VK_NaturePieces")
k=NK(); make_pine(k,21,H=10.0); o=nk_finish(k,"SM_VK_Tree_Pine_A",NC); print("pine",len(o.data.polygons))
S=bpy.data.collections["VK_NatureTest"]
for nm in ("test_heroW","test_heroF"):
    ob=bpy.data.objects.get(nm)
    if ob: bpy.data.objects.remove(ob)
ob=bpy.data.objects.get("test_pine") or bpy.data.objects.new("test_pine",o.data)
if ob.name not in S.objects: S.objects.link(ob)
ob.location=(609,0,0)
import os
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
tgt=Vector((604.5,0,4.8)); cn.location=tgt+Vector((6,-22,0.3))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_nat3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: pine 6890\n"}

# ==============================================================================================================
# [0223] 2026-09-23 11:01:18  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_leafgen"]; s=t.as_string()
s=s.replace("    dark=np.array((0.08,0.24,0.16),f32); tipc=np.array((0.22,0.44,0.26),f32)",
            "    dark=np.array((0.12,0.34,0.22),f32); tipc=np.array((0.32,0.58,0.34),f32)")
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(s)
P=paint_leaf_atlas(); save_leaf_atlas(P); write_map("T_VK_Leaves_H",blur(P.h,0.8),True)
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
a=ns.index("def make_pine("); b=ns.find("\ndef ",a+10)
b=len(ns) if b==-1 else b
new_pine='''def make_pine(k,seed,H=10.0,Rmax_f=0.30,cards_step=0.42,size=(1.35,1.85),young=False):
    rng=random.Random(seed)
    trunk=grow((0,0,-0.3),(rng.uniform(-0.03,0.03),rng.uniform(-0.03,0.03),1),H,0.34*H/10,0.03,0,rng,up=0.02,wig=0.03,step=0.4,taper=1.0,seed=seed)
    B=[trunk]; Rmax=H*Rmax_f
    z=(1.5 if not young else 0.45)*H/10
    whorl=0
    while z<H-0.6:
        t=(z+0.3)/(H+0.3); p,r,tan=point_at(trunk,min(0.98,t))
        nb=rng.randint(6,8); az0=rng.uniform(0,6.28)
        for j in range(nb):
            az=az0+j*2*math.pi/nb+rng.uniform(-0.2,0.2)
            frac=(H-z)/H
            L=(Rmax*frac**0.85+0.4)*rng.uniform(0.85,1.1)
            dz=-0.38+0.5*(z/H)
            d=Vector((math.cos(az),math.sin(az),dz)).normalized()
            B.append(grow(p,d,L,max(0.03,r*0.45),0.015,1,rng,up=0.09,droop=0.05,wig=0.05,step=0.3,seed=seed+whorl*10+j))
        whorl+=1; z+=rng.uniform(0.42,0.58)*H/10
    top=max(p.z for p in trunk["pts"])
    k.wind_fn=tree_wind(H+1)
    bark_tubes(k,B,BARK_PINE,segs=(12,5,4,4),flare=root_flare(6,0.45,0.35,0.18),tile=1.4)
    def nfn(p):
        rad=Vector((p.x,p.y,0)); R=max(0.2,Rmax*max(0.05,(H-p.z)/H)+0.4)
        n=rad/R*0.85+Vector((0,0,0.5+0.45*(p.z/H)))
        return n.normalized() if n.length>1e-6 else Vector((0,0,1))
    def aofn(p):
        rad=math.hypot(p.x,p.y); R=max(0.2,Rmax*max(0.05,(H-p.z)/H)+0.4)
        g=0.56+0.44*min(1.0,0.5*min(1.0,rad/R)+0.5*(p.z/H)+0.1)
        return g,min(1.0,0.3+0.7*min(1.0,rad/R))
    for b in B[1:]:
        P=b["pts"]; Lb=sum((P[i+1]-P[i]).length for i in range(len(P)-1))
        n=max(2,int(Lb/cards_step)+1)
        for i in range(n):
            tt=0.1+0.9*i/max(1,n-1)
            p,r,tan=point_at(b,min(tt,0.999))
            side=Vector((-tan.y,tan.x,0)).normalized() if abs(tan.z)<0.99 else Vector((1,0,0))
            sz=rng.uniform(*size)*(1-0.3*tt)*(H/10)**0.5
            for roll in (rng.uniform(0.3,0.55),-rng.uniform(0.3,0.55)):
                R=Quaternion(tan,roll)@side
                k.lcard(p-tan*0.1,R,tan,sz*0.95,sz,"pine",flip=rng.random()<0.5,bend=0.12,rows=1,cols=2,nfn=nfn,aofn=aofn)
    tip=trunk["pts"][-1]
    for j in range(6):
        a=j*2*math.pi/6+rng.uniform(-0.2,0.2); up=Vector((math.cos(a)*0.3,math.sin(a)*0.3,1)).normalized()
        right=Vector((-math.sin(a),math.cos(a),0))
        k.lcard(tip-Vector((0,0,1.3*H/10)),right,up,1.0*H/10,1.7*H/10,"pine",flip=j%2==0,bend=0.1,rows=1,cols=2,nfn=nfn,aofn=aofn)
    return B
'''
ns=ns[:a]+new_pine+ns[b:]; tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
k=NK(); make_pine(k,21,H=10.0); o=nk_finish(k,"SM_VK_Tree_Pine_A",NC); print("pine",len(o.data.polygons))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_nat3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: pine 7046\n"}

# ==============================================================================================================
# [0224] 2026-09-23 11:02:20  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace("    bark_tubes(k,B,BARK_PINE,segs=(12,5,4,4),flare=root_flare(6,0.45,0.35,0.18),tile=1.4)",
              "    bark_tubes(k,B,BARK_PINE,segs=(12,3,3,3),flare=root_flare(6,0.45,0.35,0.18),tile=1.4)")
ns=ns.replace("            B.append(grow(p,d,L,max(0.03,r*0.45),0.015,1,rng,up=0.09,droop=0.05,wig=0.05,step=0.3,seed=seed+whorl*10+j))",
              "            B.append(grow(p,d,L,max(0.03,r*0.45),0.015,1,rng,up=0.09,droop=0.05,wig=0.05,step=0.45,seed=seed+whorl*10+j))")
code = r'''
def make_birch(k,seed,H=8.5,stems=2):
    rng=random.Random(seed); B=[]; clumps=[]
    for si in range(stems):
        a=si*2*math.pi/stems+rng.uniform(-0.4,0.4); lean=rng.uniform(0.07,0.16) if stems>1 else rng.uniform(0.0,0.05)
        base=Vector((math.cos(a)*0.18*(stems>1),math.sin(a)*0.18*(stems>1),-0.3))
        d=Vector((math.cos(a)*lean,math.sin(a)*lean,1))
        Ht=H*rng.uniform(0.85,1.0)
        tr=grow(base,d,Ht,0.2,0.04,0,rng,up=0.02,wig=0.05,step=0.4,taper=0.9,seed=seed+si); B.append(tr)
        n=int(Ht/0.42)
        for j in range(n):
            t=0.32+0.64*j/max(1,n-1)
            p,r,tan=point_at(tr,t)
            az=j*GOLD+si*1.3+rng.uniform(-0.3,0.3)
            dd=child_dir(tan,math.radians(rng.uniform(32,50)),az)
            L=rng.uniform(1.0,2.2)*(1-0.55*t)+0.5
            br=grow(p,dd,L,max(0.02,r*0.35),0.01,1,rng,up=0.02,droop=0.55,wig=0.1,step=0.3,seed=seed+si*50+j); B.append(br)
            clumps.append((br["pts"][-1],rng.uniform(0.55,0.8))); clumps.append((point_at(br,0.55)[0],rng.uniform(0.45,0.65)))
    H2=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(H2+1)
    bark_tubes(k,B,BARK_BIRCH,segs=(10,4,4,4),flare=root_flare(4,0.3,0.3,0.12),tile=1.0)
    C,ext=canopy_bounds(clumps)
    for (c,r) in clumps: clump_cards(k,c,r,10,[("birch",1.0)],rng,C,ext,size=(0.7,1.0),shell=(0.1,0.8),ao_lo=0.62)
    return B
def make_willow(k,seed,H=3.0):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.4),(rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),1),H*0.85,0.5,0.36,0,rng,up=0.02,wig=0.08,step=0.3,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(5,6)
    for j in range(n):
        az=j*2*math.pi/n+rng.uniform(-0.25,0.25); d=child_dir(tt,math.radians(rng.uniform(42,62)),az)
        limbs.append(grow(tp-tt*0.25,d,rng.uniform(2.6,3.4),tr*0.6,0.06,1,rng,up=0.12,droop=0.05,wig=0.1,step=0.3,seed=seed+j))
    B+=limbs; subs=[]
    for li,L in enumerate(limbs):
        for j in range(2):
            p,r,tan=point_at(L,rng.uniform(0.45,0.8)); d=child_dir(tan,math.radians(rng.uniform(30,50)),li*2.1+j*GOLD)
            subs.append(grow(p,d,rng.uniform(1.3,2.0),r*0.6,0.03,2,rng,up=0.06,droop=0.25,wig=0.12,step=0.25,seed=seed+30+li*3+j))
    B+=subs
    Htop=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(Htop+1)
    bark_tubes(k,B,BARK_OAK,segs=(14,8,5,4),flare=root_flare(5,0.7,0.4,0.2))
    def nfn(p):
        rad=Vector((p.x,p.y,0)); n=rad.normalized()*1.0+Vector((0,0,0.3+0.4*max(0.0,(p.z-1.0)/Htop)))
        return n.normalized()
    def aofn(p):
        rad=math.hypot(p.x,p.y); g=0.55+0.45*min(1.0,0.5*min(1.0,rad/4.0)+0.5*max(0.0,p.z/Htop))
        return g,min(1.0,0.5+0.5*(1-max(0.0,p.z)/Htop))
    for b in limbs+subs:
        P=b["pts"]; Lb=sum((P[i+1]-P[i]).length for i in range(len(P)-1)); n=max(2,int(Lb/0.3))
        for i in range(n):
            t=0.3+0.7*i/max(1,n-1); p,r,tan=point_at(b,min(t,0.999))
            if p.z<1.4: continue
            maxL=p.z-0.45
            Ls=min(maxL,rng.uniform(1.8,3.4)); a=rng.uniform(0,6.28)
            right=Vector((math.cos(a),math.sin(a),0)); radial=Vector((p.x,p.y,0)).normalized() if math.hypot(p.x,p.y)>0.1 else Vector((1,0,0))
            up=(Vector((0,0,1))-radial*0.12).normalized()
            top=p.copy(); rem=Ls
            while rem>0.3:
                h=min(1.5,rem); w=rng.uniform(0.9,1.2)
                k.lcard(top,right,up,w,h,"willow",flip=rng.random()<0.5,bend=0.06,rows=2,cols=1,nfn=nfn,aofn=aofn,anchor="top")
                top=top-up*(h*0.92); rem-=h*0.92
                right=Quaternion(Vector((0,0,1)),rng.uniform(-0.5,0.5))@right
    # crown on top of limbs
    cl=[(b["pts"][-1]+Vector((0,0,0.1)),0.8) for b in limbs]+[(point_at(b,0.5)[0]+Vector((0,0,0.25)),0.7) for b in limbs]
    C,ext=canopy_bounds(cl)
    for (c,r) in cl: clump_cards(k,c,r,10,[("willow",0.5),("birch",0.5)],rng,C,ext,size=(0.8,1.1),ao_lo=0.62)
    return B
def make_fruit(k,seed,cells,spread=1.0,cards=34):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.3),(rng.uniform(-0.12,0.12),rng.uniform(-0.12,0.12),1),1.7,0.24,0.17,0,rng,up=0.02,wig=0.12,step=0.25,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(4,5)
    for j in range(n):
        az=j*2*math.pi/n+rng.uniform(-0.3,0.3); d=child_dir(tt,math.radians(rng.uniform(40,62)),az)
        limbs.append(grow(tp-tt*0.2,d,rng.uniform(1.6,2.2)*spread,tr*0.7,0.04,1,rng,up=0.12,wig=0.18,step=0.25,seed=seed+j))
    B+=limbs; subs=[]
    for li,L in enumerate(limbs):
        for j in range(3):
            p,r,tan=point_at(L,0.35+0.2*j+rng.uniform(0,0.1)); d=child_dir(tan,math.radians(rng.uniform(35,60)),li*1.9+j*GOLD)
            subs.append(grow(p,d,rng.uniform(0.7,1.1)*spread,r*0.65,0.02,2,rng,up=0.12,wig=0.2,step=0.22,seed=seed+20+li*4+j))
    B+=subs
    H=max(p.z for b in B for p in b["pts"])
    k.wind_fn=tree_wind(H+1)
    bark_tubes(k,B,BARK_OAK,segs=(10,7,5,4),flare=root_flare(4,0.5,0.3,0.15))
    cl=[(b["pts"][-1],rng.uniform(0.75,0.95)) for b in subs]+[(b["pts"][-1]+Vector((0,0,0.1)),0.95) for b in limbs]
    out=[]
    for c in cl:
        if all((c[0]-o[0]).length>0.3*(c[1]+o[1]) for o in out): out.append(c)
    C,ext=canopy_bounds(out)
    for (c,r) in out: clump_cards(k,c,r,cards//2,cells,rng,C,ext,size=(0.85,1.2),ao_lo=0.6)
    return B
def make_dead(k,seed):
    rng=random.Random(seed)
    B,limbs,subs=sk_broad(seed,trunkH=2.8,spread=0.95,nl=(3,4),limb_len=(2.2,3.0),limb_ang=(30,58),sub_len=(1.0,1.6),r0=0.42,wig=0.3)
    # break a few branch ends
    for b in subs:
        if rng.random()<0.35:
            cut=max(3,int(len(b["pts"])*rng.uniform(0.4,0.7))); b["pts"]=b["pts"][:cut]; b["rad"]=b["rad"][:cut]
    H=max(p.z for bb in B for p in bb["pts"])
    k.wind_fn=tree_wind(H+1)
    bark_tubes(k,B,BARK_MOSSY,flare=root_flare(5,0.9,0.45,0.25))
    tw=[]
    for b in subs+limbs:
        p=b["pts"][-1]; tan=(b["pts"][-1]-b["pts"][-2]).normalized()
        tw.append((p,tan))
    C=sum((p for p,t in tw),Vector())/len(tw); ext=Vector((3,3,2))
    nfn,aofn=canopy_fns(C,ext,None,0.0,0.7)
    for (p,tan) in tw:
        for j in range(2):
            right=tan.cross(Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1))).normalized())
            if right.length<1e-3: continue
            k.lcard(p-tan*0.1,right.normalized(),(tan+Vector((0,0,0.3))).normalized(),rng.uniform(0.8,1.2),rng.uniform(0.9,1.3),"deadtwigs",flip=j%2==0,bend=0.05,nfn=nfn,aofn=aofn)
    return B
def make_sapling(k,seed):
    rng=random.Random(seed)
    tr=grow((0,0,-0.2),(rng.uniform(-0.05,0.05),rng.uniform(-0.05,0.05),1),2.6,0.07,0.015,0,rng,up=0.02,wig=0.08,step=0.25,seed=seed)
    B=[tr]; cl=[]
    for j in range(6):
        p,r,tan=point_at(tr,0.4+0.1*j); d=child_dir(tan,math.radians(rng.uniform(35,55)),j*GOLD)
        b=grow(p,d,rng.uniform(0.5,0.9),r*0.6,0.01,1,rng,up=0.1,wig=0.15,step=0.2,seed=seed+j); B.append(b); cl.append((b["pts"][-1],0.45))
    cl.append((tr["pts"][-1],0.5))
    k.wind_fn=tree_wind(3.5)
    bark_tubes(k,B,BARK_OAK,segs=(6,4,4,4),flare=None)
    C,ext=canopy_bounds(cl)
    for (c,r) in cl: clump_cards(k,c,r,12,[("broadleaf",1.0)],rng,C,ext,size=(0.55,0.8),ao_lo=0.65)
    # support stake + ties
    k.box((0.14,0.0,0.7),(0.05,0.05,1.6),WOOD,bevel=0.01)
    for z in (0.5,1.2): k.box((0.07,0,z),(0.16,0.04,0.04),BURLAP,bevel=0.01)
    return B
'''
tn.clear(); tn.write(ns+code)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(tn.as_string())
NC=vcol("VK_NaturePieces")
import time
builds=[("SM_VK_Tree_Pine_A",lambda k: make_pine(k,21,H=10.0)),
        ("SM_VK_Tree_Pine_B",lambda k: make_pine(k,27,H=13.0,Rmax_f=0.26)),
        ("SM_VK_Tree_Pine_Young",lambda k: make_pine(k,29,H=4.5,Rmax_f=0.36,young=True)),
        ("SM_VK_Tree_Oak_A",lambda k: make_broad_tree(k,11,[("broadleaf",0.75),("broadleaf_dark",0.25)],cards=40,size=(1.05,1.5))),
        ("SM_VK_Tree_Oak_B",lambda k: make_broad_tree(k,17,[("broadleaf",0.6),("broadleaf_dark",0.4)],trunkH=3.8,spread=0.85,cards=38,size=(1.05,1.5))),
        ("SM_VK_Tree_Oak_Autumn",lambda k: make_broad_tree(k,13,[("autumn_orange",0.55),("autumn_red",0.3),("broadleaf",0.15)],cards=38,size=(1.05,1.5))),
        ("SM_VK_Tree_Birch",lambda k: make_birch(k,41,H=8.5,stems=2)),
        ("SM_VK_Tree_Birch_Single",lambda k: make_birch(k,43,H=7.5,stems=1)),
        ("SM_VK_Tree_Willow",lambda k: make_willow(k,51)),
        ("SM_VK_Tree_Apple",lambda k: make_fruit(k,61,[("apple",0.55),("broadleaf",0.45)])),
        ("SM_VK_Tree_Blossom",lambda k: make_fruit(k,67,[("blossom",0.8),("broadleaf",0.2)],spread=1.1)),
        ("SM_VK_Tree_Dead",lambda k: make_dead(k,71)),
        ("SM_VK_Tree_Sapling",lambda k: make_sapling(k,81))]
for n,fn in builds:
    t0=time.time(); k=NK(); fn(k); o=nk_finish(k,n,NC); print(n,len(o.data.polygons),round(time.time()-t0,1))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Pine_A 4590 0.1\nSM_VK_Tree_Pine_B 5252 0.1\nSM_VK_Tree_Pine_Young 3797 0.1\nSM_VK_Tree_Oak_A 4355 0
# .1\nSM_VK_Tree_Oak_B 3541 0.1\nSM_VK_Tree_Oak_Autumn 3837 0.1\nSM_VK_Tree_Birch 3912 0.1\nSM_VK_Tree_Birch_Single 1660 0.0\nSM_VK_Tree_Willow 1772 0.0
# \nSM_VK_Tree_Apple 1567 0.0\nSM_VK_Tree_Blossom 1674 0.0\nSM_VK_Tree_Dead 954 0.0\nSM_VK_Tree_Sapling 570 0.0\n"}

# ==============================================================================================================
# [0225] 2026-09-23 11:02:38  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
S=bpy.data.collections["VK_NatureTest"]
for ob in list(S.objects): bpy.data.objects.remove(ob)
names=["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Oak_Autumn","SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Birch",
       "SM_VK_Tree_Birch_Single","SM_VK_Tree_Willow","SM_VK_Tree_Apple","SM_VK_Tree_Blossom","SM_VK_Tree_Dead","SM_VK_Tree_Sapling"]
x=600.0
for n in names:
    me=bpy.data.objects[n].data
    xs=[v.co.x for v in me.vertices]; w=max(xs)-min(xs)
    ob=bpy.data.objects.new(n+"_t",me); S.objects.link(ob); ob.location=(x-min(xs),0,0); x+=w+0.8
W=x-600
g=bpy.data.objects["VK_Ground"]; g.location=(600+W/2,0,0); g.scale=(6,6,1)
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]; cn.data.lens=35
tgt=Vector((600+W/2,0,5.0)); cn.location=tgt+Vector((0,-W*0.95,W*0.12))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.resolution_percentage=100
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_trees1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
print(W)
# ---- result ----
# {"result":"Code executed successfully: 94.05473902225435\n"}

# ==============================================================================================================
# [0226] 2026-09-23 11:02:56  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
def pos(n): return bpy.data.objects[n+"_t"].location
SC.render.resolution_percentage=50
pb=pos("SM_VK_Tree_Birch"); pw=pos("SM_VK_Tree_Willow")
tgt=(pb+pw)/2+Vector((3,0,4)); cn.data.lens=32; cn.location=tgt+Vector((0,-24,1.0))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_trees2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
pa=pos("SM_VK_Tree_Apple"); pd=pos("SM_VK_Tree_Sapling")
tgt=(pa+pd)/2+Vector((2,0,2.2)); cn.location=tgt+Vector((0,-17,0.8))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_trees3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0227] 2026-09-23 11:03:33  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
old_start=ns.index("    for b in limbs+subs:\n        P=b[\"pts\"]; Lb=sum((P[i+1]-P[i]).length for i in range(len(P)-1)); n=max(2,int(Lb/0.3))")
old_end=ns.index("    return B\ndef make_fruit(")
new_body='''    for b in limbs+subs:
        P=b["pts"]; Lb=sum((P[i+1]-P[i]).length for i in range(len(P)-1)); n=max(2,int(Lb/0.17))
        for i in range(n):
            t=0.25+0.75*i/max(1,n-1); p,r,tan=point_at(b,min(t,0.999))
            if p.z<1.3: continue
            maxL=p.z-0.35
            radial=Vector((p.x,p.y,0)).normalized() if math.hypot(p.x,p.y)>0.1 else Vector((1,0,0))
            for rep in range(2):
                Ls=min(maxL,rng.uniform(1.4,3.6)); a=rng.uniform(0,6.28)
                right=Vector((math.cos(a),math.sin(a),0))
                up=(Vector((0,0,1))-radial*0.1).normalized()
                top=p+radial*rng.uniform(0.0,0.15); rem=Ls
                while rem>0.3:
                    h=min(1.5,rem); w=rng.uniform(0.7,1.0)
                    k.lcard(top,right,up,w,h,"willow",flip=rng.random()<0.5,bend=0.08,rows=2,cols=1,nfn=nfn,aofn=aofn,anchor="top")
                    top=top-up*(h*0.92); rem-=h*0.92
                    right=Quaternion(Vector((0,0,1)),rng.uniform(-0.6,0.6))@right
    cl=[(b["pts"][-1]+Vector((0,0,0.15)),0.85) for b in limbs]+[(point_at(b,0.5)[0]+Vector((0,0,0.3)),0.75) for b in limbs]
    C,ext=canopy_bounds(cl)
    for (c,r) in cl: clump_cards(k,c,r,12,[("birch",0.7),("broadleaf",0.3)],rng,C,ext,size=(0.8,1.1),ao_lo=0.66)
'''
ns=ns[:old_start]+new_body+ns[old_end:]
ns=ns.replace("        rad=math.hypot(p.x,p.y); g=0.55+0.45*min(1.0,0.5*min(1.0,rad/4.0)+0.5*max(0.0,p.z/Htop))",
              "        rad=math.hypot(p.x,p.y); g=0.66+0.34*min(1.0,0.5*min(1.0,rad/4.0)+0.5*max(0.0,p.z/Htop))")
ns=ns.replace("    for (c,r) in clumps: clump_cards(k,c,r,10,[(\"birch\",1.0)],rng,C,ext,size=(0.7,1.0),shell=(0.1,0.8),ao_lo=0.62)",
              "    for (c,r) in clumps: clump_cards(k,c,r,11,[(\"birch\",1.0)],rng,C,ext,size=(0.7,1.0),shell=(0.1,0.8),ao_lo=0.72)")
ns=ns.replace("def make_fruit(k,seed,cells,spread=1.0,cards=34):","def make_fruit(k,seed,cells,spread=1.0,cards=34,size=(0.85,1.2)):")
ns=ns.replace("    for (c,r) in out: clump_cards(k,c,r,cards//2,cells,rng,C,ext,size=(0.85,1.2),ao_lo=0.6)",
              "    for (c,r) in out: clump_cards(k,c,r,cards//2,cells,rng,C,ext,size=size,ao_lo=0.64)")
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
for n,fn in [("SM_VK_Tree_Willow",lambda k: make_willow(k,51)),
             ("SM_VK_Tree_Blossom",lambda k: make_fruit(k,67,[("blossom",0.88),("broadleaf",0.12)],spread=1.1,cards=52,size=(0.6,0.9))),
             ("SM_VK_Tree_Apple",lambda k: make_fruit(k,61,[("apple",0.55),("broadleaf",0.45)],cards=40)),
             ("SM_VK_Tree_Birch",lambda k: make_birch(k,41,H=8.5,stems=2)),("SM_VK_Tree_Birch_Single",lambda k: make_birch(k,43,H=7.5,stems=1))]:
    k=NK(); fn(k); o=nk_finish(k,n,NC); print(n,len(o.data.polygons))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_trees3.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
cn=bpy.data.objects["VK_CameraNature"]
def pos(n): return bpy.data.objects[n+"_t"].location
pb=pos("SM_VK_Tree_Birch"); pw=pos("SM_VK_Tree_Willow")
tgt=(pb+pw)/2+Vector((3,0,4)); cn.location=tgt+Vector((0,-24,1.0))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_trees2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Willow 2866\nSM_VK_Tree_Blossom 2090\nSM_VK_Tree_Apple 1751\nSM_VK_Tree_Birch 4172\nSM_VK_Tree_Birch
# _Single 1768\n"}

# ==============================================================================================================
# [0228] 2026-09-23 11:04:03  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace("        limbs.append(grow(tp-tt*0.25,d,rng.uniform(2.6,3.4),tr*0.6,0.06,1,rng,up=0.12,droop=0.05,wig=0.1,step=0.3,seed=seed+j))",
              "        limbs.append(grow(tp-tt*0.25,d,rng.uniform(3.4,4.3),tr*0.6,0.06,1,rng,up=0.2,droop=0.28,wig=0.1,step=0.3,seed=seed+j))")
ns=ns.replace("        az=j*2*math.pi/n+rng.uniform(-0.25,0.25); d=child_dir(tt,math.radians(rng.uniform(42,62)),az)\n        limbs.append(",
              "        az=j*2*math.pi/n+rng.uniform(-0.25,0.25); d=child_dir(tt,math.radians(rng.uniform(50,68)),az)\n        limbs.append(")
ns=ns.replace('''            if p.z<1.3: continue
            maxL=p.z-0.35
            radial=Vector((p.x,p.y,0)).normalized() if math.hypot(p.x,p.y)>0.1 else Vector((1,0,0))
            for rep in range(2):
                Ls=min(maxL,rng.uniform(1.4,3.6)); a=rng.uniform(0,6.28)''','''            if p.z<1.3: continue
            rad_d=math.hypot(p.x,p.y)
            maxL=p.z-rng.uniform(0.35,1.3)
            radial=Vector((p.x,p.y,0)).normalized() if rad_d>0.1 else Vector((1,0,0))
            for rep in range(2):
                Ls=min(maxL,rng.uniform(0.9,2.0)+1.9*min(1.0,rad_d/3.5)*rng.uniform(0.7,1.1)); a=rng.uniform(0,6.28)''')
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
k=NK(); make_willow(k,51); o=nk_finish(k,"SM_VK_Tree_Willow",NC); print(len(o.data.polygons))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cn=bpy.data.objects["VK_CameraNature"]
pw=bpy.data.objects["SM_VK_Tree_Willow_t"].location
tgt=pw+Vector((3.2,0,2.6)); cn.location=tgt+Vector((2,-15,1.2))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_trees2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 3138\n"}

# ==============================================================================================================
# [0229] 2026-09-23 11:04:41  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
a=ns.index("def make_willow("); b=ns.index("def make_fruit(")
new='''def make_willow(k,seed,H=3.0,R=3.9,Rz=2.3):
    rng=random.Random(seed); B=[]
    trunk=grow((0,0,-0.4),(rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),1),H*0.85,0.5,0.36,0,rng,up=0.02,wig=0.08,step=0.3,seed=seed); B.append(trunk)
    tp,tr,tt=point_at(trunk,1.0); limbs=[]
    n=rng.randint(5,6)
    for j in range(n):
        az=j*2*math.pi/n+rng.uniform(-0.25,0.25); d=child_dir(tt,math.radians(rng.uniform(45,62)),az)
        limbs.append(grow(tp-tt*0.25,d,rng.uniform(3.0,3.8),tr*0.6,0.06,1,rng,up=0.18,droop=0.3,wig=0.1,step=0.3,seed=seed+j))
    B+=limbs
    k.wind_fn=tree_wind(tp.z+Rz+1)
    bark_tubes(k,B,BARK_OAK,segs=(14,8,5,4),flare=root_flare(5,0.7,0.4,0.2))
    C=Vector((0,0,tp.z+0.2))
    def nfn(p):
        d=p-C; n=Vector((d.x/R,d.y/R,max(d.z,-Rz)/Rz))
        n=n.normalized() if n.length>1e-6 else Vector((0,0,1))
        return (n+Vector((0,0,0.25))).normalized()
    def aofn(p):
        d=p-C; q=Vector((d.x/R,d.y/R,d.z/Rz)); outer=min(1.0,q.length)
        up=0.5+0.5*max(-1.0,min(1.0,d.z/Rz))
        g=0.6+0.4*min(1.0,0.5*up+0.5*outer**1.5)
        return g,min(1.0,0.4+0.6*outer)
    # hair over the dome
    N=150
    for i in range(N):
        zf=1-(i+0.5)/N*0.92; th=math.acos(zf); ph=i*GOLD+rng.uniform(-0.2,0.2)
        s_=math.sin(th); dirv=Vector((s_*math.cos(ph),s_*math.sin(ph),math.cos(th)))
        p=C+Vector((dirv.x*R,dirv.y*R,dirv.z*Rz))*rng.uniform(0.9,1.03)
        t_=Vector((math.cos(th)*math.cos(ph)*R,math.cos(th)*math.sin(ph)*R,-math.sin(th)*Rz)).normalized()
        down=(t_+Vector((0,0,-0.35))).normalized()
        right=Vector((-math.sin(ph),math.cos(ph),0))
        h=rng.uniform(1.2,1.7)
        k.lcard(p,right,-down,rng.uniform(0.85,1.1),h,"willow",flip=rng.random()<0.5,bend=0.1,rows=2,cols=1,nfn=nfn,aofn=aofn,anchor="top")
    # curtain around the rim
    M=90
    for i in range(M):
        ph=i*2*math.pi/M+rng.uniform(-0.03,0.03)
        th=math.radians(rng.uniform(62,95)); s_=math.sin(th)
        radial=Vector((math.cos(ph),math.sin(ph),0))
        top=C+Vector((s_*math.cos(ph)*R,s_*math.sin(ph)*R,math.cos(th)*Rz))*rng.uniform(0.93,1.02)
        end_z=rng.uniform(0.35,1.4); Ls=max(0.5,top.z-end_z)
        right=Vector((-math.sin(ph),math.cos(ph),0)); up=(Vector((0,0,1))-radial*0.22).normalized()
        rem=Ls
        while rem>0.3:
            h=min(1.5,rem); w=rng.uniform(0.8,1.05)
            k.lcard(top,right,up,w,h,"willow",flip=rng.random()<0.5,bend=0.08,rows=2,cols=1,nfn=nfn,aofn=aofn,anchor="top")
            top=top-up*(h*0.9); rem-=h*0.9
            right=Quaternion(Vector((0,0,1)),rng.uniform(-0.35,0.35))@right
    return B
'''
ns=ns[:a]+new+ns[b:]; tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
k=NK(); make_willow(k,51); o=nk_finish(k,"SM_VK_Tree_Willow",NC); print(len(o.data.polygons))
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_trees2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 1262\n"}

# ==============================================================================================================
# [0230] 2026-09-23 11:06:28  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace('''        limbs.append(grow(tp-tt*0.25,d,rng.uniform(3.0,3.8),tr*0.6,0.06,1,rng,up=0.18,droop=0.3,wig=0.1,step=0.3,seed=seed+j))
    B+=limbs''','''        L_=grow(tp-tt*0.25,d,rng.uniform(3.0,3.8),tr*0.6,0.06,1,rng,up=0.18,droop=0.3,wig=0.1,step=0.3,seed=seed+j)
        Cq=Vector((0,0,tp.z+0.2)); keep=[]
        for pp in L_["pts"]:
            dq=pp-Cq
            if (dq.x/R)**2+(dq.y/R)**2+(max(dq.z,0)/Rz)**2>0.72 and len(keep)>2: break
            keep.append(pp)
        L_["pts"]=keep; L_["rad"]=L_["rad"][:len(keep)]
        limbs.append(L_)
    B+=limbs''')
code = r'''
# =====================  BUSHES / PLANTS  =====================
def plant_fns(center=Vector((0,0,0)),H=1.0,ao_lo=0.62,radw=0.45):
    def nfn(p):
        rad=Vector((p.x-center.x,p.y-center.y,0))
        n=Vector((0,0,1))+ (rad.normalized()*radw if rad.length>1e-4 else Vector((0,0,0)))
        return n.normalized()
    def aofn(p):
        t=max(0.0,min(1.0,(p.z-center.z)/H)); return ao_lo+(1-ao_lo)*t, min(1.0,0.2+0.8*t)
    return nfn,aofn
def make_bush(k,seed,cells,R=0.9,H=1.1,nclump=4,cards=22,size=(0.6,0.9)):
    rng=random.Random(seed); cl=[]
    for i in range(nclump):
        a=i*GOLD+rng.uniform(-0.4,0.4); d=rng.uniform(0.15,0.5)*R if i else 0.0
        c=Vector((math.cos(a)*d,math.sin(a)*d,H*rng.uniform(0.45,0.6))); cl.append((c,rng.uniform(0.55,0.75)*R))
    for i in range(3):
        a=rng.uniform(0,6.28); k.tube([Vector((0,0,-0.1)),Vector((math.cos(a)*0.2,math.sin(a)*0.2,0.45))],[0.05,0.025],5,WOOD,cap_end=True)
    C,ext=canopy_bounds(cl); ext.z=max(ext.z,H*0.6)
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z/H))
    for (c,r) in cl: clump_cards(k,c,r,cards,cells,rng,C,ext,size=size,shell=(0.2,0.9),ao_lo=0.55)
def make_fern(k,seed,n=11,Hs=(0.9,1.3)):
    rng=random.Random(seed); nfn,aofn=plant_fns(H=1.0,ao_lo=0.6,radw=0.6)
    for i in range(n):
        a=i*2*math.pi/n+rng.uniform(-0.25,0.25); out=Vector((math.cos(a),math.sin(a),0))
        up=(out*rng.uniform(0.55,0.9)+Vector((0,0,1))).normalized(); right=Vector((-math.sin(a),math.cos(a),0))
        h=rng.uniform(*Hs)
        k.lcard(Vector((0,0,0.02))+out*0.05,right,up,h*0.62,h,"fern",flip=rng.random()<0.5,bend=0.04,arch=-0.28,rows=3,cols=2,nfn=nfn,aofn=aofn)
    for i in range(3):
        a=rng.uniform(0,6.28); up=Vector((math.cos(a)*0.2,math.sin(a)*0.2,1)).normalized(); right=Vector((-math.sin(a),math.cos(a),0))
        k.lcard(Vector((0,0,0)),right,up,0.45,0.75,"fern",flip=i%2==0,bend=0.04,arch=-0.1,rows=2,cols=1,nfn=nfn,aofn=aofn)
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z))
def make_tufts(k,seed,cell,n=9,R=0.6,Hs=(0.8,1.2),W=0.8,pairs=2):
    rng=random.Random(seed); nfn,aofn=plant_fns(H=max(Hs),ao_lo=0.62,radw=0.35)
    for i in range(n):
        a=rng.uniform(0,6.28); d=R*math.sqrt(rng.random()); c=Vector((math.cos(a)*d,math.sin(a)*d,-0.02))
        h=rng.uniform(*Hs); rot=rng.uniform(0,3.14)
        for j in range(pairs):
            aa=rot+j*math.pi/pairs; right=Vector((math.cos(aa),math.sin(aa),0))
            up=Vector((rng.uniform(-0.1,0.1),rng.uniform(-0.1,0.1),1)).normalized()
            k.lcard(c,right,up,W*h,h,cell,flip=rng.random()<0.5,bend=0.05,rows=2,cols=2,nfn=nfn,aofn=aofn)
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z/max(Hs)))
def mushroom(k,c,h,r,cap_mi,seed=0,spots=False,tilt=0.0,shape="dome"):
    rng=random.Random(seed); cx,cy,cz=c
    M=Matrix.Translation(Vector(c))@Matrix.Rotation(tilt,4,Vector((rng.uniform(-1,1),rng.uniform(-1,1),0)).normalized() if tilt else "Z")
    sub=Kit()
    stem=[(r*0.28,0.0),(r*0.24,h*0.4),(r*0.2,h*0.9),(r*0.22,h)]
    lathe(sub,stem,segs=10,mi=MUSH_STEM,smooth_=True)
    if shape=="dome":
        prof=[(r*0.2,h*0.92),(r*0.95,h*0.92),(r*1.0,h*1.02),(r*0.9,h*1.25),(r*0.6,h*1.42),(r*0.25,h*1.5),(0.0,h*1.52)]
    elif shape=="cone":
        prof=[(r*0.2,h*0.92),(r*0.9,h*0.9),(r*0.7,h*1.2),(r*0.35,h*1.5),(0.0,h*1.7)]
    else:
        prof=[(r*0.2,h*0.95),(r*1.0,h*0.98),(r*1.05,h*1.08),(r*0.7,h*1.16),(0.0,h*1.2)]
    lathe(sub,prof,segs=16,mi=cap_mi,smooth_=True)
    if spots:
        for i in range(9):
            a=i*GOLD; rr=r*rng.uniform(0.3,0.8); zz=h*1.52-(rr/r)**2*h*0.55
            vs=_ico(sub,(math.cos(a)*rr,math.sin(a)*rr,zz+0.005),r*0.1,MUSH_STEM,(1,1,0.4),sub=1)
    for f in sub.bm.faces: f.smooth=True
    merge_kit(k,sub,M)
def make_mushrooms(k,seed,kind="red"):
    rng=random.Random(seed)
    n={"red":4,"brown":6,"glow":7}[kind]
    for i in range(n):
        a=i*GOLD; d=rng.uniform(0.0,0.35) if i else 0.0
        c=(math.cos(a)*d,math.sin(a)*d,-0.01)
        if kind=="red": mushroom(k,c,rng.uniform(0.14,0.3),rng.uniform(0.08,0.15),MUSH_RED,seed=i,spots=True,tilt=rng.uniform(0,0.2))
        elif kind=="brown": mushroom(k,c,rng.uniform(0.08,0.18),rng.uniform(0.05,0.1),MUSH_BROWN,seed=i,tilt=rng.uniform(0,0.25),shape="flat")
        else: mushroom(k,c,rng.uniform(0.2,0.45),rng.uniform(0.05,0.09),MUSH_GLOW,seed=i,tilt=rng.uniform(0,0.3),shape="cone")
    k.wind_fn=lambda p: 0.0
def endcap(k,c,axis,r,seed=0):
    """disc with end-grain UVs facing along axis"""
    ax=Vector(axis).normalized(); t1=ax.cross(Vector((0,0,1)) if abs(ax.z)<0.9 else Vector((1,0,0))).normalized(); t2=ax.cross(t1)
    n=16; ring=[k.bm.verts.new(Vector(c)+(t1*math.cos(2*math.pi*i/n)+t2*math.sin(2*math.pi*i/n))*r) for i in range(n)]
    ctr=k.bm.verts.new(Vector(c)+ax*0.01)
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[(i+1)%n])); f.material_index=ENDGRAIN; f.smooth=True
        for l in f.loops:
            d=l.vert.co-Vector(c); l[k.uv].uv=(0.5+d.dot(t1)/r*0.44,0.5+d.dot(t2)/r*0.44)
    k.bm.normal_update()
    if f.normal.dot(ax)<0:
        for ff in ctr.link_faces: ff.normal_flip()
def bracket_fungus(k,c,out,r,seed=0):
    rng=random.Random(seed); o=Vector(out).normalized(); side=o.cross(Vector((0,0,1))).normalized()
    for j in range(3):
        cc=Vector(c)+Vector((0,0,-j*r*0.7))+side*rng.uniform(-r,r)*0.5
        prof=[]
        vs=[]
        n=9
        ring=[]
        for i in range(n+1):
            a=math.pi*i/n; p=cc+side*math.cos(a)*r*(1-0.15*j)+o*math.sin(a)*r*0.8*(1-0.15*j)
            ring.append(p)
        top=[k.bm.verts.new(p+Vector((0,0,0.03))) for p in ring]; bot=[k.bm.verts.new(p-Vector((0,0,0.02))) for p in ring]
        ct=k.bm.verts.new(cc+Vector((0,0,0.05))); cb=k.bm.verts.new(cc-Vector((0,0,0.02)))
        fs=[]
        for i in range(n):
            fs.append(k.bm.faces.new((ct,top[i],top[i+1]))); fs.append(k.bm.faces.new((cb,bot[i+1],bot[i]))); fs.append(k.bm.faces.new((top[i],bot[i],bot[i+1],top[i+1])))
        for f in fs: f.material_index=MUSH_BROWN; f.smooth=True
        k.bm.normal_update()
        for f in fs:
            if f.calc_center_median().z>cc.z+0.02 and f.normal.z<0: f.normal_flip()
def make_stump(k,seed):
    rng=random.Random(seed)
    pts=[Vector((0,0,-0.2)),Vector((0,0,0.2)),Vector((0.02,0,0.45)),Vector((0.03,0.01,0.62))]
    k.tube(pts,[0.46,0.44,0.42,0.42],14,BARK_MOSSY,tileU=1.2,tileV=1.2,flare=root_flare(5,1.1,0.25,0.3),cap_end=False,noise_amp=0.06)
    endcap(k,(0.03,0.01,0.62),(0,0,1),0.43)
    for i in range(3):
        a=i*2.1+rng.uniform(-0.3,0.3); mushroom(k,(math.cos(a)*0.62,math.sin(a)*0.62,-0.02),rng.uniform(0.08,0.14),rng.uniform(0.05,0.08),MUSH_BROWN,seed=i,shape="flat")
    bracket_fungus(k,(0.4,-0.1,0.42),(1,-0.2,0),0.14,seed)
    k.wind_fn=lambda p: 0.0
def make_log(k,seed,L=3.4,r=0.34):
    rng=random.Random(seed)
    pts=[Vector((-L/2+L*i/8,0.08*math.sin(i*0.7),r*0.85+0.03*math.sin(i*1.3))) for i in range(9)]
    k.tube(pts,[r*(1-0.1*i/8) for i in range(9)],12,BARK_MOSSY,tileU=1.2,tileV=1.2,cap_end=False,noise_amp=0.07)
    endcap(k,pts[0],(pts[0]-pts[1]).normalized(),r*0.98); endcap(k,pts[-1],(pts[-1]-pts[-2]).normalized(),r*0.88)
    stub=[pts[3],pts[3]+Vector((0.2,0.35,0.3)),pts[3]+Vector((0.3,0.55,0.45))]
    k.tube(stub,[0.1,0.07,0.06],7,BARK_MOSSY,cap_end=False)
    endcap(k,stub[-1],(stub[-1]-stub[-2]).normalized(),0.06)
    bracket_fungus(k,pts[5]+Vector((0,-r*0.9,0.05)),(0,-1,0),0.12,seed+1)
    for i in range(4): mushroom(k,(rng.uniform(-L/2,L/2),rng.uniform(0.35,0.6)*(1 if i%2 else -1),-0.02),rng.uniform(0.08,0.14),rng.uniform(0.05,0.08),MUSH_BROWN,seed=i+10,shape="flat")
    sub=NK(); make_fern(sub,seed+5,n=6,Hs=(0.6,0.9))
    k.wind_fn=lambda p: 0.0
    return sub
# =====================  ROCKS  =====================
def box_uv(k,faces,tile,offset=(0.0,0.0)):
    for f in faces:
        n=f.normal; ax=max(range(3),key=lambda i: abs(n[i]))
        for l in f.loops:
            p=l.vert.co
            uv=(p.y,p.z) if ax==0 else ((p.x,p.z) if ax==1 else (p.x,p.y))
            l[k.uv].uv=(uv[0]/tile+offset[0],uv[1]/tile+offset[1])
def boulder(k,c,size,seed,mi=None,cuts=7,sub=3,flat_bottom=0.3,tile=1.5,rot=0.0,lean=0.0):
    mi=ROCK_MOSSY if mi is None else mi
    rnd=random.Random(seed)
    res=bmesh.ops.create_icosphere(k.bm,subdivisions=sub,radius=1.0); vs=res["verts"]
    sv=Vector((seed*1.7,seed*0.3,seed*2.9))
    for v in vs:
        d=v.co.normalized(); v.co=d*(1+0.2*noise.noise(d*1.2+sv)+0.06*noise.noise(d*3.3+sv*1.3))
    for i in range(cuts):
        n=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-0.2,1))).normalized(); off=rnd.uniform(0.6,0.84)
        for v in vs:
            dd=v.co.dot(n)
            if dd>off: v.co-=n*(dd-off)*rnd.uniform(0.9,1.0)
    for v in vs:
        if v.co.z<-flat_bottom: v.co.z=-flat_bottom+(v.co.z+flat_bottom)*0.05
    M=Matrix.Translation(Vector(c))@Matrix.Rotation(rot,4,"Z")@Matrix.Rotation(lean,4,"X")
    for v in vs:
        p=Vector((v.co.x*size[0]/2,v.co.y*size[1]/2,(v.co.z+flat_bottom)/(1+flat_bottom)*size[2]))
        v.co=M@p
    faces=list({f for v in vs for f in v.link_faces})
    for f in faces: f.material_index=mi
    k.bm.normal_update(); box_uv(k,faces,tile,(rnd.random(),rnd.random()))
    return vs
def make_rock_cluster(k,seed,n=5,R=1.2,big=1.4):
    rng=random.Random(seed)
    for i in range(n):
        a=i*GOLD+rng.uniform(-0.3,0.3); d=rng.uniform(0.2,1.0)*R if i else 0.0; s_=big*(1.0 if i==0 else rng.uniform(0.35,0.7))
        boulder(k,(math.cos(a)*d,math.sin(a)*d,-0.08*s_),(s_*rng.uniform(1.0,1.4),s_*rng.uniform(0.8,1.1),s_*rng.uniform(0.6,0.9)),seed*10+i,rot=rng.uniform(0,6.28),cuts=6)
def make_pebbles(k,seed,n=22,R=1.3):
    rng=random.Random(seed)
    for i in range(n):
        a=rng.uniform(0,6.28); d=R*math.sqrt(rng.random()); s_=rng.uniform(0.1,0.3)
        boulder(k,(math.cos(a)*d,math.sin(a)*d,-0.03),(s_*rng.uniform(1,1.5),s_,s_*rng.uniform(0.4,0.7)),seed*100+i,mi=ROCK,cuts=3,sub=2,rot=rng.uniform(0,6.28))
def make_stepstones(k,seed,n=6,L=5.0):
    rng=random.Random(seed)
    for i in range(n):
        t=i/(n-1); x=-L/2+L*t; y=0.35*math.sin(t*3.5)
        s_=rng.uniform(0.6,0.8); boulder(k,(x,y,-0.14),(s_*1.2,s_,0.3),seed*10+i,mi=ROCK,cuts=4,sub=2,flat_bottom=0.6,rot=rng.uniform(0,6.28))
def make_outcrop(k,seed):
    rng=random.Random(seed)
    layers=[(0.0,4.8,3.4,1.3),(1.1,4.0,2.8,1.1),(2.0,2.8,2.2,1.0),(2.8,1.8,1.5,0.8)]
    for i,(z,sx,sy,sz) in enumerate(layers):
        off=Vector((rng.uniform(-0.4,0.4),rng.uniform(-0.3,0.3),z-0.15))
        boulder(k,off,(sx,sy,sz*1.15),seed*10+i,cuts=9,flat_bottom=0.5,rot=rng.uniform(-0.3,0.3))
    for i in range(4):
        a=rng.uniform(0,6.28); boulder(k,(math.cos(a)*2.6,math.sin(a)*1.9,-0.05),(0.7,0.6,0.5),seed*20+i,cuts=5,sub=2,rot=rng.uniform(0,6.28))
def make_standing_stone(k,seed,H=3.0):
    rng=random.Random(seed)
    boulder(k,(0,0,-0.2),(0.95,0.62,H+0.2),seed,cuts=6,flat_bottom=0.9,rot=rng.uniform(0,6.28),lean=rng.uniform(-0.06,0.06),tile=1.5)
    for i in range(3):
        a=rng.uniform(0,6.28); boulder(k,(math.cos(a)*0.7,math.sin(a)*0.55,-0.05),(0.35,0.3,0.25),seed*7+i,mi=ROCK,cuts=3,sub=2)
# =====================  POND  =====================
def lily_pad(k,c,r,rot,seed=0):
    rng=random.Random(seed); n=14; notch=0.35
    ctr=k.bm.verts.new(Vector(c)+Vector((0,0,0.012)))
    ring=[]
    for i in range(n+1):
        a=rot+notch/2+(2*math.pi-notch)*i/n
        rr=r*(1+0.04*math.sin(a*5+seed))
        ring.append(k.bm.verts.new(Vector(c)+Vector((math.cos(a)*rr,math.sin(a)*rr,0.0))))
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[i+1])); f.material_index=LEAF; f.smooth=True
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
def lily_flower(k,c,r,seed=0):
    rng=random.Random(seed); cx,cy,cz=c
    for layer,(n,rr,tilt) in enumerate(((8,r,0.55),(6,r*0.7,0.95))):
        for i in range(n):
            a=i*2*math.pi/n+layer*0.3
            base=Vector((cx,cy,cz+0.02+layer*0.02)); d=Vector((math.cos(a),math.sin(a),0))
            tip=base+d*rr*math.cos(tilt)+Vector((0,0,rr*math.sin(tilt)))
            side=Vector((-math.sin(a),math.cos(a),0))*rr*0.3
            vs=[k.bm.verts.new(p) for p in (base,base+d*rr*0.45+side+Vector((0,0,0.02)),tip,base+d*rr*0.45-side+Vector((0,0,0.02)))]
            f=k.bm.faces.new(vs); f.material_index=PINK; f.smooth=True
    _ico(k,(cx,cy,cz+0.06),r*0.22,YELLOW,sub=1)
def make_pond(k,seed,R=2.8):
    rng=random.Random(seed); n=32
    ctr=k.bm.verts.new((0,0,0.05)); ring=[]
    radii=[R*(1+0.12*math.sin(i*2*math.pi/n*3+seed)+0.07*math.sin(i*2*math.pi/n*5+1.7)) for i in range(n)]
    for i in range(n):
        a=2*math.pi*i/n; ring.append(k.bm.verts.new((math.cos(a)*radii[i],math.sin(a)*radii[i],0.05)))
    for i in range(n):
        f=k.bm.faces.new((ctr,ring[i],ring[(i+1)%n])); f.material_index=WATER; f.smooth=True
        for l in f.loops: l[k.uv].uv=(l.vert.co.x/2,l.vert.co.y/2)
    # muddy bank ring slightly below water edge
    for i in range(n):
        a=2*math.pi*i/n; a2=2*math.pi*(i+1)/n
        p1=Vector((math.cos(a)*radii[i],math.sin(a)*radii[i],0.05)); p2=Vector((math.cos(a2)*radii[(i+1)%n],math.sin(a2)*radii[(i+1)%n],0.05))
        q1=p1*1.12; q1.z=0.0; q2=p2*1.12; q2.z=0.0
        f=k.bm.faces.new([k.bm.verts.new(p) for p in (p1,q1,q2,p2)]); f.material_index=SOIL; f.smooth=True
        for l in f.loops: l[k.uv].uv=(l.vert.co.x,l.vert.co.y)
    k.bm.normal_update()
    for f in k.bm.faces:
        if f.normal.z<0: f.normal_flip()
    # stones around ~60% of the rim
    for i in range(0,n):
        if i%3==0 or (i>n*0.55 and i<n*0.8): continue
        a=2*math.pi*i/n+rng.uniform(-0.05,0.05); rr=radii[i]*rng.uniform(1.02,1.12); s_=rng.uniform(0.35,0.7)
        boulder(k,(math.cos(a)*rr,math.sin(a)*rr,-0.06),(s_*1.3,s_,s_*0.55),seed*50+i,cuts=4,sub=2,rot=a)
    for i in range(7):
        a=rng.uniform(0,6.28); d=rng.uniform(0.3,0.8)*R; lily_pad(k,(math.cos(a)*d,math.sin(a)*d,0.055),rng.uniform(0.18,0.3),rng.uniform(0,6.28),seed+i)
        if i%3==0: lily_flower(k,(math.cos(a)*d,math.sin(a)*d,0.06),0.12,seed+i)
    sub=NK(); make_tufts(sub,seed+3,"reeds",n=9,R=0.8,Hs=(1.3,1.8),W=0.7)
    return sub
'''
tn.clear(); tn.write(ns+code)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(tn.as_string())
print("ok")
# ---- result ----
# {"result":"Code executed successfully: ok\n"}

# ==============================================================================================================
# [0231] 2026-09-23 11:07:04  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace('''def make_fern(k,seed,n=11,Hs=(0.9,1.3)):
    rng=random.Random(seed); nfn,aofn=plant_fns(H=1.0,ao_lo=0.6,radw=0.6)''','''def make_fern(k,seed,n=11,Hs=(0.9,1.3),c=(0,0,0)):
    rng=random.Random(seed); C0=Vector(c); nfn,aofn=plant_fns(center=C0,H=1.0,ao_lo=0.6,radw=0.6)''')
ns=ns.replace("        k.lcard(Vector((0,0,0.02))+out*0.05,right,up,h*0.62,h,\"fern\"","        k.lcard(C0+Vector((0,0,0.02))+out*0.05,right,up,h*0.62,h,\"fern\"")
ns=ns.replace("        k.lcard(Vector((0,0,0)),right,up,0.45,0.75,\"fern\"","        k.lcard(C0,right,up,0.45,0.75,\"fern\"")
ns=ns.replace('''def make_tufts(k,seed,cell,n=9,R=0.6,Hs=(0.8,1.2),W=0.8,pairs=2):
    rng=random.Random(seed); nfn,aofn=plant_fns(H=max(Hs),ao_lo=0.62,radw=0.35)
    for i in range(n):
        a=rng.uniform(0,6.28); d=R*math.sqrt(rng.random()); c=Vector((math.cos(a)*d,math.sin(a)*d,-0.02))''','''def make_tufts(k,seed,cell,n=9,R=0.6,Hs=(0.8,1.2),W=0.8,pairs=2,c0=(0,0,0)):
    rng=random.Random(seed); C0=Vector(c0); nfn,aofn=plant_fns(center=C0,H=max(Hs),ao_lo=0.62,radw=0.35)
    for i in range(n):
        a=rng.uniform(0,6.28); d=R*math.sqrt(rng.random()); c=C0+Vector((math.cos(a)*d,math.sin(a)*d,-0.02))''')
ns=ns.replace('''    sub=NK(); make_fern(sub,seed+5,n=6,Hs=(0.6,0.9))
    k.wind_fn=lambda p: 0.0
    return sub''','''    make_fern(k,seed+5,n=6,Hs=(0.6,0.9),c=(L*0.3,0.62,0))
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z-0.3))''')
ns=ns.replace('''    sub=NK(); make_tufts(sub,seed+3,"reeds",n=9,R=0.8,Hs=(1.3,1.8),W=0.7)
    return sub''','''    make_tufts(k,seed+3,"reeds",n=8,R=0.7,Hs=(1.3,1.8),W=0.7,c0=(math.cos(3.6)*R*0.95,math.sin(3.6)*R*0.95,0))
    make_tufts(k,seed+4,"reeds",n=5,R=0.5,Hs=(1.1,1.5),W=0.7,c0=(math.cos(0.9)*R*1.0,math.sin(0.9)*R*1.0,0))
    k.wind_fn=lambda p: min(1.0,max(0.0,p.z/1.8))''')
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
import time
builds=[
 ("SM_VK_Tree_Willow",lambda k: make_willow(k,51),{}),
 ("SM_VK_Tree_Pine_Young",lambda k: make_pine(k,29,H=5.0,Rmax_f=0.3,young=True),{}),
 ("SM_VK_Bush_Round",lambda k: make_bush(k,101,[("broadleaf_dark",0.7),("broadleaf",0.3)]),{}),
 ("SM_VK_Bush_Large",lambda k: make_bush(k,103,[("broadleaf_dark",0.6),("broadleaf",0.4)],R=1.5,H=1.8,nclump=6,cards=24,size=(0.8,1.15)),{}),
 ("SM_VK_Bush_Berry",lambda k: make_bush(k,105,[("berry",0.75),("broadleaf_dark",0.25)]),{}),
 ("SM_VK_Bush_Hydrangea",lambda k: make_bush(k,107,[("hydrangea",0.75),("broadleaf_dark",0.25)],R=1.0,H=1.2),{}),
 ("SM_VK_Bush_Autumn",lambda k: make_bush(k,109,[("autumn_orange",0.5),("autumn_red",0.5)]),{}),
 ("SM_VK_Plant_Fern",lambda k: make_fern(k,111),{"bark_ao":None}),
 ("SM_VK_Plant_Reeds",lambda k: make_tufts(k,113,"reeds",n=10,R=0.7,Hs=(1.3,1.9),W=0.7),{"bark_ao":None}),
 ("SM_VK_Plant_TallGrass",lambda k: make_tufts(k,115,"tallgrass",n=10,R=0.7,Hs=(0.7,1.1),W=0.9),{"bark_ao":None}),
 ("SM_VK_Plant_Wildflowers",lambda k: make_tufts(k,117,"wildflowers",n=12,R=0.9,Hs=(0.5,0.75),W=0.9),{"bark_ao":None}),
 ("SM_VK_Mushrooms_Red",lambda k: make_mushrooms(k,121,"red"),{"bark_ao":None}),
 ("SM_VK_Mushrooms_Brown",lambda k: make_mushrooms(k,123,"brown"),{"bark_ao":None}),
 ("SM_VK_Mushrooms_Glow",lambda k: make_mushrooms(k,125,"glow"),{"bark_ao":None}),
 ("SM_VK_Stump",lambda k: make_stump(k,131),{"bark_ao":(0.7,0.4)}),
 ("SM_VK_Log_Fallen",lambda k: make_log(k,133),{"bark_ao":(0.7,0.4)}),
 ("SM_VK_Rock_Boulder_A",lambda k: boulder(k,(0,0,-0.1),(1.8,1.4,1.3),141),{"sharp":math.radians(40),"bark_ao":(0.72,0.5)}),
 ("SM_VK_Rock_Boulder_B",lambda k: boulder(k,(0,0,-0.15),(2.8,2.2,1.9),143,cuts=9),{"sharp":math.radians(40),"bark_ao":(0.72,0.6)}),
 ("SM_VK_Rock_Boulder_Flat",lambda k: boulder(k,(0,0,-0.1),(2.4,1.7,0.8),145,cuts=6,flat_bottom=0.5),{"sharp":math.radians(40),"bark_ao":(0.72,0.4)}),
 ("SM_VK_Rock_Small_A",lambda k: boulder(k,(0,0,-0.05),(0.6,0.5,0.4),147,mi=ROCK,cuts=5,sub=2),{"sharp":math.radians(40),"bark_ao":(0.75,0.3)}),
 ("SM_VK_Rock_Small_B",lambda k: boulder(k,(0,0,-0.05),(0.5,0.45,0.55),149,mi=ROCK,cuts=5,sub=2),{"sharp":math.radians(40),"bark_ao":(0.75,0.3)}),
 ("SM_VK_Rock_Cluster",lambda k: make_rock_cluster(k,151),{"sharp":math.radians(40),"bark_ao":(0.72,0.5)}),
 ("SM_VK_Rock_Pebbles",lambda k: make_pebbles(k,153),{"sharp":math.radians(40),"bark_ao":(0.8,0.2)}),
 ("SM_VK_Rock_StepStones",lambda k: make_stepstones(k,155),{"sharp":math.radians(40),"bark_ao":(0.8,0.2)}),
 ("SM_VK_Rock_Outcrop",lambda k: make_outcrop(k,157),{"sharp":math.radians(40),"bark_ao":(0.7,1.2)}),
 ("SM_VK_Rock_Standing",lambda k: make_standing_stone(k,159),{"sharp":math.radians(40),"bark_ao":(0.72,0.6)}),
 ("SM_VK_Pond",lambda k: make_pond(k,161),{"bark_ao":(0.75,0.3)}),
]
for n,fn,kw in builds:
    t0=time.time(); k=NK(); fn(k); o=nk_finish(k,n,NC,**kw); print(n,len(o.data.polygons),[m.name[5:] for m in o.data.materials],round(time.time()-t0,2))
# ---- result ----
# {"result":"Code executed successfully: SM_VK_Tree_Willow 1150 ['BarkOak', 'Leaves'] 0.03\nSM_VK_Tree_Pine_Young 3663 ['BarkPine', 'Leaves'] 0.09\nSM_V
# K_Bush_Round 342 ['Wood', 'Leaves'] 0.01\nSM_VK_Bush_Large 558 ['Wood', 'Leaves'] 0.01\nSM_VK_Bush_Berry 330 ['Wood', 'Leaves'] 0.01\nSM_VK_Bush_Hydra
# ngea 358 ['Wood', 'Leaves'] 0.01\nSM_VK_Bush_Autumn 354 ['Wood', 'Leaves'] 0.01\nSM_VK_Plant_Fern 72 ['Leaves'] 0.0\nSM_VK_Plant_Reeds 80 ['Leaves'] 0
# .0\nSM_VK_Plant_TallGrass 80 ['Leaves'] 0.0\nSM_VK_Plant_Wildflowers 96 ['Leaves'] 0.0\nSM_VK_Mushrooms_Red 1224 ['MushRed', 'MushStem'] 0.03\nSM_VK_M
# ushrooms_Brown 564 ['MushBrown', 'MushStem'] 0.02\nSM_VK_Mushrooms_Glow 658 ['MushStem', 'MushGlow'] 0.02\nSM_VK_Stump 421 ['BarkMossy', 'EndGrain', '
# MushBrown', 'MushStem'] 0.01\nSM_VK_Log_Fallen 657 ['Leaves', 'BarkMossy', 'EndGrain', 'MushBrown', 'MushStem'] 0.02\nSM_VK_Rock_Boulder_A 320 ['RockM

# ==============================================================================================================
# [0232] 2026-09-23 11:07:31  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
S=bpy.data.collections["VK_NatureTest"]
for ob in list(S.objects):
    if ob.name.startswith(("row1_","row2_")): bpy.data.objects.remove(ob)
row1=["SM_VK_Bush_Round","SM_VK_Bush_Large","SM_VK_Bush_Berry","SM_VK_Bush_Hydrangea","SM_VK_Bush_Autumn","SM_VK_Plant_Fern","SM_VK_Plant_Reeds",
      "SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers","SM_VK_Mushrooms_Red","SM_VK_Mushrooms_Brown","SM_VK_Mushrooms_Glow","SM_VK_Stump","SM_VK_Log_Fallen"]
row2=["SM_VK_Rock_Boulder_A","SM_VK_Rock_Boulder_B","SM_VK_Rock_Boulder_Flat","SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Cluster",
      "SM_VK_Rock_Pebbles","SM_VK_Rock_StepStones","SM_VK_Rock_Standing","SM_VK_Rock_Outcrop","SM_VK_Pond"]
def lay(names,y,prefix,x0=600.0,gap=0.6):
    x=x0
    for n in names:
        me=bpy.data.objects[n].data; xs=[v.co.x for v in me.vertices]
        ob=bpy.data.objects.new(prefix+n,me); S.objects.link(ob); ob.location=(x-min(xs),y,0); x+=max(xs)-min(xs)+gap
    return x-x0
W1=lay(row1,-40,"row1_"); W2=lay(row2,-55,"row2_",gap=1.0)
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]; cn.data.lens=30
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
g=bpy.data.objects["VK_Ground"]; g.location=(640,-45,0); g.scale=(6,6,1)
SC.render.resolution_percentage=60
tgt=Vector((600+W1/2,-40,0.6)); cn.location=tgt+Vector((0,-W1*0.62,W1*0.22))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_row1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
tgt=Vector((600+W2/2,-55,1.0)); cn.location=tgt+Vector((0,-W2*0.6,W2*0.28))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_row2.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
print(W1,W2)
# ---- result ----
# {"result":"Code executed successfully: 37.43361009061368 41.712711945176125\n"}

# ==============================================================================================================
# [0233] 2026-09-23 11:07:52  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]; cn.data.lens=35
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
def ob(n,p): return bpy.data.objects[p+n]
def shot(a,b,prefix,y,fname,h=0.7,back=1.0):
    xa=ob(a,prefix).location.x; xb=ob(b,prefix).location.x
    me=bpy.data.objects[b].data; wb=max(v.co.x for v in me.vertices)-min(v.co.x for v in me.vertices)
    cx=(xa+xb+wb)/2; W=(xb+wb)-xa
    tgt=Vector((cx,y,h)); cn.location=tgt+Vector((0,-W*0.85*back,W*0.2*back))
    cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
    SC.render.filepath=os.path.join(out,fname); bpy.ops.render.render(write_still=True,scene=SC.name)
shot("SM_VK_Bush_Round","SM_VK_Plant_Fern","row1_",-40,"_row1a.png",h=0.8)
shot("SM_VK_Plant_Reeds","SM_VK_Log_Fallen","row1_",-40,"_row1b.png",h=0.5)
shot("SM_VK_Rock_Boulder_A","SM_VK_Rock_StepStones","row2_",-55,"_row2a.png",h=0.6)
shot("SM_VK_Rock_Standing","SM_VK_Pond","row2_",-55,"_row2b.png",h=1.2)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0234] 2026-09-23 11:08:49  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_leafgen"]; s=t.as_string()
s=s.replace('''    pal=[(0.10,0.28,0.08),(0.14,0.33,0.10),(0.18,0.38,0.12),(0.08,0.24,0.08)]
    B,pts=cell_broad(P,"berry"''','''    pal=[(0.16,0.40,0.12),(0.21,0.46,0.14),(0.26,0.52,0.17),(0.13,0.34,0.11)]
    B,pts=cell_broad(P,"berry"''')
s=s.replace("    blades(P,B,rng,34,(300,490),(7,11),0.14,[(0.26,0.40,0.18),(0.32,0.46,0.20),(0.22,0.36,0.16)])",
            "    blades(P,B,rng,34,(300,490),(7,11),0.14,[(0.36,0.54,0.22),(0.44,0.60,0.26),(0.30,0.48,0.20)])")
s=s.replace("    cols=[(0.40,0.56,0.17),(0.52,0.60,0.24),(0.60,0.64,0.30),(0.32,0.50,0.14)]\n    blades(P,B,rng,60,(180,420),(5,9),0.36,cols)",
            "    cols=[(0.50,0.68,0.21),(0.62,0.72,0.29),(0.70,0.74,0.36),(0.42,0.62,0.18)]\n    blades(P,B,rng,60,(180,420),(5,9),0.36,cols)")
t.clear(); t.write(s)
exec(bpy.data.texts["vk_tex"].as_string()); exec(bpy.data.texts["vk_texgen"].as_string()); exec(s)
P=paint_leaf_atlas(); save_leaf_atlas(P); write_map("T_VK_Leaves_H",blur(P.h,0.8),True)
exec(bpy.data.texts["vk_mat"].as_string())
mt=bpy.data.texts["vk_mat"]; ms=mt.as_string()
ms=ms.replace('''    mossy_material("M_VK_RockMossy","T_VK_Rock",base_tile=1.5)''','''    mossy_material("M_VK_RockMossy","T_VK_Rock",base_tile=1.5,thresh=0.66,soft=0.12,noise_amt=0.75)''')
mt.clear(); mt.write(ms); exec(ms)
mossy_material("M_VK_RockMossy","T_VK_Rock",base_tile=1.5,thresh=0.66,soft=0.12,noise_amt=0.75)
b=next(n for n in bpy.data.materials["M_VK_MushGlow"].node_tree.nodes if n.type=="BSDF_PRINCIPLED")
b.inputs["Emission Strength"].default_value=1.6; b.inputs["Emission Color"].default_value=(0.1,0.75,1.0,1)
mx=next(n for n in bpy.data.materials["M_VK_MushGlow"].node_tree.nodes if n.type=="MIX"); mx.inputs[6].default_value=(0.2,0.7,0.95,1)
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace("def plant_fns(center=Vector((0,0,0)),H=1.0,ao_lo=0.62,radw=0.45):","def plant_fns(center=Vector((0,0,0)),H=1.0,ao_lo=0.76,radw=0.45):")
ns=ns.replace("    rng=random.Random(seed); C0=Vector(c); nfn,aofn=plant_fns(center=C0,H=1.0,ao_lo=0.6,radw=0.6)","    rng=random.Random(seed); C0=Vector(c); nfn,aofn=plant_fns(center=C0,H=1.0,ao_lo=0.72,radw=0.6)")
ns=ns.replace("    rng=random.Random(seed); C0=Vector(c0); nfn,aofn=plant_fns(center=C0,H=max(Hs),ao_lo=0.62,radw=0.35)","    rng=random.Random(seed); C0=Vector(c0); nfn,aofn=plant_fns(center=C0,H=max(Hs),ao_lo=0.78,radw=0.35)")
ns=ns.replace("    for (c,r) in cl: clump_cards(k,c,r,cards,cells,rng,C,ext,size=size,shell=(0.2,0.9),ao_lo=0.55)","    for (c,r) in cl: clump_cards(k,c,r,cards,cells,rng,C,ext,size=size,shell=(0.2,0.9),ao_lo=0.62)")
ns=ns.replace("    boulder(k,(0,0,-0.2),(0.95,0.62,H+0.2),seed,cuts=6,flat_bottom=0.9,rot=rng.uniform(0,6.28),lean=rng.uniform(-0.06,0.06),tile=1.5)",
              "    boulder(k,(0,0,-0.2),(1.0,0.66,H+0.2),seed,cuts=12,flat_bottom=0.9,rot=rng.uniform(0,6.28),lean=rng.uniform(-0.06,0.06),tile=1.5)")
ns=ns.replace('''    layers=[(0.0,4.8,3.4,1.3),(1.1,4.0,2.8,1.1),(2.0,2.8,2.2,1.0),(2.8,1.8,1.5,0.8)]
    for i,(z,sx,sy,sz) in enumerate(layers):
        off=Vector((rng.uniform(-0.4,0.4),rng.uniform(-0.3,0.3),z-0.15))
        boulder(k,off,(sx,sy,sz*1.15),seed*10+i,cuts=9,flat_bottom=0.5,rot=rng.uniform(-0.3,0.3))''','''    layers=[(0.0,5.0,3.6,1.5,0.0),(1.2,3.6,2.9,1.3,0.12),(2.2,2.6,2.0,1.2,-0.1),(3.0,1.4,1.3,0.9,0.2)]
    for i,(z,sx,sy,sz,ln) in enumerate(layers):
        off=Vector((rng.uniform(-0.6,0.6),rng.uniform(-0.4,0.4),z-0.2))
        boulder(k,off,(sx,sy,sz*1.2),seed*10+i,cuts=11,flat_bottom=0.45,rot=rng.uniform(-0.6,0.6),lean=ln)''')
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
for n,fn,kw in [("SM_VK_Rock_Standing",lambda k: make_standing_stone(k,159),{"sharp":math.radians(40),"bark_ao":(0.72,0.6)}),
                ("SM_VK_Rock_Outcrop",lambda k: make_outcrop(k,157),{"sharp":math.radians(40),"bark_ao":(0.7,1.2)}),
                ("SM_VK_Bush_Round",lambda k: make_bush(k,101,[("broadleaf_dark",0.7),("broadleaf",0.3)]),{}),
                ("SM_VK_Bush_Large",lambda k: make_bush(k,103,[("broadleaf_dark",0.6),("broadleaf",0.4)],R=1.5,H=1.8,nclump=6,cards=24,size=(0.8,1.15)),{}),
                ("SM_VK_Bush_Berry",lambda k: make_bush(k,105,[("berry",0.75),("broadleaf_dark",0.25)]),{}),
                ("SM_VK_Bush_Hydrangea",lambda k: make_bush(k,107,[("hydrangea",0.75),("broadleaf_dark",0.25)],R=1.0,H=1.2),{}),
                ("SM_VK_Bush_Autumn",lambda k: make_bush(k,109,[("autumn_orange",0.5),("autumn_red",0.5)]),{}),
                ("SM_VK_Plant_Fern",lambda k: make_fern(k,111),{"bark_ao":None}),
                ("SM_VK_Plant_Reeds",lambda k: make_tufts(k,113,"reeds",n=10,R=0.7,Hs=(1.3,1.9),W=0.7),{"bark_ao":None}),
                ("SM_VK_Plant_TallGrass",lambda k: make_tufts(k,115,"tallgrass",n=10,R=0.7,Hs=(0.7,1.1),W=0.9),{"bark_ao":None}),
                ("SM_VK_Plant_Wildflowers",lambda k: make_tufts(k,117,"wildflowers",n=12,R=0.9,Hs=(0.5,0.75),W=0.9),{"bark_ao":None}),
                ("SM_VK_Log_Fallen",lambda k: make_log(k,133),{"bark_ao":(0.7,0.4)}),
                ("SM_VK_Pond",lambda k: make_pond(k,161),{"bark_ao":(0.75,0.3)})]:
    k=NK(); fn(k); o=nk_finish(k,n,NC,**kw)
import os
SC=bpy.data.scenes["VillageKit"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.filepath=os.path.join(out,"_row2b.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0235] 2026-09-23 11:09:08  blender  ok
# ==============================================================================================================
import bpy
for img in bpy.data.images:
    if img.name.startswith("T_VK") and img.has_data and not img.packed_file:
        try: img.pack()
        except Exception as e: print(img.name,e)
bpy.ops.wm.save_mainfile(); import os; print(round(os.path.getsize(bpy.data.filepath)/1e6,1),"MB")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n174.2 MB\n"}

# ==============================================================================================================
# [0236] 2026-09-23 11:09:46  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def build_glade(coll,C=(700.0,0.0),seed=7):
    cx,cy=C; rng=random.Random(seed); O=(0,0,0)
    placed=[]
    def P(name,x,y,rot=None,scale=1.0,rec=True,r=1.0):
        rot=rng.uniform(0,360) if rot is None else rot
        o=place_v(coll,name,cx+x,cy+y,0,rot,O,{})
        o.scale=(scale,scale,scale)
        if rec: placed.append((x,y,r*scale))
        return o
    # pond + willow
    P("SM_VK_Pond",-6,2,rot=10,r=3.2)
    P("SM_VK_Tree_Willow",-10.5,6.5,rot=40,r=3.5)
    P("SM_VK_Rock_StepStones",-1.2,-3.2,rot=-25,r=1.0)
    # stone circle on the right
    sc=(12.0,6.0)
    for i in range(7):
        a=i*2*math.pi/7+0.3; R=4.6
        o=P("SM_VK_Rock_Standing",sc[0]+math.cos(a)*R,sc[1]+math.sin(a)*R,rot=math.degrees(a)+90,scale=rng.uniform(0.8,1.1),r=0.8)
    P("SM_VK_Rock_Boulder_Flat",sc[0],sc[1],rot=20,scale=0.8,r=1.3)
    # outcrop + dead tree
    P("SM_VK_Rock_Outcrop",4.5,17,rot=200,r=3.2)
    P("SM_VK_Tree_Dead",9.0,15.5,rot=60,r=1.0)
    # forest layers behind
    back=[("SM_VK_Tree_Pine_B",-18,20),("SM_VK_Tree_Pine_A",-12,22),("SM_VK_Tree_Pine_A",-4,24),("SM_VK_Tree_Pine_B",14,24),("SM_VK_Tree_Pine_A",21,21),
          ("SM_VK_Tree_Pine_Young",-7,17),("SM_VK_Tree_Pine_Young",18,16),("SM_VK_Tree_Pine_B",26,14),("SM_VK_Tree_Pine_A",-24,12)]
    for n,x,y in back: P(n,x,y,r=2.5)
    mid=[("SM_VK_Tree_Oak_A",-17,10),("SM_VK_Tree_Oak_B",1,12),("SM_VK_Tree_Birch",-2,6.5),("SM_VK_Tree_Birch_Single",20,4),
         ("SM_VK_Tree_Oak_Autumn",24,-2),("SM_VK_Tree_Blossom",6.5,-2.5),("SM_VK_Tree_Birch_Single",-15,-1),("SM_VK_Tree_Oak_A",-24,1),("SM_VK_Tree_Apple",15,-8),
         ("SM_VK_Tree_Sapling",3,-8)]
    for n,x,y in mid: P(n,x,y,r=2.2)
    # log, stump, rocks
    P("SM_VK_Log_Fallen",1.5,2.0,rot=-30,r=1.8); P("SM_VK_Stump",-3.5,9.5,r=0.7)
    P("SM_VK_Rock_Boulder_A",-13,-5,r=1.0); P("SM_VK_Rock_Boulder_B",27,6,r=1.5); P("SM_VK_Rock_Cluster",10,-6,r=1.4)
    P("SM_VK_Rock_Small_A",-3,-6); P("SM_VK_Rock_Small_B",4,-5.5); P("SM_VK_Rock_Pebbles",-9,-3,r=1.2)
    # bushes
    for n,x,y in [("SM_VK_Bush_Large",-20,6),("SM_VK_Bush_Round",-8,11),("SM_VK_Bush_Berry",5,7),("SM_VK_Bush_Hydrangea",-14,3),
                  ("SM_VK_Bush_Autumn",21,1),("SM_VK_Bush_Round",17,11),("SM_VK_Bush_Berry",-22,-4),("SM_VK_Bush_Large",8,20)]:
        P(n,x,y,r=1.3)
    # mushrooms near log / stump / trees
    for n,x,y in [("SM_VK_Mushrooms_Red",2.8,3.2),("SM_VK_Mushrooms_Brown",-3.0,10.6),("SM_VK_Mushrooms_Glow",-16.2,11.2),("SM_VK_Mushrooms_Red",-1.2,7.8),("SM_VK_Mushrooms_Glow",3.0,15.5)]:
        P(n,x,y,r=0.3)
    # ground scatter: ferns under trees, grass & flowers in the open
    def free(x,y,r):
        return all((x-px)**2+(y-py)**2>(r+pr)**2 for px,py,pr in placed)
    for kind,cnt,rad,zone in (("SM_VK_Plant_Fern",26,0.6,"shade"),("SM_VK_Plant_TallGrass",30,0.6,"open"),("SM_VK_Plant_Wildflowers",22,0.7,"open"),("SM_VK_Plant_Reeds",0,0.6,"open")):
        n=0; tries=0
        while n<cnt and tries<3000:
            tries+=1
            x=rng.uniform(-26,28); y=rng.uniform(-10,24)
            if zone=="shade" and y<5: continue
            if zone=="open" and y>14: continue
            if not free(x,y,rad): continue
            P(kind,x,y,scale=rng.uniform(0.8,1.25),r=rad); n+=1
    # reeds around the pond edge
    for i in range(6):
        a=rng.uniform(0,6.28); P("SM_VK_Plant_Reeds",-6+math.cos(a)*3.4,2+math.sin(a)*3.0,scale=rng.uniform(0.8,1.1),rec=False)
'''
bpy.data.texts["vk_nature"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(bpy.data.texts["vk_nature"].as_string())
G=vcol("VK_Glade")
for o in list(G.objects): bpy.data.objects.remove(o)
for o in bpy.data.collections["VK_NatureTest"].objects: o.hide_render=True
build_glade(G)
for o in G.objects: o.hide_render=False
print(len(G.objects))
g=bpy.data.objects["VK_Ground"]; g.location=(700,5,0); g.scale=(6,6,1)
import os
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]; cn.data.lens=26
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
tgt=Vector((702,6,2.5)); cn.location=Vector((696,-22,6.5))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.camera=cn; SC.render.resolution_percentage=60
SC.render.filepath=os.path.join(out,"_glade1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: 137\n"}

# ==============================================================================================================
# [0237] 2026-09-23 11:10:12  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace('("SM_VK_Tree_Blossom",6.5,-2.5)','("SM_VK_Tree_Blossom",-19,-6)').replace('("SM_VK_Tree_Sapling",3,-8)','("SM_VK_Tree_Sapling",24,-9)')
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
G=vcol("VK_Glade")
for o in list(G.objects): bpy.data.objects.remove(o)
build_glade(G)
for o in G.objects: o.hide_render=False
import os
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=60
shots=[("_glade_hero",(697,6,3.2),(700,-13,2.2),24),("_glade_circle",(711,7,1.6),(724,-6,3.2),28),
       ("_glade_aerial",(701,6,0),(716,-38,34),26),("_glade_floor",(701.5,3,0.6),(706.5,-3.5,1.6),30)]
for name,tgt,loc,lens in shots:
    cn.data.lens=lens; cn.location=Vector(loc); cn.rotation_euler=(Vector(tgt)-cn.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=cn; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0238] 2026-09-23 11:10:56  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace("def boulder(k,c,size,seed,mi=None,cuts=7,sub=3,flat_bottom=0.3,tile=1.5,rot=0.0,lean=0.0):",
              "def boulder(k,c,size,seed,mi=None,cuts=7,sub=3,flat_bottom=0.3,tile=1.5,rot=0.0,lean=0.0,extra_cuts=(),cut_range=(0.6,0.84)):")
ns=ns.replace("        n=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-0.2,1))).normalized(); off=rnd.uniform(0.6,0.84)",
              "        n=Vector((rnd.uniform(-1,1),rnd.uniform(-1,1),rnd.uniform(-0.2,1))).normalized(); off=rnd.uniform(*cut_range)")
ns=ns.replace('''    for v in vs:
        if v.co.z<-flat_bottom: v.co.z=-flat_bottom+(v.co.z+flat_bottom)*0.05
    M=Matrix.Translation(Vector(c))''','''    for (en,eo) in extra_cuts:
        en=Vector(en).normalized()
        for v in vs:
            dd=v.co.dot(en)
            if dd>eo: v.co-=en*(dd-eo)
    for v in vs:
        if v.co.z<-flat_bottom: v.co.z=-flat_bottom+(v.co.z+flat_bottom)*0.05
    M=Matrix.Translation(Vector(c))''')
ns=ns.replace('''    boulder(k,(0,0,-0.2),(1.0,0.66,H+0.2),seed,cuts=12,flat_bottom=0.9,rot=rng.uniform(0,6.28),lean=rng.uniform(-0.06,0.06),tile=1.5)''',
'''    sl=rng.choice((-1,1))
    boulder(k,(0,0,-0.2),(1.25,0.55,H+0.2),seed,cuts=10,flat_bottom=0.9,rot=rng.uniform(0,6.28),lean=rng.uniform(-0.05,0.05),tile=1.2,
            extra_cuts=[((0,1,0),0.62),((0,-1,0),0.62),((sl*0.55,0,1),0.72),((1,0,0),0.8),((-1,0,0),0.8)],cut_range=(0.55,0.8))''')
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
k=NK(); make_standing_stone(k,159); nk_finish(k,"SM_VK_Rock_Standing",NC,sharp=math.radians(35),bark_ao=(0.72,0.6))
k=NK(); make_standing_stone(k,163,H=2.4); nk_finish(k,"SM_VK_Rock_Standing_B",NC,sharp=math.radians(35),bark_ao=(0.72,0.6))
ns=tn.as_string()
ns=ns.replace('''        o=P("SM_VK_Rock_Standing",sc[0]+math.cos(a)*R,sc[1]+math.sin(a)*R,rot=math.degrees(a)+90,scale=rng.uniform(0.8,1.1),r=0.8)''',
              '''        o=P("SM_VK_Rock_Standing" if i%2==0 else "SM_VK_Rock_Standing_B",sc[0]+math.cos(a)*R,sc[1]+math.sin(a)*R,rot=math.degrees(a)+90,scale=rng.uniform(0.85,1.1),r=0.8)''')
tn.clear(); tn.write(ns); exec(ns)
G=vcol("VK_Glade")
for o in list(G.objects): bpy.data.objects.remove(o)
build_glade(G)
for o in G.objects: o.hide_render=False
import os
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cn.data.lens=28; tgt=Vector((712,7,1.6)); cn.location=Vector((713.5,-9.5,3.6))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_glade_circle.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0239] 2026-09-23 11:11:16  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
cn.data.lens=26; tgt=Vector((712.5,6.5,1.3)); cn.location=Vector((703.0,-3.5,3.4))
cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
SC.render.filepath=os.path.join(out,"_glade_circle.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0240] 2026-09-23 11:11:47  blender  ok
# ==============================================================================================================
import bpy, os, math
from mathutils import Vector
S=bpy.data.collections["VK_NatureTest"]
for ob in list(S.objects): bpy.data.objects.remove(ob)
for o in bpy.data.collections["VK_Glade"].objects: o.hide_render=True
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
def bounds(n):
    me=bpy.data.objects[n].data; xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return min(xs),max(xs),min(ys),max(ys),max(zs)
def sheet(rows,origin,fname,gap=1.0,rowgap=2.0,pitch=14,lens=35,zfrac=0.45):
    ox,oy=origin; y=oy; allx=[];zmax=0; objs=[]
    for row in rows:
        x=ox; depth=0
        for n in row:
            mnx,mxx,mny,mxy,mz=bounds(n)
            ob=bpy.data.objects.new("cat_"+n,bpy.data.objects[n].data); S.objects.link(ob)
            ob.location=(x-mnx,y-mny,0); x+=mxx-mnx+gap; depth=max(depth,mxy-mny); zmax=max(zmax,mz); allx.append(x-gap)
            objs.append(ob)
        y+=depth+rowgap
    # center rows horizontally
    W=max(allx)-ox
    for row_objs in []: pass
    cxm=ox+W/2; cym=(oy+y)/2
    g=bpy.data.objects["VK_Ground"]; g.location=(cxm,cym,0); g.scale=(8,8,1)
    fov=2*math.atan(18/lens); d=(W/2)/math.tan(fov/2)*1.08
    tgt=Vector((cxm,cym,zmax*zfrac)); p=math.radians(pitch)
    cn.data.lens=lens; cn.location=tgt+Vector((0,-d*math.cos(p),d*math.sin(p)))
    cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=cn; SC.render.resolution_percentage=100
    SC.render.filepath=os.path.join(out,fname); bpy.ops.render.render(write_still=True,scene=SC.name)
    return objs
trees=[["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Oak_Autumn","SM_VK_Tree_Apple","SM_VK_Tree_Blossom","SM_VK_Tree_Sapling","SM_VK_Tree_Dead"],
       ["SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Birch","SM_VK_Tree_Birch_Single","SM_VK_Tree_Willow"]]
o1=sheet(trees,(800,0),"nature_catalog_trees.png",gap=1.2,rowgap=3,pitch=10,zfrac=0.4)
for o in o1: o.hide_render=True
plants=[["SM_VK_Bush_Round","SM_VK_Bush_Large","SM_VK_Bush_Berry","SM_VK_Bush_Hydrangea","SM_VK_Bush_Autumn","SM_VK_Stump","SM_VK_Log_Fallen"],
        ["SM_VK_Plant_Fern","SM_VK_Plant_Reeds","SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers","SM_VK_Mushrooms_Red","SM_VK_Mushrooms_Brown","SM_VK_Mushrooms_Glow"]]
o2=sheet(plants,(800,-100),"nature_catalog_plants.png",gap=0.8,rowgap=1.2,pitch=24,zfrac=0.35)
for o in o2: o.hide_render=True
rocks=[["SM_VK_Rock_Boulder_A","SM_VK_Rock_Boulder_B","SM_VK_Rock_Boulder_Flat","SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Standing","SM_VK_Rock_Standing_B"],
       ["SM_VK_Rock_Cluster","SM_VK_Rock_Pebbles","SM_VK_Rock_StepStones","SM_VK_Rock_Outcrop","SM_VK_Pond"]]
o3=sheet(rocks,(800,-200),"nature_catalog_rocks.png",gap=1.0,rowgap=1.5,pitch=26,zfrac=0.3)
for o in o3: o.hide_render=True
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0241] 2026-09-23 11:12:31  blender  ok
# ==============================================================================================================
import bpy, os, math
from mathutils import Vector
S=bpy.data.collections["VK_NatureTest"]
for ob in list(S.objects): bpy.data.objects.remove(ob)
SC=bpy.data.scenes["VillageKit"]; cn=bpy.data.objects["VK_CameraNature"]
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
def bounds(n):
    me=bpy.data.objects[n].data; xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return min(xs),max(xs),min(ys),max(ys),max(zs)
def sheet(rows,origin,fname,gap=1.0,rowgap=2.0,pitch=14,lens=35,zfrac=0.45,margin=1.3):
    ox,oy=origin; y=oy; widths=[]; zmax=0; objs=[]; rowobjs=[]
    for row in rows:
        x=ox; depth=0; ro=[]
        for n in row:
            mnx,mxx,mny,mxy,mz=bounds(n)
            ob=bpy.data.objects.new("cat_"+n,bpy.data.objects[n].data); S.objects.link(ob)
            ob.location=(x-mnx,y-mny,0); x+=mxx-mnx+gap; depth=max(depth,mxy-mny); zmax=max(zmax,mz); ro.append(ob)
        widths.append(x-gap-ox); rowobjs.append(ro); objs+=ro
        y+=depth+rowgap
    W=max(widths)
    for ro,w in zip(rowobjs,widths):
        for ob in ro: ob.location.x+=(W-w)/2
    cxm=ox+W/2; cym=(oy+y)/2
    g=bpy.data.objects["VK_Ground"]; g.location=(cxm,cym,0); g.scale=(10,10,1)
    fov=2*math.atan(18/lens); d=(W/2)/math.tan(fov/2)*margin
    tgt=Vector((cxm,cym,zmax*zfrac)); p=math.radians(pitch)
    cn.data.lens=lens; cn.location=tgt+Vector((0,-d*math.cos(p),d*math.sin(p)))
    cn.rotation_euler=(tgt-cn.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=cn; SC.render.resolution_percentage=100
    SC.render.filepath=os.path.join(out,fname); bpy.ops.render.render(write_still=True,scene=SC.name)
    for o in objs: o.hide_render=True
sheet([["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","SM_VK_Tree_Oak_Autumn","SM_VK_Tree_Apple","SM_VK_Tree_Blossom","SM_VK_Tree_Sapling","SM_VK_Tree_Dead"]],(800,0),"nature_catalog_trees_broadleaf.png",gap=1.0,pitch=6,zfrac=0.5,margin=1.12)
sheet([["SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Birch","SM_VK_Tree_Birch_Single","SM_VK_Tree_Willow"]],(800,50),"nature_catalog_trees_conifer.png",gap=1.0,pitch=6,zfrac=0.5,margin=1.12)
sheet([["SM_VK_Bush_Round","SM_VK_Bush_Large","SM_VK_Bush_Berry","SM_VK_Bush_Hydrangea","SM_VK_Bush_Autumn","SM_VK_Stump","SM_VK_Log_Fallen"],
       ["SM_VK_Plant_Fern","SM_VK_Plant_Reeds","SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers","SM_VK_Mushrooms_Red","SM_VK_Mushrooms_Brown","SM_VK_Mushrooms_Glow"]],
      (800,-100),"nature_catalog_plants.png",gap=0.8,rowgap=1.0,pitch=22,zfrac=0.3,margin=1.35)
sheet([["SM_VK_Rock_Boulder_A","SM_VK_Rock_Boulder_B","SM_VK_Rock_Boulder_Flat","SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Standing","SM_VK_Rock_Standing_B"],
       ["SM_VK_Rock_Cluster","SM_VK_Rock_Pebbles","SM_VK_Rock_StepStones","SM_VK_Rock_Outcrop","SM_VK_Pond"]],
      (800,-200),"nature_catalog_rocks.png",gap=1.0,rowgap=1.5,pitch=24,zfrac=0.3,margin=1.3)
for f in ("nature_catalog_trees.png",):
    p=os.path.join(out,f)
    if os.path.exists(p): os.remove(p)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0242] 2026-09-23 11:12:55  blender  ok
# ==============================================================================================================
import bpy
tn=bpy.data.texts["vk_nature"]; ns=tn.as_string()
ns=ns.replace('''def bark_tubes(k,branches,mi,segs=(14,9,6,4),flare=None,tile=1.2):
    for b in branches:
        d=b["depth"]; sg=segs[min(d,len(segs)-1)]
        k.tube(b["pts"],b["rad"],sg,mi,''','''def bark_tubes(k,branches,mi,segs=(14,9,6,4),flare=None,tile=1.2):
    for b in branches:
        d=b["depth"]; sg=segs[min(d,len(segs)-1)]
        mid=mi[min(d,len(mi)-1)] if isinstance(mi,(tuple,list)) else mi
        k.tube(b["pts"],b["rad"],sg,mid,''')
ns=ns.replace("    bark_tubes(k,B,BARK_PINE,segs=(12,3,3,3),flare=root_flare(6,0.45,0.35,0.18),tile=1.4)",
              "    bark_tubes(k,B,(BARK_PINE,BARK_OAK),segs=(12,3,3,3),flare=root_flare(6,0.45,0.35,0.18),tile=1.4)")
tn.clear(); tn.write(ns)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(ns)
NC=vcol("VK_NaturePieces")
for n,fn in [("SM_VK_Tree_Pine_A",lambda k: make_pine(k,21,H=10.0)),("SM_VK_Tree_Pine_B",lambda k: make_pine(k,27,H=13.0,Rmax_f=0.26)),
             ("SM_VK_Tree_Pine_Young",lambda k: make_pine(k,29,H=5.0,Rmax_f=0.3,young=True))]:
    k=NK(); fn(k); nk_finish(k,n,NC)
# dim the oak bark on pine branches via vertex AO? keep. check materials
print([m.name for m in bpy.data.objects["SM_VK_Tree_Pine_A"].data.materials])
bpy.ops.wm.save_mainfile()
# ---- result ----
# {"result":"Code executed successfully: ['M_VK_BarkOak', 'M_VK_BarkPine', 'M_VK_Leaves']\nInfo: Saved \"medievalDiorama.blend\"\n"}

# ==============================================================================================================
# [0243] 2026-09-23 11:14:01  blender  ok
# ==============================================================================================================
import bpy
code = r'''
def dress_town_nature(coll,C=(200.0,0.0),seed=2029):
    import mathutils
    cx,cy=C; rng=random.Random(seed); O=(0,0,0)
    for o in [o for o in coll.objects if o.name.startswith(("VK_TTree","NT_"))]: bpy.data.objects.remove(o)
    solid=[o.matrix_world.translation.copy() for o in coll.objects if not o.name.startswith(("VK_Town","NT_","VK_TTree"))]
    kd=mathutils.kdtree.KDTree(len(solid))
    for i,p in enumerate(solid): kd.insert((p.x,p.y,0),i)
    kd.balance()
    roads=[((cx-66,cy-22),(cx+66,cy-22),3.6),((cx,cy-11),(cx,cy-64),3.0)]
    def seg_d(p,a,b):
        ax,ay=a; bx,by=b; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
        t=max(0.0,min(1.0,((p[0]-ax)*dx+(p[1]-ay)*dy)/L2)); return math.hypot(p[0]-(ax+t*dx),p[1]-(ay+t*dy))
    def near_road(x,y,m):
        if cx-16<x<cx+16 and cy-13<y<cy+13: return True
        return any(seg_d((x,y),a,b)<w+m for a,b,w in roads)
    placed=[]
    def clear(x,y,build_m,self_m):
        if kd.find((x,y,0))[2]<build_m: return False
        if near_road(x,y,self_m*0.5): return False
        return all((x-px)**2+(y-py)**2>(self_m+pr)**2 for px,py,pr in placed)
    cnt=[0]
    def put(name,x,y,rot=None,s=1.0,r=1.0,rec=True):
        rot=rng.uniform(0,360) if rot is None else rot
        if name=="HERO":
            for part in ("SM_Tree_Wood","SM_Tree_Foliage"):
                o=bpy.data.objects.new(f"NT_{cnt[0]}_{part}",bpy.data.objects[part].data); coll.objects.link(o)
                o.location=(x,y,0); o.rotation_euler=(0,0,math.radians(rot)); o.scale=(s,s,s)
        else:
            o=place_v(coll,name,x,y,0,rot,O,{}); o.name=f"NT_{cnt[0]}_{name[6:]}"; o.scale=(s,s,s)
        cnt[0]+=1
        if rec: placed.append((x,y,r*s))
    # --- landmarks
    pc=(cx+42,cy-53); put("SM_VK_Pond",pc[0],pc[1],rot=15,r=3.3)
    put("SM_VK_Tree_Willow",pc[0]+4.5,pc[1]+4.5,rot=40,r=3.2)
    put("SM_VK_Rock_StepStones",pc[0]-4.5,pc[1]+3.5,rot=60,r=1.0)
    for i in range(3): put("SM_VK_Plant_Reeds",pc[0]+rng.uniform(-3,3),pc[1]-3.4+rng.uniform(-0.3,0.3),rec=False)
    sc=(cx+88,cy+12)
    for i in range(7):
        a=i*2*math.pi/7+0.4
        put("SM_VK_Rock_Standing" if i%2==0 else "SM_VK_Rock_Standing_B",sc[0]+math.cos(a)*4.6,sc[1]+math.sin(a)*4.6,rot=math.degrees(a)+90,s=rng.uniform(0.85,1.1),r=1.0)
    put("SM_VK_Rock_Boulder_Flat",sc[0],sc[1],rot=30,s=0.8,r=1.4)
    put("SM_VK_Rock_Outcrop",cx-84,cy+34,rot=160,r=3.5); put("SM_VK_Tree_Dead",cx-79,cy+31,r=1.0)
    # --- orchard west of the barn
    for i in range(3):
        for j in range(4):
            x=cx-40+i*5.2+rng.uniform(-0.3,0.3); y=cy-50-j*5.2+rng.uniform(-0.3,0.3)
            if clear(x,y,5.0,2.2): put("SM_VK_Tree_Apple",x,y,s=rng.uniform(0.9,1.1),r=2.2)
    # --- blossom trees around the plaza
    n=0
    for k_ in range(80):
        a=rng.uniform(0,6.28); d=rng.uniform(18,26); x=cx+math.cos(a)*d; y=cy+math.sin(a)*d
        if clear(x,y,6.5,3.5): put("SM_VK_Tree_Blossom",x,y,r=3.0); n+=1
        if n>=4: break
    # --- tree zones
    def species(x,y):
        dy=y-cy; dx=abs(x-cx)
        if dy>24: return rng.choices(["SM_VK_Tree_Pine_A","SM_VK_Tree_Pine_B","SM_VK_Tree_Pine_Young","SM_VK_Tree_Oak_A","SM_VK_Tree_Birch","HERO"],[30,25,12,12,12,9])[0]
        if dx>70: return rng.choices(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","HERO","SM_VK_Tree_Birch","SM_VK_Tree_Birch_Single","SM_VK_Tree_Pine_A","SM_VK_Tree_Oak_Autumn"],[20,18,16,14,10,14,8])[0]
        return rng.choices(["SM_VK_Tree_Oak_A","SM_VK_Tree_Oak_B","HERO","SM_VK_Tree_Birch","SM_VK_Tree_Birch_Single","SM_VK_Tree_Oak_Autumn","SM_VK_Tree_Pine_Young","SM_VK_Tree_Dead"],[18,16,20,14,12,8,8,4])[0]
    n=0; tries=0
    while n<150 and tries<30000:
        tries+=1
        x=cx+rng.uniform(-105,105); y=cy+rng.uniform(-100,62)
        if abs(x-cx)<66 and -48<y-cy<22 and rng.random()<0.9: continue
        if not clear(x,y,8.0,3.6): continue
        sp=species(x,y); put(sp,x,y,s=rng.uniform(0.85,1.2),r=3.4 if "Pine" not in sp else 3.0); n+=1
    # --- understory: bushes, rocks, logs, stumps, plants, mushrooms
    def scatter(names,wts,count,build_m,self_m,xr=(-100,100),yr=(-95,58),scale=(0.85,1.2),inner_ok=False):
        m=0; t=0
        while m<count and t<count*80:
            t+=1
            x=cx+rng.uniform(*xr); y=cy+rng.uniform(*yr)
            if not inner_ok and abs(x-cx)<60 and -45<y-cy<18 and rng.random()<0.7: continue
            if not clear(x,y,build_m,self_m): continue
            put(rng.choices(names,wts)[0],x,y,s=rng.uniform(*scale),r=self_m); m+=1
    scatter(["SM_VK_Bush_Round","SM_VK_Bush_Large","SM_VK_Bush_Berry","SM_VK_Bush_Hydrangea","SM_VK_Bush_Autumn"],[30,20,20,15,8],70,4.0,1.4,inner_ok=True)
    scatter(["SM_VK_Rock_Boulder_A","SM_VK_Rock_Boulder_B","SM_VK_Rock_Boulder_Flat","SM_VK_Rock_Cluster","SM_VK_Rock_Small_A","SM_VK_Rock_Small_B","SM_VK_Rock_Pebbles"],[18,8,8,8,16,16,10],45,5.0,1.4)
    scatter(["SM_VK_Log_Fallen","SM_VK_Stump"],[1,1],14,6.0,1.8)
    scatter(["SM_VK_Plant_Fern","SM_VK_Plant_TallGrass","SM_VK_Plant_Wildflowers"],[35,40,25],260,3.0,0.7,inner_ok=True)
    scatter(["SM_VK_Mushrooms_Red","SM_VK_Mushrooms_Brown","SM_VK_Mushrooms_Glow"],[40,45,15],30,4.0,0.4)
    return cnt[0]
'''
bpy.data.texts["vk_nature"].write(code)
exec(bpy.data.texts["vk_helpers"].as_string()); exec(bpy.data.texts["vk_nature"].as_string())
V=bpy.data.collections["VK_Town"]
for c in ("VK_Glade","VK_NatureTest"):
    for o in bpy.data.collections[c].objects: o.hide_render=True
n=dress_town_nature(V)
for o in V.objects: o.hide_render=False
print("placed",n,"town objects",len(V.objects))
import os
SC=bpy.data.scenes["VillageKit"]; ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
g=bpy.data.objects["VK_Ground"]; g.location=(200,-20,0); g.scale=(8,8,1)
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
ct.data.lens=24; tgt=Vector((cx+4,cy-24,0)); ct.location=Vector((cx+64,cy-140,82))
ct.rotation_euler=(tgt-ct.location).to_track_quat("-Z","Y").to_euler()
SC.camera=ct; SC.render.resolution_percentage=60
SC.render.filepath=os.path.join(out,"_townnat1.png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: placed 601 town objects 1423\n"}

# ==============================================================================================================
# [0244] 2026-09-23 11:14:23  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=60
shots=[("_tn_pond",(cx+42,cy-53,1.5),(cx+37,cy-68,4.5),26),
       ("_tn_orchard",(cx-34,cy-58,2.0),(cx-50,cy-79,5.5),28),
       ("_tn_north",(cx,cy+34,5),(cx-2,cy+2,2.2),24),
       ("_tn_circle",(cx+88,cy+12,1.6),(cx+80,cy-4,3.6),26)]
for name,tgt,loc,lens in shots:
    ct.data.lens=lens; ct.location=Vector(loc); ct.rotation_euler=(Vector(tgt)-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0245] 2026-09-23 11:15:02  blender  ok
# ==============================================================================================================
import bpy, os, math
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; ct=bpy.data.objects["VK_CameraTown"]; cx,cy=200.0,0.0
V=bpy.data.collections["VK_Town"]
trees=[o.location.copy() for o in V.objects if o.name.startswith("NT_") and ("Tree" in o.name or "SM_Tree" in o.name)]
def seg_clear(a,b,rad=3.2):
    a=Vector((a[0],a[1])); b=Vector((b[0],b[1])); d=b-a; L2=d.length_squared
    for p in trees:
        q=Vector((p.x,p.y)); t=max(0.0,min(1.0,(q-a).dot(d)/L2)); 
        if (q-(a+d*t)).length<rad: return False
    return True
sc=(cx+88,cy+12); best=None
for i in range(72):
    a=i*2*math.pi/72
    for R in (13,15,17,20):
        p=(sc[0]+math.cos(a)*R,sc[1]+math.sin(a)*R)
        if seg_clear(p,sc) and seg_clear(p,(sc[0]-math.sin(a)*5,sc[1]+math.cos(a)*5)) and seg_clear(p,(sc[0]+math.sin(a)*5,sc[1]-math.cos(a)*5)):
            score=-abs(math.sin(a+1.2))  # prefer views from the south-west
            if best is None or score>best[0]: best=(score,p)
print("circle cam",best)
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_percentage=60
shots=[("_tn_pond",(cx+42,cy-53,1.0),(cx+53,cy-65,4.0),26),
       ("_tn_north",(cx,cy+8,4),(cx-6,cy+54,7.0),24)]
if best: shots.append(("_tn_circle",(sc[0],sc[1],1.5),(best[1][0],best[1][1],3.4),26))
for name,tgt,loc,lens in shots:
    ct.data.lens=lens; ct.location=Vector(loc); ct.rotation_euler=(Vector(tgt)-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# ---- result ----
# {"result":"Code executed successfully: circle cam (-0.4028255326123513, (297.19238815542514, 2.8076118445748808))\n"}

# ==============================================================================================================
# [0246] 2026-09-23 11:15:41  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
SC=bpy.data.scenes["VillageKit"]; ct=bpy.data.objects["VK_CameraTown"]; cn=bpy.data.objects["VK_CameraNature"]; cx,cy=200.0,0.0
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
SC.render.resolution_x=1920; SC.render.resolution_y=1080; SC.render.resolution_percentage=100
if hasattr(SC.eevee,"taa_render_samples"): SC.eevee.taa_render_samples=64
def vis(coll,on):
    for o in bpy.data.collections[coll].objects: o.hide_render=not on
g=bpy.data.objects["VK_Ground"]
# town shots
vis("VK_Town",True); vis("VK_Glade",False); vis("VK_NatureTest",False)
g.location=(200,-20,0); g.scale=(8,8,1)
shots=[("nature_town_aerial",(cx+4,cy-24,0),(cx+64,cy-140,82),24),
       ("nature_town_pond",(cx+42,cy-53,1.0),(cx+53,cy-65,4.0),26),
       ("nature_town_orchard",(cx-34,cy-58,2.0),(cx-50,cy-79,5.5),28),
       ("nature_town_forest",(cx,cy+8,4),(cx-6,cy+54,7.0),24),
       ("nature_town_circle",(cx+88,cy+12,1.5),(297.2,2.8,3.4),26)]
for name,tgt,loc,lens in shots:
    ct.data.lens=lens; ct.location=Vector(loc); ct.rotation_euler=(Vector(tgt)-ct.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=ct; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
# glade shots
vis("VK_Town",False); vis("VK_Glade",True)
g.location=(700,5,0); g.scale=(6,6,1)
shots=[("nature_glade_hero",(697,6,3.2),(700,-13,2.2),24),("nature_glade_floor",(701.5,3,0.6),(706.5,-3.5,1.6),30),
       ("nature_glade_circle",(712.5,6.5,1.3),(703.0,-3.5,3.4),26)]
for name,tgt,loc,lens in shots:
    cn.data.lens=lens; cn.location=Vector(loc); cn.rotation_euler=(Vector(tgt)-cn.location).to_track_quat("-Z","Y").to_euler()
    SC.camera=cn; SC.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True,scene=SC.name)
vis("VK_Town",True)
g.location=(200,-20,0); g.scale=(8,8,1); SC.camera=ct
for f in os.listdir(out):
    if f.startswith("_") and f.endswith(".png"): os.remove(os.path.join(out,f))
for img in bpy.data.images:
    if img.name.startswith("T_VK") and img.has_data and not img.packed_file:
        try: img.pack()
        except Exception as e: print(img.name,e)
bpy.ops.wm.save_mainfile()
print(round(os.path.getsize(bpy.data.filepath)/1e6,1),"MB")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n175.1 MB\n"}

# ==============================================================================================================
# [0247] 2026-09-23 11:19:15  blender  ok
# ==============================================================================================================
import bpy, os
out=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
os.makedirs(out,exist_ok=True)
for n in ("vk_helpers","vk_tex","vk_texgen","vk_mat","vk_nature","vk_leafgen"):
    with open(os.path.join(out,n+".py"),"w",encoding="utf-8") as f: f.write(bpy.data.texts[n].as_string())
P=bpy.data.collections["VK_Pieces"]
names=sorted(o.name for o in P.objects)+sorted(o.name for o in bpy.data.collections["VK_NaturePieces"].objects)
with open(os.path.join(out,"kit_pieces.txt"),"w") as f: f.write("\n".join(names))
print(len(names), [len(bpy.data.texts[n].as_string()) for n in ("vk_helpers","vk_tex","vk_texgen","vk_mat","vk_nature")])
# ---- result ----
# {"result":"Code executed successfully: 146 [172882, 5510, 43819, 12502, 44688]\n"}

# ==============================================================================================================
# [0248] 2026-09-23 12:18:58  blender  ok
# ==============================================================================================================
import bpy, os
src=bpy.data.filepath
bak=os.path.join(os.path.dirname(src),"medievalDiorama_backup_before_expansion.blend")
bpy.ops.wm.save_mainfile(); bpy.ops.wm.save_as_mainfile(filepath=bak,copy=True)
print(os.path.exists(bak))
s=bpy.data.texts["vk_tex"].as_string()
i=s.index("def crack_segments"); print(s[i:i+1400])
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nInfo: Saved \"medievalDiorama_backup_before_expansion.blend\"\nTrue\ndef
#  crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None,jit=0.55):\n segs=[]\n def walk(x,y,a,nsteps,w,depth):\n for i i
# n range(nsteps):\n a+=rng.uniform(-jit,jit)\n if dirbias is not None: a=a*0.7+dirbias*0.3\n st=rng.uniform(*step_px); nx,ny=x+math.cos(a)*st,y+math.si
# n(a)*st\n ww=max(0.5,w*(1-i/nsteps*0.7))\n segs.append((x,y,nx,ny,ww)); x,y=nx,ny\n if depth<2 and rng.random()<branch: walk(x,y,a+rng.choice([-1,1])*
# rng.uniform(0.6,1.1),int(nsteps*0.4),ww*0.8,depth+1)\n for _ in range(n):\n a0=rng.uniform(0,2*math.pi) if dirbias is None else dirbias+rng.uniform(-0
# .2,0.2)\n walk(rng.uniform(0,S),rng.uniform(0,S),a0,int(rng.uniform(*steps)),w0,0)\n return segs\n\n"}

# ==============================================================================================================
# [0249] 2026-09-23 12:20:09  blender  ok
# ==============================================================================================================
import bpy
t=bpy.data.texts["vk_tex"]; s=t.as_string()
old='''def crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None,jit=0.55):'''
assert old in s
s=s.replace(old,'''def crack_segments(S,rng,n=5,steps=(18,40),step_px=(5,11),w0=1.8,branch=0.1,dirbias=None,jit=0.55,starts=None):''')
old2='''    for _ in range(n):
        a0=rng.uniform(0,2*math.pi) if dirbias is None else dirbias+rng.uniform(-0.2,0.2)
        walk(rng.uniform(0,S),rng.uniform(0,S),a0,int(rng.uniform(*steps)),w0,0)
    return segs'''
assert old2 in s
s=s.replace(old2,'''    if starts is not None:
        for (sx_,sy_,sa_,sn_) in starts: walk(sx_,sy_,sa_,int(sn_),w0,0)
        return segs
    for _ in range(n):
        a0=rng.uniform(0,2*math.pi) if dirbias is None else dirbias+rng.uniform(-0.2,0.2)
        walk(rng.uniform(0,S),rng.uniform(0,S),a0,int(rng.uniform(*steps)),w0,0)
    return segs''')
s+='''
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
'''
t.clear(); t.write(s); exec(s)
print("ok", smin(np.float32(0.1),np.float32(0.2),0.05), hx("#9B9384"))
# ---- result ----
# {"result":"Code executed successfully: ok 0.10000000149011612 [0.60784316 0.5764706 0.5176471 ]\n"}

# ==============================================================================================================
# [0250] 2026-09-23 12:26:09  blender  ok
# ==============================================================================================================
import bpy, time
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read()
t=bpy.data.texts.get("vk_stone2") or bpy.data.texts.new("vk_stone2"); t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
t0=time.time(); res=[]
for sd in range(50):
    L=ns['stone_layout'](sd)
    ok,sc=ns['stone_layout_score'](L)
    res.append((ok,sc,sd,L['N'],len(L['packers']),round(L['area_ratio'],2),L['viol'],round(L['min_stag'],3),round(L['wmin'],2),round(L['wmax'],2)))
res.sort(key=lambda r:(not r[0],r[1]))
print(time.time()-t0)
for r in res[:12]: print(r)
print(sum(r[0] for r in res),"pass")
# ---- result ----
# {"result":"Code executed successfully: 6.291589260101318\n(True, 3.732954086661678, 40, 32, 6, 1.73, 0, 0.126, 0.32, 1.05)\n(True, 3.8752606490319237,
#  44, 34, 6, 1.88, 0, 0.126, 0.37, 0.93)\n(True, 4.920269866738552, 13, 35, 6, 1.92, 0, 0.123, 0.32, 1.02)\n(True, 5.460207378584664, 32, 35, 6, 2.46, 
# 0, 0.122, 0.29, 1.04)\n(True, 5.947959173649796, 1, 36, 10, 1.95, 0, 0.121, 0.25, 0.88)\n(False, 2.097409842310004, 20, 33, 8, 2.1, 1, 0.126, 0.29, 1.
# 06)\n(False, 2.1518206530080946, 6, 33, 7, 1.65, 3, 0.121, 0.33, 1.09)\n(False, 2.155435308076799, 17, 33, 8, 2.16, 1, 0.123, 0.39, 1.05)\n(False, 2.3
# 180237698491304, 48, 33, 9, 1.82, 2, 0.131, 0.41, 1.1)\n(False, 2.453738131301601, 23, 33, 7, 1.95, 4, 0.12, 0.33, 1.06)\n(False, 2.969222663921977, 0
# , 33, 9, 2.47, 1, 0.124, 0.3, 1.17)\n(False, 3.32447322404486, 36, 34, 7, 1.82, 2, 0.12, 0.3, 0.96)\n5 pass\n"}

# ==============================================================================================================
# [0251] 2026-09-23 12:26:30  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
src=bpy.data.texts["vk_stone2"].as_string()
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\stone_dev"
os.makedirs(OUT,exist_ok=True)
def save_prev(arr,name):
    S0,S1=arr.shape[:2]
    if arr.ndim==2: arr=np.stack([arr]*3,-1)
    rgba=np.concatenate([np.clip(arr,0,1),np.ones((S0,S1,1),np.float32)],-1)
    im=bpy.data.images.new("_prev",S1,S0,alpha=False); im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    im.filepath_raw=os.path.join(OUT,name); im.file_format="PNG"; im.save(); bpy.data.images.remove(im)
t0=time.time()
r=ns['gen_stone'](seed=40,L=ns['stone_layout'](40),write=False)
print("time",time.time()-t0, r['stats'])
bc=r['bc']; save_prev(bc,"s40_bc.png")
nrm=ns['normal_from_height'](r['h'],0.06,3.0)*0.5+0.5; save_prev(nrm,"s40_n.png")
save_prev(r['h'],"s40_h.png")
import builtins
bpy.app.driver_namespace['stone_last']=r
L=ns['luma'](bc); st=r['stone']
j=st<0.5
print("joint cov",j.mean(),"joint luma",L[j].mean(),"p1",np.percentile(L[j],1))
print("stone mean",bc[~j].mean(0)*255,"tile mean",bc.reshape(-1,3).mean(0)*255,"tile luma",L.mean())
print("stone luma p5/50/95",np.percentile(L[~j],[5,50,95]))
print("h mortar",r['h'][st<0.1].mean(),"faces",np.percentile(r['h'][st>0.9],[10,50,90]))
print("moss",r['moss'])
# ---- result ----
# {"result":"Code executed successfully: time 16.583351373672485 {'t_layout_to_paint': 16.072973489761353, 'time': 16.44172239303589}\njoint cov 0.09600
# 73471069336 joint luma 0.35311353 p1 0.21029543429613112\nstone mean [147.90367 141.9997 132.28233] tile mean [142.84598 137.0002 126.894165] tile lum
# a 0.53926766\nstone luma p5/50/95 [0.30680323 0.56363815 0.79243526]\nh mortar 0.07818155 faces [0.24143619 0.51952308 0.65566365]\nmoss 0.01021075248
# 7182617\n"}

# ==============================================================================================================
# [0252] 2026-09-23 12:27:10  blender  ok
# ==============================================================================================================
import bpy, numpy as np
r=bpy.app.driver_namespace['stone_last']; L=r['L']
bc=r['bc']; lab=r['lab']; st=r['stone']
pid=np.array([s['pid'] for s in L['stones']]+[q['pid'] for q in L['packers']])
for p in range(6):
    m=(pid[lab]==p)&(st>0.5)
    if m.any(): print(p, (bc[m].mean(0)*255).round(), m.mean().round(3))
print("mortar",(bc[st<0.3].mean(0)*255).round())
# ---- result ----
# {"result":"Code executed successfully: 0 [149. 141. 128.] 0.32\n1 [162. 155. 137.] 0.252\n2 [129. 133. 136.] 0.229\n3 [169. 150. 130.] 0.025\n4 [148. 
# 129. 127.] 0.066\n5 [121. 120. 120.] 0.011\nmortar [95. 89. 76.]\n"}

# ==============================================================================================================
# [0253] 2026-09-23 12:27:53  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read(); t=bpy.data.texts["vk_stone2"]; t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
res=[]
for sd in range(80):
    L=ns['stone_layout'](sd); ok,sc=ns['stone_layout_score'](L)
    res.append((ok,sc,sd,L['N'],len(L['packers']),round(L['area_ratio'],2),L['viol']))
res.sort(key=lambda r:(not r[0],r[1]))
for r in res[:6]: print(r)
OUT=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\stone_dev"
def save_prev(arr,name):
    S0,S1=arr.shape[:2]
    if arr.ndim==2: arr=np.stack([arr]*3,-1)
    rgba=np.concatenate([np.clip(arr,0,1),np.ones((S0,S1,1),np.float32)],-1)
    im=bpy.data.images.new("_prev",S1,S0,alpha=False); im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    im.filepath_raw=os.path.join(OUT,name); im.file_format="PNG"; im.save(); bpy.data.images.remove(im)
bpy.app.driver_namespace['save_prev']=save_prev
best=res[0][2]
r=ns['gen_stone'](seed=best,L=ns['stone_layout'](best),write=False)
bpy.app.driver_namespace['stone_last']=r
bc=r['bc']; save_prev(bc,"v2_bc.png")
L_=ns['luma'](bc); st=r['stone']; j=st<0.5
print("seed",best,"joint cov",j.mean(),"joint luma",L_[j].mean(),"p1",np.percentile(L_[j],1))
print("stone mean",(bc[~j].mean(0)*255).round(),"tile luma",L_.mean())
print("stone luma p5/50/95",np.percentile(L_[~j],[5,50,95]))
print("moss",r['moss'])
lab=r['lab']; ids=np.unique(lab[~j]); ml=np.array([L_[(lab==i)&~j].mean() for i in ids]); print("per-stone sigma",ml.std())
# ---- result ----
# {"result":"Code executed successfully: (True, 3.460018903497781, 52, 32, 9, 1.96, 0)\n(True, 3.721302045020991, 15, 34, 7, 2.22, 0)\n(True, 3.73295408
# 6661678, 40, 32, 6, 1.73, 0)\n(True, 4.101922613188476, 3, 34, 6, 2.1, 0)\n(True, 4.129138925329338, 29, 34, 6, 2.13, 0)\n(False, 1.9472411493645942, 
# 70, 33, 8, 1.95, 2)\nseed 52 joint cov 0.10019302368164062 joint luma 0.3502132 p1 0.20850075021386147\nstone mean [145. 137. 129.] tile luma 0.523619
# 06\nstone luma p5/50/95 [0.29627959 0.55115947 0.75596848]\nmoss 0.011398077011108398\nper-stone sigma 0.061894495\n"}

# ==============================================================================================================
# [0254] 2026-09-23 12:28:52  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read(); t=bpy.data.texts["vk_stone2"]; t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
L=ns['stone_layout'](52); print(ns['stone_layout_score'](L))
r=ns['gen_stone'](seed=52,L=L,write=True)
save_prev=bpy.app.driver_namespace['save_prev']
bc=r['bc']; st=r['stone']
save_prev(np.tile(bc,(2,2,1)),"v3_bc_tile.png")
L_=ns['luma'](bc); j=st<0.5
print("joint cov",j.mean(),"joint luma",L_[j].mean(),"stone mean",(bc[~j].mean(0)*255).round(),"tile luma",L_.mean())
print("stone luma p5/50/95",np.percentile(L_[~j],[5,50,95]))
# tiling test
def seam(a):
    a=np.roll(a,(512,512),(0,1)); d=np.abs(np.diff(a,axis=1))
    return d[:,511].mean()/d.mean()
img=bpy.data.images["T_VK_Stone_BC"]; print(img.size[:], img.packed_file is not None)
print("seam ratio bc",seam(bc.mean(-1)),"h",seam(r['h']))
print("mip mean diff",abs(bc.mean()-bc.reshape(32,32,32,32,3).mean((1,3)).mean()))
# ---- result ----
# {"result":"Code executed successfully: (True, 3.460018903497781)\njoint cov 0.10019302368164062 joint luma 0.35021558 stone mean [145. 138. 128.] tile
#  luma 0.5239072\nstone luma p5/50/95 [0.2964045 0.55114532 0.75572088]\n(1024, 1024) True\nseam ratio bc 0.8509488 h 1.2169603\nmip mean diff 2.384185
# 8e-07\n"}

# ==============================================================================================================
# [0255] 2026-09-23 12:30:04  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read(); t=bpy.data.texts["vk_stone2"]; t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
t0=time.time()
r=ns['gen_stone'](seed=52,L=ns['stone_layout'](52),write=True)
t1=time.time()
b=ns['gen_stoneblock'](write=True)
print(t1-t0,time.time()-t1)
save_prev=bpy.app.driver_namespace['save_prev']
save_prev(np.tile(b['bc'],(2,2,1)),"blk_tile.png")
nrm=ns['normal_from_height'](b['h'],0.05,1.2)*0.5+0.5; save_prev(nrm,"blk_n.png")
print([ (k,v) for k,v in ns['PBR_SETS'].items() if 'Stone' in k])
# ---- result ----
# {"result":"Code executed successfully: 15.59878945350647 7.930304050445557\n[('T_VK_Stone', {'depth': 0.06, 'tile': 3.0}), ('T_VK_StoneBlock', {'depth
# ': 0.05, 'tile': 1.2})]\n"}

# ==============================================================================================================
# [0256] 2026-09-23 12:31:02  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read(); t=bpy.data.texts["vk_stone2"]; t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
b=ns['gen_stoneblock'](write=True)
save_prev=bpy.app.driver_namespace['save_prev']
save_prev(np.tile(b['bc'],(2,2,1))[::2,::2],"blk_tile2.png")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0257] 2026-09-23 12:31:47  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read(); t=bpy.data.texts["vk_stone2"]; t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
b=ns['gen_stoneblock'](write=True)
save_prev=bpy.app.driver_namespace['save_prev']
save_prev(np.tile(b['bc'],(2,2,1))[::2,::2],"blk_tile3.png")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0258] 2026-09-23 12:32:25  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
p=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\vk_stone2.py"
src=open(p).read(); t=bpy.data.texts["vk_stone2"]; t.clear(); t.write(src)
ns={}
exec(bpy.data.texts["vk_tex"].as_string(),ns); exec(bpy.data.texts["vk_texgen"].as_string(),ns); exec(src,ns)
b=ns['gen_stoneblock'](write=True)
save_prev=bpy.app.driver_namespace['save_prev']
save_prev(np.tile(b['bc'],(2,2,1))[::2,::2],"blk_tile4.png")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0259] 2026-09-23 12:32:49  blender  ok
# ==============================================================================================================
import bpy,os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n in ["vk_helpers","vk_tex","vk_texgen","vk_mat","vk_nature","vk_leafgen"]:
    open(os.path.join(D,n+".py"),"w",encoding="utf8").write(bpy.data.texts[n].as_string())
print([ (t.name,len(t.as_string())) for t in bpy.data.texts])
# ---- result ----
# {"result":"Code executed successfully: [('mc_helpers', 9064), ('tree_build', 13407), ('tree_skeleton', 47741), ('vk_helpers', 172882), ('vk_leafgen', 
# 20071), ('vk_mat', 12502), ('vk_nature', 44688), ('vk_stone2', 24666), ('vk_tex', 6948), ('vk_texgen', 43819), ('wk_helpers', 5767)]\n"}

# ==============================================================================================================
# [0260] 2026-09-23 12:36:55  blender  ok
# ==============================================================================================================
import bpy, time, numpy as np, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_stone2.py")).read()+"\n"+open(os.path.join(D,"vk_tex2_extra.py")).read()
open(os.path.join(D,"vk_tex2.py"),"w").write(src)
t=bpy.data.texts.get("vk_stone2"); 
if t: t.name="vk_tex2"
t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat"): exec(bpy.data.texts[n].as_string(),ns)
exec(src,ns)
save_prev=bpy.app.driver_namespace['save_prev']
T={}
t0=time.time(); f=ns['gen_fieldstone'](); T['field']=time.time()-t0
st=f['stone']; L_=ns['luma'](f['bc']); print("field gap cov",(st<0.5).mean(),"luma",L_.mean(),"moss",f['moss'])
save_prev(f['bc'],"field_bc.png")
t0=time.time(); w=ns['gen_wattle'](); T['wattle']=time.time()-t0; save_prev(np.tile(w['bc'],(2,2,1))[::2,::2],"wattle_bc.png")
t0=time.time(); ns['gen_net'](); ns['net_material'](); T['net']=time.time()-t0
t0=time.time(); b1=ns['gen_roof_slate'](); b2=ns['gen_roof_shingle'](); T['roofs']=time.time()-t0
save_prev(np.concatenate([b1,b2],1)[::2,::2],"roofs_new.png")
print(T)
# ---- result ----
# {"result":"Code executed successfully: field gap cov 0.12792491912841797 luma 0.46844622 moss 0.0612788200378418\n{'field': 28.890872955322266, 'wattl
# e': 1.2428512573242188, 'net': 0.17565536499023438, 'roofs': 2.726179599761963}\n"}

# ==============================================================================================================
# [0261] 2026-09-23 12:38:07  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_tex2.py")).read(); t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
w=ns['gen_wattle'](); bpy.app.driver_namespace['save_prev'](np.tile(w['bc'],(2,2,1))[::2,::2],"wattle_bc2.png")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0262] 2026-09-23 12:40:21  blender  ERROR
# ==============================================================================================================
import bpy, os, time
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_tex2.py")).read(); t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
ns['gen_ashlar']()
exec(open(os.path.join(D,"patch_kit_stone.py")).read(),{})
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: ambiguous: k.box((0,y0,(RIDGE+1.5)/2),(1.0,1.0,RIDGE+1.5),STO
# NE,bevel=0.06,segs=2)"}

# ==============================================================================================================
# [0263] 2026-09-23 12:40:39  blender  ok
# ==============================================================================================================
import bpy, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
g={}
exec(open(os.path.join(D,"patch_kit_stone.py")).read(),g)
# ---- result ----
# {"result":"Code executed successfully: patched\n"}

# ==============================================================================================================
# [0264] 2026-09-23 12:40:47  blender  ERROR
# ==============================================================================================================
import bpy, time
g={}
exec(bpy.data.texts["vk_helpers"].as_string(),g)
print(g['STONE_BLOCK'],g['NET'],len(g['kit_mats']()))
g['apply_pbr_all']()
t0=time.time()
g['full_rebuild']()
print("rebuild",time.time()-t0)
o=bpy.data.objects["SM_VK_Wall_Stone"]; print(len(o.data.materials), [m.name for m in o.data.materials][44:])
import collections
cnt=collections.Counter(p.material_index for p in o.data.polygons); print(cnt)
# ---- result ----
# {"result":"Error executing code: Communication error with Blender: Code execution error: couldn't create BPy_rna object"}

# ==============================================================================================================
# [0265] 2026-09-23 12:40:54  blender  ok
# ==============================================================================================================
import bpy
o=bpy.data.objects.get("SM_VK_Wall_Stone"); print(o, len(o.data.materials) if o else None)
print([m.name for m in o.data.materials][44:] if o else None)
print(bpy.data.objects.get("__tmp__"))
print(len([x for x in bpy.data.objects if x.name.startswith("SM_VK")]))
# ---- result ----
# {"result":"Code executed successfully: <bpy_struct, Object(\"SM_VK_Wall_Stone\") at 0x000001CB8435F908> 31\n[]\nNone\n2296\n"}

# ==============================================================================================================
# [0266] 2026-09-23 12:41:03  blender  ERROR
# ==============================================================================================================
import bpy, traceback
g={}
try:
    exec(bpy.data.texts["vk_helpers"].as_string(),g)
    print("exec ok")
    km=g['kit_mats'](); print(len(km))
except Exception as e:
    print(traceback.format_exc()[-1500:])
# ---- result ----
# {"result":"Code executed successfully: exec ok\nTraceback (most recent call last):\n File \"<string>\", line 6, in <module>\n File \"<string>\", line 
# 50, in kit_mats\n File \"<string>\", line 3245, in tex_mat\n File \"<string>\", line 1701, in tex_mat\n File \"<string>\", line 1701, in tex_mat\n Fil
# e \"<string>\", line 1701, in tex_mat\n [Previous line repeated 989 more times]\n File \"<string>\", line 1695, in tex_mat\nMemoryError: couldn't crea
# te BPy_rna object\n\n"}

# ==============================================================================================================
# [0267] 2026-09-23 12:41:11  blender  ok
# ==============================================================================================================
import bpy
L=bpy.data.texts["vk_helpers"].as_string().split("\n")
for i in list(range(1686,1703))+list(range(3236,3250)): print(i+1,L[i][:160])
print([ (i+1,l[:100]) for i,l in enumerate(L) if "_tex_mat_legacy" in l])
# ---- result ----
# {"result":"Code executed successfully: 1687 def build_guardtower(coll,origin):\n1688 place_v(coll,\"SM_VK_GuardTower\",0,0,0,0,origin,{})\n1689 place_
# v(coll,\"SM_VK_Prop_WeaponRack\",2.9,-1.2,0,90,origin,{})\n1690 place_v(coll,\"SM_VK_Prop_BarrelStack\",-2.7,-1.8,0,90,origin,{})\n1691 \n1692 exec(bp
# y.data.texts[\"vk_mat\"].as_string())\n1693 _tex_mat_legacy=tex_mat\n1694 def tex_mat(name,img,rough=0.85,flat=None,emit=None,alpha_clip=False,tint=No
# ne):\n1695 m=bpy.data.materials.get(name)\n1696 if m: return m\n1697 if img and bpy.data.images.get(img+\"_BC\"):\n1698 m=bpy.data.materials.new(name)
# ; return pbr_material(m,img,tint=tint)\n1699 if img and img.startswith(\"T_VK_\") and bpy.data.images.get(img.replace(\"T_VK_Wood\",\"T_VK_Wood\")+\"_
# BC\"):\n1700 m=bpy.data.materials.new(name); return pbr_material(m,img,tint=tint)\n1701 return _tex_mat_legacy(name,img,rough,flat,emit,alpha_clip,tin

# ==============================================================================================================
# [0268] 2026-09-23 12:41:35  blender  ok
# ==============================================================================================================
import bpy, os, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
g={"SRC_HELPERS":os.path.join(D,"vk_helpers.py")}
exec(open(os.path.join(D,"patch_kit_stone.py")).read(),g)
s=bpy.data.texts["vk_helpers"].as_string(); print(len(s.split("\n")), s.count("def tex_mat"), s.count("def wall_rocks"))
g={}
try:
    exec(bpy.data.texts["vk_helpers"].as_string(),g)
    km=g['kit_mats'](); print(len(km), [m.name for m in km[45:]])
except Exception as e:
    print(traceback.format_exc()[-1500:])
# ---- result ----
# {"result":"Code executed successfully: patched\n3042 2 1\n52 ['M_VK_StoneBlock', 'M_VK_FieldStone', 'M_VK_Wattle', 'M_VK_Hide', 'M_VK_Pigskin', 'M_VK_
# Coal', 'M_VK_Net']\n"}

# ==============================================================================================================
# [0269] 2026-09-23 12:41:42  blender  ok
# ==============================================================================================================
import bpy, time, traceback, collections
g={}
exec(bpy.data.texts["vk_helpers"].as_string(),g)
try:
    g['apply_pbr_all']()
    t0=time.time()
    g['full_rebuild']()
    print("rebuild",time.time()-t0)
except Exception as e:
    print(traceback.format_exc()[-2000:])
o=bpy.data.objects["SM_VK_Wall_Stone"]; print(len(o.data.materials))
print(collections.Counter(p.material_index for p in o.data.polygons))
# ---- result ----
# {"result":"Code executed successfully: rebuild 6.151584148406982\n52\nCounter({45: 336, 0: 88})\n"}

# ==============================================================================================================
# [0270] 2026-09-23 12:41:59  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["VillageKit"]
print([ (o.name, tuple(round(v,1) for v in o.location), tuple(round(v,2) for v in o.rotation_euler)) for o in sc.objects if o.type=="CAMERA"])
print(sc.render.resolution_x, sc.render.resolution_y, sc.render.engine, sc.camera.name if sc.camera else None)
print([c.name for c in sc.collection.children], [ (c.name,c.hide_render) for c in sc.collection.children])
# ---- result ----
# {"result":"Code executed successfully: [('VK_CameraClose', (7.5, 5.5, 2.6), (1.63, -0.0, 0.77)), ('VK_CameraKit', (8.5, -84.0, 19.2), (1.06, -0.0, 0.1
# 3)), ('VK_CameraT', (-1.0, 14.0, 15.0), (1.09, 0.0, 0.24)), ('VK_CameraProps', (112.5, -187.0, 7.3), (1.39, -0.0, 0.67)), ('VK_CameraMid', (8.0, -7.0,
#  7.5), (1.37, -0.0, 0.69)), ('VK_CameraTown', (297.2, 2.8, 3.4), (1.43, 0.0, 0.79)), ('VK_CameraNature', (703.0, -3.5, 3.4), (1.42, 0.0, -0.76)), ('VK
# _Camera', (28.0, -64.0, 48.0), (1.0, 0.0, 0.42))]\n1920 1080 BLENDER_EEVEE_NEXT VK_CameraTown\n['VK_Pieces', 'VK_Staging', 'VK_Demo', 'VK_Test', 'VK_V
# illage', 'VK_Showcase', 'VK_Town', 'VK_Catalog', 'VK_NaturePieces', 'VK_NatureTest', 'VK_Glade'] [('VK_Pieces', False), ('VK_Staging', False), ('VK_De
# mo', False), ('VK_Test', False), ('VK_Village', False), ('VK_Showcase', False), ('VK_Town', False), ('VK_Catalog', False), ('VK_NaturePieces', False),

# ==============================================================================================================
# [0271] 2026-09-23 12:42:09  blender  ok
# ==============================================================================================================
import bpy
from mathutils import Vector
sc=bpy.data.scenes["VillageKit"]
town=bpy.data.collections["VK_Town"]
def allobjs(c):
    for o in c.objects: yield o
    for ch in c.children: yield from allobjs(ch)
ws=[o for o in allobjs(town) if o.data and o.type=="MESH" and ("Wall_Stone" in o.data.name or any("Wall_Stone" in n for n in [o.name]))]
print(len(ws))
for o in ws[:15]: print(o.name,o.data.name,tuple(round(v,1) for v in o.matrix_world.translation), round(o.matrix_world.to_euler().z,2))
# ---- result ----
# {"result":"Code executed successfully: 93\nSM_VK_Wall_Stone_Window_inst.074 VAR_5162528836782080686 (194.0, 17.0, 0.0) -3.14\nSM_VK_Wall_Stone_Window_
# inst.075 VAR_5162528836782080686 (197.0, 17.0, 0.0) -3.14\nSM_VK_Wall_Stone_Door_inst.018 VAR_7468258319909628175 (200.0, 17.0, 0.0) -3.14\nSM_VK_Wall
# _Stone_Window_inst.076 VAR_5162528836782080686 (203.0, 17.0, 0.0) -3.14\nSM_VK_Wall_Stone_Window_inst.077 VAR_5162528836782080686 (206.0, 17.0, 0.0) -
# 3.14\nSM_VK_Wall_Stone_inst.075 VAR_3027802476899206371 (192.5, 12.5, 0.0) -1.57\nSM_VK_Wall_Stone_Window_inst.078 VAR_5162528836782080686 (192.5, 15.
# 5, 0.0) -1.57\nSM_VK_Wall_Stone_Window_inst.079 VAR_5162528836782080686 (207.5, 15.5, 0.0) 1.57\nSM_VK_Wall_Stone_inst.076 VAR_3027802476899206371 (20
# 7.5, 12.5, 0.0) 1.57\nSM_VK_Wall_Stone_Window_inst.080 VAR_9075809403744549803 (181.0, 0.5, 0.0) 1.57\nSM_VK_Wall_Stone_Door_inst.019 VAR_662141870700

# ==============================================================================================================
# [0272] 2026-09-23 12:42:25  blender  ok
# ==============================================================================================================
import bpy, os
from mathutils import Vector
OUTD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2"
os.makedirs(OUTD,exist_ok=True)
def shot(name,loc,target,lens=35,res=(1280,720),scene="VillageKit",samples=None):
    sc=bpy.data.scenes[scene]
    cam=bpy.data.objects.get("VK_CamTmp")
    if cam is None:
        cd=bpy.data.cameras.new("VK_CamTmp"); cam=bpy.data.objects.new("VK_CamTmp",cd)
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.location=loc; d=Vector(target)-Vector(loc); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens; cam.data.clip_end=2000
    old=(sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage)
    sc.camera=cam; sc.render.resolution_x,sc.render.resolution_y=res; sc.render.resolution_percentage=100
    sc.render.filepath=os.path.join(OUTD,name+".png")
    if samples: old_s=sc.eevee.taa_render_samples; sc.eevee.taa_render_samples=samples
    bpy.ops.render.render(write_still=True,scene=sc.name)
    if samples: sc.eevee.taa_render_samples=old_s
    sc.camera,sc.render.resolution_x,sc.render.resolution_y,sc.render.filepath,sc.render.resolution_percentage=old
    return sc.render.filepath
bpy.app.driver_namespace['shot']=shot
import time; t0=time.time()
shot("stone_close",(201.2,20.3,1.7),(199.6,17,1.4),lens=35)
shot("stone_street",(207,31,3.2),(198,17,2.2),lens=32)
print(time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: 1.9600677490234375\n"}

# ==============================================================================================================
# [0273] 2026-09-23 12:43:12  blender  ok
# ==============================================================================================================
import bpy, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_tex2.py")).read(); t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
m=bpy.data.texts["vk_mat"]; ms=m.as_string().replace('"M_VK_StoneBlock":dict(prefix="T_VK_StoneBlock",nstr=1.0)','"M_VK_StoneBlock":dict(prefix="T_VK_StoneBlock",nstr=0.8,spec=0.25)'); m.clear(); m.write(ms)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
ns['gen_stoneblock']()
ns['pbr_material'](bpy.data.materials["M_VK_StoneBlock"],"T_VK_StoneBlock",nstr=0.8,spec=0.25)
shot=bpy.app.driver_namespace['shot']
shot("stone_close2",(201.2,20.3,1.7),(199.6,17,1.4),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0274] 2026-09-23 12:43:41  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
OUTD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2"
def load(p):
    im=bpy.data.images.load(p); a=np.array(im.pixels[:],np.float32).reshape(im.size[1],im.size[0],4); bpy.data.images.remove(im); return a
a=load(os.path.join(OUTD,"stone_close.png")); b=load(os.path.join(OUTD,"stone_close2.png"))
print(np.abs(a-b).mean(), np.abs(a-b).max())
im=bpy.data.images["T_VK_StoneBlock_BC"]; px=np.array(im.pixels[:],np.float32).reshape(1024,1024,4); print(px[...,:3].mean((0,1)), im.is_dirty, im.packed_file is not None)
m=bpy.data.materials["M_VK_StoneBlock"]; print([ (n.type, n.image.name if getattr(n,'image',None) else None) for n in m.node_tree.nodes])
sc=bpy.data.scenes["VillageKit"]; print(sc.eevee.taa_render_samples)
# ---- result ----
# {"result":"Code executed successfully: 0.0043605 0.15686277\n[0.6077503 0.57644784 0.5136548 ] False True\n[('OUTPUT_MATERIAL', None), ('BSDF_PRINCIPL
# ED', None), ('UVMAP', None), ('TEX_IMAGE', 'T_VK_StoneBlock_BC'), ('TEX_IMAGE', 'T_VK_StoneBlock_N'), ('TEX_IMAGE', 'T_VK_StoneBlock_R'), ('VERTEX_COL
# OR', None), ('MIX', None), ('MATH', None), ('NORMAL_MAP', None)]\n64\n"}

# ==============================================================================================================
# [0275] 2026-09-23 12:43:59  blender  ok
# ==============================================================================================================
import bpy, numpy as np, os
for im in bpy.data.images:
    if im.name.startswith("T_VK_"):
        try: im.gl_free()
        except Exception as e: print(e); break
shot=bpy.app.driver_namespace['shot']
shot("stone_close3",(201.2,20.3,1.7),(199.6,17,1.4),lens=35)
OUTD=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\renders2"
def load(p):
    im=bpy.data.images.load(p); a=np.array(im.pixels[:],np.float32).reshape(im.size[1],im.size[0],4); bpy.data.images.remove(im); return a
a=load(os.path.join(OUTD,"stone_close2.png")); b=load(os.path.join(OUTD,"stone_close3.png"))
print(np.abs(a-b).mean())
# ---- result ----
# {"result":"Code executed successfully: 1.1701729e-08\n"}

# ==============================================================================================================
# [0276] 2026-09-23 12:44:27  blender  ok
# ==============================================================================================================
import bpy, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_tex2.py")).read(); t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
ns['gen_stoneblock']()
shot=bpy.app.driver_namespace['shot']
shot("stone_close4",(201.2,20.3,1.7),(199.6,17,1.4),lens=35)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0277] 2026-09-23 12:44:49  blender  ok
# ==============================================================================================================
import bpy, time
t0=time.time()
bpy.ops.wm.save_mainfile()
print(bpy.data.filepath, time.time()-t0)
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nE:\\Unity\\Projects\\Cube Sorter\\Art\\WallKit\\medievalDiorama.blend 0.
# 3260347843170166\n"}

# ==============================================================================================================
# [0278] 2026-09-23 12:46:01  blender  ok
# ==============================================================================================================
import time; t0=time.time(); time.sleep(2); print("A",t0,time.time())
# ---- result ----
# {"result":"Code executed successfully: A 1790167564.5638976 1790167566.5648162\n"}

# ==============================================================================================================
# [0279] 2026-09-23 12:46:02  blender  ok
# ==============================================================================================================
import time; t0=time.time(); time.sleep(2); print("B",t0,time.time())
# ---- result ----
# {"result":"Code executed successfully: B 1790167571.0653062 1790167573.0656683\n"}

# ==============================================================================================================
# [0280] 2026-09-23 12:46:41  blender  ok
# ==============================================================================================================
import bpy
sc=bpy.data.scenes["VillageKit"]
print(sc.world.name if sc.world else None)
print([(o.name,o.data.type,round(o.data.energy,2),tuple(round(a,2) for a in o.rotation_euler)) for o in sc.objects if o.type=="LIGHT"])
print(sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure)
gr=[o.name for o in sc.objects if "round" in o.name or "Ground" in o.name][:10]; print(gr)
e=sc.eevee; print(e.taa_render_samples, e.use_raytracing, e.use_shadows, getattr(e,'use_gtao',None))
# ---- result ----
# {"result":"Code executed successfully: MC_World\n[('VK_Sun', 'SUN', 3.2, (0.91, 0.1, -0.52))]\nAgX AgX - Medium High Contrast -0.20000000298023224\n['
# VK_Ground']\n64 True False True\n"}

# ==============================================================================================================
# [0281] 2026-09-23 12:47:18  blender  ok
# ==============================================================================================================
import bpy, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"ws_common.py")).read()
t=bpy.data.texts.get("ws_common") or bpy.data.texts.new("ws_common"); t.clear(); t.write(src)
for n in ["vk_helpers","vk_mat","vk_tex2"]:
    open(os.path.join(D,n+".py"),"w",encoding="utf8").write(bpy.data.texts[n].as_string())
tm=bpy.data.texts.get("ws_zztest") or bpy.data.texts.new("ws_zztest"); tm.clear()
tm.write('''
def zz_block(k):
    k.box((0,0,0.5),(1.0,1.0,1.0),STONE,bevel=0.05,segs=2)
    k.box((0,0,1.2),(1.2,1.2,0.3),WATTLE,bevel=0.03)
WS_SPECS=[("SM_VK_ZZTest_Block",zz_block,dict(wobble=False,grime=True))]
''')
exec(src)
b=ws_build("zztest")
print(ws_stats(b))
p=ws_shot("zztest","test",(3,-4,2.5),(0,0,0.8),lens=35,res=(640,360))
print(p)
# ---- result ----
# {"result":"Code executed successfully: [{'name': 'SM_VK_ZZTest_Block', 'tris': 152, 'bbox': [1.2, 1.2, 1.35], 'zmin': 0.0, 'mats': [0, 45, 47]}]\nC:\\
# Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-0
# 9-23-d49817\\renders2\\zztest\\test.png\n"}

# ==============================================================================================================
# [0282] 2026-09-23 12:49:07  blender  ok
# ==============================================================================================================
import bpy, os
# cleanup test workshop
sc=bpy.data.scenes.get("WS_zztest")
for c in ("WS_zztest_Pieces","WS_zztest_Assembly"):
    col=bpy.data.collections.get(c)
    if col:
        for o in list(col.objects): bpy.data.objects.remove(o)
        bpy.data.collections.remove(col)
for o in list(bpy.data.objects):
    if o.name.startswith("WS_zztest"): bpy.data.objects.remove(o)
if sc: bpy.data.scenes.remove(sc)
t=bpy.data.texts.get("ws_zztest"); 
if t: bpy.data.texts.remove(t)
for m in list(bpy.data.meshes):
    if m.name.startswith("WS_zztest") and m.users==0: bpy.data.meshes.remove(m)
# kit piece list
vk=bpy.data.collections["VK_Pieces"]
names=sorted(o.name for o in vk.objects)
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
lines=[]
for n in names:
    o=bpy.data.objects[n]; bb=[o.matrix_world.inverted()@ (o.matrix_world@__import__('mathutils').Vector(c)) for c in o.bound_box]
    dims=o.dimensions
    lines.append(f"{n}\t{dims.x:.2f}x{dims.y:.2f}x{dims.z:.2f}\ttris={sum(len(p.vertices)-2 for p in o.data.polygons)}")
open(os.path.join(D,"kit_pieces.txt"),"w").write("\n".join(lines))
nat=bpy.data.collections.get("VK_NaturePieces")
print(len(names), len(nat.objects) if nat else 0)
print([s.name for s in bpy.data.scenes])
# ---- result ----
# {"result":"Code executed successfully: 107 39\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n"}

# ==============================================================================================================
# [0283] 2026-09-23 12:49:16  blender  ok
# ==============================================================================================================
import bpy
g={}; exec(bpy.data.texts["vk_helpers"].as_string(),g)
sp=g['all_specs'](); print(len(sp))
missing=[n for n,_,_ in sp if n not in bpy.data.collections["VK_Pieces"].objects]
print(len(missing), missing[:10])
print({n: [c.name for c in bpy.data.objects[n].users_collection] for n in missing[:5] if n in bpy.data.objects})
# ---- result ----
# {"result":"Code executed successfully: 106\n0 []\n{}\n"}

# ==============================================================================================================
# [0284] 2026-09-23 12:51:12  blender  ok
# ==============================================================================================================
import bpy, os
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"ws_common.py")).read()
t=bpy.data.texts["ws_common"]; t.clear(); t.write(src)
tm=bpy.data.texts.new("ws_zztest"); tm.write('''
def zz_block(k):
    k.box((0,0,0.5),(1.0,1.0,1.0),STONE,bevel=0.05,segs=2)
WS_SPECS=[("SM_VK_ZZTest_Block",zz_block,dict(wobble=False,grime=True))]
EXTRA_SPECS+=WS_SPECS
''')
exec(src)
b=ws_build("zztest"); me1=b[0].data.name
sc,coll,asm=ws_scene("zztest"); g=ws_ns("zztest")
inst=g['place_v'](asm,"SM_VK_ZZTest_Block",3,0,0,0,(0,0,0),{})
b=ws_build("zztest"); print(me1,b[0].data.name,inst.data.name, len(b[0].data.materials), b[0].name)
# cleanup
for c in ("WS_zztest_Pieces","WS_zztest_Assembly"):
    col=bpy.data.collections.get(c)
    for o in list(col.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)
for o in list(bpy.data.objects):
    if o.name.startswith("WS_zztest"): bpy.data.objects.remove(o)
bpy.data.scenes.remove(bpy.data.scenes["WS_zztest"]); bpy.data.texts.remove(bpy.data.texts["ws_zztest"])
for m in list(bpy.data.meshes):
    if m.users==0 and (m.name.startswith("SM_VK_ZZ") or m.name.startswith("WS_zztest") or m.name.startswith("__wstmp")): bpy.data.meshes.remove(m)
print([s.name for s in bpy.data.scenes])
# ---- result ----
# {"result":"Code executed successfully: SM_VK_ZZTest_Block.001 SM_VK_ZZTest_Block.001 SM_VK_ZZTest_Block.001 52 SM_VK_ZZTest_Block\n['MedievalColony', 
# 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'VillageKit']\n"}

# ==============================================================================================================
# [0285] 2026-09-23 12:59:22  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read()
t=bpy.data.texts.get("vk_terrain") or bpy.data.texts.new("vk_terrain"); t.clear(); t.write(src)
g={}
try:
    exec(src,g)
    t0=time.time(); P=g['tk_build_pieces'](); print("pieces",time.time()-t0)
    for k,o in P.items(): print(o.name,len(o.data.vertices),len(o.data.polygons))
except Exception:
    print(traceback.format_exc()[-2500:])
# ---- result ----
# {"result":"Code executed successfully: pieces 0.03630423545837402\nSM_VKT_Cliff_Full_A 49 36\nSM_VKT_Cliff_Edge_A 164 162\nSM_VKT_Cliff_Outer_A 105 94
# \nSM_VKT_Cliff_Inner_A 133 138\nSM_VKT_Cliff_Saddle_A 210 188\nSM_VKT_Shore_Edge_A 145 156\nSM_VKT_Shore_Outer_A 106 110\nSM_VKT_Shore_Inner_A 116 130
# \nSM_VKT_Shore_Saddle_A 194 176\nSM_VKT_Shore_Bed_A 49 36\nSM_VKT_WaterQuad 4 1\n"}

# ==============================================================================================================
# [0286] 2026-09-23 12:59:55  blender  ok
# ==============================================================================================================
import bpy, os, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read()
t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
try:
    exec(src,g); g['_CACHE'].clear()
    f=g['tk_test_T1']()
    print(len(f))
    import collections
    print(collections.Counter((x[0],x[4]) for x in f).most_common(20))
    for x in f[:6]: print(x)
except Exception:
    print(traceback.format_exc()[-2500:])
# ---- result ----
# {"result":"Code executed successfully: 996\n[(('SM_VKT_Cliff_Saddle_A', 'tcol'), 160), (('SM_VKT_Shore_Saddle_A', 'tcol'), 160), (('SM_VKT_Shore_Outer
# _A', 'tcol'), 136), (('SM_VKT_Shore_Bed_A', 'tcol'), 112), (('SM_VKT_Shore_Edge_A', 'tcol'), 108), (('SM_VKT_Cliff_Edge_A', 'tcol'), 80), (('SM_VKT_Cl
# iff_Outer_A', 'tcol'), 80), (('SM_VKT_Cliff_Inner_A', 'tcol'), 80), (('SM_VKT_Shore_Inner_A', 'tcol'), 80)]\n('SM_VKT_Cliff_Edge_A', 0, 1, 'CLIFF', 't
# col', (2.0, 0.0), frozenset({(1.0, 0.0, 0.15, 0.0)}), frozenset({(1.0, 0.0, 0.15, 0.0)}))\n('SM_VKT_Cliff_Edge_A', 0, 1, 'CLIFF', 'tcol', (1.7803, -0.
# 0146), frozenset({(1.0, 0.0, 0.6, 0.0)}), frozenset({(1.0, 0.0, 0.6, 0.0)}))\n('SM_VKT_Cliff_Edge_A', 0, 1, 'CLIFF', 'tcol', (1.46, -0.1504), frozense
# t({(0.45, 1.0, 0.0, 0.0), (0.9, 0.0, 0.4, 0.0)}), frozenset({(0.45, 1.0, 0.0, 0.0), (0.9, 0.0, 0.4, 0.0)}))\n('SM_VKT_Cliff_Edge_A', 0, 1, 'CLIFF', 't

# ==============================================================================================================
# [0287] 2026-09-23 13:00:17  blender  ok
# ==============================================================================================================
import bpy, os, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read()
t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
exec(src,g); g['_CACHE'].clear()
f=g['tk_test_T1']()
print(len(f)); print(collections.Counter((x[0],x[4]) for x in f).most_common(20))
for x in f[:4]: print(x)
# ---- result ----
# {"result":"Code executed successfully: 0\n[]\n"}

# ==============================================================================================================
# [0288] 2026-09-23 13:00:58  blender  ok
# ==============================================================================================================
import bpy, os, traceback, collections, time
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read()
t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
exec(src,g); g['_CACHE'].clear()
t0=time.time()
try:
    f,c=g['tk_test_T3'](60)
    print("T3",len(f),"checked",c,time.time()-t0)
    print(collections.Counter(x[4] for x in f))
    for x in f[:8]: print(x)
except Exception: print(traceback.format_exc()[-2000:])
# ---- result ----
# {"result":"Code executed successfully: T3 0 checked 50669 11.765186071395874\nCounter()\n"}

# ==============================================================================================================
# [0289] 2026-09-23 13:01:25  blender  ok
# ==============================================================================================================
import bpy, os, traceback, time
import numpy as np
g={}
exec(bpy.data.texts["vk_terrain"].as_string(),g)
G=g['tk_random_grid'](7,W=14,H=12,mode="smooth")
# add some water, a mesa and a saddle
G.level[1:4,1:5]=0; G.water[1:3,1:4]=True
G.level[8,10]=3; G.level[9,11]=3
print(G.level[::-1])
coll=g['tk_terrain_coll']("VK_TerrainTest")
for o in list(coll.objects): bpy.data.objects.remove(o)
t0=time.time()
objs=g['tk_build_chunks'](G,prefix="VKTT",coll=coll)
print("chunks",time.time()-t0,[ (o.name,len(o.data.polygons)) for o in objs])
bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.25)
print("T4 rays",n,"bad",len(bad),bad[:10])
# ---- result ----
# {"result":"Code executed successfully: [[0 1 1 2 3 3 2 2 2 2 1 1 1 1]\n [0 1 1 3 4 3 3 2 2 2 2 1 1 1]\n [1 1 1 2 3 3 2 2 2 2 2 3 1 1]\n [1 1 2 2 2 2 2
#  2 2 2 3 2 2 1]\n [1 1 2 2 2 2 2 2 2 2 2 2 2 1]\n [1 1 2 2 2 2 2 2 2 2 2 2 2 1]\n [1 1 2 2 2 2 2 2 2 2 2 2 2 1]\n [1 1 2 2 2 2 2 1 1 1 1 1 1 1]\n [1 0
#  0 0 0 1 1 1 1 1 1 1 1 1]\n [0 0 0 0 0 1 1 1 1 1 1 1 0 0]\n [0 0 0 0 0 1 0 0 0 0 0 0 0 0]\n [0 0 0 0 0 0 0 0 0 0 0 0 0 0]]\nchunks 0.1465013027191162 
# [('VKTT_Chunk_0_0', 25972), ('VKTT_Water_0_0', 83)]\nT4 rays 20592 bad 0 []\n"}

# ==============================================================================================================
# [0290] 2026-09-23 13:01:37  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace['shot']
shot("terrain_t1",(1262,-22,30),(1221,17,2),lens=30)
shot("terrain_t1_close",(1236,12,9),(1226,22,3),lens=28)
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0291] 2026-09-23 13:03:06  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, numpy as np
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_tex2.py"),encoding="utf8").read(); t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
save_prev=bpy.app.driver_namespace['save_prev']
try:
    t0=time.time(); gr=ns['gen_grass'](); t1=time.time(); cl=ns['gen_cliff'](); t2=time.time(); ns['gen_terrain_macro']()
    print(t1-t0,t2-t1)
    save_prev(np.tile(gr,(2,2,1))[::2,::2],"grass_tile.png"); save_prev(cl,"cliff_bc.png")
except Exception: print(traceback.format_exc()[-2000:])
# ---- result ----
# {"result":"Code executed successfully: 2.1150221824645996 6.843318700790405\n"}

# ==============================================================================================================
# [0292] 2026-09-23 13:04:11  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, numpy as np
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_tex2.py"),encoding="utf8").read(); t=bpy.data.texts["vk_tex2"]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
save_prev=bpy.app.driver_namespace['save_prev']
gr=ns['gen_grass'](); cl=ns['gen_cliff']()
save_prev(np.concatenate([np.tile(gr,(2,2,1))[::2,::2],cl[::2,::2].repeat(2,0).repeat(2,1)[:1024,:1024]],1),"terrain_tex2.png")
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0293] 2026-09-23 13:06:11  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, numpy as np
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_tex2","vk_tex2.py"),("vk_terrain","vk_terrain.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts[n]; t.clear(); t.write(src)
ns={}
for n in ("vk_tex","vk_texgen","vk_mat","vk_tex2"): exec(bpy.data.texts[n].as_string(),ns)
try:
    t0=time.time(); ns['gen_dirt'](); ns['gen_cobble'](); ns['gen_sand'](); print("tex",time.time()-t0)
    print([n for n in ("T_VK_Moss_BC","T_VK_Moss_H") if n in bpy.data.images])
    g={}; exec(bpy.data.texts["vk_terrain"].as_string(),g)
    G=g['tk_random_grid'](7,W=14,H=12,mode="smooth")
    G.level[1:4,1:5]=0; G.water[1:3,1:4]=True; G.level[8,10]=3; G.level[9,11]=3
    G.ground[5:7,3:9]=2; G.ground[4,2:12]=1; G.ground[9:11,2:4]=4
    g['tk_ground_ctl'](G)
    m=g['terrain_material'](W=G.W,H=G.H)
    print(m.name,len(m.node_tree.nodes))
    coll=g['tk_terrain_coll']("VK_TerrainTest")
    for o in list(coll.objects): bpy.data.objects.remove(o)
    objs=g['tk_build_chunks'](G,prefix="VKTT",coll=coll)
    shot=bpy.app.driver_namespace['shot']
    shot("terrain_t2",(1262,-22,30),(1221,17,2),lens=30)
    shot("terrain_t2_close",(1236,12,9),(1226,22,3),lens=28)
except Exception: print(traceback.format_exc()[-2500:])
# ---- result ----
# {"result":"Code executed successfully: tex 6.052122116088867\n['T_VK_Moss_BC', 'T_VK_Moss_H']\nM_VK_Terrain 107\n"}

# ==============================================================================================================
# [0294] 2026-09-23 13:07:10  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, numpy as np
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}; exec(src,g)
try:
    G=g['tk_random_grid'](7,W=14,H=12,mode="smooth")
    G.level[1:4,1:5]=0; G.water[1:3,1:4]=True; G.level[8,10]=3; G.level[9,11]=3
    G.ground[5:7,3:9]=2; G.ground[4,2:12]=1; G.ground[9:11,2:4]=4
    G.stiff[5:7,3:9]=True
    coll=g['tk_terrain_coll']("VK_TerrainTest")
    for o in list(coll.objects): bpy.data.objects.remove(o)
    disp=g['make_displace'](G)
    t0=time.time()
    recs=list(g['tk_tiles'](G)); arr=g['tk_assemble'](recs,disp); print("assemble+D",time.time()-t0,"detJ",arr["T"]["detJ"])
    objs=g['tk_build_chunks'](G,prefix="VKTT",coll=coll,displace=disp)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.3)
    print("T4",n,len(bad),bad[:5])
    shot=bpy.app.driver_namespace['shot']
    shot("terrain_t3",(1262,-22,30),(1221,17,2),lens=30)
    shot("terrain_t3_close",(1236,12,9),(1226,22,3),lens=28)
except Exception: print(traceback.format_exc()[-2500:])
# ---- result ----
# {"result":"Code executed successfully: assemble+D 0.24403643608093262 detJ 0.8076593661207437\nT4 14300 1 [(28.220000000000002, 4.220000000000001, 'mi
# ss')]\n"}

# ==============================================================================================================
# [0295] 2026-09-23 13:09:47  blender  ERROR
# ==============================================================================================================
import bpy, os, time, traceback, numpy as np
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}; exec(src,g)
try:
    g['tk_build_ramps']()
    for n in ("SM_VKT_Ramp_HalfE_A","SM_VKT_Ramp_HalfW_A","SM_VKT_Ramp_Mid_A"):
        o=bpy.data.objects[n]; print(n,len(o.data.vertices),len(o.data.polygons))
    # test grid with ramps
    G=g['TGrid'](10,8)
    G.level[:,:]=1; G.level[4:,:]=2; G.level[6:,3:7]=3
    G.ramp[3,2]=1; G.ramp[3,6]=1; G.ramp[3,7]=1   # single ramp at x=2, double ramp at x=6-7 (level1->2)
    G.ramp[5,4]=1                                  # level 2->3 single
    G.ground[G.ramp>0]=1; G.ground[2,:]=1
    coll=g['tk_terrain_coll']("VK_TerrainTest")
    for o in list(coll.objects): bpy.data.objects.remove(o)
    g['_CACHE'].clear()
    objs=g['tk_build_chunks'](G,prefix="VKTR",coll=coll,origin=(1200,-60,0),displace=g['make_displace'](G))
    g['tk_ground_ctl'](G); g['tk_set_ctl_mapping'](G)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.2)
    print("T4",n,len(bad),bad[:6])
    shot=bpy.app.driver_namespace['shot']
    shot("terrain_ramps",(1203,-78,10),(1215,-50,2),lens=30)
except Exception: print(traceback.format_exc()[-2500:])
# ---- result ----
# {"result":"Code executed successfully: Traceback (most recent call last):\n File \"<string>\", line 6, in <module>\n File \"<string>\", line 850, in t
# k_build_ramps\n File \"<string>\", line 838, in gen_ramp_half_e\n File \"<string>\", line 792, in _poly_yz\n File \"<string>\", line 792, in <listcomp
# >\nIndexError: list index out of range\n\n"}

# ==============================================================================================================
# [0296] 2026-09-23 13:10:29  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, numpy as np
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}; exec(src,g)
try:
    g['tk_build_ramps']()
    for n in ("SM_VKT_Ramp_HalfE_A","SM_VKT_Ramp_HalfW_A","SM_VKT_Ramp_Mid_A"):
        o=bpy.data.objects[n]; print(n,len(o.data.vertices),len(o.data.polygons))
    G=g['TGrid'](10,8)
    G.level[:,:]=1; G.level[4:,:]=2; G.level[6:,3:7]=3
    G.ramp[3,2]=1; G.ramp[3,6]=1; G.ramp[3,7]=1
    G.ramp[5,4]=1
    G.ground[G.ramp>0]=1; G.ground[2,:]=1
    coll=g['tk_terrain_coll']("VK_TerrainTest")
    for o in list(coll.objects): bpy.data.objects.remove(o)
    g['_CACHE'].clear()
    objs=g['tk_build_chunks'](G,prefix="VKTR",coll=coll,origin=(1200,-60,0),displace=g['make_displace'](G))
    recs=[r for r in g['tk_tiles'](G) if r[3]=="Ramp"]; print(recs)
    g['tk_ground_ctl'](G); g['tk_set_ctl_mapping'](G)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.2)
    print("T4",n,len(bad),bad[:6])
    shot=bpy.app.driver_namespace['shot']
    shot("terrain_ramps",(1203,-78,10),(1215,-50,2),lens=30)
except Exception: print(traceback.format_exc()[-2500:])
# ---- result ----
# {"result":"Code executed successfully: SM_VKT_Ramp_HalfE_A 153 152\nSM_VKT_Ramp_HalfW_A 153 152\nSM_VKT_Ramp_Mid_A 91 72\n[(2, 4, 2, 'Ramp', 'HalfE', 
# 0, 'A'), (3, 4, 2, 'Ramp', 'HalfW', 0, 'A'), (6, 4, 2, 'Ramp', 'HalfE', 0, 'A'), (7, 4, 2, 'Ramp', 'Mid', 0, 'A'), (8, 4, 2, 'Ramp', 'HalfW', 0, 'A'),
#  (4, 6, 3, 'Ramp', 'HalfE', 0, 'A'), (5, 6, 3, 'Ramp', 'HalfW', 0, 'A')]\nT4 14175 0 []\n"}

# ==============================================================================================================
# [0297] 2026-09-23 13:11:57  blender  ok
# ==============================================================================================================
import bpy
print(sorted(o.name for o in bpy.data.collections["VK_NaturePieces"].objects))
print([o.name for o in bpy.data.collections["VK_Pieces"].objects if "Crop" in o.name or "Field" in o.name or "Tree" in o.name or "Fence" in o.name or "Road" in o.name])
print([s.name for s in bpy.data.scenes])
# ---- result ----
# {"result":"Code executed successfully: ['SM_VK_Bush_Autumn', 'SM_VK_Bush_Berry', 'SM_VK_Bush_Hydrangea', 'SM_VK_Bush_Large', 'SM_VK_Bush_Round', 'SM_V
# K_Log_Fallen', 'SM_VK_Mushrooms_Brown', 'SM_VK_Mushrooms_Glow', 'SM_VK_Mushrooms_Red', 'SM_VK_Plant_Fern', 'SM_VK_Plant_Reeds', 'SM_VK_Plant_TallGrass
# ', 'SM_VK_Plant_Wildflowers', 'SM_VK_Pond', 'SM_VK_Rock_Boulder_A', 'SM_VK_Rock_Boulder_B', 'SM_VK_Rock_Boulder_Flat', 'SM_VK_Rock_Cluster', 'SM_VK_Ro
# ck_Outcrop', 'SM_VK_Rock_Pebbles', 'SM_VK_Rock_Small_A', 'SM_VK_Rock_Small_B', 'SM_VK_Rock_Standing', 'SM_VK_Rock_Standing_B', 'SM_VK_Rock_StepStones'
# , 'SM_VK_Stump', 'SM_VK_Tree_Apple', 'SM_VK_Tree_Birch', 'SM_VK_Tree_Birch_Single', 'SM_VK_Tree_Blossom', 'SM_VK_Tree_Dead', 'SM_VK_Tree_Oak_A', 'SM_V
# K_Tree_Oak_Autumn', 'SM_VK_Tree_Oak_B', 'SM_VK_Tree_Pine_A', 'SM_VK_Tree_Pine_B', 'SM_VK_Tree_Pine_Young', 'SM_VK_Tree_Sapling', 'SM_VK_Tree_Willow']\

# ==============================================================================================================
# [0298] 2026-09-23 13:14:40  blender  ERROR
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    exec(bpy.data.texts["vk_helpers"].as_string(),g)
    exec(bpy.data.texts["vk_terrain"].as_string(),g)
    exec(bpy.data.texts["vk_terrain_demo"].as_string(),g)
    # remove the test terrain
    tc=bpy.data.collections.get("VK_TerrainTest")
    if tc:
        for o in list(tc.objects): bpy.data.objects.remove(o)
    t0=time.time()
    G,errs,objs=g['build_terrain_demo']()
    print("demo",time.time()-t0,"errs",errs[:10],len(errs))
    print([(o.name,len(o.data.polygons)) for o in objs])
    print(len(bpy.data.collections["VK_TerrainVillage"].objects))
    bpy.app.driver_namespace['tk_G']=G
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: Traceback (most recent call last):\n File \"<string>\", line 15, in <module>\n File \"<string>\", line 201, in 
# build_terrain_demo\n File \"<string>\", line 722, in tk_ground_ctl\nTypeError: expected sequence size 320, got 3072\n\n"}

# ==============================================================================================================
# [0299] 2026-09-23 13:15:51  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    exec(bpy.data.texts["vk_helpers"].as_string(),g)
    exec(bpy.data.texts["vk_terrain"].as_string(),g)
    exec(bpy.data.texts["vk_terrain_demo"].as_string(),g)
    t0=time.time()
    G,errs,objs=g['build_terrain_demo']()
    print("demo",time.time()-t0,"errs",errs[:10],len(errs))
    print([(o.name,len(o.data.polygons)) for o in objs])
    print(len(bpy.data.collections["VK_TerrainVillage"].objects))
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.5)
    print("T4",n,len(bad),bad[:5])
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: demo 3.4676661491394043 errs [] 0\n[('VKT_Chunk_0_0', 21452), ('VKT_Water_0_0', 51), ('VKT_Chunk_1_0', 18144), 
# ('VKT_Water_1_0', 50), ('VKT_Chunk_2_0', 978), ('VKT_Water_2_0', 3), ('VKT_Chunk_0_1', 15406), ('VKT_Chunk_1_1', 14032), ('VKT_Chunk_2_1', 972)]\n784\
# nT4 25668 0 []\n"}

# ==============================================================================================================
# [0300] 2026-09-23 13:16:46  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace['shot']
shot("demo_aerial",(1305,-45,62),(1247,36,4),lens=30,res=(1600,900))
shot("demo_plaza",(1262,26,14),(1250,44,4),lens=28,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0301] 2026-09-23 13:18:11  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    G,errs,objs=g['build_terrain_demo']()
    shot=bpy.app.driver_namespace['shot']
    shot("demo_river",(1262,-14,9),(1246,8,0),lens=30,res=(1600,900))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0302] 2026-09-23 13:18:48  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    G,errs,objs=g['build_terrain_demo']()
    print([ (o.name,[m.name for m in o.data.materials]) for o in objs if "Water" in o.name][:2])
    shot=bpy.app.driver_namespace['shot']
    shot("demo_river2",(1262,-14,9),(1246,8,0),lens=30,res=(1600,900))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: [('VKT_Water_0_0', ['M_VKT_Water']), ('VKT_Water_1_0', ['M_VKT_Water'])]\n"}

# ==============================================================================================================
# [0303] 2026-09-23 13:19:30  blender  ok
# ==============================================================================================================
import bpy
bpy.ops.wm.save_mainfile()
print([s.name for s in bpy.data.scenes])
print({c.name:len(c.objects) for c in bpy.data.collections if c.name.startswith("WS_")})
print(sorted(t.name for t in bpy.data.texts if t.name.startswith("ws_")))
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\n['MedievalColony', 'Scene', 'SpriteRig', 'StoneWallKit', 'TreeAsset', 'V
# illageKit', 'WS_construction', 'WS_defence', 'WS_frontier', 'WS_humble', 'WS_industry', 'WS_town', 'WS_water']\n{'WS_construction_Assembly': 133, 'WS_
# construction_Pieces': 15, 'WS_defence_Assembly': 53, 'WS_defence_Pieces': 23, 'WS_frontier_Assembly': 21, 'WS_frontier_Pieces': 31, 'WS_humble_Assembl
# y': 15, 'WS_humble_Pieces': 18, 'WS_industry_Assembly': 37, 'WS_industry_Pieces': 27, 'WS_town_Assembly': 16, 'WS_town_Pieces': 36, 'WS_water_Assembly
# ': 22, 'WS_water_Pieces': 13}\n['ws_common', 'ws_construction', 'ws_defence', 'ws_frontier', 'ws_humble', 'ws_industry', 'ws_town', 'ws_water']\n"}

# ==============================================================================================================
# [0304] 2026-09-23 13:21:44  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    lg=bpy.data.objects.get("SM_VKT_LipGrass")
    if lg: bpy.data.objects.remove(lg)
    t0=time.time(); G,errs,objs=g['build_terrain_demo'](); print(time.time()-t0, errs)
    print(len(bpy.data.collections["VK_TerrainVillage"].objects), sum(1 for o in bpy.data.collections["VK_TerrainVillage"].objects if "LipGrass" in o.name))
    shot=bpy.app.driver_namespace['shot']
    shot("demo_lip",(1236,40,12),(1222,52,5),lens=30,res=(1600,900))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: 4.977667570114136 []\n1297 500\n"}

# ==============================================================================================================
# [0305] 2026-09-23 13:22:29  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace['shot']
shot("demo_lip",(1238,17,4.2),(1248,27.5,2.4),lens=30,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0306] 2026-09-23 13:22:58  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace['shot']
shot("demo_lip",(1256.5,18.5,4.5),(1264,27.5,2.3),lens=32,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0307] 2026-09-23 13:24:14  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    g['tk_build_lipgrass']()
    G,errs,objs=g['build_terrain_demo']()
    shot=bpy.app.driver_namespace['shot']
    shot("demo_lip2",(1256.5,18.5,4.5),(1264,27.5,2.3),lens=32,res=(1600,900))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0308] 2026-09-23 13:25:23  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain"): exec(bpy.data.texts[n].as_string(),g)
    t0=time.time(); f,c=g['tk_test_T3r'](40); print("T3r",len(f),c,time.time()-t0)
    print(collections.Counter(x[4] for x in f)); 
    for x in f[:8]: print(x)
    nr=0
    import numpy as np
    for s in range(3):
        rng=np.random.default_rng(500+s); G=g['tk_random_grid'](500+s,mode="smooth"); G.water[:]=False; g['tk_add_random_ramps'](G,rng,80)
        nr+=int((G.ramp>0).sum())
        coll=g['tk_terrain_coll']("VK_TerrainTest")
        for o in list(coll.objects): bpy.data.objects.remove(o)
        objs=g['tk_build_chunks'](G,prefix="VKTZ",coll=coll,origin=(1200,-120,0),displace=g['make_displace'](G))
        bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.3)
        print("T4",s,n,len(bad),bad[:3])
    print("ramps in T4 grids",nr)
    for o in list(coll.objects): bpy.data.objects.remove(o)
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: T3r 116 20911 0.6738111972808838\nCounter({'pos': 116})\n(0, 10, 2, 3, 'pos', ('Ramp', 'HalfE', 0), ('Cliff', 1
# , 2))\n(0, 11, 2, 3, 'pos', ('Ramp', 'HalfW', 0), ('Cliff', 1, 1))\n(0, 4, 4, 2, 'pos', ('Ramp', 'HalfW', 3), ('Cliff', 1, 0))\n(0, 4, 5, 2, 'pos', ('
# Ramp', 'HalfE', 3), ('Cliff', 1, 3))\n(0, 2, 7, 1, 'pos', ('Ramp', 'HalfW', 3), ('Cliff', 1, 2))\n(0, 2, 8, 1, 'pos', ('Ramp', 'HalfE', 3), ('Cliff', 
# 1, 3))\n(1, 2, 1, 2, 'pos', ('Ramp', 'HalfW', 3), ('Cliff', 1, 3))\n(1, 2, 2, 2, 'pos', ('Ramp', 'HalfE', 3), ('Cliff', 1, 2))\nT4 0 12100 0 []\nT4 1 
# 12100 0 []\nT4 2 12100 0 []\nramps in T4 grids 4\n"}

# ==============================================================================================================
# [0309] 2026-09-23 13:26:50  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain"): exec(bpy.data.texts[n].as_string(),g)
    g['tk_build_ramps'](); g['_CACHE'].clear(); g['_SIG'].clear()
    f,c=g['tk_test_T3r'](60); print("T3r",len(f),c)
    for x in f[:8]: print(x)
    f2,c2=g['tk_test_T3'](30); print("T3",len(f2),c2)
    print("T1",len(g['tk_test_T1']()))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: T3r 0 31582\nT3 0 25970\nT1 0\n"}

# ==============================================================================================================
# [0310] 2026-09-23 13:28:48  blender  ERROR
# ==============================================================================================================
import bpy, os, time, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    g['tk_build_ramps'](); g['tk_build_stairs'](); g['_CACHE'].clear(); g['_SIG'].clear()
    for n in ("SM_VKT_Stair_HalfE_A","SM_VKT_Stair_Mid_A"): o=bpy.data.objects[n]; print(n,len(o.data.polygons))
    f,c=g['tk_test_T3r'](60); print("T3r",len(f),c)
    for x in f[:6]: print(x)
    G,errs,objs=g['build_terrain_demo'](); print("demo errs",errs)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.4); print("T4",n,len(bad))
    shot=bpy.app.driver_namespace['shot']
    shot("demo_stairs",(1236,34,12),(1222,46,6),lens=30,res=(1600,900))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: Traceback (most recent call last):\n File \"<string>\", line 8, in <module>\n File \"<string>\", line 1044, in 
# tk_build_stairs\n File \"<string>\", line 1038, in gen_stair_half_e\n File \"<string>\", line 799, in _poly_yz\n File \"<string>\", line 799, in <list
# comp>\nIndexError: list index out of range\n\n"}

# ==============================================================================================================
# [0311] 2026-09-23 15:41:56  blender  ERROR
# ==============================================================================================================
import bpy, os, time, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    g['tk_build_ramps'](); g['tk_build_stairs'](); g['_CACHE'].clear(); g['_SIG'].clear()
    for n in ("SM_VKT_Stair_HalfE_A","SM_VKT_Stair_Mid_A"): o=bpy.data.objects[n]; print(n,len(o.data.polygons))
    f,c=g['tk_test_T3r'](60); print("T3r",len(f),c)
    for x in f[:6]: print(x)
    G,errs,objs=g['build_terrain_demo'](); print("demo errs",errs)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.4); print("T4",n,len(bad))
    shot=bpy.app.driver_namespace.get('shot')
    print(shot is not None)
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: Traceback (most recent call last):\n File \"<string>\", line 8, in <module>\n File \"<string>\", line 1046, in 
# tk_build_stairs\n File \"<string>\", line 1040, in gen_stair_half_e\n File \"<string>\", line 799, in _poly_yz\n File \"<string>\", line 799, in <list
# comp>\nIndexError: list index out of range\n\n"}

# ==============================================================================================================
# [0312] 2026-09-23 15:42:10  blender  ok
# ==============================================================================================================
import bpy, math
g={}
for n in ("vk_helpers","vk_nature","vk_terrain"): exec(bpy.data.texts[n].as_string(),g)
P=g['P_CLIFF']; TOP_ROW=g['TOP_ROW']; CL=g['CLIFF_LAST']; sz=g['_stair_z']; SO=g['STAIR_OUT']
prof=[(1.5-P[i][0],P[i][1]) for i in range(TOP_ROW,CL+1)]
for i in range(len(prof)-1):
    (y0,z0),(y1,z1)=prof[i],prof[i+1]
    print(i,prof[i], round(z0-sz(y0),3))
print([ (y,sz(y)) for y in (-0.3,-0.25,-0.2,0.0,0.3)])
# ---- result ----
# {"result":"Code executed successfully: 0 (0.28, -0.015) 0.485\n1 (0.10000000000000009, -0.06) 0.69\n2 (-0.040000000000000036, -0.15) 0.6\n3 (0.0200000
# 00000000018, -0.24) 0.51\n4 (-0.06000000000000005, -0.62) 0.13\n5 (-0.26, -0.68) 0.32\n6 (-0.19999999999999996, -0.8) -0.05\n7 (-0.30000000000000004, 
# -1.06) -0.06\n8 (-0.19999999999999996, -1.34) -0.59\n9 (0.050000000000000044, -1.52) -0.77\n[(-0.3, -1.0), (-0.25, -1.0), (-0.2, -0.75), (0.0, -0.75),
#  (0.3, -0.5)]\n"}

# ==============================================================================================================
# [0313] 2026-09-23 15:43:15  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n,f in (("vk_terrain","vk_terrain.py"),("vk_terrain_demo","vk_terrain_demo.py")):
    src=open(os.path.join(D,f),encoding="utf8").read(); t=bpy.data.texts.get(n) or bpy.data.texts.new(n); t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    g['tk_build_ramps'](); g['tk_build_stairs'](); g['_CACHE'].clear(); g['_SIG'].clear()
    for n in ("SM_VKT_Stair_HalfE_A","SM_VKT_Stair_Mid_A"): o=bpy.data.objects[n]; print(n,len(o.data.polygons))
    f,c=g['tk_test_T3r'](60); print("T3r",len(f),c)
    for x in f[:6]: print(x)
    G,errs,objs=g['build_terrain_demo'](); print("demo errs",errs)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.4); print("T4",n,len(bad))
    print('shot' in bpy.app.driver_namespace)
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: SM_VKT_Stair_HalfE_A 149\nSM_VKT_Stair_Mid_A 13\nT3r 48 31582\n(0, 10, 2, 3, 'pos', ('Stair', 'HalfE', 0), ('Cl
# iff', 1, 2))\n(0, 11, 2, 3, 'pos', ('Stair', 'HalfW', 0), ('Cliff', 1, 1))\n(1, 7, 3, 4, 'pos', ('Stair', 'HalfW', 3), ('Cliff', 1, 3))\n(1, 7, 4, 4, 
# 'pos', ('Stair', 'HalfE', 3), ('Cliff', 1, 1))\n(5, 9, 3, 3, 'pos', ('Cliff', 1, 3), ('Stair', 'HalfE', 1))\n(5, 9, 4, 3, 'pos', ('Cliff', 1, 2), ('St
# air', 'HalfW', 1))\ndemo errs []\nT4 40309 0\nTrue\n"}

# ==============================================================================================================
# [0314] 2026-09-23 15:43:51  blender  ok
# ==============================================================================================================
import bpy, os, time, traceback, collections
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
src=open(os.path.join(D,"vk_terrain.py"),encoding="utf8").read(); t=bpy.data.texts["vk_terrain"]; t.clear(); t.write(src)
g={}
try:
    for n in ("vk_helpers","vk_nature","vk_terrain","vk_terrain_demo"): exec(bpy.data.texts[n].as_string(),g)
    g['tk_build_stairs'](); g['_CACHE'].clear(); g['_SIG'].clear()
    f,c=g['tk_test_T3r'](60); print("T3r",len(f),c)
    print("T1",len(g['tk_test_T1']()))
    G,errs,objs=g['build_terrain_demo'](); print("demo errs",errs)
    bad,n=g['tk_test_T4'](G,[o for o in objs if "Chunk" in o.name],step=0.4); print("T4",n,len(bad))
    shot=bpy.app.driver_namespace['shot']
    shot("demo_stairs",(1236,36,11),(1222,46,6),lens=30,res=(1600,900))
except Exception: print(traceback.format_exc()[-3000:])
# ---- result ----
# {"result":"Code executed successfully: T3r 0 31582\nT1 0\ndemo errs []\nT4 40309 0\n"}

# ==============================================================================================================
# [0315] 2026-09-23 15:44:25  blender  ok
# ==============================================================================================================
import bpy
shot=bpy.app.driver_namespace['shot']
shot("demo_stairs",(1214,34,10),(1222,46.5,4.8),lens=32,res=(1600,900))
# ---- result ----
# {"result":"Code executed successfully: "}

# ==============================================================================================================
# [0316] 2026-09-23 15:44:59  blender  ok
# ==============================================================================================================
import bpy, os, hashlib
D=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
for n in ("vk_helpers","vk_mat","vk_tex2","ws_common"):
    a=bpy.data.texts[n].as_string(); b=open(os.path.join(D,n+".py"),encoding="utf8").read()
    print(n, a==b, len(a), len(b))
for a in ("humble","frontier","construction","skyline","town","water","industry","defence"):
    t=bpy.data.texts.get("ws_"+a); f=os.path.join(D,"ws_"+a+".py")
    fs=open(f,encoding="utf8").read() if os.path.exists(f) else None
    print(a, t is not None, (t.as_string()==fs) if t and fs else None, bpy.data.scenes.get("WS_"+a) is not None)
# ---- result ----
# {"result":"Code executed successfully: vk_helpers True 174915 174915\nvk_mat True 13155 13155\nvk_tex2 True 52700 52700\nws_common True 5974 5974\nhum
# ble True False True\nfrontier True True True\nconstruction True False True\nskyline True True True\ntown True True True\nwater True False True\nindust
# ry True True True\ndefence True False True\n"}

# ==============================================================================================================
# [0317] 2026-09-23 15:45:55  blender  ok
# ==============================================================================================================
import bpy
bpy.ops.wm.save_mainfile(); print("saved")
# ---- result ----
# {"result":"Code executed successfully: Info: Saved \"medievalDiorama.blend\"\nsaved\n"}
