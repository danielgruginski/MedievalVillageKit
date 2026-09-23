# Terrain Tile Kit: Judge Report and Final Spec

## 1. Scores

| | Concreteness | Correctness / feasibility | Fit (WoW look, colony sim, this kit) | Risk (10 = low) | Overall |
|---|---|---|---|---|---|
| **P1** dual grid, per-cell data, 1.5 m tiers | 9 | 8 | 9 | 7 | **8.5 (winner)** |
| **P2** corners on building-grid vertices, 3.0 m tier, R1 | 9 | 7 | 6 | 6 | 7.0 |
| **P3** layered codes, about 180 baked meshes (truncated) | 5 | 7 | 6 | 4 | 5.5 |

**Why P1 wins.**
- Every game cell keeps one height and one ground type. Cliffs, shores and road edges fall on cell borders, where walls and fences already sit.
- Any height difference is handled by stacking binary layers, which needs only 5 cliff meshes.
- Shading is world-space, so the look is rotation-proof. Terrain is assembled at runtime, which suits terraforming.

**What is grafted from the others.**
- From P2:
  - profile art direction: turf lip overhang, strata ledge that catches moss, painted rim highlight;
  - a real dead-zone window for variant noise;
  - "blocks" face variant;
  - building snap formulas;
  - import settings;
  - hillside-house idea.
- From P3:
  - side vertices quantised to 1/1024 m, plus exact integer rotation;
  - oblique hole rays and back-face check;
  - determinism test;
  - anti-tiling second grass sample;
  - intent of seam-straddling rocks (implemented here with ownership by edge, not by tile).

---

## 2. Claims in the proposals that are wrong or inaccurate

**P1**
1. *"Along any cell border the bilinear weight depends only on those two cells."* This is wrong.
   - On a cell border, bilinear sampling reads 4 texels.
   - The claim holds along **render-tile sides**, the lines joining two cell centres.
   - Seams are not affected, because the sample is continuous everywhere.
2. *Reason given against `Kit.finish`.* The y-wobble is multiplied by `sin(π·clamp(z,0,6)/6)`, which is 0 for z ≤ 0. That covers all of P1's layer-local geometry.
   - The real seam breaker is the x-wobble `0.02·sin(2πz/2.3+0.4)`, which is still 7.8 mm at z = 0.
   - `finish()` also flat-shades faces, writes grime based on z, and appends all 45 materials.
   - The conclusion (do not use it) is correct.
3. *"sin²(πt) window, nothing moves within 0.35 m of a side."* This is false. sin² is only 0 at the endpoints; it is about 9.5 % at 0.3 m on an Edge. A window with a true dead zone is needed.
4. Edge_B's crack, `exp(−((t−0.62)/0.06)²)` along 3 m, is about 0.18 m wide. It cannot be represented with 0.5 m sweep columns.
5. *"Ramps up to ~34° after displacement."* This contradicts P1's own rule that A = 0 on stiff (ramp) cells. Ramps stay exactly 26.6°.
6. *"Aerial render matches the current layout."* This is impossible without a re-layout.
   - `build_town` places buildings off-grid: `street()` adds `uniform(0,3)` offsets, and the chapel is at (224, 2) with rot −90.
   - A new layout snapped to the grid is required.
   - The road widths quoted (6.8 m and 5.6 m) are correct, because `road_strip`'s `w` is a half-width.
7. `painted_light(L=(−0.2,0.9,0.4))` on a triplanar cliff texture: the lateral component flips between opposite projections. Use a light with no u component.
8. (Applies to all three proposals.) Kit's `Col` layer is a **byte** colour attribute. Blender linearises byte colours as sRGB in shaders, so a mask of 0.5 arrives as about 0.21. Terrain data must use a FLOAT_COLOR attribute.
9. Minor: `bmesh.ops.remove_doubles` needs `(bm, verts=..., dist=...)`.

**P2**
1. `delaunay_2d_cdt(..., output_type=3)`. Per the Blender 4.x API docs, 3 returns the *intersected constraint polygons with holes omitted*, not a triangulation of interior points. Use `1` on simply-connected regions.
2. Corners on building-grid vertices mean every cliff tile is a cell that is half high and half low. Each cliff line then blocks a whole row of cells in pathing, and a house needs (n+1)×3 equal corners. This is a design flaw for a colony sim rather than a factual error.
3. R1 (height difference ≤ 1 per edge) with a 3 m tier forbids any cliff taller than one tier except on diagonals. Its Steps piece is 45° (3.0 m rise over a 3.0 m run).
4. Its budget of about 0.82 M triangles for 64×64 tiles, and 800–1000 triangles per cliff tile, is heavy for the value it gives.

**P3**
1. The proposal is truncated. §1–5 and the start of §6 are missing: case codes, the PB/PS/PT profile tables, `EDGE_POLY`, and contours. It cannot be implemented as delivered.
2. `facets(2,30,0.25)` does not match the real signature `facets(S, seed, fmin, fmax, amp)`.
3. Stair_1T: 7 × 0.30 m = 2.1 m of run, but the stated span (b = 0.30 → 2.6) is 2.3 m.
4. A per-object Attribute node for tile types only works on unjoined instances, so it is incompatible with chunk joining.
5. Correct claims:
   - Float32 stays exact to 16 km for 1/1024-quantised coordinates on a 1.5 m lattice.
   - `Kit.project` builds U = n×Z per face, which breaks UVs on curved contours.

---

## 3. Resolved contradictions

| Topic | P1 | P2 | P3 | **Final** |
|---|---|---|---|---|
| Data location | per cell; render tiles centred on grid vertices (dual grid) | building-grid vertices | per tile corner | **P1 dual grid.** Marching-squares samples = cell centres. |
| Tier height | 1.5 | 3.0 | 1.5 | **1.5 m.** Ramps fit in one cell (26.6°); 2 tiers = H1 (enables hillside houses); tall cliffs come from stacking. |
| Height difference per edge | any | ≤ 1 | any (via Mixed pieces) | **any**, via binary layers |
| Mesh count | about 28 | 34 | about 180 baked | **19 base meshes plus variants.** Rotation at runtime. |
| Variation | sin² window plus global D | dead-zone window plus blocks | window plus E/N chunks | **Dead-zone window (P2), global world-space displacement D (P1), rocks owned by edges at crossings** |
| Tops | exactly flat | ±0.08 pillows | ±0.05 bumps | **Exactly flat** (buildings, pawns and props get exact z; D provides the organic look) |
| Cliff UVs | world triplanar | manual triplanar | arc-length contour UVs | **World box/biplanar.** Contour UVs are rejected for now (u-period constraints, 27 % arc stretch, extra test surface). |
| Ground types | cell control texture | corner data texture | UV2 per tile | **P1 control map**, with P2's painted outline and a threshold below 0.5 to connect diagonals |
| Vertex colour | RGB = AO, A = wet | R, G, B, A = AO, sand, rim, moss | — | **FLOAT_COLOR `TCol`: R = AO, G = rock mask, B = rim, A = wet/sand** |
| Materials | 1 | up to 6 | 3–5 | **`M_VK_Terrain` plus `M_VK_Ashlar` (stairs) plus water** |
| Chunks | 16×16, built at runtime | 8×8 CombineMeshes | 8×8 | **16×16 built at runtime** (Burst in Unity, numpy in Blender) |

---

# FINAL SPEC: `vk_terrain.py`

## 4. Grid, frames, data

**Frames.**
- Blender: Z is up, +X is east, +Y is north. Unity +Z is Blender +Y (verified by the axis test in §15).
- All world-space functions (noise, control map, textures) use **map-local** coordinates: `p = world − MAP_ORIGIN`.
- `MAP_ORIGIN` must be a multiple of 48 m. The demo uses (1200, 0, 0).
- Chunk objects sit at `MAP_ORIGIN` with no rotation, so their Object texture coordinates equal map-local coordinates.

**Constants.**
```python
TT=CELL           # 3.0  game cell = render tile size
TIER=1.5          # m per level
Q=1/1024          # quantum for every tile-side coordinate
SKIRT_Z=-2.70     # layer-local skirt bottom (= next floor −1.20 = bed depth)
WATER_Z=-0.35     # water surface below its cell's level
BED_Z=-1.20
LIP_D=1.22        # d of the top-region boundary (profile row 3)
MAP_ORIGIN=(1200.0,0.0,0.0)
```

**Game cells and render tiles.**
- Game cell `(i,j)`:
  - covers x ∈ [3i, 3i+3] and y ∈ [3j, 3j+3];
  - its centre is `(3i+1.5, 3j+1.5)`;
  - its surface is at `z = level·1.5`.
- Render tile `V(I,J)`, for I ∈ [0..W] and J ∈ [0..H], is centred on the grid vertex `(3I, 3J)`.
- Its 4 corners are the centres of the cells meeting there:

| bit | corner | local position | cell |
|---|---|---|---|
| 0 (1) | SW | (−1.5, −1.5) | (I−1, J−1) |
| 1 (2) | SE | (+1.5, −1.5) | (I, J−1) |
| 2 (4) | NE | (+1.5, +1.5) | (I, J) |
| 3 (8) | NW | (−1.5, +1.5) | (I−1, J) |

- Cells outside the map are clamped to the nearest edge cell.
- Tile sides are numbered k = 0 S, 1 E, 2 N, 3 W. Side k connects bit k to bit (k+1)%4.
- **d** is measured along a side from its high (or land) corner, from 0 to 3. Every transition crosses a side at **d = 1.5**, which is the cell border. The contour there is perpendicular to the side.

**Cell struct (4 bytes)** (P1):
```
level u8 (0..15)   ground u8 (0 Grass,1 Dirt,2 Cobble,3 Sand,4 Rock)
flags u8: b0 water | b1-3 rampDir (0 none,1 N,2 E,3 S,4 W) | b4 stair | b5 stiff(auto) | b6 noBuild(auto)
wear u8
```

**Validation, run on every edit:**
1. **Water** cell: all 8 neighbours have level ≥ its own. Water cells are never ramps and never inside a footprint.
2. **Ramp** cell R (level L, direction d):
   - `H = R + d` is at L+1;
   - `R − d` is at L and is not water;
   - each side neighbour S is either at level L with `S + d` at L+1, or is a ramp with the same direction and levels.
3. `stiff` is set automatically on building footprints, ramp R/H cells and Cobble cells. `noBuild` is set on ramp R/H cells.

## 5. Cases, rotation, lookup

Rotation r is the number of 90° CCW turns about +Z around the tile centre.
- `rotl(m) = ((m<<1)|(m>>3)) & 15`
- A tile's mask equals `rotl^r(canonical)`.
- Rotation is applied **exactly**: r = 1 maps (x, y) to (−y, x). No sin/cos.

| Case | Canonical mask | Contour (canonical, crossing curve) |
|---|---|---|
| Full | 15 | none |
| Edge | 12 (NW+NE high; cliff faces −Y, same as the wall convention) | line y = 0 |
| Outer | 8 (NW high) | arc centred on NW, from (−1.5, 0) to (0, 1.5) |
| Inner | 13 (SE low) | arc centred on SE, from (0, −1.5) to (1.5, 0) |
| Saddle | 5 (SW+NE high; low ground connects) | two Outer arcs, centred on SW and NE |
| Outer_Sq / Inner_Sq | 8 / 13 | polylines (−1.5,0)→(0,0)→(0,1.5) and (1.5,0)→(0,0)→(0,−1.5) (mitred) |

**Lookup table** (checked against `rotl` for all 16 masks; the same list is used in Python and C#):
```python
MS=[(EMPTY,0),(OUTER,1),(OUTER,2),(EDGE,2),(OUTER,3),(SADDLE,0),(EDGE,3),(INNER,2),
    (OUTER,0),(EDGE,1),(SADDLE,1),(INNER,1),(EDGE,0),(INNER,0),(INNER,3),(FULL,0)]
SHORE=list(MS); SHORE[0]=(BED,0); SHORE[15]=(FULL,0)     # bit = land
```

Free extra rotations, chosen by hash (these are seam-safe):
- Full and Bed: any r.
- Saddle: r or r+2.

Placement:
- **Blender:** `loc = MAP_ORIGIN + (3I, 3J, ℓ·1.5)`, `rot_z = r·π/2`.
- **Unity:** `pos = (3I, ℓ·1.5, 3J)`, `yaw = −90·r`. Valid only after the axis test.

## 6. Layer stacking (P1, unchanged)

```python
def tk_tiles(G):
  for J in range(G.H+1):
    for I in range(G.W+1):
      c=corners(I,J); lv=[x.level for x in c]; lo,hi=min(lv),max(lv)
      land=sum(1<<k for k in range(4) if not c[k].water)
      h=hash32(I,J,0)
      if land!=15: case,r=SHORE[land]; yield (I,J,lo,"Shore",case,r,var(h,case,c))
      else:        yield (I,J,lo,"Cliff",FULL,h&3,0)
      for l in range(lo+1,hi+1):                      # mask never 0 or 15 here
          m=sum(1<<k for k in range(4) if lv[k]>=l)
          case,r=MS[m]
          if case==EDGE: case=ramp_override(I,J,l,r,c) or EDGE     # §9
          yield (I,J,l,"Cliff",case,r,var(hash32(I,J,l),case,c,l))
```

- Each layer mesh draws **only its high region**:
  - top at local z = 0;
  - face down to −1.5;
  - skirt down to −2.70.
- The base layer draws the full tile at `lo`. Buried patches are accepted.
- **Nesting guarantee.** The mask at layer ℓ+1 is a subset of the mask at layer ℓ. The contours (lines through side midpoints, and radius-1.5 arcs about corners) are nested, and touch only at shared crossings where the height difference is 2 or more.
  - An upper band's toe and skirt (at d = 1.45) therefore always land on the lower band's top or lip.
  - That seals the stack.
  - Worked example: SW=2, SE=0, NE=1, NW=2 → base Full at 0, layer 1 is Inner r0 (mask 13), layer 2 is Edge r1 (mask 9).
- **Seam argument.** If a layer is emitted by only one of two neighbours, the shared side is FLAT and buried under that tile's next layer, or it is EMPTY. The tests use exactly this rule.

## 7. Seam contract

**Rule 1: vertices on a side.** Every vertex with |x| = 1.5 or |y| = 1.5 (within 1e-5) must take the following **exactly** from the profile for that side's type:
- its position, quantised to Q;
- its normal;
- its `TCol` values;
- the material index of the faces touching it.

**Rule 2: what the profile depends on.** The profile for a side depends only on:
- the set;
- the side's two corner bits at that layer;
- the ramp/stair flag.

**Rule 3: rotation and placement stay exact.** Rotations only swap and negate coordinates, and placement offsets are multiples of 1.5. Neighbouring side vertices are therefore bit-identical in float32 before displacement D.

| Side bits (a, b) | Set | Type | Vertices (d from the high or land corner) |
|---|---|---|---|
| 1,1 | any | FLAT | d = 0, 0.5, …, 3.0 (7 vertices); z = 0; n = (0,0,1); TCol (1,0,0,0) |
| 0,0 | Cliff | EMPTY | none |
| 0,0 | Shore | BED | same 7 d values; z = −1.20; TCol (0.55,0,0,1) |
| 1,0 | Cliff | CLIFF | `P_CLIFF`, 14 rows |
| 1,0 | Shore | SHORE | `P_SHORE`, 13 rows |
| 1,0 + ramp | Ramp | RAMP | d = 0…3 step 0.5; z = −0.5·d; n ∝ (0, 0.5, 1) in the side plane |
| 1,0 + stair | Stair | STAIR | P1's 14-point list: 6 risers × 0.25 m, 0.5 m treads, 0.25 m top and bottom landings, flat-shaded |

**Cliff profile.** Layer-local z (top 0, lower floor −1.5). TCol = (AO, rock, rim, wet).
```python
P_CLIFF=[ #  d      z     AO   rock rim   sharp
 (0.00, 0.000, 1.00, 0, 0.00, 0),
 (0.50, 0.000, 1.00, 0, 0.00, 0),
 (1.00, 0.000, 1.00, 0, 0.15, 0),
 (1.22,-0.015, 1.00, 0, 0.60, 0),  # 3 lip start = top-region boundary
 (1.40,-0.060, 1.00, 0, 1.00, 0),  # 4 sunlit crest (painted rim)
 (1.54,-0.150, 0.90, 0, 0.40, 1),  # 5 turf edge, 4 cm overhang; faces BELOW use rock=1, AO .45
 (1.48,-0.240, 0.45, 1, 0.00, 1),  # 6 root/soil recess
 (1.56,-0.620, 0.75, 1, 0.00, 0),  # 7 upper face
 (1.76,-0.680, 0.95, 1, 0.00, 0),  # 8 strata ledge nose (ledge top n.z≈0.96, catches moss)
 (1.70,-0.800, 0.55, 1, 0.00, 0),  # 9 ledge underside
 (1.80,-1.060, 0.85, 1, 0.00, 0),  # 10 max bulge, 0.30 m into the low cell
 (1.70,-1.340, 0.70, 1, 0.00, 0),  # 11
 (1.45,-1.520, 0.55, 1, 0.00, 0),  # 12 toe, tucked, 2 cm under the floor (this is what lets bands stack)
 (1.45,-2.700, 0.45, 1, 0.00, 0),  # 13 skirt bottom, open edge
]
```

Properties of this profile:
- z decreases monotonically, so the sweep never folds.
- Footprint cost: 0.28 m of the high cell and 0.30 m of the low cell.
- Saddle clearance: 4.243 − 2 × 1.80 = 0.64 m at the bulge, and 1.34 m between the toes.

**Shore profile.** z is relative to the land level. Water surface is at −0.35 and the bed at −1.20. TCol A: 0 = grass, 0.5 = dry sand, 1 = wet.
```python
P_SHORE=[ # d      z     AO   A(wet)
 (0.00, 0.000,1.00,0),(0.50,0.000,1.00,0),(1.00,0.000,1.00,0),
 (1.22,-0.015,1.00,0),             # top boundary (rim .4)
 (1.40,-0.050,1.00,0),             # turf crest (rim .8)
 (1.52,-0.120,0.90,0),  # sharp; faces below: A=.5, AO .6
 (1.48,-0.190,0.60,0.5),           # turf underside, sand starts (sharp)
 (1.62,-0.260,0.85,0.6),
 (1.80,-0.350,0.85,1.0),           # waterline, 0.30 m into the water cell
 (2.05,-0.580,0.75,1.0),(2.35,-0.900,0.65,1.0),
 (2.65,-1.200,0.55,1.0),           # bank foot = boundary of the flat bed region
 (3.00,-1.200,0.55,1.0)]           # corner point
```

**Normals.** Normals are analytic and written as custom split normals.
- Rows 0–2 and all FLAT/BED sides: (0,0,1).
- Other rows: the normalised sum of the two adjacent segment normals in the (d, z) plane, rotated into the side plane (zero component along the contour).
- Rows 5 and 6 (and shore rows 5 and 6) are split: each face side uses its own segment normal.
- The TCol split at row 5 is **per loop**: loops of faces above use the row's values, and loops of faces below use rock = 1, AO = 0.45 (shore: A = 0.5). The grass/rock line is therefore exactly the turf edge.

**Kit rule.** Never pass terrain through `Kit.finish()` or `Kit.project()`. Use `tk_finish()` instead (§8).

## 8. Tile construction (`gen_tile(set, case, var, lod)`)

1. **Sweep.** The contour `C(σ)` is walked with the high side on the left. For each profile row (rows 3–13, or shore rows 3–11):
   - Edge: position = `C + s·n̂`, with `s = 1.5 − d` and n̂ pointing toward the high side.
   - Outer: ρ = d about the high corner.
   - Inner: ρ = 3 − d about the low corner.
   - Square variants: offset polylines with a mitred corner plus a 0.15 m chamfer column pair.
   - Column counts: Edge 13 columns (every 0.25 m); arcs 9 columns (8 segments); each leg of a square variant 7 columns.
   - LOD1 uses the same rows with half the columns. The end columns of the tile are unchanged, so side vertices are identical at every LOD.
2. **Top region** (and the shore bed region at −1.20):
   - Call `mathutils.geometry.delaunay_2d_cdt(verts, edges, [], 1, 1e-6)`.
   - Constraint loop: the side vertices from the tables, plus the row-3 curve (shore bed: the row-11 curve).
   - Interior points: a 0.5 m lattice, keeping only points ≥ 0.2 m from the boundary (1.0 m lattice at LOD1).
   - Every region is simply connected; the Saddle has two separate components.
   - Assert that the output vertex count equals the input count (no Steiner points).
3. **Full:** a 6×6 quad grid (72 tris). LOD1 is a 24-tri fan over the same 24 side vertices.
4. **Variant offsets** (§10, layer 1), then **snap**: every side vertex is overwritten from its table and quantised to Q.
5. **`tk_finish()`**, modelled on `nk_finish`:
   - Write loop data into a `FLOAT_COLOR` corner attribute `TCol`.
   - Call `me.normals_split_custom_set(loop_normals)`. Interior loop normals are area-weighted smooth normals of the displaced sweep, so do not call `normals_split_custom_set_from_vertices`, which cannot hold the per-face normals at rows 5–6. Side vertices take the analytic table normals.
   - Materials: slot 0 is `M_VK_Terrain` (new index constant `TERRAIN=45`, appended to `kit_mats()`); slot 1 is `M_VK_Ashlar` for stairs only.
   - Custom properties: `kit="VillageTerrain"`, `set`, `case`, `var`, `mask`, `lod`, and `sockets` (JSON list of `(kind,x,y,z,nx,ny,nz)`).
   - Put the object in the hidden collection `VK_TerrainTiles`.
   - Mirrored variants: mirror the canonical geometry across the case's symmetry axis (Edge: x → −x; Outer/Inner: the diagonal), flip winding and normals, and bake the result. Never use negative scale.
6. **Names:** `SM_VKT_<Set>_<Case>_<Var>[_LOD1]`, for example `SM_VKT_Cliff_Edge_B`, `SM_VKT_Cliff_Outer_Sq`, `SM_VKT_Shore_Bed`, `SM_VKT_Ramp_HalfE`, `SM_VKT_WaterQuad`.

## 9. Ramps and stairs (P1)

- A ramp lives on the tile side joining R's centre (level L) and H's centre (L+1).
- It is 2.4 m wide, centred on that side, and split across the two Edge tiles that share the side.
- Canonical Edge (12):
  - **`Ramp_HalfE`**:
    - ramp plane over x ∈ [0.3, 1.5], from (y = −1.5, z = −1.5) up to (y = +1.5, z = 0);
    - a closed rock cheek over x ∈ [0, 0.3];
    - normal cliff for x < 0.
  - **`Ramp_HalfW`** is the mirror.
  - **`Ramp_Mid`** is used when both crossing sides are ramps (2+ cells wide), giving 1.2 + 3 + 1.2 = 5.4 m for a 2-cell ramp.
  - `Stair_*` pieces use the same footprint with 6 risers of 0.25 m in ASHLAR.
- **Detection** (in `ramp_override`):
  - The case is EDGE at layer ℓ.
  - The low cell of a crossing side has `rampDir` pointing at its high cell, with levels (ℓ−1, ℓ).
  - `canon_side = (world_side − r) % 4`. Side 1 selects HalfE, side 3 selects HalfW, both select Mid.
- **Contract:**
  - The ramp side uses RAMP or STAIR.
  - The N side stays FLAT.
  - The ramp foot on the S side is the **only** allowed open edge: it lies on the floor below and is coplanar with it.
- Ramp cells get ground forced to Dirt.

## 10. Irregularity that cannot break seams

**Layer 1: authored variants (baked into tiles).**
- Window: `W(σ) = smoothstep(0.25, 0.75, σ) · smoothstep(0.25, 0.75, L − σ)`, where σ is the contour arc length. W is exactly 0 within 0.25 m of any side.
- A row weight `V` protects the toe and skirt (rows 12–13 never move), which keeps stacking sealed.

| Variant | Recipe (Δs is positive toward the high side) |
|---|---|
| all | lip wiggle on rows 3–5: `Δs = 0.07·n1(σ/0.9 + seed)·W` |
| Edge_A | lip wiggle only |
| Edge_B "blocks" | rows 7–11: face split into blocks 0.7–1.2 m long (block edges snap to columns). Each block gets `Δs = −U(0.04, 0.14)`, a ±0.03 linear yaw across the block, and joint columns at −0.02. |
| Edge_C "buttress" | rows 7–11: `Δs = −0.22·cosbump(σ; centre L/2 ± 0.3, width 1.0)`. Plus 2 `vk_nature.boulder(k, c, (0.9,0.6,0.7), seed, mi=TERRAIN, cuts=5, sub=1)` at σ ≥ 0.6 m from the sides, row 8, sunk 45 %, with TCol (0.8,1,0,0). |
| Outer_B, Inner_B | the "blocks" recipe along the arc |
| Saddle_A | lip wiggle only, with outward push ≤ 0.10 (keeps the 0.64 m gap) |

**Layer 2: global world-space displacement D** (P1). Applied by the chunk assembler after placement. It is horizontal only, so every top stays at exactly `level·1.5`.
```
D(p) = A(p)·( 0.28·vn(x/6,y/6,z/4,11) + 0.08·vn(x/1.6,y/1.6,z/1.6,13),
              0.28·vn(x/6,y/6,z/4,12) + 0.08·vn(x/1.6,y/1.6,z/1.6,14), 0 )
A(p) = 1 − smoothstep(0, 0.5, stiffBilinear(p.xy))    # texel centres = cell centres
```

- **Hash:** `vn` is trilinear value noise with smoothstep weights over `hash32(ix,iy,iz,seed)/2³²·2−1`.
- `hash32` must match bit for bit between Python and C#:
  - `h = seed`
  - `h ^= x·0x8da6b343`, then `h ^= y·0xd8163841`, then `h ^= z·0xcb1ab31f`
  - `h ^= h>>16; h *= 0x7feb352d; h ^= h>>15; h *= 0x846ca68b; h ^= h>>16`
  - Every operation is uint32.
  - In numpy, compute in `uint64` and mask with `& 0xffffffff` after every multiply. In plain Python, `(v*k) & M32` handles negative inputs.
- **Normals after D:**
  - `n' = normalize(J⁻ᵀ n)`, where `J = I + ∂D/∂p` by central differences (ε = 0.02).
  - Both copies of a seam vertex evaluate the same function, so no welding is needed.
  - Never recalculate normals on chunks.
- **Why D cannot open holes:** it is a smooth map of space. With det J > 0 it is a bijection, so geometry that was sealed stays sealed. The test asserts `min det J_xy > 0.3`.
- **Scope:**
  - D is not applied to water quads.
  - D is applied to scatter **anchor points** only.
  - It never moves buildings (A = 0 on stiff cells).

**Layer 3: scatter.** Scatter is instanced and never part of the tile seam contract.
- **Edge-owned seam rocks**, which break the canonical 0.5 m strip that would otherwise repeat every 3 m:
  - One candidate per (cell border with a level difference, layer ℓ), with `p = 0.35` from `hash32(border_id, ℓ)`.
  - Piece: `SM_VK_Rock_Small_A/B` at scale 0.8–1.3.
  - Position: 0.45 m into the low cell at the crossing, floor z − 0.05.
  - Also one lip tuft at the crossing (d = 1.40).
- **Tile sockets** (tiles generate them only at σ ≥ 0.2 m):
  - `lip`: new `SM_VKT_LipGrass` (3 hanging cards 0.35×0.30 m via `NK.lcard(..., cell="tallgrass", up=(0,0,-1))`, 15 % "wildflowers"), every 0.45 ± 0.1 m.
  - `toe`: `SM_VK_Rock_Pebbles` ×0.5 or `SM_VK_Rock_Small_B` ×0.6 at 30 %; `SM_VK_Plant_Fern` or `SM_VK_Mushrooms_*` at 15 %.
  - `shore`: `SM_VK_Plant_Reeds` at 40 %.
- No scatter on stiff, road, farm or water cells.

**Layer 4: shader.** Macro tint, height-blended splat, painted rim (§12).

## 11. Water and shore

- A tile with any water corner uses the Shore set at its base level (`lo` is the water level, by validation rule 1). Higher land corners stack Cliff layers on top.
- A cliff into water works without extra pieces:
  - the skirt bottom (−2.70) equals the bed depth;
  - the shore bank shows as a thin beach at the cliff foot.
- **Water quad:** `SM_VKT_WaterQuad` (3×3 m, 2 tris) at `lo·1.5 − 0.35`, for every tile with a water corner. Land hides the overlap.
  - Blender preview: `M_VK_Water`.
  - Unity: a depth-fade water shader with depth-edge foam.
- **Saddle:** land knobs with the water connected diagonally.
- Out of scope for v1: waterfalls, and water at different levels.

## 12. Ground types, materials and textures

**Control map `T_VK_GroundCtl`.**
- RGBA8, one texel per cell.
- Sampling: bilinear, clamp, linear colour space, **no mipmaps**, `uv = p.xy/(3W, 3H)`.
- Channels: R = max(Dirt, wear/255), G = Cobble, B = Sand (water cells are forced to 1), A = Rock. Grass is the base.
- Bilinear sampling is marching squares on the dual grid. A 1-cell road is about 3.3 m wide at τ = 0.45.
- Mask per layer:
  ```
  m = saturate((w − τ + 0.35·(H_layer − 0.5) + 0.15·(macro.B − 0.5))/0.08 + 0.5)
  ```
  - τ: Dirt 0.45, Cobble 0.45 (connects diagonals), Sand 0.50, Rock 0.55.
  - Sand also takes `max(m, smoothstep(0.2, 0.45, TCol.A))`.
- Composite order: grass → sand → dirt → cobble → rock.
- Painted outline on dirt and cobble: `col *= 1 − 0.2·4m(1−m)`.

**`M_VK_Terrain`** (new `terrain_material()` in vk_mat). It is one material with no UVs.
- Coordinates: Texture Coordinate → Object, which is map-local because the chunk is unrotated.
- **Ground:**
  - planar XY / 4.0 m for grass, dirt, cobble and sand;
  - rock top reuses `T_VK_Rock` at 4.0 m;
  - grass is sampled a second time at 13.1 m, rotated 37°, blended by macro.B (range 0.3–0.7).
- **Cliff:**
  - `T_VK_Cliff` via Image Texture `projection='BOX'`, `projection_blend=0.2`, on Object coordinates / 6.0;
  - `rockW = max(TCol.G, smoothstep(0.80, 0.55, N_world.z))`.
- **Moss:**
  - `rockW · smoothstep(0.54, 0.78, N.z + 0.75·(H_moss − 0.5))`, using the `T_VK_Moss` set;
  - these are the `M_VK_RockMossy` values (thresh 0.66, soft 0.12, noise 0.75).
- **Colour adjustments:**
  - AO: `×TCol.R`.
  - Rim: grass `×(1 + 0.15·TCol.B)`.
  - Wet: `smoothstep(0.6, 0.95, TCol.A)` → colour ×0.6, roughness 0.35.
  - Macro tint: `×(0.9 + 0.2·macro.R)`, plus a hue lerp toward (1.05, 1.0, 0.8) by 0.3·macro.G.
- **Normal:** a Bump node on the blended height (strength 0.4 on ground, 0.8 on cliff). Box projection has no tangents, so no Normal Map nodes.
- **Roughness constants:** grass 0.9, dirt 0.95, cobble 0.85, sand 0.8, cliff 0.85.
- About 17 image nodes in total.
- In Unity, the same graph uses world-XZ planar mapping and a triplanar (whiteout) cliff.

**Textures** (vk_texgen style, `write_set`, colours in sRGB):

| Set | Size / tile | Recipe |
|---|---|---|
| `T_VK_Grass` | 1024 / 4.0 m | `t = smooth(−1.2, 1.2, fbm(β 2.8, fmin 2))`<br>`ramp3(t, (0.16,0.30,0.07), (0.30,0.48,0.12), (0.55,0.68,0.22), 0.55)`<br>dry patches `smooth(1.1, 1.8, fbm)` → lerp 0.6 toward (0.62,0.58,0.30)<br>2500 blade strokes via `draw_segments` (10–22 px, 2–3 px wide, ±35° around a random angle per voronoi clump of 120 points; **isotropic overall**), tips +12 %<br>flower dots (white/yellow) at 0.3 % in lush areas<br>`painted_light` default L; rough 0.9; depth 0.02 |
| `T_VK_Dirt` | 1024 / 4.0 m | `ramp3((0.30,0.21,0.13), (0.45,0.34,0.22), (0.58,0.47,0.32))`<br>voronoi pebbles (300 points, 25 % shown) (0.55,0.52,0.46)<br>`crack_segments(n=6, w0=1.5)` ×0.7<br>sprigs 20 %<br>no directional ruts; rough 0.95 |
| `T_VK_Cobble` | 1024 / 4.0 m | 110 voronoi points with 2 Lloyd iterations (circular mean for the torus)<br>dome `√clip((F2−F1)/0.05)`<br>joints `smooth(0.006, 0.018, F2−F1)` in (0.20,0.18,0.15), grass in 30 % of joints<br>stone palette **taken from the reworked `T_VK_Stone`**<br>`facets(S, seed, 6, 60, 0.08)` |
| `T_VK_Sand` | 1024 / 4.0 m | (0.72,0.64,0.46) → (0.80,0.71,0.52); weak `fbm(ax=6)` ripples; 150 pebbles; rough 0.8 |
| `T_VK_Cliff` | **2048 / 6.0 m** | v up = `1 − y` (the array is flipped on write). 4 bands per repeat, so **band boundaries sit at world z = 1.5k (tier boundaries)**.<br>Band-local b ∈ [0, 1):<br>– primary groove at b = 0 (10 px, darkest)<br>– secondary seam at b = 0.50 (the geometric ledge at z_local ≈ −0.74)<br>– soil band b > 0.86 (0.24,0.17,0.11) with root strokes (`crack_segments(n=30, dirbias=+π/2)`)<br>Per-band voronoi joints (sy = 0.4, columns 0.5–1.1 m); block dome plus `facets(S, s, 3, 30, 0.20) + facets(S, s, 8, 80, 0.08)`.<br>Band palettes, k = 0..3: sandstone (0.66,0.54,0.38), granite (0.56,0.55,0.53), tan (0.70,0.61,0.46), grey-violet shale with laminations (0.48,0.45,0.50).<br>Block top rim +15 %, under-ledge −25 %, `painted_light(L=(0,0.85,0.5))` (no lateral component), moss on up-facing block tops using the `gen_moss` palette, drips `fbm(ay=8)` ×0.9 below seams.<br>Must read as layered rock, not masonry. depth 0.10. |
| `T_VK_TerrainMacro` | 512 / 48 m, data | R = value blotches, G = dry/lush, B = blend noise (β 2.2) |

## 13. Buildings and props on terrain

- **Snap formula.** For an n×2 building with its footprint min-cell at (a, b):
  - rot 0/180: `origin = (3a + 1.5n, 3b + 3, orz)`;
  - rot 90/270: `origin = (3a + 3, 3b + 1.5n, orz)`.
  - Only multiples of 90° are allowed.
- **Code change in `place()`:** accept `origin = (ox, oy, orz[, oz])` and use `z + oz`. This is backward-compatible, and every builder goes through `place`/`place_v`.
- **Footprint registry:** `o["footprint"]` holds the list of cells.

| Building | Footprint |
|---|---|
| house, barn, stable | n×2 |
| L-house | union of both wings |
| townhall | 5×2 |
| chapel | n×2 plus the tower cell |
| windmill, guard tower | 2×2 centred on a grid vertex |
| crop plot | 1×1 (ground is set to Dirt) |

- **Validity rules:**
  1. All footprint cells are at the same level, not water, not ramp, not Rock.
  2. No 4-neighbour is higher, except +1 behind a plain back wall (the rock visibly intersects the wall).
  3. The cell in front of every door, Porch, Stair_Ext, Awning, Wall_Stall or LeanTo is walkable at the same level, or is a ramp/stair.
  4. Footprint cells become `stiff`.
- **Stiff tiles use `Outer_Sq` / `Inner_Sq`** (plus Edge_A and no D), so cells next to buildings, plazas and ramps stay square. The Saddle always stays rounded.
- **New pieces (rubble STONE, picking up the reworked stone texture):**
  - `SM_VK_Foundation_Drop`: 3 m wide, 1.6 m tall apron. Face at 0.45 m into the low cell (flush with the battered plinth, whose base reaches y = −0.44), covering the 0.30 m bulge.
  - `_Corner`: for Outer_Sq corners.
  - Stack one apron per level of drop.
  - `SM_VK_RetainingWall` / `_Corner` / `_InnerCorner`: ASHLAR with coping, for straight stiff borders not covered by a building.
- **Props and trees:**
  - Placed in a cell's safe interior (inset 0.6 m from any border with a level change or water), where z = level·1.5.
  - Otherwise raycast against the chunk BVH.
  - No trees within 0.9 m of a crossing border.
  - `scatter_trees` is rewritten to respect these zones.
- **Height query** (for pawns in Unity): z = level·1.5 inside cells; a linear lerp on ramp cells; a raycast elsewhere.

## 14. Pathing (P1)

- The navigation graph is the cell grid, built from Cell data.
- A move is allowed only between cells of the same level, or along an R↔H ramp link.
- Diagonal moves require both orthogonal cells to be walkable at the same level. This makes the Saddle gap irrelevant.
- Move costs: Cobble 0.8, Dirt 0.9, Grass 1.0, Rock 1.1, Sand 1.2, Stair 1.3, Ramp 1.5.
- `wear` increases by 1 per pawn step and decays slowly, which drives the Dirt channel. Desire paths emerge on their own.
- Terraforming a cell rebuilds its 4 render tiles, which touch 1–4 chunks.

## 15. Chunk assembly, Blender and Unity

**Blender: `tk_build_chunk(G, ci, cj, displace=True, lod=0)`.** It builds numpy arrays; it does not instance objects.
1. Cache each piece: `co`, per-loop `vertex_index`, polygon sizes, per-loop normals (`me.corner_normals`), `TCol`, material indices.
2. For each record from `tk_tiles()` inside the 16×16 chunk: exact integer rotation, then translate.
3. Apply D and the Jacobian normals.
4. Create the mesh with `me.from_pydata(verts, [], faces)` (loop order is preserved). Then:
   - `foreach_set` into the `TCol` FLOAT_COLOR corner attribute;
   - `me.normals_split_custom_set(loop_normals)`.
5. Build water quads as a separate mesh.
6. Objects: `VKT_Chunk_<ci>_<cj>` and `VKT_Water_<ci>_<cj>`, located at MAP_ORIGIN, in collection `VK_Terrain`.
7. Do not weld.

Other functions:
- `tk_ground_ctl(G)` writes `T_VK_GroundCtl`.
- `tk_scatter(G)` places sockets and seam rocks.

**Unity.**
- **FBX export:**
  - one `VK_TerrainTiles.fbx` containing all `SM_VKT_*` pieces;
  - `colors_type='LINEAR'`;
  - Apply Transform.
- **Import settings:**
  - Mesh Compression **Off** (quantisation cracks seams);
  - Read/Write on;
  - Normals: **Import**;
  - Tangents: None;
  - Bake Axis Conversion on, scale 1.
- **Axis test (mandatory):** `SM_VKT_AxisTest`, with an "N" arrow toward Blender +Y and an "E" arrow toward +X. It must read N = +Z and E = +X at identity rotation. Only then is `yaw = −90·r` valid.
- A `TerrainTileSet` ScriptableObject holds the `MS` and `SHORE` tables and the meshes indexed by [set][case][variant][lod].
- A Burst job does the same work as the Blender assembler. Inside the noise, `pB = (u.x, u.z, u.y)`.
- Per chunk: 32-bit indices, 2 submeshes (Terrain, Ashlar), a water mesh, and a MeshCollider from LOD1.
- Optional NavMesh bake: max slope 35°, step height 0.3 m.

## 16. Budgets and variants

| Piece | LOD0 tris | LOD1 | Variants |
|---|---|---|---|
| Full | 72 | 24 (fan) | 1 (rotation from hash) |
| Edge | ≤ 290 (C ≤ 380 with boulders) | about 150 | A, B, C, mirrored B′, C′ |
| Outer / Inner | ≤ 230 / ≤ 270 | about 120 / 140 | A, B, A′, B′, Sq |
| Saddle | ≤ 360 | about 190 | A (r or r+2) |
| Shore Edge / Outer / Inner / Saddle / Bed | 260 / 200 / 230 / 330 / 24 | about 50 % | Edge A, B; others A |
| Ramp half / Mid | ≤ 250 / ≤ 200 | same | — |
| Stair half / Mid | ≤ 350 / ≤ 300 | same | — |
| **Hard cap per tile mesh** | **400** | | |

- Variant pick: `hash32(I,J,ℓ) % n`. Stiff tiles use A or Sq.
- Chunk (16×16 tiles, 70 % Full): about 40k tris. About 9 visible chunks gives about 360k tris; switch to LOD1 beyond 60 m.

## 17. Automated verification (`vk_terrain_verify.py`, runs in Blender)

| Test | Method | Pass when |
|---|---|---|
| **T1 Edge signature** | For every mesh × LOD × rotation r ∈ 0..3 and each side: gather side loops, convert to (d, z) from the high/land corner, and compare to the table for that side's type (count, position, per-face-side normals and TCol, material index). | Positions **bit-exact** after Q-quantisation; normals ≤ 0.1°; TCol ≤ 1e-4 |
| **T2 Coverage and logic** | Enumerate all level quadruples in {0..3}⁴, all 16 water masks, and all valid ramp configurations. `tk_tiles` must emit existing meshes, and each emitted layer's rotated side types must equal the types derived from the corner data. | 0 failures |
| **T3 Random assembly** | 200 grids of 12×12 cells: 40 % smoothed fbm levels 0–4, 30 % noise, 30 % worst cases (checkerboards, 1-cell mesas and pits, 4-level jumps, water at local minima, every valid ramp). For every adjacent tile pair and every layer both emit, KD-match side vertices. For a layer only one emits, the side must be FLAT or EMPTY. Run with D off and with D on. | 0 unmatched (tolerance 0 with D off, 1e-5 with D on); normals ≤ 0.5°; TCol equal |
| **T4 Holes** | Void plane at z = −10. BVH of chunk plus water. Vertical rays on a 0.25 m lattice, plus oblique rays at azimuths 45/135/225/315° and elevations 35°/60°. | No void hits, no back-face hits (`dot(ray, n) > 0`), and every vertical hit has z within [lo·1.5 − 1.25, hi·1.5 + 0.01] |
| **T5 Open edges** | After `remove_doubles(bm, verts=bm.verts, dist=1e-4)`, classify every boundary edge. | Only: chunk perimeter, skirt bottom (ℓ·1.5 − 2.70), buried FLAT sides, ramp foot, water quad |
| **T6 Jacobian** | Minimum of det J_xy over all vertices, with D on. | > 0.3 |
| **T7 Determinism** | Build twice; compare SHA1 of positions, normals, TCol and indices. | Identical |
| **T8 Fuzz** | 10k random edits, then validate, then rebuild the affected chunks, then run T3 on them. | 0 failures |
| **T9 Unity parity** (EditMode) | T1 on the imported meshes, and the chunk vertices compared to a Blender dump for a test grid. | ≤ 1e-5 |

**On failure:**
- Write a JSON report: `{trial, I, J, ℓ, side, case, r, var, max_dev, grid}`.
- Rebuild the failing grid in `VK_TerrainDebug`, with red spheres on the offending vertices.
- Render a top-down orthographic view with `M_VKT_Debug`: a 1.5 m checker, red 3 m grid lines, and TCol shown as RGB.

**Visual checks, rendered for every phase:**
- **Case board:** all 16 masks, plus the Sq variants, shore and ramps. Top-down and at 45°, with the checker material and with `M_VK_Terrain`.
- **Raking-light render:** sun at 10° elevation. No shading seams at tile borders.
- **Repetition check:** a straight 10-cell cliff, which must show no visible 3 m period.

## 18. Build order (highest value first)

| Phase | Deliverables | Accept when |
|---|---|---|
| **1 Core cliff** | constants, `hash32`, P_CLIFF / FLAT, MS table, Cell arrays plus validation, `tk_tiles`; Full, Edge_A, Outer_A, Inner_A, Saddle_A; `tk_finish`; numpy chunk builder; debug material; T1–T5 and T7 (D off) | T1 exact; T3: 0 mismatches over 200 grids; T4: 0 holes; clean case board; a 16×16 chunk builds in under 3 s |
| **2 Look** | `gen_grass`, `gen_cliff`, `gen_terrain_macro`; `terrain_material` (grass, cliff, moss, AO, rim); D with stiff and Jacobian normals; `SM_VKT_LipGrass`, sockets, seam rocks; demo hill | T3/T4 pass with D on; T6 passes; raking-light render has no seams; aerial render shows no 3 m blockiness |
| **3 Ramps and stairs** | RAMP/STAIR profiles, `Ramp_*` and `Stair_*`, ramp validation and detection, pathing graph export plus overlay render | tests include ramps; a pawn path overlay crosses 3 levels |
| **4 Village on terrain** | control map plus `gen_dirt`, `gen_cobble` (after the stone rework), `gen_sand`, and the splat shader; `place()` oz; snap formulas and footprint rules; Outer_Sq/Inner_Sq; Foundation_Drop(+Corner); RetainingWall set; **new `build_town_terrain()`** on the grid; `road_strip` and the ground plane retired | nothing floats (every building base is at footprint z; every prop is within 2 cm of the raycast); roads and plaza come from the painted cells; aerial render |
| **5 Water** | P_SHORE, Shore set, Bed, WaterQuad, reeds; `SM_VK_Bridge_Plank` (spans 1 water cell), `SM_VK_Dock` (on a shore Edge) | tests with water; river demo render |
| **6 Variety and engine** | Edge_B/C, Outer_B, Inner_B, mirrored variants, LOD1, FBX export, axis test, C# tables and Burst assembler | T9 parity; repetition check passes |
| **7 Extras** | Hillside house (back row +2 levels = H1: the upper back wall uses `SM_VK_Wall_Timber_Door` onto the upper terrace, the ground-floor back wall uses new `SM_VK_Wall_Stone_Retain`); `SM_VK_CliffRail` (fence 0.45 m inside the lip); waterfall prop; waterwheel; map-rim skirt; soft grassy "Bank" profile (same row count as P_CLIFF, blended along the contour) | — |

**Demo map** (Phase 2 for the landform, Phase 4 for the village, Phase 5 for the river): 32×24 cells at MAP_ORIGIN.
- River of water cells at level 0 along the south, with shore.
- Meadow and farms at level 1.
- Village plateau at level 2: 6×4-cell cobble plaza; a 2-cell dirt main road entering by a 2-wide earth ramp (5.4 m) from the meadow.
- Chapel hill at level 4, reached by two stone stairs.
- Forest ridge at levels 3–6 in the north, with Rock ground on the summits.

## 19. Open questions for the user

1. **Tier height:** 1.5 m (recommended) or 3.0 m. All profile z values scale linearly, but ramps would then need 2 cells.
2. **Diagonal squeeze:** should pawns be allowed to squeeze diagonally past saddles? The default is no.
3. **Map edge:** clamp, or a diorama skirt?
4. **Uphill rule:** is the "+1 level behind a plain wall" rule acceptable, or should any uphill neighbour require a RetainingWall?

**Dependency on the stone rework:** `T_VK_Cobble`, `Foundation_Drop` and `RetainingWall` should take their palette from the reworked `T_VK_Stone`. `T_VK_Cliff` must stay visibly different: layered natural rock, not rubble masonry.

**Reference code:** `C:/Users/danie/AppData/Roaming/Claude/scratch-workspaces/ec03f06b-60f5-4d5d-94a9-dff3a56c5f56/f8ddc2b6-f8a4-41c6-98db-14b97d4348ea/scratch-2026-09-23-d49817/code/`, in `vk_helpers.py` (`place()` at line 404, `Kit.finish` at line 125, `plinth()` at line 167, `build_town` at line 2936), `vk_nature.py` (`nk_finish`, `boulder`), `vk_tex.py`, `vk_texgen.py` and `vk_mat.py`.