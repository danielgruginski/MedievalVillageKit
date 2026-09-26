# Interior kit (VKI): core API notes

Collected from the core-stage engineers' hand-in reports (2026-09-26). Where sections disagree, the LAST one wins.
Spec: [INTERIOR_SPEC.md](INTERIOR_SPEC.md) (see its §10 amendments). Packages: [PACKAGES.md](PACKAGES.md).

## Core API (C1: vki_core, vki_test)

LOAD: g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"](). This gives vk_kit_ns(terrain=False) + vki_core + each VKI_TEXTS entry that exists, in order: vki_fam_timber, vki_floors, vki_fam_stone, vki_fam_board, vki_fam_wattle, vki_fam_ashlar, vki_links, vki_props_home, vki_props_tavern, vki_props_smithy, vki_props_chapel, vki_rooms, vki_test. vki_test loads last, so g["vki_test_pieces"] is always available. Every top-level name in a vki_* text must start with vki_/VKI_ (or be VKIKit); T18 checks this. Imports of the same modules the kit uses are allowed.

NAMES: SM_VKI_<Class>_<Family>_<Kind>_<Len><Var>[_<L|R>]_<Full|Cut>. <Class> is Wall/Post/Floor/Stair/Apron/Leaf/Prop/Rug/Runner/RushMat/FX/Test; I read the spec's '<Class>' as this token, not O/P. Examples: SM_VKI_Wall_Timber_Plain_150A_Full, SM_VKI_Wall_Timber_Plain_300_Cut, SM_VKI_Wall_Timber_Rake_150_L, SM_VKI_Post_Timber_Corner_Full, SM_VKI_Floor_150_Q10, SM_VKI_Leaf_Plank_Cut. vki_parse_name(n) returns dict(cls, fam, kind, len[m], depth, var, height).

T2 and T3 look up references by name: SM_VKI_Wall_<Fam>_Plain_150A_Full and _Cut. Keep that spelling.

REGISTER builders at the end of your text:
  vki_register([("SM_VKI_Wall_Timber_Plain_150A_Full", vki_tim_plain_full, {"grime":"wall"}, "core"), ...])
- Each tuple is (name, fn(k), finish_kw, pkg). Same names replace earlier entries.
- grime is one of "wall" | "floor" | "prop" | "none".
- Build masters with vki_rebuild(names) (core; into VKI_Pieces, hidden, instances update in place, then VARI_* refresh).
- Package engineers use vki_ws_build(agent, names): pkg must equal agent, or pass names. It builds into WS_vki_<agent>_Pieces with an ownership guard.
- Never call k.finish on a real name. It raises unless the name starts with "__vki"; the two build functions use temp names.
- Check pieces with vki_test_pieces(names); {} means clean. It runs T1, T7, T8, T9, T10 and T14 on every piece, T2 and T3 on shipped walls, and T13 on walls from VKI_SPECS.

VKIKit(name): fam, cls (O/P), T (0.5/0.3) and H come from the name. k.set_family("Timber") changes them. Attributes and helpers:
- k.meta: dict. Keys without the vki_ prefix get it added in finish, except kit, grid_m and hinge_axis. Lists and dicts are stored as JSON.
- k.slot_mats: {slot index or style key: style name, 'M_...' name or Material}. Allowed only for WATER, WOOD, PLANKS, SHUTTER, CLOTH_A, CLOTH_B, WINDOW and 55..66. Example: {WOOD: "Dark"}, {WINDOW: "Daylight"}, {VKI_FLOOR: "ApronCobble"}.
- k.body_box(x0,x1,z0,z1,y0=-T/2,y1=+T/2,step=0.25,mi_a=VKI_WALL_A,mi_b=VKI_WALL_B): the wall-body panel. -Y face is WALL_A (room), +Y face WALL_B, ends/top/bottom WALL_A. On Stone and Ashlar the horizontal faces switch to STONE_BLOCK_IN. It runs grid_cut at 0.25, flags all new verts as body, and returns them. Build openings from several body_boxes around the hole.
- k.box(...): the Kit signature. UV offset is zero for FLOOR, WALL_A, WALL_B and INFILL (world-locked); every other slot gets the kit centre-hash offset.
- k.project(faces, mi, axes=None, sizes=None, offset=(0,0), tile=None): uses VKI_TILE for slots 55 and up, else TILE. It honours an explicit offset and tile, so Q floors call it with offset=(0.5*a, 0.5*b) and the Apron with tile=4.0. The Stone/Ashlar coping switch applies here too. CAP grain runs along the longest box axis when axes are given (like WOOD).
- Layers k.body (int), k.dark (float 0..1, via k.set_dark(verts,d)) and k.heat (float; k.set_heat(verts,h), GLOW core 1 .. rim 0) all exist from __init__. NEVER add a bmesh layer yourself mid-build: it invalidates every BMVert reference you hold (hit and fixed here).
- f.smooth is kept exactly as the builder sets it.

vki_wobble(k, L, fam, variant, holes=[(x0,z0,x1,z1)], top_body_fn=lambda x: cap_bottom_z, pins=(stud x,...)): §2.6 verbatim. Call it LAST. It moves only verts flagged body with |y| == T/2 (1e-4), outward only. VKI_FLAGS["wobble"] / ["sag"] are the G1 A/B switches; family builders should read ["sag"]. k.wobble_off is used by T13.

finish (inside vki_rebuild):
- Col is written by §2.8 as (g, 0.98g, 0.95g), in display space.
- sRGB result: bmesh writes raw bytes. 0.75 is stored as 191 (0.749); the mesh attribute .color reads 0.521 (linear); the shader linearises, so an Emission of Col rendered under Standard gives 0.753 on the PNG. Col values are display-space, and the albedo gets x0.52 at 0.75.
- Underside faces get x0.72; the final factor is x(1 - vki_dark). CAP top faces get 1.0. grime "none" gives exactly 1.0 everywhere.
- vki_rim = 1 - heat (POINT float) is stored only if some heat > 0. Write heat on every GLOW vertex.
- vki_body, vki_dark and vki_heat are removed.
- Slots: kit_mats()[:55] + vki_mats() = 67, with the M_VK_Hewn assert.
- Masters get GLOW = M_VKI_GlowIn, WINDOW = M_VKI_Window_Day, STAINED = M_VKI_Stained_In, DRESS = M_VKI_Dress.
- Family defaults: Stone WALL_A/B = StoneIn and CAP = StoneBlockIn; Ashlar AshlarIn / Dress; Board BoardsV; Wattle PlasterDaub; Timber PlasterCream + CAP Hewn. Props get PLANKS = M_VKI_WoodScrubbed.
- Banned slots and indices >= 67 raise ValueError.

Default metadata written by finish:
- kit="VillageInterior", grid_m=1.5, vki_class, vki_piece, vki_family, vki_kind, vki_len (metres), vki_var, vki_height, vki_thick.
- vki_origin, vki_rot_lock (world0 for floors), vki_footprint = geometry bbox rounded outward to 1e-4 (T10 wants footprint = bbox within 1e-3; override only if exact).
- vki_fp_cells, vki_collider (walls: [[L/2,0,1.1,L,T,2.2]]), vki_nav, vki_uv_lock, vki_mount="floor" for props.
- vki_cut_pair is filled automatically when both _Full and _Cut are registered.

YOU must set:
- vki_cut_to on Plain_150B_Full and on Rakes (value "…Plain_150A_Cut").
- vki_opening as {"x0","x1","z0","z1"} or a list of them.
- On doors: vki_trigger [cx,cy,cz,sx,sy,sz] with cy < 0, vki_leaf_socket, vki_leaf_open_deg, vki_spawn_local, vki_prompt_local.
- vki_post_rule on posts (T10 requires it). hinge_axis and vki_leaf_state on leaves.
- vki_special=1 on Fireplace/Hearth/Forge (T1 allows H+0.04, T9 allows 6000).
- vki_tier on props: furniture / dressing / hero.
- vki_back_y on wall_floor props.
- vki_mount_ref="top" plus vki_mount_offset for Tapestry.

SLOTS: VKI_FLOOR 55, VKI_WALL_A 56, VKI_WALL_B 57, VKI_CAP 58, VKI_STONE_BLOCK_IN 59, VKI_BRICK 60, VKI_STRAW 61, VKI_ASH 62, VKI_TEXTILE 63, VKI_WAX 64, VKI_FX 65, VKI_INFILL 66. VKI_TILE={55:3.0, 56:1.5, 57:1.5, 58:1.2, 59:1.5, 60:1.5, 61:1.5, 62:0.75, 64:1.0, 66:1.5}.

Constants:
- VKI_T, VKI_H_FULL, VKI_CAP_HW, VKI_POST_HW, VKI_MID_HW, VKI_NODE_FLAT, VKI_OPEN_MIN, VKI_ENV_X/Y, VKI_FOOT_Z, VKI_PROUD_LINE, VKI_CUT_H, VKI_CUT_CAP, VKI_FULL_CAP, VKI_SOLE_TOP, VKI_Z (reserved heights), VKI_AMP.
- VKI_FAMILIES[fam] holds the §2.2 data: cls, H, wall_a, cap, rake, rhythm, prio, h_fit, sag.

MATERIALS:
- vki_mat(name) returns the material, building it if missing.
- vki_apply_mats() rebuilds every VKI_MAT_MAP entry in place. Run it after C2 makes the T_VKI_* textures; missing textures give flat placeholders flagged m['vki_placeholder']=1.
- Material names are 'M_VKI_'+style (PlasterCream, StoneIn, Boards_NS, Flag, ...). Special names: M_VKI_GlowIn, Window_Day/Night, Daylight, Stained_In/Night, Dress, Wax, Ale, WaterMurky, FX_Light, WoodDark, WoodScrubbed, StoneBlockIn, Straw, Ash, Textiles.
- Style keys (VKI_SLOT): floor, wall_a, wall_b (defaults to wall_a), infill, cap (Hewn/StoneBlockIn/Dress/PlasterDaub), wood (Oak/Dark), planks (Scrubbed/Planks), window (Day/Night/Daylight), stained (In/Night), glow (GlowIn), water (Water/Ale/WaterMurky), shutter/cloth/cloth_b (exterior variant names, e.g. shutter "Red").
- vki_variant_mesh(piece, style) creates VARI_<crc32> meshes; vki_refresh_variants(names).
- VKI_NIGHT_STYLE, VKI_REUSE_STYLE and VKI_REUSE_STYLE_NIGHT hold the §4.1 styles.

TEXTILES: VKI_TEXTILE_CELLS (8, in the contract order). vki_textile_uv(cell,u,v) implements the contract formula with PAD 24/1024 and 24/512. vki_textile_map(k, faces, cell, plane=(A,B), period=None) is planar; period=m gives the runner mode, where each face keeps u in 0..1, so faces must not straddle a period boundary.

PLACEMENT: vki_place(coll, piece, x, y, rot=0, z=0, style=None, mount=None, walls=None, wall_cls=None, hug=None, name=None, **props)
- Copies all master props onto the instance, then adds vki_piece, vki_rot, vki_at (the requested lattice point, used by T11) and vki_style, then **props.
- Reused SM_VK_* props get VKI_REUSE_STYLE and are placed so their bbox centre sits on the point.
- wall_floor puts the back (vki_back_y, else bbox max y) on the proud line of the wall found behind the point. Walls are searched in `walls`, else in all objects of coll's scene; with walls=[] it falls back to the next grid line with class wall_cls. It records vki_back_line ["x"|"y", value] and vki_host. Hug is on by default and slides along the wall up to 0.30, recording vki_hug or vki_hug_fail.
- floor mount with hug=True pushes off the walls on both axes.
- wall_hung puts the back on the face (T/2); z stays as given (authored height); vki_mount_ref="top" gives z = H - offset. It records vki_host_height and vki_host_H.
- Structure pieces are placed at their origin.
- vki_mw(o) is the world matrix computed from loc/rot/scale. Use it instead of matrix_world for objects made in the same call; matrix_world is stale there, which bit me in T5/T6.

SCENES / RENDER:
- vki_scene(name, preset=None, sync=False) copies engine, EEVEE settings and view settings from VillageKit on creation, uses W_VKI_<preset>, links VKI_Key/VKI_Fill, sets 1920x1080, and never changes the window's scene.
- VKI_Key (SUN, 62 deg from the SSW, angle 8, shadows on) and VKI_Fill (SUN, along the view, shadowless) are shared objects. vki_apply_preset sets their Day/Night values and vki_shot restores them.
- Worlds: camera rays see VKI_VOID_LINEAR = (0.0118, 0.0098, 0.0090), calibrated to show #0B0908 on the PNG under AgX -0.2. Other rays see VKI_PRESETS[preset]['world'].
- vki_shot(scene, name, mode="game"|"plan"|"free", D=None, target=None, preset=None, res=(1920,1080), samples=None, bounds=None, px_per_m=None, loc=None, lens=None) renders renders/interior/<scene>/<name>.png and returns the path.
  - game: pitch 50, lens 38, 36 mm AUTO sensor, clip 0.5/80, at target + (0, -0.643D, 0.766D).
  - plan: temporary ortho top camera; px_per_m=200 gives 2 px/cm.
  - The temp camera is deleted and all settings are restored.
- vki_rig(name, [(piece,x,y,rot[,style])], origin, scene="VKI_Test") fills VKI_Rig_<name>.
- vki_ws(agent) / vki_ws_build(agent, names) / vki_ws_shot(agent, name, mode, ...) work with WS_vki_<agent>: W_VKI_Day, ground hidden, VK_Sun unlinked in that scene only.

TESTS (vki_test): each vki_tN_* returns a list of error strings.
- vki_t4_rigs(fam, corner, mid, full, cut=None, fam2_full=None, fam2_mid=None, p_full=None, o_corner=None) builds the rigs; vki_t4_coverage(rigs) checks them. Each rig uses its own post's plan footprint as the node square.
- vki_t5_coplanar(objs), vki_t6_uv_continuity(objs), vki_t11_placement(objs, pairs), vki_t13_wobble(name), vki_t15_exterior_invariance(names=None), vki_t16_determinism(names), vki_t17_render_clip(path), vki_t18_namespace(), vki_t19_visibility(scene, cams=None, points=None) with vki_ray_blocked(sc, cam, point).
- vki_t12_room_rules(scene, room=None) is partial.
- vki_col_srgb_test(), vki_smoke_rig(), vki_test_all(t15=False).

BLENDER STATE (not saved; the coordinator saves):
- Scene VKI_Test holds VKI_Pieces (hidden, fake user) with the 2 test masters, and VKI_Rig_Smoke with 3 smoke instances, the axis and VKI_Test_Slab (test floor, not a master).
- Worlds W_VKI_Day/Night and all 43 M_VKI_* materials have fake users.
- VKI_Key and VKI_Fill are linked to VKI_Test only.

## Timber family and floors (C3)

LOAD: g0={}; exec(bpy.data.texts["vki_core"].as_string(), g0); g=g0["vki_ns"](). Timber masters are listed in g["VKI_TIM_NAMES"], floors, leaves, apron and overlays in g["VKI_FLOOR_NAMES"]. All are registered as pkg "core". Rebuild with g["vki_rebuild"](names).

TIMBER CONSTANTS (vki_fam_timber):
- VKI_TIM_HW 0.28, STUD_HW 0.06, HEAD (2.88, 3.00), RAIL (0.90, 1.00), OPEN (0.33, 1.17).
- VKI_TIM_WIN / VKI_TIM_DOOR / VKI_TIM_FP hold the §3.2 numbers.
- VKI_TIM_FOOT_TOP = -0.10: footings under openings stop at the floor-slab bottom.

GENERIC HELPERS (reusable by other families): vki_cut, vki_prism(poly, a0, a1, mi, axis), vki_band (curved members), vki_proj_long, vki_top_faces, vki_hash_off.

PLACING A DOOR:
- Leaf world position = door origin + R(rot) @ (0.33, -T/2 + 0.05). At rot 180 in an O wall that is (x0 - 0.33, y0 + 0.20); the leaf takes the same rotation. Ajar by d degrees means rot - d, which opens into the room (verified).
- The Apron goes at the door's origin with the door's rotation.
- The RushMat goes on the 0.75 lattice just inside the opening (the look test uses door x - 0.75, y 0.75).
- Exit link data goes on the Door_150_Cut instance: vki_link="exit", vki_link_id, vki_target, vki_prompt, vki_facing_min=60.

C3 RIGS IN VKI_Test — vki_c3_rigs() rebuilds them all; vki_c3_tests(rigs) returns {} when clean:
- T4 rigs at y -30, x 0..24.
- Seam boards: SeamFull at y -45 and SeamCut at y -51 (150|300|150 at rot 0/180/0, Mid posts at the free ends); FullCut at x 9..16.5, y -45; the floor-parity board at x 18..28.5, y -54..-45 (600, 300, all four Q parities, a Flag band with a straight oak sill run).
- Corner room at (0, -63), 4x4 cells.
- Catalogs: VKI_Rig_Cat (y 16.5 / 21) and VKI_Rig_CatFloors (y 6..11).
- vki_c3_floor_pieces(x0, y0, nx, ny, style) is the greedy 600 -> 300 (even nodes) -> Q150 cover. The assembler can reuse it.

LOOK TEST:
- vki_looktest(pillar=False, leaf_deg=0.0, night=False) fully rebuilds VKI_LookTest in collections _Shell, _Props, _Logic (SPN_front, VKI_Root with the fit camera D 18.02, target (4.5, 3.647)) and _Lights.
- Night shots need a night=True build, so VKI masters get VKI_NIGHT_STYLE and reused props VKI_REUSE_STYLE_NIGHT. Build night=True, shoot, then build again without it (to return to Day).
- vki_lt_shot(name, preset, mode="game"|"plan", **kw) switches the scene's window and apron lights to the preset's power and renders.
- vki_lt_lights(sc, shell, lights) turns every placed master's vki_lights (window SPOT, hearth POINT, apron AREA) into Blender lights. Each light carries vki_w_day/w_night, vki_color_day/night and a vki_light JSON (the LGT_ data). It is a working reference for the assembler.
- vki_lt_floor_luma(path) measures the walkable-floor luma of a 1920x1080 fit shot. vki_luma_stats(path, boxes) is the generic version.

DIAGNOSTICS:
- vki_self_coplanar(obj) finds z-fighting between the members of one master. It ignores faces buried against another member.
- vki_t5_coplanar(objs, buried_ok=True) now skips overlaps whose front (2 mm along the normal) lies inside another solid. Examples: butt-joint end faces that also sit on a floor joint, or a body top under a cap.
- Pieces keep one intended coplanar pair: the wall end face at x=0/L against the half-stud end face. It shows only at a free end with no post (§2.3 already warns there).

SCENE SHADOWS: VillageKit renders with eevee.use_shadows=False. vki_scene now forces it True on every VKI scene. Without it there are no window pools and no key shadows at all.

FOR THE ASSEMBLER:
(1) Sills meeting at an L overlap in a 0.1 m corner square (z-fight). Either keep sill runs straight, or add a shortened or mitred sill master later.
(2) Proud line vs posts: core's note still applies — clear max(proud line, POST_HW + 0.005) next to Corner posts.
(3) Specials (Fireplace_300_Cut) are never placed on Cut runs.
(4) Door thresholds are oak now, so a doorway reads as a gap in the pale cap outline.

G1 RECOMMENDATIONS (from 1920x1080 Day and Night game shots, inspected at full resolution; montages ab_*.png sit in renders/interior/VKI_LookTest):

1. Rake vs pillar -> RAKE. The side-wall cap steps down to a Cut-height corner post, so the cut-away reads as intended. Less floor is hidden next to the near corners. With the pillar, the tallest dark mass on screen is a 3.04 m post in the foreground at SE/SW, standing above the Cut south wall (g1_pillar_day). Cost of the rake: its 66.7-degree sloped top faces the camera and shows as a fairly large pale CAP plank. It reads as a cap, but a WOOD sloped top could be tried if it looks too heavy.

2. Exit leaf -> CLOSED (the spec default). It reads clearly as a strapped plank door with a pale top edge inside the Cut wall. Ajar 30 degrees makes the door read as a door slightly better, but the leaf then sits over the rush mat, and without FX_DoorSpill (not built) the gap looks like a hole rather than light.

3. Wobble + sag -> keep ON, but both are imperceptible from the game camera. At D 18, 1.2 cm is about 1.3 px: mean absolute difference 0.26/255, g1_nowobble_*. They are seamless, deterministic and cost nothing extra, since the 0.25 grid is needed anyway. For visible hand-hewn irregularity, raise the Timber rail sag to 0.02 (the Cut cap may sag to 0.98 by §2.1). Wall wobble cannot grow much: the T13 margin caps A at 0.025 for class O.

4. Key shadows -> ON. Props (table, benches, loom, stools) get short grounding shadows and the Full side walls give the room depth. With shadows off the room looks flat (ab_shadow_day_W). The side effect is a roughly 0.6 m shade band along the west wall, from the SSW key.

5. Levels:
- Day as specified gives walkable floor 0.261 (target >= 0.25): keep.
- Window spots at 350 W are too weak: pools average only +0.06 luma. I recommend about 800-1000 W by Day so the pools read (not rendered yet).
- Night as specified gives 0.083 (target 0.15). Key 0.8 / fill 0.6 / world 0.6 gives 0.150 with the fire still the brightest thing (ab_night_levels). Adopt that, or accept darker hearth-only nights and rely on candles and lanterns in the Night scenes.

6. Door width 0.84: reads fine at D 18, both as the exit with its leaf and as the partition doorway.

## First fix round

PER-FINDING OUTCOME (review round 1)

Technical review:
1. [major] Leaf hinge: FIXED. The planks sit on the room side of the hinge axis. Checked with the new vki_leaf_swing.
2. [major] T11 false error on the Apron: FIXED. The parity/even-node rule now applies only when vki_uv_lock == 'world'.
3. [minor] CAP grain turning across the wall: FIXED. vki_tim_member passes along=X for CAP tops; the rake flats are included.
4. [minor] Post end-grain UV: FIXED with vki_endgrain_fit (one centred ring).
5. [minor] T4 rays on the chamfer: FIXED. Rays in the chamfer triangles (dx + dy < bevel + 0.005) are skipped.
6. [minor] 150B brace T4 margin: FIXED. Brace geometry changed (control point 0.10); new T4 rig BMid.
7. [minor] Window Full/Cut footprint: FIXED. Sill slab is |y| <= 0.28, which §3.2's "<= 0.30" allows, so no spec conflict remains.

Visual review:
1. [major] Fire: FIXED. Root causes:
   - M_VKI_GlowIn washes to cream under AgX.
   - Its dark-but-lit base picked up the hearth light 0.1-0.2 m away.
   Fixes: GlowIn is now a pure emitter with deeper colours; the tongues are smooth and flattened; logs darker; the hearth light is raised.
2. [major] Window pools: FIXED. The spot is moved and narrowed and runs at 1000 W Day. REJECTED in part: "pool starting at the wall foot" is geometrically impossible. With a 1.00 sill and a 0.56 m thick opening, the nearest possible pool edge is about 0.45 m from the room face; the pool now lands about 0.7-1.5 m in.
3. [major] Night levels: FIXED. The Night preset is key 0.8 / fill 0.6 / world 0.6, giving 0.141 on the stricter metric (about 0.15 on the C3 box metric). The §6 start values are kept as VKI_NIGHT_SPEC and rendered as g1_base_night_speclevels for the user's G1 choice.
4. [major] Post tops: FIXED (same fix as technical 4).
5. [major] N-S Cut partition doorway: FIXED as a layout cue. The look test places a RushMat on each side of the doorway, (5.25, 3.75) and (6.75, 4.5), both rot 90; both mats show from the game camera. The piece is unchanged:
   - Pale CAP/limewash reveals would merge the doorway into the pale cap line.
   - A lower jamb contradicts §3.2.
   - Assembler rule to add in vki_rooms: every N-S Cut doorway gets overlay mats on both sides, never across the threshold.
6. [major] Apron and doorstep: FIXED (DRESS two-slab doorstep, apron light 60/25 W, cobble tint).
7. [major] Flag floor: FIXED in the texture (unequal courses, wider length and colour spread), and the look-test hall now uses FlagRustic, which §6 specifies for the Cottage. REJECTED in part: the 3 m repeat cannot be broken by Q parity. The 3.0 m world-locked period is the §2.7 design, so any flag pattern repeats at 3 m.

Visual minors:
- Cap patchy at openings: FIXED.
- Pinhole at 150|150 joints: FIXED. The speck was the body face behind the half-studs' chamfered tops. Oak plugs in front of the body faces' top corners plus oak body tops remove it.
- Brace UV: FIXED.
- Fit camera cropping the north caps: FIXED in the look test (0.4 m margin, D 18.567, target y 3.803). The §1 formula itself is for the coordinator: adding 0.4 to L would push the chapel to D 22.48 > 22, so apply the margin only to families whose h_fit has no margin.
- Board repeat: REJECTED. It is the §2.7 3 m period; the Tavern will show it too.
- Reused table mugs: DEFERRED. They are an exterior prop; PKG-T tankards will replace them.
- Logs and chimney breast: logs FIXED; breast trim DEFERRED (optional).
- Plaster band under the sole: FIXED. The footing band below z 0 is DRESS and darker.

NEW BUG FOUND AND FIXED
Blender ignored light energy/colour changes made in the same Python call as bpy.ops.render.render. The fix is vki_flush_lights(sc), which tags the lights and world and updates the depsgraph; vki_shot calls it before rendering. As a result:
- Every earlier Day/Night preset switch and light A/B render done in one call may have rendered with the previous call's light values. This includes the C3 night shots and the reviewer's window-spot A/B.
- Any helper that renders without vki_shot must call vki_flush_lights first.

USEFUL API (all under g after vki_ns)
- vki_shot(..., outdir="fix_r1/diag") renders into renders/interior/<outdir>.
- vki_leaf_swing(door, leaf, post, angles) returns {deg: (tris overlapping the door, tris overlapping the post)}.
- Floor luma:
  - vki_floor_luma_world(path, rects, D, target) returns (mean, used, dropped). It projects world floor points with vki_cam_project and drops points hidden by walls or props.
  - vki_lt_floor_luma(path) uses VKI_LT_FLOOR_RECTS and VKI_LT_CAM.
  - VKI_LT_FLOOR_BOXES is kept only for the old D 18.02 shots.
- Timber constants:
  - VKI_TIM_WIN_SPOT: window spot data.
  - VKI_TIM_HEARTH_LIGHT: the fireplace light socket.
  - VKI_TIM_FLAMES and VKI_TIM_FLAME_PROFILE, with vki_tim_flame(k, base, h, r, tilt, spin, bow): a reusable flame tongue for Hearth, Forge and Oven.
- Glow material: VKI_GLOW_CORE / VKI_GLOW_RIM / VKI_GLOW_STRENGTH. After changing them run vki_apply_mats(['M_VKI_GlowIn']).
- vki_endgrain_fit(k, faces, centre, U, V, half, fill): fill 0.30 for hewn posts, VKI_ENDGRAIN_R (0.44) for round log ends. Other families' posts should use it.
- vki_top_faces(..., along=X) keeps cap grain along the wall.
- vki_tim_body_finish(k, L) must be the last call before vki_wobble in any Timber wall builder. It adds the DRESS footing, oak body tops and joint plugs, and T2/T3 rely on every piece having it.
- Leaf data:
  - VKI_LEAF_Y0 0.004, VKI_LEAF_T 0.08, VKI_LEAF_STRAP_X0 0.10.
  - Placement is unchanged: door origin + R(rot) @ (0.33, -T/2 + 0.05), same rotation; ajar = rot - deg.
  - New meta vki_leaf_open_dir.
- vki_gen_blocks(rows=, vrange=, warm_amp=): the defaults keep the old output unchanged, so AshlarIn is unaffected.

BLENDER STATE (not saved)
- Masters rebuilt; M_VKI_GlowIn, M_VKI_Window_Day, M_VKI_ApronCobble, M_VKI_Flag and M_VKI_FlagWarm re-applied; T_VKI_Flagstone regenerated and packed.
- VKI_LookTest is left in its Day base build (FlagRustic hall, doorway mats, new camera metadata).
- VKI_Test: the C3 rigs were rebuilt, plus the known-bad/control rigs VKI_Rig_FixR1_T11, _T4Bad, _T4Good, _T4BadRay and _Leaf90 at y -81.
- VKI_Key.use_shadow = True (restored).
- VKI_Review_Tech and the review render folders were not touched.
- The old renders in renders/interior/VKI_LookTest are stale (old camera, old materials).

## Core fix round (latest: overrides the sections above where they differ)

For the package engineers (Stone / Wattle / Ashlar / Board and the assembler). Full detail is in INTERIOR_SPEC.md §10.

1. END-PLANE RULE
- VKIKit.finish deletes the outward faces of every vki_class 'wall' piece in its planes x=0 and x=L. This is automatic for every family; do not build end faces yourself.
- Consequences:
  - T2 (identical end profiles) is what closes butt joints.
  - T7 accepts one-face edges only in those two planes.
  - A free wall end without a post is a T12 ERROR (vki_t12_posts runs at object level on any scene).
  - T4 now checks that the post covers the open end outline.

2. NEW TEST T5S (vki_t5s_self_coplanar, part of vki_test_pieces)
- Two same-facing faces of ONE master that lie in one plane and overlap by more than 1e-6 m2 fail, even when buried. Only wall end planes are exempt.
- How to satisfy it:
  - Tuck butting members 5 mm into the member they meet (VKI_TIM_TUCK pattern: stud tops into caps, cripple bottoms into lintels, sole ends under jambs).
  - Or separate flush faces by at least 5 mm (e.g. a sloped rafter at +-0.275).
  - Or trim one member.
- T5S uses exact polygon clipping. A bounding-rectangle scan still flags curved strips (the 150B brace); T5S is the reference.

3. T4 (use vki_t4_rigs + vki_t4_coverage for your family)
- The post must cover a FIXED node square: +-POST_HW at L/T/X, and at steps / free ends the Mid square (+-MID_HW along the wall x +-POST_HW across).
- Wall vertices in the square, and uncovered end-plane vertices, must lie inside the post with a 0.005 margin.
- A ray grid over the square must hit the post first.
- The post must be centred on the node; an off-node post reports 'no post'.
- Build the FamStep and PintoO rigs (PKG-S).

4. PLACEMENT
- vki_place wall_floor hug clamps at post squares and at inferred Corner posts on back-wall junction nodes (POST_HW + 0.005 from the side wall line). It records vki_hug_limit, or sets vki_hug_fail when a post or junction lies inside the prop's span.
- Assembler: skip rhythm Mid posts where a wall-backed prop spans the node, or place props before posts.
- Floor-prop hug (hug=True on floor props) still only clears walls, not posts.

5. METADATA AND REBUILDS
- vki_rebuild refreshes instance metadata. Keys in VKI_PLACEMENT_KEYS / _PREFIXES survive; add a key there if you invent a new placement-only property.
- T10i (in vki_test_all) compares every instance with its master.
- Door pieces use vki_nav 'door' + vki_nav_open [x0, x1]. BFS should use vki_collider.
- Leaves: vki_leaf_width is the measured plank width (0.83) and vki_leaf_clearance is 0.005.

6. CAMERA
- vki_fit_camera(bounds, family) is §1 with the 0.4 m far margin (Ashlar gets none). Store its D / target in VKI_Root / scene vki_cam_dist / vki_cam_target, or set scene vki_room_bounds + vki_family and vki_shot fits by itself.

7. G1 DECISIONS AND LEVELS
- The decisions live in VKI_G1 (vki_core); the switches stay: pillar, leaf_deg, VKI_FLAGS, VKI_Key.use_shadow, VKI_NIGHT_SPEC.
- Measure levels with vki_lt_levels(path); for other scenes, reuse vki_cam_ray / vki_floor_luma_world with your own boxes.
- vki_shot flushes lights. Anything that renders outside vki_shot must call vki_flush_lights first.
- The shared VKI_Key / VKI_Fill now rest at the new Day values.

8. TIMBER SWITCHES
- VKI_TIM_REVEAL ('limewash' default | 'planks' | 'cap') and VKI_TIM_POST_TOP ('endgrain' default, padded fill VKI_TIM_POST_FILL 0.26 | 'cap').
- Other families should use vki_endgrain_fit with a padded fill for their post tops.
- Other families' Cut doors should also give the reveal a plaster / mid-value face and a DRESS threshold.

9. CATALOG (coordinator)
- Isolated walls in the VKI_Catalog pieces row now have open end planes. They are barely visible at catalog scale (catalog_pieces_walls.png); add Mid posts at their ends if wanted.
- In VKI_Catalog_Room, T5 flags SM_VK_Prop_Crates_inst.016: it pokes through the east wall near x 6.1-6.2, with bottoms coplanar with the sole plate at z 0. It was already there; the placement is yours.
- I did not modify VKI_Catalog. Its instances only received refreshed master metadata through vki_rebuild.
