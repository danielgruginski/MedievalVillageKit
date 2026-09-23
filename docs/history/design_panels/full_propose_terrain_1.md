# Terrain Tile Kit: dual-grid marching squares (colony-sim and Unity spec)

## 0. Decisions

| Topic | Decision |
|---|---|
| Game cell | **3.0 m = `CELL`**. This is the same grid as the wall modules, footprints, fences (`fence_run` 3 m segments), `low_wall(L=CELL)` and crop beds (`soil_bed` 2.9 m). |
| Data location | Per **game cell**: level, water, ramp, ground type. This is the only data the simulation stores. |
| Render tile | 3.0 × 3.0 m, **offset by half a cell**. Each render tile is centred on a building-grid vertex `(3I, 3J)`, and its 4 corners are the centres of the 4 cells that meet there. This is a dual grid: the tile is chosen from its 4 corner states. |
| Why the offset | Every game cell keeps one height and one type. Transitions (cliffs, shores, path edges) always fall on cell borders, where walls and fences already sit. No cell is ever "half slope", so pathing and placement stay trivial. |
| Level step | **TIER = 1.5 m** (H1/2). Two tiers equal one storey. A 1-cell ramp is 1.5 m over 3 m, about 26.6°, which is walkable. |
| What is geometry | Level (cliffs), water (shore) and ramps/stairs only. |
| What is shader-only | Ground types (grass, dirt, cobble, sand, rock) come from a cell-resolution control texture. Painting roads or wear never rebuilds a mesh. |
| Stacking | Binary layer decomposition. Tile at layer ℓ uses `mask = corner_level ≥ ℓ`, placed at z = ℓ·1.5. |
| Unique meshes | Cliff 5, Shore 5 (+ Full reused), Ramp/Stair 6, Water quad 1. That is **17 base meshes, about 28 with variants**. |
| Irregularity | (1) Authored interior-only variants windowed to 0 at tile edges. (2) A global world-space horizontal displacement applied after assembly. Both are seam-proof by construction. |
| UVs | None needed. The shader works in world space: planar tops, triplanar cliffs. This is rotation-invariant and continuous by construction. |

Rejected alternative: storing data on the building-grid vertices, with render tiles aligned to the cells. A cell whose 4 corners differ then contains a slope, which leaves "partially buildable" cells and ambiguous pathing. The dual grid avoids this entirely.

---

## 1. Grid, coordinates and data model

### 1.1 Frames (Blender, Z up; Blender +Y = north = Unity +Z)
- Game cell `(i,j)` covers x∈[3i, 3i+3], y∈[3j, 3j+3]. Its centre is `(3i+1.5, 3j+1.5)` and its surface is at z = level·1.5.
- Render tile `V(I,J)` is centred on the grid vertex `(3I, 3J)`, for I∈[0..W], J∈[0..H]. The border tiles cover the outer half-cells. Cells outside the map are clamped to the nearest edge cell.
- Tile-local frame: the origin is the tile centre, x∈[-1.5, 1.5] east, y∈[-1.5, 1.5] north. **z = 0 is this layer's top surface.** The lower floor is at z = −1.5.
- Corner bits run counter-clockwise (CCW) from SW:

| bit | corner | local position | cell |
|---|---|---|---|
| 0 (1) | SW | (−1.5, −1.5) | (I−1, J−1) |
| 1 (2) | SE | (+1.5, −1.5) | (I, J−1) |
| 2 (4) | NE | (+1.5, +1.5) | (I, J) |
| 3 (8) | NW | (−1.5, +1.5) | (I−1, J) |

- Tile sides also run CCW. Side k connects bit k to bit (k+1)%4: S = SW→SE, E = SE→NE, N = NE→NW, W = NW→SW.

### 1.2 Cell struct (4 bytes; occupancy is stored separately)
```
level  : u8   0..15   z = level*1.5
ground : u8   0 Grass,1 Dirt,2 Cobble,3 Sand,4 Rock   (painted; shader only)
flags  : u8   b0 water | b1-3 rampDir (0 none,1 N,2 E,3 S,4 W) | b4 stairStyle | b5 stiff(auto) | b6 noBuild(auto)
wear   : u8   traffic counter -> dirt blend (desire paths)
```
Rules the game validates on edit:
- A **water** cell must be a local minimum: every 8-neighbour has level ≥ its level. This guarantees a water corner is always its tile's minimum level (see §6).
- A **ramp** cell R (level L, dir d) needs:
  - its neighbour H in direction d at level L+1;
  - its back neighbour at level L and not water;
  - each side neighbour either at level L with its d-neighbour at L+1, or another ramp with the same d and the same levels. In short, the ramp needs a straight cliff one cell wider than the ramp on each side.
- The ramp's R and H cells get `stiff` and `noBuild` set. Building footprint cells also get `stiff`.

---

## 2. Cases, rotation convention and lookup table

Rotation `r` is the number of **90° CCW turns about +Z** (Blender), applied about the tile centre. A CCW turn moves bit k to bit (k+1)%4:
`rotl(m) = ((m<<1) | (m>>3)) & 15`. A mask equals `rotl^r(canonical)`.

The canonical orientations follow the kit's wall convention (face toward local −Y):

| Case | Canonical mask | Meaning | Cliff line (canonical) |
|---|---|---|---|
| Empty | 0 | nothing (upper layers only) | none |
| OuterCorner | 8 (NW high) | convex plateau corner | quarter arc, radius 1.5, centred on NW, from (−1.5, 0) to (0, 1.5) |
| Edge | 12 (NW+NE high) | straight cliff facing −Y | line y = 0 |
| InnerCorner | 13 (all but SE) | concave pocket | quarter arc, radius 1.5, centred on SE, from (0, −1.5) to (1.5, 0) |
| Saddle | 5 (SW+NE high) | diagonal highs, separated; the low floor connects through the centre | two outer arcs, centred on SW and NE |
| Full | 15 | flat top | none |

**Lookup table** (index = mask), identical in Python and C#:
```
MS = [(EMPTY,0),(OUTER,1),(OUTER,2),(EDGE,2),(OUTER,3),(SADDLE,0),(EDGE,3),(INNER,2),
      (OUTER,0),(EDGE,1),(SADDLE,1),(INNER,1),(EDGE,0),(INNER,0),(INNER,3),(FULL,0)]
```
Free extra rotations, chosen by position hash: Full can use any r∈0..3, Saddle can use r or r+2, and the shore Bed can use any r. These are seam-safe because every edge of those tiles is of the same kind.

Placement:
- Blender: `loc = (3I, 3J, ℓ*1.5)`, `rot_z = r*π/2`.
- Unity: `pos = (3I, ℓ*1.5, 3J)`, `rot = Euler(0, -90*r, 0)`. Unity yaw is clockwise when seen from above. See the §12 axis test.

---

## 3. Multi-level stacking (cliff tiers)

For each render tile:
```
lv = [level(c) for c in corners]; lo, hi = min(lv), max(lv)
emit BASE layer at ℓ=lo : Shore set if any water corner else Cliff.Full      (mask always 15)
for ℓ in lo+1 .. hi:
    m = sum(1<<k for k in 0..3 if lv[k] >= ℓ)
    mesh, r = MS[m]; if mesh is EDGE and a crossing side is a ramp edge -> ramp mesh (§7)
    emit (mesh, r, variant(hash(I,J,ℓ))) at z = ℓ*1.5
```
- Each layer mesh draws **only the high region**: top at z = 0, cliff face down to −1.5, and a skirt to −2.7. The low region is drawn by the layer below.
- Worked example: SW=2, SE=0, NE=1, NW=2. Layer 0 is Full. Layer 1 has mask 13, so InnerCorner r0. Layer 2 has mask 9, so Edge r1.
- Buried geometry: parts of lower layers under higher tops are invisible. About 1 extra flat patch per multi-level tile; accept it.
- **Seam proof across different mins.** Take neighbouring tiles A and B sharing edge corners c1 and c2.
  - For a layer ℓ < min_B, both c1 and c2 are ≥ ℓ, so A's edge there is FLAT and lies under A's own layer ℓ+1. It is buried.
  - For ℓ > max_B, both bits are 0, so the edge is empty.
  - Therefore crossing edges only occur at layers both tiles emit. The seam test (§15) uses exactly this rule.
- Two-level cliffs (corner difference ≥ 2) are two stacked 1.5 m bands. The toe/lip geometry (§4) produces a 0.1–0.15 m strata ledge between bands, which is intentional.

---

## 4. Seam contract: each edge depends only on its two corners

Every vertex that lies on a tile side (|x| = 1.5 or |y| = 1.5, tolerance 1e-5) must belong to the **edge profile** for that side's type. The profile fixes three things per vertex: position, analytic normal, and vertex colour (RGB = AO, A = wet). d is measured along the side **from the high corner** (for shore sides, from the land corner). Any tile, rotation or variant then produces identical edge vertices.

| Side bits | Set | Edge type | Vertices |
|---|---|---|---|
| 1,1 | any | FLAT | d = 0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0; z = 0; AO 1; wet 0 |
| 0,0 | Cliff | EMPTY | none |
| 0,0 | Shore | BED | the same 7 d values; z = −1.2; AO 0.6; wet 1 |
| 1,0 | Cliff | CLIFF P | see below |
| 1,0 | Shore | SHORE Q | see below |
| 1,0, ramp flag | Ramp | RAMP R | d = 0…3 step 0.5; z = −0.5·d; AO 1 |
| 1,0, stair flag | Stair | STAIR S | (0,0) (0.25,0) (0.25,−0.25) (0.75,−0.25) (0.75,−0.5) (1.25,−0.5) (1.25,−0.75) (1.75,−0.75) (1.75,−1.0) (2.25,−1.0) (2.25,−1.25) (2.75,−1.25) (2.75,−1.5) (3.0,−1.5) |

**Cliff profile P** (d, z, AO). The crossing is at d = 1.5, the cell border.
```
0 (0.00, 0.00,1.00)  1 (0.50, 0.00,1.00)  2 (1.00, 0.00,1.00)
3 (1.28,-0.03,1.00)  <- lip start = boundary of the top region
4 (1.42,-0.12,1.00)  5 (1.55,-0.30,0.95)  6 (1.70,-0.55,0.90)
7 (1.80,-0.85,0.84)  <- max bulge, 0.30 m into the low cell
8 (1.76,-1.12,0.78)  9 (1.62,-1.35,0.70)
10 (1.45,-1.52,0.60) <- toe, 2 cm below the floor (hides the crack)
11 (1.45,-2.70,0.45) <- skirt bottom, open edge; hides stacking gaps and water depth
```
Footprint cost: 0.22 m of the high cell and 0.30 m of the low cell.

**Shore profile Q** (from the land corner). The water surface is at z = −0.35, so the shoreline falls at d ≈ 1.69.
```
(0,0) (0.5,0) (1.0,0) (1.28,-0.03) (1.45,-0.12) (1.62,-0.28)w (1.85,-0.52)w (2.15,-0.86)w (2.50,-1.12)w (3.0,-1.20)w
```
Vertices marked `w` have wet = 1.

**Construction** (this is what guarantees the contract):
1. **Face: sweep.** The cliff line C(t), t∈[0,1], is a straight line or a quarter arc. Arcs centred on a corner meet the side midpoints perpendicular to the side, so the swept cross-section at t = 0 and t = 1 lies exactly in the side plane and equals P.
   - Offset `s = 1.5 − d` is positive toward the high side.
   - Edge: position = C(t) + s·n̂.
   - OuterCorner: radius ρ = d from the high corner.
   - InnerCorner: ρ = 3 − d from the low corner.
   - Columns: 7 for Edge (every 0.5 m), 6 for arcs.
   - Rows: P[3..11], giving 8 strips.
2. **Top region: constrained Delaunay** with `mathutils.geometry.delaunay_2d_cdt(verts, edges, [], 1, 1e-6)`.
   - Constraint polygon: the side vertices from the table, plus the row-3 (lip-start) curve.
   - Interior points: a 0.5 m lattice, dropping points within 0.2 m of the boundary.
   - Check that no Steiner points were added: output vertex count equals input count.
3. **Normals.** Set custom split normals on every side vertex to the analytic profile normal. Flat and bed sides use (0,0,1). Crossing sides use the 2D profile normal inside the side plane. Interior vertices use smooth normals.
4. **Saddle geometry.** The two bulges reach 1.80 m from opposite corners. The diagonal is 4.24 m, so the gap at mid-height is 0.64 m and the bulges never overlap.

**Kit caveats:**
- Terrain must **not** use `Kit.finish()` defaults. Its `wobble` is periodic in tile-local x and is applied before rotation, which breaks seams. Its `grime` also sets vertex colours.
- Use a new `tk_finish()` in the style of `nk_finish`: remap materials to the used slots only, write AO/wet colours, set custom normals, and do not call `Kit.project`.

---

## 5. Hand-made irregularity without breaking seams

**Layer 1: authored variants (mesh interior only).** Offsets are applied to the swept face and lip in s, multiplied by a window `w(t) = sin²(πt)` that is 0 at both tile sides. Nothing moves within 0.35 m of a side.

| Variant | Recipe |
|---|---|
| Edge_A | plain; lip wiggle `Δs = 0.08·sin(4πt + φ)·w` on rows 3–4 |
| Edge_B | buttress: `Δs = +0.22·w·g(row)`, where g over rows 5..10 is 0.3, 0.7, 1, 0.8, 0.4, 0; plus a vertical crack `−0.15·exp(−((t−0.62)/0.06)²)` |
| Edge_C | recess `−0.18·w·g`; plus 2 embedded boulders (`vk_nature.boulder(sub=1, cuts=5, mi=ROCK)`, 0.9×0.6×0.7 m, at t = 0.3 and 0.7, row 7, sunk 50%) |
| Outer_A/B, Inner_A/B | the same recipes with A/B amplitudes along the arc |
| Saddle_A, Full | one mesh each; variety comes from rotation |

- **Mirrored copies:** Edge mirrored in x, and Outer/Inner mirrored across their diagonal, are also valid for the same mask. The generator can emit them automatically, doubling the variants.
- **Variant pick:** `h = hash32(I, J, ℓ)`, `variant = h % n`, extra rotation `(h >> 8) % k`. The pick is stable per position.

**Layer 2: global world-space displacement.** Applied in the chunk assembler, after placement, to every vertex. It is horizontal only (dz = 0), so tops, treads and building bases stay exactly at level·1.5. Because it is a pure function of world position, coincident seam vertices stay coincident across tiles and chunks.
```
D(p) = A(p) * ( 0.28*vn(p.x/6, p.y/6, p.z/4, 11) + 0.08*vn(p/1.6, 13),
                0.28*vn(p.x/6, p.y/6, p.z/4, 12) + 0.08*vn(p/1.6, 14), 0 )
A(p) = 1 - smoothstep(0, 0.5, bilinear_cells(stiff, p.xy))
```
- `A` straightens the cliffs under buildings, ramps and stairs, and is still seam-safe.
- `vn` is trilinear value noise with smoothstep interpolation over an integer-lattice hash. It must be portable between Python and C#, with 32-bit wraparound after every multiply:
  `h=seed; h^=x*0x8da6b343; h^=y*0xd8163841; h^=z*0xcb1ab31f; h^=h>>16; h*=0x7feb352d; h^=h>>15; h*=0x846ca68b; h^=h>>16` → `h/2³²·2−1`.
- Effect: cliff lines and lips wander about ±0.36 m across tiles, which removes the "3 m blocky" read from the top camera.
- The maximum gradient is about 0.6. The closest profile rows are 0.14 m apart, so no triangles flip.

**Normals after displacement are analytic, not recalculated:** `n' = normalize(J⁻ᵀ n)`, with J = I + ∂D/∂p by central differences (ε = 0.02 m). Both copies of a seam vertex evaluate the same global function and get identical normals. Welding is not needed and chunk borders are safe.
- Never call `RecalculateNormals` on unwelded chunks; it causes lighting seams.

**Layer 3: scatter** (instanced, not in the tile mesh, per tile by hash):
- lip grass cards (`card()` with FOL "grass"), 2 per crossing side, 0.3 m inside the high cell, hanging over the lip;
- toe scree (`make_rock_cluster`/`make_pebbles` scaled 0.5) on the low side, 30% chance;
- reeds (`make_tufts "reeds"`) on shore sides;
- flowers and pebbles by ground type.

Scatter is excluded from building, road and farm cells.

**Layer 4: shader.** Macro noise, height-blended splat and a lip rim highlight (§8).

---

## 6. Water and shore
- The water mask at the **base layer only** uses bit = 1 for land. The Shore set is the Cliff topology with profile Q, and its low region is **drawn** as a bed at −1.2.
- Table: `SHORE = MS` except mask 0 → Bed (r random) and 15 → Cliff.Full.
- Saddle means separate land with water connected diagonally, which is good for diagonal rivers.
- Water surface: per chunk, one 3×3 quad (2 tris) at `z = level·1.5 − 0.35` for every render tile with any water corner. Land hides the rest.
  - Unity uses its own water material (depth fade and shore foam from the scene depth). The Blender preview uses `M_VK_Water`.
- A cliff dropping into water just works:
  - The cliff skirt bottom (−2.7 local) equals the bed depth.
  - The shore bank is 0.1–0.2 m wide and shows as a thin beach at the cliff foot.
- The existing `make_pond` stays as a decorative prop; water cells are the terrain version.
- Out of scope for now: fords, and waterfalls, which would be a prop on an Edge cliff with water on both levels.

---

## 7. Ramps and stairs (colony-sim essential)
- A ramp lives on the side between R's centre (level L) and H's centre (L+1). It is 2.4 m wide, centred on that side, and split across the two render tiles that share it.
- In canonical Edge (12):
  - `Ramp_HalfE` has its ramp surface on x∈[0.3, 1.5]. At the south side y = −1.5 it is z = −1.5; at the north side it is z = 0. It has a rock cheek on x∈[0, 0.3], and normal cliff on x < 0.
  - `Ramp_HalfW` is the mirror.
  - `Ramp_Mid` is used when both crossing sides are ramps (ramps 2+ cells wide, i.e. roads).
- Detection at layer ℓ:
  - The case must be Edge.
  - A crossing side is a ramp side if its low cell has `rampDir` pointing at its high cell and the levels are ℓ−1 and ℓ.
  - The canonical side = (world_side − r) mod 4, and it selects HalfE, HalfW or Mid.
- Contract:
  - The ramp side uses profile R (or S for stairs).
  - The north side stays FLAT with the standard 7 vertices.
  - The ramp foot on the south side lies exactly on the floor plane below. This is the one allowed unmatched open edge, and it is coplanar, so there is no visible crack.
- `Stair_*` is the same footprint with 6 risers of 0.25 m and treads of 0.5 m, material `M_VK_Ashlar` (submesh 1).
- Ramp mesh count: 3 × {Earth, Stair} = **6**.

---

## 8. Ground types and UV strategy (world-space, no rotation problems)
- **Control map:** an RGBA8 texture with 1 texel per cell (W×H), bilinear filtering, clamp, linear colour space.
  - Channels: R = max(Dirt painted, wear), G = Cobble, B = Sand (water cells are forced to Sand), A = Rock. Grass = 1 − sum.
  - With `uv = world.xy / (3·W, 3·H)`, texel centres land on cell centres. Bilinear sampling therefore **is** marching squares: along any cell border the weight depends only on those two cells.
  - A 1-cell path is 3 m wide and 2 cells is 6 m, matching the current `road_strip` roads of 6.8 and 5.6 m. An isolated cell becomes a rounded diamond patch.
  - Painting or wear updates only the texture (`SetPixels`), never a mesh.
- **Sharpening (hand-painted edge):** `m_i = saturate((w_i − 0.5 + 0.35·(H_i − 0.5) + 0.15·macroB) / 0.08 + 0.5)`. Composite in the order grass → sand → dirt → cobble → rock.
- **Tops:** planar world UVs, `uv = world.xy / tile_m`. Tangent frames are world X/Y everywhere, so normal maps stay consistent across rotated tiles.
  - Tile-local UVs would rotate with the tile and break continuity and tangents, which is why they are rejected.
- **Cliffs:** triplanar/biplanar in world space. The cliff blend is `c = smoothstep(0.80, 0.55, n.z)`. The lip rounding (0.55 < n.z < 0.9) stays grass and gets a +12% rim highlight, which outlines plateaus from the top-down camera.
- **Strata align to levels:** cliff `v = z/6.0` with strata seams every 1.5 m (4 per repeat), so seams coincide with tier boundaries.
- **No 3 m texture periods**, which would reveal the grid. Ground uses 4.0 m, cliff 6.0 m, macro 48 m.
- **Blender preview:**
  - The assembler writes UV "UVMap" = world xy (m) into the joined chunk mesh (chunk object at the origin).
  - The material uses Texture Coordinate Object → Mapping, and Image Texture `projection='BOX'`, `projection_blend=0.25` for cliffs, with Bump from `_H` (box projection has no tangents).
  - The control map is an Image Texture with `interpolation='Linear'`, `extension='EXTEND'`.
  - The normal-Z blend mirrors `vk_mat.mossy_material` (Geometry.Normal.Z plus height noise, then MapRange smoothstep).

---

## 9. Textures and materials (vk_tex / vk_texgen style, `write_set`)

| Set | Size / tile | Recipe |
|---|---|---|
| `T_VK_Grass` | 1024 / 4.0 m | fbm β = 2.2 clumps; 260 voronoi tufts drawn as short radial strokes (`draw_segments`, 6–14 px); ramp dark (0.10,0.20,0.04), mid (0.22,0.38,0.08), light (0.45,0.56,0.16); dry patches `smooth(1.2,1.8,fbm)` → (0.50,0.46,0.20); flower dots 0.3%; `painted_light`; rough 0.9. Must be isotropic. |
| `T_VK_Dirt` | 1024 / 4.0 m | packed earth mid (0.36,0.26,0.16), dark (0.22,0.15,0.09), light (0.52,0.42,0.28); voronoi pebbles (300 points, 25% shown); `crack_segments`; **no directional ruts**, since world UVs would align them to X. |
| `T_VK_Cobble` | 1024 / 4.0 m | 110 voronoi points with 2 Lloyd iterations; F2−F1 gap 0.012; domed stones; palette taken from the **reworked** `gen_stone` so plazas match walls; grass in 30% of joints (0.20,0.34,0.08); mortar (0.20,0.18,0.15). |
| `T_VK_Sand` | 1024 / 4.0 m | fine grain fbm (0.62,0.54,0.38), pebbles; wetness darkens ×0.6 with rough 0.35 (driven by vertex alpha). |
| RockTop | reuse `T_VK_Rock` at 4.0 m | lichen already present |
| `T_VK_Cliff` | **2048 / 6.0 m** | strata seams at v = 0, 0.25, 0.5, 0.75 (10 px, warped by `fbm(ax=4)`), 1–2 sub-strata per band; vertical joints from voronoi with sy = 0.4 (columns 0.6–1.2 m); `facets()` at 2 scales; top-lit `painted_light(L=(−0.2,0.9,0.4))`; warm grey-ochre (0.52,0.47,0.40)/(0.62,0.55,0.44)/(0.42,0.40,0.38); moss on upward-facing ledges (normal.y > 0.5) using `gen_moss` colours; drip streaks `fbm(ay=8)` at −10% below seams. It must read as natural layered rock, not masonry, and stay distinct from the `T_VK_Stone` rubble. |
| `T_VK_TerrainMacro` | 512 / 48 m | R hue shift, G brightness blotches, B blend noise |

Materials:
- One terrain material, `M_VK_Terrain`, covering top, cliff, bank and splat, so there is 1 draw call per chunk.
- Plus `M_VK_Ashlar` for stairs and a water material.
- Unity: the ground slices go in one `Texture2DArray` (all 1024); the cliff texture is separate.

---

## 10. Buildings and props on terrain
- **Snap:** footprints are in whole cells, the origin is the footprint centre, and z = level·1.5 exactly (tops have dz = 0; plinth rocks already sink 0.07).
- **Required code change:** `place()` currently ignores origin z. Extend `origin` to `(ox, oy, orz, oz)` and use `o.location.z = z + oz`. This also covers `_dress`, roofs and props.
- **Footprints:** register them on the root or in a table.

| Building | Footprint |
|---|---|
| house | n×2 |
| L-house | union of both wings |
| townhall | 5×2 |
| chapel | n×2 plus the tower cell at +x |
| barn, stable | n×2 |
| windmill, guard tower | 2×2 centred on a grid vertex |
| crop plot | 1×1 (ground is set to Dirt automatically) |

- **Validity:**
  1. All footprint cells have the same level, are not water, not ramp, and not Rock.
  2. No 4-neighbour of the footprint is higher. The exception is a "hillside" back wall with a +1 level difference: that wall is forced to plain ".", and the rock intersects the wall, which reads as built into the slope.
  3. The door cell's outward neighbour is walkable at the same level, or is a ramp/stair.
  4. Footprint cells are set to `stiff`, so the cliffs next to them are straight.
- **Drops at a building edge:** for each footprint side segment whose outside cell is 1 level lower, place **`SM_VK_Foundation_Drop`**:
  - 3 m wide, 1.5 m tall rubble-stone apron with its face at y = −0.45, flush with the plinth, covering the lip;
  - `_Corner` variant for outer corners; stack for 2+ levels.
- **Free props** (trees, rocks): sample only the "safe interior" of a cell, inset 0.6 m from any border with a different level or water, so z = level·1.5. Otherwise raycast (Blender BVHTree / Unity Physics). Forbid trees within 0.9 m of a crossing border.
- **Cliff railings:** `fence_run` offset 0.45 m into the high cell along Edge borders.
- **`build_town` migration:**
  - replace the `road_strip` roads with Dirt cells (main road 2 cells wide, south road 2 cells);
  - replace the plaza strip with Cobble cells (8×6);
  - give `scatter_trees` a check against terrain safe zones.

---

## 11. Pathing and gameplay
- The nav graph is the cell grid, built from `Cell` data and never from meshes.
- Walkable means: not water, not a building, and every orthogonal move is between cells of the same level, or along a ramp link R↔H.
- **No corner-cutting:** a diagonal move is allowed only if both orthogonal cells are walkable at the same level. This makes the saddle's visual gap irrelevant, so the default is forbidden.
- Move costs: Cobble 0.8, Dirt 0.9, Grass 1.0, Sand 1.2, Rock 1.1, Ramp 1.5, Stair 1.3.
- Wear: +1 per pawn step, decaying slowly; its dirt blend is `wear/255`, so desire paths emerge on their own.
- Optional Unity NavMesh bake from the chunk meshes is consistent with this: agent max slope 35° (ramps are 26.6° nominal, up to about 34° after displacement), step height 0.3 m (below one 1.5 m tier).
- Mouse picking: raycast the chunk collider, then take the cell from the hit xz. If the hit normal is steep (a cliff face), pick the cell on the high side.
- Build-mode grid overlay in the shader: `frac(world.xz/3)` lines.
- Terraforming a cell rebuilds the 4 render tiles around it (1–4 chunks).

---

## 12. Unity integration
- **FBX:** one `VK_TerrainTiles.fbx`. Tile centre at the origin, top at y = 0. Read/Write on, Tangents None, Compression Off, no colliders.
- **Axis test (mandatory once):** export `SM_VKT_AxisTest`, with arrow "N" toward Blender +Y and arrow "E" toward +X. In Unity, N must point to +Z and E to +X with identity prefab rotation. Adjust the FBX Forward/Up settings and Bake Axis Conversion until it does. Only then is `yaw = −90°·r` valid. Add an EditMode test: rotate the Outer mesh by r = 1 and assert its top vertices lie near the SW corner.
- **`TerrainTileSet` ScriptableObject:** meshes indexed by [set][case][variant], plus the `MS` and `SHORE` tables.
- **Chunks:** 16×16 render tiles (48 m).
  - The Burst job selects layers, transforms vertices, applies `D(p)` and the Jacobian normals, and writes vertices with position, normal, and colour RGBA8 (AO, AO, AO, wet), with no UVs. Use 32-bit indices.
  - Each chunk gets a MeshRenderer (2 submeshes: terrain, ashlar), a water mesh, and a MeshCollider built from LOD1.
  - Use Blender world coordinates inside the noise, `pB = (u.x, u.z, u.y)`, so Blender and Unity agree.
- **LOD1 per tile:** keep **every side vertex** (they are part of the contract; avoids T-junctions and holes after displacement) and decimate only the interior, targeting about 35%.
- **Map rim:** optional "diorama" skirt. Extrude each border tile's side profile down to −3 m with a soil texture.

---

## 13. Polycount budget (LOD0 triangles)

| Mesh | Tris |
|---|---|
| Full (6×6 grid) | 72 |
| Edge A | about 140 |
| Edge C, with boulders | 300 or less |
| OuterCorner | about 95 |
| InnerCorner | about 140 |
| Saddle | about 190 |
| Shore Edge | about 150 |
| Shore Bed | about 22 |
| Ramp half | 250 or less |
| Stair half | 350 or less |
| **Hard cap per tile** | **400** |

- A chunk is 256 tiles. With about 30% multi-layer tiles that is roughly 30k triangles. About 9 chunks are visible at a typical colony zoom, so about 270k triangles.
- LOD1 is about 35% of that.

---

## 14. Blender implementation (new module `vk_terrain.py`)
- Constants: `TIER=1.5`, `P_CLIFF`, `P_SHORE`, `P_RAMP`, `P_STAIR`, `FLAT`, `BED`, `MS`, `SHORE`.
- `gen_tile(set, case, variant, profile, fill_low)`: sweep plus CDT plus variant offsets, then `tk_finish()`. Objects are named `SM_VKT_<Set>_<Case>_<Var>` in the hidden collection `VK_TerrainTiles`, with properties `o["kit"]="VillageTerrain"`, `o["ms_set"]`, `o["ms_mask"]`, `o["cell_m"]=3.0`.
- `tk_tiles(grid)`: returns `(I, J, ℓ, mesh, r, var)` using the §3 pseudocode.
- `tk_build_chunk(grid, displace=True)`: instances, then joins into one mesh at the origin, then applies `D` and analytic normals (`normals_split_custom_set_from_vertices`), then writes UV = world xy. It also builds water quads.
- `tk_ground_ctl(grid)`: builds the `T_VK_GroundCtl` image.
- `gen_grass`, `gen_dirt`, `gen_cobble`, `gen_sand`, `gen_cliff` go in vk_texgen; `terrain_material()` goes in vk_mat.
- Mesh names:
  - Cliff: `SM_VKT_Cliff_Full`, `…_OuterCorner_A/B`, `…_Edge_A/B/C`, `…_InnerCorner_A/B`, `…_Saddle_A`
  - Shore: `SM_VKT_Shore_OuterCorner_A`, `…_Edge_A/B`, `…_InnerCorner_A`, `…_Saddle_A`, `…_Bed`
  - Ramps/stairs: `SM_VKT_Ramp_HalfE/HalfW/Mid`, `SM_VKT_Stair_HalfE/HalfW/Mid`
  - Water: `SM_VKT_WaterQuad`

---

## 15. Automated seam verification (run in Blender)
```
def tk_seam_test(trials=200, N=12, seed=1):
  # A. per-mesh signature (fast, run first)
  for mesh in all SM_VKT_*: for side k in S,E,N,W:
      got = sorted((d,z) of verts with local coord on side k)          # d from the high/land corner
      exp = profile_for(bits(canon_mask, k, (k+1)%4), set, ramp_side?)
      assert same count, max|Δ| < 1e-4, normal dot > 0.9998, |ΔAO|,|Δwet| < 1/255
  # B. random grids
  for t in range(trials):
      g = random_grid(N, rng)   # 40% smoothed fbm levels 0..3, 30% pure noise, 30% worst cases
                                # (checkerboards, 1-cell mesas/pits, 3-level jumps);
                                # water at local minima; ramps wherever validate_ramp() passes
      for disp in (False, True):
          T = tk_tiles(g); verts = world verts per (I,J,ℓ) plus their PRE-displacement local coords
          for adjacent tiles A|B, for ℓ in both emit lists:
              ea, eb = verts on the shared side (classified by local coords)
              KD-match ea<->eb (tol 1e-4): unmatched==0, normal angle<1°, colour equal
          for ℓ emitted by only one tile: assert that side is FLAT (buried) or EMPTY
      # C. holes: raycast down on a 0.25 m lattice over the chunk interior (BVHTree of joined mesh + water)
      #    every ray hits; hit.z within [lo*1.5-1.25, hi*1.5+0.01]
      # D. open edges after bmesh.ops.remove_doubles(dist=1e-4): each boundary edge must be
      #    chunk perimeter | skirt bottom (z = ℓ*1.5-2.7) | ramp foot (z = (ℓ-1)*1.5 on a side) | water quad
  report JSON {trials, mismatches, holes, bad_open_edges, worst_case_grid}; on failure build that
  grid in VK_TerrainDebug with red spheres on offending verts and an ortho top render
```
Also render a **case board**: all 16 masks in a 4×4 layout, plus the shore and ramp cases, top-down and at 45°, once with a checker material and once with `M_VK_Terrain`.

---

## 16. Build order and acceptance criteria

| Phase | Deliverable | Accept when |
|---|---|---|
| **1 Core cliff** | profiles, 5 cliff meshes (A), MS table, layered assembler, tests A–D with displacement off, flat preview colours | 0 mismatches in 200 grids; case board clean |
| **2 Look** | displacement + stiffness + analytic normals; `gen_cliff`, `gen_grass`, `M_VK_Terrain`; demo hill | tests pass with displacement on; no lighting seams in a raking-light render |
| **3 Ground and village** | control map + dirt/cobble/sand/rock; `place()` z-offset; footprint validity; `Foundation_Drop`; `build_town` on terrain (plateau at level 1, chapel hill at level 2) | the aerial render matches the current layout, roads are painted, nothing floats |
| **4 Water and ramps** | Shore set + water quads; ramps and stairs; scatter (lip grass, scree, reeds) | river demo; stairs from the plaza to the chapel hill; tests include water and ramps |
| **5 Variety and engine** | B/C and mirrored variants, LOD1, axis test, C# tables, FBX export | Unity chunk equals the Blender chunk vertex-for-vertex on the test grid |

Demo map (for renders): 32×24 cells.
- River at level 0 along the south, with shore.
- Meadow and farms at level 0/1.
- Village plateau at level 1: cobble plaza, 2-cell dirt main road entering by a 2-wide earth ramp.
- Chapel hill at level 3, reached by a stone stair.
- Forest ridge at levels 2–4 in the north.

## 17. New village pieces this enables
- `SM_VK_Foundation_Drop` and `_Corner` (rubble stone; picks up the reworked stone texture).
- `SM_VK_RetainingWall` and `_Corner` (ashlar with coping; placed on straight Edge borders of cobble/town cells; sets `stiff`).
- `SM_VK_CliffRail` (a fence variant on the lip).
- `SM_VK_Bridge_Plank`, spanning 1 water cell between same-level land cells.
- `SM_VK_Dock`, on a shore Edge.
- `SM_VK_Waterwheel`, on a shore Edge next to a house wall.

## 18. Open points for the user
- **TIER 1.5 m vs 3.0 m.** 3.0 m is more dramatic but needs 2-cell ramps. All profile z values scale linearly if it changes.
- **Diagonal squeeze.** Whether diagonal saddle squeezes should be walkable (default: no).
- **Map rim.** Map-edge presentation: clamp vs diorama skirt.