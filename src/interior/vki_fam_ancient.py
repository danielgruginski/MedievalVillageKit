# ===================== VKI FAM ANCIENT: the ruined-temple wall family (adventure kit) =====================
# Adventure kit (docs/ADVENTURE_KIT.md). Package "adventure". Loaded by vki_ns() after vki_fam_dungeon; uses the Stone
# builders (vki_sto_*) and the dungeon helpers (vki_dun_damp, vki_dun_popouts, vki_dun_passage). Every top-level name
# starts with vki_/VKI_ (T18).
# Ancient (class O, T 0.50, H 3.0): huge weathered blocks (T_VKI_AncientIn: courses 0.5 m, blocks 0.75 / 1.5 m), pale
# weathered copings (AncientCap), dressed stone (AncientBlock); on Full walls a frieze course (2.30-2.55, 3 cm proud)
# runs the whole length, so every Full end profile carries it (T2). The dungeon's damp band too. Pieces:
#   Plain 150A / 150B (pop-out blocks) / 300, Rake L / R, posts (a monolithic pier with a capital / a pilaster)
#   Door_150 / DoorWide_300   trilithons: monolithic jambs 4 cm proud of both faces under a massive lintel with a row of
#                             carved roundels (Cut: the jambs under the coping)
#   Broken_150 / _300_Full    ruin: intact at both ends, the middle broken down to 1.0-2.3 m in a jagged line, loose
#                             blocks on the break and fallen ones on the floor in front (no Cut twin)
#   Collapsed_150_Cut         the lower metre broken down to 0.3-0.7 m with a grit and block spill into the room
#   Relief_150_Full           a carved guardian face on a proud panel
#   Vault_300_Full            a round sealed vault door: a ring of voussoirs round a 2.1 m circular opening, closed by
#                             Leaf_VaultDisc_300 (a carved stone disc with a gold sigil; it rolls aside)
#   Passage_150_Full          the dungeon's breach (a scene link) in ancient masonry
# Transitions (walls that break into caves), for the Dungeon and the Ancient family: Wall_<fam>_Breach_150 / _300,
#   Full and Cut (VKI_BRK_NAMES) -- the wall knocked through to the floor, rubble spilling to both sides; passable
# Build: g["vki_ws_build"]("adventure", VKI_ANC_NAMES); test: g["vki_test_pieces"](VKI_ANC_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_ANC_CUT_TO = "SM_VKI_Wall_Ancient_Plain_150A_Cut"
VKI_ANC_TEX = dict(seed=81, T=1.5, blocks=(2, 1, 2), wjit=0.20, min_sep=0.25, rows=(0.52, 0.46, 0.52))
VKI_ANC_FRIEZE = dict(z=(2.30, 2.55), y=(-0.28, -0.18))


def vki_anc_patch(k, leaf=None):
    """Stone / dungeon-built geometry -> Ancient: family, damp band, cut target"""
    k.set_family("Ancient")
    vki_dun_damp(k)
    if k.meta.get("vki_cut_to") in (VKI_STO_CUT_TO, VKI_DUN_CUT_TO):
        k.meta["vki_cut_to"] = VKI_ANC_CUT_TO
    if leaf:
        k.meta["vki_leaf"] = leaf


def vki_anc_frieze(k, spans):
    """the frieze course on face A over each [x0, x1] span, in units on the piece's 0.75 grid (bevelled: V-joints)"""
    (z0, z1), (y0, y1) = VKI_ANC_FRIEZE["z"], VKI_ANC_FRIEZE["y"]
    for a, b in spans:
        cuts = [a] + [0.75 * i for i in range(1, 5) if a + 1e-6 < 0.75 * i < b - 1e-6] + [b]
        for u0, u1 in zip(cuts[:-1], cuts[1:]):
            vki_sto_block(k, u0, u1, z0, z1, y0, y1, key="frz%d" % int(u0 * 100), dark=0.04)


def vki_anc_strip(k, xs, zlo, zhi):
    """rubble-core body between consecutive xs, bottoms zlo(x) and tops zhi(x) (convex quads), flagged body"""
    before = set(k.bm.verts)
    for a, b in zip(xs[:-1], xs[1:]):
        vs, fs = vki_prism(k, [(a, zlo(a)), (b, zlo(b)), (b, zhi(b)), (a, zhi(a))], -k.T / 2, k.T / 2, VKI_WALL_A,
                           axis="y")
        for f in fs:
            if f.normal.y > 0.7:
                k.project([f], VKI_WALL_B)
        grid_cut(k, vs, 0.25)
    new = [v for v in k.bm.verts if v not in before]
    k.mark_body(new)
    return new


# ---------------------------------------------------------------- Plain, Rake, posts
def vki_anc_plain(k, L, height, variant="A", popouts=False):
    full = height == "Full"
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    vki_sto_body(k, 0.0, L, VKI_FOOT_Z, zb)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    if full:
        vki_anc_frieze(k, [(0.0, L)])
    pops = vki_dun_popouts(k, VKI_ANC_TEX, "Ancient") if popouts else 0
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Ancient", variant, holes=[], top_body_fn=lambda x: zb)
    vki_dun_damp(k)
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_ANC_CUT_TO, vki_popouts=pops)


def vki_anc_plain_150a_full(k): vki_anc_plain(k, 1.5, "Full", "A")
def vki_anc_plain_150a_cut(k): vki_anc_plain(k, 1.5, "Cut", "A")
def vki_anc_plain_150b_full(k): vki_anc_plain(k, 1.5, "Full", "B", popouts=True)
def vki_anc_plain_300_full(k): vki_anc_plain(k, 3.0, "Full", "A")
def vki_anc_plain_300_cut(k): vki_anc_plain(k, 3.0, "Cut", "A")


def vki_anc_rake(k, side):
    vki_sto_rake(k, side)
    hi = VKI_STO_RAKE["hi"]
    vki_anc_frieze(k, [(hi, 1.5)] if side == "L" else [(0.0, 1.5 - hi)])
    vki_anc_patch(k)


def vki_anc_rake_l(k): vki_anc_rake(k, "L")
def vki_anc_rake_r(k): vki_anc_rake(k, "R")


VKI_ANC_POST_Z = {"Full": (-0.30, 0.25, 2.62, 3.04), "Cut": (-0.30, 0.25, 0.92, 1.04)}


def vki_anc_post(k, kind, height):
    """Corner: a monolithic pier -- plinth +-0.31, shaft +-0.295, capital +-0.31 with a CAP top; Mid: the same as a
    pilaster (+-0.12 along the wall)"""
    k.set_family("Ancient")
    z0, z1, z2, z3 = VKI_ANC_POST_Z[height]
    ay = VKI_POST_HW["O"]
    ax = ay if kind == "Corner" else VKI_MID_HW["O"][0]
    sx = ax - 0.015 if kind == "Corner" else ax
    vki_sto_block(k, -ax, ax, z0, z1, -ay, ay, bev=VKI_POST_BEVEL, key="apl%s" % kind)
    vki_sto_block(k, -sx, sx, z1, z2, -(ay - 0.015), ay - 0.015, bev=VKI_POST_BEVEL, key="ash%s" % kind, dark=0.03)
    vki_sto_block(k, -ax, ax, z2, z3, -ay, ay, bev=VKI_POST_BEVEL, top=VKI_CAP, key="acp%s" % kind)
    vki_dun_damp(k)
    other = "Cut" if height == "Full" else "Full"
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height,
                                                   "toggle_to": f"SM_VKI_Post_Ancient_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any",
                                                   "rule": "§2.3; Cave > Ancient > Dungeon > Stone ... in priority"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_anc_post_corner_full(k): vki_anc_post(k, "Corner", "Full")
def vki_anc_post_corner_cut(k): vki_anc_post(k, "Corner", "Cut")
def vki_anc_post_mid_full(k): vki_anc_post(k, "Mid", "Full")
def vki_anc_post_mid_cut(k): vki_anc_post(k, "Mid", "Cut")


# ---------------------------------------------------------------- trilithon doors
def vki_anc_roundels(k, xs, z, y):
    """small carved discs on a lintel face (proud 1.5 cm), pale"""
    for x in xs:
        _cyl(k, (x, y, z), 0.055, 0.055, 0.03, 10, VKI_CAP, rot=Matrix.Rotation(math.pi / 2, 4, "X"))


def vki_anc_door(k, height, wide=False):
    """trilithon doorway: 150 -- clear x 0.33-1.17 under a lintel at 2.20; 300 -- clear x 0.60-2.40 under 2.35.
    Monolithic jambs (0.16 wide, 4 cm proud of both faces) stand on the floor; the lintel (5 cm proud, carved
    roundels) spans past them; Cut keeps the jambs under the coping units that wrap the reveals"""
    L = 3.0 if wide else 1.5
    full = height == "Full"
    x0, x1 = (0.60, 2.40) if wide else (0.33, 1.17)
    top, ltop = (2.35, 2.80) if wide else (2.20, 2.62)
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    T2 = k.T / 2
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)
    vki_sto_block(k, x0, x1, 0.0, 0.03, -0.26, 0.26, bev=0.01, dark=0.12, key="athr")                  # worn step
    jt = top + 0.04 if full else zb + VKI_STO_TUCK
    vki_sto_block(k, x0 - 0.17, x0 - 0.01, 0.0, jt, -0.29, 0.29, key="ajl")
    vki_sto_block(k, x1 + 0.01, x1 + 0.17, 0.0, jt, -0.29, 0.29, key="ajr")
    if full:
        vki_sto_block(k, x0 - 0.23, x1 + 0.23, top, ltop, -0.30, 0.30, key="alint")
        vki_sto_body(k, x0, x1, ltop, zb)
        n = 7 if wide else 5
        vki_anc_roundels(k, [x0 + (x1 - x0) * (i + 0.5) / n for i in range(n)], (top + ltop) / 2, -0.30)
        vki_sto_coping(k, 0.0, L, zb, zt, L)
        vki_anc_frieze(k, [(0.0, x0 - 0.23 + 0.05), (x1 + 0.23 - 0.05, L)])
        holes = [(x0 - 0.17, 0.0, x1 + 0.17, ltop)]
        z1 = top
    else:
        vki_sto_coping(k, 0.0, x0, zb, zt, L, fixed=True)
        vki_sto_coping(k, x1, L, zb, zt, L, fixed=True)
        holes = [(x0 - 0.17, 0.0, x1 + 0.17, zt)]
        z1 = zt
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Ancient", "A", holes=holes, top_body_fn=lambda x: zb)
    vki_anc_patch(k)
    cx = (x0 + x1) / 2
    k.meta.update(vki_class="wall", vki_nav="door", vki_nav_open=[x0, x1],
                  vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": round(z1, 4), "head": "lintel" if full else "cut"},
                  vki_trigger=[cx, -0.65, 1.0, x1 - x0 + 0.06, 0.8, 2.0], vki_spawn_local=[cx, -1.60],
                  vki_prompt_local=[cx, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])
    if wide:
        k.meta.update(vki_leaf_socket=[[x0, -T2 + 0.05, 0.0], [x1, -T2 + 0.05, 0.0]], vki_leaf_open_deg=90)
    else:
        k.meta.update(vki_leaf_socket=[x0, -T2 + 0.05, 0.0], vki_leaf_open_deg=90,
                      vki_leaf="SM_VKI_Leaf_Plank_" + height)


def vki_anc_door_full(k): vki_anc_door(k, "Full")
def vki_anc_door_cut(k): vki_anc_door(k, "Cut")
def vki_anc_door_wide_full(k): vki_anc_door(k, "Full", wide=True)
def vki_anc_door_wide_cut(k): vki_anc_door(k, "Cut", wide=True)


# ---------------------------------------------------------------- ruins
def vki_anc_rubble(k, xs_range, rnd, n, y=(-0.95, -0.40), s=(0.14, 0.30), mi=None):
    """fallen blocks on the floor on the room side (x inside xs_range, clear of the node zones)"""
    mi = VKI_STONE_BLOCK_IN if mi is None else mi
    for i in range(n):
        sz = rnd.uniform(*s)
        c = (rnd.uniform(*xs_range), rnd.uniform(*y), sz * 0.40)
        vs = list(set(k.box(c, (sz, sz * rnd.uniform(0.6, 0.9), sz * 0.8), mi,
                            rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, math.pi)),
                            bevel=0.02, jitter=0.012, seed=rnd.randint(0, 10 ** 6))))
        k.set_dark(vs, rnd.uniform(0.05, 0.2))


def vki_anc_broken(k, L):
    """intact at both ends (0-0.35 and L-0.35..L: full section, coping, frieze), the middle broken down along a jagged
    line (1.2-2.3 m on 150, 0.9-2.0 on 300) whose top shows the rubble core (dressed-stone tops), loose blocks on the
    break, fallen blocks on the floor in front"""
    zb, zt = VKI_STO_FULL
    e = 0.35
    rnd = random.Random(int(L * 100) + 3)
    vki_sto_body(k, 0.0, e, VKI_FOOT_Z, zb)
    vki_sto_body(k, L - e, L, VKI_FOOT_Z, zb)
    lo, hi = (1.2, 2.3) if L < 2 else (0.9, 2.0)
    n = int(round((L - 2 * e) / 0.16))
    xs = [e + (L - 2 * e) * i / n for i in range(n + 1)]
    jag = {}
    z = hi
    for i, x in enumerate(xs):
        z = max(lo, min(hi, z + rnd.uniform(-0.35, 0.25)))
        jag[x] = hi + 0.25 if i in (0, n) else z                       # the break climbs to the intact ends
    zhi = lambda x: jag[min(jag, key=lambda a: abs(a - x))]
    vki_anc_strip(k, xs, lambda x: VKI_FOOT_Z, zhi)
    vki_sto_coping(k, 0.0, e, zb, zt, L, fixed=True)
    vki_sto_coping(k, L - e, L, zb, zt, L, fixed=True)
    vki_anc_frieze(k, [(0.0, e - 0.02), (L - e + 0.02, L)])          # 2 cm short of the break (T5S)
    for i in range(2 if L < 2 else 4):                                                   # loose blocks on the break
        x = e + 0.15 + (L - 2 * e - 0.3) * (i + 0.5) / (2 if L < 2 else 4)
        zz = zhi(x)
        vs = list(set(k.box((x, rnd.uniform(-0.05, 0.05), zz + 0.10), (0.30, 0.34, 0.20), VKI_STONE_BLOCK_IN,
                            rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.4, 0.4)),
                            bevel=0.02, jitter=0.01, seed=40 + i)))
        k.set_dark(vs, 0.08)
    vki_anc_rubble(k, (e + 0.25, L - e - 0.25), rnd, 3 if L < 2 else 6, s=(0.14, 0.26))     # clear of the node zones
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Ancient", "A", holes=[(e, 0.0, L - e, 3.0)], top_body_fn=lambda x: zb)
    vki_anc_patch(k)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_ANC_CUT_TO, vki_broken=1,
                  vki_broken_note="the break's top is 0.9-2.3 m: it still blocks; fallen blocks lie up to 1 m in front")


def vki_anc_broken_150(k): vki_anc_broken(k, 1.5)
def vki_anc_broken_300(k): vki_anc_broken(k, 3.0)


def vki_anc_collapsed(k):
    """Cut piece: intact ends (the Cut section, coping units), the middle broken down to 0.3-0.7 m, a mound of grit with
    blocks spilling into the room"""
    L = 1.5
    zb, zt = VKI_STO_CUT
    e = 0.35
    rnd = random.Random(77)
    vki_sto_body(k, 0.0, e, VKI_FOOT_Z, zb)
    vki_sto_body(k, L - e, L, VKI_FOOT_Z, zb)
    xs = [e + (L - 2 * e) * i / 5 for i in range(6)]
    jag = {x: (0.80 if i in (0, 5) else rnd.uniform(0.30, 0.70)) for i, x in enumerate(xs)}
    zhi = lambda x: jag[min(jag, key=lambda a: abs(a - x))]
    vki_anc_strip(k, xs, lambda x: VKI_FOOT_Z, zhi)
    vki_sto_coping(k, 0.0, e, zb, zt, L, fixed=True)
    vki_sto_coping(k, L - e, L, zb, zt, L, fixed=True)
    vki_dpr_mound(k, (0.75, -0.45, 0.0), 0.34, 0.30, 0.22, VKI_ASH, z0=0.001, nr=2, ns=10, seed=13, wob=0.10, bump=0.2)
    vki_anc_rubble(k, (0.58, 0.92), rnd, 2, y=(-0.70, -0.30), s=(0.12, 0.20))                 # T3: node zones clear
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Ancient", "A", holes=[(e, 0.0, L - e, 1.0)], top_body_fn=lambda x: zb)
    vki_anc_patch(k)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_ANC_CUT_TO, vki_broken=1)


def vki_anc_relief(k):
    """plain Full wall with a carved panel (x 0.36-1.14, z 0.95-2.20, 5 cm proud, framed): a stern guardian face --
    brow, eyes and mouth sunk dark, a wedge nose, a crown of three points -- the features pale (CAP)"""
    vki_anc_plain(k, 1.5, "Full", "A")
    vki_sto_block(k, 0.36, 1.14, 0.95, 2.20, -0.30, -0.20, key="rpan", dark=0.06)
    for (a, b, c, d) in ((0.36, 1.14, 2.12, 2.20), (0.36, 1.14, 0.95, 1.03), (0.36, 0.44, 1.03, 2.12),
                         (1.06, 1.14, 1.03, 2.12)):
        vki_sto_block(k, a, b, c, d, -0.315, -0.28, bev=0.008, key="rfr%d" % int(c * 100 + a * 10))
    vki_sto_block(k, 0.50, 1.00, 1.80, 1.88, -0.335, -0.28, mi=VKI_CAP, bev=0.01, key="rbrow")
    for x in (0.63, 0.87):
        k.box((x, -0.302, 1.70), (0.12, 0.012, 0.075), VOID, bevel=0.0)
    vki_prism(k, [(0.72, 1.44), (0.78, 1.44), (0.765, 1.74), (0.735, 1.74)], -0.345, -0.28, VKI_CAP, axis="y", bevel=0.005)
    k.box((0.75, -0.302, 1.29), (0.30, 0.012, 0.05), VOID, bevel=0.0)
    for x in (0.60, 0.75, 0.90):
        vki_prism(k, [(x - 0.05, 1.89), (x + 0.05, 1.89), (x, 2.05)], -0.325, -0.285, VKI_CAP, axis="y", bevel=0.004)
    k.meta.update(vki_relief=1, vki_cut_to=VKI_ANC_CUT_TO,
                  vki_relief_note="panel 5 cm proud (|y| 0.30-0.345): nothing wall-backed in front of it")


# ---------------------------------------------------------------- the round vault door
VKI_ANC_VAULT = dict(cx=1.5, cz=1.12, r=1.05, ring=(0.24, 0.26, 0.25, 0.27, 0.25, 0.24, 0.26, 0.25, 0.27, 0.25, 0.24,
                                                     0.26), nav=(0.90, 2.10))


def vki_anc_vault(k):
    """a circular opening (r 1.05 about (1.5, 1.12): bottom 7 cm above the floor) in a ring of 12 voussoirs 5 cm proud
    of both faces; rubble body above and below the circle; closed by Leaf_VaultDisc_300 (socket (1.5, 0))"""
    L = 3.0
    V = VKI_ANC_VAULT
    cx, cz, r = V["cx"], V["cz"], V["r"]
    zb, zt = VKI_STO_FULL
    rb = r + 0.10
    e0, e1 = cx - rb, cx + rb
    vki_sto_body(k, 0.0, e0, VKI_FOOT_Z, zb)
    vki_sto_body(k, e1, L, VKI_FOOT_Z, zb)
    n = 12
    xs = [e0 + (e1 - e0) * i / n for i in range(n + 1)]
    dz = lambda x: math.sqrt(max(rb * rb - (x - cx) ** 2, 0.0))
    vki_anc_strip(k, xs, lambda x: cz + dz(x), lambda x: zb)
    vki_anc_strip(k, xs, lambda x: VKI_FOOT_Z, lambda x: max(cz - dz(x), VKI_FOOT_Z + 0.02))
    # the ring starts at 15 deg: no voussoir joint is vertical, so none lies in a body strip's side plane (T5S)
    vki_sto_ring(k, cx, cz, r, V["ring"], math.pi / 12, 2 * math.pi + math.pi / 12, -0.30, 0.30, key="vault")
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    vki_anc_frieze(k, [(0.0, 0.95), (2.05, L)])
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Ancient", "A", holes=[(cx - r - 0.3, 0.0, cx + r + 0.3, cz + r + 0.3)], top_body_fn=lambda x: zb)
    vki_anc_patch(k)
    a0, a1 = V["nav"]
    k.meta.update(vki_class="wall", vki_cut_to=VKI_ANC_CUT_TO, vki_nav="door", vki_nav_open=[a0, a1],
                  vki_opening={"x0": round(cx - r, 3), "x1": round(cx + r, 3), "z0": round(cz - r, 3),
                               "z1": round(cz + r, 3), "head": "circle", "vault": 1},
                  vki_leaf="SM_VKI_Leaf_VaultDisc_300", vki_leaf_socket=[cx, 0.0, 0.0],
                  vki_leaf_open_socket=[cx + 1.15, -0.45, 0.0],
                  vki_collider=[[a0 / 2, 0.0, 1.1, a0, k.T, 2.2], [(a1 + L) / 2, 0.0, 1.1, L - a1, k.T, 2.2]])


def vki_anc_leaf_vault(k):
    """the vault's stone disc (r 1.02, 0.28 thick, centred at local (0, 0, 1.12) in the wall plane): three carved
    rings and a sun sigil with a gold boss on the room face; it rolls aside (vki_leaf_motion roll_x)"""
    cz = VKI_ANC_VAULT["cz"]
    rx = Matrix.Rotation(math.pi / 2, 4, "X")
    dv = _cyl(k, (0.0, 0.0, cz), 1.02, 1.02, 0.28, 24, VKI_STONE_BLOCK_IN, rot=rx)
    k.project(vki_faces_of(dv), VKI_STONE_BLOCK_IN, tile=1.5)
    for (ri, ro) in ((0.93, 0.99), (0.68, 0.74), (0.40, 0.46)):
        vki_home_hoop(k, (0.0, -0.14, cz), ri, ro, 0.03, segs=20, mi=VKI_CAP, rot=rx.to_3x3())
    _cyl(k, (0.0, -0.155, cz), 0.17, 0.15, 0.04, 12, VKI_DPR_GOLD, rot=rx)
    for i in range(8):
        a = 2 * math.pi * i / 8
        c = (math.cos(a) * 0.27, -0.148, cz + math.sin(a) * 0.27)
        k.box(c, (0.14, 0.02, 0.04), VKI_CAP, rot=(0.0, -a, 0.0), bevel=0.0)
    vki_dpr_gold_mats(k)
    k.meta.update(vki_class="leaf", hinge_axis="none (rolls along local X)", vki_leaf_motion="roll_x",
                  vki_leaf_state="closed", vki_openable=1, vki_locked=1,
                  vki_leaf_fits="SM_VKI_Wall_Ancient_Vault_300_Full at vki_leaf_socket (closed) or "
                                "vki_leaf_open_socket (rolled aside), same rotation")


def vki_anc_passage(k):
    """the dungeon's breach (vki_dun_passage) in ancient masonry, with the frieze on the intact piers"""
    vki_dun_passage(k)
    vki_anc_frieze(k, [(0.0, 0.31), (1.19, 1.5)])                    # 2 cm short of the reveals (T5S)
    vki_anc_patch(k)


# ---------------------------------------------------------------- transitions: breaches (Dungeon and Ancient)
VKI_BRK = {1.5: dict(e=0.12, open=(0.33, 1.17), hi=(2.45, 2.15)), 3.0: dict(e=0.20, open=(0.90, 2.10), hi=(2.50, 2.25))}
VKI_BRK_LO = 0.70                  # the reveals' top: every break vertex stays above 0.65, so Full = Cut below it (T2)


def vki_brk_breach(k, L, height, fam):
    """a breach knocked through the wall to the floor (adventure kit, transitions: a room broken into a cave, or two
    rooms): intact at both ends (the plain section and coping over x 0-e and L-e..L; Ancient Full: the frieze), the
    masonry between broken down in ragged steps (Full from ~2.5 m, Cut from 0.85 m) to reveals 0.70 m tall either side
    of a clear opening (150: x 0.33-1.17; 300: x 0.90-2.10), the rubble core on the break (loose blocks on the Full
    break), grit mounds and fallen blocks spilling to BOTH sides over the floor seam. Passable (vki_nav door); no scene
    link, no leaf. Full and Cut are twins: identical below 0.65."""
    full = height == "Full"
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    D = VKI_BRK[L]
    e = D["e"]
    x0, x1 = D["open"]
    rnd = random.Random(vki_seed("Breach|%s|%g" % (fam, L)) % 1000003)      # never the height: Full = Cut below 0.65
    vki_sto_body(k, 0.0, e, VKI_FOOT_Z, zb)
    vki_sto_body(k, L - e, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)                     # footing under the opening
    lo = VKI_BRK_LO
    tops = []
    for (a, b, hi, rise) in ((e, x0, D["hi"][0], False), (x1, L - e, D["hi"][1], True)):
        n = max(2, int(round((b - a) / 0.14)))
        xs = [a + (b - a) * i / n for i in range(n + 1)]
        jit = [rnd.uniform(-1.0, 1.0) for _ in xs]
        zs = []
        for i, x in enumerate(xs):
            t = i / n if not rise else 1.0 - i / n                           # 0 at the intact end, 1 at the reveal
            if full:
                z = lo + (hi - lo) * (1.0 - t) ** 1.3 + (0.14 * jit[i] if 0 < i < n else 0.0)
            else:
                z = lo + (0.85 - lo) * (1.0 - t) + (0.03 * jit[i] if 0 < i < n else 0.0)
            zs.append(max(lo, min(zb - 0.05, z)))
        jag = dict(zip(xs, zs))
        vki_anc_strip(k, xs, lambda x: VKI_FOOT_Z, lambda x, jag=jag: jag[min(jag, key=lambda q: abs(q - x))])
        tops.append((xs, zs))
    vki_sto_coping(k, 0.0, e, zb, zt, L, fixed=True)
    vki_sto_coping(k, L - e, L, zb, zt, L, fixed=True)
    if full and fam == "Ancient":
        vki_anc_frieze(k, [(0.0, e - 0.02), (L - e + 0.02, L)])              # 2 cm short of the break (T5S)
    # the spill (identical in both heights): a rubble floor across the opening, grit mounds and fallen blocks on both sides
    vki_sto_block(k, x0 - 0.01, x1 + 0.01, 0.0, 0.03, -0.29, 0.29, mi=VKI_FLOOR, bev=0.0, dark=0.15)
    for sgn in (-1, 1):                                      # earth spilt from the cave (the FLOOR slot: EarthDamp)
        cx = L / 2 + sgn * 0.08 * (L / 1.5)
        vki_dpr_mound(k, (cx, sgn * 0.60, 0.0), 0.36 * (L / 1.5) ** 0.7, 0.32, 0.12, VKI_FLOOR, z0=0.001, nr=2, ns=8,
                      seed=13 + sgn, wob=0.14, bump=0.3)
        for i in range(3 if L < 2 else 5):                                   # fallen blocks (one bevelled: budget)
            sz = rnd.uniform(0.12, 0.24)
            c = (rnd.uniform(0.42, L - 0.42), sgn * rnd.uniform(0.45, 0.95), sz * 0.40)
            vs = list(set(k.box(c, (sz, sz * rnd.uniform(0.6, 0.9), sz * 0.8), VKI_STONE_BLOCK_IN,
                                rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, math.pi)),
                                bevel=0.02 if i == 0 else 0.0, jitter=0.012, seed=rnd.randint(0, 10 ** 6))))
            k.set_dark(vs, rnd.uniform(0.05, 0.2))
    if full:                                                                  # loose blocks on the break
        for i, (xs, zs) in enumerate(tops):
            m = max(range(len(xs) - 1), key=lambda q: min(zs[q], zs[q + 1]))
            x = (xs[m] + xs[m + 1]) / 2
            z = min(zs[m], zs[m + 1])
            vs = list(set(k.box((x, rnd.uniform(-0.04, 0.04), z + 0.07), (0.16, 0.26, 0.14), VKI_STONE_BLOCK_IN,
                                rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.4, 0.4)),
                                bevel=0.02, jitter=0.01, seed=60 + i)))
            k.set_dark(vs, 0.10)
    vki_sto_body_finish(k)
    vki_wobble(k, L, fam, "A", holes=[(e, 0.0, L - e, 3.0)], top_body_fn=lambda x: zb)
    (vki_anc_patch if fam == "Ancient" else vki_dun_patch)(k)
    k.slot_mats[VKI_FLOOR] = "EarthDamp"
    k.meta.update(vki_class="wall", vki_nav="door", vki_nav_open=[x0, x1], vki_breach=1,
                  vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": zt, "head": "breach"},
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]],
                  vki_breach_note="rubble lies up to 0.95 m out on both sides; the floor seam under the opening is "
                                  "covered (a room's flagstones meeting a cave floor)")


VKI_BRK_SPECS = [("SM_VKI_Wall_%s_Breach_%d_%s" % (f_, int(L_ * 100), h_),
                  (lambda k, f_=f_, L_=L_, h_=h_: vki_brk_breach(k, L_, h_, f_)), "wall")
                 for f_ in ("Dungeon", "Ancient") for L_ in (1.5, 3.0) for h_ in ("Full", "Cut")]
VKI_BRK_NAMES = [n for n, _, _ in VKI_BRK_SPECS]


# ---------------------------------------------------------------- specs
VKI_ANC_SPECS = [
    ("SM_VKI_Wall_Ancient_Plain_150A_Full", vki_anc_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Ancient_Plain_150A_Cut", vki_anc_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Ancient_Plain_150B_Full", vki_anc_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Ancient_Plain_300_Full", vki_anc_plain_300_full, "wall"),
    ("SM_VKI_Wall_Ancient_Plain_300_Cut", vki_anc_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Ancient_Rake_150_L", vki_anc_rake_l, "wall"),
    ("SM_VKI_Wall_Ancient_Rake_150_R", vki_anc_rake_r, "wall"),
    ("SM_VKI_Wall_Ancient_Door_150_Full", vki_anc_door_full, "wall"),
    ("SM_VKI_Wall_Ancient_Door_150_Cut", vki_anc_door_cut, "wall"),
    ("SM_VKI_Wall_Ancient_DoorWide_300_Full", vki_anc_door_wide_full, "wall"),
    ("SM_VKI_Wall_Ancient_DoorWide_300_Cut", vki_anc_door_wide_cut, "wall"),
    ("SM_VKI_Wall_Ancient_Broken_150_Full", vki_anc_broken_150, "wall"),
    ("SM_VKI_Wall_Ancient_Broken_300_Full", vki_anc_broken_300, "wall"),
    ("SM_VKI_Wall_Ancient_Collapsed_150_Cut", vki_anc_collapsed, "wall"),
    ("SM_VKI_Wall_Ancient_Relief_150_Full", vki_anc_relief, "wall"),
    ("SM_VKI_Wall_Ancient_Vault_300_Full", vki_anc_vault, "wall"),
    ("SM_VKI_Wall_Ancient_Passage_150_Full", vki_anc_passage, "wall"),
    ("SM_VKI_Post_Ancient_Corner_Full", vki_anc_post_corner_full, "wall"),
    ("SM_VKI_Post_Ancient_Corner_Cut", vki_anc_post_corner_cut, "wall"),
    ("SM_VKI_Post_Ancient_Mid_Full", vki_anc_post_mid_full, "wall"),
    ("SM_VKI_Post_Ancient_Mid_Cut", vki_anc_post_mid_cut, "wall"),
    ("SM_VKI_Leaf_VaultDisc_300", vki_anc_leaf_vault, "prop"),
]
VKI_ANC_NAMES = [n for n, _, _ in VKI_ANC_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_ANC_SPECS + VKI_BRK_SPECS])
