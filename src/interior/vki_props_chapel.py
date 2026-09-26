# ===================== VKI PROPS CHAPEL: the chapel's P1 furniture (§5.4) -- PKG-L =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (§5 conventions, §5.4 chapel, §6 Chapel_F0, §10 amendments).
# Loaded by vki_ns() (VKI_TEXTS, after vki_links, whose helpers vki_lnk_box / vki_lnk_uv / vki_lnk_tops it uses, and
# vki_fam_timber's vki_prism / vki_faces_of). Every top-level name starts with vki_/VKI_ (T18).
# Props: origin at the footprint centre at floor level, back toward local +Y, front (the user's side) toward -Y.
#   Pew_300              2.70 x 0.55 x 0.80 (poppyheads 0.92), floor; seat 0.46 facing -Y, open back (3 raked posts +
#                        one pale HEWN rail 0.72-0.80, raked 10 deg), poppyhead ends, kneeler. Chapel: rot 180.
#   Altar_300            1.80 x 0.90 x 1.05 (cross 1.60), floor (on the dais: z 0.20); DRESS block, linen (CLOTH_A ->
#                        M_VK_Cloth_Cream), TEXTILE altar_frontal, BRONZE cross, 2 built-in bronze candlesticks
#   AltarRail_150        1.50 x 0.30 x 0.75, edge piece: origin at its start node on the dais edge, local x 0..1.5,
#                        y 0.02..0.32; square-ended rails + half posts so pieces chain along x (place at z 0.20)
#   CandleStand_Pricket  dia 0.60 x 1.40, floor: iron tripod, bronze dish, church candle; socket 30 W
#   Lectern              0.60 x 0.60 x 1.30, floor: oak plinth, post, sloped desk with an open book
#   Font                 dia 1.00 x 1.10, floor (hug): octagonal DRESS step, stem and bowl, pale rim, water
#   VotiveRack           1.00 x 0.40 x 1.00, wall_floor (back y 0.20): iron stand, two bronze tiers, 12 votives; 30 W
# Candles: M_VKI_Wax (VKI_WAX) with GLOW flames carrying vki_heat (root 1 .. tip 0); every light has a vki_lights
# socket and a vki_fx "candle" anchor. Build: g["vki_ws_build"]("links", VKI_CHP_NAMES); test: vki_test_pieces -> {}.
import bpy, bmesh, math, json
from mathutils import Vector, Matrix

VKI_CHP_CANDLE = dict(color=[1.0, 0.58, 0.26], range=3.0, flicker=1, shadows=0, radius=0.02)
VKI_CHP_LINEN = "M_VK_Cloth_Cream"         # CLOTH_A per-master override (whitelisted): the altar linen


# ---------------------------------------------------------------- shared helpers
def vki_chp_cyl(k, c, r1, r2, h, segs, mi, smooth=True, rot=None):
    """closed cylinder / frustum centred at c (axis Z unless rot), side faces smooth, caps flat"""
    vs = _cyl(k, c, r1, r2, h, segs, mi, rot=rot)
    k.bm.normal_update()
    ax = (rot.to_3x3() @ Vector((0, 0, 1))) if rot is not None else Vector((0, 0, 1))
    for f in vki_faces_of(vs):
        f.smooth = smooth and abs(f.normal.dot(ax)) < 0.7
    return vs


def vki_chp_flame(k, base, h=0.08, r=0.018, n=6):
    """small closed candle flame (root ring, belly, neck, tip), smooth, GLOW; heat 1 at the root, 0.85 in the
    belly, 0.4 at the neck, 0 at the tip (GlowIn: hot yellow core, orange-red tip)"""
    prof = ((0.0, 0.55, 1.0), (0.30, 1.0, 0.85), (0.65, 0.55, 0.40))
    bx, by, bz = base
    rings = []
    for t, rs, ht in prof:
        rg = []
        for i in range(n):
            a = 2 * math.pi * i / n
            v = k.bm.verts.new((bx + math.cos(a) * r * rs, by + math.sin(a) * r * rs, bz + t * h))
            k.set_heat([v], ht)
            rg.append(v)
        rings.append(rg)
    tip = k.bm.verts.new((bx, by, bz + h))
    k.set_heat([tip], 0.0)
    fs = [k.bm.faces.new(rings[0][::-1])]
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(n):
            fs.append(k.bm.faces.new((A[i], A[(i + 1) % n], B[(i + 1) % n], B[i])))
    for i in range(n):
        fs.append(k.bm.faces.new((rings[-1][i], rings[-1][(i + 1) % n], tip)))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.material_index = GLOW
        f.smooth = True
    k.project(fs, GLOW)
    return [v for rg in rings for v in rg] + [tip]


def vki_chp_candle(k, base, r=0.03, h=0.20, segs=16, flame=(0.08, None)):
    """WAX candle standing on base (x, y, z) with a GLOW flame rooted 4 mm inside its top; returns the light
    socket position (the flame's belly)"""
    x, y, z = base
    vki_chp_cyl(k, (x, y, z + h / 2), r, r, h, segs, VKI_WAX)
    fh, fr = flame
    fr = fr or max(0.012, r * 0.6)
    vki_chp_flame(k, (x, y, z + h - 0.004), fh, fr, n=6)
    return [round(x, 4), round(y, 4), round(z + h + fh * 0.35, 4)]


def vki_chp_light(pos, w, role="candle"):
    return dict(type="POINT", role=role, pos=list(pos), w=w, **VKI_CHP_CANDLE)


def vki_chp_octagon(r, c=(0.0, 0.0), rot=math.pi / 8):
    """8 (x, y) points of a regular octagon (circumradius r); rot pi/8 puts flats on the axes"""
    return [(c[0] + r * math.cos(rot + i * math.pi / 4), c[1] + r * math.sin(rot + i * math.pi / 4)) for i in range(8)]


def vki_chp_lathe(k, prof, n=8, mis=None, rot=math.pi / 8, smooth=False, c=(0.0, 0.0)):
    """closed solid of revolution: prof = [(r, z), ...] from the bottom cap to the top cap (both n-gons); band i
    (between ring i and i+1) takes mis[i] (default the first), caps take mis[0] / mis[-1]. n 8 = octagonal."""
    mis = mis or [DRESS]
    rings = []
    for r, z in prof:
        rings.append([k.bm.verts.new((c[0] + r * math.cos(rot + 2 * math.pi * i / n),
                                      c[1] + r * math.sin(rot + 2 * math.pi * i / n), z)) for i in range(n)])
    fs = [k.bm.faces.new(rings[0][::-1])]
    bands = []
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        band = [k.bm.faces.new((A[i], A[(i + 1) % n], B[(i + 1) % n], B[i])) for i in range(n)]
        bands.append(band)
        fs += band
    top = k.bm.faces.new(rings[-1])
    fs.append(top)
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    k.bm.normal_update()
    k.project([fs[0]], mis[0])
    for j, band in enumerate(bands):
        k.project(band, mis[min(j, len(mis) - 1)])
        for f in band:
            f.smooth = smooth
    k.project([top], mis[-1])
    return rings, bands, fs[0], top


# ---------------------------------------------------------------- Pew_300 (§5.4)
def vki_chp_poppyhead(k, xc, yc, z0):
    """carved finial on a bench end: a neck and three lobes (a trefoil in the end's plane, 0.10 thick, wider than
    the 0.06 board so it reads as a knob from above); widths differ so no two side faces share a plane (T5S)"""
    vki_lnk_box(k, xc - 0.04, xc + 0.04, yc - 0.05, yc + 0.05, z0 - 0.02, z0 + 0.055, WOOD, bev=0.01)
    for dy, dz, r, w in ((0.0, 0.095, 0.055, 0.05), (-0.07, 0.06, 0.042, 0.045), (0.07, 0.06, 0.042, 0.0445)):
        oc = [(yc + dy + p[0], z0 + dz + p[1]) for p in vki_chp_octagon(r)]
        vki_prism(k, oc, xc - w, xc + w, WOOD, axis="x", bevel=0.006)


def vki_chp_pew(k):
    """2.70 x 0.55 pew facing -Y: poppyhead bench ends (x +-1.29..1.35), seat top 0.46 (y -0.20..0.13), three back
    posts and the pale HEWN rail 0.72-0.80 raked 10 deg back, a low stretcher, a middle support, a kneeler at the
    front (top 0.15). Oak (WOOD) throughout, the rail HEWN. From above: two dark rails (seat, kneeler), the pale back
    rail and the end boards with their knobbed finials."""
    L2 = 1.35
    rk = math.radians(10.0)
    # bench ends with the poppyheads
    end = [(-0.20, 0.0), (0.26, 0.0), (0.26, 0.80), (0.02, 0.80), (-0.20, 0.62)]
    for s in (-1, 1):
        x0, x1 = sorted((s * 1.29, s * L2))
        vs, fs = vki_prism(k, end, x0, x1, WOOD, axis="x", bevel=0.012, project=False)
        vki_proj_long(k, fs, WOOD, (0, 0, 1), off=vki_hash_off((x0, 0.0, 0.4)))      # upright grain
        vki_chp_poppyhead(k, s * 1.32, 0.145, 0.80)
    # seat, back posts, rail, stretcher, middle support, kneeler (+ its feet inside the ends)
    vki_lnk_box(k, -1.295, 1.295, -0.20, 0.13, 0.38, 0.46, WOOD, bev=0.015)
    for x in (-0.65, 0.0, 0.65):
        c = Vector((x, 0.105, 0.44)) + Matrix.Rotation(-rk, 3, "X") @ Vector((0, 0, 0.16))
        k.box(tuple(c), (0.05, 0.045, 0.32), WOOD, rot=(-rk, 0, 0), bevel=0.01)
    c = Vector((0.0, 0.105, 0.44)) + Matrix.Rotation(-rk, 3, "X") @ Vector((0, 0, 0.32))
    k.box(tuple(c), (2.59, 0.07, 0.08), HEWN, rot=(-rk, 0, 0), bevel=0.015)
    vki_lnk_box(k, -1.295, 1.295, 0.16, 0.22, 0.10, 0.18, WOOD, bev=0.012)
    vki_lnk_box(k, -0.03, 0.03, -0.17, 0.10, 0.0, 0.385, WOOD, bev=0.01)
    vki_lnk_box(k, -1.325, 1.325, -0.275, -0.175, 0.07, 0.15, WOOD, bev=0.012)
    for s in (-1, 1):
        x0, x1 = sorted((s * 1.235, s * 1.285))
        vki_lnk_box(k, x0, x1, -0.265, -0.185, 0.0, 0.075, WOOD, bev=0.008)
    k.meta.update(vki_class="prop", vki_kind="Pew", vki_mount="floor", vki_tier="furniture", vki_seat_z=0.46,
                  vki_use=[[-0.9, -0.50, 0], [0.0, -0.50, 0], [0.9, -0.50, 0]],
                  vki_use_note="stand points in front of the seat, facing the pew (local compass 0 = +Y); the "
                               "sitter faces local -Y",
                  vki_note="chapel: rot 180 so the seat faces north (the altar)")


# ---------------------------------------------------------------- Altar_300 (§5.4)
def vki_chp_candlestick(k, x, y, z0):
    """built-in bronze candlestick (0.30 tall, like §5.2 Candlestick) with its candle and flame; returns the
    light socket position"""
    for (cz, r1, r2, h, segs) in ((0.0125, 0.07, 0.07, 0.025, 16), (0.05, 0.065, 0.024, 0.05, 16),
                                  (0.1575, 0.017, 0.017, 0.205, 10), (0.14, 0.034, 0.034, 0.04, 12),
                                  (0.2575, 0.055, 0.055, 0.015, 16), (0.285, 0.026, 0.034, 0.04, 12)):
        vki_chp_cyl(k, (x, y, z0 + cz), r1, r2, h, segs, BRONZE)
    return vki_chp_candle(k, (x, y, z0 + 0.30), r=0.03, h=0.20, segs=16, flame=(0.08, 0.018))


def vki_chp_altar(k):
    """1.80 x 0.90 stone altar (front -Y): DRESS block (x +-0.84, y -0.36..0.40) under a linen-covered mensa slab
    (CLOTH_A -> cream linen, x +-0.90, y +-0.45, z 0.93-1.065), the TEXTILE altar_frontal hanging on the front
    (u along x, v up; its gold superfrontal just under the linen's edge), a bronze cross and two built-in bronze
    candlesticks on the mensa. Two 15 W candle sockets."""
    zt = 1.065
    vki_lnk_box(k, -0.84, 0.84, -0.36, 0.40, 0.0, 0.935, DRESS, bev=0.02)
    vki_lnk_box(k, -0.90, 0.90, -0.45, 0.45, 0.93, zt, CLOTH_A, bev=0.012)
    vs = vki_lnk_box(k, -0.82, 0.82, -0.378, -0.362, 0.035, 0.925, VKI_TEXTILE, bev=0.003)
    vki_textile_map(k, vki_faces_of(vs), "altar_frontal", plane=((1, 0, 0), (0, 0, 1)))
    # cross on a stepped base at the back
    vki_lnk_box(k, -0.11, 0.11, 0.21, 0.39, zt - 0.005, zt + 0.035, BRONZE, bev=0.008)
    vki_lnk_box(k, -0.065, 0.065, 0.245, 0.355, zt + 0.03, zt + 0.075, BRONZE, bev=0.008)
    vki_lnk_box(k, -0.027, 0.027, 0.273, 0.327, zt + 0.07, zt + 0.55, BRONZE, bev=0.008)
    vki_lnk_box(k, -0.18, 0.18, 0.274, 0.326, zt + 0.36, zt + 0.415, BRONZE, bev=0.008)
    lights = [vki_chp_light(vki_chp_candlestick(k, s * 0.58, 0.25, zt - 0.003), 15.0) for s in (-1, 1)]
    k.slot_mats[CLOTH_A] = VKI_CHP_LINEN
    k.meta.update(vki_class="prop", vki_kind="Altar", vki_mount="floor", vki_tier="furniture", vki_lights=lights,
                  vki_fx=[dict(fx="candle", pos=L["pos"]) for L in lights], vki_mensa_z=zt,
                  vki_use=[[0.0, -0.80, 0]], vki_textile="altar_frontal",
                  vki_note="chapel: (6.0, 7.5) rot 0 on the dais (z 0.20), vki_warn_ok='window' on the instance")


# ---------------------------------------------------------------- AltarRail_150 (§5.4)
def vki_chp_altar_rail(k):
    """communion rail chain piece: local x 0..1.5 (origin at its start node on the dais edge), y 0.02..0.32, z 0..0.75
    (stands on the dais: place at z 0.20). A broad pale HEWN top board (y 0.04-0.30, chamfered), an oak under-rail
    and sill, all square-ended prisms so the chain has no joint gaps; 8 balusters at 0.1875 spacing (uniform across
    joints) and half posts at both ends (a full 0.10 post at every joint). At a wall the end is let into the
    wall / respond (see vki_edge_let_in)."""
    L = 1.5
    top = [(0.04, 0.69), (0.30, 0.69), (0.30, 0.735), (0.285, 0.75), (0.055, 0.75), (0.04, 0.735)]
    vs, fs = vki_prism(k, top, 0.0, L, HEWN, axis="x", project=False)
    vki_lnk_uv(k, fs, HEWN, (1, 0, 0), (0, 1, 0), c=(0.0, 0.17, 0.72))
    for f in fs:
        if abs(f.normal.z) < 0.3 and abs(f.normal.y) > 0.3:
            vki_lnk_uv(k, [f], HEWN, (1, 0, 0), (0, 0, 1), c=(0.0, 0.17, 0.72))
    for prof, off in (([(0.12, 0.62), (0.22, 0.62), (0.22, 0.69), (0.12, 0.69)], 0.3),
                      ([(0.08, 0.0), (0.26, 0.0), (0.26, 0.055), (0.24, 0.07), (0.10, 0.07), (0.08, 0.055)], 0.6)):
        vs, fs = vki_prism(k, prof, 0.0, L, WOOD, axis="x", project=False)
        vki_proj_long(k, fs, WOOD, (1, 0, 0), off=(off, 0.0))
    for i in range(8):
        x = 0.09375 + 0.1875 * i
        vki_lnk_box(k, x - 0.0225, x + 0.0225, 0.1475, 0.1925, 0.065, 0.625, WOOD, bev=0.006)
    for x0, x1 in ((0.0, 0.05), (L - 0.05, L)):
        vki_lnk_box(k, x0, x1, 0.10, 0.24, 0.07, 0.62, WOOD, bev=0.0)
    k.meta.update(vki_class="prop", vki_kind="AltarRail", vki_len=L, vki_mount="floor", vki_tier="furniture",
                  vki_origin="start_node", vki_edge=1, vki_chain="local x: pieces butt at their end nodes",
                  vki_place_z=0.20, vki_edge_let_in=0.32,
                  vki_use=[[0.375, -0.35, 0], [1.125, -0.35, 0]],
                  vki_note="place along the dais edge at z 0.20 (rot 0: rail on the dais, kneelers on the nave "
                           "side); at a wall line the first / last 0.32 m is let into the wall / respond (T12 clash "
                           "exemption for vki_edge pieces)")


# ---------------------------------------------------------------- CandleStand_Pricket (§5.4)
def vki_chp_candlestand(k):
    """floor pricket stand dia 0.60 x 1.40: iron tripod (legs from a hub at 0.26 to pads at radius 0.26), iron stem
    with a knop, a bronze dish at 1.08-1.12, a church candle 0.28 tall and its flame; socket 30 W"""
    for i in range(3):
        a = math.pi / 2 + 2 * math.pi * i / 3
        p = Vector((0.255 * math.cos(a), 0.255 * math.sin(a), 0.03))
        _tube(k, (0.0, 0.0, 0.27), tuple(p), 0.016, IRON, segs=8)
        vki_lnk_box(k, p.x - 0.035, p.x + 0.035, p.y - 0.035, p.y + 0.035, 0.0, 0.03, IRON, bev=0.008)
    vki_chp_cyl(k, (0, 0, 0.27), 0.05, 0.05, 0.08, 12, IRON)
    vki_chp_cyl(k, (0, 0, 0.68), 0.022, 0.022, 0.80, 10, IRON)
    vki_chp_cyl(k, (0, 0, 0.62), 0.045, 0.045, 0.06, 12, IRON)
    vki_chp_cyl(k, (0, 0, 1.075), 0.04, 0.03, 0.03, 12, IRON)
    vki_chp_cyl(k, (0, 0, 1.10), 0.10, 0.16, 0.04, 16, BRONZE)
    pos = vki_chp_candle(k, (0, 0, 1.115), r=0.045, h=0.28, segs=16, flame=(0.10, 0.022))
    L = vki_chp_light(pos, 30.0)
    k.meta.update(vki_class="prop", vki_kind="CandleStand", vki_mount="floor", vki_tier="furniture",
                  vki_lights=[L], vki_fx=[dict(fx="candle", pos=pos)], vki_use=[[0.0, -0.55, 0]])


# ---------------------------------------------------------------- Lectern (§5.4)
def vki_chp_lectern(k):
    """oak lectern 0.60 x 0.60 x 1.30: stepped plinth, chamfered post, a desk 0.58 x 0.46 sloping 30 deg up toward
    +Y (the reader stands at -Y) with a book stop and an open book (PAPER pages, HIDE cover), so the camera looks
    onto the pages"""
    vki_lnk_box(k, -0.24, 0.24, -0.24, 0.24, 0.0, 0.10, WOOD, bev=0.015)
    vki_lnk_box(k, -0.14, 0.14, -0.14, 0.14, 0.095, 0.19, WOOD, bev=0.015)
    vki_lnk_box(k, -0.05, 0.05, -0.05, 0.05, 0.185, 1.02, WOOD, bev=0.015)
    ang = math.radians(30.0)
    R = Matrix.Rotation(ang, 3, "X")
    c0 = Vector((0.0, 0.02, 1.14))
    k.box(tuple(c0), (0.58, 0.46, 0.04), WOOD, rot=(ang, 0, 0), bevel=0.012)
    k.box(tuple(c0 + R @ Vector((0.0, -0.225, 0.035))), (0.56, 0.025, 0.035), HEWN, rot=(ang, 0, 0), bevel=0.006)
    zu = lambda y: 1.1227 + (y - 0.03) * math.tan(ang) + 0.015          # 1.5 cm into the desk's underside
    vki_prism(k, [(-0.045, 0.99), (0.045, 0.99), (0.045, zu(0.045)), (-0.045, zu(-0.045))], -0.09, 0.09, WOOD,
              axis="x", bevel=0.01)
    # open book: leather cover under two page blocks, the pages tilted a little toward the spine
    k.box(tuple(c0 + R @ Vector((0.0, 0.0, 0.024))), (0.46, 0.33, 0.012), HIDE, rot=(ang, 0, 0), bevel=0.004)
    for s in (-1, 1):
        cp = c0 + R @ Vector((s * 0.108, 0.0, 0.045))
        k.box(tuple(cp), (0.205, 0.31, 0.026), PAPER, rot=(ang, s * math.radians(4.0), 0), bevel=0.004)
    k.meta.update(vki_class="prop", vki_kind="Lectern", vki_mount="floor", vki_tier="furniture",
                  vki_use=[[0.0, -0.50, 0]])


# ---------------------------------------------------------------- Font (§5.4)
def vki_chp_font(k):
    """octagonal stone font dia 1.00 x 1.10: DRESS step (r 0.50) and stem, a tapering bowl with a pale StoneBlockIn
    rim (the camera reads a pale octagonal ring) around water (WATER) at z 1.00"""
    vki_chp_lathe(k, [(0.54, 0.0), (0.54, 0.12)], mis=[DRESS])          # 1.00 across the flats
    vki_chp_lathe(k, [(0.43, 0.115), (0.43, 0.20)], mis=[DRESS])
    vki_chp_lathe(k, [(0.20, 0.195), (0.20, 0.57)], mis=[DRESS])
    rings, bands, bot, top = vki_chp_lathe(k, [(0.29, 0.55), (0.46, 0.95), (0.46, 1.10), (0.37, 1.10), (0.37, 1.00)],
                                           mis=[DRESS, DRESS, VKI_STONE_BLOCK_IN, DRESS, WATER])
    for v in rings[4]:
        k.set_dark([v], 0.25)
    k.meta.update(vki_class="prop", vki_kind="Font", vki_mount="floor", vki_tier="furniture", vki_water_z=1.00,
                  vki_use=[[0.0, -0.75, 0]], vki_note="chapel: (0.75, 0.75) with hug")


# ---------------------------------------------------------------- VotiveRack (§5.4)
VKI_CHP_VOTIVE_H = (0.10, 0.07, 0.12, 0.09, 0.13, 0.08, 0.11, 0.06, 0.12, 0.10, 0.08, 0.13)


def vki_chp_votive(k):
    """wall-backed votive stand 1.00 x 0.40 x 1.00 (back y 0.20): iron uprights and rails, two bronze tiers
    (front 0.78, back 0.90) with lips, 12 votive candles of burnt-down heights with flames; one 30 W socket"""
    for x in (-0.47, 0.47):
        for y in (-0.16, 0.16):
            vki_lnk_box(k, x - 0.015, x + 0.015, y - 0.015, y + 0.015, 0.0, 0.93 if y > 0 else 0.81, IRON, bev=0.004)
        vki_lnk_box(k, x - 0.012, x + 0.012, -0.17, 0.17, 0.10, 0.13, IRON, bev=0.004)
    for y0, y1, z in ((-0.185, 0.0, 0.78), (0.0, 0.185, 0.90)):
        vki_lnk_box(k, -0.49, 0.49, y0, y1, z - 0.025, z, BRONZE, bev=0.006)
        vki_lnk_box(k, -0.49, 0.49, y0 + 0.004, y0 + 0.019, z - 0.005, z + 0.025, BRONZE, bev=0.004)
    vki_lnk_box(k, -0.495, 0.495, 0.17, 0.20, 0.90, 0.96, IRON, bev=0.006)
    socks = []
    for i in range(12):
        row, col = divmod(i, 6)
        x = -0.375 + 0.15 * col + (0.075 if row else 0.0)          # the back row staggered
        y, z = (-0.09, 0.78) if row == 0 else (0.09, 0.90)
        socks.append(vki_chp_candle(k, (x, y, z - 0.004), r=0.024, h=VKI_CHP_VOTIVE_H[i], segs=8,
                                    flame=(0.05, 0.012)))
    pos = [0.0, 0.0, 1.06]
    k.meta.update(vki_class="prop", vki_kind="VotiveRack", vki_mount="wall_floor", vki_back_y=0.20,
                  vki_tier="furniture", vki_lights=[vki_chp_light(pos, 30.0)],
                  vki_fx=[dict(fx="candle", pos=p) for p in socks], vki_use=[[0.0, -0.50, 0]],
                  vki_note="chapel: (11.25, 3.75) rot -90 against the east wall")


# ---------------------------------------------------------------- workshop rigs (renders of the package)
def vki_chp_coll(name, parent=None):
    """collection WS_vki_links_<name> (a child of the workshop scene, or of `parent`), emptied"""
    sc, coll, asm = vki_ws("links")
    cn = "WS_vki_links_" + name
    c = bpy.data.collections.get(cn) or bpy.data.collections.new(cn)
    par = parent or sc.collection
    for p in [sc.collection] + list(sc.collection.children_recursive):
        if p != par and c.name in p.children:
            p.children.unlink(c)
    if c.name not in par.children:
        par.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o)
    return sc, c


def vki_chp_tidy(y=-40.0, gap=1.0):
    """workshop layout for the coordinator's live board: all PKG-L masters in ONE row along x at y (sorted as
    built, spaced by their widths + gap); the test collections stay apart (stair rig x 0..40.5 / y 0..7.5, catalog
    x 0..15 / y -21..-9, nave x 60..72 / y 0..9); lights live inside their test collection"""
    x = 0.0
    for n in VKI_LNK_NAMES + VKI_CHP_NAMES:
        o = bpy.data.objects.get(n)
        if o is None:
            continue
        bb = vki_local_box(o)
        o.location = (x - bb[0], y - (bb[1] + bb[4]) / 2, 0.0)
        x += (bb[3] - bb[0]) + gap
    return round(x, 2)


VKI_CHP_CAT_Y = -21.0                                   # the catalog (x 0..15, y -21..-9) sits south of the rig


def vki_chp_catalog():
    """every PKG-L chapel / overlay piece at x 0..15, y -21..-9 (FlagWarm floors): north row pews (rot 180 as in the
    chapel and rot 0), two daises (Flag) with a 4-piece rail chain, the altar, a pricket and the lectern on them;
    south row the font, the votive rack against a Cut wall, runners chained (150 | 300, rot 90) and a window pool
    under a Timber window. Returns (objs, cam dict)."""
    sc, c = vki_chp_coll("Catalog")
    y0 = VKI_CHP_CAT_Y
    out = []
    P = lambda n, x, y, r=0, **kw: out.append(vki_place(c, n, x, y0 + y, r, **kw)) or out[-1]
    fl = {"floor": "FlagWarm"}
    for x, y in ((0, 0), (6, 0), (0, 6)):
        P("SM_VKI_Floor_600", x, y, style=fl, walls=[])
    for x, y in ((12, 0), (12, 3), (6, 6), (9, 6), (12, 6), (12, 9)):
        P("SM_VKI_Floor_300", x, y, style=fl, walls=[])
    for x in (6.0, 9.0):
        P("SM_VKI_Floor_Dais_300", x, 9.0, style={"floor": "Flag"}, walls=[])
    P("SM_VKI_Prop_Pew_300", 2.25, 10.5, 180, walls=[]); P("SM_VKI_Prop_Pew_300", 2.25, 7.5, 0, walls=[])
    for x in (6.0, 7.5, 9.0, 10.5):
        P("SM_VKI_Prop_AltarRail_150", x, 9.0, 0, z=0.20, walls=[])
    P("SM_VKI_Prop_Altar_300", 9.0, 10.5, 0, z=0.20, walls=[])
    P("SM_VKI_Prop_CandleStand_Pricket", 6.75, 11.25, 0, z=0.20, walls=[])
    P("SM_VKI_Prop_Lectern", 11.25, 10.5, 0, z=0.20, walls=[])
    W = "SM_VKI_Wall_Timber_"; Pt = "SM_VKI_Post_Timber_"
    w1 = P(W + "Plain_150A_Cut", 3.0, 6.0, 0, walls=[])
    P(Pt + "Mid_Cut", 3.0, 6.0, walls=[]); P(Pt + "Mid_Cut", 4.5, 6.0, walls=[])
    P("SM_VKI_Prop_VotiveRack", 3.75, 5.25, 0, walls=[w1])
    w2 = P(W + "Window_150_Full", 12.0, 6.0, 0, walls=[])
    P(Pt + "Mid_Full", 12.0, 6.0, walls=[]); P(Pt + "Mid_Full", 13.5, 6.0, walls=[])
    P("SM_VKI_FX_WindowPool", 12.0, 6.0, 0, walls=[])
    P("SM_VKI_Prop_Font", 1.5, 3.0, walls=[])
    P("SM_VKI_Runner_150", 7.5, 2.25, 90, walls=[]); P("SM_VKI_Runner_300", 7.5, 4.5, 90, walls=[])
    _, cl = vki_chp_coll("CatalogLights", parent=c)
    vki_lt_lights(sc, c, cl)
    return out, dict(D=20.0, target=(7.5, y0 - 0.5 + 0.2856 * 20.0, 0.0))


VKI_CHP_NAVE_X = 60.0                                   # the nave rig stands east of everything else


def vki_chp_nave(night=False):
    """the §6 Chapel_F0 arrangement at x0 = 60 (12 x 9): nave FlagWarm, dais rows 4-5 (Flag), pews at rot 180,
    altar rail chain with the aisle gap, altar / prickets / lectern on the dais, font (hug), votive rack on the east
    wall, runners up the aisle (rot 90). Walls: Timber stand-ins for the Ashlar family (PKG-W builds it in parallel;
    Timber Window_150 stand in for the lancets): Full W / N / E with Full SW / SE corner posts (the chapel's
    pillars), Cut south wall with the 3 m exit gap (Mid posts at its free ends), Mid posts at y 3 / 6 (the
    responds). Window spots and candle sockets become lights (vki_lt_lights). Returns (objs, cam dict)."""
    sc, c = vki_chp_coll("Nave")
    _, cl = vki_chp_coll("NaveLights", parent=c)
    x0 = VKI_CHP_NAVE_X
    W = "SM_VKI_Wall_Timber_"; Pt = "SM_VKI_Post_Timber_"
    wst = {"wall_a": "PlasterWhite"}
    out = []
    P = lambda n, x, y, r=0, **kw: out.append(vki_place(c, n, x0 + x, y, r, walls=[], **kw)) or out[-1]
    for n_, y in (("Plain_150A_Full", 0.0), ("Window_150_Full", 1.5), ("Plain_150A_Full", 3.0),
                  ("Window_150_Full", 4.5), ("Plain_300_Full", 6.0)):
        P(W + n_, 0.0, y, 90, style=wst)
    for n_, y in (("Plain_300_Full", 9.0), ("Window_150_Full", 6.0), ("Plain_150A_Full", 4.5),
                  ("Window_150_Full", 3.0), ("Plain_150A_Full", 1.5)):
        P(W + n_, 12.0, y, -90, style=wst)
    for n_, x in (("Plain_300_Full", 0.0), ("Window_150_Full", 3.0), ("Window_150_Full", 4.5),
                  ("Window_150_Full", 6.0), ("Window_150_Full", 7.5), ("Plain_300_Full", 9.0)):
        P(W + n_, x, 9.0, 0, style=wst)
    for n_, x in (("Plain_150A_Cut", 12.0), ("Window_150_Cut", 10.5), ("Plain_150A_Cut", 9.0),
                  ("Plain_150A_Cut", 4.5), ("Window_150_Cut", 3.0), ("Plain_150A_Cut", 1.5)):
        P(W + n_, x, 0.0, 180, style=wst)
    for x, y in ((0, 0), (12, 0), (0, 9), (12, 9)):
        P(Pt + "Corner_Full", x, y)
    for x, y in ((0, 3.0), (0, 6.0), (12, 3.0), (12, 6.0)):
        P(Pt + "Mid_Full", x, y, 90)
    for x in (4.5, 7.5):
        P(Pt + "Mid_Cut", x, 0.0)
    for x in (0.0, 6.0):
        P("SM_VKI_Floor_600", x, 0.0, style={"floor": "FlagWarm"})
    for x in (0.0, 3.0, 6.0, 9.0):
        P("SM_VKI_Floor_Dais_300", x, 6.0, style={"floor": "Flag"})
    for x in (3.0, 9.0):
        for y in (2.25, 3.75, 5.25):
            P("SM_VKI_Prop_Pew_300", x, y, 180)
    for x in (0.0, 1.5, 3.0, 7.5, 9.0, 10.5):
        P("SM_VKI_Prop_AltarRail_150", x, 6.0, 0, z=0.20)
    P("SM_VKI_Prop_Altar_300", 6.0, 7.5, 0, z=0.20, vki_warn_ok="window")
    for x in (3.75, 8.25):
        P("SM_VKI_Prop_CandleStand_Pricket", x, 8.25, 0, z=0.20)
    P("SM_VKI_Prop_Lectern", 8.25, 6.75, 0, z=0.20)
    P("SM_VKI_Runner_150", 6.0, 2.25, 90); P("SM_VKI_Runner_300", 6.0, 4.5, 90)
    walls = [o for o in out if o.get("vki_class") == "wall"]
    out.append(vki_place(c, "SM_VKI_Prop_Font", x0 + 0.75, 0.75, 0, walls=walls, hug=True))
    out.append(vki_place(c, "SM_VKI_Prop_VotiveRack", x0 + 11.25, 3.75, -90, walls=walls))
    for o in [o for o in walls if "Window_150_Full" in o.get("vki_piece", "")]:
        dz = 0.20 if abs(o.location.y - 9.0) < 1e-6 else 0.0          # the north windows light the dais
        r = round(math.degrees(o.rotation_euler.z))
        out.append(vki_place(c, "SM_VKI_FX_WindowPool", o.location.x, o.location.y, r, z=dz, walls=[]))
    for o in list(cl.objects):
        bpy.data.objects.remove(o)
    vki_lt_lights(sc, c, cl)
    f = vki_fit_camera((x0, 0.0, x0 + 12.0, 9.0), "Ashlar")
    return out, dict(D=f["D"], target=f["target"])


VKI_CHP_SPECS = [
    ("SM_VKI_Prop_Pew_300", vki_chp_pew),
    ("SM_VKI_Prop_Altar_300", vki_chp_altar),
    ("SM_VKI_Prop_AltarRail_150", vki_chp_altar_rail),
    ("SM_VKI_Prop_CandleStand_Pricket", vki_chp_candlestand),
    ("SM_VKI_Prop_Lectern", vki_chp_lectern),
    ("SM_VKI_Prop_Font", vki_chp_font),
    ("SM_VKI_Prop_VotiveRack", vki_chp_votive),
]
VKI_CHP_NAMES = [n for n, _ in VKI_CHP_SPECS]
vki_register([(n, fn, {"grime": "prop"}, "links") for n, fn in VKI_CHP_SPECS])
