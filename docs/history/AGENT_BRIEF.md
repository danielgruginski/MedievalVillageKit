# Village Kit workshop: brief for building agents

You are one of several agents extending a procedural, hand-painted, **World-of-Warcraft-style** medieval village kit. The kit is for a **colony-sim game in Unity**. Everything is built in a live **Blender 4.4** instance via the Blender MCP tool `mcp__blender__execute_blender_code`. Load it first with `ToolSearch` using `select:mcp__blender__execute_blender_code`.

Other agents work in the **same Blender instance at the same time**. Blender runs one call at a time, so calls are serialized. The main engineer is building the terrain kit in parallel.

Paths below are relative to `ROOT = C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817`.

## 1. Hard rules (violating these can destroy other people's work)

1. **Never modify shared Blender texts.** These are:
   - `vk_helpers`, `vk_mat`, `vk_tex`, `vk_texgen`, `vk_tex2`, `vk_nature`, `vk_leafgen`, `ws_common`, `mc_helpers`, `wk_helpers`, `tree_*`;
   - any other agent's `ws_*` text.

   You own exactly one text: `ws_<agent>`.
2. **Never call these functions:**
   - `full_rebuild()`, `apply_pbr_all()`, `build_town()`;
   - any save or save-as, and any `bpy.ops.wm.*`;
   - any texture generator (`gen_*`), `write_map` or `write_set`.
3. **Never touch what you did not create.** Do not delete, rename or modify objects, meshes, materials, images, collections or scenes you didn't create. Do not touch the `VillageKit` scene or other `WS_*` scenes. Do not change the world or `VK_Sun`.
4. **Your sandbox:**
   - scene `WS_<agent>`;
   - collections `WS_<agent>_Pieces` (the piece masters) and `WS_<agent>_Assembly` (demo buildings and instances);
   - text `ws_<agent>`.

   Create them only through `ws_scene()` / `ws_build()`.
5. **Operators.** Use no `bpy.ops` except rendering through `ws_shot()`. Context operators break other agents' calls.
6. **Keep calls short and safe.**
   - Each call should take under about 20 s.
   - No unbounded loops. Keep meshes reasonable.
   - If a call fails with a communication error, wait a moment and retry. Another agent may have been rendering.
7. **New materials are strongly discouraged.** Use the 52 kit material slots and the `VARIANT_MATS` styles. If one is truly unavoidable:
   - name it `M_WS_<agent>_*`;
   - build it with `tex_mat(name, None, rough, flat=(r,g,b))`;
   - report it.

   A piece's faces may only use slot indices 0–51. `finish()` appends all 52 kit materials, so extra materials cannot be slots. Recolour through `VARIANT_MATS` slots instead.
8. **Piece names.**
   - Every piece is `SM_VK_<Name>` and must be **new**. `ws_build` refuses existing names.
   - Use only the names assigned in your task, unless you really need an extra helper piece. If so, pick a distinctive name.
9. **Module-level names.**
   - Every function or global you define is prefixed with your **agent prefix**, for example `hum_`.
   - The exceptions are builder functions, named `build_<thing>(...)`, and the list `WS_SPECS`.
   - **Never redefine or monkey-patch** an existing vk_helpers function or global (`HALF`, `RIDGE`, `TILE`, `box`, and so on). All modules are later executed into one namespace.
   - If you need a variant of an existing function, copy it under your prefix.
   - Temporary global overrides, like a roof-family switch, must be restored in `try/finally`.

## 2. Getting started (copy this pattern)

```python
# in every execute_blender_code call:
import bpy
exec(bpy.data.texts["ws_common"].as_string())     # ws_ns, ws_scene, ws_build, ws_grid, ws_shot, ws_stats, ws_clear_assembly
```

**Author the module locally.** Write it at `ROOT\code\ws_<agent>.py` with the Write and Edit tools; the local file is the source of truth. Push it into Blender each time:

```python
src=open(r"<ROOT>\code\ws_<agent>.py",encoding="utf8").read()
t=bpy.data.texts.get("ws_<agent>") or bpy.data.texts.new("ws_<agent>"); t.clear(); t.write(src)
```

**Module shape.** Your module is executed **after** vk_helpers, in the same namespace, so every kit function and constant is available:

```python
def hum_wall_wattle(k):  ...                      # piece functions take a Kit
def build_hovel(coll, origin, seed=0, style=None): ...   # builders place instances with place_v()
WS_SPECS=[("SM_VK_Wall_Wattle", hum_wall_wattle, {}),     # (name, fn, finish kwargs)
          ("SM_VK_Corner_Wattle", hum_corner_wattle, dict(wobble=False, grime=True))]
EXTRA_SPECS += WS_SPECS                                    # registers them with the kit (keep this line last)
```

**Build and look.**

```python
exec(bpy.data.texts["ws_common"].as_string())
g=ws_ns("<agent>")                    # kit + your module
objs=ws_build("<agent>", g=g)         # builds every WS_SPECS piece into WS_<agent>_Pieces (visible, at origin)
ws_grid(objs, cols=4, sx=7, sy=7)     # lay them out for a catalog shot
print(ws_stats(objs))                 # tris, bbox, materials used
p=ws_shot("<agent>","catalog_v1",(14,-22,12),(10,-6,1.5),lens=35)   # renders to ROOT\renders2\<agent>\catalog_v1.png
```

Then look at the render with the **Read** tool on that PNG path.

**Assemblies (demo buildings).**
- Call builders with `coll = the WS_<agent>_Assembly collection`, obtained from `sc,coll,asm=ws_scene("<agent>")`, and an origin like `(40, 0, 0)` (`origin = (ox, oy, rot_z_radians)`).
- `place_v(coll, piece, x, y, z, rot_deg, origin, style)` creates an instance sharing the master's mesh. The style can recolour slots, for example `{"plaster":"Daub","roof":"Thatch"}`.
- Your own new pieces can be placed as soon as they exist, whether they sit in your Pieces collection or anywhere else.
- Existing kit pieces (hidden masters in VillageKit's `VK_Pieces`) can be placed too.
- `ws_clear_assembly("<agent>")` empties the assembly before a rebuild.

## 3. The kit API (read `ROOT\code\vk_helpers.py` for everything)

### 3.1 Kit class
- `Kit()` is a bmesh builder with UVMap and a `Col` colour layer.
- `k.box(center, size, mi, rot=(rx,ry,rz), bevel=0.04, segs=1, jitter=0.0, seed=0, xform=None, tile=None)` makes a bevelled box. It returns its verts, with UVs box-projected from `TILE[mi]`.
- **STONE rule:**
  - `mi=STONE` with `bevel>0` on a small block automatically becomes `STONE_BLOCK` (jointless dressed stone).
  - Flat STONE panels use `bevel=0`, so the 3 m rubble tile lines up across modules.
- `k.quad(pts, mi, uvs=None)` and `k.project(faces, mi, axes=None, sizes=None, offset=(0,0), tile=None)`.
- `k.finish(name, coll, wobble=True, grime=True, loc=(0,0,0))` is called for you by `ws_build`.
  - The wobble is periodic in x with a 3 m period, so it only suits pieces whose ends sit at x = ±1.5, ±4.5, …
  - Use `wobble=False` for anything else: props, round pieces, roofs.
  - `grime` darkens toward z = 0. Use `grime=False` for pieces not standing on the ground (upper floors, roof items).

### 3.2 Helper functions
- `_cyl(k, center, r1, r2, depth, segs, mi, rot=Matrix)`
- `lathe(k, prof, center, segs, mi, smooth_=False, cap_top=False)`
- `ring(k, c, r_in, r_out, depth, mi, n, axis)`
- `rock(k, c, size, seed, rot_z, tilt, mi, segs)`
- `merge_kit(dst, src, Matrix)`
- `stone_panel(k, x0, x1, z0, z1, y0=-0.25, y1=0.25, mi=None)`
- `plinth()`, `batter()`, `grid_cut()`, `window_frame()`, `shutter()`, `timber_frame()`, `plaster_ground()`
- Roof functions:
  - `roof_slab`, `ridge`, `eave_tabs`, `gable_end`, `roof_mid`, `roof_gable`, `roof_hip`, `roof_L_corner`;
  - thatch: `thatch_slab`, `thatch_eave_roll`, `thatch_rake_roll`, `thatch_ridge_cap`, `roof_thatch_mid`, `roof_thatch_gable_kind`.
- Props: `prop_*`, `barrel()`, `market_stall()`, `arch_ring()`, `arch_cut_panels()`, `arch_soffit()`, `wall_rocks()`, `corner_stone()` and many more.

**Reuse and compose these.** The existing kit is the style reference.

### 3.3 Materials (use the constant names, never numbers)
`STONE PLASTER WOOD ROOF WINDOW IRON PINK YELLOW LEAF GLOW SHUTTER CLOTH_A CLOTH_B APPLE PUMPKIN BREAD HAY PAPER WATER BRONZE STAINED STEEL THATCH PLANKS ASHLAR BURLAP SOIL VOID ROCK CLAY CLOCK FOLIAGE CROPS BARK_OAK BARK_BIRCH BARK_PINE LEAVES MOSS ROCK_MOSSY BARK_MOSSY ENDGRAIN MUSH_RED MUSH_BROWN MUSH_STEM MUSH_GLOW STONE_BLOCK FIELDSTONE WATTLE HIDE PIGSKIN COAL NET`

- **STONE** is coursed rubble (3 m tile).
- **STONE_BLOCK** is jointless dressed stone, for sills, quoins, steps, caps and pop-outs.
- **FIELDSTONE** is rough rural dry-stone (3 m tile).
- **ASHLAR** is cut blocks (3 m tile, 0.5 m courses).
- **WATTLE** is a woven hazel texture (1 m tile).
- **NET** is an alpha-cut net card.
- **HIDE, PIGSKIN and COAL** are flat colours.
- **VOID** is near-black, for openings and holes.
- **GLOW** is emissive: fires, lit windows.

**Recolour styles** (`VARIANT_MATS` / `SLOT`, applied per instance via `place_v` style):

| Slot | Styles |
|---|---|
| plaster | Cream, White, Ochre, Rose, Daub, Sage, Sky |
| shutter | Teal, Red, Green, Blue, Natural |
| roof | Red, Blue, Green, Thatch, Slate, Shingle |
| cloth | Red, Blue, Green, Yellow, Purple, White |
| stone | Rubble, Field, Warm, Cool, Dark |

Only faces using PLASTER, SHUTTER, ROOF, CLOTH_A or STONE are recoloured.

### 3.4 Conventions
- `CELL=3.0`, `H1=3.0` (ground storey), `H2=2.8` (upper storey). Roof constants: `PITCH` 52°, `RIDGE`≈4.19 above the wall top for 6 m deep houses, `EAVE`, `HALF=3`, `GX=2.45`.
- **Wall modules** are 3 m wide, centred on x = 0, with the **outer face toward −Y** (face at y≈−0.25) and the inside toward +Y. The post on the left edge belongs to the module. Walls are placed on cell edges.
- **Corners** sit at the origin with their outer faces toward −X and −Y.
- **Roofs** are one piece per 3 m bay, placed at z = wall top. The house depth is 2 cells (6 m).
- The origin is at the ground, z = 0. The kit is placed on a 3 m grid, with rotations in multiples of 90° (45° only for diagonal pieces).
- **Terrain is coming.** It uses marching-squares tiles, 3 m cells and **1.5 m level steps**; buildings sit on flat plateaus. Every new ground-contact building piece should carry a **hidden skirt**: stone or soil geometry continuing down to z = −0.6 under its footprint edge, so it never floats on slightly uneven ground.
- **Water datum** (for the water set): the bank is at z 0, the water surface at **−0.6**, the bed at **−1.5**, and piles go to **−3.0**.
- **Style:** chunky, exaggerated, readable WoW proportions.
  - Bevel everything.
  - Slight irregularity: sag, tilt and jitter a few cm, seeded, so it stays deterministic.
  - Strong silhouettes that read from the **colony camera** (≈40 m away, 50° pitch).
  - Painted textures carry the detail, so don't model tiny noise.
  - Look at `ROOT\catalog_walls.png`, `catalog_props.png`, `catalog_roofs.png`, `catalog_landmarks.png`, `town_street.png`, `town_aerial.png` and `village_special_buildings.png` to match the look.
- **Budgets:**

  | Kind | Triangles |
  |---|---|
  | Wall module | ≤ 3k |
  | Roof bay | ≤ 3k |
  | Prop | ≤ 2k (small ≤ 800) |
  | Big landmark piece | ≤ 15k |

- **Existing pieces:** `ROOT\code\kit_pieces.txt` lists the names, dimensions and triangle counts. Builders like `build_house_v`, `build_barn`, `build_stable` and `build_chapel` in vk_helpers show how buildings are assembled.
- **Specification:** `ROOT\code\full_judge_buildings.md`. Your task points to the relevant sections.
  - Its material slot numbers are outdated; use the constant names.
  - It mentions `build_block`, `district_style`, sockets, stages and `roof_family` infrastructure that **does not exist yet**. Don't depend on it.
  - Where a piece needs the S roof family (3 m deep, ridge 2.27), implement it in your module with a prefixed context manager that restores `HALF`/`EAVE`/`RIDGE`/`GX` in `finally` (see spec §5.4).
  - Skip sockets. Record the socket positions you would use in your final report instead.

## 4. Working loop (quality matters more than quantity)

1. Read the relevant vk_helpers code and the spec section. Look at 2–3 reference renders.
2. Build a few pieces, then run `ws_build` and look at a catalog shot plus a close-up (`ws_shot`, then Read the PNG).
3. After **every** render, write down 3 concrete problems. Look for:
   - floating or intersecting parts, and gaps at module seams;
   - wrong scale next to a 1.8 m person (a door is ≈2.0–2.2 m);
   - flat, boring silhouettes;
   - z-fighting;
   - textures stretched or tiled wrongly (check UV scale);
   - a style mismatch with the existing kit;
   - pieces not snapping to the 3 m grid.

   Fix them, re-render and re-check. Do at least 3 improvement iterations on your most important pieces.
4. **Seam test.** For wall families, place 3 modules side by side (`.`, `W`, `D`) plus corners and check the joins.
5. **Final renders.**
   - A catalog of all pieces: `catalog_final`.
   - 1–3 hero shots of your assembled demo buildings: `hero_*`. Use a 3/4 view from about 25–35 m, plus one colony-camera view (high, 50° pitch).
   - Render at 1600×900.
6. **Leave everything built.** Keep the pieces in `WS_<agent>_Pieces` and the demos in `WS_<agent>_Assembly`, and make sure `code\ws_<agent>.py` equals the Blender text.

## 5. Final report (your structured output)

Report the following:
- **Module:** the file path and the text name.
- **Pieces:** name, one-line description, finish flags, tris, bbox.
- **Builders:** signature, what each builds, and its footprint in cells.
- **Renders:** paths to the final renders.
- **Integration notes:** dependencies on other agents' pieces, suggested sockets, and known issues or limitations.

Be honest about what isn't finished.
