# Medieval Village Kit: how the .blend is organised

File: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\blender\medievalDiorama.blend`. The main scene is **VillageKit**.
(Until 2026-09-23 the working copy lived at `E:\Unity\Projects\Cube Sorter\Art\WallKit\medievalDiorama.blend`.)

All geometry, textures and materials are generated procedurally by the Python texts stored inside the .blend: Text Editor → `vk_*`.
Every piece can be rebuilt from code at any time. The same texts are kept as files in the project's `src/` folder;
`tools/kit_sync.py` pushes files into the .blend and pulls texts back out (see §3).

## 1. Collections in VillageKit

| Collection | Contents |
|---|---|
| `VK_Pieces` | All piece masters `SM_VK_*` (hidden): core pieces, 8 expansion modules, landmark pieces (smithy, inn), stall variants. Instances share their meshes. |
| `VK_NaturePieces` | 39 trees, bushes, rocks, plants and mushrooms (hidden masters), rebuilt from `NATURE_SPECS`. |
| `VK_TerrainTiles` | Marching-squares tile masters `SM_VKT_*` (hidden), incl. the ramp/cliff transition half tiles and `SM_VKT_RampShoulder`. |
| `VK_ValleyTerrain` + `VK_ValleyTown` | The big showcase map: 72×56 cells at world (1500, 0). Terrain chunks, water, `VKV_Paving` + all placed pieces. |
| `VK_Terrain` + `VK_TerrainVillage` | The small terrain demo: 32×24 cells at world (1200, 0), with `VKT_Paving`. |
| `VK_TerrainBoard` | A catalogue of every terrain tile. |
| `VK_Town`, `VK_Glade`, `VK_Catalog`, … | Earlier showcases on flat ground. |

Other scenes: `MedievalColony` (first colony diorama, `mc_helpers`), `StoneWallKit` (`wk_helpers`), `TreeAsset` (hero oak with LODs + impostor, `tree_build`), `SpriteRig`, `Scene`.

## 2. Code texts (file in `src/` → role)

| Text | File | Role |
|---|---|---|
| `vk_kit` | `src/core/` | **Loader**: `exec(bpy.data.texts["vk_kit"].as_string()); g=vk_kit_ns()` gives one namespace with helpers + modules + nature + terrain. |
| `vk_helpers` | `src/core/` | Core kit: the `Kit` bmesh builder, 52 material slots, core pieces, `full_rebuild()`, `place_v()`, variant styles, market stalls (`STALL_TRADES`), landmarks (`build_smithy`, `build_inn`), lit windows. |
| `vk_mat` | `src/core/` | PBR material builder, `MAT_MAP`, `apply_pbr_all()`, `TONE_MAP`. Executed by `vk_helpers`. |
| `vk_render` | `src/core/` | `shot(name, cam_loc, target, lens, res, ...)` render helper (default output `renders/wip/`). |
| `vk_tex`, `vk_texgen`, `vk_tex2` | `src/textures/` | Procedural PBR texture generators (`_BC/_N/_H/_R/_AO`), written to `assets/textures/` and packed. `vk_tex2`: stone rework, wattle, net, slate/shingle roofs, terrain textures. |
| `vk_leafgen` | `src/textures/` | Leaf/flower atlas `T_VK_Leaves_*` (one cell per plant), `repaint_leaf_cell(cell)`. |
| `vk_mod_humble` … `vk_mod_defence` | `src/modules/` | 8 expansion modules: pieces (`WS_SPECS` → `EXTRA_SPECS`) and builders `build_*`. |
| `vk_nature` | `src/nature/` | Nature kit (trees, bushes, rocks…), `NATURE_SPECS` + `rebuild_nature()` + `check_nature_specs()`. |
| `vk_terrain` | `src/terrain/` | Marching-squares terrain kit: tiles, ramps/stairs (with cliff transition), chunk assembler, displacement, materials, paving/curbs, ramp dressing, tests. |
| `vk_terrain_demo`, `vk_town_map` | `src/terrain/`, `src/maps/` | The two terrain showcase maps. |
| `ws_common` | `src/workshop/` | Helper for isolated "workshop" scenes, used to develop new modules with agents. |
| `mc_helpers`, `wk_helpers`, `tree_build`, `tree_skeleton` | `src/early_scenes/` | The first scenes (colony diorama, stone wall kit, hero tree). `tree_skeleton` is JSON data. |
| `README_VillageKit` | `docs/KIT_README.md` | This file. |

## 3. Common tasks

```python
# keep src/ and the .blend in step (run inside Blender)
exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\kit_sync.py",encoding="utf8").read())
status(); push("vk_terrain"); pull("vk_town_map")

exec(bpy.data.texts["vk_kit"].as_string()); g=vk_kit_ns()
g["full_rebuild"]()                               # rebuild every SM_VK_* piece in place (instances update)
g["full_rebuild"](names={"SM_VK_Wall_Wattle"})    # just some pieces
g["apply_pbr_all"]()                              # rebuild the PBR materials from MAT_MAP
g["rebuild_nature"]({"SM_VK_Tree_Oak_A"})         # nature masters from NATURE_SPECS (all when no names)
g["tk_build_ramps"](); g["tk_build_stairs"]()     # terrain ramp/stair tiles
exec(bpy.data.texts["vk_town_map"].as_string(),g); g["build_valley_town"]()   # rebuild the big map (60-90 s)
g["build_terrain_demo"]()                         # rebuild the small terrain demo
g["tk_test_T1"](); g["tk_test_T3"](40); g["tk_test_T3r"](40)   # terrain seam tests (expect 0 failures)
exec(bpy.data.texts["vk_render"].as_string()); shot("name",(x,y,z),(tx,ty,tz),lens=35)   # render to renders/wip
```

To place a building on terrain, call its builder with `origin=(x, y, rot_z_radians)`, then raise the new objects by `level*1.5`. `TownPlacer.build()` in `vk_town_map` does this for you and checks the footprint.

The valley generator (`build_valley_town`) runs these checks and clean-up passes:
- **Clash test:** every placed object's box goes into a 3 m spatial hash. A new building is tested object by object, including height. Infill houses that hit a wall, tower, gatehouse or another building are undone.
- **Occupancy:** walls, towers, gatehouse, bridges and quay are marked occupied. Trees keep one free cell from any building; big broadleaf trees keep two. Trees are at least 1.5 m apart (2.5 m for the same model). Willows are at least 12 m apart and stay off roads, ramps, bridges and the quay. No trees on the map border or on ramp/stair tops.
- **`town_door_clear`:** slides props, bushes and rocks out of the corridor in front of every `*_Door` module (1.3 m wide, porch width when there is a porch) to a spot that clashes with nothing, else drops them. Removes weed strips from door steps.
- **`town_fix_levels`:** moves a prop that straddles a cliff, stands on a ramp or over water by up to 2 m, or deletes it if no nearby spot fits.
- **`town_wear`:** worn ground in front of doors and around busy yards (`TGrid.wear`, the R channel of the ground-control map).
- **Paving:** cobbled cells become a separate mesh (`tk_build_paving`): stones 6 cm above the terrain, dressed-stone curbs towards grass, patches of missing stones showing dirt. Props on cobbles are lifted onto it.
- **Ramps:** the half-ramp tile blends the cliff down into the ramp surface and turns the side into an earth bank; `tk_ramp_dress` adds a stone, grass and a fern at each ramp end. Stairs still get `SM_VKT_RampShoulder` rocks.
- **Cliffs:**
  - `make_displace` gives the cliff faces chunky rock relief. The displacement depends only on world position, so the duplicated vertices of neighbouring tiles move together and no seam opens.
  - Where a tier top is the middle ledge of a taller cliff, the relief runs through the ledge, and the upper layer drops its skirt (`tk_cache_noskirt`).
  - The turf lip of cliff tops sags in patches.
  - `apply()` bakes rock instead of turf on the middle ledges and in eroded patches along the lips.
  - `tk_cliff_dress` sinks boulders into the faces and puts rubble, plants and grass tufts at the toes, the lips and the middle ledges.
  - The rock texture comes from `gen_cliff_v2` in `vk_tex2`: angular blocks, strata and a soil strip under each lip.
  - The terrain material blends two cliff samples at different scales, so long cliffs don't repeat.
- **Kitchen gardens, roof palette:** crop beds next to houses; roofs chosen per district (Blue for landmarks), ±6 % per-instance brightness jitter.

Landmarks: `build_smithy` (9 m forge stack with glowing hearth, open workshop, point light) and `build_inn` (3 storeys, lit windows, big tankard sign, beer garden). Market stalls: `SM_VK_MarketStall` + `_Greengrocer/_Baker/_Fishmonger/_Potter/_Draper/_Cheese/_Tinker`.

Lighting: `VK_Sun` is the key light (from the south-west). `VK_Fill` is a shadowless fill light (from the north-east, 1.5) so faces on the shadow side stay readable. These lights are only for Blender renders.

## 4. Conventions

- **Grid:** 3 m cells.
- **Wall modules:** 3 m wide, outer face toward −Y, centred on the cell edge. Corners sit at the origin and face −X/−Y.
- **Heights:** ground storey 3.0, upper storeys 2.8, wattle walls 2.4, sheds 2.6. Roofs are placed at the wall top.
- **Materials:** 52 kit slots.
  - Added 2026-09-23: `STONE_BLOCK` (dressed stone), `FIELDSTONE`, `WATTLE`, `HIDE`, `PIGSKIN`, `COAL`, `NET`.
  - Recolour styles per instance, via the `style` dict of `place_v`:
    - plaster: Cream, White, Ochre, Rose, Daub, Sage, Sky
    - shutter: Teal, Red, Green, Blue, Natural, and the chipped `TealWorn/RedWorn/GreenWorn/BlueWorn` (≈1 in 5 random houses)
    - roof: Red, Blue, Green, Thatch, Slate, Shingle
    - cloth: Red, Blue, Green, Yellow, Purple, White
    - stone: Rubble, Field, Warm, Cool, Dark
    - window: Lit (warm glow from inside)
- **Terrain:** dual-grid marching squares. Levels are 1.5 m. Water is at −0.6 and the river bed at −1.5 below the cell level.
  - Tiles: Cliff (Full, Edge A/B/C, Outer A/B/Sq, Inner A/B/Sq, Saddle), Shore (Edge A/B, Outer, Inner, Saddle, Bed), Ramp and Stair (HalfE, HalfW, Mid), and WaterQuad.
  - Tile sides are quantised to 1/1024 m, so neighbours match bit for bit.
  - Terrain vertex colour `TCol` holds: R = AO, G = rock mask, B = rim, A = wet/sand.
  - The ground type per cell comes from `T_VK_GroundCtl*`: R dirt, G cobble, B sand, A rock (with `paved=True` cobble cells are painted as dirt under the paving mesh).

## 5. Expansion modules (builders)

| Module | Builders |
|---|---|
| humble | `build_hovel(variant cruck/hip/leanto)`, `build_longhouse`, `build_pigsty`, `build_sheepfold`, `hum_block` |
| frontier | `build_logcabin(n)`, `build_woodcutter`, `build_forester_hut`, `build_granary`, `build_storehouse`, `fro_roof_family("S")` |
| construction | `build_construction_site(stage 0..3)`, `build_camp`, `build_stockpile(w,d)`, `build_sawpit_yard` |
| skyline | `build_skyline_street`, `sky_unit` |
| town | `build_merchant_house`, `build_townhouse_gablefront`, `build_corner_house`, `build_terrace(units)` |
| water | `build_watermill`, `build_fisher_hut`, `build_smokehouse`, `build_lavoir`, `build_riverside_demo` |
| industry | `build_mine`, `build_quarry_yard`, `build_charcoal_burner`, `build_pottery`, `build_tannery`, `build_dyers_yard`, `build_brewery`, `build_apiary` |
| defence | `build_palisade_demo`, `build_townwall_demo`, `build_tower_house(kind)`, `build_training_yard`, `build_festival_green`, `def_dress_gatehouse` |
| core (`vk_helpers`) | `build_house_v`, `build_L_v`, `build_tavern`, `build_blacksmith`, `build_smithy`, `build_inn`, `build_chapel`, `build_barn`, … |

Animated or separate parts carry custom properties that Unity can use: `SM_VK_WaterWheel` (`spin_axis`, `rpm`), gate leaves (`hinge_axis`), portcullis (`slide_axis`, `travel`), crane wheel and windmill sails. Every fire and lit window uses the `GLOW` material or the `M_VK_Window_Lit` emission, so it can be toggled.

## 6. Unity (later)

Export is deliberately postponed until the Blender files are finished. The target is the Unity project `E:\Unity\Projects\MedievalSetting`. When exporting:
- strip unused material slots per piece;
- turn Mesh Compression off for the terrain tiles, so the seams stay exact;
- import normals;
- drive the terrain ground-type map from cell data;
- the per-instance roof brightness jitter (Object Info › Random) needs an equivalent in Unity (per-renderer property).
