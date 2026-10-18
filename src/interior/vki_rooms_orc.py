# ===================== VKI ROOMS ORC: the orcs' halls (2026-10-18, MedievalSetting's orc chapter) =====================
# Loaded by vki_ns() right after vki_rooms_monastery. Every top-level name starts with vki_/VKI_ (T18).
#   VKI_Orc_Hall  a warlord's hall, 10 x 6 cells (15 x 9 m), the Orc log family (vki_fam_orc): the wide gate in the
#                 south wall, unglazed barred windows; his seat at the north end between two war standards, the war
#                 table before it, trophy walls in the north corners; the cook fire and its cauldron in the middle,
#                 split-log tables with benches down both sides, bunks along the west wall with furs, weapon racks on
#                 the east wall, a meat rack by the gate; torches; night. Plain Full runs take the hide-and-skull
#                 B variant (vki_rooms_layout's B rule).
#   VKI_Orc_Barracks  8 x 4 cells (12 x 6 m): bunks along the north and south walls, a table and benches in the
#                 middle, furs, weapon racks, a trophy wall, torches
#   VKI_Orc_Forge  6 x 4 cells (9 x 6 m), the wide gate: the clay forge with its bellows, the anvil, a quench barrel,
#                 ore and a heap of loot to melt, iron stock, a weapon rack
#   VKI_Orc_ShamanHut  4 x 4 cells (6 x 6 m): the skull altar at the end wall, a totem, drying herbs and charms on
#                 both side walls, a cauldron, furs
#   VKI_Orc_Pen   6 x 4 cells (9 x 6 m): two cages (one open), the stocks, chains on the wall with a dead man under
#                 them, refuse, the guard's bench and a water barrel

VKI_ORC_SCENES = ["VKI_Orc_Hall", "VKI_Orc_Barracks", "VKI_Orc_Forge", "VKI_Orc_ShamanHut", "VKI_Orc_Pen"]

VKI_PLANS.update({
    "VKI_Orc_Hall": """
      0  1  2  3  4  5  6  7  8  9
     +##+##+WW+##+##+##+##+WW+##+##+
   5 #ob .. .. BN TH TH BN .. .. ..#
     +                             +
   4 #ob .. .. .. wt wt .. .. .. OW#
     +                             +
   3 W.. oe ot oe .. .. oe ot oe ..W
     +                             +
   2 #.. oe ot oe OC OC oe ot oe ..#
     +                             +
   1 #ob .. .. .. .. .. .. .. .. OW#
     +                             +
   0 #of .. .. .. EE EE .. om om ..#
     +==+ww+==+==+EE+EE+==+==+ww+==+
""",
})

VKI_ROOMS.update({
    "VKI_Orc_Hall": dict(
        building="OrcHall", floor=0, preset="Night", family=dict(perimeter="Orc", partition="Orc"),
        zones={"hall": dict(cells="rest", floor="EarthSooty", wall="OrcLogs")},
        links=[("front", "exit", "@return")], spawns={"front": (7.5, 1.60, 0)},
        props=[("Orc_Throne", 7.5, 8.35, 0, None, "wall_floor", {"hug": True}),
               ("Orc_Banner", 5.0, 8.3, 0, None, None), ("Orc_Banner", 10.0, 8.3, 0, None, None),
               ("Orc_WarTable", 7.5, 6.35, 0, None, None),
               ("Orc_Trophies", 1.6, 8.25, 0, None, "wall_hung"), ("Orc_Trophies", 13.4, 8.25, 0, None, "wall_hung"),
               ("Orc_Cauldron", 7.5, 3.6, 0, None, None),
               ("Orc_Table_240", 3.75, 3.75, 90, None, None), ("Orc_Bench_240", 2.85, 3.75, 90, None, None),
               ("Orc_Bench_240", 4.65, 3.75, 90, None, None),
               ("Orc_Table_240", 11.25, 3.75, 90, None, None), ("Orc_Bench_240", 10.35, 3.75, 90, None, None),
               ("Orc_Bench_240", 12.15, 3.75, 90, None, None),
               ("Orc_Bunk", 0.8, 6.75, 90, None, None), ("Orc_Bunk", 0.8, 2.25, 90, None, None),
               ("Overlay_Orc_Furs", 1.3, 0.9, 20, None, None),
               ("Orc_WeaponRack", 14.25, 6.75, -90, None, "wall_floor", {"hug": True}),
               ("Orc_WeaponRack", 14.25, 2.25, -90, None, "wall_floor", {"hug": True}),
               ("Orc_MeatRack", 12.75, 0.9, 180, None, None),
               ("Torch_Wall", 0.75, 3.75, 90, None, "wall_hung"), ("Torch_Wall", 14.25, 3.9, -90, None, "wall_hung")]),
})
VKI_PLANS.update({
    "VKI_Orc_Barracks": """
      0  1  2  3  4  5  6  7
     +##+##+WW+##+##+WW+##+##+
   3 #ob ob .. ob ob .. ob ob#
     +                       +
   2 #.. of .. ot ot .. .. OW#
     +                       +
   1 #.. .. oe oe oe oe of ..#
     +                       +
   0 #ob ob .. ee .. .. ob ob#
     +==+==+==+ee+==+==+==+==+
""",
    "VKI_Orc_Forge": """
      0  1  2  3  4  5
     +##+WW+##+##+WW+##+
   3 #.. OF OF op .. ..#
     +                 +
   2 #.. OF OF OA ba ir#
     +                 +
   1 #.. .. .. .. os OW#
     +                 +
   0 #.. .. EE EE .. ..#
     +==+==+EE+EE+==+==+
""",
    "VKI_Orc_ShamanHut": """
      0  1  2  3
     +##+##+##+##+
   3 #OT .. AL AL#
     +           +
   2 #.. .. .. ..#
     +           +
   1 #of .. OC ..#
     +           +
   0 #.. ee .. ..#
     +==+ee+==+==+
""",
    "VKI_Orc_Pen": """
      0  1  2  3  4  5
     +##+##+##+##+##+##+
   3 #cg cg .. .. cg cg#
     +                 +
   2 #sk .. .. rf .. ..#
     +                 +
   1 #.. .. st st .. ..#
     +                 +
   0 #oe oe .. ee .. ba#
     +==+==+==+ee+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Orc_Barracks": dict(
        building="OrcHall", floor=0, preset="Night", family=dict(perimeter="Orc", partition="Orc"),
        zones={"room": dict(cells="rest", floor="EarthSooty", wall="OrcLogs")},
        links=[("front", "exit", "@return")], spawns={"front": (5.25, 1.60, 0)},
        props=[("Orc_Bunk", 1.45, 5.2, 0, None, None), ("Orc_Bunk", 5.25, 5.2, 0, None, None),
               ("Orc_Bunk", 10.55, 5.2, 0, None, None),
               ("Orc_Bunk", 1.45, 0.8, 180, None, None), ("Orc_Bunk", 10.55, 0.8, 180, None, None),
               ("Orc_Table_240", 6.0, 3.25, 0, None, None), ("Orc_Bench_240", 6.0, 2.35, 0, None, None),
               ("Overlay_Orc_Furs", 2.6, 3.0, 25, None, None), ("Overlay_Orc_Furs", 9.6, 1.9, -30, None, None),
               ("Orc_WeaponRack", 11.25, 3.75, -90, None, "wall_floor", {"hug": True}),
               ("Orc_Trophies", 0.75, 3.0, 90, None, "wall_hung"),
               ("Torch_Wall", 8.25, 5.25, 0, None, "wall_hung"), ("Torch_Wall", 11.25, 1.8, -90, None, "wall_hung")]),
    "VKI_Orc_Forge": dict(
        building="OrcHall", floor=0, preset="Night", family=dict(perimeter="Orc", partition="Orc"),
        zones={"room": dict(cells="rest", floor="EarthSooty", wall="OrcLogs")},
        links=[("front", "exit", "@return")], spawns={"front": (4.5, 1.60, 0)},
        props=[("Orc_Forge", 2.25, 4.3, 0, None, None), ("Orc_Anvil", 5.0, 3.3, 0, None, None),
               ("Barrel_Water", 6.9, 3.4, 0, None, None), ("Mine_OrePile", 5.6, 5.0, 0, None, None),
               ("IronStock_150", 8.25, 3.9, -90, None, "wall_floor", {"hug": True}),
               ("Orc_ScrapPile", 6.9, 1.6, 20, None, None),
               ("Orc_WeaponRack", 8.25, 2.1, -90, None, "wall_floor", {"hug": True}),
               ("Torch_Wall", 0.75, 2.25, 90, None, "wall_hung")]),
    "VKI_Orc_ShamanHut": dict(
        building="OrcHall", floor=0, preset="Night", family=dict(perimeter="Orc", partition="Orc"),
        zones={"room": dict(cells="rest", floor="EarthSooty", wall="OrcLogs")},
        links=[("front", "exit", "@return")], spawns={"front": (2.25, 1.60, 0)},
        props=[("Orc_Altar", 3.75, 5.25, 0, None, "wall_floor", {"hug": True}), ("Orc_Totem", 1.0, 4.9, 0, None, None),
               ("Orc_HerbRack", 0.75, 3.0, 90, None, "wall_hung"), ("Orc_HerbRack", 5.25, 3.0, -90, None, "wall_hung"),
               ("Orc_Cauldron", 3.9, 2.4, 0, None, None), ("Overlay_Orc_Furs", 1.2, 1.9, 70, None, None)]),
    "VKI_Orc_Pen": dict(
        building="OrcHall", floor=0, preset="Night", family=dict(perimeter="Orc", partition="Orc"),
        zones={"room": dict(cells="rest", floor="EarthSooty", wall="OrcLogs")},
        links=[("front", "exit", "@return")], spawns={"front": (5.25, 1.60, 0)},
        props=[("Orc_Cage", 1.9, 4.6, 0, None, None), ("Orc_Cage_Open", 7.1, 4.6, 0, None, None),
               ("Orc_Stocks", 3.75, 2.0, 0, None, None),
               ("Chains_Wall", 0.75, 3.0, 90, None, "wall_hung"),
               ("Skeleton_Sitting", 0.75, 3.0, 90, None, "wall_floor", {"hug": True}),
               ("Overlay_Refuse", 4.9, 3.6, 0, None, None),
               ("Orc_Bench_240", 1.6, 0.8, 0, None, None), ("Barrel_Water", 8.2, 0.9, 180, None, None),
               ("Torch_Wall", 8.25, 3.6, -90, None, "wall_hung")]),
})
VKI_ROOMS_CODES.update({"Orc_Throne": "TH", "Orc_Banner": "BN", "Orc_WarTable": "wt", "Orc_Cauldron": "OC",
                        "Orc_Table_240": "ot", "Orc_Bench_240": "oe", "Orc_Bunk": "ob", "Overlay_Orc_Furs": "of",
                        "Orc_WeaponRack": "OW", "Orc_MeatRack": "om", "Orc_Forge": "OF", "Orc_Anvil": "OA",
                        "Orc_ScrapPile": "os", "Orc_Altar": "AL", "Orc_Totem": "OT", "Orc_Stocks": "st",
                        "Orc_Cage": "cg", "Orc_Cage_Open": "cg", "Mine_OrePile": "op"})
