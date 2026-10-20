# ===================== VISIBLE Z-FIGHT CHECK (background Blender) =====================
# Same-facing faces of one piece in one plane (normals within 0.999, planes within 2 mm) that overlap by more than
# 0.2 cm2 AND can be seen: from 2 mm off the overlap some of 24 rays in its hemisphere escape 40 m (buried overlaps
# never show). Writes renders/zfight.json (piece -> overlaps, biggest first).
#   blender -b blender/medievalDiorama.blend --python tools/vk_zfight.py -- [rebuild] [demo] [save] [SM_... names]
# With no names: the market, harbour, dock and quay pieces. "demo": also qy_demo's assembled quay chunk (overlaps
# between neighbouring tiles). Bottoms resting on / under the ground of land pieces still show here (no ground):
# read those as buried.
import bpy, os, sys, json, math, traceback
from mathutils import Vector
from mathutils.bvhtree import BVHTree
assert bpy.data.filepath.endswith("medievalDiorama.blend"), bpy.data.filepath
OUT = os.path.join(os.path.dirname(os.path.dirname(bpy.data.filepath)), "renders", "zfight.json")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\kit_sync.py", encoding="utf8").read())
push()
gk = {}; exec(bpy.data.texts["vk_kit"].as_string(), gk); kit = gk["vk_kit_ns"]()

PREFIX = ("SM_VKT_Quay_", "SM_VK_Harbour_", "SM_VK_Jetty_", "SM_VK_Breakwater", "SM_VK_Ship_", "SM_VK_Boat_", "SM_VK_Cargo_",
          "SM_VK_Dock_", "SM_VK_MarketHall", "SM_VK_Prop_Monument", "SM_VK_Prop_WeighBeam", "SM_VK_Prop_Hurdle", "SM_VK_Prop_Pen",
          "SM_VK_Prop_CrierStand")
STALLS = ["SM_VK_MarketStall_" + t for t in ("Spicer", "Butcher", "Jeweller", "Armourer", "Apothecary", "Vintner", "Scribe")]
only = [a for a in args if a.startswith("SM_")]
names = only or [o.name for o in bpy.data.objects if o.type == "MESH" and "_inst" not in o.name and (o.name.startswith(PREFIX) or o.name in STALLS)]

if "rebuild" in args:
    if any(n.startswith("SM_VKT_Quay_") for n in names): kit["tk_build_quays"]()
    for n in names:
        if n.startswith("SM_VKT_"): continue
        try: kit["full_rebuild"]([n])
        except Exception: print("REBUILD FAILED", n); traceback.print_exc()

def clip(P, Q):
    out = P
    for i in range(len(Q)):
        a, b = Q[i], Q[(i + 1) % len(Q)]
        inp, out = out, []
        if not inp: break
        side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        for j in range(len(inp)):
            cur, prv = inp[j], inp[j - 1]; sc_, sp_ = side(cur), side(prv)
            if sc_ >= 0:
                if sp_ < 0:
                    t = sp_ / (sp_ - sc_); out.append((prv[0] + t * (cur[0] - prv[0]), prv[1] + t * (cur[1] - prv[1])))
                out.append(cur)
            elif sp_ >= 0:
                t = sp_ / (sp_ - sc_); out.append((prv[0] + t * (cur[0] - prv[0]), prv[1] + t * (cur[1] - prv[1])))
    return out
def area2(P): return sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P))) / 2

DIRS = []
for i in range(24):                                  # a fixed spread of view directions
    z = 0.15 + 0.85 * (i % 6) / 5.0; a = i * 2.39996
    r = math.sqrt(max(0.0, 1 - z * z)); DIRS.append(Vector((r * math.cos(a), r * math.sin(a), z)))

def visible(bvh, p, n):
    """can a camera see the point p (2 mm off its face along n)? some ray in n's hemisphere escapes 40 m"""
    o = p + n * 0.002
    for d0 in DIRS:
        q = n.to_track_quat("Z", "Y").to_matrix() @ d0
        hit = bvh.ray_cast(o, q, 40.0)
        if hit[0] is None: return True
    return False

def zfight(o, dist=2e-3, dot=0.999, min_area=2e-5):
    me = o.data; me.calc_loop_triangles()
    co = [Vector(v.co) for v in me.vertices]
    bvh = BVHTree.FromPolygons(co, [tuple(p.vertices) for p in me.polygons])
    tris = []
    for t in me.loop_triangles:
        a, b, c = (co[i] for i in t.vertices); n = (b - a).cross(c - a)
        if n.length < 1e-12: continue
        n.normalize(); tris.append((t.polygon_index, (a, b, c), n, n.dot(a)))
    buckets = {}
    for tr in tris:
        n, d = tr[2], tr[3]
        buckets.setdefault((round(n.x, 2), round(n.y, 2), round(n.z, 2), round(d / 0.004)), []).append(tr)
    seen = set(); out = []
    for key, lst in buckets.items():
        cand = list(lst) + buckets.get(key[:3] + (key[3] + 1,), [])
        if len({c_[0] for c_ in cand}) < 2: continue
        n0 = lst[0][2]; u = Vector((0, 0, 1)) if abs(n0.z) < 0.9 else Vector((1, 0, 0))
        u = (u - n0 * u.dot(n0)).normalized(); v = n0.cross(u)
        proj = []; grid = {}
        for tr in cand:
            P = [(p.dot(u), p.dot(v)) for p in tr[1]]
            if area2(P) < 0: P = P[::-1]
            proj.append((tr, P)); k_ = len(proj) - 1
            xs = [p[0] for p in P]; ys = [p[1] for p in P]
            for gx in range(math.floor(min(xs) / 0.5), math.floor(max(xs) / 0.5) + 1):
                for gy in range(math.floor(min(ys) / 0.5), math.floor(max(ys) / 0.5) + 1):
                    grid.setdefault((gx, gy), []).append(k_)
        for cell in grid.values():
            for ii in range(len(cell)):
                for jj in range(ii + 1, len(cell)):
                    (ta, Pa), (tb, Pb) = proj[cell[ii]], proj[cell[jj]]
                    if ta[0] == tb[0] or ta[2].dot(tb[2]) <= dot or abs(ta[3] - tb[3]) >= dist: continue
                    sk = (min(ta[0], tb[0]), max(ta[0], tb[0]))
                    if sk in seen: continue
                    C = clip(Pa, Pb)
                    if len(C) < 3 or abs(area2(C)) < min_area: continue
                    seen.add(sk)
                    cx = sum(p[0] for p in C) / len(C); cy = sum(p[1] for p in C) / len(C)
                    pw = u * cx + v * cy + ta[2] * ta[3]
                    if not visible(bvh, pw, ta[2]): continue
                    out.append(dict(area=round(abs(area2(C)), 5), at=[round(x, 3) for x in pw], n=[round(x, 2) for x in ta[2]],
                                    gap=round(abs(ta[3] - tb[3]), 5), faces=list(sk),
                                    mats=[me.polygons[ta[0]].material_index, me.polygons[tb[0]].material_index]))
    out.sort(key=lambda e: -e["area"])
    return out

res = {}
for n in sorted(names):
    try: res[n] = zfight(bpy.data.objects[n])
    except Exception as e: res[n] = "ERR " + repr(e); traceback.print_exc()
if "demo" in args:
    c = bpy.data.collections.new("__zf_demo"); bpy.context.scene.collection.children.link(c)
    made = kit["qy_demo"](coll=c)
    res["QYDEMO_Chunk"] = zfight([o for o in made if o.name.startswith("QYDEMO_Chunk")][0])
    for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(c)
json.dump(res, open(OUT, "w"), indent=1)
print("WROTE", len(res))
if "save" in args:
    bpy.ops.wm.save_mainfile(); print("SAVED")
