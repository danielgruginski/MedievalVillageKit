# ===================== VKI ROOMS CASTLE: a castle's inside (2026-10-17, MedievalSetting's coming castle area) =========
# Loaded by vki_ns() right after vki_rooms_mine. The castle's halls use the 4.5 m Ashlar family (the user's call: try
# the Ashlar walls before a tall Stone set).
#   VKI_Castle_Hall  the great hall, 10 x 6 cells (15 x 9 m): the hooded Ashlar hearth in the middle of the north wall
#                    between tall lancets, lancets in the side walls, the wide exit in the south wall; long trestle
#                    tables with forms down both sides, an open aisle from the door to the fire, pricket candles by the
#                    hearth, a weapon rack and an armour stand on the west wall, a chest on the east
# Tokens: "S1" the hearth (Wall_Ashlar_Hearth_300_Full). Every top-level name starts with vki_/VKI_ (T18).

VKI_CASTLE_SCENES = ["VKI_Castle_Hall"]

VKI_PLANS.update({
    "VKI_Castle_Hall": """
      0  1  2  3  4  5  6  7  8  9
     +##+##+LT+LT+S1+S1+LT+LT+##+##+
   5 #WR .. .. cd .. .. cd .. .. CH#
     +                             +
   4 L.. fm TB fm .. .. .. fm TB fmL
     +                             +
   3 #AS fm TB fm .. .. .. fm TB fm#
     +                             +
   2 L.. fm TB fm .. .. .. fm TB fmL
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
        specials={"S1": "Wall_Ashlar_Hearth_300_Full"},
        zones={"hall": dict(cells="rest", floor="FlagWarm", wall="AshlarIn")},
        links=[("front", "exit", "@return")], spawns={"front": (7.5, 1.60, 0)},
        props=[("Table_Trestle_300", 3.0, 5.25, 90, None, None), ("Table_Trestle_300", 12.0, 5.25, 90, None, None),
               ("Form_300", 2.25, 5.25, 90, None, None), ("Form_300", 3.75, 5.25, 90, None, None),
               ("Form_300", 11.25, 5.25, 90, None, None), ("Form_300", 12.75, 5.25, 90, None, None),
               ("CandleStand_Pricket", 5.25, 8.25, 0, None, None), ("CandleStand_Pricket", 9.75, 8.25, 0, None, None),
               ("Prop_WeaponRack", 0.75, 8.25, 90, None, "wall_floor", {"hug": True}),
               ("Prop_ArmorStand", 0.75, 5.25, 90, None, "wall_floor", {"hug": True}),
               ("Chest", 14.25, 8.25, -90, None, None, {"hug": True}),
               ("Rug_300x150", 7.5, 4.5, 90, None, None)]),
})
VKI_ROOMS_CODES.update({"Prop_ArmorStand": "AS"})
