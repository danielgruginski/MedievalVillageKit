# ===================== VKI FAM BOARD: the Board partition family (§2.2, §3.1, §3.2) -- 10 masters =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (its §10 amendments override earlier sections). Package "stone".
# Loaded by vki_ns() after vki_fam_timber / vki_fam_stone (uses vki_tim_member, vki_endgrain_fit, VKI_TIM_POST_FILL).
# Every top-level name starts with vki_/VKI_ (T18).
#
# Section (class P, T 0.30, H 3.0), piece-local, room on -Y:
#   body   vertical boards +-0.15 (WALL_A / WALL_B = BoardsV; a Plaster style gives lath-and-plaster partitions),
#          z -0.30 .. rail bottom, grid_cut 0.25 (the vertex-colour ramp), no wobble (A = 0), no base; the footing
#          band below z 0 is DRESS and the body's upward faces (always under a rail) oak
#   rails  hewn oak +-0.18 (CAP_HW P), WOOD with CAP tops: the Cut cap 0.90-1.00 (also on Full walls, where the
#          boards are nailed to it) and the Full top rail 2.88-3.00; rails meet at nodes in bevel V-joints
#   Door_150: oak frame (jambs x 0.19-0.33 / 1.17-1.31, lintel 2.20-2.38), DRESS threshold, 0.84 x 2.20 clear;
#          Cut: jambs 5 mm into one continuous cap block from the piece end to the opening, reveals WALL_A (§10.2)
#   Posts: oak Corner +-0.21 and Mid +-0.10 x +-0.21, ENDGRAIN tops (one padded log end, vki_endgrain_fit)
# Build: g["vki_ws_build"]("stone", VKI_BRD_NAMES); test: g["vki_test_pieces"](VKI_BRD_NAMES) -> {}.
import bpy, bmesh, math, json
from mathutils import Vector, Matrix

VKI_BRD_HW = 0.18                   # rails / frame half width (= CAP_HW, class P)
VKI_BRD_RAIL = (0.90, 1.00)         # the Cut cap (also on Full walls)
VKI_BRD_HEAD = (2.88, 3.00)         # the Full top rail (H - 0.12 .. H)
VKI_BRD_OPEN = (0.33, 1.17)
VKI_BRD_DOOR = dict(top=2.20, lintel=(2.20, 2.38), jamb=(0.19, 0.33), thr=0.03)
VKI_BRD_FOOT_TOP = -0.10            # footing under the door stops at the floor-slab bottom
VKI_BRD_TUCK = 0.005                # members butting into a rail / lintel run this far into it (T5S)
VKI_BRD_FOOT_DARK = 0.22


def vki_brd_member(k, x0, x1, z0, z1, top=None, bev=0.02):
    """an oak member through the partition (+-0.18), WOOD, optional CAP top faces (grain along the wall)"""
    return vki_tim_member(k, x0, x1, z0, z1, y0=-VKI_BRD_HW, y1=VKI_BRD_HW, top=top, bev=bev)


def vki_brd_body(k, x0, x1, z0, z1):
    return k.body_box(x0, x1, z0, z1)


def vki_brd_body_finish(k):
    """(1) footing band below the floor (body +-Y faces with every vertex at z <= 0) -> DRESS at t 1.5, darker (no
    pale board / plaster band under the floor in the section); (2) the body's upward faces (always under a rail or
    lintel) -> oak, so no board / plaster speck shows in the V-notch where two rails meet at a node"""
    vki_sto_reproject_body(k)                              # exact world-locked body UVs (T16; vki_fam_stone)
    k.bm.normal_update()
    for f in list(k.bm.faces):
        if f.material_index not in (VKI_WALL_A, VKI_WALL_B) or not all(v[k.body] for v in f.verts):
            continue
        if f.normal.z > 0.7:
            k.project([f], WOOD)
            continue
        if abs(f.normal.y) < 0.7 or max(v.co.z for v in f.verts) > 1e-6:
            continue
        k.project([f], DRESS, tile=1.5)
        for v in f.verts:
            k.set_dark([v], VKI_BRD_FOOT_DARK * vki_smoothstep(0.0, -0.15, v.co.z) + 0.08)


# ---------------------------------------------------------------- Plain (150A, 300), Full and Cut
def vki_brd_plain(k, L, height):
    full = height == "Full"
    tb = VKI_BRD_HEAD[0] if full else VKI_BRD_RAIL[0]
    vki_brd_body(k, 0.0, L, VKI_FOOT_Z, tb)
    if full:
        # the boards pass the mid-rail on Full walls: the rail is proud strips on both faces (+-0.15 .. +-0.18),
        # buried 5 mm in the boards, so no rail face shares a plane with the body
        for ys in (-1, 1):
            y0, y1 = sorted((ys * (k.T / 2 - VKI_BRD_TUCK), ys * VKI_BRD_HW))
            vki_tim_member(k, 0.0, L, *VKI_BRD_RAIL, y0=y0, y1=y1, top=VKI_CAP)
        vki_brd_member(k, 0.0, L, *VKI_BRD_HEAD, top=VKI_CAP)
    else:
        vki_brd_member(k, 0.0, L, *VKI_BRD_RAIL, top=VKI_CAP)
    vki_brd_body_finish(k)
    vki_wobble(k, L, "Board", "A", holes=[], top_body_fn=lambda x: tb)
    k.meta.update(vki_class="wall")


def vki_brd_plain_150a_full(k): vki_brd_plain(k, 1.5, "Full")
def vki_brd_plain_150a_cut(k): vki_brd_plain(k, 1.5, "Cut")
def vki_brd_plain_300_full(k): vki_brd_plain(k, 3.0, "Full")
def vki_brd_plain_300_cut(k): vki_brd_plain(k, 3.0, "Cut")


# ---------------------------------------------------------------- Door_150 (§3.2)
def vki_brd_door(k, height):
    """clear opening x 0.33-1.17 x 2.20, oak frame (jambs x 0.19-0.33 / 1.17-1.31, +-0.18), lintel 2.20-2.38 with
    boards above, DRESS threshold z 0-0.03 (|y| <= 0.18). Full: mid-rail strips 1 cm into the jambs. Cut: each jamb
    stops 5 mm inside one continuous cap block from the piece end to the opening (x 0-0.33 / 1.17-1.5, CAP top); the
    jambs' reveal faces are WALL_A (boards or the zone's plaster, a mid value, §10.2)"""
    L = 1.5
    full = height == "Full"
    x0, x1 = VKI_BRD_OPEN
    D = VKI_BRD_DOOR
    tb = VKI_BRD_HEAD[0] if full else VKI_BRD_RAIL[0]
    ja = D["jamb"][0]
    T2 = k.T / 2
    vki_brd_body(k, 0.0, ja, VKI_FOOT_Z, tb)                         # piers stop at the jambs' outer faces
    vki_brd_body(k, L - ja, L, VKI_FOOT_Z, tb)
    vki_brd_body(k, ja, L - ja, VKI_FOOT_Z, VKI_BRD_FOOT_TOP)          # footing under the frame and threshold
    vki_tim_member(k, x0, x1, 0.0, D["thr"], y0=-VKI_BRD_HW, y1=VKI_BRD_HW, mi=DRESS, bev=0.01)   # threshold
    jambs = []
    if full:
        for a, b in ((ja, x0), (x1, L - ja)):
            jambs.append(vki_brd_member(k, a, b, 0.0, D["top"], bev=0.015))
        for ys in (-1, 1):                                            # mid-rail strips, 1 cm into the jambs
            y0, y1 = sorted((ys * (T2 - VKI_BRD_TUCK), ys * VKI_BRD_HW))
            vki_tim_member(k, 0.0, ja + 0.01, *VKI_BRD_RAIL, y0=y0, y1=y1, top=VKI_CAP)
            vki_tim_member(k, L - ja - 0.01, L, *VKI_BRD_RAIL, y0=y0, y1=y1, top=VKI_CAP)
        vki_brd_member(k, ja, L - ja, *D["lintel"])
        vki_brd_body(k, ja, L - ja, D["lintel"][1], tb)
        vki_brd_member(k, 0.0, L, *VKI_BRD_HEAD, top=VKI_CAP)
    else:
        for a, b in ((ja, x0), (x1, L - ja)):
            jambs.append(vki_brd_member(k, a, b, 0.0, VKI_BRD_RAIL[0] + VKI_BRD_TUCK, bev=0.015))
        for a, b in ((0.0, x0), (x1, L)):
            vki_brd_member(k, a, b, *VKI_BRD_RAIL, top=VKI_CAP)
        k.bm.normal_update()
        for vs_, sgn in zip(jambs, (1, -1)):
            fs = [f for f in vki_faces_of(vs_) if f.normal.x * sgn > 0.6 and f.normal.z < 0.65]
            k.project(fs, VKI_WALL_A)
    vki_brd_body_finish(k)
    vki_wobble(k, L, "Board", "A", holes=[(ja, 0.0, L - ja, D["lintel"][1] if full else VKI_BRD_RAIL[1])],
               top_body_fn=lambda x: tb)
    k.meta.update(vki_nav="door", vki_nav_open=[x0, x1])
    k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": D["top"] if full else 1.0},
                  vki_trigger=[0.75, -0.65, 1.0, 0.9, 0.8, 2.0], vki_leaf_socket=[x0, -T2 + 0.05, 0.0],
                  vki_leaf_open_deg=90, vki_leaf="SM_VKI_Leaf_Plank_" + height, vki_spawn_local=[0.75, -1.60],
                  vki_prompt_local=[0.75, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])


def vki_brd_door_full(k): vki_brd_door(k, "Full")
def vki_brd_door_cut(k): vki_brd_door(k, "Cut")


# ---------------------------------------------------------------- posts (§2.3)
def vki_brd_post(k, kind, height):
    """oak post centred on its node (class P), z -0.30 .. wall top + 0.04, bevel 0.02; Corner +-0.21 square, Mid
    +-0.10 along the wall x +-0.21 across; the top shows one centred, padded log end (vki_endgrain_fit, §10.2)"""
    k.set_family("Board")
    top = (VKI_H_FULL["Board"] if height == "Full" else VKI_CUT_H) + VKI_POST_TOP
    ax, ay = (VKI_POST_HW["P"], VKI_POST_HW["P"]) if kind == "Corner" else VKI_MID_HW["P"]
    c = (0.0, 0.0, (VKI_POST_Z0 + top) / 2); sz = (2 * ax, 2 * ay, top - VKI_POST_Z0)
    vs = list(set(k.box(c, sz, WOOD, bevel=VKI_POST_BEVEL)))
    k.bm.normal_update()
    tops = [f for f in vki_faces_of(vs) if f.normal.z > 0.65]
    vki_endgrain_fit(k, tops, (0.0, 0.0, top), VKI_TIM_X, VKI_TIM_Y, max(ax, ay), fill=VKI_TIM_POST_FILL)
    other = "Cut" if height == "Full" else "Full"
    rule = {"Corner": "L/T/X junction of Board partitions (required, T12); a P partition teeing into an O wall takes "
                      "the O family's Corner post (§2.3)",
            "Mid": "height step / free end (required) | rhythm at even nodes (Board default; skipped where a "
                   "wall-backed / wall-hung prop or a stair spans the node)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": f"SM_VKI_Post_Board_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_brd_post_corner_full(k): vki_brd_post(k, "Corner", "Full")
def vki_brd_post_corner_cut(k): vki_brd_post(k, "Corner", "Cut")
def vki_brd_post_mid_full(k): vki_brd_post(k, "Mid", "Full")
def vki_brd_post_mid_cut(k): vki_brd_post(k, "Mid", "Cut")


VKI_BRD_SPECS = [
    ("SM_VKI_Wall_Board_Plain_150A_Full", vki_brd_plain_150a_full),
    ("SM_VKI_Wall_Board_Plain_150A_Cut", vki_brd_plain_150a_cut),
    ("SM_VKI_Wall_Board_Plain_300_Full", vki_brd_plain_300_full),
    ("SM_VKI_Wall_Board_Plain_300_Cut", vki_brd_plain_300_cut),
    ("SM_VKI_Wall_Board_Door_150_Full", vki_brd_door_full),
    ("SM_VKI_Wall_Board_Door_150_Cut", vki_brd_door_cut),
    ("SM_VKI_Post_Board_Corner_Full", vki_brd_post_corner_full),
    ("SM_VKI_Post_Board_Corner_Cut", vki_brd_post_corner_cut),
    ("SM_VKI_Post_Board_Mid_Full", vki_brd_post_mid_full),
    ("SM_VKI_Post_Board_Mid_Cut", vki_brd_post_mid_cut),
]
VKI_BRD_NAMES = [n for n, _ in VKI_BRD_SPECS]
vki_register([(n, fn, {"grime": "wall"}, "stone") for n, fn in VKI_BRD_SPECS])
