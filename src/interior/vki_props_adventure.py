# ===================== VKI PROPS ADVENTURE: traps, mechanisms, loot and the ruins' furniture =====================
# Adventure kit (docs/ADVENTURE_KIT.md), on the dungeon kit. Package "adventure". Loaded by vki_ns() after
# vki_props_dungeon, whose helpers it uses (vki_dpr_*, vki_dun_*, vki_home_*, vki_sto_*). Props: origin at the
# footprint centre, back toward +Y, real height (§5); pits: origin at the min corner, unrotated (world0), they replace
# the floor over their cells (vki_covers_floor) and block the BFS with vki_collider. Every top-level name starts with
# vki_/VKI_ (T18).
#   Pit_SpikePit_150      a 1.3 m deep pit under a dressed rim, iron spikes and an unlucky skeleton at the bottom
#   Overlay_PressurePlate a loose-looking slab in a dark gap with a carved ring (vki_trap)
#   Overlay_BladeSlot_150 an iron-lined slot in the floor with a crescent blade half out (vki_trap)
#   Prop_Lever_Wall       wall lever (vki_mechanism: up / down)
#   Prop_Boulder          the rolling boulder (vki_trap)
#   Prop_Chest_Iron       the iron-bound chest, shut and padlocked (vki_dpr_chest)
#   Prop_Urns             two clay urns and a broken one with its shards
#   Prop_LootPile         a heap of gold with a crown, a goblet, gems, a shield and a sword stuck in it
#   Overlay_GoldCoins     loose coins
#   Prop_Skeleton_Fallen  a dead adventurer on his back: helmet, sword and round shield beside him
# the ruined temple (ancient stone: AncientBlock dressed, AncientCap pale carved):
#   Prop_Statue_Guardian / _Broken   a 2.4 m stone guardian on a plinth / its snapped plinth with the toppled figure
#   Prop_Altar_Idol       stepped carved altar, a golden idol with ruby eyes, offering bowls, candles (lights)
#   Prop_Column_Ancient / _Broken    a column cut at 3.0 (the vault's springing) / its snapped stump
#   Prop_Column_Fallen    three drums and a capital lying along x
#   Overlay_CrackedFloor  tilted fragments of the room's floor (FLOOR slot) over a dark gap
#   Prop_Roots_Floor / _Wall         roots snaking over the floor / down a Full wall from its top
#   Prop_Brazier_Stone    a stone fire bowl on a pedestal (light)
# Build: g["vki_ws_build"]("adventure", VKI_ADV_NAMES); test: g["vki_test_pieces"](VKI_ADV_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_ADV_PIT = dict(rim=0.15, lining=0.10, depth=1.30)


def vki_adv_box(k, x0, x1, y0, y1, z0, z1, mi, bev=0.0, dark=0.0):
    vs = list(set(k.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mi, bevel=bev)))
    if dark:
        k.set_dark(vs, dark)
    return vs


def vki_adv_coin(k, c, rx=0.0, ry=0.0):
    return _cyl(k, c, 0.03, 0.03, 0.007, 8, VKI_DPR_GOLD,
                rot=Matrix.Rotation(rx, 4, "X") @ Matrix.Rotation(ry, 4, "Y"))


# ---------------------------------------------------------------- Pit_SpikePit_150
def vki_adv_spikepit(k):
    """one cell (origin at its min corner): a dressed rim (top z 0, 0.15 wide, overhanging the shaft 0.10), a stone
    lining down to -1.30, a floor slab, 16 iron spikes and a skeleton that fell in; darkens with depth"""
    P = VKI_ADV_PIT
    r_, t = P["rim"], P["lining"]
    zb = -P["depth"]
    for (x0, x1, y0, y1) in ((0.0, 1.5, 0.0, r_), (0.0, 1.5, 1.5 - r_, 1.5), (0.0, r_, r_, 1.5 - r_),
                             (1.5 - r_, 1.5, r_, 1.5 - r_)):
        vs = vki_adv_box(k, x0, x1, y0, y1, -0.10, 0.0, VKI_STONE_BLOCK_IN, bev=0.012)
        vki_sto_top(k, vs, VKI_STONE_BLOCK_IN, ((x0 + x1) / 2, (y0 + y1) / 2, 0.0))
    a, b = r_, 1.5 - r_
    for (x0, x1, y0, y1) in ((a, b, a, a + t), (a, b, b - t, b), (a, a + t, a + t, b - t), (b - t, b, a + t, b - t)):
        vs = vki_adv_box(k, x0, x1, y0, y1, zb, -0.10, VKI_STONE_BLOCK_IN)
        for v in vs:
            k.set_dark([v], 0.25 + 0.55 * vki_clamp(-v.co.z / P["depth"]))
    vki_adv_box(k, a + t, b - t, a + t, b - t, zb - 0.10, zb, VKI_STONE_BLOCK_IN, dark=0.8)
    rnd = random.Random(61)
    for i in range(4):
        for j in range(4):
            x = a + t + 0.14 + 0.253 * i + rnd.uniform(-0.03, 0.03)
            y = a + t + 0.14 + 0.253 * j + rnd.uniform(-0.03, 0.03)
            h = rnd.uniform(0.34, 0.50)
            vs = _cyl(k, (x, y, zb + h / 2 - 0.01), 0.035, 0.003, h, 5, IRON,
                      rot=Matrix.Rotation(rnd.uniform(-0.15, 0.15), 4, "X") @ Matrix.Rotation(rnd.uniform(-0.15, 0.15), 4, "Y"))
            k.set_dark(vs, 0.3)
    vki_dun_skull(k, (0.95, 0.55, zb + 0.30), yaw=30, roll=60, pitch=15, dark=0.35)
    vki_dun_bone(k, (0.45, 0.60, zb + 0.28), (0.85, 1.05, zb + 0.35), r=0.02, dark=0.4)
    vki_dun_bone(k, (0.55, 0.40, zb + 0.30), (1.00, 0.85, zb + 0.22), r=0.018, dark=0.4)
    vki_dpr_block_mats(k)
    vki_dun_bone_mats(k)
    k.meta.update(vki_class="pit", vki_covers_floor=[0.0, 0.0, 1.5, 1.5], vki_nav="block",
                  vki_collider=[[0.75, 0.75, 0.5, 1.5 - 2 * a + 0.2, 1.5 - 2 * a + 0.2, 1.0]],
                  vki_trap={"kind": "spike_pit", "depth": P["depth"], "hole": [a, a, b, b]},
                  vki_place_rule="origin on a node, rotation 0; R['pits'] leaves the room floor out of its cell")


# ---------------------------------------------------------------- floor traps
def vki_adv_pressureplate(k):
    """a 0.66 slab a hair proud of the floor in a dark 3 cm gap, a carved ring on top"""
    vki_adv_box(k, -0.36, 0.36, -0.36, 0.36, 0.0005, 0.0055, VOID)
    vs = vki_adv_box(k, -0.33, 0.33, -0.33, 0.33, 0.002, 0.020, VKI_STONE_BLOCK_IN, bev=0.006, dark=0.06)
    vki_sto_top(k, vs, VKI_STONE_BLOCK_IN, (0.0, 0.0, 0.02))
    vki_home_hoop(k, (0.0, 0.0, 0.0195), 0.085, 0.105, 0.004, segs=16, mi=VOID)
    vki_dpr_block_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_trap={"kind": "pressure_plate", "trigger": [0.0, 0.0, 0.1, 0.66, 0.66, 0.2]})


def vki_adv_bladeslot(k):
    """an iron-lined slot along local x (1.5 m) with a crescent blade half out of it (0.30 high)"""
    for y in (-0.055, 0.055):
        vki_adv_box(k, -0.75, 0.75, y - 0.015, y + 0.015, 0.0, 0.012, IRON)
    vki_adv_box(k, -0.74, 0.74, -0.04, 0.04, 0.0005, 0.004, VOID)
    cz, ri, ro = -0.25, 0.40, 0.55
    P = lambda a, r: (math.cos(a) * r, cz + math.sin(a) * r)
    angs = [math.radians(a) for a in (28, 52, 76, 100, 124, 152)]
    for a0, a1 in zip(angs[:-1], angs[1:]):
        vs, fs = vki_prism(k, [P(a0, ri), P(a1, ri), P(a1, ro), P(a0, ro)], -0.006, 0.006, STEEL, axis="y")
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_trap={"kind": "blade", "axis": "x", "reach": 0.55})


# ---------------------------------------------------------------- mechanisms
def vki_adv_lever(k):
    """wall lever (wall_hung, real height, back at y 0): an iron plate with a slot, a pivot boss, the arm thrown up
    and out, an oak grip"""
    k.box((0.0, -0.012, 1.25), (0.18, 0.024, 0.34), IRON, bevel=0.005)
    k.box((0.0, -0.026, 1.25), (0.03, 0.006, 0.24), VOID, bevel=0.0)
    _cyl(k, (0.0, -0.045, 1.25), 0.045, 0.045, 0.04, 8, IRON, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    a = Vector((0.0, -0.05, 1.25)); b = Vector((0.0, -0.30, 1.54))
    vki_dpr_rod(k, a, b, 0.03)
    d = (b - a).normalized()
    grip = b + d * 0.07
    rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    vs = _cyl(k, tuple(grip), 0.024, 0.028, 0.16, 8, WOOD, rot=rot)
    k.set_dark(vs, 0.2)
    vki_home_meta(k, "wall_hung", "dressing", back=0.0, use=[[0.0, -0.75, 0]], vki_nav="none",
                  vki_mechanism={"kind": "lever", "states": ["up", "down"], "state": "up", "pivot": [0.0, -0.05, 1.25],
                                 "throw_deg": 70}, vki_note="authored at its real height (placer z 0); Full walls only")


def vki_adv_boulder(k):
    """the rolling boulder: a faceted rock 1.3 m across (dark dressed-stone texture), resting, with a few chips"""
    vs = vki_home_ico(k, (0.0, 0.0, 0.62), 0.66, VKI_STONE_BLOCK_IN, scale=(1.0, 0.96, 0.93), sub=2, jit=0.05, seed=5,
                      rest=0.0, smooth=False)
    k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN)
    for v in vs:
        k.set_dark([v], 0.05 + 0.3 * vki_smoothstep(0.5, 0.0, v.co.z))
    rnd = random.Random(8)
    for i in range(5):
        a = rnd.uniform(0, 6.3); d = rnd.uniform(0.6, 0.72)
        c = _ico(k, (math.cos(a) * d, math.sin(a) * d, 0.025), rnd.uniform(0.03, 0.05), VKI_STONE_BLOCK_IN,
                 scale=(1, 0.8, 0.6), sub=0, jit=0.008, seed=30 + i)
        k.project(vki_faces_of(c), VKI_STONE_BLOCK_IN)
    vki_dpr_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_trap={"kind": "rolling_boulder", "radius": 0.65})


def vki_adv_chest_iron(k):
    vki_dpr_chest(k, False)


# ---------------------------------------------------------------- loot
def vki_adv_urns(k):
    """two clay urns (an amphora 0.62 and a round pot 0.34) and a broken pot with shards"""
    amph = [(0.0, 0.0), (0.08, 0.0), (0.14, 0.08), (0.19, 0.25), (0.17, 0.42), (0.09, 0.52), (0.07, 0.58),
            (0.095, 0.62), (0.0, 0.62)]
    pot = [(0.0, 0.0), (0.10, 0.0), (0.17, 0.10), (0.18, 0.20), (0.12, 0.31), (0.10, 0.34), (0.0, 0.34)]
    half = [(0.0, 0.0), (0.09, 0.0), (0.16, 0.10), (0.17, 0.15), (0.0, 0.15)]
    for prof, (x, y), dk in ((amph, (-0.18, 0.12), 0.0), (pot, (0.22, 0.15), 0.08), (half, (0.05, -0.22), 0.15)):
        vs, fs = vki_home_lathe(k, prof, c=(x, y, 0.0), segs=12, mi=CLAY)
        for v in vs:
            k.set_dark([v], dk + 0.2 * vki_smoothstep(0.15, 0.0, v.co.z))
    rnd = random.Random(4)
    for i in range(4):                                                                        # shards
        a = rnd.uniform(0, 6.3)
        vs = vki_adv_box(k, 0.0, 0.07, 0.0, 0.05, 0.0, 0.012, CLAY)
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((0.25 + 0.2 * math.cos(a), -0.25 + 0.12 * math.sin(a),
                                                                       0.001 * i)) @ Matrix.Rotation(a, 4, "Z"))
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_breakable=1)


def vki_adv_lootpile(k):
    """a heap of gold (M_VKI_Gold on VKI_DPR_GOLD) 1.1 x 0.9 x 0.32 with coins on it, a crown, a goblet, two gems, a round shield leaning on
    it and a sword stuck in it"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.55, 0.45, 0.32, VKI_DPR_GOLD, z0=0.001, nr=3, ns=16, seed=21, wob=0.12, bump=0.2)
    hz = lambda x, y: 0.32 * max(0.0, 1 - (x / 0.55) ** 2 - (y / 0.45) ** 2) ** 0.7
    rnd = random.Random(22)
    for i in range(8):
        a = rnd.uniform(0, 6.3); d = rnd.uniform(0.1, 0.5)
        x, y = math.cos(a) * d * 0.55 / 0.5, math.sin(a) * d * 0.45 / 0.5
        vki_adv_coin(k, (x, y, hz(x, y) + 0.002), rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4))
    # crown on the top
    cx, cy = -0.08, 0.02
    cz = hz(cx, cy) + 0.02
    vki_home_hoop(k, (cx, cy, cz), 0.085, 0.10, 0.05, segs=12, mi=VKI_DPR_GOLD, rot=Matrix.Rotation(0.25, 3, "X"))
    for i in range(6):
        a = 2 * math.pi * i / 6
        _cyl(k, (cx + math.cos(a) * 0.093, cy + math.sin(a) * 0.093 * math.cos(0.25), cz + 0.045 + math.sin(a) * 0.02),
             0.014, 0.002, 0.05, 4, VKI_DPR_GOLD)
    # goblet lying on the heap's flank
    gv, gf = vki_home_lathe(k, [(0.0, 0.0), (0.05, 0.0), (0.05, 0.012), (0.012, 0.025), (0.012, 0.09), (0.045, 0.11),
                                (0.055, 0.18), (0.0, 0.18)], c=(0.0, 0.0, 0.0), segs=10, mi=VKI_DPR_GOLD)
    bmesh.ops.transform(k.bm, verts=gv, matrix=Matrix.Translation((0.30, -0.18, hz(0.30, -0.18) + 0.03)) @
                        Matrix.Rotation(1.3, 4, "Y") @ Matrix.Rotation(0.4, 4, "X"))
    for (x, y, mi) in ((0.12, 0.14, APPLE), (-0.25, -0.10, MUSH_GLOW)):
        g_ = _ico(k, (x, y, hz(x, y) + 0.012), 0.035, mi, scale=(1.0, 1.0, 0.8), sub=0, seed=3)
        k.project(vki_faces_of(g_), mi)
    # round shield leaning on the back of the heap
    before = set(k.bm.verts)
    _cyl(k, (0.0, 0.0, 0.0), 0.30, 0.30, 0.035, 14, WOOD)
    vki_home_hoop(k, (0.0, 0.0, 0.0), 0.285, 0.315, 0.045, segs=14, mi=IRON)
    _cyl(k, (0.0, 0.0, 0.03), 0.07, 0.05, 0.05, 10, IRON)
    sv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, verts=sv, matrix=Matrix.Translation((0.18, 0.40, 0.30)) @ Matrix.Rotation(-1.2, 4, "X"))
    # sword stuck in the heap
    before = set(k.bm.verts)
    k.box((0.0, 0.0, 0.38), (0.05, 0.012, 0.76), STEEL, bevel=0.0)
    k.box((0.0, 0.0, 0.78), (0.22, 0.03, 0.03), IRON, bevel=0.0)
    _cyl(k, (0.0, 0.0, 0.86), 0.018, 0.018, 0.14, 6, WOOD)
    vs = _ico(k, (0.0, 0.0, 0.945), 0.03, VKI_DPR_GOLD, sub=0)
    wv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, verts=wv, matrix=Matrix.Translation((-0.28, 0.10, 0.02)) @ Matrix.Rotation(0.35, 4, "Y") @
                        Matrix.Rotation(0.5, 4, "Z"))
    k.slot_mats[WOOD] = "Dark"
    vki_dpr_gold_mats(k)
    vki_home_meta(k, "floor", "hero", use=[[0.0, -0.95, 0]], vki_nav="block", vki_loot=1)


def vki_adv_coins(k):
    """twelve loose coins over ~0.8 x 0.6 m, some lying on others"""
    rnd = random.Random(9)
    pts = []
    for i in range(12):
        for _t in range(50):
            x, y = rnd.uniform(-0.40, 0.40), rnd.uniform(-0.30, 0.30)
            if all(math.hypot(x - a, y - b) > 0.065 for a, b in pts):
                break
        pts.append((x, y))
        vki_adv_coin(k, (x, y, 0.0045 + 0.0007 * i), rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08))
    vki_dpr_gold_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none", vki_loot=1)


# ---------------------------------------------------------------- the fallen adventurer
def vki_adv_skeleton_fallen(k):
    """a skeleton on its back along local x (skull at -x): rib hoops, arms, legs, feet; a dented helmet rolled off,
    a sword by the right hand and a round shield by the left knee"""
    bn = vki_dun_bone
    k.box((0.0, 0.0, 0.06), (0.14, 0.26, 0.10), VKI_WAX, bevel=0.025)                         # pelvis
    for x0, x1 in ((-0.62, -0.50), (-0.50, -0.38), (-0.38, -0.26), (-0.26, -0.14), (-0.14, -0.03)):
        vki_dpr_rod(k, (x0, 0.0, 0.045), (x1, 0.0, 0.045), 0.034, VKI_WAX, d=0.03)
    ry = Matrix.Rotation(math.pi / 2, 3, "Y")
    for x, r in ((-0.52, 0.12), (-0.44, 0.135), (-0.36, 0.135), (-0.28, 0.12)):
        vki_home_hoop(k, (x, 0.0, r * 0.62), r - 0.022, r, 0.020, segs=10, mi=VKI_WAX, sx=0.62, sy=1.0, rot=ry)
    bn(k, (-0.60, -0.17, 0.03), (-0.60, 0.17, 0.03), r=0.012)
    vki_dun_skull(k, (-0.76, 0.03, 0.075), s=1.05, yaw=-90, roll=-80, pitch=0)
    bn(k, (-0.60, 0.18, 0.03), (-0.32, 0.28, 0.025), r=0.018)                                 # left arm
    bn(k, (-0.32, 0.28, 0.025), (-0.05, 0.32, 0.022), r=0.015)
    k.box((0.04, 0.33, 0.012), (0.09, 0.07, 0.02), VKI_WAX, bevel=0.0)
    bn(k, (-0.60, -0.18, 0.03), (-0.40, -0.36, 0.025), r=0.018)                               # right arm, reaching
    bn(k, (-0.40, -0.36, 0.025), (-0.16, -0.50, 0.022), r=0.015)
    k.box((-0.08, -0.54, 0.012), (0.09, 0.07, 0.02), VKI_WAX, bevel=0.0, rot=(0, 0, -0.5))
    for s, (kx, ky) in ((1, (0.46, 0.16)), (-1, (0.47, -0.10))):
        bn(k, (0.04, s * 0.09, 0.045), (kx, ky, 0.04), r=0.022)
        fx, fy = (0.88, 0.22) if s > 0 else (0.90, -0.05)
        bn(k, (kx, ky, 0.04), (fx, fy, 0.035), r=0.019)
        k.box((fx + 0.05, fy, 0.045), (0.035, 0.07, 0.09), VKI_WAX, bevel=0.0, rot=(0.3 * s, 0.0, 0.0))
    for v in k.bm.verts:
        k.set_dark([v], 0.15)
    # helmet: an iron cap rolled off, lying tipped
    hv = vki_home_ico(k, (0.0, 0.0, 0.0), 0.13, IRON, scale=(1.0, 1.1, 0.9), sub=2, smooth=True)
    for v in hv:
        v.co.z = max(v.co.z, -0.01)
    bmesh.ops.transform(k.bm, verts=hv, matrix=Matrix.Translation((-1.02, -0.30, 0.09)) @ Matrix.Rotation(1.9, 4, "X"))
    # sword by the right hand
    before = set(k.bm.verts)
    k.box((0.0, 0.0, 0.0), (0.78, 0.05, 0.012), STEEL, bevel=0.0)
    k.box((-0.40, 0.0, 0.0), (0.03, 0.22, 0.03), IRON, bevel=0.0)
    _cyl(k, (-0.48, 0.0, 0.0), 0.018, 0.018, 0.14, 6, WOOD, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    vs = _ico(k, (-0.565, 0.0, 0.0), 0.03, VKI_DPR_GOLD, sub=0)
    wv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, verts=wv, matrix=Matrix.Translation((0.10, -0.62, 0.02)) @ Matrix.Rotation(0.25, 4, "Z"))
    # round shield by the left knee, lying on its face
    before = set(k.bm.verts)
    _cyl(k, (0.0, 0.0, 0.02), 0.30, 0.30, 0.035, 14, WOOD)
    vki_home_hoop(k, (0.0, 0.0, 0.02), 0.285, 0.315, 0.045, segs=14, mi=IRON)
    _cyl(k, (0.0, 0.0, 0.05), 0.07, 0.05, 0.035, 10, IRON)
    sv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, verts=sv, matrix=Matrix.Translation((0.42, 0.62, 0.0)) @ Matrix.Rotation(0.12, 4, "X"))
    vki_dun_bone_mats(k)
    vki_dpr_gold_mats(k)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


# ---------------------------------------------------------------- the ruined temple's furniture
def vki_adv_anc_mats(k):
    """ancient stone: dressed (STONE_BLOCK_IN) AncientBlock, pale carved stone (CAP) AncientCap"""
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_AncientBlock"
    k.slot_mats[VKI_CAP] = "M_VKI_AncientCap"


def vki_adv_rod(k, a, b, w, mi, d=None):
    return vki_dpr_rod(k, a, b, w, mi, d=d)


def vki_adv_plinth(k, h=0.40, hw=0.45):
    vki_sto_block(k, -hw, hw, 0.0, h, -hw, hw, bev=0.03, key="stp")
    vki_sto_block(k, -hw - 0.05, hw + 0.05, h, h + 0.08, -hw - 0.05, hw + 0.05, bev=0.02, top=VKI_CAP, key="stc")
    return h + 0.08


def vki_adv_figure(k, z0):
    """a stone guardian (pale CAP stone) standing on z0: robe, armoured torso, pauldrons, helmed head, hands resting on
    a sword whose point stands on the plinth"""
    vki_home_lathe(k, [(0.30, z0 - 0.005), (0.28, z0 + 0.33), (0.25, z0 + 0.73), (0.24, z0 + 0.89), (0.0, z0 + 0.89)],
                   c=(0.0, 0.02, 0.0), segs=12, mi=VKI_CAP, sy=0.8)
    before = set(k.bm.verts)
    zt = z0 + 0.87
    vki_home_lathe(k, [(0.24, zt), (0.29, zt + 0.28), (0.30, zt + 0.46), (0.24, zt + 0.58), (0.12, zt + 0.64),
                       (0.0, zt + 0.65)], c=(0.0, 0.03, 0.0), segs=12, mi=VKI_CAP, sy=0.62)
    hv = vki_home_ico(k, (0.0, 0.01, zt + 0.79), 0.12, VKI_CAP, scale=(0.9, 1.0, 1.1), sub=2)
    k.project(vki_faces_of(hv), VKI_CAP)
    k.box((0.0, 0.02, zt + 0.93), (0.04, 0.22, 0.10), VKI_CAP, bevel=0.01)                   # helm crest
    for s in (-1.0, 1.0):
        pv = vki_home_ico(k, (s * 0.30, 0.03, zt + 0.52), 0.10, VKI_CAP, scale=(1.1, 1.0, 0.7), sub=1)
        k.project(vki_faces_of(pv), VKI_CAP)
        vki_adv_rod(k, (s * 0.30, 0.0, zt + 0.50), (s * 0.26, -0.18, zt + 0.16), 0.10, VKI_CAP)
        vki_adv_rod(k, (s * 0.26, -0.18, zt + 0.16), (s * 0.05, -0.29, zt + 0.06), 0.09, VKI_CAP)
    k.box((0.0, -0.30, zt + 0.06), (0.16, 0.10, 0.10), VKI_CAP, bevel=0.02)                  # hands on the pommel
    k.box((0.0, -0.30, (z0 + 0.02 + zt) / 2), (0.07, 0.02, zt - z0 - 0.02), VKI_CAP, bevel=0.0)   # blade
    k.box((0.0, -0.30, zt + 0.005), (0.34, 0.04, 0.05), VKI_CAP, bevel=0.005)                  # crossguard
    upper = [v for v in k.bm.verts if v not in before]
    return upper


def vki_adv_statue(k):
    """a guardian statue 2.4 m tall on a plinth (0.9 m square): pale stone figure with a sword point-down"""
    z0 = vki_adv_plinth(k)
    vki_adv_figure(k, z0)
    vki_adv_anc_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block",
                  vki_note="2.4 m tall: stand it against a north wall (it hides what is behind it)")


def vki_adv_statue_broken(k):
    """the guardian's plinth and snapped robe; the upper body toppled face-down in front, the head rolled away"""
    z0 = vki_adv_plinth(k)
    rv, rf = vki_home_lathe(k, [(0.30, z0 - 0.005), (0.28, z0 + 0.33), (0.265, z0 + 0.50), (0.0, z0 + 0.52)],
                            c=(0.0, 0.02, 0.0), segs=12, mi=VKI_CAP, sy=0.8)
    rnd = random.Random(3)
    for v in rv:
        if v.co.z > z0 + 0.45:
            v.co.z += rnd.uniform(-0.08, 0.04)
    before = set(k.bm.verts)
    vki_home_lathe(k, [(0.26, 0.0), (0.29, 0.30), (0.30, 0.46), (0.24, 0.58), (0.12, 0.64), (0.0, 0.65)],
                   c=(0.0, 0.0, 0.0), segs=12, mi=VKI_CAP, sy=0.62)
    for s in (-1.0, 1.0):
        vki_adv_rod(k, (s * 0.30, 0.0, 0.50), (s * 0.26, -0.18, 0.16), 0.10, VKI_CAP)
    tv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, verts=tv, matrix=Matrix.Translation((0.05, -0.62, 0.21)) @
                        Matrix.Rotation(math.radians(-88), 4, "X") @ Matrix.Rotation(0.3, 4, "Z"))
    hv = vki_home_ico(k, (0.55, -0.95, 0.11), 0.12, VKI_CAP, scale=(0.9, 1.0, 1.1), sub=2, rest=0.0)
    k.project(vki_faces_of(hv), VKI_CAP)
    for i in range(3):
        c = _ico(k, (-0.35 + 0.2 * i, -0.45 - 0.15 * i, 0.03), 0.05, VKI_CAP, scale=(1, 0.8, 0.6), sub=0, jit=0.01, seed=70 + i)
        k.project(vki_faces_of(c), VKI_CAP)
    vki_adv_anc_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block")


def vki_adv_altar(k):
    """the idol altar (2.1 x 1.1): a step, a carved altar block, a pale top slab; on it a squat golden idol with ruby
    eyes, two offering bowls with coins and two candles (lights)"""
    vki_sto_block(k, -1.05, 1.05, 0.0, 0.14, -0.55, 0.55, bev=0.02, key="alst")
    vki_sto_block(k, -0.75, 0.75, 0.135, 0.95, -0.36, 0.36, bev=0.02, key="alb")
    for (a, b, c, d) in ((-0.62, 0.62, 0.84, 0.90), (-0.62, 0.62, 0.22, 0.28), (-0.62, -0.56, 0.28, 0.84),
                         (0.56, 0.62, 0.28, 0.84)):
        vki_sto_block(k, a, b, c, d, -0.38, -0.34, bev=0.006, key="alf%d" % int(c * 100 + a * 10))
    for x in (-0.30, 0.0, 0.30):
        k.box((x, -0.362, 0.56), (0.12, 0.008, 0.36), VOID, bevel=0.0)
    vki_sto_block(k, -0.80, 0.80, 0.945, 1.03, -0.40, 0.40, bev=0.02, mi=VKI_CAP, key="altop")
    G = VKI_DPR_GOLD
    vki_home_lathe(k, [(0.15, 1.025), (0.17, 1.12), (0.14, 1.26), (0.08, 1.32), (0.0, 1.33)], c=(0.0, 0.05, 0.0),
                   segs=10, mi=G, sy=0.8)
    iv = vki_home_ico(k, (0.0, 0.03, 1.41), 0.10, G, scale=(1.1, 1.0, 0.95), sub=2)
    k.project(vki_faces_of(iv), G)
    k.box((0.0, 0.05, 1.53), (0.24, 0.05, 0.08), G, bevel=0.01)                                 # headdress
    for s in (-1.0, 1.0):
        vki_adv_rod(k, (s * 0.14, 0.04, 1.25), (s * 0.12, -0.08, 1.12), 0.05, G)
        e = _ico(k, (s * 0.035, -0.058, 1.43), 0.018, APPLE, sub=0, seed=2)
        k.project(vki_faces_of(e), APPLE)
    for s in (-1.0, 1.0):
        vki_home_lathe(k, [(0.0, 1.025), (0.08, 1.028), (0.13, 1.08), (0.12, 1.09), (0.0, 1.09)],
                       c=(s * 0.48, -0.08, 0.0), segs=10, mi=CLAY)
        for j in range(3):
            _cyl(k, (s * 0.48 + 0.03 * (j - 1), -0.08 + 0.02 * (j % 2), 1.093 + 0.004 * j), 0.028, 0.028, 0.006, 8, G)
    lights = []
    for s in (-1.0, 1.0):
        p = vki_chp_candle(k, (s * 0.68, 0.22, 1.028), r=0.03, h=0.20, segs=8, flame=(0.08, None))
        lights.append(vki_dpr_light("candle", p, 30.0, VKI_DPR_CANDLE_COL, 3.0, 0.03, shadows=0))
    vki_dpr_gold_mats(k)
    vki_adv_anc_mats(k)
    vki_home_meta(k, "floor", "hero", use=[[0.0, -1.0, 0]], vki_nav="block", vki_lights=lights, vki_loot=1)


def vki_adv_column(k, broken=False):
    """ancient column: square plinth, a moulded base, a shaft with entasis (pale stone); Full: echinus, abacus and a
    block cut at 3.00 (the vault's springing); broken: the shaft snapped at about 1.3 m with a jagged break"""
    vki_sto_block(k, -0.36, 0.36, -0.02, 0.22, -0.36, 0.36, bev=0.025, key="cpl")
    bv = _cyl(k, (0.0, 0.0, 0.26), 0.31, 0.28, 0.08, 16, VKI_STONE_BLOCK_IN)
    k.project(vki_faces_of(bv), VKI_STONE_BLOCK_IN)
    if broken:
        sv, sf = vki_home_lathe(k, [(0.265, 0.29), (0.262, 0.80), (0.258, 1.25), (0.0, 1.32)], segs=16, mi=VKI_CAP)
        rnd = random.Random(12)
        for v in sv:
            if v.co.z > 1.2:
                v.co.z += rnd.uniform(-0.14, 0.06)
    else:
        vki_home_lathe(k, [(0.265, 0.29), (0.262, 1.10), (0.245, 1.90), (0.225, 2.47), (0.0, 2.47)], segs=16, mi=VKI_CAP)
        cv = _cyl(k, (0.0, 0.0, 2.555), 0.22, 0.33, 0.18, 16, VKI_STONE_BLOCK_IN)
        k.project(vki_faces_of(cv), VKI_STONE_BLOCK_IN)
        vki_sto_block(k, -0.37, 0.37, 2.64, 2.79, -0.37, 0.37, bev=0.02, key="cab")
        vki_sto_block(k, -0.33, 0.33, 2.785, 3.0, -0.33, 0.33, bev=0.02, top=VKI_CAP, key="ctop")
    vki_dun_damp(k)
    vki_adv_anc_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_collider=[[0.0, 0.0, 0.7 if broken else 1.5, 0.72, 0.72, 1.4 if broken else 3.0]],
                  vki_note=None if broken else "3.0 m tall: along a north wall, or the ends of a nave")


def vki_adv_column_full(k): vki_adv_column(k, False)
def vki_adv_column_broken(k): vki_adv_column(k, True)


def vki_adv_column_fallen(k):
    """three drums and the capital of a fallen column lying along x (2.5 m), pale stone"""
    rnd = random.Random(4)
    ry = Matrix.Rotation(math.pi / 2, 4, "Y")
    for (x, L, yaw, y) in ((-0.78, 0.80, 0.05, 0.02), (0.08, 0.72, -0.12, -0.04), (0.78, 0.55, 0.20, 0.06)):
        v = _cyl(k, (x, y, 0.255), 0.255, 0.255, L, 16, VKI_CAP, rot=Matrix.Rotation(yaw, 4, "Z") @ ry)
        k.bm.normal_update()
        for f in vki_faces_of(v):
            f.smooth = abs(f.normal.dot(Vector((math.cos(yaw), math.sin(yaw), 0.0)))) < 0.7
        k.set_dark(v, rnd.uniform(0.0, 0.1))
    vs = list(set(k.box((1.28, -0.05, 0.16), (0.40, 0.62, 0.32), VKI_STONE_BLOCK_IN, rot=(0.0, 0.25, 0.4), bevel=0.02)))
    vki_adv_anc_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_adv_cracked(k):
    """a broken patch of floor (1.3 m): five slab fragments of the room's floor (FLOOR slot, world-locked, default
    AncientFlag) tilted up 3-8 deg over a dark gap"""
    vki_adv_box(k, -0.64, 0.64, -0.64, 0.64, 0.0008, 0.004, VOID)
    frags = [[(-0.62, -0.62), (0.05, -0.62), (0.10, -0.08), (-0.62, 0.02)],
             [(0.10, -0.62), (0.62, -0.62), (0.62, -0.02), (0.15, -0.05)],
             [(-0.62, 0.07), (-0.05, -0.02), (0.02, 0.62), (-0.62, 0.62)],
             [(0.02, 0.0), (0.35, 0.03), (0.30, 0.62), (0.07, 0.62)],
             [(0.40, 0.03), (0.62, 0.03), (0.62, 0.62), (0.35, 0.62)]]
    rnd = random.Random(19)
    for i, fr in enumerate(frags):
        cx = sum(p[0] for p in fr) / 4; cy = sum(p[1] for p in fr) / 4
        sh = [(cx + (p[0] - cx) * 0.94, cy + (p[1] - cy) * 0.94) for p in fr]
        vs, fs = vki_prism(k, sh, 0.004, 0.05, VKI_FLOOR, axis="z", bevel=0.006)
        ang = math.radians(rnd.uniform(3.0, 8.0)); axd = rnd.uniform(0, math.pi)
        R = Matrix.Rotation(ang, 4, Vector((math.cos(axd), math.sin(axd), 0.0)))
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((cx, cy, 0.0)) @ R @ Matrix.Translation((-cx, -cy, 0.0)))
        dz = 0.003 - min(v.co.z for v in vs)
        for v in vs:
            v.co.z += dz
        k.set_dark(vs, 0.05 * i)
    k.slot_mats[VKI_FLOOR] = "AncientFlag"
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none",
                  vki_note="restyle with the room's floor: style {'floor': ...}")


def vki_adv_root(k, pts, r0, r1, segs=6):
    """a tapering root along pts (3-D): one cylinder per segment, radii r0 -> r1, smooth, BARK_OAK"""
    n = len(pts) - 1
    for i in range(n):
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        ra = r0 + (r1 - r0) * i / n; rb = r0 + (r1 - r0) * (i + 1) / n
        d = b - a
        L = d.length + 0.02
        rot = d.normalized().to_track_quat("Z", "Y").to_matrix().to_4x4()
        v = _cyl(k, tuple((a + b) / 2), ra, rb, L, segs, BARK_OAK, rot=rot)
        for f in vki_faces_of(v):
            f.smooth = True
        k.set_dark(v, 0.2)


def vki_adv_roots_floor(k):
    """tree roots breaking through the floor: three roots snaking over ~2.4 x 1.0 m, half sunk, thinning out"""
    rnd = random.Random(7)
    for (x0, y0, a0, L, r0) in ((-1.25, 0.25, -0.2, 2.3, 0.10), (-1.2, -0.3, 0.25, 1.6, 0.08), (0.1, 0.4, -0.9, 0.9, 0.06)):
        pts = []
        a = a0; x, y = x0, y0
        for i in range(8):
            r = r0 + (0.02 - r0) * i / 7
            pts.append((x, y, r * 0.55))
            a += rnd.uniform(-0.35, 0.35)
            x += math.cos(a) * L / 7; y += math.sin(a) * L / 7
            y = max(-0.48, min(0.48, y)); x = max(-1.3, min(1.3, x))
        vki_adv_root(k, pts, r0, 0.02)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="none")


def vki_adv_roots_wall(k):
    """roots that came through the vault: three roots down a wall face from under its coping (2.80) to the floor,
    thinning, and two short tendrils hanging free; wall_hung (back at y 0, top <= H - 0.14), 0.8 m wide (fits the
    free span between two posts on a 150 wall)"""
    rnd = random.Random(8)
    for (x0, r0, zend) in ((-0.26, 0.08, 0.0), (0.05, 0.07, 0.3), (0.28, 0.06, 1.2)):
        pts = []
        x = x0
        for i in range(9):
            z = 2.78 - (2.78 - zend) * i / 8
            r = r0 + (0.02 - r0) * i / 8
            pts.append((x, -r - 0.005, z))
            x += rnd.uniform(-0.12, 0.12)
            x = max(-0.30, min(0.30, x))
        vki_adv_root(k, pts, r0, 0.02)
    for (x, z) in ((-0.15, 2.55), (0.20, 2.2)):
        vki_adv_root(k, [(x, -0.03, z), (x + 0.05, -0.12, z - 0.35), (x + 0.02, -0.16, z - 0.7)], 0.025, 0.01, segs=5)
    vki_home_meta(k, "wall_hung", "furniture", back=0.0, use=[], vki_nav="none",
                  vki_note="2.8 m tall: Full walls only (it comes out under the coping)")


def vki_adv_brazier_stone(k):
    """a stone fire bowl on a square pedestal: coal, embers, three tongues of fire; light"""
    vki_sto_block(k, -0.22, 0.22, 0.0, 0.76, -0.22, 0.22, bev=0.02, key="bsp")
    vki_sto_block(k, -0.27, 0.27, 0.755, 0.83, -0.27, 0.27, bev=0.015, key="bsc")
    vki_home_lathe(k, [(0.10, 0.825), (0.30, 0.90), (0.35, 1.02), (0.31, 1.045), (0.0, 1.045)], segs=16,
                   mi=VKI_STONE_BLOCK_IN)
    rnd = random.Random(5)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.2, 0.2); d = 0.20 * math.sqrt(rnd.random())
        vki_smy_lump(k, (math.cos(a) * d, math.sin(a) * d, 1.06), rnd.uniform(0.06, 0.08), rnd, COAL)
    vki_sto_embers(k, 0.0, 0.0, 1.10, 7, 0.15, 0.15, 93, core=0.24, rmin=0.035, rmax=0.05, hmax=0.9)
    for (x, y, h, r, tl, sp, bw) in ((0.0, 0.0, 0.45, 0.09, 0.0, 0.2, 0.03), (-0.08, 0.05, 0.30, 0.07, -0.18, -0.5, -0.03),
                                     (0.08, -0.04, 0.27, 0.065, 0.2, 0.7, 0.025)):
        vki_sto_flame(k, Vector((x, y, 1.08)), h, r, tl, sp, bw, flat=0.8)
    vki_adv_anc_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_lights=[vki_dpr_light("brazier", (0.0, -0.06, 1.60), VKI_DPR_BRAZIER_W, VKI_DPR_BRAZIER_COL, 7.0, 0.25)],
                  vki_fx=[dict(fx="brazier_fire", pos=[0.0, 0.0, 1.2], scale=1.3)])


# ---------------------------------------------------------------- specs
VKI_ADV_SPECS = [
    ("SM_VKI_Pit_SpikePit_150", vki_adv_spikepit, "none"),
    ("SM_VKI_Overlay_PressurePlate", vki_adv_pressureplate, "none"),
    ("SM_VKI_Overlay_BladeSlot_150", vki_adv_bladeslot, "none"),
    ("SM_VKI_Prop_Lever_Wall", vki_adv_lever, "prop"),
    ("SM_VKI_Prop_Boulder", vki_adv_boulder, "prop"),
    ("SM_VKI_Prop_Chest_Iron", vki_adv_chest_iron, "prop"),
    ("SM_VKI_Prop_Urns", vki_adv_urns, "prop"),
    ("SM_VKI_Prop_LootPile", vki_adv_lootpile, "prop"),
    ("SM_VKI_Overlay_GoldCoins", vki_adv_coins, "none"),
    ("SM_VKI_Prop_Skeleton_Fallen", vki_adv_skeleton_fallen, "prop"),
    # the ruined temple
    ("SM_VKI_Prop_Statue_Guardian", vki_adv_statue, "prop"),
    ("SM_VKI_Prop_Statue_Broken", vki_adv_statue_broken, "prop"),
    ("SM_VKI_Prop_Altar_Idol", vki_adv_altar, "prop"),
    ("SM_VKI_Prop_Column_Ancient", vki_adv_column_full, "prop"),
    ("SM_VKI_Prop_Column_Broken", vki_adv_column_broken, "prop"),
    ("SM_VKI_Prop_Column_Fallen", vki_adv_column_fallen, "prop"),
    ("SM_VKI_Overlay_CrackedFloor", vki_adv_cracked, "none"),
    ("SM_VKI_Prop_Roots_Floor", vki_adv_roots_floor, "prop"),
    ("SM_VKI_Prop_Roots_Wall", vki_adv_roots_wall, "prop"),
    ("SM_VKI_Prop_Brazier_Stone", vki_adv_brazier_stone, "prop"),
]
VKI_ADV_NAMES = [n for n, _, _ in VKI_ADV_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_ADV_SPECS])
