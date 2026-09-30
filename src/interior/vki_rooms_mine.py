# ===================== VKI ROOMS MINE: the mine kit's track layout, level and catalog rows (docs/MINE_KIT.md) =====================
# Loaded by vki_ns() right after vki_fam_mine. A mine is a cave map (R["cave"]): galleries two cells wide driven
# through the rock, stopes where the veins are worked, the shaft; the track is laid from R["tracks"] (vki_mine_tracks,
# called by vki_cave_layout: its tiles join the level's auto props).
#   VKI_Mine_M1  the mine under the dwarf hall, 22 x 13: the haulage gallery runs the width of the map from the adit
#                in the west (timbered, a scene link up to the surface: the way to the town) to the tunnel back to the
#                dwarf hall in the east, the track down its middle under a timber set every few metres, lanterns on
#                every other; a spur north into the gold stope (the vein in the north face, a loaded cart, ore, a
#                barrow; the old drift beyond it caved in and barricaded); the shaft chamber south of the gallery -- the
#                shaft with the great treadwheel over it (a point of interest, the lift down to the deep workings), a
#                spur to its rim; the iron drift south-east (the vein at its end, the track to it, a tipped cart, a
#                broken set at its mouth); the crystal cave the miners broke into (north-east); the miners' store by the
#                adit (a sorting bench, tools, barrels, spare sleepers)
# The galleries are timber-lined: Mine walls (vki_fam_mine) on the inner grid lines between their floor and the rock, Cut
# ("==", ":") where the rock behind is Cut, Full ("##") where it is Full -- the haulage gallery, the drifts' mouths and
# the iron drift; the stope, the shaft chamber, the store and the crystal cave stay natural rock.
# Plan codes: "ms" the shaft (R["pits"]), "TW" the treadwheel, "AU" / "FE" / "CY" the gold / iron / crystal veins, "Sx"
# the tunnels' spawns, "Ss" the lift's, "CR" / "MG" / "SM" crystals, glowing mushrooms, stalagmites, "ba" / "bx"
# barrels, crates; the track is not painted (R["tracks"] is its source). Every top-level name
# starts with vki_/VKI_ (T18).

VKI_MINE_SCENES = ["VKI_Mine_M1"]


def vki_mine_tracks(R, P, problems):
    """the track tiles of R["tracks"] -- polylines [(x, y) | (x, y, "open"), ...] with vertices on the 0.75 lattice,
    each segment axis-aligned and a whole number of 1.5 m tiles long -- as prop tuples ("Overlay_Track_<kind>", x, y,
    rot, None, None, {"hug": False}): a tile on every track point, its kind and turn from its connections
    (vki_mine_track_piece); polylines that share a point join there (a Tee or Cross turntable); an end marked "open"
    runs on out of the level (a Straight into an adit or tunnel) instead of stopping at a buffer. A tile that is not an
    open end must lie on open cells of the map (else a problem)."""
    B = VKI_MINE_BITS
    dirs = {(0, 1): B["N"], (1, 0): B["E"], (0, -1): B["S"], (-1, 0): B["W"]}
    key = lambda x, y: (int(round(x * 1000)), int(round(y * 1000)))
    conn, pos, opened = {}, {}, set()
    for li, line in enumerate(R.get("tracks", [])):
        pts = [(float(p[0]), float(p[1])) for p in line]
        seq = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            n = int(round((abs(dx) + abs(dy)) / VKI_IG))
            if (abs(dx) > 1e-6 and abs(dy) > 1e-6) or n == 0 or abs(n * VKI_IG - abs(dx) - abs(dy)) > 1e-3:
                problems.append(f"track {li}: segment ({x0},{y0})-({x1},{y1}) is not axis-aligned whole tiles")
                break
            seq += [(x0 + dx * s / n, y0 + dy * s / n) for s in range(1, n + 1)]
        for (xa, ya), (xb, yb) in zip(seq[:-1], seq[1:]):
            d = (int(round((xb - xa) / VKI_IG)), int(round((yb - ya) / VKI_IG)))
            ka, kb = key(xa, ya), key(xb, yb)
            pos[ka], pos[kb] = (xa, ya), (xb, yb)
            conn[ka] = conn.get(ka, 0) | dirs[d]
            conn[kb] = conn.get(kb, 0) | dirs[(-d[0], -d[1])]
        if len(seq) < 2:
            continue
        for end, nb in ((0, 1), (-1, -2)):
            p = line[end]
            if len(p) > 2 and p[2] == "open":
                (xe, ye), (xn, yn) = seq[end], seq[nb]
                ke = key(xe, ye)
                conn[ke] |= dirs[(int(round((xe - xn) / VKI_IG)), int(round((ye - yn) / VKI_IG)))]
                opened.add(ke)
    codes, nc, nr = P["codes"], P["nc"], P["nr"]
    out = []
    for kk, m in sorted(conn.items()):
        x, y = pos[kk]
        kind, rot = vki_mine_track_piece(m)
        if kk not in opened:
            cs = {(c, r) for c in range(int(math.floor((x - 0.7) / VKI_IG)), int(math.floor((x + 0.7) / VKI_IG)) + 1)
                  for r in range(int(math.floor((y - 0.7) / VKI_IG)), int(math.floor((y + 0.7) / VKI_IG)) + 1)}
            bad = sorted(c for c in cs if not (0 <= c[0] < nc and 0 <= c[1] < nr) or codes.get(c) == "##")
            if bad:
                problems.append(f"track: the {kind} tile at ({x},{y}) lies on rock or off the map {bad}")
        out.append(("Overlay_Track_" + kind, round(x, 4), round(y, 4), rot, None, None, {"hug": False}))
    return out


VKI_PLANS.update({
    "VKI_Mine_M1": """
        0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21
     +##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+##+
  12 ### ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ###
     +                                                                 +
  11 #.. .. .. .. .. AU .. .. .. ## ## ## ## ## ## SM .. CY .. ## ## ###
     +                                                                 +
  10 #.. .. .. .. .. .. .. .. .. .. ## ## ## ## .. .. .. .. .. .. ## ###
     +                                                                 +
   9 ### ## ## ## .. .. .. .. .. .. ## ## ## ## CR .. .. .. .. MG ## ###
     +                                                                 +
   8 ### ## ## ## ##:.. ..:## ## ## ## ## ## ## ## ##:.. ..:## ## ## ###
     +==+==+==+==+==+      ==+==+==+##+##+##+##+==+==+      ==+==+##+##+
   7 #Sx .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. Sx#
     +                                                                 +
   6 #Sx .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. Sx#
     +==+==+      ==+==+==+==+                     ==+==+==+==+      ==+
   5 ### ##:.. ..:## ## ## ## .. .. .. .. .. .. .. ## ## ## ##:.. ..:###
     +                                                                 +
   4 ### .. .. .. .. .. ## ## .. TW .. ms ms .. bx ## ## ## ##:.. ..:###
     +                                             ==+==+==+==+        +
   3 ### .. .. .. .. .. ## ## .. .. .. ms ms .. .. .. .. .. .. .. FE ###
     +                                                                 +
   2 ### ba ba .. .. bx ## ## .. .. .. .. Ss .. .. .. .. .. .. .. .. ###
     +                                             ==+==+==+==+==+==+  +
   1 ### ## ## ## ## ## ## ## .. .. .. .. .. .. .. ## ## ## ## ## ## ###
     +                                                                 +
   0 t## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##t
     +==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+==+
""",
})

VKI_ROOMS.update({
    "VKI_Mine_M1": dict(
        building="Mine", floor=-1, preset="Mine", family=dict(perimeter="Cave", partition="Mine"), cave=True,
        pools=False,
        zones={"crystal": dict(cells=[(14, 19, 9, 11)], floor="CaveFloor"),
               "store": dict(cells=[(1, 5, 2, 4), (2, 3, 5, 5)], floor="EarthDamp"),
               "mine": dict(cells="rest", floor="EarthDamp")},
        # loose debris (vki_props_debris): the mine's own theme (rocks, ore, lost tools, rails, planks), the store kept
        # tidier, the crystal cave a cave
        debris=dict(density=0.36, seed=23, zones={"store": 0.18}, themes={"mine": "mine", "store": "mine"}),
        tunnels={(0, 7): "surface", (22, 7): "hall"},
        tunnel_kinds={"surface": "Adit"},
        links=[("surface", "passage", "@surface"), ("hall", "passage", "VKI_Dwarf_Hall"), ("deep", "lift", "@deep")],
        pits=[("Pit_Shaft_300x300", 16.5, 4.5)],
        # the main line from the adit (it runs on out of it) along the gallery's centre line, turning south into the
        # iron drift; spurs north into the gold stope and south to the shaft's rim (turntables where they leave it)
        tracks=[[(0.0, 10.5, "open"), (30.0, 10.5), (30.0, 4.5)],
                [(9.0, 10.5), (9.0, 15.0)],
                [(18.0, 10.5), (18.0, 9.0)]],
        props=[  # the haulage gallery (y 9-12): a set every few metres (none on the junctions), lanterns on every other
               ("Mine_Set_Lamp", 3.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set", 6.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set_Lamp", 12.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set", 15.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set_Lamp", 21.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set", 24.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set_Lamp", 27.0, 10.5, 90, None, None, {"hug": False}),
               ("Mine_Set", 32.25, 10.5, 90, None, None, {"hug": False}),
               # sets over the drifts' mouths
               ("Mine_Set", 9.0, 12.75, 0, None, None, {"hug": False}),
               ("Mine_Set_Lamp", 25.5, 12.75, 0, None, None, {"hug": False}),
               ("Mine_Set", 30.0, 7.5, 0, None, None, {"hug": False}),           # (off the tunnels' sight lines
               ("Mine_Set_Lamp", 4.5, 7.75, 0, None, None, {"hug": False}),      #  to the camera, T19)
               ("Mine_Set_Broken", 22.5, 4.5, 90, None, None, {"hug": False}),
               # the shaft chamber: the treadwheel over the shaft (the lift down), a loaded cart on the spur
               ("POI_Treadwheel", 18.0, 6.0, 0, None, None, {"hug": False, "link": "deep"}),
               ("Mine_Cart_Ore", 18.0, 9.3, 0, None, None, {"hug": False}),
               ("Mine_LanternPole", 21.6, 2.4, 0, None, None, {"hug": False}),
               ("Crate", 21.5, 6.6, 0, None, None, {"hug": False}),
               ("Mine_OrePile", 20.6, 4.2, 0, None, None, {"hug": False}),      # ore brought up, to be carted out
               ("Mine_ToolRack", 12.3, 3.4, 90, None, None, {"hug": False}),     # against the chamber's west face
               ("Mine_SleeperStack", 14.2, 2.5, 20, None, None, {"hug": False}),
               # the gold stope (x 4.5-15, y 13.5-18) and the caved-in drift west of it
               ("Vein_Gold", 8.25, 17.75, 0, None, None, {"hug": False}),
               ("Mine_Cart_Ore", 9.0, 13.95, 0, None, None, {"hug": False}),
               ("Mine_OrePile", 11.6, 16.4, 0, None, None, {"hug": False}),
               ("Mine_Wheelbarrow", 12.2, 15.2, -30, None, None, {"hug": False}),
               ("Mine_LanternPole", 7.0, 14.8, 0, None, None, {"hug": False}),
               ("Mine_CaveIn", 1.25, 16.5, 90, None, None, {"hug": False}),
               ("Mine_Barricade", 3.0, 16.5, 90, None, None, {"hug": False}),
               # the crystal cave (x 21-30, y 13.5-18)
               ("Vein_Crystal", 26.25, 17.75, 0, None, None, {"hug": False}),
               ("Crystals", 22.4, 14.4, 0, None, None, {"hug": False}),
               ("Mushrooms_Glow", 29.0, 14.3, 0, None, None, {"hug": False}),
               ("Stalagmites", 23.4, 16.7, 0, None, None, {"hug": False}),
               # the iron drift (x 22.5-31.5, y 3-6): the vein at its east end, the track to it
               ("Vein_Iron", 31.25, 4.5, -90, None, None, {"hug": False}),
               ("Mine_Cart", 30.0, 7.5, 0, None, None, {"hug": False}),
               ("Mine_OrePile", 28.0, 4.4, 0, None, None, {"hug": False}),
               ("Mine_Cart_Tipped", 24.3, 4.6, 0, None, None, {"hug": False}),
               ("Mine_LanternPole", 26.3, 4.5, 0, None, None, {"hug": False}),
               # the store by the adit (x 1.5-9, y 3-7.5)
               ("Barrel", 2.3, 4.0, 180, None, None, {"hug": False}),              # their use points to the room
               ("Barrel", 3.2, 4.1, 180, None, None, {"hug": False}),
               ("Mine_Bench", 5.6, 4.2, 180, None, None, {"hug": False}),
               ("Crate", 7.7, 4.1, -90, None, None, {"hug": False}),               # (the rock east of it is Full)
               ("Mine_ToolRack", 1.8, 5.6, 90, None, None, {"hug": False}),
               ("Mine_SleeperStack", 7.9, 6.4, 0, None, None, {"hug": False}),
               ("Mine_LanternPole", 4.2, 6.0, 0, None, None, {"hug": False})]),
})

# the scatter's mine theme (vki_props_debris): rocks, ore, lost tools, rails, planks
VKI_DEB_KINDS["mine"] = [("Rocks_A", 3), ("Rocks_B", 2), ("Rocks_C", 2), ("Rubble", 1.2), ("Ore", 2.5), ("Tools", 1.5),
                         ("Rail", 1), ("Planks", 1.5), ("Sack", 0.6), ("Crate", 0.4), ("Barrel", 0.4),
                         ("Campfire", 0.2), ("Overlay_Gravel", 1.5)]
VKI_DEB_STONE["mine"] = "M_VKI_CaveRock"

VKI_ROOMS_CODES.update({"POI_Treadwheel": "TW", "Vein_Gold": "AU", "Vein_Iron": "FE", "Vein_Crystal": "CY"})

VKI_ADVENTURE_CATALOG += [
    ("Mine track, carts, timbering, the adit, debris", -215.0,
     [n for n in VKI_MINE_NAMES if any(t in n for t in ("_Track_", "_Mine_Cart", "_Mine_Set", "_Adit", "_Debris_"))]),
    ("Mine veins, props, the shaft and the treadwheel", -222.0,
     [n for n in VKI_MINE_NAMES if "_Vein_" in n or ("_Prop_Mine_" in n and "_Mine_Cart" not in n and "_Mine_Set" not in n)]
     + ["SM_VKI_Pit_Shaft_300x300", "SM_VKI_Prop_POI_Treadwheel"]),
    ("Mine walls: the timber lining, and its posts", -229.0, VKI_MNW_NAMES),
]
