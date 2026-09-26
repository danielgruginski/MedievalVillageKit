# ===================== VKI FLOORS: floors, sill, door leaves, apron and overlays (§3.3, §5.4) =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md. Loaded by vki_ns() (VKI_TEXTS, after vki_fam_timber, whose
# geometry helpers vki_cut / vki_prism it uses). Every top-level name starts with vki_/VKI_ (T18).
#   Floor_150_Q00/Q10/Q01/Q11  [0,1.5]^2 slab z -0.10..0, FLOOR, UV offset (i mod 2, j mod 2) * 0.5 of its node
#   Floor_300 / Floor_600      even nodes only (x, y multiples of 3.0)
#   Floor_Sill_150             oak strip 1.5 x 0.20 x 0.015 centred on a grid line (origin at its start node), rot 0/90
#   Leaf_Plank_Full / _Cut     hinge at the origin, extends +X, 0.84 x 2.20 / 0.84 x 0.95 (CAP top), 0.08 thick
#   Apron_300x150              placed with its door's origin and rotation: local x -0.75..2.25, y 0..1.5 (beyond face B)
#   RushMat (1.2 x 0.8, STRAW), Rug_300x150 (2.6 x 1.3, TEXTILE rug_madder) -- overlays z 0..0.025
import bpy, bmesh, math, json
from mathutils import Vector, Matrix

VKI_FLOOR_Z0 = -0.10


# ---------------------------------------------------------------- floor slabs (§2.7 parity)
def vki_floor_slab(k, S, qa=0, qb=0):
    """S x S slab from the min corner, z -0.10..0, no bevel, every face FLOOR (world-locked t 3.0); Q pieces add
    the parity offset (qa, qb) * 0.5 so they tile continuously with 300/600 slabs at even nodes"""
    vs = list(set(k.box((S / 2, S / 2, VKI_FLOOR_Z0 / 2), (S, S, -VKI_FLOOR_Z0), VKI_FLOOR, bevel=0)))
    k.bm.normal_update()
    for f in list(k.bm.faces):
        # every face world-locked (T6): tops/bottoms take (qa, qb) * 0.5; a side face's U runs along x (+-Y faces)
        # or y (+-X faces), so it takes only that axis' parity, and its V (= z) none
        n = f.normal
        off = (0.5 * qa, 0.5 * qb) if abs(n.z) > 0.7 else ((0.5 * qa, 0.0) if abs(n.y) > 0.7 else (0.5 * qb, 0.0))
        k.project([f], VKI_FLOOR, offset=off)
    k.meta.update(vki_class="floor", vki_kind="Q150" if S < 2 else "Slab", vki_len=S)
    if S < 2:
        k.meta.update(vki_q_parity=[qa, qb], vki_place_rule="node (i, j) with (i mod 2, j mod 2) = (%d, %d)" % (qa, qb))
    else:
        k.meta.update(vki_place_rule="even nodes only (x, y multiples of 3.0)")
    return vs


def vki_floor_q(qa, qb):
    def fn(k):
        vki_floor_slab(k, 1.5, qa, qb)
    fn.__name__ = "vki_floor_q%d%d" % (qa, qb)
    return fn


def vki_floor_300(k): vki_floor_slab(k, 3.0)
def vki_floor_600(k): vki_floor_slab(k, 6.0)


def vki_floor_sill(k):
    """oak threshold strip over a floor-material change: 1.5 x 0.20 x 0.015, centred on the grid line, origin at
    its start node; no FLOOR faces. A stone sill is the style {"wood": "M_VKI_StoneBlockIn"}."""
    k.box((0.75, 0.0, 0.0075), (1.5, 0.20, 0.015), WOOD, bevel=0.005)
    k.meta.update(vki_class="floor", vki_kind="Sill", vki_len=1.5, vki_origin="segment_start",
                  vki_rot_lock="rot0_90", vki_nav="walk", vki_uv_lock="local")


# ---------------------------------------------------------------- door leaves
VKI_LEAF_T = 0.08                   # plank thickness
VKI_LEAF_Y0 = 0.004                 # planks occupy local y 0.004 .. 0.084: 4 mm clear of the hinge plane at any angle
VKI_LEAF_STRAP_X0 = 0.10            # room-side straps start this far from the hinge (clear of the jamb when open)


def vki_leaf_plank(k, height):
    """4 oak planks (V-jointed by their bevels), iron straps on both faces, a ring pull on the room side (-Y when
    closed in its door). Cut: 0.95 tall with CAP plank tops.
    Fix r1: the hinge axis (local Z through the origin) lies on the leaf's ROOM-side face, so the planks occupy
    local y 0.004 .. 0.084. Opening by theta (rotation -theta about Z, toward -Y) maps (x, y) to
    x' = x cos(theta) + y sin(theta), which stays > 0 for y > 0: the leaf never swings back past the reveal plane
    into the jamb or the Corner post (the old centred planks reached 5 cm into both at 90 deg). Closed in its door
    (socket at door-local y -T/2 + 0.05) the leaf spans door-local y -0.196 .. -0.116. The room-side straps (y < 0)
    start VKI_LEAF_STRAP_X0 from the hinge, so at 90 deg they sit >= 0.10 into the room, past the O jambs
    (|y| <= 0.28 at door-local y -0.20 - 0.10 = -0.30)."""
    full = height == "Full"
    z0 = VKI_TIM_DOOR["thr"] + 0.005
    z1 = z0 + (2.16 if full else 0.95)
    x0, x1, n = 0.005, 0.835, 4
    w = (x1 - x0) / n
    t, y0 = VKI_LEAF_T, VKI_LEAF_Y0
    for i in range(n):
        a = x0 + i * w
        c = (a + w / 2, y0 + t / 2, (z0 + z1) / 2); sz = (w, t, z1 - z0)
        vs = list(set(k.box(c, sz, WOOD, bevel=0.012)))
        if not full:
            vki_top_faces(k, vs, VKI_CAP, c, sz)
    zs = (0.36, 1.12, 1.88) if full else (0.24, 0.74)
    sx0 = VKI_LEAF_STRAP_X0
    for z in zs:
        k.box(((sx0 + 0.80) / 2, y0 - 0.006, z), (0.80 - sx0, 0.012, 0.045), IRON, bevel=0.004)     # room side
        k.box((0.42, y0 + t + 0.006, z), (0.76, 0.012, 0.045), IRON, bevel=0.004)                   # outer side
    zr = 1.02 if full else 0.52
    k.box((0.66, y0 - 0.006, zr + 0.03), (0.07, 0.012, 0.09), IRON, bevel=0.003)
    before = set(k.bm.verts)
    ring(k, (0.66, y0 - 0.018, zr), 0.034, 0.054, 0.012, IRON, n=12, axis="Y")
    # the ring hangs from its staple and leans 8 deg off the plank at the bottom (core fix: its 12 flat segments no
    # longer lie in the planes of the back plate / plank faces)
    rv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.rotate(k.bm, verts=rv, cent=Vector((0.66, y0 - 0.008, zr + 0.054)),
                     matrix=Matrix.Rotation(math.radians(-8.0), 3, "X"))
    # vki_leaf_width is the MEASURED plank width (review r2): 0.83 = the 0.84 opening minus 5 mm clearance each side
    k.meta.update(vki_class="leaf", hinge_axis="local Z", vki_leaf_state="closed", vki_leaf_open_deg=90,
                  vki_leaf_width=round(x1 - x0, 3), vki_leaf_height=round(z1 - z0, 3), vki_hinge=[0.0, 0.0, 0.0],
                  vki_leaf_clearance=0.005,
                  vki_leaf_open_dir="rotation -deg about local Z (toward the room, -Y)",
                  vki_leaf_fits="SM_VKI_Wall_*_Door_150_" + height + " at its vki_leaf_socket, same rotation")


def vki_leaf_plank_full(k): vki_leaf_plank(k, "Full")
def vki_leaf_plank_cut(k): vki_leaf_plank(k, "Cut")


# ---------------------------------------------------------------- exit apron
VKI_APRON_Y = (0.15, 0.30, 1.65)    # inner edge (class P outer face), full-height start, outer edge


def vki_apron_build(k, x0=-0.75, x1=2.25, slabs=((0.30, 0.745), (0.755, 1.20)), kind="Apron", fits="Door_150"):
    """exterior ground outside an exit: 3.0 x 1.5 beyond the outer face, over local x x0..x1 in the door's frame
    (place it with the door's origin and rotation). It starts at the class P outer face (y 0.15) so it closes up to
    Board / Wattle doors too; the strip y 0.15..0.30 (under an O wall's body and threshold) is 4 mm lower, so its top
    never shares the z 0 plane with a door footing (T5). FLOOR slot with its own UVs at t 4.0 (styles ApronCobble /
    ApronDirt / ApronGrass), fading to black over the outer 0.5 m; a doorstone of dressed slabs at the threshold."""
    ya, yb, yc = VKI_APRON_Y
    W = x1 - x0; cx = (x0 + x1) / 2
    before = set(k.bm.verts)
    k.box((cx, (yb + yc) / 2, VKI_FLOOR_Z0 / 2), (W, yc - yb, -VKI_FLOOR_Z0), VKI_FLOOR, bevel=0)
    k.box((cx, (ya + yb) / 2, (VKI_FLOOR_Z0 - 0.004) / 2), (W, yb - ya, -VKI_FLOOR_Z0 - 0.004), VKI_FLOOR, bevel=0)
    vs = [v for v in k.bm.verts if v not in before]
    vs = vki_cut(k, vs, xs=[x0 + 0.25 * i for i in range(1, int(round(W / 0.25)))], ys=[yb + 0.25 * j for j in range(1, 6)])
    k.project(vki_faces_of(vs), VKI_FLOOR, tile=4.0)
    for v in vs:
        d = min(yc - v.co.y, v.co.x - x0, x1 - v.co.x)
        k.set_dark([v], 1.0 - vki_smoothstep(0.0, 0.5, d))
    # doorstone (fix r1): dressed slabs (DRESS, the warm dark dressed stone) with chamfered arrises, so the step
    # reads as cut stone with a joint instead of one flat pale slab (the pale StoneBlockIn slab out-shone the window
    # glass by Day); each slab gets its own texture crop and a slight darkening toward the outer edge
    for i, (xa, xb) in enumerate(slabs):
        vs = k.box(((xa + xb) / 2, 0.52, -0.01), (xb - xa, 0.46, 0.08), DRESS, bevel=0.022, segs=2,
                   jitter=0.003, seed=77 + i)
        for v in set(vs):
            k.set_dark([v], 0.10 + 0.12 * vki_smoothstep(0.40, 0.75, v.co.y))
    k.slot_mats = {VKI_FLOOR: "ApronCobble"}
    k.meta.update(vki_class="link", vki_kind=kind, vki_len=W, vki_origin="door_origin",
                  vki_place_rule=f"same origin and rotation as its {fits} piece", vki_uv_lock="own_t4",
                  vki_rot_lock="none", vki_nav="walk", vki_styles=["ApronCobble", "ApronDirt", "ApronGrass"],
                  vki_lights=[dict(type="AREA", role="apron", pos=[cx, 1.1, 2.6], aim=[cx, 0.2, 0.0], size=1.6,
                                   w_day=60.0, w_night=25.0, color_day=[.80, .87, 1.0],
                                   color_night=[.62, .70, 1.0], shadows=1)])


def vki_apron(k):
    """the 1.5 m exit's apron: local x -0.75..2.25 (centred on the Door_150 opening), a two-slab doorstone"""
    vki_apron_build(k)


def vki_apron_wide(k):
    """the wide exit's apron (coordinator, 2026-09-26): local x 0..3.0, so it sits at its DoorWide_300's origin on the
    1.5 lattice (the centred 1.5 m apron fell 0.75 m off it, T11), with a three-slab doorstone over x 0.62-2.38 that
    covers both wide openings (Stone 0.60-2.40, Ashlar 0.70-2.30)"""
    vki_apron_build(k, 0.0, 3.0, slabs=((0.62, 1.19), (1.20, 1.79), (1.80, 2.38)), kind="ApronWide",
                    fits="DoorWide_300")


# ---------------------------------------------------------------- overlays (§5.4)
def vki_rushmat(k):
    """1.20 x 0.80 rush mat, STRAW, z 0..0.025, 1 cm bevels, a slightly darker bound border"""
    vs = list(set(k.box((0.0, 0.0, 0.0125), (1.2, 0.8, 0.025), VKI_STRAW, bevel=0.01)))
    vs = vki_cut(k, vs, xs=(-0.53, 0.53), ys=(-0.33, 0.33))
    k.project(vki_faces_of(vs), VKI_STRAW)
    for v in vs:
        if abs(v.co.x) > 0.54 or abs(v.co.y) > 0.34:
            k.set_dark([v], 0.22)
    k.meta.update(vki_class="overlay", vki_kind="RushMat", vki_mount="floor", vki_tier="dressing",
                  vki_note="inside every exit; never across a sill or threshold")


def vki_rug(k, cell="rug_madder"):
    """2.60 x 1.30 rug on the textile atlas (the cell's painted fringe sits on thin 6 mm end strips), z 0..0.025"""
    before = set(k.bm.verts)
    k.box((0.0, 0.0, 0.0125), (2.34, 1.30, 0.025), VKI_TEXTILE, bevel=0.01)
    for s in (-1, 1):
        k.box((s * 1.235, 0.0, 0.003), (0.13, 1.28, 0.006), VKI_TEXTILE, bevel=0.002)
    vs = [v for v in k.bm.verts if v not in before]
    vki_textile_map(k, vki_faces_of(vs), cell, plane=((1, 0, 0), (0, 1, 0)))
    k.meta.update(vki_class="overlay", vki_kind="Rug", vki_mount="floor", vki_tier="dressing", vki_textile=cell,
                  vki_note="never across a sill or threshold")


VKI_FLOOR_SPECS = [
    ("SM_VKI_Floor_150_Q00", vki_floor_q(0, 0), "floor"),
    ("SM_VKI_Floor_150_Q10", vki_floor_q(1, 0), "floor"),
    ("SM_VKI_Floor_150_Q01", vki_floor_q(0, 1), "floor"),
    ("SM_VKI_Floor_150_Q11", vki_floor_q(1, 1), "floor"),
    ("SM_VKI_Floor_300", vki_floor_300, "floor"),
    ("SM_VKI_Floor_600", vki_floor_600, "floor"),
    ("SM_VKI_Floor_Sill_150", vki_floor_sill, "prop"),
    ("SM_VKI_Leaf_Plank_Full", vki_leaf_plank_full, "prop"),
    ("SM_VKI_Leaf_Plank_Cut", vki_leaf_plank_cut, "prop"),
    ("SM_VKI_Apron_300x150", vki_apron, "floor"),
    ("SM_VKI_Apron_Wide_300x150", vki_apron_wide, "floor"),
    ("SM_VKI_RushMat", vki_rushmat, "floor"),
    ("SM_VKI_Rug_300x150", vki_rug, "floor"),
]
VKI_FLOOR_NAMES = [n for n, _, _ in VKI_FLOOR_SPECS]
vki_register([(n, fn, {"grime": gr}, "core") for n, fn, gr in VKI_FLOOR_SPECS])
