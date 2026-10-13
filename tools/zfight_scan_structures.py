# Z-fighting scan, layer 2: the kit's premade structures as assembled (scene VKX_Structures, one collection
# VKX_ST_<name> each; background Blender, read-only). Triangles of two different pieces that lie in the same plane
# (either facing) and overlap in it by more than 1 cm2. One CSV line per structure and piece pair: structure, pieceA,
# pieceB (master names), matA, matB, area m2, pairs, where (world), normal. Within-piece overlaps are layer 1's.
#   blender -b medievalDiorama.blend --python zfight_scan_structures.py -- out.csv [name filter]
import bpy, sys, time, re
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
ONLY = args[1] if len(args) > 1 else ""
exec(open(__file__.replace("zfight_scan_structures.py", "zfight_scan_pieces.py"), encoding="utf-8").read().split("t0 = time.time()")[0]
     .split("def scan(")[0].replace('out = args[0]', 'pass').replace('ONLY = args[1] if len(args) > 1 else ""', 'pass'))


def master(name):
    return re.sub(r"(_inst)?\.\d+$", "", name)


def tris_of(ob, dg):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        if nt == 0: return None
        co = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        M = np.array(ob.matrix_world)
        co = co @ M[:3, :3].T + M[:3, 3]
        tv = np.empty(nt * 3, np.int64); me.loop_triangles.foreach_get("vertices", tv); tv = tv.reshape(-1, 3)
        mi = np.empty(nt, np.int64); me.loop_triangles.foreach_get("material_index", mi)
        slots = [s.material.name if s.material else "-" for s in ob.material_slots]
        return co[tv[:, 0]], co[tv[:, 1]], co[tv[:, 2]], np.array([slots[m] if m < len(slots) else "-" for m in mi])
    finally:
        ev.to_mesh_clear()


def scan_structure(col, dg):
    obs = [o for o in col.all_objects if o.type == "MESH" and not o.hide_render]
    As, Bs, Cs, mats, owner = [], [], [], [], []
    for k, ob in enumerate(obs):
        t = tris_of(ob, dg)
        if t is None: continue
        A, B, C, m = t
        As.append(A); Bs.append(B); Cs.append(C); mats.append(m); owner.append(np.full(len(A), k))
    if not As: return []
    A, B, C = np.concatenate(As), np.concatenate(Bs), np.concatenate(Cs)
    mats = np.concatenate(mats); owner = np.concatenate(owner)
    n = np.cross(B - A, C - A); a2 = np.linalg.norm(n, axis=1)
    keep = a2 * 0.5 >= MIN_TRI
    A, B, C, n, a2, mats, owner = A[keep], B[keep], C[keep], n[keep], a2[keep], mats[keep], owner[keep]
    n = n / a2[:, None]
    flip = (n[:, 0] < -1e-4) | ((np.abs(n[:, 0]) <= 1e-4) & ((n[:, 1] < -1e-4) | ((np.abs(n[:, 1]) <= 1e-4) & (n[:, 2] < 0))))
    nc = np.where(flip[:, None], -n, n)
    nf = n
    d = np.einsum("ij,ij->i", nc, A)
    kn = np.round(nc * 100).astype(np.int64); kd = np.round(d / D_STEP).astype(np.int64)
    groups = {}
    for i in range(len(A)):
        groups.setdefault((kn[i, 0], kn[i, 1], kn[i, 2], kd[i]), []).append(i)
    pairs = {}
    for key, own in groups.items():
        nxt = groups.get((key[0], key[1], key[2], key[3] + 1), [])
        idx = own + nxt
        if len(idx) < 2: continue
        if len(set(owner[idx])) < 2: continue                      # one piece only: layer 1's business
        nown = len(own)
        nrm = nc[own[0]]
        u = np.cross(nrm, [0, 0, 1] if abs(nrm[2]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u)
        v = np.cross(nrm, u)
        P = lambda X: np.stack([X @ u, X @ v], axis=1)
        pa, pb, pc = P(A[idx]), P(B[idx]), P(C[idx])
        mn = np.minimum(np.minimum(pa, pb), pc); mx = np.maximum(np.maximum(pa, pb), pc)
        order = np.argsort(mn[:, 0]); m = len(idx)
        for oi in range(m):
            i = order[oi]
            for oj in range(oi + 1, m):
                j = order[oj]
                if mn[j, 0] >= mx[i, 0]: break
                if i >= nown and j >= nown: continue
                ti, tj = idx[i], idx[j]
                if owner[ti] == owner[tj]: continue
                if mn[j, 1] >= mx[i, 1] or mn[i, 1] >= mx[j, 1] or mx[j, 0] <= mn[i, 0]: continue
                ov = overlap([tuple(pa[i]), tuple(pb[i]), tuple(pc[i])], [tuple(pa[j]), tuple(pb[j]), tuple(pc[j])])
                if ov < MIN_OV: continue
                oa, ob_ = obs[owner[ti]].name, obs[owner[tj]].name
                if oa > ob_: oa, ob_, ma, mb = ob_, oa, mats[tj], mats[ti]
                else: ma, mb = mats[ti], mats[tj]
                k = (oa, ob_)
                acc = pairs.get(k)
                w = (A[ti] + B[ti] + C[ti] + A[tj] + B[tj] + C[tj]) / 6
                same = float(np.dot(nf[ti], nf[tj])) > 0
                sa, ta = (ov, 0.0) if same else (0.0, ov)
                pairs[k] = (ov, 1, w, nrm, ma, mb, sa, ta) if acc is None else (acc[0] + ov, acc[1] + 1, acc[2], acc[3], acc[4], acc[5], acc[6] + sa, acc[7] + ta)
    rows = []
    for (oa, ob_), (ar, cnt, w, nrm, ma, mb, sa, ta) in pairs.items():
        rows.append(f"{col.name[7:]},{master(oa)},{master(ob_)},{ma},{mb},{ar:.4f},{cnt},{w[0]:.2f} {w[1]:.2f} {w[2]:.2f},{nrm[0]:.2f} {nrm[1]:.2f} {nrm[2]:.2f},{oa},{ob_},{sa:.4f},{ta:.4f}")
    return rows


t0 = time.time()
sc = bpy.data.scenes["VKX_Structures"]
with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
    dg = bpy.context.evaluated_depsgraph_get()
lines = ["structure,pieceA,pieceB,matA,matB,area_m2,pairs,where,normal,objA,objB,same_facing_m2,touching_m2"]
cols = [c for c in bpy.data.collections if c.name.startswith("VKX_ST_") and (not ONLY or ONLY in c.name)]
print(f"{len(cols)} structures", flush=True)
for c in sorted(cols, key=lambda c: c.name):
    try:
        lines += scan_structure(c, dg)
    except Exception as e:
        lines.append(f"{c.name},ERROR,{e},,,0,0,,,,")
    print(f"{c.name}: {time.time() - t0:.0f}s", flush=True)
    with open(out, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
print(f"done: {len(cols)} structures, {len(lines) - 1} lines, {time.time() - t0:.0f}s", flush=True)
