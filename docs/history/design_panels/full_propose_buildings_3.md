# Village Kit expansion: new house types and village features (level art and visual storytelling proposal)

This is a design-only proposal. All sizes are in metres and follow the kit's conventions: `CELL`=3.0, `H1`=3.0, `H2`=2.8, `HB`=4.2. Wall modules are 3 m wide and centred on the cell edge. The outer face points toward local −Y, and the left-edge post belongs to the module. Roofs use `PITCH` 52° and `KICK` 26°. For the current M roof, `RIDGE` = 0.35 + 3·tan52° = **4.19 m** above the wall top, and the eave tip sits 0.31 m below the wall top.

Effort key:
- **S** is about half a day, mostly reuse or parameter changes.
- **M** is 1–2 days, with new geometry functions.
- **L** is 3–5 days, with several pieces plus a builder.

---

## 0. What the current renders show

These notes come from `nature_town_aerial.png`, which is the real colony-sim camera, plus `town_street.png` and `village_special_buildings.png`.

1. **Every house has the same roof.** Each house is 2 cells deep with a 52° pitch, a ridge at wall top + 4.19 m, and its eave facing the street. From the 3/4 camera the residential area reads as about 18 near-identical orange wedges. Roofs make up roughly 60–70% of building pixels at this zoom, so roof variety is worth more than any facade detail.
2. **About 70% of roof area is one orange-red.** There are 3 blue roofs, 1 green and 4 thatch. No dark or grey roof material gives the eye a rest. The accents (awnings, flower boxes) are under 10 px at this zoom.
3. **Only four objects break the skyline:** the chapel spire (~17 m), the town hall cupola (~16 m), the windmill and the guard tower. All of them sit at the plaza or on the edge. Residential streets have no vertical accent other than ridge chimneys.
4. **There is no water, no level change and no edge.** The village fades into forest. There is no river, bridge, quay, palisade or wall, and these are the strongest storytelling devices a medieval town has.
5. **You can't tell what a building does from above.** The blacksmith is a green-roofed house with an anvil about 30 px tall. `SM_VK_Prop_TavernSign` and `Sign_*` are thin boards, seen edge-on from a high camera.
6. **Buildings have no visible states.** There are no construction stages, no stockpiles that grow or shrink, and no smoke sockets. In a colony sim, these are the main visual feedback for how the colony is doing.

Worth keeping: the chunky bevelled geometry, bell-cast eaves, timber-frame vocabulary, painted AO grime from `finish()`, and the `_dress()` dressing (flower boxes, ivy, planters). The variant material system (`VARIANT_MATS` / `variant_mesh`) is the right lever for colour: most of the colour work below is data rather than new meshes.

---

## 1. Level-art rules every new piece should follow

### 1.1 Height ladder

| Tier | Examples (new ones in bold) | Top height |
|---|---|---|
| Clutter | props, fences, stalls | < 2.5 m |
| Low | **hovel** (ridge 6.1), **shed/hut on the S roof** (2.6 + 2.27 = 4.9), **longhouse** (6.4) | 4–6.5 m |
| Mid | 1-storey cottage (7.2), 2-storey cottage (10.0) | 7–10 m |
| High | 3-storey (12.8), **4-storey terrace** (15.6), **stepped gable** +0.5 | 12–16 m |
| Landmark | chapel (~17), town hall (~16), **keep (21–25)**, **round wall tower (14.5)**, **oast kiln (10.6)**, **treadwheel crane (9, special silhouette)** | ≥ 16 m, or a unique silhouette |

Rules:
- Every ~40 m radius the colony camera can frame should contain one Landmark-tier object.
- On residential streets, every third building gets a "breaker": a corner turret, cross gable, gable chimney, tower house or roof emblem.

### 1.2 Roof grammar

A roof is defined by four choices:
- **Depth family:** S (3 m), M (6 m, current) or L (9 m).
- **Orientation:** eave to the street, or gable to the street.
- **End type:** gable, hip, half-hip, stepped, party, hoist or cruck.
- **Breakers:** dormer, cross gable, turret, vent, chimney type.

Generator rule: two neighbouring buildings must differ in at least 2 of {depth family, orientation, end type, ridge height (by at least one storey), roof material}.

### 1.3 Colour budget

Target roof shares across a whole village:

| Material | Share |
|---|---|
| Red | 30% |
| Thatch | 20% |
| **Slate (new)** | 15% |
| Blue | 12% |
| **Shingle (new)** | 10% |
| Green | 8% |
| Other | 5% |

Every production building gets **one hero colour mass of at least 2 m², visible from above**: a banner, dye vat, cloth rack, awning, painted boat or bunting. It always goes through the existing `cloth` variant slot (`CLOTH_A`), so guild and faction colours are data, not meshes.

### 1.4 Signage at three reading distances

1. **Silhouette, readable at 60 m:** a ridge emblem 0.9–1.2 m on a 1.4 m iron spike at the gable finial, rooftop pennants, turrets, vents, cranes.
2. **Colour, readable at 30 m:** wall banners 0.9 × 2.2 m, awnings, dye vats, bunting, painted boats.
3. **Detail, readable at 10 m (already exists):** hanging signs, flower boxes, shutters.

### 1.5 Sockets for Unity

Each `finish()` call should also create child empties from a list the piece function returns:

| Socket | Placed on |
|---|---|
| `SOCK_Smoke` | every chimney, vent, forge, kiln and campfire |
| `SOCK_Light` | lanterns and window-glow centres |
| `SOCK_Door` | nav entry point, 0.9 m outside the door |
| `SOCK_Work` | colonist work spot |
| `SOCK_Stock` | stockpile anchor |
| `SOCK_Spin` | spinning parts, with custom props `spin_axis` and `rpm`. `Windmill_Sails` already has `spin_axis`. |

Smoke is the strongest "the village is alive" signal from above, so every chimney needs a socket.

### 1.6 What these pieces need from the marching-squares terrain

These are my assumptions and requests for the terrain track:

- **Tiles:** the terrain tile is 3.0 m (= `CELL`), and tile corners sit on building-grid corners. Building walls therefore run along tile edges.
- **Cliff step `LVL` = 1.5 m** (recommended). That is half of `H1`: a one-level podium equals half a storey, and two levels equal `H1`, so a house on a two-level slope can have doors on both levels.
- **Water:** the surface is −0.6 m below the adjacent bank and the river bed is −1.5 m. All piles and piers go down to −2.5 m so they work on any bed.
- **Contour-following pieces** (retaining wall, quay, quarry face) follow marching-squares contours. Those contours pass through tile-edge midpoints, so each set needs:
  - `_Straight`: 3.000 m, through the tile centre.
  - `_Diag`: 2.121 m at 45°, from edge midpoint to edge midpoint.
  - `_Post`: placed at those midpoint vertices to hide joints.
- **Grid-drawn pieces** (palisade, town wall, hedge, field wall, fence) run on cell edges. Each needs `_Straight` (3.000), `_Diag` (4.243 = 3√2, across a cell diagonal) and a joint `_Post` or tower at cell corners.
- **Build odd-length pieces with `wobble=False`.** `finish()` wobble is periodic in x with a 3 m period, so it would tear 2.121, 4.243 and 4.5 m pieces at the joins.
- **Foundation skirt:** every ground-touching building piece gets a hidden skirt down to z = −0.6, so houses sit on non-flat corners without gaps.

---

## 2. Tier A: pieces that unlock many variants (build these first)

| # | Pieces | Unlocks | Effort |
|---|---|---|---|
| A0 | Roof depth families **S (3 m) and L (9 m)** plus `_Single` pieces | huts, sheds, 1-cell wings, halls, tithe barns, warehouses, market halls; 1-bay buildings | M |
| A1 | **StoneUp and PlasterUp** upper-floor wall families | stone merchant house, tower house, keep, warehouse, gatehouse, colourful plaster terraces | S |
| A2 | New **gable kinds**: stepped, party, hoist, cruck, logs | terrace roofline, merchant houses, hovels, cabins | S each |
| A3 | Generic **`roof_field()`**, plus HalfHip, CrossGable, TJunction, Thatch Eyebrow | end and roof-break variety for all houses | M |
| A4 | **Slate and Shingle** roof textures as roof variants | colour budget, wealth reading | S |
| A5 | **Wall_Posts / Corner_Posts / Ceiling_Cell** (open bays) | market hall, sawmill, lavoir, cart shed, open workshops | S |
| A6 | **Shop fronts** (stone/plaster) with a goods socket | trade streets, butcher, weaver, herbalist | M |
| A7 | **Gallery_Wood** | coaching inn, waterfront houses, loggias | S |
| A8 | **Turret stack** (corbel, segment, cap; r = 1.0 and 1.4) | corner houses, manor stair turret, keep | M |
| A9 | **Chimney_Gable_1/2/3, Chimney_Party, Roof_Vent, RoofThatch_Vent** | skyline rhythm, smoke sockets, workshop identity | S |
| A10 | **Parapet, Parapet_Corner, Bartizan, Roof_Pyramid_6/9** | tower house, keep, gatehouse, wall towers | M |
| A11 | **Signage system**: `emblem()`, Emblem_Ridge_*, Banner_Wall, Banner_Pole, Banner_Roof, Prop_Bunting | readable function, faction colours | M |
| A12 | **Construction stages** and stockpile fill levels | the colony-sim build loop | M |
| A13 | **Humble walls**: Wattle, Log, Shed | camp → hovel → cabin → longhouse ladder | S / M / S |
| A14 | **Terrain civil pieces**: Podium, Retaining, Stair_Terrain, Stair_Stone, CellarHatch | building on the marching-squares levels | M |
| A15 | **Wall_Passage** (arch through a building) | terrace backyard pathing, coaching inn | S |
| A16 | **Jetty** corner and placement offset (Tier B) | overhanging timber streets | M |

### A0. Roof depth families (the biggest single multiplier)

The roof code reads module globals (`HALF`, `EAVE`, `PITCH`), but `roof_profile()` hard-codes `ys=[0,0.75,1.5,2.25,3.0,3.45,3.9,EAVE]`. `gable_end()` hard-codes `ys=[YC,2.5,...]` and places ornaments at absolute y values. The refactor:

```
def set_roof_family(fam):          # "S" | "M" | "L"
    HALF = {"S":1.5, "M":3.0, "L":4.5}[fam]
    OVER = {"S":0.9, "M":1.35, "L":1.35}[fam]
    EAVE = HALF + OVER
    RIDGE = roof_z(0)
roof_profile(): ys = [HALF*t for t in (0,.25,.5,.75,1)] + [HALF+OVER/3, HALF+2*OVER/3, EAVE]
gable_end(): scale every hard-coded y by HALF/3.0; keep z logic (it already uses under()/RIDGE)
```

| Family | Ridge above wall top | Long walls at | End-wall cells at | New piece names |
|---|---|---|---|---|
| S | 2.27 m | y = ±1.5 | y = 0 | `SM_VK_RoofS_{Mid,Gable,Hip,Single}`, `RoofThatchS_*` |
| M (existing) | 4.19 m | y = ±3 | y = ±1.5 | adds `SM_VK_Roof_Single` |
| L | 6.11 m | y = ±4.5 | y = −3, 0, +3 | `SM_VK_RoofL_{Mid,Gable,Gable_Planks,Hip}`, `RoofThatchL_*` |

- `_Single` is a one-bay piece with gables at both ends. Today a 1-bay building can't be roofed: placing two Gable pieces at x = 0 overlaps them completely.
- Chimneys need a height parameter per family: top = RIDGE + 1.5.
- Result: the scale variety alone (4.9 m huts next to 10.3 m tithe barns) breaks the "field of wedges" look.

### A1. StoneUp and PlasterUp families (upper floors that aren't timber)

**StoneUp**, built by `wall_stone_up(k, kind)`:
- `stone_panel(k,-1.5,1.5,0,H2)` plus `wall_rocks(...)`. **No** `plinth()` or `batter()`.
- ASHLAR belt course: `box((0,-0.33,0.10),(3.0,0.20,0.20))`, which marks the floor and hides the seam.
- Use `finish(grime=False)`. The grime ramp starts at the piece's z = 0 and would darken the bottom 0.9 m of an upper floor.

| Piece | Kind | Geometry |
|---|---|---|
| `SM_VK_Wall_StoneUp` | `.` | plain |
| `SM_VK_Wall_StoneUp_Window` | `W` | 0.8 × 1.2 opening at z 0.75–1.95; `window_frame(..., shutters=True)`; ASHLAR jambs 0.18 |
| `SM_VK_Wall_StoneUp_Twin` | `T` | two round-headed lights 0.5 × 1.3 (heads from `lancet_pts`, radius 0.25), central colonnette from `lathe` (r 0.07), ASHLAR. Reads as "wealthy". |
| `SM_VK_Wall_StoneUp_Slit` | `S` | 0.14 × 1.0 slit with 0.5 × 1.3 surround (copy of the `guard_tower` slit code) |
| `SM_VK_Wall_StoneUp_Loading` | `L` | 1.2 × 2.1 opening; two PLANKS leaves open at 100°; IRON strap hinges; WOOD lintel |
| `SM_VK_Corner_StoneUp` | — | ASHLAR quoins alternating 0.9 / 0.5 long × 0.44 high (the `guard_tower` corner loop), height H2 |

**PlasterUp:** `plaster_ground()` logic at H2, with no stone base.
- Kinds: `.`, `W`, and `O` (ox-eye round window, 0.7 m diameter).
- They take plaster variants, so each terrace unit becomes a full-height block of colour. From the high camera that colour block is far more visible than shutters.

### A2. New gable kinds

These plug into `gable_end(k, kind)` / `gable_special()`. Stone kinds end the roof slab flush: `roof_slab(k,-1.5,1.85,s)` with no verge overhang.

| Piece | Geometry | Silhouette role |
|---|---|---|
| `SM_VK_Roof_Gable_Stepped` | ASHLAR triangle at XF = 1.8. Five steps per side: step i at y = ±(3.3 − 0.62·i), top z = `roof_z(\|y\|)` + 0.45, block 0.62 (y) × 0.45 (x), coping 0.08 overhanging 0.05. Kneeler at y = ±3.3, z 0–0.9. Apex pinnacle 0.6 × 0.45 × 1.0 plus ball (`_ico` r 0.2). Ox-eye window. `trim=False`. | Sawtooth rising 0.45–0.9 m above the roof. Strongest urban skyline cue. |
| `SM_VK_Roof_Gable_Party` | Flush end, face at XF = 1.75. STONE triangle rising 0.30 above the roof surface. ASHLAR coping along both rakes (reuses the stone coping loop in `gable_special`). No bargeboard or finial. | Lets terrace units of different heights butt together cleanly. |
| `SM_VK_Roof_Gable_Hoist` ("merchant") | Timber gable. A 1.0 × 1.6 loading door at z = 0.9 replaces the gable window. Hoist beam 1.4 m proud at z = top − 0.35, pulley (`_cyl`), rope, hanging BURLAP sack. Reuses the hoist code from `gable_special` planks. | Merchant/warehouse identity, readable from above. |
| `SM_VK_RoofThatch_Gable_Cruck` | Two curved cruck blades, each 6 box segments along a quadratic Bézier: (±2.9, −HW) → (±2.6, 2.0) → (±0.1, top − 0.2). Tie beam at z = 0, collar at 0.6·top. Mud plaster plus WATTLE infill. 0.6 × 0.4 smoke louver near the apex. The piece extends below z = 0, down to −HW. | Tells you "poor" instantly. |
| `SM_VK_RoofShingle_Gable_Logs` | Horizontal logs (r 0.16, pitch 0.30) shortening to follow `under(y)`; ENDGRAIN caps. | Log cabins. |

### A3. `roof_field()`: one height-field roof builder, four new pieces

`roof_hip()` already samples `hip_z(x, y)` on a 0.25 m grid. Generalise it:

```
def roof_field(k, zfun, xs, ys, mat, breaklines=()):
    # sample zfun on xs×ys + extra samples along breaklines (valleys/hips);
    # top surface, underside offset RT/cos(PITCH), edge caps; UV as in roof_hip; eave_tabs() on free eaves
```

| Piece | `zfun` | Notes |
|---|---|---|
| `SM_VK_Roof_HalfHip`, `RoofThatch_HalfHip` (jerkinhead) | `min(roof_z(\|y\|), ZC + (1.5 - x)*tan(60°))` with ZC = 0.55·RIDGE ≈ 2.3 | The hip starts at the end-wall line at height 2.3 and reaches the ridge 1.09 m inboard. The gable wall is a trapezoid, clipped where `under(y)` = ZC. **M** |
| `SM_VK_Roof_CrossGable` (wall dormer, "Zwerchhaus") | `max(roof_z(\|y\|), roofS_z(\|x\|))` for y ≤ −1.5 | Cross ridge 2.27 m above the wall top. It meets the main slope at y = −1.5. Valley breaklines run (±1.5, −3) → (0, −1.5). The cross eave/verge extends to y = −3.6. Facade triangle at y = FACE2 (timber frame, 0.8 × 0.9 window), plus bargeboards and a finial. Variant `_Hoist` has a loading door and hoist beam. **M.** Breaks the long eave lines of cottages, the town hall and terraces. |
| `SM_VK_Roof_TJunction` | `max(roof_z(\|y\|), roof_z(\|x\|))` for y < 0, else `roof_z(\|y\|)` | Lets a 1-cell-wide wing join a main block. Enables T-plans and U-plans with the existing `Roof_LCorner`. **S** once `roof_field` exists. |
| `SM_VK_RoofThatch_Eyebrow` | `thatch_z + 0.6·cos²(π·x/2.4)·smoothstep(y ∈ [−3.4, −1.8])` for \|x\| < 1.2 | A 1.0 × 0.5 window in a small WOOD wall under the bump. Thatch houses currently get no dormers (`build_house_v` skips dormers when thatch). **M** |

### A4. Slate and shingle textures

Add these to `VARIANT_MATS["roof"]`:
- `"Slate": ("T_VK_RoofSlate", None)`: `gen_roofs` with a rectangular `shingle_layout(nrow=10, ncol=7)`, square-cut bottoms, base colour (0.20, 0.23, 0.28) with ±0.04 purple/green per-slate variation.
- `"Shingle": ("T_VK_RoofShingle", None)`: narrow split shakes about 0.15 m wide, weathered (0.42, 0.36, 0.29) with silver highlights (0.55, 0.53, 0.50).

Extend `random_style` roof weights per district (section 8). Slate means "stone and wealth"; shingle means "frontier and waterfront".

### A5. Open bays

| Piece | Geometry |
|---|---|
| `SM_VK_Wall_Posts` (H = 3.0) and `SM_VK_Wall_Posts_Shed` (H = 2.6) | Post at x = −1.5 only (kit convention), 0.28 × 0.28, on a 0.5 × 0.5 × 0.2 stone pad. Top beam 3.0 × 0.3 × 0.3 at z = H − 0.15. Two knee braces 0.7 m at 45°. |
| `SM_VK_Corner_Posts` | Braces on both axes. |
| `SM_VK_Ceiling_Cell` | 3 × 3 plank ceiling at z = H − 0.3 with 3 joists 0.2 × 0.25. Used under upper storeys over open ground floors. |

### A6. Shop fronts

`SM_VK_Wall_Stone_Shop` / `SM_VK_Wall_Plaster_Shop`, ground floor (H1):
- Opening x −1.1…1.1, z 0.85…2.35. Build the stone around it with `stone_panel` pieces, as `wall_stone_window` does. WOOD lintel 2.6 × 0.3 × 0.25.
- Lower shutter folds down into a counter: PLANKS 2.2 × 0.6 × 0.07, hinged at z = 0.85, on two WOOD brackets.
- Upper shutter is propped at 55° as a canopy: PLANKS 2.3 × 0.75, with 2 IRON rods.
- VOID quad at y = +0.1.
- A `SOCK_Stock` on the counter takes `SM_VK_Prop_ShopGoods_<kind>`: bread, apple, pumpkin (reuse `market_stall` goods), cloth (3 CLOTH bolts r 0.09 × 0.5), pots (3 CLAY lathe pots), boots, fish, meat.
- Goods are separate props, so there's one wall per material instead of one per trade.

### A7. Gallery_Wood

Wall-local; attaches to any upper-floor cell.
- Deck PLANKS 3.0 × 1.0 × 0.1 at the storey base, local y −0.45…−1.45, on 3 joists, with 2 diagonal brackets 0.9 m long underneath.
- Post at x = −1.45 only, 0.18 square, height 2.15. Top rail at 2.1.
- Handrail at 1.0, bottom rail at 0.15, balusters 0.06 every 0.2 m.
- `SM_VK_Gallery_End` adds the closing post and side rail.
- Why 2.15: on a top storey, the M-roof eave underside at local y = −1.2 is about 0.57 m below the wall top. The gallery tucks under the bell-cast eave with no roof change.

### A8. Turret stack

| Piece | Geometry |
|---|---|
| `SM_VK_Turret_Corbel` | Inverted cone from r 0.2 to r 1.0 over 1.2 m, in 4 ASHLAR rings. Top at z = H1. |
| `SM_VK_Turret_Seg` / `_Seg_Stone` | 12-sided, r = 1.0, H2 tall. PLASTER with WOOD posts every 30°. WINDOW 0.5 × 1.0 on the 3 outward facets. |
| `SM_VK_Turret_Cap` | 12-segment cone r 1.25, h 2.8, ROOF (UVs as in the `guard_tower` pyramid). Finial 0.6 plus ball or weathervane (the cupola rooster code). |
| `_Cap_Crenel` | Crenellated top for the keep. |

- Centre at (−0.45, −0.45) from a convex corner, which is the outer quadrant of the `Corner_*` convention.
- Stack rule: one segment per storey plus one extra above the wall top. On a 2-storey house the cap base is at 8.6 and the tip at 11.4, 1.4 m above the 10.0 m ridge.
- r = 1.4 variant: a full-height stair turret from the ground, with slit windows following a spiral (+0.7 m per 90°).

### A9. Chimneys and vents

| Piece | Spec |
|---|---|
| `SM_VK_Chimney_Gable_1/2/3` | External stack on the gable-end wall, centred on the ridge line. Base 1.6 (x) × 1.0 proud to z 2.2, 45° weathering shoulder, flue 1.0 × 0.8, cap 1.2 × 1.0 × 0.2, 2 CLAY pots. Tops at 8.19 / 10.99 / 13.79 m (wall top + RIDGE + 1.0). It pierces the verge overhang, which is correct and reads well. |
| `SM_VK_Chimney_Party` | 1.8 × 0.9 stack on a party wall at the ridge, 3 pots, top at RIDGE + 1.3. Gives terrace roof rhythm. |
| `SM_VK_Roof_Vent` | Ridge louver 1.4 × 0.9 × 0.8 with a mini gable roof and slats. For smithy, smokehouse and brewery. |
| `SM_VK_RoofThatch_Vent` | Ridge smoke hole with a small wooden cowl. For hovels and longhouses. |

All of these carry `SOCK_Smoke`.

### A10. Fortification top set

| Piece | Spec |
|---|---|
| `SM_VK_Parapet` | Sits at the wall top. Base 0.9 high × 0.5 thick, face at y = −0.55 (0.3 proud of the wall). Merlons 0.8 wide × 0.8 high centred at x = ±0.75; crenels 0.7. Coping 0.08. Machicolation-look course below: 5 corbels 0.3 × 0.45, two-stepped, z −0.5…0. Walkway slab 3.0 × 1.2 inside. |
| `SM_VK_Parapet_Corner` | Corner version. |
| `SM_VK_Bartizan` | r 0.85, 12-sided, 2.2 tall, on a 1.2 corbel cone; cone roof r 1.05 × h 2.0. Centre at (−0.5, −0.5) outside the corner. |
| `SM_VK_Roof_Pyramid_6` / `_9` | 4-segment cone (the `guard_tower` code) sitting inside the parapet walkway. Half-width 2.0 → radius 2.83, height 2.86 (55°). The 9 m version: half-width 3.45 → radius 4.88, height 4.93. |

### A11. Signage system

`emblem(k, kind)` builds a flat 0.12 m-thick, bevelled emblem that fits in 1.0 × 1.0:

| Kind | Primitives / materials |
|---|---|
| anvil, boot, potion | already in `shop_sign()` |
| pretzel | tube along a curve, 24 segments, r 0.07, BREAD |
| tankard | lathe body + `ring()` handle + PAPER foam `_ico` |
| fish | flattened `_ico` + tail triangle, STEEL |
| key | ring + shaft + teeth, BRONZE |
| sheaf | 20 fanned boxes + band, HAY |
| horseshoe | `ring()` 240°, IRON |
| scissors | 2 rings + crossed blades, STEEL |
| mortar and pestle | ROCK / WOOD |
| hammer and chisel | boxes |
| saw | toothed strip |
| axe | boxes |
| pick | boxes |
| shield | extruded pointed polygon, CLOTH_A + PAPER cross |

Mounts:
- **`SM_VK_Emblem_Ridge_<kind>`:** 1.4 m IRON spike at the gable finial (x = GX + 0.08), emblem centred at RIDGE + 1.3. This is the silhouette-scale sign.
- **`SM_VK_Sign_<kind>`:** existing bracket board, extended to the new emblems.
- **`SM_VK_Banner_Wall`:** pole bracket 1.2 m out at the storey top. Cloth 0.9 × 2.2 in 6 segments with a slight wave, swallowtail bottom, double-sided, CLOTH_A variant. Emblem appliqué in PAPER/YELLOW, 0.02 proud.
- **`SM_VK_Banner_Pole`:** 6 m pole, flag 1.6 × 1.0.
- **`SM_VK_Banner_Roof`:** 3 m ridge pole, pennant 1.8 long.
- **`SM_VK_Prop_Bunting_6` / `_9`:** catenary like `festoon()`, with 0.3 m triangles cycling CLOTH_A / CLOTH_B / YELLOW / LEAF.

Retrofit pass on existing buildings (S):

| Building | Additions |
|---|---|
| Blacksmith | Roof_Vent + Emblem_Ridge anvil |
| Bakery | Chimney_Gable + pretzel |
| Tavern | tankard + bunting in the beer garden |
| Stable | horseshoe |
| Town hall | 2 Banner_Wall + Banner_Roof |
| Guard tower | faction colour on the existing flag |

### A12. Construction stages and stock levels (core colony-sim loop)

**Stage pieces:**

| Piece | Spec |
|---|---|
| `SM_VK_Wall_Foundation` | Existing `plinth()` rocks, 0.8 m SOIL trench strip, 2 stakes and a string line. |
| `SM_VK_Corner_Foundation` | Corner version. |
| `SM_VK_Wall_Stone_Half` | `stone_panel` to z 1.2, top stones randomly removed. |
| `SM_VK_Wall_Timber_Frame` | `timber_frame(..., infill=False)`, frame only. |
| `SM_VK_Scaffold_Bay` / `_Ladder` | Per cell per storey. Poles r 0.06 at x = ±1.45, y = −1.2. Ledgers every 1.4 m, putlogs into the wall, 2 walk planks 0.3 wide at the top, one diagonal brace. |
| `SM_VK_Roof_{Mid,Gable,Hip}_Frame` | Rafters 0.12 × 0.16 every 0.6 m following `roof_profile()`, ridge beam, 2 purlins. |
| `SM_VK_Roof_Mid_Half` | Lower 40% tiled, rafters above. |

The builders take a `stage` parameter and substitute pieces through one table:

```
STAGE_SUB = {0: {"Wall_*":"Wall_Foundation", "Corner_*":"Corner_Foundation", "Roof*":None, ...},
             1: {"Wall_Stone*":"Wall_Stone_Half", "Wall_Timber*":"Wall_Timber_Frame", "Roof*":None, +"Scaffold_Bay"},
             2: {"Roof_Mid":"Roof_Mid_Frame", "Roof_Gable":"Roof_Gable_Frame", "Roof_Hip":"Roof_Hip_Frame", +"Scaffold_Bay"},
             3: {}}   # finished
def place_v(..., stage=3): piece = resolve(STAGE_SUB[stage], piece); if piece: ...
```

**Stockpiles in 3 fill levels (`_1/_2/_3`),** so the game can show inventory:

| Prop | Level 1 / 2 / 3 |
|---|---|
| `Prop_LogPile` | 6 / 10 / 15 logs, r 0.18–0.25 × 3.0, ENDGRAIN caps, stake posts |
| `Prop_PlankStack` | crossed layers 0.25 × 0.05 × 3.0 with spacer sticks; 6 / 12 / 18 layers |
| `Prop_StoneBlocks` | ASHLAR 0.6 × 0.4 × 0.4 on pallets |
| `Prop_OrePile` | ROCK with STEEL / BRONZE glint icos |
| `Prop_Sacks` | variants of the existing prop |

Also: `Prop_MortarTub`, `Prop_Wheelbarrow`, `Prop_Ladder`.

### A13. Humble walls

| Piece | Spec |
|---|---|
| `SM_VK_Wall_Wattle` (+ `_Door`, `_Window`, `Corner_Wattle`) | Wall top HW = 1.9, face at −0.2. `plinth()` rubble 0.35. Sill 0.2² at z 0.45. Rough posts at x = −1.5 and 0 (box with jitter 0.02). Wall plate at 1.8. Daub is PLASTER in the new `Mud` variant (0.80, 0.64, 0.46), with 1–2 fallen patches 0.4–0.7 m showing WATTLE (recessed 0.03). Door 0.9 × 1.65 (plank leaf ajar 30°, or a BURLAP hide). Window 0.45 × 0.35 with one propped shutter. |
| `SM_VK_Wall_Log` (+ `_Door`, `_Window`, `Corner_Log`) | 8 courses of r 0.16 logs (`_cyl` 8 segments, slight taper and jitter) at 0.30 pitch. Wall top HL = 2.6. End walls offset half a course so corners interlock. Log ends protrude 0.35 at the corners with ENDGRAIN caps. PLASTER chinking strip 0.1, recessed. |
| `SM_VK_Wall_Shed` (+ `_Door`, `_Window`, `_Wide`, `Corner_Shed`) | HS = 2.6. Vertical PLANKS boards (`grid_cut`), battens 0.06 every 0.3, sill on 3 stones. Door 1.1 × 2.0 with Z-brace. `_Wide` door is 1.8 m (byre / boathouse). |

### A14. Terrain civil pieces (for LVL = 1.5)

| Piece | Spec |
|---|---|
| `SM_VK_Podium_Wall` / `_Cellar` / `_Corner` | 3.0 × LVL stone, batter 0.15, top string course. Placed at z = −LVL under a house wall on the downhill side. `_Cellar` adds a 1.0 × 1.4 arched cellar door (the requested **cellar door**). |
| `SM_VK_Retaining_Straight` (3.000) / `_Diag` (2.121) / `_Post` | Contour pieces, height LVL. Dry stone with mossy coping (`mossy_material`). Optional `_Parapet` variant +0.6 m. The Post is a 0.6 × 0.6 pier with a cap at contour vertices. |
| `SM_VK_Stair_Terrain` / `_Narrow` | Rise 1.5: 9 steps of 0.1667 × 0.333, so the run is exactly 3.0 (one cell). Width 2.0 between 0.4 m cheek walls (1.2 for `_Narrow`). ASHLAR treads. |
| `SM_VK_Stair_Stone` | Along a wall to a raised door at +1.5: run 2.7, 1.0 wide, low parapet. A stone counterpart to `SM_VK_Stair_Ext`. |
| `SM_VK_Prop_CellarHatch` | Two plank leaves on a frame sloped 25°, 1.3 wide × 1.2 deep, 0.2 stone curb. Placed at a wall base. |

### A15. Wall_Passage

`SM_VK_Wall_Passage` (ground floor, H1):
- 2.4 × 2.7 segmental arch (`arch_ring` with hw 1.2, spring 2.0), plus a 6 m tunnel liner: PLASTER side walls y 0.25–5.75, PLANKS ceiling on joists at 2.9, cobble floor.
- The rear wall uses `SM_VK_Wall_Passage_Back` (arch only).
- Upper floors continue above as normal. This makes terraces pathable to backyards.

### A16. Jetty (Tier B, riskier)

- Offset upper-floor pieces on the long sides by J = 0.45 (place the existing timber walls at y = ±(3 + 0.45)).
- New `SM_VK_Corner_Timber_Jetty`: dragon beam plus a carved bracket and two 0.45 m filler strips, one along each axis.
- Roof pieces must be raised +0.25, because the bell-cast underside at |y| = 3.45 is about 0.2 m below the wall top.
- Use it on terraces, where party walls hide the end-wall seams. Avoid it on freestanding houses until the roof lift is checked.

### Builder API generalisation (needed by most of section 3)

```
def build_block(coll, origin, n, stories, style, depth="M", wall_h=None,
                faces=None,        # {"F":"DSW","B":"W..","L":"..","R":"W."}  per ground cell; S=shop, P=passage, A=arcade, O=posts
                upper=None,        # per-storey pattern or callable(r, cell)->piece
                ends=("gable","gable"),   # gable|hip|halfhip|stepped|party|hoist|cruck|logs|none
                breakers=(),       # [("cross",i),("dormer",i),("turret","FL"),("chimney_gable","R"),("vent",i),("gallery","B",lvl)]
                skip_walls=(),     # {"L"} when a neighbour owns the shared wall
                stage=3)
roof_top(stories, wall_h=None) -> (wall_h or H1) + H2*(stories-1)
```

- `build_house_v` and `build_L_v` become thin wrappers around it.
- `_pieces(style)` gains ground types: Wattle, Log, Shed, StoneUp, PlasterUp.
- Gable-to-street is just `rot += 90` with the door on an end face.

---

## 3. New house types (housing ladder)

Ridge heights are computed from the kit constants.

| Tier | Type | Footprint (cells) | Ridge | Effort |
|---|---|---|---|---|
| 0 | Settler camp | 3×3 cluster | 2.8 | M |
| 1 | Cruck hovel | 2×2 or 3×2 | 6.1 | S |
| 1 | Log cabin | 2×2 or 3×2 | 6.8 | S |
| 1–2 | Longhouse | 5×2 | 6.4 | S |
| 2 | Cottage variants (existing) | 2–4×2 | 7.2 / 10.0 | S |
| 3 | Rowhouse terrace | units 1–3 × 2, rows of 8–12 | 10.0–15.6, stepped | M |
| 3 | Gable-front townhouse | 2 wide × 3 deep | 12.8 | S |
| 3–4 | Corner house | L 3+2 | 12.8 (turret 14.2) | S |
| 4 | Stone merchant house | 3×2 | 12.8 (+0.9 steps) | S |
| 4 | Tower house | 2×2 | 14.5–15.6 (+ flag) | M |
| 5 | Manor house | U: 5×2 + 2×(2×2) + court 5×3 | 12.8 (turret 15.4) | L |

### 3.1 Settler camp (tier 0, colony start)
- **Role:** starting shelter for 2 colonists per tent; campfire for warmth and cooking; supply pile as initial storage.
- **Look:** patched cream canvas, a glowing fire, a covered wagon. The first thing the player sees, so it needs warmth: GLOW plus smoke.
- **New pieces:**
  - `SM_VK_Tent_A`: 2.4 w × 3.0 l × 2.0 h. Ridge pole and 2 uprights. Two sagging canvas slabs, back triangle, front flaps tied open over VOID, 4 guy ropes to pegs.
  - `SM_VK_Tent_Bell`: lathe cone r 1.8, h 2.8, centre pole, door flap.
  - `SM_VK_Prop_Campfire`: 8 stones r 0.55, 5-log teepee, GLOW core, tripod and pot, `SOCK_Smoke`, `SOCK_Light`.
  - `SM_VK_Prop_Bedroll`.
  - `SM_VK_Prop_Wagon_Covered`: `Prop_Cart` + 4 hoops + canvas.
  - Canvas uses CLOTH_B, with vertex-colour patches.
- **Reuses:** Prop_Crates, Prop_Sacks, Prop_BarrelStack, Prop_Woodpile, Prop_Cart.

### 3.2 Cruck hovel (tier 1)
- **Role:** cheapest permanent house, 1 family.
- **Look:** a shaggy thatch "haystack" on 1.9 m walls. The thatch eave sits 1.6 m above the ground. No chimney; smoke leaks from the vent.
- **New:** A13 Wattle walls, RoofThatch_Gable_Cruck (A2), RoofThatch_Vent (A9), `SM_VK_Prop_WattleFence` (3.0 m + 4.243 diagonal), `SM_VK_Prop_ChoppingBlock`.
- **Reuses:** RoofThatch_Hip (on a 2×2 both ends are hips, giving a true pyramid-haystack), RoofThatch_Mid, Prop_Woodpile, Prop_GardenBed, Prop_Chickens, Deco_Weeds.
- **Build:** `build_block(n=2|3, stories=1, wall_h=1.9, ground="Wattle", roof="Thatch", ends=("hip","hip")|("cruck","hip"))`.

### 3.3 Log cabin (tier 1, forest and frontier)
- **Role:** woodcutter, hunter or forester housing at the forest edge.
- **Look:** dark log walls, a silver shingle roof, a big external stone chimney. The only house type that isn't plaster or stone.
- **New:** Wall_Log family (A13), Shingle texture (A4), Gable_Logs (A2), Chimney_Gable_1 (A9).
- **Reuses:** Roof_Mid/Gable (shingle variant), Prop_Woodpile, Stump, Log_Fallen.
- **Numbers:** walls 2.6, so the ridge is 6.79. The external chimney top is 7.8. Keep `SM_VK_Porch` off cabins: its roof (top 3.15 at the wall) intersects the 2.6 m eave.

### 3.4 Longhouse (tier 1–2, farm)
- **Role:** early communal housing (2 families) with a byre end for 4 animals.
- **Look:** a 15 m-long, low, hip-ended thatch "loaf" (17.7 m including the eave overhang). The lowest, longest silhouette in the kit, contrasting with vertical townhouses.
- **New:** Wall_Shed_Wide for the byre door; RoofThatch_Vent ×2.
- **Reuses:** Wall_Wattle / Wall_Shed, RoofThatch_Hip ×2, RoofThatch_Mid ×3, Prop_Fence paddock (3×3 cells), Prop_Trough, Prop_HayBale.
- **Numbers:** walls 2.2, ridge 6.39.

### 3.5 Cottage variants (tier 2, extends `build_house_v`)

Each option is S, and together they give cheap variety:

| Option | Chance |
|---|---|
| Chimney_Gable | 0.30 |
| HalfHip ends | 0.25 |
| Thatch Eyebrow on thatch roofs | 0.35 |
| CrossGable on the front bay | 0.20 (only when n ≥ 3) |
| Gallery on the back first floor | 0.15 |
| PlasterUp instead of timber (for plaster-ground houses) | 0.30 |

Plus Slate and Shingle in the roof pool, and new plaster tints `Sage` (0.90, 1.02, 0.84) and `Sky` (0.88, 0.97, 1.12).

### 3.6 Rowhouse terrace (tier 3, urban)
- **Role:** dense housing on the market streets; shop ground floors add commerce slots.
- **Look:** a continuous street wall of colour blocks. Unit ridges step up and down, and party walls with chimney stacks punctuate the roofline.
- **New:** Gable_Party, Chimney_Party, PlasterUp, Wall_*_Shop, Wall_Passage.
- **Reuses:** all ground, timber and roof pieces; Awning; Prop_FlowerBox; Sign_*.
- **Footprint:** units 1–3 cells of frontage × 2 deep; terraces of 4–6 units (8–12 cells).
- **Effort:** M for the generator.

```
def build_terrace(coll, x0, x1, yroad, side, seed, district="market"):
    prev = None; x = x0
    while x < x1:
        w = r.choice([1,2,2,3]); st = random_style(seed, district)
        while prev and st["plaster"] == prev.style["plaster"]: reroll plaster
        stories = r.choice([2,3,3,4])
        if prev and stories == prev.stories and r.random() < 0.6: stories += r.choice([-1,1])
        front = shopfront_pattern(w)          # e.g. "SD", "DS W"; one 'P' passage every ~4 units
        own_left = (prev is None) or (stories > prev.stories)   # taller unit owns the shared wall
        ends = ("party" if prev else r.choice(["gable","halfhip","stepped"]), "party")
        build_block(..., n=w, stories=stories, faces={"F":front}, ends=ends,
                    skip_walls=() if own_left else {"L"})
        if prev and prev.stories != stories: place Wall_StoneUp/PlasterUp on exposed end-wall storeys of the taller unit
        if prev and r.random() < 0.5: place Chimney_Party at the shared wall ridge
        every 2nd unit: Banner_Wall or Awning (district colour)
        x += w*CELL; prev = unit
```

The unit that owns a shared wall places it; the other skips it, which avoids z-fighting. Where both units have the same height, the non-owner ends in `Roof_Mid`, which butts against the owner's party parapet (it stands 0.3 above the roof and hides the seam).

### 3.7 Gable-front townhouse (tier 3)
- **Role:** merchant or craftsman house on the plaza and main street.
- **Look:** a steep 6 m-wide gable to the street, with a hoist, oriel and shop. A row of them gives the classic sawtooth skyline.
- **Build:** `build_block(n=3, stories=3, rot=90)`. The street face is the end face "R": ground "SD", first floor Oriel + Window, second floor Window + Window. `ends=("gable","hoist")`.
- **New:** Gable_Hoist; the shop front.
- **Reuses:** Wall_Timber_Oriel, Wall_Timber_*, Balcony, Sign_*.
- **Footprint:** 2 wide × 3 deep. **Effort:** S.

### 3.8 Corner house (tier 3–4)
- **Role:** anchor at street intersections.
- **Look:** an L-house with a two-storey oriel turret on the convex corner (cone tip 14.2 m, above the 12.8 m ridge), shop fronts on both streets and a banner on the corner.
- **Build:** `build_L_v(a=1, b=1, stories=3)` plus Turret_Corbel, Turret_Seg ×3 and Turret_Cap at (−3, −3) offset (−0.45, −0.45).
- **New:** Turret stack, shop front. **Effort:** S.

### 3.9 Stone merchant house (tier 4)
- **Role:** wealthy trader; storage bonus from the hoist and cellar.
- **Look:**
  - All-stone storeys.
  - Stepped gables on both ends and a slate roof.
  - A cross gable with hoist on the street front, a shop front, and twin windows on the first floor.
  - A cellar hatch, and a guild banner in a cloth colour.
- **Build:** 3×2 cells, 3 storeys: Wall_Stone ground, then StoneUp_Twin / StoneUp_Window. Roof Slate, `ends=("stepped","stepped")`, `breakers=[("cross_hoist",1)]`.
- **New:** A1, A2, A3, A6. **Reuses:** Wall_Stone_Door, Corner_Stone, Roof_Mid.
- **Height:** 12.8 ridge + 0.9 steps. **Effort:** S once Tier A is in.

### 3.10 Tower house (tier 4, minor noble or defensive farmstead)
- **Role:** defensive housing; raises nearby "safety"; landmark for the noble or border district.
- **Fortified version:**
  - 2×2 cells, 4 storeys of stone, wall top 11.4. Door on the first floor, reached by Stair_Stone (tells you "defensive").
  - Parapet and 4 Bartizans (cone tips about 15.0). Roof_Pyramid_6 inside the walkway, apex 14.5. Banner_Roof pole, +3 m.
- **Domestic version:** 2 × Roof_Hip on a 2-cell block forms a true pyramid (apex 15.6), plus a corner turret.
- **New:** A1, A10. **Reuses:** Wall_Stone_Door, Corner_Stone, Roof_Hip. **Effort:** M.

### 3.11 Manor house (tier 5)
- **Role:** leader or lord residence; district-level landmark; unlocks noble-tier gameplay.
- **Layout:**
  - Main hall: 5×2 cells, 2 storeys, StoneUp_Twin windows.
  - Two 2×2 wings joined with 2 × Roof_LCorner (U-plan).
  - Stair turret r = 1.4 in one inner corner (top about 15.4).
  - Walled forecourt 5×3 cells: LowWall + `SM_VK_LowWall_GateArch` (a single-cell arched gate using `arch_ring`), with `SM_VK_Deco_Hedge` (3.0 × 0.8 × 1.2 trimmed box of FOLIAGE clumps via `make_bush` logic, plus a 4.243 diagonal) parterre.
  - Fountain, banners in a Purple cloth variant (0.35, 0.12, 0.45).
- **Effort:** L.

---

## 4. Water features (the biggest missing storytelling layer)

These depend on the terrain track's water tiles, at the levels in section 1.6. Boats and floating pieces have their origin at the water surface (−0.6).

| Feature | Footprint (cells) | Effort |
|---|---|---|
| Wooden trestle bridge | 2+ × 1 | M |
| Stone arch bridge (landmark) | 4 (1 span) or 6 (2 spans) × 1.5 | M |
| Log footbridge | 1–2 | S |
| Dock / pier set | modular 3×3 | M |
| Boats (rowboat, barge) | — | M |
| Quay set | contour | S–M |
| Watermill (landmark) | 3×2 + wheel cell | M |
| Fishery | 2×1 hut + dock | S–M |
| Lavoir (washing place) | 2×1 | S |
| Wall fountain / hand pump | wall-mounted / 1×1 | S |

### 4.1 Wooden trestle bridge
- `SM_VK_Bridge_Wood_Mid` (3.0 along x): deck at +0.35 (planks across, 3.0 between rails, 3.4 overall), 5 stringers 0.2 × 0.3. Trestle bent at x = 0: 3 piles r 0.14 from −2.5 to the deck, X-brace, cap beam 3.6 × 0.3 × 0.3. Rails: posts every 1.5 m, 1.05 high, top and mid rail.
- `SM_VK_Bridge_Wood_End` (3.0): ramp +0.05 → +0.35 with a stone abutment (`boulder()`/`rock()`) 3.4 wide × 1.2 deep facing the water, rails flaring 0.3 outward.
- A 2-cell river is End + End; a 3-cell river is End + Mid + End.
- Road width matches `road_strip` (3.2–3.4).

### 4.2 Stone arch bridge
- `SM_VK_Bridge_Stone_Span` (6.0 m module): 4.5 m clear span plus a 0.75 m half-pier at each end.
  - Segmental intrados springing at −0.6 with apex +0.8 (rise 1.4, R = 2.51).
  - ASHLAR voussoirs via `arch_ring` adapted to the XZ plane, 0.45 deep.
  - Deck crown +1.3; parapets 0.8 high × 0.35 with ASHLAR coping.
  - Chaining spans creates 1.5 m piers; add pointed cutwaters (`_Pier_Cut` ends) from −1.5 to the springing.
- `SM_VK_Bridge_Stone_Ramp` (3.0): deck +1.2 → 0.0 (22°), with a newel block 0.6 × 0.6 × 1.1. If colonist pathing needs gentler slopes, add a 6 m `_Ramp_Long` (11°).
- Totals: 1 span is 12 m (4 cells), 2 spans are 18 m.
- A landmark; a Lantern on each newel adds night reading.

### 4.3 Log footbridge
`SM_VK_Bridge_Log`: a single squared log r 0.3 × 4.5 with a pole handrail on one side. Pairs with the existing `Rock_StepStones` for streams.

### 4.4 Dock / pier set
| Piece | Spec |
|---|---|
| `SM_VK_Dock_Deck` | 3×3, top at +0.25, planks 0.3 along x, 4 piles r 0.14 at (±1.35, ±1.35) from −2.5 to +0.55. Doubled piles at seams read as a real pier. |
| `SM_VK_Dock_Edge` | Plus a fender log r 0.12 along −Y at +0.05, and 2 bollard piles to +0.9 with rope rings (`ring()`). |
| `SM_VK_Dock_Ladder` | Down to −1.4. |
| `SM_VK_Dock_Crane` | 0.35 post, 5.5 m; jib 3.2 at 4.8 with a brace; rope, hook and hanging crate. A small landmark. |

`Wall_Posts_Shed` with an S roof on top of a deck makes a boathouse.

### 4.5 Boats
- `SM_VK_Prop_Rowboat` (4.2 × 1.35 × 0.55): hull lofted from 7 U-sections of 5 vertices, sheer +0.15 at bow and stern, PLANKS with UVs along the length. 2 thwarts, 2 oars. A painted gunwale strip in the **SHUTTER slot**, so boats pick up the district's shutter palette for free.
- `SM_VK_Prop_Barge` (7.5 × 2.6 × 0.8): raked square ends, 5.5 m mast with a furled CLOTH_B sail and yard, cargo of crates, barrels and sacks, steering oar.
- Unity side: gentle bob animation.

### 4.6 Quay set (the town's water edge)
- `SM_VK_Quay_Straight` (3.000) / `_Diag` (2.121) / `_Post` (contour pieces): ASHLAR coping 0.5 wide at z = 0, STONE face down to −1.5, ROCK_MOSSY wet band from −0.6 to −1.5, IRON mooring ring every 3 m.
- `SM_VK_Quay_Stair`: 4 steps of 0.15 down along the face to −0.6.

### 4.7 Watermill (landmark, animated)
- **Role:** grinds grain (a windmill alternative, placed on rivers); can power a sawmill frame saw.
- **Look:** a 3×2 house (stone ground floor, timber upper, red roof) with a turning 4.8 m wheel over the water.
- **New pieces:**
  - `SM_VK_WaterWheel`: R 2.4, width 1.0, two `ring()` rims, 8 spokes per side, 16 paddles 1.0 × 0.08 × 0.5, hub r 0.35, axle r 0.15 × 1.8.
  - `SM_VK_Wall_Stone_Axle`: Wall_Stone with a bearing block and axle hole at z 1.3.
  - `SM_VK_Mill_WheelPier`: 0.8 × 1.0 stone pier from −1.5 to +1.5, the outer bearing.
  - `SM_VK_Prop_Millstone`: lathe disc r 0.65 × 0.3, ROCK; can lean against walls.
- **Overshot variant:**
  - `SM_VK_Flume_3` / `_45`: 3 m trough 0.7 × 0.45 of planks, WATER quad 0.1 below the rim, A-frame trestle to −H. Fed from a terrain level 2–3 LVL higher.
  - `SM_VK_Flume_Spout`: WATER sheet card falling about 1 m (UV scroll in Unity).

```
build_block(n=3, stories=2, style=st, faces={"R":"A."})     # 'A' = Axle wall on the water end
wx = 4.5 + 0.25 + 0.6 + 0.5                                  # wall line + half wall + gap + half wheel width
o = place_v(coll, "SM_VK_WaterWheel", wx, -1.5, 1.3, 90, origin, {}); o["spin_axis"]="local X"; o["rpm"]=6
place_v(coll, "SM_VK_Mill_WheelPier", wx+1.0, -1.5, 0, 90, origin, {})
```

- The wheel bottom sits at −1.1, dipping 0.5 m into the water.
- **Reuses:** walls, roofs, Prop_Sacks, Prop_Cart, Prop_Crates.

### 4.8 Fishery
- **Hut:** 2×1 cells, Wall_Shed with RoofS (A0), on Dock_Decks or the bank.
- **Props:**
  - `SM_VK_Prop_FishRack`: A-frame poles 3 m, 2 rows of STEEL flattened-ico fish.
  - `SM_VK_Prop_NetDrying`: 2 posts 2.4 m + a 3 × 1.8 NET alpha card (`lattice()` texture, `alpha_clip`) with BREAD cork floats.
  - `SM_VK_Prop_Creels`: lathe wicker baskets, HAY.
- Rowboat moored. Fish emblem on the ridge.
- **Effort:** S–M.

### 4.9 Lavoir (washing place): a vignette
- 2×1 cells: `Wall_Posts_Shed` + `Corner_Posts`, RoofS pieces.
- Basin: ASHLAR curb 5.4 × 2.0 × 0.45 with WATER at 0.3, and ASHLAR washing slabs tilted 20° on the rim.
- 4 × `SOCK_Work`. Existing `Prop_Laundry` alongside, plus `SM_VK_Prop_WashBasket`.
- **Effort:** S.

### 4.10 Wall fountain and hand pump
- `SM_VK_Prop_WallFountain` (wall-local): ASHLAR back slab 1.2 × 0.25 × 1.8, BRONZE spout, half-lathe basin r 0.8, water stream card.
- `SM_VK_Prop_HandPump`: 1.4 m WOOD/IRON pump + small trough.

---

## 5. Economy and production buildings

The emblem, hero colour and yard object are what make each building's function readable from above.

| Building | Role | Footprint | New pieces | Reuses | Emblem / hero | Effort |
|---|---|---|---|---|---|---|
| **Woodcutter's lodge** | wood | cabin 2×2 + yard 2×2 | LogPile_1-3, ChoppingBlock, SawHorse | Wall_Log set, Woodpile, Stump | axe / log pile | S |
| **Sawmill / lumber yard** | wood → planks | 3×2 open shed + yard 3×2 | `Prop_SawPit` (1 × 4 VOID pit, log on trestles, 2 `SOCK_Work`), `Prop_FrameSaw` (2 × 3 frame, water variant next to the wheel), PlankStack_1-3 | Wall_Posts_Shed, Wall_Shed, Roof (shingle) | saw / plank stacks | M |
| **Mason's yard + treadwheel crane** | stone → blocks; construction | yard 3×3 + S-roof shed 2×1 | StoneBlocks_1-3, `Prop_Banker` (bench), `Prop_TreadwheelCrane` (wheel Ø 3.6 × 1.2 from two `ring()` + treads, A-frame 5.5, jib 7 m at 40°, hook with block, `SOCK_Spin`) | Wall_Posts, Rock_Pebbles | hammer and chisel / **crane (9 m, landmark, reused on big build sites)** | M |
| **Quarry** | stone | on cliff tiles | `Quarry_Face_Straight/_Diag` (contour, height 3.0 = 2 LVL; flat-cut ROCK steps with tool marks), `Prop_QuarrySled` | crane, StoneBlocks, `boulder()` | — / pale cut faces | M |
| **Mine adit + rails** | ore | 1×1 portal + rails | `Mine_Portal` (posts 0.3, lintel 3.2, VOID tunnel 2.4 × 2.6 × 3; wrapped in a 5-boulder mound so it also works on flat ground), `Rail_Straight/_Curve (r 3.0)/_Diag` (gauge 0.8, 6 sleepers), `Prop_MineCart`, OrePile_1-3 | Lantern, Crates | pick / ore glints | M |
| **Charcoal + bloomery** | fuel, iron | 2×2 yard | `Prop_CharcoalClamp` (earth dome r 1.8 h 1.4, 6 `SOCK_Smoke`), `Prop_Bloomery` (clay stack Ø 1.2 → 0.6, 2.2 h, GLOW mouth, bellows) | LogPile, Anvil | — / **smoke columns** | S–M |
| **Tannery and dye works** | hides → leather; cloth colouring | house 3×2 + yard 3×3 (near a stream) | `Prop_DyeVat` (r 0.7 h 0.8, liquid in the CLOTH_A slot so the style cloth colour drives it), `Prop_ClothRack` (posts 3.2 m, poles at 2.2 / 2.6 / 3.0, 6–8 strips 0.5 × 2.0 in cloth colours), `Prop_HideFrame` (1.4 × 1.8), `Prop_TanPit` | house pieces, Prop_Trough | scissors / **the most colourful place in the village** | M |
| **Weaver / cloth hall** | cloth | 2×2 + shop front | `Prop_Loom` (1.6 × 1.2 × 1.6, warp-thread cards), `ShopGoods_cloth` | Gallery (loom on the gallery), Awning | shuttle or scissors / bolts | S |
| **Brewery with oast kiln** | ale | house 3×2 + kiln 1.5×1.5 | `SM_VK_Kiln_Oast` (round r 2.2, 5.0 m stone walls, cone h 3.6 in slate/red, white PLASTER cowl 0.8 × 0.8 × 1.0 with slanted top + vane, top 10.6), `Prop_MashTun` | BarrelStack, Crop_Hops | tankard / **white cowl silhouette** | M |
| **Granary** | food storage | 2×2 | `Prop_StaddleStone` (lathe stem r 0.25 → 0.18 h 0.6 + cap r 0.4; 9 in a 3×3 grid at the cell corners), `Prop_GranaryStep` (detached steps, so rats can't climb) | Wall_Shed raised to z 0.75, Roof thatch/shingle | sheaf / house on "mushrooms" | S |
| **Warehouse** | bulk storage | 4×3 (L roof) | — | StoneUp_Loading stacked in one bay, Roof_Gable_Hoist, RoofL, Crates, Sacks | key / hoist | S |
| **Smokehouse** | preserved food | 1×1 (RoofS_Single) | — | Wall_Stone, Roof_Vent, 2 × `SOCK_Smoke` at the eaves | — / smoke | S |
| **Butcher** | meat | 2×2 | `ShopGoods_meat`, hanging hams | shop front, Awning | cleaver / red awning | S |
| **Herbalist** | healing | 2×2 + herb garden | `Prop_HerbBundles` (5 bunches on a pole under the eaves), `ShopGoods_bottles` (STAINED lathe bottles) | Sign_Potion, GardenBed, Crop_Lavender | mortar and pestle | S |
| **Dovecote** | food; farm landmark | 1.5×1.5 | round r 2.0, 5.0 m walls, 3 rows of pigeon holes (VOID 0.15 × 0.2), cone h 3.0 + small open lantern, 8.5 m | — | — / white birds on the roof | S–M |
| **Apiary** | honey, wax | 1×1 | `Prop_BeeSkep` (lathe straw dome r 0.3 h 0.45, HAY coils), bee shelter (2 posts + mini roof) | Bench | — | S |
| **Pigsty / sheepfold** | animals | 2×2 | — | LowWall pen, LeanTo_Thatch, Trough | — | S |
| **Tithe barn** | farm landmark and storage | 5×3 | `SM_VK_Buttress` (stepped stone 0.6 × 1.2 × 3.0) | build_barn with RoofL (ridge 4.2 + 6.1 = 10.3), Wall_Barn | — / huge roof | S |
| **New crops** | farming variety | 1 plot each | `Crop_Hops` (4×4 poles 4.5–5 m with twine and vine cards; vertical texture), `Crop_Vines` (1.4 m trellis rows, dark grapes), `Crop_Flax` (blue flowers 0.35, 0.5, 0.95), `Crop_Sunflower` (2 m, yellow discs facing south) | `soil_bed`, `crop_rows`; new cells in the `gen_crops` atlas | colour fields | S each |

---

## 6. Civic features and street life

| Feature | Role | Look and numbers | New / reused | Footprint | Effort |
|---|---|---|---|---|---|
| **Market hall** | market building for bad weather; landmark | Ground floor open on stout Wall_Posts (0.35 posts on 0.6 pads) with Ceiling_Cell. Upper timber storey. Roof_Hip at both ends, Roof_Cupola (existing) in the middle, about 13.5 m. Stalls, tables and goods inside on ASHLAR paving. 4 Banner_Wall. | A5 + Wall_Timber_*, Roof_Hip, Roof_Cupola, Prop_Table, Crates, Sacks | 4×2 (or 4×3 with RoofL) | S–M |
| **Market cross** | plaza centrepiece | 3 octagonal ASHLAR steps (r 1.8 / 1.4 / 1.0 × 0.3, lathe with 8 segments), tapering shaft 3.5 m, small gabled tabernacle head, 5.3 m total | new | 1×1 | S |
| **Maypole and festival green** | festival, happiness | Lathe pole 9.0 m in CLOTH_A/B bands. Wreath at 7.0 (`ring()` LEAVES + PINK/YELLOW icos). 8 ribbon cards 0.08 wide from 7.0 to stakes at r = 3.2, sag 0.3, cycling cloth colours: **a coloured star from above**. Bunting between lamp posts. | Prop_Bunting, Bench, Table, Festoon, LampPost | 4×4 | S |
| **Coaching inn** | lodging, trade hub | U around a 3×3 yard. Street range 4×2, 3 storeys, with a Wall_Passage in the middle. Two 3×2 side wings with stacked Galleries facing the yard. Stable range at the back (build_stable). Well, Cart, Trough, bunting in the yard. Tankard emblem. | A7, A15, Roof_LCorner, TavernSign | 6×6 | M |
| **Barracks and training yard** | defence training | 4×2, 2 storeys. Fenced 4×3 yard with `Prop_ArcheryTarget` (straw disc r 0.6 × 0.3 on an A-frame; rings YELLOW / CLOTH_A / CLOTH_B / blue cloth, readable from above) and `Prop_TrainingDummy` (post, crossbar, BURLAP head, CLOTH_A shield). Banner_Pole in faction colour. | WeaponRack, BarrelStack, Fence | 4×5 | M |
| **Guild hall** | prestige, guild policies | Stone merchant house scaled to 4×3 with the L roof. Stepped gable facing the plaza, 2 cross gables, 4 Banner_Wall, guild emblem on the ridge. | A1–A3, A11 | 4×3 | S |
| **Wayside shrine** | faith coverage at crossroads | Stone pillar 0.5 × 0.5 × 1.6, mini gabled niche roof 0.8, candle GLOW, flowers | new | 1×1 | S |
| **Stocks / pillory** | law, storytelling | 2 posts, holed plank, bench | new | 1×1 | S |
| **Yard clutter pack** | backyard life | `Prop_Privy` (1.2 × 1.2 × 2.2 plank box, pent roof, crescent-moon VOID in the door), `Prop_RainBarrel`, `Prop_Compost`, `Prop_Kennel` | `barrel()`, Wall_Shed logic | — | S |
| **Hedges and field walls** | field boundaries on the grid | `Deco_Hedge` 3.0 / 4.243, `LowWall_Diag` 4.243 | LowWall, `make_bush` clumps | — | S |

---

## 7. Defence and landmarks (edge and progression)

These pieces are grid-drawn, so each set has Straight 3.000, Diag 4.243 and joint pieces at cell corners.

| Set | Pieces | Numbers | Effort |
|---|---|---|---|
| **Palisade (early game)** | `Palisade_Straight` (11 logs), `_Diag` (16 logs), `_Post`, `_Walk` (fire-step), `_Gate` (open/closed), `_Tower`, `Prop_Beacon` | Logs r 0.13 at 0.27 spacing, 3.3–3.8 m (seeded), 0.35 m sharpened cone tips, sunk to −0.4. 2 rails behind at 0.8 / 2.6 with BURLAP lashings. Fire-step planks at 1.8, 0.9 wide. Gate: two 1.5 m log leaves with Z-brace, 0.22 frame posts, walkway lintel. Tower: 3×3 platform on 4 log posts at 4.5, railing, shingle pyramid (4-segment cone r 2.6 h 2.2), ladder, about 8.5 m. Beacon: IRON basket on a 5 m pole, GLOW + smoke. | M |
| **Stone town wall** | `TownWall_Straight`, `_Diag`, `_Stair` (inner face), `_RuinEnd`, `TownWall_Tower_Round`, `TownWall_Tower_D` | Wall 1.6 thick, walk at 5.0, A10 Parapet above (merlons to 6.7), 1.2 m walkway, 0.2 outer batter, **foundation skirt to −1.5** so it runs down one terrain level without floating. Round tower Ø 5.4, 9 m walls, cone 4 m (14.5 m, landmark), slits via the StoneUp_Slit logic. | L |
| **Gatehouse** | `SM_VK_Wall_Gate_6` (6 m, 2-cell module: 3.4 × 4.2 arch centred between cells, portcullis IRON grid half-raised, wooden gates open), 2 half-round flanking towers r 2.0 | Block 2×2 cells, 3 storeys (wall top 8.6) + parapet. Towers to 10.0 + cones to 14.0. Timber hoarding optional (reuse the `guard_tower` hoarding code). Banners over the arch. | M–L |
| **Keep** | uses A1, A8, A10 | 3×3 cells (9×9), 5 storeys: walls 14.2, parapet 15.1, Roof_Pyramid_9 apex 19.3, 4 bartizans, r 1.4 stair turret to about 21, flagpole to about 25. The tallest thing in the village, so it should sit on the highest terrain level. | L |

---

## 8. District recipes (weight tables for `random_style(seed, district)`)

Each district gets a distinct overall read of roof colour, height and silhouette.

| District | Ground | Upper storeys | Storeys | Roof material | End types | Orientation | Breakers / dressing | Cloth & shutters |
|---|---|---|---|---|---|---|---|---|
| **Fringe** (farm edge) | Wattle .5 / Log .3 / Stone .2 | — | 1 (.85), 2 | Thatch .75 / Shingle .25 | hip .55, halfhip .25, cruck .2 | eave | vents, wattle fences, chickens, gardens | Natural / Green |
| **Craft** | Stone .7 / Plaster .3 | Timber .8 / PlasterUp .2 | 1–2 (2: .7) | Red .35 / Green .2 / Shingle .2 / Slate .15 / Thatch .1 | gable .5, hip .2, halfhip .2, hoist .1 | eave .8 | Chimney_Gable .35, Roof_Vent .4, stock-pile yards | Red / Teal |
| **Market** | Plaster .45 / Stone .25 / Shop .3 per cell | PlasterUp .45 / Timber .55 | 2–4 (3: .5) | Red .35 / Blue .3 / Slate .25 / Green .1 | party (terraces), stepped .2, hoist .3 | gable-front .45 | CrossGable .25, turrets on corners, Gallery .15, banner every 2nd unit, bunting | all four cloth colours |
| **Waterfront** | Stone .5 / Shed .5 | Timber .5 / Shed .5 | 1–3 | Slate .4 / Shingle .3 / Red .3 | hoist .4, gable .4, hip .2 | gable-front .3 | Gallery .3 on the water side, cranes, boats, nets | Blue / Natural |
| **Noble hill** | Stone 1.0 | StoneUp .7 / PlasterUp White .3 | 2–4 | Slate .5 / Blue .4 / Red .1 | stepped .5, halfhip .2, hip .3 | eave .6 | turrets .5, hedges, faction banners | Purple / Blue |

---

## 9. Roadmap

Each sprint ends with a re-render of `nature_town_aerial.png` from the same camera.

**Sprint 1, skyline:**
- A0 roof families + `_Single`; A1 StoneUp/PlasterUp; A2 gable kinds; A3 `roof_field` (HalfHip, CrossGable, TJunction); A4 Slate/Shingle; A9 chimneys and vents.
- `build_block()` and district styles.
- Houses: terrace, gable-front townhouse, stone merchant house, cottage variants.
- Retrofit identity pass (A11, emblems only).
- Test: a terrace street's skyline reads varied at the colony camera.
- Size: about 5 M + 8 S.

**Sprint 2, signage and life:**
- A11 full (banners, bunting); A6 shop fronts; A7 gallery; A8 turrets; A5 open bays; A15 passage; A12 construction stages + stockpiles.
- Features: corner house, market hall, market cross, maypole green, coaching inn.
- Size: about 5 M + 6 S.

**Sprint 3, water** (needs terrain water tiles):
- Wood and stone bridges, dock set, boats, quay, watermill + flume, fishery, lavoir, wall fountain.
- Size: about 6 M + 5 S.

**Sprint 4, humble tiers and economy:**
- A13 walls → camp, hovel, cabin, longhouse.
- Production: woodcutter, sawmill, mason yard + treadwheel crane, granary, tannery/dye works, brewery + oast, smokehouse, herbalist; farm set (dovecote, apiary, crops, tithe barn).
- Size: about 6 M + 12 S.

**Sprint 5, edges and landmarks:**
- A10 fortification set, A14 terrain civil pieces.
- Palisade, tower house, town wall, gatehouse, keep, manor.
- Quarry and mine (need cliff tiles).
- A16 jetty, if there's time.
- Size: about 3 L + 5 M.

**Top 10 by visual impact per effort:**
1. A0 + A4 (scale and roof colour everywhere).
2. A2 + A9 (skyline).
3. Terrace / gable-front generator.
4. Water set (bridges, dock, boats, watermill).
5. Ridge emblems + banners.
6. Turrets + cross gables.
7. Construction stages + stock levels.
8. Palisade → town wall + gatehouse.
9. Dye works + maypole + market hall.
10. Tower house / keep.

---

## Appendix A: new material slots and textures

**New slots:** append to the end of `kit_mats()`, starting at index 45 (after `MUSH_GLOW`), so all existing piece material indices stay valid.

| Index | Name | Source |
|---|---|---|
| 45 | `WATTLE` | `T_VK_Wattle` from `weave()` |
| 46 | `NET` | `lattice()` + alpha, `alpha_clip=True` |
| 47 | `GOLD` | flat (0.95, 0.70, 0.22), roughness 0.3; for emblems and vanes |
| 48 | `LEATHER` | flat (0.45, 0.25, 0.12) |
| 49 | `CANVAS` | optional; otherwise CLOTH_B with vertex-colour patches |

**New variant entries:**

| Kind | Name | Value |
|---|---|---|
| `roof` | Slate | `T_VK_RoofSlate` |
| `roof` | Shingle | `T_VK_RoofShingle` |
| `plaster` | Mud | (0.80, 0.64, 0.46) |
| `plaster` | Sage | (0.90, 1.02, 0.84) |
| `plaster` | Sky | (0.88, 0.97, 1.12) |
| `cloth` | Purple | (0.35, 0.12, 0.45) |
| `cloth` | White | (0.92, 0.90, 0.85) |

Boats and doors reuse the `shutter` slot for paint. Dye vats, banners and ribbons reuse the `cloth` slot.

**Other atlas work:** `gen_crops` needs new cells for hops, vine, flax and sunflower. `gen_foliage` needs a trimmed-hedge clump cell.

## Appendix B: finish() flags to watch

- **`grime=False`** for any piece placed above ground or starting mid-height: StoneUp, PlasterUp, Turret_*, Parapet, Scaffold, Gallery, Emblems.
- **`wobble=False`** for any piece not 3 m-periodic in x: all `_Diag`, 6 m gate/bridge spans, 2.121 contour pieces, round towers, boats.
- **Below-ground geometry:** piles, podiums and skirts will get the 0.62 grime floor, which is fine, and it reads as a wet line on water pieces.