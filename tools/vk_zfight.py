# ===================== VISIBLE Z-FIGHT CHECK (background Blender) =====================
# Same-facing faces of one piece in one plane (normals within 0.999, planes within 2 mm) that overlap by more than
# 0.2 cm2 AND can be seen: from 2 mm off the overlap some of 24 rays in its hemisphere escape 40 m (buried overlaps
# never show). Writes renders/zfight.json (piece -> overlaps, biggest first).
#   blender -b blender/medievalDiorama.blend --python tools/vk_zfight.py -- [rebuild] [demo] [save] [SM_... names] [@list.txt]
# With no names: the market, harbour, dock and quay pieces. "demo": also qy_demo's assembled quay chunk (overlaps
# between neighbouring tiles). Bottoms resting on / under the ground of land pieces still show here (no ground):
# read those as buried. Interior pieces (SM_VKI_*) rebuild through vki_rebuild; @file reads one name per line;
# out=<path> writes the report elsewhere; "sided" checks as the game's z-fight watch does (zfight_sided below);
# "closed" (with sided) covers wall pieces' open ends as a level does (a post or the next wall; ends=X: the planes
# x = +-X of any piece, the exterior modules' butt joints); "ground" adds the land at z -1 mm (buried bottoms
# hidden); the exterior check: sided closed ends=1.5 ground; "posts" checks each
# interior wall between its family's Mid posts (wall-post fights).
import bpy, os, sys, json, math, traceback
from mathutils import Vector
from mathutils.bvhtree import BVHTree
assert bpy.data.filepath.endswith("medievalDiorama.blend"), bpy.data.filepath
OUT = os.path.join(os.path.dirname(os.path.dirname(bpy.data.filepath)), "renders", "zfight.json")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = next((a[4:] for a in args if a.startswith("out=")), OUT)          # out=<path>: another report file
exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\kit_sync.py", encoding="utf8").read())
push()
gk = {}; exec(bpy.data.texts["vk_kit"].as_string(), gk); kit = gk["vk_kit_ns"]()

PREFIX = ("SM_VKT_Quay_", "SM_VK_Harbour_", "SM_VK_Jetty_", "SM_VK_Breakwater", "SM_VK_Ship_", "SM_VK_Boat_", "SM_VK_Cargo_",
          "SM_VK_Dock_", "SM_VK_MarketHall", "SM_VK_Prop_Monument", "SM_VK_Prop_WeighBeam", "SM_VK_Prop_Hurdle", "SM_VK_Prop_Pen",
          "SM_VK_Prop_CrierStand")
STALLS = ["SM_VK_MarketStall_" + t for t in ("Spicer", "Butcher", "Jeweller", "Armourer", "Apothecary", "Vintner", "Scribe")]
only = [a for a in args if a.startswith("SM_")]
for a in args:
    if a.startswith("@"): only += [l.strip() for l in open(a[1:], encoding="utf8") if l.strip().startswith("SM_")]
names = only or [o.name for o in bpy.data.objects if o.type == "MESH" and "_inst" not in o.name and (o.name.startswith(PREFIX) or o.name in STALLS)]

if "rebuild" in args:
    if any(n.startswith("SM_VKT_Quay_") for n in names): kit["tk_build_quays"]()
    vki = [n for n in names if n.startswith("SM_VKI_")]
    if vki:
        g0 = {}; exec(bpy.data.texts["vki_core"].as_string(), g0); ik = g0["vki_ns"]()
        for n in vki:
            try: ik["vki_rebuild"]([n])
            except Exception: print("REBUILD FAILED", n); traceback.print_exc()
    for n in names:
        if n.startswith(("SM_VKT_", "SM_VKI_")): continue
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

def mname(me, pi):
    mi = me.polygons[pi].material_index; m = me.materials[mi] if mi < len(me.materials) else None
    return m.name if m else mi

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
                                    mats=[mname(me, ta[0]), mname(me, tb[0])]))
    out.sort(key=lambda e: -e["area"])
    return out

# "sided": the game's z-fight watch (MedievalSetting ZFightWatch) instead -- faces in one plane facing either way
# (|dot| > 0.995, planes < 1 mm apart; "fight" under 0.2 mm), seen from each side where both draw: a face draws its
# back too when its material is two-sided in the export (vkx_double_sided: M_VKI_* and the sheet materials). Catches
# what one-sided thinking misses: a cap's inside bottom on a wall body's top, seen through the open wall end.
import ast
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "export", "vkx_export.py"), encoding="utf8").read()
_ns = {}
for _nd in ast.parse(_src).body:
    if (isinstance(_nd, ast.Assign) and any(getattr(t, "id", "").startswith("VKX_TWO_SIDED") for t in _nd.targets)) or \
       (isinstance(_nd, ast.FunctionDef) and _nd.name == "vkx_double_sided"):
        exec(compile(ast.Module([_nd], []), "vkx_export", "exec"), _ns)
two_sided = _ns["vkx_double_sided"]
DIRS96 = []
for i in range(96):
    z = 0.08 + 0.92 * (i % 8) / 7.0; a = i * 2.39996
    r = math.sqrt(max(0.0, 1 - z * z)); DIRS96.append(Vector((r * math.cos(a), r * math.sin(a), z)))

def seen_from(bvh, pts, s, off=0.002):
    """a ray escapes 40 m, and so do two copies tilted 0.6 deg (one ray in thousands slips through the shared edge of
    two triangles of a closed box; a real opening lets its neighbours through too). Rays start `off` from the plane:
    just past both faces (2 mm off put points near a sloping occluder's edge outside it)"""
    M = s.to_track_quat("Z", "Y").to_matrix()
    for p in pts:
        o = p + s * off
        for d0 in DIRS96:
            d = M @ d0
            if bvh.ray_cast(o, d, 40.0)[0] is not None: continue
            a = d.orthogonal().normalized(); b = d.cross(a)
            if all(bvh.ray_cast(o, (d + w * 0.0105).normalized(), 40.0)[0] is None for w in (a, b)): return True
    return False

END_X = next((float(a[5:]) for a in args if a.startswith("ends=")), None)   # ends=1.5: exterior modules' planes

def end_blockers(o, co, polys):
    """"closed": a wall's open ends (vki_open_wall_ends) as a level has them -- covered by a post or the next wall --
    as a quad 1 mm outside each end over the bounding box of the piece's vertices in that end plane. ends=X: the
    planes x = +-X of any piece instead (the exterior's 3 m modules butt their neighbours there)"""
    L = o.get("vki_len")
    if END_X is not None: planes = ((-END_X, -1.0), (END_X, 1.0))
    elif o.get("vki_class") != "wall" or not L: return
    else: planes = ((0.0, -1.0), (float(L), 1.0))
    for xe, sg in planes:
        e = [p for p in co if abs(p.x - xe) < 1e-4]
        if not e: continue
        y0, y1 = min(p.y for p in e), max(p.y for p in e); z0, z1 = min(p.z for p in e), max(p.z for p in e)
        x = xe + sg * 1e-3; i = len(co)            # 1 mm out: past the rays' 0.3 mm start off a face in the plane
        co += [Vector((x, y0, z0)), Vector((x, y1, z0)), Vector((x, y1, z1)), Vector((x, y0, z1))]
        polys.append((i, i + 1, i + 2, i + 3))

def zfight_sided(o, dist=1e-3, fight=2e-4, dot=0.995, min_area=2e-5):
    me = o.data; me.calc_loop_triangles()
    co = [Vector(v.co) for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons]
    bco = list(co)
    if "closed" in args: end_blockers(o, bco, polys)
    if "ground" in args:                    # ground: the land at z 0 (bottoms resting on it are buried)
        xs = [p.x for p in co] or [0.0]; ys = [p.y for p in co] or [0.0]; i = len(bco)
        bco += [Vector((min(xs) - 1, min(ys) - 1, -1e-3)), Vector((max(xs) + 1, min(ys) - 1, -1e-3)),
                Vector((max(xs) + 1, max(ys) + 1, -1e-3)), Vector((min(xs) - 1, max(ys) + 1, -1e-3))]
        polys.append((i, i + 1, i + 2, i + 3))
    bvh = BVHTree.FromPolygons(bco, polys)
    ts = [two_sided(m.name) if m else True for m in me.materials]
    tris = []
    for t in me.loop_triangles:
        a, b, c = (co[i] for i in t.vertices); n = (b - a).cross(c - a)
        if n.length < 1e-12: continue
        n.normalize()
        ax = max(range(3), key=lambda i: abs(n[i]))
        cn = n if n[ax] > 0 else -n                          # canonical: its largest component positive
        tris.append((t.polygon_index, (a, b, c), n, cn, cn.dot(a)))
    buckets = {}
    for tr in tris:
        cn, d = tr[3], tr[4]
        buckets.setdefault((round(cn.x, 1), round(cn.y, 1), round(cn.z, 1), math.floor(d / 0.002)), []).append(tr)
    seen = set(); out = []
    for key, lst in buckets.items():
        cand = list(lst) + buckets.get(key[:3] + (key[3] + 1,), [])
        if len({c_[0] for c_ in cand}) < 2: continue
        n0 = lst[0][3]; u = Vector((0, 0, 1)) if abs(n0.z) < 0.9 else Vector((1, 0, 0))
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
                    if ta[0] == tb[0] or abs(ta[3].dot(tb[3])) <= dot or abs(ta[4] - tb[4]) >= 0.004: continue
                    sk = (min(ta[0], tb[0]), max(ta[0], tb[0]))
                    if sk in seen: continue
                    C = clip(Pa, Pb)
                    if len(C) < 3 or abs(area2(C)) < min_area: continue
                    seen.add(sk)
                    cx = sum(p[0] for p in C) / len(C); cy = sum(p[1] for p in C) / len(C)
                    pts = [Vector((cx, cy))] + [Vector((cx + 0.7 * (p[0] - cx), cy + 0.7 * (p[1] - cy))) for p in C]
                    on_a = lambda q: (lambda w: w + n0 * ((ta[4] - ta[3].dot(w)) / ta[3].dot(n0)))(u * q.x + v * q.y)
                    pts = [on_a(q) for q in pts]             # on ta's own plane (n0 is the bucket's first triangle's)
                    ma, mb = me.polygons[ta[0]].material_index, me.polygons[tb[0]].material_index
                    pc = pts[0]                              # the gap where they overlap (tilted planes part away
                    gb = tb[3].dot(pc) - tb[4]               # from the origin: offsets there say nothing)
                    gap = abs(gb)
                    if gap >= dist: continue
                    sides = []
                    for s in (n0, -n0):                      # both draw on side s: front-facing, or two-sided
                        p0 = [p - n0 * min(gb, 0.0) if s is n0 else p - n0 * max(gb, 0.0) for p in pts]
                        if (ta[2].dot(s) > 0 or ts[ma]) and (tb[2].dot(s) > 0 or ts[mb]) and seen_from(bvh, p0, s, 3e-4):
                            sides.append("+" if s is n0 else "-")
                    if not sides: continue
                    out.append(dict(area=round(abs(area2(C)), 5), at=[round(x, 3) for x in pts[0]],
                                    n=[round(x, 2) for x in n0], side="".join(sides),
                                    facing="same" if ta[2].dot(tb[2]) > 0 else "opposite",
                                    kind="fight" if gap < fight else "near", gap=round(gap, 5), faces=list(sk),
                                    verts=[[[round(c, 4) for c in co[i]] for i in me.polygons[fi].vertices][:8] for fi in sk],
                                    mats=[mname(me, ta[0]), mname(me, tb[0])]))
    out.sort(key=lambda e: -e["area"])
    return out

import bmesh

def with_posts(o):
    """"posts": an interior wall stood between its family's Mid posts at both nodes, as a level stands it, in one
    temporary mesh -- fights between wall and post show (a breach's intact end in the post's face, HANDOFF 151)"""
    L, h = o.get("vki_len"), o.get("vki_height") or o.name.rsplit("_", 1)[-1]
    fam = o.get("vki_family")
    post = bpy.data.objects.get("SM_VKI_Post_%s_Mid_%s" % (fam, h))
    if o.get("vki_class") != "wall" or not L or post is None: return None
    me = bpy.data.meshes.new("__zf_posts"); mats = list(o.data.materials)
    bm = bmesh.new(); bm.from_mesh(o.data)
    for x in (0.0, float(L)):
        t = bmesh.new(); t.from_mesh(post.data)
        bmesh.ops.translate(t, vec=(x, 0.0, 0.0), verts=t.verts)
        for f in t.faces:
            m = post.data.materials[f.material_index] if f.material_index < len(post.data.materials) else None
            if m not in mats: mats.append(m)
            f.material_index = mats.index(m)
        tm = bpy.data.meshes.new("__zf_post"); t.to_mesh(tm); t.free()
        bm.from_mesh(tm); bpy.data.meshes.remove(tm)
    bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    tmp = bpy.data.objects.new("__zf_posts", me)
    for k_ in ("vki_class", "vki_len"): tmp[k_] = o[k_]
    return tmp

if "sided" in args: zfight = zfight_sided
res = {}
for n in sorted(names):
    if "posts" in args:
        tmp = with_posts(bpy.data.objects[n])
        if tmp is None: res[n] = "ERR no Mid post for this wall"; continue
        try: res[n + "+posts"] = zfight(tmp)
        except Exception as e: res[n + "+posts"] = "ERR " + repr(e); traceback.print_exc()
        me_ = tmp.data; bpy.data.objects.remove(tmp); bpy.data.meshes.remove(me_)
        continue
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
