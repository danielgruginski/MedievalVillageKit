# ===================== VKI FAM ASHLAR: the Ashlar wall family (§2.2, §3.1, §3.2) -- 12 masters =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (its §10 overrides). Package "wattle" (PACKAGES.md).
# Loaded by vki_ns() after vki_fam_timber (generic helpers vki_cut, vki_prism, vki_proj_long, vki_hash_off,
# vki_faces_of, vki_tim_member are used at build time). It does not depend on vki_fam_wattle.
# Every top-level name starts with vki_/VKI_ (T18).
#
# Section (class O, T 0.50, H 4.5), piece-local, room on -Y:
#   body  AshlarIn +-0.25 (WALL_A / WALL_B; horizontal faces switch to STONE_BLOCK_IN), z -0.30 .. cap bottom,
#         grid_cut 0.25 (+ rows at 0.90 / 2.90 on Full-height panels), §2.6 wobble A 0.010 (flat at the courses and
#         around openings)
#   DRESS string course 0.90 .. 1.00, +-0.28 with a weathered top (front 0.065 tall, then sloping up to +-0.23 at
#         1.00; the top faces CAP): the Cut cap, and the same course on Full walls
#   Full: second string course 2.90 .. 3.00 (same profile), cornice 4.38 .. 4.50 (chamfered underside, CAP top)
#   Lancet_150 / LancetTall_150: glass x 0.45-1.05 at y +0.15 (STAINED, closed 0.02 plate, edges buried 1 cm), spring
#     3.00 / 3.30, glass apex 3.465 / 3.765; splayed to x 0.33-1.17 at face A, apex 3.65 / 3.95; sill 1.00 = the
#     course; 3 iron saddle bars; DRESS surround on face A: 3 long-and-short jamb stones a side + 3 voussoirs an arc
#     meeting at a vertical apex joint. The second course dies into the top jamb stones.
#     Lancet_150_Cut: the lower metre + a DRESS sill slab over x 0.33-1.17 + a light-pool anchor.
#   DoorWide_300: pointed lancet_pts(0.70, 2.30, 0, 2.20) (apex 3.44), two DRESS orders: the inner order (jambs
#     x 0.54-0.70, ring r..r+0.16) behind a step at y -0.09, the outer order (jambs x 0.42-0.54, ring r+0.16..r+0.28)
#     full depth; DRESS threshold. Cut: the lower metre, the cap course runs from the piece end to the opening.
#   No B variant, no rake (pillars: Full plain piece + Full Corner post, §2.4).
#   Posts (DRESS): Corner = clustered respond +-0.31: base, core +-0.255 with 4 engaged shafts (r 0.095 on the axes),
#     flared capital, abacus with a CAP top. Mid (Full only) = shaft respond +-0.12 x +-0.31: one shaft a face.
# Build (package engineer): g["vki_ws_build"]("wattle", VKI_ASH_NAMES); test: g["vki_test_pieces"](VKI_ASH_NAMES).
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_ASH_HW = 0.28                       # courses / cornice front (= CAP_HW, class O)
VKI_ASH_COURSES = ((0.90, 1.00), (2.90, 3.00))
VKI_ASH_CORNICE = (4.38, 4.50)
VKI_ASH_WEATHER = (0.065, 0.23)         # course: vertical front 0.065, then the weathered top rises to (+-0.23, top)
# course / cornice bevel: none -- the courses butt flush into one continuous band, and an 8 mm bevel (under 1 px at
# the chapel's D 21.9) cost ~40 tris a course (the lancets must stay within T9's 1500)
VKI_ASH_CBEV = 0.0
VKI_ASH_TUCK = 0.005
VKI_ASH_CUT_TO = "SM_VKI_Wall_Ashlar_Plain_150A_Cut"
# lancets (§3.2): glass, splay at face A, sill; spring and the top of the arch solids per kind
VKI_ASH_LANCET = dict(glass=(0.45, 1.05), glass_y=0.15, splay=(0.33, 1.17), sill=1.00, n=5)   # n: segments an arc
VKI_ASH_SPRING = {"Lancet": 3.00, "LancetTall": 3.30}
VKI_ASH_TOPZ = {"Lancet": 3.75, "LancetTall": 4.05}   # above the room-face apex (3.651 / 3.951)
VKI_ASH_BARS = {"Lancet": (1.55, 2.10, 2.65), "LancetTall": (1.60, 2.20, 2.80)}
# DRESS surround on face A: stones 2 cm proud (y -0.27, 5 mm into the body), long / short jamb stones, voussoirs.
# The jamb stones are plain boxes (T9 budget) whose fronts alternate: long stones 2 cm proud, short 1.5 cm (front_s),
# so their joints read by the step; the voussoirs keep a bevel (it draws the radial joints)
VKI_ASH_SURROUND = dict(y=(-0.27, -0.245), front_s=-0.265, jamb_w=(0.20, 0.13), vous_w=0.17, n_jamb=3, n_vous=3,
                        bev=0.012)
VKI_ASH_COURSE2_END = 0.14              # the second course runs 5 mm into the top (long) jamb stone
# lancet spot, tinted by the glass (§6 "Lancets: spots tinted by the glass"): through the glass onto the floor
VKI_ASH_LANCET_SPOT = dict(pos=(0.75, 2.2, 5.0), aim=(0.75, -1.6, 0.0), cone=24.0, blend=0.15, radius=0.05,
                           w_day=800.0, w_night=120.0, color_day=[1.0, .86, .72], color_night=[.66, .62, .95])
# wide door (§3.2): opening lancet_pts(0.70, 2.30, 0, 2.20); orders d1 / d2 outside it; the inner order's step
VKI_ASH_DOOR = dict(x=(0.70, 2.30), spring=2.20, d1=0.16, d2=0.28, step_y=-0.09, thr=0.03, n=4, topz=3.85)


# ---------------------------------------------------------------- building blocks
def vki_ash_body(k, x0, x1, z0, z1):
    """an ashlar body panel (k.body_box, grid 0.25); Full-height panels also get rows at 0.90 / 2.90 (course
    bottoms), so the wobble goes flat right at the courses (every Full piece has them at its ends: T2)"""
    vs = k.body_box(x0, x1, z0, z1)
    cuts = [c for c in (VKI_ASH_COURSES[0][0], VKI_ASH_COURSES[1][0]) if z0 + 0.05 < c < z1 - 0.05]
    if cuts:
        vs = vki_cut(k, vs, zs=cuts)
        k.mark_body(vs)
    return vs


def vki_ash_dress_uv(k, fs, c):
    """DRESS faces planar at t 1.5 (continuous over 1.5 m butt joints, like the Timber footing); upward faces
    (n.z > 0.65) CAP with the grain along the wall"""
    k.bm.normal_update()
    tops = [f for f in fs if f.normal.z > 0.65]
    for f in fs:
        if f not in tops:
            k.project([f], DRESS, tile=1.5)
    vki_proj_long(k, tops, VKI_CAP, VKI_TIM_X, off=vki_hash_off(c))


def vki_ash_course(k, x0, x1, z0, z1):
    """DRESS string course x0..x1: +-0.28 front 0.065 tall, weathered top rising to +-0.23 at z1 (35 deg)"""
    fh, wy = VKI_ASH_WEATHER
    hw = VKI_ASH_HW
    poly = [(-hw, z0), (hw, z0), (hw, z0 + fh), (wy, z1), (-wy, z1), (-hw, z0 + fh)]
    vs, fs = vki_prism(k, poly, x0, x1, DRESS, axis="x", bevel=VKI_ASH_CBEV, project=False)
    vki_ash_dress_uv(k, fs, (x0, 0.0, z0))
    return vs


def vki_ash_cornice(k, x0, x1):
    """cornice 4.38 .. 4.50: chamfered underside from +-0.255 out to +-0.28, vertical front, flat CAP top"""
    z0, z1 = VKI_ASH_CORNICE
    hw = VKI_ASH_HW
    poly = [(-0.255, z0), (0.255, z0), (hw, z0 + 0.045), (hw, z1), (-hw, z1), (-hw, z0 + 0.045)]
    vs, fs = vki_prism(k, poly, x0, x1, DRESS, axis="x", bevel=VKI_ASH_CBEV, project=False)
    vki_ash_dress_uv(k, fs, (x0, 0.0, z0))
    return vs


def vki_ash_seg(k, pa, pb, qa, qb, ya, yb, Z):
    """convex body solid over one arch segment: its underside is the quad pa, pb (at y = ya) -> qb, qa (at y = yb)
    (parallel segments, so the quad is planar), its top the plane z = Z; vertical sides. Faces toward +Y WALL_B,
    the rest WALL_A (horizontal ones switch to STONE_BLOCK_IN on Ashlar). Returns its faces."""
    A = [Vector((pa[0], ya, pa[1])), Vector((pb[0], ya, pb[1])), Vector((qb[0], yb, qb[1])), Vector((qa[0], yb, qa[1]))]
    va = [k.bm.verts.new(p) for p in A]
    vb = [k.bm.verts.new((p.x, p.y, Z)) for p in A]
    fs = [k.bm.faces.new(va), k.bm.faces.new(vb[::-1])]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(k.bm.faces.new((va[i], va[j], vb[j], vb[i])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    k.bm.normal_update()
    for f in fs:
        k.project([f], VKI_WALL_B if f.normal.y > 0.7 else VKI_WALL_A)
    k.mark_body(va + vb)
    return fs


def vki_ash_arc(x0, x1, zs, n):
    """the arcs of lancet_pts(x0, x1, ., zs, n): right spring -> apex -> left spring, 2n + 1 points"""
    pts, za = lancet_pts(x0, x1, 0.0, zs, n)
    return pts[2:], za


def vki_ash_wobble(k, L, holes, tb):
    vki_wobble(k, L, "Ashlar", "A", holes=holes, top_body_fn=lambda x: tb, pins=())


def vki_ash_course_holes(L):
    return [(0.0, c0, L, c1) for c0, c1 in VKI_ASH_COURSES]


# ---------------------------------------------------------------- Plain (150A, 300), Full and Cut
def vki_ash_plain(k, L, height):
    full = height == "Full"
    tb = VKI_ASH_CORNICE[0] if full else VKI_ASH_COURSES[0][0]
    vki_ash_body(k, 0.0, L, VKI_FOOT_Z, tb)
    vki_ash_course(k, 0.0, L, *VKI_ASH_COURSES[0])                     # the Cut cap (also on Full walls)
    holes = []
    if full:
        vki_ash_course(k, 0.0, L, *VKI_ASH_COURSES[1])
        vki_ash_cornice(k, 0.0, L)
        holes = vki_ash_course_holes(L)
    vki_ash_wobble(k, L, holes, tb)
    k.meta.update(vki_class="wall")


def vki_ash_plain_150a_full(k): vki_ash_plain(k, 1.5, "Full")
def vki_ash_plain_150a_cut(k): vki_ash_plain(k, 1.5, "Cut")
def vki_ash_plain_300_full(k): vki_ash_plain(k, 3.0, "Full")
def vki_ash_plain_300_cut(k): vki_ash_plain(k, 3.0, "Cut")


# ---------------------------------------------------------------- Lancet_150 / LancetTall_150 (§3.2)
def vki_ash_surround(k, x0, x1, zs):
    """DRESS surround on face A around the splay edge: n_jamb long-and-short jamb stones a side from the sill to the
    spring (inner edge 5 mm over the splay edge, so no face lies in the pier's end plane), then n_vous voussoirs an
    arc (radial joints at every second splay vertex, inner edge 3 mm inside the arc) meeting at a vertical joint on
    the apex line"""
    S = VKI_ASH_SURROUND
    ya, yb = S["y"]
    sill = VKI_ASH_LANCET["sill"] - 0.01
    hs = (zs - sill) / S["n_jamb"]
    for side in (0, 1):
        for j in range(S["n_jamb"]):
            w = S["jamb_w"][j % 2]
            yf = ya if j % 2 == 0 else S["front_s"]
            za, zb = sill + j * hs, sill + (j + 1) * hs
            xa, xb = (x0 + 0.005 - w, x0 + 0.005) if side == 0 else (x1 - 0.005, x1 - 0.005 + w)
            k.box(((xa + xb) / 2, (yf + yb) / 2, (za + zb) / 2), (xb - xa, yb - yf, zb - za), DRESS, bevel=0)
    r = 0.85 * (x1 - x0); xm = (x0 + x1) / 2; cR = x1 - r
    ri, ro = r - 0.003, r + S["vous_w"]
    ta = math.acos((xm - cR) / r)
    tai, tao = math.acos((xm - cR) / ri), math.acos((xm - cR) / ro)
    m = S["n_vous"]
    for sgn, cx in ((1, cR), (-1, x0 + r)):
        for j in range(m):
            t0, t1 = ta * j / m, ta * (j + 1) / m
            ti1, to1 = (tai, tao) if j == m - 1 else (t1, t1)
            poly = [(cx + sgn * ri * math.cos(t0), zs + ri * math.sin(t0)),
                    (cx + sgn * ri * math.cos(ti1), zs + ri * math.sin(ti1)),
                    (cx + sgn * ro * math.cos(to1), zs + ro * math.sin(to1)),
                    (cx + sgn * ro * math.cos(t0), zs + ro * math.sin(t0))]
            if j == m - 1:                                           # exact apex line (the two arcs meet on it)
                poly[1] = (xm, poly[1][1]); poly[2] = (xm, poly[2][1])
            vs, fs = vki_prism(k, poly if sgn > 0 else poly[::-1], ya, yb, DRESS, axis="y", bevel=S["bev"])


def vki_ash_glass_broken(k, pts, gy, seed=7):
    """shattered glass (2026-10-17, the abandoned monastery): only a jagged rim of shards stays in the frame -- the
    outline resampled every ~0.25 m, each shard 1-3 of its segments plus a point 6-24 cm in toward the middle, a
    quarter of the stretches empty to the frame; each shard 1.5 mm off its neighbour's plane (never coplanar)"""
    rnd = random.Random(seed)
    ring = []
    for i in range(len(pts)):
        a, b = Vector(pts[i]), Vector(pts[(i + 1) % len(pts)])
        n = max(1, int((b - a).length / 0.25))
        ring += [a + (b - a) * j / n for j in range(n)]
    c = sum(ring, Vector((0.0, 0.0))) / len(ring)
    i, m, idx = 0, len(ring), 0
    while i < m:
        span = rnd.randint(1, 3)
        if rnd.random() < 0.25:
            i += span
            continue
        seg = [ring[(i + j) % m] for j in range(min(span, m - i) + 1)]
        mid = (seg[0] + seg[-1]) / 2
        q = mid + (c - mid).normalized() * rnd.uniform(0.06, 0.24)
        y0 = gy - 0.01 + 0.0015 * (idx % 4)
        vki_prism(k, [(p.x, p.y) for p in seg] + [(q.x, q.y)], y0, y0 + 0.012, STAINED, axis="y")
        i += span
        idx += 1


def vki_ash_lancet(k, kind, height, broken=False):
    """Full: piers x 0-0.33 / 1.17-1.5, the body under the sill, splayed jamb wedges and one convex solid per arch
    segment (the splay soffit from the face-A arc to the glass arc, then the outer reveal), body over the arch;
    glass, bars, surround, the courses and the cornice. Cut: the lower metre, the cap course in two pieces butting a
    DRESS sill slab over x 0.33-1.17 (|y| <= 0.28, top 1.00), a light-pool anchor."""
    L = 1.5
    full = height == "Full"
    A = VKI_ASH_LANCET
    x0, x1 = A["splay"]; g0, g1 = A["glass"]; gy = A["glass_y"]; n = A["n"]; sill = A["sill"]
    T2 = k.T / 2
    zs = VKI_ASH_SPRING[kind]
    c0, c1 = VKI_ASH_COURSES[0]
    tb = VKI_ASH_CORNICE[0] if full else c0
    # body: piers + the part under the sill (the same split in Full and Cut, so Full = Cut below 0.65)
    vki_ash_body(k, 0.0, x0, VKI_FOOT_Z, tb)
    vki_ash_body(k, x1, L, VKI_FOOT_Z, tb)
    vki_ash_body(k, x0, x1, VKI_FOOT_Z, c0)
    P, za_room = vki_ash_arc(x0, x1, zs, n)
    Q, za_glass = vki_ash_arc(g0, g1, zs, n)
    if full:
        Z = VKI_ASH_TOPZ[kind]
        vki_ash_course(k, 0.0, L, c0, c1)                                  # the sill course (the sill is its top)
        e2 = VKI_ASH_COURSE2_END
        vki_ash_course(k, 0.0, e2, *VKI_ASH_COURSES[1])                   # dies into the top jamb stones
        vki_ash_course(k, L - e2, L, *VKI_ASH_COURSES[1])
        vki_ash_cornice(k, 0.0, L)
        for poly in ([(x0, -T2), (g0, gy), (g0, T2), (x0, T2)], [(x1, -T2), (x1, T2), (g1, T2), (g1, gy)]):
            vs, fs = vki_prism(k, poly, sill, Z, VKI_WALL_A, axis="z")     # splayed jamb + outer reveal
            for f in fs:
                if f.normal.y > 0.7:
                    k.project([f], VKI_WALL_B)
            k.mark_body(vs)
        for i in range(len(P) - 1):
            vki_ash_seg(k, P[i], P[i + 1], Q[i], Q[i + 1], -T2, gy, Z)     # splay soffit segment
            vki_ash_seg(k, Q[i], Q[i + 1], Q[i], Q[i + 1], gy, T2, Z)      # outer reveal segment
        vki_ash_body(k, x0, x1, Z, tb)                                     # body over the arch
        # glass: a closed 0.02 plate, 1 cm larger than the glass outline on every side (edges buried in the body)
        gpts, _ = lancet_pts(g0 - 0.01, g1 + 0.01, sill - 0.01, zs, n)
        if broken:
            vki_ash_glass_broken(k, gpts, gy, seed=7 if kind == "Lancet" else 11)
            k.meta.update(vki_broken=1, vki_cut_to="SM_VKI_Wall_Ashlar_Lancet_150_Cut")
        else:
            vki_prism(k, gpts, gy - 0.01, gy + 0.01, STAINED, axis="y")
        for zb in VKI_ASH_BARS[kind]:                                      # iron saddle bars on the room side
            k.box((0.75, gy - 0.025, zb), (g1 - g0 + 0.03, 0.02, 0.02), IRON, bevel=0)
        vki_ash_surround(k, x0, x1, zs)
        holes = vki_ash_course_holes(L) + [(x0, c0, x1, Z + 0.35)]
        sp = VKI_ASH_LANCET_SPOT
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": sill, "z1": round(za_room, 3),
                                   "glass": [g0, g1, round(za_glass, 3)], "spring": zs},
                      vki_lights=[dict(type="SPOT", role="lancet", pos=list(sp["pos"]), aim=list(sp["aim"]),
                                       cone=sp["cone"], blend=sp["blend"], radius=sp["radius"], w_day=sp["w_day"],
                                       w_night=sp["w_night"], color_day=sp["color_day"],
                                       color_night=sp["color_night"], shadows=1)])
        if kind == "LancetTall":
            k.meta.update(vki_cut_to="SM_VKI_Wall_Ashlar_Lancet_150_Cut")
    else:
        vki_ash_course(k, 0.0, x0, c0, c1)
        vki_ash_course(k, x1, L, c0, c1)
        # DRESS sill slab; bevel 0.02, so its end faces start at 0.90, where the under-sill body's end faces stop (T5S)
        vki_tim_member(k, x0, x1, 0.88, 1.00, y0=-VKI_ASH_HW, y1=VKI_ASH_HW, mi=DRESS, bev=0.02)
        holes = []
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": sill, "z1": round(za_room, 3), "cut": 1},
                      vki_light_pool=[0.75, -1.20, 0.0])
    vki_ash_wobble(k, L, holes, tb)
    k.meta.update(vki_class="wall")


def vki_ash_lancet_full(k): vki_ash_lancet(k, "Lancet", "Full")
def vki_ash_lancet_cut(k): vki_ash_lancet(k, "Lancet", "Cut")
def vki_ash_lancettall_full(k): vki_ash_lancet(k, "LancetTall", "Full")
def vki_ash_lancet_full_broken(k): vki_ash_lancet(k, "Lancet", "Full", broken=True)
def vki_ash_lancettall_full_broken(k): vki_ash_lancet(k, "LancetTall", "Full", broken=True)


# ---------------------------------------------------------------- DoorWide_300 (§3.2 Ashlar, pointed)
def vki_ash_door(k, height, D=None, arch=False):
    """pointed wide door lancet_pts(0.70, 2.30, 0, 2.20), apex 3.44, with two DRESS orders:
    inner order: jambs x 0.54-0.70 / 2.30-2.46 from y -0.09 (the step) to +0.25, on the threshold; ring between the
      door arch (r 1.36) and r + 0.16 (voussoirs, same depth);
    outer order: jambs x 0.42-0.54 / 2.46-2.58 full depth from the footing; ring r + 0.16 .. r + 0.28 full depth.
    Both rings share their radial joint angles, so the shared chords coincide; the apex joints are vertical.
    Body: piers x 0-0.42 / 2.58-3.0, a strip over each outer-ring voussoir up to 3.85, a block above. DRESS threshold
    x 0.54-2.46 (|y| <= 0.28). Cut: the lower metre; the cap course runs from the piece end to the opening edge
    (x 0-0.70 / 2.30-3.0), bridging the outer order's recess."""
    L = 3.0
    full = height == "Full"
    D = D or VKI_ASH_DOOR
    xL, xR = D["x"]; zs = D["spring"]; sy = D["step_y"]; T2 = k.T / 2; tk = VKI_ASH_TUCK
    r = 0.85 * (xR - xL); cR, cL = xR - r, xL + r; xa = (xL + xR) / 2
    R0, R1, R2 = r, r + D["d1"], r + D["d2"]
    xo, xi = xL - D["d2"], xL - D["d1"]
    c0, c1 = VKI_ASH_COURSES[0]
    tb = VKI_ASH_CORNICE[0] if full else c0
    vki_ash_body(k, 0.0, xo, VKI_FOOT_Z, tb)                           # piers
    vki_ash_body(k, L - xo, L, VKI_FOOT_Z, tb)
    vki_ash_body(k, xi, L - xi, VKI_FOOT_Z, -0.10)                       # footing under the threshold
    vki_tim_member(k, xi, L - xi, 0.0, D["thr"], y0=-VKI_ASH_HW, y1=VKI_ASH_HW, mi=DRESS, bev=0.01)   # threshold
    jt = zs if full else c0 + tk
    for a, b in ((xo, xi), (L - xi, L - xo)):                            # outer order jambs
        vki_tim_member(k, a, b, VKI_FOOT_Z, jt, y0=-T2, y1=T2, mi=DRESS, bev=0.015)
    for a, b in ((xi, xL), (xR, L - xi)):                                # inner order jambs (behind the step)
        vki_tim_member(k, a, b, D["thr"], jt, y0=sy, y1=T2, mi=DRESS, bev=0.015)
    if full:
        m = D["n"]
        ta1 = math.acos((xa - cR) / R1)
        angs = [ta1 * j / m for j in range(m)]

        def pt(cx, sgn, R, t):
            return (cx + sgn * R * math.cos(t), zs + R * math.sin(t))

        def apex(R):
            return (xa, zs + math.sqrt(R * R - (xa - cR) ** 2))
        for Ra, Rb, ya, yb in ((R0, R1, sy, T2), (R1, R2, -T2, T2)):   # inner ring, outer ring
            for sgn, cx in ((1, cR), (-1, cL)):
                for j in range(m):
                    last = j == m - 1
                    poly = [pt(cx, sgn, Ra, angs[j]), apex(Ra) if last else pt(cx, sgn, Ra, angs[j + 1]),
                            apex(Rb) if last else pt(cx, sgn, Rb, angs[j + 1]), pt(cx, sgn, Rb, angs[j])]
                    vki_prism(k, poly if sgn > 0 else poly[::-1], ya, yb, DRESS, axis="y", bevel=0.012)
        Z = D["topz"]
        for sgn, cx in ((1, cR), (-1, cL)):                             # body strips over the outer ring
            pts = [pt(cx, sgn, R2, a) for a in angs] + [apex(R2)]
            for j in range(m):
                pa, pb = pts[j], pts[j + 1]
                poly = [pa, pb, (pb[0], Z), (pa[0], Z)]
                vs, fs = vki_prism(k, poly if sgn > 0 else poly[::-1], -T2, T2, VKI_WALL_A, axis="y")
                for f in fs:
                    if f.normal.y > 0.7:
                        k.project([f], VKI_WALL_B)
                k.mark_body(vs)
        vki_ash_body(k, xo, L - xo, Z, tb)
        for cz0, cz1 in VKI_ASH_COURSES:                                 # courses run 1 cm into the outer jambs
            vki_ash_course(k, 0.0, xo + 0.01, cz0, cz1)
            vki_ash_course(k, L - xo - 0.01, L, cz0, cz1)
        vki_ash_cornice(k, 0.0, L)
        holes = vki_ash_course_holes(L) + [(xo, 0.0, L - xo, Z + 0.3)]
        z1 = round(apex(R0)[1], 3)
    else:
        vki_ash_course(k, 0.0, xL, c0, c1)                               # the cap wraps the orders
        vki_ash_course(k, xR, L, c0, c1)
        holes = [(xo, 0.0, L - xo, c1)]
        z1 = 1.0
    vki_ash_wobble(k, L, holes, tb)
    k.meta.update(vki_nav="door", vki_nav_open=[xL, xR])
    if arch:                                                             # an open arch: no leaves, no exit
        k.meta.update(vki_class="wall", vki_arch=1,
                      vki_opening={"x0": xL, "x1": xR, "z0": 0.0, "z1": z1, "spring": zs, "pointed": 1},
                      vki_collider=[[xL / 2, 0.0, 1.1, xL, k.T, 2.2], [(xR + L) / 2, 0.0, 1.1, L - xR, k.T, 2.2]])
        return
    k.meta.update(vki_class="wall", vki_opening={"x0": xL, "x1": xR, "z0": 0.0, "z1": z1, "spring": zs,
                                                 "pointed": 1},
                  vki_trigger=[1.5, -0.65, 1.0, 1.9, 0.8, 2.0], vki_spawn_local=[1.5, -1.60],
                  vki_prompt_local=[1.5, -0.30, 1.40],
                  vki_leaf_socket=[[xL, sy, 0.0], [xR, sy, 0.0]], vki_leaf_open_deg=90,
                  vki_leaf_width_max=round((xR - xL) / 2 - 0.005, 3),
                  vki_collider=[[xL / 2, 0.0, 1.1, xL, k.T, 2.2], [(xR + L) / 2, 0.0, 1.1, L - xR, k.T, 2.2]])
    if not full:
        k.meta.update(vki_leaf=["SM_VKI_Leaf_Wide_Cut_L", "SM_VKI_Leaf_Wide_Cut_R"])


def vki_ash_doorwide_full(k): vki_ash_door(k, "Full")
def vki_ash_doorwide_cut(k): vki_ash_door(k, "Cut")


# ---------------------------------------------------------------- Arch_300 (2026-10-17: cloister walks, nave arcades,
# a hall's screens passage) -- the wide door's two orders round a wider open pointed arch, no leaves: clear 1.9 m
# (x 0.55-2.45), spring 2.20, apex 3.67, orders 0.14 / 0.24, body over the outer ring from 4.10
VKI_ASH_ARCH = dict(x=(0.55, 2.45), spring=2.20, d1=0.14, d2=0.24, step_y=-0.09, thr=0.03, n=4, topz=4.10)
def vki_ash_arch_full(k): vki_ash_door(k, "Full", VKI_ASH_ARCH, arch=True)
def vki_ash_arch_cut(k): vki_ash_door(k, "Cut", VKI_ASH_ARCH, arch=True)


# ---------------------------------------------------------------- Hearth_300 (2026-10-17: a great hall's or a
# monastery warming room's fireplace in the 4.5 m wall) -- a hooded fireplace: firebox x 0.48-2.52, 1.55 high, its
# back 5 cm into the wall (BRICK, sooted); DRESS cheeks x 0.33-0.48 / 2.52-2.67 out to y -0.80; a DRESS lintel
# 1.55-1.85 (x 0.33-2.67, out to -0.86); a tapered stone hood (AshlarIn) from the lintel (x 0.34-2.66, y -0.83) to 3.40
# (x 0.70-2.30, y -0.45), a chimney breast on up to the cornice line with a CAP top; the courses and the cornice die
# into the hood. The Stone hearth's fire (logs, firedogs, embers, flame tongues), no spit or cauldron.
# Cut: the lower metre -- cheeks, a front lintel course and cheek copings (CAP tops) with the cap course behind, the
# firebox open from above so the fire shows.
VKI_ASH_HEARTH = dict(firebox=(0.48, 2.52), mouth=1.55, back_y=-0.20, cheek=(0.33, 0.48), cheek_y=-0.80,
                      lintel=(1.55, 1.85, 0.335, -0.86), hood=(1.84, 3.40, 0.34, 0.70, -0.83, -0.45), wall_y=-0.24,
                      slab=(0.33, 2.67, -1.30, -0.80), cut_lintel_y=-0.62)
# (everything proud of the wall stays within x 0.33-2.67: the nodes' post zones stay plain section, T3)
VKI_ASH_HEARTH_FIRE = (1.50, -0.50)


def vki_ash_hearth(k, height):
    L = 3.0
    full = height == "Full"
    H = VKI_ASH_HEARTH
    T2 = k.T / 2
    fx0, fx1 = H["firebox"]; by = H["back_y"]; wy = H["wall_y"]
    c0, c1 = VKI_ASH_COURSES[0]
    tb = VKI_ASH_CORNICE[0] if full else c0
    mt = H["mouth"] if full else c0                       # mouth top (Full 1.55, Cut 0.90)
    p1 = vki_ash_body(k, 0.0, fx0, VKI_FOOT_Z, tb)       # piers
    p2 = vki_ash_body(k, fx1, L, VKI_FOOT_Z, tb)
    rec = k.body_box(fx0, fx1, VKI_FOOT_Z, mt, y0=by)     # the firebox's back, 5 cm into the wall
    k.bm.normal_update()
    for f in vki_faces_of(rec):
        if f.normal.y < -0.7:
            k.project([f], VKI_BRICK)
    for vs_, sgn in ((p1, 1), (p2, -1)):                  # the firebox's sides in the piers
        for f in vki_faces_of(vs_):
            c = f.calc_center_median()
            if f.normal.x * sgn > 0.7 and 0.0 <= c.z <= mt and c.y < 0:
                k.project([f], VKI_BRICK)
    for v in rec:
        if abs(v.co.y - by) < 1e-4:
            k.set_dark([v], 0.56 + 0.34 * vki_smoothstep(0.1, mt, v.co.z))
    for vs_, xe in ((p1, fx0), (p2, fx1)):
        for v in vs_:
            if abs(v.co.x - xe) < 1e-4 and v.co.y < 0.0 and v.co.z <= mt + 1e-4:
                k.set_dark([v], 0.52 + 0.34 * vki_smoothstep(0.1, mt, v.co.z))
    ch0, ch1 = H["cheek"]; cy = H["cheek_y"]
    cz = H["lintel"][0] + 0.05 if full else c0 + VKI_ASH_TUCK
    for a, b in ((ch0, ch1), (L - ch1, L - ch0)):         # cheeks (DRESS), up into the lintel
        vs = vki_tim_member(k, a, b, 0.0, cz, y0=cy, y1=wy, mi=DRESS, bev=0.015)
        for v in vs:
            if fx0 - 0.02 < v.co.x < fx1 + 0.02:
                k.set_dark([v], 0.30 * vki_smoothstep(0.2, mt, v.co.z))
    if full:
        ab = vki_ash_body(k, fx0, fx1, mt, tb)            # the wall over the mouth
        for f in vki_faces_of(ab):
            if f.normal.z < -0.7:
                k.project([f], VKI_BRICK)
                k.set_dark(list(f.verts), 0.62)
        l0, l1, lx, ly = H["lintel"]
        vs = vki_tim_member(k, lx, L - lx, l0, l1, y0=ly, y1=wy + 0.005, mi=DRESS, bev=0.02)   # (its back 5 mm deeper
                                                                                   # than the cheeks', T5S)
        for v in vs:
            if v.co.z < l0 + 0.03 and fx0 < v.co.x < fx1:
                k.set_dark([v], 0.45)                     # the mouth's sooted soffit
        h0, h1, hx0, hx1, hy0, hy1 = H["hood"]
        vs, fs = vki_sto_hexa(k, [(hx0, hy0, h0), (L - hx0, hy0, h0), (L - hx0, wy, h0), (hx0, wy, h0),
                                  (hx1, hy1, h1), (L - hx1, hy1, h1), (L - hx1, wy, h1), (hx1, wy, h1)], VKI_WALL_A)
        k.project(fs, VKI_WALL_A)
        top = VKI_ASH_CORNICE[1] + VKI_POST_TOP
        vs2 = list(set(k.box((L / 2, (hy1 + wy) / 2, (h1 + top) / 2), (L - 2 * hx1, wy - hy1, top - h1), VKI_WALL_A,
                             bevel=0)))
        k.bm.normal_update()
        bf = vki_faces_of(vs2)
        k.project([f for f in bf if f.normal.z < 0.7], VKI_WALL_A)
        for f in bf:
            if f.normal.z > 0.7:
                k.project([f], VKI_CAP)
        for v in vs + vs2:                                # soot up the hood's front, strongest over the fire
            k.set_dark([v], 0.34 * (1 - vki_smoothstep(0.3, 1.2, abs(v.co.x - 1.5))) *
                       (1 - vki_smoothstep(h0 + 0.2, 3.6, v.co.z)))
        def hood_x(z):                                     # the hood's side at height z
            return hx0 + (hx1 - hx0) * (z - h0) / (h1 - h0)
        vki_ash_course(k, 0.0, ch0 + 0.01, c0, c1)       # the first course dies into the cheeks
        vki_ash_course(k, L - ch0 - 0.01, L, c0, c1)
        c20, c21 = VKI_ASH_COURSES[1]                      # the second into the hood
        vki_ash_course(k, 0.0, hood_x(c21) + 0.01, c20, c21)
        vki_ash_course(k, L - hood_x(c21) - 0.01, L, c20, c21)
        vki_ash_cornice(k, 0.0, hx1 + 0.01)                # the cornice into the chimney breast
        vki_ash_cornice(k, L - hx1 - 0.01, L)
        holes = vki_ash_course_holes(L) + [(ch0, 0.0, L - ch0, 4.6)]
    else:
        lx, ly = H["lintel"][2], H["lintel"][3]
        vs = vki_tim_member(k, lx, L - lx, c0, c1, y0=ly, y1=H["cut_lintel_y"], mi=DRESS, top=VKI_CAP, bev=0.015)
        for v in vs:
            if v.co.z < c0 + 0.03 and fx0 < v.co.x < fx1:
                k.set_dark([v], 0.45)
        for a, b in ((ch0, ch1), (L - ch1, L - ch0)):     # cheek copings behind the lintel course
            vki_tim_member(k, a, b, c0, c1, y0=H["cut_lintel_y"], y1=-VKI_ASH_HW + 0.005, mi=DRESS, top=VKI_CAP,
                           bev=0.015)
        vki_ash_course(k, 0.0, L, c0, c1)                  # the cap course runs on behind
        holes = [(ch0, 0.0, L - ch0, c1)]
    sx0, sx1, sy0, sy1 = H["slab"]                         # hearth slabs and the firebox floor
    for a, b in ((sx0, 1.10), (1.10, 1.90), (1.90, sx1)):
        vs = k.box(((a + b) / 2, (sy0 + sy1) / 2, 0.015), (b - a, sy1 - sy0, 0.03), DRESS, bevel=0.012)
        for v in set(vs):
            k.set_dark([v], 0.16 + 0.22 * vki_smoothstep(sy0, sy1, v.co.y) * (1 - vki_smoothstep(0.4, 1.2, abs(v.co.x - 1.5))))
    k.set_dark(k.box((1.5, (sy1 + by) / 2, 0.0125), (fx1 - fx0 - 0.01, by - sy1, 0.035), DRESS, bevel=0.0), 0.38)
    fcx, fcy = VKI_ASH_HEARTH_FIRE
    k.set_dark(k.box((fcx, fcy, 0.045), (1.15, 0.46, 0.04), VKI_ASH, bevel=0.018, segs=2), 0.45)   # ash bed
    for x in (fcx - 0.40, fcx + 0.40):                     # firedogs
        k.box((x, fcy - 0.22, 0.15), (0.045, 0.045, 0.30), IRON, bevel=0.01)
        k.box((x, fcy, 0.10), (0.04, 0.42, 0.04), IRON, bevel=0.008)
        k.box((x, fcy - 0.24, 0.31), (0.07, 0.07, 0.03), IRON, bevel=0.01)
    vki_sto_logs(k, fcx + 0.02, ((fcy + 0.08, 0.175, 0.07, 0.96, 0.05), (fcy - 0.09, 0.17, 0.065, 0.92, -0.06),
                                 (fcy - 0.005, 0.29, 0.06, 0.76, 0.12)))
    vki_sto_embers(k, fcx, fcy, 0.075, 12, 0.46, 0.20, 5501, hmax=0.85)
    dx = fcx - 1.40
    for (x, y, h, r, tilt, spin, bow) in VKI_STO_HEARTH_FLAMES:
        vki_sto_flame(k, (x + dx, y + 0.02, 0.20), h * 1.1, r, tilt, spin, bow)
    vki_sto_body_finish(k)
    vki_ash_wobble(k, L, holes, tb)
    k.meta.update(vki_class="wall", vki_special=1,
                  vki_lights=[dict(type="POINT", role="hearth", pos=[fcx, -0.58, 0.95], w=480.0,
                                   color=[1.0, .52, .22], range=9.0, flicker=1, shadows=1, radius=0.45)],
                  vki_fx=[dict(fx="fire_large", pos=[fcx, fcy, 0.2])],
                  vki_collider=[[1.5, 0.0, 1.1, 3.0, k.T, 2.2],
                                [1.5, (sy0 + wy) / 2, 1.1, L - 2 * ch0, wy - sy0, 2.2]])


def vki_ash_hearth_full(k): vki_ash_hearth(k, "Full")
def vki_ash_hearth_cut(k): vki_ash_hearth(k, "Cut")


# ---------------------------------------------------------------- Door_150 (2026-10-17, the monastery's side doors)
# A single pointed portal: the Stone door's clear 0.84 (x 0.33-1.17), so Leaf_Plank_Full / _Cut hang in it (socket at
# the inner order's step); a DRESS lintel at the leaf's head (2.20) with a recessed tympanum filling the pointed arch
# over it; two orders as on DoorWide_300, narrower (0.12 / 0.22).
VKI_ASH_DOOR1 = dict(x=(0.33, 1.17), spring=2.20, d1=0.12, d2=0.22, step_y=-0.09, thr=0.03, n=3, topz=3.25,
                     lintel=(2.205, 2.34), tymp_y=0.03)


def vki_ash_door1(k, height):
    """pointed single door, L 1.5: piers x 0-0.11 / 1.39-1.5, outer order jambs x 0.11-0.21 full depth, inner order
    jambs x 0.21-0.33 behind the step (y -0.09); Full: rings r 0.714 .. +0.12 .. +0.22 springing 2.20 (apex 2.85),
    body strips over the outer ring to 3.25, the lintel (2.205-2.34, x 0.27-1.23, 8 mm inside the inner ring) and the tympanum
    (the arch above the lintel, set back 3 cm behind the step), courses on the piers, cornice. Cut: the lower metre."""
    L = 1.5
    full = height == "Full"
    D = VKI_ASH_DOOR1
    xL, xR = D["x"]; zs = D["spring"]; sy = D["step_y"]; T2 = k.T / 2; tk = VKI_ASH_TUCK
    r = 0.85 * (xR - xL); cR, cL = xR - r, xL + r; xa = (xL + xR) / 2
    R0, R1, R2 = r, r + D["d1"], r + D["d2"]
    xo, xi = xL - D["d2"], xL - D["d1"]
    c0, c1 = VKI_ASH_COURSES[0]
    tb = VKI_ASH_CORNICE[0] if full else c0
    vki_ash_body(k, 0.0, xo, VKI_FOOT_Z, tb)                           # piers
    vki_ash_body(k, L - xo, L, VKI_FOOT_Z, tb)
    vki_ash_body(k, xi, L - xi, VKI_FOOT_Z, -0.10)                       # footing under the threshold
    vki_tim_member(k, xi, L - xi, 0.0, D["thr"], y0=-VKI_ASH_HW, y1=VKI_ASH_HW, mi=DRESS, bev=0.01)   # threshold
    jt = zs if full else c0 + tk
    for a, b in ((xo, xi), (L - xi, L - xo)):                            # outer order jambs
        vki_tim_member(k, a, b, VKI_FOOT_Z, jt, y0=-T2, y1=T2, mi=DRESS, bev=0.015)
    for a, b in ((xi, xL), (xR, L - xi)):                                # inner order jambs (behind the step)
        vki_tim_member(k, a, b, D["thr"], jt, y0=sy, y1=T2, mi=DRESS, bev=0.015)
    if full:
        m = D["n"]
        ta1 = math.acos((xa - cR) / R1)
        angs = [ta1 * j / m for j in range(m)]

        def pt(cx, sgn, R, t):
            return (cx + sgn * R * math.cos(t), zs + R * math.sin(t))

        def apex(R):
            return (xa, zs + math.sqrt(R * R - (xa - cR) ** 2))
        for Ra, Rb, ya, yb in ((R0, R1, sy, T2), (R1, R2, -T2, T2)):   # inner ring, outer ring
            for sgn, cx in ((1, cR), (-1, cL)):
                for j in range(m):
                    last = j == m - 1
                    poly = [pt(cx, sgn, Ra, angs[j]), apex(Ra) if last else pt(cx, sgn, Ra, angs[j + 1]),
                            apex(Rb) if last else pt(cx, sgn, Rb, angs[j + 1]), pt(cx, sgn, Rb, angs[j])]
                    vki_prism(k, poly if sgn > 0 else poly[::-1], ya, yb, DRESS, axis="y", bevel=0.012)
        Z = D["topz"]
        for sgn, cx in ((1, cR), (-1, cL)):                             # body strips over the outer ring
            pts = [pt(cx, sgn, R2, a) for a in angs] + [apex(R2)]
            for j in range(m):
                pa, pb = pts[j], pts[j + 1]
                poly = [pa, pb, (pb[0], Z), (pa[0], Z)]
                vs, fs = vki_prism(k, poly if sgn > 0 else poly[::-1], -T2, T2, VKI_WALL_A, axis="y")
                for f in fs:
                    if f.normal.y > 0.7:
                        k.project([f], VKI_WALL_B)
                k.mark_body(vs)
        vki_ash_body(k, xo, L - xo, Z, tb)
        l0, l1 = D["lintel"]                                             # the lintel, bearing on the inner jambs
        vki_tim_member(k, xL - 0.06, xR + 0.06, l0, l1, y0=sy + 0.008, y1=T2 - 0.008, mi=DRESS, bev=0.015)   # (inset: never
                                                                         # coplanar with the inner ring it runs into)
        t0 = math.asin((l1 - zs) / R0)                                   # the tympanum: the arch over the lintel
        tym = [pt(cR, 1, R0 - 0.002, t0 + (math.acos((xa - cR) / R0) - t0) * j / 4) for j in range(4)] + [apex(R0 - 0.002)]
        tym += [pt(cL, -1, R0 - 0.002, t0 + (math.acos((xa - cR) / R0) - t0) * j / 4) for j in range(3, -1, -1)]
        tym = [(p[0], l1 - 0.005) if i in (0, len(tym) - 1) else p for i, p in enumerate(tym)]
        vki_prism(k, tym, sy + D["tymp_y"], T2 - 0.01, DRESS, axis="y")
        for cz0, cz1 in VKI_ASH_COURSES:                                 # courses run 1 cm into the outer jambs
            vki_ash_course(k, 0.0, xo + 0.01, cz0, cz1)
            vki_ash_course(k, L - xo - 0.01, L, cz0, cz1)
        vki_ash_cornice(k, 0.0, L)
        holes = vki_ash_course_holes(L) + [(xo, 0.0, L - xo, Z + 0.3)]
        z1 = l0
    else:
        vki_ash_course(k, 0.0, xL, c0, c1)                               # the cap wraps the orders
        vki_ash_course(k, xR, L, c0, c1)
        holes = [(xo, 0.0, L - xo, c1)]
        z1 = 1.0
    vki_ash_wobble(k, L, holes, tb)
    k.meta.update(vki_nav="door", vki_nav_open=[xL, xR])
    k.meta.update(vki_class="wall", vki_opening={"x0": xL, "x1": xR, "z0": 0.0, "z1": z1, "spring": zs,
                                                 "pointed": 1, "head": "lintel + tympanum" if full else "cut"},
                  vki_trigger=[0.75, -0.65, 1.0, 0.9, 0.8, 2.0], vki_spawn_local=[0.75, -1.60],
                  vki_prompt_local=[0.75, -0.30, 1.40], vki_leaf_socket=[xL, sy, 0.0], vki_leaf_open_deg=90,
                  vki_leaf="SM_VKI_Leaf_Plank_" + height,
                  vki_collider=[[xL / 2, 0.0, 1.1, xL, k.T, 2.2], [(xR + L) / 2, 0.0, 1.1, L - xR, k.T, 2.2]])


def vki_ash_door1_full(k): vki_ash_door1(k, "Full")
def vki_ash_door1_cut(k): vki_ash_door1(k, "Cut")


# ---------------------------------------------------------------- posts (§2.2, §2.3)
def vki_ash_frustum(k, z0, z1, h0, h1, mi):
    """closed truncated pyramid: rectangle +-h0 (x, y) at z0 to +-h1 at z1"""
    corners = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    bot = [k.bm.verts.new((sx * h0[0], sy * h0[1], z0)) for sx, sy in corners]
    top = [k.bm.verts.new((sx * h1[0], sy * h1[1], z1)) for sx, sy in corners]
    fs = [k.bm.faces.new(bot[::-1]), k.bm.faces.new(top)]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(k.bm.faces.new((bot[i], bot[j], top[j], top[i])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    k.bm.normal_update()
    k.project(fs, mi)
    return bot + top


def vki_ash_post(k, kind, height):
    """DRESS respond centred on its node, z -0.30 .. wall top + 0.04: base (the full plan, bevel 0.03), core
    +-0.255 (Mid +-0.10 x +-0.255), engaged shafts r 0.095 centred 0.215 out on the axes (Corner: 4, Mid: one on each
    wall face), ends buried 5 mm in base and capital; flared capital; abacus (the full plan, bevel 0.02) with a CAP
    top, so the node square reads as a pale cap and T4's rays hit the post first. The shafts cover the walls'
    course ends (+-0.28) at the node; the core covers the body (+-0.25)."""
    k.set_family("Ashlar")
    full = height == "Full"
    corner = kind == "Corner"
    top = (VKI_H_FULL["Ashlar"] if full else VKI_CUT_H) + VKI_POST_TOP
    ax, ay = (VKI_POST_HW["O"], VKI_POST_HW["O"]) if corner else VKI_MID_HW["O"]
    zb = 0.30 if full else 0.20                    # base top
    zc = top - (0.30 if full else 0.20)            # capital bottom
    zab = top - 0.12                               # abacus bottom
    hx, hy = (0.255, 0.255) if corner else (0.10, 0.255)
    k.box((0.0, 0.0, (VKI_POST_Z0 + zb) / 2), (2 * ax, 2 * ay, zb - VKI_POST_Z0), DRESS, bevel=0.03)
    k.box((0.0, 0.0, (zb + zc) / 2), (2 * hx, 2 * hy, zc - zb), DRESS, bevel=0.015)
    shafts = ((0.215, 0.0), (-0.215, 0.0), (0.0, 0.215), (0.0, -0.215)) if corner else ((0.0, 0.215), (0.0, -0.215))
    for sx, sy in shafts:
        _cyl(k, (sx, sy, (zb + zc) / 2), 0.095, 0.095, zc - zb + 0.01, 12, DRESS)
    vki_ash_frustum(k, zc, zab, (hx - 0.005, hy - 0.005), (ax - 0.005, ay - 0.005), DRESS)
    vs = list(set(k.box((0.0, 0.0, (zab + top) / 2), (2 * ax, 2 * ay, top - zab), DRESS, bevel=VKI_POST_BEVEL)))
    k.bm.normal_update()
    vki_proj_long(k, [f for f in vki_faces_of(vs) if f.normal.z > 0.65], VKI_CAP, VKI_TIM_X,
                  off=vki_hash_off((0.0, 0.0, top)))
    if corner:
        other = "SM_VKI_Post_Ashlar_Corner_" + ("Cut" if full else "Full")
    else:
        other = "SM_VKI_Post_Ashlar_Corner_Cut"        # no Mid_Cut (§3.1): an all-Cut Mid node takes the Corner_Cut
    rule = {"Corner": "L/T/X junction (required, T12 error if missing); SW/SE pillars of the chapel (Ashlar uses "
                      "pillars, never rakes, §2.4); height = tallest wall-end height present",
            "Mid": "Full only: height/family/class step or free end at a Full wall (required); rhythm on the chapel's "
                   "side walls (y 3.0 / 6.0, §2.3)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": other,
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_ash_post_corner_full(k): vki_ash_post(k, "Corner", "Full")
def vki_ash_post_corner_cut(k): vki_ash_post(k, "Corner", "Cut")
def vki_ash_post_mid_full(k): vki_ash_post(k, "Mid", "Full")


VKI_ASH_SPECS = [
    ("SM_VKI_Wall_Ashlar_Plain_150A_Full", vki_ash_plain_150a_full),
    ("SM_VKI_Wall_Ashlar_Plain_150A_Cut", vki_ash_plain_150a_cut),
    ("SM_VKI_Wall_Ashlar_Plain_300_Full", vki_ash_plain_300_full),
    ("SM_VKI_Wall_Ashlar_Plain_300_Cut", vki_ash_plain_300_cut),
    ("SM_VKI_Wall_Ashlar_Lancet_150_Full", vki_ash_lancet_full),
    ("SM_VKI_Wall_Ashlar_Lancet_150_Cut", vki_ash_lancet_cut),
    ("SM_VKI_Wall_Ashlar_LancetTall_150_Full", vki_ash_lancettall_full),
    ("SM_VKI_Wall_Ashlar_Lancet_150_Full_Broken", vki_ash_lancet_full_broken),
    ("SM_VKI_Wall_Ashlar_LancetTall_150_Full_Broken", vki_ash_lancettall_full_broken),
    ("SM_VKI_Wall_Ashlar_DoorWide_300_Full", vki_ash_doorwide_full),
    ("SM_VKI_Wall_Ashlar_DoorWide_300_Cut", vki_ash_doorwide_cut),
    ("SM_VKI_Wall_Ashlar_Door_150_Full", vki_ash_door1_full),
    ("SM_VKI_Wall_Ashlar_Door_150_Cut", vki_ash_door1_cut),
    ("SM_VKI_Wall_Ashlar_Arch_300_Full", vki_ash_arch_full),
    ("SM_VKI_Wall_Ashlar_Arch_300_Cut", vki_ash_arch_cut),
    ("SM_VKI_Wall_Ashlar_Hearth_300_Full", vki_ash_hearth_full),
    ("SM_VKI_Wall_Ashlar_Hearth_300_Cut", vki_ash_hearth_cut),
    ("SM_VKI_Post_Ashlar_Corner_Full", vki_ash_post_corner_full),
    ("SM_VKI_Post_Ashlar_Corner_Cut", vki_ash_post_corner_cut),
    ("SM_VKI_Post_Ashlar_Mid_Full", vki_ash_post_mid_full),
]
VKI_ASH_NAMES = [n for n, _ in VKI_ASH_SPECS]
vki_register([(n, fn, {"grime": "wall"}, "wattle") for n, fn in VKI_ASH_SPECS])
