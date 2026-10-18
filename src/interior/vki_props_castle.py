# ===================== VKI PROPS CASTLE: a castle's great hall (2026-10-18) =====================
# The castle interior's furniture and hangings, for the Ashlar walls (4.5 m). Loaded by vki_ns() after
# vki_props_monastery; uses the home props' boxes and trestle table (vki_props_home), the chapel's candle and cylinder
# (vki_props_chapel), the dungeon kit's rods, lights and gold (vki_props_dungeon) and vki_fam_timber's vki_prism at
# build time. Every top-level name starts with vki_/VKI_ (T18).
# Props: origin at the footprint centre at floor level, back toward local +Y, front toward -Y.
# The lord's arms, shared by the hanging (the textile atlas' hanging_heraldic cell), the banners and the shield:
# per pale gules and azure (CLOTH_A red / CLOTH_B blue), a chevron and three crosses or (gold on the TEXTILE slot).
#   Throne_Castle       0.84 x 0.62 x 2.05 + footstool: a dark-oak chair of estate, gilt finials and roundel, cushion
#   Chair_Carved        0.66 x 0.52 x 1.20: the high table's chairs, dark oak, no gilt
#   Table_High_300      the trestle table (2.70) under a linen cloth that falls 0.30 at the front and ends
#   Hanging_Estate_240  the cloth of estate behind the throne: 2.40 x 1.20 hanging_heraldic on an iron rod, wall_hung
#   Tapestry_300        2.70 x 1.35 tapestry_millefleur on an iron rod (vki_mount_ref "top": rod at H - 0.25)
#   Banner_Castle       a 0.80 x 1.70 swallow-tailed banner in the arms (vki_mount_ref "top": rod at H - 0.35)
#   Chandelier_Ring     an iron ring chandelier 1.16 across, eight candles at 2.60, hung from 4.30 (Ashlar halls)
#   Display_Arms        a heater shield in the arms over two crossed swords, wall_hung at 1.75-2.65
#   Stair_Up_Spiral_300 (+ _Tall) / Stair_Down_Spiral_300 / Floor_300_Spiral_Q**: the newel stair pair (below)
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

VKI_CAS_GOLD = VKI_DPR_GOLD                 # the TEXTILE slot (M_VKI_Gold); hangings on the atlas use bronze instead


def vki_cas_mats(k, gold=True):
    k.slot_mats[WOOD] = "Dark"
    k.slot_mats[CLOTH_A] = "M_VKI_BannerRed"
    k.slot_mats[CLOTH_B] = "M_VKI_BannerBlue"
    if gold:
        vki_dpr_gold_mats(k)


# ---------------------------------------------------------------- seats
def vki_cas_chair(k, back, W, D0, D1, throne=False):
    """a dark-oak chair with a box base: seat top 0.46, arms with knobbed front posts, back stiles to `back` with
    finials, a panelled back and a cresting rail (the throne: a gabled pediment, a gilt roundel, a red cushion)"""
    zs = 0.46
    vki_home_box(k, -W, W, D0 + 0.02, D1 - 0.02, 0.004, zs - 0.055, WOOD, bev=0.015)            # base (its foot
    #                                                                       4 mm up: the posts' feet own the floor plane)
    vki_home_box(k, -W - 0.01, W + 0.01, D0, D1 - 0.03, zs - 0.06, zs, WOOD, bev=0.012)          # seat board
    vki_home_box(k, -W + 0.04, W - 0.04, D0 - 0.005, D0 + 0.03, 0.08, zs - 0.10, WOOD, bev=0.01)  # front rail
    G = VKI_CAS_GOLD if throne else WOOD
    for s in (-1, 1):
        X = lambda a, b: tuple(sorted((s * a, s * b)))                  # x extents measured out from the middle
        vki_home_box(k, *X(W - 0.035, W + 0.025), D0 + 0.03, D1 - 0.04, zs - 0.01, zs + 0.25, WOOD, bev=0.01)  # arm
        vki_home_box(k, *X(W - 0.045, W + 0.035), D0 - 0.015, D1 - 0.03, zs + 0.245, zs + 0.29, WOOD, bev=0.01)
        vki_home_box(k, *X(W - 0.04, W + 0.03), D0 - 0.01, D0 + 0.05, 0.0, zs + 0.25, WOOD, bev=0.01)  # front post
        kv = vki_home_ico(k, (s * (W - 0.005), D0 + 0.02, zs + 0.325), 0.04, G, sub=1)
        k.project(vki_faces_of(kv), G)
        vki_home_box(k, *X(W - 0.05, W + 0.03), D1 - 0.08, D1, 0.0, back, WOOD, bev=0.012)          # back stile
        vki_chp_cyl(k, (s * (W - 0.01), D1 - 0.04, back + 0.065), 0.05, 0.006, 0.14, 4, G, smooth=False,
                    rot=Matrix.Rotation(math.pi / 4, 4, "Z"))                                       # finial
    vki_home_box(k, -W + 0.045, W - 0.045, D1 - 0.06, D1 - 0.025, zs - 0.01, back - 0.14, WOOD, bev=0.008)  # panel
    for x in (-W / 3, W / 3):                                                                   # muntins
        vki_home_box(k, x - 0.025, x + 0.025, D1 - 0.075, D1 - 0.05, zs + 0.02, back - 0.16, WOOD, bev=0.006)
    vki_home_box(k, -W + 0.035, W - 0.035, D1 - 0.08, D1 - 0.005, back - 0.18, back - 0.08, WOOD, bev=0.01)  # crest
    if throne:
        vki_prism(k, [(-W + 0.05, back - 0.085), (W - 0.05, back - 0.085), (0.0, back + 0.17)], D1 - 0.07, D1 - 0.015,
                  WOOD, axis="y", bevel=0.0)                                                     # pediment
        gv = vki_chp_cyl(k, (0.0, D1 - 0.08, zs + 0.78), 0.13, 0.13, 0.016, 16, VKI_CAS_GOLD,
                         rot=Matrix.Rotation(math.pi / 2, 4, "X"))                               # roundel
        vki_home_box(k, -W + 0.05, W - 0.05, D0 + 0.03, D1 - 0.09, zs - 0.005, zs + 0.075, CLOTH_A, bev=0.03)  # cushion
        vki_home_box(k, -0.30, 0.30, -0.66, -0.40, 0.0, 0.14, WOOD, bev=0.015)                  # footstool
        vki_home_box(k, -0.27, 0.27, -0.64, -0.42, 0.135, 0.18, CLOTH_A, bev=0.02)
    return zs


def vki_cas_throne(k):
    zs = vki_cas_chair(k, 1.88, 0.38, -0.30, 0.30, throne=True)
    vki_cas_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_seats=[[0.0, -0.08, zs + 0.07]], vki_seat_z=zs + 0.07,
                  vki_note="the lord's seat: on the dais (Floor_Dais_300), back to the wall, under Hanging_Estate_240; "
                           "sit facing local -Y")


def vki_cas_chair_carved(k):
    zs = vki_cas_chair(k, 1.20, 0.30, -0.26, 0.26)
    vki_cas_mats(k, gold=False)
    vki_home_meta(k, "floor", "furniture", use=[], vki_seats=[[0.0, -0.06, zs]], vki_seat_z=zs,
                  vki_note="the high table's chairs (behind Table_High_300, facing -Y); sit facing local -Y")


# ---------------------------------------------------------------- the high table
def vki_cas_table_high(k):
    """the trestle table (2.70 x 0.90) under a white linen cloth: a 7 mm sheet over the top (2.80 x 1.00) falling
    0.30 at the front (-Y) and both ends, 0.10 at the back (the lord's side); a red runner (the atlas' runner cell)
    down its middle"""
    vki_home_table_trestle(k, 2.70)
    zt = VKI_HOME_TABLE_Z
    hx, hy, t = 1.40, 0.50, 0.007
    z1 = zt + 0.001
    vki_home_box(k, -hx, hx, -hy, hy, z1, z1 + t, CLOTH_B, bev=0.0)                              # the sheet
    o = 0.001                          # the falls hang 1 mm outside the sheet's edges (no shared face plane, T5S)
    vki_home_box(k, -hx - o, hx + o, -hy - o, -hy - o + t, z1 - 0.30, z1 + t - 0.0005, CLOTH_B, bev=0.0)  # front
    vki_home_box(k, -hx - o, hx + o, hy + o - t, hy + o, z1 - 0.10, z1 + t - 0.0005, CLOTH_B, bev=0.0)   # back
    for s in (-1, 1):                                                                            # end falls
        a, b = sorted((s * (hx + o), s * (hx + o - t)))
        vki_home_box(k, a, b, -hy - o + t + 0.0005, hy + o - t - 0.0005, z1 - 0.30, z1 + t - 0.0008, CLOTH_B, bev=0.0)
    rv = vki_home_box(k, -hx + 0.03, hx - 0.03, -0.17, 0.17, z1 + t - 0.001, z1 + t + 0.003, VKI_TEXTILE, bev=0.0)
    vki_textile_map(k, vki_faces_of(rv), "runner", plane=((1, 0, 0), (0, 1, 0)))                   # a red runner
    k.slot_mats[CLOTH_B] = "White"
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[], vki_table_z=round(z1 + t + 0.003, 4), vki_top_rect=[-hx, -hy, hx, hy],
                  vki_fits=["SM_VKI_Prop_Chair_Carved"],
                  vki_note="the lord's table on the dais: Chair_Carved behind it (+Y side), the throne at its middle")


# ---------------------------------------------------------------- hangings
def vki_cas_rod(k, x0, x1, z, y, mi=IRON, knob=BRONZE):
    """an iron rod on two brackets out from the wall face (back y 0), knobbed ends"""
    for x in (x0 + 0.12, x1 - 0.12):
        vki_home_box(k, x - 0.02, x + 0.02, y + 0.015, -0.002, z - 0.02, z + 0.02, mi, bev=0.0)
    vki_chp_cyl(k, ((x0 + x1) / 2, y, z), 0.016, 0.016, x1 - x0, 8, mi, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    for x in (x0, x1):
        kv = vki_home_ico(k, (x, y, z), 0.032, knob, sub=1, smooth=False)


def vki_cas_cloth(k, x0, x1, z0, z1, y, cell, folds=6, depth=0.018):
    """a hanging cloth on the textile atlas: a closed 6 mm sheet pleated in `folds` vertical folds (alternating
    `depth` off the plane at y), mapped once over its face"""
    before = set(k.bm.verts)
    n = folds * 2
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    ys = [y - (depth if i % 2 else 0.0) for i in range(n + 1)]
    t = 0.006
    F = [[k.bm.verts.new((x, yy, z)) for x, yy in zip(xs, ys)] for z in (z0, z1)]
    B = [[k.bm.verts.new((x, yy + t, z)) for x, yy in zip(xs, ys)] for z in (z0, z1)]
    fs = []
    for i in range(n):
        fs.append(k.bm.faces.new((F[0][i], F[0][i + 1], F[1][i + 1], F[1][i])))
        fs.append(k.bm.faces.new((B[0][i + 1], B[0][i], B[1][i], B[1][i + 1])))
        fs.append(k.bm.faces.new((F[0][i + 1], F[0][i], B[0][i], B[0][i + 1])))                 # bottom edge
        fs.append(k.bm.faces.new((F[1][i], F[1][i + 1], B[1][i + 1], B[1][i])))                 # top edge
    for j in (0, n):
        fs.append(k.bm.faces.new((F[0][j], F[1][j], B[1][j], B[0][j])))                         # side edges
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    k.bm.normal_update()
    vki_textile_map(k, fs, cell, plane=((1, 0, 0), (0, 0, 1)))
    return [v for v in k.bm.verts if v not in before]


def vki_cas_hanging_estate(k):
    """the cloth of estate: the lord's arms (hanging_heraldic, 2.40 x 1.20) on an iron rod at 2.84, bottom 1.62;
    hangs behind the throne (whose back is 1.88-2.05: it stands in front of the cloth)"""
    vki_cas_rod(k, -1.30, 1.30, 2.84, -0.07)
    vki_cas_cloth(k, -1.20, 1.20, 1.62, 2.82, -0.09, "hanging_heraldic", folds=5, depth=0.016)
    vki_home_meta(k, "wall_hung", "dressing", back=0.0, use=[], vki_nav="none", vki_mount_zmin=1.6,
                  vki_mount_zmax=2.88, vki_note="authored at its real height (placer z 0): behind the throne, on a Full "
                                                "wall at least 3.0 m (under the Ashlar second course)")


def vki_cas_tapestry(k):
    """a millefleur tapestry 2.70 x 1.35 (tapestry_millefleur) on an iron rod; the rod at local z 0, the cloth below
    (vki_mount_ref "top": placed at H - 0.25, so on Ashlar it clears the second course by hanging 0.08 off the face)"""
    vki_cas_rod(k, -1.43, 1.43, 0.0, -0.07)
    vki_cas_cloth(k, -1.35, 1.35, -1.37, -0.02, -0.09, "tapestry_millefleur", folds=6, depth=0.016)
    vki_home_meta(k, "wall_hung", "dressing", back=0.0, use=[], vki_nav="none", vki_mount_ref="top",
                  vki_mount_offset=0.25, vki_note="rod at the host's H - 0.25 (Ashlar 4.25, Stone / Timber 2.75)")


def vki_cas_charges(k, cx, cy, s, y):
    """the chevron and three crosses or, centred on (cx, cy) at scale s, standing at y (in front of the field)"""
    for sx in (-1, 1):                                                                          # the chevron
        a = (cx + sx * 0.46 * s, cy - 0.30 * s); b = (cx, cy + 0.10 * s)
        d = Vector((b[0] - a[0], b[1] - a[1])).normalized()
        e = 0.05 * s                                                                             # meet past the apex
        vki_dpr_rod(k, (a[0], y - 0.001 * (sx > 0), a[1]), (b[0] + d.x * e, y - 0.001 * (sx > 0), b[1] + d.y * e),
                    0.004, VKI_CAS_GOLD, d=0.11 * s)
    for (px, pz) in ((-0.26, 0.34), (0.26, 0.34), (0.0, -0.42)):                                # the crosses
        x, z = cx + px * s, cy + pz * s
        vki_home_box(k, x - 0.10 * s, x + 0.10 * s, y - 0.003, y + 0.002, z - 0.03 * s, z + 0.03 * s, VKI_CAS_GOLD,
                     bev=0.0)
        vki_home_box(k, x - 0.03 * s, x + 0.03 * s, y - 0.0045, y + 0.0005, z - 0.10 * s, z + 0.10 * s, VKI_CAS_GOLD,
                     bev=0.0)


def vki_cas_banner(k):
    """a swallow-tailed banner 0.80 x 1.70 in the arms: per pale red / blue, the chevron and crosses gilt; a gilt band
    under the rod, tassels at the tails; the rod at local z 0 (vki_mount_ref "top": H - 0.35)"""
    vki_cas_rod(k, -0.50, 0.50, 0.0, -0.07)
    y0, y1 = -0.095, -0.087
    L = 1.70
    vki_prism(k, [(-0.40, -0.02), (0.0, -0.02), (0.0, -L + 0.32), (-0.40, -L)], y0, y1, CLOTH_A, axis="y")
    vki_prism(k, [(0.0, -0.02), (0.40, -0.02), (0.40, -L), (0.0, -L + 0.32)], y0, y1, CLOTH_B, axis="y")
    vki_home_box(k, -0.395, 0.395, y0 - 0.004, y0 + 0.001, -0.14, -0.06, VKI_CAS_GOLD, bev=0.0)        # band
    vki_cas_charges(k, 0.0, -0.80, 0.82, y0 - 0.006)
    for x in (-0.37, 0.37):                                                                       # tassels
        tv = vki_home_ico(k, (x, -0.091, -L - 0.03), 0.03, VKI_CAS_GOLD, scale=(1.0, 1.0, 1.5), sub=1, smooth=False)
    vki_cas_mats(k)
    vki_home_meta(k, "wall_hung", "dressing", back=0.0, use=[], vki_nav="none", vki_mount_ref="top",
                  vki_mount_offset=0.35, vki_note="rod at the host's H - 0.35 (Ashlar 4.15, Stone / Timber 2.65)")


# ---------------------------------------------------------------- light
def vki_cas_chandelier(k):
    """an iron ring chandelier: a ring 1.16 across at 2.60 with eight candles in drip cups, three chains to a crown at
    3.40 and one to a hook at 4.30 (an Ashlar hall's height); one light at the ring. Overhead: never blocks"""
    zr, R = 2.60, 0.56
    vki_home_hoop(k, (0.0, 0.0, zr), R - 0.02, R + 0.02, 0.05, segs=24, mi=IRON)
    lights = []
    for i in range(8):
        a = 2 * math.pi * i / 8
        x, y = R * math.cos(a), R * math.sin(a)
        vki_chp_cyl(k, (x, y, zr + 0.04), 0.045, 0.035, 0.04, 8, IRON)                           # drip cup
        vki_chp_candle(k, (x, y, zr + 0.055), r=0.022, h=0.16, segs=8, flame=(0.06, None))
    for i in range(3):                                                                            # chains
        a = 2 * math.pi * i / 3 + math.pi / 6
        _tube(k, (R * math.cos(a), R * math.sin(a), zr + 0.02), (0.0, 0.0, 3.40), 0.008, IRON, segs=4)
    vki_chp_cyl(k, (0.0, 0.0, 3.40), 0.06, 0.06, 0.05, 8, IRON)                                 # crown
    _tube(k, (0.0, 0.0, 3.42), (0.0, 0.0, 4.30), 0.010, IRON, segs=4)
    lights.append(vki_dpr_light("chandelier", (0.0, 0.0, zr + 0.20), 160.0, VKI_DPR_CANDLE_COL, 7.0, 0.30))
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="none", vki_lights=lights, vki_collider=[],
                  vki_note="hung over a hall's middle (Ashlar 4.5 walls: the hook at 4.30); the ring at 2.60 clears "
                           "the tables and heads")


# ---------------------------------------------------------------- arms
def vki_cas_display_arms(k):
    """a heater shield in the arms (0.56 x 0.70, iron rim) over two crossed swords; wall_hung, authored at its real
    height (1.75-2.65)"""
    cz = 2.20
    for sx in (-1, 1):                                                                            # the swords
        ang = sx * math.radians(38)
        R = Matrix.Translation((0.0, -0.02 if sx < 0 else -0.034, cz)) @ Matrix.Rotation(ang, 4, "Y")  # one in front
        P = lambda z: (R @ Vector((0.0, 0.0, z)))
        # (vki_dpr_rod: w is the depth off the wall for a rod in the wall's plane, d its width in that plane)
        vki_dpr_rod(k, tuple(P(-0.20)), tuple(P(0.55)), 0.012, STEEL, d=0.05)                     # blade
        vki_dpr_rod(k, tuple(P(-0.235)), tuple(P(-0.205)), 0.022, IRON, d=0.22)                   # crossguard
        vki_dpr_rod(k, tuple(P(-0.40)), tuple(P(-0.23)), 0.035, WOOD, d=0.035)                     # grip
        pv = vki_home_ico(k, tuple(P(-0.42)), 0.032, BRONZE, sub=1, smooth=False)                 # pommel
    arc = [(0.28 * math.cos(i / 6 * math.pi / 2), 0.02 - 0.40 * math.sin(i / 6 * math.pi / 2)) for i in range(1, 6)]
    poly_r = [(0.0, 0.32), (0.28, 0.32), (0.28, 0.02)] + arc + [(0.0, -0.38)]      # the right half (convex)
    poly_l = [(-x, z) for x, z in poly_r]
    yb, yf = -0.075, -0.045
    vki_prism(k, [(x, cz + z) for x, z in poly_l], yb, yf, CLOTH_A, axis="y")
    vki_prism(k, [(x, cz + z) for x, z in poly_r], yb, yf, CLOTH_B, axis="y")
    edge = poly_r[1:] + [(-x, z) for x, z in poly_r[1:-1]][::-1]                              # the outline
    for i, (a, b) in enumerate(zip(edge, edge[1:] + edge[:1])):                                   # iron rim
        yr = yb - 0.004 - 0.0012 * (i % 3)                       # neighbours on other planes at the joints (T5S)
        d = Vector((b[0] - a[0], b[1] - a[1])).normalized() * 0.008             # run past the corners (T5S)
        vki_dpr_rod(k, (a[0] - d.x, yr, cz + a[1] - d.y), (b[0] + d.x, yr, cz + b[1] + d.y), 0.024, IRON, d=0.012)
    vki_cas_charges(k, 0.0, cz - 0.02, 0.50, yb - 0.003)
    vki_cas_mats(k)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "wall_hung", "furniture", back=0.0, use=[], vki_nav="none", vki_mount_zmin=1.75,
                  vki_mount_zmax=2.66, vki_note="authored at its real height (placer z 0)")


# ---------------------------------------------------------------- the newel stair (2026-10-18)
# Stair_Up_Spiral_300 (+ _Tall for a 4.5 m storey) / Stair_Down_Spiral_300, the stair pair's contract (vki_links):
# min corner, footprint [0, 3]^2 (2 x 2 cells), the newel at its centre (1.5, 1.5). Stone wedge steps round a DRESS
# newel, each 22 deg (15 deg tall), lapping 3 deg under the next and 0.06 below it, rising counter-clockwise from
# the east (the first nosing on the +X radius faces -Y): the entry is the south-east quadrant, open at floor level
# under the last steps, where the trigger and the arrival are. The steps reach r 1.12 (walls on the west and north
# sides keep their proud line: 1.5 - 1.12 > 0.285; posts at the corner nodes and at (0, 1.5) stay clear).
# Up: the steps to the ceiling plane (the top ones darkened), an iron handrail on balusters up to it.
# Down: the landing (the up stair's last step) flush with the floor in the south-east, ten steps winding down into
# the dark, a VOID disc at -2.40, a stone kerb and an iron rail round the hole but at the landing. Its floor is
# Floor_300_Spiral_Q<a><b> (the room's floor with a round hole 1.18, the Q parity of the footprint's min corner,
# rotation 0), laid by the room under the down stair whatever the stair's rotation (the hole is centred).
VKI_CAS_SPIRAL = dict(c=(1.5, 1.5), newel=0.13, r_in=0.10, R=1.12, lap=3.0, under=0.06, rail_r=1.06, rail_h=0.90,
                      kerb=(1.15, 1.21), kerb_h=0.05, hole=1.18, land=(305.0, 338.0), land_r=1.19, dn=10,
                      void=(-2.40, -2.30), trigger_box=(1.62, 0.35, 2.65, 1.40), spawn=([2.135, -0.75], 180))
VKI_CAS_SPIRAL_KIND = {False: dict(n=15, H=3.0, deg=22.0), True: dict(n=22, H=4.5, deg=15.0)}


def vki_cas_wedge(k, a0, a1, z_top, depth, R, mi, nf=3):
    """a closed wedge step round the newel centre from a0 to a1 (degrees): its inner chord at r_in (buried in the
    newel), its outer edge nf facets of the circle R, top z_top, `depth` thick -> its vertices"""
    S = VKI_CAS_SPIRAL
    cx, cy = S["c"]
    P = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    poly = [P(S["r_in"], a0)] + [P(R, a0 + (a1 - a0) * i / nf) for i in range(nf + 1)] + [P(S["r_in"], a1)]
    vs, fs = vki_prism(k, poly, z_top - depth, z_top, mi, axis="z", bevel=0.0)
    return vs


def vki_cas_spiral_meta(k):
    S = VKI_CAS_SPIRAL
    x0, y0, x1, y1 = S["trigger_box"]
    (sx, sy), sf = S["spawn"]
    k.meta.update(vki_class="link", vki_len=3.0, vki_depth=3.0, vki_rot_allowed=[0, 90, -90, 180],
                  vki_nominal="0,0,3.0,3.0", vki_cells=[[0, 0], [1, 0], [0, 1], [1, 1]], vki_facing_min=60,
                  vki_trigger=[(x0 + x1) / 2, (y0 + y1) / 2, 1.0, x1 - x0, y1 - y0, 2.0],
                  vki_prompt_local=[(x0 + x1) / 2, (y0 + y1) / 2, 1.40], vki_spawn_local=[sx, sy],
                  vki_spawn_facing=sf, vki_uv_lock="local",
                  vki_note="entry: the south-east quadrant (local), keep it open to the room; walls may stand on any "
                           "other side (the steps keep 1.12 from the centre)")


def vki_cas_spiral_up(k, tall=False):
    """the newel stair up: the newel to the ceiling plane, the steps rising counter-clockwise to it (the top ones
    darkened under the ceiling), an iron handrail on balusters while it stays under the ceiling"""
    S = VKI_CAS_SPIRAL; K = VKI_CAS_SPIRAL_KIND[tall]
    n, H, deg = K["n"], K["H"], K["deg"]
    rise = H / n
    cx, cy = S["c"]
    vki_chp_cyl(k, (cx, cy, (H - 0.01) / 2), S["newel"], S["newel"], H - 0.01, 12, DRESS)        # under the top step
    vki_chp_cyl(k, (cx, cy, 0.0515), 0.19, 0.19, 0.097, 12, DRESS)                               # its base, 3 mm up
    for i in range(1, n + 1):
        z = rise * i
        vs = vki_cas_wedge(k, deg * (i - 1) - S["lap"], deg * i, z, rise + S["under"], S["R"], VKI_STONE_BLOCK_IN)
        k.set_dark(vs, 0.6 * vki_smoothstep(H - 0.9, H, z) + 0.05 * (i % 2))
    tops = []
    for i in range(2, n + 1):                                                                     # handrail
        z = rise * i
        if z + S["rail_h"] > H - 0.03:
            break
        a = math.radians(deg * (i - 0.5))
        x, y = cx + S["rail_r"] * math.cos(a), cy + S["rail_r"] * math.sin(a)
        vki_dpr_rod(k, (x, y, z - 0.01), (x, y, z + S["rail_h"]), 0.022, IRON)
        tops.append((x, y, z + S["rail_h"]))
    for a, b in zip(tops[:-1], tops[1:]):
        vki_dpr_rod(k, a, b, 0.035, IRON, d=0.03)
    vki_cas_spiral_meta(k)
    k.meta.update(vki_link="stair_up", vki_pair="SM_VKI_Stair_Down_Spiral_300", vki_rise=round(rise, 4), vki_risers=n,
                  vki_floor_under="room floor laid under the whole footprint (no FLOOR faces)", vki_nav="block",
                  vki_collider=[[0.985, 1.50, H / 2, 1.27, 2.30, H], [2.135, 2.025, H / 2, 1.03, 1.25, H]],
                  vki_collider_note="the stair and the newel; the south-east quadrant (the entry, under the last "
                                    "steps) walks")


def vki_cas_spiral_up_300(k): vki_cas_spiral_up(k)
def vki_cas_spiral_up_tall(k): vki_cas_spiral_up(k, tall=True)


def vki_cas_spiral_down(k):
    """the newel stair down: the landing flush with the floor in the south-east (the up stair's last step), ten steps
    winding down clockwise into the dark, the newel up to a capped post at rail height, a VOID disc under it all, a
    stone kerb and an iron rail round the hole but at the landing"""
    S = VKI_CAS_SPIRAL; K = VKI_CAS_SPIRAL_KIND[False]
    deg, rise = K["deg"], K["H"] / K["n"]
    cx, cy = S["c"]
    vki_chp_cyl(k, (cx, cy, (S["void"][1] + 0.92) / 2), S["newel"], S["newel"], 0.92 - S["void"][1], 12, DRESS)
    vki_chp_cyl(k, (cx, cy, 0.94), 0.17, 0.17, 0.05, 12, DRESS)                                    # the cap
    vs = vki_cas_wedge(k, S["land"][0], S["land"][1], -0.004, rise + S["under"], S["land_r"], VKI_STONE_BLOCK_IN,
                       nf=4)
    k.set_dark(vs, 0.05)
    for j in range(1, S["dn"] + 1):
        a1 = 330.0 - deg * j
        vs = vki_cas_wedge(k, a1 - deg - S["lap"], a1, -rise * j, rise + S["under"], S["R"], VKI_STONE_BLOCK_IN)
        k.set_dark(vs, 0.05 + 0.55 * (j / S["dn"]) ** 1.5)                    # the first steps read in the light
    vv = vki_chp_cyl(k, (cx, cy, sum(S["void"]) / 2), S["hole"] - 0.01, S["hole"] - 0.01, S["void"][1] - S["void"][0],
                     24, VOID)
    # kerb (DRESS segments) and rail, from the landing's east side round to its west side
    k0, k1 = S["kerb"]
    b0, b1 = S["land"][1] + 2.0, S["land"][0] + 360.0 - 2.0
    nseg = 16
    P = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    for i in range(nseg):
        a, b = b0 + (b1 - b0) * i / nseg, b0 + (b1 - b0) * (i + 1) / nseg
        vki_prism(k, [P(k0, a), P(k1, a), P(k1, b), P(k0, b)], -0.02, S["kerb_h"] + 0.002 * (i % 2), DRESS,
                  axis="z", bevel=0.0)
    posts = []
    npost = 10
    for i in range(npost + 1):
        a = b0 + 2.0 + (b1 - b0 - 4.0) * i / npost
        x, y = P(1.18, a)
        vki_dpr_rod(k, (x, y, S["kerb_h"] - 0.01), (x, y, 0.95), 0.03, IRON)
        posts.append((x, y))
    for i, ((xa, ya), (xb, yb)) in enumerate(zip(posts[:-1], posts[1:])):
        for z, w in ((0.95, 0.035), (0.50, 0.02)):
            z += 0.002 * (i % 2)                       # neighbours meet at a post on other planes (T5S)
            vki_dpr_rod(k, (xa, ya, z), (xb, yb, z), w, IRON, d=w)
    vki_cas_spiral_meta(k)
    x0, y0, x1, y1 = 0.33, 0.33, 2.67, 2.67
    k.meta.update(vki_link="stair_down", vki_pair="SM_VKI_Stair_Up_Spiral_300", vki_rise=rise, vki_nav="block",
                  vki_floor_under="Floor_300_Spiral_Q<i mod 2><j mod 2> at the footprint's min corner, rotation 0",
                  vki_collider=[[(x0 + x1) / 2, (1.40 + y1) / 2, 0.5, x1 - x0, y1 - 1.40, 1.0],
                                [(x0 + 1.62) / 2, (y0 + 1.40) / 2, 0.5, 1.62 - x0, 1.40 - y0, 1.0]],
                  vki_collider_note="blocked: the hole but its south-east quadrant (the landing, under the trigger)")


def vki_cas_spiral_floor(qa, qb):
    """Floor_300_Spiral_Q<qa><qb>: the 3.0 floor slab with the down stair's round hole (r 1.18, under the kerb):
    32 rays from the centre to the square (its corners on rays 4, 12, 20, 28), FLOOR world-locked with the Q parity
    offsets of its min corner, so the room's floor runs up to the kerb"""
    def fn(k):
        S = VKI_CAS_SPIRAL
        cx, cy = S["c"]
        n = 32
        bm = k.bm
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            dx, dy = math.cos(a), math.sin(a)
            t = 1.5 / max(abs(dx), abs(dy))
            ring.append(((cx + S["hole"] * dx, cy + S["hole"] * dy), (cx + t * dx, cy + t * dy)))
        T = [(bm.verts.new((p[0], p[1], 0.0)), bm.verts.new((q[0], q[1], 0.0))) for p, q in ring]
        B = [(bm.verts.new((p[0], p[1], VKI_FLOOR_Z0)), bm.verts.new((q[0], q[1], VKI_FLOOR_Z0))) for p, q in ring]
        fs = []
        for i in range(n):
            j = (i + 1) % n
            fs += [bm.faces.new((T[i][0], T[i][1], T[j][1], T[j][0])),          # top
                   bm.faces.new((B[j][0], B[j][1], B[i][1], B[i][0])),          # bottom
                   bm.faces.new((T[j][1], T[i][1], B[i][1], B[j][1])),          # outer side
                   bm.faces.new((T[i][0], T[j][0], B[j][0], B[i][0]))]          # the hole's side
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        bm.normal_update()
        for f in fs:
            nn = f.normal
            off = (0.5 * qa, 0.5 * qb) if abs(nn.z) > 0.7 else ((0.5 * qa, 0.0) if abs(nn.y) > 0.7 else (0.5 * qb, 0.0))
            k.project([f], VKI_FLOOR, offset=off)
        k.meta.update(vki_class="floor", vki_kind="Q300Spiral", vki_len=3.0, vki_q_parity=[qa, qb],
                      vki_place_rule="under a Stair_Down_Spiral_300: its footprint's min corner, node (i, j) with "
                                     "(i mod 2, j mod 2) = (%d, %d), rotation 0" % (qa, qb),
                      vki_hole_r=S["hole"], vki_footprint="0,0,3.0,3.0")
    fn.__name__ = "vki_cas_spiral_floor_q%d%d" % (qa, qb)
    return fn


# ---------------------------------------------------------------- specs
VKI_CAS_SPECS = [
    ("SM_VKI_Prop_Throne_Castle", vki_cas_throne, "prop"),
    ("SM_VKI_Prop_Chair_Carved", vki_cas_chair_carved, "prop"),
    ("SM_VKI_Prop_Table_High_300", vki_cas_table_high, "prop"),
    ("SM_VKI_Prop_Hanging_Estate_240", vki_cas_hanging_estate, "none"),
    ("SM_VKI_Prop_Tapestry_300", vki_cas_tapestry, "none"),
    ("SM_VKI_Prop_Banner_Castle", vki_cas_banner, "none"),
    ("SM_VKI_Prop_Chandelier_Ring", vki_cas_chandelier, "none"),
    ("SM_VKI_Prop_Display_Arms", vki_cas_display_arms, "none"),
    ("SM_VKI_Stair_Up_Spiral_300", vki_cas_spiral_up_300, "prop"),
    ("SM_VKI_Stair_Up_Spiral_300_Tall", vki_cas_spiral_up_tall, "prop"),
    ("SM_VKI_Stair_Down_Spiral_300", vki_cas_spiral_down, "prop"),
] + [("SM_VKI_Floor_300_Spiral_Q%d%d" % (a_, b_), vki_cas_spiral_floor(a_, b_), "floor") for a_ in (0, 1) for b_ in (0, 1)]
VKI_CAS_NAMES = [n for n, _, _ in VKI_CAS_SPECS]
vki_register([(n, fn, {"grime": gr}, "castle") for n, fn, gr in VKI_CAS_SPECS])
