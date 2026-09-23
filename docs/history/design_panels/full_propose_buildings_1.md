# Village Kit expansion: new house types, production buildings and modular pieces

*Design only. All sizes are in metres unless marked otherwise. The existing grid rules still apply: CELL = 3.0, DEPTH = 6.0 (2 cells), H1 = 3.0, H2 = 2.8, HB = 4.2. Wall modules are 3 m wide, centred on the cell edge, with the outer face toward local −Y. Corner pieces sit at the origin with their outer faces toward −X and −Y. Roof pieces are per 3 m bay and are placed at `z = roof_top(stories)`. Some derived numbers used below: `RIDGE = 0.35 + 3·tan52° = 4.19` above the wall top, the eave tip is at −0.31 below the wall top, and the eave overhang is 1.35.*

---

## 0. Top 12 priorities (value to a colony sim ÷ effort)

| # | Item | Why the player needs it | Effort |
|---|---|---|---|
| 1 | **Stockpile piles in 3 fill levels** (logs, planks, stone, ore, coal, sacks, wool, hides, fish, barrels, bricks) | Every production chain needs visible stock. It is the main feedback loop of the genre. | S each, M total |
| 2 | **Construction-stage set** (build site, foundation, skeleton walls and roofs, scaffold) | Every building the player places needs these stages. One substitution map covers the whole kit. | M |
| 3 | **Wattle-and-daub set, Hovel and Longhouse** (tier 1 housing) | The kit has nothing below "cottage". Colonists need a starter home. | M |
| 4 | **Log wall set, Woodcutter and Hunter** | The wood chain is missing completely, and wood is the first resource. | M |
| 5 | **Granary and Storehouse / Warehouse** | Storage is a core need. Only the barn exists today. | S–M |
| 6 | **Quarry, treadwheel crane and Mason's yard** | The stone chain is missing. The crane is also reused at the harbour and on large build sites. | M |
| 7 | **Mine, rails, Bloomery and Charcoal burner** | The metal chain has only its last link (the Blacksmith). | M |
| 8 | **Livestock and pens** (sheep, pig, cow, goat, horse) | Feeds the food, wool and leather chains. `chicken()` is already the template. | M |
| 9 | **Textile and leather** (loom, dye vats, tannery) | The cloth need. The dye colour can reuse the existing `cloth` variant slot. | S–M |
| 10 | **Water set** (water wheel and mill race, pier, quay, bridges), Watermill, Sawmill, Fisher | These tie into the new marching-squares water tiles. | M–L |
| 11 | **Town-growth set** (stone upper floors, shop front, flush/stepped gables, valley roof, terrace builder) | Tier 3–4 housing and dense streets. | M |
| 12 | **Palisade, then town wall and gatehouse** | The defence tiers. The existing Guard Tower becomes the wall tower. | M / L |

---

## 1. Design rules for this expansion

1. **Readability from the colony camera.** In `nature_town_aerial.png`, buildings are told apart almost only by roof colour. Every production building therefore gets:
   - a **roof tell**: a smoke louvre, oast cowl, hoist hood, water wheel, crane, crenels or bell-cote;
   - a **yard tell**: piles, vats, pens or racks covering at least 30% of the lot.

   Shop signs are too small to see from 40–80 m.
2. **Tier colour language.**
   - Walls go wattle → plaster/timber → stone.
   - Roofs go thatch → red/green tile → slate.
   - **Blue roofs are reserved for civic and faith buildings.** Remove `"Blue"` from the house roof list in `random_style()`, and add `random_style(seed, tier)` so each tier picks from its allowed palette:
     - T1: Thatch, plaster Daub/Cream
     - T2: Thatch/Red/Green
     - T3: Red/Green
     - T4–5: Slate/Red
     - Civic: Blue
3. **Upgrade in place.** Tiers T1–T3 all exist on a **2×2 cell** footprint, so a plot can go Hovel → Cottage → Townhouse without rebuilding the road layout.
4. **Depth is always 6 m.** Every new roof reuses `roof_z()`. Wider buildings are built as L, T or U plans, or as two parallel ranges joined by the new valley pieces. No new roof depths.
5. **Construction and stock always show.** The same builder call renders stages 0–4, and stock is shown as discrete pile meshes.
6. **Unity hooks.** Every building gets a root Empty with metadata and socket empties (see §2.5).

---

## 2. Small code infrastructure changes

### 2.1 Materials: append only, never insert
`kit_mats()` appends every material to every mesh, so existing meshes store fixed slot indices. New materials **must be appended at the end** of the list, and the unpack line changes from `range(45)` to `range(50)`. `full_rebuild()` already appends any missing slots (`while len(me.materials)<len(mats)`).

| Index | Const | Source | Used by |
|---|---|---|---|
| 45 | `WATTLE` | new `T_VK_Wattle`: `gen_wattle()` built on the existing `weave()`, 0.06 m rods, tile 1.0 | hovel, longhouse, fences, construction stage |
| 46 | `HIDE` | flat (0.50, 0.33, 0.20), rough 0.8 | tannery, hunter, cows, horses, bellows |
| 47 | `PIGSKIN` | flat (0.90, 0.62, 0.56), rough 0.7 | pigs, hams |
| 48 | `COAL` | flat (0.045, 0.043, 0.05), rough 0.95 | charcoal, coal and slag piles, soot |
| 49 | `MEAT` | flat (0.60, 0.19, 0.16), rough 0.6 | butcher, drying racks |

Also add `TILE[WATTLE]=1.0`.

### 2.2 Variant additions (no new slots needed)
- `VARIANT_MATS["plaster"]["Daub"] = ("T_VK_Plaster", (0.80, 0.66, 0.48))`
- `VARIANT_MATS["roof"]["Slate"] = ("T_VK_RoofSlate", None)`: `gen_roofs()` with rectangular slates and a blue-grey palette from (0.28, 0.31, 0.36) to (0.45, 0.50, 0.56).
- `VARIANT_MATS["roof"]["Shingle"] = ("T_VK_RoofShingle", None)`: `gen_roofs()` with a wood palette and 0.2 m shingles.
- Optional: `SLOT["stone"] = STONE` with tints "Warm", "Grey" and "Dark". This is cheap variety for merchant houses and walls; agree it with the stone-texture rework. That rework should also hold up on 6–9 m tall surfaces (town wall, bridges, quarry), which argues for macro variation or a vertex-colour tint.

### 2.3 Parametrise heights
- `wall_stone_plain/window/door(k, h=H1, plinth=True, batter=True)`
- `corner_stone(k, h=H1)` and `inner_corner_stone(k, h=H1)`
- `roof_slab(k, x0, x1, side, end_caps, trunc=False)`: `trunc` cuts the profile at `ay = 3.0` (top z = 0.35).
- `gable_end(k, kind)` gains the kinds `"cruck"`, `"flush"` and `"stepped"`.

### 2.4 Generalised assembly
```
def _assemble2(coll, origin, walls, corners, floors, style, r):
    # floors e.g. ["Stone","StoneUpper","StoneUpper"] | ["Wattle"] | ["Log"] | ["Stone","Timber"]
    z = 0
    for lvl, kind in enumerate(floors):
        for (x,y,rot,c) in walls:    place_v(coll, WALL[kind][c], x,y,z, rot, origin, style)
        for (x,y,rot)   in corners:  place_v(coll, CORNER[kind],  x,y,z, rot, origin, style)
        z += HEIGHT[kind]            # Wattle 2.4, Log 3.0, Stone 3.0, StoneUpper/Timber 2.8
    return z                         # roof base
```
The wall character codes grow to:
- `D` door, `W` window, `.` plain, `A` arcade (existing)
- `S` shop front
- `P` passage arch
- `L` loading door
- `B` byre door
- `X` arrow slit

### 2.5 Building root, metadata and sockets (for Unity)
Each `build_*` creates an Empty named `BLD_<Type>_<id>`. All pieces are parented to it (add a `parent=` argument to `place_v`). It carries these custom properties:
- `building_type`, `tier`
- `footprint=[w,d]`, `lot=[w,d]`
- `jobs`, `beds`, `storage`

Child empties:
- `SOCKET_Door_n`, `SOCKET_Work_n`, `SOCKET_Stock_n`
- `FX_Smoke_n`, `FX_Fire_n`, `FX_Water_n`
- `ANIM_Spin_<part>`

Animated parts are separate objects, like `Windmill_Sails` today:
- WaterWheel
- Crane_Treadwheel_Wheel
- gate leaves
- portcullis
- sluice gate

Keep fire and lit elements on the `GLOW` slot only, so Unity can toggle "working" per instance. `WINDOW` is already its own slot, so night-time "occupied" emission can be driven per instance.

### 2.6 Construction-stage substitution
```
STAGE_SUBST = {
 0: {"*": None},                                             # only BuildSite_Cell per footprint cell
 1: {"Wall_*|Corner_*": "Foundation_Wall|Foundation_Corner", "Roof_*|Chimney*": None},
 2: {"Wall_Timber*": "Wall_Timber_Skeleton", "Wall_Stone*": "Wall_Stone_Half",
     "Wall_Wattle*": "Wall_Wattle_Frame", "Roof_*": None, "+scaffold": True},
 3: {"Roof_Mid*": "Roof_Mid_Skeleton", "Roof_Gable*|Roof_Hip*": "Roof_Gable_Skeleton", "+scaffold": True},
 4: {}                                                       # finished
}
def place_stage(coll, piece, ..., stage): p = subst(piece, stage); if p: place_v(...)
```
With `stage < 4`, a stockpile pile of the building's material is dropped on the lot.

---

## 3. New modular pieces (the "unlockers")

### 3.1 Wall sets

**Wattle and daub** (HW = 2.4 m wall height). The existing thatch pieces sit on top at z = 2.4, giving a ridge at 6.59 m and an eave tip at 2.09 m. That reads as low and humble.

| Piece | Spec |
|---|---|
| `Wall_Wattle` | Rubble `plinth()` z 0–0.35. Sole plate 3.0×0.26×0.2 at z 0.45 (WOOD). Daub panel x ±1.5, z 0.55–2.2, y ±0.12 (PLASTER slot, so the "Daub" variant applies). Left post 0.24×0.30 at x = −1.5 (left-edge convention), mid stud 0.16×0.2. Wall plate 3.0×0.3×0.2 at z 2.3, sagging −0.04 at mid-span. 1–2 bare-wattle patches: an irregular 7-gon about 0.6×0.45 in WATTLE at y = −0.125 with a 0.03 daub lip. |
| `Wall_Wattle_Window` | Opening x ±0.35, z 1.10–1.65. VOID quad at y +0.06. Log lintel r 0.09, length 1.1. One top-hinged plank shutter 0.8×0.65 opened 55°, held by a prop stick 0.03×0.9. |
| `Wall_Wattle_Door` | Opening x ±0.45, z 0.35–2.15. Plank door ajar 25°. Stone threshold 1.1×0.5×0.12. |
| `Wall_Wattle_Byre` | Opening x ±1.0, z 0.35–2.10. Split stable door (lower leaf shut, upper open). Straw spill in HAY. |
| `Corner_Wattle` / `InnerCorner_Wattle` | Post 0.28×0.28×2.4 at (−0.1, −0.1) on a rubble foot 0.6×0.6×0.4. |
| `Wall_Wattle_Frame` | Construction stage: posts, plate, and woven wattle up to z 1.3 only, no daub. |

**Log** (H1 = 3.0). Frontier and woodland buildings.

| Piece | Spec |
|---|---|
| `Wall_Log` | 9 logs, r 0.165, 10-segment `_cyl` along X. Centres at z = 0.47 + 0.30·i and y = −0.09, so the outer skin sits at about −0.25 to match stone. Length exactly −1.5..1.5, radius jitter ±0.015 seeded by row. Daub chinking strip 3.0×0.07×0.07 between logs at y −0.2. Stone plinth z 0–0.33. Optional `Wall_Log_B` offset +0.15 in z for end walls to get a real interlock. |
| `Wall_Log_Window` | Logs split at x ±0.55 with ENDGRAIN discs on the cuts. `window_frame(k, -0.5, 0.5, 1.1, 2.0)` with shutters. |
| `Wall_Log_Door` | Opening x ±0.6, z 0.33–2.4. Heavy lintel log r 0.2. Plank door. |
| `Corner_Log` / `InnerCorner_Log` | For each row, a log along X from −0.5 to +0.35 and a log along Y from −0.5 to +0.35, the Y log raised +0.15 (half-lap). ENDGRAIN caps on the ends, which protrude 0.5 beyond the corner. |

Log roofs use `Roof_*` with the **Shingle** variant and the existing `Roof_Gable_Planks`.

**Stone upper floor** (H2 = 2.8, face at −0.25, so no jetty). This is `wall_stone_*(h=H2, plinth=False, batter=False)`.

| Piece | Spec |
|---|---|
| `Wall_Stone_Upper` | `stone_panel(-1.5, 1.5, 0, 2.8)`. ASHLAR string course 3.0×0.16×0.18 at z 0.09, projecting to y −0.33. `wall_rocks` n = 4. |
| `Wall_Stone_Upper_Window` | Cross window: opening x ±0.6, z 0.75–2.15. ASHLAR surround 0.18 wide, mullion 0.14 at x = 0, transom 0.12 at z 1.6. `window_frame(shutters=False)`. |
| `Wall_Stone_Upper_Door` | Opening x ±0.55, z 0–2.2. Used for stair landings and galleries. |
| `Wall_Stone_Upper_Loading` | Flush plank double door 1.3×2.0 with iron strap hinges. Projecting sill beam 1.6×0.4. |
| `Corner_Stone_Upper` / `InnerCorner_Stone_Upper` | `corner_stone(h=2.8)` with ASHLAR long-and-short quoins, 0.95 / 0.55. |

**Façade walls**

| Piece | Spec |
|---|---|
| `Wall_Stone_Shop_*` / `Wall_Plaster_Shop_*` (H1) | Opening x ±1.15, z 0.8–2.3. Lower shutter folds out as a stall-board 2.3×0.7×0.07 at z 0.78, hung on 2 iron chains from z 1.6. Upper shutter hinged at z 2.35, raised 35° as a canopy. VOID back at y +0.2, one shelf 2.2×0.3 at z 1.55. Goods variants: `_Empty`, `_Bread`, `_Produce` (reuse the `market_stall` goods code), `_Cloth` (4 bolts r 0.12 × 0.7 on the CLOTH_A slot, so the `cloth` style recolours them), `_Pots` (CLAY lathe jugs), `_Tools` (IRON/STEEL), `_Meat` (hams in PIGSKIN/MEAT), `_Candles` (PAPER cylinders plus GLOW). |
| `Wall_Stone_Passage` (+ `_Gated`) | Cart arch through the ground floor: hw 1.25, spring 1.5, crown 2.75. 9 voussoirs from the `wall_stone_door` arch code. `_Gated` adds two plank leaves open 100°. |
| `Passage_Vault` | 3×6 barrel-vault soffit, `arch_soffit(k, 1.25, 1.5, -3, 3, STONE, n=16)`. Cobble floor 2.5×6. Inner side walls at x ±1.25..±1.5. Goes between a front and a back `Wall_Stone_Passage`. |
| `Wall_Barn_Open` | `barn_wall` without the planks: post at x −1.5, 2 knee braces, beam at HB −0.12, stone plinth 0.4. Unlocks open-sided sheds: sawmill, cart shed, mason's lodge, Dutch hay barn. |
| `Wall_Stone_Slit` | `wall_stone_plain` plus 2 arrow slits (VOID 0.12×0.9 in an ASHLAR surround 0.5×1.2) at z 1.4. For the tower house, barracks and gatehouse. |

### 3.2 Roof pieces

| Piece | Spec | Unlocks |
|---|---|---|
| `Roof_Gable1`, `RoofThatch_Gable1`, `Roof_Gable1_Planks` | A single bay with gables at **both** ends: `roof_slab(-GX, GX, s, end_caps=(True,True))`, `ridge(-GX-0.1, GX+0.1)`, `gable_end` at +X, and a mirrored `gable_end` (`Matrix.Scale(-1,4,(1,0,0))` plus a normal flip). Needed because placing two `Roof_Gable` pieces on a 1-bay house z-fights over the same x range. | 1×2 huts: fisher, smokehouse, forester, toll booth, well-house |
| `RoofThatch_Gable_Cruck` | `gable_end(kind="cruck")` with XF = 1.5 + 0.14. Two cruck blades, each 7 boxes 0.24×0.30 following a quadratic Bézier from (y ±2.7, z −2.4, i.e. the ground) via (±2.9, +0.6) to (0, under(0) − 0.15). Collar beam at z +1.6. Daub infill with one WATTLE patch. Smoke vent (VOID 0.5×0.35) under the apex. Tied to HW 2.4. | hovel, longhouse, herbalist |
| `Roof_Gable_Flush` | No overhang or bargeboards. Slabs end at x = 1.5. Stone parapet centred on the wall line, x 1.25..1.75 (0.5 thick), top = roof_z(ay) + 0.30. ASHLAR coping 0.62×0.12. Kneeler block 0.7×0.8×0.55 at ay 3.0–3.6. Triangle via `gable_end(kind="stone")`. | party walls and firewalls, stone houses |
| `Roof_Gable_Stepped` | Like Flush, but the parapet is crow-stepped: step k (0..5) covers ay ∈ [3.0 − 0.5(k+1), 3.0 − 0.5k] with top z = roof_z(3.0 − 0.5(k+1)) + 0.30, and a coping cap 0.62×0.56×0.10. Apex pinnacle 0.5×0.5×0.9 with a pyramid cap. | merchant house, guildhall, gable-front terraces, warehouse |
| `Roof_Firewall` | Parapet only, no slabs, crossing the ridge at +X. Placed at a unit boundary where the neighbouring roofs are the same height. Gameplay: **blocks fire spread** between terrace units. | terraces |
| `Roof_Mid_Valley{L,R,B}`, `Roof_Gable_Valley{L,R,B}`, `Roof_Gable_Stepped_Valley{L,R,B}` | `roof_slab(trunc=True)` on the chosen side(s), plus a lead gutter box 3.0×0.45×0.12 at y ±3.0, z 0.18 (STEEL). Two ranges sharing a wall meet at z = +0.35 on the shared wall line, so the valley comes out exactly. | gable-front terraces, double-pile warehouse and manor (M-roof) |
| `Roof_T` | T-junction, derived from `roof_L_corner()`: start `xs` at −3.0 (not GO), drop the −X gable merge and the −X fascia, keep `surf()` = max(zA, zB) for y > 0. Neighbours are `Roof_Mid` at x < −3, x > 3 and y > 3. | T and + plans: manor, guildhall, big inn |
| `Roof_LCorner_Mirror` | The existing LCorner mirrored in X with flipped normals, so both corners of a U-plan have the gable on the same façade. | courtyard house, inn |
| `Roof_Gable_Hoist` | Roof_Gable plus a plank loading door 1.0×1.5 in the gable triangle at z +0.6. Hood: a mini gable 1.4 (y) × 1.3 (x, out) at 38°. Hoist beam 0.2×0.2×1.6 at z +2.4, pulley `ring(r_in 0.1, r_out 0.18)`, rope 0.03 dropping 3.2 m to a BURLAP sack. Works with the timber and stone gable kinds. | granary, warehouse, merchant house (**roof tell**) |
| `Roof_Pent` | Cantilevered pent roof: slab 3.2 × 1.5 (out) at 22°. The origin is where it meets the wall (y −0.3), so it can be placed at any z. Two curved brackets (3-box arcs) at x ±1.2. Uses the ROOF slot, so all roof variants apply. | over shop fronts, galleries, weaver windows, bee benches |
| `Roof_Louvre` | Sits on the ridge at z = RIDGE − 0.1. Body 0.9×0.7×0.5, 4 slats per side at 30°, two cap slabs 1.2×0.6 at 40° (ROOF slot). `FX_Smoke` socket on top. | hovel, longhouse, smokehouse, tannery, bathhouse (**roof tell**) |
| `Roof_Bellcote` | Stone bell gable on the ridge, 0.9×0.5×1.6, with an arched opening and `bell(k, top, 0.25)`. | school, almshouse, infirmary, hamlet chapel |
| `Roof_Mid_Hatch` / `Roof_Mid_Skylight` | Roof_Mid plus a 1.0×1.0 frame on the −Y slope at ay 1.7. Plank lid open 65°, or flush WINDOW glazing. | warehouse, granary, workshops |
| `Roof_Mid_Skeleton`, `Roof_Gable_Skeleton` | Rafters 0.12×0.2 at x −1.2, −0.6, 0, 0.6, 1.2 per side, each 2 boxes (pitch 0→3.0, kick 3.0→4.35). Ridge beam 0.22×0.3. 5 battens 0.05×0.08 per side. Skeleton gable = the timber framing from `gable_end` without infill. | construction stage 3 |
| `Roof_Cone_R{1.2, 2.2, 3.4}` | 16-segment cone, height 1.9·r, bell-cast skirt (last 0.25·r at KICK), finial. ROOF slot, with UVs like the `guard_tower` pyramid. | turrets, oast, wall towers, dovecote |
| `Chimney_Wall` | External chimney on a gable end: stack 1.3 wide × 0.8 deep from the wall face, z 0 → wall top + RIDGE + 1.2 (per storey count: `_1F`, `_2F`, `_3F`). Two weathering steps inset 0.2. Two clay pots. | cottages, hovel upgrade, log cabin |
| `Chimney_Party` | 1.8 (x) × 1.0 (y) stack centred on a unit boundary at the ridge, 4 pots. | terraces |

Note: a 2×2-cell tower with `Roof_Hip` at x = +1.5 (rot 0) and x = −1.5 (rot 180) already forms a **pyramid**, because the hips meet at the centre. No new piece is needed.

### 3.3 Façade attachments

| Piece | Spec |
|---|---|
| `Gallery_Timber` / `Gallery_End` | 3 m module. Deck at z = H1, depth 1.3 (y −0.3..−1.6). Post 0.22² at (x −1.5, y −1.5) running from z 0 to H1 + 1.05 (left-edge convention; `_End` adds the +1.5 post and a side rail). Joists 0.12×0.2 every 0.75. Knee braces 45°, 0.5 long. Top rail at +1.0 and balusters every 0.2 m (reuse the `balcony()` code). Add `Roof_Pent` above when nothing else covers it. |
| `Stair_Stone_Ext` | Same layout as `ext_stair` (climbs +X over one cell to an upper door at x +3, rise 3.3, 13 steps, width 1.1 at y −0.3..−1.4) but as solid ASHLAR-stepped masonry. Arch void underneath (hw 0.6) as a log store. Landing 1.5×1.1. Outer parapet 0.3×0.7. |
| `Stoop_Stone` | 3 steps, 1.8 wide, rise 0.18, tread 0.35 (top 0.54). Side cheek blocks. For doors on raised foundations. |
| `Prop_CellarHatch` / `_Open` | Stone curb 1.5 (x) × 1.3 (y), sloping 25° from z 0.55 at the wall to 0.1. Two plank leaves 0.72×1.25 with iron straps. `_Open`: one leaf flipped 160°, a VOID well and 3 visible steps. |
| `Corner_Oriel` (timber) | Replaces `Corner_Timber` on one level. Octagon r 0.95 centred at (−0.45, −0.45). Corbelled base: lathe from r 0.2 to 0.95 over 1.2 m below the floor. Body H2 with 3 WINDOW quads on the outward faces and posts on the 8 edges. Cap `Roof_Cone_R1.2` at 2.4 high; it is allowed to pierce the main eave. |
| `Corner_Turret_Stone` | Bartizan: the same geometry in STONE, r 1.0, one arrow slit, cone cap. The body rises 1.2 above the wall top so it pierces the eave (Scottish-baronial look). |
| `Corner_Stone_Door` | Ground corner with a 1.2 m chamfer at 45° holding a 0.9×2.1 door. The upper floor carries the oriel on corbels above it. |
| `Corner_Party` | Pilaster 0.3 wide, projecting 0.12, H1 or H2 tall (stone or timber). Hides the seam where two terrace units' plaster colours change. |
| `Parapet_Crenel` / `Parapet_Corner` | Sits on a wall top. 6 corbels 0.3×0.45×0.4 at x = −1.25 + 0.5·i. Parapet projects 0.35 past the face (y −0.6..−0.25). Breast 0.9 high. 2 merlons 0.9 wide × 0.8 high at x ±0.75: period 1.5, so crenels land at x = 0 and on the module seams. Coping 0.12. STONE walk floor. |
| `Foundation_Skirt` / `_Corner` (`_1`, `_2` for 1 or 2 terrain steps) | Below z = 0: `stone_panel` from −Hs to 0, batter 0.15. See §6. |

### 3.4 Water and crossings

| Piece | Spec |
|---|---|
| `WaterWheel` (animated, `spin_axis = "local X"`) | Overshot, Ø 4.2, width 0.9. Two rims `ring(1.85, 2.10, 0.12)` at x ±0.4. 24 buckets 0.9×0.36×0.05 (PLANKS) at 30°. 8 spokes per side, 0.12², from r 0.25 to 1.9. Hub r 0.32 × 1.1. Axle r 0.14 × 2.4 running into the wall. Pivot at the hub. |
| `WaterWheel_Frame` | Two stone piers 0.6×1.4×2.6 at x ±0.75 with bearing blocks at hub height z 2.3. Tail pit: stone-lined trench 1.3 wide × 5 long, water at z −0.35. |
| `MillRace` | 3 m trough: PLANKS U-channel, inner 0.8 wide × 0.45 deep, floor at z 4.6, WATER at z 4.95. A-frame trestle at x −1.5, legs splayed to ±0.9 and running down to z −1.0 so they can sink into terrain. |
| `MillRace_Spout` / `MillRace_Sluice` | Spout: the trough ends over the wheel crown with a 0.6 m chute at 20° and a WATER sheet falling 0.4 (`FX_Water`). Sluice: a plank gate in grooves plus a windlass, as the on/off tell. |
| `WheelChannel` | Undershot option for river tiles: 3×3 stone-lined channel, inner width 1.4, walls 0.5, water at z −0.8. The wheel hub goes at z +0.7. |
| `Pier_Deck` | 3×3, centred on the cell centre. Deck top z +0.6 over a water plane at z 0. 13 planks along X (0.22 × 0.07, 1 cm gaps, ±1 cm z jitter, 1 plank in 13 shortened). Stringers 0.2×0.3 at y ±1.2. Cap beam along Y at x −1.5. Piles r 0.16 at (−1.5, ±1.35) from z −3.0 to +0.95, with ≤5° seeded lean. X-brace z −1.6..0.3. |
| `Pier_End` / `Pier_Stairs` / `Pier_Rail` | End: +X piles, end cap, reused lamppost, 2 lathe bollards r 0.18 × 0.5, ladder to z −0.8. Stairs: 1.5 wide, from 0.6 down to −0.6. Rail: posts every 1.5 m, 1.0 high, rope sag 0.12 (as in `laundry()`). |
| `Quay_Wall`, `Quay_Wall_Diag`, `Quay_Corner_In/Out`, `Diag_Joint` | ASHLAR face from z −2.0 to +0.8, 0.9 thick, coping 0.25, iron mooring ring. Face −Y toward the water. Diag version: 2.121 m at 45° (see §6). |
| `Boat_Rowboat` / `Boat_Fishing` | Rowboat 4.0×1.35×0.55: hull lofted from 7 ribs (bmesh bridge), PLANKS with UV along the length, 2 thwarts, 2 oars 0.06×2.4. Fishing boat 6.5 m: 5 m mast, furled sail (CLOTH_B cylinder), net heap. The waterline is z 0. |
| `Bridge_Wood_Span` / `Bridge_Wood_Ramp` | Span: 3 m, deck 3.2 wide (planks across Y) with top at z 1.0. 3 stringers 0.25×0.35. Pile bent at x −1.5 (3 piles, r 0.18, to z −3). Railings 1.0 with X panels. Ramp: deck from z 0 to 1.0 over 3 m on a stone abutment. |
| `Bridge_Stone_Arch` | 9 m (3 cells): clear span 6.0, segmental arch rising 2.2 from springing at z −1.0. Deck crown z 2.0, ends at z 0 at x ±4.5. Width 3.6. Voussoirs via `arch_ring(n=15)` on both faces. Parapets 0.4×0.9 with coping. Refuges over the cutwaters. Wing walls splayed 30°. |
| `Bridge_Stone_Culvert` | 6 m piece, 2.4 m arch over a stream, road at z +0.5. |

### 3.5 Defence

| Piece | Spec |
|---|---|
| `Palisade_Straight` | 3 m: 10 logs Ø 0.30 ± 0.04 at 0.3 spacing (x −1.35..1.35). Heights 3.3–3.9 (seeded), 0.45 sharpened cone tip. BARK_OAK shaft, WOOD tip. Sunk to z −0.8. Two inner rails 0.14×0.2 at z 1.0 and 2.6 on the +Y face, with lashings. |
| `Palisade_Walk` (+ `_Ladder`) | Adds an inner catwalk 1.0 wide at z 2.3 (y 0.25..1.25) on posts at x −1.5 and 0. |
| `Palisade_Corner` / `_Gate` / `_Tower` / `_Diag` | Corner: 3 logs Ø 0.4 to 4.2. Gate: posts Ø 0.45 × 5.2 at x ±1.5, lintel log at 4.4, two leaves 1.45×3.4 (one open 80°), optional CLOTH_A banner. Tower: 1 cell, 4 corner logs Ø 0.36 × 6.5, platform at 4.5 with a 1.1 log parapet, thatch pyramid (`guard_tower` pyramid code, smaller). Diag: 2.121 m at 45°. |
| `TownWall_Straight` | 3 m, 2.0 thick (y −1.0..+1.0 centred on the cell edge, outer face −Y). Walk at z **6.0**, which equals the `guard_tower` hoarding floor. Outer face battered +0.35 at the base, fading to 0 at z 1.8. STONE with `grid_cut` and `wall_rocks`. ASHLAR string course at 5.4. Outer parapet (y −1.0..−0.5) with breast to 6.9. Merlons 0.9 wide rising to 7.7 at x ±0.75, each with an arrow slit (VOID 0.1×0.55), coping 0.12. Flagstone walk. |
| `TownWall_Corner_Out/_In`, `_Stair_Lower/_Upper`, `_Ruin`, `_Step`, `_Diag` | Stair: climbs 3.0 over 3 m (12 steps 0.25×0.25) against the inner face (y 1.0..2.1). Ruin: no merlons, ragged top 3.8–5.2, rubble heap from `rock()` (for siege damage and decay). Step: base and walk rise by Hs over the module. Diag: 2.121 m at 45°. |
| `GuardTower_Wall2` / `_WallL` | The existing `guard_tower` (W 4.0, stone to z 6.0) with two 1.2 m gaps cut in the hoarding parapet, opposite (`Wall2`) or adjacent (`WallL`). This turns the **existing tower into the wall tower** with almost no work. |
| `TownWall_Tower_Round` | Centred on a grid vertex, r 3.0, walk at 8.5, 16-merlon parapet ring. Optional `Roof_Cone_R3.4` variant. Three levels of arrow slits. Openings to the wall walk at z 6.0 on ±X. |
| `Gatehouse_Block` | 3×2 cells (9×6), centred on the wall line, masonry to z 6.0. Passage along Y through the middle cell: hw 1.6, spring 2.8, crown 4.4. IRON portcullis (0.08 bars at 0.3 pitch) half raised at y −2.4. Two plank leaves open inward. Half-round flanking towers r 1.8 at (±3.0, −3.0), up to z 9.0, with `Roof_Cone_R2.2`. Above the block, **reuse** `Wall_Timber*` and `Corner_Timber` at z 6.0 (`Wall_Timber_Door` on the end walls opens onto the walk), with `Roof_Hip`/`Roof_Mid` at z 8.8. |

### 3.6 Construction set and stockpiles

| Piece | Spec |
|---|---|
| `BuildSite_Cell` | SOIL quad 2.9×2.9 at z 0.01 with a 0.05 raised border. 4 stakes 0.05²×0.6. String lines 0.01. Bundle of pegs. |
| `Foundation_Wall` / `Foundation_Corner` | `plinth()` plus `stone_panel(z 0..0.6)`. Stage 1 for every wall set. |
| `Wall_Stone_Half`, `Wall_Timber_Skeleton`, `Wall_Wattle_Frame` | Stage 2. Stone: ragged top 1.2–1.9, random per 0.5 m column. Timber: `timber_frame()` with the infill `grid_cut` boxes skipped. |
| `Scaffold_Wall`, `_Ladder`, `Scaffold_Corner` | Standards r 0.07 (BARK_BIRCH) at (x −1.5, y −1.35), z 0–3.6, stackable per storey. Ledgers at 1.5 and 3.0. Putlogs into the wall at x −1.5 and 0. 3-plank decks (0.25×0.04) at y −0.45..−1.25. Dark lashings. Ladder 0.45 wide. |
| `Prop_ShearLegs`, `Prop_Wheelbarrow`, `Prop_MortarTub`, `Prop_LadderLean` | Shear legs: 5 m tripod with rope and an ASHLAR block. The others are simple box/lathe props. |
| `Pile_<Kind>_<1|2|3>` | Fits inside a 3×3 cell, maximum height 1.6. Levels 1/2/3 ≈ 33/66/100%. **Logs**: 2.8 m, r 0.15–0.2, BARK_OAK with ENDGRAIN caps, 3/7/10 logs in a pyramid with chocks. **Planks**: 2 stacks, 4/9/14 layers, stickers every 3 layers. **Stone**: ASHLAR blocks 0.6×0.4×0.35 on pallets, 6/14/24 blocks. **Ore** / **Coal** / **Slag**: flattened jittered ico heap (r 0.8/1.1/1.4, z-scale 0.55) in ROCK with IRON flecks / COAL. **Sacks**: `prop_sacks` on a pallet, 4/9/16. **Wool**: CLOTH_B bales 0.8×0.6×0.6 with twine. **Hides**: stacked HIDE 1.2×0.9 on a trestle. **Fish**: crates of STEEL fish. **Barrels**: `barrel()` 2/4/7. **Bricks**: CLAY 0.25×0.12×0.07 stacks. |
| `Stockpile_Border` | Plank edging 3×3×0.12 for player-zoned storage. |

### 3.7 Livestock and trade props (S each, M for the whole set)

- **Animals** (static placeholders in the `chicken()` style, one mesh each so Unity can swap in rigged versions later):
  - `Sheep`: body ico r 0.42 scaled (1.35, 0.85, 0.85) at z 0.62 in CLOTH_B with jitter 0.04; dark head 0.2×0.18×0.24; legs 0.07²×0.42.
  - `Pig`: ico r 0.4 scaled (1.5, 0.9, 0.85) in PIGSKIN; snout cylinder; curly tail.
  - `Cow`: bevelled body 1.6×0.6×0.7 at z 1.0 in HIDE with PAPER patches; horns.
  - `Goat`: a small sheep in HIDE, with horns.
  - `Horse_Draft`: body 1.7×0.5×0.65, neck at 45°.
- **Pens:** `Prop_PigSty` (4× existing `LowWall` plus a `Roof_Pent` corner shelter and a mud quad), `Prop_SheepShelter` (reuse `LeanTo_Thatch` plus a hay rack), `Prop_HayRack`.
- **Trade props:** `Prop_ChoppingBlock`, `Prop_Sawhorse`, `Prop_SawPit`, `Prop_FrameSaw`, `Prop_Loom` (2.0×1.3×1.8 frame, warp quad, CLOTH_A cloth roll), `Prop_SpinningWheel`, `Prop_DyeVat` (stave `_cyl` r 0.6 × 0.8; the liquid disc is on the **CLOTH_A slot**, so `{"cloth":"Blue"}` makes a blue vat), `Prop_TanningPit`, `Prop_HideFrame`, `Prop_DryingRack_{Fish,Meat,Herbs}`, `Prop_Skep`, `Prop_BeeBench` (3 skeps under a `Roof_Pent`), `Prop_CiderPress`, `Prop_Cauldron`, `Prop_CharcoalMound`, `Prop_Bloomery`, `Prop_BottleKiln`, `Prop_PottersWheel`, `Minecart`, `Rail_Straight/Curve/End` (gauge 0.8, 6 sleepers per 3 m), `Prop_NetRack`, `Prop_FishCrate`, `Prop_TrainingDummy`, `Prop_ArcheryButt`, `Prop_ArmorStand`, `Prop_Stocks`, `Prop_Maypole`, `Prop_Stage`, `Prop_WaysideShrine`, `Prop_Privy`, `Prop_StaddleStone`, `Prop_CoveredWagon`, `Prop_Antlers`, `Prop_Dovecote`, `Tent_A`, `Tent_Bell`, `Prop_Campfire`.
- **Crops:** `Crop_Hops` (4 m poles with vine cards), `Crop_Flax`, `Crop_Barley`, `Crop_Herbs`, `Crop_Saplings`. These are new cells in the `T_VK_Crops` atlas, drawn with `crop_rows()`.
- **Sign emblems:** extend `shop_sign(k, emblem)` with saw, fish, shears, candle, mortar, book, key, ham, pot, hops, scales.

---

## 4. Housing ladder (house types)

| Tier | Type | Beds | Needs to upgrade *into* this tier | Visual tell |
|---|---|---|---|---|
| T0 | Settler camp | 2 per tent | none (spawn) | canvas, campfire |
| T1 | Hovel / Longhouse | 4 / 8 | water within 30 m, 1 food type, firewood | wattle, thatch to 2 m, louvre |
| T2 | Cottage (existing) and new variants | 6 | + 2 food types, chapel coverage, market | stone or plaster ground floor, timber upper, chimney |
| T3 | Townhouse / terrace unit / corner house | 8 + shop slot | + cloth, tavern, healer, paved road | 2–3 floors, shop front, party chimneys |
| T4 | Stone merchant house / courtyard house | 8 + storage 40 | + luxury (candles, cider, dyed cloth), school, bathhouse | all stone, stepped gables, slate, hoist |
| T5 | Tower house / manor | 6 elite + 2 guards | + security (walls or barracks) | tower, bartizans, dovecote |

**T0 Settler Camp** (S)
- *Role:* arrival shelter; the colony's first night.
- *Look:*
  - `Tent_A`: 2.4 × 3.0 × 2.1 A-frame; CLOTH_B canvas with 3 sag rows; ridge pole r 0.05 on forked poles; rolled door flap; guy ropes.
  - `Tent_Bell`: round, r 1.6, conical, for the chief or storage.
  - `Prop_Campfire`: 9-rock ring r 0.6, 5-log cone, GLOW embers, `FX_Fire`.
  - Bedrolls and a cooking tripod.
- *New:* the tents, campfire, bedroll, tripod.
- *Reuses:* `Prop_Crates`, `Prop_Sacks`, `Prop_Cart`.
- *Footprint:* 1 cell per tent; camp 2×2.

**T1 Hovel (cruck cottage)** (M; the wall set carries the cost)
- *Role:* first permanent home.
- *Look:* 2×2 plan, HW 2.4 wattle walls, thatch from z 2.4 (ridge 6.6, eave at 2.1), cruck gable at both ends, `Roof_Louvre` and no chimney. Front `"WD"`, back `".."`. Dressed with a woodpile against a gable, a garden bed and chickens.
- *Variants:* `_Hip` (RoofThatch_Hip ends); `_LeanTo` (`LeanTo_Thatch` goat shed on the back); upgrade look `_Chimney` (`Chimney_Wall` replaces the louvre).
- *New:* the wattle set (6), `RoofThatch_Gable_Cruck`, `Roof_Louvre`, the "Daub" variant.
- *Reuses:* `RoofThatch_Mid/Hip`, `Prop_GardenBed`, `Prop_Chickens`, `Prop_Woodpile`, `Prop_Laundry`, `Deco_Weeds`.
- *Footprint:* 2×2.

**T1b Longhouse** (S once the wattle set exists)
- *Role:* extended family plus 2 livestock slots. A good early farm house.
- *Look:* 4×2, HW 2.4 walls (wattle, or rubble stone via `wall_stone_plain(h=2.4)`). `Wall_Wattle_Byre` in the +X end front cell and the family door in cell 1. RoofThatch_Hip at both ends with a louvre over bay 1. A 2×2 fenced paddock with a cow and sheep off the byre end.
- *New:* none beyond the wattle set.
- *Reuses:* `Prop_Fence`, `FenceGate`, `Trough`, `HayBale`.
- *Footprint:* 4×2 building, lot 6×2.

**T2 new variants** (S each)
- **Log Cabin** (`floors=["Log"]`, Shingle roof, `Roof_Gable_Planks`, `Chimney_Wall`), 2×2 or 3×2. Frontier and forest maps.
- **Stone Cottage** (all-stone, 1 floor plus dormers, `Chimney_Wall`, `Stoop_Stone`). Needs no new pieces beyond the chimney and stoop.

**T3 Rowhouse Terrace** (M for the pieces, S for the builder)
- *Role:* dense housing on the main street. Each unit can carry a shop slot. Firewalls cut fire spread.
- *Eave-front:* units 1–2 cells wide, 2–3 floors, each unit with its own `random_style()`. Rules at a shared boundary:
  - Same height: continue with `Roof_Mid`, and put a `Roof_Firewall` on every second boundary.
  - The taller unit ends in `Roof_Gable_Flush`; its end walls exist only on floors ≥ the lower neighbour's floor count. The lower unit's `Roof_Mid` runs into that wall and is hidden by the 0.25–0.40 wall thickness.
  - `Chimney_Party` on every second boundary.
  - `Corner_Party` pilasters wherever styles differ.
- *Gable-front (Hanseatic street):* each unit is 2 cells of frontage (6 m) × 2–3 cells deep, rotated so the gable faces the street. At party walls:
  - equal heights: both units use the `*_Valley` piece on that side;
  - unequal heights: the lower unit uses the valley piece and the taller keeps its normal eave. Its eave underside clears the lower roof by about 0.1 m for a one-storey difference.

  Street gables alternate between `Roof_Gable_Stepped_Valley*` and the timber `Roof_Gable_Valley*`.
- *New:* `Roof_Gable_Flush`, `Roof_Firewall`, the valley family, `Chimney_Party`, `Corner_Party`, shop fronts.
- *Reuses:* all existing walls, roofs, dormers, balcony, awning, signs.
- *Footprint:* Σ unit widths × 2 cells (eave-front), or 2 × n per unit (gable-front).

**T3b Corner House** (M)
- *Role:* high-value corner plot with two shop fronts.
- *Look:* `build_L_v(a=1, b=1)` with `Corner_Stone_Door` at the ground-floor outer corner, `Corner_Oriel` on floors 1–2 above it, and `S` shop modules on both street faces.
- *New:* `Corner_Stone_Door`, `Corner_Oriel`.
- *Reuses:* `Roof_LCorner`, `InnerCorner_*`, all walls.
- *Footprint:* 3×3 L.

**T4 Stone Merchant House** (S once the pieces exist)
- *Role:* rich trader, with 40 private storage.
- *Look:*
  - 3×2 plan, `floors=["Stone","StoneUpper","StoneUpper"]`, front `"SDS"`.
  - +X gable end: `Wall_Stone_Upper_Loading` on both upper floors in the same cell, under a `Roof_Gable_Hoist`. −X gable: `Roof_Gable_Stepped`. Slate roof.
  - 2 dormers or `Roof_Mid_Hatch`.
  - `Stair_Stone_Ext` up to a counting-room door (`Wall_Stone_Upper_Door`).
  - `Prop_CellarHatch`, and a `Corner_Turret_Stone` or `Corner_Oriel` on one front corner.
- *New:* none beyond §3.
- *Reuses:* `Wall_Stone_*`, `Corner_Stone`, `Roof_Mid`, `Roof_Dormer`, `Awning`, `Prop_Crates`, `Prop_BarrelStack`, `Prop_Cart`.
- *Footprint:* 3×2 plus a 3×1 yard.

**T4b Courtyard House / Coaching Inn** (M)
- *Role:* merchant elite housing, or a tavern upgrade (more rooms, stable slots).
- *Look:* U-plan, 4×4 cells (12×12).
  - Front range 4×2 with `Wall_Stone_Passage` and `Passage_Vault` in cell 2.
  - Wings of 2 cells each via `Roof_LCorner` and `Roof_LCorner_Mirror`.
  - `Gallery_Timber` along the courtyard faces at H1.
  - A well in the courtyard; a stable wing on the back using `Wall_Stall`.
- *New:* passage, vault, gallery, LCorner mirror.
- *Reuses:* `Prop_Well`, `Wall_Stall`, `Prop_Festoon`, `Prop_TavernSign`, tables and stools.
- *Footprint:* 4×4.

**T5 Tower House / Manor** (M)
- *Role:* lord or elite housing; gives security and prestige in an area.
- *Look:*
  - **Tower:** 2×2 plan, `floors=["Stone","StoneUpper"×3]`, walls to 11.4 m. `Wall_Stone_Slit` on the ground floor; entry by `Stair_Stone_Ext` to the first floor. `Corner_Turret_Stone` at all 4 corners of the top floor. 2× `Roof_Hip` forming a pyramid with its apex at 15.6 m, in slate.
  - **Hall range:** 3×2, 2 floors, attached via `Roof_LCorner` (or `Roof_T` for a cross plan), with `Chimney_Wall` on the hall gable.
  - **Grounds:** `Prop_Dovecote` (lathe r 1.4 × 4.2, `Roof_Cone_R1.2` variant at 1.7, rows of VOID holes) as the yard tell; a walled garden using `LowWall` on a 6×5 cell court.
- *New:* `Wall_Stone_Slit`, `Prop_Dovecote`.
- *Reuses:* `Roof_Hip`, `Roof_LCorner`, `LowWall`, `LowWall_Post`, `Tree_Blossom`, `Prop_Fountain`.
- *Footprint:* 2×2 tower plus 3×2 hall; lot 6×5.

**Almshouse** (S)
- *Role:* homeless and unemployed colonists; a faith/charity building.
- *Look:* an eave-front terrace of 4 one-cell units, 1 floor, with `Roof_Bellcote` on the middle unit and a shared garden.

---

## 5. Production and service buildings by chain

```
WOOD    Forester -> trees -> Woodcutter (logs) -> Sawpit/Sawmill (planks) -> Carpenter/Cooper
                                       \-> Charcoal burner (charcoal)
STONE   Quarry (stone) -> Mason (blocks) ; Clay pit -> Kiln (bricks, pots, roof tiles)
METAL   Mine (ore) + charcoal -> Bloomery (iron) -> Blacksmith [exists]
FOOD    Fields [exists] -> Granary -> Windmill [exists] / Watermill -> Bakery [exists]
        Fisher -> Smokehouse ; Hunter/Pigs/Cows -> Butcher ; Orchard -> Cider ; Hops+Barley -> Brewery -> Tavern [exists]
        Apiary -> honey + wax -> Chandler ; Root cellar (veg storage)
TEXTILE Sheep (wool) / Flax (linen) -> Weaver -> Dyer -> Tailor ; Hides -> Tannery -> Cobbler (Sign_Boot exists)
HEALTH  Herb garden -> Herbalist -> Healer's house ; Bathhouse ; Privy ; Wash house
FAITH   Chapel [exists], Wayside shrine, School, Festival green
TRADE   Stockpile yard, Storehouse, Warehouse, Market hall, Trading post
DEFENCE Palisade -> Town wall + Gatehouse ; Guard tower [exists] ; Barracks + training yard
```

### Wood
**Woodcutter's Lodge** (M, or S once the log set exists)
- *Role:* T1 wood source; 2 workers; stores 10 logs; needs forest within 25 m.
- *Look:* 2×2 log cabin, Shingle roof, `Roof_Gable_Planks` at both ends, `Chimney_Wall`. An open `LeanTo` on the +X end shelters `Pile_Logs_3`. Chopping block with an axe stuck in it, a sawhorse, 3 stumps and a fallen log in the yard. The yard tell is the bright end-grain circles of the log pile seen from above.
- *New:* log set, `Prop_ChoppingBlock`, `Prop_Sawhorse`, `Pile_Logs`.
- *Reuses:* `LeanTo`, `Stump`, `Log_Fallen`, `Prop_Woodpile`, `Prop_Cart`.
- *Footprint:* 2×2, lot 3×3.

**Forester's Hut** (S)
- *Role:* replants trees.
- *Look:* 1×2 hut (`RoofThatch_Gable1`, log or wattle walls) beside a nursery: 2 `soil_bed()` cells of `Crop_Saplings` (12 × `Tree_Sapling` at scale 0.5), plus a bucket.
- *New:* `Roof_Gable1`, `Crop_Saplings`.
- *Reuses:* `Tree_Sapling`, `soil_bed`, `Prop_Fence`.
- *Footprint:* lot 3×2.

**Sawpit, then Sawmill** (S, then M)
- *Role:* logs to planks (T1 by hand, T2 powered).
- *Sawpit look:* a pit 3.2 × 0.9 (VOID floor at −1.2, plank-lined), a log across trestles, a two-man saw, and sawdust (PAPER ico chips). Lot 2×1 plus `Pile_Planks`.
- *Sawmill look:* 3×2 with `Wall_Barn_Open` on the front and `Wall_Barn` on the back, RoofThatch or planks roof. `Prop_FrameSaw` (2.6 m posts, blade sash, log carriage on 6 m rails through the building). `WaterWheel` on the +X end, fed by 3× `MillRace` from +Y. `Pile_Logs` goes in and `Pile_Planks` comes out.
- *New:* SawPit, FrameSaw, `Wall_Barn_Open`, the water set.
- *Reuses:* `Wall_Barn`, `Corner_Barn`, RoofThatch/Roof pieces, `Prop_Cart`.
- *Footprint:* 3×2, plus a 1-cell wheel strip and 3 cells of race.

**Carpenter / Cooper** (S)
- *Look:* a 1-storey `build_house_v` cottage on 2×2, with 2× `LeanTo` on the end wall covering a workbench (`Prop_Table` plus tools), a sawhorse, a half-built barrel (splayed staves and a hoop) and `Pile_Planks`. Saw or barrel emblem.
- *Footprint:* lot 3×2.

**Charcoal Burner** (S)
- *Look:* `Prop_CharcoalMound` (hemisphere r 2.0 in SOIL and COAL, 3 vents each with `FX_Smoke`), `Pile_Logs`, `Pile_Coal`, and a `Tent_Bell` or hovel.
- *Footprint:* lot 2×2. Placed at the forest edge.

### Stone and clay
**Quarry** (M–L)
- *Role:* stone; 4 workers; needs rock or cliff terrain.
- *Look:*
  - `Quarry_Face` modules (3 m wide, 4 m high): 2 benches, each step 1.5 high × 0.8 deep, made of big jittered ROCK blocks with flat saw-cut faces. Drill lines as thin VOID quads, rubble at the foot. Plus `Quarry_Face_Corner`.
  - `Quarry_Floor`: 3×3 ROCK slab with a half-split block and iron wedges.
  - `Crane_Treadwheel`: wheel Ø 3.6 × 1.2 with 16 rungs, on a separate animated object. A-frame 4.5 m, 6.5 m jib at 35°, rope, and an ASHLAR block 0.8×0.6×0.5 on the hook.
  - Mason's lean-to, `Pile_Stone`.
- *New:* quarry modules, crane, `Pile_Stone`.
- *Reuses:* `LeanTo`, `Rock_Outcrop`, `Rock_Cluster`, `Rock_Pebbles`, `Prop_Cart`, `Prop_Grindstone`.
- *Footprint:* 3×3. Faces snap to cliff edges (see §6).

**Stonemason's Yard** (S)
- *Look:* a 1×2 lodge (`Wall_Barn_Open` with a thatch roof), 3 banker benches (ASHLAR 1.2×0.6×0.8, each with a half-carved lathe column drum or capital), finished voussoirs, `Pile_Stone`.
- *Footprint:* lot 3×2.

**Clay Pit and Kiln (Potter / Brickworks)** (S–M)
- *Role:* bricks, pots, and roof tiles (the input for upgrading thatch to tile).
- *Look:*
  - Sunken clay pit: 3×3 at −0.6, CLAY with a water puddle.
  - `Prop_BottleKiln`: lathe profile `[(2.2,0),(2.3,1.5),(2.0,3.5),(1.1,5.0),(0.8,6.0)]` in CLAY, with a GLOW stoke-hole and `FX_Smoke`.
  - Potter's wheel, `Pile_Bricks`, and a shop with the `_Pots` goods variant.
- *Footprint:* lot 3×3.

### Metal
**Mine** (M)
- *Role:* iron, coal or gold ore; 4 workers.
- *Look:*
  - `Mine_Portal`: set into a rock face. Two posts 0.35 × 3.0, cap beam 3.6, 3 inner timber sets receding into a VOID tunnel 2.5 deep, plank lagging, `Prop_Lantern`, rubble apron.
  - `Mine_Headframe` for flat maps: an A-frame 6 m tall with a sheave wheel over a stone shaft collar 2.4×2.4.
  - `Rail_*` running out of the portal, `Minecart` with an ore heap, spoil heap.
- *New:* portal, headframe, rails, minecart, `Pile_Ore`.
- *Reuses:* nature rocks, `Prop_Lantern`, `Prop_Crates`, `LeanTo`.
- *Footprint:* 2×2.

**Bloomery / Smelter** (S–M)
- *Role:* ore + charcoal → iron, which feeds the existing Blacksmith.
- *Look:* `Prop_Bloomery`: lathe shaft from r 1.2 to 0.7, 3.2 high, STONE and CLAY, with a GLOW tapping arch, `FX_Fire` and `FX_Smoke`. HIDE bellows under a `LeanTo`, a slag heap, `Pile_Coal` and `Pile_Ore`.
- *Reuses:* `LeanTo`, `Prop_Anvil`, `Prop_Trough`.
- *Footprint:* lot 2×2.

### Food and storage
**Granary** (S–M)
- *Role:* grain storage; lowers the spoilage rate. Rats are a gameplay hook.
- *Look:*
  - 2×2 plan raised on 9 `Prop_StaddleStone`s: mushroom lathe `[(0.18,0),(0.14,0.45),(0.35,0.5),(0.35,0.62),(0,0.64)]`.
  - Floor platform at z 0.7.
  - `Wall_Granary` / `_Door` / `Corner_Granary`: vertical PLANKS, 2.4 high, running from z 0.7 to 3.1, with one brace.
  - 2× RoofThatch_Hip (pyramid) at z 3.1, or a `Roof_Gable_Hoist` variant.
  - Detached stone steps that stop 0.3 short of the door (rat-proof, historically accurate).
- *Reuses:* the roof pieces, `Prop_Sacks`.
- *Footprint:* 2×2.

**Storehouse (T2) / Warehouse (T3)** (S compositions)
- *Storehouse:* 3×2 with `Wall_Barn`, `Wall_Barn_Door` and one `Wall_Barn_Open` cart bay, a 3×2 `Stockpile_Border` yard in front, and mixed piles.
- *Warehouse:* stone ground floor with a `Wall_Stone_Passage` cart door, then `StoneUpper` ×2 with stacked loading doors under a `Roof_Gable_Hoist`, plus `Roof_Mid_Hatch`.
- *Double-pile warehouse:* 3×4, two parallel ranges joined by `Roof_Mid_ValleyL/R`, both ends `Roof_Gable_Stepped`. The M-roof silhouette is a strong roof tell.
- *Footprint:* 3×2 or 3×4.

**Root Cellar** (S)
- *Role:* vegetable storage; low spoilage.
- *Look:* an earth mound (half-ellipsoid 3×4, 1.6 high, SOIL with `Plant_TallGrass` on top) with a stone portal front (`wall_stone_door` arch scaled 0.8, plus wing walls) and a vent pipe.
- *Footprint:* 1×2.

**Watermill** (S once the water set exists)
- *Role:* flour; an alternative to the windmill when water is nearby.
- *Look:* a 3×2 cottage (stone and timber) with `WaterWheel` and `WaterWheel_Frame` on the +X end (hub x = L/2 + 0.8, z 2.3), `MillRace` ×3 on trestles plus `MillRace_Spout` and a `Sluice`. Sacks and a cart.
- *Footprint:* 3×2 plus 1 wheel cell plus race.

**Fisher's Hut and Pier** (M)
- *Role:* fish; 2 workers; needs a water tile.
- *Look:* a 1×2 hut (`RoofThatch_Gable1`, log walls or `Wall_Granary` planks on short stilts), `Pier_Deck` ×2 plus `Pier_End`, a moored `Boat_Rowboat`, `Prop_NetRack`, `Prop_FishCrate` stack, `Prop_DryingRack_Fish`.
- *Footprint:* 1×2 on land plus 1×3 of pier over water.

**Smokehouse** (S)
- *Role:* preserves fish and meat.
- *Look:* 1×2 plan, stone H1 walls, `Roof_Gable1` with `Roof_Louvre`, a soot vertex-colour gradient near the top, drying racks, woodpile, `FX_Smoke`.
- *Footprint:* 1×2.

**Hunter's Lodge** (S)
- *Look:* a 2×2 log cabin with `Prop_Antlers` over the door, 2× `Prop_HideFrame`, `Prop_DryingRack_Meat`, `Pile_Hides`.
- *Footprint:* lot 3×3.

**Butcher** (S)
- *Look:* a 2×2 cottage with `Wall_Stone_Shop_Meat` and a chopping block; `Prop_PigSty` behind.
- *Footprint:* lot 2×3.

**Pig Sty / Sheep Farm / Cattle Byre** (S each, M for the animals)
- *Pig sty:* 3×3, 4× `LowWall`, a pent-roof shelter, mud, 3 pigs.
- *Sheep farm:* 3×3 `Prop_Fence` pen, `Prop_SheepShelter`, 6 sheep, a shearing bench, `Pile_Wool`.
- *Byre:* `build_barn(n=2)` with a paddock, 3 cows and a trough.

**Orchard and Cider House** (S)
- *Look:* a 2×2 orchard of 4 `Tree_Apple` (scale 0.8) with `Prop_LadderLean` and apple crates, next to a 2×2 cottage with a `LeanTo` covering `Prop_CiderPress` (frame 1.4×1.0×2.0, screw r 0.1, basin) and barrels.
- *Footprint:* lot 4×2.

**Apiary and Chandler** (S)
- *Apiary:* 2× `Prop_BeeBench` (skep: lathe dome r 0.28 × 0.45 in HAY) in a 2×2 plot of `Crop_Lavender`.
- *Chandler:* a townhouse with `Wall_Plaster_Shop_Candles` and a candle sign.

**Brewery / Malthouse with Oast** (M)
- *Role:* barley + hops → ale, feeding the Tavern (a T2/T3 need).
- *Look:*
  - A 3×2 stone-and-timber range.
  - An attached oast kiln: round lathe tower r 2.2 (16 segments) with walls to 5.0, `Roof_Cone_R2.2` at 4.2 high (slate or tile).
  - A **white timber cowl** on top: 0.9×0.9×1.0 PAPER-white planks with a tilted hood and a vane board. This is the roof tell.
  - A hop garden (`Crop_Hops`), `Crop_Barley`, barrels.
- *Footprint:* 3×2 plus oast 2×2; lot 5×3.

### Textile and leather
**Weaver's House** (S)
- *Look:* a townhouse with a `Wall_Plaster_Shop_Cloth` front under a `Roof_Pent`, and a `Prop_Loom` visible inside and in a `LeanTo`. Spinning wheel at the door. Shears emblem.

**Dyer's Yard** (S)
- *Role:* dyed cloth (T4 luxury).
- *Look:* 3–4 `Prop_DyeVat`s placed with different `{"cloth": Red/Blue/Yellow/Green}` styles. This reuses the variant mechanism and gives a strong coloured-circle yard tell. `Prop_Laundry` with long cloth strips, a small hovel, and ideally a stream.
- *Footprint:* lot 3×2.

**Tannery** (S–M)
- *Role:* hides → leather. It smells, so it must be placed at the edge of town (a gameplay constraint).
- *Look:* 4 `Prop_TanningPit`s (stone rim 1.2×1.2 with brown HIDE-tinted liquid), 3 `Prop_HideFrame`s, a `LeanTo`, `Roof_Louvre` on a 2×2 shed, `Pile_Hides`.
- *Footprint:* lot 3×3. The Cobbler already exists as a sign (`Sign_Boot`).

### Health, hygiene and culture
- **Herbalist** (S): a hovel or cottage, `Crop_Herbs` plus `Crop_Lavender` beds, a pole of 6 herb bundles under the eave, `Prop_Cauldron`, `Sign_Potion` (existing). Lot 3×3.
- **Healer's House / Infirmary** (S–M): 3×2, 2 floors, `Gallery_Timber` on the front, `Roof_Bellcote`, herb garden, benches, a well. Mortar emblem. Lot 3×3.
- **Bathhouse** (S–M): a 3×2 stone single storey with 2× `Roof_Louvre` (steam `FX_Smoke`), a `MillRace` feed from a pond or well, `Prop_BathTub` (half barrel r 0.7 with WATER), laundry. Lot 4×3.
- **Privy** (S): 1.2×1.2×2.2 plank booth, `Roof_Pent` at 12°, VOID crescent cut-out in the door. Hygiene radius of about 12 m.
- **Wash House** (S): a 2×2 pavilion (4 posts plus 2× `Roof_Hip`) over a stone basin 4×2 with WATER, plus laundry lines.
- **Wayside Shrine** (S): a cheap faith-coverage extender. Pillar 0.6×0.6×1.8 on 2 steps, a gabled niche (2 ROOF slabs 0.9×0.5), PAPER lathe statue, GLOW candles, flowers. Sub-cell size, for crossroads.
- **School / Scriptorium** (S): a 3×2, 2-floor house with `Roof_Bellcote`, a book sign, and a benches yard.
- **Festival Green** (S): `Prop_Maypole` (7 m pole, 8 CLOTH_A ribbons to r 3), `Prop_Stage` (plank platform 6×3×0.8 with a CLOTH_A canopy), `Prop_Festoon` (existing), a bonfire. Happiness building.

### Trade, civic and defence
- **Market Hall** (S, pure reuse): 3×2 with `Wall_Arcade` on all 10 perimeter modules plus `Corner_Stone`, `Wall_Timber*` above, `Roof_Hip` ends, `MarketStall`s underneath.
- **Trading Post** (S): `Prop_CoveredWagon` (a four-wheel version of the `Prop_Cart` chassis with 5 hoops and CLOTH_B cover 3.4×1.6), a hitching rail, `Tent_Bell`, crates, a scales emblem. Lot 3×3 by the entrance road.
- **Barracks and Training Yard** (S–M): `build_house_v(n=4, 2 floors)` with `Wall_Stone_Slit` on the ground floor and `Gallery_Timber` on the yard side. `Prop_WeaponRack` (existing), `Prop_TrainingDummy`, 3× `Prop_ArcheryButt` at 15 m, `Prop_ArmorStand`, a flag. Lot 4×5.
- **Stocks** (S): public order.
- **Palisade ring** (M), then **Town wall plus Gatehouse** (L): the pieces from §3.5. The tower spacing rule is one `GuardTower_Wall2` every 4–6 modules.

---

## 6. Terrain hooks (marching-squares tiles)

1. **Buildable rule.** A footprint is buildable if all (w+1)(d+1) corner heights are equal. With `Foundation_Skirt_1/_2`, the allowed corner difference is 1 or 2 steps (Hs). The building sits at the highest corner, skirts fill the lower edges, and `Stoop_Stone` or `Stair_Stone_Ext` serves the doors. Author the skirts for the terrain track's Hs, or build them parametrically.
2. **Contour-following modules** (quay, retaining wall, palisade, town wall). A midpoint (non-interpolated) marching-squares contour only ever produces two segment types:
   - **straight, 3.0 m**, from one edge midpoint to the opposite edge midpoint, running along the cell centre-line;
   - **diagonal, 2.121 m at 45°**, between adjacent edge midpoints. Cases 1, 2, 4, 8 and their complements; the saddles 5 and 10 are two diagonals.

   So each set needs `_Straight`, `_Diag` and a `Diag_Joint` post or buttress that hides the 135° mitre. The pivot is at the segment midpoint with the outer face −Y. If the terrain uses interpolated contours instead, only the palisade (round logs) tolerates arbitrary angles.
3. **Retaining_Wall set** (dry stone, same modules as the quay) plus `Stair_Terrace` (1 cell, climbs Hs) for hill villages.
4. **Water pieces.**
   - Pier decks sit at water + 0.6, with piles to −3.0, so any water depth ≤ 3 m works.
   - `Quay_Wall` faces the water tile.
   - `Bridge_Stone_Arch` spans 2 water cells with its abutments on land cells.
   - `WheelChannel` occupies one river tile.
5. **Cliff-edge pieces.** `Quay_Wall` (as a dry cliff face), `Mine_Portal` and `Quarry_Face` snap to height-step edges, facing −Y into the rock, in 1-step and 2-step heights.
6. **Legs and piles** on the mill race, pier, palisade and bridge bents all run 0.8–3.0 m below z = 0, so small terrain deviations never show a gap.

---

## 7. Builder API sketch

```
def build_generic(coll, origin, plan, style, stage=4):
    # plan = dict(n=3, floors=["Stone","StoneUpper","StoneUpper"],
    #   front="SDS", back="W.W", ends=("L.","W."),
    #   roof=dict(ends=("stepped","hoist"), valley=(None,None), dormers=[1], louvre=[], bellcote=None, chimney=("wall",0)),
    #   attach=[("Gallery",face,cells),("Stair_Stone",face,cell),("CellarHatch",face,cell),("Oriel",corner,level)],
    #   yard=[("Pile_Logs",dx,dy,fill),("Prop_DyeVat",dx,dy,{"cloth":"Blue"})])
    root = make_root(plan, style)                 # BLD_ empty + metadata + sockets
    top  = _assemble2(...)                        # walls per floor kind, via place_stage()
    roofs(...); attachments(...); yard(...)

def build_terrace(coll, origin, units, frontage="eave"):   # units: [(w_cells, floors, style, ground_str)]
    for i,u in enumerate(units):
        L,R = neighbours(i)
        end_walls(u, side, from_floor = 0 if nb is None else nb.floors)   # only above a lower neighbour
        roof_end = "Gable" if nb is None else ("Gable_Flush" if nb.floors < u.floors else "Mid")
        if nb and nb.floors == u.floors and i % 2: place("Roof_Firewall", boundary)
        if frontage == "gable": use *_Valley{L,R,B} per side (equal height -> both truncated; unequal -> lower only)
        if i % 2: place("Chimney_Party", boundary); if styles differ: place("Corner_Party", boundary)

def build_stockpile(coll, origin, kind, fill):  # fill 0..1 -> None|1|2|3
    lvl = 0 if fill <= 0 else min(3, 1 + int(fill * 3 - 1e-6))
    if lvl: place_v(coll, f"SM_VK_Pile_{kind}_{lvl}", ...)
```

---

## 8. Roadmap

| Sprint | Content | New meshes (approx.) | Effort |
|---|---|---|---|
| **A: Early-game loop** | Material and variant infra, root/sockets, `STAGE_SUBST`; stockpiles (Logs, Planks, Stone, Sacks ×3); construction set; wattle set, cruck gable, louvre; tents and campfire; Hovel and Longhouse; Privy; Shrine; `Roof_Gable1`; `Chimney_Wall` | ~40 | M |
| **B: Production chains** | Log set; `Wall_Barn_Open`; Woodcutter, Forester, Sawpit, Carpenter, Charcoal; Granary, Storehouse, Root cellar; Quarry, crane, Mason, Kiln; Mine, rails, Bloomery; animals and pens; Weaver, Dyer, Tannery, Hunter, Butcher; Herbalist, Orchard, Apiary; the remaining pile kinds | ~60 | L (many S items) |
| **C: Water** | Wheel, frame, race, sluice, channel; Watermill; Sawmill; pier set; boats; Fisher; Smokehouse; quay set; bridge set | ~25 | M–L |
| **D: Town growth** | Stone upper set; shop fronts; Flush/Stepped/Firewall/Valley/T/LCorner_Mirror/Hoist/Pent/Bellcote/Hatch/Cone roofs; `Chimney_Party`; `Corner_Party`, Oriel, Turret, Corner door; Gallery, stone stair, stoop, cellar hatch, passage and vault; terrace builder; Corner house; Merchant house; Courtyard inn; Market hall; Healer; Bathhouse; School; Brewery with oast; Warehouse | ~45 | M–L |
| **E: Defence and elite** | Palisade set; town wall set; `GuardTower_Wall2/L`; round tower; gatehouse; parapet; Tower house and manor; Barracks and training props; Festival green; Trading post; Dovecote; Almshouse | ~30 | L |

The only files touched are `vk_helpers.py` (pieces, builders, `kit_mats` append, variants) and `vk_texgen.py` (`gen_wattle`, and the slate and shingle palettes for `gen_roofs`). All reference code is in `C:/Users/danie/AppData/Roaming/Claude/scratch-workspaces/ec03f06b-60f5-4d5d-94a9-dff3a56c5f56/f8ddc2b6-f8a4-41c6-98db-14b97d4348ea/scratch-2026-09-23-d49817/code/`.