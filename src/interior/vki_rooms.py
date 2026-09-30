# ===================== VKI ROOMS: the interior assembler (§6, §7, §9 T12 / T19) =====================
# Spec: docs/history/interior_design/INTERIOR_SPEC.md (§1 camera, §2.3 posts, §2.7 floors, §5 mounts, §6 scenes,
# §10 amendments). Loaded by vki_ns() (VKI_TEXTS, after the package texts, before vki_test).
# Every top-level name starts with vki_/VKI_ (T18).
#   VKI_PLANS            the §6 ASCII plans (verbatim except the fixes listed in VKI_PLAN_CHANGES)
#   VKI_ROOMS[scene]     size, families, zones, specials, props [(piece, x, y, rot, style, mount[, opts])], spawns,
#                        links, stairs, sills, camera, preset
#   vki_rooms_layout(s)  parser + pure layout: wall pieces, posts (§2.3), floors (§2.7), specials, exits, stairs
#   vki_build_scene(s) / vki_build_all()   build VKI_<S>_Shell / _Props / _Logic / _Lights
#   vki_check(s)         §9 T12 room rules (posts incl. the free-end ERROR, floors, doors, spawns, clashes, mounts,
#                        BFS) + T19 as errors; R-occ1-6, palette / floor levels (measured on the game shot), plan
#                        codes as warnings; full=True returns dict(errors, warnings, placeholders, stats)
#   vki_rooms_shots(s)   fit game shot + plan in the scene's preset -> renders/interior/<scene>/<tag>_game|_plan.png
# Placement: the prop list goes through vki_place (mounts, wall_floor hug); floor props and overlays hug the walls by
# default, wall_hung props hug off posts, table dressing / candles stand on their host's centre (vki_on); a wall_floor
# prop whose hug fails between two posts stands 3 cm off its proud line (vki_pull 0.03) and hugs the side walls.
# Posts: required ones before the props, optional rhythm posts after them (skipped where any prop touches the square).
# Missing masters are placed as placeholders PH_<piece> (grey boxes with the spec footprint and the same metadata
# contract, vki_placeholder=1); a rebuild picks up every real master that exists by then.
import bpy, bmesh, math, json, zlib, os, re
from mathutils import Vector, Matrix

VKI_ROOMS_VERSION = "2026-09-26 r1"
VKI_ROOMS_SCENES = ["VKI_Hovel_F0", "VKI_Cottage_F0", "VKI_Townhouse_F0", "VKI_Townhouse_F1", "VKI_Tavern_F0",
                    "VKI_Tavern_F1", "VKI_Smithy_F0", "VKI_Workshop_F0", "VKI_Chapel_F0"]
VKI_ROOMS_PH_COLL = "VKI_Rooms_Placeholders"          # hidden placeholder masters (never linked to a scene)
VKI_ROOMS_PH_MATS = {"prop": ("VKI_PH_Grey", (0.16, 0.16, 0.16)), "struct": ("VKI_PH_GreyLight", (0.36, 0.36, 0.36))}
VKI_ROOMS_MASTER_COLLS = ("VKI_Pieces", "VK_Pieces")  # plus any WS_vki_*_Pieces
VKI_ROOMS_PULL = 0.03          # hug fallback: back 3 cm off the proud line so the O/P post squares (0.31/0.21) clear
VKI_ROOMS_RASTER = 0.25        # BFS raster (§9 T12)
VKI_ROOMS_CAPSULE = 0.30       # BFS capsule radius
VKI_ROOMS_BAND = (0.05, 1.00)  # collider z band that blocks the capsule (overhead items do not)
VKI_ROOMS_TOK_EW = {"##": ("Plain", "Full"), "==": ("Plain", "Cut"), "WW": ("Window", "Full"),
                    "ww": ("Window", "Cut"), "dd": ("Door", "Cut"), "ee": ("Exit", "Cut"), "EE": ("ExitWide", "Cut"),
                    "FF": ("Special", "Full"), "LL": ("Lancet", "Full"), "LT": ("LancetTall", "Full"),
                    "ll": ("Lancet", "Cut"), "rr": ("Rail", None), "  ": (None, None),
                    # dungeon kit: iron bars (the Bars family, always Full), barred gates, ossuary niches
                    "||": ("Bars", "Full"), "gg": ("BarsGate", "Full"), "NN": ("Niche", "Full"), "nn": ("Niche", "Cut"),
                    # adventure kit: passages (scene links), and the family's named specials ("S1".."S4": R["specials"])
                    "PP": ("Passage", "Full"), "S1": ("Named", "Full"), "S2": ("Named", "Full"), "S3": ("Named", "Full"),
                    "S4": ("Named", "Full"), "s1": ("Named", "Cut"), "s2": ("Named", "Cut"),
                    # natural openings (the Cave wall family's doors: Wall_<fam>_Gap_150_<height>)
                    "OO": ("Gap", "Full"), "oo": ("Gap", "Cut"),
                    # transitions: a breach knocked through to the floor (Dungeon / Ancient; two in a row pair to 300)
                    "XX": ("Breach", "Full"), "xx": ("Breach", "Cut")}
VKI_ROOMS_TOK_NS = {"#": ("Plain", "Full"), ":": ("Plain", "Cut"), "W": ("Window", "Full"), "w": ("Window", "Cut"),
                    "d": ("Door", "Cut"), "t": ("Rake", "Rake"), "r": ("Rail", None), "L": ("Lancet", "Full"),
                    "l": ("Lancet", "Cut"), " ": (None, None),
                    "|": ("Bars", "Full"), "g": ("BarsGate", "Full"), "N": ("Niche", "Full"), "n": ("Niche", "Cut"),
                    "P": ("Passage", "Full"), "1": ("Named", "Full"), "2": ("Named", "Full"), "3": ("Named", "Full"),
                    "4": ("Named", "Full"), "O": ("Gap", "Full"), "o": ("Gap", "Cut"), "X": ("Breach", "Full"),
                    "x": ("Breach", "Cut")}
VKI_ROOMS_OWN_FAMILY = {"Bars": "Bars", "BarsGate": "Bars"}   # segment kinds that bring their own wall family
VKI_ROOMS_GATE_DEG = 90.0      # barred gates stand open by default (closed, a gate walls the cell off for the BFS;
                               # at 70 deg the leaf left 0.55 m of the 0.84 m doorway, under the 0.6 m capsule)
# plan cell codes per piece (§6 legend); "TB" also covers the forms of a table set
VKI_ROOMS_CODES = {"Bed_Box": "BX", "Bed_HalfTester": "HT", "Bed_Straw": "bd", "Chest": "CH", "Dresser": "DR",
                   "Pantry_Shelves_300": "PN", "Shelf_Wall_150": "SH", "Prop_Sawhorse": "SH",
                   "Table_Trestle_300": "TB", "Table_Trestle_150": "TB", "Table_Small": "tb", "Table_Barrel": "tb",
                   "Form_300": "fm", "Form_150": "fm", "Rug_300x150": "rg", "LogBasket": "WP", "Jars_Cluster": "ja",
                   "Barrel": "ba", "Barrel_Water": "ba", "Crate": "bx", "Worktable_150": "KW", "Oven_150": "OV",
                   "Hearth_Open": "HH", "Prop_Loom": "LM", "Prop_SpinningWheel": "SW", "Bar_Counter_150": "CT",
                   "Bar_End_150": "CE", "CaskRack_150": "CK", "Prop_BarrelStack": "BS", "Desk_Merchant": "DK",
                   "Prop_WeaponRack": "WR", "Prop_Bellows": "BL", "Prop_Anvil": "AN", "QuenchTrough_150": "QT",
                   "CoalBin_150": "CO", "GoodsRack_150": "GR", "Prop_Grindstone": "GS", "Workbench_300": "WB",
                   "Workbench_Carpenter": "WB", "IronStock_150": "ir", "PoleLathe": "PL", "Pew_300": "PW",
                   "Altar_300": "AL", "CandleStand_Pricket": "cd", "Lectern": "LC", "Font": "FT", "VotiveRack": "vr"}


# ---------------------------------------------------------------- §6 ASCII plans (verbatim except the fixes listed in VKI_PLAN_CHANGES)
VKI_PLANS = {
    "VKI_Hovel_F0": """
      0  1  2  3  4
     +##+##+WW+##+##+
   4 #BX BX CH PN PN#
     +              +
   3 #.. .. .. .. ..#
     +              +
   2 Wbd .. HH .. ..#
     +              +
   1 #bd .. .. TB TB#
     +              +
   0 tWP .. Sf .. jat
     +==+==+ee+==+ww+
""",
    "VKI_Cottage_F0": """
      0  1  2  3  4  5
     +##+##+FF+FF+##+##+
   4 #LM LM fp fp:BX BX#
     +           +     +
   3 #LM LM rg rg:.. CH#
     +           +     +
   2 #SH .. .. ..d.. ..W
     +           +==+==+
   1 #PN TB TB .. .. ..W
     +                 +
   0 tPN TB TB Sf .. WPt
     +==+ww+==+ee+==+ww+
""",
    "VKI_Townhouse_F0": """
      0  1  2  3  4  5  6
     +##+WW+FF+FF+##+##+##+
   4 #^^rWP fp fp DR:OV ..#
     +  +           +     +
   3 #^^r.. rg rg ..d.. KWW
     +  +           +     +
   2 #^^r.. TB TB ..:ba ba#
     +  +           +==+==+
   1 #Ss .. TB TB .. DK DK#
     +                    +
   0 tCH Sf .. .. .. .. bxt
     +==+ee+==+==+ww+==+ww+
""",
    "VKI_Townhouse_F1": """
      0  1  2  3  4  5  6
     +##+WW+##+##+WW+##+##+
   4 #vv Ss LM LM CH:HT HT#
     +  +           +     +
   3 #vvr.. LM LM ..:HT HT#
     +  +           +     +
   2 #vvr.. .. .. ..drg rgW
     +rr+           +     +
   1 #SW .. tb .. ..:.. CH#
     +              +     +
   0 t.. .. .. .. ..:.. ..t
     +==+ww+==+==+==+ww+==+
""",
    "VKI_Tavern_F0": """
      0  1  2  3  4  5  6  7  8
     +##+##+FF+FF+WW+##+##+##+##+
   5 #^^rWP fp fp .. BS BS:OV KW#
     +  +                 +     +
   4 #^^r.. fm fm tb ba ..d.. ..W
     +  +                 +==+==+
   3 #^^r.. .. .. .. .. .. CE ..#
     +                          +
   2 #Ss TB TB .. TB TB .. CT CK#
     +                          +
   1 W.. TB TB .. TB TB .. CT CK#
     +                          +
   0 tbx .. .. Sf .. .. .. .. bxt
     +==+ww+==+ee+==+==+ww+==+==+
""",
    "VKI_Tavern_F1": """
      0  1  2  3  4  5  6  7  8
     +##+##+##+##+WW+##+WW+##+##+
   5 #vv Ss:BX BX CH:DR CH HT HT#
     +  +  +        +           +
   4 #vvr..:tb .. ..:.. .. HT HT#
     +  +  +==+dd+==+dd+==+==+==+
   3 #vvr.. .. .. .. .. .. .. ..W
     +  +==+dd+==+==+dd+==+==+dd+
   2 #bd .. bd:bd .. bd:bd .. bd#
     +        +        +        +
   1 Wbd .. bd:bd .. bd:bd .. bdW
     +        +        +        +
   0 t.. CH ..:.. CH ..:.. CH ..t
     +==+ww+==+==+ww+==+==+ww+==+
""",
    "VKI_Smithy_F0": """
      0  1  2  3  4  5  6
     +##+##+##+FF+FF+WW+##+
   4 #WR .. BL fg fg CO GR#
     +                    +
   3 #GS .. AN .. .. QT ..#
     +                    +
   2 W.. .. .. .. .. .. WB#
     +==+==+              +
   1 #ir ..d.. .. .. .. WB#
     +     +              +
   0 tbx bx:.. EE EE .. ..t
     +==+==+==+EE+EE+ww+==+
""",
    "VKI_Workshop_F0": """
      0  1  2  3  4  5
     +##+WW+##+WW+##+##+
   4 #WB WB GR .. PL PL#
     +                 +
   3 #.. .. .. .. .. ..W
     +                 +
   2 W.. SH .. HH .. ..#
     +                 +
   1 #ba .. .. .. .. bx#
     +                 +
   0 tbx .. Sf .. WP bxt
     +==+ww+ee+==+ww+==+
""",
    "VKI_Chapel_F0": """
      0  1  2  3  4  5  6  7
     +##+##+LL+LT+LT+LL+##+##+
   5 #CH .. cd .. .. cd .. ..#
     +                       +
   4 #.. .. .. AL AL LC .. ..#
     +rr+rr+rr+     +rr+rr+rr+
   3 L.. PW PW .. .. PW PW ..L
     +                       +
   2 #.. PW PW .. .. PW PW vr#
     +                       +
   1 L.. PW PW .. .. PW PW ..L
     +                       +
   0 #FT .. .. EE EE .. .. ..#
     +==+ll+==+EE+EE+==+ll+==+
""",
}


# ---------------------------------------------------------------- §6 room data (the prop list is the source of truth)
# props: (piece, x, y, rot, style, mount[, opts]); piece short names resolve to SM_VKI_Prop_<n> / SM_VKI_<n>, and
# Prop_<n> to the reused exterior SM_VK_Prop_<n>. opts: hug (bool), z (float), on (True: stands on the prop below
# it), pull (m, back off the proud line), warn_ok, code. Zone cells: [(c0, c1, r0, r1)] inclusive, or "rest".
VKI_ROOMS = {
    "VKI_Hovel_F0": dict(
        building="Hovel", floor=0, preset="Day", family=dict(perimeter="Wattle", partition="Wattle"),
        apron_style={"floor": "ApronDirt"},
        zones={"all": dict(cells="rest", floor="Earth", wall="PlasterDaub")},
        links=[("front", "exit", "@return")], spawns={"front": (3.75, 1.60, 0)},
        props=[("Bed_Box", 1.5, 6.75, 0, None, None), ("Chest", 3.75, 6.75, 0, None, None),
               ("Pantry_Shelves_300", 6.0, 6.75, 0, None, None, {"hug": True}),
               ("Bed_Straw", 0.75, 3.0, 0, None, None), ("Hearth_Open", 3.75, 3.75, 0, None, None),
               ("Table_Trestle_150", 6.0, 2.25, 0, None, None), ("Form_150", 6.0, 1.5, 0, None, None),
               ("Form_150", 6.0, 3.0, 0, None, None), ("TableDress_Meal_A", 6.0, 2.25, 0, None, "table", {"on": True}),
               ("LogBasket", 0.75, 0.75, 180, None, None), ("Jars_Cluster", 6.75, 0.75, 180, None, None)]),
    "VKI_Cottage_F0": dict(
        building="Cottage", floor=0, preset="Day", family=dict(perimeter="Timber", partition="Board"),
        partition_wall="zone", special="Fireplace_300",
        zones={"bed": dict(cells=[(4, 5, 2, 4)], floor="Boards_NS", wall="PlasterCream"),
               "hall": dict(cells="rest", floor="FlagRustic", wall="PlasterCream")},
        links=[("front", "exit", "@return")], spawns={"front": (5.25, 1.60, 0)},
        props=[("Prop_Loom", 1.5, 6.0, 0, None, "wall_floor"), ("Rug_300x150", 4.5, 5.25, 0, None, None),
               ("Prop_Stool", 3.75, 5.25, 0, None, None), ("Prop_Stool", 5.25, 5.25, 0, None, None),
               ("Bed_Box", 7.5, 6.75, 0, None, None), ("Chest", 8.25, 5.25, -90, None, None),
               ("Shelf_Wall_150", 0.75, 3.75, 90, None, "wall_hung"),
               ("Pantry_Shelves_300", 0.75, 1.5, 90, None, None), ("Table_Trestle_300", 3.0, 1.5, 0, None, None),
               ("Form_300", 3.0, 0.75, 0, None, None), ("Form_300", 3.0, 2.25, 0, None, None),
               ("TableDress_Meal_A", 3.0, 1.5, 0, None, "table", {"on": True}),
               ("LogBasket", 8.25, 0.75, 180, None, None)]),
    "VKI_Townhouse_F0": dict(
        building="Townhouse", floor=0, preset="Day", family=dict(perimeter="Stone", partition="Stone"),
        partition_wall="zone", special="Hearth_300",
        zones={"kitchen": dict(cells=[(5, 6, 2, 4)], floor="FlagRustic", wall="StoneIn"),
               "hall": dict(cells="rest", floor="Flag", wall="PlasterWhite")},
        stairs=[("Up", 0.0, 3.0, 0, "stairA")],
        links=[("front", "exit", "@return"), ("stairA", "stair_up", "VKI_Townhouse_F1")],
        spawns={"front": (2.25, 1.60, 0), "stairA": (0.75, 2.25, 180)},
        props=[("Chest", 0.75, 0.75, 90, None, None), ("LogBasket", 2.25, 6.75, 0, None, None),
               ("Table_Trestle_300", 4.5, 3.0, 0, None, None), ("Form_300", 4.5, 2.25, 0, None, None),
               ("Form_300", 4.5, 3.75, 0, None, None), ("TableDress_Meal_B", 4.5, 3.0, 0, None, "table", {"on": True}),
               ("Rug_300x150", 4.5, 5.25, 0, None, None), ("Dresser", 6.75, 6.75, 0, None, None, {"hug": True}),
               ("Desk_Merchant", 9.0, 2.25, 0, None, None), ("Crate", 9.75, 0.75, 180, None, None),
               # plan change: the water barrel leaves the boxed-in NE corner (oven west, worktable south: 0.48 m
               # between their corners) for the west column of row 2, and both barrels face the 0.70 m gap between them
               ("Oven_150", 8.25, 6.75, 0, None, None, {"hug": True}), ("Barrel_Water", 8.25, 3.75, 90, None, None),
               ("Worktable_150", 9.75, 5.25, -90, None, None), ("Barrel", 9.75, 3.75, -90, None, None)]),
    "VKI_Townhouse_F1": dict(
        building="Townhouse", floor=1, preset="Day", family=dict(perimeter="Timber", partition="Board"),
        partition_wall="zone",
        zones={"chamber": dict(cells=[(5, 6, 0, 4)], floor="Boards_NS", wall="PlasterCream"),
               "solar": dict(cells="rest", floor="Boards_NS", wall="PlasterCream")},
        stairs=[("Down", 0.0, 3.0, 0, "stairA")],
        links=[("stairA", "stair_down", "VKI_Townhouse_F0")], spawns={"stairA": (2.25, 6.75, 90)},
        props=[("Prop_Loom", 4.5, 6.0, 0, None, "wall_floor"), ("Chest", 6.75, 6.75, 0, None, None, {"hug": True}),
               # plan change: the half-tester moves 0.75 m west (hug / pull clear the partition): centred, it left
               # 0.42-0.5 m on both sides, so neither side's use point could be reached
               ("Bed_HalfTester", 8.25, 6.0, 0, None, None),
               # plan change: the 2.6 m rug does not fit E-W between the x 7.5 partition and the east wall (2.54 m
               # clear), so it turns N-S at (8.25, 3.0) with hug (was (9.0, 3.75) rot 0)
               ("Rug_300x150", 8.25, 3.0, 90, None, None, {"hug": True}),
               ("Chest", 9.75, 2.25, -90, None, None), ("Prop_SpinningWheel", 0.75, 2.25, 0, None, None),
               ("Table_Small", 3.75, 2.25, 0, None, None), ("Prop_Stool", 3.75, 1.5, 0, None, None),
               ("Prop_Stool", 3.75, 3.0, 0, None, None), ("Candle_Plate", 3.75, 2.25, 0, None, "table", {"on": True})]),
    "VKI_Tavern_F0": dict(
        building="Tavern", floor=0, preset="Night", family=dict(perimeter="Stone", partition="Stone"),
        partition_wall="zone", special="Hearth_300", special_style={"wall_a": "StoneInWarm"},
        zones={"hearth": dict(cells=[(2, 3, 4, 5)], floor="Flag", wall="PlasterOchre"),
               "bar": dict(cells=[(7, 8, 0, 3)], floor="Flag", wall="PlasterOchre"),
               "kitchen": dict(cells=[(7, 8, 4, 5)], floor="FlagRustic", wall="PlasterOchre"),
               "hall": dict(cells="rest", floor="Boards_EW", wall="PlasterOchre")},
        stairs=[("Up", 0.0, 4.5, 0, "stairA")],
        links=[("front", "exit", "@return"), ("stairA", "stair_up", "VKI_Tavern_F1")],
        spawns={"front": (5.25, 1.60, 0), "stairA": (0.75, 3.75, 180)},
        # §6: x 3.0 / 6.0 (y 6.0-7.55), y 6.0 (x 3.0-6.0), x 10.5 (y 0-6.0); the x 3.0 / 6.0 runs continue to the
        # north wall (y 7.5-9.0: the hearth slab does not reach x 3.0 / 6.0), and the N-S pieces at the two L corners
        # sit 2 mm up (two sills meeting at an L overlap in a 0.1 m square)
        sills=[(3.0, 6.0, 90, 0.002), (3.0, 7.5, 90, 0.0), (6.0, 6.0, 90, 0.002), (6.0, 7.5, 90, 0.0),
               (3.0, 6.0, 0, 0.0), (4.5, 6.0, 0, 0.0),
               (10.5, 0.0, 90, 0.0), (10.5, 1.5, 90, 0.0), (10.5, 3.0, 90, 0.0), (10.5, 4.5, 90, 0.0)],
        props=[("LogBasket", 2.25, 8.25, 0, None, None), ("Form_300", 4.5, 6.0, 0, None, None),
               ("Prop_BarrelStack", 9.0, 8.25, 0, None, "wall_floor"), ("Table_Barrel", 6.75, 6.75, 90, None, None),
               ("TableDress_Tavern_C", 6.75, 6.75, 90, None, "table", {"on": True}),
               ("Table_Trestle_300", 3.0, 3.0, 0, None, None), ("Table_Trestle_300", 7.5, 3.0, 0, None, None),
               ("Form_300", 3.0, 2.25, 0, None, None), ("Form_300", 3.0, 3.75, 0, None, None),
               ("Form_300", 7.5, 2.25, 0, None, None), ("Form_300", 7.5, 3.75, 0, None, None),
               ("TableDress_Tavern_A", 3.0, 3.0, 0, None, "table", {"on": True}),
               ("TableDress_Tavern_B", 7.5, 3.0, 0, None, "table", {"on": True}),
               ("Bar_Counter_150", 11.25, 2.25, -90, None, None), ("Bar_Counter_150", 11.25, 3.75, -90, None, None),
               ("Bar_End_150", 11.25, 5.25, -90, None, None),
               ("CaskRack_150", 12.75, 2.25, -90, None, None), ("CaskRack_150", 12.75, 3.75, -90, None, None),
               ("Crate", 0.75, 0.75, 180, None, None), ("Crate", 12.75, 0.75, -90, None, None),
               # plan change: oven and worktable (2 x 1.20 m) do not fit between the O corner posts of the kitchen's
               # 3.0 m north wall (2.37 m clear), so both stand 3 cm off the proud line (pull) and hug the side walls;
               # the water barrel leaves the 3 x 3 m kitchen for the hall beside the kitchen door (in front of the
               # worktable it closed the only way in: 0.50 m between the oven's and the barrel's corners)
               ("Oven_150", 11.25, 8.25, 0, None, None, {"hug": True, "pull": 0.03}),
               ("Worktable_150", 12.75, 8.25, 0, None, None, {"hug": True, "pull": 0.03}),
               ("Barrel_Water", 8.25, 6.75, 0, None, None),
               ("Lantern_Wall", 2.25, 8.25, 0, None, "wall_hung"), ("Lantern_Wall", 8.25, 8.25, 0, None, "wall_hung"),
               ("Lantern_Wall", 0.75, 3.75, 90, None, "wall_hung"),
               ("Lantern_Wall", 12.75, 2.25, -90, None, "wall_hung"),
               ("Lantern_Wall", 12.75, 3.75, -90, None, "wall_hung")]),
    "VKI_Tavern_F1": dict(
        building="Tavern", floor=1, preset="Night", family=dict(perimeter="Timber", partition="Board"),
        partition_wall=None, window_style={"shutter": "Red"}, exterior="PlasterOchre",
        zones={"corridor": dict(cells=[(1, 8, 3, 3), (1, 1, 4, 5)], floor="Boards_EW", wall="PlasterOchre"),
               "rooms": dict(cells="rest", floor="Boards_NS", wall="PlasterOchre")},
        stairs=[("Down", 0.0, 4.5, 0, "stairA")],
        links=[("stairA", "stair_down", "VKI_Tavern_F0")], spawns={"stairA": (2.25, 8.25, 90)},
        props=[("Bed_Box", 4.5, 8.25, 0, None, None), ("Chest", 6.75, 8.25, 0, None, None),
               ("Table_Small", 3.75, 6.75, 0, None, None), ("Candle_Plate", 3.75, 6.75, 0, None, "table", {"on": True}),
               ("Dresser", 8.25, 8.25, 0, None, None, {"hug": True}), ("Chest", 9.75, 8.25, 0, None, None),
               ("Bed_HalfTester", 12.0, 7.5, 0, None, None),
               ("Bed_Straw", 0.75, 3.0, 0, None, None), ("Bed_Straw", 3.75, 1.5, 0, None, None),
               ("Bed_Straw", 5.25, 1.5, 0, None, None), ("Bed_Straw", 8.25, 1.5, 0, None, None),
               ("Bed_Straw", 9.75, 1.5, 0, None, None), ("Bed_Straw", 12.75, 1.5, 0, None, None),
               ("Chest", 2.25, 0.75, 180, None, None), ("Candle_Plate", 2.25, 0.75, 0, None, "table", {"on": True}),
               ("Chest", 6.75, 0.75, 180, None, None), ("Candle_Plate", 6.75, 0.75, 0, None, "table", {"on": True}),
               ("Chest", 11.25, 0.75, 180, None, None), ("Candle_Plate", 11.25, 0.75, 0, None, "table", {"on": True}),
               ("Lantern_Wall", 3.75, 8.25, 0, None, "wall_hung"), ("Lantern_Wall", 8.25, 8.25, 0, None, "wall_hung")]),
    "VKI_Smithy_F0": dict(
        building="Smithy", floor=0, preset="Day", family=dict(perimeter="Stone", partition="Board"),
        partition_wall=None, special="Forge_300",
        zones={"forge": dict(cells=[(3, 4, 2, 4)], floor="FlagRustic", wall="StoneIn"),
               "store": dict(cells=[(0, 1, 0, 1)], floor="EarthSooty", wall="StoneIn"),
               "main": dict(cells="rest", floor="EarthSooty", wall="StoneIn")},
        links=[("front", "exit", "@return")], spawns={"front": (6.0, 1.60, 0)},
        props=[("Prop_WeaponRack", 0.75, 6.75, 0, None, "wall_floor", {"hug": True}),
               ("Prop_Bellows", 3.75, 6.75, 180, None, None), ("CoalBin_150", 8.25, 6.75, 0, None, None),
               ("GoodsRack_150", 9.75, 6.75, 0, None, None, {"hug": True}), ("Prop_Anvil", 3.75, 5.25, 0, None, None),
               ("QuenchTrough_150", 8.25, 5.25, 0, None, None),
               ("Prop_Grindstone", 0.75, 5.25, 90, None, "wall_floor"),
               ("Workbench_300", 9.75, 3.0, -90, None, None),
               ("ToolWall_150", 9.75, 2.25, -90, None, "wall_hung"), ("ToolWall_150", 9.75, 3.75, -90, None, "wall_hung"),
               ("IronStock_150", 0.75, 2.25, 90, None, None), ("Crate", 0.75, 0.75, 90, None, None),
               ("Crate", 2.25, 0.75, 180, None, None)]),
    "VKI_Workshop_F0": dict(
        building="Workshop", floor=0, preset="Day", family=dict(perimeter="Timber", partition="Timber"),
        zones={"all": dict(cells="rest", floor="FlagRustic", wall="PlasterWhite")},
        links=[("front", "exit", "@return")], spawns={"front": (3.75, 1.60, 0)},
        props=[("Workbench_Carpenter", 1.5, 6.75, 0, None, None, {"hug": True}),
               ("ToolWall_150", 0.75, 6.75, 0, None, "wall_hung"), ("ToolWall_150", 0.75, 5.25, 90, None, "wall_hung"),
               ("GoodsRack_150", 3.75, 6.75, 0, None, None), ("PoleLathe", 7.5, 6.75, 0, None, None, {"hug": True}),
               ("Prop_Sawhorse", 2.25, 3.75, 0, None, None), ("Hearth_Open", 5.25, 3.75, 0, None, None),
               ("Barrel", 0.75, 2.25, 0, None, None), ("Crate", 0.75, 0.75, 180, None, None),
               ("Crate", 8.25, 2.25, 0, None, None), ("Crate", 8.25, 0.75, 180, None, None),
               ("LogBasket", 6.75, 0.75, 180, None, None)]),
    "VKI_Chapel_F0": dict(
        building="Chapel", floor=0, preset="Day", family=dict(perimeter="Ashlar", partition="Ashlar"),
        corners="pillar", rhythm_sides=True,
        zones={"dais": dict(cells=[(0, 7, 4, 5)], floor="Flag", wall="AshlarIn", dais=True),
               "nave": dict(cells="rest", floor="FlagWarm", wall="AshlarIn")},
        dais=[(0.0, 6.0), (3.0, 6.0), (6.0, 6.0), (9.0, 6.0)],
        links=[("front", "exit", "@return")], spawns={"front": (6.0, 1.60, 0)},
        # plan change: the pew rows move 0.75 m south (y 1.5 / 3.0 / 4.5, were 2.25 / 3.75 / 5.25): the last row left
        # only 0.52 m in front of the altar rail, so neither the rail's nor that row's use points could be reached
        props=[("Pew_300", 3.0, 1.5, 180, None, None), ("Pew_300", 3.0, 3.0, 180, None, None),
               ("Pew_300", 3.0, 4.5, 180, None, None), ("Pew_300", 9.0, 1.5, 180, None, None),
               ("Pew_300", 9.0, 3.0, 180, None, None), ("Pew_300", 9.0, 4.5, 180, None, None),
               # §6 rail chain from wall to wall: the end pieces are let into the wall / respond by up to 0.32 m
               # (the master carries vki_edge=1, vki_edge_let_in=0.32; vki_check honours it)
               ("AltarRail_150", 0.0, 6.0, 0, None, "edge", {"z": 0.20}),
               ("AltarRail_150", 1.5, 6.0, 0, None, "edge", {"z": 0.20}),
               ("AltarRail_150", 3.0, 6.0, 0, None, "edge", {"z": 0.20}),
               ("AltarRail_150", 7.5, 6.0, 0, None, "edge", {"z": 0.20}),
               ("AltarRail_150", 9.0, 6.0, 0, None, "edge", {"z": 0.20}),
               ("AltarRail_150", 10.5, 6.0, 0, None, "edge", {"z": 0.20}),
               ("Altar_300", 6.0, 7.5, 0, None, None, {"z": 0.20, "warn_ok": "window"}),
               ("CandleStand_Pricket", 3.75, 8.25, 0, None, None, {"z": 0.20}),
               ("CandleStand_Pricket", 8.25, 8.25, 0, None, None, {"z": 0.20}),
               ("Lectern", 9.0, 6.75, 180, None, None, {"z": 0.20}), ("Chest", 0.75, 8.25, 90, None, None, {"z": 0.20}),
               ("Font", 0.75, 0.75, 90, None, None, {"hug": True}), ("VotiveRack", 11.25, 3.75, -90, None, None),
               ("Runner_150", 6.0, 2.25, 90, None, None), ("Runner_300", 6.0, 4.5, 90, None, None)]),
}
# every change to a §6 plan or prop list, with the reason (the coordinator reviews these)
VKI_PLAN_CHANGES = [
    "VKI_Townhouse_F1 plan row 2: '..d rg rgW' -> '..drg rgW' (typo: the extra space shifted the east half of the "
    "row by one column, so the east wall's 'W' fell outside the plan and the parser saw a perimeter gap).",
    "VKI_Townhouse_F1: Rug_300x150 (9.0, 3.75) rot 0 -> (8.25, 3.0) rot 90 + hug: 2.60 m does not fit E-W in the "
    "chamber (2.54 m between the Board partition's and the east wall's caps); it now also serves as the east mat "
    "of the x 7.5 doorway.",
    "VKI_Tavern_F0 kitchen: Oven_150 and Worktable_150 keep their §6 places but stand 3 cm off the proud line (pull "
    "0.03) and hug the side walls: 2 x 1.20 m do not fit between the O corner posts of the 3.0 m north wall (2.37 m "
    "clear after the §10.3 post hug). Barrel_Water moves from the kitchen (12.75, 6.75) -90 to the hall beside the "
    "kitchen door, (8.25, 6.75) 0: in the 3 x 3 m kitchen it closed the only way to the worktable (0.50 m between the "
    "oven's and the barrel's corners; the capsule needs 0.60). Plan codes updated.",
    "VKI_Tavern_F0: Crate (12.75, 0.75) at rot -90 (was 180): its use point faced the cask rack (0.52 m gap); now it "
    "faces the aisle behind the bar.",
    "VKI_Tavern_F0: Table_Barrel (and its TableDress_Tavern_C) at rot 90 (was 0): the north use point sat behind the "
    "1.05 m table, hidden from the camera (T19); turned, the use points face east / west.",
    "VKI_Smithy_F0: Crate (0.75, 0.75) at rot 90 (was 180): its use point faced the IronStock_150 (blocked); now it "
    "faces the gap between the two crates.",
    "VKI_Townhouse_F0 kitchen: Barrel_Water (9.75, 6.75) 0 -> (8.25, 3.75) rot 90 and Barrel (9.75, 3.75) at rot -90: "
    "boxed in by the oven and the worktable (0.48 m between their corners), the water barrel could not be reached, and "
    "the barrel's use point lay in the y 3.0 partition; now both face the 0.70 m gap between them. Plan codes updated.",
    "VKI_Townhouse_F1: Bed_HalfTester (9.0, 6.0) -> (8.25, 6.0) (hug + pull clear the partition): centred in the "
    "2.54 m chamber it left 0.42 / 0.50 m on its sides, so neither use point could be reached.",
    "VKI_Chapel_F0: Pew_300 rows at y 1.5 / 3.0 / 4.5 (were 2.25 / 3.75 / 5.25): the last row left 0.52 m before the "
    "altar rail, so the rail's use points and that row's could not be reached (capsule 0.6 m).",
    "VKI_Chapel_F0: Lectern (8.25, 6.75) 0 -> (9.0, 6.75) rot 180: its use point lay between the rail and the lectern "
    "(0.45 m), and the lectern hid the east pricket's use point from the camera (T19); the reader now stands on the "
    "dais facing the nave.",
    "VKI_Chapel_F0: Font (0.75, 0.75) at rot 90 (was 0): its use point lay inside the Cut south wall (rot 180 would "
    "hide it behind the font, T19); now it faces east.",
    "VKI_Tavern_F0 sills: the x 3.0 / 6.0 runs continue from y 7.5 to the north wall (the hearth slab does not reach "
    "x 3.0 / 6.0, so the Boards_EW | Flag joint lay open); the two N-S pieces at the L corners (3.0, 6.0) / (6.0, 6.0) "
    "sit 2 mm up so their tops do not overlap the E-W run's in the 0.1 m corner square.",
    "VKI_Chapel_F0: Runner_150 / Runner_300 at rot 90 (along the aisle, so the u-periodic runners chain at y 3.0).",
    "VKI_Hovel_F0 / VKI_Cottage_F0 / VKI_Workshop_F0: LogBasket beside the south wall at rot 180 (was 0): its use point "
    "(local 0, -0.70) lay inside the Cut south wall; turned, it faces the room.",
    "Placement fallbacks (automatic, recorded on the instance): VKI_Cottage_F0 Bed_Box (2.40 m between the T post at "
    "x 6.0 and the NE corner post: 2.37 m clear) and VKI_Smithy_F0 Prop_WeaponRack (1.52 m wide: its hug needs 0.325 > "
    "0.30 past the NW corner post) stand 3 cm off the proud line (vki_pull 0.03) so the post squares no longer bind; "
    "VKI_Townhouse_F1 Bed_HalfTester takes the same fallback after its move.",
]


# ---------------------------------------------------------------- parser (§6 plan legend)
def vki_parse_plan(txt):
    """ASCII plan -> dict(nc, nr, W, D, ew{(i, j): token}, ns{(i, r): char}, codes{(c, r): code}).
    ew[(i, j)] is the E-W wall token of the segment from node (i, j) to (i + 1, j); ns[(i, r)] the N-S wall char of
    the segment from node (i, r) to (i, r + 1); codes[(c, r)] the cell code. Row 0 is the camera (south) side."""
    lines = [l.rstrip() for l in txt.split("\n") if l.strip()]
    body = [l for l in lines if not re.match(r"^\s*\d+(\s+\d+)*\s*$", l)]
    nodes = [l for l in body if l.lstrip().startswith("+")]
    cells = [l for l in body if not l.lstrip().startswith("+")]
    c0 = nodes[0].index("+")
    nc = (len(nodes[0]) - 1 - c0) // 3
    nr = len(cells)
    if len(nodes) != nr + 1:
        raise ValueError(f"plan: {len(nodes)} node rows for {nr} cell rows")
    ch = lambda l, i: l[i] if i < len(l) else " "
    ew, ns, codes = {}, {}, {}
    for k, l in enumerate(nodes):
        j = nr - k
        for i in range(nc):
            ew[(i, j)] = ch(l, c0 + 3 * i + 1) + ch(l, c0 + 3 * i + 2)
    for k, l in enumerate(cells):
        r = nr - 1 - k
        lab = l[:c0].strip()
        if lab and int(lab) != r:
            raise ValueError(f"plan: row label {lab} where row {r} was expected")
        for i in range(nc + 1):
            ns[(i, r)] = ch(l, c0 + 3 * i)
        for i in range(nc):
            codes[(i, r)] = ch(l, c0 + 3 * i + 1) + ch(l, c0 + 3 * i + 2)
    return dict(nc=nc, nr=nr, W=VKI_IG * nc, D=VKI_IG * nr, ew=ew, ns=ns, codes=codes)


def vki_rooms_zone_map(R, nc, nr):
    """{(c, r): zone name}; listed zones first (in order), then the 'rest' zone"""
    zc = {}
    for zn, z in R["zones"].items():
        if z["cells"] == "rest":
            continue
        for (a0, a1, b0, b1) in z["cells"]:
            for c in range(a0, a1 + 1):
                for r in range(b0, b1 + 1):
                    zc.setdefault((c, r), zn)
    rest = next((zn for zn, z in R["zones"].items() if z["cells"] == "rest"), None)
    for c in range(nc):
        for r in range(nr):
            zc.setdefault((c, r), rest)
    return zc


def vki_rooms_even(a):
    return abs(a / 3.0 - round(a / 3.0)) < 1e-6


def vki_rooms_wall_name(fam, kind, height, n, var="A", side=None, special=None):
    """§3 piece name of a wall segment kind"""
    if kind == "Plain":
        return f"SM_VKI_Wall_{fam}_Plain_300_{height}" if n == 2 else f"SM_VKI_Wall_{fam}_Plain_150{var}_{height}"
    if kind == "Window":
        return f"SM_VKI_Wall_{fam}_Window_150_{height}"
    if kind in ("Door", "Exit"):
        return f"SM_VKI_Wall_{fam}_Door_150_{height}"
    if kind == "ExitWide":
        return f"SM_VKI_Wall_{fam}_DoorWide_300_{height}"
    if kind == "Lancet":
        return f"SM_VKI_Wall_{fam}_Lancet_150_{height}"
    if kind == "LancetTall":
        return f"SM_VKI_Wall_{fam}_LancetTall_150_Full"
    if kind == "Rake":
        return f"SM_VKI_Wall_{fam}_Rake_150_{side}"
    if kind == "Special":
        return f"SM_VKI_Wall_{fam}_{special}_{height}"
    if kind == "Bars":
        return f"SM_VKI_Wall_{fam}_Plain_300_Full" if n == 2 else f"SM_VKI_Wall_{fam}_Plain_150A_Full"
    if kind == "BarsGate":
        return f"SM_VKI_Wall_{fam}_Door_150_Full"
    if kind == "Niche":
        return f"SM_VKI_Wall_{fam}_Niche_150_{height}"
    if kind == "Passage":
        return f"SM_VKI_Wall_{fam}_Passage_150_Full"
    if kind == "Gap":
        return f"SM_VKI_Wall_{fam}_Gap_150_{height}"
    if kind == "Breach":
        return f"SM_VKI_Wall_{fam}_Breach_{300 if n == 2 else 150}_{height}"
    if kind == "Named":                      # special = the piece name (R["specials"][token]), e.g. "Wall_Dungeon_DartTrap_150_Full"
        return special if special.startswith("SM_VKI_") else "SM_VKI_" + special
    raise ValueError(kind)


def vki_rooms_stair_frame(x, y, rot, lx, ly):
    """stair-local (lx, ly) -> world (x, y) for a stair at (x, y) with rotation rot (0 / 90 / -90)"""
    r = math.radians(rot)
    return (x + math.cos(r) * lx - math.sin(r) * ly, y + math.sin(r) * lx + math.cos(r) * ly)


def vki_rooms_stair_cells(R):
    """{(c, r): ('Up'|'Down', index)} footprint cells of the stairs (the 1 x 3 cells of local [0, 1.5] x [0, 4.5],
    through the stair's frame: rot 0 runs +Y, 90 runs -X along an E-W wall on its south side, -90 runs +X along an
    E-W wall on its north side)"""
    out = {}
    for si, st_ in enumerate(R.get("stairs", [])):
        kind, x, y, rot, lid = st_[:5]
        for d in range(3):
            cx, cy = vki_rooms_stair_frame(x, y, rot, 0.75, 0.75 + VKI_IG * d)       # the cell centre
            out[(int(math.floor(cx / VKI_IG)), int(math.floor(cy / VKI_IG)))] = (kind, si)
    return out


def vki_rooms_layout(name, R=None, P=None):
    """pure layout of a §6 scene (no Blender objects): wall pieces, posts (§2.3), floors (§2.7), specials, exits,
    stairs, door cells. Returns a dict; 'problems' lists plan-level errors found while laying out. R / P override the
    registered room and plan (a cave map lays out its walls this way, R["open_frame"]: no closed perimeter)."""
    if R is None and name not in VKI_ROOMS:  # a generated level (vki_cave_generate): regenerate it from the scene's record
        sc_ = bpy.data.scenes.get(name)
        gp = vki_get(sc_, "vki_generated", None) if sc_ is not None else None
        if gp:
            vki_cave_generate(name, build=False, **gp)
    R = VKI_ROOMS[name] if R is None else R
    P = vki_parse_plan(VKI_PLANS[name]) if P is None else P
    nc, nr, W, D = P["nc"], P["nr"], P["W"], P["D"]
    zmap = vki_rooms_zone_map(R, nc, nr)
    if R.get("cave"):                    # adventure kit: a cave level is a cell map of rock tiles (vki_rooms_adventure)
        return vki_cave_layout(name, R, P, zmap)
    fam_p, fam_i = R["family"]["perimeter"], R["family"].get("partition", R["family"]["perimeter"])
    problems = []
    # ---- segments
    segs = {}
    for (i, j), tok in P["ew"].items():
        kind, ht = VKI_ROOMS_TOK_EW.get(tok, (None, None))
        if tok not in VKI_ROOMS_TOK_EW:
            problems.append(f"plan: unknown E-W token {tok!r} at node ({i},{j})")
        role = "N" if j == nr else ("S" if j == 0 else "part")
        segs[("EW", i, j)] = dict(ori="EW", i=i, j=j, tok=tok, kind=kind, height=ht, role=role,
                                  fam=VKI_ROOMS_OWN_FAMILY.get(kind) or (fam_i if role == "part" else fam_p))
    for (i, r), c in P["ns"].items():
        kind, ht = VKI_ROOMS_TOK_NS.get(c, (None, None))
        if c not in VKI_ROOMS_TOK_NS:
            problems.append(f"plan: unknown N-S char {c!r} at node ({i},{r})")
        role = "W" if i == 0 else ("E" if i == nc else "part")
        segs[("NS", i, r)] = dict(ori="NS", i=i, j=r, tok=c, kind=kind, height=ht, role=role,
                                  fam=VKI_ROOMS_OWN_FAMILY.get(kind) or (fam_i if role == "part" else fam_p))
    walls = lambda s: s is not None and s["kind"] not in (None, "Rail")
    # perimeter must be closed (not in a cave map: its walls stand in the rock and the open cave)
    for i in range(nc if not R.get("open_frame") else 0):
        for j in (0, nr):
            if not walls(segs[("EW", i, j)]):
                problems.append(f"plan: perimeter gap at E-W segment ({i},{j})")
    for r in range(nr if not R.get("open_frame") else 0):
        for i in (0, nc):
            if not walls(segs[("NS", i, r)]):
                problems.append(f"plan: perimeter gap at N-S segment ({i},{r})")
    # arms per node (for the junction test of the 300 pairing)
    arms = {}
    for s in segs.values():
        if not walls(s):
            continue
        if s["ori"] == "EW":
            arms.setdefault((s["i"], s["j"]), set()).add("E"); arms.setdefault((s["i"] + 1, s["j"]), set()).add("W")
        else:
            arms.setdefault((s["i"], s["j"]), set()).add("N"); arms.setdefault((s["i"], s["j"] + 1), set()).add("S")
    junction = lambda nd: len(arms.get(nd, ())) >= 3 or (arms.get(nd) and arms[nd] not in ({"E", "W"}, {"N", "S"})
                                                          and len(arms[nd]) == 2)
    # props near a segment (the B variant stays off segments with props against them)
    ppts = [(p[1], p[2]) for p in R.get("props", [])]
    # ---- pieces
    pieces = []
    special = R.get("special")
    for ori, nline, nalong in (("EW", nr + 1, nc), ("NS", nc + 1, nr)):
        for ln in range(nline):
            k = 0
            while k < nalong:
                s = segs[(ori, k, ln)] if ori == "EW" else segs[(ori, ln, k)]
                if not walls(s):
                    k += 1
                    continue
                kind, ht, fam, role = s["kind"], s["height"], s["fam"], s["role"]
                n = 1
                named = None
                if kind == "Named":
                    named = R.get("specials", {}).get(s["tok"].strip())
                    if not named:
                        problems.append(f"plan: named token {s['tok']!r} at {ori} ({k},{ln}) has no R['specials'] entry")
                        named = "SM_VKI_Wall_%s_Plain_150A_%s" % (fam, ht)
                    if "_300_" in named or named.endswith("_300"):
                        n = 2
                if kind in ("Special", "ExitWide"):
                    s2 = (segs.get((ori, k + 1, ln)) if ori == "EW" else segs.get((ori, ln, k + 1)))
                    if s2 is None or s2["kind"] != kind:
                        problems.append(f"plan: {s['tok']} at {ori} ({k},{ln}) needs a second cell")
                    n = 2
                elif kind in ("Plain", "Bars", "Breach"):
                    s2 = (segs.get((ori, k + 1, ln)) if ori == "EW" else segs.get((ori, ln, k + 1)))
                    mid = (k + 1, ln) if ori == "EW" else (ln, k + 1)
                    if (k % 2 == 0 and s2 is not None and s2["kind"] == kind and s2["height"] == ht and
                            s2["fam"] == fam and not junction(mid)):
                        n = 2
                if kind == "Rake" and not VKI_FAMILIES.get(fam, {}).get("rake"):
                    kind, ht = "Plain", "Full"                  # pillar (Ashlar, Board)
                if kind == "Special" and not special:
                    problems.append(f"plan: FF at {ori} ({k},{ln}) but the room has no special")
                # position / rotation (§2.1 perimeter placement; partitions run W->E / S->N)
                if ori == "EW":
                    x0, x1, y0 = VKI_IG * k, VKI_IG * (k + n), VKI_IG * ln
                    rot, ox, oy = (180, x1, y0) if role == "S" else (0, x0, y0)
                    cells = [(k + d, ln) for d in range(n)]            # north side
                    south = [(k + d, ln - 1) for d in range(n)]
                    fa, fb = (cells, south) if rot == 180 else (south, cells)
                    nodes = [(k, ln), (k + n, ln)]
                else:
                    y0, y1, x0 = VKI_IG * k, VKI_IG * (k + n), VKI_IG * ln
                    rot, ox, oy = (-90, x0, y1) if role == "E" else (90, x0, y0)
                    east = [(ln, k + d) for d in range(n)]
                    west = [(ln - 1, k + d) for d in range(n)]
                    fa, fb = (west, east) if rot == -90 else (east, west)
                    nodes = [(ln, k), (ln, k + n)]
                inside = lambda c: 0 <= c[0] < nc and 0 <= c[1] < nr
                var = "A"
                limewash = fam == "Stone" and any(str(R["zones"].get(zmap.get(c_), {}).get("wall", "")).startswith("Plaster")
                                                  for c_ in fa)
                if kind == "Plain" and n == 1 and ht == "Full" and role != "part" and \
                        fam in ("Timber", "Stone", "Wattle", "Dungeon", "Ancient", "Sewer") \
                        and k % 2 == 1 and not limewash:
                    mx, my = ((x0 + VKI_IG * 0.5, y0) if ori == "EW" else (x0, y0 + VKI_IG * 0.5))
                    if not any(math.hypot(px - mx, py - my) < 1.3 for px, py in ppts):
                        var = "B"
                side = None
                if kind == "Rake":
                    side = "L" if role == "W" else "R"
                    if role not in ("W", "E") or k != 0:
                        problems.append(f"plan: rake 't' at {ori} ({ln},{k}) is not the south-most side-wall piece")
                pname = vki_rooms_wall_name(fam, kind, ht if kind != "Rake" else "Rake", n, var, side,
                                            named if kind == "Named" else special)
                if kind == "Named":                                  # a named piece may be another family's
                    pf_ = vki_parse_name(pname).get("fam")
                    if pf_ in VKI_FAMILIES:
                        fam = pf_
                # end heights (a rake's low end is its south end: Cut)
                h_end = {}
                for nd in nodes:
                    h_end[nd] = ("Cut" if nd[1] == 0 else "Full") if kind == "Rake" else ht
                pieces.append(dict(piece=pname, kind=kind, height=ht, fam=fam, cls=VKI_FAMILIES[fam]["cls"], n=n,
                                   ori=ori, role=role, line=ln, k=k, x=ox, y=oy, rot=rot, var=var,
                                   face_a=[c for c in fa if inside(c)], face_b=[c for c in fb if inside(c)],
                                   nodes=nodes, h_end=h_end, tok=s["tok"]))
                k += n
    # ---- posts (§2.3 / §10.1): ends per node
    ends = {}
    for pi, pc in enumerate(pieces):
        for nd, other in ((pc["nodes"][0], pc["nodes"][1]), (pc["nodes"][1], pc["nodes"][0])):
            d = (other[0] - nd[0], other[1] - nd[1])
            ln_ = math.hypot(*d)
            ends.setdefault(nd, []).append(dict(d=(d[0] / ln_, d[1] / ln_), fam=pc["fam"], cls=pc["cls"],
                                                h=pc["h_end"][nd], pi=pi))
    stair_nodes = set()
    for st_ in R.get("stairs", []):
        kind, sx, sy, srot, lid = st_[:5]
        # the nodes along the stair's walls: local x = 0 (y 0..4.5) and y = 4.5 (x 0..1.5), in any rotation
        for lx, ly in [(0.0, VKI_IG * d) for d in range(4)] + [(VKI_IG, 3 * VKI_IG)]:
            wx, wy = vki_rooms_stair_frame(sx, sy, srot, lx, ly)
            stair_nodes.add((int(round(wx / VKI_IG)), int(round(wy / VKI_IG))))
    posts = []
    for nd, es in sorted(ends.items()):
        dirs = [e["d"] for e in es]
        corner = any(abs(a[0] * b[1] - a[1] * b[0]) > 0.5 for a in dirs for b in dirs)
        fams = sorted({e["fam"] for e in es}, key=lambda f: VKI_POST_PRIO.index(f))
        pf = fams[0]
        ph = "Full" if any(e["h"] == "Full" for e in es) else "Cut"
        along_x = abs(es[0]["d"][0]) > 0.5
        x, y = VKI_IG * nd[0], VKI_IG * nd[1]
        base = dict(node=nd, x=x, y=y, fam=pf, height=ph)
        if corner:
            posts.append(dict(base, kind="Corner", rot=0, why="L/T/X junction", req=True))
        elif len(es) == 1:
            posts.append(dict(base, kind="Mid", rot=0 if along_x else 90, why="free end", req=True))
        elif any((e["h"], e["fam"], e["cls"]) != (es[0]["h"], es[0]["fam"], es[0]["cls"]) for e in es[1:]):
            posts.append(dict(base, kind="Mid", rot=0 if along_x else 90, why="height/family/class step", req=True))
        else:
            fam = es[0]["fam"]
            along = x if along_x else y
            side_wall = nd[0] in (0, nc) and not along_x
            rh = VKI_FAMILIES[fam]["rhythm"] or (fam == "Ashlar" and R.get("rhythm_sides") and side_wall)
            if rh and vki_rooms_even(along) and nd not in stair_nodes:
                posts.append(dict(base, kind="Mid", rot=0 if along_x else 90, why="rhythm (even node)", req=False))
        if posts and posts[-1]["node"] == nd and posts[-1]["fam"] == "Ashlar" and posts[-1]["kind"] == "Mid" and \
                posts[-1]["height"] == "Cut":
            posts[-1].update(kind="Corner", rot=0)       # there is no Post_Ashlar_Mid_Cut: all-Cut Mid nodes take Corner_Cut
    for p in posts:
        p["piece"] = f"SM_VKI_Post_{p['fam']}_{p['kind']}_{p['height']}"
    # ---- floors (§2.7): greedy 600 -> 300 (even nodes) -> Q150 per zone; Stair_Down footprints excluded
    scells = vki_rooms_stair_cells(R)
    pcells = vki_rooms_pit_cells(R)
    floors = []
    for zn, z in R["zones"].items():
        cells = {c for c, zz in zmap.items() if zz == zn and not (c in scells and scells[c][0] == "Down")
                 and c not in pcells}
        if z.get("dais"):
            for (dx, dy) in R.get("dais", []):
                blk = {(int(round(dx / VKI_IG)) + a, int(round(dy / VKI_IG)) + b) for a in (0, 1) for b in (0, 1)}
                if not blk <= cells:
                    problems.append(f"floors: dais at ({dx},{dy}) leaves zone {zn}")
                cells -= blk
                floors.append(dict(piece="SM_VKI_Floor_Dais_300", x=dx, y=dy, zone=zn, style={"floor": z["floor"]}))
            if cells:
                problems.append(f"floors: dais zone {zn} cells without a dais: {sorted(cells)}")
            continue
        for S, n in ((6.0, 4), (3.0, 2)):
            for (i, j) in sorted(cells):
                x, y = VKI_IG * i, VKI_IG * j
                blk = {(i + a, j + b) for a in range(n) for b in range(n)}
                if vki_rooms_even(x) and vki_rooms_even(y) and blk <= cells:
                    cells -= blk
                    floors.append(dict(piece=f"SM_VKI_Floor_{int(S * 100)}", x=x, y=y, zone=zn,
                                       style={"floor": z["floor"]}))
        for (i, j) in sorted(cells):
            floors.append(dict(piece=f"SM_VKI_Floor_150_Q{i % 2}{j % 2}", x=VKI_IG * i, y=VKI_IG * j, zone=zn,
                               style={"floor": z["floor"]}))
    # ---- doors: cells on both sides (exits: the inside cells)
    doors = []
    for pi, pc in enumerate(pieces):
        if pc["kind"] in ("Door", "Exit", "ExitWide", "BarsGate", "Gap", "Breach"):
            cells = pc["face_a"] + pc["face_b"]
            doors.append(dict(pi=pi, kind=pc["kind"], cells=cells, ori=pc["ori"]))
        elif pc["kind"] == "Passage":
            cells = pc["face_a"]
            doors.append(dict(pi=pi, kind=pc["kind"], cells=cells, ori=pc["ori"]))
    return dict(name=name, R=R, P=P, nc=nc, nr=nr, W=W, D=D, zmap=zmap, segs=segs, pieces=pieces, posts=posts,
                floors=floors, doors=doors, stair_cells=scells, pit_cells=pcells, problems=problems)


# ---------------------------------------------------------------- placeholders (PACKAGES.md: PH_<piece>)
# A missing master is placed as PH_<piece minus SM_VKI_>: a grey box (or 16-sided cylinder) with the spec footprint
# and height (§3, §5), vki_placeholder=1 and the same metadata contract (class, mount, footprint, collider, back_y,
# use points, light / FX sockets, triggers, spawns, leaf sockets), so layout checks, BFS and camera tests work before
# the packages land. The masters (PHM_*) live in the hidden collection VKI_Rooms_Placeholders.
def vki_ph_lt(role, pos, w, color=(1.0, .52, .22), rng=5.0, radius=0.10, flicker=1):
    return dict(type="POINT", role=role, pos=list(pos), w=w, color=list(color), range=rng, flicker=flicker,
                shadows=1, radius=radius)


VKI_PH_WIN_SPOT = dict(type="SPOT", role="window", pos=[0.75, 2.0, 4.2], aim=[0.75, -1.35, 0.0], cone=24.0,
                       blend=0.15, radius=0.05, w_day=1000.0, w_night=150.0, color_day=[.82, .88, 1.0],
                       color_night=[.62, .70, 1.0], shadows=1)
VKI_PH_LANCET_SPOT = dict(VKI_PH_WIN_SPOT, pos=[0.75, 2.4, 5.4], aim=[0.75, -1.6, 0.0], cone=26.0,
                          color_day=[1.0, .86, .66], color_night=[.70, .66, .90])
VKI_PH_CANDLE = lambda p: vki_ph_lt("candle", p, 15.0, (1.0, .62, .30), 2.5, 0.03)
# (W, D, H, mount, tier, extra): W along local x, D along y (back +Y), H up from z0; extra: z0, x0 (min x when the
# footprint is not centred), y0, round, use ("front"), lights, fx, cls
VKI_PH_PROPS = {
    "Table_Trestle_300": (2.70, 0.90, 0.80, "floor", "furniture", {}),
    "Table_Trestle_150": (1.20, 0.90, 0.80, "floor", "furniture", {}),
    "Table_Small": (1.10, 0.75, 0.78, "floor", "furniture", {}),
    "Form_300": (2.70, 0.35, 0.48, "floor", "furniture", {}),
    "Form_150": (1.20, 0.35, 0.48, "floor", "furniture", {}),
    "Chest": (1.10, 0.60, 0.65, "wall_floor", "furniture", {"use": "front"}),
    "Dresser": (1.20, 0.50, 1.90, "wall_floor", "furniture", {"use": "front"}),
    "Shelf_Wall_150": (1.20, 0.30, 0.60, "wall_hung", "dressing", {"z0": 1.20}),
    "Pantry_Shelves_300": (2.70, 0.50, 1.90, "wall_floor", "furniture", {"use": "front"}),
    "Barrel": (0.80, 0.80, 1.00, "floor", "furniture", {"round": 1}),
    "Barrel_Water": (0.80, 0.80, 1.00, "floor", "furniture", {"round": 1}),
    "Crate": (0.75, 0.75, 0.75, "floor", "furniture", {}),
    "Jars_Cluster": (0.90, 0.60, 0.70, "wall_floor", "dressing", {}),
    "LogBasket": (0.80, 0.60, 0.60, "floor", "furniture", {}),
    "Bed_Straw": (0.90, 2.00, 0.45, "floor", "furniture", {}),
    "Bed_Box": (2.40, 1.20, 1.80, "wall_floor", "furniture", {"use": "front"}),
    "Bed_HalfTester": (1.70, 2.30, 2.20, "wall_floor", "hero", {"use": "front"}),
    "Hearth_Open": (1.30, 1.30, 1.20, "floor", "hero", {"use": "front", "lights": [vki_ph_lt("hearth", (0, 0, 0.5), 250.0,
                                                                                               rng=6.0, radius=0.25)],
                                                        "fx": [dict(fx="fire_small", pos=[0.0, 0.0, 0.2])]}),
    "Oven_150": (1.20, 1.20, 1.90, "wall_floor", "hero", {"use": "front",
                                                          "lights": [vki_ph_lt("oven", (0, -0.45, 0.45), 150.0)]}),
    "Worktable_150": (1.20, 0.75, 0.85, "wall_floor", "furniture", {"use": "front"}),
    "Desk_Merchant": (1.50, 0.75, 1.10, "floor", "furniture", {"use": "front"}),
    "TableDress_Meal_A": (1.00, 0.50, 0.25, "table", "dressing", {}),
    "TableDress_Meal_B": (1.00, 0.50, 0.25, "table", "dressing", {}),
    "Bar_Counter_150": (1.50, 0.70, 1.05, "floor", "furniture", {"use": "front"}),
    "Bar_End_150": (1.20, 0.70, 1.05, "floor", "furniture", {"x0": -0.45}),
    "CaskRack_150": (1.20, 0.90, 1.20, "wall_floor", "furniture", {"use": "front"}),
    "Table_Barrel": (0.90, 0.90, 1.05, "floor", "furniture", {"round": 1}),
    "TableDress_Tavern_A": (1.60, 0.50, 0.25, "table", "dressing", {"lights": [VKI_PH_CANDLE((0.55, 0.0, 0.25))],
                                                                   "fx": [dict(fx="candle", pos=[0.55, 0.0, 0.25])]}),
    "TableDress_Tavern_B": (1.60, 0.50, 0.25, "table", "dressing", {"lights": [VKI_PH_CANDLE((-0.55, 0.0, 0.25))],
                                                                   "fx": [dict(fx="candle", pos=[-0.55, 0.0, 0.25])]}),
    "TableDress_Tavern_C": (0.60, 0.60, 0.25, "table", "dressing", {"lights": [VKI_PH_CANDLE((0.0, 0.0, 0.25))],
                                                                   "fx": [dict(fx="candle", pos=[0.0, 0.0, 0.25])]}),
    "Lantern_Wall": (0.30, 0.45, 0.60, "wall_hung", "dressing", {"z0": 1.90, "lights": [
        vki_ph_lt("lantern", (0.0, 0.0, 2.15), 60.0, (1.0, .60, .28), 4.0, 0.05)]}),
    "Candle_Plate": (0.14, 0.14, 0.25, "table", "dressing", {"round": 1, "lights": [VKI_PH_CANDLE((0, 0, 0.25))],
                                                             "fx": [dict(fx="candle", pos=[0.0, 0.0, 0.25])]}),
    "Candlestick": (0.14, 0.14, 0.30, "table", "dressing", {"round": 1, "lights": [VKI_PH_CANDLE((0, 0, 0.32))]}),
    "Workbench_300": (2.70, 0.80, 0.90, "wall_floor", "furniture", {"use": "front"}),
    "QuenchTrough_150": (1.20, 0.60, 0.70, "floor", "furniture", {"use": "front"}),
    "CoalBin_150": (1.20, 0.90, 0.70, "wall_floor", "furniture", {"use": "front"}),
    "IronStock_150": (1.20, 0.60, 1.20, "wall_floor", "furniture", {"use": "front"}),
    "ToolWall_150": (1.20, 0.14, 1.20, "wall_hung", "dressing", {"z0": 1.10}),
    "GoodsRack_150": (1.20, 0.40, 1.80, "wall_floor", "furniture", {"use": "front"}),
    "Workbench_Carpenter": (2.40, 0.90, 0.95, "wall_floor", "furniture", {"use": "front"}),
    "PoleLathe": (2.40, 0.90, 2.20, "wall_floor", "hero", {"use": "front"}),
    "Pew_300": (2.70, 0.55, 0.80, "floor", "furniture", {}),
    "Altar_300": (1.80, 0.90, 1.05, "floor", "hero", {"use": "front", "lights": [VKI_PH_CANDLE((-0.6, 0.2, 1.35)),
                                                                                 VKI_PH_CANDLE((0.6, 0.2, 1.35))]}),
    "AltarRail_150": (1.50, 0.30, 0.75, "floor", "furniture", {"x0": 0.0, "y0": 0.02, "edge": 1}),
    "CandleStand_Pricket": (0.60, 0.60, 1.40, "floor", "furniture", {"round": 1, "lights": [
        vki_ph_lt("candle", (0, 0, 1.45), 30.0, (1.0, .62, .30), 3.0, 0.04)]}),
    "Lectern": (0.60, 0.60, 1.30, "floor", "furniture", {"use": "front"}),
    "Font": (1.00, 1.00, 1.10, "floor", "furniture", {"round": 1, "use": "front"}),
    "VotiveRack": (1.00, 0.40, 1.00, "wall_floor", "furniture", {"use": "front", "lights": [
        vki_ph_lt("candle", (0, -0.05, 0.95), 30.0, (1.0, .62, .30), 3.0, 0.05)]}),
    "Runner_300": (3.00, 1.00, 0.025, "floor", "dressing", {"cls": "overlay"}),
    "Runner_150": (1.50, 1.00, 0.025, "floor", "dressing", {"cls": "overlay"}),
}


def vki_ph_short(piece):
    return piece[7:] if piece.startswith("SM_VKI_") else (piece[6:] if piece.startswith("SM_VK_") else piece)


def vki_ph_mat(kind):
    n, col = VKI_ROOMS_PH_MATS[kind]
    m = bpy.data.materials.get(n)
    if m is None:
        m = bpy.data.materials.new(n)
        m.use_nodes = True
        b = next(nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*col, 1.0)
        b.inputs["Roughness"].default_value = 0.9
        m.diffuse_color = (*col, 1.0)
    return m


def vki_ph_wall_spec(fam, kind, n, height, side=None, special=None):
    """boxes [(x0, y0, z0, x1, y1, z1)] or ('prism', poly (x, z), y0, y1) + metadata of a missing wall piece"""
    cls = VKI_FAMILIES[fam]["cls"]
    T, chw = VKI_T[cls], VKI_CAP_HW[cls]
    H = VKI_H_FULL[fam]
    L = VKI_IG * n
    top = H if height == "Full" else VKI_CUT_H
    t2 = T / 2
    meta = dict(vki_class="wall", vki_family=fam, vki_kind=kind, vki_len=L, vki_height=height if kind != "Rake" else "Rake",
                vki_thick=T, vki_collider=[[L / 2, 0.0, 1.1, L, T, 2.2]], vki_nav="block", vki_origin="start_node",
                vki_uv_lock="world")
    geo = []

    def body(x0, x1, z0, z1):
        geo.append((x0, -t2, z0, x1, t2, z1))

    def cap(x0, x1, zt):
        geo.append((x0, -chw, zt - 0.10, x1, chw, zt))
    if kind == "Rake":
        lo, hi = 0.32, 1.18
        pts = [(0.0, -0.30), (L, -0.30), (L, H), (L - lo, H), (L - hi, VKI_CUT_H), (0.0, VKI_CUT_H)] if side == "R" else \
              [(0.0, -0.30), (L, -0.30), (L, H), (hi, H), (lo, VKI_CUT_H), (0.0, VKI_CUT_H)]
        geo.append(("prism", pts, -t2, t2))
        meta.update(vki_rake_low="xL" if side == "R" else "x0")
    elif kind in ("Door", "Exit", "ExitWide"):
        a, b = (0.33, 1.17) if n == 1 else (0.60, 2.40)
        body(0.0, a, -0.30, top - 0.10); cap(0.0, a, top)
        body(b, L, -0.30, top - 0.10); cap(b, L, top)
        body(a, b, -0.30, -0.10)
        geo.append((a, -chw, 0.0, b, chw, 0.03))                            # threshold
        if height == "Full":
            lt = 2.38 if n == 1 else (2.55 if fam == "Stone" else 3.44)
            body(a, b, lt, top - 0.10); cap(a, b, top)
        tr = [0.75, -0.65, 1.0, 0.9, 0.8, 2.0] if n == 1 else [1.5, -0.65, 1.0, 1.9, 0.8, 2.0]
        meta.update(vki_nav="door", vki_nav_open=[a, b], vki_trigger=tr, vki_spawn_local=[L / 2, -1.60],
                    vki_prompt_local=[L / 2, -0.30, 1.40], vki_leaf_open_deg=90,
                    vki_leaf_socket=[a, -t2 + 0.05, 0.0] if n == 1 else [[a, -t2 + 0.05, 0.0], [b, -t2 + 0.05, 0.0]],
                    vki_opening={"x0": a, "x1": b, "z0": 0.0, "z1": 2.20 if height == "Full" else 1.0},
                    vki_collider=[[a / 2, 0.0, 1.1, a, T, 2.2], [(b + L) / 2, 0.0, 1.1, L - b, T, 2.2]])
    elif kind in ("Window", "Lancet", "LancetTall") and height == "Full":
        zt = {"Window": 2.25, "Lancet": 3.65, "LancetTall": 3.95}[kind]
        body(0.0, 0.33, -0.30, top - 0.10); body(1.17, L, -0.30, top - 0.10)
        body(0.33, 1.17, -0.30, 1.00); body(0.33, 1.17, zt, top - 0.10); cap(0.0, L, top)   # open: the spot passes
        meta.update(vki_opening={"x0": 0.33, "x1": 1.17, "z0": 1.0, "z1": zt},
                    vki_lights=[dict(VKI_PH_LANCET_SPOT if kind != "Window" else VKI_PH_WIN_SPOT)])
    elif kind == "Special":
        body(0.0, L, -0.30, top - 0.10); cap(0.0, L, top)
        if special == "Forge_300":
            geo.append((0.40, -1.45, 0.0, 2.60, -t2, 0.85))
            if height == "Full":
                geo.append((0.55, -1.20, 1.60, 2.45, -t2, top))
            meta.update(vki_lights=[vki_ph_lt("forge", (1.5, -0.85, 1.3), 600.0, (1.0, .45, .15), 7.0, 0.3),
                                    vki_ph_lt("forge_bed", (1.5, -0.85, 0.95), 150.0, (1.0, .45, .15), 3.0, 0.2)],
                        vki_fx=[dict(fx="fire_forge", pos=[1.5, -0.85, 0.9])],
                        vki_collider=[[1.5, 0.0, 1.1, 3.0, T, 2.2], [1.5, (-1.45 - t2) / 2, 0.6, 2.2, 1.45 - t2, 1.2]])
        else:
            bx0, bx1, fy = (0.35, 2.65, -1.00) if special == "Hearth_300" else (0.40, 2.60, -0.85)
            geo.append((bx0, fy, 0.0, bx1, -t2, top if height == "Full" else VKI_CUT_H))
            geo.append((bx0, -1.45, 0.0, bx1, fy, 0.03))
            meta.update(vki_lights=[vki_ph_lt("hearth", (1.5, fy + 0.3, 0.6), 400.0, rng=7.0, radius=0.4)],
                        vki_fx=[dict(fx="fire_large" if special == "Hearth_300" else "fire_small", pos=[1.5, -0.5, 0.2])],
                        vki_collider=[[1.5, 0.0, 1.1, 3.0, T, 2.2], [1.5, (fy - t2) / 2, 1.1, bx1 - bx0, -t2 - fy, 2.2]])
        meta.update(vki_special=1)
    else:
        body(0.0, L, -0.30, top - 0.10); cap(0.0, L, top)
        if kind in ("Window", "Lancet"):
            meta.update(vki_opening={"x0": 0.33, "x1": 1.17, "z0": 1.0, "z1": 2.25, "cut": 1},
                        vki_light_pool=[0.75, -1.20, 0.0])
    return geo, meta


def vki_ph_spec(piece):
    """(geometry, metadata, material kind) of a missing master, from its name (§3 / §5 sizes)"""
    short = vki_ph_short(piece)
    m = re.match(r"^Wall_([A-Za-z]+)_(.+)$", short)
    if m:
        fam, rest = m.group(1), m.group(2)
        kind = rest.split("_")[0]
        if kind == "Rake":
            return vki_ph_wall_spec(fam, "Rake", 1, "Rake", side=rest.split("_")[-1]) + ("struct",)
        height = rest.split("_")[-1]
        n = 2 if "_300" in rest else 1
        if kind in ("Fireplace", "Hearth", "Forge"):
            return vki_ph_wall_spec(fam, "Special", 2, height, special=kind + "_300") + ("struct",)
        kind = {"DoorWide": "ExitWide"}.get(kind, kind)
        return vki_ph_wall_spec(fam, kind, n, height) + ("struct",)
    m = re.match(r"^Post_([A-Za-z]+)_(Corner|Mid)_(Full|Cut)$", short)
    if m:
        fam, kind, height = m.groups()
        cls = VKI_FAMILIES[fam]["cls"]
        hx, hy = (VKI_POST_HW[cls], VKI_POST_HW[cls]) if kind == "Corner" else VKI_MID_HW[cls]
        top = (VKI_H_FULL[fam] if height == "Full" else VKI_CUT_H) + VKI_POST_TOP
        meta = dict(vki_class="post", vki_family=fam, vki_kind=kind, vki_height=height, vki_thick=VKI_T[cls],
                    vki_collider=[[0.0, 0.0, 1.1, 2 * hx, 2 * hy, 2.2]], vki_nav="block", vki_origin="node_centre",
                    vki_post_rule={"role": kind.lower(), "height": height, "placeholder": 1})
        return [(-hx, -hy, VKI_POST_Z0, hx, hy, top)], meta, "struct"
    if short.startswith("Stair_Up"):
        geo = [("wedge", 0.33, 1.33, 0.0, 3.62, 3.0), (0.33, 3.62, 2.80, 1.50, 4.215, 3.00)]
        meta = dict(vki_class="link", vki_kind="Stair", vki_link_kind="stair_up", vki_nav="block",
                    vki_trigger=[0.80, 0.30, 1.0, 0.94, 0.55, 2.0], vki_spawn_local=[0.75, -0.75], vki_spawn_facing=180,
                    vki_collider=[[0.83, 2.4075, 1.5, 1.0, 3.615, 3.0]], vki_origin="min_corner")
        return geo, meta, "struct"
    if short.startswith("Stair_Down"):
        geo = [(0.28, 0.0, -0.10, 0.33, 4.215, 0.0), (1.27, 0.0, -0.10, 1.50, 4.215, 0.0),
               (0.33, 0.0, -0.10, 1.27, 0.10, 0.0), (0.33, 3.62, -0.10, 1.50, 4.215, 0.0),
               ("wedge_down", 0.33, 1.27, 0.10, 3.62, 2.0), (1.27, 0.10, 0.90, 1.33, 3.0, 0.98),
               (0.28, 0.0, 0.90, 1.33, 0.06, 0.98)]
        meta = dict(vki_class="link", vki_kind="Stair", vki_link_kind="stair_down", vki_nav="block",
                    vki_trigger=[1.485, 3.555, 1.0, 0.43, 1.31, 2.0], vki_spawn_local=[2.25, 3.75], vki_spawn_facing=90,
                    vki_collider=[[0.805, 1.81, 0.5, 1.05, 3.62, 1.0]], vki_covers_floor=[0.0, 0.0, 1.5, 4.5],
                    vki_origin="min_corner")
        return geo, meta, "struct"
    if short == "Floor_Dais_300":
        meta = dict(vki_class="floor", vki_kind="Dais", vki_len=3.0, vki_nav="walk", vki_top_z=0.20,
                    vki_origin="min_corner", vki_rot_lock="world0", vki_uv_lock="world")
        return [(0.0, 0.0, -0.10, 3.0, 3.0, 0.20)], meta, "struct"
    if short.startswith("Leaf_Wide"):
        sgn = -1.0 if short.endswith("_R") else 1.0
        w_ = 0.795 if "160" in short else 0.89
        x0, x1 = sorted((sgn * 0.005, sgn * (0.005 + w_)))
        meta = dict(vki_class="leaf", vki_kind="Leaf", hinge_axis="local Z", vki_leaf_state="closed",
                    vki_leaf_open_deg=90, vki_leaf_width=w_, vki_nav="block", vki_origin="hinge")
        return [(x0, 0.004, 0.035, x1, 0.084, 0.985)], meta, "struct"
    base = short[5:] if short.startswith("Prop_") else short
    sp = VKI_PH_PROPS.get(base)
    if sp is None:
        sp = (1.0, 1.0, 1.0, "floor", "furniture", {})
    W, Dp, H, mount, tier, ex = sp
    x0 = ex.get("x0", -W / 2); y0 = ex.get("y0", -Dp / 2); z0 = ex.get("z0", 0.0)
    geo = [("cyl", x0 + W / 2, y0 + Dp / 2, W / 2, z0, z0 + H)] if ex.get("round") else [(x0, y0, z0, x0 + W, y0 + Dp, z0 + H)]
    cls = ex.get("cls", "prop")
    meta = dict(vki_class=cls, vki_kind=base, vki_mount=mount, vki_tier=tier, vki_origin="footprint_centre",
                vki_nav="none" if cls == "overlay" else "block", vki_uv_lock="local",
                vki_collider=[[round(x0 + W / 2, 4), round(y0 + Dp / 2, 4), round(z0 + H / 2, 4), W, Dp, H]])
    if mount in ("wall_floor", "wall_hung"):
        meta["vki_back_y"] = round(y0 + Dp, 4)
    if mount == "wall_hung":
        meta.update(vki_mount_zmin=z0, vki_mount_zmax=z0 + H)
    if ex.get("use") == "front":
        meta["vki_use"] = [[round(x0 + W / 2, 3), round(y0 - 0.45, 3), 0]]
    for k_ in ("lights", "fx"):
        if ex.get(k_):
            meta["vki_" + k_] = ex[k_]
    if ex.get("edge"):
        meta["vki_edge_piece"] = 1
    return geo, meta, "prop"


def vki_ph_mesh(name, geo):
    bm = bmesh.new()

    def quad_box(x0, y0, z0, x1, y1, z1):
        r = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)) @
                            Matrix.Diagonal((max(x1 - x0, 1e-3), max(y1 - y0, 1e-3), max(z1 - z0, 1e-3), 1.0)),
                            verts=r["verts"])
    for g_ in geo:
        if g_[0] == "prism":
            _, pts, ya, yb = g_
            vs0 = [bm.verts.new((x, ya, z)) for x, z in pts]
            vs1 = [bm.verts.new((x, yb, z)) for x, z in pts]
            bm.faces.new(vs0[::-1]); bm.faces.new(vs1)
            for i in range(len(pts)):
                j = (i + 1) % len(pts)
                bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))
        elif g_[0] in ("wedge", "wedge_down"):
            _, xa, xb, ya, yb, h = g_
            if g_[0] == "wedge":        # rises +Y from z 0 at ya to h at yb
                pts = [(ya, 0.0), (yb, 0.0), (yb, h)]
            else:                        # a dark hole: descends from z -0.2 at yb to -h at ya
                pts = [(ya, -h), (yb, -0.20), (yb, -h - 0.4), (ya, -h - 0.4)]
            vs0 = [bm.verts.new((xa, y, z)) for y, z in pts]
            vs1 = [bm.verts.new((xb, y, z)) for y, z in pts]
            bm.faces.new(vs0); bm.faces.new(vs1[::-1])
            for i in range(len(pts)):
                j = (i + 1) % len(pts)
                bm.faces.new((vs0[j], vs0[i], vs1[i], vs1[j]))
        elif g_[0] == "cyl":
            _, cx, cy, r_, za, zb = g_
            res = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=r_, radius2=r_, depth=zb - za)
            bmesh.ops.translate(bm, vec=(cx, cy, (za + zb) / 2), verts=res["verts"])
        else:
            quad_box(*g_)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    return me


def vki_ph_master(piece):
    """the hidden placeholder master PHM_<short> for a missing piece (rebuilt when VKI_ROOMS_VERSION changes)"""
    short = vki_ph_short(piece)
    mn = "PHM_" + short
    o = bpy.data.objects.get(mn)
    if o is not None and o.get("vki_ph_version") == VKI_ROOMS_VERSION:
        return o
    geo, meta, mk = vki_ph_spec(piece)
    me = vki_ph_mesh(mn, geo)
    me.materials.clear()
    me.materials.append(vki_ph_mat(mk))
    if o is None:
        o = bpy.data.objects.new(mn, me)
    else:
        o.data = me
    c = bpy.data.collections.get(VKI_ROOMS_PH_COLL)
    if c is None:
        c = bpy.data.collections.new(VKI_ROOMS_PH_COLL)
        c.use_fake_user = True
    if o.name not in c.objects:
        c.objects.link(o)
    for k_ in [k_ for k_ in o.keys() if vki_is_meta_key(k_)]:
        del o[k_]
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    full = dict(kit="VillageInterior", grid_m=VKI_IG, vki_piece=piece, vki_placeholder=1, vki_rot_lock="none",
                vki_footprint="%g,%g,%g,%g" % (round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)),
                vki_fp_cells="%d,%d" % (max(1, math.ceil((max(xs) - min(xs)) / VKI_IG - 0.02)),
                                        max(1, math.ceil((max(ys) - min(ys)) / VKI_IG - 0.02))))
    full.update(meta)
    for k_, v_ in full.items():
        o[k_] = vki_prop(v_)
    o["vki_ph_version"] = VKI_ROOMS_VERSION
    return o


def vki_rooms_master(piece):
    """the real master object when it exists in VKI_Pieces / VK_Pieces / any WS_vki_*_Pieces, else None"""
    o = bpy.data.objects.get(piece)
    if o is None or o.type != "MESH":
        return None
    for c in o.users_collection:
        if c.name in VKI_ROOMS_MASTER_COLLS or (c.name.startswith("WS_vki_") and c.name.endswith("_Pieces")):
            return o
    return None


def vki_rooms_resolve(short):
    """short prop name -> (piece name, master object or None)"""
    if short.startswith("SM_"):
        cands = [short]
    elif short.startswith("Prop_"):
        cands = ["SM_VK_" + short, "SM_VKI_" + short]
    else:
        cands = ["SM_VKI_Prop_" + short, "SM_VKI_" + short]
    for c in cands:
        o = vki_rooms_master(c)
        if o is not None:
            return c, o
    base = short[5:] if short.startswith("Prop_") else short
    if base in VKI_PH_PROPS and VKI_PH_PROPS[base][5].get("cls") == "overlay":
        return "SM_VKI_" + base, None
    return (cands[0] if short.startswith(("SM_", "Prop_")) else "SM_VKI_Prop_" + short), None


# ---------------------------------------------------------------- placement helpers
def vki_rooms_tag(name):
    return name[4:] if name.startswith("VKI_") else name


def vki_rooms_colls(sc, name):
    """VKI_<S>_Shell / _Props / _Logic / _Lights under the scene (explicit collections, §6 Blender layout)"""
    tag = vki_rooms_tag(name)
    out = {}
    for suf in ("Shell", "Props", "Logic", "Lights"):
        n = f"VKI_{tag}_{suf}"
        c = bpy.data.collections.get(n) or bpy.data.collections.new(n)
        if c.name not in sc.collection.children:
            sc.collection.children.link(c)
        out[suf] = c
    return out


def vki_rooms_clear(colls):
    for c in colls.values():
        for o in list(c.objects):
            d = o.data
            bpy.data.objects.remove(o)
            if isinstance(d, bpy.types.Light) and d.users == 0:
                bpy.data.lights.remove(d)
            elif isinstance(d, bpy.types.Camera) and d.users == 0:
                bpy.data.cameras.remove(d)


def vki_rooms_uses(src, slots, cache):
    """does the master mesh use any of the material slots (e.g. WINDOW / STAINED for the Night style)?"""
    k_ = (src.name, tuple(slots))
    if k_ not in cache:
        cache[k_] = any(p.material_index in slots for p in src.data.polygons)
    return cache[k_]


def vki_rooms_put(ctx, coll, piece, x, y, rot=0, z=0.0, style=None, mount=None, hug=None, name=None, walls=None,
                  **props):
    """place the real master (VKI_Pieces / VK_Pieces / WS_vki_*_Pieces) or its placeholder PH_<piece>"""
    src = vki_rooms_master(piece)
    ph = src is None
    reuse = piece.startswith("SM_VK_") and not piece.startswith("SM_VKI_")
    st = {}
    if ph:
        src = vki_ph_master(piece)
    else:
        st = dict(style or {})
        if ctx["night"]:
            if reuse:
                st.setdefault("window", "Window_Night")
            elif vki_rooms_uses(src, (WINDOW, STAINED), ctx["slot_cache"]):
                for k_, v_ in VKI_NIGHT_STYLE.items():
                    st.setdefault(k_, v_)
    short = vki_ph_short(piece)
    nm = name or (("PH_" + short) if ph else f"{ctx['tag']}_{short}")
    o = vki_place(coll, src.name, x, y, rot, z=z, style=st or None, mount=mount, walls=walls, hug=hug, name=nm, **props)
    if ph:
        o["vki_piece"] = piece
        o["vki_placeholder"] = 1
        ctx["ph"][piece] = ctx["ph"].get(piece, 0) + 1
    return o


def vki_rooms_obj_box(o, shrink=0.0):
    """world AABB ((x0, y0, z0), (x1, y1, z1)) from the object's bound box"""
    mw = vki_mw(o)
    pts = [mw @ Vector(c) for c in o.bound_box]
    return (tuple(min(p[i] for p in pts) + shrink for i in range(3)), tuple(max(p[i] for p in pts) - shrink for i in range(3)))


def vki_rooms_box_hit(a, b, eps=0.0):
    return all(a[0][i] < b[1][i] - eps and b[0][i] < a[1][i] - eps for i in range(3))


def vki_rooms_wall_env(o):
    """world envelope box of a wall instance: its run x 0..L, |y| <= CAP_HW (+5 mm), z -0.30..H (walls only)"""
    L = float(o.get("vki_len") or 1.5)
    cls = "P" if float(o.get("vki_thick", 0.5)) < 0.4 else "O"
    chw = VKI_CAP_HW[cls]
    fam = o.get("vki_family")
    ht = o.get("vki_height", "Full")
    H = VKI_CUT_H if ht == "Cut" else VKI_H_FULL.get(fam, 3.0)
    mw = vki_mw(o)
    pts = [mw @ Vector((xx, yy, 0.0)) for xx in (0.0, L) for yy in (-chw, chw)]
    return ((min(p.x for p in pts), min(p.y for p in pts), -0.30), (max(p.x for p in pts), max(p.y for p in pts), H))


def vki_rooms_collider_boxes(o, band=None):
    """world AABBs of an object's vki_collider boxes (rotations are multiples of 90); falls back to the bound box.
    band=(z0, z1) keeps only boxes overlapping that height range."""
    mw = vki_mw(o)
    cols = vki_get(o, "vki_collider", None)
    out = []
    if not cols:
        bb = vki_rooms_obj_box(o)
        out = [bb]
    else:
        R3 = mw.to_3x3()
        for c in cols:
            ctr = mw @ Vector(c[:3])
            hx = abs((R3 @ Vector((c[3], 0, 0))).x) / 2 + abs((R3 @ Vector((0, c[4], 0))).x) / 2
            hy = abs((R3 @ Vector((c[3], 0, 0))).y) / 2 + abs((R3 @ Vector((0, c[4], 0))).y) / 2
            out.append(((ctr.x - hx, ctr.y - hy, ctr.z - c[5] / 2), (ctr.x + hx, ctr.y + hy, ctr.z + c[5] / 2)))
    if band:
        out = [bx for bx in out if bx[0][2] < band[1] and bx[1][2] > band[0]]
    return out


def vki_rooms_pull(o, src, rot, pull, objs):
    """hug fallback (§5 hug + §10.3): stand a wall_floor prop `pull` m off its proud line so the back-wall post
    squares (which reach 0.31 / 0.21 past the wall line, beyond the 0.285 / 0.185 proud line) no longer bind, then
    slide along the wall (<= 0.30) off the side walls' proud lines and any post square in its depth strip.
    Records vki_pull, vki_hug / vki_hug_limit or vki_hug_fail. Returns True when placed."""
    r = math.radians(rot)
    a = Vector((math.cos(r), math.sin(r))); b = Vector((-math.sin(r), math.cos(r)))
    bx = vki_local_box(src)
    reuse = src.name.startswith("SM_VK_") and not src.name.startswith("SM_VKI_")
    at = Vector(vki_get(o, "vki_at"))
    pa = at.dot(a)
    back_l = float(src["vki_back_y"]) if "vki_back_y" in src else bx[4]
    cx = (bx[0] + bx[3]) / 2 if reuse else 0.0
    oa = pa - cx
    ob = Vector(o.location[:2]).dot(b) - pull
    lo, hi = oa + bx[0], oa + bx[3]
    b_lo, b_hi = ob + bx[1], ob + back_l
    need, fail = [], None
    for sg in vki_wall_segments(objs):
        d = sg["p1"] - sg["p0"]
        if d.length < 1e-6 or abs(d.normalized().dot(a)) > 1e-3:
            continue
        sa = sg["p0"].dot(a)
        t0, t1 = sorted((sg["p0"].dot(b), sg["p1"].dot(b)))
        if t1 < b_lo - 1e-4 or t0 > b_hi + 1e-4:
            continue
        pl = VKI_PROUD_LINE[sg["cls"]]
        if sa >= pa and hi > sa - pl:
            need.append(((sa - pl) - hi, sg["name"]))
        elif sa < pa and lo < sa + pl:
            need.append(((sa + pl) - lo, sg["name"]))
    for p_ in objs:
        if p_.get("vki_class") != "post":
            continue
        pm = vki_mw(p_)
        cs = [(pm @ Vector(c_)).to_2d() for c_ in p_.bound_box]
        pa0, pa1 = min(c_.dot(a) for c_ in cs), max(c_.dot(a) for c_ in cs)
        pb0, pb1 = min(c_.dot(b) for c_ in cs), max(c_.dot(b) for c_ in cs)
        if pb1 < b_lo + 1e-6 or pb0 > b_hi - 1e-6 or pa1 < lo - 0.305 or pa0 > hi + 0.305:
            continue
        if pa0 > lo + 1e-6 and pa1 < hi - 1e-6:
            fail = f"{p_.name} inside the prop's span"
        elif (pa0 + pa1) / 2 >= pa and hi > pa0 - 0.005:
            need.append(((pa0 - 0.005) - hi, p_.name))
        elif (pa0 + pa1) / 2 < pa and lo < pa1 + 0.005:
            need.append(((pa1 + 0.005) - lo, p_.name))
    need = [n_ for n_ in need if abs(n_[0]) > 1e-9]
    neg = [n_ for n_ in need if n_[0] < 0]; pos = [n_ for n_ in need if n_[0] > 0]
    slide, lim = 0.0, None
    if neg and pos:
        fail = fail or "walls or posts on both sides"
    elif neg:
        slide, lim = min(neg)
    elif pos:
        slide, lim = max(pos)
    if abs(slide) > 0.30 + 1e-6:
        fail = fail or "needs %.3f (%s)" % (slide, lim)
    for k_ in ("vki_hug", "vki_hug_limit", "vki_hug_fail"):
        if k_ in o.keys():
            del o[k_]
    o["vki_pull"] = pull
    if fail:
        o["vki_hug_fail"] = fail
        return False
    O = a * (oa + slide) + b * ob
    o.location = (O.x, O.y, o.location.z)
    if slide:
        o["vki_hug"] = round(slide, 4)
        o["vki_hug_limit"] = lim
    bl_ = ob + back_l
    o["vki_back_line"] = json.dumps(["x", round(bl_ * (1 if b.x > 0 else -1), 4)] if abs(b.x) > 0.5 else
                                    ["y", round(bl_ * (1 if b.y > 0 else -1), 4)])
    return True


def vki_rooms_spawn(ctx, sid, x, y, facing, link_obj=None):
    sp = bpy.data.objects.new("SPN_" + sid, None)
    ctx["colls"]["Logic"].objects.link(sp)
    sp.location = (x, y, 0.0)
    sp.empty_display_type = "SINGLE_ARROW"
    sp.empty_display_size = 0.8
    sp.rotation_euler = (-math.pi / 2, 0.0, -math.radians(facing))      # the arrow points along the facing
    sp["vki_spawn_id"] = sid
    sp["vki_facing_deg"] = facing
    if link_obj is not None:
        sp["vki_link_obj"] = link_obj.name
    ctx["spawns"][sid] = sp
    return sp


def vki_rooms_local(pc_or_obj, lx, ly):
    """piece-local (lx, ly) -> world (x, y) for a layout piece dict or an object"""
    if isinstance(pc_or_obj, dict):
        r = math.radians(pc_or_obj["rot"]); x0, y0 = pc_or_obj["x"], pc_or_obj["y"]
        return (x0 + math.cos(r) * lx - math.sin(r) * ly, y0 + math.sin(r) * lx + math.cos(r) * ly)
    p = vki_mw(pc_or_obj) @ Vector((lx, ly, 0.0))
    return (p.x, p.y)


# ---------------------------------------------------------------- scene build
def vki_rooms_wall_style(L, pc):
    """instance style of a wall piece: face A = the zone on the room side, face B = the zone on the other side
    (partitions, when the room plasters them) or the exterior (perimeter); + special / window styles"""
    R = L["R"]
    zones = R["zones"]
    fam_def = VKI_FAMILIES[pc["fam"]]["wall_a"]

    def zs(cells, key="wall"):
        for c in cells:
            zn = L["zmap"].get(c)
            if zn and zones[zn].get(key):
                return zones[zn][key]
        return None
    st = {}
    if pc["role"] == "part":
        if R.get("partition_wall") == "zone":
            st = {"wall_a": zs(pc["face_a"]) or fam_def, "wall_b": zs(pc["face_b"]) or fam_def}
    else:
        st = {"wall_a": zs(pc["face_a"]) or fam_def, "wall_b": R.get("exterior") or fam_def}
    if st and st["wall_a"] == fam_def and st["wall_b"] == fam_def:
        st = {}
    cap = zs(pc["face_a"], "cap")
    if cap:
        st["cap"] = cap
    if pc["kind"] == "Special" and R.get("special_style"):
        st.update(R["special_style"])
    if pc["kind"] == "Window" and pc["height"] == "Full" and R.get("window_style"):
        st.update(R["window_style"])
    return st


def vki_rooms_mount_of(piece, src):
    if src is not None:
        if src.get("vki_mount"):
            return src["vki_mount"]
        return VKI_REUSE.get(piece, {}).get("mount", "floor")
    base = vki_ph_short(piece)
    base = base[5:] if base.startswith("Prop_") else base
    sp = VKI_PH_PROPS.get(base)
    return sp[3] if sp else "floor"


def vki_rooms_exit(ctx, pc, door):
    """exit: Door_150_Cut + closed Leaf_Plank_Cut (wide: DoorWide_300_Cut + Leaf_Wide_Cut_L/R) + Apron_300x150 +
    RushMat inside + link data on the door + SPN_<id> at the door's vki_spawn_local"""
    shell, props = ctx["colls"]["Shell"], ctx["colls"]["Props"]
    R = ctx["R"]
    T = VKI_T[pc["cls"]]
    wide = pc["kind"] == "ExitWide"
    Lp = VKI_IG * pc["n"]
    socks = vki_get(door, "vki_leaf_socket", None)
    if wide:
        if not (isinstance(socks, list) and socks and isinstance(socks[0], list)):
            socks = [[0.60, -T / 2 + 0.05, 0.0], [2.40, -T / 2 + 0.05, 0.0]]
        lv = vki_get(door, "vki_leaf", None)
        if not (isinstance(lv, list) and len(lv) == 2):
            # Stone DoorWide: Leaf_Wide_Cut_L/R (0.90 m); Ashlar DoorWide (clear 0.70-2.30): Leaf_Wide160_Cut_L/R (0.795 m)
            lv = ["SM_VKI_Leaf_Wide160_Cut_L", "SM_VKI_Leaf_Wide160_Cut_R"] if pc["fam"] == "Ashlar" else \
                 ["SM_VKI_Leaf_Wide_Cut_L", "SM_VKI_Leaf_Wide_Cut_R"]
        leaves = list(zip(lv, socks))
    else:
        s = socks if (isinstance(socks, list) and socks and not isinstance(socks[0], list)) else [0.33, -T / 2 + 0.05, 0]
        lv = vki_get(door, "vki_leaf", None)            # dungeon kit: the door names its own leaf (Leaf_Iron_Cut)
        lv = lv if isinstance(lv, str) and lv.endswith("_Cut") and vki_rooms_master(lv) is not None else None
        leaves = [(lv or "SM_VKI_Leaf_Plank_Cut", s)]
    for lp, s in leaves:
        x, y = vki_rooms_local(pc, s[0], s[1])
        lf = vki_rooms_put(ctx, shell, lp, round(x, 4), round(y, 4), pc["rot"], walls=[])
        lf["vki_leaf_state"] = "closed"
        lf["vki_leaf_deg"] = 0.0
        lf["vki_leaf_door"] = door.name
    if wide and vki_rooms_master("SM_VKI_Apron_Wide_300x150") is not None:
        apron, off = "SM_VKI_Apron_Wide_300x150", 0.0        # local x 0..3.0: the DoorWide's own origin
    else:
        apron, off = "SM_VKI_Apron_300x150", (0.75 if wide else 0.0)   # local x -0.75..2.25 (centred when wide)
    ax, ay = vki_rooms_local(pc, off, 0.0)
    vki_rooms_put(ctx, shell, apron, round(ax, 4), round(ay, 4), pc["rot"], style=R.get("apron_style"), walls=[])
    mx, my = vki_rooms_local(pc, Lp / 2, -0.75)
    vki_rooms_put(ctx, props, "SM_VKI_RushMat", round(mx, 4), round(my, 4), 0, walls=[])
    lk = next((l for l in R["links"] if l[1] == "exit"), ("front", "exit", "@return"))
    door["vki_link"] = "exit"
    door["vki_link_id"] = lk[0]
    door["vki_target"] = lk[2]
    door["vki_prompt"] = "Leave"
    door["vki_facing_min"] = 60
    sl = vki_get(door, "vki_spawn_local", None) or [Lp / 2, -1.60]
    sx, sy = vki_rooms_local(pc, sl[0], sl[1])
    vki_rooms_spawn(ctx, lk[0], round(sx, 4), round(sy, 4), (180 - pc["rot"]) % 360, door)
    ctx["links"][lk[0]] = door


def vki_rooms_stair(ctx, kind, x, y, rot, lid, var="RailR"):
    piece = f"SM_VKI_Stair_{kind}_150x450_{var}"                  # var "Stone": the dungeon kit's stone stairs
    o = vki_rooms_put(ctx, ctx["colls"]["Shell"], piece, x, y, rot, walls=[])
    lk = next((l for l in ctx["R"]["links"] if l[0] == lid), None)
    o["vki_link"] = "stair_up" if kind == "Up" else "stair_down"
    o["vki_link_id"] = lid
    o["vki_target"] = lk[2] if lk else ""
    o["vki_prompt"] = "Go upstairs" if kind == "Up" else "Go downstairs"
    o["vki_facing_min"] = 60
    sl = vki_get(o, "vki_spawn_local", None) or ([0.75, -0.75] if kind == "Up" else [2.25, 3.75])
    fac = float(o.get("vki_spawn_facing", 180 if kind == "Up" else 90))
    sx, sy = vki_rooms_local(o, sl[0], sl[1])
    vki_rooms_spawn(ctx, lid, round(sx, 4), round(sy, 4), (fac - rot) % 360, o)
    ctx["links"][lid] = o
    return o


def vki_rooms_pit_cells(R):
    """{(c, r): pit piece} cells covered by R["pits"] entries (piece, x, y[, rot 0]): pits are unrotated (world0) and
    cover their vki_fp_cells from their min corner (x, y); read from the master when it exists, else from the name's
    <w>x<d> token in cm (default one cell)"""
    out = {}
    for pt in R.get("pits", []):
        piece = pt[0] if pt[0].startswith("SM_") else "SM_VKI_" + pt[0]
        x, y = pt[1], pt[2]
        src = bpy.data.objects.get(piece)
        if src is not None and src.get("vki_fp_cells"):
            w, d = (int(a) for a in str(src["vki_fp_cells"]).split(","))
        else:
            p_ = vki_parse_name(piece)
            w = max(1, int(round((p_["len"] or 1.5) / VKI_IG)))
            d = max(1, int(round((p_["depth"] or p_["len"] or 1.5) / VKI_IG)))
        c0, r0 = int(round(x / VKI_IG)), int(round(y / VKI_IG))
        for a in range(w):
            for b in range(d):
                out[(c0 + a, r0 + b)] = piece
    return out


def vki_rooms_pits(ctx):
    """R["pits"]: pit pieces (spike pits, chasms, pools) at their min corners, rotation 0, in _Shell"""
    out = []
    for pt in ctx["R"].get("pits", []):
        piece = pt[0] if pt[0].startswith("SM_") else "SM_VKI_" + pt[0]
        out.append(vki_rooms_put(ctx, ctx["colls"]["Shell"], piece, pt[1], pt[2], 0, walls=[]))
    return out


def vki_rooms_passage(ctx, pc, o):
    """a passage (adventure kit): the wall piece carries the scene link -- R["passages"][(ori, k, line)] = link id,
    whose R["links"] entry gives the target scene -- and the spawn at its vki_spawn_local"""
    R = ctx["R"]
    lid = R.get("passages", {}).get((pc["ori"], pc["k"], pc["line"]))
    lk = next((l for l in R["links"] if l[0] == lid), None)
    if lk is None:
        ctx["notes"].append(f"passage at {pc['ori']} ({pc['k']},{pc['line']}) has no R['passages'] / links entry")
        return None
    o["vki_link"] = "passage"
    o["vki_link_id"] = lid
    o["vki_target"] = lk[2]
    o["vki_prompt"] = o.get("vki_prompt_text", "Go through")
    o["vki_facing_min"] = 60
    sl = vki_get(o, "vki_spawn_local", None) or [0.75, -1.60]
    sx, sy = vki_rooms_local(pc, sl[0], sl[1])
    vki_rooms_spawn(ctx, lid, round(sx, 4), round(sy, 4), (180 - pc["rot"]) % 360, o)
    ctx["links"][lid] = o
    return o


def vki_rooms_door_leaf(ctx, pc, door):
    """R["door_leaves"][(ori, k, line)] = dict(piece, deg=0.0, z=0.0, socket=None): a leaf on an interior door piece
    (a locked iron door, a portcullis let down or half raised, a secret stone door ajar) at the door's
    vki_leaf_socket (or socket), rotation door rot - deg, lifted z. Leaves whose master has vki_openable do not block
    the BFS (they open in the game)."""
    spec = ctx["R"].get("door_leaves", {}).get((pc["ori"], pc["k"], pc["line"]))
    if not spec:
        return None
    piece = spec["piece"] if spec["piece"].startswith("SM_") else "SM_VKI_" + spec["piece"]
    s = spec.get("socket") or vki_get(door, "vki_leaf_socket", None) or [0.33, -0.2, 0.0]
    if s and isinstance(s[0], list):
        s = s[0]
    x, y = vki_rooms_local(pc, s[0], s[1])
    lf = vki_rooms_put(ctx, ctx["colls"]["Shell"], piece, round(x, 4), round(y, 4), pc["rot"] - float(spec.get("deg", 0.0)),
                       z=float(spec.get("z", 0.0)), walls=[])
    lf["vki_leaf_state"] = spec.get("state", "open" if spec.get("deg") or spec.get("z") else "closed")
    lf["vki_leaf_deg"] = float(spec.get("deg", 0.0))
    lf["vki_leaf_door"] = door.name
    return lf


def vki_rooms_gate(ctx, pc, door):
    """barred gate (dungeon kit): the door's vki_leaf (Leaf_BarsGate_Full) at its vki_leaf_socket with the door's
    rotation, opened R["gates"][(ori, k, line)] degrees (default VKI_ROOMS_GATE_DEG) toward face A"""
    lv = vki_get(door, "vki_leaf", None)
    if not isinstance(lv, str):
        return None
    s = vki_get(door, "vki_leaf_socket", None) or [0.33, -0.022, 0.0]
    deg = float(ctx["R"].get("gates", {}).get((pc["ori"], pc["k"], pc["line"]), VKI_ROOMS_GATE_DEG))
    # a negative angle opens the gate toward face B: its frame (local y 0.004..0.040) would then swing through the
    # hinge-side jamb, so the hinge moves one frame thickness (0.045) into the opening
    x, y = vki_rooms_local(pc, s[0] + (0.045 if deg < 0 else 0.0), s[1])
    lf = vki_rooms_put(ctx, ctx["colls"]["Shell"], lv, round(x, 4), round(y, 4), pc["rot"] - deg, walls=[])
    lf["vki_leaf_state"] = "open" if deg else "closed"
    lf["vki_leaf_deg"] = deg
    lf["vki_leaf_door"] = door.name
    return lf


def vki_rooms_props(ctx):
    """the prop list (source of truth) through vki_place: mounts, hug (floor props and wall_hung props hug by
    default, wall_floor always), table dressing on its host, and the pull fallback when a wall_floor hug fails"""
    R, props = ctx["R"], ctx["colls"]["Props"]
    placed = []
    for idx, pr in enumerate(list(R.get("props", [])) + list(ctx["L"].get("auto_props", []))):   # + waterfalls
        short, x, y, rot, style, mount = pr[:6]
        opts = dict(pr[6]) if len(pr) > 6 else {}
        piece, src = vki_rooms_resolve(short)
        edge = mount == "edge"
        m_eff = None if edge else mount
        mnt = m_eff or vki_rooms_mount_of(piece, src)
        z = float(opts.get("z", 0.0))
        host = None
        if opts.get("on"):
            for ho, hm in reversed(placed):
                if hm == "table":
                    continue
                at = vki_get(ho, "vki_at")
                if at and abs(at[0] - x) < 1e-6 and abs(at[1] - y) < 1e-6:
                    host = ho
                    tz = ho.get("vki_table_z")
                    z = z + (float(tz) + ho.location.z if tz is not None else vki_rooms_obj_box(ho)[1][2])
                    break
        hug = opts.get("hug") if "hug" in opts else (None if mnt == "wall_floor" else
                                                     (False if (edge or mnt == "table") else True))
        o = vki_rooms_put(ctx, props, piece, x, y, rot, z=z, style=style, mount=m_eff, hug=hug)
        if host is not None:
            # table dressing / candles stand on the centre of their host's top (the host may have hugged or snapped
            # to its wall); vki_at keeps the lattice point, the shift is recorded like a hug (T11)
            bb = vki_rooms_obj_box(host)
            cx, cy = (bb[0][0] + bb[1][0]) / 2, (bb[0][1] + bb[1][1]) / 2
            dx, dy = round(cx - x, 4), round(cy - y, 4)
            if abs(dx) > 1e-4 or abs(dy) > 1e-4:
                o.location = (o.location.x + dx, o.location.y + dy, o.location.z)
                o["vki_hug"] = json.dumps([dx, dy])
            o["vki_on"] = host.name
        o["vki_prop_index"] = idx
        if opts.get("warn_ok"):
            o["vki_warn_ok"] = opts["warn_ok"]
        if edge:
            o["vki_edge_piece"] = 1
        if o.get("vki_mount") == "wall_floor" and (opts.get("pull") or "vki_hug_fail" in o.keys()):
            srcobj = vki_rooms_master(piece) or vki_ph_master(piece)
            ok = vki_rooms_pull(o, srcobj, rot, float(opts.get("pull") or VKI_ROOMS_PULL), list(ctx["sc"].objects))
            ctx["pulls"].append((o.name, ok, o.get("vki_hug_fail")))
        placed.append((o, o.get("vki_mount", mnt)))
    return placed


def vki_rooms_rhythm(ctx):
    """optional rhythm Mid posts (§2.3) at even nodes, skipped where any prop / overlay / stair would touch the post
    square (+5 mm): wall-backed and wall-hung props and stairs spanning the node, and floor props that stand close;
    edge pieces (vki_edge, the AltarRail) are let into walls and responds by design and do not count"""
    L, shell = ctx["L"], ctx["colls"]["Shell"]
    obst = [(o, vki_rooms_obj_box(o)) for o in ctx["sc"].objects
            if (o.get("vki_class") in ("prop", "overlay") and not o.get("vki_edge")) or
            o.get("vki_link") in ("stair_up", "stair_down")]            # edge pieces are let into posts
    for p in L["posts"]:
        if p["req"]:
            continue
        cls = VKI_FAMILIES[p["fam"]]["cls"]
        hx, hy = VKI_MID_HW[cls]
        if p["rot"] == 90:
            hx, hy = hy, hx
        top = (VKI_H_FULL[p["fam"]] if p["height"] == "Full" else VKI_CUT_H) + VKI_POST_TOP
        box = ((p["x"] - hx - 0.005, p["y"] - hy - 0.005, VKI_POST_Z0), (p["x"] + hx + 0.005, p["y"] + hy + 0.005, top))
        hit = [o.name for o, bb in obst if vki_rooms_box_hit(box, bb)]
        if hit:
            ctx["skipped"].append((p["node"], hit[0]))
            continue
        vki_rooms_put(ctx, shell, p["piece"], p["x"], p["y"], p["rot"], walls=[])


def vki_rooms_obstacles(sc, kinds=("wall", "post", "prop", "overlay", "link", "leaf")):
    out = []
    for o in sc.objects:
        c = o.get("vki_class")
        if c not in kinds:
            continue
        out.append(vki_rooms_wall_env(o) if c == "wall" else vki_rooms_obj_box(o))
    return out


def vki_rooms_mats(ctx):
    """every N-S Cut doorway gets a RushMat on each side, never across the threshold (§10.7); shifted along the
    doorway by 0.75 when a wall, post, prop or overlay is in the way, skipped when no spot is free"""
    L, props = ctx["L"], ctx["colls"]["Props"]
    if ctx["R"].get("rush_mats") is False:            # e.g. the sewers
        return
    for pc in L["pieces"]:
        if pc["kind"] != "Door" or pc["ori"] != "NS":
            continue
        obst = vki_rooms_obstacles(ctx["sc"])
        x0 = pc["x"]
        yc = pc["y"] + (0.75 if pc["rot"] == 90 else -0.75)
        for sx in (-0.75, 0.75):
            done = False
            for dy in (0.0, 0.75, -0.75):
                cx, cy = x0 + sx, yc + dy
                rect = ((cx - 0.40, cy - 0.60, 0.0), (cx + 0.40, cy + 0.60, 0.03))
                if cx - 0.4 < 0 or cx + 0.4 > L["W"] or cy - 0.6 < 0 or cy + 0.6 > L["D"]:
                    continue
                if any(vki_rooms_box_hit(rect, bb) for bb in obst):
                    continue
                vki_rooms_put(ctx, props, "SM_VKI_RushMat", cx, cy, 90, walls=[])
                obst.append(rect)
                done = True
                break
            if not done:
                ctx["notes"].append(f"doorway mat at x {x0 + sx:.2f}, y {yc:.2f} skipped (no free spot; a rug or "
                                    f"prop covers that side)")


def vki_rooms_pools(ctx):
    """FX_WindowPool (PKG-L) under every Full window / lancet, with the window's origin and rotation, in Day scenes
    only (vki_fx_presets); z 0.20 where the pool lands on a dais. Only when the real master exists."""
    if ctx["night"] or not ctx["R"].get("pools", True) or vki_rooms_master("SM_VKI_FX_WindowPool") is None:
        return 0                                         # R["pools"] False: the dungeon's grates (their own shafts)
    L, props = ctx["L"], ctx["colls"]["Props"]
    dais = [(dx, dy) for (dx, dy) in ctx["R"].get("dais", [])]
    n = 0
    for pc in L["pieces"]:
        if pc["kind"] not in ("Window", "Lancet", "LancetTall") or pc["height"] != "Full":
            continue
        cx, cy = vki_rooms_local(pc, 0.75, -1.15)
        z = 0.20 if any(dx <= cx <= dx + 3.0 and dy <= cy <= dy + 3.0 for dx, dy in dais) else 0.0
        vki_rooms_put(ctx, props, "SM_VKI_FX_WindowPool", pc["x"], pc["y"], pc["rot"], z=z, walls=[])
        n += 1
    return n


def vki_rooms_root(ctx):
    """VKI_Root (Unity metadata), the scene's fit camera (§1 + 0.4 m far margin) and scene properties"""
    L, R, sc = ctx["L"], ctx["R"], ctx["sc"]
    fam = R["family"]["perimeter"]
    fit = vki_fit_camera((0.0, 0.0, L["W"], L["D"]), fam)
    D, tgt = fit["D"], list(fit["target"])
    logic = ctx["colls"]["Logic"]
    rt = bpy.data.objects.new("VKI_Root", None)
    logic.objects.link(rt)
    rt.empty_display_type = "CUBE"
    rt.empty_display_size = 0.25
    links = []
    for (lid, kind, target) in R["links"]:
        lo = ctx["links"].get(lid)
        links.append(dict(id=lid, kind=kind, target=target, obj=lo.name if lo else None,
                          spawn=ctx["spawns"][lid].name if lid in ctx["spawns"] else None))
    default = "front" if any(l[0] == "front" for l in R["links"]) else (R["links"][0][0] if R["links"] else None)
    bounds = [0.0, 0.0, L["W"], L["D"]]
    for k_, v_ in dict(vki_building=R["building"], vki_floor=R["floor"], vki_cam_mode=fit["mode"], vki_cam_dist=D,
                       vki_cam_target=json.dumps(tgt), vki_cam_pitch=50, vki_cam_yaw=0, vki_bounds=json.dumps(bounds),
                       vki_default_spawn=default, vki_preset=R["preset"], vki_links=json.dumps(links),
                       vki_scene=ctx["name"], vki_family=fam, vki_cam_h_fit=fit["h_fit"], vki_cam_margin=fit["margin"],
                       vki_rooms_version=VKI_ROOMS_VERSION).items():
        rt[k_] = v_
    sc["vki_cam_dist"] = D
    sc["vki_cam_target"] = json.dumps(tgt)
    sc["vki_room_bounds"] = json.dumps(bounds)
    sc["vki_family"] = fam
    sc["vki_bounds"] = json.dumps([-0.9, -1.9, L["W"] + 0.9, L["D"] + 0.9])
    sc["vki_preset"] = R["preset"]
    sc["vki_root"] = rt.name
    cd = bpy.data.cameras.new("VKI_Cam_" + ctx["tag"])
    cam = bpy.data.objects.new("VKI_Cam_" + ctx["tag"], cd)
    logic.objects.link(cam)
    cd.lens = VKI_CAM["lens"]; cd.sensor_width = VKI_CAM["sensor"]; cd.sensor_fit = "AUTO"
    cd.clip_start, cd.clip_end = VKI_CAM["clip"]
    p = math.radians(VKI_CAM["pitch"])
    cam.location = Vector(tgt) + Vector((0.0, -math.cos(p) * D, math.sin(p) * D))
    cam.rotation_euler = (math.radians(90 - VKI_CAM["pitch"]), 0.0, 0.0)
    sc.camera = cam
    ctx["root"] = rt
    return rt


def vki_rooms_lights(ctx):
    """LGT_* empties (Unity data, _Logic) + the matching Blender lights (_Lights) from every placed piece's
    vki_lights sockets, at the scene preset's power (window spots 1000 W Day / 150 W Night, §10.5); FXA_* empties
    from vki_fx sockets"""
    night, tag = ctx["night"], ctx["tag"]
    logic, lights = ctx["colls"]["Logic"], ctx["colls"]["Lights"]
    n = nf = 0
    for o in list(ctx["colls"]["Shell"].objects) + list(ctx["colls"]["Props"].objects):
        mw = vki_mw(o)
        for Ls in vki_get(o, "vki_lights", None) or []:
            typ = Ls.get("type", "POINT")
            wd = float(Ls.get("w_day", Ls.get("w", 100.0)))
            wn = float(Ls.get("w_night", Ls.get("w", 100.0)))
            cdy = list(Ls.get("color_day", Ls.get("color", [1.0, 1.0, 1.0])))
            cnt = list(Ls.get("color_night", Ls.get("color", [1.0, 1.0, 1.0])))
            w, col = (wn, cnt) if night else (wd, cdy)
            pos = mw @ Vector(Ls["pos"])
            rot_e = None
            if "aim" in Ls:
                d = (mw @ Vector(Ls["aim"])) - pos
                rot_e = d.to_track_quat("-Z", "Y").to_euler()
            nm = f"{tag}_{n:02d}_{Ls.get('role') or typ.lower()}"
            emp = bpy.data.objects.new("LGT_" + nm, None)
            logic.objects.link(emp)
            emp.location = pos
            emp.empty_display_type = "SINGLE_ARROW" if rot_e is not None else "PLAIN_AXES"
            emp.empty_display_size = 0.3
            if rot_e is not None:
                emp.rotation_euler = rot_e
            data = dict(type=typ, role=Ls.get("role"), color=col, intensity=w, range=Ls.get("range"),
                        flicker=Ls.get("flicker", 0), shadows=Ls.get("shadows", 1), blender_w=w, w_day=wd, w_night=wn,
                        color_day=cdy, color_night=cnt, cone=Ls.get("cone"), blend=Ls.get("blend"),
                        size=Ls.get("size"), radius=Ls.get("radius"), host=o.name, piece=o.get("vki_piece"))
            emp["vki_light"] = json.dumps({k_: v_ for k_, v_ in data.items() if v_ is not None})
            ld = bpy.data.lights.new("LIT_" + nm, typ)
            lo = bpy.data.objects.new("LIT_" + nm, ld)
            lights.objects.link(lo)
            lo.location = pos
            if rot_e is not None:
                lo.rotation_euler = rot_e
            ld.energy = w
            ld.color = col
            ld.use_shadow = bool(Ls.get("shadows", 1))
            if typ == "SPOT":
                ld.spot_size = math.radians(Ls.get("cone", 60.0))
                ld.spot_blend = Ls.get("blend", 0.35)
                ld.shadow_soft_size = Ls.get("radius", 0.25)
            elif typ == "AREA":
                ld.size = Ls.get("size", 1.0)
            else:
                ld.shadow_soft_size = Ls.get("radius", 0.1)
            lo["vki_w_day"] = wd; lo["vki_w_night"] = wn
            lo["vki_color_day"] = json.dumps(cdy); lo["vki_color_night"] = json.dumps(cnt)
            lo["vki_lgt"] = emp.name
            n += 1
        for fx in vki_get(o, "vki_fx", None) or []:
            p = mw @ Vector(fx["pos"])
            e = bpy.data.objects.new(f"FXA_{tag}_{nf:02d}_{fx.get('fx', 'fx')}", None)
            logic.objects.link(e)
            e.location = p
            e.empty_display_type = "SPHERE"
            e.empty_display_size = 0.15
            e["vki_fx"] = json.dumps(dict(fx, host=o.name, piece=o.get("vki_piece")))
            nf += 1
    return n, nf


def vki_rooms_refresh_dg(sc, colls):
    """re-evaluate the depsgraphs that saw the deleted objects: the room scene (vki_check / vki_shot evaluate it) and
    every scene that instances its collections (the coordinator's board). Blender 4.4's DRW_cache_free_old_batches
    walks the depsgraph of EVERY scene on each viewport redraw, and one still holding objects deleted by a rebuild
    crashes Blender (EXCEPTION_ACCESS_VIOLATION in deg_iterator_objects_step, twice on 2026-09-26)."""
    mine = {c.name for c in colls.values()}
    todo = {sc.name: sc}
    for s in bpy.data.scenes:
        for o in s.objects:
            if o.instance_type == "COLLECTION" and o.instance_collection is not None and \
                    o.instance_collection.name in mine:
                todo[s.name] = s
                break
    for s in todo.values():
        for vl in s.view_layers:
            dg = vl.depsgraph                        # None when the scene was never evaluated (nothing stale)
            if dg is not None:
                dg.update()
    return sorted(todo)


def vki_build_scene(name):
    """build VKI_<S> from VKI_PLANS / VKI_ROOMS: walls by family and height (rakes at the side walls' south ends),
    required posts, floors (600 / 300 / Q150 with parity), dais, sills, the special, exits (door + closed leaf +
    apron + rush mat), stairs and links, props (vki_place mounts + hug), rhythm posts, doorway mats, spawns SPN_<id>,
    VKI_Root, fit camera, LGT_ / FXA_ empties and Blender lights, the Day / Night preset. Returns a summary."""
    R = VKI_ROOMS[name]
    L = vki_rooms_layout(name)
    preset = R.get("preset", "Day")
    sc = vki_scene(name, preset=preset)
    colls = vki_rooms_colls(sc, name)
    ctx = dict(name=name, tag=vki_rooms_tag(name), night=preset == "Night", colls=colls, ph={}, slot_cache={},
               spawns={}, links={}, notes=list(L["problems"]), L=L, R=R, sc=sc, skipped=[], pulls=[])
    try:
        vki_rooms_clear(colls)
        shell = colls["Shell"]
        for pc in L["pieces"]:
            o = vki_rooms_put(ctx, shell, pc["piece"], pc["x"], pc["y"], pc["rot"], style=vki_rooms_wall_style(L, pc),
                              walls=[])
            o["vki_room_role"] = pc["role"]
            pc["obj"] = o.name
            if pc["kind"] in ("Exit", "ExitWide"):
                vki_rooms_exit(ctx, pc, o)
            elif pc["kind"] == "BarsGate":
                vki_rooms_gate(ctx, pc, o)
            elif pc["kind"] == "Passage" or (pc["kind"] == "Named" and
                                              (pc["ori"], pc["k"], pc["line"]) in R.get("passages", {})):
                vki_rooms_passage(ctx, pc, o)          # a named piece may be a link too (the sewer's ladder)
            if (pc["ori"], pc["k"], pc["line"]) in R.get("door_leaves", {}):
                vki_rooms_door_leaf(ctx, pc, o)
        for gt in L.get("grounds", []):                 # cave levels: the chasm's / channels' dual-grid ground tiles
            o = vki_rooms_put(ctx, shell, gt["piece"], gt["x"], gt["y"], gt.get("rot", 0), style=gt.get("style"),
                              walls=[])
            if gt.get("flow"):                          # water tiles: the flow direction, for Unity's water shaders
                o["vki_flow"] = json.dumps(gt["flow"])
            o["vki_node"] = json.dumps(list(gt["node"]))
        for rk in L.get("rocks", []):                   # cave levels: the dual-grid rock tiles
            o = vki_rooms_put(ctx, shell, rk["piece"], rk["x"], rk["y"], rk["rot"], walls=[])
            o["vki_room_role"] = "rock"
            o["vki_node"] = json.dumps(list(rk["node"]))
            if rk.get("tunnel"):
                vki_cave_tunnel(ctx, rk, o)
        for p in L["posts"]:
            if p["req"]:
                vki_rooms_put(ctx, shell, p["piece"], p["x"], p["y"], p["rot"], walls=[])
        for f in L["floors"]:
            st = f["style"] if f["style"].get("floor") != "Boards_NS" else None
            vki_rooms_put(ctx, shell, f["piece"], f["x"], f["y"], 0, style=st, walls=[])
        for (x, y, rot, lift) in R.get("sills", []):
            vki_rooms_put(ctx, shell, "SM_VKI_Floor_Sill_150", x, y, rot, z=lift, walls=[])
        for st_ in R.get("stairs", []):
            vki_rooms_stair(ctx, *st_[:5], var=st_[5] if len(st_) > 5 else "RailR")
        vki_rooms_pits(ctx)
        vki_rooms_props(ctx)
        vki_rooms_rhythm(ctx)
        vki_rooms_mats(ctx)
        vki_rooms_pools(ctx)
        vki_rooms_root(ctx)
        nl, nf = vki_rooms_lights(ctx)
    finally:
        vki_rooms_refresh_dg(sc, colls)            # always: a stale depsgraph crashes the next viewport redraw
    return dict(scene=name, objects=len(sc.objects), placeholders=dict(sorted(ctx["ph"].items())),
                ph_total=sum(ctx["ph"].values()), skipped_rhythm=ctx["skipped"], pulls=ctx["pulls"], lights=nl, fx=nf,
                notes=ctx["notes"], cam=(sc["vki_cam_dist"], sc["vki_cam_target"]))


def vki_build_all(names=None):
    """vki_build_scene for every §6 scene (or `names`); each build is 2-6 s, so MCP callers build a few per call"""
    return [vki_build_scene(n) for n in (names or VKI_ROOMS_SCENES)]


# ---------------------------------------------------------------- vki_check: §9 T12 room rules + T19
def vki_rooms_bvh(o, cache):
    from mathutils.bvhtree import BVHTree
    if o.name not in cache:
        mw = vki_mw(o)
        me = o.data
        cache[o.name] = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    return cache[o.name]


def vki_rooms_touch(a, b, cache):
    """True when the two objects' meshes intersect (BVH triangle overlap)"""
    return bool(vki_rooms_bvh(a, cache).overlap(vki_rooms_bvh(b, cache)))


def vki_rooms_rect_dist(a, b):
    """XY distance between two boxes ((x0, y0, ..), (x1, y1, ..)); 0 when they overlap"""
    dx = max(a[0][0] - b[1][0], 0.0, b[0][0] - a[1][0])
    dy = max(a[0][1] - b[1][1], 0.0, b[0][1] - a[1][1])
    return math.hypot(dx, dy)


def vki_rooms_boxes_of(o, boxes):
    """world AABBs of local boxes [cx, cy, cz, sx, sy, sz] of an object"""
    mw = vki_mw(o)
    R3 = mw.to_3x3()
    out = []
    for c in boxes:
        ctr = mw @ Vector(c[:3])
        hx = abs((R3 @ Vector((c[3], 0, 0))).x) / 2 + abs((R3 @ Vector((0, c[4], 0))).x) / 2
        hy = abs((R3 @ Vector((c[3], 0, 0))).y) / 2 + abs((R3 @ Vector((0, c[4], 0))).y) / 2
        out.append(((ctr.x - hx, ctr.y - hy, ctr.z - c[5] / 2), (ctr.x + hx, ctr.y + hy, ctr.z + c[5] / 2)))
    return out


def vki_rooms_bfs_run(boxes, W, D, st, rr, spawns, targets, decks=()):
    """one BFS pass on a raster of step st: {spawn name: (blocked, set of reached target labels)}, reached points.
    A box with a fifth field is soft (the chasm's ground tiles): a capsule centred on a bridge deck (decks, world
    rects x0 y0 x1 y1) ignores it"""
    def clear(x, y):
        ondeck = any(d[0] <= x <= d[2] and d[1] <= y <= d[3] for d in decks)
        for b_ in boxes:
            if ondeck and len(b_) > 4:
                continue
            x0, y0, x1, y1 = b_[:4]
            if x0 - rr < x < x1 + rr and y0 - rr < y < y1 + rr:
                dx = max(x0 - x, 0.0, x - x1); dy = max(y0 - y, 0.0, y - y1)
                if dx * dx + dy * dy < rr * rr - 1e-9:
                    return False
        return True
    nx, ny = int(round(W / st)), int(round(D / st))
    free = {(i, j) for i in range(1, nx) for j in range(1, ny) if clear(i * st, j * st)}
    mid_ok = {}
    out, reach_all = {}, set()
    for sp_name, (sx, sy) in spawns:
        s0 = (int(round(sx / st)), int(round(sy / st)))
        if s0 not in free:
            out[sp_name] = (True, set())
            continue
        seen = {s0}
        todo = [s0]
        while todo:
            i, j = todo.pop()
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    n_ = (i + di, j + dj)
                    if n_ in seen or n_ not in free:
                        continue
                    if di and dj:                        # diagonal: the capsule must also clear the midpoint
                        mk = (2 * i + di, 2 * j + dj)
                        if mk not in mid_ok:
                            mid_ok[mk] = clear(mk[0] * st / 2, mk[1] * st / 2)
                        if not mid_ok[mk]:
                            continue
                    seen.add(n_)
                    todo.append(n_)
        reach_all |= {(i * st, j * st) for (i, j) in seen}
        got = set()
        for kind, lab, pt, box in targets:
            ok = False
            if kind == "use":
                # a free capsule centre within 0.30 of the use point, one clear straight step from a reached node
                for rad in (0.0, 0.1, 0.2, 0.3):
                    for k_ in range(1 if rad == 0 else 16):
                        ang = 2 * math.pi * k_ / 16
                        q = (pt[0] + rad * math.cos(ang), pt[1] + rad * math.sin(ang))
                        if not clear(*q):
                            continue
                        qi, qj = int(round(q[0] / st)), int(round(q[1] / st))
                        for a in (-1, 0, 1):
                            for b in (-1, 0, 1):
                                n_ = (qi + a, qj + b)
                                if n_ in seen and math.hypot(n_[0] * st - q[0], n_[1] * st - q[1]) <= 1.5 * st:
                                    if clear((n_[0] * st + q[0]) / 2, (n_[1] * st + q[1]) / 2):
                                        ok = True
                                        break
                            if ok:
                                break
                        if ok:
                            break
                    if ok:
                        break
            else:
                for (i, j) in seen:
                    x, y = i * st, j * st
                    dx = max(box[0][0] - x, 0.0, x - box[1][0]); dy = max(box[0][1] - y, 0.0, y - box[1][1])
                    if dx * dx + dy * dy < rr * rr:
                        ok = True
                        break
            if ok:
                got.add(lab)
        out[sp_name] = (False, got)
    return out, reach_all, len(free)


def vki_rooms_struct_xy(sc):
    """XY boxes of the wall / post colliders (z band 0.05-1.0)"""
    out = []
    for o in sc.objects:
        if o.get("vki_class") in ("wall", "post"):
            for bb in vki_rooms_collider_boxes(o, VKI_ROOMS_BAND):
                out.append((bb[0][0], bb[0][1], bb[1][0], bb[1][1]))
    return out


def vki_rooms_use_possible(x, y, sboxes, L):
    """False for a use point inside a wall / post body or outside the room (the far side of a prop that stands
    against a wall: a bed's wall side, a half-tester's corner by the east wall)"""
    if not (0.0 < x < L["W"] and 0.0 < y < L["D"]):
        return False
    return not any(x0 <= x <= x1 and y0 <= y <= y1 for (x0, y0, x1, y1) in sboxes)


def vki_rooms_bfs(sc, L):
    """§9 T12 BFS: capsule r 0.30 on the 0.25 m raster over the room; colliders (vki_collider, else the bound box) of
    walls, posts, props, leaves and links in the z band 0.05-1.0 (overhead items do not block; the 0.20 dais is a
    step); diagonal moves also clear their midpoint. Every use point (a free capsule centre within 0.30 of it) and
    trigger (a capsule that reaches the trigger box) must be reachable from every spawn. Targets missed on the 0.25
    raster are retried on 0.125 and 0.0625 rasters: found there, they pass with a 'narrow passage' warning (a 0.25
    raster can miss gaps up to 0.85 m wide). Use points inside a wall / post body or outside the room (the far side of a prop
    that stands against a wall, e.g. a bed's wall side) are skipped with a warning. Returns dict(errors, warnings,
    reach, nodes)."""
    rr = VKI_ROOMS_CAPSULE
    boxes, sboxes = [], []
    for o in sc.objects:
        c = o.get("vki_class")
        if c not in ("wall", "post", "prop", "leaf", "link", "pit", "rock", "ground"):
            continue
        if c == "prop" and o.get("vki_mount") == "table":
            continue
        if c == "leaf" and o.get("vki_openable"):
            continue                                     # locked doors, portcullis, secret doors: they open in play
        if o.get("vki_nav") in ("none", "walk") and c != "link":
            continue
        for bb in vki_rooms_collider_boxes(o, VKI_ROOMS_BAND):
            boxes.append((bb[0][0], bb[0][1], bb[1][0], bb[1][1]) + (("soft",) if c == "ground" else ()))
            if c in ("wall", "post"):
                sboxes.append((bb[0][0], bb[0][1], bb[1][0], bb[1][1]))
    targets, warns = [], []
    for o in sc.objects:
        if o.get("vki_class") in ("prop", "wall") or o.get("vki_link"):
            mw = vki_mw(o)
            for k_, u in enumerate(vki_get(o, "vki_use", None) or []):
                p = mw @ Vector((u[0], u[1], 0.0))
                lab = f"{o.name}.use{k_}"
                if not vki_rooms_use_possible(p.x, p.y, sboxes, L):
                    warns.append(f"BFS: {lab} ({p.x:.2f},{p.y:.2f}) lies in a wall / post or outside the room "
                                 f"(the prop stands against it): skipped")
                    continue
                targets.append(("use", lab, (p.x, p.y), None))
        if o.get("vki_link"):
            tr = vki_get(o, "vki_trigger", None)
            if tr:
                targets.append(("trigger", f"{o.name}.trigger", None, vki_rooms_boxes_of(o, [tr])[0]))
    spawns = [(o.name, (o.location.x, o.location.y)) for o in sc.objects if o.get("vki_spawn_id")]
    decks = []
    for o in sc.objects:                                 # rope bridges: their decks cross the chasm
        for d in vki_get(o, "vki_bridge", None) or []:
            bb = vki_rooms_boxes_of(o, [[(d[0] + d[2]) / 2, (d[1] + d[3]) / 2, 0.0, d[2] - d[0], d[3] - d[1], 0.1]])[0]
            decks.append((bb[0][0], bb[0][1], bb[1][0], bb[1][1]))
    res, reach, nodes = vki_rooms_bfs_run(boxes, L["W"], L["D"], VKI_ROOMS_RASTER, rr, spawns, targets, decks)
    errs = []
    miss = {sp: [t_ for t_ in targets if t_[1] not in got] for sp, (blk, got) in res.items() if not blk}
    fine = {}
    left = {sp: list(ts) for sp, ts in miss.items() if ts}
    for step in (VKI_ROOMS_RASTER / 2, VKI_ROOMS_RASTER / 4):
        if not any(left.values()):
            break
        r2, _, _ = vki_rooms_bfs_run(boxes, L["W"], L["D"], step, rr, spawns, [t_ for ts in left.values() for t_ in ts],
                                     decks)
        for sp in list(left):
            got2 = r2.get(sp, (True, set()))[1]
            for t_ in left[sp]:
                if t_[1] in got2:
                    fine[(sp, t_[1])] = step
            left[sp] = [t_ for t_ in left[sp] if t_[1] not in got2]
    for sp, (blk, got) in res.items():
        if blk:
            errs.append(f"T12 BFS: spawn {sp} is blocked")
            continue
        for kind, lab, pt, box in miss.get(sp, []):
            if (sp, lab) in fine:
                warns.append(f"BFS: {lab} reached from {sp} only through a narrow passage ({fine[(sp, lab)]:g} m raster)")
            else:
                errs.append(f"T12 BFS: {lab} not reached from {sp}" +
                            (f" (use point {pt[0]:.2f},{pt[1]:.2f})" if pt else ""))
    return dict(errors=errs, warnings=warns, reach=reach, nodes=nodes)


def vki_rooms_palette(sc, path=None, step=6):
    """palette (§4.3 targets, §9 T12) measured on the scene's fit game shot: the display luma of pixels whose camera
    ray first hits a floor top (FLOOR slot), a wall cap top (CAP slot) or a prop top (n.z > 0.7). Cap mean >= floor
    mean + 0.15; each prop's top median differs from the floor mean by >= 0.12. Returns (stats, warnings)."""
    import numpy
    tag = vki_rooms_tag(sc.name)
    path = path or os.path.join(VKI_RENDERS, sc.name, tag + "_game.png")
    if not os.path.exists(path):
        return None, ["palette: no game shot yet (vki_rooms_shots renders it)"]
    im = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = im.size
        a = numpy.empty(w * h * im.channels, numpy.float32)
        im.pixels.foreach_get(a)
        a = a.reshape(h, w, im.channels)[::-1, :, :3]
    finally:
        bpy.data.images.remove(im)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    D = float(sc["vki_cam_dist"]); tgt = vki_get(sc, "vki_cam_target")
    dg = vki_depsgraph(sc)
    fl, cp, pr = [], [], {}
    for py in range(step // 2, h, step):
        for px in range(step // 2, w, step):
            C, d = vki_cam_ray(px + 0.5, py + 0.5, D, tgt, (w, h))
            hit, loc, nrm, idx, ob, mat = sc.ray_cast(dg, C, d)
            if not hit or nrm.z < 0.7:
                continue
            o = ob.original
            c = o.get("vki_class")
            if c is None or o.type != "MESH" or idx >= len(o.data.polygons):
                continue
            mi = o.data.polygons[idx].material_index
            v = float(lum[py, px])
            if c in ("floor", "ground") and mi == VKI_FLOOR:
                fl.append(v)
            elif c in ("wall", "rock") and mi == VKI_CAP:
                cp.append(v)
            elif c == "prop" and o.get("vki_mount") != "table" and not o.get("vki_placeholder"):
                pr.setdefault(o.name, []).append(v)
    warns = []
    fm = float(numpy.mean(fl)) if fl else None
    cm = float(numpy.mean(cp)) if cp else None
    night = sc.get("vki_preset", "Day") in VKI_DARK_PRESETS            # Night, and the torch-lit Dungeon preset
    if fm is not None:
        lim = 0.15 if night else 0.25                    # §9 visual 3: walkable floor >= 0.25 by Day, 0.15 by Night
        if fm < lim:
            warns.append(f"level: floor mean {fm:.3f} < {lim} ({sc.get('vki_preset', 'Day')}, render luma)")
    if fm is not None and cm is not None and cm < fm + 0.15:
        warns.append(f"palette: cap tops {cm:.3f} < floor {fm:.3f} + 0.15 (render luma)")
    for n_, vs in sorted(pr.items()):
        o = sc.objects.get(n_)
        if len(vs) < 8 or fm is None or night or o is None or o.get("vki_mount") == "wall_hung" or \
                o.get("vki_tier") == "dressing":
            continue                                     # furniture tops by Day only (at Night everything is dark)
        md = float(numpy.median(vs))
        if abs(md - fm) < 0.12:
            warns.append(f"palette: {n_} top {md:.3f} vs floor {fm:.3f} (< 0.12 apart, render luma)")
    return dict(floor=fm, caps=cm, floor_n=len(fl), caps_n=len(cp), props=len(pr)), warns


def vki_check(scene, full=False, t19=True, bfs=True, palette=True):
    """§9 T12 room rules on a built VKI_<S> scene, plus T19. Errors: posts (vki_t12_posts: L/T/X Corner, steps and
    FREE ENDS need posts, post height), floor coverage gaps / overlaps, doors without free cells on both sides,
    missing links / spawns, spawn capsules within 0.2 m of a trigger, prop-prop and prop-structure clashes (AABB then
    mesh BVH), overlays across walls / sills / thresholds, wall_hung on Cut or without a host, mount zmax over H-0.14,
    Full Window/Lancet/Special pieces in Cut runs and Cut specials, failed hugs, BFS reachability, T19 visibility.
    Warnings: R-occ1-6, palette (render luma: caps >= floor + 0.15, prop tops >= 0.12 from the floor), plan codes.
    Returns the error list; full=True returns dict(errors, warnings, placeholders, stats)."""
    sc = bpy.data.scenes[scene] if isinstance(scene, str) else scene
    vki_rooms_dg_ensure(sc)
    name = sc.name
    L = vki_rooms_layout(name)
    R = L["R"]
    objs = list(sc.objects)
    errs, warns = list(L["problems"]), []
    cls_of = lambda o: o.get("vki_class")
    walls = [o for o in objs if cls_of(o) == "wall"]
    posts = [o for o in objs if cls_of(o) == "post"]
    props = [o for o in objs if cls_of(o) == "prop" and o.type == "MESH"]
    overlays = [o for o in objs if cls_of(o) == "overlay" and o.type == "MESH"]
    links = [o for o in objs if o.get("vki_link") in ("stair_up", "stair_down")]
    leaves = [o for o in objs if cls_of(o) == "leaf"]
    floors = [o for o in objs if (cls_of(o) == "floor" and o.get("vki_kind") != "Sill") or
              (cls_of(o) == "ground" and not o.get("vki_covers_floor"))]   # channel tiles: their X quarters, below
    sills = [o for o in objs if cls_of(o) == "floor" and o.get("vki_kind") == "Sill"]
    cache = {}
    # 1 posts (§2.3 / §10.1)
    errs += vki_t12_posts(walls + posts)
    # 2 floor coverage, per quarter cell (adventure kit: the chasm's dual-grid ground tiles and the Floor_075
    # quarters cover parts of cells)
    cover = {}
    qpts = [(a, b) for a in (0.25, 0.75) for b in (0.25, 0.75)]

    def mark(name, x0, y0, x1, y1):
        for c in range(L["nc"]):
            for r in range(L["nr"]):
                for qi, (a, b) in enumerate(qpts):
                    qx, qy = VKI_IG * (c + a), VKI_IG * (r + b)
                    if x0 < qx < x1 and y0 < qy < y1:
                        cover.setdefault((c, r, qi), []).append(name)
    for f in floors:
        fp = [float(t) for t in str(f.get("vki_footprint", "0,0,1.5,1.5")).split(",")]
        mark(f.name, f.location.x + fp[0], f.location.y + fp[1], f.location.x + fp[2], f.location.y + fp[3])
    for o in objs:
        if o.get("vki_link") == "stair_down" or o.get("vki_covers_floor"):
            cf = vki_get(o, "vki_covers_floor", None) or [0.0, 0.0, 1.5, 4.5]
            for cf_ in (cf if isinstance(cf[0], (list, tuple)) else [cf]):      # a rect, or a list of them
                bb = vki_rooms_boxes_of(o, [[(cf_[0] + cf_[2]) / 2, (cf_[1] + cf_[3]) / 2, 0.0, cf_[2] - cf_[0],
                                             cf_[3] - cf_[1], 0.1]])[0]
                mark(o.name, bb[0][0], bb[0][1], bb[1][0], bb[1][1])
    for c in range(L["nc"]):
        for r in range(L["nr"]):
            ns_ = [len(cover.get((c, r, qi), [])) for qi in range(4)]
            if min(ns_) == 0:
                errs.append(f"T12 floor gap at cell ({c},{r})")
            elif max(ns_) > 1:
                errs.append(f"T12 floor overlap at cell ({c},{r}): "
                            f"{sorted({n for qi in range(4) for n in cover.get((c, r, qi), [])})}")
    # 3 doors: free cells on both sides (exits: inside)
    blockers = [o for o in props if o.get("vki_mount") not in ("table", "wall_hung")] + links
    for d in L["doors"]:
        pc = L["pieces"][d["pi"]]
        for (c, r) in d["cells"]:
            cell = ((VKI_IG * c + 0.30, VKI_IG * r + 0.30, 0.05), (VKI_IG * (c + 1) - 0.30, VKI_IG * (r + 1) - 0.30, 1.0))
            hit = [o.name for o in blockers if any(vki_rooms_box_hit(cell, bb) for bb in vki_rooms_collider_boxes(o, (0.05, 1.8)))]
            if hit:
                errs.append(f"T12 door {pc['piece'][12:]} at ({pc['x']},{pc['y']}): cell ({c},{r}) not free ({hit[0]})")
    # 4 links and spawns
    spawns = {o.get("vki_spawn_id"): o for o in objs if o.get("vki_spawn_id")}
    trig = []
    for o in objs:
        if o.get("vki_link") and vki_get(o, "vki_trigger", None):
            trig.append((o, vki_rooms_boxes_of(o, [vki_get(o, "vki_trigger")])[0]))
    for (lid, kind, target) in R["links"]:
        if not any(o.get("vki_link_id") == lid and o.get("vki_link") == kind for o in objs):
            errs.append(f"T12 link {lid} ({kind} -> {target}) missing")
        if lid not in spawns:
            errs.append(f"T12 SPN_{lid} missing")
        elif lid in R.get("spawns", {}):
            ex = R["spawns"][lid]
            sp = spawns[lid]
            if math.hypot(sp.location.x - ex[0], sp.location.y - ex[1]) > 0.02:
                warns.append(f"spawn {lid} at ({sp.location.x:.2f},{sp.location.y:.2f}), §6 lists ({ex[0]},{ex[1]})")
    for sid, sp in spawns.items():
        for o, tb in trig:
            d_ = vki_rooms_rect_dist(((sp.location.x, sp.location.y, 0), (sp.location.x, sp.location.y, 0)), tb)
            if d_ < VKI_ROOMS_CAPSULE + 0.2 - 1e-6:
                errs.append(f"T12 spawn {sp.name}: capsule within 0.2 m of the trigger of {o.name} ({d_:.3f} m)")
    # 5 clashes
    boxes = {o.name: vki_rooms_obj_box(o, 0.005) for o in props + overlays}
    for i, a in enumerate(props):
        if a.get("vki_mount") == "table":
            continue
        for b in props[i + 1:]:
            if b.get("vki_mount") == "table":
                continue
            if vki_rooms_box_hit(boxes[a.name], boxes[b.name]) and vki_rooms_touch(a, b, cache):
                errs.append(f"T12 prop clash {a.name} / {b.name}")
    struct = walls + posts + links + leaves + [o for o in objs if cls_of(o) == "rock"]
    sboxes = {o.name: vki_rooms_obj_box(o) for o in struct + sills}
    for a in props + overlays:
        hung = a.get("vki_mount") == "wall_hung"
        if hung:
            r_ = math.radians(a.get("vki_rot", 0))
            bdir = Vector((-math.sin(r_), math.cos(r_)))
        for s_ in struct + (sills if cls_of(a) == "overlay" else []):
            if a.get("vki_wall_anchor") and cls_of(s_) in ("wall", "post", "rock"):
                continue                                                 # webs: anchored into the (cave) rock
            if hung and cls_of(s_) == "wall":
                d = (vki_mw(s_) @ Vector((1, 0, 0))).to_2d() - vki_mw(s_).translation.to_2d()
                if abs(d.normalized().dot(bdir)) < 1e-3:
                    off = (vki_mw(s_).translation.to_2d() - a.location.to_2d()).dot(bdir)
                    if 0.0 < off < 0.5:
                        continue                                         # the wall line the prop hangs on
            if vki_rooms_box_hit(boxes[a.name], sboxes[s_.name]) and vki_rooms_touch(a, s_, cache):
                if a.get("vki_edge") and cls_of(s_) in ("wall", "post"):
                    # edge pieces (AltarRail) may be let into a wall / respond at their ends (vki_edge_let_in)
                    li = float(a.get("vki_edge_let_in", 0.0))
                    r_ = math.radians(a.get("vki_rot", 0) or 0)
                    ax = 0 if abs(math.cos(r_)) > 0.5 else 1
                    ab, sb = vki_rooms_obj_box(a), sboxes[s_.name]
                    ov = min(ab[1][ax], sb[1][ax]) - max(ab[0][ax], sb[0][ax])
                    at_end = ab[0][ax] >= sb[0][ax] - 1e-6 or ab[1][ax] <= sb[1][ax] + 1e-6
                    if at_end and ov <= li + 1e-3:
                        continue
                errs.append(f"T12 {'overlay' if cls_of(a) == 'overlay' else 'prop'} {a.name} intersects {s_.name}")
    for a in links:
        for s_ in walls + posts:
            ab = vki_rooms_obj_box(a, 0.002)
            if vki_rooms_box_hit(ab, sboxes[s_.name]) and vki_rooms_touch(a, s_, cache):
                sb = sboxes[s_.name]
                ov = min(min(ab[1][k_], sb[1][k_]) - max(ab[0][k_], sb[0][k_]) for k_ in (0, 1))
                if ov <= 0.12:          # a trimmer / rail end let into a post: buried, invisible
                    warns.append(f"stair {a.name} runs {ov:.3f} m into {s_.name} (let-in, hidden inside it)")
                else:
                    errs.append(f"T12 stair {a.name} intersects {s_.name} ({ov:.3f} m)")
    # 6 mounts and hosts
    for a in props:
        if "vki_hug_fail" in a.keys():
            errs.append(f"T12 {a.name}: hug failed ({a['vki_hug_fail']})")
        if a.get("vki_mount") == "wall_hung":
            if a.get("vki_host_height") == "Cut":
                errs.append(f"T12 wall_hung {a.name} on a Cut wall (R-occ4)")
            elif not a.get("vki_host"):
                errs.append(f"T12 wall_hung {a.name} has no host wall")
            H = float(a.get("vki_host_H", 3.0))
            zt = vki_rooms_obj_box(a)[1][2]
            zmx = float(a.get("vki_mount_zmax", zt))
            if max(zt, zmx) > H - 0.14 + 1e-6:
                errs.append(f"T12 wall_hung {a.name}: top {max(zt, zmx):.2f} over the host's H - 0.14 ({H - 0.14:.2f})")
    runs = {}
    for w in walls:
        for e_ in vki_wall_end_nodes([w]).items():
            runs.setdefault(e_[0], []).append(w)
    for w in walls:
        kind, ht = w.get("vki_kind"), w.get("vki_height")
        if kind in ("Fireplace", "Hearth", "Forge") and ht == "Cut":
            errs.append(f"T12 special {w.name} is a Cut piece (specials are never placed on Cut runs)")
        if kind in ("Window", "Lancet", "LancetTall", "Fireplace", "Hearth", "Forge") and ht == "Full":
            nbrs = [o for nd, ws in runs.items() if w in ws for o in ws if o is not w]
            nbrs = [o for o in nbrs if abs(math.cos(vki_mw(o).to_euler().z - vki_mw(w).to_euler().z)) > 0.99]
            if nbrs and all(o.get("vki_height") == "Cut" for o in nbrs):
                errs.append(f"T12 Full {kind} {w.name} stands in a Cut run")
    # 7 BFS
    bres = vki_rooms_bfs(sc, L) if bfs else dict(errors=[], warnings=[], reach=set(), nodes=0)
    errs += bres["errors"]
    warns += bres["warnings"]
    # 8 palette (§4.3 targets, measured on the fit game shot when it exists)
    pstats, pwarn = vki_rooms_palette(sc) if palette else (None, [])
    warns += pwarn
    # 9 R-occ warnings
    cut_walls = [w for w in walls if w.get("vki_height") == "Cut"]
    for o in links:
        if o.get("vki_link") == "stair_down":
            hole = vki_rooms_boxes_of(o, [[0.80, 1.86, 0.0, 0.94, 3.52, 0.1]])[0]
            for w in cut_walls:
                if vki_rooms_rect_dist(hole, vki_rooms_wall_env(w)) < 1.5:
                    warns.append(f"R-occ1 stair hole of {o.name} within 1.5 m of the Cut wall {w.name}")
                    break
    t19e = []
    if t19:
        root = sc.objects.get(sc.get("vki_root", "")) if sc.get("vki_root") else None
        tgt = vki_get(sc, "vki_cam_target", None); D = sc.get("vki_cam_dist")
        if tgt is not None and D:
            sxy = vki_rooms_struct_xy(sc)
            pts = [(lab, p) for lab, p in vki_vis_points(sc)
                   if ".use" not in lab or vki_rooms_use_possible(p.x, p.y, sxy, L)]
            t19e = vki_t19_visibility(sc, cams=[vki_cam_loc(tgt, float(D))], points=pts)
        else:
            t19e = ["T19: the scene has no vki_cam_target / vki_cam_dist"]
    errs += t19e
    for a in props:
        bb = vki_rooms_obj_box(a)
        h = bb[1][2] - bb[0][2]
        zb = bb[0][2]
        if h > 1.25:
            hides = [e for e in t19e if a.name in e]
            north = a.get("vki_mount") == "wall_floor" and abs((a.get("vki_rot", 0) or 0) % 360) < 1e-6
            if hides and not north:
                warns.append(f"R-occ2 {a.name} ({h:.2f} m) hides: {hides[0]}")
        if bb[1][2] > 2.0 and not a.get("vki_cam_fade") and a.get("vki_mount") != "wall_hung":
            over = [n_ for n_ in bres["reach"] if bb[0][0] < n_[0] < bb[1][0] and bb[0][1] < n_[1] < bb[1][1]]
            if over:
                warns.append(f"R-occ3 {a.name} rises to {bb[1][2]:.2f} m over a walk lane")
        if h > 0.75 and a.get("vki_mount") not in ("floor", "table") and a.get("vki_mount") is not None:
            for w in cut_walls:
                if vki_rooms_rect_dist(bb, vki_rooms_wall_env(w)) < 0.9 - 0.03:
                    warns.append(f"R-occ5 {a.name} ({h:.2f} m, {a.get('vki_mount')}) within 0.9 m of the Cut wall {w.name}")
                    break
        if h > 1.00 and a.get("vki_warn_ok") != "window":
            for w in walls:
                if w.get("vki_kind") not in ("Window", "Lancet", "LancetTall") or w.get("vki_height") != "Full":
                    continue
                op = vki_get(w, "vki_opening", None) or {"x0": 0.33, "x1": 1.17}
                obox = vki_rooms_boxes_of(w, [[(op["x0"] + op["x1"]) / 2, -0.25 - 0.45, 1.0, op["x1"] - op["x0"], 0.9, 2.0]])[0]
                if vki_rooms_rect_dist(bb, obox) < 1e-6:
                    warns.append(f"R-occ6 {a.name} ({h:.2f} m) within 0.9 m of the window {w.name}")
                    break
    # 10 plan codes (a generated view: the prop list is the source of truth)
    codes = L["P"]["codes"]
    for a in props:
        short = vki_ph_short(a.get("vki_piece", ""))
        short = short[5:] if short.startswith("Prop_") and ("Prop_" + short[5:]) not in VKI_ROOMS_CODES else short
        code = VKI_ROOMS_CODES.get(short) or VKI_ROOMS_CODES.get("Prop_" + short)
        if not code:
            continue
        bb = vki_rooms_obj_box(a, 0.10)
        cells = {(c, r) for c in range(int(bb[0][0] // VKI_IG), int(bb[1][0] // VKI_IG) + 1)
                 for r in range(int(bb[0][1] // VKI_IG), int(bb[1][1] // VKI_IG) + 1)}
        have = {codes.get(c_) for c_ in cells}
        ok = code in have or (code == "fm" and "TB" in have) or (code == "tb" and "TB" in have)
        if not ok:
            warns.append(f"plan code: {a.name} ({code}) stands in cells {sorted(cells)} coded {sorted(h for h in have if h)}")
    ph = {}
    for o in objs:
        if o.get("vki_placeholder"):
            ph[o.get("vki_piece", o.name)] = ph.get(o.get("vki_piece", o.name), 0) + 1
    if not full:
        return errs
    return dict(errors=errs, warnings=warns, placeholders=dict(sorted(ph.items())), ph_total=sum(ph.values()),
                stats=dict(objects=len(objs), walls=len(walls), posts=len(posts), props=len(props),
                           overlays=len(overlays), floors=len(floors), bfs_nodes=bres["nodes"],
                           reach=len(bres["reach"]), t19=len(t19e), palette=pstats))


def vki_rooms_dg_ensure(sc):
    """make sure the scene has an evaluated depsgraph: view_layer.depsgraph is None for a scene that was never shown
    or evaluated in this session, and core helpers (vki_depsgraph, vki_flush_lights) call .update() on it"""
    for vl in sc.view_layers:
        vl.update()
    return sc.view_layers[0].depsgraph


def vki_rooms_shots(name, plan=True, px_per_m=110):
    """fit game shot + plan of a room scene in its preset (Day, Night for the tavern floors):
    renders/interior/<scene>/<tag>_game.png and _plan.png"""
    tag = vki_rooms_tag(name)
    vki_rooms_dg_ensure(bpy.data.scenes[name])
    out = [vki_shot(name, tag + "_game", "game")]
    if plan:
        out.append(vki_shot(name, tag + "_plan", "plan", px_per_m=px_per_m))
    return out
