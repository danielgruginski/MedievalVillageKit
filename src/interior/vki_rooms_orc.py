# ===================== VKI ROOMS ORC: the orcs' halls (2026-10-18, MedievalSetting's orc chapter) =====================
# Loaded by vki_ns() right after vki_rooms_monastery. Every top-level name starts with vki_/VKI_ (T18).
#   VKI_Orc_Hall  a warlord's hall, 10 x 6 cells (15 x 9 m), the Orc log family (vki_fam_orc): the wide gate in the
#                 south wall, unglazed barred windows; his seat at the north end between two war standards, the war
#                 table before it, trophy walls in the north corners; the cook fire and its cauldron in the middle,
#                 split-log tables with benches down both sides, bunks along the west wall with furs, weapon racks on
#                 the east wall, a meat rack by the gate; torches; night. Plain Full runs take the hide-and-skull
#                 B variant (vki_rooms_layout's B rule).

VKI_ORC_SCENES = ["VKI_Orc_Hall"]

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
VKI_ROOMS_CODES.update({"Orc_Throne": "TH", "Orc_Banner": "BN", "Orc_WarTable": "wt", "Orc_Cauldron": "OC",
                        "Orc_Table_240": "ot", "Orc_Bench_240": "oe", "Orc_Bunk": "ob", "Overlay_Orc_Furs": "of",
                        "Orc_WeaponRack": "OW", "Orc_MeatRack": "om"})
