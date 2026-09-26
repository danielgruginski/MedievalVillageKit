# ===================== VKI LINKS: stairs, dais, window pool, runners (§3.3, §5.4) -- PKG-L =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (§3.3 links, §5.4 overlays, §6 Unity metadata, §10 amendments).
# Loaded by vki_ns() (VKI_TEXTS, after the wall families; uses vki_fam_timber's geometry helpers vki_prism, vki_cut,
# vki_faces_of, vki_top_faces, vki_proj_long, vki_hash_off). Every top-level name starts with vki_/VKI_ (T18).
#   Stair_Up_150x450_RailR    min corner, rot 0 rises +Y (rot 0 / +-90, never 180). 15 risers x 0.200, 14 goings x
#                             0.2586 (nosing lines y (i-1) g, tops 0.2 i); flight x 0.33-1.27 between a wall string
#                             and an outer string with the closed spandrel and the handrail (0.95 above the pitch
#                             line, cut at the ceiling plane z 3.0); pale HEWN nosings; the top two treads darkened
#                             0.6; lip (upper-floor edge, the 15th step) x 0.33-1.50, y 3.62-4.215, z 2.80-3.00.
#                             No FLOOR faces: the room floor is laid under the whole footprint.
#   Stair_Down_150x450_RailR  same origin and rotation as its Up. Hole x 0.33-1.27, y 0.10-3.62 in oak trimmers,
#                             PLANKS landing y 3.62-4.215 (HEWN nosing), 10 treads descending north -> south from
#                             z -0.20 to -2.00 with their risers facing the camera, a closed VOID box z -2.40..-2.005
#                             under the hole, rails at 0.95 along +X (y 0.05-2.95) and across the south end.
#                             No FLOOR faces; the piece covers its footprint (no room floor under it).
#   Both stairs keep 5 mm clear of the wall envelope (x >= 0.285 from the wall along x = 0, y <= 4.215 = the proud
#   line of the wall along y = 4.5) and of the post squares that can exist there (Mid post at (0, 0): y <= 0.12;
#   Corner post at (0, 4.5): x, 4.5 - y <= 0.31). No posts at (0, 1.5), (0, 3.0) (rhythm posts skipped, §2.3) or at
#   (1.5, 4.5) (the lip / landing reach y 4.215 up to x 1.50).
#   Floor_Dais_300            [0,3]^2, even nodes, slab z -0.10..0.20, FLOOR top (world-locked t 3.0), DRESS nosing
#                             on the -Y edge only (0.03 overhang) with a pale StoneBlockIn chamfer
#   FX_WindowPool             floor light pool in its window's frame (place with the window's origin + rotation):
#                             an elliptic FX puck (M_VKI_FX_Light: emission (1-v)^2), top z 0.005, embedded in the floor
#   Runner_300 / Runner_150   TEXTILE runner cell (u-periodic, 1.5 m per cell): 1.00 wide, z 0..0.025, 1 cm chamfers
#                             on the long edges, square ends, so runners chain along local x with no join
# Build: g["vki_ws_build"]("links", VKI_LNK_NAMES); test: g["vki_test_pieces"](VKI_LNK_NAMES) -> {}.
import bpy, bmesh, math, json
from mathutils import Vector, Matrix

VKI_LNK_X = (0.33, 1.27)                  # flight (up) / hole (down), local x
VKI_LNK_RISE = 0.200                      # 15 risers x 0.200 = one storey (3.00)
VKI_LNK_RISERS = 15
VKI_LNK_GO = 3.62 / 14                    # going: 14 goings = 3.62
VKI_LNK_TOP_Y = 3.62                      # nosing line of the lip (up) / landing (down)
VKI_LNK_BACK_Y = 4.215                    # lip / landing back = the proud line of the wall along y 4.5
VKI_LNK_POST_CLR = 0.315                  # posts reach 0.31 from their node: stay 5 mm clear
VKI_LNK_WALL_CLR = 0.285                  # wall members reach 0.28 (CAP_HW): stay 5 mm clear (= the proud line)
VKI_LNK_MID_CLR = 0.125                   # a Mid post at (0, 0) reaches y 0.12 along its wall
VKI_LNK_TREAD_T = 0.05                    # tread board
VKI_LNK_NOSE = 0.07                       # HEWN nosing strip at the front (south edge) of each tread
VKI_LNK_OVER = 0.03                       # nosing overhang past the riser board
VKI_LNK_RISER_T = 0.025                   # riser board
VKI_LNK_STR = (0.07, 0.10, 0.30)          # string thickness, top above the pitch line, bottom below it
VKI_LNK_STR_X = ((0.33, 0.40), (1.20, 1.27))    # wall / west string, outer / east string
VKI_LNK_TREAD_X = (0.395, 1.205)          # treads and nosings run 5 mm into the strings
VKI_LNK_RISER_X = (0.39, 1.21)            # risers 1 cm into the strings (end planes apart from the treads', T5S)
VKI_LNK_RAIL_H = 0.95                     # handrail top above the pitch line (up) / rail top above the floor (down)
VKI_LNK_RAIL = (0.08, 0.07)               # handrail / rail width, height
VKI_LNK_DARK_TOP = 0.6                    # the up flight's top two treads (under the ceiling), §3.3
VKI_LNK_DN_TREADS = 10                    # z -0.20 .. -2.00
VKI_LNK_DN_DARK = (0.12, 0.62)            # the down flight darkens with depth (tread 1 .. tread 10)
VKI_LNK_DN_HEWN = 6                       # pale HEWN nosings on treads 1..6, oak below (M_VK_Hewn ignores Col)
VKI_LNK_VOID_Z = (-2.40, -2.005)          # closed VOID box under the hole (its top 5 mm below tread 10's top)
VKI_LNK_UP_TRIGGER = [0.80, 0.30, 1.0, 0.94, 0.55, 2.0]      # §3.3: centre, size (piece-local)
VKI_LNK_DN_TRIGGER = [1.485, 3.555, 1.0, 0.43, 1.31, 2.0]    # §3.3: x 1.27-1.70, y 2.90-4.21, z 0-2
VKI_LNK_UP_SPAWN = ([0.75, -0.75], 180)   # (local xy, compass facing: 0 = local +Y, 180 = toward the camera)
VKI_LNK_DN_SPAWN = ([2.25, 3.75], 90)
VKI_LNK_UP = "SM_VKI_Stair_Up_150x450_RailR"
VKI_LNK_DN = "SM_VKI_Stair_Down_150x450_RailR"


# ---------------------------------------------------------------- small helpers
def vki_lnk_uv(k, fs, mi, U, V, c=(0.0, 0.0, 0.0), tile=None, off=None):
    """planar UVs with explicit axes, any slot (Kit.project only turns the grain for WOOD / SHUTTER / CAP; HEWN
    grain runs along the texture's U): u = (p - c).U / t + off"""
    U = Vector(U).normalized(); V = Vector(V).normalized(); c = Vector(c)
    t = tile or vki_tile(mi)
    o = vki_hash_off(c) if off is None else off
    for f in fs:
        f.material_index = mi
        for l in f.loops:
            d = l.vert.co - c
            l[k.uv].uv = (d.dot(U) / t + o[0], d.dot(V) / t + o[1])


def vki_lnk_box(k, x0, x1, y0, y1, z0, z1, mi, bev=0.01, dark=0.0):
    """member box by its extents; returns its (unique) vertices"""
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    vs = list(set(k.box(c, (x1 - x0, y1 - y0, z1 - z0), mi, bevel=bev)))
    if dark:
        k.set_dark(vs, dark)
    return vs


def vki_lnk_tops(k, vs, mi, along=(1.0, 0.0, 0.0), nz=0.65):
    """re-project the upward faces of a member in slot mi with the grain along `along`"""
    k.bm.normal_update()
    fs = [f for f in vki_faces_of(vs) if f.normal.z > nz]
    a = Vector(along).normalized()
    c = sum((v.co for v in vs), Vector()) / max(1, len(vs))
    vki_lnk_uv(k, fs, mi, a, Vector((0, 0, 1)).cross(a), c=c)
    return fs


def vki_lnk_planks(k, vs, along=(1.0, 0.0, 0.0), dark=0.0):
    """PLANKS faces of a member with the boards (T_VK_Planks draws them along V, 0.25 m wide) running along
    `along`; one hash offset per member, so neighbouring treads show different boards"""
    k.bm.normal_update()
    a = Vector(along).normalized()
    c = sum((v.co for v in vs), Vector()) / max(1, len(vs))
    off = vki_hash_off(c)
    t = vki_tile(PLANKS)
    for f in vki_faces_of(vs):
        n = f.normal
        if abs(n.dot(a)) > 0.9:                       # end faces: any in-plane frame
            U = n.cross(Vector((0, 0, 1))) if abs(n.z) < 0.9 else Vector((1, 0, 0))
            U.normalize(); V = n.cross(U).normalized()
        else:
            V = (a - n * a.dot(n)).normalized(); U = n.cross(V).normalized()
        f.material_index = PLANKS
        for l in f.loops:
            p = l.vert.co
            l[k.uv].uv = (p.dot(U) / t + off[0], p.dot(V) / t + off[1])
    if dark:
        k.set_dark(vs, dark)
    return vs


def vki_lnk_pitch_up(y):
    """pitch (nosing) line of the up flight: tread i has its nosing at ((i - 1) g, 0.2 i)"""
    return VKI_LNK_RISE + y * VKI_LNK_RISE / VKI_LNK_GO


def vki_lnk_pitch_dn(y):
    """pitch (nosing) line of the down flight: 0 at the landing nosing (y 3.62), tread j at (3.62 - j g, -0.2 j)"""
    return -(VKI_LNK_TOP_Y - y) * VKI_LNK_RISE / VKI_LNK_GO


def vki_lnk_tread(k, yn, zt, hewn=True, dark=0.0):
    """one tread with its nosing line (south edge) at yn and top at zt: a HEWN nosing strip y yn .. yn + 0.07 that
    overhangs the riser below by 0.03, and the tread board behind it to yn + going + 0.055 (under the next riser).
    hewn=False: an oak nosing (M_VK_Hewn ignores the vertex colour, so a darkened tread needs WOOD)"""
    x0, x1 = VKI_LNK_TREAD_X
    t = VKI_LNK_TREAD_T
    vki_lnk_box(k, x0, x1, yn, yn + VKI_LNK_NOSE, zt - t, zt, HEWN if hewn else WOOD, bev=0.012, dark=dark)
    vki_lnk_planks(k, vki_lnk_box(k, x0, x1, yn + VKI_LNK_NOSE, yn + VKI_LNK_GO + VKI_LNK_OVER + VKI_LNK_RISER_T,
                                  zt - t, zt, PLANKS, bev=0.008), dark=dark)


def vki_lnk_riser(k, yf, z0, z1, dark=0.0):
    """riser board (planks along x) with its front face at yf (VKI_LNK_OVER behind the nosing line above it)"""
    x0, x1 = VKI_LNK_RISER_X
    return vki_lnk_planks(k, vki_lnk_box(k, x0, x1, yf, yf + VKI_LNK_RISER_T, z0, z1, PLANKS, bev=0.006), dark=dark)


def vki_lnk_string(k, x0, x1, poly, slope, dark_fn=None):
    """a string board: convex (y, z) polygon extruded x0..x1, grain along the flight"""
    vs, fs = vki_prism(k, poly, x0, x1, WOOD, axis="x", bevel=0.008, project=False)
    vki_proj_long(k, fs, WOOD, slope, off=vki_hash_off((x0, poly[0][0], poly[0][1])))
    if dark_fn is not None:
        for v in vs:
            k.set_dark([v], dark_fn(v.co.z))
    return vs


def vki_lnk_rail_prism(k, x0, x1, pa, pb, h, slope):
    """sloped handrail: parallelogram (y, z) extruded x0..x1; HEWN top with the grain along the rail, oak sides"""
    (ya, za), (yb, zb) = pa, pb
    vs, fs = vki_prism(k, [(ya, za - h), (yb, zb - h), (yb, zb), (ya, za)], x0, x1, WOOD, axis="x", bevel=0.01,
                       project=False)
    top = [f for f in fs if f.normal.z > 0.3]
    vki_proj_long(k, [f for f in fs if f not in top], WOOD, slope, off=vki_hash_off((x0, ya, za)))
    for f in top:
        vki_lnk_uv(k, [f], HEWN, slope, f.normal.cross(slope), c=(x0, ya, za))
    return vs


def vki_lnk_meta_common(k):
    k.meta.update(vki_class="link", vki_len=1.5, vki_depth=4.5, vki_rise=VKI_LNK_RISE, vki_risers=VKI_LNK_RISERS,
                  vki_going=round(VKI_LNK_GO, 5), vki_rot_lock="no180", vki_rot_allowed=[0, 90, -90],
                  vki_nominal="0,0,1.5,4.5", vki_cells=[[0, 0], [0, 1], [0, 2]], vki_facing_min=60,
                  vki_needs_walls=["local x = 0 (y 0..4.5)", "local y = 4.5 (x 0..1.5)"],
                  vki_no_wall="local x = 1.5 side (the open / rail side)",
                  vki_post_rule={"allowed": "Mid post at local (0, 0); Corner post at local (0, 4.5)",
                                 "forbidden": [[0.0, 1.5], [0.0, 3.0], [1.5, 4.5]],
                                 "note": "rhythm posts are skipped along the stair's walls (§2.3)"},
                  vki_uv_lock="local")


# ---------------------------------------------------------------- Stair_Up_150x450_RailR (§3.3)
def vki_lnk_stair_up(k):
    """the up flight: 14 treads + the lip; strings, closed spandrel, handrail cut at the ceiling plane (z 3.0: the
    rail passes through the hole in the upper floor, which the cutaway removes), top two treads darkened"""
    g_, r_ = VKI_LNK_GO, VKI_LNK_RISE
    P = vki_lnk_pitch_up
    kk = r_ / g_
    slope = Vector((0.0, g_, r_)).normalized()
    ntop = VKI_LNK_RISERS - 2                                   # treads 13 and 14 are darkened
    for i in range(1, VKI_LNK_RISERS):                          # treads 1..14 (the lip is the 15th step)
        yn, zt = (i - 1) * g_, r_ * i
        d = VKI_LNK_DARK_TOP if i >= ntop else 0.0
        vki_lnk_tread(k, yn, zt, hewn=d == 0.0, dark=d)
        z0 = zt - r_ - 0.005 if i > 1 else -0.006               # riser 1 stands 6 mm into the room floor
        vki_lnk_riser(k, yn + VKI_LNK_OVER, z0, zt - VKI_LNK_TREAD_T + 0.005, dark=d)
    # strings: top 0.10 above the pitch line, bottom 0.30 below it, running into the lip block (cut at z 2.90)
    st, sb = VKI_LNK_STR[1], VKI_LNK_STR[2]
    zc, ye = 2.90, 3.70
    yc = (zc - r_ - st) / kk

    def spoly(y0, zb):
        yb = (zb + sb - r_) / kk
        return [(y0, zb), (y0, P(y0) + st), (yc, zc), (ye, zc), (ye, P(ye) - sb), (yb, zb)]
    sdark = lambda z: 0.45 * vki_smoothstep(2.1, 2.85, z)
    (wa, wb), (oa, ob) = VKI_LNK_STR_X
    vki_lnk_string(k, wa, wb, spoly(0.015, -0.010), slope, sdark)
    vki_lnk_string(k, oa, ob, spoly(0.06, -0.010), slope, sdark)     # starts inside the bottom newel
    # closed spandrel under the outer string (oak boards, grain vertical): the triangle under the flight and the
    # full-height panel under the lip; its edges run 4 cm into the string / the lip block
    xs0, xs1 = 1.215, 1.255
    for poly in ([(0.13, -0.008), (0.13, 0.03), (VKI_LNK_TOP_Y, P(VKI_LNK_TOP_Y) - sb + 0.04),
                  (VKI_LNK_TOP_Y, -0.008)],
                 [(VKI_LNK_TOP_Y, -0.008), (4.20, -0.008), (4.20, 2.85), (VKI_LNK_TOP_Y, 2.85)]):
        vs, fs = vki_prism(k, poly, xs0, xs1, PLANKS, axis="x", bevel=0.006, project=False)
        vki_lnk_planks(k, vs, along=(0, 0, 1))                  # upright boards
        for v in vs:
            k.set_dark([v], 0.1 + 0.3 * vki_smoothstep(1.8, 2.8, v.co.z))
    # king post at the spandrel's tall end, under the lip block
    vki_lnk_box(k, 1.195, 1.305, 3.655, 3.775, -0.012, 2.805, WOOD, bev=0.015, dark=0.3)
    # balustrade: bottom newel, handrail 0.95 above the pitch line, balusters on the string, top newel cut at the
    # ceiling plane (z 3.0) where the rail passes into the upper floor
    H, (rw, rh) = VKI_LNK_RAIL_H, VKI_LNK_RAIL
    xr0, xr1 = 1.235 - rw / 2, 1.235 + rw / 2
    xn0, xn1 = 1.175, 1.295
    nb = vki_lnk_box(k, xn0, xn1, 0.01, 0.13, -0.012, 1.32, WOOD, bev=0.015)   # 1 cm behind the first nosing
    vki_lnk_tops(k, nb, HEWN)
    y_t = (3.0 - r_ - H) / kk                                  # the rail top meets z 3.0 here (2.39)
    nt = vki_lnk_box(k, xn0, xn1, y_t - 0.06, y_t + 0.06, P(y_t) - 0.15, 2.995, WOOD, bev=0.015, dark=0.2)
    vki_lnk_tops(k, nt, HEWN)
    ya, yb_ = 0.06, y_t - 0.01
    vki_lnk_rail_prism(k, xr0, xr1, (ya, P(ya) + H), (yb_, P(yb_) + H), rh, slope)
    for yb in (0.30, 0.60, 0.90, 1.20, 1.50, 1.80, 2.10):
        vki_lnk_box(k, 1.2175, 1.2525, yb - 0.0175, yb + 0.0175, P(yb) + st - 0.03, P(yb) + H - rh + 0.03, WOOD,
                    bev=0.0)
    # lip: the upper-floor edge (the 15th step): HEWN nosing, PLANKS boards, oak block whose front face is riser 15
    # under the nosing; darkened underside
    xa, xb = VKI_LNK_X[0], 1.50
    yl, yb = VKI_LNK_TOP_Y, VKI_LNK_BACK_Y
    vki_lnk_box(k, xa, xb, yl, yl + VKI_LNK_NOSE, 3.0 - VKI_LNK_TREAD_T, 3.0, HEWN, bev=0.012)
    vki_lnk_planks(k, vki_lnk_box(k, xa, xb, yl + VKI_LNK_NOSE, yb, 3.0 - VKI_LNK_TREAD_T, 3.0, PLANKS, bev=0.008))
    blk = vki_lnk_box(k, xa + 0.005, xb - 0.005, yl + VKI_LNK_OVER, yb - 0.005, 2.80, 3.0 - VKI_LNK_TREAD_T + 0.005,
                      WOOD, bev=0.01)
    for v in blk:
        k.set_dark([v], 0.6 if v.co.z < 2.85 else 0.3)
    vki_lnk_meta_common(k)
    (sx, sy), sf = VKI_LNK_UP_SPAWN
    k.meta.update(vki_link="stair_up", vki_pair=VKI_LNK_DN, vki_trigger=VKI_LNK_UP_TRIGGER,
                  vki_spawn_local=[sx, sy], vki_spawn_facing=sf, vki_prompt_local=[0.80, 0.30, 1.40],
                  vki_floor_under="room floor laid under the whole footprint (no FLOOR faces)",
                  vki_nav="block", vki_collider=[[0.815, 2.2825, 1.5, 0.97, 3.865, 3.0]],
                  vki_lip=[xa, yl, 2.80, xb, yb, 3.0])


# ---------------------------------------------------------------- Stair_Down_150x450_RailR (§3.3)
def vki_lnk_stair_down(k):
    """the hole in the upper floor: trimmers, landing, 10 treads descending north -> south (risers face the
    camera) into the dark, closed VOID box under them, rails along +X and across the south end"""
    g_, r_ = VKI_LNK_GO, VKI_LNK_RISE
    P = vki_lnk_pitch_dn
    kk = r_ / g_
    yt = VKI_LNK_TOP_Y
    xa, xb = VKI_LNK_X
    T = VKI_LNK_TREAD_T
    N = VKI_LNK_DN_TREADS
    slope = Vector((0.0, g_, r_)).normalized()
    d0, d1 = VKI_LNK_DN_DARK
    for j in range(1, N + 1):
        yn, zt = yt - j * g_, -r_ * j
        d = d0 + (d1 - d0) * (j - 1) / (N - 1)
        vki_lnk_tread(k, yn, zt, hewn=j <= VKI_LNK_DN_HEWN, dark=d)     # deep nosings oak: they fade with the ramp
        vki_lnk_riser(k, yn + g_ + VKI_LNK_OVER, zt - 0.005, -r_ * (j - 1) - T + 0.005, dark=d)
    # landing: HEWN nosing over the hole's width, PLANKS boards to the proud line (x to 1.50)
    vki_lnk_box(k, xa, xb, yt, yt + VKI_LNK_NOSE, -T, 0.0, HEWN, bev=0.012)
    vki_lnk_planks(k, vki_lnk_box(k, xa, 1.50, yt + VKI_LNK_NOSE, VKI_LNK_BACK_Y, -T, 0.0, PLANKS, bev=0.008))
    # oak trimmers (top z 0): east (to the landing), south, west (narrow full length + wide between the end posts)
    zb = -0.30
    vki_lnk_box(k, xb, 1.50, 0.0, yt + VKI_LNK_NOSE, zb, 0.0, WOOD, bev=0.008)
    vki_lnk_box(k, VKI_LNK_POST_CLR, xb, 0.0, 0.10, zb, 0.0, WOOD, bev=0.008)
    vki_lnk_box(k, VKI_LNK_POST_CLR, xa, 0.10, VKI_LNK_BACK_Y, zb, 0.0, WOOD, bev=0.004)
    vki_lnk_box(k, VKI_LNK_WALL_CLR, VKI_LNK_POST_CLR, VKI_LNK_MID_CLR, 4.5 - VKI_LNK_POST_CLR, zb, 0.0, WOOD,
                bev=0.004)
    # strings along the hole's sides, top 0.10 above the pitch line (clipped under the landing at z -0.055),
    # bottom 0.30 below it, both ends buried (in the VOID box / under the landing)
    st, sb = VKI_LNK_STR[1], VKI_LNK_STR[2]
    zc, ye, zv = -0.055, 3.70, VKI_LNK_VOID_Z[0] + 0.01
    ys = yt - (st + 2.10) / kk                      # the string top is at z -2.10 (inside the VOID box) here
    yc = yt - (st - zc) / kk                        # ... reaches the landing clip here
    yf = yt + (zv + sb) / kk                        # the string bottom meets zv here
    poly = [(ys, zv), (ys, P(ys) + st), (yc, zc), (ye, zc), (ye, P(ye) - sb), (yf, zv)]
    sdark = lambda z: vki_clamp(0.1 + 0.6 * (-z) / 2.2, 0.0, 0.7)
    for (a, b) in VKI_LNK_STR_X:
        vki_lnk_string(k, a, b, poly, slope, sdark)
    # closed VOID box under the hole (its top 5 mm below tread 10's top: no coplanar faces, T5S)
    vki_lnk_box(k, xa + 0.005, xb - 0.005, 0.105, yt - 0.005, VKI_LNK_VOID_Z[0], VKI_LNK_VOID_Z[1], VOID, bev=0.0)
    # shaft linings (upright boards, darkening with depth) on the west, east and south sides, from inside the
    # trimmers down to the VOID box's bottom: without them the camera saw the black render background beside the
    # strings. Each lining sits inside its trimmer's width, 1 mm behind the string / trimmer faces (T5S).
    ldark = lambda z: vki_clamp(0.30 + 0.5 * (-0.3 - z) / 2.0, 0.30, 0.80)
    zl0, zl1 = VKI_LNK_VOID_Z[0] + 0.005, -0.295
    for x0, x1, y0, y1, al in ((0.316, xa - 0.001, 0.086, ye - 0.005, (0, 0, 1)),
                               (xb + 0.001, 1.284, 0.086, ye - 0.005, (0, 0, 1)),
                               (xa, xb, 0.086, 0.099, (0, 0, 1))):
        vs = vki_lnk_box(k, x0, x1, y0, y1, zl0, zl1, PLANKS, bev=0.0)
        vki_lnk_planks(k, vs, along=al)
        for v in vs:
            k.set_dark([v], ldark(v.co.z))
    # rails at 0.95: posts on the trimmers (inset 5 mm), HEWN rail tops, thin balusters
    H, (rw, rh) = VKI_LNK_RAIL_H, VKI_LNK_RAIL
    xe = (xb + 1.50) / 2                             # the east trimmer's centre line (1.385)
    posts = [(0.39, 0.05), (xe, 0.05), (xe, 1.05), (xe, 2.05), (xe, 2.95)]
    for (px, py) in posts:
        vs = vki_lnk_box(k, px - 0.045, px + 0.045, py - 0.045, py + 0.045, -0.005, H + 0.05, WOOD, bev=0.012)
        vki_lnk_tops(k, vs, HEWN)
    # the south rail stops at the east rail's side face (both end inside the SE post; overlapping they were coplanar)
    vs = vki_lnk_box(k, 0.39, xe - rw / 2, 0.05 - rw / 2, 0.05 + rw / 2, H - rh, H, WOOD, bev=0.01)
    vki_lnk_tops(k, vs, HEWN, along=(1, 0, 0))
    vs = vki_lnk_box(k, xe - rw / 2, xe + rw / 2, 0.05, 2.95, H - rh, H, WOOD, bev=0.01)
    vki_lnk_tops(k, vs, HEWN, along=(0, 1, 0))
    for x in (0.64, 0.89, 1.14):
        vki_lnk_box(k, x - 0.015, x + 0.015, 0.035, 0.065, -0.004, H - rh + 0.02, WOOD, bev=0.0)
    for y in (0.30, 0.55, 0.80, 1.30, 1.55, 1.80, 2.30, 2.55, 2.80):
        vki_lnk_box(k, xe - 0.015, xe + 0.015, y - 0.015, y + 0.015, -0.004, H - rh + 0.02, WOOD, bev=0.0)
    vki_lnk_meta_common(k)
    (sx, sy), sf = VKI_LNK_DN_SPAWN
    k.meta.update(vki_link="stair_down", vki_pair=VKI_LNK_UP, vki_trigger=VKI_LNK_DN_TRIGGER,
                  vki_spawn_local=[sx, sy], vki_spawn_facing=sf, vki_prompt_local=[1.485, 3.555, 1.40],
                  vki_floor_under="none: the piece covers its footprint (trimmers, landing); no FLOOR faces",
                  vki_nav="walk",
                  vki_collider=[[0.80, 1.86, 0.5, 0.94, 3.52, 1.0], [0.8875, 0.05, 0.5, 1.085, 0.10, 1.0],
                                [xe, 1.5, 0.5, 0.10, 2.99, 1.0]],
                  vki_collider_note="blocked boxes: the hole and the two rails; trimmers and landing walk at z 0",
                  vki_hole=[xa, 0.10, xb, yt])


# ---------------------------------------------------------------- Floor_Dais_300 (§3.3)
VKI_LNK_DAIS = dict(nose=0.25, thick=0.08, chamfer=0.05, over=0.03)


def vki_lnk_dais(k):
    """3.0 x 3.0 platform, top 0.20 (§2.1 reserved height), slab z -0.10..0.20 like a floor slab. Top FLOOR
    (world-locked t 3.0, so the dais tiles with 300 / 600 floors at even nodes), DRESS sides; on the -Y edge only a
    DRESS nosing strip (0.25 deep, 0.08 thick, 0.03 overhang over the riser) with a 0.05 pale StoneBlockIn chamfer
    on its arris, so the step reads as a pale line from the camera. Everything stays inside [0, 3]^2 (T1)."""
    S, zt, zb = 3.0, VKI_Z["dais"], VKI_FLOOR_Z0
    D = VKI_LNK_DAIS
    nd, nt, ch, ov = D["nose"], D["thick"], D["chamfer"], D["over"]
    vs = list(set(k.box((S / 2, (nd + S) / 2, (zb + zt) / 2), (S, S - nd, zt - zb), DRESS, bevel=0)))
    k.bm.normal_update()
    for f in vki_faces_of(vs):
        if f.normal.z > 0.7:
            k.project([f], VKI_FLOOR)                          # zero offset: world UVs (§2.7)
    vki_prism(k, [(ov, zb), (nd, zb), (nd, zt - nt), (ov, zt - nt)], 0.0, S, DRESS, axis="x")      # riser
    vs, fs = vki_prism(k, [(0.0, zt - nt), (nd, zt - nt), (nd, zt), (ch, zt), (0.0, zt - ch)], 0.0, S, DRESS,
                       axis="x")                                                                    # nosing
    for f in fs:
        if f.normal.z > 0.3 and f.normal.y < -0.3:
            vki_lnk_uv(k, [f], VKI_STONE_BLOCK_IN, (1, 0, 0), f.normal.cross(Vector((1, 0, 0))),
                       c=(0.0, 0.0, zt))                       # the pale chamfer
    k.meta.update(vki_class="floor", vki_kind="Dais", vki_len=S, vki_step=zt,
                  vki_place_rule="even nodes only (x, y multiples of 3.0); nosing on the -Y edge",
                  vki_note="top FLOOR takes the zone's floor style (e.g. Flag); props on it stand at z 0.20")


# ---------------------------------------------------------------- FX_WindowPool (§3.3)
VKI_LNK_POOL = dict(c=(0.75, -1.15), a=0.55, b=0.70, n=20, ring=(0.55, 0.18), rim_v=0.72, z=(0.005, -0.05))


def vki_lnk_window_pool(k):
    """floor light pool under a window, in the window's frame (origin = the window's start node, same rotation;
    room on local -Y): an elliptic puck, centre (0.75, -1.15), semi-axes 0.55 x 0.70 (where the window spot's pool
    lands, 0.45-1.85 m into the room). M_VKI_FX_Light shows emission (1-v)^2 at alpha 0.15, so v runs from 0 at the
    centre (0.18 at an inner ring, a flat bright core) to 0.72 at the rim, where the blended emission about equals
    what the 15 % alpha takes from a Day floor: no visible edge. Top z 0.005 (under rugs / runners / sills); the
    bottom and sides sit in the floor slab (z -0.05), so the puck is closed (T7) but only its top shows."""
    Pp = VKI_LNK_POOL
    cx, cy = Pp["c"]; a, b, n = Pp["a"], Pp["b"], Pp["n"]
    rr, rv = Pp["ring"]
    zt, zb = Pp["z"]
    bm = k.bm
    ct = bm.verts.new((cx, cy, zt)); cb = bm.verts.new((cx, cy, zb))
    ri, ro, rb = [], [], []
    for i in range(n):
        t = 2 * math.pi * i / n
        ca, sa = math.cos(t), math.sin(t)
        ri.append(bm.verts.new((cx + rr * a * ca, cy + rr * b * sa, zt)))
        ro.append(bm.verts.new((cx + a * ca, cy + b * sa, zt)))
        rb.append(bm.verts.new((cx + a * ca, cy + b * sa, zb)))
    fs = []
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((ct, ri[i], ri[j])))
        fs.append(bm.faces.new((ri[i], ro[i], ro[j], ri[j])))
        fs.append(bm.faces.new((ro[i], rb[i], rb[j], ro[j])))
        fs.append(bm.faces.new((cb, rb[j], rb[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vv = {ct: 0.0, cb: Pp["rim_v"]}
    vv.update({v: rv for v in ri}); vv.update({v: Pp["rim_v"] for v in ro + rb})
    for f in fs:
        f.material_index = VKI_FX
        for l in f.loops:
            l[k.uv].uv = (0.5 + (l.vert.co.x - cx) / (2 * a), vv[l.vert])
    k.meta.update(vki_class="fx", vki_kind="WindowPool", vki_origin="window_origin", vki_nav="none",
                  vki_place_rule="same origin and rotation as its Window piece (room on local -Y); on a dais add "
                                 "z 0.20",
                  vki_fx_presets=["Day"], vki_fx=[dict(fx="window_pool", pos=[cx, cy, 0.0])],
                  vki_note="Day only (the Night floor is darker: the rim would show)")


# ---------------------------------------------------------------- Runner_300 / Runner_150 (§5.4)
VKI_LNK_RUNNER = dict(w=1.0, h=0.025, chamfer=0.01, period=1.5)


def vki_lnk_runner(k, L):
    """TEXTILE runner L x 1.00, z 0..0.025, origin at its centre, running along local x. The long edges have 1 cm
    chamfers; the ends are square so runners butt with a flush, continuous top. The runner cell is periodic in u
    (1/4 cell = 0.375 m) and spans 1.5 m per cell, so the faces are cut at every 1.5 m from the start and mapped in
    vki_textile_map's period mode: every runner starts and ends on a whole period, and any chain (150 | 300 | ...)
    has no join in the pattern."""
    R = VKI_LNK_RUNNER
    W, h, c = R["w"], R["h"], R["chamfer"]
    prof = [(-W / 2, 0.0), (W / 2, 0.0), (W / 2, h - c), (W / 2 - c, h), (-W / 2 + c, h), (-W / 2, h - c)]
    vs, fs = vki_prism(k, prof, -L / 2, L / 2, VKI_TEXTILE, axis="x", project=False)
    cuts = [-L / 2 + R["period"] * i for i in range(1, int(round(L / R["period"])))]
    if cuts:
        vs = vki_cut(k, vs, xs=cuts)
    vki_textile_map(k, vki_faces_of(vs), "runner", plane=((1, 0, 0), (0, 1, 0)), period=R["period"])
    k.meta.update(vki_class="overlay", vki_kind="Runner", vki_len=L, vki_mount="floor", vki_tier="dressing",
                  vki_textile="runner", vki_chain="local x: runners butt end to end (lengths are whole periods)",
                  vki_note="never across a sill or threshold; the chapel aisle uses rot 90 (Runner_150 (6.0, 2.25) "
                           "+ Runner_300 (6.0, 4.5) chain along y 1.5-6.0)")


def vki_lnk_runner_300(k): vki_lnk_runner(k, 3.0)
def vki_lnk_runner_150(k): vki_lnk_runner(k, 1.5)


# ---------------------------------------------------------------- package checks and the workshop stair rig
def vki_lnk_env_check(stairs, objs, clear=0.005):
    """no stair vertex inside a wall or post envelope (PKG-L check): every vertex of the placed stairs, in each
    wall's frame (0 <= x <= L, -0.30 <= z <= H): |y| >= CAP_HW + clear; in each post's frame (z -0.30 .. top):
    outside its square grown by clear. Returns (errors, {stair: min clearance to any envelope})"""
    walls = [o for o in objs if o.get("vki_class") == "wall"]
    posts = [o for o in objs if o.get("vki_class") == "post"]
    errs, mins = [], {}
    for s in stairs:
        mw = vki_mw(s)
        pts = [mw @ v.co for v in s.data.vertices]
        best = 1e9
        for w in walls:
            L = float(w["vki_len"]); cls = vki_cls_of(w)
            H = VKI_CUT_H if w.get("vki_height") == "Cut" else VKI_H_FULL.get(w.get("vki_family"), 3.0)
            inv = vki_mw(w).inverted(); hw = VKI_CAP_HW[cls]; n = 0
            for p in pts:
                q = inv @ p
                if -1e-6 <= q.x <= L + 1e-6 and VKI_FOOT_Z - 1e-6 <= q.z <= H + 0.05:
                    d = abs(q.y) - hw
                    best = min(best, d)
                    if d < clear - 1e-6:
                        n += 1
            if n:
                errs.append(f"ENV {s.name}: {n} vertices within {clear} of wall {w.name}")
        for po in posts:
            cls = vki_cls_of(po)
            ax, ay = VKI_MID_HW[cls] if po.get("vki_kind") == "Mid" else (VKI_POST_HW[cls], VKI_POST_HW[cls])
            top = (VKI_CUT_H if po.get("vki_height") == "Cut" else VKI_H_FULL.get(po.get("vki_family"), 3.0)) + \
                VKI_POST_TOP
            inv = vki_mw(po).inverted(); n = 0
            for p in pts:
                q = inv @ p
                if VKI_POST_Z0 - 1e-6 <= q.z <= top + 1e-6:
                    d = max(abs(q.x) - ax, abs(q.y) - ay)
                    best = min(best, d)
                    if d < clear - 1e-6:
                        n += 1
            if n:
                errs.append(f"ENV {s.name}: {n} vertices within {clear} of post {po.name}")
        mins[s.name] = round(best, 4)
    return errs, mins


def vki_lnk_trigger_check(o, gap=0.2, r=0.3):
    """spawn capsule (radius r) at least `gap` outside the piece's own trigger box (§6 scene rules)"""
    tr = vki_get(o, "vki_trigger"); sp = vki_get(o, "vki_spawn_local")
    cx, cy, cz, sx, sy, sz = tr
    dx = max(abs(sp[0] - cx) - sx / 2, 0.0); dy = max(abs(sp[1] - cy) - sy / 2, 0.0)
    d = math.hypot(dx, dy) - r
    return ([] if d >= gap - 1e-9 else [f"TRIG {o.name}: spawn capsule {d:.3f} from its trigger (< {gap})"]), round(d, 4)


def vki_lnk_riser_points(o, xs=(0.45, 0.59, 0.73, 0.87, 1.01, 1.15)):
    """world sample points 5 mm in front of each riser's exposed front face (mid height, across its width):
    [(label, [points])]"""
    g_, r_, T = VKI_LNK_GO, VKI_LNK_RISE, VKI_LNK_TREAD_T
    mw = vki_mw(o); out = []
    if o.get("vki_link") == "stair_down" or "Stair_Down" in o.get("vki_piece", o.name):
        for j in range(1, VKI_LNK_DN_TREADS + 1):
            yf = VKI_LNK_TOP_Y - j * g_ + g_ + VKI_LNK_OVER
            z = (-r_ * j + (-r_ * (j - 1) - T)) / 2
            out.append((f"down riser {j}", [mw @ Vector((x, yf - 0.005, z)) for x in xs]))
    else:
        for i in range(1, VKI_LNK_RISERS):
            yf = (i - 1) * g_ + VKI_LNK_OVER
            z = (r_ * (i - 1) + r_ * i - T) / 2
            out.append((f"up riser {i}", [mw @ Vector((x, yf - 0.005, z)) for x in xs]))
    return out


def vki_lnk_riser_visibility(sc, o, D, target):
    """fraction of each riser's sample points that the §1 game camera (D, target) sees: {label: fraction}"""
    cam = vki_cam_loc(target, D)
    dg = vki_depsgraph(sc)
    out = {}
    for lab, pts in vki_lnk_riser_points(o):
        out[lab] = round(sum(vki_ray_blocked(sc, cam, p, tol=0.01, dg=dg) is None for p in pts) / len(pts), 2)
    return out


def vki_lnk_pair_check(up=VKI_LNK_UP, dn=VKI_LNK_DN):
    """the down piece lifted one storey (z + 3.0) must put its tread tops exactly on the up flight's top ten treads
    (same origin and rotation = the same physical stair): max distance of the down tread-top vertices to the up
    master's vertices (0 when consistent)"""
    from mathutils.kdtree import KDTree
    U, Dn = bpy.data.objects[up], bpy.data.objects[dn]
    kd = KDTree(len(U.data.vertices))
    for i, v in enumerate(U.data.vertices):
        kd.insert(v.co, i)
    kd.balance()
    worst, n = 0.0, 0
    x0, x1 = VKI_LNK_TREAD_X
    for v in Dn.data.vertices:
        z = v.co.z
        if z < -0.1 and abs(z / VKI_LNK_RISE - round(z / VKI_LNK_RISE)) < 1e-6 and x0 - 1e-6 <= v.co.x <= x1 + 1e-6:
            worst = max(worst, kd.find(v.co + Vector((0, 0, 3.0)))[2]); n += 1
    return round(worst, 6), n


VKI_LNK_RIG = "WS_vki_links_Assembly"


def vki_lnk_q150(i, j):
    return "SM_VKI_Floor_150_Q%d%d" % (i % 2, j % 2)


def vki_lnk_room(coll, x0, stair, floor_cells, style_floor="Flag"):
    """the Townhouse footprint (7 x 5 cells, 10.5 x 7.5) in Timber at (x0, 0): Full west / north / east walls
    with rakes at the south, Cut south wall, Corner posts, rhythm Mid posts at the even nodes (skipped where the
    stair spans the west wall), the §2.3-allowed Mid post at the stair's local (0, 0), Q150 floors on floor_cells,
    the stair at (x0, 3.0) rot 0 (as in Townhouse_F0 / F1)"""
    P = []
    W = "SM_VKI_Wall_Timber_"; Pt = "SM_VKI_Post_Timber_"
    add = lambda n, x, y, r, st=None: P.append(vki_place(coll, n, x, y, r, style=st, walls=[]))
    for n_, y in (("Rake_150_L", 0.0), ("Plain_150A_Full", 1.5), ("Plain_300_Full", 3.0), ("Plain_150A_Full", 6.0)):
        add(W + n_, x0, y, 90)
    for x in (0.0, 3.0, 6.0):
        add(W + "Plain_300_Full", x0 + x, 7.5, 0)
    add(W + "Plain_150A_Full", x0 + 9.0, 7.5, 0)
    for n_, y in (("Plain_150A_Full", 7.5), ("Plain_300_Full", 6.0), ("Plain_150A_Full", 3.0), ("Rake_150_R", 1.5)):
        add(W + n_, x0 + 10.5, y, -90)
    for x in (10.5, 7.5, 4.5):
        add(W + "Plain_300_Cut", x0 + x, 0.0, 180)
    add(W + "Plain_150A_Cut", x0 + 1.5, 0.0, 180)
    add(Pt + "Corner_Full", x0, 7.5, 0); add(Pt + "Corner_Full", x0 + 10.5, 7.5, 0)
    add(Pt + "Corner_Cut", x0, 0.0, 0); add(Pt + "Corner_Cut", x0 + 10.5, 0.0, 0)
    for x in (3.0, 6.0, 9.0):
        add(Pt + "Mid_Full", x0 + x, 7.5, 0); add(Pt + "Mid_Cut", x0 + x, 0.0, 0)
    for y in (3.0, 6.0):
        add(Pt + "Mid_Full", x0 + 10.5, y, 90)
    add(Pt + "Mid_Full", x0, 3.0, 90)                      # the stair's local (0, 0); (0, 6.0) is spanned: skipped
    for c, r in floor_cells:
        x, y = x0 + 1.5 * c, 1.5 * r
        add(vki_lnk_q150(int(round(x / 1.5)), int(round(y / 1.5))), x, y, 0, {"floor": style_floor})
    s = vki_place(coll, stair, x0, 3.0, 0, walls=[])
    return P, s


VKI_LNK_RIG_X = (0.0, 30.0)                                # F0 room (up), F1 room (down)


def vki_lnk_stair_rig():
    """WS_vki_links: two Townhouse-sized Timber rooms, Stair_Up at (0, 3.0) with the Flag floor under the whole
    footprint (F0) and Stair_Down at (30, 3.0) with Boards_NS around it (F1): the pair at the same room-local
    origin and rotation. Returns (objs, up, down); shoot each room with vki_lnk_rig_cam(i)."""
    sc, coll, asm = vki_ws("links")
    for o in list(asm.objects):
        bpy.data.objects.remove(o)
    cells = [(c, r) for c in range(7) for r in range(5)]
    PU, up = vki_lnk_room(asm, VKI_LNK_RIG_X[0], VKI_LNK_UP, cells, "Flag")
    PD, dn = vki_lnk_room(asm, VKI_LNK_RIG_X[1], VKI_LNK_DN, [cr for cr in cells if not (cr[0] == 0 and cr[1] >= 2)],
                          "Boards_NS")
    return PU + PD + [up, dn], up, dn


def vki_lnk_rig_cam(i):
    """§1 fit camera (with the core's far margin) of rig room i: dict(D, target)"""
    x0 = VKI_LNK_RIG_X[i]
    f = vki_fit_camera((x0, 0.0, x0 + 10.5, 7.5), "Timber")
    return dict(D=f["D"], target=f["target"])


VKI_LNK_SPECS = [
    (VKI_LNK_UP, vki_lnk_stair_up, "prop"),
    (VKI_LNK_DN, vki_lnk_stair_down, "prop"),
    ("SM_VKI_Floor_Dais_300", vki_lnk_dais, "floor"),
    ("SM_VKI_FX_WindowPool", vki_lnk_window_pool, "none"),
    ("SM_VKI_Runner_300", vki_lnk_runner_300, "floor"),
    ("SM_VKI_Runner_150", vki_lnk_runner_150, "floor"),
]
VKI_LNK_NAMES = [n for n, _, _ in VKI_LNK_SPECS]
vki_register([(n, fn, {"grime": gr}, "links") for n, fn, gr in VKI_LNK_SPECS])
