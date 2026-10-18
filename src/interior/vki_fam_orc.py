# ===================== VKI FAM ORC: the orcs' log halls (warcamp interiors, 2026-10-18) -- 21 masters =====================
# For MedievalSetting's orc chapter (the warlord's hold and the camps' halls). Package "adventure". Loaded by vki_ns()
# after vki_fam_dwarf; at build time it calls vki_fam_timber's vki_tim_member / vki_endgrain_fit, vki_fam_stone's
# vki_sto_reproject_body / vki_leaf_tall, the chapel's vki_chp_cyl, the lair's hide (vki_lair_hide) and the dungeon's
# skull (vki_dun_skull) and bone material. Every top-level name starts with vki_/VKI_ (T18).
#
# Section (class O, T 0.50, H 3.0), piece-local, room on -Y:
#   body   rough logs standing side by side, bark on, mud in the gaps (WALL_A / WALL_B = OrcLogs, T_VKI_OrcLogs:
#          vki_tex.vki_gen_orclogs), z -0.30 .. rail / plate bottom, grid 0.25, wobble 0.012; darkened below the floor
#   rail   a split-log rail 0.86-1.00 (WOOD "Dark", CAP top = WoodDark): the Cut cap, full depth +-0.28; on Full walls
#          proud strips on both faces (the logs pass behind it), 5 mm into the body; rope lashings (BURLAP) round it at
#          x 0.375 + 0.75 i, clear of the node zones
#   plate  the Full wall plate 2.84-3.00, a log beam +-0.28 (CAP top)
#   B      Plain_150B_Full: a hide stretched on a pole hung across face A (1.18-2.52), a skull on a peg over it
#   Window_150: an unglazed opening x 0.45-1.05, sill = the rail (1.00) to a log lintel at 2.10, split-log jambs,
#          three stick bars, a hide rolled up under the lintel; the Timber window spot. Cut: the rail notched 4 cm
#   Door_150: 0.84 x 2.20 between split-log jambs (x 0.19-0.33 / 1.17-1.31) under a log lintel 2.20-2.42 with a skull on
#          it, a log threshold; Leaf_Orc_Full / _Cut (dark planks, iron straps, spikes). Cut: the rail wraps the jambs
#   DoorWide_300: the hall's gate, 1.80 x 2.40 (jambs x 0.44-0.60 / 2.40-2.56), a heavy lintel 2.40-2.64 with a skull and
#          two tusks over it; Leaf_OrcWide_Full / _Cut _L / _R
#   Posts: Corner = a round log r 0.30 (12 sides) with a rope band at the rail, Mid = a squared log +-0.12 x +-0.31;
#          end-grain tops (vki_endgrain_fit)
# Build: g["vki_rebuild"](VKI_ORC_FAM_NAMES); test: g["vki_test_pieces"](VKI_ORC_FAM_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_ORC_HW = 0.28                       # rail / plate / frame half width (CAP_HW, class O)
VKI_ORC_RAIL = (0.86, 1.00)             # the Cut cap (also on Full walls, as proud strips)
VKI_ORC_PLATE = (2.84, 3.00)            # the Full wall plate (H - 0.16 .. H)
VKI_ORC_TUCK = 0.005                    # strips / members run this far into what they butt against (T5S)
VKI_ORC_DOOR = dict(open=(0.33, 1.17), jamb=0.19, top=2.20, lintel=(2.20, 2.42), thr=0.03)
VKI_ORC_WIDE = dict(open=(0.60, 2.40), jamb=0.44, top=2.40, lintel=(2.40, 2.64), thr=0.03)
VKI_ORC_WIN = dict(open=(0.45, 1.05), jamb=0.33, head=2.10, lintel=(2.10, 2.26))
VKI_ORC_CHAR = 0.30                     # vertex darkness of the raw timber (WOOD "Dark")
VKI_ORC_FOOT_DARK = 0.25


def vki_orc_mats(k):
    k.slot_mats[WOOD] = "Dark"
    vki_lair_hide_mats(k)                                   # HIDE -> the sewn M_VKI_Hide
    vki_dun_bone_mats(k)                                    # WAX -> bone


def vki_orc_member(k, x0, x1, z0, z1, y0=-VKI_ORC_HW, y1=VKI_ORC_HW, top=VKI_CAP, bev=0.025):
    """a raw timber (WOOD, darkened), CAP top faces unless top=None"""
    vs = vki_tim_member(k, x0, x1, z0, z1, y0=y0, y1=y1, mi=WOOD, top=top, bev=bev)
    k.set_dark(vs, VKI_ORC_CHAR)
    return vs


def vki_orc_rail(k, x0, x1, full):
    """the split-log rail 0.86-1.00: full depth on Cut walls; on Full walls two proud strips (+-0.245 .. +-0.28)"""
    if not full:
        return vki_orc_member(k, x0, x1, *VKI_ORC_RAIL)
    for ys in (-1, 1):
        y0, y1 = sorted((ys * (k.T / 2 - VKI_ORC_TUCK), ys * VKI_ORC_HW))
        vki_orc_member(k, x0, x1, *VKI_ORC_RAIL, y0=y0, y1=y1, bev=0.015)


def vki_orc_lashings(k, xs):
    """rope bound round the rail at each x (BURLAP, 5 cm wide, 1 cm proud of its faces; its top under the rail's, so
    a Cut wall stays under 1.0, T1)"""
    for x in xs:
        vs = list(set(k.box((x, 0.0, 0.9225), (0.05, 2 * VKI_ORC_HW + 0.02, 0.145), BURLAP, bevel=0.008)))   # <= 0.995
        k.set_dark(vs, 0.25)


def vki_orc_lash_xs(L, keep=lambda x: True):
    return [0.375 + 0.75 * i for i in range(int(round(L / 0.75))) if keep(0.375 + 0.75 * i)]


def vki_orc_body_finish(k):
    """exact world-locked body UVs; the logs below the floor darken (no pale band in the section)"""
    vki_sto_reproject_body(k)
    k.bm.normal_update()
    for f in list(k.bm.faces):
        if f.material_index not in (VKI_WALL_A, VKI_WALL_B) or not all(v[k.body] for v in f.verts):
            continue
        if abs(f.normal.y) < 0.7 or max(v.co.z for v in f.verts) > 1e-6:
            continue
        for v in f.verts:
            k.set_dark([v], VKI_ORC_FOOT_DARK * vki_smoothstep(0.0, -0.15, v.co.z) + 0.08)


def vki_orc_skull(k, x, z, y=-0.335, s=1.0, yaw=0.0):
    """a skull hung on a peg in face A (the peg a dark stub into the wall)"""
    k.box((x, (y - 0.25) / 2 + 0.02, z + 0.02), (0.03, abs(y + 0.25) + 0.04, 0.03), WOOD, bevel=0.0)
    vki_dun_skull(k, (x, y, z), s=s, yaw=yaw)


# ---------------------------------------------------------------- Plain (150A, 150B, 300), Full and Cut
def vki_orc_plain(k, L, height, variant="A"):
    full = height == "Full"
    tb = VKI_ORC_PLATE[0] if full else VKI_ORC_RAIL[0]
    k.body_box(0.0, L, VKI_FOOT_Z, tb)
    vki_orc_rail(k, 0.0, L, full)
    if full:
        vki_orc_member(k, 0.0, L, *VKI_ORC_PLATE)
    vki_orc_lashings(k, vki_orc_lash_xs(L))
    holes = []
    if variant == "B":                                      # a hide stretched on a pole across face A, a skull over it
        y = -k.T / 2 - 0.025
        vki_lair_hide(k, [(0.44, y, 2.48), (1.06, y, 2.48), (1.04, y, 1.18), (0.46, y, 1.18)], dark=0.18, seed=17,
                      nu=3, nv=4, t=0.012, sagv=(0.0, -0.02, 0.0), ragged=0.06, mi=HIDE)
        vki_chp_cyl(k, (0.75, y - 0.012, 2.50), 0.022, 0.022, 0.78, 6, WOOD, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
        for x in (0.42, 1.08):                                                          # the pole's pegs
            k.box((x, -k.T / 2 - 0.01, 2.50), (0.03, 0.06, 0.03), WOOD, bevel=0.0)
        vki_orc_skull(k, 0.75, 2.68)
        holes = [(0.38, 1.10, 1.12, 2.80)]
    vki_orc_body_finish(k)
    vki_wobble(k, L, "Orc", "A", holes=holes, top_body_fn=lambda x: tb)
    vki_orc_mats(k)
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to="SM_VKI_Wall_Orc_Plain_150A_Cut")


def vki_orc_plain_150a_full(k): vki_orc_plain(k, 1.5, "Full")
def vki_orc_plain_150a_cut(k): vki_orc_plain(k, 1.5, "Cut")
def vki_orc_plain_150b_full(k): vki_orc_plain(k, 1.5, "Full", "B")
def vki_orc_plain_300_full(k): vki_orc_plain(k, 3.0, "Full")
def vki_orc_plain_300_cut(k): vki_orc_plain(k, 3.0, "Cut")


# ---------------------------------------------------------------- Window_150
def vki_orc_window(k, height):
    """Full: an unglazed opening x 0.45-1.05 from the rail (the sill, full depth) to a log lintel at 2.10 between
    split-log jambs, three stick bars, a hide rolled up under the lintel, the Timber window spot through it. Cut: the
    plain Cut wall with its rail notched 4 cm down where the opening was"""
    L = 1.5
    W = VKI_ORC_WIN
    full = height == "Full"
    x0, x1 = W["open"]; ja = W["jamb"]
    tb = VKI_ORC_PLATE[0] if full else VKI_ORC_RAIL[0]
    k.body_box(0.0, ja, VKI_FOOT_Z, tb)                                         # piers
    k.body_box(L - ja, L, VKI_FOOT_Z, tb)
    k.body_box(ja, L - ja, VKI_FOOT_Z, VKI_ORC_RAIL[0])                         # under the sill (Full and Cut alike, T2)
    if full:
        vki_orc_rail(k, 0.0, ja + 0.01, True)                                   # the strips run 1 cm into the sill
        vki_orc_rail(k, L - ja - 0.01, L, True)
        vki_orc_member(k, ja, L - ja, *VKI_ORC_RAIL, bev=0.02)                  # the sill (the rail, full depth)
        for a, b in ((ja, x0), (x1, L - ja)):                                   # jambs, into sill and lintel
            vki_orc_member(k, a, b, VKI_ORC_RAIL[1] - VKI_ORC_TUCK, W["head"] + VKI_ORC_TUCK, top=None, bev=0.02)
        vki_orc_member(k, ja, L - ja, *W["lintel"], top=None, bev=0.025)       # lintel
        k.body_box(ja, L - ja, W["lintel"][1], tb)
        vki_orc_member(k, 0.0, L, *VKI_ORC_PLATE)
        for x in (0.60, 0.75, 0.90):                                            # stick bars
            vs = vki_chp_cyl(k, (x, 0.02, (VKI_ORC_RAIL[1] + W["head"]) / 2), 0.022, 0.022,
                             W["head"] - VKI_ORC_RAIL[1] + 0.02, 6, WOOD)
            k.set_dark(vs, VKI_ORC_CHAR)
        vki_chp_cyl(k, (0.75, -0.17, W["head"] - 0.065), 0.055, 0.055, x1 - x0 - 0.02, 8, HIDE,
                    rot=Matrix.Rotation(math.pi / 2, 4, "Y"))                    # the hide rolled up
        holes = [(ja, VKI_ORC_RAIL[0], L - ja, W["lintel"][1] + 0.05)]
        S = VKI_TIM_WIN_SPOT
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": VKI_ORC_RAIL[1], "z1": W["head"], "head": "flat",
                                   "unglazed": 1},
                      vki_lights=[dict(type="SPOT", role="window", pos=list(S["pos"]), aim=list(S["aim"]),
                                       cone=S["cone"], blend=S["blend"], radius=S["radius"], w_day=S["w_day"],
                                       w_night=S["w_night"], color_day=[.82, .88, 1.0], color_night=[.62, .70, 1.0],
                                       shadows=1)])
    else:
        vki_orc_member(k, 0.0, ja, *VKI_ORC_RAIL)                               # the rail, notched down 4 cm
        vki_orc_member(k, L - ja, L, *VKI_ORC_RAIL)                             # where the opening was
        vki_orc_member(k, ja, L - ja, VKI_ORC_RAIL[0], VKI_ORC_RAIL[1] - 0.04, bev=0.02)
        holes = []
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": VKI_ORC_RAIL[1], "z1": W["head"], "cut": 1},
                      vki_light_pool=[0.75, -1.20, 0.0])
    vki_orc_body_finish(k)
    vki_wobble(k, L, "Orc", "A", holes=holes, top_body_fn=lambda x: tb)
    vki_orc_mats(k)
    k.meta.update(vki_class="wall")


def vki_orc_window_full(k): vki_orc_window(k, "Full")
def vki_orc_window_cut(k): vki_orc_window(k, "Cut")


# ---------------------------------------------------------------- Door_150, DoorWide_300
def vki_orc_door(k, height, wide=False):
    """split-log jambs on a log threshold, a log lintel with a skull (and, on the wide gate, two tusks); Cut: the
    lower metre, the rail wrapping the jambs; leaves Leaf_Orc / Leaf_OrcWide at the sockets"""
    D = VKI_ORC_WIDE if wide else VKI_ORC_DOOR
    L = 3.0 if wide else 1.5
    full = height == "Full"
    x0, x1 = D["open"]; ja = D["jamb"]
    tb = VKI_ORC_PLATE[0] if full else VKI_ORC_RAIL[0]
    T2 = k.T / 2
    k.body_box(0.0, ja, VKI_FOOT_Z, tb)                                         # piers stop at the jambs
    k.body_box(L - ja, L, VKI_FOOT_Z, tb)
    k.body_box(ja, L - ja, VKI_FOOT_Z, -0.10)                                    # footing under frame and threshold
    vki_orc_member(k, x0, x1, 0.0, D["thr"], top=None, bev=0.01)                 # the log threshold
    if full:
        for a, b in ((ja, x0), (x1, L - ja)):
            vki_orc_member(k, a, b, 0.0, D["top"] + VKI_ORC_TUCK, top=None, bev=0.02)
        vki_orc_rail(k, 0.0, ja + 0.01, True)                                    # strips 1 cm into the jambs
        vki_orc_rail(k, L - ja - 0.01, L, True)
        vki_orc_member(k, ja, L - ja, *D["lintel"], top=None, bev=0.03)          # the lintel
        k.body_box(ja, L - ja, D["lintel"][1], tb)
        vki_orc_member(k, 0.0, L, *VKI_ORC_PLATE)
        vki_orc_skull(k, L / 2, D["lintel"][1] + 0.12, s=1.15 if wide else 1.0)
        if wide:                                                                 # two tusks crossing over the skull
            for s in (-1, 1):
                vki_orc_tusk(k, (L / 2 + s * 0.32, -0.31, D["lintel"][1] + 0.04), (-s * 0.70, -0.10, 0.55), (0, -1, 0),
                             0.36, 0.045, 610 + s)
        holes = [(ja, 0.0, L - ja, D["lintel"][1] + 0.05)]
        z1 = D["top"]
    else:
        for a, b in ((ja, x0), (x1, L - ja)):
            vki_orc_member(k, a, b, 0.0, VKI_ORC_RAIL[0] + VKI_ORC_TUCK, top=None, bev=0.02)
        for a, b in ((0.0, x0), (x1, L)):
            vki_orc_member(k, a, b, *VKI_ORC_RAIL)                                # the rail wraps the jambs
        holes = [(ja, 0.0, L - ja, VKI_ORC_RAIL[1])]
        z1 = 1.0
    vki_orc_lashings(k, vki_orc_lash_xs(L, lambda x: x < ja - 0.04 or x > L - ja + 0.04))
    vki_orc_body_finish(k)
    vki_wobble(k, L, "Orc", "A", holes=holes, top_body_fn=lambda x: tb)
    vki_orc_mats(k)
    k.meta.update(vki_nav="door", vki_nav_open=[x0, x1])
    col = [[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]]
    if wide:
        k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": z1, "head": "flat"},
                      vki_trigger=[1.5, -0.65, 1.0, 1.9, 0.8, 2.0],
                      vki_leaf_socket=[[x0, -T2 + 0.05, 0.0], [x1, -T2 + 0.05, 0.0]], vki_leaf_open_deg=90,
                      vki_leaf=["SM_VKI_Leaf_OrcWide_%s_L" % height, "SM_VKI_Leaf_OrcWide_%s_R" % height],
                      vki_leaf_note="L at vki_leaf_socket[0] (extends +X), R at [1] (extends -X), both with the "
                                    "door's rotation",
                      vki_spawn_local=[1.5, -1.60], vki_prompt_local=[1.5, -0.30, 1.40], vki_collider=col)
    else:
        k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": z1},
                      vki_trigger=[0.75, -0.65, 1.0, 0.9, 0.8, 2.0], vki_leaf_socket=[x0, -T2 + 0.05, 0.0],
                      vki_leaf_open_deg=90, vki_leaf="SM_VKI_Leaf_Orc_" + height, vki_spawn_local=[0.75, -1.60],
                      vki_prompt_local=[0.75, -0.30, 1.40], vki_collider=col)


def vki_orc_door_full(k): vki_orc_door(k, "Full")
def vki_orc_door_cut(k): vki_orc_door(k, "Cut")
def vki_orc_doorwide_full(k): vki_orc_door(k, "Full", wide=True)
def vki_orc_doorwide_cut(k): vki_orc_door(k, "Cut", wide=True)


# ---------------------------------------------------------------- leaves
def vki_orc_leaf(k, side, W, h, fits):
    """an orc door leaf: vki_leaf_tall's planks (flat top, h over the threshold) darkened, its straps and ring, and
    iron spikes on the room-side straps"""
    z0 = VKI_STO_DOOR["thr"] + 0.005
    vki_leaf_tall(k, side, W, lambda xl: z0 + h, fits)
    sg = 1.0 if side == "L" else -1.0
    y0 = VKI_LEAF_Y0
    for z in VKI_LEAF_TALL_STRAPS:
        if z > z0 + h - 0.08:
            continue
        for x in (0.30, W - 0.20):
            sv = vki_chp_cyl(k, (sg * x, y0 - 0.006 - 0.03, z), 0.018, 0.003, 0.06, 4, IRON, smooth=False,
                             rot=Matrix.Rotation(math.pi / 2, 4, "X"))           # a spike pointing into the room
    for v in k.bm.verts:
        k.set_dark([v], 0.25)
    k.slot_mats[WOOD] = "Dark"


def vki_orc_leaf_full(k): vki_orc_leaf(k, "L", 0.83, 2.16, "SM_VKI_Wall_Orc_Door_150_Full at its vki_leaf_socket, same rotation")
def vki_orc_leaf_cut(k): vki_orc_leaf(k, "L", 0.83, 0.95, "SM_VKI_Wall_Orc_Door_150_Cut at its vki_leaf_socket, same rotation")
def vki_orc_leafwide_full_l(k): vki_orc_leaf(k, "L", 0.89, 2.355, "SM_VKI_Wall_Orc_DoorWide_300_Full at vki_leaf_socket[0], same rotation")
def vki_orc_leafwide_full_r(k): vki_orc_leaf(k, "R", 0.89, 2.355, "SM_VKI_Wall_Orc_DoorWide_300_Full at vki_leaf_socket[1], same rotation")
def vki_orc_leafwide_cut_l(k): vki_orc_leaf(k, "L", 0.89, 0.95, "SM_VKI_Wall_Orc_DoorWide_300_Cut at vki_leaf_socket[0], same rotation")
def vki_orc_leafwide_cut_r(k): vki_orc_leaf(k, "R", 0.89, 0.95, "SM_VKI_Wall_Orc_DoorWide_300_Cut at vki_leaf_socket[1], same rotation")


# ---------------------------------------------------------------- posts (§2.3)
def vki_orc_post(k, kind, height):
    """Corner: a round log r 0.30 (12 sides) on its node; Mid: a squared log +-0.12 along the wall x +-0.31 across;
    z -0.30 .. wall top + 0.04, a rope band round it at the rail, an end-grain top"""
    k.set_family("Orc")
    top = (VKI_H_FULL["Orc"] if height == "Full" else VKI_CUT_H) + VKI_POST_TOP
    zc = (VKI_POST_Z0 + top) / 2
    if kind == "Corner":
        r = VKI_POST_HW["O"] - 0.01
        vs = vki_chp_cyl(k, (0.0, 0.0, zc), r, r, top - VKI_POST_Z0, 12, WOOD)
        vki_home_hoop(k, (0.0, 0.0, 0.93), r - 0.02, r + 0.01, 0.10, segs=12, mi=BURLAP)
        half = r
    else:
        ax, ay = VKI_MID_HW["O"]
        vs = list(set(k.box((0.0, 0.0, zc), (2 * ax, 2 * ay, top - VKI_POST_Z0), WOOD, bevel=VKI_POST_BEVEL)))
        k.box((0.0, 0.0, 0.93), (2 * ax - 0.01, 2 * ay - 0.004, 0.10), BURLAP, bevel=0.0)
        half = max(ax, ay)
    k.set_dark(vs, VKI_ORC_CHAR)
    k.bm.normal_update()
    tops = [f for f in vki_faces_of(vs) if f.is_valid and f.normal.z > 0.65]
    vki_endgrain_fit(k, tops, (0.0, 0.0, top), VKI_TIM_X, VKI_TIM_Y, half, fill=VKI_TIM_POST_FILL)
    k.slot_mats[WOOD] = "Dark"
    other = "Cut" if height == "Full" else "Full"
    rule = {"Corner": "L/T/X junction of Orc walls (required, T12)",
            "Mid": "height step / free end (required) | rhythm at even nodes (Orc default)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": f"SM_VKI_Post_Orc_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * half, 2 * half, 2.2]])


def vki_orc_post_corner_full(k): vki_orc_post(k, "Corner", "Full")
def vki_orc_post_corner_cut(k): vki_orc_post(k, "Corner", "Cut")
def vki_orc_post_mid_full(k): vki_orc_post(k, "Mid", "Full")
def vki_orc_post_mid_cut(k): vki_orc_post(k, "Mid", "Cut")


VKI_ORC_FAM_SPECS = [
    ("SM_VKI_Wall_Orc_Plain_150A_Full", vki_orc_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Orc_Plain_150A_Cut", vki_orc_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Orc_Plain_150B_Full", vki_orc_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Orc_Plain_300_Full", vki_orc_plain_300_full, "wall"),
    ("SM_VKI_Wall_Orc_Plain_300_Cut", vki_orc_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Orc_Window_150_Full", vki_orc_window_full, "wall"),
    ("SM_VKI_Wall_Orc_Window_150_Cut", vki_orc_window_cut, "wall"),
    ("SM_VKI_Wall_Orc_Door_150_Full", vki_orc_door_full, "wall"),
    ("SM_VKI_Wall_Orc_Door_150_Cut", vki_orc_door_cut, "wall"),
    ("SM_VKI_Wall_Orc_DoorWide_300_Full", vki_orc_doorwide_full, "wall"),
    ("SM_VKI_Wall_Orc_DoorWide_300_Cut", vki_orc_doorwide_cut, "wall"),
    ("SM_VKI_Post_Orc_Corner_Full", vki_orc_post_corner_full, "wall"),
    ("SM_VKI_Post_Orc_Corner_Cut", vki_orc_post_corner_cut, "wall"),
    ("SM_VKI_Post_Orc_Mid_Full", vki_orc_post_mid_full, "wall"),
    ("SM_VKI_Post_Orc_Mid_Cut", vki_orc_post_mid_cut, "wall"),
    ("SM_VKI_Leaf_Orc_Full", vki_orc_leaf_full, "prop"),
    ("SM_VKI_Leaf_Orc_Cut", vki_orc_leaf_cut, "prop"),
    ("SM_VKI_Leaf_OrcWide_Full_L", vki_orc_leafwide_full_l, "prop"),
    ("SM_VKI_Leaf_OrcWide_Full_R", vki_orc_leafwide_full_r, "prop"),
    ("SM_VKI_Leaf_OrcWide_Cut_L", vki_orc_leafwide_cut_l, "prop"),
    ("SM_VKI_Leaf_OrcWide_Cut_R", vki_orc_leafwide_cut_r, "prop"),
]
VKI_ORC_FAM_NAMES = [n for n, _, _ in VKI_ORC_FAM_SPECS]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_ORC_FAM_SPECS])
