# ===================== VKI ROOMS CASTLE: a castle's inside (2026-10-17, MedievalSetting's coming castle area) =========
# Loaded by vki_ns() right after vki_rooms_mine. The castle's halls use the 4.5 m Ashlar family (the user's call: try
# the Ashlar walls before a tall Stone set).
#   VKI_Castle_Hall  the great hall, 10 x 6 cells (15 x 9 m). 2026-10-18 (vki_props_castle): the high end is a dais
#                    across the north end (rows 4-5) with the high table under its cloth, the throne behind it at the
#                    middle between two carved chairs, the cloth of estate on the wall behind, millefleur tapestries
#                    in the north corners; the hooded Ashlar hearth moved to the east wall (rows 2-3); tall lancets in
#                    plain leaded glass (lancet_style); long trestle tables with forms down both sides, an open aisle
#                    from the door to the dais under a ring chandelier, banners in the lord's arms on the side walls,
#                    a shield and crossed swords over the chest, pricket candles on the dais
#   VKI_Castle_Tower_F0 / _F1  a tower's two storeys, 4 x 4 cells (6 x 6 m), Stone (2026-10-18): the newel stair in the
#                    north-west corner (Stair_Up_Spiral_300 below, Stair_Down_Spiral_300 above, the same origin and
#                    rotation, linked); a guard room below (weapon rack, barrels, a crate, a banner), a chamber above
#                    (a bed, a chest, a banner)
# Tokens: "1" the hearth (Wall_Ashlar_Hearth_300_Full, east wall). Every top-level name starts with vki_/VKI_ (T18).

VKI_CASTLE_SCENES = ["VKI_Castle_Hall", "VKI_Castle_Tower_F0", "VKI_Castle_Tower_F1"]

VKI_PLANS.update({
    "VKI_Castle_Hall": """
      0  1  2  3  4  5  6  7  8  9
     +##+##+LT+LT+##+##+LT+LT+##+##+
   5 #WR .. .. cd TH ch cd .. .. CH#
     +                             +
   4 L.. .. .. .. HI HI .. .. .. ..L
     +                             +
   3 #AS fm TB fm .. .. .. fm TB fm1
     +                             +
   2 L.. fm TB fm .. ri .. fm TB fm1
     +                             +
   1 #.. .. .. .. .. .. .. .. .. ..#
     +                             +
   0 #.. .. .. .. EE EE .. .. .. ..#
     +==+ll+==+==+EE+EE+==+==+ll+==+
""",
})

VKI_ROOMS.update({
    "VKI_Castle_Hall": dict(
        building="Castle", floor=0, preset="Day", family=dict(perimeter="Ashlar", partition="Ashlar"),
        corners="pillar", rhythm_sides=True,
        specials={"1": "Wall_Ashlar_Hearth_300_Full"},
        lancet_style={"stained": "Leaded"},
        zones={"dais": dict(cells=[(0, 9, 4, 5)], floor="FlagWarm", wall="AshlarIn", dais=True),
               "hall": dict(cells="rest", floor="FlagWarm", wall="AshlarIn")},
        dais=[(0.0, 6.0), (3.0, 6.0), (6.0, 6.0), (9.0, 6.0), (12.0, 6.0)],
        links=[("front", "exit", "@return")], spawns={"front": (7.5, 1.60, 0)},
        props=[("Table_Trestle_300", 3.0, 3.75, 90, None, None), ("Table_Trestle_300", 12.0, 3.75, 90, None, None),
               ("Form_300", 2.25, 3.75, 90, None, None), ("Form_300", 3.75, 3.75, 90, None, None),
               ("Form_300", 11.25, 3.75, 90, None, None), ("Form_300", 12.75, 3.75, 90, None, None),
               ("Rug_300x150", 7.5, 3.0, 90, None, None),
               ("Chandelier_Ring", 7.5, 3.75, 0, None, None),
               # the high end, on the dais (z 0.20)
               ("Table_High_300", 7.5, 7.05, 0, None, None, {"z": 0.20}),
               ("Throne_Castle", 7.5, 8.05, 0, None, None, {"z": 0.20}),
               ("Chair_Carved", 6.45, 8.1, 0, None, None, {"z": 0.20}),
               ("Chair_Carved", 8.55, 8.1, 0, None, None, {"z": 0.20}),
               ("CandleStand_Pricket", 5.25, 8.25, 0, None, None, {"z": 0.20}),
               ("CandleStand_Pricket", 9.75, 8.25, 0, None, None, {"z": 0.20}),
               ("Prop_WeaponRack", 0.75, 8.25, 90, None, "wall_floor", {"hug": True, "z": 0.20}),
               ("Chest", 14.25, 8.25, -90, None, None, {"hug": True, "z": 0.20}),
               ("Prop_ArmorStand", 0.75, 5.25, 90, None, "wall_floor", {"hug": True}),
               # hangings
               ("Hanging_Estate_240", 7.5, 8.25, 0, None, "wall_hung"),
               ("Tapestry_300", 1.6, 8.25, 0, None, "wall_hung"),
               ("Tapestry_300", 13.4, 8.25, 0, None, "wall_hung"),
               ("Banner_Castle", 0.75, 5.25, 90, None, "wall_hung"),
               ("Banner_Castle", 0.75, 2.25, 90, None, "wall_hung"),
               ("Banner_Castle", 14.25, 2.25, -90, None, "wall_hung"),
               ("Banner_Castle", 0.75, 8.25, 90, None, "wall_hung"),     # over the weapon rack (the shield clashed)
               ("Display_Arms", 14.25, 8.25, -90, None, "wall_hung")]),
})
VKI_PLANS.update({
    "VKI_Castle_Tower_F0": """
      0  1  2  3
     +##+##+WW+##+
   3 #^^ ^^ .. ..#
     +           +
   2 #^^ ^^ .. WR#
     +           +
   1 #.. .. .. ba#
     +           +
   0 #.. .. bx ba#
     +==+ee+==+==+
""",
    "VKI_Castle_Tower_F1": """
      0  1  2  3
     +##+##+WW+##+
   3 #vv vv .. ..#
     +           +
   2 #vv vv .. HT#
     +           +
   1 #.. .. .. HT#
     +           +
   0 #.. CH .. ..#
     +==+ww+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Castle_Tower_F0": dict(
        building="Castle", floor=0, preset="Day", family=dict(perimeter="Stone", partition="Stone"),
        zones={"room": dict(cells="rest", floor="Flag", wall="StoneIn")},
        stairs=[("Up", 0.0, 3.0, 0, "stairA", "Spiral")],
        links=[("front", "exit", "@return"), ("stairA", "stair_up", "VKI_Castle_Tower_F1")],
        spawns={"front": (2.25, 1.60, 0), "stairA": (2.135, 2.25, 180)},
        props=[("Prop_WeaponRack", 5.25, 3.75, -90, None, "wall_floor", {"hug": True}),
               ("Barrel", 5.25, 2.1, -90, None, None), ("Barrel", 5.25, 0.75, -90, None, None),
               ("Crate", 3.75, 0.75, 180, None, None),
               ("Banner_Castle", 5.25, 5.25, 0, None, "wall_hung")]),
    "VKI_Castle_Tower_F1": dict(
        building="Castle", floor=1, preset="Day", family=dict(perimeter="Stone", partition="Stone"),
        zones={"room": dict(cells="rest", floor="Boards_NS", wall="StoneIn")},
        stairs=[("Down", 0.0, 3.0, 0, "stairA", "Spiral")],
        links=[("stairA", "stair_down", "VKI_Castle_Tower_F0")], spawns={"stairA": (2.135, 2.25, 180)},
        props=[("Bed_HalfTester", 5.0, 3.0, -90, None, "wall_floor", {"hug": True}),
               ("Chest", 2.25, 0.75, 180, None, None),
               ("Banner_Castle", 5.25, 5.25, 0, None, "wall_hung")]),
})
VKI_ROOMS_CODES.update({"Prop_ArmorStand": "AS", "Throne_Castle": "TH", "Chair_Carved": "ch", "Table_High_300": "HI",
                        "Chandelier_Ring": "ri"})
