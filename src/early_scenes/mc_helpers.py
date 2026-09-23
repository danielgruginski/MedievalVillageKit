
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
HALF=30.0
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

PATHS=[[(-1, 1), (0, -8), (0.5, -15), (1, -24), (2, -30)], [(-1, 1), (9, 3), (17, 3.5), (24, 5)], [(-1, 1), (-6, 8), (-11, 15), (-13, 19)], [(-1, 1), (-12, -1), (-20, -3), (-30, -3.5)]]
def seg_d(p,a,b):
    p=Vector(p);a=Vector(a);b=Vector(b);ab=b-a
    t=max(0,min(1,(p-a).dot(ab)/ab.length_squared)); return (p-(a+ab*t)).length
def path_d(x,y):
    return min(seg_d((x,y),pl[i],pl[i+1]) for pl in PATHS for i in range(len(pl)-1))
def place_z(x,y): return ground_h(x,y)

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
