# ===================== VKI ROOMS WATER: the water kit's level and catalog rows (docs/WATER_KIT.md) =====================
# Loaded by vki_ns() right after vki_rooms_sewer. Streams are painted "ss" cells in a cave map (vki_cave_ground lays
# their dual-grid tiles, vki_fam_water); a stream cell next to the chasm gets a waterfall automatically, and every water
# tile carries its flow (vki_flow) for Unity's water shaders.
#   VKI_Cave_Falls  an underground river, 16 x 10: a spring falls from a cleft high in the north wall into a stream
#                   that winds south, meets a tributary falling from the west wall in a wide confluence, runs east
#                   under stepping stones and pours over the lip into a chasm that splits the cave; a rope bridge
#                   crosses the chasm to the east ledge and the tunnel on; a pool in the south-west
# Plan codes: "ss" stream, "vv" / "==" chasm (under the bridge), "~~" pool, "Ss" / "Sx" the tunnels' spawns. Every
# top-level name starts with vki_/VKI_ (T18).

VKI_WATER_SCENES = ["VKI_Cave_Falls"]

VKI_PLANS.update({
    "VKI_Cave_Falls": """
       0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
     +##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+
   9 ### ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
     +                                               +
   8 ### ## ## .. ss .. ## ## ## ## ## ## vv ## ## ###
     +                                               +
   7 ### ## MG .. ss .. CR .. ## ## .. .. vv vv gv ..#
     +                                               +
   6 ### .. .. .. ss ss .. .. .. .. MG .. == == .. ..#
     +                                               +
   5 ### ss ss ss ss ss ss .. .. .. .. .. vv vv .. Sx#
     +                                               +
   4 ### .. .. .. .. .. ss ss ss ss ss ss vv .. .. Sx#
     +                                               +
   3 #Ss .. .. .. .. .. .. .. .. .. .. .. vv .. CR ###
     +                                               +
   2 #Ss .. ~~ ~~ .. .. CR .. .. .. .. .. vv .. ## ###
     +                                               +
   1 #.. .. ~~ ~~ .. .. .. .. SM .. BD .. vv .. .. ###
     +                                               +
   0 t## ## .. .. .. .. .. .. .. .. .. .. vv ## ## ##t
     +==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Cave_Falls": dict(
        building="Dungeon", floor=-4, preset="Cavern", family=dict(perimeter="Cave", partition="Cave"), cave=True,
        pools=False,
        zones={"cave": dict(cells="rest", floor="CaveFloor")},
        tunnels={(0, 3): "west", (16, 5): "east"},
        links=[("west", "passage", "VKI_Dungeon_B4"), ("east", "passage", "@return")],
        pits=[("Pit_Pool_300x300", 3.0, 1.5)],
        # the spring (north wall, over cell (4, 8)) and the tributary (west wall, beside cell (1, 5)); the falls into
        # the chasm are placed by the assembler; stepping stones on the tributary and the river; the rope bridge
        props=[("Waterfall_Rock", 6.75, 13.5, 0, None, None, {"hug": False}),
               ("Waterfall_Rock", 1.5, 8.25, 90, None, None, {"hug": False}),
               ("SteppingStones", 3.75, 8.25, 0, None, None, {"hug": False}),
               ("SteppingStones", 11.25, 6.75, 0, None, None, {"hug": False}),
               ("RopeBridge_420", 19.5, 9.75, 90, None, None, {"hug": False}),
               ("Mushrooms_Glow", 3.9, 11.4, 0, None, None, {"hug": False}),
               ("Crystals", 9.9, 11.0, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 15.6, 9.9, 0, None, None, {"hug": False}),
               ("Crystals", 9.6, 3.9, 0, None, None, {"hug": False}),
               ("Stalagmites", 12.6, 2.4, 0, None, None, {"hug": False}),
               ("Boulders", 15.5, 2.1, 0, None, None, {"hug": False}),
               ("Crystals", 21.6, 5.1, 0, None, None, {"hug": False}),
               ("Overlay_Gravel", 21.6, 11.0, 0, None, None, {"hug": False})]),
})

VKI_ADVENTURE_CATALOG += [
    ("Stream tiles, node parity %s" % q, -157.5 - 6.0 * i,
     [n for n in VKI_WAT_STREAM_NAMES if n.endswith("_" + q)] + (["SM_VKI_Ground_Stream_XXXX"] if q == "Q11" else []))
    for i, q in enumerate(("Q00", "Q10", "Q01", "Q11"))
] + [("Waterfalls, stepping stones", -181.5, [n for n in VKI_WAT_NAMES if "_Prop_" in n])]
