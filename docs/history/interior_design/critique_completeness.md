# Interior Kit (VKI) spec review: the user's view

I checked the spec against the user's five decisions, the showcase scope, HANDOFF.md taste notes, the gallery renders and the code (exterior door widths, loom, bellows and tool-wall geometry, `build_inn` styles). I parsed every ASCII plan cell by cell and made no Blender calls. The camera figures below are my own arithmetic from §1 (D = 18, 50° pitch, 30° vertical FOV, camera at target + (0, −11.57, 13.79)).

1. **[BLOCKER] The Board family has no Rake, but five placements in the plans need one.**
   - §3.1 marks Board `Rake_150_L/R` as "–".
   - Tavern F1 uses Board partitions with a `t` at x=3.0 row 4, x=7.5 row 4, x=4.5 row 0 and x=9.0 row 0.
   - The Smithy store partition (Board) has a `t` at x=3.0 row 0.
   - Tavern F1 and the Smithy cannot be closed as drawn.
   - **Fix, part 1:** add `SM_VKI_Wall_Board_Rake_150_L/R` to PKG-S (two masters).
   - **Fix, part 2:** change the default in §2.4. An N–S wall is Full only if its north end meets a Full wall. An N–S partition whose north end meets a Cut wall defaults to Cut and needs no rake. That covers Tavern F1 rows 0–2, the Smithy store and the Townhouse shop partition. As drawn, those 3 m fins and their Full corner posts hide a strip about 0.5 m wide and 2.5 m long north of each north end (3/tan 50°), across the corridor and room floors.
   - Add a legend code for a door in an N–S Cut wall (e.g. `d`). The legend currently has only `D`, which is Full.

2. **[HIGH] Five interactables in the plans cannot be reached, so the spec's own T12 BFS check fails.**
   - **Townhouse F0 kitchen:** its only door is `D` at x=7.5 row 3. `bn` at (4,3)–(4,4) is a Settle_300 backed onto that partition, so it covers the door. The kitchen is unreachable. The settle also runs 0.25 m into the north wall. Fix: row 3 col 4 becomes `..`, and (4,4) becomes a `Form_150` facing the fire.
   - **Smithy store:** `ir` at (1,1) is the only store-side cell in front of door `D` (x=3.0 row 1). The iron stock (1.5 × 0.6) leaves about 0.4 m, and the capsule needs 0.6.
   - **Smithy armour stand:** `AS` at (6,4) is boxed in by CO (5,4), QT (5,3) and WB (6,3). The gap between the trough end (x 9.0) and the workbench (x 9.45) is 0.45 m, so the stand's front use point lies inside the workbench.
   - Smithy fix: row 3 `#.. .. AN .. .. QT ..#`, row 2 `W.. .. .. .. .. .. WB#`, row 1 `#ir ..D.. .. .. GS WB#`, row 0 `tsk bxt.. .. Sf .. ..t`. Move the ToolWall to east wall rows 1–2.
   - **Tavern F0 kitchen:** `OV` at (8,6) opens south onto `WB` at (8,5), so the oven's use point is inside the worktable. The six-cell kitchen also has to hold a door landing (7,5) and the trapdoor approach (6,5). Fix: row 6 `#td OV WB#`, row 5 `tSc .. ..#`. Drop PN, since the cellar already has two. This keeps the trapdoor aligned with the cellar.
   - **Cellar (minor):** the row-4 cask racks sit 0.6 m behind the row-3 racks and are hidden by them. Either turn row 4 into a `Stillage_300` against the wall or accept it as set dressing.
   - Add a plan rule: the cell on each side of every door is `..` or a spawn.

3. **[HIGH] Prop sizes ignore wall thickness, so props run into walls.**
   - A cell backed by a Class-O wall has 1.25 m clear; a corner cell has 1.25 × 1.25; a Class-P wall leaves 1.35.
   - Clashes in the plans:

     | Prop | Size | Where | Problem |
     |---|---|---|---|
     | `Oven_150` | 1.3 × 1.3 | corners: Townhouse F0 (6,4), Tavern F0 (8,6) | 0.05–0.15 m into the walls |
     | `Dresser_130` | 1.3 wide | beside partitions: Cottage (4,4), Townhouse F1 (4,4), Tavern F1 (5,6) | 0.15 m into the partition |
     | `Table_Trestle_300` | 3.0 long | Cottage cols 0–1, against the west wall | 0.25 m into the wall |
     | Townhouse F0 `TB` | 2×1 | north of the cut partition | table plus two forms is 1.6 m in a 1.25 m row |
     | `Pantry_Shelves_300` | 2.9 | Cellar (4–5,4) | 0.2 m into the east wall |
     | `CaskRack_150` | 1.3 | Cellar corner (0,4) | 0.15 m into the wall |
     | `IronStock_150` | 1.5 | against a Board wall | too long for 1.35 m |
     | `Altar_150` | 1.8 wide | one-cell footprint | T10's footprint = bbox check fails |

   - **Fix:** size any prop that may touch a wall to n·1.5 − 0.30. That means 1.20 for one cell and 2.70 for two; wall-backed depth is at most 1.20 per cell. Rename or resize accordingly: the `_300` tables, forms, settles and pantry become 2.7, Oven and Dresser 1.2, IronStock 1.2, and the altar becomes `Altar_300` (2×1).
   - Add a clash check to T12: prop bounding boxes against wall bodies and post envelopes.

4. **[HIGH] The ASCII codes cannot drive a deterministic assembler.**
   - Several codes stand for different pieces or footprints:
     - `BD` is a 2×1 box bed (Hovel, Tavern F1 room 1), a 1×2 box bed (Cottage) and a 2×2 half-tester (Townhouse F1, Tavern F1 room 2).
     - `TB` is 1×2 (Hovel), 2×1 (Townhouse) and 2×2 (Cottage, Tavern).
     - `PN` covers one cell four times, but its prop is 2×1.
     - `WB` is Workbench_300 (2×1) in one room and Kitchen_Worktable (1×1) in another.
     - `bn` is a 0.48 form or a 1.2 settle. A settle facing the Tavern hearth at (2–3,5) puts its back to the camera and hides the front of the fire.
     - `CT` is a bar counter or a shop counter.
     - `rg` is a Rug_300x200, which is 1.33 cells deep and overlaps the hearthstone in the Cottage and Townhouse.
   - Codes carry no rotation and no backing wall, and they cannot split two identical neighbours into separate instances.
   - The Smithy spawn "Sf on x = 6.0" falls on a node line, which no cell code can express (col 4's centre is 6.75).
   - **Fix:** make `VKI_ROOMS[scene]["props"] = [(piece, c, r, rot, style)]` plus explicit spawn coordinates the source of truth. The ASCII becomes a generated view that `vki_check` compares against. Give each piece its own code (`BX` box bed, `HT` half-tester, `WB` vs `KW`, `FM` form vs `ST` settle), and replace the rug with `Rug_300x150`.

5. **[MEDIUM-HIGH] Part of the scope is missing: workshops, and interiors for most exteriors.**
   - The user scoped "Smithy & workshops", but there is no workshop room. `Workbench_Carpenter` and `PoleLathe` are only P2.
   - The mapping table covers 6 builders. Longhouse, log cabin, woodcutter, forester hut, fisher hut, merchant house, gablefront, corner house, terrace, skyline unit, tower house, pottery, tannery, dyers, brewery, watermill, smokehouse, storehouse, granary, barn and `build_blacksmith` have no interior.
   - **Fix, workshop room:** add `VKI_Workshop_F0`, 6×5, reusing the Stone or Timber shells. Promote Carpenter bench, PoleLathe and GoodsRack to P1, and add crates, sacks and a Hearth_Open. This costs about 3 new props.
   - **Fix, mapping table:**
     - huts and cabins → Hovel;
     - town houses and the tower house → Townhouse;
     - crafts, mills and stores → Workshop;
     - `build_blacksmith` → Smithy.

     Otherwise, state which exteriors are not enterable this round.
   - `build_inn` has 3 storeys but the interior has only F0 and F1. Add this to open question 5 (an attic dormitory F2, or declare it not enterable).

6. **[MEDIUM] On the near wall there is no door to "press a button on", and spawns overlap their triggers.**
   - Every exit is in the south Cut wall. `Door_Cut` is a 1 m gap with no leaf and no frame, but the user said the player "will press a button on the doors".
   - Door trigger y is −0.25…−1.05 and the spawn is at −1.35. With the capsule's 0.3 m radius, the spawn exactly touches the trigger, so the prompt shows on arrival.
   - At Tavern F1, `Ss` (1,6) sits between the stair-down trigger and the x=3.0 partition. It faces "away from the hole", which means facing a wall 0.75 m away.
   - **Fix:**
     - Add `Door_150_CutFrame` per family as the default exit: cut wall plus full-height jambs and lintel inside the surround zone, 0.08 thick. For Ashlar, a pointed DRESS ring. Alternatively use `Leaf_Plank_Cut` ajar at 60°. Decide at the look-test gate.
     - Put the prompt anchor at z 1.4.
     - Spawns go at local y −1.60, and T12 requires every spawn capsule to be at least 0.2 m outside every trigger.
     - Move the Tavern F1 `Ss` to (1,5), facing 0.
     - Give DoorWide its own trigger and spawn defaults: (1.5, −1.6).

7. **[MEDIUM] Tall props and a flue stand in front of windows.**
   - Townhouse F0 `OV` (6,4) sits under north window cell 6, so its flue runs into a window piece. Its `DR` (1,4) is 1.9 m tall in front of window cell 1.
   - The Hovel box bed (3–4,4) covers window cell 3.
   - The Townhouse F1 half-tester canopy runs into window cell 5.
   - The loom stands in front of north windows in the Cottage and Townhouse F1. That is historically right, but the window is lost.
   - **Fix:** Townhouse F0 north wall becomes `+##+##+FF+FF+WW+##+##+` (the kitchen keeps its east window). Hovel window cell 3 becomes `##`. Townhouse F1 window cell 5 becomes `##`.
   - Add a warning to T12: no prop taller than 1.0 m within 0.9 m of a Window or Lancet room face.

8. **[MEDIUM] Mid posts are too dense, and they break the "300 = 150A ⊕ 150B" claim.**
   - The assembler puts a ±0.30 `Post_*_Mid` at every node for Timber, Wattle and Board. On a Timber wall that is a 0.6 m post every 1.5 m plus a stud at every 0.75. About 40% of a cut wall becomes post, and a 1 m wall with posts every 1.5 m reads as a fence, the thing §1 wanted to avoid. The exterior bays (tavern.jpg) are 3 m.
   - Two 150s get a post at their shared node; a 300 does not. Swapping them is visible, which contradicts §2.6.
   - **Fix:** make Mid posts thin (±0.12 in x, proud 0.03) and place them only at even (3 m) nodes along straight runs, whatever the piece split. Bake a half-stud into every piece end so odd nodes show a full stud. Corner posts stay at ±0.30.

9. **[MEDIUM] Rooms will be too dark and low-contrast from above.**
   - BoardsDark (tint .70/.62/.58 on the #74492A midtone) comes out at roughly luma 0.2. That is below the spec's own 0.25 floor minimum.
   - Oak furniture (`M_VK_Wood` is dark red-brown in tavern.jpg) on board floors differs by only about 0.07–0.1, so tables disappear. The Tavern hall is the worst case: BoardsDark floor, Dark wood, Night preset.
   - The Smithy and Cellar use Stone Dark walls with EarthSooty or FlagRustic floors, dark iron and dark casks, all against a #0B0908 void.
   - The Tavern plan places no lighting props at all: no `Lantern_Wall`, `Sconce_Wall` or `Candle_Plate` codes, and TableDress has no candles. At Night only the hearth, at the north wall, emits light; the bar and entrance get nothing.
   - The Night preset keeps 350 W daylight window spots.
   - **Fix:**
     - Tavern hall floor becomes Boards_EW or FlagWarm. Dark wood only on the bar front and casks.
     - Add `M_VKI_WoodScrubbed` (Planks × 1.3) for table, counter and bench tops, and a T12 check that prop tops differ from the floor by at least 0.12 luma.
     - Smithy and Cellar use Stone default or Warm, with a minimum wall luma of 0.35.
     - Tavern gets 4 `Lantern_Wall` (west and east walls, rows 1 and 3), 2 on the back of the bar, and a candle socket in every TableDress_Tavern.
     - Night windows become 60 W cool moonlight; the moon key stays at 0.35 or more.
     - Night render test: mean walkable-floor luma at least 0.15.

10. **[MEDIUM] In follow rooms the far wall is off-screen at the entrance.**
    - At D=18 the top of a 3 m far wall is on screen only when the look-at point is within 3.84 m of it.
    - Tavern F0 (10.5 m deep): at the entrance the target clamps to y=2, and the frame ends at floor y≈10.1. The hearth wall (10.5) is not visible until the player reaches row 4.
    - Chapel: the LancetTall apex (3.90) is visible only when the target is at y ≥ 13.95, i.e. with the player on the dais. The hero element is never seen on entering.
    - **Fix:**
      - Raise the fit threshold to D ≤ 21 (inside the 14–22 zoom range).
      - Make Tavern F0/F1 9×6 by dropping the nearly empty row 1. D_fit becomes about 20.1, and the whole hall, bar and hearth fit one frame at about 100 px/m. Both floors and the cellar offset change together.
      - Follow rooms look 2 m ahead of the player (+Y).
      - The chapel uses D=22 (the apex appears from the target at about y 12). Optionally shorten the chapel to 9 rows.
      - State the camera mode for the Townhouse, Smithy, Cellar and Tavern F1; the spec leaves it unstated.

11. **[MEDIUM] Exterior and interior palettes don't match, and room styles overwrite family materials.**
    - `build_inn` uses ground storey Stone, plaster Ochre and Red shutters. Tavern F0 is Timber with PlasterCream, which fails the spec's own §9.4 pair check.
    - The Townhouse kitchen puts StoneIn inside Timber pieces, so rubble shows between oak studs and sole plates.
    - A room-wide `wall_a` style would also turn the Tavern's Stone `Hearth_300` into plaster.
    - **Fix:**
      - Tavern F0 perimeter becomes Stone (StoneIn Warm, or limewashed with `wall_a=PlasterOchre`). F1 becomes Timber with PlasterOchre, and SHUTTER is Red.
      - The Townhouse kitchen's north and east walls, and the x=7.5 partition, become Stone family with `wall_b=PlasterWhite` on the hall side.
      - Key room styles by family: `styles={"Timber":{…},"Stone":{…}}`.

12. **[MEDIUM] Scope is large for a user who asked not to spend credits unasked.**
    - The spec has about 107 structural masters, about 60 props, 12 texture sets, 9 scenes and 17 automated tests.
    - About 20 masters appear in no plan:
      - Timber and Ashlar DoorWide F/C (4);
      - Stone and Ashlar Niche (2);
      - 7 of the 8 leaves (only Leaf_Plank is used);
      - Stair RailL ×2;
      - Ladder_H24;
      - Bar_Corner_150;
      - Ashlar Post_Mid.
    - **Fix:** this round, build only what the plans place plus the Full/Cut twins.
    - Add a second user gate after one complete vertical slice (the Cottage: shell, props, lighting, links) before fanning out to five packages.
    - Move T5, T16 and T17 to the assembly stage.

13. **[MEDIUM-LOW] Some wall pieces have no Cut version, which goes against "every wall piece comes in two heights".**
    - Fireplace_300, Hearth_300 and Forge_300 name `Plain_150A_Cut` as their cut pair. That is the wrong length; it should be `Plain_300_Cut`.
    - A fireplace toggled onto a near wall loses its fire, which is the gameplay object.
    - Pairs cannot be reciprocal, so T10 fails by construction.
    - **Fix:** add `Fireplace_300_Cut`, `Hearth_300_Cut` and `Forge_300_Cut`, keeping the firebox, hearth and coal bed to 1.0 and cutting the breast and hood. T10 checks reciprocity only for true twins and one-way `cut_to` for the rest. Rakes point to `Plain_150A_Cut`.

14. **[MEDIUM-LOW] Floors, pews and windows will visibly repeat.**
    - World-locked 1.5 m floor tiles repeat every cell, about 168 px on screen. The B/C variants change per piece, so a `Floor_600` repeats one tile 16 times.
    - The chapel has 12 identical Pew_300s.
    - Each family has one window design, repeated 2–3 times per north wall.
    - **Fix:**
      - Paint floors with a 3.0 m period and ship four quadrant variants of `Floor_150`, chosen by node parity; `_300`/`_600` only at even nodes. This keeps UVs world-locked with no shader. Alternatively, the assembler scatters at least 35% B/C cells with no identical neighbours.
      - Two pew variants (poppyhead, wear).
      - Shutter open/closed variants per window.

15. **[MEDIUM-LOW] Furniture in row 0 and the pews read badly from the camera.**
    - Wall-backed props on the south Cut wall face north, away from the camera, and half of them sits in the 0.47–0.86 m hidden strip.
    - Examples:
      - chests in Tavern F1 row 0, Townhouse row 0 and Cottage;
      - straw beds in Hovel row 0;
      - the chapel votive rack `vr` at (5,0), whose candles at about 1.0 m sit level with the cap and disappear.
    - Pews face north. The seat (0.45) lies within 0.42 m behind a 0.95 back, so it is completely hidden and the nave reads as rows of fences.
    - **Fix:**
      - Add R-occ5: within 0.9 m of a Cut wall, only props at most 0.7 m tall that read from their top, or free-standing props with their front to the camera.
      - Move `vr` to a side wall at (6,1).
      - Pew back at most 0.85, raked 10°, with a pale HEWN top rail.
      - In front of hearths, use forms rather than settles.

16. **[LOW] The Cottage box bed is placed side-on.**
    - Bed_Box is defined as 1×2, so its opening faces sideways. At Cottage (5,3)–(5,4) against the east wall, the camera sees its roof and a grazing west face.
    - **Fix:** define Bed_Box as 2×1 with the long side against the wall and the opening to the south, and allow it only against north walls. Cottage bedroom: row 4 `BX BX`, and the dresser moves off the corner (after item 3's resize).

17. **[LOW] Interior doors are narrower than the exterior ones.**
    - The interior door is 0.84 m clear. Exterior doors are wider: the timber leaf is 1.0 (`wall_timber_door`), the stone arch 1.36 (`hw=0.68`) and wattle about 0.9.
    - Interiors may be larger than exteriors, but in this chunky style narrower doors will look pinched.
    - **Fix:** judge it at the look test. The fallback is to use `DoorWide_300_Cut(Frame)` as the default Stone and Ashlar exit, which also matches the chapel's exterior wide door. That door currently cannot be centred on the chapel's one-cell aisle.

18. **[LOW] The Ashlar rake is too steep.**
    - It climbs 1.0 → 4.5 in 1.5 m (67°), slicing through the 1.0 and 3.0 string courses and the cornice.
    - **Fix:** use the full-height post ("proscenium pillar") as the Ashlar default, or add `Rake_300` for Ashlar.

19. **[LOW] Smaller inconsistencies:**
    - §3.1 names `Plain_150A` for Board and Ashlar, but the PKG lists say `Plain_150`. T2's canonical-profile lookup depends on the name.
    - `Floor_Sill_150` runs "along +X", but N–S sills need rot 90 while floors are locked to `world0`. Exempt the sill or add `_NS`.
    - The trapdoor leaf opens toward +Y into the Timber sole plate at Tavern (6,6). Stop it at 80° or offset the hinge by at least 0.35 m.
    - The post family at a family change (Stone hearth in a Timber wall) is unspecified. Use a priority order: Stone > Ashlar > Timber > Wattle > Board.
    - Dice (about 1.7 px at 1080p) should go.
    - TableDress meals must use the goods atlas (a taste note), not flat colours.
    - `SM_VK_Prop_Bellows` is defined twice, by `smith_bellows` in `vk_helpers` and by `ind_bellows` in industry. "Industry version" depends on which builds last. Check the live master before relying on its mount offsets.
    - Board partitions with `wall_a=Plaster*` would give lath-and-plaster partitions. The spec's reason for two thicknesses (a plan-like read) is lost when the Cottage and Townhouse partitions are 0.5 m Timber.
    - Unity: toggling a wall from Cut to Full also has to swap its end posts and the neighbouring rake. Record a `vki_post_rule` now so the later editor tool can do it in one click.

Checked: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\HANDOFF.md`, `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\docs\KIT_README.md`, `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_helpers.py` (L320–338, 1384, 2014–2045, 2139–2185, 3401), `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\modules\vk_mod_industry.py` (L650, 953, 1481), `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\modules\vk_mod_humble.py` (L298), `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\docs\images\tavern.jpg`, `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\docs\images\blacksmith.jpg`.