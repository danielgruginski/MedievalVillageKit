# ===================== VKI FAM CAVE: organic caves -- dual-grid rock tiles (adventure kit) =====================
# Adventure kit (docs/ADVENTURE_KIT.md). Package "adventure". Loaded by vki_ns() after vki_fam_ancient; uses the kit
# helpers (vki_vnoise, vki_sto_hexa, vki_dun_damp, and at build time vki_adv_box / vki_dpr_* / vki_home_*). Every
# top-level name starts with vki_/VKI_ (T18).
# A cave level is a cell map, not a wall plan: each 1.5 m cell of the map is open floor or rock, and everything outside
# the map is rock. Rock is Full (3.0) or Cut (1.0): the assembler cuts any rock cell with open floor within two cells
# to its north, so the camera sees over it (vki_rooms_adventure, vki_cave_cells).
# Rock tiles sit on the DUAL grid: a tile is centred on a node, its four corners are the centres of the four cells
# around that node (SW, SE, NE, NW), and its shape comes from their states -- O (open), C (Cut rock), F (Full rock).
# Inside a tile the rock outline is the zero contour of a field (the bilinear blend of the corners, +1 rock / -1 open,
# plus windowed noise), so it wanders ~0.4 m and curls into lobes, spurs and pillars; the rock top blends the corners'
# heights with ragged dips; the cliffs lean back from a foot that flares onto the floor, faceted (flat shading). Along
# a tile edge the field is linear, the noise is zero and the cliff profile is fixed, so any two neighbours join without
# a seam: the outline crosses an edge between rock and open exactly at its midpoint, with the same cliff section.
# Masters: one per rotation class of the 80 corner codes (23 codes), two variants each (three for the straight Full
# and Cut faces), placed at 0/90/180/270; plus SM_VKI_Rock_Cave_OOFF_Tunnel (a straight Full face with a cleft into
# the rock under a fallen lintel, darkness at its back: a scene link). Class "rock".
# Transitions (walls in a cave map): a masonry wall on a grid line runs through the middle of the tiles on its nodes,
# and rock left to itself would bulge through it. Wall-backed tiles (SM_VKI_Rock_Cave_<code>_Wall<arms>, 115 masters:
# every corner code with every set of wall arms S / E / N / W that has open floor on at least one side) keep the rock
# VKI_CAV_BACK (0.33) off each wall's line and off the post square on its node, the face there straight and upright
# (hidden behind the wall): the wall backs onto the rock, or its end is let into a rock face. Their outline meets the
# plain tiles' at every tile edge the walls do not cross.
# The chasm is painted as well ("vv" cells): dual-grid ground tiles (class "ground", SM_VKI_Ground_Cave_<code>_Q<p>,
# X chasm / O ground, 14 codes x 4 node parities + XXXX) carry the floor of their footprint with the chasm's hole cut
# by a field like the rock's, so it curves, widens and narrows freely; quarter floors (SM_VKI_Floor_075_R<a><b>) fill
# the cells they half cover; SM_VKI_Prop_RopeBridge_420 spans it where it is two cells wide. The straight chasm pits
# below stay for walled levels. The rock-walled Cave family for walled levels is vki_fam_cavewall.
# Pits (class pit, they replace the floor over their cells): Pit_Chasm_150x300 (a chasm segment 1 x 2 cells running
#   along x -- tiles chain -- 4 m deep into the void), Pit_ChasmBridge_150x300 (the same with a rope bridge across),
#   Pit_Pool_300x300 (an underground pool with a rocky shore)
# Cave dressing: Prop_Stalagmites, Prop_Crystals (glowing, light), Prop_Mushrooms_Glow (light), Prop_RockPillar_Cut /
#   _Full, Prop_Boulders, Overlay_Gravel, Overlay_Spill (earth and rubble over the seam where a cave floor meets
#   flagstones)
# Build: g["vki_ws_build"]("adventure", VKI_CAV_NAMES); test: g["vki_test_pieces"](VKI_CAV_NAMES) -> {}.
import bpy, bmesh, math, json, random
from mathutils import Vector, Matrix

VKI_CAV_CRYSTAL_COL = [0.45, 0.85, 1.0]
VKI_CAV_H = {"F": 3.0, "C": VKI_CUT_H}          # rock top of a Full / Cut corner
VKI_CAV_N = 9                                    # top-surface grid per tile (odd: an edge midpoint is never a node)
VKI_CAV_AMP = 0.55                               # field noise: the outline wanders up to ~0.4 m inside a tile
VKI_CAV_FOOT = 0.30                              # field margin of the floor-level footprint (the colliders)
VKI_CAV_VARIANTS = {"FFOO": "ABC", "CCOO": "ABC"}   # the straight faces are the commonest tiles
VKI_CAV_TUNNEL = dict(hw=0.45, back=0.52, lintel=1.95)
VKI_CAV_ARMS = "SENW"                              # wall arm i runs from the node between corners i and i + 1
VKI_CAV_ARM_D = ((0, -1), (1, 0), (0, 1), (-1, 0))
VKI_CAV_CORNER_P = ((-1, -1), (1, -1), (1, 1), (-1, 1))
VKI_CAV_BACK = 0.33                                # a wall arm keeps the rock this far off its line (coping 0.28, posts 0.31)


def vki_cav_rock_mats(k):
    """cave rock on a master: STONE_BLOCK_IN -> CaveRock, CAP -> CaveCut"""
    k.slot_mats[VKI_STONE_BLOCK_IN] = "M_VKI_CaveRock"
    k.slot_mats[VKI_CAP] = "M_VKI_CaveCut"


def vki_cav_canon(code):
    """(master code, k): the smallest rotation m of a corner code (SW, SE, NE, NW) with m[i] == code[(i + k) % 4] --
    the master m placed at rotation 90 k (counter-clockwise) shows `code`"""
    best = None
    for k in range(4):
        m = "".join(code[(i + k) % 4] for i in range(4))
        if best is None or m < best[0]:
            best = (m, k)
    return best


def vki_cav_canon_arms(code, arms):
    """(master code, master arms, k): the smallest rotation of a corner code together with its wall arms (a subset of
    "SENW"); the master placed at rotation 90 k shows `code` with `arms` (master arm i shows as arm i + k)"""
    best = None
    for k in range(4):
        m = "".join(code[(i + k) % 4] for i in range(4))
        ma = "".join(a for i, a in enumerate(VKI_CAV_ARMS) if VKI_CAV_ARMS[(i + k) % 4] in arms)
        if best is None or (m, ma) < best[:2]:
            best = (m, ma, k)
    return best


def vki_cav_arms_ok(code, arms):
    """the arms of `arms` a wall can take on a tile of `code`: open floor on at least one side of the arm"""
    return "".join(a for i, a in enumerate(VKI_CAV_ARMS) if a in arms and "O" in (code[i], code[(i + 1) % 4]))


def vki_cav_backed_keys():
    """[(code, arms)]: the 115 wall-backed masters -- every rotation class of a corner code with a non-empty set of
    wall arms that each have open floor on at least one side"""
    out = set()
    for n in range(81):
        code = "".join("OCF"[(n // 3 ** i) % 3] for i in range(4))
        ok = vki_cav_arms_ok(code, VKI_CAV_ARMS)
        if code == "OOOO" or not ok:
            continue
        for b in range(1, 16):
            arms = "".join(a for i, a in enumerate(VKI_CAV_ARMS) if b >> i & 1)
            if arms and set(arms) <= set(ok):
                out.add(vki_cav_canon_arms(code, arms)[:2])
    return sorted(out)


def vki_cav_wall_clamp(code, arms, x, y):
    """cap on the rock field for the walls on a tile's arms (< 0: no rock). Arm i runs from the node out to the tile
    edge between corners i and i + 1; it keeps the rock VKI_CAV_BACK off its line, from VKI_CAV_BACK behind the node
    (the post square) outward: on the open side where one of the two corners is rock (the wall backs onto the rock),
    on both sides where both are open (the wall's end let into a rock face). Min over the arms."""
    B = VKI_CAV_BACK
    out = 9.0
    for i, a in enumerate(VKI_CAV_ARMS):
        if a not in arms:
            continue
        dx, dy = VKI_CAV_ARM_D[i]
        px, py = VKI_CAV_CORNER_P[i]
        nx, ny = (px, 0) if dx == 0 else (0, py)                  # across the arm, toward corner i
        along = x * dx + y * dy + B
        t = x * nx + y * ny
        o1, o2 = code[i] == "O", code[(i + 1) % 4] == "O"
        side = abs(t) - B if (o1 and o2) else (-(t + B) if o1 else t - B)
        out = min(out, 2.5 * max(-along, side))
    return out


def vki_cav_rot(master, code):
    """k (rotation 90 k, counter-clockwise) that shows `code` with the master built as `master`, else None"""
    for k in range(4):
        if all(master[i] == code[(i + k) % 4] for i in range(4)):
            return k
    return None


def vki_cav_codes():
    """the 23 master codes (rotation classes of the non-empty O / C / F corner codes)"""
    out = set()
    for a in "OCF":
        for b in "OCF":
            for c in "OCF":
                for d in "OCF":
                    if a + b + c + d != "OOOO":
                        out.add(vki_cav_canon(a + b + c + d)[0])
    return sorted(out)


def vki_cav_window(x, y):
    """1 at the tile centre, 0 on its edges"""
    u, v = (x + 0.75) / 1.5, (y + 0.75) / 1.5
    return max(0.0, 16.0 * u * (1.0 - u) * v * (1.0 - v))


def vki_cav_field(x, y, code, seed, amp=VKI_CAV_AMP, notch=False, sym=False):
    """> 0 rock, < 0 open: the bilinear blend of the corners (+1 rock, -1 open) plus windowed noise, biased so the
    rock grows into open space (lobes, spurs) and hardly ever recedes past the bilinear outline (at most ~4 cm, under
    the cliff's foot): the rock always covers its own cells, so nothing outside the map needs a floor. notch cuts the
    tunnel cleft (|x| < hw, y < back) out of a rock-north tile; sym: unbiased noise (the chasm's hole, whose tile
    carries its own floor)"""
    u, v = (x + 0.75) / 1.5, (y + 0.75) / 1.5
    val = [-1.0 if c == "O" else 1.0 for c in code]
    B = val[0] * (1 - u) * (1 - v) + val[1] * u * (1 - v) + val[2] * u * v + val[3] * (1 - u) * v
    n = 0.75 * (2.0 * vki_vnoise(x / 0.42 + 3.1, y / 0.42 + 1.7, seed) - 1.0) + \
        0.25 * (2.0 * vki_vnoise(x / 0.18 + 5.3, y / 0.18 + 2.9, seed + 3) - 1.0)
    s = B + amp * vki_cav_window(x, y) * (n if sym else 0.4 + 0.6 * n)
    if notch:
        T = VKI_CAV_TUNNEL
        s = min(s, 2.5 * max(abs(x) - T["hw"], y - T["back"]))
    return s


def vki_cav_height(x, y, code, seed):
    """rock top: the rock corners' heights blended bilinearly (open corners left out), minus ragged dips (up to 0.35
    on Full rock, 0.10 on Cut) that vanish on the tile edges"""
    u, v = (x + 0.75) / 1.5, (y + 0.75) / 1.5
    w = ((1 - u) * (1 - v), u * (1 - v), u * v, (1 - u) * v)
    num = den = 0.0
    for wi, c in zip(w, code):
        if c != "O":
            num += wi * VKI_CAV_H[c]
            den += wi
    Hb = num / den if den > 1e-9 else max(VKI_CAV_H[c] for c in code if c != "O")
    amp = 0.10 + 0.125 * (Hb - VKI_CUT_H)
    return Hb - amp * vki_cav_window(x, y) * vki_vnoise(x / 0.33 + 7.7, y / 0.33 + 2.2, seed + 11)


def vki_cav_prof(z, H):
    """the cliff's lean away from the top outline at height z (toward open): 0 at the bottom (-0.30) and at the top
    H, a foot that flares onto the floor around z 0, leaning back above it"""
    foot = 0.12 * math.exp(-((z - 0.05) / 0.22) ** 2) * vki_smoothstep(-0.30, -0.12, z)
    lean = 0.10 * (H - z) / (H + 0.30) * vki_smoothstep(-0.30, 0.0, z)
    return foot + lean


def vki_cav_ms_solid(k, fld, ztop, levels, prof, seed, wamp=0.10, freeze=None, bottom=True):
    """the marching-squares solid of a dual-grid tile over the region fld > 0 (the tile is [-0.75, 0.75]^2, grid
    VKI_CAV_N): a top surface at ztop(x, y); a column down every boundary vertex of the top at levels(H) (bottom
    first, the top vertex last), displaced along the outline's normal toward fld < 0 by prof(z, H) plus windowed noise
    (wamp) on the inner rows -- along the tile edge and without noise at an edge crossing, so neighbours meet
    exactly; straight vertical sections where the region meets a tile edge; a flat bottom (the top's polygons at the
    bottom level; bottom=False leaves it open: it faces down under the floor, never seen). freeze(x, y) -> True keeps
    a vertex's column straight. Closed unless bottom=False. Returns dict(tops, cliff, sect,
    bottoms): cliff faces carry UVs along the outline (u wraps to whole 1.5 m tiles, 0 at both ends) and z / 1.5."""
    N, h = VKI_CAV_N, 0.75
    st = 1.5 / N
    X = [-h + st * i for i in range(N + 1)]
    X[-1] = h
    Fv = {}
    for i in range(N + 1):
        for j in range(N + 1):
            s = fld(X[i], X[j])
            Fv[(i, j)] = s if abs(s) > 1e-7 else 1e-7
    bm = k.bm
    top, info = {}, {}

    def border(ij):
        b = set()
        if ij[0] == 0: b.add("W")
        if ij[0] == N: b.add("E")
        if ij[1] == 0: b.add("S")
        if ij[1] == N: b.add("N")
        return b

    def node(ij):
        key = ("n", ij)
        if key not in top:
            x, y = X[ij[0]], X[ij[1]]
            top[key] = bm.verts.new((x, y, ztop(x, y)))
            info[key] = dict(x=x, y=y, b=border(ij), cross=False)
        return key

    def cross(a, b):
        key = ("e", min(a, b), max(a, b))
        if key not in top:
            fa, fb = Fv[a], Fv[b]
            t = fa / (fa - fb)
            xa, ya, xb, yb = X[a[0]], X[a[1]], X[b[0]], X[b[1]]
            x = xa if xa == xb else xa + (xb - xa) * t
            y = ya if ya == yb else ya + (yb - ya) * t
            rk, op = (a, b) if fa > 0 else (b, a)
            top[key] = bm.verts.new((x, y, ztop(x, y)))
            info[key] = dict(x=x, y=y, b=border(a) & border(b), cross=True,
                             rock=(X[rk[0]], X[rk[1]]), open=(X[op[0]], X[op[1]]))
        return key

    tops = []
    for i in range(N):
        for j in range(N):
            cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            ins = [Fv[c] > 0 for c in cs]
            if not any(ins):
                continue
            polys = None
            if sum(ins) == 2 and ins[0] == ins[2]:                         # saddle
                if fld((X[i] + X[i + 1]) / 2, (X[j] + X[j + 1]) / 2) <= 0:  # the two inside corners stay apart
                    polys = [[node(cs[a]), cross(cs[a], cs[(a + 1) % 4]), cross(cs[(a - 1) % 4], cs[a])]
                             for a in ((0, 2) if ins[0] else (1, 3))]
            if polys is None:
                poly = []
                for m in range(4):
                    if ins[m]:
                        poly.append(node(cs[m]))
                    if ins[m] != ins[(m + 1) % 4]:
                        poly.append(cross(cs[m], cs[(m + 1) % 4]))
                polys = [poly]
            for poly in polys:
                tops.append(bm.faces.new([top[p] for p in poly]))
    if not tops:
        return dict(tops=[], cliff=[], sect=[], bottoms=[])
    key_of = {v: kk for kk, v in top.items()}
    bedges = [e for e in {e for f in tops for e in f.edges} if len(e.link_faces) == 1]
    cols = {}

    def column(kk):
        if kk in cols:
            return cols[kk]
        v = top[kk]
        x, y, H = v.co.x, v.co.y, v.co.z
        inf = info[kk]
        zs = levels(H)
        if not inf["cross"]:                                            # a node on the tile edge: straight
            cols[kk] = [bm.verts.new((x, y, zs[0])), v]
            return cols[kk]
        if inf["b"]:                                                     # an edge crossing: along the edge, no noise
            d = Vector(inf["open"]) - Vector(inf["rock"])
            d.normalize()
            wn = 0.0
        else:
            e_ = 1e-3
            d = Vector((-(fld(x + e_, y) - fld(x - e_, y)), -(fld(x, y + e_) - fld(x, y - e_))))
            for ax in (0, 1):                                            # never lean out across a near tile edge
                c_ = (x, y)[ax]
                gap = 0.75 - abs(c_)
                if gap < 0.35 and (d[ax] > 0) == (c_ > 0):
                    d[ax] *= gap / 0.35
            d = d.normalized() if d.length > 1e-9 else Vector((0.0, 0.0))
            wn = math.sqrt(vki_cav_window(x, y))
        if freeze is not None and freeze(x, y):                         # held upright (a tunnel's cleft, a wall's back)
            d = Vector((0.0, 0.0))
        vs = []
        for m, z in enumerate(zs):
            dd = prof(z, H)
            if m >= 1 and wn > 0:
                dd += wamp * wn * (2.0 * vki_vnoise((x + y) / 0.35 + 1.3 * m, z / 0.45 + 0.7 * m, seed + 21) - 1.0)
            vs.append(bm.verts.new((max(-h, min(h, x + d.x * dd)), max(-h, min(h, y + d.y * dd)), z)))
        vs.append(v)
        cols[kk] = vs
        return vs

    cliff, sect, cedges = [], [], []
    for e in bedges:
        ka, kb = key_of[e.verts[0]], key_of[e.verts[1]]
        if info[ka]["b"] & info[kb]["b"]:                                # on a tile edge: a vertical section
            ca, cb = column(ka), column(kb)
            if len(cb) > len(ca):
                ca, cb = cb, ca
            if len(ca) == 2:
                sect.append(bm.faces.new((ca[0], cb[0], cb[1], ca[1])))
            else:
                sect.append(bm.faces.new(list(ca) + [cb[1], cb[0]]))
        else:
            cedges.append((ka, kb))
    adj = {}
    for ka, kb in cedges:
        adj.setdefault(ka, []).append(kb)
        adj.setdefault(kb, []).append(ka)
    used, uvu = set(), {}
    for s0 in [kk for kk, nb in adj.items() if len(nb) == 1] + list(adj):
        for nb in adj[s0]:
            if frozenset((s0, nb)) in used:
                continue
            chain, cur, nxt = [s0], s0, nb
            while True:
                used.add(frozenset((cur, nxt)))
                chain.append(nxt)
                if nxt == s0:
                    break
                cand = [n_ for n_ in adj[nxt] if frozenset((nxt, n_)) not in used]
                if not cand:
                    break
                cur, nxt = nxt, cand[0]
            P = [Vector((info[c_]["x"], info[c_]["y"])) for c_ in chain]
            S = [0.0]
            for a_, b_ in zip(P[:-1], P[1:]):
                S.append(S[-1] + (b_ - a_).length)
            L = max(S[-1], 1e-6)
            nt = max(1, round(L / 1.5))
            for i_ in range(len(chain) - 1):
                ua, ub = S[i_] / L * nt, S[i_ + 1] / L * nt
                uvu[(chain[i_], chain[i_ + 1])] = (ua, ub)
                uvu[(chain[i_ + 1], chain[i_])] = (ub, ua)
    for ka, kb in cedges:
        ca, cb = column(ka), column(kb)
        ua, ub = uvu[(ka, kb)]
        for m in range(len(ca) - 1):
            f = bm.faces.new((ca[m], cb[m], cb[m + 1], ca[m + 1]))
            for lp in f.loops:
                lp[k.uv].uv = ((ua if lp.vert in (ca[m], ca[m + 1]) else ub), lp.vert.co.z / 1.5)
            cliff.append(f)
    bot, bottoms = {}, []
    for f in (tops if bottom else []):                                  # bottom=False: open there (the bottom faces
        # face down under the floor, never seen from above: 14-25 % of a cave level's triangles; T7 allows the open
        # bottom plane through vki_open_bottom)
        vs = []
        for v in f.verts:
            kk = key_of[v]
            if kk in cols:
                vs.append(cols[kk][0])
            else:
                if kk not in bot:
                    zb = levels(v.co.z)[0]
                    bot[kk] = bm.verts.new((v.co.x, v.co.y, zb))
                vs.append(bot[kk])
        bottoms.append(bm.faces.new(vs[::-1]))
    bmesh.ops.recalc_face_normals(bm, faces=tops + cliff + sect + bottoms)
    return dict(tops=tops, cliff=cliff, sect=sect, bottoms=bottoms)


def vki_cav_boxes(inside, R_=6):
    """collider boxes (local, 2-D) of the cells of an R_ x R_ raster over the tile where inside(x, y): row runs
    merged into rectangles -> [(cx, cy, w, d)]"""
    h, cs_ = 0.75, 1.5 / R_
    rows = []
    for j in range(R_):
        runs, i = [], 0
        while i < R_:
            if inside(-h + cs_ * (i + 0.5), -h + cs_ * (j + 0.5)):
                i0 = i
                while i < R_ and inside(-h + cs_ * (i + 0.5), -h + cs_ * (j + 0.5)):
                    i += 1
                runs.append((i0, i))
            else:
                i += 1
        rows.append(runs)
    boxes, open_ = [], {}
    for j in range(R_ + 1):
        runs = rows[j] if j < R_ else []
        for run in list(open_):
            if run not in runs:
                j0 = open_.pop(run)
                boxes.append((round(-h + cs_ * (run[0] + run[1]) / 2, 4), round(-h + cs_ * (j0 + j) / 2, 4),
                              round(cs_ * (run[1] - run[0]), 4), round(cs_ * (j - j0), 4)))
        for run in runs:
            open_.setdefault(run, j)
    return boxes


def vki_cav_tile(k, code, var="A", tunnel=False, arms=""):
    """one dual-grid rock tile (see the header): vki_cav_ms_solid over the rock (tops at the blended corner heights,
    cliff rows at -0.30, 0, H/4, H/2, 3H/4, H, a bottom at -0.30); tops CAP (pale CaveCut, planar UVs), cliffs, sections
    and bottom STONE_BLOCK_IN (CaveRock); the tunnel variant cuts a cleft under a fallen lintel; `arms` (wall arms,
    vki_cav_wall_clamp) keeps the rock off walls on the node's grid lines, its face there straight and upright."""
    k.set_family("Cave")
    seed = vki_seed("CaveTile|%s|%s|%d" % (code, var, int(tunnel)))
    amp = VKI_CAV_AMP * (0.5 if tunnel else 1.0)
    T = VKI_CAV_TUNNEL
    if arms:
        fld = lambda x, y: min(vki_cav_field(x, y, code, seed, amp), vki_cav_wall_clamp(code, arms, x, y))
        freeze = lambda x, y: vki_cav_wall_clamp(code, arms, x, y) < 0.15
    else:
        fld = lambda x, y: vki_cav_field(x, y, code, seed, amp, tunnel)
        freeze = (lambda x, y: abs(x) < T["hw"] + 0.10 and y > -0.25) if tunnel else None
    sd = vki_cav_ms_solid(k, fld, lambda x, y: vki_cav_height(x, y, code, seed),
                          lambda H: (VKI_FOOT_Z, 0.0, 0.25 * H, 0.5 * H, 0.75 * H), vki_cav_prof, seed, freeze=freeze,
                          bottom=False)
    k.meta["vki_open_bottom"] = VKI_FOOT_Z
    bm = k.bm
    if tunnel:                                                           # the fallen lintel and the dark at the back
        lv = vki_home_ico(k, (0.0, 0.10, T["lintel"] + 0.52), 1.0, VKI_STONE_BLOCK_IN, scale=(0.64, 0.30, 0.52),
                          sub=1, jit=0.03, seed=5, smooth=False)
        k.project(vki_faces_of(lv), VKI_STONE_BLOCK_IN)
        for v in lv:
            k.set_dark([v], 0.15)
        vki_adv_box(k, -T["hw"] + 0.01, T["hw"] - 0.01, T["back"] - 0.035, T["back"] - 0.02, 0.0, 2.4, VOID)
    for f in sd["tops"]:
        f.material_index = VKI_CAP
        for lp in f.loops:
            lp[k.uv].uv = (lp.vert.co.x / 1.2, lp.vert.co.y / 1.2)
    for f in sd["cliff"]:
        f.material_index = VKI_STONE_BLOCK_IN
    k.project(sd["sect"] + sd["bottoms"], VKI_STONE_BLOCK_IN)
    bm.normal_update()
    big = [f for f in sd["tops"] + sd["cliff"] + sd["sect"] + sd["bottoms"] if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    for f in bm.faces:                                                   # faceted cliffs, smooth tops (flat facets on
        f.smooth = f.material_index == VKI_CAP                           # the calm top texture read as a grid of tiles)
    for v in bm.verts:                                                   # grain, the damp foot, pale tops, the cleft
        k.set_dark([v], 0.12 * vki_hash01(int(round(v.co.x / 0.2)), int(round(v.co.y / 0.2 + v.co.z / 0.3)), seed + 5))
    vki_dun_damp(k)
    for f in bm.faces:
        if f.material_index == VKI_CAP:
            for v in f.verts:
                v[k.dark] = min(v[k.dark], 0.05)
    if tunnel:
        for v in bm.verts:
            if abs(v.co.x) < T["hw"] + 0.05 and v.co.y > -0.15 and v.co.z < T["lintel"] + 0.4:
                k.set_dark([v], 0.55)
    vki_cav_rock_mats(k)
    boxes = [[cx, cy, 1.1, w, d, 2.2] for cx, cy, w, d in vki_cav_boxes(lambda x, y: fld(x, y) > -VKI_CAV_FOOT)]
    k.meta.update(vki_class="rock", vki_corners=code, vki_nav="block", vki_collider=boxes or [[0, 0, -5, 0.01, 0.01, 0.01]],
                  vki_place_rule="dual grid: origin on a node (the tile centre), corners SW SE NE NW = the cells around "
                                 "it; rotation 0/90/180/270 (vki_cav_canon)")
    if arms:
        k.meta.update(vki_wall_arms=arms, vki_place_rule="dual grid, on a node with walls on the grid lines through it: "
                      "corners SW SE NE NW, wall arms S E N W (from the node to the tile edge); rotation 0/90/180/270 "
                      "(vki_cav_canon_arms)")
    if tunnel:
        k.meta.update(vki_tunnel=1, vki_nav="door", vki_trigger=[0.0, -0.45, 1.0, 0.8, 0.7, 2.0],
                      vki_spawn_local=[0.0, -1.60], vki_prompt_local=[0.0, -0.30, 1.40], vki_prompt_text="Go through",
                      vki_opening={"x0": -T["hw"], "x1": T["hw"], "z0": 0.0, "z1": T["lintel"], "head": "natural",
                                   "passage": 1})


# ---------------------------------------------------------------- the chasm: dual-grid ground tiles
# A chasm in a cave map is painted too: cells coded "vv" (or "==" under a bridge) are chasm (X), every other cell is
# ground (O). A ground tile stands on every node with chasm among its four cells: floor at 0 with the chasm's hole cut
# by the same kind of field (bilinear X +1 / O -1 plus windowed noise, both ways), rock walls down the hole that step
# in as they fall and darken to black, a VOID floor at -4.1. The tile carries the floor of its whole footprint, so
# the chasm can curve through cells freely; its FLOOR is world-locked (t 3.0), so ground tiles are never rotated and
# come in the four node parities Q00..Q11 (the noise differs per parity: four shapes per code). The floor round them
# is Floor_150 on whole cells and Floor_075 quarters where a cell is partly under ground tiles.
VKI_CAV_CHASM_LEVELS = (-4.0, -2.6, -1.3, -0.15)
VKI_CAV_CHASM_STEP = {-4.0: 0.0, -2.6: 0.20, -1.3: 0.11, -0.15: 0.03, 0.0: 0.0}   # the walls step in with depth


def vki_cav_ground(k, code, qa, qb):
    """ground tile `code` (corners SW SE NE NW, X chasm / O ground) at a node of parity (qa, qb)"""
    k.set_family("Cave")
    seed = vki_seed("CaveGround|%s|%d%d" % (code, qa, qb))
    s_ = lambda x, y: vki_cav_field(x, y, code.replace("X", "F"), seed, VKI_CAV_AMP, sym=True)
    sd = vki_cav_ms_solid(k, lambda x, y: -s_(x, y), lambda x, y: 0.0, lambda H: VKI_CAV_CHASM_LEVELS,
                          lambda z, H: VKI_CAV_CHASM_STEP.get(round(z, 2), 0.0), seed, wamp=0.08, bottom=False)
    k.meta["vki_open_bottom"] = VKI_CAV_CHASM_LEVELS[0]
    bm = k.bm
    vki_adv_box(k, -0.75, 0.75, -0.75, 0.75, -4.12, -4.04, VOID)          # the dark far below
    for f in sd["tops"]:
        f.material_index = VKI_FLOOR
        for lp in f.loops:
            lp[k.uv].uv = ((lp.vert.co.x + 0.75 + 1.5 * qa) / 3.0, (lp.vert.co.y + 0.75 + 1.5 * qb) / 3.0)
    for f in sd["cliff"]:
        f.material_index = VKI_STONE_BLOCK_IN
    k.project(sd["sect"] + sd["bottoms"], VKI_STONE_BLOCK_IN)
    bm.normal_update()
    big = [f for f in sd["tops"] + sd["cliff"] + sd["sect"] + sd["bottoms"] if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(bm, faces=big, quad_method="BEAUTY", ngon_method="BEAUTY")
    for f in bm.faces:
        f.smooth = f.material_index == VKI_FLOOR
    lip = {v for f in sd["cliff"] for v in f.verts if f.is_valid}
    for v in bm.verts:
        if v.co.z < -0.01:
            k.set_dark([v], vki_clamp(0.15 - v.co.z / 2.6) * 0.95)
    for f in bm.faces:                                                   # the floor darkens toward the lip
        if f.material_index == VKI_FLOOR:
            for v in f.verts:
                if abs(v.co.z) < 1e-6 and v in lip:
                    k.set_dark([v], 0.30)
    vki_cav_rock_mats(k)
    k.slot_mats[VKI_FLOOR] = "CaveFloor"                               # the default; a level's zone style overrides it
    hole = vki_cav_boxes(lambda x, y: s_(x, y) > -0.20)
    has_floor = bool(sd["tops"])
    k.meta.update(vki_class="ground", vki_corners=code, vki_q_parity=[qa, qb],
                  vki_uv_lock="world" if has_floor else "local", vki_nav="block" if hole else "walk",
                  vki_collider=[[cx, cy, 0.5, w, d, 1.0] for cx, cy, w, d in hole] or [[0, 0, -5, 0.01, 0.01, 0.01]],
                  vki_trap={"kind": "chasm", "depth": 4.0},
                  vki_place_rule="dual grid: origin on a node (i, j) with (i mod 2, j mod 2) = (%d, %d), rotation 0; "
                                 "corners SW SE NE NW = the cells around it" % (qa, qb))


def vki_cav_ground_void(k):
    """the all-chasm ground tile XXXX: only the dark far below (no floor, no parity)"""
    k.set_family("Cave")
    vki_adv_box(k, -0.75, 0.75, -0.75, 0.75, -4.12, -4.04, VOID)
    k.meta.update(vki_class="ground", vki_corners="XXXX", vki_nav="block", vki_uv_lock="local",
                  vki_collider=[[0.0, 0.0, 0.5, 1.5, 1.5, 1.0]], vki_trap={"kind": "chasm", "depth": 4.0},
                  vki_place_rule="dual grid: origin on a node, rotation 0")


def vki_cav_floor_quarter(k, a, b):
    """a quarter floor slab 0.75 x 0.75 from its min corner, z -0.10..0, FLOOR world-locked: its min corner sits at
    (0.75 a, 0.75 b) mod 3.0"""
    k.box((0.375, 0.375, -0.05), (0.75, 0.75, 0.10), VKI_FLOOR, bevel=0)
    k.bm.normal_update()
    for f in list(k.bm.faces):
        n = f.normal
        off = (0.25 * a, 0.25 * b) if abs(n.z) > 0.7 else ((0.25 * a, 0.0) if abs(n.y) > 0.7 else (0.25 * b, 0.0))
        k.project([f], VKI_FLOOR, offset=off)
    k.meta.update(vki_class="floor", vki_kind="Q075", vki_len=0.75, vki_q4=[a, b],
                  vki_place_rule="min corner (x, y) with (x / 0.75 mod 4, y / 0.75 mod 4) = (%d, %d)" % (a, b))


def vki_cav_bridge(k):
    """a rope bridge 4.2 m long along local y (a deck of planks -2.0..2.0 at x -0.45..0.45 sagging 0.25), four posts
    at y +-2.08, rope rails and hangers; it spans a chasm two cells wide (origin on the node between them).
    vki_bridge: the deck, where the walk BFS crosses the chasm; the colliders are the rails"""
    ya, yb = -2.0, 2.0
    sag = lambda y: -0.25 * 4 * ((y - ya) / (yb - ya)) * (1 - (y - ya) / (yb - ya))
    n = 22
    for i in range(n):
        y = ya + (yb - ya) * (i + 0.5) / n
        vki_adv_box(k, -0.45, 0.45, y - 0.08, y + 0.08, sag(y) + 0.005, sag(y) + 0.045, PLANKS, dark=0.1 * (i % 3))
    for x in (-0.47, 0.47):
        for y in (ya - 0.08, yb + 0.08):
            vki_dpr_rod(k, (x, y, -0.35), (x, y, 1.05), 0.08, WOOD)
        pts = [(x, ya - 0.08, 0.95)] + [(x, ya + (yb - ya) * t, sag(ya + (yb - ya) * t) + 0.85)
                                        for t in (0.2, 0.4, 0.6, 0.8)] + [(x, yb + 0.08, 0.95)]
        for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
            vki_dpr_rod(k, a, b, 0.024 if i % 2 else 0.028, BURLAP)
        for i in range(1, 6):
            y = ya + (yb - ya) * i / 6
            vki_dpr_rod(k, (x, y, sag(y) - 0.01), (x, y, sag(y) + 0.85), 0.015, BURLAP)
    k.slot_mats[WOOD] = "Dark"
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_collider=[[-0.47, 0.0, 0.5, 0.06, 4.4, 1.0], [0.47, 0.0, 0.5, 0.06, 4.4, 1.0]],
                  vki_bridge=[[-0.45, -2.1, 0.45, 2.1]],
                  vki_place_rule="origin on the node between the two chasm cells it spans, rotation 0 (N-S) or 90")


def vki_cav_rock_specs():
    """[(name, builder, grime)] for every rock tile, ground tile, quarter floor and the rope bridge"""
    out = []
    for m in vki_cav_codes():
        for var in VKI_CAV_VARIANTS.get(m, "AB"):
            out.append(("SM_VKI_Rock_Cave_%s_%s" % (m, var), (lambda k, m=m, var=var: vki_cav_tile(k, m, var)), "none"))
    out.append(("SM_VKI_Rock_Cave_OOFF_Tunnel", (lambda k: vki_cav_tile(k, "OOFF", "T", tunnel=True)), "none"))
    for m, ma in vki_cav_backed_keys():
        out.append(("SM_VKI_Rock_Cave_%s_Wall%s" % (m, ma), (lambda k, m=m, ma=ma: vki_cav_tile(k, m, "W" + ma, arms=ma)),
                    "none"))
    for a in "OX":
        for b in "OX":
            for c in "OX":
                for d in "OX":
                    code = a + b + c + d
                    if code in ("OOOO", "XXXX"):
                        continue
                    for qa in (0, 1):
                        for qb in (0, 1):
                            out.append(("SM_VKI_Ground_Cave_%s_Q%d%d" % (code, qa, qb),
                                        (lambda k, code=code, qa=qa, qb=qb: vki_cav_ground(k, code, qa, qb)), "none"))
    out.append(("SM_VKI_Ground_Cave_XXXX", vki_cav_ground_void, "none"))
    for a in range(4):
        for b in range(4):
            out.append(("SM_VKI_Floor_075_R%d%d" % (a, b), (lambda k, a=a, b=b: vki_cav_floor_quarter(k, a, b)), "floor"))
    out.append(("SM_VKI_Prop_RopeBridge_420", vki_cav_bridge, "none"))
    return out


# ---------------------------------------------------------------- pits: chasm, bridge, pool
VKI_CAV_CHASM = dict(y=(0.40, 2.60), depth=4.0, bands=(0.0, -1.3, -2.6, -4.0))


def vki_cav_jag(x, W, seed, amp):
    """a jag along x pinned to 0 at both tile ends (the tiles chain)"""
    return amp * math.sin(math.pi * x / W) * (vki_vnoise(x / 0.25, 3.3, seed) - 0.5) * 2.0


def vki_cav_chasm(k, bridge=False):
    """a chasm segment: one cell along x (tiles chain E-W, the edges pinned at the tile ends), two cells across. Rims
    at floor level (FLOOR slot, CaveFloor) with a jagged lip, rock walls stepping down in three bands to 4 m, darkening
    to black, a VOID floor. bridge: a sagging rope bridge across (planks, four posts, rope rails and hangers)."""
    W, D = 1.5, 3.0
    C = VKI_CAV_CHASM
    y0, y1 = C["y"]
    bands = C["bands"]
    xs = [W * i / 6 for i in range(7)]
    for side, (ya, sgn) in enumerate(((y0, -1.0), (y1, 1.0))):
        lip = lambda x, b=0: (ya + sgn * 0.0) + vki_cav_jag(x, W, 11 + side * 7 + b, 0.10) - sgn * 0.06 * b
        # rim slab (z -0.10 .. 0): from the tile edge to the lip
        for a, b in zip(xs[:-1], xs[1:]):
            yb = 0.0 if sgn < 0 else D
            poly = [(a, yb), (b, yb), (b, lip(b)), (a, lip(a))] if sgn < 0 else [(a, lip(a)), (b, lip(b)), (b, yb), (a, yb)]
            vs, fs = vki_prism(k, poly, -0.10, 0.0, VKI_FLOOR, axis="z", project=False)
            k.project(fs, VKI_FLOOR, tile=3.0)
        # the chasm wall in bands, each stepping back a little (its lip jag per band)
        for bi in range(len(bands) - 1):
            zt, zb_ = bands[bi], bands[bi + 1]
            for a, b in zip(xs[:-1], xs[1:]):
                fa, fb = lip(a, bi), lip(b, bi)
                ga, gb = lip(a, bi + 1), lip(b, bi + 1)
                back = ya + sgn * 0.38                # stays inside the tile (y 0.02 / 2.98: fp 1 x 2 cells)
                zt_ = zt - (0.10 if bi == 0 else 0.0)
                pts = [(a, back, zb_), (b, back, zb_), (b, gb, zb_), (a, ga, zb_),
                       (a, back, zt_), (b, back, zt_), (b, fb, zt_), (a, fa, zt_)]
                vs, fs = vki_sto_hexa(k, pts, VKI_STONE_BLOCK_IN)
                k.project(fs, VKI_STONE_BLOCK_IN, tile=1.5)
                for v in vs:
                    k.set_dark([v], vki_clamp(0.15 - v.co.z / 2.6) * 0.95)
    vki_adv_box(k, 0.0, W, y0 - 0.38, y1 + 0.38, bands[-1] - 0.25, bands[-1], VOID)
    cols = [[0.75, 1.5, 0.5, W, y1 - y0 + 0.1, 1.0]]
    if bridge:
        cols = [[0.14, 1.5, 0.5, 0.28, y1 - y0 + 0.1, 1.0], [W - 0.14, 1.5, 0.5, 0.28, y1 - y0 + 0.1, 1.0]]
        ya, yb = y0 - 0.25, y1 + 0.25
        sag = lambda y: -0.18 * 4 * ((y - ya) / (yb - ya)) * (1 - (y - ya) / (yb - ya))
        n = 16
        for i in range(n):
            y = ya + (yb - ya) * (i + 0.5) / n
            vki_adv_box(k, 0.30, 1.20, y - 0.055, y + 0.055, sag(y) + 0.005, sag(y) + 0.045, PLANKS, bev=0.006,
                        dark=0.1 * (i % 3))
        for x in (0.28, 1.22):
            for y in (ya - 0.08, yb + 0.08):
                vki_dpr_rod(k, (x, y, -0.35), (x, y, 1.05), 0.08, WOOD)
            pts = [(x, ya - 0.08, 0.95)] + [(x, ya + (yb - ya) * t, sag(ya + (yb - ya) * t) + 0.85) for t in (0.25, 0.5, 0.75)] + \
                [(x, yb + 0.08, 0.95)]
            for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
                vki_dpr_rod(k, a, b, 0.024 if i % 2 else 0.028, BURLAP)     # alternate widths: no coplanar joints
            for t in (0.2, 0.4, 0.6, 0.8):
                y = ya + (yb - ya) * t
                vki_dpr_rod(k, (x, y, sag(y) - 0.01), (x, y, sag(y) + 0.85), 0.015, BURLAP)
        k.slot_mats[WOOD] = "Dark"
    k.slot_mats[VKI_FLOOR] = "CaveFloor"
    vki_cav_rock_mats(k)
    k.meta.update(vki_class="pit", vki_covers_floor=[0.0, 0.0, W, D], vki_nav="block", vki_collider=cols,
                  vki_trap={"kind": "chasm", "depth": C["depth"]} if not bridge else {"kind": "bridge", "depth": C["depth"]},
                  vki_place_rule="origin on a node, rotation 0; chain tiles along x, wall to wall")


def vki_cav_chasm_plain(k): vki_cav_chasm(k, False)
def vki_cav_chasm_bridge(k): vki_cav_chasm(k, True)


def vki_cav_pool(k):
    """an underground pool (2 x 2 cells): a rocky shore sloping from floor level at the tile edge down to an irregular
    edge (-0.20), a steep inner bank to a dark bed (-0.62), a glossy dark water film meeting the shore at -0.135 and a
    few boulders on the shore. One closed solid: shore + bank + bed on top, a skirt at the tile edge, a bottom at -0.70"""
    S = 3.0
    cx = cy = S / 2
    ns = 24
    rnd = random.Random(17)
    rr = [1.0 + 0.16 * (vki_vnoise(i * 0.45, 1.0, 5) - 0.5) * 2 for i in range(ns)]
    inner, outer = [], []
    for i in range(ns):
        a = 2 * math.pi * i / ns
        dx, dy = math.cos(a), math.sin(a)
        inner.append((cx + dx * 1.02 * rr[i], cy + dy * 0.92 * rr[i]))
        t = min(cx / max(abs(dx), 1e-6), cy / max(abs(dy), 1e-6))          # the ray to the tile's square edge
        outer.append((cx + dx * t, cy + dy * t))
    bm = k.bm
    top_o = [bm.verts.new((x, y, 0.0)) for x, y in outer]
    top_i = [bm.verts.new((x, y, -0.20)) for x, y in inner]
    bot_i = [bm.verts.new((x, y, -0.62)) for x, y in inner]
    bot_o = [bm.verts.new((x, y, -0.70)) for x, y in outer]
    cb = bm.verts.new((cx, cy, -0.62)); cu = bm.verts.new((cx, cy, -0.70))
    fs = []
    for i in range(ns):
        j = (i + 1) % ns
        fs.append(bm.faces.new((top_o[i], top_o[j], top_i[j], top_i[i])))
        fs.append(bm.faces.new((top_i[i], top_i[j], bot_i[j], bot_i[i])))
        fs.append(bm.faces.new((bot_i[i], bot_i[j], cb)))
        fs.append(bm.faces.new((bot_o[i], bot_o[j], top_o[j], top_o[i])))
        fs.append(bm.faces.new((bot_o[j], bot_o[i], cu)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bm.normal_update()
    for f in fs:
        f.smooth = False
        z = min(v.co.z for v in f.verts)
        if f.normal.z > 0.5 and z > -0.3:
            k.project([f], VKI_FLOOR, tile=3.0)
        else:
            k.project([f], VKI_STONE_BLOCK_IN, tile=1.5)
    for v in top_i + bot_i + [cb]:
        k.set_dark([v], 0.35 if v.co.z > -0.3 else 0.85)
    # the water film: its edge on the shore where the shore is at -0.138 (t = 0.31 of the way out), top -0.135
    tw = 0.31
    ring = [(xi + (xo - xi) * tw, yi + (yo - yi) * tw) for (xi, yi), (xo, yo) in zip(inner, outer)]
    wt = [bm.verts.new((x, y, -0.135)) for x, y in ring]
    wb = [bm.verts.new((x, y, -0.16)) for x, y in ring]
    ct = bm.verts.new((cx, cy, -0.135)); cw = bm.verts.new((cx, cy, -0.16))
    wf = []
    for i in range(ns):
        j = (i + 1) % ns
        wf += [bm.faces.new((wt[i], wt[j], ct)), bm.faces.new((wb[j], wb[i], cw)),
               bm.faces.new((wb[i], wb[j], wt[j], wt[i]))]
    bmesh.ops.recalc_face_normals(bm, faces=wf)
    for f in wf:
        f.material_index = WATER
        for l in f.loops:
            l[k.uv].uv = (l.vert.co.x / 3.0, l.vert.co.y / 3.0)
    for i in range(5):
        a = 2 * math.pi * (i + 0.3) / 5 + rnd.uniform(-0.3, 0.3)
        d = rnd.uniform(1.22, 1.32)
        s_ = rnd.uniform(0.12, 0.22)
        v = vki_home_ico(k, (cx + math.cos(a) * d, cy + math.sin(a) * d * 0.95, s_ * 0.5 - 0.10), s_,
                         VKI_STONE_BLOCK_IN, scale=(1.1, 0.9, 0.75), sub=1, jit=0.02, seed=40 + i, smooth=False)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    k.slot_mats[WATER] = "M_VKI_Puddle"
    k.slot_mats[VKI_FLOOR] = "CaveFloor"
    vki_cav_rock_mats(k)
    k.meta.update(vki_class="pit", vki_covers_floor=[0.0, 0.0, S, S], vki_nav="block",
                  vki_collider=[[cx, cy, 0.5, 2.1, 1.9, 1.0]], vki_water=1,
                  vki_place_rule="origin on a node, rotation 0 (2 x 2 cells)")


# ---------------------------------------------------------------- cave dressing
def vki_cav_cone(k, c, r, h, segs=7, seed=0):
    """a knobbly rock cone (stalagmite), flat-shaded, rock"""
    rnd = random.Random(seed)
    prof = [(r, 0.0), (r * 0.82, h * 0.25), (r * 0.62, h * 0.52), (r * 0.36, h * 0.80), (0.0, h)]
    vs, fs = vki_home_lathe(k, prof, c=c, segs=segs, mi=VKI_STONE_BLOCK_IN, smooth=False)
    for v in vs:
        v.co.x += rnd.uniform(-0.15, 0.15) * r
        v.co.y += rnd.uniform(-0.15, 0.15) * r
    k.project(fs, VKI_STONE_BLOCK_IN, tile=1.5)
    for v in vs:
        k.set_dark([v], 0.25 * vki_smoothstep(0.4, 0.0, v.co.z - c[2]))
    return vs


def vki_cav_stalagmites(k):
    """five stalagmites 0.5-1.7 m in a clump"""
    for i, (x, y, r, h) in enumerate(((0.0, 0.05, 0.20, 1.65), (0.28, -0.15, 0.13, 0.95), (-0.25, -0.18, 0.12, 0.72),
                                      (0.22, 0.28, 0.10, 0.55), (-0.30, 0.25, 0.14, 1.10))):
        vki_cav_cone(k, (x, y, -0.02), r, h, seed=i)
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_cav_crystals(k):
    """a cluster of seven glowing crystals (hexagonal, 0.3-0.9 m, MUSH_GLOW cyan) on a rock base; cold light"""
    base = vki_home_ico(k, (0.0, 0.0, 0.06), 0.34, VKI_STONE_BLOCK_IN, scale=(1.0, 0.85, 0.40), sub=1, jit=0.03, seed=2,
                        smooth=False)
    k.project(vki_faces_of(base), VKI_STONE_BLOCK_IN)
    rnd = random.Random(6)
    for i, (x, y, h, r) in enumerate(((0.0, 0.0, 0.90, 0.09), (0.16, 0.05, 0.60, 0.07), (-0.14, 0.08, 0.66, 0.07),
                                      (0.06, -0.14, 0.48, 0.06), (-0.10, -0.12, 0.38, 0.05), (0.22, -0.10, 0.34, 0.05),
                                      (-0.22, -0.02, 0.30, 0.05))):
        d = Vector((x * 2.2 + rnd.uniform(-0.1, 0.1), y * 2.2 + rnd.uniform(-0.1, 0.1), 1.0)).normalized()
        rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        c = Vector((x, y, 0.10)) + d * (h / 2)
        _cyl(k, tuple(c), r, 0.008, h, 6, MUSH_GLOW, rot=rot)
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_lights=[dict(type="POINT", role="crystal", pos=[0.0, -0.25, 0.75], w=100.0, color=VKI_CAV_CRYSTAL_COL,
                                   range=6.0, flicker=0, shadows=0, radius=0.10)])


def vki_cav_mushrooms(k):
    """seven glowing cave mushrooms (pale stems, glowing cyan caps 0.06-0.16) in a clump; a faint cold light"""
    rnd = random.Random(3)
    for i, (x, y, h, r) in enumerate(((0.0, 0.0, 0.34, 0.16), (0.18, 0.08, 0.22, 0.10), (-0.16, 0.10, 0.26, 0.11),
                                      (0.08, -0.16, 0.16, 0.08), (-0.10, -0.14, 0.12, 0.07), (0.26, -0.08, 0.10, 0.06),
                                      (-0.26, -0.02, 0.18, 0.08))):
        _cyl(k, (x, y, h / 2 - 0.005), r * 0.28, r * 0.22, h, 5, MUSH_STEM)
        vki_home_lathe(k, [(r * 0.25, h - 0.01), (r, h + r * 0.15), (r * 0.8, h + r * 0.45), (0.0, h + r * 0.6)],
                       c=(x, y, 0.0), segs=6, mi=MUSH_GLOW)
    vki_home_meta(k, "floor", "dressing", use=[], vki_nav="block",
                  vki_lights=[dict(type="POINT", role="mushroom", pos=[0.0, -0.20, 0.45], w=50.0, color=VKI_CAV_CRYSTAL_COL,
                                   range=4.0, flicker=0, shadows=0, radius=0.08)])


def vki_cav_pillar(k, full):
    """a rock column where a stalagmite met its stalactite: Cut -- thick foot narrowing, sliced flat at 1.00 (CAP);
    Full -- waisted at 1.6 m and flaring to the 3.0 slice"""
    rnd = random.Random(8 if full else 9)
    prof = [(0.46, 0.0), (0.36, 0.35), (0.29, 0.75), (0.27, 1.0)] if not full else \
        [(0.46, 0.0), (0.34, 0.45), (0.22, 1.20), (0.20, 1.60), (0.26, 2.20), (0.40, 2.75), (0.44, 3.0)]
    vs, fs = vki_home_lathe(k, prof, c=(0.0, 0.0, -0.02), segs=10, mi=VKI_STONE_BLOCK_IN, smooth=False)
    for v in vs:
        if -0.01 < v.co.z < (0.98 if not full else 2.98):
            f_ = 1.0 + rnd.uniform(-0.12, 0.10)
            v.co.x *= f_; v.co.y *= f_
    k.bm.normal_update()
    for f in fs:
        if f.normal.z > 0.9 and min(v.co.z for v in f.verts) > (0.9 if not full else 2.9):
            k.project([f], VKI_CAP)
        else:
            k.project([f], VKI_STONE_BLOCK_IN, tile=1.5)
    for v in vs:
        k.set_dark([v], 0.2 * vki_smoothstep(0.5, 0.0, v.co.z))
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block",
                  vki_collider=[[0.0, 0.0, 0.5 if not full else 1.5, 0.9, 0.9, 1.0 if not full else 3.0]])


def vki_cav_pillar_cut(k): vki_cav_pillar(k, False)
def vki_cav_pillar_full(k): vki_cav_pillar(k, True)


def vki_cav_boulders(k):
    """three boulders (0.25-0.45) resting together"""
    for i, (x, y, r) in enumerate(((0.0, 0.05, 0.45), (0.40, -0.22, 0.28), (-0.38, -0.25, 0.25))):
        v = vki_home_ico(k, (x, y, r), r, VKI_STONE_BLOCK_IN, scale=(1.1, 0.95, 0.78), sub=2, jit=0.04 * r / 0.3,
                         seed=10 + i, rest=0.0, smooth=False)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
        for vv in v:
            k.set_dark([vv], 0.05 + 0.25 * vki_smoothstep(r, 0.0, vv.co.z))
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "furniture", use=[], vki_nav="block")


def vki_cav_gravel(k):
    """scree: a low heap of damp grit (the FLOOR slot, EarthDamp by default) strewn with rock chips and pebbles
    (~1.1 x 0.8 m)"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.55, 0.40, 0.05, VKI_FLOOR, z0=0.001, nr=2, ns=12, seed=9, wob=0.2, bump=0.4)
    rnd = random.Random(10)
    for i in range(16):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.0, 1.0) ** 0.7
        c = (math.cos(a) * d * 0.55, math.sin(a) * d * 0.40, 0.035 * (1 - d * d) + 0.012)
        v = _ico(k, c, rnd.uniform(0.03, 0.07), VKI_STONE_BLOCK_IN, scale=(1, 0.8, 0.55), sub=0, jit=0.008, seed=20 + i)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    k.slot_mats[VKI_FLOOR] = "EarthDamp"
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


def vki_cav_spill(k):
    """earth and rubble spilling over a floor seam (a cave floor meeting flagstones where a wall is gone or was never
    built): a low heap of the FLOOR slot (CaveFloor by default) about 0.8 x 1.0 m, long across the seam (y), with rock
    chips; laid on a cell edge at its midpoint it stays clear of the post squares on the nodes"""
    vki_dpr_mound(k, (0.0, 0.0, 0.0), 0.34, 0.50, 0.07, VKI_FLOOR, z0=0.001, nr=2, ns=14, seed=31, wob=0.18, bump=0.4)
    rnd = random.Random(32)
    for i in range(14):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.0, 1.0) ** 0.7
        c = (math.cos(a) * d * 0.30, math.sin(a) * d * 0.44, 0.05 * (1 - d * d) + 0.012)
        v = _ico(k, c, rnd.uniform(0.03, 0.08), VKI_STONE_BLOCK_IN, scale=(1, 0.8, 0.55), sub=0, jit=0.008, seed=40 + i)
        k.project(vki_faces_of(v), VKI_STONE_BLOCK_IN)
    k.slot_mats[VKI_FLOOR] = "CaveFloor"
    vki_cav_rock_mats(k)
    vki_home_meta(k, "floor", "dressing", use=[], vki_class="overlay", vki_nav="none")


# ---------------------------------------------------------------- specs
VKI_CAV_SPECS = vki_cav_rock_specs() + [
    ("SM_VKI_Pit_Chasm_150x300", vki_cav_chasm_plain, "none"),
    ("SM_VKI_Pit_ChasmBridge_150x300", vki_cav_chasm_bridge, "none"),
    ("SM_VKI_Pit_Pool_300x300", vki_cav_pool, "none"),
    ("SM_VKI_Prop_Stalagmites", vki_cav_stalagmites, "prop"),
    ("SM_VKI_Prop_Crystals", vki_cav_crystals, "none"),
    ("SM_VKI_Prop_Mushrooms_Glow", vki_cav_mushrooms, "none"),
    ("SM_VKI_Prop_RockPillar_Cut", vki_cav_pillar_cut, "prop"),
    ("SM_VKI_Prop_RockPillar_Full", vki_cav_pillar_full, "prop"),
    ("SM_VKI_Prop_Boulders", vki_cav_boulders, "prop"),
    ("SM_VKI_Overlay_Gravel", vki_cav_gravel, "none"),
    ("SM_VKI_Overlay_Spill", vki_cav_spill, "none"),
]
VKI_CAV_NAMES = [n for n, _, _ in VKI_CAV_SPECS]
VKI_CAV_ROCK_NAMES = [n for n in VKI_CAV_NAMES if n.startswith("SM_VKI_Rock_") and "_Wall" not in n]
VKI_CAV_BACKED_NAMES = [n for n in VKI_CAV_NAMES if n.startswith("SM_VKI_Rock_") and "_Wall" in n]
VKI_CAV_GROUND_NAMES = [n for n in VKI_CAV_NAMES if n.startswith(("SM_VKI_Ground_", "SM_VKI_Floor_075_"))] +     ["SM_VKI_Prop_RopeBridge_420"]
vki_register([(n, fn, {"grime": gr}, "adventure") for n, fn, gr in VKI_CAV_SPECS])
