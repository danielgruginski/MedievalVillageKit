# Terrain Tile Kit spec: dual-grid marching squares (seam-first)

Target module: new `vk_terrain.py`, with the harness in `vk_terrain_verify.py`.
Style target: chunky WoW-style cliff terraces with a rolled grass turf lip, strata rock, painted shoreline and shader-splatted paths.

---

## 0. Decisions at a glance

| Item | Value | Why |
|---|---|---|
| Logical cell (game data, pathing, building grid) | 3.0 m = `CELL` | Buildings, walls and crop plots (`soil_bed` 2.9 m) already use it. |
| Render tile | 3.0 m, offset by +1.5 m (dual grid) | Tile corners sit on cell centres, so every transition crosses a tile edge at a cell border. |
| Corner data | per cell: `h` height level (0..7), `type` surface (Grass, Dirt, Cobble, Sand, Farmland, Water) | |
| Tier height `TIER` | 1.5 m = H1/2 | Clearly not walkable. Two tiers = one storey. Stairs fit in one cell. |
| Geometry sets | Height set (cliffs), Shore set (water) | Meshes are chosen by marching squares. |
| Surface types | marching squares evaluated **in the shader** from the same corner data | No mesh combinations, seamless by construction. |
| Multi-level | stacked layer pieces with a **3-state corner code** (below / at / above) | 22 canonical pieces cover every heightfield with no hidden overlapping caps. |
| Contour placement | the cliff lies in the **lower** cell. Reference line 0.75 m past the border, crossing each tile edge 2.25 m from the high corner | High cells stay 100 % flat and buildable up to their border. |
| Saddles | Height: high region connects. Water: water connects. Paths: path connects (shader bump). | |
| Seam zone | 0.25 m band along every tile border is a pure extrusion of a canonical edge profile | |
| Rotation | baked in Blender (exact coordinate permutation). Runtime rotation is always 0. | UVs stay world-aligned, painted light stays consistent, seam ownership is well defined. |
| Cliff texture period | 1.5 m in u and v (v = world z / 1.5, one tier per repeat) | Contour lengths are about multiples of 1.5 m. Strata line up at tier boundaries. |

---

## 1. Grid and coordinate conventions

```
 logical cells (data)                 render tiles (meshes), dual grid
 +-------+-------+                         o-------o-------o      o = cell centre = tile corner
 | (0,1) | (1,1) |                         |  tile |  tile |
 |   o---+---o   |    tile (i,j) spans     | (0,0) | (1,0) |
 +---|---+---|---+    [3i+1.5, 3i+4.5] x   o-------o-------o
 |   o---+---o   |    [3j+1.5, 3j+4.5]
 | (0,0) | (1,0) |
 +-------+-------+    the midlines of each tile are cell borders, where walls stand
```

- Cell `(i,j)` covers world `[3i, 3i+3] × [3j, 3j+3]` (Blender XY, Z up). Building footprints are unions of cells, and wall modules sit on cell borders exactly as `build_house_v` places them today.
- Tile `(i,j)` has corners SW = cell(i,j), SE = cell(i+1,j), NE = cell(i+1,j+1), NW = cell(i,j+1). Its local origin is its SW corner, placed at world `(3i+1.5, 3j+1.5, l·TIER)`. Local x and y run 0..3.
- **Corner order and indices:** 0 = SW, 1 = SE, 2 = NE, 3 = NW (counter-clockwise). Bit or digit `k` belongs to corner `k`.
- **Rotation `r` (CCW, r·90° about the tile centre):** `R1:(x,y)→(3−y, x)`, `R2:(3−x, 3−y)`, `R3:(y, 3−x)`. Corner `k` moves to `k+r mod 4`, and a 4-bit mask rotates as `rotl4(m,r) = ((m<<r)|(m>>(4−r)))&15`. Always rotate by swapping coordinates. Never use `Matrix.Rotation` here: cos 90° = 6e-17 breaks exact borders.
- **Map padding:** emit tiles for `i ∈ [−1, N−1]` using clamped cell data so the playable area `[0, 3N]` is fully covered.
- **Unity axis check (do this first):** export `SM_VKT_Debug_Compass`, a 3×3 m tile with a +X red arrow, a +Y green arrow and an "SW" label. Confirm Blender +X becomes Unity +X and Blender +Y becomes Unity +Z. If the FBX importer mirrors X, the Unity lookup must swap SW↔SE and NW↔NE. Decide this before any lookup code is written.

---

## 2. Corner data (per logical cell)

| Field | Range | Meaning |
|---|---|---|
| `h` | 0..7 | Ground height = `h·1.5 m` |
| `type` | Grass(0), Dirt(1), Cobble(2), Sand(3), Farmland(4), Water(5) | Water changes geometry (Shore set). The others are shader-only. |
| `built` (Phase 6) | bool | Chooses a retaining-wall style instead of natural rock. |

**Editor and simulation constraints**

1. **Water:** every cell in the 8-neighbourhood of a Water cell has the same `h`. A shore never touches a cliff inside a tile.
2. **Phase A only:** at most two distinct `h` values among the 4 corners of any tile (any Δ). This is lifted in Phase B once the mixed pieces exist. The editor auto-fixes by raising the lowest offending cell.
3. **Cliff-foot cells:** a cell with any higher 8-neighbour loses a strip of up to 1.05 m to cliff and toe on that side. It stays walkable but can't hold a building footprint. Cliff-top cells are fully buildable.

---

## 3. Layer decomposition and lookup

### 3.1 The 3-state code

For tile corners `h[0..3]` with `m = min(h)` and `M = max(h)`, emit one piece for each layer `l = m..M`, placed at `z = l·TIER`, with rotation 0:

```
digit_k(l) = '0' if h[k] < l      # below: air at this layer's cap height
             '1' if h[k] == l     # at: this layer owns the cap here
             '2' if h[k] > l      # above: higher ground, the hill interior at this layer
code = digit_0 digit_1 digit_2 digit_3   (SW SE NE NW)
skip "0000" and "2222" (empty)
```

Piece local frame: **the cap is at local z = 0**. The band (cliff face) rising to this level occupies local z ∈ [−1.5, 0], and the toe fillet around a higher hole rises to +0.35.

- Flat tile: 1 piece ("1111").
- Single-tier cliff tile: 2 pieces. Layer m is a cap with a hole plus toe; layer m+1 is band plus lip plus cap.
- Sheer Δ = k tile: k+1 pieces (Hole, k−1 × Pass, BandCap).

### 3.2 Canonical pieces (22 non-empty; there are 24 rotation orbits of 3^4 codes, 2 of them empty)

| Family | Digits used | Canonical codes | What it contains |
|---|---|---|---|
| **Full** | {1} | `1111` | Flat cap |
| **BandCap** | {0,1} | Corner `1000`, Edge `1100`, Saddle `1010`, Inner `1110` | Band from −1.5 to 0, turf lip, cap over the '1' region |
| **Hole** | {1,2} | Corner `2111`, Edge `2211`, Saddle `2121`, Inner `2221` | Cap over the '1' region, with a hole under higher ground and a toe fillet around it |
| **Pass** | {0,2} | Corner `2000`, Edge `2200`, Saddle `2020`, Inner `2220` | Sheer band only (a mid-stack tier), no cap |
| **Mixed** (Phase B) | {0,1,2} | `0012 0021 0102 1102 1120 1012 2201 2210 2021` | Band, lip, cap and toe, with a junction where the two contours merge |

Phase A needs 13 of these (Full + BandCap + Hole + Pass). A code never contains all three digits while constraint 2 holds.

### 3.3 Binary lookup (the Full, Corner, Edge, Saddle, Inner, Empty table)

Every binary family uses one 16-entry table keyed by the mask of its "marked" digit:

- BandCap: mask of '1' digits
- Hole: mask of '2' digits
- Pass: mask of '2' digits
- Shore: mask of land corners

Canonical masks: Corner = 1 (SW), Edge = 3 (SW+SE), Saddle = 5 (SW+NE), Inner = 7 (all except NW).

| mask | corners | shape | r | | mask | corners | shape | r |
|---|---|---|---|---|---|---|---|---|
| 0 | none | Empty | 0 | | 8 | NW | Corner | 3 |
| 1 | SW | Corner | 0 | | 9 | SW NW | Edge | 3 |
| 2 | SE | Corner | 1 | | 10 | SE NW | Saddle | 1 |
| 3 | SW SE | Edge | 0 | | 11 | SW SE NW | Inner | 3 |
| 4 | NE | Corner | 2 | | 12 | NE NW | Edge | 2 |
| 5 | SW NE | Saddle | 0 | | 13 | SW NE NW | Inner | 2 |
| 6 | SE NE | Edge | 1 | | 14 | SE NE NW | Inner | 1 |
| 7 | SW SE NE | Inner | 0 | | 15 | all | Full | 0 |

Unique-rotation mesh counts per shape: Corner 4, Edge 4, Saddle 2, Inner 4, Full 1, which gives the 16 masks. For 3-state codes, generate the table: find canonical `C` and `r` with `code[(k+r)%4] == C[k]` for all k, and take the smallest `r` for symmetric codes.

### 3.4 Naming and runtime selection

- Height pieces: `SM_VKT_H_<code>_v<k>`, e.g. `SM_VKT_H_0110_v2` (already rotated).
- Shore pieces: `SM_VKT_W_<mask:02d>_v<k>`.
- Custom props on each object: `kit="VillageTerrain"`, `tk_canon`, `tk_rot`, `tk_variant`.
- Variant choice must be reproducible in C#:

  ```
  h = (i*0x8DA6B343) ^ (j*0xD8163841) ^ (l*0xCB1AB31F)  (uint32)
  h ^= h>>13;  h *= 0x5BD1E995;  h ^= h>>15
  variant = h % NVAR[code]
  ```

- Generation seeds come from `zlib.crc32(f"{family}|{canon}|v{k}")`. **Never seed with Python `hash()` on strings**, because it changes per process.

---

## 4. Plan-view contours (exact)

Define `b` as the distance from the logical border (the tile midline), positive toward the lower corner. The cliff **reference contour** C is at `b = 0.75`, so it crosses each tile edge at **2.25 m from the high corner** (0.75 m from the low corner). All contours are Manhattan offsets of the cell borders, with fixed roundings. The shapes below are for the canonical masks; rotate them for the others.

| Shape | High region | Contour C (reference, b = 0.75) | Length L | Δu (period 1.5) | Interior u stretch |
|---|---|---|---|---|---|
| Edge (SW+SE) | y ≤ 2.25 | straight line y = 2.25 | 3.000 | 3.0 | 1.000 |
| Corner (SW) | quadrant grown 0.75 | x = 2.25 for y ∈ [0, 1.5], arc about (1.5, 1.5) with **radius = b** (0.75), y = 2.25 for x ∈ [0, 1.5] | 4.178 | 4.5 | 1.088 |
| Inner (NW low) | everything except a pocket | x = 0.75 for y ∈ [2.75, 3], concave arc about (0.25, 2.75) with **radius = 1.25 − b** (0.5), y = 2.25 for x ∈ [0, 0.25] | 1.285 | 1.5 | 1.274 |
| Saddle (SW+NE) | connected ("high wins") | two Inner pockets, at SE and NW | 2 × 1.285 | 2 × 1.5 | 1.274 |

- **Sweeps map profile b onto the contour.** On a Corner arc the radius equals b. On an Inner arc the radius equals 1.25 − b. The smallest radius used (toe end b = 1.13 with wiggle) is 0.12 m, so nothing degenerates.
- **Contour sampling.** Start at the crossing where the traversal enters the tile. Traverse in direction `t = Z × n`, where n is the horizontal normal toward the low side. Sample:
  - s = 0 and 0.25 (the seam row),
  - then about 0.42–0.5 m steps on straight parts,
  - 4 segments per 90° arc,
  - 0.25 m as the last segment.
  
  Two contours that share a straight piece then share their vertex rows exactly, which Mixed pieces rely on.
- **Nesting:** region(mask_{l+1}) ⊆ region(mask_l) always holds, with equality along shared straight lines. Where they are equal the stack is sheer. The harness checks this (§15, T6).
- **Where features sit.** The feature band spans b ∈ [0.32, 1.12] (including wiggle). On an edge parallel to the contour it stays at least 0.38 m from the far border, which is outside the 0.25 m seam zone.

---

## 5. Canonical cross-section profiles

Coordinates are `(b, z_local)` in metres. Material codes: G = GROUND, C = CLIFF, R = GROUND with rubble mask (vertex alpha = 1). **S** marks a sharp point (split normals).

**PB: band, lip and cap** (edge states (1,0)). The cap is flat for b < 0.40.

| pt | b | z | mat | note |
|---|---|---|---|---|
| P1 | 0.40 | 0.000 | G | lip start (plinth rocks reach 0.44, which is fine) |
| P2 | 0.62 | +0.030 | G | turf crest |
| P3 | 0.80 | +0.010 | G | |
| P4 | 0.87 | −0.050 | G | turf front |
| P5 | 0.84 | −0.110 | G/C **S** | turf underside, material split |
| P6 | 0.76 | −0.160 | C | shadow notch (v ≈ 0.89) |
| P7 | 0.82 | −0.320 | C | |
| P8 | 0.86 | −0.620 | C | upper course |
| P9 | 0.80 | −0.780 | C | strata notch (v = 0.48) |
| P10 | 0.84 | −0.900 | C | |
| P11 | 0.85 | −1.250 | C | lower course |
| P12 | 0.79 | −1.420 | C | |
| P13 | 0.75 | −1.500 | C **S** | junction (world z = (l−1)·1.5) |

**PS: sheer pass band** (edge states (2,0)):
`S1 (0.75, 0.000) S`, `S2 (0.80, −0.10)`, `S3 (0.83, −0.32)`, then P8..P13. PS's top S1 meets the P13 of the piece above exactly, forming a crease on the strata line.

**PT: toe on the cap** (edge states (2,1); b is measured toward the '1' corner):
`T0 (0.55, +0.35) R` (hidden inside the band above), `T1 (0.86, +0.15) R`, `T2 (0.96, +0.05) R`, `T3 (1.05, 0.000) G`. The cap resumes after T3.

**SH: shore bank** (land '1' to water '0'; reference b = 0 at the border, rounding radius 0.6):
`(−0.50, 0) G`, `(−0.25, −0.03) G→Bank`, `(−0.05, −0.14)`, `(0.15, −0.30)`, `(0.45, −0.62)`, `(0.85, −0.86)`, `(1.20, −0.90)` bed. The water plane is at −0.22.

**Border polyline table `EDGE_POLY[(sa,sb)]`.** This is used by the generator and checked by the harness. It is expressed in a world-aligned edge frame: t runs +y along vertical edges from the south corner and +x along horizontal edges from the west corner. A profile point maps to `t = 1.5 ± b`, measured from the higher corner.

| (sa, sb) | Border content |
|---|---|
| (1,1) | flat cap at z = 0, samples at t = 0, 0.75, 1.5, 2.25, 3.0 |
| (1,0), (0,1) | cap samples at t = 0, 0.75, 1.5, then P1..P13 at t = 1.90..2.37 (mirrored for (0,1)) |
| (2,1), (1,2) | T0..T3 at t = 2.05..2.55, then cap samples at 2.75 and 3.0 |
| (2,0), (0,2) | PS points only |
| (0,0), (2,2) | nothing |

Each table point stores `(t, z, material, sharp, normal_2d[, normal_2d_b], AO, alpha)`.

---

## 6. Seam rules

- **R1.** Every piece's skin on a tile border depends only on the two corner

states relative to that piece's layer. It is exactly `EDGE_POLY[(sa,sb)]`, and nothing else touches the border.
- **R2.** Within **0.25 m** of every border, the skin is a pure extrusion of that polyline along the border normal. The first contour row, at s = 0.25, lies exactly on the extruded profile.
- **R3.** After rotation, border skin vertices are **snapped to the table values** and quantized to 1/1024 m. Tag the skin with a bmesh int layer `skin=1` so deco is not snapped. World origins are multiples of 1.5, so placed coordinates stay exact in float32 up to 16 km, and neighbouring tiles match bit for bit.
- **R4.** Border normals come from the table's 2D profile normals, with zero component along the contour. They are set as custom split normals and split at sharp points.
- **R5.** Border vertex colours (AO and alpha masks) come from the table.
- **R6.** UV rules are in §9: cliff u ≡ 0 (mod 1.5) at every border crossing with du/ds = 1 in the seam row, v = z_world / 1.5, and UV1 = (x/3, y/3).
- **R7.** All interior displacement is multiplied by `W(d) = smoothstep(0.25, 0.75, d)`, where d is the distance to the nearest border for caps and the arclength from the crossing for bands. W and W′ are both 0 at d = 0.25, so normals stay C1-continuous.
- **R8.** Band displacement is 0 on junction rows (z_local = −1.5, and the PS top at 0). This keeps stacked bands of any variant crack-free.
- **R9.** Deco (rock chunks, tufts, rubble) may cross a border only on the tile's **East or North** border, only in the band zone, and at most 0.25 m into the neighbour. There the neighbour's geometry is canonical, so the embedding is identical.
- **R10.** Flat-cap borders are exactly z = 0 (no shared periodic field). This makes LOD fans and T-junctions crack-free.
- **R11.** Material index and sharp flag for each profile point are identical on both sides of a border.
- **R12.** Do **not** use `Kit.finish`: its x-wobble `0.02·sin(2πz/2.3)` moves border vertices, and its z-grime is layer-inconsistent. Do not use `Kit.project` either: its per-face `U = n×Z` breaks UVs on curved contours. Write `tk_finish` in the style of `nk_finish`, with material remapping to used slots only and `normals_split_custom_set` per loop.

---

## 7. Adding hand-made irregularity without breaking seams

| Layer | Field | Amplitude | Window |
|---|---|---|---|
| Cap bumps | zero-mean value noise, λ ≈ 1.5 m | ±0.05 m (variant v0 = 0, perfectly flat) | W(d) × smoothstep(0, 0.4, distance to P1 or T3) |
| Lip plan wiggle | 1D noise in s applied to P1–P5, T1–T3 and the cap boundary | δb ∈ [−0.08, +0.07] | W(s) |
| Turf crest | z noise on P2–P4, plus overhang depth | ±0.03 m | W(s) |
| Band face | displacement along the horizontal normal: `0.6·n(s/1.2, z/0.35) + 0.4·n(s/0.45, z/0.3)` plus ±0.05 ledge steps at z = −1.05 and −0.55 | 0.10 m | W(s) × V(z), with V = smoothstep(−1.5, −1.2, z) × (PS only: 1 − smoothstep(−0.3, 0, z)) |
| Rock chunks | `vk_nature.boulder(mi=CLIFF, sub=1, cuts=5)`, 0.5–0.9 × 0.35–0.6 × 0.3–0.45 m, 45 % embedded, on ledges at z ∈ [−1.3, −0.3] | about 1 per 1.3 m of interior contour, plus up to 2 E/N seam chunks (width ≤ 0.5, centred on the crossing) | interior, plus R9 |
| Lip tufts | foliage "grass" cards (`card()`, crossed pair) on the crest at s = 0.15 + 0.3k ± 0.1 | 8–12 per 3 m | stay inside the tile's own s range |
| Toe rubble | 0–3 `boulder(sub=1)`, 0.2–0.4 m | Hole pieces only | interior |
| Vertex AO | band `0.70 + 0.30·smoothstep(−1.5, −0.2, z)`, notch P6 = 0.55, toe 0.75→1.0, cap 1.0, times (1 + 0.08·W·noise) | | table on borders |

**Seam-straddling chunks.** A tile owns seam chunks only on its E and N borders. Without them, a straight cliff would show a clean 0.5 m canonical strip every 3 m.

**Variant counts**

| Piece | Variants |
|---|---|
| Full | 4 (v0 flat) |
| BandCap | Edge 4, Corner 3, Inner 3, Saddle 2 |
| Hole | 2 each |
| Pass | Edge 3, others 2 |
| Mixed | 1 |
| Shore | Edge 3, Corner 2, Inner 2, Saddle 1, FullWater 2 |

This comes to about 180 baked meshes in total.

**Optional (Unity only):** a world-space vertex jitter of ≤ 0.04 m in the vertex shader, with the normal perturbed analytically from the noise gradient. It is identical on both sides of a border by construction and breaks the 3 m periodicity. Props raycast against the undisplaced mesh, so they may be off by up to 4 cm.

Use the project's own integer-hash value noise (spec'd, portable to C#), not `mathutils.noise`.

---

## 8. Normals

- **Caps:** smooth shading. Custom normals are analytic from the D gradient. At borders the normal is (0, 0, 1).
- **Bands:** smooth shading with sharp edges where the face angle exceeds 40°, so chunky facets survive. Seam rows are coplanar extrusions, so geometric normals already match. Custom normals from the table are still written as a guarantee.
- **Hard splits:** P5 (turf to rock), P13/S1 (the stacked crease), and deco.
- **Unity tangents:** use MikkTSpace. In the seam row, faces on both sides are identical extrusions with identical UV derivatives, so tangents match. Ground uses world-space normal mapping (§9), so ground tangents don't matter.

---

## 9. UVs and texture continuity

| Channel | Material | Formula | Continuity argument |
|---|---|---|---|
| UV0 | GROUND (baked fallback) | `((x_l+1.5)/3, (y_l+1.5)/3)` | Tile origins are multiples of 3 → integer offsets |
| — | GROUND (production shader, Unity and Blender) | world XY / 4.7 m, plus a second sample at 13.1 m rotated 37°, blended by macro noise | World space: rotation- and seam-free, and the period doesn't lock to the tile grid |
| UV0 | CLIFF (band) | `u = ∫k(s)ds` from the start crossing, with k = 1 in the 0.25 m seam rows and constant in the interior so that the total is Δu (§4). `v = (l·1.5 + z_ref)/1.5`. Computed from **reference (undisplaced)** positions, in metres/1.5. | Every crossing has u ≡ 0 (mod 1.5), because crossings lie at local x or y ∈ {0, 3}. Direction t = Z×n is intrinsic, so this also holds under runtime rotation. v is world z, so tiers line up. |
| UV0 | CLIFF (chunks) | `box_uv` at 1.5 m with a random offset | deco |
| UV0 | BANK | planar world XY / 1.5 | integer offsets |
| UV1 | GROUND | `(x_l/3, y_l/3)` | splat bilerp coordinates |
| UV2 | (runtime) | 4 corner types, written by the Unity chunk combiner | per tile |

**Hiding UV breaks at tier creases.** Stacked bands with different masks have different interior u. That discontinuity always falls on a tier crease, and `T_VK_Cliff` paints its strongest crack at v ≡ 0, so the break is masked.

**Alternative: runtime rotation.** Ship 22 canonical meshes and rotate them at runtime. This works with the world-space ground shader, and the cliff UVs are intrinsic so they survive rotation. It requires dropping seam chunks (R9), because E/N ownership is lost. Baked rotation stays the default.

---

## 10. Surface types: marching squares in the shader

For each type t, with corner flags `f_k = (type_k == t)` and `(u, v) = UV1`:

```
B  = f0(1-u)(1-v) + f1·u(1-v) + f2·u·v + f3(1-u)v            # uses only the 2 corners on a border
C  = 0.25·16·u(1-u)v(1-v) · (f0f2(1-f1)(1-f3) + f1f3(1-f0)(1-f2))   # diagonal-connect bump, 0 on borders
n  = 2·SplatNoise(worldXY / 12 m) − 1                         # world space
m  = B + C + 0.18·n − τ_t + 0.5
w  = smoothstep(0.44, 0.56, m + 0.25·(H_t − H_below))          # height-blend sharpening using _H maps
edge ring (Dirt only): color *= 1 − 0.18·(1 − |2·m − 1|)
```

- **Thresholds:** τ_Cobble 0.50 (full 3 m road), τ_Dirt 0.58 (≈ 2.5 m path), τ_Sand 0.45, τ_Farm 0.50.
- **Layering order:** Grass base → Farmland → Dirt → Sand → Cobble.
- **Rubble:** toe vertices with alpha = 1 blend toward Dirt.
- **Blender preview:** each tile object gets a custom prop `vk_ct` (RGBA = type/8), read with an Attribute node of type OBJECT. Mapping uses Geometry › Position (world space for instances).
- **Unity:** the chunk combiner writes UV2 = corner types.
- **Fallback without a custom shader:** per-type 16-mask overlay decal meshes, on flat caps only. Not recommended.

---

## 11. Water and shore set

- **When it is used:** any tile containing a Water corner uses `SM_VKT_W_<landmask>` at z = h·1.5, **plus** a full 3×3 quad water plane at −0.22. The plane is hidden under land, the bank crosses it exactly at the waterline, and adjacent planes tile trivially.
- **How banks are built:** as a **heightfield**, `z = SH(b(x,y))`. Here b is a per-case analytic rounded-box distance to the shore contour at the border. In seam zones it reduces to the 1D edge distance, which is seam-safe and has no sweep degeneracy in small pockets. Grid is 0.25 m in the feature band and 0.75 m elsewhere. The bed is flat at −0.90 with windowed noise.
- **Saddles:** water connects, leaving a 0.5 m channel between the two land corners.
- **Unity water shader:** depth-fade colour and foam from the scene depth texture, and world-space scrolling normals from `gen_water`.
- **Out of scope for v1:** waterfalls and water under cliffs (v2).

---

## 12. Buildings, props and pathing

- A building footprint must be flat (same h), made of whole cells, and contain no cliff-foot cells. Building origin z = h·1.5.
- Tiles with any corner inside a footprint are forced to **variant v0** (flat cap), so plinths, doors and interior voids sit on exact z. Footprint cells plus a 1-cell apron get type Dirt ("trampled"), unless they are Cobble.
- Cliff-top buildings may stand right on the border. The lip starts at b = 0.40, and plinth rocks reach about 0.44.
- `SM_VK_LowWall` on a high-cell border reads as a parapet along the cliff lip.
- **Props and trees:** allowed where the zone is Cap and at least 0.3 m from P1/T3. Z comes from a raycast, or from the analytic query below.
- **`TerrainQuery.SurfaceAt(x, y)` in C#:** locate the tile, get the code, find the canonical shape and rotation, and evaluate the rounded-box b per contour. It returns `(z, zone ∈ {Cap, Lip, Face, Toe, Bank, Water})`. Interior noise is ignored (≤ 5 cm).
- **Pathing:** use the cell data. Cells are walkable except Water. Crossing between levels is allowed only via connectors.

---

## 13. Connectors and dressing (props, not tiles)

**Connectors**

| Piece | Specification | Rule |
|---|---|---|
| `SM_VKT_Stair_1T` | 1.5 m rise, 7 steps × 0.214 m rise × 0.30 m run, 2.2 m wide, rock cheek walls. Runs from b = 0.30 on the high side to b = 2.6 in the low cell. | Placed on a cell border. Both tiles straddling it must be Edge cases at that level. |
| `SM_VKT_Ramp_1T` | Earth ramp, same footprint | Same rule |

Both skirt 0.15 m into the cap, and the low cell becomes a connector cell.

**Dressing:** reuse `Deco_Ivy_A` and `Deco_Ivy_B` on faces, `Rock_Small` and `Pebbles`, and `Mushrooms` at the toe. Also add hanging-roots cards.

---

## 14. Materials and textures

Material index constants are appended after `MUSH_GLOW` so existing indices stay valid: **GROUND = 45, CLIFF = 46, BANK = 47**. The water plane reuses `WATER` (18).

| Texture | Generator (uses `vk_tex`) | Tile | Key recipe |
|---|---|---|---|
| `T_VK_Grass` | `gen_grass(1024, 301)` | 3.0 m | `ramp3` greens (0.26,0.42,0.12)→(0.36,0.55,0.16)→(0.50,0.64,0.22) over low-frequency `fbm` · voronoi clump cushions (120 points), darker clump rims · about 4000 `draw_segments` blade strokes (5–12 px, ±35° about +v, lighter tips) · `painted_light` |
| `T_VK_Dirt` | `gen_dirt(1024, 311)` | 3.0 | warm brown ramp, voronoi pebbles (300 points, 30 % visible), soft cracks, sparse sprigs |
| `T_VK_Cobble` | `gen_cobble(1024, 321)` | 1.5 | about 60 jittered voronoi cells, dome = √clip((F2−F1)/0.05), mossy dirt gaps. Palette taken from the reworked `T_VK_Stone`. |
| `T_VK_Cliff` | `gen_cliff(1024, 331, depth=0.10)` | 1.5 | Strata boundaries at v = 0 (strongest), 0.48 and 0.89, matching profile notches P9 and P6, plus one minor boundary. Boundaries warped by `fbm(ax=8)` at ±0.015. Brick-bonded vertical joints from `crack_segments(dirbias=π/2)`, 2–4 per stratum. Blocks get dome, tilt and `facets(2,30,0.25)`. Palette alternates warm (0.62,0.54,0.43) and cool (0.50,0.50,0.52) per stratum. Top-edge rim light, moss where n_y > 0.5, cavity AO floor 0.2. |
| `T_VK_Bank` | `gen_bank(512, 341)` | 1.5 | wet mud (0.20,0.16,0.11) → sand (0.62,0.55,0.40), pebbles. The shader darkens by vertex alpha (wetness). |
| `T_VK_SplatNoise` | `gen_splatnoise(512, 351)` | 12 m | R = boundary noise, G = macro tint, B = tuft mask |

**Materials**

- `M_VKT_Ground`: new `ground_splat_material()`, world mapping, UV1 bilerp.
- `M_VKT_Cliff`: `mossy_material("M_VKT_Cliff", "T_VK_Cliff", base_tile=1.5, thresh=0.62, soft=0.12)`. Moss follows the world normal, so it is seam-safe.
- `M_VKT_Bank`: `pbr_material`.
- Chunks use CLIFF with box UV, which saves a draw call.
- Tufts use `M_VK_Foliage`.

**Debug materials:** `M_VKT_DebugUV` (1.5 m checker with u/v arrows), `M_VKT_DebugN` (world normal as RGB) and `M_VKT_Void` (bright red).

---

## 15. Polycount budget (tris, LOD0; LOD1 is about 40 %)

| Piece | Budget | | Piece | Budget |
|---|---|---|---|---|
| Full | 32 (4×4 grid; LOD1 = 16-tri fan, same border) | | Pass Edge / Corner / Inner / Saddle | 350 / 500 / 250 / 400 |
| BandCap Edge | 600 | | Mixed (each) | ≤ 900 |
| BandCap Corner | 800 | | Shore Edge / Corner / Inner / Saddle | 200 / 200 / 150 / 250 |
| BandCap Inner / Saddle | 350 / 600 | | FullWater | 34 |
| Hole Edge / Corner / Inner / Saddle | 250 / 300 / 150 / 250 | | Stair / Ramp | 600 / 200 |

Where the band budget goes: sweep 7–12 segments × 12 profile segments × 2 tris, chunks about 80 tris each, tufts 4 tris each.

**LOD rule:** LODs never change border skin vertices. They drop deco and decimate interior rows only.

**Map target:** for 96×96 cells, about 1.8 M tris at LOD0. Unity merges tiles into 8×8-tile chunks (≤ 60k verts, 16-bit indices, 4–5 materials per chunk), with chunk-level LOD beyond 50 m. Target ≤ 1 M visible terrain tris at the default camera.

---

## 16. Build order and acceptance criteria

| Phase | Deliverables | Accept when |
|---|---|---|
| 0 | Textures and materials above. Constants 45–47. `SM_VKT_Debug_Compass`. | Material balls render. Unity axis confirmed. |
| 1 | Full + BandCap ×4 + Hole ×4, all variants and rotations. `build_terrain_preview(coll, H, T, origin)`. | Harness T1–T5 and T7 pass on 200 random 12×12 maps (h 0..3, Δ = 1). Terraced-island render. |
| 2 | Pass ×4 | T1–T7 pass with Δ up to 3, 2 distinct heights per tile |
| 3 | Shore set, FullWater, water plane. Water constraint in the map generator. | Same tests pass with water blobs |
| 4 | Splat shader types. Port the plaza (Cobble) and roads (Dirt) from `build_town` onto a grid-snapped layout, replacing `road_strip` and the ground plane. | Visual review; no seams in the splat debug view |
| 5 | Mixed ×9 (SDF-driven profile morph by gap to the next contour, windowed by R7). Lift constraint 2. | T1–T7 pass on unconstrained random maps |
| 6 | Connectors, dressing, `built` style bit (retaining wall profile PR with the same crossing, BandCap per-crossing style combos RR/RB/BR/BB), map-edge skirt | |

**Generator sketch**

```
for canon in CANON[phase]:
  for v in range(NVAR[canon]):
    bm = TKit()                                        # Kit subclass: bm, uv, UVTile, Col, skin/deco layers
    Rl, Rl1 = regions(canon)                           # analytic contours (§4)
    if '0' in canon: sweep(bm, Rl.contour, PB or PS, seed, v)  # PB if '1' in canon, else PS (Pass)
    if '1' in canon: cap(bm, Rl - Rl1, seed, flat=(v == 0))    # delaunay_2d_cdt: fixed border samples + 0.75 m Steiner points
    if '1' in canon and '2' in canon: sweep(bm, Rl1.contour, PT, seed, v)
    add_interior_deco(bm, seed)
    quantize_skin(bm, 1/1024)
    for r in unique_rotations(canon):
        b2 = copy(bm); rotate_exact(b2, r); code = rot(canon, r)
        add_seam_chunks_EN(b2, code, seed); snap_border_skin(b2, code)
        uvs(b2, code); vcols(b2); custom_normals(b2)
        tk_finish(b2, f"SM_VKT_H_{code}_v{v}")
```

---

## 17. Verification harness (`vk_terrain_verify.py`, runs in Blender on the baked library)

| Test | Method | Tolerance |
|---|---|---|
| **T1 Edge signature (exhaustive)** | For every mesh and each of its 4 sides, gather skin loops with \|coord − border\| < 1e-6. Project them to (t, z) in the world edge frame, sort, and compare to `EDGE_POLY[(sa,sb)]`: positions, material index, sharp flag, normals, AO. | positions exact (==); normals ≤ 0.1°; colour ≤ 1/255 |
| **T2 Seam-zone extrusion** | Every skin vertex within 0.25 m of a border lies on the extruded table polyline | distance ≤ 1e-5 |
| **T3 Assembly weld** | Build a random map: instance the pieces, join a copy, merge by distance 1e-5, deco excluded. Count edges lying on internal tile-border lines that have exactly 1 face. | 0 |
| **T4 Normal and UV continuity** | At each welded border vertex, compare loops from the two source tiles (face attribute `src_tile`). Check normals, plus for CLIFF: v equal and `frac(u_A − u_B)` = 0. | ≤ 0.5° (except table-sharp points); ≤ 1e-4 |
| **T5 Hole rays** | Put a `M_VKT_Void` plane at z = −10 under the map. Cast downward rays on a 0.05 m grid (`BVHTree.FromObject`), then oblique rays at azimuth 45/135/225/315° and elevation 35° and 60°. Fail on a miss, a void hit, or a back-face hit (dot(ray, normal) > 0). | 0 failures |
| **T6 Nesting** | For every Mixed, Hole and Pass code: sample 10k points and assert region(l+1) ⊆ region(l), and that PB P13 or PT T0 are covered | 0 |
| **T7 Determinism** | Generate twice and compare SHA1 of each mesh's positions, UVs, normals and colours | identical |
| **T8 Unity round-trip** (EditMode test) | Rerun T1 on the imported meshes | same as T1 |

**Report:** JSON with per-code failures, plus a top-down orthographic render using `M_VKT_DebugN` and `M_VKT_DebugUV`, with the faces around failing vertices tinted red.

---

## 18. Unity integration

**Import settings**

- Mesh Compression **Off** (compression quantizes positions and breaks R3).
- Normals: **Import**. Tangents: **MikkTSpace**.
- Read/Write enabled (for combining). Scale 1. FBX exported with "Apply Transform".

**Runtime assembly**

```
foreach tile(i,j): h = corners; if any water -> W piece + water plane
  else for l in min(h)..max(h): code = digits(h, l); skip 0000/2222
       mesh = LIB[code][hash(i,j,l) % n]; add at (3i+1.5, l*1.5, 3j+1.5)
chunk 8x8 tiles -> CombineMeshes per material; write UV2 = corner types
```

**Shaders**

- Ground: splat with world mapping.
- Cliff: UV0, plus a world macro tint and optional triplanar at LOD1+.
- Water: depth fade.

---

## 19. Risks and open questions

1. **FBX handedness.** The compass test in Phase 0 is mandatory, because the lookup table depends on it.
2. **Cliff-foot cells.** Low cells at the foot of a cliff lose up to 1.05 m. Game design has to accept the no-building rule (constraint 3), or wait for the Phase 6 retaining-wall style.
3. **Cliff texture repetition.** The 1.5 m period is mitigated by chunks, displacement, macro tint and variants. If it still reads, move to a 1.5 × 3 m texture (v period = 2 tiers), which keeps every seam rule intact.
4. **Inner-corner UV stretch.** It is 27 % in arc interiors, which is acceptable because those arcs are short and partly occluded.
5. **Splat needs a custom shader.** Surface types depend on the custom shader in both Unity (Shader Graph) and Blender (Attribute node). The decal fallback is inferior.
6. **Palette dependency.** `T_VK_Cliff`, `T_VK_Cobble` and the chunk palette should be finalized after the stone-texture rework so rock reads as one family.

Files referenced (read-only): `C:/Users/danie/AppData/Roaming/Claude/scratch-workspaces/ec03f06b-60f5-4d5d-94a9-dff3a56c5f56/f8ddc2b6-f8a4-41c6-98db-14b97d4348ea/scratch-2026-09-23-d49817/code/vk_helpers.py`, `vk_tex.py`, `vk_texgen.py`, `vk_mat.py`, `vk_nature.py`, `kit_pieces.txt` (same folder).