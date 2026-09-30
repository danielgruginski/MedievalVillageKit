# ===================== VKI TEST: acceptance tests (§9) + the C1 test pieces =====================
# Loaded by vki_ns() (last entry of VKI_TEXTS):
#   g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"]()
#   g["vki_test_pieces"](["SM_VKI_..."])  -> {} when clean, else {piece: {test: [errors]}}
# Every vki_tN_* function returns a list of error strings ([] = pass).
import bpy, bmesh, math, json, hashlib, os
from mathutils import Vector, Matrix


# ---------------------------------------------------------------- test pieces (NOT shipped)
def vki_build_test_smoke(k):
    """SM_VKI_Test_Smoke -- NOT SHIPPED. Plain 1.5 m box wall, 0.5 thick (Timber class O), z -0.30..3.0, wobble,
    Full only; top face CAP. Exercises body_box / vki_wobble / finish for the C1 acceptance tests."""
    k.set_family("Timber")
    k.body_box(0.0, 1.5, VKI_FOOT_Z, 3.0)
    for f in list(k.bm.faces):
        if f.normal.z > 0.7 and f.calc_center_median().z > 2.99:
            k.project([f], VKI_CAP)
    vki_wobble(k, 1.5, "Timber", "A", holes=[], top_body_fn=lambda x: 3.0)
    k.meta.update(vki_class="wall", vki_kind="Test", vki_len=1.5, vki_height="Full", vki_test_piece=1,
                  vki_shipped=0, vki_note="C1 smoke piece, not shipped")


def vki_pyramid(k, base_c, axis, w, h, mi):
    """closed square pyramid: base centred on base_c, perpendicular to axis (a unit Vector), apex at base_c+axis*h"""
    ax = Vector(axis).normalized()
    u = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = (u - ax * u.dot(ax)).normalized(); v = ax.cross(u)
    c = Vector(base_c)
    b = [k.bm.verts.new(c + (u * sx + v * sy) * (w / 2)) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    ap = k.bm.verts.new(c + ax * h)
    fs = [k.bm.faces.new(b)] + [k.bm.faces.new((b[i], b[(i + 1) % 4], ap)) for i in range(4)]
    bmesh.ops.recalc_face_normals(k.bm, faces=fs)
    k.bm.normal_update()
    k.project(fs, mi)
    return fs


def vki_build_test_axis(k):
    """SM_VKI_Test_Axis -- NOT SHIPPED: red +X, green +Y, blue +Z arrows (1 m) on a pale origin block"""
    k.box((0, 0, 0.06), (0.16, 0.16, 0.12), VKI_CAP, bevel=0.01)
    for d, mi in (((1, 0, 0), CLOTH_A), ((0, 1, 0), LEAF), ((0, 0, 1), CLOTH_B)):
        d = Vector(d)
        base = Vector((0, 0, 0.06)) if d.z == 0 else Vector((0, 0, 0.12))
        c = base + d * (0.08 + 0.36) if d.z == 0 else base + d * 0.36
        size = [0.05, 0.05, 0.05]
        size[[0, 1, 2][list(d).index(1)]] = 0.72
        k.box(tuple(c), tuple(size), mi, bevel=0.005)
        tip0 = c + d * 0.36
        vki_pyramid(k, tip0, d, 0.14, 0.2, mi)
    k.slot_mats = {CLOTH_B: "Blue"}
    k.meta.update(vki_class="test", vki_kind="Axis", vki_test_piece=1, vki_shipped=0,
                  vki_note="orientation marker: red +X, green +Y, blue +Z; not shipped")


vki_register([("SM_VKI_Test_Axis", vki_build_test_axis, {"grime": "none"}, "core"),
              ("SM_VKI_Test_Smoke", vki_build_test_smoke, {"grime": "wall"}, "core")])


# ---------------------------------------------------------------- helpers
def vki_obj(o):
    return bpy.data.objects[o] if isinstance(o, str) else o


def vki_np_co(me):
    import numpy
    a = numpy.empty(len(me.vertices) * 3, numpy.float64)
    me.vertices.foreach_get("co", a)
    return a.reshape(-1, 3)


def vki_fp(o):
    try:
        v = [float(t) for t in str(o.get("vki_footprint", "")).split(",")]
        return v if len(v) == 4 else None
    except ValueError:
        return None


def vki_cls_of(o):
    return "P" if float(o.get("vki_thick", 0.5)) < 0.4 else "O"


def vki_kd(points):
    from mathutils.kdtree import KDTree
    t = KDTree(max(1, len(points)))
    for i, p in enumerate(points):
        t.insert(p, i)
    t.balance()
    return t


def vki_match(A, B, tol=1e-5):
    """points of A without a partner in B within tol (and vice versa): (missA, missB)"""
    tb, ta = vki_kd(B), vki_kd(A)
    ma = [p for p in A if not B or tb.find(p)[2] > tol]
    mb = [p for p in B if not A or ta.find(p)[2] > tol]
    return ma, mb


# ---------------------------------------------------------------- T1 bounds
def vki_t1_bounds(o):
    o = vki_obj(o); errs = []
    fp = vki_fp(o)
    if fp is None:
        return [f"T1 {o.name}: no vki_footprint"]
    co = vki_np_co(o.data)
    if not len(co):
        return [f"T1 {o.name}: empty mesh"]
    tol = 1e-5
    x0, y0, x1, y1 = fp
    mn, mx = co.min(0), co.max(0)
    if mn[0] < x0 - tol or mn[1] < y0 - tol or mx[0] > x1 + tol or mx[1] > y1 + tol:
        errs.append(f"T1 {o.name}: geometry x {mn[0]:.5f}..{mx[0]:.5f} y {mn[1]:.5f}..{mx[1]:.5f} outside "
                    f"footprint {fp}")
    cls, fam, ht, kind = o.get("vki_class"), o.get("vki_family"), o.get("vki_height"), o.get("vki_kind")
    H = VKI_CUT_H if ht == "Cut" else VKI_H_FULL.get(fam, 3.0)
    if cls == "wall":
        top = H + (VKI_POST_TOP if (o.get("vki_special") or kind in ("Fireplace", "Hearth", "Forge")) else 0.0)
        if mn[2] < VKI_FOOT_Z - tol or mx[2] > top + tol:
            errs.append(f"T1 {o.name}: wall z {mn[2]:.4f}..{mx[2]:.4f} outside [-0.30, {top}]")
        if float(o.get("vki_len", 0)) and (mn[0] < -tol or mx[0] > float(o["vki_len"]) + tol):
            errs.append(f"T1 {o.name}: wall x outside [0, L]")
    elif cls == "post":
        c = vki_cls_of(o)
        ax, ay = VKI_MID_HW[c] if kind == "Mid" else (VKI_POST_HW[c], VKI_POST_HW[c])
        top = H + VKI_POST_TOP
        if abs(co[:, 0]).max() > ax + tol or abs(co[:, 1]).max() > ay + tol:
            errs.append(f"T1 {o.name}: post outside its envelope +-{ax} x +-{ay}")
        if mn[2] < VKI_POST_Z0 - tol or mx[2] > top + tol:
            errs.append(f"T1 {o.name}: post z {mn[2]:.4f}..{mx[2]:.4f} outside [-0.30, {top}]")
    elif cls == "floor":
        S = float(o.get("vki_len") or (x1 - x0))
        ztop = VKI_Z["dais"] if kind == "Dais" else 0.0
        if kind not in ("Sill",) and (mn[0] < -tol or mn[1] < -tol or mx[0] > S + tol or mx[1] > S + tol):
            errs.append(f"T1 {o.name}: floor outside [0,{S}]^2")
        if kind not in ("Sill",) and (mn[2] < -0.10 - tol or mx[2] > ztop + tol):
            errs.append(f"T1 {o.name}: floor z {mn[2]:.4f}..{mx[2]:.4f} outside [-0.10, {ztop}]")
    return errs


# ---------------------------------------------------------------- T2 end profiles / T3 node zone
def vki_ref_name(o, height):
    return f"SM_VKI_Wall_{o.get('vki_family')}_Plain_150A_{height}"


def vki_end_pts(o, x, tol=1e-5):
    return [Vector(v.co) for v in o.data.vertices if abs(v.co.x - x) <= tol]


def vki_t2_end_profiles(o, ref_full=None, ref_cut=None):
    """end-plane vertices equal the family's Plain_150A profile (1e-5); Full = Cut for z <= 0.65; rakes: Cut
    profile at the low end, Full at the high end"""
    o = vki_obj(o); errs = []
    L = float(o.get("vki_len", 1.5)); ht = o.get("vki_height")
    rf = bpy.data.objects.get(ref_full or vki_ref_name(o, "Full"))
    rc = bpy.data.objects.get(ref_cut or vki_ref_name(o, "Cut"))
    if ht == "Rake":
        low_r = str(o.name).endswith("_R")
        ends = ((L if low_r else 0.0, rc, 0.0), (0.0 if low_r else L, rf, 1.5))
    else:
        r = rf if ht != "Cut" else rc
        ends = ((0.0, r, 0.0), (L, r, 1.5))
    for x, ref, rx in ends:
        if ref is None:
            errs.append(f"T2 {o.name}: reference Plain_150A ({'Cut' if ref is rc else 'Full'}) missing"); continue
        A = [Vector((0, p.y, p.z)) for p in vki_end_pts(o, x)]
        B = [Vector((0, p.y, p.z)) for p in vki_end_pts(ref, rx)]
        ma, mb = vki_match(A, B)
        if ma or mb:
            errs.append(f"T2 {o.name}: end x={x}: {len(ma)} vertices off the {ref.name} profile, {len(mb)} missing")
    twin = bpy.data.objects.get(o.get("vki_cut_pair", "")) if ht == "Full" else None
    if twin is not None:
        A = [Vector(v.co) for v in o.data.vertices if v.co.z <= 0.65 + 1e-6]
        B = [Vector(v.co) for v in twin.data.vertices if v.co.z <= 0.65 + 1e-6]
        ma, mb = vki_match(A, B)
        if ma or mb:
            errs.append(f"T2 {o.name}: Full != Cut below 0.65 ({len(ma)} / {len(mb)} unmatched vertices)")
    return errs


def vki_t3_node_zone(o, ref=None):
    """within 0.32 of an end node: plain-section vertices (as in Plain_150A) or inside the surround envelope;
    clear openings (vki_opening) inside [0.33, L-0.33]"""
    o = vki_obj(o); errs = []
    L = float(o.get("vki_len", 1.5)); c = vki_cls_of(o)
    ht = o.get("vki_height")
    Hf = VKI_H_FULL.get(o.get("vki_family"), 3.0)
    # per end: (reference plain piece, post top). Rakes (C3 fix): the low end is the Cut section under a Cut-height
    # post, the high end the Full section (as T2 already compares them)
    if ht == "Rake":
        low_r = str(o.name).endswith("_R")
        cut = (vki_ref_name(o, "Cut"), VKI_CUT_H + VKI_POST_TOP); full = (vki_ref_name(o, "Full"), Hf + VKI_POST_TOP)
        ends = {"x0": full if low_r else cut, "xL": cut if low_r else full}
    else:
        e_ = (ref or vki_ref_name(o, "Cut" if ht == "Cut" else "Full"),
              (VKI_CUT_H if ht == "Cut" else Hf) + VKI_POST_TOP)
        ends = {"x0": e_, "xL": e_}
    trees = {}
    for key, (rn, _t) in ends.items():
        r = bpy.data.objects.get(rn)
        if r is None:
            return [f"T3 {o.name}: reference plain piece {rn} missing"]
        trees[key] = vki_kd([Vector(v.co) for v in r.data.vertices])
    bad = 0
    for v in o.data.vertices:
        x, y, z = v.co
        if VKI_NODE_FLAT <= x <= L - VKI_NODE_FLAT:
            continue
        key = "x0" if x < VKI_NODE_FLAT else "xL"
        top = ends[key][1]
        xm = x if x < VKI_NODE_FLAT else L - x
        if VKI_ENV_X[0] - 1e-6 <= xm <= VKI_ENV_X[1] + 1e-6 and abs(y) <= VKI_ENV_Y[c] + 1e-6 and z <= top + 1e-6:
            continue
        p = Vector((x, y, z)) if x < VKI_NODE_FLAT else Vector((x - L + 1.5, y, z))
        if trees[key].find(p)[2] <= 1e-5:
            continue
        bad += 1
    if bad:
        errs.append(f"T3 {o.name}: {bad} vertices in the node zone are neither plain section nor in the envelope")
    op = vki_get(o, "vki_opening", None)
    rects = op if isinstance(op, list) else ([op] if isinstance(op, dict) else [])
    for rc in rects:
        x0 = rc.get("x0") if isinstance(rc, dict) else rc[0]
        x1 = rc.get("x1") if isinstance(rc, dict) else rc[2]
        if x0 < VKI_OPEN_MIN - 1e-6 or x1 > L - VKI_OPEN_MIN + 1e-6:
            errs.append(f"T3 {o.name}: opening {x0}..{x1} outside [0.33, L-0.33]")
    return errs


# ---------------------------------------------------------------- T4 coverage rigs
def vki_t4_rigs(fam, corner, mid, full, cut=None, fam2_full=None, fam2_mid=None, p_full=None, o_corner=None,
                origin=(0.0, -30.0), step=6.0, scene="VKI_Test"):
    """lay out the T4 rigs for one family in `scene` (collections VKI_Rig_T4_<fam>_<rig>) from the names you pass:
    corner / mid posts and full / cut Plain_150A walls; fam2_full + fam2_mid: the family-step neighbour wall and
    the Mid post that wins by priority; p_full + o_corner: a P partition teeing into this (O) family's wall with an
    O Corner post. Every rig has its node at its local (0, 0). Returns {rig: dict(objs, node)}"""
    rigs = {}
    plan = [("L", [(full, 0, 0, 0), (full, 0, 0, 90), (corner, 0, 0, 0)]),
            ("T", [(full, 0, 0, 0), (full, 0, 0, 180), (full, 0, 0, 90), (corner, 0, 0, 0)]),
            ("X", [(full, 0, 0, 0), (full, 0, 0, 180), (full, 0, 0, 90), (full, 0, 0, -90), (corner, 0, 0, 0)]),
            ("End", [(full, 0, 0, 0), (mid, 0, 0, 0)])]
    if cut:
        plan.append(("FullCut", [(full, -1.5, 0, 0), (cut, 0, 0, 0), (mid, 0, 0, 0)]))
    if fam2_full:
        plan.append(("FamStep", [(full, -1.5, 0, 0), (fam2_full, 0, 0, 0), (fam2_mid or mid, 0, 0, 0)]))
    if p_full:
        plan.append(("PintoO", [(full, -1.5, 0, 0), (full, 0, 0, 0), (p_full, 0, 0, -90), (o_corner or corner, 0, 0, 0)]))
    for i, (tag, items) in enumerate(plan):
        ox, oy = origin[0] + i * step, origin[1]
        rigs[tag] = dict(objs=vki_rig(f"T4_{fam}_{tag}", items, origin=(ox, oy), scene=scene), node=(ox, oy))
    return rigs


def vki_depsgraph(sc):
    """the scene's evaluated depsgraph; a scene that was never evaluated (e.g. non-active after a Blender restart)
    has none until ViewLayer.update() creates it"""
    vl = sc.view_layers[0]
    dg = vl.depsgraph
    if dg is None:
        vl.update()
        dg = vl.depsgraph
    dg.update()
    return dg


def vki_node_ends(walls, node, tol=1e-4):
    """[(wall, end_x, outward 2-D direction)] for every wall instance with an end (local x 0 or L) at `node`"""
    N = Vector(node[:2]); out = []
    for w in walls:
        L = float(w.get("vki_len") or 0.0)
        if not L:
            continue
        mw = vki_mw(w)
        p0 = (mw @ Vector((0, 0, 0))).to_2d(); p1 = (mw @ Vector((L, 0, 0))).to_2d()
        if (p0 - N).length < tol:
            out.append((w, 0.0, (p1 - p0).normalized()))
        elif (p1 - N).length < tol:
            out.append((w, L, (p0 - p1).normalized()))
    return out


def vki_node_square(ends):
    """the FIXED node square a post must cover (core fix, review r2): (kind, half x, half y). An L/T/X node (two
    non-collinear wall directions) needs +-POST_HW; a straight run / free end the Mid post's +-MID_HW along the wall
    x +-POST_HW across. Class = the thickest class present."""
    cls = "O" if any(float(w.get("vki_thick", 0.5)) >= 0.4 for w, _, _ in ends) else "P"
    dirs = [d for _, _, d in ends]
    if any(abs(a.x * b.y - a.y * b.x) > 0.5 for a in dirs for b in dirs):
        return "Corner", VKI_POST_HW[cls], VKI_POST_HW[cls]
    along, across = VKI_MID_HW[cls]
    return ("Mid",) + ((along, across) if abs(dirs[0].x) > 0.5 else (across, along))


def vki_t4_coverage(rigs, scene="VKI_Test", margin=0.005, ray_step=0.02):
    """T4 per node (core fix, review r2: the old test took its square from the post's own bbox, so an undersized
    post always passed):
    (a) the post's plan box covers the FIXED node square (vki_node_square: +-POST_HW at L/T/X, the Mid square at
        straight runs and free ends);
    (b) every wall vertex inside the node square lies inside the post (x/y margin 0.005, z <= post top - 0.005);
    (c) the open end outline (walls have no end faces since the core fix): every end-plane vertex of a wall end at
        the node that has no identical partner on a collinear neighbour's end lies inside the post (same margin);
    (d) a 2 cm grid of vertical rays over the node square hits the post first (the square's chamfer corners skipped)."""
    sc = bpy.data.scenes[scene]
    errs = []
    dg = vki_depsgraph(sc)
    for tag, rg in rigs.items():
        node = Vector(rg["node"][:2])
        walls = [o for o in rg["objs"] if o.get("vki_class") == "wall"]
        posts = [o for o in rg["objs"] if o.get("vki_class") == "post" and
                 (vki_mw(o).translation.to_2d() - node).length < 1e-4]
        if not posts:
            errs.append(f"T4 {tag}: no post at the node"); continue
        p = posts[0]
        ends = vki_node_ends(walls, node)
        if not ends:
            errs.append(f"T4 {tag}: no wall end at the node"); continue
        kind, hx, hy = vki_node_square(ends)
        S = (node.x - hx, node.y - hy, node.x + hx, node.y + hy)
        bb = [vki_mw(p) @ Vector(c) for c in p.bound_box]
        px0, py0, pz0 = (min(v[i] for v in bb) for i in range(3))
        px1, py1, pz1 = (max(v[i] for v in bb) for i in range(3))
        if px0 > S[0] + 1e-4 or py0 > S[1] + 1e-4 or px1 < S[2] - 1e-4 or py1 < S[3] - 1e-4:
            errs.append(f"T4 {tag}: {p.name} ({px1 - px0:.3f} x {py1 - py0:.3f}) does not cover the {kind} node "
                        f"square ({2 * hx:.2f} x {2 * hy:.2f})")

        def inside(q):
            return (px0 + margin - 1e-6 <= q.x <= px1 - margin + 1e-6 and py0 + margin - 1e-6 <= q.y <= py1 - margin +
                    1e-6 and pz0 - 1e-4 <= q.z <= pz1 - margin + 1e-6)
        nbad = 0
        for w in walls:
            mw = vki_mw(w)
            for v in w.data.vertices:
                q = mw @ v.co
                if S[0] - 1e-6 <= q.x <= S[2] + 1e-6 and S[1] - 1e-6 <= q.y <= S[3] + 1e-6 and not inside(q):
                    nbad += 1
        if nbad:
            errs.append(f"T4 {tag}: {nbad} wall vertices in the node square are not inside {p.name}")
        endpts = {w.name: [vki_mw(w) @ v.co for v in w.data.vertices if abs(v.co.x - xe) <= 1e-5]
                  for w, xe, d in ends}
        nopen = 0
        for w, xe, d in ends:
            partners = [q for w2, _, d2 in ends if w2 is not w and d2.dot(d) < -0.999 for q in endpts[w2.name]]
            tree = vki_kd(partners) if partners else None
            for q in endpts[w.name]:
                if tree is not None and tree.find(q)[2] <= 1e-5:
                    continue
                if not inside(q):
                    nopen += 1
        if nopen:
            errs.append(f"T4 {tag}: {nopen} open-end outline vertices are not covered by {p.name}")
        miss = 0
        x = S[0] + 0.01
        while x <= S[2] - 0.01 + 1e-9:
            y = S[1] + 0.01
            while y <= S[3] - 0.01 + 1e-9:
                # skip rays in the chamfer corners (bevel 0.02): hit / miss on the chamfer diagonal is luck
                if min(x - S[0], S[2] - x) + min(y - S[1], S[3] - y) < VKI_POST_BEVEL + 0.005:
                    y += ray_step
                    continue
                hit, loc, nrm, idx, ob, mat = sc.ray_cast(dg, Vector((x, y, pz1 + 5.0)), Vector((0, 0, -1)))
                if not hit or ob.original.name != p.name:
                    miss += 1
                y += ray_step
            x += ray_step
        if miss:
            errs.append(f"T4 {tag}: {miss} rays over the node square do not hit {p.name} first")
    return errs


# ---------------------------------------------------------------- T5 coplanar faces between objects
def vki_tris_world(o):
    me = o.data
    me.calc_loop_triangles()
    mw = vki_mw(o)
    co = [mw @ v.co for v in me.vertices]
    out = []
    for t in me.loop_triangles:
        a, b, c = (co[i] for i in t.vertices)
        n = (b - a).cross(c - a)
        if n.length < 1e-12:
            continue
        n.normalize()
        out.append((a, b, c, n, n.dot(a)))
    return out


def vki_clip_poly(P, Q):
    """Sutherland-Hodgman: polygon P clipped by convex CCW polygon Q (2-D tuples)"""
    out = P
    for i in range(len(Q)):
        a, b = Q[i], Q[(i + 1) % len(Q)]
        inp, out = out, []
        if not inp:
            break
        side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        for j in range(len(inp)):
            cur, prv = inp[j], inp[j - 1]
            sc_, sp_ = side(cur), side(prv)
            if sc_ >= 0:
                if sp_ < 0:
                    t = sp_ / (sp_ - sc_); out.append((prv[0] + t * (cur[0] - prv[0]), prv[1] + t * (cur[1] - prv[1])))
                out.append(cur)
            elif sp_ >= 0:
                t = sp_ / (sp_ - sc_); out.append((prv[0] + t * (cur[0] - prv[0]), prv[1] + t * (cur[1] - prv[1])))
    return out


def vki_area2(P):
    return sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P))) / 2


def vki_t5_coplanar(objs, dot=0.999, dist=1e-4, min_area=1e-6, max_report=20, buried_ok=True):
    """same-facing triangles of different objects on one plane (n.n > 0.999, plane distance < 1e-4) that overlap,
    unless the overlap centroid lies inside a post box"""
    posts = []
    for o in objs:
        if o.get("vki_class") == "post":
            bb = [vki_mw(o) @ Vector(c) for c in o.bound_box]
            posts.append(([min(v[i] for v in bb) for i in range(3)], [max(v[i] for v in bb) for i in range(3)]))
    owned = [(oi, tr) for oi, o in enumerate(objs) if o.type == "MESH" for tr in vki_tris_world(o)]
    parts = []
    for o in objs:
        if o.type == "MESH":
            mw = vki_mw(o)
            parts.append(([mw @ v.co for v in o.data.vertices], [tuple(p_.vertices) for p_ in o.data.polygons]))
    return vki_coplanar_pairs(owned, [o.name for o in objs], posts, dot, dist, min_area, max_report, "T5",
                              covers=vki_bvh_solids(parts) if buried_ok else ())


def vki_islands(me):
    """loose-part index per vertex of a mesh"""
    bm = bmesh.new(); bm.from_mesh(me)
    isl = [-1] * len(bm.verts); bm.verts.ensure_lookup_table(); ni = 0
    for v in bm.verts:
        if isl[v.index] >= 0:
            continue
        st = [v]; isl[v.index] = ni
        while st:
            a = st.pop()
            for e in a.link_edges:
                b = e.other_vert(a)
                if isl[b.index] < 0:
                    isl[b.index] = ni; st.append(b)
        ni += 1
    bm.free()
    return isl, ni


def vki_t5s_self_coplanar(o, dot=0.999, dist=1e-4, min_area=1e-6, max_report=12):
    """T5S (core fix, per master): same-facing faces of ONE master that lie in the same plane (n.n > 0.999, plane
    distance < 1e-4) and overlap by more than min_area (1e-6 m2) are an error -- they z-fight wherever they show,
    and 'buried' duplicates show the moment a neighbour changes. Exact polygon overlap (triangle clipping), every
    pair of different polygons (also inside one loose part), no buried exception. The only exception: faces in a
    wall's end planes x = 0 / x = L (covered by a post or the neighbour; VKIKit.finish removes the outward ones)."""
    o = vki_obj(o)
    me = o.data
    me.calc_loop_triangles()
    wall = o.get("vki_class") == "wall"
    L = float(o.get("vki_len") or 0.0)
    isl, _ = vki_islands(me)
    co = [Vector(v.co) for v in me.vertices]
    buckets = {}
    for t in me.loop_triangles:
        a, b, c = (co[i] for i in t.vertices)
        n = (b - a).cross(c - a)
        if n.length < 1e-12:
            continue
        n.normalize()
        if wall and abs(n.x) > dot and any(all(abs(co[i].x - xe) <= 1e-5 for i in t.vertices) for xe in (0.0, L)):
            continue
        d = n.dot(a)
        key = (round(n.x, 2), round(n.y, 2), round(n.z, 2), round(d, 3))
        buckets.setdefault(key, []).append((t.polygon_index, (a, b, c), n, d, isl[t.vertices[0]]))
    errs = []; seen = set(); tot = 0; area_max = 0.0
    for key, lst in buckets.items():
        cand = list(lst)
        for dd in (-0.001, 0.001):
            cand += buckets.get((key[0], key[1], key[2], round(key[3] + dd, 3)), [])
        if len({c_[0] for c_ in cand}) < 2:
            continue
        n0 = lst[0][2]
        u = Vector((0, 0, 1)) if abs(n0.z) < 0.9 else Vector((1, 0, 0))
        u = (u - n0 * u.dot(n0)).normalized(); v = n0.cross(u)
        proj = []
        for pi, tri, n, d, il in cand:
            P = [(p.dot(u), p.dot(v)) for p in tri]
            if vki_area2(P) < 0:
                P = P[::-1]
            proj.append((pi, n, d, il, P, tri))
        for i in range(len(proj)):
            for j in range(i + 1, len(proj)):
                pa_, na, da, ia, Pa, ta = proj[i]; pb_, nb, db, ib, Pb, tb = proj[j]
                if pa_ == pb_ or na.dot(nb) <= dot or abs(da - db) >= dist:
                    continue
                if max(p[0] for p in Pa) < min(p[0] for p in Pb) or max(p[0] for p in Pb) < min(p[0] for p in Pa) or \
                        max(p[1] for p in Pa) < min(p[1] for p in Pb) or max(p[1] for p in Pb) < min(p[1] for p in Pa):
                    continue
                sk = (min(pa_, pb_), max(pa_, pb_))
                C = vki_clip_poly(Pa, Pb)
                ar = abs(vki_area2(C)) if len(C) >= 3 else 0.0
                if ar <= min_area:
                    continue
                if sk in seen:
                    continue
                seen.add(sk); tot += 1; area_max = max(area_max, ar)
                if len(errs) < max_report:
                    cx = sum(p[0] for p in C) / len(C); cy = sum(p[1] for p in C) / len(C)
                    cw = u * cx + v * cy + na * da
                    errs.append(f"T5S {o.name}: faces {pa_} (part {ia}) / {pb_} (part {ib}) overlap {ar:.2e} m2 at "
                                f"({cw.x:.3f},{cw.y:.3f},{cw.z:.3f}) n=({na.x:.2f},{na.y:.2f},{na.z:.2f})")
    if tot > len(errs):
        errs.append(f"T5S {o.name}: {tot} overlapping face pairs in all (max {area_max:.2e} m2)")
    return errs


def vki_self_coplanar(o, dot=0.999, dist=1e-4, min_area=1e-6, max_report=20, buried_ok=True):
    """C3 diagnostic (z-fighting inside one master): the T5 test between the loose parts of a single mesh.
    Same-facing coplanar overlaps between two members of one piece render as z-fighting wherever they are not
    covered by other geometry (e.g. a wall body's end face in the plane of a jamb's reveal face).
    The acceptance test is vki_t5s_self_coplanar (strict: no buried exception, every polygon pair)."""
    o = vki_obj(o)
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me)
    isl = [-1] * len(bm.verts); bm.verts.ensure_lookup_table(); ni = 0
    for v in bm.verts:
        if isl[v.index] >= 0:
            continue
        st = [v]; isl[v.index] = ni
        while st:
            a = st.pop()
            for e in a.link_edges:
                b = e.other_vert(a)
                if isl[b.index] < 0:
                    isl[b.index] = ni; st.append(b)
        ni += 1
    bm.free()
    owned = [(isl[t_[5]], t_[:5]) for t_ in vki_tris_local_idx(o)]
    parts = [([], []) for _ in range(ni)]
    remap = {}
    for v in me.vertices:
        pi = isl[v.index]; remap[v.index] = len(parts[pi][0]); parts[pi][0].append(v.co.copy())
    for p_ in me.polygons:
        parts[isl[p_.vertices[0]]][1].append(tuple(remap[i] for i in p_.vertices))
    return vki_coplanar_pairs(owned, [f"{o.name}#part{i}" for i in range(ni)], [], dot, dist, min_area,
                              max_report, "SELF", covers=vki_bvh_solids(parts) if buried_ok else ())


def vki_tris_local_idx(o):
    me = o.data
    me.calc_loop_triangles()
    out = []
    for t in me.loop_triangles:
        a, b, c = (Vector(me.vertices[i].co) for i in t.vertices)
        n = (b - a).cross(c - a)
        if n.length < 1e-12:
            continue
        n.normalize()
        out.append((a, b, c, n, n.dot(a), t.vertices[0]))
    return out


def vki_bvh_solids(parts):
    """[(verts, polys)] -> BVH trees (world or local space, as given) for the 'buried face' exception"""
    from mathutils.bvhtree import BVHTree
    return [BVHTree.FromPolygons(vs, ps) for vs, ps in parts if ps]


def vki_point_inside(trees, p):
    """p lies inside one of the closed solids (nearest face's outward normal points away from p)"""
    for t in trees:
        loc, nrm, idx, d = t.find_nearest(p)
        if loc is not None and d < 5.0 and (p - loc).dot(nrm) < 0:
            return True
    return False


def vki_coplanar_pairs(owned, names, posts, dot, dist, min_area, max_report, tag, covers=()):
    """covers: BVH trees of the solids; an overlap whose front (2 mm off the plane along the normal) lies inside
    a solid is buried against a neighbour (e.g. the end faces at a butt joint that also lies on a floor joint, or a
    body top under a cap) and cannot render, so it is not reported (C3 extension of the post-box exception)"""
    buckets = {}
    for oi, tr in owned:
        n, d = tr[3], tr[4]
        key = (round(n.x, 2), round(n.y, 2), round(n.z, 2), round(d, 3))
        buckets.setdefault(key, []).append((oi, tr))
    objs = names
    errs = []; seen = set()
    for key, lst in buckets.items():
        cand = list(lst)
        for dd in (-0.001, 0.001):
            cand += buckets.get((key[0], key[1], key[2], round(key[3] + dd, 3)), [])
        if len({oi for oi, _ in cand}) < 2:
            continue
        n0 = lst[0][1][3]
        u = Vector((0, 0, 1)) if abs(n0.z) < 0.9 else Vector((1, 0, 0))
        u = (u - n0 * u.dot(n0)).normalized(); v = n0.cross(u)
        grid = {}
        proj = []
        for oi, tr in cand:
            P = [(p.dot(u), p.dot(v)) for p in tr[:3]]
            if vki_area2(P) < 0:
                P = P[::-1]
            proj.append((oi, tr, P))
            xs = [p[0] for p in P]; ys = [p[1] for p in P]
            for gx in range(math.floor(min(xs) / 0.5), math.floor(max(xs) / 0.5) + 1):
                for gy in range(math.floor(min(ys) / 0.5), math.floor(max(ys) / 0.5) + 1):
                    grid.setdefault((gx, gy), []).append(len(proj) - 1)
        for cell in grid.values():
            for ii in range(len(cell)):
                for jj in range(ii + 1, len(cell)):
                    i, j = cell[ii], cell[jj]
                    if (min(i, j), max(i, j), key) in seen:
                        continue
                    seen.add((min(i, j), max(i, j), key))
                    oa, ta, Pa = proj[i]; ob_, tb, Pb = proj[j]
                    if oa == ob_ or ta[3].dot(tb[3]) <= dot or abs(ta[4] - tb[4]) >= dist:
                        continue
                    C = vki_clip_poly(Pa, Pb)
                    if len(C) < 3 or abs(vki_area2(C)) < min_area:
                        continue
                    cx = sum(p[0] for p in C) / len(C); cy = sum(p[1] for p in C) / len(C)
                    cw = u * cx + v * cy + ta[3] * ta[4]
                    if any(all(mn[k] - 1e-6 <= cw[k] <= mx[k] + 1e-6 for k in range(3)) for mn, mx in posts):
                        continue
                    if covers and vki_point_inside(covers, cw + ta[3] * 0.002):
                        continue
                    if len(errs) < max_report:
                        errs.append(f"{tag} {objs[oa]} / {objs[ob_]}: coplanar overlap at "
                                    f"({cw.x:.3f},{cw.y:.3f},{cw.z:.3f}) n=({ta[3].x:.2f},{ta[3].y:.2f},"
                                    f"{ta[3].z:.2f})")
    return errs


# ---------------------------------------------------------------- T6 UV continuity
def vki_t6_uv_continuity(objs, slots=None, tol=1e-4):
    """world-locked faces of different objects that share a world position and facing have UVs equal mod 1"""
    slots = set(slots or VKI_WORLD_LOCKED)
    table = {}
    for oi, o in enumerate(objs):
        me = o.data
        if not me.uv_layers:
            continue
        uvd = me.uv_layers.active.data
        mw = vki_mw(o); m3 = mw.to_3x3()
        vert_only = o.get("vki_class") in ("wall", "post")     # hidden horizontal body faces flip v under 180 deg
        for p in me.polygons:
            if p.material_index not in slots or (vert_only and abs(p.normal.z) > 0.7):
                continue
            n = (m3 @ p.normal).normalized()
            nk = (round(n.x, 3), round(n.y, 3), round(n.z, 3))
            for li in p.loop_indices:
                q = mw @ me.vertices[me.loops[li].vertex_index].co
                key = (round(q.x, 4), round(q.y, 4), round(q.z, 4), nk)
                table.setdefault(key, []).append((oi, tuple(uvd[li].uv)))
    errs = []; nchk = 0
    for key, lst in table.items():
        owners = {oi for oi, _ in lst}
        if len(owners) < 2:
            continue
        ref = lst[0]
        for oi, uv in lst[1:]:
            if oi == ref[0]:
                continue
            nchk += 1
            du, dv = uv[0] - ref[1][0], uv[1] - ref[1][1]
            if abs(du - round(du)) > tol or abs(dv - round(dv)) > tol:
                if len(errs) < 20:
                    errs.append(f"T6 {objs[ref[0]].name} / {objs[oi].name}: uv jump ({du:.4f},{dv:.4f}) at {key[:3]}")
    if nchk == 0:
        errs.append("T6: no shared world-locked loops between the objects (nothing compared)")
    return errs


# ---------------------------------------------------------------- T7 / T8 / T9
def vki_t7_closed(o):
    """every edge has exactly 2 faces. Walls (core fix): the end planes x = 0 / x = L are open (VKIKit.finish
    removes the end faces), so an edge with ONE face is allowed there -- both its vertices in the same end plane;
    everywhere else a wall is closed. Dual-grid rock / ground tiles are open at their bottom plane (vki_open_bottom:
    the bottom faces face down under the floor, never seen). Edges with 3+ faces are always an error."""
    o = vki_obj(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    wall = o.get("vki_class") == "wall"
    L = float(o.get("vki_len") or 0.0)
    ends = (0.0, L) if wall else ()
    ob = o.get("vki_open_bottom")            # dual-grid rock / ground tiles: open at their bottom plane (never seen)
    bad = 0; open_ = 0
    for e in bm.edges:
        nf = len(e.link_faces)
        if nf == 2:
            continue
        if nf == 1 and any(all(abs(v.co.x - xe) <= 1e-5 for v in e.verts) for xe in ends):
            open_ += 1
            continue
        if nf == 1 and ob is not None and all(abs(v.co.z - float(ob)) <= 1e-5 for v in e.verts):
            open_ += 1
            continue
        bad += 1
    bm.free()
    return [f"T7 {o.name}: {bad} edges without exactly 2 faces (outside the open wall end planes)"] if bad else []


def vki_t8_normals(o):
    o = vki_obj(o)
    bm = bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    before = [f.normal.copy() for f in bm.faces]
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.normal_update()
    flipped = sum(1 for f, n in zip(bm.faces, before) if f.normal.dot(n) < 0)
    bm.free()
    return [f"T8 {o.name}: {flipped} flipped faces"] if flipped else []


VKI_PROP_BUDGET = {"furniture": (1500, 2000), "dressing": (400, 400), "hero": (6000, 6000)}


def vki_budget(o):
    """(soft, hard) triangle budget of a master (§9 T9, §5)"""
    cls, kind, ht = o.get("vki_class"), o.get("vki_kind"), o.get("vki_height")
    L = float(o.get("vki_len") or 1.5)
    if cls == "wall":
        if o.get("vki_special") or kind in ("Fireplace", "Hearth", "Forge"):
            return (6000, 6000)
        if ht == "Cut":
            return (700, 700) if L < 2 else (1200, 1200)
        return (1500, 1500) if L < 2 else (2500, 2500)
    if cls == "post":
        return (400, 400)
    if cls == "floor":
        if kind == "Dais":
            return (1500, 2000)
        if kind == "Sill":
            return (400, 400)
        return (12, 12) if "_Q" in o.name else (24, 24)
    if cls == "leaf":
        return (800, 800)
    if cls in ("link", "pit"):
        return (6000, 6000)
    if cls == "rock":
        return (1200, 1200)
    if cls == "ground":
        return (1500, 1500)
    if cls in ("overlay", "fx"):
        return (400, 400)
    if cls == "prop":
        return VKI_PROP_BUDGET.get(o.get("vki_tier", "furniture"), (1500, 2000))
    return (10 ** 9, 10 ** 9)


def vki_tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def vki_t9_budget(o):
    o = vki_obj(o)
    n = vki_tris(o); soft, hard = vki_budget(o)
    if n > hard:
        return [f"T9 {o.name}: {n} tris > hard limit {hard}"]
    if n > soft:
        return [f"T9 {o.name}: {n} tris > budget {soft} (hard {hard}) -- warning"]
    return []


# ---------------------------------------------------------------- T10 metadata
VKI_REQ_META = {
    "*": ["kit", "grid_m", "vki_class", "vki_kind", "vki_origin", "vki_rot_lock", "vki_footprint", "vki_fp_cells",
          "vki_collider", "vki_nav", "vki_uv_lock"],
    "wall": ["vki_family", "vki_len", "vki_height", "vki_thick"],
    "post": ["vki_family", "vki_height", "vki_thick", "vki_post_rule"],
    "leaf": ["hinge_axis", "vki_leaf_state"],
    "prop": ["vki_mount"],
    "rock": ["vki_family", "vki_corners"],
    "ground": ["vki_family", "vki_corners"],
}


def vki_t10_metadata(o):
    import re as _re
    o = vki_obj(o); errs = []
    if not _re.match(r"^SM_VKI_[A-Za-z0-9]+(_[A-Za-z0-9]+)*$", o.name):
        errs.append(f"T10 {o.name}: name does not match ^SM_VKI_...")
    if o.get("kit") != "VillageInterior" or abs(float(o.get("grid_m", 0)) - 1.5) > 1e-9:
        errs.append(f"T10 {o.name}: kit/grid_m wrong")
    cls = o.get("vki_class")
    test_piece = bool(o.get("vki_test_piece"))
    for k_ in VKI_REQ_META["*"] + (VKI_REQ_META.get(cls, []) if not test_piece or cls == "wall" else []):
        if k_ == "vki_post_rule" and test_piece:
            continue
        if k_ not in o.keys():
            errs.append(f"T10 {o.name}: missing {k_}")
    for k_ in o.keys():
        v = o[k_]
        if isinstance(v, str) and v[:1] in "[{":
            try:
                json.loads(v)
            except ValueError:
                errs.append(f"T10 {o.name}: {k_} is not valid JSON")
    cp, ct = o.get("vki_cut_pair"), o.get("vki_cut_to")
    if cp:
        t = bpy.data.objects.get(cp)
        if t is None or t.get("vki_cut_pair") != o.name:
            errs.append(f"T10 {o.name}: vki_cut_pair {cp} missing or not reciprocal")
    if ct and bpy.data.objects.get(ct) is None:
        errs.append(f"T10 {o.name}: vki_cut_to target {ct} missing")
    if cls == "wall" and not test_piece and not (cp or ct):
        errs.append(f"T10 {o.name}: wall without vki_cut_pair / vki_cut_to")
    fp = vki_fp(o)
    if fp:
        co = vki_np_co(o.data)
        if len(co):
            mn, mx = co.min(0), co.max(0)
            dv = max(abs(mn[0] - fp[0]), abs(mn[1] - fp[1]), abs(mx[0] - fp[2]), abs(mx[1] - fp[3]))
            if dv > 1e-3:
                errs.append(f"T10 {o.name}: footprint {fp} != bbox ({mn[0]:.4f},{mn[1]:.4f},{mx[0]:.4f},{mx[1]:.4f})")
    tr = vki_get(o, "vki_trigger", None)
    if cls == "wall" and tr:
        if tr[1] >= 0:
            errs.append(f"T10 {o.name}: trigger centre y {tr[1]} is not on the room side (-Y)")
    return errs


def vki_t10_instances(objs=None):
    """T10i (core fix, review r2): every instance of a VKI master (mesh = the master's, or a VARI_* mesh whose
    vki_base is the master) carries the master's metadata -- every key except the placement-only ones
    (VKI_PLACEMENT_KEYS / _PREFIXES) -- with equal values. objs default: the objects of every VKI_* / WS_vki_*
    scene. vki_rebuild refreshes instances (vki_refresh_instances), so a failure means an instance was edited or
    placed outside vki_place / vki_rebuild."""
    c = bpy.data.collections.get("VKI_Pieces")
    if c is None:
        return []
    by_mesh = {o.data.name: o for o in c.objects if o.type == "MESH" and o.data is not None}
    by_name = {o.name: o for o in c.objects}
    if objs is None:
        objs = {o.name: o for sc in bpy.data.scenes if sc.name.startswith(("VKI_", "WS_vki_"))
                for o in sc.objects}.values()
    errs = []
    for o in objs:
        if o.type != "MESH" or o.data is None or o.name in by_name:
            continue
        base = by_name.get(o.data.get("vki_base")) if o.data.name.startswith("VARI_") else by_mesh.get(o.data.name)
        if base is None:
            continue
        bad = [k_ for k_ in base.keys() if vki_is_meta_key(k_) and not vki_is_placement_key(k_) and
               not (k_ == "vki_class" and o.get("vki_reuse")) and o.get(k_) != base[k_]]
        if bad:
            errs.append(f"T10i {o.name}: {len(bad)} keys differ from {base.name}: {bad[:6]}")
    return errs


# ---------------------------------------------------------------- T11 placement
def vki_t11_placement(objs, pairs=()):
    """instances: structure on the 1.5 lattice; FLOOR pieces at even nodes / Q parity; props at a 0.75 lattice
    point (vki_at) unless vki_hug; rotations multiples of 90; world0 at 0; Stair_Up never at 180; up/down pairs
    share origin and rotation"""
    errs = []
    for o in objs:
        cls = o.get("vki_class"); piece = o.get("vki_piece", o.name.split("_inst")[0])
        x, y = o.location.x, o.location.y
        rot = math.degrees(o.rotation_euler.z)
        r90 = rot / 90.0
        if abs(r90 - round(r90)) > 1e-4:
            errs.append(f"T11 {o.name}: rotation {rot:.3f} not a multiple of 90")
        rr = int(round(rot)) % 360
        if o.get("vki_rot_lock") == "world0" and rr != 0:
            errs.append(f"T11 {o.name}: world0 piece at rotation {rr}")
        if o.get("vki_rot_lock") == "rot0_90" and rr not in (0, 90):      # core fix: e.g. Floor_Sill_150 (§2.5)
            errs.append(f"T11 {o.name}: rot0_90 piece at rotation {rr}")
        if "Stair_Up" in piece and rr == 180:
            errs.append(f"T11 {o.name}: Stair_Up at 180")
        on = lambda a, s: abs(a / s - round(a / s)) < 1e-4
        if o.get("vki_kind") == "Q075":                  # adventure kit: quarter floors on the 0.75 lattice
            import re as _re
            m4 = _re.search(r"_R([0-3])([0-3])", piece)
            want = (int(round(x / 0.75)) % 4, int(round(y / 0.75)) % 4)
            if not (on(x, 0.75) and on(y, 0.75)) or not m4 or (int(m4.group(1)), int(m4.group(2))) != want:
                errs.append(f"T11 {o.name}: quarter floor off its 0.75 lattice / parity {want}")
        elif cls in ("wall", "post", "floor", "link", "rock", "ground"):
            if not (on(x, 1.5) and on(y, 1.5)):
                errs.append(f"T11 {o.name}: structure off the 1.5 lattice ({x:.4f},{y:.4f})")
            # the parity / even-node rule is about the world-locked t 3.0 FLOOR UVs, so it applies only to pieces
            # whose UVs are world-locked (fix r1: the Apron uses the FLOOR slot with its own t 4.0 UVs,
            # vki_uv_lock "own_t4", and must sit at its door's origin, which may be an odd node)
            has_floor = o.get("vki_uv_lock", "world") == "world" and \
                any(p.material_index == VKI_FLOOR for p in o.data.polygons)
            if has_floor:
                i, j = int(round(x / 1.5)), int(round(y / 1.5))
                import re as _re
                m = _re.search(r"_Q([01])([01])", piece)
                if m:
                    if (int(m.group(1)), int(m.group(2))) != (i % 2, j % 2):
                        errs.append(f"T11 {o.name}: Q parity {m.group(0)} at node ({i},{j})")
                elif not (on(x, 3.0) and on(y, 3.0)):
                    errs.append(f"T11 {o.name}: FLOOR piece off the even nodes ({x},{y})")
        elif cls in ("prop", "overlay"):
            at = vki_get(o, "vki_at", None)
            if at is None:
                errs.append(f"T11 {o.name}: no vki_at (place props with vki_place)")
            elif not (on(at[0], 0.75) and on(at[1], 0.75)) and "vki_hug" not in o.keys():
                errs.append(f"T11 {o.name}: point {at} off the 0.75 lattice without vki_hug")
            if "vki_hug_fail" in o.keys():
                errs.append(f"T11 {o.name}: hug failed ({o['vki_hug_fail']})")
    for up, dn in pairs:
        if (Vector(up.location[:2]) - Vector(dn.location[:2])).length > 1e-4 or \
                abs(math.degrees(up.rotation_euler.z - dn.rotation_euler.z)) % 360 > 1e-3:
            errs.append(f"T11 {up.name} / {dn.name}: stair pair does not share origin and rotation")
    return errs


# ---------------------------------------------------------------- door-leaf swing check (fix r1)
def vki_leaf_swing(door="SM_VKI_Wall_Timber_Door_150_Full", leaf="SM_VKI_Leaf_Plank_Full",
                   post="SM_VKI_Post_Timber_Corner_Full", angles=(0, 15, 30, 45, 60, 75, 90)):
    """BVH overlap of a leaf master hung at its door master's vki_leaf_socket and opened by each angle (rotation
    -angle about local Z, toward the room) against the door piece and a post at the door's start node (the jamb
    side), all in the door's frame (door at the origin, rot 0). Works on the master meshes, no scene objects.
    Returns {angle: (triangles overlapping the door, triangles overlapping the post)}; clean = all (0, 0)."""
    from mathutils.bvhtree import BVHTree
    D, Lf, P = bpy.data.objects[door], bpy.data.objects[leaf], bpy.data.objects[post]
    sock = Vector(vki_get(D, "vki_leaf_socket"))

    def tree(o, M):
        me = o.data
        return BVHTree.FromPolygons([M @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    td, tp = tree(D, Matrix.Identity(4)), tree(P, Matrix.Identity(4))
    out = {}
    for a in angles:
        tl = tree(Lf, Matrix.Translation(sock) @ Matrix.Rotation(math.radians(-a), 4, "Z"))
        out[a] = (len(tl.overlap(td)), len(tl.overlap(tp)))
    return out


# ---------------------------------------------------------------- T12 room rules (assembly step)
def vki_obj_aabb(o, shrink=0.0):
    bb = [vki_mw(o) @ Vector(c) for c in o.bound_box]
    mn = Vector([min(v[i] for v in bb) + shrink for i in range(3)])
    mx = Vector([max(v[i] for v in bb) - shrink for i in range(3)])
    return mn, mx


def vki_aabb_overlap(a, b):
    return all(a[0][i] < b[1][i] and b[0][i] < a[1][i] for i in range(3))


def vki_t12_room_rules(scene, room=None):
    """§9 T12 on a built room scene. Needs the assembler's room data (`room` = VKI_ROOMS[scene], vki_rooms) for the
    post / floor-coverage / door / BFS / R-occ rules; without it only the object-level checks run and a note is
    returned. Object-level checks available now: prop/prop and prop/structure overlap (AABB, 5 mm shrink), spawn
    capsule (r 0.3) within 0.2 m of a trigger, wall_hung props on Cut hosts, vki_hug_fail, vki_mount_zmax over the
    host wall's H - 0.14."""
    sc = bpy.data.scenes[scene] if isinstance(scene, str) else scene
    errs = []
    objs = list(sc.objects)
    props = [o for o in objs if o.get("vki_class") == "prop"]
    struct = [o for o in objs if o.get("vki_class") in ("wall", "post")]
    boxes = {o.name: vki_obj_aabb(o, 0.005) for o in props}
    for i, a in enumerate(props):
        for b in props[i + 1:]:
            if vki_aabb_overlap(boxes[a.name], boxes[b.name]) and not (a.get("vki_mount") == "table" or
                                                                      b.get("vki_mount") == "table"):
                errs.append(f"T12 prop overlap {a.name} / {b.name}")
        for s_ in struct:
            if vki_aabb_overlap(boxes[a.name], vki_obj_aabb(s_)) and a.get("vki_mount") != "wall_hung":
                errs.append(f"T12 prop {a.name} intersects {s_.name} (AABB)")
        if a.get("vki_mount") == "wall_hung" and a.get("vki_host_height") == "Cut":
            errs.append(f"T12 wall_hung {a.name} on a Cut wall")
        if "vki_hug_fail" in a.keys():
            errs.append(f"T12 {a.name}: hug failed ({a['vki_hug_fail']})")
    errs += vki_t12_posts(objs)
    spawns = [o for o in objs if o.name.startswith("SPN_")]
    for o in objs:
        tr = vki_get(o, "vki_trigger", None) if o.get("vki_link") else None
        if not tr:
            continue
        c = vki_mw(o) @ Vector(tr[:3]); s_ = Vector(tr[3:6])
        R = vki_mw(o).to_3x3()
        hx = abs((R @ Vector((s_.x, 0, 0))).x) + abs((R @ Vector((0, s_.y, 0))).x)
        hy = abs((R @ Vector((s_.x, 0, 0))).y) + abs((R @ Vector((0, s_.y, 0))).y)
        for sp in spawns:
            dx = max(abs(sp.location.x - c.x) - hx / 2, 0); dy = max(abs(sp.location.y - c.y) - hy / 2, 0)
            if math.hypot(dx, dy) < 0.3 + 0.2:
                errs.append(f"T12 spawn {sp.name} within 0.2 m of the trigger of {o.name}")
    if room is None:
        errs.append("T12 note: room-level rules (floor coverage, doors, BFS, palette, R-occ) need vki_rooms")
    return errs


def vki_wall_end_nodes(objs):
    """{(x, y) node: [dict(w, xe, d, h, fam, cls)]} for every wall-instance end in objs; h is the end's height
    ("Full"/"Cut"; a rake's low end is Cut, its high end Full)"""
    nodes = {}
    for w in objs:
        if w.get("vki_class") != "wall" or not w.get("vki_len"):
            continue
        L = float(w["vki_len"]); mw = vki_mw(w)
        ht = w.get("vki_height", "Full"); low = w.get("vki_rake_low")
        for xe, xo in ((0.0, L), (L, 0.0)):
            p = (mw @ Vector((xe, 0, 0))).to_2d(); q = (mw @ Vector((xo, 0, 0))).to_2d()
            h = ("Cut" if (low == "x0") == (xe == 0.0) else "Full") if ht == "Rake" else ht
            nodes.setdefault((round(p.x, 3), round(p.y, 3)), []).append(
                dict(w=w, xe=xe, d=(q - p).normalized(), h=h, fam=w.get("vki_family"), cls=vki_cls_of(w)))
    return nodes


def vki_t12_posts(objs):
    """T12 post rules at every wall-end node (object level, core fix): an L/T/X junction needs a Corner post; a
    height / family / class step on a straight run needs a post; a FREE wall end needs a post -- an ERROR since the
    core fix (walls have open end planes; §2.3's 'warning' is superseded). Post height >= the tallest wall-end
    height at the node (a rake contributes its end height)."""
    errs = []
    pk = {}
    for p in objs:
        if p.get("vki_class") == "post":
            t = vki_mw(p).translation
            pk.setdefault((round(t.x, 3), round(t.y, 3)), []).append(p)
    for key, ends in sorted(vki_wall_end_nodes(objs).items()):
        dirs = [e["d"] for e in ends]
        corner = any(abs(a.x * b.y - a.y * b.x) > 0.5 for a in dirs for b in dirs)
        need = why = None
        if corner:
            need, why = "Corner", "L/T/X junction"
        elif len(ends) == 1:
            need, why = "Mid", "free wall end (open end plane)"
        elif any((e["h"], e["fam"], e["cls"]) != (ends[0]["h"], ends[0]["fam"], ends[0]["cls"]) for e in ends[1:]):
            need, why = "Mid", "height / family / class step"
        here = pk.get(key, [])
        if need and not here:
            errs.append(f"T12 node {key}: {why} of {[e['w'].name for e in ends]} needs a {need} post (none)")
            continue
        if need == "Corner" and not any(p.get("vki_kind") == "Corner" for p in here):
            errs.append(f"T12 node {key}: {why} needs a Corner post, found {[p.name for p in here]}")
        if here:
            need_h = max(VKI_CUT_H if e["h"] == "Cut" else VKI_H_FULL.get(e["fam"], 3.0) for e in ends)
            for p in here:
                ph = VKI_CUT_H if p.get("vki_height") == "Cut" else VKI_H_FULL.get(p.get("vki_family"), 3.0)
                if ph < need_h - 1e-6:
                    errs.append(f"T12 post {p.name} at {key}: height {ph} < tallest wall end {need_h}")
    return errs


# ---------------------------------------------------------------- T13 wobble
def vki_t13_wobble(name):
    """rebuild the piece with and without wobble (same vertex order): only y moves, outward, |dy| <= A, zero within
    0.32 of nodes, at pins, at z <= 0.16; under the cap |dy| <= A * smoothstep(tb, tb - 0.25, z) (zero at the cap
    bottom, the §2.6 ramp); body |y| <= CAP_HW - 0.005. 'moved nothing' only when some body vertex could move."""
    sp = vki_spec_map().get(name)
    if sp is None:
        return [f"T13 {name}: not in VKI_SPECS"]
    k0 = VKIKit(name); k0.wobble_off = True; sp[1](k0)
    k1 = VKIKit(name); sp[1](k1)
    errs = []
    try:
        if not k1.wobble_log:
            return []
        if len(k0.bm.verts) != len(k1.bm.verts):
            return [f"T13 {name}: vertex count differs with wobble off"]
        lg = k1.wobble_log[-1]
        A = VKI_AMP[lg["fam"]]; L = lg["L"]; chw = VKI_CAP_HW[k1.cls]
        nodes = [n for n in (0.0, 1.5, 3.0) if n <= L + 1e-6]
        k0.bm.verts.ensure_lookup_table(); k1.bm.verts.ensure_lookup_table()
        cnt = dict(xz=0, amp=0, inward=0, node=0, pin=0, low=0, cap=0, body=0)
        moved = 0; eligible = 0
        for v0, v1 in zip(k0.bm.verts, k1.bm.verts):
            d = v1.co - v0.co
            x, y, z = v0.co
            if v0[k0.body] and abs(abs(y) - k0.T / 2) <= 1e-4:
                # the §2.6 envelope e * zf of this body vertex (C3 fix: 'moved nothing' only counts when some body
                # vertex lies outside the node flats, pin ramps, hole margins, the sole band and the cap ramp)
                e_ = min(vki_smoothstep(0.32, 0.57, abs(x - n)) for n in nodes)
                e_ *= min([vki_smoothstep(0.0, 0.10, abs(x - p)) for p in lg["pins"]] or [1.0])
                e_ *= min([vki_smoothstep(0.0, 0.15, vki_rect_dist(x, z, h)) for h in lg["holes"]] or [1.0])
                tb_ = lg["top_body_fn"](x)
                if e_ * vki_smoothstep(0.16, 0.41, z) * vki_smoothstep(tb_, tb_ - 0.25, z) > 1e-6:
                    eligible += 1
            if abs(d.x) > 1e-7 or abs(d.z) > 1e-7:
                cnt["xz"] += 1
            if abs(d.y) <= 1e-7:
                if v1[k1.body] and abs(v1.co.y) > chw - 0.005 + 1e-7:
                    cnt["body"] += 1
                continue
            moved += 1
            if abs(d.y) > A + 1e-7:
                cnt["amp"] += 1
            if d.y * y < 0:
                cnt["inward"] += 1
            if min(abs(x - n) for n in nodes) <= VKI_NODE_FLAT + 1e-6:
                cnt["node"] += 1
            if any(abs(x - p) < 1e-4 for p in lg["pins"]):
                cnt["pin"] += 1
            if z <= 0.16:
                cnt["low"] += 1
            tb = lg["top_body_fn"](x)
            # §2.6: zf ramps from full strength at tb - 0.25 down to 0 at the cap bottom tb (C3 fix: the old check
            # demanded zero over the whole 0.25 band, which the verbatim formula never gives)
            if abs(d.y) > A * vki_smoothstep(tb, tb - 0.25, z) + 1e-7:
                cnt["cap"] += 1
            if abs(v1.co.y) > chw - 0.005 + 1e-7:
                cnt["body"] += 1
        for k_, c in cnt.items():
            if c:
                errs.append(f"T13 {name}: {c} vertices fail '{k_}'")
        if moved == 0 and eligible and A > 0 and VKI_FLAGS.get("wobble", True):
            errs.append(f"T13 {name}: wobble moved nothing")
    finally:
        k0.bm.free(); k1.bm.free()
    return errs


# ---------------------------------------------------------------- T14 materials
def vki_t14_materials(o):
    import numpy
    o = vki_obj(o); me = o.data; errs = []
    if len(me.materials) != VKI_NSLOTS:
        errs.append(f"T14 {o.name}: {len(me.materials)} slots, not 67")
    if kit_mats()[54].name != "M_VK_Hewn":
        errs.append("T14: kit_mats()[54] is not M_VK_Hewn")
    idx = numpy.empty(len(me.polygons), numpy.int32)
    me.polygons.foreach_get("material_index", idx)
    if len(idx) and idx.max() >= VKI_NSLOTS:
        errs.append(f"T14 {o.name}: face material index {idx.max()} >= 67")
    ban = sorted(set(int(i) for i in idx) & set(VKI_BANNED))
    if ban:
        errs.append(f"T14 {o.name}: banned slots used {ban}")
    for slot, nm in VKI_MASTER_MATS.items():
        m = me.materials[slot] if slot < len(me.materials) else None
        ok = m is not None and (m.name.startswith("M_VKI_") if slot == WINDOW else m.name == nm)
        if not ok:
            errs.append(f"T14 {o.name}: slot {slot} is {m.name if m else None}, expected {nm}")
    return errs


# ---------------------------------------------------------------- T15 exterior invariance / T16 determinism
def vki_mesh_hash(me):
    import numpy
    h = hashlib.md5()
    a = numpy.empty(len(me.vertices) * 3, numpy.float32); me.vertices.foreach_get("co", a); h.update(a.tobytes())
    a = numpy.empty(len(me.polygons), numpy.int32); me.polygons.foreach_get("material_index", a); h.update(a.tobytes())
    for uvl in me.uv_layers:
        a = numpy.empty(len(me.loops) * 2, numpy.float32); uvl.data.foreach_get("uv", a); h.update(a.tobytes())
    ca = me.color_attributes.get("Col")
    if ca is not None:
        a = numpy.empty(len(ca.data) * 4, numpy.float32); ca.data.foreach_get("color", a); h.update(a.tobytes())
    h.update("|".join(m.name if m else "-" for m in me.materials).encode())
    return h.hexdigest()


def vki_tree_hash(nt):
    items = []
    for n in sorted(nt.nodes, key=lambda n: n.name):
        row = [n.bl_idname, n.name, n.label]
        for p in ("blend_type", "data_type", "operation", "interpolation_type", "clamp", "layer_name",
                  "attribute_name", "uv_map", "sky_type"):
            if hasattr(n, p):
                row.append(str(getattr(n, p)))
        if getattr(n, "image", None) is not None:
            row.append(n.image.name)
        for s_ in n.inputs:
            dv = getattr(s_, "default_value", None)
            if dv is not None:
                row.append(repr(tuple(round(x, 6) for x in dv)) if hasattr(dv, "__len__") else repr(dv))
        items.append(row)
    items.append(sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier)
                        for l in nt.links))
    return hashlib.md5(repr(items).encode()).hexdigest()


def vki_ext_hashes():
    """hashes of every mesh used by an SM_VK_* object (vertices, UVs, Col, material names), every M_VK_* node tree,
    MC_World and the VK_Sun / VK_Fill lights"""
    out = {}
    meshes = {o.data.name: o.data for o in bpy.data.objects
              if o.name.startswith("SM_VK_") and o.type == "MESH" and o.data is not None}
    for n, me in meshes.items():
        out["mesh:" + n] = vki_mesh_hash(me)
    for m in bpy.data.materials:
        if m.name.startswith("M_VK_") and m.node_tree is not None:
            out["mat:" + m.name] = vki_tree_hash(m.node_tree)
    w = bpy.data.worlds.get("MC_World")
    if w is not None and w.node_tree is not None:
        out["world:MC_World"] = vki_tree_hash(w.node_tree)
    for n in ("VK_Sun", "VK_Fill"):
        o = bpy.data.objects.get(n)
        if o is not None:
            out["light:" + n] = hashlib.md5(repr((round(o.data.energy, 6), tuple(round(c, 6) for c in o.data.color),
                                                  [round(x, 6) for r in o.matrix_world for x in r],
                                                  sorted(s.name for s in o.users_scene))).encode()).hexdigest()
    return out


def vki_t15_exterior_invariance(names=None, baseline=None):
    """hash the exterior, run vki_ns() + vki_rebuild(names) (all when None), hash again; also compares with an
    earlier `baseline` dict when given"""
    h0 = baseline or vki_ext_hashes()
    g = vki_ns()
    g["vki_rebuild"](names)
    h1 = vki_ext_hashes()
    diff = sorted(k_ for k_ in set(h0) | set(h1) if h0.get(k_) != h1.get(k_))
    return [f"T15 changed: {k_}" for k_ in diff[:40]] + ([f"T15 ... {len(diff) - 40} more"] if len(diff) > 40 else [])


def vki_t16_determinism(names):
    errs = []
    for n in ([names] if isinstance(names, str) else names):
        vki_rebuild([n]); h1 = vki_mesh_hash(bpy.data.objects[n].data)
        vki_rebuild([n]); h2 = vki_mesh_hash(bpy.data.objects[n].data)
        if h1 != h2:
            errs.append(f"T16 {n}: two rebuilds differ")
    return errs


# ---------------------------------------------------------------- T17 render clip
def vki_clip_fraction(path, thresh=0.98):
    import numpy
    img = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = img.size; c = img.channels
        a = numpy.empty(w * h * c, numpy.float32); img.pixels.foreach_get(a)
    finally:
        bpy.data.images.remove(img)
    rgb = a.reshape(-1, c)[:, :3]
    return float((rgb.min(1) >= thresh).mean())


def vki_t17_render_clip(path, limit=0.003):
    f = vki_clip_fraction(path)
    return [f"T17 {os.path.basename(path)}: {f * 100:.3f}% pixels with min(RGB) >= 0.98"] if f >= limit else []


# ---------------------------------------------------------------- T18 namespace
def vki_t18_namespace(texts=None):
    """ast over every vki_* text: top-level names start with vki_/VKI_ or are VKIKit, and none is a name of
    vk_kit_ns(terrain=False) (imports binding the very same module/object are allowed)"""
    import ast
    kg = {}
    exec(bpy.data.texts["vk_kit"].as_string(), kg)
    kit = kg["vk_kit_ns"](terrain=False)
    errs = []
    for t in bpy.data.texts:
        if not t.name.startswith("vki_") or (texts and t.name not in texts):
            continue
        tree = ast.parse(t.as_string())
        names = []

        def targets(node):
            if isinstance(node, ast.Name):
                yield node.id
            elif isinstance(node, (ast.Tuple, ast.List)):
                for e in node.elts:
                    yield from targets(e)
            elif isinstance(node, ast.Starred):
                yield from targets(node.value)

        def walk(body):
            for nd in body:
                if isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.append((nd.name, nd.lineno, None))
                elif isinstance(nd, ast.Assign):
                    for tg in nd.targets:
                        names.extend([(n_, nd.lineno, None) for n_ in targets(tg)])
                elif isinstance(nd, (ast.AugAssign, ast.AnnAssign)):
                    names.extend([(n_, nd.lineno, None) for n_ in targets(nd.target)])
                elif isinstance(nd, (ast.Import, ast.ImportFrom)):
                    for al in nd.names:
                        names.append(((al.asname or al.name).split(".")[0], nd.lineno, nd))
                elif isinstance(nd, (ast.For, ast.AsyncFor)):
                    names.extend([(n_, nd.lineno, None) for n_ in targets(nd.target)])
                    walk(nd.body); walk(nd.orelse)
                elif isinstance(nd, (ast.If, ast.While)):
                    walk(nd.body); walk(nd.orelse)
                elif isinstance(nd, ast.Try):
                    walk(nd.body); walk(nd.orelse); walk(nd.finalbody)
                    for hd in nd.handlers:
                        walk(hd.body)
                elif isinstance(nd, ast.With):
                    for it in nd.items:
                        if it.optional_vars is not None:
                            names.extend([(n_, nd.lineno, None) for n_ in targets(it.optional_vars)])
                    walk(nd.body)
        walk(tree.body)
        for n_, ln, imp in names:
            if imp is not None:
                d = {}
                exec(compile(ast.Module(body=[imp], type_ignores=[]), "<t18>", "exec"), d)
                if n_ in kit and kit[n_] is not d.get(n_):
                    errs.append(f"T18 {t.name}:{ln}: import {n_} shadows a different kit name")
                continue
            if not (n_.startswith(("vki_", "VKI_")) or n_ == "VKIKit"):
                errs.append(f"T18 {t.name}:{ln}: top-level name {n_} lacks the vki_/VKI_ prefix")
            elif n_ in kit:
                errs.append(f"T18 {t.name}:{ln}: {n_} collides with the kit namespace")
    return errs


# ---------------------------------------------------------------- T19 visibility (assembly step)
def vki_ray_blocked(sc, cam, point, tol=0.3, dg=None):
    """None when the ray camera -> point reaches within tol of the point, else (object name, hit location).
    Dungeon kit: objects marked vki_see_through (iron bars, barred gates, the cage) do not block -- the ray continues
    through them, as the eye does between the bars."""
    dg = dg or vki_depsgraph(sc)
    org = Vector(cam); point = Vector(point)
    for _i in range(64):
        d = point - org; L = d.length
        if L <= tol:
            return None
        dn = d.normalized()
        hit, loc, nrm, idx, ob, mat = sc.ray_cast(dg, org, dn, distance=max(L - tol, 1e-4))
        if not hit:
            return None
        if ob.original.get("vki_see_through"):
            org = loc + dn * 1e-3
            continue
        return (ob.original.name, tuple(round(c, 3) for c in loc))
    return None


def vki_cam_loc(target, D, pitch=None):
    p = math.radians(VKI_CAM["pitch"] if pitch is None else pitch)
    t = Vector(target).to_3d() if len(target) == 2 else Vector(target)
    return t + Vector((0, -math.cos(p) * D, math.sin(p) * D))


def vki_vis_points(sc):
    """(label, world point) at z 0.5: props' vki_use points, link triggers' centres, SPN_* spawns"""
    pts = []
    for o in sc.objects:
        mw = vki_mw(o)
        for i, u in enumerate(vki_get(o, "vki_use", None) or []):
            p = mw @ Vector((u[0], u[1], 0)); pts.append((f"{o.name}.use{i}", Vector((p.x, p.y, 0.5))))
        tr = vki_get(o, "vki_trigger", None) if o.get("vki_link") else None
        if tr:
            p = mw @ Vector(tr[:3]); pts.append((f"{o.name}.trigger", Vector((p.x, p.y, 0.5))))
        if o.name.startswith("SPN_"):
            pts.append((o.name, Vector((o.location.x, o.location.y, 0.5))))
    return pts


def vki_t19_visibility(scene, cams=None, points=None, tol=0.3):
    """§9 T19: every use point / trigger centre / spawn (z 0.5) is visible from the scene camera(s): the first hit
    lies within 0.3 m of the point. cams: list of camera positions (default: the fit camera from VKI_Root's
    vki_cam_target / vki_cam_dist, or the follow grid once vki_rooms provides it)."""
    sc = bpy.data.scenes[scene] if isinstance(scene, str) else scene
    if cams is None:
        root = sc.objects.get("VKI_Root")
        src = root if root is not None else sc
        t = vki_get(src, "vki_cam_target", None); D = src.get("vki_cam_dist")
        if t is None or D is None:
            return ["T19: no camera (pass cams or set vki_cam_target / vki_cam_dist on VKI_Root)"]
        cams = [vki_cam_loc(t, float(D))]
    points = points if points is not None else vki_vis_points(sc)
    dg = vki_depsgraph(sc)
    errs = []
    for lab, p in points:
        seen = any(vki_ray_blocked(sc, c, p, tol, dg) is None for c in cams)
        if not seen:
            b = vki_ray_blocked(sc, cams[0], p, tol, dg)
            errs.append(f"T19 {lab} at ({p.x:.2f},{p.y:.2f}) hidden by {b[0]}")
    return errs


# ---------------------------------------------------------------- the sRGB Col test (§2.8)
def vki_col_srgb_test(values=(0.25, 0.5, 0.75)):
    """writes Col (byte layer) through bmesh, reads it back through bmesh and the mesh attribute (.color = linear,
    .color_srgb), and renders an emission-only quad per value with the Standard view transform (restored after):
    returns {value: dict(bmesh, attr_linear, attr_srgb, png)}"""
    import numpy
    sc = vki_scene("VKI_Test")
    coll = bpy.data.collections.get("VKI_Test_ColQuad") or bpy.data.collections.new("VKI_Test_ColQuad")
    if coll.name not in sc.collection.children:
        sc.collection.children.link(coll)
    m = bpy.data.materials.get("M_VKI_Test_ColEmit") or bpy.data.materials.new("M_VKI_Test_ColEmit")
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
    nt.links.new(vc.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], out.inputs[0])
    res = {}
    objs = []
    for i, val in enumerate(values):
        bm = bmesh.new(); cl = bm.loops.layers.color.new("Col")
        vs = [bm.verts.new((i * 1.0 + x, 50.0 + y, 0)) for x, y in ((0, 0), (0.9, 0), (0.9, 0.9), (0, 0.9))]
        f = bm.faces.new(vs)
        for l in f.loops:
            l[cl] = (val, val, val, 1.0)
        rb = tuple(f.loops[0][cl])[0]
        me = bpy.data.meshes.new(f"VKI_Test_ColQuad_{i}"); bm.to_mesh(me); bm.free()
        me.materials.append(m)
        o = bpy.data.objects.new(f"VKI_Test_ColQuad_{i}", me); coll.objects.link(o); objs.append(o)
        ca = me.color_attributes["Col"]
        res[val] = dict(bmesh=round(rb, 4), domain=ca.domain, dtype=ca.data_type,
                        attr_linear=round(ca.data[0].color[0], 4), attr_srgb=round(ca.data[0].color_srgb[0], 4))
    vt = (sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure)
    hidden = []
    for o in sc.objects:
        if o.type == "MESH" and o not in objs and not o.hide_render:
            o.hide_render = True; hidden.append(o)
    try:
        sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = 0.0
        fp = vki_shot(sc, "col_srgb_test", mode="plan", bounds=(0, 50, len(values), 50.9), res=(len(values) * 64, 64),
                      margin=0.0, samples=1)
    finally:
        sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure = vt
        for o in hidden:
            o.hide_render = False
    img = bpy.data.images.load(fp, check_existing=False)
    w, h = img.size; a = numpy.empty(w * h * img.channels, numpy.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, img.channels); bpy.data.images.remove(img)
    for i, val in enumerate(values):
        res[val]["png"] = round(float(a[h // 2, int((i + 0.45) * w / len(values)), 0]), 4)
    for o in objs:
        me = o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    bpy.data.materials.remove(m)
    bpy.data.collections.remove(coll)
    return res


# ---------------------------------------------------------------- C1 smoke rig
def vki_smoke_rig():
    """VKI_Rig_Smoke in VKI_Test: three smoke walls at rot 0 / 180 / 0 (a 150|150|150 run along y = 0, room on
    the south), the axis piece, and VKI_Test_Slab (a test floor slab, not a master) so the lighting reads"""
    objs = vki_rig("Smoke", [("SM_VKI_Test_Smoke", 0.0, 0.0, 0), ("SM_VKI_Test_Smoke", 3.0, 0.0, 180),
                             ("SM_VKI_Test_Smoke", 3.0, 0.0, 0), ("SM_VKI_Test_Axis", -0.75, -1.5, 0)])
    c = bpy.data.collections["VKI_Rig_Smoke"]
    old = bpy.data.meshes.get("VKI_Test_Slab")
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    k = VKIKit("SM_VKI_Floor_Test")
    k.box((2.25, -0.75, -0.05), (7.5, 4.5, 0.10), VKI_FLOOR, bevel=0)
    o = k.finish("__vki_slab", c, grime="floor")
    o.name = "VKI_Test_Slab"; o.data.name = "VKI_Test_Slab"
    for k_ in list(o.keys()):
        del o[k_]
    return objs + [o]


# ---------------------------------------------------------------- per-piece runner
def vki_test_pieces(names):
    """run the per-master tests on VKI masters: T1, T5S (self-coplanar), T7, T8, T9, T10, T14 always; T2, T3 on
    shipped walls; T13 on walls built from VKI_SPECS. Returns {} when clean, else {piece: {test: [errors]}}"""
    out = {}
    sm = vki_spec_map()
    for n in ([names] if isinstance(names, str) else names):
        o = bpy.data.objects.get(n)
        if o is None:
            out[n] = {"exists": [f"{n}: no such object"]}; continue
        tests = [("T1", vki_t1_bounds), ("T5S", vki_t5s_self_coplanar), ("T7", vki_t7_closed),
                 ("T8", vki_t8_normals), ("T9", vki_t9_budget), ("T10", vki_t10_metadata),
                 ("T14", vki_t14_materials)]
        cls = o.get("vki_class")
        if cls == "wall" and not o.get("vki_test_piece"):
            tests += [("T2", vki_t2_end_profiles), ("T3", vki_t3_node_zone)]
        res = {}
        for tn, fn in tests:
            try:
                e = fn(o)
            except Exception as ex:
                e = [f"{tn} {n}: crashed: {ex!r}"]
            if e:
                res[tn] = e
        if cls == "wall" and n in sm:
            try:
                e = vki_t13_wobble(n)
            except Exception as ex:
                e = [f"T13 {n}: crashed: {ex!r}"]
            if e:
                res["T13"] = e
        if res:
            out[n] = res
    return out


def vki_test_all(t15=False, t18=True):
    """T per master for every object in VKI_Pieces (vki_test_pieces, incl. T5S), T10i on every instance in the VKI_* /
    WS_vki_* scenes, plus T18 (and T15 when asked: it rebuilds everything). T5, T16, T17, T19 run at assembly."""
    c = bpy.data.collections.get("VKI_Pieces")
    names = [o.name for o in c.objects] if c else []
    out = vki_test_pieces(names)
    e = vki_t10_instances()
    if e:
        out["T10i"] = e
    if t18:
        e = vki_t18_namespace()
        if e:
            out["T18"] = e
    if t15:
        e = vki_t15_exterior_invariance()
        if e:
            out["T15"] = e
    return out


# ---------------------------------------------------------------- C3 rigs and seam boards (Timber + floors)
VKI_C3_W = "SM_VKI_Wall_Timber_"
VKI_C3_P = "SM_VKI_Post_Timber_"


def vki_c3_floor_pieces(x0, y0, nx, ny, style=None):
    """cover [x0, x0 + 1.5 nx] x [y0, y0 + 1.5 ny] with floor pieces the assembler's way (600, then 300 at even
    nodes, then the parity Q150). Returns [(piece, x, y, 0[, style])] in absolute coordinates."""
    cells = {(i, j) for i in range(nx) for j in range(ny)}
    out = []
    even = lambda a: abs(a / 3.0 - round(a / 3.0)) < 1e-6
    for S, n in ((6.0, 4), (3.0, 2)):
        for (i, j) in sorted(cells):
            x, y = x0 + 1.5 * i, y0 + 1.5 * j
            blk = {(i + a, j + b) for a in range(n) for b in range(n)}
            if even(x) and even(y) and blk <= cells:
                cells -= blk
                out.append((f"SM_VKI_Floor_{int(S * 100)}", x, y, 0))
    for (i, j) in sorted(cells):
        x, y = x0 + 1.5 * i, y0 + 1.5 * j
        qi, qj = int(round(x / 1.5)) % 2, int(round(y / 1.5)) % 2
        out.append((f"SM_VKI_Floor_150_Q{qi}{qj}", x, y, 0))
    return [it + ((style,) if style else ()) for it in out]


def vki_c3_rigs(scene="VKI_Test"):
    """C3 rigs in VKI_Test. T4 (L, T, X, free end, Full->Cut step) at y -30; seam boards at y -45..-54 (Full and
    Cut 150|300|150 runs at rot 0/180/0, a Full|Cut|Cut300|Full run with Mid posts, a floor-parity board with a
    Flag zone and sills); a 4x4-cell corner room at y -63 (Full north wall, Full east/west walls with a window, a
    door and the Rake at the south end, Cut south wall with a window, the Door_150_Cut exit, its leaf, apron and
    rush mat; Corner / Mid posts by the §2.3 rules). Returns {name: [objects]}."""
    W, P = VKI_C3_W, VKI_C3_P
    out = {}
    rigs = vki_t4_rigs("Timber", P + "Corner_Full", P + "Mid_Full", W + "Plain_150A_Full", cut=W + "Plain_150A_Cut",
                       origin=(0.0, -30.0), scene=scene)
    # fix r1: the 150B brace next to a Mid post (review r1: a brace vertex 2.8 mm inside the Mid post's face)
    rigs["BMid"] = dict(objs=vki_rig("T4_Timber_BMid", [(W + "Plain_150A_Full", -1.5, 0, 0), (W + "Plain_150B_Full", 0, 0, 0),
                                                          (P + "Mid_Full", 0, 0, 0)], origin=(36.0, -30.0), scene=scene),
                        node=(36.0, -30.0))
    # core fix: Window_150_Cut beside a Corner_Cut at an L (review r2: its old cap end ring lay on the post face)
    rigs["WinCutL"] = dict(objs=vki_rig("T4_Timber_WinCutL", [(W + "Window_150_Cut", 0, 0, 0), (W + "Plain_150A_Cut", 0, 0, 90),
                                                              (P + "Corner_Cut", 0, 0, 0)], origin=(42.0, -30.0), scene=scene),
                           node=(42.0, -30.0))
    out["T4"] = rigs
    fl = lambda x0, y0, nx, ny, st=None: vki_c3_floor_pieces(x0, y0, nx, ny, st)
    # seam runs: 150 | 300 | 150 at rot 0 / 180 / 0 (the 300's origin is its east end at rot 180)
    # (free ends carry Mid posts, as §2.3 asks; the rhythm posts at the even nodes are left out so the runs show
    # their seams)
    out["SeamFull"] = vki_rig("C3_SeamFull", [(W + "Plain_150A_Full", 0, -45, 0), (W + "Plain_300_Full", 4.5, -45, 180),
                                              (W + "Plain_150B_Full", 4.5, -45, 0), (P + "Mid_Full", 0, -45, 0),
                                              (P + "Mid_Full", 6, -45, 0)] + fl(0, -48, 4, 2), scene=scene)
    out["SeamCut"] = vki_rig("C3_SeamCut", [(W + "Plain_150A_Cut", 0, -51, 0), (W + "Plain_300_Cut", 4.5, -51, 180),
                                            (W + "Plain_150A_Cut", 4.5, -51, 0), (P + "Mid_Cut", 0, -51, 0),
                                            (P + "Mid_Cut", 6, -51, 0)] + fl(0, -54, 4, 2), scene=scene)
    # Full | Cut | Cut 300 | Full with Mid posts at both height steps
    out["FullCut"] = vki_rig("C3_FullCut", [(W + "Plain_150A_Full", 9, -45, 0), (W + "Plain_150A_Cut", 10.5, -45, 0),
                                            (W + "Plain_300_Cut", 12, -45, 0), (W + "Plain_150A_Full", 15, -45, 0),
                                            (P + "Mid_Full", 10.5, -45, 0), (P + "Mid_Full", 15, -45, 0),
                                            (P + "Mid_Full", 9, -45, 0), (P + "Mid_Full", 16.5, -45, 0)] +
                             fl(9, -48, 5, 2), scene=scene)
    # floor parity board: Boards_NS in rows y -51..-45 (planks must run on across every piece joint: 600, 300 and
    # all four Q150 parities meet here), a Flag band y -54..-51 with a straight sill run on the y -51 grid line
    # (two sills meeting at an L would overlap in a 0.1 m corner square: see api_notes)
    F = "SM_VKI_Floor_"
    items = [(F + "600", 21, -51, 0), (F + "300", 18, -51, 0), (F + "150_Q00", 18, -48, 0), (F + "150_Q10", 19.5, -48, 0),
             (F + "150_Q01", 18, -46.5, 0), (F + "150_Q11", 19.5, -46.5, 0), (F + "150_Q00", 27, -51, 0),
             (F + "150_Q01", 27, -49.5, 0), (F + "150_Q00", 27, -48, 0), (F + "150_Q01", 27, -46.5, 0)]
    items += fl(18, -54, 7, 2, {"floor": "Flag"})
    items += [("SM_VKI_Floor_Sill_150", 18 + 1.5 * i, -51, 0) for i in range(7)]
    out["Floors"] = vki_rig("C3_Floors", items, scene=scene)
    # corner room 4 x 4 cells, SW node (0, -63)
    y0 = -63.0; yN = y0 + 6.0
    items = [  # north wall (rot 0, origin W end)
        (W + "Plain_150A_Full", 0, yN, 0), (W + "Door_150_Full", 1.5, yN, 0), (W + "Window_150_Full", 3.0, yN, 0),
        (W + "Plain_150B_Full", 4.5, yN, 0),
        # east wall (rot -90, origin N end): the rake is the south-most piece, low end south = _R
        (W + "Plain_150A_Full", 6, yN, -90), (W + "Window_150_Full", 6, yN - 1.5, -90),
        (W + "Plain_150A_Full", 6, yN - 3.0, -90), (W + "Rake_150_R", 6, yN - 4.5, -90),
        # south wall (rot 180, origin E end): Cut, window Cut and the exit
        (W + "Plain_150A_Cut", 6, y0, 180), (W + "Window_150_Cut", 4.5, y0, 180), (W + "Door_150_Cut", 3.0, y0, 180),
        (W + "Plain_150A_Cut", 1.5, y0, 180),
        # west wall (rot +90, origin S end): rake low end south = _L
        (W + "Rake_150_L", 0, y0, 90), (W + "Plain_150A_Full", 0, y0 + 1.5, 90), (W + "Door_150_Full", 0, y0 + 3.0, 90),
        (W + "Plain_150A_Full", 0, y0 + 4.5, 90),
        # posts: Corners (NW/NE Full, SW/SE Cut: the rakes' low ends and the Cut south wall), rhythm Mids at the
        # even nodes of straight same-height runs (north x 3, east/west y -60, south x 3)
        (P + "Corner_Full", 0, yN, 0), (P + "Corner_Full", 6, yN, 0), (P + "Corner_Cut", 6, y0, 0),
        (P + "Corner_Cut", 0, y0, 0), (P + "Mid_Full", 3, yN, 0), (P + "Mid_Full", 6, y0 + 3.0, 90),
        (P + "Mid_Full", 0, y0 + 3.0, 90), (P + "Mid_Cut", 3, y0, 0),
        # the exit: apron (door origin + rotation), closed leaf at the door's leaf socket
        ("SM_VKI_Apron_300x150", 3.0, y0, 180), ("SM_VKI_Leaf_Plank_Cut", 3.0 - 0.33, y0 + 0.20, 180),
    ] + fl(0, y0, 4, 4)
    objs = vki_rig("C3_Corner", items, scene=scene)
    c = bpy.data.collections["VKI_Rig_C3_Corner"]
    objs.append(vki_place(c, "SM_VKI_RushMat", 2.25, y0 + 0.75, 0, walls=[]))
    out["Corner"] = objs
    return out


def vki_c3_tests(rigs):
    """T4 coverage, T5 coplanar, T6 UV continuity and T11 placement on the C3 rigs -> {test: [errors]}"""
    res = {}
    e = vki_t4_coverage(rigs["T4"])
    if e:
        res["T4"] = e
    for k_ in ("SeamFull", "SeamCut", "FullCut", "Floors", "Corner"):
        objs = [o for o in rigs[k_] if o.type == "MESH"]
        for tn, fn in (("T5", lambda: vki_t5_coplanar(objs)), ("T6", lambda: vki_t6_uv_continuity(objs)),
                       ("T11", lambda: vki_t11_placement(objs))):
            e = fn()
            if e:
                res[f"{tn} {k_}"] = e
    for tag, rg in rigs["T4"].items():
        e = vki_t5_coplanar(rg["objs"]) + vki_t11_placement(rg["objs"])
        if e:
            res[f"T5/T11 T4_{tag}"] = e
    return res


# ---------------------------------------------------------------- C3 look test: VKI_LookTest (6 x 5 cells, Timber)
VKI_LT = "VKI_LookTest"
# §1 fit camera with a 0.4 m far margin (fix r1): D = (7.5 + 1.5 + 0.4 + 1.428 * 3) / 0.737 = 18.57,
# y_t = y_S - 1.5 + 0.2856 D = 3.804. The plain §1 formula (D 18.02) puts the north wall LINE on the top frame edge,
# which cut off the far caps (to y + 0.28) and post tops (y + 0.31).
VKI_LT_MARGIN = VKI_FIT_MARGIN
VKI_LT_CAM = {k_: v_ for k_, v_ in vki_fit_camera((0.0, 0.0, 9.0, 7.5), "Timber").items() if k_ in ("D", "target")}
VKI_LT_HALL_FLOOR = "FlagRustic"      # §6 Cottage: hall FlagRustic / PlasterCream, bed Boards_NS


def vki_lt_coll(sc, suffix):
    n = f"{VKI_LT}_{suffix}"
    c = bpy.data.collections.get(n)
    if c is None:
        c = bpy.data.collections.new(n)
    if c.name not in sc.collection.children:
        sc.collection.children.link(c)
    return c


def vki_lt_clear(c):
    for o in list(c.objects):
        d = o.data
        bpy.data.objects.remove(o)
        if isinstance(d, bpy.types.Light) and d.users == 0:
            bpy.data.lights.remove(d)


def vki_looktest(pillar=False, leaf_deg=0.0, night=False):
    """build VKI_LookTest: the Cottage footprint (6 x 5 cells, 9 x 7.5 m) in Timber with every Timber kind.
    North Full: 150A | 150B | Fireplace_300 | 150A | Window. West Full: Rake_L | 150A | Window | Plain_300.
    East Full: 150A | Window | 150A | Door_150_Full (closed back door, Leaf_Plank_Full) | Rake_R. South Cut: 150A |
    Window_Cut | 150A | Door_150_Cut exit (Leaf_Plank_Cut, Apron, RushMat) | Plain_300_Cut. Cut partitions: x 6
    (Door_150_Cut doorway, Plain_300_Cut) and y 3 (Plain_300_Cut). Hall Flag, bedroom Boards_NS; Rug; reused props
    with the §5.5 style. pillar=True: the side walls' south-most pieces are Full plain and the SW/SE Corner posts
    Full (G1 option). leaf_deg: the exit leaf opened into the room by that angle (G1 option: ajar 30).
    night=True: VKI masters get VKI_NIGHT_STYLE (Window_Night glass) and reused props VKI_REUSE_STYLE_NIGHT (§4.1);
    render Night shots from a night build."""
    sc = vki_scene(VKI_LT, preset="Day")
    shell, props, logic, lights = (vki_lt_coll(sc, s) for s in ("Shell", "Props", "Logic", "Lights"))
    for c in (shell, props, logic, lights):
        vki_lt_clear(c)
    W, P = VKI_C3_W, VKI_C3_P
    sw = [(W + "Plain_150A_Full", 0, 0, 90), (W + "Plain_150A_Full", 9, 1.5, -90)] if pillar else \
         [(W + "Rake_150_L", 0, 0, 90), (W + "Rake_150_R", 9, 1.5, -90)]
    sh = "Full" if pillar else "Cut"
    walls = [
        (W + "Plain_150A_Full", 0, 7.5, 0), (W + "Plain_150B_Full", 1.5, 7.5, 0), (W + "Fireplace_300_Full", 3, 7.5, 0),
        (W + "Plain_150A_Full", 6, 7.5, 0), (W + "Window_150_Full", 7.5, 7.5, 0),
        sw[0], (W + "Plain_150A_Full", 0, 1.5, 90), (W + "Window_150_Full", 0, 3.0, 90), (W + "Plain_300_Full", 0, 4.5, 90),
        (W + "Plain_150A_Full", 9, 7.5, -90), (W + "Window_150_Full", 9, 6.0, -90), (W + "Plain_150A_Full", 9, 4.5, -90),
        (W + "Door_150_Full", 9, 3.0, -90), sw[1],
        (W + "Plain_300_Cut", 9, 0, 180), (W + "Door_150_Cut", 6, 0, 180), (W + "Plain_150A_Cut", 4.5, 0, 180),
        (W + "Window_150_Cut", 3, 0, 180), (W + "Plain_150A_Cut", 1.5, 0, 180),
        (W + "Door_150_Cut", 6, 3, 90), (W + "Plain_300_Cut", 6, 4.5, 90), (W + "Plain_300_Cut", 6, 3, 0),
        # posts (§2.3): Corners at L/T junctions (height = tallest wall end), rhythm Mids at even nodes
        (P + "Corner_Full", 0, 7.5, 0), (P + "Corner_Full", 9, 7.5, 0), (P + "Corner_" + sh, 0, 0, 0),
        (P + "Corner_" + sh, 9, 0, 0), (P + "Corner_Full", 6, 7.5, 0), (P + "Corner_Full", 9, 3, 0),
        (P + "Corner_Cut", 6, 3, 0),
        (P + "Mid_Full", 3, 7.5, 0), (P + "Mid_Full", 0, 3, 90), (P + "Mid_Full", 9, 6, 90), (P + "Mid_Cut", 6, 0, 0),
        (P + "Mid_Cut", 3, 0, 0),
        # links and leaves: the exit (door origin + rotation) with its closed / ajar leaf; the closed back door
        ("SM_VKI_Apron_300x150", 6, 0, 180), ("SM_VKI_Leaf_Plank_Cut", 6 - 0.33, 0.20, 180 - leaf_deg),
        ("SM_VKI_Leaf_Plank_Full", 9 - 0.20, 3.0 - 0.33, -90),
    ]
    flag = {"floor": VKI_LT_HALL_FLOOR}
    floors = vki_c3_floor_pieces(0, 0, 4, 5, flag) + vki_c3_floor_pieces(6, 0, 2, 2, flag) + \
        vki_c3_floor_pieces(6, 3, 2, 3)
    out = []
    for it in walls + floors:
        piece, x, y, rot = it[:4]
        st = dict(it[4]) if len(it) > 4 else {}
        if night and (piece.startswith("SM_VKI_Wall_") or piece.startswith("SM_VKI_Leaf_")):
            st.update(VKI_NIGHT_STYLE)
        o = vki_place(shell, piece, x, y, rot, style=st or None, walls=[])
        if "Door_150_Cut" in piece and y == 0:
            o["vki_link"] = "exit"; o["vki_link_id"] = "front"; o["vki_target"] = "@return"
            o["vki_prompt"] = "Leave"; o["vki_facing_min"] = 60
        if "Leaf" in piece:
            o["vki_leaf_state"] = "ajar" if (leaf_deg and "Cut" in piece) else "closed"
            o["vki_leaf_deg"] = leaf_deg if "Cut" in piece else 0.0
        out.append(o)
    # props (the prop list is the source of truth): overlays and reused exterior props (§5.5 style)
    # fix r1: the N-S Cut partition doorway (x 6, y 3.33-4.17) is hidden by its own 1.0 m jamb from the north-looking
    # camera (1.0 / tan 50 = 0.84 m = the opening), so it gets a floor cue a room designer would give it: a rush mat
    # on each side (overlays never cross a threshold), both visible because a N-S wall hides nothing sideways
    for piece, x, y, rot, kw in (("SM_VKI_RushMat", 5.25, 0.75, 0, {}), ("SM_VKI_Rug_300x150", 4.5, 5.25, 0, {}),
                                 ("SM_VKI_RushMat", 5.25, 3.75, 90, {}), ("SM_VKI_RushMat", 6.75, 4.5, 90, {}),
                                 ("SM_VK_Prop_Loom", 1.5, 6.0, 0, dict(mount="wall_floor")),
                                 ("SM_VK_Prop_Stool", 3.75, 5.25, 0, {}), ("SM_VK_Prop_Stool", 5.25, 5.25, 0, {}),
                                 ("SM_VK_Prop_Table", 3.0, 2.25, 0, {}), ("SM_VK_Prop_Bench", 3.0, 1.5, 0, {}),
                                 ("SM_VK_Prop_Bench", 3.0, 3.0, 180, {}),
                                 ("SM_VK_Prop_SpinningWheel", 6.75, 6.75, 0, dict(hug=True)),
                                 ("SM_VK_Prop_Bedroll", 8.25, 4.5, 0, {})):
        if night and piece.startswith("SM_VK_Prop_"):
            kw = dict(kw, style=dict(VKI_REUSE_STYLE_NIGHT))
        out.append(vki_place(props, piece, x, y, rot, **kw))
    # logic: spawn, root (fit camera)
    sp = bpy.data.objects.new("SPN_front", None); logic.objects.link(sp)
    sp.location = (5.25, 1.60, 0.0); sp.empty_display_type = "SINGLE_ARROW"
    sp["vki_spawn_id"] = "front"; sp["vki_facing_deg"] = 0
    rt = bpy.data.objects.new("VKI_Root", None); logic.objects.link(rt)
    for k_, v_ in dict(vki_building="LookTest", vki_floor=0, vki_cam_mode="fit", vki_cam_dist=VKI_LT_CAM["D"],
                       vki_cam_target=json.dumps(list(VKI_LT_CAM["target"])), vki_cam_pitch=50, vki_cam_yaw=0,
                       vki_bounds=json.dumps([0, 0, 9, 7.5]), vki_default_spawn="front").items():
        rt[k_] = v_
    sc["vki_cam_dist"] = VKI_LT_CAM["D"]; sc["vki_cam_target"] = json.dumps(list(VKI_LT_CAM["target"]))
    sc["vki_room_bounds"] = json.dumps([0, 0, 9, 7.5]); sc["vki_family"] = "Timber"
    sc["vki_bounds"] = json.dumps([-0.9, -1.9, 9.9, 8.4])
    sc["vki_preset"] = "Night" if night else "Day"
    vki_lt_lights(sc, shell, lights)
    return out


def vki_lt_lights(sc, shell, lights):
    """Blender lights + LGT_* data from the placed masters' vki_lights (window spots, hearth socket, apron area).
    Each light keeps its day and night power; vki_lt_preset(sc, preset) switches them (the key, fill and world are
    set by the preset in vki_shot)."""
    n = 0
    for o in list(shell.objects):
        for L in vki_get(o, "vki_lights", None) or []:
            mw = vki_mw(o)
            typ = L.get("type", "POINT")
            ld = bpy.data.lights.new(f"LGT_{o.name}_{n}", typ)
            lo = bpy.data.objects.new(f"LGT_{o.name}_{n}", ld); lights.objects.link(lo); n += 1
            lo.location = mw @ Vector(L["pos"])
            if "aim" in L:
                d = (mw @ Vector(L["aim"])) - lo.location
                lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
            wd = float(L.get("w_day", L.get("w", 100.0))); wn = float(L.get("w_night", L.get("w", 100.0)))
            cd = L.get("color_day", L.get("color", [1, 1, 1])); cn = L.get("color_night", L.get("color", [1, 1, 1]))
            lo["vki_w_day"] = wd; lo["vki_w_night"] = wn
            lo["vki_color_day"] = json.dumps(cd); lo["vki_color_night"] = json.dumps(cn)
            lo["vki_light"] = json.dumps(dict(type=typ, role=L.get("role"), color=cd, intensity=wd,
                                              range=L.get("range"), flicker=L.get("flicker", 0),
                                              shadows=L.get("shadows", 1), blender_w=wd))
            ld.energy = wd; ld.color = cd
            ld.use_shadow = bool(L.get("shadows", 1))
            if typ == "SPOT":
                ld.spot_size = math.radians(L.get("cone", 60.0)); ld.spot_blend = L.get("blend", 0.35)
                ld.shadow_soft_size = L.get("radius", 0.25)
            elif typ == "AREA":
                ld.size = L.get("size", 1.0)
            else:
                ld.shadow_soft_size = L.get("radius", 0.1)
    return n


def vki_lt_preset(sc, preset):
    """window and apron lights to the preset's values (hearths keep theirs); returns a restore callable"""
    old = []
    for o in sc.objects:
        if o.type == "LIGHT" and "vki_w_day" in o.keys():
            old.append((o, o.data.energy, tuple(o.data.color)))
            day = preset == "Day"
            o.data.energy = o["vki_w_day"] if day else o["vki_w_night"]
            o.data.color = json.loads(o["vki_color_day"] if day else o["vki_color_night"])

    def restore():
        for o, e, c in old:
            o.data.energy = e; o.data.color = c
    return restore


def vki_lt_shot(name, preset="Day", mode="game", **kw):
    """vki_shot on VKI_LookTest with the scene lights switched to the preset (game mode = the fit camera)"""
    sc = bpy.data.scenes[VKI_LT]
    rs = vki_lt_preset(sc, preset)
    try:
        if mode == "game":
            kw.setdefault("D", VKI_LT_CAM["D"]); kw.setdefault("target", VKI_LT_CAM["target"])
        return vki_shot(sc, name, mode, preset=preset, **kw)
    finally:
        rs()


def vki_luma_stats(path, boxes):
    """mean Rec.709 luma (display values) of the PNG inside pixel boxes [(x0, y0, x1, y1)], y from the top"""
    import numpy
    im = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = im.size
        a = numpy.array(im.pixels[:], dtype=numpy.float32).reshape(h, w, 4)[::-1]
        out = []
        for x0, y0, x1, y1 in boxes:
            r = a[y0:y1, x0:x1, :3]
            out.append(float((0.2126 * r[..., 0] + 0.7152 * r[..., 1] + 0.0722 * r[..., 2]).mean()))
        return out
    finally:
        bpy.data.images.remove(im)


VKI_LT_FLOOR_BOXES = [(480, 450, 800, 540), (920, 470, 1080, 540), (470, 580, 640, 780), (910, 560, 1090, 780),
                      (1100, 630, 1460, 780), (1170, 290, 1320, 480)]     # bare floor in the D 18.02 fit shot (C3)
# walkable bare floor of the look test in WORLD rectangles (x0, y0, x1, y1), clear of props and overlays (fix r1:
# camera independent, so the metric survives camera changes; points hidden behind walls / props are dropped)
VKI_LT_FLOOR_RECTS = [(0.55, 1.6, 1.6, 4.4), (4.6, 2.2, 5.6, 2.9), (2.0, 3.55, 4.4, 4.45), (6.4, 1.5, 8.5, 2.45),
                      (6.45, 4.9, 7.6, 6.2), (0.6, 4.6, 2.9, 4.8), (7.4, 5.3, 8.5, 6.6)]


def vki_cam_project(P, D, target, res=(1920, 1080), pitch=None, lens=None, sensor=None):
    """pixel (x, y from the top) of world point P in the §1 game camera (vki_shot mode "game")"""
    p = math.radians(pitch or VKI_CAM["pitch"])
    C = Vector(target) + Vector((0, -math.cos(p) * D, math.sin(p) * D))
    R = Matrix.Rotation(math.radians(90 - (pitch or VKI_CAM["pitch"])), 3, "X")
    c = R.transposed() @ (Vector(P) - C)
    f = (lens or VKI_CAM["lens"]) / ((sensor or VKI_CAM["sensor"]) / 2.0)     # AUTO fit: sensor spans the width
    w, h = res
    xn = f * c.x / -c.z; yn = f * c.y / -c.z * (w / h)
    return ((xn + 1) / 2 * w, (1 - yn) / 2 * h), C


def vki_floor_luma_world(path, rects, D, target, scene=VKI_LT, step=0.1, tol=0.03):
    """mean display luma of a game shot at the pixels of world floor points (a `step` grid inside `rects`, z 0),
    keeping only points whose camera ray first hits within `tol` of the point (not hidden by a wall or prop).
    Returns (mean, number of points used, number dropped)."""
    import numpy
    sc = bpy.data.scenes[scene]
    dg = vki_depsgraph(sc)
    im = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = im.size
        a = numpy.array(im.pixels[:], dtype=numpy.float32).reshape(h, w, 4)[::-1]
        vals, drop = [], 0
        for x0, y0, x1, y1 in rects:
            nx, ny = max(1, int((x1 - x0) / step)), max(1, int((y1 - y0) / step))
            for i in range(nx + 1):
                for j in range(ny + 1):
                    P = Vector((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, 0.0))
                    (px, py), C = vki_cam_project(P, D, target, (w, h))
                    d = P - C
                    hit, loc, nrm, idx, ob, mat = sc.ray_cast(dg, C, d.normalized(), distance=d.length + 1.0)
                    if not hit or (loc - P).length > tol or not (0 <= px < w and 0 <= py < h):
                        drop += 1
                        continue
                    r = a[int(py), int(px), :3]
                    vals.append(float(0.2126 * r[0] + 0.7152 * r[1] + 0.0722 * r[2]))
        return (sum(vals) / len(vals) if vals else 0.0), len(vals), drop
    finally:
        bpy.data.images.remove(im)


def vki_lt_floor_luma(path, D=None, target=None):
    """mean display luma of the look test's walkable bare floor in a 1920x1080 game shot (§9 visual 3: >= 0.25 by
    Day, >= 0.15 by Night); world-rectangle sampling (VKI_LT_FLOOR_RECTS) at the look-test fit camera"""
    return vki_floor_luma_world(path, VKI_LT_FLOOR_RECTS, D or VKI_LT_CAM["D"], target or VKI_LT_CAM["target"])[0]


# ---------------------------------------------------------------- G1 level metrics (core fix)
# world boxes (x0, y0, z0, x1, y1, z1) around the look test's fire, NE window glass, firebox and hearth; inside the
# projected box only pixels whose camera ray hits a face of the given slot count (so bricks never pass as flames)
VKI_LT_LEVEL_BOXES = dict(fire=((4.05, 6.85, 0.05, 5.0, 7.32, 0.85), "GLOW"),
                          glass_ne=((7.90, 7.50, 0.95, 8.60, 7.70, 2.30), "WINDOW"),
                          bricks=((3.65, 6.60, 0.0, 5.35, 7.32, 1.35), "BRICK"),
                          hearth=((3.30, 6.00, 0.0, 5.70, 6.70, 0.05), "DRESS"))


def vki_cam_ray(px, py, D, target, res=(1920, 1080), pitch=None, lens=None, sensor=None):
    """world ray (origin, unit direction) through pixel (px, py from the top) of the §1 game camera"""
    p = math.radians(pitch or VKI_CAM["pitch"])
    C = Vector(target) + Vector((0, -math.cos(p) * D, math.sin(p) * D))
    R = Matrix.Rotation(math.radians(90 - (pitch or VKI_CAM["pitch"])), 3, "X")
    f = (lens or VKI_CAM["lens"]) / ((sensor or VKI_CAM["sensor"]) / 2.0)
    w, h = res
    xn = 2.0 * px / w - 1.0; yn = 1.0 - 2.0 * py / h
    return C, (R @ Vector((xn / f, yn / (f * w / h), -1.0))).normalized()


def vki_lt_levels(path, D=None, target=None, scene=VKI_LT):
    """G1 brightness order on a look-test game shot (any resolution): walkable-floor mean (world-rectangle metric);
    fire = p90 luma of the pixels whose camera ray hits a GLOW face (flames, embers); glass_ne = p95 of the NE
    window's WINDOW-slot pixels; bricks / hearth = p90 of the BRICK / DRESS pixels of the firebox / hearth. The
    fire must lead the glass by Day and by Night; bricks <= ~0.5."""
    import numpy
    D = D or VKI_LT_CAM["D"]; target = target or VKI_LT_CAM["target"]
    sc = bpy.data.scenes[scene]
    dg = vki_depsgraph(sc)
    floor = vki_floor_luma_world(path, VKI_LT_FLOOR_RECTS, D, target, scene=scene)
    im = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = im.size
        a = numpy.array(im.pixels[:], dtype=numpy.float32).reshape(h, w, 4)[::-1, :, :3]
    finally:
        bpy.data.images.remove(im)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    slots = {"GLOW": GLOW, "WINDOW": WINDOW, "BRICK": VKI_BRICK, "DRESS": DRESS}
    out = dict(floor=round(floor[0], 4), floor_n=floor[1])
    for key, ((x0, y0, z0, x1, y1, z1), sl) in VKI_LT_LEVEL_BOXES.items():
        pts = [vki_cam_project((x, y, z), D, target, (w, h))[0] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
        px0, px1 = max(0, int(min(p[0] for p in pts))), min(w, int(max(p[0] for p in pts)) + 1)
        py0, py1 = max(0, int(min(p[1] for p in pts))), min(h, int(max(p[1] for p in pts)) + 1)
        vals = []
        for py in range(py0, py1):
            for px in range(px0, px1):
                C, d = vki_cam_ray(px + 0.5, py + 0.5, D, target, (w, h))
                hit, loc, nrm, idx, ob, mat = sc.ray_cast(dg, C, d)
                if not hit or not (x0 - 0.05 <= loc.x <= x1 + 0.05 and y0 - 0.05 <= loc.y <= y1 + 0.05 and
                                   z0 - 0.05 <= loc.z <= z1 + 0.05):
                    continue
                me = ob.original.data if ob.original.type == "MESH" else None
                if me is None or idx >= len(me.polygons) or me.polygons[idx].material_index != slots[sl]:
                    continue
                vals.append(float(lum[py, px]))
        out[key + "_n"] = len(vals)
        out[key] = round(float(numpy.percentile(vals, 95 if key.startswith("glass") else 90)), 4) if vals else None
    return out
