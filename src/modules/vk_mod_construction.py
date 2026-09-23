# ===================== ws_construction  (agent "construction", prefix con_) =====================
# Construction stages + stock piles + settler camp + early work yard (spec M1, §5.7, M3 camp/early props, §7/§8).
# Executed after vk_helpers in the same namespace: every kit function / constant is available.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

def con_pick(name, fallback): return name if bpy.data.objects.get(name) else fallback

# ------------------------------------------------------------------ generic geometry helpers
def con_frame(p0, p1, up=None):
    """4x4 rotation whose local X runs p0->p1 and whose Z is as close to `up` as possible; returns (R, length)"""
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0; L = d.length; X = d / L
    u = Vector(up) if up is not None else Vector((0, 0, 1))
    if abs(X.dot(u.normalized())) > 0.98: u = Vector((0, 1, 0)) if abs(X.y) < 0.9 else Vector((1, 0, 0))
    Z = (u - X * X.dot(u)).normalized(); Y = Z.cross(X)
    return Matrix((X, Y, Z)).transposed().to_4x4(), L

def con_beam(k, p0, p1, w, h, mi=WOOD, bevel=0.03, up=None, ext=0.0, segs=1):
    """bevelled box from p0 to p1 (centre line); w = width across (local Y), h = depth (local Z, towards `up`)"""
    R, L = con_frame(p0, p1, up)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ R
    return k.box((0, 0, 0), (L + 2 * ext, w, h), mi, bevel=bevel, segs=segs, xform=M)

def con_cap_uv(k, f, c, Y, Z, r, sc=0.47):
    for l in f.loops:
        d = l.vert.co - c; l[k.uv].uv = (0.5 + d.dot(Y) / r * sc, 0.5 + d.dot(Z) / r * sc)

def con_pole(k, p0, p1, r, mi=BARK_BIRCH, segs=8, r1=None, tile=None, caps=True, cap_mi=None, noise_=0.0, seed=0, nring=2):
    """round pole p0->p1 with cylindrical UVs (U around, V along the axis); ENDGRAIN or `cap_mi` caps"""
    p0 = Vector(p0); p1 = Vector(p1); R, L = con_frame(p0, p1)
    X = R.col[0].xyz; Y = R.col[1].xyz; Z = R.col[2].xyz
    r1 = r if r1 is None else r1; t = tile or TILE.get(mi, 1.0)
    rnd = random.Random(seed); ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    rings = []; vs_all = []
    for j in range(nring):
        s = j / (nring - 1); p = p0 + (p1 - p0) * s; rr = r + (r1 - r) * s
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            q = rr * (1 + noise_ * (math.sin(3 * a + ph[0] + 5 * s) * 0.6 + math.sin(2 * a + ph[1] - 3 * s) * 0.4))
            v = k.bm.verts.new(p + (Y * math.cos(a) + Z * math.sin(a)) * q); ring.append(v)
        rings.append((ring, s * L)); vs_all += ring
    C = math.pi * (r + r1)
    for j in range(nring - 1):
        ra, va = rings[j]; rb, vb = rings[j + 1]
        for i in range(segs):
            i2 = (i + 1) % segs
            f = k.bm.faces.new((ra[i], ra[i2], rb[i2], rb[i])); f.material_index = mi
            u0 = i / segs * C / t; u1 = (i + 1) / segs * C / t
            for l, uv in zip(f.loops, ((u0, va / t), (u1, va / t), (u1, vb / t), (u0, vb / t))): l[k.uv].uv = uv
    if caps:
        cm = ENDGRAIN if cap_mi is None else cap_mi
        f = k.bm.faces.new(rings[-1][0]); f.material_index = cm; con_cap_uv(k, f, p1, Y, Z, r1)
        f = k.bm.faces.new(rings[0][0][::-1]); f.material_index = cm; con_cap_uv(k, f, p0, Y, Z, r)
    return vs_all

def con_log(k, p0, p1, r, seed=0, segs=10, mi=BARK_OAK, taper=0.93, noise_=0.06):
    """sawn log: slightly irregular bark tube, bevelled bark rim and ENDGRAIN faces at both ends"""
    p0 = Vector(p0); p1 = Vector(p1); R, L = con_frame(p0, p1)
    X = R.col[0].xyz; Y = R.col[1].xyz; Z = R.col[2].xyz
    rnd = random.Random(seed); ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    t = TILE.get(mi, 1.2)
    def rad(a, s):
        rr = r * (1 + (taper - 1) * s)
        return rr * (1 + noise_ * (0.6 * math.sin(3 * a + ph[0] + 2 * s) + 0.4 * math.sin(2 * a + ph[1] - 4 * s) + 0.3 * math.sin(5 * a + ph[2])))
    ss = [0.0, 0.5, 1.0]; rings = []
    for s in ss:
        p = p0 + (p1 - p0) * s
        rings.append([k.bm.verts.new(p + (Y * math.cos(2 * math.pi * i / segs) + Z * math.sin(2 * math.pi * i / segs)) * rad(2 * math.pi * i / segs, s)) for i in range(segs)])
    C = 2 * math.pi * r
    for j in range(len(ss) - 1):
        ra = rings[j]; rb = rings[j + 1]
        for i in range(segs):
            i2 = (i + 1) % segs
            f = k.bm.faces.new((ra[i], ra[i2], rb[i2], rb[i])); f.material_index = mi
            u0 = i / segs * C / t; u1 = (i + 1) / segs * C / t
            for l, uv in zip(f.loops, ((u0, ss[j] * L / t), (u1, ss[j] * L / t), (u1, ss[j + 1] * L / t), (u0, ss[j + 1] * L / t))): l[k.uv].uv = uv
    # bevelled ends: inner ring pulled in by 12% and 3 cm, ENDGRAIN disc (UVs sized so the painted bark rim shows)
    for (ring, p, sgn, s) in ((rings[0], p0, -1, 0.0), (rings[-1], p1, 1, 1.0)):
        inner = []
        for i, v in enumerate(ring):
            d = v.co - p; inner.append(k.bm.verts.new(p + d * 0.86 + X * sgn * 0.03))
        for i in range(segs):
            i2 = (i + 1) % segs
            q = (ring[i], ring[i2], inner[i2], inner[i]) if sgn > 0 else (ring[i2], ring[i], inner[i], inner[i2])
            f = k.bm.faces.new(q); f.material_index = ENDGRAIN; con_cap_uv(k, f, p, Y, Z, r, 0.5)
        f = k.bm.faces.new(inner if sgn > 0 else inner[::-1]); f.material_index = ENDGRAIN
        con_cap_uv(k, f, p + X * sgn * 0.03, Y, Z, r, 0.5)
    k.bm.normal_update()

def con_box_faces(k, vs):
    return list({f for v in vs for f in v.link_faces if f.is_valid})

def con_local_axes(rot, xform=None):
    R = Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X")
    if xform is not None: R = xform.to_3x3().to_4x4() @ R
    return [(R @ Vector(a)).normalized() for a in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]

def con_board(k, c, size, rot=(0, 0, 0), mi=PLANKS, col=None, seed=0, bevel=0.0, xform=None):
    """plank board whose long axis is local X; UVs put exactly one painted board of T_VK_Planks across its width"""
    rnd = random.Random(seed); col = rnd.randrange(8) if col is None else col
    vs = k.box(c, size, mi, rot=rot, bevel=bevel, xform=xform)
    A, B, Cz = con_local_axes(rot, xform)
    cc = Vector(c) if xform is None else xform @ Vector(c)
    t = TILE[PLANKS]; v0 = rnd.random()
    for f in con_box_faces(k, vs):
        n = f.normal
        for l in f.loops:
            p = l.vert.co - cc
            if abs(n.dot(A)) > 0.7:  u = (p.dot(B)) / t; v = p.dot(Cz) / t
            elif abs(n.dot(Cz)) > 0.5: u = p.dot(B) / size[1] * 0.105; v = p.dot(A) / t
            else:                    u = p.dot(Cz) / max(size[2], 1e-3) * 0.03; v = p.dot(A) / t
            l[k.uv].uv = ((col + 0.5) / 8 + u, v0 + v)
    return vs

# painted blocks of T_VK_Ashlar (u0,v0,u1,v1): one block face maps onto one painted block
#   (rects include half of the painted joint so every block gets a dark outline on its bevels)
CON_ASHLAR_LONG = [(0.435, 0.498, 0.692, 0.673), (0.686, 0.498, 0.941, 0.673), (0.421, 0.161, 0.676, 0.338), (0.671, 0.161, 0.925, 0.338)]
CON_ASHLAR_SHORT = [(0.343, 0.666, 0.547, 0.839), (0.338, 0.331, 0.544, 0.507), (0.543, 0.666, 0.747, 0.839)]
def con_ashlar_block(k, c, size, rot=(0, 0, 0), seed=0, bevel=0.035):
    rnd = random.Random(seed)
    vs = k.box(c, size, ASHLAR, rot=rot, bevel=bevel, segs=1)
    A = con_local_axes(rot); cc = Vector(c)
    rl = CON_ASHLAR_LONG[rnd.randrange(4)]; rs = CON_ASHLAR_SHORT[rnd.randrange(3)]; rt = CON_ASHLAR_LONG[rnd.randrange(4)]
    for f in con_box_faces(k, vs):
        nl = [abs(f.normal.dot(a)) for a in A]; ax = nl.index(max(nl))
        if ax == 2:   ua, va, rect = 0, 1, rt
        elif ax == 1: ua, va, rect = 0, 2, rl
        else:         ua, va, rect = 1, 2, rs
        for l in f.loops:
            p = l.vert.co - cc
            su = min(1, max(0, p.dot(A[ua]) / size[ua] + 0.5)); sv = min(1, max(0, p.dot(A[va]) / size[va] + 0.5))
            l[k.uv].uv = (rect[0] + (rect[2] - rect[0]) * su, rect[1] + (rect[3] - rect[1]) * sv)
    return vs

def con_rope(k, p0, p1, r=0.014, mi=HAY):
    return con_pole(k, p0, p1, r, mi=mi, segs=4, caps=False)

def con_brace2(k, x0, z0, x1, z1, y, d, w, mi=WOOD):
    L = math.hypot(x1 - x0, z1 - z0); ang = math.atan2(z1 - z0, x1 - x0)
    k.box(((x0 + x1) / 2, y, (z0 + z1) / 2), (L, d, w), mi, rot=(0, -ang, 0), bevel=0.03)

def con_skirt(k, x0, x1, y0, y1, z0=-0.6, z1=0.02, mi=SOIL):
    """hidden skirt: vertical faces around a footprint down to z0 (so the piece never floats on uneven terrain)"""
    P = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        (ax, ay), (bx, by) = P[i], P[(i + 1) % 4]
        f = k.bm.faces.new([k.bm.verts.new(p) for p in ((ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1))])
        f.material_index = mi
    k.bm.normal_update()

def con_tray(k, c, bot, top, h, t, mi=PLANKS, rim=WOOD):
    """hollow tapered tray (wheelbarrow / mortar tub): outer shell, inner shell, rim"""
    cx, cy, cz = c
    def ring(w, d, z): return [(cx - w / 2, cy - d / 2, z), (cx + w / 2, cy - d / 2, z), (cx + w / 2, cy + d / 2, z), (cx - w / 2, cy + d / 2, z)]
    ob = [k.bm.verts.new(p) for p in ring(bot[0], bot[1], cz)]
    ot = [k.bm.verts.new(p) for p in ring(top[0], top[1], cz + h)]
    ib = [k.bm.verts.new(p) for p in ring(bot[0] - 2 * t, bot[1] - 2 * t, cz + t)]
    it = [k.bm.verts.new(p) for p in ring(top[0] - 2 * t, top[1] - 2 * t, cz + h)]
    fs = [k.bm.faces.new(ob[::-1]), k.bm.faces.new(ib)]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(k.bm.faces.new((ob[i], ob[j], ot[j], ot[i])))
        fs.append(k.bm.faces.new((ib[j], ib[i], it[i], it[j])))
        fr = k.bm.faces.new((ot[i], ot[j], it[j], it[i])); fr.material_index = rim
    for f in fs: f.material_index = mi
    k.bm.normal_update(); k.project(fs, mi)
    k.project([f for f in k.bm.faces if f.material_index == rim and all(l[k.uv].uv.length == 0 for l in f.loops)], rim)

# ------------------------------------------------------------------ stage 0: site + foundations
def con_buildsite_cell(k, seed=3):
    rnd = random.Random(seed); H = 1.5; n = 6     # full cell so neighbouring cells tile seamlessly (edges at z 0.015)
    V = {}
    for i in range(n + 1):
        for j in range(n + 1):
            x = -H + 2 * H * i / n; y = -H + 2 * H * j / n
            edge = i in (0, n) or j in (0, n)
            V[i, j] = k.bm.verts.new((x, y, 0.015 if edge else 0.025 + 0.035 * rnd.random()))
    for i in range(n):
        for j in range(n):
            f = k.bm.faces.new((V[i, j], V[i + 1, j], V[i + 1, j + 1], V[i, j + 1])); f.material_index = SOIL
            for l in f.loops: l[k.uv].uv = (l.vert.co.x / 1.2, l.vert.co.y / 1.2)
    k.bm.normal_update()
    con_skirt(k, -H, H, -H, H, -0.6, 0.015)
    # plot border: 4 slightly skewed boards
    for s in (-1, 1):
        con_board(k, (rnd.uniform(-0.03, 0.03), s * 1.39, 0.035), (2.9, 0.12, 0.05), rot=(0, 0, rnd.uniform(-0.01, 0.01)), mi=WOOD, seed=seed + s)
        con_board(k, (s * 1.39, rnd.uniform(-0.03, 0.03), 0.04), (2.66, 0.12, 0.05), rot=(0, 0, math.pi / 2 + rnd.uniform(-0.01, 0.01)), mi=WOOD, seed=seed + 3 * s)
    # survey pegs with rag tags
    spots = [(-1.39, -1.39), (1.39, -1.39), (1.39, 1.39), (-1.39, 1.39), (0.0, -1.39), (-1.39, 0.0)]
    for i, (x, y) in enumerate(spots):
        h = rnd.uniform(0.28, 0.4)
        k.box((x, y, h / 2 - 0.05), (0.06, 0.06, h + 0.1), WOOD, rot=(rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), rnd.uniform(0, 1)), bevel=0.015)
        if i % 2 == 0: k.box((x + 0.05, y, h - 0.06), (0.1, 0.012, 0.09), CLOTH_A, rot=(0, 0.3, rnd.uniform(0, 3)), bevel=0)
    # clods and pebbles
    for i in range(7):
        x, y = rnd.uniform(-1.1, 1.1), rnd.uniform(-1.1, 1.1); s = rnd.uniform(0.12, 0.24)
        rock(k, (x, y, 0.03), (s, s * 0.8, s * 0.55), seed=seed * 50 + i, mi=SOIL if i % 3 else ROCK, segs=1)

def con_foundation_wall(k, seed=4):
    rnd = random.Random(seed)
    k.box((0, -0.05, 0.012), (3.0, 1.2, 0.024), SOIL, bevel=0)                       # dug trench
    stone_panel(k, -1.5, 1.5, -0.6, 0.45)
    plinth(k)
    x = -1.5
    while x < 1.4:                                                                   # inner face rocks
        w = min(rnd.uniform(0.45, 0.75), 1.5 - x)
        if 1.5 - (x + w) < 0.3: w = 1.5 - x
        h = rnd.uniform(0.32, 0.46)
        rock(k, (x + w / 2, 0.23, h / 2 - 0.06), (w - 0.06, 0.34, h), seed=rnd.randrange(1 << 30))
        x += w
    x = -1.5                                                                         # first course being laid
    while x < 1.35:
        w = rnd.uniform(0.38, 0.62)
        if x + w > 1.5: w = 1.5 - x
        if w > 0.2: rock(k, (x + w / 2, rnd.uniform(-0.06, 0.06), 0.47), (w - 0.07, rnd.uniform(0.32, 0.44), rnd.uniform(0.12, 0.2)), seed=rnd.randrange(1 << 30), tilt=0.05)
        x += w + rnd.uniform(0.0, 0.12)
    # setting-out stakes + string line (continuous across modules)
    for yy in (-0.9, 0.9):
        k.box((-1.5, yy, 0.27), (0.055, 0.055, 0.74), WOOD, rot=(rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04), 0.3), bevel=0.012)
    k.box((0, -0.9, 0.55), (3.0, 0.014, 0.014), PAPER, bevel=0)
    for i in range(3):                                                                # spoil clods along the trench
        rock(k, (rnd.uniform(-1.2, 1.2), rnd.choice((-0.55, 0.55)), 0.04), (0.22, 0.16, 0.1), seed=seed * 9 + i, mi=SOIL, segs=1)

def con_foundation_corner(k):
    k.box((-0.1, -0.1, 0.012), (1.4, 1.4, 0.024), SOIL, bevel=0)
    k.box((0, 0, -0.1), (0.8, 0.8, 1.0), STONE, bevel=0)
    rock(k, (-0.05, -0.05, 0.2), (1.0, 1.0, 0.45), seed=11, tilt=0.03)
    rock(k, (0.1, 0.05, 0.47), (0.5, 0.42, 0.18), seed=12, tilt=0.05)
    # batter-board corner: 3 stakes, 2 rails, strings meeting the wall strings at y=-0.9 / x=-0.9
    for (x, y) in ((-0.9, -0.9), (-0.9, -0.45), (-0.45, -0.9)):
        k.box((x, y, 0.27), (0.06, 0.06, 0.74), WOOD, bevel=0.012)
    k.box((-0.93, -0.66, 0.5), (0.03, 0.56, 0.1), WOOD, bevel=0.01)
    k.box((-0.66, -0.93, 0.5), (0.56, 0.03, 0.1), WOOD, bevel=0.01)
    k.box((-0.45, -0.9, 0.55), (0.9, 0.014, 0.014), PAPER, bevel=0)
    k.box((-0.9, -0.45, 0.55), (0.014, 0.9, 0.014), PAPER, bevel=0)

# ------------------------------------------------------------------ stage 1: part-built walls
def con_top_rocks(k, x0, x1, top, rnd, skip=()):
    """ragged last course along a column top"""
    x = x0 + 0.02
    while x < x1 - 0.12:
        w = min(rnd.uniform(0.22, 0.4), x1 - x - 0.02)
        if w < 0.14: break
        if not any(a - 0.05 < x + w / 2 < b + 0.05 for a, b in skip):
            h = rnd.uniform(0.14, 0.24)
            rock(k, (x + w / 2, rnd.uniform(-0.07, 0.07), top + h * 0.3), (w, rnd.uniform(0.3, 0.46), h), seed=rnd.randrange(1 << 30), tilt=0.06, segs=1)
        x += w + 0.02

def con_mortar_board(k, x, y, z, rnd):
    k.box((x, y, z + 0.02), (0.36, 0.34, 0.035), WOOD, rot=(0, 0, rnd.uniform(-0.4, 0.4)), bevel=0.01)
    rock(k, (x - 0.03, y + 0.02, z + 0.07), (0.2, 0.18, 0.08), seed=rnd.randrange(999), mi=PLASTER, segs=1)
    k.box((x + 0.1, y - 0.06, z + 0.06), (0.16, 0.09, 0.012), STEEL, rot=(0, 0.25, 0.6), bevel=0)
    k.box((x + 0.2, y - 0.14, z + 0.1), (0.1, 0.03, 0.03), WOOD, rot=(0, 0.25, 0.6), bevel=0.008)

def con_wall_stone_half(k, door=False, seed=1):
    rnd = random.Random(seed * 7 + 3); base = 1.2; hw = 0.68
    if not door:
        tops = [1.62, 1.45, 1.3, 1.25, 1.42, 1.62]
        tops = [t if i in (0, 5) else t + rnd.uniform(-0.08, 0.28) for i, t in enumerate(tops)]
        cols = [(-1.5 + 0.5 * i, -1.0 + 0.5 * i, tops[i]) for i in range(6)]
        stone_panel(k, -1.5, 1.5, -0.6, base)
        for (a, b, t) in cols: stone_panel(k, a, b, base, t)
        plinth(k); batter(k)
    else:
        cols = [(-1.5, -1.1, 1.62), (-1.1, -hw, 1.9), (hw, 1.1, 1.9), (1.1, 1.5, 1.62)]
        for (a, b, t) in cols: stone_panel(k, a, b, -0.6, t)
        stone_panel(k, -hw, hw, -0.6, 0.0)
        plinth(k, -1.5, -hw - 0.02); plinth(k, hw + 0.02, 1.5); batter(k)
        for s in (-1, 1):                                          # jamb stones as in Wall_Stone_Door
            for j, zz in enumerate((0.35, 1.05, 1.7)):
                k.box((s * (hw + 0.16), -0.3, zz), (0.34 if j % 2 else 0.46, 0.16, 0.62), STONE, bevel=0.05, segs=2)
        k.box((0, -0.02, 0.08), (2 * hw + 0.1, 0.5, 0.16), STONE, bevel=0.02)
        k.box((0, -0.55, 0.1), (1.7, 0.6, 0.2), STONE, bevel=0.05, segs=2, jitter=0.02, seed=3)
        # timber centring for the arch: 2 props, a sill and a half-round rib
        for s in (-1, 1):
            k.box((s * (hw - 0.09), 0.05, 1.0), (0.12, 0.12, 2.0), WOOD, bevel=0.02)
        k.box((0, 0.05, 2.05), (2 * hw + 0.12, 0.3, 0.1), WOOD, bevel=0.02)
        n = 7
        for i in range(n):
            a0 = math.pi * i / n; a1 = math.pi * (i + 1) / n; r = hw - 0.02
            p0 = (math.cos(a0) * r, 0.05, 2.1 + math.sin(a0) * r); p1 = (math.cos(a1) * r, 0.05, 2.1 + math.sin(a1) * r)
            con_beam(k, p0, p1, 0.28, 0.1, WOOD, bevel=0.015, up=(math.cos((a0 + a1) / 2), 0, math.sin((a0 + a1) / 2)), ext=0.02)
        con_beam(k, (-hw + 0.1, 0.05, 0.3), (hw - 0.1, 0.05, 1.8), 0.08, 0.1, WOOD, bevel=0.015)
    # ragged top course + loose blocks + mortar board
    idx = list(range(len(cols))); rnd.shuffle(idx)
    blk = idx[0]; mb = idx[1]
    for i, (a, b, t) in enumerate(cols):
        skip = [((a + b) / 2 - 0.25, (a + b) / 2 + 0.25)] if i in (blk, mb) else []
        con_top_rocks(k, a, b, t, rnd, skip)
    a, b, t = cols[blk]
    con_ashlar_block(k, ((a + b) / 2 + rnd.uniform(-0.03, 0.03), rnd.uniform(-0.04, 0.04), t + 0.15), (0.48, 0.3, 0.3), rot=(0, 0, rnd.uniform(-0.25, 0.25)), seed=seed)
    a, b, t = cols[mb]
    con_mortar_board(k, (a + b) / 2, rnd.uniform(-0.05, 0.05), t, rnd)
    # a block waiting at the wall foot
    con_ashlar_block(k, (rnd.uniform(-1.0, 1.0) if not door else rnd.choice((-1.15, 1.15)), 0.62, 0.15), (0.5, 0.3, 0.3), rot=(0, 0, rnd.uniform(-0.5, 0.5)), seed=seed + 5)

def con_corner_stone_half(k, top=1.62):
    k.box((0, 0, (top - 0.6) / 2), (0.8, 0.8, top + 0.6), STONE, bevel=0)
    rock(k, (-0.05, -0.05, 0.18), (1.05, 1.05, 0.42), seed=11, tilt=0.03)
    z = 0.36; i = 0; rnd = random.Random(5)
    while z < top - 0.12:
        h = min(rnd.uniform(0.38, 0.5), top - z)
        sx, sy = (1.05, 0.62) if i % 2 == 0 else (0.62, 1.05)
        rock(k, (-0.43 + sx / 2, -0.43 + sy / 2, z + h / 2), (sx, sy, h - 0.03), seed=i * 17 + 3, tilt=0.02, segs=2)
        z += h; i += 1
    rock(k, (0.12, 0.1, top + 0.08), (0.5, 0.45, 0.2), seed=71, tilt=0.06, segs=1)
    # next quoin waiting on the ground
    rock(k, (0.75, -0.75, 0.2), (1.0, 0.6, 0.4), seed=72, tilt=0.04, segs=2)

def con_wall_plaster_frame(k, door=False, seed=2):
    rnd = random.Random(seed)
    stone_panel(k, -1.5, 1.5, -0.6, PL, -0.28, 0.25); plinth(k); batter(k, 0.05)
    YC = -0.14; D = 0.4
    k.box((0, -0.2, PL + 0.1), (CELL, 0.4, 0.2), WOOD, bevel=0.035)
    k.box((0, -0.2, H1 - 0.11), (CELL, 0.4, 0.22), WOOD, bevel=0.035)
    k.box((-1.5, YC, (PL + H1) / 2), (0.24, D, H1 - PL - 0.2), WOOD, bevel=0.03)
    pegs(k, (-1.5,), (PL + 0.3, H1 - 0.35), y=-0.35)
    if not door:
        k.box((0, YC, (PL + H1) / 2), (0.22, D, H1 - PL - 0.2), WOOD, bevel=0.03)
        for s_ in (-1, 1): con_brace2(k, s_ * 1.35, PL + 0.25, s_ * 0.15, H1 - 0.3, YC, D - 0.06, 0.17)
        # one panel half woven: wattle up to ~1.7, bare staves above
        s = rnd.choice((-1, 1)); xa, xb = sorted((s * 1.38, s * 0.11)); zt = rnd.uniform(1.55, 1.8)
        vs = k.box(((xa + xb) / 2, 0.0, (PL + 0.2 + zt) / 2), (xb - xa, 0.08, zt - PL - 0.2), WATTLE, bevel=0)
        n = 5
        for i in range(n):
            x = xa + (i + 0.5) * (xb - xa) / n
            k.box((x, 0.0, (zt + H1 - 0.22) / 2), (0.035, 0.035, H1 - 0.22 - zt), WOOD, rot=(0, rnd.uniform(-0.03, 0.03), 0), bevel=0)
        k.box(((xa + xb) / 2, 0.0, zt + 0.02), (xb - xa, 0.1, 0.04), WATTLE, bevel=0.01)
    else:
        hw = 0.62; top = 2.3
        for s_ in (-1, 1): k.box((s_ * (hw + 0.11), YC, top / 2), (0.22, D, top), WOOD, bevel=0.035)
        k.box((0, -0.2, top + 0.12), (2 * hw + 0.6, 0.4, 0.26), WOOD, bevel=0.04)
        k.box((0, -0.5, 0.1), (1.5, 0.55, 0.2), STONE, bevel=0.05, segs=2, jitter=0.02, seed=5)
        for s_ in (-1, 1): con_brace2(k, s_ * 1.38, PL + 0.25, s_ * 0.85, top - 0.1, YC, D - 0.06, 0.16)
        # the door leaf, not hung yet, leaning against the wall
        sub = Kit()
        for i in range(4):
            sub.box((-2 * hw / 2 + (i + 0.5) * (2 * hw) / 4, 0, 1.1), ((2 * hw) / 4 - 0.015, 0.08, 2.2), WOOD, bevel=0.012)
        for zz in (0.45, 1.7): sub.box((0, -0.06, zz), (2 * hw - 0.1, 0.04, 0.12), WOOD, bevel=0.01)
        merge_kit(k, sub, Matrix.Translation((0.0, -0.75, 0.0)) @ Matrix.Rotation(0.17, 4, "X"))

def con_wall_timber_frame(k):
    k.box((0, -0.14, 0.15), (CELL, 0.52, 0.3), WOOD, bevel=0.04)              # belt beam
    for i in range(6): k.box((-1.25 + i * 0.5, -0.47, -0.1), (0.16, 0.3, 0.2), WOOD, bevel=0.03)
    k.box((0, -0.2, H2 - 0.1), (CELL, 0.46, 0.22), WOOD, bevel=0.04)           # top plate
    YC = -0.2; D = 0.42
    k.box((-1.5, YC, H2 / 2), (0.26, D, H2 - 0.4), WOOD, bevel=0.03)
    k.box((0, YC, H2 / 2), (0.22, D, H2 - 0.4), WOOD, bevel=0.03)
    for s in (-1, 1): con_brace2(k, s * 1.3, 0.35, s * 0.15, H2 - 0.25, YC, D - 0.06, 0.17)
    k.box((0, YC, 1.35), (CELL, D - 0.06, 0.16), WOOD, bevel=0.03)
    for s in (-1, 1): con_brace2(k, s * 1.36, H2 - 0.85, s * 0.92, H2 - 0.22, YC, D - 0.1, 0.13)   # knee braces
    pegs(k, (-1.5, 0.0), (0.42, H2 - 0.33))
    k.box((0, -0.42, 0.02), (CELL, 0.1, 0.06), WOOD, bevel=0.02)

# ------------------------------------------------------------------ stage 2: roof frames (follow roof_z exactly)
CON_BAT_TOP = 0.04     # batten top below the finished roof surface
CON_BAT_T = 0.05       # batten thickness
CON_RAF_D = 0.18       # rafter depth
CON_RAF_C = CON_BAT_TOP + CON_BAT_T + CON_RAF_D / 2      # rafter centre-line depth (0.18)
CON_PUR_C = CON_BAT_TOP + CON_BAT_T + CON_RAF_D + 0.09   # purlin centre-line depth
def con_nP(): return Vector((math.sin(PITCH), math.cos(PITCH)))
def con_nK(): return Vector((math.sin(KICK), math.cos(KICK)))
def con_off_z(ay, d):
    """z of the roof section offset inward by d (perpendicular), at plan distance ay from the ridge"""
    if ay <= HALF: return roof_z(ay) - d / math.cos(PITCH)
    return roof_z(ay) - d / math.cos(KICK)
def con_corner(d):
    """intersection (ay,z) of the pitch and kick offset lines at depth d"""
    c = Vector((HALF, roof_z(HALF)))
    p = c - con_nP() * d; u = Vector((math.cos(PITCH), -math.sin(PITCH)))
    q = c - con_nK() * d; v = Vector((math.cos(KICK), -math.sin(KICK)))
    den = u.x * v.y - u.y * v.x; w = q - p
    t = (w.x * v.y - w.y * v.x) / den
    r = p + u * t; return r.x, r.y
def con_rafter(k, x, s, w=0.12, d=CON_RAF_D, tail=EAVE - 0.2, head=0.0):
    ayc, zc = con_corner(CON_RAF_C)
    p0 = (x, s * head, con_off_z(head, CON_RAF_C)); p1 = (x, s * ayc, zc); p2 = (x, s * tail, con_off_z(tail, CON_RAF_C))
    con_beam(k, p0, p1, w, d, WOOD, bevel=0.025, up=(0, s * math.sin(PITCH), math.cos(PITCH)), ext=0.03)
    con_beam(k, p1, p2, w * 0.9, d * 0.85, WOOD, bevel=0.02, up=(0, s * math.sin(KICK), math.cos(KICK)), ext=0.02)
def con_beam_board(k, p0, p1, w, h, up=None, col=None, seed=0, bevel=0.0, mi=PLANKS):
    """plank board p0->p1 with one painted board of T_VK_Planks across its width (fresh sawn timber)"""
    R, L = con_frame(p0, p1, up)
    M = Matrix.Translation((Vector(p0) + Vector(p1)) / 2) @ R
    return con_board(k, (0, 0, 0), (L, w, h), mi=mi, col=col, seed=seed, bevel=bevel, xform=M)
CON_FRESH = (0, 1, 3, 5)     # golden columns of T_VK_Planks
def con_slope_x(k, x0, x1, s, ay, depth, w, h, mi=WOOD, bevel=0.0, seed=0):
    """member running along x on one slope at plan distance ay"""
    n = (0, s * math.sin(PITCH), math.cos(PITCH)) if ay <= HALF else (0, s * math.sin(KICK), math.cos(KICK))
    z = con_off_z(ay, depth)
    if mi == PLANKS:
        return con_beam_board(k, (x0, s * ay, z), (x1, s * ay, z), w, h, up=n, col=CON_FRESH[seed % 4], seed=seed, bevel=bevel)
    return con_beam(k, (x0, s * ay, z), (x1, s * ay, z), w, h, mi, bevel=bevel, up=n)
CON_BATTENS = [0.4, 1.0, 1.6, 2.2, 2.8, 3.55]
def con_roof_frame_bay(k, x0, x1, xs, joists=True, collars=True):
    for s in (-1, 1):
        for x in xs: con_rafter(k, x, s)
        for ay in (HALF / 3, 2 * HALF / 3): con_slope_x(k, x0, x1, s, ay, CON_PUR_C, 0.14, 0.18, WOOD, bevel=0.025)
        for i, ay in enumerate(CON_BATTENS): con_slope_x(k, x0, x1, s, ay, CON_BAT_TOP + CON_BAT_T / 2, 0.09, CON_BAT_T, PLANKS, bevel=0.0, seed=i * 3 + s + 7)
    k.box(((x0 + x1) / 2, 0, RIDGE - 0.45), (x1 - x0, 0.22, 0.30), WOOD, bevel=0.03)          # ridge beam
    for x in xs:
        if joists: k.box((x, 0, 0.1), (0.12, 6.3, 0.2), WOOD, bevel=0.025)                       # tie beam / ceiling joist
        if collars:
            zc = 2.35; ay = HALF - (zc - roof_z(HALF) + CON_RAF_C / math.cos(PITCH)) / math.tan(PITCH)
            k.box((x + 0.1, 0, zc), (0.06, 2 * ay + 0.1, 0.16), WOOD, bevel=0.015)
CON_XS = [-1.2, -0.6, 0.0, 0.6, 1.2]
def con_roof_mid_frame(k):
    con_roof_frame_bay(k, -1.5, 1.5, CON_XS)

def con_gable_truss(k, XF):
    """timber members of gable_end('timber') without infill or window"""
    def under(ay): return roof_z(ay) - RT / math.cos(PITCH) - 0.05
    YC = HALF + 0.02; top = under(0)
    k.box((XF - 0.02, 0, 0.12), (0.2, 2 * YC, 0.24), WOOD, bevel=0.04)
    for i in range(6): k.box((XF + 0.1, -2.5 + i * 1.0, -0.12), (0.3, 0.16, 0.2), WOOD, bevel=0.03)
    zc = top * 0.45; half_c = YC * (1 - zc / top) * 0.98
    k.box((XF - 0.02, 0, zc), (0.18, 2 * half_c, 0.2), WOOD, bevel=0.035)
    k.box((XF - 0.02, 0, top / 2), (0.18, 0.24, top), WOOD, bevel=0.035)
    for s_ in (-1, 1):
        L = math.hypot(YC, top); ang = math.atan2(top, YC)
        k.box((XF - 0.02, s_ * YC / 2, top / 2 - 0.14), (0.18, L, 0.2), WOOD, rot=(-s_ * ang, 0, 0), bevel=0.035)
        k.box((XF - 0.02, s_ * 1.6, zc / 2 + 0.1), (0.16, 0.16, zc - 0.1), WOOD, bevel=0.03)
        k.box((XF - 0.02, s_ * 0.8, (zc + 0.24) / 2 + 0.06), (0.14, 0.14, zc - 0.18), WOOD, bevel=0.03)
        con_beam(k, (XF - 0.02, s_ * 0.12, zc + 0.1), (XF - 0.02, s_ * 0.75, top - 0.62), 0.14, 0.14, WOOD, bevel=0.025, up=(1, 0, 0))

def con_bargeboards(k):
    prof = [(ay, roof_z(ay)) for ay in (0.0, HALF, EAVE)]     # the profile is two straight runs (pitch + kick)
    for s in (-1, 1):
        for j in range(len(prof) - 1):
            (y0, z0), (y1, z1) = prof[j], prof[j + 1]
            L = math.hypot(y1 - y0, z1 - z0); ang = math.atan2(z1 - z0, y1 - y0)
            k.box((GX + 0.08, s * (y0 + y1) / 2, (z0 + z1) / 2 - 0.16), (0.16, L + 0.12, 0.36), WOOD, rot=(s * ang, 0, 0), bevel=0.04)

def con_roof_gable_frame(k):
    con_roof_frame_bay(k, -1.5, GX, CON_XS)
    for s in (-1, 1): con_rafter(k, GX - 0.12, s, w=0.1)              # verge (flying) rafters
    k.box((GX + 0.06, 0, RIDGE - 0.45), (0.2, 0.26, 0.34), WOOD, bevel=0.04)   # ridge beam end
    con_gable_truss(k, 1.5 + 0.40)
    con_bargeboards(k)

def con_roof_hip_frame(k):
    """frame of Roof_Hip: apex at x=-1.5 (the bay seam), hips to the wall corners (1.5,+-3), end eave at x=1.5+OVER"""
    xa = XH - HALF; tail = EAVE - 0.2; ayc, zc = con_corner(CON_RAF_C)
    # common rafter pair at the apex
    for s in (-1, 1): con_rafter(k, xa + 0.07, s)
    # hip rafters on the diagonals (plan 45 deg), deeper section
    for s in (-1, 1):
        def P(a, zz): return (xa + a, s * a, zz)
        up = (0, 0, 1)
        con_beam(k, P(0.0, con_off_z(0.0, CON_RAF_C) - 0.03), P(ayc, zc - 0.03), 0.14, 0.24, WOOD, bevel=0.03, up=up, ext=0.03)
        con_beam(k, P(ayc, zc - 0.03), P(tail, con_off_z(tail, CON_RAF_C) - 0.03), 0.13, 0.2, WOOD, bevel=0.025, up=up, ext=0.02)
    # side jack rafters every 0.6 from the hip line down to the eave
    for x in (-0.9, -0.3, 0.3, 0.9):
        head = x - xa + 0.1
        for s in (-1, 1): con_rafter(k, x, s, head=head)
    # end rafters: along +x, from the hip line to the end eave (the centre one from the apex)
    for y in (-2.4, -1.8, -1.2, -0.6, 0.0, 0.6, 1.2, 1.8, 2.4):
        head = abs(y) + (0.1 if y else 0.0)
        sub = Kit(); con_rafter(sub, -y, 1, head=head)
        merge_kit(k, sub, Matrix.Translation((xa, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"))
    # purlins + battens as U-shaped contours: side runs along x, end run along y at x = xa + a
    for i, (a, depth, w, h, bev, mi) in enumerate([(HALF / 3, CON_PUR_C, 0.14, 0.18, 0.025, WOOD), (2 * HALF / 3, CON_PUR_C, 0.14, 0.18, 0.025, WOOD)] + \
                                  [(a, CON_BAT_TOP + CON_BAT_T / 2, 0.09, CON_BAT_T, 0.0, PLANKS) for a in CON_BATTENS]):
        for s in (-1, 1): con_slope_x(k, -1.5, xa + a, s, a, depth, w, h, mi, bevel=bev, seed=i * 3 + s + 7)
        sub = Kit(); con_slope_x(sub, -a, a, 1, a, depth, w, h, mi, bevel=bev, seed=i * 5 + 2)
        merge_kit(k, sub, Matrix.Translation((xa, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"))
    # apex block + ceiling joists
    k.box((xa + 0.05, 0, RIDGE - 0.45), (0.3, 0.3, 0.34), WOOD, bevel=0.04)
    for x in (-0.9, -0.3, 0.3, 0.9): k.box((x, 0, 0.1), (0.12, 6.3, 0.2), WOOD, bevel=0.025)
    k.box((0.9, 0, 0.1), (0.12, 6.3, 0.2), WOOD, bevel=0.025)

# ------------------------------------------------------------------ scaffolding (birch poles, independent 2-row scaffold)
CON_SY = (-0.9, -1.58)      # standard rows (outside the wall line; inner row clears opened shutters, which reach y -0.82)
CON_LZ = (0.95, 2.0)        # ledger heights
CON_DZ = 2.15               # deck plank centre height (top 2.17)
CON_DY = (-1.09, -1.39)     # deck board centre lines
def con_lash(k, c, r=0.095, h=0.13):
    c = Vector(c); con_pole(k, c - Vector((0, 0, h / 2)), c + Vector((0, 0, h / 2)), r, mi=BURLAP, segs=8, caps=False)
def con_scaffold_wall(k, seed=0, top=3.0):
    """one 3 m lift; the lower lift's standards run to 3.0 (the next lift stands on them), a top lift (top=2.3)
    stops just above its deck so it passes under eaves, verges and hip rafters"""
    rnd = random.Random(seed); ym = (CON_SY[0] + CON_SY[1]) / 2
    for y in CON_SY:
        con_pole(k, (-1.5, y, 0.0), (-1.5, y, top), 0.07, BARK_OAK, segs=8, seed=int(-y * 10))
        for z in CON_LZ:
            con_pole(k, (-1.62, y, z), (1.62, y, z), 0.05, BARK_OAK, segs=6, caps=False, seed=int(z * 10))
            con_lash(k, (-1.5, y, z))
    for x in (-1.5, 0.0):   # transoms on the upper ledgers
        k.box((x, ym, CON_LZ[1] + 0.09), (0.08, 0.86, 0.08), WOOD, bevel=0.015)
    for i, y in enumerate(CON_DY):
        con_board(k, (rnd.uniform(-0.04, 0.04), y, CON_DZ), (3.02, 0.28, 0.04), rot=(0, 0, rnd.uniform(-0.01, 0.01)), seed=seed * 3 + i, bevel=0.008)
    # diagonal brace on the outer face
    yb = CON_SY[1] - 0.09
    con_pole(k, (-1.5, yb, 0.12), (1.5, yb, 2.05), 0.045, BARK_OAK, segs=6, caps=False, seed=3)
    con_lash(k, (-1.5, yb + 0.04, 0.18), 0.085, 0.1); con_lash(k, (1.44, yb + 0.04, 2.0), 0.085, 0.1)

def con_scaffold_corner(k, seed=0, top=3.0):
    rnd = random.Random(seed)
    o, i_ = CON_SY[1], CON_SY[0]
    for (x, y) in ((o, o), (i_, i_), (i_, 0.0), (o, 0.0)):
        con_pole(k, (x, y, 0.0), (x, y, top), 0.07, BARK_OAK, segs=8, seed=int(abs(x * 13 + y * 7)))
    for z in CON_LZ:
        con_pole(k, (o - 0.07, o, z), (0.12, o, z), 0.05, BARK_OAK, segs=6, caps=False)
        con_pole(k, (i_, i_, z), (0.12, i_, z), 0.05, BARK_OAK, segs=6, caps=False)
        con_pole(k, (o, o - 0.07, z + 0.1), (o, 0.12, z + 0.1), 0.05, BARK_OAK, segs=6, caps=False)
        con_pole(k, (i_, i_, z + 0.1), (i_, 0.12, z + 0.1), 0.05, BARK_OAK, segs=6, caps=False)
        for (x, y) in ((o, o), (i_, i_), (i_, 0.0), (o, 0.0)): con_lash(k, (x, y, z + 0.05), 0.095, 0.2)
    # transoms: one along x at y=0 (closes the -X run), one along y at x=-1.45
    ym = (o + i_) / 2
    k.box((ym, 0.0, CON_LZ[1] + 0.19), (0.86, 0.08, 0.08), WOOD, bevel=0.015)
    k.box((-1.45, ym, CON_LZ[1] + 0.09), (0.08, 0.86, 0.08), WOOD, bevel=0.015)
    # deck: boards along x in front of the -Y face, short boards along y on the -X side
    for j, y in enumerate(CON_DY):
        con_board(k, (-0.8, y, CON_DZ), (1.62, 0.28, 0.04), rot=(0, 0, rnd.uniform(-0.01, 0.01)), seed=seed + j, bevel=0.008)
    for j, x in enumerate(CON_DY):
        con_board(k, (x, -0.4, CON_DZ + 0.05), (0.95, 0.28, 0.04), rot=(0, 0, math.pi / 2), seed=seed + 7 + j, bevel=0.008)
    con_pole(k, (o - 0.09, -1.5, 0.12), (o - 0.09, 0.0, 1.2), 0.045, BARK_OAK, segs=6, caps=False, seed=4)

def con_ladder(k, p0, p1, w=0.45, rung=0.3, rail=(0.06, 0.04), mi=WOOD):
    p0 = Vector(p0); p1 = Vector(p1); R, L = con_frame(p0, p1)
    X = R.col[0].xyz; side = Vector((1, 0, 0)) if abs(X.x) < 0.9 else Vector((0, 1, 0))
    side = (side - X * X.dot(side)).normalized(); nrm = X.cross(side)
    for s in (-1, 1):
        off = side * s * w / 2
        con_beam(k, p0 + off, p1 + off, rail[1], rail[0], mi, bevel=0.012, up=nrm)
    n = int((L - 0.25) / rung)
    for i in range(n):
        c = p0 + X * (0.3 + i * rung)
        con_pole(k, c - side * (w / 2 + 0.01), c + side * (w / 2 + 0.01), 0.022, WOOD, segs=5, caps=False)

def con_scaffold_ladder(k):
    con_ladder(k, (0.75, -2.15, 0.0), (0.75, -1.44, 3.0))     # rests on the outer upper ledger (y -1.58, z 2.0)

# ------------------------------------------------------------------ tools
def con_wheel(k, c, r, w=0.08, spokes=6, axis="Y", tyre_n=12, single=False, hub=8):
    if single:      # one felloe ring whose rolling surface is the iron tyre (half the tris)
        fs = ring(k, c, r - 0.11, r, w, WOOD, n=tyre_n, axis=axis)
        for f in fs[2::4]: k.project([f], IRON)
    else:
        ring(k, c, r - 0.045, r, w, IRON, n=tyre_n, axis=axis)
        ring(k, c, r - 0.12, r - 0.045, w * 0.85, WOOD, n=tyre_n, axis=axis)
    rot = Matrix.Rotation(math.pi / 2, 4, "X")
    _cyl(k, c, 0.075, 0.075, w * 2.0, hub, WOOD, rot=rot)
    for i in range(spokes):
        a = math.pi * i / spokes
        k.box(c, (2 * (r - 0.1), w * 0.45, 0.045), WOOD, rot=(0, a, 0), bevel=0)

def con_wheelbarrow(k, seed=5):
    rnd = random.Random(seed)
    con_tray(k, (0.02, 0, 0.36), (0.72, 0.5), (1.02, 0.7), 0.32, 0.04, PLANKS, WOOD)
    k.box((0.02, 0, 0.35), (0.74, 0.52, 0.03), WOOD, bevel=0.01)
    for s in (-1, 1):
        con_beam(k, (0.7, s * 0.14, 0.2), (-1.0, s * 0.3, 0.52), 0.07, 0.08, WOOD, bevel=0.02)
        con_pole(k, (-1.0, s * 0.3, 0.52), (-1.28, s * 0.31, 0.6), 0.035, WOOD, segs=6, cap_mi=WOOD)
        con_beam(k, (-0.42, s * 0.24, 0.42), (-0.5, s * 0.28, 0.0), 0.06, 0.06, WOOD, bevel=0.015)
        k.box((0.35, s * 0.3, 0.44), (0.05, 0.03, 0.3), IRON, rot=(s * 0.35, 0, 0), bevel=0)
    con_wheel(k, (0.7, 0, 0.21), 0.21, 0.07, 6)
    for i in range(4):
        rock(k, (rnd.uniform(-0.25, 0.3), rnd.uniform(-0.14, 0.14), 0.6 + 0.04 * i), (0.28, 0.22, 0.18), seed=seed * 10 + i, tilt=0.3, segs=1)

def con_mortar_tub(k, seed=6):
    rnd = random.Random(seed)
    con_tray(k, (0, 0, 0.02), (0.8, 0.5), (0.92, 0.62), 0.3, 0.04, PLANKS, WOOD)
    for x in (-0.3, 0.3): k.box((x, 0, 0.02), (0.08, 0.66, 0.05), WOOD, bevel=0.01)
    # lumpy mortar surface
    nx, ny = 5, 4; V = {}
    for i in range(nx + 1):
        for j in range(ny + 1):
            x = -0.41 + 0.82 * i / nx; y = -0.27 + 0.54 * j / ny
            e = i in (0, nx) or j in (0, ny)
            V[i, j] = k.bm.verts.new((x, y, 0.25 + (0.0 if e else rnd.uniform(0.0, 0.05))))
    fs = [k.bm.faces.new((V[i, j], V[i + 1, j], V[i + 1, j + 1], V[i, j + 1])) for i in range(nx) for j in range(ny)]
    k.bm.normal_update(); k.project(fs, PLASTER)
    # hoe resting in the mortar, a trowel, a bucket and a lime sack
    con_pole(k, (0.05, 0.05, 0.28), (-0.95, 0.45, 0.95), 0.025, WOOD, segs=6, cap_mi=WOOD)
    k.box((0.1, 0.03, 0.27), (0.05, 0.22, 0.12), IRON, rot=(0, 0.5, 0.38), bevel=0.01)
    k.box((0.3, -0.2, 0.33), (0.18, 0.1, 0.012), STEEL, rot=(0.2, 0.1, 0.4), bevel=0)
    k.box((0.42, -0.27, 0.36), (0.12, 0.035, 0.035), WOOD, rot=(0.2, 0.1, 0.4), bevel=0.008)
    _cyl(k, (0.72, 0.28, 0.17), 0.14, 0.17, 0.34, 10, WOOD)
    for zz in (0.07, 0.28): _cyl(k, (0.72, 0.28, zz), 0.155 + zz * 0.05, 0.155 + zz * 0.05, 0.03, 10, IRON)
    _cyl(k, (0.72, 0.28, 0.33), 0.155, 0.155, 0.02, 10, PLASTER)
    _ico(k, (-0.62, -0.25, 0.26), 0.28, BURLAP, (0.95, 0.8, 0.95), jit=0.02, seed=seed)
    _cyl(k, (-0.62, -0.25, 0.54), 0.06, 0.1, 0.1, 6, BURLAP)

def con_ladder_lean(k):
    """3 m ladder leaning on a wall face (wall-local: outer face y=-0.25); top stays below the jetty joists (z 2.8)"""
    con_ladder(k, (0.0, -1.02, 0.0), (0.0, -0.3, 2.78), w=0.46)

def con_shear_legs(k, seed=7):
    rnd = random.Random(seed)
    apex = Vector((0, 0, 4.85))
    feet = [Vector((math.cos(a) * 1.55, math.sin(a) * 1.55, -0.05)) for a in (math.radians(90), math.radians(210), math.radians(330))]
    for i, f in enumerate(feet):
        d = (apex - f).normalized()
        con_pole(k, f, apex + d * 0.3, 0.085, BARK_BIRCH, segs=8, r1=0.07, seed=i)
        rock(k, (f.x, f.y, 0.05), (0.3, 0.3, 0.14), seed=seed + i, mi=ROCK, segs=1)
    con_lash(k, apex - Vector((0, 0, 0.05)), 0.17, 0.3)
    # block + hook + chains, hanging ashlar block
    k.box((0, 0, 4.35), (0.14, 0.2, 0.32), WOOD, bevel=0.03)
    _cyl(k, (0, 0, 4.35), 0.11, 0.11, 0.06, 10, IRON, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    con_rope(k, (0, 0.04, 4.2), (0, 0.04, 1.75), 0.018)
    k.box((0, 0.04, 1.7), (0.06, 0.06, 0.12), IRON, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            con_pole(k, (0, 0.04, 1.66), (sx * 0.28, 0.04 + sy * 0.2, 1.36), 0.012, IRON, segs=4, caps=False)
    con_ashlar_block(k, (0, 0.04, 1.1), (0.8, 0.6, 0.5), rot=(0, 0, 0.15), seed=seed)
    # haul rope from the block down to a cleat on one leg and a coil on the ground
    f = feet[0]; p = f + (apex - f) * 0.3
    con_rope(k, (0, -0.04, 4.2), (p.x, p.y, p.z), 0.018)
    con_rope(k, (p.x, p.y, p.z), (p.x + 0.25, p.y - 0.15, 0.05), 0.018)
    ring(k, (p.x + 0.35, p.y - 0.25, 0.04), 0.1, 0.22, 0.07, HAY, n=10, axis="Z")
    con_ashlar_block(k, (-0.9, -0.7, 0.2), (0.7, 0.45, 0.4), rot=(0, 0, 0.5), seed=seed + 3)

# ------------------------------------------------------------------ stock piles (each within 2.9 x 2.9 x 1.6)
def con_pile_logs(k, level=1, seed=10):
    rnd = random.Random(seed * 3 + level)
    rows = {1: [3], 2: [4, 3], 3: [4, 3, 2, 1]}[level]
    pitch = 0.39; W = rows[0] * pitch
    for x in (-0.9, 0.9):   # bearers
        con_pole(k, (x, -W / 2 - 0.1, 0.06), (x, W / 2 + 0.1, 0.06), 0.07, BARK_OAK, segs=6, seed=int(x * 10))
    for ri, cnt in enumerate(rows):
        for i in range(cnt):
            y = (i - (cnt - 1) / 2) * pitch; r_ = rnd.uniform(0.15, 0.2); z = 0.12 + 0.18 + ri * 0.31
            x0 = -1.4 + rnd.uniform(-0.06, 0.06)
            con_log(k, (x0, y, z), (x0 + 2.8, y + rnd.uniform(-0.04, 0.04), z + rnd.uniform(-0.02, 0.02)), r_, seed=seed * 100 + ri * 10 + i)
    h = 0.45 + 0.3 * (len(rows) - 1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            if level == 1 and sx != sy: continue
            con_pole(k, (sx * 1.05, sy * (W / 2 + 0.07), -0.1), (sx * 1.05 + sx * 0.02, sy * (W / 2 + 0.1), h), 0.05, BARK_OAK, segs=6, seed=sx + 2 * sy)

def con_pile_planks(k, level=1, seed=20):
    rnd = random.Random(seed * 3 + level)
    layers = {1: 4, 2: 9, 3: 14}[level]
    for s in (-1, 1):
        yc = s * 0.5
        for x in (-1.15, 0.0, 1.15): k.box((x, yc, 0.05), (0.14, 0.95, 0.1), WOOD, bevel=0.02)
        z = 0.1
        for L_ in range(layers):
            if L_ and L_ % 3 == 0:
                for x in (-1.15, 0.0, 1.15): k.box((x + rnd.uniform(-0.03, 0.03), yc, z + 0.02), (0.06, 0.92, 0.04), WOOD, bevel=0)
                z += 0.04
            top = (L_ == layers - 1)
            for b in range(3):
                if top and level < 3 and b == 2 and s > 0: continue
                y = yc + (b - 1) * 0.3
                con_board(k, (rnd.uniform(-0.05, 0.05), y + rnd.uniform(-0.01, 0.01), z + 0.025), (2.8, 0.25, 0.05),
                          rot=(0, 0, rnd.uniform(-0.012, 0.012) + (rnd.uniform(-0.06, 0.06) if top else 0)), col=rnd.randrange(8), seed=seed + L_ * 7 + b)
            z += 0.05

def con_pallet(k, c, size=(1.3, 1.0, 0.12), seed=0):
    rnd = random.Random(seed); cx, cy, cz = c; W, D, H = size
    for x in (-W / 2 + 0.07, 0, W / 2 - 0.07): k.box((cx + x, cy, cz + (H - 0.035) / 2), (0.1, D, H - 0.035), WOOD, bevel=0.015)
    n = 4
    for i in range(n):
        y = -D / 2 + (i + 0.5) * D / n
        con_board(k, (cx, cy + y, cz + H - 0.0175), (W, D / n - 0.03, 0.035), rot=(0, 0, 0), col=rnd.randrange(8), seed=seed + i)

def con_pile_stone(k, level=1, seed=30):
    rnd = random.Random(seed * 3 + level)
    count = {1: 6, 2: 14, 3: 24}[level]
    slots = []
    for lay in range(3):
        for px in (-0.7, 0.7):
            for (ox, oy) in ((-0.31, -0.21), (0.31, -0.21), (-0.31, 0.21), (0.31, 0.21)):
                slots.append((px + ox, oy, 0.12 + 0.175 + lay * 0.355))
    for px in (-0.7, 0.7): con_pallet(k, (px, 0, 0), seed=seed + int(px * 10))
    for i in range(count):
        x, y, z = slots[i]
        con_ashlar_block(k, (x + rnd.uniform(-0.02, 0.02), y + rnd.uniform(-0.02, 0.02), z), (0.58, 0.39, 0.35),
                         rot=(0, 0, math.radians(rnd.uniform(-3, 3))), seed=seed * 50 + i)

def con_sack(k, c, rz=0.0, L=0.74, W=0.5, H=0.3, seed=0):
    """grain sack lying down: boxy pillow (superellipsoid) with a short tied tuft at +x"""
    rnd = random.Random(seed)
    sub = Kit()
    _ico(sub, (0, 0, 0), 1.0, BURLAP, (1, 1, 1), sub=2, jit=0.0)
    for v in sub.bm.verts:
        p = v.co.normalized()
        q = Vector([math.copysign(abs(a) ** 0.55, a) for a in p])
        t = q.x
        q.z *= 1.0 - 0.3 * t * t                     # thinner towards the ends
        q.y *= 1.0 - 0.22 * max(0.0, t) ** 3         # gathered towards the tied end
        v.co = Vector((q.x * L / 2, q.y * W / 2, q.z * H / 2 + 0.03 * (1 - t * t) * (1 if q.z > 0 else 0)))
        v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.01
    _cyl(sub, (L / 2 + 0.03, 0, 0.02), 0.06, 0.09, 0.08, 5, BURLAP, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    _cyl(sub, (L / 2 - 0.0, 0, 0.02), 0.075, 0.075, 0.03, 5, HAY, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    for f in sub.bm.faces:
        if f.material_index == BURLAP:
            for l in f.loops: l[sub.uv].uv = (l.vert.co.x / 0.8, (l.vert.co.y + l.vert.co.z) / 0.8)
    merge_kit(k, sub, Matrix.Translation(c) @ Matrix.Rotation(rz, 4, "Z"))

def con_pile_sacks(k, level=1, seed=40):
    rnd = random.Random(seed * 3 + level)
    count = {1: 4, 2: 9, 3: 16}[level]
    con_pallet(k, (0, 0, 0), (1.7, 1.6, 0.12), seed=seed)
    A = [((sx * 0.4, sy * 0.52), 0.0) for sy in (-1, 0, 1) for sx in (-1, 1)]
    B = [((sx * 0.52, sy * 0.4), math.pi / 2) for sx in (-1, 0, 1) for sy in (-1, 1)]
    slots = [(p, r, 0) for (p, r) in A] + [(p, r, 1) for (p, r) in B] + [(p, r, 2) for (p, r) in A[1:5]]
    for i in range(count):
        (x, y), rz, lay = slots[i]
        flip = math.pi if rnd.random() < 0.5 else 0.0
        con_sack(k, (x + rnd.uniform(-0.03, 0.03), y + rnd.uniform(-0.03, 0.03), 0.12 + 0.15 + lay * 0.25), rz + flip + rnd.uniform(-0.1, 0.1), seed=seed * 20 + i)

def con_stockpile_border(k, seed=45):
    rnd = random.Random(seed)
    for s in (-1, 1):
        con_board(k, (rnd.uniform(-0.02, 0.02), s * 1.40, 0.07), (2.9, 0.12, 0.1), rot=(math.pi / 2, 0, rnd.uniform(-0.008, 0.008)), col=rnd.randrange(8), seed=seed + s)
        con_board(k, (s * 1.40, rnd.uniform(-0.02, 0.02), 0.07), (2.7, 0.12, 0.1), rot=(math.pi / 2, 0, math.pi / 2 + rnd.uniform(-0.008, 0.008)), col=rnd.randrange(8), seed=seed + 5 * s)
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.box((sx * 1.40, sy * 1.40, 0.13), (0.11, 0.11, 0.36), WOOD, rot=(0, 0, rnd.uniform(-0.2, 0.2)), bevel=0.025)
            k.box((sx * 1.40, sy * 1.40, 0.33), (0.07, 0.07, 0.07), WOOD, rot=(0, 0, 0.785), bevel=0.02)

# ------------------------------------------------------------------ settler camp
def con_cloth_sheet(k, P, nu, nv, mi=CLOTH_B, double=True, tile=1.0, thick=0.015):
    """grid sheet from a point function P(u,v) (u,v in 0..1), both sides"""
    G = [[P(i / nu, j / nv) for j in range(nv + 1)] for i in range(nu + 1)]
    def build(offset, flip):
        V = [[k.bm.verts.new(G[i][j] + offset(i, j)) for j in range(nv + 1)] for i in range(nu + 1)]
        idx = {V[i][j]: (i, j) for i in range(nu + 1) for j in range(nv + 1)}
        fs = []
        for i in range(nu):
            for j in range(nv):
                q = (V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1])
                f = k.bm.faces.new(q[::-1] if flip else q); f.material_index = mi; fs.append(f)
                for l in f.loops:
                    ii, jj = idx[l.vert]; l[k.uv].uv = (ii / nu * tile, jj / nv * tile)
        return fs, idx
    fs, idx = build(lambda i, j: Vector((0, 0, 0)), False)
    k.bm.normal_update()
    if double:
        nrm = [[Vector((0, 0, 0)) for j in range(nv + 1)] for i in range(nu + 1)]
        for f in fs:
            for v in f.verts:
                i, j = idx[v]; nrm[i][j] += f.normal
        build(lambda i, j: -nrm[i][j].normalized() * thick if nrm[i][j].length > 0 else Vector((0, 0, 0)), True)
    k.bm.normal_update()
    return fs

def con_tent_a(k, seed=50):
    rnd = random.Random(seed); W = 1.2; H = 2.1; Ly = 1.55
    for s in (-1, 1):
        n = Vector((s * H, 0, W)).normalized()
        def P(u, v, s=s, n=n):
            y = -Ly + 2 * Ly * u; t = v
            p = Vector((s * (W * t + 0.03), y, H * (1 - t) + 0.02))
            sag = 0.1 * math.sin(math.pi * t) * (0.5 + 0.5 * math.sin(math.pi * u)) + 0.05 * math.sin(math.pi * u) * (1 - t)
            return p - n * sag + Vector((s * 0.06 * t * t, 0, 0))
        con_cloth_sheet(k, P, 6, 4, CLOTH_B, tile=1.5)
        # coloured hem band (cloth style recolours it)
        con_cloth_sheet(k, lambda u, v, P=P, n=n: P(u, 0.8 + 0.12 * v) + n * 0.012, 6, 1, CLOTH_A, double=False, tile=1.0)
    # back wall (closed) and front: VOID doorway + two flaps swung open
    for (y, closed) in ((Ly, True), (-Ly, False)):
        tri = [Vector((-W - 0.02, y, 0.02)), Vector((W + 0.02, y, 0.02)), Vector((0, y, H + 0.01))]
        if closed:
            f = k.bm.faces.new([k.bm.verts.new(p) for p in tri]); f.material_index = CLOTH_B
            f2 = k.bm.faces.new([k.bm.verts.new(p - Vector((0, 0.015, 0))) for p in tri[::-1]]); f2.material_index = CLOTH_B
            k.bm.normal_update()
            if f.normal.y < 0: f.normal_flip(); f2.normal_flip()
        else:
            f = k.bm.faces.new([k.bm.verts.new(p + Vector((0, 0.06, 0))) for p in tri]); f.material_index = VOID
            k.bm.normal_update()
            if f.normal.y > 0: f.normal_flip()
            for s in (-1, 1):
                R_ = Vector((0, y, H)); C_ = Vector((s * W, y, 0.0)); F_ = Vector((0, y, 0.0))
                ax = (C_ - R_).normalized()
                best = None
                for sign in (-1, 1):
                    M = Matrix.Rotation(sign * math.radians(118), 3, ax)
                    Fr = R_ + M @ (F_ - R_)
                    if best is None or Fr.y < best.y: best = Fr
                mid = (R_ + C_) / 2 + (best - (R_ + C_) / 2) * 0.5 + Vector((0, -0.05, 0))
                for (pts, fl) in (([R_, C_, best], False), ([R_, C_, best], True)):
                    off = Vector((0, 0.012 if fl else 0, 0))
                    ff = k.bm.faces.new([k.bm.verts.new(p + off) for p in (pts[::-1] if fl else pts)]); ff.material_index = CLOTH_B
                con_rope(k, best + Vector((0, 0.05, 0.3)), C_ + Vector((s * 0.08, 0, 0.9)), 0.012)
    # ridge pole, uprights, guy ropes, pegs, sod stones, ground sheet
    con_pole(k, (0, -Ly - 0.18, H + 0.04), (0, Ly + 0.18, H + 0.04), 0.05, WOOD, segs=6, cap_mi=ENDGRAIN)
    for y in (-Ly - 0.05, Ly + 0.05):
        con_pole(k, (0, y, 0.0), (0, y, H + 0.12), 0.045, WOOD, segs=6, cap_mi=WOOD)
    for sy in (-1, 1):
        for sx in (-1, 1):
            pk = Vector((sx * 0.55, sy * 2.65, 0.0))
            con_rope(k, (0, sy * (Ly + 0.15), H + 0.05), (pk.x, pk.y, 0.18), 0.012)
            k.box((pk.x, pk.y, 0.08), (0.05, 0.05, 0.26), WOOD, rot=(sy * 0.3, 0, 0), bevel=0.01)
    for s in (-1, 1):
        for i in range(4):
            rock(k, (s * (W + 0.12), -1.2 + 0.8 * i + rnd.uniform(-0.1, 0.1), 0.05), (0.22, 0.18, 0.14), seed=seed + i * 2 + s, mi=ROCK, segs=1)
    k.box((0, 0, 0.012), (2.3, 3.0, 0.02), HIDE, bevel=0)

def con_tent_bell(k, seed=55):
    rnd = random.Random(seed); segs = 16; R0 = 1.8
    prof = [(R0, 0.0), (R0, 0.5)]
    for i in range(1, 7):
        t = i / 6.0
        prof.append((R0 + (0.08 - R0) * t, 0.5 + 2.3 * t - 0.16 * math.sin(math.pi * t)))
    fs = lathe(k, prof, center=(0, 0, 0), segs=segs, mi=CLOTH_B, smooth_=True)
    for idx, f in enumerate(fs):
        band = idx // segs; i = idx % segs
        if band >= 1 and i % 2 == 0: f.material_index = CLOTH_A     # striped canopy (cloth style recolours it)
        cc = f.calc_center_median(); ac = math.atan2(cc.y, cc.x)
        for l in f.loops:
            p = l.vert.co; a = math.atan2(p.y, p.x)
            if a - ac > math.pi: a -= 2 * math.pi
            if a - ac < -math.pi: a += 2 * math.pi
            l[k.uv].uv = (a * R0 / 1.2, p.z / 1.2)
    # doorway (VOID patch hugging the surface at -Y) + rolled-up door canvas
    def surf(a, z):
        if z <= 0.5: r = R0
        else:
            t = (z - 0.5) / 2.3; r = R0 + (0.08 - R0) * t
        return Vector((math.cos(a) * (r + 0.012), math.sin(a) * (r + 0.012), z))
    a0 = -math.pi / 2; da = 0.24
    rows = [0.02, 0.5, 1.0, 1.45]
    V = [[k.bm.verts.new(surf(a0 + da * (u - 0.5) * 2 * (1 - 0.35 * (j / 3.0)), z)) for u in (0, 0.5, 1)] for j, z in enumerate(rows)]
    for j in range(3):
        for u in range(2):
            f = k.bm.faces.new((V[j][u], V[j][u + 1], V[j + 1][u + 1], V[j + 1][u])); f.material_index = VOID
    k.bm.normal_update()
    top = surf(a0, 1.5)
    con_pole(k, top + Vector((-0.5, -0.1, 0)), top + Vector((0.5, -0.1, 0)), 0.09, CLOTH_B, segs=8, cap_mi=CLOTH_B)
    for sx in (-0.3, 0.3): _cyl(k, (sx, top.y - 0.1, top.z), 0.1, 0.1, 0.03, 8, HAY, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    # scalloped valance at the eave
    for i in range(segs):
        a = 2 * math.pi * (i + 0.5) / segs; a1 = 2 * math.pi * i / segs; a2 = 2 * math.pi * (i + 1) / segs
        r = R0 + 0.03
        pts = [Vector((math.cos(a1) * r, math.sin(a1) * r, 0.56)), Vector((math.cos(a2) * r, math.sin(a2) * r, 0.56)), Vector((math.cos(a) * r, math.sin(a) * r, 0.36))]
        f = k.bm.faces.new([k.bm.verts.new(p) for p in pts]); f.material_index = CLOTH_A
        f2 = k.bm.faces.new([k.bm.verts.new(p * 0.995) for p in pts[::-1]]); f2.material_index = CLOTH_A
    k.bm.normal_update()
    # centre pole, finial and pennant
    con_pole(k, (0, 0, 0), (0, 0, 3.25), 0.06, WOOD, segs=6, cap_mi=WOOD)
    _ico(k, (0, 0, 3.3), 0.08, BRONZE, sub=1)
    pts = [Vector((0.03, 0, 3.15)), Vector((0.03, 0, 2.95)), Vector((0.62, 0.05, 3.02))]
    f = k.bm.faces.new([k.bm.verts.new(p) for p in pts]); f.material_index = CLOTH_A
    f = k.bm.faces.new([k.bm.verts.new(p + Vector((0, 0.01, 0))) for p in pts[::-1]]); f.material_index = CLOTH_A
    # guy ropes + pegs
    for i in range(8):
        a = 2 * math.pi * (i + 0.5) / 8
        if abs(a - (3 * math.pi / 2)) < 0.4: continue
        p0 = (math.cos(a) * (R0 + 0.02), math.sin(a) * (R0 + 0.02), 0.52); p1 = (math.cos(a) * 2.65, math.sin(a) * 2.65, 0.15)
        con_rope(k, p0, p1, 0.012)
        k.box((p1[0], p1[1], 0.06), (0.05, 0.05, 0.24), WOOD, rot=(0, 0, a), bevel=0.01)
    k.box((0, -1.45, 0.012), (1.0, 0.7, 0.02), HIDE, rot=(0, 0, 0.1), bevel=0)      # hide mat at the door

def con_flame(k, c, h, r, seed=0, twist=0.9):
    rnd = random.Random(seed); ph = rnd.uniform(0, 6.28)
    prof = [(r, 0.0), (r * 1.08, h * 0.18), (r * 0.8, h * 0.45), (r * 0.42, h * 0.72), (r * 0.12, h * 0.92), (0.0, h)]
    segs = 7; rings = []
    for (rr, z) in prof:
        t = z / h; off = Vector((math.sin(ph + t * 3.0) * 0.06 * t, math.cos(ph + t * 2.3) * 0.05 * t, 0))
        rings.append([k.bm.verts.new(Vector(c) + off + Vector((math.cos(2 * math.pi * i / segs + twist * t) * rr, math.sin(2 * math.pi * i / segs + twist * t) * rr, z))) for i in range(segs)])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs; f = k.bm.faces.new((a[i], a[j], b[j], b[i])); f.material_index = GLOW
    k.bm.normal_update()

def con_campfire(k, seed=60):
    rnd = random.Random(seed)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.1, 0.1)
        rock(k, (math.cos(a) * 0.58, math.sin(a) * 0.58, 0.1), (0.3, 0.24, 0.24), seed=seed + i, rot_z=a, mi=ROCK, segs=1)
    lathe(k, [(0.5, 0.0), (0.42, 0.04), (0.2, 0.07), (0.0, 0.075)], center=(0, 0, 0.0), segs=12, mi=COAL)
    for i in range(7):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.1, 0.38)
        _ico(k, (math.cos(a) * d, math.sin(a) * d, 0.07), rnd.uniform(0.04, 0.07), GLOW, (1, 1, 0.5), sub=1)
    for i in range(5):
        a = 2 * math.pi * i / 5 + 0.3
        p0 = Vector((math.cos(a) * 0.46, math.sin(a) * 0.46, 0.04)); p1 = Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, 0.72))
        con_pole(k, p0, p1, 0.06, BARK_OAK, segs=6, r1=0.045, cap_mi=COAL, seed=i)
    _ico(k, (0, 0, 0.18), 0.17, GLOW, (1, 1, 0.7), sub=2)
    con_flame(k, (0, 0, 0.1), 0.72, 0.13, seed=1)
    con_flame(k, (0.13, 0.07, 0.08), 0.46, 0.08, seed=2, twist=-1.1)
    con_flame(k, (-0.11, -0.09, 0.08), 0.4, 0.075, seed=3)
    con_flame(k, (-0.05, 0.13, 0.08), 0.34, 0.06, seed=4, twist=1.4)
    # tripod and pot
    apex = Vector((0, 0, 1.55))
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.5
        f = Vector((math.cos(a) * 0.85, math.sin(a) * 0.85, 0.0))
        con_pole(k, f, apex + (apex - f).normalized() * 0.15, 0.032, BARK_OAK, segs=5, seed=i)
    con_lash(k, apex, 0.05, 0.1)
    k.box((0, 0, 1.28), (0.02, 0.02, 0.5), IRON, bevel=0)
    lathe(k, [(0.0, 0.0), (0.14, 0.01), (0.2, 0.08), (0.21, 0.2), (0.19, 0.28), (0.21, 0.3)], center=(0, 0, 0.73), segs=12, mi=IRON)
    _cyl(k, (0, 0, 1.0), 0.18, 0.18, 0.02, 12, BREAD)
    k.box((0, 0, 1.12), (0.44, 0.015, 0.015), IRON, bevel=0)
    for sx in (-1, 1): k.box((sx * 0.21, 0, 1.07), (0.015, 0.015, 0.12), IRON, bevel=0)

def con_bedroll(k, seed=70):
    k.box((0, 0, 0.03), (0.74, 1.66, 0.06), HIDE, bevel=0.025, segs=2)
    k.box((0, -0.18, 0.085), (0.66, 1.16, 0.08), CLOTH_A, bevel=0.035, segs=2)
    con_pole(k, (-0.34, 0.38, 0.11), (0.34, 0.38, 0.11), 0.055, CLOTH_A, segs=8, cap_mi=CLOTH_A)
    con_pole(k, (-0.36, 0.66, 0.13), (0.36, 0.66, 0.13), 0.12, CLOTH_B, segs=10, cap_mi=CLOTH_B)
    for x in (-0.22, 0.22): _cyl(k, (x, 0.66, 0.13), 0.126, 0.126, 0.03, 10, HAY, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))

def con_wagon_covered(k, seed=80):
    rnd = random.Random(seed)
    # undercarriage
    for y in (-0.42, 0.42): k.box((0, y, 0.56), (3.0, 0.12, 0.14), WOOD, bevel=0.025)
    for x in (-1.05, 1.05): k.box((x, 0, 0.46), (0.14, 1.78, 0.12), WOOD, bevel=0.025)
    for (x, r) in ((-1.05, 0.5), (1.05, 0.43)):
        for y in (-0.88, 0.88): con_wheel(k, (x, y, r), r, 0.09, 6, tyre_n=10, single=True, hub=6)
    # bed: floor + board sides
    k.box((0, 0, 0.67), (3.2, 1.34, 0.08), PLANKS, bevel=0.02)
    for s in (-1, 1):
        for zz in (0.8, 0.96):
            con_board(k, (0, s * 0.69, zz), (3.2, 0.16, 0.05), rot=(math.pi / 2, 0, 0), col=rnd.randrange(8), seed=seed + int(zz * 10) + s)
        for x in (-1.5, -0.5, 0.5, 1.5): k.box((x, s * 0.72, 0.84), (0.08, 0.05, 0.36), WOOD, bevel=0.0)
    k.box((-1.62, 0, 0.86), (0.06, 1.38, 0.34), WOOD, bevel=0.02)
    # hoops (only the end hoops are visible through the openings; the inner ones show as ribs in the canvas)
    Rc = 0.8; zc = 1.0; xs = (-1.45, -0.72, 0.0, 0.72, 1.45)
    for x in (xs[0], xs[-1]):
        for i in range(8):
            a0 = math.pi * i / 8; a1 = math.pi * (i + 1) / 8
            con_pole(k, (x, -math.cos(a0) * (Rc - 0.05), zc + math.sin(a0) * (Rc - 0.05)), (x, -math.cos(a1) * (Rc - 0.05), zc + math.sin(a1) * (Rc - 0.05)), 0.025, WOOD, segs=4, caps=False)
        for s in (-1, 1): con_pole(k, (x, s * (Rc - 0.05), zc), (x, s * 0.7, 0.78), 0.025, WOOD, segs=4, caps=False)
    X0, X1 = -1.72, 1.62
    def P(u, v):
        x = X0 + (X1 - X0) * u; a = math.pi * v
        hoop = min(abs(x - h) for h in xs)
        rr = Rc + 0.02 - 0.05 * min(1.0, hoop / 0.36) * math.sin(a) ** 0.5
        end = min(u, 1 - u)
        if end < 0.06: rr -= (0.06 - end) * 1.6
        return Vector((x, -math.cos(a) * rr, zc + math.sin(a) * rr - (0.03 if v in (0.0, 1.0) else 0.0)))
    con_cloth_sheet(k, P, 14, 9, CLOTH_B, double=False, tile=2.0)
    # openings: front dark mouth, back gathered with a small hole
    for (x, mi, rr) in ((X1 - 0.06, VOID, Rc - 0.08), (X0 + 0.05, CLOTH_B, Rc - 0.06)):
        pts = [Vector((x, -math.cos(math.pi * i / 10) * rr, zc + math.sin(math.pi * i / 10) * rr)) for i in range(11)]
        vs = [k.bm.verts.new(p) for p in pts]; f = k.bm.faces.new(vs); f.material_index = mi
        k.bm.normal_update()
        want = 1 if x > 0 else -1
        if f.normal.x * want < 0: f.normal_flip()
    _cyl(k, (X0 + 0.02, 0, zc + 0.38), 0.1, 0.1, 0.03, 8, VOID, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    # tongue + singletree, tailgate barrel, water bucket
    con_beam(k, (1.05, 0, 0.44), (2.95, 0, 0.3), 0.1, 0.1, WOOD, bevel=0.02)
    k.box((2.9, 0, 0.3), (0.08, 0.9, 0.08), WOOD, bevel=0.015)
    barrel(k, -1.95, 0.35, 0.02, 0.26, 0.62)
    _cyl(k, (-2.0, -0.3, 0.11), 0.12, 0.14, 0.22, 8, WOOD)
    k.box((-2.0, -0.3, 0.23), (0.3, 0.02, 0.02), IRON, bevel=0)
    # driver's bench at the front opening
    k.box((1.35, 0, 1.12), (0.34, 1.3, 0.06), WOOD, bevel=0.015)
    for s in (-1, 1): k.box((1.35, s * 0.55, 0.9), (0.06, 0.06, 0.4), WOOD, bevel=0.01)

# ------------------------------------------------------------------ early work yard
def con_chopping_block(k, seed=90):
    rnd = random.Random(seed)
    con_pole(k, (0, 0, -0.05), (0, 0, 0.5), 0.36, BARK_OAK, segs=12, r1=0.3, nring=3, noise_=0.05, seed=seed)
    # axe bitten into the top
    k.box((0.02, 0.0, 0.52), (0.22, 0.045, 0.14), STEEL, rot=(0, 0.25, 0.2), bevel=0.01)
    con_pole(k, (-0.06, -0.02, 0.58), (-0.55, -0.12, 0.92), 0.028, WOOD, segs=6, cap_mi=WOOD)
    # split billets + chips
    for i in range(4):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.55, 0.9)
        c = Vector((math.cos(a) * d, math.sin(a) * d, 0.09))
        rz = rnd.uniform(0, 3.14)
        sub = Kit(); r = rnd.uniform(0.1, 0.14)
        pts = [Vector((0, 0, 0))] + [Vector((0, math.cos(t) * r, math.sin(t) * r)) for t in (0.2, 0.9, 1.6)]
        L = rnd.uniform(0.42, 0.55)
        A = [sub.bm.verts.new(p + Vector((-L / 2, 0, 0))) for p in pts]; B_ = [sub.bm.verts.new(p + Vector((L / 2, 0, 0))) for p in pts]
        for j in range(4):
            j2 = (j + 1) % 4; f = sub.bm.faces.new((A[j], A[j2], B_[j2], B_[j])); f.material_index = BARK_OAK if j in (1, 2) else WOOD
        fa = sub.bm.faces.new(A[::-1]); fa.material_index = ENDGRAIN; fb = sub.bm.faces.new(B_); fb.material_index = ENDGRAIN
        sub.bm.normal_update()
        if fb.normal.x < 0:
            for f in list(sub.bm.faces): f.normal_flip()
        for f in sub.bm.faces:
            if f.material_index == ENDGRAIN:
                for l in f.loops: l[sub.uv].uv = (0.5 + l.vert.co.y / r * 0.44, 0.5 + l.vert.co.z / r * 0.44)
            else: sub.project([f], f.material_index)
        merge_kit(k, sub, Matrix.Translation(c) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(-0.8, 4, "X"))
    for i in range(10):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.38, 0.8)
        k.box((math.cos(a) * d, math.sin(a) * d, 0.01), (0.09, 0.05, 0.015), PAPER, rot=(0, 0, rnd.uniform(0, 3)), bevel=0)

def con_sawhorse(k, seed=95):
    rnd = random.Random(seed)
    k.box((0, 0, 0.66), (1.2, 0.1, 0.12), WOOD, bevel=0.02)
    for x in (-0.45, 0.45):
        for s in (-1, 1):
            con_beam(k, (x, s * 0.36, 0.0), (x + 0.02 * s, -s * 0.12, 0.92), 0.08, 0.08, WOOD, bevel=0.015)
    con_log(k, (-0.8, 0.0, 0.87), (0.85, 0.02, 0.86), 0.11, seed=seed, segs=8)
    # bow saw resting on the log
    k.box((0.2, -0.2, 0.9), (0.62, 0.015, 0.035), STEEL, rot=(0.3, 0, 0), bevel=0)
    for x in (-0.12, 0.52): k.box((x, -0.22, 1.02), (0.04, 0.03, 0.34), WOOD, rot=(0.3, 0, 0), bevel=0.008)
    k.box((0.2, -0.27, 1.14), (0.66, 0.03, 0.04), WOOD, rot=(0.3, 0, 0), bevel=0.008)
    # sawdust under the cut + a few offcuts
    _ico(k, (0.2, 0.0, 0.0), 0.26, HAY, (1.4, 1.0, 0.16), sub=2, jit=0.01, seed=seed)
    for i in range(4):
        k.box((rnd.uniform(-0.7, 0.7), rnd.uniform(-0.45, 0.45), 0.03), (rnd.uniform(0.12, 0.2), 0.08, 0.06), WOOD, rot=(0, 0, rnd.uniform(0, 3)), bevel=0.01)

def con_sawpit(k, seed=100):
    rnd = random.Random(seed); X, Y = 1.6, 0.45
    # hidden pit lining + floor (for terrain with holes) and the dark mouth decal at ground level
    for (a, b) in (((-X, -Y), (X, -Y)), ((X, -Y), (X, Y)), ((X, Y), (-X, Y)), ((-X, Y), (-X, -Y))):
        f = k.bm.faces.new([k.bm.verts.new(p) for p in ((b[0], b[1], -1.2), (a[0], a[1], -1.2), (a[0], a[1], 0.0), (b[0], b[1], 0.0))]); f.material_index = PLANKS
    f = k.bm.faces.new([k.bm.verts.new(p) for p in ((-X, -Y, -1.2), (X, -Y, -1.2), (X, Y, -1.2), (-X, Y, -1.2))]); f.material_index = VOID
    f = k.bm.faces.new([k.bm.verts.new(p) for p in ((-X, -Y, 0.015), (X, -Y, 0.015), (X, Y, 0.015), (-X, Y, 0.015))]); f.material_index = VOID
    k.bm.normal_update()
    # timber kerb with plank lining lip
    for s in (-1, 1):
        k.box((0, s * (Y + 0.12), 0.08), (2 * X + 0.48, 0.24, 0.18), WOOD, bevel=0.03)
        k.box((s * (X + 0.12), 0, 0.08), (0.24, 2 * Y, 0.18), WOOD, bevel=0.03)
        con_board(k, (0, s * (Y - 0.02), 0.02), (2 * X, 0.16, 0.04), rot=(math.pi / 2, 0, 0), col=3, seed=seed + s)
    # trestles across the pit, log on them, pit saw in the kerf
    for x in (-1.0, 1.0): k.box((x, 0, 0.3), (0.26, 1.5, 0.24), WOOD, bevel=0.035)
    con_log(k, (-2.0, 0.0, 0.72), (2.0, 0.02, 0.72), 0.3, seed=seed, segs=12)
    k.box((1.02, 0.0, 1.03), (1.9, 0.02, 0.012), VOID, bevel=0)
    k.box((0.25, 0.0, 0.3), (0.2, 0.02, 2.6), STEEL, bevel=0)
    k.box((0.25, 0.0, 1.62), (0.06, 0.58, 0.06), WOOD, bevel=0.015)
    k.box((0.25, 0.0, 1.5), (0.05, 0.05, 0.22), WOOD, bevel=0.01)
    # sawdust heaps and fresh cut boards
    for (x, y, r) in ((0.35, -0.82, 0.3), (0.05, -0.95, 0.2), (-0.5, 0.86, 0.26), (0.3, 0.84, 0.18), (1.4, 0.88, 0.2)):
        _ico(k, (x, y, 0.0), r, HAY, (1.5, 1.0, 0.22), sub=2, jit=0.015, seed=int(x * 10 + y))
    for i in range(2):
        con_board(k, (-0.3 + i * 0.05, -1.25 - i * 0.3, 0.03 + i * 0.05), (2.6, 0.26, 0.05), rot=(0, 0, 0.06 - i * 0.05), col=1 + 2 * i, seed=seed + i)
    con_skirt(k, -X - 0.24, X + 0.24, -Y - 0.24, Y + 0.24, -0.6, 0.0, SOIL)

def con_privy(k, seed=110):
    rnd = random.Random(seed); W = 0.6; Hf = 2.2; Hb = Hf - 1.2 * math.tan(math.radians(12))
    for (x, y) in ((-W, -W), (W, -W), (W, W), (-W, W)):
        h = Hf if y < 0 else Hb
        k.box((x, y, h / 2), (0.1, 0.1, h), WOOD, bevel=0.02)
        rock(k, (x, y, 0.04), (0.24, 0.24, 0.14), seed=seed + int(x * 10 + y * 3), mi=ROCK, segs=1)
    def zt(y): return Hf - (y + W) * math.tan(math.radians(12))
    # side + back walls: vertical boards
    n = 5
    for s in (-1, 1):
        for i in range(n):
            y = -W + 0.06 + (i + 0.5) * (2 * W - 0.12) / n
            con_beam_board(k, (s * (W + 0.01), y, 0.1), (s * (W + 0.01), y, zt(y) - 0.05), (2 * W - 0.12) / n - 0.012, 0.04, up=(s, 0, 0), col=rnd.randrange(8), seed=seed + i + 10 * s)
    for i in range(n):
        x = -W + 0.06 + (i + 0.5) * (2 * W - 0.12) / n
        con_beam_board(k, (x, W + 0.01, 0.1), (x, W + 0.01, Hb - 0.05), (2 * W - 0.12) / n - 0.012, 0.04, up=(0, 1, 0), col=rnd.randrange(8), seed=seed + i + 40)
    # front: door with Z battens and the crescent moon, lintel above
    for i in range(4):
        x = -W + 0.08 + (i + 0.5) * (2 * W - 0.16) / 4
        con_beam_board(k, (x, -W - 0.02, 0.12), (x, -W - 0.02, 1.95), (2 * W - 0.16) / 4 - 0.012, 0.04, up=(0, -1, 0), col=rnd.randrange(8), seed=seed + i + 60)
    for zz in (0.4, 1.65): k.box((0, -W - 0.06, zz), (2 * W - 0.25, 0.03, 0.1), WOOD, bevel=0.01)
    con_brace2(k, -W + 0.2, 0.45, W - 0.2, 1.6, -W - 0.06, 0.03, 0.09)
    k.box((0, -W - 0.02, 2.06), (2 * W + 0.1, 0.12, 0.14), WOOD, bevel=0.02)
    k.box((W - 0.2, -W - 0.08, 1.02), (0.04, 0.04, 0.1), IRON, bevel=0.005)
    pts = [(math.cos(a) * 0.11, math.sin(a) * 0.11) for a in [math.radians(40 + i * 28) for i in range(11)]]
    pts += [(0.055 + math.cos(a) * 0.09, math.sin(a) * 0.09) for a in [math.radians(300 - i * 24) for i in range(11)]]
    vs = [k.bm.verts.new((x, -W - 0.065, 1.78 + z)) for (x, z) in pts]
    f = k.bm.faces.new(vs); f.material_index = VOID; k.bm.normal_update()
    if f.normal.y > 0: f.normal_flip()
    # pent roof: plank boards falling to the back, bargeboards
    ang = math.radians(12)
    for i in range(6):
        x = -W - 0.12 + (i + 0.5) * (2 * W + 0.24) / 6
        p0 = Vector((x, -W - 0.2, Hf + 0.08 + 0.2 * math.tan(ang))); p1 = Vector((x, W + 0.25, Hf + 0.08 - (2 * W + 0.25) * math.tan(ang)))
        con_beam_board(k, p0, p1, (2 * W + 0.24) / 6 - 0.01, 0.04, up=(0, math.sin(ang), math.cos(ang)), col=rnd.randrange(8), seed=seed + 80 + i)
    for s in (-1, 1):
        con_beam(k, (s * (W + 0.13), -W - 0.2, Hf + 0.06 + 0.2 * math.tan(ang)), (s * (W + 0.13), W + 0.25, Hf + 0.06 - (2 * W + 0.25) * math.tan(ang)), 0.05, 0.12, WOOD, bevel=0.012)
    k.box((0, 0, 0.05), (2 * W, 2 * W, 0.1), PLANKS, bevel=0)
    con_skirt(k, -W - 0.05, W + 0.05, -W - 0.05, W + 0.05, -0.6, 0.02, SOIL)

def con_shrine(k, seed=120):
    rnd = random.Random(seed)
    k.box((0, 0, 0.09), (1.2, 1.2, 0.18), STONE, bevel=0.05, segs=2, jitter=0.01, seed=1)
    k.box((0, 0, 0.27), (0.9, 0.9, 0.18), STONE, bevel=0.05, segs=2, jitter=0.01, seed=2)
    for i, z in enumerate((0.36, 0.9, 1.44)):
        con_ashlar_block(k, (0, 0, z + 0.27), (0.6, 0.6, 0.54), rot=(0, 0, rnd.uniform(-0.03, 0.03)), seed=seed + i)
    k.box((0, 0, 2.04), (0.72, 0.72, 0.12), STONE, bevel=0.04)
    # niche head
    k.box((0, 0.04, 2.45), (0.66, 0.58, 0.7), STONE, bevel=0.05, segs=2)
    k.quad([(-0.2, -0.265, 2.18), (0.2, -0.265, 2.18), (0.2, -0.265, 2.62), (-0.2, -0.265, 2.62)], VOID, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    arch = [Vector((math.cos(a) * 0.2, -0.265, 2.62 + math.sin(a) * 0.2)) for a in [math.pi * i / 6 for i in range(7)]]
    f = k.bm.faces.new([k.bm.verts.new(p) for p in arch]); f.material_index = VOID; k.bm.normal_update()
    if f.normal.y > 0: f.normal_flip()
    for i in range(7):
        a = math.pi * (i + 0.5) / 7
        k.box((math.cos(a) * 0.27, -0.29, 2.62 + math.sin(a) * 0.27), (0.1, 0.06, 0.14), STONE, rot=(0, -(a - math.pi / 2), 0), bevel=0.02)
    lathe(k, [(0.0, 0.0), (0.09, 0.0), (0.08, 0.1), (0.06, 0.22), (0.07, 0.3), (0.05, 0.36), (0.055, 0.4), (0.0, 0.46)], center=(0, -0.16, 2.12), segs=8, mi=PAPER, cap_top=False)
    # gabled roof (ridge front-to-back) with a little bronze sun on the front
    for s in (-1, 1):
        k.box((s * 0.27, 0.04, 2.98), (0.62, 0.9, 0.07), ROOF, rot=(0, s * math.radians(38), 0), bevel=0.02)
    k.box((0, 0.04, 3.17), (0.08, 0.94, 0.08), WOOD, bevel=0.02)
    _cyl(k, (0, -0.44, 3.08), 0.1, 0.1, 0.03, 10, BRONZE, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    # candles on the niche sill and the upper step
    for (x, y, z, h) in ((-0.13, -0.24, 2.12, 0.1), (0.14, -0.23, 2.12, 0.13), (-0.3, -0.36, 0.36, 0.16), (0.28, -0.38, 0.36, 0.11), (0.36, -0.3, 0.36, 0.08)):
        _cyl(k, (x, y, z + h / 2), 0.03, 0.03, h, 6, PAPER)
        _ico(k, (x, y, z + h + 0.035), 0.022, GLOW, (1, 1, 1.8), sub=1)
    # flowers + offering bowl
    for i in range(9):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.5, 0.58)
        x, y = math.cos(a) * d, math.sin(a) * d
        if y < -0.2 and abs(x) < 0.3: continue
        _ico(k, (x, y, 0.22), rnd.uniform(0.07, 0.1), LEAF, (1, 1, 0.7), sub=1, jit=0.01, seed=i)
        _ico(k, (x + 0.02, y, 0.3), 0.045, PINK if i % 2 else YELLOW, sub=1)
    lathe(k, [(0.0, 0.0), (0.08, 0.0), (0.12, 0.06), (0.13, 0.08)], center=(0.0, -0.36, 0.36), segs=10, mi=CLAY)
    for i in range(3): _ico(k, (-0.03 + i * 0.035, -0.36, 0.43), 0.03, APPLE, sub=1)

# ------------------------------------------------------------------ builders
def con_house_plan(n, front, back, ends=("W.", ".W")):
    """wall modules (x, y, rot, char) and corners (x, y, rot) of an n x 2 house centred on the origin"""
    L = n * CELL
    walls = [(-L / 2 + 1.5 + 3 * i, -3, 0, front[i]) for i in range(n)] + [(-L / 2 + 1.5 + 3 * i, 3, 180, back[::-1][i]) for i in range(n)]
    walls += [(-L / 2, -1.5, -90, ends[0][0]), (-L / 2, 1.5, -90, ends[0][1]), (L / 2, 1.5, 90, ends[1][0]), (L / 2, -1.5, 90, ends[1][1])]
    corners = [(-L / 2, -3, 0), (L / 2, -3, 90), (L / 2, 3, 180), (-L / 2, 3, -90)]
    return walls, corners

def con_scaffold_run(coll, origin, walls, corners, faces, z, n, top=False):
    """Scaffold_Wall on every module of the chosen faces ('F' front -Y, 'B', 'L' -X end, 'R' +X end) + corners;
    top=True uses the short top-lift pieces (standards end above the deck, clear of the roof)"""
    sw, scn = ("SM_VK_Scaffold_Wall_Top", "SM_VK_Scaffold_Corner_Top") if top else ("SM_VK_Scaffold_Wall", "SM_VK_Scaffold_Corner")
    L = n * CELL
    def face_of(x, y, rot):
        return {0: "F", 180: "B", -90: "L", 90: "R"}[rot]
    for (x, y, rot, c) in walls:
        if face_of(x, y, rot) in faces: place_v(coll, sw, x, y, z, rot, origin, {})
    # a corner closes the run on its local -X face and wraps its local -Y face
    cmap = {(-1, -1): ("L", "F"), (1, -1): ("F", "R"), (1, 1): ("R", "B"), (-1, 1): ("B", "L")}
    for (x, y, rot) in corners:
        a, b = cmap[(1 if x > 0 else -1, 1 if y > 0 else -1)]
        if a in faces: place_v(coll, scn, x, y, z, rot, origin, {})

CON_FRAME = {"SM_VK_Roof_Mid": "SM_VK_Roof_Mid_Frame", "SM_VK_Roof_Gable": "SM_VK_Roof_Gable_Frame", "SM_VK_Roof_Hip": "SM_VK_Roof_Hip_Frame"}
def build_construction_site(coll, origin, stage, seed=0, style=None):
    """3x2 two-storey cottage (Stone or Plaster ground, Wall_Timber* upper floor, M roof with gable or hip ends)
    at construction stage 0 (site), 1 (walls), 2 (frame) or 3 (finished).  origin=(ox, oy, rot_z_radians);
    front (door) faces -Y; lot = 3x2 footprint + 2 cells in front (yard + stock cell) + 2 cells at +X (tools).
    style keys: ground "Stone"|"Plaster", ends ("gable"|"hip", "gable"|"hip") for the -X/+X roof ends, plus the
    usual plaster/shutter/roof recolours."""
    r = random.Random(seed * 13 + 5)
    st = {"ground": "Stone", "plaster": r.choice(["Cream", "White", "Ochre"]), "shutter": r.choice(["Teal", "Red", "Green", "Natural"]), "roof": "Red"}
    st.update(style or {})
    ground = st.get("ground", "Stone"); stone = ground == "Stone"
    ends = tuple(st.get("ends", ("gable", "gable")))
    n = 3; L = n * CELL; front = "WDW"; back = r.choice(["W.W", ".WW", "W.."])
    walls, corners = con_house_plan(n, front, back)
    gw = {"D": f"SM_VK_Wall_{ground}_Door", "W": f"SM_VK_Wall_{ground}_Window", ".": f"SM_VK_Wall_{ground}"}
    gc = f"SM_VK_Corner_{ground}"
    top = H1 + H2
    vst = {k_: v for k_, v in st.items() if k_ in ("plaster", "shutter", "roof", "stone")}
    own = {nm for nm, _, _ in WS_SPECS}         # my pieces only take the stone recolour (their PLASTER is mortar)
    ost = {"stone": st["stone"]} if "stone" in st else {}
    P = lambda piece, x, y, z, rot, s=None: place_v(coll, piece, x, y, z, rot, origin, (ost if piece in own else vst) if s is None else s)
    # scaffold on the front plus a gable end (a hip end's rafter tails would clash with the upper lift)
    faces = "FL" if (stage < 2 or ends[0] == "gable") else ("FR" if ends[1] == "gable" else "FB")
    if stage < 3:
        for cx in (-3.0, 0.0, 3.0):
            for cy in (-1.5, 1.5): P("SM_VK_BuildSite_Cell", cx, cy, 0, r.choice((0, 90, 180, -90)), {})
    if stage == 0:
        for (x, y, rot, c) in walls: P("SM_VK_Foundation_Wall", x, y, 0, rot)
        for (x, y, rot) in corners: P("SM_VK_Foundation_Corner", x, y, 0, rot)
    elif stage == 1:
        for (x, y, rot, c) in walls:
            if stone: P("SM_VK_Wall_Stone_Half_Door" if c == "D" else "SM_VK_Wall_Stone_Half", x, y, 0, rot)
            else: P("SM_VK_Wall_Plaster_Frame_Door" if c == "D" else "SM_VK_Wall_Plaster_Frame", x, y, 0, rot)
        for (x, y, rot) in corners: P("SM_VK_Corner_Stone_Half" if stone else gc, x, y, 0, rot)
        con_scaffold_run(coll, origin, walls, corners, faces, 0.0, n)
    else:
        for (x, y, rot, c) in walls: P(gw[c], x, y, 0, rot)
        for (x, y, rot) in corners: P(gc, x, y, 0, rot)
        for (x, y, rot, c) in walls:
            if stage == 2: up = "SM_VK_Wall_Timber_Frame"
            else: up = "SM_VK_Wall_Timber_Window" if c in "WD" else r.choice(["SM_VK_Wall_Timber", "SM_VK_Wall_Timber_X", "SM_VK_Wall_Timber_K"])
            P(up, x, y, H1, rot)
        for (x, y, rot) in corners: P("SM_VK_Corner_Timber", x, y, H1, rot)
        for i in range(n):
            x = -L / 2 + 1.5 + 3 * i; rot = 180 if i == 0 else 0
            pc = "SM_VK_Roof_Mid"
            if i in (0, n - 1): pc = "SM_VK_Roof_Hip" if ends[0 if i == 0 else 1] == "hip" else "SM_VK_Roof_Gable"
            P(CON_FRAME[pc] if stage == 2 else pc, x, 0, top, rot)
        ci = n - 1 if ends[1] == "gable" else (0 if ends[0] == "gable" else 1)
        P("SM_VK_Chimney", -L / 2 + 1.5 + 3 * ci, 0, top, 0)
        if stage == 2:
            con_scaffold_run(coll, origin, walls, corners, faces, 0.0, n)
            con_scaffold_run(coll, origin, walls, corners, faces, H1, n, top=True)
        else:
            for (x, y, rot, c) in walls:
                if c == "W" and rot == 0: P("SM_VK_Prop_FlowerBox", x, y - (0.55 if stone else 0.5), 0.78 if stone else 0.9, rot, {})
    # site dressing (stock cell on the lot in front, left of the door path; tools on the +X cell)
    if stage < 3:
        P("SM_VK_Stockpile_Border", -3.0, -7.0, 0, 0, {})
        pile = ({0: "SM_VK_Pile_Stone_3", 1: "SM_VK_Pile_Stone_2", 2: "SM_VK_Pile_Planks_2"} if stone else
                {0: "SM_VK_Pile_Logs_2", 1: "SM_VK_Pile_Planks_3", 2: "SM_VK_Pile_Planks_2"})[stage]
        P(pile, -3.0, -7.0, 0, 180 if r.random() < 0.5 else 0, {})
        P("SM_VK_Prop_Wheelbarrow", 1.9, -6.6, 0, 150 + r.uniform(-15, 15), {})
    if stage == 0:
        P("SM_VK_Pile_Logs_1", 7.4, -1.2, 0, 90, {})
        P("SM_VK_Prop_ChoppingBlock", 6.9, 2.2, 0, r.uniform(0, 360), {})
    elif stage == 1:
        if stone:
            P("SM_VK_Prop_MortarTub", 2.6, -5.35, 0, 10, {})
            P("SM_VK_Prop_ShearLegs", 6.6, 0.4, 0, 0, {})
            P("SM_VK_Pile_Stone_1", 7.6, -3.9, 0, 90, {})
        else:
            P("SM_VK_Prop_Sawhorse", 2.7, -5.3, 0, 12, {})
            P("SM_VK_Pile_Logs_1", 7.4, -1.0, 0, 90, {})
            P("SM_VK_Prop_ChoppingBlock", 6.8, 2.3, 0, r.uniform(0, 360), {})
    elif stage == 2:
        P("SM_VK_Prop_LadderLean", L / 2, 1.5, 0, 90, {})
        P("SM_VK_Prop_Sawhorse", 6.6, -2.2, 0, 70, {})
        P("SM_VK_Pile_Planks_1", 7.4, 1.6, 0, 90, {})
        P("SM_VK_Scaffold_Ladder", -1.5 - 3.0, -3.0, 0, 0, {})
    # lot: x -4.5..10.5 (2 tool cells at +X), y -9..3 (2 yard/stock cells at -Y)
    return dict(footprint=(n, 2), lot=(5, 4), wall_top=top, ground=ground, ends=ends)

def build_camp(coll, origin, seed=0):
    """settler camp (T0), 3x3 cells centred on origin: 2 ridge tents + a bell tent around a campfire,
    bedrolls, covered wagon, first storage (Crates, Sacks, BarrelStack, Pile_Logs_1), privy and wayside shrine"""
    r = random.Random(seed * 7 + 1)
    P = lambda piece, x, y, rot, st=None: place_v(coll, piece, x, y, 0, rot, origin, st or {})
    def facing(x, y):   # rotation so a piece's local -Y (door) faces the fire at the origin
        return math.degrees(math.atan2(-y, -x)) + 90
    P("SM_VK_Prop_Campfire", 0, 0, r.uniform(0, 360))
    # three tents on a ring round the fire, doors (local -Y) towards it
    cl = ["Red", "Blue", "Green", "Yellow"]; r.shuffle(cl)
    for i, (a, rr, pc) in enumerate(((100, 3.3, "SM_VK_Tent_A"), (203, 3.3, "SM_VK_Tent_A"), (318, 3.4, "SM_VK_Tent_Bell"))):
        x = math.cos(math.radians(a)) * rr; y = math.sin(math.radians(a)) * rr
        P(pc, x, y, facing(x, y) + r.uniform(-6, 6), {"cloth": cl[i]})
    # bedrolls between the doors, head end (+Y pillow) away from the fire
    for a in (45, 155, 262, 12):
        rr = 1.5 if a != 12 else 1.75; x = math.cos(math.radians(a)) * rr; y = math.sin(math.radians(a)) * rr
        P("SM_VK_Prop_Bedroll", x, y, a - 90 + r.uniform(-12, 12), {"cloth": r.choice(["Red", "Blue", "Green", "Yellow"])})
    # the wagon parked on the east side, stores unloaded around it
    P("SM_VK_Prop_Wagon_Covered", 3.75, 1.9, 95 + r.uniform(-4, 4))
    P("SM_VK_Prop_BarrelStack", 1.95, 4.05, 90 + r.uniform(-8, 8))
    P("SM_VK_Prop_Crates", -3.75, 2.95, 90 + r.uniform(-6, 6))
    P("SM_VK_Prop_Sacks", -2.45, 4.55, r.uniform(0, 360))
    # firewood corner (south-west)
    P("SM_VK_Pile_Logs_1", -2.3, -4.45, r.choice((0, 180)) + r.uniform(-4, 4))
    P("SM_VK_Prop_ChoppingBlock", -4.55, -4.0, r.uniform(0, 360))
    # privy just outside the north-west corner (door turned away), the settlers' shrine on the west edge facing the fire
    P("SM_VK_Prop_Privy", -5.3, 5.2, -90 + r.uniform(-5, 5))
    P("SM_VK_Prop_WaysideShrine", -4.6, 0.8, facing(-4.6, 0.8))
    return dict(footprint=(3, 3), beds=6)

CON_PILES = ["Logs", "Planks", "Stone", "Sacks"]
def build_stockpile(coll, origin, w=2, d=2, seed=0, kinds=None):
    """player-zoned storage: Stockpile_Border on every cell (w x d cells centred on origin) with mixed piles"""
    r = random.Random(seed * 11 + 3); kinds = kinds or CON_PILES
    for i in range(w):
        for j in range(d):
            x = (i - (w - 1) / 2) * CELL; y = (j - (d - 1) / 2) * CELL
            place_v(coll, "SM_VK_Stockpile_Border", x, y, 0, r.choice((0, 180)), origin, {})
            kind = kinds[(i * d + j + seed) % len(kinds)]; lvl = r.choice((1, 2, 3, 3, 2))
            if r.random() < 0.12: continue      # an empty bay
            o = place_v(coll, f"SM_VK_Pile_{kind}_{lvl}", x, y, 0, r.choice((0, 180)), origin, {})
            if o is not None: o.scale = (0.88, 0.88, 1.0)      # keep the pile inside the border kerb
    return dict(footprint=(w, d), storage=w * d)

def build_sawpit_yard(coll, origin, seed=0):
    """sawpit yard (T1, logs -> planks): pit across 2x1 cells centred on origin, log stock behind-left,
    plank stock behind-right, sawhorse, chopping block and barrow"""
    r = random.Random(seed * 5 + 9)
    P = lambda piece, x, y, rot: place_v(coll, piece, x, y, 0, rot, origin, {})
    P("SM_VK_Prop_SawPit", 0, 0, r.choice((0, 180)))
    for (x, pile) in ((-1.5, "SM_VK_Pile_Logs_3"), (1.5, "SM_VK_Pile_Planks_2")):
        P("SM_VK_Stockpile_Border", x, 3.0, 0); P(pile, x, 3.0, r.choice((0, 180)))
    P("SM_VK_Prop_Sawhorse", 3.9, -1.0, 80 + r.uniform(-10, 10))
    P("SM_VK_Prop_ChoppingBlock", -3.8, -0.9, r.uniform(0, 360))
    P("SM_VK_Prop_Wheelbarrow", -3.7, 0.8, 205 + r.uniform(-10, 10))
    return dict(footprint=(2, 2), jobs=2)

# ------------------------------------------------------------------ registry (keep EXTRA_SPECS line last)
CON_NG = dict(wobble=False, grime=True); CON_NW = dict(wobble=False, grime=False)
WS_SPECS = [
    ("SM_VK_BuildSite_Cell", con_buildsite_cell, CON_NW),
    ("SM_VK_Foundation_Wall", con_foundation_wall, CON_NG),
    ("SM_VK_Foundation_Corner", con_foundation_corner, CON_NG),
    ("SM_VK_Wall_Stone_Half", lambda k: con_wall_stone_half(k, False, 1), {}),
    ("SM_VK_Wall_Stone_Half_Door", lambda k: con_wall_stone_half(k, True, 2), {}),
    ("SM_VK_Corner_Stone_Half", con_corner_stone_half, CON_NG),
    ("SM_VK_Wall_Plaster_Frame", lambda k: con_wall_plaster_frame(k, False), {}),
    ("SM_VK_Wall_Plaster_Frame_Door", lambda k: con_wall_plaster_frame(k, True), {}),
    ("SM_VK_Wall_Timber_Frame", con_wall_timber_frame, dict(wobble=True, grime=False)),
    ("SM_VK_Roof_Mid_Frame", con_roof_mid_frame, CON_NW),
    ("SM_VK_Roof_Gable_Frame", con_roof_gable_frame, CON_NW),
    ("SM_VK_Roof_Hip_Frame", con_roof_hip_frame, CON_NW),
    ("SM_VK_Scaffold_Wall", con_scaffold_wall, CON_NW),
    ("SM_VK_Scaffold_Corner", con_scaffold_corner, CON_NW),
    ("SM_VK_Scaffold_Wall_Top", lambda k: con_scaffold_wall(k, 1, top=2.3), CON_NW),
    ("SM_VK_Scaffold_Corner_Top", lambda k: con_scaffold_corner(k, 1, top=2.3), CON_NW),
    ("SM_VK_Scaffold_Ladder", con_scaffold_ladder, CON_NW),
    ("SM_VK_Prop_Wheelbarrow", con_wheelbarrow, CON_NG),
    ("SM_VK_Prop_MortarTub", con_mortar_tub, CON_NG),
    ("SM_VK_Prop_LadderLean", con_ladder_lean, CON_NG),
    ("SM_VK_Prop_ShearLegs", con_shear_legs, CON_NG),
    ("SM_VK_Pile_Logs_1", lambda k: con_pile_logs(k, 1), CON_NG),
    ("SM_VK_Pile_Logs_2", lambda k: con_pile_logs(k, 2), CON_NG),
    ("SM_VK_Pile_Logs_3", lambda k: con_pile_logs(k, 3), CON_NG),
    ("SM_VK_Pile_Planks_1", lambda k: con_pile_planks(k, 1), CON_NG),
    ("SM_VK_Pile_Planks_2", lambda k: con_pile_planks(k, 2), CON_NG),
    ("SM_VK_Pile_Planks_3", lambda k: con_pile_planks(k, 3), CON_NG),
    ("SM_VK_Pile_Stone_1", lambda k: con_pile_stone(k, 1), CON_NG),
    ("SM_VK_Pile_Stone_2", lambda k: con_pile_stone(k, 2), CON_NG),
    ("SM_VK_Pile_Stone_3", lambda k: con_pile_stone(k, 3), CON_NG),
    ("SM_VK_Pile_Sacks_1", lambda k: con_pile_sacks(k, 1), CON_NG),
    ("SM_VK_Pile_Sacks_2", lambda k: con_pile_sacks(k, 2), CON_NG),
    ("SM_VK_Pile_Sacks_3", lambda k: con_pile_sacks(k, 3), CON_NG),
    ("SM_VK_Stockpile_Border", con_stockpile_border, CON_NG),
    ("SM_VK_Tent_A", con_tent_a, CON_NG),
    ("SM_VK_Tent_Bell", con_tent_bell, CON_NG),
    ("SM_VK_Prop_Campfire", con_campfire, CON_NG),
    ("SM_VK_Prop_Bedroll", con_bedroll, CON_NG),
    ("SM_VK_Prop_Wagon_Covered", con_wagon_covered, CON_NG),
    ("SM_VK_Prop_ChoppingBlock", con_chopping_block, CON_NG),
    ("SM_VK_Prop_Sawhorse", con_sawhorse, CON_NG),
    ("SM_VK_Prop_SawPit", con_sawpit, CON_NG),
    ("SM_VK_Prop_Privy", con_privy, CON_NG),
    ("SM_VK_Prop_WaysideShrine", con_shrine, CON_NG),
]
EXTRA_SPECS += WS_SPECS
