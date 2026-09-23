# ===================== KIT SYNC: src/ files  <->  Blender texts =====================
# The generator code runs from Blender *texts* stored inside the .blend (vk_kit loads them by name).
# src/ holds one file per text, with the same name (src/terrain/vk_terrain.py <-> text "vk_terrain").
# Workflow: edit the file in src/, push it into the .blend, re-run the builder you need, save the .blend.
#
# Run inside Blender (Text Editor > Run Script, or the Blender MCP tool):
#   exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\kit_sync.py", encoding="utf8").read())
#   status()                  # which texts differ from their files
#   push("vk_terrain")        # file -> Blender text (one name, a list, or everything when called without names)
#   pull("vk_town_map")       # Blender text -> file (for edits made in Blender's Text Editor)
# Nothing is rebuilt by this tool.
import bpy, os, glob

VK_ROOT = globals().get("VK_ROOT_OVERRIDE") or r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
SRC = os.path.join(VK_ROOT, "src")
EXTRA = {"README_VillageKit": os.path.join(VK_ROOT, "docs", "KIT_README.md")}   # texts that live outside src/


def text_files():
    """text name -> file path: every src/**/*.py or *.json (text name = file name without extension) + EXTRA"""
    out = {}
    for p in glob.glob(os.path.join(SRC, "**", "*.*"), recursive=True):
        if p.endswith((".py", ".json")) and "__pycache__" not in p:
            n = os.path.splitext(os.path.basename(p))[0]
            if n in out:
                raise RuntimeError(f"two files for text {n}: {out[n]} and {p}")
            out[n] = p
    out.update(EXTRA)
    return out


def _read(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def _text(t):
    return t.as_string().replace("\r\n", "\n")


def _names(names):
    return None if names is None else ([names] if isinstance(names, str) else list(names))


def status(quiet=False):
    """list every text / file pair: same, DIFFERENT, file only, blender only"""
    files, rows = text_files(), []
    for n in sorted(set(files) | {t.name for t in bpy.data.texts}):
        t, p = bpy.data.texts.get(n), files.get(n)
        if t is None: s = "file only (push to add)"
        elif p is None: s = "blender only (pull to save)"
        else: s = "same" if _read(p).rstrip() == _text(t).rstrip() else "DIFFERENT"
        rows.append((n, s))
    if not quiet:
        for n, s in rows: print(f"  {s:28s} {n}")
    return rows


def push(names=None):
    """file -> Blender text (creates the text if needed); returns the names that changed"""
    files, done = text_files(), []
    for n in (_names(names) or sorted(files)):
        if n not in files: raise KeyError(f"no file for text {n}")
        src = _read(files[n])
        t = bpy.data.texts.get(n) or bpy.data.texts.new(n)
        if _text(t).rstrip() != src.rstrip():
            t.from_string(src); done.append(n)
    print("pushed:", done or "nothing (all same)")
    return done


def pull(names=None, new_dir="unsorted"):
    """Blender text -> file; texts without a file go to src/<new_dir>/<name>.py; returns the names written"""
    files, done = text_files(), []
    for n in (_names(names) or sorted(t.name for t in bpy.data.texts)):
        t = bpy.data.texts.get(n)
        if t is None: raise KeyError(f"no Blender text {n}")
        p = files.get(n) or os.path.join(SRC, new_dir, n + ".py")
        s = _text(t)
        if not os.path.exists(p) or _read(p).rstrip() != s.rstrip():
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf8", newline="\n") as f:
                f.write(s if s.endswith("\n") else s + "\n")
            done.append(n)
    print("pulled:", done or "nothing (all same)")
    return done
