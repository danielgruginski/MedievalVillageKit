export const meta = {
  name: 'village-expansion-design',
  description: 'Design panels for marching-squares terrain tiles, new village buildings/features, and the stone texture rework',
  phases: [
    { title: 'Propose', detail: 'independent proposals per track from different angles' },
    { title: 'Judge', detail: 'score proposals and synthesize one concrete spec per track' },
  ],
}

const ROOT = 'C:/Users/danie/AppData/Roaming/Claude/scratch-workspaces/ec03f06b-60f5-4d5d-94a9-dff3a56c5f56/f8ddc2b6-f8a4-41c6-98db-14b97d4348ea/scratch-2026-09-23-d49817'

const CONTEXT = `
PROJECT CONTEXT (read carefully):
We are building a stylized, hand-painted "World of Warcraft"-like medieval village asset kit for a COLONY-SIM game (target engine: Unity). Everything is generated procedurally in a live Blender 4.4 instance with Python (bpy/bmesh + numpy texture generators). You cannot run Blender yourself; your job is DESIGN ONLY (text output). The implementer (me) will build it.

Code (exported from the .blend, read-only reference) lives in ${ROOT}/code/:
 - vk_helpers.py (large; kit geometry: class Kit with box()/quad()/project()/finish(), constants CELL=3.0 m grid, H1=3.0 ground-floor height, H2=2.8 upper-floor height, HB=4.2 barn wall height, HC=4.5 chapel; wall modules are 3 m wide, centered on the cell edge, OUTER face toward local -Y; houses are 2 cells deep (6 m); roofs are per-3 m-bay pieces (Roof_Mid, Roof_Gable, Roof_Hip, Roof_LCorner, thatch variants); material slots via kit_mats() and index constants (STONE, PLASTER, WOOD, ROOF, WINDOW, ... ROCK, MOSS, LEAVES ...); place_v() instances a piece; build_house_v()/build_L_v()/build_townhall()/build_tavern()/build_bakery()/build_barn()/build_stable()/build_chapel()/build_windmill()/build_guardtower() assemble buildings; random_style(seed) picks plaster/shutter/roof colors).
 - vk_tex.py: numpy texture toolkit: grid(), fbm() (tileable FFT noise, ax/ay elongation), blur(), smooth(), voronoi(x,y,pts,sx,sy) -> F1,F2,ID (tileable), normal_from_height(), cavity_ao(), painted_light(), draw_segments(), crack_segments(), write_set(prefix, albedo, height, rough, depth_m, tile_m) -> writes _BC,_N,_H,_R,_AO maps.
 - vk_texgen.py: the texture generators (gen_stone, gen_ashlar, gen_plaster, gen_wood, gen_planks, gen_roofs, gen_thatch, gen_rock, gen_moss, barks, ...).
 - vk_mat.py: pbr_material() builds Principled materials from a texture set; mossy_material() blends moss onto upward-facing surfaces via world normal Z.
 - vk_nature.py: nature kit (trees, bushes, rocks via boulder(), pond, etc.).
 - kit_pieces.txt: list of all existing kit pieces (146).
Existing renders you can LOOK AT with the Read tool (they are PNG images): ${ROOT}/nature_town_aerial.png, ${ROOT}/town_plaza.png, ${ROOT}/town_street.png, ${ROOT}/town_detail.png, ${ROOT}/catalog_walls.png, ${ROOT}/catalog_roofs.png, ${ROOT}/catalog_props.png, ${ROOT}/village_special_buildings.png, ${ROOT}/nature_glade_hero.png.
The current rubble-stone texture (used on ground-floor walls, foundations, chimneys, wells): ${ROOT}/VillageKit/Textures/T_VK_Stone_BC.png (base color), T_VK_Stone_N.png (normal), T_VK_Stone_H.png (height). Tile = 3.0 m per texture repeat.
Existing buildings: cottages (1-3 floors, stone or plaster ground floor, timber upper floors, tile/thatch/hip roofs, dormers, porches, balconies, oriel windows, exterior stairs, awnings), L-shaped houses, town hall with arcade + clock cupola, tavern, blacksmith (lean-to workshop), bakery (bread oven), barn, stable, chapel + bell tower, windmill, guard tower, market stalls, well, fountain, graveyard set, farm plots, fences, lots of props, and a nature pack (13 trees, bushes, rocks, pond, stone circle).
`

const TRACKS = [
  {
    key: 'terrain',
    brief: `TRACK: TERRAIN TILE KIT. The user said: "For the terrain we will do tiles that fit in a marching square system, connecting them by their corners." Design a marching-squares (dual-grid) terrain tile kit: data lives on grid CORNERS, each tile's mesh is chosen from its 4 corner states. Must tile seamlessly with the village kit. Your spec must be concrete and implementable: tile size (relate it to the 3 m building grid), corner-state semantics (height levels? terrain types? both?), exact list of unique meshes per set (count cases incl. rotations/mirrors, name each: e.g. Full, Corner, Edge, Saddle/Diagonal, InnerCorner, Empty), the rotation convention and a lookup table from 4-bit corner mask to (mesh, rotation), SEAM RULES (what exactly must be identical along an edge that only depends on its two corners; where the transition crosses the edge; the fixed cross-section profile), how to add hand-made irregularity/noise WITHOUT breaking seams (e.g. displacement faded to zero at edges, or position-hashed deterministic noise), how multi-level heights stack (cliff tiers), UV/texture strategy so grass/rock textures stay continuous across tiles and rotations (e.g. world-space planar UVs baked from world position / tile-local UVs aligned to world axes before rotation), which sets to build first (e.g. grass-cliff height set, water/shore set, dirt-path set), variants per case to avoid repetition, polycount budget, what textures/materials are needed (grass top, cliff rock face with strata, dirt, sand, water), how buildings/props sit on tiles, and an automated seam-verification test the implementer can run in Blender (assemble random corner grids, compare shared-edge vertices).`,
    angles: [
      'You are a COLONY-SIM SYSTEMS DESIGNER and Unity integrator: prioritize gameplay readability, pathing/walkability, building placement, simple data model, runtime lookup tables, and what the engine needs.',
      'You are a STYLIZED ENVIRONMENT ARTIST (WoW / Warcraft III look): prioritize chunky readable cliffs with painted rock strata, grassy overhanging lips, soft rounded shapes, shoreline sand and water edges, and avoiding visible tiling repetition.',
      'You are a TECHNICAL ARTIST obsessed with seams: prioritize exact edge-profile math, deterministic displacement, vertex placement on tile borders, normals continuity across tiles, UV continuity under rotation, tri budgets, and a verification harness.',
    ],
  },
  {
    key: 'buildings',
    brief: `TRACK: NEW HOUSE TYPES AND VILLAGE FEATURES. The user said: "Keep working on features, you can expand the types of houses and new features for the village." Propose new building types and village features that would most expand the kit's usefulness for a medieval colony sim, in the established style. For each item give: name, gameplay role, visual description, the NEW modular pieces it needs (reusable elsewhere), which EXISTING pieces it reuses, rough footprint in 3 m cells, and effort (S/M/L). Also propose new house TYPES/variants (e.g. poor hovel/cruck cottage, stone merchant house, tower house, longhouse, rowhouse terrace with shared walls, corner house) and new modular pieces that unlock many variants (e.g. water wheel, dock/pier modules, bridge, town wall set in this style, stone stair, cellar door, shop front, jettied corner, skylight, wooden gallery). Keep items feasible to generate procedurally with boxes/lathes/tubes/cards in Python.`,
    angles: [
      'You are a COLONY-SIM GAMEPLAY DESIGNER: think production chains and needs (food, wood, stone, cloth, health, faith, storage, housing tiers) and what buildings a player needs to see.',
      'You are a MODULAR KIT ARCHITECT: maximize reuse; propose the smallest set of new modular pieces that unlocks the largest number of distinct buildings; care about grid alignment and seams.',
      'You are a VISUAL STORYTELLING / LEVEL ART lead: think about what makes the village feel alive and varied from the typical colony-sim camera (high 3/4 view): silhouettes, color accents, signage, landmark buildings, water features.',
    ],
  },
  {
    key: 'stone',
    brief: `TRACK: STONE TEXTURE REWORK. The user said: "Rework the stone texture." LOOK at T_VK_Stone_BC.png, T_VK_Stone_N.png and the renders town_detail.png / town_street.png / catalog_walls.png (Read the images). Read gen_stone() in vk_texgen.py and the helpers in vk_tex.py. Critique what is wrong with the current rubble stone (be specific: shapes, proportions, surface noise, mortar, color, lighting, how it reads at game camera distance and up close), then propose a concrete procedural recipe (numpy, using the existing helpers where useful) for a much better hand-painted WoW-style stone wall texture: stone layout algorithm (coursed rubble? irregular polygons? size distribution), per-stone facets/bevels, painted highlight/shadow, color palette with hex/RGB values, mortar treatment, cracks/chips/moss, height map design for the normal map, roughness, tile size, and pitfalls. Also say whether separate variants are worth making (e.g. a cleaner "cut stone" and a rougher "field stone").`,
    angles: [
      'You are the ART DIRECTOR of a WoW-style game: judge readability, color, stylization and charm; give strong visual direction.',
      'You are a PROCEDURAL TEXTURE ENGINEER: give an implementable step-by-step numpy algorithm with parameter values that works with the given helper functions and stays tileable.',
    ],
  },
]

const results = await pipeline(
  TRACKS,
  (t) => parallel(t.angles.map((angle, i) => () =>
    agent(`${CONTEXT}\n\n${t.brief}\n\nYOUR PERSPECTIVE: ${angle}\n\nWrite a thorough but concrete proposal (markdown). Use exact numbers. Where you reference existing code, name the functions. Do not write full implementation code; short pseudocode is fine.`,
      { label: `propose:${t.key}:${i + 1}`, phase: 'Propose' }))),
  (proposals, t) => agent(`${CONTEXT}\n\n${t.brief}\n\nBelow are ${proposals.filter(Boolean).length} independent proposals from different perspectives.\n\n${proposals.filter(Boolean).map((p, i) => `===== PROPOSAL ${i + 1} =====\n${p}`).join('\n\n')}\n\nYou are the JUDGE. First, briefly score each proposal (1-10) on: concreteness, correctness/feasibility, fit to the WoW-style colony-sim kit, and risk. Then SYNTHESIZE a single final spec that takes the winner as the base and grafts the best ideas from the others, resolving contradictions explicitly. The final spec must be directly implementable in Python/Blender by one engineer: exact numbers, ordered build list (highest value first), acceptance tests / visual checks. Point out any claim in the proposals that is wrong. Output markdown.`,
    { label: `judge:${t.key}`, phase: 'Judge' }),
)
return TRACKS.map((t, i) => ({ track: t.key, spec: results[i] }))
