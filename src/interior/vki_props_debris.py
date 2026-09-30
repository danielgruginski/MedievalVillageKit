# ===================== VKI PROPS DEBRIS: loose debris that gives a level its age (docs/DEBRIS.md) =====================
# Package "adventure". Loaded after vki_props_poi. Small dressing meant to be strewn by the dozen: overlay class,
# walkable (vki_nav "none", no collider: the walker's path ignores it), 400 triangles at most, origin on the footprint
# centre, lying on the floor (z 0). Stone debris carries its stone on the CAP slot and the flag vki_debris_stone: a
# level's scatter restyles it to its own stone (cave rock, dungeon block, ancient stone, sewer block, dwarf granite).
#   Debris_Rocks_A / _B / _C    loose rocks: a scatter; a fallen chunk with chips; a strip of scree for a wall's foot
#   Debris_Pottery_A / _B / _C  a jar broken open spilling grain; a toppled amphora, its neck snapped off; shards
#                               round a pot's base
#   Debris_Planks, _Crate, _Barrel   splintered planks; a smashed crate; a barrel fallen apart (staves, hoops)
#   Debris_Masonry_A / _B       a fallen carved cornice block; a broken column drum
#   Debris_Weapons              a broken sword, a dented helm, arrows
#   Debris_Campfire             a cold campfire: a ring of stones, charred logs, ash
#   Debris_Stalactite           broken stalactites and chips
#   Debris_Ore, Debris_Slag     ore chunks with gold flecks; forge slag and cooled drips (the dwarf halls, the mines)
#   Debris_Sack, Debris_Rags    a torn sack spilling grain; rags and a lost boot
#   Debris_PotPile, _Rubble     a pile of broken pots; a low heap of rubble (the level's stone)
# vki_rooms_debris(ctx) (vki_build_scene, after the props and pools) strews them over a level from R["debris"] =
# dict(density, seed, zones={zone: density}): the theme by each zone's floor style, clear of structure, props, use
# points, spawns, water and chasms.
# Building note (vki_props_poi): an icosphere invalidates vert references held from before it; every part here is
# moved the moment it exists. Every top-level name starts with vki_/VKI_ (T18).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix


# ---------------------------------------------------------------- helpers
VKI_DEB_RUST = VKI_BRICK      # the debris' rusty iron (M_VKI_Rust): the kit's flat IRON read as black lumps on a floor


def vki_deb_rock(k, x, y, r, seed, flat=0.62, mi=VKI_CAP, z=0.0, dark=0.08):
    """one loose rock resting on the floor at (x, y): a jittered, flattened icosahedron (20 faces) turned at random,
    darker toward the floor. -> verts"""
    rnd = random.Random(seed)
    v = vki_home_ico(k, (0.0, 0.0, 0.0), r, mi, scale=(1.0, rnd.uniform(0.70, 0.95), flat), sub=1, jit=0.22 * r,
                     seed=seed, smooth=False)
    M = Matrix.Rotation(rnd.uniform(0.0, 2 * math.pi), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.3, 0.3), 4, "X")
    bmesh.ops.transform(k.bm, verts=v, matrix=M)
    dz = z - 0.005 - min(vv.co.z for vv in v)
    bmesh.ops.translate(k.bm, verts=v, vec=(x, y, dz))
    k.bm.normal_update()
    k.project(vki_faces_of(v), mi)
    top = max(vv.co.z for vv in v)
    for vv in v:
        k.set_dark([vv], dark + 0.28 * vki_smoothstep(top, z, vv.co.z))
    return v


def vki_deb_chips(k, n, rx, ry, seed, rmin=0.018, rmax=0.04, cx=0.0, cy=0.0, mi=VKI_CAP, hole=0.0):
    """n small chips strewn over an ellipse rx x ry round (cx, cy), none inside `hole` (m) of the centre"""
    rnd = random.Random(seed)
    for i in range(n):
        for _ in range(8):
            a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.0, 1.0) ** 0.6
            if d * min(rx, ry) >= hole:
                break
        vki_deb_rock(k, cx + math.cos(a) * d * rx, cy + math.sin(a) * d * ry, rnd.uniform(rmin, rmax), seed * 31 + i,
                     flat=0.55, mi=mi, dark=0.12)


def vki_deb_shard(k, x, y, s, seed, mi=CLAY, z=0.0, n=None):
    """a pottery shard: a flake of a pot's wall (a convex polygon on an ellipse, 7 mm thick) lying tilted on the floor,
    one edge lifted as if still curved. -> verts"""
    rnd = random.Random(seed)
    n = n or rnd.choice((3, 4, 4, 5))
    angs = sorted(rnd.uniform(0.0, 2 * math.pi) for _ in range(n))
    poly = [(s * math.cos(a), 0.72 * s * math.sin(a)) for a in angs]
    vs, fs = vki_prism(k, poly, 0.0, 0.007, mi, axis="z", bevel=0.0)
    M = Matrix.Rotation(rnd.uniform(0.0, 2 * math.pi), 4, "Z") @ Matrix.Rotation(rnd.uniform(-0.45, 0.45), 4, "X") @ \
        Matrix.Rotation(rnd.uniform(-0.25, 0.25), 4, "Y")
    bmesh.ops.transform(k.bm, verts=vs, matrix=M)
    dz = z - 0.002 - min(v.co.z for v in vs)
    bmesh.ops.translate(k.bm, verts=vs, vec=(x, y, dz))
    k.bm.normal_update()
    k.project(vki_faces_of(vs), mi)
    k.set_dark(vs, rnd.uniform(0.05, 0.25))
    return vs


def vki_deb_meta(k, stone=False, **kw):
    """debris metadata: an overlay (walkable, no collider), dressing tier; stone=True flags the CAP-slot stone that a
    level's scatter restyles; rusty iron on VKI_DEB_RUST"""
    k.slot_mats[VKI_DEB_RUST] = "M_VKI_Rust"
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none", vki_debris=1,
                  vki_debris_stone=1 if stone else 0,
                  vki_place_rule="loose debris: anywhere on open floor, any rotation; walkable (no collider); "
                                 "vki_rooms_debris strews it", **kw)


def vki_deb_plank(k, x, y, z, L, w, t, yaw, seed, tilt=0.0, mi=PLANKS, split=True):
    """a board L x w x t lying at (x, y, z) turned yaw, one end snapped to a splintered point (a convex pentagon),
    tilted `tilt` about its length. -> verts"""
    rnd = random.Random(seed)
    p = rnd.uniform(0.05, 0.10) if split else 0.0
    poly = [(-L / 2, -w / 2), (L / 2 - p, -w / 2), (L / 2, -w / 2 + rnd.uniform(0.25, 0.75) * w), (L / 2 - p * 0.6, w / 2),
            (-L / 2, w / 2)] if split else [(-L / 2, -w / 2), (L / 2, -w / 2), (L / 2, w / 2), (-L / 2, w / 2)]
    vs, fs = vki_prism(k, poly, -t / 2, t / 2, mi, axis="z", bevel=0.0)
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(tilt, 4, "X")
    bmesh.ops.transform(k.bm, verts=vs, matrix=M)
    k.bm.normal_update()
    k.project(vki_faces_of(vs), mi)
    k.set_dark(vs, rnd.uniform(0.10, 0.30))
    return vs


# ---------------------------------------------------------------- loose rocks
def vki_deb_rocks_a(k):
    """loose rocks, a scatter over ~0.9 x 0.7 m: seven rocks 0.05-0.12 and a few chips"""
    rnd = random.Random(101)
    for i, (x, y, r) in enumerate(((0.0, 0.0, 0.12), (0.26, 0.10, 0.08), (-0.24, 0.12, 0.09), (0.12, -0.22, 0.07),
                                   (-0.18, -0.18, 0.06), (0.36, -0.12, 0.05), (-0.38, -0.02, 0.05))):
        vki_deb_rock(k, x + rnd.uniform(-0.03, 0.03), y + rnd.uniform(-0.03, 0.03), r, 110 + i)
    vki_deb_chips(k, 6, 0.46, 0.36, 12, hole=0.10)
    vki_deb_meta(k, stone=True)


def vki_deb_rocks_b(k):
    """a fallen chunk: an angular rock 0.45 across, sunk a little, two broken pieces off it and chips round"""
    vki_deb_rock(k, 0.0, 0.0, 0.22, 201, flat=0.70, z=-0.02, dark=0.05)
    vki_deb_rock(k, 0.30, -0.12, 0.10, 202, flat=0.6)
    vki_deb_rock(k, -0.26, 0.16, 0.08, 203, flat=0.6)
    vki_deb_chips(k, 8, 0.50, 0.42, 21, hole=0.24)
    vki_deb_meta(k, stone=True)


def vki_deb_rocks_c(k):
    """scree: a strip of rocks and chips 1.2 m long along local x (for a wall's or a rock face's foot)"""
    rnd = random.Random(301)
    for i in range(8):
        x = -0.52 + 0.15 * i + rnd.uniform(-0.04, 0.04)
        vki_deb_rock(k, x, rnd.uniform(-0.08, 0.10), rnd.uniform(0.05, 0.10), 310 + i, flat=0.6)
    vki_deb_chips(k, 8, 0.62, 0.22, 31, cy=-0.02)
    vki_deb_meta(k, stone=True)


# ---------------------------------------------------------------- broken pottery
def vki_deb_pot_half(k, c, seed, h=0.26, r=0.19, segs=12, light=False):
    """the lower part of a clay jar standing at c, broken off in a jagged rim (outer and inner walls, the inner floor),
    a bite missing from one side; light: a coarser profile (piles). -> verts"""
    rnd = random.Random(seed)
    prof = [(r * 0.53, 0.0), (r * 0.74, h * 0.20), (r * 0.95, h * 0.62), (r, h), (r - 0.014, h), (r * 0.93, h * 0.62),
            (r * 0.70, h * 0.24), (0.0, h * 0.14)]
    if light:
        prof = [(r * 0.53, 0.0), (r * 0.92, h * 0.40), (r, h), (r - 0.014, h), (r * 0.88, h * 0.40), (0.0, h * 0.14)]
    vs, fs = vki_home_lathe(k, prof, c=(0.0, 0.0, 0.0), segs=segs, mi=CLAY, smooth=True)
    off = [rnd.uniform(-0.25, 0.05) * h for _ in range(segs)]         # (the ring under the rim is at 0.62 h)
    bite = rnd.randrange(segs)
    for j in (bite - 1, bite, bite + 1):
        off[j % segs] = -rnd.uniform(0.28, 0.34) * h
    for v in vs:
        if v.co.z > h * 0.95:
            j = int(round((math.atan2(v.co.y, v.co.x) % (2 * math.pi)) / (2 * math.pi / segs))) % segs
            v.co.z += off[j]
    bmesh.ops.translate(k.bm, verts=vs, vec=c)
    k.bm.normal_update()
    return vs


def vki_deb_pottery_a(k):
    """a clay jar broken open where it stood: its lower half with a jagged rim, grain spilt from it, shards round"""
    vs = vki_deb_pot_half(k, (0.0, 0.05, 0.0), 401)
    k.set_dark(vs, 0.10)
    vki_dpr_mound(k, (0.20, -0.20, 0.0), 0.22, 0.14, 0.03, VKI_STRAW, z0=0.001, nr=2, ns=10, seed=402, wob=0.25,
                  bump=0.3)
    rnd = random.Random(403)
    for i in range(7):
        a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.25, 0.45)
        vki_deb_shard(k, math.cos(a) * d, 0.05 + math.sin(a) * d * 0.8, rnd.uniform(0.035, 0.06), 410 + i)
    vki_deb_meta(k)


def vki_deb_pottery_b(k):
    """a clay amphora toppled on its side, its neck snapped off and lying by it, a few shards"""
    rnd = random.Random(501)
    vs, fs = vki_home_lathe(k, [(0.0, 0.0), (0.06, 0.01), (0.15, 0.10), (0.18, 0.28), (0.14, 0.44), (0.07, 0.52),
                                (0.055, 0.56), (0.042, 0.56), (0.045, 0.50), (0.0, 0.50)], c=(0.0, 0.0, 0.0), segs=10,
                            mi=CLAY, smooth=True)
    noff = [rnd.uniform(-0.035, 0.0) for _ in range(10)]
    for v in vs:                                                       # the snapped neck: a ragged edge
        if v.co.z > 0.555:
            v.co.z += noff[int(round((math.atan2(v.co.y, v.co.x) % (2 * math.pi)) / (2 * math.pi / 10))) % 10]
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((-0.08, 0.02, 0.172)) @
                        Matrix.Rotation(0.35, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    k.bm.normal_update()
    k.set_dark(vs, 0.12)
    nv, nf = vki_home_lathe(k, [(0.056, 0.0), (0.050, 0.06), (0.068, 0.10), (0.068, 0.125), (0.048, 0.125),
                                (0.042, 0.06), (0.044, 0.0)], c=(0.0, 0.0, 0.0), segs=8, mi=CLAY, smooth=True,
                            closed=True)                                # the neck with its rim, a tube
    bmesh.ops.transform(k.bm, verts=nv, matrix=Matrix.Translation((0.44, -0.12, 0.066)) @
                        Matrix.Rotation(-0.9, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X"))
    k.bm.normal_update()
    k.set_dark(nv, 0.15)
    for i, (x, y) in enumerate(((0.36, 0.14), (0.28, -0.26), (-0.36, -0.20))):
        vki_deb_shard(k, x, y, rnd.uniform(0.035, 0.05), 510 + i)
    vki_deb_meta(k)


def vki_deb_pottery_c(k):
    """shards round a smashed pot's base: the foot and a stub of wall, a dozen shards flung out"""
    vs = vki_deb_pot_half(k, (0.0, 0.0, 0.0), 601, h=0.09, r=0.15, segs=10)
    k.set_dark(vs, 0.12)
    rnd = random.Random(602)
    for i in range(12):
        a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.20, 0.50)
        vki_deb_shard(k, math.cos(a) * d, math.sin(a) * d * 0.8, rnd.uniform(0.03, 0.06), 610 + i)
    vki_deb_meta(k)


def vki_deb_potpile(k):
    """a pile of broken pots (1.1 x 0.8 m): a jar's lower half standing, a smaller one beside it, a third on its side,
    shards all round"""
    for (x, y, h, r, sd, lie) in ((-0.12, 0.05, 0.26, 0.19, 1701, False), (0.20, 0.14, 0.18, 0.14, 1702, False),
                                  (0.10, -0.20, 0.22, 0.16, 1703, True)):
        vs = vki_deb_pot_half(k, (0.0, 0.0, 0.0), sd, h=h, r=r, segs=9, light=True)
        if lie:
            bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((x, y, r * 0.98)) @
                                Matrix.Rotation(0.7, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y"))
        else:
            bmesh.ops.translate(k.bm, verts=vs, vec=(x, y, 0.0))
        k.bm.normal_update()
        k.set_dark(vs, 0.10)
    rnd = random.Random(1704)
    for i in range(7):
        a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.38, 0.55)
        vki_deb_shard(k, math.cos(a) * d, math.sin(a) * d * 0.72, rnd.uniform(0.035, 0.06), 1710 + i)
    vki_deb_meta(k)


def vki_deb_rubble(k):
    """a low heap of rubble (1.3 x 1.0 m, 0.3 high): broken stone chunks tumbled over a mound of grey grit and dust,
    chips strewn round (the level's stone)"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.58, 0.44, 0.10, VKI_ASH, z0=0.001, nr=2, ns=12, seed=1801, wob=0.2, bump=0.35)
    rnd = random.Random(1802)
    for i, (x, y, r) in enumerate(((0.0, 0.02, 0.16), (0.26, -0.08, 0.12), (-0.24, 0.10, 0.13), (0.10, 0.22, 0.09),
                                   (-0.10, -0.20, 0.10), (0.36, 0.14, 0.07), (-0.38, -0.10, 0.07))):
        d = math.hypot(x / 0.58, y / 0.44)
        vki_deb_rock(k, x, y, r, 1810 + i, flat=0.72, z=0.10 * max(0.0, 1.0 - d * d) * 0.8)
    vki_deb_chips(k, 8, 0.66, 0.52, 1820, hole=0.40)
    vki_deb_meta(k, stone=True)


# ---------------------------------------------------------------- wood
def vki_deb_planks(k):
    """splintered planks: four boards and two short pieces, some lying across others, their ends snapped"""
    rnd = random.Random(701)
    for i, (x, y, L, yaw, lay, tilt) in enumerate(((0.0, 0.0, 0.80, 0.2, 0, 0.0), (0.05, 0.12, 0.62, -0.5, 1, 0.06),
                                                   (-0.20, -0.14, 0.55, 1.2, 0, 0.0), (0.26, -0.10, 0.34, 2.4, 0, 0.0),
                                                   (-0.30, 0.18, 0.26, 0.9, 0, 0.0), (0.12, 0.26, 0.22, -1.3, 0, 0.0))):
        vki_deb_plank(k, x, y, 0.0125 + 0.026 * lay + 0.0012 * i, L, rnd.uniform(0.10, 0.13), 0.024, yaw, 710 + i,
                      tilt=tilt)
    vki_deb_meta(k)


def vki_deb_crate(k):
    """a smashed crate: its bottom and a corner of two sides still standing, their boards broken off at odd heights,
    the lid's boards and a side's thrown round"""
    W = 0.25
    k.box((0.0, 0.0, 0.015), (2 * W, 2 * W, 0.03), PLANKS, bevel=0.0)                            # the bottom
    rnd = random.Random(801)
    for j in range(3):                                                  # west side, broken shorter going up
        z = 0.03 + 0.11 * j
        Lj = 2 * W * (1.0 - 0.25 * j)
        vki_deb_plank(k, -W + 0.012, W - Lj / 2, z + 0.055, Lj, 0.105, 0.024, -math.pi / 2, 810 + j, tilt=math.pi / 2)
    for j in range(2):                                                  # north side, butting inside the west side
        z = 0.033 + 0.11 * j                                            # (3 mm up: no shared planes, T5S)
        Lj = 2 * W * (0.9 - 0.3 * j)
        vki_deb_plank(k, -W + 0.024 + Lj / 2, W - 0.012, z + 0.055, Lj, 0.105, 0.022, 0.0, 820 + j, tilt=math.pi / 2)
    k.box((-0.225, 0.225, 0.20), (0.04, 0.04, 0.34), WOOD, bevel=0.0)                          # corner post
    for i, (x, y, yaw, lay) in enumerate(((0.45, -0.10, 0.3, 0), (0.30, -0.42, -0.8, 0), (-0.40, -0.38, 1.9, 0),
                                          (0.46, 0.14, 1.1, 1))):
        vki_deb_plank(k, x, y, 0.0125 + 0.026 * lay + 0.0012 * i, rnd.uniform(0.34, 0.50), 0.105, 0.022, yaw, 830 + i)
    k.slot_mats[WOOD] = "Dark"
    vki_deb_meta(k)


def vki_deb_barrel(k):
    """a barrel fallen apart: its head on the floor with five staves still standing in a ragged ring, more staves
    fallen outward, one hoop lying round the lot and one leaning"""
    rnd = random.Random(901)
    _cyl(k, (0.0, 0.0, 0.015), 0.22, 0.22, 0.03, 10, WOOD)                                      # the head
    for i in range(5):                                                                           # standing staves
        a = math.radians(110 + 32 * i)
        h = rnd.uniform(0.22, 0.52)
        lean = rnd.uniform(0.05, 0.30)
        vs = list(set(k.box((0.0, 0.0, h / 2 + 0.004), (0.105, 0.024, h), WOOD, bevel=0.0)))
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((0.215 * math.cos(a), 0.215 * math.sin(a), 0.0)) @
                            Matrix.Rotation(a - math.pi / 2, 4, "Z") @ Matrix.Rotation(-lean, 4, "X"))
        k.set_dark(vs, rnd.uniform(0.05, 0.2))
    for i in range(4):                                                                           # fallen staves
        a = math.radians(-60 + 35 * i) + rnd.uniform(-0.2, 0.2)
        vki_deb_plank(k, 0.40 * math.cos(a), 0.40 * math.sin(a), 0.0125 + 0.0012 * i, rnd.uniform(0.40, 0.56), 0.10,
                      0.024, a + rnd.uniform(-0.4, 0.4), 910 + i, mi=WOOD, split=i % 2 == 0)
    vki_home_hoop(k, (0.05, -0.02, 0.0115), 0.27, 0.29, 0.02, segs=12, mi=VKI_DEB_RUST)                   # a hoop round it
    vki_home_hoop(k, (-0.30, 0.20, 0.16), 0.24, 0.26, 0.022, segs=12, mi=VKI_DEB_RUST,
                  rot=Matrix.Rotation(1.15, 3, "Y") @ Matrix.Rotation(0.4, 3, "Z"))               # one leaning
    k.slot_mats[WOOD] = "Dark"
    vki_deb_meta(k)


# ---------------------------------------------------------------- masonry
def vki_deb_masonry_a(k):
    """a fallen cornice block (0.72 long): a plain course, a projecting fillet and a roll moulding along it, one end
    broken off on the slant; chips round"""
    vki_prism(k, [(-0.36, 0.0), (0.36, 0.0), (0.30, 0.26), (-0.36, 0.26)], -0.14, 0.14, VKI_CAP, axis="y", bevel=0.012)
    vki_prism(k, [(-0.36, 0.26), (0.30, 0.26), (0.27, 0.32), (-0.36, 0.32)], -0.20, 0.14, VKI_CAP, axis="y",
              bevel=0.008)
    _cyl(k, (-0.035, -0.17, 0.215), 0.045, 0.045, 0.60, 8, VKI_CAP, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))  # roll
    vki_deb_chips(k, 7, 0.55, 0.38, 41, hole=0.30)
    for v in k.bm.verts:
        k.set_dark([v], 0.06 + 0.20 * vki_smoothstep(0.30, 0.0, v.co.z))
    vki_deb_meta(k, stone=True)


def vki_deb_masonry_b(k):
    """a broken column drum lying on its side: 0.52 long, 0.25 radius, twelve flutes; chips round"""
    vs = _cyl(k, (0.0, 0.0, 0.0), 0.25, 0.25, 0.52, 12, VKI_CAP)
    for v in vs:                                                       # the flutes: every other arris drawn in
        a = math.atan2(v.co.y, v.co.x)
        j = int(round((a % (2 * math.pi)) / (math.pi / 6))) % 12
        if j % 2:
            v.co.x *= 0.88; v.co.y *= 0.88
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((0.0, 0.0, 0.232)) @
                        Matrix.Rotation(0.25, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    k.bm.normal_update()
    k.project(vki_faces_of(vs), VKI_CAP)
    for v in vs:
        k.set_dark([v], 0.06 + 0.22 * vki_smoothstep(0.35, 0.0, v.co.z) + 0.12 * (v.co.x > 0.2))
    vki_deb_chips(k, 7, 0.58, 0.45, 51, hole=0.34)
    vki_deb_meta(k, stone=True)


# ---------------------------------------------------------------- lost gear, a cold camp
def vki_deb_weapons(k):
    """lost gear: a sword snapped in two (hilt and point apart), a dented kettle helm on its side, three arrows (one
    broken)"""
    before = set(k.bm.verts)                                           # the sword's hilt half, lying flat
    k.box((0.01, 0.0, 0.006), (0.40, 0.045, 0.010), VKI_DEB_RUST, bevel=0.0)
    k.box((-0.21, 0.0, 0.016), (0.03, 0.20, 0.030), VKI_DEB_RUST, bevel=0.0)
    k.box((-0.31, 0.0, 0.016), (0.17, 0.030, 0.030), WOOD, bevel=0.0)
    _cyl(k, (-0.41, 0.0, 0.020), 0.024, 0.024, 0.030, 8, VKI_DEB_RUST, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((-0.05, -0.18, 0.0)) @
                        Matrix.Rotation(0.3, 4, "Z"))
    vs, _ = vki_prism(k, [(0.0, -0.0225), (0.20, -0.0225), (0.30, 0.0), (0.20, 0.0225), (0.0, 0.0225)], 0.001, 0.011,
                      VKI_DEB_RUST, axis="z")                                    # the point
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((0.30, 0.02, 0.0)) @ Matrix.Rotation(-0.6, 4, "Z"))
    hv, _ = vki_home_lathe(k, [(0.0, 0.17), (0.07, 0.165), (0.12, 0.13), (0.14, 0.07), (0.145, 0.03), (0.20, 0.02),
                               (0.20, 0.0), (0.0, 0.0)], c=(0.0, 0.0, 0.0), segs=10, mi=VKI_DEB_RUST, smooth=True)   # the helm
    for v in hv:                                                       # a dent
        if v.co.x > 0.05 and v.co.z > 0.08:
            v.co.x -= 0.025
    bmesh.ops.transform(k.bm, verts=hv, matrix=Matrix.Translation((-0.26, 0.20, 0.17)) @ Matrix.Rotation(0.9, 4, "Z") @
                        Matrix.Rotation(1.35, 4, "X"))
    k.bm.normal_update()
    rnd = random.Random(1001)
    for i, (x, y, yaw, ln) in enumerate(((0.20, 0.30, 0.15, 0.70), (0.30, 0.18, 0.45, 0.70), (0.05, -0.38, -0.3, 0.36))):
        before = set(k.bm.verts)
        k.box((0.0, 0.0, 0.006), (ln, 0.012, 0.012), WOOD, bevel=0.0)                            # shaft
        if ln > 0.5:
            vki_prism(k, [(ln / 2, -0.012), (ln / 2 + 0.06, 0.0), (ln / 2, 0.012)], 0.002, 0.010, VKI_DEB_RUST, axis="z")
            for s in (-1.0, 1.0):                                                               # fletching
                vki_prism(k, [(-ln / 2 + 0.01, s * 0.006), (-ln / 2 + 0.11, s * 0.006), (-ln / 2 + 0.02, s * 0.034)],
                          0.004 + 0.001 * (s > 0), 0.007 + 0.001 * (s > 0), CLOTH_B, axis="z")
        bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((x, y, 0.0005 * i)) @
                            Matrix.Rotation(yaw, 4, "Z"))
    k.slot_mats[WOOD] = "Dark"
    for v in k.bm.verts:
        k.set_dark([v], 0.25)                                          # old, rusted, dusty
    vki_deb_meta(k)


def vki_deb_campfire(k):
    """a cold campfire: a ring of seven stones round a bed of ash, three charred logs fallen in"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.30, 0.28, 0.035, VKI_ASH, z0=0.001, nr=2, ns=12, seed=1101, wob=0.15, bump=0.3)
    for i in range(7):
        a = 2 * math.pi * i / 7 + 0.2
        vki_deb_rock(k, 0.36 * math.cos(a), 0.34 * math.sin(a), 0.075 + 0.01 * (i % 3), 1110 + i, flat=0.75)
    for i, (x, y, yaw, ln) in enumerate(((0.02, 0.04, 0.3, 0.42), (-0.06, -0.05, 1.6, 0.36), (0.10, -0.08, 2.5, 0.30))):
        vs = _cyl(k, (0.0, 0.0, 0.0), 0.045, 0.040, ln, 6, WOOD, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((x, y, 0.050 + 0.012 * i)) @
                            Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(0.12 * (i - 1), 4, "Y"))
        k.set_dark(vs, 0.82)                                           # charred
    k.slot_mats[WOOD] = "Dark"
    vki_deb_meta(k, stone=True)


def vki_deb_stalactite(k):
    """broken stalactites: three tapering pieces fallen and lying across each other, a stub on its broken end, chips"""
    rnd = random.Random(1201)
    for i, (x, y, yaw, ln, r, lay) in enumerate(((0.0, 0.0, 0.3, 0.62, 0.09, 0), (0.14, 0.16, 1.9, 0.44, 0.07, 1),
                                                 (-0.26, -0.12, 2.8, 0.36, 0.06, 0))):
        vs = _cyl(k, (0.0, 0.0, 0.0), r, 0.012, ln, 6, VKI_CAP, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((x, y, r * 0.9 + 0.09 * lay)) @
                            Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(-0.08 * lay, 4, "Y"))
        k.bm.normal_update()
        k.project(vki_faces_of(vs), VKI_CAP)
        k.set_dark(vs, 0.10)
    vs = _cyl(k, (0.30, -0.18, 0.11), 0.06, 0.03, 0.22, 6, VKI_CAP)                                # a stub, point up
    k.project(vki_faces_of(vs), VKI_CAP)
    vki_deb_chips(k, 6, 0.50, 0.40, 1210, hole=0.2)
    vki_deb_meta(k, stone=True)


# ---------------------------------------------------------------- ore, slag
def vki_deb_ore(k):
    """ore: six chunks of dark rock (CaveRock, darkened) glinting with gold flecks"""
    rnd = random.Random(1301)
    for i, (x, y, r) in enumerate(((0.0, 0.0, 0.11), (0.22, 0.08, 0.08), (-0.20, 0.10, 0.09), (0.10, -0.20, 0.07),
                                   (-0.16, -0.16, 0.06), (0.30, -0.14, 0.05))):
        vs = vki_deb_rock(k, x, y, r, 1310 + i, flat=0.7, mi=VKI_STONE_BLOCK_IN, dark=0.35)
        top = [v.co.copy() for v in vs if v.co.z > r * 0.5]
        for j, p in enumerate(rnd.sample(top, min(2, len(top)))):
            k.box(tuple(p), (0.024, 0.02, 0.018), VKI_DPR_GOLD, rot=(rnd.uniform(0, 1), 0.3, rnd.uniform(0, 3)),
                  bevel=0.0)
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_CaveRock"
    vki_dpr_gold_mats(k)
    vki_deb_meta(k)


def vki_deb_slag(k):
    """forge slag: glassy black puddles and lumps (M_VKI_Slag) and a few cooled metal drips"""
    rnd = random.Random(1401)
    for i, (x, y, rx, ry) in enumerate(((0.0, 0.0, 0.22, 0.15), (0.26, 0.12, 0.10, 0.08), (-0.24, -0.08, 0.12, 0.09),
                                        (0.10, -0.22, 0.08, 0.06))):
        vki_dpr_blob(k, (x, y), (rx, ry), 0.0005 + 0.001 * i, 0.012 + 0.004 * i, VKI_WAX, ns=10, wob=0.3, seed=1410 + i)
    for i in range(5):
        a = rnd.uniform(0.0, 2 * math.pi); d = rnd.uniform(0.05, 0.30)
        vki_deb_rock(k, math.cos(a) * d, math.sin(a) * d * 0.8, rnd.uniform(0.025, 0.045), 1420 + i, flat=0.6,
                     mi=VKI_DEB_RUST if i % 2 else VKI_WAX, z=0.012, dark=0.1)
    k.slot_mats[VKI_WAX] = "M_VKI_Slag"
    vki_deb_meta(k)


# ---------------------------------------------------------------- a torn sack, rags
def vki_deb_sack(k):
    """a sack lying on its side, torn open, spilling grain in a fan"""
    vs = vki_home_ico(k, (0.0, 0.0, 0.0), 0.20, BURLAP, scale=(1.35, 0.95, 0.60), sub=2, jit=0.02, seed=1501,
                      smooth=True)
    for v in vs:                                                       # its torn mouth, slumped open
        if v.co.x > 0.18:
            v.co.x -= 0.04; v.co.z *= 0.6
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((-0.12, 0.04, 0.115)) @ Matrix.Rotation(0.2, 4, "Z"))
    k.bm.normal_update()
    k.project(vki_faces_of(vs), BURLAP)
    k.set_dark(vs, 0.12)
    vki_dpr_mound(k, (0.22, -0.02, 0.0), 0.26, 0.20, 0.045, VKI_STRAW, z0=0.001, nr=2, ns=12, seed=1502, wob=0.25,
                  bump=0.3)
    vki_deb_meta(k)


def vki_deb_rags(k):
    """rags left on the floor and a lost boot on its side"""
    vki_dpr_blob(k, (0.0, 0.0), (0.22, 0.14), 0.001, 0.010, CLOTH_A, ns=10, wob=0.3, seed=1601)
    vki_dpr_blob(k, (0.26, 0.14), (0.14, 0.10), 0.0015, 0.009, BURLAP, ns=9, wob=0.3, seed=1602)
    vki_dpr_blob(k, (-0.22, 0.16), (0.10, 0.08), 0.0020, 0.008, CLOTH_B, ns=8, wob=0.3, seed=1603)
    before = set(k.bm.verts)
    k.box((0.0, 0.0, 0.045), (0.24, 0.09, 0.09), HIDE, bevel=0.02)                               # the foot
    k.box((-0.08, 0.0, 0.14), (0.09, 0.085, 0.14), HIDE, bevel=0.02)                            # the leg
    bmesh.ops.transform(k.bm, verts=vki_poi_new(k, before), matrix=Matrix.Translation((0.10, -0.24, 0.045)) @
                        Matrix.Rotation(0.6, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X"))
    for v in k.bm.verts:
        k.set_dark([v], 0.30)
    vki_deb_meta(k)


# ---------------------------------------------------------------- the scatter: strewing a level
VKI_DEB_THEME = {"CaveFloor": "cave", "EarthDamp": "lair", "DungeonFlag": "dungeon", "DungeonFlagWarm": "dungeon",
                 "AncientFlag": "ruins", "SewerFloor": "sewer", "DwarfFloor": "dwarf", "DwarfFlag": "dwarf"}
VKI_DEB_STONE = {"cave": "M_VKI_CaveRock", "lair": "M_VKI_CaveRock", "dungeon": "M_VKI_DungeonBlock",
                 "ruins": "M_VKI_AncientBlock", "sewer": "M_VKI_SewerBlock", "dwarf": "M_VKI_DwarfBlock",
                 "forge": "M_VKI_DwarfBlock"}
VKI_DEB_KINDS = {            # (kind, weight) per theme: Debris_<kind>, or a kit overlay named in full (Overlay_...)
    "cave": [("Rocks_A", 3), ("Rocks_B", 2), ("Rocks_C", 2), ("Rubble", 1.5), ("Stalactite", 2), ("Pottery_C", 0.6),
             ("Weapons", 0.6), ("Sack", 0.4), ("Campfire", 0.3), ("Overlay_Gravel", 1.2), ("Overlay_Bones", 0.5)],
    "lair": [("Rocks_A", 2), ("Rocks_B", 1), ("Rubble", 0.8), ("Pottery_C", 1.5), ("Pottery_A", 1), ("PotPile", 0.8),
             ("Planks", 1.5), ("Rags", 1.5), ("Sack", 1), ("Barrel", 0.8), ("Weapons", 1), ("Campfire", 0.5),
             ("Overlay_Refuse", 1.2), ("Overlay_Bones", 1)],
    "dungeon": [("Rocks_A", 1.5), ("Rocks_C", 1.5), ("Rubble", 1.2), ("Pottery_A", 1.5), ("Pottery_B", 1),
                ("Pottery_C", 1.5), ("PotPile", 1), ("Planks", 1.5), ("Crate", 1), ("Barrel", 1), ("Weapons", 1),
                ("Rags", 1), ("Sack", 0.8), ("Overlay_Bones", 1), ("Overlay_Puddle", 0.6)],
    "ruins": [("Masonry_A", 3), ("Masonry_B", 2), ("Rubble", 2), ("Rocks_A", 2), ("Rocks_B", 1), ("Rocks_C", 1),
              ("Pottery_A", 1.5), ("Pottery_B", 1), ("Pottery_C", 1.5), ("PotPile", 1), ("Weapons", 0.6),
              ("Overlay_Bones", 0.5)],
    "sewer": [("Rocks_A", 1), ("Rubble", 0.8), ("Planks", 2), ("Barrel", 1), ("Crate", 1), ("Rags", 2), ("Sack", 1),
              ("Pottery_C", 1), ("Pottery_B", 0.5), ("Overlay_Sludge", 1.5), ("Overlay_Puddle", 1),
              ("Overlay_Bones", 0.3)],
    "dwarf": [("Rocks_A", 1.5), ("Rubble", 1), ("Masonry_A", 1), ("Ore", 2), ("Pottery_C", 1), ("Weapons", 0.8),
              ("Barrel", 0.7), ("Planks", 0.7), ("Slag", 0.5)],
    "forge": [("Slag", 3), ("Ore", 2), ("Rocks_A", 1), ("Rubble", 1), ("Planks", 1), ("Barrel", 1)],
}
VKI_DEB_ONCE = ("Campfire",)                       # at most one per level
VKI_DEB_HUG = ("Rocks_B", "Rocks_C", "Rubble", "Masonry_A", "Masonry_B", "Stalactite", "Overlay_Gravel")  # gather
#                                                  at the feet of walls and rock faces
VKI_DEB_ALONG = ("Rocks_C",)                       # long pieces laid along the nearest wall or rock face
VKI_DEB_NOFLOOR = ("##", "vv", "==", "ss", "ww", "ll", "~~")   # plan codes with no loose floor


def vki_deb_footprint(src, x, y, rot):
    """world XY box (x0, y0, x1, y1) of a master's local footprint turned rot (deg) and moved to (x, y)"""
    bx = vki_local_box(src)
    r = math.radians(rot)
    cs, sn = math.cos(r), math.sin(r)
    pts = [(px * cs - py * sn, px * sn + py * cs) for px in (bx[0], bx[3]) for py in (bx[1], bx[4])]
    return (x + min(p[0] for p in pts), y + min(p[1] for p in pts), x + max(p[0] for p in pts),
            y + max(p[1] for p in pts))


def vki_deb_hit(a, b, gap=0.0):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def vki_deb_near(x, y, boxes):
    """(distance, dx, dy) from (x, y) to the nearest box; dx / dy the gaps along x and y"""
    best = (9e9, 0.0, 0.0)
    for b in boxes:
        dx = max(b[0] - x, 0.0, x - b[2]); dy = max(b[1] - y, 0.0, y - b[3])
        d = math.hypot(dx, dy)
        if d < best[0]:
            best = (d, dx, dy)
    return best


def vki_rooms_debris(ctx):
    """strew debris over a level (vki_build_scene, after the props and pools) from R["debris"] = dict(density
    (fraction of a zone's open cells that get a piece, default 0.15), seed, zones={zone: density}, themes={zone: theme},
    kinds={theme: [(kind, weight)]}). A zone's theme comes from its floor style (VKI_DEB_THEME); a zone without one
    gets none. Each piece stands on a random point of an open cell (no rock, chasm, water or pool code), turned at
    random, its footprint clear of the walls (+6 cm; their whole mesh +4, for spills), posts, links, leaves and pits (+10), props and overlays (+12),
    their use points (0.45), the spawns (0.8), the rock's and the ground tiles' colliders (+15) and the other debris
    (+15). Heavy stone (VKI_DEB_HUG) takes, of eight tries, the one nearest the structure, so it gathers at the feet of
    walls and rock faces; scree (VKI_DEB_ALONG) lies along the nearest one. Stone debris takes the theme's stone
    (VKI_DEB_STONE). Deterministic for a seed. -> pieces placed"""
    R, L, sc = ctx["R"], ctx["L"], ctx["sc"]
    cfg = R.get("debris")
    if not cfg:
        return 0
    rnd = random.Random(cfg.get("seed", 0))
    codes, zmap, zones = L["P"]["codes"], L["zmap"], R["zones"]
    obst = []

    def grow(b, m):
        obst.append((b[0][0] - m, b[0][1] - m, b[1][0] + m, b[1][1] + m))
    struct = []                                        # walls and rock faces (the feet debris gathers at)
    for o in sc.objects:
        c = o.get("vki_class")
        if c == "wall":                                # the whole piece: breaches and collapsed walls spill past
            grow(vki_rooms_wall_env(o), 0.06)          # the wall's envelope
            struct.append(obst[-1])
            grow(vki_rooms_obj_box(o), 0.04)
        elif c in ("post", "leaf", "link", "pit", "stair"):
            grow(vki_rooms_obj_box(o), 0.10)
        elif c in ("prop", "overlay") and o.type == "MESH":
            grow(vki_rooms_obj_box(o), 0.12)
            for u in vki_get(o, "vki_use", None) or []:
                p = vki_mw(o) @ Vector((u[0], u[1], 0.0))
                obst.append((p.x - 0.45, p.y - 0.45, p.x + 0.45, p.y + 0.45))
        elif c in ("rock", "ground"):
            for b in vki_rooms_collider_boxes(o):
                grow(b, 0.15)
                if c == "rock":
                    struct.append(obst[-1])
        elif o.name.startswith("SPN_"):
            p = o.location
            obst.append((p.x - 0.8, p.y - 0.8, p.x + 0.8, p.y + 0.8))
    by_zone = {}
    for cell in sorted(zmap):
        zn = zmap[cell]
        if not zn or codes.get(cell, "..") in VKI_DEB_NOFLOOR:
            continue
        th = cfg.get("themes", {}).get(zn) or VKI_DEB_THEME.get(zones.get(zn, {}).get("floor"))
        if th:
            by_zone.setdefault(zn, (th, []))[1].append(cell)
    props, placed, once, n = ctx["colls"]["Props"], [], set(), 0
    for zn in sorted(by_zone):
        th, cells = by_zone[zn]
        want = int(round(cfg.get("zones", {}).get(zn, cfg.get("density", 0.15)) * len(cells)))
        kinds = cfg.get("kinds", {}).get(th) or VKI_DEB_KINDS[th]
        rnd.shuffle(cells)
        got = 0
        for cell in cells * 4:
            if got >= want:
                break
            ks = [(kd, w) for kd, w in kinds if kd not in once]
            t = rnd.uniform(0.0, sum(w for _, w in ks))
            for kd, w in ks:
                t -= w
                if t <= 0.0:
                    break
            piece = ("SM_VKI_" + kd) if kd.startswith(("Overlay_", "Prop_")) else "SM_VKI_Overlay_Debris_" + kd
            src = vki_rooms_master(piece)
            if src is None:
                continue
            hug = kd in VKI_DEB_HUG
            best = None
            for _ in range(8):
                x = VKI_IG * (cell[0] + rnd.uniform(0.15, 0.85))
                y = VKI_IG * (cell[1] + rnd.uniform(0.15, 0.85))
                rot = round(rnd.uniform(0.0, 360.0), 1)
                if kd in VKI_DEB_ALONG and struct:
                    d_, dx_, dy_ = vki_deb_near(x, y, struct)
                    rot = round((90.0 if dx_ > dy_ else 0.0) + rnd.uniform(-12.0, 12.0) + 180.0 * rnd.randrange(2), 1)
                fp = vki_deb_footprint(src, x, y, rot)
                if any(vki_deb_hit(fp, b) for b in obst) or any(vki_deb_hit(fp, b, 0.15) for b in placed):
                    continue
                d_ = vki_deb_near(x, y, struct)[0] if (hug and struct) else 0.0
                if best is None or d_ < best[0]:
                    best = (d_, x, y, rot, fp)
                if not hug:
                    break
            if best is not None:
                d_, x, y, rot, fp = best
                st = {"cap": VKI_DEB_STONE[th]} if src.get("vki_debris_stone") else None
                o = vki_rooms_put(ctx, props, piece, round(x, 3), round(y, 3), rot, style=st, walls=[], hug=False)
                o["vki_debris"] = 1                        # (the kit's own overlays strewn with it too)
                o["vki_debris_theme"] = th
                placed.append(fp)
                got += 1
                n += 1
                if kd in VKI_DEB_ONCE:
                    once.add(kd)
    ctx["notes"].append("debris: %d pieces" % n)
    return n


# ---------------------------------------------------------------- specs
VKI_DEB_SPECS = [
    ("SM_VKI_Overlay_Debris_Rocks_A", vki_deb_rocks_a), ("SM_VKI_Overlay_Debris_Rocks_B", vki_deb_rocks_b),
    ("SM_VKI_Overlay_Debris_Rocks_C", vki_deb_rocks_c), ("SM_VKI_Overlay_Debris_Pottery_A", vki_deb_pottery_a),
    ("SM_VKI_Overlay_Debris_Pottery_B", vki_deb_pottery_b), ("SM_VKI_Overlay_Debris_Pottery_C", vki_deb_pottery_c),
    ("SM_VKI_Overlay_Debris_Planks", vki_deb_planks), ("SM_VKI_Overlay_Debris_Crate", vki_deb_crate),
    ("SM_VKI_Overlay_Debris_Barrel", vki_deb_barrel), ("SM_VKI_Overlay_Debris_Masonry_A", vki_deb_masonry_a),
    ("SM_VKI_Overlay_Debris_Masonry_B", vki_deb_masonry_b), ("SM_VKI_Overlay_Debris_Weapons", vki_deb_weapons),
    ("SM_VKI_Overlay_Debris_Campfire", vki_deb_campfire), ("SM_VKI_Overlay_Debris_Stalactite", vki_deb_stalactite),
    ("SM_VKI_Overlay_Debris_Ore", vki_deb_ore), ("SM_VKI_Overlay_Debris_Slag", vki_deb_slag),
    ("SM_VKI_Overlay_Debris_Sack", vki_deb_sack), ("SM_VKI_Overlay_Debris_Rags", vki_deb_rags),
    ("SM_VKI_Overlay_Debris_PotPile", vki_deb_potpile), ("SM_VKI_Overlay_Debris_Rubble", vki_deb_rubble),
]
VKI_DEB_NAMES = [n for n, _ in VKI_DEB_SPECS]
vki_register([(n, fn, {"grime": "none"}, "adventure") for n, fn in VKI_DEB_SPECS])

VKI_ADVENTURE_CATALOG += [("Debris (strewn by vki_rooms_debris)", -209.0, VKI_DEB_NAMES)]
