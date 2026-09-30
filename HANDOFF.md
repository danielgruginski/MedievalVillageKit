# HANDOFF — Medieval Village Kit (state at the end of 2026-09-29)

Read this first when continuing the work (new session: *"Read MedievalVillageKit/HANDOFF.md and continue"*).
Project root: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit` (git repo, branch `main`).
Overview and folder map: [README.md](README.md). Kit reference: [docs/KIT_README.md](docs/KIT_README.md).
Interior kit (built 2026-09-25/26): [docs/INTERIOR_KIT.md](docs/INTERIOR_KIT.md).
Dungeon kit (built 2026-09-29 on the interior kit): [docs/DUNGEON_KIT.md](docs/DUNGEON_KIT.md).
Adventure kit (built 2026-09-29 on the dungeon kit): [docs/ADVENTURE_KIT.md](docs/ADVENTURE_KIT.md).

---

## 1. Working agreements (from the user)

- **Style:** hand-painted, World of Warcraft–like, chunky and slightly irregular; readable from a colony-sim camera
  about 40 m away at 50° pitch. **No LODs.**
- **Terrain is geometry:** marching-squares tiles connected by their corners (dual grid). Fix terrain problems in the
  tiles (e.g. the ramp/cliff transition tile) rather than painting over them; props are fine for hiding texture seams.
- **Blender first, Unity later:** finish the Blender files before exporting. Target Unity project:
  `E:\Unity\Projects\MedievalSetting`. Do not export until the user asks.
- **Verify visually:** after a change, render (`shot()`), look at the PNG, fix what is wrong, then report.
- **Save the .blend** after each completed step (`bpy.ops.wm.save_mainfile()`).
- **The user steers:** finish the task at hand and report; don't start big new directions or spend a lot of
  credits unasked. The user writes English (sometimes Portuguese); answer in their language.
- **Make work visible in Blender:** the user watches changes live in the Blender window. Build in scenes they can
  open, and keep the scene being worked on (or the `Interior_Progress` board) on screen. The user has hit weekly and
  session usage limits during multi-agent work: keep agent counts and review rounds modest.
- Taste notes from feedback: plaster must look even (no repeating decals); broadleaf trees = dense leaf cards, **no
  solid "lump" cores**; cherry blossom foliage in the style of the hero oak's leaves; cobbles sit on a curb with a
  few missing-stone patches; market stalls sell different goods; landmark buildings (smithy, inn) must stand out;
  shutters mostly have fresh paint (about 1 in 5 worn); the user likes Unity-style camera controls
  (`blender_addons/unity_nav.py`, installed).
  More taste notes:
  - Built things look man-made: stairs are one dressed stone throughout (treads too, no cobble), not dirt or cliff rock.
  - Ground textures must read as the material, not grime: a calm base colour with small-scale structure, never big
    dark blotches or thin dark lines that look like hairs. Dirt has pebbles and clods (`gen_dirt_v2`); grass is dense
    painted tufts over darker gaps (`gen_grass_v2`).
  - Cliffs are natural, never trim-like.
  - Small goods (food, hides, fish) are textured from the goods atlas (`M_VK_Goods`, 27 pieces), not flat colours.
    Every fish in the kit is `kit_fish` (core): lofted body, forked tail, dorsal fin.
  - Sharpened stakes (palisades, gate posts and leaves) have pale hewn points (`M_VK_Hewn`, grain up the point) over
    oak bark, with occasional mossy bark: the row of light points must read from the colony camera.
  - Broadleaf foliage (oaks, autumn oak, apple, birches, sapling, and the round/large/berry/autumn bushes) uses sprig
    cells: one twig with separate leaves, like the hero oak's (`SPRIG_CELLS` in `vk_leafgen` / `vk_nature`). Sprig cards
    are narrow (`SPRIG_ASPECT` 0.52) and map the cell's middle band. The old dense twig-bunch cells read as flat mushy
    patches. `broadleaf_dark` is gone: that cell is now `broadleaf_b`, a second, slightly darker green sprig.
    Every sprig grows out of the wood (`sprig_foliage` + `Anchors` in `vk_nature`): a sprig's painted stem starts at the
    bottom of its card, so a card floating in a clump sphere (the old `clump_cards`) showed stems starting in mid-air.
    Now a thin bark twig runs from the nearest branch to where the leaves go and carries the sprigs (tip + fanned side
    sprigs); sprigs point outward tilted 35-60 deg (never tip-on from outside) with their faces turned out; the birch
    hangs its sprigs (droop). Bushes have woody stems from the root crown to each leaf clump (dark bark, seen through
    the gaps); the hydrangea's flower cards stand up (negative droop). Bush sizes were tuned back to about their old
    footprint. The sprig cells are painted from their own rng; the old cell painters only replay their draws (`_burn`),
    so every other atlas cell stays bit-identical.
  - The chapel's dressings (arches, jambs, sills, plinth, cornice, pinnacles, the bell tower's quoins and courses) are a
    warm dark dressed stone (`M_VK_StoneDressed`) against the pale ashlar walls.

## 2. Opening the project

1. Run `open_in_blender.bat` (starts `D:\Program Files\Blender Foundation\Blender 4.4\blender-launcher.exe` with
   `blender\medievalDiorama.blend`). The Blender MCP add-on (`%APPDATA%\Blender Foundation\Blender\4.4\scripts\addons\addon.py`)
   starts its server on port 9876 automatically.
2. Agents drive Blender through the MCP tool `mcp__blender__execute_blender_code`. Every call is a fresh Python
   namespace; calls are serialized (parallel agents share one Blender), so keep each call short. The valley rebuild
   takes 60–90 s, which is fine.
3. The live file is **`blender/medievalDiorama.blend`**. Before 2026-09-23 the working copy was
   `E:\Unity\Projects\Cube Sorter\Art\WallKit\medievalDiorama.blend` (identical at handoff; it and the
   `_backup_before_*` files there are now just old backups).

## 3. How the code works

- The code runs from **Blender texts inside the .blend**. `src/` holds the same texts as files (text name = file
  name): edit the file, then push it with `tools/kit_sync.py`. `status()` shows any drift; `pull()` saves texts edited
  in Blender back to `src/`. At handoff all 26 texts were identical to their files.
- Loader: `exec(bpy.data.texts["vk_kit"].as_string()); g=vk_kit_ns()`. It loads `vk_helpers` (which runs `vk_mat`),
  the 8 `vk_mod_*` modules, `vk_nature`, `vk_terrain` and `vk_terrain_demo`. Exec separately when needed:
  `vk_town_map` (into `g`), `vk_render` (`shot()`), `vk_leafgen` and the texture generators `vk_tex`/`vk_texgen`/`vk_tex2`.
- Everything is rebuilt **in place**: `full_rebuild(names)` for kit pieces, `rebuild_nature(names)` for nature
  (recipes in `NATURE_SPECS`, verified exact), `tk_build_ramps()`/`tk_build_stairs()` for tiles. Instances share the
  master meshes, so they update automatically.
- Interior kit loader: `g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"]()` (the exterior kit
  without terrain, plus every `vki_*` text). Rebuild interior pieces with `vki_rebuild(names)`, rooms with
  `vki_build_scene(name)`; commands and rules in [docs/INTERIOR_KIT.md](docs/INTERIOR_KIT.md) §4.
- Paths in code: `VK_ROOT` in `vk_tex` (textures → `assets/textures`, then packed), `vk_render` (renders →
  `renders/wip`) and `ws_common` (→ `renders/modules`), plus `VKI_ROOT` in `vki_core` (→ `renders/interior`). If the
  project folder moves, change these four lines.
- All kit textures are packed in the .blend; their file paths point to `assets/textures/`.

Common commands: [docs/KIT_README.md §3](docs/KIT_README.md). Quick checks after terrain changes:
`tk_test_T1()` → `[]`; `tk_test_T3(30)` / `tk_test_T3r(30)` → no failures (≈26k / 16k checks);
`tk_test_T4(G, chunks, step=0.25)`: the demo gives 5 known hits, the valley 15. They are grazing rays on near-vertical
relief and talus faces (face normal z between −0.19 and 0), plus the same small downward face on the ramps (open
issue 13: three in the valley, one in the demo).
A first hit with normal z below about −0.2 anywhere else would be a real hole.
Valley build log (`T.log`) known entries: watermill and smokehouse overhang the bank slightly, `WS_skyline_Road`
touches a tower (the road strip is deleted right after). `fix_levels dropped` lists a cart and the creels.

## 4. What exists (state at handoff)

- **Scenes:** `VillageKit` (main), `MedievalColony` (first diorama), `StoneWallKit`, `TreeAsset` (hero oak with LODs
  and impostor, predates the no-LOD rule), `SpriteRig` (from the user's sprite pipeline), `Scene`.
- **Kit (`VK_Pieces`, 417 masters):** core pieces + modules humble, frontier, construction, skyline, town, water,
  industry, defence; town-wall postern; landmarks `build_smithy` (9 m forge stack, glowing hearth, open workshop,
  bellows, tool wall, sign) and `build_inn` (3 storeys, lit windows, tankard sign, ale cask, beer garden); 8 market
  stall trades; lit-window style; worn/fresh shutter styles; roof palette + per-instance brightness jitter.
  Gatehouse (`SM_VK_Gatehouse_*`, sizes in the `GH_*` constants of `vk_mod_defence`): 4 cells wide, 3.5 m passage
  (3.3 m clear between the open leaves), flanking towers at ±4.4 m, portcullis raised to 3.5 m above the road.
- **Nature (`VK_NaturePieces`, 39):** oaks, apple, cherry blossom, birches, willow, pines, dead tree, sapling, bushes,
  plants, mushrooms, rocks, stump, log, pond. Leaf atlas `T_VK_Leaves_*` (cherry cell repainted in hero-oak style).
- **Terrain (`vk_terrain`):** dual-grid marching squares, 3 m cells, 1.5 m levels; cliff/shore tiles with A/B/C
  variants; ramps whose half tile blends the cliff down and has an earth bank (plus `tk_ramp_dress` props); built
  stairs (all dressed stone: treads, risers, flanking walls with sloped copings and piers);
  separate cobble paving mesh with curbs and missing-stone patches (left out where a stair climbs into a cell).
  - `make_displace` (position-only, seam-safe) does all of this:
    - wobbles the contours;
    - gives cliff faces rock relief;
    - makes stacked tiers read as one face: the relief runs through their middle ledges and the upper layer has no skirt;
    - sags the turf lip in patches;
    - bakes rock on middle ledges and eroded lip patches.
  - `tk_cliff_dress` adds boulders, rubble, plants and ledge grass.
  - The cliff texture is `gen_cliff_v2`.
- **Maps:** valley town (`vk_town_map`, 72×56 cells at world 1500,0 — see [docs/VALLEY_MAP.md](docs/VALLEY_MAP.md)) and
  the terrain demo (`vk_terrain_demo`, 32×24 at 1200,0). Both are rebuilt entirely by code.
- **Lighting (renders only):** `VK_Sun` key light + shadowless `VK_Fill`.
- **Interior kit (`VKI_Pieces`, 146 masters; see [docs/INTERIOR_KIT.md](docs/INTERIOR_KIT.md)):** modular interiors
  for a top-down camera (pitch 50°) on a 1.5 m grid, every wall in Full and 1 m Cut heights. Wall families Timber,
  Stone, Board, Wattle, Ashlar with posts, rakes, windows, doors, wide doors and the fireplace / hearth / forge
  specials; floors with 3 m texture parity; door leaves, aprons, overlays; up/down stairs as scene links; 23 home,
  18 tavern and smithy, and 7 chapel props; 16 interior texture sets (`T_VKI_*`). Nine showcase scenes, one per floor:
  `VKI_Hovel_F0`, `VKI_Cottage_F0`, `VKI_Townhouse_F0/F1`, `VKI_Tavern_F0/F1`, `VKI_Smithy_F0`, `VKI_Workshop_F0`,
  `VKI_Chapel_F0`, rebuilt by `vki_rooms` (`vki_check` gives 0 errors in all nine). Viewer scenes: `VKI_Catalog`
  (every piece, a camera per group) and `Interior_Progress` (a live board of all rooms and workshops). Every piece
  passes `vki_test_pieces`; the exterior is untouched (T15).
- **Dungeon kit (46 more masters in `VKI_Pieces`, 194 in all; see [docs/DUNGEON_KIT.md](docs/DUNGEON_KIT.md)):** the interior
  kit's framework with two new wall families: Dungeon (dark coursed masonry, damp band, light grates, ossuary niches) and
  Bars (iron cell fronts, barred gates, never cut). Iron and gate leaves, stone stairs, 14 props, 5 overlays, the
  `Dungeon` lighting preset (torch-lit, floor target 0.15) and two linked levels: `VKI_Dungeon_B1` (gaol, stair up to
  `@return`) and `VKI_Dungeon_B2` (crypt). Both pass `vki_check` with 0 errors. `vki_test_all()` is clean for all 194
  masters. The nine interiors rebuild unchanged. Viewer scene: `VKI_Dungeon_Catalog`. The workshop scene `WS_vki_dungeon`
  still holds the first piece rows (its masters were adopted into `VKI_Pieces`).
- **Adventure kit (331 more masters, 525 in all; see [docs/ADVENTURE_KIT.md](docs/ADVENTURE_KIT.md)):** the dungeon
  kit widened to adventuring places, all four themes the user chose: traps and mechanisms, ancient ruins, monster
  lairs, caves. The Ancient wall family (sunken-temple blocks, frieze, trilithon doors, broken / collapsed walls,
  relief, vault) and the Cave wall family (rock walls for walled levels, `vki_fam_cavewall`). **Organic caves** (the
  user asked for them after the first try, the rock-textured walls, which stay as the Cave family): a cave level is a
  cell map, and 49 dual-grid rock tiles (class `rock`, 23 corner codes O / C / F, 2-3 variants, a tunnel tile) give it
  curving outlines, spurs, bays, pillars, leaning cliffs, ragged tops; rock is Cut where it would hide floor from the
  camera. **A winding chasm** (the user found the straight chasm too linear): chasm cells are painted too, and 57
  dual-grid ground tiles (class `ground`, X / O codes, never rotated, four node parities for the world-locked floor)
  carry the floor with the hole cut in curves; Floor_075 quarters fill part-covered cells; a standalone rope bridge
  (`vki_bridge` deck: the BFS crosses the chasm there). Rock texture from `vki_gen_rockface`. A `pit` class (spike
  pit, straight chasm segments, pool). Passages and tunnels (scene links), named plan pieces, door leaves (portcullis,
  rolling vault disc, secret door, locked iron door), 51 props / overlays, the `Cavern` preset. Three more levels
  continue the descent from B2 through a breach: `VKI_Dungeon_B3` (sunken temple, walls), `B4` (caverns, 12 x 7: the
  winding chasm and bridge) and `B5` (goblin warren) as cave maps. **Transitions** (the user asked for "walls that
  break into caves"): walls may be drawn inside a cave map (partition family, `vki_cave_walls`); 115 wall-backed rock
  tiles (`Rock_Cave_<code>_Wall<arms>`) keep the rock 0.33 m off a wall on the node lines; breaches knocked through
  to the floor (`Wall_<Dungeon|Ancient>_Breach_150/300`, Full and Cut, plan tokens `XX` / `X`, `xx` / `x`);
  `Overlay_Spill` for floor seams. Demo `VKI_Cave_Breach` (0 errors, 0 warnings). **Cave generator**
  `vki_cave_generate` (the user asked for a larger cave spawned as a map): `VKI_Cave_Test`, 24 x 16, seed 7, 0
  errors. All five levels pass `vki_check` with 0 errors; `vki_test_all()` is clean for 525 masters; the nine
  interiors still check at 0 errors. Viewer scene: `VKI_Adventure_Catalog` (26 groups). The workshop scene
  `WS_vki_adventure` is empty.
- **Sewer kit (30 more masters, 555 in all; see [docs/SEWER_KIT.md](docs/SEWER_KIT.md)):** the user asked for "some
  sewers, including the transitions". A sewer level is a cave map: rock between the tunnels, brick walls (the Sewer
  family, `vki_fam_sewer`) on the inner grid lines backed by wall-backed rock tiles, channels painted `ww` and built
  from five dual-grid channel tiles (class `ground`, rotated, no floor: `vki_covers_floor` lists their X quarters),
  culverts where a channel passes under a wall, an outfall, a sluice, slab bridges (`vki_bridge` decks), a ladder link,
  sewer breaches into caves. Textures `T_VKI_SewerBrick` / `T_VKI_SewerFloor`, the `Sewer` preset. Level
  `VKI_Sewer_S1` (0 errors, 0 warnings); every other level still checks at 0 errors.
- **Water kit (61 more masters, 616 in all; see [docs/WATER_KIT.md](docs/WATER_KIT.md)):** the user asked for
  "natural water, streams and waterfalls", the animation and shaders to be done in Unity. Streams are painted `ss` in a
  cave map: 57 dual-grid stream tiles (class `ground`, like the chasm's: sloping banks, a bed at -0.45, clear water at
  -0.22, soft colliders). A stream meeting the chasm pours in (the chasm's tiles take the shared nodes and the
  assembler adds `Prop_Waterfall_Chasm`); springs fall from rock faces (`Prop_Waterfall_Rock` / `_RockLow`); stepping
  stones cross. Every stream and sewer-channel tile carries `vki_flow` (a BFS from the sinks) and the falls `vki_fx`
  sockets for Unity. Level `VKI_Cave_Falls` (0 errors, 0 warnings). The user's next asks: dwarven halls, mines, the
  connection to the town.
- **Dwarf kit (35 more masters, 651 in all; see [docs/DWARF_KIT.md](docs/DWARF_KIT.md)):** dwarven halls cut into the
  mountain (a cave map with Dwarf walls backed by the rock): the Dwarf family (granite ashlar, plinth and gilded rune
  band on both faces, corbelled doors, the great gate + `Leaf_DwarfGate_300`, passage, posts, breaches), lava channels
  (`ll` cells: the sewer's channel tiles with emissive lava, `R["lava_sinks"]`), pillars, a throne, king statues,
  braziers, a forge, an anvil, a stone arch bridge, a gold floor medallion; the warm `Hall` preset. Level
  `VKI_Dwarf_Hall` (0 errors, 0 warnings). Next in the user's queue: mines, then the connection to the town.
- **Critique round on the dwarven halls (2026-09-30; the user: "criticize, then improve it"; DWARF_KIT section 6).**
  - **Open bottoms.** The rock, chasm and stream tiles no longer close their solids underneath (`bottom=False`,
    `vki_open_bottom`, T7's exemption): 278 masters, 88,468 → 65,218 triangles; every cave level is 18–30 % lighter.
  - **Lava.** Dark scorched kerbs, a heat gradient on the surface (the material kind `heat`, `vki_rim` for Unity),
    crust against the banks.
  - **Floor.** A checkered runner up the aisle and plain granite flags elsewhere (`T_VKI_DwarfFlag`).
  - **Rooms and dressing.** A treasury in the south band, red clan banners (`Prop_Banner_Dwarf`, the 36th master),
    richer king statues, vestibule braziers.
  - **Light.** A cooler Hall key of the same luminance, so the fires' warm pools read.
  - **Result.** The hall: 0 errors, 0 warnings, 98,700 triangles.
- **Points of interest (6 masters, 658 in all; see [docs/POINTS_OF_INTEREST.md](docs/POINTS_OF_INTEREST.md)).** The
  user asked for "points of interests (a single asset that is more interesting, not expected to be repeated many
  times over a level)", after asking whether there were enough assets for larger levels.
  - **The pieces** (`vki_props_poi`, hero tier, 1,612–3,318 triangles each), each with a `vki_poi` record for the game:
    the wyrm's bones (caves), the fallen king's head (ruins), the great crucible (dwarf), the necromancer's circle
    (dungeon), the rat king's throne (sewers), the sacred spring (water).
  - **Placement.** Each is placed once: the crucible in the hall's enlarged foundry, the circle in B2's nave, the head
    in `VKI_Cave_Breach`, the throne in `VKI_Sewer_S1`, the spring in `VKI_Cave_Falls`. The cave generator places the
    wyrm (its new `poi` option) in `VKI_Cave_Test`. All check at 0 errors.
  - **Larger levels (the user's question).** The tilesets are size-independent and the follow camera handles big maps.
    What bites at scale: one variant per tile class (repetition), hand-drawn plans (only caves have a generator), the
    rock mass's triangles, and no height changes inside a level.
- **Debris (20 masters, 678 in all; see [docs/DEBRIS.md](docs/DEBRIS.md)).** The user: "we need more debris, things
  like loose rocks, broken vases, things that add flavor to the environment".
  - **The pieces** (`vki_props_debris`): walkable overlays of 96–372 triangles. Loose rocks, a rubble heap, broken
    pottery (a jar broken open, a toppled amphora, shards, a pot pile), planks, a smashed crate, a broken barrel,
    fallen masonry, lost weapons, a cold campfire, broken stalactites, ore, slag, a torn sack, rags. Stone pieces take
    the level's stone (CAP-slot variants); old iron is rust (`M_VKI_Rust`).
  - **The scatter** (`vki_rooms_debris`, run by `vki_build_scene` from `R["debris"]`): themed by each zone's floor
    style, clear of structure, props, use points, spawns and water. Heavy stone gathers at walls' and rock faces' feet.
  - **Result.** Ten adventure levels carry 15–32 pieces each (the generated cave 79), at 0 errors and with no new
    warnings.
- **Mines (35 masters, 713 in all; see [docs/MINE_KIT.md](docs/MINE_KIT.md)).** The user: "start the mines" (next in
  his queue after the dwarven halls; the connection to the town comes after).
  - **The pieces** (`vki_fam_mine`):
    - track tiles (overlays), laid from polylines by `vki_mine_tracks` (`R["tracks"]`; turntables at junctions,
      "open" ends run on into an adit);
    - carts (empty, ore, tipped);
    - timber sets (plain, lamp, broken);
    - veins (gold, iron, crystal: seam ribbons over rock lumps);
    - `Pit_Shaft_300x300`, and `POI_Treadwheel` (the mine's point of interest: headframe, cage, a great treadwheel;
      it carries the lift link);
    - eight props and two debris pieces;
    - the adit (`Rock_Cave_OOFF_Adit`, `R["tunnel_kinds"]`).
  - **Framework hooks.**
    - `vki_rooms_prop_link`: any prop can carry a scene link, via the props option `{"link": id}`.
    - A tunnel dict in `vki_cav_tile`. The natural tunnel is unchanged.
    - The track hook in `vki_cave_layout`.
    - The Mine preset, `M_VKI_MineWood`, `M_VKI_Quartz`, `M_VKI_IronOre`.
    - The debris "mine" theme.
  - **The level** `VKI_Mine_M1` (22 × 13):
    - the haulage gallery from the adit (`@surface`, for the town) to the tunnel back to `VKI_Dwarf_Hall` (whose
      "mines" link now targets it);
    - the gold stope and a caved-in drift;
    - the shaft chamber with the treadwheel (the lift to `@deep`);
    - the iron drift, the crystal cave, the miners' store.

    0 errors, 0 warnings, 94,140 triangles.
  - **Critiqued before handing over.** Head boards across the sets' caps read as ladder rungs from the game camera
    (removed). Seams painted on the veins' faces read as teeth (now ribbons). The shaft chamber's south half was bare
    (ore pile, tool rack, spare sleepers).
  - **Timber lining** (the user asked whether timber-lined galleries would be too complicated, then: "ok, we can build
    it").
    - **The family.** A Mine wall family (8 masters): lagging boards on both faces of a packed-rock core, a wale that is
      the Cut wall's cap, a wall plate, crib corners, hewn Mid posts.
    - **Where it goes.** It is drawn on the cave map's inner grid lines, so the rock tiles behind become wall-backed.
      Heights follow the rock behind: Cut mostly, Full where the rock is Full.
    - **In `VKI_Mine_M1`.** The gallery, the drift mouths and the iron drift are lined: 32 walls, 35 posts. The level
      is still 0 errors, 0 warnings, and has 98,398 triangles (+4.3k).
    - **Looks.** The first boards (dark oak) read as black panels, and square corner posts as stumps. Now: hewn boards
      darkened a board at a time, on the SHUTTER slot for the grain, and cribs.

## 5. Open issues and ideas (none started unless marked done)

1. ~~Gatehouse passage is only ~2.1 m clear.~~ Done 2026-09-24: the block is 4 cells wide and the towers stand clear
   of the passage (ray casts: ≥ 3.34 m clear at every height, 3.5 m headroom under the portcullis). The gate apron is
   now cols 39–44, so the construction sites moved 3 m east.
2. ~~A smithy crate touches the gatehouse.~~ Done 2026-09-24: `town_inside` moves it to the yard by the wall, next to
   the woodpile. Also fixed: `town_fix_levels` had dropped the hanging `SM_VK_Prop_SmithSign` on every build (its
   height read as level 4); it is now in `WALL_MOUNTED`.
3. ~~River's west end is open at the map edge; the lake reads as a rounded rectangle.~~ Done 2026-09-24: the river
   rises from a spring pool a few cells in from the west edge (`town_spring` dresses it), and the lake has an irregular
   outline (`_blob` in `town_grid`). No water touches the map border any more; the rest of the border is still a
   thin sheet (a closed diorama edge was offered and not chosen).
4. ~~Worn-ground pads follow cell squares.~~ Done 2026-09-24: the ground-control map has 5 texels per cell and wear is
   painted from soft marks (`TGrid.wear_marks`). The old per-cell wear (0.35–0.39) was also below the dirt layer's
   0.45 threshold, so it hardly showed; the marks are 0.8–0.85. Wall-walk and upper-storey doors no longer get a
   worn patch on the ground below them.
5. Fishmonger's ice tray reads very white from above.
6. ~~Stairs in the open have no transition tile yet (they use `SM_VKT_RampShoulder` rocks). Stairs on cobble have
   plain dressed-stone side walls.~~ Done 2026-09-24: the half-stair tile builds flanking walls (sloped coping, a pier
   where the cliff meets the flight, a kerb up top) on grass and cobble alike; the rock shoulders and
   `SM_VKT_RampShoulder` are gone. T1/T3/T3r pass and T4 keeps its known hits.
7. ~~Cliffs seen head-on read as a band with a straight toe line; mossy middle ledges show as a green line from
   above.~~ Done 2026-09-24: `make_displace` flares the foot of each cliff into a talus whose size wanders along the run
   (turf climbs it up to ~0.7 m, the shader picks turf or rock by slope), and up-facing rock gets top-projected rock
   with moss only in patches. Still open: the cliff texture's painted grass tufts look flat on vertical faces.
8. The old small `build_blacksmith` is no longer placed (the landmark smithy replaced it); the skyline street still
   has a small smithy house.
9. Willow slightly wispy from above; a few pine bark flecks at distance.
10. Watermill and smokehouse overhang the river bank by ~0.5 m.
11. Unity export (when asked): strip unused material slots, no mesh compression on terrain tiles, import normals,
    drive the ground-type map from cell data, replace the Object-Info roof jitter.
12. `E:\Unity\Projects\GameArtGeneration\unity\DualGridTerrain` exists in the parent folder (not inspected) — may be
    relevant to the terrain export.
13. Ramp tops have a small face pointing down, coincident with the ramp surface. `tk_test_T4` flags it at three valley
    ramps and one demo ramp (earth ramps only: the walled road ramps don't use `ramp_blend_shoulder`, which confirms
    the fault is there).

Interior kit (spec: `docs/history/interior_design/INTERIOR_SPEC.md`, its §10–§11 record the changes made while building):

14. Floor light levels below the spec's targets in three rooms: Townhouse_F1 0.187 and Smithy 0.221 by Day (target
    0.25), Tavern_F1 0.114 by Night (target 0.15). Dark floors by design (Boards_NS, EarthSooty, a night guest floor);
    lift them with paler floor styles or more lights if wanted. Unity lighting will be set up separately.
15. `vki_check` palette warnings where caps are dark stone by design: the Ashlar chapel (Dress caps), the Stone
    townhouse, the tavern at night. A pale `cap` style would make the room outline read more.
16. The Night style maps the unglazed Wattle window's daylight card to the glass texture `M_VKI_Window_Night`; it should
    be a flat night-sky emissive (matters only if a Wattle room is ever lit for Night).
17. Not built yet: §5 P2/P3 props (home P2, tavern P2/P3 such as stillage, back bar, chandelier; chapel P2/P3), a
    cellar, trapdoor and ladder, a cottage loft, the Log wall family, Slit/Niche windows, Timber/Board wide doors.
18. The exterior smithy's only door is blocked by its forge chimney (found while designing the interiors). Move the door
    to bay 1 (`front="WD"`) or fix it with the export.
19. Unity export of interiors (when asked): the metadata is in place (INTERIOR_KIT §2). It needs an importer for the
    link triggers, spawns, `LGT_`/`FXA_` empties and colliders, the glow gradient `vki_rim` baked to UV2 or `Col.a`, and
    a Full↔Cut toggle tool using `vki_cut_pair` / `vki_cut_to`.
20. `M_VKI_WoodScrubbed` renders at floor luma; the home props use pale hewn tops instead, the tavern bar and tables
    still use it.
21. Open questions from the spec for the user: live 3D characters or sprites (the sprite pitch must then match 50°);
    fixed camera yaw and the 14–22 m zoom range; AgX vs Standard for interiors; which buildings are enterable (the §6
    mapping leaves out barns, granaries, stables, the town hall and the inn's third storey).
22. ~~The weapon rack's spear and axe heads floated ~0.2 m behind their shafts~~ (seen in the interior smithy). Done
    2026-09-26: `prop_weaponrack` leans the shafts back against the top rail with their feet on the ground, seats each
    head on its shaft and turns the axe blades sideways; the exterior racks update too.
23. Solid viewport colours: flat-colour materials (coal, leather, steel, bronze, food…) showed white in Solid/Texture
    view. Their viewport colours (`diffuse_color`, display only) now match their base colours; use Material Preview to
    judge materials.
24. ~~The industry bellows (`SM_VK_Prop_Bellows`, also used in the interior smithy) was a stack of pale hide wedges on
    a plank.~~ Done 2026-09-26: `ind_bellows` builds a forge bellows: teardrop boards (the top one hinged and lifted),
    a pleated leather bag, iron straps, a pump pole with a cross handle, a trestle, and a long iron pipe (tip at local
    x −1.50) that stops 2.5 cm short of the Smithy forge's tuyere. The exterior bloomery uses the same piece.

Dungeon kit (2026-09-29; details in docs/DUNGEON_KIT.md):

25. `vki_check` warnings left in the two levels:
    - Palette: cap tops sit just under floor + 0.15 (0.300 vs 0.308 in B1, 0.293 vs 0.304 in B2). The caps are a
      tinted `T_VKI_StoneBlockIn` (`M_VKI_DungeonCap`), already lifted 1.16x; lift further or accept.
    - B1 has R-occ5 notes: chains, a torch and the skeleton stand within 0.9 m of the Cut cell partitions.
    - B2's stair is let into a Plain_150B pop-out. The assembler picks the B variant without checking stairs.
    - 2026-09-29 (adventure kit): B2 lost its east-wall torch to the breach on to B3; floor candles by the breach keep
      its floor at 0.156. Its cap tops now sit at 0.291 vs 0.306.
26. From the game camera:
    - The wall chains read weakly (dark iron on dark stone).
    - The down stair's steps are hard to see in the dark shaft; paler treads or a faint light at the bottom would help.
    - The puddles (`M_VKI_Puddle`, a 55 % glossy film) read as dark wet patches, with few highlights.
27. Not built yet:
    - ~~a portcullis leaf for `DoorWide_300`~~ (adventure kit: `Leaf_Portcullis_300`);
    - ~~cobwebs (for spider lairs, Insectoids)~~ (adventure kit: `Prop_Web_Corner`, `Overlay_WebFloor`);
    - stocks or a rack;
    - ~~a rough rock / cave wall family~~ (adventure kit: the Cave family);
    - ~~goblin-lair dressing (bedrolls, totems)~~ (adventure kit: `vki_props_lair`);
    - an exterior entrance (cellar stair, crypt door).
    `@return` sends the player back to wherever the game entered the dungeon.
28. Unity export (issue 19) also needs:
    - the `vki_see_through` flag: bars, gates and the cage don't block sight lines;
    - `vki_no_cut` on the Bars pieces;
    - the gloss puddle material;
    - the grate's SPOT, which sits inside the opening.

Adventure kit (2026-09-29; details in docs/ADVENTURE_KIT.md):

29. Cave maps: openings between rock must be two cells wide -- the rock's lobes and foot take up to ~0.6 m off each
    side, and a one-cell gap closed below the 0.6 m walker (B4's first spur and pillar, B5's first chambers). Props
    near rock stand off it with the hug off (`{"hug": False}`; there are no walls to hug); webs, the cocoon and the
    rat hole carry `vki_wall_anchor` and may enter rock. Rock colliders are the floor-level footprint in 0.25 m boxes;
    a game with tight collision should use the mesh. Rock UVs turn at tile edges (rotated instances): a triplanar rock
    shader in Unity would hide the seams. The first cave try (the Cave wall family: bulging faces, a ragged skyline)
    was not organic enough for cave levels; it stays for walled levels (the user asked to keep pieces unless they
    clash with the new ones).
30. N-S doors read edge-on from the fixed camera (B3's portcullis and vault disc). The vault door faces east because a
    Full front wall hid the loot (T19); the vault's south side is a Cut wall.
31. Chasms: the cave maps use the ground tiles (curving; they end in a rounded tip or under the rock); the straight
    `Pit_Chasm` segments stay for walled levels and have open ends (run them wall to wall). Ground tiles are never
    rotated (world-locked floor: four parity versions per code); a pit must keep a cell clear of the chasm; the rope
    bridge needs the chasm two cells wide and a cell-centre column.
32. Not in a level yet: `Wall_Dungeon_Secret_150_Full` + `Leaf_SecretStone_Full`, `Leaf_Iron_Full`. They are in the
    catalog.
33. Unity export (issue 19) also needs: the `pit` class (floor replaced over `vki_covers_floor`, never rotated), the
    `rock` class (dual-grid tiles on nodes, rotated), the `ground` class (dual-grid chasm tiles on nodes, never
    rotated) and the Floor_075 quarters, the bridge deck (`vki_bridge`), the passage and tunnel links (`vki_link`
    passage, `vki_target`), `vki_trap` / `vki_mechanism` / `vki_openable` /
    `vki_leaf_motion` for gameplay, the web card material (alpha clip) and the `Cavern` preset.
34. Transitions: walls in a cave map go on its inner grid lines only, never between two rock cells (an error); the
    rock tiles on their nodes are the wall-backed ones (`vki_wall_arms`), picked by `vki_cave_tiles`. A breach in an
    N-S wall is hidden from the game camera by the wall south of it; put the one that should be seen in an E-W wall.
    The generated test cave (`VKI_Cave_Test`) is rebuilt from `scene["vki_generated"]` in a fresh namespace.
35. Sewers: channel water darker than `M_VKI_SewerWater` read as holes in the floor; the channel tiles' water
    surface must keep vki_dark 0 (the slime darkening multiplies the material). The doorway rush mats are off in the
    sewers (`R["rush_mats"] = False`).
36. Water: a stream may meet the chasm (it pours in) and rock (it runs under), not a pit, a sewer channel or another
    water type at one node. A chasm fall facing east or west is edge-on to the game camera. Streams are one level
    (-0.22); height changes only at waterfalls. Unity: water tiles carry `vki_flow` (world x / y), falls `vki_fx`
    (`waterfall`, `mist`); the static sheets are placeholders for a scrolling waterfall shader.
37. Dwarf halls: keep the rows round a lava channel's ends clear (a brazier or statue there cut the walkways off). The
    lava is a pure emitter on a heat gradient (a lit base read pink; cores brighter than 1.25 went peach under AgX).
    The pale dwarf floors are tinted 0.56 for the palette rule. Solid rock is still the largest part of a mountain
    level (a third of VKI_Dwarf_Hall); a cheap solid-rock filler tile would help deep mountain. A Full N-S wall hides a
    strip east of it from the game camera (the foundry's west side): keep use points out of it.
38. Points of interest: one per level; a POI's tall parts carry `vki_cam_fade` (R-occ3). Each has one variant; a level
    wanting two of a theme needs a second design. The catalog's POI row (`G33`) is tight and its title overlaps the
    wyrm's skull. Unity: `vki_poi` (name, kind, theme, interact), the crucible's molten metal carries `vki_rim` like
    the lava, and a light may carry `specular` 0 (diffuse only).
39. `VKI_Cave_Test` keeps one warning, its floor mean (0.130) under the dark target 0.15: the generated cave has few
    light sources for its size (from its first build). The generator could scale its crystals and mushrooms with the
    map's area.
40. Debris is decorative (walk-through, no collider) and scattered at build time; a level's pieces change with its
    seed or its layout. Density is what a zone asks for: crowded zones place fewer (a piece needs its footprint clear).
    Unity may keep the placements or rerun the rules (DEBRIS.md section 4). Not built: wall-hung debris (hanging
    chains, more cobwebs, roots) and a second variant per piece.
41. Mines: one level at one height. The shaft and the adit are links, so there are no inclines or winzes inside a
    level. The timber lining (the Mine wall family) has no doorway, rake or damaged variant, and its height must follow
    the rock behind it (Cut where the rock is Cut). Veins read best on north faces: the iron vein on the drift's east
    end reads side-on. The barricade across an E-W drift is seen edge-on. Unity: `vki_track` (conn bits turned by the
    tile's rotation give the cart graph), link kind "lift" (new), `vki_lift`, `vki_vein`, `vki_cart`. The treadwheel
    is one mesh (split it to animate). The adit `@surface` is where the town connection plugs in.
42. T19 checks a follow-mode level from one camera over its centre, so tall props near the level's ends (the timber
    sets by the mine's tunnels) can hide a spawn or trigger they would not hide in play. `VKI_Mine_M1` moved its sets
    off those rays; a follow grid of cameras (`vki_t19_visibility` accepts several) would test what the game sees.

## 6. Gotchas

- **Python on this machine:** `python` resolves to the Python install manager, a *packaged* app. Inside `%APPDATA%`
  it sees a virtualized file view (it cannot see folders other programs created). For file work under `AppData`,
  use PowerShell or Blender's Python. The project on `E:` is not affected.
- Blender inherits the working directory it was launched from; a Blender started from a folder keeps it locked
  (`os.chdir` in Blender to release it).
- Blender's BOX image projection rotates the texture on X-facing faces; the terrain uses its own biplanar
  `side_sample` instead.
- `Mesh.materials.clear()` resets every face's material index to 0. Fill the material slots first, then write the
  indices. Doing it the other way round had hidden the stair and curb materials behind the terrain material.
- Never `raise SystemExit` in code run through MCP. Don't keep references to objects/bmesh elements you delete in
  the same call (`StructRNA ... removed` / `BMesh data ... removed`).
- **Creating an icosphere invalidates BMVert references held from before it** (`bmesh.ops.create_icosphere`, so
  `_ico` / `vki_home_ico`). A `set(k.bm.verts)` taken before it no longer matches the verts after it: "the verts added
  since" then returns every vert, and a transform meant for one part moves the whole master (the spring's basin took
  its spout's tilt). Build parts with icospheres first, or transform them the moment they exist, and measure
  colliders at once (`vki_props_poi`).
- `vk_tex` creates `TEXDIR` when executed; generated textures are saved there *and* packed.
- The valley generator deletes and rebuilds `VK_ValleyTown` / `VK_ValleyTerrain` completely: never hand-edit them;
  change the code instead.
- **Never publish the .blend as-is:** its `SpriteRig` scene holds third-party character assets. The repo is public;
  keep the .blend, renders and anything from that scene out of git.
- Blender cannot create folders under the long scratchpad path (Windows `MAX_PATH`); render into `renders/` instead.
- **Blender 4.4 crashes when scripts delete objects in scenes that are not on screen.** Its GPU-buffer garbage
  collector (`DRW_cache_free_old_batches`) walks every scene's depsgraph, and a stale one still points at the deleted
  objects (access violation; logs in `%TEMP%\medievalDiorama.crash.txt`). It crashed three times on 2026-09-26 while
  six agents built interiors in parallel. Fix: `bpy.context.preferences.system.vbo_time_out = 0` (the collector then
  returns at once). Launch with it set from the first second:
  `blender-launcher.exe "…\blender\medievalDiorama.blend" --python-expr "import bpy; bpy.context.preferences.system.vbo_time_out = 0"`
  from Blender's own folder. The preference is 0 in the current session (the default is 120).
- After a restart, a scene that is not on screen has no depsgraph (`view_layers[0].depsgraph` is `None`) until
  `view_layers[0].update()` evaluates it; `vki_depsgraph` and `vki_flush_lights` handle this.
- Parallel agents on one Blender: each owns its texts and its `WS_vki_<name>` scene, compiles every file before
  pushing (`vki_ns` skips a broken package text but raises on core texts), and only the coordinator saves.
- The `Interior_Progress` board shows collection instances refreshed by a 60 s timer
  (`bpy.app.driver_namespace["ip_tick"]`). The timer is lost when Blender restarts; re-register it or open the room
  scenes directly.
- README gallery: `tools/render_showcase.py` → `render_showcase()` re-renders `docs/images/*.jpg` (cameras in
  `SHOWCASE`); rebuild the valley and the demo first.

## 7. History (where the details are)

- `archive/script_logs/` — every script run in Blender during the build (main session + all agents), chronological,
  with results. Start at its `INDEX.md`.
- `reviews/` — the two valley reviews (33 confirmed issues, then the re-review) and the module-build agent reports.
- `docs/history/` — design briefs, specs and design-panel outputs from the expansion phase.
- `docs/history/interior_design/` — the interior kit: spec (with the §10–§11 amendments), design-panel surveys and
  critiques, the package briefs (`PACKAGES.md`) and the core API notes the builders used.
- `renders/` — every render made, by topic; `renders/final/` has the latest verification shots.
