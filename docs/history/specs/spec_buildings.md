 |
| Prop_ShopGoods_{Bread, Produce, Cloth, Pots, Tools, Meat, Candles, Fish, Boots, Bottles} | each fits within 2.0×0.5×0.45 on the counter. Bread and Produce reuse the `market_stall` goods code. Cloth: 3 CLOTH_A bolts r 0.09 × 0.5, so the style recolours them. Pots: CLAY lathes. Meat: APPLE / PIGSKIN hams. Candles: PAPER + GLOW. Fish: STEEL. Bottles: STAINED | ng |
| Roof_Pent | origin at the wall face (0, −0.3, 0). ROOF slab 3.2 × 1.5 (out) × 0.08, sloping down at 22° (outer edge at −0.6); WOOD fascia; 2 three-box curved brackets at x ±1.2, running from (−0.3, −0.9) to (−1.2, −0.4) | nw |
| Wall_Stone_Passage (+ `_Gated`) | arch hw **1.2**, spring **1.4**, crown **2.6** (ring top 3.0), using `arch_cut_panels`, `arch_ring(n=9)` and `arch_soffit`; plinth split; cobble strip. `_Gated`: 2 PLANKS leaves 1.2×2.5 open 100° | std; Door ±0.9 |
| Passage_Vault | placed at house-local y 0 between the front and back passage walls. `arch_soffit(1.2, 1.4, y −2.75..2.75, STONE)`; PLASTER side walls x ±1.2..±1.45, z 0–1.4; cobble floor 2.4×5.5 | ng |
| Wall_Arcade_Open | `wall_arcade()` without the loggia floor, ceiling, back facade and lantern | ng |
| Gallery_Timber / Gallery_End | PLANKS deck 3.0×1.3×0.08 with its top at H1, y −0.30..−1.60; joists every 0.75; post 0.22² at (−1.5, −1.5) from z 0 to 4.05; knee braces; handrail at H1+1.0, bottom rail at H1+0.12, balusters r 0.03 every 0.2. `_End` adds the post at +1.5 and a side rail | nw |
| Gallery_Top | top storey only. Deck 3.0×1.0×0.1 at the storey base, y −0.45..−1.45; 2 brackets 0.9 at 45°; post 0.18² at (−1.45, −1.35), 2.1 high (its top is 0.70 below the wall top; the eave underside at ay 4.35 is −0.64); rails at 1.0 and 0.15; balusters 0.06 every 0.2 | nw |
| Turret_Corbel / Turret_Seg / Turret_Seg_Stone / Turret_Cap | axis at corner-local (**−0.6, −0.6**), **r 1.1**, 12 sides. Corbel: lathe [(0.2, −1.2), (0.45, −0.9), (0.7, −0.6), (0.9, −0.3), (1.1, 0)] with ASHLAR rings; its top sits at the first upper floor. Seg: H2 tall, PLASTER with 6 WOOD posts, sill and head rings, 3 WINDOW 0.5×1.0 facing −X/−Y. Seg_Stone: STONE with 1 slit. Cap: cone r 1.35 × h 2.8, bell-cast skirt of 0.3 at KICK, ROOF UVs as in `guard_tower`, WOOD finial 0.6 + BRONZE ball. **Stack:** one Seg per upper storey plus one above the wall top. On a 3-storey house the cap base is at 11.4 and the tip at 14.2 | nw |
| Corner_Party_Stone / Corner_Party_Timber | pilaster 0.30 (x) × 0.12 proud of the face (stone face −0.25, timber −0.40) × H1 or H2 | ng / nw |
| Roof_Mid_CapL / Roof_Mid_CapR | Roof_Mid with `end_caps=(True,False)` / `(False,True)` | nw |
| Roof_LCorner_Mirror | Roof_LCorner mirrored in X, with `reverse_faces` | nw |
| Roof_T | `roof_field`, x −3..3, y −EAVE..3. zfun = `roof_z(|y|)` for y ≤ 0, else `max(roof_z(|y|), roof_z(|x|))`. Eave tabs on −Y; ridge A from −3 to 3 and ridge B from 0 to 3. Neighbours: Roof_Mid at x = ±4.5 and Roof_Mid rot 90 at y = 4.5 | nw |
| Roof_X | `roof_field` on [−3, 3]²; zfun = `max(roof_z(|y|), roof_z(|x|))`; 4 valleys; ridges along both axes; Mid pieces on all 4 sides | nw |
| Roof_CrossGable / Roof_CrossGable_Hoist | replaces a Roof_Mid bay: x ±1.5, y −3.6..4.35. zfun = `roof_z(|y|)`, except for y ≤ −1.5, where it is `max(roof_z(|y|), 0.35+(1.5-|x|)*tan52)`. Cross ridge at 2.27; valleys from (±1.5, −3) to (0, −1.5). Timber triangle face at y −3.40 with a window 0.8×0.8 at z 0.55–1.35 (Hoist version: door 0.8×1.2 + beam + pulley + rope). **Eave stops:** WOOD 0.06 boards at x = ±1.5 following the neighbour eave, ay 3.0–4.35, from `roof_z(ay)+0.02` down to `roof_z(ay)-0.36` | nw |
| Roof_HalfHip / RoofThatch_HalfHip | drop-in for Roof_Gable (x −1.5..GX 2.45). zfun = `min(roof_z(|y|), roof_z(max(0, x)))`. The hip starts at 2.27 on the wall line, reaches the ridge at local x 0, and the creases are \|y\| = x. Gable wall = `gable_end` outline clipped by the hip underside (a trapezoid). Hip eave tabs (tile) or eave roll (thatch); rake rolls on the lower verges | nw |
| Roof_Mid_Hatch / Roof_Mid_Skylight | Roof_Mid plus a 1.0×1.0 WOOD frame centred at ay 1.7 on −Y. Hatch: PLANKS lid open 65° over VOID. Skylight: WINDOW 0.9² set 0.02 proud | nw |
| Roof_Bellcote | origin at the ridge apex. ASHLAR 0.9 (x) × 0.5 × 1.6; VOID arch hw 0.25, spring 0.8; `bell(k, 1.25, 0.22)`; 2 ROOF slabs 0.7×0.4 at 45° | nw |
| Stair_Stone_Ext | same run as `ext_stair`: 13 steps, rise 3.3, run 2.7, climbing +X to a landing at x 1.35–2.85, z 3.3. Solid ASHLAR wedge y −0.3..−1.4; VOID arch under the upper half (hw 0.6); parapet 0.3 × 0.7. About 50°, so Unity needs a NavMeshLink | ng; Door at the landing |
| Stoop_Stone | 3 ASHLAR steps 1.8 wide, rise 0.18, tread 0.35 (top 0.54); cheeks 0.3×1.05×0.6 | ng |
| Prop_CellarHatch / _Open | curb 1.5×1.3; slope from z 0.55 at y −0.3 to 0.10 at y −1.6 (25°); 2 PLANKS leaves 0.72×1.25 with IRON straps. `_Open`: one leaf rotated 160°, VOID well, 3 steps | ng |

Optional in M4, coordinated with the stone-texture track: `SLOT["stone"]=STONE` with tints Warm (1.06, 0.98, 0.88), Grey (0.92, 0.95, 1.00) and Dark (0.75, 0.75, 0.78).

### M5: water (4 days)

All heights use the water datum (bank 0, water −0.6).

| Piece | Geometry | Flags / sockets |
|---|---|---|
| Pier_Deck | 3×3, centred on the cell. Deck top +0.05. 13 planks 0.22 × 3.0 × 0.07 along X, 1 cm gaps, ±1 cm z jitter, one plank 0.4 short. Stringers 0.2×0.3 at y ±1.2. Cap beam along Y at x −1.5. Piles r 0.16 at (−1.5, ±1.35) from −3.0 to +0.35, lean ≤ 5°. X-brace at z −1.8..−0.35 | ng |
| Pier_End / Pier_Stairs / Pier_Rail | End: piles at (+1.5, ±1.35) + cap; 2 bollards (lathe r 0.18 × 0.5); ladder to −1.4; lantern pole (Light). Stairs: 1.5 wide, 4 steps from +0.05 to −0.55. Rail: posts 0.12² every 1.5, 1.0 high, rope sag 0.12 | ng |
| Prop_Rowboat / Prop_Barge | Rowboat 4.2×1.35×0.55: hull lofted from 7 U-sections of 5 vertices (bmesh bridge), sheer +0.15, PLANKS with UVs along the length; gunwale strip in the **SHUTTER** slot; 2 thwarts; 2 oars 0.06×2.4. Barge 7.5×2.6×0.8: square raked ends, 5.5 m mast, yard, furled CLOTH_B sail, crates, barrels, steering oar. Origin at the waterline | nw |
| Bridge_Wood_Mid / _End / _Bent | Mid: deck top +0.35, 12 planks 3.4 × 0.25 × 0.07 across; 5 stringers 0.2×0.3; posts 0.14² at x −1.5 and 0, y ±1.6, 1.05 high; top and mid rails. End: deck rises from +0.05 (bank) to +0.35; rock abutment 3.4 wide at x −1.5..−0.3; rails flare out 0.3. Bent: 3 piles r 0.14 at y −1.3, 0, 1.3 from −3.0 to 0.0; cap 3.6×0.3×0.3; X-brace. Placed at every seam between two bridge modules | ng |
| Bridge_Stone_Span (6 m) / _Ramp (3 m) / _Pier | Span: 4.5 m clear + 0.75 half-piers. Segmental intrados springing at −0.6, apex +0.8 (R 2.51). ASHLAR voussoirs 0.45 deep. Deck +1.2 at the ends, +1.3 in the middle; 3.2 between parapets 0.35 × 0.8 with coping 0.45×0.12. Ramp: deck from +1.2 down to 0.0 (21.8°); newel 0.6×0.6×1.1; wing walls 1.5 m splayed 30°. Pier: pointed cutwater 1.5 × 3.9 with 1.2 m noses, z −2.0..−0.6, at seams between spans | nw (6 m) |
| Bridge_Log | squared log r 0.3 × 4.5 + one pole handrail; pairs with `Rock_StepStones` | ng |
| Quay_Straight (3.0) / Quay_Diag (2.121) / Quay_Post / Quay_Stair | Face −Y toward the water. ASHLAR coping 0.5 × 0.25 at z −0.25..0. STONE face 0.9 thick from 0 down to **−2.0**. ROCK_MOSSY strip from −0.6 to −2.0. IRON ring `ring(0.1, 0.16)` at (0, −0.52, −0.4). Post: ASHLAR 0.6×0.6×0.9. Stair: 4 steps of 0.15 cut to −0.6, 1.2 wide | Straight ng; Diag, Post nw |
| WaterWheel (animated) | R 2.4, width 1.0; **axle along local X**. Rims `ring(2.15, 2.4, 0.12, axis X)` at x ±0.45; 8 spokes per side 0.12², r 0.3–2.2; 16 PLANKS paddles 1.0 × 0.5 × 0.08 at r 2.1–2.6; hub r 0.35 × 1.1; axle r 0.15 from x −1.1 to +1.2. Origin at the hub; `spin_axis="local X"`, `rpm=6` | nw; Spin |
| Wall_Stone_Axle / Mill_WheelPier / Prop_Millstone | Axle wall: Wall_Stone + ASHLAR bearing 0.6×0.3×0.6 at z 1.3 + VOID disc r 0.2. Pier: STONE 0.8×1.0, z −1.5..+1.5, ASHLAR bearing at 1.3. Millstone: lathe r 0.65 × 0.3 with an eye ring | std / ng |
| Prop_NetRack / Prop_FishRack / Prop_Creels / Pile_Fish_1–3 | Net rack: 2 posts 2.4 + NET card 3.0×1.8 with BREAD floats. Fish rack: A-frame 3 m, 2 rows of STEEL flattened icos. Creels: HAY lathe baskets. Pile_Fish: crates of STEEL fish | ng |
| Prop_LavoirBasin / Prop_WallFountain / Prop_HandPump | Basin: ASHLAR curb 5.4×2.0×0.45, WATER at 0.3, 4 slabs tilted 20° (4 × Work). Wall fountain: back slab 1.2×0.25×1.8, BRONZE spout, half-lathe basin r 0.8, WATER stream card. Hand pump: 1.4 m WOOD/IRON pump + trough | ng |

### M6: production props (5 days, all ng unless noted)

| Group | Pieces and key numbers |
|---|---|
| Quarry | `Quarry_Face_Straight` (3.0) / `_Diag` (2.121, nw) / `_Corner`: 3.0 high = 2 LVL; 2 benches, each 1.5 high × 0.8 deep; ROCK blocks with jitter 0.02 and flat cuts; VOID drill lines 0.02×0.6; 6 rubble rocks at the foot. `Quarry_Floor`: 3×3 ROCK slab, a split block, 3 IRON wedges. `Prop_QuarrySled`, `Prop_Banker` (ASHLAR 1.2×0.6×0.8 + half-carved lathe drum) |
| Crane | `Prop_TreadwheelCrane`: A-frame 5.5, jib 7.0 at 40°, hook + ASHLAR 0.8×0.6×0.5. Wheel is a separate object: 2 × `ring(1.6, 1.8)` 1.2 apart + 16 treads; `spin_axis="local Y"`. Landmark at 9 m |
| Clay | `Prop_BottleKiln`: lathe [(2.2,0),(2.3,1.5),(2.0,3.5),(1.1,5.0),(0.8,6.0)], 16 segments, CLAY, GLOW stoke hole (Smoke, Fire). `Prop_ClayPit`: CLAY quad 3×3 at z 0.01 + WATER puddle + spade. `Prop_PottersWheel`. `Pile_Bricks_1–3` (CLAY 0.25×0.12×0.07 stacks) |
| Mine | `Mine_Portal`: posts 0.35 × 3.0, cap 3.6; 3 timber sets 0.8 apart into a VOID tunnel 2.5 × 2.6 × 3.0; plank lagging; lantern; 5-boulder mound (`boulder()`), so it also works on flat ground. `Rail_Straight` (3.0), `Rail_Curve` (r 3, 90°), `Rail_Diag` (4.243, nw), `Rail_End`: STEEL rails 0.05×0.07 at gauge 0.8, 6 sleepers 1.2×0.18×0.1. `Prop_Minecart`: 1.2×0.8×0.6, 4 wheels r 0.15, ore heap. `Pile_Ore_1–3`: flattened jittered ico r 0.8 / 1.1 / 1.4, z-scale 0.55, ROCK with STEEL flecks. `Pile_Coal_1–3` (COAL) |
| Iron | `Prop_CharcoalMound`: half-ico r 2.0 × h 1.4, SOIL with COAL patches, 4 VOID vents (4 × Smoke). `Prop_Bloomery`: lathe [(1.2,0),(1.1,1.0),(0.9,2.2),(0.7,3.2)] STONE/CLAY, GLOW arch 0.4×0.5 (Fire, Smoke). `Prop_Bellows`: HIDE wedge 1.0×0.6 |
| Leather and cloth | `Prop_TanningPit`: stone rim 1.2×1.2×0.3, HIDE liquid. `Prop_HideFrame`: 1.4×1.8 frame + HIDE quad + lacing. `Prop_DyeVat`: stave `_cyl` r 0.6×0.8 + 2 IRON hoops; liquid disc in **CLOTH_A**, so `{"cloth":"Blue"}` gives a blue vat. `Prop_ClothRack`: posts 3.2, poles at 2.2 / 2.6 / 3.0, 7 strips 0.5×2.0 in CLOTH_A, CLOTH_B, YELLOW, PAPER. `Prop_Loom` (2.0×1.3×1.8, warp as 20 boxes 0.01 thick, CLOTH_A roll). `Prop_SpinningWheel`. `Pile_Hides_1–3`. `Pile_Wool_1–3` (CLOTH_B bales 0.8×0.6×0.6) |
| Food | `Kiln_Oast`: round STONE wall r 2.2 × 5.0, 16 segments; ROOF cone r 2.4 × h 3.6; white PLASTER cowl 0.8×0.8×1.0 with a slanted top and a vane (top 10.6). `Prop_MashTun` (barrel r 0.9). `Prop_CiderPress` (frame 1.4×1.0×2.0, screw r 0.1, basin). `Prop_Skep` (HAY lathe r 0.28 × 0.45). `Prop_BeeBench` (3 skeps under a Roof_Pent). `Prop_HerbBundles` (pole with 6 bundles). `Prop_Cauldron`. `Prop_DryingRack_{Meat,Herbs}`. `Prop_Antlers`. `Prop_Dovecote`: lathe r 2.0 × 5.0, 3 rows of VOID holes 0.15×0.2, cone r 2.2 × 3.0, open lantern, 8.5 m |
| Crops | new `gen_crops` atlas cells + `crop_rows`: `Crop_Hops` (poles 4.5–5.0 with twine and vine cards), `Crop_Barley`, `Crop_Flax` (blue flowers (0.35, 0.5, 0.95)), `Crop_Vines` (1.4 m trellis rows), `Crop_Sunflower` (2 m) |

### M7: defence and elite pieces (5 days)

| Piece | Geometry | Flags |
|---|---|---|
| Palisade_Straight (3.0) / _Diag (4.243) | 10 / 14 logs Ø 0.30 ± 0.04 at 0.30 spacing; heights U(3.3, 3.9), seeded; 0.45 cone tips (WOOD); BARK_OAK shafts sunk to −0.8; inner rails 0.14×0.2 at z 1.0 and 2.6 on +Y, with BURLAP lashings | ng / nw |
| Palisade_Post / _Walk / _Gate / _GateLeaf / _Tower / Prop_Beacon | Post: 3 logs Ø 0.4 × 4.2 at a vertex. Walk: catwalk 1.0 wide at z 2.3, y 0.25..1.25, on posts at x −1.5 and 0 (+ `_Ladder`). Gate: posts Ø 0.45 × 5.2 at x ±1.5, lintel log at 4.4. GateLeaf: separate object 1.45×3.4, hinge pivot, `hinge_axis`. Tower: 1 cell, 4 logs Ø 0.36 × 6.5, platform at 4.5, log parapet 1.1, 4-segment cone r 2.6 × 2.2 (thatch or shingle). Beacon: IRON basket on a 5 m pole, GLOW, Smoke | ng |
| TownWall_Straight | 2.0 thick (y −1.0..+1.0, outer face −Y). Outer batter +0.35 at the base, fading to 0 at z 1.8. STONE panels with `grid_cut` + `wall_rocks`. ASHLAR string course at 5.6. Outer parapet (y −1.0..−0.5) breast to 7.1; merlons 0.9 wide at x ±0.75 up to 7.9, each with a VOID slit 0.1×0.55; coping 0.12. ASHLAR walk at **6.2**, y −0.5..+1.0. Skirt to −1.5 | std |
| TownWall_Diag / _Corner_Out / _Corner_In / _Step / _Ruin | Diag 4.243 (nw). Step: base and walk rise by LVL over 3 m. Ruin: ragged top U(3.8, 5.2), no merlons, rubble `rock()` heap | std / nw |
| TownWall_Stair | 3.0 run, 2.067 rise, 8 steps (rise 0.258, tread 0.375) against the inner face, y 1.0..2.1; solid support down to local −4.2. Placed at z 0, 2.067 and 4.133 (34.6°) | ng |
| GuardTower_Wall2 / GuardTower_WallL | `guard_tower()` with 1.2 m gaps cut in the hoarding breastwork on 2 opposite / 2 adjacent sides; centred on a grid vertex; ground door facing +Y (inside) | ng |
| TownWall_Tower_Round / Roof_Cone_R{1.2, 2.2, 3.4} | Tower: r 3.0 on a vertex; walk at 8.5; ring of 16 merlons; 3 levels of slits; openings at 6.2 on ±X. Cones: 16 segments, h 1.9·r, bell-cast skirt of 0.25·r at KICK, finial | ng / nw |
| Gatehouse_Block (+ Portcullis, Gate_Leaf) | 3×2 cells centred on the wall line; masonry to 6.2. Passage along Y: hw 1.6, spring 2.8, crown 4.4. IRON portcullis (separate object, 0.08 bars at 0.3 pitch) half raised at y −2.4; 2 PLANKS leaves (separate objects). Half-round towers r 1.8 at (±3.0, −3.0) up to 9.0 with Roof_Cone_R2.2. Above 6.2: Wall_Timber* + Corner_Timber, `Wall_Timber_Door` onto the walk on both end walls; Roof_Hip ends + Roof_Mid at 9.0 | ng |
| Parapet_Crenel / Parapet_Corner / Roof_Pyramid_6 / Roof_Pyramid_9 | Parapet: 6 corbels 0.3×0.45×0.4 at x −1.25 + 0.5i, z −0.4..0; breast 0.9 high at y −0.6..−0.25; merlons 0.9 × 0.8 at x ±0.75; coping 0.12; walk slab 3.0×1.2. Pyramids: 4-segment cone rotated 45°, r 2.83 × h 2.86 and r 4.88 × h 4.93, ROOF UVs as in `guard_tower` | nw |
| Training props | `Prop_TrainingDummy` (post, crossbar, BURLAP head, CLOTH_A shield); `Prop_ArcheryButt` (straw disc r 0.6 × 0.3 on an A-frame; rings YELLOW / CLOTH_A / CLOTH_B); `Prop_ArmorStand` | ng |

### M8: civic pieces (1 day of pieces)

| Piece | Geometry |
|---|---|
| Prop_MarketCross | 3 octagonal ASHLAR steps (r 1.8 / 1.4 / 1.0, each 0.3 high), tapering shaft 3.5, small gabled head; 5.3 m total |
| Prop_Maypole | lathe pole 9.0 in CLOTH_A/B bands; wreath `ring()` at 7.0 in LEAVES + PINK/YELLOW icos; 8 ribbons 0.08 wide from 7.0 to stakes at r 3.2, sag 0.3 |
| Prop_Stage | plank platform 6×3×0.8 with a CLOTH_A canopy |
| Prop_Stocks / Prop_Pillory | 2 posts, holed plank, bench |
| Prop_BathTub | half barrel r 0.7 with WATER |
| LowWall_GateArch / LowWall_Diag / Deco_Hedge (3.0 and 4.243) | gate: single-cell arch with `arch_ring`. Hedge: FOLIAGE clumps via the `make_bush` logic, trimmed to 3.0×0.8×1.2 |
| Chapel_InnerCorner | concave corner for HC 4.5 walls |

## 7. House types

The effort column covers only the builder, once its milestone's pieces exist.

| Type (tier) | Role | Look | New pieces | Reused | Footprint (lot) | Effort / milestone |
|---|---|---|---|---|---|---|
| Settler camp (T0) | first shelter, 2 beds per tent, first storage | canvas, fire glow, covered wagon | tents, campfire, bedroll, covered wagon | Crates, Sacks, BarrelStack, Pile_Logs_1 | 3×3 | S / M3 |
| Hovel (T1) | cheapest home, 4 beds | "haystack" thatch on 2.4 m daub walls; cruck gables; vent smoke; no chimney | wattle set, cruck gable, thatch vent | RoofThatch_Mid/Hip, Woodpile, GardenBed, Chickens, Deco_Weeds | 2×2 (3×3) | S / M3 |
| Longhouse (T1) | 8 beds + 4 livestock | low thatch "loaf", 15 m long; people at one end, byre at the other | Wall_Wattle_Byre | RoofThatch_Mid ×3, RoofThatch_Gable_Planks, Fence, Trough, HayBale, Cow, Sheep | 5×2 (8×3) | S / M3 |
| Log cabin (T1–2) | frontier home for woodcutters and hunters | dark logs, silver shingle roof, big gable chimney | log set, Roof_Gable_Logs, Shingle | Roof_Mid, Porch, Woodpile, Stump, Log_Fallen | 2×2 or 3×2 (3×3) | S / M3 |
| Cottage variants (T2) | standard home, 6 beds | existing cottage plus chimney-gable, half-hip, cross-gable, gallery, PlasterUp and slate/shingle options | none beyond M2 and M4 | everything existing | 2–4×2 | S / M2 + M4 |
| Rowhouse terrace (T3) | dense housing with shop slots; firewalls stop fire spread | continuous colour blocks, stepped ridges, party chimneys and firewalls | Flush, Firewall, Mid_Cap, Chimney_Party, Corner_Party, shops, PlasterUp, Passage | all walls, roofs, awnings, signs | units 1–3 × 2; 4–8 units | M / M4 |
| Gable-front townhouse (T3) | craftsman or merchant house on the plaza | steep 6 m gable to the street, oriel, hoist, shop | Roof_Gable_Hoist, shop | Wall_Timber_Oriel, Balcony, Sign | 2 × 3 (+1 alley cell) | S / M4 |
| Corner house (T3–4) | anchor at a street corner, 2 shops | L-plan with a turret on the convex corner (tip 14.2) | turret stack, shops | Roof_LCorner, InnerCorner_* | L 3+2 | S / M4 |
| Stone merchant house (T4) | rich trader, storage 40 | all stone, stepped gables, slate, cross-gable hoist over stacked loading doors, twin windows | StoneUp, Stepped, CrossGable_Hoist, CellarHatch, Stair_Stone_Ext | Wall_Stone_*, Corner_Stone, Roof_Mid | 3×2 + 3×1 yard | S / M4 |
| Courtyard inn (T4) | lodging and trade hub | U-plan around a yard, galleries, cart passage, stable range | Passage + Vault, Gallery_Timber, LCorner_Mirror | build_stable, Well, Cart, Trough, Bunting, TavernSign | 7×5 | M / M4 |
| Tower house (T5) | minor noble; security; landmark | 4-storey stone tower; domestic (slate pyramid, 4 stone turrets) or fortified (parapet, bartizans, inner pyramid, banner) | Parapet, Pyramid_6, Turret_Seg_Stone | Roof_Hip + Hip_Plain, Stair_Stone_Ext | 2×2 (3×3) | M / M7 |
| Manor (T5) | lord's residence | L-plan hall + attached tower house + walled forecourt, dovecote, hedges | LowWall_GateArch, Deco_Hedge | build_L_block, tower house, Fountain | lot 8×7 | L / M7 |
| Almshouse (T3 civic) | beds for the poor | 4 one-cell units under one roof, bellcote | Roof_Bellcote | Wall_Stone_* | 4×2 | S / M4 |

### 7.1 Recipes

- **Camp**
  - Tent_A at (−2.5, 1.5, 10°) and (2.2, 2.0, −15°); Tent_Bell at (0, −2.6); Campfire at (0, 0).
  - 4 bedrolls; wagon at (4.2, −1.5, 30°); Crates, Sacks, BarrelStack, Pile_Logs_1.
- **Hovel**
  - `build_block(n=2, floors=["Wattle"], style=district_style(s,"fringe"), faces={"R":["DW"],"F":[".W"],"B":[".."],"L":[".."]}, ends=("cruck","cruck"), breakers=[("vent",0)])`.
  - The door is on the R gable end, which faces the street.
  - Variant: `ends=("hip","cruck")`.
  - Lean-to variant: `LeanTo_Thatch` on the L gable end (not the eave wall).
  - Upgrade look: `Chimney_Gable_H24` on L replaces the vent.
  - Upgrade in place, 2×2 → cottage 2×2 → townhouse 2×2 (P1 rule), with `upgrade_to` metadata.
- **Longhouse**
  - `n=5, floors=["Wattle"], ends=("cruck","planks"), faces={"L":["D."],"R":["B."],"F":[".W.W."],"B":["....W"]}`, vents in bays 1 and 3.
  - Paddock of 3×3 cells off R, with FenceGate, Trough, HayBale, 1 Cow and 2 Sheep.
- **Log cabin**
  - `floors=["Log"]`, style roof "Shingle", `ends=("logs","logs")`, `("chimney_gable","L")`, F "DW" or "WDW"; Porch allowed.
  - Dress: ChoppingBlock, Woodpile, Stump.
- **Cottage**
  - `build_cottage(seed, district)` uses district weights.
  - Chimney_Gable with p .30 instead of the ridge chimney; halfhip per district (M4); cross gable p .20 if n ≥ 3 (M4); Gallery_Top on the back, p .15 (M4); PlasterUp per district (M4).
- **Terrace**: `build_terrace(coll, x0, x1, y_street, side, seed, district="market")`.
  1. **Unit size:** w ∈ {1: .2, 2: .5, 3: .3}. Storeys ∈ {2: .25, 3: .5, 4: .25}; if equal to the previous unit, change by ±1 with p .6.
  2. **Style:** plaster must differ from the previous unit.
  3. **Ground string** per module from {S .45, D .3, W .25}, with at least one D per unit. Every 4th unit with w ≥ 2 gets one P (a Passage_Vault goes behind it).
  4. **Boundary between equal-height units:**
     - no end walls; both end bays are Roof_Mid;
     - Roof_Firewall on even boundaries, and always when the roof materials differ;
     - Chimney_Party on odd boundaries;
     - Corner_Party on F and B on every level where the families or styles differ.
  5. **Boundary between unequal heights (taller unit t, lower unit l):**
     - t places its end walls and the corners at (x_b, ±3) only on levels f_l … f_t−1;
     - t's end = "flush" (the parapet on x_b); l's end = "none" (Roof_Mid_CapL or CapR).
  6. **Street ends** use {stepped .3, flush .3, gable .2, halfhip .2}.
  7. **Dressing:** Banner_Wall on every 2nd unit at level 1; Awning or Roof_Pent over S modules; the Sign kind matches the goods.
- **Gable-front townhouse**
  - `n=3, depth=2, floors=["Plaster","Timber","Timber"]`, placed so that R faces the street.
  - R faces: `["SD","OW","WW"]`; `ends=("gable","hoist")`; plus `("emblem","R",kind)`.
  - Keep one empty cell to each neighbour.
- **Corner house**
  - `build_L_block(a=1, b=1, floors=["Stone","Timber","Timber"])` with S modules on both street faces.
  - Turret: Corbel at z 3.0, Seg at 3.0, 5.8 and 8.6, Cap at 11.4; axis at world (−3.6, −3.6).
  - Banner_Wall on the corner.
- **Merchant house**
  - `n=3, floors=["Stone","StoneUp","StoneUp"]`.
  - F faces `["SDS","TLT","WLW"]`; B `[".W.","D.W","W.W"]` with `("stair_stone","B",0)` up to the B door in bay 1.
  - `ends=("stepped","stepped")`, roof Slate; `("cross_hoist",1)`, `("chimney",0)`.
  - CellarHatch at F bay 2; optional stone turret at FL (p .5).
  - Yard 3×1 with a cart, BarrelStack and Crates.
- **Courtyard inn**
  - Front range n = 7: `Roof_LCorner` at the left junction, `Roof_LCorner_Mirror` at the right, 3 Mid bays with a P in the middle cell.
  - Wings 2 wide, going 3 cells back (Mid ×2 + Gable, rot 90).
  - Gallery_Timber on the yard faces; `build_stable` across the back.
- **Tower house (domestic)**
  - `n=2, floors=["Stone","StoneUp","StoneUp","StoneUp"]`, F level 0 "XX", F level 1 ".D" via `("stair_stone","F",0)`.
  - Ends hip + hip (Roof_Hip + Roof_Hip_Plain, apex 15.59), slate.
  - 4 stone turrets: corbel at 8.6, Segs 8.6–14.2, caps to 17.0.
- **Tower house (fortified)**
  - Same walls, but Parapet_Crenel ×8 + ×4 corners at 11.4 and Roof_Pyramid_6 inside (apex ≈14.4).
  - 4 stone turrets r 0.85 corbelled at 11.4; Banner_Roof.
- **Manor**
  - `build_L_block(a=4, b=2, floors=["Stone","StoneUp"], roof "Slate")`.
  - Domestic tower house at the far end of wing A. The tower owns the shared wall; the hall end there is `none`.
  - Forecourt 6×4: LowWall + LowWall_GateArch, Deco_Hedge parterre, Fountain, Dovecote; banners in Purple.
- **Almshouse**
  - `n=4, floors=["Stone"]`, F "DDDD", `("bellcote",1)`, gable ends; garden beds in front.

## 8. Village features

| Feature | Role | Look / tell | New pieces | Reused | Footprint | Effort / milestone |
|---|---|---|---|---|---|---|
| Stockpile yard | player-zoned storage | bordered cells with piles | Stockpile_Border, Pile_* | — | n cells | S / M1 |
| Woodcutter's lodge | logs, 2 jobs | log cabin + LeanTo over Pile_Logs_3; end grain seen from above | ChoppingBlock, Sawhorse | log cabin, LeanTo, Stump | cabin 2×2, lot 3×3 | S / M3 |
| Forester's hut | replants trees | 1-cell Shed hut with RoofS_Single + sapling nursery | Crop_Saplings | Shed set, Fence | lot 3×2 | S / M3 |
| Sawpit yard | logs → planks (T1) | pit, log on trestles, sawdust | Prop_SawPit | Pile_Logs, Pile_Planks | 2×1 + pile | S / M3 |
| Carpenter / cooper | planks → goods | 2×2 cottage + 2 LeanTo, half-built barrel, saw emblem | — | cottage, Table, Pile_Planks | lot 3×2 | S / M3 |
| Granary | grain storage, less spoilage | Shed walls at z 0.75 on 9 staddle stones, thatch pyramid (2 hips), detached steps | StaddleStone, GranaryStep | Shed set, RoofThatch_Hip, Sacks | 2×2 | S / M3 |
| Storehouse | general storage (T2) | 3×2 barn with one Posts_Barn cart bay + bordered yard | — | Wall_Barn, Posts_Barn, piles | 3×2 + 3×2 | S / M3 |
| Root cellar | vegetable storage | earth mound + stone portal + vent | Prop_RootCellar (half-ellipsoid 3×4×1.6 SOIL, `wall_stone_door` arch at 0.8 scale) | Plant_TallGrass | 1×2 | S / M3 |
| Pig sty / sheepfold / byre | animal products | LowWall pen + pent shelter; fence pen + LeanTo_Thatch; barn + paddock | animals, HayRack | LowWall, Fence, LeanTo_Thatch, Trough, build_barn | 3×3 each | S / M3 |
| Privy / wayside shrine | hygiene; faith coverage | plank booth; candle niche at crossroads | Privy, Shrine | — | sub-cell | S / M3 |
| Market hall | market in bad weather; landmark | open arcade ground floor, timber upper floor, hip ends, cupola | Wall_Arcade_Open, Ceiling_Cell | Roof_Hip, Roof_Cupola, MarketStall, Banner_Wall | 4×2 | S / M4 |
| School | education | 3×2, 2 floors, bellcote, book emblem | Roof_Bellcote | cottage walls, Bench | lot 3×3 | S / M4 |
| Watermill | flour on rivers | 3×2 house + turning wheel over the water | WaterWheel, Wall_Stone_Axle, WheelPier, Millstone | walls, roofs, Sacks, Cart | 3×2 + wheel strip | M / M5 |
| Fisher's hut | fish, 2 jobs | Shed 2×1 with RoofS on the bank, pier, rowboat, net rack | pier set, boats, racks | Crates | 2×1 + 1×3 pier | S / M5 |
| Smokehouse | preserves fish and meat | 1×1 stone hut, RoofS_Single, vent smoke | — | Wall_Stone, Roof_Vent | 1×1 | S / M5 |
| Lavoir | washing; social | 2×1 open posts + RoofS over a basin | LavoirBasin | Wall_Posts, Laundry | 2×1 | S / M5 |
| Bridges / docks / quays | crossings, harbour | see M5 | M5 set | LampPost | per river | M / M5 |
| Sawmill | powered planks (T2) | 3×2 open shed on Posts_Barn + frame saw next to the wheel | Prop_FrameSaw (2.6 m posts, blade sash, 6 m log carriage) | M5 wheel set | 3×2 + wheel | M / M6 |
| Quarry + mason's yard | stone | stepped pale cut faces; treadwheel crane | quarry set, crane, Banker | LeanTo, rocks, Pile_Stone | 3×3 (quarry faces on cliffs) | M / M6 |
| Clay pit + kiln | bricks, pots, roof tiles | bottle kiln smoke | kiln set | shop `_Pots` | lot 3×3 | S / M6 |
| Mine | ore | portal in a rock mound, rails, cart, spoil heap | mine set | Lantern, LeanTo | 2×2 | M / M6 |
| Charcoal burner + bloomery | fuel → iron for the blacksmith | smoking mound; glowing furnace | CharcoalMound, Bloomery, Bellows, coal/ore piles | Anvil, LeanTo | lot 2×2 each | S / M6 |
| Tannery | hides → leather (edge of town) | pits and hide frames | tannery props | LeanTo, Roof_Vent | lot 3×3 | S / M6 |
| Dyer's yard | dyed cloth (T4 luxury) | 3–4 vats in different cloth colours + cloth racks: the most colourful spot in the village | DyeVat, ClothRack | Laundry | lot 3×2 | S / M6 |
| Weaver | cloth | townhouse with a Cloth shop front + loom | Loom, SpinningWheel | shop, Roof_Pent | townhouse | S / M6 |
| Brewery + oast | ale for the tavern | 3×2 range + round oast with a white cowl | Kiln_Oast, MashTun, Crop_Hops/Barley | BarrelStack | lot 5×3 | M / M6 |
| Orchard + cider house | cider | 4 Tree_Apple + press under a LeanTo | CiderPress | Tree_Apple, LadderLean | lot 4×2 | S / M6 |
| Apiary + chandler | honey, wax, candles | bee benches in lavender; Candles shop front | Skep, BeeBench | Crop_Lavender | 2×2 | S / M6 |
| Herbalist / butcher / hunter | healing; meat; game | herb bundles + cauldron; Meat shop + sty; cabin + antlers + hide frames | HerbBundles, Cauldron, Antlers | Sign_Potion, GardenBed, cabin | lot 3×3 each | S / M6 |
| Palisade ring → town wall + gatehouse | defence tiers | see M7; the gatehouse replaces the palisade gate on the same middle cell | M7 set | GuardTower | per wall | M–L / M7 |
| Barracks + training yard | soldiers, training | 4×2, 2 floors, slits, Gallery on the yard side, archery butts | training props | WeaponRack, Banner_Pole | lot 4×5 | S / M7 |
| Market cross / festival green / stocks | plaza centre; happiness; law | see M8 | M8 props | Bunting, Festoon, Bench | 1×1 / 4×4 / 1×1 | S / M8 |
| Bathhouse / wash house / healer | hygiene; health | stone house with 2 vents + tubs; 4 posts + 2 Roof_Hip over a basin; 3×2 with Gallery and bellcote | BathTub | Roof_Vent, Laundry, Gallery | 4×3 / 2×2 / 3×3 | S / M8 |
| Guildhall | guild policies, prestige | T-plan: street range `Gable, Mid, Roof_T, Mid, Gable` (18 m) + rear wing of 2 cells; `Wall_Arcade_Open` on the 4 central bays; Balcony; Cupola | Roof_T | Wall_Timber*, Roof_Cupola | 6×4 | M / M8 |
| Cruciform church | faith tier 2 | nave 4×2 + crossing 2×2 (Roof_X) + 1-bay transepts (Roof_Gable_Stone) + chancel with a hip; BellTower at the west end | Chapel_InnerCorner, Roof_X | Chapel_* walls, BellTower | 8×4 | M / M8 |
| Trading post | trade with outsiders | covered wagon, bell tent, hitching rail, scales emblem | — | camp pieces, Crates | lot 3×3 | S / M8 |
| Keep (optional) | stronghold | 3×3, 5 floors StoneUp, walls to 14.2; parapet, Pyramid_9 (apex 19.3); 4 turrets | — | M7 set | 3×3 | L / after M8 |

**Deferred:** L roof family (9 m deep tithe barn), gable-front valley family, a deeper jetty (0.45 m offset plus +0.25 roof lift), thatch eyebrow dormer, overshot race with `MillRace` and `_Spout`.

## 9. Terrain interface (agree with the terrain track)

1. **Grid.** Terrain tile = CELL = 3.0, with tile corners on kit grid vertices (primal grid).
   - A cell is flat when its 4 corners are equal.
   - A footprint is buildable when every cell in it is flat at the same level.
   - If the terrain track picks a dual grid instead, the same contour meshes go on cell edges; only placement code changes.
2. **Step height.** LVL = 1.5 is requested: two levels equal H1.
3. **Contour pieces** (quay, quarry face, retaining walls, cliff props):
   - Straight 3.0 along a cell centre-line; Diag 2.121 between adjacent edge midpoints; saddle cases 5 and 10 are two diagonals.
   - Pivot at the segment midpoint, face −Y toward the lower side.
   - Heights are multiples of LVL.
4. **Grid-drawn pieces** (palisade, town wall, low wall, hedge, fence, rails): Straight 3.0 on cell edges, Diag 4.243 across a cell, joint pieces at vertices. `_Step` covers slope tiles.
5. **Water.** Water tiles use water −0.6 and bed −1.5. Piles go to −3.0, the quay face to −2.0 and the town-wall skirt to −1.5.
6. **Skirts.** New ground-contact pieces carry a hidden skirt to −0.6. Existing walls get skirts only after the M0 regression snapshot, in a separate commit (`SKIRT_EXISTING=True`).
7. **Watermill check.** The house-local rectangle x ∈ [L/2+0.85, L/2+1.85], y ∈ [−3.9, 0.9] must be water. If the shoreline does not reach the end wall, add `Quay_Straight` in front of it.

## 10. Build order (one engineer, about 38 days)

| # | Milestone | New meshes | Days | Why it comes here |
|---|---|---|---|---|
| M0 | Infrastructure (§5) + regression snapshot | 0 | 3.5 | every later piece depends on the API; stages and sockets can't be retrofitted cheaply |
| M1 | Construction + stock | ~30 | 3 | the core colony-sim feedback loop; applies to every existing building immediately |
| M2 | Skyline pack + district styles + retrofit | ~35 | 3.5 | fixes the "field of orange wedges" across the whole existing town at low cost |
| M3 | Humble walls, S roofs, camp, T0–T1 houses, early chain | ~60 | 5.5 | early game currently has no housing below the cottage |
| M4 | Town tier (StoneUp, shops, `roof_field`, turrets, galleries) + terraces, merchant, inn, market hall | ~50 | 6 | T3–T4 housing and dense streets |
| M5 | Water set + watermill, fisher, smokehouse, lavoir | ~28 | 4 | depends on the terrain track's water tiles |
| M6 | Production props + chains | ~45 | 5 | stone, metal, cloth, food chains |
| M7 | Defence + tower house, manor, barracks | ~35 | 5 | late-game edge and landmarks |
| M8 | Civic props + guildhall, church, bathhouse | ~12 | 3 | polish and happiness buildings |

**Cross-track dependencies:**
- The stone-texture rework should land before M4 and M7. StoneUp, quays, bridges and a town wall 7.9 m tall show a 3.0 m stone tile across large areas; ask that track for macro variation.
- The terrain track must confirm LVL, the grid convention and the water datum before M5.

## 11. Acceptance tests

### 11.1 Automated `kit_qa()` (must return an empty list after every milestone)

1. **Material slots.** Every `SM_VK_*` mesh has exactly 50 slots; no face index is above 49.
2. **Stage coverage.** Every builder runs for stage 0, 1, 2 and 3, and every `stage_piece` target exists.
3. **Wobble rule.** Every spec with `wobble=True` has its length L in `PIECE_META` with L/2 % 3 == 1.5.
4. **Horizontal seams.** For each wall family, place `.`, `W` and `D` at x = 0, 3 and 6. The outer-skin vertices (|y − face| < 0.06) at x = 1.5 and 4.5 must match in y within 2 mm.
5. **Stacked seams.** Wall_Stone with Wall_StoneUp at z 3.0, and StoneUp on StoneUp at z 5.8: outer-skin vertices at the seam match within 2 mm.
6. **Roof continuity.** For every roof piece, the edge vertices at x = ±1.5 lie on `roof_z(|y|)+roof_sag` within 5 mm. `roof_family("M")` must reproduce the old `roof_profile()` exactly.
7. **Sockets.** Every piece containing GLOW, clay pots or fire has a Smoke, Light or Fire socket. Every door piece has a Door socket at (0, −0.9, 0).
8. **Wattle door rule.** `build_block` raises on a Wattle door under an eave or hip end.
9. **Piles.** Every Pile_* fits within 2.9×2.9×1.6. Scaffold planks do not overlap any SHUTTER face in the M1 stage renders (bounding-box test).
10. **Slopes.** Every walkable stair or ramp is ≤ 35° (town-wall stair 34.6°, bridge ramp 21.8°). `ext_stair` and `Stair_Stone_Ext` (≈50°) are flagged for NavMeshLink.
11. **Triangle budget.** Each piece has ≤ 1.5× the triangle count of the heaviest existing piece in its category (walls, roofs, props, landmarks).

### 11.2 Regression (M0)

- Before M0, `snapshot_kit()` records the vertex count and bounding box of all 146 pieces.
- After M0 (with SKIRT_EXISTING off), every piece must match within 1e-5.
- Re-render `nature_town_aerial.png` from the saved camera: mean absolute pixel difference < 0.5 %.

### 11.3 Visual checks (catalog sheets like `catalog_walls.png` + targeted renders)

- **M1:** strip of stages 0–3 for a 3×2 two-storey stone cottage and for the tavern (L-plan).
  - No floating parts; a frame in every roof bay at stage 2.
  - Piles of all 3 levels on a 3 m grid.
- **M2:** re-render the aerial camera with a district-built demo town (`build_town2`).
  - A roof-ID pass (roof materials swapped for flat emission colours) shows Red ≤ 45 % of roof pixels.
  - No 3 consecutive houses on a street share (roof material, end kind, storeys).
  - Emblems on the blacksmith, bakery and tavern read as ≥ 8 px silhouettes at 1920×1080.
  - Close-up of the pyramid apex shows no z-fighting.
  - Stepped and flush parapets fully hide the slab ends.
- **M3:** line-up of camp, hovel, longhouse, cabin and a 2-storey cottage.
  - Measured ridges: hovel/longhouse 6.59 (+ thatch cap), cabin 7.19, cottage 9.99.
  - Hovel eave-roll underside ≥ 1.65; cruck blades stay under the thatch.
  - Log corners alternate with no interpenetration.
- **M4:** 8-unit terrace from 3 seeds.
  - Close-ups at an equal-height boundary with a firewall and at an unequal one (Flush + Mid_Cap): no open roof section and no hole in an end wall.
  - The corner-house turret contains the eave corner (distance check < r).
  - Cross-gable eave stops close the neighbour eave.
  - Half-hip creases are clean (no sawtooth).
  - Passage ring top ≤ 3.0; merchant house hoist rope lines up with the loading doors.
- **M5:** river test scene (2-cell river).
  - Wood bridge End + Bent + End.
  - Stone bridge Ramp + Span + Ramp = 12 m.
  - Pier of 3 decks + End.
  - Watermill: wheel dips 0.5 m into the water and spins about an axle perpendicular to the end wall over a 120-frame turntable.
- **M6:** colony-camera crop of each production building.
  - Props and piles cover ≥ 30 % of the lot.
  - Its roof or yard tell (vent, cowl, crane, kiln, vats, mound smoke) is identifiable at 1920×1080.
- **M7:** wall circuit of 20 modules with 2 GuardTower_Wall2, 1 gatehouse and 3 stair runs.
  - Walk surface at 6.2 ± 0.02 from wall to hoarding to gatehouse door.
  - Merlons don't pierce the hoarding; gate leaves and portcullis move about their pivots.
- **Unity smoke test (after M1, M4 and M7):**
  - Import 5 pieces + 1 recipe JSON; the prefab assembles at stages 0–3.
  - Sockets arrive as child transforms.
  - Renderer material count equals the number of materials actually used (unused slots stripped).
  - Spin and hinge objects rotate about their pivots.