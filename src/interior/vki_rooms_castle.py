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
# Tokens: "1" the hearth (Wall_Ashlar_Hearth_300_Full, east wall). Every top-level name starts with vki_/VKI_ (T18).

VKI_CASTLE_SCENES = ["VKI_Castle_Hall"]

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
VKI_ROOMS_CODES.update({"Prop_ArmorStand": "AS", "Throne_Castle": "TH", "Chair_Carved": "ch", "Table_High_300": "HI",
                        "Chandelier_Ring": "ri"})
