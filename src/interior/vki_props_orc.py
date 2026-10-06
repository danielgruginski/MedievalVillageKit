# ===================== VKI PROPS ORC: the burnt borderland and the orcs' camps (adventure kit) =====================
# Adventure kit (docs/ADVENTURE_KIT.md). Package "adventure". Loaded by vki_ns() after vki_props_lair, whose helpers
# it uses (vki_lair_*), with the prop helpers (vki_dpr_*, vki_dun_*, vki_home_*, vki_sto_*). Props: origin at the
# footprint centre, back toward +Y, real height (§5). Every top-level name starts with vki_/VKI_ (T18).
# For the RPG's orc chapter (MedievalSetting, 2026-10-05): Greywall's farms north of the town, burned by the orcs, the
# old north wood they cut and burn for their forges, their scout camps. Charred wood is the WOOD slot ("Dark")
# darkened almost to black, with COAL where it burned through; ash is VKI_ASH.
#   burnt:  Prop_Ruin_Farmhouse_Burnt (7.2 x 5 m: broken stone footings, charred corner posts, the chimney left
#           standing, fallen beams, ash and rubble inside, embers still in the ash), Prop_BurntTree_A (a charred
#           trunk, top snapped, stub branches) and _B (a split, leaning trunk), Prop_BurntStump, Overlay_Ash (a burnt
#           patch), Overlay_Tracks_Orc (two furrows where logs were dragged, big bootprints either side, along +Y)
#   orcs:   Prop_Orc_WarTable (a heavy trestle table, a hide map of a walled town with marks on it, a dagger stuck in
#           it, a skull with a candle), Prop_Orc_Banner (the warband's standard, 3.5 m: a red hide with a black tusk, an
#           orc skull, two tusks, an iron spike, a cairn; the sign faces -Y)
#   the siege yard in the burnt march (2026-10-05, the orc chapter's second part): Prop_Siege_Ram (a covered ram on
#           wheels, its iron head out of the front, -Y), Prop_Siege_Tower (half built: two storeys of three, a gin pole
#           hoisting a beam), Prop_Siege_Catapult (an onager, drawn back, throwing toward -Y), each with a _Burnt twin the
#           RPG swaps in when the player fires it; Prop_Orc_Cage / _Open (the prisoners' cage, its door in -Y),
#           Prop_Orc_WarDrum (the drummer at -Y), Overlay_Orc_BearTrap / _Sprung, Prop_Orc_Totem (the war-shaman's)
# Build: g["vki_rebuild"](VKI_ORC_NAMES); test: g["vki_test_pieces"](VKI_ORC_NAMES) -> {}.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

VKI_ORC_CHAR = 0.6                   # how dark charred wood is (vertex darkness on the "Dark" WOOD slot)


def vki_orc_beam(k, a, b, w, d=None, char=VKI_ORC_CHAR, mi=WOOD):
    """a charred timber a -> b (square, w x d), darkened"""
    vs = vki_dpr_rod(k, a, b, w, mi, d=d, bevel=0.015)
    k.set_dark(vs, char)
    return vs


def vki_orc_splinter(k, c, r, h, seed, n=4, mi=WOOD, char=VKI_ORC_CHAR):
    """a snapped end: n thin wedges of uneven height standing up from the disc (c, r)"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-0.2, 0.2)) / n
        p = Vector(c) + Vector((math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, 0.0))
        hh = h * rnd.uniform(0.4, 1.0)
        v = _cyl(k, (p.x, p.y, p.z + hh / 2), r * 0.42, 0.004, hh, 4, mi,
                 rot=Matrix.Rotation(rnd.uniform(-0.2, 0.2), 4, "X") @ Matrix.Rotation(a, 4, "Z"))
        k.set_dark(v, char)
        out += v
    return out


def vki_orc_stone(k, c, r, seed, dark=0.15, mi=VKI_STONE_BLOCK_IN):
    v = _ico(k, c, r, mi, scale=(1.2, 0.95, 0.7), sub=1, jit=0.02 * r / 0.1, seed=seed)
    k.project(vki_faces_of(v), mi)
    k.set_dark(v, dark)
    return v


def vki_orc_wall(k, a, b, h0, h1, t, seed, gaps=(), soot=0.0, course=0.3):
    """a broken stone footing from a to b (plan, z 0), t thick, laid in courses of stones (`course` high, 0.32-0.6
    long, each course's joints staggered, every stone a little skewed); the wall's height wanders along its run between
    h0 and h1, so its top is ragged course by course; along a `gaps` run (fractions) only the bottom course is left,
    rubble beside it. `soot` darkens the stones toward the top (the fire was inside)."""
    rnd = random.Random(seed)
    A = Vector((a[0], a[1], 0.0)); B = Vector((b[0], b[1], 0.0))
    u = (B - A); L = u.length; u /= L
    nrm = Vector((-u.y, u.x, 0.0))
    yaw = math.atan2(u.y, u.x)
    ctrl = [rnd.uniform(h0, h1) for _ in range(max(3, int(L / 1.1) + 2))]

    def height(s):
        f = s / L * (len(ctrl) - 1)
        i = min(int(f), len(ctrl) - 2)
        return ctrl[i] + (ctrl[i + 1] - ctrl[i]) * (f - i)
    for c in range(int(math.ceil(h1 / course))):
        z0 = c * course
        s = -rnd.uniform(0.1, 0.25) if c % 2 else 0.0                     # joints staggered course to course
        i = 0
        while s < L - 0.04:
            ln = rnd.uniform(0.32, 0.6)
            s0, s1 = max(s, 0.0), min(s + ln, L)
            s += ln
            if s1 - s0 < 0.14:
                continue
            mid = (s0 + s1) / 2
            if c > 0 and any(g0 <= mid / L <= g1 for g0, g1 in gaps):
                continue                                                  # fallen here
            if c > 0 and height(mid) < z0 + course * 0.5:
                continue                                                  # the wall is lower here
            hh = course * rnd.uniform(0.86, 1.0)
            p = A + u * mid + nrm * rnd.uniform(-0.025, 0.025)
            vs = list(set(k.box((p.x, p.y, z0 + hh / 2), (s1 - s0 - 0.025, t * rnd.uniform(0.88, 1.0), hh), VKI_STONE_BLOCK_IN,
                                rot=(0, 0, yaw + rnd.uniform(-0.05, 0.05)), bevel=0.0, jitter=0.022,
                                seed=seed * 101 + c * 17 + i)))
            k.set_dark(vs, rnd.uniform(0.0, 0.12) + soot * min(1.0, (z0 + course) / max(h1, 0.01)) ** 1.5)
            i += 1
    for j, (g0, g1) in enumerate(gaps):                                  # what fell, beside the run
        for m in range(5):
            p = A + u * (rnd.uniform(g0, g1) * L) + nrm * rnd.uniform(-0.7, 0.7)
            vki_orc_stone(k, (p.x, p.y, 0.08), rnd.uniform(0.12, 0.2), seed * 31 + j * 7 + m)


# ---------------------------------------------------------------- burnt
def vki_orc_farmhouse_ruin(k):
    """a farmhouse the orcs burned (7.2 x 5 m footprint, the chimney 4.4 m): stone footings broken down to
    0.3-1.6 m (the door gap at the front, -Y, a fallen run at the back), four charred corner posts (two snapped
    short), the chimney left standing at the east gable with its blackened hearth, the ridge beam and rafters fallen
    in across the ash, rubble, and a few embers still glowing under the ash"""
    X, Y, T = 3.6, 2.5, 0.5
    vki_orc_wall(k, (-X, -Y), (-0.75, -Y), 0.3, 1.0, T, 1, soot=0.35)                 # front, west of the door
    vki_orc_wall(k, (0.45, -Y), (X, -Y), 0.5, 1.4, T, 2, gaps=((0.55, 0.75),), soot=0.35)
    vki_orc_wall(k, (-X, Y), (X - 0.9, Y), 0.6, 1.6, T, 3, gaps=((0.3, 0.45),), soot=0.4)   # back
    vki_orc_wall(k, (-X, -Y + 0.25), (-X, Y - 0.25), 0.35, 1.2, T, 4, soot=0.35)        # west gable
    vki_orc_wall(k, (X, -Y + 0.25), (X, -0.25), 0.4, 1.1, T, 5, soot=0.35)              # east gable, south of the chimney
    # the chimney (east gable): a stone stack, its flue, a cap; the hearth's mouth into the house (-X), sooted
    cx, cy = X - 0.05, 0.85
    rc = random.Random(40)
    for c in range(15):                                                  # courses: the stack, then the flue, broken off
        z0 = c * 0.29
        w, d, x = (0.95, 1.4, cx) if z0 < 2.3 else (0.66, 0.84, cx + 0.06)
        if c == 14:                                                      # the top course half gone
            w, d, x = w * 0.6, d * 0.7, x + 0.12
        vs = list(set(k.box((x + rc.uniform(-0.02, 0.02), cy + rc.uniform(-0.02, 0.02), z0 + 0.14),
                            (w + rc.uniform(-0.03, 0.03), d + rc.uniform(-0.03, 0.03), 0.28), VKI_STONE_BLOCK_IN,
                            rot=(0, 0, rc.uniform(-0.03, 0.03)), bevel=0.0, jitter=0.012, seed=400 + c)))
        k.set_dark(vs, 0.06 + 0.42 * (z0 / 4.2) ** 1.5)                   # soot rising to the top
    k.box((cx - 0.49, cy, 0.52), (0.05, 0.78, 0.82), VOID, bevel=0.0)                    # the hearth's mouth
    vki_orc_beam(k, (cx - 0.52, cy - 0.55, 0.98), (cx - 0.52, cy + 0.55, 0.98), 0.14, d=0.16)   # its lintel
    # charred corner posts: SW and NE stand tall, NW and SE snapped short
    for (px, py, h, sd) in ((-X + 0.3, -Y + 0.3, 2.6, 50), (X - 0.3, Y - 0.3, 2.1, 51), (-X + 0.3, Y - 0.3, 1.0, 52),
                            (X - 0.3, -Y + 0.3, 0.7, 53)):
        vki_orc_beam(k, (px, py, -0.02), (px, py, h), 0.2)
        vki_orc_splinter(k, (px, py, h - 0.02), 0.2, 0.32, sd)
    # the fallen ridge beam and rafters: across the house, one end on the wall or the post, the other in the ash
    vki_orc_beam(k, (-X + 0.3, -Y + 0.4, 2.5), (1.2, 1.4, 0.15), 0.22, d=0.2)            # off the SW post
    vki_orc_beam(k, (-2.6, 1.9, 1.5), (0.6, -1.2, 0.12), 0.16)
    vki_orc_beam(k, (1.4, -2.2, 1.2), (2.6, 1.2, 0.1), 0.15)
    vki_orc_beam(k, (cx - 0.55, cy + 0.2, 2.2), (1.3, 0.6, 0.08), 0.14)                  # a rafter against the chimney
    vki_orc_beam(k, (-1.8, -0.9, 0.06), (-0.2, -1.6, 0.06), 0.18, d=0.12)               # lying flat
    # ash over the floor, rubble heaps under the fallen runs, charred boards
    ash = vki_dpr_mound(k, (-0.1, 0.1, 0.0), 2.9, 2.0, 0.16, VKI_ASH, z0=0.001, nr=3, ns=18, seed=7, wob=0.14, bump=0.2)
    k.set_dark(ash, 0.15)
    rnd = random.Random(9)
    for i in range(12):
        x, y = rnd.uniform(-2.8, 2.6), rnd.uniform(-1.8, 1.8)
        vki_orc_stone(k, (x, y, 0.1), rnd.uniform(0.1, 0.17), 60 + i, dark=0.3)
    for i in range(6):
        x, y = rnd.uniform(-2.6, 2.2), rnd.uniform(-1.6, 1.6)
        a = rnd.uniform(0, math.pi)
        vs = list(set(k.box((x, y, 0.17), (0.9, 0.16, 0.035), WOOD, rot=(0, rnd.uniform(-0.15, 0.15), a), bevel=0.01)))
        k.set_dark(vs, VKI_ORC_CHAR)
    for i, (x, y, r) in enumerate(((0.9, -0.5, 0.13), (-1.4, 0.8, 0.1))):           # still smouldering
        c = _ico(k, (x, y, 0.16), r, COAL, scale=(1.5, 1.1, 0.5), sub=1, jit=0.02, seed=90 + i)
        k.project(vki_faces_of(c), COAL)
        vki_sto_embers(k, x, y, 0.17, 6, r * 1.3, r, 70 + i, core=0.2, rmin=0.03, rmax=0.045, hmax=0.5)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_note="outdoors (a KitVillage layout): the door gap faces -Y; walk round it, not through")


def vki_orc_tree(k, seed, h, r, lean, forks, split=False):
    """a burnt tree: a charred trunk (darkest at the foot) flaring into roots, its top snapped and splintered, a few
    stub branches burned short; split: the trunk forks low and one fork is broken off"""
    rnd = random.Random(seed)
    top = Vector((lean[0], lean[1], h))
    before = set(k.bm.verts)
    def_log(k, (0.0, 0.0, -0.15), tuple(top), r, segs=10, mi=BARK_OAK, top_cap=True, bot_cap=True, taper=0.5,
            seed=seed, wob=0.1, ts=(0.0, 0.2, 0.45, 0.7, 1.0), bend=0.12)
    trunk = [v for v in k.bm.verts if v not in before]
    vki_orc_splinter(k, tuple(top + Vector((0, 0, -0.04))), r * 0.55, 0.45, seed + 1, n=5, mi=BARK_OAK)
    for i in range(5):                                                   # roots
        a = 2 * math.pi * (i + rnd.uniform(-0.25, 0.25)) / 5
        rv = vki_lair_log(k, (math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, 0.35),
                          (math.cos(a) * r * 3.2, math.sin(a) * r * 3.2, -0.12), r * 0.42, seed + 10 + i, segs=6, bend=0.05)
        k.set_dark(rv, 0.68)
    for j, (t, l) in enumerate(forks):                                   # stub branches, burned short
        a = rnd.uniform(0, 2 * math.pi)
        p = Vector((lean[0] * t, lean[1] * t, h * t))
        d = Vector((math.cos(a), math.sin(a), rnd.uniform(0.5, 1.1))).normalized()
        bv = vki_lair_log(k, tuple(p), tuple(p + d * l), r * rnd.uniform(0.25, 0.35), seed + 20 + j, segs=6, bend=0.08)
        k.set_dark(bv, 0.6)
    if split:                                                            # a second fork, broken off
        p = Vector((lean[0] * 0.35, lean[1] * 0.35, h * 0.35))
        d = Vector((-lean[0] - 0.4, -lean[1] + 0.3, 1.0)).normalized()
        sv = vki_lair_log(k, tuple(p), tuple(p + d * h * 0.4), r * 0.6, seed + 30, segs=8, bend=0.06)
        k.set_dark(sv, 0.62)
        vki_orc_splinter(k, tuple(p + d * h * 0.4), r * 0.35, 0.35, seed + 31, n=4, mi=BARK_OAK)
    for v in trunk:                                                      # charred to black at the foot, ash grey above
        k.set_dark([v], 0.72 if v.co.z < h * 0.3 else 0.58)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_note="outdoors: a tree of the burnt north wood (forest species or a single tree)")


def vki_orc_tree_a(k):
    vki_orc_tree(k, 401, 5.6, 0.3, (0.25, -0.1), ((0.45, 1.3), (0.62, 0.9), (0.78, 0.6)))


def vki_orc_tree_b(k):
    vki_orc_tree(k, 417, 4.2, 0.34, (-0.55, 0.2), ((0.6, 0.8),), split=True)


def vki_orc_stump(k):
    """a burnt stump (0.8 m across, 0.6 high): a charred trunk's foot, its top burned to a ragged crater of splinters,
    roots spreading"""
    rnd = random.Random(23)
    before = set(k.bm.verts)
    def_log(k, (0.0, 0.0, -0.1), (0.03, 0.0, 0.55), 0.3, segs=10, mi=BARK_OAK, top_cap=True, bot_cap=True, taper=0.85,
            seed=23, wob=0.12, ts=(0.0, 0.5, 1.0))
    sv = [v for v in k.bm.verts if v not in before]
    k.set_dark(sv, 0.7)
    vki_orc_splinter(k, (0.03, 0.0, 0.5), 0.3, 0.3, 24, n=6, mi=BARK_OAK)
    for i in range(4):
        a = 2 * math.pi * (i + rnd.uniform(-0.2, 0.2)) / 4
        rv = vki_lair_log(k, (math.cos(a) * 0.15, math.sin(a) * 0.15, 0.25),
                          (math.cos(a) * 0.75, math.sin(a) * 0.75, -0.1), 0.11, 25 + i, segs=6, bend=0.05)
        k.set_dark(rv, 0.68)
    c = _ico(k, (0.03, 0.0, 0.56), 0.16, COAL, scale=(1.0, 1.0, 0.25), sub=1, jit=0.02, seed=26)
    k.project(vki_faces_of(c), COAL)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_orc_ash(k):
    """a burnt patch (about 2.6 x 2 m): grey ash over blackened ground, charred sticks and cinders in it"""
    g = vki_dpr_blob(k, (0.0, 0.0), (1.35, 1.0), 0.001, 0.006, COAL, ns=14, wob=0.28, seed=3)
    k.project(vki_faces_of(g), COAL)
    z = 0.0065                                                           # the ash in layers over it, each on the last
    for i, (x, y, rx, ry) in enumerate(((-0.25, 0.1, 0.9, 0.62), (0.45, -0.2, 0.55, 0.42))):
        a = vki_dpr_blob(k, (x, y), (rx, ry), z, z + 0.008, VKI_ASH, ns=12 - 2 * i, wob=0.3, seed=4 + i)
        k.set_dark(a, 0.1 + 0.1 * i)
        z += 0.0085
    rnd = random.Random(5)
    for i in range(5):
        x, y = rnd.uniform(-0.9, 0.9), rnd.uniform(-0.6, 0.6)
        vs = list(set(k.box((x, y, 0.039), (rnd.uniform(0.25, 0.55), 0.05, 0.04), WOOD,
                            rot=(0, 0, rnd.uniform(0, math.pi)), bevel=0.0)))
        k.set_dark(vs, VKI_ORC_CHAR)
    for i in range(6):
        c = _ico(k, (rnd.uniform(-1.1, 1.1), rnd.uniform(-0.8, 0.8), 0.03), rnd.uniform(0.02, 0.04), COAL,
                 scale=(1.3, 1.0, 0.6), sub=0, seed=40 + i)
        k.project(vki_faces_of(c), COAL)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_orc_tracks(k):
    """the orcs' tracks (6 m along +Y, 2.4 wide): two furrows where logs were dragged, a low ridge thrown up either
    side of each, and big bootprints (0.4 m long, a hand longer than a man's) of two orcs walking either side"""
    rnd = random.Random(11)
    for x in (-0.3, 0.32):
        f = vki_dpr_blob(k, (x, 0.0), (0.15, 2.95), 0.001, 0.007, SOIL, ns=12, wob=0.05, seed=12 + int(x * 10))
        k.set_dark(f, 0.28)
    for side, x0, seed in ((-1, -0.95, 30), (1, 0.98, 50)):
        for i in range(6):                                               # long strides, left and right feet
            y = -2.6 + i * 1.02 + rnd.uniform(-0.05, 0.05)
            x = x0 + (0.13 if i % 2 else -0.13) + rnd.uniform(-0.03, 0.03)
            p = vki_dpr_blob(k, (x, y), (0.085, 0.21), 0.001, 0.006, SOIL, ns=6, wob=0.06, seed=seed + i)
            k.set_dark(p, 0.4)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_note="the tracks run toward +Y (turn it to where they went)")


# ---------------------------------------------------------------- orcs
def vki_orc_tusk(k, base, d, up, L, r, seed, mi=VKI_WAX, n=7, segs=8, curve=0.35):
    """a curved tusk from base along d, bending toward up over its length, radius r tapering to a point"""
    base = Vector(base); d = Vector(d).normalized(); up = Vector(up)
    side = d.cross(up).normalized(); up2 = side.cross(d).normalized()
    rings = []
    for i in range(n - 1):
        t = i / (n - 1)
        c = base + d * L * t + up2 * L * curve * t * t
        tg = (d * L + up2 * L * curve * 2 * t).normalized()
        s1 = tg.cross(up2).normalized(); s2 = s1.cross(tg).normalized()
        rr = r * (1.0 - t) ** 0.75 + 0.003
        rings.append([k.bm.verts.new(c + (s1 * math.cos(2 * math.pi * j / segs) + s2 * math.sin(2 * math.pi * j / segs)) * rr)
                      for j in range(segs)])
    tip = k.bm.verts.new(base + d * L + up2 * L * curve)
    fs = [k.bm.faces.new(rings[0][::-1])]
    for A, B in zip(rings[:-1], rings[1:]):
        for j in range(segs):
            jj = (j + 1) % segs
            fs.append(k.bm.faces.new((A[j], A[jj], B[jj], B[j])))
    for j in range(segs):
        fs.append(k.bm.faces.new((rings[-1][j], rings[-1][(j + 1) % segs], tip)))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.smooth = True
    k.project(fs, mi)
    return [v for rg in rings for v in rg] + [tip]


def vki_orc_crescent(k, p0, p1, p2, w0, y, mi=VOID, n=14, t=0.006):
    """a tusk painted on an upright face at depth y (x, z plan): its middle line the curve p0 -> p2 bent toward p1
    (quadratic), w0 wide at the root (p0) tapering to the point (p2)"""
    P0, P1, P2 = Vector(p0), Vector(p1), Vector(p2)
    out, inn = [], []
    for i in range(n + 1):
        s = i / n
        c = P0 * (1 - s) ** 2 + P1 * 2 * s * (1 - s) + P2 * s * s
        tg = ((P1 - P0) * 2 * (1 - s) + (P2 - P1) * 2 * s).normalized()
        nr = Vector((-tg.y, tg.x))
        w = w0 / 2 * (1 - s) ** 0.85
        out.append(c + nr * w)
        inn.append(c - nr * w)
    pts = [(p.x, y, p.y) for p in out] + [(p.x, y, p.y) for p in inn[-2::-1]]
    return vki_lair_slab(k, pts, mi, t=t)


def vki_orc_crescent3(k, o, U, V, p0, p1, p2, w0, mi=VOID, n=14, t=0.006):
    """vki_orc_crescent on any plane: the point (a, b) of the plane is o + U a + V b"""
    o = Vector(o); U = Vector(U); V = Vector(V)
    P0, P1, P2 = Vector(p0), Vector(p1), Vector(p2)
    out, inn = [], []
    for i in range(n + 1):
        s = i / n
        c = P0 * (1 - s) ** 2 + P1 * 2 * s * (1 - s) + P2 * s * s
        tg = ((P1 - P0) * 2 * (1 - s) + (P2 - P1) * 2 * s).normalized()
        nr = Vector((-tg.y, tg.x))
        w = w0 / 2 * (1 - s) ** 0.85
        out.append(c + nr * w)
        inn.append(c - nr * w)
    return vki_lair_slab(k, [tuple(o + U * p.x + V * p.y) for p in out + inn[-2::-1]], mi, t=t)


def vki_orc_mark(k, pts, z, mi=VOID, t=0.004):
    """a painted mark: a flat plate over the polygon pts (plan) at height z"""
    return vki_lair_slab(k, [(x, y, z) for x, y in pts], mi, t=t)


def vki_orc_band(k, pts, w, z, mi=VOID, t=0.004, closed=True):
    """a painted line along pts (plan), w wide, t thick at height z, as one closed solid strip (closed: a ring), so its
    joints do not overlap the way strokes laid end to end would"""
    P = [Vector((x, y)) for x, y in pts]
    n = len(P)
    O, I = [], []
    for i in range(n):
        a = P[i - 1] if (closed or i > 0) else P[i]
        b = P[(i + 1) % n] if (closed or i < n - 1) else P[i]
        d = (b - a).normalized()
        nr = Vector((-d.y, d.x)) * (w / 2)
        O.append(P[i] + nr); I.append(P[i] - nr)
    zt, zb = z + t / 2, z - t / 2
    Ot = [k.bm.verts.new((p.x, p.y, zt)) for p in O]; It = [k.bm.verts.new((p.x, p.y, zt)) for p in I]
    Ob = [k.bm.verts.new((p.x, p.y, zb)) for p in O]; Ib = [k.bm.verts.new((p.x, p.y, zb)) for p in I]
    fs = []
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        fs += [k.bm.faces.new((Ot[i], Ot[j], It[j], It[i])), k.bm.faces.new((Ob[i], Ib[i], Ib[j], Ob[j])),
               k.bm.faces.new((Ob[i], Ob[j], Ot[j], Ot[i])), k.bm.faces.new((Ib[i], It[i], It[j], Ib[j]))]
    if not closed:
        fs += [k.bm.faces.new((Ot[0], It[0], Ib[0], Ob[0])), k.bm.faces.new((Ot[-1], Ob[-1], Ib[-1], It[-1]))]
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.smooth = False
    k.project(fs, mi)
    return Ot + It + Ob + Ib


def vki_orc_stroke(k, a, b, w, z, mi=VOID):
    """a painted stroke a -> b (plan), w wide, at height z"""
    a = Vector((a[0], a[1])); b = Vector((b[0], b[1])); d = (b - a); n = Vector((-d.y, d.x)).normalized() * (w / 2)
    return vki_orc_mark(k, [tuple(a - n), tuple(b - n), tuple(b + n), tuple(a + n)], z, mi)


def vki_orc_wartable(k):
    """the scouts' war table (1.9 x 1.1 m, top 0.95): three thick planks on two crooked trestles, a hide map of a walled
    town pinned on it -- its wall ring and towers, the north gate ringed twice in red, the south road struck through,
    tallies of logs and a sketch of a frame on wheels with a long beam -- a dagger stuck through it, a skull with a
    candle"""
    for i, y in enumerate((-0.37, 0.0, 0.37)):
        vs = list(set(k.box((0.0, y, 0.905), (1.9, 0.35, 0.09), WOOD, bevel=0.02, jitter=0.008, seed=i)))
        k.set_dark(vs, 0.1 * i)
    for x in (-0.68, 0.68):
        vki_lair_log(k, (x * 1.04, -0.44, -0.03), (x, -0.04, 0.86), 0.055, int(70 + x * 10), segs=6, bend=0.04)
        vki_lair_log(k, (x * 1.04, 0.44, -0.03), (x, 0.04, 0.86), 0.055, int(72 + x * 10), segs=6, bend=0.04)
        vki_dpr_rod(k, (x, -0.33, 0.3), (x, 0.33, 0.3), 0.06, WOOD)
    z = 0.955
    hv = vki_lair_hide(k, [(-0.66, -0.44, z), (0.66, -0.44, z), (0.66, 0.44, z), (-0.66, 0.44, z)], dark=0.0, seed=3,
                       nu=3, nv=2, t=0.008, mottle=0.04, edge=0.15)
    for (x, y) in ((-0.62, -0.4), (0.62, -0.4), (0.62, 0.4), (-0.62, 0.4)):          # pinned: iron spikes
        vki_dpr_rod(k, (x, y, 0.95), (x, y, 1.0), 0.016, IRON)
    # the marks: each line one strip, so no two pieces of paint lie in one plane; what crosses a line lies a step over it
    zm, up = z + 0.0065, 0.0045
    cx, cy, R = -0.12, 0.03, 0.24                                        # the town: its wall ring, towers on it
    rnd = random.Random(5)
    ring = [(cx + math.cos(2 * math.pi * i / 12) * R * rnd.uniform(0.92, 1.06),
             cy + math.sin(2 * math.pi * i / 12) * R * 0.85 * rnd.uniform(0.92, 1.06)) for i in range(12)]
    vki_orc_band(k, ring, 0.014, zm)
    for i in (0, 2, 4, 6, 8, 10):
        x, y = ring[i]
        vki_orc_mark(k, [(x - 0.022, y - 0.022), (x + 0.022, y - 0.022), (x + 0.022, y + 0.022), (x - 0.022, y + 0.022)], zm + up)
    gx, gy = ring[3]                                                     # the north gate (map +Y), ringed twice in red
    for rr in (0.05, 0.075):
        vki_orc_band(k, [(gx + math.cos(2 * math.pi * j / 12) * rr, gy + math.sin(2 * math.pi * j / 12) * rr) for j in range(12)],
                     0.008, zm + up, CLOTH_A)
    sx, sy = ring[9]                                                     # the south road, struck through
    vki_orc_band(k, [(sx + 0.004, sy - 0.014), (sx + 0.018, sy - 0.1), (sx + 0.03, sy - 0.18)], 0.012, zm, closed=False)
    vki_orc_stroke(k, (sx - 0.06, sy - 0.13), (sx + 0.09, sy - 0.06), 0.016, zm + 2 * up, CLOTH_A)
    for gr in range(3):                                                  # tallies of logs, in fives
        for t in range(4):
            x = 0.32 + gr * 0.09 + t * 0.016
            vki_orc_stroke(k, (x, -0.33), (x, -0.25), 0.006, zm)
        vki_orc_stroke(k, (0.31 + gr * 0.09, -0.27), (0.39 + gr * 0.09, -0.31), 0.006, zm + up)
    fx, fy = 0.4, 0.2                                                    # a frame on wheels with a long beam
    vki_orc_band(k, [(fx - 0.1, fy - 0.05), (fx + 0.1, fy - 0.05), (fx + 0.1, fy + 0.08), (fx - 0.1, fy + 0.08)], 0.008, zm)
    vki_orc_stroke(k, (fx - 0.18, fy + 0.02), (fx + 0.16, fy + 0.02), 0.008, zm + up)
    for wx in (fx - 0.07, fx + 0.07):
        vki_orc_band(k, [(wx + math.cos(2 * math.pi * j / 10) * 0.028, fy - 0.088 + math.sin(2 * math.pi * j / 10) * 0.028)
                         for j in range(10)], 0.006, zm)
    # the dagger, driven through the map beside the town
    dx, dy = 0.12, -0.14
    vki_dpr_rod(k, (dx, dy, 0.93), (dx, dy, 1.1), 0.034, IRON, d=0.008)            # blade
    vki_dpr_rod(k, (dx - 0.06, dy, 1.1), (dx + 0.06, dy, 1.1), 0.02, IRON)        # guard
    vki_dpr_rod(k, (dx, dy, 1.1), (dx, dy, 1.21), 0.026, WOOD)                    # grip
    _ico(k, (dx, dy, 1.225), 0.022, IRON, sub=1, seed=8)                          # pommel
    # a skull with a candle on it, at the table's west end
    vki_dun_skull(k, (-0.8, 0.28, 1.02), s=1.0, yaw=25)
    _cyl(k, (-0.8, 0.28, 1.15), 0.024, 0.022, 0.09, 8, VKI_WAX)
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.95, 0]], vki_nav="block",
                  vki_note="the map's town is drawn north up (+Y); the RPG's clue marker stands at its middle")


def vki_orc_banner(k):
    """the warband's standard (3.5 m): a pole in a cairn, an iron spike, a crossbar, a red-dyed hide with the black tusk
    (the warlord's sign) facing -Y, an orc skull (tusked) under the spike, two tusks hung from the bar on cords"""
    rnd = random.Random(31)
    for i in range(7):                                                   # the cairn
        a = 2 * math.pi * i / 7 + rnd.uniform(-0.2, 0.2)
        vki_orc_stone(k, (math.cos(a) * 0.26, math.sin(a) * 0.26, 0.1), rnd.uniform(0.13, 0.17), 300 + i, dark=0.2)
    vki_orc_stone(k, (0.05, 0.02, 0.27), 0.12, 310, dark=0.25)
    vki_lair_log(k, (0.0, 0.02, -0.05), (0.02, 0.02, 3.3), 0.07, 320, segs=8, bend=0.02)
    _cyl(k, (0.02, 0.02, 3.42), 0.05, 0.004, 0.26, 8, IRON)                       # the spike
    vki_dpr_rod(k, (-0.62, -0.03, 2.98), (0.64, -0.03, 2.95), 0.07, WOOD)          # crossbar
    for x in (-0.55, 0.0, 0.55):                                         # lashings
        vki_dpr_rod(k, (x, -0.075, 2.92), (x, -0.075, 3.02), 0.05, BURLAP, d=0.012)
    hv = vki_lair_hide(k, [(-0.52, -0.09, 2.93), (0.54, -0.09, 2.9), (0.48, -0.12, 1.35), (-0.5, -0.12, 1.38)],
                       dark=0.15, seed=33, nu=3, nv=4, t=0.016, sagv=(0.0, -0.03, 0.0), ragged=0.09, mottle=0.08,
                       edge=0.18, mi=CLOTH_A)
    # the black tusk on the hide's face: its root high on the left, curving over and down to a point on the right
    vki_orc_crescent(k, (-0.24, 2.62), (0.42, 2.66), (0.16, 1.62), 0.17, -0.137)
    # the orc's skull under the spike, tusks from its jaw
    vki_dun_skull(k, (0.02, -0.04, 3.14), s=1.35, yaw=0, pitch=-8)
    for s in (-1, 1):
        vki_orc_tusk(k, (0.02 + s * 0.045, -0.13, 3.06), (s * 0.15, -0.35, 0.6), (0, 0, 1), 0.1, 0.018, 340 + s)
    for s in (-1, 1):                                                    # trophies hung from the bar's ends
        x = s * 0.58
        vki_dpr_rod(k, (x, -0.05, 2.94), (x, -0.05, 2.62), 0.012, BURLAP)
        vki_orc_tusk(k, (x, -0.05, 2.62), (s * 0.15, -0.1, -1.0), (s, 0, 0), 0.34, 0.035, 350 + s)
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_note="3.5 m: the warlord's sign (a black tusk) faces -Y")


# ---------------------------------------------------------------- the siege yard (the burnt march)
VKI_ORC_FRESH = 0.05                 # new-cut timber, hardly darkened: the engines read light against the burnt land


def vki_orc_timber(k, a, b, w, d=None, dark=VKI_ORC_FRESH, bevel=0.012, mi=WOOD):
    """a sawn timber a -> b (w x d)"""
    vs = vki_dpr_rod(k, a, b, w, mi, d=d, bevel=bevel)
    k.set_dark(vs, dark)
    return vs


def vki_orc_turn(d):
    """the rotation taking +Z to the direction d (a 4x4, for _cyl)"""
    return Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(d).normalized()).to_matrix().to_4x4()


def vki_orc_cone(k, base, d, r0, r1, L, segs, mi):
    """a cone (or a tapering pole) from base along d, radius r0 at the base, r1 at the far end"""
    d = Vector(d).normalized()
    return _cyl(k, tuple(Vector(base) + d * L / 2), r0, r1, L, segs, mi, rot=vki_orc_turn(d))


def vki_orc_ring_x(k, c, r_in, r_out, w, mi=IRON, n=14):
    """an annulus about the X axis (a wheel's tyre)"""
    fs = ring(k, (0.0, 0.0, 0.0), r_in, r_out, w, mi, n=n, axis="Y")
    vs = list({v for f in fs for v in f.verts})
    bmesh.ops.transform(k.bm, matrix=Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.pi / 2, 4, "Z"), verts=vs)
    k.bm.normal_update()
    k.project(fs, mi)
    return vs


def vki_orc_wheel(k, c, r, w, dark=0.08):
    """a solid wheel turning about X: a disc of planks, an iron tyre, an iron hub boss, an iron strap across each face"""
    R = Matrix.Rotation(math.pi / 2, 4, "Y")
    d = _cyl(k, c, r - 0.04, r - 0.04, w, 14, WOOD, rot=R)
    k.set_dark(d, dark)
    vki_orc_ring_x(k, c, r - 0.055, r, w + 0.014)
    _cyl(k, c, 0.1, 0.1, w + 0.1, 8, IRON, rot=R)
    cx, cy, cz = c
    for s in (-1, 1):
        k.box((cx + s * (w / 2 + 0.009), cy, cz), (0.012, 0.07, 2 * (r - 0.07)), IRON, bevel=0.0)


def vki_orc_band_on(k, a, b, t, r_in, r_out, h, mi=IRON, segs=10):
    """a band (iron, or a rope sling) round the pole a -> b at the fraction t of its length"""
    a = Vector(a); b = Vector(b)
    return vki_home_hoop(k, tuple(a.lerp(b, t)), r_in, r_out, h, segs=segs, mi=mi,
                         rot=Vector((0.0, 0.0, 1.0)).rotation_difference((b - a).normalized()).to_matrix())


def vki_orc_ladder(k, p0, p1, w=0.5, rung=0.32, dark=VKI_ORC_FRESH):
    """a ladder from its feet p0 to its top p1: square rails, round rungs shut at both ends"""
    p0 = Vector(p0); p1 = Vector(p1)
    ax = p1 - p0; L = ax.length; ax /= L
    side = Vector((1.0, 0.0, 0.0)) if abs(ax.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    side = (side - ax * ax.dot(side)).normalized()
    for s in (-1, 1):
        vki_orc_timber(k, tuple(p0 + side * s * w / 2), tuple(p1 + side * s * w / 2), 0.06, d=0.045, dark=dark, bevel=0.0)
    for i in range(int((L - 0.2) / rung)):
        c = p0 + ax * (0.25 + i * rung)
        vki_orc_cone(k, c - side * (w / 2 + 0.01), side, 0.022, 0.022, w + 0.02, 5, WOOD)


def vki_orc_spike(k, c, h=0.26, r=0.035):
    """an iron spike standing on c"""
    return _cyl(k, (c[0], c[1], c[2] + h / 2), r, 0.004, h, 6, IRON)


def vki_orc_ash_bed(k, c, rx, ry, seed, coals=()):
    """what a fire leaves under a burnt engine: ash mounded low over the ground, coals glowing in it"""
    a = vki_dpr_mound(k, (c[0], c[1], 0.0), rx, ry, 0.12, VKI_ASH, z0=0.001, nr=3, ns=18, seed=seed, wob=0.16, bump=0.22)
    k.set_dark(a, 0.45)
    for i, (x, y, r) in enumerate(coals):
        g = _ico(k, (x, y, 0.1), r, COAL, scale=(1.5, 1.1, 0.5), sub=1, jit=0.02, seed=seed + 10 + i)
        k.project(vki_faces_of(g), COAL)
        vki_sto_embers(k, x, y, 0.11, 5, r * 1.3, r, seed + 20 + i, core=0.2, rmin=0.03, rmax=0.045, hmax=0.5)


def vki_orc_rag(k, top_l, top_r, drop, seed, dark=VKI_ORC_CHAR):
    """a scorched rag of hide hanging from a line (what is left of a hide cover)"""
    tl = Vector(top_l); tr = Vector(top_r)
    return vki_lair_hide(k, [tuple(tl), tuple(tr), tuple(tr - Vector((0.0, 0.0, drop))), tuple(tl - Vector((0.0, 0.0, drop * 0.8)))],
                         dark=dark, seed=seed, nu=2, nv=1, t=0.012, ragged=drop * 0.4, mottle=0.08, edge=0.1)


def vki_orc_ram(k, burnt=False):
    """a covered battering ram (2.9 x 6.2 m, 3.3 high): a chassis of two sills on four solid wheels, posts and a steep
    gabled roof of hides over rafters (the right slope's back half still bare), the front gable a red hide with the
    black tusk, iron spikes along the ridge; the ram -- a bark log with an iron head and two iron tusks -- hangs from the
    ridge on chains, its head out of the front (-Y). burnt: the hides burned off but for rags, the front of the roof
    fallen in with the ridge, the ram down on the chassis, the timber charred, ash and embers under it."""
    rnd = random.Random(61)

    def T(a, b, w, d=None, bevel=0.012, mi=WOOD):
        dk = VKI_ORC_CHAR + rnd.uniform(-0.06, 0.06) if burnt else VKI_ORC_FRESH + rnd.uniform(0.0, 0.1)
        return vki_orc_timber(k, a, b, w, d=d, dark=dk, bevel=bevel, mi=mi)
    wdark = VKI_ORC_CHAR if burnt else 0.08
    ZE, ZR, XE = 1.98, 3.08, 1.22                                        # eaves, ridge, eave line (rafter feet)
    # the chassis: sills, cross beams on them, axles under them, the wheels
    for x in (-1.0, 1.0):
        T((x, -2.45, 0.56), (x, 2.45, 0.56), 0.26, d=0.3)
    for y in (-2.3, -0.78, 0.78, 2.3):
        T((-1.18, y, 0.78), (1.18, y, 0.78), 0.2, d=0.16)
    for y in (-1.55, 1.55):
        T((-1.36, y, 0.5), (1.36, y, 0.5), 0.13, bevel=0.0)
        for x in (-1.27, 1.27):
            vki_orc_wheel(k, (x, y, 0.5), 0.5, 0.16, dark=wdark)
    # posts on the cross beams, wall plates on them
    for y in (-2.3, -0.78, 0.78, 2.3):
        for x in (-0.98, 0.98):
            if burnt and y == -2.3:                                      # the front posts burned through
                top = 1.3 if x < 0 else 1.75
                T((x, y, 0.84), (x * 1.02, y, top), 0.18)
                vki_orc_splinter(k, (x * 1.02, y, top - 0.02), 0.18, 0.3, int(80 + x * 3))
                continue
            T((x, y, 0.84), (x * 1.04, y, ZE + 0.03), 0.18)
    for x in (-1.0, 1.0):
        if burnt and x > 0:                                              # the right plate broke and fell at the front
            T((x * 1.02, -0.62, ZE + 0.07), (x * 1.02, 2.6, ZE + 0.07), 0.18, d=0.16)
            T((x * 1.02 + 0.05, -0.68, ZE - 0.02), (1.62, -2.45, 0.12), 0.18, d=0.16)
            vki_orc_splinter(k, (x * 1.02, -0.6, ZE + 0.07), 0.16, 0.24, 85)
        elif burnt:
            T((x * 1.02, -2.4, ZE + 0.07), (x * 1.02, 2.6, ZE + 0.07), 0.18, d=0.16)
        else:
            T((x * 1.02, -2.6, ZE + 0.07), (x * 1.02, 2.6, ZE + 0.07), 0.18, d=0.16)
    # the ridge and the rafters (five pairs), collar ties on three of them
    ys = (-2.3, -1.15, 0.0, 1.15, 2.3)
    if burnt:
        T((0.0, -0.32, ZR), (0.0, 2.72, ZR), 0.2, d=0.22)
        vki_orc_splinter(k, (0.0, -0.36, ZR), 0.2, 0.26, 86)
        T((0.18, -0.4, ZR - 0.12), (0.62, -2.85, 0.92), 0.2, d=0.22)          # the ridge's front half, fallen in
        for y in ys[2:]:
            for s in (-1, 1):
                if y == 0.0 and s > 0:
                    continue
                T((s * XE, y + 0.016 * (s > 0), ZE), (0.0, y + 0.016 * (s > 0), ZR + 0.03), 0.11, d=0.13)
        for (a, b) in (((-1.65, -1.6, 0.08), (-0.35, -2.95, 0.72)), ((0.9, -1.3, 0.92), (1.95, -2.6, 0.1)),
                       ((-1.25, -0.9, 0.95), (-1.9, 0.2, 0.08))):       # front rafters fallen across the chassis
            T(a, b, 0.11, d=0.13)
    else:
        T((0.0, -2.72, ZR), (0.0, 2.72, ZR), 0.2, d=0.22)
        for y in ys:
            for s in (-1, 1):
                T((s * XE, y + 0.016 * (s > 0), ZE), (0.0, y + 0.016 * (s > 0), ZR + 0.03), 0.11, d=0.13)
    for y in ((0.0, 2.3) if burnt else (-2.3, 0.0, 2.3)):
        T((-0.68, y + 0.07, 2.58), (0.68, y + 0.07, 2.58), 0.1, d=0.12, bevel=0.0)
    # the roof's hides (each slope's front and back halves; the right slope's back half not yet covered)
    rl = math.hypot(XE, ZR - ZE)
    tx, tz = XE / rl, (ZR - ZE) / rl                                     # along a rafter, eave -> ridge (left slope: +x)

    def S(s, y, u, o):
        """a point on slope s (-1 left, +1 right) above the rafters: u 0 eave .. 1 ridge, o off the rafters"""
        return (s * XE * (1 - u) + s * tz * o, y, ZE + (ZR - ZE) * u + tx * o)
    if not burnt:
        for s, y0, y1, o, sd in ((-1, -2.75, 0.08, 0.1, 91), (-1, -0.08, 2.75, 0.125, 92), (1, -2.75, 0.08, 0.1, 93)):
            vki_lair_hide(k, [S(s, y0, 1.0, o), S(s, y1, 1.0, o), S(s, y1, -0.07, o), S(s, y0, -0.07, o)], dark=0.12,
                          seed=sd, nu=3, nv=2, t=0.016, sagv=(-s * tz * 0.04, 0.0, -tx * 0.04), ragged=0.06, mottle=0.08, edge=0.15)
        roll = _cyl(k, (0.55, 1.6, 0.98), 0.17, 0.17, 1.5, 8, HIDE, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
        k.set_dark(roll, 0.2)                                            # the hides still to go on, rolled
        for x in (0.15, 0.95):
            vki_orc_band_on(k, (x - 0.01, 1.6, 0.98), (x + 0.01, 1.6, 0.98), 0.5, 0.165, 0.185, 0.05, mi=BURLAP, segs=8)
        # the front gable: a red-dyed hide with the warlord's sign (a black tusk)
        vki_lair_hide(k, [(-1.1, -2.42, 2.07), (1.1, -2.42, 2.07), (0.08, -2.42, 2.98), (-0.08, -2.42, 2.98)], dark=0.1,
                      seed=94, nu=3, nv=2, t=0.016, ragged=0.0, mottle=0.06, edge=0.12, mi=CLOTH_A)
        vki_orc_crescent(k, (-0.42, 2.18), (0.08, 3.0), (0.42, 2.26), 0.2, -2.437)
    else:
        for (x, y0, y1, drop, sd) in ((-1.1, 0.2, 0.9, 0.5, 95), (-1.1, 1.5, 2.1, 0.38, 96), (1.1, 1.0, 1.5, 0.44, 97)):
            vki_orc_rag(k, (x, y0, ZE + 0.05), (x, y1, ZE + 0.05), drop, sd)
    # the ridge's spikes
    for y in ((0.0, 1.2, 2.4) if burnt else (-2.4, -1.2, 0.0, 1.2, 2.4)):
        vki_orc_spike(k, (0.0, y, ZR + 0.1))
    # the ram: a bark log hung on two chains, its iron head and tusks out of the front
    zh = 1.4
    a, b = ((0.06, 2.75, zh - 0.08), (0.28, -2.7, 0.62)) if burnt else ((0.0, 2.75, zh + 0.03), (0.0, -2.9, zh))
    log = vki_lair_log(k, a, b, 0.19, 70, segs=10, bend=0.012, ts=(0.0, 0.33, 0.66, 1.0))
    k.set_dark(log, VKI_ORC_CHAR if burnt else 0.05)
    A, B = Vector(a), Vector(b)
    d = (B - A).normalized()
    side = d.cross(Vector((0.0, 0.0, 1.0))).normalized()
    vki_orc_cone(k, B - d * 0.08, d, 0.21, 0.05, 0.5, 10, IRON)
    for s in (-1, 1):
        vki_orc_tusk(k, tuple(B + d * 0.06 + side * s * 0.14), tuple(d * 0.85 + side * s * 0.35), (0, 0, 1), 0.36, 0.045,
                     100 + s, mi=IRON)
    for t in (0.06, 0.4, 0.86):
        vki_orc_band_on(k, b, a, t, 0.165, 0.215, 0.09)
    for y, t in ((-1.25, 0.3), (1.25, 0.75)):
        if burnt and y < 0:
            continue                                                     # the front chain went with the ridge
        p = A.lerp(B, 1 - t)
        vki_dpr_chain(k, (p.x, p.y, ZR - 0.12), (p.x, p.y, p.z + 0.22), 9 if not burnt else 11, sag=0.0, link=0.11, w=0.045, t=0.014)
        sl = vki_orc_band_on(k, b, a, t, 0.18, 0.24, 0.1, mi=BURLAP)
        if burnt:
            k.set_dark(sl[0] if isinstance(sl, tuple) else sl, VKI_ORC_CHAR)
    if burnt:
        vki_orc_ash_bed(k, (0.0, -0.4), 2.0, 3.2, 110, coals=((0.5, -1.6, 0.13), (-0.6, 0.9, 0.1), (0.2, 1.9, 0.09)))
        k.slot_mats[WOOD] = "Dark"
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_note="outdoors (the burnt march's siege yard): the ram's head points -Y" +
                           ("; burnt (the RPG swaps it in for the fresh one)" if burnt else ""))


def vki_orc_ram_burnt(k):
    vki_orc_ram(k, burnt=True)


def vki_orc_tower(k, burnt=False):
    """a siege tower half built (3.9 x 3.6 m base, the gin pole out to +X; corner posts to 7.3 m; when done three
    storeys and a fighting top): a chassis on four solid wheels, four corner posts leaning in, girts at each floor, the
    first storey boarded on the front (-Y) and sides and the front hung with hides (the black tusk on them), the second
    storey's front half boarded and its floor half laid, the back (+Y) open on cross braces and two ladders, a gin pole
    at the back corner hoisting a beam. burnt: the posts burned through at 2-4 m, the boards burned short, the upper
    girts and the gin pole fallen round it, ash and embers."""
    rnd = random.Random(71)

    def T(a, b, w, d=None, bevel=0.012, mi=WOOD, dark=None):
        dk = dark if dark is not None else (VKI_ORC_CHAR + rnd.uniform(-0.06, 0.06) if burnt else VKI_ORC_FRESH + rnd.uniform(0.0, 0.1))
        return vki_orc_timber(k, a, b, w, d=d, dark=dk, bevel=bevel, mi=mi)
    wdark = VKI_ORC_CHAR if burnt else 0.08
    Z0, ZT, P0, PT = 0.95, 7.3, 1.45, 1.22
    Z1, Z2, Z3 = 1.03, 3.4, 5.8                                          # the floors

    def pxy(z):                                                          # the corner posts' offset at height z
        return P0 - (P0 - PT) * (z - Z0) / (ZT - Z0)
    lean = math.atan((P0 - PT) / (ZT - Z0))
    # chassis: sills along Y, cross sills along X on them, axles, wheels
    for x in (-1.55, 1.55):
        T((x, -1.75, 0.62), (x, 1.75, 0.62), 0.26, d=0.3)
    for y in (-1.6, 1.6):
        T((-1.62, y, 0.86), (1.62, y, 0.86), 0.24, d=0.2)
    for y in (-1.05, 1.05):
        T((-1.95, y, 0.55), (1.95, y, 0.55), 0.13, bevel=0.0)
        for x in (-1.84, 1.84):
            vki_orc_wheel(k, (x, y, 0.55), 0.55, 0.18, dark=wdark)
    for i in range(10):                                                  # the base deck, along Y
        x = -1.3 + i * 0.29
        T((x, -1.72, 0.995), (x, 1.72, 0.995), 0.27, d=0.05, bevel=0.0)
    # the corner posts (snapped when burnt)
    snaps = {(-1, -1): 3.6, (1, -1): 2.4, (-1, 1): 4.1, (1, 1): 1.9}
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = snaps[(sx, sy)] if burnt else ZT
            T((sx * P0, sy * P0, Z0 - 0.05), (sx * pxy(top), sy * pxy(top), top), 0.24)
            if burnt:
                vki_orc_splinter(k, (sx * pxy(top), sy * pxy(top), top - 0.02), 0.24, 0.36, int(120 + sx * 3 + sy))
            else:
                vki_orc_spike(k, (sx * pxy(ZT), sy * pxy(ZT), ZT - 0.02), h=0.3, r=0.045)
    # girts round the floors: the second floor's on all four faces, the third's on the front and the left only
    def girt(z, face):
        p = pxy(z) + 0.02
        ends = {"front": ((-p - 0.17, -p, z), (p + 0.17, -p, z)), "back": ((-p - 0.17, p, z), (p + 0.17, p, z)),
                "left": ((-p, -p - 0.13, z + 0.1), (-p, p + 0.13, z + 0.1)), "right": ((p, -p - 0.13, z + 0.1), (p, p + 0.13, z + 0.1))}[face]
        T(ends[0], ends[1], 0.2, d=0.22)
    for f in ("front", "back", "left", "right"):
        if not burnt or f in ("front", "left"):
            girt(Z2, f)
    if not burnt:
        girt(Z3, "front"); girt(Z3, "left")
    # mid posts on the front and the sides, up to the second floor's girt
    for (x, y) in ((0.0, -1), (-1, 0.0), (1, 0.0)):
        top = Z2 if burnt else Z3 - 0.1
        if x in (-1, 1):
            T((x * P0, 0.0, Z0), (x * pxy(top), 0.0, top), 0.18)
        else:
            T((0.0, y * P0, Z0), (0.0, y * pxy(top), top), 0.18)
    # boards: the first storey's front and sides, the second storey's front half up
    def boards(face, z0, z1, n, seed):
        rb = random.Random(seed)
        for i in range(n):
            t = -1.0 + (2 * i + 1) / n
            zz1 = z1
            if burnt:
                if rb.random() < 0.35:
                    continue
                zz1 = z0 + (z1 - z0) * rb.uniform(0.25, 0.8)
            zm = (z0 + zz1) / 2
            p = pxy(zm) + 0.15
            h = zz1 - z0
            dk = VKI_ORC_CHAR + rb.uniform(-0.05, 0.08) if burnt else VKI_ORC_FRESH + rb.uniform(0.0, 0.12)
            if face in ("front", "back"):
                s = -1 if face == "front" else 1
                vs = k.box((t * (p - 0.05), s * p, zm), (2 * (p - 0.05) / n - 0.012, 0.045, h), WOOD,
                           rot=(s * lean, 0.0, 0.0), bevel=0.0, jitter=0.004, seed=seed + i)
            else:
                s = -1 if face == "left" else 1
                vs = k.box((s * p, t * (p - 0.05), zm), (0.045, 2 * (p - 0.05) / n - 0.012, h), WOOD,
                           rot=(0.0, -s * lean, 0.0), bevel=0.0, jitter=0.004, seed=seed + i)
            k.set_dark(list(set(vs)), dk)
            if burnt and zz1 < z1 - 0.2:
                vki_orc_splinter(k, (t * (p - 0.05) if face in ("front", "back") else s * p,
                                     s * p if face in ("front", "back") else t * (p - 0.05), zz1), 0.1, 0.16, seed + 50 + i, n=3)
    boards("front", Z1 + 0.04, Z2 - 0.12, 11, 200)
    boards("left", Z1 + 0.04, Z2 - 0.12, 11, 220)
    boards("right", Z1 + 0.04, Z2 - 0.12, 11, 240)
    if not burnt:
        boards("front", Z2 + 0.12, Z2 + 1.25, 11, 260)
        # hides hung from the second floor's girt over the front boards, the black tusk on them
        yf = -(pxy(Z2) + 0.24)
        for (x0, x1, sd, dy) in ((-1.55, 0.08, 270, 0.0), (-0.08, 1.55, 271, -0.03)):
            vki_lair_hide(k, [(x0, yf + dy, Z2 + 0.05), (x1, yf + dy, Z2 + 0.05), (x1, yf + dy - 0.03, Z1 + 0.25),
                              (x0, yf + dy - 0.03, Z1 + 0.25)], dark=0.14, seed=sd, nu=3, nv=3, t=0.016, ragged=0.08,
                          mottle=0.08, edge=0.14)
        vki_orc_crescent(k, (-0.7, 1.75), (0.02, 3.25), (0.62, 1.95), 0.36, yf - 0.085)
        # the second floor, half laid (planks along Y on the girts), and the cross braces on the open back
        for i in range(6):
            x = -1.15 + i * 0.27
            T((x, -pxy(Z2) - 0.05, Z2 + 0.13), (x, pxy(Z2) + 0.05, Z2 + 0.13), 0.25, d=0.05, bevel=0.0)
        for (z0, z1) in ((Z1 + 0.1, Z2 - 0.1), (Z2 + 0.1, Z3 - 0.2)):
            p0, p1 = pxy(z0) - 0.02, pxy(z1) - 0.02
            T((-p0, p0 + 0.12, z0), (p1, p1 + 0.12, z1), 0.12, d=0.1, bevel=0.0)
            T((p0, p0 + 0.16, z0), (-p1, p1 + 0.16, z1), 0.12, d=0.1, bevel=0.0)
        for (z0, z1, s) in ((Z2 + 0.1, Z3 - 0.2, -1), (Z2 + 0.1, Z3 - 0.2, 1)):     # one brace on each side's second storey
            p0, p1 = pxy(z0), pxy(z1)
            T((s * (p0 + 0.13), -p0 + 0.1, z0), (s * (p1 + 0.13), p1 - 0.1, z1), 0.1, d=0.12, bevel=0.0)
        # ladders inside, by the open back
        vki_orc_ladder(k, (-0.75, 0.6, Z1 + 0.03), (-0.75, 1.02, Z2 + 0.15))
        vki_orc_ladder(k, (0.8, 0.55, Z2 + 0.17), (0.8, 0.98, Z3 + 0.1))
        # the gin pole at the back right corner, a beam on its rope
        g0, g1 = Vector((1.38, 1.38, Z2 + 0.2)), Vector((2.55, 2.05, 8.1))
        gp = vki_lair_log(k, tuple(g0), tuple(g1), 0.1, 280, segs=8, bend=0.01)
        k.set_dark(gp, 0.06)
        for z in (Z2 + 0.6, Z3 - 0.3):                                 # lashed to the post
            vki_orc_band_on(k, g0, g1, (z - g0.z) / (g1.z - g0.z), 0.085, 0.13, 0.14, mi=BURLAP, segs=8)
        k.box((g1.x, g1.y, g1.z - 0.18), (0.14, 0.1, 0.24), WOOD, bevel=0.01)                     # the block
        def_rope(k, (g1.x, g1.y, g1.z - 0.28), (2.5, 2.0, 6.62), r=0.022, n=1)
        def_rope(k, (g1.x - 0.05, g1.y, g1.z - 0.28), (1.62, 1.68, 0.95), r=0.022, sag=0.12, n=6)
        T((2.5, 0.75, 6.5), (2.5, 3.25, 6.5), 0.22, d=0.2)                                     # the beam going up
        for y in (1.7, 2.3):
            def_rope(k, (2.5, 2.0, 6.62), (2.5, y, 6.63), r=0.02, n=1)
    else:
        # what fell: the upper girts and posts round the base, the gin pole across the ground
        for (a, b, w) in (((-2.4, -1.0, 0.12), (-0.6, -2.7, 0.2), 0.2), ((1.6, -2.3, 0.1), (2.7, 0.4, 0.14), 0.2),
                          ((-1.9, 1.6, 1.15), (0.4, 2.9, 0.1), 0.22), ((2.2, 1.6, 0.12), (0.6, 3.1, 0.25), 0.2),
                          ((-2.7, 0.3, 0.1), (-2.1, 2.6, 0.12), 0.24)):
            T(a, b, w, d=w * 1.05)
        gp = vki_lair_log(k, (1.9, 1.7, 0.14), (3.4, 4.2, 0.1), 0.1, 281, segs=8, bend=0.01)
        k.set_dark(gp, VKI_ORC_CHAR)
        vki_orc_rag(k, (-1.55, -1.62, Z2 - 0.05), (-0.9, -1.62, Z2 - 0.05), 0.55, 290)
        vki_orc_ash_bed(k, (0.1, 0.1), 2.5, 2.5, 300, coals=((-0.8, -0.6, 0.14), (0.9, 0.5, 0.12), (0.2, 1.4, 0.1)))
        k.slot_mats[WOOD] = "Dark"
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_note="outdoors (the siege yard): the front (-Y) is hung with hides, the back open" +
                           ("; burnt" if burnt else ""))


def vki_orc_tower_burnt(k):
    vki_orc_tower(k, burnt=True)


def vki_orc_catapult(k, burnt=False):
    """a throwing engine (an onager, 2.3 x 4.6 m, 1.9 high): a frame of two side beams on four low solid wheels, a skein
    of twisted rope across its middle in iron washers, the arm drawn back (+Y) with a stone in its cup, the padded stop
    on an A-frame braced to the front (-Y, the way it throws), a windlass at the back, stones stacked beside it.
    burnt: the skein burned away (the washers left), the arm snapped and fallen, the stop down, charred, ash."""
    rnd = random.Random(81)

    def T(a, b, w, d=None, bevel=0.012, mi=WOOD):
        dk = VKI_ORC_CHAR + rnd.uniform(-0.06, 0.06) if burnt else VKI_ORC_FRESH + rnd.uniform(0.0, 0.1)
        return vki_orc_timber(k, a, b, w, d=d, dark=dk, bevel=bevel, mi=mi)
    wdark = VKI_ORC_CHAR if burnt else 0.08
    XS, ZS = 0.72, 0.5                                                   # the side beams
    for x in (-XS, XS):
        T((x, -2.05, ZS), (x, 2.05, ZS), 0.24, d=0.28)
    for y in (-1.85, 1.85):
        T((-0.95, y, ZS + 0.2), (0.95, y, ZS + 0.2), 0.2, d=0.16)
    for y in (-1.35, 1.35):
        T((-1.1, y, 0.34), (1.1, y, 0.34), 0.11, bevel=0.0)
        for x in (-1.0, 1.0):
            vki_orc_wheel(k, (x, y, 0.34), 0.34, 0.15, dark=wdark)
    # the skein across the middle, iron washers outside the beams, their levers
    ysk, zsk = 0.25, ZS + 0.02
    R = Matrix.Rotation(math.pi / 2, 4, "Y")
    if not burnt:
        sk = _cyl(k, (0.0, ysk, zsk), 0.2, 0.2, 1.3, 10, BURLAP, rot=R)
        k.set_dark(sk, 0.1)
    for s in (-1, 1):
        _cyl(k, (s * (XS + 0.17), ysk, zsk), 0.24, 0.24, 0.07, 12, IRON, rot=R)
        lv = T((s * (XS + 0.24), ysk - 0.45, zsk + 0.1), (s * (XS + 0.24), ysk + 0.45, zsk - 0.1), 0.06, d=0.05, mi=IRON, bevel=0.0)
    # the arm, drawn back, its cup and stone (burnt: snapped, its two halves down)
    a0 = Vector((0.0, ysk, zsk))
    if not burnt:
        a1 = Vector((0.0, 2.05, 0.95))
        T(tuple(a0), tuple(a1), 0.17, d=0.2)
        for t in (0.15, 0.55):
            vki_orc_band_on(k, a0, a1, t, 0.1, 0.13, 0.07, segs=8)
        cup, _ = vki_home_lathe(k, [(0.05, 0.0), (0.2, 0.06), (0.25, 0.18), (0.22, 0.2), (0.1, 0.08)], c=(0.0, 2.1, 1.03),
                                segs=10, mi=WOOD, smooth=True, closed=False)
        st = _ico(k, (0.0, 2.1, 1.25), 0.16, VKI_STONE_BLOCK_IN, sub=1, jit=0.01, seed=88)
        k.project(vki_faces_of(st), VKI_STONE_BLOCK_IN)
        k.set_dark(st, 0.32)
        def_rope(k, (0.0, 2.38, 0.95), (0.0, 1.85, 0.98), r=0.022, n=1)
    else:
        T(tuple(a0), (0.15, 1.05, 0.88), 0.17, d=0.2)
        vki_orc_splinter(k, (0.15, 1.08, 0.88), 0.17, 0.26, 89)
        T((0.6, 1.4, 0.12), (1.6, 2.6, 0.1), 0.17, d=0.2)                     # its far half, on the ground
    # the stop: an A-frame, its padded crossbar, struts to the front
    zt = 1.78
    if not burnt:
        for s in (-1, 1):
            T((s * XS, -0.42, ZS + 0.1), (s * (XS - 0.1), -0.48, zt), 0.16)
            T((s * (XS - 0.08), -0.5, zt - 0.1), (s * XS, -1.95, ZS + 0.1), 0.13, bevel=0.0)
            vki_orc_spike(k, (s * (XS + 0.06), -0.48, zt + 0.08), h=0.24)
        T((-XS - 0.06, -0.48, zt), (XS + 0.06, -0.48, zt), 0.16, d=0.18)
        pad = k.box((0.0, -0.33, zt - 0.02), (0.95, 0.16, 0.3), BURLAP, bevel=0.04, jitter=0.01, seed=90)
        k.set_dark(list(set(pad)), 0.08)
        vki_orc_crescent(k, (-0.24, zt - 0.08), (0.02, zt + 0.12), (0.22, zt - 0.06), 0.06, -0.43, n=10)
    else:
        T((-XS, -0.42, ZS + 0.1), (-XS + 0.1, -0.48, 1.2), 0.16)
        vki_orc_splinter(k, (-XS + 0.1, -0.48, 1.2), 0.16, 0.22, 91)
        T((XS - 0.1, -0.5, 0.15), (-0.5, -2.2, 0.1), 0.16)               # the other leg and the bar, fallen forward
        T((-1.2, -1.5, 0.08), (0.75, -1.15, 0.65), 0.16, d=0.18)
    # the windlass at the back
    for s in (-1, 1):
        T((s * 0.45, 1.95, ZS + 0.25), (s * 0.45, 1.95, 1.05 if not burnt else 0.8), 0.12)
    if not burnt:
        _cyl(k, (0.0, 1.95, 0.95), 0.1, 0.1, 0.84, 8, WOOD, rot=R)
        for s in (-1, 1):
            for a in (math.pi / 4, 3 * math.pi / 4):
                x = s * (0.52 if a < 1.0 else 0.555)
                vki_dpr_rod(k, (x, 1.95 - 0.28 * math.cos(a), 0.95 - 0.28 * math.sin(a)),
                            (x, 1.95 + 0.28 * math.cos(a), 0.95 + 0.28 * math.sin(a)), 0.04, WOOD)
    # stones stacked by its right side (ready to throw)
    for i, (x, y, z, r) in enumerate(((1.42, -1.75, 0.17, 0.17), (1.5, -1.38, 0.17, 0.17), (1.28, -1.1, 0.16, 0.16),
                                      (1.42, -1.45, 0.43, 0.16))):
        st = _ico(k, (x, y, z), r, VKI_STONE_BLOCK_IN, sub=1, jit=0.012, seed=130 + i)
        k.project(vki_faces_of(st), VKI_STONE_BLOCK_IN)
        k.set_dark(st, 0.45 if burnt else 0.32)
    if burnt:
        vki_orc_ash_bed(k, (0.0, 0.0), 1.5, 2.6, 140, coals=((0.2, 0.3, 0.13), (-0.4, -1.0, 0.1)))
        k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_note="outdoors (the siege yard): it throws toward -Y" + ("; burnt" if burnt else ""))


def vki_orc_catapult_burnt(k):
    vki_orc_catapult(k, burnt=True)


def vki_orc_cage(k, open_=False):
    """the orcs' prisoner cage (2.7 x 1.9 m, 2.6 high to its spikes; room for three standing): a frame of squared posts
    and rails, round bars all round 0.24 apart, poles across the top, iron straps, an iron spike on each post; the door
    in the front (-Y) hung on iron hinges, chained shut with a padlock; straw inside. open_: the door swung out, the
    chain hanging from the post, the lock on the ground."""
    rnd = random.Random(141)
    X, Y, ZT = 1.25, 0.85, 2.3
    for sx in (-1, 1):
        for sy in (-1, 1):
            vki_orc_timber(k, (sx * X, sy * Y, -0.05), (sx * X, sy * Y, ZT + 0.12), 0.2, dark=0.25)
            vki_orc_spike(k, (sx * X, sy * Y, ZT + 0.1), h=0.22, r=0.05)
    for sy in (-1, 1):                                                   # rails along X (the long faces)
        for z in (0.14, ZT):
            vki_orc_timber(k, (-X, sy * Y, z), (X, sy * Y, z), 0.14, d=0.12, dark=0.25, bevel=0.0)
    for sx in (-1, 1):                                                   # rails along Y, 2 cm higher (they cross the others)
        for z in (0.16, ZT + 0.02):
            vki_orc_timber(k, (sx * X, -Y, z), (sx * X, Y, z), 0.14, d=0.12, dark=0.25, bevel=0.0)
    XD = 0.47                                                            # the door's posts

    def bar(x, y, z0=0.03, z1=ZT + 0.04):
        vs = _cyl(k, (x, y, (z0 + z1) / 2), 0.045, 0.04, z1 - z0, 5, BARK_OAK)
        k.set_dark(vs, 0.2 + rnd.uniform(0, 0.15))
    for i in range(10):                                                  # back bars
        bar(-X + (i + 1) * 2 * X / 11, Y)
    for x in (-1.0, -0.76, 0.76, 1.0):                                    # front bars beside the door
        bar(x, -Y)
    for sx in (-1, 1):
        for i in range(6):
            bar(sx * X, -Y + (i + 1) * 2 * Y / 7)
    for x in (-XD, XD):
        vki_orc_timber(k, (x, -Y, 0.1), (x, -Y, ZT + 0.03), 0.12, dark=0.25, bevel=0.0)
    for x in (-0.78, -0.26, 0.26, 0.78):                                 # poles across the top
        vs = _cyl(k, (x, 0.0, ZT + 0.12), 0.05, 0.05, 2 * Y + 0.2, 5, BARK_OAK, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
        k.set_dark(vs, 0.25)
    for z in (0.95, 1.72):                                               # iron straps round three sides
        k.box((0.0, Y + 0.075, z), (2 * X, 0.012, 0.06), IRON, bevel=0.0)
        for sx in (-1, 1):
            k.box((sx * (X + 0.075), 0.0, z + 0.02), (0.012, 2 * Y, 0.06), IRON, bevel=0.0)
        for x0, x1 in ((-X, -XD - 0.06), (XD + 0.06, X)):
            k.box(((x0 + x1) / 2, -Y - 0.075, z), (x1 - x0, 0.012, 0.06), IRON, bevel=0.0)
    # the door: a frame of its own with three bars, hinged on the left post; open, it swings out 110 degrees
    before = set(k.bm.verts)
    yd = -Y - 0.1
    for x in (-XD + 0.07, XD - 0.07):
        vki_orc_timber(k, (x, yd, 0.12), (x, yd, ZT - 0.08), 0.09, dark=0.3, bevel=0.0)
    for z in (0.22, 1.2, ZT - 0.14):
        vki_orc_timber(k, (-XD + 0.03, yd, z), (XD - 0.03, yd, z), 0.072, d=0.1, dark=0.3, bevel=0.0)
    for x in (-0.18, 0.0, 0.18):
        bar(x, yd, 0.2, ZT - 0.12)
    for z in (0.4, ZT - 0.35):                                           # the hinges
        k.box((-XD + 0.02, yd - 0.055, z), (0.16, 0.012, 0.07), IRON, bevel=0.0)
    door = [v for v in k.bm.verts if v not in before]
    if open_:
        bmesh.ops.rotate(k.bm, cent=(-XD, -Y - 0.1, 0.0), matrix=Matrix.Rotation(math.radians(-110), 3, "Z"), verts=door)
        vki_dpr_chain(k, (XD + 0.07, -Y - 0.09, 1.25), (XD + 0.07, -Y - 0.09, 0.3), 9, sag=0.0)
        k.box((XD + 0.3, -Y - 0.32, 0.05), (0.09, 0.05, 0.1), IRON, rot=(math.pi / 2, 0.0, 0.6), bevel=0.01)
    else:
        vki_dpr_chain(k, (XD - 0.1, -Y - 0.17, 1.24), (XD + 0.12, -Y - 0.11, 1.18), 4, sag=0.0)
        vki_dpr_chain(k, (XD - 0.1, -Y - 0.17, 1.12), (XD + 0.12, -Y - 0.11, 1.08), 4, sag=0.0)
        k.box((XD + 0.06, -Y - 0.21, 1.0), (0.09, 0.05, 0.11), IRON, bevel=0.01)              # the padlock
        vki_home_hoop(k, (XD + 0.06, -Y - 0.21, 1.08), 0.022, 0.034, 0.016, segs=8, mi=IRON,
                      rot=Matrix.Rotation(math.pi / 2, 3, "X"))
    st = vki_dpr_mound(k, (0.2, 0.15, 0.0), 0.95, 0.55, 0.06, VKI_STRAW, z0=0.001, nr=2, ns=12, seed=143, wob=0.2)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -1.5, 0]], vki_nav="block", vki_see_through=1,
                  vki_note="outdoors: the door is in the -Y face" + ("; open" if open_ else "; the RPG puts its prisoners inside"))


def vki_orc_cage_open(k):
    vki_orc_cage(k, open_=True)


def vki_orc_wardrum(k):
    """the war drum (1.6 x 1.3 m, 1.7 high): a great drum, its hide head tipped toward the drummer (-Y), red-dyed shell
    with the black tusk, laced head to head, on a timber cradle; orc skulls on the two front posts, two thigh-bone
    beaters across the front rail"""
    tilt = Matrix.Rotation(math.radians(22), 4, "X")                     # its top head turned toward -Y
    c = Vector((0.0, 0.08, 0.98))
    ax = (tilt @ Vector((0.0, 0.0, 1.0))).normalized()
    sh = _cyl(k, tuple(c), 0.5, 0.55, 0.72, 16, CLOTH_A, rot=tilt)
    k.set_dark(sh, 0.12)
    for t, mi, r in ((0.37, HIDE, 0.575), (-0.37, HIDE, 0.525)):         # the heads, a little proud of the shell
        hd = _cyl(k, tuple(c + ax * t), r, r, 0.03, 16, mi, rot=tilt)
        k.set_dark(hd, 0.05 if t > 0 else 0.2)
    side = Vector((1.0, 0.0, 0.0)); fwd = ax.cross(side).normalized()
    for i in range(12):                                                  # lacing, zigzag head to head
        a0 = 2 * math.pi * i / 12; a1 = 2 * math.pi * (i + 0.5) / 12
        p0 = c + ax * 0.36 + (side * math.cos(a0) + fwd * math.sin(a0)) * 0.575
        p1 = c - ax * 0.36 + (side * math.cos(a1) + fwd * math.sin(a1)) * 0.53
        vki_dpr_rod(k, tuple(p0), tuple(p1), 0.02, BURLAP)
    # the black tusk painted on the top head (seen from the camera, above the drummer)
    U = Vector((1.0, 0.0, 0.0)); V = ax.cross(U).normalized()
    vki_orc_crescent3(k, c + ax * 0.391, U, V, (-0.22, -0.18), (0.05, 0.38), (0.24, -0.12), 0.11)
    # the cradle: four posts, rails, cross pieces under the drum
    for sx in (-1, 1):
        for sy, h in ((-1, 1.05), (1, 0.9)):
            vki_orc_timber(k, (sx * 0.62, sy * 0.5, -0.03), (sx * 0.6, sy * 0.48, h), 0.13, dark=0.2)
        vki_orc_timber(k, (sx * 0.6, -0.62, 0.62), (sx * 0.6, 0.62, 0.55), 0.1, dark=0.22, bevel=0.0)
    for y, z in ((-0.5, 0.42), (0.5, 0.38)):
        vki_orc_timber(k, (-0.7, y, z), (0.7, y, z), 0.1, dark=0.22, bevel=0.0)
    vki_orc_timber(k, (-0.75, -0.62, 0.8), (0.75, -0.62, 0.8), 0.09, dark=0.22, bevel=0.0)  # the front rail
    for sx in (-1, 1):                                                   # skulls on the front posts, tusks from their jaws
        vki_dun_skull(k, (sx * 0.6, -0.5, 1.15), s=1.25, yaw=0, pitch=-6)
        for s in (-1, 1):
            vki_orc_tusk(k, (sx * 0.6 + s * 0.04, -0.6, 1.08), (s * 0.12, -0.35, 0.6), (0, 0, 1), 0.08, 0.016, 150 + s)
    for i, x in enumerate((-0.2, 0.18)):                                 # the beaters: thigh bones laid on the rail
        b0 = Vector((x - 0.12, -0.7, 0.86)); b1 = Vector((x + 0.2, -0.55, 0.88))
        vki_dpr_rod(k, tuple(b0), tuple(b1), 0.04, VKI_WAX)
        for p in (b0, b1):
            _ico(k, tuple(p), 0.045, VKI_WAX, scale=(1.0, 1.0, 0.8), sub=1, seed=160 + i)
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.95, 0]], vki_nav="block",
                  vki_note="the drummer stands at -Y (the RPG's war drummer)")


def vki_orc_beartrap(k, sprung=False):
    """a bear trap set in the path (0.75 x 0.45 m): a cross of iron bars, the pan in the middle, two toothed jaws lying
    open, a leaf spring at each end, a chain to an iron stake. sprung: the jaws shut, standing up."""
    k.box((0.0, 0.0, 0.012), (0.62, 0.05, 0.022), IRON, bevel=0.0)
    k.box((0.0, 0.0, 0.016), (0.05, 0.3, 0.022), IRON, bevel=0.0)
    _cyl(k, (0.0, 0.0, 0.036), 0.075, 0.075, 0.014, 8, IRON)
    R = 0.2
    for s in (-1, 1):                                                    # each jaw: a half ring of 6 links, teeth on it
        before = set(k.bm.verts)
        pts = [(math.cos(math.pi * i / 6) * R, s * math.sin(math.pi * i / 6) * R * 0.95) for i in range(7)]
        for i, ((x0, y0), (x1, y1)) in enumerate(zip(pts[:-1], pts[1:])):
            z = 0.02 + 0.004 * (i % 2) + (0.0015 if s > 0 else 0.0)
            vki_dpr_rod(k, (x0, y0, z), (x1, y1, z), 0.03, IRON, d=0.024)
        for i in range(1, 6):
            a = math.pi * (i + 0.5) / 6 if i < 5 else math.pi * 5.2 / 6
            x, y = math.cos(math.pi * i / 6) * R * 0.97, s * math.sin(math.pi * i / 6) * R * 0.92
            _cyl(k, (x, y, 0.06), 0.016, 0.0, 0.06, 4, IRON)
        jaw = [v for v in k.bm.verts if v not in before]
        if sprung:                                                       # turned up about the X axis to stand closed
            bmesh.ops.rotate(k.bm, cent=(0.0, 0.0, 0.02), matrix=Matrix.Rotation(-s * math.radians(84), 3, "X"), verts=jaw)
    for s in (-1, 1):                                                    # the springs
        vki_dpr_rod(k, (s * 0.28, -0.05, 0.03), (s * 0.4, 0.0, 0.06 if not sprung else 0.035), 0.035, IRON, d=0.014)
        vki_dpr_rod(k, (s * 0.28, 0.05, 0.03), (s * 0.4, 0.0, 0.06 if not sprung else 0.035), 0.035, IRON, d=0.014)
    vki_dpr_chain(k, (0.42, 0.02, 0.03), (0.6, 0.08, 0.03), 3, sag=0.0, link=0.07, w=0.03, t=0.01)
    _cyl(k, (0.64, 0.1, 0.05), 0.022, 0.0, 0.12, 5, IRON)
    k.set_dark(list(k.bm.verts), 0.15)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_note="walked over: the RPG springs it on whoever steps in it" + ("; sprung" if sprung else "; set (it glints)"))


def vki_orc_beartrap_sprung(k):
    vki_orc_beartrap(k, sprung=True)


def vki_orc_totem(k):
    """the war-shaman's totem (3.4 m): a carved pole in a cairn, banded red and black, three skulls up it (an orc's,
    tusked, at the bottom; a great beast's skull with horns at the top), a crossbar hung with hide strips and tusks on
    cords, a round hide shield with the black tusk nailed to its front (-Y), an iron spike on top"""
    rnd = random.Random(171)
    for i in range(6):
        a = 2 * math.pi * i / 6 + rnd.uniform(-0.2, 0.2)
        vki_orc_stone(k, (math.cos(a) * 0.3, math.sin(a) * 0.3, 0.1), rnd.uniform(0.15, 0.2), 400 + i, dark=0.25)
    vki_orc_stone(k, (0.0, 0.05, 0.28), 0.13, 410, dark=0.3)
    pole = vki_lair_log(k, (0.0, 0.03, -0.05), (0.0, 0.03, 3.05), 0.11, 420, segs=8, bend=0.015)
    k.set_dark(pole, 0.35)
    for i, (z, mi) in enumerate(((0.75, CLOTH_A), (0.86, VOID), (1.95, CLOTH_A), (2.06, VOID), (2.75, CLOTH_A))):
        vki_home_hoop(k, (0.0, 0.03, z), 0.1, 0.128, 0.08, segs=8, mi=mi)
    vki_dun_skull(k, (0.0, -0.08, 1.15), s=1.35, yaw=0, pitch=-5)
    for s in (-1, 1):
        vki_orc_tusk(k, (s * 0.045, -0.17, 1.06), (s * 0.15, -0.35, 0.6), (0, 0, 1), 0.1, 0.018, 430 + s, n=5, segs=6)
    vki_dun_skull(k, (0.0, -0.06, 1.58), s=1.1, yaw=10, pitch=8)
    # the beast's skull at the top, horns curving up and out
    vki_dun_skull(k, (0.0, -0.1, 3.0), s=2.1, yaw=0, pitch=-12)
    for s in (-1, 1):
        vki_orc_tusk(k, (s * 0.12, -0.05, 3.12), (s * 1.0, 0.1, 0.5), (0, 0, 1), 0.55, 0.06, 440 + s, curve=0.5)
    vki_orc_spike(k, (0.0, 0.03, 3.26), h=0.32, r=0.04)
    # the crossbar, its hide strips and trophies
    vki_dpr_rod(k, (-0.65, -0.02, 2.48), (0.66, -0.02, 2.45), 0.07, WOOD)
    for i, x in enumerate((-0.58, -0.3, 0.32, 0.6)):
        vki_lair_hide(k, [(x - 0.07, -0.07, 2.42), (x + 0.07, -0.07, 2.42), (x + 0.06, -0.08, 1.75 + rnd.uniform(-0.1, 0.15)),
                          (x - 0.06, -0.08, 1.8 + rnd.uniform(-0.1, 0.1))], dark=0.25, seed=450 + i, nu=1, nv=2, t=0.01,
                      ragged=0.08, mottle=0.08, edge=0.1)
    for s in (-1, 1):
        x = s * 0.45
        vki_dpr_rod(k, (x, -0.05, 2.43), (x, -0.05, 2.15), 0.012, BURLAP)
        vki_orc_tusk(k, (x, -0.05, 2.15), (s * 0.1, -0.1, -1.0), (s, 0, 0), 0.24, 0.028, 460 + s, n=5, segs=6)
    # the shield on the front, the black tusk on it
    sh = _cyl(k, (0.0, -0.17, 0.42), 0.32, 0.32, 0.04, 12, HIDE, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    k.set_dark(sh, 0.12)
    vki_home_hoop(k, (0.0, -0.17, 0.42), 0.3, 0.335, 0.05, segs=12, mi=IRON, rot=Matrix.Rotation(math.pi / 2, 3, "X"))
    vki_orc_crescent(k, (-0.16, 0.3), (0.0, 0.62), (0.15, 0.32), 0.07, -0.197, n=10)
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_lair_hide_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_note="3.4 m: the shield with the black tusk faces -Y (the RPG's war-shaman keeps a ring of them)")


# ---------------------------------------------------------------- specs
VKI_ORC_SPECS = [
    ("SM_VKI_Prop_Ruin_Farmhouse_Burnt", vki_orc_farmhouse_ruin, "none"),
    ("SM_VKI_Prop_BurntTree_A", vki_orc_tree_a, "none"),
    ("SM_VKI_Prop_BurntTree_B", vki_orc_tree_b, "none"),
    ("SM_VKI_Prop_BurntStump", vki_orc_stump, "none"),
    ("SM_VKI_Overlay_Ash", vki_orc_ash, "none"),
    ("SM_VKI_Overlay_Tracks_Orc", vki_orc_tracks, "none"),
    ("SM_VKI_Prop_Orc_WarTable", vki_orc_wartable, "prop"),
    ("SM_VKI_Prop_Orc_Banner", vki_orc_banner, "prop"),
    ("SM_VKI_Prop_Siege_Ram", vki_orc_ram, "prop"),
    ("SM_VKI_Prop_Siege_Ram_Burnt", vki_orc_ram_burnt, "none"),
    ("SM_VKI_Prop_Siege_Tower", vki_orc_tower, "prop"),
    ("SM_VKI_Prop_Siege_Tower_Burnt", vki_orc_tower_burnt, "none"),
    ("SM_VKI_Prop_Siege_Catapult", vki_orc_catapult, "prop"),
    ("SM_VKI_Prop_Siege_Catapult_Burnt", vki_orc_catapult_burnt, "none"),
    ("SM_VKI_Prop_Orc_Cage", vki_orc_cage, "prop"),
    ("SM_VKI_Prop_Orc_Cage_Open", vki_orc_cage_open, "prop"),
    ("SM_VKI_Prop_Orc_WarDrum", vki_orc_wardrum, "prop"),
    ("SM_VKI_Overlay_Orc_BearTrap", vki_orc_beartrap, "none"),
    ("SM_VKI_Overlay_Orc_BearTrap_Sprung", vki_orc_beartrap_sprung, "none"),
    ("SM_VKI_Prop_Orc_Totem", vki_orc_totem, "prop"),
]
VKI_ORC_NAMES = [n for n, _, _ in VKI_ORC_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_ORC_SPECS])
