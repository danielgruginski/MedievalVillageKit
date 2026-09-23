# run inside Blender: push module, rebuild given pieces, rebuild the whole construction assembly
import bpy, time
_t0 = time.time()
_src = open(r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code\ws_construction.py", encoding="utf8").read()
_t = bpy.data.texts["ws_construction"]; _t.clear(); _t.write(_src)
exec(bpy.data.texts["ws_common"].as_string())
g = ws_ns("construction")
_names = globals().get("REBUILD", None)
if _names != []:
    _objs = ws_build("construction", g=g, names=_names)
    for _s in ws_stats(_objs): print(_s["name"][6:], _s["tris"], _s["bbox"], _s["zmin"])
    # new pieces land at the origin: park them in the catalog area
    for _o in _objs:
        if _o.location.length < 0.01: _o.location = (30.0, -12.0 - 4.0 * _objs.index(_o), 0.0)
sc, coll, asm = ws_scene("construction")
ws_clear_assembly("construction")
for _n in [n for n, _, _ in g["WS_SPECS"]]:
    for _c in ("Red", "Blue", "Green", "Yellow", "Purple", "White"):
        _me = bpy.data.meshes.get("VAR_" + str(abs(hash((_n, ("cloth", _c))))))
        if _me and _me.users == 0: bpy.data.meshes.remove(_me)
_B = g["build_construction_site"]
for _i, _st in enumerate((0, 1, 2, 3)): _B(asm, (-24 + 16 * _i, 0, 0), _st, seed=4)
_PL = {"ground": "Plaster", "ends": ("hip", "gable"), "plaster": "Ochre", "shutter": "Green", "roof": "Red"}
_B(asm, (-16, 30, 0), 1, seed=7, style=_PL)
_B(asm, (0, 30, 0), 2, seed=7, style=_PL)
_B(asm, (16, 30, 0), 2, seed=8, style={"ground": "Stone", "ends": ("hip", "hip"), "roof": "Slate"})
_B(asm, (32, 30, 0), 3, seed=7, style=_PL)
g["build_camp"](asm, (-20, 13, 0), seed=1)
g["build_stockpile"](asm, (-4, 13, 0), w=3, d=2, seed=2)
g["build_sawpit_yard"](asm, (10, 13, 0), seed=3)
print("assembly", len(asm.objects), round(time.time() - _t0, 1), "s")
