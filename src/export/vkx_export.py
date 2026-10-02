# ===================== VKX: export the kit to the Unity package =====================
# Writes FBX per master piece, the textures, and JSON (materials, pieces, levels) into the Unity package
# unity/com.danielgruginski.medievalkit. Unity's editor tools (Tools > Medieval Kit) build materials,
# prefabs and scenes from that data. Blender stays the source of truth: everything under Art/ and Data/
# is regenerated.
#
# Run inside Blender:
#   g={}; exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\export\vkx_export.py", encoding="utf8").read(), g)
#   g["vkx_export_level"]("VKI_Tavern_F0")                      # a scene: its pieces, materials, textures + level JSON
#   g["vkx_export_level"]("VKX_Slice_House", objects=coll.objects, name="Slice_House")
#
# Coordinates: meshes are exported with bake_space_transform, so Unity sees vertices as C*v with
# C (x, y, z) -> (-x, z, -y) and no root rotation. Placements are converted with the same C (C M C^-1),
# so the two agree by construction; the Unity verifier checks the piece bounds against C.
import bpy, bmesh, os, io, json, re, math, contextlib, hashlib
from mathutils import Matrix

VKX_PKG = globals().get("VKX_PKG_OVERRIDE") or r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\unity\com.danielgruginski.medievalkit"
VKX_MODELS = os.path.join(VKX_PKG, "Art", "Models")
VKX_TEX = os.path.join(VKX_PKG, "Art", "Textures")
VKX_DATA = os.path.join(VKX_PKG, "Data")
VKX_VERSION = "2026-09-30 slice"

VKX_PIECE_COLLECTIONS = ["VK_Pieces", "VKI_Pieces", "VK_NaturePieces", "VK_TerrainTiles"]

C = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
CI = C.inverted()


def _mk(p):
    os.makedirs(p, exist_ok=True)
    return p


def _r(v, n=5):
    return round(float(v), n)


def _jsonable(v):
    if hasattr(v, "to_dict"): return v.to_dict()
    if hasattr(v, "to_list"): return v.to_list()
    if isinstance(v, (int, float, str, bool)) or v is None: return v
    try: return list(v)
    except TypeError: return str(v)


def _props(idb):
    """custom properties -> dict; JSON strings stay strings (Unity parses the ones it knows)"""
    return {k: _jsonable(idb[k]) for k in idb.keys() if not k.startswith("_") and k != "cycles"}


# ---------------------------------------------------------------- bases and variants
def vkx_base_mesh(o):
    """the master mesh an instance was made from, or the instance's own mesh when it is unique.
    VARI_* (interior) records it in vki_base; VAR_* (exterior) only in the object name '<piece>_inst.NNN'."""
    me = o.data
    cand = me.get("vki_base")
    if not cand and me.name.startswith("VAR_"):
        nm = re.sub(r"_inst(\.\d+)?$", "", o.name)
        po = bpy.data.objects.get(nm)
        cand = po.data.name if po and po.type == "MESH" else None
    if not cand:
        return me
    bm = bpy.data.meshes.get(cand)
    if bm is None or len(bm.vertices) != len(me.vertices) or len(bm.polygons) != len(me.polygons) \
            or len(bm.materials) != len(me.materials):
        return me
    return bm


_MASTERS = {}


def master_object(me):
    """the master object that owns a mesh (SM_VK*_ name, not an instance), or None"""
    if not _MASTERS:
        for cn in VKX_PIECE_COLLECTIONS:          # the master collections win over helpers sharing a mesh
            c = bpy.data.collections.get(cn)
            for o in (sorted(c.objects, key=lambda x: x.name) if c else []):
                if o.type == "MESH" and o.name.startswith("SM_VK") and not re.search(r"\.\d+$", o.name):
                    _MASTERS.setdefault(o.data.name, o)
        for o in bpy.data.objects:
            if o.type == "MESH" and o.name.startswith("SM_VK") and "_inst" not in o.name \
                    and not re.search(r"\.\d+$", o.name):
                _MASTERS.setdefault(o.data.name, o)
    return _MASTERS.get(me.name)


def piece_name(me):
    """the exported piece's name: its master object's name; unique restyled meshes keep their own name"""
    mo = master_object(me)
    if mo is not None: return mo.name
    n = re.sub(r"\.\d+$", "", me.name)
    if n.startswith(("VAR_", "VARI_")) or bpy.data.objects.get(n) is not None:   # never take a master's name
        return "U_" + re.sub(r"[^A-Za-z0-9_]", "_", me.name)
    return n


def used_slots(me):
    idx = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", idx)
    return sorted(set(idx)) if idx else []


def material_overrides(o, base):
    """original slot index -> material name, where the instance's mesh differs from its base"""
    me = o.data
    out = {}
    used = used_slots(base)
    for i, s in enumerate(o.material_slots):     # object-level material links win over mesh ones
        if s.link == "OBJECT" and s.material and i in used:
            out[str(i)] = s.material.name
    if me == base: return out
    for i in used:
        if str(i) in out: continue
        a = base.materials[i].name if base.materials[i] else None
        b = me.materials[i].name if me.materials[i] else None
        if a != b and b: out[str(i)] = b
    return out


# ---------------------------------------------------------------- materials
def _link_from(nt, node, socket):
    for l in nt.links:
        if l.to_node == node and l.to_socket.name == socket:
            return l.from_node, l.from_socket
    return None, None


def _upstream(nt, node, seen=None):
    seen = seen if seen is not None else set()
    for l in nt.links:
        if l.to_node == node and l.from_node.name not in seen:
            seen.add(l.from_node.name)
            yield l.from_node
            yield from _upstream(nt, l.from_node, seen)


def analyze_material(m):
    """reduce a kit material's node tree to the parameters of the Unity KitLit shader.
    Unknown node patterns are listed in 'notes' (the export report shows them)."""
    d = {"name": m.name, "notes": [], "base_color": [1, 1, 1, 1], "base_map": None, "normal_map": None,
         "rough_map": None, "rough_scale": 1.0, "roughness": 0.5, "metallic": 0.0, "specular": 0.5,
         "vertex_color": False, "hsv": None, "jitter": None, "emission": [0, 0, 0], "emission_strength": 0.0,
         "rim": None, "alpha": "opaque", "alpha_map": None, "cutoff": 0.5, "double_sided": not m.use_backface_culling}
    if not m.use_nodes or not m.node_tree:
        d["base_color"] = list(m.diffuse_color); d["notes"].append("no nodes"); return d
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if b is None:
        d["notes"].append("no Principled BSDF"); return d
    known = {"OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "UVMAP", "TEX_IMAGE", "VERTEX_COLOR", "MIX", "MATH", "NORMAL_MAP",
             "HUE_SAT", "OBJECT_INFO", "MAP_RANGE", "ATTRIBUTE", "TEX_COORD", "MAPPING"}
    for n in nt.nodes:
        if n.type not in known: d["notes"].append("node " + n.type)

    def inp(name):
        s = b.inputs.get(name)
        return s

    def val(name, default):
        s = inp(name)
        if s is None or s.is_linked: return default
        v = s.default_value
        return list(v) if hasattr(v, "__len__") else float(v)

    d["metallic"] = val("Metallic", 0.0)
    d["specular"] = val("Specular IOR Level", 0.5)
    d["roughness"] = val("Roughness", 0.5)
    bc = val("Base Color", None)
    if bc is not None: d["base_color"] = bc
    # base colour chain
    fn, fs = _link_from(nt, b, "Base Color")
    for n in ([fn] + list(_upstream(nt, fn)) if fn else []):
        if n.type == "TEX_IMAGE" and n.image and d["base_map"] is None:
            d["base_map"] = n.image.name
        elif n.type == "VERTEX_COLOR":
            d["vertex_color"] = True
        elif n.type == "HUE_SAT":
            d["hsv"] = [_r(n.inputs[i].default_value) for i in range(3)]   # hue, saturation, value
        elif n.type == "MAP_RANGE" and any(x.type == "OBJECT_INFO" for x in _upstream(nt, n)):
            d["jitter"] = [_r(n.inputs[3].default_value), _r(n.inputs[4].default_value)]
        elif n.type == "MIX" and n.blend_type not in ("MULTIPLY",) and n.data_type == "RGBA":
            d["notes"].append("base colour mix " + n.blend_type)
    # flat colour mixed with vertex colour (no image): read the constant input of the multiply
    if fn is not None and fn.type == "MIX" and d["base_map"] is None:
        for i in (6, 7):
            if not fn.inputs[i].is_linked: d["base_color"] = list(fn.inputs[i].default_value)
    # roughness
    fn, fs = _link_from(nt, b, "Roughness")
    if fn is not None:
        if fn.type == "MATH" and fn.operation == "MULTIPLY":
            src = next((l.from_node for l in nt.links if l.to_node == fn), None)
            k = [i.default_value for i in fn.inputs[:2] if not i.is_linked]
            if src is not None and src.type == "TEX_IMAGE":
                d["rough_map"] = src.image.name; d["rough_scale"] = _r(k[0] if k else 1.0)
            else: d["notes"].append("roughness math from " + (src.type if src else "?"))
        elif fn.type == "TEX_IMAGE":
            d["rough_map"] = fn.image.name
        else: d["notes"].append("roughness from " + fn.type)
    # normal
    fn, fs = _link_from(nt, b, "Normal")
    if fn is not None:
        if fn.type == "NORMAL_MAP":
            t, _ = _link_from(nt, fn, "Color")
            if t is not None and t.type == "TEX_IMAGE": d["normal_map"] = t.image.name
            d["normal_strength"] = _r(fn.inputs["Strength"].default_value)
        else: d["notes"].append("normal from " + fn.type)
    # emission
    es = inp("Emission Strength"); ec = inp("Emission Color")
    if es is not None:
        fn, _ = _link_from(nt, b, "Emission Strength")
        if fn is not None and fn.type == "MATH" and any(x.type == "ATTRIBUTE" for x in [fn] + list(_upstream(nt, fn))):
            at = next(x for x in [fn] + list(_upstream(nt, fn)) if x.type == "ATTRIBUTE")
            cn, _ = _link_from(nt, b, "Emission Color")
            cols = [list(cn.inputs[i].default_value) for i in (6, 7)] if cn is not None and cn.type == "MIX" else None
            d["rim"] = {"attribute": at.attribute_name, "op": fn.operation,
                        "k": [_r(i.default_value) for i in fn.inputs[1:3]], "colors": cols}
        elif fn is not None:
            d["notes"].append("emission strength from " + fn.type)
        else:
            d["emission_strength"] = float(es.default_value)
            if not ec.is_linked: d["emission"] = list(ec.default_value)[:3]
            else:
                cn, _ = _link_from(nt, b, "Emission Color")
                if cn is not None and cn.type == "TEX_IMAGE": d["emission_map"] = cn.image.name
                elif cn is not None: d["notes"].append("emission colour from " + cn.type)
    # alpha
    fn, fs = _link_from(nt, b, "Alpha")
    if fn is not None:
        if fn.type == "TEX_IMAGE":
            # Blender's hashed alpha dithers partial alpha (thin web strands read as see-through): blend in Unity
            d["alpha"] = "blend" if m.blend_method in ("HASHED", "BLEND") else "clip"
            d["alpha_map"] = fn.image.name
        else: d["notes"].append("alpha from " + fn.type)
    elif val("Alpha", 1.0) < 0.999:
        d["alpha"] = "blend"; d["base_color"][3] = val("Alpha", 1.0)
    # cut-outs built as Mix Shader(Transparent, surface) with Fac = image alpha > threshold (foliage, leaves)
    for n in nt.nodes:
        if n.type != "MIX_SHADER" or not n.inputs[1].is_linked: continue
        if n.inputs[1].links[0].from_node.type != "BSDF_TRANSPARENT" or not n.inputs[0].is_linked: continue
        f = n.inputs[0].links[0].from_node
        if f.type == "MATH" and f.operation == "GREATER_THAN" and f.inputs[0].is_linked:
            src = f.inputs[0].links[0]
            if src.from_node.type == "TEX_IMAGE" and src.from_socket.name in ("Alpha", "Color"):
                d["alpha"] = "clip"; d["alpha_map"] = src.from_node.image.name
                d["alpha_channel"] = "a" if src.from_socket.name == "Alpha" else "r"
                d["cutoff"] = _r(f.inputs[1].default_value)
                d["notes"] = [x for x in d["notes"] if x not in ("node MIX_SHADER", "node BSDF_TRANSPARENT")]
        if any(x.type == "BSDF_TRANSLUCENT" for x in nt.nodes):
            d["translucent"] = True
            for mx in nt.nodes:      # Mix Shader(fac, surface, translucent): the translucent share of the shading
                if mx.type == "MIX_SHADER" and not mx.inputs[0].is_linked:
                    src = [i.links[0].from_node.type if i.is_linked else None for i in mx.inputs[1:3]]
                    if "BSDF_TRANSLUCENT" in src:
                        f = mx.inputs[0].default_value
                        d["translucency"] = _r(f if src[1] == "BSDF_TRANSLUCENT" else 1 - f)
            d["notes"] = [x for x in d["notes"] if x not in ("node BSDF_TRANSLUCENT", "node MIX_SHADER")]
    _moss(nt, b, d)
    if d.get("moss") is None and any(n.type == "TEX_COORD" and any(o.is_linked for o in n.outputs if o.name != "UV")
                                     for n in nt.nodes):
        # world / object projected (terrain, stair, river water): needs its own Unity shader, see UNITY_EXPORT
        _projected(m, nt, b, d)
    return d


def _projected(m, nt, b, d):
    """object-space projected materials: the vk_terrain recipes, ported as MedievalKit/KitTerrain keyword modes"""
    imgs = sorted({n.image.name for n in nt.nodes if n.type == "TEX_IMAGE" and n.image})
    ctl = next((n for n in nt.nodes if n.type == "MAPPING" and n.label == "CTL_MAP"), None)
    nm = m.name
    if ctl is not None or any("GroundCtl" in i for i in imgs): recipe = "terrain"
    elif "Stair" in nm: recipe = "stair"
    elif "Water" in nm: recipe = "water"
    elif any(n.type == "TEX_IMAGE" for n in nt.nodes): recipe = "paving"
    else: recipe = None
    d["shader"] = "projected"; d["recipe"] = recipe
    d["images"] = imgs
    d["base_color"] = [_r(x) for x in m.diffuse_color]
    d["base_map"] = d["normal_map"] = d["rough_map"] = None
    d["vertex_color"] = False; d["alpha"] = "opaque"; d["notes"] = []
    if recipe is None:
        d["notes"] = ["projected material with no KitTerrain recipe: placeholder colour"]
    if ctl is not None:
        sc_ = ctl.inputs["Scale"].default_value
        d["ctl_scale"] = [sc_[0], sc_[1]]
    if recipe == "paving":
        d["box"] = any(n.type == "TEX_IMAGE" and n.projection == "BOX" for n in nt.nodes)
        sv = next((n for n in nt.nodes if n.type == "VECT_MATH" and n.operation == "SCALE"), None)
        d["proj_scale"] = _r(sv.inputs["Scale"].default_value) if sv else 0.25
        d["roughness"] = _r(b.inputs["Roughness"].default_value)
        bp = next((n for n in nt.nodes if n.type == "BUMP"), None)
        d["bump_strength"] = _r(bp.inputs["Strength"].default_value) if bp else 0.5
    if recipe == "water":
        d["alpha"] = "blend"; d["base_color"][3] = _r(b.inputs["Alpha"].default_value)


def _moss(nt, b, d):
    """the mossy_material pattern (vk_mat): moss mixed in where world normal z + moss height noise passes a
    smoothstep, gated by the vertex colour's alpha; the moss maps sit on a Mapping (tile scale) of the UVs"""
    geo = [n for n in nt.nodes if n.type == "NEW_GEOMETRY"]
    mapn = [n for n in nt.nodes if n.type == "MAPPING"]
    mr = [n for n in nt.nodes if n.type == "MAP_RANGE"]
    if not (geo and mapn and mr): return
    mp = mapn[0]
    moss = {}
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.inputs[0].is_linked and n.inputs[0].links[0].from_node == mp:
            suf = n.image.name.rsplit("_", 1)[-1]
            moss[{"BC": "moss_map", "N": "moss_normal", "R": "moss_rough", "H": "moss_height"}.get(suf, "x")] = n.image.name
    if "moss_map" not in moss: return
    bases = {}
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name not in moss.values():
            suf = n.image.name.rsplit("_", 1)[-1]
            bases[suf] = n.image.name
    hh = next((n for n in nt.nodes if n.type == "MATH" and n.operation == "MULTIPLY_ADD"), None)
    r = mr[0]
    nm = next((n for n in nt.nodes if n.type == "NORMAL_MAP"), None)
    d["moss"] = {**moss, "tile": _r(mp.inputs["Scale"].default_value[0]),
                 "noise": [_r(hh.inputs[1].default_value), _r(hh.inputs[2].default_value)] if hh else [0, 0],
                 "range": [_r(r.inputs["From Min"].default_value), _r(r.inputs["From Max"].default_value)],
                 "gate_vertex_alpha": any(l.from_socket.name == "Alpha" and l.from_node.type == "VERTEX_COLOR" for l in nt.links)}
    d["base_map"] = bases.get("BC"); d["normal_map"] = bases.get("N"); d["rough_map"] = bases.get("R")
    d["rough_scale"] = 1.0; d["vertex_color"] = True
    if nm is not None: d["normal_strength"] = _r(nm.inputs["Strength"].default_value)
    d["notes"] = []


_BAKED = set()
_SIMPLE_BASE = {"TEX_IMAGE", "UVMAP", "VERTEX_COLOR", "MAP_RANGE", "OBJECT_INFO"}


def needs_bake(m, socket):
    """True when the network feeding a BSDF socket is more than image x vertex colour (x jitter):
    tints, HSV, masks, separate/greyscale tricks. Those are baked to a texture instead of ported."""
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    fn, _ = _link_from(nt, b, socket)
    if fn is None: return False
    nodes = [fn] + list(_upstream(nt, fn))
    imgs = [n for n in nodes if n.type == "TEX_IMAGE"]
    if bake_blocker(nodes): return False
    for n in nodes:
        if n.type == "MIX":
            if n.blend_type != "MULTIPLY": return True
            # a multiply by a constant colour (a tint) is baked too, unless it is the flat-colour case
            if imgs and any(not n.inputs[i].is_linked for i in (6, 7)): return True
        elif n.type == "MATH" and socket == "Roughness" and n.operation == "MULTIPLY":
            continue                                   # roughness map x constant: KitLit's _RoughScale
        elif n.type not in _SIMPLE_BASE: return True
    return len(imgs) > 1


def bake_blocker(nodes):
    """why a network can't be baked over the UV square (it reads the surface, not just the UVs), or None"""
    for n in nodes:
        if n.type in ("NEW_GEOMETRY", "ATTRIBUTE", "LIGHT_PATH", "CAMERA", "TANGENT", "WIREFRAME", "LAYER_WEIGHT", "FRESNEL"):
            return n.type
        if n.type == "TEX_COORD" and any(o.is_linked for o in n.outputs if o.name != "UV"): return "TEX_COORD"
        if n.type == "OBJECT_INFO" and any(o.is_linked for o in n.outputs if o.name != "Random"): return "OBJECT_INFO"
    return None


def bake_socket(m, socket, size=None, alpha_from=None, alpha_channel="a"):
    """bake what a material feeds into a BSDF socket, over its UV square, with the vertex colour at white and
    Object Info random at 0.5 (both are applied by the Unity shader). Every kit material samples its images
    with the plain UVMap, so a unit quad bakes the network exactly. Returns the new image's name."""
    nm = f"T_VKX_{m.name[2:] if m.name.startswith('M_') else m.name}_{socket.replace(' ', '')}"
    if nm in _BAKED: return nm       # baked once per run (a fresh exec of this file bakes again)
    if size is None:
        ims = [n.image for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
        size = max([max(i.size) for i in ims] + [256])
    mc = m.copy(); mc.name = "VKX_BAKE_" + m.name
    nt = mc.node_tree
    for n in list(nt.nodes):
        if n.type == "VERTEX_COLOR":
            rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = (1, 1, 1, 1)
            for l in list(nt.links):
                if l.from_node == n: nt.links.new(rgb.outputs[0], l.to_socket)
        elif n.type == "OBJECT_INFO":
            v = nt.nodes.new("ShaderNodeValue"); v.outputs[0].default_value = 0.5
            for l in list(nt.links):
                if l.from_node == n: nt.links.new(v.outputs[0], l.to_socket)
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    src = next(l.from_socket for l in nt.links if l.to_node == b and l.to_socket.name == socket)
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(src, em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    img = bpy.data.images.get(nm)
    if img is not None:          # always a fresh image: size and alpha planes may have changed since last time
        bpy.data.images.remove(img)
    img = bpy.data.images.new(nm, size, size, alpha=alpha_from is not None)
    img.colorspace_settings.name = "sRGB" if socket in ("Base Color", "Emission Color") else "Non-Color"
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img
    for n in nt.nodes: n.select = False
    tn.select = True; nt.nodes.active = tn
    me = bpy.data.meshes.new("VKX_BAKE_Quad")
    me.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
    me.materials.append(mc)
    ob = bpy.data.objects.new("VKX_BAKE_Quad", me)
    sc = bpy.data.scenes.get("VKX_Export") or bpy.data.scenes.new("VKX_Export")
    sc.collection.objects.link(ob)
    win = bpy.context.window; prev = win.scene; eng = sc.render.engine
    try:
        win.scene = sc
        sc.render.engine = "CYCLES"
        sc.cycles.samples = 1; sc.cycles.device = "CPU"
        sc.render.bake.margin = 0
        with bpy.context.temp_override(window=win, scene=sc, view_layer=sc.view_layers[0]):
            for o2 in sc.objects: o2.select_set(o2 == ob)
            sc.view_layers[0].objects.active = ob
            bpy.ops.object.bake(type="EMIT")
    finally:
        sc.render.engine = eng; win.scene = prev
        bpy.data.objects.remove(ob); bpy.data.meshes.remove(me); bpy.data.materials.remove(mc)
    if alpha_from is not None:      # the cut-out's alpha rides in the baked colour map
        import numpy as np
        a = bpy.data.images[alpha_from]
        if tuple(a.size) != tuple(img.size):
            a = a.copy(); a.scale(*img.size)
        pa = np.empty(len(a.pixels), dtype=np.float32); a.pixels.foreach_get(pa)
        pb = np.empty(len(img.pixels), dtype=np.float32); img.pixels.foreach_get(pb)
        pb[3::4] = pa[{"r": 0, "g": 1, "b": 2, "a": 3}[alpha_channel]::4]
        img.pixels.foreach_set(pb)
        if a.name != alpha_from: bpy.data.images.remove(a)
    img.pack()
    _BAKED.add(img.name)
    return img.name


def export_image(name, done):
    """write a kit image as PNG into Art/Textures (packed bytes when packed, else a copy); returns the file name"""
    if name in done: return done[name]
    img = bpy.data.images[name]
    fn = re.sub(r"[^A-Za-z0-9_\-]", "_", name) + ".png"
    dst = os.path.join(_mk(VKX_TEX), fn)
    if img.packed_file is not None:
        data = img.packed_file.data
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"{name}: packed data is not a PNG")
    elif img.source == "GENERATED" or img.is_dirty:
        tmp = os.path.join(_mk(VKX_TEX), "_tmp_" + fn)
        img.save_render(tmp)      # writes with the image's colour space (sRGB for colour bakes)
        with open(tmp, "rb") as f: data = f.read()
        os.remove(tmp)
    else:
        src = bpy.path.abspath(img.filepath)
        with open(src, "rb") as f: data = f.read()
    if not os.path.exists(dst) or open(dst, "rb").read() != data:
        with open(dst, "wb") as f: f.write(data)
    done[name] = fn
    return fn


# ---------------------------------------------------------------- pieces
def _family_dir(pn):
    """Models/<kit>/<family>: VK (exterior, nature), VKI (interior side), VKT (terrain tiles)"""
    if pn.startswith("U_"): return os.path.join("Unique")
    m = re.match(r"SM_(VK[IT]?)_([A-Za-z]+)", pn)
    return os.path.join(m.group(1), m.group(2)) if m else "Misc"


def export_piece(me, report):
    """one FBX per master mesh, unused slots stripped, vki_rim baked to a 'Rim' UV channel"""
    pn = piece_name(me)
    keep = used_slots(me)
    d = os.path.join(_mk(VKX_MODELS), _family_dir(pn))
    path = os.path.join(_mk(d), pn + ".fbx")
    tmp_me = me.copy(); tmp_me.name = "VKX_TMP_" + pn
    # one submesh per used slot. FBX merges slots that share a material, but restyles (VAR/VARI) may change one
    # of them only, so a repeated material is exported as a temporary copy named '<name>__s<slot>'
    mats, fbx_names, slot_map, temps = [], [], {}, []
    for i in keep:
        m = me.materials[i]
        em = m
        if m is not None and m.name in [x.name for x in mats if x is not None]:
            em = m.copy(); em.name = f"{m.name}__s{i}"; temps.append(em)
        slot_map[i] = len(mats)
        mats.append(m); fbx_names.append(em.name if em else None)
    export_mats = [bpy.data.materials.get(n) if n else None for n in fbx_names]
    idx = [0] * len(tmp_me.polygons)
    tmp_me.polygons.foreach_get("material_index", idx)
    idx = [slot_map[i] for i in idx]
    tmp_me.materials.clear()
    for m in export_mats: tmp_me.materials.append(m)
    tmp_me.polygons.foreach_set("material_index", idx)
    tcol = "TCol" in tmp_me.color_attributes
    if tcol:    # terrain tiles: TCol (R AO, G rock, B rim, A wet) is their only vertex colour
        for c in [c for c in tmp_me.color_attributes if c.name != "TCol"]:
            tmp_me.color_attributes.remove(c)
        tmp_me.color_attributes.active_color = tmp_me.color_attributes["TCol"]
        tmp_me.color_attributes.render_color_index = 0
    rim = "vki_rim" in tmp_me.attributes
    if rim:     # the glow gradient goes into the vertex colour's alpha (only rim materials read it)
        a = tmp_me.attributes["vki_rim"]
        vals = [0.0] * len(tmp_me.vertices)
        a.data.foreach_get("value", vals)
        col = tmp_me.color_attributes.get("Col") or tmp_me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
        if col.domain == "CORNER":
            for loop in tmp_me.loops:
                c = col.data[loop.index].color
                col.data[loop.index].color = (c[0], c[1], c[2], max(0.0, min(1.0, vals[loop.vertex_index])))
        else:
            for i, v in enumerate(vals):
                c = col.data[i].color
                col.data[i].color = (c[0], c[1], c[2], max(0.0, min(1.0, v)))
    for a in [a for a in tmp_me.attributes if a.name.startswith("vki_")]:
        tmp_me.attributes.remove(a)
    bm = bmesh.new(); bm.from_mesh(tmp_me)      # triangulate as Blender renders it (Unity would re-split n-gons)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(tmp_me); bm.free()
    ob = bpy.data.objects.new(pn, tmp_me)
    sc = bpy.data.scenes.get("VKX_Export") or bpy.data.scenes.new("VKX_Export")
    sc.collection.objects.link(ob)
    win = bpy.context.window
    prev = win.scene
    try:
        win.scene = sc
        with bpy.context.temp_override(window=win, scene=sc, view_layer=sc.view_layers[0]):
            for o2 in sc.objects: o2.select_set(o2 == ob)
            sc.view_layers[0].objects.active = ob
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"},
                                     apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                                     axis_forward="-Z", axis_up="Y", bake_space_transform=True,
                                     mesh_smooth_type="FACE", use_mesh_modifiers=False, colors_type="LINEAR",
                                     use_custom_props=False, add_leaf_bones=False, bake_anim=False,
                                     path_mode="STRIP", embed_textures=False, use_tspace=True)
    finally:
        win.scene = prev
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(tmp_me)
        for t in temps: bpy.data.materials.remove(t)
    lo = [min(v.co[i] for v in me.vertices) for i in range(3)] if me.vertices else [0, 0, 0]
    hi = [max(v.co[i] for v in me.vertices) for i in range(3)] if me.vertices else [0, 0, 0]
    report["pieces"] += 1
    return {"name": pn, "fbx": os.path.relpath(path, VKX_PKG).replace("\\", "/"), "slot_map": {str(k): v for k, v in slot_map.items()},
            "materials": [m.name if m else None for m in mats], "fbx_names": fbx_names,
            "vertex_color": "TCol" if tcol else "Col", "rim": rim,
            "bounds_blender": [[_r(x, 4) for x in lo], [_r(x, 4) for x in hi]],
            "tris": sum(len(p.vertices) - 2 for p in me.polygons),
            "props": _props(master_object(me)) if master_object(me) is not None else {}}


# ---------------------------------------------------------------- placements
_ORIGIN = [Matrix.Identity(4)]      # set by vkx_export_level(origin=...): the level is exported relative to it


def to_unity(mw):
    """Blender world matrix -> Unity position, rotation (x, y, z, w), scale"""
    loc, rot, sca = (_ORIGIN[0] @ mw).decompose()
    mu = C @ rot.to_matrix().to_4x4() @ CI
    q = mu.to_quaternion()
    p = C @ loc
    return [_r(p.x), _r(p.y), _r(p.z)], [_r(q.x, 6), _r(q.y, 6), _r(q.z, 6), _r(q.w, 6)], \
        [_r(sca.x), _r(sca.z), _r(sca.y)]


def _light(o):
    L = o.data
    return {"type": L.type, "color": [_r(c) for c in L.color], "energy": _r(L.energy),
            "radius": _r(getattr(L, "shadow_soft_size", 0)), "shadow": bool(L.use_shadow),
            "spot_size": _r(math.degrees(getattr(L, "spot_size", 0))) if L.type == "SPOT" else None,
            "spot_blend": _r(getattr(L, "spot_blend", 0)) if L.type == "SPOT" else None}


def _vfov(cd, sc):
    aspect = sc.render.resolution_x * sc.render.pixel_aspect_x / (sc.render.resolution_y * sc.render.pixel_aspect_y)
    fit = cd.sensor_fit
    if fit == "AUTO": fit = "HORIZONTAL" if aspect >= 1 else "VERTICAL"
    if fit == "VERTICAL": return 2 * math.atan(cd.sensor_height / 2 / cd.lens)
    sw = cd.sensor_width
    return 2 * math.atan(sw / 2 / cd.lens / aspect)


def _world(w):
    """world background colour x strength (the ambient light), when it is a plain Background node"""
    if w is None: return None
    if w.use_nodes:
        nt = w.node_tree
        # Light Path trick: Mix Shader(Fac = Is Camera Ray, lighting background, camera background)
        mix = next((n for n in nt.nodes if n.type == "MIX_SHADER" and n.inputs[0].is_linked
                    and n.inputs[0].links[0].from_node.type == "LIGHT_PATH"
                    and n.inputs[0].links[0].from_socket.name == "Is Camera Ray"), None)
        if mix is not None and all(i.is_linked and i.links[0].from_node.type == "BACKGROUND" for i in mix.inputs[1:3]):
            lit, cam = (i.links[0].from_node for i in mix.inputs[1:3])
            if not any(x.is_linked for b in (lit, cam) for x in b.inputs[:2]):
                return {"color": [_r(x) for x in lit.inputs[0].default_value][:3], "strength": _r(lit.inputs[1].default_value),
                        "camera_color": [_r(x * cam.inputs[1].default_value) for x in cam.inputs[0].default_value][:3],
                        "linked": False}
        if any(n.type in ("TEX_SKY", "TEX_ENVIRONMENT", "TEX_COORD") for n in nt.nodes):
            return world_probe(w)
        bg = next((n for n in nt.nodes if n.type == "BACKGROUND"), None)
        if bg is not None:
            c = bg.inputs["Color"]; s = bg.inputs["Strength"]
            return {"color": [_r(x) for x in c.default_value][:3], "strength": _r(s.default_value),
                    "linked": c.is_linked or s.is_linked}
    return {"color": [_r(x) for x in w.color], "strength": 1.0, "linked": False}


def material_signature(m):
    """what a material's export depends on: its nodes (types, settings, unlinked inputs), links and images (with the
    packed data's size). Same signature = same analysis and bakes, so process_materials can skip it."""
    h = hashlib.md5()
    if not (m.use_nodes and m.node_tree):
        h.update(repr(tuple(m.diffuse_color)).encode()); return h.hexdigest()
    nt = m.node_tree
    for n in sorted(nt.nodes, key=lambda n: n.name):
        h.update(f"{n.name}|{n.type}|".encode())
        for a in ("blend_type", "data_type", "operation", "interpolation_type", "projection", "attribute_name",
                  "layer_name", "uv_map", "label"):
            if hasattr(n, a): h.update(f"{a}={getattr(n, a)}|".encode())
        if n.type == "TEX_IMAGE" and n.image:
            im = n.image
            h.update(f"img={im.name}|{im.packed_file.size if im.packed_file else im.filepath}|{im.colorspace_settings.name}|".encode())
        for i in n.inputs:
            if not i.is_linked and hasattr(i, "default_value"):
                v = i.default_value
                h.update(repr(tuple(v) if hasattr(v, "__len__") else v).encode())
    for l in nt.links:
        h.update(f"{l.from_node.name}.{l.from_socket.identifier}>{l.to_node.name}.{l.to_socket.identifier}|".encode())
    h.update(f"{m.blend_method}|{m.use_backface_culling}".encode())
    return h.hexdigest()


def _files_exist(d):
    names = [d.get(k) for k in ("base_map", "normal_map", "rough_map", "alpha_map", "emission_map")]
    names += list((d.get("images") or {}).values()) if isinstance(d.get("images"), dict) else []
    names += [v for k, v in (d.get("moss") or {}).items() if k.startswith("moss_") and isinstance(v, str)]
    return all(os.path.exists(os.path.join(VKX_TEX, n)) for n in names if n)


def process_materials(mats, tex_done, report):
    """analyse every material named in mats (name -> dict), bake what needs baking, write the textures"""
    for mn in list(mats):
        if mn is None or mn not in bpy.data.materials: continue
        m = bpy.data.materials[mn]
        sig = material_signature(m)
        prev = mats.get(mn)
        if isinstance(prev, dict) and prev.get("sig") == sig and _files_exist(prev):
            continue        # unchanged since the last export: keep its entry and its bakes
        d = analyze_material(m)
        d["sig"] = sig
        special = d.get("moss") is not None or d.get("shader") is not None
        if m.use_nodes and any(n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes) and not special:
            bnode = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            own_alpha = d["alpha"] != "clip" or (d.get("alpha_channel", "a") == "a" and d["alpha_map"] == d["base_map"])
            if needs_bake(m, "Base Color") or not own_alpha:     # a separate cut-out mask rides in the baked map
                d["base_map"] = bake_socket(m, "Base Color", alpha_from=d["alpha_map"] if d["alpha"] == "clip" else None,
                                            alpha_channel=d.get("alpha_channel", "a"))
                d["base_color"][:3] = [1, 1, 1]; d["baked"] = True
                d["notes"] = [n for n in d["notes"] if not n.startswith(("base colour", "node RGBTOBW", "node SEPARATE", "node HUE", "node SEPXYZ", "node COMBXYZ"))]
                d["hsv"] = None
            else:
                fn, _ = _link_from(m.node_tree, bnode, "Base Color")
                why = bake_blocker([fn] + list(_upstream(m.node_tree, fn))) if fn is not None else None
                if why: d["notes"] = [f"base colour reads {why}: painted map kept as is"]
            if needs_bake(m, "Emission Color"):
                d["emission_map"] = bake_socket(m, "Emission Color"); d["emission"] = [1, 1, 1]
                d["notes"] = [n for n in d["notes"] if not n.startswith(("emission colour", "node SEPARATE", "node SEPXYZ"))]
            if needs_bake(m, "Roughness"):
                d["rough_map"] = bake_socket(m, "Roughness"); d["rough_scale"] = 1.0
            if any(n.type == "LIGHT_PATH" for n in m.node_tree.nodes):
                d["no_shadow"] = True       # 'Is Shadow Ray -> Transparent': the surface casts no shadow
                d["notes"] = [n for n in d["notes"] if n not in ("node LIGHT_PATH", "node BSDF_TRANSPARENT", "node MIX_SHADER")]
        for k in ("base_map", "normal_map", "rough_map", "alpha_map", "emission_map"):
            if d.get(k): d[k] = export_image(d[k], tex_done)
        if d.get("images"):
            d["images"] = {i: export_image(i, tex_done) for i in d["images"]}
        if d.get("moss"):
            for k in ("moss_map", "moss_normal", "moss_rough", "moss_height"):
                if d["moss"].get(k): d["moss"][k] = export_image(d["moss"][k], tex_done)
        mats[mn] = d
        if d["notes"]: report["notes"][mn] = d["notes"]


def world_probe(w, res=(64, 32)):
    """a world with a node network (sky texture, Light Path tricks): render it panoramically with Cycles and average it
    into sky / horizon / ground colours for Unity's trilight ambient. The lighting branch is used (Is Camera Ray = 0);
    the camera branch gives the clear colour."""
    import tempfile
    out = {}
    for branch, cam_ray in (("light", 0.0), ("camera", 1.0)):
        wc = w.copy(); nt = wc.node_tree
        for l in list(nt.links):
            if l.from_node.type == "LIGHT_PATH":
                sock, out_name = l.to_socket, l.from_socket.name
                nt.links.remove(l)
                sock.default_value = cam_ray if out_name == "Is Camera Ray" else 0.0
        sc = bpy.data.scenes.new("VKX_WorldProbe"); sc.world = wc
        cd = bpy.data.cameras.new("VKX_ProbeCam"); cd.type = "PANO"
        try: cd.panorama_type = "EQUIRECTANGULAR"
        except Exception: cd.cycles.panorama_type = "EQUIRECTANGULAR"
        cam = bpy.data.objects.new("VKX_ProbeCam", cd); sc.collection.objects.link(cam); sc.camera = cam
        cam.rotation_euler = (math.radians(90), 0, 0)
        sc.render.engine = "CYCLES"; sc.cycles.samples = 4; sc.cycles.device = "CPU"
        sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
        sc.render.image_settings.file_format = "OPEN_EXR"; sc.view_settings.view_transform = "Standard"
        fp = os.path.join(tempfile.gettempdir(), f"vkx_probe_{branch}.exr")
        sc.render.filepath = fp
        try:
            bpy.ops.render.render(write_still=True, scene=sc.name)
            im = bpy.data.images.load(fp, check_existing=False)
            import numpy as np
            a = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(a)
            a = a.reshape(res[1], res[0], 4)[..., :3]; bpy.data.images.remove(im)
        finally:
            bpy.data.scenes.remove(sc); bpy.data.objects.remove(cam); bpy.data.cameras.remove(cd); bpy.data.worlds.remove(wc)
        h = res[1]      # image rows bottom-up: row 0 = straight down
        out[branch] = {"ground": a[: h // 3].mean(axis=(0, 1)).tolist(), "equator": a[h // 3: 2 * h // 3].mean(axis=(0, 1)).tolist(),
                       "sky": a[2 * h // 3:].mean(axis=(0, 1)).tolist(), "mean": a.mean(axis=(0, 1)).tolist()}
    L, Cm = out["light"], out["camera"]
    return {"color": [_r(x) for x in L["mean"]], "strength": 1.0, "linked": False, "probe": True,
            "trilight": {k: [_r(x) for x in L[k]] for k in ("sky", "equator", "ground")},
            "camera_color": [_r(x) for x in Cm["equator"]]}


def vkx_export_level(scene_name, objects=None, name=None, export_pieces=True, quiet=True, origin=None, world=None,
                     materials=True, folder="Levels", extra=None):
    """export a scene (or a list of objects) as a level: pieces + materials + textures + Data/Levels/<name>.json.
    origin: a Blender point that becomes the level's (0, 0, 0) (the valley sits at x 1500).
    world: a world to describe instead of the scene's (lighting only)."""
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            return vkx_export_level(scene_name, objects, name, export_pieces, quiet=False, origin=origin, world=world,
                                    materials=materials, folder=folder, extra=extra)
    from mathutils import Vector
    _ORIGIN[0] = Matrix.Translation(-Vector(origin)) if origin is not None else Matrix.Identity(4)
    try:
        return _export_level(scene_name, objects, name, export_pieces, world, materials, folder, extra)
    finally:
        _ORIGIN[0] = Matrix.Identity(4)


def _export_level(scene_name, objects, name, export_pieces, world_override, do_materials=True, folder="Levels",
                  extra=None):
    sc = bpy.data.scenes[scene_name]
    for vl in sc.view_layers:       # a scene that was never on screen has stale matrix_world on new objects
        vl.update()
    objs = list(objects) if objects is not None else list(sc.objects)
    name = name or scene_name
    report = {"pieces": 0, "notes": {}}
    pieces = _load(os.path.join(VKX_DATA, "pieces.json"))
    mats = _load(os.path.join(VKX_DATA, "materials.json"))
    tex_done = {}
    placements, markers, lights, cams = [], [], [], []
    for o in objs:
        if o.type == "MESH":
            if o.hide_render: continue
            base = vkx_base_mesh(o)
            pn = piece_name(base)
            if (export_pieces or pn not in pieces) and pn not in report.setdefault("_done", set()):
                pieces[pn] = export_piece(base, report)
                report["_done"].add(pn)
                for mn in pieces[pn]["materials"]:
                    if mn: mats[mn] = None
            ov = material_overrides(o, base)
            for mn in ov.values(): mats[mn] = None
            p, q, s = to_unity(o.matrix_world)
            placements.append({"piece": pn, "name": o.name, "p": p, "r": q, "s": s, "mat": ov,
                               "props": _props(o), "coll": o.users_collection[0].name if o.users_collection else None})
        elif o.type == "EMPTY":
            p, q, s = to_unity(o.matrix_world)
            markers.append({"name": o.name, "p": p, "r": q, "s": s, "props": _props(o),
                            "coll": o.users_collection[0].name if o.users_collection else None})
        elif o.type == "LIGHT":
            if o.hide_render: continue
            p, q, s = to_unity(o.matrix_world)
            lights.append({"name": o.name, "p": p, "r": q, **_light(o), "props": _props(o),
                           "coll": o.users_collection[0].name if o.users_collection else None})
        elif o.type == "CAMERA":
            p, q, s = to_unity(o.matrix_world)
            cd = o.data
            cams.append({"name": o.name, "p": p, "r": q, "type": cd.type, "ortho_scale": _r(cd.ortho_scale),
                         "fov_deg": _r(math.degrees(_vfov(cd, sc))),
                         "clip": [_r(cd.clip_start), _r(cd.clip_end)], "active": o == sc.camera,
                         "aspect": _r(sc.render.resolution_x / sc.render.resolution_y)})
    if do_materials:      # materials named by this level are (re-)analysed, with their textures; else left for later
        process_materials(mats, tex_done, report)
    root = next((m for m in markers if m["name"].startswith("VKI_Root")), None)
    world = world_override or sc.world
    level = {"name": name, "scene": scene_name, "version": VKX_VERSION,
             "blender_origin": list((_ORIGIN[0].inverted() @ Matrix.Identity(4)).translation),
             "root": root["props"] if root else {}, "preset": (root or {}).get("props", {}).get("vki_preset"),
             "view_transform": sc.view_settings.view_transform, "exposure": sc.view_settings.exposure,
             "world": _world(world), "look": sc.view_settings.look,
             "placements": placements, "markers": markers, "lights": lights, "cameras": cams}
    if extra: level.update(extra)
    _mk(os.path.join(VKX_DATA, folder))
    _save(os.path.join(VKX_DATA, folder, name + ".json"), level)
    _save(os.path.join(VKX_DATA, "pieces.json"), pieces)
    _save(os.path.join(VKX_DATA, "materials.json"), mats)
    report.pop("_done", None)
    report.update({"level": name, "placements": len(placements), "markers": len(markers), "lights": len(lights),
                   "materials": sum(1 for v in mats.values() if v), "textures": len(tex_done)})
    return report


def _load(p):
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f: return json.load(f)
    return {}


def _save(p, d):
    _mk(os.path.dirname(p))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=1, sort_keys=True)


def vkx_export_pieces(collections=None, names=None, fresh=False, quiet=True):
    """every master piece in the kit's master collections (or only `names`), with its materials and textures.
    fresh=True starts pieces.json / materials.json over. Levels exported later reuse these pieces."""
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            return vkx_export_pieces(collections, names, fresh, quiet=False)
    if fresh:
        for f in ("pieces.json", "materials.json"):
            p = os.path.join(VKX_DATA, f)
            if os.path.exists(p): os.remove(p)
    pieces = _load(os.path.join(VKX_DATA, "pieces.json"))
    mats = _load(os.path.join(VKX_DATA, "materials.json"))
    report = {"pieces": 0, "notes": {}, "failed": {}}
    done = set()
    for cn in (collections or VKX_PIECE_COLLECTIONS):
        for o in sorted(bpy.data.collections[cn].objects, key=lambda o: o.name):
            if o.type != "MESH" or (names and o.name not in names): continue
            if master_object(o.data) is not o:          # helpers / temp objects parked in a master collection
                report.setdefault("skipped", []).append(o.name); continue
            pn = piece_name(o.data)
            if pn in done: continue
            done.add(pn)
            try:
                pieces[pn] = export_piece(o.data, report)
                pieces[pn]["collection"] = cn
            except Exception as e:
                report["failed"][pn] = repr(e)
                continue
            for mn in pieces[pn]["materials"]:
                if mn and mn not in mats: mats[mn] = None
    tex_done = {}
    try:
        process_materials(mats, tex_done, report)
    finally:
        _save(os.path.join(VKX_DATA, "pieces.json"), pieces)
        _save(os.path.join(VKX_DATA, "materials.json"), mats)
    report.update({"materials": sum(1 for v in mats.values() if v), "textures": len(tex_done),
                   "tris": sum(pieces[p]["tris"] for p in done if p in pieces)})
    return report


VKX_WORLD_JSON = os.path.join(VKX_PKG, "..", "..", "docs", "world_graph.json")   # the package sits in <repo>/unity


def vkx_valley_objects():
    """the valley level: its ground, the town, the valley's sun and fill, and the verification cameras"""
    objs = [*bpy.data.collections["VK_ValleyTerrain"].all_objects, *bpy.data.collections["VK_ValleyTown"].all_objects,
            bpy.data.objects["VK_Sun"], bpy.data.objects["VK_Fill"]]
    cams = bpy.data.collections.get("VKX_ValleyCams")
    return objs + (list(cams.objects) if cams else [])


def vkx_export_world(levels=None):
    """every level of docs/world_graph.json (or `levels`) under its world-graph name, so links resolve in Unity by
    name; the graph itself goes to Data/world.json. Materials are processed once at the end."""
    import shutil
    graph = _load(os.path.normpath(VKX_WORLD_JSON))
    names = levels or list(graph["levels"])
    out = {}
    try:
        for n in names:
            if n == "VK_ValleyTown":
                r = vkx_export_level("VillageKit", objects=vkx_valley_objects(), name=n, export_pieces=False,
                                     origin=(1500, 0, 0), materials=False)
            else:
                r = vkx_export_level(n, name=n, export_pieces=False, materials=False)
            out[n] = {"placements": r["placements"], "new_pieces": r["pieces"], "markers": r["markers"]}
        mats = _load(os.path.join(VKX_DATA, "materials.json")); rep = {"notes": {}}
        with contextlib.redirect_stdout(io.StringIO()):
            process_materials(mats, {}, rep)
        _save(os.path.join(VKX_DATA, "materials.json"), mats)
        out["_notes"] = rep["notes"]
    finally:
        vkx_cleanup()
    shutil.copyfile(os.path.normpath(VKX_WORLD_JSON), os.path.join(VKX_DATA, "world.json"))
    return out


def vkx_cleanup():
    """drop what an export leaves in the .blend: baked T_VKX_* images (re-baked every run) and the VKX_Export scene"""
    for im in [i for i in bpy.data.images if i.name.startswith("T_VKX_")]:
        bpy.data.images.remove(im)
    sc = bpy.data.scenes.get("VKX_Export")
    if sc is not None and bpy.context.window.scene != sc:
        bpy.data.scenes.remove(sc)
    _BAKED.clear()


VKX_SLICE = [("VKI_Tavern_F0", None, "Tavern_F0"), ("VKI_Dungeon_B4", None, "Dungeon_B4"),
             ("VKX_Slice_House", "scene", "Slice_House")]


def vkx_export_slice(fresh=True):
    """the vertical slice (a valley house, the tavern ground floor, cave level B4). fresh=True rewrites
    pieces.json / materials.json so they hold only what these levels use. Then in Unity: Tools > Medieval Kit > Build All."""
    if fresh:
        for f in ("pieces.json", "materials.json"):
            p = os.path.join(VKX_DATA, f)
            if os.path.exists(p): os.remove(p)
    out = []
    try:
        for scene, objs, name in VKX_SLICE:
            o = list(bpy.data.scenes[scene].objects) if objs == "scene" else objs
            out.append(vkx_export_level(scene, objects=o, name=name))
    finally:
        vkx_cleanup()
    return out


# ---------------------------------------------------------------- verification catalogs
def vkx_build_catalog(scene_name, collections, row_w=36.0, shot_w=24.0, gap=0.8):
    """a scene with every master of `collections` (linked copies, grouped by family, shelf-packed rows) lit like the
    valley, and orthographic 50-degree cameras tiling it. Exported as a level, Unity renders the same cameras
    (KitCapture.CaptureAll) for a side-by-side check of every piece."""
    sc = bpy.data.scenes.get(scene_name) or bpy.data.scenes.new(scene_name)
    for o in list(sc.collection.objects):
        if o.name.startswith(("CAT_", "VKX_CatCam")):
            cd = o.data if o.type == "CAMERA" else None
            bpy.data.objects.remove(o)
            if cd is not None and cd.users == 0: bpy.data.cameras.remove(cd)
    vk = bpy.data.scenes["VillageKit"]
    for n in ("VK_Sun", "VK_Fill"):
        if n not in sc.objects: sc.collection.objects.link(bpy.data.objects[n])
    sc.world = bpy.data.worlds.get("VKX_SliceWorld") or vk.world
    for a in ("view_transform", "look", "exposure", "gamma"): setattr(sc.view_settings, a, getattr(vk.view_settings, a))
    sc.render.engine = vk.render.engine
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    masters = []
    for cn in collections:
        for o in bpy.data.collections[cn].objects:
            if o.type == "MESH" and master_object(o.data) is o: masters.append(o)
    masters.sort(key=lambda o: (_family_dir(o.name), o.name))
    x = y = 0.0; row_d = 0.0; fam = None
    for o in masters:
        me = o.data
        if not me.vertices: continue
        lo = [min(v.co[i] for v in me.vertices) for i in range(3)]
        hi = [max(v.co[i] for v in me.vertices) for i in range(3)]
        w, d = hi[0] - lo[0], hi[1] - lo[1]
        f = _family_dir(o.name)
        if (fam is not None and f != fam and x > row_w * 0.6) or x + w > row_w:
            x = 0.0; y -= row_d + gap * 2; row_d = 0.0
        fam = f
        c = bpy.data.objects.new("CAT_" + o.name, me)
        for i, s in enumerate(o.material_slots):          # keep object-level material links
            if s.link == "OBJECT": c.material_slots[i].link = "OBJECT"; c.material_slots[i].material = s.material
        c.location = (x - lo[0], y - hi[1], -lo[2] if lo[2] < -0.5 else 0.0)
        sc.collection.objects.link(c)
        x += w + gap; row_d = max(row_d, d)
    depth = -y + row_d
    pitch = math.radians(50); shot_h = shot_w * 9 / 16
    n = 0
    yy = 0.0
    while yy > -depth - 1:
        xx = 0.0
        while xx < row_w:
            cd = bpy.data.cameras.new(f"VKX_CatCam_{n:02d}"); cd.type = "ORTHO"; cd.ortho_scale = shot_w; cd.clip_end = 500
            cam = bpy.data.objects.new(f"VKX_CatCam_{n:02d}", cd)
            tx, ty = xx + shot_w / 2, yy - shot_h / math.sin(pitch) / 2
            dist = 32.0     # inside URP's 50 m shadow distance (a far ortho camera renders without shadows)
            cam.location = (tx, ty - math.cos(pitch) * dist, math.sin(pitch) * dist)
            cam.rotation_euler = (math.radians(90) - pitch, 0, 0)
            sc.collection.objects.link(cam)
            if n == 0: sc.camera = cam
            n += 1; xx += shot_w
        yy -= shot_h / math.sin(pitch)
    return {"pieces": len(masters), "cameras": n, "size": [row_w, round(depth, 1)]}


def vkx_render_cameras(scene_name, out_dir, percent=50, prefix="VKX_CatCam"):
    """render every camera named prefix* (or the scene camera) of a scene to out_dir/blender_<scene>_<cam>.png"""
    sc = bpy.data.scenes[scene_name]
    cams = sorted([o for o in sc.objects if o.type == "CAMERA" and o.name.startswith(prefix)], key=lambda o: o.name) or [sc.camera]
    prev_cam, prev_pct = sc.camera, sc.render.resolution_percentage
    sc.render.resolution_percentage = percent
    out = []
    try:
        for c in cams:
            sc.camera = c
            sc.render.filepath = os.path.join(out_dir, f"blender_{scene_name}_{c.name}.png")
            bpy.ops.render.render(write_still=True, scene=sc.name)
            out.append(sc.render.filepath)
    finally:
        sc.camera, sc.render.resolution_percentage = prev_cam, prev_pct
    return out


# ---------------------------------------------------------------- generator rules
def vkx_export_house_rules():
    """Data/house_rules.json for Unity's KitHouseGenerator (a port of vk_helpers.build_house_v / random_style):
    the grid, the pieces that fill each role, and the style table (style kind -> option -> the material that replaces
    that kind's Blender slot; null = the piece's own material). Every variant material is created and exported, so
    styles the valley never used are available too."""
    gk = {}; exec(bpy.data.texts["vk_kit"].as_string(), gk); kit = gk["vk_kit_ns"]()
    VM, SLOT = kit["VARIANT_MATS"], kit["SLOT"]
    variants = {}
    for kind, opts in VM.items():
        variants[kind] = {}
        for opt in opts:
            m = kit["variant_mat"](kind, opt)
            base = {"plaster": "M_VK_Plaster", "shutter": "M_VK_Shutter_Teal", "roof": "M_VK_RoofRed",
                    "cloth": "M_VK_Cloth_Red", "stone": "M_VK_Stone"}[kind]
            variants[kind][opt] = None if m.name == base else m.name
    roles = {
        "ground_wall": {g: {"D": f"SM_VK_Wall_{g}_Door", "W": f"SM_VK_Wall_{g}_Window", ".": f"SM_VK_Wall_{g}"}
                        for g in ("Stone", "Plaster")},
        "ground_corner": {g: f"SM_VK_Corner_{g}" for g in ("Stone", "Plaster")},
        "ground_inner_corner": {g: f"SM_VK_InnerCorner_{g}" for g in ("Stone", "Plaster")},     # L-houses (build_L_v)
        "upper_inner_corner": ["SM_VK_InnerCorner_Timber"],
        "upper_wall_window": ["SM_VK_Wall_Timber_Window"],
        "upper_wall_plain": ["SM_VK_Wall_Timber", "SM_VK_Wall_Timber_X", "SM_VK_Wall_Timber_K"],
        "upper_corner": ["SM_VK_Corner_Timber"],
        "roof": {"tile": {"gable": "SM_VK_Roof_Gable", "mid": "SM_VK_Roof_Mid", "hip": "SM_VK_Roof_Hip",
                          "lcorner": "SM_VK_Roof_LCorner"},
                 "thatch": {"gable": "SM_VK_RoofThatch_Gable", "mid": "SM_VK_RoofThatch_Mid", "hip": "SM_VK_RoofThatch_Hip"}},
        "chimney": ["SM_VK_Chimney"], "dormer": ["SM_VK_Roof_Dormer"], "porch": ["SM_VK_Porch"],
        "flower_box": ["SM_VK_Prop_FlowerBox", "SM_VK_Prop_FlowerBox_Daisy"], "weeds": ["SM_VK_Deco_Weeds"],
        "ivy": ["SM_VK_Deco_Ivy_A", "SM_VK_Deco_Ivy_B"], "planter": ["SM_VK_Prop_Planter"], "lantern": ["SM_VK_Prop_Lantern"],
    }
    pieces = _load(os.path.join(VKX_DATA, "pieces.json"))

    def names(v):
        if isinstance(v, str): yield v
        elif isinstance(v, list):
            for x in v: yield from names(x)
        elif isinstance(v, dict):
            for x in v.values(): yield from names(x)
    missing = [n for n in names(roles) if n not in pieces]
    rules = {"version": VKX_VERSION, "source": "vk_helpers.build_house_v / build_L_v / _assemble / _dress / random_style",
             "cell": kit["CELL"], "h1": kit["H1"], "h2": kit["H2"], "depth": kit["DEPTH"],
             "slots": {k: v for k, v in SLOT.items()}, "variants": variants, "roles": roles,
             "random_style": {"ground": {"Stone": 0.6, "Plaster": 0.4},
                              "plaster": ["Cream", "White", "Ochre", "Rose", "Cream"],
                              "shutter": ["Teal", "Red", "Green", "Blue", "Natural"], "shutter_worn": 0.2,
                              "roof": ["Red", "Blue", "Green", "Red"], "roof_thatch_plaster": 2, "roof_thatch_stone": 1}}
    _save(os.path.join(VKX_DATA, "house_rules.json"), rules)
    mats = _load(os.path.join(VKX_DATA, "materials.json"))
    for kind in variants.values():
        for mn in kind.values():
            if mn and mn not in mats: mats[mn] = None
    rep = {"notes": {}}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            process_materials(mats, {}, rep)
    finally:
        _save(os.path.join(VKX_DATA, "materials.json"), mats)
        vkx_cleanup()
    return {"missing_pieces": missing, "variants": {k: len(v) for k, v in variants.items()}, "notes": rep["notes"]}


# ---------------------------------------------------------------- premade structures
# name, builder (in the kit namespace), keyword arguments: the one-off landmarks and the modules' buildings; whole
# quarters, demos and the town map are left out. Each is built in scene VKX_Structures (a row to look at) and exported
# relative to its own origin into Data/Structures/<name>.json; Unity makes Generated/Structures/<name>.prefab.
VKX_STRUCTURES = [
    ("Smithy", "build_smithy", {}), ("Inn", "build_inn", {}), ("TownHall", "build_townhall", {}),
    ("Chapel", "build_chapel", {}), ("Barn", "build_barn", {}), ("Windmill", "build_windmill", {}),
    ("GuardTower", "build_guardtower", {}), ("Bakery", "build_bakery", {}), ("Stable", "build_stable", {}),
    ("LogCabin", "build_logcabin", {}), ("Woodcutter", "build_woodcutter", {}), ("ForesterHut", "build_forester_hut", {}),
    ("Granary", "build_granary", {}), ("Storehouse", "build_storehouse", {}),
    ("Hovel_Cruck", "build_hovel", {"variant": "cruck"}), ("Hovel_Hip", "build_hovel", {"variant": "hip"}),
    ("Hovel_LeanTo", "build_hovel", {"variant": "leanto"}), ("Longhouse", "build_longhouse", {}),
    ("Pigsty", "build_pigsty", {}), ("Sheepfold", "build_sheepfold", {}),
    ("Mine", "build_mine", {}), ("CharcoalBurner", "build_charcoal_burner", {}), ("Tannery", "build_tannery", {}),
    ("DyersYard", "build_dyers_yard", {}), ("Brewery", "build_brewery", {}), ("Apiary", "build_apiary", {}),
    ("Pottery", "build_pottery", {}), ("MerchantHouse", "build_merchant_house", {}),
    ("TownhouseGablefront", "build_townhouse_gablefront", {}), ("CornerHouse", "build_corner_house", {}),
    ("Terrace", "build_terrace", {}), ("Watermill", "build_watermill", {}), ("FisherHut", "build_fisher_hut", {}),
    ("Smokehouse", "build_smokehouse", {}), ("Lavoir", "build_lavoir", {}),
    ("TowerHouse_Fortified", "build_tower_house", {"kind": "fortified"}),
    ("TowerHouse_Domestic", "build_tower_house", {"kind": "domestic"}),
    ("Camp", "build_camp", {}), ("SawpitYard", "build_sawpit_yard", {}), ("TrainingYard", "build_training_yard", {}),
    ("FestivalGreen", "build_festival_green", {}),
    ("ConstructionSite_0", "build_construction_site", {"stage": 0}),
    ("ConstructionSite_1", "build_construction_site", {"stage": 1}),
    ("ConstructionSite_2", "build_construction_site", {"stage": 2}),
    ("ConstructionSite_3", "build_construction_site", {"stage": 3}),
]


def vkx_build_structures(items=None, scene_name="VKX_Structures", gap=8.0):
    """build every structure into its own collection VKX_ST_<name> in `scene_name`, in a row along +X (fronts face -Y),
    each with a 50-degree camera VKX_StCam_<name>. Returns ([(name, collection, origin x, camera)], {name: error})."""
    from mathutils import Vector
    gk = {}; exec(bpy.data.texts["vk_kit"].as_string(), gk); kit = gk["vk_kit_ns"]()
    sc = bpy.data.scenes.get(scene_name) or bpy.data.scenes.new(scene_name)
    vk = bpy.data.scenes["VillageKit"]
    for n in ("VK_Sun", "VK_Fill"):
        if n not in sc.objects: sc.collection.objects.link(bpy.data.objects[n])
    sc.world = bpy.data.worlds.get("VKX_SliceWorld") or vk.world
    for a in ("view_transform", "look", "exposure", "gamma"): setattr(sc.view_settings, a, getattr(vk.view_settings, a))
    sc.render.engine = vk.render.engine
    sc.render.resolution_x, sc.render.resolution_y = 1280, 800
    out, cursor, errors = [], 0.0, {}
    for name, fn, kw in (items or VKX_STRUCTURES):
        cn = "VKX_ST_" + name
        old = bpy.data.collections.get(cn)
        if old is not None:
            for o in list(old.all_objects):
                d = o.data if o.type == "CAMERA" else None
                bpy.data.objects.remove(o)
                if d is not None and d.users == 0: bpy.data.cameras.remove(d)
            bpy.data.collections.remove(old)
        coll = bpy.data.collections.new(cn); sc.collection.children.link(coll)
        try:
            kit[fn](coll, (cursor, 0.0, 0.0), **kw)
        except Exception as e:
            errors[name] = repr(e); continue
        meshes = [o for o in coll.all_objects if o.type == "MESH"]
        if not meshes: errors[name] = "built nothing"; continue
        for vl in sc.view_layers: vl.update()
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
        y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
        z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
        shift = cursor - x0                      # the structure's left edge on the cursor
        for o in coll.all_objects:
            if o.parent is None: o.location.x += shift
        ox = cursor + shift                      # where its origin went
        cx = (x0 + x1) / 2 + shift
        size = max(x1 - x0, y1 - y0, (z1 - z0) * 1.2, 6.0)
        cd = bpy.data.cameras.new("VKX_StCam_" + name); cd.lens = 35; cd.clip_end = 500
        cam = bpy.data.objects.new("VKX_StCam_" + name, cd); coll.objects.link(cam)
        pitch = math.radians(50); dist = size * 1.35 + 4
        T = Vector((cx, (y0 + y1) / 2, z0 + (z1 - z0) * 0.35))
        cam.location = T + Vector((0, -math.cos(pitch) * dist, math.sin(pitch) * dist))
        cam.rotation_euler = (math.radians(90) - pitch, 0, 0)
        out.append((name, coll, ox, cam))
        cursor += (x1 - x0) + gap
    for vl in sc.view_layers: vl.update()
    return out, errors


def vkx_export_structures(items=None, scene_name="VKX_Structures"):
    """build (vkx_build_structures) and export every structure to Data/Structures/<name>.json, and the whole row as the
    level Structures_Showcase (with the cameras, for side-by-side checks)"""
    items = items or VKX_STRUCTURES
    builders = {n: f for n, f, k in items}
    built, errors = vkx_build_structures(items, scene_name)
    sc = bpy.data.scenes[scene_name]
    report = {}
    try:
        for name, coll, ox, cam in built:
            objs = [o for o in coll.all_objects if o.type != "CAMERA"]
            r = vkx_export_level(scene_name, objects=objs, name=name, export_pieces=False, origin=(ox, 0, 0),
                                 materials=False, folder="Structures",
                                 extra={"structure": name, "builder": builders[name]})
            report[name] = {"placements": r["placements"], "lights": r["lights"], "new_pieces": r["pieces"]}
        vkx_export_level(scene_name, objects=list(sc.objects), name="Structures_Showcase", export_pieces=False)
    finally:
        vkx_cleanup()
    return report, errors


# ---------------------------------------------------------------- interior rules (Unity KitRoom)
def _jsonify(v):
    """room records -> JSON: tuple keys become 'a|b|c', tuples lists"""
    if isinstance(v, dict):
        return {("|".join(str(x) for x in k) if isinstance(k, tuple) else str(k)): _jsonify(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_jsonify(x) for x in v]
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    return str(v)


def vkx_export_interior_rules():
    """Data/interior_rules.json for Unity's KitRoom (a port of vki_rooms: plan parser + layout + shell build): the
    grid, wall classes and heights, the families, post priority, the plan token tables, the style slots and every
    style value's material, and every VKI_ROOMS record with its VKI_PLANS plan (presets and the golden test).
    Every style material is created and exported."""
    g0 = {}; exec(bpy.data.texts["vki_core"].as_string(), g0); v = g0["vki_ns"]()
    styles = {}
    for key, tab in v["VKI_STYLE_MATS"].items():
        styles[key] = {val: mn for val, mn in tab.items()}
    gk = {}; exec(bpy.data.texts["vk_kit"].as_string(), gk); kit = gk["vk_kit_ns"]()
    for key, kind in (("shutter", "shutter"), ("cloth", "cloth"), ("cloth_b", "cloth")):
        styles[key] = {opt: kit["variant_mat"](kind, opt).name for opt in kit["VARIANT_MATS"][kind]}
    for key, tab in styles.items():               # make sure every style material exists in the .blend
        for val, mn in tab.items():
            try: v["vki_style_mat"](key, mn)
            except Exception: pass
    fams = {n: {"cls": f["cls"], "rake": bool(f.get("rake")), "rhythm": bool(f.get("rhythm")), "wall_a": f["wall_a"],
                "H": v["VKI_H_FULL"].get(n, f.get("H", 3.0))} for n, f in v["VKI_FAMILIES"].items()}
    # zones overlap and the first listed wins (vki_rooms_zone_map), but the JSON is saved with sorted keys: keep the order
    rooms = {n: dict(_jsonify(r), zone_order=list(r.get("zones", {}).keys())) for n, r in v["VKI_ROOMS"].items()}
    rules = {"version": VKX_VERSION, "source": "vki_rooms.vki_parse_plan / vki_rooms_layout / vki_build_scene",
             "ig": v["VKI_IG"], "t": v["VKI_T"], "cut_h": v["VKI_CUT_H"], "mid_hw": _jsonify(v["VKI_MID_HW"]),
             "cap_hw": v["VKI_CAP_HW"], "post_hw": v["VKI_POST_HW"], "proud_line": v["VKI_PROUD_LINE"],
             "post_z0": v["VKI_POST_Z0"], "post_top": v["VKI_POST_TOP"], "families": fams,
             "post_prio": v["VKI_POST_PRIO"], "tok_ew": _jsonify(v["VKI_ROOMS_TOK_EW"]),
             "tok_ns": _jsonify(v["VKI_ROOMS_TOK_NS"]), "own_family": v["VKI_ROOMS_OWN_FAMILY"],
             "gate_deg": v["VKI_ROOMS_GATE_DEG"], "slots": v["VKI_SLOT"], "styles": styles,
             "night_style": v["VKI_NIGHT_STYLE"], "reuse_style": v["VKI_REUSE_STYLE"],
             "reuse_style_night": v["VKI_REUSE_STYLE_NIGHT"], "codes": v["VKI_ROOMS_CODES"],
             "reuse": {n: {"mount": r.get("mount", "floor"), "fp": list(r.get("fp", (1, 1)))} for n, r in v["VKI_REUSE"].items()},
             "rooms": rooms, "plans": dict(v["VKI_PLANS"])}
    _save(os.path.join(VKX_DATA, "interior_rules.json"), rules)
    mats = _load(os.path.join(VKX_DATA, "materials.json"))
    for tab in styles.values():
        for mn in tab.values():
            if mn and mn not in mats and mn in bpy.data.materials: mats[mn] = None
    rep = {"notes": {}}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            process_materials(mats, {}, rep)
    finally:
        _save(os.path.join(VKX_DATA, "materials.json"), mats)
        vkx_cleanup()
    missing = sorted({mn for tab in styles.values() for mn in tab.values() if mn not in bpy.data.materials})
    return {"rooms": len(rooms), "style_keys": {k: len(t) for k, t in styles.items()}, "missing_materials": missing,
            "notes": rep["notes"]}
