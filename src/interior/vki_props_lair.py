# ===================== VKI PROPS LAIR: goblin camps, spider nests, rat warrens (adventure kit) =====================
# Adventure kit (docs/ADVENTURE_KIT.md). Package "adventure". Loaded by vki_ns() after vki_props_adventure; uses the
# prop helpers (vki_dpr_*, vki_adv_*, vki_dun_*, vki_home_*, vki_sto_*). Props: origin at the footprint centre, back
# toward +Y, real height (§5). Silk: the FX slot (65) carries M_VKI_Web (T_VKI_Web_BC with alpha) on web masters, with
# the card's own 0..1 UVs; bones WAX -> M_VKI_Bone; egg sacs and cocoon silk stay WAX (M_VKI_Wax, a pale cream).
# Every top-level name starts with vki_/VKI_ (T18).
#   goblins: Overlay_Bedroll, Prop_FirePit_Camp (stone ring, logs, fire, a spit with a roasting haunch; light),
#            Prop_Totem_Goblin (crooked pole, skulls, feathers, a hide banner), Prop_LeanTo (hide shelter on poles, 2 x 1),
#            Prop_Barricade_Stakes (sharpened stakes on a trestle, hewn points), Overlay_Refuse (gnawed bones, rags,
#            droppings)
#   spiders: Prop_Web_Corner (a web across a room corner, rot 0 = the NW corner), Overlay_WebFloor, Prop_EggSacs,
#            Prop_Cocoon (a wrapped victim leaning on the wall)
#   rats:    Prop_Burrow (an earth mound with a dark hole), Prop_RatHole_Wall (a gnawed hole at a wall's foot)
# Build: g["vki_ws_build"]("adventure", VKI_LAIR_NAMES); test: g["vki_test_pieces"](VKI_LAIR_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_LAIR_FIRE_W = 200.0


def vki_lair_web_mats(k):
    k.slot_mats[VKI_FX] = "M_VKI_Web"


def vki_lair_card(k, corners, t=0.006, u=(0.0, 1.0), v=(0.0, 1.0)):
    """a thin closed card (silk): corners = 4 points (3-D, in order round the card), thickness t along its normal;
    both big faces map the web texture over u x v (FX slot)"""
    P = [Vector(c) for c in corners]
    n = (P[1] - P[0]).cross(P[3] - P[0]).normalized()
    A = [k.bm.verts.new(p - n * t / 2) for p in P]
    B = [k.bm.verts.new(p + n * t / 2) for p in P]
    fs = [k.bm.faces.new(A[::-1]), k.bm.faces.new(B)]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(k.bm.faces.new((A[i], A[j], B[j], B[i])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    uvs = [(u[0], v[0]), (u[1], v[0]), (u[1], v[1]), (u[0], v[1])]
    for f in fs:
        f.material_index = VKI_FX
        f.smooth = False
        for l in f.loops:
            idx = A.index(l.vert) if l.vert in A else B.index(l.vert)
            l[k.uv].uv = uvs[idx]
    return A + B


# ---------------------------------------------------------------- goblins
def vki_lair_bedroll(k):
    """a hide spread on the floor (1.35 x 0.7), a rolled blanket at its head and a wisp of straw"""
    vki_dpr_blob(k, (0.0, 0.0), (0.68, 0.36), 0.001, 0.022, HIDE, ns=14, wob=0.12, seed=4)
    rv = _cyl(k, (-0.52, 0.0, 0.07), 0.07, 0.07, 0.55, 10, BURLAP, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    for f in vki_faces_of(rv):
        f.smooth = True
    k.set_dark(rv, 0.15)
    vki_dpr_mound(k, (0.40, 0.18, 0.02), 0.22, 0.14, 0.05, VKI_STRAW, z0=0.018, nr=2, ns=8, seed=5)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_lair_firepit(k):
    """a camp fire: a ring of stones (r 0.45) round an ash bed, crossed charred logs, embers and flames, and a spit on
    two forked sticks with a roasting haunch; light"""
    rnd = random.Random(14)
    for i in range(11):
        a = 2 * math.pi * i / 11 + rnd.uniform(-0.1, 0.1)
        s = rnd.uniform(0.08, 0.11)
        v = _ico(k, (math.cos(a) * 0.45, math.sin(a) * 0.45, s * 0.45), s, VKI_STONE_BLOCK_IN, scale=(1.2, 0.9, 0.7),
                 sub=1, jit=0.015, seed=20 + i)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
        k.set_dark(v, 0.1 + 0.25 * (i % 3) / 2)
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.38, 0.38, 0.05, VKI_ASH, z0=0.001, nr=2, ns=12, seed=6)
    vki_sto_logs(k, 0.0, [(0.02, 0.09, 0.055, 0.62, 0.5), (-0.03, 0.10, 0.05, 0.58, -0.6)])
    vki_sto_embers(k, 0.0, 0.0, 0.10, 7, 0.20, 0.20, 44, core=0.25, rmin=0.035, rmax=0.05, hmax=0.9)
    for (x, y, h, r, tl, sp, bw) in ((0.0, 0.0, 0.42, 0.09, 0.0, 0.2, 0.03), (-0.08, 0.05, 0.28, 0.07, -0.2, -0.5, -0.03),
                                     (0.08, -0.05, 0.26, 0.065, 0.2, 0.7, 0.02)):
        vki_sto_flame(k, Vector((x, y, 0.10)), h, r, tl, sp, bw, flat=0.8)
    for s in (-1.0, 1.0):                                                       # forked sticks
        vki_dpr_rod(k, (s * 0.62, 0.0, -0.02), (s * 0.60, 0.0, 0.70), 0.035, WOOD)
        vki_dpr_rod(k, (s * 0.60, 0.0, 0.62), (s * 0.64, 0.0, 0.78), 0.025, WOOD)
        vki_dpr_rod(k, (s * 0.60, 0.0, 0.62), (s * 0.55, 0.0, 0.77), 0.021, WOOD)             # thinner: T5S
    vki_dpr_rod(k, (-0.70, 0.0, 0.70), (0.70, 0.0, 0.70), 0.022, WOOD)             # spit
    vki_home_ham(k, 0.0, 0.0, 0.62, rz=0.0, s=1.1)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.95, 0]], vki_nav="block",
                  vki_lights=[vki_dpr_light("campfire", (0.0, -0.08, 0.75), VKI_LAIR_FIRE_W, VKI_DPR_BRAZIER_COL, 7.0, 0.25)],
                  vki_fx=[dict(fx="campfire", pos=[0.0, 0.0, 0.25], scale=1.2)])


def vki_lair_totem(k):
    """a goblin totem (2.4 m): a crooked pole on a cairn, a crossbar, skulls on top and on the bar, red feathers and a
    hide banner hanging from the bar"""
    rnd = random.Random(9)
    for i in range(6):
        a = 2 * math.pi * i / 6
        v = _ico(k, (math.cos(a) * 0.22, math.sin(a) * 0.22, 0.08), 0.11, VKI_STONE_BLOCK_IN, scale=(1.1, 1.0, 0.7),
                 sub=1, jit=0.02, seed=50 + i)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    pts = [(0.0, 0.0, -0.02), (0.03, 0.02, 0.8), (-0.02, 0.04, 1.6), (0.02, 0.02, 2.25)]
    for a, b in zip(pts[:-1], pts[1:]):
        v = vki_dpr_rod(k, a, b, 0.09, WOOD)
    vki_dpr_rod(k, (-0.48, 0.03, 1.78), (0.48, 0.03, 1.72), 0.06, WOOD)            # crossbar
    vki_dun_skull(k, (0.02, 0.02, 2.36), s=1.2, yaw=5, pitch=-5)
    for x, z in ((-0.40, 1.88), (0.40, 1.82)):
        vki_dun_skull(k, (x, 0.0, z), s=0.9, yaw=rnd.uniform(-20, 20), roll=10)
    for x in (-0.30, -0.18, 0.18, 0.30):                                           # feathers
        vki_dpr_rod(k, (x, -0.02, 1.72), (x + rnd.uniform(-0.04, 0.04), -0.05, 1.42), 0.03, CLOTH_A, d=0.008)
    before = set(k.bm.verts)
    k.box((0.0, -0.01, 1.42), (0.34, 0.012, 0.52), HIDE, bevel=0.0)                 # banner
    bv = [v for v in k.bm.verts if v not in before]
    for v in bv:
        if v.co.z < 1.3:
            v.co.x *= 0.7
    for (x, z) in ((0.0, 1.35), (0.0, 1.25)):
        k.box((x, -0.02, z + 0.1), (0.14, 0.012, 0.02), VOID, bevel=0.0)          # painted marks
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_note="2.4 m tall: against a north wall, or the back of a camp")


def vki_lair_leanto(k):
    """a hide lean-to (2.4 x 1.1 x 1.6): two forked front poles and a ridge pole, four rafters sloping back to the
    ground (+Y), three hide patches over them, a bedroll under it"""
    for x in (-1.1, 1.1):
        vki_dpr_rod(k, (x, -0.42, -0.02), (x, -0.42, 1.60), 0.06, WOOD)
    vki_dpr_rod(k, (-1.18, -0.42, 1.55), (1.18, -0.42, 1.55), 0.055, WOOD)
    for x in (-1.0, -0.33, 0.33, 1.0):
        vki_dpr_rod(k, (x, -0.46, 1.58), (x, 0.52, -0.02), 0.045, WOOD)
    a = Vector((0.0, -0.40, 1.60)); b = Vector((0.0, 0.50, 0.02))
    d = (b - a).normalized(); n = Vector((1, 0, 0)).cross(d).normalized()
    for i, (x0, x1) in enumerate(((-1.18, -0.38), (-0.38, 0.40), (0.40, 1.18))):      # abutting, not overlapping
        off = n * (0.035 + 0.004 * i)
        c = [a + Vector((x0, 0, 0)) + off, a + Vector((x1, 0, 0)) + off, b + Vector((x1, 0, 0)) + off,
             b + Vector((x0, 0, 0)) + off]
        vs = list({v for v in vki_lair_card(k, c, t=0.012)})
        for f in vki_faces_of(vs):
            f.material_index = HIDE
        k.set_dark(vs, 0.1 * i)
    vki_dpr_blob(k, (0.0, 0.05), (0.62, 0.30), 0.001, 0.02, HIDE, ns=12, wob=0.12, seed=8)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.95, 0]], vki_nav="block",
                  vki_note="its back (the low edge) toward +Y: set it against a wall")


def vki_lair_barricade(k):
    """a goblin barricade (1.5 m): a trestle of two crossed pairs of poles with a rail, five sharpened stakes leaning
    out toward -Y, their points pale hewn wood (the kit's stake rule)"""
    for x in (-0.62, 0.62):
        vki_dpr_rod(k, (x - 0.25, 0.25, -0.02), (x + 0.12, -0.10, 0.95), 0.07, WOOD)
        vki_dpr_rod(k, (x + 0.25, 0.25, -0.02), (x - 0.12, -0.10, 0.95), 0.07, WOOD)
    vki_dpr_rod(k, (-0.75, 0.02, 0.62), (0.75, 0.02, 0.62), 0.08, WOOD)
    for i, x in enumerate((-0.60, -0.30, 0.0, 0.30, 0.60)):
        a = Vector((x, 0.45, 0.10)); b = Vector((x, -0.42, 1.05 + 0.05 * (i % 2)))
        d = (b - a).normalized()
        vki_dpr_rod(k, a, b - d * 0.20, 0.08, WOOD)
        rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        _cyl(k, tuple(b - d * 0.10), 0.045, 0.004, 0.22, 6, HEWN, rot=rot)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_lair_refuse(k):
    """camp refuse over ~1.1 x 0.8 m: gnawed long bones, a rib hoop, rags, a broken pot, rat droppings"""
    rnd = random.Random(33)
    for (a, b, r) in (((-0.45, -0.10), (-0.10, -0.25), 0.018), ((0.05, 0.20), (0.40, 0.05), 0.016),
                      ((-0.20, 0.25), (0.05, 0.32), 0.014)):
        vki_dun_bone(k, (a[0], a[1], r * 1.25), (b[0], b[1], r * 1.25 + 0.006), r=r, dark=0.3)
    vki_dpr_blob(k, (0.30, -0.22), (0.20, 0.13), 0.001, 0.012, BURLAP, ns=9, wob=0.25, seed=2)
    vki_dpr_blob(k, (-0.35, 0.28), (0.16, 0.11), 0.001, 0.010, CLOTH_A, ns=8, wob=0.25, seed=3)
    for i in range(8):
        c = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.35, 0.35), 0.008)
        v = _ico(k, c, 0.012, VOID, scale=(1.6, 0.9, 0.7), sub=0, seed=i)
        k.project(vki_faces_of(v), VOID)
    vki_dun_bone_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


# ---------------------------------------------------------------- spiders
def vki_lair_web_corner(k):
    """a web across a room corner: rot 0 = the corner of the walls at -X and +Y of the cell (NW), the card from the
    west wall's face to the north wall's face (3 cm off them), 0.2-2.6 m high; plus a smaller web lower down and three
    anchor strands to the floor"""
    w0, w1 = Vector((-0.47, -0.30, 0.0)), Vector((0.30, 0.47, 0.0))
    vki_lair_card(k, [w0 + Vector((0, 0, 0.25)), w1 + Vector((0, 0, 0.25)), w1 + Vector((0, 0, 2.6)),
                      w0 + Vector((0, 0, 2.6))])
    m0, m1 = Vector((-0.47, 0.05, 0.0)), Vector((-0.05, 0.47, 0.0))
    vki_lair_card(k, [m0 + Vector((0, 0, 0.05)), m1 + Vector((0, 0, 0.05)), m1 + Vector((0, 0, 1.0)),
                      m0 + Vector((0, 0, 1.0))], u=(0.15, 0.85), v=(0.15, 0.85))
    for (x, y) in ((-0.30, -0.45), (0.05, -0.20), (0.40, 0.10)):
        vki_dpr_rod(k, (x * 0.6, y * 0.6 + 0.2, 0.6), (x, y, 0.0), 0.012, VKI_WAX, d=0.004)
    vki_lair_web_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="none", vki_see_through=1, vki_wall_anchor=1,
                  vki_note="rot 0: the NW corner of its cell (walls at -X and +Y); rot -90: NE; 180: SE; 90: SW; "
                           "vki_wall_anchor: its card edges may enter a rough (cave) wall face -- T12 lets them")


def vki_lair_webfloor(k):
    """a silk sheet on the floor (1.3 m), and a second smaller one across it"""
    vki_lair_card(k, [(-0.65, -0.65, 0.010), (0.65, -0.65, 0.010), (0.65, 0.65, 0.010), (-0.65, 0.65, 0.010)], t=0.004)
    vki_lair_card(k, [(-0.20, -0.30, 0.020), (0.50, -0.45, 0.020), (0.62, 0.25, 0.020), (-0.08, 0.40, 0.020)], t=0.004,
                  u=(0.1, 0.9), v=(0.1, 0.9))
    vki_lair_web_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none", vki_see_through=1)


def vki_lair_eggsacs(k):
    """a clutch of seven pale egg sacs (ovoids 0.18-0.30) on a silk pad, bound by strands"""
    rnd = random.Random(21)
    pts = [(0.0, 0.0), (0.24, 0.10), (-0.22, 0.12), (0.10, -0.22), (-0.14, -0.18), (0.30, -0.14), (-0.30, -0.06)]
    for i, (x, y) in enumerate(pts):
        r = rnd.uniform(0.09, 0.15)
        v = vki_home_ico(k, (x, y, r * 1.1), r, VKI_WAX, scale=(1.0, 0.9, 1.25), sub=2, jit=0.006, seed=i, rest=0.0)
        k.project(vki_faces_of(v), VKI_WAX)
        k.set_dark(v, rnd.uniform(0.0, 0.15))
    vki_lair_card(k, [(-0.55, -0.45, 0.006), (0.55, -0.45, 0.006), (0.55, 0.45, 0.006), (-0.55, 0.45, 0.006)], t=0.004)
    for (a, b) in (((-0.40, 0.30, 0.0), (0.0, 0.0, 0.30)), ((0.45, 0.25, 0.0), (0.24, 0.10, 0.25)),
                   ((0.40, -0.35, 0.0), (0.10, -0.22, 0.22))):
        vki_dpr_rod(k, a, b, 0.010, VKI_WAX, d=0.004)
    vki_lair_web_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_lair_cocoon(k):
    """a victim wrapped in silk (1.7 m), leaning back against the wall (wall_floor, back at local y ~0.3): a lumpy
    wrapped body, bands of thicker silk, strands to the wall"""
    before = set(k.bm.verts)
    v = vki_home_ico(k, (0.0, 0.0, 0.85), 0.26, VKI_WAX, scale=(0.95, 0.85, 3.3), sub=2, jit=0.02, seed=3)
    k.project(vki_faces_of(v), VKI_WAX)
    for i, z in enumerate((0.35, 0.70, 1.05, 1.40)):
        r = 0.26 * (1.0 - ((z - 0.85) / 0.86) ** 2) ** 0.5 * 0.95 + 0.012
        vki_home_hoop(k, (0.0, 0.0, z), r - 0.02, r, 0.05, segs=12, mi=VKI_WAX, sx=0.95, sy=0.85,
                      rot=Matrix.Rotation(0.15 * (i % 2 - 0.5), 3, "Y"))
    body = [vv for vv in k.bm.verts if vv not in before]
    bmesh.ops.transform(k.bm, verts=body, matrix=Matrix.Translation((0.0, 0.05, 0.0)) @ Matrix.Rotation(math.radians(-10), 4, "X"))
    for (x, z) in ((-0.15, 1.5), (0.18, 1.2), (0.0, 0.5)):
        vki_dpr_rod(k, (x, 0.05, z), (x * 1.6, 0.32, z + 0.1), 0.012, VKI_WAX, d=0.005)
    k.set_dark(body, 0.05)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[], vki_nav="block", vki_wall_anchor=1)


# ---------------------------------------------------------------- rats
def vki_lair_burrow(k):
    """a giant rat's burrow: a mound of earth (the FLOOR slot, EarthDamp by default) with a dark hole in its south
    face, clods scattered round it"""
    vki_dpr_mound(k, (0.0, 0.05, 0.0), 0.60, 0.50, 0.40, VKI_FLOOR, z0=0.001, nr=3, ns=14, seed=31, wob=0.15, bump=0.15)
    hv = vki_dpr_blob(k, (0.0, 0.0), (0.21, 0.16), -0.02, 0.02, VOID, ns=12, wob=0.1, seed=7)
    bmesh.ops.transform(k.bm, verts=hv, matrix=Matrix.Translation((0.0, -0.36, 0.20)) @ Matrix.Rotation(math.radians(65), 4, "X"))
    rnd = random.Random(8)
    for i in range(7):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.62, 0.72)
        c = _ico(k, (math.cos(a) * d, math.sin(a) * d * 0.9, 0.025), rnd.uniform(0.03, 0.05), VKI_FLOOR,
                 scale=(1, 0.8, 0.6), sub=0, jit=0.008, seed=60 + i)
        k.project(vki_faces_of(c), VKI_FLOOR)
    k.slot_mats[VKI_FLOOR] = "EarthDamp"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_lair_rathole(k):
    """a gnawed hole at the foot of a wall (wall_floor, back at y 0): a dark arch 0.40 wide on the wall face, broken
    stone and gnawed crumbs in front"""
    hv = vki_dpr_blob(k, (0.0, 0.0), (0.20, 0.17), 0.0, 0.012, VOID, ns=12, wob=0.12, seed=3)   # -> y -0.012..0
    bmesh.ops.transform(k.bm, verts=hv, matrix=Matrix.Translation((0.0, 0.0, 0.10)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    for v in hv:
        v.co.z = max(v.co.z, -0.004)
    rnd = random.Random(5)
    for i in range(6):
        c = (rnd.uniform(-0.28, 0.28), rnd.uniform(-0.30, -0.08), 0.02)
        v = _ico(k, c, rnd.uniform(0.025, 0.045), VKI_STONE_BLOCK_IN, scale=(1, 0.8, 0.6), sub=0, jit=0.006, seed=80 + i)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    for i in range(8):
        c = (rnd.uniform(-0.35, 0.35), rnd.uniform(-0.40, -0.10), 0.006)
        v = _ico(k, c, 0.010, VOID, scale=(1.6, 0.9, 0.7), sub=0, seed=90 + i)
        k.project(vki_faces_of(v), VOID)
    vki_dpr_block_mats(k)
    vki_home_meta(k, "wall_floor", "dressing", back=0.0, use=[], vki_nav="none", vki_wall_anchor=1)


# ---------------------------------------------------------------- specs
VKI_LAIR_SPECS = [
    ("SM_VKI_Overlay_Bedroll", vki_lair_bedroll, "none"),
    ("SM_VKI_Prop_FirePit_Camp", vki_lair_firepit, "prop"),
    ("SM_VKI_Prop_Totem_Goblin", vki_lair_totem, "prop"),
    ("SM_VKI_Prop_LeanTo", vki_lair_leanto, "prop"),
    ("SM_VKI_Prop_Barricade_Stakes", vki_lair_barricade, "prop"),
    ("SM_VKI_Overlay_Refuse", vki_lair_refuse, "none"),
    ("SM_VKI_Prop_Web_Corner", vki_lair_web_corner, "none"),
    ("SM_VKI_Overlay_WebFloor", vki_lair_webfloor, "none"),
    ("SM_VKI_Prop_EggSacs", vki_lair_eggsacs, "prop"),
    ("SM_VKI_Prop_Cocoon", vki_lair_cocoon, "prop"),
    ("SM_VKI_Prop_Burrow", vki_lair_burrow, "prop"),
    ("SM_VKI_Prop_RatHole_Wall", vki_lair_rathole, "prop"),
]
VKI_LAIR_NAMES = [n for n, _, _ in VKI_LAIR_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_LAIR_SPECS])
