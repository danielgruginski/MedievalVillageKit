# ===================== VKI FAM SEWER: the sewers -- brick walls, channel tiles, sewer props (sewer kit) =====================
# Sewer kit (docs/SEWER_KIT.md). Package "adventure". Loaded by vki_ns() after vki_fam_cavewall; uses the Stone
# builders (vki_sto_*), the dungeon helpers (vki_dun_plain, vki_dun_damp), the breaches (vki_brk_breach) and at build
# time the prop helpers (vki_dpr_*, vki_home_*). Every top-level name starts with vki_/VKI_ (T18).
# A sewer level is a cave map (R["cave"]): the ground between the tunnels is rock, the tunnels are brick walls drawn
# on the map's inner grid lines (backed by the rock: the wall-backed tiles), and the channels are painted cells.
# Sewer (class O, T 0.50, H 3.0): the Stone family's construction in old wet brick (T_VKI_SewerBrick), a dressed
#   stone coping (SewerCap) and dressed stone (SewerBlock), a slime band toward the floor. Pieces:
#     Plain 150A / 150B (a barred drain low in face A) / 300, Full and Cut; Rake L / R; posts
#     Door_150        a brick round arch (Stone's door), Full and Cut
#     Culvert_150     the channel passes under the wall: a low brick arch (crown 0.88) over x 0.33-1.17 from the
#                     footing's bottom, iron bars across it; Full and Cut (twins below 0.65); nav block
#     Outfall_150_Full  a pipe mouth in a stone ring over a projecting lip; the water falls in a sheet into the channel
#                     below (put it over a channel's end)
#     Ladder_150_Full   iron rungs up to a manhole: a scene link (R["passages"], prompt "Climb up")
#     Passage_150_Full  a dark brick tunnel mouth: a scene link (the door arch with darkness behind)
#     Breach_150 / _300, Full and Cut (vki_brk_breach): knocked through into a cave
# Channels (sewer kit): cells coded "ww" in a cave map. Dual-grid channel tiles (class "ground", on the nodes, like the
#   chasm's): SM_VKI_Ground_Sewer_<code>, code SW SE NE NW with X (channel) / O, five rotation classes (OOOX, OOXX,
#   OXOX, OXXX, XXXX), rotated to fit. A tile carries the channel over its X quarters only -- dressed rims 0.15 wide
#   (kerb 4 cm proud) along every edge where the channel meets floor, murky water at -0.28, a dark bed at -0.75 -- and
#   no floor, so the cells round a channel keep whole floors (vki_covers_floor lists the X quarters; the colliders are
#   soft: a bridge's deck crosses them).
# Props: Prop_Bridge_Sewer (a stone slab over a one-cell channel, vki_bridge deck), Prop_Sluice (a sluice gate in a
#   timber frame across a channel, handwheel), Overlay_Sludge (a slick of sludge).
# Build: g["vki_ws_build"]("adventure", VKI_SEW_NAMES); test: g["vki_test_pieces"](VKI_SEW_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_SEW_CUT_TO = "SM_VKI_Wall_Sewer_Plain_150A_Cut"
VKI_SEW_SLIME = (0.30, 0.75)                   # the slime band: darkening toward the floor, gone by 0.75 m
VKI_SEW_CH = dict(water=-0.28, bed=-0.75, rim=0.15, kerb=0.04)
VKI_SEW_CULVERT = dict(spring=0.36, r=0.42, depth=0.10)   # voussoir ring 0.42-0.52: crown 0.88, under the Cut coping


# ---------------------------------------------------------------- family patch, walls
def vki_sew_patch(k, leaf=None):
    """Stone / dungeon-built geometry -> Sewer: family (materials, metadata), slime band, the Sewer cut target"""
    k.set_family("Sewer")
    vki_dun_damp(k, VKI_SEW_SLIME[0], VKI_SEW_SLIME[1])
    if k.meta.get("vki_cut_to") in (VKI_STO_CUT_TO, VKI_DUN_CUT_TO):
        k.meta["vki_cut_to"] = VKI_SEW_CUT_TO
    if leaf:
        k.meta["vki_leaf"] = leaf


def vki_sew_drain(k):
    """a barred drain low in face A: a dressed frame (x 0.50-1.00, z 0.08-0.50, 3 cm proud), darkness, four bars"""
    vki_sto_block(k, 0.50, 1.00, 0.08, 0.50, -0.28, -0.20, key="drain", dark=0.10)
    k.box((0.75, -0.2838, 0.29), (0.36, 0.0075, 0.28), VOID, bevel=0.0)
    for x in (0.63, 0.71, 0.79, 0.87):
        k.box((x, -0.2905, 0.29), (0.022, 0.012, 0.30), IRON, bevel=0.0)


def vki_sew_plain(k, L, height, variant="A"):
    vki_dun_plain(k, L, height, "A")
    if variant == "B":
        vki_sew_drain(k)
    vki_sew_patch(k)
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_SEW_CUT_TO, vki_drain=[0.75, -0.30, 0.29])


def vki_sew_plain_150a_full(k): vki_sew_plain(k, 1.5, "Full")
def vki_sew_plain_150a_cut(k): vki_sew_plain(k, 1.5, "Cut")
def vki_sew_plain_150b_full(k): vki_sew_plain(k, 1.5, "Full", "B")
def vki_sew_plain_300_full(k): vki_sew_plain(k, 3.0, "Full")
def vki_sew_plain_300_cut(k): vki_sew_plain(k, 3.0, "Cut")
def vki_sew_rake_l(k): vki_sto_rake(k, "L"); vki_sew_patch(k)
def vki_sew_rake_r(k): vki_sto_rake(k, "R"); vki_sew_patch(k)
def vki_sew_door_full(k): vki_sto_door(k, "Full"); vki_sew_patch(k, "SM_VKI_Leaf_Plank_Full")
def vki_sew_door_cut(k): vki_sto_door(k, "Cut"); vki_sew_patch(k, "SM_VKI_Leaf_Iron_Cut")


def vki_sew_post(k, kind, height):
    vki_sto_post(k, kind, height)
    vki_sew_patch(k)
    r = dict(k.meta["vki_post_rule"])
    r["toggle_to"] = r["toggle_to"].replace("_Stone_", "_Sewer_")
    r["rule"] = r["rule"].replace("Stone wins over every other family", "Sewer wins over the lower families")
    k.meta["vki_post_rule"] = r


def vki_sew_post_corner_full(k): vki_sew_post(k, "Corner", "Full")
def vki_sew_post_corner_cut(k): vki_sew_post(k, "Corner", "Cut")
def vki_sew_post_mid_full(k): vki_sew_post(k, "Mid", "Full")
def vki_sew_post_mid_cut(k): vki_sew_post(k, "Mid", "Cut")


def vki_sew_culvert(k, height):
    """the channel passes under the wall: piers x 0-0.33 / 1.17-1.5 (the plain section at the ends), a low brick
    arch (voussoirs 0.42-0.52 about (0.75, 0.36): crown 0.88) over the clear opening x 0.33-1.17, open from the
    footing's bottom (-0.30, under the channel's water at -0.28); iron bars across it; the wall above; Full = Cut below
    0.65. Nav block: the channel is not walked."""
    L = 1.5
    full = height == "Full"
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    x0, x1 = VKI_STO_OPEN
    C = VKI_SEW_CULVERT
    sp, r, dp = C["spring"], C["r"], C["depth"]
    cx = (x0 + x1) / 2
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    rb = r + dp
    zfn = lambda x: sp + math.sqrt(max(rb * rb - (x - cx) ** 2, 0.0))
    xs = [x0, 0.54, cx, 0.96, x1]
    vki_sto_strips(k, x0, x1, zfn, zb, xs)
    vki_sto_ring(k, cx, sp, r, (dp,) * 7, math.pi, 0.0, -0.27, 0.27, key="culv")
    for i in range(5):                                                  # the grate: bars to the intrados
        x = x0 + 0.09 + (x1 - x0 - 0.18) * i / 4
        zt_ = sp + math.sqrt(max(r * r - (x - cx) ** 2, 0.0)) + 0.03
        k.box((x, 0.0, (VKI_FOOT_Z + zt_) / 2), (0.028, 0.028, zt_ - VKI_FOOT_Z), IRON, bevel=0.0)
    k.box((cx, 0.0, 0.05), (x1 - x0 + 0.02, 0.022, 0.045), IRON, bevel=0.0)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Sewer", "A", holes=[(x0, VKI_FOOT_Z, x1, sp + rb + 0.05)], top_body_fn=lambda x: zb)
    vki_sew_patch(k)
    k.meta.update(vki_class="wall", vki_nav="block", vki_culvert=1,
                  vki_opening={"x0": x0, "x1": x1, "z0": VKI_FOOT_Z, "z1": round(sp + r, 4), "head": "round",
                               "culvert": 1},
                  vki_collider=[[L / 2, 0.0, 1.1, L, k.T, 2.2]],
                  vki_place_rule="on a grid line a channel crosses (channel cells on both sides)")


def vki_sew_culvert_full(k): vki_sew_culvert(k, "Full")
def vki_sew_culvert_cut(k): vki_sew_culvert(k, "Cut")


def vki_sew_outfall(k):
    """a Full wall with a pipe mouth: a dark disc (r 0.26) in a ring of dressed stones (6 cm proud) centred at z 0.80
    over a lip projecting 0.30 from face A; the water pours off the lip in a pale sheet into the channel below and
    foams on it (z -0.27, just over the water). Put it over a channel's end."""
    vki_dun_plain(k, 1.5, "Full", "A")
    cx, cz, r0, r1 = 0.75, 0.80, 0.26, 0.40
    n = 16
    vki_prism(k, [(cx + r0 * math.cos(2 * math.pi * i / n), cz + r0 * math.sin(2 * math.pi * i / n)) for i in range(n)],
              -0.285, -0.26, VOID, axis="y")
    for i in range(10):                                                 # the ring (V-joints)
        a0, a1 = 2 * math.pi * i / 10, 2 * math.pi * (i + 1) / 10
        pts = [(cx + rr * math.cos(a), cz + rr * math.sin(a)) for rr, a in ((r0, a0), (r1, a0), (r1, a1), (r0, a1))]
        vs, fs = vki_prism(k, pts, -0.31, -0.24, VKI_STONE_BLOCK_IN, axis="y", bevel=0.008)
        k.set_dark(vs, 0.06 * (i % 3))
    vki_sto_block(k, 0.52, 0.98, cz - r1 - 0.08, cz - r1 + 0.02, -0.55, -0.24, top=VKI_CAP, key="lip", dark=0.08)
    # the sheet: off the lip's edge (y -0.55, z 0.34) in a parabola to the water (y -0.74, z -0.27)
    z_lip = cz - r1 + 0.02
    front, back = [], []                                                # a closed sheet 1.2 cm thick
    for i in range(7):
        t = i / 6
        y, z = -0.55 - 0.19 * t - 0.02 * t * t, z_lip - (z_lip + 0.27) * t * t
        front.append([k.bm.verts.new((x, y, z)) for x in (0.60, 0.75, 0.90)])
        back.append([k.bm.verts.new((x, y + 0.012, z + 0.004)) for x in (0.60, 0.75, 0.90)])
    sheet = []
    for i in range(6):
        for j in range(2):
            sheet.append(k.bm.faces.new((front[i + 1][j], front[i + 1][j + 1], front[i][j + 1], front[i][j])))
            sheet.append(k.bm.faces.new((back[i][j], back[i][j + 1], back[i + 1][j + 1], back[i + 1][j])))
        for j in (0, 2):
            sheet.append(k.bm.faces.new((front[i][j], front[i + 1][j], back[i + 1][j], back[i][j])))
    for i in (0, 6):
        for j in range(2):
            sheet.append(k.bm.faces.new((front[i][j], front[i][j + 1], back[i][j + 1], back[i][j])))
    bmesh.ops.recalc_face_normals(k.bm, faces=sheet)
    for ff in sheet:
        ff.material_index = VKI_WAX
    vki_dpr_blob(k, (0.75, -0.78), (0.30, 0.22), -0.275, -0.268, VKI_WAX, ns=12, wob=0.25, seed=4)
    vki_sew_patch(k)
    k.slot_mats[VKI_WAX] = "M_VKI_Foam"
    k.meta.update(vki_cut_to=VKI_SEW_CUT_TO, vki_outfall=1,
                  vki_fx=[dict(fx="water_pour", pos=[0.75, -0.62, 0.10], scale=0.5)],
                  vki_place_rule="over a channel's end: the channel cell on face A's side")


def vki_sew_ladder(k):
    """a Full wall with an iron ladder up face A to a manhole: two rails 8 cm off the face on brackets, rungs every
    0.28 m, a dressed band behind them; a scene link (the assembler writes vki_link from R["passages"])"""
    vki_dun_plain(k, 1.5, "Full", "A")
    vki_sto_block(k, 0.46, 1.04, 0.0, 2.80, -0.28, -0.22, key="lband", dark=0.05)
    for x in (0.56, 0.94):
        k.box((x, -0.33, 1.44), (0.032, 0.032, 2.86), IRON, bevel=0.0)
        for z in (0.45, 1.45, 2.45):
            k.box((x, -0.305, z), (0.025, 0.05, 0.025), IRON, bevel=0.0)
    z = 0.30
    while z < 2.85:
        k.box((0.75, -0.33, z), (0.36, 0.024, 0.024), IRON, bevel=0.0)
        z += 0.28
    vki_sew_patch(k)
    k.meta.update(vki_cut_to=VKI_SEW_CUT_TO, vki_nav="block", vki_ladder=1,
                  vki_trigger=[0.75, -0.45, 1.0, 0.8, 0.4, 2.0], vki_spawn_local=[0.75, -1.20],
                  vki_prompt_local=[0.75, -0.40, 1.40], vki_prompt_text="Climb up")


def vki_sew_passage(k):
    """a dark brick tunnel mouth: the door arch (Stone's Door_150_Full) with darkness behind it -- a scene link"""
    vki_sto_door(k, "Full")
    k.box((0.75, 0.2075, 1.115), (0.86, 0.015, 2.17), VOID, bevel=0.0)
    vki_sew_patch(k)
    for key in ("vki_leaf", "vki_leaf_socket", "vki_leaf_open_deg"):
        k.meta.pop(key, None)
    k.meta.update(vki_cut_to=VKI_SEW_CUT_TO, vki_nav="door", vki_prompt_text="Go through",
                  vki_trigger=[0.75, -0.55, 1.0, 0.8, 0.7, 2.0], vki_spawn_local=[0.75, -1.60])


# ---------------------------------------------------------------- channel tiles
VKI_SEW_QUAD = ((-1, -1), (1, -1), (1, 1), (-1, 1))       # SW SE NE NW: the quarter of each corner (signs)


def vki_sew_channel(k, code, fam="Sewer", C=None, liquid="M_VKI_SewerWater", rim_top=VKI_CAP, volumes=True):
    """one dual-grid channel tile (see the header): per X quarter a bed (-0.75, dark) and water (-0.28, WATER slot);
    a rim along each inner edge where the quarter meets an O quarter (the channel meets floor), shortened where two
    meet, and a corner block where both neighbours are channel and the diagonal is floor (the inner corner).
    fam / C / liquid: another channel on the same tiles (the dwarven lava channels: vki_dwf_lava); rim_top: the rim
    tops' slot (None: the block's own, the lava's dark kerbs); volumes=False leaves the liquid to the caller.
    -> (the X quarters, the liquid rects)"""
    k.set_family(fam)
    C = C or VKI_SEW_CH
    h, rw = 0.75, C["rim"]
    X = [c == "X" for c in code]
    quads, rims, waters = [], [], []
    for i, (sx, sy) in enumerate(VKI_SEW_QUAD):
        if not X[i]:
            continue
        hn = VKI_SEW_QUAD.index((-sx, sy))                   # across x = 0
        vn = VKI_SEW_QUAD.index((sx, -sy))                   # across y = 0
        dn = VKI_SEW_QUAD.index((-sx, -sy))
        qx, qy = sorted((0.0, sx * h)), sorted((0.0, sy * h))
        quads.append((qx[0], qy[0], qx[1], qy[1]))
        if not X[hn]:
            rims.append((sorted((0.0, sx * rw)), qy))
        if not X[vn]:
            rims.append((sorted((sx * rw, sx * h)) if not X[hn] else qx, sorted((0.0, sy * rw))))
        if X[hn] and X[vn] and not X[dn]:
            rims.append((sorted((0.0, sx * rw)), sorted((0.0, sy * rw))))
        # the water inside the rims (u, v: distances from the node's lines), so no face shares a rim's plane
        if X[hn] and X[vn] and not X[dn]:
            uv = [(rw, h, 0.0, h), (0.0, rw, rw, h)]
        else:
            uv = [(0.0 if X[hn] else rw, h, 0.0 if X[vn] else rw, h)]
        for (u0, u1, v0, v1) in uv:
            wx, wy = sorted((sx * u0, sx * u1)), sorted((sy * v0, sy * v1))
            waters.append((wx[0], wy[0], wx[1], wy[1]))
    for (x0, y0, x1, y1) in (waters if volumes else []):                # closed water volumes
        vs = list(set(k.box(((x0 + x1) / 2, (y0 + y1) / 2, (C["bed"] + C["water"]) / 2),
                            (x1 - x0, y1 - y0, C["water"] - C["bed"]), VKI_STONE_BLOCK_IN, bevel=0.0)))
        k.bm.normal_update()
        for f in vki_faces_of(vs):
            if f.normal.z > 0.7:
                f.material_index = WATER
        k.set_dark(vs, 0.65)
    for (xa, ya) in rims:
        vki_sto_block(k, xa[0], xa[1], C["bed"], C["kerb"], ya[0], ya[1], top=rim_top, bev=0.012,
                      key="rim%d%d" % (int(xa[0] * 100), int(ya[0] * 100)))
    for v in k.bm.verts:                                                 # slime on the rims toward the water
        if v.co.z < -0.05:
            k.set_dark([v], 0.25 + 0.35 * vki_smoothstep(-0.05, C["water"], v.co.z))
    for v in k.bm.verts:                                                 # the water's surface keeps its colour
        if abs(v.co.z - C["water"]) < 1e-4:
            v[k.dark] = 0.0
    k.slot_mats[WATER] = liquid
    k.meta.update(vki_class="ground", vki_corners=code, vki_nav="block", vki_rot_lock="none", vki_water=1,
                  vki_uv_lock="local", vki_channel=1,
                  vki_covers_floor=[list(q) for q in quads],
                  vki_collider=[[(x0 + x1) / 2, (y0 + y1) / 2, 0.5, x1 - x0, y1 - y0, 1.0] for (x0, y0, x1, y1) in quads],
                  vki_place_rule="dual grid: origin on a node, corners SW SE NE NW = the cells around it (X channel, "
                                 "O not); rotation 0/90/180/270 (vki_cav_canon); carries no floor")
    return quads, waters


def vki_sew_channel_codes():
    """the five rotation classes of the X / O corner codes but OOOO"""
    out = set()
    for n in range(1, 16):
        out.add(vki_cav_canon("".join("X" if n >> i & 1 else "O" for i in range(4)))[0])
    return sorted(out)


# ---------------------------------------------------------------- props
def vki_sew_bridge(k):
    """a stone slab footbridge over a one-cell channel: 0.90 x 2.20 along local y, top 0.10, ends resting on the
    walkways, a worn kerb along each side; vki_bridge deck (the walk BFS crosses the channel there), no colliders"""
    vki_sto_block(k, -0.45, 0.45, -0.08, 0.08, -1.10, 1.10, top=VKI_CAP, bev=0.02, key="bslab", dark=0.05)
    for x in (-0.40, 0.40):
        vki_sto_block(k, x - 0.05, x + 0.05, 0.08, 0.14, -1.05, 1.05, top=VKI_CAP, bev=0.012, key="bk%d" % int(x * 10))
    for v in k.bm.verts:
        if v.co.z < 0.0:
            k.set_dark([v], 0.3)
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_SewerBlock"
    k.slot_mats[VKI_CAP] = "M_VKI_SewerCap"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="walk",
                  vki_collider=[[0.0, 0.0, -5.0, 0.01, 0.01, 0.01]], vki_bridge=[[-0.45, -1.1, 0.45, 1.1]],
                  vki_place_rule="on a channel cell's centre, spanning it: rotation 0 (a west-east channel) or 90")


def vki_sew_sluice(k):
    """a sluice gate across a one-cell channel (along local x): oak posts on the rims (x +-0.64), a head beam at 1.60,
    a plank gate half lowered into the water in the posts' grooves, an iron screw rod and a handwheel on the beam"""
    for x in (-0.64, 0.64):
        vki_adv_box(k, x - 0.07, x + 0.07, -0.08, 0.08, -0.30, 1.72, WOOD, bev=0.01)
    vki_adv_box(k, -0.74, 0.74, -0.09, 0.09, 1.60, 1.76, WOOD, bev=0.01)
    for i in range(5):
        vki_adv_box(k, -0.57, 0.57, -0.035, 0.035, -0.30 + 0.17 * i, -0.30 + 0.17 * i + 0.165, PLANKS,
                    dark=0.05 * (i % 2))
    vki_adv_box(k, -0.585, 0.585, -0.045, 0.045, 0.53, 0.57, IRON)
    vki_dpr_rod(k, (0.0, 0.0, 0.55), (0.0, 0.0, 1.98), 0.035, IRON)
    n, rr, zw = 10, 0.22, 1.92
    pts = [(rr * math.cos(2 * math.pi * i / n), rr * math.sin(2 * math.pi * i / n), zw) for i in range(n)]
    for i in range(n):                                                  # alternating widths: no coplanar joints
        vki_dpr_rod(k, pts[i], pts[(i + 1) % n], 0.030 if i % 2 else 0.034, IRON)
    for i in range(0, n, 2):
        vki_dpr_rod(k, (0.0, 0.0, zw + 0.004), pts[i], 0.018, IRON)
    for v in k.bm.verts:
        if v.co.z < 0.1:
            k.set_dark([v], 0.35)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.9, 0.0]], vki_nav="block",
                  vki_collider=[[-0.64, 0.0, 0.8, 0.14, 0.16, 1.6], [0.64, 0.0, 0.8, 0.14, 0.16, 1.6]],
                  vki_mechanism={"kind": "sluice", "states": ["lowered", "raised"], "state": "lowered",
                                 "travel_z": 0.8},
                  vki_place_rule="on a channel cell's centre, across it: rotation 0 (a south-north channel) or 90")


def vki_sew_sludge(k):
    """a slick of sewer sludge: a larger and a smaller dark olive glossy blob (M_VKI_Sludge on the WATER slot)"""
    vki_dpr_blob(k, (0.0, 0.0), (0.50, 0.36), 0.0006, 0.005, WATER, ns=16, wob=0.26, seed=8)
    vki_dpr_blob(k, (0.42, 0.34), (0.16, 0.12), 0.0011, 0.0045, WATER, ns=10, wob=0.2, seed=9)
    k.slot_mats[WATER] = "M_VKI_Sludge"
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


# ---------------------------------------------------------------- specs
VKI_SEW_SPECS = [
    ("SM_VKI_Wall_Sewer_Plain_150A_Full", vki_sew_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Sewer_Plain_150A_Cut", vki_sew_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Sewer_Plain_150B_Full", vki_sew_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Sewer_Plain_300_Full", vki_sew_plain_300_full, "wall"),
    ("SM_VKI_Wall_Sewer_Plain_300_Cut", vki_sew_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Sewer_Rake_150_L", vki_sew_rake_l, "wall"),
    ("SM_VKI_Wall_Sewer_Rake_150_R", vki_sew_rake_r, "wall"),
    ("SM_VKI_Wall_Sewer_Door_150_Full", vki_sew_door_full, "wall"),
    ("SM_VKI_Wall_Sewer_Door_150_Cut", vki_sew_door_cut, "wall"),
    ("SM_VKI_Wall_Sewer_Culvert_150_Full", vki_sew_culvert_full, "wall"),
    ("SM_VKI_Wall_Sewer_Culvert_150_Cut", vki_sew_culvert_cut, "wall"),
    ("SM_VKI_Wall_Sewer_Outfall_150_Full", vki_sew_outfall, "wall"),
    ("SM_VKI_Wall_Sewer_Ladder_150_Full", vki_sew_ladder, "wall"),
    ("SM_VKI_Wall_Sewer_Passage_150_Full", vki_sew_passage, "wall"),
    ("SM_VKI_Post_Sewer_Corner_Full", vki_sew_post_corner_full, "wall"),
    ("SM_VKI_Post_Sewer_Corner_Cut", vki_sew_post_corner_cut, "wall"),
    ("SM_VKI_Post_Sewer_Mid_Full", vki_sew_post_mid_full, "wall"),
    ("SM_VKI_Post_Sewer_Mid_Cut", vki_sew_post_mid_cut, "wall"),
] + [("SM_VKI_Wall_Sewer_Breach_%d_%s" % (int(L_ * 100), h_), (lambda k, L_=L_, h_=h_: vki_brk_breach(k, L_, h_, "Sewer")),
      "wall") for L_ in (1.5, 3.0) for h_ in ("Full", "Cut")] + \
    [("SM_VKI_Ground_Sewer_%s" % c_, (lambda k, c_=c_: vki_sew_channel(k, c_)), "none") for c_ in vki_sew_channel_codes()] + [
    ("SM_VKI_Prop_Bridge_Sewer", vki_sew_bridge, "none"),
    ("SM_VKI_Prop_Sluice", vki_sew_sluice, "prop"),
    ("SM_VKI_Overlay_Sludge", vki_sew_sludge, "none"),
]
VKI_SEW_NAMES = [n for n, _, _ in VKI_SEW_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_SEW_SPECS])
