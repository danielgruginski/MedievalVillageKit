# ===================== VKI PROPS POI: points of interest -- one landmark per theme (docs/POINTS_OF_INTEREST.md) =====================
# Package "adventure". Loaded by vki_ns() after the rooms texts (it adds its catalog group); the builders call the prop
# helpers (vki_home_*, vki_dpr_*, vki_dun_*, vki_adv_*, vki_chp_candle, vki_wat_sheet) at build time.
# A point of interest is a hero-tier prop (T9: 6,000 tris) meant to be placed ONCE in a level: the landmark a level is
# built round and the player remembers. Each carries its own lights and FX sockets, colliders, use points and a
# vki_poi record (name, kind, theme, interaction) for the game. Origin on the footprint centre, back toward +Y,
# geometry at its real height; place it with hug off.
#   POI_WyrmBones     caves: the bones of a great wyrm on the cave floor, horned skull, ribs, a fanned wing
#   POI_ColossusHead  ruins: a colossal king's head toppled from its statue, face up, nose broken, and its hand
#   POI_Crucible      dwarf halls: the great crucible -- a round furnace, a jib crane pouring a crucible of molten metal
#                     into a casting bed of ingot moulds
#   POI_NecroCircle   dungeon: a necromancer's circle round an opened sarcophagus -- a glowing sigil, standing stones,
#                     binding chains
#   POI_RatKing       sewers: the rat king's throne of junk on a refuse heap, a crown of bones, a hoard
#   POI_SpringShrine  water: a sacred spring -- a carved basin fed from a stele's spout, crystals crowning it
# Building note: creating an icosphere (vki_home_ico / _ico) can invalidate BMVert references held from before it (a
# set of "the verts so far" then misses every old vert). So no vert references are held across an ico here: parts
# with icos are built first or transformed the moment they exist, and colliders are measured right away.
# Every top-level name starts with vki_/VKI_ (T18).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix


# ---------------------------------------------------------------- helpers
def vki_poi_tube(k, pts, radii, mi, segs=6, smooth=True):
    """a continuous tube along pts (3-D), one radius per point, its rings parallel-transported (no twist); an end of
    radius 0 closes to a point, any other end gets an n-gon cap. Horns, claws, ribs, the pour of molten metal.
    -> (verts, faces)"""
    P = [Vector(p) for p in pts]
    n = len(P)
    T = [(P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized() for i in range(n)]
    ref = Vector((0.0, 0.0, 1.0)) if abs(T[0].z) < 0.9 else Vector((1.0, 0.0, 0.0))
    N = [T[0].cross(ref).normalized()]
    for i in range(1, n):
        N.append((T[i - 1].rotation_difference(T[i]) @ N[-1]).normalized())
    bm = k.bm
    rings = []
    for i in range(n):
        if radii[i] <= 1e-6:
            rings.append([bm.verts.new(P[i])])
            continue
        B = T[i].cross(N[i]).normalized()
        rings.append([bm.verts.new(P[i] + radii[i] * (math.cos(2 * math.pi * j / segs) * N[i] +
                                                     math.sin(2 * math.pi * j / segs) * B)) for j in range(segs)])
    fs = []
    for A, C in zip(rings[:-1], rings[1:]):
        if len(A) == 1:
            fs += [bm.faces.new((A[0], C[(j + 1) % segs], C[j])) for j in range(segs)]
        elif len(C) == 1:
            fs += [bm.faces.new((A[j], A[(j + 1) % segs], C[0])) for j in range(segs)]
        else:
            fs += [bm.faces.new((A[j], A[(j + 1) % segs], C[(j + 1) % segs], C[j])) for j in range(segs)]
    if len(rings[0]) > 1:
        fs.append(bm.faces.new(rings[0][::-1]))
    if len(rings[-1]) > 1:
        fs.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.material_index = mi
        f.smooth = smooth
    k.project(fs, mi)
    return [v for r in rings for v in r], fs


def vki_poi_spline(K, n):
    """n points on the Catmull-Rom spline through the key points K (3-D), evenly in parameter"""
    K = [Vector(p) for p in K]
    m = len(K) - 1
    out = []
    for s in range(n):
        t = s / (n - 1) * m
        i = min(int(t), m - 1)
        u = t - i
        p0, p1, p2, p3 = K[max(i - 1, 0)], K[i], K[i + 1], K[min(i + 2, m)]
        out.append(0.5 * (2 * p1 + (p2 - p0) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u +
                          (3 * p1 - p0 - 3 * p2 + p3) * u ** 3))
    return out


def vki_poi_new(k, before):
    """the verts added since `before` (a set of verts)"""
    return [v for v in k.bm.verts if v not in before]


def vki_poi_aabb(vs, pad=0.0, zmin=0.0):
    """a vki_collider box [cx, cy, cz, sx, sy, sz] round the verts (from zmin up)"""
    x0 = min(v.co.x for v in vs) - pad; x1 = max(v.co.x for v in vs) + pad
    y0 = min(v.co.y for v in vs) - pad; y1 = max(v.co.y for v in vs) + pad
    z1 = max(v.co.z for v in vs)
    return [round((x0 + x1) / 2, 3), round((y0 + y1) / 2, 3), round((zmin + z1) / 2, 3), round(x1 - x0, 3),
            round(y1 - y0, 3), round(z1 - zmin, 3)]


def vki_poi_meta(k, name, kind, theme, interact, use, colliders, **kw):
    """a point of interest's metadata: hero tier, the vki_poi record the game reads (placed once per level), and
    vki_cam_fade (the game fades its tall parts -- a crane, a stele -- when they hide the player; R-occ3)"""
    vki_home_meta(k, "floor", "hero", use=use, vki_nav="block", vki_collider=colliders, vki_cam_fade=1,
                  vki_poi={"name": name, "kind": kind, "theme": theme, "interact": interact, "once": True}, **kw)


# ---------------------------------------------------------------- POI_WyrmBones (caves)
VKI_POI_WYRM_SPINE = [(0.45, -1.75, 0.40), (0.28, -1.38, 0.52), (0.10, -0.98, 0.64), (0.0, -0.53, 0.72),
                      (-0.05, -0.07, 0.72), (-0.07, 0.37, 0.60), (-0.14, 0.78, 0.40), (-0.31, 1.19, 0.24),
                      (-0.48, 1.60, 0.14), (-0.53, 2.00, 0.10), (-0.37, 2.36, 0.08), (-0.08, 2.60, 0.06)]


def vki_poi_wyrm_skull(k):
    """the wyrm's skull at the origin (snout toward local -y, the jaw hinge at y 0.05, z 0.05) -- build it FIRST in a
    master (it returns every vert): the upper skull (cranium, brow ridges, dark eye sockets and nostrils, a tapering
    snout with fangs, cheek bars, two swept horns and two small ones) lifted 20 deg on the hinge, the mouth gaping;
    the lower jaw lying on the floor, teeth up. -> verts"""
    cv = vki_home_ico(k, (0.0, 0.12, 0.30), 0.30, VKI_WAX, scale=(1.0, 1.15, 0.85), sub=2)
    k.project(vki_faces_of(cv), VKI_WAX)
    sv = list(set(k.box((0.0, -0.52, 0.25), (0.44, 0.84, 0.22), VKI_WAX, bevel=0.0)))       # the snout, tapered
    for v in sv:
        t = (-0.10 - v.co.y) / 0.84
        v.co.x *= 1.0 - 0.48 * t
        v.co.z = 0.14 + (v.co.z - 0.14) * (1.0 - 0.40 * t)
    k.bm.normal_update()
    k.project(vki_faces_of(sv), VKI_WAX)
    for s_ in (-1.0, 1.0):
        k.box((s_ * 0.17, -0.03, 0.50), (0.15, 0.30, 0.07), VKI_WAX, rot=(0.0, 0.0, s_ * 0.2), bevel=0.02)   # brow
        k.box((s_ * 0.20, -0.09, 0.40), (0.13, 0.15, 0.11), VOID, bevel=0.0)                            # eye socket
        k.box((s_ * 0.055, -0.92, 0.215), (0.04, 0.05, 0.035), VOID, bevel=0.0)                         # nostril
        vki_poi_tube(k, [(s_ * 0.26, -0.12, 0.27), (s_ * 0.30, 0.02, 0.19), (s_ * 0.26, 0.10, 0.10)],
                     [0.04, 0.042, 0.04], VKI_WAX, segs=5)                                              # cheek bar
        for j in range(6):                                                                             # fangs
            y = -0.18 - 0.13 * j
            t = (-0.10 - y) / 0.84
            x, h = s_ * (0.205 - 0.10 * t), 0.06 + (0.07 if j >= 4 else 0.0) + 0.006 * j
            vki_prism(k, [(y - 0.022, 0.16), (y + 0.022, 0.16), (y, 0.16 - h)], x - 0.014, x + 0.014, VKI_WAX, axis="x")
        vki_poi_tube(k, [(s_ * 0.19, 0.32, 0.47), (s_ * 0.27, 0.62, 0.62), (s_ * 0.33, 0.95, 0.70),
                         (s_ * 0.36, 1.22, 0.72), (s_ * 0.35, 1.42, 0.66)], [0.075, 0.062, 0.047, 0.028, 0.0], VKI_WAX,
                     segs=6)                                                                           # horns
        vki_poi_tube(k, [(s_ * 0.27, 0.12, 0.27), (s_ * 0.44, 0.30, 0.22), (s_ * 0.55, 0.50, 0.21)], [0.045, 0.030, 0.0],
                     VKI_WAX, segs=5)
    bmesh.ops.transform(k.bm, verts=list(k.bm.verts), matrix=Matrix.Translation((0.0, 0.05, 0.05)) @
                        Matrix.Rotation(math.radians(-20.0), 4, "X") @ Matrix.Translation((0.0, -0.05, -0.05)))
    for s_ in (-1.0, 1.0):                                              # the mandibles, lying on the floor
        vki_poi_tube(k, [(s_ * 0.25, 0.08, 0.06), (s_ * 0.20, -0.30, 0.05), (s_ * 0.12, -0.70, 0.045),
                         (s_ * 0.04, -0.92, 0.042)], [0.055, 0.048, 0.040, 0.034], VKI_WAX, segs=5)
        for j in range(5):
            y, x, h = -0.24 - 0.14 * j, s_ * (0.205 - 0.034 * j), 0.05 + 0.012 * j
            vki_prism(k, [(y - 0.02, 0.07), (y + 0.02, 0.07), (y, 0.07 + h)], x - 0.013, x + 0.013, VKI_WAX, axis="x")
    return list(k.bm.verts)


def vki_poi_wyrm(k):
    """the bones of a great wyrm on the cave floor (4.7 x 5.8 m), lying away from the viewer: its horned skull at the
    front with the jaw fallen open, a neck and spine of 29 vertebrae with dorsal spines (tallest over the shoulders)
    running back to a tail that curls away, ribs arching out to both sides (a few broken, one fallen), both wings'
    finger bones fanned on the floor, the pelvis and both hind legs folded, claws out; glowing crystals grown up
    through the ribcage and by the jaw (a cold light); gold coins, a sword and a shield among the bones"""
    rnd = random.Random(11)
    # the skull first (it holds the master's only ico), its occiput at the neck
    sk = vki_poi_wyrm_skull(k)
    bmesh.ops.transform(k.bm, verts=sk, matrix=Matrix.Translation((0.52, -2.15, 0.0)) @
                        Matrix.Rotation(math.radians(-8.0), 4, "Z"))
    skull_box = vki_poi_aabb(sk, pad=0.02)
    # the spine
    S = vki_poi_spline(VKI_POI_WYRM_SPINE, 30)
    ribs, n = [], len(S) - 1
    sh = None
    for i in range(n):
        a, b = S[i], S[i + 1]
        t = i / (n - 1)
        d = b - a
        L = d.length
        dn = d.normalized()
        yaw = math.atan2(d.y, d.x)
        r = 0.075 + 0.030 * vki_smoothstep(0.08, 0.22, t) - 0.085 * vki_smoothstep(0.40, 1.0, t)
        mid = (a + b) / 2
        _cyl(k, tuple(mid), r, r * 0.92, 0.70 * L, 6, VKI_WAX, rot=dn.to_track_quat("Z", "Y").to_matrix().to_4x4())
        h = 0.08 + 0.26 * math.exp(-((t - 0.28) / 0.16) ** 2) - 0.04 * t
        vs, _ = vki_prism(k, [(-0.30 * L, 0.0), (0.30 * L, 0.0), (0.30 * L + 0.28 * h, h)], -0.016, 0.016, VKI_WAX,
                          axis="y")
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation(mid + Vector((0.0, 0.0, r * 0.75))) @
                            Matrix.Rotation(yaw, 4, "Z"))
        side = Vector((d.y, -d.x, 0.0)).normalized()                  # across the body
        if 0.19 <= t <= 0.46:                                          # ribs, both sides
            f = 0.72 + 0.28 * math.sin(math.pi * (t - 0.19) / 0.27)
            for s_ in (1.0, -1.0):
                base = mid + side * (s_ * r * 0.8)
                W, H = 0.80 * f, mid.z - 0.05
                np_ = 5 if rnd.random() > 0.2 else 3                  # a broken rib now and then
                pts = []
                for j in range(np_):
                    ph = math.radians(90.0 * j / 4)
                    pts.append(base + side * (s_ * W * math.sin(ph)) + dn * (0.18 * j / 4) +
                               Vector((0.0, 0.0, -H * (1.0 - math.cos(ph)))))
                vs, _ = vki_poi_tube(k, pts, [0.036, 0.034, 0.030, 0.025, 0.018][:np_], VKI_WAX, segs=5)
                ribs += vs
        if abs(t - 0.24) < 0.02 and sh is None:
            sh = (Vector(mid), side, dn)
    rib_box = vki_poi_aabb(ribs, pad=0.02)
    vki_poi_tube(k, [(0.95, -0.95, 0.03), (1.18, -0.66, 0.03), (1.20, -0.28, 0.03)], [0.030, 0.028, 0.02], VKI_WAX,
                 segs=5)                                                # a rib fallen on the floor
    # both wings: the arm bones low off the shoulders, the finger bones fanned back on the floor
    m, side, dn = sh
    for s_ in (1.0, -1.0):
        sd = side * s_
        shw = m + sd * 0.12 + Vector((0.0, 0.0, -0.08))
        elw = Vector((m.x, m.y, 0.26)) + sd * 0.75 + dn * 0.25
        wrw = Vector((m.x, m.y, 0.10)) + sd * 1.05 - dn * 0.05
        vki_poi_tube(k, [shw, elw], [0.060, 0.048], VKI_WAX, segs=6)
        vki_poi_tube(k, [elw, wrw], [0.048, 0.038], VKI_WAX, segs=6)
        sg = 1.0 if sd.x * dn.y - sd.y * dn.x > 0 else -1.0          # the turn that takes the wing toward the tail
        for ang, ln in ((10.0, 0.95), (35.0, 1.25), (60.0, 1.15), (85.0, 0.85)):
            fd = Matrix.Rotation(math.radians(sg * ang), 3, "Z") @ sd
            mp = wrw + fd * (ln * 0.5)
            vki_poi_tube(k, [wrw, Vector((mp.x, mp.y, 0.08)), wrw + fd * ln + Vector((0.0, 0.0, -0.06))],
                         [0.030, 0.022, 0.012], VKI_WAX, segs=5)
    # the pelvis and both hind legs, folded, claws forward
    hp = S[15]
    dh = (S[16] - S[14]).normalized()
    sideh = Vector((dh.y, -dh.x, 0.0)).normalized()
    k.box(tuple(hp + Vector((0.0, 0.0, -0.06))), (0.40, 0.66, 0.14), VKI_WAX, rot=(0.0, 0.0, math.atan2(dh.y, dh.x)),
          bevel=0.03)
    for s_ in (1.0, -1.0):
        sd = sideh * s_
        hip = hp + sd * 0.18 + Vector((0.0, 0.0, -0.08))
        kn = Vector((hip.x, hip.y, 0.30)) + sd * 0.45 - dh * 0.35
        an = Vector((kn.x, kn.y, 0.06)) + sd * 0.20 + dh * 0.30
        vki_poi_tube(k, [hip, kn], [0.070, 0.055], VKI_WAX, segs=6)
        vki_poi_tube(k, [kn, an], [0.055, 0.040], VKI_WAX, segs=6)
        for ang in (-25.0, 0.0, 25.0):
            cd = Matrix.Rotation(math.radians(ang), 3, "Z") @ (-dh)
            vki_poi_tube(k, [an, an + cd * 0.15 + Vector((0, 0, 0.02)), an + cd * 0.27 + Vector((0, 0, -0.03))],
                         [0.028, 0.020, 0.0], VKI_WAX, segs=5)
    # glowing crystals grown up through the ribcage and beside the jaw
    for (cx, cy, sc_) in ((0.12, -0.28, 1.0), (-0.55, -2.55, 0.65)):
        for j, (x, y, h, r_) in enumerate(((0.0, 0.0, 0.78, 0.085), (0.15, 0.06, 0.52, 0.065), (-0.13, 0.09, 0.58, 0.065),
                                            (0.06, -0.14, 0.44, 0.055), (-0.10, -0.12, 0.34, 0.05))):
            dv = Vector((x * 2.2, y * 2.2, 1.0)).normalized()
            base = Vector((cx + x * sc_, cy + y * sc_, -0.02))
            _cyl(k, tuple(base + dv * (h * sc_ / 2)), r_ * sc_, 0.008, h * sc_, 6, MUSH_GLOW,
                 rot=dv.to_track_quat("Z", "Y").to_matrix().to_4x4())
    # the hoard among the bones: coins, a sword stuck in the floor, a shield
    for i in range(14):
        vki_adv_coin(k, (rnd.uniform(0.55, 1.35), rnd.uniform(-1.45, -0.35), 0.004 + 0.002 * (i % 3)),
                     rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2))
    before = set(k.bm.verts)
    k.box((0.0, 0.0, 0.40), (0.055, 0.012, 0.80), IRON, bevel=0.0)                          # blade
    k.box((0.0, 0.0, 0.81), (0.26, 0.03, 0.035), IRON, bevel=0.0)                           # crossguard
    k.box((0.0, 0.0, 0.93), (0.035, 0.035, 0.20), WOOD, bevel=0.0)                          # grip
    _cyl(k, (0.0, 0.0, 1.05), 0.032, 0.032, 0.05, 8, IRON)                                  # pommel
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((-0.85, -1.05, -0.08)) @
                        Matrix.Rotation(math.radians(20.0), 4, "Y") @ Matrix.Rotation(math.radians(35.0), 4, "Z"))
    before = set(k.bm.verts)
    vki_home_lathe(k, [(0.0, 0.0), (0.30, 0.0), (0.30, 0.03), (0.0, 0.05)], c=(0.0, 0.0, 0.0), segs=12, mi=WOOD)
    vki_home_lathe(k, [(0.0, 0.03), (0.08, 0.03), (0.0, 0.09)], c=(0.0, 0.0, 0.0), segs=8, mi=IRON)
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((1.35, -1.75, 0.02)) @
                        Matrix.Rotation(math.radians(8.0), 4, "X"))
    for v in k.bm.verts:                                                # the bones darken toward the floor
        k.set_dark([v], 0.05 + 0.25 * vki_smoothstep(0.30, 0.0, v.co.z))
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_dpr_gold_mats(k)
    vki_poi_meta(k, "Wyrm bones", "landmark", "cave", "examine", use=[[0.40, -3.65, 0.0]],
                 colliders=[skull_box, rib_box],
                 vki_lights=[dict(type="POINT", role="crystal", pos=[0.12, -0.60, 1.00], w=120.0,
                                  color=VKI_CAV_CRYSTAL_COL, range=6.0, flicker=0, shadows=0, radius=0.15)],
                 vki_place_rule="a cave floor with 4 x 4 open cells (6 x 6 m), the skull toward the camera (rotation "
                                "0); the tail, wing and leg bones are low enough to walk over (no collider)")


# ---------------------------------------------------------------- POI_ColossusHead (ruins)
def vki_poi_colossus_head(k):
    """a colossal crowned king's head at the origin (face toward local -y, up +z; 1.8 wide, 2.3 tall without the
    beard): brow, lidded eyes with carved pupils, a nose (its tip broken off), lips under a moustache, a squared beard
    of five curled rows ending in ringlets, ears, a tall crown with a band of gilded rosettes and a crenellated rim,
    two merlons broken off. -> verts"""
    before = set(k.bm.verts)
    hv = vki_home_ico(k, (0.0, 0.0, 0.0), 1.0, VKI_CAP, scale=(0.88, 0.95, 1.12), sub=3)
    k.project(vki_faces_of(hv), VKI_CAP)
    k.box((0.0, -0.77, 0.34), (1.20, 0.44, 0.18), VKI_CAP, bevel=0.05)                          # brow
    for s in (-1.0, 1.0):
        ev = vki_home_ico(k, (s * 0.33, -0.84, 0.13), 0.16, VKI_CAP, scale=(1.25, 0.45, 0.62), sub=2)
        k.project(vki_faces_of(ev), VKI_CAP)
        _cyl(k, (s * 0.33, -0.912, 0.13), 0.055, 0.055, 0.02, 8, VOID, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
        k.box((s * 0.33, -0.86, 0.225), (0.40, 0.14, 0.05), VKI_CAP, rot=(0.0, s * 0.10, 0.0), bevel=0.02)   # lid
        ov = vki_home_ico(k, (s * 0.86, -0.05, 0.02), 0.24, VKI_CAP, scale=(0.35, 0.80, 1.20), sub=1)       # ear
        k.project(vki_faces_of(ov), VKI_CAP)
        k.box((s * 0.20, -0.90, -0.40), (0.36, 0.24, 0.09), VKI_CAP, rot=(0.0, s * 0.30, 0.0), bevel=0.03)   # moustache
    vki_prism(k, [(-0.97, 0.22), (-1.15, -0.08), (-1.12, -0.22), (-0.95, -0.34)], -0.13, 0.13, VKI_CAP, axis="x",
              bevel=0.02)                                                                          # the nose, broken
    k.box((0.0, -0.87, -0.52), (0.46, 0.24, 0.08), VKI_CAP, bevel=0.03)                           # lips
    k.box((0.0, -0.83, -0.63), (0.38, 0.22, 0.07), VKI_CAP, bevel=0.03)
    for j in range(5):                                                                           # the beard's rows
        z0, z1 = -0.62 - 0.20 * j, -0.62 - 0.20 * (j + 1)
        w = 0.62 - 0.03 * j
        yf = -1.00 - (0.035 if j % 2 else 0.0) + 0.04 * j
        k.box((0.0, (yf - 0.20) / 2, (z0 + z1) / 2), (2 * w, -0.20 - yf, z0 - z1), VKI_CAP, bevel=0.04)
    for j in range(5):                                                                           # ringlets below
        x = -0.40 + 0.20 * j
        _cyl(k, (x, -0.66, -1.72), 0.07, 0.05, 0.24, 8, VKI_CAP)
    vki_home_lathe(k, [(0.74, 0.60), (0.79, 0.70), (0.76, 1.22), (0.70, 1.28), (0.0, 1.28)], c=(0.0, 0.03, 0.0),
                   segs=16, mi=VKI_CAP, sy=0.95)                                                    # the crown
    vki_home_hoop(k, (0.0, 0.03, 0.86), 0.77, 0.815, 0.10, segs=16, mi=VKI_CAP, sy=0.95)
    for i in range(8):                                                                           # gilded rosettes
        a = -math.pi / 2 + (i - 3.5) * 0.30
        if abs(i - 3.5) > 2.6:
            continue
        c = Vector((0.815 * math.cos(a), 0.03 + 0.815 * 0.95 * math.sin(a), 0.86))
        _cyl(k, tuple(c), 0.055, 0.055, 0.02, 8, VKI_DPR_GOLD,
             rot=Vector((0, 0, 1)).rotation_difference(Vector((math.cos(a), math.sin(a), 0.0))).to_matrix().to_4x4())
    for i in range(12):                                                                          # merlons (2 broken off)
        if i in (7, 8):
            continue
        a = 2 * math.pi * i / 12 + math.pi / 12
        c = (0.70 * math.cos(a), 0.03 + 0.70 * 0.95 * math.sin(a), 1.36)
        k.box(c, (0.20, 0.10, 0.18), VKI_CAP, rot=(0.0, 0.0, a + math.pi / 2), bevel=0.02)
    return vki_poi_new(k, before)


def vki_poi_colossus(k):
    """a colossal king's head fallen from its statue (about 5 x 3.6 m): face up and turned toward the viewer, sunk into
    the floor, its crown split; beside it the colossus's broken hand, palm down, the crown's lost merlons, the nose's
    tip and rubble. Ancient stone (pale AncientCap, dressed AncientBlock), traces of gilding"""
    rnd = random.Random(21)
    hv = vki_poi_colossus_head(k)
    bmesh.ops.transform(k.bm, verts=hv, matrix=Matrix.Translation((-0.35, 0.30, 0.80)) @
                        Matrix.Rotation(math.radians(-10.0), 4, "Z") @ Matrix.Rotation(math.radians(16.0), 4, "Y") @
                        Matrix.Rotation(math.radians(-62.0), 4, "X"))
    head_box = vki_poi_aabb(hv, pad=0.02, zmin=0.0)
    # the hand: palm down, fingers slightly curled, broken at the wrist
    before = set(k.bm.verts)
    k.box((0.0, 0.0, 0.17), (0.70, 0.62, 0.30), VKI_CAP, bevel=0.06)                              # palm
    for j, (x, ln) in enumerate(((-0.25, 0.46), (-0.08, 0.54), (0.09, 0.52), (0.25, 0.42))):
        vki_poi_tube(k, [(x, -0.28, 0.20), (x, -0.28 - ln * 0.55, 0.19), (x, -0.28 - ln, 0.10)], [0.085, 0.080, 0.072],
                     VKI_CAP, segs=7)
    vki_poi_tube(k, [(0.34, 0.05, 0.18), (0.52, -0.18, 0.15), (0.60, -0.40, 0.09)], [0.10, 0.09, 0.08], VKI_CAP, segs=7)
    vki_poi_tube(k, [(0.0, 0.28, 0.17), (0.0, 0.52, 0.19)], [0.24, 0.23], VKI_STONE_BLOCK_IN, segs=10)   # the wrist
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((1.75, -0.55, 0.0)) @
                        Matrix.Rotation(math.radians(28.0), 4, "Z"))
    # the crown's merlons, the nose's tip, rubble
    for (x, y, a, i) in ((-1.55, 1.05, 0.4, 0), (-1.85, 0.55, 1.3, 1)):
        k.box((x, y, 0.09), (0.20, 0.10, 0.18), VKI_CAP, rot=(0.0, math.radians(80.0), a), bevel=0.02)
    before = set(k.bm.verts)
    vki_prism(k, [(0.02, 0.12), (-0.07, -0.10), (0.05, -0.02)], -0.10, 0.10, VKI_CAP, axis="x", bevel=0.01)   # tip
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((0.95, -1.45, 0.09)) @
                        Matrix.Rotation(math.radians(90.0), 4, "X"))
    for i in range(7):
        x, y = rnd.uniform(-2.2, 2.2), rnd.uniform(-1.6, 1.4)
        if abs(x + 0.35) < 1.2 and -1.2 < y < 1.4 or abs(x - 1.75) < 0.6 and abs(y + 0.55) < 0.6:
            x = -2.1 + 4.2 * i / 6
            y = -1.55
        sz = (rnd.uniform(0.18, 0.40), rnd.uniform(0.15, 0.30), rnd.uniform(0.12, 0.26))
        k.box((x, y, sz[2] / 2 - 0.01 - 0.002 * i), sz, VKI_STONE_BLOCK_IN, rot=(0.0, 0.0, rnd.uniform(0.0, 3.0)),
              bevel=0.03)                                               # (bottoms apart: T5S)
    for v in k.bm.verts:                                                # weathering toward the floor, blotches
        k.set_dark([v], 0.06 + 0.22 * vki_smoothstep(0.45, 0.0, v.co.z) + 0.10 * (vki_hash01(
            int(v.co.x * 7), int(v.co.y * 7), int(v.co.z * 7)) > 0.8))
    vki_adv_anc_mats(k)
    vki_dpr_gold_mats(k)
    vki_poi_meta(k, "The fallen king", "landmark", "ruins", "examine", use=[[-0.35, -2.25, 0.0]],
                 colliders=[head_box, [1.75, -0.55, 0.20, 1.35, 1.35, 0.40]],
                 vki_place_rule="a floor with 4 x 3 open cells (6 x 4.5 m), in a ruin or a cave under one")


# ---------------------------------------------------------------- POI_Crucible (dwarf halls)
def vki_poi_crucible(k):
    """the great crucible of a dwarven foundry (4.4 x 2.8, 3.0 tall): at the back a round stone furnace on a plinth,
    iron-banded and gold-ringed, its open throat glowing and a glowing mouth under a stone arch; an iron jib crane
    beside it holds a crucible on a chain, tipped to pour a stream of molten metal into the head basin of a stone
    casting bed at the front, whose channels feed six ingot moulds (the far ones cooling); stacks of gold and iron
    ingots, a heap of coal. Molten metal is the lava's material on the WATER slot (M_VKI_Lava, heat: yellow-hot at
    the pour, cooling to orange-red out in the moulds; the GLOW fire blew out to cream there); the furnace's mouth is
    fire (GLOW)"""
    C = Vector((1.15, 0.45, 0.0))                                      # the furnace
    vki_sto_block(k, C.x - 0.95, C.x + 0.95, 0.0, 0.22, C.y - 0.95, C.y + 0.95, bev=0.03, top=VKI_CAP, key="cf0")
    vki_home_lathe(k, [(0.88, 0.215), (0.93, 0.70), (0.87, 1.70), (0.68, 2.10), (0.52, 2.24), (0.40, 2.24),
                       (0.35, 2.06), (0.0, 2.06)], c=tuple(C), segs=16, mi=VKI_STONE_BLOCK_IN)
    for z, mi, r0, r1 in ((0.70, IRON, 0.925, 0.955), (1.20, VKI_DPR_GOLD, 0.905, 0.94), (1.70, IRON, 0.865, 0.895)):
        vki_home_hoop(k, (C.x, C.y, z), r0, r1, 0.07, segs=16, mi=mi)
    gv = _cyl(k, (C.x, C.y, 2.075), 0.345, 0.345, 0.03, 12, WATER)                    # the molten throat
    k.set_heat(gv, 1.0)
    # the mouth: a glowing panel under a stone arch in the furnace's front, iron bars across
    my = C.y - 0.90
    mv = list(set(k.box((C.x, my + 0.02, 0.62), (0.52, 0.10, 0.56), GLOW, bevel=0.0)))
    for v in mv:
        k.set_heat([v], 0.9 if v.co.z < 0.62 else 0.6)
    vki_sto_block(k, C.x - 0.40, C.x - 0.26, 0.30, 0.94, my - 0.10, my + 0.10, bev=0.015, key="cmj0")
    vki_sto_block(k, C.x + 0.26, C.x + 0.40, 0.30, 0.94, my - 0.10, my + 0.10, bev=0.015, key="cmj1")
    vki_sto_block(k, C.x - 0.44, C.x + 0.44, 0.94, 1.10, my - 0.12, my + 0.12, bev=0.02, top=VKI_CAP, key="cml")
    for x in (-0.15, -0.05, 0.05, 0.15):
        k.box((C.x + x, my - 0.05, 0.62), (0.025, 0.025, 0.60), IRON, bevel=0.0)
    # the jib crane: an iron post on a stone footing, the arm out over the casting bed, a brace
    P0 = Vector((-0.05, 1.05, 0.0))
    vki_sto_block(k, P0.x - 0.22, P0.x + 0.22, 0.0, 0.16, P0.y - 0.22, P0.y + 0.22, bev=0.02, key="cjf")
    k.box((P0.x, P0.y, 1.58), (0.13, 0.13, 2.84), IRON, bevel=0.01)
    A1 = Vector((-1.25, -0.23, 2.78))                                   # the arm's end, over the bail
    vki_dpr_rod(k, (P0.x, P0.y, 2.78), A1, 0.11, IRON, d=0.12)
    vki_dpr_rod(k, (P0.x, P0.y, 1.95), (P0.x + (A1.x - P0.x) * 0.55, P0.y + (A1.y - P0.y) * 0.55, 2.74), 0.07, IRON)
    vki_dpr_chain(k, (A1.x, A1.y, 2.72), (A1.x, A1.y, 1.47), 13, sag=0.0)
    # the crucible, tipped toward the casting bed (-y), and its pour
    before = set(k.bm.verts)
    vki_home_lathe(k, [(0.24, 0.0), (0.30, 0.10), (0.34, 0.38), (0.36, 0.44), (0.31, 0.44), (0.28, 0.14),
                       (0.0, 0.14)], c=(0.0, 0.0, 0.0), segs=12, mi=IRON)
    mvv = _cyl(k, (0.0, 0.0, 0.40), 0.30, 0.30, 0.02, 10, WATER)
    k.set_heat(mvv, 1.0)
    for s in (-1.0, 1.0):
        k.box((s * 0.37, 0.0, 0.40), (0.05, 0.05, 0.07), IRON, bevel=0.0)                       # trunnions
    vki_dpr_rod(k, (-0.40, 0.0, 0.42), (0.0, 0.0, 0.78), 0.035, IRON)                            # the bail
    vki_dpr_rod(k, (0.40, 0.003, 0.42), (0.0, 0.003, 0.78), 0.035, IRON)
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((A1.x, A1.y + 0.48, 0.845)) @
                        Matrix.Rotation(math.radians(38.0), 4, "X"))                    # its bail's top under the chain
    lip = Vector((A1.x, -0.305, 0.97))
    basin = Vector((A1.x, -0.62, 0.50))
    pts = [lip + Vector((0.0, -0.02, 0.0))]
    for i in range(1, 6):
        t = i / 5
        pts.append(Vector((A1.x, lip.y + (basin.y - lip.y) * (0.35 * t + 0.65 * t * t) * 0.9, lip.z - (lip.z - basin.z - 0.01) * t * t)))
    pv, _ = vki_poi_tube(k, pts, [0.050, 0.046, 0.042, 0.040, 0.040, 0.044], WATER, segs=6)
    k.set_heat(pv, 1.0)
    # the casting bed: head basin, channels, six moulds (the far ones cooling), cooled ingots in the last two
    vki_sto_block(k, -2.15, 0.16, 0.0, 0.48, -1.36, -0.22, bev=0.03, key="cbd")          # clear of the plinth (0.20)
    vki_sto_block(k, -2.19, 0.20, 0.40, 0.50, -1.40, -0.18, bev=0.015, top=VKI_CAP, key="cbt")
    vki_home_lathe(k, [(0.26, 0.495), (0.27, 0.56), (0.20, 0.56), (0.18, 0.515), (0.0, 0.515)], c=tuple(basin),
                   segs=12, mi=VKI_STONE_BLOCK_IN)
    bv = _cyl(k, (basin.x, basin.y, 0.53), 0.19, 0.19, 0.02, 10, WATER)
    k.set_heat(bv, 0.9)
    for (x0, x1, heat0, heat1) in ((-2.05, basin.x - 0.20, 0.40, 0.75), (basin.x + 0.20, 0.05, 0.75, 0.40)):
        cv = vki_adv_box(k, x0, x1, basin.y - 0.035, basin.y + 0.035, 0.5015, 0.508, WATER)      # channels
        for v in cv:
            k.set_heat([v], heat0 + (heat1 - heat0) * (v.co.x - x0) / (x1 - x0))
    for j, x in enumerate((-1.95, -1.65, -0.85, -0.55, -0.25, 0.05)):
        far = j in (0, 5)                                                # the far moulds have cooled
        fv = vki_adv_box(k, x - 0.025, x + 0.025, -1.01, -0.65, 0.5008, 0.505, VKI_STONE_BLOCK_IN if far else WATER)
        mv_ = vki_adv_box(k, x - 0.13, x + 0.13, -1.18, -0.98, 0.5022, 0.511, VKI_DPR_GOLD if far else WATER)
        if not far:
            k.set_heat(fv + mv_, 0.25 + 0.30 * (j in (1, 2)))
        else:
            k.set_dark(fv, 0.5)
    # ingot stacks, west of the crane; coal by the furnace
    for lay in range(3):
        for j in range(4 - lay):
            if lay % 2 == 0:
                x, y, sx, sy = -1.95 + 0.17 * j + 0.085 * lay, 0.55, 0.14, 0.34
            else:
                x, y, sx, sy = -1.80 + 0.085 * lay, 0.42 + 0.17 * j, 0.34, 0.14
            k.box((x, y, 0.035 + 0.07 * lay), (sx, sy, 0.066), VKI_DPR_GOLD, bevel=0.01)
    for j in range(3):                                                  # iron ingots
        k.box((-1.20 + 0.20 * j, 0.95, 0.04), (0.16, 0.36, 0.07), IRON, bevel=0.01)
        if j < 2:
            k.box((-1.10 + 0.20 * j, 0.95, 0.11), (0.16, 0.36, 0.07), IRON, bevel=0.01)
    rnd = random.Random(5)
    for i in range(16):
        a = rnd.uniform(0.0, 2 * math.pi); d = 0.32 * math.sqrt(rnd.random())
        vki_smy_lump(k, (1.85 + math.cos(a) * d, -0.95 + math.sin(a) * d * 0.8, 0.05 + 0.08 * (1 - d / 0.32)),
                     rnd.uniform(0.07, 0.10), rnd, COAL)
    k.slot_mats[WATER] = "M_VKI_Lava"
    vki_dwf_block_mats(k)
    vki_poi_meta(k, "The great crucible", "workshop", "dwarf", "cast", use=[[-0.8, -2.0, 0.0], [1.15, -1.2, 0.0]],
                 colliders=[[C.x, C.y, 1.12, 1.90, 1.90, 2.24], [-0.995, -0.79, 0.25, 2.39, 1.22, 0.50],
                            [P0.x, P0.y, 1.4, 0.44, 0.44, 2.8], [-1.6, 0.6, 0.12, 0.80, 0.60, 0.24]],
                 vki_lights=[vki_dpr_light("furnace", (C.x, my - 0.35, 0.75), 300.0, [1.0, 0.50, 0.18], 7.0, 0.3),
                             vki_dpr_light("pour", (basin.x, basin.y - 0.25, 1.00), 220.0, [1.0, 0.55, 0.20], 6.0, 0.2)],
                 vki_fx=[dict(fx="furnace_fire", pos=[C.x, C.y, 2.15], scale=1.2),
                         dict(fx="molten_pour", pos=[A1.x, -0.30, 0.80], scale=1.0),
                         dict(fx="sparks", pos=[basin.x, basin.y, 0.60], scale=0.8)],
                 vki_place_rule="against a wall (local +y, the furnace side), a room 3 x 2 cells or more; the "
                                "casting bed's front (local -y) needs a clear cell")


# ---------------------------------------------------------------- POI_NecroCircle (dungeon)
def vki_poi_necro(k):
    """a necromancer's circle (3.9 m across) round an opened sarcophagus: an octagonal dais of dark stone with a
    glowing sigil -- two rings, a seven-pointed star and runes (the FX slot, M_VKI_RuneGlow) -- seven standing stones
    with glowing runes, the sarcophagus at the centre with its lid shoved aside and green light welling from it, a
    skull on the lid, chains from four stones to the tomb's corners, black candles, bones"""
    R = 1.95
    ring = [(R * math.cos(math.pi / 8 + i * math.pi / 4), R * math.sin(math.pi / 8 + i * math.pi / 4)) for i in range(8)]
    vs, fs = vki_prism(k, ring, 0.0, 0.10, VKI_STONE_BLOCK_IN, axis="z", bevel=0.012)
    zt = 0.10
    for (ri, ro, i) in ((1.52, 1.58, 0), (1.70, 1.76, 1)):
        vki_home_hoop(k, (0.0, 0.0, zt - 0.003 + 0.0006 * i), ri, ro, 0.012, segs=28, mi=VKI_FX)
    star = [(1.50 * math.cos(math.pi / 2 + 2 * math.pi * i / 7), 1.50 * math.sin(math.pi / 2 + 2 * math.pi * i / 7))
            for i in range(7)]
    for i in range(7):                                                  # the heptagram {7/3}
        a, b = Vector((*star[i], 0.0)), Vector((*star[(i + 3) % 7], 0.0))
        c = (a + b) / 2
        k.box((c.x, c.y, zt + 0.003 + 0.0007 * i), ((b - a).length, 0.035, 0.006), VKI_FX,
              rot=(0.0, 0.0, math.atan2(b.y - a.y, b.x - a.x)), bevel=0.0)
    rnd = random.Random(13)
    for i in range(14):                                                 # runes between the rings
        a = 2 * math.pi * (i + 0.5) / 14
        c = Vector((1.64 * math.cos(a), 1.64 * math.sin(a), zt + 0.002))
        for j in range(2):
            ang = a + rnd.choice((0.0, 0.6, -0.6, math.pi / 2))
            k.box((c.x + 0.02 * j * math.cos(a), c.y + 0.02 * j * math.sin(a), c.z + 0.0007 * j),
                  (0.075 - 0.02 * j, 0.016, 0.004), VKI_FX, rot=(0.0, 0.0, ang), bevel=0.0)
    # the standing stones, with a glowing rune on their inner faces
    stones = []
    for i in range(7):                                                  # on the star's points: the south is open
        a = math.pi / 2 + 2 * math.pi * i / 7
        c = Vector((1.78 * math.cos(a), 1.78 * math.sin(a), 0.0))
        h = 0.75 + 0.25 * ((i * 3) % 4) / 3
        before = set(k.bm.verts)
        vki_sto_block(k, -0.14, 0.14, zt - 0.02, zt + h, -0.10, 0.10, bev=0.03, key="ns%d" % i)
        k.box((0.0, -0.103, zt + h * 0.62), (0.06, 0.008, 0.16), VKI_FX, bevel=0.0)
        k.box((0.0, -0.104, zt + h * 0.62), (0.13, 0.008, 0.025), VKI_FX, rot=(0.0, 0.5, 0.0), bevel=0.0)
        tilt = rnd.uniform(-0.08, 0.08)
        bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation(c) @
                            Matrix.Rotation(a - math.pi / 2, 4, "Z") @ Matrix.Rotation(tilt, 4, "Y"))   # rune in
        stones.append(c)
    # the sarcophagus, opened: the chest, its lid shoved aside askew, the green glow inside
    bx = lambda x0, x1, y0, y1, z0, z1, mi, bev=0.02: k.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                                                             (x1 - x0, y1 - y0, z1 - z0), mi, bevel=bev)
    bx(-0.98, 0.98, -0.48, 0.48, zt - 0.01, zt + 0.12, DRESS, 0.02)
    for (x0, x1, y0, y1) in ((-0.90, 0.90, -0.40, -0.32), (-0.90, 0.90, 0.32, 0.40), (-0.90, -0.82, -0.32, 0.32),
                             (0.82, 0.90, -0.32, 0.32)):
        bx(x0, x1, y0, y1, zt + 0.115, zt + 0.74, DRESS, 0.012)
    bx(-0.82, 0.82, -0.32, 0.32, zt + 0.115, zt + 0.30, DRESS, 0.0)                              # the floor inside
    bx(-0.80, 0.80, -0.30, 0.30, zt + 0.302, zt + 0.322, VKI_FX, 0.0)                            # the welling glow
    for (x, y) in ((-0.50, 0.05), (0.0, -0.08), (0.45, 0.10)):                                    # bones on it
        vki_dun_bone(k, (x - 0.18, y, zt + 0.35), (x + 0.18, y + 0.05, zt + 0.36), r=0.02)
    vki_dun_skull(k, (-0.58, -0.10, zt + 0.40), s=1.1, yaw=15, pitch=10)
    before = set(k.bm.verts)                                           # the lid, shoved askew across the top
    bx(-0.88, 0.88, -0.38, 0.38, 0.0, 0.10, DRESS, 0.02)
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((0.55, -0.20, zt + 0.745)) @
                        Matrix.Rotation(math.radians(22.0), 4, "Z"))
    # chains from four stones to the tomb's corners, black candles, bones on the dais
    for i, (sx, sy) in zip((1, 2, 5, 6), ((-1, 1), (-1, -1), (1, -1), (1, 1))):
        s_ = stones[i]
        A = Vector((s_.x * 0.93, s_.y * 0.93, zt + 0.55))
        M = Vector((sx * 0.92, sy * 0.40, zt + 0.66))
        vki_dpr_chain(k, A, M, max(4, int((M - A).length / 0.085)), sag=0.0)
    lp = []
    for (x, y) in ((0.0, 1.22), (-1.28, -1.12), (1.28, -1.12)):
        vki_dpr_mound(k, (x, y, zt), 0.13, 0.11, 0.012, VKI_WAX, z0=zt + 0.001, nr=2, ns=8, seed=4, wob=0.2, bump=0.3)
        for (dx, dy, h) in ((0.0, 0.0, 0.30), (-0.07, 0.05, 0.20), (0.06, 0.06, 0.16)):
            lp.append(vki_chp_candle(k, (x + dx, y + dy, zt + 0.004), r=0.028, h=h, segs=8, flame=(0.07, None)))
    for (a, b) in (((-0.9, -1.05), (-0.55, -1.25)), ((0.95, -0.95), (1.25, -0.70)), ((-1.35, -0.15), (-1.30, 0.20))):
        vki_dun_bone(k, (a[0], a[1], zt + 0.02), (b[0], b[1], zt + 0.025), r=0.018)
    vki_dun_skull(k, (-1.45, 0.30, zt + 0.07), s=1.0, yaw=60, pitch=-10)
    k.slot_mats[VKI_FX] = "M_VKI_RuneGlow"
    vki_dun_bone_mats(k)
    vki_dpr_block_mats(k)
    vki_poi_meta(k, "The necromancer's circle", "ritual", "dungeon", "disrupt", use=[[0.0, -2.35, 0.0]],
                 colliders=[[0.0, 0.0, 0.47, 1.96, 0.96, 0.84]] + [[round(c.x, 3), round(c.y, 3), 0.55, 0.32, 0.32, 1.10]
                                                                  for c in stones],
                 vki_lights=[dict(type="POINT", role="ritual", pos=[0.0, 0.0, 1.30], w=180.0, color=[0.40, 1.0, 0.50],
                                  range=6.0, flicker=1, shadows=0, radius=0.3),
                             vki_dpr_light("candles", (0.0, 1.22, 0.55), VKI_DPR_CANDLE_W, VKI_DPR_CANDLE_COL, 3.5, 0.05,
                                           shadows=0)],
                 vki_fx=[dict(fx="ritual_glow", pos=[0.0, 0.0, 0.70], scale=1.5),
                         dict(fx="rune_pulse", pos=[0.0, 0.0, zt], scale=3.8)],
                 vki_place_rule="a floor with a 3 x 3 open cell block (the dais is walkable; the stones leave 1.2 m "
                                "gaps)")


# ---------------------------------------------------------------- POI_RatKing (sewers)
def vki_poi_ratking(k):
    """the rat king's throne (3.0 x 3.0): a heap of refuse and muck, on it a throne of junk -- a broken high-backed
    chair patched with barrel staves before a cart wheel -- crowned with a ring of bones and a rat skull on a pole,
    rag banners, candles stuck in the heap, broken barrels and a crate, a rusty helm, bones and skulls, a scatter of
    stolen gold"""
    rnd = random.Random(31)
    vki_dpr_mound(k, (0.0, 0.10, 0.0), 1.30, 1.10, 0.55, VKI_ASH, z0=0.001, nr=4, ns=16, seed=7, wob=0.14, bump=0.25)
    zs = 0.52                                                           # the throne stands in the heap's top
    for x in (-0.30, 0.30):                                             # legs, sunk in the muck
        for y in (0.05, 0.50):
            k.box((x, y, zs + 0.18), (0.07, 0.07, 0.46), WOOD, bevel=0.0)
    for j in range(4):                                                  # the seat, planks (heights apart: T5S)
        k.box((-0.33 + 0.165 * j + 0.08, 0.28, zs + 0.43 + 0.004 * j), (0.15, 0.62, 0.04), PLANKS,
              rot=(0.0, 0.0, 0.03 * (j - 1.5)), bevel=0.0)
    for s in (-1.0, 1.0):                                               # arms: barrel staves on posts
        k.box((s * 0.36, 0.28, zs + 0.60), (0.06, 0.06, 0.40), WOOD, bevel=0.0)
        k.box((s * 0.37, 0.25, zs + 0.82), (0.10, 0.66, 0.035), PLANKS, rot=(0.12 * s, 0.0, 0.0), bevel=0.0)
    for j, x in enumerate((-0.28, -0.12, 0.05, 0.22)):                   # the tall back, odd boards
        h = 1.05 + 0.18 * ((j * 7) % 3)
        k.box((x, 0.60 + 0.006 * j, zs + 0.40 + h / 2), (0.15, 0.04, h), PLANKS, rot=(0.0, 0.06 * (j - 1.5), 0.0),
              bevel=0.0)
    # the cart wheel behind, a halo; the crown of bones and the rat skull on its pole
    wc = Vector((0.0, 0.72, zs + 1.30))
    vki_home_hoop(k, tuple(wc), 0.56, 0.64, 0.07, segs=16, mi=WOOD, rot=Matrix.Rotation(math.pi / 2, 3, "X"))
    _cyl(k, tuple(wc), 0.10, 0.10, 0.12, 8, WOOD, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.2
        if i == 5:
            continue                                                    # a spoke gone
        vki_dpr_rod(k, (wc.x + 0.09 * math.cos(a), wc.y, wc.z + 0.09 * math.sin(a)),
                    (wc.x + 0.57 * math.cos(a), wc.y, wc.z + 0.57 * math.sin(a)), 0.045, WOOD, d=0.035)
    for i in range(7):                                                  # the crown of bones, on the back's top
        a = 2 * math.pi * i / 7
        c = Vector((0.0, 0.60, zs + 1.72))
        vki_dun_bone(k, (c.x + 0.16 * math.cos(a), c.y + 0.10 * math.sin(a), c.z),
                     (c.x + 0.22 * math.cos(a), c.y + 0.13 * math.sin(a), c.z + 0.28), r=0.017)
    vki_dpr_rod(k, (0.62, 0.55, 0.30), (0.66, 0.60, 2.35), 0.05, WOOD)                           # the pole
    before = set(k.bm.verts)
    vki_dun_skull(k, (0.0, 0.0, 0.0), s=0.9)
    k.box((0.0, -0.12, -0.03), (0.07, 0.16, 0.05), VKI_WAX, bevel=0.0)                            # the rat's snout
    for s in (-1.0, 1.0):
        k.box((s * 0.018, -0.21, -0.055), (0.012, 0.03, 0.045), VKI_WAX, bevel=0.0)              # incisors
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((0.66, 0.55, 2.42)) @
                        Matrix.Rotation(math.radians(-15.0), 4, "Z"))
    # rag banners on poles
    for (x, y, h, c) in ((-1.05, 0.40, 1.90, CLOTH_A), (1.05, -0.35, 1.60, CLOTH_B)):
        vki_dpr_rod(k, (x, y, 0.20), (x + 0.03, y, h), 0.045, WOOD)
        cv, _ = vki_prism(k, [(x + 0.03, h - 0.05), (x + 0.44, h - 0.09), (x + 0.40, h - 0.58), (x + 0.03, h - 0.52)],
                          y - 0.005, y + 0.005, c, axis="y")            # a rag, and a torn strip below it
        vv, _ = vki_prism(k, [(x + 0.10, h - 0.53), (x + 0.22, h - 0.55), (x + 0.19, h - 0.80), (x + 0.12, h - 0.74)],
                          y - 0.012, y - 0.002, c, axis="y")
        k.set_dark(cv + vv, 0.35)
    # junk: two broken barrels, a crate, a helm, bones, skulls, gold
    for (x, y, a, open_) in ((-0.75, -0.55, 0.4, True), (0.85, 0.55, -1.1, False)):
        before = set(k.bm.verts)
        vki_home_lathe(k, [(0.20, -0.30), (0.25, 0.0), (0.20, 0.30)] + ([(0.17, 0.30), (0.21, 0.0), (0.17, -0.30)]
                                                                           if open_ else [(0.0, 0.30)]),
                       c=(0.0, 0.0, 0.0), segs=10, mi=WOOD, closed=open_)
        for z in (-0.20, 0.20):
            vki_home_hoop(k, (0.0, 0.0, z), 0.212, 0.232, 0.035, segs=10, mi=IRON)
        bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((x, y, 0.24)) @
                            Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    k.box((-0.20, -0.95, 0.17), (0.40, 0.34, 0.34), PLANKS, rot=(0.0, 0.3, 0.5), bevel=0.01)
    vki_home_lathe(k, [(0.15, 0.0), (0.15, 0.05), (0.12, 0.13), (0.0, 0.17)], c=(0.45, -0.85, 0.03), segs=10, mi=IRON)
    for i in range(7):
        a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.55, 1.15)
        c = Vector((math.cos(a) * d, 0.1 + math.sin(a) * d * 0.85, 0.0))
        z = 0.55 * max(0.0, 1.0 - (c.x / 1.3) ** 2 - ((c.y - 0.1) / 1.1) ** 2) ** 0.7 + 0.02
        b = rnd.uniform(0.0, math.pi)
        vki_dun_bone(k, (c.x - 0.18 * math.cos(b), c.y - 0.18 * math.sin(b), z + 0.01),
                     (c.x + 0.18 * math.cos(b), c.y + 0.18 * math.sin(b), z + 0.03), r=0.018, dark=0.2)
    for (x, y, yaw) in ((-0.55, -0.20, 30), (0.35, -0.55, -40), (-0.95, 0.20, 70)):
        z = 0.55 * max(0.0, 1.0 - (x / 1.3) ** 2 - ((y - 0.1) / 1.1) ** 2) ** 0.7
        vki_dun_skull(k, (x, y, z + 0.06), s=1.0, yaw=yaw, pitch=-12, dark=0.15)
    for i in range(16):
        a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.2, 0.8)
        x, y = math.cos(a) * d, -0.2 + math.sin(a) * d * 0.6
        z = 0.55 * max(0.0, 1.0 - (x / 1.3) ** 2 - ((y - 0.1) / 1.1) ** 2) ** 0.7
        vki_adv_coin(k, (x, y, z + 0.006 + 0.002 * (i % 3)), rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4))
    lp = []
    for (x, y) in ((-0.55, 0.35), (0.50, 0.05), (-0.25, -0.60)):
        z = 0.55 * max(0.0, 1.0 - (x / 1.3) ** 2 - ((y - 0.1) / 1.1) ** 2) ** 0.7
        lp.append(vki_chp_candle(k, (x, y, z - 0.01), r=0.035, h=0.14, segs=8, flame=(0.07, None)))
    k.slot_mats[VKI_ASH] = "M_VKI_EarthDamp"
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_dpr_gold_mats(k)
    vki_poi_meta(k, "The rat king's throne", "lair", "sewer", "challenge", use=[[0.0, -1.30, 0.0]],
                 colliders=[[0.0, 0.10, 0.45, 2.30, 1.90, 0.90], [0.0, 0.60, 1.40, 1.30, 0.30, 1.30]],
                 vki_lights=[vki_dpr_light("candles", (0.0, -0.20, 1.10), 120.0, VKI_DPR_CANDLE_COL, 5.0, 0.1, shadows=0)],
                 vki_place_rule="a floor with 2 x 2 open cells and a cell clear in front (local -y)")


# ---------------------------------------------------------------- POI_SpringShrine (water)
def vki_poi_spring(k):
    """a sacred spring (3.0 x 3.0): a round carved basin of pale stone brimming with still water, offerings of coins
    on its floor and candles on its rim; behind it a framed stele carved with a sun round a gold boss, a stone spout
    jutting from it pouring a thin stream into the basin (foam where it lands), glowing crystals crowning the stele"""
    vki_home_lathe(k, [(1.05, 0.0), (1.12, 0.10), (1.10, 0.40), (1.04, 0.47), (0.94, 0.47), (0.90, 0.40), (0.88, 0.12),
                       (0.0, 0.12)], c=(0.0, 0.0, 0.0), segs=20, mi=VKI_CAP)
    wv = _cyl(k, (0.0, 0.0, 0.25), 0.895, 0.895, 0.26, 20, WATER)                               # the water
    rnd = random.Random(41)
    for i in range(12):
        a = rnd.uniform(0.0, 2 * math.pi); d = 0.7 * math.sqrt(rnd.random())
        vki_adv_coin(k, (math.cos(a) * d, math.sin(a) * d, 0.126 + 0.001 * (i % 4)), rnd.uniform(-0.1, 0.1), 0.0)
    for a in (-2.2, -1.2, -0.3):                                        # candles on the rim
        vki_chp_candle(k, (0.99 * math.cos(a), 0.99 * math.sin(a), 0.47), r=0.03, h=0.12 + 0.04 * (a > -1.0), segs=8,
                       flame=(0.07, None))
    # the stele: a framed slab with a carved sun (a gold boss) over a stone spout; the crystals crown it
    vki_sto_block(k, -0.48, 0.48, -0.01, 1.62, 0.95, 1.27, bev=0.03, top=VKI_CAP, key="sst")   # (sunk: T5S)
    for (x0, x1, z0, z1) in ((-0.40, 0.40, 1.47, 1.52), (-0.40, 0.40, 0.46, 0.51), (-0.40, -0.35, 0.51, 1.47),
                             (0.35, 0.40, 0.51, 1.47)):                   # the frame, 2 cm proud
        vki_adv_box(k, x0, x1, 0.93, 0.955, z0, z1, VKI_CAP)
    _cyl(k, (0.0, 0.94, 1.18), 0.17, 0.17, 0.025, 12, VKI_CAP, rot=Matrix.Rotation(math.pi / 2, 4, "X"))   # the sun
    _cyl(k, (0.0, 0.925, 1.18), 0.06, 0.06, 0.012, 10, VKI_DPR_GOLD, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    for i in range(8):                                                  # its rays, alternately long and short
        a = 2 * math.pi * i / 8
        ln = 0.10 if i % 2 else 0.07
        c = (0.26 + ln / 2 - 0.05)
        k.box((c * math.cos(a), 0.935 + 0.0015 * (i % 2), 1.18 + c * math.sin(a)), (ln, 0.02, 0.035), VKI_CAP,
              rot=(0.0, -a, 0.0), bevel=0.0)
    vki_adv_box(k, -0.08, 0.08, 0.64, 0.955, 0.87, 0.93, VKI_CAP)          # the spout: a trough out over the water
    for x in (-0.08, 0.05):
        vki_adv_box(k, x, x + 0.03, 0.64, 0.955, 0.93, 0.975, VKI_CAP)
    pts = [(0.66, 0.945), (0.62, 0.935), (0.595, 0.86), (0.575, 0.72), (0.56, 0.55), (0.555, 0.385)]
    vki_wat_sheet(k, pts, 0.045, 0.06, VKI_FX, dark=lambda t: 0.05, seed=9)
    for i, (x, y, r) in enumerate(((0.0, 0.53, (0.16, 0.10)), (-0.13, 0.44, (0.08, 0.06)), (0.14, 0.46, (0.07, 0.05)))):
        vki_wat_foam(k, (x, y), r, 0.381 + 0.0012 * i, seed=50 + i)
    for i, (x, y, h, r) in enumerate(((0.0, 1.10, 0.62, 0.075), (0.16, 1.14, 0.42, 0.06), (-0.15, 1.08, 0.46, 0.06),
                                      (0.30, 1.10, 0.28, 0.045), (-0.30, 1.13, 0.30, 0.045))):
        d = Vector((x * 1.6, (y - 1.11) * 3.0 - 0.15, 1.0)).normalized()
        rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        c = Vector((x, y, 1.60)) + d * (h / 2)
        _cyl(k, tuple(c), r, 0.008, h, 6, MUSH_GLOW, rot=rot)
    # three stepping stones up to the basin
    for i, (x, y) in enumerate(((0.0, -1.45), (-0.30, -1.25), (0.28, -1.22))):
        vki_dpr_blob(k, (x, y), (0.20, 0.15), -0.002 * i, 0.06 + 0.01 * i, VKI_CAP, ns=9, wob=0.2, seed=60 + i)
    k.slot_mats[WATER] = "M_VKI_StreamWater"
    k.slot_mats[VKI_FX] = "M_VKI_WaterFall"
    k.slot_mats[VKI_WAX] = "M_VKI_Foam"
    k.slot_mats[VKI_CAP] = "M_VKI_AncientCap"
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_AncientBlock"
    vki_dpr_gold_mats(k)
    vki_poi_meta(k, "The sacred spring", "shrine", "water", "drink", use=[[0.0, -1.55, 0.0]],
                 colliders=[[0.0, 0.0, 0.24, 2.24, 2.24, 0.48], [0.0, 1.11, 0.81, 0.96, 0.32, 1.62]],
                 vki_water={"kind": "spring", "surface_z": 0.38},
                 vki_lights=[dict(type="POINT", role="crystal", pos=[0.0, 0.70, 2.00], w=140.0, color=VKI_CAV_CRYSTAL_COL,
                                  range=6.0, flicker=0, shadows=0, radius=0.15, specular=0.0)],   # diffuse only: its
                 #                                                        image in the still water read as two discs
                 vki_fx=[dict(fx="spring_pour", pos=[0.0, 0.55, 0.70], scale=0.5),
                         dict(fx="shrine_motes", pos=[0.0, 0.2, 1.0], scale=1.2)],
                 vki_place_rule="a floor with 2 x 2 open cells; by a stream or pool reads best")


# ---------------------------------------------------------------- specs, catalog
VKI_POI_SPECS = [
    ("SM_VKI_Prop_POI_WyrmBones", vki_poi_wyrm, "prop"),
    ("SM_VKI_Prop_POI_ColossusHead", vki_poi_colossus, "prop"),
    ("SM_VKI_Prop_POI_Crucible", vki_poi_crucible, "prop"),
    ("SM_VKI_Prop_POI_NecroCircle", vki_poi_necro, "prop"),
    ("SM_VKI_Prop_POI_RatKing", vki_poi_ratking, "prop"),
    ("SM_VKI_Prop_POI_SpringShrine", vki_poi_spring, "prop"),
]
VKI_POI_NAMES = [n for n, _, _ in VKI_POI_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_POI_SPECS])

VKI_ADVENTURE_CATALOG += [("Points of interest (one per level)", -201.0, VKI_POI_NAMES)]
VKI_ROOMS_CODES.update({"POI_WyrmBones": "WY", "POI_ColossusHead": "KH", "POI_Crucible": "CU", "POI_NecroCircle": "NC",
                        "POI_RatKing": "RK", "POI_SpringShrine": "SP"})
