# ===================== the siege catapult unit, headless (src/units/vku_siege_catapult.py) =====================
# Stage 1, the parts from the kit's builder (opens the kit's .blend, never saves it):
#   blender -b blender/medievalDiorama.blend --python tools/unit_catapult_run.py -- parts
# Stage 2, in the unit's own .blend (written by stage 1):
#   blender -b blender/vku_siege_catapult.blend --python tools/unit_catapult_run.py -- rig clips check renders export save
# Steps: rig (armature + skin), clips (all actions), check (lowest vertex per clip, wheel slip / Motion trace, part
# overlaps), renders (close-ups, frame strips, game camera into renders/units/siege_catapult), export (FBX + clip FBXs +
# JSON into the package's Art/Units/SiegeCatapult), save (the unit's .blend).
# The package's Art/Units/SiegeCatapult is LIVE (the open Unity editor imports what lands there): to export somewhere
# else, pass `export_dir=<folder>` (or set the env var VKU_EXPORT_DIR); `export` and `reimport` then use that folder,
# laid out like the package's (<folder>/VKU_SiegeCatapult.fbx, <folder>/Anims/...), to be copied in by hand, e.g.
#   ... --python tools/unit_catapult_run.py -- rig clips check export reimport export_dir=renders/units/siege_catapult_export
import bpy, sys, os, json, subprocess, traceback

ROOT = r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
sys.path.insert(0, os.path.join(ROOT, "src", "units"))
import vku_siege_catapult as U

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = {}


def kit_ns():
    exec(open(os.path.join(ROOT, "tools", "kit_sync.py"), encoding="utf8").read(), globals())
    push()                                                       # noqa: F821 (kit_sync's) -- in memory only
    g0 = {}
    exec(bpy.data.texts["vki_core"].as_string(), g0)
    return g0["vki_ns"]()


try:
    if "parts" in args:
        assert bpy.data.filepath.endswith("medievalDiorama.blend"), bpy.data.filepath
        bpy.context.preferences.system.vbo_time_out = 0
        g = kit_ns()
        # the static pieces must not move: hash them built from HEAD's vki_props_orc and from the working tree's
        head = subprocess.run(["git", "-C", ROOT, "show", "HEAD:src/interior/vki_props_orc.py"], capture_output=True,
                              text=True, encoding="utf8").stdout
        now = {b: U.static_hash(g, b) for b in (False, True)}
        t = bpy.data.texts["vki_props_orc"]
        mine = t.as_string()
        t.from_string(head)
        g_head = (lambda g0: (exec(bpy.data.texts["vki_core"].as_string(), g0), g0["vki_ns"]())[1])({})
        before = {b: U.static_hash(g_head, b) for b in (False, True)}
        t.from_string(mine)
        out["static_unchanged"] = {("burnt" if b else "fresh"): (before[b], now[b], before[b] == now[b]) for b in now}
        g = (lambda g0: (exec(bpy.data.texts["vki_core"].as_string(), g0), g0["vki_ns"]())[1])({})
        out["parts"] = U.build_unit_blend(g)
    else:
        assert bpy.data.filepath.endswith("vku_siege_catapult.blend"), bpy.data.filepath
        bpy.context.preferences.system.vbo_time_out = 0
        out.update(U.run(args))
        if "save" in args:
            bpy.ops.wm.save_mainfile()
            out["saved"] = bpy.data.filepath
except Exception:
    out["error"] = traceback.format_exc()
print("VKU_RESULT " + json.dumps(out, default=str))
