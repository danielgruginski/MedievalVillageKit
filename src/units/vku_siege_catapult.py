# ===================== VKU SIEGE CATAPULT: the orcs' onager as an animated unit (2026-10-23) =====================
# Daniel (2026-10-23): "Do these tasks you mentioned" -- the card game's catapult as an animated unit for the RPG: the
# kit's onager (vki_props_orc.vki_orc_catapult, static SM_VKI_Prop_Siege_Catapult) with a rigged throwing arm and
# wheels and a load-and-throw clip. Model + rig + clips + export; no game wiring.
#
# Stage 1 (needs the kit: run inside blender/medievalDiorama.blend, which is never saved):
#     build_unit_blend(g)            g = vki_ns(); writes blender/vku_siege_catapult.blend (the unit's own file)
#   The geometry is vki_orc_catapult's own: the builder tags its parts (vki_orc_part) and this splits them -- frame,
#   four wheels, the arm (cut in two at ARM_CUT so Destroyed can snap it), the stone in the cup, the windlass. The
#   lashing rope and the stones stacked on the ground are left out; a rope from the windlass to the arm is added, and
#   (2026-10-23, Daniel: "Do the number 4") a basket of stones on the rear cross beam that Load takes the stone from.
# Stage 2 (inside blender/vku_siege_catapult.blend): build_rig(), build_clips(), checks, renders, export().
# Headless driver: tools/unit_catapult_run.py. Unity: Editor/Units/KitSiegeCatapultSetup.cs (see HANDOFF 140, 141).
# The package's Art/Units/SiegeCatapult is live in the open Unity editor: export elsewhere with set_export_dir /
# VKU_EXPORT_DIR / the driver's export_dir=<folder> and copy in by hand.
#
# Coordinates are the kit's: front (the way it throws and drives) -Y, up +Z; Unity sees (-x, z, -y), front +Z.
# Rig (Generic): Root (the skeleton's parent, never moves) and Motion (its sibling: root motion only, nothing skinned)
# point up with +Z toward the front so Motion imports with identity orientation (Insectoids/HANDOFF.md). Under Root:
# Frame -> Wheel_FL/FR/BL/BR, Arm -> Arm_Tip -> (Socket_Projectile, Stone), Windlass, Rope. Every part is weighted 1.0
# to one bone. The rope is stretched by its bone's Y scale (rest: hanging loose, 0.35 m); the stone in the cup is hidden by
# scaling the Stone bone to ~0. Socket_Projectile's +Z (Unity forward) points out of the cup: at the Throw clip's
# "Release" event it is the stone's launch direction.
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

ROOT = r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
BLEND = os.path.join(ROOT, "blender", "vku_siege_catapult.blend")
RENDERS = os.path.join(ROOT, "renders", "units", "siege_catapult")
PKG = os.path.join(ROOT, "unity", "com.danielgruginski.medievalkit")
EXPORT_LIVE = os.path.join(PKG, "Art", "Units", "SiegeCatapult")   # live: the open editor imports what lands here
# the export folder: the package's (default), or a staging folder outside it (env VKU_EXPORT_DIR, or the driver's
# `export_dir=<folder>` argument -> set_export_dir) to be copied in by hand when Unity is not playing
EXPORT = os.environ.get("VKU_EXPORT_DIR") or EXPORT_LIVE


def set_export_dir(path):
    """export (and read back) into `path` instead of the package's live Art/Units/SiegeCatapult"""
    global EXPORT
    EXPORT = os.path.normpath(path if os.path.isabs(path) else os.path.join(ROOT, path))   # relative: to the repo
    return EXPORT

UNIT = "VKU_SiegeCatapult"           # scene, FBX and prefab name
RIG = UNIT + "_Rig"
MESH = UNIT                          # the skinned mesh object
STONE = "SM_VKU_CatapultStone"       # the projectile, a static mesh of its own (the stone in the cup, at the origin)
GROUND = "VKU_Ground"
FPS = 30

# ---------------------------------------------------------------- the builder's numbers (vki_orc_catapult)
PIVOT = Vector((0.0, 0.25, 0.52))    # the skein: the arm's axle (rotation about +X)
ARM_END = Vector((0.0, 2.05, 0.95))  # the arm's end drawn back (the bind pose is the static piece's: drawn back)
ARM_HALF = 0.1                       # half the arm's depth (vki_orc_timber w 0.17, d 0.2)
ARM_CUT = 0.62                       # Destroyed snaps the arm here (fraction of its length; the bands are at .15/.55)
STONE_C = Vector((0.0, 2.1, 1.25))   # the stone in the cup
DRUM = Vector((0.0, 1.95, 0.95))     # the windlass's axis (x), radius DRUM_R
DRUM_R = 0.1
WHEEL_R = 0.34
WHEELS = {"FL": Vector((1.0, -1.35, 0.34)), "FR": Vector((-1.0, -1.35, 0.34)),
          "BL": Vector((1.0, 1.35, 0.34)), "BR": Vector((-1.0, 1.35, 0.34))}     # the engine's own left is +X
ROPE_DANGLE = (math.radians(-65.0), 0.35)   # the rope off the arm: hanging down and back from the drum (angle from +Y
                                            # toward +Z in the YZ plane, length from the drum's axis)
ROPE_REST = Vector((0.0, math.cos(ROPE_DANGLE[0]), math.sin(ROPE_DANGLE[0])))   # the rope bone's rest direction
PARTS_DROPPED = ("lash", "stack")
PART_BONE = {"frame": "Frame", "wheelFL": "Wheel_FL", "wheelFR": "Wheel_FR", "wheelBL": "Wheel_BL",
             "wheelBR": "Wheel_BR", "arm": "Arm", "armtip": "Arm_Tip", "stone": "Stone", "windlass": "Windlass",
             "rope": "Rope", "basket": "Frame"}
# the stone basket (2026-10-23, Daniel: "Do the number 4" -- the stone popped in above the cup): a woven basket of
# stones on the rear cross beam's left (+X) end, beside the windlass's spokes. Load lifts the next stone out of it and
# swings it into the cup; the stone grows to full size inside the basket's closed body (under the heap's top), so it
# never appears in view. Its geometry rides the Frame bone (no new bone).
BASKET = Vector((0.83, 1.85, 0.775))  # its base centre, on the cross beam (y 1.75..1.95, top z 0.78; its floor 5 mm
                                      # down in the beam, not coplanar); the spokes end at x 0.575, its belly at 0.615
BASKET_SEGS = 12
BASKET_IN = 0.19                      # the lip's inner radius (12-gon: 0.1835 to a face); the stone's is 0.173
BASKET_PROF = [(0.0, 0.0), (0.19, 0.0), (0.215, 0.22), (0.21, 0.44), (BASKET_IN, 0.45), (BASKET_IN, 0.41),
               (0.11, 0.435), (0.0, 0.45)]   # (r, z over BASKET): bottom, belly, rim, the lip's inside down to the heap
BASKET_HEAP = ((0.095, math.radians(20.0), 0.095, 151), (0.095, math.radians(140.0), 0.088, 152),
               (0.095, math.radians(260.0), 0.1, 153))   # stones on the heap: (from the axis, angle, radius, seed)
STONE_HIDDEN = BASKET + Vector((0.0, 0.0, 0.19))   # the loaded stone's centre inside the basket (its top 0.05 under
                                                   # the heap, its bottom 0.017 over the floor)
STONE_LIFT_Z = 1.52                   # how high it is lifted straight up before it swings over (its bottom then clears
                                      # the heap's stones, top ~1.28, and the spokes, top 1.27)


def arm_dir():
    return (ARM_END - PIVOT).normalized()


def arm_normal():
    """perpendicular to the arm on the cup's side (up in the bind pose)"""
    u = arm_dir()
    return Vector((0.0, -u.z, u.y))


def arm_len():
    return (ARM_END - PIVOT).length


# ================================================================= stage 1: the parts (inside medievalDiorama.blend)
def _tagging_kit(g, name):
    """a VKIKit whose vki_orc_part calls tag the vertices made since the last call (an int layer made before any
    geometry, so no BMVert reference is ever invalidated by it)"""
    k = g["VKIKit"](name)
    lay = k.bm.verts.layers.int.new("vku_part")
    k.part_names = []

    def tag(part):
        if part not in k.part_names:
            k.part_names.append(part)
        i = k.part_names.index(part) + 1
        for v in k.bm.verts:
            if v[lay] == 0:
                v[lay] = i
    k.part_tag = tag
    return k


def _mesh_hash(me):
    import hashlib
    h = hashlib.sha1()
    co = [0.0] * (len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    h.update(str([round(c, 6) for c in co]).encode())
    idx = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", idx)
    h.update(str(idx).encode())
    if me.uv_layers:
        uv = [0.0] * (len(me.loops) * 2)
        me.uv_layers[0].data.foreach_get("uv", uv)
        h.update(str([round(c, 5) for c in uv]).encode())
    return h.hexdigest()[:16]


def static_hash(g, burnt=False):
    """the static piece built the kit's way (vki_build_tmp: plain VKIKit) -> mesh hash (stage-1 check that the part
    markers changed nothing)"""
    coll = bpy.data.collections.get("VKU_Tmp") or bpy.data.collections.new("VKU_Tmp")
    fn = g["vki_orc_catapult_burnt" if burnt else "vki_orc_catapult"]
    o = g["vki_build_tmp"]("SM_VKI_Prop_Siege_Catapult" + ("_Burnt" if burnt else ""), fn, {"grime": "prop" if not burnt else "none"},
                          coll, "__vki_vku_hash")
    h = _mesh_hash(o.data)
    me = o.data
    bpy.data.objects.remove(o)
    bpy.data.meshes.remove(me)
    return h


def _compact_materials(me):
    """keep only the used material slots (as vkx_export does), in slot order"""
    idx = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", idx)
    used = sorted(set(idx))
    mats = [me.materials[i] for i in used]
    remap = {s: i for i, s in enumerate(used)}
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", [remap[i] for i in idx])
    return [m.name for m in mats]


def _split_arm(bm, lay, names):
    """cut the arm part across at ARM_CUT: the far side becomes part 'armtip', both cut faces closed (the cut lies
    inside the arm until Destroyed snaps it)"""
    arm_i = names.index("arm") + 1
    if "armtip" not in names:
        names.append("armtip")
    tip_i = names.index("armtip") + 1
    u = arm_dir()
    P = PIVOT + u * (arm_len() * ARM_CUT)
    faces = [f for f in bm.faces if all(v[lay] == arm_i for v in f.verts)]
    geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=P, plane_no=u, dist=1e-6)
    cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    for v in [v for v in res["geom_cut"] if isinstance(v, bmesh.types.BMVert)]:
        v[lay] = arm_i
    bmesh.ops.split_edges(bm, edges=cut_edges)
    # every arm vertex beyond the plane goes to the tip (the cut's own vertices by the faces they belong to)
    for f in bm.faces:
        if not all(v[lay] in (arm_i, tip_i) for v in f.verts):
            continue
        c = sum((v.co for v in f.verts), Vector()) / len(f.verts)
        if (c - P).dot(u) > 0:
            for v in f.verts:
                v[lay] = tip_i
    on_plane = [e for e in bm.edges if e.is_boundary and all(abs((v.co - P).dot(u)) < 1e-4 for v in e.verts)
                and all(v[lay] in (arm_i, tip_i) for v in e.verts)]
    new = bmesh.ops.holes_fill(bm, edges=on_plane, sides=0)["faces"]
    return new, P, u


def _basket(g, k):
    """the stone basket (BASKET): a woven body (the kit's burlap) closed on top by its heap (stone) -- one closed solid,
    so the loaded stone can wait inside it unseen -- and three stones on the heap. The lathe and its colours come
    before the icospheres (creating one invalidates BMVert references held from before it)."""
    stone_mi = g["VKI_STONE_BLOCK_IN"]
    vs, fs = g["vki_home_lathe"](k, BASKET_PROF, c=tuple(BASKET), segs=BASKET_SEGS, mi=g["BURLAP"], smooth=True)

    def rad(v):
        return math.hypot(v.co.x - BASKET.x, v.co.y - BASKET.y)
    heap = [f for f in fs if any(rad(v) < 0.15 for v in f.verts) and all(v.co.z > BASKET.z + 0.3 for v in f.verts)]
    for f in heap:
        f.material_index = stone_mi
    k.project(heap, stone_mi)
    k.set_dark(vs, 0.12)
    k.set_dark([v for v in vs if v.co.z > BASKET.z + 0.43 and rad(v) > 0.185], 0.3)   # the rim, a darker band
    k.set_dark(list({v for f in heap for v in f.verts}), 0.5)                            # the heap: stones in shadow
    for rr, a, r, seed in BASKET_HEAP:
        c = BASKET + Vector((math.cos(a) * rr, math.sin(a) * rr, 0.437 + 0.4 * r))
        st = g["_ico"](k, tuple(c), r, stone_mi, sub=1, jit=0.008, seed=seed)
        k.project(g["vki_faces_of"](st), stone_mi)
        k.set_dark(st, 0.32)


def build_parts(g):
    """the fresh onager with its parts tagged -> (mesh object, part names, material names), in scene UNIT"""
    k = _tagging_kit(g, "SM_VKI_Prop_Siege_Catapult")
    g["vki_orc_catapult"](k)
    # the unit's rope, hanging loose from the drum's axis (ROPE_DANGLE; the Rope bone turns and stretches it)
    g["def_rope"](k, tuple(DRUM), tuple(DRUM + ROPE_REST * ROPE_DANGLE[1]), r=0.022, n=1)
    k.part_tag("rope")
    _basket(g, k)
    k.part_tag("basket")
    for f in k.bm.faces:                                     # as vki_build_tmp: faces left without UVs
        if all(l[k.uv].uv.length == 0 for l in f.loops):
            k.project([f], f.material_index)
    names = list(k.part_names)
    sc = g["vki_scene"](UNIT)
    coll = bpy.data.collections.get(UNIT) or bpy.data.collections.new(UNIT)
    if coll.name not in sc.collection.children:
        sc.collection.children.link(coll)
    for n in (MESH, "__vki_vku_unit"):
        o = bpy.data.objects.get(n)
        if o is not None:
            me = o.data
            bpy.data.objects.remove(o)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)
    o = k.finish("__vki_vku_unit", coll, grime="prop")
    for key in list(o.keys()):
        del o[key]
    o.name = MESH
    o.data.name = MESH
    me = o.data
    # split, drop, weight
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.verts.layers.int.get("vku_part")
    drop = {names.index(p) + 1 for p in PARTS_DROPPED if p in names}
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v[lay] in drop], context="VERTS")
    caps, P, u = _split_arm(bm, lay, names)
    uvl = bm.loops.layers.uv.active
    col = bm.loops.layers.color.get("Col") or bm.loops.layers.float_color.get("Col")
    for f in caps:                                           # the snapped ends: end grain, a little darker
        f.material_index = next(lf.material_index for e in f.edges for lf in e.link_faces if lf is not f)
        ax = Vector((1.0, 0.0, 0.0)); ay = u.cross(ax)
        for l in f.loops:
            l[uvl].uv = (l.vert.co.dot(ax) * 2.0, l.vert.co.dot(ay) * 2.0)
            if col is not None:
                l[col] = (0.62, 0.58, 0.52, 1.0)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    dl = bm.verts.layers.deform.verify()
    bones = list(dict.fromkeys(PART_BONE.values()))
    for v in bm.verts:
        v[dl].clear()
        v[dl][bones.index(PART_BONE[names[v[lay] - 1]])] = 1.0
    tri_count = {}
    for f in bm.faces:
        p = names[f.verts[0][lay] - 1]
        tri_count[p] = tri_count.get(p, 0) + 1
    # vertex-group names live on the mesh (Blender 4): clearing them after to_mesh would drop the weights
    o.vertex_groups.clear()
    for b in bones:
        o.vertex_groups.new(name=b)
    bm.to_mesh(me)
    bm.free()
    mats = _compact_materials(me)
    if "vku_part" in me.attributes:
        me.attributes.remove(me.attributes["vku_part"])
    o["vku_tris_by_part"] = json.dumps(tri_count)
    return o, names, mats


def build_stone(unit):
    """the projectile: the cup's stone (its vertices, UVs and colours) moved to the origin, a mesh of its own"""
    me = unit.data
    gi = unit.vertex_groups["Stone"].index
    keep = {v.index for v in me.vertices if any(g.group == gi for g in v.groups)}
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context="VERTS")
    dl = bm.verts.layers.deform.active
    if dl is not None:
        bm.verts.layers.deform.remove(dl)
    for v in bm.verts:
        v.co -= STONE_C
    sme = bpy.data.meshes.get(STONE)
    if sme is None:
        sme = bpy.data.meshes.new(STONE)
    sme.materials.clear()                  # slots first: clearing them later would reset every face's index to 0
    for m in me.materials:
        sme.materials.append(m)
    bm.to_mesh(sme)
    bm.free()
    _compact_materials(sme)
    so = bpy.data.objects.get(STONE) or bpy.data.objects.new(STONE, sme)
    so.data = sme
    so.vertex_groups.clear()
    return so


def _flat_mat(name, rgb, checker=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.95
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    if checker is None:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    else:
        tc = nt.nodes.new("ShaderNodeTexChecker")
        tcoord = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tcoord.outputs["Object"], tc.inputs["Vector"])
        tc.inputs["Scale"].default_value = checker             # squares of 1/scale... object coords: 1 m / scale
        tc.inputs["Color1"].default_value = (*rgb, 1.0)
        tc.inputs["Color2"].default_value = (rgb[0] * 0.72, rgb[1] * 0.72, rgb[2] * 0.72, 1.0)
        nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def build_ground(sc):
    o = bpy.data.objects.get(GROUND)
    if o is None:
        me = bpy.data.meshes.new(GROUND)
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30.0)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(GROUND, me)
        sc.collection.objects.link(o)
    o.data.materials.clear()
    o.data.materials.append(_flat_mat("M_VKU_Ground", (0.30, 0.31, 0.20)))
    o.data.materials.append(_flat_mat("M_VKU_GroundChecker", (0.36, 0.37, 0.25), checker=2.0))   # 0.5 m squares
    return o


def build_unit_blend(g, path=BLEND):
    """stage 1: parts + stone + ground in scene UNIT, written alone to `path` (the kit's .blend is not saved)"""
    unit, names, mats = build_parts(g)
    stone = build_stone(unit)
    sc = bpy.data.scenes[UNIT]
    coll = bpy.data.collections[UNIT]
    if stone.name not in coll.objects:
        coll.objects.link(stone)
    stone.location = (3.2, 0.0, 0.16)
    build_ground(sc)
    sc.render.fps = FPS
    for m in ("M_VKI_WoodDark",):                            # the charred look (Destroyed's alternative material)
        if m in bpy.data.materials:
            bpy.data.materials[m].use_fake_user = True
    extra = {bpy.data.materials[m] for m in ("M_VKI_WoodDark",) if m in bpy.data.materials}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.data.libraries.write(path, {sc} | extra, fake_user=True, compress=True)
    me = unit.data
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    return {"parts": names, "materials": mats, "tris": tris, "verts": len(me.vertices),
            "tris_by_part": json.loads(unit["vku_tris_by_part"]),
            "stone_tris": sum(len(p.vertices) - 2 for p in stone.data.polygons), "blend": path,
            "groups": [vg.name for vg in unit.vertex_groups]}


# ================================================================= stage 2: rig (inside blender/vku_siege_catapult.blend)
UP_FWD = Matrix(((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0))).transposed()   # bone X; Y up; Z the front (-Y)
NO_DEFORM = ("Root", "Motion", "Socket_Projectile")
STONE_HIDE = 0.001                    # the Stone bone's scale while the cup is empty (0 would make singular matrices)
X = Vector((1.0, 0.0, 0.0))
Z = Vector((0.0, 0.0, 1.0))


def _bframe(ydir, zhint):
    """a bone frame (columns X, Y, Z): Y along ydir, Z toward zhint"""
    y = Vector(ydir).normalized()
    z = Vector(zhint)
    z = (z - y * z.dot(y)).normalized()
    return Matrix((y.cross(z), y, z)).transposed()


def bone_table():
    """name -> (head, frame, length, parent), parents first. Root and Motion: identity in Unity (up, +Z the front);
    the socket's Z (Unity forward) points out of the cup, its Y along the arm."""
    u, n, L = arm_dir(), arm_normal(), arm_len()
    T = {"Root": (Vector(), UP_FWD, 0.6, None), "Motion": (Vector(), UP_FWD, 0.45, None),
         "Frame": (Vector((0.0, 0.0, 0.5)), UP_FWD, 0.5, "Root")}
    for w, c in WHEELS.items():
        T["Wheel_" + w] = (c.copy(), _bframe(X, Z), 0.3, "Frame")
    T["Arm"] = (PIVOT.copy(), _bframe(u, n), L * ARM_CUT, "Frame")
    T["Arm_Tip"] = (PIVOT + u * (L * ARM_CUT), _bframe(u, n), L * (1.0 - ARM_CUT), "Arm")
    T["Socket_Projectile"] = (STONE_C.copy(), _bframe(u, n), 0.3, "Arm_Tip")
    T["Stone"] = (STONE_C.copy(), _bframe(n, u), 0.2, "Arm_Tip")
    T["Windlass"] = (DRUM.copy(), _bframe(X, Z), 0.5, "Frame")
    T["Rope"] = (DRUM.copy(), _bframe(ROPE_REST, X), ROPE_DANGLE[1], "Frame")
    return T


def build_rig():
    """the armature (rest = the static piece's pose: arm drawn back), the mesh bound with its rigid groups"""
    coll = bpy.data.collections[UNIT]
    old = bpy.data.objects.get(RIG)
    if old is not None:
        bpy.data.objects.remove(old)
    ad = bpy.data.armatures.get(RIG)
    if ad is not None:
        bpy.data.armatures.remove(ad)
    ad = bpy.data.armatures.new(RIG)
    ad.display_type = "STICK"
    rig = bpy.data.objects.new(RIG, ad)
    coll.objects.link(rig)
    rig.show_in_front = True
    vl = bpy.context.view_layer
    vl.update()
    for o in vl.objects:
        o.select_set(False)
    vl.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = ad.edit_bones
    T = bone_table()
    for n, (h, fr, L, par) in T.items():
        b = eb.new(n)
        b.head = h
        b.tail = h + fr.col[1] * L
        b.align_roll(fr.col[2])
        b.use_deform = n not in NO_DEFORM
        if par:
            b.parent = eb[par]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    me_o = bpy.data.objects[MESH]
    for m in [m for m in me_o.modifiers if m.type == "ARMATURE"]:
        me_o.modifiers.remove(m)
    me_o.parent = rig
    me_o.matrix_parent_inverse = Matrix.Identity(4)
    me_o.matrix_world = Matrix.Identity(4)
    mod = me_o.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    groups = {vg.name for vg in me_o.vertex_groups}
    bones = {b.name for b in ad.bones if b.use_deform}
    unweighted = sum(1 for v in me_o.data.vertices if not v.groups)
    return {"bones": [b.name for b in ad.bones], "groups_without_bone": sorted(groups - bones),
            "unweighted": unweighted, "over1": sum(1 for v in me_o.data.vertices if len(v.groups) > 1)}


# ================================================================= geometry the clips are fitted to
def rx(a, p):
    """rotation by a about the line through p parallel to X"""
    p = Vector(p)
    return Matrix.Translation(p) @ Matrix.Rotation(a, 4, "X") @ Matrix.Translation(-p)


def raxis(a, p, d):
    p = Vector(p)
    return Matrix.Translation(p) @ Matrix.Rotation(a, 4, Vector(d).normalized()) @ Matrix.Translation(-p)


def _parts():
    """bind-pose vertices, each vertex's bone, triangles by bone"""
    o = bpy.data.objects[MESH]
    me = o.data
    names = [vg.name for vg in o.vertex_groups]
    vb = [names[max(v.groups, key=lambda g: g.weight).group] for v in me.vertices]
    co = [v.co.copy() for v in me.vertices]
    tris = {}
    for p in me.polygons:
        tris.setdefault(vb[p.vertices[0]], []).append(tuple(p.vertices))
    return co, vb, tris


def _bvh(co, tris, M=None):
    if M is not None:
        co = [M @ c for c in co]
    return BVHTree.FromPolygons(co, tris, epsilon=0.0)


def _hits(a, b):
    return len(a.overlap(b)) > 0


def _min_z(co, idx, M):
    return min((M @ co[i]).z for i in idx)


WHIP = 6                     # Throw: frames from the trigger to the slam
T_TRIGGER = 4                # Throw: the frame the arm lets go
STUMP = math.radians(26.0)   # Destroyed: where the snapped arm's stump comes to rest (from the drawn-back bind pose)
FULCRUM = Vector((0.0, -0.25, 1.91))   # the pad's top edge: the arm's tip tips over it when the arm snaps
TIP_TURN = math.radians(84.0)          # Destroyed: how far the tip turns over the pad before it lies on the ground
TIP_ROLL = math.radians(70.0)          # ... rolled about its own length so the cup lies on its side
TIP_AT = (0.18, -2.32)                 # ... its middle's x, and the y its back end lies short of (clear of the beams)
WHEEL_SLIDE = 0.27                     # Destroyed: the front-left wheel slides off its axle, then falls outward
_AN = {}


def analyse():
    """fit the clips to the geometry: where the arm meets the stop's pad (stop), where it lies on the windlass drum
    (loaded), the rope's hook on the arm, Throw's release frame, Destroyed's tilt and resting places"""
    if _AN:
        return _AN
    co, vb, tris = _parts()
    arm_tris = tris["Arm"] + tris["Arm_Tip"]

    def near_pivot(i):                                                # the skein: the arm turns inside it
        c = co[i]
        return abs(c.x) < 0.7 and math.hypot(c.y - PIVOT.y, c.z - PIVOT.z) < 0.26
    frame_tris = [t for t in tris["Frame"] if not any(near_pivot(i) for i in t)]
    obst = _bvh(co, frame_tris + tris["Windlass"])

    def arm_hits(d):
        return _hits(_bvh(co, arm_tris, rx(d, PIVOT)), obst)

    def bisect(lo, hi, hit_at_hi, n=40):
        for _ in range(n):
            mid = (lo + hi) / 2
            if arm_hits(mid) == hit_at_hi:
                hi = mid
            else:
                lo = mid
        return lo, hi
    hit0 = arm_hits(0.0)
    assert not arm_hits(math.radians(60)) and arm_hits(math.radians(100))     # (past ~115 deg it is through the pad)
    d_free = bisect(0.0, math.radians(35), False)[1] if hit0 else 0.0     # first angle clear of the drum
    d_stop = bisect(math.radians(60), math.radians(100), True)[0]          # last angle clear of the pad
    loaded = d_free + math.radians(0.25)
    stop = d_stop - math.radians(0.15)
    sweep = [round(math.degrees(d), 1) for d in [loaded + (stop - loaded) * i / 60 for i in range(61)] if arm_hits(d)]
    # the hook: on the arm's underside, over the drum when loaded (bind coordinates)
    u, n = arm_dir(), arm_normal()
    Dl = rx(-loaded, PIVOT) @ DRUM
    s_h = (Dl - PIVOT).dot(u)
    hook = PIVOT + u * s_h - n * ARM_HALF
    # Throw: the arm whips from loaded to the stop in WHIP frames (constant angular acceleration); the stone leaves the
    # cup on the frame whose launch elevation (90 deg - the arm's elevation) is nearest 45 deg
    phi0 = math.atan2(u.z, u.y)
    a0 = loaded + math.radians(0.3)
    elev = {f: 90.0 - math.degrees(phi0 + a0 + (stop - a0) * (f / WHIP) ** 2) for f in range(1, WHIP)}
    rel = min(elev, key=lambda f: abs(elev[f] - 45.0))
    # Destroyed: the front-left wheel gone, the frame tips about the line through the front-right and back-left
    # wheels' contacts until its front-left corner is down; the other wheels' dip is taken up by a lift
    p1 = Vector((WHEELS["FR"].x, WHEELS["FR"].y, 0.0))
    p2 = Vector((WHEELS["BL"].x, WHEELS["BL"].y, 0.0))
    axis = (p2 - p1).normalized()
    fidx = [i for i, b in enumerate(vb) if b in ("Frame", "Windlass")]
    widx = [i for i, b in enumerate(vb) if b in ("Wheel_FR", "Wheel_BL", "Wheel_BR")]
    lo, hi = 0.0, math.radians(25)
    for _ in range(40):
        mid = (lo + hi) / 2
        if _min_z(co, fidx, raxis(mid, p1, axis)) > 0.012:
            lo = mid
        else:
            hi = mid
    tilt = lo
    lift = max(0.0, -_min_z(co, widx, raxis(tilt, p1, axis)))
    _AN.update(stop=stop, loaded=loaded, hook=hook, release=T_TRIGGER + rel, release_elev=elev[rel],
               arm_elev0=math.degrees(phi0), tilt=tilt, tilt_p=p1, tilt_axis=axis, tilt_lift=lift, sweep_hits=sweep,
               drum_hit_at_bind=hit0, co=co, tris_tip=tris["Arm_Tip"],
               tris_fixed=frame_tris + tris["Windlass"] + tris["Wheel_FR"] + tris["Wheel_BL"] + tris["Wheel_BR"])
    _AN.update(_destroyed_rest(co, vb))
    return _AN


def _destroyed_rest(co, vb):
    """the final transforms (armature space, applied to the bind pose) of the snapped tip and of the fallen wheel"""
    out = {}
    tip = [i for i, b in enumerate(vb) if b == "Arm_Tip"]
    R = rx(TIP_TURN, FULCRUM) @ rx(_AN["stop"], PIVOT)              # turned over the pad from the stop
    pts = [R @ co[i] for i in tip]
    mid = sum(pts, Vector()) / len(pts)
    along = (R.to_3x3() @ arm_dir()).normalized()
    R = raxis(TIP_ROLL, mid, along) @ R                               # rolled about its own length
    pts = [R @ co[i] for i in tip]
    mid = sum(pts, Vector()) / len(pts)
    shift = Vector((TIP_AT[0] - mid.x, TIP_AT[1] - max(p.y for p in pts), 0.002 - min(p.z for p in pts)))
    out["tip_final"] = Matrix.Translation(shift) @ R
    whl = [i for i, b in enumerate(vb) if b == "Wheel_FL"]
    c = WHEELS["FL"]
    half = max(co[i].x for i in whl) - c.x                            # how far the hub boss stands out
    edge = Vector((c.x + WHEEL_SLIDE + half, 0.0, 0.0))
    W = raxis(math.pi / 2, edge, Vector((0.0, 1.0, 0.0))) @ Matrix.Translation((WHEEL_SLIDE, 0.0, 0.0))
    out["wheel_lift"] = 0.002 - min((W @ co[i]).z for i in whl)
    out["wheel_edge"] = edge
    out["pts"] = {"Arm_Tip": [co[i] for i in tip], "Wheel_FL": [co[i] for i in whl]}
    out["tip_c"] = sum((co[i] for i in tip), Vector()) / len(tip)
    return out


# ================================================================= poses
def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def hump(f, f0, n):
    """0 -> 1 -> 0 (half a sine) over frames f0 .. f0 + n"""
    return math.sin(math.pi * (f - f0) / n) if f0 <= f <= f0 + n else 0.0


class Pose:
    """one frame: Motion's travel, the frame's move (armature space), wheel turns, the arm's turn from the bind pose,
    the rope (('free', angle, length) | ('hook',) | ('end', point in frame space)), the windlass (None: wound by the
    rope's length), the stone (scale, world offset); free (armature-space) moves for parts that broke off"""

    def __init__(s, an):
        s.motion = 0.0
        s.frame = Matrix.Identity(4)
        s.wheel = {w: 0.0 for w in WHEELS}
        s.wheel_free = {}
        s.arm = an["stop"]
        s.tip_free = None
        s.windlass = None
        s.rope = ("free", ROPE_DANGLE[0], ROPE_DANGLE[1])
        s.stone = (STONE_HIDE, Vector())
        s.stone_at = None          # (scale, centre, turn): the stone off the arm (Load: in the basket, on its way)


def rope_state(p, an):
    """(angle, length) of the rope in the frame's YZ plane, from the drum's axis"""
    if p.rope[0] == "free":
        return p.rope[1], p.rope[2]
    E = (rx(p.arm, PIVOT) @ an["hook"]) if p.rope[0] == "hook" else Vector(p.rope[1])
    d = E - DRUM
    return math.atan2(d.z, d.y), d.length


def windlass_angle(L):
    """the drum turns with the rope: paid out (longer) turns it forward (+X), wound in turns it back"""
    return (L - ROPE_DANGLE[1]) / DRUM_R


def matrices(p, an, rest):
    """armature-space pose matrix of every bone"""
    F = p.frame
    M = {"Root": rest["Root"].copy(), "Motion": Matrix.Translation((0.0, -p.motion, 0.0)) @ rest["Motion"],
         "Frame": F @ rest["Frame"]}
    for w, c in WHEELS.items():
        D = p.wheel_free.get(w)
        M["Wheel_" + w] = (D if D is not None else F @ rx(p.wheel[w], c)) @ rest["Wheel_" + w]
    Darm = F @ rx(p.arm, PIVOT)
    M["Arm"] = Darm @ rest["Arm"]
    Dtip = p.tip_free if p.tip_free is not None else Darm
    M["Arm_Tip"] = Dtip @ rest["Arm_Tip"]
    M["Socket_Projectile"] = Dtip @ rest["Socket_Projectile"]
    if p.stone_at is not None:                     # the stone's centre at c, turned q from its bind pose
        s, c, q = p.stone_at
        M["Stone"] = Matrix.Translation(c) @ q.to_matrix().to_4x4() @ Matrix.Translation(-STONE_C) @ rest["Stone"] \
            @ Matrix.Diagonal((s, s, s, 1.0))
    else:
        s, off = p.stone
        M["Stone"] = Matrix.Translation(off) @ Dtip @ rest["Stone"] @ Matrix.Diagonal((s, s, s, 1.0))
    a, L = rope_state(p, an)
    M["Rope"] = F @ rx(a - ROPE_DANGLE[0], DRUM) @ rest["Rope"] @ Matrix.Diagonal((1.0, L / ROPE_DANGLE[1], 1.0, 1.0))
    psi = p.windlass if p.windlass is not None else windlass_angle(L)
    M["Windlass"] = F @ rx(psi, DRUM) @ rest["Windlass"]
    return M


def set_pose(rig, M, frame=None):
    """armature-space matrices -> matrix_basis (parents' poses known), keyed when frame is given"""
    for pb in rig.pose.bones:
        b = pb.bone
        if b.parent is None:
            B = b.matrix_local.inverted() @ M[b.name]
        else:
            local = b.parent.matrix_local.inverted() @ b.matrix_local
            B = local.inverted() @ M[b.parent.name].inverted() @ M[b.name]
        loc, q, sc = B.decompose()
        if pb.rotation_quaternion.dot(q) < 0.0:
            q.negate()
        pb.location = loc
        pb.rotation_quaternion = q
        pb.scale = sc
        if frame is not None:
            pb.keyframe_insert("location", frame=frame, group=b.name)
            pb.keyframe_insert("rotation_quaternion", frame=frame, group=b.name)
            pb.keyframe_insert("scale", frame=frame, group=b.name)


def _bez(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * (2 * t * (1 - t)) + p2 * t * t


def _dangle_end():
    a, L = ROPE_DANGLE
    return DRUM + Vector((0.0, math.cos(a), math.sin(a))) * L


# ================================================================= clips (30 fps; loops end on their first pose)
def clip_idle(an, f, N):
    """still, the arm against the stop, the loose rope swaying a little; a slight creak of the arm"""
    p = Pose(an)
    w = 2 * math.pi * f / N
    p.arm = an["stop"] - math.radians(0.4) * (0.5 - 0.5 * math.cos(w))
    p.rope = ("free", ROPE_DANGLE[0] + math.radians(4.0) * math.sin(w), ROPE_DANGLE[1])
    return p


def clip_idle_loaded(an, f, N):
    """drawn back and loaded: the arm strains a hair against the rope, the windlass held"""
    p = Pose(an)
    p.arm = an["loaded"] + math.radians(0.15) * (0.5 - 0.5 * math.cos(2 * math.pi * f / N))
    p.rope = ("hook",)
    p.windlass = windlass_angle(rope_state(Pose_loaded(an), an)[1])
    p.stone = (1.0, Vector())
    return p


def Pose_loaded(an):
    p = Pose(an)
    p.arm = an["loaded"]
    p.rope = ("hook",)
    return p


MOVE_FRAMES = 64                                         # one full turn of the wheels
MOVE_SPEED = 2 * math.pi * WHEEL_R / (MOVE_FRAMES / FPS)    # m/s: the wheels roll without sliding


def clip_move(an, f, N):
    """rolling forward at a cart's pace: Motion travels MOVE_SPEED, the wheels turn one full turn a loop (v = w r);
    the arm rattles against the stop, the loose rope swings"""
    p = Pose(an)
    p.motion = MOVE_SPEED * f / FPS
    for w in WHEELS:
        p.wheel[w] = 2 * math.pi * f / N
    p.arm = an["stop"] - math.radians(0.6) * (0.5 - 0.5 * math.cos(4 * math.pi * f / N))
    p.rope = ("free", ROPE_DANGLE[0] + math.radians(7.0) * math.sin(4 * math.pi * f / N), ROPE_DANGLE[1])
    return p


# Load (frames). 2026-10-23, Daniel: "Do the number 4" -- the windlass had spun ~3.5 turns a second (7 at its peak,
# from a standing start) for 0.9 s while the rope ran out, and the stone popped in over the cup. Now the rope is run
# out over 56 frames, the windlass easing up to ~2.5 turns a second and back down (below the heaves' peaks), so the
# eight heaves start later and pause less (Hooked 1.2 -> 1.9 s; the heaves' own speed is within 5 % of before); the
# stone grows inside the basket, is lifted straight out of it and swung over into the cup (Loaded stays 4.633 s).
LOAD = dict(carry=(1, 57), swing=12, ramp=16, wind=(59, 128), heaves=8, heave_move=0.92, settle=(128, 137),
            basket=98, grow=(100, 104), lift=(106, 139))   # basket: the hidden (0.001) stone moves from the cup into
                                                           # the basket, held 2 frames (curve tangents settle) ere it grows
STONE_TURN = Quaternion(Vector((0.45, -0.7, 0.55)).normalized(), math.radians(75.0))   # how it lies in the basket


def ease_run(t, D, R):
    """the distance fraction (0..1) at frame t of a run over D frames whose speed eases up over the first R frames (half
    a cosine), holds, and eases down over the last R: the windlass paying out"""
    t = max(0.0, min(float(D), t))
    R = min(R, D / 2.0)

    def part(x):
        if x <= R:
            return x / 2.0 - R / (2.0 * math.pi) * math.sin(math.pi * x / R)
        return R / 2.0 + (x - R)
    total = D - R
    return part(t) / total if t <= D / 2.0 else 1.0 - part(D - t) / total


def _cup(p):
    """the cup's stone centre and the cup's turn (armature space) in pose p"""
    D = p.frame @ rx(p.arm, PIVOT)
    return D @ STONE_C, D.to_quaternion()


def _bez3(p0, p1, p2, p3, t):
    u = 1.0 - t
    return p0 * (u * u * u) + p1 * (3 * u * u * t) + p2 * (3 * u * t * t) + p3 * (t * t * t)


def stone_path(s, C, q_cup):
    """the loaded stone's centre and turn at fraction s (by length) of its way: straight up out of the basket until it
    clears the heap's stones and the windlass's spokes, then an arc over and down into the cup (C, q_cup: the cup now)"""
    A = STONE_HIDDEN
    B = Vector((A.x, A.y, STONE_LIFT_Z))
    n = q_cup @ Vector((0.0, 0.0, 1.0))                     # the cup's opening (+Z when the arm is drawn back)
    P1, P2 = B + Vector((0.0, 0.0, 0.25)), C + n * 0.42
    pts = [_bez3(B, P1, P2, C, i / 48.0) for i in range(49)]
    cum = [0.0]
    for i in range(48):
        cum.append(cum[-1] + (pts[i + 1] - pts[i]).length)
    up = (B - A).length
    d = max(0.0, min(1.0, s)) * (up + cum[-1])
    if d <= up:
        c = A.lerp(B, d / up)
    else:
        d -= up
        i = max(0, min(47, next((j for j in range(48) if cum[j + 1] >= d), 47)))
        seg = cum[i + 1] - cum[i]
        c = pts[i].lerp(pts[i + 1], (d - cum[i]) / seg if seg > 1e-9 else 0.0)
    q = STONE_TURN.copy()
    if q.dot(q_cup) < 0.0:
        q.negate()
    return c, q.slerp(q_cup, max(0.0, min(1.0, s)))


def load_rope(an, f):
    """Load's rope: (angle, length) while it is run out (the loose end swung up over the drum toward the arm while the
    windlass pays out, eased), None once it is on the hook"""
    c0, c1 = LOAD["carry"]
    if f >= c1:
        return None
    d = rx(an["stop"], PIVOT) @ an["hook"] - DRUM
    a0, L0 = ROPE_DANGLE
    a1, L1 = math.atan2(d.z, d.y), d.length
    while a1 < a0:
        a1 += 2 * math.pi
    a = a0 + (a1 - a0) * smooth((f - c0) / LOAD["swing"])
    return a, L0 + (L1 - L0) * ease_run(f - c0, c1 - c0, LOAD["ramp"])


def clip_load(an, f, N):
    """the rope swung up over the drum and run out to the arm, the windlass easing up and down as it pays out; eight
    heaves on the windlass wind the arm down onto the drum (the windlass turns with the rope's length); a stone is
    lifted out of the basket on the rear beam and swung over into the cup (it grows to size hidden inside the basket)"""
    p = Pose(an)
    w0, w1 = LOAD["wind"]
    r = load_rope(an, f)
    p.rope = ("free", r[0], r[1]) if r is not None else ("hook",)
    if f >= w0:
        n = LOAD["heaves"]
        per = (w1 - w0) / n
        k = min(n - 1, int((f - w0) // per))
        ph = smooth(((f - w0) - k * per) / (per * LOAD["heave_move"]))
        prog = min(1.0, (k + ph) / n)
        p.arm = an["stop"] + (an["loaded"] - an["stop"]) * prog
    s0, s1 = LOAD["settle"]
    if s0 <= f <= s1:
        p.arm = an["loaded"] + math.radians(0.8) * hump(f, s0, 4) + math.radians(0.25) * hump(f, s0 + 4, 4)
    g0, g1 = LOAD["grow"]
    t0, t1 = LOAD["lift"]
    if LOAD["basket"] <= f < t0:                            # inside the basket: grows to full size, unseen
        p.stone_at = (max(STONE_HIDE, smooth((f - g0) / (g1 - g0))), STONE_HIDDEN.copy(), STONE_TURN.copy())
    elif t0 <= f <= t1:                                     # lifted out, swung over, set down in the cup
        C, q = _cup(p)
        c, qs = stone_path(smooth((f - t0) / (t1 - t0)), C, q)
        p.stone_at = (1.0, c, qs)
    elif f > t1:                                            # in the cup: a little settle
        p.stone = (1.0, Vector((0.0, 0.0, 0.03 * hump(f, t1, 4))))
    return p


def clip_throw(an, f, N):
    """the trigger: the hook lets go, the arm whips up (the stone leaves the cup at the Release event), slams into the
    padded stop and bounces, the back of the frame kicks up; ends on Idle's pose"""
    p = Pose(an)
    a0 = an["loaded"] + math.radians(0.3)
    hold = windlass_angle(rope_state(Pose_loaded(an), an)[1])
    if f <= T_TRIGGER:
        p.arm = an["loaded"] + math.radians(0.3) * smooth(f / T_TRIGGER)
        p.rope = ("hook",)
        p.windlass = hold
    else:
        g = min(1.0, (f - T_TRIGGER) / WHIP)
        p.arm = a0 + (an["stop"] - a0) * g * g
        slam = T_TRIGGER + WHIP
        if f > slam:                                    # bounces off the pad: 6, 2, 0.6 degrees
            p.arm = an["stop"] - math.radians(6.0) * hump(f, slam, 6) - math.radians(2.0) * hump(f, slam + 6, 5) \
                - math.radians(0.6) * hump(f, slam + 11, 4)
        # the rope's end drops off the hook behind the drum, then swings out
        hook_l = rx(an["loaded"], PIVOT) @ an["hook"]
        t = smooth((f - T_TRIGGER) / 8.0)
        if t < 1.0:
            P1 = Vector((0.0, DRUM.y + 0.45, DRUM.z + 0.12))
            p.rope = ("end", _bez(hook_l, P1, _dangle_end(), t))
        else:
            k = f - (T_TRIGGER + 8)
            fade = 1.0 - smooth((f - 30) / 15.0)
            p.rope = ("free", ROPE_DANGLE[0] + math.radians(10.0) * math.sin(2 * math.pi * k / 16.0)
                      * math.exp(-k / 12.0) * fade, ROPE_DANGLE[1])
        # the kick: the back of the frame jumps up about the front wheels' contact and drops back, a small second hop
        slam = T_TRIGGER + WHIP
        b = 0.0
        if slam <= f <= slam + 4:
            b = math.radians(4.0) * math.sin(0.5 * math.pi * (f - slam) / 4.0)
        elif slam + 4 < f <= slam + 9:
            b = math.radians(4.0) * (1.0 - ((f - slam - 4) / 5.0) ** 2)
        elif slam + 9 < f <= slam + 13:
            b = math.radians(0.8) * hump(f, slam + 9, 4)
        p.frame = rx(b, (0.0, WHEELS["FL"].y, 0.0))
    p.stone = (1.0 if f < an["release"] else STONE_HIDE, Vector())
    return p


def clip_hit(an, f, N):
    """a jolt from the front: shoved back a few cm (the wheels turn with it), the front bucks up, the arm rattles
    against the stop, the rope swings; ends on Idle's pose"""
    p = Pose(an)
    yb = 0.07 * (smooth(f / 3.0) if f < 3 else 1.0 - smooth((f - 3) / (N - 3)))
    beta = -math.radians(2.5) * hump(f, 0, 8) - math.radians(0.7) * hump(f, 8, 5)
    p.frame = Matrix.Translation((0.0, yb, 0.0)) @ rx(beta, (0.0, WHEELS["BL"].y, 0.0))
    for w in WHEELS:
        p.wheel[w] = -yb / WHEEL_R
    p.arm = an["stop"] - math.radians(4.0) * hump(f, 0, 6) - math.radians(1.2) * hump(f, 6, 5)
    p.rope = ("free", ROPE_DANGLE[0] + math.radians(14.0) * math.sin(2 * math.pi * f / 12.0) * (1.0 - f / N),
              ROPE_DANGLE[1])
    return p


DEST = dict(brk=5, slide=(5, 9), fall=(9, 17), tilt=(6, 14), snap=12, stump=(12, 22), tip_turn=(12, 17),
            tip_fall=(17, 31))


def _lerp_m(A, B, c, t, t_pos):
    """blend two rigid moves of a piece whose (bind) centre is c: its centre travels by the per-axis fractions t_pos,
    it turns by slerp(t) about that centre"""
    ca, cb = A @ c, B @ c
    ra, rb = A.to_quaternion(), B.to_quaternion()
    if ra.dot(rb) < 0.0:
        rb.negate()
    cc = Vector((ca.x + (cb.x - ca.x) * t_pos[0], ca.y + (cb.y - ca.y) * t_pos[1], ca.z + (cb.z - ca.z) * t_pos[2]))
    return Matrix.Translation(cc) @ ra.slerp(rb, t).to_matrix().to_4x4() @ Matrix.Translation(-c)


def _above_ground(M, pts, clear=0.002):
    """lift a free piece so none of its points is under the ground"""
    z = min((M @ q).z for q in pts)
    return Matrix.Translation((0.0, 0.0, clear - z)) @ M if z < clear else M


def _dest_frame(an, f):
    """Destroyed: the frame's move at frame f -- a shudder, then it tips about the front-right / back-left contact line
    onto its front-left corner and bounces once"""
    t0, t1 = DEST["tilt"]
    roll = math.radians(1.2) * hump(f, 0, 5)
    g = an["tilt"] * min(1.0, max(0.0, (f - t0) / (t1 - t0))) ** 2
    if t1 < f <= t1 + 4:
        g = an["tilt"] - math.radians(1.2) * hump(f, t1, 4)
    lift = an["tilt_lift"] * (g / an["tilt"] if an["tilt"] > 0 else 0.0)
    F = Matrix.Translation((0.0, 0.0, lift)) @ raxis(g, an["tilt_p"], an["tilt_axis"])
    return F @ raxis(roll, (WHEELS["FR"].x, 0.0, 0.0), (0.0, -1.0, 0.0))


TIP_TOPPLE = math.radians(50.0)        # Destroyed: how far the tip topples over the pad's back edge before it flies


def _tip_path(an, f):
    """Destroyed, the tip's way before any lift: toppling over the pad's back edge, then flying to its place on the
    ground"""
    q0, q1 = DEST["tip_turn"]
    r1 = DEST["tip_fall"][1]
    if f <= q1:
        u = (f - q0) / (q1 - q0)
        return _dest_frame(an, f) @ rx(TIP_TOPPLE * u * u, FULCRUM) @ rx(an["stop"], PIVOT)
    Fq = _dest_frame(an, q1) @ rx(TIP_TOPPLE, FULCRUM) @ rx(an["stop"], PIVOT)
    v = (f - q1) / (r1 - q1)
    z0, z1 = (Fq @ an["tip_c"]).z, (an["tip_final"] @ an["tip_c"]).z
    rise = 0.05
    zf = (rise * v - (z0 - z1 + rise) * v * v) / (z1 - z0) if abs(z1 - z0) > 1e-6 else v
    return _lerp_m(Fq, an["tip_final"], an["tip_c"], v, (v, v, zf))


def _tip_lift(an):
    """Destroyed: per frame of the tip's flight, how far it must be lifted to pass over the pad, the crossbar and the
    frame (triangle overlaps), smoothed so it eases up ahead of an edge and drops off it at most 6 cm a frame"""
    if "tip_lift" in an:
        return an["tip_lift"]
    q0, r1 = DEST["tip_turn"][0], DEST["tip_fall"][1]
    need = {}
    for f in range(q0, r1 + 1):
        obst = _bvh(an["co"], an["tris_fixed"], _dest_frame(an, f))
        T = _tip_path(an, f)
        lift = 0.0
        while lift < 1.0 and _hits(_bvh(an["co"], an["tris_tip"], Matrix.Translation((0.0, 0.0, lift)) @ T), obst):
            lift += 0.01
        need[f] = lift + (0.01 if lift > 0 else 0.0)
    out, prev = {}, 0.0
    for f in range(q0, r1 + 1):
        ahead = max(need.get(f + k, 0.0) * w for k, w in ((0, 1.0), (1, 0.7), (2, 0.4)))
        prev = max(ahead, prev - 0.06)
        out[f] = prev
    an["tip_lift"] = out
    return out


def clip_destroyed(an, f, N):
    """the front-left wheel breaks off its axle and falls flat, the frame tips onto that corner, the arm snaps: its
    stump falls back in the skein, its tip turns over the pad and drops in front; holds the wreck"""
    p = Pose(an)
    d = DEST
    p.arm = an["stop"] - math.radians(3.0) * hump(f, 0, 5)           # a shudder first
    F = _dest_frame(an, f)
    p.frame = F
    # the wheel: off its axle (riding the frame), then over onto its face (on its own)
    if f >= d["brk"]:
        s0, s1 = d["slide"]
        a0, a1 = d["fall"]
        W0 = Matrix.Translation((WHEEL_SLIDE * smooth((f - s0) / (s1 - s0)), 0.0, 0.0))
        if f < a0:
            p.wheel_free["FL"] = _above_ground(F @ W0, an["pts"]["Wheel_FL"], 0.0)
        else:
            Fa = _dest_frame(an, a0)
            ga = (math.pi / 2) * min(1.0, (f - a0) / (a1 - a0)) ** 2
            W = raxis(ga, Fa @ an["wheel_edge"], Fa.to_3x3() @ Vector((0.0, 1.0, 0.0))) @ Fa @ W0
            if a1 < f <= a1 + 4:
                W = Matrix.Translation((0.0, 0.0, 0.02 * hump(f, a1, 4))) @ W
            p.wheel_free["FL"] = _above_ground(W, an["pts"]["Wheel_FL"])
    # the arm snaps: the stump falls back, the tip turns over the pad and drops in front
    if f >= d["snap"]:
        s0, s1 = d["stump"]
        k = min(1.0, (f - s0) / (s1 - s0))
        p.arm = an["stop"] + (STUMP - an["stop"]) * (1.0 - (1.0 - k) ** 2)     # whips back as it lets go
        if s1 < f <= s1 + 5:
            p.arm = STUMP + math.radians(3.0) * hump(f, s1, 5)
        q0, q1 = d["tip_turn"]
        r0, r1 = d["tip_fall"]
        if f <= r1:
            # topples over the pad's back edge, then flies off the front and drops: steady across, a parabola down,
            # lifted over whatever it would pass through
            T = Matrix.Translation((0.0, 0.0, _tip_lift(an)[f])) @ _tip_path(an, f)
        else:
            T = Matrix.Translation((0.0, 0.0, 0.025 * hump(f, r1, 4))) @ an["tip_final"]
        p.tip_free = _above_ground(T, an["pts"]["Arm_Tip"])
    k = max(0.0, f - d["brk"])
    p.rope = ("free", ROPE_DANGLE[0] + math.radians(12.0) * math.sin(2 * math.pi * k / 14.0) * math.exp(-k / 10.0)
              * (1.0 - smooth((f - 30) / max(1.0, N - 30))), ROPE_DANGLE[1])
    return p


# name: (function, frames, loop, root motion, events {name: frame})
CLIPS = {
    "Idle": (clip_idle, 90, True, False, {}),
    "IdleLoaded": (clip_idle_loaded, 60, True, False, {}),
    "Move": (clip_move, MOVE_FRAMES, True, True, {}),
    "Load": (clip_load, 150, False, False, {"Hooked": LOAD["carry"][1], "Loaded": LOAD["lift"][1]}),
    "Throw": (clip_throw, 45, False, False, {"Release": None, "Slam": T_TRIGGER + WHIP}),
    "Hit": (clip_hit, 18, False, False, {}),
    "Destroyed": (clip_destroyed, 44, False, False, {"Break": DEST["brk"], "Snap": DEST["snap"]}),
}


def action_name(clip):
    return f"{UNIT}_{clip}"


def clip_events(clip, an):
    ev = dict(CLIPS[clip][4])
    if clip == "Throw":
        ev["Release"] = an["release"]
    return ev


def rest_mats(rig):
    return {b.name: b.matrix_local.copy() for b in rig.data.bones}


def pose_at(clip, f, an=None):
    an = an or analyse()
    fn, N = CLIPS[clip][0], CLIPS[clip][1]
    return fn(an, f, N)


def build_clips(only=None):
    rig = bpy.data.objects[RIG]
    an = analyse()
    rest = rest_mats(rig)
    prefs = bpy.context.preferences.edit
    keep = prefs.keyframe_new_interpolation_type
    prefs.keyframe_new_interpolation_type = "LINEAR"
    if rig.animation_data is None:
        rig.animation_data_create()
    out = {}
    try:
        for clip, (fn, N, loop, moves, _) in CLIPS.items():
            if only and clip not in only:
                continue
            nm = action_name(clip)
            old = bpy.data.actions.get(nm)
            if old is not None:
                bpy.data.actions.remove(old)
            act = bpy.data.actions.new(nm)
            act.use_fake_user = True
            rig.animation_data.action = act
            for pb in rig.pose.bones:
                pb.matrix_basis = Matrix.Identity(4)
            for f in range(N + 1):
                set_pose(rig, matrices(fn(an, f, N), an, rest), frame=f)
            act["frames"] = N
            act["loop"] = loop
            act["root_motion"] = moves
            for k, v in clip_events(clip, an).items():
                act["event_" + k] = v / FPS
            out[clip] = {"frames": N, "seconds": round(N / FPS, 3), "loop": loop,
                         "events": {k: round(v / FPS, 3) for k, v in clip_events(clip, an).items()}}
    finally:
        prefs.keyframe_new_interpolation_type = keep
        rig.animation_data.action = None
        for pb in rig.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
    return out


def use_clip(rig, clip):
    act = bpy.data.actions[action_name(clip)]
    rig.animation_data.action = act
    if hasattr(rig.animation_data, "action_slot") and len(getattr(act, "slots", [])) > 0:
        rig.animation_data.action_slot = act.slots[0]
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, int(act["frames"])
    return act


# ================================================================= checks
def _eval_co():
    """the skinned mesh's vertices at the current frame (armature space: the mesh sits on the rig at the origin)"""
    dg = bpy.context.evaluated_depsgraph_get()
    ob = bpy.data.objects[MESH].evaluated_get(dg)
    me = ob.to_mesh()
    co = [ob.matrix_world @ v.co for v in me.vertices]
    ob.to_mesh_clear()
    return co


def check_lowest():
    """lowest vertex of every clip (the skeleton plays in place; Motion carries the travel) and which part it is"""
    rig = bpy.data.objects[RIG]
    _, vb, _ = _parts()
    sc = bpy.context.scene
    out = {}
    for clip in CLIPS:
        act = use_clip(rig, clip)
        best = (9.0, -1, "")
        for f in range(int(act["frames"]) + 1):
            sc.frame_set(f)
            co = _eval_co()
            i = min(range(len(co)), key=lambda j: co[j].z)
            if co[i].z < best[0]:
                best = (co[i].z, f, vb[i])
        out[clip] = {"min_z_mm": round(best[0] * 1000, 1), "frame": best[1], "part": best[2]}
    rig.animation_data.action = None
    return out


def _bone_m(rig, name):
    return rig.pose.bones[name].matrix.copy()


def check_move():
    """Move traced from the keys: Motion's travel per frame against the wheels' turn times their radius (sliding), the
    skeleton staying in place, the loop's seam"""
    rig = bpy.data.objects[RIG]
    sc = bpy.context.scene
    act = use_clip(rig, "Move")
    N = int(act["frames"])
    motion, turn, root = [], {w: [] for w in WHEELS}, []
    for f in range(N + 1):
        sc.frame_set(f)
        motion.append(_bone_m(rig, "Motion").translation.copy())
        root.append(_bone_m(rig, "Frame").translation.copy())
        for w in WHEELS:
            m = _bone_m(rig, "Wheel_" + w).to_3x3()
            z = m.col[2]                                    # the bone's Z turns about X with the wheel
            turn[w].append(math.atan2(z.y, z.z))            # = -(the turn about +X)
    # rolling forward (-Y) turns a wheel about +X at w = v / r: slip = |v_motion - w r|
    worst = 0.0
    for w in WHEELS:
        for f in range(N):
            dpsi = (turn[w][f + 1] - turn[w][f] + math.pi) % (2 * math.pi) - math.pi
            v = -(motion[f + 1].y - motion[f].y) * FPS
            worst = max(worst, abs(v - (-dpsi) * WHEEL_R * FPS))
    rig.animation_data.action = None
    travel = motion[-1] - motion[0]
    return {"speed_mps": round(travel.length / (N / FPS), 4), "per_loop_m": round(travel.length, 4),
            "dir_blender": [round(c, 3) for c in travel.normalized()], "wheel_turns_per_loop": 1.0,
            "max_slip_mps": round(worst, 5), "skeleton_moves_m": round(max((r - root[0]).length for r in root), 5),
            "frames": N}


def check_socket():
    """the socket at Throw's Release: where it is, which way its +Z (Unity forward) points, the stone's centre"""
    rig = bpy.data.objects[RIG]
    an = analyse()
    sc = bpy.context.scene
    use_clip(rig, "Throw")
    out = {}
    for f in (an["release"] - 1, an["release"], an["release"] + 1):
        sc.frame_set(f)
        m = _bone_m(rig, "Socket_Projectile")
        st = _bone_m(rig, "Stone")
        z = m.to_3x3().col[2].normalized()
        out[f] = {"pos": [round(c, 3) for c in m.translation], "forward_blender": [round(c, 3) for c in z],
                  "elevation_deg": round(math.degrees(math.asin(max(-1, min(1, z.z)))), 1),
                  "stone_scale": round(st.to_scale().x, 3), "stone_pos": [round(c, 3) for c in st.translation]}
    rig.animation_data.action = None
    return out


def _basket_tris():
    """the basket's triangles (Frame's, at the basket): (heap -- the stone-faced top and the stones on it --, the rest)"""
    o = bpy.data.objects[MESH]
    me = o.data
    stone_slot = next(i for i, m in enumerate(me.materials) if m is not None and m.name == "M_VKI_StoneBlockIn")
    gi = o.vertex_groups["Frame"].index

    def inb(i):
        v = me.vertices[i]
        return (math.hypot(v.co.x - BASKET.x, v.co.y - BASKET.y) < 0.3 and v.co.z > BASKET.z - 0.001
                and any(g.group == gi and g.weight > 0.5 for g in v.groups))
    heap, wall = [], []
    for p in me.polygons:
        if all(inb(i) for i in p.vertices):
            (heap if p.material_index == stone_slot else wall).append(tuple(p.vertices))
    return heap, wall


def _basket_body_tris():
    """the basket's closed body alone (its lathe: walls + the heap's top), without the stones lying on the heap (their
    lower halves are inside it)"""
    me = bpy.data.objects[MESH].data
    prof = [(r, BASKET.z + z) for r, z in BASKET_PROF]

    def on_lathe(i):
        v = me.vertices[i].co
        r = math.hypot(v.x - BASKET.x, v.y - BASKET.y)
        return any(abs(r - pr) < 2e-3 and abs(v.z - pz) < 2e-3 for pr, pz in prof)
    heap, wall = _basket_tris()
    return [t for t in heap + wall if all(on_lathe(i) for i in t)]


def _windlass_turn(rig):
    """the Windlass bone's turn about X (radians) at the current frame"""
    z = rig.pose.bones["Windlass"].matrix.to_3x3().col[2]
    return math.atan2(-z.y, z.z)


def check_load():
    """Load from its keys: the windlass's speed (turns a second, frame to frame) while the rope is run out and while the
    heaves wind it in; the stone kept inside the basket's closed body whenever it is not full size (rays from each of
    its vertices leave through the basket's own faces: it grows unseen); its lowest point over the cup's rim"""
    rig = bpy.data.objects[RIG]
    sc = bpy.context.scene
    act = use_clip(rig, "Load")
    N = int(act["frames"])
    _, vb, _ = _parts()
    stone_i = [i for i, b in enumerate(vb) if b == "Stone"]
    heap, wall = _basket_tris()
    body = _basket_body_tris()
    psi, scale, hidden_bad, grow_frames = [], [], [], []
    for f in range(N + 1):
        sc.frame_set(f)
        psi.append(_windlass_turn(rig))
        s = rig.pose.bones["Stone"].matrix.to_scale().x
        scale.append(s)
        if 0.002 < s < 0.999:
            grow_frames.append(f)
            co = _eval_co()
            bvh = BVHTree.FromPolygons(co, body, epsilon=0.0)
            for i in stone_i:
                for d in (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, -1, 0)), Vector((-0.6, 0.6, -0.5))):
                    loc, nrm, idx, dist = bvh.ray_cast(co[i], d.normalized())
                    if loc is None or nrm.dot(d) <= 0.0:
                        hidden_bad.append((f, i))
                        break
    rate = []
    for f in range(N):
        d = (psi[f + 1] - psi[f] + math.pi) % (2 * math.pi) - math.pi
        rate.append(d * FPS / (2 * math.pi))
    c0, c1 = LOAD["carry"]
    w0, w1 = LOAD["wind"]
    # the stone seated in the cup (IdleLoaded): how many of its triangles touch the cup's (the static's own fit)
    act = use_clip(rig, "IdleLoaded")
    sc.frame_set(0)
    co = _eval_co()
    co0, _, tris = _parts()
    seated = len(BVHTree.FromPolygons(co, tris["Stone"], epsilon=0.0).overlap(
        BVHTree.FromPolygons(co, tris["Arm"] + tris["Arm_Tip"], epsilon=0.0)))
    # the windlass's spokes through a whole turn against the basket (the overlap check holds the windlass as fixed),
    # and its closest approach
    bas = BVHTree.FromPolygons(co0, heap + wall, epsilon=0.0)
    wi = sorted({i for t in tris["Windlass"] for i in t})
    sweep_hits, gap = [], 9.0
    for k in range(72):
        Mw = rx(2 * math.pi * k / 72, DRUM)
        if len(BVHTree.FromPolygons([Mw @ c for c in co0], tris["Windlass"], epsilon=0.0).overlap(bas)):
            sweep_hits.append(k * 5)
        gap = min(gap, min((bas.find_nearest(Mw @ co0[i])[3] for i in wi), default=9.0))
    rig.animation_data.action = None
    pay = rate[c0 - 1:c1]
    wind = rate[w0 - 1:w1 + 1]
    return {"payout_frames": [c0, c1], "payout_turns": round(sum(pay) / FPS, 3), "payout_peak_tps": round(max(pay), 2),
            "payout_mean_tps": round(sum(pay) / FPS / ((c1 - c0) / FPS), 2),
            "payout_first_steps_tps": [round(r, 2) for r in rate[c0 - 1:c0 + 5]],
            "payout_last_steps_tps": [round(r, 2) for r in rate[c1 - 5:c1 + 1]],
            "wind_frames": [w0, w1], "wind_turns": round(-sum(wind) / FPS, 3),
            "wind_mean_tps": round(-sum(wind) / FPS / ((w1 - w0) / FPS), 2), "wind_peak_tps": round(-min(wind), 2),
            "max_deg_per_frame": round(max(abs(r) for r in rate) * 360 / FPS, 1),
            "rate_tps": [round(r, 2) for r in rate],
            "stone_grow_frames": grow_frames, "stone_not_hidden_while_growing": hidden_bad[:10] or "none",
            "basket_tris": {"heap": len(heap), "wall": len(wall), "body": len(body)},
            "stone_cup_overlaps_seated": seated,
            "windlass_turn_vs_basket": {"hits_at_deg": sweep_hits or "none", "closest_vertex_mm": round(gap * 1000, 1)},
            "events": {k: round(v / FPS, 3) for k, v in clip_events("Load", analyse()).items()}}


def check_overlaps(clips=None):
    """moving parts through fixed ones, frame by frame (triangle overlaps of the skinned mesh): the arm and the stone
    against the frame (skein left out) / windlass / wheels / basket; Destroyed's loose wheel and tip against the rest;
    Load's stone against the arm on its way to the cup (more than the seated stone's own contact with its cup), and
    against the basket's heap only while it is lifted out through it (by design: listed apart as `Load_by_design`)"""
    rig = bpy.data.objects[RIG]
    co0, vb, tris = _parts()
    sc = bpy.context.scene

    def near_pivot(i):
        c = co0[i]
        return abs(c.x) < 0.7 and math.hypot(c.y - PIVOT.y, c.z - PIVOT.z) < 0.26
    frame_t = [t for t in tris["Frame"] if not any(near_pivot(i) for i in t)]
    fixed = frame_t + tris["Windlass"] + tris["Wheel_FR"] + tris["Wheel_BL"] + tris["Wheel_BR"]
    heap = set(_basket_tris()[0])
    fixed_noheap = [t for t in fixed if tuple(t) not in heap]
    # the stone seated in the cup touches it (the static's own fit, IdleLoaded): on its way in, only more than that counts
    use_clip(rig, "IdleLoaded")
    sc.frame_set(0)
    co = _eval_co()
    seat = len(BVHTree.FromPolygons(co, tris["Stone"], epsilon=0.0).overlap(
        BVHTree.FromPolygons(co, tris["Arm"] + tris["Arm_Tip"], epsilon=0.0)))
    out = {"stone_seat_contact": seat}
    for clip in (clips or CLIPS):
        act = use_clip(rig, clip)
        bad = []
        by_design = []
        for f in range(int(act["frames"]) + 1):
            sc.frame_set(f)
            co = _eval_co()
            B = lambda ts: BVHTree.FromPolygons(co, ts, epsilon=0.0)
            fx = B(fixed + (tris["Wheel_FL"] if clip != "Destroyed" else []))
            st_fx = fx
            if clip == "Load" and LOAD["lift"][0] <= f <= LOAD["lift"][1]:
                st_fx = B(fixed_noheap + tris["Wheel_FL"])
                n = len(B(tris["Stone"]).overlap(B(list(heap))))
                if n:
                    by_design.append((f, "stone-heap", n))
            pairs = [("arm", B(tris["Arm"]), fx), ("tip", B(tris["Arm_Tip"]), fx), ("stone", B(tris["Stone"]), st_fx)]
            if clip == "Load" and f < LOAD["lift"][1]:
                pairs.append(("stone-arm", B(tris["Stone"]), B(tris["Arm"] + tris["Arm_Tip"])))
            if clip == "Destroyed":
                # (the axle runs through the wheel's hub until it has slid off; the arm's two halves meet at the cut
                # until it snaps: both by design)
                if f >= DEST["slide"][1]:
                    pairs.append(("wheelFL", B(tris["Wheel_FL"]), B(fixed + tris["Arm"] + tris["Arm_Tip"])))
                if f > DEST["snap"]:
                    pairs.append(("tip-arm", B(tris["Arm_Tip"]), B(tris["Arm"])))
            for nm, a, b in pairs:
                n = len(a.overlap(b))
                if n > (seat if nm == "stone-arm" else 0):
                    bad.append((f, nm, n))
                elif n:
                    by_design.append((f, nm, n))            # the stone settling into its seat (<= the seat's contact)
        out[clip] = bad[:40] if bad else "none"
        if by_design:
            out[clip + "_by_design"] = by_design
    rig.animation_data.action = None
    return out


# ================================================================= renders (renders/units/siege_catapult)
def _cam(name, loc, target, lens=40.0, ortho=None):
    sc = bpy.context.scene
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cd.lens = lens or 40.0
    cd.sensor_width = 36.0
    cd.clip_start, cd.clip_end = 0.05, 300.0
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    else:
        cd.type = "PERSP"
    return cam


def _render(cam, path, res=(1400, 1000), samples=24):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = res[0], res[1], 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = path
    sc.eevee.taa_render_samples = samples
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return path


def _sheet(paths, out, cols):
    """tile PNGs (all one size) into one image, row-major from the top left; a 6 px gap"""
    import numpy as np
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p, check_existing=False)
        w, h = im.size
        a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        imgs.append(a)
        bpy.data.images.remove(im)
    h, w = imgs[0].shape[:2]
    rows = (len(imgs) + cols - 1) // cols
    gap = 6
    W, H = cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap
    canvas = np.ones((H, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.08
    for k, a in enumerate(imgs):
        r, c = divmod(k, cols)
        y0 = H - (r + 1) * h - r * gap                      # Blender images start at the bottom row
        x0 = c * (w + gap)
        canvas[y0:y0 + h, x0:x0 + w] = a
    img = bpy.data.images.new("vku_sheet", W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = out
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    for p in paths:
        try:
            os.remove(p)
        except OSError:
            pass
    return out


def _ground(checker=False):
    g = bpy.data.objects[GROUND]
    for p in g.data.polygons:
        p.material_index = 1 if checker else 0


def _charred_material():
    """the charred look for the wreck: the kit's dark wood (M_VKI_WoodDark) at 0.46 -- the burnt static's vertex
    darkening (0.6) against the unit's fresh one (~0.1); Unity: M_VKU_WoodCharred, made by the setup the same way"""
    m = bpy.data.materials.get("M_VKU_WoodCharred")
    if m is not None:
        return m
    m = bpy.data.materials["M_VKI_WoodDark"].copy()
    m.name = "M_VKU_WoodCharred"
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    inp = bsdf.inputs["Base Color"]
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    mix.inputs[7].default_value = (0.46, 0.46, 0.46, 1.0)
    if inp.is_linked:
        src = inp.links[0].from_socket
        nt.links.remove(inp.links[0])
        nt.links.new(src, mix.inputs[6])
    else:
        mix.inputs[6].default_value = inp.default_value
    nt.links.new(mix.outputs[2], inp)
    return m


def _copy_unit(tag, charred=False):
    """a second rig + mesh (shared data) for lineups; posed by hand"""
    rig = bpy.data.objects[RIG]
    mo = bpy.data.objects[MESH]
    r2 = rig.copy()
    r2.name = f"{RIG}_{tag}"
    r2.animation_data_clear()
    m2 = mo.copy()
    m2.name = f"{MESH}_{tag}"
    m2.parent = r2
    m2.modifiers["Armature"].object = r2
    coll = bpy.data.collections[UNIT]
    coll.objects.link(r2)
    coll.objects.link(m2)
    if charred:
        wood = [i for i, s in enumerate(m2.material_slots) if s.material and s.material.name == "M_VK_Wood"]
        for i in wood:
            m2.material_slots[i].link = "OBJECT"
            m2.material_slots[i].material = _charred_material()
    return r2, m2


def _remove(objs):
    for o in objs:
        bpy.data.objects.remove(o)


def _pose_obj(r, clip, f, an, rest):
    for pb in r.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    set_pose(r, matrices(pose_at(clip, f, an), an, rest))


def render_setup():
    """outdoor light for the checks (this file's own copies of the kit's interior Day key / fill / world): a brighter
    sun, a grey-blue backdrop instead of the interiors' black void"""
    sc = bpy.context.scene
    for n, e in (("VKI_Key", 3.2), ("VKI_Fill", 1.0)):
        o = bpy.data.objects.get(n)
        if o is not None:
            o.data.energy = e
    w = sc.world
    if w is not None and w.use_nodes:
        for nd in w.node_tree.nodes:
            if nd.type == "BACKGROUND" and nd.label == "VKI_LIGHT":
                nd.inputs[1].default_value = 1.0
            if nd.type == "BACKGROUND" and nd.label == "VKI_VOID":
                nd.inputs[0].default_value = (0.30, 0.34, 0.40, 1.0)
    sc.render.film_transparent = False


def _ghost_stones(clip, frames, an, rest, tag):
    """copies of the projectile mesh where the Stone bone puts the stone at each frame (the path, in one picture)"""
    sme = bpy.data.objects[STONE].data
    coll = bpy.data.collections[UNIT]
    rig = bpy.data.objects[RIG]
    out = []
    for f in frames:
        p = pose_at(clip, f, an)
        M = matrices(p, an, rest)["Stone"]
        if M.to_scale().x < 0.5:
            continue
        o = bpy.data.objects.new(f"VKU_Ghost_{tag}_{f:03d}", sme)
        coll.objects.link(o)
        o.matrix_world = rig.matrix_world @ M @ rest["Stone"].inverted() @ Matrix.Translation(STONE_C)
        out.append(o)
    return out


def render_all(which=("views", "throw", "load", "move", "hit", "destroyed", "snap", "game", "windlass", "stone",
                      "gameload")):
    rig = bpy.data.objects[RIG]
    mesh = bpy.data.objects[MESH]
    stone = bpy.data.objects[STONE]
    an = analyse()
    rest = rest_mats(rig)
    sc = bpy.context.scene
    render_setup()
    out = {}
    stone_loc = stone.location.copy()
    stone.hide_render = True
    try:
        rig.animation_data.action = None if rig.animation_data else None
        C = Vector((0.0, 0.0, 0.9))
        if "views" in which:
            for pose_name, clip, f in (("idle", "Idle", 0), ("loaded", "IdleLoaded", 0)):
                _pose_obj(rig, clip, f, an, rest)
                paths = []
                for k, (loc, tgt, lens) in enumerate((((-5.2, -6.2, 3.4), C, 40), ((5.6, 5.4, 3.6), C, 40),
                                                      ((7.5, 0.3, 1.5), (0, 0, 1.0), 40), ((-6.0, 4.8, 2.0), C, 40),
                                                      ((0.0, -7.6, 1.6), (0, 0, 1.0), 40), ((0.01, 0.0, 9.0), (0, 0, 0), 40))):
                    paths.append(_render(_cam("VKU_Cam", loc, tgt, lens), os.path.join(RENDERS, f"_v{k}.png"), (900, 700)))
                out["views_" + pose_name] = _sheet(paths, os.path.join(RENDERS, f"views_{pose_name}.png"), 3)
            # close-ups: the arm's pivot and skein, the windlass and the rope, a wheel, the cup and stone
            _pose_obj(rig, "IdleLoaded", 0, an, rest)
            paths = []
            for k, (loc, tgt) in enumerate((((1.9, -0.9, 1.3), (0.0, 0.3, 0.6)), ((1.6, 3.2, 1.9), (0.0, 1.9, 1.0)),
                                            ((2.7, -2.2, 0.7), (1.0, -1.35, 0.34)), ((-1.3, 2.9, 2.3), (0.0, 2.0, 1.3)))):
                paths.append(_render(_cam("VKU_Cam", loc, tgt, 40), os.path.join(RENDERS, f"_c{k}.png"), (900, 700)))
            out["closeups"] = _sheet(paths, os.path.join(RENDERS, "closeups_loaded.png"), 2)
            _pose_obj(rig, "Idle", 0, an, rest)
            paths = []
            for k, (loc, tgt) in enumerate((((1.6, -2.0, 2.4), (0.0, -0.4, 1.8)), ((-1.8, 1.0, 2.8), (0.0, -0.2, 1.9)))):
                paths.append(_render(_cam("VKU_Cam", loc, tgt, 40), os.path.join(RENDERS, f"_d{k}.png"), (900, 700)))
            out["closeups_stop"] = _sheet(paths, os.path.join(RENDERS, "closeups_stop.png"), 2)
            # the rope at the windlass: hanging loose (Idle), swung over the drum and run out (Load), dropped (Throw)
            paths = []
            for k, (clip, f) in enumerate((("Idle", 0), ("Load", 6), ("Load", 30), ("Load", 80), ("Throw", 8), ("Throw", 14))):
                _pose_obj(rig, clip, f, an, rest)
                paths.append(_render(_cam("VKU_Cam", (2.2, 3.6, 1.9), (0.0, 1.7, 1.1), 40),
                                     os.path.join(RENDERS, f"_r{k}.png"), (720, 560)))
            out["closeups_rope"] = _sheet(paths, os.path.join(RENDERS, "closeups_rope.png"), 3)
        strips = {
            "throw": ("Throw", [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 19, 24, 32, 45],
                      ((6.4, -1.6, 2.2), (0.0, 0.1, 1.2), 32, None)),
            "load": ("Load", [0, 8, 20, 32, 44, 57, 70, 86, 100, 108, 114, 120, 126, 132, 139, 150],
                     ((5.0, 4.6, 3.0), (0.0, 0.5, 1.1), 32, None)),
            # the windlass paying out: the ease-up (every 4th frame), then four running frames back to back
            "windlass": ("Load", [1, 5, 9, 13, 17, 21, 25, 29, 30, 31, 32, 33],
                         ((-1.9, 3.3, 1.75), (-0.15, 1.95, 0.98), 45, None)),
            # the stone: hidden in the basket, lifted out, swung over, set down in the cup
            "stone": ("Load", [100, 106, 110, 114, 118, 121, 124, 127, 130, 133, 136, 139],
                      ((2.6, 3.9, 2.5), (0.35, 1.85, 1.25), 40, None)),
            "hit": ("Hit", [0, 1, 2, 3, 4, 6, 8, 10, 13, 18], ((5.2, -4.4, 2.2), (0.0, -0.2, 0.9), 32, None)),
            "destroyed": ("Destroyed", [0, 5, 7, 9, 11, 12, 14, 16, 18, 20, 23, 26, 29, 31, 34, 44],
                          ((5.4, -5.6, 3.0), (0.4, -1.0, 0.6), 32, None)),
            "snap": ("Destroyed", [12, 13, 14, 15, 16, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 44],
                     ((6.5, -1.4, 1.6), (0.0, -1.2, 1.0), 30, None)),
        }
        for key, (clip, frames, (loc, tgt, lens, ortho)) in strips.items():
            if key not in which:
                continue
            act = use_clip(rig, clip)
            paths = []
            for f in frames:
                sc.frame_set(f)
                paths.append(_render(_cam("VKU_Cam", loc, tgt, lens or 40, ortho), os.path.join(RENDERS, f"_{key}{f:03d}.png"),
                                     (720, 560), 16))
            out[key] = (_sheet(paths, os.path.join(RENDERS, f"strip_{key}.png"), 4 if len(frames) > 10 else 5), frames)
            rig.animation_data.action = None
        if "move" in which:
            # travel preview over a 0.5 m checker: the rig carried along Motion's travel, a fixed camera at the left side
            _ground(True)
            act = use_clip(rig, "Move")
            paths = []
            frames = [0, 8, 16, 24, 32, 40, 48, 56]
            for f in frames:                              # 45 deg of wheel and 0.267 m of road between two frames
                sc.frame_set(f)
                rig.location = (0.0, -MOVE_SPEED * f / FPS, 0.0)
                paths.append(_render(_cam("VKU_Cam", (4.4, -2.6, 2.6), (1.0, -2.6, 0.25), None, 3.4),
                                     os.path.join(RENDERS, f"_m{f:03d}.png"), (720, 520), 16))
            out["move"] = (_sheet(paths, os.path.join(RENDERS, "strip_move_wheels.png"), 4), frames)
            rig.location = (0.0, 0.0, 0.0)
            rig.animation_data.action = None
            _ground(False)
        if "game" in which:
            # the RPG camera: pitch 50, lens 38, 22 m (the kit's VKI_CAM), a lineup of poses and the charred wreck
            copies = []
            lineup = (("Idle", 0, False), ("IdleLoaded", 0, False), ("Throw", an["release"], False),
                      ("Destroyed", 44, False), ("Destroyed", 44, True))
            for i, (clip, f, ch) in enumerate(lineup):
                r2, m2 = _copy_unit(f"L{i}", ch)
                copies += [r2, m2]
                r2.location = ((i - (len(lineup) - 1) / 2) * 4.0, 0.0, 0.0)
                r2.rotation_euler = (0.0, 0.0, math.radians(-25.0))
                _pose_obj(r2, clip, f, an, rest)
            stone.hide_render = False
            stone.location = (-2.0, -3.4, 0.16)
            mesh.hide_render = True
            p = math.radians(50.0)
            for D, nm in ((22.0, "game_22m.png"), (14.0, "game_14m.png")):
                cam = _cam("VKU_Cam", (0.0, -math.cos(p) * D, math.sin(p) * D), (0.0, 0.0, 0.0), 38.0)
                cam.rotation_euler = (math.radians(90 - 50), 0.0, 0.0)
                out[nm] = _render(cam, os.path.join(RENDERS, nm), (1920, 1080), 32)
            mesh.hide_render = False
            _remove(copies)
        if "stone" in which:
            # the stone's way in one picture: the engine at Loaded, a copy of the stone every 3rd frame of its way
            stone.hide_render = True
            _pose_obj(rig, "Load", LOAD["lift"][1], an, rest)
            ghosts = _ghost_stones("Load", range(LOAD["lift"][0], LOAD["lift"][1], 3), an, rest, "P")
            for nm, (loc, tgt) in (("stone_path_rear.png", ((2.9, 4.4, 2.6), (0.35, 1.85, 1.2))),
                                   ("stone_path_side.png", ((4.6, 1.2, 1.7), (0.3, 1.7, 1.2)))):
                out[nm] = _render(_cam("VKU_Cam", loc, tgt, 40), os.path.join(RENDERS, nm), (1400, 1000), 32)
            _remove(ghosts)
        if "gameload" in which:
            # the RPG camera (as "game") on Load: rope hooked, the stone in the basket (hidden), lifted, swung, in the cup;
            # and one engine with the stone's way as copies
            copies = []
            lineup = (57, 104, 116, 127, 150)
            for i, f in enumerate(lineup):
                r2, m2 = _copy_unit(f"G{i}")
                copies += [r2, m2]
                r2.location = ((i - (len(lineup) - 1) / 2) * 4.0, 0.0, 0.0)
                r2.rotation_euler = (0.0, 0.0, math.radians(-25.0))
                _pose_obj(r2, "Load", f, an, rest)
            stone.hide_render = True
            mesh.hide_render = True
            p = math.radians(50.0)
            cam = _cam("VKU_Cam", (0.0, -math.cos(p) * 22.0, math.sin(p) * 22.0), (0.0, 0.0, 0.0), 38.0)
            cam.rotation_euler = (math.radians(90 - 50), 0.0, 0.0)
            out["game_22m_load.png"] = _render(cam, os.path.join(RENDERS, "game_22m_load.png"), (1920, 1080), 32)
            _remove(copies)
            mesh.hide_render = False
            # one engine at Loaded with its stone's way, the game camera turned to look at its rear-left corner
            _pose_obj(rig, "Load", LOAD["lift"][1], an, rest)
            ghosts = _ghost_stones("Load", range(LOAD["lift"][0], LOAD["lift"][1], 3), an, rest, "G")
            for D, nm in ((22.0, "game_22m_stonepath.png"),):
                yaw = math.radians(150.0)                         # from behind and to its left (+X)
                tgt = Vector((0.0, 0.6, 0.8))
                off = Vector((math.sin(yaw) * math.cos(p), -math.cos(yaw) * math.cos(p), math.sin(p))) * D
                cam = _cam("VKU_Cam", tgt + off, tgt, 38.0)
                out[nm] = _render(cam, os.path.join(RENDERS, nm), (1920, 1080), 32)
            _remove(ghosts)
    finally:
        stone.location = stone_loc
        stone.hide_render = False
        rig.location = (0.0, 0.0, 0.0)
        if rig.animation_data:
            rig.animation_data.action = None
        for pb in rig.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
    return out


# ================================================================= export (into the package's Art/Units)
FBX = dict(apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", use_armature_deform_only=False,
           add_leaf_bones=False, primary_bone_axis="Y", secondary_bone_axis="X", armature_nodetype="NULL",
           bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=False, use_custom_props=False,
           path_mode="STRIP", embed_textures=False, colors_type="LINEAR", use_tspace=True)


def _select(objs):
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.hide_set(False)
        o.select_set(True)
    vl.objects.active = objs[0]


def _export_clip(rig, clip, path, default_frame=0):
    """one clip as its own FBX: the skeleton with one baked take; the file's default pose = default_frame (the clip's
    first frame for the delivered files)"""
    use_clip(rig, clip)
    bpy.context.scene.frame_set(default_frame)
    _select([rig])
    opts = dict(FBX)
    opts.update(bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True, bake_anim_step=1.0,
                bake_anim_simplify_factor=0.0)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE"}, **opts)
    return path


def export_all():
    rig = bpy.data.objects[RIG]
    mesh = bpy.data.objects[MESH]
    stone = bpy.data.objects[STONE]
    an = analyse()
    os.makedirs(os.path.join(EXPORT, "Anims"), exist_ok=True)
    written = []
    sc = bpy.context.scene
    keep = (sc.frame_start, sc.frame_end, sc.render.fps)
    try:
        # the model in the bind pose, no clip assigned
        if rig.animation_data:
            rig.animation_data.action = None
        for pb in rig.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()
        _select([rig, mesh])
        path = os.path.join(EXPORT, UNIT + ".fbx")
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE", "MESH"}, **FBX)
        written.append(path)
        # one FBX per clip: the skeleton with one baked take
        meta = []
        sc.render.fps = FPS
        for clip, (fn, N, loop, moves, _) in CLIPS.items():
            p = os.path.join(EXPORT, "Anims", f"{UNIT}@{clip}.fbx")
            _export_clip(rig, clip, p)
            written.append(p)
            meta.append({"name": clip, "frames": N, "fps": FPS, "loop": loop, "rootMotion": moves,
                         "events": [{"name": k, "time": round(v / FPS, 4)} for k, v in clip_events(clip, an).items()]})
        with open(os.path.join(EXPORT, "Anims", "siegecatapult_clips.json"), "w", encoding="utf-8") as f:
            json.dump({"clips": meta}, f, indent=1)
        written.append(os.path.join(EXPORT, "Anims", "siegecatapult_clips.json"))
        # the projectile: a static mesh written the kit's way (Unity vertex = (-x, z, -y), no root rotation)
        rig.animation_data.action = None
        loc = stone.location.copy()
        stone.location = (0.0, 0.0, 0.0)
        bpy.context.view_layer.update()
        _select([stone])
        p = os.path.join(EXPORT, STONE + ".fbx")
        bpy.ops.export_scene.fbx(filepath=p, use_selection=True, object_types={"MESH"}, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                                 bake_space_transform=True, mesh_smooth_type="FACE", use_mesh_modifiers=False,
                                 colors_type="LINEAR", use_custom_props=False, add_leaf_bones=False, bake_anim=False,
                                 path_mode="STRIP", embed_textures=False, use_tspace=True)
        stone.location = loc
        written.append(p)
        # what the Unity setup needs besides the clips
        me = mesh.data
        info = {
            "unit": UNIT, "model": UNIT + ".fbx", "stone": STONE + ".fbx",
            "materials": [m.name for m in me.materials], "stone_materials": [m.name for m in stone.data.materials],
            "charred": {"M_VK_Wood": {"from": "M_VKI_WoodDark", "scale": 0.46, "name": "M_VKU_WoodCharred"}},
            "tris": sum(len(p.vertices) - 2 for p in me.polygons),
            "stone_tris": sum(len(p.vertices) - 2 for p in stone.data.polygons),
            "stone_radius": 0.17, "move_speed_mps": round(MOVE_SPEED, 5),
            "release_elevation_deg": round(an["release_elev"], 1),
            "sockets": ["Socket_Projectile"], "motion": "Motion",
            "bounds_blender": [[-1.7, -3.6, 0.0], [2.0, 2.5, 2.6]],
        }
        with open(os.path.join(EXPORT, "siegecatapult_unit.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, indent=1)
        written.append(os.path.join(EXPORT, "siegecatapult_unit.json"))
    finally:
        sc.frame_start, sc.frame_end, sc.render.fps = keep
        if rig.animation_data:
            rig.animation_data.action = None
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
    return written


def check_reimport():
    """import the written model and the Move / Throw / Load clips into a scratch scene: bones, meshes, UVs, colours,
    Motion's travel, the wheels' turn, the stone's scale keys, the windlass's turn per frame, the stone's way in Load
    (from a scratch copy, see below) -- then remove everything imported"""
    import tempfile, shutil
    out = {}
    tmpdir = tempfile.mkdtemp(prefix="vku_")
    load_check = None
    try:
        load_check = _export_clip(bpy.data.objects[RIG], "Load", os.path.join(tmpdir, "load_check.fbx"), LOAD["lift"][0])
    finally:
        bpy.data.objects[RIG].animation_data.action = None
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
    before = set(bpy.data.objects)
    kinds = ("meshes", "materials", "armatures", "actions", "images")
    had = {k: set(getattr(bpy.data, k)) for k in kinds}
    sc_old = bpy.context.window.scene
    tmp = bpy.data.scenes.new("VKU_Reimport")
    bpy.context.window.scene = tmp
    try:
        bpy.ops.import_scene.fbx(filepath=os.path.join(EXPORT, UNIT + ".fbx"))
        arm = next(o for o in tmp.objects if o.type == "ARMATURE")
        mo = [o for o in tmp.objects if o.type == "MESH"]
        me = mo[0].data
        out["model"] = {"bones": len(arm.data.bones), "names": [b.name for b in arm.data.bones],
                        "motion_parent": arm.data.bones["Motion"].parent.name if arm.data.bones["Motion"].parent else None,
                        "meshes": len(mo), "tris": sum(len(p.vertices) - 2 for p in me.polygons),
                        "uv_layers": len(me.uv_layers), "colors": [c.name for c in me.color_attributes],
                        "materials": [m.name for m in me.materials], "groups": len(mo[0].vertex_groups)}
        for clip in ("Move", "Throw", "Load"):
            n0 = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=os.path.join(EXPORT, "Anims", f"{UNIT}@{clip}.fbx"))
            a2 = next(o for o in set(bpy.data.objects) - n0 if o.type == "ARMATURE")
            act = a2.animation_data.action
            r0, r1 = act.frame_range
            res = {"frames": [r0, r1]}
            tmp.frame_set(int(r0))
            m0 = a2.pose.bones["Motion"].matrix.translation.copy()
            w0 = a2.pose.bones["Wheel_FL"].matrix.to_3x3().col[2].copy()
            tmp.frame_set(int(r1))
            m1 = a2.pose.bones["Motion"].matrix.translation.copy()
            res["motion_travel"] = [round(c, 4) for c in (m1 - m0)]
            if clip == "Move":
                tmp.frame_set(int(r0) + 8)
                w8 = a2.pose.bones["Wheel_FL"].matrix.to_3x3().col[2]
                res["wheel_turn_8f_deg"] = round(math.degrees(w0.angle(w8)), 2)
            if clip == "Throw":
                sc_ = []
                for f in range(int(r0), int(r1) + 1):
                    tmp.frame_set(f)
                    sc_.append(round(a2.pose.bones["Stone"].matrix.to_scale().x, 3))
                res["stone_scale"] = sc_
            if clip == "Load":
                # the windlass's largest turn between two frames (q and -q are one turn)
                prev, top = None, 0.0
                for f in range(int(r0), int(r1) + 1):
                    tmp.frame_set(f)
                    q = a2.pose.bones["Windlass"].matrix.to_quaternion()
                    if prev is not None:
                        top = max(top, math.degrees(2.0 * math.acos(min(1.0, abs(prev.dot(q))))))
                    prev = q
                res["windlass_max_deg_per_frame"] = round(top, 1)
            out[clip] = res
        if load_check is not None:
            # the stone's keys, read from a scratch copy of Load whose default pose is a frame with the stone full size
            # (Blender's importer takes a scaled bone's default as its rest: the delivered file's default is frame 0,
            # the stone hidden at 0.001, so it reads every later scale 1000x; Unity plays the keys themselves)
            n0 = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=load_check)
            a2 = next(o for o in set(bpy.data.objects) - n0 if o.type == "ARMATURE")
            r0 = int(a2.animation_data.action.frame_range[0])
            pts = {}
            for f in (LOAD["basket"] - 1, LOAD["basket"], LOAD["grow"][0], LOAD["grow"][1], LOAD["lift"][0], 118, 127,
                      LOAD["lift"][1], CLIPS["Load"][1]):
                tmp.frame_set(r0 + f)
                m = a2.pose.bones["Stone"].matrix
                pts[f] = {"scale": round(m.to_scale().x, 3), "at": [round(c, 3) for c in m.translation]}
            out["Load_stone_keys"] = pts
    finally:
        for o in set(bpy.data.objects) - before:
            bpy.data.objects.remove(o)
        bpy.context.window.scene = sc_old
        bpy.data.scenes.remove(tmp)
        for k in kinds:                                   # the imported data too, or a later save keeps it
            coll = getattr(bpy.data, k)
            for idb in set(coll) - had[k]:
                coll.remove(idb)
        shutil.rmtree(tmpdir, ignore_errors=True)
    return out


def run(args):
    out = {}
    for a in args:
        if a.startswith("export_dir="):
            set_export_dir(a[len("export_dir="):])
    out["export_dir"] = EXPORT
    if "rig" in args:
        out["rig"] = build_rig()
    an = analyse()
    out["fit"] = {"stop_deg": round(math.degrees(an["stop"]), 2), "loaded_deg": round(math.degrees(an["loaded"]), 2),
                  "arm_elev_bind_deg": round(an["arm_elev0"], 2), "drum_hit_at_bind": an["drum_hit_at_bind"],
                  "release_frame": an["release"], "release_elev_deg": round(an["release_elev"], 1),
                  "tilt_deg": round(math.degrees(an["tilt"]), 2), "tilt_lift_mm": round(an["tilt_lift"] * 1000, 1),
                  "sweep_hits": an["sweep_hits"], "hook": [round(c, 3) for c in an["hook"]],
                  "move_speed": round(MOVE_SPEED, 5),
                  "tip_lift_cm": {f: round(v * 100, 1) for f, v in _tip_lift(an).items()}}
    if "clips" in args:
        out["clips"] = build_clips()
    if "check" in args:
        out["lowest"] = check_lowest()
        out["move"] = check_move()
        out["socket"] = check_socket()
        out["load"] = check_load()
        out["overlaps"] = check_overlaps()
    if "renders" in args:
        which = [a[len("only="):].split(",") for a in args if a.startswith("only=")]
        out["renders"] = render_all(*(which or []))
    if "export" in args:
        out["export"] = export_all()
    if "reimport" in args:
        out["reimport"] = check_reimport()
    return out
