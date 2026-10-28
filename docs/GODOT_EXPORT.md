# Godot export

The kit goes to Godot 4.7 straight from Blender (Blender -> glTF -> Godot, no Unity in between), beside the Unity
export, which it reuses and leaves untouched. Pilot done 2026-10-24 (HANDOFF 143), the C# set-up the same day (HANDOFF
145), the whole kit (147) and the levels (148); the rest: FULL_PORT_PLAN.md.

**To look at it** (no Godot knowledge needed): double-click `Play Medieval Kit demo.bat` in the Godot project folder --
a menu of the levels; walk with WASD, E at doors and stairs, Tab for Blender's camera views, F for a free camera (hold
the right mouse button to look), Esc back to the menu. `Open in Godot editor.bat` opens the project in the editor
(F5 or the Play button runs the same demo; double-click a level in `res://kit/layouts/` to open it in the 3D view).

- Exporter: `src/export/gdx_export.py` (runs in a background Blender; execs `vkx_export.py` for its readers).
- The Godot package: the addon `godot/addons/medieval_kit/` (the counterpart of `unity/com.danielgruginski.medievalkit`):
  `Shaders/` (KitLit), `Editor/` (C#: `KitImport` post-import, `KitBuilder` layouts + piece check, `KitCapture`;
  `kit_cli.gd`, the command-line entry), `Runtime/` (C#), `MedievalKitPlugin.cs` (Project > Tools menu). A project gets
  it as a directory junction `addons/medieval_kit` (`gdx_link_addon` makes it), so it is edited in the repo only;
  Godot's `.uid` files beside the sources are kept in git.
- Godot: the **.NET build** 4.7.2 (`C:\Users\danie\Downloads\Godot_v4.7.2-stable_mono_win64\`, SHA-512 checked against
  the release's sums), .NET SDK 10. The project targets `net10.0` (`MedievalKit.csproj`; its `nuget.config` points at
  the GodotSharp packages that ship with the editor, so a build downloads nothing).
- Godot project: `E:\Unity\Godot\GameArtGeneration\medieval-kit` (MedievalKit, C#, Forward+, Jolt, d3d12; not a git
  repo). Everything under `res://kit/` is regenerated; `res://pilot/shots/` (with a `.gdignore`) holds the comparison
  renders.

## 1. Running it

```sh
# Blender (headless; it only adds its own scenes, nothing is saved): the pilot scene, its layout, the pieces it uses,
# their materials, then the reference renders (19 cameras, shadows off and on)
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- pilot          # ~40 s
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- pilot norender # ~15 s
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- all            # every piece + material, ~4.5 min
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- materials      # all 200 materials only, ~1 min
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- catalog Exterior   # or Interior: layout + renders
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- terrain        # the valley's ground + 8 cameras
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- world          # the 20 world-graph levels + renders
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- structures     # the 45 premade structures + renders, ~3.5 min
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- pieces SM_VKI_Overlay_Ash ...
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- classify       # every material's verdict
# add 'standard' to write the pilot's StandardMaterial3Ds instead of KitLit (the reference KitLit was checked against)

# Godot: import, check the pieces, build the layout scene, render its cameras, compare with Blender (~1 min; the
# first import of the whole kit ~7 min)
sh tools/gdx_round.sh Pilot
sh tools/gdx_round.sh Catalog_Exterior "" E:/Unity/Godot/GameArtGeneration/medieval-kit/catalog/exterior/shots 1920x1080
sh tools/gdx_round.sh Valley_Terrain "" E:/Unity/Godot/GameArtGeneration/medieval-kit/catalog/valley_terrain/shots 1600x1000
sh tools/gdx_levels.sh                 # the world levels: build (navmesh, walk test), structures, captures, travel test
# one structure or a few (Godot): ...console.exe --headless --path <project> --script res://addons/medieval_kit/Editor/kit_cli.gd -- structures Shack_Planks Shack_Stilts
```

`tools/gdx_round.sh` builds the C# (`dotnet build`), runs Godot's `--import` (with `KitImport`), then through
`kit_cli.gd`: `check` (`KitBuilder.CheckPieces`: bounds, surfaces, shadows), `build Pilot` (`KitBuilder.BuildLayout` ->
`res://kit/layouts/Pilot.tscn`), `capture` (`KitCapture`, needs a window; a 1600x900 SubViewport, MSAA 4x + TAA), and
`tools/gdx_compare.py` (mean / p95 difference per camera, sheets in `shots/compare/`, the chart's patches). `tools/gdx_crop.py` makes side-by-side crops for full-resolution checks.

## 2. What it writes

| Output | Contents |
|---|---|
| `kit/models/<VK\|VKI\|VKT>/<Family>/<piece>.glb` | one per master piece (a level's own meshes, such as the valley's `U_VKV_` chunks, in `models/Unique/`), at the origin, used slots only, triangulated (BEAUTY, as for FBX), COLOR_0 linear with `vki_rim` in its alpha, tangents, the master's custom properties as glTF extras (Godot: node meta `extras`) |
| `<piece>.glb.import` | no LODs (the kit's rule), surfaces not deduplicated, every glTF material name -> `res://kit/materials/<name>.tres`, post-import `KitImport.cs` |
| `kit/materials/<M_name>.tres` | the shared library: a ShaderMaterial on a KitLit or KitTerrain variant (section 3) |
| `kit/textures/*.png` (+ `.import`) | copied from the Unity package's `Art/Textures` (the `T_VKX_*` bakes included); VRAM compressed BC7, mipmaps, normal maps as normal maps; a terrain control map lossless without mipmaps |
| `kit/.vkx/` (Godot ignores it) | vkx's analysis and bakes of materials the Unity export has not seen yet, made with vkx's own functions (the Unity package is never written), and the .blend images the Unity export never wrote (the leaves' height maps) |
| `kit/data/pieces.json` | per piece: glb path, `surfaces` (library material per Godot surface), `slot_map` (Blender slot -> surface), Blender and Godot bounds, tris, props |
| `kit/data/materials.json` | per material: what it became (`kitlit` / `kitterrain`, or `standard` in the reference mode) and the approximations made |
| `kit/data/layouts/<name>.json` | placements (piece, basis, origin, material overrides by surface, Blender's Object Info random, the instance's properties, its collection), markers (empties: spawns, anchors, the level root), helpers, lights, cameras, world, view transform, render size |
| `kit/data/structures/<name>.json` | the same for each premade structure (origin on its own), with its Blender builder |
| `kit/data/world.json` | the world graph (docs/world_graph.json): levels, their links, targets and arrivals |
| `kit/world.tres`, `kit/layouts/<name>.tscn` (+ `<name>_nav.res`), `kit/structures/<name>.tscn` | built in Godot by `KitBuilder` (section 5c) |

- **Axes.** glTF is +Y up: Godot sees Blender (x, y, z) as (x, z, -y); Blender's front (-Y) is Godot's +Z (Godot's
  model front). Placements are `G M G^-1` (the object's own axes convert like its vertices); cameras and lights look
  down their local -Z in both programs, so theirs stay as they are (`G M`). `KitBuilder.CheckPieces` compares every
  imported AABB with Blender's bounds turned that way (1 mm).
- **Restyles** (`VAR_` / `VARI_`): the master's glb plus `surface_material_override/N` on the instance
  (`slot_map` gives N); the builder marks those instances editable so the override is saved.
- **Repeated materials:** a material in two slots goes out once per slot as `<name>__s<slot>` and maps back to the one
  `.tres`, so surfaces stay 1:1 with the Blender slots a restyle may change.

## 3. Materials

Every kit material is a **KitLit** ShaderMaterial (the projected ones **KitTerrain**), as in Unity: the see-through and
the shroud will clip every one. The reduction is vkx's analysis (UNITY_EXPORT section 3). The pilot first wrote it as
StandardMaterial3Ds -- the table below, still written with `standard` -- and KitLit reproduces those exactly (the
pilot's 38 shots: mean difference 0.000, at most 2 levels):

| Blender | Godot |
|---|---|
| base map x colour x vertex colour | `albedo_texture` x `albedo_color` (sRGB-encoded) x COLOR (`vertex_color_use_as_albedo`, `vertex_color_is_srgb = false`) |
| roughness map x scale | `roughness_texture` (red) x `roughness` |
| Normal Map strength | `normal_scale` (Godot mixes towards the mapped normal like Blender) |
| Specular IOR Level `l` (F0 = 0.08 l) | `metallic_specular = sqrt(l / 2)` (Godot's F0 = 0.16 s^2) |
| Principled diffuse | `diffuse_mode = Lambert` (Godot's default Burley is darker at grazing angles) |
| emission map x colour x strength | `emission_texture`, `emission`, `emission_energy_multiplier`, **`emission_operator = Multiply`** (Godot's default adds colour and map) |
| `alpha > t` cut-out | `ALPHA_SCISSOR`, threshold t |
| dithered texture alpha | `ALPHA_HASH` (none left in the kit after the no-shadow rule) |
| blended / constant alpha | `ALPHA` |
| Is Shadow Ray -> Transparent | the transparent pass: opaque ones `ALPHA` at alpha 1 with `depth_draw_mode = Always`; dithered ones blended |
| Translucent BSDF share t | `albedo x (1 - t)` and `backlight = t / (1 - t)` (Godot's own back-lighting term) |
| backface culling (vkx's rule) | `cull_mode` Back / Disabled |

**KitLit** (`Shaders/kit_lit.gdshaderinc`; a variant per draw mode, `KitLit[TwoSided][Jitter][Clip|Hash|Blend|Glass].gdshader`:
cull, alpha scissor / hash / blend, and Glass = opaque in the transparent pass) does the table's work plus moss on top (world-up normal + height noise, gated by vertex alpha, maps mixed
before decoding), the `vki_rim` glow (emission from vertex alpha) and the roof jitter as `instance uniform float
object_random` (only in `KitLitJitter`, the six roof materials: Godot gives every instance of a material with an
instance uniform 16 slots of a 4,096-instance buffer, and the valley's 5,370 pieces ran out), which `KitBuilder` sets
per placement to Blender's own value: `blender_object_random(name)`
reproduces EEVEE's `BLI_hash_int_2d(BLI_hash_string(name), 0)` (checked: 4 decimals, the rest is EEVEE's half floats).
And the leaves' and herbs' **bump**: their Blender normal is a Bump node on a height map (`T_*_H`, strength 0.25-0.35,
distance 0.02) over the geometric normal flipped on back faces (Godot's own flip for two-sided materials); KitLit's
`use_bump` does the same screen-space bump as KitTerrain. Unity keeps their cards flat.

**Leaves, a look call (Daniel, 2026-10-24: C).** Blender's EEVEE renders the crowns dark: the leaf material scales its
Translucent BSDF's normal by -1, and EEVEE then darkens the leaves below what a black translucent share gives (one oak
rendered one node change at a time: as built 27, translucent share black 59, no translucency 77 -- mean green of the
leaf pixels; Cycles renders the same material at 53). Of the three looks -- A EEVEE, B the material as Cycles reads it
(a custom light() in KitLit, tried and dropped), C Godot's built-in backlight as Unity's port -- Daniel saw no
difference between B and C and called A the thing being fixed: C, the engine's standard. The catalogs' four tree and
bush shots are 4.5-16 / 255 off Blender by that choice.

**KitTerrain** (`Shaders/kit_terrain.gdshaderinc` + `kit_noise.gdshaderinc`, variants `KitTerrain[Stair|Paving|Curb|Water]`):
the Unity port line for line -- vk_terrain's recipes on Blender object coordinates (Godot's model (x, -z, y)), the
noise stand-ins of `KitNoise.hlsl`, the screen-space Bump. Images bind by name as Unity's `TerrainProp` does
(`T_VK_<Layer>_BC|H|R`, `GroundCtl`, `TerrainMacro`); the grass saturation is the Blender material's (0.8; the shader's
0.6 is MedievalSetting's pick for its maps). **Godot's image v runs from the top** (Blender's and Unity's from the
bottom): every texture sampled at Blender coordinates turns v (`kuv`), the clamped control map reads `1 - v`
(`ctl_uv`) -- without it the control map was read from the map's wrong end and tile tops came out rock with moss.

Shadows come from both faces (`KitImport`: `ShadowCastingSetting.DoubleSided`), as Blender casts them.

## 4. Light, view, world (KitBuilder)

- Colours are linear in Blender, sRGB-encoded in Godot's Color properties. Sun: Blender W/m2 / pi = Godot energy.
- Point / spot: `P / (4 pi^2)` with inverse-square falloff (`omni_attenuation` / `spot_attenuation` 2) and a range
  where it is down to ~1 % (`clamp(10 sqrt(E), 1.5, 60)`); measured in Godot (`tools/godot_probes/`: a floor under an
  omni reads albedo x E / d^2). **Spot cone:** Blender fades the cone's last `spot_blend` share with a smoothstep;
  Godot 4.7 fades by `1 - rim^(1/a)` for `spot_angle_attenuation` a -- measured, `a` above 1 softens the whole beam (the
  first build's a = 8.9 left the chapel's window shafts at 45 % in their middle), below 1 sharpens the edge -- so
  `a = ln(1 - blend/2) / ln(0.5)` (0.11 for the kit's 0.15) puts Godot's half-way where Blender's is.
- Area: Godot 4.7 has `AreaLight3D`. Blender's area light is a one-sided Lambertian emitter (on its axis P / pi W/sr,
  four times a point light of the same power); Godot's normalized area light of energy E shines on its axis as an omni
  of E with the same cosine fall-off (measured): `E = P / pi^2`, Blender's size (a disk or ellipse as its rectangle).
  Unity's builder makes them point lights. The kit's seven are the interiors' doorway aprons.
- World: a flat colour L lights a Lambert surface as albedo x L in both, so it is Godot's ambient colour (energy 1).
  Reflections come from a one-line flat **sky shader** in the world's colour: with a colour background Godot's
  `REFLECTION_SOURCE_BG` reflects nothing (the sludge's glossy film came out too warm).
- AgX: Godot's `TONE_MAPPER_AGX`, exposure `2^exposure`; Blender's "Medium High Contrast" = `tonemap_agx_contrast` 1.5
  (calibrated on a chart of emissive patches: greys within 1/255 but the brightest at 3; saturated primaries up to
  ~17/255 apart, since Godot's AgX is not Blender's matrices: the candle flames read a little yellower).
- Cameras: an orthographic one keeps Blender's sensor-fit axis (`ortho_scale` = the width of a landscape render); a
  perspective one locks the height, since vkx records the vertical field of view and Godot reads `fov` along the
  locked axis (the valley's cameras came out zoomed in with the width locked).
- Sun shadows: one orthogonal map over 60 m, the project's directional atlas at 8192 (`project.godot`), Blender's sun
  angle x 0.6. Godot's defaults (4 splits over 100 m, 4096, the full angle) lost the small stones' contact shadows and
  spread every penumbra wider.

## 5. The pilot (2026-10-24)

The interior kit's **Overlay** family (52 pieces) is the one family with every case: restyles (the debris stones take
the level's stone in slot 58), alpha-clip foliage (moss, overgrowth), a dithered web (WebFloor), glass that casts no
shadow (GlassShards: stained glass in an iron frame) and one-sided solids (the `M_VK_*` materials). Scene `GDX_Pilot`
(`gdx_build_pilot_scene`, built fresh in each run) adds the restyles (12), the KitLit and glass cases (two dormers for
the jitter, a mossy boulder, candles and lava for the rim, the timber window wall for glass inside a house piece, the
corner web), a calibration chart and a floor; 58 pieces, 51 materials, 88 textures; lit like the verification catalogs
(VK_Sun, VK_Fill, VKX_SliceWorld, AgX Medium High Contrast -0.2, no AO), 19 orthographic 50-degree cameras.

Result (`sh tools/gdx_round.sh`): 58 pieces 0 problems (bounds within 1 mm, every surface on its library material);
all 19 cameras **0.5-1.0 / 255 mean difference, p95 1-3** without shadows, **0.5-1.6, p95 1-6** with them; looked at in
full-resolution crops: window glass, stained glass, moss on the boulder, the moss overlays, web, sludge, lava, candles,
restyled stones, roof jitter (dormer 1 / dormer 0 brightness 1.038-1.046 in both).

**Open questions settled:**

- *Does the glTF importer turn vertex colour as albedo on by itself?* Partly, and unreliably: on a glb imported with
  its own materials, 2 of 3 surfaces got it (all three have COLOR_0). Irrelevant for the kit: every surface maps to a
  library `.tres`, which sets `vertex_color_use_as_albedo` from vkx's analysis. The glTF exporter writes COLOR_0
  linear (16-bit) and Godot keeps it as is, so `vertex_color_is_srgb = false`.
- *Shadow casting is per node; what does glass inside a house piece need?* Nothing per node: Godot never draws a surface
  of the transparent pass into shadow maps (unless it uses the depth pre-pass). The glass's material goes there
  (`ALPHA` at alpha 1, depth written), so the piece stays one mesh and the sun lights the room through the window
  (the `GDX_Cam_18_glass` shots show the lit window patch in both renders).

**Found on the way:**

- Blender's glTF exporter visits every scene of the file unless `use_active_scene=True`; one scene of the kit file
  crashes the depsgraph (access violation in `update_id_after_copy`). The export scene is also the window's scene while
  exporting (a background Blender keeps the file's window).
- `export_materials='PLACEHOLDER'` drops the material names too: materials go out as plain glTF materials without images.
- The glTF exporter computes no tangents for meshes with n-gons (it aborts): pieces are triangulated first.
- Godot 4.7's `array_mesh/deduplicate_surfaces` is on by default; the import turns it off.
- **Unity export bug (not fixed here):** a material whose Emission Color is a plain image keeps `emission: [0, 0, 0]`
  in materials.json, and KitBuilder multiplies the map by it, so `M_VK_Stained`, `M_VKI_Stained_In`,
  `M_VKI_Stained_Night` and `M_VKI_Leaded_In` render without their glow in Unity. Godot takes white for any material
  with an emission map (Blender's colour is the map there).

## 5b. Phase 1: the whole kit (2026-10-24, HANDOFF 147)

- **Export:** 1,396 pieces (`-- all`, 4 m 18 s, no failures), 200 materials (194 KitLit, 6 KitTerrain), 302 textures;
  Godot's first import 6 m 40 s, no warnings; `CheckPieces` 1,396 (1,427 with the valley chunks) 0 problems.
- **KitLit for every material:** the pilot with every material on KitLit against its StandardMaterial3D build: mean
  0.000 in all 38 shots (at most 2 levels); against Blender as before (worst mean 1.6, p95 6).
- **Catalogs** (`-- catalog`, vkx_build_catalog's layouts: 544 exterior pieces in 52 shots, 852 interior in 26, at
  1920x1080, lit like the pilot): interior all under 2.5 / 255 mean; exterior 48 of 52 under 2.5 (median 1.1), the four
  others the tree and bush shots (the look call above).
- **KitTerrain on a real map** (`-- terrain`: the valley's 31 ground chunks seen by copies of the Unity verification's
  eight cameras, lit like the catalogs): 2.5-3.4 mean in six shots (Unity's valley check was 10-16 with shadows and
  trees in), 5.2 and 9.9 where the river fills the view -- the water's noise is a stand-in for Blender's (scale and
  distribution, not the pattern), as in Unity.

**Found on the way (phase 1):**

- The capture saved one camera's view for a whole shadow pass once: a hidden or minimized Godot window keeps
  processing but stops drawing. `KitCapture` now counts frames drawn (`Engine.GetFramesDrawn`) and warns.
- In a background Blender, objects of a scene that is not on screen keep a stale `matrix_world` until that scene's view
  layer is updated (HANDOFF's gotcha, met again with the valley's cameras).
- The Bash tool joins a backslash-continued line in a heredoc into one: write edit scripts to files (memory note).

## 5c. Phase 2: the levels (2026-10-24, HANDOFF 148)

- **Runtime** (`Runtime/`, the Unity package's counterparts): `KitPiece` (every imported piece's root: Blender
  properties, Blender slot per surface), `KitLink` (an Area3D: id, kind, target, arrival, prompt, facing), `KitSpawn` /
  `KitMarker`, `KitLevel`, `KitWorld` (+ levels, links; the arrival rule), `KitTravel` (+ `KitTravelHost`: the fade,
  threaded preloads, held levels for instant cuts, "@return" doors), `KitDecks`, `KitNavMesh` (a NavigationRegion3D
  that sets its map's cell size), `KitEncounter`, `KitPortalMarker`, `KitStructure`; `Runtime/World/`: the
  see-through (`KitSeeThrough` + `SetUpLevel`, `KitSeeThroughProbe`, the real caps `KitSeeThroughCaps` with their bank
  `KitSeeThroughCapBank` -> `res://kit/see_through_caps.res`, baked by `kit_cli -- bakecaps`, in `tools/gdx_round.sh`),
  `KitMapFrame`, phase 3a's systems: `Fire` / `FireFx` / `FireFlicker` / `KitFires` (GPU particles on the addon's `FX/`
  flipbooks; a level lights its kit fires as it stands), `Interactable` + `UseVia` (click-to-use), `Missile`,
  `CreatureSilhouettes` (+ `Shaders/CreatureSilhouetteMark/Fill`: stencil overlays), `KitWalkways`, `KitGround`;
  `KitNodes` (FindChildren / GetChildren without leaving Godot arrays to the finalizer). How to use all of it, for a
  game: the addon's [MANUAL.md](../godot/addons/medieval_kit/MANUAL.md). The z-fight watch is not part of the Godot
  addon (Daniel, 2026-10-27). `Walker/`: `KitCamera` (+ `KitPointer`),
  `KitClickToMove` + `KitWalker` (click / hold to walk on the navmesh, doors by clicking them), `KitTestWalker` (WASD),
  the demo (`KitDemo`, `KitDemoView`, `kit_demo.tscn`: the project's main scene), `KitPlayBoot` (Project > Tools >
  Play From Start Level / Walk This Level: KitWalker where the level has a navmesh, else KitTestWalker).
- **Import** (`KitImport`): the piece's colliders -- `vki_collider` boxes on a StaticBody3D, layer 1 (`KitPiece.Solid`),
  or 2 (`Passable`) for doors that open and breakables; the open quarters of cave / stream tiles; the mesh itself on
  ground pieces. **Godot reimports a .glb only when its md5 file is gone and its .import is touched** (a changed import
  script alone is not noticed).
- **Build** (`KitBuilder`): world graph -> `res://kit/world.tres`; each level with its pieces, links (trigger boxes),
  markers, lights, cameras, world; bridge decks cut into the ground tiles' colliders (4 levels); for a world level a
  navmesh (Recast from layer 1, 0.05 m cells indoors, 0.1 outdoors, the kit's walker r 0.3 / h 1.8 / step 0.35 / 40
  degrees; saved as `<level>_nav.res`) and the walk test (`KitWalkTest`: the navmesh's polygons joined by shared edges;
  every spawn, link and encounter point must lie on the start spawn's island within 1.5 m): **all 20 levels pass**.
  Structures (`-- structures` in Blender, `kit_cli structures`): 45 scenes in `res://kit/structures/` and the
  `Structures_Showcase` layout with a camera on each.
- **Travel test** (`kit_cli travel`, headless): every link of every level taken through `KitTravel` (a "@return" door
  after a way in): **40 links, 0 problems**, one `@deep`; on arrival Godot's own pathfinding from the arrival spawn to
  every spawn and link (the map needs a few physics frames before it answers: regions sync asynchronously); preload at
  the valley: its 5 neighbours held, a cut there and back instant both ways. (Loads still in flight when the test quits
  print parse errors; harmless.)
- **Captures** (`sh tools/gdx_levels.sh`: each level's Blender cameras at the level's own size and shadows): interiors
  and dungeons **1.9-5.7 / 255** mean (the chapel the highest: window shafts and the doorway area light), the valley
  **5.6-7.8** with one camera at 16.5 (an oak crown in front: the leaves' look C, and the river's noise stand-in).
- Not yet: chains and their streamer (phase 4), the see-through (phase 6: a walker under a roof is hidden).

## 6. What converts cleanly, what needs shaders (all 200 materials of materials.json)

| | Materials |
|---|---|
| **160 plain** KitLit (what a StandardMaterial3D would do) | every other `M_VK_*` / `M_VKI_*` |
| **13 transparent pass** (no shadow) | glass `M_VKI_Daylight`, `Leaded_In`, `Stained_In`, `Stained_Night`, `Window_Day`, `Window_Night` (KitLit Glass); `M_VKI_FX_Light`, `Puddle`, `SewerWater`, `Sludge`, `StreamWater`, `WaterFall`, `Web` (KitLit Blend) |
| **3 cut-outs** | `M_VK_Foliage`, `M_VK_Crops` (translucent: backlight), `M_VK_Net` |
| **8 translucent leaf / herb cards** | `M_VK_Leaves`, `Cotton`, `Fireweed`, `GoblinHerb`, `HerbsCh2`, `HerbsCh3`, `WildGarlic`, `Yarrow`: backlight (look C) and, where the .blend still has them, the height-map bump |
| **10 KitLit specials** | jitter: `M_VK_RoofRed`, `Roof_Blue`, `Roof_Green`, `Roof_Shingle`, `Roof_Slate`, `Roof_Thatch`; rim: `M_VKI_GlowIn`, `M_VKI_Lava`; moss: `M_VK_BarkMossy`, `M_VK_RockMossy` |
| **6 KitTerrain** | `M_VK_Terrain`, `M_VK_TerrainTown` (terrain), `M_VKT_Stair`, `M_VKT_Paving`, `M_VKT_Curb`, `M_VKT_Water` |

Still to port in KitLit (phases 5-6): the see-through and its caps, the shroud. Point, spot and area lights: section 4. Five materials are in materials.json but no longer in the .blend (`M_VK_HerbsCh2/Ch3`, three
`M_VK_Shutter_*Worn`): written from the analysis, without the bump.

## 7. Plan for the rest

Superseded by [FULL_PORT_PLAN.md](FULL_PORT_PLAN.md) (2026-10-24: everything the Unity kit has, in C#, and the Unity
kit completed from the game first); the notes below remain the art side of it.

0. **The rest of the kit:** done (section 5b; FULL_PORT_PLAN phase 1); the levels (5c, phase 2).
1. **Weapons and items.** Weapons (GameArtGeneration/Weapons, parametric Blender kit with its own atlases and rune glow
   maps) and Items (icon-only and ground-drop models, which already use the kit's materials by name): a small exporter
   in each repo that reuses `gdx_export`'s glb writer, `_Tres` and material rules; grip / mouthpiece sockets as glTF
   nodes; the enchanted copies' violet light as a node. Icons: keep the PNGs rendered in Unity or render them with a
   Godot capture like `KitCapture`.
2. **Creatures** (Beasts, Insectoids, the dragon and hydra, warg, ooze): skinned glbs with their Blender-authored
   clips as glTF animations (Godot: Skeleton3D + AnimationLibrary), root motion from the Motion bone
   (`AnimationMixer.root_motion_track`); coats are painted textures (StandardMaterial3D). Shaders to port: whatever
   each Unity setup adds (ooze, the slime trail, fire breath, the undead's torn cloth). Mind Blender 4.4's action slots.
3. **Humanoids** (Humans, orcs, undead, goblins, dwarves): face and body keys as glTF morph targets; Unity's
   `Humans/Skin|Eye|Hair|Cloth` shaders (region / cover masks, CapCut, ombre and streak ids in the Clump UV) and the
   HumanFace generator need Godot ports; Humanoid retargeting is Godot's BoneMap + SkeletonProfileHumanoid. The bought
   Asset Store clips (Kevin Iglesias) are licensed for Unity: check before using them in Godot; the own clips go as is.
4. **Level layouts.** `gdx_export_layout` already writes placements, restyles, lights, cameras and the world; add the
   world graph's 20 levels and the 45 structures (twins of `vkx_export_world` / `vkx_export_structures`), markers
   (`SPN_`, `LGT_`, `FXA_`) as Marker3D with metadata, links as Area3D, `vki_collider` boxes as StaticBody3D, the
   valley's world probe as a sky. The Unity-side generators (houses, rooms, caves, dungeons, villages) are C#: port
   them to GDScript from `house_rules.json` / `interior_rules.json`, or bake their output in Blender -- a decision for
   then. Instanced glb scenes are fine for the pilot; big levels may want the meshes saved as resources
   (MeshInstance3D + mesh, or a MeshLibrary for GridMap building).
5. **Terrain.** Port KitTerrain (terrain / stair / paving / curb / river water, the noise stand-ins of `KitNoise.hlsl`),
   KitSea and KitGrass to Godot shaders; terrain tiles' `TCol` vertex colour and uncompressed control maps; the
   dual-grid tiles and terrain tiers on a GridMap or as baked chunks.
