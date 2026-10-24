# HANDOFF — Medieval Village Kit (state at the end of 2026-09-29)

Read this first when continuing the work (new session: *"Read MedievalVillageKit/HANDOFF.md and continue"*).
Project root: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit` (git repo, branch `main`).
Overview and folder map: [README.md](README.md). Kit reference: [docs/KIT_README.md](docs/KIT_README.md).
Interior kit (built 2026-09-25/26): [docs/INTERIOR_KIT.md](docs/INTERIOR_KIT.md).
Dungeon kit (built 2026-09-29 on the interior kit): [docs/DUNGEON_KIT.md](docs/DUNGEON_KIT.md).
Adventure kit (built 2026-09-29 on the dungeon kit): [docs/ADVENTURE_KIT.md](docs/ADVENTURE_KIT.md).
The town connection, the world graph (2026-09-30): [docs/WORLD_GRAPH.md](docs/WORLD_GRAPH.md).
Unity export (vertical slice, 2026-09-30): [docs/UNITY_EXPORT.md](docs/UNITY_EXPORT.md).
Godot export (pilot, 2026-10-24, entries 143 and 145): [docs/GODOT_EXPORT.md](docs/GODOT_EXPORT.md); the full port
(a Godot kit with everything the Unity kit has, the Unity kit completed from the game): [docs/FULL_PORT_PLAN.md](docs/FULL_PORT_PLAN.md).
Animated units (the siege catapult, 2026-10-23, entries 140-141): [docs/UNITS.md](docs/UNITS.md).

---

## 1. Working agreements (from the user)

- **Style:** hand-painted, World of Warcraft–like, chunky and slightly irregular; readable from a colony-sim camera
  about 40 m away at 50° pitch. **No LODs.**
- **Terrain is geometry:** marching-squares tiles connected by their corners (dual grid). Fix terrain problems in the
  tiles (e.g. the ramp/cliff transition tile) rather than painting over them; props are fine for hiding texture seams.
- **Blender first, Unity later:** finish the Blender files before exporting. Target Unity project:
  `E:\Unity\Projects\MedievalSetting`. Export started 2026-09-30 at the user's request (docs/UNITY_EXPORT.md).
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
  the 9 `vk_mod_*` modules, `vk_nature`, `vk_terrain` and `vk_terrain_demo`. Exec separately when needed:
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
- **Kit (`VK_Pieces`, 421 masters):** core pieces + modules humble, frontier, construction, skyline, town, water,
  industry, defence, entrances (the valley's ways underground); town-wall postern; landmarks `build_smithy` (9 m forge stack, glowing hearth, open workshop,
  bellows, tool wall, sign) and `build_inn` (3 storeys, lit windows, tankard sign, ale cask, beer garden); 8 market
  stall trades; lit-window style; worn/fresh shutter styles; roof palette + per-instance brightness jitter.
  Gatehouse (`SM_VK_Gatehouse_*`, sizes in the `GH_*` constants of `vk_mod_defence`): 4 cells wide, 3.5 m passage
  (3.3 m clear between the open leaves), flanking towers at ±4.4 m, portcullis raised to 3.5 m above the road.
- **Nature (`VK_NaturePieces`, 40):** oaks, apple, cherry blossom, birches, willow, pines, dead tree, sapling, bushes,
  plants, mushrooms, rocks, stump, log, pond. Leaf atlas `T_VK_Leaves_*` (cherry cell repainted in hero-oak style).
  Wild garlic (`SM_VK_Plant_WildGarlic`, 2026-10-03, the RPG's gatherable herb): geometry leaves folded along the
  midrib and white star-flower umbels on its own small sheet `T_VK_WildGarlic` (`vk_leafgen.paint_wild_garlic`),
  material slot `WILD_GARLIC` (`M_VK_WildGarlic`, the leaves' shader), not a cell of the full leaf atlas.
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
- **The town connection (4 exterior masters, 421 in `VK_Pieces`; see [docs/WORLD_GRAPH.md](docs/WORLD_GRAPH.md)).** The
  user: "start the connection to the town" (last in his queue after the dwarven halls and the mines).
  - **Five ways down from the valley** (`vk_mod_entrances`, placed by `vk_town_map`):
    - the mine portal (existing) → `VKI_Mine_M1`;
    - the dwarves' gate, a corbelled doorway in a crag on the west bench beside the mine → `VKI_Dwarf_Hall`;
    - the spring cave at the river's head → `VKI_Cave_Falls`;
    - a sewer grate in the main street → `VKI_Sewer_S1`;
    - a stone lock-up on the market place, by the inn's garden → `VKI_Dungeon_B1` (stair down).
  - **Link data.** Each entrance instance carries the interior kit's link props, plus an `SPN_<id>` spawn in
    `VK_ValleyTown` (`town_links`, run last in `build_valley_town`). The valley is level `VK_ValleyTown` (`VKI_TOWN`).
  - **Underground.** The five surface links (`@surface` / `@return` before) now target the valley. Three one-way links
    got their way back: B1 has a passage to the sewer, and B4 has tunnels to the falls and the sewer.
  - **The world graph** (`vki_world`): `vki_world_check` (two-way, unambiguous arrival, kinds that pair, built link
    objects and spawns) and `vki_world_json` (`docs/world_graph.json`).
  - **Result.** 0 errors and 9 notes (the building interiors' and the breach demo's `@return`, the mine's `@deep`).
    The six levels touched check at 0 errors.
  - **Lessons.**
    - The terrain has no holes, so every way down starts above ground and its passage must end in front of the cliff
      behind it. Rock round an opening must be carved (faces spanning it deleted), not only pushed out of a box.
    - The colony camera hides the ground about 8 m north of a two-storey house: the lock-up moved from beside the
      keep to the market place.
    - Metallic bronze facing the camera reads as a hole.

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
    - ~~an exterior entrance (cellar stair, crypt door)~~ (the town connection: the lock-up on the market place,
      [docs/WORLD_GRAPH.md](docs/WORLD_GRAPH.md)).
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
    is one mesh (split it to animate). The adit links to the valley's mine portal (WORLD_GRAPH).
42. T19 checks a follow-mode level from one camera over its centre, so tall props near the level's ends (the timber
    sets by the mine's tunnels) can hide a spawn or trigger they would not hide in play. `VKI_Mine_M1` moved its sets
    off those rays; a follow grid of cameras (`vki_t19_visibility` accepts several) would test what the game sees.

Town connection (2026-09-30; details in docs/WORLD_GRAPH.md):

43. The world graph: run `vki_world_check(built=True)` after changing any level's links (a level built before its
    links changed reports "rebuild the level"), then `vki_world_json(VKI_WORLD_JSON)`. The arrival rule needs exactly
    one link back per pair of levels. The valley's links live in `ENT_TOWN_LINKS` (`vk_mod_entrances`), placements in
    `TOWN_ENTRANCES` / `TOWN_SPRING_CAVE` (`vk_town_map`).
44. Not done yet:
    - The valley's building doors carry no links: the building interiors keep `@return`, and which buildings are
      enterable is still issue 21.
    - `@deep` (the mine's lift) has no level.
    - B1's sewer passage (like S1's to the gaol) is in a north–south wall, edge-on to the game camera (issue 30).
    - The entrances' passages are shallow (at most 2.2 m) because the terrain has no holes. A real cellar stair would
      need holes in the terrain tiles.
    - The valley's `SPN_` spawns are in world coordinates (the valley at x 1500): shift them if the valley is
      exported at the origin.

Unity export (2026-09-30; details in docs/UNITY_EXPORT.md):

45. Vertical slice exported and verified (valley house, `VKI_Tavern_F0`, `VKI_Dungeon_B4`): the local UPM package
    `unity/com.danielgruginski.medievalkit` (referenced from MedievalSetting's manifest), exporter
    `src/export/vkx_export.py` (`vkx_export_slice()`), Unity `Tools > Medieval Kit > Build All`. Unity renders match the
    Blender renders from the same cameras (AgX reproduced by `KitAgX`). Test scene `VKX_Slice_House` holds the house.
    Next: the full piece export, the valley and other levels, runtime behaviour for links / doors / Full-Cut /
    traps / water (UNITY_EXPORT section 6). Issues 11, 19, 28 and 33 are partly covered there.
46. 2026-10-01: all 1199 master pieces exported (`vkx_export_pieces`), checked against Blender through the
    verification catalogs `VKX_Catalog_Exterior` / `VKX_Catalog_Interior` (UNITY_EXPORT section 7). Open: the
    world-projected terrain / stair / river materials (placeholders), trees ~10-15 % brighter in Unity, the stray
    `tmp_tw` object in `VK_Pieces`.
47. 2026-10-01: KitTerrain (terrain / stair / paving / curb / river water ported from vk_terrain as one URP shader)
    and the valley exported as level `Valley` (origin x 1500 -> 0, sky probed for ambient, verification cameras in
    `VKX_ValleyCams`). Matches Blender except cast shadows (off in the Blender scene) and trees. 9.37 M tris, 3.9 M of
    them pines.
48. 2026-10-01: all 20 world-graph levels exported (`vkx_export_world`) and linked in Unity (KitWorld / KitLink / KitSpawn /
    KitTravel, a test walker; UNITY_EXPORT section 8). Next decided with the user: how levels and buildings are made
    in Unity (generators vs Blender-baked layouts).
49. 2026-10-01: Unity house generator (UNITY_EXPORT section 9), rules-compatible with build_house_v, not seed-identical.
50. 2026-10-01: shutters. The user had asked for fresh paint on most shutters, yet nearly all read worn: the chips are
    painted into T_VK_PaintedWood_BC / _N / _R (bare wood where _Mask is 0, ~11 %), and "fresh" only moved a mask
    threshold. Fixed in `vk_mat.pbr_material` / `fresh_paint_set`: fresh shutters use T_VK_PaintedWoodFresh_* (chips
    grown 3 px and filled from offset samples of the same set); the *Worn variants keep the chips. The valley had no
    worn shutters at all (all 128 painted ones fresh) although its infill houses use `random_style` (with
    `_maybe_worn`); not checked why (other modules set shutters explicitly).
51. 2026-10-01: bevel seams (the user saw it on the chimney, in Blender and Unity). Cause, in `Kit.box`: bevelling
    replaces the box's big faces, which `box` then never textured; `rebuild()` gave them its default projection
    (material tile, no offset) while the bevel strips got `box`'s own (its tile, a random offset), so every bevelled
    box showed strips of another part of the texture. Fixed kit-wide: bevel strips now get the default projection, each
    as the box face it leans towards (`project(..., snap_axes=)`); the big faces are unchanged. Rebuilt all 420
    exterior masters: geometry identical, 151k bevel faces + 612 flat faces (left unreplaced by the bevel) re-textured,
    catalog renders differ by <=1.3 % of pixels. A planar projection still breaks at a box corner; the chimney shaft
    uses `box(..., wrap=True)` (`Kit.wrap_uv`: u = distance around the bevelled outline, closing on the back-left
    corner), so its stones run on round the corners. Found on the way: `SM_VK_TownWall_Tower_Round` in the .blend
    differs (up to 3.8 m) from what its builder makes today, and `fro_staddle` jitters vertices in set order (not
    reproducible); both left as stored, the tower excluded from the rebuild.
    Interior side (same day): `VKIKit` overrides `box` / `project` with a copy of the old code, so it had the same bug;
    fixed the same way and all 713 VKI masters rebuilt (`vki_rebuild`, VARI_* refreshed): 37k bevel faces + 59 flat
    faces re-textured, 261 pieces only renumbered vertices (same shapes), 3 (Bed_Straw, Bed_Box, Hearth_Open) came out
    ~1.2 cm different from builder randomness, so they kept their stored geometry with the new UVs transferred
    (faces matched <= 8 mm). 14 mine props changed materials only in unused slots 56-59. Interior catalog renders differ
    by <= 1.5 % of pixels. The exterior VAR_ meshes already carried the new UVs. Both kits re-exported to Unity.
52. 2026-10-01: Unity L-houses (KitHouseGenerator Shape L), the Kit Palette for building by hand (UNITY_EXPORT 9-10),
    and a material signature cache in the exporter (UNITY_EXPORT 11).
53. 2026-10-01: 45 premade structures (landmarks + module buildings) exported as Unity prefabs (UNITY_EXPORT 12);
    scene `VKX_Structures` shows them in a row. Next: generators for interiors and caves.
54. 2026-10-01: rooms from typed plans in Unity (UNITY_EXPORT 13), phase 1 of 4 (structure; then props from plan
    codes, caves, a random room generator). `vkx_export_interior_rules` -> `Data/interior_rules.json`; `KitRoomLayout`
    + `KitRoom` port `vki_parse_plan` / `vki_rooms_layout` / `vki_build_scene`'s shell. Golden test: the 12 walled
    rooms match Blender piece for piece (720 pieces, materials, spawns, links, lights); 14 rhythm posts / doorway mats
    differ only because props are not placed yet.
55. 2026-10-01: phase 2, furniture in `KitRoom` (UNITY_EXPORT 13): the record's props by mount (wall_floor, wall_hung,
    table, floor hug, prop links), or furniture from the plan's cell codes, and bare plans build with defaults. The
    user asked for the general idea, not a Blender-exact match: props are tested to 5 cm (10 of 12 rooms match; 3 props
    0.3 m off), codes alone find 158 / 165 coded props. Debris not ported. Next: caves (phase 3), random rooms (4).
56. 2026-10-01: phase 3, caves in `KitRoom` (UNITY_EXPORT 13): cave maps (rock tiles by corner code, wall-backed
    tiles, chasm / stream ground tiles, sewer / lava channels with flow, quarter floors, tunnels, mine track) and
    `KitCaveGenerator` (the cellular automaton in outline). The 7 cave levels match Blender piece for piece (2,437).
    The export now keeps rooms' zone order (`zone_order`). Next: the random room generator (phase 4).
57. 2026-10-01: phase 4, generators (UNITY_EXPORT 13): `KitDungeonGenerator` (rooms + corridors in rock, doors, stairs
    up / down, themed rooms via `KitFurnisher`, torches, debris, `KitEncounter` markers for the game's monsters) and
    `KitInteriorGenerator` (house ground floors). The user asked whether this makes playable levels: layout, markers
    and walkability yes; monster AI / combat is game code still to design. Walkability fixes found on the way (kit-wide):
    chasm / stream tiles had no floor collider on their open quarters (prefab builder `AddGroundFloor`), bridge decks
    were not walkable (`KitDecks`), and the walk test (navmesh) shows openable leaves must carve, agents <= 0.35 m.
58. 2026-10-01: the user found the random caves weak ("an artificial zigzag", no maze, the chasm never widening,
    narrowing or crossing the cave to a bridge). `KitCaveGenerator` rebuilt: Maze layout (lattice + depth-first maze +
    loops + alcoves), the chasm a gorge carved across the map with breathing width, forks, ledges, land bridges and
    rope bridges (either way) where it splits the cave (UNITY_EXPORT 13). Old automaton kept as layout "Open".
59. 2026-10-02: debris ported (`KitRoom.Debris.cs`); generator validation (Rooms > Validate Generators, WalkMap) and
    the fixes it drove until seeds 1-120 of all nine generators were walkable (1,080 levels): cave bridge decks need
    chasm on both sides and no rock beside their landings, decks count as joined only along their span, finds and
    dressing never cut the floor; dungeon stairs on any wall run (a Down hole's arrival is on the piece's +x side),
    pocket ways = the middle of each opening; a worktable from codes now backs onto its wall (it had slid 3 m into a
    doorway). Then the user's "keep going on the other generators": `KitSetPieces` (bar, altar / hoard, pillars on
    nodes, wall-hung pieces, table dressing, beside-placement) used by both generators (UNITY_EXPORT 13), bigger taverns,
    a great hall per dungeon, and Rooms > Build Interior Showcase. Seen in renders; not yet seen by the user.
60. 2026-10-02: chained maps (the user: dungeons, caves, ruins chained by smaller transition maps that load the next
    seamlessly; transitions read best north-south, north best). His calls: a continuous world (no fade), exits on any
    edge, maps baked in the editor. Built: `KitPortal` (generator input / record output, any edge), the seam rule in
    `KitCaveLayout`, `KitConnectorGenerator`, `KitChain` + `KitChainTools.Bake` + `KitChainStreamer` (UNITY_EXPORT 13).
    Then he asked whether the features are documented for use, since AI will build most levels: the package's
    `Documentation~/LEVEL_BUILDING.md` (an agent-facing guide), `AGENTS.md` at the root, a package README. Unity could
    not compile for a while (Windows commit limit exhausted: ComfyUI held 39 GB, the editor 20 GB; it cleared). Then
    verified: Chains > Create Sample Chain bakes 5 pieces + `SampleChain_Play.unity` (Assets/MedievalKitChains), and in
    play mode the streamer loads the walker's piece and its neighbours and unloads the rest. Asked what "stairs between
    heights" meant: seamless descents need new art (a walkable flight, two-storey rock); advised staying flat, with
    scene-transition stairs for dramatic drops (his decision pending). He said branching is needed: done (a map joins
    any earlier map's portal, `attachTo` / `attachPortal`; every portal joined once; 20 / 20 branching chains walk).
    Next: he will feed his own game maps (sketches or "generate it" specs, plus the graph of joins); ruins generator,
    loops and navmesh across pieces as they come up.
61. 2026-10-02: outdoor maps, `KitVillage` (Runtime/World) + `KitVillageTools` (Editor). The user's brief for the RPG's
    starting map (MedievalSetting): a small hamlet with a captain by the dungeon's entrance (rat bounty), one market
    (potions, gear, herbs), a chapel (respawn), a small inn (part of the game's loop), generic houses, closed by fences
    or forest too dense to walk, 2-3 road exits; maps only for now (no gameplay), organic, "avoiding the box feel"
    of square tiles. The rats' way in: the inn's cellar breaks into a cave (bigger infestation) that leads on into the
    cave network; no sewers, so no old-town ruins (his calls). A layout (JSON, plan metres) -> a scene: a ground mesh
    with the terrain material and a control map painted along curves (roads, areas, doorsteps), relief rising into
    the forest, pads under buildings; structures or generated houses turned to face a point; gardens, fences along
    curves, props, trees; a forest round a lumpy clearing (stragglers, undergrowth, a 24 m margin beyond the map);
    invisible walls (a ring inside the forest, road corridors, the border); spawns, `KitMarker`s, exits as `KitLink`s
    at road ends; door links. Walk test (navmesh): every spawn and marker reached, forest probes beyond the wall not.
    `Assets/MedievalKitWorld/Hamlet.unity` from `Hamlet_layout.json` (also the package's
    `Documentation~/examples/Hamlet_layout.json`): ok, 7 spawns, 4 markers, 24 forest probes; about 6.5 s to build.
    Guide section 5.7. Next: the inn interior ("Hamlet_Inn", the inn door's target), stairs down to a hand-made cellar,
    its breach into a rat cave chain (chains need a hand-made map kind for the cellar). The captain in plate is the
    Humans track's.
62. 2026-10-02: the inn and the rats' way in (MedievalSetting `Assets/MedievalKitWorld`). Package: hand-made maps in
    chains (`KitChain.Kind.Plan`: plan / record files or text, portals from the record), a scene link into a chain
    (target the play scene, `arrive` a piece's spawn: `KitTravel` hands it to `KitChainStreamer`, which loads that
    piece first; Bake records each piece's spawns), arrivals without the kit world (a link's `arrive`, a record link's
    fourth element, a village door's `arrive`, else the spawn named like the link; `@return` remembered when one
    arrives on a "@return" door), cave encounters (`creature`, `encounters`; the poi is the boss's lair),
    `KitRoomTools.BuildRoomScene` (+ Rooms > Build Room From Selected Plan). Content: `Hamlet_Inn` (VKI_Tavern_F0
    widened by a storeroom with a stair down), `Hamlet_Inn_F1` (the kit's, relinked), `Hamlet_Cellar` (hand-made cave
    map: cellar and vault in dressed stone, a breach north into a rat-dug cave, a north portal, two rat encounters),
    chain `HamletCellar.asset` -> cellar -> rat cave (Maze, rats x5, POI_RatKing lair) -> cave network (Maze, chasm,
    no encounters yet). Verified: walk tests (inn 2/2 + floor 28/28, cellar 6/6 + 69/69, rats 34/34 + 230/230,
    network 299/299), 30 / 30 rat caves over seeds, and in play mode the whole loop: hamlet -> inn door -> inn ->
    stair down -> chain (walker on the cellar's stair, cellar + connector loaded, the rat cave loading ahead) -> stair
    up -> inn -> front -> hamlet; chapel door -> VKI_Chapel_F0 -> @return -> the chapel's door. Hamlet.unity still
    needs a rebuild for its doors' `arrive` (it was open in the editor). The .plan.txt / .record.json files are the
    source from now on (written once from the tavern preset and the dungeon generator's wall rule; edit by hand).
63. 2026-10-02: the user saw the hamlet's pines blue-grey with black streaks, then the inn's painted chests light
    blue. One cause: the kit's levels have no environment reflection (Custom, intensity 0) but
    `KitHouseTools.CopyLighting` copied only the ambient, suns and volume, so every scene built with it (hamlet, inn,
    chains' play scenes, showcases) reflected Unity's default procedural sky at full strength, which washes dark leaves
    and painted wood blue-white at grazing angles. Fixed in CopyLighting; the generated scenes in MedievalSetting
    patched (Hamlet rebuilt, with its doors' arrivals; Hamlet_Inn_F1 once the user closed it). A first fix
    in KitLit (foliage without indirect light) treated the symptom and was reverted. The pine atlas tile is green,
    the leaf vertex colours neutral; the dark whorl stems are Blender's own (vk_nature: "read as shadow"). The chests'
    teal is Blender's design (the shutter slot 10, M_VK_Shutter_Teal); the user doesn't like it, so in Unity chests
    and dressers default to M_VK_Shutter_Natural (`KitBuilder.MaterialDefaults`, kit-wide; shutters, the draper's
    stall and the boats keep their paint).
64. 2026-10-02: the goblin warcamp (the user: no Rat King; goblin bodies as loot early in the caves, spiders and
    centipedes deeper, goblins near the camp; the warcamp on the surface in the woods, a cave entrance inside it joined
    by tunnels to the cellar's breach; the surface way is shorter but the goblins hold their gate; a woods map between
    the hamlet and the camp; real dead-goblin props). Package: cave `creature` lists by depth, `dressing`, `finds`,
    `extraFinds`, finds marked as loot (R["markers"] -> KitMarker, also for hand-made records); props may name the
    game's prefabs (`KitInteriorRules.External`, the editor's `KitRoomTools.ProjectPrefab`); a Warren dungeon is all
    goblins; a chained dungeon's `exit` stair up to a scene; KitVillage: `clearings` (glades), closed fences with gates
    at their own width, `offset` / `flip` / `collide` on fences, link pieces as doors (a cave mouth), `encounters`,
    exits' `arrive`, invisible walls rebuilt as the outline of the walkable ground on a 1 m grid (the ring + road
    corridor walls left gaps where roads met glades and walled a side trail across the main path), the walk test
    checks ground encounter points. Content (MedievalSetting): the chain HamletCellar is now cellar -> rats (5 dead
    goblins to loot) -> deep caves (spiders, then centipedes; chasm, egg sacs, cocoons) -> goblin tunnels -> warren
    (goblins, a boss by the stair up into the camp); Woods and Warcamp layouts and scenes; the hamlet's forest track
    leads to the woods. Goblins repo: `GoblinCorpses` (Tools > Goblins > Bake Dead Goblins: four goblins posed at the
    last frame of the Human Animations death clips, baked to static props in Prefabs/Corpses) and an editor-safe
    destroy in `GoblinAppearance`. Verified: every map walk-tested (all spawns, markers, encounter points; forests
    sealed), and in play mode inn -> hamlet -> woods -> warcamp -> cave -> warren -> stair up -> warcamp -> woods ->
    hamlet, each arrival on its spawn.
65. 2026-10-02: the warcamp looked human-built (tidy towers, cream tents, a heraldic banner), so the user allowed new
    Blender assets. Four goblin camp pieces in `vki_props_lair` (package adventure): `Prop_Goblin_Watchtower` (crooked
    bark legs, lashed braces, a platform at 4.18 of uneven planks, a parapet of stakes with skulls, a lopsided hide
    awning, a red rag; front -Y outward, ladder +Y; colliders: legs, floor, parapet open at the ladder),
    `Prop_Goblin_Tent`, `Prop_Goblin_ChiefTent` (a tusk-gated tipi, door -Y), `Prop_Goblin_Bonfire` (light). Helpers
    `vki_lair_hide` (a closed hide plate split into a grid, sag, mottled vertex tone, ragged hem: M_VK_Hide has no
    texture, so flat hides read as plain tan boards), `vki_lair_slab`, `vki_lair_log`, `vki_lair_stone`. The
    `Overlay_Bedroll` hide darkened (it read near white outdoors). KitVillage: props' `scale` and material `swap`
    (layout palette + per entry). Walk test: a lifted encounter point is judged by its height over the terrain (the
    lowest hit), not over the first collider (a tower platform under an archer counted as ground). MedievalSetting:
    Warcamp has the watchtowers astride the wall by the gate (walkways end at them, archers on both), 14 goblin tents
    in clusters round the bonfire, fire pits with bedrolls, racks, totems instead of the banner poles, the chief tent;
    the woods' lookout is a watchtower with a goblin tent. Tests {} on the four; walk tests ok (Warcamp 12 encounter
    points, Woods 7). Renders: game-camera gate, yard, chief, tower.
66. 2026-10-02: the user found the goblin tent "weird" up close and asked for a leather material. Why: M_VK_Hide is a
    flat colour, so the hides were smooth vertex-tone gradients (card / plastic up close), strips of different flat
    tones read as painted boards, and a pale sewn-on patch half under the tied-back flap made an "N". Fix:
    `T_VKI_Hide` (vki_tex_dungeon `vki_gen_hide`: sewn hide pieces, wavy seams, thong lacing, creases kept soft -- the
    first, streaky creases read as wood grain) and `M_VKI_Hide`; HIDE joined `VKI_OVERRIDABLE` so the goblin pieces
    take it per master (`vki_lair_hide_mats`: the four camp pieces, Overlay_Bedroll, Prop_Totem_Goblin,
    Prop_LeanTo), their hides projected at its 2 m tile; vertex tones lowered; one patch per tent side, clear of the
    flap. Exterior M_VK_Hide untouched. Tests {} on the seven; seen in Blender and in Unity (close-up, game camera).
67. 2026-10-02: the user: the warcamp needs a gate the player has to destroy to get in. `Prop_Goblin_Gate` (two leaves
    of lashed stakes in the exterior Palisade_Gate frame's opening, skulls and a marked hide outside, the bar inside;
    `vki_breakable` 1, `vki_broken` "SM_VKI_Prop_Goblin_Gate_Broken"; one collider over the frame's posts too, which
    have none) and `Prop_Goblin_Gate_Broken` (a leaf fallen in face up, one hanging open with two stakes snapped, the
    bar in two, splinters; colliders: the posts and the hanging leaf; a 1.9 m way through). Both fill the 0.3 m slits
    between the frame's posts and the palisade (`vki_lair_gate_fill`; they showed the camp through them). KitVillage:
    fences' `gateDoor` / `gateDoorFlip` (doors at the gate's transform, named GATE_*). WalkVillage: breakables
    (KitPiece `vki_breakable`) count as broken; a second navmesh with them whole lists what they shut off. Warcamp:
    `"gateDoor": "Goblin_Gate"`; checked in a throwaway copy of the map (the user had Warcamp open): walk test ok, the
    gate shuts off 16 of 17 points (all the camp; the cave's way in arrives inside); both states rendered in place.
68. 2026-10-02: player movement (the user: a capsule placeholder; hold to move, click to interact, like Diablo / Baldur's
    Gate; the camera never rotates -- people would see the art's flaws; instant cuts where levels can be preloaded,
    e.g. a town's interiors). Package: `KitNavMesh` (a level's baked NavMeshData, added while it is enabled) and
    `KitNavBake` (from the colliders the way the walk tests see them; default agent type 0 with radius 0.3; outdoor
    0.1 m voxels, rooms and chains 0.05; a chain gets one surface over all its pieces in its play scene; breakables carve
    with NavMeshObstacles), baked by BuildVillage / BuildRoomScene / chain Bake and the Navigation menu; `KitTravel`
    preloading (the current level's link targets held loaded with their roots inactive; a held target is an instant
    cut; others, chains and the way out of a chain, a plain load behind a short fade; `Place` warps NavMeshAgents);
    `KitLink.walkInto` (village road exits); KitTestWalker steps aside for a registered player; the village walk test
    turns carving obstacles off while it runs. MedievalSetting `Assets/Game/Scripts`: `ClickToMove`, `GameCamera`
    (looks north at 50 degrees, wheel zoom, copies the level camera's backdrop), `GameBoot` and Game > Play From Hamlet /
    Play This Level (playModeStartScene: the open scenes are left alone). Verified in play mode: hamlet -> chapel
    (instant) -> @return -> hamlet -> forest road (walked into) -> woods (instant) -> warcamp (instant); the gate makes a
    path into the camp partial; the cave -> HamletCellar_Play (fade, the chain streamed, the test walker gone, paths of
    238 m across unloaded pieces). Baked: Hamlet, Woods, Warcamp (rebuilt), Hamlet_Inn_F1, VKI_Chapel_F0, the HamletCellar
    chain; Hamlet_Inn not yet (the user had it open). Next: trees / roofs between camera and player, interior doors that
    open as one comes (agents walk through closed leaves today).
69. 2026-10-02: movement, second pass. Hamlet_Inn baked (the user closed it). Interior doors: none of MedievalSetting's
    levels has one (their only leaves are exit doors, taken by their link first), so doors that open on approach wait
    for a level that has them. See-through in KitLit (`KitSeeThrough.hlsl`: a cone from the camera to a 2.4 m disc
    round the walker's chest, above feet + 1.4, dithered with a 4x4 Bayer, a soft rim; the forward, DepthOnly and
    DepthNormals passes clip -- the PC renderer runs SSAO --, the shadow pass does not), driven by MedievalSetting's
    GameCamera; checked on the inn's roof in the hamlet and pine branches in the woods (a first capture with one
    Render lost the instanced trees: render twice). Pointer feedback (`PointerFeedback`: a gold pointer-and-door cursor
    over a way out, a gold ring shrinking at a click's destination, the prompt with a shadow). Play-mode route checked:
    hamlet -> inn (instant) -> cellar stair -> HamletCellar_Play (fade, on the chain's navmesh) -> stair up -> inn (fade),
    the hamlet and F1 held again.
70. 2026-10-02: the warcamp's cave mouth showed grass inside and a ladder stood in the yard leading nowhere. The spring
    cave's darkness stopped halfway in (the valley's copy stands before a cliff): now dark side cards to the mouth and a
    dark floor under the jamb rocks; a dry variant `SM_VK_Entrance_CaveMouth` (no trickle: the user found the blue
    ribbon weird) is the warcamp's cave. Fences take `along` (pieces on the line at fractions, turned as its pieces):
    the ladders stand on the walkways' lines and lean on the deck. Grass blades (the user asked; then asked for a
    compute shader, the proper way): `KitGrass` holds the map's clump list (16 bytes a clump: position, tint, height;
    KitVillage.Grass places them on the ground mesh, clear of everything placed, thinning on roads, paving, slopes and
    at the forest's edge); a compute shader (`Resources/KitGrassCull.compute`) culls them per camera into an append
    buffer, one `RenderPrimitivesIndirect` draws them, the vertex shader (`KitGrassInput.hlsl`) builds 5-7 blades a
    clump from the index (no meshes; 0.5 s to open the warcamp). The blades take the ground's grass colour (KitTerrain's
    recipe in the ground's object space), dark roots and sunlit tips, sway, part round the walker (the see-through's
    globals) and cast shadows (without them the grass vanished from the game camera). Two dead ends: a geometry
    shader (no Metal, slow); baked meshes (76 MB for the warcamp). Hamlet 36k clumps, Woods 10k, Warcamp 34k; walk
    tests ok; seen in edit and play mode (instant cut keeps it). Not grass: streaks in the gate's shadow on the path.
71. 2026-10-03: the see-through cut the wall of a house the player stood in front of. It tested "nearer than the walker"
    along the line of sight; the camera looks down 50 degrees, so the wall above the walker's head counted as nearer.
    Now "in front" is measured along the camera's level heading (KitSeeThrough.hlsl; z: kept within z in front, level).
    Checked in play mode at cottage_2: in front of it the wall stays whole, behind it the roof opens, a pine between
    camera and walker opens. (Renders right after teleporting the camera can show instanced trees black and leafless:
    render a few frames before capturing.)
72. 2026-10-03: the user shared a game draft (Sewer Slice: click-to-fight rats, loot, fever, trader, quest, death recap)
    and asked to build it on the kit. Game code lives in MedievalSetting `Assets/Game` (README there: stages 1-3); the
    game project is now in Unity Version Control (cloud repo MedievalSetting, /main, baseline changeset 2). Kit change:
    `KitTravel.GoTo(level, spawn)` -- travel without a link (a respawn): instant cut when held, fade otherwise, placed
    in place when already there; the return stack is forgotten. The HamletCellar chain's creature lists now
    `rat,giant_rat` (rat cave) and `plague_rat,spider,centipede` (deep caves); re-baked. Open: cave rock tops carry
    navmesh islands (2.2 m up, unreachable): a click or a sampled point can land there -- KitNavBake should leave out
    surfaces not connected to the level's spawns.
73. 2026-10-03: the game's stage 2-3 (humanoid player, loot, bag, fever, food, villagers, shop, bounty, campfires, UI
    Toolkit HUD: MedievalSetting `Assets/Game/README.md`). Kit changes (KitTravel): `GoTo` into a level that is still
    preloading now waits for it like `Go` does (it used to start a second load of the same scene); `Pending` (a journey
    waits on a preload) and `CancelPending()` (the game calls it when the player dies, so a door taken a moment before
    does not carry the dead); `Reset` (domain reload off) also clears `Arrived` / `Leaving` and unhooks `sceneLoaded`;
    KitTravelHost unsubscribes its Arrived handler. MedievalSetting level data: `Hamlet_layout.json` gained the
    herbalist marker (64.5, 100) with a cauldron and a herb drying rack, Mara's note; the Hamlet was rebuilt (walk test:
    7 spawns, 5 markers ok). Campfire spots in the cellar chain are game data (GameRules), in the connector passages
    01a and 02a: the rat caves have no chamber 7 m by path from every creature.
74. 2026-10-03: the user saw z-fighting on the cellar's stair (HamletCellar 00 cellar). Cause: its record placed
    `Stair_Up_150x450_Stone` (rot 0) with its rail side against the room's wall -- the side its `vki_no_wall` keeps
    clear -- so the lip (x to 1.50, top z 3.0) lay in the wall's coping, coplanar with its cap (0.105 m2, both facing up;
    KitLit renders both sides, `_Cull 0`), and the balustrade stood inside the wall. A stair running +Y with its wall on
    its right cannot be had by rotating (no 180), so the stone stairs got left-hand twins: `Stair_Up/Down_150x450_StoneL`
    (`vki_dun_mirror_l` in vki_fam_dungeon: the mesh mirrored across local x 0.75, faces reversed, every local-x
    metadata value with it; tests clean, same tris). The cellar record now names `StoneL`; the chain re-baked (pieces
    identical but the stair: 0 coplanar overlaps, 0 vertices in walls; the stair link to the inn works). The rooms' post
    rule follows the variant: a `StoneL` flight's wall-side nodes are at its local x 1.5 (`stairNodes` in KitRoomLayout,
    the stair rule in vki_rooms), so no rhythm post is laid out beside it (the generator and the down stair's slot: item
    75). Open: in `Hamlet_Inn_F1` the down stair (`RailR`) overlaps a `Post_Board_Mid_Cut` (0.013 m2, 68 vertices
    inside the post). Also: the chain
    bake silently dropped a piece whose prefab the interior rules did not know yet (the cellar came out without its
    stair): `KitChainTools.Build` now fails on a room's "no prefab" notes as it does on portal notes -- run Build
    Interior Rules after adding pieces. Seen while fixing the game's hold-to-walk jitter: besides rock tops, villages
    carry unreachable navmesh islands on roofs and flat prop tops (the Hamlet: patches ~4 m up over many buildings, the
    inn's included, each with a twin on the building's unreachable floor); the game now picks reachable floor only, but KitNavBake could
    still drop surfaces not connected to the level's spawns (item 72).
75. 2026-10-03: (a) KitDungeonGenerator picks the left-hand stair: an Up flight whose cells have the room's edge (wall
    or rock) on their local +x side and floor on -x is emitted as `StoneL` (Down lines keep their wall on -x). The game's
    HamletCellar chain re-baked: 'HamletCellar 04 warren' now has `Stair_Up_150x450_StoneL` (rail on the open side; 92
    of 1,794 vertices meet the rock where the cave wall bulges against the flight's solid side, down from 632; 0 flat
    faces coplanar with rock tops); the cellar and the warren are the chain's only stone up stairs. (b) The stone down
    stair's slot: kerb `kw` runs on to `VKI_LNK_BACK_Y` like the timber trimmer; both masters rebuilt (tests clean,
    same tris), exported, prefabs rebuilt; vertical rays through the old slot now hit the kerb top (Blender and the
    Unity meshes). (c) Props without colliders were walked through (the navmesh is baked from colliders): no exterior
    `SM_VK_` prefab carries a collider, and KitVillage boxed only layout props and the buildings' walls. New
    `KitSolid` (Runtime/World): `Box` puts boxes over what one bumps into -- a mesh's faces below 1.2 m, gathered on a
    0.25 m grid into the separate parts they stand as, one box each (a signpost's post, not its arms; each post of a
    canopy or gallery, not its roof; a fence's whole run; a table) -- `Round` a capsule on a bush's or stump's pivot;
    soft pieces (plants, `Deco_`, crops, flower boxes, chickens, ladders, overlays, piers, decks, steps) stay walkable.
    KitVillage.Dress boxes a building's own dressing outside its walls' box (the inn's tables, stools, barrels, ale
    cask, hitch rail, lamp posts and yard fence; the barn's cart, hay and trough; the chapel's bell tower; a gable
    chimney), skipping the porch and gates; layout props use `KitSolid.Box` too (they had a 2.5 m box over their whole
    footprint: invisible walls round signposts); Forest undergrowth and Scatter get KitSolid.Nature; KitRoom.Put boxes
    reused `SM_VK_Prop_` pieces (the inn's and the cellar's barrel stack). Rebuilt: Hamlet, Woods, Warcamp (walk tests
    ok), the HamletCellar chain; Hamlet_Inn patched (its barrel stack boxed, navmesh re-baked). A census (navmesh under
    a renderer's pivot, reachable from a spawn) now lists only steppable sunken rocks, the goblin watchtower (its
    authored colliders are its legs) and the warcamp's walkway deck. Open: porch posts are still walked through (the
    porch is not boxed so its door stays reachable).
76. 2026-10-03: wild garlic for the RPG (its gatherable herb): `SM_VK_Plant_WildGarlic` (`make_wild_garlic` in
    vk_nature; 1,406 tris): crowns of broad leaves folded along the midrib (real geometry, the sheet's leaf on them) and
    stalks of white star-flower umbels, chunky enough that the white reads from the colony camera (a first, sparser
    patch did not). Its own 512 sheet `T_VK_WildGarlic` (`vk_leafgen.paint_wild_garlic`: leaf, flower, stalk; the full
    leaf atlas has no free cell), material slot 55 `WILD_GARLIC` (`M_VK_WildGarlic` = `leaf_material` on the sheet, a
    flat stand-in until it is painted). Exported alone (`vkx_export_pieces(names=[...])`), Unity Build Materials + Build
    Prefabs (1,246, 0 off). Preview scene `WildGarlic_Preview`. Seen in MedievalSetting at the woods' gather spots.
    Also from the game: a goblin tent in `Warcamp_layout.json` stood on the foot of the west walkway's ladder (an
    `along` piece), and the tent's hollow inside is a navmesh pocket: the game's ladder dropped the player in it. The
    tent moved; the walk test checks spawns, markers and encounter points, not ladder feet -- it could.
77. 2026-10-04 (from the game; the user: the caves' "persistence of those tiles and that black part", "it is ok to
    have black areas, but we need better transition"; a burrow "blocking too much the passage"; a lean-to "we could
    walk inside, but we cannot"):
    (a) **`KitShroud`** (Runtime, `Shaders/KitShroud.hlsl`, KitLit's forward pass): the Diablo-like underground look.
    On a level's scene (a chain's play scene gets one from `WritePlayScene`; MedievalSetting's `HamletCellar_Play` was
    given one): while enabled it rasterises the navmesh near the level's floor into a distance field (0.5 m cells, R8,
    globals `_KitShroudTex/_Rect/_Args/_Args2`); KitLit darkens with the distance from the walkable ground
    (`darkFrom` 0.2 -> black at `blackAt` 3 m) and keeps `topLight` 0.3 of the light on the rock's tops (faces turned
    up 1 m+ over the floor), so the pale `CaveCut` tops no longer read as tiles and the rock fades into the black
    round the level instead of ending at a cliff edge. The floor is the height band (0.25 m, >= 5% of the area)
    nearest the loaded levels' spawns: a cave's rock tops carry navmesh islands that outweigh its floor (65% of
    HamletCellar's navmesh is at 2.25 m), and the first try (the biggest band) lit the tops and blackened the
    floor. It builds once the walker stands on the navmesh and a spawn is in (pieces stream), again on each arrival;
    held or left, it is off. Outdoor levels have none.
    (b) `SM_VKI_Prop_Burrow` shrunk (1.35 x 1.24 x 0.43 -> 0.87 x 0.79 x 0.27 m with its clods), exported, prefab
    rebuilt (its box follows), HamletCellar's navmesh re-baked (`KitNavBake.BakeChain`).
    (c) `KitSolid.Box`: faces lower than a step (a plank floor, a threshold) no longer part anything (boxes still
    reach the ground), and a hollow part (< 60% of its cell rectangle) gets boxes along its walls (greedy rectangles)
    instead of one over all. `SM_VK_LeanTo` is a floor, two front posts and a roof: one box used to cover its floor;
    now the posts only, and the floor is walked on (Woods rebuilt; its pieces gained 23 boxes -- the boulder, the
    outcrops, the watchtower follow their shapes -- and lost none; the invisible walls are redrawn from the outline).
    (d) `vki_core`'s master check asserted `len(kit_mats()) == 55`: the wild garlic slot (55, entry 76) broke every
    interior rebuild. The interior takes slots 0-54 and numbers its own from 55, so it now asserts `>= 55`.
78. 2026-10-04 (MedievalSetting's Greywall, the user: "no offense to valley town, but it is too square ... we will
    need to create a new city plan. It can have walls like valley town"; plan approved, then built overnight; no kit
    code changed): a walled town and a forest road built with KitVillage from layouts a script writes
    (MedievalSetting `Assets/MedievalKitWorld/Tools~/greywall_layout.py`, `banditroad_layout.py`).
    (a) **Town walls as props, not a fence line.** A fence lays a piece every `max(planBox)` = 3.45 m for
    `TownWall_Straight` (its buttress counts), but the modules are 3 m pitch pieces: 0.45 m see-through gaps. And a
    fence `gate` gets no colliders (the gatehouse's masonry is walked through) while a `building` gets one box over
    the passage. So the script lays `TownWall_Straight` props on exactly 3 m along each straight run between corners
    (`rot` = the run's heading on a counter-clockwise ring: local +Z, the outer face, turns outward), a
    `TownWall_Tower_Round` on each corner turned to the corners' bisector (its ground door toward the town),
    `Gatehouse_Block` on a run (`rot` = the heading; modules kept 5.5-6 m off its centre) and `TownWall_Postern` in
    place of one module. The corners are nudged (up to 1.8 m) so every run is whole modules with 2.0-2.8 m left to each
    tower's centre (the round tower hides the ends). Props get `KitSolid.Box` per part: the gatehouse passage stays
    3.3 m clear, the postern's 1.9 m; the walk test goes through both. 125 modules, 18 towers. The bare
    `Gatehouse_Block` comes without its timber storey and portcullis (props have no height key). A fence `length` key
    (3.0 for the wall) and boxed gates would let a fence line do it.
    (b) Measured plan boxes (about the origin, x east / y north before turning) and fronts, for laying out:
    Inn (-5.95,-5.75)..(11.50,4.52) front (0,-1); TownHall (-9.63,-5.71)..(8.70,4.52) (0,1); Smithy
    (-4.20,-6.45)..(5.91,7.52) (-1,0); Bakery (-5.55,-5.26)..(5.65,4.52) (0,-1); Chapel (-7.20,-4.52)..(10.60,4.52)
    (0,1); TowerHouse_Fortified (-4.37,-5.25)..(5.20,4.37) (0,1); MerchantHouse (-6.74,-5.24)..(5.40,6.42) (0,-1);
    TowerHouse_Domestic +-5.24 (0,1); TrainingYard (-7.20,-7.70)..(7.20,9.02) (-1,0); TownhouseGablefront
    (-4.67,-6.55)..(4.52,5.70) (1,0); Brewery (-8.95,-5.45)..(7.60,5.52) (0,-1); Granary (-5.64,-5.29)..(4.70,4.54)
    (0,-1); Stable (-6.81,-8.81)..(6.06,4.56) (0,-1); Tannery (-9.03,-5.27)..(6.77,7.06) (0,-1); DyersYard
    (-5.75,-3.20)..(4.59,3.27); Pottery (-6.10,-4.65)..(4.88,5.60); Hovel_* (-7.10,-6.18)..(4.16,4.56) (1,0); Windmill
    +-6.79 x (-5.51..5.28); GuardTower +-3.2. A generated house (`house`) is about (1.5 cells + 1.55) either side and
    -5.3..4.6 front to back (porch and eaves), not cells x 3 by 6.
    (c) `BuildVillage` creates its scene additively: run it with a saved scene open (it throws "Cannot create a new
    scene additively with an untitled scene unsaved" after `NewScene`). An edit-mode `Camera.Render` right after
    opening a big map can draw only the terrain: KitLit's variants are still compiling (async); render again.
    (d) In play, travelling back into a held map logs "Failed to create agent because there is no valid NavMesh" once
    per creature; they are all on the navmesh a moment later (seen with BanditRoad's 21).
79. 2026-10-04 (MedievalSetting: every building with a door enterable, the user: "the buildings on the hamlet should be
    visitable", "think this about the way baldurs gate 1 and 2 worked ... loot inside the houses, but it does not
    respawn", "you could reuse some scenes ... but there should be some tool for adding random things at runtime"):
    (a) `KitTravel.Entered` (the door the current building was entered by: level, link), `ReturnStack` and
    `PushReturn` (a game's save keeps the doors to return through; its load puts them back after its GoTo, which
    forgets them). One room scene shared by many doors tells its houses apart by `Entered` (the game's
    InteriorDresser dresses each house from it).
    (b) `KitRoom.CodeFootprint` is public: a tool that writes interiors with `KitInteriorGenerator.Generate` itself
    passes it (the real footprints of the furniture codes; without it every code is one cell).
    (c) `KitVillage.MeasureWalls`: a building's front is the side its door opens to -- the axis of the door piece's own
    forward, on the side of the walls it stands at -- no longer the box edge the door sits nearest. A building with a
    yard (the Smithy's forge, the TrainingYard, the Woodcutter's) has a box whose nearest edge is not the door's: its
    door spawn landed inside the building and the walk test failed. Changes the front of Smithy, TrainingYard,
    Woodcutter, Terrace, FisherHut and ConstructionSite_1 only (checked over every structure); maps that face those
    turn them.
    (d) The kit's own `Generated/Levels/VKI_*` interiors (Cottage, Hovel, Townhouse, Workshop, Chapel, Tavern...) carry
    no navmesh: a walker cannot move in them (the hamlet's chapel door led into VKI_Chapel_F0). MedievalSetting builds
    copies from `rules.Plan` / `rules.Room` with `KitRoomTools.BuildRoomScene` (which bakes) instead. Baking the
    VKI_* levels themselves (KitNavBake) would fix it at the source.
80. 2026-10-04 (MedievalSetting's Greywall, the user: "The gates aren't complete, and that part being shown causes Z
    fighting"): `SM_VK_Gatehouse_Block` is only the gatehouse's stone base -- in Blender `def_dress_gatehouse`
    (vk_mod_defence) finishes it with a timber storey on the walk (6.2), a slate hip roof and the flanking towers'
    cones (9.0), the portcullis raised under the arch and the leaves open. A layout prop of the block showed its flat
    top and open tower rims. `KitVillage.Dressings` (piece -> parts in its own frame, Unity metres, from the valley
    town's placements) now finishes it wherever a layout places it, as children of the block; `"dress": false` on
    the prop leaves it bare. The roof material goes in by name (any `M_VK_Roof*` -> `M_VK_Roof_Slate`): the Blender
    slot index (3) is not the Unity one. The editor's `Names` / material list take the parts in.
81. 2026-10-04 (MedievalSetting's menus: save slots, New Game): `KitTravel.Reload(target, spawn)` -- `GoTo` but always the
    fade and a plain single load, so every held level is dropped and the target comes back as built (GoTo keeps held
    copies and only places the walker when the target is current: a load would find the last visit's dead and broken
    things still there). Forgets the way back like GoTo; the game pushes its saved doors after the call.
82. 2026-10-05 (MedievalSetting's orc chapter, the user: "we may need some wasteland props and terrain for creating the
    orc lands"; the wasteland is the old north wood the orcs burned): `vki_props_orc` (package adventure, loaded after
    `vki_props_lair`): `Prop_Ruin_Farmhouse_Burnt` (hero tier), `Prop_BurntTree_A` / `_B`, `Prop_BurntStump`,
    `Overlay_Ash`, `Overlay_Tracks_Orc`, `Prop_Orc_WarTable`, `Prop_Orc_Banner` (docs/ADVENTURE_KIT.md). Lessons:
    FIELDSTONE is banned on VKI masters (VKI_STONE_BLOCK_IN); overlays are budgeted as dressing (400 tris) whatever
    tier they are given; painted marks laid as overlapping strokes trip T5S -- one closed strip per line
    (`vki_orc_band`), what crosses it a step higher; a ruin wall of one tall box per run read as tombstones -- lay it
    in courses of stones (`vki_orc_wall`). Tests {} on all eight; exported with `vkx_export_pieces(names=...)`, Unity
    Build Prefabs (1254, 0 failed). Preview scene `Orc_Preview`. MedievalSetting: the Northfields map uses them.
83. 2026-10-05 (the orc chapter's second part, the user: "continue the orc questline"): the siege yard in
    `vki_props_orc` -- `Prop_Siege_Ram`, `Prop_Siege_Tower` (half built), `Prop_Siege_Catapult` and their `_Burnt`
    twins, `Prop_Orc_Cage` / `_Open`, `Prop_Orc_WarDrum`, `Overlay_Orc_BearTrap` / `_Sprung`, `Prop_Orc_Totem`
    (docs/ADVENTURE_KIT.md; 12 masters, 348-3672 tris, tests {}; 1266 prefabs, 0 failed). A burnt twin is the same
    builder with `burnt=True` (members charred, some fallen or snapped, hides to rags, an ash bed with coals:
    `vki_orc_ash_bed`, `vki_orc_rag`). Lessons: rafter pairs meeting at a ridge share their side planes (T5S): offset
    one of each pair; girts ending flush with the crossing girts' faces (T5S): run one direction past the other; a hub
    ending exactly on a sill face (T5S); the construction module's `con_ladder` and `con_lash` leave open tubes (T7) --
    `vki_orc_ladder` and hoop bands instead; `def_rope` of several straight segments overlaps itself (T5S): one
    segment, or sag. Preview scene `Siege_Preview`. Unity package: a layout's `ground` key (a terrain material of the
    map's own: the RPG's burnt march, scorched grass and ash) and a layout-level `swap` now repaints the forest and
    scatter too (LEVEL_BUILDING.md). MedievalSetting: the burnt march map uses them.
84. 2026-10-05 (MedievalSetting's underground, the user: "something that the player could keep following from the
    goblins all the way into bandit infested caves"): `KitDungeonGenerator`'s **Hideout** theme (guard posts, stores
    and cells walled into the rock, rough tunnels between, every encounter "bandit" but the lair's boss) marks its
    plunder as record markers (`Plunder`: the lair's treasure chest `strongbox`, store rooms' crates and barrels and a
    guard post's chest `plunder<n>`, role `loot`), and puts a chained map's exit stair in the deepest room but the lair,
    a room with no encounter (the lair's stair meant a boss appearing at the stair's foot for whoever came down: the
    game's spawners never fill a spot by the player, so it popped in as they stepped away; other themes unchanged, the
    warren's stair is still in its lair). `KitChainTools.Bake` keeps the play scene's `KitShroud` as it was tuned (a
    re-bake had put MedievalSetting's top light back to 0.4 from 0.3). MedievalSetting: the HamletCellar chain's
    oldway (Maze cave, goblin + bandit) and hideout pieces, the bandit road's cave mouth.
85. 2026-10-07 (MedievalSetting, the user's reports): **a swap target may be a map's own material** by its asset path
    (`"M_VK_Leaves": "Assets/.../M_BurntMarch_Leaves.mat"`, like the layout's `ground`; `KitVillageEditor` loads it,
    `KitVillage.Swap` matches its file name) -- the burnt march swapped the leaves to the opaque coal material and the
    dead trees' leaf cards showed as grey squares ("something wrong with the shader of the trees on the wasteland"); an
    opaque material must never replace a cut-out one. And **`KitDungeonGenerator` cuts a room's east and west walls**
    like its south one (only the north wall stands full): a full side wall's inner face, seen from the camera's side,
    hid the cut doorway beside it and its panelling read as a grille ("turn the grilles into open doorways, they are
    hard to see"); a corridor run of one or two segments on an east or west side is always left open (its doorway sat
    at the run's end, pinched shut by the rock bulging in from the corner; the random draw is still made, so layouts
    stay as they were). MedievalSetting: BurntMarch and the HamletCellar chain rebuilt.
86. 2026-10-09 (MedievalSetting's burnt march, the user: an orc swordsman a few metres from his archer "is trapped,
    needs to rework the pathfinding over that region"). Cause: `ambush_rocks` point 0 sat in the invisible wall and
    snapped to the forest's own navmesh beyond it (2/3 of the map's navmesh lay outside the walls); the melee orc only
    notices along a complete path, so it never came. Kit changes: **the bake leaves out the ground beyond the walls**
    (`KitVillage.Outside()`: the one-metre cells off the walls' grid, walls' own cells and the margin, as ~400 merged
    rectangles -> Not Walkable ModifierBox sources in `KitNavBake.Build`; rooms, caves, chains untouched); **trees and
    stumps get trunk colliders only** (`KitSolid.Trunk`: the burnt trees' / stump's export boxes -- their whole crown
    or root spread, hollow to the bake -- dropped at build; capsules 0.45 / burnt tree 0.4, stump 0.5 / burnt stump
    0.32; forest, scatter, undergrowth and layout props alike); **the walk test is loud** (problems logged as an error;
    a marker in a cage is a prisoner, not a problem; `BuildVillage` runs it before the bake with `repair`: a cut-off
    encounter point moves to the nearest reached spot within 3 m, half a metre clear, with a warning naming it);
    **the bake reports islands** (`KitVillageTools.Islands`, warning for a spawn, marker or ground encounter point on
    one; the breakables' carving switched off while it reads -- NavMeshObstacles carve in the editor too). Burnt march:
    navmesh 39,025 -> 14,598 m2 (beyond the walls 25,496 -> 0), pieces 1,993 -> 32, the walked area +10%, burnt-tree
    and stump top islands gone, the strip's necks under 0.5 m 7 -> 0; the point moved in `burntmarch_layout.py` to
    (94, 72). BurntMarch and Northfields rebuilt, the other outdoor maps rebaked (their tree colliders change at their
    next build); LEVEL_BUILDING 5.7 and 5.9.
87. 2026-10-11 (MedievalSetting's barrows, the user: "add zombies as creatures in the barrows"). **`mounds`**, a new
    `KitVillage` layout key: `{centre, radius (one number or [rx, ry]), rot, height, top}` raised into the ground as
    smooth domes (an ellipse, flat over the inner `top` share, smoothstepped out to the rim; added to `Natural()`, so
    clearings, roads and pads still flatten over them); LEVEL_BUILDING's layout key table. And **`KitDungeonGenerator`'s
    spawn points in a room its set pieces filled**: the set pieces reserve the floor round them, so a small dressed room
    (the Crypt lair with its chest shrine, a 3 x 3 crypt, a shrine) had no free cell and its encounter came out with no
    points (the game's spawner then spawns nothing: the barrow's boss was missing). Such a room now takes its open floor
    (not door or stair cells, off the doorways if it can), its first spot the one nearest the middle, without a random
    draw (the rest of a level comes out as before; no other built record had an empty encounter). MedievalSetting:
    ShepherdDowns (mounds) and the Hollow Barrow (Crypt, seed 117) built.
88. 2026-10-11 (the user: the terrain tiles "as an extra tool for building things ... to add some terrain variation on
    the maps"): **`terrain` on outdoor maps** (`KitVillage.Terrain.cs`, LEVEL_BUILDING 5.7 "Terrain"). The exported
    `SM_VKT_*` tiles had no Unity user before. The layout's `terrain` gives a 3 m cell grid levels (1.5 m tiers) from
    `areas` (rect / ellipse / poly, the last area over a cell's middle wins, `stiff` for the `Sq` corners), `ramps`
    (a low cell climbing towards its higher neighbour; `width`, `stair`, `walled`) and `dress`. Laid as `tk_tiles` does:
    the dual grid's corner takes its four cells' levels, a Full tile at their lowest (above 0), a cliff layer per level
    above (MS table, quarter turns -> -90 deg about y), `pick_var` weights by a port of `hash32`, `ramp_override` for
    Ramp/Stair Half E/W and Mid, a stacked identical layer without its skirt (faces below -2.5 m dropped). The FBX tiles'
    axes already match plan space ((x, y, z) Blender -> (-x, z, -y), as `KitVillage.Local`). The tiles are merged into
    one mesh in the ground object's space (the terrain shader projects grass and the control map in object space, so
    separate tile objects would each shift the pattern), sharing the ground's material instance (the stairs keep
    `M_VKT_Stair`), with a MeshCollider; saved as `<Map>_Terrain.asset`. `tk_cliff_dress` and `tk_ramp_dress` ported
    (boulders, lip pieces, lip grass on middle ledges, rubble and plants at the foot; stones and plants at ramp joins).
    Heights: `Base()` = a raised cell's tier, else `Natural` flattened within 3.5 m of raised cells (`TerrainNear`);
    `Height` and the buildings' pads use it; the ground mesh sinks to 0 under raised cells. Grass raycasts the terrain
    first (blades on the tops and on ramp banks up to Nz 0.7, none on faces or stairs: `OnStair`). `KitNavBake` adds Not
    Walkable boxes under raised cells up to 1 m (`UnderTerrain`). Checked on a test map (every case, stacked tiers,
    stiff corners, ramp, two-wide stair, ramp to a knoll) and MedievalSetting's ShepherdDowns (knoll, two terraces, a
    shelf). Known: the half-ramp tiles show a small dark sliver at one cliff join (in the piece itself); faces facing
    east or west read as edges and north faces hide behind their tops from the game camera.
89. 2026-10-11 (MedievalSetting's cliffs + resource zones pass: all 8 outdoor maps got terrain; found by its reviewers):
    **dressing keeps off the cliffs** -- `Free()` (forest, undergrowth, stragglers, scatter) now refuses a spot within
    1.6 m of a cliff line or a ramp (`NearCliff`), so no tree stands on a lip or a bush in a face (maps without terrain
    are unchanged; with terrain the darts' draws shift, so the forest and scatter of those maps reshuffle); **a building
    on a tier levels no pad** -- its pad (1.5 m up) used to ease the level-0 ground round it up towards it, burying the
    cliff's foot and banking a second way onto the tier (Greywall's motte, the windmill knoll). And a rule found there:
    a ramp is laid only on Edge tiles (`RampOver`), so each side neighbour of a ramp's low cell must continue the
    straight step (at or below its level, one level up ahead) or be a ramp the same way; otherwise one grid point is a
    corner tile and half a ramp leaves an open wedge. MedievalSetting's `Tools~/layout_check.py` tests it (with
    reachability, tiers off roads/buildings/mounds/rim); LEVEL_BUILDING's terrain notes say it too.
    Round 2, from renders of every map with the game camera: **trees keep out of the cliffs' view** -- forest darts and
    stragglers refuse a spot up to 8 m south of a higher level (it hides the south face, the only one the camera sees)
    or up to 3 m north of one (the trunk's foot hides behind the top, so it seems to grow out of the lip): `Shades`;
    **the dressing runs last** -- `DressTerrain()` (cliffs, ramps) after `Trees()` and before `Forest()`, and each piece
    asks `DressFree` (its level, off every ramp's tiles via a cached `OnRampTile`, out of the occupied footprints), so
    nothing lands in a ramp's mouth, in a tent or on a fence; sunk face boulders only on faces that look south (seen
    edge-on they read as logs or posts on the lip); lip pieces 0.3-0.75 m back from the edge; **no grass out of the
    faces** -- on the terrain collider blades need Nz >= 0.85 except on a ramp's tiles (>= 0.7, its banks are turf);
    **a boulder on each ramp bank** -- the tongue's earth banks are turf slopes that the top-down grass projection
    stretches into a pale wedge, and the cliff beside them ends open; a sunk Rock_Boulder_A/B on each bank, long side
    along the face, hides both (checked on a test map: a 3-cell and a 7-cell face look the same, so it is the tile, not
    the layout). Not fixed: a 3 m step (two stacked 1.5 m layers) reads as two bands with a grass lip between; E/W
    ramps still read as gaps from the camera (put the ramp meant to be found on a south face).
    Round 3 (the round-2 renders): `Shades` was still too short -- at 50 degrees down a crown h m up covers the ground
    0.84 h north of its trunk, so the pines buried faces 8 m away: now no tree up to 14 m south of a higher level and 3 m
    to either side of that strip, none on a raised top within 4 m of its own south lip, and none where its foot hides
    behind a higher top (`HidesFoot`: within pad + 0.84 x the drop of a north edge; trees pad 2 m, undergrowth and
    scatter 0.5 m); lip pieces 0.9-1.4 m back from the edge; the ramp dressing out beyond the bank boulder (a tuft sat on
    it and a pebble in every mouth: they looked stamped), the boulder's long side along the bank; **grass on a tier only
    at a top's height** (+-0.12 m, ramps excepted): the face tiles carry small flat ledges halfway up that passed the
    slope test, so blades stood out of the rock; **`_RimTint`** (KitTerrain, Vector: rgb + strength, default the old
    constant lime at 0.1) tints the tiers' lip band (vertex colour B) per map -- Burnt March's lips read as a sage
    icing border, now a dark ash at 0.5. The ramp tile's open face end (a flat tongue with a slit above it, beside each
    bank boulder) is in the piece: it needs an end cap in vk_terrain.

90. 2026-10-12 (MedievalSetting's rat contract, the user: "we probably should have a proper sewer dungeon for the rats
    quest ... Maybe we should have a proper generator of sewers like we have for other dungeon types?"): **the sewer
    generator**, `KitSewerGenerator` (Unity package, `Runtime/Rooms/KitSewerGenerator.cs`; KitRoom `sewer` settings and
    `RandomSewer()`, inspector "Random Sewer"; Validate Generators "sewer" / "sewer large"; BuildRoomScene lights a
    `Sewer` preset like VKI_Sewer_S1). A cave map of brick tunnels along a street grid (a walkway either side of a `ww`
    channel), channel heads under culverts or pouring from outfalls, one outlet, cisterns and halls, cross walls, bridges
    by union-find over the walkway regions, sluices, grottoes breached from the tunnels (the farthest the lair: the rat
    king's throne and the tunnel on down), a ladder up, torches, sludge, encounters. Rules in docs/SEWER_KIT.md section
    7 and UNITY_EXPORT; settings in LEVEL_BUILDING 5.1. `KitDungeonGenerator.Plan` is internal now (the sewer generator
    writes its plan with it). Checked: 20 / 20 validation seeds walkable, 200 generator-only seeds without an exception or
    a stranded cell, MedievalSetting's Greywall_Sewer (36 x 26, seed 35) played: ladder, tunnel down and back, 21
    creatures on the navmesh. Seen in renders; not yet seen by the user. Also not in this list before: 29fa628 (the
    interior generator's `open` great halls and `stair` up/down, docs/UNITY_EXPORT.md).

91. 2026-10-12 (MedievalSetting, the user: the see-through dithered a full wall beside the player in the generated
    sewer, "this wall covers nothing of interest"): every see-through test was per fragment, and a north-south wall
    beside the walker has fragments exactly where a wall across its way would (its stretch south of the walker is "in
    front", above the knees, within the cone). Now **only a piece in the walker's way opens** (`KitSeeThrough.hlsl`,
    `KitSeeThroughInTheWay`): its `Renderer.bounds` (URP's `unity_RendererBounds_Min/Max`) must meet the wedge from the
    camera to a box `_KitSeeThroughArgs.w` each side of the walker, feet to head (an interval test in s per axis); `w <= 0`,
    instanced draws or empty bounds keep the old behaviour. MedievalSetting's `GameCamera.seeThroughBody` = 0.2 (under the
    navmesh agent's 0.3, so a wall the walker walks along stays whole). Checked in play: the sewer's side wall whole at the
    walkway's middle and at the navmesh edge (it dithered before), a house roof south of the player still opens round the
    player. Trade-off: on a wall of separate modules crossing the line of sight only the modules in the way open, so the
    round hole can end straight at a joint. Diagnosed by a subagent (numeric check of the cases: scratchpad wedge_check).

92. 2026-10-12 (MedievalSetting, the user: "how about modelling a smaller ladder entrance?" ... "Make those part of the
    medieval kit"): **the trapdoor pair**, one cell each, in `vki_links` beside the flights (same link contract):
    `Stair_Down_150x150_Hatch` (oak curb round a centred 0.74 m hole, the lid opened 95 deg on the north curb so its
    ledged underside faces the camera and its top stays inside a north wall's proud line, a ladder down the hole's north
    side, linings into a VOID box; 1,292 tris) and `Stair_Up_150x150_Hatch` (the same ladder from the floor to the
    ceiling plane, the curb's frame hanging there; 992 tris), plus `Floor_150_Hatch_Q00..Q11` (the Q150 slab with the
    curb's hole, FLOOR with the parity offsets: the room's floor style runs up to the curb in any rotation; 32 tris, T9
    budget `Q150Hatch`). A first try gave the hatch its own plank deck, which read as a patch in the room's floor.
    Records: variant `Hatch` (`["Down", x, y, 0, id, "Hatch"]`); Blender `vki_rooms_stair_depth` / `_piece`, Unity
    `KitRoomLayout.StairDepth` / `StairPiece` / `HatchDown` (one cell, no wall nodes, the holed floor; cave layouts too),
    KitRoom honours `vki_prompt_text` on stairs ("Climb down" / "Climb up"), vki_check takes a hatch's `vki_hole`.
    Checked: vki_test_pieces {} on all six, `vki_lnk_hatch_pair_check()` 0 over 128 rung vertices, two rig rooms
    (`VKI_HatchRig_F0` Stone cellar / `_F1` Timber loft, built from records registered in memory, not in VKI_ROOMS)
    pass vki_check and were looked at in game shots and close-ups; exported, Unity Build Prefabs 1,272 / 0 failed.

93. 2026-10-12 (MedievalSetting, the user: "a hatch in the front of the initial hamlet inn, leading to the cellar ...
    we add another region south of the cellar"): **`SM_VK_Entrance_Trapdoor`** (`ent_trapdoor` in vk_mod_entrances,
    ENT_META "Climb down into the cellar"; 928 tris): the outdoor twin of the interior hatch -- a kerb of four dressed
    stones, a raised oak coaming 0.18 high round a 0.80 m opening, darkness cards at the ground and on the inner faces'
    lower half (the ground covers everything below z 0, so the depth is painted), a ladder's top standing up out of the
    dark, the lid opened 100 deg on the north coaming with its ledges to the camera. A `buildings` entry in an outdoor
    layout (the piece is the door). **`KitChain.origin`**: where the first map lies (Bake used the world origin), so a
    hand-made first map can grow south / west without moving the pieces after it (LEVEL_BUILDING 5.5). Checked in
    MedievalSetting: the hamlet's trapdoor by the inn (BuildVillage walk test ok, area map "Cellar hatch", game-camera
    renders); HamletCellar's cellar grown 4 rows south with `origin` z 6.0 and only that piece rebuilt (Build with the
    one piece, its scene saved, `chain.pieces[0]` updated, then `KitNavBake.BakeChain`): its old spawns moved 0.000 m,
    3 / 3 spawns walked, no overlap with the other 12 pieces. Prefabs 1,273 / 0 failed.

94. 2026-10-12 (MedievalSetting's bears' caves, the user: the cave's stair "should be like in skyrim, a natural opening
    to the outer world"): **`SM_VKI_Rock_Cave_OOFF_Mouth`** (`vki_cav_mouth` in vki_fam_cave; 974 tris): the tunnel tile's
    cleft wider and taller (`VKI_CAV_MOUTH`, a dict with a `portal` builder as the mine's adit), a ragged rock lintel
    closing its top (the cleft is cut through the rock's whole height), stones jutting from its sides, a daylight card
    (WINDOW -> Daylight, in front of the tunnel's VOID card), an earth slope (FLOOR -> EarthDamp), two backlit bushes
    and grass, roots, and a cold SPOT under the lintel (`vki_lights`, as the dungeon's light grate). `tunnel_kinds`
    "Mouth"; prompt "Leave the cave". Tests {}; seen in a workshop scene (WS_cavemouth) and in both MedievalSetting
    dens (DensMenu puts it on a north face of the cleared cave). Two dead ends on the way: rocks floating in the
    opening (no lintel: the cut runs the full height) and the FOLIAGE slot (a white flower-bush texture).
95. 2026-10-12 (MedievalSetting, the user: the chapel's windows "casting lights on the stair black part" and the bandit
    road's frame rate while Greywall loads): (a) **window pools keep off openings**: `vki_rooms_pools` / KitRoom.Pools
    leave out an FX_WindowPool whose patch (centre within 0.6 m) reaches a stair's or a hatch's cells (`stair_cells`,
    `pit_cells`), with a note: it lies at floor height and glowed over the shaft (the hamlet chapel's east lancet over
    its stair down; that one pool also taken out of the built scene, the only such pool in MedievalSetting's 16
    interiors with pools). (b) **paced preloads**: KitTravel's background preloads run at `PreloadPriority` (Low:
    about 2 ms of loading work a frame) instead of the default share, back to what it was when they are done; a
    journey that reaches a level still loading waits (as before) and raises it to High; `PendingLevel` names that
    level so a game can say "Loading..." (MedievalSetting does). The Blender side of (a) is in src only: push it
    before the next Blender interior build.
96. 2026-10-12 (MedievalSetting, an audit for more costs like its skirt simulation): **KitTravel frees what a let-go
    level used** (`FreeAssets`, on): Refresh, after unloading held levels that are no longer neighbours, runs
    `Resources.UnloadUnusedAssets` before the next preloads. A plain load does that by itself; an additive unload
    does not, so a journey of instant cuts kept every passed level's meshes, textures and materials in memory until
    the next plain load (10-25 MB of level-only files each in MedievalSetting). A short stall a frame or two after a
    cut, only when something was unloaded (back and forth through one door unloads nothing).
97. 2026-10-13 (MedievalSetting, the user: the look "pale and washed away, the units blend too much with the
    background" -- vivid grass, greyed wolves; "get the grass less saturated (while we keep the classic look)"):
    **the grass recipe's saturation is a property**, `_GrassSat` on KitTerrain and KitGrass (it was the constant 0.8 in
    both `KitHSV(col, 0.505, 0.8, 0.97)` calls), default **0.6** (he picked it from 0.8 / 0.6 / 0.45 / 0.3 shown in
    play). No map material stores its own value, so every map follows the default; KitVillage copies the ground's
    value to the grass material when it builds a map (the blades take the ground's colour, so they must match). The
    Blender terrain material still has 0.8: change it there before comparing Blender renders with Unity.
98. 2026-10-13 (MedievalSetting, the user: "the amount of z fighting that happens. Especially at regions where we
    can see inside the geometry due to the xray shader"; his examples a wayside shrine and the Greywall apothecary;
    "we should do the proper fix"). **The scan** (`tools/zfight_scan_pieces.py`, `zfight_scan_structures.py`, background
    Blender, read-only; results in `reviews/zfight_2026-10-13/`): triangles in one plane that overlap, split into
    *touching* (opposite facings: a plinth's top under a shaft's bottom, a stone on a ledge, a wall's foot on the
    ground; hidden until the game's see-through opens the piece) and *flush* (same facing: visible flicker). 631 of
    1171 masters overlap: about 1,300 m2 touching in 513 pieces, 200 m2 flush in 265 (bell tower, windmill, guard
    tower, gatehouse, roof trims); in the 45 premade structures 1,000 m2 touching, 45 m2 flush (parapets, turret
    corbels, scaffolds). **Fix A, done: solid materials are drawn one-sided** -- every material was two-sided
    (176 of 176), which is what turned the touching faces into flicker. The rule is in `vkx_export`
    (`VKX_TWO_SIDED`, `vkx_double_sided`, `vkx_apply_cull_policy`, run by `process_materials` before a material's
    signature, so it sets Blender's Backface Culling too): exterior `M_VK_*` materials one-sided (54), sheets two-sided
    (foliage, crops, flowers, leaf, window, stained, clock, net, void, water, moss, thatch, cloth, paper, burlap, hay,
    goods, mushrooms) and every interior-kit `M_VKI_*` material unchanged (their walls are sheets facing the room).
    Chosen by eye: `tools/cull_render_check.py` renders every master from four sides at the game's 50 degrees with
    culling off and on, `cull_render_diff.py` ranks the change, `cull_render_ids.py` (flat material ID colours) says
    which material lost surface. Real holes it found, fixed in the builders: the chapel door leaf faced into its wall
    (`chapel_wall` "D": `faces.new(vs)`), and a plank door in an arched opening (`def_arch_opening(planks=True)`:
    Def_StoneUp_Door, the round town-wall tower) got its back face 4 mm in, since the opening runs through. Looked at
    and left: the turret segments and the passage vault lose only their insides seen from above (capped / built over
    in use), the stone bridge pier's cap tip changes a little (under the span). Rebuilt + exported the three pieces,
    materials re-processed, .blend saved; Unity: Build Materials (the variants follow their base). Verified in
    MedievalSetting play: the shrine opened by the see-through shows no layers any more. **B, open:** the flush
    overlaps -- lift trims and corbels a few millimetres or drop the face hidden under them, down
    `reviews/zfight_2026-10-13/pieces.csv` (same_facing_m2) and `structures.csv`; then rescan.
    **B, partly done (2026-10-13 night; found in play by MedievalSetting's z-fight watch, `ZFightWatch`):** dressed
    reveals laid on a window or door hole's own side faces now stand 3 mm into the opening (`TWN_PROUD`:
    `twn_side_reveal` for the StoneUp twin window, loading door and door; the shops' `twn_reveal`); Wall_StoneUp_Door's
    hole runs up to the arch's crown (a panel and the spandrels had been built over each other above the door); the
    outer stair's landing parapet end, end-wall coping and landing top (under an upper door's threshold slab); the bell
    tower's plinth front (in the door's gap) and its belfry lintels (front/back the whole width, sides between, 3 mm
    proud of the piers); the stone gable parapet's 0.3 m seat into the wall below is 4 cm narrower a side (`SKY_SEAT`:
    the upper walls wobble 35 mm, so its faces crossed theirs); `twn_skirt` tops 3 mm under the piece's base (beside a
    stair's foot they lay in the ground's plane); the plaster window's sill 3 mm over the plaster under it. Rebuilt and
    exported: Wall_StoneUp_Twin / _Loading / _Door, Wall_Stone_Shop, Wall_Plaster_Shop, Wall_Stone_Passage,
    Passage_Vault, Stoop_Stone, Stair_Stone_Ext, Prop_CellarHatch, BellTower, Roof_Gable_Flush, Roof_Firewall,
    Roof_Gable_Stepped, Wall_Plaster_Window; .blend saved. Checked with the watch round Greywall's apothecary (the same
    12 stops): fight pixels 40,057 -> 4,514; with the chapel and the wizard's tower too, 2,546 left -- crop soil on the
    ground, a turret segment against a window wall, StoneUp corners' quoins crossing their core, slates crossing slates.
    Gotcha met: `vk_mod_town` already had a `twn_reveal` further down (the shops'); a second one of that name, defined
    earlier, was silently replaced and the walls came out with parts turned 90 degrees.
    Second batch (2026-10-14, the user's own walk with the watch through the hamlet and Greywall): the porch's step is
    0.13 high, under a door wall's own 0.2 step (both jittered 2 cm, they crossed in front of the door); the plaster
    ground walls' panels end 3 mm under the top beam (`plaster_ground` PT: their tops z-fought where the hole opens the
    roof); the ale cask's cradles were inside out (every face pointing in, the bottom up in the ground's plane) -- now
    wound outward; the gable chimney's base set back behind its quoin rocks; a thatch ridge cap's liggers and spars stop
    8 cm short of a gable's rake roll (`thatch_ridge_cap`, when an end runs past GX). Rebuilt and exported: Porch,
    Wall_Plaster / _Window / _Door, Prop_AleCask, Chimney_Gable_H30, RoofThatch_Gable / _Gable_Planks / _Gable_Cruck /
    _Single, RoofThatchS_Gable / _Single. Left: crop beds' soil crossing undulating ground (needs raised beds or the
    ground flattened under them), pine and bush leaf cards, hip-roof tiles where two slopes meet, the real caps' own
    self-overlaps (spike).

99. 2026-10-13 (99-103: the road to the see-through as it stands, entry 104; MedievalSetting, the user's
    screenshots of the see-through: "that first one is a tree, getting cut in
    the base, I don't understand why"; bush tops and a chapel's eave speckled though nothing hid the player; roof holes
    with a wall end standing whole in them and straight edges at joints). Four causes: the hole is open whether or not
    anything hides the walker; everything is sliced at feet + 1.4 (a tree left a stump); each piece decides alone
    whether it is in the way (HANDOFF 91); the dithered rim was 45% of the radius. The user picked five fixes and asked
    for the three small ones first, done here (`Shaders/KitSeeThrough.hlsl`, new `Runtime/World/KitSeeThrough.cs`,
    `KitVillage.Start/LateUpdate`): **the rim** 15% of the radius (`kKitSeeThroughRim`); **"in the way" from the waist
    up** (the wedge was to the feet: a bush or a fence before the legs opened); **rendering layers** set in play (nothing
    saved): KitVillage's Nature and Props are *loose* (bit 16: open down to the walker's feet, no foot kept -- only
    a building keeps the walls' footprint), the Nature is also *round* (bit 17: in the way when the ellipsoid inside
    its bounds meets the sight lines to the chest or head -- a big bush's box reaches the feet of a walker beside it,
    and the whole bush went), a building's pieces are a *group* (bit 18) decided on the CPU each frame
    (`KitSeeThrough.Building.Decide`): a cheap test of the building's whole box, then per piece the world box (the
    shader's wedge) and the piece's own turned box against nine sight lines (waist, middle, head; centre and a
    half-width to each side); one piece in the way and every piece carries *open* (bit 19). The turned box matters:
    world boxes of turned pieces are loose (the hamlet chapel stands at 37 degrees; its wall piece's world box held the
    walker in front of it). Walls placed as props along a line (`KitSeeThrough.IsStanding`: TownWall, Palisade,
    Gatehouse, Gate, Tower in the name -- Greywall's town wall is 125 modules under Props) are not loose: they keep
    their foot, and each run of them (modules whose boxes, grown 0.3 m, touch: `KitSeeThrough.Runs`) opens as one --
    Greywall's whole ring is one run, so near a corner the side wall in the hole opens too. A first try that gave every piece its building's bounds (`Renderer.localBounds`) was dropped:
    the chapel's box with its bell tower is 33 m across, and culling and shadows took the big boxes too. MedievalSetting
    side: `GameCamera.seeThroughNear` 0.25 (was 0.6 in code: the back wall of a house the walker stood against, 0.3-0.5
    m in front, stayed whole over it), `ClickToMove.SeenThrough` takes the marks (a building not open stays solid for
    the cursor, a loose piece is seen through down to the feet). Checked in play, off/on pairs in
    `reviews/seethrough_2026-10-13/` (hamlet: an oak, bushes, cottage_2, the inn, the stable, the chapel; Greywall:
    four houses, the town wall): a round hole through a canopy with no stump, bushes beside the walker whole, roof and chimney cut as
    one, no bite beside a house the walker is not behind -- except where the walker stands right against a building
    (the stable's roof corner, the chapel's buttress recess, a Greywall house's corner): its own box holds the sight
    lines though its surface does not. **Open (the user's list, next):** open the hole only when something really
    hides the walker (a small render of what stands between the camera and the walker, without the cut; grow/shrink
    the hole) -- this ends those bites and the speckle round a walker nobody hides; cap the cut: back faces in the hole
    drawn flat and darker, so a sliced wall or rock reads solid (a roof's ridge behind the walker floats above the
    hole today).

100. 2026-10-13 (MedievalSetting, the user: "yes, go ahead with the hidden check"): **the hole opens only while
    something hides the walker.** `Runtime/World/KitSeeThroughProbe.cs`: a disabled camera of its own (child of the game
    camera, at its position, 32 x 40 px, framing the walker's upper body 0.8 m wide) renders with the global
    `_KitSeeThroughProbe` = 1, under which `KitSeeThroughClip` keeps only what the hole would open (the new
    `KitSeeThroughOpens`: in front, above the foot kept, in the way -- the cone left out) and KitLit's forward pass
    returns flat magenta; everything else draws as usual and what stands behind the walker is discarded. An
    `AsyncGPUReadback` counts magenta in an ellipse over the body: `Cover` (0..1). At most 15 renders a second, none
    while a read is pending, no shadows or post (`UniversalAdditionalCameraData`), and the kit's per-camera work skips
    it (`KitSeeThroughProbe.IsProbe`: KitGrass, KitAgXFeature -- the AgX grade would tint the magenta). `Forget()` drops
    the answer and a read in flight (a teleport). Since the hole can now be shut while the walker is set, `w <= 0`
    means shut, not off: the CPU building decision and the grass parting look at `_KitSeeThrough.xyz` instead (all 0:
    no walker); `KitSeeThroughClipCS` runs in probe mode with w 0. MedievalSetting `GameCamera.SeeThrough`: opens when
    `Cover` > 0.12, shuts under 0.04 after a 0.3 s hold, grows in 0.2 s and shrinks in 0.35 s from/to the middle
    (`seeThroughWhenHidden` off: always open, as before); `Snap` forgets. Checked in play, `reviews/seethrough_2026-10-13/
    hidden_check/` (hamlet + Greywall): open behind the oak, cottage_2, the inn, the stable, two Greywall houses, the town
    wall (cover 0.99-1.0); shut in the open, beside both bushes, beside cottage_2 and the stable's roof corner, in the
    chapel's buttress recess, at the Greywall house corner (cover 0.0) -- the bites of entry 99 are gone. Cost: 0.7 ms of
    CPU a probe render in the editor (the game camera's own render to a texture: 1.6 ms), so ~0.2 ms a frame at 15 a
    second. A first capture of a fresh spot can drop a tree from a render made from a script (seen twice); the game's
    frames are not affected (off/on renders alternated at the same spot all agree). Still open: the caps (entry 99).

101. 2026-10-13 (MedievalSetting, the user: "yes, go ahead with the caps", with nine screenshots of the current
    behaviour: wall stubs cut at the hole's foot showing hollow insides, an oak's and a blossom tree's trunk sliced
    lengthways with a black inside, a thatch-and-plank wall's foot). **Caps:** KitLit's new pass `SeeThroughCap`
    (LightMode `SRPDefaultUnlit`, drawn with the opaques; `Cull Front`, `Offset 1, 2`, ZWrite on): a one-sided
    material's back faces, drawn only inside the open hole on screen and only below the foot kept
    (`KitSeeThroughCapClip`) -- the inside of a wall cut to its footprint -- in one flat colour per material (the base
    map's average, `SAMPLE_TEXTURE2D_LOD(..., 12)`, times the base colour and jitter, no vertex AO, lit by the sky's SH
    x 0.7), behind real faces by the depth offset. The vertex stage drops everything else (two-sided materials via the
    new per-material `_Cull` in KitLitInput's CBUFFER, a shut hole, the hidden check's view, a piece out of the way);
    KitBuilder disables the pass on two-sided and transparent materials (Build Materials run: 52 of 173 KitLit
    materials carry it, exactly the one-sided ones). Two tries dropped on the way: caps also behind the walker (the
    far slope of a roof is a ceiling from below: grey slabs over the street) and caps over the walker's own margin (the
    far side of a wall it stands against was painted flat over it); textured caps with vertex AO read as walls within
    walls. **Trunks:** the level test "in front of the walker" for a loose piece's solid (one-sided) materials now uses
    the piece's origin (`KitSeeThroughLevelPoint`: a tree's foot; its bounds' middle if the origin lies off them), so a
    trunk is in front or behind as a whole -- point by point it was sliced along the level line beside the walker and
    showed its inside; the bounds' middle was tried first, but a lopsided canopy moved it off the trunk. Leaves (two-
    sided) are still judged point by point, so the canopy over the walker opens. A loose piece's floor is now 0.25 m
    under the feet (a root flare at the walker's own level stayed as a thin dark curve); ClickToMove follows. Checked in
    play (`reviews/seethrough_2026-10-13/caps/`): beside the oak and the blossom tree the trunks stay whole and the
    canopy opens round the walker; behind them the whole tree opens; Greywall's stone houses and the town wall show
    flat grey cut tops; thatch and plank buildings unchanged; no cap over the walker or the street behind it. Not done:
    the caps are not in the depth passes (SSAO may shade over a cap's edge); a building whose walls are thinner than
    the cut shows only a thin cap.

102. 2026-10-13 (MedievalSetting, the user's four shots of entry 101 in play: the hamlet chapel's walls cut with flat
    cool-grey caps, and the bell tower sliced in half beside the walker). **Caps drawn as a level cut:** each cap pixel
    takes the material's texture where its line of sight meets the cut plane (`KitSeeThroughCapPoint`: the plane at the
    foot kept; `kKitCapTile` 0.5 tiles a metre, projected from above) and the light of a level face (sky SH + the main
    light by its height, x 0.8): the chapel's cut walls read as stone wall stubs, a cut door shows its planks.
    **An open building is cut as a whole inside the hole:** `KitSeeThroughOpens` no longer asks "in front of the walker"
    of a group piece (the CPU opened the building because it is in the way). Judged point by point, the bell tower
    beside the walker was sliced along the walker's level line (its hollow half showing) and a roof's far slope floated
    over the hole; now the hole is round through roof, chimney and walls, and what the hole shows of the tower is its
    floor inside cut stone walls. Tried and dropped: writing the cap's depth at the cut plane (`SV_Depth`, a real lid,
    to hide the pieces that interpenetrate inside a wall -- a wall's end inside a corner buttress shows as small fins in
    the cut, a window pane as a coloured line): the walls' buried back faces below the ground were lifted to the plane
    too and filled the chapel's nave and the tower with one stone slab, over the walker's legs (a lid needs a stencil
    pass; not worth it for the fins). Checked in play (`reviews/seethrough_2026-10-13/caps2/`). The probe draws the
    whole open building in magenta now (behind the walker too); the walker's body still hides what is behind it.

103. 2026-10-13 (MedievalSetting; the user: "I still think we need to recreate all assets in their cut off version ...
    I don't see how we can fix this without altering the geometry", then "Can't we have both the hole and the
    cutting? the hole is for pieces that cover the player, while the cutting is for pieces that stay on the ground",
    and "All the problems we are having happen because the hole shows part of the geometry it was not supposed to
    show"). **Real caps, prototype** (`Runtime/World/KitSeeThroughCaps.cs`, `Editor/KitSeeThroughCapsHook.cs`): the
    hole stays for what covers the walker; every piece is cut at 1.4 m over its base (a house's floor = its root's
    height, a tree's / prop's / town-wall module's own foot) and the cut is closed by a real cap -- the piece's own
    cross-section there, sliced from its mesh and filled (loops welded at 1 mm, nested loops as holes bridged to their
    outer loop, ear clipping), a child renderer with the piece's materials (the texture laid flat, `uv = local xz *
    0.5`, normal up, white vertex colour with alpha 0: no AO, no moss), no shadow casting, the piece's bounds
    (`localBounds`) so the shader's in-the-way tests agree, 1-4 mm under the cut by place so the caps of overlapping
    pieces do not fight. A check on 14 pieces (walls, corners, bell tower, town wall + round tower, palisade, trees,
    bush, well, cart) first: every solid material's section at 1.4 m is closed loops; only sheets (leaf cards, a door
    leaf, a window pane) are open and get no cap. The cut is kept per renderer in its rendering layer (bit 21 + a signed
    10-bit offset over its own origin in 5 cm steps, bits 22-31: `KitSeeThrough.WithCut` / `CutY`), and the shader
    (`KitSeeThroughFoot`) cuts at origin.y + m11 x offset -- exactly where the cap lies, whatever the walker's own height.
    A cap renderer (bit 20, `kKitSeeThroughCapMesh`) is drawn only where the hole opened its piece (in the way, in front
    / its building open, inside the cone, with the complement of its dithered rim), never in the hidden check's view.
    A building's caps open with it (`Building.caps`). Loose pieces are no longer opened to the feet: they are cut at
    their own 1.4 m like the rest (a tree in front keeps a capped trunk, the user's point: the obstacle stays visible).
    ClickToMove uses `CutY`. The back-face cap pass (entries 101-102) stays as the fallback where a piece has no real
    cap. Reading the meshes: they are not Read/Write, and in play mode only editor code may read them (`Mesh.vertices`
    and even `AcquireReadOnlyMeshData` refuse from a MonoBehaviour's Start; from an editor update both work), so
    `KitVillage.Start` sets the cuts and queues the caps, and the editor hook makes them between frames (8 ms a frame).
    Hamlet: 2,351 queued, 2,053 caps placed from 123 cap meshes, 8 polygons not filled, 1.4 s spread; the game camera's
    render costs the same with or without them (1.3-1.6 ms either way, editor). Checked in play
    (`reviews/seethrough_2026-10-13/realcaps/`): the chapel's cut walls are solid stone tops (the fins inside the corner
    are gone, under the caps), the bell tower a solid cut stub, cottage_2 / inn / stable round holes as before, the oak
    behind the walker a capped trunk, the blossom tree beside it whole. **Open for the full version:** bake the caps at
    level build (a player build gets none now; the cut itself works there), the other outdoor maps (Greywall's 47
    buildings and town wall untested), interiors / dungeons / sewers (no KitVillage), a stained-glass pane still shows
    as a thin coloured line at a cut wall's end, bark caps show bark rather than end grain.

104. 2026-10-14 (MedievalSetting; the see-through spike ended and was merged into `main` -- the user: "Proceed").
    Entries 99-103 were the road; the spike's rounds, its gallery of 19 edge cases and its tools are in
    [docs/history/SPIKE_SEETHROUGH.md](docs/history/SPIKE_SEETHROUGH.md). **The see-through as it stands:** the hole
    opens only while kit pieces hide the walker (`KitSeeThroughProbe`), and a building opens only where its own surface
    hides it -- each building's pieces carry a tag (rendering layer bits 8-14, `KitSeeThrough.TagShift`), the probe
    draws it in green, and `Building.Decide` opens a building while its tag covers 1% of the walker's body (held 0.3 s;
    the box test decides only without a probe answer in the last 1.5 s): a barn behind the walker no longer opens
    because a vat before it did. Every piece of a KitVillage map is cut 1.4 m over its base (`KitVillage.PieceRoot`:
    each mesh of a many-mesh prop such as the gatehouse over the prop's base), never under the walker's feet + 5 cm
    (`KitSeeThrough.AboveFeet` / `CutAt`: up the keep's outer stair the walker stood over a hole to the ground), and
    closed by a real cap. **Caps baked:** `KitSeeThroughCapBank`, a Resources asset named `KitSeeThroughCaps`
    (MedievalSetting `Assets/Game/Resources/KitSeeThroughCaps.asset`), made by `Editor/KitSeeThroughCapsBake.cs` --
    Tools > Medieval Kit > Bake See-through Caps, and by itself before every player build: each build scene with a
    KitVillage is opened additively, asked for its keys (`KitVillage.SetUpSeeThrough` with
    `KitSeeThroughCaps.Collecting` set; rendering layers put back) and closed unsaved (8 levels, 295 keys, 263 cap
    meshes, 12,034 triangles, 9.4 s). An entry keeps its source mesh's vertex count and bounds, so a piece re-exported
    since is ignored and, in the editor, made in play by the hook as before: re-bake after re-exporting pieces (a build
    does it anyway; before a build a bank that holds exactly the caps needed, none stale, is left untouched -- a bake
    rewrites the asset, and every build would leave it changed in Plastic; the menu always bakes anew; first Windows
    build with it 2026-10-14: 1,622 MB, 7 min, the bank found current in 9.9 s). **Caps pooled:** a cut piece is registered, not given a renderer; 96 pooled renderers are laid each
    camera frame over the registered pieces in the hole's cone, nearest first (Greywall: 96 instead of 4,255). Round 1's
    fixes: the gatehouse's gallery cut with it, caps stacked by area inside a piece and across a building (a stone
    corner's quoins z-fought in its rubble core), a plank floor in a cut house (the grass showed), end grain on bark
    caps, sheets in a building (stained glass, ivy, cloth) opened to the feet, nothing a character carries is cut
    (`KitSeeThrough.KeepBit`, bit 15). Rendering layers in play: 8-14 the building's tag, 15 keep, 16-19 loose / round /
    group / open, 20 cap mesh, 21 cut + 22-31 its offset. KitLit's back-face `SeeThroughCap` pass stays: it caps what
    has no real cap (no KitVillage: interiors, dungeons, sewers) and a cut held up at a raised walker's feet. Checked:
    every gallery case (15 last, 2026-10-14: the Greywall inn's interior and the generated sewer -- their walls are low
    or pre-cut, nothing hides the walker, the hole stays shut). MedievalSetting's side, checked in as cs:27: the hidden
    check and the cut in `GameCamera`, `ClickToMove.SeenThrough` (`CutAt`), the keep bit on carried items
    (`CreatureSilhouettes`, `PlayerModel`), the baked bank, the capture tool (Tools > See-through Spike) and the z-fight
    watch (`ZFightWatch`, F8; the find list behind entry 98's two batches). **Open:** entry 98's smaller z-fighting
    leftovers; a crop's soil on undulating ground (the user's call: raised beds, or the ground flattened under them -- done: raised beds, entry 105);
    self-overlapping outlines inside one cap (16 Greywall cap meshes, 0.15 m2 in all).

105. 2026-10-14 (MedievalSetting, the user's call on entry 98's leftover, the crops' soil on undulating ground: "raise
    beds"). **Crop fields are raised beds** (`vk_helpers` `bed_frame` / `soil_bed`; `CROPBED_RAISE` 0.2, `CROPBED_SINK`
    0.35, `CROPBED_T` 0.07): a timber frame of four boards (the short ones between the long ones) and corner posts 1 cm
    proud of them, the boards from 0.35 m under the piece's base to 0.25 m over it; the soil inside at 0.2 m (a fill
    down to the boards' foot, 2 mm inside them), the ridges and every plant lifted by `CROPBED_LIFT` (0.14 m) and set
    inside the frame (2.76 m). A flat bed's 6 cm of soil cut in and out of the undulating ground and z-fought with it
    (the watch: the hamlet's lavender, pumpkin and wheat, Greywall's carrots, the guild garden's plots); behind the
    boards a bump or a slope under a bed no longer shows. Wheat, carrot, lavender, cabbage, pumpkin and the tree nursery
    (`vk_mod_frontier`, the same `soil_bed`) rebuilt and exported, and a new **`SM_VK_Crop_Bed`**, an empty bed (the
    game's bare garden plot). Name clash met: `BED_T` is also `vk_terrain`'s (a tuple), loaded later into the same
    namespace -- hence `CROPBED_*`. The frame is now each crop's first material (`M_VK_Wood` sorts before `M_VK_Soil`):
    the crop prefabs were rebuilt (Build Prefabs, crops only); the maps' 90 crops (Hamlet, Greywall, Northfields,
    VK_ValleyTown) are prefab instances and follow. **Walked round:** the levels' navmesh runs through the fields (one
    waded through a slab); `KitVillage.CarveBeds` gives each `SM_VK_Crop_*` a carving `NavMeshObstacle` the frame's size
    (`KitVillage.BedSize` 2.92) in play, so no level had to be baked again. MedievalSetting: a bare garden plot is the
    empty bed (`GameRules.plotSoil`; drawing only the carrot field's first material would now draw only its frame), a
    field grows from its soil line (scaled 0.6 / 0.75 / 0.85 / 1 about the soil, so the frame barely moves), plants set
    out on a bed stand on its soil, and a plot carves the navmesh too (reached from 1.34 m; its use radius is 1.7).
    Checked in play (Greywall): the fenced garden's beds and the guild garden's plots right, the walkable edge 1.76 m
    from a bed's middle, no crop or plot among the watch's 24 spots; the see-through caps unaffected (crops never reach
    the cut). `docs/PIECES.md` rows updated.

106. 2026-10-14 (MedievalSetting's skill books, the user: "shelves and books as 3D assets, it is actually weird we don't
    have those", then "Maybe work on the shelves and books now? As in the models?"). **Library props**, a new interior
    package `library` (`src/interior/vki_props_library.py`, in VKI_TEXTS after `vki_props_orc`):
    `SM_VKI_Prop_Bookcase_150` (1.40 x 0.36 x 2.00, four shelves of books: runs of a set, gaps with a book leaning in, a
    few lying flat), `_Bookcase_150_Sparse` (half empty: a crock, scrolls, stacks, leaning books), `_Bookcase_075`
    (narrow), `_ScrollRack_120` (five by five dark oak pigeonholes, two or three scrolls in each, ribbons on a few),
    `_TableDress_Books` (a stack, an open book, ink and quill; on a table at 0.80), `_Book` (one closed oxblood book
    lying: a skill book or a tome on the ground, 12 triangles), `_Book_Open`, `_Books_Pile` (two stacks, loose books,
    one propped). **The book atlas** `T_VKI_Books` (new generator text `vki_tex_library`, run with `vki_tex_run`): 4 x 4
    cells, painted 512 and stored 256 -- spines in six leathers (oxblood, brown, green, blue, black, vellum), two
    designs each side by side in the cell (four raised bands and a title label; three bands, gold rules at head and
    tail), their covers (gilt frame and lozenge on oxblood, blue, black; blind on the others), the page edges (the
    boards' dark edges painted at both sides, so a single box reads as covers and pages), an open spread (text, a red
    initial, a framed picture), a scroll and a scroll's end; `M_VKI_Books` (VKI_MAT_MAP) on the TEXTILE slot overridden
    per master (`k.slot_mats`; not a style-swapped slot). The user, at the first look: "books look dirty" -- the
    leather's mottle, grain, stains and wear and the paper's noise cut to about a third (bump too). Every book is a
    closed 12-triangle box and every scroll and ribbon closed (test T7 wants props closed); the scroll rack's 6-sided
    scrolls keep it at 1,768 triangles (T9: over the 1,500 soft budget, under the 2,000 hard one -- a warning).
    `vki_test_pieces` otherwise clean. Built in `WS_vki_library`, adopted into VKI_Pieces (`vki_adopt`; instances `*_ws`
    left in the workshop's assembly), exported (8 pieces, the atlas's BC/N/R), Unity: Build Materials + Build Prefabs
    (these 8): `Generated/Prefabs/VKI/Prop/`. Renders: `renders/interior/WS_vki_library/`. `M_VKI_Books` is two-sided
    like every `M_VKI_` material (the export's cull policy). **Not yet:** the interior generators do not place them
    (KitInteriorRules); the game's uses (town shelves to search for general-skill books, the guild hall's library work,
    the tome item's ground model) are MedievalSetting work.

107. 2026-10-14 (MedievalSetting, the user: "have the interior generators place them, for example the wizard's tower,
    the chapel and townhouses", then "richer houses should have more books"). **The library props in the interiors.**
    Plan codes (`vki_rooms` `VKI_ROOMS_CODES`, exported in `interior_rules.json`, Build Interior Rules): BK
    `Bookcase_150`, bk `_Sparse`, BN `Bookcase_075`, SR `ScrollRack_120`, bp `Books_Pile`.
    `KitInteriorGenerator.Options.books` (0-3, -1 by kind: a townhouse 1 or 2, its upper floor and every other kind 0)
    -- decided on `new Random(seed * 7919 + 11)`, so a house without books comes out exactly as before: 1 a narrow
    bookcase in the hall, 2 a bookcase and the last side room a **study** (a run of shelves, a desk, a reading table
    with `TableDress_Books`, maybe a pile), 3 the hall a **library** (runs of shelves, a trestle table with books, desk,
    piles, rug). Shelves go up first and in runs side by side (`Shelves` -> `KitSetPieces.Strip`: along plain walls,
    never before a window or a door); the furnisher's rule of a clear cell round every piece kept a library to three
    cases. **A tall piece's walls** (`Tall`): a north wall anywhere, an east or west wall only in the house's back half,
    never the front (south) wall -- a 2 m case on the camera's side, or in the front rows, hid the room behind it. (`DK`
    desks and the rest use the furnisher as before.)

108. 2026-10-16 (MedievalSetting's meadow herb, the user: "we need to model the yarrow herbs"): **yarrow**,
    `SM_VK_Plant_Yarrow` (`make_yarrow` in vk_nature, seed 127; 1,552 tris, 0.87 x 0.92 x 0.66 m): a low rosette of
    feathery leaves (wild garlic's `wg_leaf` cards, flat) and 8 stalks with 2-3 small leaves each and a flat head of
    white florets on top (`ya_head`: a shallow dome facing up, about twice life size so the white reads from the colony
    camera). Its own 512 sheet `T_VK_Yarrow` (`vk_leafgen.paint_yarrow`: feathery leaf, head from above, stalk),
    material slot 56 `YARROW` (`yarrow_material`, `M_VK_Yarrow`, two-sided in `VKX_TWO_SIDED`). `wg_grid` / `wg_leaf`
    take `mi` (and `uvr`) now; the wild garlic rebuilds identical (`check_nature_specs` ok). Exported alone, Unity Build
    Materials + Build Prefabs (the yarrow only). Preview scene `Yarrow_Preview` (with wild garlic and wildflowers to
    compare). In MedievalSetting it replaces the wildflower stand-in at the `herb_meadow` spots (1.15x) and in the garden.

109. 2026-10-16 (the user: "make the wild cotton next"; MedievalSetting grows it among the yarrow): **wild cotton**,
    `SM_VK_Plant_Cotton` (`make_cotton` in vk_nature, seed 129; 900 tris, 1.15 x 0.86 x 0.92 m): 4 woody stems
    (crossed strips) leaning out from the crown with 2-3 side branches each, broad five-lobed leaves held out flat on
    short stalks (`ct_leaf`: a 3 x 3 card, rim cupped up; two leaf shades) at the nodes and round the crown's foot, and
    open bolls (`ct_boll`: three crossed cards, ~0.13 m, twice life size) at every tip and a few nodes. Its own 512
    sheet `T_VK_Cotton` (`vk_leafgen.paint_cotton`: two leaves, the boll's white puff of soft tufts over a brown
    four-pointed husk, a woody stalk), slot 57 `COTTON` (`cotton_material`, `M_VK_Cotton`, two-sided). Seen next to
    the yarrow in `Yarrow_Preview`. In MedievalSetting it replaces the white round-bush stand-in (`cotton` gatherable).

110. 2026-10-17 (the user: "the goblin herb next? It will be a olive colored patch of long leaves, grows in caves"):
    **goblin herb**, `SM_VK_Plant_GoblinHerb` (`make_goblin_herb` in vk_nature, seed 131; 1,540 tris, 1.27 x 1.23 x
    0.43 m): 10 crowns of 5-7 long strap leaves (0.34-0.52 m, `wg_leaf` with `e0r`/`e1r`: rising, then drooping to the
    ground; the middle crown's stand up so the patch has no hole). Its own 512 sheet `T_VK_GoblinHerb`
    (`vk_leafgen.paint_goblin_herb`: a smooth olive leaf with a pale midrib, a crinkled browner one with dark blotches),
    slot 58 `GOBLIN_HERB` (`goblin_herb_material`, `M_VK_GoblinHerb`, two-sided). `wg_leaf` takes `e0r`/`e1r` (defaults
    = the old ranges: garlic, yarrow, cotton rebuild identical). Seen on a dark floor in `Yarrow_Preview`. In
    MedievalSetting a `goblin_herb` gatherable placed by the cave walls (`GameRules.veins`).

111. 2026-10-17 (MedievalSetting's guild garden, the user: "onions and turnip first"; they grew as the lavender and
    cabbage fields): two raised-bed crops in `vk_helpers` beside the others. **`SM_VK_Crop_Onion`** (`crop_onion` /
    `onion`; 3,864 tris): 6 ridges of 9 golden bulbs (a 7-sided lathe, `BREAD`, smooth) on the ridge tops, each with 4-5
    tubular leaves as twisted ribbons on `LEAF` (two-sided), flopping over at the tips. No red onions: `CLAY` is not in
    `full_rebuild`'s smooth list. **`SM_VK_Crop_Turnip`** (`crop_turnip`; 4,298 tris): 7 x 7 roots, a lathe dome with
    the goods atlas's `turnip` (white below, purple shoulders), each under a rosette of 4 `ivy` foliage cards leaning
    out -- the crop atlas's `leafy` cell (the carrot tops) read as grass. Both use the frame-first material order of
    entry 105. Exported, Build Prefabs (the two). Preview scene `Crops_Preview` (with the carrot and cabbage fields).

112. 2026-10-17 (the user: "go for the ores"; MedievalSetting's ore spots were recoloured kit rocks). First try: coal
    and silver added to the mine kit's vein family (banded lumps); the user: "these don't look good, we need better ones"
    -- reverted (code, masters, package files). **Ore nodes** in the nature kit instead: `SM_VK_Ore_Iron` (520 tris),
    `SM_VK_Ore_Coal` (520), `SM_VK_Ore_Silver` (1,200), about 2.0 x 1.5 x 1.0-1.2 m (`make_ore_node` in vk_nature,
    `NATURE_SPECS` sharp 40 deg): a broad chiselled boulder and two smaller ones in ore-bearing rock, 10 nuggets breaking
    out of their front (-y) and top, 4 loose before it -- iron rounded rusty lumps, coal angular black blocks, silver
    nuggets each with 3-4 crystal shards (`ore_shard`). The rock is `T_VK_Ore<Kind>` (`vk_texgen.gen_ore`: gen_rock's
    chiselled rock, cooler and bare, with the ore painted in -- iron rust bands and blotches, coal black strata with
    glinting flakes, silver thin bright veins over blue-grey galena; zero-crossing veins of plain noise curled into
    worm loops, so they are stretched, `ax` 4); the nuggets the same texture tinted (`ORE_TINTS`, pbr_material `flat`;
    silver barely metallic -- a metal reflected the dark and read grey). Six slots 59-64 (`ore_material`). The front is
    Unity +Z: MedievalSetting's `GatherDef.facing` (new) turns it out of a cave wall (0) or, at a cliff marker that faces
    the cliff, to the camera (180). Preview `Ores_Preview` (the old vein row hidden). `renders/wip/ore_nodes.png`.

113. 2026-10-17 (the user: "a worked out node and new herbs are good ideas ... some kind of gathered plant for the
    scorched lands"; gem icons come later from a diffusion model, no gem models). **Worked-out ore nodes**
    `SM_VK_Ore_<Kind>_Spent` (620 tris each; `make_ore_node(..., spent=True)`): the same boulders in the kit's plain
    `ROCK`, a broken stub of ore sunk where each nugget was, rubble before it; MedievalSetting shows one while the ore
    grows back (`GatherDef.spent`). **Ghostpipe** `SM_VK_Plant_Ghostpipe` (1,700 tris, 0.72 x 0.58 x 0.34 m;
    `make_ghostpipe` / `gp_stem`): six clumps of waxy white stems bending into nodding bells, slot 65 `GHOSTPIPE`
    (`ghostpipe_material`: flat white, a faint blue-white emission 0.35 so it reads in the barrow's dark) -- the Hollow
    Barrow's crypt herb, a new item (the user's call; its use undecided). **Fireweed** `SM_VK_Plant_Fireweed` (1,132
    tris, 0.6 x 0.6 x 1.28 m; `make_fireweed`): eight tall stems, narrow leaves spiralling up them, a magenta flower spike
    on three crossed cards; its own sheet `T_VK_Fireweed` (`vk_leafgen.paint_fireweed`), slot 66 `FIREWEED` (two-sided)
    -- the Burnt March's plant (a placeholder item: "look only for now"). `kit_mats()` returns 67. Previews: the spent
    row in `Ores_Preview`, ghostpipe on the dark floor and fireweed in `Yarrow_Preview`.

114. 2026-10-17 (the user: "a better resource for stone ... the current one is stone already cut lying on the floor ...
    it can't be a quarry on each map"; models only, the game side left alone). **Stone node** `SM_VK_Stone_Node` (927
    tris, 2.3 x 2.2 x 1.1 m; `make_stone_node` in vk_nature): a natural boulder being worked the medieval way -- split
    clean in two (the same boulder seed built twice, each half cut at x 0 and set 0.13 m off it), the halves' inner faces
    fresh rock (`STONE_FRESH`, slot 67: `fresh_stone_material`, the kit's rock texture paler and warmer) against a mossy
    weathered skin (`ROCK_MOSSY`); a row of five iron wedges in dark slits across the right half (set on the surface by a
    BVH ray); three rough-hewn blocks and chips before it. **`SM_VK_Stone_Node_Spent`** (392 tris, 0.52 m high): the
    halves split down low, their tops fresh rock, more chips, no wedges or blocks. The cut squashed vertices together
    and the slivers streaked the split faces: `remove_doubles` 3 cm + `dissolve_degenerate` after the cut, then re-mapped.
    A first try (one outcrop with a split-off slab leaning off its front) did not read: the slab merged with the rock.
    Preview: the bottom row of `Ores_Preview` (with the old `SM_VK_Pile_Stone_2` beside it).

115. 2026-10-17 (MedievalSetting's coming areas, the abandoned monastery and a castle's inside; the user: "build the
    missing door pieces first: full-height double leaves, the pointed single Ashlar door, and a broken/ajar leaf").
    **Full-height double leaves**: the wide doors' Full walls had openings but only the Cut exits had leaves.
    `vki_leaf_tall` (vki_fam_stone): planks as prisms whose 3-point tops follow the arch over them, 1 cm under it
    (`vki_sto_wide_full_top`: Stone's segmental arch; `vki_ash_wide_full_top`: Ashlar's pointed one), straps at 0.36 /
    1.12 / 1.88 on both faces, the ring at 1.02 -- `SM_VKI_Leaf_Wide_Full_L/R` (0.89 x 2.50, 628 tris) and
    `SM_VKI_Leaf_Wide160_Full_L/R` (0.795 x 3.39, pointed). **Single pointed door** `SM_VKI_Wall_Ashlar_Door_150_Full`
    (1,476 tris) / `_Cut` (400; `vki_ash_door1`): the Stone door's clear 0.84 (x 0.33-1.17), two narrower orders
    (0.12 / 0.22), a DRESS lintel 2.205-2.34 (inset 8 mm in y: T5S flagged it coplanar with the inner ring) and a
    recessed tympanum filling the pointed arch (apex 2.85) -- so the existing `Leaf_Plank_Full` / `_Cut` hang in it
    (socket at the inner order's step, y -0.09; `vki_leaf` names them). **Broken leaves** `SM_VKI_Leaf_Wide160_Full_
    Broken_L` and `SM_VKI_Leaf_Plank_Full_Broken` (428 tris; `vki_leaf_break`): the meeting-edge plank gone and the next
    snapped with a splinter, the straps ending with the wood, sagged 7 / 6 deg in their plane about the lower strap (the
    free corner on the floor), hanging ajar 38 / 55 deg, darkened; static (`vki_leaf_state` "broken"). A first try with
    the gap in the middle left the snapped meeting-edge plank floating on the bottom strap. Existing pieces rebuild
    identical; `vki_test_pieces` clean. Test wall: scene `WS_vki_doors`. **Not done:** the Full wide walls' metadata
    still lists no `vki_leaf` (the generators will not hang the new leaves by themselves), and the Ashlar
    `DoorWide_300_Cut` lists `Leaf_Wide_Cut_L/R` though its leaves are the narrower `Leaf_Wide160_Cut` (the plans use
    Wide160).

116. 2026-10-17 (the user, on the 4.5 m Ashlar wall: "follow your order" -- an open arch and a tall hearth first, the
    castle's hall tried with the Ashlar walls before any tall Stone set). **`SM_VKI_Wall_Ashlar_Arch_300_Full`** (1,808
    tris) / `_Cut` (516): `vki_ash_door` now takes a spec and `arch=True` (the wide door rebuilds identical) --
    `VKI_ASH_ARCH`: clear x 0.55-2.45 (1.9 m), spring 2.20, apex 3.67, orders 0.14 / 0.24, body over the outer ring from
    4.10; no leaf sockets, no exit trigger (`vki_arch` 1, `vki_nav` "door"). **`SM_VKI_Wall_Ashlar_Hearth_300_Full`**
    (3,306) / `_Cut` (2,330; `vki_ash_hearth`, special): a hooded fireplace -- firebox x 0.48-2.52, 1.55 high, its back
    5 cm into the wall (BRICK, sooted); DRESS cheeks to y -0.80 and a lintel 1.55-1.85; a tapered hood (AshlarIn,
    `vki_sto_hexa`) from x 0.34-2.66 / y -0.83 at 1.84 to x 0.70-2.30 / y -0.45 at 3.40, a chimney breast on to 4.54
    with a CAP top; the first course dies into the cheeks, the second into the hood, the cornice into the breast; the
    Stone hearth's fire (logs, firedogs, embers, nine flame tongues 10% taller), no spit or cauldron; a hearth light
    (480 W) and `fire_large` FX in its metadata. Cut: cheeks, a front lintel course and cheek copings (CAP tops), the cap
    course behind, the fire open from above. T3 wants everything proud of the wall within x 0.33-2.67 (the posts' node
    zones); T5S flagged the cheeks' backs and outer faces against the lintel (lintel back 5 mm deeper, ends at 0.335).
    Test row: scene `WS_vki_doors`, y -7. Blender had Beasts' `hydra.blend` open (that session done, nothing unsaved):
    switched back with the user's OK; a kit text pushed into it by mistake was removed before.

117. 2026-10-17 (the user: "proceed" -- the castle's hall tried with the Ashlar walls before any tall Stone set).
    **`VKI_Castle_Hall`** (new text `vki_rooms_castle`, loaded after `vki_rooms_mine`): the great hall, 10 x 6 cells
    (15 x 9 m), Ashlar perimeter with pillar corners and side rhythm posts -- the hooded hearth (`S1` =
    `Wall_Ashlar_Hearth_300_Full`) in the north wall between four tall lancets, lancets in the side walls, the wide exit
    south; trestle tables with forms down both sides, an open aisle with a rug, pricket candles by the hearth, a weapon
    rack and an armour stand west, a chest east; FlagWarm floor, Day preset. `vki_check`: 0 errors (palette and R-occ6
    window warnings only). `SM_VK_Prop_ArmorStand` joins `VKI_REUSE` (wall_floor, hug; code AS). Game shot:
    `renders/interior/VKI_Castle_Hall/`. **Verdict:** the Ashlar walls carry a castle hall -- no tall Stone set needed
    for now. **Castle gaps it shows:** the lancets' stained glass reads as a chapel (a plain leaded-glass style for the
    lancets would fix it), and the hall wants a lord's chair or throne (only the dwarf throne exists), a high table on
    a dais (the chapel's dais pieces), banners or tapestries on the walls, a chandelier; the towers want a spiral
    stair.

118. 2026-10-17 (the user: "monastery set" -- the abandoned monastery's pieces). New text `vki_props_monastery`
    (after `vki_props_library`): **`SM_VKI_Prop_ChoirStall_300`** (1,372 tris; three seats between shaped arm
    partitions with carved knobs, a panelled back to 1.60, a pale cresting rail, four pinnacles; wall_floor) -- a first
    version with a canopy to 2.55 read as a dark wardrobe from the game camera and hid its seats, and the pew's
    poppyheads on its arms cost 2,476 tris; **`SM_VKI_Prop_Pew_300_Broken`** (1,236: the right end board fallen outward,
    the seat's right half down to the floor, the back rail snapped, the right post gone, all built from the pew's parts
    moved by `vki_mon_part` / `vki_mon_about`); **`SM_VKI_Prop_Pew_300_Overturned`** (the pew tipped onto its back, 7 deg
    askew); **`SM_VKI_Prop_FallenBeam`** (472: a 4.2 m tie-beam, one end on a rubble heap, splintered ends -- wedges
    in a right-handed frame, their bases staggered, T8 / T5S --, a broken rafter, planks; explicit colliders for the beam
    and the heap); **`SM_VKI_Prop_Desk_Scriptorium`** (634: a slanted writing desk, manuscript, inkhorn, quill, book,
    candle 30 W); **`SM_VKI_Overlay_GlassShards`**. In vki_fam_ashlar: **`SM_VKI_Wall_Ashlar_Lancet_150_Full_Broken`** /
    `LancetTall_..._Broken` (`vki_ash_glass_broken`: a jagged rim of shards round the frame, a quarter of it empty,
    each shard off its neighbour's plane; `vki_cut_to` the Lancet Cut). Test room **`VKI_Monastery_Church`** (new text
    `vki_rooms_monastery`): 8 x 6 Ashlar, broken lancets north (`S2`) and west (`2`), choir stalls, pews whole, broken
    and overturned, the beam across the crossing, shards, rubble; `vki_check` 0 errors. **Gotcha:** the room BFS boxes
    every collider square to the room (rotations are taken as multiples of 90): a beam turned 32 deg boxed its whole
    diagonal and cut the altar off -- keep long props near 0 / 90 deg in plans. The altar stays pristine (an
    abandoned one stripped of its linen and candles would read better).

119. 2026-10-17 (the user: "stuff for an abandoned monastery, the one in the game will be abandoned (but keep the new
    ones for the set)" -- the intact pieces stay; abandoned twins beside them, in `vki_props_monastery`):
    **`SM_VKI_Prop_Altar_300_Stripped`** (500 tris: bare DRESS mensa, its front corner broken off and lying by it, a torn
    strip of the frontal and a rag of it on the floor, a candlestick toppled on the mensa, the cross on the floor;
    nothing lit; a tight collider over the block, the floor bits walked over), **`CandleStand_Pricket_Fallen`** (the
    stand built, its flame deleted -- `vki_mon_drop_glow` -- and tipped 84 deg), **`Desk_Scriptorium_Fallen`** (the
    desk's frame on its own, `vki_mon_desk_frame`, tipped onto its front; the manuscript, a book, the inkhorn, the
    quill, the candle and leaves spilled round it), **`Bookcase_150_Ransacked`** (a case with its third shelf broken
    out and slid down onto the second, a few books left, the rest heaped at its foot with leaves; collider over the
    case only), **`Cot_Broken`** (780: a plank cot tipped over the diagonal between two legs onto its snapped leg's
    stub -- the angle solved from the stub height --, the snapped leg by it, the straw pallet slid off, a blanket
    rag), **`RoofCollapse`** (960: a mounded heap of rubble and slates, two broken rafters, a cold daylight SPOT from
    6.5 m in its metadata; collider 2.0 x 1.6), **`Overlay_Pages`** (leaves and a torn open book; the book 1.5 mm under
    the first leaf, T5S). The intact `Desk_Scriptorium` rebuilds from the shared frame (same mesh). Test rooms (all
    `vki_check` 0 errors): `VKI_Monastery_Church` now with the stripped altar, the fallen stand and the roof collapse;
    new `VKI_Monastery_Scriptorium` (Stone 6 x 4: the ransacked and the sparse bookcase, the fallen desk, leaves, a
    pile of books) and `VKI_Monastery_Dorter` (Stone 6 x 3: broken cots, rags). The cots' tilt barely reads from the
    game camera (their pallets on the floor carry it).

120. 2026-10-18 (the user: "more for the abandoned monastery"). In vki_fam_ashlar: **`SM_VKI_Wall_Ashlar_Ruin_150/300_Full`**
    + `_Cut` twins (intact 0.35 ends, the middle broken down in steps on the 0.25 course grid -- dressed stone breaks
    at its beds -- to 1.25-3.75 (300) / 2.0-3.75 (150); one body panel to 1.25 with the ends and steps stacked on it so
    Full = Cut below 0.65 (T2); the second course passes only under tops of 3.25+; loose blocks on the break, fallen
    blocks, a length of course and grit on the floor in front, also on the Cut twin; 1,672 / 676 tris);
    **`SM_VKI_Wall_Ashlar_Arcade_300_Full`** (the cloister's garth side: two pointed openings 1.0 clear, spring 1.90,
    over a dwarf wall whose sill is the first course, a coupled column, one ring of voussoirs; `vki_cut_to` the plain
    Cut; 2,360) and **`_Full_Broken`** (the arches fallen: two springers a pier, the colonnettes snapped, voussoirs,
    the capital and a length of shaft on the floor; 1,788). New material **`M_VKI_AshlarBlock`** (StoneBlockIn x1.30,
    the AshlarIn mean): the ruins' break tops and loose blocks -- grey StoneBlockIn and brown Dress both read wrong
    against the pale wall. In vki_props_monastery: **`SM_VKI_Overlay_Overgrowth`** (moss, weed tufts, ground ivy),
    **`SM_VKI_Overlay_Moss`**, **`SM_VKI_Prop_Ivy_Wall`** / **`_Tall`** (wall_hung, hanging ivy, highest leaf 2.84 / 4.34 =
    the host's H - 0.16), **`SM_VKI_Prop_Font_Broken`** (the chapel font's stem snapped, the bowl on its side with its
    mouth to the room, dry), **`SM_VKI_Prop_Statue_Saint`** (2.2 m hooded monk in prayer, for the set) and
    **`_Toppled`** (on its back in front of the plinth, the head rolled off). Moss = new **`M_VKI_Moss`** (T_VK_Moss
    tinted dull) on the ASH slot; weeds and ivy are the exterior foliage atlas (`FOLIAGE`, two-sided cards, 2 tris
    each via `vki_mon_card`) -- the first VKI pieces with open cards, so **T7 / T8 now leave faces on
    `VKI_CARD_SLOTS` (FOLIAGE, CROPS) alone**. Moss patches use smooth lobed outlines (per-vertex noise read as paper
    cut-outs) and staggered bottoms (T5S). New scene **`VKI_Monastery_Cloister`** (8 x 4, walk + ApronGrass garth
    between arcades, the open Arch_300, the fallen arcade; the ruin on the north wall), ivy and moss added to the
    church and the dorter; all four monastery rooms `vki_check` 0 errors. **Gotcha:** `bmesh.ops.create_icosphere`
    kills older python BMVert references (their hashes change), so a `before = set(bm.verts)` / `not in before`
    collection after an icosphere takes in every vertex of the piece (the toppled saint moved its plinth too): use
    `vki_ash_new(k, build, M)` (a temporary int layer marks the old vertices; moves and drops the new part).
    Wall-hung props are placed in front of their wall (the host search looks ahead of the point), not on its line.

121. 2026-10-18 (the user: "now the castle pieces?" -- the castle hall's gaps). New text **`vki_props_castle`** (after
    `vki_props_monastery`, package "castle"): **`Prop_Throne_Castle`** (924 tris: dark-oak chair of estate, gilt
    finials, knobs and roundel, red cushion, footstool; `vki_seats`), **`Prop_Chair_Carved`** (724: the high table's
    chairs), **`Prop_Table_High_300`** (the trestle table under a white linen cloth falling 0.30 at the front and ends,
    a red runner from the atlas' `runner` cell; `vki_table_z` on the runner), **`Prop_Hanging_Estate_240`** (the cloth
    of estate: the atlas' `hanging_heraldic` cell on an iron rod at 2.84, behind the throne), **`Prop_Tapestry_300`**
    (the spec's P2 piece at last: `tapestry_millefleur`, `vki_mount_ref` top, rod at H - 0.25), **`Prop_Banner_Castle`**
    (swallow-tailed, per pale red / blue with the chevron and crosses gilt, rod at H - 0.35), **`Prop_Chandelier_Ring`**
    (eight candles at 2.60, chains to 4.30, one 160 W light, no collider) and **`Prop_Display_Arms`** (heater shield in
    the arms over two crossed swords). The arms (per pale gules and azure, a chevron and three crosses or) are the
    hanging cell's, so hanging, banners and shield agree. New materials `M_VKI_BannerBlue` (flat, the clan banners'
    pattern) and **`M_VKI_Leaded_In`**: plain leaded glazing, `T_VK_Leaded` from `vk_texgen.gen_leaded` (the stained
    set's lattice, pale crown-glass quarries), style `stained: "Leaded"`. Rooms take **`lancet_style`** (like
    `window_style`, for Lancet / LancetTall pieces), ported to Unity's `KitRoom.WallStyle` too. `VKI_Castle_Hall`
    reworked: a dais across the north end with the high table, throne and chairs, the cloth of estate, tapestries in
    the north corners, the hearth moved to the east wall (NS token "1"), leaded lancets, banners, the chandelier over
    the aisle; `vki_check` 0 errors (warnings: palette, R-occ3 the chandelier's chain, R-occ6 the candle stands, one
    plan code). **Gotchas:** `vki_dpr_rod(a, b, w, mi, d)` for a rod lying in a wall's plane: `w` is its depth off the
    wall, `d` its width in the plane (the swords' guards first went 0.22 m deep, through the shield). A gold-trimmed
    piece cannot also use the textile atlas (both are the TEXTILE slot): the hangings' rod knobs are BRONZE.

122. 2026-10-18 (the user: "ok, go on" -- the castle's newel stair). In vki_props_castle: **`SM_VKI_Stair_Up_Spiral_300`**
    (592 tris), **`_Tall`** (900: 22 risers for a 4.5 m storey) and **`SM_VKI_Stair_Down_Spiral_300`** (968), the
    stair pair's contract (min corner, `vki_link` / `vki_pair` / `vki_trigger` / `vki_spawn_local`), footprint 3 x 3
    (2 x 2 cells): stone wedge steps (22 deg; 15 tall) round a DRESS newel at the centre, lapping 3 deg / 6 cm under
    the next, rising counter-clockwise from the east, so the entry is the south-east quadrant -- open at floor level
    under the last steps, where the trigger and the arrival are; steps within r 1.12 (walls on the other sides keep
    their proud line). Up: to the ceiling plane, the top steps darkened, an iron handrail while it stays under it.
    Down: a landing flush with the floor (4 mm under it), ten steps winding down (darkening with depth^1.5 so the first
    ones read), a VOID disc at -2.40, a DRESS kerb and an iron rail round the hole but at the landing. Its floor is
    **`SM_VKI_Floor_300_Spiral_Q00..Q11`** (the slab with the round hole 1.18, Q parity of the footprint's min corner,
    rotation 0; T9 budget kind Q300Spiral 256). Rooms: a stair record's sixth field "Spiral" / "SpiralTall"
    (`vki_rooms_stair_spiral`, `vki_rooms_stair_local_cells`, `vki_rooms_stair_piece`); its 2 x 2 cells, no rhythm
    posts round its footprint, the holed floor under a down stair, the floor-coverage check skips it like a hatch --
    all ported to Unity's `KitRoomLayout` (`StairSpiral`, `StairLocalCells`, `StairPiece`; its floors match Blender's
    for both test storeys). Scenes **`VKI_Castle_Tower_F0`** (guard room, the stair up) and **`_F1`** (chamber, the
    stair down), Stone 4 x 4, linked; `vki_check` 0 errors and no warnings. Not done: no left-hand (clockwise) twin;
    the up stair's darkened top reads as a dark block in the ceiling corner.

123. 2026-10-18 (the user: "do we have a tileset for the interior of a building in a warcamp? ... orcs" -> "full orc
    interior set"). A new wall family **`Orc`** (class O, H 3.0; text `vki_fam_orc`, after vki_fam_dwarf): rough logs
    standing side by side with mud in the gaps -- the body's texture, new **`T_VKI_OrcLogs`** (`vki_tex.vki_gen_orclogs`:
    four logs a 1.5 m tile, round shading and a highlight down each, bark streaks, knots; six logs read as planks) on
    **`M_VKI_OrcLogs`** (style `OrcLogs`) --, a split-log rail 0.86-1.00 lashed with rope (full depth on Cut walls,
    proud strips on Full ones; the lashings stay under 0.995 so Cut walls pass T1), a log wall plate 2.84-3.00, wobble
    0.012, CAP = WoodDark. 21 masters: `Plain_150A/300` Full + Cut, **`Plain_150B_Full`** (a hide stretched on a pole and
    a skull over it; the B rule's family lists in vki_rooms and Unity's KitRoomLayout now include Orc),
    `Window_150` (unglazed, split-log jambs, stick bars, a hide rolled up; Cut: the rail notched 4 cm -- jamb stubs
    broke T1 -- and the window's three bodies on both, so Full = Cut below 0.65), `Door_150` (log frame, a skull on the
    lintel) and **`DoorWide_300`** (the hall's gate, a skull between two tusks) with new leaves **`Leaf_Orc_Full/_Cut`**,
    **`Leaf_OrcWide_Full/_Cut_L/_R`** (vki_leaf_tall's planks, dark, iron spikes on the room-side straps), posts
    Corner (a round log r 0.30 with a rope band) / Mid (a squared log) Full + Cut; registered in VKI_FAMILIES,
    VKI_H_FULL, VKI_AMP, VKI_POST_PRIO (after Mine), VKI_FAMILY_SLOT_MATS, VKI_WALL_MATS. Furniture in
    vki_props_orc: **`Prop_Orc_Throne`** (sharpened bark logs, a great skull between tusks, a fur; seats),
    **`Prop_Orc_Bunk`**, **`Prop_Orc_Table_240`** + **`Prop_Orc_Bench_240`**, **`Prop_Orc_WeaponRack`** (cleavers, an axe,
    spears, a hide shield), **`Prop_Orc_Trophies`** (wall_hung: men's shields, crossed spears, skulls, a helm),
    **`Prop_Orc_MeatRack`**, **`Prop_Orc_Cauldron`** (the cook fire, light) and **`Overlay_Orc_Furs`**. Test scene
    **`VKI_Orc_Hall`** (new text `vki_rooms_orc`: 10 x 6, Night, the gate south, the throne between the war standards,
    the war table, the cauldron, tables, bunks, racks, torches): `vki_check` 0 errors, 0 warnings; Unity's
    KitRoomLayout gives the same walls and posts. Not done: the game's `OrcHold_Hall` still uses the generator's
    Townhouse shell (switch it to the Orc family / the kit room in MedievalSetting's InteriorsMenu).

124. 2026-10-18 (the user: "1 and 3" -- more orc rooms, then the game's warlord hall). In vki_props_orc:
    **`Prop_Orc_Forge`** (a sooted clay hearth on a footing of stones, glowing coals, a hide bellows on a stand; light
    180 W, keep its +X side clear), **`Prop_Orc_Anvil`** (on a stump, a half-beaten cleaver, hammer, quench bucket),
    **`Prop_Orc_ScrapPile`** (loot to melt: blades, a helm, a shield rim, cleaver blanks), **`Prop_Orc_Altar`** (the
    shaman's: a slab on boulders, a great skull with a candle, a bowl of blood -- new `M_VKI_Blood`, water style
    `Blood` --, a bone bundle; candle light), **`Prop_Orc_HerbRack`** (wall_hung drying herbs, a skull, bone charms) and
    **`Prop_Orc_Stocks`**. Fix: `Prop_Orc_Cage_Open`'s use point lay inside its own collider (the swung door): now
    local y -2.15. Four rooms in vki_rooms_orc (Night, Orc family): **`VKI_Orc_Barracks`** (8 x 4), **`VKI_Orc_Forge`**
    (6 x 4, the wide gate), **`VKI_Orc_ShamanHut`** (4 x 4), **`VKI_Orc_Pen`** (6 x 4: both cages, the stocks, the
    dungeon's wall chains with a seated skeleton); `vki_check` 0 errors (Night floor-level warnings only).
    The game's `OrcHold_Hall` now uses the Orc family (MedievalSetting InteriorsMenu.WarlordHall, not checked in).
    **Gotcha:** new pieces reach KitRoom (the game's interiors) only after `KitRoomTools.BuildRules` (Tools >
    Medieval Kit > Build Interior Rules) rewrites Generated/KitInteriorRules.asset, and its prefab map is cached
    in memory: `Resources.UnloadAsset` the asset (or reload the domain) before building a room with them.

125. 2026-10-18 (the user: "props to the market district ... for the capital?" -> "only the stalls first"). Seven new
    trades in vk_helpers `STALL_TRADES` (each registers `SM_VK_MarketStall_<Trade>`; goods in `stall_wares_capital`,
    helpers `_open_sack`, `_bottle`, `_book`): **`_Spicer`** (open sacks with heaped spice, jars, garlic and chilli
    strings), **`_Butcher`** (block and cleaver, cuts, hams and sausages hung), **`_Jeweller`** (cloth counter, open
    strongbox, gold coins and stacks, a ring tray, a balance, goblets, a locked chest), **`_Armourer`** (helms on
    stands, gauntlets, three shields at the front, a hauberk on a stand, swords in a barrel), **`_Apothecary`**
    (bottles, mortar, herbs in a basket and hung, a book), **`_Vintner`** (two casks on cradles, heads and taps to the
    customer, cups, jug, bottles) and **`_Scribe`** (book stacks, writing slope, inkpot and quill, scrolls, a seal
    box). 2.7k-4.0k tris each (the older stalls run 2.7k-5.3k). Exported; prefabs built in MedievalSetting
    (Generated/Prefabs/VK/MarketStall). Not placed in any map yet.

126. 2026-10-18 (the user: "rest of the market"). New module **`vk_mod_market`** (prefix `mkt_`, last in `KIT_MODULES`;
    borrows `twn_arch_*` and `def_beam`). **`SM_VK_MarketHall`** (Saltmere's covered market, one piece: an open ashlar
    arcade, 3 round arches a long side and 2 an end, plain unbevelled voussoirs, a flagged floor 0.12 up, planked
    ceiling on beams, two lanterns; the kit's own `timber_frame` walls above at z 3.8 so it matches the houses; one
    light hipped roof `mkt_roof` on the kit profile `roof_z` (planar between the ridge, wall-line and eave rows, ~1.2k
    tris instead of ~16k for Roof_Hip x2 + Roof_Mid) and a clock lantern with a bell `mkt_lantern`; wall lines 9 x 6,
    15.8 m, 19.4k tris -- the timber walls are 11k of it), **`SM_VK_Prop_Monument`** (3 steps, ashlar pedestal, four
    bronze plaques and a laurel, a smooth bronze crowned king with his sword point down; 2.1k),
    **`SM_VK_Prop_WeighBeam`** (the tron: gallows frame under a tile hood, 1.9 m balance with chained pans, a wool sack
    against iron weights, the weigher's bench and ledger, sacks; 2.8k), **`SM_VK_Prop_Hurdle`** (one 2 m wattle
    hurdle), **`SM_VK_Prop_Pen`** (4 x 3 m hurdle pen, gate swung open, straw, trough, tally board; put
    SM_VK_Animal_Sheep / _Pig in it) and **`SM_VK_Prop_CrierStand`** (1.1 m platform, back steps, rails, the city's
    cloth over the front rail, hand bell, proclamation). Already in the kit and not remade: Pillory, Stocks, HitchRail,
    Bunting_6/9, Festoon, Cart (a hand cart), Stage, MarketCross, Fountain, NoticeBoard. Shared change: the rebuild's
    smoothing rule keeps smooth-flagged **BRONZE** faces smooth (like GOODS), so `bell()`'s bells turn smooth the next
    time their pieces (Roof_Cupola, the skyline bell tower) are rebuilt. Exported; prefabs built in MedievalSetting
    (VK/MarketHall, VK/Prop); not placed in Saltmere_Market (the other session's map).

127. 2026-10-18 (the user: "we need more tiles for a docks district, and props" -> "Round 1": the harbour tiles).
    **Sea datum:** the sea is water cells one terrain level below the quay's land: water -2.1, bed -3.0 below the land
    (the terrain's WATER_Z / BED_Z on the lower level). **Quay tiles** (new text `vk_terrain_quay`, after `vk_terrain` in
    `TERRAIN_TEXTS`): dual-grid tiles like the cliffs, `SM_VKT_Quay_Edge_A`, `_Edge_Stair` (water stairs along the face to
    a landing 0.25 above the water), `_Edge_Slip` (a 2 m slipway of setts, 0.45 a metre, running 3 m past the tile into
    the sea), `_Outer_A`, `_Inner_A`, `_Saddle_A`: the face on the cell edge, coursed (every other course 12 mm proud),
    jittered coping stones as a kerb +0.08, quoins at convex corners, the land top and the sea bed in M_VK_Terrain (the
    map's ground), the masonry in M_VKT_Stair (object space, no UVs: survives the terrain merge; the tide band and the
    wet stone darken by TCol AO). 96-256 tris. `TGrid.quay` (land cells: 1 wall, 2 stairs, 3 slip; stairs/slip go on an
    Edge vertex whose two land cells both carry the flag); `tk_tiles` asks `qy_pick` first: a quay vertex gives a Water
    quad at the sea's level and a Quay tile on the land's layer instead of a Shore plus a Cliff layer. `qy_demo()` builds
    a sample harbour. **Harbour props** (new module `vk_mod_harbour`, prefix `hbr_`, on the wall line facing -Y at the
    land's height): `SM_VK_Harbour_Bollard`, `_Ring`, `_Fender`, `_Ladder`; `SM_VK_Jetty_Deck` / `_End` / `_Landing` (the
    river piers' convention, along +X, deck +0.05, piles to -4.0, slimy to the sea's water line; the landing: seven steps
    to a stage 0.35 above the water); `SM_VK_Breakwater` (3 m mole: paved crest, quay face on the harbour side -Y, parapet
    and armour rock to the bed on the sea side +Y) and `SM_VK_Breakwater_End` (its round head with the harbour light: a
    stone tower, railed gallery, open iron lantern with a fire basket). Exported; prefabs built (VKT/Quay, VK/Harbour,
    VK/Jetty, VK/Breakwater). **Not wired in Unity:** KitVillage's terrain only raises ground and has no water; a docks
    map needs a sea mode there (sea cells lowered to their bed, a water plane, `qy_pick`'s rule picking the Quay tiles
    for layers over the sea, no cliff dressing on them, the wall props along the quays).

128. 2026-10-18 (Saltmere session's brief: "add a sea to the Unity kit's outdoor terrain so a docks map can use the new
    harbour tiles"). **Unity only** (`KitVillage.Terrain.cs`, `KitVillage.cs`, `KitVillage.Grass.cs`, `KitNavBake`,
    `KitVillageEditor`); docs in `LEVEL_BUILDING.md` ("The sea"). **Convention:** sea cells are level 0 and water, the
    docks' land a level-1 terrace (the quay tiles' frame: land top 0, water -2.1, bed -3.0 = the sea's -0.6 / -1.5).
    Layout keys in `terrain`: `sea` (shapes; `quay`, default true, flags every land cell touching them as a wall, as
    `qy_demo` does), `quays` (shapes with `kind` wall / stairs / slip / none = `TGrid.quay` 1/2/3/0), `quayDress`.
    `QuayPick` ports `qy_pick` (hi = lo + 1, sea corners at lo, land at hi, a land corner flagged; Edge with both land
    flags 2 -> `_Stair`, 3 -> `_Slip`) and puts the tile on the land's layer in place of the cliff layer; the tiles merge
    with the rest (`Merge`, factored out of `Terrain()`). The ground mesh drops to the bed under the sea (`SeaGround`:
    3 cm under the quay tiles' own bed against raised land; a 3 m beach slope against level-0 land), relief flattens
    toward the sea (`TerrainNear`). `Sea()` lays `SM_VKT_WaterQuad` on every grid point a sea cell meets, held to the grid
    beyond it so the water runs through the margin; no collider; saved as `<Map>_Sea.asset`. `Height` over the sea is the
    water's surface; props take `"z"`; a prop standing in the sea gets mesh colliders (`SeaSurface`: jetty decks and the
    mole's crest are walked on; decks are "soft" on land). Navmesh: `UnderSea()` rects Not Walkable up to -0.45 (the
    stairs' landing at -0.35 stays). `DressCliffs` skips edges ending at a quay point and the foot dressing of cliffs
    into the sea; `DressQuays` puts `SM_VK_Harbour_Bollard` (box collider) / `_Fender` / `_Ring` on the wall lines facing
    the water, 0.8 m from corners and 1.7 m from stairs and slips. Forest, scatter (1.5 m) and grass (0.8 m) keep off the
    sea; the control map paints its bed and shore dirt. Maps without `sea` build exactly as before (rng draws unchanged).
    **Tested** with `Documentation~/examples/HarbourTest_layout.json` (the `qy_demo` grid, its jetty, mole, ladder and
    rowboat) built by `BuildVillage` in a throwaway scene (deleted after): 25 quay tiles, walk test ok, the stairs'
    landing, the slipway above water, the jetty's end, the mole's crest and the island all reached from the arrival, no
    navmesh on the bed or water; imported into Blender: 500k vertical rays over the land found no hole at any tile seam
    (bar the slipway's own cut) and no ground above the quay tiles' bed. One 5 m2 navmesh island "on top of things" is
    left (likely the harbour light's gallery). **Not done:** the land at a map's edge still ends 1.5 m past the grid
    with no face (the terrace must end inside the clearing); no Unity-side render (the editor rule).

129. 2026-10-18 (the user: harbour "round 2", after the sea mode of 128). More in `vk_mod_harbour`: **`SM_VK_Ship_Cog`**
    (17 m merchant cog: clinker hull from `wat_hull`, deck fitted to the inner skin (`hbr_deck`/`hbr_y_at`), cargo
    hatch, castles fore and aft, 16 m mast, crow's nest, furled square sail, shrouds and stays, bowsprit, rudder and
    tiller, an anchor; 5.2k) and **`SM_VK_Boat_Fishing`** (7.5 m, mast and furled sail, nets, baskets, oars; 3.1k),
    both with the origin at the waterline (place them at the quay's land -2.1); on the quay (origin on the land, front
    -Y): **`SM_VK_Harbour_Crane`** (braced post, jib 3.4 m over the water, windlass, a netted load on the hook),
    **`_Gangplank`** (from the quay edge 4.2 out and 0.8 down to a moored deck), **`_Capstan`**, **`_Anchor`** (lying, with
    chain), **`_RopeCoils`**, **`_TarCauldron`**, **`_Booth`** (the harbourmaster's), **`SM_VK_Cargo_Crates`** (under a cargo
    net) and **`_Bales`**, **`SM_VK_Ship_Hull_Stocks`** (a 9 m hull being built: ribs, lower strakes, keel blocks, shores,
    staging); **`SM_VK_Harbour_Buoy`** at the waterline. Gotcha: `wat_hull` with a pointed bow needs a flat-bottom width
    of 0 everywhere (the tip's station has none, rows must match). Built in a background Blender (`blender -b`): the
    shared Blender had another session's unsaved scene open. Exported; prefabs built (VK/Ship, VK/Boat, VK/Harbour,
    VK/Cargo).

130. 2026-10-18 (the user: "a cartoony somewhat water shader like the one I have in the voxel game ... foam at the
    borders", and boats set low must not fill with water: "we need a way to create negative space ... make them in the
    level"). **Unity only.** New **`Shaders/KitSea.shader`** (`MedievalKit/KitSea`), a port of VoxelRealm's
    `VoxelWaterLit` to URP's main light: refraction of the opaque scene, the domain-warped five-wave ripple with its
    distance crossfade, gusts and calming; colour by the water's depth over the bed in hard bands (`_ColorBands`);
    hard-edged ragged foam where the scene sits just behind the surface (quay walls, hulls, piles, the beach) plus a
    dashed second line further out; a stepped sun glint; the water takes the main light's shadows. Needs the URP Depth +
    Opaque textures (on in MedievalSetting's PC_RPAsset, off in Mobile_RPAsset). **Negative space:**
    `Shaders/KitWaterMask.shader` writes stencil bit 8 (ColorMask 0, ZTest LEqual, queue Transparent-1); KitSea (queue
    Transparent+1) skips those pixels. `KitVillage.SeaMasks()` (after `Props()`) slices every hull standing in the sea
    (`IsHull`: `_Ship_`, `_Boat_`, `_Rowboat`, `_Barge`) at the water's actual height where it floats, takes the convex
    outline of the crossings and fans it into one static mesh (`SeaMask`, saved as `<Map>_SeaMask.asset`), so a boat
    sits as low as its `"z"` puts it and stays dry inside. Materials `M_VKT_Sea` and `M_VKT_WaterMask` are made by
    `KitBuilder.BuildMaterials` only when missing (tune `M_VKT_Sea` in the inspector: a rebuild keeps it); the editor sets
    `KitVillage.seaMaterial` / `waterMaskMaterial`, and `Sea()` puts `seaMaterial` on the water quads (none: their own
    `M_VK_Water`). The HarbourTest example now moors the cog (at the water), a fishing boat sunk 0.2 lower and a buoy;
    built to MedievalSetting `Assets/KitTests/HarbourTest.unity` (sea 81 cells, the mask over 3 hulls; not checked in).
    Shaders compile with no messages; **not seen rendered** (no Unity renders by the editor rules): look at the test
    scene and tune `M_VKT_Sea`.

131. 2026-10-18 (the user: dock buildings, "this thread is for modelling, another one is building the city"). Round 3 in
    `vk_mod_harbour`, single pieces built from the kit's own walls through `mkt_put` (they match the houses), front -Y:
    **`SM_VK_Dock_Warehouse`** (6 x 9, gable to the quay: cart door, the loading door above, a hoist beam out of the
    gable with a bale on the rope; 35k), **`SM_VK_Dock_FishMarket`** (open timber shed 9 x 6 on stone pads, flagged
    floor, stone-topped tables with crates of fish, a hanging balance, trough, fish sign; 15k), **`SM_VK_Dock_Chandlery`**
    (6 x 6: stone shopfront with counter and awning, rope, lanterns and an anchor on the counter, timber storey, anchor
    sign on a bracket, barrels, coils, oars; 30k) and **`SM_VK_Dock_CustomsHouse`** (9 x 6: a three-arch ashlar loggia on
    the quay side with the officer's table, ledger and balance, goods under declaration, stone upper storey, the city's
    banners, hipped roof; 40k). New light gable roof `hbr_roof_gable` (planar on the roof_z profile, verge boards,
    gable triangles in a wall material or open). The stone walls' grid-cut panels are most of the weight (as in the
    town's houses). Built in a background Blender (the live one held another session's scene); exported; prefabs built
    (VK/Dock); not placed (the city session's maps).

132. 2026-10-19 (the user: "many of the new tiles have ZFighting problems, can you test them and fix those?"). New
    **`tools/vk_zfight.py`** (background Blender): same-facing faces of a piece in one plane (within 2 mm) that overlap
    and that a camera can see (rays escape from 2 mm off the overlap), per piece, plus qy_demo's assembled chunk for
    tile-to-tile overlaps; writes renders/zfight.json. Run over the 45 pieces of HANDOFF 125-131 and fixed: **quay
    tiles** (convex corners' quoins reached 1 cm into each other instead of stopping 1 cm short -- every quoin joint
    z-fought, in every assembled harbour; the course ledges of two walls overlapped at an inner corner; a saddle's two
    corner stones shared a top), **arch voussoirs** (`mkt_voussoirs`, market hall + customs house: their faces lay in
    the wall's planes and in each other's; every other stone now less proud, both faces off the wall, 12 mm lip under
    the crown), the **gable roof's** verge boards (crossed at the apex), the cog's castle rails and deck, the
    breakwater head's crest ring (on the drum) and parapet copings, the booth's walls (flush with the posts), the
    crier stand's skirts and cloth trim, the jetty's mid waling (flush with the braces), the pen's trough, the weigh
    beam's caps and ridge board, the hull-on-stocks trestles, the scribe's scrolls (coaxial) and the armourer's
    hauberk shoulders. Left (the kit's own, from before, 4-40 cm2 and mostly undersides): `wall_stone_window`'s
    lintel over its frame, the timber walls' plaster under their beams, shutter leaves meeting, the base stall's
    counter, `prop_trough`'s and `wat_fish_crate`'s bevelled corners, `wat_gunwale`. All 45 rebuilt, exported, prefabs
    rebuilt. **Maps already built with quay tiles must be rebuilt** (the terrain mesh is merged and saved per map).

133. 2026-10-19 (the user: "fix those too": the kit's older overlaps 132 left). Fixed in shared code:
    `window_frame`'s head beam (flush with the wall over the opening: every window piece; now 1 cm into the opening),
    `wall_stone_door`'s arch strips (the last overlapped the panel above), `corner_plaster`'s post (top flush with its
    cap), the base `market_stall` counter (flush with the posts: all 15 stalls), `prop_trough` (base and end boards
    flush with the sides), `wat_fish_crate`'s base (fish piles, the fish market), `wat_gunwale` (strake top level with
    the rim: drop 0.05 -> 0.06; rowboat, barge, fishing boat, cog) and the town's lintels (loading door, stone and
    plaster shops). Rebuilt every exterior spec in a background Blender and compared mesh hashes: 43 changed, among
    them `SM_VK_Chimney_Gable_H24/H58` and `SM_VK_TownWall_Tower_Round`, which were stale in the .blend (older than
    the code's z-fight batches of HANDOFF 98) and are now in step. All 43 exported and their prefabs rebuilt; vk_zfight
    clean on the base pieces. Left: contacts at the wall pieces' 3 m ends (the neighbour or a corner covers them) and the
    same joints inside the one-piece buildings (timber walls meeting at a corner, shutters at a joint; 4-100 cm2,
    undersides). See-through caps not re-baked (stale entries are made in play; the next player build bakes).

134. 2026-10-19 (the user: "more herbs that will be the ones used in chapters 2 and 3"; the user picked all eight).
    Nature specs (vk_nature, seeds 137-151), about twice life size like the others, `{"bark_ao":None}`:
    chapter 2 -- **samphire** `SM_VK_Plant_Samphire` (396 tris, 0.9 x 0.9 x 0.37 m: 40 jointed fleshy sprigs on crossed
    cards, a few reddening; the salt marsh), **angelica** `SM_VK_Plant_Angelica` (396 tris, 1.9 m: big compound leaves,
    purple-footed stems, green-white globe umbels on three crossed cards; monastery garden), **monkshood**
    `SM_VK_Plant_Monkshood` (472 tris, 1.3 m: deeply cut dark leaves, violet hooded flower spikes), **feverfew**
    `SM_VK_Plant_Feverfew` (1,430 tris, 0.64 m: lobed yellow-green leaves, bunches of white daisies; farmlands);
    chapter 3 -- **houseleek** `SM_VK_Plant_Houseleek` (2,428 tris, 0.55 x 0.3 m: 9 rosettes + 4 offsets of fleshy
    red-tipped leaves (`hl_rosette`), two stalks of pink stars), **edelweiss** `SM_VK_Plant_Edelweiss` (1,014 tris,
    0.31 m: silver felty leaves, white felty stars), **roseroot** `SM_VK_Plant_Roseroot` (1,758 tris, 0.52 m: stems clad
    in fleshy blue-green leaves, flat yellow heads), **arnica** `SM_VK_Plant_Arnica` (678 tris, 0.59 m: flat ribbed
    rosettes, ragged orange-yellow daisies turned outward). Two shared 1024 sheets instead of one 512 sheet each:
    `T_VK_HerbsCh2` / `T_VK_HerbsCh3` (`vk_leafgen.paint_herbs_ch2` / `_ch3`; each cell painted on its own 512 painter,
    cells across, top row first; the painter lives outside the kit namespace: exec `vk_tex` then `vk_leafgen` into one
    dict). `vk_nature.hb_cell` maps a cell-local region into the sheet; helpers `hb_strip`, `hb_cards`, `hb_ball`,
    `hb_head` (ya_head with its own region/slot and a facing), `hb_palm` (ct_leaf likewise). Slots 68 `HERBS_CH2`, 69
    `HERBS_CH3` (`herb_sheet_material`, two-sided); `kit_mats()` returns 70. Heads painted over a small backdrop disc
    only: a full-size dark disc showed as a rim round every head. Built, painted and saved from a background Blender
    (the live one held another session's scene); preview scene `Herbs_Ch23_Preview` in the .blend. Exported, Unity Build
    Materials + Build Prefabs (the eight only). Not placed in MedievalSetting (no gather spots or items yet).

135. 2026-10-20 (the user picked "the fresh piece catalogue" from my improvement list). `docs/PIECES.md` had been
    generated 2026-09-23 and patched by hand (it said 483 masters and 55 slots). Now generated from the package's
    `Data/pieces.json`: `tools/render_thumbs.py` (background Blender; one ortho thumbnail per piece from the
    front-left, transparent, to `renders/thumbs/`, 6 minutes for all) and `tools/pieces_catalogue.py` (plain `py` +
    Pillow: `PIECES.md` by kit and category with size, tris and material count; contact sheets
    `docs/catalogue/sheets/<kit>_<category>.jpg`, 8 across; `docs/catalogue/index.html` from the template
    `docs/catalogue/page.html` with search, kit and category filters, heaviest-first order and a detail panel with
    the prefab path). 1,405 pieces in 99 categories (building 464, nature 61, terrain 33, interior 847); the 37
    map-unique `U_*` meshes are counted, not listed. Kits are told apart by the FBX folder (VK, VKT, VKI) and the
    nature collection. Published as a private Artifact for browsing: https://claude.ai/artifact/BJojc6Wwk3Tua8hf9zzar4
    (republish `renders/catalogue_page.html`, the same page without a document skeleton, with the sheets as files).
    `INTERIOR_KIT.md` §6 (the interior's first 146 pieces, generated then) now points to PIECES.md.

136. 2026-10-20 (the user: "improving old props"). Close-ups of the props that looked weak in the catalogue's sheets:
    the clay pit, mortar tub, hoist beam, banker and the water props (trough, fountain) hold up close (their sheet
    thumbnails were too small); six were redone in their builders. `prop_garden_bed` (1,448 tris): a raised bed
    (`soil_bed` 2.8 x 1.6, three ridges) with a row each of cabbages, carrot tops and onions, the crop fields'
    helpers (was 18 flat green blobs). `coal_pile` (2,956): a low `ind_heap` core heaped with 110 `ind_chunks` lumps,
    more round its foot, a plank bin behind and a shovel stuck in (was loose faceted balls and a floating board).
    `prop_woodpile` (3,396): firewood billets (`con_log`: bark and end grain) stacked end-on in five settling rows on
    bearers under the old lean-to (was 7-sided cylinders, some in BREAD). `prop_crates` (2,288): PLANKS bodies, WOOD
    rims, corner battens and a diagonal brace per side; the second barrel moved (their hoops overlapped). `fro_staddle`:
    STONE_BLOCK instead of the noisy ROCK. `prop_signpost` (1,424): solid wedge points (the tips were single faces,
    invisible from behind), pale painted letter strokes, iron brackets, a pyramid cap and fieldstones at its foot.
    vk_zfight clean (the garden bed's only hits are its frame bottoms 35 cm underground, as on the crop beds).
    Saved, exported, prefabs rebuilt, catalogue regenerated and the page republished.

137. 2026-10-20 (the user: "any old prop that needs improvement"). Scanned the rest of the sheets (animals, piles, deco,
    signs, emblems, tents, graves, all interior props) and checked suspects close up: the coal and hide piles hold up;
    four interior props were redone (vki_rebuild, vki_test_pieces clean). `vki_adv_lootpile` (3,524 tris, hero budget
    6,000): 120 coins (6-sided `vki_adv_coin(segs=)`) half sunk over the gold mound at every tilt, 16 spilled round its
    foot and three short stacks (each one solid: coins laid flat on flat would z-fight); it read as a smooth yellow
    dome. `vki_cav_crystals` (262): eleven faceted six-sided prisms with six-faced points (`vki_cav_crystal`, flat
    shaded) instead of seven cones, small ones round the base. `vki_lair_cocoon` (996): a lathe body with a head,
    shoulders and hips under the silk, jittered, seven wraps at uneven tilts, strands to the wall and the floor, darker
    toward the floor (was a smooth spindle). `vki_adv_boulder` (420): noise-displaced, flat-faceted, darker in its
    hollows; still round enough to roll. The farm animals (`SM_VK_Animal_*`) are to move to the Beasts pack (the user,
    2026-10-20): make them there first, swap the game's placements (Hamlet 9, Saltmere_Farms 7, ShepherdDowns 2,
    Greywall 1, KitSeeThroughCaps), then take them out of the kit (vk_mod_humble's farmsteads, Hovel_Cruck/Hip).

138. 2026-10-21 (the user: "place those on the game and remove the placeholder animal props"). The six farm animals
    (`SM_VK_Animal_Cow/Sheep/Pig/Goat/Horse/Chickens`) are out of the kit: the game uses Beasts' rigged, animated ones
    (Beasts repo, farm_*.py; MedievalSetting `Assets/Game/Farm/Animal_*.prefab`, looping idle/graze/call/sleep in place).
    `vk_mod_humble`: the livestock section (`hum_leg`, `hum_hen`, six `hum_animal_*`) and their six WS_SPECS rows are
    gone; the hovel, longhouse, pigsty and sheepfold builders leave their pens and yards empty, each removed animal's
    `r.uniform` draw kept so the bushes and weeds stay where they were. In the open medievalDiorama.blend: text pushed,
    the 6 masters + 40 placed copies (VK_ValleyTown, VKX_Structures, VKX_Catalog_Exterior) deleted, NOT saved by me.
    Package (unversioned): the animal placements dropped from Data/Structures (Hovel_Cruck/Hip/LeanTo, Longhouse, Pigsty,
    Sheepfold), Data/Levels (VK_ValleyTown, Structures_Showcase, Catalog_KitExterior) and Data/pieces.json; the six
    structure prefabs and three level scenes in Generated had the nested instances stripped (exactly what Build
    Structures would give, without re-applying three weeks of builder changes to all 45); the fbx + piece prefabs
    moved out of the package. KitSolid's soft "Animal_Chickens" stays (the game's hen flock has that name). The game's
    layouts place the animals that stood in the pens (Tools~ `*_layout.py` + JSON, with "z" = the old floor height).
    Catalogue regenerated (1399 pieces). Stale: two baked caps in the game's KitSeeThroughCaps.asset
    (SM_VK_Animal_Horse/Cow...Cap), dropped at the next caps bake.
139. 2026-10-21 (the game's user: "baking a level should allow the inclusion of data that is currently said to be added
    by hand"). Two package features so a game's hand-made additions survive a rebuild (LEVEL_BUILDING 5.5 and 5.7):
    `KitVillage` reads a layout's `"links"` (ways in that are no building's door: a trigger box at a spot, `LNK_<id>`,
    its `spawn` as `SPN_<id>`; KitLink's own defaults where a key is left out) and a prop's `"colliders": false` (the
    piece's own colliders off, beside `collide`'s box); `KitChain.AfterBake` (a static `Func<KitChain, string>`) is
    called last by `KitChainEditor.Bake`, after the navmesh, its lines added to the report. MedievalSetting moved its
    hamlet's well and burrow into Tools~/hamlet_layout.py (a scratch rebuild reproduced the hand-placed spots exactly),
    Fen's marker into Hamlet_Inn.record.json's `markers`, and sets AfterBake for the HamletCellar chain
    (Editor/LevelBakeHooks.cs). Checked: offline compiles of MedievalKit.Runtime/.Editor, the game's editor assembly,
    scratch builds of Hamlet and Hamlet_Inn; not checked: a real re-bake of HamletCellar (its hook not run end to end).
140. 2026-10-23 (Daniel: "Do these tasks you mentioned" -- the card game's catapult as an animated unit for the RPG: the
    kit's onager with a rigged throwing arm and wheels and a load-and-throw clip; "don't bother with adding them to the
    game, build the creatures"). **The first animated unit, `VKU_SiegeCatapult`** (docs/UNITS.md has the rig, the clips
    and the commands). Built headless (`tools/unit_catapult_run.py`), in its own `blender/vku_siege_catapult.blend`;
    the kit's .blend opened, never saved.
    - **Parts from the builder, not a copy:** `vki_orc_catapult` now calls `vki_orc_part(k, name)` after each part
      (frame, wheelFL/FR/BL/BR, arm, stone, lash, windlass, stack). On a plain VKIKit it does nothing: the static
      `SM_VKI_Prop_Siege_Catapult` and `_Burnt` hash the same built from HEAD's text and from the new one (stage 1
      checks it every run). `src/units/vku_siege_catapult.py` builds with a kit whose tag writes an int layer made
      before any geometry (no BMVert reference is invalidated), drops the lash and the ground stack, adds a windlass
      rope, cuts the arm at 62 % (both cut faces closed), weights each part 1.0 to its bone. 2,028 tris, the kit's five
      materials + vertex colours; projectile `SM_VKU_CatapultStone` (20 tris).
    - **Fitted to the geometry, not guessed:** the arm's stop angle (92.98 deg from the bind pose) and the loaded angle
      (7.35 deg: the static's arm lies through the windlass drum and the back cross beam) by bisection on triangle
      overlaps (BVH), the rope's hook over the drum, Throw's release frame (7: launch elevation 47.6 deg), Destroyed's
      tilt (9.0 deg about the front-right / back-left contact line until the front-left corner is down) and the
      snapped tip's flight lifted over the pad and crossbar where it would pass through them.
    - Clips: Idle, IdleLoaded, Move (1.0014 m/s, the wheels one turn a loop), Load (5 s), Throw (Release 0.233 s), Hit,
      Destroyed; events Hooked/Loaded, Release/Slam, Break/Snap. Burnt look: a material swap (`M_VKU_WoodCharred`).
    - **Unity:** built first in `Units~` folders Unity skips (the package is live in MedievalSetting through its `file:`
      reference); installed the same day by renaming the three to `Units` (`Editor/Units/KitSiegeCatapultSetup.cs`,
      `Runtime/Units/KitUnitEvents.cs`, `Art/Units/SiegeCatapult/`), then Tools > Medieval Kit > Units > Build Siege
      Catapult: report `OK` (13 bones, 2028 tris, 7 clips and states, Release at 47.6 deg); the first run threw on the
      stone's collider read after its object was destroyed (fixed: radius read first). Its own folder (`Art/Units`,
      not `Art/Models`) keeps `KitImport`'s static-piece import settings (animation off, axis conversion off) away
      from the rig.
    - Checked: lowest vertex per clip (>= -0.3 mm), Move traced (skeleton in place, slip 1e-5 m/s), no part through
      another in any frame (triangle overlaps), the FBX read back (13 bones, Motion unparented, Move -2.1363 m, the Stone
      scale step at frame 7), renders at full res (`renders/units/siege_catapult/`: views, close-ups, rope, frame
      strips of every clip, the wheels on a 0.5 m checker, the 22 m / 14 m game camera), offline compile of
      MedievalKit.Runtime + .Editor with the two scripts against MedievalSetting's assemblies (0 errors, output in a
      temp folder). Not done: game wiring.
    - Gotchas: `Mesh.materials.clear()` after `to_mesh` reset the stone's faces to slot 0 (wood) -- fill the slots
      first (§6 says so; it bit again); Blender 4's vertex-group names live on the mesh, so clearing the object's groups
      after writing the deform layer dropped every weight; the rope's rest is the loose 0.35 m hang (a 1 m rest made the
      bind pose a rope to the ground); FBX clip files carry the current frame as the bones' default, so each clip is
      exported from its frame 0; Blender's FBX importer reads a scaled bone's default as rest (the re-imported Stone
      read 1000x until the frame-0 fix).
    - Open: no IdleLoaded -> Hit or Move-while-loaded clips (the controller only hits from Idle / Move); the windlass
      spins fast while the rope is run out to the arm (~3.5 turns a second for 0.9 s); the stone pops in above the cup (scale 0 -> 1
      over 3 frames while it drops 0.35 m) [both done in 141]; no turn-in-place (a game turns the transform; the
      wheels don't counter-roll).
141. 2026-10-23 (Daniel, on the list of the catapult's rough edges: "Do the number 4" -- the Load clip's two: the
    windlass spinning while the rope is run out, the stone popping in over the cup). `src/units/vku_siege_catapult.py`,
    rebuilt headless (stage 1 + 2; the static `SM_VKI_Prop_Siege_Catapult` / `_Burnt` hash unchanged).
    - **The windlass:** the run-out is 3.34 turns of the drum (2.1 m of rope on r 0.1). It took 28 frames from a
      standing start at 7.0 turns a second (84 deg a frame: past the 45 at which the four-spoke cross strobes; mean
      3.6). Now `load_rope` swings the rope's end up over the drum (12 frames) while `ease_run` pays it out over 56
      frames: 0 -> 2.51 -> 0 turns a second (half-cosine ramps of 16 frames; mean 1.8; nowhere in the clip more than
      35 deg a frame). The windlass still turns with the rope's length. To fit, the eight heaves start 22 frames later
      (59..128) and pause less between pulls (0.7 frames, was 2.75): their peaks 2.79 -> 2.92 turns a second, mean
      1.27 -> 1.61. **Hooked 1.2 -> 1.9 s**; Loaded 4.633 s and the 5 s length kept. The setup reads events from
      `siegecatapult_clips.json`: no C# change. A truly hand-paced windlass (~1 turn a second) needs Load at 6+ s (the
      drum turns 7.1 times in all); not done, the game's reload time stays. Chart:
      `renders/units/siege_catapult/windlass_speed_before_after.png`.
    - **The stone:** a basket of stones on the rear cross beam's +X end, beside the windlass's spokes (`_basket`, part
      `basket` on the Frame bone, no new bone): a 12-sided burlap lathe closed on top by a stone-faced heap, three stones
      on the heap; 204 triangles (unit 2,028 -> 2,232), the kit's M_VK_Burlap / M_VKI_StoneBlockIn. In Load the hidden
      stone (0.001) moves from the cup into the basket at frame 98, holds 2 frames (so Unity's curve tangents settle
      before it grows), grows to full size inside the basket's closed body (100-104), is lifted straight up out of the
      heap (106-118) and swung over in an arc and set down in the cup (`stone_path`: by length, smoothstep in time;
      straight down into the cup at the end), seated at 139 = Loaded, then the old 3 cm settle. `Pose.stone_at`
      (scale, centre, turn) places the Stone bone off the arm; it turns from `STONE_TURN` to the cup's turn on the way.
      Nothing else changes: every other clip keeps the hidden stone at the cup.
    - **Export override:** the package's `Art/Units/SiegeCatapult` is live in the open editor, so the export went to
      `renders/units/siege_catapult_export/SiegeCatapult/` (`export_dir=<folder>` on the driver, or env
      `VKU_EXPORT_DIR`, or `set_export_dir`; `export` and `reimport` both use it). Copied in by hand afterwards.
    - Checked: lowest vertex per clip (unchanged: Idle/IdleLoaded/Load +8.5, Move 0.0, Throw +3.2, Hit -0.3, Destroyed
      0.0 mm); Move trace (1.0014 m/s, slip 1e-5, skeleton still); the socket at Release (47.6 deg); overlaps in every
      frame of every clip: none, apart from the stone rising through the heap's stones (111-117, by design) and the last
      frame before it is seated (138: the same 5-triangle contact the seated stone has with its cup in IdleLoaded, the
      static's own fit); new `check_load`: the payout / heave speeds above from the keys, the stone inside the basket's
      closed body in every frame it is not full size (vertex rays leave through the basket's own faces: none fail), the
      spokes through a whole turn against the basket (no hit, closest 44.9 mm); `reimport` (13 bones, 2,232 tris, UVs,
      `Col`, Move -2.1363 m, Throw's Stone step at frame 7, Load's windlass at most 35 deg a frame, the stone's keys
      read from a scratch Load whose default pose is frame 106). Renders at full res (`renders/units/siege_catapult/`):
      `strip_load.png` (before: `before_load_fix/strip_load.png`), `strip_windlass.png` (four running frames back to
      back), `strip_stone.png`, `stone_path_rear.png` / `_side.png` (the way as copies), `game_22m_load.png`,
      `game_22m_stonepath.png`, plus every earlier render re-made with the basket.
    - Gotcha: Blender's FBX importer takes a scaled bone's default as rest, so any clip whose frame 0 has the Stone at
      0.001 (Load, like Idle) reads back 1000x in Blender; Unity plays the keys. Read such keys from a scratch export
      with another default frame (`check_reimport` does).
    - Unity (the same evening): the staged export copied over `Art/Units/SiegeCatapult`, Build Siege Catapult: report
      `OK` (2,232 tris, Load Hooked@1.900s / Loaded@4.633s, Release at 47.6 deg); Load sampled in a preview scene: the
      stone (scale 0.001 -> 1 inside the basket at 3.33-3.47 s, a -0.005 / 1.006 curve overshoot, invisible there)
      rises from y 0.97 to 1.61 m, arcs over and sits in the cup at 4.633 s; the windlass at most 35 deg a frame.
    - Open: no crew, so the stone is lifted by no one (the basket only hides where it comes from); the charred prefab keeps the
      basket burlap-fresh (as it keeps the stop's pad); the basket overhangs the cross beam's end by ~10 cm; the static
      piece has no basket (unit only).
142. 2026-10-24 (Daniel, in the game: the scorched earth maps "read as badly made, not destroyed scenery"; Daniel picked
    "the ground and materials" step of three). Unity side only, no Blender. Two layout keys in `KitVillage.Patches.cs`
    (LEVEL_BUILDING 5.7): `patches` paints the control map's sand (B) / cobble (G) layers after the nature stands --
    ragged rings under a share of named pieces, or noise patches by scale and cover (the cover's noise level found by
    sampling the map, so `cover` is a real share) -- and `pieceSwaps` swaps materials on named nature pieces only (a
    palisade's or a prop's wood untouched). The grass thins on B too (no map painted B before: unchanged elsewhere), and
    `grass.tip` tints the blades' tips. Own random stream: a map rebuilt with the keys keeps every marker, prop and piece
    where it was (BurntMarch and OrcHold diffed before/after: identical). The game's BurntMarch_Textures carry the burnt
    look (`Tools~/burnt_textures.py`). Learned: a ground slot's 4 m tile must hold nothing over ~0.3 m (the old burnt
    grass's 1 m blots tiled into a grid over the map); the AgX grade stretches light greys (ash over ~90 sRGB renders as
    snow); noise drifts of pale ash read as puddles, rings round trunks read as ash. Before/after from play mode in the
    game's session notes. Not done (the next steps offered): dressing (fallen trunks, clumped forest, smoulders, the ash
    overlay's slab look, the Northfields' edge) and better burnt tree meshes (Prop_BurntTree_A/B are ~450-tri poles).
143. 2026-10-24 (Daniel: "Pilot: bring the MedievalVillageKit into Godot 4.7.2, going Blender -> glTF -> Godot (not
    through Unity)"). **Godot export pilot**, all in [docs/GODOT_EXPORT.md](docs/GODOT_EXPORT.md). New exporter
    `src/export/gdx_export.py` beside vkx (execs it for its readers; the Unity export untouched), Godot files in
    `godot/kit/` (since entry 145 the addon `godot/addons/medieval_kit/`: KitLit.gdshader for moss / rim / roof
    jitter, import script, layout builder, capture, checks),
    `tools/gdx_round.sh` / `gdx_compare.py` / `gdx_crop.py`. One .glb per piece + a shared .tres library mapped by
    name at import; restyles = surface_material_override. Pilot family: the interior Overlay (52) + restyles, KitLit
    and glass checks, scene `GDX_Pilot` built in a background Blender (nothing saved): 58 pieces, 51 materials, all 19
    cameras 0.5-1.6 / 255 mean from Blender (shadows on and off), checked in full-res crops. Settled: vertex colour
    as albedo comes from our .tres (the importer sets it on 2 of 3 surfaces by itself); glass needs no node split (a
    transparent-pass material never casts shadows). Calibrated: AgX MHC = Godot contrast 1.5, flat sky for
    reflections, emission operator Multiply, sun shadows orthogonal 60 m / 8192 / angle x 0.6. Verdict on all 200
    materials: 160 clean, 13 transparent pass, 13 cut-out / translucent cards (8 leaf normals unported, as in Unity),
    10 KitLit, 6 projected (KitTerrain port). **Unity bug found, not fixed:** `M_VK_Stained`, `M_VKI_Stained_In`,
    `M_VKI_Stained_Night`, `M_VKI_Leaded_In` lose their glow in Unity (emission map x `emission: [0,0,0]`). Plan for
    the rest (the full kit, weapons + items, creatures, humanoids, layouts, terrain): GODOT_EXPORT section 7.
    Gotcha: Blender's glTF export crashes on this file unless `use_active_scene=True` (it visits every scene).
144. 2026-10-24 (Daniel: "Go ahead with step B, the dressing: fallen charred trunks, a clumped forest with clearings, a
    few smouldering stumps, replace the Overlay_Ash slabs, and the green-to-burnt edge in the Northfields"). Kit:
    `KitVillage.ForestDress.cs` -- forest `clumps` (glades by noise, the gaps' share found by sampling the spots), `lean`,
    `fallen` (beyond the wall only, the first of four ways with no cliff and < 1.5 m of drop over the trunk; roots up,
    lifted 0.22 m; the trunk's capsule turns with it), `zones` (per-region species / undergrowth / scatter and swap,
    mixed over the rim; `PieceSwaps` also swaps all nature in a zone's core: lip plants and boulders; not over the rim,
    where green crowns went black); `patches` got `spots` and `centre` ovals with `band`; areas take `surface: sand`.
    All of it draws from its own stream (Rz) and a glade's spot still draws its tree's piece and turn, so maps without
    the keys build as before; the three game maps rebuilt with every marker, prop and encounter where it was (only the
    slabs gone and the new stumps / smoulder markers added). Game side (MedievalSetting): `FireFx.Smoulder` + a
    LevelDirector "smoulder" marker role; a Northfields ground material (the kit's with burnt ground in sand, ash in
    cobble). Learned: solid pale ash (spots at 0.9, an ash farmyard) reads as a pond: keep it near the 0.5 threshold so
    it breaks up; the dirt layer draws over sand, so a fringe in dirt sits between black and green; a zone's swap over
    its rim blackened green pine crowns. Not done: Blender (better burnt trees and fallen trunks).
145. 2026-10-24 (Daniel, after the pilot (143): "a full port, even the shaders" -- the Godot kit gets everything the Unity
    kit has, and the Unity kit is completed by moving into it what the game already has: "transposing code that already
    exists in the game into the kit"; his picks: C#, generic outdoor-map generators). **The plan:**
    [docs/FULL_PORT_PLAN.md](docs/FULL_PORT_PLAN.md) (decisions, what the Unity kit has to port, the game code to move
    in from a read-only survey of MedievalSetting, the outdoor maps' scripts, phases 0-7 with a check each). **Phase 0
    done:** Godot 4.7.2 .NET build (`C:\Users\danie\Downloads\Godot_v4.7.2-stable_mono_win64\`, SHA-512 checked), .NET
    SDK 10; the Godot files became the addon `godot/addons/medieval_kit/` (Shaders, Editor, Runtime, plugin), linked into
    the project as a directory junction (`gdx_link_addon`); `MedievalKit.csproj` (net10.0, the editor's own NuGet
    packages: nothing downloaded); the pilot's GDScript tools are C# (`KitImport`, `KitBuilder`, `KitCapture`, entry
    `kit_cli.gd`); `tools/gdx_round.sh` builds the C# first. Check: the whole pilot round gives the GDScript run's
    numbers exactly (58 pieces 0 problems, 19 cameras 0.5-1.6 / 255). Next: phase 1 (all pieces, every material on
    KitLit) and, beside it, phase 3a (the game's ready-to-move code into the Unity kit).

146. 2026-10-24 (Daniel, on the burnt maps after 144: "Before we check them in, keep improving"). Kit pieces
    (`vki_props_orc`, built in a background Blender: the live one had another project open): `Prop_BurntTree_C` (a 4 m
    snag, a split shard), `_D` (6 m, dead limbs with twigs), `_E` (a 2 m burned-out snag), `Prop_BurntLog` (a fallen
    trunk along X, root plate at -X), `Overlay_BurntBranches`; `_A`, `_B` and `Prop_BurntStump` rebuilt on the same
    buried foot (`vki_orc_foot`: a flare that narrows inside the trunk and short roots sinking under the ground; their
    five / four-root stars repeated into clip art from the game camera) and charred to the ends (pale end-grain rings
    and COAL lumps rendered as light "stars"; `vki_orc_crater` is darkened bark). 356-672 tris each; vki_test_pieces {};
    exported (8 pieces; materials unchanged), Unity Build Prefabs (8 / 0 failed), catalogue thumbs + PIECES.md.
    Viewer scene `Burnt_Preview` in the .blend (old and new in a row). Fixed: the hall's stump-leg helper was also
    named `vki_orc_stump` and shadowed the burnt stump's builder (any rebuild of Prop_BurntStump failed): now
    `vki_orc_leg`, no geometry change. The .blend's `vki_props_orc` text is one header comment behind src (push before
    the next rebuild). Package: forest `fallen.as` (the trunk laid down as that piece, both ends beyond the wall),
    patches `onRoads`, the build loads forest zones' and `fallen.as` pieces (`KitVillageTools.Names`). Game: the three
    burnt maps use them (logs only via `fallen`: a 6 m log in the walkable undergrowth cut off a gather marker),
    charred-log / branch / rock debris in the clearings, scorch round the camps' fires, tents and engines (`onRoads`),
    darker ash and cliffs; rebuilt with markers and encounters unchanged (one archer point moved 1.2 m off a log).
    Tried and dropped: noise scorch over the yards (cow print). Disk: E: had 1.2 GB free (the .blend save needs ~710 MB
    of temp space).
147. 2026-10-24 (Daniel: "Commit and push the Godot work so far ... then start phase 1"; FULL_PORT_PLAN phase 1, the
    whole kit in Godot; details in docs/GODOT_EXPORT.md 3 and 5b). **Every material on KitLit** (variants for clip /
    hash / blend / glass, the leaves' height-map bump) -- identical to the pilot's StandardMaterial3Ds (mean 0.000) --
    and **KitTerrain** ported (terrain, stair, paving, curb, water, `kit_noise`). Whole kit exported (`-- all`: 1,396
    pieces, 200 materials, 4 m 18 s), imported (6 m 40 s), every piece checked. Catalogs (`-- catalog Exterior|Interior`)
    and the valley's ground (`-- terrain`) against Blender: interior all under 2.5 / 255, exterior 48 of 52 (the four
    others trees and bushes, below), valley ground 2.5-3.4 (water noise 5-10). **Godot's image v runs from the top**:
    textures sampled at Blender coordinates turn v (tile tops had come out rock); perspective cameras lock the height.
    **Trees:** EEVEE darkens the leaves (their Translucent BSDF normal scaled by -1; one oak rendered a node change at a
    time); Daniel picked C, Godot's backlight as in Unity ("B and C look the same ... proper industry standard; the A
    look isn't very good"). Materials missing from Unity's materials.json are analysed with vkx's own code into the
    project's `kit/.vkx` cache. KitSea / KitGrass / KitWaterMask moved to phase 5 (only KitVillage builds them).
    Disk: E: down to 1.2 GB again; the comparison sheets (~460 MB, rebuilt by every round) removed -> 1.7 GB.
148. 2026-10-24 (Daniel: "ok, we have enough space to work now, can we resume?", then "Can you build me a test scene
    to see how it looks in godot? I know nothing about godot"; FULL_PORT_PLAN phase 2, details in GODOT_EXPORT 4 and
    5c). **The levels in Godot:** runtime C# in the addon (KitPiece / Link / Spawn / Marker / Level / World / Travel +
    its host, KitDecks, KitNavMesh = a NavigationRegion3D, KitEncounter, KitPortalMarker, KitStructure); the importer
    makes every piece a KitPiece with its colliders (doors that open and breakables on a second layer); KitBuilder
    builds the 20 world-graph levels with bridge decks, a navmesh each and a walk test (all 20: every spawn and link
    reachable), and the 45 structures (exporter `-- structures`). Travel test (`kit_cli travel`): 40 links taken,
    Godot's own paths reach every spawn and link, preload cuts instant. Captures against Blender: interiors and
    dungeons 1.9-5.7 / 255, valley 5.6-7.8 (one camera 16.5: an oak crown, look C, and the river's noise stand-in).
    **Lights measured in Godot** (`tools/godot_probes/`): point / spot P / (4 pi^2) holds; Godot 4.7 reads
    `spot_angle_attenuation` inverted (the first build's 8.9 dimmed every window shaft to 45 %; now ln(1 - blend/2) /
    ln 0.5); Godot 4.7 has AreaLight3D: Blender's area lights (the doorway aprons) are area lights of P / pi^2 (Unity
    makes them points). The roof jitter's instance uniform moved to a KitLitJitter variant (instance uniforms cost
    every instance a slot of a 4096-instance buffer: the valley ran out). **The demo:** the Godot project's main
    scene (`Walker/kit_demo.tscn`): a menu of the built levels, the test walker (E at doors and stairs), Blender's
    cameras (Tab), a free camera (F), Esc back; `Play Medieval Kit demo.bat` / `Open in Godot editor.bat` in the
    project folder; Project > Tools > "Play From Start Level" / "Walk This Level" too. Chains and their streamer wait
    for phase 4 (they need the generators). Committed with phase 1 (147) in one commit.

## 6. Gotchas
- `vki_ws_build` refuses a piece whose master already sits in VKI_Pieces ("not yours"): build it there with
  `vki_rebuild` and show it in a workshop scene as an object sharing the master's mesh.
- Unity RunCommand cannot see the package's editor assembly (`MedievalKit.Editor` is not auto-referenced): call
  `KitBuilder` / `KitVillageTools` through `System.Type.GetType("MedievalKit.Editor.KitBuilder, MedievalKit.Editor")`.

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
