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
#   warcamp (outdoors, goblin-built: crooked bark poles, patched dark hides, skulls; door / front -Y):
#            Prop_Goblin_Watchtower (stakes on a platform at 4.2, astride a palisade), Prop_Goblin_Tent (A-frame),
#            Prop_Goblin_ChiefTent (a tusk-gated tipi), Prop_Goblin_Bonfire (light), Prop_Goblin_Gate (the doors of the
#            exterior Palisade_Gate frame, barred inside: vki_breakable) and Prop_Goblin_Gate_Broken (its smashed state)
# Build: g["vki_ws_build"]("adventure", VKI_LAIR_NAMES); test: g["vki_test_pieces"](VKI_LAIR_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_LAIR_FIRE_W = 200.0
VKI_LAIR_HIDE_T = 2.0               # T_VKI_Hide's tile (M_VKI_Hide on the goblin pieces' HIDE slot)


def vki_lair_web_mats(k):
    k.slot_mats[VKI_FX] = "M_VKI_Web"


def vki_lair_hide_mats(k):
    """goblin hides: the textured sewn hide (M_VKI_Hide) on the HIDE slot, not the exterior's flat M_VK_Hide"""
    k.slot_mats[HIDE] = "M_VKI_Hide"


def vki_lair_hide_uv(k, vs):
    """box-project the HIDE faces among vs at T_VKI_Hide's tile"""
    k.project([f for f in vki_faces_of(vs) if f.material_index == HIDE], HIDE, tile=VKI_LAIR_HIDE_T)


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
    hv = vki_dpr_blob(k, (0.0, 0.0), (0.68, 0.36), 0.001, 0.022, HIDE, ns=14, wob=0.12, seed=4)
    vki_lair_hide_uv(k, hv)
    k.set_dark(hv, 0.2)                                          # a worn, dirty hide
    rv = _cyl(k, (-0.52, 0.0, 0.07), 0.07, 0.07, 0.55, 10, BURLAP, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    for f in vki_faces_of(rv):
        f.smooth = True
    k.set_dark(rv, 0.15)
    vki_dpr_mound(k, (0.40, 0.18, 0.02), 0.22, 0.14, 0.05, VKI_STRAW, z0=0.018, nr=2, ns=8, seed=5)
    vki_lair_hide_mats(k)
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
    k.box((0.0, -0.01, 1.42), (0.34, 0.012, 0.52), HIDE, bevel=0.0, tile=VKI_LAIR_HIDE_T)    # banner
    bv = [v for v in k.bm.verts if v not in before]
    for v in bv:
        if v.co.z < 1.3:
            v.co.x *= 0.7
    for (x, z) in ((0.0, 1.35), (0.0, 1.25)):
        k.box((x, -0.02, z + 0.1), (0.14, 0.012, 0.02), VOID, bevel=0.0)          # painted marks
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
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
        vki_lair_hide_uv(k, vs)
        k.set_dark(vs, 0.1 * i)
    vki_lair_hide_uv(k, vki_dpr_blob(k, (0.0, 0.05), (0.62, 0.30), 0.001, 0.02, HIDE, ns=12, wob=0.12, seed=8))
    k.slot_mats[WOOD] = "Dark"
    vki_lair_hide_mats(k)
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


# ---------------------------------------------------------------- warcamp (outdoors)
def vki_lair_slab(k, pts, mi, t=0.02, dark=0.0):
    """a thin closed plate over the polygon pts (3-D, in order round it), thickness t along its normal, box-projected
    UVs: hide panels, flaps, rags, painted marks. Returns its verts."""
    P = [Vector(c) for c in pts]
    n = (P[1] - P[0]).cross(P[-1] - P[0]).normalized()
    A = [k.bm.verts.new(c - n * t / 2) for c in P]
    B = [k.bm.verts.new(c + n * t / 2) for c in P]
    fs = [k.bm.faces.new(A[::-1]), k.bm.faces.new(B)]
    for i in range(len(P)):
        j = (i + 1) % len(P)
        fs.append(k.bm.faces.new((A[i], A[j], B[j], B[i])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.smooth = False
    k.project(fs, mi, tile=VKI_LAIR_HIDE_T if mi == HIDE else None)
    if dark:
        k.set_dark(A + B, dark)
    return A + B


def vki_lair_hide(k, corners, dark=0.25, seed=0, nu=3, nv=3, t=0.02, sagv=None, ragged=0.0, mottle=0.06, edge=0.12,
                  mi=HIDE):
    """a hide stretched over the quad `corners` (3-D, in order: u runs 0 -> 1, v runs 0 -> 3): a closed plate split
    nu x nv, sagging by the vector sagv in the middle, its far edge (v = 1) ragged along v, its tone a little mottled
    (vertex darkness dark +- mottle, + edge at the rim; the sewn pieces themselves are T_VKI_Hide's); UVs projected
    at the texture's tile. Returns its verts."""
    rnd = random.Random(seed)
    C = [Vector(c) for c in corners]
    nrm = (C[1] - C[0]).cross(C[3] - C[0]).normalized()
    at = lambda u, v: C[0].lerp(C[1], u).lerp(C[3].lerp(C[2], u), v)
    sagv = Vector(sagv) if sagv is not None else Vector((0.0, 0.0, 0.0))
    A, B, D = [], [], []
    for j in range(nv + 1):
        ra, rb, rd = [], [], []
        for i in range(nu + 1):
            u, v = i / nu, j / nv
            q = at(u, v) + sagv * (math.sin(math.pi * u) * math.sin(math.pi * v))
            if j == nv and ragged:
                q += (at(u, 1.0) - at(u, 0.0)).normalized() * rnd.uniform(-ragged, ragged)
            ra.append(k.bm.verts.new(q - nrm * t / 2)); rb.append(k.bm.verts.new(q + nrm * t / 2))
            rim = i in (0, nu) or j in (0, nv)
            rd.append(min(0.95, max(0.0, dark + rnd.uniform(-mottle, mottle) + (edge if rim else 0.0))))
        A.append(ra); B.append(rb); D.append(rd)
    fs, rims = [], []
    for j in range(nv):
        for i in range(nu):
            fs.append(k.bm.faces.new((A[j][i], A[j + 1][i], A[j + 1][i + 1], A[j][i + 1])))
            fs.append(k.bm.faces.new((B[j][i], B[j][i + 1], B[j + 1][i + 1], B[j + 1][i])))
    ring = ([(0, i) for i in range(nu)] + [(j, nu) for j in range(nv)] + [(nv, i) for i in range(nu, 0, -1)]
            + [(j, 0) for j in range(nv, 0, -1)])
    for a, b in zip(ring, ring[1:] + ring[:1]):
        rims.append(k.bm.faces.new((A[a[0]][a[1]], A[b[0]][b[1]], B[b[0]][b[1]], B[a[0]][a[1]])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs + rims)
    for f in fs:
        f.smooth = True
    for f in rims:
        f.smooth = False
    k.project(fs + rims, mi, tile=VKI_LAIR_HIDE_T if mi == HIDE else None)
    for j in range(nv + 1):
        for i in range(nu + 1):
            k.set_dark([A[j][i], B[j][i]], D[j][i])
    return [v for row in A + B for v in row]


def vki_lair_log(k, a, b, r, seed, segs=6, tip=0.0, dark=0.0, bend=0.04, ts=(0.0, 0.5, 1.0), mi=BARK_OAK):
    """a crooked bark pole a -> b (def_log, both ends shut), a hewn point of length `tip` past b; returns its verts"""
    before = set(k.bm.verts)
    def_log(k, a, b, r, segs=segs, mi=mi, tip=tip, bot_cap=True, seed=seed, bend=bend, ts=ts, taper=0.9)
    vs = [v for v in k.bm.verts if v not in before]
    if dark:
        k.set_dark(vs, dark)
    return vs


def vki_lair_stone(k, c, r, seed, dark=0.2, sub=0):
    v = _ico(k, c, r, VKI_STONE_BLOCK_IN, scale=(1.2, 0.95, 0.7), sub=sub, jit=0.02 * r / 0.1, seed=seed)
    k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    k.set_dark(v, dark)
    return v


def vki_lair_watchtower(k):
    """a goblin watchtower (3.2 x 3.8 m, 7 m with its rag): four crooked bark legs splayed to the ground, lashed X
    braces, a platform of uneven planks (top 4.18) on bearer logs, a parapet of sharpened stakes with skulls on three,
    a gap at the back (+Y) where the ladder comes up, a lopsided awning of patched hides over the back half on the
    taller back legs, a red rag on a pole. Stands astride a palisade, its front (-Y) outward."""
    rnd = random.Random(61)
    zp = 4.18
    legs = {}
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        a = Vector((sx * 1.38, sy * 1.30, -0.35))
        b = Vector((sx * 1.02, sy * 0.98, 6.2 if sy > 0 else 5.45))                 # back tops under the awning
        legs[sx, sy] = (a, b)
        vki_lair_log(k, a, b, 0.14, 300 + i, segs=7, bend=0.05, ts=(0.0, 0.3, 0.65, 1.0), dark=0.1)
        for j in range(2):
            ang = rnd.uniform(0, 2 * math.pi)
            vki_lair_stone(k, (a.x + math.cos(ang) * 0.22, a.y + math.sin(ang) * 0.22, 0.05), rnd.uniform(0.13, 0.18),
                           310 + 2 * i + j)

    def on(leg, z, out):
        a, b = legs[leg]
        return a + (b - a) * ((z - a.z) / (b.z - a.z)) + Vector(out)

    sides = [((-1, -1), (1, -1), (0.0, -1.0, 0.0)), ((1, -1), (1, 1), (1.0, 0.0, 0.0)), ((-1, 1), (-1, -1), (-1.0, 0.0, 0.0))]
    for i, (l0, l1, o) in enumerate(sides):                                        # X braces
        o1 = Vector(o) * 0.13; o2 = Vector(o) * 0.24
        vki_lair_log(k, on(l0, 0.35, o1), on(l1, 3.75, o1), 0.065, 320 + 2 * i, segs=5, ts=(0.0, 1.0), bend=0.03)
        vki_lair_log(k, on(l1, 0.35, o2), on(l0, 3.75, o2), 0.065, 321 + 2 * i, segs=5, ts=(0.0, 1.0), bend=0.03)
    vki_lair_log(k, on((-1, 1), 0.35, (0, 0.13, 0)), on((1, 1), 3.75, (0, 0.13, 0)), 0.065, 327, segs=5,
                 ts=(0.0, 1.0), bend=0.03)
    for leg in legs:                                                              # lashings at the platform
        a, b = legs[leg]
        def_band(k, tuple(on(leg, 4.0, (0, 0, 0))), 0.165, 0.16, BURLAP, 8, axis=tuple(b - a))
    for i, y in enumerate((-1.29, 1.31)):                                         # bearers
        vki_lair_log(k, (-1.75, y, 4.0), (1.75, y + 0.02, 3.97), 0.11, 330 + i, segs=7)
    for i, x in enumerate((-1.34, 1.34)):
        vki_lair_log(k, (x, -1.62, 4.02), (x + 0.02, 1.62, 4.0), 0.09, 332 + i, segs=6)
    w = 0.256
    for i in range(10):                                                           # planks along Y
        x = -1.28 + w * (i + 0.5)
        L = 2.70 + rnd.uniform(-0.10, 0.04) if i != 6 else 1.85
        y = rnd.uniform(-0.04, 0.04) + (0.40 if i == 6 else 0.0)
        before = set(k.bm.verts)
        k.box((x, y, zp - 0.035), (w - 0.025, L, 0.07), PLANKS,
              rot=(rnd.uniform(-0.012, 0.012), rnd.uniform(-0.015, 0.015), rnd.uniform(-0.025, 0.025)), bevel=0.012)
        k.set_dark([v for v in k.bm.verts if v not in before], rnd.uniform(0.05, 0.35))
    skulls = {3: 0, 8: 1, 13: 2}
    rows = [[(x, -1.47, (0, -1)) for x in [-1.42 + 2.84 * i / 16 for i in range(17)]],
            [(-1.51, y, (-1, 0)) for y in [-1.28 + 2.56 * i / 14 for i in range(15)]],
            [(1.51, y, (1, 0)) for y in [-1.28 + 2.56 * i / 14 for i in range(15)]],
            [(x, 1.51, (0, 1)) for x in (-1.42, -1.22, -1.02, -0.82, -0.62, 0.62, 0.82, 1.02, 1.22, 1.42)]]
    n = 0
    for r_, row in enumerate(rows):                                               # the parapet
        for j, (x, y, (ox, oy)) in enumerate(row):
            n += 1
            sk = r_ == 0 and j in skulls
            top = 5.08 + rnd.uniform(-0.12, 0.18)
            tip = 0.0 if sk or rnd.random() < 0.12 else rnd.uniform(0.16, 0.22)
            lean = rnd.uniform(0.04, 0.10)
            vki_lair_log(k, (x, y, 3.72), (x + ox * lean, y + oy * lean, top), rnd.uniform(0.05, 0.065), 340 + n,
                         segs=5, tip=tip, ts=(0.0, 1.0), bend=0.02, dark=rnd.uniform(0.0, 0.25))
            if sk:
                vki_dun_skull(k, (x + ox * lean, y + oy * lean - 0.02, top + 0.10), s=1.35,
                              yaw=rnd.uniform(-15, 15), pitch=rnd.uniform(-12, 4), dark=0.15)
    for i, (a, b) in enumerate((((-1.62, -1.58, 4.55), (1.62, -1.57, 4.62)), ((-1.62, -1.6, 4.58), (-1.62, 1.6, 4.52)),
                                ((1.62, -1.6, 4.6), (1.62, 1.6, 4.55)), ((-1.6, 1.62, 4.56), (-0.5, 1.62, 4.6)),
                                ((0.5, 1.62, 4.58), (1.6, 1.62, 4.55)))):
        vki_lair_log(k, a, b, 0.05, 420 + i, segs=5, ts=(0.0, 1.0), bend=0.02)       # rails lashing the stakes
    # awning: a back cross bar on the back legs' tops, a front bar on two sticks, three hides over them
    vki_lair_log(k, (-1.35, 1.0, 6.2), (1.35, 1.0, 6.16), 0.07, 430, segs=6)
    for i, x in enumerate((-1.0, 1.0)):
        vki_lair_log(k, (x, -0.40, zp - 0.05), (x * 1.02, -0.42, 5.62), 0.05, 431 + i, segs=5, ts=(0.0, 1.0))
    vki_lair_log(k, (-1.35, -0.42, 5.6), (1.35, -0.42, 5.55), 0.055, 433, segs=6)
    sl = (6.25 - 5.63) / 1.42
    nrm = Vector((0.0, -sl, 1.0)).normalized()
    zat = lambda y: 5.66 + (y + 0.42) * sl
    for i, ((x0, x1), d) in enumerate((((-1.45, -0.52), 0.30), ((-0.55, 0.40), 0.15), ((0.37, 1.42), 0.38))):
        y0, y1 = -0.70 + rnd.uniform(-0.12, 0.08), -0.70 + rnd.uniform(-0.12, 0.08)
        off = nrm * (0.06 + 0.012 * i)
        yb = 1.30 + 0.03 * i
        c = [Vector((x0, yb, zat(yb))), Vector((x1, yb, zat(yb))), Vector((x1, y1, zat(y1))), Vector((x0, y0, zat(y0)))]
        vki_lair_hide(k, [p + off for p in c], dark=d, seed=460 + i, nu=3, nv=3, sagv=(0.0, 0.0, -0.10), ragged=0.08)
    # a red rag on a pole lashed to the front-left leg; a skull on the front-right leg
    vki_lair_log(k, (-1.20, -1.15, 4.4), (-1.17, -1.12, 7.0), 0.04, 440, segs=5, ts=(0.0, 1.0))
    vki_lair_slab(k, [(-1.21, -1.13, 6.92), (-2.05, -1.13, 6.82), (-1.80, -1.13, 6.58), (-2.0, -1.13, 6.32),
                      (-1.21, -1.13, 6.42)], CLOTH_A, t=0.012, dark=0.2)
    vki_dun_skull(k, (1.02, -1.02, 5.55), s=1.3, yaw=-10, pitch=-8)
    # the ladder up the back
    for i, x in enumerate((-0.30, 0.30)):
        vki_lair_log(k, (x, 2.25, -0.2), (x * 1.03, 1.42, 4.75), 0.045, 450 + i, segs=5, ts=(0.0, 1.0), bend=0.02)
    for i in range(11):
        z = 0.35 + 0.4 * i
        y = 2.25 - 0.83 * (z + 0.2) / 4.95
        _cyl(k, (rnd.uniform(-0.02, 0.02), y + 0.05, z), 0.025, 0.025, 0.74, 6, WOOD,
             rot=Matrix.Rotation(math.pi / 2, 4, "Y") @ Matrix.Rotation(rnd.uniform(-0.05, 0.05), 4, "X"))
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    cols = [[round(sx * 1.24, 3), round(sy * 1.18, 3), 1.8, 0.45, 0.45, 3.6] for sx in (-1, 1) for sy in (-1, 1)]
    cols += [[0.0, 0.0, zp - 0.1, 3.0, 2.9, 0.2],                                  # the floor, archers stand on it
             [0.0, -1.5, zp + 0.5, 3.1, 0.15, 1.0], [-1.53, 0.0, zp + 0.5, 0.15, 3.0, 1.0],
             [1.53, 0.0, zp + 0.5, 0.15, 3.0, 1.0], [-0.98, 1.53, zp + 0.5, 1.1, 0.15, 1.0],
             [0.98, 1.53, zp + 0.5, 1.1, 0.15, 1.0]]                              # the parapet, open at the ladder
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block", vki_collider=cols,
                  vki_note="front (-Y) outward: stand it astride a palisade, the ladder (+Y) inside; platform top 4.18")


def vki_lair_goblin_tent(k):
    """a goblin hide tent (2.7 x 3.1, 2.3 m): crossed pole pairs front and back under a ridge pole, two slopes of
    patched dark hides weighed down with stones, the back closed, the front half-open with one flap tied back over the
    slope, a skull and a bone at the front crossing, a hide to sleep on inside; door -Y"""
    rnd = random.Random(71)
    H, W, Y = 1.88, 1.28, 1.25
    for i, y in enumerate((-Y, Y)):
        for s in (-1.0, 1.0):
            a = Vector((s * W, y + s * 0.03, -0.12)); c = Vector((0.0, y, H))
            vki_lair_log(k, a, a + (c - a) * 1.24, 0.05, 400 + 2 * i + (s > 0), segs=5, bend=0.03)
    vki_lair_log(k, (0.02, -1.55, H + 0.04), (-0.02, 1.52, H + 0.03), 0.045, 410, segs=5)
    for si, s in enumerate((-1.0, 1.0)):                                          # the slopes
        ridge = Vector((0.0, 0.0, H + 0.10)); hem = Vector((s * (W + 0.07), 0.0, 0.0))
        nrm = Vector((s * (H + 0.10), 0.0, W + 0.07)).normalized()
        P = lambda y, t: ridge + (hem - ridge) * t + Vector((0.0, y, 0.0))
        cuts = [-1.36 - 0.02 * si, -0.42 + rnd.uniform(-0.1, 0.1), 0.46 + rnd.uniform(-0.1, 0.1), 1.37 + 0.02 * si]
        darks = [0.28, 0.15, 0.35] if s < 0 else [0.22, 0.38, 0.25]
        for i in range(3):
            y0, y1 = cuts[i] - (0.02 if i else 0.0), cuts[i + 1]
            off = nrm * (0.005 + 0.008 * i)
            c = [P(y0, -0.015 * i), P(y1, -0.015 * i), P(y1, 0.97), P(y0, 0.97)]
            vki_lair_hide(k, [p + off for p in c], dark=darks[i], seed=470 + 3 * si + i, nu=3, nv=3, sagv=-nrm * 0.05,
                          ragged=0.04)
        y0 = (0.15 if si == 0 else -0.85) + rnd.uniform(0.0, 0.35); t0 = rnd.uniform(0.3, 0.5)  # a patch sewn
        dy, dt = rnd.uniform(0.35, 0.45), rnd.uniform(0.2, 0.28)                    # on, clear of the flap
        c = [P(y0, t0), P(y0 + dy, t0 + 0.02), P(y0 + dy - 0.03, t0 + dt), P(y0 + 0.02, t0 + dt - 0.03)]
        vki_lair_slab(k, [p + nrm * 0.032 for p in c], BURLAP if si == 0 else HIDE, t=0.012, dark=0.35 if si == 0 else 0.45)
        for j in range(4):                                                        # stones on the hem
            vki_lair_stone(k, (s * (W + 0.14), -1.05 + 0.7 * j + rnd.uniform(-0.15, 0.15), 0.05),
                           rnd.uniform(0.08, 0.11), 412 + 4 * si + j, dark=rnd.uniform(0.1, 0.4))
    vki_lair_slab(k, [(-W - 0.04, 1.33, 0.01), (W + 0.04, 1.33, 0.01), (0.0, 1.33, H + 0.08)], HIDE, dark=0.3)
    vki_lair_slab(k, [(0.0, -1.33, H + 0.08), (0.25, -1.33, 0.01), (W + 0.04, -1.33, 0.01)], HIDE, dark=0.25)
    nl = Vector((-(H + 0.10), 0.0, W + 0.07)).normalized()                        # the flap, tied back over the slope
    tipv = Vector((0.0, 0.0, H + 0.10)) + (Vector((-(W + 0.07), 0.0, 0.0)) - Vector((0.0, 0.0, H + 0.10))) * 0.6
    vki_lair_slab(k, [(0.0, -1.39, H + 0.06), (-W - 0.05, -1.39, 0.01), tuple(tipv + Vector((0.0, -0.75, 0.0)) + nl * 0.06)],
                  HIDE, t=0.015, dark=0.35)
    vki_lair_slab(k, [(-W * 0.8, 0.55, 0.01), (W * 0.8, 0.55, 0.01), (0.0, 0.55, H * 0.82)], VOID, t=0.01)
    hv = set(k.bm.verts)
    vki_dpr_blob(k, (-0.35, -0.15), (0.40, 0.62), 0.001, 0.022, HIDE, ns=10, wob=0.12, seed=12)
    hv = [v for v in k.bm.verts if v not in hv]
    vki_lair_hide_uv(k, hv)
    k.set_dark(hv, 0.3)
    vki_dun_skull(k, (0.0, -1.40, H + 0.02), s=1.0, pitch=8)
    vki_dun_bone(k, (0.02, -1.42, H - 0.12), (0.05, -1.43, H - 0.42), r=0.013, dark=0.2)
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[[-0.35, -1.9, 0]], vki_nav="block",
                  vki_note="door -Y: face it toward the camp's fire")


def vki_lair_chief_tent(k):
    """the warband chieftain's tent (5.3 x 6.0 m, 5 m): nine crooked poles round a 2.45 m circle crossing at 4.15 and
    splaying above, a cone of patched hide panels in two bands (sooted toward the smoke hole, a red painted band), the
    door at -Y with its two flaps pinned aside and darkness inside, two great tusks arching before it, a skull on a
    stake, a hide banner, a fur on the ground; stones weigh down the hem"""
    rnd = random.Random(83)
    R, AP = 2.45, 4.15
    ang = [math.radians(-70 + 40 * i) for i in range(9)]                          # the door between -110 and -70
    rad = lambda z: 0.06 + (R - 0.06) * (AP - z) / (AP + 0.1)
    for i, a in enumerate(ang):
        b0 = Vector((math.cos(a) * R, math.sin(a) * R, -0.1))
        c = Vector((math.cos(a) * 0.06, math.sin(a) * 0.06, AP))
        vki_lair_log(k, b0, b0 + (c - b0) * rnd.uniform(1.16, 1.24), 0.075, 500 + i, segs=6, bend=0.04, dark=0.15)
    P = lambda a, z, off: Vector((math.cos(a) * (rad(z) + off), math.sin(a) * (rad(z) + off), z))
    for band, (z0, z1, off) in enumerate(((0.02, 2.05, 0.08), (1.95, 3.75, 0.095))):
        for j in range(9):
            a0 = ang[j]; a1 = ang[j + 1] if j < 8 else ang[0] + 2 * math.pi
            if j == 8 and band == 0:
                continue                                                          # the doorway
            am = (a0 + a1) / 2
            vs = vki_lair_hide(k, [P(a0, z0, off), P(a1, z0, off), P(a1, z1, off), P(a0, z1, off)],
                               dark=rnd.uniform(0.12, 0.35), seed=560 + 9 * band + j, nu=2, nv=3, t=0.025,
                               sagv=Vector((-math.cos(am), -math.sin(am), 0.0)) * 0.07 if band else None,
                               ragged=0.0 if band else 0.03)
            if band:
                k.set_dark([v for v in vs if v.co.z > 3.2], 0.6)                  # soot round the smoke hole
            elif j != 8:
                vki_lair_slab(k, [P(a0, 1.25, off + 0.02), P(a1, 1.25, off + 0.02), P(a1, 1.45, off + 0.02),
                                  P(a0, 1.45, off + 0.02)], CLOTH_A, t=0.01, dark=0.25)
    for a, d in ((ang[8], -1), (ang[0], 1)):                                       # the flaps, pinned aside
        vki_lair_slab(k, [P(a, 1.95, 0.12), P(a, 0.02, 0.12), P(a + d * math.radians(25), 0.35, 0.13)], HIDE,
                      t=0.018, dark=0.35)
    vki_lair_slab(k, [(-1.6, -0.7, 0.01), (1.6, -0.7, 0.01), (0.9, -0.7, 2.1), (-0.9, -0.7, 2.1)], VOID, t=0.01)
    hv = set(k.bm.verts)
    vki_dpr_blob(k, (0.0, -1.3), (1.0, 0.9), 0.0005, 0.008, VOID, ns=12, wob=0.1, seed=3)
    for s in (-1.0, 1.0):                                                         # the tusks
        P0 = Vector((s * 1.05, -2.85, -0.15)); C = Vector((s * 1.55, -3.05, 1.7)); P1 = Vector((s * 0.32, -2.75, 2.75))
        q = lambda t: P0 * (1 - t) ** 2 + C * (2 * (1 - t) * t) + P1 * t * t
        for i in range(6):
            t0, t1 = i / 6, (i + 1) / 6
            a, b = q(t0), q(t1); d = (b - a).normalized()
            _cyl(k, tuple((a + b) / 2), 0.14 * (1 - t0) + 0.025 * t0, 0.14 * (1 - t1) + 0.025 * t1, (b - a).length + 0.03,
                 8, VKI_WAX, rot=Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4())
        def_band(k, tuple(q(0.18)), 0.14, 0.10, BURLAP, 8, axis=tuple(q(0.22) - q(0.14)))
        for j in range(2):
            vki_lair_stone(k, (s * (1.05 + 0.25 * (j * 2 - 1)), -2.85 + rnd.uniform(-0.2, 0.2), 0.06),
                           rnd.uniform(0.12, 0.16), 530 + j + (s > 0) * 2, dark=0.25)
    vki_lair_log(k, (1.85, -2.55, -0.2), (1.83, -2.57, 1.95), 0.05, 520, segs=5, ts=(0.0, 1.0))
    vki_dun_skull(k, (1.83, -2.60, 2.05), s=1.3, pitch=-5, dark=0.1)
    vki_lair_log(k, (-1.95, -2.35, -0.25), (-1.92, -2.38, 3.5), 0.05, 521, segs=5, tip=0.25, ts=(0.0, 1.0))
    vki_dpr_rod(k, (-2.35, -2.40, 3.25), (-1.50, -2.40, 3.22), 0.045, WOOD)
    vki_lair_slab(k, [(-2.30, -2.44, 3.20), (-1.55, -2.44, 3.18), (-1.62, -2.44, 2.05), (-1.95, -2.44, 1.85),
                      (-2.25, -2.44, 2.10)], HIDE, t=0.015, dark=0.3)
    vki_lair_slab(k, [(-2.10, -2.47, 2.85), (-1.75, -2.47, 2.85), (-1.92, -2.47, 2.45)], CLOTH_A, t=0.01, dark=0.2)
    hv = set(k.bm.verts)
    vki_dpr_blob(k, (0.0, -3.05), (0.75, 0.45), 0.001, 0.025, HIDE, ns=12, wob=0.15, seed=22)
    hv = [v for v in k.bm.verts if v not in hv]
    vki_lair_hide_uv(k, hv)
    k.set_dark(hv, 0.3)
    for i in range(16):                                                           # stones on the hem
        a = math.radians(-60 + 300 * (i + rnd.uniform(-0.3, 0.3)) / 15.0)
        r0 = rad(0.0) + 0.2
        vki_lair_stone(k, (math.cos(a) * r0, math.sin(a) * r0, 0.06), rnd.uniform(0.12, 0.17), 540 + i,
                       dark=rnd.uniform(0.1, 0.4))
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "hero", use=[[0.0, -3.4, 0]], vki_nav="block",
                  vki_collider=[[0.0, 0.0, 1.6, 3.9, 3.9, 3.2], [-1.05, -2.85, 1.0, 0.4, 0.4, 2.0],
                                [1.05, -2.85, 1.0, 0.4, 0.4, 2.0], [1.85, -2.55, 1.0, 0.2, 0.2, 2.0],
                                [-1.95, -2.35, 1.6, 0.2, 0.2, 3.2]],
                  vki_note="door -Y between the tusks: face it toward the camp")


def vki_lair_bonfire(k):
    """the warcamp's bonfire (3.2 m across, flames 2.5 m): a ring of blackened stones round a bed of ash, a teepee of
    charred logs and two fallen in, tall flames and embers, firewood stacked beside it; light"""
    rnd = random.Random(91)
    for i in range(13):
        a = 2 * math.pi * i / 13 + rnd.uniform(-0.08, 0.08)
        s = rnd.uniform(0.15, 0.21)
        vki_lair_stone(k, (math.cos(a) * 1.38, math.sin(a) * 1.38, s * 0.42), s, 120 + i, dark=rnd.uniform(0.3, 0.6),
                       sub=1)
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 1.2, 1.2, 0.08, VKI_ASH, z0=0.001, nr=2, ns=14, seed=9)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.15, 0.15)
        vki_lair_log(k, (math.cos(a) * 0.95, math.sin(a) * 0.95, 0.04),
                     (math.cos(a + 0.4) * 0.10, math.sin(a + 0.4) * 0.10, 1.75 + rnd.uniform(-0.1, 0.1)),
                     rnd.uniform(0.08, 0.11), 600 + i, segs=6, dark=0.45)
    vki_lair_log(k, (-0.9, 0.3, 0.1), (0.2, 0.6, 0.13), 0.10, 610, segs=6, dark=0.6)
    vki_lair_log(k, (0.5, -0.8, 0.1), (0.9, 0.1, 0.12), 0.09, 611, segs=6, dark=0.6)
    vki_sto_flame(k, Vector((0.0, 0.0, 0.12)), 2.5, 0.45, 0.0, 0.3, 0.05, flat=0.85)
    for i in range(6):
        a = 2 * math.pi * i / 6 + 0.3
        vki_sto_flame(k, Vector((math.cos(a) * 0.38, math.sin(a) * 0.38, 0.12)), rnd.uniform(1.1, 1.7),
                      rnd.uniform(0.22, 0.30), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 3), rnd.uniform(-0.06, 0.06), flat=0.75)
    vki_sto_embers(k, 0.0, 0.0, 0.10, 10, 0.8, 0.8, 140, core=0.7, rmin=0.05, rmax=0.08, hmax=0.9)
    for i, (a, b, r) in enumerate((((1.95, -0.55, 0.11), (1.98, 0.55, 0.11), 0.11), ((2.20, -0.50, 0.11), (2.22, 0.60, 0.11), 0.10),
                                   ((2.08, -0.45, 0.30), (2.10, 0.50, 0.31), 0.10))):
        vki_lair_log(k, a, b, r, 620 + i, segs=6, bend=0.02)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_lights=[vki_dpr_light("campfire", (0.0, -0.3, 2.6), 3.5 * VKI_LAIR_FIRE_W, VKI_DPR_BRAZIER_COL,
                                            16.0, 0.6)],
                  vki_fx=[dict(fx="campfire", pos=[0.0, 0.0, 0.5], scale=2.6)],
                  vki_collider=[[0.0, 0.0, 0.8, 3.0, 3.0, 1.6], [2.08, 0.03, 0.25, 0.5, 1.2, 0.5]])


VKI_LAIR_GATE_TOPS = (3.40, 3.36, 3.30, 3.22, 2.95)   # a leaf's stake tops (with the point), centre -> post: under the
#                                                       Palisade_Gate frame's top rail (3.47) and knee braces


def vki_lair_gate_leaf(k, s, seed, broken=(), front=True):
    """one leaf of the goblin gate, s = -1 (left) / +1 (right), closed in place in the Palisade_Gate frame (posts at
    +-1.5): five crooked stakes from 0.13 to 1.13 off the centre, two rails and a brace lashed on the inside (+Y), a peg
    for the bar; `broken`: stakes snapped short (a splintered stub); front: a skull on its face (-Y), the left leaf a
    hide with a red mark. Returns its verts."""
    rnd = random.Random(seed)
    before = set(k.bm.verts)
    for i, top in enumerate(VKI_LAIR_GATE_TOPS):
        x = s * (0.13 + 0.25 * i)
        if i in broken:
            vki_lair_log(k, (x, -0.1, -0.05), (x + rnd.uniform(-0.02, 0.02), -0.1, rnd.uniform(1.4, 2.0)), 0.13, seed + i,
                         segs=7, tip=0.14, bend=0.01, dark=rnd.uniform(0.05, 0.2))
        else:
            vki_lair_log(k, (x, -0.1, -0.05), (x + rnd.uniform(-0.02, 0.02), -0.1 + rnd.uniform(-0.015, 0.015),
                                               top - rnd.uniform(0.0, 0.04) - 0.28), 0.13, seed + i, segs=7, tip=0.28,
                         bend=0.015, dark=rnd.uniform(0.05, 0.2))
    for j, z in enumerate((0.6, 2.35)):                                            # rails, lashed
        vki_lair_log(k, (s * 0.02, 0.1, z), (s * 1.25, 0.1, z + rnd.uniform(-0.04, 0.04)), 0.075, seed + 10 + j, segs=6,
                     ts=(0.0, 1.0), bend=0.02)
        for x in (0.38, 1.0):
            def_band(k, (s * x, 0.1, z), 0.09, 0.08, BURLAP, 6, axis=(1.0, 0.0, 0.0))
    vki_lair_log(k, (s * 0.15, 0.13, 0.75), (s * 1.12, 0.13, 2.2), 0.065, seed + 20, segs=5, ts=(0.0, 1.0))  # brace
    vki_lair_log(k, (s * 0.85, 0.22, 1.1), (s * 0.85, 0.22, 1.72), 0.045, seed + 21, segs=5, ts=(0.0, 1.0))   # bar peg
    if front:
        vki_dun_skull(k, (s * 0.62, -0.31, 2.85), s=1.3, yaw=rnd.uniform(-10, 10), pitch=-6, dark=0.1)
        if s < 0:
            vki_lair_hide(k, [(-1.15, -0.25, 1.05), (-0.2, -0.25, 1.1), (-0.25, -0.25, 2.25), (-1.1, -0.25, 2.2)], dark=0.3,
                          seed=seed + 30, nu=2, nv=2, t=0.015, ragged=0.05)
            vki_lair_slab(k, [(-0.85, -0.275, 1.85), (-0.45, -0.275, 1.88), (-0.66, -0.275, 1.45)], CLOTH_A, t=0.008,
                          dark=0.2)
    return [v for v in k.bm.verts if v not in before]


def vki_lair_gate_fill(k):
    """the slits between the Palisade_Gate frame's posts (+-1.5, r 0.225) and the palisade beside it (from +-2.06): two
    stakes each side lashed to the post, the same in both states of the gate"""
    rnd = random.Random(790)
    for s in (-1, 1):
        for j, x in enumerate((1.84, 2.0)):
            vki_lair_log(k, (s * x, 0.0, -0.3), (s * x + rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), 3.05 - 0.15 * j),
                         0.105, 791 + 2 * j + (s > 0), segs=7, tip=0.3, bend=0.015, dark=0.1)
        for z in (0.9, 2.5):
            vki_lair_log(k, (s * 1.62, -0.16, z), (s * 2.1, -0.15, z + 0.03), 0.04, 797 + int(z) + (s > 0), segs=5,
                         ts=(0.0, 1.0))


def vki_lair_gate(k):
    """the goblin gate (2.6 x 0.6, 3.4 m): two leaves of lashed, sharpened stakes closed in the exterior Palisade_Gate
    frame's opening, skulls and a marked hide on the face (-Y, outward), the bar across both leaves on the inside.
    Breakable: the game swaps in Prop_Goblin_Gate_Broken at the same transform. Its collider spans the frame's posts
    too (+-2.15): the frame has none, and the way past the posts would be open."""
    for s in (-1, 1):
        vki_lair_gate_leaf(k, s, 700 + 50 * (s > 0))
    vki_lair_gate_fill(k)
    vki_lair_log(k, (-1.18, 0.34, 1.47), (1.18, 0.34, 1.44), 0.11, 760, segs=7)               # the bar
    vki_dun_skull(k, (0.0, -0.33, 3.12), s=1.6, pitch=-8, dark=0.15)                         # over the join
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block", vki_breakable=1,
                  vki_broken="SM_VKI_Prop_Goblin_Gate_Broken", vki_collider=[[0.0, -0.05, 1.7, 4.3, 0.5, 3.4]],
                  vki_note="the doors of the Palisade_Gate frame (same transform; front -Y outward, barred inside): the "
                           "map's way in until the game breaks it (vki_broken: the piece to swap in)")


def vki_lair_gate_broken(k):
    """the goblin gate smashed in: the left leaf torn off and fallen into the camp (+Y) face up, the right leaf hanging
    open on its hinge with two stakes snapped, the bar broken in two, splinters and a skull on the ground. The way through
    is 1.9 m wide; colliders: the frame's posts and the hanging leaf."""
    rnd = random.Random(77)
    vs = vki_lair_gate_leaf(k, -1, 700)                                              # fallen in, face up
    piv = Vector((0.0, 0.1, 0.0))
    M = (Matrix.Translation((0.08, 0.15, 0.08)) @ Matrix.Translation((-0.65, 1.8, 0.0)) @ Matrix.Rotation(math.radians(12), 4, "Z")
         @ Matrix.Translation((0.65, -1.8, 0.0)) @ Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-86), 4, "X")
         @ Matrix.Translation(-piv))
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    vs = vki_lair_gate_leaf(k, 1, 750, broken=(1, 2), front=True)                    # hanging open, leaning in
    hp = Vector((1.27, -0.1, 0.0))
    M = (Matrix.Translation(hp) @ Matrix.Rotation(math.radians(-55), 4, "Z") @ Matrix.Rotation(math.radians(-4), 4, "X")
         @ Matrix.Translation(-hp))
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    vki_lair_log(k, (-0.95, 0.9, 0.11), (0.05, 1.2, 0.12), 0.11, 761, segs=7, tip=0.12)       # the bar, snapped
    vki_lair_log(k, (1.0, 2.35, 0.11), (0.3, 1.75, 0.1), 0.11, 762, segs=7, tip=0.12)
    for i in range(7):                                                                # splinters
        a = Vector((rnd.uniform(-1.3, 1.3), rnd.uniform(-1.1, 2.6), 0.04))
        d = Vector((math.cos(rnd.uniform(0, 6.3)), math.sin(rnd.uniform(0, 6.3)), 0.0)).normalized() * rnd.uniform(0.3, 0.6)
        vki_lair_log(k, a, a + d + Vector((0, 0, 0.01)), rnd.uniform(0.03, 0.05), 770 + i, segs=5, tip=0.08, ts=(0.0, 1.0))
    vki_dun_skull(k, (0.45, -0.7, 0.10), s=1.5, yaw=40, roll=25, dark=0.15)
    vki_lair_gate_fill(k)
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_collider=[[-1.75, -0.05, 1.7, 0.85, 0.5, 3.4], [1.75, -0.05, 1.7, 0.85, 0.5, 3.4],
                                [0.95, 0.37, 1.6, 0.75, 1.05, 3.2]],
                  vki_note="Prop_Goblin_Gate after the game breaks it (same transform)")


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
    ("SM_VKI_Prop_Goblin_Watchtower", vki_lair_watchtower, "prop"),
    ("SM_VKI_Prop_Goblin_Tent", vki_lair_goblin_tent, "prop"),
    ("SM_VKI_Prop_Goblin_ChiefTent", vki_lair_chief_tent, "prop"),
    ("SM_VKI_Prop_Goblin_Bonfire", vki_lair_bonfire, "prop"),
    ("SM_VKI_Prop_Goblin_Gate", vki_lair_gate, "prop"),
    ("SM_VKI_Prop_Goblin_Gate_Broken", vki_lair_gate_broken, "prop"),
]
VKI_LAIR_NAMES = [n for n, _, _ in VKI_LAIR_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_LAIR_SPECS])
