# ===================== VKI ROOMS DWARF: the dwarf kit's level and catalog rows (docs/DWARF_KIT.md) =====================
# Loaded by vki_ns() right after vki_rooms_water. Dwarven halls are cut into the mountain: a cave map (R["cave"]) whose
# halls are Dwarf walls drawn on its inner grid lines (backed by the rock: the wall-backed tiles), with lava channels
# painted as "ll" cells (vki_cave_channels) and the natural caves beside them.
#   VKI_Dwarf_Hall  the great hall, 19 x 11: a vestibule from the surface gate (a passage), lit by two braziers, opens
#                   through a wide doorway into a pillared hall (8 x 6 cells): a checkered runner leads up the aisle
#                   over a gold rune medallion to the king's throne on its dais before the sealed great gate (rune-carved
#                   stone leaves), between red clan banners and two statues of dwarf kings; plain granite flags on the
#                   side walkways; two lava channels along the aisle; the treasury through a door off the east walkway;
#                   the foundry through the east door -- the forge and the great crucible (a point of interest,
#                   vki_props_poi); the west wall broken into a natural cave where a stone arch bridge crosses the chasm
#                   to the tunnel on to the mines
# Plan codes: "ll" lava, "vv" / "==" chasm (under the bridge), "Sx" the tunnel's spawn; tokens "S1" the great gate, "s1"
# the wide doorway, "S2" the relief wall, "s2" the treasury door, "1" the forge door, "X" the breach, "P" the passage.
# Every top-level name starts with vki_/VKI_ (T18).

VKI_DWARF_SCENES = ["VKI_Dwarf_Hall"]

VKI_PLANS.update({
    "VKI_Dwarf_Hall": """
       0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
     +##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+
  10 ### ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
     +                                                        +
   9 ### ## vv vv ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
     +                  ##+S2+##+S1+S1+##+S2+##+              +
   8 #.. SM vv vv .. MG#.. .. .. .. .. .. .. ..### ## ## ## ###
     +                                          ##+##+##+##+  +
   7 #.. .. vv vv .. ..#.. ll .. .. .. .. ll ..#.. .. .. ..####
     +                                                        +
   6 #Sx .. == == .. ..X.. ll .. .. .. .. ll ..#.. .. CU ..####
     +                                                        +
   5 #Sx .. vv vv .. ..#.. ll .. .. .. .. ll ..1.. .. .. ..####
     +                                                        +
   4 #.. .. vv vv .. ..#.. ll .. .. .. .. ll ..#.. .. .. ..####
     +                                          ==+==+==+==+  +
   3 ### ## vv vv .. ..#.. .. .. .. .. .. .. ..### ## ## ## ###
     +                  ==+==+==+s1+s1+==+==+s2+==+==+        +
   2 ### ## vv vv CR .. ## ###.. .. .. ..:CI .. TR ..### ## ###
     +                                                        +
   1 ### ## ## ## ## ## ## ##P.. .. .. ..:ur gc .. lp### ## ###
     +                        ==+==+==+==+==+==+==+==+        +
   0 t## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##t
     +==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Dwarf_Hall": dict(
        building="Dwarf", floor=-1, preset="Hall", family=dict(perimeter="Cave", partition="Dwarf"), cave=True,
        pools=False, partition_wall="zone",
        specials={"S1": "Wall_Dwarf_DoorWide_300_Full", "S2": "Wall_Dwarf_Plain_150B_Full",
                  "s1": "Wall_Dwarf_DoorWide_300_Cut", "s2": "Wall_Dwarf_Door_150_Cut", "1": "Wall_Dwarf_Door_150_Full"},
        door_leaves={("EW", 9, 9): dict(piece="Leaf_DwarfGate_300", state="closed")},
        # the checkered runner from the wide doorway up the aisle to the throne (x 13.5-16.5: on the checker's 0.75
        # joints), plain flags on the walkways, the vestibule, the forge and the treasury
        zones={"runner": dict(cells=[(9, 10, 3, 8)], floor="DwarfFloor", wall="DwarfIn"),
               "foundry": dict(cells=[(14, 17, 4, 7)], floor="DwarfFlag", wall="DwarfIn"),
               "hall": dict(cells=[(6, 13, 3, 8), (8, 11, 1, 2), (12, 15, 1, 2)], floor="DwarfFlag", wall="DwarfIn"),
               "cave": dict(cells="rest", floor="CaveFloor")},
        # loose debris (vki_props_debris): the runner kept clean, the halls a little, slag and ore in the foundry
        debris=dict(density=0.40, seed=19, zones={"runner": 0.0, "hall": 0.08, "foundry": 0.60},
                    themes={"foundry": "forge"}),
        passages={("NS", 1, 8): "gate"},
        tunnels={(0, 6): "mines"},
        links=[("gate", "passage", VKI_TOWN), ("mines", "passage", "VKI_Mine_M1")],    # the gate: the valley's dwarf_gate
        lava_sinks={(7, 4): (0, -1), (12, 4): (0, -1)},          # the lava runs south (flow, for Unity)
        # the hall: x 9-21, y 4.5-13.5. Cross passages along the south and north rows (y 4.5-6, 12-13.5) join the side
        # walkways to the aisle round the lava channels' ends, so nothing stands on them but the throne's dais; the
        # pillars stand at the aisle's edges between them, the braziers flank the throne's dais (a metre off the sealed
        # gate, which the camera then sees over the throne), the kings
        # stand in the walkways' north corners
        props=[("Throne_Dwarf", 15.0, 11.0, 0, None, None, {"hug": False}),         # 1 m off the gate: it shows
               ("Statue_DwarfKing", 9.85, 12.6, 0, None, None, {"hug": False}),
               ("Statue_DwarfKing", 20.13, 12.6, 0, None, None, {"hug": False}),
               ("Pillar_Dwarf_Cut", 12.6, 7.5, 0, None, None, {"hug": False}),
               ("Pillar_Dwarf_Cut", 17.4, 7.5, 0, None, None, {"hug": False}),
               ("Pillar_Dwarf_Cut", 12.6, 10.5, 0, None, None, {"hug": False}),
               ("Pillar_Dwarf_Cut", 17.4, 10.5, 0, None, None, {"hug": False}),
               ("Overlay_RuneCircle", 15.0, 7.5, 0, None, None, {"hug": False}),
               ("Brazier_Dwarf", 13.6, 9.55, 0, None, None, {"hug": False}),
               ("Brazier_Dwarf", 16.4, 9.55, 0, None, None, {"hug": False}),
               ("Banner_Dwarf", 12.75, 13.2, 0, None, "wall_hung", {"hug": False}),       # flanking the gate
               ("Banner_Dwarf", 17.25, 13.2, 0, None, "wall_hung", {"hug": False}),
               ("Brazier_Dwarf", 12.9, 3.8, 0, None, None, {"hug": False}),                # the vestibule, by the doorway
               ("Brazier_Dwarf", 17.1, 3.8, 0, None, None, {"hug": False}),
               # the treasury (x 18-24, y 1.5-4.5; its door on the east walkway's south end, x 19.5-21; a Cut wall to
               # the vestibule, so no Full corner post hides it): the chests by the north wall either side of the door,
               # the gold heap in the south-east corner facing west, a brazier behind it
               ("Chest_Iron", 18.85, 3.9, 0, None, None, {"hug": False}),
               ("Chest_Treasure", 22.1, 3.68, 0, None, None, {"hug": False}),
               ("LootPile", 23.15, 2.5, -90, None, None, {"hug": False}),
               ("Overlay_GoldCoins", 19.9, 2.5, 0, None, None, {"hug": False}),
               ("Urns", 18.75, 2.25, 0, None, None, {"hug": False}),
               ("Brazier_Dwarf", 23.3, 3.9, 0, None, None, {"hug": False}),
               # the foundry (x 21-27, y 6-12; its door on the west wall, y 7.5-9): the great crucible against the
               # north wall, its moulds and the furnace's mouth toward the camera (the hall's Full east wall hides the
               # room's west strip), the forge on the east wall and the anvil before it
               ("POI_Crucible", 24.3, 10.27, 0, None, None, {"hug": False}),
               ("Forge_Dwarf", 26.10, 7.2, -90, None, None, {"hug": False}),
               ("Anvil_Dwarf", 24.3, 7.55, -90, None, None, {"hug": False}),
               ("Bridge_Dwarf", 4.5, 9.75, 90, None, None, {"hug": False}),
               ("Crystals", 6.9, 3.9, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 7.7, 12.2, 0, None, None, {"hug": False}),
               ("Stalagmites", 2.3, 12.0, 0, None, None, {"hug": False})]),
})

VKI_ADVENTURE_CATALOG += [
    ("Dwarf walls, posts, breaches and the gate", -187.5,
     [n for n in VKI_DWF_NAMES if "_Wall_Dwarf_" in n or "_Post_" in n or "_Leaf_" in n]),
    ("Dwarf lava channel tiles, props", -193.5,
     [n for n in VKI_DWF_NAMES if "_Ground_Lava_" in n or "_Prop_" in n or "_Overlay_" in n]),
]
