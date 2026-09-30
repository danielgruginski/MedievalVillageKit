# ===================== VKI FAM MINE: mines -- track, carts, timbering, ore veins, the shaft and its treadwheel (mine kit) =====================
# Mine kit (docs/MINE_KIT.md). Package "adventure". Loaded by vki_ns() after vki_props_debris; the builders call the
# prop helpers (vki_home_*, vki_dpr_*, vki_adv_*, vki_deb_*, vki_poi_*, vki_cav_rock_mats) at build time. A mine is a
# cave map (R["cave"]) whose galleries are driven through the rock; its levels are laid out like the caves
# (vki_rooms_mine), with the track laid from polylines.
# Track (class overlay, walkable, 1.5 m tiles centred on track points): a 0.60 m gauge -- oak rails capped with an
#   iron strap worn bright (the running surface, rail top 0.117), on sleepers every 0.375 m. Overlay_Track_Straight,
#   _End (a buffer stop), _Curve (a quarter turn of radius 0.75 about the tile's corner), _Tee and _Cross (a timber
#   turntable with rail stubs to each arm). vki_mine_tracks (vki_rooms_mine) picks each tile from its connections
#   (N 1, E 2, S 4, W 8; vki_track["conn"] at rotation 0) and turns it.
# Carts (the rails' gauge): Mine_Cart (a wooden tub battered out, iron-bound, on four iron wheels), Mine_Cart_Ore
#   (heaped with ore), Mine_Cart_Tipped (on its side off the track, its ore spilt).
# Timbering (vki_wall_anchor: posts may be let into a rock face; vki_cam_fade): Mine_Set (two battered posts and a cap
#   across a gallery two cells wide, head boards over the cap), Mine_Set_Lamp (a lantern on a post), Mine_Set_Broken
#   (a set that gave way: its cap snapped and down across the gallery, rocks on it).
# Ore veins (let into a rock face, back at local +y): Vein_Gold (white quartz seams flecked with gold), Vein_Iron
#   (rust-red bands and nodules), Vein_Crystal (glowing crystals growing from a seam, a cold light).
# The shaft: Pit_Shaft_300x300 (a timber collar round a 2.16 m opening, cribbing down into the dark, a ladder) and
#   POI_Treadwheel (a point of interest over it: the headframe, its sheave, the cage at the landing, a great treadwheel
#   winding the rope, a signal bell, a kibble; it carries the level's lift link, vki_link "lift").
# Props: Mine_OrePile, Mine_Wheelbarrow, Mine_ToolRack, Mine_Bench (a sorting bench), Mine_LanternPole, Mine_CaveIn (a
#   collapse filling a gallery), Mine_Barricade (planks across a drift, a warning board), Mine_SleeperStack; debris
#   Debris_Tools and Debris_Rail (the scatter's "mine" theme, vki_rooms_mine).
# The adit: SM_VKI_Rock_Cave_OOFF_Adit -- the cave's tunnel tile with a wider cleft, timbered like a mine's mouth
#   (vki_cav_tile with tunnel=VKI_MINE_ADIT_T; R["tunnel_kinds"] = {link id: "Adit"}), a floor running into the dark.
# Building note (vki_props_poi): an icosphere can invalidate BMVert references held from before it, so every part with
# an icosphere is finished (moved, coloured, measured) the moment it exists.
# Build: g["vki_ws_build"]("adventure", VKI_MINE_NAMES); test: g["vki_test_pieces"](VKI_MINE_NAMES) -> {}.
# Every top-level name starts with vki_/VKI_ (T18).
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_MINE_HG = 0.30                          # half gauge: the rails' centres at +-0.30
VKI_MINE_RAIL = (0.035, 0.034, 0.105)       # the oak rail: half width, bottom (let into the sleepers), top
VKI_MINE_STRAP = (0.025, 0.105, 0.117)      # its iron strap: half width, bottom, top (the running surface)
VKI_MINE_SLEEPER = (0.50, 0.07, -0.012, 0.042)   # half length, half width, bottom, top
VKI_MINE_TOP = VKI_MINE_STRAP[2]            # the rail top: the carts' wheels stand on it
VKI_MINE_BITS = {"N": 1, "E": 2, "S": 4, "W": 8}
VKI_MINE_TRACK_BASE = {"End": 4, "Straight": 5, "Curve": 6, "Tee": 14, "Cross": 15}   # connections at rotation 0
VKI_MINE_WOOD = "M_VKI_MineWood"            # sleepers, rails, carts: weathered oak
VKI_MINE_TIMBER = "M_VK_Hewn"               # the sets, the collar, the headframe: pale hewn timber that reads in the dark
VKI_MINE_LAMP_COL = [1.0, 0.62, 0.30]
VKI_MINE_LAMP_W = 90.0
VKI_MINE_CART = dict(L=1.10, wt=0.33, wb=0.27, zb=0.36, zt=0.82, wall=0.04, wr=0.14, wy=0.32)
VKI_MINE_ADIT = dict(hw=0.72, back=0.62, lintel=2.30, head="timbered")


# ---------------------------------------------------------------- track
def vki_mine_rot90(m):
    """a track tile's connections turned 90 deg counter-clockwise: N -> W, E -> N, S -> E, W -> S"""
    B = VKI_MINE_BITS
    out = 0
    for a, b in (("N", "W"), ("E", "N"), ("S", "E"), ("W", "S")):
        if m & B[a]:
            out |= B[b]
    return out


def vki_mine_track_piece(mask):
    """(kind, rotation deg -180..90) of the track tile showing the connections `mask`, or None (no connection)"""
    for kind, m in VKI_MINE_TRACK_BASE.items():
        for kk in range(4):
            if m == mask:
                return kind, (90 * kk + 180) % 360 - 180
            m = vki_mine_rot90(m)
    return None


def vki_mine_sweep(k, path, hw, z0, z1, mi):
    """a bar of rectangular section (half width hw, z0..z1) swept along path [(x, y, tx, ty)] (unit tangents), both
    ends capped. -> verts"""
    bm = k.bm
    rings = []
    for (x, y, tx, ty) in path:
        nx, ny = -ty, tx
        rings.append([bm.verts.new((x - hw * nx, y - hw * ny, z0)), bm.verts.new((x + hw * nx, y + hw * ny, z0)),
                      bm.verts.new((x + hw * nx, y + hw * ny, z1)), bm.verts.new((x - hw * nx, y - hw * ny, z1))])
    fs = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for A, B in zip(rings[:-1], rings[1:]):
        for j in range(4):
            fs.append(bm.faces.new((A[j], A[(j + 1) % 4], B[(j + 1) % 4], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.smooth = False
    k.project(fs, mi)
    return [v for r in rings for v in r]


def vki_mine_rails(k, path, dark=0.30):
    """the two rails along a centreline path [(x, y, tx, ty)]: an oak rail and its iron strap at +-VKI_MINE_HG"""
    hw, z0, z1 = VKI_MINE_RAIL
    sw, s0, s1 = VKI_MINE_STRAP
    for s in (-1.0, 1.0):
        p2 = [(x - s * VKI_MINE_HG * ty, y + s * VKI_MINE_HG * tx, tx, ty) for (x, y, tx, ty) in path]
        k.set_dark(vki_mine_sweep(k, p2, hw, z0, z1, WOOD), dark)
        vki_mine_sweep(k, p2, sw, s0, s1, STEEL)


def vki_mine_sleeper(k, x, y, yaw, seed, L=None):
    """one sleeper centred at (x, y), its length along yaw, laid by hand: turned +-3 deg, shifted along itself, sunk up
    to 6 mm. -> verts"""
    rnd = random.Random(seed)
    hl, hw, z0, z1 = VKI_MINE_SLEEPER
    L = L or 2 * hl * rnd.uniform(0.94, 1.04)
    a = yaw + math.radians(rnd.uniform(-3.0, 3.0))
    sh = rnd.uniform(-0.02, 0.02)
    c = (x + sh * math.cos(a), y + sh * math.sin(a), (z0 + z1) / 2 - rnd.uniform(0.0, 0.006))
    vs = list(set(k.box(c, (L, 2 * hw * rnd.uniform(0.9, 1.08), z1 - z0), WOOD, rot=(0.0, 0.0, a), bevel=0.0)))
    k.set_dark(vs, rnd.uniform(0.30, 0.50))
    return vs


def vki_mine_track_meta(k, kind):
    k.slot_mats[WOOD] = VKI_MINE_WOOD
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none", vki_wall_anchor=1,
                  vki_track={"kind": kind, "conn": VKI_MINE_TRACK_BASE[kind], "gauge": round(2 * VKI_MINE_HG, 3),
                             "top": VKI_MINE_TOP},
                  vki_place_rule="a track tile (1.5 m): origin on a track point, rotation 90 k -- vki_mine_tracks lays "
                                 "them from R['tracks']; connections at rotation 0 in vki_track conn (N 1, E 2, S 4, "
                                 "W 8); walkable")


def vki_mine_track_straight(k):
    """a straight 1.5 m of track along local y: four sleepers, two rails"""
    for i in range(4):
        vki_mine_sleeper(k, 0.0, -0.5625 + 0.375 * i, 0.0, 11 + i)
    vki_mine_rails(k, [(0.0, -0.75, 0.0, 1.0), (0.0, 0.75, 0.0, 1.0)])
    vki_mine_track_meta(k, "Straight")


def vki_mine_track_end(k):
    """the end of a line: rails from the south edge into a buffer stop -- a heavy timber across them (y 0.40-0.58) with
    an iron plate on its face, braced by two posts behind it, on a sleeper of its own"""
    for i in range(3):
        vki_mine_sleeper(k, 0.0, -0.5625 + 0.375 * i, 0.0, 21 + i)
    vki_mine_sleeper(k, 0.0, 0.49, 0.0, 24, L=1.10)
    vki_mine_rails(k, [(0.0, -0.75, 0.0, 1.0), (0.0, 0.44, 0.0, 1.0)])
    k.set_dark(vki_adv_box(k, -0.48, 0.48, 0.40, 0.58, 0.035, 0.33, WOOD, bev=0.012), 0.2)
    for x in (-0.30, 0.30):
        k.set_dark(vki_adv_box(k, x - 0.07, x + 0.07, 0.575, 0.71, -0.01, 0.40, WOOD, bev=0.01), 0.3)
    k.box((0.0, 0.395, 0.20), (0.40, 0.012, 0.08), IRON, bevel=0.0)
    vki_mine_track_meta(k, "End")


def vki_mine_track_curve(k):
    """a quarter turn of radius 0.75 about the tile's south-east corner: in at the south edge, out at the east edge;
    three sleepers laid radially"""
    cx, cy, R_ = 0.75, -0.75, 0.75
    N = 6
    path = []
    for i in range(N + 1):
        th = math.pi - 0.5 * math.pi * i / N
        path.append((cx + R_ * math.cos(th), cy + R_ * math.sin(th), math.sin(th), -math.cos(th)))
    for i, d in enumerate((15.0, 45.0, 75.0)):
        th = math.pi - math.radians(d)
        vki_mine_sleeper(k, cx + R_ * math.cos(th), cy + R_ * math.sin(th), th, 31 + i)
    vki_mine_rails(k, path)
    vki_mine_track_meta(k, "Curve")


def vki_mine_track_turntable(k, kind):
    """a junction: a timber turntable (a planked disc 1.40 across, an iron band round its edge, an iron pivot boss) with
    a rail pair across it N-S -- running on to the tile edge where the arm connects -- and rail stubs out to the edge
    on the connected E / W sides, each on a short sleeper"""
    R_ = 0.70
    conn = VKI_MINE_TRACK_BASE[kind]
    B = VKI_MINE_BITS
    vs, fs = vki_home_lathe(k, [(R_, -0.016), (R_, 0.040), (R_ - 0.025, 0.052), (0.0, 0.052)], segs=12, mi=PLANKS,
                            smooth=False)
    band = [f for f in fs if abs(f.normal.z) < 0.5]
    for f in band:
        f.material_index = IRON
    k.project([f for f in fs if f not in band], PLANKS)
    k.set_dark(vs, 0.15)
    _cyl(k, (0.0, 0.0, 0.058), 0.07, 0.06, 0.016, 8, IRON)
    y0 = -0.75 if conn & B["S"] else -0.62
    y1 = 0.75 if conn & B["N"] else 0.62
    vki_mine_rails(k, [(0.0, y0, 0.0, 1.0), (0.0, y1, 0.0, 1.0)])
    for side, d in (("E", 1.0), ("W", -1.0)):
        if not conn & B[side]:
            continue
        vki_mine_rails(k, [(0.60 * d, 0.0, d, 0.0), (0.75 * d, 0.0, d, 0.0)])
        k.set_dark(vki_adv_box(k, 0.69 * d - 0.05, 0.69 * d + 0.05, -0.45, 0.45, -0.012, 0.036, WOOD), 0.4)
    vki_mine_track_meta(k, kind)


def vki_mine_track_tee(k): vki_mine_track_turntable(k, "Tee")
def vki_mine_track_cross(k): vki_mine_track_turntable(k, "Cross")


# ---------------------------------------------------------------- the lantern, timber materials
def vki_mine_lantern(k, x, y, z):
    """a small caged lantern hanging from a hook at (x, y, z): a hanger, a pyramid roof, iron top and bottom plates,
    glowing panes (vki_heat) behind four corner bars. -> the light socket's position (the panes' centre)"""
    k.box((x, y, z - 0.025), (0.012, 0.012, 0.05), IRON, bevel=0.0)
    vki_home_lathe(k, [(0.082, 0.0), (0.0, 0.055)], c=(x, y, z - 0.105), segs=4, mi=IRON, smooth=False,
                   a0=math.pi / 4)
    k.box((x, y, z - 0.115), (0.13, 0.13, 0.02), IRON, bevel=0.0)
    gv = list(set(k.box((x, y, z - 0.195), (0.09, 0.09, 0.14), GLOW, bevel=0.0)))
    k.set_heat(gv, 0.9)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            k.box((x + sx * 0.05, y + sy * 0.05, z - 0.195), (0.014, 0.014, 0.15), IRON, bevel=0.0)
    k.box((x, y, z - 0.275), (0.12, 0.12, 0.02), IRON, bevel=0.0)
    return (x, y, z - 0.195)


def vki_mine_lamp_meta(p, w=VKI_MINE_LAMP_W, rng=6.0):
    """the vki_lights / vki_fx entries of a lantern whose panes' centre is p"""
    return dict(vki_lights=[vki_dpr_light("lantern", p, w, VKI_MINE_LAMP_COL, rng, 0.06, shadows=0)],
                vki_fx=[dict(fx="lantern", pos=[round(c, 3) for c in p], scale=0.4)])


def vki_mine_timber_mats(k):
    k.slot_mats[WOOD] = VKI_MINE_TIMBER
    k.slot_mats[PLANKS] = "Planks"


# ---------------------------------------------------------------- carts
def vki_mine_tub(k, C, cy=0.0):
    """an open tub of planks, its long axis along local y: the outer walls battered out from the bottom (wb x L - 0.10)
    to the rim (wt x L), C["wall"] thick, an inner floor 5 cm up. -> (outer bottom ring, outer top ring) as coordinates"""
    hl = C["L"] / 2
    lb = hl - 0.05
    zb, zt, w = C["zb"], C["zt"], C["wall"]
    wb, wt = C["wb"], C["wt"]
    f_ = (zt - zb - 0.05) / (zt - zb)
    ixb, iyb = (wt - w) - (wt - wb) * f_, (hl - w) - (hl - lb) * f_
    bm = k.bm

    def ring(hx, hy, z):
        return [bm.verts.new((-hx, cy - hy, z)), bm.verts.new((hx, cy - hy, z)), bm.verts.new((hx, cy + hy, z)),
                bm.verts.new((-hx, cy + hy, z))]
    ob, ot, it, ib = ring(wb, lb, zb), ring(wt, hl, zt), ring(wt - w, hl - w, zt), ring(ixb, iyb, zb + 0.05)
    fs = [bm.faces.new(ob[::-1]), bm.faces.new(ib)]
    for A, B_ in ((ob, ot), (ot, it), (it, ib)):
        for j in range(4):
            fs.append(bm.faces.new((A[j], A[(j + 1) % 4], B_[(j + 1) % 4], B_[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.smooth = False
    k.project(fs, PLANKS)
    for v in ib + it:
        k.set_dark([v], 0.35)
    return [v.co.copy() for v in ob], [v.co.copy() for v in ot]


def vki_mine_cart_body(k):
    """the cart upright on the rails, its long axis along local y: the tub, corner irons and a rim band, two axles and
    four iron wheels standing on the rail tops (x +-0.30), axle boxes, a push bar at the +y end, couplings. No
    icospheres (the tipped cart turns it over)."""
    C = VKI_MINE_CART
    ob, ot = vki_mine_tub(k, C)
    for j in range(4):
        a, b = ob[j], ot[j]
        d = Vector((math.copysign(0.008, a.x), math.copysign(0.008, a.y), 0.0))
        vki_dpr_rod(k, a + d, b + d, 0.045, IRON, d=0.045)
    for j in range(4):
        a, b = ot[j], ot[(j + 1) % 4]
        e = (b - a).normalized()
        n = Vector((e.y, -e.x, 0.0))
        if n.dot(a) < 0:
            n = -n
        vki_dpr_rod(k, a + n * 0.010 - e * 0.012 + Vector((0, 0, -0.033)), b + n * 0.010 + e * 0.012 + Vector((0, 0, -0.033)),
                    0.022, IRON, d=0.060 if j % 2 == 0 else 0.056)
    wz = VKI_MINE_TOP + C["wr"]
    for y in (-C["wy"], C["wy"]):
        vki_dpr_rod(k, (-0.37, y, wz), (0.37, y, wz), 0.045, IRON)
        for x in (-VKI_MINE_HG, VKI_MINE_HG):
            _cyl(k, (x, y, wz), C["wr"], C["wr"], 0.05, 10, IRON, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
            k.set_dark(vki_adv_box(k, x * 0.80 - 0.04, x * 0.80 + 0.04, y - 0.07, y + 0.07, wz, C["zb"] + 0.012, WOOD),
                       0.3)
    hl = C["L"] / 2
    for x in (-0.20, 0.20):
        vki_dpr_rod(k, (x, hl - 0.03, 0.70), (x, hl + 0.17, 0.72), 0.04, WOOD, d=0.045)
    vki_dpr_rod(k, (-0.25, hl + 0.17, 0.72), (0.25, hl + 0.17, 0.72), 0.05, WOOD, d=0.05)
    for s in (-1.0, 1.0):
        k.box((0.0, s * (hl - 0.02), C["zb"] + 0.07), (0.07, 0.07, 0.045), IRON, bevel=0.0)


def vki_mine_cart_meta(k, colliders, **kw):
    k.slot_mats[WOOD] = VKI_MINE_WOOD
    k.slot_mats[PLANKS] = "Planks"
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_CaveRock"
    vki_dpr_gold_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_collider=colliders, **kw)


def vki_mine_cart(k):
    """Mine_Cart: an empty cart on the rails (local y along the track; place it on a track tile's line)"""
    vki_mine_cart_body(k)
    vki_mine_cart_meta(k, [[0.0, 0.07, 0.45, 0.72, 1.30, 0.90]], vki_cart={"load": "empty"},
                       vki_place_rule="on the track: origin on its centreline, rotation along it")


def vki_mine_ore_lumps(k, pts, seed, gold=0.5, iron=0.0, mi=VKI_STONE_BLOCK_IN):
    """ore lumps at pts [(x, y, z, r)] resting on z: dark rock, some flecked with gold (a fraction `gold` of them),
    some rust-red iron ore on the CAP slot (a fraction `iron`)"""
    rnd = random.Random(seed)
    for i, (x, y, z, r) in enumerate(pts):
        is_iron = rnd.random() < iron
        vs = vki_deb_rock(k, x, y, r, seed * 7 + i, flat=0.72, mi=VKI_CAP if is_iron else mi, z=z,
                          dark=0.15 if is_iron else 0.32)
        top = [v.co.copy() for v in vs if v.co.z > z + r * 0.45]
        if top and not is_iron and rnd.random() < gold:
            for p in rnd.sample(top, min(2, len(top))):
                k.box(tuple(p), (0.024, 0.02, 0.018), VKI_DPR_GOLD, rot=(rnd.uniform(0, 1), 0.3, rnd.uniform(0, 3)),
                      bevel=0.0)


def vki_mine_cart_ore(k):
    """Mine_Cart_Ore: the cart heaped with ore -- a mound of broken rock inside the rim, lumps on it, gold flecks"""
    C = VKI_MINE_CART
    vki_mine_cart_body(k)
    rx, ry, h, zc = C["wt"] - 0.05, C["L"] / 2 - 0.06, 0.20, C["zt"] - 0.10
    k.set_dark(vki_dpr_mound(k, (0.0, 0.0, zc), rx, ry, h, VKI_STONE_BLOCK_IN, nr=2, ns=12, seed=2201, wob=0.08,
                             bump=0.25, smooth=False), 0.38)
    rnd = random.Random(2202)
    pts = []
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.3, 0.3); t = rnd.uniform(0.15, 0.75)
        x, y = math.cos(a) * rx * t, math.sin(a) * ry * t
        pts.append((x, y, zc + h * (1 - t * t) ** 0.7 - 0.03, rnd.uniform(0.05, 0.085)))
    vki_mine_ore_lumps(k, pts, 2203, gold=0.6)
    vki_mine_cart_meta(k, [[0.0, 0.07, 0.47, 0.72, 1.30, 0.94]], vki_cart={"load": "ore"},
                       vki_place_rule="on the track: origin on its centreline, rotation along it")


def vki_mine_cart_tipped(k):
    """Mine_Cart_Tipped: a cart gone off the rails, lying on its side (turned 84 deg about its length, its mouth toward
    local +x), its ore spilt in a fan before the mouth"""
    before = set(k.bm.verts)
    vki_mine_cart_body(k)
    vs = [v for v in k.bm.verts if v not in before]
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Rotation(math.radians(6.0), 4, "Z") @
                        Matrix.Rotation(math.radians(84.0), 4, "Y"))
    zmin = min(v.co.z for v in vs)
    bmesh.ops.translate(k.bm, verts=vs, vec=(-0.55, 0.0, -zmin - 0.008))
    k.bm.normal_update()
    box = vki_poi_aabb(vs)
    k.set_dark(vki_dpr_mound(k, (0.62, 0.0, 0.0), 0.42, 0.55, 0.10, VKI_STONE_BLOCK_IN, z0=0.001, nr=2, ns=12,
                             seed=2301, wob=0.2, bump=0.3, smooth=False), 0.38)
    rnd = random.Random(2302)
    pts = []
    for i in range(10):
        x, y = rnd.uniform(0.20, 1.05), rnd.uniform(-0.55, 0.55)
        t = math.hypot((x - 0.62) / 0.42, y / 0.55)
        pts.append((x, y, 0.10 * max(0.0, 1 - t * t) ** 0.7 * 0.9 - 0.005, rnd.uniform(0.045, 0.08)))
    vki_mine_ore_lumps(k, pts, 2303, gold=0.5)
    vki_mine_cart_meta(k, [box], vki_cart={"load": "spilt"},
                       vki_place_rule="off the track, anywhere on open floor; the spilt ore (local +x) is walkable")


# ---------------------------------------------------------------- timbering
def vki_mine_set_frame(k, seed=3, dark=0.15):
    """a timber set across local x: two posts (0.20 x 0.21) battered in 6 cm from the floor (+-1.30) to the cap
    (+-1.24) on foot blocks, the cap (3.00 x 0.24 x 0.24, z 2.30-2.54), a blocking wedge on it over each post (head
    boards across the cap read as ladder rungs from the game camera)"""
    rnd = random.Random(seed)
    for s in (-1.0, 1.0):
        k.set_dark(vki_dpr_rod(k, (s * 1.30, 0.0, -0.03), (s * 1.24, 0.0, 2.33), 0.20, WOOD, d=0.21, bevel=0.012),
                   dark + 0.10 * rnd.random())
        k.set_dark(vki_adv_box(k, s * 1.30 - 0.15, s * 1.30 + 0.15, -0.13, 0.13, -0.02, 0.04, WOOD), dark + 0.25)
    k.set_dark(vki_adv_box(k, -1.50, 1.50, -0.12, 0.12, 2.30, 2.54, WOOD, bev=0.015), dark)
    for s in (-1.0, 1.0):
        x = s * 1.14
        k.set_dark(vki_prism(k, [(x - 0.10, 2.535), (x + 0.10, 2.535), (x + 0.06, 2.61), (x - 0.06, 2.61)], -0.10,
                             0.10, WOOD, axis="y")[0], dark + 0.1)


def vki_mine_set(k, lamp=False):
    """Mine_Set / Mine_Set_Lamp: a timber set spanning a gallery two cells wide (local x across it); the lamp set hangs
    a lantern from a spike in its +x post's inner face (1.92 m)"""
    vki_mine_set_frame(k)
    kw = {}
    if lamp:
        k.box((1.075, 0.0, 1.93), (0.16, 0.018, 0.018), IRON, bevel=0.0)
        kw = vki_mine_lamp_meta(vki_mine_lantern(k, 1.02, 0.0, 1.92))
    vki_mine_timber_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_cam_fade=1, vki_wall_anchor=1,
                  vki_collider=[[-1.27, 0.0, 1.15, 0.26, 0.24, 2.30], [1.27, 0.0, 1.15, 0.26, 0.24, 2.30]],
                  vki_place_rule="across a gallery two cells wide: origin on its centre line, local x across it "
                                 "(rotation 0 in a N-S gallery, 90 in an E-W one), hug off; the posts may be let "
                                 "into the rock face (vki_wall_anchor)", **kw)


def vki_mine_set_plain(k): vki_mine_set(k, False)
def vki_mine_set_lamp(k): vki_mine_set(k, True)


def vki_mine_set_broken(k):
    """Mine_Set_Broken: a set that gave way -- the -x post still standing, leaning out; the +x post kicked out, its
    stump standing splintered and its upper part lying along the gallery; the cap snapped, its -x half still on the
    post's head sagging to the break at 1.1 m, the +x half down to the floor; rocks fallen from the roof on it, the
    head boards thrown down. A way stays open on the -x side (0.9 m, under the sagging cap)"""
    rnd = random.Random(41)
    k.set_dark(vki_dpr_rod(k, (-1.30, 0.0, -0.03), (-1.40, 0.03, 2.31), 0.20, WOOD, d=0.21, bevel=0.012), 0.22)
    k.set_dark(vki_adv_box(k, -1.45, -1.15, -0.13, 0.13, -0.02, 0.04, WOOD), 0.4)
    k.set_dark(vki_dpr_rod(k, (1.30, 0.0, -0.03), (1.29, 0.0, 0.52), 0.20, WOOD, d=0.21, bevel=0.012), 0.25)
    k.set_dark(vki_adv_box(k, 1.15, 1.45, -0.13, 0.13, -0.02, 0.04, WOOD), 0.4)
    vki_prism(k, [(1.20, 0.515), (1.39, 0.515), (1.33, 0.71), (1.26, 0.62)], -0.095, 0.095, WOOD, axis="y")
    k.set_dark(vki_dpr_rod(k, (0.95, -1.05, 0.10), (0.62, 0.72, 0.10), 0.20, WOOD, d=0.21, roll=0.3), 0.3)
    k.set_dark(vki_dpr_rod(k, (-1.52, 0.0, 2.43), (0.20, 0.03, 1.10), 0.24, WOOD, d=0.24, bevel=0.012), 0.2)
    k.set_dark(vki_dpr_rod(k, (0.16, 0.0, 1.06), (1.42, -0.14, 0.12), 0.235, WOOD, d=0.235, bevel=0.012), 0.25)
    for i, (a, b) in enumerate((((0.14, 0.05, 1.12), (0.36, 0.09, 1.02)), ((0.18, -0.06, 1.05), (0.02, -0.10, 1.20)),
                                ((0.20, 0.02, 1.00), (0.34, 0.00, 0.86)))):
        vki_dpr_rod(k, a, b, 0.03, WOOD, d=0.025 + 0.003 * i)                  # splinters at the break
    for i, (x, y, r) in enumerate(((0.95, 0.15, 0.22), (0.55, -0.45, 0.17), (1.25, 0.55, 0.14), (0.25, 0.40, 0.12),
                                   (-0.15, -0.30, 0.09), (1.10, -0.60, 0.11))):
        vki_deb_rock(k, x, y, r, 4110 + i, flat=0.75, mi=VKI_STONE_BLOCK_IN, dark=0.2)
    for i, (x, y, yaw) in enumerate(((-0.45, 0.55, 0.3), (0.35, -0.85, 1.9), (-0.85, -0.35, 2.6))):
        vki_deb_plank(k, x, y, 0.016 + 0.002 * i, 0.66, 0.14, 0.03, yaw, 4120 + i, mi=PLANKS)
    vki_mine_timber_mats(k)
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_CaveRock"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_cam_fade=1, vki_wall_anchor=1,
                  vki_collider=[[-1.35, 0.0, 1.15, 0.28, 0.26, 2.30], [0.75, -0.05, 0.45, 1.55, 1.90, 0.90]],
                  vki_place_rule="like Mine_Set (local x across the gallery); the way past it is on its -x side")


# ---------------------------------------------------------------- ore veins
VKI_MINE_VEIN_LUMPS = ((0.0, 0.26, 0.76, 0.86, 0.40, 0.84, 3),         # centre x, y, z; radii x, y, z; subdivisions
                       (-0.70, 0.22, 0.34, 0.46, 0.34, 0.40, 2),
                       (0.74, 0.22, 0.30, 0.42, 0.32, 0.36, 2))
VKI_MINE_SEAMS = {"gold": ((0.62, 0.30, 0.11, -1.05, 1.00), (1.12, -0.22, 0.07, -0.62, 0.58)),    # z at x 0, slope,
                  "iron": ((0.50, 0.20, 0.17, -1.05, 1.05), (1.14, 0.06, 0.11, -0.66, 0.66)),      # width, x from, to
                  "crystal": ((0.84, 0.22, 0.09, -0.80, 0.80),)}
VKI_MINE_SEAM_MATS = {"gold": "M_VKI_Quartz", "iron": "M_VKI_IronOre", "crystal": "M_VKI_Quartz"}


def vki_mine_vein_front(x, z):
    """the vein's front at (x, z): the frontmost (least y) point on its lumps' ellipsoids and the outward normal there,
    or None off them"""
    best = None
    for (cx, cy, cz, a, b, c, _) in VKI_MINE_VEIN_LUMPS:
        u, w = (x - cx) / a, (z - cz) / c
        s = 1.0 - u * u - w * w
        if s <= 0.03:
            continue
        y = cy - b * math.sqrt(s)
        if best is None or y < best[0].y:
            best = (Vector((x, y, z)), Vector(((x - cx) / (a * a), (y - cy) / (b * b), (z - cz) / (c * c))).normalized())
    return best


def vki_mine_seam(k, seam, mi, seed, n=14, t=0.045):
    """a seam over the vein's front: a flat band (t thick, 0.6 t proud of the lumps' ellipsoids) along the wobbling curve
    z = z0 + slope x from x0 to x1, its width swelling and pinching and tapering to its ends; a band per stretch on the
    lumps. Painting the lumps' faces instead gave a zigzag of triangles, like teeth. -> [(point on its face, normal)]"""
    z0, sl, w, xa, xb = seam
    rnd = random.Random(seed)
    ph = rnd.uniform(0.0, 6.3)
    runs, run = [], []
    for i in range(n + 1):
        x = xa + (xb - xa) * i / n
        f = vki_mine_vein_front(x, z0 + sl * x + 0.06 * math.sin(4.3 * x + ph))
        if f is None:
            if len(run) > 1:
                runs.append(run)
            run = []
        else:
            run.append(f)
    if len(run) > 1:
        runs.append(run)
    out = []
    bm = k.bm
    for run in runs:
        m = len(run)
        rings = []
        for j, (p, nn) in enumerate(run):
            T = (run[min(j + 1, m - 1)][0] - run[max(j - 1, 0)][0]).normalized()
            b = nn.cross(T).normalized()
            wj = w * (0.25 + 0.75 * math.sin(math.pi * (j + 0.5) / m) ** 0.6) * rnd.uniform(0.8, 1.15)
            rings.append([bm.verts.new(p - b * wj / 2 - nn * 0.4 * t), bm.verts.new(p + b * wj / 2 - nn * 0.4 * t),
                          bm.verts.new(p + b * wj / 2 + nn * 0.6 * t), bm.verts.new(p - b * wj / 2 + nn * 0.6 * t)])
            out.append((p + nn * 0.6 * t, nn))
        fs = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
        for A, B_ in zip(rings[:-1], rings[1:]):
            for q in range(4):
                fs.append(bm.faces.new((A[q], A[(q + 1) % 4], B_[(q + 1) % 4], B_[q])))
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        bm.normal_update()
        for f in fs:
            f.smooth = False
        k.project(fs, mi)
    return out


def vki_mine_vein(k, ore):
    """an ore vein in a rock face (its back at local +y, buried to +0.66): three lumps of dark cave rock bulging 0.1-0.14
    m out of the face -- a broad one (1.7 wide, 1.6 high) flanked by two low ones -- crossed by seams, flat bands 2.7 cm
    proud of the rock that swell and pinch (vki_mine_seam): gold -- white quartz flecked with gold; iron -- rust-red bands
    studded with nodules of ore; crystal -- a quartz seam with clusters of glowing crystals growing out of it, a cold
    light. Broken ore lies at its foot."""
    rnd = random.Random(vki_seed("Vein|" + ore))
    for (x, y, z, a, b, c, sub) in VKI_MINE_VEIN_LUMPS:
        vs = vki_home_ico(k, (x, y, z), 1.0, VKI_STONE_BLOCK_IN, scale=(a, b, c), sub=sub, jit=0.018,
                          seed=rnd.randint(0, 9999), smooth=False)
        k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN)
        for v in vs:
            k.set_dark([v], 0.28 + 0.30 * vki_smoothstep(0.45, 0.0, v.co.z))
    hits = []
    for j, seam in enumerate(VKI_MINE_SEAMS[ore]):
        hits += vki_mine_seam(k, seam, VKI_CAP, 5400 + 17 * j + len(ore))
    if ore == "gold":
        for p, n in hits[1::2]:
            for m in range(2):
                q = p + Vector((rnd.uniform(-0.03, 0.03), 0.0, rnd.uniform(-0.03, 0.03)))
                k.box(tuple(q - n * 0.008), (0.03, 0.026, 0.024), VKI_DPR_GOLD,
                      rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)), bevel=0.0)
    elif ore == "iron":
        for p, n in hits[1::2]:
            vs = vki_home_ico(k, tuple(p + n * 0.01), rnd.uniform(0.05, 0.08), VKI_CAP, scale=(1.0, 0.75, 0.8), sub=1,
                              jit=0.01, seed=rnd.randint(0, 9999), smooth=False)
            k.project(vki_faces_of(vs), VKI_CAP)
    else:
        for p, n in hits[1::2]:
            for m in range(rnd.choice((2, 3))):
                d = (n + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.15, 0.15), rnd.uniform(0.2, 0.8)))).normalized()
                h, r = rnd.uniform(0.30, 0.62), rnd.uniform(0.045, 0.075)
                _cyl(k, tuple(p + d * (h / 2 - 0.05)), r, 0.008, h, 6, MUSH_GLOW,
                     rot=d.to_track_quat("Z", "Y").to_matrix().to_4x4())
    pts = [(-0.45, -0.40, 0.0, 0.09), (-0.12, -0.48, 0.0, 0.07), (0.22, -0.42, 0.0, 0.08), (0.52, -0.34, 0.0, 0.06),
           (0.04, -0.31, 0.0, 0.10)]
    if ore == "crystal":
        vki_mine_ore_lumps(k, pts[::2], 5301, gold=0.0)
        for i, (x, y, a) in enumerate(((-0.25, -0.42, 0.4), (0.18, -0.50, 2.1), (0.40, -0.40, 1.2))):
            d = Vector((math.cos(a), math.sin(a), 0.12)).normalized()
            _cyl(k, (x, y, 0.035), 0.035, 0.006, 0.26, 6, MUSH_GLOW,
                 rot=d.to_track_quat("Z", "Y").to_matrix().to_4x4())            # broken crystals lying
    else:
        vki_mine_ore_lumps(k, pts, 5302, gold=0.7 if ore == "gold" else 0.0, iron=0.6 if ore == "iron" else 0.0)
    vki_cav_rock_mats(k)
    k.slot_mats[VKI_CAP] = VKI_MINE_SEAM_MATS[ore]
    vki_dpr_gold_mats(k)
    kw = {}
    if ore == "crystal":
        kw["vki_lights"] = [dict(type="POINT", role="crystal", pos=[0.0, -0.55, 1.05], w=130.0,
                                 color=VKI_CAV_CRYSTAL_COL, range=6.0, flicker=0, shadows=0, radius=0.10)]
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.95, 0.0]], vki_nav="block", vki_wall_anchor=1,
                  vki_collider=[[0.0, 0.12, 0.8, 1.95, 0.95, 1.6]], vki_vein={"ore": ore},
                  vki_place_rule="against a rock face: its back (local +y) into the rock, hug off; let into the face "
                                 "(vki_wall_anchor); the use point 0.95 m in front (where a miner works it)", **kw)


def vki_mine_vein_gold(k): vki_mine_vein(k, "gold")
def vki_mine_vein_iron(k): vki_mine_vein(k, "iron")
def vki_mine_vein_crystal(k): vki_mine_vein(k, "crystal")


# ---------------------------------------------------------------- the shaft
def vki_mine_shaft(k):
    """Pit_Shaft_300x300 (2 x 2 cells, origin at its min corner): a floor strip round its edge, a collar of four heavy
    timbers round the opening (0.42-2.58: 2.16 m square), cribbing -- courses of timbers, crossing at the corners like
    a log cabin -- lining the shaft into the dark (black by -2.6, a black floor at -3.2), corner posts, and a ladder
    down the north side whose stiles stand 0.9 m above the collar"""
    S, o0, o1 = 3.0, 0.42, 2.58
    for (x0, x1, y0, y1) in ((0.0, 3.0, 0.0, 0.14), (0.0, 3.0, 2.86, 3.0), (0.0, 0.14, 0.14, 2.86),
                             (2.86, 3.0, 0.14, 2.86)):
        vki_adv_box(k, x0, x1, y0, y1, -0.06, 0.0, VKI_FLOOR)
    for (x0, x1, y0, y1, z0, z1) in ((0.10, 2.90, 0.12, o0, -0.03, 0.21), (0.10, 2.90, o1, 2.88, -0.03, 0.21),
                                     (0.12, o0, o0, o1, -0.04, 0.19), (o1, 2.88, o0, o1, -0.04, 0.19)):
        k.set_dark(vki_adv_box(k, x0, x1, y0, y1, z0, z1, WOOD, bev=0.02), 0.22)
    rnd = random.Random(61)
    for i in range(11):
        z1 = -0.06 - 0.27 * i
        z0 = z1 - 0.24
        dk = 0.25 + 0.72 * vki_smoothstep(-0.3, -2.5, (z0 + z1) / 2)
        ns_long = i % 2 == 0                                   # N / S courses cross the corners on even courses
        for side in "NSEW":
            j = rnd.uniform(-0.012, 0.012)
            if side in "NS":
                xa, xb = (o0 - 0.16, o1 + 0.16) if ns_long else (o0, o1)
                ya, yb = (o0 - 0.18 + j, o0 + j) if side == "S" else (o1 - j, o1 + 0.18 - j)
            else:
                ya, yb = (o0 - 0.16, o1 + 0.16) if not ns_long else (o0, o1)
                xa, xb = (o0 - 0.18 + j, o0 + j) if side == "W" else (o1 - j, o1 + 0.18 - j)
            k.set_dark(vki_adv_box(k, xa, xb, ya, yb, z0 + 0.004 * (side in "EW"), z1 - 0.004 * (side in "EW"), WOOD),
                       dk)
    for (x, y) in ((o0 + 0.075, o0 + 0.075), (o1 - 0.075, o0 + 0.075), (o1 - 0.075, o1 - 0.075),
                   (o0 + 0.075, o1 - 0.075)):                              # 1 cm off the cribbing's faces (T5S)
        k.set_dark(vki_adv_box(k, x - 0.065, x + 0.065, y - 0.065, y + 0.065, -3.05, -0.05, WOOD), 0.75)
    vki_adv_box(k, o0, o1, o0, o1, -3.24, -3.20, VOID)
    for x in (1.25, 1.75):                                                         # the ladder
        vs = vki_adv_box(k, x - 0.025, x + 0.025, o1 - 0.09, o1 - 0.02, -2.95, 0.92, WOOD)
        for v in vs:
            k.set_dark([v], 0.2 + 0.75 * vki_smoothstep(-0.3, -2.5, v.co.z))
    for i in range(13):
        z = 0.62 - 0.30 * i
        vs = vki_adv_box(k, 1.235, 1.765, o1 - 0.075, o1 - 0.04, z - 0.018, z + 0.018, WOOD)
        k.set_dark(vs, 0.2 + 0.75 * vki_smoothstep(-0.3, -2.5, z))
    k.slot_mats[VKI_FLOOR] = "EarthDamp"
    vki_mine_timber_mats(k)
    k.meta.update(vki_class="pit", vki_covers_floor=[0.0, 0.0, S, S], vki_nav="block",
                  vki_collider=[[1.5, 1.5, 0.5, o1 - o0, o1 - o0, 1.0]],
                  vki_shaft={"depth": 3.2, "opening": [o0, o0, o1, o1]},
                  vki_place_rule="origin on a node (its min corner), rotation 0 (2 x 2 cells); POI_Treadwheel stands "
                                 "over it (origin on its centre, x + 1.5, y + 1.5)")


# ---------------------------------------------------------------- POI_Treadwheel: the shaft head
VKI_MINE_WHEEL = dict(x=-3.60, z=1.62, r=1.50, hw=0.50)        # the treadwheel: centre x, axle height, radius, half width
VKI_MINE_SHEAVE = dict(x=-0.42, z=3.25, r=0.42)               # the sheave: its east side over the shaft's centre


def vki_mine_treadwheel(k):
    """POI_Treadwheel -- the shaft head, origin on the centre of a Pit_Shaft_300x300 (the opening 2.16 m square, the
    collar to +-1.38): a headframe of two A-frames (y +-0.75, their feet on the collar's east and west timbers, tied at
    1.85 and 1.20) carrying the sheave (0.42 m) at 3.25 m; the rope from the sheave's east side straight down to the
    cage -- a timber cage hanging in the shaft at the landing, open to the south -- and from its west side to the drum
    of a great treadwheel (3.0 m across, 1.0 m wide, its plane facing the camera) on its trestles west of the shaft;
    on the landing south of the shaft a signal bell on its post and a kibble of ore, a lantern under the headframe.
    It carries the level's lift link (vki_link "lift"): the trigger on the landing, the spawn 2.45 m south."""
    W, SV = VKI_MINE_WHEEL, VKI_MINE_SHEAVE
    TX, TZ, TR, THW = W["x"], W["z"], W["r"], W["hw"]
    SX, SZ, SR = SV["x"], SV["z"], SV["r"]
    rx = Matrix.Rotation(math.pi / 2, 4, "X")
    ry = Matrix.Rotation(math.pi / 2, 4, "Y")
    # -- the treadwheel: two rims, six spokes a side, eighteen treads inside the rims, the hub and axle, the drum
    for s in (-1.0, 1.0):
        vs, _ = vki_home_hoop(k, (TX, s * (THW - 0.03), TZ), TR - 0.10, TR, 0.06, segs=16, mi=WOOD, rot=rx)
        k.set_dark(vs, 0.12)
        for i in range(6):
            a = 2 * math.pi * i / 6 + math.pi / 12
            k.set_dark(vki_dpr_rod(k, (TX + 0.12 * math.cos(a), s * (THW - 0.03), TZ + 0.12 * math.sin(a)),
                                   (TX + (TR - 0.06) * math.cos(a), s * (THW - 0.03), TZ + (TR - 0.06) * math.sin(a)),
                                   0.055 + 0.004 * (s > 0), WOOD, d=0.07), 0.2)
    for i in range(18):
        a = 2 * math.pi * (i + 0.5) / 18
        k.set_dark(list(set(k.box((TX + (TR - 0.12) * math.cos(a), 0.0, TZ + (TR - 0.12) * math.sin(a)),
                                  (0.04, 2 * THW - 0.02, 0.11), PLANKS, rot=(0.0, -a, 0.0), bevel=0.0))), 0.15)
    _cyl(k, (TX, 0.0, TZ), 0.16, 0.16, 2 * THW - 0.10, 10, WOOD, rot=rx)
    _cyl(k, (TX, 0.07, TZ), 0.055, 0.055, 2.18, 8, IRON, rot=rx)                 # the axle, y -1.02..1.16
    _cyl(k, (TX, 1.00, TZ), 0.20, 0.20, 0.16, 10, WOOD, rot=rx)                  # the drum
    vki_home_hoop(k, (TX, 1.00, TZ), 0.19, 0.245, 0.11, segs=10, mi=BURLAP, rot=rx)   # rope wound on it
    for y in (-0.88, 0.80):                                                       # the trestles
        for s in (-1.0, 1.0):
            k.set_dark(vki_dpr_rod(k, (TX + s * 0.85, y, -0.03), (TX + s * 0.05, y, TZ + 0.10), 0.12 + 0.004 * (s > 0),
                                   WOOD, d=0.13),
                       0.2)
        k.set_dark(vki_adv_box(k, TX - 0.60, TX + 0.60, y - 0.055, y + 0.055, 0.48, 0.60, WOOD), 0.25)
        k.set_dark(vki_adv_box(k, TX - 0.12, TX + 0.12, y - 0.08, y + 0.08, TZ - 0.02, TZ + 0.14, WOOD), 0.3)
    # -- the headframe: two A-frames over the shaft, ties, the sheave on its axle
    for y in (-0.75, 0.75):
        for s in (-1.0, 1.0):
            k.set_dark(vki_dpr_rod(k, (s * 1.28, y, 0.16), (SX + 0.04 * s, y, SZ + 0.02), 0.16 + 0.004 * (s > 0),
                                   WOOD, d=0.17, bevel=0.012), 0.15)
        zt = 1.85
        xw = -1.28 + (SX + 1.28) * (zt - 0.16) / (SZ - 0.14)
        xe = 1.28 + (SX - 1.28) * (zt - 0.16) / (SZ - 0.14)
        k.set_dark(vki_adv_box(k, xw - 0.06, xe + 0.06, y - 0.065, y + 0.065, zt - 0.07, zt + 0.07, WOOD), 0.2)
        k.set_dark(vki_adv_box(k, SX - 0.13, SX + 0.13, y - 0.10, y + 0.10, SZ - 0.10, SZ + 0.06, WOOD), 0.25)
    for s in (-1.0, 1.0):                                                          # ties along y at 1.20
        zt = 1.20
        x_ = s * 1.28 + (SX - s * 1.28) * (zt - 0.16) / (SZ - 0.14)
        k.set_dark(vki_adv_box(k, x_ - 0.055, x_ + 0.055, -0.82, 0.82, zt - 0.06 - 0.004 * (s > 0),
                               zt + 0.06 + 0.004 * (s > 0), WOOD), 0.2)
    vs, _ = vki_home_hoop(k, (SX, 0.0, SZ), SR - 0.07, SR, 0.08, segs=14, mi=WOOD, rot=rx)
    k.set_dark(vs, 0.15)
    for i in range(4):
        a = math.pi / 4 + math.pi / 2 * i
        vki_dpr_rod(k, (SX, 0.0, SZ), (SX + (SR - 0.04) * math.cos(a), 0.0, SZ + (SR - 0.04) * math.sin(a)),
                    0.05 + 0.004 * (i % 2), WOOD, d=0.05)
    _cyl(k, (SX, 0.0, SZ), 0.07, 0.07, 0.12, 8, IRON, rot=rx)
    _cyl(k, (SX, 0.0, SZ), 0.035, 0.035, 1.72, 6, IRON, rot=rx)
    # -- the rope: from the sheave's east side down to the cage, from its west side to the drum's top
    vki_dpr_rod(k, (SX + SR - 0.01, 0.0, SZ), (SX + SR - 0.01, 0.0, 2.42), 0.034, BURLAP)
    vki_dpr_rod(k, (SX - SR + 0.01, 0.0, SZ), (TX, 1.00, TZ + 0.24), 0.034, BURLAP)
    # -- the cage: a planked floor at the landing (z 0.13-0.19), four corner posts, a top frame, rails on three sides,
    # four chains to a ring on the rope
    cx0, cx1, cy0, cy1 = -0.50, 0.50, -0.45, 0.45
    k.set_dark(vki_adv_box(k, cx0, cx1, cy0, cy1, 0.13, 0.19, PLANKS), 0.1)
    for (x, y) in ((cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)):
        px, py = x - math.copysign(0.04, x), y - math.copysign(0.04, y)      # 5 mm inside the frame's faces (T5S)
        vki_adv_box(k, px - 0.035, px + 0.035, py - 0.035, py + 0.035, 0.17, 2.05, WOOD)
    for (x0, x1, y0, y1, z0, z1) in ((cx0, cx1, cy0, cy0 + 0.07, 1.98, 2.06), (cx0, cx1, cy1 - 0.07, cy1, 1.98, 2.06),
                                     (cx0, cx0 + 0.07, cy0 + 0.07, cy1 - 0.07, 1.985, 2.055),
                                     (cx1 - 0.07, cx1, cy0 + 0.07, cy1 - 0.07, 1.985, 2.055),
                                     (cx0, cx1, cy1 - 0.06, cy1 - 0.01, 0.98, 1.05),
                                     (cx0 + 0.01, cx0 + 0.06, cy0 + 0.07, cy1 - 0.07, 0.975, 1.045),
                                     (cx1 - 0.06, cx1 - 0.01, cy0 + 0.07, cy1 - 0.07, 0.975, 1.045)):
        vki_adv_box(k, x0, x1, y0, y1, z0, z1, WOOD)
    for (x, y) in ((cx0 + 0.04, cy0 + 0.04), (cx1 - 0.04, cy0 + 0.04), (cx1 - 0.04, cy1 - 0.04), (cx0 + 0.04, cy1 - 0.04)):
        vki_dpr_rod(k, (x, y, 2.06), (0.05 * x, 0.05 * y, 2.40), 0.022, IRON)       # (ends apart: T5S)
    k.box((0.0, 0.0, 2.42), (0.09, 0.09, 0.05), IRON, bevel=0.0)
    # -- the landing: the signal bell on its post, a kibble of ore, the lantern under the south A-frame's tie
    k.set_dark(vki_adv_box(k, 1.25, 1.35, -1.67, -1.57, -0.02, 1.92, WOOD), 0.25)
    vki_adv_box(k, 1.02, 1.25, -1.645, -1.595, 1.80, 1.85, WOOD)
    vki_home_lathe(k, [(0.085, 0.0), (0.075, 0.02), (0.05, 0.12), (0.0, 0.14)], c=(1.08, -1.62, 1.60), segs=10,
                   mi=VKI_DPR_GOLD, smooth=False)
    vki_adv_box(k, 1.075, 1.085, -1.625, -1.615, 1.74, 1.80, IRON)
    vki_dpr_rod(k, (1.08, -1.62, 1.60), (1.10, -1.64, 1.10), 0.012, BURLAP)
    vs, _ = vki_home_lathe(k, [(0.0, 0.0), (0.19, 0.0), (0.23, 0.40), (0.205, 0.40), (0.17, 0.05), (0.0, 0.05)],
                           c=(-0.95, -1.72, 0.0), segs=12, mi=WOOD, smooth=False)
    k.set_dark(vs, 0.2)
    for z in (0.08, 0.32):
        vki_home_hoop(k, (-0.95, -1.72, z), 0.187 + 0.1 * z, 0.207 + 0.1 * z, 0.04, segs=12, mi=IRON)
    k.set_dark(vki_dpr_mound(k, (-0.95, -1.72, 0.34), 0.17, 0.17, 0.10, VKI_STONE_BLOCK_IN, nr=2, ns=10, seed=6101,
                             wob=0.1, bump=0.3, smooth=False), 0.35)
    k.box((0.15, -0.75, 1.765), (0.012, 0.012, 0.03), IRON, bevel=0.0)
    lamp = vki_mine_lamp_meta(vki_mine_lantern(k, 0.15, -0.75, 1.75), w=110.0)
    vki_mine_timber_mats(k)
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_CaveRock"
    vki_dpr_gold_mats(k)
    vki_poi_meta(k, "The great treadwheel", "lift", "mine", "descend", use=[[0.0, -1.75, 0.0]],
                 colliders=[[TX, 0.07, 1.0, 2 * TR + 0.25, 2.20, 2.0], [-1.28, 0.0, 0.5, 0.22, 1.72, 1.0],
                            [1.28, 0.0, 0.5, 0.22, 1.72, 1.0], [1.30, -1.62, 0.5, 0.14, 0.14, 1.0],
                            [-0.95, -1.72, 0.25, 0.48, 0.48, 0.5]],
                 vki_spawn_local=[0.0, -2.45], vki_spawn_facing=180,
                 vki_trigger=[0.0, -1.58, 1.0, 1.0, 0.36, 2.0], vki_prompt_text="Ride the cage down",
                 vki_lift={"cage": [0.0, 0.0, 0.19], "sheave": [SX, 0.0, SZ], "wheel": [TX, 0.0, TZ]},
                 vki_place_rule="origin on the centre of a Pit_Shaft_300x300 (its min corner at x - 1.5, y - 1.5), "
                                "hug off; the treadwheel needs 5.3 m clear west of it and the landing 2.8 m south; "
                                "R['props'] opts {'link': id} makes it the level's lift", **lamp)


# ---------------------------------------------------------------- mine props
def vki_mine_tool(k, kind, a, b, rnd):
    """a tool from its foot a to its head end b (3-D): a pick (a pointed, curved iron head across the haft's top at b),
    a shovel (its blade from the foot a, the haft on from it), a sledge (a square iron head across the foot a) or an
    iron bar"""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    side = d.cross(Vector((0.0, 0.0, 1.0)))
    side = side.normalized() if side.length > 1e-6 else Vector((1.0, 0.0, 0.0))
    if kind == "bar":
        vki_dpr_rod(k, a, b, 0.028, IRON)
        return
    if kind == "shovel":
        vki_dpr_rod(k, a, a + d * 0.30, 0.22, IRON, d=0.012, roll=rnd.uniform(-0.05, 0.05))
        vki_dpr_rod(k, a + d * 0.26, b, 0.036, WOOD, d=0.034)
        return
    vki_dpr_rod(k, a, b, 0.036, WOOD, d=0.034)
    if kind == "pick":
        up = side.cross(d).normalized()
        pts = [b - side * 0.27 - up * 0.05, b - side * 0.13, b + up * 0.015, b + side * 0.13, b + side * 0.27 - up * 0.05]
        vki_poi_tube(k, pts, [0.004, 0.018, 0.026, 0.018, 0.004], IRON, segs=4, smooth=False)
    elif kind == "sledge":
        k.box(tuple(a), (0.22, 0.10, 0.10), IRON, rot=(0.0, 0.0, math.atan2(side.y, side.x)), bevel=0.01)


def vki_mine_orepile(k):
    """Mine_OrePile: a heap of ore (1.3 x 1.0, 0.45 high) -- broken rock over a mound of grit, lumps flecked with gold
    and rust-red iron ore -- a shovel stuck in it"""
    rx, ry, h = 0.62, 0.48, 0.40
    k.set_dark(vki_dpr_mound(k, (0.0, 0.0, 0.0), rx, ry, h, VKI_STONE_BLOCK_IN, z0=0.001, nr=3, ns=14, seed=2101,
                             wob=0.12, bump=0.2, smooth=False), 0.38)
    rnd = random.Random(2102)
    pts = []
    for i in range(12):
        a = 2 * math.pi * i / 12 + rnd.uniform(-0.2, 0.2); t = rnd.uniform(0.1, 0.95)
        x, y = math.cos(a) * rx * t, math.sin(a) * ry * t
        pts.append((x, y, h * (1 - t * t) ** 0.7 * 0.92 - 0.03, rnd.uniform(0.06, 0.11)))
    for i in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        pts.append((math.cos(a) * rx * 1.12, math.sin(a) * ry * 1.12, 0.0, rnd.uniform(0.04, 0.07)))
    vki_mine_ore_lumps(k, pts, 2103, gold=0.5, iron=0.25)
    vki_mine_tool(k, "shovel", (0.16, 0.02, 0.24), (0.48, -0.20, 1.10), rnd)
    vki_mine_cart_meta(k, [[0.0, 0.0, 0.25, 1.36, 1.06, 0.5]])
    k.slot_mats[VKI_CAP] = "M_VKI_IronOre"


def vki_mine_wheelbarrow(k):
    """Mine_Wheelbarrow: a barrow of planks -- its tray battered out -- on two shafts from the wheel at the front
    (local -y) back to the handles, two legs under the tray's back, a few ore lumps in it"""
    C = dict(L=0.80, wt=0.31, wb=0.24, zb=0.44, zt=0.70, wall=0.03)
    vki_mine_tub(k, C, cy=0.05)
    for x in (-0.22, 0.22):
        segs = (((x, -0.62, 0.20), (x, -0.30, 0.40)), ((x, -0.32, 0.40), (x, 0.46, 0.42)),
                ((x, 0.44, 0.42), (x * 1.25, 0.88, 0.56)))
        for i, (a, b) in enumerate(segs):
            k.set_dark(vki_dpr_rod(k, a, b, 0.045 + 0.002 * i, WOOD, d=0.055 + 0.002 * i), 0.2)
        k.set_dark(vki_dpr_rod(k, (x * 1.05, 0.40, 0.41), (x * 1.10, 0.46, -0.01), 0.045, WOOD, d=0.05), 0.3)
    _cyl(k, (0.0, -0.62, 0.20), 0.20, 0.20, 0.06, 12, WOOD, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    _cyl(k, (0.0, -0.62, 0.20), 0.05, 0.05, 0.10, 8, IRON, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    vki_dpr_rod(k, (-0.25, -0.62, 0.20), (0.25, -0.62, 0.20), 0.025, IRON)
    rnd = random.Random(2401)
    vki_mine_ore_lumps(k, [(rnd.uniform(-0.12, 0.12), 0.05 + rnd.uniform(-0.2, 0.2), 0.49, rnd.uniform(0.05, 0.08))
                           for _ in range(5)], 2402, gold=0.3, iron=0.3)
    vki_mine_cart_meta(k, [[0.0, 0.12, 0.35, 0.66, 1.62, 0.70]])
    k.slot_mats[VKI_CAP] = "M_VKI_IronOre"


def vki_mine_toolrack(k):
    """Mine_ToolRack: a tool rack against a rock face (its back toward local +y): two posts, two rails; two picks, two
    shovels, a sledge and a bar leaning on it, a bucket and a coil of rope at its foot"""
    rnd = random.Random(2501)
    for x in (-0.60, 0.60):
        k.set_dark(vki_adv_box(k, x - 0.045, x + 0.045, 0.08, 0.17, -0.02, 1.62, WOOD), 0.2)
    for z in (0.50, 1.40):
        k.set_dark(vki_adv_box(k, -0.72, 0.72, 0.02, 0.08, z - 0.035, z + 0.035 + 0.002 * (z > 1), WOOD), 0.15)
    for (kind, xa, xb, top) in (("pick", -0.44, -0.40, True), ("shovel", -0.18, -0.20, False),
                                ("pick", 0.06, 0.02, False), ("shovel", 0.28, 0.30, False),
                                ("sledge", 0.47, 0.44, False), ("bar", 0.60, 0.58, False)):
        foot, head = (xa, -0.24, 0.02), (xb, 0.00, 1.46)
        if kind == "pick" and not top:
            foot, head = (xb, 0.00, 1.44), (xa, -0.26, 0.10)
            vki_mine_tool(k, "pick", foot, head, rnd)
            continue
        if kind == "sledge":
            foot = (xa, -0.24, 0.07)
        vki_mine_tool(k, kind, foot, head, rnd)
    vs, _ = vki_home_lathe(k, [(0.0, 0.0), (0.13, 0.0), (0.16, 0.30), (0.145, 0.30), (0.12, 0.03), (0.0, 0.03)],
                           c=(-0.45, -0.36, 0.0), segs=10, mi=WOOD, smooth=False)
    k.set_dark(vs, 0.2)
    vki_home_hoop(k, (-0.45, -0.36, 0.24), 0.155, 0.17, 0.035, segs=10, mi=IRON)
    vki_home_hoop(k, (0.38, -0.36, 0.045), 0.08, 0.17, 0.09, segs=10, mi=BURLAP)
    vki_mine_timber_mats(k)
    k.slot_mats[WOOD] = VKI_MINE_WOOD
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_wall_anchor=1,
                  vki_collider=[[0.0, -0.08, 0.8, 1.46, 0.60, 1.6]],
                  vki_place_rule="against a rock face or wall: its back (local +y) to it, hug off")


def vki_mine_bench(k):
    """Mine_Bench: a sorting bench (1.8 x 0.8, 0.85 high) -- a thick plank top on two trestles with a stretcher --
    ore sorted on it in three heaps (gold-flecked, iron ore, waste rock), a hammer; two baskets under it"""
    k.set_dark(vki_adv_box(k, -0.90, 0.90, -0.40, 0.40, 0.78, 0.85, PLANKS, bev=0.01), 0.1)
    for x in (-0.66, 0.66):
        for s in (-1.0, 1.0):
            k.set_dark(vki_dpr_rod(k, (x, s * 0.34, -0.01), (x, s * 0.10, 0.79), 0.06, WOOD, d=0.065), 0.2)
        k.set_dark(vki_adv_box(k, x - 0.035, x + 0.035, -0.30, 0.30, 0.30, 0.36, WOOD), 0.25)
        k.set_dark(vki_adv_box(k, x - 0.05, x + 0.05, -0.36, 0.36, 0.71, 0.785, WOOD), 0.2)
    k.set_dark(vki_adv_box(k, -0.66, 0.66, -0.03, 0.03, 0.26, 0.34, WOOD), 0.25)
    rnd = random.Random(2601)
    for j, (cx, gold, iron) in enumerate(((-0.55, 1.0, 0.0), (0.0, 0.0, 1.0), (0.55, 0.0, 0.0))):
        k.set_dark(vki_dpr_mound(k, (cx, 0.05, 0.85), 0.20, 0.17, 0.06, VKI_CAP if iron else VKI_STONE_BLOCK_IN,
                                 nr=2, ns=10, seed=2610 + j, wob=0.15, bump=0.3, smooth=False), 0.15 if iron else 0.35)
        pts = [(cx + rnd.uniform(-0.14, 0.14), 0.05 + rnd.uniform(-0.12, 0.12), 0.87, rnd.uniform(0.035, 0.06))
               for _ in range(4)]
        vki_mine_ore_lumps(k, pts, 2620 + j, gold=gold, iron=iron)
    vki_dpr_rod(k, (0.22, -0.22, 0.87), (0.52, -0.28, 0.87), 0.03, WOOD)
    k.box((0.53, -0.28, 0.875), (0.05, 0.12, 0.05), IRON, rot=(0.0, 0.0, -0.2), bevel=0.005)
    for (x, y) in ((-0.36, 0.02), (0.34, -0.04)):
        vs, _ = vki_home_lathe(k, [(0.0, 0.0), (0.15, 0.0), (0.20, 0.24), (0.185, 0.24), (0.14, 0.02), (0.0, 0.02)],
                               c=(x, y, 0.0), segs=10, mi=VKI_STRAW, smooth=False)
        k.set_dark(vs, 0.15)
    vki_mine_cart_meta(k, [[0.0, 0.0, 0.45, 1.80, 0.80, 0.9]])
    k.meta["vki_use"] = [[0.0, -0.75, 0.0]]
    k.slot_mats[VKI_CAP] = "M_VKI_IronOre"


def vki_mine_lanternpole(k):
    """Mine_LanternPole: a lantern hung from a short arm on a pole (2.1 m) set in a cross of planks"""
    k.set_dark(vki_adv_box(k, -0.36, 0.36, -0.06, 0.06, -0.01, 0.045, PLANKS), 0.2)
    k.set_dark(vki_adv_box(k, -0.06, 0.06, -0.36, 0.36, 0.035, 0.09, PLANKS), 0.2)
    k.set_dark(vki_adv_box(k, -0.05, 0.05, -0.05, 0.05, 0.0, 2.10, WOOD), 0.15)
    vki_adv_box(k, 0.04, 0.34, -0.022, 0.022, 1.955, 2.005, WOOD)
    vki_dpr_rod(k, (0.04, 0.0, 1.72), (0.24, 0.0, 1.965), 0.03, WOOD)
    lamp = vki_mine_lamp_meta(vki_mine_lantern(k, 0.28, 0.0, 1.955))
    vki_mine_timber_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_collider=[[0.0, 0.0, 0.5, 0.40, 0.40, 1.0]],
                  **lamp)


def vki_mine_cavein(k):
    """Mine_CaveIn: a collapse filling the end of a gallery 3 m wide (local +y into the dead end): a heap of fallen
    rock 1.35 m high against its back, spilling forward, broken timbers -- a post jutting out, a cap across its face,
    splintered head boards -- and a pick's haft sticking out of the rubble"""
    rx, ry, h, cy = 1.55, 1.05, 1.35, 0.25
    k.set_dark(vki_dpr_mound(k, (0.0, cy, 0.0), rx, ry, h, VKI_STONE_BLOCK_IN, z0=0.001, nr=4, ns=16, seed=2701,
                             wob=0.14, bump=0.22, smooth=False), 0.3)
    rnd = random.Random(2702)
    for i in range(16):
        a = rnd.uniform(0, 2 * math.pi); t = rnd.uniform(0.15, 1.0) ** 0.8
        x, y = math.cos(a) * rx * t, cy + math.sin(a) * ry * t
        r = rnd.uniform(0.14, 0.32) * (1.1 - 0.4 * t)
        vki_deb_rock(k, x, y, r, 2710 + i, flat=0.7, mi=VKI_STONE_BLOCK_IN, z=h * max(0.0, 1 - t * t) ** 0.7 - r * 0.4,
                     dark=0.15)
    for i in range(7):
        a = rnd.uniform(math.pi * 1.1, math.pi * 1.9)
        vki_deb_rock(k, math.cos(a) * rx * 1.08, cy + math.sin(a) * ry * 1.10, rnd.uniform(0.06, 0.12), 2730 + i,
                     flat=0.7, mi=VKI_STONE_BLOCK_IN, dark=0.1)
    k.set_dark(vki_dpr_rod(k, (-1.25, -0.70, 0.22), (-0.30, 0.35, 1.25), 0.20, WOOD, d=0.21, roll=0.4), 0.3)
    k.set_dark(vki_dpr_rod(k, (-1.10, -0.35, 0.95), (1.30, 0.05, 0.55), 0.24, WOOD, d=0.24, roll=-0.2), 0.25)
    for i, (x, y, z, yaw, tilt) in enumerate(((0.55, -0.62, 0.22, 0.4, 0.5), (0.95, -0.85, 0.06, 2.2, 0.1),
                                             (-0.30, -0.80, 0.10, 1.1, 0.2))):
        vki_deb_plank(k, x, y, z, 0.62, 0.14, 0.03, yaw, 2740 + i, tilt=tilt, mi=PLANKS)
    vki_dpr_rod(k, (0.62, -0.35, 0.55), (0.80, -0.62, 1.05), 0.036, WOOD, d=0.034)
    vki_mine_timber_mats(k)
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_CaveRock"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_wall_anchor=1,
                  vki_collider=[[0.0, cy, 0.6, 2 * rx, 2 * ry, 1.2]],
                  vki_place_rule="at the dead end of a gallery two cells wide: its back (local +y) into the end, hug "
                                 "off; it may be let into the rock (vki_wall_anchor)")


def vki_mine_barricade(k):
    """Mine_Barricade: planks nailed across a drift two cells wide -- two posts (+-1.20), boards at 0.45 and 0.95, a
    diagonal brace -- and a warning board hung on them, a red cross daubed on it"""
    for x in (-1.20, 1.20):
        k.set_dark(vki_adv_box(k, x - 0.06, x + 0.06, -0.06, 0.06, -0.02, 1.36, WOOD), 0.2)
    for i, z in enumerate((0.45, 0.95)):
        k.set_dark(vki_adv_box(k, -1.36, 1.36, -0.095 - 0.002 * i, -0.065 - 0.002 * i, z - 0.08, z + 0.08, PLANKS),
                   0.15 + 0.1 * i)
    k.set_dark(vki_dpr_rod(k, (-1.15, -0.118, 0.22), (1.15, -0.118, 1.18), 0.03, PLANKS, d=0.15), 0.2)
    k.set_dark(vki_adv_box(k, -0.24, 0.24, -0.16, -0.135, 0.98, 1.28, PLANKS), 0.05)
    for i, (za, zb) in enumerate(((1.03, 1.23), (1.23, 1.03))):                    # the daubed cross
        vki_dpr_rod(k, (-0.15, -0.162 - 0.003 * i, za), (0.15, -0.162 - 0.003 * i, zb), 0.004, CLOTH_A, d=0.035)
    vki_mine_timber_mats(k)
    k.slot_mats[CLOTH_A] = "M_VKI_BannerRed"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_wall_anchor=1,
                  vki_collider=[[0.0, -0.05, 0.65, 2.74, 0.24, 1.3]],
                  vki_place_rule="across a drift two cells wide: origin on its centre line, local x across it, hug "
                                 "off; the posts may be let into the rock (vki_wall_anchor)")


def vki_mine_sleeperstack(k):
    """Mine_SleeperStack: spare sleepers stacked crosswise (three courses of four) and two loose rails on top"""
    rnd = random.Random(2801)
    for c in range(3):
        z0 = 0.056 * c - 0.004
        for i in range(4):
            o = -0.375 + 0.25 * i + rnd.uniform(-0.02, 0.02)
            L = rnd.uniform(0.92, 1.0)
            if c % 2 == 0:
                vs = vki_adv_box(k, -L / 2, L / 2, o - 0.07, o + 0.07, z0 + 0.001 * i, z0 + 0.054 + 0.001 * i, WOOD)
            else:
                vs = vki_adv_box(k, o - 0.07, o + 0.07, -L / 2, L / 2, z0 + 0.001 * i, z0 + 0.054 + 0.001 * i, WOOD)
            k.set_dark(vs, rnd.uniform(0.25, 0.45))
    for i, (x, a) in enumerate(((-0.12, 0.25), (0.20, 0.32))):
        t = Vector((math.cos(a), math.sin(a), 0.0))
        c = Vector((x, 0.0, 0.0))
        p0, p1 = c - t * 0.60, c + t * 0.60
        path = [(p0.x, p0.y, t.x, t.y), (p1.x, p1.y, t.x, t.y)]
        zb = 0.168 + 0.004 * i
        k.set_dark(vki_mine_sweep(k, path, VKI_MINE_RAIL[0], zb, zb + 0.071, WOOD), 0.3)
        vki_mine_sweep(k, path, VKI_MINE_STRAP[0], zb + 0.071, zb + 0.083, STEEL)
    k.slot_mats[WOOD] = VKI_MINE_WOOD
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block", vki_collider=[[0.0, 0.0, 0.13, 1.25, 1.10, 0.26]])


# ---------------------------------------------------------------- debris (the scatter's "mine" theme)
def vki_mine_debris_tools(k):
    """Debris_Tools: lost gear -- a pick with its haft snapped (the head and a stub, the rest lying by it), a shovel,
    a dented bucket on its side, two iron wedges"""
    rnd = random.Random(2901)
    pts = [Vector((-0.30, 0.10, 0.03)), Vector((-0.17, 0.12, 0.05)), Vector((-0.04, 0.10, 0.06)),
           Vector((0.09, 0.08, 0.05)), Vector((0.22, 0.04, 0.03))]
    vki_poi_tube(k, pts, [0.004, 0.017, 0.024, 0.017, 0.004], VKI_DEB_RUST, segs=4, smooth=False)
    vki_dpr_rod(k, (-0.04, 0.10, 0.06), (-0.06, -0.14, 0.03), 0.034, WOOD, d=0.032)
    vki_dpr_rod(k, (0.08, -0.22, 0.018), (0.60, -0.02, 0.018), 0.034, WOOD, d=0.032)
    vki_dpr_rod(k, (-0.55, -0.30, 0.02), (0.30, -0.45, 0.02), 0.032, WOOD, d=0.03)
    vki_dpr_rod(k, (-0.82, -0.25, 0.008), (-0.55, -0.30, 0.012), 0.20, VKI_DEB_RUST, d=0.012, roll=0.05)
    vs, _ = vki_home_lathe(k, [(0.0, 0.0), (0.11, 0.0), (0.135, 0.24), (0.12, 0.24), (0.10, 0.025), (0.0, 0.025)],
                           c=(0.0, 0.0, 0.0), segs=10, mi=WOOD, smooth=False)
    bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((0.40, 0.32, 0.125)) @
                        Matrix.Rotation(1.9, 4, "Z") @ Matrix.Rotation(math.pi / 2 - 0.08, 4, "X"))
    k.bm.normal_update()
    k.project(vki_faces_of(vs), WOOD)
    k.set_dark(vs, 0.3)
    for i, (x, y, a) in enumerate(((0.62, -0.30, 0.3), (0.72, -0.18, 1.7))):
        vs, _ = vki_prism(k, [(-0.06, 0.0), (0.06, 0.0), (0.0, 0.035)], -0.02, 0.02, VKI_DEB_RUST, axis="y")
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((x, y, 0.018 + 0.001 * i)) @
                            Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X"))
    k.slot_mats[WOOD] = VKI_MINE_WOOD
    vki_deb_meta(k)


def vki_mine_debris_rail(k):
    """Debris_Rail: a loose length of rail lying askew, a sleeper and the broken half of another, spikes"""
    a = 0.35
    t = Vector((math.cos(a), math.sin(a), 0.0))
    p0, p1 = -t * 0.62, t * 0.62
    path = [(p0.x, p0.y, t.x, t.y), (p1.x, p1.y, t.x, t.y)]
    k.set_dark(vki_mine_sweep(k, path, VKI_MINE_RAIL[0], 0.001, 0.072, WOOD), 0.35)
    vki_mine_sweep(k, path, VKI_MINE_STRAP[0], 0.072, 0.083, STEEL)
    vki_mine_sleeper(k, -0.20, -0.30, 0.2, 2951)
    vki_deb_plank(k, 0.45, -0.28, 0.026, 0.48, 0.14, 0.05, 1.3, 2952, mi=WOOD)
    for i, (x, y, yaw) in enumerate(((0.10, 0.28, 0.4), (-0.42, 0.10, 2.0), (0.62, 0.08, 1.2))):
        vki_dpr_rod(k, (x, y, 0.008 + 0.001 * i), (x + 0.12 * math.cos(yaw), y + 0.12 * math.sin(yaw), 0.009 + 0.001 * i),
                    0.014, VKI_DEB_RUST)
    k.slot_mats[WOOD] = VKI_MINE_WOOD
    vki_deb_meta(k)


# ---------------------------------------------------------------- the adit
def vki_mine_adit_portal(k, T):
    """the adit's timbering (vki_cav_tile with tunnel=VKI_MINE_ADIT_T, built after the rock): a set at the mouth and one
    0.46 m in -- posts let into the cleft's sides, caps whose ends run into the rock -- breast boards over the front cap
    up to the rock top, roof boards over both caps, and a floor running into the dark (the track runs in on it)"""
    hw, back, zl = T["hw"], T["back"], T["lintel"]
    rnd = random.Random(71)
    for j, y in enumerate((0.02, 0.46)):
        for s in (-1.0, 1.0):
            x = s * (hw - 0.02)
            k.set_dark(vki_adv_box(k, x - 0.10, x + 0.10, y - 0.10, y + 0.10, -0.02, zl + 0.01, WOOD, bev=0.012),
                       0.2 + 0.3 * j)
        k.set_dark(vki_adv_box(k, -(hw + 0.24), hw + 0.24, y - 0.12, y + 0.12, zl, zl + 0.24 + 0.004 * j, WOOD,
                               bev=0.012), 0.2 + 0.3 * j)
    for i in range(6):
        x0 = -(hw + 0.12) + (2 * hw + 0.24) * i / 6
        k.set_dark(vki_adv_box(k, x0 + 0.004, x0 + (2 * hw + 0.24) / 6 - 0.004, -0.13 + 0.004 * (i % 2),
                               -0.10 + 0.004 * (i % 2), zl + 0.23, 3.02 - 0.03 * rnd.random(), PLANKS),
                   0.1 + 0.1 * rnd.random())
        k.set_dark(vki_adv_box(k, x0 + 0.016, x0 + (2 * hw + 0.24) / 6 - 0.016, -0.10, back - 0.05,
                               zl + 0.244 + 0.002 * (i % 2), zl + 0.274 + 0.002 * (i % 2), PLANKS), 0.3)
    fv = vki_adv_box(k, -hw, hw, -0.02, back, -0.06, 0.0, VKI_FLOOR)
    for v in fv:
        k.set_dark([v], 0.15 + 0.7 * vki_smoothstep(0.0, back, v.co.y))
    k.slot_mats[VKI_FLOOR] = "EarthDamp"
    vki_mine_timber_mats(k)


VKI_MINE_ADIT_T = dict(VKI_MINE_ADIT, portal=vki_mine_adit_portal)


# ---------------------------------------------------------------- the Mine wall family: timber lining
# Mine (class O, T 0.50, H 3.0; vki_core VKI_FAMILIES): timber lining for galleries, drawn on a cave map's inner grid
# lines like any partition. The rock tiles on its nodes are then the wall-backed ones (VKI_CAV_BACK off the line), so
# the rock stands straight behind it. A wall's height follows the rock behind it: Cut where the rock is Cut (open floor
# within two cells north of it), Full where it is Full. Symmetric, since a partition may show either face to the
# gallery:
#   core     packed rock +-0.20 (WALL_A = CaveRock), dark between the boards
#   lagging  horizontal boards on both faces (+-0.20 .. +-0.23, SHUTTER = hewn wood darkened 0.26-0.44 board by board,
#            so the frame stays the palest), 0.20 high on a 0.25 pitch (the dark core shows between them), their
#            joints staggered row by row (odd rows at the odd 0.75 marks, even rows at 1.5); the rows below 0.65 are the
#            same on Full and Cut walls (T2)
#   wale     a hewn beam 0.78-1.00 (+-0.27, CAP top): the Cut wall's cap, a wale on Full walls; Full walls end in a wall
#            plate 2.76-3.00 (+-0.28); the 300 has a stud at its middle (the rhythm posts stand at its ends)
#   posts    Corner: a crib of short hewn beams crossed course by course (+-0.29; a square post that size read as a
#            stump); Mid: a hewn post (+-0.12 x +-0.31: 8 cm proud of the boards) with an end-grain top
# No rakes (a cave map's walls are partitions) and no doors (a drift's mouth is left open).
VKI_MNW_CORE = 0.20
VKI_MNW_BOARD = 0.03
VKI_MNW_ROWS = ((0.00, 0.20), (0.25, 0.45), (0.50, 0.70),               # 5 cm apart: the dark core between them
                (1.03, 1.23), (1.28, 1.48), (1.53, 1.73), (1.78, 1.98), (2.03, 2.23), (2.28, 2.48), (2.53, 2.73))
VKI_MNW_WALE = (0.78, 1.00, 0.27)             # z0, z1, half width
VKI_MNW_PLATE = (2.76, 3.00, 0.28)


def vki_mnw_plain(k, L, height):
    """Wall_Mine_Plain_150A / _300, Full or Cut (see the section header)"""
    k.set_family("Mine")
    full = height == "Full"
    rnd = random.Random(vki_seed("MineWall|%g|%s" % (L, height)))
    w0, w1, whw = VKI_MNW_WALE
    p0, p1, phw = VKI_MNW_PLATE
    for z0, z1 in [(VKI_FOOT_Z, w0)] + ([(w1, p0)] if full else []):   # the core, split round the wale (T5S)
        k.set_dark(vki_adv_box(k, 0.0, L, -VKI_MNW_CORE, VKI_MNW_CORE, z0, z1, VKI_WALL_A), 0.45)
    for ri, (z0, z1) in enumerate(VKI_MNW_ROWS):
        if z0 > w0 and not full:
            break
        marks = [0.75 * j for j in range(1, int(round(L / 0.75))) if j % 2 == ri % 2]
        cuts = [0.0] + marks + [L]
        for side in (-1.0, 1.0):
            ya, yb = sorted((side * VKI_MNW_CORE, side * (VKI_MNW_CORE + VKI_MNW_BOARD)))
            for a, b in zip(cuts[:-1], cuts[1:]):
                a2, b2 = a + (0.004 if a > 1e-6 else 0.0), b - (0.004 if b < L - 1e-6 else 0.0)
                k.set_dark(vki_adv_box(k, a2, b2, ya, yb, z0, z1, SHUTTER),
                           0.26 + 0.18 * rnd.random() + (0.08 if z0 < 0.1 else 0.0))
    k.set_dark(vki_tim_member(k, 0.0, L, w0, w1, y0=-whw, y1=whw, top=VKI_CAP, bev=0.015), 0.12)
    if full:
        k.set_dark(vki_tim_member(k, 0.0, L, p0, p1, y0=-phw, y1=phw, top=VKI_CAP, bev=0.015), 0.10)
    if L > 2.0:                                           # (5 mm into the beams: no face in the core's planes, T5S)
        for z0, z1 in [(-0.02, w0 + 0.005)] + ([(w1 - 0.005, p0 + 0.005)] if full else []):
            k.set_dark(vki_adv_box(k, 1.39, 1.61, -0.275, 0.275, z0, z1, WOOD), 0.18)
    k.slot_mats[SHUTTER] = VKI_MINE_TIMBER     # hewn wood darkened a board at a time (SHUTTER: the grain runs along
    #    each board; the planks texture's seams tiled the boards, and the kit's oak, even tinted, read as black panels)
    k.slot_mats[WOOD] = VKI_MINE_TIMBER
    k.meta.update(vki_class="wall")


def vki_mnw_plain_150a_full(k): vki_mnw_plain(k, 1.5, "Full")
def vki_mnw_plain_150a_cut(k): vki_mnw_plain(k, 1.5, "Cut")
def vki_mnw_plain_300_full(k): vki_mnw_plain(k, 3.0, "Full")
def vki_mnw_plain_300_cut(k): vki_mnw_plain(k, 3.0, "Cut")


def vki_mnw_post(k, kind, height):
    """Post_Mine_Corner / _Mid, Full or Cut, centred on its node, z -0.30 .. wall top + 0.04. Corner: a crib (+-0.29)
    of two short hewn beams per course (0.26 wide, 6 cm apart), the courses crossed and 1 cm apart, the top course's
    tops CAP; Mid: a hewn post +-0.12 along the wall x +-0.31 across (8 cm proud of the lagging), bevel 0.02, an
    end-grain top (vki_endgrain_fit). Grime toward the floor"""
    k.set_family("Mine")
    top = (VKI_H_FULL["Mine"] if height == "Full" else VKI_CUT_H) + VKI_POST_TOP
    ax, ay = (0.29, 0.29) if kind == "Corner" else VKI_MID_HW["O"]
    if kind == "Corner":
        n = int(round((top - VKI_POST_Z0) / 0.25))          # the top course takes up the rest
        for ci in range(n):
            z0 = VKI_POST_Z0 + 0.25 * ci
            z1 = min(z0 + 0.24, top)
            last = ci == n - 1
            for s in (-1.0, 1.0):
                if ci % 2 == 0:
                    x0, x1, y0, y1 = -ax, ax, s * 0.16 - 0.13, s * 0.16 + 0.13
                else:
                    x0, x1, y0, y1 = s * 0.16 - 0.13, s * 0.16 + 0.13, -ay, ay
                vki_tim_member(k, x0, x1, z0, top if last else z1, y0=y0, y1=y1, top=VKI_CAP if last else None,
                               bev=0.0)
    else:
        c = (0.0, 0.0, (VKI_POST_Z0 + top) / 2); sz = (2 * ax, 2 * ay, top - VKI_POST_Z0)
        vs = list(set(k.box(c, sz, WOOD, bevel=VKI_POST_BEVEL)))
        k.bm.normal_update()
        tops = [f for f in vki_faces_of(vs) if f.normal.z > 0.65]
        vki_endgrain_fit(k, tops, (0.0, 0.0, top), VKI_TIM_X, VKI_TIM_Y, max(ax, ay), fill=VKI_TIM_POST_FILL)
    for v in k.bm.verts:
        k.set_dark([v], 0.10 + 0.25 * vki_smoothstep(0.5, 0.0, v.co.z))
    k.slot_mats[WOOD] = VKI_MINE_TIMBER
    other = "Cut" if height == "Full" else "Full"
    rule = {"Corner": "L/T/X junction of Mine lining walls (required, T12)",
            "Mid": "height step / free end (required) | rhythm at even nodes (skipped where a prop touches the node: "
                   "a timber set's post stands there)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": f"SM_VKI_Post_Mine_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_mnw_post_corner_full(k): vki_mnw_post(k, "Corner", "Full")
def vki_mnw_post_corner_cut(k): vki_mnw_post(k, "Corner", "Cut")
def vki_mnw_post_mid_full(k): vki_mnw_post(k, "Mid", "Full")
def vki_mnw_post_mid_cut(k): vki_mnw_post(k, "Mid", "Cut")


# ---------------------------------------------------------------- specs
VKI_MINE_SPECS = [
    ("SM_VKI_Overlay_Track_Straight", vki_mine_track_straight, "none"),
    ("SM_VKI_Overlay_Track_End", vki_mine_track_end, "none"),
    ("SM_VKI_Overlay_Track_Curve", vki_mine_track_curve, "none"),
    ("SM_VKI_Overlay_Track_Tee", vki_mine_track_tee, "none"),
    ("SM_VKI_Overlay_Track_Cross", vki_mine_track_cross, "none"),
    ("SM_VKI_Prop_Mine_Cart", vki_mine_cart, "prop"),
    ("SM_VKI_Prop_Mine_Cart_Ore", vki_mine_cart_ore, "prop"),
    ("SM_VKI_Prop_Mine_Cart_Tipped", vki_mine_cart_tipped, "prop"),
    ("SM_VKI_Prop_Mine_Set", vki_mine_set_plain, "prop"),
    ("SM_VKI_Prop_Mine_Set_Lamp", vki_mine_set_lamp, "prop"),
    ("SM_VKI_Prop_Mine_Set_Broken", vki_mine_set_broken, "prop"),
    ("SM_VKI_Rock_Cave_OOFF_Adit", (lambda k: vki_cav_tile(k, "OOFF", "Adit", tunnel=VKI_MINE_ADIT_T)), "none"),
    ("SM_VKI_Overlay_Debris_Tools", vki_mine_debris_tools, "none"),
    ("SM_VKI_Overlay_Debris_Rail", vki_mine_debris_rail, "none"),
    ("SM_VKI_Prop_Vein_Gold", vki_mine_vein_gold, "prop"),
    ("SM_VKI_Prop_Vein_Iron", vki_mine_vein_iron, "prop"),
    ("SM_VKI_Prop_Vein_Crystal", vki_mine_vein_crystal, "none"),
    ("SM_VKI_Prop_Mine_OrePile", vki_mine_orepile, "prop"),
    ("SM_VKI_Prop_Mine_Wheelbarrow", vki_mine_wheelbarrow, "prop"),
    ("SM_VKI_Prop_Mine_ToolRack", vki_mine_toolrack, "prop"),
    ("SM_VKI_Prop_Mine_Bench", vki_mine_bench, "prop"),
    ("SM_VKI_Prop_Mine_LanternPole", vki_mine_lanternpole, "prop"),
    ("SM_VKI_Prop_Mine_CaveIn", vki_mine_cavein, "prop"),
    ("SM_VKI_Prop_Mine_Barricade", vki_mine_barricade, "prop"),
    ("SM_VKI_Prop_Mine_SleeperStack", vki_mine_sleeperstack, "prop"),
    ("SM_VKI_Pit_Shaft_300x300", vki_mine_shaft, "none"),
    ("SM_VKI_Prop_POI_Treadwheel", vki_mine_treadwheel, "prop"),
    ("SM_VKI_Wall_Mine_Plain_150A_Full", vki_mnw_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Mine_Plain_150A_Cut", vki_mnw_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Mine_Plain_300_Full", vki_mnw_plain_300_full, "wall"),
    ("SM_VKI_Wall_Mine_Plain_300_Cut", vki_mnw_plain_300_cut, "wall"),
    ("SM_VKI_Post_Mine_Corner_Full", vki_mnw_post_corner_full, "wall"),
    ("SM_VKI_Post_Mine_Corner_Cut", vki_mnw_post_corner_cut, "wall"),
    ("SM_VKI_Post_Mine_Mid_Full", vki_mnw_post_mid_full, "wall"),
    ("SM_VKI_Post_Mine_Mid_Cut", vki_mnw_post_mid_cut, "wall"),
]
VKI_MNW_NAMES = [n for n, _, _ in VKI_MINE_SPECS if "_Wall_Mine_" in n or "_Post_Mine_" in n]
VKI_MINE_NAMES = [n for n, _, _ in VKI_MINE_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_MINE_SPECS])
