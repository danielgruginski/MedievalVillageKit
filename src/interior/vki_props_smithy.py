# ===================== VKI PROPS SMITHY: smithy and workshop furniture (§5.3 P1) -- 8 masters =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md §5 (conventions), §5.3, §10. Loaded by vki_ns() after
# vki_props_tavern, whose vki_tav_* helpers (lathe, slab, leg, rod, extrude, board UVs) it uses. Top-level names vki_.
# Props: origin at the footprint centre at floor level, back toward local +Y, front toward -Y (§2.1, §5).
#   Workbench_300        heavy sooty top, splayed legs, shelf with bar stock, a blacksmith's leg vice holding a bar
#   QuenchTrough_150     dressed stone blocks (STONE_BLOCK_IN), murky water (WATER -> M_VKI_WaterMurky), tongs
#   CoalBin_150          board bin with a heaped coal bed: bevelled, flat-shaded COAL lumps, a shovel
#   IronStock_150        base trough and lean rail holding iron (and a few steel) bars
#   ToolWall_150         wall_hung board (z 1.10-2.30) with tongs, hammers, a file and horseshoes on pegs
#   GoodsRack_150        open shelving: iron pots, stacks of turned bowls, tools
#   Workbench_Carpenter  bench with a tool tray, a wooden leg vice, planes, chisels, a mallet, shavings
#   PoleLathe            bed on trestles, poppets and centres, a spindle being turned, treadle, cord, spring pole
# Build: g["vki_ws_build"]("tavern", VKI_SMY_NAMES); test: g["vki_test_pieces"](VKI_SMY_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_SMY_SOOT = 0.18                 # smithy tops and boards: a little soot (vki_dark)
VKI_SMY_LEG_SPLAY = math.tan(math.radians(6.0))   # §5: legs splayed 5-8 deg


def vki_smy_box_rot(k, a, b, w, d, mi, bevel=0.003):
    """a bar of section w x d whose axis runs from point a to point b (its ends may be buried in other members)"""
    a = Vector(a); b = Vector(b); dv = b - a
    R = Vector((0.0, 0.0, 1.0)).rotation_difference(dv.normalized()).to_matrix().to_4x4()
    return list(set(k.box((0.0, 0.0, 0.0), (w, d, dv.length), mi, bevel=bevel,
                          xform=Matrix.Translation((a + b) / 2) @ R)))


def vki_smy_frame(k, x_legs, y_legs, z_top, w=0.14, sy_str=(0.16, 0.24), side_z=(0.30, 0.36)):
    """four splayed legs (flat tops and feet), long stretchers at sy_str, side stretchers at side_z (a different
    height, so no stretcher tops share a plane). Returns the leg centre x at the long-stretcher height."""
    sp = VKI_SMY_LEG_SPLAY
    for x in (-x_legs, x_legs):
        for y in y_legs:
            vki_tav_leg(k, x, y, 0.0, z_top, w, sx=math.copysign(sp, x))
    zs = (sy_str[0] + sy_str[1]) / 2
    xc = x_legs + sp * (z_top - zs)
    for y in y_legs:
        k.box((0.0, y, zs), (2 * xc, 0.06, sy_str[1] - sy_str[0]), WOOD, bevel=0.008)
    zq = (side_z[0] + side_z[1]) / 2
    xq = x_legs + sp * (z_top - zq)
    for sx in (-1, 1):
        k.box((sx * xq, (y_legs[0] + y_legs[1]) / 2, zq), (0.06, abs(y_legs[1] - y_legs[0]), side_z[1] - side_z[0]),
              WOOD, bevel=0.008)
    return xc


def vki_smy_hammer(k, x, y, z, rz=0.0, s=1.0, head=IRON):
    """a hammer lying on a surface at z: the head rests on it, the handle floats 5 mm (their feet never share a
    plane)"""
    R = Matrix.Rotation(rz, 4, "Z")
    hl = 0.30 * s
    k.box((0.0, 0.0, 0.0), (0.028 * s, hl, 0.025 * s), WOOD, bevel=0.004,
          xform=Matrix.Translation((x, y, z + 0.005 + 0.0125 * s)) @ R)
    c = Matrix.Translation((x, y, z)) @ R @ Vector((0.0, hl / 2, 0.0225 * s))
    k.box((0.0, 0.0, 0.0), (0.12 * s, 0.045 * s, 0.045 * s), head, bevel=0.006,
          xform=Matrix.Translation(c) @ R)


def vki_smy_horseshoe(k, M, mi=IRON, t=0.012):
    """a horseshoe: a U polygon (outer 0.065, inner 0.042, legs 0.05) in the local XZ plane, t thick along Y,
    placed by M"""
    ro, ri, lg, n = 0.065, 0.042, 0.05, 4
    pts = [(ro, -lg)] + [(ro * math.cos(math.pi * i / n), ro * math.sin(math.pi * i / n)) for i in range(n + 1)] + \
        [(-ro, -lg), (-ri, -lg)] + [(ri * math.cos(math.pi * (n - i) / n), ri * math.sin(math.pi * (n - i) / n))
                                    for i in range(n + 1)] + [(ri, -lg)]
    vs, fs = vki_tav_extrude(k, pts, -t / 2, t / 2, mi, axis="y")
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    k.bm.normal_update()
    k.project(fs, mi)
    return vs


def vki_smy_tongs(k, M, L=0.46, mi=IRON):
    """smith's tongs hanging jaws down in the local XZ plane (top at z 0): two crossed bars on different Y planes,
    small inturned jaws; placed by M"""
    out = []
    for sgn, y in ((1, -0.006), (-1, 0.006)):
        a = Vector((-0.030 * sgn, y, 0.0)); b = Vector((0.020 * sgn, y, -L))
        out += vki_smy_box_rot(k, a, b, 0.016, 0.010, mi, bevel=0.0)
        out += list(set(k.box((0.0, 0.0, 0.0), (0.040, 0.014, 0.050), mi, bevel=0.0,       # thicker than the bar
                              xform=Matrix.Translation((0.004 * sgn, y, -L - 0.012)) @
                              Matrix.Rotation(0.5 * sgn, 4, "Y"))))
    bmesh.ops.transform(k.bm, matrix=M, verts=list(set(out)))
    k.bm.normal_update()
    k.project(vki_tav_faces(out), mi)
    return out


def vki_smy_pot(k, x, y, z, r, h, mi=IRON, lugs=True):
    """an iron pot: rounded belly, rim, dark inside (vki_dark), two lugs"""
    prof = [(0.78 * r, 0.0), (r, 0.40 * h), (0.93 * r, h), (0.84 * r, h), (0.84 * r, 0.82 * h)]
    vs, bands, capf = vki_tav_lathe(k, prof, mi, M=Matrix.Translation((x, y, z)))
    k.set_dark(capf[-1].verts, 0.55)
    if lugs:
        for sx in (-1, 1):
            k.box((x + sx * 0.97 * r, y, z + 0.78 * h), (0.05 * r + 0.02, 0.030, 0.022), mi, bevel=0.0)
    return vs


def vki_smy_bowls(k, x, y, z, r, mi=HEWN):
    """a stack of three nested turned bowls (pale fresh wood): stepped rims, the top bowl's hollow"""
    prof = [(0.42 * r, 0.0), (0.86 * r, 0.26 * r), (0.98 * r, 0.40 * r), (1.00 * r, 0.52 * r), (1.02 * r, 0.64 * r),
            (0.90 * r, 0.64 * r), (0.55 * r, 0.36 * r)]
    vs, bands, capf = vki_tav_lathe(k, prof, mi, M=Matrix.Translation((x, y, z)), sharp_deg=20.0)
    k.set_dark(capf[-1].verts, 0.25)
    return vs


def vki_smy_heightfield(k, x0, x1, y0, y1, nx, ny, hfn, z0, mi, jit_xy=0.0, rnd=None):
    """closed solid: a triangulated grid top z = hfn(x, y) over [x0, x1] x [y0, y1], vertical sides down to z0, a flat
    bottom at z0; flat-shaded facets. jit_xy (fraction of a cell) moves the interior grid vertices at random, so the
    facets are irregular (rubble)."""
    bm = k.bm
    top = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, 0.0)) for i in range(nx + 1)]
           for j in range(ny + 1)]
    if jit_xy and rnd is not None:
        cx, cy = (x1 - x0) / nx, (y1 - y0) / ny
        for j in range(1, ny):
            for i in range(1, nx):
                top[j][i].co.x += rnd.uniform(-jit_xy, jit_xy) * cx
                top[j][i].co.y += rnd.uniform(-jit_xy, jit_xy) * cy
    for row in top:
        for v in row:
            v.co.z = hfn(v.co.x, v.co.y)
    fs = []
    for j in range(ny):
        for i in range(nx):
            a, b, c, d = top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]
            if (i + j) % 2:
                fs += [bm.faces.new((a, b, c)), bm.faces.new((a, c, d))]
            else:
                fs += [bm.faces.new((a, b, d)), bm.faces.new((b, c, d))]
    loop = [top[0][i] for i in range(nx + 1)] + [top[j][nx] for j in range(1, ny + 1)] + \
        [top[ny][i] for i in range(nx - 1, -1, -1)] + [top[j][0] for j in range(ny - 1, 0, -1)]
    bot = [bm.verts.new((v.co.x, v.co.y, z0)) for v in loop]
    m = len(loop)
    for i in range(m):
        j = (i + 1) % m
        fs.append(bm.faces.new((loop[i], loop[j], bot[j], bot[i])))
    fs.append(bm.faces.new(bot[::-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.material_index = mi
        f.smooth = False
    k.project(fs, mi)
    return [v for row in top for v in row] + bot


def vki_smy_lump(k, c, s, rnd, mi=COAL):
    """a coal lump: a strongly jittered box with small bevels (angular facets that catch the key light), flat-shaded,
    turned at random; each lump gets its own darkness and darker undersides (crevices between lumps)"""
    size = (s * rnd.uniform(0.85, 1.25), s * rnd.uniform(0.70, 1.05), s * rnd.uniform(0.55, 0.85))
    rot = (rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(0.0, math.pi))
    vs = list(set(k.box(c, size, mi, rot=rot, bevel=0.08 * min(size), jitter=0.22 * s,
                        seed=rnd.randint(0, 10 ** 6))))
    for f in vki_tav_faces(vs):
        f.smooth = False
    d0 = rnd.uniform(0.0, 0.18)
    for v in vs:
        k.set_dark([v], d0 + (0.35 if v.co.z < c[2] else 0.0))
    return vs


def vki_smy_chip(k, c, r, rnd, mi=COAL):
    """a small coal chip: a jittered icosahedron (20 flat facets) filling the gaps between the lumps"""
    vs = _ico(k, c, r, mi, scale=(1.0, rnd.uniform(0.7, 1.0), rnd.uniform(0.55, 0.8)), sub=0, jit=0.25 * r,
              seed=rnd.randint(0, 10 ** 6))
    fs = vki_tav_faces(vs)
    for f in fs:
        f.smooth = False
    k.bm.normal_update()
    k.project(fs, mi)
    k.set_dark(vs, rnd.uniform(0.10, 0.40))
    return vs


def vki_smy_curl(k, c, r, w, turns, rz, mi=HEWN, n=7, t=0.004):
    """a wood shaving: a thin closed ribbon (width w along the curl axis, thickness t) winding `turns` times round a
    horizontal axis with the radius shrinking; resting on z = c.z, turned rz about Z"""
    rows = []
    for i in range(n + 1):
        th = -math.pi / 2 + 2 * math.pi * turns * i / n
        rr = r * (1.0 - 0.45 * i / n)
        ax = w * 0.9 * i / n
        rows.append([(ax + da, (rr + dr) * math.cos(th), (rr + dr) * math.sin(th))
                     for da, dr in ((-w / 2, t / 2), (w / 2, t / 2), (w / 2, -t / 2), (-w / 2, -t / 2))])
    bm = k.bm
    vv = [[bm.verts.new(p) for p in row] for row in rows]
    fs = []
    for i in range(n):
        A, B = vv[i], vv[i + 1]
        for q in range(4):
            q2 = (q + 1) % 4
            fs.append(bm.faces.new((A[q], A[q2], B[q2], B[q])))
    fs.append(bm.faces.new(vv[0][::-1]))
    fs.append(bm.faces.new(vv[-1]))
    vs = [v for row in vv for v in row]
    zmin = min(v.co.z for v in vs)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((c[0], c[1], c[2] - zmin + 0.001)) @
                        Matrix.Rotation(rz, 4, "Z"), verts=vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.material_index = mi
        f.smooth = True
    k.project(fs, mi)
    return vs


def vki_smy_sweep(k, pts, radii, mi, seg=8):
    """closed tube along a polyline (Vectors) with per-point radii (a curved pole); caps at both ends"""
    bm = k.bm
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        up = Vector((0.0, 0.0, 1.0)) if abs(t.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        a = t.cross(up).normalized(); b = t.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * j / seg) + b * math.sin(2 * math.pi * j / seg))
                                   * radii[i]) for j in range(seg)])
    fs = []
    for A, B in zip(rings[:-1], rings[1:]):
        for j in range(seg):
            j2 = (j + 1) % seg
            fs.append(bm.faces.new((A[j], A[j2], B[j2], B[j])))
    fs.append(bm.faces.new(rings[0][::-1]))
    fs.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs[:-2]:
        f.smooth = True
    L = pts[-1] - pts[0]
    for f in fs:
        V = f.normal.cross(L).normalized() if f.normal.cross(L).length > 1e-6 else Vector((0.0, 0.0, 1.0))
        vki_tav_uv(k, [f], mi, L.normalized(), V)
    return [v for rg in rings for v in rg]


# ---------------------------------------------------------------- Workbench_300
def vki_smy_workbench(k):
    """Workbench_300 (2.70 x 0.80 x 0.90, wall_floor): heavy scrubbed top (sooty) with pale HEWN edges, splayed legs,
    stretchers and a bottom shelf with bar stock; a blacksmith's leg vice at the front left holding a bar; hammers,
    tongs, a file, bar ends and a horseshoe on the top"""
    top = vki_tav_slab(k, (0.0, 0.07, 0.85), (2.70, 0.66, 0.10), bevel=0.02)           # y -0.26..0.40
    k.set_dark(top, VKI_SMY_SOOT)
    vki_smy_frame(k, 1.16, (-0.14, 0.30), 0.80)
    shelf = vki_tav_slab(k, (0.0, 0.08, 0.255), (2.30, 0.50, 0.03), bevel=0.006)       # on the long stretchers
    k.set_dark(shelf, VKI_SMY_SOOT)
    for i, (y, L) in enumerate(((0.00, 1.10), (0.05, 0.85), (0.12, 1.25))):           # bar stock on the shelf
        k.box((-0.15 + 0.2 * i, y, 0.2825), (L, 0.025, 0.025), IRON, bevel=0.003)
    # leg vice (x -0.85): fixed jaw on the top's front edge, moving jaw, a bar clamped between them, screw, boss,
    # tommy bar, fixed leg to the floor, slanted moving leg, pivot block
    xv = -0.85
    k.box((xv, -0.285, 0.87), (0.12, 0.05, 0.14), IRON, bevel=0.008)
    k.box((xv, -0.36, 0.865), (0.12, 0.045, 0.13), IRON, bevel=0.008)
    k.box((xv + 0.04, -0.324, 0.9325), (0.03, 0.024, 0.255), IRON, bevel=0.003)      # feet 5 mm above the jaws'
    vki_tav_rod(k, (xv, -0.395, 0.845), (xv, -0.25, 0.845), 0.016, IRON)
    vki_tav_rod(k, (xv, -0.3825, 0.845), (xv, -0.397, 0.845), 0.028, IRON)
    vki_tav_rod(k, (xv - 0.13, -0.389, 0.845), (xv + 0.13, -0.389, 0.845), 0.009, IRON)
    k.box((xv, -0.285, 0.40), (0.04, 0.035, 0.80), IRON, bevel=0.004)
    vki_tav_rod(k, (xv, -0.36, 0.81), (xv, -0.30, 0.10), 0.016, IRON)
    k.box((xv, -0.30, 0.10), (0.05, 0.05, 0.05), IRON, bevel=0.005)
    # on the top (z 0.90): feet in the top plane never overlap in plan
    vki_smy_hammer(k, 0.35, -0.02, 0.90, rz=0.35)
    vki_smy_hammer(k, 0.72, 0.15, 0.90, rz=-1.2, s=1.25)
    for sgn, zb in ((1, 0.900), (-1, 0.906)):                                          # tongs lying crossed
        vki_smy_box_rot(k, (-0.30, 0.05 + 0.04 * sgn, zb + 0.007), (0.10, 0.05 - 0.05 * sgn, zb + 0.007), 0.016, 0.014,
                        IRON, bevel=0.0)
    k.box((1.02, -0.10, 0.903), (0.025, 0.26, 0.006), STEEL, bevel=0.0)                # file
    k.box((1.02, 0.08, 0.905), (0.028, 0.10, 0.010), WOOD, bevel=0.002)                # its handle
    k.box((-0.02, 0.26, 0.915), (0.36, 0.03, 0.03), IRON, bevel=0.004)                 # bar ends
    k.box((0.30, 0.30, 0.915), (0.30, 0.03, 0.03), IRON, bevel=0.004)
    vki_smy_horseshoe(k, Matrix.Translation((-0.55, 0.12, 0.906)) @ Matrix.Rotation(math.pi / 2, 4, "X") @
                      Matrix.Rotation(0.4, 4, "Y"))
    k.meta.update(vki_kind="Workbench", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=0.40,
                  vki_use=[[0.0, -0.75, 0], [-0.85, -0.75, 0]],
                  vki_note="leg vice at local x -0.85 on the front edge")


# ---------------------------------------------------------------- QuenchTrough_150
def vki_smy_quench(k):
    """QuenchTrough_150 (1.20 x 0.60 x 0.70, floor): dressed stone blocks (STONE_BLOCK_IN, chamfered, irregular
    tops, level feet), murky water 0.12 under the rim (WATER -> M_VKI_WaterMurky), tongs and a bar resting in it"""
    rnd = random.Random(5311)
    blocks = []
    for (x0, x1) in ((-0.60, -0.20), (-0.20, 0.20), (0.20, 0.60)):
        blocks += [((x0 + x1) / 2, -0.24, x1 - x0, 0.12), ((x0 + x1) / 2, 0.24, x1 - x0, 0.12)]
    blocks += [(-0.54, 0.0, 0.12, 0.36), (0.54, 0.0, 0.12, 0.36)]
    for (cx, cy, sx_, sy_) in blocks:
        vs = list(set(k.box((cx, cy, 0.35), (sx_, sy_, 0.70), VKI_STONE_BLOCK_IN, bevel=0.025)))
        vs.sort(key=lambda v: (round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)))   # set order is not stable
        for v in vs:
            if v.co.z > 0.05:                                    # hewn, irregular tops; feet stay level (§5)
                v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.004
        k.bm.normal_update()
        k.project(vki_tav_faces(vs), VKI_STONE_BLOCK_IN, offset=vki_hash_off((cx, cy, 0.35)))
        k.set_dark(vs, 0.08)
    k.box((0.0, 0.0, 0.31), (0.96, 0.36, 0.54), WATER, bevel=0.0)                     # water z 0.04..0.58
    vki_tav_rod(k, (0.20, -0.03, 0.40), (0.575, 0.01, 0.80), 0.009, IRON)               # tongs resting on the rim
    vki_tav_rod(k, (0.20, 0.05, 0.40), (0.575, 0.03, 0.80), 0.009, IRON)
    vki_tav_rod(k, (-0.25, -0.08, 0.35), (-0.52, 0.10, 0.76), 0.014, IRON)              # a bar
    k.slot_mats = {WATER: "WaterMurky"}
    k.meta.update(vki_kind="QuenchTrough", vki_tier="furniture", vki_mount="floor", vki_use=[[0.0, -0.65, 0]],
                  vki_note="water surface z 0.58, rim 0.70")


# ---------------------------------------------------------------- CoalBin_150
def vki_smy_coal_h(x, y):
    """the coal bed's surface: heaped against the back, low at the front board, lower at the sides, lumpy"""
    t = min(1.0, max(0.0, (y + 0.40) / 0.80))
    b = 0.15 * math.sin(7.0 * x + 1.3) * math.sin(5.0 * y + 0.4) + 0.06 * math.sin(13.0 * x - 3.0 * y)
    return 0.19 + 0.32 * t ** 0.9 - 0.06 * (x / 0.55) ** 2 + 0.25 * b * (0.4 + 0.6 * t)


def vki_smy_coalbin(k):
    """CoalBin_150 (1.20 x 0.90 x 0.70, wall_floor): a bin of boards (back 0.70, sides sloping to 0.34, a low front
    board, iron corner straps) holding a heaped coal bed covered in bevelled, flat-shaded COAL lumps; a shovel"""
    rnd = random.Random(8812)
    for (z0, z1) in ((0.0, 0.235), (0.235, 0.47), (0.47, 0.70)):                   # back: three boards
        vs = vki_tav_slab(k, (0.0, 0.425, (z0 + z1) / 2), (1.19, 0.04, z1 - z0), mi=WOOD,
                          bevel=0.01 if z1 > 0.6 else 0.0, along=(1, 0, 0))
        k.set_dark(vs, VKI_SMY_SOOT)
    for sx in (-1, 1):                                                               # sloping sides
        vs, fs = vki_tav_extrude(k, [(-0.405, 0.0), (0.405, 0.0), (0.405, 0.70), (-0.405, 0.34)],
                                 sx * 0.555, sx * 0.595, WOOD, axis="x")
        k.bm.normal_update()
        vki_tav_board_uv(k, fs, WOOD, (0, 1, 0), off=vki_hash_off((sx, 0.0, 0.3)), edge_mi=HEWN)
        k.set_dark(vs, VKI_SMY_SOOT)
    vs = vki_tav_slab(k, (0.0, -0.425, 0.13), (1.11, 0.04, 0.26), mi=WOOD, bevel=0.01)   # low front board
    k.set_dark(vs, VKI_SMY_SOOT)
    for sx in (-1, 1):
        k.box((sx * 0.575, -0.425, 0.13), (0.05, 0.045, 0.20), IRON, bevel=0.004)     # corner straps
    # coal (catalog r2/r3: with the material's 0.045 albedo only steep facets show any contrast -- a jagged bed read as
    # soot, sparse lumps as rocks on a sheet): a dense packing of angular lumps on a jittered 6 x 4 grid over the heap,
    # their tops barely darkened and their undersides dark; the bed below is a uniformly dark shadow between them
    hr = random.Random(8813)
    bed = vki_smy_heightfield(k, -0.545, 0.545, -0.40, 0.40, 6, 5,
                              lambda x, y: vki_smy_coal_h(x, y) - 0.03 + hr.uniform(-0.015, 0.015), 0.005, COAL)
    k.set_dark(bed, 0.55)
    for j in range(4):
        for i in range(6):
            x = -0.36 + 0.144 * i + rnd.uniform(-0.05, 0.05)
            y = -0.21 + 0.145 * j + rnd.uniform(-0.05, 0.05) + (0.03 if i % 2 else -0.03)
            s = rnd.uniform(0.07, 0.145)
            vs = vki_smy_lump(k, (x, y, vki_smy_coal_h(x, y) + 0.10 * s), s, rnd)
            # keep every lump inside the boards' inner faces (x +-0.55, y -0.40..0.40)
            xs = [v.co.x for v in vs]; ys = [v.co.y for v in vs]
            dx = min(0.0, 0.55 - max(xs)) or max(0.0, -0.55 - min(xs))
            dy = min(0.0, 0.40 - max(ys)) or max(0.0, -0.40 - min(ys))
            if dx or dy:
                bmesh.ops.translate(k.bm, vec=(dx, dy, 0.0), verts=vs)
    # coal shovel: blade dug into the heap (its far edge down toward the back), handle out toward the front
    bl = Matrix.Translation((0.22, 0.02, 0.46)) @ Matrix.Rotation(0.35, 4, "Z") @ Matrix.Rotation(-0.95, 4, "X")
    k.box((0.0, 0.0, 0.0), (0.22, 0.24, 0.012), IRON, bevel=0.003, xform=bl)
    vki_tav_rod(k, bl @ Vector((0.0, -0.11, 0.0)), (0.36, -0.30, 0.84), 0.018, WOOD)
    k.meta.update(vki_kind="CoalBin", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=0.445,
                  vki_use=[[0.0, -0.80, 0]],
                  vki_note="coal: 24 bevelled, jittered, flat-shaded COAL lumps packed on a jittered grid over a dark "
                           "heaped bed (heightfield)")


# ---------------------------------------------------------------- IronStock_150
def vki_smy_ironstock(k):
    """IronStock_150 (1.20 x 0.60 x 1.20, wall_floor): a base trough, two posts with lean rails, bars of square, round
    and flat stock (a few steel) leaning in the trough against the top rail, offcuts across the trough"""
    rnd = random.Random(7721)
    vs = vki_tav_slab(k, (0.0, -0.08, 0.15), (1.16, 0.40, 0.30), mi=WOOD, bevel=0.02, along=(1, 0, 0))  # y -.28..12
    k.set_dark(vs, VKI_SMY_SOOT)
    for sx in (-1, 1):                                                                # posts to 1.20
        vs = list(set(k.box((sx * 0.53, 0.22, 0.60), (0.08, 0.08, 1.20), WOOD, bevel=0.012)))
        vki_tav_hewn_tops(k, vs)
    for zc in (0.65, 1.10):                                                           # lean rails
        vs = vki_tav_slab(k, (0.0, 0.24, zc), (1.12, 0.08, 0.08), mi=WOOD, bevel=0.012, along=(1, 0, 0))
    xs = [-0.44, -0.36, -0.27, -0.19, -0.10, -0.02, 0.07, 0.15, 0.24, 0.32, 0.40, 0.46]
    for i, x in enumerate(xs):
        zt = rnd.uniform(1.07, 1.19)
        a = Vector((x + rnd.uniform(-0.02, 0.02), -0.12, 0.10)); b = Vector((x, 0.185, zt))
        mi = STEEL if i in (3, 8) else IRON
        kind = i % 3
        if kind == 0:
            vki_smy_box_rot(k, a, b, 0.024, 0.024, mi)
        elif kind == 1:
            vki_tav_rod(k, a, b, 0.013, mi)
        else:
            vki_smy_box_rot(k, a, b, 0.050, 0.012, mi)
    for (x, y, L, rz) in ((-0.20, -0.22, 0.55, 0.10), (0.25, -0.19, 0.42, -0.15)):   # offcuts across the trough
        k.box((x, y, 0.3125), (L, 0.025, 0.025), IRON, bevel=0.003, rot=(0.0, 0.0, rz))
    k.meta.update(vki_kind="IronStock", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=0.28,
                  vki_use=[[0.0, -0.65, 0]])


# ---------------------------------------------------------------- ToolWall_150
def vki_smy_toolwall(k):
    """ToolWall_150 (1.20 x 0.14, board z 1.10-2.30, wall_hung): a board of four vertical planks with two battens and
    pegs; tongs, hammers, a file and horseshoes hang on the pegs. Back (wall side) at local y +0.07."""
    vs = list(set(k.box((0.0, 0.0525, 1.70), (1.20, 0.035, 1.20), PLANKS, bevel=0.008)))
    for f in vki_tav_faces(vs):
        vki_tav_uv(k, [f], PLANKS, (1, 0, 0), (0, 0, 1), tile=2.4, off=(0.25, 0.0))    # four 0.30 planks
    k.set_dark(vs, 0.10)
    for zb in (1.34, 2.10):
        vki_tav_slab(k, (0.0, 0.025, zb), (1.16, 0.02, 0.08), mi=WOOD, bevel=0.006, along=(1, 0, 0))
    pegs = [(-0.42, 2.10), (-0.26, 2.10), (-0.08, 2.10), (0.12, 2.10), (0.30, 2.10), (0.47, 2.10),
            (-0.30, 1.34), (0.05, 1.34), (0.36, 1.34)]
    for (x, z) in pegs:
        k.box((x, -0.005, z + 0.015), (0.022, 0.07, 0.022), WOOD, bevel=0.004)
    for x in (-0.42, -0.26):                                                          # tongs
        vki_smy_tongs(k, Matrix.Translation((x, -0.035, 2.13)), L=0.46)
    for x, s in ((-0.08, 1.0), (0.12, 1.15), (0.30, 0.9)):                            # hammers, head up
        k.box((x, -0.035, 2.075), (0.13 * s, 0.040, 0.045 * s), IRON, bevel=0.005)
        k.box((x, -0.035, 2.075 - 0.17 * s), (0.028, 0.022, 0.30 * s), WOOD, bevel=0.004)
    k.box((0.47, -0.030, 1.93), (0.030, 0.008, 0.30), STEEL, bevel=0.0)             # file
    k.box((0.47, -0.030, 1.745), (0.026, 0.020, 0.10), WOOD, bevel=0.003)
    for i, (x, dy) in enumerate(((-0.30, -0.022), (0.05, -0.022), (0.075, -0.040))):   # horseshoes on the low pegs
        vki_smy_horseshoe(k, Matrix.Translation((x, dy, 1.33)) @ Matrix.Rotation(0.12 * (i - 1), 4, "Y"))
    vki_smy_tongs(k, Matrix.Translation((0.36, -0.035, 1.39)), L=0.23)                # jaws end at z 1.12
    k.meta.update(vki_kind="ToolWall", vki_tier="furniture", vki_mount="wall_hung", vki_back_y=0.07,
                  vki_mount_zmin=1.10, vki_mount_zmax=2.30, vki_nav="none",
                  vki_note="authored at its real height (placer z 0); Full walls only (R-occ4)")


# ---------------------------------------------------------------- GoodsRack_150
def vki_smy_goodsrack(k):
    """GoodsRack_150 (1.20 x 0.40 x 1.80, wall_floor): open shelving (uprights, four scrubbed shelves with pale front
    edges, a top board, back rails) holding iron pots, stacks of turned bowls and tools; more on the top board"""
    for sx in (-1, 1):
        vs = list(set(k.box((sx * 0.5775, 0.0, 0.8825), (0.045, 0.40, 1.765), WOOD, bevel=0.012)))
        vki_tav_hewn_tops(k, vs)
    front = lambda n: n.y < -0.3
    for zt in (0.10, 0.62, 1.14, 1.66):
        vki_tav_slab(k, (0.0, 0.0, zt - 0.0175), (1.11, 0.38, 0.035), bevel=0.008, along=(1, 0, 0), edge_ok=front)
    vki_tav_slab(k, (0.0, 0.0, 1.7825), (1.20, 0.40, 0.035), bevel=0.008, along=(1, 0, 0))   # top board
    for zc in (0.38, 0.90, 1.42):
        k.box((0.0, 0.19, zc), (1.11, 0.02, 0.04), WOOD, bevel=0.0)                       # back rails
    # goods: shelf 1 (0.10) a big pot + tongs; shelf 2 (0.62) two pots; shelf 3 (1.14) bowls + a hammer; top: bowls
    vki_smy_pot(k, -0.25, -0.02, 0.10, 0.17, 0.26)
    vki_smy_box_rot(k, (0.12, -0.10, 0.108), (0.46, 0.06, 0.108), 0.016, 0.016, IRON, bevel=0.0)
    vki_smy_box_rot(k, (0.12, -0.05, 0.116), (0.46, 0.10, 0.116), 0.016, 0.016, IRON, bevel=0.0)
    vki_smy_pot(k, -0.28, 0.0, 0.62, 0.13, 0.19)
    vki_smy_pot(k, 0.22, -0.01, 0.62, 0.11, 0.16)
    vki_smy_bowls(k, -0.24, -0.02, 1.14, 0.14)
    vki_smy_hammer(k, 0.24, -0.02, 1.14, rz=1.75)
    vki_smy_bowls(k, 0.20, 0.0, 1.80, 0.15)
    k.meta.update(vki_kind="GoodsRack", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=0.20,
                  vki_use=[[0.0, -0.65, 0]], vki_note="1.80 tall: against a Full north wall (R-occ2)")


# ---------------------------------------------------------------- Workbench_Carpenter
def vki_smy_carpenter(k):
    """Workbench_Carpenter (2.40 x 0.90 x 0.95, wall_floor): thick scrubbed top with pale edges, a tool tray and back
    board, splayed legs, stretchers and a shelf of boards; a wooden leg vice on the front-left leg; two wooden planes,
    a mallet, a square, chisels in the tray, curly shavings"""
    vki_tav_slab(k, (0.0, -0.075, 0.82), (2.40, 0.59, 0.12), bevel=0.02)                # top y -0.37..0.22
    vki_tav_slab(k, (0.0, 0.32, 0.78), (2.36, 0.20, 0.04), bevel=0.006)                 # tray floor y 0.22..0.42
    vki_tav_slab(k, (0.0, 0.435, 0.85), (2.40, 0.03, 0.18), mi=WOOD, bevel=0.006, along=(1, 0, 0))   # back board
    for sx in (-1, 1):
        k.box((sx * 1.19, 0.32, 0.82), (0.02, 0.20, 0.12), WOOD, bevel=0.0)            # tray ends
    vki_smy_frame(k, 1.02, (-0.26, 0.30), 0.76, w=0.13)
    vki_tav_slab(k, (0.0, 0.02, 0.255), (1.96, 0.60, 0.03), bevel=0.006)               # shelf on the stretchers
    for (x, y, z, L) in ((-0.10, -0.05, 0.285, 1.60), (0.05, 0.06, 0.315, 1.40)):       # boards stacked on it
        vki_tav_slab(k, (x, y, z), (L, 0.22, 0.03), mi=WOOD, bevel=0.0, along=(1, 0, 0))
    # wooden leg vice on the front-left leg (x -1.02): chop, screw into the leg, boss, tommy bar, parallel guide
    xv = -1.02
    k.box((xv, -0.40, 0.4475), (0.14, 0.06, 0.855), WOOD, bevel=0.012)                  # chop y -.43..-.37, z .02..875
    vki_tav_rod(k, (xv, -0.42, 0.62), (xv, -0.28, 0.62), 0.030, WOOD)
    vki_tav_rod(k, (xv, -0.427, 0.62), (xv, -0.438, 0.62), 0.042, WOOD)
    vki_tav_rod(k, (xv - 0.16, -0.4325, 0.62), (xv + 0.16, -0.4325, 0.62), 0.012, WOOD)
    k.box((xv, -0.305, 0.12), (0.05, 0.23, 0.04), WOOD, bevel=0.004)                   # parallel guide (in the chop)
    # planes (beech: HEWN bodies), iron wedges and blades
    for (x, y, rz, L, s) in ((0.30, -0.14, 0.12, 0.42, 1.0), (-0.40, -0.02, -0.35, 0.24, 0.9)):
        M = Matrix.Translation((x, y, 0.88)) @ Matrix.Rotation(rz, 4, "Z")
        k.box((0.0, 0.0, 0.0), (L, 0.075 * s, 0.07 * s), HEWN, bevel=0.008, xform=M @ Matrix.Translation((0, 0, 0.035 * s)))
        k.box((0.0, 0.0, 0.0), (0.012, 0.05 * s, 0.07), IRON, bevel=0.002,
              xform=M @ Matrix.Translation((0.03 * s, 0.0, 0.07 * s)) @ Matrix.Rotation(0.7, 4, "Y"))
        if L > 0.3:
            k.box((0.0, 0.0, 0.0), (0.10, 0.03, 0.07), HEWN, bevel=0.0,
                  xform=M @ Matrix.Translation((-0.11, 0.0, 0.095)))                      # tote
            k.box((0.0, 0.0, 0.0), (0.04, 0.04, 0.04), HEWN, bevel=0.0,
                  xform=M @ Matrix.Translation((0.14, 0.0, 0.085)))                       # front knob
    Mm = Matrix.Translation((0.85, 0.02, 0.88)) @ Matrix.Rotation(-0.5, 4, "Z")         # mallet
    k.box((0.0, 0.0, 0.0), (0.15, 0.085, 0.085), WOOD, bevel=0.012, xform=Mm @ Matrix.Translation((0, 0.15, 0.0425)))
    k.box((0.0, 0.0, 0.0), (0.032, 0.30, 0.028), WOOD, bevel=0.0, xform=Mm @ Matrix.Translation((0, -0.02, 0.02)))
    Ms = Matrix.Translation((-0.85, -0.16, 0.88)) @ Matrix.Rotation(0.3, 4, "Z")         # try square
    k.box((0.0, 0.0, 0.0), (0.26, 0.03, 0.012), STEEL, bevel=0.0, xform=Ms @ Matrix.Translation((0.13, 0.0, 0.009)))
    k.box((0.0, 0.0, 0.0), (0.034, 0.16, 0.022), WOOD, bevel=0.0,
          xform=Ms @ Matrix.Translation((0.0, 0.06, 0.011)))                            # stock: faces off the blade's
    for i, (x, y) in enumerate(((-0.60, 0.27), (-0.35, 0.31), (-0.10, 0.35))):          # chisels in the tray
        k.box((x, y, 0.8125), (0.12, 0.028, 0.025), WOOD, bevel=0.0)
        k.box((x + 0.11, y, 0.803), (0.10, 0.020, 0.006), STEEL, bevel=0.0)
    for (x, y, r, w, tr, rz) in ((0.02, -0.28, 0.030, 0.050, 1.3, 0.4), (0.12, -0.24, 0.026, 0.045, 1.2, 1.9),
                                 (-0.08, -0.22, 0.032, 0.055, 1.4, -0.5), (0.58, -0.26, 0.028, 0.048, 1.25, 2.6),
                                 (0.46, 0.00, 0.025, 0.040, 1.2, 0.9), (-0.15, -0.32, 0.024, 0.045, 1.1, 3.0)):
        vki_smy_curl(k, (x, y, 0.88), r, w, tr, rz, n=5)
    k.meta.update(vki_kind="Workbench_Carpenter", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=0.45,
                  vki_use=[[0.0, -0.80, 0], [-1.02, -0.80, 0]], vki_note="wooden leg vice on the front-left leg")


# ---------------------------------------------------------------- PoleLathe
def vki_smy_polelathe(k):
    """PoleLathe (2.40 x 0.90 x 2.20, wall_floor): a bed of two rails on splayed trestles, two poppets with iron
    centres holding a spindle being turned (pale), a tool rest, a treadle hinged at the back, the cord from the treadle
    round the spindle to the tip of the spring pole, which is lashed to a post at the back left and bows over the
    work; shavings on the floor"""
    for sy in (-1, 1):                                                                 # bed rails y +-(0.05..0.13)
        vki_tav_slab(k, (0.06, sy * 0.09, 0.90), (2.28, 0.08, 0.12), mi=WOOD, bevel=0.012, along=(1, 0, 0))
    sp = VKI_SMY_LEG_SPLAY; sy_ = math.tan(math.radians(7.5))
    for x in (-0.78, 0.92):
        for sy in (-1, 1):
            vki_tav_leg(k, x, sy * 0.09, 0.0, 0.84, 0.09, sx=math.copysign(sp, x) * 0.6, sy=sy * sy_)
        yb = 0.09 + sy_ * (0.84 - 0.35)
        k.box((x + math.copysign(sp, x) * 0.6 * (0.84 - 0.35), 0.0, 0.35), (0.06, 2 * yb, 0.06), WOOD, bevel=0.006)
    xl, xr, zc = -0.24, 0.42, 1.14
    for x in (xl - 0.06, xr + 0.06):                                                   # poppets through the slot
        vs = list(set(k.box((x, 0.0, 0.98), (0.12, 0.10, 0.52), WOOD, bevel=0.010)))
        vki_tav_hewn_tops(k, vs)
    vki_tav_lathe(k, [(0.018, 0.0), (0.003, 0.04)], IRON, seg=8,
                  M=Matrix.Translation((xl, 0.0, zc)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))      # left centre
    vki_tav_lathe(k, [(0.018, 0.0), (0.003, 0.04)], IRON, seg=8,
                  M=Matrix.Translation((xr, 0.0, zc)) @ Matrix.Rotation(-math.pi / 2, 4, "Y"))     # right centre
    a0, a1 = xl + 0.035, xr - 0.035                                                    # the spindle, tips embedded
    L = a1 - a0
    prof = [(0.030, 0.0), (0.040, 0.13 * L), (0.030, 0.30 * L), (0.045, 0.43 * L), (0.030, 0.57 * L),
            (0.040, 0.77 * L), (0.040, 0.94 * L), (0.030, L)]
    vki_tav_lathe(k, prof, HEWN, M=Matrix.Translation((a0, 0.0, zc)) @ Matrix.Rotation(math.pi / 2, 4, "Y"),
                  sharp_deg=40.0)
    k.box(((xl + xr) / 2, -0.075, 1.10), (xr - xl + 0.12, 0.035, 0.03), WOOD, bevel=0.004)   # tool rest
    for x in (xl - 0.06, xr + 0.06):
        k.box((x, -0.06, 1.10), (0.03, 0.03, 0.024), WOOD, bevel=0.0)                       # its arms (tops below)
    # treadle hinged on a floor block at the back, its front end held up by the cord
    xt = 0.10
    k.box((xt, 0.38, 0.03), (0.22, 0.08, 0.06), WOOD, bevel=0.006)
    th = math.atan2(0.20, 0.74)
    k.box((0.0, 0.0, 0.0), (0.12, 0.77, 0.03), WOOD, bevel=0.006,
          xform=Matrix.Translation((xt, -0.01, 0.145)) @ Matrix.Rotation(-th, 4, "X"))
    # the spring pole: post with a foot block at the back left, a bowed pole from the post top over the work
    k.box((-1.10, 0.35, 0.04), (0.20, 0.20, 0.08), WOOD, bevel=0.008)                  # x -1.20..-1.00
    vs = list(set(k.box((-1.13, 0.35, 1.05), (0.12, 0.12, 2.06), WOOD, bevel=0.012)))  # post z 0.02..2.08
    vki_tav_hewn_tops(k, vs)
    p0, pc, p1 = Vector((-1.13, 0.35, 1.97)), Vector((-0.45, 0.24, 2.24)), Vector((xt, 0.02, 2.16))
    pts = [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * pc + t * t * p1 for t in [i / 6 for i in range(7)]]
    vki_smy_sweep(k, pts, [0.050 - 0.0053 * i for i in range(7)], HEWN)
    vki_tav_rod(k, (xt, -0.365, 0.265), (xt, -0.033, zc - 0.03), 0.006, BURLAP, seg=6)    # cord: treadle -> spindle
    vki_tav_rod(k, (xt, 0.033, zc + 0.03), (xt, 0.02, 2.15), 0.006, BURLAP, seg=6)         # spindle -> pole tip
    rnd = random.Random(4417)
    for i in range(9):                                                                     # shavings on the floor
        c = (rnd.uniform(-0.30, 0.55), rnd.uniform(-0.36, -0.16), 0.0)
        if abs(c[0] - xt) < 0.10:
            continue
        r = rnd.uniform(0.022, 0.034)
        vs = _ico(k, (0.0, 0.0, 0.0), r, HEWN, scale=(1.3, 0.8, 0.45), sub=0, jit=0.003, seed=4420 + i)
        bmesh.ops.transform(k.bm, matrix=Matrix.Translation((c[0], c[1], 0.45 * r)) @
                            Matrix.Rotation(rnd.uniform(0, 3.1), 4, "Z"), verts=vs)
        k.bm.normal_update()
        k.project(vki_tav_faces(vs), HEWN)
    k.meta.update(vki_kind="PoleLathe", vki_tier="furniture", vki_mount="wall_floor", vki_back_y=0.45,
                  vki_use=[[xt, -0.70, 0]], vki_note="2.2 tall: against a Full north wall (R-occ2); the pole tip at "
                                                        "z 2.16 stays over the lathe, not over a walk lane (R-occ3)")


# ---------------------------------------------------------------- workshop assemblies (renders for the hand-in)
# Everything below builds instances in WS_vki_tavern_Assembly with vki_place (Timber walls, posts and floors from
# VKI_Pieces as backdrop); nothing here touches a master. Shots: vki_ws_shot("tavern", name, "game", D=, target=).
VKI_SMY_WS = "tavern"
VKI_SMY_W, VKI_SMY_P, VKI_SMY_T = "SM_VKI_Wall_Timber_", "SM_VKI_Post_Timber_", "SM_VKI_Prop_"


def vki_smy_ws_build(names):
    """vki_ws_build for this package's masters, except that each temp object is finished into WS_vki_tavern_Tmp, a
    collection linked to no scene, instead of WS_vki_tavern_Pieces. The coordinator's board scene instances the pieces
    collection in a RENDERED viewport; a temp object appearing and vanishing inside an instanced collection within one
    call is a likely trigger of the 14:51 viewport crash (EEVEE draw: deg_iterator_objects_step). Same ownership guard
    as vki_ws_build; the master mesh is updated in place (vki_copy_into), so instances follow."""
    sc, coll, asm = vki_ws(VKI_SMY_WS)
    tc = bpy.data.collections.get("WS_vki_tavern_Tmp") or bpy.data.collections.new("WS_vki_tavern_Tmp")
    sm = vki_spec_map()
    built = []
    for n in ([names] if isinstance(names, str) else names):
        if n not in sm or not n.startswith("SM_VKI_"):
            raise KeyError(f"not a VKI spec: {n}")
        _, fn, kw, pkg = sm[n]
        base = bpy.data.objects.get(n)
        if base is not None and [c_.name for c_ in base.users_collection] != [coll.name]:
            raise RuntimeError(f"{n} already exists in {[c_.name for c_ in base.users_collection]}: not yours")
        tmp = vki_build_tmp(n, fn, kw, tc, "__vki_wstmp_tavern")
        if base is None:
            tmp.name = n; tmp.data.name = n
            coll.objects.link(tmp); tc.objects.unlink(tmp)
            base = tmp
        else:
            vki_copy_into(base, tmp)
        built.append(base)
    return built


def vki_smy_ws_coll(name):
    """a cleared child collection of WS_vki_tavern_Assembly (light objects removed; their datablocks are left for
    the save's orphan purge rather than removed under a rendered viewport)"""
    sc, coll, asm = vki_ws(VKI_SMY_WS)
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [ch.name for ch in asm.children]:
        asm.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o)
    return c


def vki_smy_ws_place(c, items, ox=0.0, oy=0.0):
    """place [(piece, x, y, rot[, kw])] (room coordinates + (ox, oy)) in order: the walls and posts placed so far
    steer the wall_floor / wall_hung mounts and hug; returns the objects"""
    struct, out = [], []
    for it in items:
        piece, x, y, rot = it[:4]
        kw = dict(it[4]) if len(it) > 4 else {}
        o = vki_place(c, piece, ox + x, oy + y, rot, walls=struct, **kw)
        if o.get("vki_class") in ("wall", "post"):
            struct.append(o)
        out.append(o)
    return out


def vki_smy_ws_lights(c):
    """Blender lights from the placed props' vki_lights (vki_lt_lights, the look-test reference), kept in the room's
    own collection so each room is one collection on the coordinator's board"""
    return vki_lt_lights(bpy.data.scenes["WS_vki_" + VKI_SMY_WS], c, c)


def vki_smy_ws_row(gap=0.6):
    """lay the masters of WS_vki_tavern_Pieces out in one row along +X from the origin (y 0), in VKI_TAV_NAMES +
    VKI_SMY_NAMES order, `gap` apart by their bounding boxes (the board scene shows this collection as a row). The
    workshop rooms sit at y >= 10, north of the row, so the row never enters their game-camera frames."""
    sc, coll, asm = vki_ws(VKI_SMY_WS)
    x = 0.0
    for n in VKI_TAV_NAMES + VKI_SMY_NAMES:
        o = bpy.data.objects.get(n)
        if o is None or coll.name not in [c_.name for c_ in o.users_collection]:
            continue
        bx = vki_local_box(o)
        o.location = (x - bx[0], 0.0, 0.0)
        o.rotation_euler = (0.0, 0.0, 0.0)
        x += (bx[3] - bx[0]) + gap
    return x


def vki_smy_ws_floor(x0, y0, nx, ny, style):
    return [(p, x - x0, y - y0, r, {"style": st}) for (p, x, y, r, st) in vki_c3_floor_pieces(x0, y0, nx, ny, style)]


def vki_smy_ws_catalogs():
    """three catalog rooms (12 x 6 m, Full north wall of Plain_300, Corner posts at the ends, Mid at x 6):
    tavern set at (0, 12), smithy set at (0, 30), workshop set at (18, 30) (even nodes, so floors tile from Floor_600).
    Returns {name: (D, target)}."""
    W, P, T = VKI_SMY_W, VKI_SMY_P, VKI_SMY_T
    wall = [(W + "Plain_300_Full", x, 6.0, 0) for x in (0, 3, 6, 9)] + \
        [(P + "Corner_Full", 0, 6, 0), (P + "Corner_Full", 12, 6, 0), (P + "Mid_Full", 6, 6, 0)]
    rooms = {
        "WS_vki_tavern_CatTavern": ((0.0, 12.0), "Boards_EW", [
            (T + "CaskRack_150", 1.5, 5.25, 0), (T + "Lantern_Wall", 3.75, 5.25, 0), (T + "Lantern_Wall", 8.25, 5.25, 0),
            (T + "CaskRack_150", 10.5, 5.25, 0),
            (T + "Bar_End_150", 2.25, 3.75, 0), (T + "Bar_Counter_150", 3.75, 3.75, 0),
            (T + "Bar_Counter_150", 5.25, 3.75, 0),
            (T + "Candlestick", 4.3, 3.95, 0, {"z": 1.05}), (T + "Candle_Plate", 5.7, 3.9, 0, {"z": 1.05}),
            (T + "Table_Barrel", 7.5, 3.75, 0), (T + "TableDress_Tavern_C", 7.5, 3.75, 0, {"z": 1.05}),
            (T + "Table_Trestle_300", 3.0, 1.5, 0), (T + "TableDress_Tavern_A", 3.0, 1.5, 0, {"z": 0.80}),
            (T + "Form_300", 3.0, 0.75, 0), (T + "Form_300", 3.0, 2.25, 0),
            (T + "Table_Trestle_300", 8.25, 1.5, 0), (T + "TableDress_Tavern_B", 8.25, 1.5, 0, {"z": 0.80}),
            (T + "Form_300", 8.25, 0.75, 0), (T + "Form_300", 8.25, 2.25, 0)]),
        "WS_vki_tavern_CatSmithy": ((0.0, 30.0), "EarthSooty", [
            (T + "Workbench_300", 1.5, 5.25, 0), (T + "CoalBin_150", 3.75, 5.25, 0),
            (T + "GoodsRack_150", 5.25, 5.25, 0), (T + "IronStock_150", 6.75, 5.25, 0),
            (T + "ToolWall_150", 8.25, 5.25, 0), (T + "ToolWall_150", 9.75, 5.25, 0),
            (T + "QuenchTrough_150", 4.5, 3.0, 0), ("SM_VK_Prop_Anvil", 6.75, 3.0, 0)]),
        "WS_vki_tavern_CatWorkshop": ((18.0, 30.0), "FlagRustic", [
            (T + "Workbench_Carpenter", 1.5, 5.25, 0), (T + "GoodsRack_150", 3.75, 5.25, 0),
            (T + "PoleLathe", 7.5, 5.25, 0), (T + "ToolWall_150", 10.5, 5.25, 0)]),
    }
    out = {}
    for name, ((ox, oy), fl, props) in rooms.items():
        c = vki_smy_ws_coll(name)
        # floor zone offset so floor parity follows world nodes (ox, oy are multiples of 1.5)
        vki_smy_ws_place(c, vki_smy_ws_floor(ox, oy, 8, 4, {"floor": fl}) + wall + props, ox, oy)
        vki_smy_ws_lights(c)
        out[name] = (16.0, (ox + 6.0, oy + 3.3, 0.0))
    return out


def vki_smy_ws_bar_corner(ox=0.0, oy=51.0):
    """the Tavern_F0 bar corner (§6, x - 9: cols 6-8, rows 0-4) in Timber: east wall Full (Plain_300 x 2 + Rake_R),
    north wall Full, the kitchen partition Cut at y 6, south wall Cut; Corner / Mid posts by §2.3 (rhythm Mids where
    no wall-backed prop spans the node); Flag floor; the prop list of §6 translated (counters, bar end, cask racks,
    lanterns on the east wall) plus a barrel table with TableDress_Tavern_C and candles on the bar.
    Returns (D, target) of the §1 fit camera."""
    W, P, T = VKI_SMY_W, VKI_SMY_P, VKI_SMY_T
    c = vki_smy_ws_coll("WS_vki_tavern_BarCorner")
    items = vki_smy_ws_floor(ox, oy, 3, 5, {"floor": "Flag"}) + [
        (W + "Plain_150A_Full", 0, 7.5, 0), (W + "Plain_300_Full", 1.5, 7.5, 0),
        (W + "Plain_300_Full", 4.5, 7.5, -90), (W + "Plain_300_Full", 4.5, 4.5, -90), (W + "Rake_150_R", 4.5, 1.5, -90),
        (W + "Plain_300_Cut", 4.5, 0, 180), (W + "Plain_150A_Cut", 1.5, 0, 180), (W + "Plain_300_Cut", 1.5, 6.0, 0),
        (P + "Corner_Full", 4.5, 7.5, 0), (P + "Corner_Full", 4.5, 6.0, 0), (P + "Corner_Cut", 4.5, 0, 0),
        (P + "Mid_Full", 0, 7.5, 0), (P + "Mid_Cut", 0, 0, 0), (P + "Mid_Cut", 1.5, 6.0, 0),
        (P + "Mid_Full", 3.0, 7.5, 0), (P + "Mid_Full", 4.5, 3.0, 90), (P + "Mid_Cut", 3.0, 0, 0),
        (P + "Mid_Cut", 3.0, 6.0, 0),
        (T + "Bar_Counter_150", 2.25, 2.25, -90), (T + "Bar_Counter_150", 2.25, 3.75, -90),
        (T + "Bar_End_150", 2.25, 5.25, -90),
        (T + "CaskRack_150", 3.75, 2.25, -90), (T + "CaskRack_150", 3.75, 3.75, -90),
        (T + "Lantern_Wall", 3.75, 2.25, -90), (T + "Lantern_Wall", 3.75, 3.75, -90),
        (T + "Candlestick", 2.20, 2.75, 0, {"z": 1.05}), (T + "Candle_Plate", 2.30, 4.05, 0, {"z": 1.05}),
        (T + "Table_Barrel", 0.75, 3.75, 0), (T + "TableDress_Tavern_C", 0.75, 3.75, 0, {"z": 1.05})]
    vki_smy_ws_place(c, items, ox, oy)
    vki_smy_ws_lights(c)
    fit = vki_fit_camera((ox, oy, ox + 4.5, oy + 7.5), "Timber")
    return fit["D"], fit["target"]


def vki_smy_ws_smithy_corner(ox=21.0, oy=51.0):
    """the Smithy_F0 north-east corner (§6, x - 6: cols 4-6, rows 0-4) in Timber (the smithy itself is Stone, PKG-S):
    north wall Full with a window over the coal bin, east wall Full (Plain_300 x 2 + Rake_R), south wall Cut; posts by
    §2.3 (no rhythm Mids at east y 3.0 and north x 3.0: the workbench and the hugged goods rack span those nodes);
    EarthSooty floor; the §6 props translated (coal bin,
    goods rack, quench trough, workbench, two tool walls) plus the iron stock and the reused anvil.
    Returns (D, target) of the §1 fit camera."""
    W, P, T = VKI_SMY_W, VKI_SMY_P, VKI_SMY_T
    c = vki_smy_ws_coll("WS_vki_tavern_SmithyCorner")
    items = vki_smy_ws_floor(ox, oy, 3, 5, {"floor": "EarthSooty"}) + [
        (W + "Plain_150A_Full", 0, 7.5, 0), (W + "Window_150_Full", 1.5, 7.5, 0), (W + "Plain_150A_Full", 3.0, 7.5, 0),
        (W + "Plain_300_Full", 4.5, 7.5, -90), (W + "Plain_300_Full", 4.5, 4.5, -90), (W + "Rake_150_R", 4.5, 1.5, -90),
        (W + "Plain_300_Cut", 4.5, 0, 180), (W + "Plain_150A_Cut", 1.5, 0, 180),
        (P + "Corner_Full", 4.5, 7.5, 0), (P + "Corner_Cut", 4.5, 0, 0), (P + "Mid_Full", 0, 7.5, 0),
        (P + "Mid_Cut", 0, 0, 0), (P + "Mid_Cut", 3.0, 0, 0),         # no rhythm Mid at north x 3.0: the hugged
        # goods rack spans that node (§2.3 skip rule; vki_place's hug does not re-check posts after its slide)
        (T + "CoalBin_150", 2.25, 6.75, 0), (T + "GoodsRack_150", 3.75, 6.75, 0), (T + "IronStock_150", 0.75, 6.75, 0),
        (T + "QuenchTrough_150", 2.25, 5.25, 0), (T + "Workbench_300", 3.75, 3.0, -90),
        (T + "ToolWall_150", 3.75, 2.25, -90), (T + "ToolWall_150", 3.75, 3.75, -90),
        ("SM_VK_Prop_Anvil", 0.75, 4.5, 0)]
    vki_smy_ws_place(c, items, ox, oy)
    vki_smy_ws_lights(c)
    fit = vki_fit_camera((ox, oy, ox + 4.5, oy + 7.5), "Timber")
    return fit["D"], fit["target"]


VKI_SMY_SPECS = [
    ("SM_VKI_Prop_Workbench_300", vki_smy_workbench),
    ("SM_VKI_Prop_QuenchTrough_150", vki_smy_quench),
    ("SM_VKI_Prop_CoalBin_150", vki_smy_coalbin),
    ("SM_VKI_Prop_IronStock_150", vki_smy_ironstock),
    ("SM_VKI_Prop_ToolWall_150", vki_smy_toolwall),
    ("SM_VKI_Prop_GoodsRack_150", vki_smy_goodsrack),
    ("SM_VKI_Prop_Workbench_Carpenter", vki_smy_carpenter),
    ("SM_VKI_Prop_PoleLathe", vki_smy_polelathe),
]
VKI_SMY_NAMES = [n for n, _ in VKI_SMY_SPECS]
vki_register([(n, fn, {"grime": "prop"}, "tavern") for n, fn in VKI_SMY_SPECS])
