"""The slum pieces (vk_mod_slums), headless: push the texts, rebuild the pieces, lay out the review scene SLM_Review
(the four shacks + every piece in a row), render the review shots to renders/slums/, save the .blend.

    blender.exe -b blender/medievalDiorama.blend --python tools/slums_run.py -- [build] [scene] [shots] [save]
"""
import bpy, sys, os, math, time
ROOT = r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
OUT = os.path.join(ROOT, "renders", "slums")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["build", "scene", "shots", "save"]
t0 = time.time()
exec(open(os.path.join(ROOT, "tools", "kit_sync.py"), encoding="utf8").read())
print("PUSH", push(["vk_kit", "vk_mod_slums", "vkx_export"]))
exec(bpy.data.texts["vk_kit"].as_string())
g = vk_kit_ns()
names = list(g["KIT_MODULE_SPECS"]["vk_mod_slums"])
if "build" in args:
    g["full_rebuild"](names=set(names))
    tris = {}
    for n in names:
        o = bpy.data.objects.get(n)
        tris[n] = sum(len(p.vertices) - 2 for p in o.data.polygons) if o else None
    print("TRIS", tris)

SC = "SLM_Review"
if "scene" in args:
    sc = bpy.data.scenes.get(SC) or bpy.data.scenes.new(SC)
    vk = bpy.data.scenes["VillageKit"]
    for o in list(sc.collection.all_objects):
        if o.name not in ("VK_Sun", "VK_Fill"): bpy.data.objects.remove(o)
    for c in list(sc.collection.children):
        sc.collection.children.unlink(c)
        if c.users == 0: bpy.data.collections.remove(c)
    for n in ("VK_Sun", "VK_Fill"):
        if n not in sc.collection.objects: sc.collection.objects.link(bpy.data.objects[n])
    sc.world = vk.world
    for a in ("view_transform", "look", "exposure", "gamma"): setattr(sc.view_settings, a, getattr(vk.view_settings, a))
    sc.render.engine = vk.render.engine
    coll = bpy.data.collections.new("SLM_Shacks"); sc.collection.children.link(coll)
    # ground
    bpy.ops.mesh.primitive_plane_add(size=1)
    gp = bpy.context.active_object
    for c in gp.users_collection: c.objects.unlink(gp)
    coll.objects.link(gp); gp.name = "SLM_Ground"; gp.scale = (80, 50, 1); gp.location = (14, 4, -0.01)
    gm = bpy.data.materials.get("SLM_GroundMat") or bpy.data.materials.new("SLM_GroundMat")
    gm.use_nodes = True
    bsdf = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.16, 0.13, 0.08, 1.0); bsdf.inputs["Roughness"].default_value = 1.0
    gp.data.materials.append(gm)
    # the four shacks (as the structures) and every piece in a row behind them
    for (x, kw) in ((0, dict(seed=1, walls="planks", roof="leanto")), (9, dict(seed=2, bays=2, walls="patched", roof="thatch")),
                    (19, dict(seed=3, walls="wattle", roof="sail")), (28, dict(seed=4, walls="patched", roof="leanto", stilts=1.8))):
        g["build_shack"](coll, (x, 0, 0), **kw)
    rows = [[n for n in names if "_Wall_" in n or n.endswith("Corner")],
            [n for n in names if "_Roof_" in n],
            [n for n in names if "Shack_Stilt" in n or "Walkway" in n or n.startswith("SM_VK_Slum_")]]
    ROW_SPAN = []
    for r_, row in enumerate(rows):
        x = -2.0; x_start = x
        for n in row:
            o = bpy.data.objects.get(n)
            if o is None: continue
            inst = bpy.data.objects.new(n + "_rev", o.data); coll.objects.link(inst)
            w = max(o.dimensions.x, 1.0)
            z = 2.6 if ("Stilt" in n or "Walkway" in n) else 0.0
            inst.location = (x + w / 2, 10.0 + 6.0 * r_ + 30.0 * r_, z)
            x += w + 1.0
        ROW_SPAN.append((x_start, x, 10.0 + 36.0 * r_))
    bpy.data.scenes[SC]["slm_rows"] = [list(v) for v in ROW_SPAN]
    print("SCENE", len(coll.objects), "objects")

if "shots" in args:
    exec(bpy.data.texts["vk_render"].as_string(), g)
    os.makedirs(OUT, exist_ok=True)
    g["shot"]("slm_shacks_34", (14, -21, 11), (14, 0.5, 1.4), lens=30, res=(1600, 900), scene=SC, outdir=OUT)
    g["shot"]("slm_shacks_low", (-6, -11, 3.2), (6, 0.5, 1.6), lens=35, res=(1600, 900), scene=SC, outdir=OUT)
    g["shot"]("slm_stilts", (36, -9, 4.0), (28, 0, 1.8), lens=35, res=(1600, 900), scene=SC, outdir=OUT)
    g["shot"]("slm_wattle_sail", (14.5, -7.5, 3.6), (19, 0, 1.6), lens=35, res=(1600, 900), scene=SC, outdir=OUT)
    for nm, (x0, x1, y) in zip(("walls", "roofs", "props"), bpy.data.scenes[SC]["slm_rows"]):
        xc = (x0 + x1) / 2; d = (x1 - x0) * 0.62
        g["shot"]("slm_pieces_" + nm, (xc, y - d, d * 0.42), (xc, y, 1.2), lens=35, res=(1800, 900), scene=SC, outdir=OUT)
    g["shot"]("slm_game_cam", (14, -30, 32), (14, 2, 0), lens=30, res=(1600, 900), scene=SC, outdir=OUT)

if "save" in args:
    bpy.ops.wm.save_mainfile()
    print("SAVED")
print("DONE %.0f s" % (time.time() - t0))
