# Unity export

The kit goes to Unity as a local UPM package, `unity/com.danielgruginski.medievalkit`, referenced from
`E:\Unity\Projects\MedievalSetting\Packages\manifest.json` with
`"file:../../GameArtGeneration/MedievalVillageKit/unity/com.danielgruginski.medievalkit"`.
Blender stays the source of truth: `Art/`, `Data/` and `Generated/` are rebuilt and never edited by hand.
Game-specific work (prefab variants, gameplay scripts, dressed scenes) belongs in the game project's `Assets/`.

State (2026-10-01): **every master piece and every level of the world graph exported and linked.** 1236 pieces,
162 materials, the 20 levels of docs/world_graph.json under their world-graph names (`VK_ValleyTown`, `VKI_Dungeon_B1`
...), plus the slice house and the catalogs. Links work in play mode (section 8).

## 1. Running it

Blender (`src/export/vkx_export.py`, also a text in the .blend):

```python
g={}; exec(bpy.data.texts["vkx_export"].as_string(), g)
g["vkx_export_pieces"](fresh=True)                        # every master (4 collections), ~3 min; no levels
g["vkx_export_world"]()                                   # all 20 world-graph levels + Data/world.json, ~4 min
g["vkx_export_slice"]()                                   # the slice house (+ tavern, B4), ~30 s
objs = [*bpy.data.collections["VK_ValleyTerrain"].all_objects, *bpy.data.collections["VK_ValleyTown"].all_objects,
        bpy.data.objects["VK_Sun"], bpy.data.objects["VK_Fill"], *bpy.data.collections["VKX_ValleyCams"].objects]
g["vkx_export_level"]("VillageKit", objects=objs, name="Valley", export_pieces=False, origin=(1500, 0, 0))
g["vkx_export_level"]("VKI_Mine_M1", name="Mine_M1")      # any scene; objects=[...] for a subset
g["vkx_cleanup"]()                                         # after vkx_export_level calls: drops the bake images
```

Unity: **Tools > Medieval Kit > Build All** (materials, prefabs, every `Data/Levels/*.json`). It refuses to run while
an open scene has unsaved changes and reopens your scenes afterwards. Report: `MedievalSetting/Logs/MedievalKit/build_report.txt`.
`KitCapture.Capture(level, png)` renders a level's camera for side-by-side checks with Blender renders.

## 2. What the exporter writes

| Output | Contents |
|---|---|
| `Art/Models/<VK|VKI|VKT>/<Family>/<piece>.fbx` | one per master piece (the master object's name), at the origin, triangulated as Blender renders it, unused material slots dropped |
| `Art/Textures/*.png` | the kit's packed images, plus `T_VKX_*` bakes (below) |
| `Data/pieces.json` | per piece: fbx path, `slot_map` (Blender slot -> submesh), `materials` / `fbx_names`, the master's custom properties, Blender bounds, tris |
| `Data/materials.json` | per material: the KitLit parameters (below) |
| `Data/Levels/<name>.json` | placements (piece, Unity position / rotation / scale, material overrides by slot, instance properties, collection), markers (empties), lights, cameras, world, view transform |

Rules worth knowing:

- **Axes.** FBX is written with `bake_space_transform`, so Unity sees vertices as `(-x, z, -y)` with no root rotation.
  Placements go through the same matrix (`C M C^-1`), so the two agree by construction; `KitBuilder` checks every
  piece's bounds against it (`bounds check: N pieces, 0 off`). Blender's front (-Y) is Unity's +Z.
- **Restyles.** `VARI_*` (interior, base in `vki_base`) and `VAR_*` (exterior, base from the object name
  `<piece>_inst.NNN`) are the master's mesh with other materials in some slots. They export as the master plus a
  per-instance override `{slot: material}`. A restyle whose geometry differs from its base exports as its own
  piece (`U_*`; one in the slice, a barrel stack).
- **Submeshes.** Unity orders submeshes its own way and FBX merges slots sharing a material, so every used slot is its
  own submesh (a repeated material is written as a temporary copy `<name>__s<slot>`) and `KitBuilder` matches
  submeshes by those names. A master that uses one material in two slots may be restyled in one only (the tavern's
  stone walls: plaster inside, stone outside).
- **`vki_rim`** (the hearth / lava glow gradient) rides in the vertex colour's alpha; UV2 stays free for lightmaps.
- **Vertex colours** export linear (the shader multiplies them as Blender does).

## 3. Materials: `MedievalKit/KitLit`

Every kit material reduces to: albedo = map x colour x vertex colour x per-object jitter; roughness map x scale;
normal map; Blender's specular level (0.5 = F0 0.04); metallic; emission (map x colour x strength); the rim glow;
alpha clip or blend; double-sided (Blender doesn't cull). `analyze_material` reads these off the node tree.

Anything more than image x vertex colour on Base Colour, Emission Colour or Roughness (tints, HSV, painted-wood masks,
greyscale tricks, the window glass) is **baked** to a `T_VKX_<material>_<socket>.png` over the UV square, with the
vertex colour at white and Object Info > Random at 0.5 (both applied in the shader). All kit materials sample with the
plain UVMap, so the bake is exact. Cut-outs built as `alpha > threshold` keep their alpha in the baked map.

- Object Info > Random (the roof brightness jitter) is a hash of the object's position in the shader: SRP-batcher
  and instancing safe, but **static batching would give every roof the same value**.
- `Is Shadow Ray -> Transparent` (windows, webs, puddles) = the material's ShadowCaster pass off.
- Hashed alpha from a texture (webs) exports as alpha blend; `alpha > 0.5` (foliage, leaves) as alpha clip.
- **Moss** (`mossy_material`: rock and bark): a second texture set mixed in by world-up normal + moss height noise,
  gated by the vertex colour's alpha (`_VKX_MOSS`). Exported as `moss` in materials.json.
- **Translucency** (leaves 0.32, foliage and crops 0.25): the Translucent BSDF share; KitLit lowers the surface by it
  and adds light from behind (main light + ambient). Trees still render ~10-15 % brighter than in Blender.
- **No environment reflection.** Every exported level sets Lighting > Environment Reflections to Custom with
  intensity 0 (Blender's sky is not reflected; its ray tracing would hide it inside crowns and rooms anyway). A scene
  left on Unity's default (its procedural sky at full strength) washes dark leaves and painted wood blue-white at
  grazing angles: `KitHouseTools.CopyLighting` copies the setting with the ambient and the suns (fixed 2026-10-02).
- **Mask cut-outs** (`alpha > t` from a separate mask image, e.g. the net): the mask rides in the baked colour map.
- **Not baked:** networks reading the surface (Geometry, Attribute, object/world coordinates) can't be baked over the
  UV square. The leaves only use those for their normal, so the painted atlas is kept.
- **Object-space projected materials: `MedievalKit/KitTerrain`.** `vk_terrain`'s recipes ported as keyword modes:
  `terrain` (`terrain_material`: grass at two scales + HSV, sand / dirt / cobble layers from the map's control texture
  `T_VK_GroundCtl*` warped by noise, biplanar cliffs with a second offset sample, rock from above, tone drift, moss
  patches, TCol AO / rock / rim / wet, macro tint, Bump), `stair` (dressed stone over cobbles, voronoi riser joints),
  `paving` (cobbles top-projected; the curb box-projected) and `water` (two noises, alpha 0.9). The exporter classifies
  them (`_projected`: control map scale from the `CTL_MAP` Mapping, images bound by name). Blender's Noise / Voronoi /
  Hue-Saturation / Bump nodes have HLSL stand-ins in `KitNoise.hlsl`: same scales and octaves, not the same hash, so
  the patterns differ in detail. Positions are Blender object coordinates, so these meshes must stay unrotated at
  their map origin (as vk_terrain builds them). Terrain meshes carry `TCol` (R AO, G rock, B rim, A wet) as their
  vertex colour; the control map imports uncompressed, clamped, without mips.

## 4. Lights, camera, look

- Blender W -> URP intensity: point / spot `P / (4 pi^2)`, sun `S / pi` (Blender's diffuse is albedo/pi, URP's is
  albedo). Range = where the light falls to ~1 % of its 1 m value. Soft-radius shadows become URP soft shadows.
- World: the Light Path trick (lighting background vs camera background) becomes flat ambient + camera clear colour.
  A world with a sky / environment texture (the valley's `MC_World`) is probed: `world_probe` renders it
  panoramically in Cycles (lighting branch) and averages sky / horizon / ground into Unity's Trilight ambient.
- `origin=` exports a level relative to a Blender point (the valley sits at x 1500 -> exported at the origin;
  `blender_origin` in the level JSON). Spawns, links and cameras shift with it.
- **AgX:** the kit was tuned under AgX (Medium High Contrast, exposure -0.2). `KitAgX` (volume override) +
  `KitAgXFeature` (renderer feature, added to the project's URP renderers by Build All) reproduce it before URP's
  post; URP tonemapping is set to None in those levels. Scenes without a KitAgX volume are unaffected.
- Each level gets the Blender scene camera (the active one tagged MainCamera) and a global volume profile.

## 5. Gameplay data in Unity

`KitPiece` (piece name + the instance's Blender properties: `vki_link`, `vki_target`, `vki_trap`, `vki_collider`, ...),
`KitMarker` (SPN_ spawns, LGT_ / FXA_ anchors, the root), `KitLevel` (VKI_Root: camera mode, bounds, links JSON).
`vki_collider` boxes become BoxColliders on the prefabs. Exterior pieces carry no metadata and get no colliders yet.

## 6. Not done yet (next steps)

- The other levels (B1-B5, sewer, falls, dwarf hall, mine, caves) and the building interiors; scene loading along
  the world graph.
- Valley budget: 9.37 M tris in 5387 renderers (no LODs by design). Pines are 3.9 M of it (511 pines x 6-9 k tris);
  the colony camera sees a fraction, but the pine masters are the obvious place to save.
- Cast shadows: the Blender `VillageKit` scene has Eevee's scene-wide shadows off, so the Blender valley renders have
  no cast shadows while Unity draws them (the comparison renders differ by exactly that).
- Foliage brightness (above); URP's 50 m shadow distance is close to the ~40 m colony camera.
- Runtime behaviour for the data: link triggers and scene loading (world graph), spawns, doors (`hinge_axis`), the
  Full<->Cut wall toggle (`vki_cut_pair`), traps, water flow / waterfalls (`vki_flow`, `vki_fx`), lava, FX anchors.
- Exterior colliders, the per-renderer roof jitter if static batching is wanted, foliage translucency,
  point-light shadow softness (Blender's light radius), lightmapping (UV2 is free).
- Whether `Art/` + `Generated/` are committed (113 MB for the slice) or rebuilt locally.

## 7. Verification catalogs

`vkx_build_catalog(scene, collections)` lays every master out on a grid by family (linked copies) with orthographic
50-degree cameras; `vkx_render_cameras` renders them in Blender and `KitCapture.CaptureAll(level, dir)` in Unity.
Scenes `VKX_Catalog_Exterior` (486 pieces, 42 shots) and `VKX_Catalog_Interior` (713, 20) / levels
`Catalog_KitExterior`, `Catalog_KitInterior`. 2026-10-01 result: interior shots differ by ~0.026 mean (a slight
global brightness offset, no local hotspots); exterior the same except the terrain tiles (placeholder material) and
trees (above). Keep catalog cameras inside URP's shadow distance (50 m): a far camera renders with no shadows.

Gotchas found: objects created in a scene that is not on screen have a stale `matrix_world` until the view layer is
updated (the exporter now updates it); `ShaderUtil.ShaderHasError` misses errors in keyword variants — check
`ShaderUtil.GetShaderMessages` after rendering; `VK_Pieces` holds a stray helper `tmp_tw` (skipped).

Valley (2026-10-01): eight game-angle cameras in `VKX_ValleyCams` (the five entrances, town west, forge, east);
Blender vs Unity mean difference 0.041-0.064, the remainder being Unity's cast shadows and the brighter trees.
`KitCapture` compiles shaders synchronously: with async compilation the first capture after opening a scene drew
only the terrain and the shadows of everything else.

## 8. Levels and links in Unity

- **Names.** A level is a scene named as in the world graph, so a link's `vki_target` is a scene name.
  `Generated/KitWorld.asset` (built from `Data/world.json`) holds the graph; Build All puts every level in the build
  settings (start level `VK_ValleyTown` first) and runs a check: today 30 links resolve, 9 holes, 0 problems.
- **Components.** `KitLink` on every link piece (id, kind, target, arrive, prompt, facing; a trigger box from
  `vki_trigger`); `KitSpawn` on every `SPN_` (`vki_spawn_id`, facing from `vki_facing_deg`); `KitLevel.world`.
- **`KitTravel`** loads the target and puts the walker (`SetWalker`, or the object tagged Player) on the arrival
  spawn: the link's `arrive`, else the target's one link back here, else the target's `@return` door (entering a
  building). Arriving on a `@return` door pushes the way back; `@return` pops it. Without a spawn of that id the walker
  stands at the link of that id (hand-made doors). Events: `Leaving`, `Arrived`.
- **Trying it.** Tools > Medieval Kit > Play From Start Level (or Walk This Level): `KitTestWalker` (WASD, E to use a
  link, the 50-degree camera; package assembly `MedievalKit.Walker`, needs the Input System). Terrain and paving get
  MeshColliders so it has ground; exterior buildings still have no colliders.
- Verified 2026-10-01 in play mode: valley -> mine (surface) -> dwarf hall (mines) -> valley (dwarf_gate); a door into the
  tavern -> upstairs -> down -> front door (`@return`) -> valley.
- Open: the valley's building doors carry no links (HANDOFF 21), so the interiors are reachable only through a
  hand-placed KitLink; `@deep` has no level.

## 9. House generator (Unity)

The rules of `vk_helpers.build_house_v` / `_assemble` / `_dress` / `random_style`, ported to C#
(`Runtime/Generation/KitHouseGenerator.cs`). Same rules, not Blender's random sequence: a seed gives a stable house in
Unity, not the Blender house of that seed.

- **Data.** `vkx_export_house_rules()` writes `Data/house_rules.json`: the grid (cell 3, storeys 3 / 2.8, depth 6), the
  pieces filling each role (ground walls and corners per Stone / Plaster, timber upper walls and corners, tile and
  thatch roofs, chimney, dormer, porch, flower boxes, weeds, ivy, planters, lantern) and the style table (plaster 7,
  shutter 9, roof 6, cloth 6, stone 5 options; each the material that replaces its Blender slot, `vk_helpers.SLOT`).
  It also creates and exports every variant material. Build All turns it into `Generated/KitHouseRules.asset`;
  copy that asset to customise roles (your own pieces in a role list) or styles.
- **Restyling.** Every prefab's `KitPiece.blenderSlots` maps submeshes to Blender slots, so a style swaps the right
  submesh (as Blender's `VAR_` meshes do).
- **Use.** GameObject > Medieval Kit > House Generator; inspector Generate / Reroll / Clear / Save as Prefab (into
  `Assets/MedievalKitHouses`, kit pieces stay nested prefabs). Options: cells 1-6 (x 2 deep), storeys 1-3, seed, random
  or fixed style, front / back bay patterns (D door, W window, . plain), chimney, dormers, dressing.
  Tools > Medieval Kit > Generate House Set: 12 random houses as prefabs + `HouseShowcase.unity` lit like the kit
  levels (`KitHouseTools.CopyLighting`). Works at runtime too (`KitHouseGenerator.Spawn` = Instantiate).
- Verified 2026-10-01: 12 houses, 24-51 pieces, bays / corners / upper floors / roofs / dressing in place.
- **L-houses** (`build_L_v`): Shape = L, a 2 x 2 corner block with `armCells` along the front and `wingCells` to the
  back, inner corner pieces (ground + timber), the L corner roof; tile roofs only (thatch becomes red, as in Blender).
  The house set makes about a third L-houses.
- Next generators: the landmark builders (smithy, inn, town hall), interiors, caves.

## 10. Building by hand (Unity)

Tools > Medieval Kit > Kit Palette: every prefab by kit / family with thumbnails and search. Click a piece, click in
the Scene view: it lands on the kit's grid, in the space of the "Place under" object (so a building can sit anywhere,
turned any way, and its pieces still meet). R turns 90 degrees, [ ] change storey (0, 3, 5.8, 8.6 m), Esc stops.
Grids: exterior structure 1.5 m (walls on cell edges, corners on nodes, roofs on the centre line are all multiples of
half a 3 m cell), interior structure and cave / ground tiles 0.75 m, props / dressing / nature 0.25 m. Moving placed
pieces keeps them on their grid (Tools > Medieval Kit > Snap Pieces When Moved toggles it). `KitPalette.PlaceAt` does
the same from scripts. Verified 2026-10-01: a 2 x 2 two-storey house placed with every aim up to 0.45 m off, under a
parent at an off-grid position and under one turned 30 degrees: 0.0000 m error, all pieces meet.

## 12. Premade structures

`vkx_export_structures()` builds the kit's one-off buildings into scene `VKX_Structures` (one collection `VKX_ST_<name>`
each, in a row, a 50-degree camera `VKX_StCam_<name>` each) and exports each relative to its own origin into
`Data/Structures/<name>.json`, plus the whole row as level `Structures_Showcase`. The list is `VKX_STRUCTURES` (45 on
2026-10-01): the landmarks (Smithy, Inn, TownHall, Chapel), barn, windmill, guard tower, bakery, stable, the frontier /
humble buildings (log cabin, woodcutter, forester, granary, storehouse, three hovels, longhouse, pigsty, sheepfold),
the industry yards (mine, charcoal burner, tannery, dyers, brewery, apiary, pottery), town houses (merchant, gablefront,
corner, terrace), the river buildings (watermill, fisher hut, smokehouse, lavoir), two tower houses, camp, sawpit,
training yard, festival green and the four construction-site stages. Whole quarters, demos and the town map are left
out. All are made of kit masters (no one-off meshes).
Unity: Tools > Medieval Kit > Build Structures (also in Build All) -> `Generated/Structures/<name>.prefab` (kit pieces
nested, restyles applied, lights included; root component `KitStructure`). They are listed in the Kit Palette under
"Structures". Verified 2026-10-01: all 45 cameras Blender vs Unity, median mean difference 0.028, the largest local
differences being Unity's cast shadows.

## 11. Export speed

`process_materials` keeps a signature per material (nodes, settings, links, images and their packed size) in
materials.json and skips unchanged ones (and their bakes): a re-export went from ~60 s of material work to 0.08 s.
Long exports (all 713 VKI pieces) can still outlast the MCP call; Blender finishes them anyway (check the Data/*.json
times).

## 13. Rooms from plans (Unity `KitRoom`)

The interior builder (`vki_rooms`) ported to C#: a room is a typed ASCII plan (the kit's plan grid, one cell = 1.5 m,
row 0 the south / camera side; tokens in `tok_ew` / `tok_ns`) plus a room record (families, zones with floor and wall
styles, links, stairs, sills, pits, specials, passages, door leaves, gates). `vkx_export_interior_rules()` writes
`Data/interior_rules.json`: the grid and wall constants, families, post priority, plan tokens, style slots and every
style value's material, and all 19 Blender rooms with their plans as presets. Tools > Medieval Kit > Build Interior
Rules (also in Build All) makes `Generated/KitInteriorRules.asset` (the JSON, the VKI and VK prefabs by name, the style
materials by name).
- `KitRoomLayout` (runtime): `vki_parse_plan` + `vki_rooms_layout` (wall pieces with the 300 pairing and the B
  variant, rakes, posts required and rhythm, floors 600 / 300 / Q150 by parity, dais, stair and pit cells).
- `KitRoom` (runtime component; GameObject > Medieval Kit > Room From Plan): pick a preset or type a plan and record,
  Generate. Builds the shell like `vki_build_scene`: walls restyled by zone (wall_a / wall_b, caps, special and window
  styles, Night window styles), required posts, floors, sills, exits (door, closed leaf or wide pair, apron, rush mat,
  `KitLink` + trigger, `KitSpawn`), stairs, barred gates, passages, door leaves, pits, rhythm posts (skipped where a
  prop / overlay / stair touches the post square), doorway mats, window light pools (Day) and the pieces' lights.
  Blender room space (x, y, z) is the component's local (-x, z, -y). Works at runtime (`KitRoom.Spawn`).
- Furniture (phase 2, `KitRoom.Props.cs`): Furniture = Auto takes the record's prop list when it has one, else the
  plan's cell codes (Record / Codes / None force one). Props go in by their mount, in outline of `vki_place`:
  wall_floor backs onto the proud line of the wall behind and slides (<= 0.30) off side walls and post squares;
  wall_hung backs onto the wall face (or hangs from the top); table dressing stands on its host's top; floor props are
  pushed off walls; prop links (the lift) get a link and spawn. Rhythm posts and doorway mats then make room for them.
  From codes: each block of one code (not split by walls) takes the largest piece of that code that fits, at the
  block's centre; a block holding several footprints is tiled (a row of pews); trestle tables get forms on their long
  sides where the cells are free; pieces at a wall turn their back to it (a worktable too: it has a top, but stands
  against its wall). Inspector "Codes -> Record" writes that list
  into the record to edit by hand. A bare plan (no record) builds with defaults: Timber / Board walls, board floor, a
  front exit back to where one came from.
- Caves (phase 3, `KitCaveLayout.cs`): a record with "cave": true makes the plan a cell map ("##" rock, all outside
  the map rock). A rock tile stands on every node whose four cells are not all open: the corner code (SW SE NE NW of O
  open / C cut / F full rock; Cut in the south ring and row or with floor within two cells north) picks the master and
  its turn, a variant by the node's hash; walls on the map's inner grid lines are laid out as partitions and the rock
  tiles on their nodes are the wall-backed masters. Chasm ("vv", "==") and stream ("ss") cells get dual-grid ground
  tiles (waterfalls where a stream meets the chasm), sewer ("ww") and lava ("ll") cells channel tiles with a flow
  direction (`vki_flow`); floors are Q150 cells, or 0.75 m quarters round the ground tiles; R["tunnels"] puts a tunnel
  (or the mine's adit) with its passage link and spawn on a straight Full face; R["tracks"] lays the mine's track.
- Random caves (`KitCaveGenerator`, inspector "Random Cave" / "New Seed" with the Cave settings; Rooms > Build Cave
  Showcase). Layout "Maze" (default): nodes on a jittered lattice about 6 cells apart (chambers with noisy outlines, or
  junctions) joined by winding tunnels 2-3 cells wide along a randomised depth-first spanning tree of the lattice
  (corridors, turns, dead-end leaves) plus loops and spurs ending in alcoves (loot, a skeleton, a chest); walls
  roughened and smoothed shut only, so the rock between tunnels stands. Layout "Open": the kit's cellular automaton.
  The chasm carves its own gorge across the map: a curve from one side, through a point on the cave's floor in the
  middle, to the other side (a fork optional), its width breathing between Chasm Width x..y cells (pinching to nothing
  leaves a natural rock bridge), with ledges >= 2 cells along stretches of it. Where it cuts the cave in two: a rope
  bridge over a two-cell narrows (turned to the crossing), a one-cell gap filled as a land bridge, or a wider stretch
  pinched to two cells round a bridge; floor islands under 6 cells become rock pillars; the cave kept is the largest
  region one can walk. A bridge's deck has chasm on both sides (floor beside it would be cut off by the rails, and a rock
  tile's lobe narrows a landing below an agent's width), its landings have no rock beside them, decks stay two cells
  apart, and a deck joins only the cells along its span when regions are counted. Alcove finds and dressing (crystals,
  mushrooms, stalagmites, boulders; against tunnel walls too) never cut the floor: the regions stay as many and no free
  cell beside one is left in a one-cell squeeze. System.Random: not Blender's maps for a seed (vki_cave_generate is
  the old automaton).
- Random dungeons (phase 4, `KitDungeonGenerator`, inspector "Random Dungeon"): a cave map with rooms dug into the
  rock (the first a great hall of 7-9 x 5-7 cells, the rest 3-7 x 3-5), joined by corridors two cells wide (a spanning
  tree plus loops; no checkerboard pinches, no one-cell necks), walled in Dungeon stone on the grid lines between floor
  and rock (Cut on the camera side, the rock behind Cut / Full) with a door (or an open gap) where a corridor meets a
  room; some rooms natural cave pockets (their ways in: the middle two cells of each opening onto a tunnel). A stair up
  (Stone) where the player arrives, a stair down in the room farthest from it: any three cells along a wall, up with
  its top against the wall it runs into (corners first), down a hole whose arrival is on the piece's local +x side
  (its spawn), so that side faces into the room; another room when the first has no room. Room themes (guardroom,
  cells, crypt, store, shrine, warren, lair) are written into the plan as furniture codes (`KitFurnisher`: along walls /
  in the middle, a cell apart, and only where every walkable cell of the room stays reachable from its doors and the
  stair) with set-pieces as record props (`KitSetPieces`, below): a shrine's altar between guardian statues with
  braziers before it, the lair's treasure chest between braziers, chains on the cells' walls, the guards' table laid
  and a weapon rack, pillars down the larger rooms (rock pillars in pockets); torches, debris and an encounter per room
  (record "encounters" -> `KitEncounter`: creature tag, budget 1 + depth from the entrance, the lair +3 and boss, spawn
  points spread over free cells). Themes: Dungeon (mixed), Crypt, Warren. Record flag "props_from_codes": the plan's
  codes and then the record's props both furnish (codes first, so the record's table dressing finds its tables).
- Random house ground floors (`KitInteriorGenerator`, inspector "Random Interior"): Cottage / Townhouse / Tavern /
  Workshop; a hall (taproom, workroom) with the front door and the hearth (Timber Fireplace_300 / Stone Hearth_300),
  side rooms (bedroom, kitchen, pantry, store) behind partitions with doors (two side rooms only when each is three
  cells deep), windows, raked side walls, zone styles, furniture codes through `KitFurnisher`. Set-pieces first: the
  taproom's bar (counters a cell out from a wall, cask racks behind them, an end piece and the barkeep's way in behind
  it), the kitchen's oven beside its worktable, the workroom's bench under a tool wall; then the codes' furniture; then
  the dressing: a log basket by the hearth, a chest beside the bed with a candle on it, table dressing by room (tavern
  mugs, meals), lanterns on full-height walls. Taverns are 9-11 x 6-7 cells (a bar and tables).
- `KitSetPieces` (runtime, shared by the generators): groups the furniture codes cannot say, as record props. A
  set-piece holds its cells with the code "@@" (furniture the record places: the codes' furniture skips it, the walk
  test counts it as a prop), keeps the cells it needs clear (the way up to an altar, behind a bar), and goes in only
  where the room stays connected (`KitFurnisher.Connected`). Pillars stand on grid nodes (a corner of four cells, all
  four left walkable). Wall-hung pieces go on full-height plain walls away from doorways.
- Walkability (`KitDecks`, `AddGroundFloor`, Tools > Medieval Kit > Rooms > Walk Test): chasm / stream tiles block their
  chasm with 1 m boxes and owned the floor of their open quarters without a collider (a 0.75 m strip with nothing to
  stand on along every chasm edge): the prefab builder now gives those quarters a floor slab. Bridges (vki_bridge
  decks: rope bridge, dwarf / sewer bridges, stepping stones) get a walkable deck and the ground tiles' blocking boxes
  are cut round it (KitRoom and the level builder run KitDecks; B4, Cave_Falls, Dwarf_Hall, Sewer_S1 rebuilt). The walk
  test bakes a navmesh (UnityEngine.AI.NavMeshBuilder, radius 0.3, height 1.8, 0.05 m voxels; openable leaves left out)
  and paths from the first spawn to every spawn, encounter point and plan cell. Game notes: agents must stay under
  ~0.35 m radius (doors leave 0.84 m, the rope bridge 0.88 m) and need fine voxels on narrow decks; openable leaves
  (portcullis, iron / secret doors, gates) want a carving NavMeshObstacle switched with the door.
- The walk test bakes one navmesh per room from its own colliders (rooms side by side or another open scene's do not
  mix); its island check skips stair cells and cells holding a prop's code (a sliver of navmesh between a statue and a
  wall is not stranded floor). The showcase builders ask to save modified open scenes first (they open a new scene);
  the cave, dungeon and interior builders also build additively (`Build...Showcase(true)`: a new scene beside the open
  ones, which the caller closes) and use their own scene's camera.
- Tools > Medieval Kit > Rooms > Validate Generators (20 seeds): builds seeds of every generator (cave Maze / Open,
  dungeon Dungeon / Crypt / Warren, interior Cottage / Townhouse / Tavern / Workshop) one at a time in a temporary scene,
  walk-tests each (every spawn, encounter point and floor cell reachable from the first spawn) and lists the failing
  seeds (`Logs/MedievalKit/generator_validation.txt`; `KitRoomTools.ValidateGenerators(count, which, firstSeed)`).
  `KitRoomTools.WalkMap(room)` prints a room's plan marked by the navmesh ('o' reachable, 'x' cut off) for one seed.
  Verified 2026-10-02: seeds 1-120 of all nine walkable everywhere (1,080 levels).
- Verified 2026-10-01: the 3 showcase dungeons and 6 random interiors are walkable everywhere (every stair, encounter
  point and floor cell reachable); all 19 kit rooms reach every spawn; a few floor pockets of kit levels are cut off
  (B2 3 cells, Cave_Breach 3, Dwarf_Hall 10, Mine 4 = the caved-in drift, B3 1) and are left for review.
- Chains (one continuous world; how to use them: the package's `Documentation~/LEVEL_BUILDING.md` 5.5). A map's
  way out is a `KitPortal` in its generator's `portals` (side, cell along the edge, width): the generator opens the
  edge there, runs a straight way in for 3 cells (natural rock in a dungeon) and on to the floor, and records
  R["portals"]; `KitRoom` puts a `KitPortalMarker` on each opening and a spawn inside. `KitConnectorGenerator` makes
  the short passages between maps (straight or round a corner, winding, a chamber sometimes, glowing mushrooms);
  both its ends are seams. Seam rule (`KitCaveLayout.CaveCells` / `CaveTiles`): beyond a map's opening the floor runs
  on and the `Margin` (2) cells either side are cut rock; the map builds the rock tiles on the seam line, the
  connector skips them and gives its seam row the heights the map assumes (cut in the band, else what the map makes
  of its ring there), so the shared cells agree. `KitChain` (asset: maps in order, each joined to an earlier one,
  the one before by default, through a connector: a tree, every portal joined once) is baked by `KitChainTools.Bake` (pieces lined up in world space, overlap check, walk test, a scene per
  piece, build settings, a play scene with `KitChainStreamer` and the test walker); the streamer keeps the walker's
  piece and its neighbours loaded. Verified 2026-10-02: connectors 4 shapes x 30 seeds, sample chains 20 / 20
  walkable end to end across the seams (`KitChainTools.WalkChain`); with a branch (7 pieces) 20 / 20. Limits: no
  loops, connectors are level, no navmesh across pieces, no ruins generator.
- Debris (`KitRoom.Debris.cs`): R["debris"] {density, seed, zones, themes} strews the kit's debris by zone theme
  (cave, lair, dungeon, ruins, sewer, dwarf, forge, mine) on free floor, clear of walls, posts, props, rock and spawns;
  the generators set it (caves 0.34, dungeons 0.25). Not compared piece for piece with Blender's (counts are close).
- Not yet: monster spawning and combat (the game's: KitEncounter only marks where and how hard).
- Golden test: Tools > Medieval Kit > Rooms > Golden Test rebuilds the 12 walled rooms and compares them with the
  levels Blender exported (`Logs/MedievalKit/room_test.txt`): structure to 2 mm, props to 5 cm (the general idea, by
  the user's call, not Blender's every refinement). Verified 2026-10-01: structure 720 / 720 pieces with materials,
  spawns, links and lights; with furniture 10 of 12 rooms match outright, 3 props differ by about 0.3 m (Blender's
  junction-node slide) plus the rhythm post that follows; debris is not ported. With the caves (all 19 rooms): the 7
  cave levels match piece for piece (2,437 pieces: rock, ground and channel tiles, quarter floors, tunnels, track,
  waterfalls; materials, spawns, links, lights). Furniture from codes alone finds 238 of the 249 coded props.
  The export keeps each room's zone order ("zone_order"; JSON keys are sorted, and the first listed zone wins where
  zones overlap, as in the dwarf hall).
- Tools > Medieval Kit > Rooms > Build Room Showcase: `Assets/MedievalKitRooms/RoomShowcase.unity`, the 12 rooms
  generated in rows, then four of them furnished from their codes alone, the 7 cave levels, two random caves
  (seeds 7 and 31, the second with the wyrm bones), six random house ground floors and a plan typed from scratch.
  Rooms > Build Dungeon Showcase: `Assets/MedievalKitRooms/DungeonShowcase.unity`, three generated dungeons (Dungeon
  seed 11, Crypt 5, Warren 9) lit like VKI_Dungeon_B1. Rooms > Build Cave Showcase: `CaveShowcase.unity`, four random
  caves. Rooms > Build Interior Showcase: `InteriorShowcase.unity`, two of each house kind (seeds 3 and 8) lit like
  VKI_Tavern_F0.

## 14. Outdoor maps (Unity `KitVillage`)

- `KitVillage` (Runtime/World) builds an outdoor map from a JSON layout in plan metres (x east, y north, origin at
  the south-west corner): a ground mesh (`M_VK_Terrain` instance; control map R dirt / G cobble painted along road
  curves, lumpy areas and doorsteps, noise-warped edges), relief rising into the forest, level pads under buildings;
  `Generated/Structures` prefabs or `KitHouseGenerator` houses turned so their door faces a point; gardens, fences
  along Catmull-Rom curves, props, trees; a dart-thrown forest round a lumpy clearing with a ragged edge, stragglers,
  undergrowth and a margin beyond the map; scatter; colliders (building walls, props, fences, trunks) and invisible
  walls (a ring inside the forest with gaps at roads, walls along the roads through it, the map border); `KitSpawn`s,
  `KitMarker`s, exits (`KitLink` triggers where roads leave the map) and door links. Problems (overlaps, a building
  on a road or past the forest's wall) go to `notes`.
- `KitVillageTools.BuildVillage(layout, scene)` (Tools > Medieval Kit > World > Build Village From Selected Layout)
  builds additively in a scene of its own, saves the ground's mesh, control map and material beside it, lights it
  like VK_ValleyTown, adds a camera at the start spawn and walk-tests it (`WalkVillage`: navmesh from the start
  spawn; every spawn and marker reached, probes in the forest beyond the wall not).
- Verified 2026-10-02: MedievalSetting `Assets/MedievalKitWorld/Hamlet.unity` (140 x 160 m, 14 buildings, 3 exits):
  walk test ok, 7 spawns, 4 markers, 24 forest probes. Layout schema and rules: the package's
  `Documentation~/LEVEL_BUILDING.md` 5.7; example `Documentation~/examples/Hamlet_layout.json`.
- Linking (2026-10-02): `KitTravel` lands on the link's `arrive`, else the kit world's rule, else the spawn named
  like the link; "@return" is remembered on arrival at a door whose target is "@return". A chain is entered by a
  scene link whose target is its play scene and whose `arrive` is a spawn of one of its pieces (the streamer starts
  there). Hand-made maps join chains as `KitChain.Kind.Plan`. Verified in play mode on the hamlet: village -> inn ->
  cellar chain -> inn -> village, and the chapel's @return.
- Cave encounters: `KitCaveGenerator.Options.creature` / `encounters` (30 / 30 seeds walkable with every spawn point
  reached). `KitRoomTools.BuildRoomScene`: a hand-made plan + record (files) as a level scene, walk-tested.
- Outdoor maps, 2026-10-02: several clearings (glades), palisade rings (closed fences, gates at their own width,
  walkways along an offset line), link pieces as doors (cave mouths), encounters, exits with arrivals; invisible walls
  are the outline of the walkable ground on a 1 m grid. Caves: creatures by depth, themed dressing, finds as loot
  markers, the game's own prefabs by name. Chained dungeons: an exit stair to a scene. Examples: MedievalSetting's
  Woods and Warcamp, and the HamletCellar chain from the inn's cellar to the warcamp's cave.
- Navigation and travel, 2026-10-02: every level carries a baked navmesh (`KitNavMesh`, baked by the builders and
  `KitNavBake`) for the game's NavMeshAgents; `KitTravel.Preload` holds the levels one link away loaded and switched
  off, so doors are instant cuts. LEVEL_BUILDING 5.8-5.9.
