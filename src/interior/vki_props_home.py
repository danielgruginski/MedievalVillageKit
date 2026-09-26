# ===================== VKI PROPS HOME: §5.1 home furniture (PKG-H, agent "home") =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md §5 (conventions) and §5.1 (list); §10 amendments.
# Loaded by vki_ns() (VKI_TEXTS, after vki_links). Every top-level name starts with vki_/VKI_ (T18).
# Props: origin at the footprint centre on the floor, back toward local +Y, front toward -Y (§2.1, §5).
#   floor       free-standing (size <= 1.5 n - 0.10)
#   wall_floor  vki_back_y = the geometry's max y: vki_place puts that plane on the proud line (0.285 O / 0.185 P)
#   wall_hung   back on the wall face (T/2); geometry is authored at its real height (Shelf_Wall_150: z 1.20 .. 1.93)
#   table       origin on the table-top surface: TableDress_* are placed with z = 0.80 (vki_table_z)
# Conventions (§5): table tops 0.10 thick at 0.80, form seats 0.08 at 0.48, legs 0.12-0.14 splayed 5-8 deg, round
# things 16 segments (small pottery / food below r 0.12: 12; TableDress items 10), flat floor contact, food from the
# goods atlas (goods_map), bedding from the textile atlas, grime "prop".
# Tops: pale HEWN boards (top face and chamfers) over oak (WOOD) sides -- the scrubbed-planks material renders at
# the floor's luma (0.24 vs FlagRustic 0.25-0.30, the §4.3 prop-top palette rule wants >= 0.12 apart); hewn tops
# render ~0.45 and read like the pale cap line. Split tops (2-3 boards) show their V-joints.
# Build: g["vki_ws_build"]("home", VKI_HOME_NAMES); test: g["vki_test_pieces"](VKI_HOME_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_HOME_X = Vector((1.0, 0.0, 0.0))
VKI_HOME_Y = Vector((0.0, 1.0, 0.0))
VKI_HOME_Z = Vector((0.0, 0.0, 1.0))
VKI_HOME_SEG = 16                 # round things (§5)
VKI_HOME_SEG_S = 12               # small round things (r < 0.12: pottery, food)
VKI_HOME_SEG_D = 10               # TableDress items (400-tri dressing budget)
VKI_HOME_TABLE_Z = 0.80           # table-top surface = the table mount height
VKI_HOME_TOP_T = 0.10             # table tops 0.10 thick
VKI_HOME_FORM_Z = 0.48            # form seat top
VKI_HOME_FORM_T = 0.08            # form seat thickness
VKI_HOME_TOP_BEV = 0.025          # chamfer round the top edge of every top (V-joints between boards)
VKI_HOME_LEG_W = 0.13             # legs 0.12-0.14
VKI_HOME_SPLAY = (5.0, 7.0)       # leg splay in degrees: along the length (x), across (y)
VKI_HOME_BARK_TILE = 0.6          # bark ridges on logs
# hearth socket: §5.1 says (0, 0, 0.5) 250 W; there it sat inside the flames and blew the kerb, ash and flames out to
# near-white (the Timber fireplace had the same fault, §10.2). Moved in front of the fire above the flame tips and
# below the pot's rim (at 0.90 it lit the stew inside the pot like a lamp), with a soft radius, at the spec's 250 W.
VKI_HOME_HEARTH_LIGHT = (0.0, -0.28, 0.74)
VKI_HOME_HEARTH_W = 250.0
VKI_HOME_HEARTH_RADIUS = 0.35
VKI_HOME_OVEN_LIGHT = (0.0, -0.72, 1.05)    # out in front of and above the oven mouth, 150 W (§5.1)
VKI_HOME_OVEN_W = 150.0


# ---------------------------------------------------------------- generic helpers
def vki_home_uv(k, faces, mi, U, V, tile, off=(0.0, 0.0)):
    """planar UVs (u = p.U / tile, v = p.V / tile) and material mi on faces"""
    U = Vector(U); V = Vector(V)
    for f in faces:
        f.material_index = mi
        for l in f.loops:
            p = l.vert.co
            l[k.uv].uv = (p.dot(U) / tile + off[0], p.dot(V) / tile + off[1])


def vki_home_new_verts(k, before):
    return [v for v in k.bm.verts if v not in before]


def vki_home_box(k, x0, x1, y0, y1, z0, z1, mi=WOOD, bev=0.015, segs=1, jitter=0.0, seed=0, rot=(0, 0, 0)):
    """box from its extents (Kit.box: WOOD grain along the longest side); rot turns it about its centre"""
    return list(set(k.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mi,
                          rot=rot, bevel=bev, segs=segs, jitter=jitter, seed=seed)))


def vki_home_slab(k, x0, x1, y0, y1, z0, z1, bev=VKI_HOME_TOP_BEV, top=HEWN, side=WOOD, edge=HEWN, along="x",
                  planks=None, seed=0, segs=1):
    """a board: `top` on the upward face (grain along `along`; PLANKS: the painted boards of T_VK_Planks run along
    it, `planks` of them across the width), `edge` on the upper chamfers (grain along each edge), `side` (WOOD,
    grain along the long side) below. Returns the new faces."""
    before = set(k.bm.faces)
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    k.box(c, (x1 - x0, y1 - y0, z1 - z0), side, bevel=bev, segs=segs)
    fs = [f for f in k.bm.faces if f not in before]
    k.bm.normal_update()
    rnd = random.Random(7919 * seed + 17)
    gx = along == "x"
    g, acr = (VKI_HOME_X, VKI_HOME_Y) if gx else (VKI_HOME_Y, VKI_HOME_X)
    wa, a0 = ((y1 - y0), y0) if gx else ((x1 - x0), x0)
    tops = [f for f in fs if f.normal.z > 0.95]
    edges = [f for f in fs if 0.25 < f.normal.z <= 0.95]
    if top == PLANKS:
        n = planks or max(1, int(round(wa / 0.30)))
        t = 8.0 * wa / n                                  # T_VK_Planks: 8 boards per tile across (u)
        vki_home_uv(k, tops, PLANKS, acr, g, t, (-a0 / t + rnd.randrange(8) / 8.0, rnd.random()))
    elif top is not None:
        vki_home_uv(k, tops, top, g, acr, vki_tile(top), (rnd.random(), rnd.random()))
    if edge is not None:
        for f in edges:
            n_ = f.normal
            d = Vector((-n_.y, n_.x, 0.0))
            d = d.normalized() if d.length > 1e-3 else g.copy()
            vki_home_uv(k, [f], edge, d, n_.cross(d).normalized(), vki_tile(edge), (rnd.random(), rnd.random()))
    return fs


def vki_home_top(k, x0, x1, y0, y1, z0, z1, boards=1, along="x", bev=0.02, seed=0, side=WOOD, tone=0.08):
    """a top of `boards` boards side by side (split across the grain): pale HEWN top face and chamfers (the
    chamfers make the V-joints), WOOD below; each board a little darker or lighter (vki_dark up to `tone`)"""
    rnd = random.Random(911 * seed + 5)
    out = []
    for i in range(boards):
        if along == "x":
            w = (y1 - y0) / boards; sp = (x0, x1, y0 + i * w, y0 + (i + 1) * w)
        else:
            w = (x1 - x0) / boards; sp = (x0 + i * w, x0 + (i + 1) * w, y0, y1)
        fs = vki_home_slab(k, sp[0], sp[1], sp[2], sp[3], z0, z1, bev=bev, top=HEWN, side=side, edge=HEWN,
                           along=along, seed=seed * 7 + i)
        if tone:
            k.set_dark(list({v for f in fs for v in f.verts}), tone * rnd.random())
        out += fs
    return out


def vki_home_boards_v(k, faces, mi=PLANKS, across=VKI_HOME_X, n=None, width=None, seed=0):
    """vertical boards: PLANKS on `faces` with the painted boards running up (z); `n` boards over `width`"""
    rnd = random.Random(seed)
    t = 8.0 * width / n if (n and width) else 1.6
    vki_home_uv(k, faces, mi, across, VKI_HOME_Z, t, (rnd.randrange(8) / 8.0, rnd.random()))


def vki_home_leg(k, top_xy, bot_xy, z0, z1, w, d=None, mi=WOOD, bev=0.012):
    """a splayed leg: a hexahedron with a flat horizontal foot (w x d at bot_xy, z0) and top (at top_xy, z1),
    chamfered, grain along the leg. Returns its faces."""
    d = w if d is None else d
    bm = k.bm
    before = set(bm.faces)
    vs = []
    for (cx, cy), z in ((bot_xy, z0), (top_xy, z1)):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new((cx + sx * w / 2, cy + sy * d / 2, z)))
    b, t = vs[:4], vs[4:]
    fs = [bm.faces.new(b[::-1]), bm.faces.new(t)]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((b[i], b[j], t[j], t[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    if bev > 0:
        edges = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges + vs, offset=min(bev, 0.45 * min(w, d)), segments=1, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    fs = [f for f in bm.faces if f not in before]
    bm.normal_update()
    ax = (Vector((top_xy[0], top_xy[1], z1)) - Vector((bot_xy[0], bot_xy[1], z0))).normalized()
    sd = (VKI_HOME_X - ax * ax.dot(VKI_HOME_X)).normalized()
    k.project(fs, mi, axes=[ax, sd, ax.cross(sd)], sizes=[z1 - z0, w, d],
              offset=vki_hash_off((top_xy[0], top_xy[1], z1)))
    return fs


def vki_home_lathe(k, prof, c=(0.0, 0.0, 0.0), segs=VKI_HOME_SEG, mi=CLAY, smooth=True, sx=1.0, sy=1.0, rot=None,
                   uv="cyl", tile=None, a0=0.0, closed=False):
    """closed solid of revolution about local Z. prof = [(r, z), ...] bottom to top: an end with r = 0 is a pole
    (triangle fan), any other end gets an n-gon cap; closed=True joins the last ring back to the first (bands,
    hoops: give the profile counter-clockwise in (r, z)). sx / sy stretch the rings (ovals); rot (Matrix) turns it
    about its local origin before it moves to c. uv "cyl": u around at the widest radius, v = z; "cylv": u = z,
    v around (WOOD grain up the staves). Returns (verts, faces)."""
    bm = k.bm
    rings, info = [], {}
    for r, z in prof:
        if r <= 1e-9:
            v = bm.verts.new((0.0, 0.0, z)); info[v] = (None, z)
            rings.append([v])
        else:
            rg = []
            for i in range(segs):
                a = a0 + 2 * math.pi * i / segs
                v = bm.verts.new((math.cos(a) * r * sx, math.sin(a) * r * sy, z)); info[v] = (i, z)
                rg.append(v)
            rings.append(rg)
    fs = []
    if not closed and len(rings[0]) > 1:
        fs.append(bm.faces.new(rings[0][::-1]))
    pairs = list(zip(rings[:-1], rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
    for A, B in pairs:
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(segs):
            j = (i + 1) % segs
            if len(A) == 1:
                fs.append(bm.faces.new((A[0], B[j], B[i])))
            elif len(B) == 1:
                fs.append(bm.faces.new((A[i], A[j], B[0])))
            else:
                fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    if not closed and len(rings[-1]) > 1:
        fs.append(bm.faces.new(rings[-1]))
    vs = [v for rg in rings for v in rg]
    rmax = max(r for r, _ in prof) * (sx + sy) / 2
    tt = tile or vki_tile(mi)
    circ = 2 * math.pi * max(rmax, 1e-3)
    arc, s_ = {}, 0.0                                           # arc length along the profile ("cylr")
    for j, (r, z) in enumerate(prof):
        if j:
            s_ += math.hypot(r - prof[j - 1][0], z - prof[j - 1][1])
        arc[j] = s_
    ring_of = {v: j for j, rg in enumerate(rings) for v in rg}
    for f in fs:
        idx = [info[l.vert][0] for l in f.loops]
        wrap = 0 in idx and (segs - 1) in idx
        us = []
        for l in f.loops:
            i, z = info[l.vert]
            if i is None:
                us.append(None)
                continue
            ii = segs if (wrap and i == 0) else i
            if uv == "cylr":                                    # true scale round each ring (courses converge)
                us.append((ii / segs) * 2 * math.pi * prof[ring_of[l.vert]][0] * (sx + sy) / 2 / tt)
            else:
                us.append((ii / segs) * circ / tt)
        known = [u for u in us if u is not None]
        um = sum(known) / len(known) if known else 0.0
        for l, u in zip(f.loops, us):
            u = um if u is None else u
            z = info[l.vert][1]
            if uv == "cylv":
                l[k.uv].uv = (z / tt, u)
            elif uv == "cylr":
                l[k.uv].uv = (u, arc[ring_of[l.vert]] / tt)
            else:
                l[k.uv].uv = (u, z / tt)
        f.material_index = mi
        f.smooth = smooth
    M = Matrix.Translation(Vector(c))
    if rot is not None:
        M = M @ (rot.to_4x4() if len(rot) == 3 else rot)
    bmesh.ops.transform(bm, matrix=M, verts=vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    if uv == "cyl":                                             # caps, lips, floors: planar (no radial smear)
        flat = [f for f in fs if abs(f.normal.z) > 0.8]
        k.project(flat, mi)
        for f in flat:
            f.smooth = smooth
    return vs, fs


def vki_home_hoop(k, c, r_in, r_out, h, segs=VKI_HOME_SEG, mi=IRON, sx=1.0, sy=1.0, rot=None, smooth=False):
    """closed band (barrel hoop, rim, ring handle): annulus r_in..r_out, height h, about local Z through c"""
    return vki_home_lathe(k, [(r_in, -h / 2), (r_out, -h / 2), (r_out, h / 2), (r_in, h / 2)], c=c, segs=segs,
                          mi=mi, smooth=smooth, sx=sx, sy=sy, rot=rot, closed=True)


def vki_home_cyl(k, x, y, z0, r1, r2, h, segs=VKI_HOME_SEG, mi=WOOD, rot=None):
    """_cyl standing on z0 (its base at z0, axis +Z unless rot); returns verts"""
    if rot is None:
        return _cyl(k, (x, y, z0 + h / 2), r1, r2, h, segs, mi)
    ax = rot.to_3x3() @ VKI_HOME_Z
    c = Vector((x, y, z0)) + ax * (h / 2)
    return _cyl(k, tuple(c), r1, r2, h, segs, mi, rot=rot.to_4x4() if len(rot) == 3 else rot)


def vki_home_log(k, c, r, ln, rz=0.0, ry=0.0, segs=10, dark=0.0, mi=BARK_OAK):
    """a log along local X turned rz about Z and tilted ry about Y (+ry lowers the +X end): bark round (ridges along
    the log), each end one painted log end of T_VK_EndGrain (vki_endgrain_fit). dark: vki_dark. Returns verts."""
    R = Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(math.pi / 2, 4, "Y")
    vs = _cyl(k, tuple(c), r, r * 0.95, ln, segs, mi, rot=R)
    k.bm.normal_update()
    R3 = R.to_3x3()
    ax = R3 @ VKI_HOME_Z; e1 = R3 @ VKI_HOME_X; e2 = R3 @ VKI_HOME_Y
    cc = Vector(c)
    for f in vki_faces_of(vs):
        if abs(f.normal.dot(ax)) > 0.9:
            U = f.normal.cross(VKI_HOME_Z if abs(f.normal.z) < 0.9 else VKI_HOME_X).normalized()
            vki_endgrain_fit(k, [f], f.calc_center_median(), U, f.normal.cross(U), r, fill=VKI_ENDGRAIN_R)
            continue
        ang = [math.atan2((l.vert.co - cc).dot(e2), (l.vert.co - cc).dot(e1)) for l in f.loops]
        if max(ang) - min(ang) > math.pi:
            ang = [a + 2 * math.pi if a < 0 else a for a in ang]
        f.material_index = mi
        for l, a in zip(f.loops, ang):
            l[k.uv].uv = (a * r / VKI_HOME_BARK_TILE, (l.vert.co - cc).dot(ax) / VKI_HOME_BARK_TILE)
    if dark:
        k.set_dark(vs, dark)
    return vs


def vki_home_billet(k, c, r, ln, rz=0.0, ry=0.0, split=WOOD, dark=0.0):
    """a split half-log along local X: bark on the round, the split face up (oak grain, not pale), end grain at
    the ends"""
    n = 6
    poly = [(math.cos(math.pi + math.pi * i / n) * r, math.sin(math.pi + math.pi * i / n) * r + r * 0.35)
            for i in range(n + 1)]
    vs, fs = vki_prism(k, poly, -ln / 2, ln / 2, BARK_OAK, axis="x", project=False)
    R = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(ry, 4, "Y")
    bmesh.ops.transform(k.bm, matrix=R, verts=vs)
    k.bm.normal_update()
    ax = R.to_3x3() @ VKI_HOME_X
    up = R.to_3x3() @ VKI_HOME_Z
    for f in fs:
        n_ = f.normal
        if abs(n_.dot(ax)) > 0.9:
            U = n_.cross(VKI_HOME_Z).normalized()
            vki_endgrain_fit(k, [f], f.calc_center_median(), U, n_.cross(U), r, fill=VKI_ENDGRAIN_R)
        elif n_.dot(up) > 0.95:
            vki_home_uv(k, [f], split, ax, up.cross(ax).normalized(), vki_tile(split), vki_hash_off(c))
        else:
            vki_home_uv(k, [f], BARK_OAK, n_.cross(ax).normalized(), ax, VKI_HOME_BARK_TILE, vki_hash_off(c))
    if dark:
        k.set_dark(vs, dark)
    return vs


def vki_home_drape(k, faces, cell, ztop, along="x"):
    """a textile atlas cell on a cover draped over a bed: the top maps planar (u along `along`), each side face is
    unfolded outward by its depth below ztop, so the pattern runs on over the edges down to the hem"""
    rows = []
    k.bm.normal_update()
    for f in faces:
        n = f.normal
        side = abs(n.z) < 0.6
        for l in f.loops:
            p = l.vert.co
            a, b = (p.x, p.y) if along == "x" else (p.y, -p.x)
            if side:
                d = max(0.0, ztop - p.z)
                na, nb = (n.x, n.y) if along == "x" else (n.y, -n.x)
                if abs(na) >= abs(nb):
                    a += math.copysign(d, na)
                else:
                    b += math.copysign(d, nb)
            rows.append((l, a, b))
        f.material_index = VKI_TEXTILE
    a0 = min(r_[1] for r_ in rows); a1 = max(r_[1] for r_ in rows)
    b0 = min(r_[2] for r_ in rows); b1 = max(r_[2] for r_ in rows)
    for l, a, b in rows:
        l[k.uv].uv = vki_textile_uv(cell, (a - a0) / max(a1 - a0, 1e-6), (b - b0) / max(b1 - b0, 1e-6))


def vki_home_cover(k, x0, x1, y0, y1, z0, z1, cell, along="x", bev=0.03, wave=0.006, seed=0):
    """a quilt / blanket: a soft slab (2-segment bevel) whose top undulates a little, on the textile atlas"""
    vs = vki_home_box(k, x0, x1, y0, y1, z0, z1, VKI_TEXTILE, bev=bev, segs=2)
    ph = random.Random(seed).random() * 6.0
    for v in vs:
        if v.co.z > z1 - bev * 0.7:
            v.co.z += wave * math.sin(v.co.x * 6.3 + ph) * math.cos(v.co.y * 4.7 + ph)
    vki_home_drape(k, vki_faces_of(vs), cell, z1, along=along)
    return vs


def vki_home_squash(vs, c, below=0.5, above=1.0):
    """flatten an ico's lower half toward its centre height (items resting on a surface), optional top scale"""
    for v in vs:
        dz = v.co.z - c[2]
        v.co.z = c[2] + dz * (below if dz < 0 else above)


def vki_home_ico(k, c, r, mi, scale=(1, 1, 1), sub=2, jit=0.0, seed=0, rest=None, smooth=True):
    """_ico (sub 2 = 80 faces, sub 1 = the 20-face icosahedron) with smooth faces; rest=z: the lowest point sits
    5 mm under z (resting, never coplanar)"""
    vs = _ico(k, c, r, mi, scale=scale, sub=sub, jit=jit, seed=seed)
    if rest is not None:
        dz = rest - 0.005 - min(v.co.z for v in vs)
        for v in vs:
            v.co.z += dz
    for f in vki_faces_of(vs):
        f.smooth = smooth
    return vs


def vki_home_sack(k, x, y, z, s=1.0, seed=0, mi=BURLAP):
    """tied grain sack resting on z: a lumpy body, a gathered neck with a cord and a tuft"""
    vs = _ico(k, (x, y, z + 0.2 * s), 0.21 * s, mi, scale=(1.0, 0.85, 1.05), sub=2, jit=0.012 * s, seed=seed)
    vki_home_squash(vs, (x, y, z + 0.2 * s), below=0.55)
    dz = z - 0.006 - min(v.co.z for v in vs)
    for v in vs:
        v.co.z += dz
    top = max(v.co.z for v in vs)
    fs = vki_faces_of(vs)
    k.bm.normal_update()
    k.project(fs, mi)
    for f in fs:
        f.smooth = True
    vki_home_cyl(k, x, y, top - 0.03 * s, 0.06 * s, 0.045 * s, 0.10 * s, segs=8, mi=mi)
    vki_home_hoop(k, (x, y, top + 0.02 * s), 0.04 * s, 0.058 * s, 0.022 * s, segs=8, mi=HIDE)
    t = vki_home_ico(k, (x, y, top + 0.085 * s), 0.055 * s, mi, scale=(1.3, 1.0, 0.7), sub=1, jit=0.01 * s,
                     seed=seed + 1)
    k.project(vki_faces_of(t), mi)
    return vs


def vki_home_meta(k, mount="floor", tier="furniture", back=None, use=None, **kw):
    """prop metadata (§3.4, §5): class, mount, tier (T9 budget), use points [x, y, facing_deg] (0 = local +Y,
    90 = +X, clockwise), vki_back_y on wall-mounted props (back="geo": the geometry's max y)"""
    if back == "geo":
        back = round(max(v.co.y for v in k.bm.verts), 5)
    k.meta.update(vki_class="prop", vki_mount=mount, vki_tier=tier,
                  vki_use=[[round(a, 3) for a in u] for u in (use or [])])
    if back is not None:
        k.meta["vki_back_y"] = back
    k.meta.update(kw)


# ---------------------------------------------------------------- pottery and food (shared)
def vki_home_seg(r):
    """segments for a round item of radius r: 16 (§5) from r 0.12, 12 below (small pottery / food)"""
    return VKI_HOME_SEG if r >= 0.12 else VKI_HOME_SEG_S


def vki_home_jug(k, x, y, z, h=0.24, seed=0, segs=None, mi=CLAY, rz=0.0, hseg=6):
    """clay jug standing on z: bellied body, neck, flared lip with a pouring spout (-Y), strap handle (+Y); rz turns
    the whole jug about its axis"""
    before = set(k.bm.verts)
    r = h * 0.36
    segs = segs or vki_home_seg(r)
    prof = [(0.0, 0.0), (r * 0.72, 0.0), (r, h * 0.30), (r * 0.80, h * 0.60), (r * 0.50, h * 0.80),
            (r * 0.62, h), (r * 0.50, h * 0.99), (0.0, h * 0.96)]
    vs, fs = vki_home_lathe(k, prof, c=(x, y, z - 0.004), segs=segs, mi=mi, a0=math.pi / 2)
    for v in vs:
        if v.co.z > z + h * 0.9 and (v.co - Vector((x, y, v.co.z))).dot(Vector((0, -1, 0))) > r * 0.45:
            v.co.y -= 0.018 * (h / 0.24)                        # spout toward -Y
    rnd = random.Random(seed)
    s = h / 0.24
    hr = y + r * 0.95
    a = Vector((x, hr - 0.02 * s, z + h * 0.80)); b = Vector((x, hr + 0.045 * s, z + h * 0.64))
    c2 = Vector((x, hr - 0.01 * s, z + h * 0.36))
    # the two handle strokes differ in radius, so their side faces never share a plane at the joint (T5S)
    _tube(k, tuple(a), tuple(b), 0.012 * s, mi, segs=hseg)
    _tube(k, tuple(b), tuple(c2), 0.0105 * s, mi, segs=hseg)
    k.set_dark([v for v in vs if v.co.z > z + h * 0.55], 0.12 + 0.05 * rnd.random())
    if rz:
        bmesh.ops.rotate(k.bm, verts=vki_home_new_verts(k, before), cent=Vector((x, y, z)),
                         matrix=Matrix.Rotation(rz, 3, "Z"))
    return vs


def vki_home_bowl(k, x, y, z, r=0.10, h=0.07, mi=CLAY, segs=None, a0=0.0, fill=None):
    """open bowl on z (rim wall 1.2 cm, inner floor); fill: a goods cell for the contents (a flat mound)"""
    segs = segs or vki_home_seg(r)
    prof = [(0.0, 0.0), (r * 0.55, 0.0), (r, h), (r - 0.012, h), (r * 0.50, h * 0.2), (0.0, h * 0.2)]
    vs, fs = vki_home_lathe(k, prof, c=(x, y, z - 0.003), segs=segs, mi=mi, a0=a0)
    if fill:
        fv, ff = vki_home_lathe(k, [(0.0, h * 0.25), (r * 0.9, h * 0.25), (r * 0.70, h * 0.95), (0.0, h * 1.05)],
                                c=(x, y, z - 0.003), segs=segs, mi=GOODS, a0=a0 + 0.1)
        goods_map(k, ff, fill, plane=((1, 0, 0), (0, 1, 0)))
    return vs


def vki_home_crock(k, x, y, z, r=0.08, h=0.20, lid=False, cloth=False, seed=0, segs=None, mi=CLAY,
                   glaze=True):
    """storage crock on z: shouldered body with a rolled rim, a darker glazed upper half; lid=True: a wooden lid
    with a knob; cloth=True: a cream cloth cover tied with a cord"""
    segs = segs or vki_home_seg(r)
    prof = [(0.0, 0.0), (r * 0.78, 0.0), (r, h * 0.45), (r * 0.84, h * 0.86), (r * 0.74, h * 0.92),
            (r * 0.80, h), (0.0, h * 0.985)]
    rnd = random.Random(seed)
    vs, fs = vki_home_lathe(k, prof, c=(x, y, z - 0.004), segs=segs, mi=mi, a0=rnd.random())
    if glaze:
        k.set_dark([v for v in vs if v.co.z > z + h * 0.5], 0.14 + 0.14 * rnd.random())
    if lid:
        vki_home_cyl(k, x, y, z + h * 0.975, r * 0.84, r * 0.80, 0.022, segs=segs, mi=WOOD)
        vki_home_cyl(k, x, y, z + h * 0.975 + 0.02, 0.018, 0.014, 0.03, segs=6, mi=WOOD)
    if cloth:
        cv, cf = vki_home_lathe(k, [(0.0, h * 0.86), (r * 0.92, h * 0.86), (r * 0.64, h * 1.07), (0.0, h * 1.10)],
                                c=(x, y, z - 0.004), segs=segs, mi=CLOTH_B, a0=0.13)
        for v in cv:
            v.co.x += 0.004 * math.sin(7 * v.co.y / max(r, 1e-3) + seed)
        vki_home_hoop(k, (x, y, z + h * 0.90), r * 0.84, r * 0.97, 0.014, segs=8, mi=HIDE)
    return vs


def vki_home_plate(k, x, y, z, r=0.12, t=0.014, lean=None, mi=CLAY, a0=0.0, segs=None):
    """dished plate: lying on z, or standing on its rim at z leaning back (toward +Y) by `lean` radians with its
    back at y"""
    segs = segs or vki_home_seg(r)
    prof = [(0.0, 0.0), (r, t), (r * 0.64, t * 0.5), (0.0, t * 0.5)]
    if lean is None:
        vs, fs = vki_home_lathe(k, prof, c=(x, y, z - 0.003), segs=segs, mi=mi, a0=a0)
        return vs
    R = Matrix.Rotation(math.pi / 2 - lean, 3, "X")            # face toward -Y (and up), top leaning back (+Y)
    vs, fs = vki_home_lathe(k, prof, c=(0, 0, 0), segs=segs, mi=mi, a0=a0, rot=R)
    lo = min(v.co.z for v in vs)
    ymax = max(v.co.y for v in vs)
    for v in vs:
        v.co += Vector((x, y - ymax, z - 0.004 - lo))
    return vs


def vki_home_loaf(k, x, y, z, rz=0.0, s=1.0, seed=0, sub=2):
    """bread loaf resting on z, long axis along local Y turned rz (goods atlas: pale crumb below, crust on top)"""
    vs = vki_home_ico(k, (0.0, 0.0, 0.0), 1.0, GOODS, scale=(0.085 * s, 0.14 * s, 0.065 * s), sub=sub,
                      jit=0.004, seed=seed)
    vki_home_squash(vs, (0, 0, 0), below=0.55)
    R = Matrix.Rotation(rz, 4, "Z")
    bmesh.ops.transform(k.bm, matrix=R, verts=vs)
    dz = z - 0.004 - min(v.co.z for v in vs)
    for v in vs:
        v.co += Vector((x, y, dz))
    goods_map(k, vs, "bread", ref=R.to_3x3() @ VKI_HOME_Y)
    return vs


def vki_home_ham(k, x, y, z, rz=0.0, s=1.0, hang=False, sub=2):
    """cured ham resting on z (or hanging from z when hang=True: shank up), goods atlas "ham", a pale bone end"""
    vs = vki_home_ico(k, (0.0, 0.0, 0.0), 1.0, GOODS, scale=(0.15 * s, 0.10 * s, 0.085 * s), sub=sub, jit=0.004,
                      seed=9)
    for v in vs:                                                 # pear shape: narrow toward the shank (+X)
        f = 1.0 - 0.45 * max(0.0, v.co.x / (0.15 * s))
        v.co.y *= f; v.co.z *= f
    vki_home_squash(vs, (0, 0, 0), below=0.7)
    bone = _cyl(k, (0.17 * s, 0.0, 0.0), 0.017 * s, 0.015 * s, 0.07 * s, 6, CLOTH_B,
                rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    allv = vs + bone
    R = Matrix.Rotation(rz, 4, "Z") @ (Matrix.Rotation(-math.pi / 2, 4, "Y") if hang else Matrix.Identity(4))
    bmesh.ops.transform(k.bm, matrix=R, verts=allv)
    if hang:
        dz = z - max(v.co.z for v in allv)
    else:
        dz = z - 0.004 - min(v.co.z for v in vs)
    for v in allv:
        v.co += Vector((x, y, dz))
    goods_map(k, vs, "ham", axis=R.to_3x3() @ VKI_HOME_X)
    return vs


def vki_home_wedge(k, x, y, z, a=0.0, s=1.0):
    """a cut cheese wedge standing on z, its point toward angle a (goods atlas cheese)"""
    wv, wf = vki_prism(k, [(0.0, 0.0), (0.085 * s, -0.026 * s), (0.085 * s, 0.026 * s)], z, z + 0.065 * s, GOODS,
                       axis="z", project=False)
    bmesh.ops.transform(k.bm, matrix=Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(a, 4, "Z"), verts=wv)
    goods_map(k, wf, "cheese", plane=((1, 0, 0), (0, 1, 0)))
    return wv


def vki_home_basket(k, x, y, z, r=0.16, h=0.13, fill=None, n=5, seed=0):
    """round basket on z (BURLAP weave, dark rim) with goods heaped on top (apple / cabbage / turnip ...)"""
    prof = [(0.0, 0.0), (r * 0.82, 0.0), (r, h), (r - 0.014, h), (r * 0.80, h * 0.2), (0.0, h * 0.2)]
    vs, fs = vki_home_lathe(k, prof, c=(x, y, z - 0.003), segs=VKI_HOME_SEG, mi=BURLAP, smooth=False, tile=0.6)
    vki_home_hoop(k, (x, y, z + h - 0.005), r - 0.016, r + 0.008, 0.02, segs=VKI_HOME_SEG, mi=WOOD)
    if not fill:
        return vs
    rnd = random.Random(seed)
    size = {"apple": 0.045, "cabbage": 0.095, "turnip": 0.055}.get(fill, 0.05)
    for i in range(n):
        a = 2 * math.pi * i / max(1, n - (1 if n > 4 else 0)) + rnd.uniform(-0.2, 0.2)
        rr = 0.0 if (n > 4 and i == n - 1) else (r - size) * 0.72
        cz = z + h * 0.62 + size * 0.6 + (0.03 if rr == 0.0 else 0.0)
        iv = vki_home_ico(k, (x + math.cos(a) * rr, y + math.sin(a) * rr, cz), size, GOODS,
                          scale=(1.0, 1.0, 0.9 if fill != "cabbage" else 0.85), sub=2 if fill == "cabbage" else 1,
                          jit=size * 0.08, seed=seed * 10 + i)
        goods_map(k, iv, fill)
    return vs


# ---------------------------------------------------------------- tables and forms
def vki_home_table_trestle(k, L):
    """trestle table L x 0.90 x 0.80: a 0.10 top of three pale hewn boards on two A-trestles (legs 0.13 splayed
    5 deg outward and 7 deg front / back, a cleat under the top, a low cross-bar) joined by a stretcher with
    through-tenons and wedges"""
    W = 0.90
    zt = VKI_HOME_TABLE_Z; z0 = zt - VKI_HOME_TOP_T
    hx, hy = L / 2, W / 2
    vki_home_top(k, -hx, hx, -hy, hy, z0, zt, boards=3, bev=VKI_HOME_TOP_BEV, seed=int(L * 10))
    tx, ty = (math.tan(math.radians(a)) for a in VKI_HOME_SPLAY)
    xt = hx - (0.30 if L > 2 else 0.22)                       # trestle line under the top
    lw, yt = VKI_HOME_LEG_W, 0.27
    zl = z0 - 0.045                                            # leg tops buried in the cleat
    zc = (0.20, 0.29)                                          # cross-bar
    zs = (0.25, 0.35)                                          # stretcher
    xm = lambda z: xt + (zl - z) * tx                          # leg centre line x at height z
    for s in (-1, 1):
        vki_home_box(k, s * xt - 0.065, s * xt + 0.065, -0.40, 0.40, z0 - 0.09, z0, WOOD, bev=0.015)
        for sy in (-1, 1):
            vki_home_leg(k, (s * xt, sy * yt), (s * (xt + zl * tx), sy * (yt + zl * ty)), 0.0, zl, lw)
        xc = s * xm((zc[0] + zc[1]) / 2)
        vki_home_box(k, xc - 0.045, xc + 0.045, -0.405, 0.405, zc[0], zc[1], WOOD, bev=0.012)
        xw = s * (xm((zc[0] + zc[1]) / 2) + 0.045 + 0.02)                  # wedge tight against the cross-bar
        vki_home_box(k, xw - 0.018, xw + 0.018, -0.03, 0.03, zs[0] - 0.05, zs[1] + 0.06, WOOD, bev=0.006)
    xs = xm((zc[0] + zc[1]) / 2) + 0.045 + 0.10
    vki_home_box(k, -xs, xs, -0.05, 0.05, zs[0], zs[1], WOOD, bev=0.012)
    vki_home_meta(k, "floor", "furniture", use=[], vki_table_z=zt, vki_top_rect=[-hx, -hy, hx, hy],
                  vki_note="used through its forms: no use points of its own (they would sit between table and form)")


def vki_home_table_trestle_300(k): vki_home_table_trestle(k, 2.70)
def vki_home_table_trestle_150(k): vki_home_table_trestle(k, 1.20)


def vki_home_table_small(k):
    """small table 1.10 x 0.75 x 0.78: a two-board hewn top 0.10 thick, four legs 0.12 splayed 5 / 6 deg, aprons
    under the top, a low H-stretcher"""
    zt = 0.78; z0 = zt - VKI_HOME_TOP_T
    hx, hy = 0.55, 0.375
    vki_home_top(k, -hx, hx, -hy, hy, z0, zt, boards=2, bev=VKI_HOME_TOP_BEV, seed=41)
    tx, ty = math.tan(math.radians(5.0)), math.tan(math.radians(6.0))
    lw, lx, ly = 0.12, 0.40, 0.235
    zl = z0 + 0.03
    for sx in (-1, 1):
        for sy in (-1, 1):
            vki_home_leg(k, (sx * lx, sy * ly), (sx * (lx + zl * tx), sy * (ly + zl * ty)), 0.0, zl, lw)
    # aprons (the side ones stop short of the long ones inside the legs: no shared top faces, T5S)
    for sy in (-1, 1):
        ya, yb = sorted((sy * (ly - 0.02), sy * (ly + 0.02)))
        vki_home_box(k, -lx, lx, ya, yb, z0 - 0.12, z0, WOOD, bev=0.01)
    for sx in (-1, 1):
        xa, xb = sorted((sx * (lx - 0.02), sx * (lx + 0.02)))
        vki_home_box(k, xa, xb, -ly + 0.05, ly - 0.05, z0 - 0.12, z0, WOOD, bev=0.01)
    xs = lx + (zl - 0.155) * tx
    for sx in (-1, 1):
        vki_home_box(k, sx * xs - 0.03, sx * xs + 0.03, -(ly + (zl - 0.155) * ty) - 0.02,
                     ly + (zl - 0.155) * ty + 0.02, 0.12, 0.19, WOOD, bev=0.01)
    vki_home_box(k, -xs, xs, -0.03, 0.03, 0.14, 0.21, WOOD, bev=0.01)
    vki_home_meta(k, "floor", "furniture", use=[], vki_table_z=zt, vki_top_rect=[-hx, -hy, hx, hy],
                  vki_note="table mount height 0.78 (a Candle_Plate or dressing goes at z 0.78)")


def vki_home_form(k, L):
    """form (bench) L x 0.35 x 0.48: a 0.08 hewn seat plank at 0.48 on stake legs 0.11 splayed 7 deg front / back and
    4 deg outward (3 pairs on the 300, 2 on the 150)"""
    D = 0.35
    zt = VKI_HOME_FORM_Z; z0 = zt - VKI_HOME_FORM_T
    hx = L / 2
    vki_home_top(k, -hx, hx, -D / 2, D / 2, z0, zt, boards=1, bev=0.022, seed=int(L * 10) + 3)
    tx, ty = math.tan(math.radians(4.0)), math.tan(math.radians(7.0))
    lw, yt, zl = 0.11, 0.066, z0 + 0.03
    xs = [-(hx - 0.25), hx - 0.25] + ([0.0] if L > 2 else [])
    for x in xs:
        s = (x > 0) - (x < 0)
        for sy in (-1, 1):
            vki_home_leg(k, (x, sy * yt), (x + s * zl * tx, sy * (yt + zl * ty)), 0.0, zl, lw)
    seats = [[round(x, 3), 0.0, zt] for x in ((-0.9, 0.0, 0.9) if L > 2 else (-0.3, 0.3))]
    vki_home_meta(k, "floor", "furniture", use=[], vki_seats=seats, vki_seat_z=zt,
                  vki_note="seats: vki_seats [x, y, z] (sit facing local +Y or -Y, toward the table)")


def vki_home_form_300(k): vki_home_form(k, 2.70)
def vki_home_form_150(k): vki_home_form(k, 1.20)


# ---------------------------------------------------------------- storage
def vki_home_chest(k):
    """boarded chest 1.10 x 0.60 x 0.65, wall_floor: oak corner stiles (feet), painted SHUTTER panels (two boards
    in front), a painted lid with pale worn edges, iron straps over the lid and down the front, corner plates, lock
    plate and hasp, drop handles. The lid (vki_lid_box / vki_lid_rule) hinges about local X at the back."""
    zc = 0.555                                                  # carcass top = lid bottom
    st = 0.09
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.43, sx * 0.52))
        for ya, yb in ((-0.27, -0.27 + st), (0.29 - st, 0.29)):
            vki_home_box(k, xa, xb, ya, yb, 0.0, zc, WOOD, bev=0.015)
    for i, (za, zb) in enumerate(((0.06, 0.31), (0.31, 0.56))):
        vs = vki_home_box(k, -0.435, 0.435, -0.255, -0.215, za, zb, SHUTTER, bev=0.012)
        k.set_dark(vs, 0.06 * i)
    vki_home_box(k, -0.435, 0.435, 0.235, 0.275, 0.06, 0.56, SHUTTER, bev=0.01)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.465, sx * 0.505))
        vki_home_box(k, xa, xb, -0.185, 0.205, 0.06, 0.56, SHUTTER, bev=0.01)
    # lid: pale hewn top (a teal top sat at the floors' luma, §4.3 prop-top rule), painted sides
    vki_home_slab(k, -0.55, 0.55, -0.285, 0.30, zc, 0.635, bev=0.022, top=HEWN, side=SHUTTER, edge=HEWN, seed=5)
    for x in (-0.33, 0.33):
        vki_home_box(k, x - 0.028, x + 0.028, -0.297, 0.29, 0.635, 0.645, IRON, bev=0.0)          # over the lid
        vki_home_box(k, x - 0.024, x + 0.024, -0.295, -0.285, 0.545, 0.638, IRON, bev=0.0)        # lid front
        vki_home_box(k, x - 0.024, x + 0.024, -0.267, -0.255, 0.08, 0.52, IRON, bev=0.0)          # front band
        for yb in (0.15, 0.24):                                                                    # strap hinges
            vki_home_box(k, x - 0.032, x + 0.032, yb - 0.022, yb + 0.022, 0.643, 0.652, IRON, bev=0.0)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.435, sx * 0.515))
        for za, zb in ((0.42, 0.51), (0.07, 0.16)):                                               # corner plates
            vki_home_box(k, xa, xb, -0.278, -0.27, za, zb, IRON, bev=0.0)
    vki_home_box(k, -0.065, 0.065, -0.265, -0.255, 0.36, 0.50, IRON, bev=0.0)                     # lock plate
    vki_home_box(k, -0.03, 0.03, -0.28, -0.268, 0.47, 0.60, IRON, bev=0.0)                        # hasp (lid)
    for sx in (-1, 1):                                                                             # drop handles
        vki_home_box(k, sx * 0.505 + (0.0 if sx > 0 else -0.01), sx * 0.505 + (0.01 if sx > 0 else 0.0),
                     -0.05, 0.05, 0.42, 0.49, IRON, bev=0.0)
        vki_home_hoop(k, (sx * 0.52, 0.0, 0.40), 0.038, 0.052, 0.014, segs=10, mi=IRON,
                      rot=Matrix.Rotation(math.pi / 2, 3, "Y") @ Matrix.Rotation(math.radians(8 * sx), 3, "Z"))
    vki_home_meta(k, "wall_floor", "furniture", back=0.30, use=[[0.0, -0.75, 0]],
                  hinge_axis="local X", vki_lid_hinge=[0.0, 0.29, zc], vki_lid_open_deg=100,
                  vki_lid_open_dir="rotation -deg about local X through vki_lid_hinge (the front lifts)",
                  vki_lid_box=[-0.56, -0.31, 0.52, 0.56, 0.31, 0.66],
                  vki_lid_rule="the lid = every loose part whose bbox centre lies inside vki_lid_box")


def vki_home_dresser(k):
    """dresser 1.20 x 0.50 x 1.90, wall_floor: a cupboard with two painted doors (SHUTTER) on a plinth, a hewn
    worktop at 0.92 with clay jugs and bowls, an open plate rack above (two hewn shelves with plate rails, clay and
    pewter plates leaning on the dark back boards) under a hewn cornice"""
    X, Y = 0.60, 0.25
    for s in (-1, 1):
        xa, xb = sorted((s * X, s * (X - 0.045)))
        vki_home_box(k, xa, xb, -Y, Y, 0.0, 0.86, WOOD, bev=0.012)                              # cupboard sides
        vki_home_box(k, xa, xb, 0.0, Y, 0.92, 1.84, WOOD, bev=0.012)                            # rack sides
    bk = vki_home_box(k, -0.555, 0.555, 0.225, 0.247, 0.02, 1.84, WOOD, bev=0.0)                # back boards
    k.set_dark(bk, 0.25)
    vki_home_box(k, -0.555, 0.555, -0.245, -0.215, 0.0, 0.08, WOOD, bev=0.008)                  # plinth
    for s in (-1, 1):                                                                            # doors
        xa, xb = sorted((s * 0.005, s * 0.55))
        vki_home_box(k, xa, xb, -0.24, -0.21, 0.09, 0.84, SHUTTER, bev=0.01)
        for zz in (0.20, 0.70):                                                                  # hinges
            ha, hb = sorted((s * 0.40, s * 0.545))
            vki_home_box(k, ha, hb, -0.249, -0.24, zz - 0.02, zz + 0.02, IRON, bev=0.0)
        pa, pb = sorted((s * 0.035, s * 0.06))
        vki_home_box(k, pa, pb, -0.2495, -0.24, 0.50, 0.58, IRON, bev=0.0)                       # pull
    vki_home_top(k, -X, X, -Y, Y, 0.86, 0.92, boards=2, bev=0.018, seed=51)
    for i, zs in enumerate((1.30, 1.62)):
        vki_home_top(k, -0.56, 0.56, 0.0, 0.222, zs - 0.03, zs, boards=1, bev=0.012, seed=52 + i)
        vki_home_box(k, -0.556, 0.556, 0.115, 0.13, zs + 0.03, zs + 0.05, WOOD, bev=0.0)          # plate rail
    vki_home_top(k, -X, X, -0.02, Y, 1.84, 1.90, boards=1, bev=0.018, seed=55)
    for i, (x, r) in enumerate(((-0.34, 0.11), (-0.02, 0.11), (0.30, 0.11))):
        vki_home_plate(k, x, 0.215, 1.30, r=r, lean=math.radians(12), mi=STEEL if i == 1 else CLAY, a0=0.3 * i)
    for i, (x, r) in enumerate(((-0.33, 0.10), (-0.05, 0.10))):
        vki_home_plate(k, x, 0.215, 1.62, r=r, lean=math.radians(12), mi=CLAY if i == 1 else STEEL, a0=0.2 * i)
    vki_home_bowl(k, 0.30, 0.10, 1.62, r=0.09, h=0.06, mi=CLAY)
    vki_home_jug(k, -0.36, 0.02, 0.92, h=0.26, seed=7)
    vki_home_jug(k, 0.36, 0.06, 0.92, h=0.20, seed=8, rz=0.5)
    vki_home_bowl(k, -0.02, -0.02, 0.92, r=0.11, h=0.07, mi=CLAY)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.70, 0]],
                  vki_note="tall (1.90): against a Full wall (R-occ2)")


def vki_home_shelf_wall(k):
    """wall shelf 1.20 x 0.30, wall_hung: two shaped oak end boards against the wall (x +-0.45, clear of the Timber
    studs at 0 / +-0.75) carrying hewn boards with tops at 1.30 and 1.70 (their backs 3.5 cm off the wall face,
    clear of the proud studs); a jug, bowls and a lidded crock below, plates leaning on the wall, a covered crock
    and herb bunches above. Authored at its real height (z 1.20 .. ~1.93)."""
    for s in (-1, 1):
        x = s * 0.45
        vki_prism(k, [(0.15, 1.20), (0.15, 1.76), (-0.125, 1.76), (-0.125, 1.30), (-0.02, 1.20)],
                  x - 0.02, x + 0.02, WOOD, axis="x", bevel=0.008)
    for zt, sd in ((1.30, 11), (1.70, 12)):
        vki_home_top(k, -0.60, 0.60, -0.15, 0.115, zt - 0.04, zt, boards=1, bev=0.015, seed=sd)
    vki_home_jug(k, -0.26, -0.02, 1.30, h=0.24, seed=1)
    vki_home_bowl(k, 0.10, -0.03, 1.30, r=0.10, h=0.07, mi=CLAY)
    vki_home_bowl(k, 0.10, -0.03, 1.365, r=0.085, h=0.06, mi=CLAY, a0=0.3)
    vki_home_crock(k, 0.33, 0.0, 1.30, r=0.075, h=0.17, lid=True, seed=3)
    for i, (x, yb) in enumerate(((-0.32, 0.085), (-0.20, 0.068), (-0.08, 0.051))):
        vki_home_plate(k, x, yb, 1.70, r=0.12 - 0.008 * i, lean=math.radians(14), mi=STEEL if i == 1 else CLAY,
                       a0=0.2 * i)
    vki_home_crock(k, 0.28, 0.0, 1.70, r=0.08, h=0.20, lid=False, cloth=True, seed=4)
    for x in (0.06, 0.14):                                     # herb bunches hanging from the upper board
        hv = vki_home_ico(k, (x, -0.11, 1.555), 0.05, GOODS, scale=(0.8, 0.7, 1.5), sub=1, jit=0.008,
                          seed=int(x * 100))
        goods_map(k, hv, "herbs")
        vki_home_box(k, x - 0.004, x + 0.004, -0.114, -0.106, 1.605, 1.665, HIDE, bev=0.0)
    vki_home_meta(k, "wall_hung", "furniture", back=0.15, use=[[0.0, -0.60, 0]], vki_mount_zmin=1.2,
                  vki_mount_zmax=round(max(v.co.z for v in k.bm.verts), 3),
                  vki_note="authored at its real height (boards at 1.30 / 1.70); back on the wall face; place at z 0")


def vki_home_pantry(k):
    """pantry shelving 2.70 x 0.50 x 1.90, wall_floor: three oak uprights, two bays, hewn shelves at 0.12 / 0.62 /
    1.10 / 1.55, dark board backs, a hewn top board; stocked from the goods atlas (cheese, bread, ham, sausages,
    apples, cabbages, carrots, turnips, herbs), clay crocks and grain sacks"""
    X, Y, H = 1.35, 0.25, 1.90
    zt = 1.855                                                   # upright tops = top board bottom
    for a, b in ((-X, -X + 0.05), (-0.025, 0.025), (X - 0.05, X)):
        vki_home_box(k, a, b, -Y, Y, 0.0, zt, WOOD, bev=0.012)
    bays = ((-X + 0.05, -0.025), (0.025, X - 0.05))
    for i, (a, b) in enumerate(bays):
        vki_home_box(k, a, b, -0.235, -0.205, 0.0, 0.08, WOOD, bev=0.008)                       # plinth
        bk = vki_home_box(k, a, b, 0.225, 0.247, 0.12, zt, WOOD, bev=0.0)                         # back boards
        k.set_dark(bk, 0.22)
        for j, top in enumerate((0.12, 0.62, 1.10, 1.55)):
            vki_home_top(k, a - 0.005, b + 0.005, -0.245, 0.22, top - 0.04, top, boards=1, bev=0.012,
                         seed=20 + 4 * i + j)
    vki_home_top(k, -X, X, -Y, Y, zt, H, boards=2, bev=0.018, seed=31)
    rnd = random.Random(4242)
    # --- floor shelf (0.12): sacks, a basket of turnips, a big lidded crock, a basket of cabbages, a covered crock
    vki_home_sack(k, -1.02, 0.02, 0.12, s=0.92, seed=1)
    vki_home_sack(k, -0.62, -0.02, 0.12, s=0.86, seed=2)
    vki_home_basket(k, -0.24, -0.01, 0.12, r=0.15, h=0.14, fill="turnip", n=5, seed=3)
    vki_home_crock(k, 0.30, 0.0, 0.12, r=0.16, h=0.40, lid=True, seed=4)
    vki_home_basket(k, 0.78, -0.01, 0.12, r=0.19, h=0.15, fill="cabbage", n=3, seed=5)
    vki_home_crock(k, 1.12, 0.02, 0.12, r=0.11, h=0.28, cloth=True, seed=6)
    # --- shelf 1 (0.62): cheese wheels, bread; apples, covered and lidded crocks
    for n_ in range(3):
        goods_map(k, vki_home_cyl(k, -1.10 + 0.01 * n_, -0.02, 0.617 + 0.101 * n_, 0.15 - 0.012 * n_,
                                  0.15 - 0.012 * n_, 0.10, segs=VKI_HOME_SEG, mi=GOODS), "cheese", caps=True)
    for x, y, rz, s in ((-0.74, -0.06, 0.25, 1.0), (-0.45, -0.07, -0.3, 1.0), (-0.60, 0.12, 1.4, 0.85)):
        vki_home_loaf(k, x, y, 0.62, rz=rz, s=s, seed=int(x * 100))
    vki_home_basket(k, 0.30, -0.01, 0.62, r=0.16, h=0.12, fill="apple", n=7, seed=7)
    vki_home_crock(k, 0.72, 0.02, 0.62, r=0.10, h=0.24, cloth=True, seed=8)
    vki_home_crock(k, 1.06, 0.0, 0.62, r=0.12, h=0.30, lid=True, seed=9)
    # --- shelf 2 (1.10): jars, carrots; loaves and a cheese
    for n_, x in enumerate((-1.14, -0.94, -0.74)):
        vki_home_crock(k, x, 0.02, 1.10, r=0.075 + 0.01 * (n_ % 2), h=0.18 + 0.03 * n_, lid=(n_ == 1), seed=10 + n_)
    for n_ in range(5):                                          # carrots, crowns (thick ends) toward -Y
        cx = -0.45 + n_ * 0.055 + rnd.uniform(-0.01, 0.01); a = rnd.uniform(-0.2, 0.2)
        R = Matrix.Rotation(math.pi / 2 + a, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y")
        cc = Vector((cx, -0.02, 1.10 + 0.028 + 0.01 * (n_ % 2)))
        cv = _cyl(k, tuple(cc), 0.028, 0.004, 0.22, 6, PUMPKIN, rot=R)
        goods_map(k, cv, "carrot", axis=-(R.to_3x3() @ VKI_HOME_Z), c=tuple(cc))
        lv = vki_home_ico(k, tuple(cc + R.to_3x3() @ Vector((0.0, 0.0, -0.13))), 0.03, GOODS, scale=(1.0, 1.0, 0.7),
                          sub=1, smooth=False, seed=70 + n_)
        goods_map(k, lv, "herbs")
    vki_home_loaf(k, 0.30, 0.0, 1.10, rz=0.1, s=1.0, seed=12)
    vki_home_loaf(k, 0.62, -0.03, 1.10, rz=-0.2, s=0.9, seed=13)
    goods_map(k, vki_home_cyl(k, 1.02, 0.0, 1.097, 0.14, 0.14, 0.11, segs=VKI_HOME_SEG, mi=GOODS), "cheese",
              caps=True)
    # --- shelf 3 (1.55): a ham, small jars; bowls of goods, turnips
    vki_home_ham(k, -1.0, 0.0, 1.55, rz=0.2, s=1.0)
    for n_, x in enumerate((-0.55, -0.36)):
        vki_home_crock(k, x, 0.03, 1.55, r=0.065, h=0.15, lid=(n_ == 0), seed=20 + n_)
    for n_, x in enumerate((0.25, 0.47, 0.69)):
        vki_home_bowl(k, x, 0.0, 1.55, r=0.095, h=0.08, mi=CLAY, a0=0.2 * n_, fill=("apple", "pomace", "herbs")[n_])
    for n_ in range(4):
        tv = vki_home_ico(k, (0.98 + 0.11 * (n_ % 2) + rnd.uniform(-0.01, 0.01), -0.05 + 0.1 * (n_ // 2), 0.0),
                          0.06, GOODS, scale=(1.0, 1.0, 0.9), sub=1, jit=0.006, seed=40 + n_, rest=1.55)
        goods_map(k, tv, "turnip")
    # --- hanging from the top board: sausages on a cord, herb bunches
    for n_, hz in enumerate((0.085, 0.095, 0.08)):
        sv = vki_home_ico(k, (-0.80 + 0.075 * n_, -0.215, 1.785 - hz), 1.0, GOODS, scale=(0.034, 0.034, hz),
                          sub=1, seed=50 + n_)
        goods_map(k, sv, "sausage")
    vki_home_box(k, -0.84, -0.61, -0.219, -0.211, 1.78, 1.79, HIDE, bev=0.0)
    for x in (-0.835, -0.615):
        vki_home_box(k, x - 0.004, x + 0.004, -0.2195, -0.2105, 1.785, 1.86, HIDE, bev=0.0)
    for x in (-0.12, 0.10):
        hv = vki_home_ico(k, (x, -0.195, 1.73), 0.055, GOODS, scale=(0.8, 0.7, 1.4), sub=1, jit=0.01, seed=int(x * 90))
        goods_map(k, hv, "herbs")
        vki_home_box(k, x - 0.004, x + 0.004, -0.199, -0.191, 1.795, 1.856, HIDE, bev=0.0)
    vki_home_meta(k, "wall_floor", "hero", back=Y, use=[[-0.70, -0.70, 0], [0.70, -0.70, 0]],
                  vki_note="tall (1.90): against a Full wall (R-occ2)")


def vki_home_barrel(k, x=0.0, y=0.0, r=0.40, h=1.0, open_top=False, water_z=0.90, hoops=(0.10, 0.28, 0.72, 0.90)):
    """a stave barrel standing on the floor: bellied oak staves (16, flat-shaded, grain up), iron hoops, a pale
    hewn chime ring on top; closed: a boarded head 3 cm down, open: an inner wall down to water_z - 0.04"""
    re, t = r * 0.84, 0.035
    outer = [(re, 0.0), (r * 0.965, h * 0.25), (r, h * 0.5), (r * 0.965, h * 0.75), (re, h)]
    if open_top:
        prof = [(0.0, 0.0)] + outer + [(re - t, h), (re - t - 0.004, water_z - 0.04), (0.0, water_z - 0.04)]
    else:
        prof = [(0.0, 0.0)] + outer + [(re - t, h), (re - t, h - 0.03), (0.0, h - 0.03)]
    vs, fs = vki_home_lathe(k, prof, c=(x, y, 0.0), segs=VKI_HOME_SEG, mi=WOOD, smooth=False, uv="cylv", tile=1.2)
    k.bm.normal_update()
    for f in fs:
        if f.normal.z > 0.9:
            cz = f.calc_center_median().z
            if cz > h - 0.004:
                vki_home_uv(k, [f], HEWN, VKI_HOME_X, VKI_HOME_Y, vki_tile(HEWN), vki_hash_off((x, y, h)))
            elif not open_top and cz > h - 0.035:                    # head: pale boards, a shade under the ring
                vki_home_uv(k, [f], HEWN, VKI_HOME_X, VKI_HOME_Y, vki_tile(HEWN), vki_hash_off((x, y, h - 0.03)))
                k.set_dark(list(f.verts), 0.14)
        elif f.normal.z < -0.9:
            k.set_dark(list(f.verts), 0.1)

    def rad(z):
        for (r0, z0), (r1, z1) in zip(outer[:-1], outer[1:]):
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                return r0 + (r1 - r0) * (z - z0) / max(z1 - z0, 1e-9)
        return outer[-1][0]
    for zf in hoops:
        z = zf * h
        lo = min(rad(z - 0.0225), rad(z + 0.0225)); hi = max(rad(z - 0.0225), rad(z + 0.0225))
        vki_home_hoop(k, (x, y, z), lo - 0.012, hi + 0.011, 0.045, segs=VKI_HOME_SEG, mi=IRON)
    k.set_dark([v for v in vs if v.co.z < 0.12], 0.06)
    return vs, re - t


def vki_home_barrel_prop(k):
    """barrel r 0.40 x 1.00, floor: bellied staves, four iron hoops, a boarded head with a batten, pale chime ring"""
    vki_home_barrel(k)
    vki_home_box(k, -0.24, 0.24, -0.028, 0.028, 0.968, 0.99, WOOD, bev=0.006)                    # head batten
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.75, 0]])


def vki_home_barrel_water(k):
    """water barrel r 0.40 x 1.00, floor: an open barrel with its water 10 cm below the rim (WATER top; style
    water=WaterMurky for a darker butt), wet dark inner staves, a wooden dipper leaning on the rim"""
    vs, ri = vki_home_barrel(k, open_top=True, water_z=0.90)
    k.set_dark([v for v in vs if v.co.z > 0.85 and (v.co.x ** 2 + v.co.y ** 2) ** 0.5 < ri + 0.002], 0.35)
    vki_home_cyl(k, 0.0, 0.0, 0.88, ri + 0.006, ri + 0.006, 0.02, segs=VKI_HOME_SEG, mi=WATER)
    # dipper: a small bowl afloat by the rim, its handle over the rim
    vki_home_bowl(k, 0.10, -0.08, 0.885, r=0.06, h=0.05, mi=WOOD, segs=10)
    _tube(k, (0.15, -0.10, 0.93), (0.29, -0.20, 1.10), 0.013, WOOD, segs=6)
    # coordinator 2026-09-26: still water, not the exterior M_VK_Water, whose rippled normal map glittered white
    # under the interior lights
    k.slot_mats = {WATER: "WaterMurky"}
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.75, 0]], vki_water_z=0.90)


def vki_home_crate(k):
    """crate 0.75 x 0.75 x 0.75, floor: a body of scrubbed horizontal boards, oak corner battens, wrap-round
    bands top and bottom, a diagonal brace on the front, a lid of three pale hewn boards"""
    body = vki_home_box(k, -0.345, 0.345, -0.345, 0.345, 0.004, 0.715, PLANKS, bev=0.0)
    k.bm.normal_update()
    for f in vki_faces_of(body):
        n = f.normal
        if abs(n.x) > 0.7:
            vki_home_uv(k, [f], PLANKS, VKI_HOME_Z, VKI_HOME_Y, 8 * 0.71 / 4, (0.25, 0.3))
        elif abs(n.y) > 0.7:
            vki_home_uv(k, [f], PLANKS, VKI_HOME_Z, VKI_HOME_X, 8 * 0.71 / 4, (0.5, 0.7))
    vki_home_top(k, -0.355, 0.355, -0.355, 0.355, 0.715, 0.745, boards=3, bev=0.01, seed=61)
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * 0.335, sx * 0.375)); ya, yb = sorted((sy * 0.335, sy * 0.375))
            vki_home_box(k, xa, xb, ya, yb, 0.0, 0.735, WOOD, bev=0.008)       # top inside the lid edge (T5S)
    for za, zb in ((0.03, 0.105), (0.63, 0.705)):
        vki_home_box(k, -0.365, 0.365, -0.365, 0.365, za, zb, WOOD, bev=0.008)
    a = math.atan2(0.54, 0.60)
    vki_home_box(k, -0.40, 0.40, -0.369, -0.345, 0.335, 0.405, WOOD, bev=0.006, rot=(0, -a, 0))
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.75, 0]])


def vki_home_jars(k):
    """jar cluster 0.90 x 0.60 x 0.70, wall_floor: a tall storage jar with a wooden lid, a cloth-covered crock, a
    lidded pot and a small jug (clay, darker glazed shoulders)"""
    prof = [(0.0, 0.0), (0.12, 0.0), (0.20, 0.14), (0.225, 0.32), (0.20, 0.50), (0.12, 0.60), (0.10, 0.63),
            (0.125, 0.655), (0.115, 0.675), (0.0, 0.66)]
    vs, fs = vki_home_lathe(k, prof, c=(-0.19, 0.075, -0.004), segs=VKI_HOME_SEG, mi=CLAY, a0=0.2)
    k.set_dark([v for v in vs if v.co.z > 0.36], 0.22)
    vki_home_cyl(k, -0.19, 0.075, 0.652, 0.118, 0.112, 0.026, segs=VKI_HOME_SEG, mi=WOOD)
    vki_home_cyl(k, -0.19, 0.075, 0.676, 0.022, 0.016, 0.024, segs=6, mi=WOOD)
    vki_home_crock(k, 0.20, 0.12, 0.0, r=0.17, h=0.44, cloth=True, seed=33)
    vki_home_crock(k, 0.31, -0.17, 0.0, r=0.105, h=0.26, lid=True, seed=34)
    vki_home_jug(k, 0.0, -0.19, 0.0, h=0.22, seed=35, rz=math.pi / 2)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.70, 0]])


# ---------------------------------------------------------------- firewood
def vki_home_logbasket(k):
    """oval log basket 0.80 x 0.60 x 0.60, floor: woven body (BURLAP weave at a coarse tile), a dark oak rim, two
    end handles; round logs (bark, one painted log end each) and two split billets heaped above the rim"""
    sy = 0.75
    prof = [(0.0, 0.0), (0.33, 0.0), (0.365, 0.12), (0.39, 0.30), (0.395, 0.36), (0.368, 0.36), (0.356, 0.30),
            (0.33, 0.12), (0.30, 0.06), (0.0, 0.06)]
    vki_home_lathe(k, prof, segs=VKI_HOME_SEG, mi=BURLAP, smooth=False, sy=sy, tile=1.6)
    vki_home_hoop(k, (0.0, 0.0, 0.365), 0.36, 0.40, 0.05, segs=VKI_HOME_SEG, mi=WOOD, sy=sy)
    for s in (-1, 1):                                            # end handles: loops across the ends above the rim
        vki_home_hoop(k, (s * 0.372, 0.0, 0.42), 0.045, 0.062, 0.028, segs=10, mi=WOOD,
                      rot=Matrix.Rotation(math.pi / 2, 3, "Y"))
    rnd = random.Random(611)
    logs = [(-0.02, -0.12, 0.17, 0.070, 0.66, 0.05, 0.0), (0.03, 0.02, 0.17, 0.075, 0.64, -0.04, 0.0),
            (0.0, 0.14, 0.17, 0.066, 0.62, 0.02, 0.0),
            (-0.03, -0.07, 0.30, 0.068, 0.70, 0.12, 0.04), (0.02, 0.08, 0.30, 0.072, 0.68, -0.10, -0.03),
            (0.0, -0.13, 0.42, 0.062, 0.72, -0.06, 0.10), (0.01, 0.00, 0.44, 0.070, 0.74, 0.08, -0.06),
            (0.0, 0.12, 0.41, 0.058, 0.70, 0.18, 0.05)]
    for (x, y, z, r, ln, rz, ry) in logs:
        vki_home_log(k, (x, y, z), r, ln, rz=rz, ry=ry, segs=10, dark=0.05 + 0.1 * rnd.random())
    for (x, y, z, rz, ry) in ((-0.03, -0.06, 0.52, 0.10, 0.06), (0.04, 0.07, 0.515, -0.12, -0.05)):
        vki_home_billet(k, (x, y, z), 0.072, 0.62, rz=rz, ry=ry, split=WOOD, dark=0.12)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.70, 0]])


# ---------------------------------------------------------------- beds
def vki_home_bed_straw(k):
    """straw bed 0.90 x 2.00 x 0.45, floor, long along Y with its head at +Y: a low oak frame (posts, rails, head and
    foot boards), a lumpy straw mattress (STRAW), a wool blanket (textile blanket_wool) over the lower part, a
    linen bolster"""
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.36, sx * 0.45))
        for (ya, yb), zt in (((0.91, 1.00), 0.45), ((-1.00, -0.91), 0.30)):
            vki_home_box(k, xa, xb, ya, yb, 0.0, zt, WOOD, bev=0.014)
        ra, rb = sorted((sx * 0.375, sx * 0.435))
        vki_home_box(k, ra, rb, -0.915, 0.915, 0.10, 0.22, WOOD, bev=0.012)
    vki_home_slab(k, -0.365, 0.365, 0.925, 0.965, 0.20, 0.44, bev=0.012, top=WOOD, side=WOOD, edge=HEWN, seed=81)
    vki_home_slab(k, -0.365, 0.365, -0.965, -0.925, 0.10, 0.28, bev=0.012, top=WOOD, side=WOOD, edge=HEWN, seed=82)
    mv = vki_home_box(k, -0.37, 0.37, -0.90, 0.905, 0.12, 0.36, VKI_STRAW, bev=0.06, segs=2)
    rnd = random.Random(84)
    for v in mv:
        if v.co.z > 0.32:
            v.co.z += rnd.uniform(-0.008, 0.008)
    k.project(vki_faces_of(mv), VKI_STRAW)
    vki_home_cover(k, -0.405, 0.405, -0.93, 0.36, 0.20, 0.39, "blanket_wool", along="y", bev=0.035, seed=85)
    pv = vki_home_ico(k, (0.0, 0.70, 0.0), 1.0, CLOTH_B, scale=(0.30, 0.13, 0.075), sub=2, jit=0.003, seed=86,
                      rest=0.36)
    k.project(vki_faces_of(pv), CLOTH_B)
    vki_home_meta(k, "floor", "furniture", use=[[0.85, 0.0, 270], [-0.85, 0.0, 90]],
                  vki_lie=[0.0, 0.05, 0.39, 0], vki_textile="blanket_wool",
                  vki_note="head at +Y; use points on both long sides (keep the reachable one)")


def vki_home_bed_box(k):
    """box bed (lit clos) 2.40 x 1.20 x 1.80, wall_floor, bed along X with its head at +X: oak corner posts, scrubbed
    vertical-board end and back panels, an oak front (bed board with a pale worn top edge, stiles, fascia) round the
    opening x -0.90..0.90, z 0.60..1.50 (-Y), an oak roof with a raised panel and pale hewn chamfers; inside a straw
    mattress, the patchwork quilt (textile quilt_patch) and two pillows, red curtains gathered at the sides"""
    X, Y, H, zr, pw = 1.20, 0.60, 1.80, 1.72, 0.10
    for sx in (-1, 1):
        xa, xb = sorted((sx * X, sx * (X - pw)))
        for ya, yb in ((-Y, -Y + pw), (Y - pw, Y)):
            vki_home_box(k, xa, xb, ya, yb, 0.0, zr, WOOD, bev=0.015)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 1.13, sx * 1.165))
        fs = vki_faces_of(vki_home_box(k, xa, xb, -0.505, 0.505, 0.02, zr, PLANKS, bev=0.006))
        vki_home_boards_v(k, [f for f in fs if abs(f.normal.x) > 0.7], across=VKI_HOME_Y, n=4, width=1.01, seed=3 + sx)
    fs = vki_faces_of(vki_home_box(k, -1.105, 1.105, 0.535, 0.565, 0.02, zr, PLANKS, bev=0.006))
    vki_home_boards_v(k, [f for f in fs if abs(f.normal.y) > 0.7], across=VKI_HOME_X, n=8, width=2.21, seed=5)
    # front: bed board (pale worn top edge), stiles, fascia -- butting, faces in one plane only along edges
    vki_home_slab(k, -1.10, 1.10, -0.57, -0.53, 0.02, 0.60, bev=0.012, top=WOOD, side=WOOD, edge=HEWN, seed=6)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.90, sx * 1.10))
        vki_home_box(k, xa, xb, -0.57, -0.53, 0.60, 1.50, WOOD, bev=0.012)
    vki_home_box(k, -1.10, 1.10, -0.57, -0.53, 1.50, zr, WOOD, bev=0.012)
    vki_home_slab(k, -X, X, -Y, Y, zr, 1.78, bev=0.022, top=HEWN, side=WOOD, edge=HEWN, seed=7)
    pn = vki_home_slab(k, -1.06, 1.06, -0.46, 0.46, 1.775, H, bev=0.018, top=HEWN, side=WOOD, edge=HEWN, seed=8)
    k.set_dark(list({v for f in pn for v in f.verts}), 0.12)                                  # panel a shade darker
    # bedding
    mv = vki_home_box(k, -1.08, 1.08, -0.50, 0.52, 0.40, 0.64, VKI_STRAW, bev=0.05, segs=2)
    rnd = random.Random(88)
    for v in mv:
        if v.co.z > 0.6:
            v.co.z += rnd.uniform(-0.008, 0.008)
    k.project(vki_faces_of(mv), VKI_STRAW)
    vki_home_cover(k, -1.09, 0.42, -0.515, 0.525, 0.55, 0.68, "quilt_patch", along="x", seed=89)
    for i, yy in enumerate((-0.20, 0.20)):
        pv = vki_home_ico(k, (0.62, yy, 0.0), 1.0, CLOTH_B, scale=(0.17, 0.24, 0.085), sub=2, jit=0.004,
                          seed=60 + i, rest=0.64 + 0.005 * i)
        k.project(vki_faces_of(pv), CLOTH_B)
    # curtains gathered at both sides of the opening, mostly behind the stiles (pleats: thin boards turned
    # +-32 deg with stepped ends, so no two share a face plane)
    for sx in (-1, 1):
        for i in range(5):
            x = sx * (0.95 - 0.045 * i)
            a = math.radians(32 if i % 2 else -32) * sx
            z0, z1 = 0.62 + 0.006 * i, 1.49 - 0.006 * i
            k.box((x, -0.505, (z0 + z1) / 2), (0.065, 0.022, z1 - z0), CLOTH_A, rot=(0, 0, a), bevel=0.0)
    vki_home_meta(k, "wall_floor", "furniture", back=Y, use=[[0.0, -1.05, 0]],
                  vki_lie=[0.0, 0.0, 0.68, 90], vki_textile="quilt_patch",
                  vki_note="bed along X, head at +X; the quilt shows through the -Y opening (x -0.90..0.90, z 0.60..1.50)")


def vki_home_bed_halftester(k):
    """half-tester bed 1.70 x 2.30 x 2.20, wall_floor, long along Y with its head at +Y (the wall): tall oak head
    posts carrying a tester 0.9 deep over the head only (oak rails and a boarded top, all pale hewn, a red pleated
    valance, gathered red side curtains), a headboard under a red back cloth, low foot posts with turned knobs,
    rails and a foot board; a linen mattress, the patchwork quilt (textile quilt_patch) and two pillows"""
    X, Y = 0.85, 1.15
    zt = 2.20
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.75, sx * X))
        vki_home_box(k, xa, xb, 1.05, Y, 0.0, zt, WOOD, bev=0.018)                              # head posts
        fa, fb = sorted((sx * 0.76, sx * X))
        vki_home_box(k, fa, fb, -Y, -1.06, 0.0, 0.70, WOOD, bev=0.016)                          # foot posts
        vki_home_lathe(k, [(0.0, 0.0), (0.032, 0.0), (0.044, 0.05), (0.028, 0.10), (0.0, 0.12)],
                       c=(sx * 0.805, -1.105, 0.695), segs=VKI_HOME_SEG_S, mi=WOOD, smooth=True)
        ra, rb = sorted((sx * 0.765, sx * 0.825))
        vki_home_box(k, ra, rb, -1.065, 1.055, 0.20, 0.40, WOOD, bev=0.012)                     # side rails
    vki_home_slab(k, -0.755, 0.755, 1.075, 1.115, 0.30, 1.25, bev=0.014, top=WOOD, side=WOOD, edge=HEWN, seed=91)
    vki_home_slab(k, -0.753, 0.753, 1.07, 1.12, 1.20, 1.30, bev=0.016, top=HEWN, side=WOOD, edge=HEWN, seed=92)
    vki_home_box(k, -0.752, 0.752, 1.082, 1.102, 1.30, 2.10, CLOTH_A, bev=0.0)                  # back cloth
    vki_home_slab(k, -0.765, 0.765, -1.125, -1.085, 0.20, 0.62, bev=0.012, top=WOOD, side=WOOD, edge=HEWN, seed=93)
    # tester: front rail, side rails (butting the front rail and the posts), back rail between the posts, canopy
    vki_home_slab(k, -X, X, 0.25, 0.33, 2.06, zt, bev=0.016, top=HEWN, side=WOOD, edge=HEWN, seed=94)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.77, sx * X))
        vki_home_slab(k, xa, xb, 0.33, 1.05, 2.08, zt, bev=0.014, top=HEWN, side=WOOD, edge=HEWN, along="y",
                      seed=95 + sx)
    vki_home_slab(k, -0.75, 0.75, 1.05, Y, 2.10, zt, bev=0.014, top=HEWN, side=WOOD, edge=HEWN, seed=97)
    vki_home_top(k, -0.772, 0.772, 0.328, 1.052, 2.155, 2.18, boards=2, along="y", bev=0.005, seed=96, tone=0.14)
    # valance: pleats hanging from the front and side rails (alternate +-20 deg, stepped bottoms)
    for i in range(8):                                            # neighbours differ in top and bottom height (T5S)
        x = -0.74 + i * (1.48 / 7)
        z0, z1 = 1.88 + 0.006 * (i % 3), 2.07 - 0.005 * (i % 2)
        k.box((x, 0.235, (z0 + z1) / 2), (0.21, 0.02, z1 - z0), CLOTH_A, rot=(0, 0, math.radians(18 if i % 2 else -18)),
              bevel=0.0)
    for sx in (-1, 1):
        for i in range(4):
            y = 0.42 + i * 0.19
            z0, z1 = 1.89 + 0.006 * (i % 3), 2.09 - 0.005 * (i % 2)
            k.box((sx * 0.81, y, (z0 + z1) / 2), (0.02, 0.19, z1 - z0), CLOTH_A,
                  rot=(0, 0, math.radians(18 if i % 2 else -18)), bevel=0.0)
        for i in range(4):                                                                        # side curtains
            y = 0.70 + i * 0.09
            z0, z1 = 0.64 + 0.006 * i, 2.06 - 0.006 * i
            k.box((sx * 0.80, y, (z0 + z1) / 2), (0.022, 0.085, z1 - z0), CLOTH_A,
                  rot=(0, 0, math.radians(30 if i % 2 else -30)), bevel=0.0)
    # bedding
    mv = vki_home_box(k, -0.755, 0.755, -1.075, 1.065, 0.34, 0.60, CLOTH_B, bev=0.05, segs=2)
    k.project(vki_faces_of(mv), CLOTH_B)
    vki_home_cover(k, -0.795, 0.795, -1.10, 0.45, 0.44, 0.64, "quilt_patch", along="x", seed=98)
    for i, xx in enumerate((-0.36, 0.36)):
        pv = vki_home_ico(k, (xx, 0.78, 0.0), 1.0, CLOTH_B, scale=(0.30, 0.19, 0.09), sub=2, jit=0.004, seed=99 + i,
                          rest=0.60 + 0.004 * i)
        k.project(vki_faces_of(pv), CLOTH_B)
    vki_home_meta(k, "wall_floor", "furniture", back=Y, use=[[1.30, -0.30, 270], [-1.30, -0.30, 90]],
                  vki_lie=[0.0, 0.0, 0.64, 0], vki_textile="quilt_patch",
                  vki_note="tall (2.20): against a Full north wall (R-occ2); the tester is over the head 0.9 m only")


# ---------------------------------------------------------------- hearth and kitchen
def vki_home_hearth_open(k):
    """open hearth 1.30 x 1.30 x 1.20, floor: a kerb of dressed stones (STONE_BLOCK_IN, flat on the floor, tops a
    little uneven, sooty inside) round an ash bed, glowing embers (vki_heat), four charred logs laid like a star,
    five flame tongues, an iron tripod with a chain and a cauldron of stew (goods pomace)"""
    rnd = random.Random(501)
    sq = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            sq.append((sorted((sx * 0.435, sx * 0.63)), sorted((sy * 0.435, sy * 0.63))))
    for s in (-1, 1):
        for a, b in ((-0.42, -0.008), (0.008, 0.42)):
            sq.append(((a, b), sorted((s * 0.43, s * 0.63))))
            sq.append((sorted((s * 0.43, s * 0.63)), (a, b)))
    for (xa, xb), (ya, yb) in sq:
        h = 0.12 + 0.04 * rnd.random()
        vs = vki_home_box(k, xa, xb, ya, yb, 0.0, h, VKI_STONE_BLOCK_IN, bev=0.03,
                          rot=(0, 0, rnd.uniform(-0.02, 0.02)))
        for v in vs:
            if v.co.z > 0.06:
                v.co.z += rnd.uniform(-0.007, 0.007)
            k.set_dark([v], 0.40 if (abs(v.co.x) < 0.47 and abs(v.co.y) < 0.47) else 0.16 + 0.08 * rnd.random())
    av = vki_home_box(k, -0.46, 0.46, -0.46, 0.46, 0.004, 0.06, VKI_ASH, bev=0.02)
    for v in av:
        k.set_dark([v], 0.35 + 0.35 * (1.0 - vki_clamp((v.co.x ** 2 + v.co.y ** 2) ** 0.5 / 0.46)))
    for i in range(10):                                          # embers: faceted glowing coals
        a = 2 * math.pi * i / 10 + rnd.uniform(-0.3, 0.3); rr = rnd.uniform(0.04, 0.24)
        c = Vector((math.cos(a) * rr, math.sin(a) * rr, 0.075))
        vs = vki_home_ico(k, c, rnd.uniform(0.045, 0.065), GLOW, scale=(1.0, 1.0, 0.6), sub=1, jit=0.006,
                          seed=520 + i, smooth=False)
        for v in vs:
            k.set_heat([v], vki_clamp(1.0 - (v.co - Vector((0.0, 0.0, 0.05))).length / 0.36))
        k.project(vki_faces_of(vs), GLOW)
    for i, a in enumerate((0.35, 1.95, 3.55, 5.05)):              # logs laid like a star, charred
        vki_home_log(k, (math.cos(a) * 0.21, math.sin(a) * 0.21, 0.115), 0.055 - 0.004 * (i % 2), 0.44, rz=a,
                     ry=0.20, segs=10, dark=0.55)
    for (x, y, h, r, tl, sp, bw) in ((0.0, 0.0, 0.46, 0.10, 0.0, 0.1, 0.03), (-0.10, 0.05, 0.34, 0.08, 0.2, -0.3, -0.03),
                                     (0.11, -0.03, 0.36, 0.08, -0.18, 0.3, 0.035), (0.03, 0.10, 0.30, 0.07, -0.05, 0.5, 0.02),
                                     (-0.05, -0.10, 0.26, 0.065, 0.12, -0.2, -0.02)):
        vki_tim_flame(k, (x, y, 0.10), h, r, tl, sp, bw)
    apex = Vector((0.0, 0.08, 1.165))
    for a in (90.0, 210.0, 330.0):                                # tripod feet on the kerb
        ar = math.radians(a)
        _tube(k, (math.cos(ar) * 0.555, math.sin(ar) * 0.555, 0.12), tuple(apex), 0.016, IRON, segs=6)
    vki_home_ico(k, tuple(apex), 0.032, IRON, sub=1, smooth=False)
    _tube(k, tuple(apex), (0.0, 0.08, 0.985), 0.008, IRON, segs=6)
    pv, pf = vki_home_lathe(k, [(0.0, 0.60), (0.10, 0.60), (0.155, 0.64), (0.175, 0.71), (0.165, 0.78), (0.15, 0.80),
                                (0.163, 0.815), (0.148, 0.822), (0.132, 0.80), (0.0, 0.785)], c=(0.0, 0.08, 0.0),
                            segs=VKI_HOME_SEG, mi=IRON, smooth=True)
    k.set_dark([v for v in pv if v.co.z < 0.70], 0.25)
    sv, sf = vki_home_lathe(k, [(0.0, 0.782), (0.136, 0.782), (0.134, 0.798), (0.0, 0.802)], c=(0.0, 0.08, 0.0),
                            segs=VKI_HOME_SEG, mi=GOODS)
    goods_map(k, sf, "pomace", plane=((1, 0, 0), (0, 1, 0)))
    vki_home_hoop(k, (0.0, 0.08, 0.82), 0.160, 0.172, 0.012, segs=12, mi=IRON,
                  rot=Matrix.Rotation(math.pi / 2, 3, "Y"))
    vki_home_meta(k, "floor", "hero", use=[[0.0, -1.05, 0]],
                  vki_lights=[dict(type="POINT", role="hearth", pos=list(VKI_HOME_HEARTH_LIGHT), w=VKI_HOME_HEARTH_W,
                                   color=[1.0, .52, .22], range=6.0, flicker=1, shadows=1,
                                   radius=VKI_HOME_HEARTH_RADIUS)],
                  vki_fx=[dict(fx="fire_small", pos=[0.0, 0.0, 0.2])])


def vki_home_oven(k):
    """bread oven 1.20 x 1.20 x 1.90, wall_floor: a brick base with a log store under an oak lintel, a stone hearth
    slab, a brick dome, an arched brick mouth (voussoirs, sooty) glowing inside (embers and a flame, vki_heat), a
    brick flue at the back rising into the wall, an iron door and a peel"""
    B = VKI_BRICK
    vki_home_box(k, -0.58, -0.34, -0.56, 0.12, 0.0, 0.62, B, bev=0.02)
    vki_home_box(k, 0.34, 0.58, -0.56, 0.12, 0.0, 0.62, B, bev=0.02)
    vki_home_box(k, -0.58, 0.58, 0.12, 0.60, 0.0, 0.62, B, bev=0.02)
    for x, z, r in ((-0.20, 0.075, 0.07), (0.0, 0.075, 0.072), (0.20, 0.075, 0.068), (-0.10, 0.205, 0.066),
                    (0.10, 0.205, 0.07), (0.0, 0.33, 0.062)):
        vki_home_log(k, (x, -0.24, z), r, 0.54, rz=math.pi / 2, segs=10, dark=0.08)
    vki_home_box(k, -0.40, 0.40, -0.575, -0.50, 0.54, 0.616, WOOD, bev=0.012)                    # lintel
    sl = vki_home_box(k, -0.60, 0.60, -0.60, 0.60, 0.62, 0.74, VKI_STONE_BLOCK_IN, bev=0.02)     # hearth slab
    k.set_dark([v for v in sl if v.co.y < -0.3 and abs(v.co.x) < 0.35], 0.18)
    dv, df = vki_home_lathe(k, [(0.0, 0.0), (0.50, 0.0), (0.49, 0.10), (0.455, 0.22), (0.39, 0.33), (0.29, 0.42),
                                (0.16, 0.48), (0.0, 0.50)], c=(0.0, 0.06, 0.735), segs=VKI_HOME_SEG, mi=B,
                            smooth=True, tile=1.5, uv="cylr", a0=math.pi / 2)
    for v in dv:                                                 # soot plume over the mouth
        if v.co.y < -0.1:
            k.set_dark([v], 0.45 * (1 - vki_smoothstep(0.0, 0.35, abs(v.co.x))) * vki_smoothstep(-0.1, -0.45, v.co.y))
    for s in (-1, 1):                                            # mouth jambs
        xa, xb = sorted((s * 0.17, s * 0.33))
        jv = vki_home_box(k, xa, xb, -0.56, -0.36, 0.74, 0.96, B, bev=0.015)
        k.set_dark([v for v in jv if abs(v.co.x) < 0.2], 0.45)
    for i in range(7):                                           # voussoirs
        a = math.pi * (i + 0.5) / 7
        c = (0.235 * math.cos(a), -0.46, 0.96 + 0.235 * math.sin(a))
        vv = list(set(k.box(c, (0.13, 0.20, 0.075), B, rot=(0, -a, 0), bevel=0.012)))
        k.set_dark([v for v in vv if (Vector((v.co.x, v.co.z)) - Vector((0.0, 0.96))).length < 0.20], 0.5)
    vki_home_box(k, -0.19, 0.19, -0.40, -0.10, 0.745, 1.14, VOID, bev=0.0)                      # dark oven
    rnd = random.Random(707)
    for i in range(4):
        c = Vector((-0.10 + 0.065 * i + rnd.uniform(-0.01, 0.01), -0.46 + rnd.uniform(-0.03, 0.03), 0.765))
        ev = vki_home_ico(k, c, 0.04, GLOW, scale=(1.0, 1.0, 0.6), sub=1, jit=0.005, seed=710 + i, smooth=False)
        for v in ev:
            k.set_heat([v], vki_clamp(0.95 - (v.co - Vector((0.0, -0.46, 0.75))).length / 0.25))
        k.project(vki_faces_of(ev), GLOW)
    vki_tim_flame(k, (0.0, -0.44, 0.76), 0.17, 0.055, 0.0, 0.2, 0.02)
    vki_home_box(k, -0.18, 0.18, 0.30, 0.595, 1.0, 1.845, B, bev=0.015)                          # flue
    vki_home_box(k, -0.21, 0.21, 0.27, 0.60, 1.84, 1.90, VKI_STONE_BLOCK_IN, bev=0.012)          # flue cap
    vki_home_box(k, 0.35, 0.57, -0.56, -0.36, 0.735, 0.752, IRON, bev=0.004, rot=(0, 0, 0.12))   # door, set down
    vki_home_box(k, 0.43, 0.49, -0.47, -0.45, 0.75, 0.775, IRON, bev=0.0, rot=(0, 0, 0.12))       # its handle
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -1.05, 0]],
                  vki_lights=[dict(type="POINT", role="oven", pos=list(VKI_HOME_OVEN_LIGHT), w=VKI_HOME_OVEN_W,
                                   color=[1.0, .50, .20], range=4.0, flicker=1, shadows=1, radius=0.15)],
                  vki_fx=[dict(fx="fire_small", pos=[0.0, -0.46, 0.78])],
                  vki_note="the flue runs up the back plane (into the wall); tall (1.90): against a Full wall")


def vki_home_worktable(k):
    """kitchen worktable 1.20 x 0.75 x 0.85, wall_floor: a two-board hewn top, legs (the front pair splayed
    forward), aprons, a pot board with a crock and a basket; on top a chopping board with a cabbage, carrots and a
    knife, a turnip, a bowl of stew and a bunch of herbs (goods atlas)"""
    X, Y, zt = 0.60, 0.375, 0.85
    z0 = zt - VKI_HOME_TOP_T
    vki_home_top(k, -X, X, -Y, Y, z0, zt, boards=2, bev=VKI_HOME_TOP_BEV, seed=71)
    tx, ty = math.tan(math.radians(4.0)), math.tan(math.radians(4.0))
    zl = z0 + 0.03
    for sx in (-1, 1):
        for sy, spl in ((-1, ty), (1, 0.0)):
            vki_home_leg(k, (sx * 0.46, sy * 0.25), (sx * (0.46 + zl * tx), sy * 0.25 + (-zl * spl if sy < 0 else 0.0)),
                         0.0, zl, 0.12)
    for sy in (-1, 1):
        ya, yb = sorted((sy * 0.23, sy * 0.27))
        vki_home_box(k, -0.46, 0.46, ya, yb, z0 - 0.12, z0, WOOD, bev=0.0)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 0.44, sx * 0.48))
        vki_home_box(k, xa, xb, -0.20, 0.20, z0 - 0.12, z0, WOOD, bev=0.0)
    vki_home_box(k, -0.53, 0.53, -0.31, 0.29, 0.14, 0.18, WOOD, bev=0.01)                       # pot board
    vki_home_crock(k, -0.25, 0.02, 0.18, r=0.11, h=0.30, lid=True, seed=72)
    vki_home_basket(k, 0.22, -0.02, 0.18, r=0.15, h=0.12, fill="apple", n=5, seed=73)
    vki_home_box(k, -0.46, -0.04, -0.24, 0.06, zt, zt + 0.03, WOOD, bev=0.006)                  # chopping board
    cb = vki_home_ico(k, (-0.30, -0.08, 0.0), 0.10, GOODS, scale=(1.0, 1.0, 0.85), sub=2, jit=0.01, seed=74,
                      rest=zt + 0.03)
    goods_map(k, cb, "cabbage")
    rnd = random.Random(75)
    for i in range(3):
        a = rnd.uniform(-0.3, 0.3)
        R = Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-math.pi / 2, 4, "Y")
        cc = Vector((-0.12, -0.16 + 0.05 * i, zt + 0.03 + 0.026))
        cv = _cyl(k, tuple(cc), 0.026, 0.004, 0.20, 6, PUMPKIN, rot=R)
        goods_map(k, cv, "carrot", axis=-(R.to_3x3() @ VKI_HOME_Z), c=tuple(cc))
        lv = vki_home_ico(k, tuple(cc + R.to_3x3() @ Vector((0.0, 0.0, -0.12))), 0.028, GOODS, scale=(1.0, 1.0, 0.7),
                          sub=1, smooth=False, seed=76 + i)
        goods_map(k, lv, "herbs")
    vki_home_box(k, -0.40, -0.25, 0.005, 0.03, zt + 0.03, zt + 0.036, STEEL, bev=0.0, rot=(0, 0, 0.15))   # knife
    vki_home_box(k, -0.25, -0.16, 0.0, 0.03, zt + 0.03, zt + 0.052, WOOD, bev=0.004, rot=(0, 0, 0.15))
    tv = vki_home_ico(k, (0.08, 0.14, 0.0), 0.06, GOODS, scale=(1.0, 1.0, 0.9), sub=2, jit=0.005, seed=77, rest=zt)
    goods_map(k, tv, "turnip")
    vki_home_bowl(k, 0.30, 0.08, zt, r=0.11, h=0.07, mi=CLAY, fill="pomace")
    hv = vki_home_ico(k, (0.33, -0.19, 0.0), 0.06, GOODS, scale=(1.4, 0.8, 0.5), sub=1, jit=0.008, seed=78, rest=zt)
    goods_map(k, hv, "herbs")
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[[0.0, -0.80, 0]], vki_table_z=zt)


def vki_home_desk(k):
    """merchant's standing desk 1.50 x 0.75 x 1.10, floor: four oak legs, a desk box with a leather writing slope
    (HIDE) and an open ledger (PAPER pages), a hewn back gallery with an ink pot, a quill and loose papers; a low
    shelf with closed ledgers and an iron-bound strongbox"""
    X, Y = 0.75, 0.375
    tx = math.tan(math.radians(3.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            vki_home_leg(k, (sx * 0.64, sy * 0.28), (sx * (0.64 + 0.85 * tx), sy * 0.28), 0.0, 0.85, 0.12)
    vki_home_box(k, -0.67, 0.67, -0.32, 0.32, 0.16, 0.20, WOOD, bev=0.01)                       # low shelf
    vki_home_box(k, -0.72, 0.72, -0.36, 0.36, 0.82, 0.95, WOOD, bev=0.014)                      # desk box
    sv, sf = vki_prism(k, [(-0.375, 0.945), (0.10, 0.945), (0.10, 1.035), (-0.375, 0.975)], -0.74, 0.74, WOOD,
                       axis="x", bevel=0.01)
    k.bm.normal_update()
    top = [f for f in sf if f.normal.z > 0.9]
    vki_home_uv(k, top, HIDE, VKI_HOME_X, (VKI_HOME_Y + VKI_HOME_Z * 0.126).normalized(), 1.0)
    vki_home_top(k, -0.74, 0.74, 0.10, Y, 1.03, 1.075, boards=1, bev=0.012, seed=101)             # gallery
    vki_home_box(k, -0.74, 0.74, 0.345, Y, 1.07, 1.10, WOOD, bev=0.006)                         # back rail
    # open ledger on the slope (tilted like it): cover, two pages in a shallow V
    sl = math.atan2(0.06, 0.475)
    Rs = Matrix.Rotation(sl, 4, "X")
    base = Vector((-0.12, -0.15, 0.975 + (0.225) * math.tan(sl)))
    for (x0, x1, mi, dz, ang) in ((-0.23, 0.23, HIDE, 0.0, 0.0), (-0.215, -0.005, PAPER, 0.008, 0.07),
                                  (0.005, 0.215, PAPER, 0.008, -0.07)):
        hy = 0.155 if mi == HIDE else 0.15
        bv = vki_home_box(k, x0, x1, -hy, hy, dz, dz + (0.008 if mi == HIDE else 0.012), mi, bev=0.0,
                          rot=(0, ang, 0))
        bmesh.ops.transform(k.bm, matrix=Matrix.Translation(base) @ Rs, verts=bv)
    vki_home_cyl(k, -0.55, 0.22, 1.072, 0.036, 0.03, 0.055, segs=10, mi=IRON)                  # ink pot
    vki_home_box(k, -0.56, -0.535, 0.21, 0.222, 1.10, 1.24, PAPER, bev=0.0, rot=(0.25, 0.2, 0))  # quill
    for i in range(3):                                                                            # loose papers
        vki_home_box(k, 0.35, 0.60, 0.14, 0.33, 1.075 + 0.004 * i, 1.078 + 0.004 * i, PAPER, bev=0.0,
                     rot=(0, 0, 0.12 * (i - 1)))
    for i in range(3):                                                                            # closed ledgers
        z = 0.20 + 0.052 * i
        vki_home_box(k, -0.55, -0.23, -0.12 + 0.01 * i, 0.12 + 0.01 * i, z, z + 0.05, HIDE, bev=0.004,
                     rot=(0, 0, 0.06 * (i - 1)))
        vki_home_box(k, -0.54, -0.24, -0.126 + 0.01 * i, -0.118 + 0.01 * i, z + 0.006, z + 0.044, PAPER, bev=0.0,
                     rot=(0, 0, 0.06 * (i - 1)))
    vki_home_box(k, 0.15, 0.50, -0.12, 0.12, 0.20, 0.42, WOOD, bev=0.012)                        # strongbox
    for x in (0.22, 0.43):
        vki_home_box(k, x - 0.02, x + 0.02, -0.128, 0.128, 0.198, 0.428, IRON, bev=0.0)
    vki_home_box(k, 0.30, 0.35, -0.13, -0.12, 0.30, 0.36, IRON, bev=0.0)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.80, 0]], vki_fp_cells="2,1",
                  vki_note="2 x 1 cells: 1.50 wide > 1.40 (a 1-cell floor prop is <= 1.5 - 0.10); centre it on a node")


# ---------------------------------------------------------------- table dressing
def vki_home_dress_meal_a(k):
    """table dressing A (origin on the table top, placed at z 0.80), within 1.0 x 0.5 so it fits Table_Trestle_150:
    a board with a loaf and a cheese (a wheel and a cut wedge), a ham with its bone, a clay jug (goods atlas food)"""
    vki_home_box(k, -0.46, -0.02, -0.20, 0.10, 0.0, 0.03, WOOD, bev=0.0)                      # bread board
    vki_home_loaf(k, -0.31, -0.06, 0.03, rz=math.pi / 2, s=1.0, seed=3)
    goods_map(k, vki_home_cyl(k, -0.10, 0.02, 0.027, 0.075, 0.075, 0.07, segs=VKI_HOME_SEG_D, mi=GOODS), "cheese",
              caps=True)
    vki_home_wedge(k, -0.13, -0.15, 0.03, a=0.5)
    vki_home_ham(k, 0.15, -0.03, 0.0, rz=0.35, s=0.95)
    vki_home_jug(k, 0.42, 0.13, 0.0, h=0.22, seed=5, segs=VKI_HOME_SEG_D, hseg=5)
    vki_home_meta(k, "table", "dressing", use=[], vki_table_z=VKI_HOME_TABLE_Z,
                  vki_fits=["SM_VKI_Prop_Table_Trestle_300", "SM_VKI_Prop_Table_Trestle_150"],
                  vki_note="origin on the table-top surface: place at the table's origin with z = 0.80")


def vki_home_dress_meal_b(k):
    """table dressing B (origin on the table top, placed at z 0.80), within 1.5 x 0.45 for Table_Trestle_300: a long
    board with a loaf and two cheese wedges, a ham with its bone, a clay jug"""
    vki_home_box(k, -0.72, -0.18, -0.17, 0.13, 0.0, 0.03, WOOD, bev=0.0)
    vki_home_loaf(k, -0.55, -0.02, 0.03, rz=math.pi / 2 + 0.25, s=1.05, seed=21)
    vki_home_wedge(k, -0.33, 0.05, 0.03, a=2.3)
    vki_home_wedge(k, -0.30, -0.09, 0.03, a=0.9, s=0.9)
    vki_home_ham(k, 0.10, 0.03, 0.0, rz=-0.45, s=1.0)
    vki_home_jug(k, 0.56, -0.03, 0.0, h=0.24, seed=9, segs=VKI_HOME_SEG_D, hseg=5, rz=-0.6)
    vki_home_meta(k, "table", "dressing", use=[], vki_table_z=VKI_HOME_TABLE_Z,
                  vki_fits=["SM_VKI_Prop_Table_Trestle_300"],
                  vki_note="origin on the table-top surface: place at the table's origin with z = 0.80")


# ---------------------------------------------------------------- workshop rigs (WS_vki_home only; not shipped)
VKI_HOME_WS = "WS_vki_home"
VKI_HOME_TW = "SM_VKI_Wall_Timber_"
VKI_HOME_TP = "SM_VKI_Post_Timber_"


def vki_home_ws_coll(sc, suffix, clear=True):
    """a collection WS_vki_home_<suffix> in the workshop scene (emptied, lights removed with their data)"""
    n = f"{VKI_HOME_WS}_{suffix}"
    c = bpy.data.collections.get(n) or bpy.data.collections.new(n)
    if c.name not in sc.collection.children:
        sc.collection.children.link(c)
    if clear:
        for o in list(c.objects):
            d = o.data
            bpy.data.objects.remove(o)
            if isinstance(d, bpy.types.Light) and d.users == 0:
                bpy.data.lights.remove(d)
    return c


def vki_home_ws_build_rig(name, walls, floors, props, origin, bounds):
    """place walls / posts / floors and props (vki_place, props backed by these walls) in collections
    WS_vki_home_<name>Shell / Props / Lights, lights from the masters' sockets; masters excluded from the renders"""
    sc, _, _ = vki_ws("home")
    lc = sc.view_layers[0].layer_collection.children.get(f"{VKI_HOME_WS}_Pieces")
    if lc is not None:
        lc.exclude = True
    shell, pc, lights = (vki_home_ws_coll(sc, name + s) for s in ("Shell", "Props", "Lights"))
    ox, oy = origin
    out = {"shell": [], "props": []}
    for it in walls:
        piece, x, y, rot = it[:4]
        out["shell"].append(vki_place(shell, piece, ox + x, oy + y, rot, style=(it[4] if len(it) > 4 else None),
                                      walls=[]))
    for it in floors:
        out["shell"].append(vki_place(shell, it[0], it[1], it[2], 0, style=(it[4] if len(it) > 4 else None), walls=[]))
    wl = [o for o in out["shell"] if o.get("vki_class") in ("wall", "post")]
    for piece, x, y, rot, kw in props:
        if bpy.data.objects.get(piece) is None:
            continue
        out["props"].append(vki_place(pc, piece, ox + x, oy + y, rot, walls=wl, **kw))
    vki_lt_lights(sc, shell, lights)
    vki_lt_lights(sc, pc, lights)
    sc["vki_room_bounds"] = json.dumps(list(bounds)); sc["vki_family"] = "Timber"
    for k_ in ("vki_cam_dist", "vki_cam_target"):
        if k_ in sc:
            del sc[k_]
    return out


def vki_home_ws_room(origin=(0.0, 0.0)):
    """the furnished corner (the Cottage set): a 5 x 3-cell Timber room (7.5 x 4.5 m, SW node at origin) placed with
    vki_place -- north wall Full (Plain_300 | Plain_150A | Plain_300), west wall Full (Rake_L | Window_150 |
    Plain_150A), east wall Full (Plain_300 | Rake_R), south wall Cut (Plain_300_Cut | Plain_150A_Cut |
    Plain_300_Cut), Corner posts (Cut at the rakes' low ends), rhythm Mid posts at the even nodes no wall-backed prop
    spans, a FlagRustic floor; Bed_Box, Chest under the Shelf, Pantry, table set with Meal_A, LogBasket"""
    W, P = VKI_HOME_TW, VKI_HOME_TP
    walls = [(W + "Plain_300_Full", 0, 4.5, 0), (W + "Plain_150A_Full", 3.0, 4.5, 0), (W + "Plain_300_Full", 4.5, 4.5, 0),
             (W + "Rake_150_L", 0, 0, 90), (W + "Window_150_Full", 0, 1.5, 90), (W + "Plain_150A_Full", 0, 3.0, 90),
             (W + "Plain_300_Full", 7.5, 4.5, -90), (W + "Rake_150_R", 7.5, 1.5, -90),
             (W + "Plain_300_Cut", 7.5, 0, 180), (W + "Plain_150A_Cut", 4.5, 0, 180), (W + "Plain_300_Cut", 3.0, 0, 180),
             (P + "Corner_Full", 0, 4.5, 0), (P + "Corner_Full", 7.5, 4.5, 0), (P + "Corner_Cut", 0, 0, 0),
             (P + "Corner_Cut", 7.5, 0, 0), (P + "Mid_Full", 3.0, 4.5, 0), (P + "Mid_Full", 0, 3.0, 90),
             (P + "Mid_Cut", 3.0, 0, 0)]
    ox, oy = origin
    floors = vki_c3_floor_pieces(ox, oy, 5, 3, {"floor": "FlagRustic"})
    props = [("SM_VKI_Prop_Bed_Box", 1.5, 3.75, 0, {}), ("SM_VKI_Prop_Chest", 3.75, 3.75, 0, {}),
             ("SM_VKI_Prop_Shelf_Wall_150", 3.75, 3.75, 0, {}),
             ("SM_VKI_Prop_Pantry_Shelves_300", 6.0, 3.75, 0, {}),
             ("SM_VKI_Prop_Table_Trestle_300", 4.5, 2.25, 0, {}), ("SM_VKI_Prop_Form_300", 4.5, 1.5, 0, {}),
             ("SM_VKI_Prop_Form_300", 4.5, 3.0, 0, {}),
             ("SM_VKI_Prop_TableDress_Meal_A", 4.5, 2.25, 0, dict(z=VKI_HOME_TABLE_Z, mount="table")),
             ("SM_VKI_Prop_LogBasket", 6.75, 2.25, 0, {})]
    return vki_home_ws_build_rig("Room", walls, floors, props, origin, (ox, oy, ox + 7.5, oy + 4.5))


def vki_home_ws_gallery(origin=(0.0, -12.0)):
    """the catalog gallery: a 12 x 5-cell Timber room (18 x 7.5 m) with a Full north wall carrying every wall-backed
    master (placed with vki_place), Full side walls with rakes, a Cut south wall, Boards_NS floor; the floor props in
    two rows (tables with forms and dressing, small table, desk, hearth, straw bed; barrels, crate, log basket)"""
    W, P = VKI_HOME_TW, VKI_HOME_TP
    walls = [(W + "Plain_300_Full", 3.0 * i, 7.5, 0) for i in range(6)]
    walls += [(W + "Rake_150_L", 0, 0, 90), (W + "Plain_300_Full", 0, 1.5, 90), (W + "Plain_300_Full", 0, 4.5, 90),
              (W + "Plain_300_Full", 18, 7.5, -90), (W + "Plain_300_Full", 18, 4.5, -90), (W + "Rake_150_R", 18, 1.5, -90)]
    walls += [(W + "Plain_300_Cut", 18 - 3.0 * i, 0, 180) for i in range(6)]
    walls += [(P + "Corner_Full", 0, 7.5, 0), (P + "Corner_Full", 18, 7.5, 0), (P + "Corner_Cut", 0, 0, 0),
              (P + "Corner_Cut", 18, 0, 0)]
    walls += [(P + "Mid_Cut", 3.0 * i, 0, 0) for i in range(1, 6)]
    ox, oy = origin
    floors = vki_c3_floor_pieces(ox, oy, 12, 5, {"floor": "Boards_NS"})
    t = dict(z=VKI_HOME_TABLE_Z, mount="table")
    N = 6.75                                                     # the wall-backed row snaps to the north wall
    props = [("SM_VKI_Prop_Bed_Box", 1.5, N, 0, {}), ("SM_VKI_Prop_Chest", 3.75, N, 0, {}),
             ("SM_VKI_Prop_Dresser", 5.25, N, 0, {}), ("SM_VKI_Prop_Worktable_150", 6.75, N, 0, {}),
             ("SM_VKI_Prop_Shelf_Wall_150", 6.75, N, 0, {}), ("SM_VKI_Prop_Pantry_Shelves_300", 9.0, N, 0, {}),
             ("SM_VKI_Prop_Oven_150", 11.25, N, 0, {}), ("SM_VKI_Prop_Jars_Cluster", 12.75, N, 0, {}),
             ("SM_VKI_Prop_Bed_HalfTester", 15.0, 6.0, 0, {}),
             ("SM_VKI_Prop_Table_Trestle_300", 2.25, 3.75, 0, {}), ("SM_VKI_Prop_TableDress_Meal_B", 2.25, 3.75, 0, t),
             ("SM_VKI_Prop_Form_300", 2.25, 3.0, 0, {}), ("SM_VKI_Prop_Form_300", 2.25, 4.5, 0, {}),
             ("SM_VKI_Prop_Table_Trestle_150", 5.25, 3.75, 0, {}), ("SM_VKI_Prop_TableDress_Meal_A", 5.25, 3.75, 0, t),
             ("SM_VKI_Prop_Form_150", 5.25, 3.0, 0, {}), ("SM_VKI_Prop_Form_150", 5.25, 4.5, 0, {}),
             ("SM_VKI_Prop_Table_Small", 7.5, 3.75, 0, {}), ("SM_VKI_Prop_Desk_Merchant", 9.75, 3.75, 0, {}),
             ("SM_VKI_Prop_Hearth_Open", 12.0, 3.75, 0, {}), ("SM_VKI_Prop_Bed_Straw", 16.5, 3.75, 0, {}),
             ("SM_VKI_Prop_Barrel", 7.5, 1.5, 0, {}), ("SM_VKI_Prop_Barrel_Water", 9.0, 1.5, 0, {}),
             ("SM_VKI_Prop_Crate", 10.5, 1.5, 0, {}), ("SM_VKI_Prop_LogBasket", 12.0, 1.5, 0, {})]
    return vki_home_ws_build_rig("Gallery", walls, floors, props, origin, (ox, oy, ox + 18.0, oy + 7.5))


VKI_HOME_ROW_Y = 9.0              # the masters' row in WS_vki_home (north of the test room; the board shows *_Pieces)


def vki_home_ws_layout(gap=0.6):
    """lay the built masters out in one row along +X at y = VKI_HOME_ROW_Y (in VKI_HOME_NAMES order, spaced by their
    footprints), so nothing overlaps at the origin; the renders exclude the pieces collection anyway"""
    x = 0.0
    out = []
    for n in VKI_HOME_NAMES:
        o = bpy.data.objects.get(n)
        if o is None or not any(c.name == f"{VKI_HOME_WS}_Pieces" for c in o.users_collection):
            continue
        x0, y0, x1, y1 = [float(t) for t in o["vki_footprint"].split(",")]
        o.location = (x - x0, VKI_HOME_ROW_Y, 0.0)
        o.rotation_euler = (0.0, 0.0, 0.0)
        x += (x1 - x0) + gap
        out.append((n, round(o.location.x, 3)))
    return out


def vki_home_ws_overlaps(props, shell):
    """T12's object-level AABB checks restricted to one rig (the workshop scene also holds the parked masters):
    prop / prop (5 mm shrink; table mounts exempt) and prop / wall-or-post (wall_hung exempt), plus the post rules"""
    errs = []
    struct = [o for o in shell if o.get("vki_class") in ("wall", "post")]
    boxes = {o.name: vki_obj_aabb(o, 0.005) for o in props}
    for i, a in enumerate(props):
        for b in props[i + 1:]:
            if "table" in (a.get("vki_mount"), b.get("vki_mount")):
                continue
            if vki_aabb_overlap(boxes[a.name], boxes[b.name]):
                errs.append(f"prop overlap {a.name} / {b.name}")
        if a.get("vki_mount") == "wall_hung":
            continue
        for s_ in struct:
            if vki_aabb_overlap(boxes[a.name], vki_obj_aabb(s_)):
                errs.append(f"prop {a.name} intersects {s_.name}")
        if "vki_hug_fail" in a.keys():
            errs.append(f"{a.name}: hug failed ({a['vki_hug_fail']})")
    return errs + vki_t12_posts(shell)


def vki_home_ws_checks(objs):
    """placement checks on placed props: wall_floor backs on the proud line (gap), wall_hung backs on the wall
    face, table dressing height. Returns rows (name, check, value, ok)."""
    rows = []
    for o in objs:
        mw = vki_mw(o)
        mount = o.get("vki_mount")
        if mount in ("wall_floor", "wall_hung"):
            wall = bpy.data.objects.get(o.get("vki_host", ""))
            if wall is None:
                rows.append((o.name, "host", None, False))
                continue
            cls = "P" if float(wall.get("vki_thick", 0.5)) < 0.4 else "O"
            wi = vki_mw(wall).inverted()
            d = -max((wi @ (mw @ v.co)).y for v in o.data.vertices)    # room side is the wall's local -Y
            want = VKI_PROUD_LINE[cls] if mount == "wall_floor" else VKI_T[cls] / 2
            rows.append((o.name, "back gap", round(d - want, 5), -1e-6 <= d - want <= 0.005))
        if mount == "table":
            zmin = min((mw @ v.co).z for v in o.data.vertices)
            rows.append((o.name, "table z / min z", (round(mw.translation.z, 4), round(zmin, 4)),
                         abs(mw.translation.z - VKI_HOME_TABLE_Z) < 1e-6 and zmin > VKI_HOME_TABLE_Z - 0.006))
    return rows


def vki_home_fp_check(names):
    """footprint vs vki_fp_cells and the §5 mount size rules: floor <= 1.5 n - 0.10; wall_floor width <= 1.5 n - 0.30,
    depth <= 1.5 d - 0.30. Returns rows (name, (w, d), cells, ok)."""
    rows = []
    for n in names:
        o = bpy.data.objects.get(n)
        if o is None:
            continue
        x0, y0, x1, y1 = [float(t) for t in o["vki_footprint"].split(",")]
        w, d = x1 - x0, y1 - y0
        cw, cd = [int(t) for t in o["vki_fp_cells"].split(",")]
        m = o.get("vki_mount")
        if m == "wall_floor":
            ok = w <= 1.5 * cw - 0.30 + 1e-3 and d <= 1.5 * cd - 0.30 + 1e-3
        elif m == "floor":
            ok = w <= 1.5 * cw - 0.10 + 1e-3 and d <= 1.5 * cd - 0.10 + 1e-3
        else:
            ok = w <= 1.5 * cw and d <= 1.5 * cd
        ok = ok and (cw - 1) * 1.5 < w + 1e-3 + (0.30 if m == "wall_floor" else 0.10)
        rows.append((n, (round(w, 3), round(d, 3)), (cw, cd), m, ok))
    return rows


# ---------------------------------------------------------------- registration
VKI_HOME_SPECS = [
    ("SM_VKI_Prop_Table_Trestle_300", vki_home_table_trestle_300, "prop"),
    ("SM_VKI_Prop_Table_Trestle_150", vki_home_table_trestle_150, "prop"),
    ("SM_VKI_Prop_Table_Small", vki_home_table_small, "prop"),
    ("SM_VKI_Prop_Form_300", vki_home_form_300, "prop"),
    ("SM_VKI_Prop_Form_150", vki_home_form_150, "prop"),
    ("SM_VKI_Prop_Chest", vki_home_chest, "prop"),
    ("SM_VKI_Prop_Dresser", vki_home_dresser, "prop"),
    ("SM_VKI_Prop_Shelf_Wall_150", vki_home_shelf_wall, "prop"),
    ("SM_VKI_Prop_Pantry_Shelves_300", vki_home_pantry, "prop"),
    ("SM_VKI_Prop_Barrel", vki_home_barrel_prop, "prop"),
    ("SM_VKI_Prop_Barrel_Water", vki_home_barrel_water, "prop"),
    ("SM_VKI_Prop_Crate", vki_home_crate, "prop"),
    ("SM_VKI_Prop_Jars_Cluster", vki_home_jars, "prop"),
    ("SM_VKI_Prop_LogBasket", vki_home_logbasket, "prop"),
    ("SM_VKI_Prop_Bed_Straw", vki_home_bed_straw, "prop"),
    ("SM_VKI_Prop_Bed_Box", vki_home_bed_box, "prop"),
    ("SM_VKI_Prop_Bed_HalfTester", vki_home_bed_halftester, "prop"),
    ("SM_VKI_Prop_Hearth_Open", vki_home_hearth_open, "prop"),
    ("SM_VKI_Prop_Oven_150", vki_home_oven, "prop"),
    ("SM_VKI_Prop_Worktable_150", vki_home_worktable, "prop"),
    ("SM_VKI_Prop_Desk_Merchant", vki_home_desk, "prop"),
    ("SM_VKI_Prop_TableDress_Meal_A", vki_home_dress_meal_a, "prop"),
    ("SM_VKI_Prop_TableDress_Meal_B", vki_home_dress_meal_b, "prop"),
]
VKI_HOME_NAMES = [n_ for n_, _, _ in VKI_HOME_SPECS]
vki_register([(n_, fn_, {"grime": gr_}, "home") for n_, fn_, gr_ in VKI_HOME_SPECS])
