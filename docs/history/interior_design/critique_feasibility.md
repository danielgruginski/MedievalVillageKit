# VKI Interior Kit spec: code review, most severe first

I checked the spec against `src/core/vk_helpers.py`, `vk_mat.py`, `vk_kit.py`, `src/workshop/ws_common.py`, `src/textures/vk_tex.py`, `vk_texgen.py`, `vk_tex2.py`, `vk_mod_industry.py`, `vk_mod_town.py`, `tools/kit_sync.py`, `tools/render_showcase.py` and `docs/PIECES.md`. I made no Blender calls and edited no files. Numbers use the spec's own constants.

1. **Stair_Up does not fit its footprint, and its lip runs into the head wall. HIGH.**
   - **Evidence:** spec §3.3 has 15 risers × 0.20, going 0.28, and a 1.5 × 0.6 lip at z 3.0. The class O north wall line is at local y 4.5, so its room face is at 4.25 and the cap/skirting line at 4.23.
   - **The numbers:** 14 goings × 0.28 = 3.92, plus 0.60 of lip = 4.52. That is 0.29 m past 4.23. The top tread and the lip sit inside the wall body.
   - **Z-fights:** the lip top (3.00) equals the Full cap top (H = 3.00) where they overlap. The lip spans x 0–1.5, so it also overlaps the west wall's cap top.
   - **Posts:** the flight at x 0.27 and the Stair_Down hole at x 0.27–1.27 overlap the west wall's Mid posts (±0.30) by 3 cm at every node, so posts hang over the hole edge.
   - **Missing:** the mirrored flight position for RailL is not given.
   - **Fix:**
     - Set going to 0.259 (14 × 0.259 = 3.63), so the lip runs y 3.63–4.23.
     - Lip x 0.31–1.50. Flight x 0.31–1.27 (RailR) or 0.23–1.19 (RailL). Hole x 0.31–1.27, y 0.10–4.20.
     - Add a rig test: no vertex of a link piece inside any wall or post envelope.

2. **The occlusion model only looks along the camera pitch; Full N–S partitions hide floor to the side, and R-occ1 is too short away from screen centre. MEDIUM-HIGH.**
   - **Sideways hiding:** §1 considers pitch only, and §2.4 makes every N–S wall Full by default, partitions included. A ray over a wall of height H at lateral offset dx lands H·dx/(13.79 − H) beyond it (camera height 13.79 at D = 18).
     - A 3 m wall hides 0.28·dx: 0.83 m at dx 3, 1.67 m at dx 6. A 4.5 m Ashlar wall hides 0.48·dx.
     - Tavern_F1: with the target clamped at x = 3, the Board partition at x = 9 hides the whole bed column at col 6.
     - Cottage: the fit camera at x = 4.5 loses 0.42 m of the bedroom behind the x = 6 partition.
   - **Along the pitch:** a 1.0 m cut wall hides 1.45 m at the top of frame (φ 35°), and 1.15 m for a partition 4 m north of a follow target (φ ≈ 41.5°). R-occ1's 0.9 m is only true at screen centre.
   - Perimeter side walls are fine, because the side they hide is void.
   - **Fix:**
     - Make interior N–S partitions Cut by default. Keep Full for perimeter side walls, and for partitions whose far side has no walkable floor.
     - Raise R-occ1 to 1.5 m.
     - Add a visibility test (T19). Per scene, sample camera targets: the fit target, or a 1.5 m grid inside the follow clamp. From each, `scene.ray_cast` to every `vki_use` point, trigger centre and spawn at z 0.5. The first hit must be within 0.3 m of the point. This is stronger than R-occ1–3, which stay as warnings.

3. **The wobble amplitudes break T13 and the caps' overhang, and they are invisible anyway. MEDIUM-HIGH.**
   - **Evidence:** §2.6 sets `VKI_AMP` Stone 0.022 and Wattle 0.020, outward only, with PROUD 0.02 (caps at 0.27 for class O, 0.17 for class P). T13 requires body ≤ cap − 0.005.
     - Stone: 0.25 + 0.022 = 0.272 > 0.265.
     - Wattle: 0.15 + 0.020 = 0.170 > 0.165.
     - Both fail by construction, and the stone body bulges past its own coping.
   - **Visibility:** with `grid_cut` at step 0.25, a Cut 150 piece only moves vertices at x 0.5/0.75/1.0 × z 0.5/0.75. Timber, pinned at the studs, only moves x 0.5 and 1.0. 12 mm is 1.3 px at 112 px/m. The exterior `Kit.finish` uses 0.035 at 40 m.
   - **Fix, one of:**
     - Cap A at 0.015 for every family.
     - Or raise PROUD to 0.035: caps O 0.285 / P 0.185, POST_HW O 0.315 / P 0.215. The O post still fits within NODE_FLAT 0.32 and still covers the cap corner.
   - Either way, decide at the C3 look gate with an A/B render. Add an end-pinned vertical sag on caps and rails (≤ 0.02, zero within NODE_FLAT); from above, that is what reads as irregular.

4. **Overlapping faces at junctions: T5 fails on every rig, a missing post must be an error, and posts must reach the footing. MEDIUM-HIGH.**
   - **Evidence at an L junction** (north wall x ∈ [0, L], |y| ≤ 0.27; west wall |x| ≤ 0.27, y ∈ [−L, 0]): the skirting tops (0.16), cap tops (1.00 or H) and body tops face the same way and are coplanar over [0, 0.27] × [−0.27, 0]. At a T junction the overlap is [−0.27, 0.27] × [−0.27, 0].
   - **What breaks:**
     - T5 has no rule for faces enclosed by a post, so every L/T/X rig fails.
     - §2.3 treats a missing post as a warning only. At L/T/X that leaves a visible z-fight.
     - T1 fixes only the post top. Wall bodies go down to −0.30, so T4 fails on the footing vertices unless posts do too.
     - There is no rule for which family's post to use where two families of the same class meet (Tavern_F0: Timber wall with the Stone `Hearth_300`).
   - **Fix:**
     - T5 skips pairs whose overlap centroid lies inside a post box.
     - A missing post at L/T/X or at a height change is an error; a free end is a warning.
     - Posts span z −0.30 to H + 0.04.
     - Tie-break the post family: Stone > Ashlar > Timber > Wattle > Board.

5. **Square Mid posts leave 3 cm jamb slivers, make 40% of a wall post, and pierce 3 m wall props. MEDIUM.**
   - **Evidence:** §2.3 puts a POST_HW 0.30 post at every node for Timber, Wattle and Board, against OPEN_MIN 0.33. That leaves 0.03 m of frame beside each opening (3.4 px) and a 0.60 m pier every 1.5 m.
   - `Tapestry_300`, `Pantry_Shelves_300`, `Settle_300` and the reused `Prop_ToolWall` (1.80 m wide per `docs/PIECES.md`) all span a node. The post stands 0.05 proud of the face, through them.
   - **Mid posts cover nothing:** collinear ends are identical by T2. A height change or a free end only needs the end plane (x = 0, |y| ≤ 0.27) covered.
   - **Fix:**
     - Make Mid posts ±0.12 along the wall × ±0.30 across (±0.10 × ±0.20 for class P). They still cover height changes and free ends. Keep square Corner posts for L/T/X only.
     - Keep OPEN_MIN 0.33, which now shows 0.21 m of frame. Optionally add a `Door_150_W` (clear 1.10, OPEN_MIN 0.20), allowed only in pieces whose end nodes are not L/T/X. Every §6 door meets that rule except the smithy store door, which is class P, where a 0.20 Corner post already allows 1.04.
     - Wall-hung items stand 0.06 off the face, or come as 150 bays.

6. **The plans use Board rakes that are not in the piece list. MEDIUM.**
   - **Evidence:** the §3.1 table has no Board Rake. But §6 has a `t` at x 3.0 row 0 in the Smithy (Board store partition), and Tavern_F1 (partitions Board) has `t` at x 4.5 and 9.0 on row 0 and at x 3.0 and 7.5 on row 4.
   - **Also:** `bn` means "form or settle", and Tavern_F0 row 5 puts `bn` directly south of the hearth zone. A settle's 1.2 m back hides 1.0 m, so P1's defect survives the repair.
   - **Fix:**
     - Add Board `Rake_150_L/R` (Board becomes 12 masters, 81 in total), or define those ends as Full Corner posts.
     - Split `bn` into `fm` (form) and `st` (settle), and forbid settles south of `fp` or anything interactable.

7. **The Rake contradicts NODE_FLAT, T3 and T4. MEDIUM.**
   - **Evidence:** §2.4 slopes the rake from 1.00 at x = 0. The Cut Corner post at that node tops out at 1.04, but the rake top is already 1.40 at x = 0.30.
     - T4 fails: rake vertices sit in the node square above the post, and the 2 cm ray grid hits the rake cap first.
     - T3 fails: the profile changes inside 0.32 of the node.
     - Ashlar climbs 3.5 m over 1.5 m, a 67° slope.
   - **Fix:**
     - Keep the Cut profile for x ≤ 0.32 and the Full profile for x ≥ L − 0.32. Slope only in between: 67° for Timber, 58° for Wattle.
     - Allow "rail springs from post" as a documented T4 exception at the high end.
     - Ashlar uses the full-height post instead (a 76° slope otherwise).
     - State that L means the low end is at x = 0.

8. **The surround zone makes the Stone round-arch door impossible. MEDIUM.**
   - **Evidence:** §2.1 limits the surround to x ∈ [0.25, 0.33]. §3.2's Stone door has clear width 0.84, spring 1.78, crown 2.20, with voussoirs inside x 0.25–1.25. That caps the ring at 0.50 − 0.42 = 0.08 m deep at the springers (9 px). The exterior `wall_stone_door` uses 0.34–0.50 m voussoirs.
   - **Why the rule is stricter than needed:** inside the node zone, anything within the post footprint is hidden when a post exists. Stone runs have no posts, and a proud voussoir end there looks fine.
   - **Fix:** make the envelope x ∈ [0.02, 0.33], |y| ≤ POST_HW − 0.01, z ≤ post top. That allows 0.25–0.30 m voussoirs. Update T3 to match.

9. **The VKI slot indices sit on top of a list that keeps growing. MEDIUM.**
   - **Evidence:** `vk_helpers.kit_mats()` ends with `...=range(55)`. `docs/PIECES.md` (2026-09-23) lists 52 material slots on 416 `SM_VK` masters, while `kit_mats()` now returns 55; GOODS, DRESS and HEWN were appended recently. One more exterior slot shifts FLOOR through FX on every VKI master.
   - `vk_helpers.variant_mesh` already guards `slot < len(me.materials)` because older masters carry fewer slots.
   - **Fix:**
     - `VKIKit.finish` uses `kit_mats()[:55] + vki_mats()`, and asserts `kit_mats()[54].name == "M_VK_Hewn"`.
     - `vki_variant_mesh` guards the slot range when styling reused exterior masters.

10. **The window spot lights are blocked, and Night scenes show daylight windows. MEDIUM.**
    - **Blocked spots:** §6 aims a spot through each window from 2 m outside. But the glass is a closed opaque box, and the Wattle daylight card and the stained glass are also opaque. Blender 4.2+ removed the per-material shadow setting (`shadow_method`), so opaque glass casts shadow and no light pool appears.
    - **Night:** §4.1 bakes WINDOW → `Window_Day` into every master, and the Tavern uses the Night preset.
    - **Fix:**
      - In `Window_Day`, `Daylight` and `Stained_In`, mix in a Transparent BSDF on the Light Path "Is Shadow Ray" output, and set `use_transparent_shadow = True`.
      - Add `M_VKI_Window_Night` and a night stained material. `vki_build_scene` applies them as a {window, stained} style in Night scenes.
      - Add a look-test assertion: the window-pool pixels are brighter than the floor mean.

11. **VKI code can silently change exterior pieces, and T15 checks too few masters. MEDIUM.**
    - **Evidence:** `vk_helpers._late()` resolves builders through `globals()[fn.__name__]`, and helpers look up globals when called. `vki_ns` runs the VKI texts in the same dictionary as `vk_helpers` and the 8 modules. So any VKI top-level name that equals a kit name (`barrel`, `ring`, `lathe`, `plinth`, `shutter`, …) changes exterior rebuilds done from that namespace. T15 hashes only 5 masters.
    - **Fix:**
      - T18: parse every VKI text with `ast`; top-level names must start with `vki_`/`VKI_` (or be `VKIKit`) and must not appear in `vk_kit_ns(terrain=False)`.
      - Extend T15 to hash all `SM_VK_*` masters (about 420 meshes, cheap).

12. **The Wattle B "bare WattleIn patch" has no material slot. LOW-MEDIUM.**
    - **Evidence:** §4.1 has 11 VKI slots; WATTLE (47) is banned; `WALL_A` is daub. None of them can hold WattleIn next to daub on the same piece.
    - **Fix:** add slot 66 `INFILL_B` (67 slots; update T14), or drop the patch.

13. **The vertex colour layer `Col` is stored as sRGB bytes; the spec's values read as linear. LOW-MEDIUM.**
    - **Evidence:** `Kit.__init__` creates `bm.loops.layers.color.new("Col")`, a byte-colour layer. Blender treats those bytes as sRGB and linearises them in the shader, so grime 0.75 → 0.52, the footing's 0.34 → 0.095, and `vki_heat` 0.5 → 0.21 in GlowIn's mix. Confirm with one test quad before relying on it.
    - **Fix:**
      - State that the §2.8 values are in display space.
      - Drive GlowIn from the float attribute `vki_heat` through an Attribute node; bake it to `Col.r` or UV2 only at export.
      - Remove `vki_body` and `vki_dark` from the mesh after finish (they are build-time only).

14. **The package boundaries have gaps. LOW-MEDIUM.**
    - **Textiles:** PKG-L is told to produce `M_VKI_Textiles`. But `vki_mats()` (core) creates it as a flat placeholder at the first finish, and packages may neither call `vki_apply_mats` nor edit `vki_core`. The placeholder would stay.
    - **Shared datablocks:** `W_VKI_Day`, `VKI_Key`/`VKI_Fill` (linked into every `WS_vki_*` scene), `M_VKI_*` and `T_VKI_*` are not listed as read-only. A package retuning `VKI_Key` for its render changes every scene.
    - **After adoption:** once `vki_adopt` moves masters into `VKI_Pieces`, the `ws_owner` guard in `ws_common.ws_build` blocks any package fix.
    - **Fix:**
      - PKG-L delivers only the `T_VKI_Textiles_*` images; the coordinator runs `vki_apply_mats(["M_VKI_Textiles"])`.
      - Add an explicit read-only list for packages.
      - Fixes after adoption go through the coordinator's `vki_rebuild`.

15. **`vki_ws_build` must not copy two `ws_build` behaviours. LOW.**
    - `ws_common.ws_build` lines 69–70 reset `use_smooth` by material index, which also drops GOODS smoothing. That contradicts "finish honours `f.smooth`".
    - Its re-projection of faces with all-zero UVs uses `Kit.project`, where `TILE.get(mi, 1.0)` has no entries for 55–65.
    - **Fix:** `VKIKit.project` checks a `VKI_TILE` table first; `vki_ws_build` and `vki_rebuild` leave out the smoothing loop.

16. **API mistakes, and helpers that default to banned slots. LOW.**
    - `vk_mat.pbr_material(mat, prefix, …)` takes the material first; §4.3's `pbr_material(prefix="T_VK_Stained", emission=1.8)` omits it.
    - Helpers that fill banned slots:
      - `smithy_chimney`, which `Forge_300` is "built from", uses STONE and STONE_BLOCK, so the forge must be re-implemented.
      - `window_frame` hard-codes a STONE sill.
      - `stone_panel` and `plinth` default to STONE; `lathe` and `rock` default to STONE_BLOCK.
    - The lancet apex numbers do not match `lancet_pts`, where the rise above the spring is 0.7746·width:
      - Ashlar door: 2.50, not 2.45.
      - Lancet glass (0.6 wide, spring 3.00): 3.465, not 3.55.
      - LancetTall: 3.765, not 3.90.
    - `vki_ns` lives in `vki_core` and reads `VKI_TEXTS`, so it needs a bootstrap line:
      ```python
      g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"]()
      ```

17. **The B variants' Full and Cut twins do not match. LOW.**
    - `Plain_150B_Full` pairs with `150A_Cut`. Below 0.65 m the B piece uses wobble seed B and the Cut piece seed A, so toggling changes the lower wall and fails T2 ("Full equals Cut for z ≤ 0.65") for this pair.
    - `Plain_300_Cut`'s second span uses seed B, which no 150 Cut piece has.
    - **Fix:** add `Plain_150B_Cut` for Timber, Stone and Wattle (3 masters, without brace or pop-outs), with reciprocal pairs.

18. **Some pieces break the reserved-height rule. LOW.**
    - The Wattle sole beam (0–0.20) tops out at the dais height, 0.20.
    - `Counter_Shop_300` (1.0), `Altar_150` (1.0), `VotiveRack` (1.0) and `Pew_300` (0.95) fall inside the 0.90–1.00 cut-cap band.
    - Rugs at "2–4 cm" include the hearth apron (0.02) and the threshold (0.03).
    - The `Fireplace_300` breast top at H overlaps the cap top over y −0.27 to −0.25, and uses `WALL_A` instead of `CAP`.
    - **Fix:** Wattle sole to 0.16; wall-backed props keep their tops outside 0.88–1.02 or stand 0.03 off the face; rugs at 0.025 or 0.035; breast top at H + 0.04 in `CAP`.

19. **T1's wall bounds need exemptions. LOW.**
    - Specials reach y −1.45; pop-out rocks reach about −0.335 (`rock()` jitter plus depth 0.10); the `Window_Cut` sill is ±0.33.
    - **Fix:** T1 uses each master's `vki_footprint`; limit pop-out depth to 0.06.

20. **The StoneIn stone list gives almost no pop-out candidates, and u is mirrored. LOW.**
    - `vk_tex2.gen_stone` writes only stones with w·h > 0.25 m². At T 1.5 with 4 courses of about 0.375 m, only stones wider than 0.67 m qualify: 0–3 of about 12.
    - `wall_rocks` maps `x = ((-3u+1.5)%3)-1.5`, because the −Y face projects u = −x/t.
    - **Fix:** use a 0.08 m² threshold in the copy; map x = (−1.5u) mod 1.5 and z = 1.5v (+1.5k); keep stones at least 0.32 + w/2 from nodes.

21. **T17 needs masks that EEVEE cannot provide. LOW.**
    - EEVEE has no material-index pass, and Cryptomatte cannot be decoded from a PNG.
    - **Fix:** test the whole frame (min RGB ≥ 0.98 on under 0.3% of pixels), or render a second pass with an emission-only override.

22. **Edge-locked B/C floor variants cannot break the joint repeat, and `Floor_600` cannot mix variants. LOW.**
    - With 2 butt joints per board per tile, each board's only interior segment ends on the two locked joints. Every variant therefore has the same joint layout, and each variant is a separate material per whole piece.
    - **Fix:** one edge-locked A|B|C atlas; bake a per-cell variant into `Floor_300`/`600` UVs (cells as separate quads, floor budget up to 40 tris); 3 joints per board so a variant can move one.

23. **The apron textures render at the wrong scale. LOW.**
    - `T_VK_Cobble`, `T_VK_Dirt` and `T_VK_Grass` are generated at T 4.0. Under the world-locked FLOOR rule (tile 1.5) they render at 37% scale.
    - **Fix:** the Apron gets its own UVs at t 4.0.

24. **The camera fit has no target, and the plan grammar has gaps. LOW.**
    - The fit formula assumes the apron sits at the bottom edge, but no target is given. Use y_t = y_S − 1.5 + 0.2856·D, x_t = room centre.
    - The follow clamp y_S + 2 shows 1.6 m of void; use y ≥ y_S − 1.5 + 0.2856·D.
    - The Smithy's "Sf on x = 6.0" is a node line the cell grammar cannot express (`Sf` at col 4 is x 6.75).
    - `DoorWide` has no trigger or spawn defaults.

25. **Link and leaf clearances. LOW.**
    - **Door spawn:** at (0.75, −1.35) with capsule radius 0.3, the spawn touches the trigger edge at −1.05.
    - **Stair_Up trigger:** which side of the first riser the band sits on is unspecified. On the south side it overlaps the `Ss` spawn capsule.
    - **Door leaf:** at 100° the free end reaches (0.18, −1.03), inside a perpendicular wall whose face is at 0.25.
    - **Trapdoor:** at Tavern (6,6) the leaf (to y 10.28) touches the north wall face at 10.25.
    - **Fix:** spawn at −1.50; put the band on the flight side; open leaves to 90°; move the hatch 0.1 m south.

26. **The new textures add a lot to the .blend. LOW.**
    - `blender/medievalDiorama.blend` is already 400 MB, because `vk_tex.write_map` packs every image. `write_set` writes 5 maps per set but `pbr_material` reads only BC, N and R. §4.2 adds about 19 sets, 95 images.
    - **Fix:** a VKI `write_set` that writes and packs only `_BC`, `_N` and `_R`.

27. **Mount heights ignore the family's wall height; master metadata never reaches instances. LOW.**
    - The `Tapestry_300` rod at 2.8 is taller than the 2.4 Wattle wall. `Beam_Stubs_150` at "H − 0.30" is one master for H of 2.4, 3.0 and 4.5.
    - `vki_*` metadata lives on the hidden master objects. FBX exports only object properties, so scene instances carry none.
    - **Fix:** add a `vki_mount_zmax` check to T12; make stubs per height (or set z at placement); have `vki_place` copy master props onto instances, or plan the export as masters plus a JSON layout.

**Confirmed correct:**
- **Camera maths:** lens 38 gives a 29.8° vertical FOV; floor span −5.14 to +8.12; the 0.778 and 0.737 factors are right.
- **World-locked UVs:** `Kit.project` gives u = −x/t on −Y faces, and a 180° rotation shifts u by a whole number of tiles.
- **§0.2 claims:** #1 (AgX), #7 (tool wall back at −0.01, lantern back at +0.10), #10 (`ws_common` L83), #12 and #13 all hold.
- **Bellows:** `SM_VK_Prop_Bellows` resolves to the industry `ind_bellows` (nozzle −X), because module specs register later.
- **Name clashes:** `VARI_` meshes are untouched by `full_rebuild` (it only matches `VAR_`), and `ws_build`'s `SM_VK_` assert does reject `SM_VKI_` names.

**Relevant files:**
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_helpers.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_mat.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\core\vk_kit.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\workshop\ws_common.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_tex.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_texgen.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\textures\vk_tex2.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\src\modules\vk_mod_industry.py`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\docs\PIECES.md`
- `E:\Unity\Projects\GameArtGeneration\MedievalVillageKit\blender\medievalDiorama.blend`