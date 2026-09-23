# ===================== VK KIT LOADER =====================
# One namespace with the whole village kit: core helpers + the expansion modules + terrain.
#   exec(bpy.data.texts["vk_kit"].as_string()); g=vk_kit_ns()
#   g["full_rebuild"]()            rebuilds every SM_VK_* piece (core + modules) in place
#   g["build_hovel"](coll, origin) ... every builder of every module is available
import bpy
KIT_MODULES=["vk_mod_humble","vk_mod_frontier","vk_mod_construction","vk_mod_skyline",
             "vk_mod_town","vk_mod_water","vk_mod_industry","vk_mod_defence"]
TERRAIN_TEXTS=["vk_nature","vk_terrain","vk_terrain_demo"]
def vk_kit_ns(terrain=True,modules=True):
    g={}
    exec(bpy.data.texts["vk_helpers"].as_string(),g)
    g["KIT_MODULE_SPECS"]={}
    if modules:
        for m in KIT_MODULES:
            exec(bpy.data.texts[m].as_string(),g)
            g["KIT_MODULE_SPECS"][m]=[n for n,_,_ in g.get("WS_SPECS",[])]
    if terrain:
        for t in TERRAIN_TEXTS: exec(bpy.data.texts[t].as_string(),g)
    return g
