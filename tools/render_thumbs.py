"""Render one thumbnail per kit piece for the catalogue (tools/pieces_catalogue.py builds PIECES.md and the sheets).

Run in a background Blender (it only adds and removes its own scene; nothing is saved):
  blender -b blender/medievalDiorama.blend --python tools/render_thumbs.py -- [force] [size=192] [SM_VK_Name ...]

Reads the package's Data/pieces.json for the piece list, renders each master's mesh from the front-left, a little
above (fronts face -Y), orthographic and framed to its bounds, on a transparent background, to renders/thumbs/<name>.png.
Existing thumbnails are kept unless `force` (or the piece is named). Writes renders/thumbs/_missing.json: pieces
without a mesh master in the .blend.
"""
import bpy, json, math, os, sys, time
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIECES = os.path.join(ROOT, "unity", "com.danielgruginski.medievalkit", "Data", "pieces.json")
OUT = os.path.join(ROOT, "renders", "thumbs")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
force = "force" in args
size = next((int(a[5:]) for a in args if a.startswith("size=")), 192)
named = [a for a in args if a.startswith("SM_")]
assert bpy.data.filepath.endswith("medievalDiorama.blend"), bpy.data.filepath
os.makedirs(OUT, exist_ok=True)

names = named or sorted(n for n in json.load(open(PIECES, encoding="utf8")) if not n.startswith("U_"))
VIEW = Vector((-0.55, -1.0, 0.62)).normalized()            # camera sits front-left, above, looking back along -VIEW

sc = bpy.data.scenes.new("__thumbs")
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try: sc.render.engine = eng; break
    except TypeError: pass
try: sc.eevee.taa_render_samples = 16
except AttributeError: pass
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = size
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "Standard"
sc.world = bpy.data.worlds[0] if bpy.data.worlds else None
cd = bpy.data.cameras.new("__thumbs_cam"); cd.type = "ORTHO"; cd.clip_start = 0.01; cd.clip_end = 1000
cam = bpy.data.objects.new("__thumbs_cam", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_euler = (-VIEW).to_track_quat("-Z", "Y").to_euler()
for nm, rot, en in (("__thumbs_key", (50, 0, -35), 3.2), ("__thumbs_fill", (65, 0, 150), 0.9)):
    ld = bpy.data.lights.new(nm, "SUN"); ld.energy = en; lo = bpy.data.objects.new(nm, ld)
    lo.rotation_euler = tuple(math.radians(a) for a in rot); sc.collection.objects.link(lo)
R = cam.rotation_euler.to_matrix(); cx, cy = R.col[0], R.col[1]

missing = []; done = 0; t0 = time.time()
for i, n in enumerate(names):
    path = os.path.join(OUT, n + ".png")
    if os.path.exists(path) and not force and n not in named: continue
    src = bpy.data.objects.get(n)
    if src is None or src.type != "MESH" or not src.data.vertices:
        missing.append(n); continue
    o = bpy.data.objects.new("__thumbs_piece", src.data); sc.collection.objects.link(o)
    cs = [Vector(c) for c in src.bound_box]
    ctr = sum(cs, Vector()) / 8
    xs = [(c - ctr).dot(cx) for c in cs]; ys = [(c - ctr).dot(cy) for c in cs]
    cd.ortho_scale = max(max(xs) - min(xs), max(ys) - min(ys), 0.05) * 1.08
    cam.location = ctr + VIEW * (max((c - ctr).length for c in cs) + 5.0)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    bpy.data.objects.remove(o, do_unlink=True); done += 1
    if done % 50 == 0: print(f"THUMBS {done} rendered, at {i + 1}/{len(names)}, {time.time() - t0:.0f} s", flush=True)

json.dump(sorted(missing), open(os.path.join(OUT, "_missing.json"), "w"), indent=1)
for ob in list(sc.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.scenes.remove(sc)
print(f"THUMBS DONE {done} rendered, {len(missing)} missing, {time.time() - t0:.0f} s", flush=True)
