# Backface-culling check, by eye (the z-fighting fix A, 2026-10-13). Background Blender, nothing saved: every master
# piece rendered with Workbench (textures, flat light) from four sides at the game camera's 50-degree pitch, once with
# backface culling off (as the game draws now) and once on, at 128 px. A piece whose two renders differ shows back faces
# from outside -- an open sheet or a shell facing inward -- that would vanish if culled. Writes the PNG pairs to
# <out>/off_<piece>_<view>.png and on_..., for cull_render_diff.py.
#   blender -b medievalDiorama.blend --python cull_render_check.py -- <out dir> [name filter]
import bpy, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
OUT = args[0]
ONLY = args[1] if len(args) > 1 else ""
os.makedirs(OUT, exist_ok=True)
COLLS = ["VK_Pieces", "VKI_Pieces"]

sc = bpy.data.scenes.new("ZF_CullCheck")
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x = sc.render.resolution_y = 128
sc.render.resolution_percentage = 100
sc.render.film_transparent = True
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.display.render_aa = "OFF"
sh = sc.display.shading
sh.light = "FLAT"
sh.color_type = "TEXTURE"
sh.show_object_outline = False
sh.show_cavity = False
sh.show_shadows = False
cam_data = bpy.data.cameras.new("ZF_Cam")
cam_data.lens_unit = "FOV"; cam_data.angle = math.radians(30)
cam = bpy.data.objects.new("ZF_Cam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam

pieces = []
for cname in COLLS:
    col = bpy.data.collections.get(cname)
    if col is None: continue
    for ob in sorted(col.all_objects, key=lambda o: o.name):
        if ob.type == "MESH" and (not ONLY or ONLY in ob.name):
            pieces.append(ob)
print(f"{len(pieces)} pieces", flush=True)

for k, ob in enumerate(pieces):
    inst = bpy.data.objects.new("ZF_" + ob.name, ob.data)
    sc.collection.objects.link(inst)
    try:
        corners = [Vector(c) for c in ob.bound_box]
        mid = sum(corners, Vector()) / 8
        rad = max((c - mid).length for c in corners) + 0.05
        dist = rad / math.sin(math.radians(15)) * 1.05
        for vi, az in enumerate((0, 90, 180, 270)):
            pitch = math.radians(50)
            d = Vector((math.cos(math.radians(az)) * math.cos(pitch), math.sin(math.radians(az)) * math.cos(pitch), math.sin(pitch)))
            cam.location = mid + d * dist
            cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            for mode in ("off", "on"):
                sh.show_backface_culling = mode == "on"
                sc.render.filepath = os.path.join(OUT, f"{mode}_{ob.name}_{vi}.png")
                bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        bpy.data.objects.remove(inst)
    if k % 25 == 0: print(f"{k}/{len(pieces)}", flush=True)
print("done", flush=True)
