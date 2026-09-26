# ===================== VKI PROPS TAVERN: the tavern set and its lights (§5.2 P1) -- 10 masters =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md §5 (conventions), §5.2, §10. Loaded by vki_ns() (VKI_TEXTS, after
# vki_props_home); vki_props_smithy (loaded next) reuses the vki_tav_* helpers. Every top-level name starts with vki_.
# Props: origin at the footprint centre at floor level, back toward local +Y, front toward -Y (§2.1, §5).
#   Bar_Counter_150   chain piece, tops / nosing / foot rail / board rhythm butt at local x +-0.75 (UV tile 1.5)
#   Bar_End_150       local x -0.45..0.75, its +X end butts a counter's -X end; 0.8 lift flap, hinge_axis "local Y"
#   CaskRack_150      two casks on saddles, BRONZE taps toward -Y over one drip tub (WATER -> M_VKI_Ale)
#   Table_Barrel      a standing barrel with a round plank top at 1.05
#   TableDress_Tavern_A / B (Table_Trestle_300, z 0.80) and C (Table_Barrel, z 1.05): tankards 0.16 with WAX foam
#                     domes or an ale surface (WATER -> M_VKI_Ale), goods-atlas food, a built-in Candle_Plate
#   Lantern_Wall      wall_hung (z 1.90-2.45), GLOW panes with vki_heat, 60 W socket
#   Candle_Plate / Candlestick   WAX candles, GLOW flames (vki_heat), 15 W sockets, FX "candle"
# Build: g["vki_ws_build"]("tavern", VKI_TAV_NAMES); test: g["vki_test_pieces"](VKI_TAV_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_TAV_SEG = 16                    # round things (§5)
VKI_TAV_X = Vector((1.0, 0.0, 0.0)); VKI_TAV_Y = Vector((0.0, 1.0, 0.0)); VKI_TAV_Z = Vector((0.0, 0.0, 1.0))
VKI_TAV_TOP_TILE = 1.5              # counter tops / nosing: 1.5 / tile is an integer -> UVs continue across the chain
VKI_TAV_CANDLE_COL = [1.0, 0.64, 0.32]
VKI_TAV_LANTERN_COL = [1.0, 0.60, 0.28]
VKI_TAV_CANDLE_W = 15.0
VKI_TAV_LANTERN_W = 60.0
# M_VKI_Ale (.45, .28, .08) rendered as a bright mustard disc in the tankards and the drip tub (catalog r1); the ale
# surfaces get vki_dark (vertex colour) so they read as dark amber liquid inside a vessel
VKI_TAV_ALE_DARK = 0.5


# ---------------------------------------------------------------- generic helpers (also used by vki_props_smithy)
def vki_tav_faces(vs):
    return list({f for v in vs for f in v.link_faces})


def vki_tav_new(k, before):
    """vertices created since `before` (a set of the bmesh's vertices)"""
    return [v for v in k.bm.verts if v not in before]


def vki_tav_uv(k, faces, mi, U, V, tile=None, off=(0.0, 0.0)):
    """planar UVs u = p.U / tile, v = p.V / tile (+ off); sets the material"""
    tt = tile or vki_tile(mi)
    U = Vector(U); V = Vector(V)
    for f in faces:
        f.material_index = mi
        for l in f.loops:
            p = l.vert.co
            l[k.uv].uv = (p.dot(U) / tt + off[0], p.dot(V) / tt + off[1])


def vki_tav_board_uv(k, faces, mi, A, tile=None, off=(0.0, 0.0), edge_mi=None, edge_ok=None):
    """UVs for a board / top whose long direction is the horizontal vector A. T_VK_Planks runs its planks along v,
    the WOOD / HEWN grain runs along u: up / down faces get the planks (or grain) along A, side faces along their
    edge. Upward chamfers (0.3 < n.z < 0.97) switch to edge_mi (HEWN: the pale edge line of §5) where edge_ok(n)."""
    A = Vector(A).normalized(); B = VKI_TAV_Z.cross(A).normalized()
    for f in faces:
        f.normal_update()
        n = f.normal
        m = mi
        if edge_mi is not None and 0.3 < n.z < 0.97 and (edge_ok is None or edge_ok(n)):
            m = edge_mi
        if abs(n.z) >= 0.97:
            U, V = (B, A) if m == PLANKS else (A, B)
        else:
            E = VKI_TAV_Z.cross(n)
            if E.length < 1e-6:
                E = A.copy()
            E.normalize()
            W = n.cross(E).normalized()
            U, V = (W, E) if m == PLANKS else (E, W)
        vki_tav_uv(k, [f], m, U, V, tile=tile if m == mi else None, off=off)


def vki_tav_slab(k, c, size, mi=None, bevel=0.02, edge_mi=HEWN, along=None, tile=None, off=None, edge_ok=None,
                 rot_z=0.0):
    """a board / top: bevelled box, planks (PLANKS) or grain (WOOD) along its long horizontal axis (or `along`),
    upward chamfers HEWN (pale edge bevels, §5; edge_ok(n) picks which edges, None = all). Returns the verts."""
    mi = PLANKS if mi is None else mi
    vs = list(set(k.box(c, size, mi, bevel=bevel, rot=(0.0, 0.0, rot_z))))
    if along is None:
        along = Vector((math.cos(rot_z), math.sin(rot_z), 0.0)) if size[0] >= size[1] else \
            Vector((-math.sin(rot_z), math.cos(rot_z), 0.0))
    vki_tav_board_uv(k, vki_tav_faces(vs), mi, along, tile=tile, off=off if off is not None else vki_hash_off(c),
                     edge_mi=edge_mi, edge_ok=edge_ok)
    return vs


def vki_tav_hewn_tops(k, vs, ok=None):
    """re-map the upward chamfers (0.3 < n.z < 0.97) of a member (e.g. a k.box upright, whose grain stays along its
    long axis) as HEWN with the grain along each edge: the pale top outline of §5"""
    for f in vki_tav_faces(vs):
        f.normal_update()
        n = f.normal
        if 0.3 < n.z < 0.97 and (ok is None or ok(n)):
            E = VKI_TAV_Z.cross(n)
            E = E.normalized() if E.length > 1e-6 else VKI_TAV_X.copy()
            vki_tav_uv(k, [f], HEWN, E, n.cross(E).normalized(), off=vki_hash_off(tuple(f.calc_center_median())))


def vki_tav_extrude(k, poly, a0, a1, mi, axis="y"):
    """closed prism of a simple polygon (convex or concave; 2-D points in order) extruded a0..a1: axis 'y' poly=(x, z),
    'x' poly=(y, z), 'z' poly=(x, y). Normals outward. Returns (verts, faces)."""
    def P(p, a):
        if axis == "y":
            return Vector((p[0], a, p[1]))
        if axis == "z":
            return Vector((p[0], p[1], a))
        return Vector((a, p[0], p[1]))
    bm = k.bm
    A = [bm.verts.new(P(p, a0)) for p in poly]
    B = [bm.verts.new(P(p, a1)) for p in poly]
    n = len(poly)
    fs = [bm.faces.new(A), bm.faces.new(B[::-1])]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    for f in fs:
        f.material_index = mi
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    k.project(fs, mi)
    return A + B, fs


def vki_tav_lathe(k, prof, mis, seg=VKI_TAV_SEG, M=None, smooth=True, sharp_deg=30.0, phase=0.5, off=None,
                  caps=(None, None)):
    """closed solid of revolution about local Z, placed by the 4x4 matrix M. prof: [(r, z), ...] from bottom to top;
    a point with r == 0 is an apex (triangle fan), otherwise the first / last ring gets a flat n-gon cap. mis: one
    material per band (len(prof) - 1 entries) or one int; caps: (bottom, top) cap materials (default: the adjacent
    band's). UVs: side faces u along the axis (staves / grain), v round the axis; ring bands and caps planar. Side
    bands are smooth, nearly horizontal bands flat; ring edges are sharp at profile corners > sharp_deg and at
    material changes. Returns (verts, bands, cap faces)."""
    bm = k.bm
    n = len(prof)
    mis = [mis] * (n - 1) if isinstance(mis, int) else list(mis)
    rings = []
    for r, z in prof:
        if r <= 1e-7:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * (i + phase) / seg),
                                        r * math.sin(2 * math.pi * (i + phase) / seg), z)) for i in range(seg)])
    bands = []
    for j in range(n - 1):
        A, B = rings[j], rings[j + 1]
        fs = []
        for i in range(seg):
            i2 = (i + 1) % seg
            if len(A) == 1:
                fs.append(bm.faces.new((A[0], B[i], B[i2])))
            elif len(B) == 1:
                fs.append(bm.faces.new((A[i], A[i2], B[0])))
            else:
                fs.append(bm.faces.new((A[i], A[i2], B[i2], B[i])))
        bands.append(fs)
    cap0 = bm.faces.new(rings[0][::-1]) if len(rings[0]) > 1 else None
    cap1 = bm.faces.new(rings[-1]) if len(rings[-1]) > 1 else None
    capf = [c_ for c_ in (cap0, cap1) if c_ is not None]
    allf = [f for fs in bands for f in fs] + capf
    vs = [v for rg in rings for v in rg]
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=vs)
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    bm.normal_update()
    R = M.to_3x3() if M is not None else Matrix.Identity(3)
    ax = (R @ VKI_TAV_Z).normalized()
    e1 = (R @ VKI_TAV_X).normalized(); e2 = ax.cross(e1).normalized()
    org = (M @ Vector((0.0, 0.0, 0.0))) if M is not None else Vector((0.0, 0.0, 0.0))
    o = off if off is not None else vki_hash_off(tuple(org))
    for j, fs in enumerate(bands):
        dr = prof[j + 1][0] - prof[j][0]; dz = prof[j + 1][1] - prof[j][1]
        flat = abs(dz) < 0.35 * math.hypot(dr, dz)
        for f in fs:
            if flat:
                vki_tav_uv(k, [f], mis[j], e1, e2, off=o)
            else:
                V = f.normal.cross(ax)
                V = V.normalized() if V.length > 1e-6 else e1.copy()
                vki_tav_uv(k, [f], mis[j], ax, V, off=o)
            f.smooth = bool(smooth) and not flat
    if cap0 is not None:
        vki_tav_uv(k, [cap0], caps[0] if caps[0] is not None else mis[0], e1, e2, off=o)
    if cap1 is not None:
        vki_tav_uv(k, [cap1], caps[1] if caps[1] is not None else mis[-1], e1, e2, off=o)
    # sharp ring edges: cap rims, profile corners, material changes
    for j, rg in enumerate(rings):
        if len(rg) == 1:
            continue
        sharp = j == 0 or j == n - 1
        if not sharp:
            d1 = Vector((prof[j][0] - prof[j - 1][0], prof[j][1] - prof[j - 1][1]))
            d2 = Vector((prof[j + 1][0] - prof[j][0], prof[j + 1][1] - prof[j][1]))
            if d1.length > 1e-9 and d2.length > 1e-9:
                sharp = math.degrees(d1.angle(d2)) > sharp_deg
            sharp = sharp or mis[j - 1] != mis[j]
        if sharp:
            for i in range(seg):
                e = bm.edges.get((rg[i], rg[(i + 1) % seg]))
                if e is not None:
                    e.smooth = False
    return vs, bands, capf


def vki_tav_leg(k, x, y, z0, z1, w, d=None, sx=0.0, sy=0.0, mi=None, bevel=0.015):
    """a square leg (w x d) with a flat top at z1 centred on (x, y) and a flat foot at z0 moved by (sx, sy) * height
    (sx = tan(splay), sign = direction): a sheared box, so both ends stay level (§5: floor contact is flat)"""
    mi = WOOD if mi is None else mi
    d = w if d is None else d
    h = z1 - z0
    S = Matrix(((1.0, 0.0, -sx, 0.0), (0.0, 1.0, -sy, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))
    xf = Matrix.Translation((x + sx * h / 2, y + sy * h / 2, (z0 + z1) / 2)) @ S
    return list(set(k.box((0.0, 0.0, 0.0), (w, d, h), mi, bevel=bevel, xform=xf)))


def vki_tav_rod(k, a, b, r, mi, seg=8, smooth=True):
    """closed cylinder from point a to point b (a lathe along a-b); returns its verts"""
    a = Vector(a); b = Vector(b); d = b - a
    R = VKI_TAV_Z.rotation_difference(d.normalized()).to_matrix().to_4x4()
    vs, _, _ = vki_tav_lathe(k, [(r, 0.0), (r, d.length)], mi, seg=seg, M=Matrix.Translation(a) @ R, smooth=smooth)
    return vs


def vki_tav_light(role, pos, w, color, rng, radius=0.03, shadows=0):
    """one vki_lights socket entry (the fields vki_lt_lights and the Unity LGT_ empties read)"""
    return dict(type="POINT", role=role, pos=[round(c, 4) for c in pos], w=w, color=list(color), range=rng,
                flicker=1, shadows=shadows, radius=radius)


# ---------------------------------------------------------------- small table items
def vki_tav_tankard(k, x, y, z=0.0, kind="foam", mat=None, turn=0.0):
    """a 0.16 tankard (§5) at (x, y, z): tapered body with a foot and a C handle (turned `turn` rad about its axis).
    kind 'foam': a WAX foam dome over the rim (reads as a pale disc from the game camera); 'ale': an ale surface
    (WATER; the master overrides WATER -> M_VKI_Ale) 2.8 cm under the rim. mat: WOOD (staved) or STEEL (pewter)."""
    mat = WOOD if mat is None else mat
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(turn, 4, "Z")
    if kind == "foam":
        prof = [(0.062, 0.0), (0.066, 0.014), (0.058, 0.156), (0.055, 0.168), (0.030, 0.180)]
        vki_tav_lathe(k, prof, [mat, mat, VKI_WAX, VKI_WAX], M=M, caps=(mat, VKI_WAX))
    else:
        prof = [(0.062, 0.0), (0.066, 0.014), (0.058, 0.160), (0.050, 0.160), (0.050, 0.132)]
        vs, bands, capf = vki_tav_lathe(k, prof, mat, M=M, caps=(mat, WATER))
        k.set_dark(capf[-1].verts, VKI_TAV_ALE_DARK)                    # ale in the tankard's shadow, not a yellow disc
    poly =[(0.054, 0.140), (0.100, 0.140), (0.114, 0.126), (0.114, 0.060), (0.100, 0.046), (0.054, 0.046),
            (0.054, 0.060), (0.096, 0.060), (0.096, 0.126), (0.054, 0.126)]
    vs, fs = vki_tav_extrude(k, poly, -0.011, 0.011, mat, axis="y")
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    k.bm.normal_update()
    k.project(fs, mat)


def vki_tav_platter(k, x, y, z=0.0, r=0.15, mat=None):
    """a turned platter (WOOD) or pewter plate (STEEL): flared foot, rim, shallow well; returns the well-floor z"""
    mat = WOOD if mat is None else mat
    vki_tav_lathe(k, [(r - 0.02, 0.0), (r, 0.018), (r - 0.018, 0.022), (r - 0.030, 0.010)], mat,
                  M=Matrix.Translation((x, y, z)))
    return z + 0.010


def vki_tav_food(k, kind, c, s=1.0, rz=0.0):
    """goods-atlas food (never flat colours, §5): 'bread' loaf, 'ham', 'cheese' wedge, 'apple', 'sausage'"""
    c = Vector(c)
    if kind in ("bread", "ham", "apple"):
        r, sc = {"bread": (0.060, (1.30, 0.85, 0.62)), "ham": (0.062, (1.25, 0.92, 0.72)),
                 "apple": (0.032, (1.0, 1.0, 0.92))}[kind]
        vs = _ico(k, (0.0, 0.0, 0.0), r * s, GOODS, scale=sc, sub=1)
        bmesh.ops.transform(k.bm, matrix=Matrix.Translation(c) @ Matrix.Rotation(rz, 4, "Z"), verts=vs)
        k.bm.normal_update()
        goods_map(k, vs, kind, plane=((math.cos(rz), math.sin(rz), 0.0), (-math.sin(rz), math.cos(rz), 0.0)))
        return vs
    if kind == "cheese":
        poly = [(0.0, 0.0), (0.095 * s, -0.040 * s), (0.105 * s, 0.0), (0.095 * s, 0.040 * s)]
        vs, fs = vki_tav_extrude(k, poly, 0.0, 0.055 * s, GOODS, axis="z")
        bmesh.ops.transform(k.bm, matrix=Matrix.Translation(c) @ Matrix.Rotation(rz, 4, "Z"), verts=vs)
        k.bm.normal_update()
        goods_map(k, vs, "cheese", plane=((math.cos(rz), math.sin(rz), 0.0), (-math.sin(rz), math.cos(rz), 0.0)))
        for f in fs:
            f.smooth = False
        return vs
    if kind == "sausage":
        pts = [Vector((-0.07 * s, 0.0, 0.0)), Vector((0.0, 0.025 * s, 0.0)), Vector((0.07 * s, 0.0, 0.0))]
        R = Matrix.Rotation(rz, 3, "Z")
        vs = []
        for a, b in zip(pts[:-1], pts[1:]):
            vs += vki_tav_rod(k, c + R @ a, c + R @ b, 0.018 * s, GOODS, seg=8)
        goods_map(k, vs, "sausage", plane=((math.cos(rz), math.sin(rz), 0.0), (0.0, 0.0, 1.0)))
        return vs
    raise ValueError(kind)


def vki_tav_candle(k, x, y, z0, h=0.20, r=0.030):
    """a WAX candle Ø 0.06 x 0.20 (§5) standing on z0 with a softened top and a GLOW flame (vki_heat core 1 at the
    root, 0 at the tip); returns the light socket position (1.5 cm above the flame tip)"""
    ct = z0 + h
    vki_tav_lathe(k, [(r, z0), (r * 0.97, ct - 0.010), (r * 0.80, ct)], VKI_WAX, M=Matrix.Translation((x, y, 0.0)))
    vki_tim_flame(k, (x, y, ct - 0.004), 0.075, 0.020, 0.0, 0.0, 0.004, flat=0.85, nseg=8)
    return [x, y, ct + 0.086]


def vki_tav_candle_plate(k, x, y, z=0.0):
    """Candle_Plate: an iron dish Ø 0.14 with a finger tab (+X), a WAX candle, a GLOW flame; returns the socket"""
    vki_tav_lathe(k, [(0.058, 0.0), (0.070, 0.016), (0.058, 0.018), (0.052, 0.009)], IRON,
                  M=Matrix.Translation((x, y, z)))
    k.box((x + 0.085, y, z + 0.013), (0.040, 0.030, 0.006), IRON, bevel=0.002)
    return vki_tav_candle(k, x, y, z + 0.006)


def vki_tav_candlestick(k, x, y, z=0.0):
    """Candlestick: BRONZE, 0.30 tall (domed foot, stem, drip pan, socket), a WAX candle, a GLOW flame"""
    vki_tav_lathe(k, [(0.075, 0.0), (0.022, 0.060), (0.016, 0.200), (0.060, 0.258), (0.060, 0.272),
                      (0.034, 0.300)], BRONZE, M=Matrix.Translation((x, y, z)))
    return vki_tav_candle(k, x, y, z + 0.290)


def vki_tav_jug(k, x, y, z=0.0, turn=0.0):
    """a CLAY ale jug: belly, neck, lip, dark mouth, strap handle"""
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(turn, 4, "Z")
    prof = [(0.058, 0.0), (0.078, 0.060), (0.070, 0.130), (0.044, 0.175), (0.050, 0.205), (0.041, 0.205),
            (0.041, 0.185)]
    vki_tav_lathe(k, prof, CLAY, M=M)
    poly = [(0.040, 0.190), (0.090, 0.180), (0.102, 0.160), (0.084, 0.060), (0.064, 0.052), (0.064, 0.068),
            (0.074, 0.074), (0.088, 0.158), (0.082, 0.168), (0.040, 0.174)]
    vs, fs = vki_tav_extrude(k, poly, -0.012, 0.012, CLAY, axis="y")
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    k.bm.normal_update()
    k.project(fs, CLAY)


# ---------------------------------------------------------------- Bar_Counter_150 / Bar_End_150
# top cross-section (y, z), extruded along x: a 0.12 scrubbed top (PLANKS) with a rounded pale front nosing (HEWN)
VKI_TAV_TOP_PROF = [(-0.335, 0.93), (0.34, 0.93), (0.35, 0.94), (0.35, 1.04), (0.34, 1.05), (-0.315, 1.05),
                    (-0.338, 1.042), (-0.35, 1.02), (-0.35, 0.945)]
VKI_TAV_BOARD_W = 0.1875            # 8 front boards per 1.5 m: the rhythm continues across butt joints
VKI_TAV_RAIL = dict(y=-0.30, z=0.20, r=0.026)       # BRONZE foot rail
VKI_TAV_FLAP = dict(x0=-0.047, x1=0.75, pivot=(-0.0485, 0.0, 1.058), open_deg=100.0)


def vki_tav_counter_top(k, x0, x1):
    """the counter top from x0 to x1: planks along x and the pale nosing, both at UV tile 1.5 with zero offset, so
    chained pieces continue seamlessly (1.5 / 1.5 = 1)"""
    vs, fs = vki_tav_extrude(k, VKI_TAV_TOP_PROF, x0, x1, PLANKS, axis="x")
    k.bm.normal_update()
    for f in fs:
        n = f.normal
        m = HEWN if (n.y < -0.3 and n.z > -0.5) else PLANKS
        vki_tav_board_uv(k, [f], m, VKI_TAV_X, tile=VKI_TAV_TOP_TILE, off=(0.0, 0.0))
    return vs


def vki_tav_counter_body(k, x0, x1, brackets=(), battens=(), rail=True):
    """dark carcass (WOOD -> Dark on the master), recessed toe plinth, vertical front boards with V-joints, two front
    rails, the BRONZE foot rail on IRON brackets, back battens (barman side)"""
    xm, w = (x0 + x1) / 2, x1 - x0
    k.box((xm, 0.06, 0.515), (w, 0.48, 0.83), WOOD, bevel=0.0)            # carcass y -0.18..0.30, z 0.10..0.93
    k.box((xm, 0.07, 0.05), (w, 0.42, 0.10), WOOD, bevel=0.0)             # toe plinth y -0.14..0.28
    nb = max(1, int(round(w / VKI_TAV_BOARD_W)))
    bw = w / nb
    for i in range(nb):
        a = x0 + i * bw
        k.box((a + bw / 2, -0.20, 0.515), (bw, 0.04, 0.83), WOOD, bevel=0.010)        # boards y -0.22..-0.18
    for z0, z1 in ((0.84, 0.90), (0.10, 0.16)):
        k.box((xm, -0.2325, (z0 + z1) / 2), (w, 0.025, z1 - z0), WOOD, bevel=0.006)    # rails y -0.245..-0.22
    for bx in battens:
        k.box((bx, 0.315, 0.515), (0.08, 0.03, 0.83), WOOD, bevel=0.008)
    if rail:
        rl = VKI_TAV_RAIL
        vki_tav_lathe(k, [(rl["r"], 0.0), (rl["r"], w)], BRONZE,
                      M=Matrix.Translation((x0, rl["y"], rl["z"])) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
        for bx in brackets:
            k.box((bx, -0.26, rl["z"]), (0.022, 0.08, 0.03), IRON, bevel=0.004)
    vki_tav_counter_top(k, x0, x1)


def vki_tav_bar_counter(k):
    """Bar_Counter_150 (1.50 x 0.70 x 1.05): chain piece, front -Y (customers), back +Y (barman)"""
    vki_tav_counter_body(k, -0.75, 0.75, brackets=(-0.375, 0.375), battens=(-0.375, 0.375))
    k.slot_mats = {WOOD: "Dark"}
    k.meta.update(vki_kind="Bar_Counter", vki_tier="furniture", vki_mount="floor",
                  vki_use=[[0.0, -0.75, 0], [0.0, 0.75, 180]],
                  vki_chain={"axis": "local X", "pitch": 1.5, "ends": [-0.75, 0.75],
                             "note": "top, nosing, foot rail and board rhythm continue across butt joints; "
                                     "Bar_End_150 butts its +X end against a counter's -X end (same rotation)"},
                  vki_note="free-standing; chained pieces touch at their ends (T12's 5 mm AABB shrink keeps them apart)")


def vki_tav_bar_end(k):
    """Bar_End_150: fixed end x -0.45..-0.05 (counter section), then a 0.80 lift flap over an open passage
    (x -0.047..0.75) whose +X end butts the next counter. The flap is its own loose part with iron strap hinges on
    top; it opens by rotating about local Y through the knuckles."""
    vki_tav_counter_body(k, -0.45, -0.05, brackets=(-0.25,), battens=(-0.25,))
    F = VKI_TAV_FLAP
    vki_tav_counter_top(k, F["x0"], F["x1"])                                  # the flap (continues the counter top)
    for sy in (-0.20, 0.20):                                                  # cleats under the flap
        k.box((0.35, sy, 0.915), (0.72, 0.05, 0.03), WOOD, bevel=0.006)
    px, _, pz = F["pivot"]
    for sy in (-0.18, 0.18):                                                  # strap hinges: leaf, leaf, knuckle
        k.box((-0.0975, sy, 1.053), (0.085, 0.040, 0.006), IRON, bevel=0.0015)
        k.box((0.028, sy, 1.053), (0.140, 0.040, 0.006), IRON, bevel=0.0015)
        vki_tav_rod(k, (px, sy - 0.025, pz), (px, sy + 0.025, pz), 0.009, IRON, seg=8)
    k.slot_mats = {WOOD: "Dark"}
    flap_box = [F["x0"], -0.35, 0.89, F["x1"], 0.35, 1.07]
    k.meta.update(vki_kind="Bar_End", vki_tier="furniture", vki_mount="floor", hinge_axis="local Y",
                  vki_flap={"pivot": list(F["pivot"]), "axis": "local Y", "open_deg": F["open_deg"],
                            "open_dir": "rotate by -deg about local +Y at the pivot: the free +X end lifts and folds "
                                        "back over the fixed end",
                            "part": "every vertex with x > pivot x inside part_box (the flap top, its cleats and "
                                    "hinge leaves)", "part_box": flap_box, "state": "closed"},
                  vki_passage={"x": [F["x0"], F["x1"]], "when": "flap open", "clear_w": round(F["x1"] - F["x0"], 3)},
                  vki_collider=[[-0.25, 0.0, 0.525, 0.40, 0.70, 1.05], [0.3515, 0.0, 0.98, 0.797, 0.70, 0.16]],
                  vki_use=[[0.35, -0.75, 0], [0.35, 0.75, 180]],
                  vki_chain={"axis": "local X", "ends": [-0.45, 0.75], "joins_at": 0.75,
                             "partner": "SM_VKI_Prop_Bar_Counter_150 (its -X end), same rotation"},
                  vki_note="the fixed end (x -0.45) faces a wall; the flap's closed collider blocks the passage")


# ---------------------------------------------------------------- CaskRack_150
VKI_TAV_CASK = dict(xs=(-0.30, 0.30), zc=0.82, L=0.74, y_back=0.42, rb=0.285, rh=0.245)


def vki_tav_cask_r(z):
    c = VKI_TAV_CASK
    t = (z - c["L"] / 2) / (c["L"] / 2)
    return c["rh"] + (c["rb"] - c["rh"]) * (1.0 - t * t)


def vki_tav_cask(k, xc):
    """one cask lying along Y (back head at y_back, front head toward -Y): bulged staves (WOOD) with two raised
    IRON hoops at each end, recessed plank heads (PLANKS)"""
    c = VKI_TAV_CASK
    L, rh, r = c["L"], c["rh"], vki_tav_cask_r
    hp = 0.006                                                               # hoop relief
    zs = [0.05, 0.12, 0.25, L / 2, L - 0.25, L - 0.12, L - 0.05]
    prof = [(rh - 0.022, 0.018), (rh, 0.0), (r(zs[0]) + hp, zs[0]), (r(zs[1]) + hp, zs[1]), (r(zs[2]), zs[2]),
            (r(zs[3]), zs[3]), (r(zs[4]), zs[4]), (r(zs[5]) + hp, zs[5]), (r(zs[6]) + hp, zs[6]), (rh, L),
            (rh - 0.022, L - 0.018)]
    mis = [WOOD, WOOD, IRON, WOOD, WOOD, WOOD, WOOD, IRON, WOOD, WOOD]
    M = Matrix.Translation((xc, c["y_back"], c["zc"])) @ Matrix.Rotation(math.pi / 2, 4, "X")
    vs, bands, capf = vki_tav_lathe(k, prof, mis, M=M, caps=(PLANKS, PLANKS))
    for f in capf:                                                           # head boards: planks vertical
        vki_tav_uv(k, [f], PLANKS, VKI_TAV_X, VKI_TAV_Z, off=vki_hash_off((xc, f.calc_center_median().y, 0.0)))
    return vs


def vki_tav_saddle(k, y0, y1, rn):
    """a saddle beam across both casks (x -0.58..0.58, y0..y1): legs at the ends, notches of radius rn under the
    casks (1 cm clear of the staves); one concave polygon extruded along Y"""
    c = VKI_TAV_CASK
    zc = c["zc"]
    beta = math.radians(35.0)
    zl = zc - rn * math.sin(beta)
    pts = [(-0.58, 0.0), (-0.44, 0.0), (-0.44, 0.20), (0.44, 0.20), (0.44, 0.0), (0.58, 0.0), (0.58, zl)]
    for xc in (0.30, -0.30):                                                 # right notch first (walking right to left)
        for i in range(9):
            th = 2 * math.pi - beta - (math.pi - 2 * beta) * i / 8
            pts.append((xc + rn * math.cos(th), zc + rn * math.sin(th)))
    pts.append((-0.58, zl))
    vs, fs = vki_tav_extrude(k, pts, y0, y1, WOOD, axis="y")
    k.bm.normal_update()
    vki_tav_board_uv(k, fs, WOOD, VKI_TAV_X, off=vki_hash_off((0.0, y0, 0.0)))
    return vs


def vki_tav_tap(k, x, z):
    """BRONZE tap on a front head (exaggerated, §5): spigot along -Y with a collar, the spout turned down, a T key"""
    y0 = VKI_TAV_CASK["y_back"] - VKI_TAV_CASK["L"] + 0.02                 # 2 mm inside the recessed head face
    vki_tav_rod(k, (x, y0, z), (x, -0.385, z), 0.024, BRONZE)
    vki_tav_rod(k, (x, -0.316, z), (x, -0.342, z), 0.036, BRONZE)
    vki_tav_rod(k, (x, -0.366, z + 0.010), (x, -0.366, z - 0.070), 0.020, BRONZE)
    k.box((x, -0.352, z + 0.048), (0.016, 0.016, 0.060), BRONZE, bevel=0.0)
    k.box((x, -0.352, z + 0.082), (0.090, 0.020, 0.020), BRONZE, bevel=0.004)


def vki_tav_cask_rack(k):
    """CaskRack_150 (1.20 x 0.90 x 1.20 envelope, wall_floor): two casks on two saddle beams with stretchers,
    BRONZE taps toward -Y over one drip tub (the WATER in it -> M_VKI_Ale)"""
    c = VKI_TAV_CASK
    for xc in c["xs"]:
        vki_tav_cask(k, xc)
    # saddles: notch radius = the largest stave radius across the beam's thickness + 4 mm
    for y0, y1 in ((-0.14, -0.04), (0.20, 0.30)):
        zp = [c["y_back"] - y for y in (y0, y1, (y0 + y1) / 2)]
        rn = max(vki_tav_cask_r(z) for z in zp) + 0.004
        vki_tav_saddle(k, y0, y1, rn)
    for sx in (-0.51, 0.51):                                                 # stretchers between the saddles' legs
        k.box((sx, 0.08, 0.08), (0.10, 0.24, 0.10), WOOD, bevel=0.01)
    # taps (toward the middle, over the tub) and the drip tub (staved, one hoop, ale inside)
    zt = c["zc"] - 0.12
    for xc in c["xs"]:
        vki_tav_tap(k, xc - math.copysign(0.17, xc), zt)
    ty = -0.25
    prof = [(0.170, 0.0), (0.176, 0.05), (0.181, 0.075), (0.195, 0.20), (0.176, 0.20), (0.176, 0.150)]
    vs, bands, capf = vki_tav_lathe(k, prof, [WOOD, IRON, WOOD, WOOD, WOOD], M=Matrix.Translation((0.0, ty, 0.0)),
                                    caps=(WOOD, WATER))
    k.set_dark(capf[-1].verts, VKI_TAV_ALE_DARK)
    k.slot_mats = {WATER: "Ale"}
    k.meta.update(vki_kind="CaskRack", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=c["y_back"],
                  vki_use=[[0.0, -0.80, 0]],
                  vki_note="taps at z %.2f toward -Y; the drip tub holds ale (WATER -> M_VKI_Ale)" % (zt,))


# ---------------------------------------------------------------- Table_Barrel
def vki_tav_table_barrel(k):
    """Table_Barrel (Ø 0.90 x 1.05, floor): a standing barrel (bulged staves, three raised IRON hoops) under a round
    plank top Ø 0.90 at 1.05 with a pale HEWN edge"""
    rb, rh, H = 0.36, 0.305, 0.995
    def r(z):
        t = (z - H / 2) / (H / 2)
        return rh + (rb - rh) * (1.0 - t * t)
    hp = 0.006
    zs = [0.0, 0.07, 0.13, 0.30, H / 2 - 0.03, H / 2 + 0.03, H - 0.30, H - 0.13, H - 0.07, H]
    prof = []
    for i, z in enumerate(zs):
        prof.append((r(z) + (hp if i in (1, 2, 4, 5, 7, 8) else 0.0), z))
    mis = [WOOD, IRON, WOOD, WOOD, IRON, WOOD, WOOD, IRON, WOOD]
    vki_tav_lathe(k, prof, mis)
    vki_tav_rod(k, (0.0, -r(0.40) + 0.01, 0.40), (0.0, -r(0.40) - 0.022, 0.40), 0.028, WOOD)   # bung
    # the top: Ø 0.90, z 0.99..1.05, bottom chamfer, HEWN side and top chamfer, scrubbed planks on top
    vs, bands, capf = vki_tav_lathe(k, [(0.43, 0.99), (0.45, 1.005), (0.45, 1.03), (0.43, 1.05)],
                                    [PLANKS, HEWN, HEWN], caps=(PLANKS, PLANKS))
    for f in capf:
        vki_tav_uv(k, [f], PLANKS, VKI_TAV_Y, VKI_TAV_X, off=(0.13, 0.0))
    for f in bands[1] + bands[2]:
        E = VKI_TAV_Z.cross(f.normal).normalized()
        vki_tav_uv(k, [f], HEWN, E, f.normal.cross(E).normalized())
    k.meta.update(vki_kind="Table_Barrel", vki_tier="furniture", vki_mount="floor", vki_table_z=1.05,
                  vki_use=[[0.0, -0.75, 0], [0.0, 0.75, 180]],
                  vki_note="dress with SM_VKI_Prop_TableDress_Tavern_C at z 1.05 (mount table)")


# ---------------------------------------------------------------- TableDress_Tavern_A / B / C
def vki_tav_dress_meta(k, var, lights, fits):
    k.slot_mats = {WATER: "Ale"}
    k.meta.update(vki_kind="TableDress_Tavern", vki_var=var, vki_tier="furniture", vki_mount="table",
                  vki_nav="none", vki_fits=fits,
                  vki_lights=[vki_tav_light("candle", p, VKI_TAV_CANDLE_W, VKI_TAV_CANDLE_COL, 3.0, 0.02)
                              for p in lights],
                  vki_fx=[dict(fx="candle", pos=[p[0], p[1], round(p[2] - 0.05, 4)]) for p in lights],
                  vki_note="origin at the table-top surface; tankards: WAX foam domes / ale (WATER -> M_VKI_Ale); "
                           "tier furniture: a whole table set (see the hand-in)")


def vki_tav_dress_a(k):
    """TableDress_Tavern_A, for Table_Trestle_300 (top 2.70 x 0.90 at 0.80): four tankards (three foaming, one of
    them pewter; one with ale), a platter of ham, bread and cheese, a Candle_Plate"""
    vki_tav_tankard(k, -1.02, -0.27, kind="foam", turn=0.4)
    vki_tav_tankard(k, -0.42, 0.29, kind="ale", turn=2.6)
    vki_tav_tankard(k, 0.62, -0.28, kind="foam", mat=STEEL, turn=-0.3)
    vki_tav_tankard(k, 1.08, 0.24, kind="foam", turn=3.4)
    zf = vki_tav_platter(k, 0.10, 0.02)
    vki_tav_food(k, "ham", (0.06, 0.03, zf + 0.040), rz=0.5)
    vki_tav_food(k, "bread", (0.17, -0.05, zf + 0.026), s=0.8, rz=-0.3)
    vki_tav_food(k, "cheese", (0.13, 0.09, zf - 0.004), s=0.8, rz=2.3)
    s1 = vki_tav_candle_plate(k, -0.52, -0.08)
    vki_tav_dress_meta(k, "A", [s1], "SM_VKI_Prop_Table_Trestle_300 at z 0.80 (also Table_Trestle_150: x +-0.55)")


def vki_tav_dress_b(k):
    """TableDress_Tavern_B, for Table_Trestle_300: three tankards (foam, ale, pewter foam), a clay jug, a bread board
    with a loaf, cheese and apples, a Candle_Plate"""
    vki_tav_tankard(k, -0.88, 0.26, kind="foam", turn=2.9)
    vki_tav_tankard(k, 0.30, -0.29, kind="ale", turn=0.2)
    vki_tav_tankard(k, 0.98, 0.27, kind="foam", mat=STEEL, turn=3.3)
    vki_tav_jug(k, -0.30, 0.22, turn=2.2)
    vki_tav_slab(k, (-0.46, -0.16, 0.0125), (0.34, 0.20, 0.025), mi=WOOD, bevel=0.006, rot_z=0.15)
    vki_tav_food(k, "bread", (-0.50, -0.16, 0.058), rz=0.15)
    vki_tav_food(k, "cheese", (-0.37, -0.12, 0.024), s=0.7, rz=-2.6)
    vki_tav_food(k, "apple", (0.62, 0.05, 0.030))
    vki_tav_food(k, "apple", (0.68, 0.10, 0.030), rz=1.0)
    s1 = vki_tav_candle_plate(k, 0.20, 0.10)
    vki_tav_dress_meta(k, "B", [s1], "SM_VKI_Prop_Table_Trestle_300 at z 0.80")


def vki_tav_dress_c(k):
    """TableDress_Tavern_C, for Table_Barrel (top Ø 0.90 at 1.05): two tankards (foam, pewter ale), a small plate
    with a sausage and bread, a Candle_Plate"""
    vki_tav_tankard(k, -0.20, -0.20, kind="foam", turn=0.9)
    vki_tav_tankard(k, 0.24, 0.12, kind="ale", mat=STEEL, turn=4.0)
    zf = vki_tav_platter(k, -0.06, 0.18, r=0.12)
    vki_tav_food(k, "sausage", (-0.08, 0.17, zf + 0.018), s=0.9, rz=0.4)
    vki_tav_food(k, "bread", (-0.02, 0.22, zf + 0.026), s=0.62, rz=-0.8)
    s1 = vki_tav_candle_plate(k, 0.14, -0.20)
    vki_tav_dress_meta(k, "C", [s1], "SM_VKI_Prop_Table_Barrel at z 1.05")


# ---------------------------------------------------------------- lights: Lantern_Wall, Candle_Plate, Candlestick
VKI_TAV_LANTERN_Y = -0.085          # the lantern's axis; the wall plate's back face is at y +0.225 (vki_back_y)


def vki_tav_lantern_wall(k):
    """Lantern_Wall (0.30 x 0.45 x 0.60 envelope, wall_hung, z 1.90-2.45): iron wall plate, arm and strut; a caged
    lantern hanging from the arm: bottom plate and drip knob, GLOW panes (vki_heat: hot centre, cool edges), four
    corner posts, cross bars, top plate, pyramid roof, finial"""
    cy = VKI_TAV_LANTERN_Y
    g_, zg = 0.095, (1.965, 2.245)                                                    # pane half width, pane z
    zm = (zg[0] + zg[1]) / 2
    k.box((0.0, 0.212, 2.30), (0.10, 0.026, 0.30), IRON, bevel=0.0)                   # wall plate y 0.199..0.225
    k.box((0.0, 0.0525, 2.405), (0.028, 0.293, 0.028), IRON, bevel=0.0)               # arm y -0.094..0.199
    vki_tav_rod(k, (0.0, 0.199, 2.20), (0.0, 0.02, 2.396), 0.011, IRON, seg=6)          # strut
    k.box((0.0, cy, 2.378), (0.014, 0.014, 0.034), IRON, bevel=0.0)                   # hanger into arm and finial
    k.box((0.0, cy, 1.92), (0.08, 0.08, 0.04), IRON, bevel=0.0)                       # drip knob z 1.90..1.94
    k.box((0.0, cy, 1.955), (0.25, 0.25, 0.03), IRON, bevel=0.0)                      # bottom plate z 1.94..1.97
    before = set(k.bm.verts)
    k.box((0.0, cy, zm), (2 * g_, 2 * g_, zg[1] - zg[0]), GLOW, bevel=0.0)            # panes
    gv = vki_cut(k, vki_tav_new(k, before), xs=[0.0], ys=[cy], zs=[zm - 0.07, zm, zm + 0.07])
    for v in gv:
        dxy = math.hypot(v.co.x, v.co.y - cy); dz = abs(v.co.z - (zm - 0.025))
        k.set_heat([v], vki_clamp(1.3 - (dxy + 0.7 * dz) / 0.155))
    k.project(vki_tav_faces(gv), GLOW)
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.box((sx * g_, cy + sy * g_, zm), (0.028, 0.028, 0.30), IRON, bevel=0.0)  # corner posts 1.955..2.255
    b_ = g_ + 0.006
    for (dx, dy, sx_, sy_) in ((0.0, -b_, 2 * g_, 0.012), (0.0, b_, 2 * g_, 0.012), (-b_, 0.0, 0.012, 2 * g_),
                               (b_, 0.0, 0.012, 2 * g_)):
        k.box((dx, cy + dy, zm), (sx_, sy_, 0.014), IRON, bevel=0.0)                   # cross bars
    k.box((0.0, cy, 2.255), (0.27, 0.27, 0.03), IRON, bevel=0.008)                    # top plate z 2.24..2.27
    vki_tav_lathe(k, [(0.191, 2.27), (0.050, 2.345)], IRON, seg=4, phase=0.5, M=Matrix.Translation((0.0, cy, 0.0)),
                  smooth=False)                                                         # roof
    k.box((0.0, cy, 2.3575), (0.03, 0.03, 0.025), IRON, bevel=0.0)                    # finial z 2.345..2.37
    k.meta.update(vki_kind="Lantern_Wall", vki_tier="dressing", vki_mount="wall_hung", vki_back_y=0.225,
                  vki_mount_zmin=1.90, vki_mount_zmax=2.45, vki_nav="none",
                  # socket just in front of the front pane (a 60 W point 0.31 m off the wall face burned a white halo
                  # into the plaster behind the lantern)
                  vki_lights=[vki_tav_light("lantern", (0.0, cy - g_ - 0.035, zm - 0.02), VKI_TAV_LANTERN_W,
                                            VKI_TAV_LANTERN_COL, 5.0, 0.06)],
                  vki_note="authored at its real height (placer z 0); Full walls only (R-occ4); zmax 2.45 needs H >= "
                           "2.59: on Wattle (H 2.4) place it with z -0.30")


def vki_tav_candle_plate_piece(k):
    """Candle_Plate (Ø 0.14, table mount): iron dish, WAX candle, GLOW flame, socket 15 W, FX candle"""
    s = vki_tav_candle_plate(k, -0.0175, 0.0)
    k.meta.update(vki_kind="Candle_Plate", vki_tier="dressing", vki_mount="table", vki_nav="none",
                  vki_lights=[vki_tav_light("candle", s, VKI_TAV_CANDLE_W, VKI_TAV_CANDLE_COL, 3.0, 0.02)],
                  vki_fx=[dict(fx="candle", pos=[s[0], s[1], round(s[2] - 0.05, 4)])],
                  vki_note="origin at the surface it stands on (table, chest, shelf)")


def vki_tav_candlestick_piece(k):
    """Candlestick (BRONZE, 0.30 + a 0.20 candle, table mount): socket 15 W, FX candle"""
    s = vki_tav_candlestick(k, 0.0, 0.0)
    k.meta.update(vki_kind="Candlestick", vki_tier="dressing", vki_mount="table", vki_nav="none",
                  vki_lights=[vki_tav_light("candle", s, VKI_TAV_CANDLE_W, VKI_TAV_CANDLE_COL, 3.0, 0.02)],
                  vki_fx=[dict(fx="candle", pos=[s[0], s[1], round(s[2] - 0.05, 4)])],
                  vki_note="origin at the surface it stands on")


# ---------------------------------------------------------------- tests and registration
def vki_tav_flap_parts(me, fl):
    """(flap islands, pin islands, {island: [min, max]}, island index per vertex) of a Bar_End mesh by its vki_flap:
    flap = loose parts with a vertex inside part_box beyond the pivot x; pins = the knuckles on the pivot axis"""
    px, py, pz = fl["pivot"]; bx = fl["part_box"]
    isl, ni = vki_islands(me)
    boxes = {}
    for v in me.vertices:
        b = boxes.setdefault(isl[v.index], [Vector(v.co), Vector(v.co)])
        for i in range(3):
            b[0][i] = min(b[0][i], v.co[i]); b[1][i] = max(b[1][i], v.co[i])
    pins = {i for i, (b0, b1) in boxes.items() if b0.x < px < b1.x and b0.z < pz < b1.z}
    flap = set()
    for v in me.vertices:
        c = v.co
        if isl[v.index] not in pins and c.x > px and bx[0] - 1e-6 <= c.x <= bx[3] + 1e-6 and \
                bx[1] - 1e-6 <= c.y <= bx[4] + 1e-6 and bx[2] - 1e-6 <= c.z <= bx[5] + 1e-6:
            flap.add(isl[v.index])
    return flap, pins, boxes, isl


def vki_tav_flap_demo(c, x, y, deg=100.0, rot=0.0, name="WS_tav_BarEnd_FlapOpen"):
    """a display copy of Bar_End_150 (a plain object with its own mesh, not a master) with the flap opened `deg`
    about vki_flap's hinge (rotation -deg about local +Y at the pivot), linked into collection c"""
    src = bpy.data.objects["SM_VKI_Prop_Bar_End_150"]
    fl = vki_get(src, "vki_flap")
    px, py, pz = fl["pivot"]
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old)
    me = bpy.data.meshes.get(name) or src.data.copy()
    if me.name != name:
        me.name = name
    else:
        bm = bmesh.new(); bm.from_mesh(src.data); bm.to_mesh(me); bm.free()
    flap, pins, boxes, isl = vki_tav_flap_parts(me, fl)
    R = Matrix.Rotation(math.radians(-deg), 3, "Y"); P = Vector((px, py, pz))
    for v in me.vertices:
        if isl[v.index] in flap:
            v.co = R @ (Vector(v.co) - P) + P
    me.update()
    o = bpy.data.objects.new(name, me)
    c.objects.link(o)
    o.location = (x, y, 0.0); o.rotation_euler = (0.0, 0.0, math.radians(rot))
    return o


def vki_tav_flap_check(name="SM_VKI_Prop_Bar_End_150", degs=(30.0, 60.0, 100.0)):
    """rotate the flap part of a built Bar_End_150 about its hinge (vki_flap) and report, per angle, how many flap
    vertices end up inside the fixed part's bounding boxes of loose parts (0 = swings clear) and the flap's top z"""
    o = bpy.data.objects[name]
    fl = vki_get(o, "vki_flap")
    px, py, pz = fl["pivot"]
    me = o.data
    # the hinge knuckles straddle the pivot axis: they are the pins, neither flap nor obstacle
    flap_parts, pins, boxes, isl = vki_tav_flap_parts(me, fl)
    fixed = {i: b for i, b in boxes.items() if i not in flap_parts and i not in pins}
    out = {}
    for d in degs:
        R = Matrix.Rotation(math.radians(-d), 3, "Y")
        inside = 0; ztop = -1.0
        for v in me.vertices:
            if isl[v.index] not in flap_parts:
                continue
            p = R @ (Vector(v.co) - Vector((px, py, pz))) + Vector((px, py, pz))
            ztop = max(ztop, p.z)
            for b0, b1 in fixed.values():
                if all(b0[i] + 1e-4 < p[i] < b1[i] - 1e-4 for i in range(3)):
                    inside += 1
                    break
        out[d] = (inside, round(ztop, 3))
    return out


VKI_TAV_SPECS = [
    ("SM_VKI_Prop_Bar_Counter_150", vki_tav_bar_counter),
    ("SM_VKI_Prop_Bar_End_150", vki_tav_bar_end),
    ("SM_VKI_Prop_CaskRack_150", vki_tav_cask_rack),
    ("SM_VKI_Prop_Table_Barrel", vki_tav_table_barrel),
    ("SM_VKI_Prop_TableDress_Tavern_A", vki_tav_dress_a),
    ("SM_VKI_Prop_TableDress_Tavern_B", vki_tav_dress_b),
    ("SM_VKI_Prop_TableDress_Tavern_C", vki_tav_dress_c),
    ("SM_VKI_Prop_Lantern_Wall", vki_tav_lantern_wall),
    ("SM_VKI_Prop_Candle_Plate", vki_tav_candle_plate_piece),
    ("SM_VKI_Prop_Candlestick", vki_tav_candlestick_piece),
]
VKI_TAV_NAMES = [n for n, _ in VKI_TAV_SPECS]
vki_register([(n, fn, {"grime": "prop"}, "tavern") for n, fn in VKI_TAV_SPECS])
