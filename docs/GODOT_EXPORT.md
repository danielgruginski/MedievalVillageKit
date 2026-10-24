# Godot export

The kit goes to Godot 4.7 straight from Blender (Blender -> glTF -> Godot, no Unity in between), beside the Unity
export, which it reuses and leaves untouched. Pilot done 2026-10-24 (HANDOFF 143), the C# set-up the same day (HANDOFF 145); the rest: FULL_PORT_PLAN.md.

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
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- pieces SM_VKI_Overlay_Ash ...
blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- classify       # every material's verdict

# Godot: import, check the pieces, build the layout scene, render its cameras, compare with Blender (~1 min)
sh tools/gdx_round.sh Pilot
```

`tools/gdx_round.sh` builds the C# (`dotnet build`), runs Godot's `--import` (with `KitImport`), then through
`kit_cli.gd`: `check` (`KitBuilder.CheckPieces`: bounds, surfaces, shadows), `build Pilot` (`KitBuilder.BuildLayout` ->
`res://kit/layouts/Pilot.tscn`), `capture` (`KitCapture`, needs a window; a 1600x900 SubViewport, MSAA 4x + TAA), and
`tools/gdx_compare.py` (mean / p95 difference per camera, sheets in `shots/compare/`, the chart's patches). `tools/gdx_crop.py` makes side-by-side crops for full-resolution checks.

## 2. What it writes

| Output | Contents |
|---|---|
| `kit/models/<VK\|VKI\|VKT>/<Family>/<piece>.glb` | one per master piece, at the origin, used slots only, triangulated (BEAUTY, as for FBX), COLOR_0 linear with `vki_rim` in its alpha, tangents, the master's custom properties as glTF extras (Godot: node meta `extras`) |
| `<piece>.glb.import` | no LODs (the kit's rule), surfaces not deduplicated, every glTF material name -> `res://kit/materials/<name>.tres`, post-import `kit/tools/kit_import.gd` |
| `kit/materials/<M_name>.tres` | the shared library: StandardMaterial3D, or ShaderMaterial on KitLit (section 3) |
| `kit/textures/*.png` (+ `.import`) | copied from the Unity package's `Art/Textures` (the `T_VKX_*` bakes included); VRAM compressed BC7, mipmaps, normal maps as normal maps |
| `kit/data/pieces.json` | per piece: glb path, `surfaces` (library material per Godot surface), `slot_map` (Blender slot -> surface), Blender and Godot bounds, tris, props |
| `kit/data/materials.json` | per material: what it became (`standard` / `kitlit` / `skip`) and the approximations made |
| `kit/data/layouts/<name>.json` | placements (piece, basis, origin, material overrides by surface, Blender's Object Info random), helpers, lights, cameras, world, view transform |

- **Axes.** glTF is +Y up: Godot sees Blender (x, y, z) as (x, z, -y); Blender's front (-Y) is Godot's +Z (Godot's
  model front). Placements are `G M G^-1` (the object's own axes convert like its vertices); cameras and lights look
  down their local -Z in both programs, so theirs stay as they are (`G M`). `KitBuilder.CheckPieces` compares every
  imported AABB with Blender's bounds turned that way (1 mm).
- **Restyles** (`VAR_` / `VARI_`): the master's glb plus `surface_material_override/N` on the instance
  (`slot_map` gives N); the builder marks those instances editable so the override is saved.
- **Repeated materials:** a material in two slots goes out once per slot as `<name>__s<slot>` and maps back to the one
  `.tres`, so surfaces stay 1:1 with the Blender slots a restyle may change.

## 3. Materials

Most kit materials are a plain **StandardMaterial3D** from vkx's analysis (UNITY_EXPORT section 3):

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

**KitLit** (`Shaders/kit_lit.gdshaderinc`; `KitLit.gdshader` one-sided, `KitLitTwoSided.gdshader` with
`KIT_TWO_SIDED`): the same reduction plus moss on top (world-up normal + height noise, gated by vertex alpha, maps mixed
before decoding), the `vki_rim` glow (emission from vertex alpha) and the roof jitter as `instance uniform float
object_random`, which `KitBuilder` sets per placement to Blender's own value: `blender_object_random(name)`
reproduces EEVEE's `BLI_hash_int_2d(BLI_hash_string(name), 0)` (checked: 4 decimals, the rest is EEVEE's half floats).

Shadows come from both faces (`KitImport`: `ShadowCastingSetting.DoubleSided`), as Blender casts them.

## 4. Light, view, world (KitBuilder)

- Colours are linear in Blender, sRGB-encoded in Godot's Color properties. Sun: Blender W/m2 / pi = Godot energy.
  Point / spot: `P / (4 pi^2)` (as for URP; not checked yet, the pilot has suns only).
- World: a flat colour L lights a Lambert surface as albedo x L in both, so it is Godot's ambient colour (energy 1).
  Reflections come from a one-line flat **sky shader** in the world's colour: with a colour background Godot's
  `REFLECTION_SOURCE_BG` reflects nothing (the sludge's glossy film came out too warm).
- AgX: Godot's `TONE_MAPPER_AGX`, exposure `2^exposure`; Blender's "Medium High Contrast" = `tonemap_agx_contrast` 1.5
  (calibrated on a chart of emissive patches: greys within 1/255 but the brightest at 3; saturated primaries up to
  ~17/255 apart, since Godot's AgX is not Blender's matrices: the candle flames read a little yellower).
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

## 6. What converts cleanly, what needs shaders (all 200 materials of materials.json)

| | Materials |
|---|---|
| **160 clean** StandardMaterial3D | every other `M_VK_*` / `M_VKI_*` |
| **13 transparent pass** (no shadow), StandardMaterial3D | glass `M_VKI_Daylight`, `Leaded_In`, `Stained_In`, `Stained_Night`, `Window_Day`, `Window_Night`; `M_VKI_FX_Light`, `Puddle`, `SewerWater`, `Sludge`, `StreamWater`, `WaterFall`, `Web` (blended) |
| **3 cut-outs** | `M_VK_Foliage`, `M_VK_Crops` (translucent: backlight), `M_VK_Net` |
| **8 translucent leaf / herb cards** | `M_VK_Leaves`, `Cotton`, `Fireweed`, `GoblinHerb`, `HerbsCh2`, `HerbsCh3`, `WildGarlic`, `Yarrow`: backlight works; their normal is a Geometry-based Bump that Unity never ported either -- decide on trees whether it needs a shader |
| **10 KitLit** | jitter: `M_VK_RoofRed`, `Roof_Blue`, `Roof_Green`, `Roof_Shingle`, `Roof_Slate`, `Roof_Thatch`; rim: `M_VKI_GlowIn`, `M_VKI_Lava`; moss: `M_VK_BarkMossy`, `M_VK_RockMossy` |
| **6 need a KitTerrain port** (left out) | `M_VK_Terrain`, `M_VK_TerrainTown` (terrain), `M_VKT_Stair`, `M_VKT_Paving`, `M_VKT_Curb`, `M_VKT_Water` |

Not ported (game features of the Unity KitLit, not the kit's look): the see-through and its caps, the shroud.
Checked in the pilot: 51 of the 200, at least one of every kind above except the leaf cards (foliage was seen only as
flat overlays, never lit from behind) and the projected ones; not checked: point / spot lights. Five materials are in
materials.json but no longer in the .blend (`M_VK_HerbsCh2/Ch3`, three `M_VK_Shutter_*Worn`).

## 7. Plan for the rest

Superseded by [FULL_PORT_PLAN.md](FULL_PORT_PLAN.md) (2026-10-24: everything the Unity kit has, in C#, and the Unity
kit completed from the game first); the notes below remain the art side of it.

0. **The rest of the kit** (before the other repos; ~5 min of export): every master of `VKX_PIECE_COLLECTIONS`
   (1,399 pieces) and the 194 non-projected materials; a verification catalog per kit the way the pilot was checked
   (generalise `gdx_build_pilot_scene` to `vkx_build_catalog`'s families). Trees first among the risks: translucency
   from behind, the leaf normals (section 6), 3.9 M tris of pines in the valley; then point / spot lights.
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
