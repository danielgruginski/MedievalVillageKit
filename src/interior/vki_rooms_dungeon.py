# ===================== VKI ROOMS DUNGEON: the dungeon kit's showcase levels (docs/DUNGEON_KIT.md) =====================
# Loaded by vki_ns() right after vki_rooms, whose tables it extends: VKI_PLANS / VKI_ROOMS get two linked levels, built
# and checked like every interior (vki_build_scene, vki_check, vki_rooms_shots). They are not in VKI_ROOMS_SCENES (the
# nine interiors); build them with vki_build_all(VKI_DUNGEON_SCENES).
#   VKI_Dungeon_B1  the gaol, 10 x 6: a stone stair up to the surface (the exit, @return), two barred cells under the
#                   north wall's light grates, a barred holding pen in the SE, the guard table, a brazier, and the
#                   stone stair down to the crypt in the NE
#   VKI_Dungeon_B2  the crypt, 10 x 6: the stair up (same origin and rotation as B1's stair down), ossuary niches in the
#                   north and side walls, four cut pillars round a sarcophagus, coffins, tomb slabs, a barred treasure
#                   vault in the SW; a breach in the east wall (a passage) leads on to the adventure kit's B3
# Plan legend additions (vki_rooms): "||" / "|" bars, "gg" / "g" barred gate (Bars family), "NN" / "N" ossuary niche
# (Full), "nn" / "n" (Cut). Stairs take a sixth field, the piece variant ("Stone"). Every top-level name starts with
# vki_/VKI_ (T18).

VKI_DUNGEON_SCENES = ["VKI_Dungeon_B1", "VKI_Dungeon_B2"]

VKI_PLANS.update({
    "VKI_Dungeon_B1": """
      0  1  2  3  4  5  6  7  8  9
     +##+##+WW+##+##+WW+##+##+##+##+
   5 #^^rCG:st ..:sk st:ba vv vv vv#
     +                             +
   4 #^^r..:bu ..:bo ..:.. .. .. Sd#
     +      ||+gg+||+gg+           +
   3 #^^r.. .. .. .. .. .. .. .. ..#
     +                        ||+||+
   2 #Ss .. .. .. BR .. .. pd|.. sk#
     +                             +
   1 #WR .. tb .. .. .. .. ..g.. ..#
     +                             +
   0 tba .. .. pd dg .. RB ..:bu stt
     +==+==+==+==+==+==+==+==+==+==+
""",
    "VKI_Dungeon_B2": """
      0  1  2  3  4  5  6  7  8  9
     +##+NN+##+NN+##+NN+##+##+##+##+
   5 N.. .. sk .. .. cn Su ^^ ^^ ^^#
     +                             +
   4 #.. bo .. PI .. .. .. PI cn ..N
     +                             +
   3 N.. ts .. .. NC NC .. .. ts ..P
     +                             +
   2 #.. .. .. PI .. .. .. PI .. ..N
     +||+gg+                       +
   1 #TR ..|.. CF CF .. CF CF .. ..#
     +                             +
   0 tcn ..:.. .. .. .. .. pd RB RBt
     +==+==+==+==+==+==+==+==+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Dungeon_B1": dict(
        building="Dungeon", floor=-1, preset="Dungeon", family=dict(perimeter="Dungeon", partition="Dungeon"),
        partition_wall="zone", pools=False,
        debris=dict(density=0.26, seed=11, themes={"cells": "dungeon"}),     # loose debris (vki_props_debris)
        zones={"cells": dict(cells=[(2, 5, 4, 5), (8, 9, 0, 2)], floor="EarthDamp", wall="DungeonInDamp"),
               "hall": dict(cells="rest", floor="DungeonFlag", wall="DungeonIn")},
        stairs=[("Up", 0.0, 4.5, 0, "surface", "Stone"), ("Down", 10.5, 9.0, -90, "crypt", "Stone")],
        links=[("surface", "stair_up", "@return"), ("crypt", "stair_down", "VKI_Dungeon_B2")],
        spawns={"surface": (0.75, 3.75, 180), "crypt": (14.25, 6.75, 180)},
        props=[("Cage", 2.25, 7.5, 0, None, None),          # clear of the NW corner post of cell A
               ("Torch_Wall", 2.25, 8.25, 0, None, "wall_hung"),                   # lights the cage
               # cell A (x 3.0-6.0): straw under the grate, chains, the slop bucket
               ("Overlay_StrawPile", 3.75, 8.25, 0, None, None), ("Chains_Wall", 5.25, 8.25, 0, None, "wall_hung"),
               ("Bucket", 3.75, 6.75, 0, None, None),
               # cell B (x 6.0-9.0): a skeleton in chains, bones, straw under the second grate
               ("Skeleton_Sitting", 6.75, 8.25, 0, None, None), ("Chains_Wall", 6.75, 8.25, 0, None, "wall_hung"),
               ("Overlay_Bones", 6.75, 6.75, 0, None, None), ("Overlay_StrawPile", 8.25, 8.25, 0, None, None),
               # the nook before the stair down
               ("Barrel", 9.75, 8.25, 0, None, None), ("Torch_Wall", 9.75, 8.25, 0, None, "wall_hung"),
               # guard room
               ("Prop_WeaponRack", 0.75, 2.25, 90, None, "wall_floor", {"hug": True}),
               ("Barrel", 0.75, 0.75, 90, None, None),                             # use point to the east
               ("Table_Small", 3.75, 2.25, 0, None, None), ("TableDress_Guard", 3.75, 2.25, 0, None, "table", {"on": True}),
               ("Prop_Stool", 3.0, 2.25, 0, None, None), ("Prop_Stool", 4.5, 2.25, 0, None, None),
               ("Brazier", 6.75, 3.75, 0, None, None),
               ("Overlay_Puddle", 5.25, 0.75, 0, None, None), ("Overlay_DrainGrate", 6.75, 0.75, 0, None, None),
               ("Rubble", 9.75, 0.75, 0, None, None), ("Overlay_Puddle", 11.25, 3.75, 0, None, None),
               ("Torch_Wall", 0.75, 3.75, 90, None, "wall_hung"), ("Torch_Wall", 14.25, 5.25, -90, None, "wall_hung"),
               # the holding pen (x 12.0-15.0, y 0-4.5)
               ("Skeleton_Sitting", 14.25, 3.75, -90, None, None), ("Overlay_StrawPile", 14.25, 0.75, 0, None, None),
               ("Bucket", 12.75, 0.75, 0, None, None), ("Torch_Wall", 14.25, 2.25, -90, None, "wall_hung")]),
    "VKI_Dungeon_B2": dict(
        building="Dungeon", floor=-2, preset="Dungeon", family=dict(perimeter="Dungeon", partition="Dungeon"),
        partition_wall="zone", pools=False,
        debris=dict(density=0.26, seed=12),                                  # loose debris (vki_props_debris)
        gates={("EW", 1, 2): -90.0},            # the vault gate opens out into the nave (inside, it closed the chest off)
        zones={"vault": dict(cells=[(0, 1, 0, 1)], floor="DungeonFlag", wall="DungeonIn"),
               "crypt": dict(cells="rest", floor="DungeonFlagWarm", wall="DungeonInWarm")},
        stairs=[("Up", 10.5, 9.0, -90, "above", "Stone")],
        passages={("NS", 3, 10): "temple"},       # adventure kit: the breach on down to the sunken temple (B3)
        links=[("above", "stair_up", "VKI_Dungeon_B1"), ("temple", "passage", "VKI_Dungeon_B3")],
        spawns={"above": (9.75, 8.25, 270)},
        props=[("Skeleton_Sitting", 3.75, 8.25, 0, None, None), ("Candles_Floor", 8.25, 8.25, 0, None, None),
               ("Overlay_Bones", 2.25, 6.75, 0, None, None),
               ("Pillar_Cut", 4.5, 6.0, 0, None, None), ("Pillar_Cut", 4.5, 3.0, 0, None, None),
               ("Pillar_Cut", 10.5, 6.0, 0, None, None), ("Pillar_Cut", 10.5, 3.0, 0, None, None),
               # the nave: a necromancer's circle round the crypt's opened sarcophagus (a point of interest,
               # vki_props_poi; it brings its own tomb and candles)
               ("POI_NecroCircle", 7.5, 4.5, 0, None, None, {"hug": False}),
               ("Coffin", 6.0, 2.25, 0, None, None), ("Coffin", 10.5, 2.25, 0, None, None),
               ("Overlay_TombSlab", 1.5, 4.5, 90, None, None), ("Overlay_TombSlab", 13.5, 4.5, 90, None, None),
               ("Rubble", 13.5, 0.75, 0, None, None), ("Overlay_Puddle", 11.25, 0.75, 0, None, None),
               ("Torch_Wall", 0.75, 3.75, 90, None, "wall_hung"), ("Torch_Wall", 0.75, 6.75, 90, None, "wall_hung"),
               ("Torch_Wall", 14.25, 2.25, -90, None, "wall_hung"), ("Torch_Wall", 6.75, 8.25, 0, None, "wall_hung"),
               ("Candles_Floor", 12.9, 6.6, 0, None, None),       # by the breach (its wall lost a torch to the passage)
               # the treasure vault (x 0-3.0, y 0-3.0) behind bars
               # the chest faces the gate (its use point lands in the gate's inner cell); the lid, thrown back
               # against the west wall, is hugged off it
               ("Chest_Treasure", 0.75, 2.25, 90, None, None), ("Candles_Floor", 0.75, 0.75, 0, None, None)]),
})

VKI_ROOMS_CODES.update({"Cage": "CG", "Overlay_StrawPile": "st", "Bucket": "bu", "Skeleton_Sitting": "sk",
                        "Overlay_Bones": "bo", "Overlay_Puddle": "pd", "Overlay_DrainGrate": "dg", "Brazier": "BR",
                        "Rubble": "RB", "Pillar_Cut": "PI", "Pillar_Full": "PF", "Sarcophagus": "SA", "Coffin": "CF",
                        "Overlay_TombSlab": "ts", "Candles_Floor": "cn", "Chest_Treasure": "TR"})


# ---------------------------------------------------------------- VKI_Dungeon_Catalog (a viewer scene, like VKI_Catalog)
# every dungeon master, labelled, in rows by group, on a DungeonFlag floor, Day preset; a camera per group
# (VKI_DunCat_Cam_G<i>, the game pitch). Walls stand with Mid posts on their open ends; wall-mounted props hang on a
# plain wall. Rebuild: g["vki_dungeon_catalog"]() (clears and refills its collections).
VKI_DUNGEON_CATALOG = [
    ("Dungeon walls, Full, and rakes", 0.0,
     ["SM_VKI_Wall_Dungeon_Plain_150A_Full", "SM_VKI_Wall_Dungeon_Plain_150B_Full", "SM_VKI_Wall_Dungeon_Plain_300_Full",
      "SM_VKI_Wall_Dungeon_Window_150_Full", "SM_VKI_Wall_Dungeon_Niche_150_Full", "SM_VKI_Wall_Dungeon_Door_150_Full",
      "SM_VKI_Wall_Dungeon_DoorWide_300_Full", "SM_VKI_Wall_Dungeon_Rake_150_L", "SM_VKI_Wall_Dungeon_Rake_150_R"]),
    ("Dungeon walls, Cut; posts; the iron exit leaf", -6.0,
     ["SM_VKI_Wall_Dungeon_Plain_150A_Cut", "SM_VKI_Wall_Dungeon_Plain_300_Cut", "SM_VKI_Wall_Dungeon_Niche_150_Cut",
      "SM_VKI_Wall_Dungeon_Door_150_Cut", "SM_VKI_Wall_Dungeon_DoorWide_300_Cut", "SM_VKI_Post_Dungeon_Corner_Full",
      "SM_VKI_Post_Dungeon_Corner_Cut", "SM_VKI_Post_Dungeon_Mid_Full", "SM_VKI_Post_Dungeon_Mid_Cut"]),
    ("Bars, barred gate, posts; stone stairs", -16.0,
     ["SM_VKI_Wall_Bars_Plain_150A_Full", "SM_VKI_Wall_Bars_Door_150_Full", "SM_VKI_Wall_Bars_Plain_300_Full",
      "SM_VKI_Post_Bars_Corner_Full", "SM_VKI_Post_Bars_Mid_Full", "SM_VKI_Stair_Up_150x450_Stone",
      "SM_VKI_Stair_Down_150x450_Stone"]),
    ("Furniture", -24.0,
     ["SM_VKI_Prop_Sarcophagus", "SM_VKI_Prop_Coffin", "SM_VKI_Prop_Pillar_Full", "SM_VKI_Prop_Pillar_Cut",
      "SM_VKI_Prop_Cage", "SM_VKI_Prop_Brazier", "SM_VKI_Prop_Chest_Treasure", "SM_VKI_Prop_Rubble"]),
    ("Dressing and overlays", -30.0,
     ["SM_VKI_Prop_Torch_Wall", "SM_VKI_Prop_Chains_Wall", "SM_VKI_Prop_Skeleton_Sitting", "SM_VKI_Prop_Candles_Floor",
      "SM_VKI_Prop_Bucket", "SM_VKI_Prop_TableDress_Guard", "SM_VKI_Overlay_StrawPile", "SM_VKI_Overlay_Bones",
      "SM_VKI_Overlay_Puddle", "SM_VKI_Overlay_DrainGrate", "SM_VKI_Overlay_TombSlab"]),
]


def vki_dungeon_catalog():
    """(re)build VKI_Dungeon_Catalog; returns {group: camera name}"""
    return vki_kit_catalog("VKI_Dungeon_Catalog", VKI_DUNGEON_CATALOG, "VKI_DunCat_", "DungeonFlag")


def vki_kit_catalog(scene, groups, prefix, floor, host=("SM_VKI_Wall_Dungeon_Plain_150A_Full",
                                                        "SM_VKI_Post_Dungeon_Mid_Full"),
                    leaf_on=(("Door_150_Cut", 0.0), ("Bars_Door_150_Full", -60.0)), fy=(-36, 6)):
    """a kit catalog viewer scene (VKI_Dungeon_Catalog, VKI_Adventure_Catalog): groups [(title, y, [masters])] in rows,
    labelled, on Floor_600 tiles of style `floor` (fy: their y range), Day preset, a camera per group
    (<prefix>Cam_G<i>, the game pitch). Walls stand with Mid posts on their open ends; doors whose name ends with a
    leaf_on suffix show their vki_leaf at the socket, turned by the given angle; wall_hung and wall_floor props stand
    against a `host` wall (wall, Mid post); pits and ground tiles snap to the 1.5 grid and the floor leaves their cells
    open (Q150 tiles around them). Returns {group: camera name}."""
    sc = vki_scene(scene, preset="Day")
    colls = {}
    for suf in ("Pieces", "Labels", "Floor", "Cams"):
        n = prefix + suf
        c = bpy.data.collections.get(n) or bpy.data.collections.new(n)
        if c.name not in sc.collection.children:
            sc.collection.children.link(c)
        for o in list(c.objects):
            d = o.data
            bpy.data.objects.remove(o)
            if d is not None and d.users == 0 and isinstance(d, (bpy.types.Curve, bpy.types.Camera)):
                (bpy.data.curves if isinstance(d, bpy.types.Curve) else bpy.data.cameras).remove(d)
        colls[suf] = c
    lab = bpy.data.materials.get("M_VKI_CatalogLabel")

    def label(text, x, y, size, align="CENTER"):
        cu = bpy.data.curves.new(prefix + "Lbl", "FONT")
        cu.body = text; cu.size = size; cu.align_x = align
        if lab is not None:
            cu.materials.append(lab)
        o = bpy.data.objects.new(prefix + "Lbl_" + text[:40], cu)
        o.location = (x, y, 0.01)
        colls["Labels"].objects.link(o)
        return o

    def put(piece, x, y, rot=0.0, style=None, coll="Pieces"):
        return vki_place(colls[coll], piece, x, y, rot, style=style, mount="floor", walls=[], hug=False)

    cams = {}
    holes = []
    xmax = 0.0
    for gi, (title, y, names) in enumerate(groups):
        label(title, 0.0, y - 2.3, 0.45, "LEFT")
        x = 0.0
        for ni, n in enumerate(names):
            src = bpy.data.objects[n]
            bx = vki_local_box(src)
            w = bx[3] - bx[0]
            cls = src.get("vki_class")
            mnt = src.get("vki_mount")
            if cls == "wall":
                put(n, x, y)
                fam = src.get("vki_family")
                L = float(src.get("vki_len", 1.5))
                ht = src.get("vki_height")
                for ex, h in ((0.0, "Cut" if ht == "Rake" and n.endswith("_L") else ("Full" if ht == "Rake" else ht)),
                              (L, "Cut" if ht == "Rake" and n.endswith("_R") else ("Full" if ht == "Rake" else ht))):
                    pn = f"SM_VKI_Post_{fam}_Mid_{h}"
                    if bpy.data.objects.get(pn) is not None:
                        put(pn, x + ex, y)
                lf = vki_get(src, "vki_leaf", None)
                sk = vki_get(src, "vki_leaf_socket", None)
                for suf, deg in leaf_on:
                    if isinstance(lf, str) and n.endswith(suf) and sk:
                        s0 = sk[0] if isinstance(sk[0], list) else sk
                        put(lf, x + s0[0], y + s0[1], deg)
            elif mnt in ("wall_hung", "wall_floor"):
                put(host[0], x + w / 2 - 0.75, y + 0.25)      # face A at y
                for ex in (x + w / 2 - 0.75, x + w / 2 + 0.75):
                    put(host[1], ex, y + 0.25)
                put(n, x - bx[0], y - (float(src.get("vki_back_y", 0.0)) if mnt == "wall_floor" else 0.0))
            elif cls in ("pit", "ground"):           # on the cell grid, the floor left out under them
                x = math.ceil(x / VKI_IG - 1e-6) * VKI_IG
                put(n, x - bx[0], y - bx[1])
                holes.append((x, y, x + (bx[3] - bx[0]), y + (bx[4] - bx[1])))
            else:
                put(n, x - bx[0], y - (bx[4] if n.startswith("SM_VKI_Stair") else 0.0))
            label(n[7:], x + w / 2, y - (4.9 if n.startswith("SM_VKI_Stair") else 1.2) - 0.35 * (ni % 2), 0.16)
            x += max(w, 1.5 if mnt in ("wall_hung", "wall_floor") else 0.0) + 0.9
        xmax = max(xmax, x)
        cd = bpy.data.cameras.new(prefix + "Cam_G%d" % gi)
        cd.lens = VKI_CAM["lens"]; cd.sensor_width = VKI_CAM["sensor"]; cd.sensor_fit = "AUTO"
        cd.clip_start, cd.clip_end = 0.5, 150.0
        cam = bpy.data.objects.new(prefix + "Cam_G%d" % gi, cd)
        D = max(10.0, 1.2 * (x + 1.0) / 0.945)            # 20 % margin: near things look larger
        p = math.radians(VKI_CAM["pitch"])
        cam.location = (x / 2, y - 0.8 - math.cos(p) * D, math.sin(p) * D)
        cam.rotation_euler = (math.radians(90 - VKI_CAM["pitch"]), 0.0, 0.0)
        colls["Cams"].objects.link(cam)
        cams[title] = cam.name
    inside = lambda a0, b0, a1, b1: any(a0 >= h[0] - 1e-3 and b0 >= h[1] - 1e-3 and a1 <= h[2] + 1e-3 and
                                        b1 <= h[3] + 1e-3 for h in holes)
    over = lambda a0, b0, a1, b1: any(a0 < h[2] - 1e-3 and a1 > h[0] + 1e-3 and b0 < h[3] - 1e-3 and b1 > h[1] + 1e-3
                                      for h in holes)
    for fx in range(-6, int(xmax) + 6, 6):
        for fy_ in range(fy[0], fy[1], 6):
            if not over(fx, fy_, fx + 6, fy_ + 6):
                put("SM_VKI_Floor_600", float(fx), float(fy_), style={"floor": floor})
                continue
            for i in range(4):
                for j in range(4):
                    a0, b0 = fx + VKI_IG * i, fy_ + VKI_IG * j
                    if not inside(a0, b0, a0 + VKI_IG, b0 + VKI_IG):
                        put(f"SM_VKI_Floor_150_Q{i % 2}{j % 2}", a0, b0, style={"floor": floor})
    sc.camera = bpy.data.objects[cams[groups[0][0]]]
    for vl in sc.view_layers:
        if vl.depsgraph is not None:
            vl.depsgraph.update()
    return cams
