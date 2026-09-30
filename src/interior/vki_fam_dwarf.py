# ===================== VKI FAM DWARF: dwarven halls -- the Dwarf wall family, lava channels, hall props (dwarf kit) =====================
# Dwarf kit (docs/DWARF_KIT.md). Package "adventure". Loaded by vki_ns() after vki_fam_water; uses the Stone builders
# (vki_sto_*), the ancient trim idea (courses on the 0.75 grid), the sewer's channel tiles (vki_sew_channel), and at
# build time the prop helpers (vki_dpr_*, vki_home_*, vki_sto_flame / embers). Every top-level name starts with
# vki_/VKI_ (T18).
# Dwarf (class O, T 0.50, H 3.0): halls cut into the mountain -- big precise granite ashlar (T_VKI_DwarfIn: 0.5 m
#   courses, blocks 0.75 / 1.5 m, crisp joints), a plinth course (0-0.28) and on Full walls a rune band (2.20-2.50) with a
#   gilded line (2.33-2.37), both 3 cm proud of BOTH faces (partitions show both) and cut on the 0.75 grid, so every end
#   profile carries them (T2); pale polished coping (DwarfCap), dark dressed stone (DwarfBlock), gold (TEXTILE slot).
#   Plain 150A / 150B (a carved relief: raised frame, lozenge, gold rune disc) / 300, Full and Cut; Rake L / R; posts (a
#   square pier with a stepped capital and a gold ring); Door_150 (a corbelled doorway: the opening's top corners cut by
#   45-degree corbels under a massive lintel with a gold band); DoorWide_300 (the great gate: the same at 1.80 x 2.45,
#   closed by Leaf_DwarfGate_300, two rune-carved stone leaves); Passage_150_Full (a dark corbelled doorway: a scene
#   link); Breach_150 / _300, Full and Cut (vki_brk_breach, with the plinth and band on their intact ends).
# Lava channels: cells coded "ll" in a cave map -- the sewer's channel tiles (five rotation classes, rotated, no floor)
#   with dark dressed-stone kerbs and molten lava at -0.20 on a heat gradient (vki_rim: the hot core down the middle,
#   M_VKI_Lava yellow-white there and deep red at the banks), crust plates cooling along the banks; a light per tile;
#   vki_flow from R["lava_sinks"] (Unity animates the lava).
# Props: Pillar_Dwarf_Cut / _Full, Statue_DwarfKing, Throne_Dwarf (on its own dais), Brazier_Dwarf, Forge_Dwarf,
#   Anvil_Dwarf, Bridge_Dwarf (a stone arch bridge over a two-cell chasm), Banner_Dwarf (a clan banner, wall_hung),
#   Overlay_RuneCircle (a gold floor medallion).
# Build: g["vki_ws_build"]("adventure", VKI_DWF_NAMES); test: g["vki_test_pieces"](VKI_DWF_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_DWF_CUT_TO = "SM_VKI_Wall_Dwarf_Plain_150A_Cut"
VKI_DWF_PLINTH = (0.0, 0.28)          # the plinth course, 3 cm proud of both faces
VKI_DWF_BAND = (2.20, 2.50)           # the rune band on Full walls, 3 cm proud of both faces
VKI_DWF_GOLD = (2.33, 2.37)           # its gilded line, 4 mm proud of the band
VKI_DWF_HW = 0.28                     # course half width (the coping's)
VKI_DWF_DOOR = {1.5: dict(open=(0.33, 1.17), top=2.25, cor=0.22, lint=(2.25, 2.70)),
                3.0: dict(open=(0.60, 2.40), top=2.45, cor=0.32, lint=(2.45, 2.85))}
VKI_DWF_POST_Z = {"Full": (-0.30, 0.28, 2.52, 2.74, 3.04), "Cut": (-0.30, 0.28, 0.80, 0.92, 1.04)}
VKI_DWF_LAVA = dict(water=-0.20, bed=-0.75, rim=0.15, kerb=0.06)
VKI_DWF_HEAT = (0.02, 0.55)           # the lava's heat: a smoothstep of the distance from the banks (m), 1 = the core


# ---------------------------------------------------------------- family patch, trim
def vki_dwf_patch(k, leaf=None):
    """Stone-built geometry -> Dwarf: family (materials, metadata), a faint grime toward the floor, gold on the TEXTILE
    slot, the Dwarf cut target"""
    k.set_family("Dwarf")
    vki_dun_damp(k, 0.10, 0.45)
    if k.meta.get("vki_cut_to") in (VKI_STO_CUT_TO, VKI_DUN_CUT_TO, VKI_ANC_CUT_TO):
        k.meta["vki_cut_to"] = VKI_DWF_CUT_TO
    if leaf:
        k.meta["vki_leaf"] = leaf
    vki_dpr_gold_mats(k)


def vki_dwf_course(k, a, b, z0, z1, key, dark=0.03):
    """a dressed course 3 cm proud of both faces over [a, b], in units on the piece's 0.75 grid (bevelled: V-joints)"""
    cuts = [a] + [0.75 * i for i in range(1, 5) if a + 1e-6 < 0.75 * i < b - 1e-6] + [b]
    for u0, u1 in zip(cuts[:-1], cuts[1:]):
        vki_sto_block(k, u0, u1, z0, z1, -VKI_DWF_HW, VKI_DWF_HW, key="%s%d" % (key, int(round(u0 * 100))), dark=dark)


def vki_dwf_trim(k, spans, full, band_spans=None):
    """the plinth course over spans; on Full walls the rune band and its gilded line over band_spans (default: spans)"""
    for a, b in spans:
        vki_dwf_course(k, a, b, *VKI_DWF_PLINTH, "dpl")
    if full:
        g0, g1 = VKI_DWF_GOLD
        Lx = max(b for a, b in spans)
        for a, b in (band_spans if band_spans is not None else spans):
            vki_dwf_course(k, a, b, *VKI_DWF_BAND, "dbd")
            ga = a + (0.01 if a > 1e-6 else 0.0)                         # 1 cm short of a band end inside the piece
            gb = b - (0.01 if b < Lx - 1e-6 else 0.0)                    # (its end face not in the band's plane, T5S)
            k.box(((ga + gb) / 2, 0.0, (g0 + g1) / 2), (gb - ga, 2 * VKI_DWF_HW + 0.008, g1 - g0), VKI_DPR_GOLD,
                  bevel=0.0)


def vki_dwf_relief(k):
    """a carved panel on face A (x 0.36-1.14, z 0.85-1.95, 4 cm proud): a raised frame, a lozenge, a gold rune disc at
    its heart and gold studs at its points"""
    vki_sto_block(k, 0.36, 1.14, 0.85, 1.95, -0.29, -0.22, key="drp", dark=0.05)
    for (a, b, c, d) in ((0.36, 1.14, 1.88, 1.95), (0.36, 1.14, 0.85, 0.92), (0.36, 0.43, 0.92, 1.88),
                         (1.07, 1.14, 0.92, 1.88)):
        vki_sto_block(k, a, b, c, d, -0.305, -0.285, bev=0.006, key="drf%d%d" % (int(a * 100), int(c * 100)))
    pts = ((0.75, 1.02), (1.00, 1.40), (0.75, 1.78), (0.50, 1.40))
    vki_prism(k, list(pts), -0.30, -0.285, VKI_STONE_BLOCK_IN, axis="y", bevel=0.006)
    _cyl(k, (0.75, -0.304, 1.40), 0.085, 0.085, 0.012, 8, VKI_DPR_GOLD, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    for (x, z) in pts:
        k.box((x, -0.302, z), (0.04, 0.012, 0.04), VKI_DPR_GOLD, bevel=0.0)


# ---------------------------------------------------------------- Plain, Rake
def vki_dwf_plain(k, L, height, variant="A"):
    full = height == "Full"
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    vki_sto_body(k, 0.0, L, VKI_FOOT_Z, zb)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    vki_dwf_trim(k, [(0.0, L)], full)
    if variant == "B":
        vki_dwf_relief(k)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dwarf", variant, holes=[], top_body_fn=lambda x: zb)
    vki_dwf_patch(k)
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_DWF_CUT_TO)


def vki_dwf_plain_150a_full(k): vki_dwf_plain(k, 1.5, "Full", "A")
def vki_dwf_plain_150a_cut(k): vki_dwf_plain(k, 1.5, "Cut", "A")
def vki_dwf_plain_150b_full(k): vki_dwf_plain(k, 1.5, "Full", "B")
def vki_dwf_plain_300_full(k): vki_dwf_plain(k, 3.0, "Full", "A")
def vki_dwf_plain_300_cut(k): vki_dwf_plain(k, 3.0, "Cut", "A")


def vki_dwf_rake(k, side):
    vki_sto_rake(k, side)
    hi = VKI_STO_RAKE["hi"]
    vki_dwf_trim(k, [(0.0, 1.5)], True, band_spans=[(hi, 1.5)] if side == "L" else [(0.0, 1.5 - hi)])
    vki_dwf_patch(k)


def vki_dwf_rake_l(k): vki_dwf_rake(k, "L")
def vki_dwf_rake_r(k): vki_dwf_rake(k, "R")


# ---------------------------------------------------------------- posts
def vki_dwf_post(k, kind, height):
    """Corner: a monolithic square pier -- plinth +-0.31, the shaft +-0.28 with rounded arrises and a gold ring, a
    two-stepped capital with a CAP top; Mid: the same as a pilaster (+-0.12 along the wall)"""
    k.set_family("Dwarf")
    z0, z1, z2, z3, z4 = VKI_DWF_POST_Z[height]
    ay = VKI_POST_HW["O"]
    ax = ay if kind == "Corner" else VKI_MID_HW["O"][0]
    sx, sy = (ax - 0.03 if kind == "Corner" else ax - 0.015), ay - 0.03
    vki_sto_block(k, -ax, ax, z0, z1, -ay, ay, bev=VKI_POST_BEVEL, key="dpp%s" % kind)
    vki_sto_block(k, -sx, sx, z1, z2, -sy, sy, bev=VKI_POST_BEVEL, key="dps%s" % kind, dark=0.03)
    vki_sto_block(k, -(ax - 0.012), ax - 0.012, z2, z3, -(ay - 0.012), ay - 0.012, bev=0.012, key="dc1%s" % kind)
    vki_sto_block(k, -ax, ax, z3, z4, -ay, ay, bev=VKI_POST_BEVEL, top=VKI_CAP, key="dc2%s" % kind)
    gz = z2 - 0.10
    k.box((0.0, 0.0, gz), (2 * sx + 0.012, 2 * sy + 0.012, 0.04), VKI_DPR_GOLD, bevel=0.0)
    vki_dun_damp(k, 0.10, 0.45)
    vki_dpr_gold_mats(k)
    other = "Cut" if height == "Full" else "Full"
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height,
                                                   "toggle_to": f"SM_VKI_Post_Dwarf_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any",
                                                   "rule": "§2.3; Cave > Ancient > Dwarf > Dungeon > Sewer > Stone ... "
                                                           "in priority"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_dwf_post_corner_full(k): vki_dwf_post(k, "Corner", "Full")
def vki_dwf_post_corner_cut(k): vki_dwf_post(k, "Corner", "Cut")
def vki_dwf_post_mid_full(k): vki_dwf_post(k, "Mid", "Full")
def vki_dwf_post_mid_cut(k): vki_dwf_post(k, "Mid", "Cut")


# ---------------------------------------------------------------- corbelled doors, the great gate
def vki_dwf_door(k, height, wide=False):
    """the corbelled dwarven doorway: 150 -- clear x 0.33-1.17 to 2.25, its top corners cut by 45-degree corbels
    (0.22); 300 (the great gate) -- clear x 0.60-2.40 to 2.45, corbels 0.32. Dressed jambs (0.17 wide, 4 cm proud of
    both faces) stand on the floor; on Full a massive lintel (5 cm proud, a gold band across it) spans past them and
    the rune band runs into it; Cut keeps the jambs under the coping units that wrap the reveals"""
    L = 3.0 if wide else 1.5
    D = VKI_DWF_DOOR[L]
    full = height == "Full"
    x0, x1 = D["open"]
    top, c = D["top"], D["cor"]
    l0, l1 = D["lint"]
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    T2 = k.T / 2
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)
    vki_sto_block(k, x0, x1, 0.0, 0.03, -0.26, 0.26, bev=0.01, dark=0.10, key="dthr")
    jt = top - c if full else zb + VKI_STO_TUCK
    vki_sto_block(k, x0 - 0.18, x0 - 0.01, 0.0, jt, -0.29, 0.29, key="djl")
    vki_sto_block(k, x1 + 0.01, x1 + 0.18, 0.0, jt, -0.29, 0.29, key="djr")
    if full:
        for pts in ([(x0 - 0.01, top - c), (x0 + c, top), (x0 - 0.01, top)],
                    [(x1 + 0.01, top - c), (x1 + 0.01, top), (x1 - c, top)]):
            vki_prism(k, pts, -0.29, 0.29, VKI_STONE_BLOCK_IN, axis="y", bevel=0.008)
        vki_sto_block(k, x0 - 0.24, x1 + 0.24, l0, l1, -0.30, 0.30, key="dlint")
        k.box(((x0 + x1) / 2, 0.0, (l0 + l1) / 2), (x1 - x0, 0.608, 0.05), VKI_DPR_GOLD, bevel=0.0)   # T3: over the opening
        vki_sto_body(k, x0, x1, l1, zb)
        vki_sto_coping(k, 0.0, L, zb, zt, L)
        vki_dwf_trim(k, [(0.0, x0 - 0.18 + 0.03), (x1 + 0.18 - 0.03, L)], True,
                     band_spans=[(0.0, x0 - 0.24 + 0.05), (x1 + 0.24 - 0.05, L)])
        holes = [(x0 - 0.18, 0.0, x1 + 0.18, l1)]
        z1 = top
    else:
        vki_sto_coping(k, 0.0, x0, zb, zt, L, fixed=True)
        vki_sto_coping(k, x1, L, zb, zt, L, fixed=True)
        vki_dwf_trim(k, [(0.0, x0 - 0.18 + 0.03), (x1 + 0.18 - 0.03, L)], False)
        holes = [(x0 - 0.18, 0.0, x1 + 0.18, zt)]
        z1 = zt
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Dwarf", "A", holes=holes, top_body_fn=lambda x: zb)
    vki_dwf_patch(k)
    cx = (x0 + x1) / 2
    k.meta.update(vki_class="wall", vki_nav="door", vki_nav_open=[x0, x1],
                  vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": round(z1, 4), "head": "corbelled" if full else "cut"},
                  vki_trigger=[cx, -0.65, 1.0, x1 - x0 + 0.06, 0.8, 2.0], vki_spawn_local=[cx, -1.60],
                  vki_prompt_local=[cx, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])
    if wide:
        k.meta.update(vki_leaf_socket=[[x0, -T2 + 0.05, 0.0], [x1, -T2 + 0.05, 0.0]], vki_leaf_open_deg=90)
        if full:
            k.meta["vki_leaf"] = "SM_VKI_Leaf_DwarfGate_300"
    else:
        k.meta.update(vki_leaf_socket=[x0, -T2 + 0.05, 0.0], vki_leaf_open_deg=90,
                      vki_leaf="SM_VKI_Leaf_Plank_" + height)


def vki_dwf_door_full(k): vki_dwf_door(k, "Full")
def vki_dwf_door_cut(k): vki_dwf_door(k, "Cut")
def vki_dwf_door_wide_full(k): vki_dwf_door(k, "Full", wide=True)
def vki_dwf_door_wide_cut(k): vki_dwf_door(k, "Cut", wide=True)


def vki_dwf_passage(k):
    """a dark corbelled doorway (Door_150_Full with darkness behind it): a scene link"""
    vki_dwf_door(k, "Full")
    k.box((0.75, 0.2075, 1.115), (0.82, 0.015, 2.17), VOID, bevel=0.0)             # inside the corbels' planes
    for key in ("vki_leaf", "vki_leaf_socket", "vki_leaf_open_deg"):
        k.meta.pop(key, None)
    k.meta.update(vki_cut_to=VKI_DWF_CUT_TO, vki_nav="door", vki_prompt_text="Go through",
                  vki_trigger=[0.75, -0.55, 1.0, 0.8, 0.7, 2.0], vki_spawn_local=[0.75, -1.60])


def vki_dwf_leaf_gate(k):
    """the great gate's two stone leaves, closed, for Wall_Dwarf_DoorWide_300_Full: from the left hinge (the local
    origin, the door's first leaf socket at x 0.60) two leaves 0.89 wide fill the opening (x 0.005-1.795, z 0.01-2.44,
    their outer top corners cut to the corbels), 0.12 thick (local y 0.004-0.124); on the room face raised borders,
    a lozenge split down the seam under a gold rune disc, gold hinge bands. They swing apart (swing_pair: hinges at
    local x 0 and 1.80)"""
    D = VKI_DWF_DOOR[3.0]
    W = D["open"][1] - D["open"][0]
    top, c = D["top"], D["cor"]
    y0, y1 = 0.004, 0.124
    fl = lambda x, m: W - x if m else x
    for m in (False, True):
        pts = [(0.005, 0.01), (0.895, 0.01), (0.895, top - 0.01), (c + 0.005, top - 0.01), (0.005, top - c)]
        pts = [(fl(x, m), z) for x, z in pts]
        vki_prism(k, pts if not m else pts[::-1], y0, y1, VKI_STONE_BLOCK_IN, axis="y", bevel=0.008)
        for (a, b, zz0, zz1) in ((0.06, 0.84, 0.10, 0.16), (0.06, 0.84, 2.02, 2.08), (0.06, 0.12, 0.16, 2.02),
                                 (0.78, 0.84, 0.16, 2.02)):
            xa, xb = sorted((fl(a, m), fl(b, m)))
            vki_sto_block(k, xa, xb, zz0, zz1, -0.012, 0.006, bev=0.004, key="lgb%d%d%d" % (int(m), int(a * 100), int(zz0 * 100)))
        tri = [(0.895, 0.66), (0.895, 1.94), (0.46, 1.30)]
        tri = [(fl(x, m), z) for x, z in tri]
        vki_prism(k, tri if not m else tri[::-1], -0.014, 0.005, VKI_CAP, axis="y", bevel=0.004)
        for z in (0.40, 1.30, 2.00):
            xa, xb = sorted((fl(0.02, m), fl(0.40, m)))
            k.box(((xa + xb) / 2, -0.002, z), (xb - xa, 0.012, 0.06), VKI_DPR_GOLD, bevel=0.0)
    _cyl(k, (W / 2, -0.019, 1.30), 0.16, 0.16, 0.012, 12, VKI_DPR_GOLD, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_DwarfBlock"
    k.slot_mats[VKI_CAP] = "M_VKI_DwarfCap"
    vki_dpr_gold_mats(k)
    k.meta.update(vki_class="leaf", hinge_axis="z at local x 0 (left leaf) and x %.2f (right leaf)" % W,
                  vki_leaf_motion="swing_pair", vki_leaf_state="closed", vki_openable=1,
                  vki_hinges=[[0.0, y0, 0.0], [round(W, 3), y0, 0.0]],
                  vki_leaf_fits="SM_VKI_Wall_Dwarf_DoorWide_300_Full at vki_leaf_socket[0], same rotation",
                  vki_collider=[[W / 2, (y0 + y1) / 2, 1.2, W, y1 - y0, 2.4]])


# ---------------------------------------------------------------- lava channels
def vki_dwf_lava_quarters(code):
    """the X quarters of a channel code: [(sx, sy, bank_u, bank_v, inner)] -- bank_u: floor across x = 0 (the quarter's
    rim runs along y), bank_v: floor across y = 0, inner: the inner corner (both neighbours channel, the diagonal floor)"""
    X = [c == "X" for c in code]
    out = []
    for i, (sx, sy) in enumerate(VKI_SEW_QUAD):
        if X[i]:
            hn, vn, dn = (VKI_SEW_QUAD.index(q_) for q_ in ((-sx, sy), (sx, -sy), (-sx, -sy)))
            out.append((sx, sy, not X[hn], not X[vn], X[hn] and X[vn] and not X[dn]))
    return out


def vki_dwf_lava_heat(x, y, q, rw, wob):
    """heat 0..1 at tile-local (x, y) of quarter q: a smoothstep (VKI_DWF_HEAT) of the distance to the nearest bank (the
    rims' inner faces, the inner corner's block). Seamless: at a tile edge (a cell's centre line) the distance is the
    same from both tiles, or 0.60 from a bank, past the smoothstep's top; the wobble (a, b, f) that bends the core
    fades to 0 at the tile's edges."""
    sx, sy, bu, bv, inner = q
    u, v = sx * x, sy * y
    d = 9.0
    if bu:
        d = min(d, u - rw)
    if bv:
        d = min(d, v - rw)
    if inner:
        d = min(d, math.hypot(max(u - rw, 0.0), max(v - rw, 0.0)))
    a, b, f = wob
    fade = math.sin(math.pi * (x + 0.75) / 1.5) * math.sin(math.pi * (y + 0.75) / 1.5)
    d += 0.09 * fade * math.sin(f * x + a) * math.cos(0.8 * f * y + b)
    return vki_smoothstep(VKI_DWF_HEAT[0], VKI_DWF_HEAT[1], max(d, 0.0))


def vki_dwf_lava_pool(k, rect, q, C, wob, step=(0.10, 0.25)):
    """the lava in one rect: a volume from the bed up to the surface, open below (the tile's vki_open_bottom), its top a
    grid whose vertices carry the heat -- the WATER slot. Grid step: step[0] across a bank (the heat's rise), step[1]
    along it (only the wobble changes there); one quad where no bank is near."""
    x0, y0, x1, y1 = rect
    sx_, sy_, bu, bv, inner = q
    calm = not (bu or bv or inner)
    nx = 1 if calm else max(1, int(math.ceil((x1 - x0) / step[0 if (bu or inner) else 1] - 1e-6)))
    ny = 1 if calm else max(1, int(math.ceil((y1 - y0) / step[0 if (bv or inner) else 1] - 1e-6)))
    bm = k.bm
    top = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, C["water"])) for j in range(ny + 1)]
           for i in range(nx + 1)]
    fs = [bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1])) for i in range(nx) for j in range(ny)]
    ring = [top[i][0] for i in range(nx)] + [top[nx][j] for j in range(ny)] + \
        [top[i][ny] for i in range(nx, 0, -1)] + [top[0][j] for j in range(ny, 0, -1)]
    bot = [bm.verts.new((v.co.x, v.co.y, C["bed"])) for v in ring]
    sides = [bm.faces.new((ring[(i + 1) % len(ring)], ring[i], bot[i], bot[(i + 1) % len(ring)])) for i in range(len(ring))]
    bm.normal_update()
    k.project(fs, WATER)
    k.project(sides, VKI_STONE_BLOCK_IN)
    for col in top:
        for v in col:
            k.set_heat([v], 1.0 if calm else vki_dwf_lava_heat(v.co.x, v.co.y, q, C["rim"], wob))
    k.set_dark(bot, 0.65)


def vki_dwf_lava_crust(k, q, C, rnd, n0):
    """crust cooling against the banks of one quarter (the ASH slot: M_VKI_LavaCrust): one or two broad plates per bank,
    long with it, their outer part tucked under the rim (small scattered plates read as pebbles), sunk 12 mm into the
    lava, tops and bottoms staggered 1.5 mm (T5S); a plate in an inner corner, an island now and then in open lava.
    -> the plates laid"""
    sx, sy, bu, bv, inner = q
    rw = C["rim"]
    plates = []                                           # (u, v, ru, rv) in the quarter's frame
    for along_v, bank in ((True, bu), (False, bv)):
        if not bank:
            continue
        lo = (rw + 0.02 if (bv if along_v else bu) else 0.03)  # clear of a crossing rim
        spans = [(lo, 0.72)] if rnd.random() < 0.5 else [(lo, (lo + 0.72) / 2), ((lo + 0.72) / 2, 0.72)]
        for a, b in spans:
            rl = min(rnd.uniform(0.14, 0.24), (b - a) / 2.8)
            if rl < 0.06:
                continue
            c = rnd.uniform(a + 1.35 * rl, b - 1.35 * rl)
            off = rw + rnd.uniform(0.01, 0.04)                 # its centre just off the rim; the blob reaches 1.3 r,
            rs = rnd.uniform(0.08, 0.11)                       # so it stays short of the node line (u 0)
            plates.append((off, c, rs, rl) if along_v else (c, off, rl, rs))
    if inner:
        plates.append((rw + 0.03, rw + 0.03, 0.12, 0.12))
    if not (bu or bv or inner) and rnd.random() < 0.35:
        plates.append((rnd.uniform(0.25, 0.50), rnd.uniform(0.25, 0.50), 0.12, 0.09))
    n = n0
    for (u, v, ru, rv) in plates:
        dz = 0.0015 * n
        vs = vki_dpr_blob(k, (sx * u, sy * v), (ru, rv), C["water"] - 0.012 - dz, C["water"] + 0.010 + dz, VKI_ASH, ns=7,
                          wob=0.30, seed=70 + n)
        k.set_dark(vs, 0.30)
        n += 1
    return n - n0


def vki_dwf_lava(k, code):
    """a lava channel tile: the sewer channel's tile (vki_sew_channel) in dwarven stone -- rims 0.15 wide with dark
    dressed-stone kerbs 6 cm proud (scorched toward the lava), molten lava at -0.20 on a heat gradient (M_VKI_Lava:
    yellow-white down the channel's middle, deep red at the banks; vki_rim = 1 - heat, which Unity's shader takes
    from UV2 / Col.a at export), dark crust plates cooling along the banks; open below (vki_open_bottom); a light"""
    C = VKI_DWF_LAVA
    quads, waters = vki_sew_channel(k, code, fam="Dwarf", C=C, liquid="M_VKI_Lava", rim_top=None, volumes=False)
    k.set_dark(list(k.bm.verts), 0.45)                                  # the kerbs, scorched (the lava's light is strong)
    rnd = random.Random(vki_seed("Lava|" + code) % 100003)
    wob = (rnd.uniform(0.0, 6.3), rnd.uniform(0.0, 6.3), rnd.uniform(2.6, 3.8))
    qs = {(q[0], q[1]): q for q in vki_dwf_lava_quarters(code)}
    for (x0, y0, x1, y1) in waters:                                     # every liquid rect lies in one quarter
        sx = 1 if x0 + x1 > 0 else -1
        sy = 1 if y0 + y1 > 0 else -1
        vki_dwf_lava_pool(k, (x0, y0, x1, y1), qs[(sx, sy)], C, wob)
    n = 0
    for q in qs.values():
        n += vki_dwf_lava_crust(k, q, C, rnd, n)
    k.slot_mats[VKI_ASH] = "M_VKI_LavaCrust"
    qx = sum((q[0] + q[2]) / 2 for q in quads) / len(quads)
    qy = sum((q[1] + q[3]) / 2 for q in quads) / len(quads)
    k.meta.update(vki_water={"kind": "lava", "surface_z": C["water"]}, vki_trap={"kind": "lava", "damage": "burn"},
                  vki_open_bottom=C["bed"],
                  vki_lights=[vki_dpr_light("lava", (qx, qy, 0.30), 40.0, [1.0, 0.42, 0.12], 2.6, 0.3, shadows=0)],
                  vki_fx=[dict(fx="lava_glow", pos=[round(qx, 3), round(qy, 3), C["water"]], scale=0.6)])


# ---------------------------------------------------------------- props
def vki_dwf_block_mats(k):
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_DwarfBlock"
    k.slot_mats[VKI_CAP] = "M_VKI_DwarfCap"
    vki_dpr_gold_mats(k)


def vki_dwf_pillar(k, full):
    """a square dwarven pillar: a stepped base (0.96 / 0.86 sq), the shaft 0.72 sq with rounded arrises and a gold ring;
    Cut: the shaft cut at 1.00 (a pale section, like the walls' caps); Full: a three-stepped capital cut at 3.00"""
    vki_sto_block(k, -0.48, 0.48, 0.0, 0.16, -0.48, 0.48, bev=0.02, key="pb0")
    vki_sto_block(k, -0.43, 0.43, 0.16, 0.30, -0.43, 0.43, bev=0.02, key="pb1")
    zt = 2.50 if full else 0.96
    vki_sto_block(k, -0.36, 0.36, 0.30, zt, -0.36, 0.36, bev=0.05, key="psh", dark=0.02)
    gz = 1.92 if full else 0.74
    k.box((0.0, 0.0, gz), (0.735, 0.735, 0.05), VKI_DPR_GOLD, bevel=0.0)
    if full:
        vki_sto_block(k, -0.42, 0.42, 2.50, 2.66, -0.42, 0.42, bev=0.02, key="pc1")
        vki_sto_block(k, -0.48, 0.48, 2.66, 2.84, -0.48, 0.48, bev=0.02, key="pc2")
        vki_sto_block(k, -0.44, 0.44, 2.84, 3.00, -0.44, 0.44, bev=0.02, top=VKI_CAP, key="pc3")
    else:
        vki_sto_block(k, -0.36, 0.36, 0.96, 1.00, -0.36, 0.36, bev=0.01, top=VKI_CAP, key="pcut")
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_collider=[[0.0, 0.0, 1.5 if full else 0.5, 0.96, 0.96, 3.0 if full else 1.0]])


def vki_dwf_pillar_cut(k): vki_dwf_pillar(k, False)
def vki_dwf_pillar_full(k): vki_dwf_pillar(k, True)


def vki_dwf_statue(k):
    """a dwarf king in pale stone on a stepped plinth (1.10 sq): squat and broad under a cloak falling from his
    shoulders (gold clasps), a squared beard from the chin ending in two braids bound in gold rings over the gold belt,
    a crowned helm with cheek guards (gold crown points), pauldrons, both hands on the haft of a great hammer whose
    gold-banded head stands on the plinth; 2.2 m"""
    vki_sto_block(k, -0.55, 0.55, 0.0, 0.25, -0.55, 0.55, bev=0.03, key="skb0")
    vki_sto_block(k, -0.48, 0.48, 0.25, 0.45, -0.48, 0.48, bev=0.02, top=VKI_CAP, key="skb1")
    z0 = 0.45
    vki_home_lathe(k, [(0.34, z0 - 0.005), (0.36, z0 + 0.22), (0.33, z0 + 0.62), (0.0, z0 + 0.62)], c=(0.0, 0.02, 0.0),
                   segs=12, mi=VKI_CAP, sy=0.78)
    vki_home_lathe(k, [(0.33, z0 + 0.60), (0.41, z0 + 0.86), (0.43, z0 + 1.05), (0.35, z0 + 1.18), (0.16, z0 + 1.24),
                       (0.0, z0 + 1.25)], c=(0.0, 0.03, 0.0), segs=12, mi=VKI_CAP, sy=0.72)
    vki_home_hoop(k, (0.0, 0.02, z0 + 0.66), 0.33, 0.365, 0.08, segs=12, mi=VKI_DPR_GOLD, sy=0.8)
    # the cloak: from behind the shoulders to the plinth, flaring out and back (a frustum)
    cv = list(set(k.box((0.0, 0.38, z0 + 0.59), (0.92, 0.16, 1.18), VKI_CAP, bevel=0.0)))
    for v in cv:
        if v.co.z > z0 + 0.6:
            v.co.x *= 0.42 / 0.46
            v.co.y = 0.27 if v.co.y < 0.38 else 0.36
    k.bm.normal_update()
    k.project(vki_faces_of(cv), VKI_CAP)
    for s_ in (-1.0, 1.0):                                              # its gold clasps, at the shoulders' front
        _cyl(k, (s_ * 0.27, -0.17, z0 + 1.10), 0.045, 0.045, 0.03, 8, VKI_DPR_GOLD,
             rot=Matrix.Rotation(math.radians(-70.0), 4, "X"))
    hv = vki_home_ico(k, (0.0, 0.0, z0 + 1.40), 0.17, VKI_CAP, scale=(1.0, 1.0, 1.05), sub=2)
    k.project(vki_faces_of(hv), VKI_CAP)
    _cyl(k, (0.0, 0.0, z0 + 1.50), 0.185, 0.175, 0.12, 12, VKI_CAP)
    for i in range(6):                                                  # the crown's points, round the helm
        a = 2 * math.pi * i / 6 + math.pi / 6
        vs, _ = vki_prism(k, [(-0.035, z0 + 1.55), (0.035, z0 + 1.55), (0.0, z0 + 1.66)], -0.012, 0.012, VKI_DPR_GOLD,
                          axis="y", bevel=0.0)
        bmesh.ops.transform(k.bm, verts=vs, matrix=Matrix.Translation((0.17 * math.cos(a), 0.17 * math.sin(a), 0.0)) @
                            Matrix.Rotation(a + math.pi / 2, 4, "Z"))
    for s_ in (-1.0, 1.0):                                              # the helm's cheek guards
        x_ = sorted((s_ * 0.158, s_ * 0.192))
        vki_prism(k, [(-0.14, z0 + 1.47), (0.05, z0 + 1.47), (0.02, z0 + 1.29), (-0.11, z0 + 1.27)], x_[0], x_[1],
                  VKI_CAP, axis="x", bevel=0.006)
    # the beard: squared from the chin, then two braids down the chest, each bound in a gold ring above its tuft --
    # all above the hands, which hide what hangs lower from the game camera
    vki_prism(k, [(-0.14, z0 + 1.34), (0.14, z0 + 1.34), (0.12, z0 + 1.06), (-0.12, z0 + 1.06)], -0.36, -0.14, VKI_CAP,
              axis="y", bevel=0.01)
    for s_ in (-1.0, 1.0):
        x_ = s_ * 0.065
        for j in range(3):
            k.box((x_, -0.33, z0 + 1.035 - 0.05 * j), (0.066, 0.066 - 0.006 * (j % 2), 0.064), VKI_CAP,   # (T5S)
                  rot=(0.0, math.radians(28.0 * (1 if j % 2 else -1)), 0.0), bevel=0.008)
        _cyl(k, (x_, -0.33, z0 + 0.885), 0.040, 0.040, 0.040, 8, VKI_DPR_GOLD)
        vki_prism(k, [(x_ - 0.030, z0 + 0.868), (x_ + 0.030, z0 + 0.868), (x_ + 0.016, z0 + 0.83), (x_ - 0.016, z0 + 0.83)],
                  -0.35, -0.31, VKI_CAP, axis="y", bevel=0.0)
    for s_ in (-1.0, 1.0):
        pv = vki_home_ico(k, (s_ * 0.40, 0.03, z0 + 1.12), 0.12, VKI_CAP, scale=(1.1, 1.0, 0.75), sub=1)
        k.project(vki_faces_of(pv), VKI_CAP)
        vki_adv_rod(k, (s_ * 0.40, 0.0, z0 + 1.08), (s_ * 0.30, -0.26, z0 + 0.86), 0.12, VKI_CAP)
        vki_adv_rod(k, (s_ * 0.30, -0.26, z0 + 0.86), (s_ * 0.07, -0.42, z0 + 0.80), 0.10, VKI_CAP)
    k.box((0.0, -0.44, z0 + 0.80), (0.24, 0.12, 0.12), VKI_CAP, bevel=0.02)                       # hands
    k.box((0.0, -0.465, z0 + 0.52), (0.06, 0.06, 0.60), VKI_STONE_BLOCK_IN, bevel=0.0)             # the haft
    vki_sto_block(k, -0.27, 0.27, z0 + 0.01, z0 + 0.29, -0.62, -0.34, bev=0.02, key="skh")          # the hammer's head
    for x_ in (-0.19, 0.19):                                                                       # its gold bands
        k.box((x_, -0.48, z0 + 0.15), (0.045, 0.292, 0.292), VKI_DPR_GOLD, bevel=0.0)
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block", vki_collider=[[0.0, 0.0, 1.1, 1.10, 1.10, 2.2]],
                  vki_note="2.2 m tall: stand it against a north wall (it hides what is behind it)")


def vki_dwf_throne(k):
    """the king's throne on its own dais (2.40 x 2.00, two steps to 0.30): a massive stone seat with angular arms and
    gold caps, a tall back with a stepped crest and a gold rune disc; it faces local -y"""
    vki_sto_block(k, -1.20, 1.20, 0.0, 0.15, -1.00, 1.00, bev=0.02, top=VKI_CAP, key="td0")
    vki_sto_block(k, -0.95, 0.95, 0.15, 0.30, -0.55, 1.00, bev=0.02, top=VKI_CAP, key="td1")
    vki_sto_block(k, -0.45, 0.45, 0.30, 0.78, -0.30, 0.45, bev=0.02, top=VKI_CAP, key="tseat")
    for s in (-1.0, 1.0):
        xa, xb = sorted((s * 0.45, s * 0.66))
        vki_sto_block(k, xa, xb, 0.30, 1.08, -0.34, 0.45, bev=0.02, key="tarm%d" % int(s))
        k.box(((xa + xb) / 2, -0.26, 1.10), (0.23, 0.14, 0.05), VKI_DPR_GOLD, bevel=0.01)
    vki_sto_block(k, -0.55, 0.55, 0.78, 2.10, 0.30, 0.52, bev=0.02, key="tback")
    vki_prism(k, [(-0.55, 2.10), (0.55, 2.10), (0.30, 2.42), (-0.30, 2.42)], 0.30, 0.52, VKI_CAP, axis="y", bevel=0.01)
    _cyl(k, (0.0, 0.290, 1.72), 0.18, 0.18, 0.024, 12, VKI_DPR_GOLD, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "hero", use=[], vki_nav="block", vki_collider=[[0.0, 0.0, 0.5, 2.40, 2.00, 1.0]],
                  vki_note="the dais is part of the throne (a cave map has no dais floors)")


def vki_dwf_brazier(k):
    """a dwarven fire basin: a square stepped pedestal, a square gold bowl with coals, embers and fire; light"""
    vki_sto_block(k, -0.28, 0.28, 0.0, 0.12, -0.28, 0.28, bev=0.02, key="bz0")
    vki_sto_block(k, -0.20, 0.20, 0.12, 0.70, -0.20, 0.20, bev=0.03, key="bz1")
    vki_home_lathe(k, [(0.18, 0.695), (0.38, 0.84), (0.41, 0.92), (0.0, 0.92)], segs=4, mi=VKI_DPR_GOLD,
                   a0=math.pi / 4, smooth=False)
    rnd = random.Random(7)
    for i in range(8):
        a = 2 * math.pi * i / 8 + rnd.uniform(-0.2, 0.2); d = 0.18 * math.sqrt(rnd.random())
        vki_smy_lump(k, (math.cos(a) * d, math.sin(a) * d, 0.94), rnd.uniform(0.06, 0.08), rnd, COAL)
    vki_sto_embers(k, 0.0, 0.0, 0.98, 6, 0.14, 0.14, 97, core=0.24, rmin=0.035, rmax=0.05, hmax=0.9)
    for (x, y, h, r, tl, sp, bw) in ((0.0, 0.0, 0.42, 0.09, 0.0, 0.2, 0.03), (-0.08, 0.05, 0.28, 0.07, -0.18, -0.5, -0.03),
                                     (0.08, -0.04, 0.26, 0.065, 0.2, 0.7, 0.025)):
        vki_sto_flame(k, Vector((x, y, 1.0)), h, r, tl, sp, bw, flat=0.8)
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_lights=[vki_dpr_light("brazier", (0.0, -0.06, 1.55), VKI_DPR_BRAZIER_W, VKI_DPR_BRAZIER_COL, 7.0, 0.25)],
                  vki_fx=[dict(fx="brazier_fire", pos=[0.0, 0.0, 1.1], scale=1.3)])


def vki_dwf_forge(k):
    """a dwarven forge standing against a wall (its back at local +y 0.55): a stone hearth 1.60 x 1.00 x 0.85 with a
    glowing coal bed inside a kerb, two squat piers carrying a stepped stone hood with a gold band, the flue cut at
    2.60; the fire lights it"""
    vki_sto_block(k, -0.80, 0.80, 0.0, 0.85, -0.45, 0.55, bev=0.02, key="fh")
    for (a, b, c, d) in ((-0.80, 0.80, -0.45, -0.33), (-0.80, 0.80, 0.43, 0.55), (-0.80, -0.66, -0.33, 0.43),
                         (0.66, 0.80, -0.33, 0.43)):
        vki_sto_block(k, a, b, 0.85, 0.95, c, d, bev=0.01, top=VKI_CAP, key="fk%d%d" % (int(a * 10), int(c * 10)))
    rnd = random.Random(9)
    for i in range(12):
        x, y = rnd.uniform(-0.55, 0.55), rnd.uniform(-0.25, 0.35)
        vki_smy_lump(k, (x, y, 0.88), rnd.uniform(0.06, 0.09), rnd, COAL)
    vki_sto_embers(k, 0.0, 0.05, 0.92, 9, 0.45, 0.25, 71, core=0.30, rmin=0.04, rmax=0.06, hmax=0.95)
    for (x, h) in ((-0.2, 0.30), (0.15, 0.36)):
        vki_sto_flame(k, Vector((x, 0.05, 0.93)), h, 0.08, 0.0, 0.3, 0.02, flat=0.8)
    for s in (-1.0, 1.0):
        xa, xb = sorted((s * 0.62, s * 0.80))
        vki_sto_block(k, xa, xb, 0.95, 1.85, 0.15, 0.55, bev=0.02, key="fp%d" % int(s))
    vki_prism(k, [(-0.86, 1.85), (0.86, 1.85), (0.34, 2.36), (-0.34, 2.36)], 0.05, 0.55, VKI_STONE_BLOCK_IN, axis="y",
              bevel=0.01)
    k.box((0.0, 0.045, 1.95), (1.52, 0.012, 0.06), VKI_DPR_GOLD, bevel=0.0)
    vki_sto_block(k, -0.30, 0.30, 2.36, 2.60, 0.12, 0.55, bev=0.015, top=VKI_CAP, key="ff")
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.95, 0.0]], vki_nav="block",
                  vki_collider=[[0.0, 0.05, 0.5, 1.60, 1.00, 1.0]],
                  vki_lights=[vki_dpr_light("forge", (0.0, -0.10, 1.30), 220.0, [1.0, 0.50, 0.18], 6.0, 0.3)],
                  vki_fx=[dict(fx="forge_fire", pos=[0.0, 0.05, 1.0], scale=1.4)],
                  vki_place_rule="against a wall, local +y to the wall, hug off")


def vki_dwf_anvil(k):
    """a dwarven anvil on a dressed stone block: a squared body with a horn and a heel, a hammer lying on its face"""
    vki_sto_block(k, -0.24, 0.24, 0.0, 0.50, -0.20, 0.20, bev=0.02, key="ab")
    k.box((0.0, 0.0, 0.53), (0.36, 0.20, 0.06), IRON, bevel=0.01)
    k.box((0.0, 0.0, 0.60), (0.26, 0.14, 0.08), IRON, bevel=0.01)
    k.box((-0.02, 0.0, 0.69), (0.46, 0.20, 0.10), IRON, bevel=0.012)
    vki_prism(k, [(0.21, 0.64), (0.44, 0.71), (0.21, 0.74)], -0.07, 0.07, IRON, axis="y", bevel=0.0)
    k.box((-0.27, 0.0, 0.715), (0.06, 0.14, 0.05), IRON, bevel=0.0)
    vki_dpr_rod(k, (-0.10, -0.05, 0.755), (0.18, -0.13, 0.755), 0.03, WOOD)
    k.box((-0.12, -0.045, 0.768), (0.08, 0.05, 0.05), IRON, bevel=0.005)
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[[0.0, -0.55, 0.0]], vki_nav="block",
                  vki_collider=[[0.0, 0.0, 0.4, 0.50, 0.40, 0.8]])


def vki_dwf_bridge(k):
    """a narrow stone arch bridge 4.2 m long along local y over a chasm two cells wide (origin on the node between
    them): a deck 1.10 wide (top 0.10), parapets 0.35 tall, gold-capped end posts, and the arch below -- a segmental
    barrel whose underside rises from the abutments (-1.20) to the crown (-0.35); vki_bridge deck"""
    vki_sto_block(k, -0.55, 0.55, -0.12, 0.10, -2.10, 2.10, bev=0.02, top=VKI_CAP, key="bdk")
    for s in (-1.0, 1.0):
        xa, xb = sorted((s * 0.41, s * 0.55))
        vki_sto_block(k, xa, xb, 0.10, 0.45, -1.90, 1.90, bev=0.015, top=VKI_CAP, key="bpp%d" % int(s))
        for e in (-1.0, 1.0):
            ya, yb = sorted((e * 1.90, e * 2.10))
            vki_sto_block(k, xa - (0.03 if s < 0 else 0.0), xb + (0.03 if s > 0 else 0.0), 0.10, 0.62, ya, yb,
                          bev=0.015, key="bep%d%d" % (int(s), int(e)))
            k.box(((xa + xb) / 2, (ya + yb) / 2, 0.645), (0.18, 0.18, 0.05), VKI_DPR_GOLD, bevel=0.0)
    zi = lambda y: -0.35 - 0.85 * (y / 2.1) ** 2
    ys = [-2.1 + 4.2 * i / 8 for i in range(9)]
    for a, b in zip(ys[:-1], ys[1:]):
        vki_prism(k, [(a, zi(a)), (b, zi(b)), (b, -0.12), (a, -0.12)], -0.52, 0.52, VKI_STONE_BLOCK_IN, axis="x")
    for v in k.bm.verts:
        if v.co.z < -0.13:
            k.set_dark([v], 0.2 + 0.5 * vki_smoothstep(-0.2, -1.2, v.co.z))
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_collider=[[-0.48, 0.0, 0.3, 0.14, 4.2, 0.6], [0.48, 0.0, 0.3, 0.14, 4.2, 0.6]],
                  vki_bridge=[[-0.40, -2.3, 0.40, 2.3]],           # 0.2 m past the ends: off the chasm's soft rim
                  vki_place_rule="origin on the node between the two chasm cells it spans, rotation 0 (N-S) or 90")


def vki_dwf_runecircle(k):
    """a carved floor medallion 2.8 m across: a gold ring, eight gold spokes, four rune bars, a dark stone disc at the
    heart with a gold rune; a flat inlay (z 0-6 mm)"""
    vki_home_hoop(k, (0.0, 0.0, 0.0035), 1.30, 1.40, 0.006, segs=20, mi=VKI_DPR_GOLD)   # bottoms staggered (T5S)
    for i in range(8):
        a = 2 * math.pi * i / 8
        c = (math.cos(a) * 0.955, math.sin(a) * 0.955, 0.0032)
        k.box(c, (0.67, 0.05, 0.0044), VKI_DPR_GOLD, rot=(0.0, 0.0, a), bevel=0.0)
    for i in range(4):
        a = 2 * math.pi * i / 4 + math.pi / 8
        c = (math.cos(a) * 0.95, math.sin(a) * 0.95, 0.0040)
        k.box(c, (0.05, 0.26, 0.005), VKI_DPR_GOLD, rot=(0.0, 0.0, a), bevel=0.0)
    _cyl(k, (0.0, 0.0, 0.002), 0.52, 0.52, 0.004, 10, VKI_STONE_BLOCK_IN)
    _cyl(k, (0.0, 0.0, 0.0045), 0.16, 0.16, 0.003, 6, VKI_DPR_GOLD)
    vki_dwf_block_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_dwf_banner(k):
    """a clan banner (wall_hung, authored at its real height, back at local y 0) for a Full Dwarf wall, under its rune
    band: a gilded rod on two brackets at 2.08, a deep red cloth 1.00 wide falling to a point at 0.50, gold bands
    across its head and foot, a gold lozenge round a rune disc at its heart, a gold tassel at the point"""
    for x_ in (-0.42, 0.42):
        k.box((x_, -0.045, 2.08), (0.04, 0.09, 0.04), VKI_DPR_GOLD, bevel=0.0)                       # brackets
    _cyl(k, (0.0, -0.085, 2.08), 0.020, 0.020, 1.20, 8, VKI_DPR_GOLD, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    for x_ in (-0.625, 0.625):
        vki_home_ico(k, (x_, -0.085, 2.08), 0.035, VKI_DPR_GOLD, sub=1, smooth=False)                # finials
    vki_prism(k, [(-0.50, 2.07), (0.50, 2.07), (0.50, 0.70), (0.0, 0.50), (-0.50, 0.70)], -0.093, -0.081, CLOTH_A,
              axis="y", bevel=0.0)                                                                  # the cloth
    for zc in (1.93, 0.84):                                                                         # gold bands
        k.box((0.0, -0.096, zc), (0.98, 0.006, 0.055), VKI_DPR_GOLD, bevel=0.0)
    cz, r = 1.38, 0.25                                                                              # the lozenge
    for i, (a0, b0) in enumerate(((0.0, r), (r, 0.0), (0.0, -r), (-r, 0.0))):
        a1, b1 = ((r, 0.0), (0.0, -r), (-r, 0.0), (0.0, r))[i]
        e = 0.015 / math.hypot(a1 - a0, b1 - b0)       # run past the corners (under the half width: no end face in a
        #                                                 neighbour's side plane, T5S)
        yb = -0.097 - 0.0012 * (i % 2)                                   # alternate planes at the joints (T5S)
        vki_dpr_rod(k, (a0 - (a1 - a0) * e, yb, cz + b0 - (b1 - b0) * e), (a1 + (a1 - a0) * e, yb, cz + b1 + (b1 - b0) * e),
                    0.006, VKI_DPR_GOLD, d=0.036)                         # 6 mm thick (y), 36 mm wide
    _cyl(k, (0.0, -0.097, cz), 0.085, 0.085, 0.008, 12, VKI_DPR_GOLD, rot=Matrix.Rotation(math.pi / 2, 4, "X"))
    vki_home_ico(k, (0.0, -0.087, 0.47), 0.035, VKI_DPR_GOLD, scale=(1.0, 1.0, 1.4), sub=1, smooth=False)   # tassel
    k.slot_mats[CLOTH_A] = "M_VKI_BannerRed"
    vki_dpr_gold_mats(k)
    vki_home_meta(k, "wall_hung", "dressing", back=0.0, use=[], vki_nav="none", vki_mount_zmin=0.45,
                  vki_mount_zmax=2.12, vki_note="authored at its real height (placer z 0); a Full wall, under a Dwarf "
                                                "wall's rune band (2.20)")


# ---------------------------------------------------------------- specs
VKI_DWF_SPECS = [
    ("SM_VKI_Wall_Dwarf_Plain_150A_Full", vki_dwf_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Dwarf_Plain_150A_Cut", vki_dwf_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Dwarf_Plain_150B_Full", vki_dwf_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Dwarf_Plain_300_Full", vki_dwf_plain_300_full, "wall"),
    ("SM_VKI_Wall_Dwarf_Plain_300_Cut", vki_dwf_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Dwarf_Rake_150_L", vki_dwf_rake_l, "wall"),
    ("SM_VKI_Wall_Dwarf_Rake_150_R", vki_dwf_rake_r, "wall"),
    ("SM_VKI_Wall_Dwarf_Door_150_Full", vki_dwf_door_full, "wall"),
    ("SM_VKI_Wall_Dwarf_Door_150_Cut", vki_dwf_door_cut, "wall"),
    ("SM_VKI_Wall_Dwarf_DoorWide_300_Full", vki_dwf_door_wide_full, "wall"),
    ("SM_VKI_Wall_Dwarf_DoorWide_300_Cut", vki_dwf_door_wide_cut, "wall"),
    ("SM_VKI_Wall_Dwarf_Passage_150_Full", vki_dwf_passage, "wall"),
    ("SM_VKI_Post_Dwarf_Corner_Full", vki_dwf_post_corner_full, "wall"),
    ("SM_VKI_Post_Dwarf_Corner_Cut", vki_dwf_post_corner_cut, "wall"),
    ("SM_VKI_Post_Dwarf_Mid_Full", vki_dwf_post_mid_full, "wall"),
    ("SM_VKI_Post_Dwarf_Mid_Cut", vki_dwf_post_mid_cut, "wall"),
    ("SM_VKI_Leaf_DwarfGate_300", vki_dwf_leaf_gate, "wall"),
] + [("SM_VKI_Wall_Dwarf_Breach_%d_%s" % (int(L_ * 100), h_), (lambda k, L_=L_, h_=h_: vki_brk_breach(k, L_, h_, "Dwarf")),
      "wall") for L_ in (1.5, 3.0) for h_ in ("Full", "Cut")] + \
    [("SM_VKI_Ground_Lava_%s" % c_, (lambda k, c_=c_: vki_dwf_lava(k, c_)), "none") for c_ in vki_sew_channel_codes()] + [
    ("SM_VKI_Prop_Pillar_Dwarf_Cut", vki_dwf_pillar_cut, "prop"),
    ("SM_VKI_Prop_Pillar_Dwarf_Full", vki_dwf_pillar_full, "prop"),
    ("SM_VKI_Prop_Statue_DwarfKing", vki_dwf_statue, "prop"),
    ("SM_VKI_Prop_Throne_Dwarf", vki_dwf_throne, "prop"),
    ("SM_VKI_Prop_Brazier_Dwarf", vki_dwf_brazier, "prop"),
    ("SM_VKI_Prop_Forge_Dwarf", vki_dwf_forge, "prop"),
    ("SM_VKI_Prop_Anvil_Dwarf", vki_dwf_anvil, "prop"),
    ("SM_VKI_Prop_Bridge_Dwarf", vki_dwf_bridge, "prop"),
    ("SM_VKI_Prop_Banner_Dwarf", vki_dwf_banner, "prop"),
    ("SM_VKI_Overlay_RuneCircle", vki_dwf_runecircle, "none"),
]
VKI_DWF_NAMES = [n for n, _, _ in VKI_DWF_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_DWF_SPECS])
