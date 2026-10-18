# ===================== VKI ROOMS MONASTERY: the abandoned monastery (2026-10-17, MedievalSetting's coming area) =========
# Loaded by vki_ns() right after vki_rooms_castle. Every top-level name starts with vki_/VKI_ (T18).
#   VKI_Monastery_Church  the abandoned church, 8 x 6 cells (12 x 9 m), Ashlar: the altar under tall lancets, one
#                         lancet in the north wall and one in the west wall broken (shards on the floor below), choir
#                         stalls facing across the choir, the nave's pews broken, overturned or left standing, a roof
#                         beam fallen across the nave on its heap of rubble, more rubble about
# Tokens: "S2" / "2" the broken lancet (Wall_Ashlar_Lancet_150_Full_Broken).

VKI_MONASTERY_SCENES = ["VKI_Monastery_Church"]

VKI_PLANS.update({
    "VKI_Monastery_Church": """
      0  1  2  3  4  5  6  7
     +##+##+S2+LT+LT+LL+##+##+
   5 #.. .. .. AL AL .. .. ..#
     +                       +
   4 #CS .. .. .. .. .. .. CS#
     +                       +
   3 #CS .. .. .. FB FB .. CS#
     +                       +
   2 L.. PW PW .. .. PW PW ..L
     +                       +
   1 2gs PW PW .. .. PW PW ..L
     +                       +
   0 #.. .. .. EE EE .. .. ..#
     +==+ll+==+EE+EE+==+ll+==+
""",
})

VKI_ROOMS.update({
    "VKI_Monastery_Church": dict(
        building="Monastery", floor=0, preset="Day", family=dict(perimeter="Ashlar", partition="Ashlar"),
        corners="pillar", rhythm_sides=True,
        specials={"S2": "Wall_Ashlar_Lancet_150_Full_Broken", "2": "Wall_Ashlar_Lancet_150_Full_Broken"},
        zones={"nave": dict(cells="rest", floor="FlagRustic", wall="AshlarIn")},
        links=[("front", "exit", "@return")], spawns={"front": (6.0, 1.60, 0)},
        props=[("Altar_300", 6.0, 7.65, 0, None, None, {"warn_ok": "window"}),
               ("ChoirStall_300", 0.75, 6.0, 90, None, "wall_floor", {"hug": True}),
               ("ChoirStall_300", 11.25, 6.0, -90, None, "wall_floor", {"hug": True}),
               ("Pew_300_Broken", 3.0, 1.5, 180, None, None), ("Pew_300", 9.0, 1.5, 180, None, None),
               ("Pew_300", 3.0, 3.0, 180, None, None), ("Pew_300_Overturned", 9.0, 3.25, 0, None, None),
               ("FallenBeam", 7.6, 5.0, 8, None, None),   # (the BFS boxes colliders square to the room: a steep angle
               #  boxed the whole diagonal and cut the altar off)
               ("Overlay_GlassShards", 3.75, 8.35, 0, None, None),
               ("Overlay_GlassShards", 0.65, 2.25, 90, None, None),
               ("Overlay_Debris_Rubble", 7.9, 1.9, 40, None, None)]),
})
VKI_ROOMS_CODES.update({"ChoirStall_300": "CS", "Pew_300_Broken": "PW", "Pew_300_Overturned": "PW",
                        "FallenBeam": "FB", "Desk_Scriptorium": "DS", "Overlay_GlassShards": "gs"})
