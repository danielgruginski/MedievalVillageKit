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
def vki_mon_desk_frame(k):
    """the writing desk's woodwork: side boards, the desk board sloping 30 deg, its book stop, the shelf, the back
    stretcher and the foot rail -> (slope angle, its rotation, the board's centre)"""
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
    return ang, R, c0


def vki_mon_desk(k):
    """a slanted writing desk: two side boards (front 0.80, the slope rising 30 deg to 1.10 at the back, a back post
    to 1.30), the desk board, a book stop, a shelf at 1.24-1.27 between the posts, a foot rail; an open manuscript on
    the slope (HIDE cover, PAPER pages), on the shelf an inkhorn, a quill, a closed book and a candle (30 W)"""
    ang, R, c0 = vki_mon_desk_frame(k)
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


# ================================================================ the abandoned state (2026-10-17, round 2: the user,
# "the one in the game will be abandoned (but keep the new ones for the set)")
#   Altar_300_Stripped          the altar bare: no linen or candles, the mensa's front corner broken off (the chip on
#                               the floor), a torn strip of the frontal, a candlestick toppled, the cross on the floor
#   CandleStand_Pricket_Fallen  the pricket stand toppled, its candle out
#   Desk_Scriptorium_Fallen     the writing desk tipped onto its front, the manuscript, a book, the inkhorn, the quill,
#                               the candle and loose leaves spilled round it
#   Bookcase_150_Ransacked      a bookcase stripped: a shelf broken and slid down, a few books left, the rest heaped at
#                               its foot with loose leaves
#   Cot_Broken                  a monk's plank cot, a leg snapped so the bed has tipped onto that corner, the straw
#                               pallet slid off onto the floor, a blanket rag
#   RoofCollapse                a heap where the roof came in: rubble, slates, two broken rafters, daylight from the
#                               hole above (a cold spot)
#   Overlay_Pages               loose leaves and a torn open book strewn over ~1.3 x 0.9 m
def vki_mon_drop_glow(k):
    """delete the flame tongues (GLOW faces) of a built prop: an abandoned place's candles are out"""
    vs = list({v for f in k.bm.faces if f.material_index == GLOW for v in f.verts})
    if vs:
        bmesh.ops.delete(k.bm, geom=vs, context="VERTS")
    for key in ("vki_lights", "vki_fx"):
        k.meta.pop(key, None)


def vki_mon_settle(k, vs=None, centre=True):
    """drop the geometry onto the floor (its lowest point 2 mm under z 0) and, centre=True, put its footprint's middle
    on the origin"""
    vs = list(k.bm.verts) if vs is None else vs
    lo = min(v.co.z for v in vs)
    dx = dy = 0.0
    if centre:
        xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]
        dx, dy = -(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2
    bmesh.ops.translate(k.bm, verts=vs, vec=(dx, dy, -0.002 - lo))
    k.bm.normal_update()


def vki_mon_sheets(k, rng, n, rx, ry, cx=0.0, cy=0.0, z0=0.002):
    """n loose parchment leaves (PAPER, 0.19 x 0.26) lying over +-rx, +-ry, each 1.2 mm over the last"""
    for i in range(n):
        z = z0 + 0.0012 * i
        vki_mon_part(k, lambda z=z: vki_lnk_box(k, -0.095, 0.095, -0.13, 0.13, z, z + 0.0015, PAPER, bev=0.0),
                     Matrix.Translation((cx + rng.uniform(-rx, rx), cy + rng.uniform(-ry, ry), 0.0)) @
                     Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z"))


def vki_mon_altar_stripped(k):
    zt = 1.0
    vki_lnk_box(k, -0.84, 0.84, -0.36, 0.40, 0.0, 0.935, DRESS, bev=0.02)
    slab = [(-0.90, -0.28), (-0.76, -0.45), (0.90, -0.45), (0.90, 0.45), (-0.90, 0.45)]   # the corner broken off
    vki_prism(k, slab, 0.93, zt, DRESS, axis="z", bevel=0.012)
    vki_deb_rock(k, -1.05, -0.72, 0.09, 6101, flat=0.6, mi=DRESS)                      # the broken corner
    vki_deb_rock(k, -0.82, -0.86, 0.05, 6102, flat=0.6, mi=DRESS)
    vs = vki_lnk_box(k, 0.06, 0.78, -0.378, -0.362, 0.42, 0.925, VKI_TEXTILE, bev=0.003)   # what is left of the frontal
    vki_textile_map(k, vki_faces_of(vs), "altar_frontal", plane=((1, 0, 0), (0, 0, 1)))
    rng = random.Random(611)
    vs = vki_mon_part(k, lambda: vki_lnk_box(k, -0.30, 0.30, -0.20, 0.20, 0.0, 0.006, VKI_TEXTILE, bev=0.0),
                      Matrix.Translation((0.35, -0.95, 0.002)) @ Matrix.Rotation(0.35, 4, "Z"))
    vki_textile_map(k, vki_faces_of(vs), "altar_frontal", plane=((1, 0, 0), (0, 1, 0)))
    def stick():                                          # a candlestick without its candle, lying on the mensa
        for (cz, r1, r2, h, segs) in ((0.0125, 0.07, 0.07, 0.025, 16), (0.05, 0.065, 0.024, 0.05, 16),
                                      (0.1575, 0.017, 0.017, 0.205, 10), (0.2575, 0.055, 0.055, 0.015, 16)):
            vki_chp_cyl(k, (0.0, 0.0, cz), r1, r2, h, segs, BRONZE)
    vki_mon_part(k, stick, Matrix.Translation((0.30, 0.12, zt + 0.068)) @ Matrix.Rotation(0.4, 4, "Z") @
                 Matrix.Rotation(math.pi / 2, 4, "Y"))
    def cross():                                          # the cross, lying on the floor before the altar
        vki_lnk_box(k, -0.027, 0.027, -0.24, 0.24, 0.0, 0.054, BRONZE, bev=0.008)
        vki_lnk_box(k, -0.18, 0.18, 0.07, 0.125, 0.003, 0.050, BRONZE, bev=0.008)
    vki_mon_part(k, cross, Matrix.Translation((-0.45, -1.00, 0.0)) @ Matrix.Rotation(1.1, 4, "Z"))
    for v in k.bm.verts:
        k.set_dark([v], 0.15)
    vki_home_meta(k, "floor", "furniture", vki_kind="Altar", vki_broken=1, vki_mensa_z=zt, use=[[0.0, -0.80, 0]],
                  vki_collider=[[0.0, 0.0, 0.5, 1.80, 0.90, 1.0]], vki_textile="altar_frontal",
                  vki_note="abandoned church: no candles, nothing lit; the cross and the chips before it are walked over")


def vki_mon_candlestand_fallen(k):
    vki_chp_candlestand(k)
    vki_mon_drop_glow(k)
    vs = list(k.bm.verts)
    bmesh.ops.transform(k.bm, verts=vs, matrix=vki_mon_about((0.0, -0.13, 0.0), "X", 84.0) @
                        Matrix.Rotation(0.5, 4, "Z"))
    vki_mon_settle(k)
    for v in k.bm.verts:
        k.set_dark([v], 0.15)
    vki_home_meta(k, "floor", "furniture", vki_kind="CandleStand", vki_broken=1, use=[])


def vki_mon_desk_fallen(k):
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    vki_mon_desk_frame(k)
    vs = list(k.bm.verts)
    bmesh.ops.transform(k.bm, verts=vs, matrix=vki_mon_about((0.0, -0.31, 0.0), "X", 78.0))   # onto its front
    vki_mon_settle(k)
    rng = random.Random(631)
    vki_lib_open_book(k, Matrix.Translation((0.62, 0.55, 0.0005)) @ Matrix.Rotation(0.5, 4, "Z"), colour="brown")
    col, des = vki_lib_pick(rng)
    vki_lib_lying(k, -0.70, 0.40, 0.0, 0.05, 0.22, 0.30, col, des, rz=-0.6)
    vki_mon_part(k, lambda: vki_chp_cyl(k, (0.0, 0.0, 0.0), 0.035, 0.03, 0.07, 10, HIDE),
                 Matrix.Translation((-0.55, -0.62, 0.033)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))   # the inkhorn
    vki_mon_part(k, lambda: vki_lnk_box(k, -0.004, 0.004, -0.12, 0.12, 0.0, 0.008, PAPER, bev=0.0),
                 Matrix.Translation((-0.35, -0.75, 0.002)) @ Matrix.Rotation(0.9, 4, "Z"))           # the quill
    vki_mon_part(k, lambda: vki_chp_cyl(k, (0.0, 0.0, 0.0), 0.025, 0.025, 0.14, 12, VKI_WAX),
                 Matrix.Translation((0.75, -0.55, 0.027)) @ Matrix.Rotation(1.2, 4, "Z") @
                 Matrix.Rotation(math.pi / 2, 4, "Y"))                                               # the candle
    vki_mon_sheets(k, rng, 8, 0.75, 0.55)
    vki_home_meta(k, "floor", "furniture", vki_kind="Desk", vki_broken=1, use=[])


def vki_mon_bookcase_ransacked(k):
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(1503)
    x0, x1, yf, sh = vki_lib_case(k, 1.40, shelves=(0.10, 0.56, 1.48), seed=4)   # the third shelf broken out
    (z0, c0), (z1, c1), (z3, c3) = sh
    L = x1 - x0 - 0.01; a = math.asin(0.40 / L)                    # it slid down to rest on the shelf below
    vki_mon_part(k, lambda: vki_home_box(k, -L / 2, L / 2, -0.15, 0.14, -0.02, 0.02, WOOD, bev=0.008),
                 Matrix.Translation(((x0 + x1) / 2, 0.0, z1 + 0.24)) @ Matrix.Rotation(-a, 4, "Y"))
    vki_lib_shelf(k, rng, x0 + 0.004, x0 + 0.40, z0, yf, c0 - 0.025, 0.30, fill=0.8, lean=0.5, flat=0.0)
    vki_lib_stack(k, rng, x1 - 0.30, yf + 0.13, z1, 2, 0.30, 0.24)
    col, des = vki_lib_pick(rng)
    vki_lib_lying(k, x0 + 0.40, yf + 0.14, z3, 0.05, 0.22, 0.30, col, des, rz=0.3)
    vki_lib_stack(k, rng, -0.30, yf - 0.36, 0.0, 3, 0.32, 0.25, rz=0.5)                     # the heap at its foot
    vki_lib_stack(k, rng, 0.25, yf - 0.30, 0.0, 2, 0.30, 0.24, rz=-0.4)
    for x, y, rz in ((0.55, -0.62, 0.9), (-0.05, -0.70, -0.5), (-0.62, -0.58, 1.6)):
        col, des = vki_lib_pick(rng)
        vki_lib_lying(k, x, y, 0.0, rng.uniform(0.035, 0.06), 0.20, 0.27, col, des, rz=rz)
    vki_mon_sheets(k, rng, 6, 0.6, 0.20, cy=-0.62)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", vki_kind="Bookcase", vki_broken=1, use=[],
                  vki_collider=[[0.0, 0.0, 1.0, 1.40, 0.36, 2.0]],
                  vki_note="the books heaped before it are walked over")


def vki_mon_cot_broken(k):
    """a plank cot 0.86 x 1.96 (legs 0.36): the foot-right leg snapped -- the bed tipped over the diagonal between
    the head-right and foot-left legs until that corner's stub met the floor --, the snapped leg lying by it, the straw
    pallet slid off onto the floor, a blanket rag (CLOTH_B)"""
    hx, hy, lh, stub = 0.40, 0.94, 0.36, 0.12
    before = set(k.bm.verts)
    for sx in (-1, 1):
        for sy in (-1, 1):
            z1 = stub if (sx, sy) == (1, -1) else lh - 0.006            # (tops inside the rails, T5S)
            vki_home_box(k, sx * hx - 0.03, sx * hx + 0.03, sy * hy - 0.03, sy * hy + 0.03, 0.0, z1, WOOD, bev=0.008)
    for sx in (-1, 1):
        vki_home_box(k, sx * hx - 0.025, sx * hx + 0.025, -hy - 0.036, hy + 0.036, lh - 0.08, lh, WOOD, bev=0.008)
    for sy, top in ((1, 0.62), (-1, 0.50)):
        vki_home_box(k, -hx - 0.036, hx + 0.036, sy * hy - 0.02, sy * hy + 0.02, 0.10, top, WOOD, bev=0.01)
    for i in range(6):
        y = -hy + 0.17 + i * 0.32
        vki_home_box(k, -hx + 0.02, hx - 0.02, y - 0.10, y + 0.10, lh - 0.004, lh + 0.02, WOOD, bev=0.006)
    frame = [v for v in k.bm.verts if v not in before]
    A = Vector((hx, hy, 0.0)); B = Vector((-hx, -hy, 0.0)); C = Vector((hx, -hy, stub))
    d = (B - A).normalized()
    dist = (C - A).cross(d).length
    ang = math.asin(min(1.0, (stub - 0.01) / dist))
    for sgn in (1, -1):
        M = Matrix.Translation(A) @ Matrix.Rotation(sgn * ang, 4, d) @ Matrix.Translation(-A)
        if (M @ C).z < C.z:
            break
    bmesh.ops.transform(k.bm, verts=frame, matrix=M)
    k.bm.normal_update()
    vki_mon_part(k, lambda: vki_home_box(k, -0.03, 0.03, -0.03, 0.03, 0.0, lh - stub - 0.02, WOOD, bev=0.008),
                 Matrix.Translation((hx + 0.30, -hy + 0.10, 0.032)) @ Matrix.Rotation(0.7, 4, "Z") @
                 Matrix.Rotation(math.pi / 2, 4, "Y"))                               # the snapped leg
    mv = vki_mon_part(k, lambda: vki_home_box(k, -0.38, 0.38, -0.88, 0.88, 0.0, 0.13, VKI_STRAW, bev=0.05, segs=2),
                      Matrix.Translation((hx + 0.42, 0.10, 0.0)) @ Matrix.Rotation(-0.18, 4, "Z"))
    k.project(vki_faces_of(mv), VKI_STRAW)
    vki_mon_part(k, lambda: vki_lnk_box(k, -0.35, 0.35, -0.45, 0.45, 0.0, 0.008, CLOTH_B, bev=0.0),
                 Matrix.Translation((-hx - 0.30, -0.55, 0.002)) @ Matrix.Rotation(0.4, 4, "Z"))
    for v in k.bm.verts:
        k.set_dark([v], 0.15)
    vki_home_meta(k, "floor", "furniture", vki_kind="Bed", vki_broken=1, use=[],
                  vki_note="a monk's cell or the dorter; the pallet beside it is walked over")


def vki_mon_roof_collapse(k):
    """a heap 2.2 x 1.8 where the roof came in: 14 rocks (0.10-0.34) mounded higher in the middle, a dozen slates
    tilted among them (STONE_BLOCK_IN, darkened), two broken rafters lying on the heap with splintered ends; a cold
    daylight spot from the hole above (6.5 m)"""
    rng = random.Random(651)
    for i in range(14):
        a = rng.uniform(0, 6.28); d = rng.uniform(0.0, 1.0) ** 0.7
        x, y = math.cos(a) * d * 1.0, math.sin(a) * d * 0.8
        r = 0.34 - 0.20 * d + rng.uniform(-0.04, 0.04)
        vki_deb_rock(k, x, y, r, 6510 + i, flat=0.7, mi=VKI_STONE_BLOCK_IN, z=max(0.0, (1 - d) * 0.18 - 0.05), dark=0.12)
    for i in range(12):
        a = rng.uniform(0, 6.28); d = rng.uniform(0.2, 1.15)
        z = 0.02 + 0.30 * max(0.0, 1 - d) + 0.004 * i
        vs = vki_mon_part(k, lambda z=z: vki_lnk_box(k, -0.16, 0.16, -0.11, 0.11, z, z + 0.022, VKI_STONE_BLOCK_IN, bev=0.004),
                          Matrix.Translation((math.cos(a) * d, math.sin(a) * d * 0.8, 0.0)) @
                          Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z") @ Matrix.Rotation(rng.uniform(-0.4, 0.4), 4, "X"))
        k.set_dark(vs, 0.35)
    for (x, y, rz, L, tilt, seed) in ((-0.10, 0.10, 0.5, 1.7, -0.22, 661), (0.35, -0.30, -0.9, 1.1, 0.15, 663)):
        M = Matrix.Translation((x, y, 0.32)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(tilt, 4, "Y")
        vki_mon_part(k, lambda L=L: vki_lnk_box(k, -L / 2, L / 2, -0.06, 0.06, -0.07, 0.07, WOOD, bev=0.01), M)
        vki_mon_splinters(k, M @ Vector((L / 2, 0.0, 0.0)), (M.to_3x3() @ Vector((1, 0, 0))).normalized(), 0.12, 0.14, seed)
    vki_mon_settle(k, centre=False)
    vki_home_meta(k, "floor", "furniture", vki_kind="RoofCollapse", use=[],
                  vki_collider=[[0.0, 0.0, 0.30, 2.0, 1.6, 0.6]],
                  vki_lights=[dict(type="SPOT", role="daylight", pos=[0.0, 0.0, 6.5], aim=[0.0, 0.0, 0.0], cone=38.0,
                                   blend=0.5, radius=0.3, w_day=1800.0, w_night=120.0, color_day=[.82, .88, 1.0],
                                   color_night=[.55, .62, .90], shadows=1)],
                  vki_place_rule="open floor where the roof came in; rot multiples of 90 (the BFS boxes its collider)")


def vki_mon_pages(k):
    k.slot_mats[VKI_TEXTILE] = VKI_LIB_MAT
    rng = random.Random(671)
    vki_lib_open_book(k, Matrix.Translation((0.25, 0.05, 0.0005)) @ Matrix.Rotation(-0.4, 4, "Z"),
                      colour=vki_lib_pick(rng)[0])
    vki_mon_sheets(k, rng, 12, 0.6, 0.40)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_place_rule="loose debris on open floor; walkable (no collider)")



# ---------------------------------------------------------------- overgrowth (2026-10-18)
# Moss: low mounds on the ASH slot mapped to M_VKI_Moss (the exterior moss texture); weeds and ivy: the exterior
# foliage atlas (FOLIAGE, two-sided cards: card() cells "grass", "daisy", "ivy"); ivy stems WOOD (Dark).
def vki_mon_moss(k, x, y, rx, ry, seed, i=0, z=0.0, h=0.022, ns=14):
    """a low moss patch with a smooth lobed outline (three low harmonics, not per-vertex noise: the hard edge of an
    opaque patch reads as a cut-out when it is spiky), a dome to h; i staggers its flat bottom (0.7 mm a patch) so
    overlapping patches never share a plane (T5S)"""
    k.slot_mats[VKI_ASH] = "M_VKI_Moss"
    rnd = random.Random(seed)
    hs = [(m, rnd.uniform(0.06, 0.16) / (m * 0.5), rnd.uniform(0, 2 * math.pi)) for m in (2, 3, 5)]
    rr = [1.0 + sum(a * math.sin(m * 2 * math.pi * j / ns + ph) for m, a, ph in hs) for j in range(ns)]
    z0 = z + 0.001 + 0.0007 * i
    bm = k.bm
    top = bm.verts.new((x, y, z + h))
    rings = [[bm.verts.new((x + math.cos(2 * math.pi * j / ns) * rx * t * rr[j],
                            y + math.sin(2 * math.pi * j / ns) * ry * t * rr[j], z + hz)) for j in range(ns)]
             for t, hz in ((0.6, h * 0.8), (1.0, 0.004))]
    bot = [bm.verts.new((v.co.x, v.co.y, z0)) for v in rings[-1]]
    cb = bm.verts.new((x, y, z0))
    fs = []
    for j in range(ns):
        n = (j + 1) % ns
        fs.append(bm.faces.new((top, rings[0][j], rings[0][n])))
        fs.append(bm.faces.new((rings[0][j], rings[1][j], rings[1][n], rings[0][n])))
        fs.append(bm.faces.new((rings[1][j], bot[j], bot[n], rings[1][n])))
        fs.append(bm.faces.new((cb, bot[n], bot[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.material_index = VKI_ASH
        f.smooth = True
    k.project(fs, VKI_ASH)
    return [top, cb] + rings[0] + rings[1] + bot


def vki_mon_card(k, c, right, up, w, h, cell, flip=False):
    """a flat foliage card (2 tris; card() is a 3 x 3 grid for bending): FOLIAGE, two-sided on export"""
    u0, u1, v0, v1 = fol_uv(cell)
    if flip:
        u0, u1 = u1, u0
    C = Vector(c); R = Vector(right).normalized(); U = Vector(up).normalized()
    q = [(-0.5, -0.5, u0, v0), (0.5, -0.5, u1, v0), (0.5, 0.5, u1, v1), (-0.5, 0.5, u0, v1)]
    vs = [k.bm.verts.new(C + R * (a * w) + U * (b * h)) for a, b, _, _ in q]
    f = k.bm.faces.new(vs)
    f.material_index = FOLIAGE
    f.smooth = True
    for l, (_, _, u, v) in zip(f.loops, q):
        l[k.uv].uv = (u, v)
    return f


def vki_mon_tuft(k, x, y, h, rnd, cell="grass", n=3, z=0.0, lean=(0.30, 0.55)):
    """a weed tuft: n cards round a vertical axis, each leaning out (so it reads from the game camera above)"""
    a0 = rnd.uniform(0.0, 2 * math.pi)
    for i in range(n):
        a = a0 + 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        out = Vector((math.cos(a), math.sin(a), 0.0))
        t = rnd.uniform(*lean)
        up = out * math.sin(t) + Vector((0.0, 0.0, 1.0)) * math.cos(t)
        hh = h * rnd.uniform(0.85, 1.1)
        vki_mon_card(k, Vector((x, y, z - 0.01)) + up * (hh / 2) + out * 0.03, (-math.sin(a), math.cos(a), 0.0), up,
                     hh * rnd.uniform(0.8, 1.0), hh, cell, flip=rnd.random() < 0.5)


def vki_mon_creeper(k, x, y, s, rnd, z=0.0):
    """ground ivy: an ivy card lying almost flat, its stems trailing out"""
    a = rnd.uniform(0.0, 2 * math.pi)
    out = Vector((math.cos(a), math.sin(a), 0.0))
    up = (out + Vector((0.0, 0.0, 0.22))).normalized()
    vki_mon_card(k, Vector((x, y, z + 0.035)) + out * (s * 0.35), (-math.sin(a), math.cos(a), 0.0), up, s, s, "ivy",
                 flip=rnd.random() < 0.5)


def vki_mon_overgrowth(k):
    """1.8 x 1.4 m of floor gone green: three moss patches, weeds standing in them (grass, a few daisies), ground ivy
    creeping off their edges"""
    rnd = random.Random(1901)
    for i, (x, y, rx, ry) in enumerate(((-0.35, 0.10, 0.52, 0.40), (0.42, -0.18, 0.40, 0.30), (0.10, 0.42, 0.30, 0.22))):
        vki_mon_moss(k, x, y, rx, ry, 1910 + i, i=i)
    for i, (x, y, h) in enumerate(((-0.45, 0.20, 0.42), (-0.15, -0.10, 0.30), (0.40, -0.15, 0.36), (0.55, 0.05, 0.24),
                                   (0.05, 0.45, 0.28), (-0.62, -0.18, 0.22), (0.20, 0.15, 0.20))):
        vki_mon_tuft(k, x, y, h * 1.2, rnd, cell="daisy" if i in (2, 5) else "grass", n=4, z=0.015)
    for (x, y, sz) in ((-0.70, 0.40, 0.38), (0.68, -0.42, 0.34), (-0.05, -0.45, 0.30), (0.45, 0.45, 0.30)):
        vki_mon_creeper(k, x, y, sz, rnd)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_mon_moss_patch(k):
    """moss only (1.2 x 0.9 m): four low patches in the floor's joints and two small tufts -- walkable"""
    rnd = random.Random(1931)
    for i, (x, y, rx, ry) in enumerate(((-0.30, 0.05, 0.32, 0.26), (0.25, -0.15, 0.28, 0.22), (0.30, 0.28, 0.20, 0.14),
                                        (-0.38, -0.32, 0.16, 0.12))):
        vki_mon_moss(k, x, y, rx, ry, 1940 + i, i=i, h=0.016)
    vki_mon_tuft(k, -0.32, 0.08, 0.18, rnd, z=0.012)
    vki_mon_tuft(k, 0.28, -0.12, 0.14, rnd, z=0.012)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_mon_ivy(k, zmax):
    """ivy hanging down a wall face from under its top (it came in over the broken wall head or through the roof):
    five stems, the longest to ~0.4 m off the floor, leafy cards along them, thickest at the top, its highest leaf at
    zmax (wall_hung tops stay 0.14 under the host wall's H, T12); 1.4 m wide, wall_hung (back y 0)"""
    top = zmax - 0.36
    rnd = random.Random(int(zmax * 100) + 1951)
    k.slot_mats[WOOD] = "Dark"
    for si, (x0, frac) in enumerate(((-0.50, 0.55), (-0.22, 0.85), (0.05, 0.65), (0.30, 0.92), (0.52, 0.45))):
        L = (top - 0.40) * frac
        n = max(3, int(L / 0.36))
        pts = []
        x = x0
        for i in range(n + 1):
            z = top - L * i / n
            pts.append(Vector((x, -0.025 - 0.02 * math.sin(i * 1.3 + si), z)))
            x = max(-0.62, min(0.62, x + rnd.uniform(-0.10, 0.10)))
        for ri, (a, b) in enumerate(zip(pts[:-1:2], pts[2::2] + ([pts[-1]] if n % 2 else []))):   # a rod every 2 joints
            u = (b - a).normalized()                                 # 6 mm past each joint, every other one turned 45
            vki_dpr_rod(k, a - u * 0.006, b + u * 0.006, 0.016 if ri % 2 == 0 else 0.0135, WOOD,   # deg and thinner:
                        roll=math.pi / 4 * (ri % 2))                 # no end caps back to back, no sides in one
            # plane (2026-10-24)
        for i, pnt in enumerate(pts[:-1]):                          # leaves: two cards a joint up top, fewer below
            f = i / n
            for j in range(3 if f < 0.25 else 2 if f < 0.7 else 1):
                sz = rnd.uniform(0.36, 0.50) * (1.0 - 0.35 * f)
                ang = rnd.uniform(-0.5, 0.5)
                R = Vector((math.cos(ang), 0.0, math.sin(ang)))
                U = (Vector((-math.sin(ang), 0.0, math.cos(ang))) + Vector((0.0, -rnd.uniform(0.15, 0.45), 0.0)))
                c = pnt + Vector((rnd.uniform(-0.10, 0.10), -rnd.uniform(0.05, 0.12), sz * 0.15))
                c.x = max(-0.70 + sz / 2, min(0.70 - sz / 2, c.x))
                vki_mon_card(k, c, R, U, sz, sz, "ivy", flip=rnd.random() < 0.5)
    # a mat of leaves along the top, where it comes over
    for i in range(10):
        x = -0.55 + 1.1 * (i % 5) / 4 + rnd.uniform(-0.08, 0.08) + (0.12 if i >= 5 else 0.0)
        sz = rnd.uniform(0.40, 0.52)
        c = Vector((max(-0.70 + sz / 2, min(0.70 - sz / 2, x)), -0.10 - 0.04 * (i >= 5), top - 0.08 - 0.22 * (i >= 5)))
        vki_mon_card(k, c, (1.0, 0.0, rnd.uniform(-0.15, 0.15)), (0.0, -rnd.uniform(0.45, 0.75), 1.0), sz, sz, "ivy",
                     flip=i % 2 == 0)
    dz = zmax - max(v.co.z for v in k.bm.verts)
    for v in k.bm.verts:
        v.co.y = min(v.co.y, -0.004)                                 # off the wall face
        v.co.z += dz
    vki_home_meta(k, "wall_hung", "furniture", back=0.0, use=[], vki_nav="none",
                  vki_note="top %.2f: on walls %.1f m and up (Timber / Stone 3.0, Ashlar 4.5)" % (zmax, zmax + 0.16))


def vki_mon_ivy_wall(k): vki_mon_ivy(k, 2.84)
def vki_mon_ivy_wall_tall(k): vki_mon_ivy(k, 4.34)


# ---------------------------------------------------------------- the font, the saint (2026-10-18)
def vki_mon_snap(vs, z, rnd, lo=-0.07, hi=0.03):
    """a jagged break: vertices at/above z (a lathe's top ring) jostled in height"""
    for v in vs:
        if v.co.z > z - 1e-4:
            v.co.z += rnd.uniform(lo, hi)


def vki_mon_rest(k, vs, M, sink=0.008):
    """move vs by M, then drop them so their lowest point is `sink` under the floor"""
    bmesh.ops.transform(k.bm, verts=vs, matrix=M)
    dz = -sink - min(v.co.z for v in vs)
    for v in vs:
        v.co.z += dz
    k.bm.normal_update()


def vki_mon_font_broken(k):
    """the chapel's octagonal font (Prop_Font) thrown down: the step and the stem, snapped at ~0.40; the bowl lying
    on its side in front, dry (grit in it); a piece of the rim and chips about. 1.6 x 1.3 m"""
    rnd = random.Random(2001)
    vki_chp_lathe(k, [(0.54, 0.0), (0.54, 0.12)], mis=[DRESS])
    vki_chp_lathe(k, [(0.43, 0.115), (0.43, 0.20)], mis=[DRESS])
    rings, bands, bot, top = vki_chp_lathe(k, [(0.20, 0.195), (0.20, 0.42)], mis=[DRESS])
    vki_mon_snap(rings[-1], 0.42, rnd, -0.06, 0.05)
    before = set(k.bm.verts)
    rings, bands, bot, top = vki_chp_lathe(k, [(0.29, 0.0), (0.46, 0.40), (0.46, 0.55), (0.37, 0.55), (0.37, 0.45)],
                                           mis=[DRESS, DRESS, VKI_STONE_BLOCK_IN, DRESS, VKI_ASH])
    for v in rings[4]:
        k.set_dark([v], 0.3)
    bv = [v for v in k.bm.verts if v not in before]
    vki_mon_rest(k, bv, Matrix.Translation((0.55, -0.62, 0.0)) @ Matrix.Rotation(0.45, 4, "Z") @
                 Matrix.Rotation(math.radians(78), 4, "X"))                       # its mouth to the room (-Y)
    # a piece of the rim (a wedge of the octagon's top band) and chips
    rim = vki_mon_part(k, lambda: vki_prism(k, [(0.37, 0.0), (0.46, 0.0), (0.46, 0.15), (0.37, 0.15)], -0.16, 0.16,
                                            DRESS, axis="x"),
                       Matrix.Translation((-0.62, -0.42, 0.0)) @ Matrix.Rotation(2.2, 4, "Z") @
                       Matrix.Rotation(0.10, 4, "Y") @ Matrix.Translation((0.0, -0.415, -0.075)))
    vki_mon_rest(k, rim, Matrix.Identity(4))
    k.set_dark(rim, 0.1)
    for i in range(5):
        sz = rnd.uniform(0.05, 0.09)
        vs = list(set(k.box((rnd.uniform(-0.65, 0.65), rnd.uniform(-0.95, -0.35), sz * 0.3), (sz, sz * 0.8, sz * 0.6),
                            DRESS, rot=(rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0, math.pi)),
                            bevel=0.0, seed=2010 + i)))
        k.set_dark(vs, 0.15)
    vki_home_meta(k, "floor", "furniture", use=[], vki_kind="Font", vki_nav="block",
                  vki_note="the abandoned twin of Prop_Font (chapel): the stem stands at the origin, the bowl lies at -Y")


def vki_mon_saint_mats(k):
    """pale carved stone (CAP -> AncientCap) on the Ashlar block stone (STONE_BLOCK_IN -> AshlarBlock)"""
    k.slot_mats[VKI_CAP] = "M_VKI_AncientCap"
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_AshlarBlock"


def vki_mon_saint_body(k, z0, z_from=None):
    """the robed saint (pale CAP stone) standing on z0: a habit, hands joined in prayer at the chest, a cord hanging
    from the girdle; z_from: build the habit from that height up (a statue broken off at the shins)"""
    prof = [(0.27, z0 - 0.005), (0.25, z0 + 0.40), (0.20, z0 + 0.85), (0.22, z0 + 1.12), (0.245, z0 + 1.28),
            (0.15, z0 + 1.38), (0.0, z0 + 1.40)]
    if z_from is not None:
        prof = [(0.255, z_from)] + [p for p in prof if p[1] > z_from + 0.02]
    vki_home_lathe(k, prof, c=(0.0, 0.02, 0.0), segs=12, mi=VKI_CAP, sy=0.72)
    vki_home_hoop(k, (0.0, 0.02, z0 + 0.80), 0.20, 0.222, 0.05, segs=12, mi=VKI_CAP, sy=0.72)        # girdle
    k.box((0.07, -0.155, z0 + 0.58), (0.03, 0.03, 0.40), VKI_CAP, bevel=0.0, rot=(0.10, 0.0, 0.0))     # the cord
    for sx in (-1.0, 1.0):
        vki_adv_rod(k, (sx * 0.23, 0.02, z0 + 1.26), (sx * 0.21, -0.08, z0 + 0.98), 0.12, VKI_CAP)    # upper arm
        vki_adv_rod(k, (sx * 0.20, -0.08, z0 + 0.99), (sx * 0.05, -0.22, z0 + 1.08), 0.11, VKI_CAP)   # sleeve
    k.box((0.0, -0.25, z0 + 1.14), (0.08, 0.06, 0.15), VKI_CAP, bevel=0.012, rot=(-0.35, 0.0, 0.0))  # joined hands


def vki_mon_saint_head(k, z0):
    """the face in its hood, over a body standing on z0"""
    hv = vki_home_ico(k, (0.0, -0.035, z0 + 1.52), 0.105, VKI_CAP, scale=(0.9, 1.0, 1.15), sub=2)      # the face
    k.project(vki_faces_of(hv), VKI_CAP)
    cv = vki_home_ico(k, (0.0, 0.045, z0 + 1.57), 0.135, VKI_CAP, scale=(1.05, 1.1, 1.30), sub=2)     # the hood
    k.project(vki_faces_of(cv), VKI_CAP)
    vki_home_hoop(k, (0.0, 0.03, z0 + 1.385), 0.10, 0.205, 0.07, segs=12, mi=VKI_CAP, sy=0.80)       # its cowl


def vki_mon_saint(k):
    """a saint 2.2 m tall on a plinth (0.8 m square): a robed, hooded monk in prayer, pale stone (for the set: the
    abandoned monastery's has fallen, Statue_Saint_Toppled)"""
    z0 = vki_adv_plinth(k, h=0.40, hw=0.35)
    vki_mon_saint_body(k, z0)
    vki_mon_saint_head(k, z0)
    vki_mon_saint_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_note="2.2 m tall: stand it by a wall or in a niche (it hides what is behind it)")


def vki_mon_saint_toppled(k):
    """the saint thrown down: the plinth with the habit's hem snapped at the shins; the body lying on its back in
    front, a little askew; the hooded head broken off and rolled aside; chips"""
    rnd = random.Random(2031)
    z0 = vki_adv_plinth(k, h=0.40, hw=0.35)
    rv, rf = vki_home_lathe(k, [(0.27, z0 - 0.005), (0.258, z0 + 0.20), (0.20, z0 + 0.215), (0.0, z0 + 0.22)],
                            c=(0.0, 0.02, 0.0), segs=12, mi=VKI_CAP, sy=0.72)
    vki_mon_snap(rv, z0 + 0.20, rnd, -0.07, 0.03)
    vki_ash_new(k, lambda: vki_mon_saint_body(k, 0.0, z_from=0.30),
                Matrix.Translation((0.08, -0.62, 0.0)) @ Matrix.Rotation(math.pi - 0.28, 4, "Z") @
                Matrix.Rotation(math.radians(-90), 4, "X") @ Matrix.Translation((0.0, 0.0, -0.30)), sink=0.008)
    vki_ash_new(k, lambda: vki_mon_saint_head(k, 0.0),
                Matrix.Translation((0.62, -1.50, 0.0)) @ Matrix.Rotation(1.1, 4, "Z") @
                Matrix.Rotation(1.25, 4, "Y") @ Matrix.Translation((0.0, 0.0, -1.55)), sink=0.004)
    for i in range(4):
        c = _ico(k, (rnd.uniform(-0.45, 0.45), rnd.uniform(-0.70, -0.42), 0.025), 0.045, VKI_CAP,
                 scale=(1, 0.8, 0.6), sub=0, jit=0.01, seed=2040 + i)
        k.project(vki_faces_of(c), VKI_CAP)
    vki_mon_saint_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block")


VKI_MON_SPECS = [
    ("SM_VKI_Prop_ChoirStall_300", vki_mon_choirstall, "prop"),
    ("SM_VKI_Prop_Pew_300_Broken", vki_mon_pew_broken, "prop"),
    ("SM_VKI_Prop_Pew_300_Overturned", vki_mon_pew_overturned, "prop"),
    ("SM_VKI_Prop_FallenBeam", vki_mon_fallen_beam, "prop"),
    ("SM_VKI_Prop_Desk_Scriptorium", vki_mon_desk, "prop"),
    ("SM_VKI_Overlay_GlassShards", vki_mon_glass_shards, "none"),
    ("SM_VKI_Prop_Altar_300_Stripped", vki_mon_altar_stripped, "prop"),
    ("SM_VKI_Prop_CandleStand_Pricket_Fallen", vki_mon_candlestand_fallen, "prop"),
    ("SM_VKI_Prop_Desk_Scriptorium_Fallen", vki_mon_desk_fallen, "prop"),
    ("SM_VKI_Prop_Bookcase_150_Ransacked", vki_mon_bookcase_ransacked, "prop"),
    ("SM_VKI_Prop_Cot_Broken", vki_mon_cot_broken, "prop"),
    ("SM_VKI_Prop_RoofCollapse", vki_mon_roof_collapse, "prop"),
    ("SM_VKI_Overlay_Pages", vki_mon_pages, "none"),
    ("SM_VKI_Overlay_Overgrowth", vki_mon_overgrowth, "none"),
    ("SM_VKI_Overlay_Moss", vki_mon_moss_patch, "none"),
    ("SM_VKI_Prop_Ivy_Wall", vki_mon_ivy_wall, "none"),
    ("SM_VKI_Prop_Ivy_Wall_Tall", vki_mon_ivy_wall_tall, "none"),
    ("SM_VKI_Prop_Font_Broken", vki_mon_font_broken, "prop"),
    ("SM_VKI_Prop_Statue_Saint", vki_mon_saint, "prop"),
    ("SM_VKI_Prop_Statue_Saint_Toppled", vki_mon_saint_toppled, "prop"),
]
VKI_MON_NAMES = [n for n, _, _ in VKI_MON_SPECS]
vki_register([(n, fn, {"grime": gr}, "monastery") for n, fn, gr in VKI_MON_SPECS])
