# ===================== GDX: export the kit to a Godot project =====================
# Godot 4 side of the kit, beside the Unity export (vkx_export.py), which it reuses and never changes:
#   - one .glb per master piece (Blender -> glTF, no Unity in between), at the origin, used slots only;
#   - one shared material library, kit/materials/<M_name>.tres, written from vkx's analysis in the Unity package's
#     Data/materials.json (its T_VKX_* bakes included): plain StandardMaterial3D where that is enough, the small
#     KitLit.gdshader for moss, the vki_rim glow and the roof jitter. Every glb maps its materials to the library by
#     name at import (its .glb.import), so all pieces share one material per kit material;
#   - the textures those materials use, copied from the Unity package's Art/Textures;
#   - kit/data/pieces.json (surfaces, Blender slot -> surface, bounds) and layouts (placements, lights, cameras) for
#     the Godot builder (the addon's KitBuilder.cs);
#   - the addon itself (the repo's godot/addons/medieval_kit: shaders, C# tools) is linked into the project, not copied.
# The Godot side runs on Godot's .NET build: tools/gdx_round.sh (import, check, build, capture, compare).
# Restyles (VAR_ / VARI_) are the master's glb with surface_material_override/N on the instance.
#
# Run in a background Blender (it only adds and removes its own scenes; nothing is saved):
#   blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- pilot
# or inside Blender:
#   g={}; exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\export\gdx_export.py", encoding="utf8").read(), g)
#   g["gdx_export_pieces"](["SM_VKI_Overlay_Ash"]); g["gdx_write_materials"]()
#
# Axes: the glTF exporter writes +Y up, so Godot sees Blender (x, y, z) as (x, z, -y); Blender's front (-Y) is Godot's
# +Z (Godot's model front). Placements use the same matrix (G M G^-1); cameras and lights keep their own frames (G M).
import bpy, bmesh, os, io, json, re, math, shutil, struct, contextlib, sys
from mathutils import Matrix, Vector

GDX_REPO = r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
GDX_PROJECT = globals().get("GDX_PROJECT_OVERRIDE") or r"E:\Unity\Godot\GameArtGeneration\medieval-kit"
GDX_KIT = os.path.join(GDX_PROJECT, "kit")
GDX_VERSION = "2026-10-24 pilot"

# vkx_export in a namespace of its own: piece names, used slots, restyles, light / world descriptions, signatures.
# Only its readers are called here; its paths point at the Unity package, read for materials.json and the textures.
VKX = {}
exec(open(os.path.join(GDX_REPO, "src", "export", "vkx_export.py"), encoding="utf8").read(), VKX)

G = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
GI = G.inverted()


def _mk(p):
    os.makedirs(p, exist_ok=True)
    return p


def _res(path):
    """absolute path inside the Godot project -> res:// path"""
    return "res://" + os.path.relpath(path, GDX_PROJECT).replace("\\", "/")


def _r(v, n=5):
    return round(float(v), n)


def _load(p):
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f: return json.load(f)
    return {}


def _save(p, d):
    _mk(os.path.dirname(p))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=1, sort_keys=True)


def _write_if_changed(p, text):
    _mk(os.path.dirname(p))
    if os.path.exists(p) and open(p, encoding="utf-8").read() == text: return False
    with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(text)
    return True


GDX_ADDON = os.path.join(GDX_REPO, "godot", "addons", "medieval_kit")


def gdx_link_addon():
    """the project's addons/medieval_kit is a directory junction to the repo's godot/addons/medieval_kit (the Godot
    counterpart of the Unity package: edited in the repo, seen by the project as is); made when missing"""
    dst = os.path.join(GDX_PROJECT, "addons", "medieval_kit")
    if os.path.exists(dst):
        if os.path.normcase(os.path.realpath(dst)) != os.path.normcase(os.path.realpath(GDX_ADDON)):
            raise RuntimeError(f"{dst} exists and is not a link to {GDX_ADDON}")
        return "linked"
    import _winapi
    _mk(os.path.dirname(dst))
    _winapi.CreateJunction(GDX_ADDON, dst)
    return "made"


# ---------------------------------------------------------------- colours
def srgb(c):
    """Blender's linear colour -> the sRGB-encoded values Godot's Color properties take"""
    c = max(0.0, float(c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _color(rgb, a=1.0):
    return "Color(%s, %s, %s, %s)" % tuple(_r(x, 6) for x in (srgb(rgb[0]), srgb(rgb[1]), srgb(rgb[2]), a))


def godot_specular(level):
    """Blender's Specular IOR Level (F0 = 0.08 x level at IOR 1.5) -> Godot's metallic_specular (F0 = 0.16 x s^2)"""
    return _r(math.sqrt(max(0.0, float(level)) / 2.0), 4)


# ---------------------------------------------------------------- Object Info > Random
def _rot32(x, k):
    return ((x << k) | (x >> (32 - k))) & 0xFFFFFFFF


def blender_object_random(name):
    """Object Info > Random of a (non-instanced) object, as EEVEE and Cycles compute it:
    BLI_hash_int_2d(BLI_hash_string(name), 0) / 0xFFFFFFFF"""
    M = 0xFFFFFFFF
    h = 0
    for ch in name.encode("utf-8"): h = (h * 37 + ch) & M
    a = b = c = (0xdeadbeef + (2 << 2) + 13) & M
    a = (a + h) & M
    c ^= b; c = (c - _rot32(b, 14)) & M
    a ^= c; a = (a - _rot32(c, 11)) & M
    b ^= a; b = (b - _rot32(a, 25)) & M
    c ^= b; c = (c - _rot32(b, 16)) & M
    a ^= c; a = (a - _rot32(c, 4)) & M
    b ^= a; b = (b - _rot32(a, 14)) & M
    c ^= b; c = (c - _rot32(b, 24)) & M
    return c / M


# ---------------------------------------------------------------- pieces -> .glb
def _family_dir(pn):
    """models/<kit>/<family>, as the Unity export files them"""
    return VKX["_family_dir"](pn)


def _glb_read(path):
    with open(path, "rb") as f: data = f.read()
    magic, ver, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF", path
    jl, jt = struct.unpack_from("<I4s", data, 12)
    js = json.loads(data[20:20 + jl].decode("utf-8"))
    rest = data[20 + jl:]
    return js, rest


def _glb_write(path, js, rest):
    j = json.dumps(js, separators=(",", ":")).encode("utf-8")
    j += b" " * ((4 - len(j) % 4) % 4)
    body = struct.pack("<I4s", len(j), b"JSON") + j + rest
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body)


# where the kit's pieces depart from Blender's materials, as Unity's KitBuilder.MaterialDefaults: painted furniture is
# plain wood (Daniel's call, 2026-10-02: no teal chests); shutters, stalls and boats keep their paint, and a style on
# the "shutter" slot still paints them
GDX_MATERIAL_DEFAULTS = {
    "SM_VKI_Prop_Chest": ("M_VK_Shutter_Teal", "M_VK_Shutter_Natural"),
    "SM_VKI_Prop_Dresser": ("M_VK_Shutter_Teal", "M_VK_Shutter_Natural"),
}


def gdx_piece_path(pn):
    return os.path.join(GDX_KIT, "models", _family_dir(pn), pn + ".glb")


def gdx_export_piece(me, report):
    """one .glb per master mesh: used slots only (a material repeated in two slots is written once per slot, as a
    temporary copy '<name>__s<slot>', so a restyle can change one of them), the vertex colour 'Col' (linear, glTF's
    COLOR_0) with the vki_rim glow gradient in its alpha, tangents for the normal maps, the master's custom
    properties as glTF extras (Godot: node metadata 'extras'). Materials go out without images (glTF's own
    'PLACEHOLDER' mode drops their names too); the .glb.import maps each name to the shared library."""
    pn = VKX["piece_name"](me)
    keep = VKX["used_slots"](me)
    path = gdx_piece_path(pn)
    _mk(os.path.dirname(path))
    tmp = me.copy(); tmp.name = "GDX_TMP_" + pn
    mats, names, slot_of, temps = [], [], {}, []
    for i in keep:
        m = me.materials[i]
        if m is None:
            m = bpy.data.materials.get("GDX_None") or bpy.data.materials.new("GDX_None")
        em = m
        if m.name in names or any(t.name == m.name for t in temps):
            em = m.copy(); em.name = f"{m.name}__s{i}"; temps.append(em)
        slot_of[i] = len(mats)
        mats.append(m.name); names.append(em.name)
    idx = [0] * len(tmp.polygons)
    tmp.polygons.foreach_get("material_index", idx)
    idx = [slot_of[i] for i in idx]
    tmp.materials.clear()
    for n in names: tmp.materials.append(bpy.data.materials[n])
    tmp.polygons.foreach_set("material_index", idx)
    tcol = "TCol" in tmp.color_attributes
    keep_col = "TCol" if tcol else "Col"
    rim = "vki_rim" in tmp.attributes
    if rim:     # the glow gradient rides in the vertex colour's alpha (only rim materials read it), as for Unity
        a = tmp.attributes["vki_rim"]
        vals = [0.0] * len(tmp.vertices)
        a.data.foreach_get("value", vals)
        col = tmp.color_attributes.get("Col") or tmp.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
        if col.domain == "CORNER":
            for loop in tmp.loops:
                c = col.data[loop.index].color
                col.data[loop.index].color = (c[0], c[1], c[2], max(0.0, min(1.0, vals[loop.vertex_index])))
        else:
            for i, v in enumerate(vals):
                c = col.data[i].color
                col.data[i].color = (c[0], c[1], c[2], max(0.0, min(1.0, v)))
    for c in [c for c in tmp.color_attributes if c.name != keep_col]:
        tmp.color_attributes.remove(c)
    if keep_col in tmp.color_attributes:
        tmp.color_attributes.active_color = tmp.color_attributes[keep_col]
        tmp.color_attributes.render_color_index = tmp.color_attributes.active_color_index
    for a in [a for a in tmp.attributes if a.name.startswith("vki_")]:
        tmp.attributes.remove(a)
    bm = bmesh.new(); bm.from_mesh(tmp)       # triangulated as vkx does: the glTF exporter computes no tangents for n-gons
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(tmp); bm.free()
    ob = bpy.data.objects.new("GDX_TMP_" + pn, tmp)
    mo = VKX["master_object"](me)
    props = VKX["_props"](mo) if mo is not None else {}
    for k, v in props.items():
        try: ob[k] = v
        except (TypeError, ValueError): ob[k] = json.dumps(v)
    sc = bpy.data.scenes.get("GDX_Export") or bpy.data.scenes.new("GDX_Export")
    sc.collection.objects.link(ob)
    vl = sc.view_layers[0]
    # the window shows the export scene while exporting (as vkx does), and the exporter is kept to that scene
    # (use_active_scene): by default it visits every scene of the file, and one of them crashes the depsgraph
    win = bpy.context.window
    prev = win.scene if win else None
    try:
        if win: win.scene = sc
        vl.update()
        with bpy.context.temp_override(window=win, scene=sc, view_layer=vl):
            for o2 in sc.objects: o2.select_set(o2 == ob)
            vl.objects.active = ob
            with contextlib.redirect_stdout(io.StringIO()):
                bpy.ops.export_scene.gltf(
                    filepath=path, export_format="GLB", use_selection=True, use_active_scene=True,
                    export_yup=True, export_apply=False,
                    export_texcoords=True, export_normals=True, export_tangents=True, export_materials="EXPORT", export_image_format="NONE",
                    export_vertex_color="ACTIVE", export_all_vertex_colors=False, export_extras=True,
                    export_attributes=False, export_animations=False, export_skins=False, export_morph=False,
                    export_lights=False, export_cameras=False)
    finally:
        if win: win.scene = prev
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(tmp)
        for t in temps: bpy.data.materials.remove(t)
    # the node and mesh carry the piece's name (the master object holds that name in the .blend)
    js, rest = _glb_read(path)
    for n in js.get("nodes", []): n["name"] = pn
    for m in js.get("meshes", []): m["name"] = pn
    js.setdefault("asset", {})["extras"] = {"gdx": GDX_VERSION}
    _glb_write(path, js, rest)
    gm = [x.get("name") for x in js.get("materials", [])]
    surf = [gm[p["material"]] if "material" in p else None for p in js["meshes"][0]["primitives"]]
    base_of = {n: mats[i] for i, n in enumerate(names)}
    swap = GDX_MATERIAL_DEFAULTS.get(pn)
    if swap: base_of = {k: (swap[1] if v == swap[0] else v) for k, v in base_of.items()}
    surfaces = [base_of.get(s, s) for s in surf]
    slot_map = {str(i): surf.index(names[slot_of[i]]) for i in keep}
    lo = [min(v.co[i] for v in me.vertices) for i in range(3)] if me.vertices else [0, 0, 0]
    hi = [max(v.co[i] for v in me.vertices) for i in range(3)] if me.vertices else [0, 0, 0]
    has_col = keep_col in me.color_attributes or rim
    report["pieces"] += 1
    return {"name": pn, "glb": _res(path), "surfaces": surfaces, "glb_materials": surf, "slot_map": slot_map,
            "vertex_color": keep_col if has_col else None, "rim": rim,
            "bounds_blender": [[_r(x, 4) for x in lo], [_r(x, 4) for x in hi]],
            "bounds_godot": [[_r(lo[0], 4), _r(lo[2], 4), _r(-hi[1], 4)], [_r(hi[0], 4), _r(hi[2], 4), _r(-lo[1], 4)]],
            "tris": sum(len(p.vertices) - 2 for p in me.polygons), "props": props}


GLB_IMPORT = """[remap]

importer="scene"
importer_version=1
type="PackedScene"

[params]

nodes/root_type=""
nodes/root_name=""
nodes/apply_root_scale=true
nodes/root_scale=1.0
array_mesh/deduplicate_surfaces=false
meshes/ensure_tangents=true
meshes/generate_lods=false
meshes/create_shadow_meshes=true
meshes/light_baking=1
meshes/lightmap_texel_size=0.2
meshes/force_disable_compression=false
skins/use_named_skins=true
animation/import=false
import_script/path="res://addons/medieval_kit/Editor/KitImport.cs"
_subresources={
"materials": {
%s
}
}
gltf/naming_version=2
gltf/embedded_image_handling=0
"""


def gdx_write_glb_import(piece):
    """the .glb.import: no LODs (the kit's rule), every material name -> the shared library's .tres"""
    ents = []
    for gname, base in zip(piece["glb_materials"], piece["surfaces"]):
        if gname is None: continue
        ents.append('"%s": {\n"use_external/enabled": true,\n"use_external/path": "res://kit/materials/%s.tres"\n}'
                    % (gname, base))
    p = os.path.join(GDX_PROJECT, piece["glb"][len("res://"):]) + ".import"
    old = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    text = GLB_IMPORT % ",\n".join(ents)
    if old is not None and "uid=" in old:      # keep Godot's uid and the generated keys it added after a first import
        m = re.search(r'^uid="[^"]+"$', old, re.M)
        if m: text = text.replace('type="PackedScene"\n', 'type="PackedScene"\n%s\n' % m.group(0), 1)
    _write_if_changed(p, text)


def gdx_export_pieces(names):
    """export these master pieces (object names) to .glb, update kit/data/pieces.json; returns the report and the
    material names they use"""
    meshes, failed = {}, {}
    for n in names:
        o = bpy.data.objects.get(n)
        if o is None or o.type != "MESH" or VKX["master_object"](o.data) is not o: failed[n] = "no master object"
        else: meshes[n] = o.data
    report, used = gdx_export_meshes(meshes)
    report["failed"].update(failed)
    return report, used


def gdx_export_meshes(meshes):
    """export these meshes ({name: mesh}: masters, or a level's own meshes such as the valley's U_VKV_ chunks) to .glb,
    update kit/data/pieces.json; returns the report and the material names they use"""
    pieces = _load(os.path.join(GDX_KIT, "data", "pieces.json"))
    report = {"pieces": 0, "failed": {}}
    used = set()
    for n, me in meshes.items():
        try:
            d = gdx_export_piece(me, report)
        except Exception as e:
            report["failed"][n] = repr(e); continue
        pieces[d["name"]] = d
        gdx_write_glb_import(d)
        used.update(m for m in d["surfaces"] if m)
    _save(os.path.join(GDX_KIT, "data", "pieces.json"), pieces)
    return report, sorted(used)


# ---------------------------------------------------------------- materials -> .tres
VKX_MATERIALS = os.path.join(VKX["VKX_DATA"], "materials.json")
VKX_TEXTURES = VKX["VKX_TEX"]
# vkx's analysis (and bakes) of materials the Unity export has not seen yet, made here with vkx's own functions into a
# cache of the Godot project's, so the Unity package is never written (kit/.vkx, ignored by Godot)
GDX_VKX_CACHE = os.path.join(GDX_KIT, ".vkx")


def vkx_materials(names):
    """vkx's analysis for these materials: the Unity export's materials.json, else (made now) the Godot-side cache"""
    out = _load(VKX_MATERIALS)
    missing = [n for n in names if not out.get(n) and bpy.data.materials.get(n) is not None]
    cache = _load(os.path.join(GDX_VKX_CACHE, "materials.json"))
    todo = {n: cache.get(n) for n in missing}
    if todo:
        _mk(os.path.join(GDX_VKX_CACHE, "textures"))
        open(os.path.join(GDX_VKX_CACHE, ".gdignore"), "w").close()
        old = VKX["VKX_TEX"], VKX["VKX_DATA"]
        VKX["VKX_TEX"], VKX["VKX_DATA"] = os.path.join(GDX_VKX_CACHE, "textures"), GDX_VKX_CACHE
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                VKX["process_materials"](todo, {}, {"notes": {}})     # skips those whose signature is unchanged
        finally:
            VKX["VKX_TEX"], VKX["VKX_DATA"] = old
            VKX["vkx_cleanup"]()                                       # the bake images, in memory only
        cache.update(todo)
        _save(os.path.join(GDX_VKX_CACHE, "materials.json"), cache)
    out.update({n: cache[n] for n in missing if cache.get(n)})
    return out

TEX_IMPORT = """[remap]

importer="texture"
type="CompressedTexture2D"

[params]

compress/mode=%d
compress/high_quality=true
compress/lossy_quality=0.7
compress/hdr_compression=1
compress/normal_map=%d
compress/channel_pack=0
mipmaps/generate=%s
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=0
"""


def gdx_texture(fn, normal=False, done=None, control=False):
    """copy a texture of the Unity export into kit/textures (with an .import: VRAM compressed, mipmaps, BC5 normals;
    a terrain control map lossless and without mipmaps, as in Unity: its layers are thresholded, not blurred)"""
    src = os.path.join(VKX_TEXTURES, fn)
    if not os.path.exists(src): src = os.path.join(GDX_VKX_CACHE, "textures", fn)
    if not os.path.exists(src): raise FileNotFoundError(fn)
    dst = os.path.join(GDX_KIT, "textures", fn)
    _mk(os.path.dirname(dst))
    if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src) or open(dst, "rb").read() != open(src, "rb").read():
        shutil.copyfile(src, dst)
    imp = dst + ".import"
    mode = 0 if control else 2
    text = TEX_IMPORT % (mode, 1 if normal else 0, "false" if control else "true")
    old = open(imp, encoding="utf-8").read() if os.path.exists(imp) else ""
    if ("compress/normal_map=%d" % (1 if normal else 0)) not in old or ("compress/mode=%d" % mode) not in old:
        _write_if_changed(imp, text)
    if done is not None: done.add(fn)
    return _res(dst)


def gdx_bump(mn):
    """a card material's bump from a height map over its geometric normal (vk_leafgen's leaves and herbs: Blender's
    Bump(Height = T_*_H, Normal = Geometry > Normal flipped on back faces)); vkx keeps the flat card. None if absent."""
    m = bpy.data.materials.get(mn)
    if m is None or not m.use_nodes: return None
    nt = m.node_tree
    for b in (n for n in nt.nodes if n.type == "BUMP"):
        if not (b.inputs["Height"].is_linked and b.inputs["Normal"].is_linked): continue
        h = b.inputs["Height"].links[0].from_node
        if h.type != "TEX_IMAGE" or h.image is None: continue
        src = b.inputs["Normal"].links[0].from_node
        if not any(n.type == "NEW_GEOMETRY" for n in [src] + list(VKX["_upstream"](nt, src))): continue
        return {"image": h.image.name, "strength": _r(b.inputs["Strength"].default_value),
                "distance": _r(b.inputs["Distance"].default_value)}
    return None


def gdx_blend_image(name):
    """a .blend image the Unity export never wrote (a leaf sheet's height map), written into the Godot-side cache with
    vkx's export_image; returns its file name for gdx_texture"""
    _mk(os.path.join(GDX_VKX_CACHE, "textures"))
    old = VKX["VKX_TEX"]
    VKX["VKX_TEX"] = os.path.join(GDX_VKX_CACHE, "textures")
    try:
        return VKX["export_image"](name, {})
    finally:
        VKX["VKX_TEX"] = old


def blender_alpha_mode(mn):
    """how Blender draws a material's transparency: 'DITHERED' (hashed) or 'BLENDED'"""
    m = bpy.data.materials.get(mn)
    return getattr(m, "surface_render_method", None) if m is not None else None


class _Tres:
    """a Godot text resource being written: ext_resources, sub_resources + [resource] lines"""
    def __init__(self, typ):
        self.typ, self.ext, self.lines, self.subs = typ, [], [], []

    def sub_res(self, typ, lines):
        """a [sub_resource] (lines: "key = value" strings) -> its reference"""
        sid = "sub_%d" % (len(self.subs) + 1)
        self.subs.append((typ, sid, lines))
        return f'SubResource("{sid}")'

    def ext_res(self, typ, path):
        for i, (t, p) in enumerate(self.ext):
            if p == path: return f'ExtResource("{i + 1}")'
        self.ext.append((typ, path))
        return f'ExtResource("{len(self.ext)}")'

    def set(self, k, v):
        if isinstance(v, bool): v = "true" if v else "false"
        elif isinstance(v, float): v = repr(_r(v, 6))
        self.lines.append(f"{k} = {v}")

    def text(self):
        out = [f'[gd_resource type="{self.typ}" format=3]', ""]
        for i, (t, p) in enumerate(self.ext):
            out.append(f'[ext_resource type="{t}" path="{p}" id="{i + 1}"]')
        if self.ext: out.append("")
        for typ, sid, lines in self.subs:
            out += [f'[sub_resource type="{typ}" id="{sid}"]'] + lines + [""]
        out.append("[resource]")
        out += self.lines
        return "\n".join(out) + "\n"


# StandardMaterial3D enums
TRANSPARENCY = {"opaque": 0, "alpha": 1, "scissor": 2, "hash": 3}
CULL_BACK, CULL_DISABLED = 0, 2
DEPTH_OPAQUE, DEPTH_ALWAYS, DEPTH_NEVER = 0, 1, 2
FILTER_ANISO = 5            # linear, mipmaps, anisotropic
DIFFUSE_LAMBERT = 1         # Blender's Principled diffuse is Lambertian (Godot's default is Burley)


def gdx_draw_mode(d):
    """how a kit material is drawn: Blender's cut-outs (alpha > threshold) -> 'clip'; dithered texture alpha -> 'hash';
    blended or a constant alpha -> 'blend'. A surface that casts no shadow ('Is Shadow Ray' -> Transparent: windows,
    webs, puddles) goes to the transparent pass, which Godot never draws into shadow maps: an opaque one as 'glass'
    (alpha 1, depth written), a dithered one blended (Blender's 64 dithered samples converge to the blend; Godot's hash
    stayed grainy on web strands)."""
    alpha, no_shadow = d.get("alpha", "opaque"), bool(d.get("no_shadow"))
    if alpha == "clip": return "clip"
    if alpha == "blend":
        return "hash" if d.get("alpha_map") and blender_alpha_mode(d["name"]) != "BLENDED" and not no_shadow else "blend"
    return "glass" if no_shadow else "opaque"


KITLIT_VARIANT = {"opaque": "", "clip": "Clip", "hash": "Hash", "blend": "Blend", "glass": "Glass"}
# Every kit material is a KitLit ShaderMaterial (the see-through and the shroud clip every one, as in Unity).
# 'standard' writes the pilot's StandardMaterial3Ds instead where they suffice: the reference KitLit was checked against.
GDX_MATERIALS = globals().get("GDX_MATERIALS_OVERRIDE") or "kitlit"


KITTERRAIN_VARIANT = {"terrain": "", "stair": "Stair", "paving": "Paving", "water": "Water"}   # paving + box: Curb
TERRAIN_LAYERS = ("Grass", "Sand", "Dirt", "Cobble", "Cliff", "Moss", "Stone")


def terrain_slot(image):
    """a projected material's image -> its KitTerrain parameter, by name (Unity: KitBuilder.TerrainProp)"""
    if "GroundCtl" in image: return "ctl_map"
    if "TerrainMacro" in image: return "macro_map"
    m = re.match(r"^T_VK_([A-Za-z]+)_(BC|H|R)$", image)
    if not m: return None
    key = "Stone" if m.group(1) == "StoneBlock" else m.group(1)
    if key not in TERRAIN_LAYERS: return None
    return key.lower() + ("_map" if m.group(2) == "BC" else "_h")


def gdx_terrain_tres(d, done, notes):
    """a projected material (vk_terrain's recipes) -> a ShaderMaterial on its KitTerrain variant"""
    t = _Tres("ShaderMaterial")
    t.set("resource_name", f'"{d["name"]}"')
    t.set("render_priority", 0)
    rec = d.get("recipe")
    var = "Curb" if rec == "paving" and d.get("box") else KITTERRAIN_VARIANT[rec]
    t.set("shader", t.ext_res("Shader", "res://addons/medieval_kit/Shaders/KitTerrain%s.gdshader" % var))
    sp = lambda k, v: t.set("shader_parameter/" + k, v)
    imgs = d.get("images") if isinstance(d.get("images"), dict) else {}
    for img, fn in sorted(imgs.items()):
        slot = terrain_slot(img)
        if slot is None:
            notes.append("image %s has no KitTerrain slot" % img); continue
        sp(slot, t.ext_res("Texture2D", gdx_texture(fn, done=done, control=slot == "ctl_map")))
    if d.get("ctl_scale"): sp("ctl_scale", "Vector2(%s, %s)" % (_r(d["ctl_scale"][0], 8), _r(d["ctl_scale"][1], 8)))
    if rec == "terrain":    # the grass's saturation as the Blender material has it (the shader's 0.6 is the game's pick)
        m = bpy.data.materials.get(d["name"])
        hs = next((n for n in m.node_tree.nodes if n.type == "HUE_SAT"), None) if m is not None and m.use_nodes else None
        if hs is not None: sp("grass_sat", _r(hs.inputs["Saturation"].default_value))
    if d.get("proj_scale") is not None: sp("proj_scale", float(d["proj_scale"]))
    sp("rough", float(d.get("roughness", 0.8)))
    if d.get("bump_strength") is not None: sp("bump_strength", float(d["bump_strength"]))
    if rec == "water": sp("water_alpha", float((d.get("base_color") or [0, 0, 0, 0.9])[3]))
    return t.text()


def gdx_classify(d):
    """what a kit material becomes in Godot: 'kitlit' (a KitLit variant), 'kitterrain' (the projected terrain /
    stair / paving / water recipes), 'standard' (StandardMaterial3D, only with GDX_MATERIALS 'standard') or 'skip'
    (a projected material without a recipe), with notes on approximations"""
    if d.get("shader") == "projected":
        if d.get("recipe") not in KITTERRAIN_VARIANT: return "skip", ["projected material without a KitTerrain recipe"]
        return "kitterrain", ["KitTerrain %s: Blender's noise and bump as the Unity port's stand-ins" % d["recipe"]]
    notes = []
    mode = gdx_draw_mode(d)
    if d.get("translucency"): notes.append("translucency %.2f as backlight (Godot's own back-lighting term)" % d["translucency"])
    if d.get("no_shadow"):
        notes.append("casts no shadow: drawn in the transparent pass" if mode in ("glass", "blend")
                     else "casts no shadow in Blender, a cut-out here: it casts one")
    if gdx_bump(d["name"]):
        notes.append("bump from the height map over the geometric normal (vkx keeps the flat card)")
        notes += [n for n in d.get("notes") or [] if not any(k in n for k in ("NEW_GEOMETRY", "VECT_MATH", "BUMP"))]
    else:
        notes += d.get("notes") or []
    special = d.get("moss") or d.get("rim") or d.get("jitter") or gdx_bump(d["name"])
    return ("kitlit" if GDX_MATERIALS == "kitlit" or special else "standard"), notes


def gdx_material_tres(d, done):
    """one kit material (vkx analysis) -> the .tres text"""
    kind, notes = gdx_classify(d)
    if kind == "kitterrain": return gdx_terrain_tres(d, done, notes), kind, notes
    mode = gdx_draw_mode(d)
    if kind == "kitlit":
        t = _Tres("ShaderMaterial")
        two = bool(d.get("double_sided"))
        t.set("resource_name", f'"{d["name"]}"')
        t.set("render_priority", 0)
        j = d.get("jitter") or [1.0, 1.0]
        jit = list(j) != [1.0, 1.0]       # only the roofs: an instance uniform costs every instance a slot
        t.set("shader", t.ext_res("Shader", "res://addons/medieval_kit/Shaders/KitLit%s%s%s.gdshader"
                                  % ("TwoSided" if two else "", "Jitter" if jit else "", KITLIT_VARIANT[mode])))
        sp = lambda k, v: t.set("shader_parameter/" + k, v)
        bc = d.get("base_color") or [1, 1, 1, 1]
        sp("base_color", _color(bc[:3], 1.0 if mode == "glass" else (bc[3] if len(bc) > 3 else 1.0)))
        if d.get("base_map"): sp("albedo_map", t.ext_res("Texture2D", gdx_texture(d["base_map"], done=done)))
        if mode == "clip": sp("alpha_cut", float(d.get("cutoff", 0.5)))
        if d.get("translucency"): sp("translucency", float(d["translucency"]))
        bump = gdx_bump(d["name"])
        if bump:
            sp("use_bump", True)
            sp("bump_map", t.ext_res("Texture2D", gdx_texture(gdx_blend_image(bump["image"]), done=done)))
            sp("bump_strength", bump["strength"]); sp("bump_distance", bump["distance"])
        sp("use_vertex_color", bool(d.get("vertex_color")))
        if jit: sp("jitter", "Vector2(%s, %s)" % (_r(j[0]), _r(j[1])))
        sp("roughness", float(d.get("roughness", 0.5)))
        if d.get("rough_map"):
            sp("use_rough_map", True); sp("rough_map", t.ext_res("Texture2D", gdx_texture(d["rough_map"], done=done)))
            sp("rough_scale", float(d.get("rough_scale", 1.0)))
        sp("metallic", float(d.get("metallic", 0.0)))
        sp("specular", godot_specular(d.get("specular", 0.5)))
        if d.get("normal_map"):
            sp("use_normal_map", True)
            sp("normal_map", t.ext_res("Texture2D", gdx_texture(d["normal_map"], normal=True, done=done)))
            sp("normal_strength", float(d.get("normal_strength", 1.0)))
        es = float(d.get("emission_strength", 0.0))
        if es > 0:
            ec = [1, 1, 1] if d.get("emission_map") else (d.get("emission") or [0, 0, 0])
            sp("emission_color", _color(ec)); sp("emission_strength", es)
            if d.get("emission_map"): sp("emission_map", t.ext_res("Texture2D", gdx_texture(d["emission_map"], done=done)))
        rim = d.get("rim")
        if rim:
            k = rim.get("k") or [1, 0]
            kk = (k[0], k[1]) if rim.get("op") == "MULTIPLY_ADD" else (k[0], 0.0)
            if rim.get("op") not in ("MULTIPLY_ADD", "MULTIPLY"): notes.append("rim op %s not ported" % rim.get("op"))
            cols = rim.get("colors") or [[0, 0, 0, 1], [1, 1, 1, 1]]
            sp("use_rim", True); sp("rim_color_a", _color(cols[0][:3])); sp("rim_color_b", _color(cols[1][:3]))
            sp("rim_k", "Vector2(%s, %s)" % (_r(kk[0]), _r(kk[1])))
        moss = d.get("moss")
        if moss:
            sp("use_moss", True)
            sp("moss_map", t.ext_res("Texture2D", gdx_texture(moss["moss_map"], done=done)))
            if moss.get("moss_normal"): sp("moss_normal", t.ext_res("Texture2D", gdx_texture(moss["moss_normal"], normal=True, done=done)))
            if moss.get("moss_rough"): sp("moss_rough", t.ext_res("Texture2D", gdx_texture(moss["moss_rough"], done=done)))
            if moss.get("moss_height"): sp("moss_height", t.ext_res("Texture2D", gdx_texture(moss["moss_height"], done=done)))
            sp("moss_tile", float(moss.get("tile", 1.0)))
            sp("moss_noise", "Vector2(%s, %s)" % tuple(_r(x) for x in moss.get("noise", [0, 0])))
            sp("moss_range", "Vector2(%s, %s)" % tuple(_r(x) for x in moss.get("range", [0, 1])))
            if not moss.get("gate_vertex_alpha"): notes.append("moss without the vertex-alpha gate (the shader always gates)")
        if not two and mode in ("opaque", "clip", "hash"):
            # the see-through's caps (Unity KitLit's SeeThroughCap pass): a one-sided solid opened by the hole shows its
            # back faces flat, as its cut (KitLitCap.gdshader)
            cap = ['resource_name = "%s_Cap"' % d["name"],
                   "shader = %s" % t.ext_res("Shader", "res://addons/medieval_kit/Shaders/KitLitCap.gdshader"),
                   "shader_parameter/base_color = %s" % _color(bc[:3], 1.0)]
            if d.get("base_map"):
                cap.append("shader_parameter/albedo_map = %s" % t.ext_res("Texture2D", gdx_texture(d["base_map"], done=done)))
            if mode == "clip": cap.append("shader_parameter/alpha_cut = %r" % _r(float(d.get("cutoff", 0.5)), 6))
            if jit: cap.append("shader_parameter/jitter = Vector2(%s, %s)" % (_r(j[0]), _r(j[1])))
            t.set("next_pass", t.sub_res("ShaderMaterial", cap))
        return t.text(), kind, notes
    t = _Tres("StandardMaterial3D")
    t.set("resource_name", f'"{d["name"]}"')
    tr = {"clip": "scissor", "hash": "hash", "blend": "alpha", "glass": "alpha"}.get(mode)
    if tr: t.set("transparency", TRANSPARENCY[tr])
    if mode == "clip": t.set("alpha_scissor_threshold", float(d.get("cutoff", 0.5)))
    if mode == "glass": t.set("depth_draw_mode", DEPTH_ALWAYS)      # alpha 1: drawn as opaque, writes depth
    t.set("cull_mode", CULL_DISABLED if d.get("double_sided") else CULL_BACK)
    t.set("diffuse_mode", DIFFUSE_LAMBERT)
    t.set("texture_filter", FILTER_ANISO)
    t.set("vertex_color_use_as_albedo", bool(d.get("vertex_color")))
    t.set("vertex_color_is_srgb", False)           # glTF vertex colours are linear, as Blender multiplies them
    bc = list(d.get("base_color") or [1, 1, 1, 1])
    tl = float(d.get("translucency") or 0.0)
    a = 1.0 if mode == "glass" else (bc[3] if len(bc) > 3 else 1.0)
    # translucency (leaves, foliage, crops): Blender mixes (1 - t) x surface + t x Translucent BSDF. Godot's backlight
    # adds light from behind times albedo x backlight: albedo x (1 - t) and backlight t / (1 - t) give the same shares.
    k = 1.0 - tl
    t.set("albedo_color", _color([x * k for x in bc[:3]], a))
    if d.get("base_map"): t.set("albedo_texture", t.ext_res("Texture2D", gdx_texture(d["base_map"], done=done)))
    if tl > 0:
        t.set("backlight_enabled", True)
        b = tl / k
        t.set("backlight", _color([b, b, b]))
    t.set("metallic", float(d.get("metallic", 0.0)))
    t.set("metallic_specular", godot_specular(d.get("specular", 0.5)))
    if d.get("rough_map"):
        t.set("roughness", float(d.get("rough_scale", 1.0)))
        t.set("roughness_texture", t.ext_res("Texture2D", gdx_texture(d["rough_map"], done=done)))
        t.set("roughness_texture_channel", 0)
    else:
        t.set("roughness", float(d.get("roughness", 0.5)))
    if d.get("normal_map"):
        t.set("normal_enabled", True)
        t.set("normal_scale", float(d.get("normal_strength", 1.0)))
        t.set("normal_texture", t.ext_res("Texture2D", gdx_texture(d["normal_map"], normal=True, done=done)))
    es = float(d.get("emission_strength", 0.0))
    ec = [1, 1, 1] if d.get("emission_map") else (d.get("emission") or [0, 0, 0])
    if es > 0 and (d.get("emission_map") or any(x > 0 for x in ec)):
        t.set("emission_enabled", True)
        t.set("emission", _color(ec))
        t.set("emission_energy_multiplier", es)
        if d.get("emission_map"):         # map x colour (Godot's default operator adds them)
            t.set("emission_operator", 1)
            t.set("emission_texture", t.ext_res("Texture2D", gdx_texture(d["emission_map"], done=done)))
    return t.text(), kind, notes


def gdx_write_materials(names=None):
    """write kit/materials/<name>.tres for these kit materials (default: every one in materials.json) and
    kit/data/materials.json: what each became and why. Names ending in __s<slot> are the slots' copies (no .tres)."""
    src = vkx_materials(names) if names is not None else _load(VKX_MATERIALS)
    out = _load(os.path.join(GDX_KIT, "data", "materials.json"))
    done, written, missing = set(), [], []
    for mn in sorted(names if names is not None else src):
        d = src.get(mn)
        if not d:
            missing.append(mn); continue
        kind, notes = gdx_classify(d)
        if kind == "skip":
            out[mn] = {"kind": kind, "notes": notes}; continue
        text, kind, notes = gdx_material_tres(d, done)
        if _write_if_changed(os.path.join(GDX_KIT, "materials", mn + ".tres"), text): written.append(mn)
        out[mn] = {"kind": kind, "notes": notes, "tres": "res://kit/materials/%s.tres" % mn}
    _save(os.path.join(GDX_KIT, "data", "materials.json"), out)
    return {"written": written, "textures": sorted(done), "missing": missing}


def gdx_export_all(collections=None):
    """every master piece of the kit's collections (VK_Pieces, VKI_Pieces, VK_NaturePieces, VK_TerrainTiles) and the
    materials they use"""
    names = []
    for cn in (collections or VKX["VKX_PIECE_COLLECTIONS"]):
        for o in sorted(bpy.data.collections[cn].objects, key=lambda o: o.name):
            if o.type == "MESH" and o.data.vertices and VKX["master_object"](o.data) is o: names.append(o.name)
    rep, used = gdx_export_pieces(names)
    mats = gdx_write_materials(used)
    return {"pieces": rep["pieces"], "failed": rep["failed"], "materials": len(used),
            "written": len(mats["written"]), "textures": len(mats["textures"]), "missing": mats["missing"]}


GDX_CATALOGS = {"Exterior": ["VK_Pieces", "VK_NaturePieces", "VK_TerrainTiles"], "Interior": ["VKI_Pieces"]}


def gdx_catalog(which, render=True):
    """a verification catalog (vkx_build_catalog: every master of the kit by family, orthographic 50-degree cameras,
    lit like the valley) as scene GDX_Catalog_<which>, its layout Catalog_<which> and the Blender renders into the
    project's catalog/<which>/shots; the Godot side: sh tools/gdx_round.sh Catalog_<which> <project> <shots> 1920x1080"""
    sc_name = "GDX_Catalog_" + which
    info = VKX["vkx_build_catalog"](sc_name, GDX_CATALOGS[which])
    sc = bpy.data.scenes[sc_name]
    for o in sorted([o for o in sc.objects if o.type == "CAMERA" and o.name.startswith("VKX_CatCam")], key=lambda o: o.name):
        o.name = "GDX_Cam_%s_%s" % (re.match(r"VKX_CatCam_(\d+)", o.name).group(1), which.lower())
    lay = gdx_export_layout(sc_name, name="Catalog_" + which, export_pieces=False)
    out = {"catalog": info, "layout": {k: v for k, v in lay.items() if k != "materials"}}
    out["materials"] = gdx_write_materials(lay["materials"])["missing"]
    if render:
        shots = _mk(os.path.join(GDX_PROJECT, "catalog", which.lower(), "shots"))
        open(os.path.join(GDX_PROJECT, "catalog", ".gdignore"), "w").close()
        out["renders"] = len(gdx_render_cameras(sc_name, shots, shadows=False))
    return out


def gdx_valley_terrain(render=True):
    """KitTerrain on a real map: the valley's ground (VK_ValleyTerrain: terrain, paving, curbs, stairs, river) seen by
    copies of the Unity verification's eight VKX_ValleyCams, lit like the catalogs (flat world, no AO, no shadows) so
    only the shader is compared; layout Valley_Terrain (origin x 1500 -> 0), renders in the project's
    catalog/valley_terrain/shots. Godot: sh tools/gdx_round.sh Valley_Terrain "" <shots> 1600x1000"""
    name = "GDX_ValleyTerrain"
    old = bpy.data.scenes.get(name)
    if old is not None:
        for o in list(old.objects):
            if o.name.startswith("GDX_Cam"):
                cd = o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(cd)
        bpy.data.scenes.remove(old)
    sc = bpy.data.scenes.new(name)
    cat, vk = bpy.data.scenes["VKX_Catalog_Interior"], bpy.data.scenes["VillageKit"]
    sc.world = cat.world
    for a in ("view_transform", "look", "exposure", "gamma"): setattr(sc.view_settings, a, getattr(cat.view_settings, a))
    sc.render.engine = cat.render.engine
    for a in ("use_gtao", "use_shadows", "taa_render_samples", "use_raytracing"):
        if hasattr(cat.eevee, a): setattr(sc.eevee, a, getattr(cat.eevee, a))
    sc.render.resolution_x, sc.render.resolution_y = vk.render.resolution_x, vk.render.resolution_y
    for o in bpy.data.collections["VK_ValleyTerrain"].all_objects:
        if o.type == "MESH": sc.collection.objects.link(o)
    for n in ("VK_Sun", "VK_Fill"): sc.collection.objects.link(bpy.data.objects[n])
    for vl in vk.view_layers: vl.update()       # a scene not on screen has stale matrix_world (HANDOFF gotchas)
    for i, c in enumerate(sorted(bpy.data.collections["VKX_ValleyCams"].objects, key=lambda o: o.name)):
        cam = bpy.data.objects.new("GDX_Cam_%02d_%s" % (i, c.name.split("_", 3)[-1]), c.data.copy())
        cam.matrix_world = c.matrix_world.copy()
        sc.collection.objects.link(cam)
        if i == 0: sc.camera = cam
    for vl in sc.view_layers: vl.update()
    lay = gdx_export_layout(name, name="Valley_Terrain", origin=(1500, 0, 0), export_pieces=False)
    out = {"layout": {k: v for k, v in lay.items() if k != "materials"},
           "missing": gdx_write_materials(lay["materials"])["missing"]}
    if render:
        shots = _mk(os.path.join(GDX_PROJECT, "catalog", "valley_terrain", "shots"))
        open(os.path.join(GDX_PROJECT, "catalog", ".gdignore"), "w").close()
        out["renders"] = len(gdx_render_cameras(name, shots, shadows=False))
    return out


GDX_WORLD_JSON = os.path.join(GDX_REPO, "docs", "world_graph.json")


def gdx_export_world(levels=None, render=True):
    """every level of docs/world_graph.json (or `levels`) as a layout under its world-graph name -- the valley is
    VillageKit's ground, town, sun and fill with the verification cameras, x 1500 -> 0, as for Unity -- plus
    kit/data/world.json, and each level's cameras rendered into the project's catalog/levels/<level>/
    (blender_<camera>.png) for: sh tools/gdx_round.sh <level> "" <that folder>"""
    graph = _load(GDX_WORLD_JSON)
    out = {}
    for n in (levels or list(graph["levels"])):
        if n == "VK_ValleyTown":
            sc_name, objs = "VillageKit", VKX["vkx_valley_objects"]()
            lay = gdx_export_layout(sc_name, objects=objs, name=n, origin=(1500, 0, 0), export_pieces=False)
        else:
            sc_name, objs = n, None
            lay = gdx_export_layout(n, name=n, export_pieces=False)
        mats = gdx_write_materials(lay["materials"])
        out[n] = {"placements": lay["placements"], "new_pieces": lay["new_pieces"], "failed": lay["failed"],
                  "missing": mats["missing"]}
        if render:
            shots = _mk(os.path.join(GDX_PROJECT, "catalog", "levels", n))
            open(os.path.join(GDX_PROJECT, "catalog", ".gdignore"), "w").close()
            cams = [o for o in (objs if objs is not None else bpy.data.scenes[sc_name].objects) if o.type == "CAMERA"]
            out[n]["renders"] = len(gdx_render_cameras(sc_name, shots, cameras=cams))
    shutil.copyfile(GDX_WORLD_JSON, os.path.join(GDX_KIT, "data", "world.json"))
    return out


def gdx_export_rules():
    """the generators' rules as the Unity export wrote them (vkx_export_interior_rules / vkx_export_house_rules: Blender
    room space and Blender piece names, nothing engine-specific) -> kit/data/interior_rules.json (KitRoom and the room
    generators) and kit/data/house_rules.json (KitHouseGenerator); run those two first when the Blender rules change"""
    out = []
    for fn in ("interior_rules.json", "house_rules.json"):
        shutil.copyfile(os.path.join(VKX["VKX_DATA"], fn), os.path.join(_mk(os.path.join(GDX_KIT, "data")), fn))
        out.append(fn)
    return out


def gdx_export_structures(render=True):
    """the premade structures (vkx_build_structures: Blender's builders, a row in scene GDX_Structures) -> one
    kit/data/structures/<name>.json each (origin on the structure's own, as Unity's Data/Structures; KitBuilder makes
    res://kit/structures/<name>.tscn) and the whole row as the layout Structures_Showcase with a 50-degree camera on each,
    rendered into the project's catalog/structures/shots for (at its own size):
    sh tools/gdx_round.sh Structures_Showcase "" <shots> "" """
    sc_name = "GDX_Structures"
    built, errors = VKX["vkx_build_structures"](None, sc_name)
    builders = {n: f for n, f, k in VKX["VKX_STRUCTURES"]}
    sc = bpy.data.scenes[sc_name]
    out = {"errors": errors, "structures": {}}
    mats = set()
    for name, coll, ox, cam in built:
        objs = [o for o in coll.all_objects if o.type != "CAMERA"]
        r = gdx_export_layout(sc_name, objects=objs, name=name, origin=(ox, 0, 0), export_pieces=False, folder="structures",
                              extra={"structure": name, "builder": builders[name]})
        out["structures"][name] = {"placements": r["placements"], "new_pieces": r["new_pieces"], "failed": r["failed"]}
        mats.update(r["materials"])
    lay = gdx_export_layout(sc_name, name="Structures_Showcase", export_pieces=False)
    mats.update(lay["materials"])
    out["missing"] = gdx_write_materials(sorted(mats))["missing"]
    if render:
        shots = _mk(os.path.join(GDX_PROJECT, "catalog", "structures", "shots"))
        open(os.path.join(GDX_PROJECT, "catalog", ".gdignore"), "w").close()
        out["renders"] = len(gdx_render_cameras(sc_name, shots, cameras=[cam for _, _, _, cam in built]))
    return out


def gdx_classify_all():
    """every material of the Unity export's materials.json -> kind + notes (no files written)"""
    src = _load(VKX_MATERIALS)
    return {mn: gdx_classify(d) for mn, d in src.items() if d}


# ---------------------------------------------------------------- layouts (scenes -> placements for Godot)
def to_godot(mw, origin=None, local=True):
    """Blender world matrix -> Godot basis columns (x, y, z axes) and origin. local=True converts the object's own axes
    too (G M G^-1: meshes, whose vertices the glTF exporter converted the same way); cameras and lights look down their
    local -Z in both programs, so their frames stay as they are (G M)."""
    M = (Matrix.Translation(-Vector(origin)) if origin is not None else Matrix.Identity(4)) @ mw
    Mg = G @ M @ GI if local else G @ M
    cols = [[_r(Mg[r][c], 6) for r in range(3)] for c in range(3)]
    return cols, [_r(Mg[0][3]), _r(Mg[1][3]), _r(Mg[2][3])]


def gdx_export_layout(scene_name, objects=None, name=None, origin=None, export_pieces=True, folder="layouts", extra=None):
    """a scene (or some of its objects) -> kit/data/<folder>/<name>.json: placements (piece, transform, material
    overrides by Godot surface, Blender's Object Info random), lights, cameras, world and view transform, + `extra`. The
    pieces it uses are exported (export_pieces=False: only those not exported yet). Objects with a 'gdx_kind' property
    (helpers: floor, chart) are passed as is."""
    sc = bpy.data.scenes[scene_name]
    for vl in sc.view_layers: vl.update()
    objs = list(objects) if objects is not None else list(sc.objects)
    name = name or scene_name
    pieces = _load(os.path.join(GDX_KIT, "data", "pieces.json"))
    meshes = {}
    for o in objs:
        if o.type == "MESH" and not o.hide_render and "gdx_kind" not in o:
            base = VKX["vkx_base_mesh"](o)
            meshes.setdefault(VKX["piece_name"](base), base)
    todo = {n: me for n, me in sorted(meshes.items()) if export_pieces or n not in pieces}
    rep, _ = gdx_export_meshes(todo) if todo else ({}, [])
    pieces = _load(os.path.join(GDX_KIT, "data", "pieces.json"))
    placements, helpers, lights, cams, markers, mats = [], [], [], [], [], set()
    coll = lambda o: o.users_collection[0].name if o.users_collection else None
    for o in objs:
        if o.hide_render: continue
        basis, org = to_godot(o.matrix_world, origin, local=o.type not in ("CAMERA", "LIGHT"))
        if "gdx_kind" in o:     # flat quads: placed by their world bounding box (centre in Godot axes, Blender x / y size)
            pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
            lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
            ctr = [(lo[i] + hi[i]) / 2 - (origin[i] if origin else 0) for i in range(3)]
            helpers.append({"kind": o["gdx_kind"], "name": o.name, "center": [_r(ctr[0]), _r(ctr[2]), _r(-ctr[1])],
                            "size": [_r(hi[0] - lo[0]), _r(hi[1] - lo[1])], "props": VKX["_props"](o)})
        elif o.type == "MESH":
            base = VKX["vkx_base_mesh"](o)
            pn = VKX["piece_name"](base)
            pc = pieces.get(pn)
            if pc is None: continue
            ov = {}
            for slot, mn in VKX["material_overrides"](o, base).items():
                s = pc["slot_map"].get(str(slot))
                if s is not None: ov[str(s)] = mn; mats.add(mn)
            mats.update(m for m in pc["surfaces"] if m)
            placements.append({"piece": pn, "name": o.name, "basis": basis, "origin": org, "mat": ov,
                               "random": _r(blender_object_random(o.name), 6), "props": VKX["_props"](o),
                               "coll": coll(o)})
        elif o.type == "EMPTY":     # SPN_ spawns, LGT_ / FXA_ anchors, the VKI_Root and the rest of a level's markers
            markers.append({"name": o.name, "basis": basis, "origin": org, "props": VKX["_props"](o), "coll": coll(o)})
        elif o.type == "LIGHT":
            L = VKX["_light"](o)
            L.update({"name": o.name, "basis": basis, "origin": org, "coll": coll(o), "props": VKX["_props"](o),
                      "angle_deg": _r(math.degrees(getattr(o.data, "angle", 0.0)))})
            if o.data.type == "AREA":   # its rectangle (a disk or ellipse as the rectangle round it)
                two = o.data.shape in ("RECTANGLE", "ELLIPSE")
                L.update({"shape": o.data.shape, "size": [_r(o.data.size), _r(o.data.size_y if two else o.data.size)]})
            lights.append(L)
        elif o.type == "CAMERA":
            cd = o.data
            aspect = sc.render.resolution_x / sc.render.resolution_y
            cams.append({"name": o.name, "basis": basis, "origin": org, "type": cd.type,
                         "ortho_scale": _r(cd.ortho_scale), "fov_deg": _r(math.degrees(VKX["_vfov"](cd, sc))),
                         "clip": [_r(cd.clip_start), _r(cd.clip_end)], "aspect": _r(aspect),
                         "fit": "width" if aspect >= 1 else "height", "active": o == sc.camera})
    e = sc.eevee
    lay = {"name": name, "scene": scene_name, "version": GDX_VERSION,
           "view": {"transform": sc.view_settings.view_transform, "look": sc.view_settings.look,
                    "exposure": _r(sc.view_settings.exposure), "gamma": _r(sc.view_settings.gamma)},
           "world": VKX["_world"](sc.world), "shadows": bool(getattr(e, "use_shadows", True)),
           "ao": bool(getattr(e, "use_gtao", False)), "resolution": [sc.render.resolution_x, sc.render.resolution_y],
           "root": next((m["props"] for m in markers if m["name"].startswith("VKI_Root")), {}),
           "placements": placements, "markers": markers, "helpers": helpers, "lights": lights, "cameras": cams}
    lay.update(extra or {})
    _save(os.path.join(GDX_KIT, "data", folder, name + ".json"), lay)
    return {"layout": name, "placements": len(placements), "new_pieces": rep.get("pieces", 0),
            "failed": rep.get("failed", {}), "materials": sorted(mats)}


# ---------------------------------------------------------------- the pilot
# The interior kit's Overlay family (52 pieces) is the one family with every case the pilot has to settle: restyles
# (the debris stones take the level's stone in slot 58), alpha-clip foliage (moss, overgrowth), a hashed web
# (WebFloor), window glass that casts no shadow (GlassShards: stained glass in an iron frame) and one-sided solids
# (the exterior M_VK_ materials). A second row holds the restyles, a third the KitLit cases (roof jitter on two
# dormers, a mossy boulder, rim glow on candles and lava) and glass / web inside larger pieces (a window wall, a corner
# web), then a calibration chart of flat emissive patches for the view transform.
GDX_PILOT_RESTYLES = [
    ("SM_VKI_Overlay_Debris_Rocks_A", 58, [None, "M_VKI_AncientBlock", "M_VKI_CaveRock", "M_VKI_DungeonBlock", "M_VKI_SewerBlock"]),
    ("SM_VKI_Overlay_Debris_Rocks_C", 58, [None, "M_VKI_AncientBlock", "M_VKI_CaveRock", "M_VKI_DungeonBlock"]),
    ("SM_VKI_Overlay_Debris_Masonry_A", 58, [None, "M_VKI_AncientBlock", "M_VKI_DwarfBlock"]),
]
GDX_PILOT_CHECKS = ["SM_VK_Roof_Dormer", "SM_VK_Roof_Dormer", "SM_VK_Rock_Boulder_A", "SM_VKI_Prop_Candles_Floor",
                    "SM_VKI_Ground_Lava_OOOX", "SM_VKI_Wall_Timber_Window_150_Full", "SM_VKI_Prop_Web_Corner"]
GDX_CHART = [(v, v, v) for v in (0.01, 0.03, 0.08, 0.18, 0.4, 0.9, 2.0, 5.0)] + \
            [(0.8, 0.05, 0.02), (0.05, 0.6, 0.05), (0.03, 0.08, 0.9), (0.9, 0.6, 0.05), (0.6, 0.25, 0.15), (2.5, 1.2, 0.3)]
GDX_PILOT_SCENE = "GDX_Pilot"


def _shelf(items, x0, y0, row_w, gap):
    """lay masters out in rows along +X (fronts face -Y); returns [(object name, mesh, location)], the depth used"""
    x, y, row_d, out = 0.0, 0.0, 0.0, []
    for nm, me in items:
        lo = [min(v.co[i] for v in me.vertices) for i in range(3)]
        hi = [max(v.co[i] for v in me.vertices) for i in range(3)]
        w, d = hi[0] - lo[0], hi[1] - lo[1]
        if x > 0 and x + w > row_w:
            x = 0.0; y -= row_d + gap; row_d = 0.0
        out.append((nm, me, (x0 + x - lo[0], y0 + y - hi[1], -lo[2] if lo[2] < -0.3 else 0.0)))
        x += w + gap; row_d = max(row_d, d)
    return out, -y + row_d


def gdx_build_pilot_scene(row_w=12.0, gap=0.6, cols=2):
    """the pilot's comparison scene: the Overlay family, its restyles, the shader / glass checks and the chart, lit
    like the verification catalogs (VK_Sun, VK_Fill, VKX_SliceWorld, AgX), with orthographic 50-degree cameras tiling
    each row and a camera behind the window wall for the shadow check"""
    sc = bpy.data.scenes.get(GDX_PILOT_SCENE)
    if sc is not None:
        for o in list(sc.objects):
            d = o.data if o.type in ("CAMERA",) else None
            if o.name.startswith("GDX_"): bpy.data.objects.remove(o)
            if d is not None and d.users == 0: bpy.data.cameras.remove(d)
    else:
        sc = bpy.data.scenes.new(GDX_PILOT_SCENE)
    cat = bpy.data.scenes["VKX_Catalog_Interior"]
    for n in ("VK_Sun", "VK_Fill"):
        if n not in sc.objects: sc.collection.objects.link(bpy.data.objects[n])
    sc.world = cat.world
    for a in ("view_transform", "look", "exposure", "gamma"): setattr(sc.view_settings, a, getattr(cat.view_settings, a))
    sc.render.engine = cat.render.engine
    for a in ("use_gtao", "use_shadows", "taa_render_samples", "use_raytracing", "shadow_ray_count", "shadow_step_count"):
        if hasattr(cat.eevee, a): setattr(sc.eevee, a, getattr(cat.eevee, a))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1600, 900, 100
    sc.render.film_transparent = False
    rows = []
    vp = bpy.data.collections["VKI_Pieces"]
    over = sorted([o for o in vp.objects if o.type == "MESH" and o.name.startswith("SM_VKI_Overlay")
                   and VKX["master_object"](o.data) is o], key=lambda o: o.name)
    lay, depth = _shelf([(o.name, o.data) for o in over], 0.0, 0.0, row_w, gap)
    rows.append(("overlays", lay, 0.0, depth))
    y = -depth - 2.0
    items = []
    for pn, slot, opts in GDX_PILOT_RESTYLES:
        for mn in opts: items.append((f"{pn}|{slot}|{mn or ''}", bpy.data.objects[pn].data))
    lay, depth = _shelf(items, 0.0, y, row_w, gap)
    rows.append(("restyles", lay, y, depth))
    y -= depth + 2.0
    items = [(f"{pn}|#{i}", bpy.data.objects[pn].data) for i, pn in enumerate(GDX_PILOT_CHECKS)]
    lay, depth = _shelf(items, 0.0, y, row_w, gap * 2)
    rows.append(("checks", lay, y, depth))
    y -= depth + 2.0
    made = {}
    for row, lay, y0, d in rows:
        for key, me, loc in lay:
            parts = key.split("|")
            nm = "GDX_" + parts[0][3:] + ("_" + parts[2][2:] if len(parts) == 3 and parts[2] else "") + \
                 (parts[1].replace("#", "_") if len(parts) == 2 else "")
            o = bpy.data.objects.new(nm, me)
            if len(parts) == 3 and parts[2]:
                s = int(parts[1])
                o.material_slots[s].link = "OBJECT"; o.material_slots[s].material = bpy.data.materials[parts[2]]
            o.location = loc
            sc.collection.objects.link(o)
            made.setdefault(row, []).append(o)
    # the calibration chart: flat emissive patches (no diffuse, no specular) -> the view transform alone
    cm = []
    for i, c in enumerate(GDX_CHART):
        m = bpy.data.materials.get(f"GDX_Chart_{i:02d}") or bpy.data.materials.new(f"GDX_Chart_{i:02d}")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0, 0, 0, 1); b.inputs["Specular IOR Level"].default_value = 0.0
        b.inputs["Roughness"].default_value = 1.0
        b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = 1.0
        me = bpy.data.meshes.get(f"GDX_ChartQuad_{i:02d}") or bpy.data.meshes.new(f"GDX_ChartQuad_{i:02d}")
        me.clear_geometry()
        me.from_pydata([(0, 0, 0), (0.7, 0, 0), (0.7, 0.7, 0), (0, 0.7, 0)], [], [(0, 1, 2, 3)])
        me.materials.clear(); me.materials.append(m)
        o = bpy.data.objects.new(f"GDX_Chart_{i:02d}", me)
        o.location = ((i % 8) * 0.8, y - (i // 8) * 0.8, 0.01)
        o["gdx_kind"] = "chart"; o["gdx_emission"] = list(c)
        sc.collection.objects.link(o); cm.append(o)
    rows.append(("chart", [], y, 1.6))
    y -= 1.6 + 1.0
    # a grey floor under everything, a little below the overlays' undersides
    fm = bpy.data.materials.get("GDX_Floor") or bpy.data.materials.new("GDX_Floor")
    fm.use_nodes = True
    b = next(n for n in fm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.35, 0.33, 0.3, 1); b.inputs["Roughness"].default_value = 0.9
    b.inputs["Specular IOR Level"].default_value = 0.5
    fme = bpy.data.meshes.get("GDX_FloorQuad") or bpy.data.meshes.new("GDX_FloorQuad")
    fme.clear_geometry()
    x0, x1, y0f, y1f = -3.0, row_w + 3.0, y - 2.0, 4.0
    fme.from_pydata([(x0, y0f, 0), (x1, y0f, 0), (x1, y1f, 0), (x0, y1f, 0)], [], [(0, 1, 2, 3)])
    fme.materials.clear(); fme.materials.append(fm)
    fo = bpy.data.objects.new("GDX_Floor", fme); fo.location.z = -0.006
    fo["gdx_kind"] = "floor"; fo["gdx_color"] = [0.35, 0.33, 0.3]; fo["gdx_roughness"] = 0.9
    sc.collection.objects.link(fo)
    # cameras: 50 degrees down, looking north (+Y), orthographic, shot_w wide; each row tiled
    pitch = math.radians(50); aspect = sc.render.resolution_x / sc.render.resolution_y
    shot_w = (row_w + 1.0) / cols
    shot_h = shot_w / aspect
    n = 0
    for row, lay, ytop, d in rows:
        yy = ytop + 0.5
        while yy > ytop - d - 0.5:
            xx = -0.5
            while xx < row_w + 0.5 - 0.01:
                cd = bpy.data.cameras.new(f"GDX_Cam_{n:02d}_{row}"); cd.type = "ORTHO"; cd.ortho_scale = shot_w
                cd.clip_start = 0.1; cd.clip_end = 200
                cam = bpy.data.objects.new(f"GDX_Cam_{n:02d}_{row}", cd)
                tx, ty = xx + shot_w / 2, yy - shot_h / math.sin(pitch) / 2
                dist = 30.0
                cam.location = (tx, ty - math.cos(pitch) * dist, math.sin(pitch) * dist)
                cam.rotation_euler = (math.radians(90) - pitch, 0, 0)
                sc.collection.objects.link(cam)
                if n == 0: sc.camera = cam
                n += 1; xx += shot_w
            yy -= shot_h / math.sin(pitch)
    # the window wall seen from behind (the room side), where the sun comes through its glass
    win = next(o for o in made["checks"] if "Window" in o.name)
    lo = Vector([min(v.co[i] for v in win.data.vertices) for i in range(3)]) + win.location
    hi = Vector([max(v.co[i] for v in win.data.vertices) for i in range(3)]) + win.location
    ctr = (lo + hi) / 2
    cd = bpy.data.cameras.new(f"GDX_Cam_{n:02d}_glass"); cd.type = "ORTHO"; cd.ortho_scale = 5.0
    cd.clip_start = 0.1; cd.clip_end = 200
    cam = bpy.data.objects.new(f"GDX_Cam_{n:02d}_glass", cd)
    dist = 20.0
    cam.location = (ctr.x, ctr.y + 1.2 + math.cos(pitch) * dist, math.sin(pitch) * dist)
    cam.rotation_euler = (math.radians(90) - pitch, 0, math.radians(180))
    sc.collection.objects.link(cam)
    for vl in sc.view_layers: vl.update()
    return {"objects": sum(len(v) for v in made.values()), "cameras": n + 1, "rows": [(r[0], round(r[3], 2)) for r in rows]}


def gdx_render_cameras(scene_name, out_dir, shadows=None, tag="", cameras=None):
    """render every GDX_Cam_* of a scene (or these camera objects) to out_dir/blender<tag>_<camera>.png (shadows: force
    Eevee's on / off)"""
    sc = bpy.data.scenes[scene_name]
    prev = sc.camera, getattr(sc.eevee, "use_shadows", None)
    if shadows is not None: sc.eevee.use_shadows = shadows
    out = []
    try:
        for c in sorted(cameras if cameras is not None else
                        [o for o in sc.objects if o.type == "CAMERA" and o.name.startswith("GDX_Cam")], key=lambda o: o.name):
            sc.camera = c
            sc.render.filepath = os.path.join(_mk(out_dir), f"blender{tag}_{c.name}.png")
            with contextlib.redirect_stdout(io.StringIO()):
                bpy.ops.render.render(write_still=True, scene=sc.name)
            out.append(sc.render.filepath)
    finally:
        sc.camera = prev[0]
        if prev[1] is not None: sc.eevee.use_shadows = prev[1]
    return out


def gdx_check_random(names=("GDX_Roof_Dormer_0", "GDX_Roof_Dormer_1", "Foo", "SM_VK_Roof_Gable")):
    """Object Info > Random as EEVEE renders it vs blender_object_random: flat emissive quads, Standard view"""
    sc = bpy.data.scenes.new("GDX_RandomCheck")
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try: sc.render.engine = eng; break
        except TypeError: pass
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = 0
    sc.render.resolution_x, sc.render.resolution_y = len(names) * 8, 8
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.eevee.taa_render_samples = 1
    m = bpy.data.materials.new("GDX_RandomMat"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    oi = nt.nodes.new("ShaderNodeObjectInfo"); em = nt.nodes.new("ShaderNodeEmission"); out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(oi.outputs["Random"], em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
    w = bpy.data.worlds.new("GDX_RandomWorld"); sc.world = w; w.color = (0, 0, 0)
    objs = []
    for i, nm in enumerate(names):
        me = bpy.data.meshes.new("GDX_RQ")
        me.from_pydata([(i, 0, 0), (i + 1, 0, 0), (i + 1, 1, 0), (i, 1, 0)], [], [(0, 1, 2, 3)])
        me.materials.append(m)
        o = bpy.data.objects.new(nm, me); sc.collection.objects.link(o); objs.append(o)
    cd = bpy.data.cameras.new("GDX_RC"); cd.type = "ORTHO"; cd.ortho_scale = len(names)
    cam = bpy.data.objects.new("GDX_RC", cd); cam.location = (len(names) / 2, 0.5, 5); sc.collection.objects.link(cam); sc.camera = cam
    import tempfile
    fp = os.path.join(tempfile.gettempdir(), "gdx_random.exr"); sc.render.filepath = fp
    res = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.render.render(write_still=True, scene=sc.name)
        im = bpy.data.images.load(fp, check_existing=False)
        px = list(im.pixels)
        W = im.size[0]
        for i, o in enumerate(objs):
            k = (4 * W + i * 8 + 4) * 4
            res[o.name] = (round(px[k], 5), round(blender_object_random(o.name), 5))
        bpy.data.images.remove(im)
    finally:
        for o in objs:
            me = o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
        bpy.data.objects.remove(cam); bpy.data.cameras.remove(cd); bpy.data.materials.remove(m)
        bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    return res


def gdx_pilot(render=True):
    """the whole pilot: Godot files, the comparison scene, its layout (exports the pieces), the materials, renders"""
    out = {"addon": gdx_link_addon()}
    out["scene"] = gdx_build_pilot_scene()
    lay = gdx_export_layout(GDX_PILOT_SCENE, name="Pilot")
    out["layout"] = {k: v for k, v in lay.items() if k != "materials"}
    out["materials"] = gdx_write_materials(lay["materials"])
    out["random_check"] = gdx_check_random()
    if render:
        shots = os.path.join(GDX_PROJECT, "pilot", "shots")
        _mk(shots)
        open(os.path.join(shots, ".gdignore"), "w").close()       # Godot leaves the folder alone (no imports)
        out["renders"] = len(gdx_render_cameras(GDX_PILOT_SCENE, shots, shadows=False)) + \
            len(gdx_render_cameras(GDX_PILOT_SCENE, shots, shadows=True, tag="_shadows"))
    return out


if globals().get("__name__") == "__main__" and bpy.app.background and "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]
    if "standard" in args:          # the pilot's StandardMaterial3Ds (the reference KitLit is checked against)
        GDX_MATERIALS = "standard"; args.remove("standard")
    if args[:1] == ["pilot"]:
        print("GDX " + json.dumps(gdx_pilot(render="norender" not in args), default=str))
    elif args[:1] == ["pieces"]:
        gdx_link_addon()
        r, used = gdx_export_pieces(args[1:])
        print("GDX " + json.dumps({"report": r, "materials": gdx_write_materials(used)}, default=str))
    elif args[:1] == ["all"]:
        gdx_link_addon()
        print("GDX " + json.dumps(gdx_export_all(), default=str))
    elif args[:1] == ["catalog"]:
        gdx_link_addon()
        print("GDX " + json.dumps(gdx_catalog(args[1], render="norender" not in args), default=str))
    elif args[:1] == ["materials"]:     # every material of the Unity export's analysis and of the exported pieces
        used = {m for pc in _load(os.path.join(GDX_KIT, "data", "pieces.json")).values() for m in pc["surfaces"] if m}
        r = gdx_write_materials(sorted(used | set(_load(VKX_MATERIALS))))
        print("GDX " + json.dumps({"written": len(r["written"]), "textures": len(r["textures"]), "missing": r["missing"]}))
    elif args[:1] == ["terrain"]:
        gdx_link_addon()
        print("GDX " + json.dumps(gdx_valley_terrain(render="norender" not in args), default=str))
    elif args[:1] == ["world"]:       # world [level ...] [norender]
        gdx_link_addon()
        lv = [a for a in args[1:] if a != "norender"] or None
        print("GDX " + json.dumps(gdx_export_world(lv, render="norender" not in args), default=str))
    elif args[:1] == ["rules"]:       # the generators' rules (KitRoom, KitHouseGenerator)
        print("GDX " + json.dumps(gdx_export_rules()))
    elif args[:1] == ["structures"]:  # structures [norender]
        gdx_link_addon()
        print("GDX " + json.dumps(gdx_export_structures(render="norender" not in args), default=str))
    elif args[:1] == ["classify"]:
        print("GDX " + json.dumps(gdx_classify_all(), default=str))
