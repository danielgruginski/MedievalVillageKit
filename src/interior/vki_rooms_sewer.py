# ===================== VKI ROOMS SEWER: the sewer kit's level and catalog rows (docs/SEWER_KIT.md) =====================
# Loaded by vki_ns() right after vki_rooms_adventure, whose cave-map machinery it uses: a sewer level is a cave map
# (R["cave"]) -- the ground between the tunnels is rock -- with the tunnels' brick walls drawn on its inner grid lines
# (the Sewer family, R["family"]["partition"]; the rock tiles behind them are the wall-backed ones), the channels
# painted as "ww" cells (vki_cave_channels: dual-grid channel tiles, vki_fam_sewer) and bridges over them. Built and
# checked like every level (vki_build_scene, vki_check, vki_rooms_shots).
#   VKI_Sewer_S1  the town sewer, 16 x 10: a west-east brick tunnel (a walkway either side of the channel) from the
#                 gaol's drain (a passage on to B1) past a ladder up to a street manhole; a cross wall with a culvert
#                 under it and a door; a branch from the north fed by an outfall, with a sluice gate, crossing the
#                 walkway under a slab bridge; the south wall broken into a natural grotto (a pool, crystals), the east
#                 end breached into a cave the channel runs out into, a tunnel on to the caverns (B4)
# Plan codes: "ww" channel, "~~" pool, "Sx" the tunnel on; tokens "xx" / "X" breaches, "1" the culvert, "S1" the
# ladder, "S2" the outfall, "P" the passage. Every top-level name starts with vki_/VKI_ (T18).

VKI_SEWER_SCENES = ["VKI_Sewer_S1"]

VKI_PLANS.update({
    "VKI_Sewer_S1": """
       0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
     +##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+
   9 ### ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
     +                        ##+S2+##+              +
   8 ### ## ## ## ## ## ## ###.. ww ..### ## .. .. ###
     +                                               +
   7 ### ## ## ## ## ## ## ###.. ww ..### ## MG .. Sx#
     +   ##+##+S1+##+##+##+##+         ##+##+        +
   6 ###P.. .. .. .. ..d.. .. .. ww .. .. ..X.. .. Sx#
     +                                               +
   5 ####ww ww ww ww ww1ww ww ww ww ww ww ww1ww ww ..#
     +                                               +
   4 ####pd .. .. .. ..#.. .. .. .. .. .. ..#.. .. ###
     +   ==+==+==+xx+xx+==+==+==+==+==+==+==+        +
   3 ### ## .. .. .. .. .. .. ## ## ## .. .. .. .. ###
     +                                               +
   2 ### .. gv .. .. .. .. .. .. ## .. .. .. CR .. ###
     +                                               +
   1 ### .. .. CR .. .. ~~ ~~ .. .. .. BD ## ## ## ###
     +                                               +
   0 t## ## .. .. .. .. ~~ ~~ MG .. .. ## ## ## ## ##t
     +==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Sewer_S1": dict(
        building="Sewer", floor=-1, preset="Sewer", family=dict(perimeter="Cave", partition="Sewer"), cave=True,
        pools=False, partition_wall="zone", rush_mats=False,
        specials={"S1": "Wall_Sewer_Ladder_150_Full", "S2": "Wall_Sewer_Outfall_150_Full",
                  "1": "Wall_Sewer_Culvert_150_Full"},
        zones={"sewer": dict(cells=[(1, 12, 4, 6), (8, 10, 7, 8)], floor="SewerFloor", wall="SewerBrick"),
               "cave": dict(cells="rest", floor="CaveFloor")},
        passages={("NS", 6, 1): "gaol", ("EW", 3, 7): "street"},
        tunnels={(16, 7): "caverns"},
        links=[("gaol", "passage", "VKI_Dungeon_B1"), ("street", "passage", "@surface"),
               ("caverns", "passage", "VKI_Dungeon_B4")],
        pits=[("Pit_Pool_300x300", 9.0, 0.0)],
        # the tunnel (x 1.5-19.5, y 6-10.5): walkways on rows 4 and 6, the channel on row 5; the branch (x 12-16.5,
        # y 10.5-13.5) with its channel on column 9; bridges where the walkways need crossing
        props=[("Bridge_Sewer", 5.25, 8.25, 0, None, None, {"hug": False}),
               ("Bridge_Sewer", 17.25, 8.25, 0, None, None, {"hug": False}),
               ("Bridge_Sewer", 14.25, 9.75, 90, None, None, {"hug": False}),
               ("Sluice", 14.25, 11.25, 0, None, None, {"hug": False}),
               ("Torch_Wall", 2.25, 9.75, 0, None, "wall_hung"), ("Torch_Wall", 11.25, 9.75, 0, None, "wall_hung"),
               ("Torch_Wall", 18.75, 9.75, 0, None, "wall_hung"), ("Torch_Wall", 12.75, 12.75, 90, None, "wall_hung"),
               ("Overlay_Puddle", 2.6, 6.9, 0, None, None, {"hug": False}),
               ("Overlay_Sludge", 11.0, 6.7, 0, None, None, {"hug": False}),
               ("Overlay_Sludge", 17.9, 9.55, 0, None, None, {"hug": False}),
               # the grotto and the east cave
               ("Crystals", 5.2, 2.2, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 12.9, 1.0, 0, None, None, {"hug": False}),
               ("Overlay_Gravel", 3.75, 3.75, 0, None, None, {"hug": False}),
               ("Boulders", 16.6, 2.3, 0, None, None, {"hug": False}),
               ("Crystals", 20.6, 3.9, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 20.4, 11.4, 0, None, None, {"hug": False})]),
})

VKI_ADVENTURE_CATALOG += [
    ("Sewer walls, posts and breaches", -145.5, [n for n in VKI_SEW_NAMES if "_Wall_Sewer_" in n or "_Post_" in n]),
    ("Sewer channel tiles, bridge, sluice, sludge", -151.5,
     [n for n in VKI_SEW_NAMES if "_Ground_Sewer_" in n] + ["SM_VKI_Prop_Bridge_Sewer", "SM_VKI_Prop_Sluice",
                                                            "SM_VKI_Overlay_Sludge"]),
]
