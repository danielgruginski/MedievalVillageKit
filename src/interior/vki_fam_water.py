# ===================== VKI FAM WATER: natural water -- streams, waterfalls, stepping stones (water kit) =====================
# Water kit (docs/WATER_KIT.md). Package "adventure". Loaded by vki_ns() after vki_fam_sewer; uses the cave mesher
# (vki_cav_field, vki_cav_ms_solid, vki_cav_boxes, vki_cav_rock_mats) and at build time the prop helpers (vki_dpr_*,
# vki_home_*). Every top-level name starts with vki_/VKI_ (T18).
# Streams: in a cave map, cells coded "ss" are stream (X). Dual-grid stream tiles (class "ground", like the chasm's):
#   SM_VKI_Ground_Stream_<code>_Q<p> -- 14 X / O codes x 4 node parities, never rotated (their floor is world-locked)
#   -- plus SM_VKI_Ground_Stream_XXXX. A tile carries the floor of its footprint with the stream's bed cut by the cave
#   field (bilinear plus windowed noise, both ways: it meanders, swells and narrows), banks that slope in 0.32 m as they
#   fall to the bed, a pebbly bed at -0.45 (the ASH slot: M_VKI_StreamBed) and clear water at -0.22 (the WATER slot:
#   M_VKI_StreamWater, 72 % opaque). Water and bed are closed slabs over the whole tile, 1 mm short of its edges (inside
#   the bank solid they are hidden). Colliders soft, like the chasm's: a stepping-stone deck crosses them.
#   Where a stream meets the chasm the chasm's tiles take the shared nodes (the stream counts as chasm there), and the
#   assembler puts a waterfall over the lip. A stream runs in under rock at its ends (the rock's foot overhangs it).
# Waterfalls (props; the animation, foam and mist are Unity's -- vki_fx sockets and vki_flow mark them):
#   Prop_Waterfall_Chasm    the stream pouring over the chasm's lip: a sheet from the water surface curving over and
#                           falling 3.6 m, darkening into the deep; placed by the assembler on the stream cell's centre
#   Prop_Waterfall_Rock     a fall from a cleft in a Full rock face (2.3 m) into a stream below, foam at its foot
#   Prop_Waterfall_RockLow  the same from a Cut rock face (0.85 m)
#   Prop_SteppingStones     four flat stones across a one-cell stream (vki_bridge deck)
# Build: g["vki_ws_build"]("adventure", VKI_WAT_NAMES); test: g["vki_test_pieces"](VKI_WAT_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_WAT_STREAM = dict(levels=(-0.60, -0.45, -0.30, -0.15), water=-0.22, bed=(-0.50, -0.45),
                      step={-0.60: 0.0, -0.45: 0.32, -0.30: 0.22, -0.15: 0.10, 0.0: 0.0})   # -0.60 (under the
# bed): no inset, so the solid's flat bottom never folds over


# ---------------------------------------------------------------- stream tiles
def vki_wat_slabs(k):
    """the water (-0.24..-0.22, WATER) and the bed (-0.50..-0.45, ASH: M_VKI_StreamBed) over the whole tile, 1 mm short
    of its edges"""
    W = VKI_WAT_STREAM
    h = 0.749
    vs = list(set(k.box((0.0, 0.0, W["water"] - 0.01), (2 * h, 2 * h, 0.02), WATER, bevel=0.0)))
    b0, b1 = W["bed"]
    bs = list(set(k.box((0.0, 0.0, (b0 + b1) / 2), (2 * h, 2 * h, b1 - b0), VKI_ASH, bevel=0.0)))
    k.project(vki_faces_of(bs), VKI_ASH)
    k.set_dark(bs, 0.25)
    k.slot_mats[WATER] = "M_VKI_StreamWater"
    k.slot_mats[VKI_ASH] = "M_VKI_StreamBed"
    return vs, bs


def vki_wat_stream(k, code, qa, qb):
    """stream tile `code` (corners SW SE NE NW, X stream / O ground) at a node of parity (qa, qb)"""
    k.set_family("Cave")
    W = VKI_WAT_STREAM
    seed = vki_seed("Stream|%s|%d%d" % (code, qa, qb))
    s_ = lambda x, y: vki_cav_field(x, y, code.replace("X", "F"), seed, VKI_CAV_AMP * 0.8, sym=True)
    sd = vki_cav_ms_solid(k, lambda x, y: -s_(x, y), lambda x, y: 0.0, lambda H: W["levels"],
                          lambda z, H: W["step"].get(round(z, 2), 0.0), seed, wamp=0.05)
    bm = k.bm
    for f in sd["tops"]:
        f.material_index = VKI_FLOOR
        for lp in f.loops:
            lp[k.uv].uv = ((lp.vert.co.x + 0.75 + 1.5 * qa) / 3.0, (lp.vert.co.y + 0.75 + 1.5 * qb) / 3.0)
    for f in sd["cliff"]:
        f.material_index = VKI_STONE_BLOCK_IN
    k.project(sd["sect"] + sd["bottoms"], VKI_STONE_BLOCK_IN)
    bm.normal_update()
    big = [f for f in sd["tops"] + sd["cliff"] + sd["sect"] + sd["bottoms"] if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    for f in bm.faces:
        f.smooth = f.material_index == VKI_FLOOR
    lip = {v for f in sd["cliff"] for v in f.verts if f.is_valid}
    for v in bm.verts:                                                   # wet banks, darker below the water line
        if v.co.z < -0.01:
            k.set_dark([v], 0.25 + (0.25 if v.co.z < W["water"] else 0.0))
    for f in bm.faces:                                                   # the floor darkens toward the bank (damp)
        if f.material_index == VKI_FLOOR:
            for v in f.verts:
                if abs(v.co.z) < 1e-6 and v in lip:
                    k.set_dark([v], 0.22)
    vki_wat_slabs(k)
    vki_cav_rock_mats(k)
    k.slot_mats[VKI_FLOOR] = "CaveFloor"                               # the default; a level's zone style overrides it
    wet = vki_cav_boxes(lambda x, y: s_(x, y) > 0.05)                 # the water, not the banks (shallow, walkable)
    has_floor = bool(sd["tops"])
    k.meta.update(vki_class="ground", vki_corners=code, vki_q_parity=[qa, qb],
                  vki_uv_lock="world" if has_floor else "local", vki_nav="block" if wet else "walk",
                  vki_collider=[[cx, cy, 0.5, w, d, 1.0] for cx, cy, w, d in wet] or [[0, 0, -5, 0.01, 0.01, 0.01]],
                  vki_water={"kind": "stream", "surface_z": W["water"], "bed_z": W["bed"][1]},
                  vki_place_rule="dual grid: origin on a node (i, j) with (i mod 2, j mod 2) = (%d, %d), rotation 0; "
                                 "corners SW SE NE NW = the cells around it (X stream)" % (qa, qb))


def vki_wat_stream_all(k):
    """the all-stream tile XXXX: water and bed only (no floor, no parity)"""
    k.set_family("Cave")
    vki_wat_slabs(k)
    k.meta.update(vki_class="ground", vki_corners="XXXX", vki_nav="block", vki_uv_lock="local",
                  vki_collider=[[0.0, 0.0, 0.5, 1.5, 1.5, 1.0]],
                  vki_water={"kind": "stream", "surface_z": VKI_WAT_STREAM["water"], "bed_z": VKI_WAT_STREAM["bed"][1]},
                  vki_place_rule="dual grid: origin on a node, rotation 0")


# ---------------------------------------------------------------- waterfalls
def vki_wat_sheet(k, pts, w0, w1, mi, dark=None, seed=0):
    """a closed water sheet 1.2 cm thick along the path pts [(y, z)] in the local y-z plane, half width w0 at the start
    tapering to w1 at the end, five columns across; vki_dark streaks the sheet (paler ribs, darker thin edges) on top
    of dark(t) along the path (t 0..1)"""
    n = len(pts)
    rnd = random.Random(seed)
    cols = (-1.0, -0.5, 0.0, 0.5, 1.0)
    rib = (0.34, 0.02, 0.14, 0.0, 0.34)
    front, back = [], []
    for i, (y, z) in enumerate(pts):
        t = i / (n - 1)
        hw = w0 + (w1 - w0) * t
        wob = 0.03 * t * (rnd.random() - 0.5)
        if i < n - 1:
            ty, tz = pts[i + 1][0] - y, pts[i + 1][1] - z
        else:
            ty, tz = y - pts[i - 1][0], z - pts[i - 1][1]
        L = math.hypot(ty, tz) or 1.0
        ny, nz = tz / L, -ty / L                                           # the sheet's normal (toward +y / up)
        front.append([k.bm.verts.new((x * hw + wob, y, z)) for x in cols])
        back.append([k.bm.verts.new((x * hw + wob, y + 0.012 * ny, z + 0.012 * nz)) for x in cols])
    fs = []
    m = len(cols) - 1
    for i in range(n - 1):
        for j in range(m):
            fs.append(k.bm.faces.new((front[i + 1][j], front[i + 1][j + 1], front[i][j + 1], front[i][j])))
            fs.append(k.bm.faces.new((back[i][j], back[i][j + 1], back[i + 1][j + 1], back[i + 1][j])))
        for j in (0, m):
            fs.append(k.bm.faces.new((front[i][j], front[i + 1][j], back[i + 1][j], back[i][j])))
    for i in (0, n - 1):
        for j in range(m):
            fs.append(k.bm.faces.new((front[i][j], front[i][j + 1], back[i][j + 1], back[i][j])))
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.material_index = mi
    for i in range(n):
        base = dark(i / (n - 1)) if dark is not None else 0.0
        for j in range(len(cols)):
            d = min(0.95, base + rib[j] + 0.08 * (rnd.random() - 0.5))
            for v in (front[i][j], back[i][j]):
                v[k.dark] = max(0.0, d)
    return fs


def vki_wat_foam(k, c, r, z, seed):
    """a foam patch on the water (VKI_WAX: M_VKI_Foam)"""
    vki_dpr_blob(k, c, r, z, z + 0.006, VKI_WAX, ns=9, wob=0.3, seed=seed)


def vki_wat_fall_chasm(k):
    """the stream pouring over the chasm's lip (local -y is the chasm): origin on the stream cell's centre, where the
    stream tiles end and the chasm's hole begins; a sheet from over the water (y +0.12, z -0.21) curving over the lip
    and falling to -3.8, 1.32 m wide at the lip (the stream's width) narrowing to 0.92, pale ribs, darkening into the
    deep; foam on the lip"""
    pts = [(0.12, -0.21), (0.0, -0.215), (-0.12, -0.26), (-0.22, -0.40), (-0.30, -0.70), (-0.36, -1.20),
           (-0.41, -1.90), (-0.45, -2.70), (-0.48, -3.80)]
    vki_wat_sheet(k, pts, 0.66, 0.46, WATER, dark=lambda t: 0.80 * vki_smoothstep(0.1, 1.0, t), seed=3)
    for i, (x, y, r) in enumerate(((-0.42, 0.10, (0.18, 0.10)), (0.40, 0.12, (0.18, 0.10)), (0.0, 0.16, (0.24, 0.10)),
                                   (-0.16, 0.30, (0.14, 0.08)), (0.20, 0.32, (0.12, 0.07)))):
        vki_wat_foam(k, (x, y), r, -0.2085 + 0.0012 * i, seed=30 + i)
    k.slot_mats[WATER] = "M_VKI_WaterFall"
    k.slot_mats[VKI_WAX] = "M_VKI_Foam"
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="none", vki_collider=[[0.0, 0.0, -5.0, 0.01, 0.01, 0.01]],
                  vki_flow=[0.0, -1.0], vki_water={"kind": "waterfall", "drop": 3.6},
                  vki_fx=[dict(fx="waterfall", pos=[0.0, -0.25, -0.40], scale=1.0),
                          dict(fx="mist", pos=[0.0, -0.50, -3.40], scale=1.5)],
                  vki_place_rule="on a stream cell's centre next to the chasm, local -y toward the chasm (the "
                                 "assembler places it)")


def vki_wat_fall_rock(k, top):
    """a fall from a cleft in a rock face (local +y is the rock; origin on the face's cell edge): the water leaves the
    rock at `top`, starting 0.40 m inside the face (the rock's lobes wander), curves out and falls into the stream below
    (-0.22) 0.6 m out, 0.55 m wide widening to 0.75; foam at its foot"""
    zt = top
    pts = [(0.40, zt), (0.22, zt - 0.02), (0.08, zt - 0.10), (-0.05, zt - 0.28)]
    n = 5
    for i in range(1, n + 1):
        t = i / n
        pts.append((-0.05 - 0.55 * t ** 0.8, zt - 0.28 - (zt - 0.28 + 0.215) * t ** 1.4))
    vki_wat_sheet(k, pts, 0.27, 0.38, WATER, dark=lambda t: 0.05, seed=5)
    for i, (x, y, r) in enumerate(((0.0, -0.64, (0.50, 0.34)), (-0.40, -0.42, (0.18, 0.13)), (0.38, -0.46, (0.16, 0.12)),
                                   (-0.12, -0.98, (0.20, 0.10)), (0.26, -0.92, (0.14, 0.08)))):
        vki_wat_foam(k, (x, y), r, -0.2085 + 0.0012 * i, seed=40 + i)
    k.slot_mats[WATER] = "M_VKI_WaterFall"
    k.slot_mats[VKI_WAX] = "M_VKI_Foam"
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="none", vki_collider=[[0.0, 0.0, -5.0, 0.01, 0.01, 0.01]],
                  vki_wall_anchor=1, vki_flow=[0.0, -1.0], vki_water={"kind": "waterfall", "drop": round(zt + 0.22, 2)},
                  vki_fx=[dict(fx="waterfall", pos=[0.0, -0.2, zt * 0.5], scale=1.0),
                          dict(fx="mist", pos=[0.0, -0.62, -0.10], scale=0.8)],
                  vki_place_rule="on the cell edge where a stream meets rock (the rock %s), local +y into the rock; "
                                 "hug off" % ("Full" if top > 1.5 else "Cut"))


def vki_wat_fall_rock_full(k): vki_wat_fall_rock(k, 2.30)
def vki_wat_fall_rock_low(k): vki_wat_fall_rock(k, 0.85)


def vki_wat_stones(k):
    """four flat stepping stones along local y across a one-cell stream (tops 0.02-0.05 over the floor line, from
    the bed); vki_bridge deck: the walk BFS crosses the stream there"""
    rnd = random.Random(12)
    for i, y in enumerate((-0.86, -0.30, 0.28, 0.84)):
        r = rnd.uniform(0.27, 0.31)
        top = 0.03 + 0.03 * rnd.random()
        v = vki_home_ico(k, (rnd.uniform(-0.05, 0.05), y, (top - 0.50) / 2), r, VKI_STONE_BLOCK_IN,
                         scale=(1.0, 0.85, (top + 0.50) / (2 * r)), sub=1, jit=0.02, seed=60 + i, smooth=False)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
        for vv in v:
            k.set_dark([vv], 0.35 * vki_smoothstep(-0.12, -0.40, vv.co.z))       # pale dry tops, wet below
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="walk", vki_collider=[[0.0, 0.0, -5.0, 0.01, 0.01, 0.01]],
                  vki_bridge=[[-0.35, -1.20, 0.35, 1.20]],
                  vki_place_rule="on a stream cell's centre, across it: rotation 0 (a west-east stream) or 90")


# ---------------------------------------------------------------- specs
def vki_wat_specs():
    out = []
    for n in range(1, 15):
        code = "".join("X" if n >> i & 1 else "O" for i in range(4))
        for qa in (0, 1):
            for qb in (0, 1):
                out.append(("SM_VKI_Ground_Stream_%s_Q%d%d" % (code, qa, qb),
                            (lambda k, code=code, qa=qa, qb=qb: vki_wat_stream(k, code, qa, qb)), "none"))
    out.append(("SM_VKI_Ground_Stream_XXXX", vki_wat_stream_all, "none"))
    return out


VKI_WAT_SPECS = vki_wat_specs() + [
    ("SM_VKI_Prop_Waterfall_Chasm", vki_wat_fall_chasm, "none"),
    ("SM_VKI_Prop_Waterfall_Rock", vki_wat_fall_rock_full, "none"),
    ("SM_VKI_Prop_Waterfall_RockLow", vki_wat_fall_rock_low, "none"),
    ("SM_VKI_Prop_SteppingStones", vki_wat_stones, "none"),
]
VKI_WAT_NAMES = [n for n, _, _ in VKI_WAT_SPECS]
VKI_WAT_STREAM_NAMES = [n for n in VKI_WAT_NAMES if n.startswith("SM_VKI_Ground_Stream_")]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_WAT_SPECS])
