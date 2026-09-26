# ===================== VKI FAM WATTLE: the Wattle wall family (§2.2, §3.1, §3.2) -- 15 masters =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (its §10 overrides). Package "wattle" (PACKAGES.md).
# Loaded by vki_ns() after vki_fam_timber, whose generic helpers it reuses at build time (vki_cut, vki_prism,
# vki_proj_long, vki_top_faces, vki_endgrain_fit, vki_hash_off, vki_faces_of, vki_tim_member, vki_tim_sag_fn,
# vki_tim_apply_sag, vki_tim_grid). Every top-level name starts with vki_/VKI_ (T18).
#
# Section (class P, T 0.30, H 2.4), piece-local, room on -Y:
#   body  PlasterDaub +-0.15 (WALL_A -Y / WALL_B +Y), z -0.30 .. cap bottom, grid_cut 0.25 (+ a row at 0.90 on
#         Full-height panels). Pillowed by the §2.6 wobble (A 0.020: zero at the node studs, the sole, the cap, the
#         Full rail and around openings, so the daub swells between the members). Soot band above 1.4 in vki_dark.
#         Footing band below z 0 DRESS and darker; body tops oak; oak plugs behind the half-stud tops (as Timber).
#   hewn oak members +-0.18 (CAP_HW), WOOD, bevel 0.02:
#     sole beam 0 .. 0.16 | half-studs x 0..0.07 / L-0.07..L (a 0.14 stud at every node; a full stud at 1.5 on 300s)
#     rail 0.90 .. 1.00 (the Cut cap, top CAP; also on Full walls between the studs)
#     wall plate 2.28 .. 2.40 (Full, top CAP). Rail and plate sag 0.020 end-pinned (zero within NODE_FLAT).
#   Plain_150B: a bare INFILL (WattleIn) patch above 1.2 -- the daub knocked off, 22 mm deep, ragged rim.
#   Window_150 (unglazed x 0.45-1.05, z 1.00-1.60): hewn jambs standing on the rail (= the sill), a hewn lintel,
#     2 rods, a top-hung board shutter propped open 55 deg into the room (inside the R-occ6 zone: x 0.42-1.08,
#     y >= -0.75, z >= 1.20), daylight card at y +0.10 (WINDOW -> M_VKI_Daylight per master).
#     Cut: plain Cut wall whose cap over x 0.33-1.17 is a CAP sill slab (|y| <= 0.18) + a light-pool anchor.
#   Door_150 (0.84 x 2.00): hewn jambs, crooked lintel (tilted 3 cm, bowed, unevenly hewn), DRESS threshold.
#     Cut: jambs stop under one cap block from the piece end to the opening; reveal faces limewash (WALL_A).
#   Rake_150_L/R: Cut profile for u <= 0.32 from the low end, Full for u >= 1.18, the cap slopes 58.4 deg between.
#   Posts: Corner +-0.21, a crooked hewn post (each face bows IN by up to 0.02, never out, so it stays inside the
#     envelope and the top / foot are the full square); Mid +-0.10 x +-0.21 thin hewn post (bows <= 0.012).
#     ENDGRAIN tops (one padded log end, as Timber); soot on the Full posts' sides above 1.4.
# Build (package engineer): g["vki_ws_build"]("wattle", VKI_WAT_NAMES); test: g["vki_test_pieces"](VKI_WAT_NAMES).
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_WAT_HW = 0.18                  # members' half width (= CAP_HW, class P)
VKI_WAT_BEV = 0.02                  # hewn member bevel
VKI_WAT_STUD_HW = 0.07              # half-stud at each piece end (every node shows one 0.14 stud)
VKI_WAT_RAIL = (0.90, 1.00)         # the Cut cap (hewn oak rail); the same rail runs on Full walls
VKI_WAT_PLATE = (2.28, 2.40)        # the sagging wall plate (H - 0.12 .. H)
VKI_WAT_TUCK = 0.005                # a member butting into a cap / lintel runs this far into it (T5S, §10.1)
VKI_WAT_OPEN = (0.33, 1.17)         # door opening / window frame (x)
VKI_WAT_FOOT_TOP = -0.10            # footing under a door opening stops at the floor-slab bottom
VKI_WAT_FOOT_DARK = 0.22            # extra darkening on the footing band (below z 0)
VKI_WAT_PIN_CELL = 0.025            # oak plug behind each half-stud's chamfered top corner (joint pinhole, as Timber)
VKI_WAT_CUT_TO = "SM_VKI_Wall_Wattle_Plain_150A_Cut"
# soot band (§2.2 "soot above 1.4 is written to vki_dark"): daub and post sides darken from z0 to full at z1
# (0.42 on the daub was barely visible in the first game shot; 0.58 reads as a smoke-blackened upper wall)
VKI_WAT_SOOT = dict(z0=1.40, z1=2.20, body=0.58, post=0.30)
# Plain_150B patch: centre (x, z), half sizes, the face-A zone of whole 0.25 grid cells it replaces, recess depth,
# broken-rim width range, outline points and ragged-outline harmonics (m, amplitude, phase)
VKI_WAT_PATCH = dict(c=(0.78, 1.66), r=(0.30, 0.34), zone=(0.25, 1.25, 1.00, 2.25), depth=0.022, lip=(0.010, 0.024),
                     n=28, seed=5171, harm=((2, 0.15, 0.7), (3, 0.10, 2.1), (5, 0.06, 4.0), (7, 0.04, 0.4)))
# window (§3.2 Wattle): clear opening x 0.45-1.05, z 1.00-1.60
# jamb_top: jambs and rods run 3 cm up into the lintel, their front faces staying below its bevelled front face
# (T5S); the card stops 5 mm lower so its top is not in the jamb tops' plane
VKI_WAT_WIN = dict(x=(0.45, 1.05), sill=1.00, head=1.60, lintel=(0.25, 1.25, 1.60, 1.76), lintel_crook=(0.010, 0.008,
                   0.006), jamb_top=1.63, rods=(0.65, 0.85), rod_y=0.0, rod_r=0.021, card_y=0.10,
                   shutter_deg=170.0, hinge=(-0.195, 1.61), board=(0.66, 0.64, 0.035), prop_x=0.25)
# shutter_deg: 170 = swung up against the wall above the opening (coordinator, 2026-09-26). The spec's 55 deg propped
# inward faced the 50 deg game camera and hid the opening on north walls; any inward prop hides it from above. Angles
# above 120 drop the prop stick (the board hangs on its hook); 55 still builds the propped version.
# window spot (like VKI_TIM_WIN_SPOT, re-aimed for the low 1.00-1.60 opening): through the opening onto the floor
# about 1.2-2.0 m into the room, passing under the propped shutter
VKI_WAT_WIN_SPOT = dict(pos=(0.75, 1.8, 2.9), aim=(0.75, -1.5, 0.0), cone=24.0, blend=0.15, radius=0.05,
                        w_day=900.0, w_night=120.0)
# door (§3.2 Wattle): 0.84 x 2.00, crooked lintel x 0.14-1.36, bottom 2.00 (+ crook, never lower), 0.18 deep.
# jamb_top 2.04: inside the lintel at both jambs (its underside is 2.003-2.009 over the left jamb, 2.031 over the
# right one), while the jambs' bevelled front / back faces end at 2.025, below the lintel's (>= 2.034): T5S
VKI_WAT_DOOR = dict(top=2.00, jamb=(0.19, 0.33), thr=0.03, lintel=(0.14, 1.36, 2.00, 2.18), crook=(0.030, 0.015,
                    0.008), jamb_top=2.04)
VKI_WAT_RAKE = dict(lo=0.32, hi=1.18)            # Cut profile up to 0.32 from the low end, Full from 1.18
# post bows (inward, per face +x, -x, +y, -y, metres) and profile exponents (where along the shaft each face bows)
VKI_WAT_POST_BOW = {"Corner": (0.018, 0.006, 0.008, 0.016), "Mid": (0.012, 0.004, 0.007, 0.010)}
VKI_WAT_POST_BOW_P = (0.8, 1.35, 1.1, 0.9)


# ---------------------------------------------------------------- building blocks
def vki_wat_member(k, x0, x1, z0, z1, mi=None, top=None, bev=VKI_WAT_BEV, cuts=(), y0=-VKI_WAT_HW, y1=VKI_WAT_HW):
    """a hewn oak member box (WOOD by default), +-0.18 deep; top: slot of its upward faces (CAP, grain along X)"""
    return vki_tim_member(k, x0, x1, z0, z1, y0=y0, y1=y1, mi=mi, top=top, bev=bev, cuts=cuts)


def vki_wat_body(k, x0, x1, z0, z1):
    """a daub body panel (k.body_box, grid 0.25); Full-height panels get a vertex row at 0.90 too, so the wobble
    can flatten the daub right under the Full rail (every Full piece has it at its ends: T2)"""
    vs = k.body_box(x0, x1, z0, z1)
    if z0 < VKI_WAT_RAIL[0] - 0.05 and z1 > VKI_WAT_RAIL[1] + 0.05:
        vs = vki_cut(k, vs, zs=[VKI_WAT_RAIL[0]])
        k.mark_body(vs)
    return vs


def vki_wat_sag_fn(L):
    """end-pinned sag of the rail and the plate: 0.020 (§2.6) at mid-span, zero within NODE_FLAT of every node"""
    amp = VKI_FAMILIES["Wattle"]["sag"] if VKI_FLAGS.get("sag", True) else 0.0
    return vki_tim_sag_fn(L, amp)


def vki_wat_ends(k, L, tb0, tb1=None):
    """the two half-studs (sole top .. 5 mm into the cap above; tb1: the high end of a rake)"""
    tb1 = tb0 if tb1 is None else tb1
    vki_wat_member(k, 0.0, VKI_WAT_STUD_HW, VKI_SOLE_TOP, tb0 + VKI_WAT_TUCK)
    vki_wat_member(k, L - VKI_WAT_STUD_HW, L, VKI_SOLE_TOP, tb1 + VKI_WAT_TUCK)


def vki_wat_crooked(k, x0, x1, z0, z1, crook, n=8, bev=0.025):
    """a crooked hewn beam x0..x1, z0..z1: every vertex rises by tilt*t + bow*sin(pi t), the top faces also by
    wave*sin(2 pi t) (uneven hewing); t = (x - x0) / (x1 - x0). crook = (tilt, bow, wave); all >= 0 at the bottom, so
    the underside never drops below z0 (clear openings keep their height)"""
    tilt, bow, wave = crook
    vs = vki_wat_member(k, x0, x1, z0, z1, bev=bev, cuts=[x0 + (x1 - x0) * i / n for i in range(1, n)])
    zm = (z0 + z1) / 2
    for v in vs:
        t = (v.co.x - x0) / (x1 - x0)
        dz = tilt * t + bow * math.sin(math.pi * t)
        if v.co.z > zm:
            dz += wave * math.sin(2 * math.pi * t)
        v.co.z += dz
    return vs


def vki_wat_rod(k, a, b, r, segs=6, mi=None):
    """round rod a -> b (grain along it)"""
    mi = WOOD if mi is None else mi
    a = Vector(a); b = Vector(b); d = b - a
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    vs = _cyl(k, (a + b) / 2, r, r, d.length, segs, mi, rot=q)
    vki_proj_long(k, vki_faces_of(vs), mi, d.normalized(), off=vki_hash_off(tuple(a)))
    return vs


def vki_wat_body_finish(k, L):
    """as vki_tim_body_finish, with the class P section: (1) the footing band below z 0 (body +-Y faces with every
    vertex at z <= 0) becomes DRESS at t 1.5, darker; (2) the body's upward faces (always under a rail, plate or
    lintel) become oak; (3) small oak plugs in front of the body faces' top corners at each end (x 0.001..0.025),
    inside the half-studs, so the chamfer notch at a butt joint shows oak, not daub"""
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
            k.set_dark([v], VKI_WAT_FOOT_DARK * vki_smoothstep(0.0, -0.15, v.co.z) + 0.08)
    T2 = k.T / 2
    for xe, sgn in ((0.0, 1), (L, -1)):
        if zt[xe] is None:
            continue
        x0, x1 = sorted((xe + sgn * 0.001, xe + sgn * VKI_WAT_PIN_CELL))
        for ys in (-1, 1):
            y0, y1 = sorted((ys * (T2 + 0.0005), ys * (VKI_WAT_HW - 0.01)))
            k.box(((x0 + x1) / 2, (y0 + y1) / 2, zt[xe] - 0.013), (x1 - x0, y1 - y0, 0.024), WOOD, bevel=0)


def vki_wat_soot(k):
    """the soot band: body vertices above 1.4 darken (vki_dark) toward the plate -- the open hearth's smoke"""
    S = VKI_WAT_SOOT
    for v in k.bm.verts:
        if v[k.body] and v.co.z > S["z0"]:
            k.set_dark([v], S["body"] * vki_smoothstep(S["z0"], S["z1"], v.co.z))


def vki_wat_wobble(k, L, variant, holes, tbf):
    """§2.6 (A 0.020 for Wattle): the pillowed daub; call it last"""
    vki_wobble(k, L, "Wattle", variant, holes=holes, top_body_fn=tbf, pins=())


def vki_wat_rail_hole(L, x0=0.0, x1=None):
    """wobble 'hole' over the Full rail (sagged down to 0.88), so the daub goes flat against it"""
    return (x0, VKI_WAT_RAIL[0] - 0.02, L if x1 is None else x1, VKI_WAT_RAIL[1])


# ---------------------------------------------------------------- Plain_150B patch
def vki_wat_patch(k):
    """bare INFILL patch above 1.2 (§2.2 _B), the daub knocked off: the face-A cells of the zone (whole 0.25 grid
    cells) are deleted and the rectangular hole is refilled with (1) a daub ring zipped (by angle round the patch
    centre) from the hole's grid vertices to a smooth ragged outline, (2) a broken rim sloping 22 mm into the wall
    with a jittered lip, (3) the recessed floor, one INFILL (WattleIn, world-locked) polygon. The outline vertices lie
    on face A (body, so they wobble with the daub); the recessed ones are not at |y| = T/2, so the wobble leaves them
    alone (T13 builds the same patch with and without wobble). Replaces a finer-grid recess whose outline stair-
    stepped along the grid (review of the first renders)."""
    P = VKI_WAT_PATCH
    cx, cz = P["c"]; rx, rz = P["r"]; x0, x1, z0, z1 = P["zone"]
    ya = -k.T / 2
    k.bm.normal_update()
    zone = [f for f in k.bm.faces if f.material_index == VKI_WALL_A and f.normal.y < -0.7 and
            all(v[k.body] for v in f.verts) and x0 < f.calc_center_median().x < x1 and
            z0 < f.calc_center_median().z < z1]
    zverts = list({v for f in zone for v in f.verts})
    bmesh.ops.delete(k.bm, geom=zone, context="FACES")
    # the hole's boundary = the zone vertices that survive (the interior ones went with the faces); not a z test --
    # the rail sag has already lowered the zone's bottom row below 1.00
    bnd = [v for v in zverts if v.is_valid]

    def ang(x, z):
        return math.atan2(z - cz, x - cx)
    A = sorted(bnd, key=lambda v: ang(v.co.x, v.co.z))
    pts = []
    for i in range(P["n"]):
        a = 2 * math.pi * i / P["n"]
        R = 1.0 + sum(amp * math.sin(m * a + ph) for m, amp, ph in P["harm"])
        pts.append((cx + rx * R * math.cos(a), cz + rz * R * math.sin(a)))
    pts.sort(key=lambda p: ang(*p))
    B = [k.bm.verts.new((x, ya, z)) for x, z in pts]
    aA = [ang(v.co.x, v.co.z) for v in A]
    aB = [ang(x, z) for x, z in pts]
    M, N = len(A), len(B)
    new = []
    i = j = 0
    while i < M or j < N:                           # zipper triangulation between the two angle-sorted loops
        na = (aA[(i + 1) % M] + (2 * math.pi if i + 1 >= M else 0.0)) if i < M else 1e9
        nb = (aB[(j + 1) % N] + (2 * math.pi if j + 1 >= N else 0.0)) if j < N else 1e9
        if na <= nb:
            new.append(k.bm.faces.new((A[i % M], A[(i + 1) % M], B[j % N]))); i += 1
        else:
            new.append(k.bm.faces.new((A[i % M], B[(j + 1) % N], B[j % N]))); j += 1
    rnd = random.Random(P["seed"])
    inner = []
    for x, z in pts:
        d = Vector((x - cx, z - cz)); s = max(0.0, (d.length - rnd.uniform(*P["lip"])) / d.length)
        inner.append(k.bm.verts.new((cx + d.x * s, ya + P["depth"], cz + d.y * s)))
    rim = [k.bm.faces.new((B[jj], B[(jj + 1) % N], inner[(jj + 1) % N], inner[jj])) for jj in range(N)]
    floor = k.bm.faces.new(inner)
    k.bm.normal_update()
    front = Vector((cx, ya - 0.05, cz))
    for f in new + [floor]:
        if f.normal.y > 0:
            f.normal_flip()
    for f in rim:
        if f.normal.dot(front - f.calc_center_median()) < 0:
            f.normal_flip()
    k.bm.normal_update()
    k.mark_body(B + inner)
    k.project(new + rim, VKI_WALL_A)
    k.project([floor], VKI_INFILL)
    return [floor]


# ---------------------------------------------------------------- Plain (150A, 150B, 300), Full and Cut
def vki_wat_plain(k, L, height, variant="A", patch=False):
    full = height == "Full"
    tb = VKI_WAT_PLATE[0] if full else VKI_WAT_RAIL[0]
    sag = vki_wat_sag_fn(L)
    grid = vki_tim_grid(L)
    vki_wat_body(k, 0.0, L, VKI_FOOT_Z, tb)
    vki_wat_member(k, 0.0, L, 0.0, VKI_SOLE_TOP)                          # sole beam
    vki_wat_ends(k, L, tb)
    studs = [1.5] if L > 1.6 else []                                     # 300 = 150 (+) 150: a full stud at 1.5
    for s in studs:
        vki_wat_member(k, s - VKI_WAT_STUD_HW, s + VKI_WAT_STUD_HW, VKI_SOLE_TOP, tb + VKI_WAT_TUCK)
    if full:
        xs = [VKI_WAT_STUD_HW] + [v for s in studs for v in (s - VKI_WAT_STUD_HW, s + VKI_WAT_STUD_HW)] + \
             [L - VKI_WAT_STUD_HW]
        for i in range(0, len(xs), 2):                                   # rail between the studs
            vki_wat_member(k, xs[i], xs[i + 1], *VKI_WAT_RAIL, top=VKI_CAP, cuts=grid)
        vki_wat_member(k, 0.0, L, *VKI_WAT_PLATE, top=VKI_CAP, cuts=grid)  # wall plate
        vki_tim_apply_sag(k, sag, *VKI_WAT_RAIL)
        vki_tim_apply_sag(k, sag, *VKI_WAT_PLATE)
    else:
        vki_wat_member(k, 0.0, L, *VKI_WAT_RAIL, top=VKI_CAP, cuts=grid)   # the Cut cap
        vki_tim_apply_sag(k, sag, *VKI_WAT_RAIL)
    if patch:
        vki_wat_patch(k)
    vki_wat_body_finish(k, L)
    vki_wat_soot(k)
    vki_wat_wobble(k, L, variant, [vki_wat_rail_hole(L)] if full else [], lambda x: tb - sag(x))
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_WAT_CUT_TO)


def vki_wat_plain_150a_full(k): vki_wat_plain(k, 1.5, "Full", "A")
def vki_wat_plain_150a_cut(k): vki_wat_plain(k, 1.5, "Cut", "A")
def vki_wat_plain_150b_full(k): vki_wat_plain(k, 1.5, "Full", "B", patch=True)
def vki_wat_plain_300_full(k): vki_wat_plain(k, 3.0, "Full", "A")
def vki_wat_plain_300_cut(k): vki_wat_plain(k, 3.0, "Cut", "A")


# ---------------------------------------------------------------- Window_150 (§3.2 Wattle)
def vki_wat_plank_uv(k, fs, U, V, u0, width, j, voff):
    """map faces onto ONE painted plank column j (of 8) of T_VK_Planks: u across the board, v along it (t 2.0), so a
    0.16 m board never shows a painted plank joint"""
    for f in fs:
        f.material_index = PLANKS
        for l in f.loops:
            p = l.vert.co
            s = min(1.0, max(0.0, (p.dot(U) - u0) / width))
            l[k.uv].uv = ((j + 0.06 + 0.88 * s) / 8.0, p.dot(V) / 2.0 + voff)


def vki_wat_shutter(k):
    """top-hung board shutter, open by VKI_WAT_WIN["shutter_deg"] (170: swung up against the wall; <=120: propped into the room): four vertical boards (PLANKS), two battens and two
    iron straps on the room face, and a prop stick standing on the sill. Built in the hinge frame (hinge line along
    X at W['hinge'], the board hanging along -Z with its back at local y 0) and turned -55 deg about X, so its lower
    edge swings up into the room (y -0.72, z 1.24)"""
    W = VKI_WAT_WIN
    bw, bl, bt = W["board"]
    hy, hz = W["hinge"]
    M = Matrix.Translation((0.75, hy, hz)) @ Matrix.Rotation(math.radians(-W["shutter_deg"]), 4, "X")
    R3 = M.to_3x3()
    U = Vector((1, 0, 0)); V = (R3 @ Vector((0, 0, 1))).normalized()
    n = 4; gap = 0.007; pw = (bw - gap * (n - 1)) / n
    for i in range(n):
        xl = -bw / 2 + i * (pw + gap)
        ln = bl - 0.012 * (i % 2)                                   # alternate boards 12 mm shorter (hand-sawn)
        vs = k.box((xl + pw / 2, -bt / 2, -ln / 2), (pw, bt, ln), PLANKS, bevel=0.008, xform=M)
        vki_wat_plank_uv(k, vki_faces_of(vs), U, V, 0.75 + xl, pw, (3 * i + 1) % 8, 0.37 * i)
    for zc in (-0.11, -0.53):                                       # battens, 3 mm into the boards
        k.box((0.0, -bt - 0.013, zc), (bw - 0.06, 0.032, 0.075), WOOD, bevel=0.01, xform=M)
    for xs_ in (-0.20, 0.20):                                       # iron hinge straps from the top edge
        k.box((xs_, -bt - 0.002, -0.155), (0.04, 0.008, 0.29), IRON, bevel=0.002, xform=M)
    if W["shutter_deg"] <= 120.0:                                    # propped version: a stick from the sill
        tip = M @ Vector((W["prop_x"], -bt + 0.004, -0.60))           # prop tip: 4 mm into the lowest board face
        foot = Vector((0.75 + W["prop_x"], -0.10, W["sill"] - 0.004))  # prop foot: standing on the sill (rail)
        vki_wat_rod(k, foot, tip, 0.017, segs=6)


def vki_wat_window(k, height):
    """unglazed window x 0.45-1.05, z 1.00-1.60 (Full): the rail is the sill (no sag), hewn jambs x 0.33-0.45 /
    1.05-1.17 stand on it, a slightly crooked hewn lintel over x 0.25-1.25, daub over it, 2 rods, the propped
    shutter, and the daylight card at y +0.10 (WINDOW -> M_VKI_Daylight). Cut: the lower metre with a pale CAP sill
    slab over x 0.33-1.17 (|y| <= 0.18, flush with the cap) instead of the rail + a light-pool anchor."""
    L = 1.5
    full = height == "Full"
    x0, x1 = VKI_WAT_OPEN
    W = VKI_WAT_WIN
    tb = VKI_WAT_PLATE[0] if full else VKI_WAT_RAIL[0]
    # body: piers + the part under the sill (the same split in Full and Cut, so Full = Cut below 0.65)
    vki_wat_body(k, 0.0, x0, VKI_FOOT_Z, tb)
    vki_wat_body(k, x1, L, VKI_FOOT_Z, tb)
    vki_wat_body(k, x0, x1, VKI_FOOT_Z, VKI_WAT_RAIL[0])
    vki_wat_member(k, 0.0, L, 0.0, VKI_SOLE_TOP)
    vki_wat_ends(k, L, tb)
    if full:
        sag = vki_wat_sag_fn(L)
        g0, g1 = W["x"]
        lx0, lx1, lz0, lz1 = W["lintel"]
        vki_wat_member(k, VKI_WAT_STUD_HW, L - VKI_WAT_STUD_HW, *VKI_WAT_RAIL, top=VKI_CAP)   # rail = sill
        for a, b in ((x0, g0), (g1, x1)):                                  # jambs: 5 mm into the sill, up into the lintel
            vki_wat_member(k, a, b, W["sill"] - VKI_WAT_TUCK, W["jamb_top"], bev=0.015)
        vki_wat_crooked(k, lx0, lx1, lz0, lz1, W["lintel_crook"])
        vki_wat_body(k, x0, x1, lz1 - 0.06, tb)                            # daub over the lintel (from inside it)
        vki_wat_member(k, 0.0, L, *VKI_WAT_PLATE, top=VKI_CAP, cuts=vki_tim_grid(L))
        for x in W["rods"]:                                                 # 2 rods, ends buried in sill and lintel
            vki_wat_rod(k, (x, W["rod_y"], W["sill"] - VKI_WAT_TUCK), (x, W["rod_y"], W["jamb_top"]), W["rod_r"])
        cy = W["card_y"]                                                    # daylight card (closed 0.02 box)
        cz0, cz1 = W["sill"] - 0.01, W["jamb_top"] - 0.005                  # buried in the sill and the lintel
        k.box((0.75, cy, (cz0 + cz1) / 2), (g1 - g0 + 0.04, 0.02, cz1 - cz0), WINDOW, bevel=0)
        k.slot_mats[WINDOW] = "M_VKI_Daylight"
        vki_wat_shutter(k)
        vki_tim_apply_sag(k, sag, *VKI_WAT_PLATE)
        holes = [(x0, VKI_WAT_RAIL[0] - 0.02, x1, lz1), vki_wat_rail_hole(L)]
        sp = VKI_WAT_WIN_SPOT
        k.meta.update(vki_opening={"x0": g0, "x1": g1, "z0": W["sill"], "z1": W["head"], "glazed": 0},
                      vki_lights=[dict(type="SPOT", role="window", pos=list(sp["pos"]), aim=list(sp["aim"]),
                                       cone=sp["cone"], blend=sp["blend"], radius=sp["radius"], w_day=sp["w_day"],
                                       w_night=sp["w_night"], color_day=[.82, .88, 1.0], color_night=[.62, .70, 1.0],
                                       shadows=1)],
                      vki_shutter={"hinge": [0.75, W["hinge"][0], W["hinge"][1]], "open_deg": W["shutter_deg"],
                                   "hinge_axis": "local X",
                                   "zone": ([0.42, -0.75, 1.20, 1.08, -0.15, 1.66] if W["shutter_deg"] <= 120.0
                                            else [0.42, -0.32, 1.55, 1.08, -0.15, 2.27])})
    else:
        sag = (lambda x: 0.0)
        # cap segments run 0.04 into the sill slab: their bevelled front / top faces end where the slab's begin
        vki_wat_member(k, 0.0, x0 + 0.04, *VKI_WAT_RAIL, top=VKI_CAP)
        vki_wat_member(k, x1 - 0.04, L, *VKI_WAT_RAIL, top=VKI_CAP)
        vki_wat_member(k, x0, x1, 0.88, 1.00, mi=VKI_CAP, top=VKI_CAP)     # the sill slab, all CAP (paler)
        holes = []
        k.meta.update(vki_opening={"x0": W["x"][0], "x1": W["x"][1], "z0": W["sill"], "z1": W["head"], "cut": 1},
                      vki_light_pool=[0.75, -1.20, 0.0])
    vki_wat_body_finish(k, L)
    vki_wat_soot(k)
    vki_wat_wobble(k, L, "A", holes, lambda x: tb - sag(x))
    k.meta.update(vki_class="wall")


def vki_wat_window_full(k): vki_wat_window(k, "Full")
def vki_wat_window_cut(k): vki_wat_window(k, "Cut")


# ---------------------------------------------------------------- Door_150 (§3.2 Wattle)
def vki_wat_door(k, height):
    """clear opening x 0.33-1.17 x 2.00: hewn jambs x 0.19-0.33 / 1.17-1.31 (up into the lintel), a crooked lintel
    x 0.14-1.36 whose underside never drops below 2.00, DRESS threshold z 0-0.03. Cut: jambs end 5 mm inside one cap
    block from the piece end to the opening (the cap wraps the reveal), reveal faces WALL_A (§10.2)."""
    L = 1.5
    full = height == "Full"
    x0, x1 = VKI_WAT_OPEN
    D = VKI_WAT_DOOR
    tb = VKI_WAT_PLATE[0] if full else VKI_WAT_RAIL[0]
    ja = D["jamb"][0]
    vki_wat_body(k, 0.0, ja, VKI_FOOT_Z, tb)                          # piers end at the jambs' outer faces
    vki_wat_body(k, L - ja, L, VKI_FOOT_Z, tb)
    vki_wat_body(k, ja, L - ja, VKI_FOOT_Z, VKI_WAT_FOOT_TOP)          # footing under frame + threshold
    vki_wat_member(k, 0.0, ja + 0.01, 0.0, VKI_SOLE_TOP)               # sole beams run 1 cm under the jambs
    vki_wat_member(k, L - ja - 0.01, L, 0.0, VKI_SOLE_TOP)
    vki_wat_ends(k, L, tb)
    vki_wat_member(k, x0, x1, 0.0, D["thr"], mi=DRESS, bev=0.01)        # threshold (DRESS, §10.2)
    jambs = []
    if full:
        for a, b in ((ja, x0), (x1, L - ja)):
            jambs.append(vki_wat_member(k, a, b, 0.0, D["jamb_top"], bev=0.015))
    else:
        for a, b in ((ja, x0), (x1, L - ja)):
            jambs.append(vki_wat_member(k, a, b, 0.0, VKI_WAT_RAIL[0] + VKI_WAT_TUCK, bev=0.015))
        for a, b in ((0.0, x0), (x1, L)):
            jambs.append(vki_wat_member(k, a, b, *VKI_WAT_RAIL, top=VKI_CAP))
        k.bm.normal_update()
        for vs_, sgn in zip(jambs, (1, -1, 1, -1)):                    # reveal faces: limewash / daub (§10.2)
            k.project([f for f in vki_faces_of(vs_) if f.normal.x * sgn > 0.6 and f.normal.z < 0.65], VKI_WALL_A)
    if full:
        sag = vki_wat_sag_fn(L)
        vki_wat_member(k, VKI_WAT_STUD_HW, ja + 0.01, *VKI_WAT_RAIL, top=VKI_CAP)     # rail stubs 1 cm into jambs
        vki_wat_member(k, L - ja - 0.01, L - VKI_WAT_STUD_HW, *VKI_WAT_RAIL, top=VKI_CAP)
        lx0, lx1, lz0, lz1 = D["lintel"]
        vki_wat_crooked(k, lx0, lx1, lz0, lz1, D["crook"], n=8, bev=0.03)             # the crooked lintel
        vki_wat_body(k, ja, L - ja, 2.10, tb)                                         # daub over it (from inside)
        vki_wat_member(k, 0.0, L, *VKI_WAT_PLATE, top=VKI_CAP, cuts=vki_tim_grid(L))
        vki_tim_apply_sag(k, sag, *VKI_WAT_PLATE)
        holes = [(ja, 0.0, L - ja, 2.30), vki_wat_rail_hole(L)]
    else:
        sag = (lambda x: 0.0)
        holes = [(ja, 0.0, L - ja, VKI_WAT_RAIL[1])]
    vki_wat_body_finish(k, L)
    vki_wat_soot(k)
    vki_wat_wobble(k, L, "A", holes, lambda x: tb - sag(x))
    T2 = k.T / 2
    k.meta.update(vki_nav="door", vki_nav_open=[x0, x1])
    k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": D["top"] if full else 1.0},
                  vki_trigger=[0.75, -0.65, 1.0, 0.9, 0.8, 2.0], vki_leaf_socket=[x0, -T2 + 0.05, 0.0],
                  vki_leaf_open_deg=90, vki_spawn_local=[0.75, -1.60], vki_prompt_local=[0.75, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])
    if full:
        # Leaf_Plank_Full is 2.16 m tall: it does not fit under the 2.00 m wattle lintel -> a leafless doorway
        k.meta.update(vki_leaf_max_h=round(D["top"] - 0.005, 3))
    else:
        k.meta.update(vki_leaf="SM_VKI_Leaf_Plank_Cut")


def vki_wat_door_full(k): vki_wat_door(k, "Full")
def vki_wat_door_cut(k): vki_wat_door(k, "Cut")


# ---------------------------------------------------------------- Rake_150_L / _R (§2.4)
def vki_wat_rake(k, side):
    """Cut profile for u <= 0.32 from the low end, Full profile for u >= 1.18, the cap sloping at 58.4 deg between.
    _L: low end at local x = 0 (west walls); _R: low end at x = L (east walls). u = distance from the low end."""
    L = 1.5
    R = VKI_WAT_RAKE
    zb0, zb1 = VKI_WAT_RAIL[0], VKI_WAT_PLATE[0]
    zt0, zt1 = VKI_WAT_RAIL[1], VKI_WAT_PLATE[1]
    X = (lambda u: u) if side == "L" else (lambda u: L - u)

    def cb(u):                                                # cap bottom at distance u from the low end
        if u <= R["lo"]:
            return zb0
        if u >= R["hi"]:
            return zb1
        return zb0 + (zb1 - zb0) * (u - R["lo"]) / (R["hi"] - R["lo"])

    def span(u0, u1):
        return (min(X(u0), X(u1)), max(X(u0), X(u1)))

    def poly(pts):                                            # (u, z) -> (x, z), winding kept
        p = [(X(u), z) for u, z in pts]
        return p if side == "L" else p[::-1]

    tbf = lambda x: cb(x if side == "L" else L - x)
    # body: low Cut part, high Full part (it has the 0.90 row), sloped part between
    vki_wat_body(k, *span(0.0, R["lo"]), VKI_FOOT_Z, zb0)
    vki_wat_body(k, *span(R["hi"], L), VKI_FOOT_Z, zb1)
    before = set(k.bm.verts)
    vs, fs = vki_prism(k, poly([(R["lo"], VKI_FOOT_Z), (R["hi"], VKI_FOOT_Z), (R["hi"], zb1), (R["lo"], zb0)]),
                       -k.T / 2, k.T / 2, VKI_WALL_A, axis="y")
    for f in fs:
        if f.normal.y > 0.7:
            k.project([f], VKI_WALL_B)
    grid_cut(k, vs, 0.25)
    k.mark_body([v for v in k.bm.verts if v not in before])
    # members
    tk = VKI_WAT_TUCK
    vki_wat_member(k, 0.0, L, 0.0, VKI_SOLE_TOP)
    vki_wat_member(k, *span(0.0, VKI_WAT_STUD_HW), VKI_SOLE_TOP, zb0 + tk)               # low half-stud (Cut)
    vki_wat_member(k, *span(L - VKI_WAT_STUD_HW, L), VKI_SOLE_TOP, zb1 + tk)             # high half-stud (Full)
    vki_wat_member(k, *span(0.0, R["lo"]), zb0, zt0, top=VKI_CAP)                         # low flat (= Cut rail)
    vki_wat_member(k, *span(R["hi"], L), zb1, zt1, top=VKI_CAP)                           # high flat (= plate)
    sl = Vector((X(R["hi"]) - X(R["lo"]), 0.0, zb1 - zb0)).normalized()
    ry = VKI_WAT_HW - tk              # the sloped rafter sits 5 mm behind the flats' / rail's faces (§10.1)
    vs, fs = vki_prism(k, poly([(R["lo"], zb0), (R["hi"], zb1), (R["hi"], zt1), (R["lo"], zt0)]),
                       -ry, ry, WOOD, axis="y", bevel=VKI_WAT_BEV, project=False)
    top = [f for f in fs if f.normal.z > 0.3]
    vki_proj_long(k, [f for f in fs if f not in top], WOOD, sl, off=vki_hash_off((0.75, 0, 2.0)))
    vki_proj_long(k, top, VKI_CAP, sl, off=vki_hash_off((0.75, 0, 2.1)))
    # the rail on the Full side of the slope: its sloped end runs 5 mm into the rafter, its far end butts the stud
    u_s = R["lo"] + (zt0 - tk - zb0) * (R["hi"] - R["lo"]) / (zb1 - zb0)
    vs, fs = vki_prism(k, poly([(R["lo"], zb0), (L - VKI_WAT_STUD_HW, zb0), (L - VKI_WAT_STUD_HW, zt0), (u_s, zt0),
                                (R["lo"], zb0 + tk)]),
                       -VKI_WAT_HW, VKI_WAT_HW, WOOD, axis="y", bevel=VKI_WAT_BEV, project=False)
    vki_proj_long(k, [f for f in fs if f.normal.z <= 0.65], WOOD, VKI_TIM_X, off=vki_hash_off((0.5, 0, 0.95)))
    vki_proj_long(k, [f for f in fs if f.normal.z > 0.65], VKI_CAP, VKI_TIM_X, off=vki_hash_off((0.5, 0, 0.96)))
    vki_wat_body_finish(k, L)
    vki_wat_soot(k)
    ra, rb = span(R["lo"], L - VKI_WAT_STUD_HW)
    vki_wat_wobble(k, L, "A", [vki_wat_rail_hole(L, ra, rb)], tbf)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_WAT_CUT_TO, vki_rake_low="x0" if side == "L" else "xL",
                  vki_rake_slope_deg=round(math.degrees(math.atan2(zt1 - zt0, R["hi"] - R["lo"])), 2))


def vki_wat_rake_l(k): vki_wat_rake(k, "L")
def vki_wat_rake_r(k): vki_wat_rake(k, "R")


# ---------------------------------------------------------------- posts (§2.3)
def vki_wat_post(k, kind, height):
    """hewn oak post centred on its node, z -0.30 .. wall top + 0.04, bevel 0.02, ENDGRAIN top.
    Corner +-0.21 square; Mid +-0.10 along the wall (local x) x +-0.21 across. Crooked: between z 0.05 and top - 0.16
    each side face moves IN by VKI_WAT_POST_BOW (sin profile, a different peak per face; Cut posts half), vertices
    scaled toward the axis so the chamfers follow -- the post never leaves its envelope, and its top and foot stay
    the full square (T4 rays hit the top; the walls' members, +-0.18, stay inside the bowed faces, >= 0.19)."""
    k.set_family("Wattle")
    full = height == "Full"
    top = (VKI_H_FULL["Wattle"] if full else VKI_CUT_H) + VKI_POST_TOP
    ax, ay = (VKI_POST_HW["P"], VKI_POST_HW["P"]) if kind == "Corner" else VKI_MID_HW["P"]
    c = (0.0, 0.0, (VKI_POST_Z0 + top) / 2); sz = (2 * ax, 2 * ay, top - VKI_POST_Z0)
    vs = list(set(k.box(c, sz, WOOD, bevel=VKI_POST_BEVEL)))
    za, zb = 0.05, top - 0.16
    vs = vki_cut(k, vs, zs=[za + (zb - za) * i / 6 for i in range(1, 6)])
    amps = [a * (1.0 if full else 0.5) for a in VKI_WAT_POST_BOW[kind]]
    for v in vs:
        t = (v.co.z - za) / (zb - za)
        if not 0.0 < t < 1.0:
            continue
        b = [a * math.sin(math.pi * t ** p) for a, p in zip(amps, VKI_WAT_POST_BOW_P)]
        x, y = v.co.x, v.co.y
        v.co.x = x - (b[0] if x > 0 else b[1]) * x / ax
        v.co.y = y - (b[2] if y > 0 else b[3]) * y / ay
    k.bm.normal_update()
    tops = [f for f in vki_faces_of(vs) if f.normal.z > 0.65]
    vki_endgrain_fit(k, tops, (0.0, 0.0, top), VKI_TIM_X, VKI_TIM_Y, max(ax, ay), fill=VKI_TIM_POST_FILL)
    if full:                                                            # soot on the sides above 1.4, not the top
        S = VKI_WAT_SOOT
        for v in vs:
            if S["z0"] < v.co.z < top - 0.015:
                k.set_dark([v], S["post"] * vki_smoothstep(S["z0"], S["z1"], v.co.z))
    other = "Cut" if full else "Full"
    rule = {"Corner": "L/T/X junction (required, T12 error if missing); height = tallest wall-end height present "
                      "(a rake contributes its end height)",
            "Mid": "height/family/class step on a straight run or a free end (required, T12 error); rhythm at even "
                   "nodes (optional; skipped where a wall-backed / wall-hung prop or a stair spans the node)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": f"SM_VKI_Post_Wattle_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_wat_post_corner_full(k): vki_wat_post(k, "Corner", "Full")
def vki_wat_post_corner_cut(k): vki_wat_post(k, "Corner", "Cut")
def vki_wat_post_mid_full(k): vki_wat_post(k, "Mid", "Full")
def vki_wat_post_mid_cut(k): vki_wat_post(k, "Mid", "Cut")


VKI_WAT_SPECS = [
    ("SM_VKI_Wall_Wattle_Plain_150A_Full", vki_wat_plain_150a_full),
    ("SM_VKI_Wall_Wattle_Plain_150A_Cut", vki_wat_plain_150a_cut),
    ("SM_VKI_Wall_Wattle_Plain_150B_Full", vki_wat_plain_150b_full),
    ("SM_VKI_Wall_Wattle_Plain_300_Full", vki_wat_plain_300_full),
    ("SM_VKI_Wall_Wattle_Plain_300_Cut", vki_wat_plain_300_cut),
    ("SM_VKI_Wall_Wattle_Window_150_Full", vki_wat_window_full),
    ("SM_VKI_Wall_Wattle_Window_150_Cut", vki_wat_window_cut),
    ("SM_VKI_Wall_Wattle_Door_150_Full", vki_wat_door_full),
    ("SM_VKI_Wall_Wattle_Door_150_Cut", vki_wat_door_cut),
    ("SM_VKI_Wall_Wattle_Rake_150_L", vki_wat_rake_l),
    ("SM_VKI_Wall_Wattle_Rake_150_R", vki_wat_rake_r),
    ("SM_VKI_Post_Wattle_Corner_Full", vki_wat_post_corner_full),
    ("SM_VKI_Post_Wattle_Corner_Cut", vki_wat_post_corner_cut),
    ("SM_VKI_Post_Wattle_Mid_Full", vki_wat_post_mid_full),
    ("SM_VKI_Post_Wattle_Mid_Cut", vki_wat_post_mid_cut),
]
VKI_WAT_NAMES = [n for n, _ in VKI_WAT_SPECS]
vki_register([(n, fn, {"grime": "wall"}, "wattle") for n, fn in VKI_WAT_SPECS])


# ---------------------------------------------------------------- workshop test rooms and T4 rigs (package wattle)
# Only ever built into WS_vki_<agent> (collections WS_vki_<agent>_Hovel / _Chapel / _T4_*). Items: (piece, x, y, rot)
# relative to the room's SW node; walls run node to node (§2.1 rotations), posts at every junction (§2.3).
VKI_WAT_WS = dict(hovel=(12.0, 0.0), chapel=(36.0, 0.0), t4=(0.0, -40.0))
VKI_WAT_WS_ROW = (0.0, 20.0, 3.6)   # masters row (x0, y, spacing): north of the rooms, outside both room cameras


def vki_wat_ws_layout(agent="wattle"):
    """lay the package's masters out in one row in WS_vki_<agent>_Pieces (visible, unrotated) -- the coordinator's
    board instances that collection; vki_adopt later moves them back to the origin, hidden"""
    x0, y0, sp = VKI_WAT_WS_ROW
    names = VKI_WAT_NAMES + list(globals().get("VKI_ASH_NAMES", []))
    done = 0
    for i, n in enumerate(names):
        o = bpy.data.objects.get(n)
        if o is None or f"WS_vki_{agent}_Pieces" not in [c.name for c in o.users_collection]:
            continue
        o.location = (x0 + i * sp, y0, 0.0); o.rotation_euler = (0.0, 0.0, 0.0)
        o.hide_viewport = o.hide_render = False
        done += 1
    return done
VKI_WAT_WS_HOVEL = [       # 3 x 3 cells: window + rhythm post north, door + rake R east, Cut south wall with the exit
    ("SM_VKI_Wall_Wattle_Plain_300_Full", 0.0, 4.5, 0), ("SM_VKI_Wall_Wattle_Window_150_Full", 3.0, 4.5, 0),
    ("SM_VKI_Wall_Wattle_Plain_150A_Full", 4.5, 4.5, -90), ("SM_VKI_Wall_Wattle_Door_150_Full", 4.5, 3.0, -90),
    ("SM_VKI_Wall_Wattle_Rake_150_R", 4.5, 1.5, -90),
    ("SM_VKI_Wall_Wattle_Plain_150A_Cut", 4.5, 0.0, 180), ("SM_VKI_Wall_Wattle_Door_150_Cut", 3.0, 0.0, 180),
    ("SM_VKI_Wall_Wattle_Window_150_Cut", 1.5, 0.0, 180),
    ("SM_VKI_Wall_Wattle_Rake_150_L", 0.0, 0.0, 90), ("SM_VKI_Wall_Wattle_Plain_150B_Full", 0.0, 1.5, 90),
    ("SM_VKI_Wall_Wattle_Plain_150A_Full", 0.0, 3.0, 90),
    ("SM_VKI_Wall_Wattle_Plain_300_Cut", 0.0, 3.0, 0),                      # Cut partition: T at the west wall
    ("SM_VKI_Post_Wattle_Corner_Full", 0.0, 4.5, 0), ("SM_VKI_Post_Wattle_Corner_Full", 4.5, 4.5, 0),
    ("SM_VKI_Post_Wattle_Corner_Cut", 4.5, 0.0, 0), ("SM_VKI_Post_Wattle_Corner_Cut", 0.0, 0.0, 0),
    ("SM_VKI_Post_Wattle_Corner_Full", 0.0, 3.0, 0), ("SM_VKI_Post_Wattle_Mid_Cut", 3.0, 3.0, 0),
    ("SM_VKI_Post_Wattle_Mid_Full", 3.0, 4.5, 0), ("SM_VKI_Post_Wattle_Mid_Full", 4.5, 3.0, 90),
    ("SM_VKI_Post_Wattle_Mid_Cut", 3.0, 0.0, 0),
    ("SM_VKI_Leaf_Plank_Cut", 2.67, 0.10, 180), ("SM_VKI_Apron_300x150", 3.0, 0.0, 180),
    ("SM_VKI_RushMat", 2.25, 0.75, 0)]
VKI_WAT_WS_CHAPEL = [      # 6 x 3 cells: triple-lancet north wall, wide doors east (Full) and south (Cut exit)
    ("SM_VKI_Wall_Ashlar_Plain_150A_Full", 0.0, 4.5, 0), ("SM_VKI_Wall_Ashlar_Lancet_150_Full", 1.5, 4.5, 0),
    ("SM_VKI_Wall_Ashlar_LancetTall_150_Full", 3.0, 4.5, 0), ("SM_VKI_Wall_Ashlar_LancetTall_150_Full", 4.5, 4.5, 0),
    ("SM_VKI_Wall_Ashlar_Lancet_150_Full", 6.0, 4.5, 0), ("SM_VKI_Wall_Ashlar_Plain_150A_Full", 7.5, 4.5, 0),
    ("SM_VKI_Wall_Ashlar_DoorWide_300_Full", 9.0, 4.5, -90), ("SM_VKI_Wall_Ashlar_Plain_150A_Full", 9.0, 1.5, -90),
    ("SM_VKI_Wall_Ashlar_Plain_150A_Cut", 9.0, 0.0, 180), ("SM_VKI_Wall_Ashlar_Lancet_150_Cut", 7.5, 0.0, 180),
    ("SM_VKI_Wall_Ashlar_DoorWide_300_Cut", 6.0, 0.0, 180), ("SM_VKI_Wall_Ashlar_Plain_300_Cut", 3.0, 0.0, 180),
    ("SM_VKI_Wall_Ashlar_Plain_150A_Full", 0.0, 0.0, 90), ("SM_VKI_Wall_Ashlar_Plain_300_Full", 0.0, 1.5, 90),
    ("SM_VKI_Post_Ashlar_Corner_Full", 0.0, 4.5, 0), ("SM_VKI_Post_Ashlar_Corner_Full", 9.0, 4.5, 0),
    ("SM_VKI_Post_Ashlar_Corner_Full", 9.0, 0.0, 0), ("SM_VKI_Post_Ashlar_Corner_Full", 0.0, 0.0, 0),   # pillars
    ("SM_VKI_Post_Ashlar_Mid_Full", 0.0, 1.5, 90), ("SM_VKI_Post_Ashlar_Mid_Full", 9.0, 1.5, 90),
    ("SM_VKI_Apron_300x150", 6.0, 0.0, 180), ("SM_VKI_RushMat", 4.5, 0.75, 0)]
VKI_WAT_WS_ROOMS = {"hovel": (VKI_WAT_WS_HOVEL, 3, 3, "Earth", "Wattle"),
                    "chapel": (VKI_WAT_WS_CHAPEL, 6, 3, "FlagWarm", "Ashlar")}


def vki_wat_ws_coll(sc, name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    if c.name not in sc.collection.children:
        sc.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o)
    return c


def vki_wat_ws_rooms(agent="wattle", which=("hovel", "chapel"), style=None):
    """(re)build the package's test rooms in WS_vki_<agent>; style (e.g. VKI_NIGHT_STYLE) goes on the VKI walls.
    Returns {room: dict(objs, bounds, fam, posts)}; bounds are the wall lines (vki_fit_camera)."""
    sc, _, _ = vki_ws(agent)
    out = {}
    for key in which:
        items, nx, ny, floor, fam = VKI_WAT_WS_ROOMS[key]
        c = vki_wat_ws_coll(sc, f"WS_vki_{agent}_{key.capitalize()}")
        ox, oy = VKI_WAT_WS[key]
        objs = []
        for p, x, y, r in items:
            if bpy.data.objects.get(p) is None:
                continue
            st = style if (style and p.startswith("SM_VKI_Wall_")) else None
            objs.append(vki_place(c, p, ox + x, oy + y, r, style=st, walls=[]))
        for it in vki_c3_floor_pieces(ox, oy, nx, ny, {"floor": floor}):
            objs.append(vki_place(c, it[0], it[1], it[2], 0, style=it[4], walls=[]))
        vki_lt_lights(sc, c, c)          # window / lancet spots and the apron light from the masters' vki_lights
        out[key] = dict(objs=objs, bounds=(ox, oy, ox + 1.5 * nx, oy + 1.5 * ny), fam=fam,
                        posts=[(ox + x, oy + y) for p, x, y, r in items if "_Post_" in p])
    return out


def vki_wat_ws_t4(agent="wattle"):
    """T4 rigs L / T / X / End / FullCut per family (as vki_t4_rigs, but in WS_vki_<agent>); returns the rigs dict
    for vki_t4_coverage(rigs, scene="WS_vki_<agent>")"""
    sc, _, _ = vki_ws(agent)
    rigs = {}
    ox, oy = VKI_WAT_WS["t4"]
    for fi, fam in enumerate(("Wattle", "Ashlar")):
        corner, mid = f"SM_VKI_Post_{fam}_Corner_Full", f"SM_VKI_Post_{fam}_Mid_Full"
        full, cut = f"SM_VKI_Wall_{fam}_Plain_150A_Full", f"SM_VKI_Wall_{fam}_Plain_150A_Cut"
        plan = [("L", [(full, 0, 0, 0), (full, 0, 0, 90), (corner, 0, 0, 0)]),
                ("T", [(full, 0, 0, 0), (full, 0, 0, 180), (full, 0, 0, 90), (corner, 0, 0, 0)]),
                ("X", [(full, 0, 0, 0), (full, 0, 0, 180), (full, 0, 0, 90), (full, 0, 0, -90), (corner, 0, 0, 0)]),
                ("End", [(full, 0, 0, 0), (mid, 0, 0, 0)]),
                ("FullCut", [(full, -1.5, 0, 0), (cut, 0, 0, 0), (mid, 0, 0, 0)])]
        for i, (tag, items) in enumerate(plan):
            nx_, ny_ = ox + i * 6.0, oy - fi * 8.0
            c = vki_wat_ws_coll(sc, f"WS_vki_{agent}_T4_{fam}_{tag}")
            objs = [vki_place(c, p, nx_ + x, ny_ + y, r, walls=[]) for p, x, y, r in items]
            rigs[f"{fam}_{tag}"] = dict(objs=objs, node=(nx_, ny_))
    return rigs
