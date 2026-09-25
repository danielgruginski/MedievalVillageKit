# HANDOFF — Medieval Village Kit (state at the end of 2026-09-24)

Read this first when continuing the work (new session: *"Read MedievalVillageKit/HANDOFF.md and continue"*).
Project root: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit` (git repo, branch `main`).
Overview and folder map: [README.md](README.md). Kit reference: [docs/KIT_README.md](docs/KIT_README.md).

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
- Paths in code: `VK_ROOT` in `vk_tex` (textures → `assets/textures`, then packed), `vk_render` (renders →
  `renders/wip`) and `ws_common` (→ `renders/modules`). If the project folder moves, change these three lines.
- All kit textures are packed in the .blend; their file paths point to `assets/textures/`.

Common commands: [docs/KIT_README.md §3](docs/KIT_README.md). Quick checks after terrain changes:
`tk_test_T1()` → `[]`; `tk_test_T3(30)` / `tk_test_T3r(30)` → no failures (≈26k / 16k checks);
`tk_test_T4(G, chunks, step=0.25)`: the demo gives 5 known hits, the valley 17. They are grazing rays on near-vertical
relief and talus faces (face normal z between −0.19 and 0), plus the same small downward face on the ramps (open
issue 13: five in the valley, one in the demo).
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
13. Ramp tops have a small face pointing down, coincident with the ramp surface. `tk_test_T4` flags it at five valley
    ramps and one demo ramp. It is probably in `ramp_blend_shoulder`.

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
- `vk_tex` creates `TEXDIR` when executed; generated textures are saved there *and* packed.
- The valley generator deletes and rebuilds `VK_ValleyTown` / `VK_ValleyTerrain` completely: never hand-edit them;
  change the code instead.
- **Never publish the .blend as-is:** its `SpriteRig` scene holds third-party character assets. The repo is public;
  keep the .blend, renders and anything from that scene out of git.
- Blender cannot create folders under the long scratchpad path (Windows `MAX_PATH`); render into `renders/` instead.
- README gallery: `tools/render_showcase.py` → `render_showcase()` re-renders `docs/images/*.jpg` (cameras in
  `SHOWCASE`); rebuild the valley and the demo first.

## 7. History (where the details are)

- `archive/script_logs/` — every script run in Blender during the build (main session + all agents), chronological,
  with results. Start at its `INDEX.md`.
- `reviews/` — the two valley reviews (33 confirmed issues, then the re-review) and the module-build agent reports.
- `docs/history/` — design briefs, specs and design-panel outputs from the expansion phase.
- `renders/` — every render made, by topic; `renders/final/` has the latest verification shots.
