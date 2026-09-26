# ===================== VKI FAM TIMBER: the Timber wall family (§2.2, §3.1, §3.2) -- 17 masters =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md. Loaded by vki_ns() (VKI_TEXTS, before vki_floors).
# Every top-level name starts with vki_/VKI_ (T18).
#
# Section (class O, T 0.50, H 3.0), piece-local, room on -Y:
#   body   plaster +-0.25 (WALL_A on -Y, WALL_B on +Y), z -0.30 .. cap bottom, grid_cut 0.25, wobble last (§2.6)
#   oak members +-0.28 (CAP_HW), WOOD, bevel 0.02:
#     sole plate 0 .. 0.16 | half-studs x 0..0.06 and L-0.06..L | studs 0.12 wide at 0.75 (1.5, 2.25 on 300s)
#     mid-rail 0.90 .. 1.00 (the Cut cap; also on Full walls, split by the studs that pass it), top face CAP
#     head plate 2.88 .. 3.00 (Full), top face CAP; end-pinned sag (VKI_FLAGS["sag"]) on the Cut cap / head plate
#   Plain_150B: curved brace above z 1.2 (its own wobble seed B). Rakes: Cut profile for x <= 0.32 from the low end,
#   Full for x >= 1.18, the cap slopes at 66.7 deg between.
# Build: g["vki_rebuild"](VKI_TIM_NAMES); test: g["vki_test_pieces"](VKI_TIM_NAMES) -> {}.
import bpy, bmesh, math, json
from mathutils import Vector, Matrix

VKI_TIM_BEV = 0.02                  # member bevel (chunky hewn edges)
VKI_TIM_HW = 0.28                   # oak members' half width (= CAP_HW, class O)
VKI_TIM_STUD_HW = 0.06              # studs 0.12 wide; half-studs 0.06 at each piece end
VKI_TIM_HEAD = (2.88, 3.00)         # full head plate (H - 0.12 .. H)
VKI_TIM_RAIL = (0.90, 1.00)         # mid-rail = cut cap
VKI_TIM_OPEN = (0.33, 1.17)         # clear opening (x) of every 150 opening piece
VKI_TIM_WIN = dict(sill=1.00, head=2.25, glass=(0.45, 1.05), glass_y=0.10, lintel=(2.25, 2.40))
# window spot (fix r1): raised and brought in (was pos (0.75, 2.25, 3.0) aimed at y -2.44, 350 W) so the beam
# through the 1.00-2.25 opening lands as a compact pool about 0.7-1.5 m from the room face instead of a faint streak
# 1.5-6 m into the room (the pool's near edge is set by the sill's room edge: a pool at the wall foot is impossible
# with a 1.00 sill and a 0.56 thick opening); a small radius keeps its edges readable. The cone is 24 deg (half
# angle 12: the opening subtends about +-8 deg from the light), so the spot, now above the wall top, does not also
# light the caps and post tops beside the window (a 60 deg cone put hot patches on them)
VKI_TIM_WIN_SPOT = dict(pos=(0.75, 2.0, 4.2), aim=(0.75, -1.35, 0.0), cone=24.0, blend=0.15, radius=0.05,
                        w_day=1000.0, w_night=150.0)
VKI_TIM_DOOR = dict(top=2.20, lintel=(2.20, 2.38), jamb=(0.19, 0.33), thr=0.03)
VKI_TIM_RAKE = dict(lo=0.32, hi=1.18)            # Cut profile up to 0.32 from the low end, Full from 1.18
VKI_TIM_FP = dict(firebox=(0.90, 2.10), back_y=-0.20, breast=(0.40, 2.60), front_y=-0.85, mouth=(0.70, 2.30),
                  mouth_top=1.30, bress=(1.28, 1.50), hearth=(0.35, 2.65, -1.45, -0.85))
VKI_TIM_CUT_TO = "SM_VKI_Wall_Timber_Plain_150A_Cut"
VKI_TIM_FOOT_TOP = -0.10            # footings under openings stop at the floor-slab bottom (no face in the z 0 plane)
# core fix (z-fighting): a member that butts into a cap / lintel / plate runs this far INTO it, so its end face is
# buried inside the other member instead of lying in the same plane as the body's top face (studs, half-studs,
# cripple studs, the rake stud and rail stub, door sole plates and rail stubs under the jambs, the fireplace throat)
VKI_TIM_TUCK = 0.005
# post tops (G1 / visual r2): "endgrain" maps each top onto ONE centred, padded log end of T_VK_EndGrain (fill
# VKI_TIM_POST_FILL: corners at uv radius 0.37 < the ring's 0.44, so no bark and no second ring); "cap" gives the
# top the pale hewn CAP with its grain across the post (the alternative if the ring reads as a sawn log)
VKI_TIM_POST_TOP = "endgrain"
VKI_TIM_POST_FILL = 0.26
# Door_150_Cut reveal faces (visual r2): "limewash" (WALL_A, the zone's plaster style) | "planks" (M_VKI_WoodScrubbed,
# grain vertical) | "cap" (hewn). Measured on the look test's N-S partition doorway by Day (reveal mean luma): oak
# 0.05, planks 0.18 (reads as a closed plank door), cap 0.35 (merges with the cap top into one pale block), limewash
# 0.45 (reads as the plastered side of an opening, clearly apart from the dark studs and the wood cap) -> limewash
VKI_TIM_REVEAL = "limewash"
VKI_TIM_X = Vector((1, 0, 0)); VKI_TIM_Y = Vector((0, 1, 0)); VKI_TIM_Z = Vector((0, 0, 1))


# ---------------------------------------------------------------- generic geometry helpers (reused by other families)
def vki_cut(k, vs, xs=(), ys=(), zs=()):
    """bisect the geometry of vertices vs at the given x / y / z planes; returns the (new) vertex list"""
    geom = set(vs) | {e for v in vs for e in v.link_edges} | {f for v in vs for f in v.link_faces}
    for axis, vals in ((0, xs), (1, ys), (2, zs)):
        for c in vals:
            co = [0.0, 0.0, 0.0]; no = [0.0, 0.0, 0.0]
            co[axis] = c; no[axis] = 1.0
            g = [e for e in geom if e.is_valid]
            r = bmesh.ops.bisect_plane(k.bm, geom=g, plane_co=co, plane_no=no)
            geom = set(g) | set(r["geom"])
    return [v for v in geom if isinstance(v, bmesh.types.BMVert) and v.is_valid]


def vki_faces_of(vs):
    return list({f for v in vs for f in v.link_faces})


def vki_hash_off(c):
    """the kit's centre-hash UV offset (float tuples hash identically in every session)"""
    h = abs(hash((round(c[0], 2), round(c[1], 2), round(c[2], 2))))
    return ((h % 997) / 997.0, (h // 997 % 991) / 991.0)


def vki_prism(k, poly, a0, a1, mi, axis="y", bevel=0.0, project=True):
    """closed prism: a convex polygon `poly` (2-D points) in the plane perpendicular to `axis`, extruded a0..a1.
    axis "y": poly = (x, z); "z": poly = (x, y); "x": poly = (y, z). Outward normals; optional bevel on every edge
    (like Kit.box). Returns (verts, faces), faces projected with mi."""
    def P(p, a):
        if axis == "y":
            return Vector((p[0], a, p[1]))
        if axis == "z":
            return Vector((p[0], p[1], a))
        return Vector((a, p[0], p[1]))
    before = set(k.bm.faces)
    A = [k.bm.verts.new(P(p, a0)) for p in poly]
    B = [k.bm.verts.new(P(p, a1)) for p in poly]
    n = len(poly)
    fs = [k.bm.faces.new(A), k.bm.faces.new(B[::-1])]
    for i in range(n):
        j = (i + 1) % n
        fs.append(k.bm.faces.new((A[i], A[j], B[j], B[i])))
    for f in fs:
        f.material_index = mi
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    vs = A + B
    if bevel > 0:
        edges = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(k.bm, geom=edges + vs, offset=bevel, segments=1, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
        fs = [f for f in k.bm.faces if f not in before]           # bevel may replace the original faces
        vs = list({v for f in fs for v in f.verts})
    k.bm.normal_update()
    for f in fs:
        f.material_index = mi
    if project:
        k.project(fs, mi)
    return vs, fs


def vki_proj_long(k, fs, mi, long_dir, off=(0.0, 0.0), sizes=(1.0, 0.3, 0.1)):
    """project faces with the grain (U) along long_dir (WOOD / CAP members that are not axis-aligned)"""
    L = Vector(long_dir).normalized()
    for f in fs:
        f.normal_update()
        side = f.normal.cross(L)
        if side.length < 1e-6:
            side = VKI_TIM_Y.copy()
        k.project([f], mi, axes=[L, side.normalized(), f.normal.copy()], sizes=list(sizes), offset=off)


def vki_top_faces(k, vs, mi, c, sz, nz=0.65, along=None):
    """re-project the upward faces (n.z > nz, i.e. the top and its chamfers) of a member in slot mi (CAP /
    ENDGRAIN), grain along the member's long axis, or along `along` when given (fix r1: wall caps pass X, so a cap
    member shorter than the wall is thick -- jamb tops, rail stubs, rake flats -- keeps its grain along the wall)"""
    k.bm.normal_update()
    fs = [f for f in vki_faces_of(vs) if f.normal.z > nz]
    if along is not None:
        a = Vector(along).normalized()
        side = VKI_TIM_Z.cross(a).normalized()
        k.project(fs, mi, axes=[a, side, VKI_TIM_Z.copy()], sizes=[1.0, 0.3, 0.1], offset=vki_hash_off(c))
    else:
        k.project(fs, mi, axes=[VKI_TIM_X.copy(), VKI_TIM_Y.copy(), VKI_TIM_Z.copy()], sizes=list(sz),
                  offset=vki_hash_off(c))
    return fs


VKI_ENDGRAIN_R = 0.44               # radius of the painted log end in T_VK_EndGrain (centred at uv 0.5, 0.5)


def vki_endgrain_fit(k, fs, c, U, V, half, fill=0.30):
    """fix r1: map end-grain faces onto the ONE painted log end of T_VK_EndGrain (a ring centred in the tile on a
    bark ground): point p -> uv 0.5 + ((p - c).U, (p - c).V) * fill / half. A hewn post uses fill 0.30 (its square
    stays inside the ring's inscribed square, so no bark and no neighbouring ring shows); a round log end uses about
    VKI_ENDGRAIN_R. The old tile-0.6 planar projection with a hash offset showed parts of 2-3 rings per post top."""
    U = Vector(U).normalized(); V = Vector(V).normalized(); c = Vector(c)
    s = fill / half
    for f in fs:
        f.material_index = ENDGRAIN
        for l in f.loops:
            d = l.vert.co - c
            l[k.uv].uv = (0.5 + d.dot(U) * s, 0.5 + d.dot(V) * s)


def vki_band(k, A, B, y0, y1, mi):
    """closed solid between two polylines A and B (same count, points (x, z)), extruded y0..y1 (curved braces).
    The start cap joins A[0]-B[0], the end cap A[-1]-B[-1]. Grain follows the band.
    Fix r1: the band is unwrapped as ONE strip -- u = arc length along the band's mid-line, v = distance across it
    (front / back faces) or y (the two curved edge faces) -- so the grain runs on continuously round the curve (the
    old per-segment projection gave a checkerboard of offset grain blocks)."""
    fa = [k.bm.verts.new((p[0], y0, p[1])) for p in A]; ba = [k.bm.verts.new((p[0], y1, p[1])) for p in A]
    fb = [k.bm.verts.new((p[0], y0, p[1])) for p in B]; bb = [k.bm.verts.new((p[0], y1, p[1])) for p in B]
    segs = []
    for i in range(len(A) - 1):
        q = [k.bm.faces.new((fa[i], fa[i + 1], fb[i + 1], fb[i])), k.bm.faces.new((ba[i], bb[i], bb[i + 1], ba[i + 1])),
             k.bm.faces.new((fa[i], ba[i], ba[i + 1], fa[i + 1])), k.bm.faces.new((fb[i], fb[i + 1], bb[i + 1], bb[i]))]
        segs.append(q)
    caps = [k.bm.faces.new((fa[0], fb[0], bb[0], ba[0])), k.bm.faces.new((fa[-1], ba[-1], bb[-1], fb[-1]))]
    allf = [f for q in segs for f in q] + caps
    bmesh.ops.recalc_face_normals(k.bm, faces=allf)
    k.bm.normal_update()
    tt = vki_tile(mi)
    off = vki_hash_off((A[0][0], y0, A[0][1]))
    mid = [(Vector(a) + Vector(b)) / 2 for a, b in zip(A, B)]
    s = [0.0]
    for i in range(1, len(mid)):
        s.append(s[-1] + (mid[i] - mid[i - 1]).length)
    uvi = {}                                          # vert -> (u, v across the band, y)
    for i in range(len(A)):
        w = (Vector(B[i]) - Vector(A[i])).length
        for v_, across in ((fa[i], 0.0), (ba[i], 0.0), (fb[i], w), (bb[i], w)):
            uvi[v_] = (s[i], across, v_.co.y)
    for i, q in enumerate(segs):
        for j, f in enumerate(q):
            f.material_index = mi
            for l in f.loops:
                u_, a_, y_ = uvi[l.vert]
                l[k.uv].uv = (u_ / tt + off[0], (a_ if j < 2 else y_) / tt + off[1])
    k.project(caps, mi)
    return allf


def vki_bez(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])


# ---------------------------------------------------------------- Timber building blocks
def vki_tim_member(k, x0, x1, z0, z1, y0=-VKI_TIM_HW, y1=VKI_TIM_HW, mi=None, top=None, bev=VKI_TIM_BEV, cuts=()):
    """an oak member box (WOOD by default); `top`: slot for its upward faces (CAP); `cuts`: extra x planes (sag)"""
    mi = WOOD if mi is None else mi
    if x1 - x0 < 1e-6 or z1 - z0 < 1e-6 or y1 - y0 < 1e-6:
        return []
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); sz = (x1 - x0, y1 - y0, z1 - z0)
    vs = list(set(k.box(c, sz, mi, bevel=bev)))
    xs = [x for x in cuts if x0 + 1e-4 < x < x1 - 1e-4]
    if xs:
        vs = vki_cut(k, vs, xs=xs)
    if top is not None:
        vki_top_faces(k, vs, top, c, sz, along=VKI_TIM_X if top == VKI_CAP else None)
    return vs


def vki_tim_rails(k, a, b, studs, z0=VKI_TIM_RAIL[0], z1=VKI_TIM_RAIL[1], y0=-VKI_TIM_HW, y1=VKI_TIM_HW):
    """the Full-wall mid-rail between a and b, interrupted by the studs that pass it; top faces CAP"""
    xs = [a]
    for s in sorted(studs):
        if a < s - VKI_TIM_STUD_HW - 1e-6 and s + VKI_TIM_STUD_HW < b - 1e-6:
            xs += [s - VKI_TIM_STUD_HW, s + VKI_TIM_STUD_HW]
    xs.append(b)
    for i in range(0, len(xs), 2):
        vki_tim_member(k, xs[i], xs[i + 1], z0, z1, y0=y0, y1=y1, top=VKI_CAP)


def vki_tim_body(k, x0, x1, z0, z1, y0=None):
    return k.body_box(x0, x1, z0, z1, y0=y0)


def vki_tim_studs(L):
    return [s for s in (0.75, 1.5, 2.25) if s < L - 0.1]


def vki_tim_grid(L):
    return [0.25 * i for i in range(1, int(round(L / 0.25)))]


def vki_tim_sag_fn(L, amp=None):
    """end-pinned sag: 0 within NODE_FLAT (0.32) of every node, amp at mid-span (Timber rails 0.010)"""
    if amp is None:
        amp = VKI_FAMILIES["Timber"]["sag"] if VKI_FLAGS.get("sag", True) else 0.0
    nodes = [n for n in (0.0, 1.5, 3.0) if n <= L + 1e-6]

    def f(x):
        return amp * min(vki_smoothstep(0.32, 0.75, abs(x - n)) for n in nodes) if amp else 0.0
    return f


def vki_tim_apply_sag(k, sag, z0, z1):
    """lower every vertex with z in [z0, z1] by sag(x) (the cap member, the body top and the stud tops under it)"""
    for v in k.bm.verts:
        if z0 - 1e-6 <= v.co.z <= z1 + 1e-6:
            d = sag(v.co.x)
            if d:
                v.co.z -= d


def vki_tim_ends(k, L, tb):
    """sole plate is laid by the caller; this lays the two half-studs (each node shows one full stud)"""
    vki_tim_member(k, 0.0, VKI_TIM_STUD_HW, VKI_SOLE_TOP, tb + VKI_TIM_TUCK)
    vki_tim_member(k, L - VKI_TIM_STUD_HW, L, VKI_SOLE_TOP, tb + VKI_TIM_TUCK)


def vki_tim_brace(k):
    """Plain_150B: a curved oak arch-brace from the west half-stud up to the head plate (z 1.86 .. 2.88).
    Fix r1: the inner curve's control point is x 0.10 (was 0.08), so no brace vertex lies within 5 mm of a Mid
    post's side face (x 0.12): its vertex at t 3/8 moved from x 0.117 (2.8 mm inside the face, a T4 margin failure
    next to a Mid post) to x 0.127, just outside."""
    n = 8
    A = [vki_bez((0.06, 2.12), (0.10, 2.74), (0.40, VKI_TIM_HEAD[0]), i / n) for i in range(n + 1)]
    B = [vki_bez((0.06, 1.86), (0.20, 2.52), (0.66, VKI_TIM_HEAD[0]), i / n) for i in range(n + 1)]
    return vki_band(k, A, B, -VKI_TIM_HW, VKI_TIM_HW, WOOD)


def vki_tim_meta_wall(k, **kw):
    k.meta.update(kw)


VKI_TIM_FOOT_DARK = 0.22            # extra darkening on the stone footing band (below z 0)
VKI_TIM_PIN_CELL = 0.025            # oak plug behind each half-stud's chamfered top corner (joint pinhole)


def vki_tim_body_finish(k, L):
    """fix r1, called by every wall builder after its bodies exist (before wobble, which never moves z <= 0.16):
    (1) the footing band below the floor (body +-Y faces with every vertex at z <= 0) becomes a dressed-stone
        plinth (DRESS at t 1.5: 1.5 / t is an integer, so it stays continuous across pieces like the world-locked
        slots) and darkens a little more, instead of a pale limewash band under the timber sole on the outer face
        of the south Cut wall;
    (2) at a butt joint the chamfers of the two half-studs and of the cap / head plate leave a small diamond
        through which the pale plaster showed as a speck at the game camera (the body face's top corner behind the
        half-stud's chamfered top, and the body top). Each end gets small oak plugs in front of the body faces'
        top corners (inside the half-stud's volume, so they show only through that notch; x 0.001..0.025 from the
        end, never in the end plane), and the body's upward faces (always under a rail, plate or lintel) become oak."""
    body = [v for v in k.bm.verts if v[k.body]]
    zt = {xe: max([v.co.z for v in body if abs(v.co.x - xe) < 1e-5] or [None]) for xe in (0.0, L)}
    k.bm.normal_update()
    for f in list(k.bm.faces):
        if f.material_index not in (VKI_WALL_A, VKI_WALL_B) or not all(v[k.body] for v in f.verts):
            continue
        if f.normal.z > 0.7:
            k.project([f], WOOD)
            continue
        if abs(f.normal.y) < 0.7 or max(v.co.z for v in f.verts) > 1e-6:
            continue
        k.project([f], DRESS, tile=1.5)
        for v in f.verts:
            k.set_dark([v], VKI_TIM_FOOT_DARK * vki_smoothstep(0.0, -0.15, v.co.z) + 0.08)
    T2 = k.T / 2
    for xe, sgn in ((0.0, 1), (L, -1)):
        if zt[xe] is None:
            continue
        x0, x1 = sorted((xe + sgn * 0.001, xe + sgn * VKI_TIM_PIN_CELL))
        for ys in (-1, 1):
            y0, y1 = sorted((ys * (T2 + 0.0005), ys * (VKI_TIM_HW - 0.01)))
            k.box(((x0 + x1) / 2, (y0 + y1) / 2, zt[xe] - 0.013), (x1 - x0, y1 - y0, 0.024), WOOD, bevel=0)


# ---------------------------------------------------------------- Plain (150A, 150B, 300), Full and Cut
def vki_tim_plain(k, L, height, variant="A", brace=False):
    full = height == "Full"
    tb = VKI_TIM_HEAD[0] if full else VKI_TIM_RAIL[0]
    studs = vki_tim_studs(L)
    sag = vki_tim_sag_fn(L)
    vki_tim_body(k, 0.0, L, VKI_FOOT_Z, tb)
    vki_tim_member(k, 0.0, L, 0.0, VKI_SOLE_TOP)                        # sole plate
    vki_tim_ends(k, L, tb)
    for s in studs:
        vki_tim_member(k, s - VKI_TIM_STUD_HW, s + VKI_TIM_STUD_HW, VKI_SOLE_TOP, tb + VKI_TIM_TUCK)
    if full:
        vki_tim_rails(k, VKI_TIM_STUD_HW, L - VKI_TIM_STUD_HW, studs)   # studs pass the mid-rail on Full walls
        vki_tim_member(k, 0.0, L, *VKI_TIM_HEAD, top=VKI_CAP, cuts=vki_tim_grid(L))
        if brace:
            vki_tim_brace(k)
        vki_tim_apply_sag(k, sag, *VKI_TIM_HEAD)
    else:
        vki_tim_member(k, 0.0, L, *VKI_TIM_RAIL, top=VKI_CAP, cuts=vki_tim_grid(L))
        vki_tim_apply_sag(k, sag, *VKI_TIM_RAIL)
    vki_tim_body_finish(k, L)
    vki_wobble(k, L, "Timber", variant, holes=[], top_body_fn=lambda x: tb - sag(x), pins=studs)
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_TIM_CUT_TO)


def vki_tim_plain_150a_full(k): vki_tim_plain(k, 1.5, "Full", "A")
def vki_tim_plain_150a_cut(k): vki_tim_plain(k, 1.5, "Cut", "A")
def vki_tim_plain_150b_full(k): vki_tim_plain(k, 1.5, "Full", "B", brace=True)
def vki_tim_plain_300_full(k): vki_tim_plain(k, 3.0, "Full", "A")
def vki_tim_plain_300_cut(k): vki_tim_plain(k, 3.0, "Cut", "A")


# ---------------------------------------------------------------- Window_150 (§3.2)
def vki_tim_window(k, height):
    """glass x 0.45-1.05 at y +0.10 (closed 0.02 box, WINDOW), splayed to 0.33-1.17 at face A; sill top 1.00 (the
    mid-rail), head 2.25 under an oak lintel; interior shutters folded into the splays (SHUTTER).
    Cut: plain cut wall whose cap over x 0.33-1.17 is a pale CAP sill slab |y| <= 0.30, top 1.00 + light-pool anchor."""
    L = 1.5
    full = height == "Full"
    x0, x1 = VKI_TIM_OPEN
    tb = VKI_TIM_HEAD[0] if full else VKI_TIM_RAIL[0]
    # body: piers + the part under the sill (the same split in Full and Cut, so Full = Cut below 0.65)
    vki_tim_body(k, 0.0, x0, VKI_FOOT_Z, tb)
    vki_tim_body(k, x1, L, VKI_FOOT_Z, tb)
    vki_tim_body(k, x0, x1, VKI_FOOT_Z, VKI_TIM_RAIL[0])
    vki_tim_member(k, 0.0, L, 0.0, VKI_SOLE_TOP)
    vki_tim_ends(k, L, tb)
    sag = vki_tim_sag_fn(L) if full else (lambda x: 0.0)
    if full:
        W = VKI_TIM_WIN
        vki_tim_member(k, 0.69, 0.81, VKI_SOLE_TOP, VKI_TIM_RAIL[0] + VKI_TIM_TUCK)  # stud under the sill
        vki_tim_member(k, VKI_TIM_STUD_HW, L - VKI_TIM_STUD_HW, *VKI_TIM_RAIL, top=VKI_CAP)   # rail = sill
        T2 = k.T / 2
        for poly in ([(x0, -T2), (W["glass"][0], W["glass_y"]), (W["glass"][0], T2), (x0, T2)],
                     [(x1, -T2), (x1, T2), (W["glass"][1], T2), (W["glass"][1], W["glass_y"])]):
            vs, fs = vki_prism(k, poly, W["sill"], W["head"], VKI_WALL_A, axis="z")   # splayed reveals
            for f in fs:
                if f.normal.y > 0.7:
                    k.project([f], VKI_WALL_B)
            k.mark_body(vs)
        vki_tim_member(k, 0.20, 1.30, W["head"], W["lintel"][1])                     # oak lintel 2.25-2.40
        vki_tim_body(k, x0, x1, W["lintel"][1], tb)                                  # wall over the lintel
        vki_tim_member(k, 0.69, 0.81, W["lintel"][1] - VKI_TIM_TUCK, tb + VKI_TIM_TUCK)   # cripple stud
        vki_tim_member(k, 0.0, L, *VKI_TIM_HEAD, top=VKI_CAP, cuts=vki_tim_grid(L))
        # glass (closed 0.02 box, embedded 1 cm in rail / lintel / reveals) + oak glazing bars on the room side
        k.box((0.75, W["glass_y"], (0.99 + 2.26) / 2), (0.62, 0.02, 1.27), WINDOW, bevel=0)
        vki_tim_member(k, 0.72, 0.78, W["sill"], W["head"], y0=0.035, y1=0.085, bev=0.008)
        vki_tim_member(k, 0.425, 1.075, 1.62, 1.68, y0=0.04, y1=0.08, bev=0.008)
        # interior shutters folded flat against the splays
        P = Vector((x0, -T2)); d = Vector((W["glass"][0] - x0, W["glass_y"] + T2)).normalized()
        nrm = Vector((d.y, -d.x))
        for side in (0, 1):
            pts = [P + d * 0.03 + nrm * 0.003, P + d * 0.27 + nrm * 0.003, P + d * 0.27 + nrm * 0.03,
                   P + d * 0.03 + nrm * 0.03]
            if side:
                pts = [Vector((L - p.x, p.y)) for p in pts][::-1]
            vs, fs = vki_prism(k, [tuple(p) for p in pts], 1.05, 2.20, SHUTTER, axis="z", project=False)
            vki_proj_long(k, fs, SHUTTER, VKI_TIM_Z, off=(0.37 * side, 0.0))
            for zz in (1.30, 1.95):                                                  # iron hinge straps
                q = [P + d * 0.05 + nrm * 0.03, P + d * 0.25 + nrm * 0.03, P + d * 0.25 + nrm * 0.036,
                     P + d * 0.05 + nrm * 0.036]
                if side:
                    q = [Vector((L - p.x, p.y)) for p in q][::-1]
                vki_prism(k, [tuple(p) for p in q], zz, zz + 0.045, IRON, axis="z")
        vki_tim_apply_sag(k, sag, *VKI_TIM_HEAD)
        holes = [(x0, VKI_TIM_RAIL[0], x1, W["lintel"][1])]
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": W["sill"], "z1": W["head"]},
                      vki_lights=[dict(type="SPOT", role="window", pos=list(VKI_TIM_WIN_SPOT["pos"]),
                                       aim=list(VKI_TIM_WIN_SPOT["aim"]), cone=VKI_TIM_WIN_SPOT["cone"],
                                       blend=VKI_TIM_WIN_SPOT["blend"], radius=VKI_TIM_WIN_SPOT["radius"],
                                       w_day=VKI_TIM_WIN_SPOT["w_day"], w_night=VKI_TIM_WIN_SPOT["w_night"],
                                       color_day=[.82, .88, 1.0], color_night=[.62, .70, 1.0], shadows=1)])
    else:
        vki_tim_member(k, 0.69, 0.81, VKI_SOLE_TOP, 0.88)
        # cap segments run 0.04 into the sill slab (review r2 minor): their bevelled ends are buried in the slab, so
        # the 2 x 10 cm open V-slots at 0.31-0.33 / 1.17-1.19 close, the tops meet the sill top flush at 0.35 / 1.15,
        # and the end ring no longer lies on a Corner post's face plane (0.31, the T4 false positive)
        vki_tim_member(k, 0.0, x0 + 0.04, *VKI_TIM_RAIL, top=VKI_CAP)
        vki_tim_member(k, x1 - 0.04, L, *VKI_TIM_RAIL, top=VKI_CAP)
        # sill slab (fix r1): |y| <= 0.28 with the rails' 0.02 bevel -- flush with the cap line instead of 2 cm
        # proud (§3.2 allows |y| <= 0.30), so Window Full and Cut share one footprint (§2.4); all CAP, so paler
        vki_tim_member(k, x0, x1, 0.88, 1.00, mi=VKI_CAP, top=VKI_CAP)
        holes = []
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": 1.00, "z1": VKI_TIM_WIN["head"], "cut": 1},
                      vki_light_pool=[0.75, -1.20, 0.0])
    vki_tim_body_finish(k, L)
    vki_wobble(k, L, "Timber", "A", holes=holes, top_body_fn=lambda x: tb - sag(x), pins=(0.75,))
    k.meta.update(vki_class="wall")


def vki_tim_window_full(k): vki_tim_window(k, "Full")
def vki_tim_window_cut(k): vki_tim_window(k, "Cut")


# ---------------------------------------------------------------- Door_150 (§3.2)
def vki_tim_door(k, height):
    """clear opening x 0.33-1.17 x 2.20, oak frame (jambs x 0.19-0.33 / 1.17-1.31), lintel 2.20-2.38, threshold
    z 0-0.03 (oak). Cut: jambs end at 1.00 with a CAP top (the cap wraps the reveal) + the threshold."""
    L = 1.5
    full = height == "Full"
    x0, x1 = VKI_TIM_OPEN
    D = VKI_TIM_DOOR
    tb = VKI_TIM_HEAD[0] if full else VKI_TIM_RAIL[0]
    ja = D["jamb"][0]
    # the piers stop at the jambs' outer faces (x 0.19 / 1.31): a pier running on to the opening edge put its end
    # face in the same plane as the jamb's reveal face and z-fought there (seen in the C3 catalog render)
    vki_tim_body(k, 0.0, ja, VKI_FOOT_Z, tb)
    vki_tim_body(k, L - ja, L, VKI_FOOT_Z, tb)
    # footing under the frame + threshold: its top stops at the floor-slab bottom (z -0.10), so it never shares the
    # z 0 plane with the room floor or the apron (T5); floors / the apron close the space over it
    vki_tim_body(k, ja, L - ja, VKI_FOOT_Z, VKI_TIM_FOOT_TOP)
    # sole plates run 1 cm under the jambs (core fix: their end faces lay in the pier's end plane x 0.19 / 1.31)
    vki_tim_member(k, 0.0, ja + 0.01, 0.0, VKI_SOLE_TOP)
    vki_tim_member(k, L - ja - 0.01, L, 0.0, VKI_SOLE_TOP)
    vki_tim_ends(k, L, tb)
    # threshold (visual r2): DRESS, the warm dark dressed stone -- a doorstep that reads as a walkway in plan and at
    # 50 deg (the dark oak board read as a solid dark rectangle; a pale CAP top read as the cap line running on)
    vki_tim_member(k, x0, x1, 0.0, D["thr"], mi=DRESS, bev=0.01)
    jt = D["top"] if full else VKI_TIM_RAIL[1]
    jambs = []
    if full:
        for a, b in ((ja, x0), (x1, L - ja)):
            jambs.append(vki_tim_member(k, a, b, 0.0, jt, bev=0.015))
    else:
        # Cut (visual r2): each jamb stops under ONE continuous cap block from the piece end to the opening (x 0 ..
        # 0.33), so the cap wraps the reveal without the extra joints at 0.19 / 0.2; the jamb runs 5 mm into it
        for a, b in ((ja, x0), (x1, L - ja)):
            jambs.append(vki_tim_member(k, a, b, 0.0, VKI_TIM_RAIL[0] + VKI_TIM_TUCK, bev=0.015))
        for a, b in ((0.0, x0), (x1, L)):
            jambs.append(vki_tim_member(k, a, b, *VKI_TIM_RAIL, top=VKI_CAP))
        # reveal faces (visual r2: the 1.0 m dark oak reveal filled the 0.84 m opening from the north-looking camera,
        # so the partition doorway read as a solid post): VKI_TIM_REVEAL, limewash by default (see there)
        k.bm.normal_update()
        mi_r = {"planks": PLANKS, "cap": VKI_CAP, "limewash": VKI_WALL_A}[VKI_TIM_REVEAL]
        for vs_, sgn in zip(jambs, (1, -1, 1, -1)):
            fs = [f for f in vki_faces_of(vs_) if f.normal.x * sgn > 0.6 and f.normal.z < 0.65]
            if mi_r == VKI_WALL_A:
                k.project(fs, mi_r)
            else:
                vki_proj_long(k, fs, mi_r, VKI_TIM_Z, off=vki_hash_off((0.33 * sgn, 0.0, 0.5)))
        if mi_r == PLANKS:
            k.slot_mats[PLANKS] = "M_VKI_WoodScrubbed"
    sag = vki_tim_sag_fn(L) if full else (lambda x: 0.0)
    if full:
        vki_tim_rails(k, VKI_TIM_STUD_HW, ja + 0.01, [])                     # 1 cm into the jamb (core fix)
        vki_tim_rails(k, L - ja - 0.01, L - VKI_TIM_STUD_HW, [])
        vki_tim_member(k, ja, L - ja, *D["lintel"])
        vki_tim_body(k, ja, L - ja, D["lintel"][1], tb)
        vki_tim_member(k, 0.69, 0.81, D["lintel"][1] - VKI_TIM_TUCK, tb + VKI_TIM_TUCK)   # cripple stud
        vki_tim_member(k, 0.0, L, *VKI_TIM_HEAD, top=VKI_CAP, cuts=vki_tim_grid(L))
        vki_tim_apply_sag(k, sag, *VKI_TIM_HEAD)
        holes = [(ja, 0.0, L - ja, D["lintel"][1])]
    else:
        holes = [(ja, 0.0, L - ja, VKI_TIM_RAIL[1])]
    vki_tim_body_finish(k, L)
    vki_wobble(k, L, "Timber", "A", holes=holes, top_body_fn=lambda x: tb - sag(x), pins=(0.75,))
    T2 = k.T / 2
    k.meta.update(vki_nav="door", vki_nav_open=[x0, x1])
    k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": jt if full else 1.0},
                  vki_trigger=[0.75, -0.65, 1.0, 0.9, 0.8, 2.0], vki_leaf_socket=[x0, -T2 + 0.05, 0.0],
                  vki_leaf_open_deg=90, vki_leaf="SM_VKI_Leaf_Plank_" + height, vki_spawn_local=[0.75, -1.60],
                  vki_prompt_local=[0.75, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])


def vki_tim_door_full(k): vki_tim_door(k, "Full")
def vki_tim_door_cut(k): vki_tim_door(k, "Cut")


# ---------------------------------------------------------------- Rake_150_L / _R (§2.4)
def vki_tim_rake(k, side):
    """Cut profile for u <= 0.32 from the low end, Full profile for u >= 1.18, cap sloping at 66.7 deg between.
    _L: low end at local x = 0 (west walls); _R: low end at x = L (east walls). u = distance from the low end."""
    L = 1.5
    R = VKI_TIM_RAKE
    zb0, zb1 = VKI_TIM_RAIL[0], VKI_TIM_HEAD[0]
    zt0, zt1 = VKI_TIM_RAIL[1], VKI_TIM_HEAD[1]
    X = (lambda u: u) if side == "L" else (lambda u: L - u)

    def cb(u):                                                # cap bottom at distance u from the low end
        if u <= R["lo"]:
            return zb0
        if u >= R["hi"]:
            return zb1
        return zb0 + (zb1 - zb0) * (u - R["lo"]) / (R["hi"] - R["lo"])

    def span(u0, u1):
        return (min(X(u0), X(u1)), max(X(u0), X(u1)))

    def poly(pts):                                            # (u, z) -> (x, z), counter-clockwise kept convex
        p = [(X(u), z) for u, z in pts]
        return p if side == "L" else p[::-1]

    tbf = lambda x: cb(x if side == "L" else L - x)
    # body: three convex pieces (low Cut part, sloped part, high Full part)
    vki_tim_body(k, *span(0.0, R["lo"]), VKI_FOOT_Z, zb0)
    vki_tim_body(k, *span(R["hi"], L), VKI_FOOT_Z, zb1)
    before = set(k.bm.verts)
    vs, fs = vki_prism(k, poly([(R["lo"], VKI_FOOT_Z), (R["hi"], VKI_FOOT_Z), (R["hi"], zb1), (R["lo"], zb0)]),
                       -k.T / 2, k.T / 2, VKI_WALL_A, axis="y")
    for f in fs:
        if f.normal.y > 0.7:
            k.project([f], VKI_WALL_B)
    grid_cut(k, vs, 0.25)
    k.mark_body([v for v in k.bm.verts if v not in before])
    # members
    vki_tim_member(k, 0.0, L, 0.0, VKI_SOLE_TOP)
    tk = VKI_TIM_TUCK
    vki_tim_member(k, *span(0.0, VKI_TIM_STUD_HW), VKI_SOLE_TOP, zb0 + tk)           # low half-stud (Cut)
    vki_tim_member(k, *span(L - VKI_TIM_STUD_HW, L), VKI_SOLE_TOP, zb1 + tk)         # high half-stud (Full)
    # the stud's sloped top runs 5 mm into the rafter (core fix: it lay in the plane of the body's sloped top)
    vs, fs = vki_prism(k, poly([(0.69, VKI_SOLE_TOP), (0.81, VKI_SOLE_TOP), (0.81, cb(0.81) + tk),
                                (0.69, cb(0.69) + tk)]),
                       -VKI_TIM_HW, VKI_TIM_HW, WOOD, axis="y", bevel=VKI_TIM_BEV, project=False)
    vki_proj_long(k, fs, WOOD, VKI_TIM_Z, off=vki_hash_off((0.75, 0, 1.0)))            # stud with a sloped top
    # cap: low flat (= the Cut rail), sloped rafter, high flat (= the head plate)
    vki_tim_member(k, *span(0.0, R["lo"]), zb0, zt0, top=VKI_CAP)
    vki_tim_member(k, *span(R["hi"], L), zb1, zt1, top=VKI_CAP)
    sl = Vector((X(R["hi"]) - X(R["lo"]), 0.0, zb1 - zb0)).normalized()
    # the sloped rafter sits 5 mm behind the faces of the flats, studs and rails (core fix: its faces were in the
    # same +-0.28 planes as the stud and rail stub it meets); the step is invisible at the game camera
    ry = VKI_TIM_HW - VKI_TIM_TUCK
    vs, fs = vki_prism(k, poly([(R["lo"], zb0), (R["hi"], zb1), (R["hi"], zt1), (R["lo"], zt0)]),
                       -ry, ry, WOOD, axis="y", bevel=VKI_TIM_BEV, project=False)
    top = [f for f in fs if f.normal.z > 0.3]
    vki_proj_long(k, [f for f in fs if f not in top], WOOD, sl, off=vki_hash_off((0.75, 0, 2.0)))
    vki_proj_long(k, top, VKI_CAP, sl, off=vki_hash_off((0.75, 0, 2.1)))
    # mid-rail pieces on the Full side of the slope (the first one is cut along the rafter's underside)
    # (its sloped face runs 5 mm into the rafter, core fix: it lay in the plane of the body's sloped top)
    u_s = R["lo"] + (zt0 - tk - zb0) * (R["hi"] - R["lo"]) / (zb1 - zb0)
    vs, fs = vki_prism(k, poly([(R["lo"], zb0), (0.69, zb0), (0.69, zt0), (u_s, zt0), (R["lo"], zb0 + tk)]),
                       -VKI_TIM_HW, VKI_TIM_HW, WOOD, axis="y", bevel=VKI_TIM_BEV, project=False)
    vki_proj_long(k, [f for f in fs if f.normal.z <= 0.65], WOOD, VKI_TIM_X, off=vki_hash_off((0.5, 0, 0.95)))
    vki_proj_long(k, [f for f in fs if f.normal.z > 0.65], VKI_CAP, VKI_TIM_X, off=vki_hash_off((0.5, 0, 0.96)))
    vki_tim_member(k, *span(0.81, L - VKI_TIM_STUD_HW), *VKI_TIM_RAIL, top=VKI_CAP)
    vki_tim_body_finish(k, L)
    vki_wobble(k, L, "Timber", "A", holes=[], top_body_fn=tbf, pins=(0.75,))
    k.meta.update(vki_class="wall", vki_cut_to=VKI_TIM_CUT_TO, vki_rake_low="x0" if side == "L" else "xL",
                  vki_rake_slope_deg=round(math.degrees(math.atan2(zt1 - zt0, R["hi"] - R["lo"])), 2))


def vki_tim_rake_l(k): vki_tim_rake(k, "L")
def vki_tim_rake_r(k): vki_tim_rake(k, "R")


# ---------------------------------------------------------------- Fireplace_300 (§3.2, special)
# hearth light socket (fix r1): raised above the flame tips (was (1.5, -0.6, 0.5), 0.1-0.25 m from the logs and
# flames, which it blew out to white by diffuse / specular light); it still sits inside the firebox, under the Cut
# lintel (0.90) and the Full mouth (1.30), 0.35 m from the brick back
VKI_TIM_HEARTH_LIGHT = (1.5, -0.55, 0.85)
# flame tongues (x, y, height, radius, tilt about Y, spin about Z, bow): flattened toward the camera (-Y), bowed
# G1 (core fix): seven tongues of varied height across the 0.84 m log pile (was four within 0.3 m)
VKI_TIM_FLAMES = ((1.52, -0.45, 0.56, 0.10, 0.0, 0.15, 0.03), (1.36, -0.41, 0.40, 0.08, 0.18, -0.35, -0.035),
                  (1.68, -0.48, 0.46, 0.085, -0.16, 0.30, 0.04), (1.60, -0.37, 0.32, 0.06, -0.06, -0.20, 0.025),
                  (1.27, -0.46, 0.27, 0.062, 0.26, 0.25, -0.03), (1.81, -0.43, 0.30, 0.065, -0.24, -0.30, 0.035),
                  (1.44, -0.51, 0.24, 0.055, 0.10, 0.40, 0.02))
# hearth socket power / radius (G1: 400 W, the §6 maximum, with a softer 0.40 m radius; one value Day and Night)
VKI_TIM_HEARTH_W = 400.0
VKI_TIM_HEARTH_RADIUS = 0.40
# firebox soot (G1: the brick back and cheeks glowed almost as bright as the flames, p90 0.68): vki_dark base + ramp
VKI_TIM_SOOT_BACK = (0.56, 0.34)
VKI_TIM_SOOT_CHEEK = (0.52, 0.34)
VKI_TIM_HEARTH_SOOT = (0.16, 0.22)     # hearth slabs: base + extra toward the mouth (they read as pale polished tile)
# (t along the height, radius factor, heat): a small white-hot root, orange body, deep orange-red tip (heat 0)
# G1: a brighter, longer core (heat 1.0 at the root, 0.88 through the belly) before the orange-red tip
VKI_TIM_FLAME_PROFILE = ((0.0, 0.70, 1.0), (0.14, 1.0, 0.88), (0.32, 0.92, 0.66), (0.52, 0.70, 0.40),
                         (0.72, 0.42, 0.18), (0.88, 0.18, 0.05))


def vki_tim_flame(k, base, h, r, tilt, spin, bow, flat=0.55, nseg=8):
    """fix r1: a closed, smooth-shaded flame tongue -- rings along the height with a swelling then tapering radius,
    flattened across Y (a broad face toward the camera), a bow that leans the tip, heat per ring
    (VKI_TIM_FLAME_PROFILE, tip 0). Replaces the faceted 6-sided cones, which read as paper cones / crystals."""
    rings = []
    for t, rs, ht in VKI_TIM_FLAME_PROFILE:
        dx = bow * math.sin(math.pi * 0.8 * t)
        ring_ = []
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            v = k.bm.verts.new((math.cos(a) * r * rs + dx, math.sin(a) * r * rs * flat, t * h))
            k.set_heat([v], ht)
            ring_.append(v)
        rings.append(ring_)
    tip = k.bm.verts.new((bow * math.sin(math.pi * 0.8), 0.0, h))
    k.set_heat([tip], 0.0)
    fs = [k.bm.faces.new(rings[0][::-1])]
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(nseg):
            fs.append(k.bm.faces.new((A[i], A[(i + 1) % nseg], B[(i + 1) % nseg], B[i])))
    for i in range(nseg):
        fs.append(k.bm.faces.new((rings[-1][i], rings[-1][(i + 1) % nseg], tip)))
    vs = [v for rg in rings for v in rg] + [tip]
    M = Matrix.Translation(base) @ Matrix.Rotation(tilt, 4, "Y") @ Matrix.Rotation(spin, 4, "Z")
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.material_index = GLOW
        f.smooth = True
    k.project(fs, GLOW)
    return vs


def vki_tim_fireplace(k, height):
    """Firebox x 0.90-2.10, z 0-1.00, back at y -0.20 (BRICK, recessed into the wall body). Breast x 0.40-2.60 to
    y -0.85: splayed brick-lined cheeks, oak bressumer at 1.40 (z 1.28-1.50), plaster hood (WALL_A) with a soot fan,
    top at H + 0.04 in CAP. Hearthstone x 0.35-2.65, y -1.45..-0.85, z 0-0.03. Crane + cauldron, firedogs, logs,
    GLOW embers and flames (vki_heat). Cut: cheeks to 0.90 under an oak lintel 0.90-1.00 with a CAP top over the
    0.90 mouth; firebox and hearth intact. Members inside the breast run on face B only (y 0..0.28)."""
    L = 3.0
    full = height == "Full"
    F = VKI_TIM_FP
    tb = VKI_TIM_HEAD[0] if full else VKI_TIM_RAIL[0]
    zr = 1.00 if full else VKI_TIM_RAIL[0]                       # firebox recess top
    fx0, fx1 = F["firebox"]
    bx0, bx1 = F["breast"]
    fy = F["front_y"]
    T2 = k.T / 2
    # wall body around the recess
    p1 = vki_tim_body(k, 0.0, fx0, VKI_FOOT_Z, tb)
    p2 = vki_tim_body(k, fx1, L, VKI_FOOT_Z, tb)
    # the recessed body behind the firebox runs down to the footing in one piece (a separate footing ended in the
    # z 0 plane of the room floor, T5)
    rec = vki_tim_body(k, fx0, fx1, VKI_FOOT_Z, zr, y0=F["back_y"])
    k.bm.normal_update()
    for f in vki_faces_of(rec):
        if f.normal.y < -0.7:
            k.project([f], VKI_BRICK)
    for vs_, sgn in ((p1, 1), (p2, -1)):
        for f in vki_faces_of(vs_):
            c = f.calc_center_median()
            if f.normal.x * sgn > 0.7 and 0.0 <= c.z <= zr:
                k.project([f], VKI_BRICK)
    if full:
        ab = vki_tim_body(k, fx0, fx1, zr, tb)
        for f in vki_faces_of(ab):
            if f.normal.z < -0.7:
                k.project([f], VKI_BRICK)
    # members: full depth outside the breast, face B only inside it
    studs = vki_tim_studs(L)
    vki_tim_member(k, 0.0, bx0, 0.0, VKI_SOLE_TOP)
    vki_tim_member(k, bx1, L, 0.0, VKI_SOLE_TOP)
    vki_tim_member(k, bx0, bx1, 0.0, VKI_SOLE_TOP, y0=0.0)
    vki_tim_ends(k, L, tb)
    for s in studs:
        vki_tim_member(k, s - VKI_TIM_STUD_HW, s + VKI_TIM_STUD_HW, VKI_SOLE_TOP, tb + VKI_TIM_TUCK, y0=0.0)
    sag = vki_tim_sag_fn(L) if full else (lambda x: 0.0)
    if full:
        vki_tim_rails(k, VKI_TIM_STUD_HW, bx0, [])
        vki_tim_rails(k, bx1, L - VKI_TIM_STUD_HW, [])
        # inside the breast the mid-rail is only its proud strip on face B (y 0.25..0.28, core fix: a rail from y 0
        # put its top in the plane of the recess body's top, z 1.00, buried between the recess and the body above)
        vki_tim_rails(k, bx0, bx1, studs, y0=T2)
        vki_tim_member(k, 0.0, L, *VKI_TIM_HEAD, top=VKI_CAP, cuts=vki_tim_grid(L))
    else:
        vki_tim_member(k, 0.0, L, *VKI_TIM_RAIL, top=VKI_CAP)
    # breast: cheeks with splayed brick-lined inner faces
    mt = F["mouth_top"] if full else VKI_TIM_RAIL[0]
    mx0, mx1 = F["mouth"]
    for pl in ([(bx0, fy), (mx0, fy), (fx0, -T2), (bx0, -T2)], [(bx1, fy), (bx1, -T2), (fx1, -T2), (mx1, fy)]):
        vs, fs = vki_prism(k, pl, 0.0, mt, VKI_WALL_A, axis="z")
        vs = vki_cut(k, vs, zs=[z for z in (0.25, 0.5, 0.75, 1.0, 1.25) if z < mt - 0.05])
        k.bm.normal_update()
        for f in vki_faces_of(vs):
            n = f.normal
            if abs(n.z) < 0.5 and abs(n.x) > 0.3 and abs(n.y) > 0.1:        # the splayed inner face
                k.project([f], VKI_BRICK)
        for v in vs:
            if abs(v.co.x - 1.5) < 0.85:
                k.set_dark([v], VKI_TIM_SOOT_CHEEK[0] + VKI_TIM_SOOT_CHEEK[1] * vki_smoothstep(0.2, mt, v.co.z))
    if full:
        before = set(k.bm.verts)
        hood = list(set(k.box(((bx0 + bx1) / 2, (fy - T2) / 2, (mt + 3.04) / 2), (bx1 - bx0, -T2 - fy, 3.04 - mt),
                              VKI_WALL_A, bevel=0)))
        grid_cut(k, hood, 0.25)
        hood = [v for v in k.bm.verts if v not in before]
        k.bm.normal_update()
        for f in vki_faces_of(hood):
            if f.normal.z < -0.7:
                k.project([f], VKI_BRICK)
            elif f.normal.z > 0.7:
                k.project([f], VKI_CAP)
        for v in hood:                                                          # soot fan over the bressumer
            if abs(v.co.y - fy) < 1e-4 or v.co.z < mt + 1e-4:
                k.set_dark([v], 0.42 * (1 - vki_smoothstep(0.25, 1.0, abs(v.co.x - 1.5))) *
                           (1 - vki_smoothstep(1.5, 2.7, v.co.z)))
        vki_tim_member(k, bx0 - 0.03, bx1 + 0.03, *F["bress"], y0=fy - 0.03, y1=-0.60)           # bressumer
        tk = VKI_TIM_TUCK                     # throat: back and top 5 mm into the wall / hood (core fix)
        vs, fs = vki_prism(k, [(-T2 + tk, zr), (-T2 + tk, mt + tk), (-0.47, mt + tk)], mx0 + 0.10, mx1 - 0.10,
                           VKI_BRICK, axis="x")
        k.set_dark(vs, 0.55)                                                    # throat (smoke shelf)
    else:
        vki_tim_member(k, bx0 - 0.03, bx1 + 0.03, *VKI_TIM_RAIL, y0=fy - 0.03, y1=-VKI_TIM_HW, top=VKI_CAP)  # lintel
    # recess + soffit soot
    for v in rec:
        if abs(v.co.y - F["back_y"]) < 1e-4:
            k.set_dark([v], VKI_TIM_SOOT_BACK[0] + VKI_TIM_SOOT_BACK[1] * vki_smoothstep(0.1, zr, v.co.z))
    for vs_, xe in ((p1, fx0), (p2, fx1)):          # the firebox side walls (brick ends of the wall body)
        for v in vs_:
            if abs(v.co.x - xe) < 1e-4 and v.co.y < 0.0 and v.co.z <= zr + 1e-4:
                k.set_dark([v], VKI_TIM_SOOT_CHEEK[0] + VKI_TIM_SOOT_CHEEK[1] * vki_smoothstep(0.1, zr, v.co.z))
    # hearth (fix r1: DRESS, the warm dark dressed stone -- the pale StoneBlockIn slabs right under the fire were the
    # brightest surface in the frame by Day, brighter than the flames)
    hx0, hx1, hy0, hy1 = F["hearth"]
    for a, b in ((hx0, 1.10), (1.10, 1.90), (1.90, hx1)):
        vs = k.box(((a + b) / 2, (hy0 + hy1) / 2, 0.015), (b - a, hy1 - hy0, 0.03), DRESS, bevel=0.012)
        for v in set(vs):                  # G1: sooty toward the fire, so the lit slabs stay below the glass
            k.set_dark([v], VKI_TIM_HEARTH_SOOT[0] + VKI_TIM_HEARTH_SOOT[1] *
                       vki_smoothstep(hy0, hy1, v.co.y) * (1 - vki_smoothstep(0.4, 1.2, abs(v.co.x - 1.5))))
    # firebox floor: its bottom 5 mm below the floor top (core fix: it lay in the z 0 plane of the cheeks' bottoms)
    k.set_dark(k.box((1.5, (fy + F["back_y"]) / 2, 0.0125), (mx1 - mx0 - 0.04, F["back_y"] - fy, 0.035), DRESS,
                     bevel=0.0), 0.35)
    vs = k.box((1.5, -0.44, 0.045), (1.0, 0.44, 0.04), VKI_ASH, bevel=0.018, segs=2)            # ash bed
    k.set_dark(vs, 0.15)
    # firedogs
    for x in (1.14, 1.86):
        k.box((x, -0.64, 0.15), (0.045, 0.045, 0.30), IRON, bevel=0.01)
        k.box((x, -0.44, 0.10), (0.04, 0.40, 0.04), IRON, bevel=0.008)
        k.box((x, -0.66, 0.31), (0.07, 0.07, 0.03), IRON, bevel=0.01)
    # logs on the firedogs (oak bark, charred: darker overall and black underneath; each end shows one whole log
    # end of the ENDGRAIN tile, fix r1)
    rx = Matrix.Rotation(math.pi / 2, 4, "Y")
    for (y, z, r, ln, rz) in ((-0.36, 0.175, 0.065, 0.84, 0.05), (-0.53, 0.17, 0.06, 0.80, -0.06),
                              (-0.445, 0.285, 0.055, 0.66, 0.12)):
        vs = _cyl(k, (1.52, y, z), r, r * 0.92, ln, 8, BARK_OAK, rot=Matrix.Rotation(rz, 4, "Z") @ rx)
        k.bm.normal_update()
        ax_ = Matrix.Rotation(rz, 3, "Z") @ VKI_TIM_X
        for f in [f for f in vki_faces_of(vs) if abs(f.normal.dot(ax_)) > 0.9]:
            U = f.normal.cross(VKI_TIM_Z).normalized()
            vki_endgrain_fit(k, [f], f.calc_center_median(), U, f.normal.cross(U), r, fill=VKI_ENDGRAIN_R)
        for v in vs:
            k.set_dark([v], 0.70 if v.co.z < z else 0.40)
    # embers (GLOW: hot core under the logs, cooler rim) and four flame tongues
    rnd = random.Random(3301)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.3, 0.3); rr = rnd.uniform(0.05, 0.30)
        c = Vector((1.52 + math.cos(a) * rr * 1.3, -0.44 + math.sin(a) * rr * 0.55, 0.075))
        vs = _ico(k, c, rnd.uniform(0.045, 0.07), GLOW, scale=(1.0, 1.0, 0.55), sub=1, jit=0.008, seed=3310 + i)
        for v in vs:
            k.set_heat([v], vki_clamp(1.0 - (v.co - Vector((1.52, -0.44, 0.05))).length / 0.42))
        k.project(vki_faces_of(vs), GLOW)
    for (x, y, h, r, tilt, spin, bow) in VKI_TIM_FLAMES:
        vki_tim_flame(k, (x, y, 0.20), h, r, tilt, spin, bow)
    # crane and cauldron (iron): the crane is swung toward the west cheek so the pot hangs beside the fire, not in
    # front of it (from the 50 deg camera a pot over the flames hid the whole fire); the arm at 0.82 clears the Cut
    # lintel
    # (G1: swung further out toward the west cheek, so the pot hangs clear of the widened fire, x < 1.21)
    _tube(k, (0.95, -0.30, 0.02), (0.95, -0.30, 0.86), 0.022, IRON)
    _tube(k, (0.95, -0.30, 0.80), (1.01, -0.66, 0.80), 0.02, IRON)
    _tube(k, (0.95, -0.30, 0.55), (0.985, -0.50, 0.80), 0.015, IRON)
    px, py = 1.0, -0.62
    _tube(k, (px, py, 0.80), (px, py, 0.58), 0.008, IRON)
    _cyl(k, (px, py, 0.465), 0.15, 0.205, 0.13, 10, IRON)
    _cyl(k, (px, py, 0.575), 0.205, 0.17, 0.09, 10, IRON)
    _cyl(k, (px, py, 0.405), 0.10, 0.15, 0.03, 10, IRON)
    if full:
        vki_tim_apply_sag(k, sag, *VKI_TIM_HEAD)
    vki_tim_body_finish(k, L)
    vki_wobble(k, L, "Timber", "A", holes=[(fx0, 0.0, fx1, zr)], top_body_fn=lambda x: tb - sag(x), pins=studs)
    k.meta.update(vki_class="wall", vki_special=1,
                  vki_lights=[dict(type="POINT", role="hearth", pos=list(VKI_TIM_HEARTH_LIGHT), w=VKI_TIM_HEARTH_W,
                                   color=[1.0, .52, .22], range=7.0, flicker=1, shadows=1,
                                   radius=VKI_TIM_HEARTH_RADIUS)],
                  vki_fx=[dict(fx="fire_small", pos=[1.5, -0.5, 0.2])],
                  vki_collider=[[1.5, 0.0, 1.1, 3.0, k.T, 2.2], [1.5, (fy - T2) / 2, 1.1, bx1 - bx0, -T2 - fy, 2.2]])


def vki_tim_fireplace_full(k): vki_tim_fireplace(k, "Full")
def vki_tim_fireplace_cut(k): vki_tim_fireplace(k, "Cut")


# ---------------------------------------------------------------- posts (§2.3)
def vki_tim_post(k, kind, height):
    """oak post centred on its node, z -0.30 .. wall top + 0.04, bevel 0.02, top face ENDGRAIN.
    Corner +-0.31 square; Mid +-0.12 along the wall (local x) x +-0.31 across."""
    k.set_family("Timber")
    top = (VKI_H_FULL["Timber"] if height == "Full" else VKI_CUT_H) + VKI_POST_TOP
    ax, ay = (VKI_POST_HW["O"], VKI_POST_HW["O"]) if kind == "Corner" else VKI_MID_HW["O"]
    c = (0.0, 0.0, (VKI_POST_Z0 + top) / 2); sz = (2 * ax, 2 * ay, top - VKI_POST_Z0)
    vs = list(set(k.box(c, sz, WOOD, bevel=VKI_POST_BEVEL)))
    k.bm.normal_update()
    # fix r1: the top (and its chamfers) shows ONE centred log end: the post square maps inside the painted ring's
    # inscribed square (Corner 0.62 -> uv 0.20..0.80; Mid 0.24 x 0.62 -> a centred strip of the same ring)
    tops = [f for f in vki_faces_of(vs) if f.normal.z > 0.65]
    if VKI_TIM_POST_TOP == "cap":
        # hewn CAP with its grain ACROSS the post (local y), so a post top reads as a hewn member end, not a log
        vki_top_faces(k, vs, VKI_CAP, c, sz, along=VKI_TIM_Y)
    else:
        # core fix: padded fill (0.26, was 0.30): the post corners stay at uv radius 0.37, well inside the ring (0.44)
        vki_endgrain_fit(k, tops, (0.0, 0.0, top), VKI_TIM_X, VKI_TIM_Y, max(ax, ay), fill=VKI_TIM_POST_FILL)
    other = "Cut" if height == "Full" else "Full"
    rule = {"Corner": "L/T/X junction (required, T12 error if missing); height = tallest wall-end height present "
                      "(a rake contributes its end height)",
            "Mid": "height/family/class step on a straight run (required) | free end (warning) | rhythm at even "
                   "nodes (optional; skipped where a wall-backed / wall-hung prop or a stair spans the node)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": f"SM_VKI_Post_Timber_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_tim_post_corner_full(k): vki_tim_post(k, "Corner", "Full")
def vki_tim_post_corner_cut(k): vki_tim_post(k, "Corner", "Cut")
def vki_tim_post_mid_full(k): vki_tim_post(k, "Mid", "Full")
def vki_tim_post_mid_cut(k): vki_tim_post(k, "Mid", "Cut")


VKI_TIM_SPECS = [
    ("SM_VKI_Wall_Timber_Plain_150A_Full", vki_tim_plain_150a_full),
    ("SM_VKI_Wall_Timber_Plain_150A_Cut", vki_tim_plain_150a_cut),
    ("SM_VKI_Wall_Timber_Plain_150B_Full", vki_tim_plain_150b_full),
    ("SM_VKI_Wall_Timber_Plain_300_Full", vki_tim_plain_300_full),
    ("SM_VKI_Wall_Timber_Plain_300_Cut", vki_tim_plain_300_cut),
    ("SM_VKI_Wall_Timber_Window_150_Full", vki_tim_window_full),
    ("SM_VKI_Wall_Timber_Window_150_Cut", vki_tim_window_cut),
    ("SM_VKI_Wall_Timber_Door_150_Full", vki_tim_door_full),
    ("SM_VKI_Wall_Timber_Door_150_Cut", vki_tim_door_cut),
    ("SM_VKI_Wall_Timber_Rake_150_L", vki_tim_rake_l),
    ("SM_VKI_Wall_Timber_Rake_150_R", vki_tim_rake_r),
    ("SM_VKI_Wall_Timber_Fireplace_300_Full", vki_tim_fireplace_full),
    ("SM_VKI_Wall_Timber_Fireplace_300_Cut", vki_tim_fireplace_cut),
    ("SM_VKI_Post_Timber_Corner_Full", vki_tim_post_corner_full),
    ("SM_VKI_Post_Timber_Corner_Cut", vki_tim_post_corner_cut),
    ("SM_VKI_Post_Timber_Mid_Full", vki_tim_post_mid_full),
    ("SM_VKI_Post_Timber_Mid_Cut", vki_tim_post_mid_cut),
]
VKI_TIM_NAMES = [n for n, _ in VKI_TIM_SPECS]
vki_register([(n, fn, {"grime": "wall"}, "core") for n, fn in VKI_TIM_SPECS])
