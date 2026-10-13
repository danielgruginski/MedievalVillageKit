# Z-fighting scan, layer 1: every master piece of the Medieval Village Kit on its own (background Blender, read-only:
# nothing is saved). Triangles of one piece that lie in the same plane (either facing: the kit draws two-sided) and
# overlap in it by more than 1 cm2 -- between two materials (a frame flush on a wall) or within one (two parts on top of
# each other). One CSV line per piece and material pair: piece, collection, matA, matB, area m2, triangle pairs, where
# (the first pair's middle, piece space), the plane's normal.
#   blender -b medievalDiorama.blend --python zfight_scan_pieces.py -- out.csv
import bpy, sys, time, math
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
ONLY = args[1] if len(args) > 1 else ""
COLLS = ["VK_Pieces", "VKI_Pieces"]
MIN_TRI = 1e-4          # m2: smaller triangles are ignored
MIN_OV = 1e-4           # m2: smaller overlaps are ignored
D_STEP = 0.002          # m: planes closer than this count as one


def clip(poly, p, q):
    ex, ey = q[0] - p[0], q[1] - p[1]
    o = []
    n = len(poly)
    for i in range(n):
        A = poly[i]; B = poly[(i + 1) % n]
        sa = ex * (A[1] - p[1]) - ey * (A[0] - p[0])
        sb = ex * (B[1] - p[1]) - ey * (B[0] - p[0])
        if sa >= 0: o.append(A)
        if (sa >= 0) != (sb >= 0):
            t = sa / (sa - sb)
            o.append((A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t))
    return o


def area(p):
    s = 0.0
    for i in range(len(p)):
        a = p[i]; b = p[(i + 1) % len(p)]
        s += a[0] * b[1] - b[0] * a[1]
    return abs(s) * 0.5


def ccw(t):
    a, b, c = t
    if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0:
        return [a, c, b]
    return [a, b, c]


def overlap(s, t):
    poly = ccw(s); cl = ccw(t)
    for i in range(3):
        if len(poly) < 3: return 0.0
        poly = clip(poly, cl[i], cl[(i + 1) % 3])
    return area(poly) if len(poly) > 2 else 0.0


def scan(ob, dg):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        if nt == 0: return []
        co = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        tv = np.empty(nt * 3, np.int64); me.loop_triangles.foreach_get("vertices", tv); tv = tv.reshape(-1, 3)
        mi = np.empty(nt, np.int64); me.loop_triangles.foreach_get("material_index", mi)
        A, B, C = co[tv[:, 0]], co[tv[:, 1]], co[tv[:, 2]]
        n = np.cross(B - A, C - A)
        a2 = np.linalg.norm(n, axis=1)
        keep = a2 * 0.5 >= MIN_TRI
        if keep.sum() < 2: return []
        A, B, C, n, a2, tv, mi = A[keep], B[keep], C[keep], n[keep], a2[keep], tv[keep], mi[keep]
        n = n / a2[:, None]
        # one sign for both facings
        flip = (n[:, 0] < -1e-4) | ((np.abs(n[:, 0]) <= 1e-4) & ((n[:, 1] < -1e-4) | ((np.abs(n[:, 1]) <= 1e-4) & (n[:, 2] < 0))))
        nc = np.where(flip[:, None], -n, n)
        nf = n                                   # the true facing
        d = np.einsum("ij,ij->i", nc, A)
        kn = np.round(nc * 100).astype(np.int64)
        kd = np.round(d / D_STEP).astype(np.int64)
        groups = {}
        for i in range(len(A)):
            groups.setdefault((kn[i, 0], kn[i, 1], kn[i, 2], kd[i]), []).append(i)
        slots = [s.material.name if s.material else "-" for s in ob.material_slots]
        pairs = {}
        for key, own in groups.items():
            nxt = groups.get((key[0], key[1], key[2], key[3] + 1), [])
            idx = own + nxt
            if len(idx) < 2: continue
            nown = len(own)
            nrm = nc[own[0]]
            u = np.cross(nrm, [0, 0, 1] if abs(nrm[2]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u)
            v = np.cross(nrm, u)
            P = lambda X: np.stack([X @ u, X @ v], axis=1)
            pa, pb, pc = P(A[idx]), P(B[idx]), P(C[idx])
            mn = np.minimum(np.minimum(pa, pb), pc); mx = np.maximum(np.maximum(pa, pb), pc)
            m = len(idx)
            # candidate pairs: boxes that overlap (sweep on x)
            order = np.argsort(mn[:, 0])
            for oi in range(m):
                i = order[oi]
                for oj in range(oi + 1, m):
                    j = order[oj]
                    if mn[j, 0] >= mx[i, 0]: break
                    if i >= nown and j >= nown: continue
                    if mn[j, 1] >= mx[i, 1] or mn[i, 1] >= mx[j, 1] or mx[j, 0] <= mn[i, 0]: continue
                    ti, tj = idx[i], idx[j]
                    if len(set(tv[ti]) & set(tv[tj])) >= 2: continue      # neighbours on one surface
                    ov = overlap([tuple(pa[i]), tuple(pb[i]), tuple(pc[i])], [tuple(pa[j]), tuple(pb[j]), tuple(pc[j])])
                    if ov < MIN_OV: continue
                    k = (min(mi[ti], mi[tj]), max(mi[ti], mi[tj]))
                    acc = pairs.get(k)
                    w = (A[ti] + B[ti] + C[ti] + A[tj] + B[tj] + C[tj]) / 6
                    same = float(np.dot(nf[ti], nf[tj])) > 0
                    sa, oa_ = (ov, 0.0) if same else (0.0, ov)
                    pairs[k] = (ov, 1, w, nrm, sa, oa_) if acc is None else (acc[0] + ov, acc[1] + 1, acc[2], acc[3], acc[4] + sa, acc[5] + oa_)
        rows = []
        for (a, b), (ar, cnt, w, nrm, sa, oa_) in pairs.items():
            ma = slots[a] if a < len(slots) else f"slot{a}"; mb = slots[b] if b < len(slots) else f"slot{b}"
            rows.append(f"{ob.name},{ma},{mb},{ar:.4f},{cnt},{w[0]:.2f} {w[1]:.2f} {w[2]:.2f},{nrm[0]:.2f} {nrm[1]:.2f} {nrm[2]:.2f},{sa:.4f},{oa_:.4f}")
        return rows
    finally:
        ev.to_mesh_clear()


t0 = time.time()
dg = bpy.context.evaluated_depsgraph_get()
lines = ["piece,collection,matA,matB,area_m2,pairs,where,normal,same_facing_m2,touching_m2"]
count = 0
for cname in COLLS:
    col = bpy.data.collections.get(cname)
    if col is None:
        print("no collection", cname); continue
    for ob in sorted(col.all_objects, key=lambda o: o.name):
        if ob.type != "MESH" or (ONLY and ONLY not in ob.name): continue
        count += 1
        try:
            for r in scan(ob, dg):
                lines.append(r.replace(",", "," + cname + ",", 1) if False else r.split(",", 1)[0] + "," + cname + "," + r.split(",", 1)[1])
        except Exception as e:
            lines.append(f"{ob.name},{cname},ERROR,{e},0,0,,")
        if count % 50 == 0:
            print(f"{count} pieces, {time.time() - t0:.0f}s", flush=True)
            with open(out, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
with open(out, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
print(f"done: {count} pieces, {len(lines) - 1} lines, {time.time() - t0:.0f}s", flush=True)
