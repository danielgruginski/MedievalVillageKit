# Survey C: reusable indoor props and the exteriors the interiors must match

Everything below comes from reading the code in `src/core/vk_helpers.py` and `src/modules/*.py`, plus the three gallery renders. Sizes are from `docs/PIECES.md` (generated 2026-09-23). I made no Blender calls and edited no files, so the "close camera" verdicts are judged from the code (segment counts, bevels, what is baked in), not from interior renders.

## 0. Findings that affect the interior kit

1. **The exterior wall pieces cannot be reused from inside.**
   - Window glass is one quad that faces −Y only. It sits at y −0.02 (stone), 0.0 (plaster), −0.12 (timber), −0.05 (log) and −0.33 (chapel stained glass).
   - Every door has a VOID quad or box on the inside:
     - `wall_stone_door`: quad at y +0.075.
     - Wattle door: box to y +0.6.
     - Byre door: to +0.8.
     - Log door: plank floor plus VOID to +0.5.
     - `wall_stall`: to +1.2.
     - Shop walls (`twn_shop_inside`): VOID at +0.2, plus a shelf.
   - Frames, sills, shutters and the pop-out stones (`wall_rocks`) exist only on the −Y face. The inner face is just the grid-cut material box.
   - So the interior kit needs its own door and window pieces.
2. **Wall-mounted props all assume "outer face toward −Y".** If interior walls put the room face toward −Y at y = −0.25, as the exterior walls do, these props mount without changes:
   - `SM_VK_Prop_WallFountain`, `SM_VK_Banner_Wall` and `window_frame()` expect the face at −0.25.
   - `SM_VK_Prop_ToolWall` has its board plane at y ≈ −0.04, so it expects the face at 0 and needs a −0.25 offset.
   - `SM_VK_Prop_Lantern` has its bracket back at y ≈ +0.1; place it at y −0.3 against a −0.25 face.
3. **Name collision on `SM_VK_Prop_Bellows`.** Both `smith_bellows` (vk_helpers:2014) and `ind_bellows` (vk_mod_industry:650) register it. The industry version is built later and wins (1.96 × 0.81 × 1.21), so `smith_bellows` is dead code.
4. **Exterior smithy bugs, likely but not yet checked in a render:**
   - `build_smithy` builds the house with `front="DW"`. The door is in bay 0 at smithy (−1.5, 0), and `SM_VK_Smithy_Chimney` (2.2 m wide, at x −2.85…−0.65, y −1.9…−0.2) stands right in front of it.
   - The back is `".."` and the end walls get W or `.`, so the forge house has no reachable door. The interior trigger needs a door moved to bay 1, or a trigger on the canopy.
   - `SM_VK_Prop_ToolWall` is placed at y −0.02, inside the 0.5 m stone wall (its face is at −0.25), so it is buried. It does not show in `blacksmith.jpg`.
   - The bellows are placed at rot 180, which turns the −X nozzle to +X, pointing away from the forge.
5. **Precedent for the 1.5 m seam rule.** `twn_flat_wobble` (vk_mod_town:13) already swaps in a module-specific wobble and builds with `finish(wobble=False)`. The x-wobble in `finish()` depends only on z, so it is seam-safe. Only the y term (period 3 m) breaks 1.5 m seams, by up to 0.035 × 2 × 0.62 ≈ 4.4 cm.
6. **Lights and fire.** All fire uses `GLOW` (M_VK_Glow, emissive) and lit windows use `M_VK_Window_Lit`, so both can be toggled. The smithy adds a point light `VK_Light_Forge` (450 W, colour (1.0, 0.45, 0.15), at 1.3 m). `M_VK_Stained` is textured (T_VK_Stained) with emission 0.5.

## 1. Indoor prop inventory

Verdicts:
- **OK**: usable as-is from a close top-down camera.
- **Tweak**: usable, but something is baked in or coarse.
- **Interior version**: needs a new variant.

### Furniture

| Piece | Builder | Size (m) | Verdict |
|---|---|---|---|
| `SM_VK_Prop_Table` | `prop_table` vk_helpers:1316 | 2.00 × 0.95 × 1.09 | Tweak. Trestle table, top at 0.83. It bakes in 3 tankards (WOOD + HAY foam) and a bread platter. Good for a tavern; homes need a plain top and 3 m (2-grid) long tables. |
| `SM_VK_Prop_Stool` | `prop_stool` :1327 | 0.48 × 0.50 × 0.55 | OK. 10-segment seat, 3 splayed legs. |
| `SM_VK_Prop_Bench` | `prop_bench` :1226 | 1.80 × 0.48 × 1.00 | Interior version. It is a garden bench with a backrest (seat 0.53), fine as a wall settle. Tables need backless forms. |
| `SM_VK_Prop_Bedroll` | `con_bedroll` vk_mod_construction:890 | 0.74 × 1.66 × 0.25 | OK as a straw pallet (hide, red blanket, pillow). Reads well from above. |
| `SM_VK_Prop_Planter` | `prop_planter` :2879 | 0.68 × 0.70 × 1.06 | OK (potted flowers). |

### Storage

| Piece | Builder | Size (m) | Verdict |
|---|---|---|---|
| `barrel()` helper | :1310 | r 0.4, h 1.0 | No standalone piece exists. Register `SM_VK_Prop_Barrel` (upright and lying); 12 segments, iron hoops. |
| `SM_VK_Prop_BarrelStack` | `prop_barrelstack` :1411 | 1.90 × 1.07 × 1.55 | OK: 3 lying barrels on wedged rails. Cellar, tavern. |
| `SM_VK_Prop_AleCask` | `ale_cask` :2098 | 1.25 × 1.76 × 1.43 | OK: great cask in cradles, brass tap to −Y, bucket; 20 segments. Behind the bar. |
| `SM_VK_Prop_Crates` | `prop_crates` :1232 | 2.50 × 1.76 × 1.50 | Tweak: a cluster of 4 crates and 2 barrels. A single crate and a chest are missing. |
| `SM_VK_Prop_Sacks` | `prop_sacks` :1396 | 1.12 × 1.02 × 1.27 | OK: 4 burlap sacks. |
| `SM_VK_Pile_Sacks_1/2/3` | `con_pile_sacks` :693 | 1.7 × 1.6 × 0.45 / 0.71 / 0.96 | OK: grain store, pantry. |
| `SM_VK_Pile_Planks_1/2/3` | `con_pile_planks` :632 | 2.9 × 1.95 × 0.34–0.96 | OK: carpenter stock. |
| `SM_VK_Pile_Logs_1/2/3` | `con_pile_logs` :615 | 2.94 × 1.46–1.85 × 0.56–1.48 | OK: wood store. |
| `SM_VK_Pile_Wool_*`, `SM_VK_Pile_Hides_*` | industry :1019 / :1005 | about 1–3.3 × 1.0–1.3 | OK: weaver or tanner store. The `ind_pelt` helper (:824) can make fur rugs. |
| `SM_VK_Pile_Coal_1/2/3` | `ind_pile_coal` :354 | 2.09 × 1.43 × 0.68 and up | OK: smithy coal bin. |
| `SM_VK_Pile_Fish_1/2/3` | `wat_pile_fish` :869 | 0.85–1.78 wide × 0.37–0.68 high | OK: kitchen. |
| `SM_VK_Prop_ShopGoods_{Bread,Produce,Cloth,Pots,Tools,Meat,Candles,Fish}` | `twn_goods_*` vk_mod_town:421–549 | about 1.9 × 0.5 × 0.3–0.85, origin at the counter top | OK: dressing for shelves, counters and tables. Candles is a tallow row with flames plus an iron candlestick. |

### Hearth, kitchen and pantry

| Piece | Builder | Size (m) | Verdict |
|---|---|---|---|
| `SM_VK_Prop_Campfire` | `con_campfire` :859 | 1.53 × 1.60 × 1.73 | OK as a hovel's central hearth: rock ring, embers, flames, tripod with a pot. |
| `SM_VK_Prop_Cauldron` | `ind_cauldron` :1186 | 1.75 × 1.72 × 2.12 | Tweak: the tripod legs spread to r 1.0 and it is 2.1 m tall. Fits under a hovel smoke vent. |
| `SM_VK_BreadOven` | `bread_oven` :3166 | 2.70 × 2.25 × 3.06 | Interior version. Clay dome on a stone base, mouth with glow, flue, firewood. The shelter roof on posts is outdoor-only; drop it. |
| `SM_VK_Prop_BreadRack` | `bread_rack` :3207 | 1.50 × 0.50 × 1.91 | OK: 3 shelves of goods-atlas bread. Pantry. |
| `SM_VK_Prop_DryingRack_Meat` | :1206 | 2.70 × 1.19 × 2.21 | OK: hams, sausages, strips. Pantry or smoke corner. |
| `SM_VK_Prop_DryingRack_Herbs` | :1227 | 1.68 × 0.88 × 1.93 | OK: tray shelves. |
| `SM_VK_Prop_HerbBundles` | :1171 | 2.50 × 0.86 × 2.10 | Tweak: posts on stone pads. Indoors, hang the bundles from a beam instead. |
| `SM_VK_Prop_Trough` | `prop_trough` :1331 | 2.02 × 0.90 × 0.73 | OK: wooden water trough; doubles as a byre trough or quench trough. |
| `SM_VK_Prop_CiderPress`, `SM_VK_Prop_MashTun` | :1112 / :1094 | 2.24 × 1.60 × 2.27 / 3.09 × 2.70 × 2.03 | OK for a cellar or brew room. |
| `SM_VK_Prop_WallFountain` | `wat_wall_fountain` :910 | 1.80 × 1.09 × 2.08 | OK as a lavabo or basin. Wall-mounted (face −0.25) with a floor slab. |

### Smithy and workshops

| Piece | Builder | Size (m) | Verdict |
|---|---|---|---|
| `SM_VK_Prop_Anvil` | `prop_anvil` :1384 | 0.91 × 0.72 × 1.06 | OK: stump, steel anvil with a horn, hammer. Blocky but reads well in `blacksmith.jpg`. |
| `SM_VK_Prop_Grindstone` | :1390 | 0.95 × 0.84 × 1.32 | OK. |
| `SM_VK_Prop_Bellows` | `ind_bellows` :650 | 1.96 × 0.81 × 1.21 | OK: pleated hide, nozzle to −X, lever post. |
| `SM_VK_Prop_QuenchTub` | `smith_quench` :2027 | 0.86 × 0.86 × 0.96 | OK (round tub with tongs). A stone quench trough is missing; `Prop_Trough` can stand in. |
| `SM_VK_Prop_ToolWall` | `smith_toolwall` :2032 | 1.80 × 0.14 × 1.00 (board z 1.1–2.1) | OK: 5 tools and 2 rings. Only visible on full-height walls; note the offset in §0. |
| `SM_VK_Prop_WeaponRack` | :1401 | 1.52 × 0.64 × 2.08 | OK: spears, swords, round shield. |
| `SM_VK_Prop_ArmorStand` | `def_armor_stand` vk_mod_defence:1014 | 1.64 × 0.94 × 2.36 | OK: helm, breastplate, tabard, shield and spear. |
| `SM_VK_Prop_CoalPile` | `coal_pile` :2043 | 1.31 × 0.99 × 0.57 | Tweak: subdivision-1 icosphere lumps look like low-poly rocks up close. |
| `SM_VK_Prop_Forge` | `prop_bellows_forge` :1421 | 2.47 × 1.20 × 2.80 | Usable indoors as-is: stone hearth 1.6 × 1.2 × 0.9 with a glowing bed, back flue to 2.8, hood slab, small cloth bellows. |
| `SM_VK_Smithy_Chimney` | `smithy_chimney` :1969 | 2.50 × 1.88 × 9.82 | Interior version. The hearth is the best one in the kit: bed 0.85, fire box 1.1 × 1.4, hood lintel at 2.45, coal bed, fire irons. The 9.8 m stack must be cut to room height. |
| `SM_VK_Prop_Sawhorse` | :976 | 1.71 × 0.83 × 1.22 | OK: log and bow saw. Carpenter. |
| `SM_VK_Prop_ChoppingBlock` | :946 | 1.59 × 1.41 × 0.99 | OK for a woodshed (axe in the block, billets, chips). |
| `SM_VK_Prop_PottersWheel` | :752 | 1.69 × 1.20 × 1.10 | OK. |
| `SM_VK_Prop_Woodpile` | :1357 | 3.70 × 1.30 × 1.52 | Interior version: it has a roof lean-to. A log basket or firewood stack is missing. |

### Crafts

| Piece | Builder | Size (m) | Verdict |
|---|---|---|---|
| `SM_VK_Prop_Loom` | `ind_loom` :953 | 1.80 × 2.11 × 1.83 | OK: floor loom, 20 warp threads, cloth roll, bench; the weaver faces −Y. |
| `SM_VK_Prop_SpinningWheel` | :983 | 1.08 × 0.52 × 1.41 | OK: distaff with wool. |
| `SM_VK_Prop_DyeVat`, `SM_VK_Prop_HideFrame` | industry | 1.62 × 1.50 × 1.61 / 1.70 × 0.95 × 2.04 | OK for workshop variants. |

### Livestock (longhouse byre, stable corner)

- `SM_VK_Animal_Cow` 2.61 × 1.03 × 1.57, `_Horse` 2.95 × 0.89 × 2.52, `_Pig`, `_Sheep`, `_Goat`, `_Chickens` 1.91 × 1.56 × 0.71 (humble :550–754). `SM_VK_Prop_Chickens` (core). All OK.
- `SM_VK_Prop_HayBale` 1.61 × 1.09 × 1.28: OK.
- `SM_VK_Prop_HayRack` (`hum_prop_hayrack` :769) has a thatch hood, so it needs an interior version (a manger).

### Lighting and decor

| Piece | Size (m) | Verdict |
|---|---|---|
| `SM_VK_Prop_Lantern` (`prop_lantern` :587) | 0.32 × 0.68 × 0.62 | OK: wall-bracket lantern with a GLOW box. |
| `SM_VK_Prop_Festoon` (`festoon` :1798) | 6.01 × 0.12 × 0.78 | OK: glow-bulb string for a tavern ceiling line. |
| `SM_VK_Prop_InnSign` / `_TavernSign` / `_SmithSign` | 0.30 × 2.15 × 1.30 / 0.46 × 1.68 × 1.35 / 0.12 × 1.08 × 1.18 | Tweak: nice above-bar decor, but the brackets stick out 1–2 m. |
| `SM_VK_Banner_Wall` (`sky_banner_wall` :755) | 0.16 × 1.27 × 2.48 | Tweak: bracket banner. Flat tapestries are missing. |
| `bell()` helper | :2643 | Bronze bell, if a chapel prop is wanted. |
| `SM_VK_Prop_WaysideShrine` (`con_shrine` :1059) | 1.21 × 1.23 × 3.22 | Tweak: stone pillar with a niche and statue (PAPER lathe). Could be a chapel side altar. |

### Floors, lofts and access

- `SM_VK_Ceiling_Cell` (`fro_ceiling_cell` :600), 2.99 × 3.00 × 0.28: plank deck with joists, planks on top at H − 0.24. Usable as a floor or loft tile (place it at z −2.76). It is 3 m only; a 1.5 m tile is missing.
- `SM_VK_Prop_LadderLean` (:585), 0.50 × 0.77 × 2.79: loft ladder. It could be a storey-change trigger in hovels.
- `SM_VK_Stair_Ext` (`ext_stair` :3408), 4.70 × 1.04 × 4.31: a wooden flight of 13 treads, rising 3.3 over a 2.7 run, with railing and landing. A good template for the interior stair.
- `SM_VK_Stair_Stone_Ext` (`twn_stair_stone_ext` :828), 5.45 × 1.36 × 4.74.
- `SM_VK_Prop_CellarHatch` (:867), 1.54 × 1.56 × 1.29: exterior-only; the interior trapdoor is missing.

### Pieces with no existing equivalent

- Beds: box bed, four-poster, straw bed frame.
- Chests.
- Shelves and cupboards, pantry shelving.
- Bar counter.
- 3 m long table, backless forms.
- Chapel: pews, altar, altar rail, candlesticks and candle stands, chandelier or corona.
- Wall fireplace and central-hearth kerb.
- Interior bread oven and forge (room height).
- Workbench.
- Rugs, rushes on the floor.
- Tapestries.
- Trapdoor, interior stair.
- Manger.
- Single crate, standalone barrel (only needs registering), log basket.

### Helper functions for matching each exterior family

| Family | Helpers |
|---|---|
| Stone | `stone_panel`, `grid_cut`, `plinth`, `rock`, `wall_rocks` (aligned to painted stones on the −Y face only), `window_frame`, `shutter` |
| Plaster and half-timber | `plaster_ground`, `timber_frame`, `brace`, `braces_pattern`, `pegs` |
| Wattle | `hum_daub`, `hum_post`, `hum_bar`, `hum_plate`, `hum_plinth`, `hum_patch` |
| Log | `fro_log`, `fro_chink`, `fro_course_z`/`fro_course_r` (phase A 0.47 / B 0.62 + 0.30·i), `fro_board` |
| Openings in thick walls | `twn_hole`, `twn_arch_fill`, `twn_arch_soffit`, `twn_voussoirs`, `twn_jambs`, `twn_jack_arch`, `twn_belt`, `twn_reveal` |
| Chapel | `lancet_pts`, `lancet_surround`, `CH_DRESS` = `DRESS` |
| Props | `barrel`, `_cyl`, `_ico`, `_tube`, `lathe`, `ring`, `card`, `goods_map`, `kit_fish`, `con_pole`, `con_board`, `con_log`, `con_flame`, `ind_flames`, `ind_pelt`, `ind_beam`, `ind_lathe` |

Goods atlas cells: cabbage, pumpkin, carrot, apple, bread, cheese, fish, fish_smoked, hide, fur, meat, ham, sausage, turnip, herbs, pomace.

## 2. Buildings whose interiors we need

Conventions: 3 m cells; wall modules are centred on the cell edge; the house front faces local −Y.

### Hovel: `build_hovel(variant cruck/hip/leanto)` (vk_mod_humble:937)

- **Size:** 2×2 cells (6 × 6 m) on a 3×3 lot. Tier T1, "4 beds".
- **Walls:** wattle-and-daub (`SM_VK_Wall_Wattle*`, `Corner_Wattle`).
  - Wall top 2.4 m. Rubble footing to 0.35, oak sole plate at 0.45.
  - Crooked posts and tilted braces; a sagging 3-piece wall plate.
  - Daub is PLASTER in the "Daub" style (0.80, 0.65, 0.47), pillowed between the timbers, with bare patches showing T_VK_Wattle.
  - Thickness about 0.30 (outer timber face at y −0.16, daub −0.12…+0.12).
- **Roof:** thatch "haystack" with cruck gables (curved blades); ridge at about 6.6 m.
- **Smoke vent** (`RoofThatch_Vent`) over bay 0, or bay 1 for `hip`. There is no chimney, so the interior has an open central hearth under the vent.
- **Faces:** F `.W`, B `..`, L `..`, R `DW`. The door is on the R gable at y −1.5, a window at y +1.5.
- **Door:** 0.90 wide, about 1.75 clear (threshold 0.37, lintel 2.12). Plank leaf ajar 25° inward.
- **Window:** 0.70 × 0.55, sill 1.10. Unglazed (VOID), 2 rods, top-hung board shutter propped open 55°.
- **Yard:** woodpile or lean-to, wattle coop, chickens, garden bed, bench.

### Longhouse: `build_longhouse` (:964)

- 5×2 cells (15 × 6 m). T1, "8 beds + 4 livestock". Same wattle family.
- F `.W.W.`, B `....W`.
- L cruck gable `D.`: people door at y +1.5.
- R plank gable `B.`: byre door `Wall_Wattle_Byre`, 2.0 wide × 2.1, split stable doors, at y −1.5.
- Vents over bays 1 and 3 (x −4.5 and +1.5).
- Interior: people end (hearth under vent 1) plus a byre end (cow, horse, sheep, hay rack, trough) behind a partition.

### Standard house: `build_house_v` (vk_helpers:1029) and `build_L_v` (:1067)

- **Size:** n×2 cells. Valley infill uses n = 2–3 with 1–2 storeys; the code allows 3. The L plan is a 2×2 junction plus a cells along +X and b cells along +Y.
- **Ground floor:**
  - Stone (60%): `SM_VK_Wall_Stone*`, grey rubble T_VK_Stone (stone styles Rubble, Warm, Cool, Dark, Field). 0.5 thick (−0.25…+0.25), 3.0 high. Chunky plinth rocks, battered base, pop-out stones, rough corner quoins.
  - Plaster (40%): `SM_VK_Wall_Plaster*`. Stone plinth to 0.75, plaster 0.44 thick, dark timber posts, sill and head beams and braces on the outside.
- **Upper storeys:** `SM_VK_Wall_Timber{,_X,_K,_Window}`, 2.8 high. Jettied (joist ends and belt beam out to about −0.6), dark pegged oak, plaster infill 0.46 thick.
- **Colours:** plaster Cream / White / Ochre / Rose. Shutters Teal / Red / Green / Blue / Natural, about 1 in 5 worn. Roofs Red / Blue / Green; Thatch only on plaster houses; Slate / Shingle by district. The L plan never gets thatch.
- **Openings:**
  - One door at a random front bay; porch (45%) or lantern; planters.
  - Flower boxes under 70% of windows.
  - Back wall: random W/`.`. Each end wall has one bay that may be a window.
- **Chimney:** `SM_VK_Chimney` stands on the roof at a random bay, 1.0 m square, at ±1.3 m from the ridge line. It starts at the wall top, so there is no ground-floor breast. The interior hearth goes about 1.45 m in from a long wall.
- **Dormers:** on 1-storey houses, 55% per bay, which suggests an attic floor.
- **Cottage:** the finished construction-site "3x2 two-storey cottage" (vk_mod_construction:1121) uses this same family.

### Town houses (vk_mod_town)

- **Upper-storey families:**
  - `SM_VK_Wall_StoneUp*`: 0.5 thick. Plain, window, Romanesque twin light, slit, loading door, door. Stone belt course, jack arches.
  - `SM_VK_Wall_PlasterUp*`: 0.44 thick. Plain, window, oxeye; timber bands, bare patches.
  - Timber: as in the standard house.
- **Shop walls:** `Wall_Stone_Shop` / `Wall_Plaster_Shop` have a 2.2 m opening (0.93–2.35), a drop-down counter at 0.95 projecting 0.6 outward, a canopy, and goods.
- **Merchant house** `build_merchant_house` (:1048): T4, 3×2, Stone + StoneUp × 2 (wall top 8.6). Slate roof with stepped gables and a hoist cross-gable. Street front F `SDS` / `TLT` / `WLW` (two shops, stacked loading doors). Optional stone turret. External stone stair at the back to the first-floor door, cellar hatch, walled yard. Chimney at x −3.
- **Gable-front townhouse** `build_townhouse_gablefront` (:1078): T3, 2 wide × 3 deep, Plaster + Timber × 2. The street gable has a shop and door, an oriel, and a hoist gable. Colours Cream / Ochre / Rose / White / Sage; roof Red / Green / Shingle.
- **Corner house** `build_corner_house` (:1101): T3–4, L plan (3×3 L), Stone + Timber × 2. A shop on each street face, plaster turret on the corner, first-floor gallery in the yard.
- **Terrace** `build_terrace(units)` (:1139): T3, units 1–3 cells wide × 2 deep, 2–4 storeys. Ground Stone or Plaster; uppers Timber / PlasterUp / StoneUp. Shops with pent roofs, cart passage and vault, back galleries, firewalls and party chimneys.

### Log cabin: `build_logcabin(n)` (vk_mod_frontier:695)

- n×2 cells (default 2×2, also 3×2). One storey, wall top 3.0.
- **Walls:** `SM_VK_Wall_Log*` (phase A on the long sides) and `_Log_B*` (ends, half a course up).
  - 9 dark round WOOD logs per 3 m (r about 0.165, centre line y −0.09, outer face −0.255, so about 0.33 thick).
  - Daub chinking in PLASTER (Daub or Cream), fieldstone footing (stone "Field").
  - Notched corners with log ends sticking out about 0.25 m, ENDGRAIN caps.
- **Roof:** Shingle, `Roof_Gable_Logs`.
- **Chimney:** `SM_VK_Chimney_Gable_H30` outside the L gable, centred at y 0 (the seam between the two wall modules). The interior fireplace goes at the centre of the L gable wall.
- **Door:** on the long front (n = 2 gives `DW`), or on the R gable with a porch (40%). Opening 1.2 wide (about 1.0 between the jambs), about 2.03 tall (phase A: 0.33–2.36).
- **Window:** 0.94 × 0.87 glass (1.24–2.11), frame x ±0.55, shutters in Red / Green / Natural / Blue / Teal.
- **Yard:** woodpile against the blank back bay, flower boxes, lantern. The woodcutter variant is a 2×2 cabin with a log lean-to.

### Tavern: `build_tavern` (vk_helpers:1934)

This builder is not placed in the valley; the inn is.

- `build_L_v(a=2, b=1, 2 storeys)`: wing A x −3…9 (4 cells) × y −3…3, junction wing to y 6.
- Stone ground floor, Ochre timber upper, Red shutters, Red roof.
- Round-arched stone door in A front bay 1 (x 1.5) with a porch and tavern sign. The B inner side may get a second door (W/D choice).
- Chimney on wing A (x 4.5 or 7.5).
- Beer garden in the inner yard (x 3–12, y 3–9): 2 tables and stools, barrel stack, festoon, lamp posts, fence.

### Inn: `build_inn` (:2177)

- `build_house_v(3, 3 storeys)`: 9 × 6 m. Wall heights 3.0 + 2.8 + 2.8 = 8.6.
- Stone rubble ground floor; Ochre plaster jettied timber frame above (V/X/K braces); Red shutters; Red tile roof; every window lit.
- Front `WDW`: stone arched door in the middle bay, lanterns either side. Back `W.W`; each end has one possible window.
- Chimney at a random bay (y ±1.3). Possible dormers and porch.
- Props: big tankard `InnSign`, `AleCask` and `BarrelStack` by the door, hitch rail, weathervane, beer garden on +X.
- Interior plan: ground-floor taproom; guest rooms on floors 1 and 2 (the brief allows larger interiors).

### Smithy: `build_smithy` (:2154)

- **Forge house:** 2×2 at smithy y 0…6, one storey, via `build_house_v(front="DW", back="..", chimney=False)`. Stone "Dark", Slate roof, Natural shutters, lit windows, possible dormers.
- **Workshop canopy:** `Smithy_Canopy` 6 × 6 at y −6…0. Posts 0.36 thick at ±2.75 on stone pads, 3.2 m high, knee braces, Slate roof, ridge 4.6.
- **Forge stack:** 9.8 m `Smithy_Chimney` at (−1.75, −1.05), backed onto the house front wall, hearth facing −Y. STONE with STONE_BLOCK courses and an iron rain hat.
- **Props under the canopy:** bellows, anvil, quench tub, tool wall, coal pile, grindstone, weapon rack, crates, woodpile, anvil sign, lantern, forge light.
- **Blocked door:** see §0.4.
- Interior plan: an enclosed forge, workshop and store combined.

### Chapel: `build_chapel(n=4, roof="Blue")` (:1716)

- **Size:** 4×2 cells (12 × 6 m), walls HC 4.5, ridge about 8.7.
- **Walls:** pale ashlar (T_VK_Ashlar), 0.6 thick (−0.3…+0.3).
  - Dressings in `M_VK_StoneDressed` (T_VK_StoneBlock tinted (0.62, 0.52, 0.44)): plinth 0.5, cornice, lancet surrounds.
  - Stepped buttress at every module's left edge (0.6 wide, 0.9 then 0.65 deep).
  - `Chapel_Corner` has pinnacles.
- **Roof:** Blue, `Roof_Gable_Stone` at both ends.
- **Openings:**
  - Front (−Y): 4 lancets. Back (+Y): 3 lancets plus the door in bay 1 (x −1.5).
  - The gable ends (`Chapel_Wall_Plain`) have no windows, so the interior altar wall is free for a hanging or an interior-only window.
  - Lancet: 0.9 wide, sill 1.3, spring 3.1, apex 3.80. `M_VK_Stained` glass, lead cames.
  - Door: pointed, 1.6 wide, spring 2.2, apex 3.44. PLANKS leaf, 3 stepped orders, iron straps, threshold step.
- **Bell tower:** `BellTower`, 3.6 m square, about 19 m tall. Attached outside the +X gable, its door (1.2 wide, apex about 2.83) faces away from the nave. There is no internal connection.

### Exterior openings reference

| Piece | Opening w × h (m) | Sill / threshold | Wall thickness |
|---|---|---|---|
| `Wall_Stone_Door` | 1.36 round arch, crown 2.68 (spring 2.0) | reveal 0.16 | 0.50 |
| `Wall_Stone_Window` | 1.10 × 1.20 | 1.05 | 0.50 |
| `Wall_Plaster_Door` | 1.24 × 2.30, flat lintel | 0 | 0.44 (plinth 0.53) |
| `Wall_Plaster_Window` | 1.10 × 1.15 | 1.10 | 0.44 |
| `Wall_Timber_Window` (upper) | 1.00 × 1.20, no shutters | 0.95 | 0.46 |
| `Wall_Timber_Door` (upper) | 1.00 × 2.20 | 0.2 | 0.46 |
| `Wall_StoneUp_Door` | 1.10 round arch, crown 2.35 | 0.30 | 0.50 |
| `Wall_StoneUp_Window` / `PlasterUp_Window` | 0.90 × 1.20 | 0.75 / 0.80 | 0.50 / 0.44 |
| `PlasterUp_Oxeye` | ⌀ 0.72, centre at 1.55 | – | 0.44 |
| Stone / Plaster `_Shop` | 2.20 × 1.42 | counter 0.95 | 0.50 / 0.44 |
| `Wall_Log_Door` / `_Window` | 1.2 (1.0 clear) × 2.03 / 0.94 × 0.87 | 0.33 / 1.24 | about 0.33 |
| `Wall_Wattle_Door` / `_Window` | 0.90 × 1.75 / 0.70 × 0.55 | 0.37 / 1.10 | about 0.30 |
| `Wall_Wattle_Byre` | 2.00 × 1.9 | 0.22 | about 0.30 |
| `Chapel_Wall_Door` / `Chapel_Wall` | 1.60 × 3.44 pointed / 0.90 × 2.50 lancet | 0 / 1.30 | 0.60 |

Storey heights for reference: ground 3.0, upper 2.8 (floors at 3.0, 5.8, 8.6), wattle 2.4, chapel 4.5, smithy canopy 3.2. Exterior floor levels vary (stone reveal 0.16, log sill 0.33, wattle threshold 0.37), which doesn't matter for separate interior scenes.