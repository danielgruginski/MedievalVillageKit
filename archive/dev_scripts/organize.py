"""Reorganize the session workspace into one coherent project folder: <workspace>/MedievalVillageKit/..."""
import os, shutil, glob, filecmp, sys
W = r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817"
TMP = r"C:\Users\danie\AppData\Local\Temp\claude\C--Users-danie-AppData-Roaming-Claude-scratch-workspaces-ec03f06b-60f5-4d5d-94a9-dff3a56c5f56-f8ddc2b6-f8a4-41c6-98db-14b97d4348ea-scratch-2026-09-23-d49817\421a57cc-0ba3-43b1-888d-34ef79f58bc6"
PROJ = r"C:\Users\danie\.claude\projects"
P = os.path.join(W, "MedievalVillageKit")
log = []

def mv(src, dst):
    """move a file or a folder; dst is the full destination path"""
    if not os.path.exists(src): log.append(f"MISSING {src}"); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst): raise RuntimeError(f"refusing to overwrite {dst}")
    shutil.move(src, dst); log.append(f"moved {os.path.relpath(src, W)} -> {os.path.relpath(dst, W)}")

def cp(src, dst):
    if not os.path.exists(src): log.append(f"MISSING {src}"); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src): shutil.copytree(src, dst)
    else: shutil.copy2(src, dst)
    log.append(f"copied {src} -> {os.path.relpath(dst, W)}")

C = os.path.join(W, "code"); X = os.path.join(W, "_blender_texts_export")
# ---------------------------------------------------------------- src/ (the Blender texts, one file each)
groups = {
    "core": ["vk_kit", "vk_helpers", "vk_mat", "vk_render"],
    "textures": ["vk_tex", "vk_texgen", "vk_tex2", "vk_leafgen"],
    "modules": ["vk_mod_humble", "vk_mod_frontier", "vk_mod_construction", "vk_mod_skyline",
                "vk_mod_town", "vk_mod_water", "vk_mod_industry", "vk_mod_defence"],
    "nature": ["vk_nature"],
    "terrain": ["vk_terrain", "vk_terrain_demo"],
    "maps": ["vk_town_map"],
    "workshop": ["ws_common"],
    "early_scenes": ["mc_helpers", "wk_helpers", "tree_build"],
}
for grp, names in groups.items():
    for n in names:
        local, exp = os.path.join(C, n + ".py"), os.path.join(X, n + ".py")
        dst = os.path.join(P, "src", grp, n + ".py")
        if os.path.exists(local):
            if n != "vk_nature" and not filecmp.cmp(local, exp, shallow=False):
                # line endings may differ; compare normalized text
                a = open(local, encoding="utf8").read().replace("\r\n", "\n"); b = open(exp, encoding="utf8").read().replace("\r\n", "\n")
                if a != b: raise RuntimeError(f"{n}: local copy differs from the Blender text")
            mv(local, dst)
            os.remove(exp); log.append(f"removed duplicate export {n}.py (identical to code/)" if n != "vk_nature" else "removed older export vk_nature.py (code/ has NATURE_SPECS)")
        else:
            mv(exp, dst)
mv(os.path.join(X, "tree_skeleton.py"), os.path.join(P, "src", "early_scenes", "tree_skeleton.json"))
# README text inside the .blend == docs/KIT_README.md
a = open(os.path.join(X, "README_VillageKit.md"), encoding="utf8").read().replace("\r\n", "\n")
b = open(os.path.join(C, "KIT_README.md"), encoding="utf8").read().replace("\r\n", "\n")
log.append("README_VillageKit identical to KIT_README.md: " + str(a.strip() == b.strip()))
if a.strip() == b.strip(): os.remove(os.path.join(X, "README_VillageKit.md"))
else: mv(os.path.join(X, "README_VillageKit.md"), os.path.join(P, "archive", "backups", "README_VillageKit_blender_text.md"))
# ---------------------------------------------------------------- add-on, docs, reviews
mv(os.path.join(C, "unity_nav.py"), os.path.join(P, "blender_addons", "unity_nav.py"))
mv(os.path.join(C, "KIT_README.md"), os.path.join(P, "docs", "KIT_README.md"))
mv(os.path.join(C, "VALLEY_MAP.md"), os.path.join(P, "docs", "VALLEY_MAP.md"))
H = os.path.join(P, "docs", "history")
mv(os.path.join(C, "AGENT_BRIEF.md"), os.path.join(H, "AGENT_BRIEF.md"))
mv(os.path.join(C, "WS_MANIFEST.md"), os.path.join(H, "WS_MANIFEST.md"))
mv(os.path.join(C, "_mods_summary.md"), os.path.join(H, "modules_summary.md"))
mv(os.path.join(C, "kit_pieces.txt"), os.path.join(H, "kit_pieces_2026-09-23_morning.txt"))
for f in glob.glob(os.path.join(C, "spec_*.md")): mv(f, os.path.join(H, "specs", os.path.basename(f)))
for f in glob.glob(os.path.join(C, "full_*.md")): mv(f, os.path.join(H, "design_panels", os.path.basename(f)))
R = os.path.join(P, "reviews")
mv(os.path.join(C, "review_confirmed.txt"), os.path.join(R, "valley_review_1", "review_confirmed.txt"))
mv(os.path.join(C, "review_result.json"), os.path.join(R, "valley_review_1", "review_result.json"))
mv(os.path.join(C, "agent_reports.json"), os.path.join(R, "module_build_agents", "agent_reports.json"))
mv(os.path.join(C, "agent_notes.txt"), os.path.join(R, "module_build_agents", "agent_notes.txt"))
wf_out = {"wtztjbn3k": "01_design_panels_terrain_buildings_stone", "wxp2qnltq": "02_village_kit_buildings_8_agents",
          "w31ua9oy7": "03_village_kit_buildings_continue", "wre4m6tad": "04_valley_review_1",
          "wo6ikbrat": "05_nature_mesh_fixes", "w7zndtw1h": "06_valley_review_2_rereview", "b819noyla": "misc_overlap_scan"}
for tid, name in wf_out.items():
    cp(os.path.join(TMP, "tasks", tid + ".output"), os.path.join(R, "workflow_results", name + ".json" if not name.startswith("misc") else name + ".txt"))
shots = {"1.webp": "01_plaster_repeats.webp", "2.webp": "02_cherry_tree_billboards.webp", "3.webp": "03_ramp_cliff_mismatch.webp"}
for s, d in shots.items(): cp(os.path.join(TMP, "images", s), os.path.join(P, "docs", "feedback_screenshots", d))
# ---------------------------------------------------------------- tools
for f in glob.glob(os.path.join(PROJ, "*scratch-2026-09-23-d49817*", "**", "workflows", "scripts", "*.js"), recursive=True):
    dst = os.path.join(P, "tools", "workflows", os.path.basename(f).rsplit("-wf_", 1)[0] + ".js")
    if not os.path.exists(dst): cp(f, dst)
# ---------------------------------------------------------------- archive
A = os.path.join(P, "archive")
for f in glob.glob(os.path.join(C, "ws_*.py")): mv(f, os.path.join(A, "workshop_modules", os.path.basename(f)))
mv(os.path.join(C, "patch_kit_stone.py"), os.path.join(A, "patches", "patch_kit_stone.py"))
for f in glob.glob(os.path.join(C, "*_before_*.py")): mv(f, os.path.join(A, "backups", os.path.basename(f)))
for f in os.listdir(os.path.join(W, "backup_nature2")):
    src = os.path.join(W, "backup_nature2", f)
    if f.endswith("_before.py"): mv(src, os.path.join(A, "backups", f.replace("_before", "_before_nature_pass1")))
    else: mv(src, os.path.join(A, "dev_scripts", "nature_pass1", f))
SP = os.path.join(TMP, "scratchpad")
patches = {"p_final.py", "p_landmarks.py", "p_mat.py", "p_mods.py", "p_paving.py", "p_shutters.py", "p_stalls.py", "fix2.py", "splice.py"}
data_ext = (".json", ".txt", ".png")
for f in sorted(os.listdir(SP)):
    src = os.path.join(SP, f)
    if os.path.isdir(src): continue
    if f in patches: cp(src, os.path.join(A, "patches", f))
    elif f.startswith(("T_VK_Leaves", "vk_nature_", "ws_humble_backup")): cp(src, os.path.join(A, "backups", f))
    elif f.endswith(".py"): cp(src, os.path.join(A, "dev_scripts", f))
    elif f.endswith(data_ext): cp(src, os.path.join(A, "dev_data", f))
mv(os.path.join(W, "_staging_logs"), os.path.join(A, "script_logs"))
# ---------------------------------------------------------------- assets
mv(os.path.join(W, "VillageKit", "Textures"), os.path.join(P, "assets", "textures"))
mv(os.path.join(W, "TreeAsset"), os.path.join(P, "assets", "tree_asset"))
mv(os.path.join(W, "StoneWallKit_FBX"), os.path.join(P, "assets", "stone_wall_kit_fbx"))
mv(os.path.join(W, "stone_dev"), os.path.join(P, "assets", "texture_dev"))
# ---------------------------------------------------------------- renders
RD = os.path.join(P, "renders")
for f in glob.glob(os.path.join(W, "*.png")): mv(f, os.path.join(RD, "showcase", os.path.basename(f)))
R2 = os.path.join(W, "renders2")
module_dirs = {"construction", "defence", "frontier", "humble", "industry", "skyline", "town", "water"}
for d in sorted(os.listdir(R2)):
    src = os.path.join(R2, d)
    if os.path.isdir(src):
        if d in module_dirs: mv(src, os.path.join(RD, "modules", d))
        elif d == "review": mv(src, os.path.join(RD, "valley_review_1"))
        elif d == "rereview": mv(src, os.path.join(RD, "valley_review_2"))
        elif d == "zztest": mv(src, os.path.join(RD, "misc", "zztest"))
        else: mv(src, os.path.join(RD, d))
    else: mv(src, os.path.join(RD, "misc", d))
# ---------------------------------------------------------------- clean up emptied folders
for d in (C, X, os.path.join(W, "VillageKit"), os.path.join(W, "backup_nature2"), R2):
    left = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs] if os.path.exists(d) else []
    if left: log.append(f"NOT EMPTY, kept: {d}: {left[:10]}")
    elif os.path.exists(d): shutil.rmtree(d); log.append(f"removed empty {os.path.relpath(d, W)}")
print("\n".join(l for l in log if not l.startswith(("moved", "copied"))))
print(sum(1 for l in log if l.startswith("moved")), "moves,", sum(1 for l in log if l.startswith("copied")), "copies")
print("workspace root now:", os.listdir(W))
