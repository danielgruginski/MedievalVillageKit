# Survey A: Kit API digest for building `vk_mod_interior`

I read the files listed plus the related docs (HANDOFF, KIT_README, `docs/history/AGENT_BRIEF.md`, `WS_MANIFEST.md`, `PIECES.md`, `vk_tex*.py`, `vk_mod_defence.py` placer, `vk_town_map.py` door helpers, archived script logs). I did not call Blender and did not edit anything. Paths are relative to `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\`.

---

## 0. Runtime model

- **Code runs from Blender texts inside the .blend.** The text name equals the file basename (`src/modules/vk_mod_interior.py` becomes the text `vk_mod_interior`).
  - `tools/kit_sync.py` provides `status()`, `push(names)` (file to text) and `pull(names)` (text to file).
  - Two files with the same basename make it raise an error.
- **Loader** (`src/core/vk_kit.py`):
  ```python
  KIT_MODULES=["vk_mod_humble",...,"vk_mod_defence"]
  def vk_kit_ns(terrain=True,modules=True):
      g={}; exec(bpy.data.texts["vk_helpers"].as_string(),g); g["KIT_MODULE_SPECS"]={}
      for m in KIT_MODULES: exec(bpy.data.texts[m].as_string(),g); g["KIT_MODULE_SPECS"][m]=[n for n,_,_ in g.get("WS_SPECS",[])]
  ```
  - A new module must be appended to `KIT_MODULES`, and `vk_kit` pushed again. Put it last so it can see earlier modules' `hum_*`/`ind_*` helpers in the full namespace.
  - Use `vk_kit_ns(terrain=False)` to skip `vk_nature`/`vk_terrain`/`vk_terrain_demo`.
- **What `vk_helpers` needs to exec:**
  - It needs scene `VillageKit` (`SC=bpy.data.scenes["VillageKit"]`).
  - Mid-file (line 2236) it runs `exec(bpy.data.texts["vk_mat"]...)`.
  - `kit_mats()` indexes `bpy.data.materials["M_VK_Foliage"]` and similar names directly, so it raises KeyError if they are missing.
- **Many functions are defined twice.** A "DETAIL PASS (overrides)" section from line 2247 redefines `tex_mat`, `plinth`, `wall_stone_*`, `corner_stone`, `timber_frame`, `ridge`, `roof_mid`, `chimney`, `cupola`, `_assemble`, and others. **Always read the last definition.**
- **MCP calls:** every call starts with a fresh namespace, calls are serialized across agents, and each should stay under about 20 s.
- **Saving:** save after each completed step. The .blend must never go to git (the `SpriteRig` scene has third-party assets).

## 1. Constants and conventions

```python
CELL=3.0; H1=3.0; H2=2.8; DEPTH=6.0; HC=4.5 (chapel); HB=4.2 (barn); PL=0.75 (plaster plinth); HUM_HW=2.4 (wattle)
PITCH=52deg; KICK=26deg; HALF=3.0; EAVE=4.35; RT=0.3; RIDGE=roof_z(0); GX=2.45; FACE2=-0.40
```

- **Wall modules:**
  - 3 m wide, centred on local x=0, outer face toward −Y, inside toward +Y.
  - The post at the left edge (x=−1.5) belongs to the module; the right edge belongs to the neighbour or corner.
  - Walls are placed on cell edges:
    - front: rot 0 at y=−3
    - back: rot 180 at y=+3
    - left end: rot −90 at x=−L/2
    - right end: rot +90 at x=+L/2
- **Corners** sit at the origin with outer faces toward −X/−Y. Inner corners have their concave quadrant at local +X+Y.
- **Where exterior walls meet the room** (local y of the inner face; useful when matching interior surfaces):

  | Wall | Wall body | Inner face |
  |---|---|---|
  | stone | `stone_panel` y −0.25..0.25 | +0.25 |
  | plaster ground | −0.28..0.25 | +0.25 |
  | timber upper | infill box centre −0.08, depth 0.46 | about +0.15 |
  | wattle | timber face −0.16, daub to +0.12 | about +0.12 |
  | chapel | −0.3..0.3 | +0.3 |

- **Exterior door and window openings** (so an interior door can mirror them):

  | Piece | Opening |
  |---|---|
  | Stone door | round arch, hw 0.68, spring 2.0, top 2.68 |
  | Plaster door | hw 0.62, top 2.3 |
  | Wattle door | hw 0.45, top 2.12 |
  | Chapel door | lancet x ±0.8, spring 2.2 |
  | Stone window | x ±0.55, z 1.05–2.25 |
  | Plaster window | x ±0.55, z 1.1–2.25 |
  | Timber upper window | x ±0.5, z 0.95–2.15 |
  | Wattle window | x ±0.35, z 1.10–1.65 |
  | Chapel lancet window | x ±0.45, sill 1.3, spring 3.1, apex about 3.80 (`lancet_pts(x0,x1,z0,zs,n)` returns `(pts, apex_z)`) |

- **Triangle budgets** (from the agent brief): wall module ≤3k, prop ≤2k (small ≤800), big landmark ≤15k.

## 2. `class Kit` (vk_helpers.py:203)

```python
def __init__(s): s.bm=bmesh.new(); s.uv=s.bm.loops.layers.uv.new("UVMap"); s.cl=s.bm.loops.layers.color.new("Col")
def project(s,faces,mi,axes=None,sizes=None,offset=(0.0,0.0),tile=None)
def box(s,center,size,mi,rot=(0,0,0),bevel=0.04,segs=1,jitter=0.0,seed=0,xform=None,tile=None)  # -> list of verts (with duplicates)
def quad(s,pts,mi,uvs=None)       # -> face; winding = pts order; no uvs -> project([f],mi)
def finish(s,name,coll,wobble=True,grime=True,loc=(0,0,0))  # -> object; frees bm
```

### `project()`: planar UVs in piece-local space, before wobble

```python
t=tile or TILE.get(mi,1.0)
if mi==STONE and abs(n.z)>0.7: f.material_index=STONE_BLOCK; tt=TILE[STONE_BLOCK]   # overrides tile arg!
if mi in (WOOD,SHUTTER) and axes: U=longest axis with |ax·n|<0.8; V=n×U           # grain along long box axis
elif abs(n.z)>0.7: U=X; V=Y
else: U=n×Z (normalized); V=Z
uv=(p·U/tt+offset[0], p·V/tt+offset[1])
```

- Resulting mappings:
  - −Y face: u = −x/t
  - +Y face: u = +x/t
  - +X face: u = −y/t
  - −X face: u = +y/t
  - vertical faces: v = z/t
  - horizontal faces: u = x/t, v = y/t
- **`project()` also sets `f.material_index=mi`.**

### `box()`

- Unit cube, then `M = T(center) @ Rz@Ry@Rx(rot) @ diag(size)`. `xform` is left-multiplied.
- Bevel offset is `min(bevel, min(size)*0.45)`, with `clamp_overlap`.
- `jitter` moves each vertex randomly (seeded).
- A small STONE block (`bevel>0` and (`sorted(size)[1]<0.7` or `min(size)<0.25`)) automatically becomes STONE_BLOCK.
- **UV offset rule** (determines seam continuity):
  ```python
  h=abs(hash((round(c.x,2),round(c.y,2),round(c.z,2))))
  off=(0.0,0.0) if (mi in (STONE,ASHLAR,FIELDSTONE) and bevel==0) else ((h%997)/997.0,(h//997%991)/991.0)
  ```
  - Float hashes are deterministic across sessions.
  - Identical boxes in different pieces get identical offsets.
  - PLASTER, PLANKS and WOOD get a hash offset **even with `bevel=0`**.
- Other helpers:
  - `grid_cut(k, vs, step=0.5)` bisects at every 0.5 m in local x and z so the wobble has vertices to move; `bisect_plane` interpolates the UVs.
  - `stone_panel(k,x0,x1,z0,z1,y0=-0.25,y1=0.25,mi=None)` is a bevel-0 box plus `grid_cut`.

### `finish()` (verbatim essentials)

```python
if wobble:
  for v in bm.verts:
    p=v.co
    v.co.y+=0.035*math.sin(2*math.pi*p.x/CELL+0.9)*math.sin(math.pi*max(0,min(p.z,6))/6)
    v.co.x+=0.02*math.sin(2*math.pi*p.z/2.3+0.4)
bm.normal_update()
for f in bm.faces:
  for l in f.loops:
    z=l.vert.co.z; g=1.0
    if grime: g=0.62+0.38*min(1,max(0,z)/0.9)
    if f.normal.z<-0.6: g*=0.72          # applies even with grime=False
    l[s.cl]=(g,g*0.98,g*0.95,1)          # OVERWRITES any Col the builder wrote
me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=p.material_index in (APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF) or (p.material_index==GOODS and p.use_smooth)
old=bpy.data.objects.get(name); if old: bpy.data.objects.remove(old)     # deletes a same-named master!
o=bpy.data.objects.new(name,me); coll.objects.link(o); o.location=loc
for m in kit_mats(): me.materials.append(m)     # all 55 slots, fixed order
o["kit"]="VillageHouse"; o["cell_m"]=CELL
```

- `full_rebuild` and `rebuild` then re-set smoothing to `(HAY,APPLE,PUMPKIN,BREAD,CLOTH_A,CLOTH_B,LEAF,BURLAP,FOLIAGE,CROPS)` plus flagged GOODS faces. **Smoothing depends only on the material index**, so `lathe(smooth_=True)` and `f.smooth` are discarded, except on GOODS. Everything else is flat-shaded (that is the chunky look).
- No custom normals are set.
- Spec kwargs: `{}` means wobble and grime both on (exterior walls). Corners use wobble False; props use `ng=dict(wobble=False,grime=True)` or `nw=dict(wobble=False,grime=False)`.
- `merge_kit(dst,src,M)` converts src to a temporary mesh, applies `M`, merges it into dst, and **frees src.bm**. The sub-kit's UVs are kept as they were before the transform, so grain follows the sub-part.

## 3. Materials

**Slot order** (`kit_mats()`, vk_helpers.py:47; never reorder):

```
STONE,PLASTER,WOOD,ROOF,WINDOW,IRON,PINK,YELLOW,LEAF,GLOW,SHUTTER,CLOTH_A,CLOTH_B,APPLE,PUMPKIN,BREAD,HAY,PAPER,WATER,BRONZE,
STAINED,STEEL,THATCH,PLANKS,ASHLAR,BURLAP,SOIL,VOID,ROCK,CLAY,CLOCK,FOLIAGE,CROPS,BARK_OAK,BARK_BIRCH,BARK_PINE,LEAVES,MOSS,
ROCK_MOSSY,BARK_MOSSY,ENDGRAIN,MUSH_RED,MUSH_BROWN,MUSH_STEM,MUSH_GLOW,STONE_BLOCK,FIELDSTONE,WATTLE,HIDE,PIGSKIN,COAL,NET,
GOODS,DRESS,HEWN = range(55)
```

- **Slot counts in the docs are stale.** KIT_README says 53, the agent brief says 52, and PIECES.md shows 52. The code has 55.

**`TILE` (metres per UV unit, keyed by index; missing means 1.0):**

| Slot | Tile | Slot | Tile |
|---|---|---|---|
| STONE | 3.0 | STONE_BLOCK | 1.2 |
| ASHLAR | 3.0 | FIELDSTONE | 3.0 |
| PLASTER | 2.2 | WOOD, SHUTTER | 1.6 |
| PLANKS | 2.0 | ROOF, THATCH | 3.0 |
| WINDOW | 1.0 | IRON, BRONZE, STEEL | 0.5 |
| CLOTH_A, CLOTH_B | 0.5 | HAY | 1.2 |
| PAPER | 0.3 | BURLAP | 0.8 |
| SOIL | 1.0 | ROCK, CLAY | 1.5 |
| WATTLE | 1.0 | ENDGRAIN | 0.6 |
| HEWN | 1.2 | DRESS | missing, so 1.0 (its texture is STONE_BLOCK's) |

**How materials are built:**

- `tex_mat(name,img,rough,flat,emit,alpha_clip,tint)` returns an existing material by name. For a new one, it builds a PBR material via `pbr_material` when image `<img>_BC` exists, otherwise a legacy flat colour × `Col`.
- `pbr_material(mat,prefix,tint,nstr,metallic,rough_mul,emission,flat,paint,spec,metal_map,hsv,jitter,wear)` builds `_BC × (tint/flat/paint) × Col` into Base Color, `_R × rough_mul` into Roughness, and `_N` as a normal map.
- Every kit material multiplies albedo by the vertex colour `Col`.
- `MAT_MAP` plus `apply_pbr_all()` rebuild the PBR node trees.
- `GLOW` is a legacy emissive flat (emission 4.0). `VOID` is near-black (0.015).

**Adding a slot (a core edit; the workshop brief forbids it for parallel agents):**

1. Append a `tex_mat(...)` at the end of `kit_mats()`.
2. Extend the tuple unpack and `range(55→56)`.
3. Add a `TILE` entry, and a `MAT_MAP` entry if it is PBR.
4. Generate the texture with `write_set(prefix, albedo, height, rough, depth_m, tile_m)` from `vk_tex` (writes `assets/textures/<name>.png` and packs it).

`full_rebuild` appends missing slots to existing masters and VAR meshes. DRESS and HEWN were added this way. No existing module creates materials.

**Relevant generator tiles:**
- `gen_plaster` was authored at tile 1.5 but is projected at 2.2.
- `gen_planks` is 2.0, `gen_wood` 1.6, `gen_stoneblock` 1.2, `gen_ashlar` 2.5 (projected at 3.0).
- `vk_tex2`: `gen_stone` T=3.0, `gen_fieldstone` 3.0, `gen_wattle` 1.0.
- All are FFT-tileable, so any tile size works; only the offsets at seams matter.

**Goods atlas:** `goods_map(k, verts_or_faces, cell, axis, ref, c, plane, caps)` with cells `GOODS_CELLS` (cabbage…pomace). `kit_fish(k, M, L, cell, ref)`.

## 4. Registration, rebuild, instancing

**Module shape** (template: `vk_mod_humble.py`):
- Every helper and global is prefixed (`hum_*`, `HUM_*`); builders are `build_*`.
- It ends with:
  ```python
  WS_SPECS=[("SM_VK_Name", fn_taking_Kit, finish_kwargs), ...]
  EXTRA_SPECS += WS_SPECS      # keep last
  ```
- Refer to other modules' pieces through a fallback: `hum_pick(name, fallback)`.
- No module uses an `int_` prefix yet; it is free.

**`all_specs()`** is the core list plus `[(n_,_late(f_),kw_) for ... in EXTRA_SPECS]`:
```python
def _late(fn):
    nm=getattr(fn,"__name__","")
    if nm and nm not in ("<lambda>","fn") and nm in globals(): return globals()[nm]
```
- A named builder is looked up again by name at build time, so a later module defining the same function name silently replaces it.
- Duplicate piece names: the last spec wins. There is a live case: `SM_VK_Prop_Bellows` is registered by both core `smith_bellows` and industry `ind_bellows`.

**`full_rebuild(names=None)`** is the only safe way to rebuild:
1. For each selected spec: `Kit()`, `fn(k)`, project faces whose UVs are all zero, `finish("__tmp__", VK_Pieces, **kw)`, re-set smoothing.
2. If the master exists, copy geometry and materials into the same mesh datablock (instances update). Otherwise rename tmp to the piece name and hide it (a new master in `VK_Pieces`).
3. Refresh `VAR_*` meshes used by objects named `*_inst*`, keeping their overrides only in `SLOT` indices.
- **It does not copy custom properties from tmp to an existing master.**
- Pass `names` (a set); rebuilding all ~417 pieces is slow.
- `rebuild(n,fn)` and `rebuild_all()` are legacy. They call `finish(n)` directly, which deletes the master object and leaves its instances on the old mesh. Do not use them.

**Placing instances:**
```python
place(coll,piece,x,y,z,rot_deg,origin)      # origin=(ox,oy,rz_RADIANS); rot in DEGREES; z absolute; name piece+"_inst"
place_v(coll,piece,x,y,z,rot_deg,origin,style)   # style keys filtered by SLOT -> o.data=variant_mesh(piece,st)
_sub_origin(origin,lx,ly,rdeg) ; _new_objs(coll,fn)   # nest builders / capture created objects
```
- The map finds instances with `base_name(o)=o.name.split("_inst")[0]` and `is_door(o)="_Door" in o.name and not SM_VK_Prop*`.

**Variants:**
- `SLOT={"plaster":PLASTER,"shutter":SHUTTER,"roof":ROOF,"cloth":CLOTH_A,"stone":STONE,"window":WINDOW}`.
- Only those slots are recoloured. CLOTH_B is not, and neither are STONE faces auto-switched to STONE_BLOCK.
- Styles:
  - plaster: Cream, White, Ochre, Rose, Daub, Sage, Sky
  - shutter: Teal, Red, Green, Blue, Natural, plus the `*Worn` versions
  - roof: Red, Blue, Green, Thatch, Slate, Shingle
  - cloth: Red, Blue, Green, Yellow, Purple, White (flat colours)
  - stone: Rubble, Field, Warm, Cool, Dark
  - window: Lit (warm night emission)
- `variant_mesh` caches `"VAR_"+str(abs(hash(key)))`, where the key contains strings. String hashing is probably salted per Blender session, so after a restart new VAR copies get made; `full_rebuild` refreshes them through `*_inst` objects. Orphans are cleaned only by legacy `rebuild_all`.

**Custom properties for Unity:**
- These live on **instances** and are set in builders. Pattern from `vk_mod_defence.def_placer`:
  ```python
  def P(n,x,y,z=0.0,r=0.0,st=None,**props):
      o=place_v(coll,n,x,y,z,r,origin,base if st is None else st)
      for k_,v_ in props.items(): o[k_]=v_
  ```
- Precedents: `hinge_axis="local Z"`, `slide_axis="local Z"`, `travel=float`, `spin_axis="local X"/"local Y"`, `rpm=float`.
- Masters only carry `kit`/`cell_m` from `finish`. Props on master objects do not reach instances (separate objects sharing a mesh).
- Door and stair triggers (target scene or floor) therefore belong on instances placed by the interior-scene builders.
- **Light precedent:** `build_smithy` creates a POINT light (`energy=450`, colour (1,0.45,0.15), `shadow_soft_size=0.4`) in the builder's collection.

## 5. Workshop scenes (`src/workshop/ws_common.py`)

- **`ws_ns(agent)`** execs `vk_helpers` plus the text `ws_<agent>` only. **Other modules are not loaded**, so their `hum_*`/`ind_*` helpers are missing unless copied under your prefix. Their pieces can still be placed by name.
- **`ws_scene(agent)`** creates `WS_<agent>`:
  - copies world, engine, eevee properties, view transform, look and exposure at creation only;
  - links **`VK_Sun` only (not `VK_Fill`)**;
  - adds a 120×120 m ground plane at **z=0** with `VK_Ground`'s material;
  - creates collections `WS_<agent>_Pieces` and `WS_<agent>_Assembly`.
- **`ws_build(agent,names=None,g=None,row_spacing=None)`:**
  - asserts the `SM_VK_` prefix;
  - raises if the name exists outside your Pieces collection;
  - builds, projects, finishes, and updates in place (copying tmp custom props to the base);
  - masters stay visible in `WS_<agent>_Pieces`; a later `full_rebuild` updates them in place but does not move them to `VK_Pieces`;
  - its smoothing list **omits GOODS**, so goods look flat in the workshop but smooth after `full_rebuild`.
- Other helpers:
  - `ws_grid(objs,cols,sx,sy,origin)`
  - `ws_clear_assembly(agent)`
  - `ws_shot(agent,name,loc,target,lens=35,res=(1280,720),samples=32)` renders to `renders/modules/<agent>/<name>.png`; it leaves the samples setting and camera `WS_<agent>_Cam` on the scene.
  - `ws_stats(objs)` returns tris, bbox, zmin and the material indices used.
- Agent rules (brief): own only `ws_<agent>` and your WS scene; no `bpy.ops` except rendering; never call `full_rebuild`, `apply_pbr_all`, `gen_*` or save.

## 6. Rendering

- **`shot(name, loc, target, lens=35, res=(1280,720), scene="VillageKit", samples=None, outdir=None)`** (`vk_render`):
  - perspective camera `VK_CamTmp` (`to_track_quat('-Z','Y')`), `clip_end` 3000;
  - renders to `renders/wip/<name>.png`, restores camera, resolution and filepath, returns the path;
  - no orthographic option (set `cam.data.type` yourself and restore it; the camera is shared).
- **Lights** (archived logs):
  - `VK_Sun`: SUN 3.2, direction (0.34, 0.71, −0.61). Light comes from the SW at about 38° elevation.
  - `VK_Fill`: SUN 1.5, direction (−0.61, −0.50, −0.61), shadowless.
  - Neither is created by code in `src/`; both exist only in the .blend.
- **View transform does not match the brief.** The brief says Standard, but the logs (the valley review) show **AgX, "Medium High Contrast", exposure −0.2**. `render_showcase` converts the PNG to JPEG with Standard only to avoid applying the transform twice. Check it read-only before matching the look.
- `tools/render_showcase.py` `SHOWCASE` holds the README cameras.

## 7. Helpers worth reusing (signatures)

```
_cyl(k,center,r1,r2,depth,segs,mi,rot=Matrix)   lathe(k,prof[(r,z)],center,segs,mi,smooth_,cap_top)
ring(k,c,r_in,r_out,depth,mi,n=28,axis="Y")     _ico(k,c,r,mi,scale,sub,jit,seed)
rock(k,c,size,seed,rot_z=0,tilt=0.12,mi=STONE_BLOCK,segs=2)   barrel(k,x,y,z,r,h,lying)
card(k,center,right,up,w,h,cell,flip,bend)      _rot_vs(vs,c,ang,axis) ; _mat(vs,mi,smooth)
window_frame(k,x0,x1,z0,z1,depth_y,sill,shutters,face)   lancet_pts / lancet_surround(k,pts,y,off,t,d,mi,jamb_h)
hum_cut(k,vs,xs,zs)  hum_rod(k,a,b,r1,r2,segs,mi)  hum_log(k,c,r,L,axis)  hum_sq(...)  hum_daub(...)  (full ns only)
```

**Existing props usable indoors** (size in m, x × y × z):

| Piece | Size / note |
|---|---|
| `Prop_Table` | 2.0×0.95×1.09, with tankards and bread built in |
| `Prop_Stool` | 0.48×0.50×0.55 |
| `Prop_Bench` | 1.8×0.48×1.0, has a back |
| `Prop_BarrelStack`, `Prop_AleCask`, `Prop_Crates`, `Prop_Sacks`, `Pile_Sacks_1-3` | |
| `Prop_Anvil` | |
| `Prop_Bellows` | industry version wins |
| `Prop_QuenchTub` | |
| `Prop_ToolWall` | 1.8×0.14×1.0, grime off |
| `Prop_Forge` | 2.47×1.2×2.8 |
| `Prop_CoalPile`, `Prop_Grindstone`, `Prop_WeaponRack` | |
| `Prop_Loom` | 1.8×2.11×1.83, cloth style |
| `Prop_SpinningWheel` | |
| `Prop_Cauldron`, `Prop_HerbBundles`, `Prop_DryingRack_Herbs` | |
| `Prop_Bedroll` | cloth style |
| `Prop_ShopGoods_Candles`, `Prop_ShopGoods_Tools` | |
| `Prop_LadderLean` | |
| `Ceiling_Cell` | 2.99×3.0×0.28 |
| `Prop_Lantern` | origin at the wall bracket |

All were sized for the 40 m colony camera.

## 8. Gotchas for 1.5 m interior pieces (with numbers)

1. **The wobble does not tile at 1.5 m.** With f(x)=sin(2πx/3+0.9) and S(z)=sin(π·clamp(z,0,6)/6):
   - x=±1.5 gives −0.7833, so dy=−0.0274·S (3 m pieces match each other).
   - x=+0.75 gives +0.6216 and x=−0.75 gives −0.6216, so dy=±0.0218·S.
   - Two 1.5 m pieces side by side step **4.35 cm·S** (S=1 at z=3; S=0.5 at the top of a 1 m cutaway, about 2.2 cm).
   - A 1.5 m piece next to a 3 m piece steps 4.9 cm·S on one side and 0.56 cm·S on the other.
   - The dx term 0.02·sin(2πz/2.3+0.4) is uniform per z but follows each piece's local X. At z=0 it is 7.8 mm, so floor tiles rotated 90° misalign, and wall ends at corners slide up to ±2 cm.
   - **Seam rule:** finish with `wobble=False` and apply a module-owned pre-finish wobble that is zero at every x=k·0.75, for example `dy=A·sin(2πx/1.5)·S(z)`, or a per-piece bow `A·sin(π(x+W/2)/W)·S(z)`. Drop or keep dx the same everywhere. This needs vertex density: `grid_cut` at 0.25–0.5 m. Never use jitter on boxes that touch piece edges.

2. **UV continuity math.** For centred pieces with zero offsets, a seam is continuous only if (Wa+Wb)/(2t) is an integer.
   - STONE (t=3) with two 1.5 m pieces: 0.5, a visible half-tile jump.
   - A 1.5 m piece next to a 3 m piece needs 2.25/t to be an integer, so t=0.75.
   - **Rule:** give every piece `offset=((W/2)/t % 1, (D/2)/t % 1)` (the same sign for ±Y faces; this amounts to measuring UVs from the piece's min corner), and choose a t that divides 1.5 (1.5, 0.75, 0.5, …).
   - Current TILEs that fail this: PLASTER 2.2, WOOD 1.6, PLANKS 2.0, STONE/ASHLAR/FIELDSTONE 3.0, STONE_BLOCK 1.2, WATTLE 1.0. Only ROCK and CLAY (1.5) pass.
   - Re-project continuous surfaces with `k.project(faces, mi, offset=..., tile=...)` after `box()`, because box's hash offset breaks continuity and also shifts v between cut and full walls (different box centres give different offsets).
   - The exterior hides plaster seams with a timber post at every module's left edge; that is the alternative if you don't do this.

3. **Horizontal STONE faces become STONE_BLOCK at tile 1.2**, overriding the `tile` argument. Floors and wall caps must use STONE_BLOCK, ASHLAR, FIELDSTONE or PLANKS explicitly with a tile that divides 1.5. Pop-out stones from `wall_rocks` assume STONE at 3 m with offset 0 and misalign on 1.5 m pieces.

4. **Floor tiles bake UVs in local space**, so rotating a tile turns the planks. Place floors at rot 0 only (at 180° the texture mirrors), or use direction-free textures. Walls may rotate freely.

5. **Grime is by local z.** It is 0.62 at z=0 and rises to 1.0 at 0.9 m.
   - A floor with its top at z=0 is uniformly ×0.62.
   - A 1 m cutaway wall is almost all grime band.
   - Tabletop or shelf props built at z=0 get dark bottoms wherever they are placed, so use `grime=False` for them.
   - Undersides are ×0.72 even with `grime=False`.
   - `finish` overwrites all `Col`, so custom vertex AO (such as darker room corners) has to be written after `finish`, into the mesh that `full_rebuild` copies.
   - **Unity:** grime and AO live only in vertex colours, so Unity needs a vertex-colour-multiplying shader.

6. **Workshop ground z-fights with floors.** The WS ground plane is at z=0, so an interior floor with its top at z=0 z-fights with it. Hide `WS_<agent>_Ground` or raise the assembly.

7. **Upper floors:** one scene per floor with its own z=0, so `grime=True` is right for upper-floor pieces too. This differs from the exterior, where upper walls use grime False.

8. **Unity culls back faces.** One-sided quads (VOID backings, glass) disappear from behind in Unity, and `finish` does not close them. Cutaway walls are seen from above and behind, so build them as closed solids with a deliberate top cap material. The Blender materials leave backface culling off, so Blender renders will not show the problem.

9. **Name collisions:**
   - Prefix every helper (`int_`).
   - Never reuse a function name that already backs a registered piece; `_late` will swap it.
   - Keep piece names new. Door pieces containing `_Door` match `is_door` if they ever end up in the valley collection.

10. **Periodic helpers assume 3 m:** `roof_sag`, `_pnoise` (thatch), `hum_plate`, `wall_rocks`. They misbehave on 1.5 m pieces.

11. **Exterior-only helpers:** `batter()` pushes vertices with y<−0.2, z<0.05 out to −Y. `plinth()` places foundation rocks on the −Y face. Neither suits interior faces.

12. **Smoothing depends only on the material index** (see §2). Bedding and cushions in CLOTH_A/B come out smooth; metal candlesticks and the like will be faceted.

13. **`full_rebuild` does not move props to existing masters.** Write any piece-level props after rebuilding, or better, put them on instances.

14. **Separate interior scenes** can hold instances whose masters stay in `VillageKit/VK_Pieces`. `vcol()` links new collections into VillageKit, so pass explicit collections for other scenes.

15. **The Lit window style is a warm night emission.** A daylight look from inside needs a new variant (`variant_mat` special-cases "window"), which is a core edit.