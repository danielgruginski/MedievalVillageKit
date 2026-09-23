# =============================================================================
# ws_humble.py  -  workshop module of the "humble" agent (prefix hum_)
# Early-game housing for the Village Kit:
#   * wattle-and-daub wall family (wall top HUM_HW = 2.4, outer timber face y = -0.16)
#   * cruck thatch gable, thatch smoke vent, low thatch lean-to
#   * livestock (cow, sheep, pig, goat, draft horse, chickens) + hay rack + wattle coop
#   * builders: build_hovel, build_longhouse, build_pigsty, build_sheepfold
# Executed after vk_helpers in the same namespace: every kit name is available.
# =============================================================================
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

HUM_HW = 2.4        # wattle wall top (spec HW)
HUM_TF = -0.16      # outer timber face, wall-local y
HUM_DF = -0.12      # daub face before bulge
HUM_CRUCK_X = 1.70  # cruck blade centre line, roof-bay local x (gable wall face at 1.62)
HUM_FUR = CLOTH_B   # white hair / horn for livestock (PAPER shows its script lines on big areas)


def hum_pick(name, fallback):
    return name if bpy.data.objects.get(name) else fallback


def hum_refresh_variants(names):
    """workshop helper: place_v caches restyled mesh copies (VAR_*) forever; after a piece master is
    rebuilt, copy its new geometry into every cached VAR copy of that piece (materials stay swapped)"""
    n_ = 0
    for nm in names:
        src = bpy.data.objects.get(nm)
        if src is None: continue
        for kind_ in ({}, {"plaster": "Daub"}, {"plaster": "Daub", "roof": "Thatch"}, {"roof": "Thatch"}):
            key = (nm,) + tuple(sorted(kind_.items()))
            me = bpy.data.meshes.get("VAR_" + str(abs(hash(key))))
            if me is None or me == src.data: continue
            bm_ = bmesh.new(); bm_.from_mesh(src.data); bm_.to_mesh(me); bm_.free(); n_ += 1
    return n_


# ----------------------------------------------------------------- generic helpers
def hum_cut(k, vs, xs=(), zs=()):
    """bisect the geometry around verts vs at the given x and z planes; returns the verts"""
    geom = list(set(vs) | {e for v in vs for e in v.link_edges} | {f for v in vs for f in v.link_faces})
    planes = [((x, 0, 0), (1, 0, 0)) for x in xs] + [((0, 0, z), (0, 0, 1)) for z in zs]
    for co, no in planes:
        geom = [g_ for g_ in geom if g_.is_valid]
        r = bmesh.ops.bisect_plane(k.bm, geom=geom, plane_co=co, plane_no=no)
        geom = list(set(geom) | set(r["geom"]))
    return [g_ for g_ in geom if isinstance(g_, bmesh.types.BMVert) and g_.is_valid]


def hum_rod(k, a, b, r1, r2=None, segs=6, mi=WOOD):
    a = Vector(a); b = Vector(b); d = b - a
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    return _cyl(k, (a + b) / 2, r1, r1 if r2 is None else r2, d.length, segs, mi, rot=q)


def hum_log(k, c, r, L, axis="X", segs=8, mi=WOOD):
    """round log with ENDGRAIN caps"""
    rot = {"X": Matrix.Rotation(math.pi / 2, 4, "Y"), "Y": Matrix.Rotation(math.pi / 2, 4, "X"), "Z": None}[axis]
    vs = _cyl(k, c, r, r, L, segs, mi, rot=rot)
    ax = {"X": Vector((1, 0, 0)), "Y": Vector((0, 1, 0)), "Z": Vector((0, 0, 1))}[axis]
    caps = [f for f in {f for v in vs for f in v.link_faces} if abs(f.normal.dot(ax)) > 0.9]
    k.project(caps, ENDGRAIN)
    return vs


def hum_tube(k, pts, r, segs=8, mi=THATCH, lump=0.0, seed=0.0):
    """tube along a polyline (r scalar or list); returns (faces, rings)"""
    pts = [Vector(p) for p in pts]; n = len(pts); rings = []; prevN = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        if prevN is None:
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            N = t.cross(ref).normalized()
        else:
            N = (prevN - t * prevN.dot(t)).normalized()
        B = t.cross(N); prevN = N
        rr = r[i] if isinstance(r, (list, tuple)) else r
        ring = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            lr = rr * (1 + lump * _pnoise(i * 0.9 + j * 1.7, seed))
            ring.append(k.bm.verts.new(p + (N * math.cos(a) + B * math.sin(a)) * lr))
        rings.append(ring)
    fs = []
    for i in range(n - 1):
        for j in range(segs):
            j2 = (j + 1) % segs
            fs.append(k.bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j])))
    k.bm.normal_update()
    k.project(fs, mi)
    return fs, rings


def hum_spow(v, e):
    return math.copysign(abs(v) ** e, v)


def hum_sq(k, c, r, e=0.7, nu=12, nv=8, mi=HIDE, rot=None, mat=None, disp=None, warp=None, flat_below=None):
    """superquadric blob. c centre, r radii, e<1 boxier. rot: Matrix (rotation about c).
    mat(n)->material per face from the normalised local position; disp(n)->radial factor;
    warp(p)->p deforms local coordinates; flat_below: clamp local z (before rot) to this value"""
    c = Vector(c); Rm = rot.to_3x3() if rot is not None else Matrix.Identity(3)
    nmap = {}

    def P(th, ph):
        ct, st = math.cos(th), math.sin(th); cp, sp = math.cos(ph), math.sin(ph)
        n = Vector((hum_spow(ct, e) * hum_spow(cp, e), hum_spow(ct, e) * hum_spow(sp, e), hum_spow(st, e)))
        s = disp(n) if disp else 1.0
        p = Vector((n.x * r[0] * s, n.y * r[1] * s, n.z * r[2] * s))
        if warp: p = warp(p)
        if flat_below is not None and p.z < flat_below: p.z = flat_below
        v = k.bm.verts.new(c + Rm @ p); nmap[v] = n
        return v
    vb = P(-math.pi / 2, 0.0); vt = P(math.pi / 2, 0.0)
    rows = [[P(-math.pi / 2 + math.pi * i / nv, -math.pi + 2 * math.pi * j / nu) for j in range(nu)] for i in range(1, nv)]
    fs = []
    for j in range(nu):
        j2 = (j + 1) % nu
        fs.append(k.bm.faces.new((vb, rows[0][j2], rows[0][j])))
        fs.append(k.bm.faces.new((vt, rows[-1][j], rows[-1][j2])))
    for i in range(len(rows) - 1):
        for j in range(nu):
            j2 = (j + 1) % nu
            fs.append(k.bm.faces.new((rows[i][j], rows[i][j2], rows[i + 1][j2], rows[i + 1][j])))
    k.bm.normal_update()
    groups = {}
    for f in fs:
        n = Vector((0, 0, 0))
        for v in f.verts: n += nmap[v]
        n /= len(f.verts)
        groups.setdefault(mat(n) if mat else mi, []).append(f)
    for m_, g_ in groups.items(): k.project(g_, m_)
    return fs


def hum_eye(k, c, r=0.045, out=(1, 0, 0), mi=COAL, hl=True, white=0.0):
    c = Vector(c); o = Vector(out).normalized()
    if white:
        _ico(k, c, r * white, HUM_FUR, sub=1); c = c + o * r * (white - 0.7)
    _ico(k, c, r, mi, sub=1)
    if hl: _ico(k, c + o * r * 0.8 + Vector((0, 0, r * 0.35)), r * 0.33, HUM_FUR, sub=1)


def hum_patch(k, C, U, V, N, w, h, seed=0, n=11):
    """bare-wattle patch where the daub has fallen off: ragged WATTLE polygon inside a broken daub lip"""
    rnd = random.Random(seed); C = Vector(C); U = Vector(U); V = Vector(V); N = Vector(N)
    n = max(n, 14)
    p1, p2, p3 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    ang = [2 * math.pi * i / n + rnd.uniform(-0.12, 0.12) for i in range(n)]
    rad = [max(0.35, 1.0 + 0.3 * math.sin(2 * a + p1) + 0.18 * math.sin(3 * a + p2) + 0.1 * math.sin(7 * a + p3) + rnd.uniform(-0.12, 0.12)) for a in ang]
    lip = [rnd.uniform(0.006, 0.02) for _ in range(n)]
    wid = [rnd.uniform(1.08, 1.3) for _ in range(n)]

    def Pt(a, r_, s, d): return C + U * (math.cos(a) * w / 2 * r_ * s) + V * (math.sin(a) * h / 2 * r_ * s) + N * d
    inner = [k.bm.verts.new(Pt(a, r_, 1.0, 0.004)) for a, r_ in zip(ang, rad)]
    rim = [k.bm.verts.new(Pt(a, r_, 1.04, l_)) for a, r_, l_ in zip(ang, rad, lip)]
    outer = [k.bm.verts.new(Pt(a, r_, s_, -0.012)) for a, r_, s_ in zip(ang, rad, wid)]
    f = k.bm.faces.new(inner)
    walls = []; lips = []
    for i in range(n):
        j = (i + 1) % n
        walls.append(k.bm.faces.new((inner[i], inner[j], rim[j], rim[i])))
        lips.append(k.bm.faces.new((rim[i], rim[j], outer[j], outer[i])))
    k.bm.normal_update()
    if f.normal.dot(N) < 0: f.normal_flip()
    for g_ in walls:
        if g_.normal.dot(C - g_.calc_center_median()) < 0: g_.normal_flip()
    for g_ in lips:
        if g_.normal.dot(N) < 0: g_.normal_flip()
    k.bm.normal_update()
    f.material_index = WATTLE
    for l in f.loops: l[k.uv].uv = ((l.vert.co - C).dot(U), (l.vert.co - C).dot(V))
    k.project(walls + lips, PLASTER)


# ----------------------------------------------------------------- wattle wall parts
def hum_bulge(x, z, panels, z0, z1, amp):
    for (a, c) in panels:
        if a - 1e-4 <= x <= c + 1e-4 and c > a:
            return max(0.0, amp * math.sin(math.pi * (x - a) / (c - a)) * math.sin(math.pi * (z - z0) / (z1 - z0)))
    return 0.0


def hum_daub(k, x0, x1, z0, z1, panels=None, seed=0, amp=0.024, y1=0.12, sx=0.25, sz=0.3):
    """PLASTER daub box, subdivided, outer face pillowed between the timbers and jittered"""
    vs = k.box(((x0 + x1) / 2, (HUM_DF + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - HUM_DF, z1 - z0), PLASTER, bevel=0)
    nx = max(1, int(round((x1 - x0) / sx))); nz = max(1, int(round((z1 - z0) / sz)))
    vs = hum_cut(k, vs, [x0 + (x1 - x0) * i / nx for i in range(1, nx)], [z0 + (z1 - z0) * j / nz for j in range(1, nz)])
    panels = panels or [(x0, x1)]
    rnd = random.Random(seed)
    for v in sorted(vs, key=lambda v: (round(v.co.x, 3), round(v.co.z, 3), round(v.co.y, 3))):
        if v.co.y > HUM_DF + 0.005: continue
        x, z = v.co.x, v.co.z
        inner = (x0 + 0.01 < x < x1 - 0.01) and (z0 + 0.01 < z < z1 - 0.01)
        v.co.y -= hum_bulge(x, z, panels, z0, z1, amp)
        if inner:
            v.co.y -= rnd.uniform(-0.01, 0.012)
            v.co.x += rnd.uniform(-0.012, 0.012); v.co.z += rnd.uniform(-0.012, 0.012)


def hum_wall_patch(k, cx, cz, w, h, seed, panels, z0=0.55, z1=2.2, amp=0.024):
    fy = HUM_DF - hum_bulge(cx, cz, panels, z0, z1, amp) - 0.01
    hum_patch(k, (cx, fy, cz), (1, 0, 0), (0, 0, 1), (0, -1, 0), w, h, seed)


def hum_post(k, x, z0, z1, w=0.24, d=0.30, tilt=0.0):
    k.box((x, HUM_TF + d / 2, (z0 + z1) / 2), (w, d, z1 - z0), WOOD, rot=(0, tilt, 0), bevel=0.045, segs=2)


def hum_bar(k, x0, z0, x1, z1, w=0.16, d=0.22, face=HUM_TF):
    L = math.hypot(x1 - x0, z1 - z0); ang = math.atan2(z1 - z0, x1 - x0)
    k.box(((x0 + x1) / 2, face + d / 2, (z0 + z1) / 2), (L, d, w), WOOD, rot=(0, -ang, 0), bevel=0.035, segs=2)


def hum_plate(k, z=2.3, sag=0.035):
    """wall plate in 3 hewn pieces sagging toward x=0; top exactly HUM_HW at the seams"""
    pts = [(-1.5, z), (-0.5, z - sag), (0.5, z - sag), (1.5, z)]
    for (xa, za), (xb, zb) in zip(pts[:-1], pts[1:]):
        ang = math.atan2(zb - za, xb - xa)
        xm = (xa + xb) / 2
        if xa == -1.5: xm += 0.02
        if xb == 1.5: xm -= 0.02
        k.box((xm, HUM_TF + 0.15, (za + zb) / 2), (math.hypot(xb - xa, zb - za) + 0.04, 0.30, 0.2), WOOD,
              rot=(0, -ang, 0), bevel=0.04, segs=2)


def hum_plinth(k, x0=-1.5, x1=1.5, seed=1, gaps=(), core_gaps=(), skirt=True):
    """low rubble footing z 0-0.35 with chunky face rocks; hidden STONE skirt to z -0.6"""
    segs_ = [(x0, x1)]
    for a, b in core_gaps:
        new = []
        for (p, q) in segs_:
            if b <= p or a >= q: new.append((p, q)); continue
            if a > p: new.append((p, a))
            if b < q: new.append((b, q))
        segs_ = new
    for (p, q) in segs_:
        k.box(((p + q) / 2, -0.03, 0.17), (q - p, 0.30, 0.34), STONE, bevel=0)
    if skirt: k.box(((x0 + x1) / 2, -0.03, -0.3), (x1 - x0, 0.46, 0.6), STONE, bevel=0)
    rnd = random.Random(seed); x = x0
    while x < x1 - 0.1:
        w = min(rnd.uniform(0.36, 0.6), x1 - x)
        if x1 - (x + w) < 0.24: w = x1 - x
        h = rnd.uniform(0.32, 0.46); d = rnd.uniform(0.26, 0.34)
        xc = x + w / 2
        sd = rnd.randrange(1 << 30)
        if not any(a < xc < b for a, b in gaps):
            rock(k, (xc, HUM_TF + 0.02, h / 2 - 0.07), (w - 0.04, d, h), seed=sd, tilt=0.06)
        x += w


def hum_wall_base(k, seed, gaps=(), core_gaps=(), sole_gaps=()):
    hum_plinth(k, seed=seed, gaps=gaps, core_gaps=core_gaps)
    xs = [-1.5] + [v for g_ in sole_gaps for v in g_] + [1.5]
    for i in range(0, len(xs), 2):
        a, b = xs[i], xs[i + 1]
        if b - a > 0.05: k.box(((a + b) / 2, HUM_TF + 0.14, 0.45), (b - a, 0.28, 0.2), WOOD, bevel=0.035, segs=2)
    hum_post(k, -1.5, 0.36, 2.32)
    hum_plate(k)


# ----------------------------------------------------------------- wattle walls
def hum_wall_wattle(k):
    sd = 11; panels = [(-1.5, 0.0), (0.0, 1.5)]
    hum_wall_base(k, sd)
    hum_daub(k, -1.5, 1.5, 0.55, 2.2, panels, seed=sd)
    hum_post(k, 0.0, 0.55, 2.22, w=0.18, d=0.27, tilt=0.015)
    hum_bar(k, -1.36, 0.6, -0.1, 1.98, w=0.15, d=0.24)
    hum_wall_patch(k, 0.78, 1.42, 0.64, 0.48, sd, panels)
    hum_wall_patch(k, -1.02, 1.72, 0.34, 0.28, sd + 5, panels)


def hum_wall_wattle_window(k):
    sd = 23; x0, x1, z0, z1 = -0.35, 0.35, 1.10, 1.65
    hum_wall_base(k, sd)
    hum_daub(k, -1.5, x0, 0.55, 2.2, [(-1.5, -0.42)], seed=sd)
    hum_daub(k, x1, 1.5, 0.55, 2.2, [(0.42, 1.5)], seed=sd + 1)
    hum_daub(k, x0, x1, 0.55, z0, None, seed=sd + 2, amp=0.008)
    hum_daub(k, x0, x1, z1, 2.2, None, seed=sd + 3, amp=0.0)
    for s in (-1, 1): hum_post(k, s * 0.43, 0.55, 2.22, w=0.16, d=0.27)
    k.box((0, HUM_TF + 0.1, z0 - 0.05), (1.02, 0.32, 0.09), WOOD, bevel=0.025, segs=2)      # sill
    hum_log(k, (0, HUM_TF + 0.08, z1 + 0.1), 0.1, 1.15, "X")                              # log lintel
    for x in (-0.12, 0.12): hum_rod(k, (x, -0.02, z0 - 0.01), (x, -0.02, z1 + 0.02), 0.024, segs=6)
    k.quad([(x0, 0.10, z0), (x1, 0.10, z0), (x1, 0.10, z1), (x0, 0.10, z1)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    # top-hinged board shutter propped open 55 degrees
    sub = Kit()
    for i in range(4): sub.box((-0.3 + i * 0.2, 0, -0.31), (0.19, 0.045, 0.62), PLANKS, bevel=0.012)
    for zz in (-0.12, -0.5): sub.box((0, 0.04, zz), (0.74, 0.04, 0.08), WOOD, bevel=0.012)
    sub.box((0, -0.03, -0.02), (0.84, 0.05, 0.06), IRON, bevel=0.01)
    merge_kit(k, sub, Matrix.Translation((0, -0.25, z1 + 0.27)) @ Matrix.Rotation(math.radians(-55), 4, "X"))
    zb = z1 + 0.27 - 0.62 * math.cos(math.radians(55)); yb = -0.25 - 0.62 * math.sin(math.radians(55))
    hum_rod(k, (0.28, -0.24, z0 - 0.02), (0.28, yb + 0.03, zb + 0.02), 0.022, segs=5)
    hum_wall_patch(k, -0.95, 0.95, 0.36, 0.3, sd + 7, [(-1.5, -0.42)])
    hum_bar(k, 0.55, 0.62, 1.38, 1.9, w=0.14, d=0.24)


def hum_wall_wattle_door(k):
    sd = 37; hw = 0.45; zt = 2.12
    hum_wall_base(k, sd, gaps=((-0.64, 0.64),), sole_gaps=((-0.56, 0.56),))
    hum_daub(k, -1.5, -hw, 0.55, 2.2, [(-1.5, -0.62)], seed=sd)
    hum_daub(k, hw, 1.5, 0.55, 2.2, [(0.62, 1.5)], seed=sd + 1)
    for s in (-1, 1): hum_post(k, s * 0.55, 0.36, 2.22, w=0.2, d=0.29)
    k.box((0, HUM_TF + 0.15, 2.2), (1.45, 0.34, 0.2), WOOD, bevel=0.045, segs=2)             # lintel
    rock(k, (0, -0.05, 0.31), (1.12, 0.5, 0.13), seed=91, tilt=0.01, segs=1)                 # threshold
    rock(k, (0.04, -0.55, 0.1), (0.95, 0.46, 0.24), seed=92, tilt=0.03)                      # step stone
    # dark interior box
    yb = 0.6
    k.quad([(-0.6, yb, 0.36), (0.6, yb, 0.36), (0.6, yb, 2.2), (-0.6, yb, 2.2)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.quad([(-hw, 0.12, 0.36), (-hw, yb, 0.36), (-hw, yb, 2.2), (-hw, 0.12, 2.2)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.quad([(hw, yb, 0.36), (hw, 0.12, 0.36), (hw, 0.12, 2.2), (hw, yb, 2.2)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.quad([(-hw, 0.1, 0.37), (hw, 0.1, 0.37), (hw, yb, 0.37), (-hw, yb, 0.37)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    # plank door ajar 25 degrees inward, hinged on the right jamb
    sub = Kit(); bw = 0.215
    for i in range(4):
        sub.box((-bw / 2 - i * bw, 0, 0.37 + (zt - 0.37) / 2 - 0.005 * (i % 2)), (bw - 0.012, 0.06, zt - 0.38 - 0.01 * (i % 2)), PLANKS, bevel=0.012)
    for zz in (0.72, 1.78):
        sub.box((-0.32, -0.04, zz), (0.62, 0.025, 0.075), IRON, bevel=0.01)
        _cyl(sub, (-0.62, -0.045, zz), 0.04, 0.04, 0.02, 8, IRON, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    ring(sub, (-0.74, -0.06, 1.2), 0.045, 0.07, 0.02, IRON, n=10, axis="Y")
    for zz in (0.62, 1.88): sub.box((-0.43, 0.045, zz), (0.8, 0.03, 0.11), WOOD, bevel=0.01)
    merge_kit(k, sub, Matrix.Translation((hw - 0.02, 0.06, 0)) @ Matrix.Rotation(math.radians(-25), 4, "Z"))
    hum_wall_patch(k, -1.0, 1.55, 0.36, 0.3, sd + 3, [(-1.5, -0.62)])
    hum_bar(k, 0.72, 0.6, 1.36, 1.7, w=0.14, d=0.24)


def hum_wall_wattle_byre(k):
    sd = 41; hw = 1.0; zs = 0.22; zt = 2.1
    hum_wall_base(k, sd, gaps=((-1.12, 1.12),), core_gaps=((-1.1, 1.1),), sole_gaps=((-1.12, 1.12),))
    hum_daub(k, -1.5, -hw, 0.55, 2.2, [(-1.5, -1.1)], seed=sd, amp=0.012)
    hum_daub(k, hw, 1.5, 0.55, 2.2, [(1.1, 1.5)], seed=sd + 1, amp=0.012)
    for s in (-1, 1): hum_post(k, s * 1.1, 0.12, 2.22, w=0.22, d=0.3)
    k.box((0, HUM_TF + 0.16, 2.17), (2.55, 0.34, 0.22), WOOD, bevel=0.045, segs=2)            # lintel
    k.box((0, -0.02, zs - 0.08), (2.3, 0.34, 0.16), WOOD, bevel=0.035, segs=1)                # sill beam
    # interior darkness
    yb = 0.8
    k.quad([(-hw, yb, 0.0), (hw, yb, 0.0), (hw, yb, zt), (-hw, yb, zt)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.quad([(-hw, 0.12, 0.0), (-hw, yb, 0.0), (-hw, yb, zt), (-hw, 0.12, zt)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.quad([(hw, yb, 0.0), (hw, 0.12, 0.0), (hw, 0.12, zt), (hw, yb, zt)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.quad([(-hw, 0.1, 0.23), (hw, 0.1, 0.23), (hw, yb, 0.23), (-hw, yb, 0.23)], HAY, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])

    def leaf(sign, z0, z1, M, braces=True):
        sub = Kit(); n = 3; bw = 0.98 / n
        for i in range(n):
            sub.box((sign * (bw / 2 + i * bw), 0, (z0 + z1) / 2), (bw - 0.014, 0.06, z1 - z0 - 0.012 * (i % 2)), PLANKS, bevel=0.012)
        for zz in (z0 + 0.14, z1 - 0.14): sub.box((sign * 0.49, -0.045, zz), (0.9, 0.035, 0.1), WOOD, bevel=0.012)
        if braces:
            L = math.hypot(0.75, z1 - z0 - 0.35); ang = math.atan2(z1 - z0 - 0.35, 0.75) * sign
            sub.box((sign * 0.49, -0.05, (z0 + z1) / 2), (L, 0.03, 0.09), WOOD, rot=(0, -ang, 0), bevel=0.01)
        for zz in (z0 + 0.14, z1 - 0.14): sub.box((sign * 0.2, -0.07, zz), (0.36, 0.02, 0.06), IRON, bevel=0.0)
        merge_kit(k, sub, M)
    for s in (-1, 1):
        leaf(-s, zs, 1.22, Matrix.Translation((s * hw, -0.02, 0)))                                  # lower leaves closed
        leaf(-s, 1.27, zt - 0.03, Matrix.Translation((s * hw, -0.12, 0)) @ Matrix.Rotation(-s * math.pi / 2 * -1, 4, "Z"), braces=False)
    # hay: tuft inside behind the half doors + spill on the trodden earth
    _ico(k, (0.25, 0.35, 1.18), 0.34, HAY, (1.5, 0.8, 0.65), sub=2, jit=0.04, seed=3)
    for i, (x, y, s_) in enumerate(((-0.45, -0.45, 0.3), (0.15, -0.6, 0.36), (0.6, -0.4, 0.24), (-0.05, -0.95, 0.2))):
        _ico(k, (x, y, 0.03), s_, HAY, (1.5, 1.0, 0.28), sub=2, jit=0.03, seed=10 + i)


def hum_wall_wattle_frame(k):
    """stage-1 piece: footing, plates and posts, woven panel to z 1.3, bare stakes above"""
    sd = 53; rnd = random.Random(sd)
    hum_wall_base(k, sd)
    hum_post(k, 0.0, 0.55, 2.22, w=0.18, d=0.27)
    k.box((0, -0.02, 0.925), (3.0, 0.1, 0.75), WATTLE, bevel=0.0)
    k.box((0, -0.02, 1.31), (3.0, 0.12, 0.04), WATTLE, bevel=0.01)
    for i in range(10):
        x = -1.35 + i * 0.3
        if abs(x) < 0.12: continue
        hum_rod(k, (x, -0.02, 0.55), (x + rnd.uniform(-0.04, 0.04), -0.02 + rnd.uniform(-0.04, 0.03), 2.1 + rnd.uniform(-0.1, 0.05)), 0.026, 0.02, segs=5)
    # bundle of withies leaning on the wall
    for i in range(6):
        x = 0.72 + i * 0.07 + rnd.uniform(-0.02, 0.02)
        hum_rod(k, (x, -0.72 + rnd.uniform(-0.05, 0.05), 0.0), (x + rnd.uniform(-0.15, 0.15), -0.22, 1.95 + rnd.uniform(0, 0.2)), 0.022, 0.016, segs=5)
    hum_rod(k, (0.7, -0.6, 0.55), (1.2, -0.52, 0.52), 0.035, segs=6, mi=BURLAP)


def hum_corner_wattle(k):
    rock(k, (-0.1, -0.1, 0.17), (0.64, 0.64, 0.44), seed=5, tilt=0.03)
    k.box((-0.08, -0.08, -0.3), (0.62, 0.62, 0.6), STONE, bevel=0)
    k.box((-0.1, -0.1, 1.36), (0.28, 0.28, 2.1), WOOD, bevel=0.05, segs=2)
    k.box((-0.2, HUM_TF + 0.15, 2.3), (0.66, 0.30, 0.2), WOOD, bevel=0.04, segs=2)
    k.box((HUM_TF + 0.15, -0.2, 2.3), (0.30, 0.66, 0.2), WOOD, bevel=0.04, segs=2)
    k.box((-0.12, HUM_TF + 0.14, 0.45), (0.44, 0.28, 0.2), WOOD, bevel=0.035, segs=2)
    k.box((HUM_TF + 0.14, -0.12, 0.45), (0.28, 0.44, 0.2), WOOD, bevel=0.035, segs=2)


def hum_inner_corner_wattle(k):
    rock(k, (0.14, 0.14, 0.15), (0.42, 0.42, 0.36), seed=7, tilt=0.03)
    k.box((0.13, 0.13, -0.3), (0.36, 0.36, 0.6), STONE, bevel=0)                          # hidden skirt
    k.box((0.1, 0.1, 1.36), (0.24, 0.24, 2.1), WOOD, bevel=0.045, segs=2)


# ----------------------------------------------------------------- cruck thatch gable
def hum_bez(P0, P1, P2, t):
    a = (1 - t) ** 2; b = 2 * t * (1 - t); c = t * t
    return (a * P0[0] + b * P1[0] + c * P2[0], a * P0[1] + b * P1[1] + c * P2[1])


def hum_under(ay):
    return roof_z(ay) - RT / math.cos(PITCH) - 0.05


HUM_CRUCK_P = ((2.75, -2.4), (2.95, 0.2), (0.0, 3.36))


def hum_gable_cruck(k):
    XC = HUM_CRUCK_X; XD = XC - 0.09; YC = HALF + 0.02
    ys = [2.8, 2.5, 2.0, 1.5, 1.0, 0.5, 0.0]
    outline = [(-YC, 0.0), (YC, 0.0)] + [(y, max(0.02, hum_under(y))) for y in ys] + [(-y, max(0.02, hum_under(y))) for y in ys[::-1][1:]]
    for xf, out in ((XD, 1), (1.45, -1)):
        vs = [k.bm.verts.new((xf, y, z)) for y, z in outline]
        f = k.bm.faces.new(vs); k.bm.normal_update()
        if f.normal.x * out < 0: f.normal_flip()
        f.material_index = PLASTER
        for l in f.loops: l[k.uv].uv = (l.vert.co.y / TILE[PLASTER], l.vert.co.z / TILE[PLASTER])
    k.bm.normal_update()
    P0, P1, P2 = HUM_CRUCK_P
    n = 8
    for s in (-1, 1):
        pts = [hum_bez(P0, P1, P2, i / n) for i in range(n + 1)]
        for i in range(n):
            (ya, za), (yb, zb) = pts[i], pts[i + 1]
            L = math.hypot(yb - ya, zb - za) + (0.1 if i < n - 1 else 0.28)
            ang = math.atan2(zb - za, s * (yb - ya))
            yc = s * (ya + yb) / 2; zc = (za + zb) / 2
            k.box((XC + 0.01 * s, yc, zc), (0.26, L, 0.32), WOOD, rot=(ang, 0, 0), bevel=0.06, segs=1)
        rock(k, (XC, s * P0[0], -HUM_HW + 0.1), (0.56, 0.56, 0.3), seed=40 + s, tilt=0.03)
    # tie beam on the wall plate, collar
    k.box((XC + 0.06, 0, 0.07), (0.24, 2 * YC + 0.14, 0.26), WOOD, bevel=0.05, segs=2)
    zc_ = 1.55; t = 0.5
    for _ in range(30):
        y_, z_ = hum_bez(P0, P1, P2, t)
        t += (zc_ - z_) * 0.08
    yc_ = hum_bez(P0, P1, P2, t)[0]
    k.box((XC + 0.08, 0, zc_), (0.2, 2 * yc_ + 0.4, 0.22), WOOD, bevel=0.04, segs=2)
    # smoke hole under the apex
    zv = hum_under(0) - 0.62
    k.quad([(XD + 0.005, -0.24, zv - 0.17), (XD + 0.005, 0.24, zv - 0.17), (XD + 0.005, 0.24, zv + 0.17), (XD + 0.005, -0.24, zv + 0.17)],
           VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    k.box((XD + 0.05, 0, zv - 0.21), (0.12, 0.62, 0.08), WOOD, bevel=0.02)
    for yy in (-0.27, 0.27): k.box((XD + 0.05, yy, zv), (0.1, 0.07, 0.42), WOOD, bevel=0.02)
    # daub gives way to the wattle here and there
    hum_patch(k, (XD, -0.95, 0.8), (0, 1, 0), (0, 0, 1), (1, 0, 0), 0.62, 0.46, seed=5)
    hum_patch(k, (XD, 0.62, 2.25), (0, 1, 0), (0, 0, 1), (1, 0, 0), 0.34, 0.28, seed=9)


def hum_roof_thatch_cruck(k):
    for s in (-1, 1):
        thatch_slab(k, -1.5, GX, s, end_caps=(False, True)); thatch_eave_roll(k, -1.5, GX, s, seed=1.0 + s)
    thatch_ridge_cap(k, -1.5, GX + 0.05)
    thatch_rake_roll(k, GX, seed=2.0)
    hum_gable_cruck(k)


# ----------------------------------------------------------------- ridge smoke vent
def hum_roof_thatch_vent(k):
    """origin at the ridge apex (placed at wall_top + RIDGE): lifted thatch bonnet over a dark smoke gap"""
    # saddle-shaped thatch hump growing out of the ridge cap
    hum_sq(k, (0, 0, 0.05), (0.82, 0.62, 0.4), e=0.85, nu=14, nv=7, mi=THATCH,
           warp=lambda p: Vector((p.x, p.y, p.z - 0.85 * abs(p.y))))
    # dark smoke slots on both sides, between hump and bonnet
    k.box((0, 0, 0.18), (0.74, 0.4, 0.76), VOID, bevel=0.0)                          # z -0.2..0.56
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.box((sx * 0.34, sy * 0.19, 0.4), (0.09, 0.09, 0.24), WOOD, bevel=0.02)
    # lifted bonnet
    hum_sq(k, (0, 0, 0.52), (0.84, 0.62, 0.4), e=0.85, nu=14, nv=8, mi=THATCH,
           disp=lambda n: 1.0 + 0.04 * math.sin(9 * n.x + 1.3) * math.sin(7 * n.y), flat_below=-0.02)
    # bound straw knob and a ligger around the rim
    _ico(k, (0, 0, 0.94), 0.13, THATCH, (1.3, 1, 0.8), sub=2, jit=0.015, seed=4)
    hum_rod(k, (0, 0, 0.88), (0.02, 0, 1.2), 0.03, 0.02, segs=5)
    pts = [(math.cos(2 * math.pi * i / 16) * 0.82, math.sin(2 * math.pi * i / 16) * 0.6, 0.53) for i in range(17)]
    hum_tube(k, pts, 0.025, segs=5, mi=WOOD)


# ----------------------------------------------------------------- low thatch lean-to
def hum_thatch_sheet(k, x0, x1, y0, y1, zfun, th=0.3, seed=0.0, step=0.3, rsegs=10, knob_sub=2):
    """thatch slab from back y0 to front y1, underside z=zfun(y); rolls on front and rakes"""
    nx = max(2, int(round((x1 - x0) / step))); ny = max(2, int(round(abs(y1 - y0) / step)))
    xs = [x0 + (x1 - x0) * i / nx for i in range(nx + 1)]; ys = [y0 + (y1 - y0) * j / ny for j in range(ny + 1)]
    T = TILE[THATCH]; slope = math.hypot(1, (zfun(y1) - zfun(y0)) / (y1 - y0))
    top = {}; bot = {}
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            zb = zfun(y)
            bump = 0.035 * _pnoise(x * 1.1 + 0.9 * j, seed) if (0 < i < nx and 0 < j < ny) else 0.0
            top[i, j] = k.bm.verts.new((x, y, zb + th + bump)); bot[i, j] = k.bm.verts.new((x, y, zb))
    fs_t = []; fs_b = []
    for i in range(nx):
        for j in range(ny):
            fs_t.append(k.bm.faces.new((top[i, j], top[i + 1, j], top[i + 1, j + 1], top[i, j + 1])))
            fs_b.append(k.bm.faces.new((bot[i, j + 1], bot[i + 1, j + 1], bot[i + 1, j], bot[i, j])))
    k.bm.normal_update()
    for f in fs_t:
        if f.normal.z < 0: f.normal_flip()
    for f in fs_b:
        if f.normal.z > 0: f.normal_flip()
    for f in fs_t + fs_b:
        f.material_index = THATCH
        for l in f.loops: l[k.uv].uv = (l.vert.co.x / T, abs(l.vert.co.y - y1) * slope / T)
    # back edge closed (rakes and front get rolls)
    for i in range(nx):
        f = k.bm.faces.new((top[i, 0], top[i + 1, 0], bot[i + 1, 0], bot[i, 0])); f.material_index = THATCH
    k.bm.normal_update()
    zf = zfun(y1) + th / 2; R = th / 2 + 0.07
    front = [(x, y1 - 0.03, zf) for x in xs]
    front = [(x0 - 0.12, y1 - 0.03, zf)] + front + [(x1 + 0.12, y1 - 0.03, zf)]
    hum_tube(k, front, [R * (1 + 0.1 * _pnoise(p[0] * 1.7, seed)) for p in front], segs=rsegs, mi=THATCH)
    for xe in (x0, x1):
        side = [(xe, y, zfun(y) + th / 2) for y in ys]
        hum_tube(k, side, [R * 0.9 * (1 + 0.08 * _pnoise(p[1] * 1.9, seed + xe)) for p in side], segs=rsegs, mi=THATCH)
        _ico(k, (xe, y1 - 0.03, zf), R * 1.1, THATCH, sub=knob_sub, jit=0.02, seed=int(xe * 10) + 7)


def hum_leanto_thatch_low(k):
    """wall-local lean-to (outer = -Y) whose back beam rests on a 2.4 m wattle wall plate;
    fits under a cruck/thatch gable (place centred on the gable end)"""
    yf = -2.45; zft = 2.1; ybk = -0.04; zbt = 2.64
    s = (zbt - zft) / (ybk - yf)

    def z_raft(y): return zft + (y - yf) * s                   # top of the beams line
    for sx in (-1, 1):
        rock(k, (sx * 1.42, yf, 0.07), (0.44, 0.44, 0.3), seed=60 + sx, tilt=0.03)
        k.box((sx * 1.42, yf, -0.3), (0.4, 0.4, 0.6), STONE, bevel=0)                        # hidden skirt
        k.box((sx * 1.42, yf, 1.03), (0.2, 0.2, 1.9), WOOD, bevel=0.04, segs=2)
        k.box((sx * 1.42, -0.34, 1.25), (0.18, 0.18, 2.36), WOOD, bevel=0.04, segs=2)
        hum_rod(k, (sx * 1.42, yf, 1.45), (sx * 0.95, yf, 1.98), 0.05, segs=6)
        hum_rod(k, (sx * 1.42, yf + 0.05, 1.5), (sx * 1.42, yf + 0.55, 2.02), 0.045, segs=6)
    k.box((0, yf, zft - 0.11), (3.3, 0.22, 0.22), WOOD, bevel=0.04, segs=2)
    k.box((0, ybk, zbt - 0.12), (3.3, 0.26, 0.24), WOOD, bevel=0.04, segs=2)
    for x in (-1.35, -0.45, 0.45, 1.35):
        hum_rod(k, (x, 0.22, z_raft(0.22) + 0.05), (x, -2.98, z_raft(-2.98) + 0.05), 0.065, segs=6)
    hum_thatch_sheet(k, -1.62, 1.62, 0.22, -2.9, lambda y: z_raft(y) + 0.1, th=0.32, seed=3.0)


# ----------------------------------------------------------------- livestock (face +X, origin at the feet)
def hum_leg(k, top, knee, foot, r_top, r_knee, r_foot, mi=HIDE, lower=None, hoof=COAL, hoof_r=None, hoof_h=0.09, segs=8):
    lower = mi if lower is None else lower
    top = Vector(top); knee = Vector(knee); foot = Vector(foot)
    hum_rod(k, top, knee, r_top, r_knee, segs, mi)
    _ico(k, knee, r_knee * 1.05, mi if lower == mi else lower, sub=1)
    hum_rod(k, knee, foot + Vector((0, 0, hoof_h * 0.6)), r_knee, r_foot, segs, lower)
    if hoof is not None:
        hr = hoof_r or r_foot * 1.12
        _cyl(k, (foot.x, foot.y, hoof_h / 2), hr, hr * 0.9, hoof_h, segs, hoof)


def hum_animal_cow(k):
    """chunky Holstein cow: black and white patches, black head with a white blaze, pink muzzle and udder,
    cream horns, red collar with a bronze bell"""
    def bmat(n):
        if n.z < -0.72: return HUM_FUR
        v = noise.noise(Vector((n.x * 1.6 + 4.3, n.y * 1.6 + 1.1, n.z * 1.6 + 7.7)))
        return COAL if v > 0.1 else HUM_FUR

    def bwarp(p):
        u = p.x / 0.94
        if p.z > 0: p.z -= 0.07 * (1 - u * u)                          # sway back
        if p.z > 0 and u < -0.4: p.z += 0.09 * (-u - 0.4) / 0.6         # hip bones
        if p.z < 0: p.z *= 1.0 + 0.14 * (1 - u * u)                    # round belly
        return p
    hum_sq(k, (0, 0, 1.06), (0.92, 0.45, 0.45), e=0.86, nu=14, nv=9, mat=bmat, warp=bwarp)
    hum_sq(k, (0.8, 0, 1.14), (0.3, 0.3, 0.34), e=0.85, nu=10, nv=6,
           mat=lambda n: HUM_FUR if n.z < -0.3 else COAL)                                                  # neck/shoulder
    hum_sq(k, (0.92, 0, 0.84), (0.15, 0.13, 0.2), e=0.9, nu=6, nv=4, mi=HUM_FUR)                           # dewlap
    hc = Vector((1.16, 0, 1.2)); a = 0.62; d = Vector((math.cos(a), 0, -math.sin(a)))
    R = Matrix.Rotation(a, 3, "Y")
    hum_sq(k, hc, (0.31, 0.22, 0.23), e=0.75, nu=12, nv=7, rot=R,
           mat=lambda n: HUM_FUR if (n.z > 0.3 and abs(n.y) < 0.42) else COAL)
    mz = hc + d * 0.28
    hum_sq(k, mz, (0.13, 0.2, 0.16), e=0.8, nu=8, nv=5, mi=PIGSKIN, rot=R)
    for s in (-1, 1):
        _ico(k, mz + d * 0.1 + Vector((0.0, s * 0.08, 0.04)), 0.032, VOID, (1, 1, 0.7), sub=1)
        hum_eye(k, hc + Vector((0.02, s * 0.185, 0.09)), 0.042, out=(0.45, s, 0.15), mi=VOID, white=1.4)
        # horns: out sideways, tips curling forward and up
        pts = [hc + Vector(p) for p in ((-0.13, s * 0.12, 0.15), (-0.12, s * 0.32, 0.17), (-0.05, s * 0.46, 0.24), (0.05, s * 0.5, 0.35))]
        hum_tube(k, pts, [0.075, 0.058, 0.04, 0.014], segs=6, mi=HUM_FUR)
        _ico(k, pts[-1], 0.02, COAL, sub=1)
        # ears, below the horns, pink inside
        hum_sq(k, hc + Vector((-0.12, s * 0.31, 0.05)), (0.08, 0.14, 0.045), e=0.9, nu=8, nv=5, mi=COAL,
               rot=Matrix.Rotation(-s * 0.3, 3, "X"))
        hum_sq(k, hc + Vector((-0.1, s * 0.33, 0.052)), (0.05, 0.1, 0.02), e=0.9, nu=6, nv=4, mi=PIGSKIN,
               rot=Matrix.Rotation(-s * 0.3, 3, "X"))
    for i, (x, y) in enumerate(((0.0, 0), (-0.05, 0.07), (-0.04, -0.07))):
        _ico(k, hc + Vector((x - 0.1, y, 0.22)), 0.075, COAL, sub=1, jit=0.012, seed=i)       # forelock
    # legs
    for s in (-1, 1):
        hum_leg(k, (0.58, s * 0.25, 0.95), (0.6, s * 0.25, 0.48), (0.6, s * 0.25, 0.0), 0.14, 0.1, 0.09, mi=HUM_FUR)
        hum_leg(k, (-0.6, s * 0.25, 1.0), (-0.7, s * 0.25, 0.5), (-0.62, s * 0.25, 0.0), 0.16, 0.105, 0.09, mi=HUM_FUR)
    # udder
    hum_sq(k, (-0.42, 0, 0.66), (0.21, 0.18, 0.14), e=0.9, nu=10, nv=6, mi=PIGSKIN)
    for sx in (-1, 1):
        for sy in (-1, 1): hum_rod(k, (-0.42 + sx * 0.08, sy * 0.07, 0.57), (-0.42 + sx * 0.08, sy * 0.07, 0.48), 0.027, 0.02, 5, PIGSKIN)
    # tail with tuft
    hum_tube(k, [(-0.92, 0, 1.34), (-1.0, 0, 1.2), (-1.02, 0.01, 0.92), (-1.0, 0.03, 0.68)], 0.035, segs=6, mi=HUM_FUR)
    _ico(k, (-1.0, 0.03, 0.6), 0.08, COAL, (0.8, 0.8, 1.5), sub=2, jit=0.012, seed=2)
    # red collar and bronze bell
    col = [(0.9 + 0.07 * math.sin(a_), 0.315 * math.cos(a_), 1.1 + 0.35 * math.sin(a_)) for a_ in [2 * math.pi * i / 11 for i in range(12)]]
    hum_tube(k, col, 0.045, segs=6, mi=CLOTH_A)
    lathe(k, [(0.03, 0.0), (0.07, -0.03), (0.078, -0.12), (0.115, -0.21), (0.0, -0.21)], center=(0.85, 0, 0.77), segs=8, mi=BRONZE)


def hum_animal_sheep(k):
    """fluffy cream fleece, black face and legs"""
    def wool(n):
        return 1.0 + 0.075 * noise.noise(Vector((n.x * 3.4 + 2, n.y * 3.4 + 5, n.z * 3.4 + 1))) + 0.04 * math.sin(8 * n.x + 2) * math.sin(7 * n.y + 1)
    hum_sq(k, (0, 0, 0.66), (0.56, 0.4, 0.35), e=0.85, nu=16, nv=10, mi=CLOTH_B, disp=wool)
    hc = Vector((0.6, 0, 0.84)); a = 0.5; d = Vector((math.cos(a), 0, -math.sin(a))); R = Matrix.Rotation(a, 3, "Y")
    hum_sq(k, hc, (0.2, 0.13, 0.14), e=0.8, nu=10, nv=6, mi=COAL, rot=R)
    _ico(k, hc + Vector((-0.07, 0, 0.12)), 0.13, CLOTH_B, (1.0, 1.1, 0.75), sub=2, jit=0.015, seed=3)       # wool cap
    for s in (-1, 1):
        hum_sq(k, hc + Vector((-0.06, s * 0.17, 0.05)), (0.05, 0.12, 0.035), e=0.9, nu=8, nv=5, mi=COAL,
               rot=Matrix.Rotation(s * 0.45, 3, "X"))
        hum_eye(k, hc + Vector((0.05, s * 0.11, 0.05)), 0.03, out=(0.3, s, 0.1), mi=HUM_FUR, hl=False)
        _ico(k, hc + Vector((0.07, s * 0.13, 0.05)), 0.016, VOID, sub=1)
        for x in (0.3, -0.3):
            hum_leg(k, (x, s * 0.17, 0.5), (x + 0.01, s * 0.17, 0.24), (x, s * 0.17, 0.0), 0.05, 0.042, 0.038, mi=COAL, hoof=COAL, hoof_h=0.06)
    _ico(k, (-0.58, 0, 0.72), 0.1, CLOTH_B, (0.8, 0.9, 1.1), sub=2, jit=0.01, seed=6)


def hum_animal_pig(k):
    """round pink pig with muddy socks, flappy ears and a curly tail"""
    def pmat(n):
        v = noise.noise(Vector((n.x * 2.6 + 1, n.y * 2.6 + 3, n.z * 2.6)))
        return SOIL if (n.z < -0.3 and v > 0.05) or (n.z < -0.75) else PIGSKIN

    def pwarp(p):
        u = p.x / 0.62
        f = 1.0 + 0.06 * u
        p.y *= f; p.z *= f
        return p
    hum_sq(k, (0, 0, 0.48), (0.62, 0.37, 0.35), e=0.85, nu=16, nv=10, mat=pmat, warp=pwarp)
    hc = Vector((0.58, 0, 0.52))
    hum_sq(k, hc, (0.24, 0.27, 0.26), e=0.9, nu=12, nv=8, mi=PIGSKIN)
    _cyl(k, (0.82, 0, 0.47), 0.13, 0.12, 0.16, 12, PIGSKIN, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    for s in (-1, 1):
        _ico(k, (0.9, s * 0.045, 0.47), 0.03, VOID, (0.6, 1, 1.3), sub=1)
        hum_eye(k, (0.74, s * 0.15, 0.62), 0.035, out=(0.5, s, 0.1))
        k.box((0.64, s * 0.18, 0.76), (0.16, 0.18, 0.035), PIGSKIN, rot=(s * 0.5, -0.9, 0), bevel=0.015)
        for x in (0.32, -0.34):
            hum_leg(k, (x, s * 0.2, 0.35), (x, s * 0.2, 0.18), (x, s * 0.2, 0.0), 0.085, 0.07, 0.065, mi=PIGSKIN, lower=SOIL, hoof=COAL, hoof_h=0.05)
    pts = []
    for i in range(14):
        t = i / 13
        pts.append((-0.62 - 0.12 * t, 0.055 * math.cos(2 * math.pi * 1.6 * t), 0.62 + 0.055 * math.sin(2 * math.pi * 1.6 * t) + 0.05 * t))
    hum_tube(k, pts, 0.022, segs=5, mi=PIGSKIN)


def hum_animal_goat(k):
    """brown goat with a black dorsal stripe, dark legs, swept-back horns, beard and amber eyes"""
    def gmat(n):
        if n.z > 0.72 and abs(n.y) < 0.35: return COAL
        if n.z < -0.6: return HUM_FUR
        return HIDE
    hum_sq(k, (0, 0, 0.64), (0.46, 0.23, 0.25), e=0.72, nu=14, nv=9, mat=gmat)
    hum_sq(k, (0.4, 0, 0.84), (0.13, 0.12, 0.22), e=0.85, nu=10, nv=6, mi=HIDE, rot=Matrix.Rotation(0.55, 3, "Y"))
    hc = Vector((0.58, 0, 1.03)); a = 0.75; d = Vector((math.cos(a), 0, -math.sin(a))); R = Matrix.Rotation(a, 3, "Y")
    hum_sq(k, hc, (0.19, 0.1, 0.1), e=0.8, nu=10, nv=6, mi=HIDE, rot=R)
    hum_sq(k, hc + d * 0.17, (0.07, 0.08, 0.07), e=0.9, nu=8, nv=5, mi=HUM_FUR, rot=R)
    hum_sq(k, hc + d * 0.06 + Vector((0.0, 0, -0.13)), (0.035, 0.035, 0.08), e=0.9, nu=6, nv=4, mi=HUM_FUR,
           rot=Matrix.Rotation(-0.25, 3, "Y"))                                                            # beard tuft
    for s in (-1, 1):
        pts = [hc + Vector(p) for p in ((-0.04, s * 0.05, 0.08), (-0.06, s * 0.07, 0.19), (-0.13, s * 0.1, 0.27), (-0.23, s * 0.12, 0.28), (-0.29, s * 0.13, 0.22))]
        hum_tube(k, pts, [0.035, 0.03, 0.025, 0.017, 0.008], segs=6, mi=COAL)
        hum_sq(k, hc + Vector((-0.07, s * 0.14, 0.04)), (0.04, 0.1, 0.03), e=0.9, nu=8, nv=5, mi=HIDE, rot=Matrix.Rotation(-s * 0.2, 3, "X"))
        _ico(k, hc + Vector((0.0, s * 0.095, 0.04)), 0.03, YELLOW, sub=1)
        _ico(k, hc + Vector((0.012, s * 0.115, 0.04)), 0.014, COAL, (1, 0.6, 1.3), sub=1)
        for x in (0.26, -0.28):
            hum_leg(k, (x, s * 0.12, 0.52), (x + 0.01, s * 0.12, 0.26), (x, s * 0.12, 0.0), 0.05, 0.04, 0.035, mi=HIDE, lower=COAL, hoof=COAL, hoof_h=0.05)
    hum_rod(k, (-0.44, 0, 0.74), (-0.52, 0, 0.86), 0.04, 0.02, 6, HIDE)


def hum_animal_horse(k):
    """draft horse: buckskin body with black points (mane, tail, lower legs), white blaze,
    white feathered fetlocks, dark leather collar"""
    def bwarp(p):
        u = p.x / 0.92
        if p.z > 0: p.z -= 0.06 * (1 - u * u)                  # saddle dip
        if p.z > 0 and u < -0.45: p.z += 0.06 * (-u - 0.45) / 0.55
        f = 1.0 + 0.08 * max(0.0, u)                             # deep chest
        p.y *= f
        if p.z < 0: p.z *= f
        return p
    hum_sq(k, (0, 0, 1.28), (0.95, 0.43, 0.47), e=0.82, nu=14, nv=9, mi=HIDE, warp=bwarp)
    # thick arched neck as a tapered tube (withers -> poll)
    npts = [Vector(p) for p in ((0.5, 0, 1.5), (0.78, 0, 1.84), (0.98, 0, 2.06), (1.14, 0, 2.22))]
    nr = [0.36, 0.3, 0.25, 0.2]
    hum_tube(k, npts, nr, segs=10, mi=HIDE)
    hc = Vector((1.33, 0, 2.1)); a = 1.08; d = Vector((math.cos(a), 0, -math.sin(a))); R = Matrix.Rotation(a, 3, "Y")

    def hmat(n): return HUM_FUR if (n.z > 0.5 and abs(n.y) < 0.38) else HIDE
    hum_sq(k, hc, (0.37, 0.17, 0.2), e=0.75, nu=12, nv=7, mat=hmat, rot=R)
    mz = hc + d * 0.31
    hum_sq(k, mz, (0.15, 0.165, 0.16), e=0.8, nu=8, nv=5, mi=HUM_FUR, rot=R)
    for s in (-1, 1):
        _ico(k, mz + d * 0.1 + Vector((0.07, s * 0.08, 0.0)), 0.034, VOID, (1, 1, 0.7), sub=1)
        hum_eye(k, hc + Vector((-0.08, s * 0.17, 0.08)), 0.04, out=(0.3, s, 0.1), mi=VOID, white=1.3)
        hum_rod(k, hc + Vector((-0.24, s * 0.08, 0.2)), hc + Vector((-0.24, s * 0.12, 0.42)), 0.065, 0.012, 6, HIDE)
        for (x0, xk, xf) in ((0.6, 0.63, 0.63), (-0.62, -0.74, -0.66)):
            hum_leg(k, (x0, s * 0.24, 1.1), (xk, s * 0.24, 0.52), (xf, s * 0.24, 0.0), 0.2, 0.135, 0.12, mi=HIDE, lower=COAL, hoof=COAL, hoof_r=0.15, hoof_h=0.1, segs=7)
            _cyl(k, (xf, s * 0.24, 0.21), 0.2, 0.13, 0.24, 9, HUM_FUR)
            for i in range(3):
                aa = 2 * math.pi * i / 3 + 0.4
                _ico(k, (xf + math.cos(aa) * 0.13, s * 0.24 + math.sin(aa) * 0.13, 0.14), 0.075, HUM_FUR, (1, 1, 0.8), sub=1)
    # mane along the crest, forelock, tail
    up = Vector((-0.74, 0, 0.67))
    mane = [npts[i] + up * nr[i] * 0.88 for i in range(4)] + [hc + Vector((-0.12, 0, 0.3))]
    hum_tube(k, mane, [0.1, 0.13, 0.13, 0.12, 0.09], segs=8, mi=COAL, lump=0.3, seed=1.0)
    for i in range(3):
        p = (mane[i] + mane[i + 1]) / 2
        _ico(k, p + Vector((0.03, 0.09 * (-1) ** i, -0.1)), 0.09, COAL, (1.0, 0.6, 1.4), sub=1, jit=0.01, seed=i)
    _ico(k, hc + Vector((-0.02, 0, 0.26)), 0.1, COAL, (1.5, 0.8, 0.6), sub=1)
    hum_tube(k, [(-0.92, 0, 1.6), (-1.08, 0, 1.46), (-1.16, 0, 1.14), (-1.14, 0, 0.8), (-1.08, 0, 0.56)],
             [0.1, 0.13, 0.15, 0.14, 0.05], segs=8, mi=COAL, lump=0.25, seed=2.0)
    # padded draft collar around the neck base, bronze hames knobs
    ax = Vector((0.74, 0, 0.67)).normalized(); w = Vector((0.67, 0, -0.74)); C = Vector((0.72, 0, 1.76))
    col = [C + Vector((0, math.cos(a_) * 0.36, 0)) + w * math.sin(a_) * 0.4 for a_ in [2 * math.pi * i / 14 for i in range(15)]]
    hum_tube(k, col, 0.09, segs=6, mi=WOOD)
    for s in (-1, 1): hum_rod(k, C + Vector((0, s * 0.4, 0)) - w * 0.18, C + Vector((0, s * 0.38, 0)) - w * 0.46, 0.035, 0.02, 5, BRONZE)


def hum_hen(k, c, rot, col, seed=0, rooster=False, peck=False):
    sub = Kit(); s = 1.3 if rooster else 1.0
    hum_sq(sub, (0, 0, 0.25 * s), (0.17 * s, 0.125 * s, 0.13 * s), e=0.9, nu=8, nv=5, mi=col,
           warp=lambda p: Vector((p.x, p.y, p.z + (0.35 * max(0.0, -p.x)) * (1 if p.z > 0 else 0.4))))
    tail = COAL if rooster else col
    hum_sq(sub, (-0.16 * s, 0, 0.37 * s), (0.045 * s, 0.06 * s, 0.1 * s), e=0.9, nu=6, nv=4, mi=tail, rot=Matrix.Rotation(-0.5, 3, "Y"))
    if rooster:
        for i, yy in enumerate((-0.025, 0.0, 0.025)):
            pts = [(-0.17 * s, yy, 0.4 * s), (-0.24 * s, yy, 0.49 * s), (-0.31 * s, yy, 0.45 * s), (-0.33 * s, yy, 0.35 * s)]
            hum_tube(sub, pts, [0.02, 0.018, 0.013, 0.004], segs=4, mi=COAL if i != 1 else LEAF)
    hp = Vector((0.2 * s, 0, 0.3 * s)) if peck else Vector((0.14 * s, 0, 0.44 * s))
    neck = Vector((0.1 * s, 0, 0.33 * s))
    hum_sq(sub, (neck + hp) / 2, (0.055 * s, 0.055 * s, 0.07 * s), e=0.9, nu=6, nv=4, mi=col,
           rot=Matrix.Rotation(-0.6 if peck else 0.3, 3, "Y"))
    hum_sq(sub, hp, (0.07 * s, 0.06 * s, 0.07 * s), e=0.9, nu=6, nv=4, mi=col)
    fwd = Vector((0.6, 0, -0.8)).normalized() if peck else Vector((1, 0, 0))
    up = Vector((0.8, 0, 0.6)).normalized() if peck else Vector((0, 0, 1))
    hum_rod(sub, hp + fwd * 0.055 * s, hp + fwd * 0.11 * s, 0.022 * s, 0.004, 4, YELLOW)
    for i in range(1 if not rooster else 2):
        _ico(sub, hp + up * 0.07 * s + fwd * (0.0 - 0.035 * i) * s, (0.034 if not rooster else 0.038) * s, APPLE, (1.2, 0.8, 1.0), sub=1)
    _ico(sub, hp + fwd * 0.05 * s - up * 0.05 * s, 0.02 * s, APPLE, (1, 0.7, 1.4), sub=1)
    for sy in (-1, 1):
        sub.box(hp + Vector((0.025 * s, sy * 0.055 * s, 0.015 * s)), (0.022 * s, 0.012, 0.022 * s), COAL, bevel=0.0)
        hum_sq(sub, (-0.02 * s, sy * 0.11 * s, 0.27 * s), (0.1 * s, 0.03 * s, 0.07 * s), e=0.9, nu=6, nv=4, mi=col,
               rot=Matrix.Rotation(-0.25, 3, "Y"))
        hum_rod(sub, (0.0, sy * 0.045, 0.15 * s), (0.01, sy * 0.05, 0.0), 0.012 * s, 0.01, 3, YELLOW)
        sub.box((0.04, sy * 0.05, 0.008), (0.08, 0.05, 0.016), YELLOW, bevel=0.0)
    merge_kit(k, sub, Matrix.Translation(c) @ Matrix.Rotation(rot, 4, "Z"))


def hum_animal_chickens(k):
    """four hens, a rooster and a feed dish (fits 2.0 x 1.6)"""
    rnd = random.Random(12)
    spots = [(-0.7, -0.5, 0.4, HUM_FUR, False, True), (0.35, -0.7, 2.2, BREAD, False, False), (0.8, 0.25, 3.6, HUM_FUR, False, True),
             (-0.75, 0.45, 5.0, BREAD, False, False), (0.15, 0.1, 0.9, PUMPKIN, True, False)]
    for i, (x, y, r_, col, roo, peck) in enumerate(spots):
        hum_hen(k, (x, y, 0), r_, col, seed=i, rooster=roo, peck=peck)
    _cyl(k, (-0.3, -0.05, 0.04), 0.2, 0.24, 0.08, 10, WOOD)
    _cyl(k, (-0.3, -0.05, 0.085), 0.19, 0.19, 0.01, 10, HAY)
    for i in range(3):
        a_ = rnd.uniform(0, 6.28); rr = rnd.uniform(0.25, 0.55)
        _ico(k, (-0.3 + math.cos(a_) * rr, -0.05 + math.sin(a_) * rr, 0.01), 0.025, HAY, (1, 1, 0.4), sub=1)


# ----------------------------------------------------------------- animal props
def hum_prop_hayrack(k):
    """slatted V hay rack on four posts under a little thatch hood (2.2 x 1.1)"""
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.box((sx * 0.95, sy * 0.46, 0.98), (0.14, 0.14, 1.96), WOOD, bevel=0.035, segs=1)
            rock(k, (sx * 0.95, sy * 0.46, 0.05), (0.26, 0.26, 0.14), seed=int(10 + sx * 3 + sy), tilt=0.02, segs=1)
        k.box((sx * 0.95, 0, 1.9), (0.14, 1.12, 0.14), WOOD, bevel=0.03)
    k.box((0, 0, 0.5), (1.96, 0.16, 0.12), WOOD, bevel=0.03)
    for sy in (-1, 1): k.box((0, sy * 0.46, 1.3), (2.0, 0.12, 0.12), WOOD, bevel=0.03)
    for i in range(8):
        x = -0.77 + i * 0.22
        for sy in (-1, 1): hum_rod(k, (x, sy * 0.03, 0.54), (x, sy * 0.45, 1.3), 0.026, segs=4)
    k.box((0, 0, 0.36), (1.9, 0.9, 0.08), PLANKS, bevel=0.015)
    k.box((0, 0, 0.41), (1.8, 0.8, 0.06), HAY, bevel=0.02)
    # messy hay heaped in the V, a few stalks poking out
    rnd = random.Random(8)
    for i in range(5):
        x = -0.72 + i * 0.36 + rnd.uniform(-0.05, 0.05)
        _ico(k, (x, rnd.uniform(-0.08, 0.08), 1.22 + rnd.uniform(-0.03, 0.06)), rnd.uniform(0.29, 0.33), HAY,
             (1.0, 1.55, 0.85), sub=2, jit=0.035, seed=i)
    for i in range(8):
        x = rnd.uniform(-0.85, 0.85); a_ = rnd.uniform(0, 6.28)
        p0 = Vector((x, math.cos(a_) * 0.3, 1.3 + rnd.uniform(0, 0.12)))
        hum_rod(k, p0, p0 + Vector((rnd.uniform(-0.15, 0.15), math.cos(a_) * 0.28, rnd.uniform(0.02, 0.18))), 0.014, 0.008, 3, HAY)
    _ico(k, (0.5, -0.74, 0.02), 0.28, HAY, (1.5, 1.0, 0.25), sub=2, jit=0.03, seed=20)          # spilled hay
    # little thatch hood
    for sy in (-1, 1):
        hum_thatch_sheet(k, -1.22, 1.22, sy * 0.02, sy * 0.86, lambda y: 2.34 - 0.62 * abs(y), th=0.17, seed=3.0 + sy, step=0.42, rsegs=6, knob_sub=1)
        k.box((0, sy * 0.46, 1.95), (2.1, 0.1, 0.12), WOOD, bevel=0.025)
    hum_tube(k, [(-1.3, 0, 2.5), (0, 0, 2.52), (1.3, 0, 2.5)], 0.12, segs=8, mi=THATCH, lump=0.1, seed=4.0)
    for sx in (-1, 1): k.box((sx * 0.95, 0, 2.15), (0.12, 0.12, 0.4), WOOD, bevel=0.03)


def hum_prop_coop_wattle(k):
    """round woven chicken coop on stilts with a pointed thatch hat and a ramp (front -Y)"""
    R = 0.62; z0 = 0.46; h = 0.74
    for i in range(4):
        a_ = math.pi / 4 + i * math.pi / 2
        k.box((math.cos(a_) * 0.44, math.sin(a_) * 0.44, (z0 + 0.1) / 2), (0.11, 0.11, z0 + 0.1), WOOD, bevel=0.025)
        rock(k, (math.cos(a_) * 0.44, math.sin(a_) * 0.44, 0.04), (0.2, 0.2, 0.12), seed=30 + i, tilt=0.02, segs=1)
    _cyl(k, (0, 0, z0), 0.68, 0.68, 0.08, 14, PLANKS)
    lathe(k, [(R, z0), (R * 1.05, z0 + h * 0.5), (R * 0.97, z0 + h)], segs=14, mi=WATTLE)
    lathe(k, [(R * 0.93, z0 + h), (R * 1.0, z0 + h * 0.5), (R * 0.9, z0)], segs=14, mi=WATTLE)
    for zz in (z0 + 0.06, z0 + h - 0.04): ring(k, (0, 0, zz), R - 0.01, R + 0.05, 0.06, WOOD, n=14, axis="Z")
    # door hole facing -Y
    dz0 = z0 + 0.08; dz1 = z0 + 0.46
    pts = [(-0.16, dz0), (0.16, dz0), (0.16, dz1 - 0.1)] + [(0.16 * math.cos(math.pi * i / 6), dz1 - 0.1 + 0.12 * math.sin(math.pi * i / 6)) for i in range(1, 6)] + [(-0.16, dz1 - 0.1)]
    vs = [k.bm.verts.new((x, -R * 1.06, z)) for x, z in pts]
    f = k.bm.faces.new(vs); k.bm.normal_update()
    if f.normal.y > 0: f.normal_flip()
    f.material_index = VOID
    for l in f.loops: l[k.uv].uv = (l.vert.co.x, l.vert.co.z)
    _ico(k, (0.05, -R - 0.05, dz0 + 0.02), 0.13, HAY, (1.2, 0.7, 0.4), sub=2, jit=0.02, seed=5)
    # ramp
    L = math.hypot(0.95, dz0); ang = math.atan2(dz0, 0.95)          # high end at the door, foot 0.95 out
    k.box((0, -R - 0.475, dz0 / 2), (0.34, L + 0.05, 0.04), PLANKS, rot=(ang, 0, 0), bevel=0.01)
    for i in range(5):                                                # cleats on top of the plank
        yy = -R - 0.14 - i * 0.18; zz = dz0 * (1 - (-R - yy) / 0.95) + 0.035
        k.box((0, yy, zz), (0.32, 0.035, 0.03), WOOD, rot=(ang, 0, 0), bevel=0.005)
    # pointed thatch hat with a rolled rim
    zr = z0 + h - 0.06
    lathe(k, [(R + 0.3, zr), (R + 0.18, zr + 0.14), (0.42, zr + 0.5), (0.14, zr + 0.82), (0.0, zr + 0.9)], segs=14, mi=THATCH, smooth_=True)
    lathe(k, [(0.0, zr + 0.02), (R + 0.28, zr + 0.02)], segs=14, mi=THATCH)
    rim = [(math.cos(2 * math.pi * i / 16) * (R + 0.3), math.sin(2 * math.pi * i / 16) * (R + 0.3), zr) for i in range(17)]
    hum_tube(k, rim, 0.075, segs=6, mi=THATCH, lump=0.12, seed=2.0)
    ring(k, (0, 0, zr + 0.62), 0.28, 0.34, 0.06, WOOD, n=12, axis="Z")
    hum_rod(k, (0, 0, zr + 0.8), (0.03, 0, zr + 1.12), 0.035, 0.02, 5, WOOD)


def hum_deco_mudwallow(k):
    """trodden pig wallow (about 3.2 x 2.4): low SOIL pan with a lumpy rim, clods and a few straws.
    Sits on the ground (edge sinks to z -0.04), so it reads as mud from the colony camera"""
    rnd = random.Random(17); N = 22
    p1, p2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    rings = ((0.0, 0.035), (0.4, 0.03), (0.72, 0.045), (0.88, 0.085), (1.0, 0.05), (1.14, -0.04))
    verts = []
    for ri, (f, z) in enumerate(rings):
        row = []
        for j in range(N):
            a = 2 * math.pi * j / N
            rr = f * (1.0 + 0.16 * math.sin(2 * a + p1) + 0.09 * math.sin(3 * a + p2) + 0.05 * math.sin(7 * a))
            zz = z + (0.03 * _pnoise(j * 0.45, 3.0 + ri) if 2 <= ri <= 4 else 0.0)
            row.append(k.bm.verts.new((math.cos(a) * rr * 1.45, math.sin(a) * rr * 1.05, zz)))
            if ri == 0: break
        verts.append(row)
    fs = []
    c = verts[0][0]
    for j in range(N): fs.append(k.bm.faces.new((c, verts[1][j], verts[1][(j + 1) % N])))
    for ri in range(1, len(verts) - 1):
        for j in range(N):
            j2 = (j + 1) % N
            fs.append(k.bm.faces.new((verts[ri][j], verts[ri + 1][j], verts[ri + 1][j2], verts[ri][j2])))
    k.bm.normal_update()
    for f in fs:
        if f.normal.z < 0: f.normal_flip()
    k.bm.normal_update()
    k.project(fs, SOIL)
    for i in range(9):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(0.75, 1.1)
        _ico(k, (math.cos(a) * rr * 1.45, math.sin(a) * rr * 1.05, 0.05), rnd.uniform(0.08, 0.16), SOIL,
             (1.3, 1.0, 0.5), sub=1, jit=0.02, seed=i)
    for i in range(5):
        a = rnd.uniform(0, 6.28); rr = rnd.uniform(0.2, 0.9); p0 = Vector((math.cos(a) * rr * 1.4, math.sin(a) * rr, 0.05))
        b = rnd.uniform(0, 6.28)
        hum_rod(k, p0, p0 + Vector((math.cos(b) * 0.35, math.sin(b) * 0.35, 0.01)), 0.018, 0.012, 3, HAY)


# ----------------------------------------------------------------- builders
HUM_WALLS = {".": "SM_VK_Wall_Wattle", "W": "SM_VK_Wall_Wattle_Window", "D": "SM_VK_Wall_Wattle_Door",
             "B": "SM_VK_Wall_Wattle_Byre", "F": "SM_VK_Wall_Wattle_Frame"}
HUM_ENDS = {"cruck": "SM_VK_RoofThatch_Gable_Cruck", "planks": "SM_VK_RoofThatch_Gable_Planks",
            "gable": "SM_VK_RoofThatch_Gable", "hip": "SM_VK_RoofThatch_Hip"}
HUM_STYLE = {"plaster": "Daub", "roof": "Thatch"}


def hum_block(coll, origin, n, faces, ends=("cruck", "cruck"), style=None, vents=()):
    """wattle house, n cells along local X, 2 cells deep, thatch roof at HUM_HW.
    faces: {"F","B","L","R"} strings read left to right from outside (F = -Y long side, L = -X end).
    Doors (D, B) only on gable-type ends: raises ValueError on an eave wall or a hipped end."""
    if n < 2: raise ValueError("hum_block needs n >= 2 (single-bay thatch piece not in this set)")
    style = HUM_STYLE if style is None else style
    L = n * CELL; parts = []
    for side in ("F", "B"):
        if any(c in "DB" for c in faces.get(side, "")):
            raise ValueError(f"wattle door on eave wall {side}: the thatch eave roll hangs at ~1.7 m; put doors on gable ends")
    for side, e in (("L", ends[0]), ("R", ends[1])):
        if any(c in "DB" for c in faces.get(side, "")) and e not in ("cruck", "planks", "gable"):
            raise ValueError(f"wattle door under a {e} end ({side})")

    def P(nm, x, y, z, rot):
        o = place_v(coll, nm, x, y, z, rot, origin, style); parts.append(o); return o
    Fs = faces.get("F", "." * n); Bs = faces.get("B", "." * n); Ls = faces.get("L", ".."); Rs = faces.get("R", "..")
    for i, c in enumerate(Fs): P(HUM_WALLS[c], -L / 2 + 1.5 + 3 * i, -3, 0, 0)
    for i, c in enumerate(Bs): P(HUM_WALLS[c], L / 2 - 1.5 - 3 * i, 3, 0, 180)
    for j, c in enumerate(Ls): P(HUM_WALLS[c], -L / 2, 1.5 - 3 * j, 0, -90)
    for j, c in enumerate(Rs): P(HUM_WALLS[c], L / 2, -1.5 + 3 * j, 0, 90)
    for (cx, cy, r) in ((-L / 2, -3, 0), (L / 2, -3, 90), (L / 2, 3, 180), (-L / 2, 3, -90)):
        P("SM_VK_Corner_Wattle", cx, cy, 0, r)
    for i in range(n):
        x = -L / 2 + 1.5 + 3 * i
        if i == 0: P(HUM_ENDS[ends[0]], x, 0, HUM_HW, 180)
        elif i == n - 1: P(HUM_ENDS[ends[1]], x, 0, HUM_HW, 0)
        else: P("SM_VK_RoofThatch_Mid", x, 0, HUM_HW, 0)
    for i in vents:
        if (i == 0 and ends[0] == "hip") or (i == n - 1 and ends[1] == "hip"):
            raise ValueError("thatch vent on a hipped bay: the ridge does not reach the bay centre")
        P("SM_VK_RoofThatch_Vent", -L / 2 + 1.5 + 3 * i, 0, HUM_HW + RIDGE, 0)
    return parts


def hum_weeds(coll, origin, r, runs, p=0.55, parts=None):
    for (x, y, rot) in runs:
        if r.random() < p:
            o = place_v(coll, "SM_VK_Deco_Weeds", x, y, 0, rot, origin, {})
            if parts is not None: parts.append(o)


def hum_fence(coll, a, b, origin, gate_at=None, parts=None):
    """fence_run() that also returns/collects the placed instances"""
    a = Vector(a); b = Vector(b); n = max(1, round((b - a).length / 3)); d = (b - a) / n
    rot = math.degrees(math.atan2(d.y, d.x)); out = []
    for i in range(n):
        c = a + d * (i + 0.5)
        out.append(place_v(coll, "SM_VK_Prop_FenceGate" if gate_at == i else "SM_VK_Prop_Fence", c.x, c.y, 0, rot, origin, {}))
    if parts is not None: parts.extend(out)
    return out


def build_hovel(coll, origin, seed=0, variant="cruck"):
    """Hovel (T1, 4 beds): 2x2 wattle-and-daub hut under a thatch 'haystack', cruck gables, smoke vent.
    Lot 3x3 cells: x -6..3, y -6..3 (house x -3..3, y -3..3). The door is on the R gable end (x = 3) and
    faces the street; the L cell column is the yard, the y -6..-3 strip the garden.
    variant: "cruck" | "hip" (hipped L end, vent moves to bay 1) | "leanto" (LeanTo_Thatch_Low on the L gable end)"""
    r = random.Random(seed)
    ends = ("hip", "cruck") if variant == "hip" else ("cruck", "cruck")
    parts = hum_block(coll, origin, 2, {"F": ".W", "B": "..", "L": "..", "R": "DW"}, ends=ends,
                      vents=(1,) if variant == "hip" else (0,))

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    if variant == "leanto":
        P("SM_VK_LeanTo_Thatch_Low", -3.0, 0.0, 0, -90, HUM_STYLE)
        P("SM_VK_Prop_HayBale", -4.4, 0.45, 0, 90 + r.uniform(-4, 4))
        P("SM_VK_Prop_Sacks", -4.5, -0.8, 0, r.uniform(-20, 20))
    else:
        P("SM_VK_Prop_Woodpile", -4.45, 0.35, 0, 90, HUM_STYLE)
    P("SM_VK_Prop_ChickenCoop_Wattle", -5.5, -2.55, 0, -90)
    P("SM_VK_Animal_Chickens", -4.5, -4.75, 0, r.uniform(0, 360))
    P("SM_VK_Prop_GardenBed", -0.9, -5.0, 0, 0)
    P("SM_VK_Prop_Bench", 1.35, -3.62, 0, 0)
    P("SM_VK_Prop_Planter", 2.65, -3.5, 0, 0)
    P("SM_VK_Deco_Bush", 2.2, -5.1, 0, r.uniform(0, 360))
    hum_weeds(coll, origin, r, [(-1.5, -3.05, 0), (-1.5, 3.05, 180), (1.5, 3.05, 180), (3.05, 1.5, 90), (-3.05, 1.5, -90)], parts=parts)
    return parts


def build_longhouse(coll, origin, seed=0):
    """Longhouse (T1, 8 beds + 4 livestock): 5x2 thatch 'loaf' on 2.4 m daub walls, vents in bays 1 and 3.
    People end L (cruck gable, door at y +1.5), byre end R (plank gable, byre door at y -1.5).
    Lot 8x3 cells: x -10.5..13.5, y -6..3; fenced paddock x 7.5..13.5, y -6..3 in front of the byre door,
    gate on the far side (x 13.5)."""
    r = random.Random(seed)
    parts = hum_block(coll, origin, 5, {"F": ".W.W.", "B": "....W", "L": "D.", "R": "B."}, ends=("cruck", "planks"), vents=(1, 3))

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    # paddock
    hum_fence(coll, (7.5, -6.0), (13.5, -6.0), origin, parts=parts)
    hum_fence(coll, (7.5, 3.0), (13.5, 3.0), origin, parts=parts)
    hum_fence(coll, (13.5, -6.0), (13.5, 3.0), origin, gate_at=1, parts=parts)
    hum_fence(coll, (7.5, -6.0), (7.5, -3.0), origin, parts=parts)
    P("SM_VK_Prop_HayRack", 10.6, 1.75, 0, 0)
    P("SM_VK_Prop_Trough", 12.75, -3.9, 0, 90)
    P("SM_VK_Prop_HayBale", 8.7, -5.05, 0, 12)
    P("SM_VK_Animal_Cow", 9.9, -2.7, 0, 195 + r.uniform(-12, 12))
    P("SM_VK_Animal_Horse", 11.9, -0.3, 0, 250 + r.uniform(-10, 10))
    P("SM_VK_Animal_Sheep", 10.9, -4.9, 0, 20 + r.uniform(-20, 20))
    P("SM_VK_Animal_Sheep", 12.4, -1.9, 0, 205 + r.uniform(-20, 20))
    # people end: yard x -10.5..-7.5, front strip y -6..-3
    P("SM_VK_Prop_Bench", -8.05, -0.4, 0, -90)
    P("SM_VK_Prop_ChickenCoop_Wattle", -9.35, -2.6, 0, 180)
    P("SM_VK_Animal_Chickens", -9.3, -4.9, 0, r.uniform(0, 360))
    P("SM_VK_Prop_GardenBed", -4.5, -5.0, 0, 0)
    P("SM_VK_Prop_Woodpile", 1.5, -4.95, 0, 0, HUM_STYLE)
    P("SM_VK_Deco_Bush", -8.9, 2.3, 0, r.uniform(0, 360))
    hum_weeds(coll, origin, r, [(-6.0, -3.05, 0), (4.5, -3.05, 0), (-3.0, 3.05, 180), (3.0, 3.05, 180), (-7.55, -1.5, -90)], parts=parts)
    return parts


def build_pigsty(coll, origin, seed=0):
    """Pig sty (3x3 lot, x/y -4.5..4.5): 6x6 m yard in low dry-stone walls with a gate in front (-Y),
    wattle back wall carrying two thatch lean-tos (shelter over the back half), mud wallow, trough, 3 pigs"""
    r = random.Random(seed); parts = []

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    for x in (-1.5, 1.5):
        P("SM_VK_Wall_Wattle", x, 3.0, 0, 0, HUM_STYLE)
        P("SM_VK_LeanTo_Thatch_Low", x, 3.0, 0, 0, HUM_STYLE)
    for (x, y, rt) in ((-3.0, 1.5, 90), (-3.0, -1.5, 90), (3.0, 1.5, 90), (3.0, -1.5, 90), (-1.5, -3.0, 0)):
        P("SM_VK_LowWall", x, y, 0, rt)
    P("SM_VK_Prop_FenceGate", 1.5, -3.0, 0, 0)
    for (x, y) in ((-3.0, 3.0), (3.0, 3.0), (-3.0, -3.0), (3.0, -3.0), (0.0, -3.0), (-3.0, 0.0), (3.0, 0.0)):
        P("SM_VK_LowWall_Post", x, y, 0, 0)
    P("SM_VK_Deco_MudWallow", 0.3, -0.9, 0, r.uniform(-15, 15))
    P("SM_VK_Animal_Pig", -0.5, -1.2, 0, 20 + r.uniform(-20, 20))
    P("SM_VK_Animal_Pig", 1.3, -0.3, 0, 150 + r.uniform(-20, 20))
    P("SM_VK_Animal_Pig", -1.0, 1.7, 0, 260 + r.uniform(-20, 20))
    P("SM_VK_Prop_Trough", -1.55, -2.05, 0, 0)
    P("SM_VK_Prop_Sacks", 3.9, -2.2, 0, 30)
    P("SM_VK_Prop_HayBale", 3.9, 1.9, 0, 80)
    hum_weeds(coll, origin, r, [(-1.5, -3.4, 0), (-3.4, 1.5, -90), (3.4, -1.5, 90)], p=0.8, parts=parts)
    return parts


def build_sheepfold(coll, origin, seed=0):
    """Sheepfold (3x3 lot, x/y -4.5..4.5): fenced pen with a wattle back wall (daub side into the pen) carrying
    two thatch lean-to shelters, hay rack, trough, five sheep and a goat; gate in the front fence (-Y)"""
    r = random.Random(seed); parts = []

    def P(nm, x, y, z=0.0, rot=0.0, sty=None): o = place_v(coll, nm, x, y, z, rot, origin, sty or {}); parts.append(o); return o
    for x in (-3.0, 0.0, 3.0): P("SM_VK_Wall_Wattle", x, 4.5, 0, 0, HUM_STYLE)
    for x in (0.0, 3.0): P("SM_VK_LeanTo_Thatch_Low", x, 4.5, 0, 0, HUM_STYLE)
    P("SM_VK_Corner_Wattle", -4.5, 4.5, 0, 0, HUM_STYLE)
    P("SM_VK_Corner_Wattle", 4.5, 4.5, 0, 90, HUM_STYLE)
    hum_fence(coll, (-4.5, 4.2), (-4.5, -4.5), origin, parts=parts)
    hum_fence(coll, (4.5, -4.5), (4.5, 4.2), origin, parts=parts)
    hum_fence(coll, (-4.5, -4.5), (4.5, -4.5), origin, gate_at=1, parts=parts)
    P("SM_VK_Prop_HayRack", -3.0, 2.65, 0, 0)
    P("SM_VK_Prop_Trough", 2.2, -3.3, 0, 0)
    for i, (x, y) in enumerate(((-1.8, -1.2), (0.4, -0.2), (1.6, -2.0), (-0.6, 1.4), (2.4, 2.3))):
        P("SM_VK_Animal_Sheep", x, y, 0, r.uniform(0, 360))
    P("SM_VK_Animal_Goat", -3.1, -2.8, 0, r.uniform(0, 360))
    P("SM_VK_Prop_HayBale", 3.3, 1.2, 0, 10)
    return parts


# ----------------------------------------------------------------- specs
_hum_std = {}
_hum_ng = dict(wobble=False, grime=True)
_hum_nw = dict(wobble=False, grime=False)
WS_SPECS = [
    ("SM_VK_Wall_Wattle", hum_wall_wattle, _hum_std),
    ("SM_VK_Wall_Wattle_Window", hum_wall_wattle_window, _hum_std),
    ("SM_VK_Wall_Wattle_Door", hum_wall_wattle_door, _hum_std),
    ("SM_VK_Wall_Wattle_Byre", hum_wall_wattle_byre, _hum_std),
    ("SM_VK_Wall_Wattle_Frame", hum_wall_wattle_frame, _hum_std),
    ("SM_VK_Corner_Wattle", hum_corner_wattle, _hum_ng),
    ("SM_VK_InnerCorner_Wattle", hum_inner_corner_wattle, _hum_ng),
    ("SM_VK_RoofThatch_Gable_Cruck", hum_roof_thatch_cruck, _hum_nw),
    ("SM_VK_RoofThatch_Vent", hum_roof_thatch_vent, _hum_nw),
    ("SM_VK_LeanTo_Thatch_Low", hum_leanto_thatch_low, _hum_ng),
    ("SM_VK_Animal_Cow", hum_animal_cow, _hum_ng),
    ("SM_VK_Animal_Sheep", hum_animal_sheep, _hum_ng),
    ("SM_VK_Animal_Pig", hum_animal_pig, _hum_ng),
    ("SM_VK_Animal_Goat", hum_animal_goat, _hum_ng),
    ("SM_VK_Animal_Horse", hum_animal_horse, _hum_ng),
    ("SM_VK_Animal_Chickens", hum_animal_chickens, _hum_nw),
    ("SM_VK_Prop_HayRack", hum_prop_hayrack, _hum_ng),
    ("SM_VK_Prop_ChickenCoop_Wattle", hum_prop_coop_wattle, _hum_ng),
    ("SM_VK_Deco_MudWallow", hum_deco_mudwallow, _hum_ng),
]
EXTRA_SPECS += WS_SPECS
