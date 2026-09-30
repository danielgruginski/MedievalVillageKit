# ===================== VKI PROPS DUNGEON: dungeon furniture, dressing and floor overlays =====================
# Dungeon kit (docs/DUNGEON_KIT.md). Package "dungeon". Loaded by vki_ns() after the other prop texts; uses their
# helpers (vki_home_*, vki_tav_*, vki_smy_*, vki_chp_*) and vki_fam_dungeon's (vki_dun_skull, vki_dun_bone, ...).
# Props: origin at the footprint centre, back toward +Y, geometry at its real height (§5). Every top-level name
# starts with vki_/VKI_ (T18). Bones and skulls use the WAX slot with M_VKI_Bone (vki_dun_bone_mats); dressed stone
# the STONE_BLOCK_IN slot with M_VKI_DungeonBlock; fire the GLOW slot (heat per vertex: M_VKI_GlowIn core -> rim).
#   Torch_Wall        wall_hung: iron plate, arm and ring cup, an oak torch leaning out 18 deg, pitch head, flame; light
#   Brazier           iron fire bowl on three legs, coal lumps, embers, flames; light
#   Chains_Wall       wall_hung: two chains from wall eyes to hanging manacles
#   Skeleton_Sitting  wall_floor: a prisoner's skeleton slumped against the wall
#   Bucket            coopered slop bucket with an iron bail
#   Cage              iron floor cage with a pyramid top and a hook, straw and a skull inside (see-through)
#   Rubble            fallen blocks half sunk in a mound of grit
#   Sarcophagus       2 x 1 chest tomb: dark dressed chest with pilasters, pale lid with a recumbent effigy
#   Coffin            2 x 1 dark wooden coffin (toe-pincher), iron handles, cross on the lid
#   Pillar_Cut / _Full   octagonal column on a square plinth; Cut ends in a pale cut cap at 1.00, Full carries a
#                     capital and a block cut at 3.00 (the vault's springing, removed by the cutaway)
#   Candles_Floor     a cluster of tall candles in a wax pool; light
#   Chest_Treasure    open iron-bound chest heaped with gold, gems, coins spilt in front
#   TableDress_Guard  table dressing: dice, cards, a key ring, a tankard and a candle stub; light
#   Overlay_StrawPile loose straw bedding (a low mound)
#   Overlay_Bones     a skull and long bones strewn on the floor
#   Overlay_Puddle    standing water: dark glossy blobs (M_VKI_Puddle) that pick up the torches
#   Overlay_DrainGrate  iron grate over a dark pit in a dressed frame
#   Overlay_TombSlab  2 x 1 grave slab set in the floor, raised cross (head toward local +x: place it at rot 90)
# Build: g["vki_ws_build"]("dungeon", VKI_DPR_NAMES); test: g["vki_test_pieces"](VKI_DPR_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_DPR_TORCH_COL = [1.0, 0.55, 0.22]
VKI_DPR_TORCH_W = 110.0
VKI_DPR_BRAZIER_COL = [1.0, 0.52, 0.20]
VKI_DPR_BRAZIER_W = 260.0
VKI_DPR_CANDLE_COL = [1.0, 0.60, 0.28]
VKI_DPR_CANDLE_W = 60.0


# ---------------------------------------------------------------- helpers
def vki_dpr_light(role, pos, w, color, rng, radius, shadows=1):
    """one vki_lights socket (POINT, flickering)"""
    return dict(type="POINT", role=role, pos=[round(c, 4) for c in pos], w=w, color=list(color), range=rng,
                flicker=1, shadows=shadows, radius=radius)


def vki_dpr_rod(k, a, b, w, mi=IRON, d=None, roll=0.0, bevel=0.0):
    """a square bar from a to b (3-D), cross-section w x d, rolled `roll` rad about its own axis"""
    a = Vector(a); b = Vector(b); dv = b - a
    yaw = math.atan2(dv.y, dv.x)
    pitch = -math.atan2(dv.z, math.hypot(dv.x, dv.y))
    return list(set(k.box(tuple((a + b) / 2), (dv.length, w, d or w), mi, rot=(roll, pitch, yaw), bevel=bevel)))


def vki_dpr_mound(k, c, rx, ry, h, mi, z0=None, nr=3, ns=14, seed=0, wob=0.12, bump=0.12, rim=0.004, smooth=True):
    """closed low mound (straw, gold, wax, grit): rings of ns vertices out to an irregular elliptic outline (radius
    wobble `wob`), height h (1 - t^2)^0.7 with bumps, `rim` at the outline, flat bottom at z0 (default c.z + 0.001)"""
    rnd = random.Random(seed)
    cx, cy, cz = c
    z0 = cz + 0.001 if z0 is None else z0
    bm = k.bm
    rr = [1.0 + wob * (rnd.uniform(-1, 1) + 0.5 * math.sin(3 * 2 * math.pi * i / ns + seed)) for i in range(ns)]
    top = bm.verts.new((cx, cy, cz + h))
    rings = []
    for j in range(1, nr + 1):
        t = j / nr
        rg = []
        for i in range(ns):
            a = 2 * math.pi * i / ns
            ht = rim if j == nr else h * (1 - t * t) ** 0.7 * (1 + bump * rnd.uniform(-1, 1))
            rg.append(bm.verts.new((cx + math.cos(a) * rx * t * rr[i], cy + math.sin(a) * ry * t * rr[i], cz + ht)))
        rings.append(rg)
    bot = [bm.verts.new((v.co.x, v.co.y, z0)) for v in rings[-1]]
    cb = bm.verts.new((cx, cy, z0))
    fs = []
    for i in range(ns):
        j = (i + 1) % ns
        fs.append(bm.faces.new((top, rings[0][i], rings[0][j])))
        for A, B in zip(rings[:-1], rings[1:]):
            fs.append(bm.faces.new((A[i], B[i], B[j], A[j])))
        fs.append(bm.faces.new((rings[-1][i], bot[i], bot[j], rings[-1][j])))
        fs.append(bm.faces.new((cb, bot[j], bot[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.material_index = mi
        f.smooth = smooth
    k.project(fs, mi)
    return [top, cb] + [v for rg in rings for v in rg] + bot


def vki_dpr_blob(k, c, r, z0, z1, mi, ns=16, wob=0.22, seed=0):
    """closed flat star-shaped slab (puddles): irregular outline of mean radius r (tuple: rx, ry), z0..z1"""
    rnd = random.Random(seed)
    rx, ry = (r, r) if not isinstance(r, (tuple, list)) else r
    ph = rnd.uniform(0, 6.3)
    rr = [1.0 + wob * (0.6 * math.sin(2 * 2 * math.pi * i / ns + ph) + 0.4 * rnd.uniform(-1, 1)) for i in range(ns)]
    cx, cy = c
    bm = k.bm
    top = [bm.verts.new((cx + math.cos(2 * math.pi * i / ns) * rx * rr[i], cy + math.sin(2 * math.pi * i / ns) * ry * rr[i],
                         z1)) for i in range(ns)]
    bot = [bm.verts.new((v.co.x, v.co.y, z0)) for v in top]
    ct = bm.verts.new((cx, cy, z1)); cb = bm.verts.new((cx, cy, z0))
    fs = []
    for i in range(ns):
        j = (i + 1) % ns
        fs += [bm.faces.new((ct, top[i], top[j])), bm.faces.new((cb, bot[j], bot[i])),
               bm.faces.new((top[i], bot[i], bot[j], top[j]))]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.material_index = mi
        f.smooth = False
    k.project(fs, mi)
    return top + bot + [ct, cb]


def vki_dpr_block_mats(k):
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_DungeonBlock"
    k.slot_mats[VKI_CAP] = "M_VKI_DungeonCap"


# gold: the TEXTILE slot (63) carries M_VKI_Gold on loot masters -- a flat, painted gold that reads in any light (the
# kit's BRONZE is metallic and went near-black away from the torches); loot masters have no textiles
VKI_DPR_GOLD = VKI_TEXTILE


def vki_dpr_gold_mats(k):
    k.slot_mats[VKI_DPR_GOLD] = "M_VKI_Gold"


# ---------------------------------------------------------------- Torch_Wall
def vki_dpr_torch_wall(k):
    """wall torch, wall_hung and authored at its real height (placer z 0), back at local y 0: an iron wall plate, an
    arm to a ring cup, an oak torch leaning out 18 deg (handle 0.42 m), a pitch-soaked rag head and two GLOW tongues
    that rise straight up; the light socket sits in front of the flame (toward the room)"""
    tilt = math.radians(18.0)
    ax = Vector((0.0, -math.sin(tilt), math.cos(tilt)))
    B = Vector((0.0, -0.13, 1.70))                                    # handle foot
    L = 0.42
    T = B + ax * L                                                     # handle top
    k.box((0.0, -0.010, 1.86), (0.09, 0.020, 0.24), IRON, bevel=0.004)                 # wall plate y -0.02..0
    for z in (1.78, 1.94):
        k.box((0.0, -0.022, z), (0.024, 0.006, 0.024), IRON, bevel=0.0)                 # bolt heads
    cup = B + ax * (0.55 * L)
    vki_dpr_rod(k, (0.0, -0.015, 1.84), (0.0, cup.y + 0.03, cup.z - 0.01), 0.022)      # arm, into the cup ring
    vki_home_hoop(k, tuple(cup), 0.030, 0.044, 0.035, segs=8, mi=IRON, rot=Matrix.Rotation(tilt, 3, "X"))
    rot = Matrix.Rotation(tilt, 4, "X")
    hv = _cyl(k, tuple((B + T) / 2), 0.022, 0.028, L, 8, WOOD, rot=rot)                # handle (flares upward)
    k.bm.normal_update()
    for f in vki_faces_of(hv):
        f.smooth = abs(f.normal.dot(ax)) < 0.7
    head = T + ax * 0.03
    rv = _cyl(k, tuple(head), 0.040, 0.046, 0.12, 8, BURLAP, rot=rot)                 # rag head
    k.set_dark(rv, 0.45)
    top = head + ax * 0.055
    f1 = vki_sto_flame(k, top + Vector((0.0, 0.0, -0.01)), 0.30, 0.060, 0.0, 0.4, 0.02, flat=0.85)
    f2 = vki_sto_flame(k, top + Vector((0.018, -0.012, -0.02)), 0.19, 0.040, 0.25, -0.6, -0.015, flat=0.8)
    lp = top + Vector((0.0, -0.10, 0.12))
    vki_home_meta(k, "wall_hung", "dressing", back=0.0, use=[], vki_nav="none",
                  vki_lights=[vki_dpr_light("torch", lp, VKI_DPR_TORCH_W, VKI_DPR_TORCH_COL, 6.0, 0.08)],
                  vki_fx=[dict(fx="torch_fire", pos=[round(c, 4) for c in (top + Vector((0, 0, 0.1)))], scale=1.0)],
                  vki_mount_zmin=1.70, vki_mount_zmax=2.50,
                  vki_note="authored at its real height (placer z 0); Full walls only")


# ---------------------------------------------------------------- Brazier
def vki_dpr_brazier(k):
    """iron fire bowl (0.60 across, rim 0.74) on three splayed legs with a ring stretcher and pads; a mound of coal
    lumps, glowing embers and three tongues of fire; light 0.5 m above the coals"""
    zb0, zb1 = 0.56, 0.74
    vki_chp_cyl(k, (0.0, 0.0, (zb0 + zb1) / 2), 0.17, 0.30, zb1 - zb0, 12, IRON, smooth=True)
    vki_home_hoop(k, (0.0, 0.0, zb1 - 0.015), 0.283, 0.325, 0.04, segs=12, mi=IRON)
    rr = lambda z: 0.345 - (0.345 - 0.19) * (z / (zb0 + 0.05))
    for i in range(3):
        a = 2 * math.pi * i / 3 + math.pi / 2
        c_, s_ = math.cos(a), math.sin(a)
        z_top = zb0 + 0.05
        vki_dpr_rod(k, (rr(0.02) * c_, rr(0.02) * s_, 0.02), (rr(z_top) * c_, rr(z_top) * s_, z_top), 0.036, roll=a)
        k.box((rr(0.02) * c_, rr(0.02) * s_, 0.012), (0.075, 0.075, 0.024), IRON, bevel=0.006, rot=(0, 0, a))
        k.box((0.25 * c_, 0.25 * s_, zb1 - 0.02), (0.05, 0.03, 0.08), IRON, bevel=0.0, rot=(0, 0, a))   # bowl lugs
    zr = 0.17
    vki_home_hoop(k, (0.0, 0.0, zr), rr(zr) - 0.016, rr(zr) + 0.012, 0.024, segs=12, mi=IRON)
    rnd = random.Random(7)
    for i in range(13):
        a = 2 * math.pi * i / 13 + rnd.uniform(-0.2, 0.2); d = 0.22 * math.sqrt(rnd.random())
        vki_smy_lump(k, (math.cos(a) * d, math.sin(a) * d, zb1 + 0.02 + 0.05 * (1 - d / 0.22)), rnd.uniform(0.06, 0.085),
                     rnd, COAL)
    vki_sto_embers(k, 0.0, 0.0, zb1 + 0.06, 8, 0.17, 0.17, 91, core=0.26, rmin=0.035, rmax=0.055, hmax=0.9)
    for (x, y, h, r, tl, sp, bw) in ((0.0, 0.0, 0.48, 0.10, 0.0, 0.2, 0.03), (-0.09, 0.05, 0.34, 0.075, -0.18, -0.5, -0.03),
                                     (0.09, -0.04, 0.30, 0.07, 0.2, 0.7, 0.025)):
        vki_sto_flame(k, Vector((x, y, zb1 + 0.05)), h, r, tl, sp, bw, flat=0.8)
    lp = (0.0, -0.06, zb1 + 0.55)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_lights=[vki_dpr_light("brazier", lp, VKI_DPR_BRAZIER_W, VKI_DPR_BRAZIER_COL, 7.0, 0.25)],
                  vki_fx=[dict(fx="brazier_fire", pos=[0.0, 0.0, round(zb1 + 0.15, 3)], scale=1.4)])


# ---------------------------------------------------------------- Chains_Wall
def vki_dpr_chain(k, A, M, n, sag=0.05, link=0.080, w=0.040, t=0.012):
    """n links from A to M: centres along a gently bowed path, each link a flat bar along the path, rolled 90 deg
    from its neighbours (reads as a chain from the game camera)"""
    A = Vector(A); M = Vector(M)
    P = lambda s: A.lerp(M, s) + Vector((0.0, -sag * math.sin(math.pi * s), 0.0))
    for i in range(n):
        s0, s1 = (i + 0.1) / n, (i + 0.9) / n
        a, b = P(s0), P(s1)
        d = (b - a).normalized()
        e = link / 2
        mid = (a + b) / 2
        vki_dpr_rod(k, mid - d * e, mid + d * e, w, IRON, d=t, roll=(math.pi / 2) * (i % 2))


def vki_dpr_chains_wall(k):
    """two chains from iron wall eyes (z 1.95) to manacles hanging at 1.2-1.3; back at local y 0 (wall_hung, real
    height)"""
    for (xa, xm, zm, n) in ((-0.28, -0.21, 1.22, 10), (0.28, 0.23, 1.32, 9)):
        k.box((xa, -0.010, 1.95), (0.08, 0.020, 0.08), IRON, bevel=0.004)                    # wall plate
        vki_home_hoop(k, (xa, -0.045, 1.93), 0.022, 0.034, 0.014, segs=8, mi=IRON,
                      rot=Matrix.Rotation(math.pi / 2, 3, "Y"))                             # eye (ring in the y-z plane)
        vki_dpr_rod(k, (xa, -0.018, 1.95), (xa, -0.045, 1.95), 0.011)                       # eye shank
        vki_dpr_chain(k, (xa, -0.045, 1.905), (xm, -0.07, zm + 0.075), n)
        vki_home_hoop(k, (xm, -0.07, zm), 0.042, 0.058, 0.035, segs=10, mi=IRON,
                      rot=Matrix.Rotation(math.pi / 2, 3, "Y") @ Matrix.Rotation(0.3, 3, "Z"))   # manacle
    vki_home_meta(k, "wall_hung", "furniture", back=0.0, use=[], vki_nav="none",
                  vki_note="authored at its real height (placer z 0); Full walls only")


# ---------------------------------------------------------------- Skeleton_Sitting
def vki_dpr_skeleton(k):
    """a prisoner's skeleton sitting against the wall (back at local y ~0.29): pelvis, spine, four rib hoops, a skull
    nodding forward, one arm on the raised knee, the other hand on the floor, one leg drawn up and one outstretched"""
    bn = vki_dun_bone
    k.box((0.0, 0.10, 0.085), (0.26, 0.14, 0.11), VKI_WAX, bevel=0.03)                     # pelvis
    sp = [Vector((0.0, 0.13 + 0.10 * t, 0.15 + 0.47 * t)) for t in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    for a, b in zip(sp[:-1], sp[1:]):
        vki_dpr_rod(k, a, b, 0.035, VKI_WAX, d=0.030)                                        # vertebrae
    lean = Matrix.Rotation(-math.radians(12), 3, "X")
    for i, (z, r) in enumerate(((0.34, 0.12), (0.42, 0.135), (0.50, 0.135), (0.58, 0.12))):
        y = 0.13 + 0.10 * (z - 0.15) / 0.47 - 0.05
        vki_home_hoop(k, (0.0, y, z), r - 0.022, r, 0.020, segs=10, mi=VKI_WAX, sx=1.0, sy=0.72, rot=lean)
    bn(k, (-0.16, 0.21, 0.63), (0.16, 0.21, 0.63), r=0.012)                                  # clavicles
    vki_dun_skull(k, (0.03, 0.12, 0.76), s=1.05, yaw=8, pitch=14, roll=28)
    # arms: left forearm on the raised left knee, right hand on the floor
    bn(k, (-0.16, 0.20, 0.61), (-0.21, 0.04, 0.36), r=0.018)
    bn(k, (-0.21, 0.04, 0.36), (-0.11, -0.22, 0.40), r=0.015)
    k.box((-0.09, -0.29, 0.39), (0.07, 0.09, 0.022), VKI_WAX, bevel=0.0, rot=(0.2, 0.0, 0.3))   # left hand
    bn(k, (0.16, 0.20, 0.61), (0.23, 0.05, 0.33), r=0.018)
    bn(k, (0.23, 0.05, 0.33), (0.29, -0.14, 0.04), r=0.015)
    k.box((0.31, -0.21, 0.015), (0.07, 0.09, 0.02), VKI_WAX, bevel=0.0, rot=(0.0, 0.0, 0.2))    # right hand
    # legs
    bn(k, (-0.09, 0.07, 0.09), (-0.13, -0.30, 0.40), r=0.022)                                # left femur (up)
    bn(k, (-0.13, -0.30, 0.40), (-0.15, -0.55, 0.05), r=0.019)                               # left tibia
    k.box((-0.15, -0.61, 0.022), (0.07, 0.14, 0.035), VKI_WAX, bevel=0.0)                    # left foot
    bn(k, (0.09, 0.07, 0.09), (0.15, -0.36, 0.06), r=0.022)                                  # right femur (flat)
    bn(k, (0.15, -0.36, 0.06), (0.19, -0.74, 0.035), r=0.019)                                # right tibia
    k.box((0.20, -0.79, 0.045), (0.07, 0.035, 0.09), VKI_WAX, bevel=0.0, rot=(0.3, 0.0, 0.0))  # right foot (up)
    for v in k.bm.verts:
        k.set_dark([v], 0.10 + 0.25 * vki_smoothstep(0.35, 0.0, v.co.z))
    vki_dun_bone_mats(k)
    vki_home_meta(k, "wall_floor", "furniture", back="geo", use=[], vki_nav="block")


# ---------------------------------------------------------------- Bucket
def vki_dpr_bucket(k):
    """coopered slop bucket (r 0.15, h 0.30) with murky water and an iron bail lying back against the rim"""
    vki_sto_bucket(k, (0.0, 0.0, 0.0), r=0.15, h=0.30, water=True)
    pts = [Vector((math.cos(a) * 0.162, 0.0, 0.25 + math.sin(a) * 0.16)) for a in
           (0.0, 0.5, 1.0, 1.57, 2.14, 2.64, math.pi)]
    R = Matrix.Rotation(math.radians(-55), 3, "X")
    pts = [R @ (p - Vector((0.0, 0.0, 0.25))) + Vector((0.0, 0.0, 0.25)) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        vki_dpr_rod(k, a, b, 0.012)
    k.slot_mats[WATER] = "WaterMurky"
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="block")


# ---------------------------------------------------------------- Cage
def vki_dpr_cage(k):
    """iron floor cage 0.90 x 0.90, walls to 1.80, pyramid top to 2.15 with a hook ring; plank floor, straw and a
    skull inside; a door in the -Y face (stiles and a lock box). See-through (bars 22 mm)."""
    h = 0.45
    zt = 1.80
    P = lambda x, y, z: Vector((x, y, z))
    for sx in (-1, 1):
        for sy in (-1, 1):
            vki_dpr_rod(k, P(sx * h, sy * h, 0.0), P(sx * h, sy * h, zt + 0.03), 0.044)          # corner posts
            vki_dpr_rod(k, P(sx * h, sy * h, zt), P(0.1 * sx * h, 0.1 * sy * h, zt + 0.9 * 0.36), 0.030)   # ribs
    for z in (0.06, zt, 0.95):
        # rails along y sit 6 mm higher than those along x: crossing in the corner posts, they share no plane (T5S)
        for (a, b) in ((P(-h, -h, z), P(h, -h, z)), (P(-h, h, z), P(h, h, z)),
                       (P(-h, -h, z + 0.006), P(-h, h, z + 0.006)), (P(h, -h, z + 0.006), P(h, h, z + 0.006))):
            if z == 0.95 and a.y == b.y == -h:
                continue                                                                        # no mid rail (door)
            vki_dpr_rod(k, a, b, 0.034)
    n = 6
    for i in range(n):
        t = -h + 2 * h * (i + 1) / (n + 1)
        for (x, y) in ((t, -h), (t, h), (-h, t), (h, t)):
            vki_dpr_rod(k, P(x, y, 0.04), P(x, y, zt + 0.02), 0.022)
    k.box((0.32, -h - 0.03, 0.95), (0.09, 0.04, 0.12), IRON, bevel=0.004)                       # lock box
    vki_home_hoop(k, (0.0, 0.0, 2.21), 0.035, 0.05, 0.016, segs=10, mi=IRON, rot=Matrix.Rotation(math.pi / 2, 3, "X"))
    k.box((0.0, 0.0, 2.15), (0.10, 0.10, 0.07), IRON, bevel=0.01)                                  # apex boss
    vs = list(set(k.box((0.0, 0.0, 0.025), (0.86, 0.86, 0.042), WOOD, bevel=0.008)))           # plank floor
    k.set_dark(vs, 0.3)
    vki_dpr_mound(k, (0.05, 0.08, 0.04), 0.30, 0.26, 0.07, VKI_STRAW, z0=0.035, nr=2, ns=10, seed=3)
    vki_dun_skull(k, (-0.20, -0.18, 0.105), yaw=-30, roll=70, pitch=20)
    k.slot_mats[WOOD] = "Dark"
    vki_dun_bone_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_see_through=1,
                  vki_note="2.2 m tall but see-through: best against a north wall anyway (the hook ring and ribs)")


# ---------------------------------------------------------------- Rubble
def vki_dpr_rubble(k):
    """a heap of fallen blocks (dark dressed stone, bevelled, tumbled) half sunk in a mound of grit (ASH)"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.62, 0.52, 0.16, VKI_ASH, z0=0.001, nr=3, ns=14, seed=11, wob=0.18, bump=0.2)
    rnd = random.Random(21)
    items = [(-0.20, 0.05, 0.40, 0.30, 0.26, 0.18), (0.18, -0.10, 0.36, 0.28, 0.24, 0.16), (0.02, 0.20, 0.44, 0.24,
             0.22, 0.26), (-0.05, -0.22, 0.30, 0.22, 0.18, 0.10), (0.30, 0.18, 0.26, 0.20, 0.18, 0.12),
             (-0.36, -0.14, 0.24, 0.20, 0.16, 0.08), (0.05, 0.02, 0.32, 0.26, 0.20, 0.33)]
    for i, (x, y, sx, sy, sz, z) in enumerate(items):
        vs = list(set(k.box((x, y, z), (sx, sy, sz), VKI_STONE_BLOCK_IN,
                            rot=(rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0, math.pi)),
                            bevel=0.025, jitter=0.012, seed=100 + i)))
        k.set_dark(vs, rnd.uniform(0.0, 0.15))
    for i in range(9):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.35, 0.62)
        vs = _ico(k, (math.cos(a) * d, math.sin(a) * d * 0.85, 0.03), rnd.uniform(0.035, 0.06), VKI_STONE_BLOCK_IN,
                  scale=(1.0, 0.8, 0.6), sub=0, jit=0.01, seed=200 + i)
        k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN)
    vki_dpr_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


# ---------------------------------------------------------------- Sarcophagus
def vki_dpr_sarcophagus(k):
    """chest tomb 2.30 x 1.10 x 1.06: dark dressed plinth, chest and lid (DRESS) with pilasters; on the lid a pale
    recumbent effigy (STONE_BLOCK_IN): pillow, head, torso, legs, hands joined in prayer, feet up"""
    bx = lambda x0, x1, y0, y1, z0, z1, mi, bev=0.02, dark=0.0: k.set_dark(
        list(set(k.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mi, bevel=bev))),
        dark)
    bx(-1.15, 1.15, -0.55, 0.55, 0.0, 0.12, DRESS, 0.02, 0.15)                                  # plinth
    bx(-1.05, 1.05, -0.45, 0.45, 0.115, 0.745, DRESS, 0.015, 0.05)                              # chest
    for x in (-0.90, -0.45, 0.0, 0.45, 0.90):
        for (y0, y1) in ((-0.47, -0.44), (0.44, 0.47)):
            bx(x - 0.035, x + 0.035, y0, y1, 0.16, 0.70, DRESS, 0.008, 0.0)                     # pilasters
    for (x0, x1) in ((-1.07, -1.04), (1.04, 1.07)):
        bx(x0, x1, -0.035, 0.035, 0.16, 0.70, DRESS, 0.008, 0.0)
    bx(-1.10, 1.10, -0.50, 0.50, 0.74, 0.84, DRESS, 0.025, 0.0)                                  # lid (dark: the
    # pale effigy reads against it from above; on a pale lid it vanished)
    # effigy (each part sunk into the lid by its own depth: no coplanar bottoms)
    bx(-0.97, -0.70, -0.23, 0.23, 0.835, 0.905, VKI_STONE_BLOCK_IN, 0.025, 0.05)                 # pillow
    hv = vki_home_ico(k, (-0.80, 0.0, 0.965), 0.105, VKI_STONE_BLOCK_IN, scale=(1.0, 0.9, 0.8), sub=1)
    k.project(vki_faces_of(hv), VKI_STONE_BLOCK_IN)
    bx(-0.72, 0.02, -0.21, 0.21, 0.83, 0.99, VKI_STONE_BLOCK_IN, 0.05, 0.02)                     # torso
    bx(0.0, 0.72, -0.17, 0.17, 0.825, 0.955, VKI_STONE_BLOCK_IN, 0.045, 0.04)                    # legs
    bx(-0.36, -0.22, -0.045, 0.045, 0.97, 1.06, VKI_STONE_BLOCK_IN, 0.015, 0.0)                  # hands
    for y in (-0.085, 0.085):
        bx(0.70, 0.80, y - 0.055, y + 0.055, 0.832, 1.00, VKI_STONE_BLOCK_IN, 0.02, 0.05)        # feet
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block")


# ---------------------------------------------------------------- Coffin
def vki_dpr_coffin(k):
    """dark wooden coffin 1.95 x 0.62: toe-pincher body (widest at the shoulders), a lid 2 cm wider, two iron handles
    a side, a raised iron cross on the lid"""
    hexa = [(-0.95, -0.19), (-0.45, -0.30), (0.95, -0.15), (0.95, 0.15), (-0.45, 0.30), (-0.95, 0.19)]
    vs, fs = vki_prism(k, hexa, 0.0, 0.44, WOOD, axis="z", bevel=0.012)
    k.set_dark(vs, 0.10)
    lid = [(x * 1.015 + (-0.01 if x < 0 else 0.01), y * 1.07) for x, y in hexa]
    vs, fs = vki_prism(k, lid, 0.435, 0.52, WOOD, axis="z", bevel=0.015)
    for (xa, xb) in ((-0.30, -0.10), (0.25, 0.45)):
        for s in (-1, 1):
            y = s * (0.30 - (0.15 * ((xa + xb) / 2 + 0.45) / 1.40)) + s * 0.006     # 2 mm into the slanted side
            k.box(((xa + xb) / 2, y, 0.30), (xb - xa, 0.016, 0.03), IRON, bevel=0.0, rot=(0.0, 0.0, -s * 0.107))
    k.box((0.05, 0.0, 0.527), (1.10, 0.06, 0.014), IRON, bevel=0.0)
    k.box((-0.25, 0.0, 0.530), (0.06, 0.36, 0.014), IRON, bevel=0.0)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


# ---------------------------------------------------------------- Pillar_Cut / Pillar_Full
def vki_dpr_pillar(k, full):
    """octagonal column (r 0.24) on a square plinth (0.70, z 0-0.22) and a base moulding; Cut: a pale cut cap
    0.96-1.00 (the cutaway section, like the walls' caps); Full: capital, abacus and a block cut at 3.00"""
    vki_sto_block(k, -0.35, 0.35, -0.02, 0.22, -0.35, 0.35, bev=0.025, key="pplinth")
    rot8 = Matrix.Rotation(math.pi / 8, 4, "Z")
    mv = _cyl(k, (0.0, 0.0, 0.26), 0.31, 0.27, 0.08, 8, VKI_STONE_BLOCK_IN, rot=rot8)
    k.project(vki_faces_of(mv), VKI_STONE_BLOCK_IN, offset=(0.1, 0.4))
    zt = 2.56 if full else 0.965
    sv = _cyl(k, (0.0, 0.0, (0.29 + zt) / 2), 0.24, 0.235, zt - 0.29, 8, VKI_STONE_BLOCK_IN, rot=rot8)
    k.project(vki_faces_of(sv), VKI_STONE_BLOCK_IN, offset=(0.6, 0.2))
    k.set_dark(sv, 0.06)
    if full:
        cv = _cyl(k, (0.0, 0.0, 2.64), 0.235, 0.33, 0.17, 8, VKI_STONE_BLOCK_IN, rot=rot8)
        k.project(vki_faces_of(cv), VKI_STONE_BLOCK_IN, offset=(0.3, 0.8))
        vki_sto_block(k, -0.38, 0.38, 2.72, 2.84, -0.38, 0.38, bev=0.02, key="pabacus")
        vki_sto_block(k, -0.34, 0.34, 2.835, 3.0, -0.34, 0.34, bev=0.02, top=VKI_CAP, key="ptop")
        k.meta["vki_cut_pair_note"] = "Pillar_Cut is its cut-away twin"
    else:
        cp = _cyl(k, (0.0, 0.0, 0.98), 0.262, 0.262, 0.04, 8, VKI_STONE_BLOCK_IN, rot=rot8)
        k.bm.normal_update()
        k.project([f for f in vki_faces_of(cp) if f.normal.z > 0.7], VKI_CAP, offset=(0.2, 0.5))
    vki_dun_damp(k)
    vki_dpr_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_collider=[[0.0, 0.0, 1.5 if full else 0.5, 0.70, 0.70, 3.0 if full else 1.0]])


def vki_dpr_pillar_cut(k): vki_dpr_pillar(k, False)
def vki_dpr_pillar_full(k): vki_dpr_pillar(k, True)


# ---------------------------------------------------------------- Candles_Floor
def vki_dpr_candles(k):
    """five tall candles (0.16-0.46) standing in a pool of wax on the floor; one light over the cluster"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.26, 0.21, 0.018, VKI_WAX, z0=0.001, nr=2, ns=10, seed=4, wob=0.2, bump=0.3)
    for (x, y, h, r) in ((0.0, 0.03, 0.46, 0.034), (-0.12, -0.06, 0.30, 0.03), (0.11, -0.08, 0.36, 0.03),
                         (0.14, 0.10, 0.22, 0.027), (-0.10, 0.12, 0.16, 0.026)):
        vki_chp_candle(k, (x, y, 0.004), r=r, h=h, segs=8, flame=(0.08, None))
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="block",
                  vki_lights=[vki_dpr_light("candles", (0.0, -0.08, 0.62), VKI_DPR_CANDLE_W, VKI_DPR_CANDLE_COL, 3.5,
                                            0.05, shadows=0)])


# ---------------------------------------------------------------- Chest_Treasure
def vki_dpr_chest_treasure(k):
    vki_dpr_chest(k, True)


def vki_dpr_chest(k, open_=True):
    """iron-bound chest (0.92 x 0.58 x 0.52, dark oak boards round a core). open_: heaped with gold (VKI_DPR_GOLD: M_VKI_Gold), two
    gems, the lid thrown back 105 deg on its rear hinge, coins spilt on the floor in front (Chest_Treasure); closed:
    the lid shut and a padlock on the hasp (Chest_Iron, adventure kit)"""
    W, D, H = 0.46, 0.29, 0.52
    t = 0.03
    k.box((0.0, 0.0, 0.225), (2 * W - 2 * t + 0.01, 2 * D - 2 * t + 0.01, 0.43), WOOD, bevel=0.0)          # core
    for (cx, cy, sx, sy) in ((0.0, -D + t / 2, 2 * W, t), (0.0, D - t / 2, 2 * W, t), (-W + t / 2, 0.0, t, 2 * D - 2 * t),
                             (W - t / 2, 0.0, t, 2 * D - 2 * t)):
        vs = list(set(k.box((cx, cy, H / 2), (sx, sy, H), WOOD, bevel=0.008)))
        vki_top_faces(k, vs, WOOD, (cx, cy, H / 2), (sx, sy, H))
    for x in (-0.30, 0.30):                                                                  # iron straps
        k.box((x, -D - 0.005, H / 2), (0.05, 0.012, H - 0.02), IRON, bevel=0.0)
        k.box((x, D + 0.005, H / 2), (0.05, 0.012, H - 0.02), IRON, bevel=0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.box((sx * (W - 0.03), sy * (D + 0.004), 0.05), (0.07, 0.012, 0.08), IRON, bevel=0.0)       # corners
    k.box((0.0, -D - 0.006, H - 0.09), (0.10, 0.012, 0.12), IRON, bevel=0.0)                           # lock plate
    rnd = random.Random(12)
    if not open_:
        lt = 0.06
        k.box((0.0, 0.0, H + lt / 2), (2 * W + 0.02, 2 * D + 0.02, lt), WOOD, bevel=0.012)                 # lid, shut
        for x in (-0.30, 0.30):
            k.box((x, 0.0, H + lt + 0.004), (0.05, 2 * D + 0.03, 0.012), IRON, bevel=0.0)
            k.box((x, -D - 0.012, H + lt / 2), (0.044, 0.012, lt + 0.01), IRON, bevel=0.0)       # narrower: T5S
        k.box((0.0, -D - 0.022, H - 0.17), (0.075, 0.03, 0.085), IRON, bevel=0.006)                    # padlock
        vki_home_hoop(k, (0.0, -D - 0.022, H - 0.105), 0.016, 0.026, 0.012, segs=8, mi=IRON,
                      rot=Matrix.Rotation(math.pi / 2, 3, "X"))
        k.slot_mats[WOOD] = "Dark"
        vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.85, 0]], vki_nav="block", hinge_axis="local X",
                      vki_lid_state="closed", vki_lid_open_deg=105, vki_locked=1,
                      vki_lid_hinge=[0.0, D, H], vki_lid_box=[-W - 0.02, -D - 0.02, H - 0.005, W + 0.02, D + 0.02, H + 0.08])
        return
    vki_dpr_mound(k, (0.0, 0.0, 0.43), W - t - 0.01, D - t - 0.01, 0.20, VKI_DPR_GOLD, z0=0.40, nr=3, ns=14, seed=8,
                  wob=0.05, bump=0.25)
    for i in range(7):                                                                        # coins on the heap
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.05, 0.25)
        x, y = math.cos(a) * d * 1.3, math.sin(a) * d * 0.7
        z = 0.43 + 0.20 * max(0.0, 1 - (x / 0.42) ** 2 - (y / 0.25) ** 2) ** 0.7 + 0.004
        _cyl(k, (x, y, z), 0.03, 0.03, 0.007, 8, VKI_DPR_GOLD,
             rot=Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, "X") @ Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, "Y"))
    for (x, y, mi) in ((-0.12, -0.05, APPLE), (0.16, 0.04, MUSH_GLOW)):
        g_ = _ico(k, (x, y, 0.60), 0.035, mi, scale=(1.0, 1.0, 0.8), sub=0, seed=3)
        k.project(vki_faces_of(g_), mi)
    spill = [(-0.25, -0.42), (-0.05, -0.47), (0.12, -0.40), (0.30, -0.50), (-0.38, -0.55), (0.05, -0.62), (0.22, -0.66)]
    for i, (x, y) in enumerate(spill):
        _cyl(k, (x, y, 0.0045 + 0.001 * i), 0.03, 0.03, 0.007, 8, VKI_DPR_GOLD,
             rot=Matrix.Rotation(rnd.uniform(-0.12, 0.12), 4, "X"))
    # lid: built closed (hinge line y +D, z H, extending toward -Y), then thrown back 105 deg about the hinge
    before = set(k.bm.verts)
    lt = 0.06
    vs = list(set(k.box((0.0, -D + 0.01, H + lt / 2), (2 * W + 0.02, 2 * D + 0.02, lt), WOOD, bevel=0.012)))
    for x in (-0.30, 0.30):
        k.box((x, -D + 0.01, H + lt + 0.004), (0.05, 2 * D + 0.03, 0.012), IRON, bevel=0.0)
    new = [v for v in k.bm.verts if v not in before]
    bmesh.ops.translate(k.bm, verts=new, vec=(0.0, D, 0.0))                   # hinge edge onto y = +D
    piv = Vector((0.0, D, H))
    bmesh.ops.rotate(k.bm, verts=new, cent=piv, matrix=Matrix.Rotation(math.radians(-105), 3, "X"))
    k.slot_mats[WOOD] = "Dark"
    vki_dpr_gold_mats(k)
    vki_home_meta(k, "floor", "hero", use=[[0.0, -1.05, 0]], vki_nav="block", hinge_axis="local X",
                  vki_lid_state="open", vki_lid_open_deg=105)


# ---------------------------------------------------------------- TableDress_Guard
def vki_dpr_dress_guard(k):
    """guard-room table dressing (on its table's top, z 0 = the top): two dice, a spread of cards, a key ring with two
    keys, a tankard and a candle stub (light)"""
    k.box((-0.12, 0.10, 0.014), (0.028, 0.028, 0.028), VKI_WAX, bevel=0.0, rot=(0, 0, 0.4))
    for i, (x, y, a) in enumerate(((-0.02, -0.08, 0.3), (0.03, -0.09, 0.0), (0.08, -0.08, -0.35))):
        k.box((x, y, 0.002 + 0.0035 * i), (0.062, 0.09, 0.003), PAPER, bevel=0.0, rot=(0, 0, a))
    vki_home_hoop(k, (0.16, -0.13, 0.0045), 0.030, 0.038, 0.006, segs=8, mi=IRON)
    for (dx, a) in ((0.0, 0.2), (0.02, -0.9)):
        vki_dpr_rod(k, (0.16 + 0.03 * math.cos(a), -0.13 + 0.03 * math.sin(a), 0.004),
                    (0.16 + 0.11 * math.cos(a), -0.13 + 0.11 * math.sin(a), 0.004 + 0.001 * (dx > 0)), 0.012, d=0.006)
    vki_tav_tankard(k, -0.18, -0.08, 0.0, kind="foam")
    lp = vki_chp_candle(k, (0.10, 0.02, 0.0), r=0.03, h=0.08, segs=8, flame=(0.07, None))
    vki_home_meta(k, "table", "dressing", use=[], vki_nav="none",
                  vki_lights=[vki_dpr_light("candle", lp, 15.0, VKI_DPR_CANDLE_COL, 2.5, 0.03, shadows=0)],
                  vki_fits="Table_Small (vki_table_z 0.78) or a trestle table")


# ---------------------------------------------------------------- overlays
def vki_dpr_straw(k):
    """loose straw bedding: a low irregular mound (0.12 high) of the straw texture"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.60, 0.46, 0.12, VKI_STRAW, z0=0.001, nr=4, ns=14, seed=5, wob=0.14, bump=0.2)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_dpr_bones(k):
    """a skull on its side and five long bones strewn over ~0.9 x 0.7 m"""
    rnd = random.Random(31)
    for (a, b, r) in (((-0.35, -0.10), (0.05, -0.22), 0.020), ((-0.05, 0.12), (0.30, 0.22), 0.018),
                      ((0.10, -0.05), (0.38, -0.20), 0.016), ((-0.30, 0.20), (-0.10, 0.02), 0.015),
                      ((0.20, 0.05), (0.42, 0.10), 0.014)):
        vki_dun_bone(k, (a[0], a[1], r * 1.25), (b[0], b[1], r * 1.25 + rnd.uniform(0.0, 0.01)), r=r, dark=0.2)
    vki_dun_skull(k, (-0.22, -0.30, 0.075), yaw=35, roll=80, pitch=10, dark=0.1)
    vki_dun_bone_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_dpr_puddle(k):
    """standing water: a larger and a smaller dark glossy blob (M_VKI_Puddle on the WATER slot), 4 mm high"""
    vki_dpr_blob(k, (0.0, 0.05), (0.46, 0.34), 0.0006, 0.004, WATER, ns=16, wob=0.22, seed=2)
    vki_dpr_blob(k, (0.40, -0.40), (0.14, 0.11), 0.0006, 0.0035, WATER, ns=10, wob=0.2, seed=5)
    k.slot_mats[WATER] = "M_VKI_Puddle"
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_dpr_drain(k):
    """iron drain grate over a dark pit, in a dressed stone frame (0.66 square, 2 cm high)"""
    o, i_ = 0.33, 0.21
    for (x0, x1, y0, y1) in ((-o, o, i_, o), (-o, o, -o, -i_), (-o, -i_, -i_, i_), (i_, o, -i_, i_)):
        vs = list(set(k.box(((x0 + x1) / 2, (y0 + y1) / 2, 0.01), (x1 - x0, y1 - y0, 0.02), VKI_STONE_BLOCK_IN,
                            bevel=0.006)))
        k.set_dark(vs, 0.12)
    k.box((0.0, 0.0, 0.0035), (2 * i_ + 0.01, 2 * i_ + 0.01, 0.005), VOID, bevel=0.0)
    for x in (-0.16, -0.08, 0.0, 0.08, 0.16):
        k.box((x, 0.0, 0.012), (0.022, 2 * i_ + 0.05, 0.012), IRON, bevel=0.0)
    for y in (-0.10, 0.10):
        k.box((0.0, y, 0.012), (2 * i_ + 0.05, 0.018, 0.008), IRON, bevel=0.0)
    vki_dpr_block_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_dpr_tombslab(k):
    """grave slab set in the floor (1.90 x 0.90, 3 cm, darkened dressed stone) with a pale raised cross along it"""
    vs = list(set(k.box((0.0, 0.0, 0.015), (1.90, 0.90, 0.03), DRESS, bevel=0.012)))
    k.set_dark(vs, 0.30)
    # pale raised cross, its arms toward local +x (the head: placed at rot 90 the head is north, the cross upright
    # from the game camera; toward -x it read upside down)
    vs = list(set(k.box((-0.05, 0.0, 0.040), (1.30, 0.09, 0.024), VKI_STONE_BLOCK_IN, bevel=0.006)))
    for (y0, y1) in ((-0.28, -0.047), (0.047, 0.28)):
        vs += list(set(k.box((0.30, (y0 + y1) / 2, 0.0395), (0.09, y1 - y0, 0.023), VKI_STONE_BLOCK_IN, bevel=0.006)))
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


# ---------------------------------------------------------------- specs
VKI_DPR_SPECS = [
    ("SM_VKI_Prop_Torch_Wall", vki_dpr_torch_wall, "prop"),
    ("SM_VKI_Prop_Brazier", vki_dpr_brazier, "prop"),
    ("SM_VKI_Prop_Chains_Wall", vki_dpr_chains_wall, "prop"),
    ("SM_VKI_Prop_Skeleton_Sitting", vki_dpr_skeleton, "prop"),
    ("SM_VKI_Prop_Bucket", vki_dpr_bucket, "prop"),
    ("SM_VKI_Prop_Cage", vki_dpr_cage, "prop"),
    ("SM_VKI_Prop_Rubble", vki_dpr_rubble, "prop"),
    ("SM_VKI_Prop_Sarcophagus", vki_dpr_sarcophagus, "prop"),
    ("SM_VKI_Prop_Coffin", vki_dpr_coffin, "prop"),
    ("SM_VKI_Prop_Pillar_Cut", vki_dpr_pillar_cut, "prop"),
    ("SM_VKI_Prop_Pillar_Full", vki_dpr_pillar_full, "prop"),
    ("SM_VKI_Prop_Candles_Floor", vki_dpr_candles, "prop"),
    ("SM_VKI_Prop_Chest_Treasure", vki_dpr_chest_treasure, "prop"),
    ("SM_VKI_Prop_TableDress_Guard", vki_dpr_dress_guard, "prop"),
    ("SM_VKI_Overlay_StrawPile", vki_dpr_straw, "none"),
    ("SM_VKI_Overlay_Bones", vki_dpr_bones, "none"),
    ("SM_VKI_Overlay_Puddle", vki_dpr_puddle, "none"),
    ("SM_VKI_Overlay_DrainGrate", vki_dpr_drain, "none"),
    ("SM_VKI_Overlay_TombSlab", vki_dpr_tombslab, "none"),
]
VKI_DPR_NAMES = [n for n, _, _ in VKI_DPR_SPECS]
vki_register([(n, fn, {"grime": gr}, "dungeon") for n, fn, gr in VKI_DPR_SPECS])
