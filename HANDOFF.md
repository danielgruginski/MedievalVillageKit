# HANDOFF — Medieval Village Kit (state at the end of 2026-09-29)

Read this first when continuing the work (new session: *"Read MedievalVillageKit/HANDOFF.md and continue"*).
Project root: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit` (git repo, branch `main`).
Overview and folder map: [README.md](README.md). Kit reference: [docs/KIT_README.md](docs/KIT_README.md).
Interior kit (built 2026-09-25/26): [docs/INTERIOR_KIT.md](docs/INTERIOR_KIT.md).
Dungeon kit (built 2026-09-29 on the interior kit): [docs/DUNGEON_KIT.md](docs/DUNGEON_KIT.md).
Adventure kit (built 2026-09-29 on the dungeon kit): [docs/ADVENTURE_KIT.md](docs/ADVENTURE_KIT.md).
The town connection, the world graph (2026-09-30): [docs/WORLD_GRAPH.md](docs/WORLD_GRAPH.md).
Unity export (vertical slice, 2026-09-30): [docs/UNITY_EXPORT.md](docs/UNITY_EXPORT.md).

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
