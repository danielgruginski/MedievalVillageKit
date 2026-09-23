# Stone texture rework: art direction and procedural recipe (T_VK_Stone and its variants)

## 0. Verdict

The idea behind the current texture is right: coursed rubble on the ground floor, timber and plaster above, a 3 m tile that lines up with the module. The execution reads as bread, pillows and sponge rather than stone. Four things cause it:

- The stones are blob shapes with no straight edges.
- A worm-like surface noise covers every stone.
- The joints are near-black and look like empty holes.
- The colouring swaps between two families (beige and grey) at random, and there is no painted light direction.

The rework keeps the tile size, the prefix and the pipeline. It replaces the stone layout, the height profile and the whole paint stack.

---

## 1. What is wrong now

I measured the current `T_VK_Stone_BC/H.png` in pure Python, treating H < 0.25 as mortar:

| Metric | Now | Problem |
|---|---|---|
| Mortar area | **20.1 %** of the tile | Too much void. The stones look like they float. |
| Mortar mean colour | **#2E2720** (46,39,32) | Almost black. It reads as tar or a hole, not lime mortar. |
| Stone mean colour | #8E8372 | Acceptable. |
| Tile mean colour | **#7B7062** | Muddy. From a distance it reads as brown-grey dirt, too close in value to the timber. |
| Stone luminance p5 / p50 / p95 | 101 / 131 / 168 | The spread is wide, but it comes from hue-family swaps and lumps, not from light. |

The problems in detail, by `gen_stone()` term:

1. **Silhouette.** Every stone is a rounded rectangle (`rad=40` px, about 12 cm corners). Its outline is displaced by `en = fbm(fmin=4, fmax=60)*4.5` px of high-frequency wobble, which gives torn-paper or cookie-cutter edges. There are no straight chisel edges, no angles and no chamfered corners, and every stone has the same topology.
2. **Proportions and layout.**
   - There are 6 rigid rows, and each bed joint is a continuous straight line across the whole tile. That reads as a brick or tile wall, not rubble.
   - The `split` rule (35 % of stones) cuts a stone into two half-height stones of the same width. The result is stacked "sausage pairs" with aspect ratios up to 7:1. This is the most artificial element in the texture.
   - There are no packing stones, no jumpers and no size hierarchy.
3. **Surface.** `facets()` = `-|fbm|` produces a network of ridge lines (the white squiggles in `_H`). Every stone gets the same amount of it, and the result reads as sponge, brain or bread crust, which is organic rather than mineral. Add the `mott` and `grain` terms and a stone at game distance becomes grey noise that shimmers under mips.
4. **Profile and normal.** `prof = smooth(gap, gap+46, d)**0.5`: the square root has infinite slope at the edge. That makes a 2–3 px cliff ring in `_N` (the cyan/magenta outline) around a flat plateau, so each stone looks like a cushion or a gummy sweet. The ring is sub-texel by mip 2–3. At colony-camera distance the stones become flat stickers with no volume.
5. **Mortar.** Base colour `(0.26,0.22,0.18)`, then `write_set(ao_in_albedo=0.55)` multiplies in `cavity_ao(floor=0.25)`, which pushes it to near-black. Joint width is 13 px nominal ±9 px of noise, so between 1 and 9 cm, varying randomly.
6. **Colour.** The 7 palette entries fall into two families, beige/tan and neutral grey, assigned at random. The wall looks like patchwork. Highlights and shadows keep the base hue, which is how photo-sourced texture looks, not painted.
7. **Light.** `painted_light` runs on `blur(h,2.5)` and gives a weak, soft form. Its light has a sideways component (L.x = −0.35), but walls face in every direction. The `rim` term adds +0.06 to *all* edges, which makes a halo instead of a top-lit lip. There is no top-to-bottom gradient per stone and no cast shadow into the joints.
8. **Lichen.** It is 50 % sage specks driven by `fbm(fmin=20)`. Up close it reads as mould and from a distance it is invisible.
9. **Usage (visible in the renders):**
   - The same texture goes on modeled single stones: arch voussoirs, sills, steps and the well ring blocks. Mortar lines then cross a single stone ("stone made of stones"). The well in `catalog_props.png` is the worst case.
   - Chimneys 0.8–1.25 m wide show only 1–2 stones.
   - `Kit.box()` gives each box a random UV offset from its hash, so the pattern jumps at the seams between different wall pieces.

---

## 2. Target look (art direction)

- **Shape language:** chunky stones shaped as soft-cornered polygons, with 2–4 flat chiselled planes each. Not pillows, not Voronoi crazy-paving, not bricks.
- **Construction read:** loose courses with a clear horizontal rhythm, head joints that lean, staggered bond, small packing stones in the corner pockets, and one thin "lacing" course of flat slate-like stones.
- **Light (the core of the WoW read):** light comes from above in every stone:
  - a bright, warm, cream-coloured lip on the upper edges;
  - a lit face made of 2–4 value planes;
  - a cool violet underside;
  - joints that are dark because they are in shadow, not because the mortar is black.
- **Colour:** warm grey is dominant. Drift toward cool blue-grey, tan and a little mauve. Shadows go cool and violet, highlights go warm and cream. Chroma stays low, and value does the work.
- **Detail budget:** about 70 % of the interest sits at the edges (rim light, chips, corner pockets, packers) and 30 % on the faces (planes, faint brush strokes, lichen). No photographic noise.
- **Value stack for the kit:** dark timber, then the stone base at mid value (tile mean about **#908879**), then light plaster. This three-value stack is what makes the houses readable from the colony camera.

**Distance check.** At about 35 m, 1080p and a 50° vertical FOV, a wall gets about 33 px/m, so the 3 m tile is about 100 px (mip 3–4, 2–5 cm per texel). Anything under 5 cm disappears. What must survive is:

- the value difference between neighbouring stones (at least 4 %);
- the dark band below each stone (joint + cast shadow + underside ≈ 5–7 cm);
- the bright upper rim.

Everything else is close-up detail.

---

## 3. Recipe: `gen_stone()` v2 (coursed rubble)

### 3.1 Units, resolution, tile
- Keep **tile = 3.0 m** and the prefix `T_VK_Stone`. One tile = one module = one ground floor (H1), which makes the tile edge a bed joint at z = 0 and z = 3.0, exactly under the timber sill beam.
- Work at **S = 2048** (682.7 px/m, 1 cm = 6.8 px). Downsample 2× by box average to **1024** for output: `a.reshape(S/2,2,S/2,2,C).mean((1,3))`. This is tileable-safe and anti-aliases the crisp edges. Compute normals at 2048, average them, then renormalise.
- Do all layout maths **in metres**, with `yu` pointing up: `yu = T*(1 - row/S)`, because array row 0 is the image top, i.e. v = 1. Height is in metres too. `h01 = clip(h_m / depth, 0, 1)` with **depth = 0.06 m**.
- Everything must wrap: use wrapped differences `wrapT(a) = (a + T/2) % T - T/2`, periodic polylines, `fbm` (already tileable), `draw_segments(wrap=True)`, and `np.roll`.

### 3.2 Layout: course partition with function-defined joints

A partition gives exact, straight, controllable joints. Every stone is a cell bounded by two bed joints and two head joints, so a signed distance to the edge can be computed exactly per term.

```
courses: 6 normal H_r ~ U(0.34, 0.54) m  + 1 lacing course U(0.20, 0.24) m at index 3 or 4
         rescale the 6 normal ones so ΣH = 3.0 m   (never put the lacing course at index 0 or 6)
bed joint r: B_r(x) = y_r + periodic piecewise-linear, 5 jittered vertices/tile, amplitude ±0.025 m
             (B_0 amplitude ±0.008 m so the ground and top edges stay clean); B_7 = B_0 + T
head joints per course: widths ~ lognormal(median = 1.45*H_r, σ = 0.30),
             clip to [max(0.28, 0.75 H_r), min(1.20, 2.6 H_r)] m, draw until Σ ≥ T, rescale to T
             lacing course: median = 3.0*H_r
             random course phase x0_r;   tilt t_k ~ U(-0.30, 0.30) (±17°), lacing ±0.15
stagger rule: every head joint ≥ 0.12 m (wrapped) from any head joint of the course below,
             measured on the shared bed; also check course 6 against course 0. Re-draw ≤ 30 tries.
```

- **Result:** about 30–34 stones plus 6–10 packers per 9 m². Typical stone: 0.67 × 0.46 m.
- **Rasterise per course band:** `band = B_r(x) ≤ yu' < B_{r+1}(x)`, with `yu'` wrapped into `[B_0(x), B_0(x)+T)`.
- For each stone k in the band:
  - `dL = wrapT(x − (J_k + t_k(yu − yc_r))) / √(1+t_k²)`;
  - `dR` likewise for the right-hand joint;
  - the pixel belongs to stone k where `dL ≥ 0 & dR ≥ 0`.
- **Optional jumpers:** in 1–2 places per tile, force a stone in course r+1 to use the same head joints as the stone below and merge the two cells into one label (drop the shared bed term).

### 3.3 Stone silhouette (SDF built from the partition terms)

```
dB = yu - B_r(x) - 0.0025 ;  dT = B_{r+1}(x) - yu - 0.0025      # bed joints 0.5 cm wider than head joints
chamfers: each corner p = 0.5, leg c ~ U(0.03, 0.10) m (≤ 0.3·min(w,h)), a,b ~ U(0.6, 1.4)
          e.g. bottom-left: dC = (a·dL + b·dB − c)/√(a²+b²)       # reuses the terms, no new geometry
d = smin_poly(dB, dT, dL, dR, dC..., k_i)                          # k_i ~ U(0.012, 0.035) m per stone
d += 0.002 * fbm(fmin=10, fmax=40)                                 # low-frequency wobble only
g(p) = 0.0085 + 0.0025*fbm(fmin=6, fmax=30)                        # joint half-width → head joints 1.2–2.2 cm
stone = smooth(g-0.0012, g+0.0012, d)
```

`smin_poly(a,b,k)`: `h = clip(0.5+0.5(b−a)/k, 0, 1); b + (a−b)h − k·h(1−h)`, folded over the terms. The varying `k_i` makes some stones crisp and others worn.

- **Bites (silhouette chips).** Place 0–2 per stone, 65 % on the top edge or top corners. Each is an ellipse centred on the edge, 1.5–3.5 cm along the edge by 1–2 cm across it: `d = min(d, ellipse_dist − r)`.
- **Packers.** In 35 % of the chamfer pockets whose leg is ≥ 6 cm, add a small stone:
  - flattened ellipse, radius 0.35 × leg, y scale 0.75;
  - its own label, palette S3 or S6;
  - fully rounded;
  - protrudes 1.5–2 cm.

  Pockets without a packer stay as mortar triangles. These show up at distance as small dark accents.

### 3.4 Height map (metres, then /0.06)

| Component | Formula / value |
|---|---|
| Mortar | `0.004 + 0.004·(meniscus rising within 0.5 cm of stones) + 0.0006·fbm(fmin=120)`, and a slight concave rake |
| Face plane | protrusion `p_i ~ U(0.028, 0.036)` |
| Bevel shoulder | `d' = d − g`; `r_i = clip(0.10·min(w,h), 0.025, 0.06)`; `h += −0.6·r_i·(1 − √(1 − (1 − min(d'/r_i, 1))²))` (quarter circle, **no** √ cliff) |
| Bulge | `+0.010 · smooth(0, 0.85·inr_i, d')^0.7`, with `inr_i ≈ 0.5·min(w_i,h_i) − g` taken from the design values |
| Facets (key feature) | K = 4 planes per stone, direction `θ_k = 90°k + U(−35°, 35°)`, slope `s_k ~ U(0.10, 0.20)` (6–11°), the plane meets face level at `a_k ~ U(0.3, 0.7)` of the way to the edge. `facet = min(0, min_k(s_k·(a_k·R_k − (p−c_i)·u_k)))`. Vectorise with per-label parameter arrays indexed by `lab`, using `wrapT` for `p − c_i`. Blur 0.8 px so the creases stay crisp. Drop at the edge is 1–2.5 cm. |
| Tilt | per-stone gradient ±0.035 m/m |
| Grain | `0.0008·fbm(beta=1.8, fmin=60, fmax=300)` plus sparse pits `−0.002·smooth(2.2, 2.6, fbm(fmin=40))`, faces only |
| Face chips | 1–2 per stone inside the edge zone (d' < 5 cm): `h = min(h, chip_plane)`, sloping 25–35° toward the edge |
| Cracks | 1 per ~7 stones. Start **on an edge** and run inward ≤ 0.6 × width using `crack_segments` with a custom start point, width 2.5 px @2048, `h −= 0.4/0.06·…` (about −0.4 in h01) |

Clamp the stone height to at least mortar + 0.004. Delete the old `facets()`/`-|fbm|` term from this texture completely.

### 3.5 Palette (sRGB, which is what `write_map` stores in byte PNGs)

| ID | Role | Hex | Share |
|---|---|---|---|
| S1 | warm grey (base) | **#9B9384** | 38 % |
| S2 | pale limestone | **#B0A792** | 18 % |
| S3 | cool blue-grey | **#8B8F93** | 18 % |
| S4 | tan sandstone | **#AD967A** | 14 % |
| S5 | mauve accent | **#9E8886** | 7 % |
| S6 | slate (packers and lacing) | **#74767A** | 5 % (60 % of lacing stones) |
| HI | highlight tint | **#F4E9CC** | – |
| SH | shadow tint | **#3E3A4C** | – |
| MO | lime mortar | **#6E6557** | – |
| Lichen | sage / ochre / pale | **#A9B38C / #C8963E / #DAD5BD** | 60/30/10 |
| Moss | deep / mid / tip | **#3A5226 / #5F7F34 / #93AE52** | mossy variant only |

Per stone:
- value × U(0.93, 1.06);
- warm/cool shift `w ~ U(−1, 1)`: `rgb *= (1+0.02w, 1, 1−0.025w)`.

Assignment rules (a blue-noise style re-roll):
- no two touching stones may share S4, S5 or S6;
- touching stones must differ by at least 4 % in value.

This separation of neighbours by value is what keeps stones readable at mip 3.

### 3.6 Paint stack (in order, at 2048)

1. **Local colour:** `pal[lab]·val·warm`.
2. **Facet tint:** with `k* = argmin plane`, `col *= 1 + 0.035·fsign[lab, k*]` (fsign ∈ [−1, 1]). The planes read as painted planes.
3. **Stone gradient:** `vloc = dB/(dB+dT)` follows the tilted beds. `col *= 0.93 + 0.10·vloc`.
4. **Brush strokes:** three pre-made oriented fbm fields (`ax=4`, angles 20°/80°/140°, `fmin=12, fmax=70`), chosen by `lab % 3`: `col *= 1 + 0.025·stroke`.
5. **Form light:** `n_s = normal_from_height(blur(h01,3), depth*2.5, tile)`; `f = painted_light(n_s, L=(−0.12, 0.80, 0.58))`. The light is almost vertical because walls face every direction. `s = f − 0.587` (the flat-face response). Soft posterise with `q = s/0.10; s = lerp(s, (floor(q) + smooth(0.3,0.7,frac(q)))·0.10, 0.5)`. Then:
   - `hi = clip(s/0.35, 0, 1)`: `col = lerp(col·(1+0.28hi), HI, 0.18hi)`
   - `lo = clip(−s/0.45, 0, 1)`: `col = lerp(col·(1−0.32lo), SH, 0.30lo)`
6. **Top rim light (the signature):** `rim = (smooth(g, g+.004, d) − smooth(g+.012, g+.024, d))·smooth(0.20, 0.50, n_s.y)`, then `col = lerp(col·(1+0.10rim), HI, 0.40rim)`. The band is 1.5–2 cm on upper edges only; replace the old all-around `rim`.
7. **Underside band:** the same shape with `smooth(0.15, 0.45, −n_s.y)`, then `col = lerp(col·0.78, SH, 0.25·under)`.
8. **Cast shadow into the joints:** a height-field march, k = 1..20 px:
   - `occ = max(occ, roll(h_m,(k, round(−0.15k))) − h_m − k·px·1.43)`;
   - 1.43 = tan 55°, a deliberately steeper shadow light (the flatter form-light angle would throw ~4 cm shadows), so shadows fill the joint (~2 cm) without eating the rim of the stone below;
   - `sh = blur(smooth(0, 0.004, occ), 1.2)`, then `col = lerp(col·(1−0.45sh), SH, 0.30sh)`.
9. **Mortar:** `MO·(1 + 0.05·fbm(fmin=20, fmax=150))`, +6 % on the lower lip of bed joints. The cast shadow from step 8 then darkens the upper half of each joint. Target values: about **#5C5449** in light and about **#403B42** in shadow. Never below #20.
10. **Chips:** chip faces `lerp(col, desat(col)·1.12, 0.7)` (fresh, lighter stone) with a 1 px SH line on the lower boundary.
11. **Cracks:** `col *= 0.5`, lerp 0.4 toward SH, and a +8 % highlight lip 2 px *below* the crack.
12. **Lichen:** 3–5 colonies per tile. Each is 8–25 dots of radius 0.4–1.2 cm inside a 6–12 cm patch, only where `stone > 0.5 & vloc > 0.4`, at alpha 0.85, +0.001 m height. Total coverage at most 4 % of stone area.
13. **Macro breakup:** `col *= 1 + 0.03·fbm(fmin=1.5, fmax=5)`. Keep it at ±3 % or the 3 m repeat becomes visible along streets.
14. **AO:** `cavity_ao` on the 1024 height with `floor=0.35` and `write_set(..., ao_in_albedo=0.30)`. The explicit shadow already does the heavy lifting; ship the unmultiplied AO map separately.

### 3.7 Roughness and normal
- **Roughness:** `R = 0.84 + 0.03·fsign − 0.06·rim − 0.08·chipface + 0.11·(1−stone) + 0.04·lichen`, clipped to [0.60, 0.97]. For Unity, pack `1 − R` as smoothness in the alpha of the Metallic/Mask map.
- **Normal:** OpenGL Y+ from `normal_from_height` (already correct for Unity and Blender). Set `PBR_SETS["T_VK_Stone"]` depth to 0.06 and change `MAT_MAP` `nstr` from 1.1 to **1.0**. The painted light should stay dominant and the real normal should support it.

### 3.8 Target stats (re-measure with the same method)

| Metric | Target |
|---|---|
| Joint area | 10–14 % |
| Joint mean | ≈ #4A444A–#555048 |
| Stone mean | ≈ #9A9283 |
| Tile mean | ≈ #908879 |
| Stone luminance p5 / p50 / p95 | ≈ 105 / 142 / 185, with p95 pixels on upper rims and p5 on undersides |

---

## 4. Variants: worth making?

| Variant | Worth it? | Use | Differences from v2 |
|---|---|---|---|
| **T_VK_StoneBlock** (mortarless single-stone surface) | **Yes, priority 2** | every modeled stone: voussoirs, sills, steps, quoins, chimney caps, well ring and cap, fountain rim, `stone_panel` pier bases | Tile 1.2 m. Tileable power-Voronoi with 10–14 facet cells, each a plane at 4–9°; crease = exact bisector distance (below), 0.6 px blur. Same palette (S1 70 % blended with S2), per-facet ±4 % value, same paint stack without joints, 1 hairline crack, 1–2 lichen colonies. The random box UV offset then works *in favour* of variety. |
| **T_VK_FieldStone** (random rubble, dry-stone) | **Yes, priority 3** | wells, garden and farm walls (a new dry-stone wall fence type for farm plots), windmill base, barn/stable plinths | Tile 2.0 m. Power diagram: seeds in rows (pitch 0.28–0.40 m, spacing 0.35–0.65 m, jitter ±25 % / ±15 %), anisotropy sy = 1.35, one Lloyd step (wrap-aware centroids via `np.bincount`), 12 % small packer seeds with negative weight. Rounder profile: bevel radius 0.35–0.5 × inradius, facets blended 50 %. **No mortar:** 1.5–4 cm gaps of dark soil #3A3029 with pebbles in 25 % of gaps. Palette shifted toward tan/brown; 30 % "granite" stones get 1–2 px speckle (#5A5652 / #C9C3B6, 3 % coverage), the only place high-frequency speckle is allowed. |
| **T_VK_StoneMossy** (full BC/N/R set with the same layout seed) | **Yes, cheap, priority 4** | old or poor buildings, the bottom band; can plug into a colony-sim "building condition" state | Moss mask = (upward bevels with d' < 3 cm) ∪ bed joints, × `smooth(0.3, 1.2, fbm(fmin=2, fmax=12))` × `(1 − yu/T)^1.5`. Coverage about 15 % in the bottom third and about 3 % at the top. Moss sits 4 mm proud. |
| Separate "cut stone" | **No, retune T_VK_Ashlar instead** | chapel, town hall arcade | Move the paint stack (steps 5–9 and 13–14) into a shared `paint_masonry(col, h, d, lab, g)` and call it from `gen_ashlar`, so all masonry reads as one family. |
| Colour variants of the rubble | **No** | – | Tint per building with the existing vertex colour `Col` or per-instance colour in Unity. Add three presets to `random_style(seed)`: warm (1.04, 1.00, 0.94), cool (0.95, 0.98, 1.03), dark (0.88, 0.88, 0.88). |

**Helper for FieldStone and StoneBlock.** Add `voronoi2()` to `vk_tex.py`. It returns ID1 and the **exact** distance to the cell edge, replacing the curved F2−F1 approximation:

`d = min over b≠a of [(|p−b|² − w_b) − (|p−a|² − w_a)] / (2|b−a|)`

Here `a` is the nearest seed, `w` are the power weights (0 gives a plain Voronoi diagram), and `b` uses the periodic image nearest to `a`. This is a second loop over the seeds, with the same cost as the existing `voronoi()`.

---

## 5. Integration notes (geometry side, small but important)

1. **UV phase:** in `Kit.box()`/`project()`, pass `offset=(0,0)` for STONE and ASHLAR wall panels (vertical faces of boxes ≥ 1.5 m). This makes every module seam continuous (u = ±0.5 lands on the same texel) and puts the bed joint at z = 0 and z = 3.0. Keep random offsets for small boxes.
2. **Corners:** the U axis (`n × Z`) of each face breaks at building corners. Hide it with modeled **quoins** in StoneBlock: alternating 0.50 / 0.30 m long, 0.35–0.45 m tall, protruding 3 cm. They are a signature WoW-house element.
3. **Chimneys and wells:** give these a smaller stone scale with a TILE override of **1.8 m** for STONE, so there are at least 2–3 stones across a 1 m stack. Smaller objects getting smaller masonry is a normal stylisation rule.
4. **Horizontal STONE faces** (sills, wall caps, step treads) should use StoneBlock (`abs(n.z) > 0.7` branch in `project()`). The painted top light means nothing on a horizontal surface.
5. **Optional:** edge-matched alternates. Freeze the stones that cross the band u ∈ [−0.08, 0.08] and re-seed the interior. That gives 2–3 wall textures that still join seamlessly module to module.

---

## 6. Pitfalls

- **Aliasing and shimmer:** keep every important read at least 8 px wide at 1024 (≥ 2.3 cm). Lines of 1–2 px (hairline cracks, lichen dots) are close-up only and must never carry the read.
- **Pillows coming back:** never use `smoothstep^0.5` or any profile with infinite slope, and do not give every stone the same radius.
- **Repetition:** no hero feature. No stone larger than 2.5 × the median area, no crack longer than one stone, and lichen spread evenly. Test: tile the texture 4×1, blur with σ = 20 px (@1024); the luminance range must be under 8 %.
- **Baked light fighting engine light:** keep the painted highlight gain at +30 % or less, or the stones glow on shaded façades. Keep the light near-vertical.
- **Darkening applied twice:** baked AO, the painted shadow, the `finish()` grime vertex colour (0.62 at the ground) and SSAO all multiply. That is why `ao_in_albedo` goes down to 0.30 and the mortar floor is about #40.
- **Colour space:** the hex values are sRGB, matching byte PNGs written through `img.pixels`. If you switch to float images, convert to linear.
- **Pixel radii:** `cavity_ao`/`blur` radii are in pixels. Double them if you run them at 2048.
- **Tileability:** `np.roll` the final BC, N and H by S/2 on both axes and look for seams. Stagger and joint-distance checks must include the course 6 / course 0 wrap and the x wrap.
- **Colour clusters:** random palette draws make blotches. The neighbour re-roll rule is required.

## 7. Acceptance renders
1. Close-up at 2 m (the `town_detail` framing): every stone reads as a volume lit from above, with 2–4 planes, a cream rim and a violet underside, and the mortar reads as recessed material.
2. Street view at 12 m (`town_street`): no patchwork, bed-joint rhythm visible.
3. Colony camera at 40 m, 50° pitch, plus a 128 px/tile mip preview: individual stones still visible as value patches, and the ground floor sits clearly between timber and plaster in value.
4. Well, arch and chimney after the StoneBlock and tile-override changes: no mortar lines across single stones.

**Order of work:** v2 `gen_stone`, UV offset fix, StoneBlock and the reassignment of modeled stones, `paint_masonry` shared with Ashlar, FieldStone plus dry-stone walls, Mossy set.