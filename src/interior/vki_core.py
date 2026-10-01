# ===================== VKI CORE: the interior kit ("VillageInterior") =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (sections are quoted as §n).
# Bootstrap (any MCP call):
#   g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"]()
# vki_ns() = vk_kit_ns(terrain=False) + vki_core + every VKI_TEXTS entry present, in order.
# Every top-level name here starts with vki_/VKI_ (or is VKIKit): T18 checks it.
import bpy, bmesh, math, json, zlib, os, re, hashlib
from mathutils import Vector, Matrix
if "Kit" not in globals():                    # exec'd into an empty dict: pull in the exterior kit namespace first
    exec(bpy.data.texts["vk_kit"].as_string(), globals())
    globals().update(vk_kit_ns(terrain=False))

VKI_ROOT = r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit"
VKI_RENDERS = os.path.join(VKI_ROOT, "renders", "interior")
# load order of the package texts (vki_tex / vki_textiles are generators, executed on demand, not listed)
VKI_TEXTS = ["vki_fam_timber", "vki_floors", "vki_fam_stone", "vki_fam_board", "vki_fam_wattle", "vki_fam_ashlar",
             "vki_links", "vki_fam_dungeon", "vki_fam_ancient", "vki_fam_cave", "vki_fam_cavewall", "vki_fam_sewer", "vki_fam_water", "vki_fam_dwarf", "vki_props_home", "vki_props_tavern",
             "vki_props_smithy", "vki_props_chapel", "vki_props_dungeon", "vki_props_adventure", "vki_props_lair",
             "vki_rooms", "vki_rooms_dungeon", "vki_rooms_adventure", "vki_rooms_sewer", "vki_rooms_water", "vki_rooms_dwarf", "vki_props_poi", "vki_props_debris", "vki_fam_mine", "vki_rooms_mine", "vki_world", "vki_test"]


VKI_CORE_TEXTS = ("vki_fam_timber", "vki_floors", "vki_test")    # a failure here raises; package texts only warn


def vki_ns(strict=False):
    """fresh namespace: exterior kit (no terrain) + vki_core + the VKI_TEXTS that exist, in order.
    Several engineers share one Blender, so a package text that fails to load (e.g. a half-finished push) must not
    break everyone else's call: its error is recorded in g["VKI_LOAD_ERRORS"] ({text: message}) and printed, and
    loading goes on. Core texts, or strict=True, raise instead."""
    g = {}
    exec(bpy.data.texts["vk_kit"].as_string(), g)
    g = g["vk_kit_ns"](terrain=False)
    exec(bpy.data.texts["vki_core"].as_string(), g)
    errs = {}
    for t in VKI_TEXTS:
        if t not in bpy.data.texts:
            continue
        try:
            exec(compile(bpy.data.texts[t].as_string(), t, "exec"), g)
        except Exception as e:
            if strict or t in VKI_CORE_TEXTS:
                raise
            errs[t] = f"{type(e).__name__}: {e}"
            print(f"vki_ns: text {t} failed to load and was skipped: {errs[t]}")
    g["VKI_LOAD_ERRORS"] = errs
    return g


# ---------------------------------------------------------------- §2.1 grid and constants
VKI_TOWN = "VK_ValleyTown"                     # the valley's level id: the target of the underground's ways up (vki_world)
VKI_IG = 1.5                                   # interior grid
VKI_T = {"O": 0.50, "P": 0.30}                 # wall thickness by class
VKI_H_FULL = {"Timber": 3.0, "Stone": 3.0, "Board": 3.0, "Wattle": 2.4, "Ashlar": 4.5, "Dungeon": 3.0, "Bars": 3.0,
              "Ancient": 3.0, "Cave": 3.0, "Sewer": 3.0, "Dwarf": 3.0, "Mine": 3.0}
VKI_H_UPPER = 3.0                              # upper floors use 3.0
VKI_PROUD = 0.03
VKI_CAP_HW = {"O": 0.28, "P": 0.18}            # caps, rails, skirtings, oak members
VKI_POST_HW = {"O": 0.31, "P": 0.21}           # Corner posts (square)
VKI_POST_BEVEL = 0.02                          # max bevel on posts
VKI_MID_HW = {"O": (0.12, 0.31), "P": (0.10, 0.21)}   # Mid posts: (along the wall, across)
VKI_POST_Z0 = -0.30                            # posts run from -0.30 ...
VKI_POST_TOP = 0.04                            # ... to wall top + 0.04
VKI_NODE_FLAT = 0.32                           # no deformation within this distance of a piece-end node
VKI_OPEN_MIN = 0.33                            # clear openings lie in x in [0.33, L-0.33]
VKI_ENV_X = (0.02, 0.33)                       # surround envelope from each end node ...
VKI_ENV_Y = {"O": 0.30, "P": 0.20}             # ... |y| <= POST_HW - 0.01, z <= post top
VKI_FOOT_Z = -0.30                             # wall bodies continue below the floor
VKI_PROUD_LINE = {"O": 0.285, "P": 0.185}      # floor-standing wall-backed props put their back here
VKI_CUT_H = 1.00                               # cut height (top of the cap)
VKI_CUT_CAP = (0.90, 1.00)                     # cut cap band (the top may sag to 0.98)
VKI_FULL_CAP = 0.12                            # full cap: H-0.12 .. H
VKI_SOLE_TOP = 0.16                            # skirting / sole plate top
VKI_Z = {"floor": 0.0, "sill": 0.015, "overlay": 0.025, "threshold": 0.03, "skirting": 0.16, "dais": 0.20,
         "cut_cap": (0.88, 1.00), "cut_post": 1.04}   # reserved heights (§2.1)
VKI_SEED_BLEND = (0.65, 1.0)                   # below 0.65 every piece uses wobble seed A
VKI_CAM = {"pitch": 50.0, "yaw": 0.0, "lens": 38.0, "sensor": 36.0, "clip": (0.5, 80.0), "D": (14.0, 22.0)}
VKI_FLAGS = {"wobble": True, "sag": True}      # look gate G1 A/B switches (family builders read "sag")

# ---------------------------------------------------------------- §2.2 families (data only)
VKI_FAMILIES = {
    "Timber": dict(cls="O", H=3.0, wall_a="PlasterCream", cap="Hewn", base="oak sole plate 0-0.16",
                   cut_cap="oak mid-rail, CAP top (Hewn); also on Full", full_top="oak head plate",
                   posts="oak Corner; thin oak Mid; ENDGRAIN tops", b_variant="curved brace above 1.2",
                   rake=True, rhythm=True, prio=3, h_fit=3.0, sag=0.010),
    "Stone": dict(cls="O", H=3.0, wall_a="StoneIn", cap="StoneBlockIn", base=None,
                  cut_cap="StoneBlockIn coping in 0.75 m units, V-joints", full_top="same coping",
                  posts="Corner: quoin pier of StoneBlockIn blocks; Mid: thin dressed pilaster",
                  b_variant="pop-out stones above 1.2 (<= 0.06 proud)", rake=True, rhythm=False, prio=5, h_fit=3.0,
                  sag=0.0, coping_jitter=0.006),
    "Ashlar": dict(cls="O", H=4.5, wall_a="AshlarIn", cap="Dress", base=None,
                   cut_cap="DRESS string course, weathered top (also on Full)",
                   full_top="second string course 2.90-3.00, cornice H-0.12..H",
                   posts="Corner: clustered respond; Mid: shaft respond, Full only", b_variant=None,
                   rake=False, rhythm=False, prio=4, h_fit=3.97, sag=0.0),
    "Wattle": dict(cls="P", H=2.4, wall_a="PlasterDaub", cap="Hewn", base="oak sole beam 0-0.16",
                   cut_cap="hewn oak rail", full_top="sagging wall plate",
                   posts="Corner: crooked hewn post (bow <= 0.02); Mid: thin hewn post",
                   b_variant="bare INFILL (WattleIn) patch above 1.2", rake=True, rhythm=True, prio=2, h_fit=2.4,
                   sag=0.020, soot_z=1.4),
    "Board": dict(cls="P", H=3.0, wall_a="BoardsV", cap="Hewn", base=None, cut_cap="Hewn rail", full_top="Hewn rail",
                  posts="oak Corner and Mid", b_variant=None, rake=False, rhythm=True, prio=1, h_fit=3.0, sag=0.0),
    # dungeon kit (docs/DUNGEON_KIT.md, text vki_fam_dungeon)
    "Dungeon": dict(cls="O", H=3.0, wall_a="DungeonIn", cap="DungeonCap", base=None,
                    cut_cap="rough coping slabs in 0.75 m units, pale DungeonCap top", full_top="same coping",
                    posts="Corner: chamfered pier of dark dressed blocks; Mid: pilaster",
                    b_variant="pop-out blocks above 1.2", rake=True, rhythm=False, prio=6, h_fit=3.0, sag=0.0,
                    coping_jitter=0.010),
    "Bars": dict(cls="P", H=3.0, wall_a="DungeonIn", cap="DungeonCap", base="stone curb 0-0.14",
                 cut_cap=None, full_top="iron top rail under a stone lintel", posts="Corner / Mid: dressed stone piers",
                 b_variant=None, rake=False, rhythm=False, prio=0, h_fit=3.0, sag=0.0, no_cut=True),
    # adventure kit (docs/ADVENTURE_KIT.md): the ruined temple and the natural caves
    "Ancient": dict(cls="O", H=3.0, wall_a="AncientIn", cap="AncientCap", base=None,
                    cut_cap="weathered coping slabs in 0.75 m units", full_top="coping over a carved frieze course",
                    posts="Corner: monolithic pier with a capital; Mid: pilaster", b_variant="pop-out blocks",
                    rake=True, rhythm=False, prio=7, h_fit=3.0, sag=0.0, coping_jitter=0.012),
    # Cave: the rock-wall family for walled levels (vki_fam_cavewall), and the family of the cave maps' dual-grid
    # rock and ground tiles (vki_fam_cave: its slots, the camera's h_fit)
    "Cave": dict(cls="O", H=3.0, wall_a="CaveRock", cap="CaveCut", base=None,
                 cut_cap="the rock itself, sliced flat (CAP top)", full_top="sliced flat at 3.0, a ragged skyline",
                 posts="rock masses", b_variant="another rock face with a crystal vein", rake=True, rhythm=False,
                 prio=8, h_fit=3.0, sag=0.0),
    # sewer kit (docs/SEWER_KIT.md, text vki_fam_sewer): old wet brick on the Stone construction
    "Sewer": dict(cls="O", H=3.0, wall_a="SewerBrick", cap="SewerCap", base=None,
                  cut_cap="dressed stone coping in 0.75 m units, SewerCap top", full_top="same coping",
                  posts="Corner: brick pier with stone quoins; Mid: pilaster", b_variant="a barred drain low in face A",
                  rake=True, rhythm=False, prio=5, h_fit=3.0, sag=0.0, coping_jitter=0.010),
    # dwarf kit (docs/DWARF_KIT.md, text vki_fam_dwarf): halls cut into the mountain, granite ashlar with a plinth and a
    # gilded rune band
    "Dwarf": dict(cls="O", H=3.0, wall_a="DwarfIn", cap="DwarfCap", base="plinth course 0-0.28, 3 cm proud",
                  cut_cap="polished coping in 0.75 m units, DwarfCap top", full_top="coping over the gilded rune band",
                  posts="Corner: square pier with a stepped capital and a gold ring; Mid: pilaster",
                  b_variant="a carved relief: frame, lozenge, gold rune disc", rake=True, rhythm=False, prio=6,
                  h_fit=3.0, sag=0.0, coping_jitter=0.006),
    # mine kit (docs/MINE_KIT.md, text vki_fam_mine): timber lining for galleries in a cave map -- lagging boards on
    # both faces of a packed-rock core, hewn posts; partitions only (no rakes, no doors: a drift's mouth stays open)
    "Mine": dict(cls="O", H=3.0, wall_a="CaveRock", cap="Hewn", base=None,
                 cut_cap="a hewn cap beam 0.78-1.00 (CAP top)", full_top="a hewn wall plate 2.76-3.00 (CAP top)",
                 posts="Corner / Mid: hewn posts through the lining, end-grain tops", b_variant=None, rake=False,
                 rhythm=True, prio=4, h_fit=3.0, sag=0.0),
}
VKI_POST_PRIO = ["Cave", "Ancient", "Dwarf", "Dungeon", "Sewer", "Mine", "Stone", "Ashlar", "Timber", "Wattle", "Board",
                 "Bars"]  # §2.3

# ---------------------------------------------------------------- §4.1 slots
VKI_FLOOR, VKI_WALL_A, VKI_WALL_B, VKI_CAP, VKI_STONE_BLOCK_IN, VKI_BRICK, VKI_STRAW, VKI_ASH, VKI_TEXTILE, \
    VKI_WAX, VKI_FX, VKI_INFILL = range(55, 67)
VKI_NSLOTS = 67
VKI_TILE = {55: 3.0, 56: 1.5, 57: 1.5, 58: 1.2, 59: 1.5, 60: 1.5, 61: 1.5, 62: 0.75, 64: 1.0, 66: 1.5}  # 63, 65: own UVs
VKI_WORLD_LOCKED = (VKI_FLOOR, VKI_WALL_A, VKI_WALL_B, VKI_INFILL)
VKI_BANNED = (STONE, PLASTER, ASHLAR, FIELDSTONE, WATTLE, STONE_BLOCK, ROCK, MOSS, ROCK_MOSSY)
VKI_OVERRIDABLE = (WATER, WOOD, PLANKS, SHUTTER, CLOTH_A, CLOTH_B, WINDOW)   # whitelisted per-master overrides
VKI_SLOT_NAMES = {VKI_FLOOR: "FLOOR", VKI_WALL_A: "WALL_A", VKI_WALL_B: "WALL_B", VKI_CAP: "CAP",
                  VKI_STONE_BLOCK_IN: "STONE_BLOCK_IN", VKI_BRICK: "BRICK", VKI_STRAW: "STRAW", VKI_ASH: "ASH",
                  VKI_TEXTILE: "TEXTILE", VKI_WAX: "WAX", VKI_FX: "FX", VKI_INFILL: "INFILL"}
VKI_SLOT = {"floor": 55, "wall_a": 56, "wall_b": 57, "cap": 58, "infill": 66, "wood": WOOD, "planks": PLANKS,
            "shutter": SHUTTER, "cloth": CLOTH_A, "cloth_b": CLOTH_B, "window": WINDOW, "stained": STAINED,
            "glow": GLOW, "water": WATER}
VKI_GRIMES = ("wall", "floor", "prop", "none")


def vki_tile(mi):
    return VKI_TILE.get(mi, 1.0) if mi >= 55 else TILE.get(mi, 1.0)


# ---------------------------------------------------------------- small maths
def vki_smoothstep(e0, e1, x):
    """GLSL smoothstep; e0 > e1 gives the falling step (1 at e1, 0 at e0)"""
    if e0 == e1:
        return 1.0 if x >= e0 else 0.0
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def vki_lerp(a, b, t):
    return a + (b - a) * t


def vki_clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def vki_hash01(ix, iz, seed):
    """integer lattice hash -> [0, 1]; pure integer maths, identical in every session"""
    h = (ix * 374761393 + iz * 668265263 + (seed & 0xFFFFFFFF) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    return h / 4294967295.0


def vki_vnoise(u, w, seed):
    """smooth 2-D value noise in [0, 1] (lattice spacing 1, smoothstep fade); seed = crc32 integer"""
    i0, j0 = math.floor(u), math.floor(w)
    fu, fw = u - i0, w - j0
    su, sw = fu * fu * (3 - 2 * fu), fw * fw * (3 - 2 * fw)
    a, b = vki_hash01(i0, j0, seed), vki_hash01(i0 + 1, j0, seed)
    c, d = vki_hash01(i0, j0 + 1, seed), vki_hash01(i0 + 1, j0 + 1, seed)
    return vki_lerp(vki_lerp(a, b, su), vki_lerp(c, d, su), sw)


def vki_seed(s):
    """crc32 seed of a string (never Python's hash() of strings: it is salted per session)"""
    return zlib.crc32(s.encode())


def vki_rect_dist(x, z, h):
    """distance from (x, z) to the rectangle h = (x0, z0, x1, z1); 0 inside"""
    dx = max(h[0] - x, 0.0, x - h[2])
    dz = max(h[1] - z, 0.0, z - h[3])
    return math.hypot(dx, dz)


def vki_srgb(hexs):
    """'#RRGGBB' (display sRGB) -> linear RGB tuple"""
    def c(x):
        x /= 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return tuple(c(int(hexs[i:i + 2], 16)) for i in (1, 3, 5))


# ---------------------------------------------------------------- names
VKI_CLASS_TOKENS = {"Wall": "wall", "Post": "post", "Floor": "floor", "Stair": "link", "Apron": "link",
                    "Leaf": "leaf", "Prop": "prop", "Overlay": "overlay", "Rug": "overlay", "Runner": "overlay",
                    "RushMat": "overlay", "FX": "fx", "Test": "test",
                    "Pit": "pit",          # adventure kit: spike pits, chasms, pools -- they replace the floor over their cells
                    "Rock": "rock",        # adventure kit: dual-grid cave rock tiles (vki_fam_cave)
                    "Ground": "ground"}    # adventure kit: dual-grid chasm ground tiles (vki_fam_cave)


def vki_parse_name(n):
    """SM_VKI_<Class>_<Family>_<Kind>_<Len><Var>[_<L|R>]_<Full|Cut> -> dict(cls, fam, kind, len, depth, var,
    height). Tolerant: every field may be None. Builders override anything through k.meta."""
    out = dict(cls=None, fam=None, kind=None, len=None, depth=None, var=None, height=None)
    if not n.startswith("SM_VKI_"):
        return out
    tk = n[7:].split("_")
    out["cls"] = VKI_CLASS_TOKENS.get(tk[0], "prop")
    rest = tk[1:]
    if rest and rest[0] in VKI_FAMILIES:
        out["fam"] = rest[0]
        rest = rest[1:]
    if rest and rest[-1] in ("Full", "Cut"):
        out["height"] = rest[-1]
        rest = rest[:-1]
    var = []
    for t in rest:
        if t in ("Full", "Cut"):                       # e.g. Leaf_Wide_Cut_L
            out["height"] = t
            continue
        m1 = re.match(r"^(\d{3})([A-Z]?)$", t)
        m2 = re.match(r"^(\d{3})x(\d{3})$", t)
        if m1 and out["len"] is None:
            out["len"] = int(m1.group(1)) / 100.0
            if m1.group(2):
                var.append(m1.group(2))
        elif m2 and out["len"] is None:
            out["len"], out["depth"] = int(m2.group(1)) / 100.0, int(m2.group(2)) / 100.0
        elif re.match(r"^Q[01]{2}$", t) or (t in ("L", "R") and out["kind"] is not None):
            var.append(t)
        elif out["kind"] is None:
            out["kind"] = t
        else:
            var.append(t)
    if out["kind"] is None:
        out["kind"] = tk[0]
    if out["kind"] == "Rake":
        out["height"] = "Rake"
    out["var"] = "_".join(var) or None
    return out


# ---------------------------------------------------------------- the kit class
class VKIKit(Kit):
    """Kit for interior pieces. VKIKit(name) reads family/class/thickness from the piece name.
    Builders fill k.meta (-> vki_* props) and k.slot_mats ({slot or style key: material / style name}).
    Build layers: k.body (int, per vertex: wall body), k.dark (float, per vertex: darkening 0..1),
    k.heat (float, per vertex: GLOW core 1 .. rim 0; finish stores vki_rim = 1 - heat when any heat > 0).
    Never add bmesh layers yourself mid-build: a new layer invalidates every BMVert reference you hold."""

    def __init__(s, name="", fam=None):
        Kit.__init__(s)
        s.name = name
        s.parsed = vki_parse_name(name) if name else vki_parse_name("")
        s.meta = {}
        s.slot_mats = {}
        # all build layers exist before any geometry: adding a bmesh layer later invalidates every BMVert reference
        s.body = s.bm.verts.layers.int.new("vki_body")
        s.dark = s.bm.verts.layers.float.new("vki_dark")
        s.heat = s.bm.verts.layers.float.new("vki_heat")
        s.wobble_off = False            # T13 builds the same piece with this on
        s.wobble_log = []               # vki_wobble records its arguments here (T13 reads them)
        s.set_family(fam or s.parsed["fam"])

    def set_family(s, fam):
        """family drives class (O/P), thickness T, full height H, the Stone/Ashlar coping switch and slot defaults"""
        s.fam = fam
        s.cls = VKI_FAMILIES[fam]["cls"] if fam in VKI_FAMILIES else "O"
        s.T = VKI_T[s.cls]
        s.H = VKI_H_FULL.get(fam, 3.0)
        return s

    def set_heat(s, verts, h):
        for v in verts:
            v[s.heat] = h

    def set_dark(s, verts, d):
        for v in verts:
            v[s.dark] = max(v[s.dark], d)

    def mark_body(s, verts):
        for v in verts:
            v[s.body] = 1

    # -- UVs: VKI_TILE for slots >= 55; Stone/Ashlar coping switch; CAP grain along the long box axis
    def project(s, faces, mi, axes=None, sizes=None, offset=(0.0, 0.0), tile=None):
        for f in faces:
            if not f.is_valid:
                continue
            f.normal_update()
            n = f.normal
            m2 = mi
            if mi == STONE and abs(n.z) > 0.7:
                m2 = STONE_BLOCK
            elif mi in (VKI_WALL_A, VKI_WALL_B) and abs(n.z) > 0.7 and s.fam in ("Stone", "Ashlar", "Dungeon", "Bars",
                                                                                "Ancient", "Sewer", "Dwarf"):
                m2 = VKI_STONE_BLOCK_IN
            f.material_index = m2
            tt = (tile or vki_tile(mi)) if m2 == mi else vki_tile(m2)
            if m2 in (WOOD, SHUTTER, VKI_CAP) and axes:
                cand = [(sz, ax) for ax, sz in zip(axes, sizes) if abs(ax.dot(n)) < 0.8]
                cand.sort(key=lambda a: -a[0])
                U = cand[0][1] if cand else axes[0]
                V = n.cross(U).normalized()
            elif abs(n.z) > 0.7:
                U = Vector((1, 0, 0)); V = Vector((0, 1, 0))
            else:
                U = n.cross(Vector((0, 0, 1))); U.normalize(); V = Vector((0, 0, 1))
            for l in f.loops:
                p = l.vert.co
                l[s.uv].uv = (p.dot(U) / tt + offset[0], p.dot(V) / tt + offset[1])

    # -- Kit.box with a zero UV offset for the world-locked slots (FLOOR, WALL_A, WALL_B, INFILL)
    def box(s, center, size, mi, rot=(0, 0, 0), bevel=0.04, segs=1, jitter=0.0, seed=0, xform=None, tile=None):
        if mi == STONE and bevel > 0 and (sorted(size)[1] < 0.7 or min(size) < 0.25):
            mi = STONE_BLOCK
        r = bmesh.ops.create_cube(s.bm, size=1.0); vs = r["verts"]
        R = Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X")
        M = Matrix.Translation(Vector(center)) @ R @ Matrix.Diagonal((*size, 1))
        if xform is not None:
            M = xform @ M; R = xform.to_3x3().to_4x4() @ R
        bmesh.ops.transform(s.bm, matrix=M, verts=vs)
        if jitter:
            rnd = random.Random(seed)
            for v in vs:
                v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jitter
        faces = list({f for v in vs for f in v.link_faces})
        for f in faces:
            f.material_index = mi
        if bevel > 0:
            edges = list({e for v in vs for e in v.link_edges})
            res = bmesh.ops.bevel(s.bm, geom=edges + vs, offset=min(bevel, min(size) * 0.45), segments=segs,
                                  profile=0.5, affect="EDGES", clamp_overlap=True)
            faces = [f for f in faces if f.is_valid] + list(res["faces"])
            for f in faces:
                f.material_index = mi
        s.bm.normal_update()
        axes = [(R @ Vector(a)).normalized() for a in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
        c = Vector(center) if xform is None else xform @ Vector(center)
        if mi in VKI_WORLD_LOCKED or (mi in (STONE, ASHLAR, FIELDSTONE) and bevel == 0):
            off = (0.0, 0.0)
        else:
            h = abs(hash((round(c.x, 2), round(c.y, 2), round(c.z, 2))))
            off = ((h % 997) / 997.0, (h // 997 % 991) / 991.0)
        s.project(faces, mi, axes, size, offset=off, tile=tile)
        return [v for f in faces for v in f.verts]

    def body_box(s, x0, x1, z0, z1, y0=None, y1=None, step=0.25, mi_a=None, mi_b=None):
        """a wall-body panel: -Y face WALL_A (room), +Y face WALL_B, ends/top/bottom WALL_A (the coping switch
        turns horizontal faces into STONE_BLOCK_IN on Stone/Ashlar), grid_cut at `step`, every new vertex flagged
        k.body. y0/y1 default to -T/2 / +T/2. Returns the new vertices."""
        y0 = -s.T / 2 if y0 is None else y0
        y1 = s.T / 2 if y1 is None else y1
        before = set(s.bm.verts)
        vs = s.box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0),
                   VKI_WALL_A if mi_a is None else mi_a, bevel=0)
        for f in list({f for v in vs for f in v.link_faces}):
            if f.normal.y > 0.7:
                s.project([f], VKI_WALL_B if mi_b is None else mi_b)
        grid_cut(s, list(set(vs)), step)
        new = [v for v in s.bm.verts if v not in before]
        s.mark_body(new)
        return new

    # -- finish: §2.8 vertex colour, §3.4 metadata, §4.1 slots
    def finish(s, name=None, coll=None, grime="wall", loc=(0, 0, 0)):
        name = name or s.name
        piece = s.name or name
        if grime not in VKI_GRIMES:
            raise ValueError(f"{piece}: grime must be one of {VKI_GRIMES}, not {grime!r}")
        bm = s.bm
        bm.normal_update()
        vki_open_wall_ends(s, piece)
        used = {}
        for f in bm.faces:
            used[f.material_index] = used.get(f.material_index, 0) + 1
        bad = sorted(i for i in used if i < 0 or i >= VKI_NSLOTS)
        if bad:
            raise ValueError(f"{piece}: material indices out of range {bad}")
        ban = sorted(i for i in used if i in VKI_BANNED)
        if ban:
            nm = {v: k_ for k_, v in globals().items() if isinstance(v, int) and k_.isupper() and 0 <= v < 55}
            raise ValueError(f"{piece}: banned slots on a VKI master: {[(i, nm.get(i)) for i in ban]}")
        # footprint (bbox) before the mesh is written
        if bm.verts:
            xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
            bbox = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
        else:
            bbox = (0, 0, 0, 0, 0, 0)
        # vertex colour
        cl, dk = s.cl, s.dark
        for f in bm.faces:
            nz = f.normal.z
            capf = f.material_index == VKI_CAP and nz > 0.7
            under = nz < -0.6
            for l in f.loops:
                v = l.vert; z = v.co.z
                if grime == "none":
                    g = 1.0
                else:
                    if capf or grime == "floor":
                        g = 1.0
                    elif grime == "wall":
                        g = 0.75 + 0.25 * vki_smoothstep(0.0, 0.6, z) if z >= 0 else \
                            0.75 * (0.45 + 0.55 * vki_clamp((z + 0.30) / 0.30))
                    else:
                        g = 0.85 + 0.15 * vki_smoothstep(0.0, 0.3, z)
                    if under:
                        g *= 0.72
                g *= 1.0 - vki_clamp(v[dk])
                l[cl] = (g, g * 0.98, g * 0.95, 1.0)
        # vki_rim = 1 - heat (only when a builder wrote heat); drop the build layers
        hl = bm.verts.layers.float.get("vki_heat")
        heat = [vki_clamp(v[hl]) for v in bm.verts]
        bm.verts.layers.float.remove(hl)
        bm.verts.layers.int.remove(bm.verts.layers.int.get("vki_body"))
        bm.verts.layers.float.remove(bm.verts.layers.float.get("vki_dark"))
        if any(h > 0.0 for h in heat):
            rim = bm.verts.layers.float.new("vki_rim")
            for v, h in zip(bm.verts, heat):          # fresh iteration: the new layer invalidated older refs
                v[rim] = 1.0 - h
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me); bm.free(); s.bm = None
        old = bpy.data.objects.get(name)
        if old is not None:
            if not name.startswith("__vki"):
                bpy.data.meshes.remove(me)
                raise RuntimeError(f"{name} exists: build through vki_rebuild / vki_ws_build (they use a temp name)")
            om = old.data
            bpy.data.objects.remove(old)
            if om is not None and om.users == 0:
                bpy.data.meshes.remove(om)
        o = bpy.data.objects.new(name, me)
        (coll or vki_pieces_coll()).objects.link(o)
        o.location = loc
        km = kit_mats()
        assert len(km) == 55 and km[54].name == "M_VK_Hewn", "kit_mats() changed: slot 54 must be M_VK_Hewn"
        mats = km[:55] + vki_mats()
        assert len(mats) == VKI_NSLOTS
        ov = vki_master_slot_mats(piece, s.fam, s.meta, s.slot_mats)
        for i, m in enumerate(mats):
            me.materials.append(ov.get(i, m))
        meta = vki_default_meta(piece, s, bbox)
        for k_, v_ in s.meta.items():
            meta[vki_meta_key(k_)] = v_
        for k_, v_ in meta.items():
            if v_ is None:
                continue
            o[k_] = vki_prop(v_)
        return o


VKI_END_TOL = 1e-5


def vki_open_wall_ends(k, piece=""):
    """core fix (z-fighting): delete the outward-facing faces of a wall piece that lie in its end planes x = 0 and
    x = L. Every wall end is either covered by a post or butts a neighbour with the identical end profile (T2), so
    the end faces never show; at every butt joint they were coplanar with the half-stud / sole / cap end faces of
    the same piece (10-26 same-facing overlaps per wall, visible as z-fighting at a free end). Rules that follow:
    walls have boundary edges only in these two planes (T7), a free wall end without a post is an ERROR (T12), and
    T4 checks that the post covers the open end outline. Loose vertices / edges left behind are removed."""
    cls = k.meta.get("vki_class", k.meta.get("class")) or k.parsed.get("cls")
    L = k.meta.get("vki_len", k.meta.get("len", k.parsed.get("len")))
    if cls != "wall" or not L:
        return 0
    L = float(L)
    bm = k.bm
    dead = []
    for f in bm.faces:
        n = f.normal
        for xe, sgn in ((0.0, -1.0), (L, 1.0)):
            if n.x * sgn > 0.999 and all(abs(v.co.x - xe) <= VKI_END_TOL for v in f.verts):
                dead.append(f)
                break
    if dead:
        bmesh.ops.delete(bm, geom=dead, context="FACES_ONLY")
        loose_e = [e for e in bm.edges if not e.link_faces]
        if loose_e:
            bmesh.ops.delete(bm, geom=loose_e, context="EDGES")
        loose_v = [v for v in bm.verts if not v.link_edges]
        if loose_v:
            bmesh.ops.delete(bm, geom=loose_v, context="VERTS")
        bm.normal_update()
    k.meta.setdefault("vki_open_ends", 1)
    return len(dead)


def vki_meta_key(k_):
    return k_ if (k_.startswith("vki_") or k_ in ("kit", "grid_m", "hinge_axis")) else "vki_" + k_


def vki_prop(v):
    """custom-property value: JSON strings for lists / tuples / dicts, ints for bools"""
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (list, tuple, dict)):
        return json.dumps(v)
    if isinstance(v, Vector):
        return json.dumps([round(c, 6) for c in v])
    return v


def vki_get(o, key, default=None):
    """read a vki_* property back (JSON decoded when it is a JSON string)"""
    v = o.get(key, default)
    if isinstance(v, str) and v[:1] in "[{":
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def vki_default_meta(piece, k, bbox):
    """metadata every master gets unless the builder sets it (§3.4)"""
    p = k.parsed if k.name == piece else vki_parse_name(piece)
    cls = k.meta.get("vki_class", k.meta.get("class")) or p["cls"] or "prop"
    x0, y0, z0, x1, y1, z1 = bbox
    r4 = lambda a, up: (math.ceil(a * 1e4 - 1e-6) if up else math.floor(a * 1e4 + 1e-6)) / 1e4
    fp = (r4(x0, 0), r4(y0, 0), r4(x1, 1), r4(y1, 1))
    L = k.meta.get("vki_len", k.meta.get("len", p["len"]))
    meta = {"kit": "VillageInterior", "grid_m": VKI_IG, "vki_class": cls, "vki_piece": piece}
    if k.fam:
        meta["vki_family"] = k.fam
    meta["vki_kind"] = p["kind"]
    if L is not None:
        meta["vki_len"] = L
    if p["var"]:
        meta["vki_var"] = p["var"]
    if p["height"]:
        meta["vki_height"] = p["height"]
    if cls in ("wall", "post"):
        meta["vki_thick"] = k.T
    meta["vki_origin"] = {"wall": "start_node", "post": "node_centre", "floor": "min_corner",
                          "link": "min_corner", "leaf": "hinge", "pit": "min_corner",
                          "rock": "node_centre", "ground": "node_centre"}.get(cls, "footprint_centre")
    meta["vki_rot_lock"] = "world0" if cls in ("floor", "pit", "ground") else "none"
    meta["vki_footprint"] = "%g,%g,%g,%g" % fp
    meta["vki_fp_cells"] = "%d,%d" % (max(1, math.ceil((fp[2] - fp[0]) / VKI_IG - 0.02)),
                                      max(1, math.ceil((fp[3] - fp[1]) / VKI_IG - 0.02)))
    if cls == "wall" and L:
        meta["vki_collider"] = [[L / 2, 0.0, 1.1, L, k.T, 2.2]]
    else:
        meta["vki_collider"] = [[round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4), round((z0 + z1) / 2, 4),
                                 round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)]]
    meta["vki_nav"] = {"wall": "block", "post": "block", "floor": "walk", "overlay": "none", "fx": "none",
                       "leaf": "block", "link": "walk", "test": "none"}.get(cls, "block")
    meta["vki_uv_lock"] = "world" if cls in ("wall", "floor") else "local"
    if cls == "prop":
        meta["vki_mount"] = "floor"
    # Full <-> Cut twin when both are registered
    names = {sp[0] for sp in VKI_SPECS}
    if "vki_cut_to" not in k.meta and "cut_to" not in k.meta:
        for a, b in (("_Full", "_Cut"), ("_Cut", "_Full")):
            if piece.endswith(a) and piece[:-len(a)] + b in names:
                meta["vki_cut_pair"] = piece[:-len(a)] + b
    return meta


# ---------------------------------------------------------------- §2.6 seam rule (wobble)
VKI_AMP = {"Timber": .012, "Stone": .020, "Ashlar": .010, "Wattle": .020, "Board": 0.0, "Dungeon": .020, "Bars": 0.0,
           "Ancient": .020, "Cave": 0.0, "Sewer": .015, "Dwarf": .006, "Mine": 0.0}
VKI_SECOND = {"A": "B", "B": "A"}


def vki_wobble(k, L, fam, variant, holes, top_body_fn, pins=()):
    """§2.6 exactly: outward-only noise on wall-body faces (|y| = T/2, flagged k.body). Call it LAST, after
    every body panel exists (grid_cut 0.25). holes: [(x0, z0, x1, z1)]; top_body_fn(x) -> cap bottom z;
    pins: Timber stud centres. Flat within 0.32..0.57 of nodes 0/1.5/3.0, zero below 0.16 and near the cap."""
    k.wobble_log.append(dict(L=L, fam=fam, variant=variant, holes=list(holes), top_body_fn=top_body_fn,
                             pins=list(pins)))
    if k.wobble_off or not VKI_FLAGS.get("wobble", True):
        return 0
    A = VKI_AMP[fam]
    if A == 0.0:
        return 0
    sA = zlib.crc32(f"{fam}|A".encode())
    moved = 0
    for v in k.bm.verts:
        if not v[k.body] or abs(abs(v.co.y) - k.T / 2) > 1e-4:
            continue
        x, z = v.co.x, v.co.z
        e = min(vki_smoothstep(0.32, 0.57, abs(x - n)) for n in (0.0, 1.5, 3.0) if n <= L + 1e-6)
        e *= min([vki_smoothstep(0.0, 0.10, abs(x - p)) for p in pins] or [1.0])       # Timber studs
        e *= min([vki_smoothstep(0.0, 0.15, vki_rect_dist(x, z, h)) for h in holes] or [1.0])
        tb = top_body_fn(x)                                                             # cap bottom
        zf = vki_smoothstep(0.16, 0.41, z) * vki_smoothstep(tb, tb - 0.25, z)
        if e * zf == 0.0:
            continue
        span = int(min(x, L - 1e-6) // 1.5)
        var = variant if span == 0 else VKI_SECOND[variant]
        sV = zlib.crc32(f"{fam}|{var}".encode())
        u, w = (x - 1.5 * span) / 0.8, z / 0.8
        n = vki_lerp(vki_vnoise(u, w, sA), vki_vnoise(u, w, sV), vki_smoothstep(0.65, 1.0, z))
        v.co.y += math.copysign(A * e * zf * n, v.co.y)                                # outward only
        moved += 1
    return moved


# ---------------------------------------------------------------- look gate G1 decisions (core fix, 2026-09-26)
# Made by the coordinator; the user may still override them, so every alternative stays switchable:
#   corners: "rake" (default) | "pillar" (vki_looktest(pillar=True); the assembler picks per family)
#   exit leaf: "closed" (default, no FX_DoorSpill) | "ajar" 30 deg (vki_looktest(leaf_deg=30) + PKG-L FX_DoorSpill)
#   wobble / cap sag: VKI_FLAGS (both on); key-light shadows: VKI_Key.data.use_shadow (on)
# Levels (measured on the look test with vki_lt_levels, see the spec's §10): VKI_PRESETS below, the window glass
# strength, the FlagRustic lift, the hearth socket (vki_fam_timber VKI_TIM_HEARTH_W / _RADIUS) and M_VKI_GlowIn.
VKI_G1 = dict(corners="rake", exit_leaf="closed", wobble=True, sag=True, key_shadows=True,
              window_day=0.65, flagrustic_tint=(1.12, 1.12, 1.12))

# ---------------------------------------------------------------- §4.3 materials
VKI_VOID = "#0B0908"                              # what camera rays must show on the PNG
VKI_VOID_LINEAR = (0.0118, 0.0098, 0.0090)        # calibrated: renders as #0B0908 under AgX MHC, exposure -0.2
VKI_WALL_STYLES = {"PlasterWhite": (1.08, 1.08, 1.10), "PlasterCream": (1.0, 1.0, 1.0),
                   "PlasterDaub": (.80, .65, .47), "PlasterOchre": (1.03, .84, .56), "PlasterRed": (.78, .42, .33)}
VKI_MAT_MAP = {
    # floors (FLOOR slot, world-locked t 3.0)
    "M_VKI_Boards_NS": dict(tex="T_VKI_Boards_NS", ph="#74492A", nstr=1.1, spec=0.15),
    "M_VKI_Boards_EW": dict(tex="T_VKI_Boards_EW", ph="#74492A", nstr=1.1, spec=0.15),
    "M_VKI_BoardsDark_NS": dict(tex="T_VKI_Boards_NS", tint=(.86, .80, .76), ph="#74492A", nstr=1.1, spec=0.15),
    "M_VKI_BoardsDark_EW": dict(tex="T_VKI_Boards_EW", tint=(.86, .80, .76), ph="#74492A", nstr=1.1, spec=0.15),
    "M_VKI_BoardsPale_NS": dict(tex="T_VKI_Boards_NS", tint=(1.10, 1.05, .95), ph="#74492A", nstr=1.1, spec=0.15),
    "M_VKI_BoardsPale_EW": dict(tex="T_VKI_Boards_EW", tint=(1.10, 1.05, .95), ph="#74492A", nstr=1.1, spec=0.15),
    "M_VKI_Flag": dict(tex="T_VKI_Flagstone", ph="#857D70", nstr=1.0, spec=0.25),
    "M_VKI_FlagWarm": dict(tex="T_VKI_Flagstone", tint=(1.04, 1.0, .93), ph="#857D70", nstr=1.0, spec=0.25),
    # G1 (core fix): a small lift so the walkable floor reaches the Day level (BC display luma 0.373 -> ~0.39,
    # inside the 0.25-0.45 palette band)
    "M_VKI_FlagRustic": dict(tex="T_VKI_FlagRustic", tint=VKI_G1["flagrustic_tint"], ph="#7A6D5C", nstr=1.1,
                             spec=0.2),
    "M_VKI_Earth": dict(tex="T_VKI_Earth", ph="#6B5840", nstr=1.0, spec=0.1),
    "M_VKI_EarthSooty": dict(tex="T_VKI_EarthSooty", ph="#4E443A", nstr=1.0, spec=0.1),
    # fix r1: the raw exterior cobble is pale (p95 luma 0.73 on screen by Day) and pulled the eye below the windows
    "M_VKI_ApronCobble": dict(kind="bc", tex="T_VK_Cobble", tint=(.74, .72, .70), ph="#7A7468"),
    "M_VKI_ApronDirt": dict(kind="bc", tex="T_VK_Dirt", ph="#6E5A42"),
    "M_VKI_ApronGrass": dict(kind="bc", tex="T_VK_Grass", ph="#4F6B30"),
    # walls (WALL_A / WALL_B / INFILL, world-locked t 1.5)
    **{"M_VKI_" + k_: dict(tex="T_VKI_PlasterIn", tint=v_, ph="#D6CBB2", nstr=0.8, spec=0.2)
       for k_, v_ in VKI_WALL_STYLES.items()},
    "M_VKI_StoneIn": dict(tex="T_VKI_StoneIn", ph="#8A8274", nstr=1.0, spec=0.25),
    "M_VKI_StoneInWarm": dict(tex="T_VKI_StoneIn", tint=(1.04, 1.00, 0.94), ph="#8A8274", nstr=1.0, spec=0.25),
    "M_VKI_StoneInCool": dict(tex="T_VKI_StoneIn", tint=(0.95, 0.98, 1.03), ph="#8A8274", nstr=1.0, spec=0.25),
    "M_VKI_AshlarIn": dict(tex="T_VKI_AshlarIn", ph="#C4B8A0", nstr=1.0, spec=0.25),
    "M_VKI_WattleIn": dict(tex="T_VKI_WattleIn", ph="#7A5A3A", nstr=1.1, spec=0.15),
    "M_VKI_BoardsV": dict(tex="T_VKI_BoardsV", ph="#7C4F2E", nstr=1.1, spec=0.15),
    "M_VKI_Brick": dict(tex="T_VKI_Brick", ph="#8A4A34", nstr=1.0, spec=0.2),
    # other slots
    "M_VKI_StoneBlockIn": dict(tex="T_VKI_StoneBlockIn", ph="#A39988", nstr=0.8, spec=0.25),
    "M_VKI_Dress": dict(tex="T_VKI_StoneBlockIn", tint=DRESS_TINT, ph="#A39988", nstr=0.8, spec=0.25),
    "M_VKI_Straw": dict(tex="T_VKI_StrawBed", ph="#C4A45E", nstr=0.9, spec=0.1),
    "M_VKI_Ash": dict(tex="T_VKI_Ash", ph="#6E6A66", nstr=0.8, spec=0.1),
    "M_VKI_Textiles": dict(tex="T_VKI_Textiles", ph="#8A3A2A", nstr=0.8, spec=0.2),
    "M_VKI_WoodDark": dict(tex="T_VK_Wood", tint=(.62, .55, .50), ph="#4A2E1E", nstr=1.2, spec=0.15),
    "M_VKI_WoodScrubbed": dict(tex="T_VK_Planks", tint=(1.30, 1.25, 1.15), ph="#9C7A56", nstr=1.2, spec=0.15),
    # still water in troughs and barrels (coordinator 2026-09-26): a flat murky surface; the textured version
    # (T_VK_Water, normal 0.6) broke every interior light into white glitter
    "M_VKI_WaterMurky": dict(kind="flat", col=(.075, .085, .065), rough=0.6),     # 0.18 mirrored the room
    "M_VKI_Wax": dict(kind="flat", col=(.93, .88, .74), rough=0.5),
    "M_VKI_Ale": dict(kind="flat", col=(.45, .28, .08), rough=0.3),
    "M_VKI_GlowIn": dict(kind="glow"),
    # G1 (core fix): 1.0 (§4.3) -> 0.8 (fix r1) -> 0.65, so the fire leads the day glass in brightness
    "M_VKI_Window_Day": dict(kind="window", warm=(.78, .86, 1.0), strength=VKI_G1["window_day"]),
    "M_VKI_Window_Night": dict(kind="window", warm=(.45, .55, .85), strength=0.35),
    "M_VKI_Daylight": dict(kind="daylight", col=(.80, .86, .95), strength=0.8),
    "M_VKI_Stained_In": dict(kind="stained", tex="T_VK_Stained", emission=1.8),
    "M_VKI_Stained_Night": dict(kind="stained", tex="T_VK_Stained", emission=0.4),
    "M_VKI_FX_Light": dict(kind="fx", col=(1.0, .93, .78), strength=0.6, alpha=0.15),
    # dungeon kit (docs/DUNGEON_KIT.md): big coursed blocks and worn slabs (vki_tex_dungeon), dressed stone and caps
    # from T_VKI_StoneBlockIn (the caps stay a step paler than the walls so the cutaway outline reads in the dark)
    "M_VKI_DungeonIn": dict(tex="T_VKI_DungeonIn", ph="#5E5E5C", nstr=1.1, spec=0.3),
    "M_VKI_DungeonInDamp": dict(tex="T_VKI_DungeonIn", tint=(0.84, 0.90, 0.84), ph="#5E5E5C", nstr=1.1, spec=0.35),
    "M_VKI_DungeonInWarm": dict(tex="T_VKI_DungeonIn", tint=(1.10, 1.02, 0.90), ph="#5E5E5C", nstr=1.1, spec=0.3),
    "M_VKI_DungeonCap": dict(tex="T_VKI_StoneBlockIn", tint=(1.16, 1.18, 1.22), ph="#8E8C88", nstr=0.8, spec=0.25),
    "M_VKI_DungeonBlock": dict(tex="T_VKI_StoneBlockIn", tint=(0.58, 0.59, 0.62), ph="#66645F", nstr=0.9, spec=0.25),
    "M_VKI_DungeonFlag": dict(tex="T_VKI_DungeonFlag", ph="#57544E", nstr=1.1, spec=0.3),
    "M_VKI_DungeonFlagWarm": dict(tex="T_VKI_DungeonFlag", tint=(1.10, 1.03, 0.92), ph="#57544E", nstr=1.1, spec=0.3),
    "M_VKI_EarthDamp": dict(tex="T_VKI_Earth", tint=(0.66, 0.65, 0.64), ph="#4A4238", nstr=1.0, spec=0.15),
    "M_VKI_Bone": dict(kind="flat", col=(.62, .56, .44), rough=0.6),
    "M_VKI_Gold": dict(kind="flat", col=(.80, .52, .12), rough=0.3),
    # standing water on a dungeon floor: a dark glossy film (70 % opaque) that darkens the slabs under it and picks up
    # the torches as highlights (not the murky trough water, which is rough on purpose; opaque black read as holes)
    "M_VKI_Puddle": dict(kind="gloss", col=(.040, .046, .052), rough=0.05, alpha=0.55),
    # adventure kit: the ruined temple (huge weathered blocks, pale slabs), the caves (rock, cut rock, cave floor),
    # spider silk (alpha)
    "M_VKI_AncientIn": dict(tex="T_VKI_AncientIn", tint=(0.96, 1.00, 0.92), ph="#8C8A78", nstr=1.1, spec=0.25),
    "M_VKI_AncientFlag": dict(tex="T_VKI_AncientFlag", tint=(0.98, 1.00, 0.94), ph="#77756A", nstr=1.1, spec=0.25),
    "M_VKI_AncientCap": dict(tex="T_VKI_StoneBlockIn", tint=(1.44, 1.48, 1.36), ph="#A8A690", nstr=0.8, spec=0.25),
    "M_VKI_AncientBlock": dict(tex="T_VKI_StoneBlockIn", tint=(0.84, 0.88, 0.78), ph="#8A8878", nstr=0.9, spec=0.25),
    "M_VKI_CaveRock": dict(tex="T_VKI_CaveRock", ph="#5A5048", nstr=1.3, spec=0.3),
    "M_VKI_CaveRockDamp": dict(tex="T_VKI_CaveRock", tint=(0.82, 0.86, 0.84), ph="#5A5048", nstr=1.3, spec=0.4),
    "M_VKI_CaveCut": dict(tex="T_VKI_CaveTop", tint=(1.58, 1.55, 1.50), ph="#8A8076", nstr=0.6, spec=0.2),
    "M_VKI_CaveFloor": dict(tex="T_VKI_CaveFloor", tint=(0.70, 0.72, 0.80), ph="#4E463E", nstr=1.2, spec=0.25),
    "M_VKI_Web": dict(kind="web"),
    # sewer kit: old wet brick walls and brick paving (vki_tex_dungeon), dressed stone from T_VKI_StoneBlockIn (caps a
    # step paler than the brick), murky channel water (glossy, 88 % opaque over the dark bed), sludge, falling foam
    "M_VKI_SewerBrick": dict(tex="T_VKI_SewerBrick", ph="#4A3228", nstr=1.1, spec=0.35),
    "M_VKI_SewerFloor": dict(tex="T_VKI_SewerFloor", tint=(1.22, 1.18, 1.12), ph="#40362C", nstr=1.1, spec=0.35),
    "M_VKI_SewerCap": dict(tex="T_VKI_StoneBlockIn", tint=(1.08, 1.10, 1.02), ph="#86847A", nstr=0.8, spec=0.3),
    "M_VKI_SewerBlock": dict(tex="T_VKI_StoneBlockIn", tint=(0.56, 0.60, 0.52), ph="#5E5E54", nstr=0.9, spec=0.3),
    "M_VKI_SewerWater": dict(kind="gloss", col=(.10, .11, .065), rough=0.08, alpha=0.93),
    "M_VKI_Sludge": dict(kind="gloss", col=(.060, .064, .028), rough=0.30, alpha=0.90),
    "M_VKI_Foam": dict(kind="flat", col=(.62, .66, .62), rough=0.7),
    # water kit: clear cave water over a pebbly bed (the bed shows through), pale falling water; Unity animates them
    "M_VKI_StreamWater": dict(kind="gloss", col=(.070, .115, .125), rough=0.04, alpha=0.72),
    "M_VKI_StreamBed": dict(tex="T_VKI_CaveFloor", tint=(0.46, 0.50, 0.50), ph="#3A3632", nstr=1.3, spec=0.5),
    "M_VKI_WaterFall": dict(kind="gloss", col=(.50, .58, .60), rough=0.25, alpha=0.82),
    # dwarf kit: granite ashlar and the paneled hall floor (vki_tex_dungeon), pale polished caps and dark dressed stone
    # from T_VKI_StoneBlockIn, molten lava (emissive; Unity animates it)
    "M_VKI_DwarfIn": dict(tex="T_VKI_DwarfIn", ph="#4A4B4E", nstr=1.0, spec=0.35),
    "M_VKI_DwarfFloor": dict(tex="T_VKI_DwarfFloor", tint=(0.56, 0.56, 0.58), ph="#5A5C5E", nstr=1.0, spec=0.45),
    "M_VKI_DwarfCap": dict(tex="T_VKI_StoneBlockIn", tint=(1.18, 1.20, 1.22), ph="#8E9092", nstr=0.8, spec=0.35),
    "M_VKI_DwarfBlock": dict(tex="T_VKI_StoneBlockIn", tint=(0.62, 0.64, 0.68), ph="#5E6064", nstr=0.9, spec=0.35),
    "M_VKI_DwarfFlag": dict(tex="T_VKI_DwarfFlag", tint=(0.56, 0.56, 0.58), ph="#55575A", nstr=1.0, spec=0.40),
    # molten lava: a pure emitter (a lit base read pink) on the heat gradient its tiles write (vki_rim: 0 at the hot
    # core, 1 at the banks), yellow-white down the middle to a deep red at the banks; the crust that cools on it, dark
    # with a faint red glow (it read as holes when black)
    "M_VKI_Lava": dict(kind="heat", core=(1.0, 0.70, 0.15), rim=(1.0, 0.12, 0.0), strength=(1.25, -0.9)),  # (brighter
    # cores went peach under AgX)
    "M_VKI_LavaCrust": dict(kind="flat", col=(0.035, 0.026, 0.022), rough=0.9, emit=(1.0, 0.14, 0.01), strength=0.12),
    "M_VKI_BannerRed": dict(kind="flat", col=(0.36, 0.035, 0.03), rough=0.9),               # the clan banners' cloth
    # points of interest (vki_props_poi): the necromancer's sigil, a pure green emitter
    "M_VKI_RuneGlow": dict(kind="flat", col=(0.0, 0.0, 0.0), rough=1.0, emit=(0.22, 1.0, 0.30), strength=1.0),
    # debris (vki_props_debris): forge slag, glassy black
    "M_VKI_Slag": dict(kind="gloss", col=(0.035, 0.030, 0.035), rough=0.18, alpha=1.0),
    "M_VKI_Rust": dict(kind="flat", col=(0.26, 0.15, 0.09), rough=0.85),                      # old iron
    # mine kit (docs/MINE_KIT.md, vki_fam_mine): weathered oak for the track and the carts, the veins' quartz and ore
    "M_VKI_MineWood": dict(tex="T_VK_Wood", tint=(0.92, 0.88, 0.84), ph="#6A5442", nstr=1.2, spec=0.15),
    "M_VKI_Quartz": dict(kind="flat", col=(0.74, 0.73, 0.68), rough=0.45),
    "M_VKI_IronOre": dict(kind="flat", col=(0.36, 0.13, 0.07), rough=0.8),
}
VKI_SLOT_DEFAULTS = ["M_VKI_Boards_NS", "M_VKI_PlasterCream", "M_VKI_PlasterCream", "M_VK_Hewn",
                     "M_VKI_StoneBlockIn", "M_VKI_Brick", "M_VKI_Straw", "M_VKI_Ash", "M_VKI_Textiles", "M_VKI_Wax",
                     "M_VKI_FX_Light", "M_VKI_WattleIn"]           # slots 55..66
VKI_WALL_MATS = {**{k_: "M_VKI_" + k_ for k_ in VKI_WALL_STYLES},
                 **{k_: "M_VKI_" + k_ for k_ in ("StoneIn", "StoneInWarm", "StoneInCool", "AshlarIn", "WattleIn",
                                                 "BoardsV", "Brick", "DungeonIn", "DungeonInDamp", "DungeonInWarm",
                                                 "AncientIn", "CaveRock", "CaveRockDamp", "SewerBrick", "DwarfIn")}}
VKI_STYLE_MATS = {
    "floor": {k_: "M_VKI_" + k_ for k_ in ("Boards_NS", "Boards_EW", "BoardsDark_NS", "BoardsDark_EW",
                                           "BoardsPale_NS", "BoardsPale_EW", "Flag", "FlagWarm", "FlagRustic",
                                           "Earth", "EarthSooty", "ApronCobble", "ApronDirt", "ApronGrass",
                                           "DungeonFlag", "DungeonFlagWarm", "EarthDamp", "AncientFlag", "CaveFloor",
                                           "SewerFloor", "DwarfFloor", "DwarfFlag")},
    "wall_a": VKI_WALL_MATS, "wall_b": VKI_WALL_MATS, "infill": VKI_WALL_MATS,
    "cap": {"Hewn": "M_VK_Hewn", "StoneBlockIn": "M_VKI_StoneBlockIn", "Dress": "M_VKI_Dress",
            "PlasterDaub": "M_VKI_PlasterDaub", "DungeonCap": "M_VKI_DungeonCap", "DungeonBlock": "M_VKI_DungeonBlock",
            "AncientCap": "M_VKI_AncientCap", "AncientBlock": "M_VKI_AncientBlock", "CaveCut": "M_VKI_CaveCut",
            "SewerCap": "M_VKI_SewerCap", "SewerBlock": "M_VKI_SewerBlock", "DwarfCap": "M_VKI_DwarfCap",
            "DwarfBlock": "M_VKI_DwarfBlock"},
    "wood": {"Oak": "M_VK_Wood", "Dark": "M_VKI_WoodDark"},
    "planks": {"Scrubbed": "M_VKI_WoodScrubbed", "Planks": "M_VK_Planks"},
    "window": {"Day": "M_VKI_Window_Day", "Window_Day": "M_VKI_Window_Day", "Night": "M_VKI_Window_Night",
               "Window_Night": "M_VKI_Window_Night", "Daylight": "M_VKI_Daylight", "Plain": "M_VK_Window"},
    "stained": {"In": "M_VKI_Stained_In", "Stained_In": "M_VKI_Stained_In", "Night": "M_VKI_Stained_Night",
                "Stained_Night": "M_VKI_Stained_Night"},
    "glow": {"GlowIn": "M_VKI_GlowIn", "Glow": "M_VK_Glow"},
    "water": {"Water": "M_VK_Water", "Ale": "M_VKI_Ale", "WaterMurky": "M_VKI_WaterMurky", "Puddle": "M_VKI_Puddle",
              "SewerWater": "M_VKI_SewerWater", "Sludge": "M_VKI_Sludge", "StreamWater": "M_VKI_StreamWater",
              "WaterFall": "M_VKI_WaterFall", "Lava": "M_VKI_Lava"},
    # "shutter", "cloth", "cloth_b": the exterior variants (variant_mat), e.g. shutter "Red", cloth "Blue"
}
VKI_FAMILY_SLOT_MATS = {
    "Stone": {VKI_WALL_A: "M_VKI_StoneIn", VKI_WALL_B: "M_VKI_StoneIn", VKI_CAP: "M_VKI_StoneBlockIn"},
    "Ashlar": {VKI_WALL_A: "M_VKI_AshlarIn", VKI_WALL_B: "M_VKI_AshlarIn", VKI_CAP: "M_VKI_Dress"},
    "Board": {VKI_WALL_A: "M_VKI_BoardsV", VKI_WALL_B: "M_VKI_BoardsV"},
    "Wattle": {VKI_WALL_A: "M_VKI_PlasterDaub", VKI_WALL_B: "M_VKI_PlasterDaub"},
    "Timber": {},
    "Dungeon": {VKI_WALL_A: "M_VKI_DungeonIn", VKI_WALL_B: "M_VKI_DungeonIn", VKI_CAP: "M_VKI_DungeonCap",
                VKI_STONE_BLOCK_IN: "M_VKI_DungeonBlock"},
    "Bars": {VKI_WALL_A: "M_VKI_DungeonIn", VKI_WALL_B: "M_VKI_DungeonIn", VKI_CAP: "M_VKI_DungeonCap",
             VKI_STONE_BLOCK_IN: "M_VKI_DungeonBlock"},
    "Ancient": {VKI_WALL_A: "M_VKI_AncientIn", VKI_WALL_B: "M_VKI_AncientIn", VKI_CAP: "M_VKI_AncientCap",
                VKI_STONE_BLOCK_IN: "M_VKI_AncientBlock"},
    "Cave": {VKI_WALL_A: "M_VKI_CaveRock", VKI_WALL_B: "M_VKI_CaveRock", VKI_CAP: "M_VKI_CaveCut",
             VKI_STONE_BLOCK_IN: "M_VKI_CaveRock"},
    "Sewer": {VKI_WALL_A: "M_VKI_SewerBrick", VKI_WALL_B: "M_VKI_SewerBrick", VKI_CAP: "M_VKI_SewerCap",
              VKI_STONE_BLOCK_IN: "M_VKI_SewerBlock"},
    "Mine": {VKI_WALL_A: "M_VKI_CaveRock", VKI_WALL_B: "M_VKI_CaveRock", VKI_CAP: "M_VK_Hewn",
             VKI_STONE_BLOCK_IN: "M_VKI_CaveRock"},
    "Dwarf": {VKI_WALL_A: "M_VKI_DwarfIn", VKI_WALL_B: "M_VKI_DwarfIn", VKI_CAP: "M_VKI_DwarfCap",
              VKI_STONE_BLOCK_IN: "M_VKI_DwarfBlock"},
}
VKI_MASTER_MATS = {GLOW: "M_VKI_GlowIn", WINDOW: "M_VKI_Window_Day", STAINED: "M_VKI_Stained_In",
                   DRESS: "M_VKI_Dress"}                     # on every VKI master (§4.1)


def vki_tex_ready(prefix, suffixes=("_BC", "_N", "_R")):
    return all(bpy.data.images.get(prefix + s_) is not None for s_ in suffixes)


def vki_nodes_reset(m):
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (900, 0)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.location = (550, 0)
    nt.links.new(b.outputs[0], out.inputs[0])
    return nt, b, out


def vki_flat_nodes(m, col, rough=0.85, use_col=True, emit=None, strength=0.0):
    """flat colour x vertex colour Col (the placeholder when a texture is missing)"""
    nt, b, out = vki_nodes_reset(m)
    if use_col:
        vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"; vc.location = (-300, 300)
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        mx.inputs[0].default_value = 1.0; mx.inputs[6].default_value = (*col, 1); mx.location = (150, 300)
        nt.links.new(vc.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.3
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*col, 1)
    return nt, b


def vki_bc_nodes(m, prefix, tint=None, rough=0.9):
    """base-colour-only texture (terrain textures have no _N/_R) x tint x Col"""
    nt, b, out = vki_nodes_reset(m)
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"; uv.location = (-900, 300)
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images[prefix + "_BC"]; tx.location = (-650, 300)
    nt.links.new(uv.outputs[0], tx.inputs[0])
    col = tx.outputs[0]
    if tint:
        mt = nt.nodes.new("ShaderNodeMix"); mt.data_type = "RGBA"; mt.blend_type = "MULTIPLY"
        mt.inputs[0].default_value = 1.0; mt.inputs[7].default_value = (*tint, 1)
        nt.links.new(col, mt.inputs[6]); col = mt.outputs[2]
    vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"; vc.location = (-300, 500)
    mv = nt.nodes.new("ShaderNodeMix"); mv.data_type = "RGBA"; mv.blend_type = "MULTIPLY"
    mv.inputs[0].default_value = 1.0
    nt.links.new(col, mv.inputs[6]); nt.links.new(vc.outputs[0], mv.inputs[7])
    nt.links.new(mv.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.2
    return m


def vki_shadow_transparent(m):
    """shadow rays pass through: Mix Shader (Light Path 'Is Shadow Ray') -> Transparent BSDF; idempotent"""
    nt = m.node_tree
    if any(n.label == "VKI_SHADOW_MIX" for n in nt.nodes):
        return m
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    ln = next((l for l in nt.links if l.to_node == out and l.to_socket.name == "Surface"), None)
    if ln is None:
        return m
    src = ln.from_socket
    nt.links.remove(ln)
    lp = nt.nodes.new("ShaderNodeLightPath"); lp.location = (out.location.x - 250, out.location.y + 300)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.location = (out.location.x - 250, out.location.y - 200)
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.label = "VKI_SHADOW_MIX"
    mx.location = (out.location.x - 60, out.location.y)
    out.location.x += 200
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    nt.links.new(src, mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    if "use_transparent_shadow" in m.bl_rna.properties:
        m.use_transparent_shadow = True
    return m


# M_VKI_GlowIn (fix r1, a deviation from §4.3's (1,.72,.30)/(.85,.28,.05), 2.2 - 1.0 rim on a (.08,.04,.02) base):
# under AgX Medium High Contrast those emissions render near-white cream, and the dark-but-lit base picked up the
# hearth light 0.1-0.2 m away (diffuse + specular) and washed the flames out further. Now a pure emitter (black base,
# no specular) with deeper, more saturated colours that AgX renders orange: core (1,.60,.16) x 2.2 at rim 0 (a hot
# yellow root, so the fire out-shines the day window glass), rim (1,.13,0) x 0.6 at rim 1 (deep orange-red tips).
# Measured on the look-test fire (renders/interior/fix_r1/diag).
VKI_GLOW_CORE = (1.0, .60, .16)
VKI_GLOW_RIM = (1.0, .13, 0.0)
VKI_GLOW_STRENGTH = (2.2, -1.6)     # strength = a + b * rim


def vki_glow_nodes(m):
    """M_VKI_GlowIn: the flames' heat gradient (VKI_GLOW_CORE -> VKI_GLOW_RIM, VKI_GLOW_STRENGTH)"""
    return vki_heat_nodes(m, VKI_GLOW_CORE, VKI_GLOW_RIM, VKI_GLOW_STRENGTH, diffuse=(1.0, .6, .25, 1))


def vki_heat_nodes(m, core, rim, strength, diffuse=None):
    """a pure emitter on a heat gradient: black, non-specular base; emission = mix(core, rim, Attribute vki_rim),
    strength strength[0] + strength[1] * rim. M_VKI_GlowIn (the flames) and the kind "heat" (the dwarf kit's lava).
    A mesh without vki_rim reads 0: full core."""
    nt, b, out = vki_nodes_reset(m)
    b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.0
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = "GEOMETRY"; at.attribute_name = "vki_rim"
    at.location = (-500, 0)
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MIX"; mx.location = (-200, 100)
    mx.inputs[6].default_value = (*core, 1); mx.inputs[7].default_value = (*rim, 1)
    nt.links.new(at.outputs["Fac"], mx.inputs[0])
    st = nt.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY_ADD"; st.location = (-200, -150)
    st.inputs[1].default_value = strength[1]; st.inputs[2].default_value = strength[0]
    nt.links.new(at.outputs["Fac"], st.inputs[0])
    nt.links.new(mx.outputs[2], b.inputs["Emission Color"]); nt.links.new(st.outputs[0], b.inputs["Emission Strength"])
    m.diffuse_color = diffuse or (*core, 1)
    return m


def vki_fx_nodes(m, col, strength, alpha):
    """M_VKI_FX_Light: emission col*(1-v)^2 at `strength`, alpha `alpha`, no shadow, blended"""
    nt, b, out = vki_nodes_reset(m)
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"; uv.location = (-900, 0)
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); sp.location = (-700, 0); nt.links.new(uv.outputs[0], sp.inputs[0])
    iv = nt.nodes.new("ShaderNodeMath"); iv.operation = "SUBTRACT"; iv.inputs[0].default_value = 1.0
    iv.location = (-520, 0); nt.links.new(sp.outputs[1], iv.inputs[1])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.0
    pw.location = (-350, 0); nt.links.new(iv.outputs[0], pw.inputs[0])
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = "RGBA"; mc.blend_type = "MULTIPLY"; mc.location = (-150, 0)
    mc.inputs[0].default_value = 1.0; mc.inputs[6].default_value = (*col, 1)
    nt.links.new(pw.outputs[0], mc.inputs[7])
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    nt.links.new(mc.outputs[2], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Alpha"].default_value = alpha
    vki_shadow_transparent(m)
    rm = m.bl_rna.properties.get("surface_render_method")
    if rm and "BLENDED" in [i.identifier for i in rm.enum_items]:
        m.surface_render_method = "BLENDED"
    elif "blend_method" in m.bl_rna.properties:
        bm_ = [i.identifier for i in m.bl_rna.properties["blend_method"].enum_items]
        if "BLEND" in bm_:
            m.blend_method = "BLEND"
    m.diffuse_color = (*col, alpha)
    return m


def vki_build_mat(name):
    """(re)build one VKI_MAT_MAP material in place; a missing texture gives the flat placeholder colour
    (flagged m['vki_placeholder']=1) until vki_apply_mats() runs again after the textures exist"""
    sp = VKI_MAT_MAP[name]
    m = bpy.data.materials.get(name)
    kind = sp.get("kind", "pbr")
    if kind == "window":
        m = lit_window_material(name, warm=sp["warm"], strength=sp["strength"])
        vki_shadow_transparent(m)
        m["vki_placeholder"] = 0
        m.use_fake_user = True
        return m
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_fake_user = True                          # styles unused so far must survive the coordinator's save
    ph = 0
    if kind == "pbr":
        if vki_tex_ready(sp["tex"]):
            kw = {k_: sp[k_] for k_ in ("tint", "nstr", "spec", "rough_mul") if k_ in sp}
            pbr_material(m, sp["tex"], **kw)
        else:
            c = vki_srgb(sp["ph"]); t = sp.get("tint") or (1, 1, 1)
            vki_flat_nodes(m, tuple(a * b for a, b in zip(c, t)), 0.85); ph = 1
    elif kind == "bc":
        if vki_tex_ready(sp["tex"], ("_BC",)):
            vki_bc_nodes(m, sp["tex"], sp.get("tint"))
        else:
            vki_flat_nodes(m, vki_srgb(sp["ph"])); ph = 1
    elif kind == "flat":                            # (emit / strength: an emissive flat colour, the dwarf kit's lava)
        vki_flat_nodes(m, sp["col"], sp.get("rough", 0.85), emit=sp.get("emit"), strength=sp.get("strength", 0.0))
    elif kind == "glow":
        vki_glow_nodes(m)
    elif kind == "heat":                            # an emitter on a heat gradient (vki_rim): the dwarf kit's lava
        vki_heat_nodes(m, sp["core"], sp["rim"], sp["strength"])
    elif kind == "daylight":
        vki_flat_nodes(m, sp["col"], 0.5, use_col=False, emit=sp["col"], strength=sp["strength"])
        vki_shadow_transparent(m)
    elif kind == "stained":
        if vki_tex_ready(sp["tex"]):
            pbr_material(m, sp["tex"], emission=sp["emission"], spec=0.5)
        else:
            vki_flat_nodes(m, (0.9, 0.5, 0.2), 0.3, emit=(0.9, 0.35, 0.15), strength=sp["emission"]); ph = 1
        vki_shadow_transparent(m)
    elif kind == "fx":
        vki_fx_nodes(m, sp["col"], sp["strength"], sp["alpha"])
    elif kind == "web":                            # adventure kit: spider silk -- T_VKI_Web_BC (RGB + alpha), clipped
        if vki_tex_ready("T_VKI_Web", ("_BC",)):
            nt, b, out = vki_nodes_reset(m)
            uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"; uv.location = (-900, 0)
            tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images["T_VKI_Web_BC"]; tx.location = (-650, 0)
            nt.links.new(uv.outputs[0], tx.inputs[0])
            nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
            nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
            b.inputs["Roughness"].default_value = 0.6
            b.inputs["Emission Color"].default_value = (0.55, 0.58, 0.62, 1)
            b.inputs["Emission Strength"].default_value = 0.15      # silk catches the light: a faint glow keeps it legible
            vki_shadow_transparent(m)
            rm = m.bl_rna.properties.get("surface_render_method")
            if rm and "DITHERED" in [i.identifier for i in rm.enum_items]:
                m.surface_render_method = "DITHERED"
            elif "blend_method" in m.bl_rna.properties:
                m.blend_method = "CLIP"
            m.diffuse_color = (0.85, 0.86, 0.88, 1)
        else:
            vki_flat_nodes(m, (0.8, 0.8, 0.82)); ph = 1
    elif kind == "gloss":                          # dungeon kit: a thin glossy film (puddles), alpha-blended over the floor
        nt, b = vki_flat_nodes(m, sp["col"], sp.get("rough", 0.1))
        b.inputs["Specular IOR Level"].default_value = 0.5
        b.inputs["Alpha"].default_value = sp.get("alpha", 1.0)
        if sp.get("alpha", 1.0) < 1.0:
            vki_shadow_transparent(m)
            rm = m.bl_rna.properties.get("surface_render_method")
            if rm and "BLENDED" in [i.identifier for i in rm.enum_items]:
                m.surface_render_method = "BLENDED"
            elif "blend_method" in m.bl_rna.properties:
                m.blend_method = "BLEND"
    else:
        raise ValueError(f"{name}: unknown material kind {kind}")
    m["vki_placeholder"] = ph
    return m


def vki_mat(name):
    """material by name: VKI_MAT_MAP entries are built when missing; exterior names must exist (M_VK_Hewn is
    created by hewn_material if needed)"""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    if name in VKI_MAT_MAP:
        return vki_build_mat(name)
    if name == "M_VK_Hewn":
        return hewn_material()
    raise KeyError(f"material {name} does not exist and is not in VKI_MAT_MAP")


def vki_mats():
    """the 12 VKI slot materials (55..66) in slot order"""
    return [vki_mat(n) for n in VKI_SLOT_DEFAULTS]


def vki_apply_mats(names=None):
    """rebuild the VKI_MAT_MAP materials in place (picks up T_VKI_* textures generated since); never touches
    exterior materials. Returns {name: 'textured' | 'placeholder' | kind}"""
    out = {}
    for n in VKI_MAT_MAP:
        if names is not None and n not in names:
            continue
        m = vki_build_mat(n)
        k_ = VKI_MAT_MAP[n].get("kind", "pbr")
        out[n] = "placeholder" if m.get("vki_placeholder") else ("textured" if k_ in ("pbr", "bc", "stained") else k_)
    return out


def vki_style_mat(key, val):
    """style key + value -> Material. Values may also be full material names ('M_...')."""
    if isinstance(val, bpy.types.Material):
        return val
    if isinstance(val, str) and val.startswith("M_"):
        return vki_mat(val)
    if key in ("shutter", "cloth", "cloth_b"):
        return variant_mat("cloth" if key == "cloth_b" else key, val)
    tab = VKI_STYLE_MATS.get(key)
    if tab is None:
        raise KeyError(f"unknown style key {key!r}")
    if val not in tab:
        raise KeyError(f"style {key}={val!r}: not one of {sorted(tab)}")
    return vki_mat(tab[val])


def vki_slot_key(slot):
    """slot index -> style key (None for slots without a style table)"""
    return {v_: k_ for k_, v_ in VKI_SLOT.items()}.get(slot)


def vki_master_slot_mats(piece, fam, meta, slot_mats):
    """{slot: Material} baked into a master: GLOW/WINDOW/STAINED/DRESS defaults, family WALL/CAP defaults,
    PLANKS -> Scrubbed on props, then the builder's k.slot_mats (whitelisted slots + 55..66 only)"""
    ov = {i: vki_mat(n) for i, n in VKI_MASTER_MATS.items()}
    for i, n in VKI_FAMILY_SLOT_MATS.get(fam, {}).items():
        ov[i] = vki_mat(n)
    cls = meta.get("vki_class", meta.get("class")) or vki_parse_name(piece)["cls"]
    if cls == "prop":
        ov[PLANKS] = vki_mat("M_VKI_WoodScrubbed")
    for k_, v_ in slot_mats.items():
        slot = VKI_SLOT[k_] if isinstance(k_, str) else int(k_)
        if not (slot in VKI_OVERRIDABLE or 55 <= slot < VKI_NSLOTS):
            raise ValueError(f"{piece}: slot {slot} is not overridable per master")
        if isinstance(v_, bpy.types.Material):
            ov[slot] = v_
        elif isinstance(v_, str) and v_.startswith("M_"):
            ov[slot] = vki_mat(v_)
        else:
            ov[slot] = vki_style_mat(vki_slot_key(slot), v_)
    return ov


# ---------------------------------------------------------------- §4.1 variants
def vki_style_norm(style):
    """style dict with wall_b defaulting to wall_a"""
    st = dict(style or {})
    if "wall_a" in st and "wall_b" not in st:
        st["wall_b"] = st["wall_a"]
    return st


def vki_variant_mesh(piece, style):
    """mesh copy of a master with materials swapped per style ({key: value}, keys in VKI_SLOT);
    named VARI_<crc32(piece + sorted style JSON)>, carries vki_base / vki_style"""
    st = vki_style_norm(style)
    st = {k_: v_ for k_, v_ in st.items() if k_ in VKI_SLOT}
    if not st:
        return bpy.data.objects[piece].data
    js = json.dumps(st, sort_keys=True)
    nm = "VARI_%08x" % zlib.crc32((piece + js).encode())
    src = bpy.data.objects[piece].data
    me = bpy.data.meshes.get(nm)
    if me is None:
        me = src.copy(); me.name = nm
    me["vki_base"] = piece; me["vki_style"] = js
    vki_variant_apply(me, src, st)
    return me


def vki_variant_apply(me, src, st):
    base = list(src.materials)
    while len(me.materials) < len(base):
        me.materials.append(base[len(me.materials)])
    for i, m in enumerate(base):
        me.materials[i] = m
    for k_, v_ in st.items():
        slot = VKI_SLOT[k_]
        if slot < len(me.materials):
            me.materials[slot] = vki_style_mat(k_, v_)


def vki_refresh_variants(names=None):
    """copy geometry from each VARI_* mesh's master, re-apply its style (run after vki_rebuild and after any
    exterior full_rebuild, which only refreshes VAR_*)"""
    done = []
    for me in list(bpy.data.meshes):
        if not me.name.startswith("VARI_") or "vki_base" not in me:
            continue
        piece = me["vki_base"]
        if names is not None and piece not in names:
            continue
        base = bpy.data.objects.get(piece)
        if base is None:
            continue
        bm = bmesh.new(); bm.from_mesh(base.data); bm.to_mesh(me); bm.free()
        vki_variant_apply(me, base.data, json.loads(me.get("vki_style", "{}")))
        done.append(me.name)
    return done


# ---------------------------------------------------------------- textile atlas (shared with vki_textiles)
VKI_TEXTILE_CELLS = ("rug_madder", "rug_indigo", "runner", "hanging_heraldic", "tapestry_millefleur", "quilt_patch",
                     "blanket_wool", "altar_frontal")
VKI_TEX_PAD_U = 24 / 1024
VKI_TEX_PAD_V = 24 / 512


def vki_textile_uv(cell, u, v):
    """cell-local (u, v) in 0..1 -> atlas uv. 2 x 4 cells of 2:1, row 0 at the top of the image"""
    i = VKI_TEXTILE_CELLS.index(cell) if isinstance(cell, str) else int(cell)
    col, row = i % 2, i // 2
    u = vki_clamp(u); v = vki_clamp(v)
    return ((col + VKI_TEX_PAD_U + u * (1 - 2 * VKI_TEX_PAD_U)) / 2,
            (3 - row + VKI_TEX_PAD_V + v * (1 - 2 * VKI_TEX_PAD_V)) / 4)


def vki_textile_map(k, geom, cell, plane=((1, 0, 0), (0, 1, 0)), c=None, period=None, flip_v=False):
    """put faces on the textile atlas (material TEXTILE): planar u along plane[0], v along plane[1] over the
    faces' bbox. period (metres, runners): u = distance along A / period, and each face gets the integer part of
    its centroid removed, so a runner whose faces never straddle a period boundary chains seamlessly."""
    fs = [g_ for g_ in geom if isinstance(g_, bmesh.types.BMFace)] or list({f for v in geom for f in v.link_faces})
    if not fs:
        return fs
    A = Vector(plane[0]).normalized(); B = Vector(plane[1]).normalized()
    vs = {v for f in fs for v in f.verts}
    c = Vector(c) if c is not None else Vector()
    a = [(v.co - c).dot(A) for v in vs]; b = [(v.co - c).dot(B) for v in vs]
    a0, a1, b0, b1 = min(a), max(a), min(b), max(b)
    for f in fs:
        f.material_index = VKI_TEXTILE
        if period:
            cu = sum(((l.vert.co - c).dot(A) - a0) / period for l in f.loops) / len(f.loops)
            base = math.floor(cu + 1e-9)
        for l in f.loops:
            p = l.vert.co - c
            if period:
                u = ((p.dot(A) - a0) / period) - base
            else:
                u = (p.dot(A) - a0) / max(a1 - a0, 1e-6)
            v = (p.dot(B) - b0) / max(b1 - b0, 1e-6)
            l[k.uv].uv = vki_textile_uv(cell, u, 1 - v if flip_v else v)
    return fs


# ---------------------------------------------------------------- specs, reuse, pieces collection
VKI_SPECS = []            # (name, fn(k: VKIKit), finish_kw e.g. {"grime": "wall"}, pkg)
VKI_REUSE = {             # §5.5 exterior props reused indoors (masters stay in VK_Pieces)
    "SM_VK_Prop_Loom": dict(fp=(2, 2), mount="wall_floor", note="north wall, weaver faces -Y"),
    "SM_VK_Prop_SpinningWheel": dict(fp=(1, 1), mount="floor"),
    "SM_VK_Prop_Stool": dict(fp=(1, 1), mount="floor"),
    "SM_VK_Prop_Bellows": dict(fp=(2, 1), mount="floor", note="industry version, nozzle -X; rot 180 west of a forge"),
    "SM_VK_Prop_Anvil": dict(fp=(1, 1), mount="floor"),
    "SM_VK_Prop_WeaponRack": dict(fp=(1, 1), mount="wall_floor", hug=True),
    "SM_VK_Prop_Grindstone": dict(fp=(1, 1), mount="wall_floor"),
    "SM_VK_Prop_BarrelStack": dict(fp=(2, 1), mount="wall_floor"),
    "SM_VK_Prop_Sawhorse": dict(fp=(1, 1), mount="floor"),
}
VKI_REUSE_STYLE = {"glow": "GlowIn", "window": "Window_Day"}
VKI_NIGHT_STYLE = {"window": "Window_Night", "stained": "Stained_Night"}      # Night scenes, on VKI masters (§4.1)
VKI_REUSE_STYLE_NIGHT = {"glow": "GlowIn", "window": "Window_Night"}


def vki_register(specs):
    """add (name, fn, finish_kw, pkg) entries to VKI_SPECS, replacing entries of the same name"""
    names = {sp[0] for sp in specs}
    VKI_SPECS[:] = [sp for sp in VKI_SPECS if sp[0] not in names] + list(specs)
    return [sp[0] for sp in specs]


def vki_spec_map():
    return {sp[0]: sp for sp in VKI_SPECS}


def vki_pieces_coll():
    """VKI_Pieces: hidden master collection, linked under the VKI_Test scene (fake user as a safety net)"""
    c = bpy.data.collections.get("VKI_Pieces")
    if c is None:
        c = bpy.data.collections.new("VKI_Pieces")
        c.hide_viewport = True; c.hide_render = True
        c.use_fake_user = True
    sc = vki_scene("VKI_Test")
    if c.name not in sc.collection.children:
        sc.collection.children.link(c)
    return c


def vki_build_tmp(n, fn, kw, coll, tmp):
    k = VKIKit(n)
    fn(k)
    for f in k.bm.faces:
        if all(l[k.uv].uv.length == 0 for l in f.loops):
            k.project([f], f.material_index)
    return k.finish(tmp, coll, **kw)


def vki_copy_into(base, tmp):
    """geometry, materials and custom props of tmp -> base (same mesh datablock, so instances update); frees tmp"""
    me = base.data
    bm = bmesh.new(); bm.from_mesh(tmp.data); bm.to_mesh(me); bm.free()
    mats = list(tmp.data.materials)
    while len(me.materials) > len(mats):
        me.materials.pop()
    while len(me.materials) < len(mats):
        me.materials.append(mats[len(me.materials)])
    for i, m in enumerate(mats):
        me.materials[i] = m
    for k_ in [k_ for k_ in base.keys() if k_.startswith("vki_") or k_ in ("kit", "grid_m", "hinge_axis")]:
        if k_ not in tmp:
            del base[k_]
    for k_, v_ in tmp.items():
        base[k_] = v_
    tmd = tmp.data
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(tmd)
    return base


def vki_rebuild(names=None):
    """build VKI_SPECS pieces (all, or `names`) into a temp object and copy into the master in VKI_Pieces
    (instances update); new masters are created hidden in VKI_Pieces; then VARI_* meshes refresh."""
    sm = vki_spec_map()
    if names is not None:
        names = [names] if isinstance(names, str) else list(names)
        miss = [n for n in names if n not in sm]
        if miss:
            raise KeyError(f"not in VKI_SPECS: {miss}")
    todo = [n for n in sm if names is None or n in names]
    coll = vki_pieces_coll()
    out = []
    old_meta = {}
    for n in todo:
        if not n.startswith("SM_VKI_"):
            raise ValueError(f"{n}: VKI pieces are named SM_VKI_*")
        base = bpy.data.objects.get(n)
        if base is not None and coll.name not in [c.name for c in base.users_collection]:
            raise RuntimeError(f"{n} lives in {[c.name for c in base.users_collection]}: vki_adopt it first")
        _, fn, kw, pkg = sm[n]
        tmp = vki_build_tmp(n, fn, kw, coll, "__vki_tmp__")
        if base is None:
            tmp.name = n; tmp.data.name = n
            tmp.hide_viewport = tmp.hide_render = True
            base = tmp
        else:
            old_meta[n] = {k_: base[k_] for k_ in base.keys() if vki_is_meta_key(k_)}
            vki_copy_into(base, tmp)
        out.append(base)
    vki_refresh_variants(set(todo))
    vki_refresh_instances(out, old_meta)
    return out


# instance keys that belong to the placement, never to the master (vki_rebuild keeps them; T10i ignores them)
VKI_PLACEMENT_KEYS = ("vki_piece", "vki_rot", "vki_at", "vki_style", "vki_back_line", "vki_back_y", "vki_reuse",
                      "vki_mount", "vki_target", "vki_prompt", "vki_facing_min", "vki_leaf_state", "vki_leaf_deg",
                      "vki_spawn_id", "vki_facing_deg", "vki_class_override", "vki_warn_ok")
VKI_PLACEMENT_PREFIXES = ("vki_host", "vki_hug", "vki_link")


def vki_is_meta_key(k_):
    return k_.startswith("vki_") or k_ in ("kit", "grid_m", "hinge_axis")


def vki_is_placement_key(k_):
    return k_ in VKI_PLACEMENT_KEYS or k_.startswith(VKI_PLACEMENT_PREFIXES)


def vki_instances_of(base):
    """objects that instance a master: data is the master mesh, or a VARI_* mesh whose vki_base is the master"""
    out = []
    for o in bpy.data.objects:
        if o is base or o.type != "MESH" or o.data is None:
            continue
        if o.data == base.data or (o.data.name.startswith("VARI_") and o.data.get("vki_base") == base.name):
            out.append(o)
    return out


def vki_refresh_instances(bases, old_meta=None):
    """core fix (review r2): re-copy each master's metadata onto its instances after a rebuild (instances share the
    mesh, so their geometry updated, but vki_place copied the props only once -> stale footprints / lights /
    colliders in the FBX). Placement-only keys (VKI_PLACEMENT_KEYS / _PREFIXES) stay; master keys that the rebuild
    dropped are removed; instance-only keys added at placement (**props) are kept. Returns the refreshed count."""
    old_meta = old_meta or {}
    n = 0
    for base in bases:
        new = {k_: base[k_] for k_ in base.keys() if vki_is_meta_key(k_)}
        gone = set(old_meta.get(base.name, {})) - set(new)
        for o in vki_instances_of(base):
            for k_ in gone:
                if k_ in o.keys() and not vki_is_placement_key(k_):
                    del o[k_]
            for k_, v_ in new.items():
                if vki_is_placement_key(k_):
                    continue
                if o.get("vki_reuse") and k_ == "vki_class":
                    continue
                o[k_] = v_
            n += 1
    return n


def vki_adopt(names):
    """move package masters from WS_vki_<pkg>_Pieces into VKI_Pieces (hidden, at the origin)"""
    coll = vki_pieces_coll()
    out = []
    for n in ([names] if isinstance(names, str) else names):
        if not n.startswith("SM_VKI_"):
            raise ValueError(n)
        o = bpy.data.objects[n]
        cs = [c for c in o.users_collection]
        if any(not (c.name == coll.name or (c.name.startswith("WS_vki_") and c.name.endswith("_Pieces"))) for c in cs):
            raise RuntimeError(f"{n} is in {[c.name for c in cs]}: only WS_vki_*_Pieces masters are adopted")
        for c in cs:
            if c.name != coll.name:
                c.objects.unlink(o)
        if coll.name not in [c.name for c in o.users_collection]:
            coll.objects.link(o)
        o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0)
        o.hide_viewport = o.hide_render = True
        out.append(o)
    return out


# ---------------------------------------------------------------- placement (§5)
def vki_mw(o):
    """world matrix computed from location/rotation/scale (matrix_world is stale for objects created or moved in
    the same call until the depsgraph of their scene updates)"""
    m = o.matrix_basis.copy()
    if o.parent is not None:
        m = vki_mw(o.parent) @ o.matrix_parent_inverse @ m
    return m


def vki_wall_segments(objs):
    """wall instances -> [dict(p0, p1, cls, thick, height, H, name)] in world XY (walls run local x 0..L)"""
    out = []
    for o in objs:
        if o.get("vki_class") != "wall" or o.get("vki_len") is None:
            continue
        L = float(o["vki_len"])
        mw = vki_mw(o)
        p0 = (mw @ Vector((0, 0, 0))).to_2d(); p1 = (mw @ Vector((L, 0, 0))).to_2d()
        th = float(o.get("vki_thick", 0.5))
        fam = o.get("vki_family")
        ht = o.get("vki_height", "Full")
        H = VKI_CUT_H if ht == "Cut" else VKI_H_FULL.get(fam, 3.0)
        out.append(dict(p0=p0, p1=p1, cls="P" if th < 0.4 else "O", thick=th, height=ht, H=H, name=o.name))
    return out


def vki_scene_objs(coll):
    """all objects of the scene(s) that contain collection coll (for the wall search)"""
    for sc in bpy.data.scenes:
        if coll.name == sc.collection.name or coll.name in [c.name for c in sc.collection.children_recursive]:
            return list(sc.objects)
    return list(coll.all_objects)


def vki_local_box(src):
    """(x0, y0, z0, x1, y1, z1) of a master's mesh in local space"""
    bb = [Vector(c) for c in src.bound_box]
    return (min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb),
            max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb))


def vki_place(coll, piece, x, y, rot=0, z=0, style=None, mount=None, walls=None, wall_cls=None, hug=None,
              name=None, **props):
    """instance of `piece` in `coll` at (x, y) (world, rotation in degrees). Copies the master's metadata onto the
    instance, then **props (lists/dicts become JSON). Reused exterior props (SM_VK_*) get VKI_REUSE_STYLE and are
    positioned from their bbox (bbox centre on the point). Mounts:
      floor / table: origin (VKI) or bbox centre (reused) on (x, y); table: z is the table-top height.
      wall_floor: the back (vki_back_y, else bbox max y) goes on the proud line of the wall behind the point
        (0.285 O / 0.185 P); the wall is searched in `walls` (objects; default the scene's wall instances), else the
        next grid line with class wall_cls (default "O"). Then 'hug' slides along the wall (<= 0.30) off side walls'
        proud lines and records vki_hug.
      wall_hung: back on the wall face (T/2); z = the z argument (geometry is authored at its real height, 0 by
        default); vki_mount_ref="top": z = H - vki_mount_offset (default 0.25). Records vki_host, vki_host_height.
    Structure pieces (walls/posts/floors/links) are placed by origin with no mount logic."""
    src = bpy.data.objects[piece]
    reuse = piece.startswith("SM_VK_") and not piece.startswith("SM_VKI_")
    st = dict(VKI_REUSE_STYLE) if reuse else {}
    st.update(style or {})
    me = vki_variant_mesh(piece, st) if st else src.data
    o = bpy.data.objects.new(name or piece + "_inst", me)
    coll.objects.link(o)
    for k_, v_ in src.items():
        o[k_] = v_
    cls = src.get("vki_class", "prop")
    if reuse:
        o["vki_class"] = "prop"; cls = "prop"
        o["vki_reuse"] = 1
    mount = mount or src.get("vki_mount") or (VKI_REUSE.get(piece, {}).get("mount") if reuse else None)
    r = math.radians(rot)
    a = Vector((math.cos(r), math.sin(r))); b = Vector((-math.sin(r), math.cos(r)))    # along, back
    P = Vector((x, y))
    bx = vki_local_box(src)
    cx = (bx[0] + bx[3]) / 2 if reuse else 0.0
    cy = (bx[1] + bx[4]) / 2 if reuse else 0.0
    zz = z
    info = {}
    if cls in ("prop", "overlay", "fx") and mount in ("wall_floor", "wall_hung"):
        back_l = float(src["vki_back_y"]) if "vki_back_y" in src else bx[4]
        objl = walls if walls is not None else vki_scene_objs(coll)
        segs = vki_wall_segments(objl)
        pa, pb = P.dot(a), P.dot(b)
        best = None
        for sg in segs:
            d = sg["p1"] - sg["p0"]
            if d.length < 1e-6 or abs(d.normalized().dot(b)) > 1e-3:
                continue                                     # not parallel to the back wall
            wb = sg["p0"].dot(b)
            if wb - pb <= 1e-6:
                continue                                     # behind the point, not ahead
            s0, s1 = sorted((sg["p0"].dot(a), sg["p1"].dot(a)))
            if not (s0 - 1e-4 <= pa <= s1 + 1e-4):
                continue
            if best is None or wb < best[0]:
                best = (wb, sg)
        if best is None:
            wb = math.floor(pb / VKI_IG + 1e-6) * VKI_IG + VKI_IG
            wc = wall_cls or "O"; H = VKI_H_FULL["Timber"]; wall_name = None; ht = None
        else:
            wb, sg = best; wc = sg["cls"]; H = sg["H"]; wall_name = sg["name"]; ht = sg["height"]
        if mount == "wall_floor":
            gap = VKI_PROUD_LINE[wc]
        else:
            gap = VKI_T[wc] / 2
            if src.get("vki_mount_ref") == "top":            # e.g. Tapestry_300: rod at H - offset
                zz = H - float(src.get("vki_mount_offset", 0.25))
            info["vki_host_height"] = ht or ""
            info["vki_host_H"] = H
        ob = wb - gap - back_l
        oa = pa - cx
        # hug: side walls (perpendicular to the back wall) whose proud line the prop would cross
        slide = 0.0
        do_hug = (mount == "wall_floor") if hug is None else hug
        if do_hug:
            half = (bx[3] - bx[0]) / 2
            b_lo, b_hi = ob + bx[1], ob + back_l
            lo, hi = pa - half, pa + half
            need = []                                               # (slide, limiter)
            for sg in segs:
                d = sg["p1"] - sg["p0"]
                if d.length < 1e-6 or abs(d.normalized().dot(a)) > 1e-3:
                    continue
                sa = sg["p0"].dot(a)
                t0, t1 = sorted((sg["p0"].dot(b), sg["p1"].dot(b)))
                if t1 < b_lo - 1e-4 or t0 > b_hi + 1e-4:
                    continue
                pl = VKI_PROUD_LINE[sg["cls"]]
                if sa >= pa and hi > sa - pl:
                    need.append(((sa - pl) - hi, sg["name"]))       # slide toward -a
                elif sa < pa and lo < sa + pl:
                    need.append(((sa + pl) - lo, sg["name"]))       # slide toward +a
            # core fix (review r2): post squares reach POST_HW (0.31 O / 0.21 P) from the wall lines, past the proud
            # line (0.285 / 0.185), so a prop hugged to a side wall's proud line sat 25 mm inside the Corner post.
            # Keep 0.005 clear of (1) every placed post whose square reaches the prop's back strip and (2) every
            # junction node on the back wall line (a perpendicular wall ends there: an L/T/X node, which must carry a
            # Corner post, §2.3 / T12), in case posts are placed after props. The limiter is recorded in vki_hug_limit.
            squares = []
            for p_ in [o_ for o_ in objl if o_.get("vki_class") == "post"]:
                pm = vki_mw(p_)
                cs = [(pm @ Vector(c_)).to_2d() for c_ in p_.bound_box]
                squares.append((min(c_.dot(a) for c_ in cs), max(c_.dot(a) for c_ in cs),
                                min(c_.dot(b) for c_ in cs), max(c_.dot(b) for c_ in cs), p_.name))
            if best is not None:
                for sg in segs:
                    d = sg["p1"] - sg["p0"]
                    if d.length < 1e-6 or abs(d.normalized().dot(a)) > 1e-3:
                        continue
                    for e_ in (sg["p0"], sg["p1"]):
                        if abs(e_.dot(b) - wb) < 1e-4:
                            ph = VKI_POST_HW["O" if "O" in (sg["cls"], wc) else "P"]
                            na = e_.dot(a)
                            squares.append((na - ph, na + ph, wb - ph, wb + ph,
                                            "Corner post @ %.2f,%.2f" % (e_.x, e_.y)))
            for pa0, pa1, pb0, pb1, pn in squares:
                if pb1 < b_lo + 1e-6 or pb0 > b_hi - 1e-6 or pa1 < lo - 0.30 - 0.005 or pa0 > hi + 0.30 + 0.005:
                    continue
                pcen = (pa0 + pa1) / 2
                if pa0 > lo + 1e-6 and pa1 < hi - 1e-6:
                    info["vki_hug_fail"] = f"{pn} inside the prop's span"
                elif pcen >= pa and hi > pa0 - 0.005:
                    need.append(((pa0 - 0.005) - hi, pn))
                elif pcen < pa and lo < pa1 + 0.005:
                    need.append(((pa1 + 0.005) - lo, pn))
            need = [nd_ for nd_ in need if abs(nd_[0]) > 1e-9]
            if need and "vki_hug_fail" not in info:
                neg = [nd_ for nd_ in need if nd_[0] < 0]; pos = [nd_ for nd_ in need if nd_[0] > 0]
                slide, lim = min(neg) if neg and not pos else (max(pos) if pos and not neg else (0.0, None))
                if neg and pos:
                    info["vki_hug_fail"] = "walls or posts on both sides"
                    slide = 0.0
                elif abs(slide) > 0.30 + 1e-6:
                    info["vki_hug_fail"] = "needs %.3f (%s)" % (slide, lim)
                    slide = 0.0
                if slide:
                    info["vki_hug"] = round(slide, 4)
                    info["vki_hug_limit"] = lim
        O = a * (oa + slide) + b * ob
        o.location = (O.x, O.y, zz)
        info["vki_back_y"] = back_l
        bl_ = wb - gap                                       # the back plane, as a world line x = .. or y = ..
        info["vki_back_line"] = json.dumps(["x", round(bl_ * (1 if b.x > 0 else -1), 4)] if abs(b.x) > 0.5 else
                                           ["y", round(bl_ * (1 if b.y > 0 else -1), 4)])
        if wall_name:
            info["vki_host"] = wall_name
    elif cls in ("prop", "overlay", "fx"):
        O = P - (a * cx + b * cy)
        slide = Vector((0, 0))
        if hug:                                              # floor prop: push off nearby walls' proud lines
            segs = vki_wall_segments(walls if walls is not None else vki_scene_objs(coll))
            corners = [Vector((bx[0], bx[1])), Vector((bx[3], bx[1])), Vector((bx[3], bx[4])), Vector((bx[0], bx[4]))]
            wc_ = [O + a * c.x + b * c.y for c in corners]
            lo = [min(p.x for p in wc_), min(p.y for p in wc_)]
            hi = [max(p.x for p in wc_), max(p.y for p in wc_)]
            need = ([], [])
            for sg in segs:
                pl = VKI_PROUD_LINE[sg["cls"]]
                for ax in (0, 1):                                # ax 0: N-S wall (pushes x), 1: E-W wall (pushes y)
                    if abs(sg["p0"][ax] - sg["p1"][ax]) > 1e-6:
                        continue
                    w_ = sg["p0"][ax]; t0, t1 = sorted((sg["p0"][1 - ax], sg["p1"][1 - ax]))
                    if t1 < lo[1 - ax] or t0 > hi[1 - ax] or w_ < lo[ax] - pl or w_ > hi[ax] + pl:
                        continue
                    if (lo[ax] + hi[ax]) / 2 >= w_:              # prop on the + side of the wall line
                        if lo[ax] < w_ + pl:
                            need[ax].append(w_ + pl - lo[ax])
                    elif hi[ax] > w_ - pl:
                        need[ax].append(w_ - pl - hi[ax])
            fail = []
            for ax in (0, 1):
                if need[ax]:
                    if min(need[ax]) < 0 < max(need[ax]):
                        fail.append("walls on both sides")
                    else:
                        slide[ax] = max(need[ax], key=abs)
            if slide.length > 0 or fail:
                if fail or max(abs(slide.x), abs(slide.y)) > 0.30 + 1e-6:
                    info["vki_hug_fail"] = ", ".join(fail) or "needs %.3f,%.3f" % tuple(slide)
                else:
                    O = O + slide
                    info["vki_hug"] = json.dumps([round(slide.x, 4), round(slide.y, 4)])
        o.location = (O.x, O.y, zz)
    else:
        o.location = (x, y, z)
    o.rotation_euler = (0, 0, r)
    o["vki_piece"] = piece
    o["vki_rot"] = rot
    o["vki_at"] = json.dumps([round(x, 4), round(y, 4)])          # the requested lattice point (T11)
    if st:
        o["vki_style"] = json.dumps(vki_style_norm(st), sort_keys=True)
    if mount:
        o["vki_mount"] = mount
    for k_, v_ in info.items():
        o[k_] = v_
    for k_, v_ in props.items():
        o[vki_meta_key(k_)] = vki_prop(v_)
    return o


# ---------------------------------------------------------------- scenes, worlds, lights (§6)
VKI_PRESETS = {
    # G1 (core fix): Day world 0.55 -> 0.65, fill 0.5 -> 0.6 (+ the FlagRustic lift): walkable floor >= 0.25
    "Day": dict(world=(0.52, 0.50, 0.46), world_strength=0.65, key=1.0, key_color=(1.0, 0.95, 0.88),
                fill=0.6, fill_color=(0.85, 0.90, 1.0), window_w=1000.0, window_color=(.82, .88, 1.0)),
    # G1 (core fix): the fire takes charge at night -- cold key 0.8 -> 0.5 (fewer hard moon shadows of the caps),
    # fill / world make up the floor (>= 0.15), hearth 400 W with a 0.40 m radius (vki_fam_timber).
    # VKI_NIGHT_SPEC keeps the §6 start values (darker, moodier) as the alternative.
    "Night": dict(world=(0.10, 0.12, 0.20), world_strength=0.8, key=0.5, key_color=(.62, .70, 1.0),
                  fill=0.8, fill_color=(.62, .70, 1.0), window_w=150.0, window_color=(.62, .70, 1.0)),
    # dungeon kit: underground, so no sun to speak of -- a dim cold key keeps the forms, the torches and braziers
    # (vki_lights sockets) carry the warm light, and light shafts fall through the grates (their Day sockets)
    "Dungeon": dict(world=(0.10, 0.11, 0.15), world_strength=0.90, key=0.45, key_color=(.62, .70, 1.0),
                    fill=0.95, fill_color=(.62, .70, 1.0), window_w=700.0, window_color=(.78, .86, 1.0)),
    # adventure kit: natural caves, lit by glowing crystals and fungus more than by torches -- a stronger cold key
    # (the Dungeon key left the rock tops too close to the floor, palette rule caps >= floor + 0.15)
    "Cavern": dict(world=(0.09, 0.11, 0.14), world_strength=0.90, key=0.85, key_color=(.58, .74, 1.0),
                   fill=0.95, fill_color=(.60, .72, 1.0), window_w=700.0, window_color=(.78, .86, 1.0)),
    # sewer kit: torch-lit tunnels with a faint green cast (the Dungeon key left the brick paving under the dark target)
    "Sewer": dict(world=(0.09, 0.11, 0.10), world_strength=0.90, key=0.70, key_color=(.66, .80, .72),
                  fill=0.95, fill_color=(.62, .76, .70), window_w=700.0, window_color=(.78, .86, 1.0)),
    # dwarf kit: the halls under the mountain, lit by braziers, forges and lava -- a cool stone-grey key and fill (a
    # warm key flattened the fires' warm pools), of about the same luminance as the first warm one
    "Hall": dict(world=(0.10, 0.10, 0.11), world_strength=0.90, key=0.55, key_color=(.90, .92, 1.0),
                 fill=0.95, fill_color=(.78, .80, .86), window_w=700.0, window_color=(.78, .86, 1.0)),
    # mine kit: galleries lit by lanterns on the timber sets -- a dim neutral key and fill, the lanterns' warm pools
    "Mine": dict(world=(0.09, 0.09, 0.10), world_strength=0.90, key=0.60, key_color=(.84, .86, .95),
                 fill=0.95, fill_color=(.72, .74, .82), window_w=700.0, window_color=(.78, .86, 1.0)),
}
VKI_DARK_PRESETS = ("Night", "Dungeon", "Cavern", "Sewer", "Hall", "Mine")   # floor-level target 0.15 (vki_check), torch-lit
VKI_NIGHT_SPEC = dict(world_strength=0.35, key=0.35, fill=0.2)     # §6 start values (moodier, darker)
VKI_KEY_DIR = (-0.1797, -0.4338, 0.8829)       # toward the light: elevation 62 deg, from the SSW (azimuth 202.5)
VKI_FILL_DIR = (0.0, -0.6428, 0.7660)          # toward the camera: the fill shines along the view direction


VKI_FIT_MARGIN = 0.4                           # core fix: far margin added to the §1 D_fit (north caps / post tops)


def vki_fit_camera(bounds, fam="Timber", h_fit=None, margin=None):
    """§1 fit camera with the far margin: bounds (x_W, y_S, x_E, y_N) of the room's wall lines ->
    dict(mode, D, target, h_fit, margin). D_fit = (L + 1.5 + margin + 1.428 h_fit) / 0.737, D >= (W + 1) / 0.778,
    D = max(D, 14); fit when D <= 22 (target x = room centre, y_t = y_S - 1.5 + 0.2856 D), else follow (D 22).
    The plain §1 formula puts the north wall LINE on the top frame edge, so the caps (+0.28) and post tops (+0.31)
    of the north wall were cut off; the margin (0.4) is added when h_fit is the full wall height (Timber, Stone,
    Board 3.0, Wattle 2.4). Ashlar's h_fit (3.97) is a feature height below its 4.5 m wall top, whose top leaves the
    frame by design, so it gets no margin (the chapel stays a fit scene at D 21.94)."""
    x0, y0, x1, y1 = bounds
    L, W = y1 - y0, x1 - x0
    fd = VKI_FAMILIES.get(fam, VKI_FAMILIES["Timber"])
    h = fd["h_fit"] if h_fit is None else h_fit
    if margin is None:
        margin = VKI_FIT_MARGIN if abs(h - fd["H"]) < 1e-6 else 0.0
    D = max((L + 1.5 + margin + 1.428 * h) / 0.737, (W + 1.0) / 0.778, VKI_CAM["D"][0])
    mode = "fit" if D <= VKI_CAM["D"][1] + 1e-6 else "follow"
    if mode == "follow":
        D = VKI_CAM["D"][1]
    tgt = ((x0 + x1) / 2, y0 - 1.5 + 0.2856 * D, 0.0)
    return dict(mode=mode, D=round(D, 3), target=(round(tgt[0], 3), round(tgt[1], 3), 0.0), h_fit=h, margin=margin)


def vki_copy_rna(dst, src):
    for p in src.bl_rna.properties:
        if p.is_readonly or p.identifier in ("rna_type",):
            continue
        try:
            setattr(dst, p.identifier, getattr(src, p.identifier))
        except Exception:
            pass


def vki_world(preset="Day"):
    """W_VKI_Day / W_VKI_Night: camera rays see the void #0B0908, everything else the preset's lighting colour"""
    name = "W_VKI_" + preset
    pr = VKI_PRESETS[preset]
    w = bpy.data.worlds.get(name)
    if w is None:
        w = bpy.data.worlds.new(name)
        w.use_nodes = True
        nt = w.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputWorld"); out.location = (400, 0)
        lp = nt.nodes.new("ShaderNodeLightPath"); lp.location = (-300, 300)
        bl = nt.nodes.new("ShaderNodeBackground"); bl.label = "VKI_LIGHT"; bl.location = (-100, 50)
        bv = nt.nodes.new("ShaderNodeBackground"); bv.label = "VKI_VOID"; bv.location = (-100, -150)
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.location = (200, 0)
        nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
        nt.links.new(bl.outputs[0], mx.inputs[1]); nt.links.new(bv.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        w.use_fake_user = True
    nt = w.node_tree
    bl = next(n for n in nt.nodes if n.label == "VKI_LIGHT")
    bv = next(n for n in nt.nodes if n.label == "VKI_VOID")
    bl.inputs[0].default_value = (*pr["world"], 1); bl.inputs[1].default_value = pr["world_strength"]
    bv.inputs[0].default_value = (*VKI_VOID_LINEAR, 1); bv.inputs[1].default_value = 1.0
    w.color = pr["world"]
    return w


def vki_lights():
    """VKI_Key (SUN, 62 deg from the SSW, angle 8) and VKI_Fill (SUN, shadowless, along the view); Day values"""
    out = []
    for n, d, ang, sh in (("VKI_Key", VKI_KEY_DIR, 8.0, True), ("VKI_Fill", VKI_FILL_DIR, 2.0, False)):
        o = bpy.data.objects.get(n)
        if o is None:
            ld = bpy.data.lights.new(n, "SUN")
            o = bpy.data.objects.new(n, ld)
            ld.angle = math.radians(ang)
            ld.use_shadow = sh
            o.rotation_euler = Vector(d).to_track_quat("Z", "Y").to_euler()
            pr = VKI_PRESETS["Day"]
            ld.energy = pr["key"] if n == "VKI_Key" else pr["fill"]
            ld.color = pr["key_color"] if n == "VKI_Key" else pr["fill_color"]
        out.append(o)
    return out


def vki_link_lights(sc):
    for o in vki_lights():
        if o.name not in sc.collection.objects:
            sc.collection.objects.link(o)


def vki_apply_preset(sc, preset):
    """set the scene's world + the shared VKI_Key / VKI_Fill to a preset; returns a restore callable"""
    pr = VKI_PRESETS[preset]
    key, fill = vki_lights()
    old = (sc.world, key.data.energy, tuple(key.data.color), fill.data.energy, tuple(fill.data.color))
    sc.world = vki_world(preset)
    key.data.energy = pr["key"]; key.data.color = pr["key_color"]
    fill.data.energy = pr["fill"]; fill.data.color = pr["fill_color"]

    def restore():
        sc.world = old[0]
        key.data.energy, key.data.color, fill.data.energy, fill.data.color = old[1], old[2], old[3], old[4]
    return restore


def vki_scene(name, preset=None, sync=False):
    """interior scene: engine, EEVEE settings and view transform/look/exposure copied from VillageKit (on creation,
    or with sync=True), world W_VKI_<preset>, VKI_Key/VKI_Fill linked, 1920x1080. Never changes the window's scene."""
    src = bpy.data.scenes["VillageKit"]
    sc = bpy.data.scenes.get(name)
    new = sc is None
    if new:
        sc = bpy.data.scenes.new(name)
    if new or sync:
        sc.render.engine = src.render.engine
        vki_copy_rna(sc.eevee, src.eevee)
        sc.view_settings.view_transform = src.view_settings.view_transform
        sc.view_settings.look = src.view_settings.look
        sc.view_settings.exposure = src.view_settings.exposure
        sc.view_settings.gamma = src.view_settings.gamma
        sc.display_settings.display_device = src.display_settings.display_device
        sc.render.film_transparent = False
        sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
        sc.render.image_settings.file_format = "PNG"
    # C3: VillageKit renders with scene shadows off (eevee.use_shadows False). Interiors need them: the window spots
    # must be stopped by the walls and pass only through the glass (§4.3, §6), and G1 compares key shadows on / off
    # per light (VKI_Key.data.use_shadow), which only works with scene shadows on.
    if hasattr(sc.eevee, "use_shadows"):
        sc.eevee.use_shadows = True
    if preset or "vki_preset" not in sc:
        sc["vki_preset"] = preset or "Day"
    vki_link_lights(sc)
    sc.world = vki_world(sc["vki_preset"])
    return sc


def vki_scene_bounds(sc):
    """(x0, y0, x1, y1) of the visible mesh objects of a scene"""
    xs, ys = [], []
    for o in sc.objects:
        if o.type != "MESH" or o.hide_render or not o.visible_get(view_layer=sc.view_layers[0]):
            continue
        mw = vki_mw(o)
        for c in o.bound_box:
            p = mw @ Vector(c)
            xs.append(p.x); ys.append(p.y)
    if not xs:
        return (-1, -1, 1, 1)
    return (min(xs), min(ys), max(xs), max(ys))


def vki_flush_lights(sc):
    """make light / world changes made earlier in the same Python call reach the next render. Fix r1: without this,
    a light's energy or colour set in the same call as bpy.ops.render.render was ignored (measured: a hearth light
    set to 0 W rendered byte-identical to 300 W; set in a separate call, or after this flush, it rendered dark), so
    the preset switch in vki_shot / vki_lt_shot could render with the previous call's light values."""
    for o in sc.objects:
        if o.type == "LIGHT":
            o.data.update_tag()
    if sc.world is not None:
        sc.world.update_tag()
    dg = sc.view_layers[0].depsgraph    # None until the scene has been evaluated once (e.g. after a Blender restart):
    if dg is not None:                  # then there is no stale evaluated copy and the render builds from the data
        dg.update()


def vki_shot(scene, name, mode="game", D=None, target=None, preset=None, res=(1920, 1080), samples=None,
             bounds=None, px_per_m=None, loc=None, lens=None, margin=0.06, outdir=None):
    """render renders/interior/<scene>/<name>.png (or renders/interior/<outdir>/<name>.png) and return the path.
    mode "game": the §1 reference camera (pitch 50, lens 38, 36 mm AUTO sensor, clip 0.5/80) at
      target + (0, -0.643 D, 0.766 D); D default scene['vki_cam_dist'], else the §1 fit with the 0.4 m far margin
      (vki_fit_camera) when the scene has vki_room_bounds, else 18; target default scene['vki_cam_target'] or the
      origin.
    mode "plan": temporary ortho camera looking straight down (north up) over `bounds` (x0, y0, x1, y1; default
      scene['vki_bounds'] or the visible meshes) + margin; px_per_m sets the resolution (e.g. 200 = 2 px/cm).
    mode "free": perspective camera at `loc` looking at `target` (lens default 38).
    preset: "Day"/"Night" (default scene['vki_preset']); world, lights, camera, resolution, samples and file path
    are restored afterwards."""
    sc = bpy.data.scenes[scene] if isinstance(scene, str) else scene
    preset = preset or sc.get("vki_preset", "Day")
    cam_d = bpy.data.cameras.new("VKI_CamTmp")
    cam = bpy.data.objects.new("VKI_CamTmp", cam_d)
    sc.collection.objects.link(cam)
    cam_d.sensor_width = VKI_CAM["sensor"]; cam_d.sensor_fit = "AUTO"
    rx, ry = res
    if mode == "game":
        if D is None and "vki_cam_dist" not in sc and vki_get(sc, "vki_room_bounds", None):
            fit = vki_fit_camera(vki_get(sc, "vki_room_bounds"), sc.get("vki_family", "Timber"))
            D = fit["D"]; target = fit["target"] if target is None else target
        D = D or float(sc.get("vki_cam_dist", 18.0))
        t = Vector(target if target is not None else vki_get(sc, "vki_cam_target", [0, 0, 0]))
        if len(t) == 2:
            t = t.to_3d()
        p = math.radians(VKI_CAM["pitch"])
        cam.location = t + Vector((0, -math.cos(p) * D, math.sin(p) * D))
        cam.rotation_euler = (math.radians(90 - VKI_CAM["pitch"]), 0, 0)
        cam_d.type = "PERSP"; cam_d.lens = lens or VKI_CAM["lens"]
        cam_d.clip_start, cam_d.clip_end = VKI_CAM["clip"]
    elif mode == "plan":
        bb = bounds or vki_get(sc, "vki_bounds", None) or vki_scene_bounds(sc)
        x0, y0, x1, y1 = bb
        w, h = (x1 - x0) * (1 + 2 * margin), (y1 - y0) * (1 + 2 * margin)
        if px_per_m:
            rx, ry = max(16, int(round(w * px_per_m))), max(16, int(round(h * px_per_m)))
        cam_d.type = "ORTHO"
        cam_d.ortho_scale = max(w, h * rx / ry) if rx >= ry else max(h, w * ry / rx)
        cam.location = ((x0 + x1) / 2, (y0 + y1) / 2, 40.0)
        cam.rotation_euler = (0, 0, 0)
        cam_d.clip_start, cam_d.clip_end = 0.1, 100.0
    elif mode == "free":
        cam.location = Vector(loc)
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam_d.type = "PERSP"; cam_d.lens = lens or VKI_CAM["lens"]
        cam_d.clip_start, cam_d.clip_end = VKI_CAM["clip"][0], 200.0
    else:
        raise ValueError(mode)
    old = (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage,
           sc.render.filepath, sc.eevee.taa_render_samples, sc.render.image_settings.file_format)
    restore = vki_apply_preset(sc, preset)
    d = os.path.join(VKI_RENDERS, outdir or sc.name)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, name + ".png")
    try:
        sc.camera = cam
        sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = rx, ry, 100
        sc.render.filepath = fp
        sc.render.image_settings.file_format = "PNG"
        if samples:
            sc.eevee.taa_render_samples = samples
        vki_flush_lights(sc)
        bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        (sc.camera, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage,
         sc.render.filepath, sc.eevee.taa_render_samples, sc.render.image_settings.file_format) = old
        restore()
        bpy.data.objects.remove(cam)
        bpy.data.cameras.remove(cam_d)
    return fp


def vki_rig(name, items, origin=(0.0, 0.0), scene="VKI_Test", clear=True):
    """lay out instances for seam boards / tests: collection VKI_Rig_<name> in `scene` (cleared first),
    items = [(piece, x, y, rot[, style])] relative to origin. Returns the objects."""
    sc = vki_scene(scene)
    cn = "VKI_Rig_" + name
    c = bpy.data.collections.get(cn)
    if c is None:
        c = bpy.data.collections.new(cn)
    if c.name not in sc.collection.children:
        sc.collection.children.link(c)
    if clear:
        for o in list(c.objects):
            bpy.data.objects.remove(o)
    out = []
    for it in items:
        piece, x, y, rot = it[:4]
        st = it[4] if len(it) > 4 else None
        out.append(vki_place(c, piece, origin[0] + x, origin[1] + y, rot, style=st, walls=[]))
    return out


# ---------------------------------------------------------------- workshop scenes (§7)
def vki_ws(agent):
    """WS_vki_<agent>: ws_scene + W_VKI_Day, ground hidden, VK_Sun unlinked (this scene only), VKI lights linked"""
    wg = {}
    exec(bpy.data.texts["ws_common"].as_string(), wg)
    sc, coll, asm = wg["ws_scene"]("vki_" + agent)
    if "vki_preset" not in sc:
        sc["vki_preset"] = "Day"
    sc.world = vki_world(sc["vki_preset"])
    gr = bpy.data.objects.get(sc.name + "_Ground")
    if gr is not None:
        gr.hide_render = True; gr.hide_viewport = True
    sun = bpy.data.objects.get("VK_Sun")
    if sun is not None and sun.name in sc.collection.objects:
        sc.collection.objects.unlink(sun)
    vki_link_lights(sc)
    return sc, coll, asm


def vki_ws_build(agent, names=None, row_spacing=None):
    """build your package's VKI_SPECS (pkg == agent, or `names`) into WS_vki_<agent>_Pieces (visible masters).
    Refuses non-SM_VKI_ names and names that exist outside your pieces collection."""
    sc, coll, asm = vki_ws(agent)
    if isinstance(names, str):
        names = [names]
    specs = [sp for sp in VKI_SPECS if (sp[0] in names if names else sp[3] == agent)]
    if names:
        miss = set(names) - {sp[0] for sp in specs}
        if miss:
            raise KeyError(f"not in VKI_SPECS: {sorted(miss)}")
    built = []
    for n, fn, kw, pkg in specs:
        if not n.startswith("SM_VKI_"):
            raise ValueError(f"{n}: VKI pieces are named SM_VKI_*")
        base = bpy.data.objects.get(n)
        if base is not None and [c.name for c in base.users_collection] != [coll.name]:
            raise RuntimeError(f"{n} already exists in {[c.name for c in base.users_collection]}: not yours")
        tmp = vki_build_tmp(n, fn, kw, coll, "__vki_wstmp_" + agent)
        if base is None:
            tmp.name = n; tmp.data.name = n; base = tmp
        else:
            vki_copy_into(base, tmp)
        built.append(base)
    if row_spacing:
        for i, o in enumerate(built):
            o.location = (i * row_spacing, 0, 0)
    return built


def vki_ws_shot(agent, name, mode="game", **kw):
    """vki_shot on WS_vki_<agent> (renders/interior/WS_vki_<agent>/<name>.png)"""
    vki_ws(agent)
    return vki_shot("WS_vki_" + agent, name, mode, **kw)
