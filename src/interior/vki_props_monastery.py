# ===================== VKI PROPS MONASTERY: an abandoned monastery's furniture and ruin (2026-10-17) =====================
# MedievalSetting's coming area, the abandoned monastery. Loaded by vki_ns() after vki_props_library; uses the chapel's
# pew parts (vki_props_chapel), the debris helpers (vki_props_debris) and vki_fam_timber's vki_prism / vki_faces_of at
# build time. Every top-level name starts with vki_/VKI_ (T18).
# Props: origin at the footprint centre at floor level, back toward local +Y, front (the user's side) toward -Y.
#   ChoirStall_300        3.0 x 0.80 x 1.90, wall_floor (back +Y to a wall): three seats between shaped arm
#                         partitions with carved knobs on a low platform, a panelled back, a cresting rail and pinnacles
#   Pew_300_Broken        the chapel pew with its right end board fallen outward, the right half of the seat dropped to
#                         the floor, the back rail snapped (its right half on the floor), the right post gone
#   Pew_300_Overturned    the chapel pew tipped over backward onto its back, a little askew
#   FallenBeam            a roof tie-beam (0.30 x 0.34 x 4.2) down from the roof, one end on the floor, the other
#                         raised on a heap of rubble, both ends splintered; a broken rafter across it, loose planks
#   Desk_Scriptorium      1.00 x 0.62 x 1.30, floor: a monk's slanted writing desk, an open manuscript, a shelf with
#                         an inkhorn, a quill, a book and a candle (socket 30 W); the writer sits at -Y
#   Overlay_GlassShards   stained-glass shards strewn over ~1.0 x 0.6 m (under a broken lancet)
import bpy, bmesh, math, random
from mathutils import Vector, Matrix


# ---------------------------------------------------------------- helpers
def vki_mon_part(k, build, M):
    """build() adds geometry; the new vertices are moved by the 4x4 matrix M -> their list"""
    before = set(k.bm.verts)
    build()
    vs = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    k.bm.normal_update()
    return vs


def vki_mon_about(pivot, axis, deg):
    """rotation by deg about an axis ("X" / "Y" / "Z") through pivot"""
    P = Vector(pivot)
    return Matrix.Translation(P) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-P)


def vki_mon_pew_end(k, s):
    """one of the chapel pew's bench ends with its poppyhead (s -1: left, +1: right)"""
    end = [(-0.20, 0.0), (0.26, 0.0), (0.26, 0.80), (0.02, 0.80), (-0.20, 0.62)]
    x0, x1 = sorted((s * 1.29, s * 1.35))
    vs, fs = vki_prism(k, end, x0, x1, WOOD, axis="x", bevel=0.012, project=False)
    vki_proj_long(k, fs, WOOD, (0, 0, 1), off=vki_hash_off((x0, 0.0, 0.4)))
    vki_chp_poppyhead(k, s * 1.32, 0.145, 0.80)


# ---------------------------------------------------------------- ChoirStall_300
VKI_MON_STALL_BAYS = (-0.98, 0.0, 0.98)
VKI_MON_STALL_ARMS = (-1.445, -0.49, 0.49, 1.445)   # (the end arms 5 mm proud of the back panel's ends, T5S)


def vki_mon_choirstall(k):
    """three seats facing -Y on a platform (0.12), between shaped arm partitions (back 1.05, the arm sloping to 0.82
    at the front) with a carved knob on each arm's front, a panelled back to 1.62 (muntins, a pale mid rail) under a
    pale cresting rail and four small pinnacles over the partitions; oak (WOOD) with HEWN rails. Kept low (no canopy):
    from the game camera a canopied stall read as a dark wardrobe and hid its seats."""
    vki_lnk_box(k, -1.48, 1.48, -0.40, 0.37, 0.0, 0.12, WOOD, bev=0.015)
    vki_lnk_box(k, -1.47, 1.47, 0.30, 0.36, 0.115, 1.60, WOOD, bev=0.012)
    for i in range(7):                                    # muntins on the panel's front
        x = -1.38 + i * 0.46
        vki_lnk_box(k, x - 0.03, x + 0.03, 0.272, 0.302, 0.13, 1.55, WOOD, bev=0.006)
    vki_lnk_box(k, -1.44, 1.44, 0.268, 0.305, 1.04, 1.11, HEWN, bev=0.008)            # mid rail
    vki_lnk_box(k, -1.49, 1.49, 0.25, 0.40, 1.58, 1.66, HEWN, bev=0.012)              # cresting rail
    for xc in VKI_MON_STALL_BAYS:                         # seats
        vki_lnk_box(k, xc - 0.45, xc + 0.45, -0.16, 0.29, 0.44, 0.49, WOOD, bev=0.012)
        vki_lnk_box(k, xc - 0.42, xc + 0.42, -0.10, 0.25, 0.115, 0.445, WOOD, bev=0.01)  # the seat's front board
    arm = [(-0.30, 0.115), (0.31, 0.115), (0.31, 1.05), (0.10, 1.05), (-0.30, 0.82)]
    for x in VKI_MON_STALL_ARMS:                          # arm partitions, a knob on each front
        vki_prism(k, arm, x - 0.03, x + 0.03, WOOD, axis="x", bevel=0.01)
        vki_lnk_box(k, x - 0.045, x + 0.045, -0.30, -0.21, 0.80, 0.89, WOOD, bev=0.02)   # a carved knob (the pew's
        #                                                                 poppyhead cost 2,476 tris for the four)
    for x in VKI_MON_STALL_ARMS:                          # pinnacles: a shaft and a pointed cap
        vki_lnk_box(k, x - 0.045, x + 0.045, 0.28, 0.37, 1.64, 1.80, WOOD, bev=0.008)
        vki_mon_part(k, lambda: vki_ash_frustum(k, 0.0, 0.10, (0.06, 0.06), (0.004, 0.004), WOOD),
                     Matrix.Translation((x, 0.325, 1.795)))
    vki_home_meta(k, "wall_floor", "furniture", back="geo", vki_kind="ChoirStall", vki_seat_z=0.49,
                  use=[[x, -0.70, 0] for x in VKI_MON_STALL_BAYS],
                  vki_place_rule="against a wall, its back (local +Y) to it, facing across the choir")


# ---------------------------------------------------------------- Pew_300_Broken / _Overturned
def vki_mon_pew_broken(k):
    """the chapel pew, broken: the right bench end fallen outward onto the floor (turned 20 deg), the seat snapped
    by the middle support -- its right half's end on the floor --, the back rail snapped (the right half lying on the
    floor behind), the right post and the right half of the stretcher gone, the kneeler's right half knocked askew"""
    rk = math.radians(10.0)
    vki_mon_pew_end(k, -1)
    vki_mon_part(k, lambda: vki_mon_pew_end(k, 1), vki_mon_about((1.35, 0.0, 0.0), "Z", 20.0) @
                 vki_mon_about((1.35, 0.0, 0.0), "Y", 90.0))
    vki_lnk_box(k, -1.295, -0.03, -0.20, 0.13, 0.38, 0.46, WOOD, bev=0.015)
    vki_mon_part(k, lambda: vki_lnk_box(k, 0.03, 1.27, -0.20, 0.13, 0.38, 0.46, WOOD, bev=0.015),
                 vki_mon_about((0.03, 0.0, 0.38), "Y", 17.0))
    for x in (-0.65, 0.0):                                # back posts (the right one gone)
        c = Vector((x, 0.105, 0.44)) + Matrix.Rotation(-rk, 3, "X") @ Vector((0, 0, 0.16))
        k.box(tuple(c), (0.05, 0.045, 0.32), WOOD, rot=(-rk, 0, 0), bevel=0.01)
    c = Vector((-0.66, 0.105, 0.44)) + Matrix.Rotation(-rk, 3, "X") @ Vector((0, 0, 0.32))
    k.box(tuple(c), (1.27, 0.07, 0.08), HEWN, rot=(-rk, 0, 0), bevel=0.015)          # the rail's left half
    k.box((0.72, 0.55, 0.04), (1.20, 0.07, 0.08), HEWN, rot=(0, 0, 0.22), bevel=0.015)   # its right half, fallen
    vki_lnk_box(k, -1.295, -0.02, 0.16, 0.22, 0.10, 0.18, WOOD, bev=0.012)              # stretcher, left half
    vki_lnk_box(k, -0.03, 0.03, -0.17, 0.10, 0.0, 0.385, WOOD, bev=0.01)                # middle support
    vki_lnk_box(k, -1.325, -0.02, -0.275, -0.175, 0.07, 0.15, WOOD, bev=0.012)          # kneeler, left half
    vki_mon_part(k, lambda: vki_lnk_box(k, 0.02, 1.30, -0.275, -0.175, 0.0, 0.08, WOOD, bev=0.012),
                 vki_mon_about((0.02, -0.225, 0.0), "Z", -9.0))
    vki_lnk_box(k, -1.285, -1.235, -0.265, -0.185, 0.0, 0.075, WOOD, bev=0.008)
    for v in k.bm.verts:
        k.set_dark([v], 0.18)
    vki_home_meta(k, "floor", "furniture", vki_kind="Pew", vki_broken=1, use=[[-0.9, -0.50, 0]],
                  vki_note="abandoned chapel: rot 180 like the whole pews")


def vki_mon_pew_overturned(k):
    """the chapel pew tipped over backward: turned -90 deg about its back's foot (x axis), so it lies on its back
    with the seat standing up and the underside toward -Y, then 7 deg askew; recentred on its footprint"""
    vki_chp_pew(k)
    vs = list(k.bm.verts)
    bmesh.ops.transform(k.bm, verts=vs, matrix=vki_mon_about((0.0, 0.26, 0.0), "X", -90.0))
    lo = min(v.co.z for v in vs)
    ys = [v.co.y for v in vs]
    bmesh.ops.translate(k.bm, verts=vs, vec=(0.0, -(min(ys) + max(ys)) / 2, -lo))
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Rotation(math.radians(7.0), 4, "Z"))
    k.bm.normal_update()
    for v in vs:
        k.set_dark([v], 0.18)
    for key in ("vki_seat_z", "vki_use_note"):
        k.meta.pop(key, None)
    vki_home_meta(k, "floor", "furniture", vki_kind="Pew", vki_broken=1, use=[],
                  vki_note="abandoned chapel: overturned, lying on its back")


# ---------------------------------------------------------------- FallenBeam
def vki_mon_splinters(k, c, d, w, h, seed):
    """a splintered beam end at c looking along d (unit, horizontal-ish): a few long thin wedges standing out of the
    end face"""
    rnd = random.Random(seed)
    d = Vector(d).normalized(); s = d.cross(Vector((0, 0, 1))).normalized(); u = d.cross(s)   # (s, u, d) right-handed
    for i in range(4):
        o = Vector(c) - d * (0.02 + 0.007 * i) + s * rnd.uniform(-w * 0.35, w * 0.35) + u * rnd.uniform(-h * 0.35, h * 0.35)
        L = rnd.uniform(0.10, 0.24); t = rnd.uniform(0.03, 0.06)
        tri = [(-t, 0.0), (t, 0.0), (rnd.uniform(-t, t) * 0.4, L)]
        vki_mon_part(k, lambda tri=tri: vki_prism(k, tri, -t * 0.6, t * 0.6, WOOD, axis="y"),
                     Matrix.Translation(o) @ Matrix(((s.x, u.x, d.x, 0), (s.y, u.y, d.y, 0), (s.z, u.z, d.z, 0),
                                                     (0, 0, 0, 1))))   # (the wedge's length, its poly z, along d)


def vki_mon_fallen_beam(k):
    """the tie-beam along local x (4.2 m): its east end raised 0.45 on a rubble heap, the west end on the floor;
    splintered ends; a broken rafter (2.3 m) fallen across it; three loose planks; a few chips"""
    L, bw, bh = 4.2, 0.30, 0.34
    tilt = math.asin(0.45 / L)
    M = Matrix.Translation((0.0, 0.0, 0.45 / 2 + bh / 2)) @ Matrix.Rotation(-tilt, 4, "Y")
    vki_mon_part(k, lambda: vki_lnk_box(k, -L / 2, L / 2, -bw / 2, bw / 2, -bh / 2, bh / 2, WOOD, bev=0.02), M)
    ax = (M.to_3x3() @ Vector((1, 0, 0))).normalized()
    for sgn, seed in ((1, 31), (-1, 37)):
        vki_mon_splinters(k, M @ Vector((sgn * L / 2, 0.0, 0.0)), ax * sgn, bw, bh, seed)
    rnd = random.Random(41)
    for i, (x, y, r, z) in enumerate(((1.80, 0.02, 0.34, -0.04), (2.05, -0.28, 0.24, 0.0), (1.55, 0.30, 0.25, 0.0),
                                      (2.25, 0.24, 0.20, 0.0), (1.35, -0.26, 0.18, 0.0), (2.40, -0.05, 0.17, 0.0),
                                      (1.95, 0.05, 0.16, 0.26))):   # the rubble heap under the east end
        vki_deb_rock(k, x, y, r, 4100 + i, flat=0.75, mi=VKI_STONE_BLOCK_IN, z=z, dark=0.10)
    rf = math.radians(52.0)                               # the broken rafter across the beam
    Mr = Matrix.Translation((-0.35, 0.10, 0.20)) @ Matrix.Rotation(rf, 4, "Z") @ Matrix.Rotation(math.radians(-8.0), 4, "Y")
    vki_mon_part(k, lambda: vki_lnk_box(k, -1.15, 1.15, -0.08, 0.08, -0.09, 0.09, WOOD, bev=0.012), Mr)
    vki_mon_splinters(k, Mr @ Vector((1.15, 0.0, 0.0)), (Mr.to_3x3() @ Vector((1, 0, 0))).normalized(), 0.16, 0.18, 43)
    for i, (x, y, yaw, Lp) in enumerate(((-1.2, -0.55, 0.3, 1.1), (0.6, 0.65, -0.5, 0.9), (-0.4, -0.75, 1.2, 0.8))):
        vki_deb_plank(k, x, y, 0.015 + 0.012 * i, Lp, 0.18, 0.025, yaw, 4200 + i, mi=PLANKS)
    for i in range(5):                                    # chips round the heap
        vki_deb_rock(k, rnd.uniform(1.1, 2.5), rnd.uniform(-0.55, 0.55), rnd.uniform(0.04, 0.07), 4300 + i,
                     mi=VKI_STONE_BLOCK_IN)
    vki_home_meta(k, "floor", "furniture", vki_kind="FallenBeam", use=[],
                  vki_collider=[[0.0, 0.0, 0.40, 4.2, 0.36, 0.80], [1.85, 0.0, 0.25, 1.30, 0.80, 0.50]],
                  vki_place_rule="anywhere on open floor, any rotation; the beam and its heap block the way (the "
                                 "planks and the rafter's ends are walked over)")


# ---------------------------------------------------------------- Desk_Scriptorium
def vki_mon_desk(k):
    """a slanted writing desk: two side boards (front 0.80, the slope rising 30 deg to 1.10 at the back, a back post
    to 1.30), the desk board, a book stop, a shelf at 1.24-1.27 between the posts, a foot rail; an open manuscript on
    the slope (HIDE cover, PAPER pages), on the shelf an inkhorn, a quill, a closed book and a candle (30 W)"""
    ang = math.radians(30.0)
    for s in (-1, 1):
        x0, x1 = sorted((s * 0.46, s * 0.50))
        pts = [(-0.31, 0.0), (0.31, 0.0), (0.31, 1.30), (0.22, 1.30), (-0.31, 0.80)]
        vki_prism(k, pts, x0, x1, WOOD, axis="x", bevel=0.01)
    R = Matrix.Rotation(ang, 3, "X")
    c0 = Vector((0.0, -0.045, 0.955))
    k.box(tuple(c0), (0.92, 0.62, 0.03), WOOD, rot=(ang, 0, 0), bevel=0.01)          # the desk board
    k.box(tuple(c0 + R @ Vector((0.0, -0.30, 0.03))), (0.90, 0.025, 0.04), HEWN, rot=(ang, 0, 0), bevel=0.006)
    vki_lnk_box(k, -0.46, 0.46, 0.16, 0.30, 1.235, 1.265, WOOD, bev=0.008)            # shelf
    vki_lnk_box(k, -0.46, 0.46, 0.25, 0.29, 0.30, 0.38, WOOD, bev=0.008)              # back stretcher
    vki_lnk_box(k, -0.46, 0.46, -0.24, -0.18, 0.10, 0.16, WOOD, bev=0.008)            # foot rail
    k.box(tuple(c0 + R @ Vector((0.0, 0.0, 0.024))), (0.44, 0.32, 0.012), HIDE, rot=(ang, 0, 0), bevel=0.004)
    for s in (-1, 1):
        cp = c0 + R @ Vector((s * 0.105, 0.0, 0.040))
        k.box(tuple(cp), (0.20, 0.30, 0.020), PAPER, rot=(ang, s * math.radians(4.0), 0), bevel=0.004)
    vki_chp_cyl(k, (-0.26, 0.23, 1.30), 0.035, 0.03, 0.07, 10, HIDE)                  # the inkhorn
    vki_mon_part(k, lambda: vki_lnk_box(k, -0.004, 0.004, -0.004, 0.004, 0.0, 0.24, PAPER, bev=0.0),
                 Matrix.Translation((-0.24, 0.22, 1.30)) @ Matrix.Rotation(math.radians(24.0), 4, "Y"))   # the quill
    vki_lnk_box(k, -0.10, 0.12, 0.17, 0.29, 1.265, 1.33, HIDE, bev=0.006)             # a closed book
    sock = vki_chp_candle(k, (0.30, 0.23, 1.265), r=0.025, h=0.14, segs=12, flame=(0.06, 0.014))
    vki_home_meta(k, "floor", "furniture", vki_kind="Desk", use=[[0.0, -0.70, 180]],
                  vki_lights=[vki_chp_light(sock, 30.0)], vki_fx=[dict(fx="candle", pos=sock)],
                  vki_note="the writer sits at -Y (a Prop_Stool there)")


# ---------------------------------------------------------------- Overlay_GlassShards
def vki_mon_glass_shards(k):
    """twenty stained-glass shards lying flat over ~1.0 x 0.6 m, each a small triangle 1-2 mm higher than the last
    (never coplanar), turned at random; a few lead cames (IRON) among them"""
    rnd = random.Random(53)
    for i in range(20):
        x, y = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.3, 0.3)
        r = rnd.uniform(0.03, 0.08)
        tri = [(r * math.cos(a), r * math.sin(a)) for a in sorted(rnd.uniform(0, 2 * math.pi) for _ in range(3))]
        z = 0.002 + 0.0015 * i
        vki_mon_part(k, lambda tri=tri, z=z: vki_prism(k, tri, z, z + 0.004, STAINED, axis="z"),
                     Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z"))
    for i in range(3):
        k.box((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.25, 0.25), 0.0035 + 0.0011 * i), (rnd.uniform(0.15, 0.3), 0.008, 0.006),
              IRON, rot=(0, 0, rnd.uniform(0, 3.14)), bevel=0.0)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_place_rule="loose debris under a broken window; walkable (no collider)")


VKI_MON_SPECS = [
    ("SM_VKI_Prop_ChoirStall_300", vki_mon_choirstall, "prop"),
    ("SM_VKI_Prop_Pew_300_Broken", vki_mon_pew_broken, "prop"),
    ("SM_VKI_Prop_Pew_300_Overturned", vki_mon_pew_overturned, "prop"),
    ("SM_VKI_Prop_FallenBeam", vki_mon_fallen_beam, "prop"),
    ("SM_VKI_Prop_Desk_Scriptorium", vki_mon_desk, "prop"),
    ("SM_VKI_Overlay_GlassShards", vki_mon_glass_shards, "none"),
]
VKI_MON_NAMES = [n for n, _, _ in VKI_MON_SPECS]
vki_register([(n, fn, {"grime": gr}, "monastery") for n, fn, gr in VKI_MON_SPECS])
