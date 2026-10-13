# Which material loses visible surface when backface culling goes on (the z-fighting fix A, 2026-10-13). Background
# Blender, nothing saved. For the pieces cull_render_diff.py flagged (share >= 1%), every material gets a flat ID colour
# (Workbench, colour type Material, flat light, Standard view transform) and each piece is rendered from the same four
# views with culling off and on. A pixel that shows material X with culling off and anything else (or nothing) with it
# on is a pixel X loses. Writes <dir>/ids.csv: material, piece, lost pixels, the piece's pixels.
#   blender -b medievalDiorama.blend --python cull_render_ids.py -- <dir with diff.csv>
import bpy, sys, os, math, csv
import numpy as np
from mathutils import Vector

d = sys.argv[sys.argv.index("--") + 1]
flag = [r["piece"] for r in csv.DictReader(open(os.path.join(d, "diff.csv"), encoding="utf-8")) if float(r["share"]) >= 0.01]

# the palette: 6 sRGB levels per channel (216 ids); the material's viewport colour is that level in linear
LEV = [0, 51, 102, 153, 204, 255]
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
used = set()
for name in flag:
    ob = bpy.data.objects.get(name)
    if ob is not None: used |= {s.material.name for s in ob.material_slots if s.material}
for m in bpy.data.materials: m.diffuse_color = (0, 0, 0, 1)      # id 0: not one of these pieces' materials
mats = sorted(used)
print(len(mats), "materials on the flagged pieces", flush=True)
pal = {(0, 0, 0): "(none)"}
for i, mn in enumerate(mats):
    if i >= 214: print("palette full at", mn); break
    r, g, b = LEV[(i + 1) // 36 % 6], LEV[(i + 1) // 6 % 6], LEV[(i + 1) % 6]
    bpy.data.materials[mn].diffuse_color = (lin(r), lin(g), lin(b), 1.0)
    pal[(r // 51, g // 51, b // 51)] = mn

sc = bpy.data.scenes.new("ZF_CullIds")
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x = sc.render.resolution_y = 128
sc.render.film_transparent = True
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.display.render_aa = "OFF"
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
sc.view_settings.exposure = 0; sc.view_settings.gamma = 1
sh = sc.display.shading
sh.light = "FLAT"; sh.color_type = "MATERIAL"
sh.show_object_outline = False; sh.show_cavity = False; sh.show_shadows = False; sh.show_specular_highlight = False
cam_data = bpy.data.cameras.new("ZF_CamI"); cam_data.lens_unit = "FOV"; cam_data.angle = math.radians(30)
cam = bpy.data.objects.new("ZF_CamI", cam_data); sc.collection.objects.link(cam); sc.camera = cam
tmp = os.path.join(d, "_id.png")


def render_ids():
    bpy.ops.render.render(write_still=True, scene=sc.name)
    im = bpy.data.images.load(tmp)
    a = np.array(im.pixels[:], np.float32).reshape(im.size[1], im.size[0], 4)
    bpy.data.images.remove(im)
    q = np.round(a[..., :3] * 5).astype(np.int64)
    ids = q[..., 0] * 36 + q[..., 1] * 6 + q[..., 2]
    ids[a[..., 3] < 0.5] = -1
    return ids


lost = {}
sc.render.filepath = tmp
for k, name in enumerate(flag):
    ob = bpy.data.objects.get(name)
    if ob is None: continue
    inst = bpy.data.objects.new("ZFI_" + name, ob.data); sc.collection.objects.link(inst)
    try:
        corners = [Vector(c) for c in ob.bound_box]
        mid = sum(corners, Vector()) / 8
        rad = max((c - mid).length for c in corners) + 0.05
        dist = rad / math.sin(math.radians(15)) * 1.05
        for az in (0, 90, 180, 270):
            p = math.radians(50)
            dv = Vector((math.cos(math.radians(az)) * math.cos(p), math.sin(math.radians(az)) * math.cos(p), math.sin(p)))
            cam.location = mid + dv * dist
            cam.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler()
            sh.show_backface_culling = False; off = render_ids()
            sh.show_backface_culling = True; on = render_ids()
            gone = (off >= 0) & (off != on)
            cover = int((off >= 0).sum())
            vals, counts = np.unique(off[gone], return_counts=True)
            for v, c in zip(vals, counts):
                key = (int(v) // 36, int(v) // 6 % 6, int(v) % 6)
                mn = pal.get(key, f"?{key}")
                acc = lost.get((mn, name), (0, 0))
                lost[(mn, name)] = (acc[0] + int(c), acc[1] + cover)
    finally:
        bpy.data.objects.remove(inst)
    if k % 25 == 0: print(f"{k}/{len(flag)}", flush=True)

with open(os.path.join(d, "ids.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["material", "piece", "lost_px", "piece_px"])
    for (mn, name), (c, cov) in sorted(lost.items(), key=lambda kv: -kv[1][0]): w.writerow([mn, name, c, cov])
print("done", flush=True)
