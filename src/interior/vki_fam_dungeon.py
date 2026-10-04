# ===================== VKI FAM DUNGEON: Dungeon + Bars wall families, iron leaves, stone stairs =====================
# Dungeon kit (docs/DUNGEON_KIT.md). Package "dungeon". Loaded by vki_ns() after vki_fam_stone / vki_links, whose
# builders and helpers it uses (vki_sto_*, vki_prism, vki_cut, vki_faces_of, vki_top_faces, vki_hash_off, vki_lnk_*).
# Every top-level name starts with vki_/VKI_ (T18).
#
# Dungeon (class O, T 0.50, H 3.0): the Stone family's masonry construction (rubble-cored body, 0.75 m coping units,
#   dressed jambs / voussoirs / quoins) in the dungeon materials -- body M_VKI_DungeonIn (big coursed dark blocks),
#   dressed stone M_VKI_DungeonBlock, coping tops M_VKI_DungeonCap (a step paler, so the cutaway outline reads) -- plus
#   a damp band (extra darkening toward the floor, uniform along the wall so pieces join seamlessly) and its own pieces:
#     Plain_150B_Full   pop-out blocks keyed to the painted blocks of T_VKI_DungeonIn (vki_gen_blocks' draws replayed)
#     Window_150_Full   the dungeon "window": a high barred light grate (sill 2.05, flat lintel 2.62) with a daylight
#                       card at the back and a cold SPOT falling through the bars (their shadows stripe the pool)
#     Niche_150_Full/_Cut  ossuary niches (catacomb): recesses 0.30 deep with skulls and long bones; Cut keeps the
#                       lower niche (Full = Cut below 0.65)
# Bars (class P, T 0.30, H 3.0, Full only -- bars never hide the room, so they are never cut; vki_cut_to = itself):
#   iron cell fronts on a dressed curb (z -0.30..0.14) under a dressed lintel (2.80..3.00), square bars at a 0.15 m
#   pitch (x 0.075 + 0.15 i, so runs chain), flat iron bands at 1.00 and 2.10 through the bars; Door_150 is a gate
#   opening x 0.33-1.17 under the 2.10 transom, closed by Leaf_BarsGate_Full. Posts: dressed stone piers.
# Leaves: Leaf_Iron_Cut (exit leaf of Dungeon Door_150_Cut: dark oak, iron straps and studs), Leaf_BarsGate_Full.
# Stairs (scene links, same footprint / metadata contract as vki_links' timber stairs): Stair_Up_150x450_Stone (solid
#   stone flight of wedge steps on a masonry spandrel, iron balustrade, cut at the ceiling plane) and
#   Stair_Down_150x450_Stone (stone steps into a lined shaft, iron railings on low stone upstands); their left-hand
#   twins ..._StoneL (mirrored: the wall on local x = 1.5, the rail side x = 0) for a flight with the wall on its right.
# Build: g["vki_ws_build"]("dungeon", VKI_DUN_NAMES); test: g["vki_test_pieces"](VKI_DUN_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_DUN_CUT_TO = "SM_VKI_Wall_Dungeon_Plain_150A_Cut"
VKI_DUN_DAMP = (0.20, 0.90)          # extra darkening at the floor, gone by 0.90 m (under the Cut coping)
VKI_DUN_BONE = "M_VKI_Bone"           # bones and skulls: the WAX slot, overridden per master (vki_dun_bone_mats)
# T_VKI_DungeonIn's layout parameters (keep in sync with VKI_TEX_JOBS["T_VKI_DungeonIn"] in vki_tex_dungeon)
VKI_DUN_TEX = dict(seed=71, T=1.5, blocks=(3, 2, 3, 2), wjit=0.28, min_sep=0.14, rows=(0.40, 0.34, 0.42, 0.36))
VKI_DUN_POP_DEPTH = (0.035, 0.050)   # pop-out fronts 0.035-0.05 proud (Stone 150B: 0.04-0.05; T1 allows 0.06)


# ---------------------------------------------------------------- damp band, family patch
def vki_dun_damp(k, a=None, z1=None):
    """darken every vertex below z1 toward the floor (vki_dark, max-combined): a damp tide band. Uniform along x, so
    every piece of the family (and its posts) matches at the joints."""
    a = VKI_DUN_DAMP[0] if a is None else a
    z1 = VKI_DUN_DAMP[1] if z1 is None else z1
    for v in k.bm.verts:
        z = v.co.z
        if z < z1:
            k.set_dark([v], a * vki_smoothstep(z1, 0.0, z))


def vki_dun_patch(k, leaf=None):
    """Stone-built geometry -> Dungeon: family (materials, metadata), damp band, the Dungeon cut target"""
    k.set_family("Dungeon")
    vki_dun_damp(k)
    if k.meta.get("vki_cut_to") == VKI_STO_CUT_TO:
        k.meta["vki_cut_to"] = VKI_DUN_CUT_TO
    if leaf:
        k.meta["vki_leaf"] = leaf


def vki_dun_bone_mats(k):
    k.slot_mats[VKI_WAX] = VKI_DUN_BONE


# ---------------------------------------------------------------- painted block layout -> pop-outs (Plain_150B)
def vki_dun_block_layout(p=None):
    """the painted blocks of T_VKI_DungeonIn: vki_gen_blocks' own random draws replayed (widths, course offsets), in
    UV: [dict(u0, w, v0, v1, row, col)] (u0 + w may pass 1: the block wraps). write_map stores rows flipped, so UV v =
    1 - the generator's y."""
    import numpy as np
    p = p or VKI_DUN_TEX
    rng = np.random.default_rng(p["seed"])
    blocks = p["blocks"]; nrow = len(blocks); T = p["T"]
    wr = lambda d: d - np.round(d)
    for _try in range(2000):
        Wd = []
        for r in range(nrow):
            w = (1 + rng.uniform(-p["wjit"], p["wjit"], blocks[r])) / blocks[r]; Wd.append(w / w.sum())
        off = rng.uniform(0, 1, nrow)
        E = [(np.concatenate([[0.0], np.cumsum(Wd[r])[:-1]]) - off[r]) % 1 for r in range(nrow)]
        sep = min(float(np.abs(wr(E[r][:, None] - E[(r + 1) % nrow][None, :])).min()) for r in range(nrow)) * T
        if sep >= p["min_sep"]:
            break
    rh = np.array(p["rows"], np.float64); rh = rh / rh.sum()
    rb = np.concatenate([[0.0], np.cumsum(rh)]); rb[-1] = 1.0
    out = []
    for r in range(nrow):
        e = np.concatenate([[0.0], np.cumsum(Wd[r])])
        for c in range(blocks[r]):
            out.append(dict(u0=float((e[c] - off[r]) % 1.0), w=float(Wd[r][c]), v0=float(1.0 - rb[r + 1]),
                            v1=float(1.0 - rb[r]), row=r, col=c))
    return out


def vki_dun_pop_sites(face="A", p=None):
    """painted blocks that may pop out in a 1.5 m span: world-locked t 1.5 (face A: u = -x / 1.5, face B: u = x / 1.5,
    v = z / 1.5); the whole block keeps NODE_FLAT from both nodes and its 0.9 w x 0.9 h pop-out lies in VKI_STO_POP_Z"""
    T = 1.5
    out = []
    for b in vki_dun_block_layout(p):
        uc = b["u0"] + b["w"] / 2; vc = (b["v0"] + b["v1"]) / 2
        w, h = b["w"] * T, (b["v1"] - b["v0"]) * T
        x = ((-T * uc) if face == "A" else (T * uc)) % T
        if not (VKI_NODE_FLAT + w / 2 - 1e-6 <= x <= T - VKI_NODE_FLAT - w / 2 + 1e-6):
            continue
        for kk in range(3):
            z = T * vc + T * kk
            w9, h9 = 0.9 * w, 0.9 * h
            if z - h9 / 2 >= VKI_STO_POP_Z[0] - 1e-6 and z + h9 / 2 <= VKI_STO_POP_Z[1] + 1e-6:
                out.append(dict(x=x, z=z, w=w9, h=h9, lab=b["row"] * 10 + b["col"] + 100 * kk))
    return out


def vki_dun_popouts(k, p=None, key="Dungeon"):
    """pop-out blocks of the texture whose vki_gen_blocks parameters are p (default T_VKI_DungeonIn's)"""
    n = 0
    for face in ("A", "B"):
        for s in vki_dun_pop_sites(face, p):
            d = VKI_DUN_POP_DEPTH[0] + (VKI_DUN_POP_DEPTH[1] - VKI_DUN_POP_DEPTH[0]) * \
                vki_hash01(s["lab"], 11, vki_seed(key + "|pop|" + face))
            vki_sto_popout(k, s["x"], s["z"], s["w"], s["h"], face, d)
            n += 1
    return n


# ---------------------------------------------------------------- Dungeon: Plain, Rake, Door, DoorWide, Posts
def vki_dun_plain(k, L, height, variant="A", popouts=False):
    full = height == "Full"
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    vki_sto_body(k, 0.0, L, VKI_FOOT_Z, zb)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    pops = vki_dun_popouts(k) if popouts else 0
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dungeon", variant, holes=[], top_body_fn=lambda x: zb)
    vki_dun_damp(k)
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_DUN_CUT_TO, vki_popouts=pops,
                      vki_popout_note="pop-out blocks up to 0.05 proud of both faces between z 1.2 and 2.8: keep "
                                      "wall_hung props and wall-backed props taller than 1.2 m off this piece")


def vki_dun_plain_150a_full(k): vki_dun_plain(k, 1.5, "Full", "A")
def vki_dun_plain_150a_cut(k): vki_dun_plain(k, 1.5, "Cut", "A")
def vki_dun_plain_150b_full(k): vki_dun_plain(k, 1.5, "Full", "B", popouts=True)
def vki_dun_plain_300_full(k): vki_dun_plain(k, 3.0, "Full", "A")
def vki_dun_plain_300_cut(k): vki_dun_plain(k, 3.0, "Cut", "A")
def vki_dun_rake_l(k): vki_sto_rake(k, "L"); vki_dun_patch(k)
def vki_dun_rake_r(k): vki_sto_rake(k, "R"); vki_dun_patch(k)
def vki_dun_door_full(k): vki_sto_door(k, "Full"); vki_dun_patch(k, "SM_VKI_Leaf_Plank_Full")
def vki_dun_door_cut(k): vki_sto_door(k, "Cut"); vki_dun_patch(k, "SM_VKI_Leaf_Iron_Cut")
def vki_dun_door_wide_full(k): vki_sto_door_wide(k, "Full"); vki_dun_patch(k)
def vki_dun_door_wide_cut(k): vki_sto_door_wide(k, "Cut"); vki_dun_patch(k)


def vki_dun_post(k, kind, height):
    """the Stone quoin pier / pilaster (vki_sto_post) in the Dungeon materials, with the damp band"""
    vki_sto_post(k, kind, height)
    vki_dun_patch(k)
    r = dict(k.meta["vki_post_rule"])
    r["toggle_to"] = r["toggle_to"].replace("_Stone_", "_Dungeon_")
    r["rule"] = r["rule"].replace("Stone wins over every other family", "Dungeon wins over every other family")
    k.meta["vki_post_rule"] = r


def vki_dun_post_corner_full(k): vki_dun_post(k, "Corner", "Full")
def vki_dun_post_corner_cut(k): vki_dun_post(k, "Corner", "Cut")
def vki_dun_post_mid_full(k): vki_dun_post(k, "Mid", "Full")
def vki_dun_post_mid_cut(k): vki_dun_post(k, "Mid", "Cut")


# ---------------------------------------------------------------- Window_150_Full: the light grate
VKI_DUN_GRATE = dict(x=(0.45, 1.05), sill=(1.95, 2.05), head=(2.62, 2.78), card_y=(0.21, 0.23), bar_y=-0.10,
                     bars=(0.57, 0.69, 0.81, 0.93), bar_hw=0.016, rail_z=2.33, face=-0.29)
# the spot sits in the opening, 2 cm in front of the daylight card, and shines down into the room: the sill, lintel and
# reveals frame the beam and the bars stripe the pool. (Outside the wall its cone lit the coping top as a bright disc,
# and through the 0.57 m x 0.50 m shaft only a sliver of it reached the floor.)
VKI_DUN_GRATE_SPOT = dict(type="SPOT", role="window", pos=[0.75, 0.19, 2.34], aim=[0.75, -2.0, 0.0], cone=60.0,
                          blend=0.30, radius=0.04, w_day=1200.0, w_night=120.0, color_day=[.78, .86, 1.0],
                          color_night=[.62, .70, 1.0], shadows=1)


def vki_dun_window(k):
    """high barred light grate (a shaft from the surface): opening x 0.45-1.05, z 2.05-2.62 through the wall; dressed
    sill (1.95-2.05, CAP top) and flat lintel (2.62-2.78) 4 cm proud of face A; four square iron bars and a flat
    rail set 0.10 in from the room face; a daylight card (WINDOW -> M_VKI_Daylight) closes the shaft 0.21 behind the
    wall centre; a cold SPOT falls through the bars (shadows on: the bars stripe the pool). No Cut twin (the Cut
    wall below a grate is plain): vki_cut_to Plain_150A_Cut."""
    L = 1.5
    G = VKI_DUN_GRATE
    x0, x1 = G["x"]
    zb, zt = VKI_STO_FULL
    s0, s1 = G["sill"]; h0, h1 = G["head"]
    fy = G["face"]
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)                                       # piers
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, s0)                                        # under the sill
    vki_sto_body(k, x0, x1, h1, zb)                                                # over the lintel
    vki_sto_block(k, x0 - 0.05, x1 + 0.05, s0, s1, fy, k.T / 2 - 0.01, top=VKI_CAP, key="gsill")
    vki_sto_block(k, x0 - 0.07, x1 + 0.07, h0, h1, fy, k.T / 2 - 0.01, key="glint")   # lintel: the opening's soffit
    # iron: bars 5 cm into sill and lintel, a flat rail through them; the card at the back
    by, hw = G["bar_y"], G["bar_hw"]
    for bx in G["bars"]:
        k.box((bx, by, (s1 - 0.05 + h0 + 0.05) / 2), (2 * hw, 2 * hw, h0 - s1 + 0.10), IRON, bevel=0.0)
    k.box(((x0 + x1) / 2, by, G["rail_z"]), (x1 - x0 + 0.02, 0.05, 0.045), IRON, bevel=0.0)
    c0, c1 = G["card_y"]
    k.box(((x0 + x1) / 2, (c0 + c1) / 2, (s1 + h0) / 2), (x1 - x0 + 0.02, c1 - c0, h0 - s1 + 0.02), WINDOW, bevel=0.0)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dungeon", "A", holes=[(x0 - 0.07, s0, x1 + 0.07, h1)], top_body_fn=lambda x: zb)
    vki_dun_damp(k)
    k.slot_mats[WINDOW] = "Daylight"
    k.meta.update(vki_class="wall", vki_cut_to=VKI_DUN_CUT_TO,
                  vki_opening={"x0": x0, "x1": x1, "z0": s1, "z1": h0, "head": "flat", "grate": 1},
                  vki_lights=[dict(VKI_DUN_GRATE_SPOT)])


# ---------------------------------------------------------------- skulls and bones (niches, props)
def vki_dun_xform(k, verts, c, yaw=0.0, pitch=0.0, roll=0.0):
    """rotate verts (built about the origin) by roll (X), pitch (Y), yaw (Z, degrees) and move them to c"""
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ \
        Matrix.Rotation(math.radians(pitch), 4, "Y") @ Matrix.Rotation(math.radians(roll), 4, "X")
    bmesh.ops.transform(k.bm, matrix=M, verts=list(verts))


def vki_dun_skull(k, c, s=1.0, yaw=0.0, pitch=0.0, roll=0.0, dark=0.0, segs=(6, 4), nose=False):
    """a low skull facing local -Y: cranium (UV sphere, smooth), face / jaw block, two VOID eye sockets (and a VOID
    nose notch when nose=True); 72 tris at segs (6, 4). c = the cranium centre. Returns its verts."""
    before = set(k.bm.verts)
    r = bmesh.ops.create_uvsphere(k.bm, u_segments=segs[0], v_segments=segs[1], radius=0.080 * s)
    vs = list(r["verts"])
    bmesh.ops.scale(k.bm, vec=(0.90, 1.10, 0.92), verts=vs)
    bmesh.ops.translate(k.bm, vec=(0.0, 0.0, 0.012 * s), verts=vs)
    for f in {f for v in vs for f in v.link_faces}:
        f.material_index = VKI_WAX; f.smooth = True
    k.box((0.0, -0.050 * s, -0.052 * s), (0.092 * s, 0.078 * s, 0.056 * s), VKI_WAX, bevel=0.0)          # face / jaw
    for sx in (-1.0, 1.0):
        k.box((sx * 0.030 * s, -0.081 * s, -0.004 * s), (0.030 * s, 0.022 * s, 0.028 * s), VOID, bevel=0.0)
    if nose:
        k.box((0.0, -0.086 * s, -0.036 * s), (0.016 * s, 0.018 * s, 0.020 * s), VOID, bevel=0.0)
    new = [v for v in k.bm.verts if v not in before]
    vki_dun_xform(k, new, c, yaw, pitch, roll)
    if dark:
        k.set_dark(new, dark)
    return new


def vki_dun_bone(k, a, b, r=0.016, dark=0.0):
    """a long bone from a to b: a square shaft and two knuckle blocks (36 tris, WAX slot)"""
    a = Vector(a); b = Vector(b); d = b - a
    L = d.length
    yaw = math.atan2(d.y, d.x)
    pitch = -math.atan2(d.z, math.hypot(d.x, d.y))
    rot = (0.0, pitch, yaw)
    before = set(k.bm.verts)
    k.box(tuple((a + b) / 2), (L - 3.0 * r, 2 * r, 2 * r), VKI_WAX, rot=rot, bevel=0.0)
    u = d.normalized()
    for e in (a + u * 1.6 * r, b - u * 1.6 * r):
        k.box(tuple(e), (3.2 * r, 3.0 * r, 2.6 * r), VKI_WAX, rot=rot, bevel=0.0)
    new = [v for v in k.bm.verts if v not in before]
    if dark:
        k.set_dark(new, dark)
    return new


def vki_dun_ossuary(k, x0, x1, zf, y0, y1, seed):
    """contents of one ossuary niche: long bones stacked along x at the back, a row of skulls on them in front"""
    rng = random.Random(seed)
    L = x1 - x0
    for i, (dy, dz) in enumerate(((0.10, 0.018), (0.06, 0.018), (0.08, 0.05))):
        ya = y1 - dy
        xa = x0 + 0.03 + rng.uniform(0.0, 0.05); xb = x1 - 0.03 - rng.uniform(0.0, 0.05)
        vki_dun_bone(k, (xa, ya, zf + dz), (xb, ya + rng.uniform(-0.02, 0.02), zf + dz + rng.uniform(-0.006, 0.006)),
                     r=0.016, dark=0.25 + 0.05 * i)
    n = 3
    for i in range(n):
        x = x0 + L * (i + 0.5) / n + rng.uniform(-0.03, 0.03)
        vki_dun_skull(k, (x, y0 + 0.11, zf + 0.085), s=0.95 + 0.1 * rng.random(), yaw=rng.uniform(-18, 18),
                      pitch=rng.uniform(-6, 6))


# ---------------------------------------------------------------- Niche_150 (ossuary)
VKI_DUN_NICHE = dict(x=(0.36, 1.14), rows=((0.30, 0.74), (1.40, 1.86)), back_y=0.05, lint=0.10, face=-0.29)


def vki_dun_niche(k, height):
    """ossuary niches: piers x 0-0.36 / 1.14-1.5; each niche 0.78 x 0.44, 0.30 deep (back at y +0.05, body behind),
    a dressed sill (its top the niche floor) and lintel 4 cm proud of face A; long bones and skulls inside.
    Full: niches at 0.30-0.74 and 1.40-1.86; Cut: the lower one (identical below 0.65, T2)."""
    L = 1.5
    full = height == "Full"
    N = VKI_DUN_NICHE
    x0, x1 = N["x"]
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    rows = N["rows"] if full else N["rows"][:1]
    by = N["back_y"]; fy = N["face"]; T2 = k.T / 2
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    zc = VKI_FOOT_Z
    holes = []
    # the bodies between the piers lie inside the wobble's hole margin (no wobble there), so they skip the 0.25 grid
    for (a, b) in rows:
        k.body_box(x0, x1, zc, a - 0.04, step=10.0)                             # solid under the sill
        k.body_box(x0, x1, a - 0.04, b + N["lint"], y0=by, step=10.0)           # the back of the niche
        vki_sto_block(k, x0 - 0.03, x1 + 0.03, a - 0.05, a, fy, by + 0.01, top=VKI_CAP, key="nsill%d" % int(a * 100))
        vki_sto_block(k, x0 - 0.05, x1 + 0.05, b, b + N["lint"], fy, by + 0.01, key="nlint%d" % int(a * 100))
        vki_dun_ossuary(k, x0 + 0.02, x1 - 0.02, a, fy + 0.04, by, seed=int(a * 100))
        holes.append((x0 - 0.05, a - 0.05, x1 + 0.05, b + N["lint"]))
        zc = b + N["lint"]
    k.body_box(x0, x1, zc, zb, step=10.0)
    vki_sto_coping(k, 0.0, L, zb, zt, L, fixed=not full)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dungeon", "A", holes=holes, top_body_fn=lambda x: zb)
    vki_dun_damp(k)
    vki_dun_bone_mats(k)
    k.meta.update(vki_class="wall",
                  vki_opening=[{"x0": x0, "x1": x1, "z0": a, "z1": b, "niche": 1, "depth": round(by + T2, 3)}
                               for (a, b) in rows],
                  vki_niche_note="sills and lintels 4 cm proud of face A (|y| 0.29): no wall-backed props here")


def vki_dun_niche_full(k): vki_dun_niche(k, "Full")
def vki_dun_niche_cut(k): vki_dun_niche(k, "Cut")


# ---------------------------------------------------------------- Bars family (class P)
VKI_BAR = dict(curb=0.14, lintel=(2.80, 3.00), hw=0.15, pitch=0.15, bar_hw=0.0175, bands=(1.00, 2.10), band_h=0.05,
               band_hy=0.028, gate=(0.33, 1.17), jamb=0.04, transom=2.10)
VKI_BAR_SELF = "SM_VKI_Wall_Bars_Plain_150A_Full"


def vki_bar_units(k, x0, x1, z0, z1, top, key, fixed_ends=True):
    """dressed stone units (curb / lintel) on the piece's 0.75 m grid, |y| <= 0.15, bevelled (V-joints)"""
    hw = VKI_BAR["hw"]
    cuts = [x0] + [0.75 * i for i in range(1, 5) if x0 + 1e-6 < 0.75 * i < x1 - 1e-6] + [x1]
    for a, b in zip(cuts[:-1], cuts[1:]):
        vki_sto_block(k, a, b, z0, z1, -hw, hw, top=VKI_CAP if top else None, key=key + "%d" % int(a * 100))


def vki_bar_bar(k, x, z0, z1, y=0.0):
    h = VKI_BAR["bar_hw"]
    k.box((x, y, (z0 + z1) / 2), (2 * h, 2 * h, z1 - z0), IRON, bevel=0.0)


def vki_bar_band(k, x0, x1, z):
    B = VKI_BAR
    k.box(((x0 + x1) / 2, 0.0, z + B["band_h"] / 2), (x1 - x0, 2 * B["band_hy"], B["band_h"]), IRON, bevel=0.0)


def vki_bar_plain(k, L):
    B = VKI_BAR
    k.set_family("Bars")
    vki_bar_units(k, 0.0, L, VKI_FOOT_Z, B["curb"], True, "curb")
    vki_bar_units(k, 0.0, L, B["lintel"][0], B["lintel"][1], True, "lint")
    n = int(round(L / B["pitch"]))
    for i in range(n):
        vki_bar_bar(k, B["pitch"] * (i + 0.5), B["curb"] - 0.005, B["lintel"][0] + 0.005)
    for z in B["bands"]:
        vki_bar_band(k, 0.0, L, z)
    vki_dun_damp(k)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_BAR_SELF, vki_no_cut=1, vki_see_through=1,
                  vki_nav="block", vki_collider=[[L / 2, 0.0, 1.5, L, 0.30, 3.0]],
                  vki_bars_note="bars never hide the room: Full only, never cut (vki_cut_to = itself)")


def vki_bar_plain_150(k): vki_bar_plain(k, 1.5)
def vki_bar_plain_300(k): vki_bar_plain(k, 3.0)


def vki_bar_door(k):
    """barred gate opening x 0.33-1.17 (0.84 clear) under a flat-iron transom at 2.10; iron jambs, bars left / right
    and over the transom; DRESS threshold 0-0.03 over a dressed footing; Leaf_BarsGate_Full closes it"""
    B = VKI_BAR
    L = 1.5
    k.set_family("Bars")
    g0, g1 = B["gate"]; j = B["jamb"]; tz = B["transom"]
    vki_bar_units(k, 0.0, g0, VKI_FOOT_Z, B["curb"], True, "curb")
    vki_bar_units(k, g1, L, VKI_FOOT_Z, B["curb"], True, "curb")
    vki_sto_block(k, g0, g1, VKI_FOOT_Z, -0.10, -B["hw"], B["hw"], key="gfoot")
    vki_sto_block(k, g0, g1, 0.0, 0.03, -0.14, 0.14, mi=DRESS, bev=0.01, dark=0.06)            # threshold
    vki_bar_units(k, 0.0, L, B["lintel"][0], B["lintel"][1], True, "lint")
    for x in (0.075, 0.225, 1.275, 1.425):
        vki_bar_bar(k, x, B["curb"] - 0.005, B["lintel"][0] + 0.005)
    for x in (g0 + (g1 - g0) * (i + 0.5) / 6 for i in range(6)):                                  # over the transom
        vki_bar_bar(k, x, tz + B["band_h"] - 0.005, B["lintel"][0] + 0.005)
    for xa, xb in ((g0 - j - 0.005, g0 - 0.005), (g1 + 0.005, g1 + j + 0.005)):                   # iron jambs
        k.box(((xa + xb) / 2, 0.0, (0.025 + B["lintel"][0] + 0.005) / 2), (xb - xa, 0.06, B["lintel"][0] - 0.02),
              IRON, bevel=0.0)
    vki_bar_band(k, 0.0, g0 - j + 0.005, B["bands"][0])
    vki_bar_band(k, g1 + j - 0.005, L, B["bands"][0])
    vki_bar_band(k, 0.0, L, tz)
    vki_dun_damp(k)
    T2 = 0.15
    k.meta.update(vki_class="wall", vki_cut_to="SM_VKI_Wall_Bars_Door_150_Full", vki_no_cut=1, vki_see_through=1,
                  vki_nav="door", vki_nav_open=[g0, g1],
                  vki_opening={"x0": g0, "x1": g1, "z0": 0.0, "z1": tz, "head": "transom", "gate": 1},
                  vki_leaf="SM_VKI_Leaf_BarsGate_Full", vki_leaf_socket=[g0, -0.022, 0.0], vki_leaf_open_deg=90,
                  vki_collider=[[g0 / 2, 0.0, 1.5, g0, 2 * T2, 3.0], [(g1 + L) / 2, 0.0, 1.5, L - g1, 2 * T2, 3.0],
                                [0.75, 0.0, 2.55, L, 2 * T2, 0.9]])


VKI_BAR_POST_Z = (-0.30, 0.14, 0.62, 1.10, 1.58, 2.06, 2.54, 3.04)


def vki_bar_post(k, kind):
    """dressed stone pier (Corner +-0.21, Mid +-0.10 along x +-0.21 across), -0.30 .. 3.04, bevel 0.02, CAP top"""
    k.set_family("Bars")
    ax, ay = (VKI_POST_HW["P"], VKI_POST_HW["P"]) if kind == "Corner" else VKI_MID_HW["P"]
    zs = VKI_BAR_POST_Z
    n = len(zs) - 1
    for i in range(n):
        hx, hy = ax, ay
        if kind == "Corner" and i < n - 1:
            if i % 2 == 0:
                hy = ay - VKI_STO_QUOIN_INSET
            else:
                hx = ax - VKI_STO_QUOIN_INSET
        vki_sto_block(k, -hx, hx, zs[i], zs[i + 1], -hy, hy, bev=VKI_POST_BEVEL, top=VKI_CAP if i == n - 1 else None,
                      key="bpost%s%d" % (kind, i))
    vki_dun_damp(k)
    me = f"SM_VKI_Post_Bars_{kind}_Full"
    k.meta.update(vki_class="post",
                  vki_post_rule={"role": kind.lower(), "height": "Full", "toggle_to": me, "orient":
                                 "along local x" if kind == "Mid" else "any",
                                 "rule": "Bars-only nodes (any Dungeon / Stone wall at the node wins, §2.3); Full only"},
                  vki_collider=[[0.0, 0.0, 1.5, 2 * ax, 2 * ay, 3.0]])


def vki_bar_post_corner(k): vki_bar_post(k, "Corner")
def vki_bar_post_mid(k): vki_bar_post(k, "Mid")


# ---------------------------------------------------------------- leaves
def vki_dun_leaf_iron(k):
    """exit leaf of the Dungeon Door_150_Cut: the plank leaf (vki_leaf_plank) in dark oak with a row of iron studs
    along each room-side strap and a dark iron lock plate"""
    vki_leaf_plank(k, "Cut")
    y0 = VKI_LEAF_Y0
    for z in (0.24, 0.74):
        for x in (0.16, 0.30, 0.44, 0.58, 0.72):
            k.box((x, y0 - 0.017, z), (0.024, 0.012, 0.024), IRON, bevel=0.0)
    k.box((0.765, y0 - 0.005, 0.40), (0.07, 0.012, 0.14), IRON, bevel=0.003)
    k.box((0.765, y0 - 0.012, 0.38), (0.012, 0.004, 0.03), VOID, bevel=0.0)
    k.slot_mats[WOOD] = "Dark"
    k.meta["vki_leaf_fits"] = "SM_VKI_Wall_Dungeon_Door_150_Cut at its vki_leaf_socket, same rotation"


def vki_dun_leaf_gate(k):
    """barred gate for Bars Door_150_Full: flat-iron frame x 0.005-0.835, z 0.035-2.095, bars at 0.125 m, a lock box
    on the room side near the meeting stile. Hinge at the origin; the frame lies at local y 0.004-0.040, so at the
    door's socket (y -0.022) it is centred on the bars' plane. Opens toward -Y (rotation -deg), like every leaf."""
    x0, x1 = 0.005, 0.835
    z0, z1 = 0.035, 2.095
    ya, yb = 0.004, 0.040
    yc = (ya + yb) / 2
    s = 0.04
    for xa, xb in ((x0, x0 + s), (x1 - s, x1)):
        k.box(((xa + xb) / 2, yc, (z0 + z1) / 2), (xb - xa, yb - ya, z1 - z0), IRON, bevel=0.0)
    rails = ((z0 + 0.01, z0 + 0.06), (1.00, 1.05), (z1 - 0.06, z1 - 0.01))     # 1 cm off the stile ends (T5S)
    for za, zb_ in rails:
        k.box(((x0 + x1) / 2, yc, (za + zb_) / 2), (x1 - x0 - 2 * s + 0.01, yb - ya - 0.006, zb_ - za), IRON, bevel=0.0)
    for i in range(5):
        x = x0 + s + 0.125 * (i + 1)
        for za, zb_ in ((rails[0][1] - 0.005, rails[1][0] + 0.005), (rails[1][1] - 0.005, rails[2][0] + 0.005)):
            k.box((x, yc, (za + zb_) / 2), (0.03, 0.026, zb_ - za), IRON, bevel=0.0)
    k.box((0.72, ya - 0.018, 1.10), (0.12, 0.036, 0.16), IRON, bevel=0.004)                       # lock box
    k.box((0.72, ya - 0.037, 1.08), (0.012, 0.004, 0.035), VOID, bevel=0.0)
    k.meta.update(vki_class="leaf", hinge_axis="local Z", vki_leaf_state="closed", vki_leaf_open_deg=90,
                  vki_leaf_width=round(x1 - x0, 3), vki_leaf_height=round(z1 - z0, 3), vki_hinge=[0.0, 0.0, 0.0],
                  vki_leaf_clearance=0.005, vki_see_through=1,
                  vki_leaf_open_dir="rotation -deg about local Z (toward the room, -Y)",
                  vki_leaf_fits="SM_VKI_Wall_Bars_Door_150_Full at its vki_leaf_socket, same rotation")


# ---------------------------------------------------------------- stone stairs (scene links)
VKI_DUN_STAIR_D = 0.26         # step blocks reach this far below the pitch line (their sloped soffit)
VKI_DUN_RAIL_X = 1.215         # the up flight's iron balustrade stands on the steps' outer ends (they end at 1.27)


def vki_dun_rod(k, a, b, w, mi=IRON, d=None, roll=0.0):
    """a square bar from a to b (3-D), cross-section w x d (d vertical-ish), unbevelled"""
    a = Vector(a); b = Vector(b); dv = b - a
    yaw = math.atan2(dv.y, dv.x)
    pitch = -math.atan2(dv.z, math.hypot(dv.x, dv.y))
    return list(set(k.box(tuple((a + b) / 2), (dv.length, w, d or w), mi, rot=(roll, pitch, yaw), bevel=0.0)))


def vki_dun_stair_mats(k):
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_DungeonBlock"
    k.slot_mats[VKI_CAP] = "M_VKI_DungeonCap"


def vki_dun_step(k, poly, x0, x1, dark, key, top=True):
    """one dressed step block: convex (y, z) polygon extruded x0..x1, bevelled; CAP tread top"""
    vs, fs = vki_prism(k, poly, x0, x1, VKI_STONE_BLOCK_IN, axis="x", bevel=0.015, project=False)
    c = (0.5 * (x0 + x1), poly[0][0], poly[0][1])
    k.project(fs, VKI_STONE_BLOCK_IN, offset=vki_hash_off(c), tile=VKI_STO_TILE)
    if top:
        vki_sto_top(k, vs, VKI_CAP, c)
    k.set_dark(vs, dark + 0.08 * vki_hash01(int(round(c[1] * 50)), int(round(c[2] * 50)), vki_seed("Dungeon|" + key)))
    return vs


def vki_dun_step_poly(y0, y1, zt, s0, s1, fl):
    """(y, z) polygon of a step block: top zt over [y0, y1], soffit from (y0, s0) to (y1, s1), clipped at z >= fl
    (a convex quad or pentagon)"""
    if s0 >= fl and s1 >= fl:
        return [(y0, s0), (y1, s1), (y1, zt), (y0, zt)]
    if s0 < fl and s1 < fl:
        return [(y0, fl), (y1, fl), (y1, zt), (y0, zt)]
    ym = y0 + (fl - s0) * (y1 - y0) / (s1 - s0)
    if s0 < fl:
        return [(y0, fl), (ym, fl), (y1, s1), (y1, zt), (y0, zt)]
    return [(y0, s0), (ym, fl), (y1, fl), (y1, zt), (y0, zt)]


def vki_dun_stair_up(k):
    """solid stone flight: 14 wedge steps (tops 0.2 i, nosing lines (i - 1) g) whose soffits rest on a masonry
    spandrel, an iron balustrade on the open side (handrail 0.95 above the pitch line on newels and square balusters
    standing on the steps' ends, cut at the ceiling plane z 3.0: see-through, like the timber rail -- a stone parapet
    rose into a 3 m slab under the ceiling and hid the room beside the stair) and the lip slab; the top two steps
    darkened (under the ceiling). Same footprint, clearances and metadata as Stair_Up_150x450_RailR (vki_links)."""
    g_, r_ = VKI_LNK_GO, VKI_LNK_RISE
    P = vki_lnk_pitch_up
    kk = r_ / g_
    xa, xb = VKI_LNK_X
    d = VKI_DUN_STAIR_D
    fl = -0.006                                        # step and spandrel bottoms: 6 mm into the room floor
    sof = lambda y: P(y) - r_ - d                      # step soffit line (parallel to the pitch line)
    ntop = VKI_LNK_RISERS - 2
    for i in range(1, VKI_LNK_RISERS):
        y0, y1, zt = (i - 1) * g_, i * g_, r_ * i
        dk = VKI_LNK_DARK_TOP if i >= ntop else 0.0
        vki_dun_step(k, vki_dun_step_poly(y0, y1, zt, sof(y0), sof(y1), fl), xa, xb, dk, "st%d" % i)
    # spandrel: the masonry under the soffit line, from where it meets the floor to the lip, and the block under the lip
    y_a = (fl + d) / kk                                # sof(y_a) = fl
    y_e = VKI_LNK_TOP_Y
    vs, fs = vki_prism(k, [(y_a, fl), (y_e, fl), (y_e, sof(y_e))], xa + 0.005, xb - 0.005, VKI_STONE_BLOCK_IN,
                       axis="x", project=False)
    k.project(fs, VKI_STONE_BLOCK_IN, offset=(0.0, 0.0), tile=1.5)
    for v in vs:
        k.set_dark([v], 0.15 + 0.35 * vki_smoothstep(1.2, 2.8, v.co.z))
    vs = vki_lnk_box(k, xa + 0.005, 1.495, y_e, VKI_LNK_BACK_Y - 0.005, fl, 2.80, VKI_STONE_BLOCK_IN, bev=0.0)
    k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN, tile=1.5)
    for v in vs:
        k.set_dark([v], 0.25 + 0.35 * vki_smoothstep(1.2, 2.8, v.co.z))
    # iron balustrade: newels 0.044, balusters 0.018 (bottoms 5 mm into their treads), a 0.05 x 0.04 handrail whose
    # top runs 0.95 above the pitch line until it meets the ceiling plane (y_t), newel tops 3 cm above the rail
    H = VKI_LNK_RAIL_H
    xr = VKI_DUN_RAIL_X
    y_t = (2.995 - H - r_) / kk
    tread = lambda y: r_ * (int(y // g_) + 1)
    for yp, w, cap in ([(0.05, 0.044, 0.03)] + [(yb, 0.018, -0.02) for yb in (0.30, 0.55, 0.80, 1.05, 1.30, 1.55, 1.80,
                                                                            2.05, 2.30)] + [(y_t - 0.03, 0.044, 0.0)]):
        vki_lnk_box(k, xr - w / 2, xr + w / 2, yp - w / 2, yp + w / 2, tread(yp) - 0.005,
                    min(P(yp) + H + cap, 2.995), IRON, bev=0.0)
    vki_dun_rod(k, (xr, 0.05, P(0.05) + H - 0.02), (xr, y_t, 2.975), 0.05, IRON, d=0.04)
    # lip: the upper-floor edge (the 15th step)
    vs = vki_dun_step(k, [(y_e, 2.80), (VKI_LNK_BACK_Y, 2.80), (VKI_LNK_BACK_Y, 3.0), (y_e, 3.0)], xa, 1.50, 0.3, "lip")
    vki_dun_stair_mats(k)
    vki_lnk_meta_common(k)
    (sx, sy), sf = VKI_LNK_UP_SPAWN
    k.meta.update(vki_link="stair_up", vki_pair="SM_VKI_Stair_Down_150x450_Stone", vki_trigger=VKI_LNK_UP_TRIGGER,
                  vki_spawn_local=[sx, sy], vki_spawn_facing=sf, vki_prompt_local=[0.80, 0.30, 1.40],
                  vki_floor_under="room floor laid under the whole footprint (no FLOOR faces)",
                  vki_nav="block", vki_collider=[[0.815, 2.2825, 1.5, 0.97, 3.865, 3.0]],
                  vki_lip=[xa, y_e, 2.80, 1.50, VKI_LNK_BACK_Y, 3.0], vki_no_wall="local x = 1.5 side (the rail side)")


def vki_dun_stair_down(k):
    """stone steps descending north -> south into a lined shaft: landing slab and trimmer kerbs (tops z 0), 10 wedge
    steps from z -0.20 to -2.00 darkening with depth, shaft linings of dressed stone, a closed VOID box under the
    steps, and along +X and across the south end a low stone upstand (0.12) carrying an iron railing (0.95): posts,
    top and mid rails, balusters -- see-through, so the steps going down stay visible (a solid 0.9 m parapet hid the
    whole flight from the game camera). Same footprint / metadata as the timber Stair_Down_150x450_RailR."""
    g_, r_ = VKI_LNK_GO, VKI_LNK_RISE
    P = vki_lnk_pitch_dn
    yt = VKI_LNK_TOP_Y
    xa, xb = VKI_LNK_X
    N = VKI_LNK_DN_TREADS
    d0, d1 = VKI_LNK_DN_DARK
    d = VKI_DUN_STAIR_D
    for j in range(1, N + 1):
        y0, y1, zt = yt - j * g_, yt - (j - 1) * g_, -r_ * j
        dk = d0 + (d1 - d0) * (j - 1) / (N - 1)
        # the block under tread j: its soffit parallel to the pitch line, d below it, clipped 5 mm over the VOID box
        poly = vki_dun_step_poly(y0, y1, zt, P(y0) - r_ - d, P(y1) - r_ - d, VKI_LNK_VOID_Z[1])
        vki_dun_step(k, poly, xa + 0.005, xb - 0.005, dk, "dn%d" % j)
    # landing slab and kerbs (tops z 0): landing to the proud line, east kerb, south kerb, west kerbs (the inner west
    # kerb runs on beside the landing to the proud line, as the timber trimmer does: stopped at yt it left a 15 mm slot
    # open to the void between the landing and kw2)
    vki_dun_step(k, [(yt, -0.30), (VKI_LNK_BACK_Y, -0.30), (VKI_LNK_BACK_Y, 0.0), (yt, 0.0)], xa, 1.50, 0.0, "land")
    zb = -0.30
    for (x0, x1, y0, y1, key) in ((xb, 1.50, 0.0, yt, "ke"), (VKI_LNK_POST_CLR, xb, 0.0, 0.10, "ks"),
                                  (VKI_LNK_POST_CLR, xa, 0.10, VKI_LNK_BACK_Y, "kw"),
                                  (VKI_LNK_WALL_CLR, VKI_LNK_POST_CLR, VKI_LNK_MID_CLR, 4.5 - VKI_LNK_POST_CLR, "kw2")):
        vs = vki_lnk_box(k, x0, x1, y0, y1, zb, 0.0, VKI_STONE_BLOCK_IN, bev=0.006)
        k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN, offset=vki_hash_off((x0, y0, 0.0)), tile=VKI_STO_TILE)
        vki_sto_top(k, vs, VKI_CAP, (x0, y0, 0.0))
    # VOID box under the steps (top 5 mm below the last step's soffit end)
    vki_lnk_box(k, xa + 0.01, xb - 0.01, 0.105, yt - 0.005, VKI_LNK_VOID_Z[0], VKI_LNK_VOID_Z[1] - 0.005, VOID, bev=0.0)
    # shaft linings (dressed stone, darkening with depth) on the west, east and south sides
    ldark = lambda z: vki_clamp(0.30 + 0.5 * (-0.3 - z) / 2.0, 0.30, 0.80)
    zl0, zl1 = VKI_LNK_VOID_Z[0] + 0.005, -0.295
    for x0, x1, y0, y1 in ((0.316, xa - 0.001, 0.086, yt - 0.005), (xb + 0.001, 1.284, 0.086, yt - 0.005),
                           (xa, xb, 0.086, 0.099)):
        vs = vki_lnk_box(k, x0, x1, y0, y1, zl0, zl1, VKI_STONE_BLOCK_IN, bev=0.0)
        k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN, tile=1.5)
        for v in vs:
            k.set_dark([v], ldark(v.co.z))
    # upstands on the east and south kerbs (they meet 5 mm apart in the SE corner), then the iron railing on them
    H = VKI_LNK_RAIL_H
    xe0, xe1 = xb + 0.03, 1.47
    ys = 0.059                                                   # the south upstand's centre line
    for (x0, x1, y0, y1, along) in ((xe0, xe1, 0.02, 3.0, (0, 1, 0)), (0.335, xe0 - 0.005, 0.02, 0.098, (1, 0, 0))):
        vs = vki_lnk_box(k, x0, x1, y0, y1, -0.004, 0.12, VKI_STONE_BLOCK_IN, bev=0.01)
        k.project(vki_faces_of(vs), VKI_STONE_BLOCK_IN, offset=vki_hash_off((x0, y0, 0.5)), tile=VKI_STO_TILE)
        vki_lnk_tops(k, vs, VKI_CAP, along=along)
    xe = (xe0 + xe1) / 2
    for (px, py) in ((0.39, ys), (xe, ys), (xe, 1.05), (xe, 2.05), (xe, 2.95)):
        vki_lnk_box(k, px - 0.022, px + 0.022, py - 0.022, py + 0.022, 0.115, H + 0.03, IRON, bev=0.0)
    for z in (H - 0.02, 0.52):
        # the south rail stops at the east rail's side face (overlapping, their tops were coplanar)
        vki_dun_rod(k, (0.39, ys, z), (xe - 0.025, ys, z), 0.05, IRON, d=0.04)
        vki_dun_rod(k, (xe, ys, z), (xe, 2.95, z), 0.05, IRON, d=0.04)
    for x in (0.64, 0.89, 1.14):
        vki_lnk_box(k, x - 0.009, x + 0.009, ys - 0.009, ys + 0.009, 0.115, H - 0.03, IRON, bev=0.0)
    for y in (0.30, 0.55, 0.80, 1.30, 1.55, 1.80, 2.30, 2.55, 2.80):
        vki_lnk_box(k, xe - 0.009, xe + 0.009, y - 0.009, y + 0.009, 0.115, H - 0.03, IRON, bev=0.0)
    vki_dun_stair_mats(k)
    vki_lnk_meta_common(k)
    (sx, sy), sf = VKI_LNK_DN_SPAWN
    xe = (xe0 + xe1) / 2
    k.meta.update(vki_link="stair_down", vki_pair="SM_VKI_Stair_Up_150x450_Stone", vki_trigger=VKI_LNK_DN_TRIGGER,
                  vki_spawn_local=[sx, sy], vki_spawn_facing=sf, vki_prompt_local=[1.485, 3.555, 1.40],
                  vki_floor_under="none: the piece covers its footprint (kerbs, landing); no FLOOR faces",
                  vki_nav="walk",
                  vki_collider=[[0.80, 1.86, 0.5, 0.94, 3.52, 1.0], [0.8875, 0.05, 0.5, 1.085, 0.10, 1.0],
                                [xe, 1.5, 0.5, xe1 - xe0, 2.99, 1.0]],
                  vki_collider_note="blocked boxes: the hole and the two railings; kerbs and landing walk at z 0",
                  vki_hole=[xa, 0.10, xb, yt], vki_no_wall="local x = 1.5 side (the rail side)")


def vki_dun_mirror_l(k, w=1.5):
    """the left-hand twin of a stair: the built piece mirrored across local x = w / 2, so its wall runs along local
    x = w and its open (rail) side is x = 0. A flight climbing with a wall on its right needs it: the right-hand
    stairs may not turn 180 and their rail side must stay clear of walls (placed against one, their lip lay in the
    wall's coping, coplanar with its cap, and the balustrade stood in the wall). Every local x of the metadata goes
    with the mesh; origin, cells and rotations stay the stair's."""
    for v in k.bm.verts:
        v.co.x = w - v.co.x
    bmesh.ops.reverse_faces(k.bm, faces=list(k.bm.faces))          # the mirror turned every face inside out
    m = k.meta
    fx = lambda x: round(w - x, 5)
    if "vki_collider" in m:
        m["vki_collider"] = [[fx(b[0])] + list(b[1:]) for b in m["vki_collider"]]
    for key in ("vki_trigger", "vki_spawn_local", "vki_prompt_local"):
        if key in m:
            m[key] = [fx(m[key][0])] + list(m[key][1:])
    if "vki_spawn_facing" in m:
        m["vki_spawn_facing"] = (-m["vki_spawn_facing"]) % 360       # compass: 0 = local +Y, 90 = +X
    for key, i, j in (("vki_lip", 0, 3), ("vki_hole", 0, 2)):         # boxes [x0, y0, (z0,) x1, ...]
        if key in m:
            a = list(m[key])
            a[i], a[j] = fx(a[j]), fx(a[i])
            m[key] = a
    if "vki_pair" in m:
        m["vki_pair"] += "L"
    m.update(vki_needs_walls=[f"local x = {w:g} (y 0..4.5)", f"local y = 4.5 (x 0..{w:g})"],
             vki_no_wall="local x = 0 side (the open / rail side)",
             vki_post_rule={"allowed": f"Mid post at local ({w:g}, 0); Corner post at local ({w:g}, 4.5)",
                            "forbidden": [[w, 1.5], [w, 3.0], [0.0, 4.5]],
                            "note": "rhythm posts are skipped along the stair's walls (§2.3)"})


def vki_dun_stair_up_l(k):
    """Stair_Up_150x450_Stone with its wall on the right going up (vki_dun_mirror_l)"""
    vki_dun_stair_up(k)
    vki_dun_mirror_l(k)


def vki_dun_stair_down_l(k):
    """Stair_Down_150x450_Stone with its wall on the right going down the flight's length (vki_dun_mirror_l)"""
    vki_dun_stair_down(k)
    vki_dun_mirror_l(k)


# ---------------------------------------------------------------- adventure kit: passage, dart trap, secret door, leaves
VKI_DUN_PASS = dict(x=(0.33, 1.17), crown=2.15, void_y=(0.20, 0.215))
VKI_DUN_SECRET = dict(x=(0.33, 1.17), top=2.20, void_y=(0.21, 0.225))


def vki_dun_passage(k):
    """a rough breach through the wall leading into darkness (adventure kit, a scene link): piers x 0-0.33 / 1.17-1.5,
    the masonry over the gap broken along a jagged line (crown about 2.15), broken dressed blocks jutting from the
    edge, a VOID card at the back, rubble slabs in the gap and a few fallen blocks on the room side. The link data
    (vki_link "passage", target) is written by the assembler (R["passages"])."""
    L = 1.5
    P = VKI_DUN_PASS
    x0, x1 = P["x"]
    zb, zt = VKI_STO_FULL
    rnd = random.Random(47)
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)
    xs = [x0, 0.45, 0.58, 0.70, 0.82, 0.95, 1.06, x1]
    jag = {x: P["crown"] - 0.55 * ((x - 0.75) / 0.42) ** 2 + rnd.uniform(-0.07, 0.07) for x in xs}
    jag[x0] = jag[x1] = 1.80
    zfn = lambda x: jag[min(jag, key=lambda a: abs(a - x))]
    vki_sto_strips(k, x0, x1, zfn, zb, xs)
    for i, (a, b) in enumerate(zip(xs[:-1], xs[1:])):                          # broken blocks along the edge
        if i % 2 == 0:
            z = min(zfn(a), zfn(b))
            vki_sto_block(k, a + 0.01, b - 0.01, z - 0.09, z + 0.14, -0.27 - 0.02 * rnd.random(), 0.12,
                          key="pbrk%d" % i)
    vki_sto_block(k, x0 - 0.02, x1 + 0.02, 0.0, 0.03, -0.26, 0.19, mi=DRESS, bev=0.01, dark=0.25)   # rubble floor
    for (cx, cy, s, r) in ((0.54, -0.46, 0.16, 0.5), (0.98, -0.52, 0.18, -0.3), (0.80, -0.82, 0.11, 1.1)):  # T3: clear of the node zones
        vs = list(set(k.box((cx, cy, s * 0.42), (s, s * 0.8, s * 0.8), VKI_STONE_BLOCK_IN, rot=(0.25, -0.2, r),
                            bevel=0.02, jitter=0.01, seed=int(cx * 100))))
        k.set_dark(vs, 0.15)
    v0, v1 = P["void_y"]
    k.box(((x0 + x1) / 2, (v0 + v1) / 2, 1.2), (x1 - x0 + 0.02, v1 - v0, 2.4), VOID, bevel=0.0)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dungeon", "A", holes=[(x0, 0.0, x1, P["crown"] + 0.2)], top_body_fn=lambda x: zb)
    vki_dun_damp(k)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_DUN_CUT_TO, vki_nav="door", vki_nav_open=[x0, x1],
                  vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": 1.8, "head": "broken", "passage": 1},
                  vki_trigger=[0.75, -0.55, 1.0, 0.8, 0.7, 2.0], vki_spawn_local=[0.75, -1.60],
                  vki_prompt_local=[0.75, -0.30, 1.40], vki_prompt_text="Go through",
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])


def vki_dun_darttrap(k):
    """plain Full wall with a dressed band (1.00-1.40, x 0.36-1.14, 3 cm proud) pierced by four VOID dart holes; the
    emitters are in vki_trap (piece-local, firing toward -Y) and vki_fx"""
    vki_dun_plain(k, 1.5, "Full", "A")
    vki_sto_block(k, 0.36, 1.14, 1.00, 1.40, -0.28, -0.20, key="dband", dark=0.05)
    holes = []
    for x in (0.48, 0.66, 0.84, 1.02):
        k.box((x, -0.281, 1.20), (0.036, 0.008, 0.036), VOID, bevel=0.0)
        holes.append([x, -0.29, 1.20])
    k.meta.update(vki_cut_to=VKI_DUN_CUT_TO,
                  vki_trap={"kind": "darts", "emitters": holes, "dir": [0, -1, 0]},
                  vki_fx=[dict(fx="dart_launch", pos=h, scale=0.3) for h in holes])


def vki_dun_secret(k):
    """plain-faced Full wall with a hidden opening x 0.33-1.17, z 0-2.20 (no dressed surround, a flat soffit inside
    the body), a VOID card behind it; closed by Leaf_SecretStone_Full (its face textured like the wall)"""
    L = 1.5
    S = VKI_DUN_SECRET
    x0, x1 = S["x"]
    zb, zt = VKI_STO_FULL
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)
    vki_sto_body(k, x0, x1, S["top"], zb)
    vki_sto_block(k, x0, x1, -0.10, -0.004, -k.T / 2, k.T / 2, mi=DRESS, bev=0.006, dark=0.3)    # sill under the floor
    v0, v1 = S["void_y"]
    k.box(((x0 + x1) / 2, (v0 + v1) / 2, 1.1), (x1 - x0 + 0.02, v1 - v0, 2.2), VOID, bevel=0.0)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dungeon", "A", holes=[(x0, 0.0, x1, S["top"])], top_body_fn=lambda x: zb)
    vki_dun_damp(k)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_DUN_CUT_TO, vki_nav="door", vki_nav_open=[x0, x1], vki_secret=1,
                  vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": S["top"], "head": "flat", "secret": 1},
                  vki_leaf="SM_VKI_Leaf_SecretStone_Full", vki_leaf_socket=[x0 + 0.005, -k.T / 2, 0.0],
                  vki_leaf_open_deg=90,
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])


def vki_dun_leaf_iron_full(k):
    """locked iron-bound door for Door_150_Full: the Full plank leaf in dark oak with studs on its straps, a judas
    grille, a lock plate and keyhole; vki_openable (the BFS walks through it: it opens in play), vki_locked"""
    vki_leaf_plank(k, "Full")
    y0 = VKI_LEAF_Y0
    for z in (0.36, 1.12, 1.88):
        for x in (0.25, 0.45, 0.65):
            k.box((x, y0 - 0.017, z), (0.024, 0.012, 0.024), IRON, bevel=0.0)
    k.box((0.42, y0 - 0.003, 1.62), (0.20, 0.010, 0.15), VOID, bevel=0.0)                       # judas opening
    for x in (0.37, 0.47):
        k.box((x, y0 - 0.010, 1.62), (0.016, 0.012, 0.17), IRON, bevel=0.0)
    k.box((0.765, y0 - 0.005, 0.98), (0.07, 0.012, 0.16), IRON, bevel=0.003)
    k.box((0.765, y0 - 0.012, 0.96), (0.012, 0.004, 0.035), VOID, bevel=0.0)
    k.slot_mats[WOOD] = "Dark"
    k.meta.update(vki_openable=1, vki_locked=1,
                  vki_leaf_fits="SM_VKI_Wall_Dungeon_Door_150_Full at its vki_leaf_socket, same rotation (R door_leaves)")


def vki_dun_leaf_secret(k):
    """the secret door: a stone slab 0.83 x 0.30 x 2.16 hinged at the origin (room face), faced like the wall --
    DungeonIn with UVs locked to the door's frame (u = -(x + 0.335) / 1.5), so closed it continues the wall's block
    pattern -- with the wall grime and damp band; opens toward -Y"""
    x0, x1 = 0.005, 0.835
    ya, yb = 0.004, 0.300
    z0, z1 = 0.005, 2.195
    before = set(k.bm.verts)
    k.box(((x0 + x1) / 2, (ya + yb) / 2, (z0 + z1) / 2), (x1 - x0, yb - ya, z1 - z0), VKI_WALL_A, bevel=0.0)
    vs = [v for v in k.bm.verts if v not in before]
    grid_cut(k, vs, 0.25)
    vs = [v for v in k.bm.verts if v not in before]
    k.bm.normal_update()
    for f in vki_faces_of(vs):
        n = f.normal
        f.material_index = VKI_WALL_A
        if abs(n.z) > 0.7:
            U = Vector((-1, 0, 0)); V = Vector((0, 1, 0))
        else:
            U = n.cross(Vector((0, 0, 1))); U.normalize(); V = Vector((0, 0, 1))
        for l in f.loops:
            p = l.vert.co + Vector((0.335, -0.25, 0.0))
            l[k.uv].uv = (p.dot(U) / 1.5, p.dot(V) / 1.5)
    vki_dun_damp(k)
    k.slot_mats[VKI_WALL_A] = "M_VKI_DungeonIn"
    k.meta.update(vki_class="leaf", hinge_axis="local Z", vki_leaf_state="closed", vki_leaf_open_deg=90,
                  vki_leaf_width=round(x1 - x0, 3), vki_leaf_height=round(z1 - z0, 3), vki_hinge=[0.0, 0.0, 0.0],
                  vki_leaf_clearance=0.005, vki_openable=1, vki_secret=1,
                  vki_leaf_open_dir="rotation -deg about local Z (toward the room, -Y)",
                  vki_leaf_fits="SM_VKI_Wall_Dungeon_Secret_150_Full at its vki_leaf_socket, same rotation")


VKI_DUN_PORT = dict(w=1.84, h=2.20, bars=12, rails=(0.45, 0.95, 1.45, 1.95), spike=0.10)


def vki_dun_leaf_portcullis(k):
    """portcullis for DoorWide_300_Full: a grille 1.84 x 2.20 in the wall's centre plane (origin at its bottom left,
    place it at door-local (0.58, 0.0)); 12 flat verticals ending in spikes, four rails; it slides up
    (vki_leaf_motion slide_z, up to 0.75: its top beam then stays under the coping top)"""
    P = VKI_DUN_PORT
    w, h = P["w"], P["h"]
    n = P["bars"]
    sp = P["spike"]
    for i in range(n):
        x = 0.06 + (w - 0.12) * i / (n - 1)
        k.box((x, 0.0, (sp + h - 0.02) / 2), (0.04, 0.05, h - 0.02 - sp), IRON, bevel=0.0)       # tops in the beam
        _cyl(k, (x, 0.0, sp / 2 + 0.002), 0.004, 0.026, sp, 4, IRON, rot=Matrix.Rotation(math.pi / 4, 4, "Z"))
    for z in P["rails"]:
        k.box((w / 2, 0.0, z), (w, 0.07, 0.06), IRON, bevel=0.0)
    k.box((w / 2, 0.0, h - 0.04), (w, 0.08, 0.08), IRON, bevel=0.0)
    k.meta.update(vki_class="leaf", hinge_axis="none (slides along local Z)", vki_leaf_motion="slide_z",
                  vki_leaf_travel=0.75, vki_leaf_state="closed", vki_openable=1, vki_see_through=1,
                  vki_leaf_fits="SM_VKI_Wall_Dungeon_DoorWide_300_Full at door-local (0.58, 0.0), same rotation")


# ---------------------------------------------------------------- specs
VKI_DUN_SPECS = [
    ("SM_VKI_Wall_Dungeon_Plain_150A_Full", vki_dun_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Dungeon_Plain_150A_Cut", vki_dun_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Dungeon_Plain_150B_Full", vki_dun_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Dungeon_Plain_300_Full", vki_dun_plain_300_full, "wall"),
    ("SM_VKI_Wall_Dungeon_Plain_300_Cut", vki_dun_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Dungeon_Rake_150_L", vki_dun_rake_l, "wall"),
    ("SM_VKI_Wall_Dungeon_Rake_150_R", vki_dun_rake_r, "wall"),
    ("SM_VKI_Wall_Dungeon_Door_150_Full", vki_dun_door_full, "wall"),
    ("SM_VKI_Wall_Dungeon_Door_150_Cut", vki_dun_door_cut, "wall"),
    ("SM_VKI_Wall_Dungeon_DoorWide_300_Full", vki_dun_door_wide_full, "wall"),
    ("SM_VKI_Wall_Dungeon_DoorWide_300_Cut", vki_dun_door_wide_cut, "wall"),
    ("SM_VKI_Wall_Dungeon_Window_150_Full", vki_dun_window, "wall"),
    ("SM_VKI_Wall_Dungeon_Niche_150_Full", vki_dun_niche_full, "wall"),
    ("SM_VKI_Wall_Dungeon_Niche_150_Cut", vki_dun_niche_cut, "wall"),
    ("SM_VKI_Post_Dungeon_Corner_Full", vki_dun_post_corner_full, "wall"),
    ("SM_VKI_Post_Dungeon_Corner_Cut", vki_dun_post_corner_cut, "wall"),
    ("SM_VKI_Post_Dungeon_Mid_Full", vki_dun_post_mid_full, "wall"),
    ("SM_VKI_Post_Dungeon_Mid_Cut", vki_dun_post_mid_cut, "wall"),
    ("SM_VKI_Wall_Bars_Plain_150A_Full", vki_bar_plain_150, "wall"),
    ("SM_VKI_Wall_Bars_Plain_300_Full", vki_bar_plain_300, "wall"),
    ("SM_VKI_Wall_Bars_Door_150_Full", vki_bar_door, "wall"),
    ("SM_VKI_Post_Bars_Corner_Full", vki_bar_post_corner, "wall"),
    ("SM_VKI_Post_Bars_Mid_Full", vki_bar_post_mid, "wall"),
    ("SM_VKI_Leaf_Iron_Cut", vki_dun_leaf_iron, "prop"),
    ("SM_VKI_Leaf_BarsGate_Full", vki_dun_leaf_gate, "prop"),
    ("SM_VKI_Stair_Up_150x450_Stone", vki_dun_stair_up, "prop"),
    ("SM_VKI_Stair_Down_150x450_Stone", vki_dun_stair_down, "prop"),
    ("SM_VKI_Stair_Up_150x450_StoneL", vki_dun_stair_up_l, "prop"),
    ("SM_VKI_Stair_Down_150x450_StoneL", vki_dun_stair_down_l, "prop"),
    # adventure kit
    ("SM_VKI_Wall_Dungeon_Passage_150_Full", vki_dun_passage, "wall"),
    ("SM_VKI_Wall_Dungeon_DartTrap_150_Full", vki_dun_darttrap, "wall"),
    ("SM_VKI_Wall_Dungeon_Secret_150_Full", vki_dun_secret, "wall"),
    ("SM_VKI_Leaf_Iron_Full", vki_dun_leaf_iron_full, "prop"),
    ("SM_VKI_Leaf_SecretStone_Full", vki_dun_leaf_secret, "wall"),
    ("SM_VKI_Leaf_Portcullis_300", vki_dun_leaf_portcullis, "prop"),
]
VKI_DUN_NAMES = [n for n, _, _ in VKI_DUN_SPECS]
vki_register([(n, fn, {"grime": gr}, "dungeon") for n, fn, gr in VKI_DUN_SPECS])
