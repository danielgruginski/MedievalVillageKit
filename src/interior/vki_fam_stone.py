# ===================== VKI FAM STONE: the Stone (rubble) wall family (§2.2, §3.1, §3.2) -- 21 masters + 4 leaves ====
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (its §10 amendments override earlier sections). Package "stone".
# Loaded by vki_ns() after vki_fam_timber / vki_floors, whose helpers it uses (vki_prism, vki_cut, vki_proj_long,
# vki_hash_off, vki_tim_flame, VKI_TIM_FLAME_PROFILE, VKI_TIM_WIN_SPOT, VKI_LEAF_*). Top-level names: vki_/VKI_ (T18).
#
# Section (class O, T 0.50, H 3.0), piece-local, room on -Y:
#   body   coursed rubble +-0.25 (WALL_A StoneIn on -Y, WALL_B on +Y; a Plaster wall_a style gives limewashed stone),
#          z -0.30 .. coping bottom, grid_cut 0.25, the §2.6 wobble (A 0.020) last; the footing band below z 0 is DRESS
#   coping StoneBlockIn (CAP slot) +-0.28 in 0.75 m units on the piece's own 0.75 grid, bevelled 0.02 so units and
#          pieces meet in V-joints; Cut 0.90-1.00, Full 2.88-3.00 (no band at 0.90 on Full walls); inner units of 300
#          pieces sit up to 12 mm low (§2.6 +-0.006 jitter, downward only so T1's z <= H holds; end units fixed)
#   dressed stone (STONE_BLOCK_IN, bevel 0.02): arch voussoirs, jamb blocks, sills, lintels, quoins -- separate solids
#          embedded in the rubble body and proud of its faces, never coplanar with a body face (T5S)
#   Plain_150B: pop-out stones keyed to T_VKI_StoneIn_stones.json above z 1.2 (<= 0.05 proud) on both faces
#   Rakes: Cut profile for u <= 0.32 from the low end, Full for u >= 1.18, a sloped coping of three tabling stones
#   Posts: Corner = quoin pier of stacked StoneBlockIn blocks (alternate blocks long on X / on Y), Mid = thin dressed
#          pilaster; top faces CAP
# Build: g["vki_ws_build"]("stone", VKI_STO_NAMES); test: g["vki_test_pieces"](VKI_STO_NAMES) -> {}.
import bpy, bmesh, math, json, os, random
from mathutils import Vector, Matrix

VKI_STO_HW = 0.28                   # coping / sill / jamb half width (= CAP_HW, class O)
VKI_STO_CUT = (0.90, 1.00)          # Cut coping (the cut cap band)
VKI_STO_FULL = (2.88, 3.00)         # Full coping (H - 0.12 .. H)
VKI_STO_UNIT = 0.75                 # coping units (§2.2)
VKI_STO_BEV = 0.02                  # dressed-stone bevel: V-joints between units and blocks
VKI_STO_TILE = 1.5                  # UV tile of the coping / dressed stone (T_VKI_StoneBlockIn is painted at t 1.5)
VKI_STO_OPEN = (0.33, 1.17)         # clear opening of every 150 opening piece
VKI_STO_CUT_TO = "SM_VKI_Wall_Stone_Plain_150A_Cut"
VKI_STO_FOOT_TOP = -0.10            # footings under openings stop at the floor-slab bottom (no face in the z 0 plane)
VKI_STO_TUCK = 0.005                # a member that butts into a coping / lintel runs this far into it (T5S)
VKI_STO_FOOT_DARK = 0.22            # extra darkening of the DRESS footing band (below z 0)
VKI_STO_RECESS = 0.010              # jamb blocks stop this far short of the reveal plane (never coplanar with it);
                                    # their bevelled arrises then sit at x 0.300, 5 mm inside a Corner post's T4 margin
                                    # (0.305) -- at 0.305 exactly, float32 rounding at some rig positions failed T4
VKI_STO_X = Vector((1, 0, 0)); VKI_STO_Y = Vector((0, 1, 0)); VKI_STO_Z = Vector((0, 0, 1))

# openings (§3.2). Door: 0.84 wide, round arch spring 1.78 / crown 2.20, voussoirs 0.25-0.29 deep, |y| <= 0.30.
VKI_STO_DOOR = dict(spring=1.78, r=0.42, depths=(0.27, 0.25, 0.28, 0.29, 0.28, 0.25, 0.27), vy=0.30, thr=0.03,
                    jamb_z=(0.0, 0.40, 0.84, 1.30, 1.78), jamb_x=(0.09, 0.17))
# Window: glass x 0.45-1.05 at y +0.10, round head (glass r 0.30 springing 1.95, crown 2.25), splayed to x 0.33-1.17
# at face A (rere-arch r 0.42, crown 2.37), STONE_BLOCK_IN sill 0.88-1.00 (top 1.00), dressed rere-arch ring on face A
VKI_STO_WIN = dict(sill=(0.88, 1.00), spring=1.95, glass=(0.45, 1.05), glass_y=0.10, r_glass=0.30, r_face=0.42,
                   chords=6, depths=(0.20, 0.18, 0.21, 0.22, 0.21, 0.18, 0.20), vy=(-0.30, -0.18),
                   jamb_z=(1.00, 1.46, 1.95), jamb_x=(0.14, 0.21))
# DoorWide_300: clear x 0.60-2.40 (1.80), segmental arch springing 2.40, crown 2.55 (R 2.775 about (1.5, -0.225))
VKI_STO_WIDE = dict(open=(0.60, 2.40), spring=2.40, crown=2.55,
                    depths=(0.24, 0.26, 0.25, 0.27, 0.28, 0.27, 0.25, 0.26, 0.24), vy=0.30,
                    jamb_z=(0.0, 0.44, 0.90, 1.38, 1.88, 2.40), jamb_x=(0.36, 0.44))
VKI_STO_WIDE_LEAF_W = 0.89          # each Leaf_Wide_Cut: x 0.005 .. 0.895 from its hinge (5 mm clear at jamb and meet)
VKI_STO_WIDE160_LEAF_W = 0.795      # each Leaf_Wide160_Cut (the Ashlar pointed DoorWide_300: clear 1.60 m, sockets at
                                    # x 0.70 / 2.30): x 0.005 .. 0.800 from its hinge, the Ashlar engineer's maximum


# ---------------------------------------------------------------- small helpers
def vki_sto_body(k, x0, x1, z0, z1, y0=None, y1=None):
    """rubble wall-body panel (k.body_box: WALL_A / WALL_B faces, grid_cut 0.25, flagged body)"""
    return k.body_box(x0, x1, z0, z1, y0=y0, y1=y1)


def vki_sto_wall_uv(k, fs, mi=None):
    """world-locked WALL_A / WALL_B projection WITHOUT the Stone coping switch (VKIKit.project turns |n.z| > 0.7
    wall faces into STONE_BLOCK_IN): embrasure soffits, pop-out tops and hood slopes keep the wall style (StoneIn or
    a limewash) instead of flipping to dressed stone at some angle"""
    for f in fs:
        f.normal_update()
        n = f.normal
        m = mi if mi is not None else f.material_index
        f.material_index = m
        if abs(n.z) > 0.7:
            U = VKI_STO_X.copy(); V = VKI_STO_Y.copy()
        else:
            U = n.cross(VKI_STO_Z); U.normalize(); V = VKI_STO_Z.copy()
        for l in f.loops:
            p = l.vert.co
            l[k.uv].uv = (p.dot(U) / 1.5, p.dot(V) / 1.5)


def vki_sto_block(k, x0, x1, z0, z1, y0=-VKI_STO_HW, y1=VKI_STO_HW, mi=None, bev=VKI_STO_BEV, top=None, dark=None,
                  key=None):
    """a dressed-stone block (STONE_BLOCK_IN by default) with bevelled arrises; `top`: slot for its upward faces
    (CAP); `dark`: vki_dark tone (None: a small hashed tone per block so neighbouring stones differ)"""
    mi = VKI_STONE_BLOCK_IN if mi is None else mi
    if x1 - x0 < 1e-6 or z1 - z0 < 1e-6 or y1 - y0 < 1e-6:
        return []
    c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); sz = (x1 - x0, y1 - y0, z1 - z0)
    vs = list(set(k.box(c, sz, mi, bevel=bev, tile=VKI_STO_TILE)))
    if top is not None:
        vki_sto_top(k, vs, top, c)
    d = dark if dark is not None else 0.10 * vki_hash01(int(round(c[0] * 97)), int(round(c[2] * 89)),
                                                        vki_seed("Stone|tone|%s" % (key or "")))
    if d > 0:
        k.set_dark(vs, d)
    return vs


def vki_sto_top(k, vs, mi, c, nz=0.65):
    """re-project the upward faces (top + chamfers) of a block into slot mi (CAP), planar from above, t 1.5"""
    k.bm.normal_update()
    fs = [f for f in vki_faces_of(vs) if f.normal.z > nz]
    k.project(fs, mi, axes=[VKI_STO_X.copy(), VKI_STO_Y.copy(), VKI_STO_Z.copy()], sizes=[1.0, 0.3, 0.1],
              offset=vki_hash_off(c), tile=VKI_STO_TILE)
    return fs


def vki_sto_cop_dz(L, a, b, zt):
    """coping unit [a, b] height offset: 0 for units at a piece end (fixed, so every end profile is identical, T2),
    else -2 J .. 0 (±J about -J, J = the family's coping_jitter 0.006); deterministic (integer hash, crc32 seed)"""
    if a < 1e-6 or b > L - 1e-6 or not VKI_FLAGS.get("sag", True):
        return 0.0
    J = VKI_FAMILIES["Stone"].get("coping_jitter", 0.006)
    h = vki_hash01(int(round(a * 100)), int(round(zt * 100)), vki_seed("Stone|coping|%g" % L))
    return -J * (2.0 * h)


def vki_sto_coping(k, x0, x1, zb, zt, L, fixed=False):
    """StoneBlockIn coping (the CAP slot: M_VKI_StoneBlockIn on Stone masters, restyled by a `cap` style) over
    [x0, x1] in 0.75 m units on the piece's 0.75 grid; bevelled, so units meet in V-joints"""
    cuts = [x0] + [VKI_STO_UNIT * i for i in range(1, 5) if x0 + 1e-6 < VKI_STO_UNIT * i < x1 - 1e-6] + [x1]
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        dz = 0.0 if fixed else vki_sto_cop_dz(L, a, b, zt)
        out.append(vki_sto_block(k, a, b, zb, zt + dz, mi=VKI_CAP, key="cop"))
    return out


def vki_sto_reproject_body(k, fs=None):
    """determinism (T16): recompute the world-locked planar UVs of the wall-body faces (WALL_A / WALL_B, and
    STONE_BLOCK_IN faces the coping switch made of horizontal body faces) from their final vertex positions. The
    panels are projected before grid_cut / vki_cut split them, and bisect interpolates the new loops' UVs in an
    order that follows BMesh set iteration, so two builds could differ by ~4e-7 in UV. Same formulas as
    VKIKit.project (t 1.5, zero offset), so nothing moves; only the rounding becomes exact."""
    k.bm.normal_update()
    if fs is None:
        fs = [f for f in k.bm.faces if all(v[k.body] for v in f.verts)]
    for f in fs:
        m = f.material_index
        if m not in (VKI_WALL_A, VKI_WALL_B, VKI_STONE_BLOCK_IN):
            continue
        n = f.normal
        if abs(n.z) > 0.7:
            U = VKI_STO_X.copy(); V = VKI_STO_Y.copy()
        else:
            U = n.cross(VKI_STO_Z); U.normalize(); V = VKI_STO_Z.copy()
        for l in f.loops:
            p = l.vert.co
            l[k.uv].uv = (p.dot(U) / 1.5, p.dot(V) / 1.5)


def vki_sto_body_finish(k):
    """call after every body exists (before wobble): exact world-locked body UVs (vki_sto_reproject_body); the
    footing band below the floor (body +-Y faces with every vertex at z <= 0) becomes DRESS at t 1.5 (continuous
    across pieces) and darkens, so a limewash style never shows a pale band under the floor on the south wall's outer
    face (the Timber rule, vki_tim_body_finish)"""
    vki_sto_reproject_body(k)
    k.bm.normal_update()
    for f in list(k.bm.faces):
        if f.material_index not in (VKI_WALL_A, VKI_WALL_B) or not all(v[k.body] for v in f.verts):
            continue
        if abs(f.normal.y) < 0.7 or max(v.co.z for v in f.verts) > 1e-6:
            continue
        k.project([f], DRESS, tile=1.5)
        for v in f.verts:
            k.set_dark([v], VKI_STO_FOOT_DARK * vki_smoothstep(0.0, -0.15, v.co.z) + 0.08)


def vki_sto_hexa(k, pts, mi):
    """closed convex hexahedron: bottom quad pts[0:4], top quad pts[4:8] (top i above bottom i); planar faces"""
    vs = [k.bm.verts.new(Vector(p)) for p in pts]
    fs = [k.bm.faces.new([vs[i] for i in q]) for q in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2),
                                                       (2, 6, 7, 3), (3, 7, 4, 0))]
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.material_index = mi
    k.bm.normal_update()
    return vs, fs


VKI_STO_RING_BEV = 0.015           # voussoir bevel: a springer's corner at the reveal (x 0.33) bevels to x 0.315, just
                                    # outside a Corner post's node square (0.31) -- 0.02 put vertices at 0.31, inside
                                    # the square but not 5 mm inside the post (T4, rig DoorL)


def vki_sto_ring(k, cx, cz, r_in, depths, a0, a1, y0, y1, mi=None, bev=VKI_STO_RING_BEV, key="arch"):
    """voussoirs from angle a0 to a1 (radians about (cx, cz) in the x-z plane), one per depth (radial), extruded
    y0..y1, bevelled (V-joints); returns [verts per voussoir]"""
    mi = VKI_STONE_BLOCK_IN if mi is None else mi
    n = len(depths)
    out = []
    for i, dp in enumerate(depths):
        t0 = a0 + (a1 - a0) * i / n; t1 = a0 + (a1 - a0) * (i + 1) / n
        P = lambda t, r: (cx + math.cos(t) * r, cz + math.sin(t) * r)
        poly = [P(t0, r_in), P(t1, r_in), P(t1, r_in + dp), P(t0, r_in + dp)]
        vs, fs = vki_prism(k, poly, y0, y1, mi, axis="y", bevel=bev, project=False)
        k.project(fs, mi, offset=vki_hash_off((cx + 0.37 * i, y0, cz + r_in)), tile=VKI_STO_TILE)
        k.set_dark(vs, 0.10 * vki_hash01(i, int(round(cz * 100)), vki_seed("Stone|tone|" + key)))
        out.append(vs)
    return out


def vki_sto_strips(k, x0, x1, zfn, ztop, xs, y0=None, y1=None):
    """rubble body over an arch: vertical strips between consecutive xs whose bottoms follow zfn(x) (a polyline
    buried inside the voussoir ring) and whose tops are at ztop; flagged body, WALL_B on +Y; grid_cut 0.25"""
    y0 = -k.T / 2 if y0 is None else y0
    y1 = k.T / 2 if y1 is None else y1
    before = set(k.bm.verts)
    for a, b in zip(xs[:-1], xs[1:]):
        vs, fs = vki_prism(k, [(a, zfn(a)), (b, zfn(b)), (b, ztop), (a, ztop)], y0, y1, VKI_WALL_A, axis="y")
        for f in fs:
            if f.normal.y > 0.7:
                k.project([f], VKI_WALL_B)
        grid_cut(k, vs, 0.25)
    new = [v for v in k.bm.verts if v not in before]
    k.mark_body(new)
    return new


# ---------------------------------------------------------------- pop-out stones (Plain_150B, §2.2 / §4.2)
VKI_STO_STONES_JSON = os.path.join(VKI_ROOT, "assets", "textures", "T_VKI_StoneIn_stones.json")
# the JSON as written by vki_gen_stone_in (2026-09-26); used when the file cannot be read
VKI_STO_STONES_EMBED = [
    dict(u=0.29868999, v=0.14852252, w=0.63589662, h=0.44556757, lab=0),
    dict(u=0.66918088, v=0.14852252, w=0.47557607, h=0.44556757, lab=1),
    dict(u=0.95721536, v=0.14852252, w=0.38852730, h=0.44556757, lab=2),
    dict(u=0.29918351, v=0.40372183, w=0.49903986, h=0.32003035, lab=3),
    dict(u=0.54962243, v=0.40372183, w=0.25227693, h=0.32003035, lab=4),
    dict(u=0.75938482, v=0.40372183, w=0.37701020, h=0.32003035, lab=5),
    dict(u=0.00894590, v=0.40372183, w=0.37167299, h=0.32003035, lab=6),
    dict(u=0.17378597, v=0.65178821, w=0.49608138, h=0.42416879, lab=7),
    dict(u=0.54887658, v=0.65178821, w=0.62919039, h=0.42416879, lab=8),
    dict(u=0.88351607, v=0.65178821, w=0.37472820, h=0.42416879, lab=9),
    dict(u=0.28882669, v=0.89658890, w=0.35644624, h=0.31023329, lab=10),
    dict(u=0.54810575, v=0.89658890, w=0.42139086, h=0.31023329, lab=11),
    dict(u=0.92929035, v=0.89658890, w=0.72216290, h=0.31023329, lab=12)]
VKI_STO_POP_Z = (1.20, 2.80)        # pop-outs lie between these heights (above 1.2, clear of the Full coping)
VKI_STO_POP_DEPTH = (0.040, 0.050)  # proud of the nominal face (T1 allows 0.06): fronts at |y| 0.29-0.30, up to 15 mm
                                    # past the proud line (0.285) -- keep wall-backed props taller than 1.2 m and
                                    # wall-hung props off Plain_150B (vki_popout_note)


def vki_sto_stones():
    try:
        with open(VKI_STO_STONES_JSON, encoding="utf8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return VKI_STO_STONES_EMBED


def vki_sto_pop_sites(face="A", L=1.5):
    """painted stones that may pop out in the first 1.5 m span. World-locked t 1.5: face A (-Y) maps u = -x / 1.5,
    face B (+Y) u = x / 1.5, v = z / 1.5 (+k). A stone qualifies when the WHOLE painted stone keeps NODE_FLAT from
    both nodes (x in [0.32 + w/2, 1.18 - w/2], §4.2) and its 0.9 w x 0.9 h pop-out lies inside VKI_STO_POP_Z"""
    T = 1.5
    out = []
    for s in vki_sto_stones():
        x = ((-T * s["u"]) if face == "A" else (T * s["u"])) % T
        if not (VKI_NODE_FLAT + s["w"] / 2 - 1e-6 <= x <= T - VKI_NODE_FLAT - s["w"] / 2 + 1e-6):
            continue
        for kk in range(3):
            z = T * s["v"] + T * kk
            w9, h9 = 0.9 * s["w"], 0.9 * s["h"]
            if z - h9 / 2 >= VKI_STO_POP_Z[0] - 1e-6 and z + h9 / 2 <= VKI_STO_POP_Z[1] + 1e-6:
                out.append(dict(x=x, z=z, w=w9, h=h9, lab=int(s["lab"])))
    return out


def vki_sto_popout(k, x, z, w, h, face, depth):
    """one pop-out stone: a pillowed slab -- a rounded-rectangle back outline (3 segments per corner) buried 12 mm in
    the body, a middle ring at 60 % of the depth inset 8 mm, a front ring inset 20 mm, `depth` proud of the nominal
    face. Every face is the wall slot of its face (WALL_A on A, WALL_B on B, so a limewash style covers it too) with
    the world-locked planar UV of the wall (u = -+x / 1.5, v = z / 1.5): the front shows exactly the painted stone
    behind it; the flanks sample the stone's interior. Rounded and pillowed, it reads as a stone standing proud (and
    as a stone under the wash on a limewashed wall) instead of an octagonal plaque."""
    sgn = -1.0 if face == "A" else 1.0
    T2 = k.T / 2
    ys = (sgn * (T2 - 0.012), sgn * (T2 + 0.6 * depth), sgn * (T2 + depth))
    ins = (0.0, 0.008, 0.020)
    r0 = min(w, h) * 0.26

    def rrect(hw, hh, r):
        pts = []
        for cxs, czs, a0_ in ((1, 1, 0.0), (-1, 1, 0.5 * math.pi), (-1, -1, math.pi), (1, -1, 1.5 * math.pi)):
            ccx, ccz = x + cxs * (hw - r), z + czs * (hh - r)
            for j in range(4):
                a = a0_ + 0.5 * math.pi * j / 3
                pts.append((ccx + math.cos(a) * r, ccz + math.sin(a) * r))
        return pts
    rings = []
    for yy, d in zip(ys, ins):
        rings.append([k.bm.verts.new((p[0], yy, p[1])) for p in rrect(w / 2 - d, h / 2 - d, max(r0 - d * 0.5, 0.01))])
    n = len(rings[0])
    caps = [k.bm.faces.new(rings[0]), k.bm.faces.new(rings[-1][::-1])]
    sides = []
    for A, B in zip(rings[:-1], rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            sides.append(k.bm.faces.new((A[i], A[j], B[j], B[i])))
    fs = caps + sides
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    mi = VKI_WALL_A if face == "A" else VKI_WALL_B
    for f in fs:
        f.material_index = mi
        q = 1.0 if f in caps else 0.55
        for l in f.loops:
            p = l.vert.co
            px, pz = x + (p.x - x) * q, z + (p.z - z) * q
            l[k.uv].uv = ((sgn * px) / 1.5, pz / 1.5)
        f.smooth = f not in caps
    return [v for rg in rings for v in rg]


def vki_sto_popouts(k):
    n = 0
    for face in ("A", "B"):
        for s in vki_sto_pop_sites(face):
            d = VKI_STO_POP_DEPTH[0] + (VKI_STO_POP_DEPTH[1] - VKI_STO_POP_DEPTH[0]) * \
                vki_hash01(s["lab"], 7, vki_seed("Stone|pop|" + face))
            vki_sto_popout(k, s["x"], s["z"], s["w"], s["h"], face, d)
            n += 1
    return n


# ---------------------------------------------------------------- Plain (150A, 150B, 300), Full and Cut
def vki_sto_plain(k, L, height, variant="A", popouts=False):
    full = height == "Full"
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    vki_sto_body(k, 0.0, L, VKI_FOOT_Z, zb)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    pops = vki_sto_popouts(k) if popouts else 0
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", variant, holes=[], top_body_fn=lambda x: zb)
    k.meta.update(vki_class="wall")
    if variant == "B":
        k.meta.update(vki_cut_to=VKI_STO_CUT_TO, vki_popouts=pops,
                      vki_popout_note="pop-out stones up to 0.05 proud of both faces between z 1.2 and 2.7, x 0.45-1.05:"
                                      " keep wall_hung props and wall-backed props taller than 1.2 m off this piece")


def vki_sto_plain_150a_full(k): vki_sto_plain(k, 1.5, "Full", "A")
def vki_sto_plain_150a_cut(k): vki_sto_plain(k, 1.5, "Cut", "A")
def vki_sto_plain_150b_full(k): vki_sto_plain(k, 1.5, "Full", "B", popouts=True)
def vki_sto_plain_300_full(k): vki_sto_plain(k, 3.0, "Full", "A")
def vki_sto_plain_300_cut(k): vki_sto_plain(k, 3.0, "Cut", "A")


# ---------------------------------------------------------------- Rake_150_L / _R (§2.4)
VKI_STO_RAKE = dict(lo=0.32, hi=1.18, vt=0.30, stones=3)   # sloped coping: 0.30 vertical = 0.12 square to the slope
                                                            # (as thick as the flat coping), three tabling stones


def vki_sto_rake(k, side):
    """Cut profile for u <= 0.32 from the low end (body to 0.90 + a Cut coping unit), Full profile for u >= 1.18
    (body to 2.88 + a Full coping unit), a sloped coping of three tabling stones between (top line (0.32, 1.00) ->
    (1.18, 3.00), 66.7 deg, 0.30 thick vertically = 0.12 square to the slope, joints square to the slope). _L: low end at local x = 0 (west
    walls); _R: low end at x = L (east walls). u = distance from the low end."""
    L = 1.5
    R = VKI_STO_RAKE
    lo, hi = R["lo"], R["hi"]
    zb0, zt0 = VKI_STO_CUT; zb1, zt1 = VKI_STO_FULL
    X = (lambda u: u) if side == "L" else (lambda u: L - u)

    def span(u0, u1):
        return (min(X(u0), X(u1)), max(X(u0), X(u1)))

    def poly(pts):
        return [(X(u), z) for u, z in pts]
    slope = (zt1 - zt0) / (hi - lo)
    ztop = lambda u: zt0 + slope * (u - lo)
    zcb = lambda u: ztop(u) - R["vt"]                                  # sloped coping bottom
    zbody = lambda u: zb0 + (zb1 - zb0) * (u - lo) / (hi - lo)         # body top, inside the sloped coping
    # body: low Cut part, sloped part, high Full part. The flat parts reach 5 mm past lo / hi (still outside the
    # node zones), so the sloped prism's end faces lie 5 mm off the tabling stones' end faces (T5S)
    tk = VKI_STO_TUCK
    vki_sto_body(k, *span(0.0, lo + tk), VKI_FOOT_Z, zb0)
    vki_sto_body(k, *span(hi - tk, L), VKI_FOOT_Z, zb1)
    before = set(k.bm.verts)
    vs, fs = vki_prism(k, poly([(lo + tk, VKI_FOOT_Z), (hi - tk, VKI_FOOT_Z), (hi - tk, zbody(hi - tk)),
                                (lo + tk, zbody(lo + tk))]), -k.T / 2, k.T / 2, VKI_WALL_A, axis="y")
    for f in fs:
        if f.normal.y > 0.7:
            k.project([f], VKI_WALL_B)
    grid_cut(k, vs, 0.25)
    k.mark_body([v for v in k.bm.verts if v not in before])
    # flat coping units at both ends (fixed: the end profiles)
    vki_sto_coping(k, *span(0.0, lo), zb0, zt0, L, fixed=True)
    vki_sto_coping(k, *span(hi, L), zb1, zt1, L, fixed=True)
    # sloped coping: stones between joints square to the slope; the first starts on the vertical u = lo, the last
    # ends on u = hi (both faces butt the flat units / the body there, opposite-facing)
    th = math.atan2(zt1 - zt0, hi - lo)
    s = Vector((math.cos(th), math.sin(th))); m = Vector((math.sin(th), -math.cos(th)))
    w = R["vt"] * math.cos(th)                                         # thickness square to the slope
    P0 = Vector((lo, zt0))
    S = (Vector((hi, zt1)) - P0).length
    n = R["stones"]
    tops = [P0 + s * (S * j / n) for j in range(1, n)]
    joints = [(t, t + m * w) for t in tops]                            # (top point, bottom point) of each joint
    sdir = Vector((X(1.0) - X(0.0), 0.0, 0.0)) * math.cos(th) + Vector((0.0, 0.0, math.sin(th)))
    for j in range(n):
        a = [(lo, zt0), (lo, zcb(lo))] if j == 0 else [tuple(joints[j - 1][0]), tuple(joints[j - 1][1])]
        b = [(hi, zcb(hi)), (hi, zt1)] if j == n - 1 else [tuple(joints[j][1]), tuple(joints[j][0])]
        pts = [a[1], b[0], b[1], a[0]]                                 # bottom-low, bottom-high, top-high, top-low
        vs, fs = vki_prism(k, poly(pts), -VKI_STO_HW, VKI_STO_HW, VKI_CAP, axis="y", bevel=VKI_STO_BEV,
                           project=False)
        off = vki_hash_off((0.4 * j, 0.0, 1.0 + j))
        for f in fs:                                                   # grain along the slope, t 1.5
            f.normal_update()
            sd = f.normal.cross(sdir)
            sd = sd.normalized() if sd.length > 1e-6 else VKI_STO_Y.copy()
            k.project([f], VKI_CAP, axes=[sdir.normalized(), sd, f.normal.copy()], sizes=[1.0, 0.3, 0.1],
                      offset=off, tile=VKI_STO_TILE)
        k.set_dark(vs, 0.08 * vki_hash01(j, 3, vki_seed("Stone|tone|rake")))
    tbf = lambda x: (zb0 if (x if side == "L" else L - x) <= lo else
                     (zb1 if (x if side == "L" else L - x) >= hi else
                      min(zbody(x if side == "L" else L - x), zcb(x if side == "L" else L - x))))
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", "A", holes=[], top_body_fn=tbf)
    k.meta.update(vki_class="wall", vki_cut_to=VKI_STO_CUT_TO, vki_rake_low="x0" if side == "L" else "xL",
                  vki_rake_slope_deg=round(math.degrees(th), 2))


def vki_sto_rake_l(k): vki_sto_rake(k, "L")
def vki_sto_rake_r(k): vki_sto_rake(k, "R")


# ---------------------------------------------------------------- Window_150 (§3.2, round head)
def vki_sto_window(k, height):
    """Full: glass x 0.45-1.05 at y +0.10 (closed 0.02 prism, WINDOW) with a round head (r 0.30 springing 1.95,
    crown 2.25), splayed to x 0.33-1.17 at face A where the rere-arch is r 0.42 (crown 2.37); the conical soffit and
    the splayed reveals keep the wall style (WALL_A, no coping switch); STONE_BLOCK_IN sill 0.88-1.00 with a CAP top;
    a dressed ring of 7 voussoirs round the rere-arch and two jamb blocks a side on face A; iron glazing cross.
    Cut: plain cut wall whose coping over x 0.33-1.17 becomes the same sill slab (|y| <= 0.28, CAP top 1.00), the
    coping units running 0.04 into it; plus a light-pool anchor. Full = Cut below 0.65 (same body split)."""
    L = 1.5
    full = height == "Full"
    W = VKI_STO_WIN
    x0, x1 = VKI_STO_OPEN
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    T2 = k.T / 2
    s0, s1 = W["sill"]
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)                                       # piers
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, s0)                                        # under the sill
    sill = vki_sto_block(k, x0, x1, s0, s1, -VKI_STO_HW, VKI_STO_HW, top=VKI_CAP, dark=0.0)
    if full:
        g0, g1 = W["glass"]; gy = W["glass_y"]; sp = W["spring"]
        rg, rf = W["r_glass"], W["r_face"]
        cx = (x0 + x1) / 2
        # splayed reveals (face A 0.33 -> glass 0.45, then straight to face B), sill top to the coping bottom
        before = set(k.bm.verts)
        for pl in ([(x0, -T2), (g0, gy), (g0, T2), (x0, T2)], [(x1, -T2), (x1, T2), (g1, T2), (g1, gy)]):
            vs, fs = vki_prism(k, pl, s1, zb, VKI_WALL_A, axis="z")
            for f in fs:
                if f.normal.y > 0.7:
                    k.project([f], VKI_WALL_B)
            vs = vki_cut(k, vs, zs=[z for z in (1.25, 1.5, 1.75) if z < zb])
            vki_sto_wall_uv(k, [f for f in vki_faces_of(vs) if abs(f.normal.z) < 0.7])
        # head: per chord a splayed hexahedron (face A arch -> glass arch, planar conical strip) + an outer prism
        nch = W["chords"]
        ang = [math.pi - math.pi * i / nch for i in range(nch + 1)]
        A = [Vector((cx + rf * math.cos(a), -T2, sp + rf * math.sin(a))) for a in ang]
        G = [Vector((cx + rg * math.cos(a), gy, sp + rg * math.sin(a))) for a in ang]
        for i in range(nch):
            top = lambda p: Vector((p.x, p.y, zb))
            vs, fs = vki_sto_hexa(k, [A[i], A[i + 1], G[i + 1], G[i], top(A[i]), top(A[i + 1]), top(G[i + 1]),
                                      top(G[i])], VKI_WALL_A)
            vki_sto_wall_uv(k, fs)
            vs2, fs2 = vki_prism(k, [(G[i].x, G[i].z), (G[i + 1].x, G[i + 1].z), (G[i + 1].x, zb), (G[i].x, zb)],
                                 gy, T2, VKI_WALL_A, axis="y", project=False)
            vki_sto_wall_uv(k, fs2)
            for f in fs2:
                if f.normal.y > 0.7:
                    f.material_index = VKI_WALL_B
        k.mark_body([v for v in k.bm.verts if v not in before])
        # glass: round-headed closed prism, embedded 1 cm in the sill, reveals and soffit
        gp = [(g0 - 0.01, s1 - 0.01), (g1 + 0.01, s1 - 0.01)] + \
             [(cx + (rg + 0.01) * math.cos(math.pi * i / 12), sp + (rg + 0.01) * math.sin(math.pi * i / 12))
              for i in range(13)]
        vki_prism(k, gp, gy - 0.01, gy + 0.01, WINDOW, axis="y")
        # iron glazing cross on the room side of the glass (embedded in the soffit / reveals / sill)
        k.box((cx, 0.06, (s1 - 0.005 + 2.275) / 2), (0.035, 0.03, 2.275 - s1 + 0.005), IRON, bevel=0.006)
        k.box((cx, 0.066, 1.66), (0.645, 0.03, 0.035), IRON, bevel=0.006)     # 6 mm behind the upright (T5S)
        # dressed rere-arch ring and jamb blocks on face A (proud 5 cm, embedded 7 cm)
        vy0, vy1 = W["vy"]
        vki_sto_ring(k, cx, sp, rf, W["depths"], math.pi, 0.0, vy0, vy1, key="win")
        jz = W["jamb_z"]
        for i in range(len(jz) - 1):
            xa = W["jamb_x"][i % 2]
            vki_sto_block(k, xa, x0 - VKI_STO_RECESS, jz[i], jz[i + 1], vy0, vy1, key="winj%d" % i)
            vki_sto_block(k, x1 + VKI_STO_RECESS, L - xa, jz[i], jz[i + 1], vy0, vy1, key="winj%d" % (i + 5))
        vki_sto_coping(k, 0.0, L, zb, zt, L)
        crown = sp + rf
        holes = [(x0, s0, x1, crown + 0.03)]
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": s1, "z1": round(crown, 4), "head": "round",
                                   "glass_crown": round(sp + rg, 4)},
                      vki_lights=[dict(type="SPOT", role="window", pos=list(VKI_TIM_WIN_SPOT["pos"]),
                                       aim=list(VKI_TIM_WIN_SPOT["aim"]), cone=VKI_TIM_WIN_SPOT["cone"],
                                       blend=VKI_TIM_WIN_SPOT["blend"], radius=VKI_TIM_WIN_SPOT["radius"],
                                       w_day=VKI_TIM_WIN_SPOT["w_day"], w_night=VKI_TIM_WIN_SPOT["w_night"],
                                       color_day=[.82, .88, 1.0], color_night=[.62, .70, 1.0], shadows=1)])
    else:
        # coping units run 0.04 into the sill slab: their bevelled tops end at 0.35 / 1.15 where the slab's top
        # starts (no overlap, no open V-slot beside the sill; the Timber rule)
        vki_sto_coping(k, 0.0, x0 + 0.04, zb, zt, L, fixed=True)
        vki_sto_coping(k, x1 - 0.04, L, zb, zt, L, fixed=True)
        holes = []
        k.meta.update(vki_opening={"x0": x0, "x1": x1, "z0": s1, "z1": 2.37, "cut": 1},
                      vki_light_pool=[0.75, -1.20, 0.0])
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", "A", holes=holes, top_body_fn=lambda x: zb)
    k.meta.update(vki_class="wall")


def vki_sto_window_full(k): vki_sto_window(k, "Full")
def vki_sto_window_cut(k): vki_sto_window(k, "Cut")


# ---------------------------------------------------------------- Door_150 (§3.2, round arch)
def vki_sto_jambs(k, xl, xr, zs, xs, y0=-VKI_STO_HW, y1=VKI_STO_HW, key="j"):
    """dressed jamb blocks either side of an opening [xl, xr]: alternating long / short (quoin-like) blocks between
    the heights zs, stopping VKI_STO_RECESS short of the reveal plane (the rubble reveal stays one clean face)"""
    for i in range(len(zs) - 1):
        w = xl - xs[i % 2]
        vki_sto_block(k, xl - w, xl - VKI_STO_RECESS, zs[i], zs[i + 1], y0, y1, key="%sl%d" % (key, i))
        vki_sto_block(k, xr + VKI_STO_RECESS, xr + w, zs[i], zs[i + 1], y0, y1, key="%sr%d" % (key, i))


def vki_sto_door(k, height):
    """clear opening x 0.33-1.17; Full: round arch springing 1.78, crown 2.20 (7 STONE_BLOCK_IN voussoirs 0.25-0.29
    deep, |y| <= 0.30, reaching x 0.04-1.46), dressed jamb blocks (|y| <= 0.28) either side, rubble reveals,
    DRESS threshold z 0-0.03 (|y| <= 0.28). Cut: the jambs stop 5 mm inside one continuous coping unit from the
    piece end to the opening (x 0-0.33 / 1.17-1.5), so the cap wraps the reveal; the reveal is the rubble body face
    (WALL_A: StoneIn or the zone's limewash, a mid value, §10.2)."""
    L = 1.5
    full = height == "Full"
    D = VKI_STO_DOOR
    x0, x1 = VKI_STO_OPEN
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    T2 = k.T / 2
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)                                       # piers (reveal = their end face)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)                           # footing under the threshold
    vki_sto_block(k, x0, x1, 0.0, D["thr"], -VKI_STO_HW, VKI_STO_HW, mi=DRESS, bev=0.01, dark=0.06)   # threshold
    if full:
        jz = D["jamb_z"]
        vki_sto_jambs(k, x0, x1, jz, D["jamb_x"], key="dj")
        cx, sp, r = (x0 + x1) / 2, D["spring"], D["r"]
        rb = r + 0.10                                                              # strip bottoms, inside the ring
        zfn = lambda x: sp + math.sqrt(max(rb * rb - (x - cx) ** 2, 0.0))
        xs = [x0, 0.43, 0.54, 0.645, cx, 0.855, 0.96, 1.07, x1]
        vki_sto_strips(k, x0, x1, zfn, zb, xs)
        vki_sto_ring(k, cx, sp, r, D["depths"], math.pi, 0.0, -D["vy"], D["vy"], key="door")
        vki_sto_coping(k, 0.0, L, zb, zt, L)
        holes = [(x0, 0.0, x1, sp + r)]
        z1 = sp + r
    else:
        vki_sto_jambs(k, x0, x1, (0.0, D["jamb_z"][1], zb + VKI_STO_TUCK), D["jamb_x"], key="dj")
        vki_sto_coping(k, 0.0, x0, zb, zt, L, fixed=True)
        vki_sto_coping(k, x1, L, zb, zt, L, fixed=True)
        holes = [(x0, 0.0, x1, zt)]
        z1 = zt
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", "A", holes=holes, top_body_fn=lambda x: zb)
    k.meta.update(vki_nav="door", vki_nav_open=[x0, x1])
    k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": round(z1, 4),
                                                 "head": "round" if full else "cut"},
                  vki_trigger=[0.75, -0.65, 1.0, 0.9, 0.8, 2.0], vki_leaf_socket=[x0, -T2 + 0.05, 0.0],
                  vki_leaf_open_deg=90, vki_leaf="SM_VKI_Leaf_Plank_" + height, vki_spawn_local=[0.75, -1.60],
                  vki_prompt_local=[0.75, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])


def vki_sto_door_full(k): vki_sto_door(k, "Full")
def vki_sto_door_cut(k): vki_sto_door(k, "Cut")


# ---------------------------------------------------------------- DoorWide_300 (§3.2, segmental arch)
def vki_sto_door_wide(k, height):
    """clear x 0.60-2.40 (1.80); Full: segmental arch springing 2.40, crown 2.55 (R 2.775 about (1.5, -0.225)),
    9 voussoirs 0.24-0.28 deep (|y| <= 0.30), dressed jambs (|y| <= 0.28), rubble reveals, DRESS threshold.
    Cut: the lower metre -- jambs 5 mm into the coping units x 0-0.60 / 2.40-3.0 that wrap the reveals; exits carry
    Leaf_Wide_Cut_L (hinge x 0.60, extends +X) and Leaf_Wide_Cut_R (hinge x 2.40, extends -X)."""
    L = 3.0
    full = height == "Full"
    D = VKI_STO_WIDE
    x0, x1 = D["open"]
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    T2 = k.T / 2
    vki_sto_body(k, 0.0, x0, VKI_FOOT_Z, zb)
    vki_sto_body(k, x1, L, VKI_FOOT_Z, zb)
    vki_sto_body(k, x0, x1, VKI_FOOT_Z, VKI_STO_FOOT_TOP)
    for a, b in ((x0, (x0 + x1) / 2 - 0.005), ((x0 + x1) / 2 + 0.005, x1)):         # two threshold slabs
        vki_sto_block(k, a, b, 0.0, VKI_STO_DOOR["thr"], -VKI_STO_HW, VKI_STO_HW, mi=DRESS, bev=0.01, dark=0.06)
    if full:
        vki_sto_jambs(k, x0, x1, D["jamb_z"], D["jamb_x"], key="wj")
        cx = (x0 + x1) / 2
        half = (x1 - x0) / 2
        rise = D["crown"] - D["spring"]
        R = (half * half + rise * rise) / (2 * rise)
        cz = D["crown"] - R
        a0 = math.atan2(D["spring"] - cz, x0 - cx); a1 = math.atan2(D["spring"] - cz, x1 - cx)
        rb = R + 0.10
        zfn = lambda x: cz + math.sqrt(max(rb * rb - (x - cx) ** 2, 0.0))
        xs = [x0 + (x1 - x0) * i / 6 for i in range(7)]
        vki_sto_strips(k, x0, x1, zfn, zb, xs)
        vki_sto_ring(k, cx, cz, R, D["depths"], a0, a1, -D["vy"], D["vy"], key="wide")
        vki_sto_coping(k, 0.0, L, zb, zt, L)
        holes = [(x0, 0.0, x1, D["crown"])]
        z1 = D["crown"]
    else:
        vki_sto_jambs(k, x0, x1, (0.0, D["jamb_z"][1], zb + VKI_STO_TUCK), D["jamb_x"], key="wj")
        vki_sto_coping(k, 0.0, x0, zb, zt, L, fixed=True)
        vki_sto_coping(k, x1, L, zb, zt, L, fixed=True)
        holes = [(x0, 0.0, x1, zt)]
        z1 = zt
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", "A", holes=holes, top_body_fn=lambda x: zb)
    k.meta.update(vki_nav="door", vki_nav_open=[x0, x1])
    k.meta.update(vki_class="wall", vki_opening={"x0": x0, "x1": x1, "z0": 0.0, "z1": round(z1, 4),
                                                 "head": "segmental" if full else "cut"},
                  vki_trigger=[1.5, -0.65, 1.0, 1.9, 0.8, 2.0],
                  vki_leaf_socket=[[x0, -T2 + 0.05, 0.0], [x1, -T2 + 0.05, 0.0]], vki_leaf_open_deg=90,
                  vki_spawn_local=[1.5, -1.60], vki_prompt_local=[1.5, -0.30, 1.40],
                  vki_collider=[[x0 / 2, 0.0, 1.1, x0, k.T, 2.2], [(x1 + L) / 2, 0.0, 1.1, L - x1, k.T, 2.2]])
    if not full:
        k.meta.update(vki_leaf=["SM_VKI_Leaf_Wide_Cut_L", "SM_VKI_Leaf_Wide_Cut_R"],
                      vki_leaf_note="L at vki_leaf_socket[0] (extends +X), R at [1] (extends -X), both with the "
                                    "door's rotation; the Apron goes at door origin + R(rot) @ (0.75, 0)")


def vki_sto_door_wide_full(k): vki_sto_door_wide(k, "Full")
def vki_sto_door_wide_cut(k): vki_sto_door_wide(k, "Cut")


# ---------------------------------------------------------------- fire helpers (Hearth / Forge)
def vki_sto_embers(k, cx, cy, z, n, rx, ry, seed, core=0.42, rmin=0.045, rmax=0.07, hmax=1.0):
    """GLOW ember lumps (icosahedra) with vki_heat falling from the fire centre (M_VKI_GlowIn: core -> rim); hmax
    caps the heat (1.0 = the white-hot core colour; coal beds use less so they read orange-red, not cream)"""
    rnd = random.Random(seed)
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3); rr = rnd.uniform(0.15, 1.0)
        c = Vector((cx + math.cos(a) * rr * rx, cy + math.sin(a) * rr * ry, z))
        vs = _ico(k, c, rnd.uniform(rmin, rmax), GLOW, scale=(1.0, 1.0, 0.55), sub=1, jit=0.008, seed=seed + 7 + i)
        for v in vs:
            k.set_heat([v], hmax * vki_clamp(1.0 - (v.co - Vector((cx, cy, z - 0.02))).length / core))
        k.project(vki_faces_of(vs), GLOW)


def vki_sto_logs(k, cx, specs):
    """charred oak logs (x-aligned): (y, z, r, length, yaw); ends show one whole log end (vki_endgrain_fit)"""
    rx = Matrix.Rotation(math.pi / 2, 4, "Y")
    for (y, z, r, ln, rz) in specs:
        vs = _cyl(k, (cx, y, z), r, r * 0.92, ln, 8, BARK_OAK, rot=Matrix.Rotation(rz, 4, "Z") @ rx)
        k.bm.normal_update()
        ax_ = Matrix.Rotation(rz, 3, "Z") @ VKI_STO_X
        for f in [f for f in vki_faces_of(vs) if abs(f.normal.dot(ax_)) > 0.9]:
            U = f.normal.cross(VKI_STO_Z).normalized()
            vki_endgrain_fit(k, [f], f.calc_center_median(), U, f.normal.cross(U), r, fill=VKI_ENDGRAIN_R)
        for v in vs:
            k.set_dark([v], 0.70 if v.co.z < z else 0.40)


def vki_sto_bucket(k, c, r=0.14, h=0.28, water=True):
    """a coopered bucket: WOOD staves (12-gon, slightly flared), two iron hoops, WATER surface below the rim"""
    x, y, z = c
    _cyl(k, (x, y, z + h / 2), r * 0.88, r, h, 12, WOOD)
    for zz in (0.06, h - 0.06):
        rr = r * 0.88 + (r - r * 0.88) * zz / h + 0.006
        _cyl(k, (x, y, z + zz), rr, rr, 0.03, 12, IRON)
    if water:
        _cyl(k, (x, y, z + h - 0.045), r * 0.93, r * 0.93, 0.02, 12, WATER)


# ---------------------------------------------------------------- Hearth_300 (§3.2, special)
VKI_STO_HEARTH = dict(firebox=(0.50, 2.50), fb_top=1.20, back_y=-0.20, breast=(0.35, 2.65), front_y=-1.00,
                      slab=(0.35, 2.65, -1.45, -1.00), lintel=(1.20, 1.52), mantel=(1.52, 1.60),
                      breast_lo=(0.40, 2.60, -0.96), weather=(2.25, 2.47), breast_up=(0.72, 2.28, -0.66),
                      cut_lintel_y=-0.73)
# hearth socket (the Timber fix r1 lesson, §10.2): above the flame tips, inside the firebox under the Cut lintel
# (0.90), 0.40 m from the back -- the spec's (1.5, -0.7, 0.5) sits among the logs and flames and burns them white
VKI_STO_HEARTH_LIGHT = (1.45, -0.60, 0.84)
VKI_STO_HEARTH_W = 400.0
VKI_STO_HEARTH_RADIUS = 0.40
VKI_STO_HEARTH_FIRE = (1.38, -0.52)          # fire centre: left of the roast, right of the cauldron
# flame profile (t along the height, radius factor, heat): VKI_TIM_FLAME_PROFILE's white-hot root, but the body cools
# a little sooner (0.84 at t 0.14, 0.58 at t 0.32 against 0.88 / 0.66) so the large hearth fire's tongues read more
# orange than cream under AgX. Measured (workshop room, Day, fire p90 vs north glass p90): Timber profile 0.751 /
# 0.729; (0.78, 0.50, ...) 0.708 / 0.717 -- the fire lost the lead; this profile keeps it
VKI_STO_FLAME_PROFILE = ((0.0, 0.75, 1.0), (0.14, 1.0, 0.84), (0.32, 0.92, 0.58), (0.52, 0.70, 0.34),
                         (0.72, 0.42, 0.15), (0.88, 0.18, 0.05))


def vki_sto_flame(k, base, h, r, tilt, spin, bow, flat=0.55, nseg=8, profile=VKI_STO_FLAME_PROFILE):
    """vki_tim_flame (smooth, flattened, bowed GLOW tongue with heat per ring) with its own heat profile"""
    rings = []
    for t, rs, ht in profile:
        dx = bow * math.sin(math.pi * 0.8 * t)
        ring_ = []
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            v = k.bm.verts.new((math.cos(a) * r * rs + dx, math.sin(a) * r * rs * flat, t * h))
            k.set_heat([v], ht)
            ring_.append(v)
        rings.append(ring_)
    tip = k.bm.verts.new((bow * math.sin(math.pi * 0.8), 0.0, h))
    k.set_heat([tip], 0.0)
    fs = [k.bm.faces.new(rings[0][::-1])]
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(nseg):
            fs.append(k.bm.faces.new((A[i], A[(i + 1) % nseg], B[(i + 1) % nseg], B[i])))
    for i in range(nseg):
        fs.append(k.bm.faces.new((rings[-1][i], rings[-1][(i + 1) % nseg], tip)))
    vs = [v for rg in rings for v in rg] + [tip]
    M = Matrix.Translation(base) @ Matrix.Rotation(tilt, 4, "Y") @ Matrix.Rotation(spin, 4, "Z")
    bmesh.ops.transform(k.bm, matrix=M, verts=vs)
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    for f in fs:
        f.material_index = GLOW
        f.smooth = True
    k.project(fs, GLOW)
    return vs
VKI_STO_HEARTH_FLAMES = ((1.40, -0.47, 0.60, 0.105, 0.0, 0.15, 0.03), (1.22, -0.43, 0.44, 0.085, 0.18, -0.35, -0.035),
                         (1.58, -0.50, 0.50, 0.09, -0.16, 0.30, 0.04), (1.49, -0.38, 0.34, 0.065, -0.06, -0.20, 0.025),
                         (1.08, -0.48, 0.30, 0.065, 0.26, 0.25, -0.03), (1.72, -0.45, 0.33, 0.07, -0.24, -0.30, 0.035),
                         (1.31, -0.54, 0.27, 0.06, 0.10, 0.40, 0.02), (0.98, -0.40, 0.22, 0.05, 0.30, -0.1, -0.02),
                         (1.84, -0.40, 0.24, 0.055, -0.3, 0.2, 0.03))


def vki_sto_hearth(k, height):
    """Firebox x 0.50-2.50, 1.20 high (Cut: 0.90), back at y -0.20 (BRICK, sooted), recessed 5 cm into the wall.
    Breast x 0.35-2.65 to y -1.00: rubble cheeks (WALL_A, so the instance's wall style applies: StoneInWarm in the
    Tavern, plaster in a limewashed hall), a three-stone dressed lintel 1.20-1.52, a mantel shelf 1.52-1.60 (CAP top),
    then a stepped chimney breast: rubble lower breast (x 0.40-2.60, y -0.96) to 2.25 with a soot fan, a dressed
    sloped weathering course to 2.47, a narrower upper breast (x 0.72-2.28, y -0.66) to H + 0.04 with a CAP top.
    Slab x 0.35-2.65, y -1.45..-1.00, z 0-0.03 (DRESS, three slabs, sooted toward the fire) plus the firebox floor.
    Spit with a goods-atlas roast (GOODS meat, browned) on two spit dogs, a cauldron on a trivet over its own embers,
    firedogs, logs, GLOW embers and nine flame tongues (vki_heat, VKI_STO_FLAME_PROFILE).
    Cut (the cutaway reading of the Fireplace rule): cheeks to 0.90, a front lintel course 0.90-1.00 (CAP tops,
    y -1.03..-0.73) and a coping stone on each cheek, the firebox open from above so the fire shows; firebox, hearth
    and fire identical to the Full piece."""
    L = 3.0
    full = height == "Full"
    H = VKI_STO_HEARTH
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    fx0, fx1 = H["firebox"]; bx0, bx1 = H["breast"]; fy = H["front_y"]; by = H["back_y"]
    mt = H["fb_top"] if full else zb                       # mouth top (Full 1.20, Cut 0.90)
    zr = mt                                                 # recess top
    T2 = k.T / 2
    # wall body round the recess
    p1 = vki_sto_body(k, 0.0, fx0, VKI_FOOT_Z, zb)
    p2 = vki_sto_body(k, fx1, L, VKI_FOOT_Z, zb)
    rec = vki_sto_body(k, fx0, fx1, VKI_FOOT_Z, zr, y0=by)
    k.bm.normal_update()
    for f in vki_faces_of(rec):
        if f.normal.y < -0.7:
            k.project([f], VKI_BRICK)
    for vs_, sgn in ((p1, 1), (p2, -1)):
        for f in vki_faces_of(vs_):
            c = f.calc_center_median()
            if f.normal.x * sgn > 0.7 and 0.0 <= c.z <= zr and c.y < 0:
                k.project([f], VKI_BRICK)
    if full:
        ab = vki_sto_body(k, fx0, fx1, zr, zb)
        for f in vki_faces_of(ab):
            if f.normal.z < -0.7:
                k.project([f], VKI_BRICK)
                k.set_dark(list(f.verts), 0.62)
    # cheeks (rubble, the breast's sides): x 0.35-0.50 / 2.50-2.65, y -1.00 .. -0.25 (flush with face A: buried
    # deeper, their brick inner face would lie in the plane of the piers' brick end faces, T5S)
    for a, b in ((bx0, fx0), (fx1, bx1)):
        vs = vki_sto_body(k, a, b, 0.0, mt, y0=fy, y1=-T2)
        k.bm.normal_update()
        for f in vki_faces_of(vs):
            if abs(f.normal.x) > 0.7 and ((a < 1.5 and f.normal.x > 0) or (a > 1.5 and f.normal.x < 0)):
                k.project([f], VKI_BRICK)                  # the firebox side of the cheek
        vki_sto_reproject_body(k, vki_faces_of(vs))        # exact UVs after body_box's grid cut (T16)
        for v in vs:
            v[k.body] = 0                                  # not wall-face body: no wobble, no footing rule
            if fx0 - 1e-4 <= v.co.x <= fx1 + 1e-4 or abs(v.co.x - fx0) < 1e-4 or abs(v.co.x - fx1) < 1e-4:
                k.set_dark([v], 0.52 + 0.34 * vki_smoothstep(0.2, mt, v.co.z))
    # recess soot (back and the 5 cm pier strips)
    for v in rec:
        if abs(v.co.y - by) < 1e-4:
            k.set_dark([v], 0.56 + 0.34 * vki_smoothstep(0.1, zr, v.co.z))
    for vs_, xe in ((p1, fx0), (p2, fx1)):
        for v in vs_:
            if abs(v.co.x - xe) < 1e-4 and v.co.y < 0.0 and v.co.z <= zr + 1e-4:
                k.set_dark([v], 0.52 + 0.34 * vki_smoothstep(0.1, zr, v.co.z))
    if full:
        # three-stone lintel over the 2.0 m mouth (buried 5 cm in the wall), the mantel shelf, the breast above
        # (x 0.33-2.67: everything proud of the envelope keeps NODE_FLAT from the nodes, T3; the back stops 15 mm
        # inside the wall so its bevelled underside never shares the z 1.20 plane with the body's soffit, T5S)
        l0, l1 = H["lintel"]
        for i, (a, b) in enumerate(((0.33, 1.08), (1.08, 1.92), (1.92, 2.67))):
            vs = vki_sto_block(k, a, b, l0, l1, fy - 0.03, -0.235, key="hl%d" % i)
            for v in vs:
                if v.co.z < l0 + 0.03:
                    k.set_dark([v], 0.45)                  # sooted soffit of the mouth
        m0, m1 = H["mantel"]
        vki_sto_block(k, 0.33, 2.67, m0, m1, fy - 0.08, by, top=VKI_CAP, dark=0.0, key="hm")
        # stepped chimney breast: a rubble lower breast to 2.25, a dressed sloped weathering course, a narrower
        # upper breast to H + 0.04 with a CAP top (a plain full-width box read as one heavy block from the camera)
        (lx0, lx1, ly), (ux0, ux1, uy), (w0, w1) = H["breast_lo"], H["breast_up"], H["weather"]
        before = set(k.bm.verts)
        lo_ = list(set(k.box(((lx0 + lx1) / 2, (ly + by) / 2, (m1 + w0) / 2), (lx1 - lx0, by - ly, w0 - m1),
                             VKI_WALL_A, bevel=0)))
        grid_cut(k, lo_, 0.25)
        up_ = list(set(k.box(((ux0 + ux1) / 2, (uy + by) / 2, (w1 + zt + VKI_POST_TOP) / 2),
                             (ux1 - ux0, by - uy, zt + VKI_POST_TOP - w1), VKI_WALL_A, bevel=0)))
        grid_cut(k, up_, 0.25)
        brs = [v for v in k.bm.verts if v not in before]
        k.bm.normal_update()
        vki_sto_reproject_body(k, vki_faces_of(brs))                   # exact UVs after the grid cuts (T16)
        for f in vki_faces_of(brs):
            if f.normal.z > 0.7 and f.calc_center_median().z > zt:
                vki_sto_top(k, list(f.verts), VKI_CAP, (1.5, uy, 3.0))
        vs, fs = vki_sto_hexa(k, [(lx0, ly, w0), (lx1, ly, w0), (lx1, by, w0), (lx0, by, w0),
                                  (ux0, uy, w1), (ux1, uy, w1), (ux1, by, w1), (ux0, by, w1)], VKI_STONE_BLOCK_IN)
        k.project(fs, VKI_STONE_BLOCK_IN, offset=vki_hash_off((1.5, ly, w0)), tile=VKI_STO_TILE)
        brs += vs
        for v in brs:                                      # soot fan up the breast over the mouth
            if v.co.y < -0.5 or v.co.z < w1 + 1e-4:
                k.set_dark([v], 0.40 * (1 - vki_smoothstep(0.30, 1.05, abs(v.co.x - 1.45))) *
                           (1 - vki_smoothstep(1.7, 2.8, v.co.z)))
        vki_sto_coping(k, 0.0, L, zb, zt, L)
    else:
        # Cut (the cutaway reading of "breast cut at 1.00 with a CAP top"): the hollow breast is cut open -- a
        # front lintel course (three stones, CAP tops, y -1.03..-0.73) over the mouth and a coping stone on each
        # cheek behind it, so the firebox stays open from above and the fire shows from the game camera (a full-
        # depth slab hid it); the wall coping runs on behind
        for i, (a, b) in enumerate(((0.33, 1.08), (1.08, 1.92), (1.92, 2.67))):
            vs = vki_sto_block(k, a, b, zb, zt, fy - 0.03, H["cut_lintel_y"], top=VKI_CAP, key="hc%d" % i)
            for v in vs:
                if v.co.z < zb + 0.03 and fx0 < v.co.x < fx1:
                    k.set_dark([v], 0.45)
        for a, b in ((0.33, fx0 + 0.02), (fx1 - 0.02, 2.67)):
            vki_sto_block(k, a, b, zb, zt, H["cut_lintel_y"], -VKI_STO_HW, top=VKI_CAP, key="hk%d" % int(a))
        vki_sto_coping(k, 0.0, L, zb, zt, L)
    # hearth: front slab (three DRESS slabs, sooted toward the fire) and the firebox floor (bottom at z -0.005)
    sx0, sx1, sy0, sy1 = H["slab"]
    for a, b in ((sx0, 1.10), (1.10, 1.90), (1.90, sx1)):
        vs = k.box(((a + b) / 2, (sy0 + sy1) / 2, 0.015), (b - a, sy1 - sy0, 0.03), DRESS, bevel=0.012)
        for v in set(vs):
            k.set_dark([v], 0.16 + 0.22 * vki_smoothstep(sy0, sy1, v.co.y) *
                       (1 - vki_smoothstep(0.4, 1.2, abs(v.co.x - 1.45))))
    k.set_dark(k.box((1.5, (fy + by) / 2, 0.0125), (fx1 - fx0 - 0.01, by - fy, 0.035), DRESS, bevel=0.0), 0.38)
    fcx, fcy = VKI_STO_HEARTH_FIRE
    k.set_dark(k.box((fcx, fcy, 0.045), (1.05, 0.46, 0.04), VKI_ASH, bevel=0.018, segs=2), 0.45)   # ash bed
    for x in (fcx - 0.36, fcx + 0.36):                     # firedogs
        k.box((x, fcy - 0.22, 0.15), (0.045, 0.045, 0.30), IRON, bevel=0.01)
        k.box((x, fcy, 0.10), (0.04, 0.42, 0.04), IRON, bevel=0.008)
        k.box((x, fcy - 0.24, 0.31), (0.07, 0.07, 0.03), IRON, bevel=0.01)
    vki_sto_logs(k, fcx + 0.02, ((fcy + 0.08, 0.175, 0.065, 0.86, 0.05), (fcy - 0.09, 0.17, 0.06, 0.82, -0.06),
                                 (fcy - 0.005, 0.285, 0.055, 0.68, 0.12)))
    vki_sto_embers(k, fcx, fcy, 0.075, 11, 0.42, 0.20, 5301, hmax=0.85)
    for (x, y, h, r, tilt, spin, bow) in VKI_STO_HEARTH_FLAMES:
        vki_sto_flame(k, (x, y, 0.20), h, r, tilt, spin, bow)
    # spit: two iron spit dogs with cradles, the rod, a crank, and a goods-atlas roast (right of the flames)
    spy, spz = -0.80, 0.58
    for x in (0.64, 2.36):                                # feet on the firebox floor, uprights 2 cm into them
        k.box((x, spy, 0.05), (0.05, 0.24, 0.04), IRON, bevel=0.008)
        k.box((x, spy, 0.335), (0.04, 0.04, 0.57), IRON, bevel=0.008)
        k.box((x, spy, spz + 0.03), (0.05, 0.06, 0.03), IRON, bevel=0.006)
    _tube(k, (0.56, spy, spz), (2.44, spy, spz), 0.012, IRON)
    _tube(k, (0.56, spy, spz), (0.56, spy, spz - 0.16), 0.010, IRON)
    _tube(k, (0.56, spy, spz - 0.16), (0.50, spy, spz - 0.16), 0.014, WOOD)
    rv = _ico(k, (2.08, spy, spz), 0.15, GOODS, scale=(1.35, 0.78, 0.72), sub=2, jit=0.004, seed=5390)
    # explicit centre: goods_map's default centroid sums a set of vertices, whose order (and float rounding) varies
    # between builds (T16)
    goods_map(k, rv, "meat", axis=(1, 0, 0), ref=(0, 0, 1), c=(2.08, spy, spz))
    k.set_dark(rv, 0.28)                                   # browned on the spit
    # cauldron on a trivet over a few embers of its own (left of the fire)
    cx_, cy_ = 0.80, -0.55
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.4
        _tube(k, (cx_ + math.cos(a) * 0.15, cy_ + math.sin(a) * 0.15, 0.03), (cx_ + math.cos(a) * 0.11,
              cy_ + math.sin(a) * 0.11, 0.14), 0.010, IRON)
    _cyl(k, (cx_, cy_, 0.145), 0.13, 0.13, 0.02, 10, IRON)
    _cyl(k, (cx_, cy_, 0.215), 0.14, 0.185, 0.12, 10, IRON)
    _cyl(k, (cx_, cy_, 0.315), 0.185, 0.16, 0.08, 10, IRON)
    vki_sto_embers(k, cx_, cy_, 0.06, 4, 0.12, 0.10, 5341, core=0.25, rmin=0.035, rmax=0.05, hmax=0.6)
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", "A", holes=[(bx0, 0.0, bx1, zb)], top_body_fn=lambda x: zb)
    k.meta.update(vki_class="wall", vki_special=1,
                  vki_lights=[dict(type="POINT", role="hearth", pos=list(VKI_STO_HEARTH_LIGHT), w=VKI_STO_HEARTH_W,
                                   color=[1.0, .52, .22], range=8.0, flicker=1, shadows=1,
                                   radius=VKI_STO_HEARTH_RADIUS)],
                  vki_fx=[dict(fx="fire_large", pos=[fcx, fcy, 0.2])],
                  vki_collider=[[1.5, 0.0, 1.1, 3.0, k.T, 2.2],
                                [1.5, (sy0 + by) / 2, 1.1, bx1 - bx0, by - sy0, 2.2]])


def vki_sto_hearth_full(k): vki_sto_hearth(k, "Full")
def vki_sto_hearth_cut(k): vki_sto_hearth(k, "Cut")


# ---------------------------------------------------------------- Forge_300 (§3.2, special)
VKI_STO_FORGE = dict(hearth=(0.40, 2.60, -1.45, -0.20), top=0.85, pit=(0.88, 2.12, -1.10, -0.52), frame_z=0.75,
                     cheek=(0.22, -1.30), hood_z0=2.00, hood_top=(1.05, 1.95, -0.62), beam=(1.95, 2.20, -1.34, -1.10),
                     tuyere=(0.33, -0.81, 0.60))
# forge sockets (§3.2 says forge (1.5, -0.85, 1.3) and bed glow (1.5, -0.85, 0.95), 450-900 W + 150 W): at those
# points, 0.45 m and 0.05 m over the coal bed, the lights burned the coals and the pale hearth slabs white (irradiance
# ~240x the key) and washed the whole room orange -- the Timber fix r1 lesson. Unlike the hearth, the forge is open:
# every watt lands on pale slabs 1 m away. Measured on the workshop room (Day, p90 luma of material-masked pixels):
# 600+150 W at the spec points: frame 0.76 > coals 0.72, coal lumps 0.62 (grey); 200+30 W: frame 0.63, lumps 0.47;
# 120+20 W: frame 0.55, lumps 0.39. Chosen: the forge light just under the hood mouth (2.00) at 150 W, the bed glow
# 0.55 m over the bed at 25 W, shadowless.
VKI_STO_FORGE_LIGHT = (1.5, -0.66, 1.85)
VKI_STO_FORGE_GLOW = (1.5, -0.82, 1.40)
VKI_STO_FORGE_W = (150.0, 25.0)
VKI_STO_FORGE_HEAT = 0.85           # coal-bed heat ceiling: a yellow-orange heart (leads the window glass), orange-red
                                    # toward the rim


def vki_sto_forge(k, height):
    """Raised hearth x 0.40-2.60, y -1.45..-0.25 (its back runs 5 cm into the wall), top 0.85: a rubble block
    (WALL_A) under a frame of dressed slabs (CAP tops, sooted toward the fire) round a coal pit x 0.88-2.12, y
    -1.10..-0.52 filled with an ash bed, bevelled flat-shaded COAL lumps and graded GLOW embers (hot where the tuyere
    blows). Tuyere: an iron pipe out of the hearth's -X face (to x 0.33) and its nozzle in the pit. Fire irons
    (tongs, poker, rake) on the front slab, a water bucket on the front-right corner. Full: two dressed cheeks carry a
    dressed beam 1.95-2.20 and a rubble hood tapering from x 0.40-2.60 / y -1.30 at 2.00 into the wall top (x
    1.05-1.95, y -0.62 at 3.04, CAP top), sooted underneath and up its front. Cut: hearth, coal bed and irons kept,
    cheeks and hood removed. Re-implemented here (smithy_chimney is not used)."""
    L = 3.0
    full = height == "Full"
    F = VKI_STO_FORGE
    zb, zt = VKI_STO_FULL if full else VKI_STO_CUT
    T2 = k.T / 2
    hx0, hx1, hy0, hy1 = F["hearth"]
    px0, px1, py0, py1 = F["pit"]
    ztp, zf = F["top"], F["frame_z"]
    vki_sto_body(k, 0.0, L, VKI_FOOT_Z, zb)
    vki_sto_coping(k, 0.0, L, zb, zt, L)
    # rubble hearth block (not wall-face body: no wobble), its top at the frame's bottom
    before = set(k.bm.verts)
    blk = list(set(k.box(((hx0 + hx1) / 2, (hy0 + 0.02 + hy1) / 2, zf / 2), (hx1 - hx0 - 0.04, hy1 - hy0 - 0.02, zf),
                         VKI_WALL_A, bevel=0)))
    grid_cut(k, blk, 0.25)
    blk = [v for v in k.bm.verts if v not in before]
    k.bm.normal_update()
    vki_sto_wall_uv(k, [f for f in vki_faces_of(blk) if abs(f.normal.z) < 0.7])
    for f in vki_faces_of(blk):
        if f.normal.z > 0.7:                                 # the pit floor (under the ash): sooted
            k.set_dark(list(f.verts), 0.5)
    # frame of dressed slabs (CAP tops) round the pit; soot toward the pit
    frame = ((hx0, hx1, hy0, py0), (hx0, hx1, py1, hy1), (hx0, px0, py0, py1), (px1, hx1, py0, py1))
    for i, (a, b, c, d) in enumerate(frame):
        vs = vki_sto_block(k, a, b, zf, ztp, c, d, top=VKI_CAP, dark=0.0, key="ff%d" % i)
        for v in vs:
            dx = max(px0 - v.co.x, 0.0, v.co.x - px1); dy = max(py0 - v.co.y, 0.0, v.co.y - py1)
            k.set_dark([v], 0.35 + 0.40 * (1 - vki_smoothstep(0.0, 0.38, math.hypot(dx, dy))))
    # coal bed: ash, embers (hot core toward the tuyere side), coal lumps round them
    pcx, pcy = (px0 + px1) / 2, (py0 + py1) / 2
    k.set_dark(k.box((pcx, pcy, zf + 0.025), (px1 - px0 - 0.03, py1 - py0 - 0.03, 0.05), VKI_ASH, bevel=0.012), 0.55)
    vki_sto_embers(k, pcx - 0.12, pcy, zf + 0.085, 14, 0.40, 0.19, 5401, core=0.50, rmin=0.05, rmax=0.08,
                   hmax=VKI_STO_FORGE_HEAT)
    rnd = random.Random(5431)
    for i in range(30):
        a = 2 * math.pi * i / 30 + rnd.uniform(-0.1, 0.1)
        rr = rnd.uniform(0.72, 1.0)
        c = (pcx + math.cos(a) * rr * 0.55, pcy + math.sin(a) * rr * 0.25, zf + 0.07 + rnd.uniform(0.0, 0.035))
        s = rnd.uniform(0.07, 0.11)
        vs = k.box(c, (s, s * rnd.uniform(0.7, 1.0), s * 0.65), COAL, rot=(rnd.uniform(-0.4, 0.4),
                   rnd.uniform(-0.4, 0.4), rnd.uniform(0, 3.1)), bevel=0.012, jitter=0.006, seed=5440 + i)
        for f in vki_faces_of(set(vs)):
            f.smooth = False
    for i in range(9):                                      # lumps lying on the embers: glow between dark coal
        c = (pcx - 0.12 + rnd.uniform(-0.36, 0.36), pcy + rnd.uniform(-0.15, 0.15), zf + 0.10 + rnd.uniform(0, 0.02))
        s = rnd.uniform(0.06, 0.09)
        vs = k.box(c, (s, s * rnd.uniform(0.7, 1.0), s * 0.6), COAL, rot=(rnd.uniform(-0.4, 0.4),
                   rnd.uniform(-0.4, 0.4), rnd.uniform(0, 3.1)), bevel=0.01, jitter=0.005, seed=5480 + i)
        for f in vki_faces_of(set(vs)):
            f.smooth = False
    # tuyere: pipe from the hearth's -X face out to x 0.33, flange, and the nozzle mouth inside the pit
    tx, ty, tz = F["tuyere"]
    _tube(k, (tx, ty, tz), (hx0 + 0.06, ty, tz), 0.045, IRON, segs=10)
    _cyl(k, (hx0 - 0.005, ty, tz), 0.075, 0.075, 0.02, 10, IRON, rot=Matrix.Rotation(math.pi / 2, 4, "Y"))
    k.box((px0 + 0.03, ty, zf + 0.07), (0.07, 0.10, 0.07), IRON, bevel=0.01)
    # fire irons on the front slab (tongs, poker, rake) and the water bucket on the front-right corner
    # (all low enough for the Cut piece, whose T1 ceiling is 1.04; clear of the Full piece's cheeks)
    iz = ztp + 0.012
    _tube(k, (0.70, -1.28, iz), (1.36, -1.22, iz), 0.011, IRON)                 # tongs
    _tube(k, (0.70, -1.25, iz), (1.36, -1.20, iz + 0.004), 0.011, IRON)
    k.box((1.40, -1.21, iz), (0.09, 0.05, 0.02), IRON, bevel=0.005)
    _tube(k, (1.46, -1.34, iz), (1.96, -1.25, iz), 0.013, IRON)                 # poker
    _tube(k, (0.72, -1.39, iz), (1.30, -1.37, iz), 0.010, IRON)                 # rake
    k.box((1.33, -1.37, iz + 0.005), (0.035, 0.14, 0.03), IRON, bevel=0.005)
    vki_sto_bucket(k, (2.20, -1.29, ztp), r=0.12, h=0.18)
    if full:
        cw, cy0 = F["cheek"]
        h0 = F["hood_z0"]
        for a, b in ((hx0, hx0 + cw), (hx1 - cw, hx1)):
            for j, (z0, z1) in enumerate(((ztp, 1.45), (1.45, h0))):
                vs = vki_sto_block(k, a, b, z0, z1, cy0, hy1, key="fc%d%d" % (int(a * 10), j))
                for v in vs:
                    if (a < 1.5 and v.co.x > b - 1e-4) or (a > 1.5 and v.co.x < a + 1e-4):
                        k.set_dark([v], 0.45 + 0.25 * vki_smoothstep(0.9, 2.0, v.co.z))
        b0, b1, by0, by1 = F["beam"]
        for i, (a, b) in enumerate(((hx0 - 0.04, 1.12), (1.12, 1.88), (1.88, hx1 + 0.04))):
            vs = vki_sto_block(k, a, b, b0, b1, by0, by1, key="fb%d" % i)
            for v in vs:
                if v.co.z < b0 + 0.03:
                    k.set_dark([v], 0.40)
        tx0, tx1, ty0 = F["hood_top"]
        ztop = zt + VKI_POST_TOP
        vs, fs = vki_sto_hexa(k, [(hx0, cy0, h0), (hx1, cy0, h0), (hx1, hy1, h0), (hx0, hy1, h0),
                                  (tx0, ty0, ztop), (tx1, ty0, ztop), (tx1, hy1, ztop), (tx0, hy1, ztop)], VKI_WALL_A)
        vs = vki_cut(k, vs, zs=[2.25, 2.5, 2.75], xs=[0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25])
        k.bm.normal_update()
        hf = vki_faces_of(vs)
        vki_sto_wall_uv(k, [f for f in hf if abs(f.normal.z) < 0.7])
        for f in hf:
            if f.normal.z > 0.7:
                vki_sto_top(k, list(f.verts), VKI_CAP, (1.5, ty0, 3.0))
            elif f.normal.z < -0.7:
                k.project([f], VKI_BRICK)
                k.set_dark(list(f.verts), 0.65)
        for v in vs:                                        # soot up the hood front, strongest over the fire
            k.set_dark([v], 0.38 * (1 - vki_smoothstep(0.2, 1.1, abs(v.co.x - 1.5))) *
                       (1 - vki_smoothstep(h0 + 0.1, 2.9, v.co.z)))
    # soot on the wall face behind the fire (the alcove between the cheeks, up into the hood)
    for v in k.bm.verts:
        if v[k.body] and v.co.y < 0 and hx0 + 0.1 < v.co.x < hx1 - 0.1 and v.co.z > zf - 0.05:
            k.set_dark([v], (0.55 - 0.25 * vki_smoothstep(0.3, 1.1, abs(v.co.x - 1.5))) *
                       (1 - (0.0 if full else 1.0) * vki_smoothstep(0.9, 1.0, v.co.z)))
    vki_sto_body_finish(k)
    vki_wobble(k, L, "Stone", "A", holes=[(hx0, 0.0, hx1, ztp)], top_body_fn=lambda x: zb)
    lights = [dict(type="POINT", role="forge", pos=list(VKI_STO_FORGE_LIGHT), w=VKI_STO_FORGE_W[0],
                   color=[1.0, .45, .15], range=9.0, flicker=1, shadows=1, radius=0.35),
              dict(type="POINT", role="bed_glow", pos=list(VKI_STO_FORGE_GLOW), w=VKI_STO_FORGE_W[1],
                   color=[1.0, .45, .15], range=3.0, flicker=1, shadows=0, radius=0.25)]
    k.meta.update(vki_class="wall", vki_special=1, vki_lights=lights,
                  vki_fx=[dict(fx="forge_fire", pos=[pcx, pcy, zf + 0.10]), dict(fx="smoke", pos=[1.5, -0.8, 1.9])],
                  vki_tuyere=[tx, ty, tz],
                  vki_collider=[[1.5, 0.0, 1.1, 3.0, k.T, 2.2],
                                [1.5, (hy0 + hy1) / 2, 1.1, hx1 - hx0, hy1 - hy0, 2.2]])


def vki_sto_forge_full(k): vki_sto_forge(k, "Full")
def vki_sto_forge_cut(k): vki_sto_forge(k, "Cut")


# ---------------------------------------------------------------- posts (§2.3)
VKI_STO_QUOIN = {"Full": (-0.30, 0.10, 0.48, 0.86, 1.26, 1.66, 2.06, 2.50, 3.04),
                 "Cut": (-0.30, 0.10, 0.48, 1.04)}
VKI_STO_PILASTER = {"Full": (-0.30, 0.10, 0.62, 1.14, 1.62, 2.10, 2.56, 3.04), "Cut": (-0.30, 0.10, 0.62, 1.04)}
VKI_STO_QUOIN_INSET = 0.018         # quoins: alternate blocks are long on X or on Y (the short face set back)


def vki_sto_post(k, kind, height):
    """Corner: a quoin pier of stacked StoneBlockIn blocks, +-0.31, alternate blocks set back 18 mm on one axis (the
    long / short quoin rhythm; the top block is full on both axes so T4's rays hit it everywhere). Mid: a thin
    dressed pilaster +-0.12 along the wall x +-0.31 across. z -0.30 .. wall top + 0.04, bevel 0.02, top faces CAP."""
    k.set_family("Stone")
    ax, ay = (VKI_POST_HW["O"], VKI_POST_HW["O"]) if kind == "Corner" else VKI_MID_HW["O"]
    zs = (VKI_STO_QUOIN if kind == "Corner" else VKI_STO_PILASTER)[height]
    n = len(zs) - 1
    for i in range(n):
        hx, hy = ax, ay
        if kind == "Corner" and i < n - 1:
            if i % 2 == 0:
                hy = ay - VKI_STO_QUOIN_INSET
            else:
                hx = ax - VKI_STO_QUOIN_INSET
        vki_sto_block(k, -hx, hx, zs[i], zs[i + 1], -hy, hy, bev=VKI_POST_BEVEL, top=VKI_CAP if i == n - 1 else None,
                      key="post%s%d" % (kind, i))
    other = "Cut" if height == "Full" else "Full"
    rule = {"Corner": "L/T/X junction (required, T12 error if missing); height = tallest wall-end height present "
                      "(a rake contributes its end height); Stone wins over every other family (§2.3)",
            "Mid": "height/family/class step on a straight run (required) | free end (required, §10.1) | rhythm at "
                   "even nodes (optional; Stone has none by default)"}[kind]
    k.meta.update(vki_class="post", vki_post_rule={"role": kind.lower(), "height": height, "rule": rule,
                                                   "toggle_to": f"SM_VKI_Post_Stone_{kind}_{other}",
                                                   "orient": "along local x" if kind == "Mid" else "any"},
                  vki_collider=[[0.0, 0.0, 1.1, 2 * ax, 2 * ay, 2.2]])


def vki_sto_post_corner_full(k): vki_sto_post(k, "Corner", "Full")
def vki_sto_post_corner_cut(k): vki_sto_post(k, "Corner", "Cut")
def vki_sto_post_mid_full(k): vki_sto_post(k, "Mid", "Full")
def vki_sto_post_mid_cut(k): vki_sto_post(k, "Mid", "Cut")


# ---------------------------------------------------------------- Leaf_Wide_Cut_L / _R (§3.3)
def vki_sto_leaf_wide(k, side, W=VKI_STO_WIDE_LEAF_W, fits=None):
    """one leaf of a wide Cut exit: hinge at the origin on the leaf's room-side face (planks at local y 0.004..0.084,
    the Leaf_Plank rule), W x 0.95 (x 0.005..0.005 + W; _R is the mirror image, extending -X), four oak planks with
    CAP tops, iron straps on both faces starting 0.10 from the hinge, a ring pull near the meeting edge. Placed at the
    door's vki_leaf_socket[0] (_L) / [1] (_R) with the door's rotation; opens toward the room: _L by rotation -deg
    about local Z, _R by +deg. W 0.89: Stone DoorWide_300_Cut (clear 1.80); W 0.795: Ashlar DoorWide_300 (clear
    1.60, Leaf_Wide160)."""
    sg = 1.0 if side == "L" else -1.0
    z0 = VKI_STO_DOOR["thr"] + 0.005
    z1 = z0 + 0.95
    xa, xb, n = 0.005, 0.005 + W, 4
    w = (xb - xa) / n
    t, y0 = VKI_LEAF_T, VKI_LEAF_Y0
    for i in range(n):
        a = xa + i * w
        c = (sg * (a + w / 2), y0 + t / 2, (z0 + z1) / 2); sz = (w, t, z1 - z0)
        vs = list(set(k.box(c, sz, WOOD, bevel=0.012)))
        vki_top_faces(k, vs, VKI_CAP, c, sz)
    sx0 = VKI_LEAF_STRAP_X0
    xs1, xo1 = xb - 0.035, xb - 0.045                    # strap ends (W 0.89: 0.86 / 0.85)
    for z in (0.26, 0.76):
        k.box((sg * (sx0 + xs1) / 2, y0 - 0.006, z), (xs1 - sx0, 0.012, 0.045), IRON, bevel=0.004)     # room side
        k.box((sg * (0.05 + xo1) / 2, y0 + t + 0.006, z), (xo1 - 0.05, 0.012, 0.045), IRON, bevel=0.004)  # outer
    zr = 0.52
    xr = sg * (xb - 0.115)                               # ring pull near the meeting edge (W 0.89: 0.78)
    k.box((xr, y0 - 0.006, zr + 0.03), (0.07, 0.012, 0.09), IRON, bevel=0.003)
    before = set(k.bm.verts)
    ring(k, (xr, y0 - 0.018, zr), 0.034, 0.054, 0.012, IRON, n=12, axis="Y")
    rv = [v for v in k.bm.verts if v not in before]
    bmesh.ops.rotate(k.bm, verts=rv, cent=Vector((xr, y0 - 0.008, zr + 0.054)),
                     matrix=Matrix.Rotation(math.radians(-8.0), 3, "X"))
    k.meta.update(vki_class="leaf", hinge_axis="local Z", vki_leaf_state="closed", vki_leaf_open_deg=90,
                  vki_leaf_width=round(xb - xa, 3), vki_leaf_height=round(z1 - z0, 3), vki_hinge=[0.0, 0.0, 0.0],
                  vki_leaf_clearance=0.005, vki_leaf_side=side,
                  vki_leaf_open_dir="rotation %sdeg about local Z (toward the room, -Y)" % ("-" if side == "L" else "+"),
                  vki_leaf_fits=(fits or "SM_VKI_Wall_Stone_DoorWide_300_Cut") + " at vki_leaf_socket[%d], same rotation" %
                                (0 if side == "L" else 1))


def vki_sto_leaf_wide_l(k): vki_sto_leaf_wide(k, "L")
def vki_sto_leaf_wide_r(k): vki_sto_leaf_wide(k, "R")
def vki_sto_leaf_wide160_l(k): vki_sto_leaf_wide(k, "L", VKI_STO_WIDE160_LEAF_W, "SM_VKI_Wall_Ashlar_DoorWide_300_Cut")
def vki_sto_leaf_wide160_r(k): vki_sto_leaf_wide(k, "R", VKI_STO_WIDE160_LEAF_W, "SM_VKI_Wall_Ashlar_DoorWide_300_Cut")


VKI_STO_SPECS = [
    ("SM_VKI_Wall_Stone_Plain_150A_Full", vki_sto_plain_150a_full, "wall"),
    ("SM_VKI_Wall_Stone_Plain_150A_Cut", vki_sto_plain_150a_cut, "wall"),
    ("SM_VKI_Wall_Stone_Plain_150B_Full", vki_sto_plain_150b_full, "wall"),
    ("SM_VKI_Wall_Stone_Plain_300_Full", vki_sto_plain_300_full, "wall"),
    ("SM_VKI_Wall_Stone_Plain_300_Cut", vki_sto_plain_300_cut, "wall"),
    ("SM_VKI_Wall_Stone_Window_150_Full", vki_sto_window_full, "wall"),
    ("SM_VKI_Wall_Stone_Window_150_Cut", vki_sto_window_cut, "wall"),
    ("SM_VKI_Wall_Stone_Door_150_Full", vki_sto_door_full, "wall"),
    ("SM_VKI_Wall_Stone_Door_150_Cut", vki_sto_door_cut, "wall"),
    ("SM_VKI_Wall_Stone_DoorWide_300_Full", vki_sto_door_wide_full, "wall"),
    ("SM_VKI_Wall_Stone_DoorWide_300_Cut", vki_sto_door_wide_cut, "wall"),
    ("SM_VKI_Wall_Stone_Rake_150_L", vki_sto_rake_l, "wall"),
    ("SM_VKI_Wall_Stone_Rake_150_R", vki_sto_rake_r, "wall"),
    ("SM_VKI_Wall_Stone_Hearth_300_Full", vki_sto_hearth_full, "wall"),
    ("SM_VKI_Wall_Stone_Hearth_300_Cut", vki_sto_hearth_cut, "wall"),
    ("SM_VKI_Wall_Stone_Forge_300_Full", vki_sto_forge_full, "wall"),
    ("SM_VKI_Wall_Stone_Forge_300_Cut", vki_sto_forge_cut, "wall"),
    ("SM_VKI_Post_Stone_Corner_Full", vki_sto_post_corner_full, "wall"),
    ("SM_VKI_Post_Stone_Corner_Cut", vki_sto_post_corner_cut, "wall"),
    ("SM_VKI_Post_Stone_Mid_Full", vki_sto_post_mid_full, "wall"),
    ("SM_VKI_Post_Stone_Mid_Cut", vki_sto_post_mid_cut, "wall"),
    ("SM_VKI_Leaf_Wide_Cut_L", vki_sto_leaf_wide_l, "prop"),
    ("SM_VKI_Leaf_Wide_Cut_R", vki_sto_leaf_wide_r, "prop"),
    ("SM_VKI_Leaf_Wide160_Cut_L", vki_sto_leaf_wide160_l, "prop"),
    ("SM_VKI_Leaf_Wide160_Cut_R", vki_sto_leaf_wide160_r, "prop"),
]
VKI_STO_NAMES = [n for n, _, _ in VKI_STO_SPECS]
vki_register([(n, fn, {"grime": gr}, "stone") for n, fn, gr in VKI_STO_SPECS])
