# Survey B: textures and materials for the interior kit

## 0. Summary

- **The toolkit carries over to interiors unchanged.** Every surface generator is numpy code. The noise is FFT-based and the voronoi, segment and dome helpers wrap, so each map tiles exactly at its tile size `T`. Each generator writes a 5-map set through `write_set`, saves PNGs to `assets/textures` and packs them into the .blend. The hand-painted look comes from `paint_form_light` in `vk_tex2`. New interior textures should be new `gen_*` functions written like the vk_tex2 ones, plus a few new parameters on existing generators, always with defaults that reproduce today's output bit for bit.
- **The 1.5 m grid sets the tile size.** Kit UVs are planar and in object-local space. They are only continuous across 1.5 m pieces when `1.5/t` is a whole number (§3). **Every floor and wall texture should use t = 1.5.** Of the existing textures, only Plaster was authored at 1.5, and the kit projects it at 2.2. Cloth (0.5), Iron (0.5) and Paper (0.3) also divide 1.5, but they are only used on props.
- **Reusable indoors as they are:** Wood, Planks (furniture only, not floors), PaintedWood, Iron/Bronze/Steel, Cloth tints, Burlap, Paper, the Goods atlas, Water, Bark/EndGrain (firewood), Coal, Hide and Void. Window and Stained are reusable through brighter material variants.
- **Not reusable indoors as they are:**
  - Stone, FieldStone and StoneBlock: moss, lichen and a 3 m or 1.2 m tile.
  - Ashlar: 3 m tile.
  - Wattle: 1 m tile.
  - Planks as a floor: 2 m tile, no butt joints, and nail rows plus grey stripes that read as outdoor decking.
  - Plaster: two hairline cracks that would repeat every 1.5 m. That breaks the handoff's "no repeating decals" rule.
  - Dirt: grass sprigs and a 4 m tile.
  - Straw: too busy and too saturated.
- **What's new:**
  - Floors: Floorboards (NS/EW, with edge-locked B/C variants), Flagstone, FlagRustic, EarthFloor (plus a sooty version), StrawBed.
  - Walls: PlasterIn, StoneIn, AshlarIn, WattleIn.
  - Other textures: StoneBlockIn, Brick, Ash, and a Textiles atlas (rugs, runner, hangings, quilt, blanket).
  - About 7 material-only variants that need no new texture: Window_Day, Stained_In, GlowIn, Wax, WoodDark, WaterMurky, and Ale/Foam as flat colours.

---

## 1. How textures and materials are made today

**Load order.** The texture texts are not run by the `vk_kit` loader; they are exec'd on demand into one namespace:
- `vk_tex` holds the helpers: `grid, fbm, blur, smooth, voronoi, voronoi_edge, normal_from_height, cavity_ao, painted_light, draw_segments, crack_segments, wrapd, lerp, smin, down2, hx, luma, write_map, write_set`.
- `vk_texgen` holds the first-generation generators and the helpers `facets, weave, lattice, warp, ramp3`.
- `vk_tex2` holds the v2 generators and the helpers `stone_layout, paint_form_light, lichen_dots, voronoi_edge2, _stamp_domes, _per1d`.
- `vk_goods` holds the goods atlas. The order it documents is vk_tex, vk_texgen, vk_tex2, vk_mat, vk_goods.

**Writing maps.** `write_set(prefix, albedo, height, rough, depth_m, tile_m, ao=None, ao_in_albedo=0.55, extra=None)` (`src/textures/vk_tex.py` L69):
- AO defaults to `cavity_ao(height)`. The BC map is `albedo*(1-k+k*AO)`, so **AO is baked into the albedo**.
- It writes `_BC` (sRGB), `_N`, `_H`, `_R` and `_AO`, plus any extras such as `_M`, `_Mask` or `_A`, all as Non-Color.
- `_N` comes from `normal_from_height(h, depth_m, tile_m)`. It is tangent-space OpenGL (Y+), which is Unity's convention, and its slope is in real metres because `px = tile_m/S`.
- `_R` is roughness, not smoothness.
- `write_map` (L54) creates or updates an S×S RGBA image, flips the rows, saves `<VK_ROOT>/assets/textures/<name>.png` and calls `img.pack()`.
- `PBR_SETS[prefix] = {depth, tile}` is a runtime-only registry.

**Resolution.** The vk_tex2 recipe paints at S=2048, stores at 1024 via `down2`, and runs `cavity_ao` on the downsampled height with `ao_in_albedo` between 0.25 and 0.45. Stored sizes are 1024 for nearly everything, 512 for Cloth, Burlap, Iron, Window, Stained, Paper, Soil and Water, and 2048 for Goods. The first-generation generators size their features per tile, so their `tile` argument only changes normal strength. The vk_tex2 ones size features in metres (`r/px`), so changing `T` changes the repeat but keeps feature size.

**Painted light.** `paint_form_light(col, h01, depth, T, hig, log, post, ex)` lights from `Ln = (-0.12, 0.80, 0.58)`, which is **from the top of the image (+V)**, slightly left. The shading is posterised, with highlight `#F4E9CC` and a cool purple shadow `#3E3A4C`. Generators then add rim and underside bands and a cast shadow by rolling the height map. On walls +V means light from above. On floors +V is local +Y, so the light reads as coming from the top of the screen when the camera looks along +Y.

**Materials.** `pbr_material` (`src/core/vk_mat.py` L2) builds a Principled BSDF:
- Base colour is BC, optionally multiplied by `tint`, or `flat` × luma, or mixed through a `paint` mask. It can then go through HSV and a per-instance `jitter` (Object Info Random), and is always multiplied by vertex colour `Col`.
- Roughness is `_R × rough_mul`. Normal is `_N` through a Normal Map node at strength `nstr`. `metal_map` reads `_M`. `emission` feeds the colour into emission.
- `_H` and `_AO` are not used.

**Material registry.** `MAT_MAP` (L62) maps names to kwargs, and `apply_pbr_all()` (L130) rebuilds every listed material by name, plus `TONE_MAP` and `M_VK_Void`. `vk_helpers` overrides `tex_mat` (L2238): an existing material of that name wins; otherwise it builds PBR if `<img>_BC` exists, else falls back to a legacy flat colour × `Col`. Per-instance restyling uses `VARIANT_MATS`, `variant_mat` and `variant_mesh` for the kinds plaster, shutter, roof, cloth, stone and window, driven by `SLOT`.

**Slots and UVs.**
- `kit_mats()` (vk_helpers L47) returns 55 materials, and indices come from the unpack at L70. `finish()` appends all 55 to every mesh.
- `Kit.project` (L205) uses planar UVs: object-local metres divided by `TILE[slot]` (L6). Horizontal faces use U=+X, V=+Y. Vertical faces use U = n × Z, V = +Z. WOOD and SHUTTER run along the box's longest axis.
- `box()` adds a **pseudo-random UV offset per box** from a hash of its centre (L245–246). The only exception is an unbevelled STONE, ASHLAR or FIELDSTONE box.
- STONE faces with |n.z| > 0.7 become STONE_BLOCK.
- `finish()`: the wobble runs after UVs are assigned, so it never moves them. Grime multiplies vertex colour by `g = 0.62 + 0.38*clamp(z/0.9)`, and by a further 0.72 on undersides.

**Terrain materials** (`M_VK_Terrain`, `M_VKT_Paving/Curb/Stair`) sample Object coordinates of unrotated map chunks. That only works because the chunks sit unrotated at the map origin, so it is not usable for instanced pieces.

---

## 2. Inventory of existing textures

For each texture: file, what it looks like, tile size (generator tile / kit TILE), the slot and materials that use it, and the verdict for interiors.

### `vk_texgen.py`

- **`gen_plaster`** (T_VK_Plaster)
  - Look: calm cream limewash with soft blotches and 2 hairline cracks; brick patches are off.
  - Tile: 1.5 / **PLASTER 2.2**. The kit enlarges it 1.47×, and 3/2.2 is not a whole number.
  - Used by: M_VK_Plaster, White/Ochre/Rose (MAT_MAP), Daub/Sage/Sky (VARIANT_MATS), and M_VK_Clay (terracotta tint).
  - Verdict: walls only after a crack-free re-generation at 1.5 m. Clay pots are fine as they are.
- **`gen_wood`** (T_VK_Wood)
  - Look: dark streaky brown beam grain, knots, long cracks.
  - Tile: 1.6 / 1.6.
  - Used by: WOOD, Shutter_Natural, the tinted shutter variants and M_VK_Hewn (grain remapped pale).
  - Verdict: reuse for beams, posts, furniture, pews and casks. The per-box offsets are fine because these need no continuity.
- **`gen_planks`** (T_VK_Planks)
  - Look: 8 full-length boards 0.25 m wide, orange mixed with 30 % grey boards, 2 rows of nails, dark gaps.
  - Tile: 2.0 / 2.0 (PLANKS).
  - Verdict: reuse for tabletops, shelves, doors, crates and counters. Not for floors: 2.0 does not divide 1.5, there are no butt joints, and the look is weathered decking.
- **`gen_paintedwood`** (T_VK_PaintedWood + `_Mask`)
  - Look: wood under chipped paint.
  - Tile: 1.6 (SHUTTER).
  - Used by: Shutter_Teal/Red/Green/Blue and their Worn versions (`wear=1`).
  - Verdict: reuse for painted chests, cupboards and doors.
- **`gen_iron`** (T_VK_Iron + `_M`)
  - Look: hammered dark metal with rust.
  - Tile: 0.5 / 0.5.
  - Used by: IRON (metal map), BRONZE (flat colour, metallic), STEEL.
  - Verdict: reuse for anvil, tools, hoops and hinges; Bronze doubles as brass or gilt for candlesticks.
- **`gen_window`** (T_VK_Window)
  - Look: diamond leaded glass, bluish, with a reflection streak.
  - Tile: 1.0.
  - Used by: WINDOW and M_VK_Window_Lit (emission masked by blue − red).
  - Verdict: reuse through a daylight variant.
- **`gen_stained`** (T_VK_Stained)
  - Look: diamond lattice in 6 saturated colours.
  - Tile: 1.0.
  - Used by: STAINED, emission 0.5.
  - Verdict: reuse for the chapel lancets with more emission.
- **`gen_straw`** (T_VK_Straw)
  - Look: dense, bright, high-contrast crosshatched strands.
  - Tile: 1.2 / 1.2.
  - Used by: HAY.
  - Verdict: not for floors or bedding; needs a new calmer texture.
- **`gen_burlap`** (T_VK_Burlap): coarse tan weave, tile 0.8, BURLAP. Reuse for sacks and mattresses (props only).
- **`gen_cloth`** (T_VK_Cloth)
  - Look: fine white weave.
  - Tile: 0.5.
  - Used by: the MAT_MAP Cloth_Red/Cream/Blue/Green/Yellow tints and CLOTH_A/B.
  - Verdict: reuse for linen, tablecloths, curtains and pillows. 0.5 divides 1.5.
- **`gen_soil`** (T_VK_Soil): dark clods and pebbles, tile 1.0, SOIL. Not for interiors (garden soil, too dark).
- **`gen_paper`** (T_VK_Paper): parchment with ink lines, tile 0.3, PAPER. Reuse for ledgers, notices and books.
- **`gen_water`** (T_VK_Water): flat teal, tile 1.0, WATER. Reuse for the quench trough and washtubs with a murky tint.
- **`gen_rock`** (T_VK_Rock): faceted rock with moss and lichen, tile 1.5, ROCK and RockMossy. Not for interiors (natural rock).
- **Roofs** (`gen_roofs`, `gen_thatch`, and vk_tex2 slate/shingle), tile 3.0: not needed, because top-down interiors have no ceilings.
- **`gen_clock`, `gen_moss`, `gen_foliage`, `gen_crops`**: not needed. At most, a potted herb could use the foliage or crops atlas.
- **`gen_bark_*`, `gen_endgrain`** (nature), tiles 1.0–1.4 and 0.6: reuse for firewood, log benches and chopping blocks.

### `vk_tex2.py`

- **`gen_stone`** (v2 coursed rubble)
  - Look: chunky stones in 7 courses of about 0.43 m, pastel greys, moss tufts on stone tops, lichen, cracks. Also writes `T_VK_Stone_stones.json`.
  - Tile: 3.0 / 3.0.
  - Used by: STONE and the Warm/Cool/Dark tints.
  - Verdict: the style is right, but 3 m does not divide 1.5 and moss is wrong indoors. Becomes **StoneIn**.
- **`gen_stoneblock`**
  - Look: jointless dressed-stone surface with 3×3 facets, 1–2 lichen spots, 1 crack.
  - Tile: 1.2 / 1.2. DRESS is missing from TILE, so it falls back to 1.0.
  - Used by: STONE_BLOCK, DRESS, and the terrain curb and stair materials.
  - Verdict: lichen is wrong indoors. Becomes **StoneBlockIn**.
- **`gen_fieldstone`**
  - Look: rounded rubble in soil joints with 6–8 % moss, plus lichen.
  - Tile: 3.0 / 3.0.
  - Used by: FIELDSTONE and the "Field" stone style.
  - Verdict: not as it is. It is the basis for **FlagRustic**.
- **`gen_wattle`**
  - Look: horizontal rods woven around stakes every 0.25 m, with grey patches.
  - Tile: 1.0 / 1.0 (WATTLE).
  - Verdict: partitions only, after re-generation at T=1.5.
- **`gen_ashlar`** (v2)
  - Look: pale S2 blocks, 6 courses of 0.5 m with 4–5 blocks each.
  - Tile: 3.0 / 3.0.
  - Used by: ASHLAR (chapel).
  - Verdict: the style is right. Re-generate at 1.5 as **AshlarIn** and **Flagstone**.
- **`gen_dirt_v2`**
  - Look: calm warm brown with clods, pebbles, green grass sprigs and straw bits.
  - Tile: 4.0 (terrain layer).
  - Verdict: not as it is (grass indoors, 4 m). It is the basis for **EarthFloor**.
- **Grass, cliff, cobble, sand, terrain macro and net:** not needed. They are terrain textures at 4–6 m tiles, sampled by object-space materials.

### Goods atlas

`vk_goods.gen_goods_atlas` writes T_VK_Goods at 2048: a 4×4 grid of 16 food and hide cells, mapped with its own UVs by `goods_map`. Reuse it for pantries, kitchens, the tavern, and hams, sausages and herb bundles hanging from beams.

### Flat-colour slots

Glow (emission 4.0), Coal, Hide, Pigskin, Bread, Apple, Pumpkin, Leaf, the flowers, the mushrooms and Void. Void is useful as the black fill beyond the walls and in stairwells. **GLOW clips to white under the Standard view transform** (see the forge in `docs/images/blacksmith.jpg`), so it would render as white blobs in a dim interior.

---

## 3. UV rule: keeping textures continuous across 1.5 m pieces

**Why it works.** `Kit.project` computes `u = p·U/t` in local space. For an unrotated piece whose origin sits at `X0 = 1.5·i`, `u = (X−X0)/t`, which equals `X/t (mod 1)` exactly when `1.5/t` is a whole number. So local planar UVs are world-aligned for free, provided these rules hold:

- **R1. Tile size.** `t ∈ {1.5, 0.75, 0.5, 0.375, 0.3, 0.25}`. Use **1.5 for every floor and wall texture**. Never use 3.0, because a 3 m piece can sit on an odd 1.5 m position.
- **R2. Origins.** Every piece's origin is on the 1.5 m lattice, with one convention for all pieces.
- **R3. No UV offset.** World-locked slots must skip `box()`'s hash offset: `off = (0,0) if mi in WORLD_LOCKED`.
- **R4. Floors are never rotated.** A 90° rotation turns the pattern, and a 180° rotation mirrors it (seam-safe only if the texture were mirror-symmetric along its edge columns, which none are). Plank direction is therefore **two textures**, `_NS` and `_EW`, built by transposing the board layout **before** `paint_form_light`. The painted light stays on +V for both, the UVs stay U=X, V=Y, and one mesh serves both through a material variant. Tag floor pieces with `o["uv_lock"]="no_rotate"` so Unity can warn.
- **R5. Walls.** All pieces in a straight run share one rotation (room side on the same side), so U is continuous. V is z starting from 0, so a full-height piece and a 1 m cutaway piece match exactly along a run: the cut piece's texture is the full piece's lower metre. U restarts at corners; posts or quoins hide that.
- **R6. No bevels on seams.** Floor-slab edges and wall butt ends must not be bevelled, because a bevel makes a groove every 1.5 m and shows the grid. The texture supplies the joints.
- **R7. Grime and wobble.** The wobble runs after UVs are assigned, so it never breaks texture continuity (geometry seams are Survey A's topic). **Floors must be built with `grime=False`**; otherwise g = 0.62 at z = 0 and the whole floor is 38 % darker. Walls keep grime: dirt at the base looks right and depends only on z, so it stays continuous.
- **R8. TILE entries.** Every new slot needs a TILE entry. `TILE.get(mi, 1.0)` silently falls back to 1.0; DRESS already does this.

**Repetition.** A 9×12 m room shows 48 copies of a 1.5 m tile.
1. **Even content.** Author statistically even tiles: at least 12 elements per tile with spread tints, no single standout feature (one knot, one crack, one dark board), and low-frequency colour drift of at most ±3 %.
2. **Edge-locked variants B and C.** Keep the same layout. Elements that touch a tile edge (board segments crossing v=0/1, flags crossing an edge) keep their random draws; only interior elements get new tints, grain offsets and knots from `default_rng(seed+1000*variant)`. Any variant can then sit next to any other, and designers mix A/B/C freely. The cost is two more 1024 sets per floor type.
3. **Fallback, only if repetition still shows:** 3 m textures with UV offsets by position parity, done either as four mesh variants per piece or as a Unity editor component that sets a per-renderer `_BaseMap_ST` offset of `frac(worldPos/3)` (a MaterialPropertyBlock, no custom shader). Designers would easily get the variants wrong, so this is not the default.

**Texel density.** 1024 px over 1.5 m is 683 px/m; exterior textures are 341–512 px/m. An interior camera 15–20 m away gives roughly 90 px/m at 1080p, so mip level is about 3 and a tile effectively has about 130 px. Design shapes of at least 3 cm and dark joints of at least 6 mm with AO. Avoid lines thinner than 1 cm (the handoff's "hairs" note). Store at 1024 to leave room for zooming in.

---

## 4. New textures to add

All of these tile at 1.5 m unless stated otherwise. They are generated at 2048, stored at 1024 with `down2`, and written with `write_set(out_prefix, bc, h1, R1, depth, T, ao=cavity_ao(h1,(2,6,18),(2.0,1.5,0.8),0.45), ao_in_albedo≈0.35)`. The hand-painted look comes from `paint_form_light` with a light touch (`hig 0.10–0.15, log 0.16–0.22, post 0.2–0.3`). Moss and lichen are off indoors.

### 4.1 T_VK_Floorboards_NS / _EW (+ _B, _C) — new `gen_floorboards(S=2048, seed=611, T=1.5, depth=0.02, nb=6, orient="NS", variant=0, out_prefix=…)`
Used for townhouse and upper floors, the tavern hall and guest rooms.
- **Layout.** `u = x·nb`, giving 6 boards of 0.25 m (5 boards of 0.30 m for the tavern). Each board has 2 butt joints: `j1 ~ U(0,1)` and `j2 = (j1 + U(0.35,0.65)) % 1`. The joints of neighbouring boards must be at least 0.12 m apart; re-draw until they are, as in `stone_layout`. The segment wrapping v=0/1 is the shared edge segment; the middle segment is re-drawn per variant.
- **Distances in metres.** Edge distance `de = min(fu,1−fu)·T/nb` and joint distance `dj = min|wrapd(v−j)|·T`. Gap mask `gapm = smooth(.003,.007,de)·smooth(.002,.005,dj)`.
- **Grain.** `G = fbm(S,1.8,seed,fmin=4,ay=12)` and `G2 = fbm(S,1.5,seed+1,fmin=30,ay=18)`, each shifted per segment with `np.roll` as `gen_planks` does. Add faint cathedral arcs `0.03·sin(2π(1.3fu + 0.25G + φseg))`. Knots: 25 % of segments get one, radius 1.5–2.5 cm. Two treenails of 8 mm at each joint side, placed only at joints: no nail rows.
- **Height.** `h = gapm·(0.55 + 0.25·bow + 0.05G + 0.02G2) + (1−gapm)·0.08`, with `bow = 1 − 0.3(2fu−1)²`.
- **Colour.** `ramp3(clip(.58+.12G+.05G2), #3A2414, #74492A, #A07448, .5)` × segment tint `U(.88,1.08)`. 8 % of segments are old grey (lerp towards luma × (1.02, 1, .96) by 0.4). Gaps are `#2A1C12`.
- **Orientation.** For `orient="EW"`, `swapaxes` the layout, height and colour arrays before painting.
- **Roughness.** `R = .78 + .04G + .12(1−gapm)`.
- **Materials.** `M_VK_Floorboards` (`nstr 1.0, spec .2, rough_mul .95`), `_Dark` with tint (.70,.62,.58) for the tavern and chapel, `_Pale` with tint (1.10,1.05,.95).

### 4.2 T_VK_Flagstone — `gen_ashlar` v2 made general
`gen_ashlar(S=1024, seed=15, tile=1.5, depth=0.025, nrow=3, blocks=(2,3,2), pal=("S1","S2","S4"), mortar="#5E564C", chip=0.5, out_prefix="T_VK_Flagstone")`
- Rows of 0.5 m; flags 0.5–0.75 m wide. Keep row offsets at least 0.15 of a block width apart.
- Used for the chapel nave, tavern kitchen and cellar, and the townhouse hall.
- Material `M_VK_Flagstone` (`nstr .9, spec .25`); `_Warm` tint (1.04, 1, .93) for the chapel.

### 4.3 T_VK_FlagRustic — `gen_fieldstone` made general
`gen_fieldstone(S=2048, seed=33, T=1.5, depth=0.035, aspect=1.0, rows=(.38,.55), cols=(.45,.75), prot=(.010,.018), moss=0, lichen=0, joint="#4A3A2C", out_prefix="T_VK_FlagRustic")`
- Flatter, larger, irregular flags set in packed earth, with pebbles in the joints kept.
- Used for the smithy, hovel hearth area, cellars and workshops.

### 4.4 T_VK_EarthFloor and T_VK_EarthFloorSooty — new `gen_earthfloor(S=2048, seed=456, T=1.5, depth=0.03, rushes=1.0, soot=0.0, out_prefix=…)`
This is a copy of `gen_dirt_v2`. Keep the terrain dirt frozen rather than adding parameters to it.
- **Counts.** Scale by `a = (T/4)²`. Clods `int(800·a·1.3)`. Pebbles `int(620·a·.35)`, radius 0.8–1.8 cm, 3 % big. **No grass sprigs.**
- **Base.** Mostly packed earth: `loose = smooth(.3,1.5,…)`, colours `#6A4E35 → #7C5E41`.
- **Rushes.** `int(110·rushes)` tapered, slightly bent strands per tile, drawn with the blade code from `gen_grass_v2`. Length 0.12–0.32 m, width 4–7 mm (in metres/px). Direction follows a 12-cell voronoi clump field (angle ±0.5 rad). Colours are a lerp of `#8F8246 → #BFAE6A`, plus 20 % `#7F8A4A` and 15 % trodden `#7A5E3A`. Each strand gets a darker copy under it, offset by (2,1) px, so it reads as lying on the floor.
- **Strewing herbs.** 12 clusters of 3–6 dots, 3–5 mm, in `#E9E0B8` and `#C9B6D8`.
- **Sooty version** (`soot=1, rushes=.2`): charcoal specks from `_stamp_domes`, 4–12 mm, ×250 in `#25211F`; an ash haze lerping towards `#6E6862` by 0.25; iron scale flakes of 3–6 mm, ×120 in `#4D4A48`.
- **Roughness.** `.92 − .05·packed − .1·pebbles`.
- Used for hovels and cottages (with rushes) and the smithy and workshops (sooty).

### 4.5 T_VK_StrawBed — new `gen_strawbed(S=2048, seed=97, T=1.5, depth=0.03)`
- About 900 flat strands per tile, 8–22 cm long, 3–5 mm wide, in clumped directions.
- Colours `#B08A45 / #C9A456 / #D9BD6E` with paler tips and 18 % old grey `#9A8E6E`; gaps `#4A3A22`.
- `paint_form_light(hig=.15)`. Much lower contrast than `gen_straw`.
- Used for bedding, the hovel sleeping corner and stall pens. It also works as a floor variant.

### 4.6 T_VK_PlasterIn — `gen_plaster(seed=23, tile=1.5, depth=.015, patches=False, cracks=0, blot=.2, out_prefix="T_VK_PlasterIn")`
- Needs new `cracks`, `blot` and `out_prefix` parameters.
- Variants: White (1.08, 1.08, 1.10) as the default, Cream (1, 1, 1), Daub (.80, .65, .47) for hovels, Ochre (1.03, .84, .56) and Red (.78, .42, .33) for dado bands.

### 4.7 T_VK_StoneIn — `gen_stone` v2
Call it as `L = stone_layout(10, T=1.5, lacing=False, NC=4)`, then `gen_stone(S=2048, seed=10, T=1.5, depth=.05, L=L, moss=False, lichen=False, mortar="#857B6C", out_prefix="T_VK_StoneIn")`.
- Needs `range(7)` at L161/L165 replaced by `len(L['H'])`. With `moss=False` and `lichen=False`, steps 12 and 13 are skipped.
- Courses come out at about 0.375 m, close to the exterior's 0.43 m.
- Lacing must be off at T=1.5, because a lacing course gives fewer than 3 stones and those draws get rejected.
- Used for the smithy, the townhouse ground floor, tavern hearth walls and cellars.

### 4.8 T_VK_AshlarIn — `gen_ashlar(seed=14, tile=1.5, nrow=3, blocks=(3,2,3), out_prefix="T_VK_AshlarIn")`
Pale S2 blocks in 0.5 m courses, the same metric size as the exterior ashlar. Used for chapel walls.

### 4.9 T_VK_WattleIn — `gen_wattle(T=1.5, nst=6, nrod=28, out_prefix="T_VK_WattleIn")`
- **Both counts must be even.** The weave phase `cos(π(X/sp−.5)+π·row)` only wraps in X for an even `nst`, and in Y for an even `nrod`.
- Used for hovel partitions and byre screens.

### 4.10 T_VK_StoneBlockIn — `gen_stoneblock(seed=18, T=1.5, lichen=0, cracks=0, out_prefix="T_VK_StoneBlockIn")`
- Needs new `lichen` and `cracks` parameters.
- Used for hearth kerbs and slabs, the altar, window sills and steps. It is also what the tops of cut StoneIn and AshlarIn walls switch to.

### 4.11 T_VK_Brick — new `gen_brick(S=2048, seed=621, T=1.5, depth=.02, nr=20, nbk=6)`
- Take the running-bond layout from `gen_plaster` L90–94, with **`nr` even**. The existing code uses 21, which would leave a seam in Y.
- Bricks 0.25 × 0.075 m with 8 mm joints in `#9C9284`. Use `bpal` from `gen_plaster`, per-brick value `U(.88,1.08)`, and 10 % overfired `#5C3324`. Add chips and `paint_form_light(.18,.26)`.
- Used for the bread oven, forge hood and chimney breasts. Put soot in vertex colour, not in the texture.

### 4.12 T_VK_Ash — new `gen_ash(S=1024, seed=631, T=0.75, depth=.02)` (hearth prop)
- Base `lerp(#7E7872, #B3ADA4)`, soft domes of 1–4 cm, char lumps of 0.6–2 cm in `#2A2624` with `#4A4440` edges, and pale flakes in `#D8D2C6`.
- **No embers in the texture.** Embers would glow across the whole tile; make them GLOW geometry chips instead.

### 4.13 T_VK_Textiles atlas — new `src/textures/vk_textiles.py`, modelled on `vk_goods`
`gen_textiles_atlas(S=2048, seed=950, depth=.004, tile=1.0, out_prefix="T_VK_Textiles", cells=None)`
- 2048 px, 2 columns × 4 rows of **2:1 cells**. Each cell painter works at 2×, then `paint_form_light(post=0, hig=.08, log=.12)`, `down2`, `write_set`, and builds `M_VK_Textiles` with `nstr .5, spec .15`.
- Thread structure from `weave()` at 2.5–4 mm pitch, varying value by ±8 %.
- Helpers `textile_uv` and `textile_map(k, faces, cell, plane=(A,B))`, copied from `goods_uv` and `goods_map`, with padding.
- Cells:
  1. `rug_madder`: `#8E2B22` field, `#2C3E66` border, `#D9C9A0` guard stripes, a lozenge chain in `#B8862E` drawn from an |u|+|v| distance field, fringes at the short ends.
  2. `rug_indigo`: kilim-style stepped bands on `#2F4470`.
  3. `rug_check`: `#3E5A34` / `#B39448` checks.
  4. `runner`: red `#7A2020` with a gold `#C49A3A` border and quatrefoils, **periodic in u** so 3 m segments join along the chapel aisle.
  5. `hanging_heraldic`: two-colour vertical banner with a cross or chevron and a fringe.
  6. `tapestry_millefleur`: `#23402E` field with scattered flower dots and a `#6E2A22` border.
  7. `quilt_patch`: 6×3 patches in muted tints with dashed running stitches.
  8. `blanket_wool`: `#CFC2A6` with two `#6B4A32` stripes and fuzz.

### 4.14 Material-only variants (no new texture)

| Material | Built from | Settings | Use |
|---|---|---|---|
| `M_VK_Window_Day` | `lit_window_material` | `name="M_VK_Window_Day", warm=(.78,.86,1.0), strength≈1.0` | Glass seen from inside, cool daylight |
| `M_VK_Stained_In` | T_VK_Stained | `emission 1.8` | Chapel lancets |
| `M_VK_GlowIn` | flat | `(1.0,.62,.25)`, emission about 1.5–2.0; route `Col` to emission for a gradient | Hearths, forge, candles without clipping |
| `M_VK_Wax` | flat | `(.93,.88,.74)`, roughness .5 | Candles |
| `M_VK_WoodDark` | T_VK_Wood | tint `(.62,.55,.50)` | Pews, bar counter, inn beams |
| `M_VK_WaterMurky` | T_VK_Water | tint `(.55,.50,.40)` | Quench trough |
| `M_VK_Ale`, `M_VK_Foam` | flat | `(.45,.28,.08)` and `(.93,.88,.75)` | Tankard tops, which the camera sees |

Optional: painted false ashlar for the chapel, which is historically right and cheap. Take PlasterIn White and paint a red line grid of 0.5 × 0.75 m before `write_set`.

---

## 5. Wiring it into the kit

- **Separate interior builder.** Add `IKit(Kit)` whose `finish()` appends `kit_mats() + imats()`. The new slots take indices **55 and up**, so shared slots such as Goods, Iron and Glow keep their indices. Exterior pieces and `full_rebuild` stay untouched.
- **New slots and tile sizes:**

| Index | Slot | TILE | World-locked |
|---|---|---|---|
| 55 | FLOOR | 1.5 | yes |
| 56 | PLASTER_IN | 1.5 | yes |
| 57 | STONE_IN | 1.5 | yes |
| 58 | ASHLAR_IN | 1.5 | yes |
| 59 | WATTLE_IN | 1.5 | yes |
| 60 | STONE_BLOCK_IN | 1.5 | no |
| 61 | BRICK | 1.5 | yes |
| 62 | STRAW | 1.5 | yes |
| 63 | ASH | 0.75 | no |
| 64 | TEXTILE | own UVs | no |
| 65 | WAX | 1.0 | no |
| 66 | GLOW_IN | 1.0 | no |
| 67 | WINDOW_DAY | 1.0 | no |
| 68 | STAINED_IN | 1.0 | no |

  In `IKit.project`, faces of STONE_IN or ASHLAR_IN with |n.z| > 0.7 switch to STONE_BLOCK_IN, so the tops of cut walls read as coping.
- **Variants (`VARIANT_MATS`, `SLOT`, and the base dict in `variant_mat`):**
  - `"floor"`: Boards_NS (default), Boards_EW, Boards_B/C, BoardsDark, BoardsPale, Flag, FlagRustic, Earth, EarthSooty, Straw. With this, floor meshes don't depend on the material: one mesh per size, and the style picks the material.
  - `"plaster_in"`: White, Cream, Daub, Ochre, Red.
  - `"wood"`: Oak, Dark.
  - Add `floor→FLOOR`, `plaster_in→PLASTER_IN` and `wood→WOOD` to `SLOT`.
- **`MAT_MAP` entries** for every new prefix, so `apply_pbr_all()` rebuilds them all.
- **Code location.** Put the generators in a new text `vk_tex_interior` (`src/textures/vk_tex_interior.py`) plus `vk_textiles.py`. Exec them after vk_tex, vk_texgen, vk_tex2 and vk_mat. `gen_interior_textures()` runs one generator per MCP call; stone v2 and fieldstone are the slow ones. Sync with `tools/kit_sync.py push`.
- **Changes to existing generators:** new parameters must **default to today's random-draw order**, so exterior textures stay bit-identical (the same approach as the `_burn` rule in `vk_leafgen`).

| Function | Hard-coded today | New parameter |
|---|---|---|
| `vk_tex2.gen_stone` | `7` at L161 and L165 | `NC=len(L['H'])`, `moss`, `lichen`, `mortar` |
| `vk_tex2.gen_ashlar` | `nrow=6`, block counts, prefix, single palette | `nrow`, `blocks`, `out_prefix`, `pal`, `mortar`, `chip` |
| `vk_tex2.gen_fieldstone` and `fieldstone_seeds` | aspect 1.35 (twice), row/column ranges, protrusion, moss target 6–8 %, lichen count | `aspect`, `rows`, `cols`, `prot`, `moss`, `lichen`, `joint` |
| `vk_tex2.gen_wattle` | `nst=4`, `nrod=18` | `nst`, `nrod` (both even) |
| `vk_tex2.gen_stoneblock` | lichen count 1–2, `crack n=1` | `lichen`, `cracks` |
| `vk_texgen.gen_plaster` | `crack n=2`, fixed prefix | `cracks`, `blot`, `out_prefix` |
| `vk_texgen.gen_straw` | fixed prefix | `out_prefix` (or replace it with `gen_strawbed`) |

- **Existing mismatches to leave alone:** TILE[PLASTER] is 2.2 while the texture is 1.5 (exterior only; interiors use PLASTER_IN), and DRESS has no TILE entry.

---

## 6. Materials by building

| Building | Floors | Walls | Other |
|---|---|---|---|
| Hovel / cottage | EarthFloor (rushes), StrawBed corner | PlasterIn Daub, WattleIn partitions, WOOD posts | StoneBlockIn hearth + Ash + GlowIn, Burlap mattress, Textiles blanket/quilt, Clay pots, Goods |
| Townhouse | Floorboards (upstairs, parlour), Flagstone (kitchen, hall) | PlasterIn White/Cream + WOOD frame, Ochre/Red dado, StoneIn ground floor | Brick chimney breast, Textiles tapestry and rugs, PaintedWood chests, Loom (WOOD + Cloth) |
| Tavern / inn | Floorboards Dark (hall, guest rooms), Flagstone (kitchen, cellar, around the big hearth) | PlasterIn Cream, WoodDark beams, StoneIn hearth wall | Brick oven, casks (WOOD + IRON), Ale/Foam, rugs, Goods |
| Smithy / workshop | EarthFloorSooty or FlagRustic | StoneIn | Brick or StoneBlockIn forge, GlowIn, Coal, Ash, Iron/Steel, Hide bellows, WaterMurky trough, PLANKS tool wall |
| Chapel | Flagstone Warm + Textiles runner | AshlarIn (or PlasterIn + false ashlar), DRESS / StoneBlockIn dressings | Stained_In, Window_Day, Wax + GlowIn candles, Bronze gilt, WoodDark pews, Textiles altar frontal and hangings |

---

## 7. Lighting and export notes

- **Vertex colour.** `Col` multiplies every PBR base colour, so these need no textures: soot on hearth backs and forge hoods, grime at wall bases, and contact darkening along the floor lip of wall pieces. Unity can use baked or screen-space AO instead.
- **Palette.** Keep albedo moderate: floors at luma 0.25–0.45, limewash at 0.6–0.8. Warm hearth and candle light plus cool window light then set the mood. The saturated orange of the existing Planks and Straw would dominate a room.
- **Floor seams between materials.** Where two floor types meet (boards to flags), the join lies on the grid; a WOOD or StoneBlockIn threshold strip piece hides it.
- **Export, later:**
  - AO is already in `_BC`, so use `_AO` at low strength or not at all.
  - `_R` is roughness; URP needs smoothness (1−R) in the alpha of the metallic map.
  - Normals are OpenGL Y+, so no flip is needed.
  - The fallback in §3 would need per-renderer ST offsets.

## 8. Priority

- **P1** (every scope building needs these): Floorboards NS/EW + B/C, PlasterIn, EarthFloor, Flagstone, StoneBlockIn, Window_Day, GlowIn, Wax.
- **P2:** StoneIn, AshlarIn, FlagRustic, EarthFloorSooty, StrawBed, Textiles atlas, Stained_In, Brick, Ash, WoodDark.
- **P3:** WattleIn, painted false ashlar, and a second goods atlas (ale surface, grain in sack tops, onion strings, eggs) if the pantries need them.

## 9. Files read

- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_tex.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_texgen.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_tex2.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_goods.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_mat.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_helpers.py` (L6 TILE, L11/L2238 tex_mat, L47 kit_mats, L70 slot unpack, L144 VARIANT_MATS, L205 project, L225 box, L255 finish)
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\terrain\vk_terrain.py` (object-space terrain materials)
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\assets\textures\` — texture PNGs viewed: T_VK_Planks_BC, T_VK_Plaster_BC, T_VK_StoneBlock_BC, T_VK_Wood_BC, T_VK_Stone_BC, T_VK_FieldStone_BC, T_VK_Ashlar_BC, T_VK_Dirt_BC, T_VK_Straw_BC, T_VK_Wattle_BC
- Gallery renders: `docs\images\tavern.jpg` and `docs\images\blacksmith.jpg`