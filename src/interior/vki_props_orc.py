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
]
VKI_ORC_NAMES = [n for n, _, _ in VKI_ORC_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_ORC_SPECS])
