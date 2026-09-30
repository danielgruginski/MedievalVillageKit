# ===================== VKI FAM CAVEWALL: the Cave wall family -- rock walls on the wall grid (adventure kit) =====================
# Adventure kit (docs/ADVENTURE_KIT.md). Package "adventure". Loaded by vki_ns() after vki_fam_cave (VKI_CAV_CRYSTAL_COL,
# vki_cav_rock_mats); uses the kit helpers (grid_cut, vki_prism, vki_sto_*, vki_dun_*). Every top-level name starts
# with vki_/VKI_ (T18).
# For WALLED levels that want rock (a mine, a cave-like cellar): the cave levels themselves are cell maps of organic
# dual-grid rock tiles (vki_fam_cave). Cave (class O, T 0.50, H 3.0): a rock mass on the node-to-node grid. Both
# faces bulge into their rooms by up to VKI_CAV_BULGE (noise + bedding ledges, a foot that flares onto the floor),
# faceted (flat shading), and the skyline dips mid-span; bulge and dip fade to zero within 0.32 m of every piece-end
# node, so every piece ends in the plain rock section and butts, turns and meets posts like any family (T2, T3). No
# coping: the rock is sliced flat at the wall's height and the slice is the cut section (CAP -> M_VKI_CaveCut). Pieces:
#   Plain 150A / 150B (another face, with a vein of glowing crystals and a light) / 300, Full and Cut; Rake L / R;
#   Gap_150 (a natural opening, Full: rock arching over it; plan tokens "OO" / "O", "oo" / "o"); Passage_150_Full (a
#   tunnel mouth: a scene link); posts (rock masses)
# Build: g["vki_ws_build"]("adventure", VKI_CWL_NAMES); test: g["vki_test_pieces"](VKI_CWL_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_CAV_CUT_TO = "SM_VKI_Wall_Cave_Plain_150A_Cut"
VKI_CAV_BULGE = 0.26            # max bulge of each rock face (mid-span); typical 0.10-0.18
VKI_CAV_STEP = 0.15             # grid of the rock face (its facets)

def vki_cav_env(x, L, mid=False):
    """0 within 0.32 of the piece-end nodes (0, L; and 1.5 when mid), rising to 1 by 0.62"""
    nodes = [0.0, L] + ([1.5] if mid else [])
    return min(vki_smoothstep(0.32, 0.62, abs(x - n)) for n in nodes)


def vki_cav_disp(x, z, L, seed, mid=False):
    """bulge of the rock face into the room at (x, z): value noise at two scales, bedding ledges, a flared foot"""
    e = vki_cav_env(x, L, mid)
    if e <= 0.0:
        return 0.0
    n1 = vki_vnoise(x / 0.45 + 7.3, z / 0.35, seed)
    n2 = vki_vnoise(x / 0.20 + 1.1, z / 0.16, seed + 17)
    strata = 0.5 + 0.5 * math.sin(z * 2 * math.pi / 0.62 + 2.0 * n1)
    zp = vki_smoothstep(-0.10, 0.20, z) * (1.0 - 0.30 * vki_clamp(z / 3.0)) + 0.35 * vki_smoothstep(0.45, 0.0, z) * \
        vki_smoothstep(-0.12, 0.0, z)
    return VKI_CAV_BULGE * e * zp * (0.30 + 0.45 * n1 + 0.15 * n2 + 0.10 * strata)


def vki_cav_body(k, polys, step=VKI_CAV_STEP):
    """rock body: convex (x, z) polygons extruded +-T/2 (WALL_A on -Y, WALL_B on +Y), cut to the facet grid, flagged
    body"""
    before = set(k.bm.verts)
    for poly in polys:
        vs, fs = vki_prism(k, poly, -k.T / 2, k.T / 2, VKI_WALL_A, axis="y")
        for f in fs:
            if f.normal.y > 0.7:
                k.project([f], VKI_WALL_B)
        grid_cut(k, vs, step)
    new = [v for v in k.bm.verts if v not in before]
    k.mark_body(new)
    return new


def vki_cav_finish(k, L, H_fn, seed, mid=False, dip=None):
    """bulge both faces, slice the top as the CAP section (faces at the height H_fn(x)), then dip: (z_base, H, D) lowers
    the top mid-span by up to D (a ragged skyline; the band above z_base is squeezed, zero within 0.32 of the nodes);
    tone the rock (damp foot, noise). UVs stay the undisplaced world-locked ones."""
    T2 = k.T / 2
    for v in k.bm.verts:                                  # (UVs stay the undisplaced world-locked ones)
        if not v[k.body]:
            continue
        if abs(v.co.y + T2) <= 1e-4:
            v.co.y -= vki_cav_disp(v.co.x, v.co.z, L, seed, mid)
        elif abs(v.co.y - T2) <= 1e-4:
            v.co.y += vki_cav_disp(v.co.x, v.co.z, L, seed + 1, mid)
    k.bm.normal_update()
    tops = [f for f in k.bm.faces if all(v[k.body] for v in f.verts) and f.normal.z > 0.3 and
            all(v.co.z >= H_fn(v.co.x) - 2e-3 for v in f.verts)]
    for f in tops:
        f.material_index = VKI_CAP
        for l in f.loops:
            l[k.uv].uv = (l.vert.co.x / 1.2, l.vert.co.y / 1.2)
    if dip:
        zb_, Ht, D = dip
        for v in k.bm.verts:
            if v[k.body] and v.co.z > zb_ + 1e-6:
                dd = D * vki_cav_env(v.co.x, L, mid) * (0.35 + 0.65 * vki_vnoise(v.co.x / 0.30, 5.5, seed + 9))
                v.co.z = zb_ + (v.co.z - zb_) * (Ht - dd - zb_) / (Ht - zb_)
        k.bm.normal_update()
    for v in k.bm.verts:
        d = 0.12 * vki_hash01(int(round(v.co.x / 0.15)), int(round(v.co.z / 0.15)), seed + 5)
        k.set_dark([v], d)
    vki_dun_damp(k)
    for f in tops:
        for v in f.verts:
            v[k.dark] = min(v[k.dark], 0.05)


# ---------------------------------------------------------------- Plain, Rake, posts
VKI_CAV_DIP = {"Full": (2.0, 3.0, 0.40), "Cut": (0.70, VKI_CUT_H, 0.12)}   # (z_base, H, max dip) of the skyline


def vki_cav_plain(k, L, height, variant="A"):
    H = 3.0 if height == "Full" else VKI_CUT_H
    vki_cav_body(k, [[(0.0, VKI_FOOT_Z), (L, VKI_FOOT_Z), (L, H), (0.0, H)]])
    seed = vki_seed("Cave|%s|%g" % (variant, L))
    vki_cav_finish(k, L, lambda x: H, seed, dip=VKI_CAV_DIP[height])
    light = None
    if variant == "B":
        rnd = random.Random(seed)
        pts = []
        for i in range(6):
            x = 0.62 + 0.26 * rnd.random(); z = 1.25 + 0.5 * rnd.random()
            y = -k.T / 2 - vki_cav_disp(x, z, L, seed) + 0.03
            h = rnd.uniform(0.18, 0.42); r = rnd.uniform(0.035, 0.07)
            d = Vector((rnd.uniform(-0.5, 0.5), -1.0, rnd.uniform(-0.3, 0.6))).normalized()
            rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
            c = Vector((x, y, z)) + d * (h / 2 - 0.02)
            _cyl(k, tuple(c), r, 0.006, h, 6, MUSH_GLOW, rot=rot)
            pts.append(c)
        cc = sum(pts, Vector()) / len(pts)
        light = [dict(type="POINT", role="crystal", pos=[round(cc.x, 3), round(cc.y - 0.25, 3), round(cc.z, 3)], w=30.0,
                      color=VKI_CAV_CRYSTAL_COL, range=4.0, flicker=0, shadows=0, radius=0.05)]
    k.meta.update(vki_class="wall", vki_bulge=VKI_CAV_BULGE)
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_CAV_CUT_TO, vki_lights=light)


def vki_cav_plain_150a_full(k): vki_cav_plain(k, 1.5, "Full", "A")
def vki_cav_plain_150a_cut(k): vki_cav_plain(k, 1.5, "Cut", "A")
def vki_cav_plain_150b_full(k): vki_cav_plain(k, 1.5, "Full", "B")
def vki_cav_plain_300_full(k): vki_cav_plain(k, 3.0, "Full", "A")
def vki_cav_plain_300_cut(k): vki_cav_plain(k, 3.0, "Cut", "A")


def vki_cav_rake(k, side):
    """Cut section for u <= 0.32 from the low end, Full for u >= 1.18, the top sloping between (the slice, CAP)"""
    L = 1.5
    lo, hi = VKI_STO_RAKE["lo"], VKI_STO_RAKE["hi"]
    X = (lambda u: u) if side == "L" else (lambda u: L - u)
    top = lambda u: VKI_CUT_H + (3.0 - VKI_CUT_H) * vki_clamp((u - lo) / (hi - lo))
    pa = [(0.0, VKI_FOOT_Z), (lo, VKI_FOOT_Z), (lo, VKI_CUT_H), (0.0, VKI_CUT_H)]
    pb = [(lo, VKI_FOOT_Z), (L, VKI_FOOT_Z), (L, 3.0), (hi, 3.0), (lo, VKI_CUT_H)]
    polys = []
    for p in (pa, pb):
        q = [(X(u), z) for u, z in p]
        if side == "R":
            q = q[::-1]
        polys.append(q)
    vki_cav_body(k, polys)
    H_fn = lambda x: top(x if side == "L" else L - x)
    vki_cav_finish(k, L, H_fn, vki_seed("Cave|rake|" + side))
    k.meta.update(vki_class="wall", vki_cut_to=VKI_CAV_CUT_TO, vki_rake_low="x0" if side == "L" else "xL")


def vki_cav_rake_l(k): vki_cav_rake(k, "L")
def vki_cav_rake_r(k): vki_cav_rake(k, "R")


def vki_cav_post(k, kind, height):
    """a rock mass on the node: +-0.305 (Corner) or +-0.12 x +-0.305 (Mid), -0.30 .. wall top + 0.04, its sides
    faceted inward by up to 3.5 cm below the rim (T4: the square stays covered from above), a CAP slice on top"""
    k.set_family("Cave")
    top = (3.0 if height == "Full" else VKI_CUT_H) + VKI_POST_TOP
    ay = VKI_POST_HW["O"]
    ax = ay if kind == "Corner" else VKI_MID_HW["O"][0]
    before = set(k.bm.verts)
    k.box((0.0, 0.0, (VKI_POST_Z0 + top) / 2), (2 * ax, 2 * ay, top - VKI_POST_Z0), VKI_STONE_BLOCK_IN, bevel=0.0)
    vs = [v for v in k.bm.verts if v not in before]
    grid_cut(k, vs, 0.25)
    vs = [v for v in k.bm.verts if v not in before]
    rnd = random.Random(vki_seed("Cave|post|%s|%s" % (kind, height)))
    for v in vs:
        if VKI_POST_Z0 + 0.05 < v.co.z < top - 0.12:
            if abs(abs(v.co.x) - ax) < 1e-4 and kind == "Corner":
                v.co.x -= math.copysign(rnd.uniform(0.0, 0.035), v.co.x)
            if abs(abs(v.co.y) - ay) < 1e-4:
                v.co.y -= math.copysign(rnd.uniform(0.0, 0.035), v.co.y)
    k.bm.normal_update()
    for f in vki_faces_of(vs):
        f.smooth = False
        if f.normal.z > 0.7 and all(abs(v.co.z - top) < 1e-4 for v in f.verts):
            k.project([f], VKI_CAP)
        else:
            k.project([f], VKI_STONE_BLOCK_IN, tile=1.5)
    for v in vs:
        k.set_dark([v], 0.12 * rnd.random())
    vki_dun_damp(k)
    other = "Cut" if height == "Full" else "Full"
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height,
                                                   "toggle_to": f"SM_VKI_Post_Cave_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any",
                                                   "rule": "§2.3; Cave wins over every other family"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_cav_post_corner_full(k): vki_cav_post(k, "Corner", "Full")
def vki_cav_post_corner_cut(k): vki_cav_post(k, "Corner", "Cut")
def vki_cav_post_mid_full(k): vki_cav_post(k, "Mid", "Full")
def vki_cav_post_mid_cut(k): vki_cav_post(k, "Mid", "Cut")


# ---------------------------------------------------------------- Gap, Passage
VKI_CAV_GAP = dict(x=(0.33, 1.17), arch=(2.00, 2.35))


def vki_cav_gap(k, height, passage=False):
    """a natural opening x 0.33-1.17 through the rock; Full: the rock arches over it from a jagged 2.0-2.35 up to 3.0
    (bulging like the face); passage: a VOID card behind it and the link data (a tunnel mouth)"""
    L = 1.5
    x0, x1 = VKI_CAV_GAP["x"]
    full = height == "Full"
    H = 3.0 if full else VKI_CUT_H
    rnd = random.Random(41)
    polys = [[(0.0, VKI_FOOT_Z), (x0, VKI_FOOT_Z), (x0, H), (0.0, H)], [(x1, VKI_FOOT_Z), (L, VKI_FOOT_Z), (L, H), (x1, H)],
             [(x0, VKI_FOOT_Z), (x1, VKI_FOOT_Z), (x1, -0.10), (x0, -0.10)]]
    if full:
        xs = [x0 + (x1 - x0) * i / 5 for i in range(6)]
        a0, a1 = VKI_CAV_GAP["arch"]
        ra = random.Random(43 + passage)
        zb = {x: a0 + (a1 - a0) * math.sin(math.pi * ((x - x0) / (x1 - x0)) ** 1.3) ** 0.6 + ra.uniform(-0.08, 0.08)
              for x in xs}
        for a, b in zip(xs[:-1], xs[1:]):
            polys.append([(a, zb[a]), (b, zb[b]), (b, H), (a, H)])
    vki_cav_body(k, polys)
    jt = (VKI_CAV_GAP["arch"][0] if full else H) - 0.03                  # ragged jambs: inward only (T3)
    for v in k.bm.verts:
        for xe, sg in ((x0, 1.0), (x1, -1.0)):
            if abs(v.co.x - xe) < 1e-4 and 0.0 < v.co.z < jt:
                v.co.x += sg * 0.07 * vki_vnoise(v.co.z / 0.22, 2.0 + sg, 77)
    vki_cav_finish(k, L, lambda x: H, vki_seed("Cave|gap|%d" % passage),     # Full = Cut below 0.65 (T2)
                   dip=(2.45, 3.0, 0.35) if full else VKI_CAV_DIP["Cut"])
    if passage:
        k.box(((x0 + x1) / 2, 0.21, 1.2), (x1 - x0 + 0.02, 0.015, 2.4), VOID, bevel=0.0)
    for i in range(3):                                                   # rubble at the threshold's sides
        c = (rnd.choice((x0 + 0.08, x1 - 0.08)), rnd.uniform(-0.45, -0.30), 0.04)
        v = _ico(k, c, rnd.uniform(0.05, 0.08), VKI_STONE_BLOCK_IN, scale=(1, 0.8, 0.6), sub=0, jit=0.01, seed=i)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    z1 = VKI_CAV_GAP["arch"][0] if full else H
    k.meta.update(vki_class="wall", vki_nav="door", vki_nav_open=[x0, x1],
                  vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": z1, "head": "natural" if full else "cut",
                               "passage": int(passage)},
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])
    if passage:
        k.meta.update(vki_cut_to=VKI_CAV_CUT_TO, vki_trigger=[0.75, -0.55, 1.0, 0.8, 0.7, 2.0],
                      vki_spawn_local=[0.75, -1.60], vki_prompt_local=[0.75, -0.30, 1.40], vki_prompt_text="Go through")


def vki_cav_gap_full(k): vki_cav_gap(k, "Full")
def vki_cav_gap_cut(k): vki_cav_gap(k, "Cut")
def vki_cav_passage(k): vki_cav_gap(k, "Full", passage=True)


# ---------------------------------------------------------------- specs
VKI_CWL_SPECS = [
    ("SM_VKI_Wall_Cave_Plain_150A_Full", vki_cav_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Cave_Plain_150A_Cut", vki_cav_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Cave_Plain_150B_Full", vki_cav_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Cave_Plain_300_Full", vki_cav_plain_300_full, "wall"),
    ("SM_VKI_Wall_Cave_Plain_300_Cut", vki_cav_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Cave_Rake_150_L", vki_cav_rake_l, "wall"),
    ("SM_VKI_Wall_Cave_Rake_150_R", vki_cav_rake_r, "wall"),
    ("SM_VKI_Wall_Cave_Gap_150_Full", vki_cav_gap_full, "wall"),
    ("SM_VKI_Wall_Cave_Gap_150_Cut", vki_cav_gap_cut, "wall"),
    ("SM_VKI_Wall_Cave_Passage_150_Full", vki_cav_passage, "wall"),
    ("SM_VKI_Post_Cave_Corner_Full", vki_cav_post_corner_full, "wall"),
    ("SM_VKI_Post_Cave_Corner_Cut", vki_cav_post_corner_cut, "wall"),
    ("SM_VKI_Post_Cave_Mid_Full", vki_cav_post_mid_full, "wall"),
    ("SM_VKI_Post_Cave_Mid_Cut", vki_cav_post_mid_cut, "wall"),
]
VKI_CWL_NAMES = [n for n, _, _ in VKI_CWL_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_CWL_SPECS])
