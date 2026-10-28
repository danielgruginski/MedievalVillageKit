# Full port plan: a complete Unity kit and a Godot kit with everything it has

Daniel's brief (2026-10-24): the Godot kit gets **everything the Unity kit has**, shaders included, even where that
means writing code; and the **Unity kit becomes complete** by moving into it what already exists in the Guild RPG
(MedievalSetting) but is not game-specific -- the see-through's driver, the outdoor-map generators and the like
("transposing code that already exists in the game into the kit"). The Godot export pilot (docs/GODOT_EXPORT.md,
HANDOFF 143) settled the art route; this file plans the rest.

## 1. Decisions

| | Decision | Why |
|---|---|---|
| Godot language | **C#** (Daniel, 2026-10-24) on Godot 4.7.2's .NET build | the kit's 15,800 lines of C# port nearly line for line; the kit draws only from `System.Random` (checked: no `UnityEngine.Random` in Runtime), whose seeded sequence .NET 8 keeps from Mono's, so a generator gives the same level for the same seed in both engines (the parity test; float-heavy steps and collection order after removals to watch); the game's own code is C# |
| Outdoor maps | **generic seeded generators in the kit** (Daniel), made from the game's 16 per-map scripts | the kit has generators for dungeons, caves, sewers, interiors, connectors and houses, but none for outdoor maps |
| Engine-free logic | new generator code written once as a shared C# core (no engine types), compiled into both kits; existing Unity logic moved into it only when it is ported, checked seed for seed | one implementation to fix; Unity: an asmdef with `noEngineReferences`, Godot: the same files in the .csproj |
| Materials in Godot | **every kit material on KitLit** (a ShaderMaterial), as in Unity | the see-through and the shroud clip every kit material; a StandardMaterial3D cannot take that code. The pilot's StandardMaterial3D mapping stays as the reference KitLit must match (same harness) |
| Godot package | `godot/addons/medieval_kit/` in the kit repo, linked into Godot projects (a directory junction) | the counterpart of `unity/com.danielgruginski.medievalkit`; the generated art (`res://kit/`) stays out of git like `Art/` / `Generated/` |
| Order | anything that moves out of the game goes into the **Unity kit first**, then to Godot | Godot ports one finished kit, and the game is the check that the move kept it working |

## 2. Inventory

### 2.1 The Unity kit today (to port)

| Area | Unity | Lines |
|---|---|---|
| Shaders | KitLit (+ `KitSeeThrough.hlsl`, the `SeeThroughCap` pass, `KitShroud.hlsl`), KitTerrain (+ `KitNoise.hlsl`), KitGrass (+ `KitGrassCull.compute`), KitSea, KitWaterMask; KitAgX not needed (Godot's AgX, contrast 1.5) | 2,000 |
| Data + levels | KitData, KitPiece, KitMarker, KitSpawn, KitStructure, KitLevel, KitLink, KitPortalMarker, KitWorld, KitTravel, KitChain, KitChainStreamer, KitEncounter, KitDecks, KitNavMesh | 1,032 |
| Rooms + generators | KitRoom (+ Props, Debris), KitRoomLayout, KitCaveLayout, KitSetPieces, KitFurnisher, KitPortal, KitInteriorRules; KitDungeon / Cave / Sewer / Interior / Connector generators; KitHouseGenerator + rules | 5,693 |
| Outdoor maps | KitVillage (+ Terrain, Grass, Patches, ForestDress), KitGrass, KitSolid | 2,956 |
| See-through + shroud | KitSeeThrough, KitSeeThroughProbe, KitSeeThroughCaps (+ CapBank), KitShroud | 1,568 |
| Units, look | KitUnitEvents (the siege catapult); KitAgX + its renderer feature (not needed in Godot) | 29 + 91 |
| Editor | KitBuilder, KitImport, KitPalette, KitHouseEditor, KitRoomEditor, KitVillageEditor, KitChainEditor, KitNavBake, KitPlay, KitCapture, the caps bake | 4,353 |
| Walker | KitTestWalker | 96 |

### 2.2 In the game, to move into the Unity kit

From a read-only survey of MedievalSetting (2026-10-24; paths under `Assets/Game/Scripts/` unless given). Of the
game's ~55k lines, ~40k are the RPG itself (combat and `GameRules`, items, party, player, quests, UI, NPCs, saves,
spells) and stay. The other art repos' folders (`Beasts/`, `Goblins/`, `Humans/`, `Insectoids/`, `Weapons/`) are their
own pipelines (section 3, phase 7).

**Moves almost as is** (no game dependency, or one that becomes a hook):

| What | Where | Lines | Hook to cut |
|---|---|---|---|
| Z-fight watch (two off-screen renders find coplanar faces, CSV + PNG) | `ZFightWatch.cs` + `Game/Resources/ZFightProbe.shader` | 482 + 136 | none |
| Fires: flicker, particle parts, steady / blaze / collapse / smoulder fires; lighting the kit's torches, braziers, hearths (the `M_VKI_GlowIn` submesh to coals, the `LIT_*` light flickering) | `World/FireFlicker.cs`, `FireFx.cs`, `Fire.cs`, `LevelDirector.cs` (KitFires, ~100), `Editor/FireFxMenu.cs`, `Game/Tools~/fx/make_fx.py` | 64 + 557 + 435 + 100 + 122 + 270 | `Sfx` (5 calls) -> a sound event; `Campfire` |
| Decks: a runtime navmesh over walkway tops without colliders | `World/Decks.cs` | 72 | the deck names from `GameRules` -> a parameter |
| Click-to-use base (use point, radius, priority) | `World/Interactable.cs`, `UseVia.cs` | 77 + 22 | none |
| A thrown / shot object's flight arc | `Combat/Missile.cs` | 88 | none |
| Map <-> world transform and walk-grid spans (the camera stays over walkable ground) | `World/AreaMap.cs` (`WalkWindow`, the geometry of `AreaMapData`) | ~160 | `GameRules.NpcRole` in `Person` -> split off |
| Silhouettes of hidden actors (rendering-layer bits laid out round the see-through's) | `CreatureSilhouettes.cs` + shader | 135 + 97 | `Creature.All` -> a registry |
| Small helpers: drops scattered on the navmesh, floor raycast; the "add scene to the build" helper copied across menus | `World/GroundLoot.cs` (Scatter, Floor), `Editor/*Menu.cs` | ~40 | none |

**A generic core inside RPG code** (the kit takes the core; the game keeps its rules on top):

| What | Where | Lines | Generic core |
|---|---|---|---|
| **Game camera + the see-through driver** | `GameCamera.cs` | 245 | the 50-degree follow camera and zoom, level cameras / listeners off on `KitTravel.Arrived`, sky outdoors / black indoors, shadow distance; sets `_KitSeeThrough` / `_KitSeeThroughArgs` and runs `KitSeeThroughProbe` with open / shut hysteresis. Hooks: area map, UI-blocks-pointer, ambience, look preview |
| **Click to move** | `ClickToMove.cs` | 613 | navmesh floor under the cursor seen through the hole (`SeenThrough`, `KitSeeThroughCaps.CutAt`), hold-to-walk, taking links (road ends, doors, `HouseUnder`); RPG: creatures, combat, loot, party (~40 uses) |
| Area maps + fog of war | `Editor/AreaMapsMenu.cs`, `World/AreaFog.cs`, `AreaMap.cs`, `UI/MiniMap.cs`, `UI/AreaView.cs` | 471 + 248 + ... | the tiled top-down render of a KitVillage level, the reveal grid; the POIs and the UI are RPG |
| Day / night on outdoor maps | `World/DayNight.cs` (+ `GameClock.cs`) | 223 + 62 | sun, moon, ambient, sky, lit windows, lamps; the clock's length and saves are the game's |
| Level director: dressing markers, resource-node placement (veins at rock edges reachable from a spawn, patches, trees) | `World/LevelDirector.cs` | 674 | placement rules; what they create (`Gatherable`, `Npc`, `Gate`...) is RPG |
| Interior dresser: one shared interior dressed per door (palettes, clutter kept off paths, props removed) | `World/InteriorDresser.cs` | 479 | the dressing; palettes come from `GameRules` |
| Gate parts (a kit gate cut into frame, leaves, bar), ladders as link cuts, closed ways, world-map routes, per-scene world state, encounter spawning | `GateParts.cs` + `Editor/GatePartsBuilder.cs`, `Ladder.cs`, `ClosedWays.cs`, `WorldMap.cs`, `WorldState.cs`, `Combat/EncounterSpawner.cs` | 22 + 185 + 118 + 168 + 340 + 99 + 211 | mechanisms; contents are quests / rules (`WorldMap` overlaps `KitWorld`) |
| Footsteps by surface | `Audio/Footsteps.cs` | 114 | surface from collider / material names |
| See-through capture harness | `Editor/SeeThroughSpike.cs` | 320 | the capture; its cases are Hamlet / Greywall |
| Boot | `GameBoot.cs` | 164 | spawn at a `KitSpawn`, the test walker removed, `KitChainStreamer` hooked |
| Level recipes for the room generators (plan, record, scene, walk test, nav bake, build entry) | `Editor/{Barrows,Burrow,Crypts,Dens,Interiors,Sewers,Smugglers,WarTunnels,WaspNests,Well}Menu.cs` | ~2,240 | reusable steps: a cave mouth open to daylight instead of a stair, a crawl hole, keep only the deepest encounter |

### 2.3 The outdoor maps (`MedievalKitWorld/Tools~`, 5,273 lines of Python)

Shared already: `raster.py` (check pictures), `lone_oaks.py` (oaks and gather markers kept off everything),
`layout_check.py` (rasterises the terrain as `KitVillage.Terrain.cs` does; unreachable markers, doors, spawns, bad
ramps, buildings on cliffs), `saltmere_common.District` (roads, squares, a town wall of 3 m modules between round
towers with gatehouses, landmarks with measured footprints, houses filled along streets, an edge ring closing a
district, exits with banners, shared-interior doors by hash), `burnt_textures.py`. Copied instead of shared:
`catmull` (7 copies), the vector helpers, `BOX` / `place` / `fill` / `door_for` (Greywall, the market, `District`),
`smoulders`; Greywall's wall nudges its corners to whole modules, `District.city_wall` does not. Per-map data only:
hamlet, woods and warcamp (ported from hand-made JSON), the rest's polylines, landmarks and markers.

A kit generator has to offer what those layouts use: map size / margin / seed / relief / rim; clearings (chains of
glades), mounds, terrain tiers (areas, levels, ramps); catmull roads (width, surface), squares; buildings (a structure
or `house{cells, stories}`, door target / arrive / prompt), yards and gardens, fences; town walls with towers and
gatehouses; market rings; forest (species, edge, keep off roads and buildings, undergrowth), scatter, grass; the burnt
variant (ground, swaps, ash patches, smoulders); spawns, links, markers, encounters, exits -- with the game's
vocabulary (marker roles, interior scene names) as parameters, and the layout check and picture built in.

## 3. Phases

Each phase ends with its check passing and its record in HANDOFF; commits and Plastic check-ins only when Daniel says.

0. **Set-up. Done 2026-10-24 (HANDOFF 145).** Godot 4.7.2 .NET build, the addon `godot/addons/medieval_kit/` linked
   into the project, `MedievalKit.csproj` (net10.0), `tools/gdx_round.sh` on C#; the pilot's GDScript tools became the
   addon's C# editor tools (`KitImport`, `KitBuilder`, `KitCapture`, behind `kit_cli.gd`). Check: the pilot round gives
   the GDScript run's numbers exactly.
1. **Godot art, the whole kit. Done 2026-10-24 (HANDOFF 147; GODOT_EXPORT 5b).** All the pieces and materials, every material on KitLit (alpha, cull, translucency
   variants; the leaves' bump; point / spot lights) and KitTerrain (terrain, stair, paving, curb, water). Check:
   KitLit-for-all against the pilot's StandardMaterial3Ds (identical) and Blender; the verification catalogs
   (vkx_build_catalog), Blender vs Godot. KitSea, KitGrass (+ its culling compute) and KitWaterMask move to phase 5:
   only KitVillage builds them, so they are checked there against Unity.
2. **Godot levels. Done 2026-10-24 (HANDOFF 148; GODOT_EXPORT 5c).** Data, pieces' metadata (colliders, links,
   spawns, markers), the 20 world-graph levels and 45 structures, navmeshes, travel along the world graph, the test
   walker and a demo. Check: walk tests and Godot's own paths (all 20 levels), the travel test (40 links, preload),
   Blender vs Godot captures from the levels' cameras. Chains and their streamer moved to phase 4: a chain's pieces
   are made by the generators.
3. **Unity kit, completed from the game** (can run beside 1-2: different files). One system at a time: moved into the
   package, the game switched to it (its rules on top through hooks), the game played by Daniel or with his OK.
   a. The table of section 2.2 that moves almost as is (z-fight watch, fires, decks, click-to-use, missiles, walk
      window, silhouettes, helpers). **Done 2026-10-25 (HANDOFF 156), not play-tested:** compiles clean in the game;
      left for later: the build-settings helper copied across the game's level menus.
   b. The camera and the see-through driver out of `GameCamera`, and the click-to-move core (floor through the hole,
      links, doors): with them the kit's see-through works without the game, and the test walker becomes a real one.
      **Done 2026-10-26 (HANDOFF 159), not play-tested:** KitCamera, KitPointer, KitClickToMove, KitWalker,
      KitSeeThrough.Opened; the game's GameCamera and ClickToMove are subclasses with its rules on top.
   **3c and 3d parked 2026-10-26** (Daniel, on whether the package was growing past what people want from it: "lets
   keep godot up to date with unity"): the Unity package stops growing here; Godot is brought level with everything
   it has (phases 4-6, with 3a-3b's systems in 6). 3c-3d come back only if buyers or the game ask for them.
   c. The outdoor-map generators (section 2.3): the shared C# core with the layout check built in, then generators
      for the kinds the game has made by hand (walled town, village and hamlet, district of a city, road, wilds and
      woods, camp and hold, a burnt variant). Check: maps of each kind generated over many seeds pass the layout check
      and the walk test; the game's existing maps stay as they are unless Daniel wants them regenerated.
   d. The generic cores of the mixed table (area maps and fog, day / night, resource-node placement, interior dressing,
      gates, ladders, closed ways, world-state memory, encounter spawning, footsteps, the generator recipes' steps).
4. **Godot rooms and generators.** KitRoom and the six generators (+ the new outdoor ones from the shared core), and
   chains (KitChain, its bake, KitChainStreamer and KitTravel's hand-over to it).
   Check: same seed, same layout as Unity (dumped and diffed), the generators' walk validators.
   **Done 2026-10-28 (HANDOFF 167; GODOT_EXPORT 5d).** KitRoom, the cave / dungeon / sewer / interior / connector
   generators, the house generator, chains with their bake, streamer and KitTravel hand-over (no outdoor generators:
   3c is parked). Same seed, same level: 1,000 generated plans the same as Unity's Mono run of the Unity sources; 48
   built levels the same as the Unity editor's (every placement, spawn, link, encounter); 20 houses the same; the golden
   test as Unity's (17 / 19, the two known prop slides). Walk: 320 / 320 generated levels (20 seeds x 16 runs), the
   sample chain 10 / 10 seeds end to end, the streamer over the baked chain. Daniel's order after it (2026-10-28):
   phase 5, then the Godot itch files, and phase 7 after those.
5. **Godot outdoor maps.** KitVillage (terrain, grass with GPU culling, patches, forest dress, the sea) with the
   KitGrass, KitSea and KitWaterMask shaders, navmesh baking (NavigationRegion3D), the shroud. Check: a game map's layout built in both engines, captures from its cameras.
   **Done 2026-10-28 (HANDOFF 168; GODOT_EXPORT 5e).** Same rules, not the same numbers (Daniel: "no need to do a
   perfect copy, they can differ in results"). All 11 of the game's outdoor layouts build and walk in Godot (9 clean,
   2 with a forest leak that Unity's map shows too); Hamlet and Woods match Unity's area maps plan for plan; the
   grass culls per 16 m chunk (no compute cull). The see-through leftovers below are done with it.
6. **Godot see-through.** The shader's hole and caps pass, the hidden check (a small SubViewport read back), a building
   opening as one, the baked caps, and the driver moved out of the game in phase 3. Check: the spike's edge-case
   gallery (docs/history/SPIKE_SEETHROUGH.md) walked in both engines.
7. **The other repos** (GODOT_EXPORT section 7): weapons and items, creatures, humanoids.
8. **User documentation** (Daniel, 2026-10-26: "Do we have the documentation about how all this stuff works? If we
   don't add it to the list"). Today: the Unity package has a 10-line README and `Documentation~/LEVEL_BUILDING.md`
   (level building, written for AI agents) and, since 0.3.0, `Documentation~/MANUAL.md`; the Godot addon `addons/medieval_kit/MANUAL.md` since 2026-10-27 (HANDOFF 166); the repo's docs (UNITY_EXPORT, GODOT_EXPORT,
   HANDOFF) are for developing the kit, not using it. Wanted, one manual per engine, in the package / addon (shipped
   with the packs): getting started (install, the demo, the palette), pieces and their data (colliders, links,
   markers, decks), levels and the world graph (travel, chains), the generators (rooms, dungeons, caves, sewers,
   houses, outdoor maps), the see-through (how the hole, the caps and the driver work, what a game must call), fires,
   the map frame / walk window, the shroud, the hooks a game fills, and the tests (walk, travel); plus the FBX / glTF
   zip's README. Written as each system lands in the kit (3b's driver and walker first), checked against the code.
   Order agreed 2026-10-26: 3b, then the Godot see-through (6), the Unity pack, then 4-5 and the Godot pack.
   Godot's phase 6 also takes 3a-3b's systems (fires, usable things, missiles, silhouettes, walkways, map frame +
   walk window, the z-fight watch, the camera, click to move, the walker), so the two engines offer the same kit.
   Done in Godot: the see-through, the camera, the map frame (HANDOFF 161); click to move and the walker (162); the
   real caps, baked (164); the 3a systems: fires, usable things (with click to move), missiles, silhouettes, walkways,
   ground helpers (165); the manual (166). **The z-fight watch is not part of the Godot addon** (Daniel, 2026-10-27:
   "The Zfight scanner will not be part of the godot"; the pieces are checked in Blender). Done with phase 5
   (HANDOFF 168): HouseUnder, the house floors under the hole, loose nature / props and wall runs
   (`KitVillage.SetUpSeeThrough`).
