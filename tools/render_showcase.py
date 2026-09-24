# Renders the README gallery (docs/images/*.jpg) from the current state of the VillageKit scene.
# Run inside Blender after rebuilding the valley and the terrain demo:
#   exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\render_showcase.py", encoding="utf8").read())
#   render_showcase()                  # all views, or render_showcase(["tavern"]) for some
import bpy, os
VK_ROOT = VK_ROOT_OVERRIDE if "VK_ROOT_OVERRIDE" in globals() else r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
SHOWCASE = {   # name: (camera, target, lens, resolution)   (valley at world 1500,0; terrain demo at 1200,0)
    "valley_aerial":  ((1608, -95, 150), (1608, 78, 0),    28, (1600, 1000)),
    "market_plaza":   ((1644, 76, 28),   (1624, 100, 1),   30, (1600, 900)),
    "tavern":         ((1622, 92, 11),   (1604, 99, 5),    30, (1600, 900)),
    "blacksmith":     ((1625, 80, 7),    (1635, 84, 2.5),  32, (1600, 900)),
    "river_mill":     ((1560, 18, 12),   (1545, 45, 2),    30, (1600, 900)),
    "festival_green": ((1659, 66, 40),   (1659, 98, 1),    32, (1600, 900)),
    "quarry_cliffs":  ((1545, 70, 26),   (1545, 98, 5),    30, (1600, 900)),
    "terrain_demo":   ((1290, -30, 55),  (1245, 38, 0),    30, (1600, 900)),
}

def render_showcase(names=None, quality=85):
    """render each view to renders/showcase/readme/<name>.png, then save docs/images/<name>.jpg"""
    exec(bpy.data.texts["vk_render"].as_string(), globals())
    src = os.path.join(VK_ROOT, "renders", "showcase", "readme"); dst = os.path.join(VK_ROOT, "docs", "images")
    os.makedirs(dst, exist_ok=True)
    sc = bpy.data.scenes["VillageKit"]; st = sc.render.image_settings; vs = sc.view_settings
    out = []
    for n in names or SHOWCASE:
        cam, tgt, lens, res = SHOWCASE[n]
        png = shot(n, cam, tgt, lens=lens, res=res, outdir=src)
        # PNG -> JPEG with an identity view transform (the PNG already has the scene's AgX look baked in)
        old = (st.file_format, st.quality, st.color_mode, vs.view_transform, vs.look, vs.exposure, vs.gamma)
        try:
            st.file_format = "JPEG"; st.quality = quality; st.color_mode = "RGB"
            vs.view_transform = "Standard"; vs.look = "None"; vs.exposure = 0.0; vs.gamma = 1.0
            im = bpy.data.images.load(png, check_existing=False)
            im.save_render(os.path.join(dst, n + ".jpg"), scene=sc); bpy.data.images.remove(im)
        finally:
            st.file_format, st.quality, st.color_mode, vs.view_transform, vs.look, vs.exposure, vs.gamma = old
        out.append(os.path.join(dst, n + ".jpg"))
    return out
