# Which kit materials can be drawn one-sided (backface culling) -- the z-fighting fix A, 2026-10-13. Background Blender,
# read-only. For every material, over every master piece (exterior, interior, nature): its area on closed shells (mesh
# islands with no open edge: safe to cull), on open sheets (islands with open edges: a card, an awning, a single-sided
# surface; culling hides their back), and on closed shells that face inward (negative volume: culling would hide them
# from outside). One CSV line per material, plus the pieces with the most open-sheet area for that material.
#   blender -b medievalDiorama.blend --python cull_scan_materials.py -- out.csv
import bpy, bmesh, sys, collections

out = sys.argv[sys.argv.index("--") + 1]
COLLS = ["VK_Pieces", "VKI_Pieces", "VK_NaturePieces"]

closed = collections.defaultdict(float)
opened = collections.defaultdict(float)
inward = collections.defaultdict(float)
users = collections.defaultdict(lambda: collections.defaultdict(float))
seen = set()
for cname in COLLS:
    col = bpy.data.collections.get(cname)
    if col is None:
        print("no collection", cname); continue
    for ob in col.all_objects:
        if ob.type != "MESH" or ob.data.name in seen: continue
        seen.add(ob.data.name)
        slots = [s.material.name if s.material else "-" for s in ob.material_slots]
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bm.faces.ensure_lookup_table()
        left = set(range(len(bm.faces)))
        while left:
            f0 = bm.faces[left.pop()]
            isl = [f0]; stack = [f0]; open_edge = False
            while stack:
                f = stack.pop()
                for e in f.edges:
                    if len(e.link_faces) == 1: open_edge = True
                    for g in e.link_faces:
                        if g.index in left:
                            left.discard(g.index); isl.append(g); stack.append(g)
            vol = 0.0
            if not open_edge:
                for f in isl:
                    vs = [v.co for v in f.verts]
                    for i in range(1, len(vs) - 1):
                        vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6.0
            for f in isl:
                m = slots[f.material_index] if f.material_index < len(slots) else "-"
                a = f.calc_area()
                if open_edge:
                    opened[m] += a; users[m][ob.name] += a
                elif vol < 0:
                    inward[m] += a; users[m]["(inward) " + ob.name] += a
                else:
                    closed[m] += a
        bm.free()

mats = sorted(set(closed) | set(opened) | set(inward), key=lambda m: -(closed[m] + opened[m] + inward[m]))
with open(out, "w", encoding="utf-8") as fh:
    fh.write("material,closed_m2,open_m2,inward_m2,open_share,top_open_pieces\n")
    for m in mats:
        tot = closed[m] + opened[m] + inward[m]
        top = sorted(users[m].items(), key=lambda x: -x[1])[:4]
        fh.write(f"{m},{closed[m]:.2f},{opened[m]:.2f},{inward[m]:.2f},{(opened[m] + inward[m]) / tot if tot else 0:.3f},"
                 + " | ".join(f"{p} {a:.2f}" for p, a in top) + "\n")
print(f"done: {len(mats)} materials over {len(seen)} meshes", flush=True)
