# Interior kit (VKI): parallel work packages

Stage (b) and (c) of the build plan in [INTERIOR_SPEC.md](INTERIOR_SPEC.md) §8. Read the spec first, **including §10
(amendments after the core stage)**, which overrides earlier sections where they differ.

Project root: `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit`. Code: `src/interior/`. Renders: `renders/interior/`.

## Rules for every package

**Ownership**
- You own only your texts (below) and your workshop scene `WS_vki_<agent>` (made by `vki_ws(agent)`).
- Read-only for you: `vki_core`, `vki_test`, `vki_tex`, `vki_textiles`, `vki_fam_timber`, `vki_floors`, every other package's
  text, every `M_VKI_*` / `T_VKI_*` material and image, `W_VKI_*`, `VKI_Key`, `VKI_Fill`, `VKI_Pieces`, and the scenes
  `VKI_Test`, `VKI_LookTest`, `VKI_Catalog` (the scene the user looks at: never change, delete or re-render into it).
- If core code is wrong for you, work around it in your own text and report it under "core requests". Do not edit core.

**Blender (one live instance shared by 6 engineers)**
- Drive it only with `mcp__blender__execute_blender_code` (load with ToolSearch `select:mcp__blender__execute_blender_code`).
  Every call is a fresh namespace: `g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"]()`.
- Keep each call under ~20 s (at most ~6 pieces built per call). Never change the window's active scene.
- **Never save the .blend.** No `bpy.ops` except rendering. Never `raise SystemExit`.
- Never call `vki_rebuild`, `vki_adopt`, `vki_apply_mats`, `full_rebuild`, `apply_pbr_all` or any texture generator.
  Build your masters with `vki_ws_build(agent, names)`: they go into `WS_vki_<agent>_Pieces`. The coordinator adopts them
  into `VKI_Pieces` when you hand in.
- Material slots 0–66 and the whitelisted per-master overrides only (§4.1). Piece names from your list only (§3, §5 names,
  prefix `SM_VKI_`). Every top-level name in your text starts with `vki_` / `VKI_` (T18).

**Code**
- Edit `src/interior/<text>.py`, then push:
  `exec(open(r"E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\tools\kit_sync.py",encoding="utf8").read()); push("<text>")`.
- **Before every push, compile the file outside Blender** so a syntax error never reaches the shared Blender (everyone's
  `vki_ns()` executes every package text):
  `"C:\Users\danie\Documents\ComfyUI\.venv\Scripts\python.exe" -c "import sys; compile(open(sys.argv[1],encoding='utf8').read(), sys.argv[1], 'exec')" <file>`.
  Use that same Python (with PIL) for crops and montages; the plain `python` command on this machine is a sandboxed app.
- Register builders at the end of your text: `vki_register([(name, fn, {"grime": ...}, "<agent>"), ...])`.
- Keep the file and the Blender text identical when you finish.

**Quality**
- Style: the exterior kit's hand-painted World-of-Warcraft look (`docs/images/tavern.jpg`, `blacksmith.jpg`), chunky,
  slightly irregular, warm, readable from the §1 game camera (pitch 50°, lens 38, D 14–22). Tops of things get the detail
  budget: the camera looks down on them.
- `vki_test_pieces(names)` must return `{}`. It includes the within-piece coplanar-overlap check (z-fighting): same-facing
  faces in one plane must not overlap. Separate members by ≥ 5 mm or trim them. Wall end planes are removed by `finish`.
- Render with `vki_ws_shot(agent, name, mode="game"|"plan"|"free", ...)`. Read every PNG and inspect crops at full
  resolution (junctions, piece ends, openings, tops). For structure families, assemble a small test room in your workshop
  scene (all your kinds, Full and Cut, posts at every junction) and render it in the game camera, Day and Night.
- The user's weekly usage limit was hit once: work efficiently. Focused renders (1280x720 unless full-res inspection needs
  more; prefer crops), batch small operations, no redundant work. Finish the priority list well before extras.

**Hand-in (your final message)**, as markdown with these headings:
`Texts` · `Pieces` (name, tris, one-line note) · `Tests` (exact results) · `Renders` (absolute paths worth showing) ·
`API notes` (what the assembler and the coordinator need) · `Deviations` (from the spec, with reasons) ·
`Core requests` · `Unfinished`.

## Packages

| Agent | Texts | Pieces (spec sections) | Specific checks |
|---|---|---|---|
| `stone` | `vki_fam_stone`, `vki_fam_board` | Stone family, 21 masters (§2.2, §3.1, §3.2: Plain_150A F/C, Plain_150B F with pop-outs keyed to `T_VKI_StoneIn_stones.json`, Plain_300 F/C, Window_150 F/C round head, Door_150 F/C round arch, DoorWide_300 F/C segmental, Rake_150_L/R, Hearth_300 F/C, Forge_300 F/C, Post_Stone_Corner F/C, Post_Stone_Mid F/C). Board family, 10 (Plain_150A F/C, Plain_300 F/C, Door_150 F/C, Post_Board_Corner F/C, Post_Board_Mid F/C). `Leaf_Wide_Cut_L/R` (§3.3). | T4 rigs: Stone L/T/X/free end, Timber↔Stone family step, Board (P) tee into Stone and into Timber (O). Pop-outs match the painted stones in an ortho close-up. Forge and hearth glow: T17 on a rig render, fire reads orange not white. Limewashed stone (`wall_a` Plaster style on Stone). |
| `wattle` | `vki_fam_wattle`, `vki_fam_ashlar` | Wattle family, 15 (Plain_150A F/C, Plain_150B F INFILL patch, Plain_300 F/C, Window_150 F/C unglazed with prop-open shutter and daylight card, Door_150 F/C crooked lintel, Rake_150_L/R, Post_Wattle_Corner F/C, Post_Wattle_Mid F/C). Ashlar family, 12 (Plain_150A F/C, Plain_300 F/C, Lancet_150 F/C, LancetTall_150 F, DoorWide_300 F/C pointed, Post_Ashlar_Corner F/C, Post_Ashlar_Mid F). | Sag and bow stay inside the envelope (T3, T13). Soot band on wattle. A triple-lancet north wall (Lancet, LancetTall, LancetTall, Lancet) reads in the game camera with the glass unclipped (T17); Ashlar H = 4.5 needs the §1 h_fit 3.97 camera. |
| `links` | `vki_links`, `vki_props_chapel` | `Stair_Up_150x450_RailR`, `Stair_Down_150x450_RailR`, `Floor_Dais_300`, `FX_WindowPool`, `Runner_300`, `Runner_150` (§3.3, §5.4). Chapel P1 (§5.4): `Pew_300`, `Altar_300`, `AltarRail_150`, `CandleStand_Pricket`, `Lectern`, `Font`, `VotiveRack`. No FX_DoorSpill (the exit leaf is closed, §10). | Up/down pair at the same origin; the down flight's risers visible from the game camera; no stair vertex inside a wall or post envelope; triggers and spawns separated (≥ 0.2 m). Runners chain seamlessly (u-periodic cell). Pews read as pews from above. |
| `home` | `vki_props_home` | §5.1 P1: Table_Trestle_300, Table_Trestle_150, Table_Small, Form_300, Form_150, Chest, Dresser, Shelf_Wall_150, Pantry_Shelves_300, Barrel, Barrel_Water, Crate, Jars_Cluster, LogBasket, Bed_Straw, Bed_Box, Bed_HalfTester, Hearth_Open, Oven_150, Worktable_150, Desk_Merchant, TableDress_Meal_A, TableDress_Meal_B. Then P2 if time allows. | Footprints equal `vki_fp_cells`; backs on the proud line (gap ≤ 0.005) when placed with `vki_place`; table dressing snaps at 0.80; beds read from above; small food from the goods atlas (`goods_map`), never flat colours. |
| `tavern` | `vki_props_tavern`, `vki_props_smithy` | §5.2 P1: Bar_Counter_150, Bar_End_150, CaskRack_150, Table_Barrel, TableDress_Tavern_A/B/C, Lantern_Wall, Candle_Plate, Candlestick. §5.3 P1: Workbench_300, QuenchTrough_150, CoalBin_150, IronStock_150, ToolWall_150, GoodsRack_150, Workbench_Carpenter, PoleLathe. | Bar tops continuous at 1.5 m; flap `hinge_axis` correct; tankard foam readable at D 20; every light-giving prop has `vki_lights`; coal reads as coal (bevelled flat-shaded lumps). |
| `rooms` | `vki_rooms` | The assembler (§6, §7): `VKI_PLANS`, `VKI_ROOMS`, parser, `vki_build_scene(name)`, `vki_build_all()`, `vki_check` (T12 room rules, incl. the free-end post **error**), T19 visibility, lights and FX empties from sockets, spawns, links, `VKI_Root`, fit camera (§1 + 0.4 m far margin), Day/Night presets. Builds the 9 scenes of §6. | See below. |

## The assembler (`rooms`) works in parallel with the packages

Most pieces don't exist yet when it starts. The placer uses the real master when `bpy.data.objects` has it (in
`VKI_Pieces` or in any `WS_vki_*_Pieces`), and otherwise a **placeholder**: a box named `PH_<piece>` with the footprint and
height the spec gives (§3, §5), a flat grey material outside the kit slots, `vki_placeholder=1`, and the same metadata
contract (mount, footprint, use points, sockets, triggers) so layout checks, BFS and camera tests work before the packages
land. Walls of a missing family get placeholders of the right thickness, height and length. `vki_check` reports placeholder
counts per scene. When the coordinator has adopted every package, the assembler is asked to rebuild all scenes with the
real pieces, fix what breaks, and render.
