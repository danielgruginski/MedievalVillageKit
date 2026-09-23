export const meta = {
  name: 'village-kit-buildings-continue',
  description: 'Resume the 8 building agents (interrupted by a usage limit) to finish, polish and report their kit modules',
  phases: [{ title: 'Continue', detail: 'humble, frontier, construction, skyline, town, water, industry, defence' }],
}
const ROOT = 'C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817'
const AGENTS = [
  { a: 'humble', p: 'hum_', focus: 'wattle-and-daub family (2.4 m), cruck thatch gable, thatch vent, lean-to, livestock + animal props, Hovel / Longhouse / pig sty / sheepfold builders.' },
  { a: 'frontier', p: 'fro_', focus: 'log-cabin family, plank shed family, open post bays, S roof family (3 m deep, prefixed context manager restoring HALF/EAVE/RIDGE/GX), log cabin / woodcutter / forester / granary / storehouse builders.' },
  { a: 'construction', p: 'con_', focus: 'construction stages (sites, foundations, half walls, frames, roof frames, scaffolding), piles at 3 fill levels, stockpile border, settler camp and early work props; construction-site (stages 0-2 next to a finished house), camp, stockpile and sawpit builders.' },
  { a: 'skyline', p: 'sky_', focus: 'roofline variety: single-bay roofs, gable/party chimneys, vents, flush/stepped/hoist gables, firewall, half-hips, cross gable, hatch/skylight, bellcote, trade emblems, banners, bunting; build_skyline_street showing 6-8 varied houses. Roof pieces must join SM_VK_Roof_Mid exactly at x=+-1.5.' },
  { a: 'town', p: 'twn_', focus: 'StoneUp/PlasterUp upper-floor families, shop fronts + goods, pent roof, passage + vault, galleries, corner turret stack, stoop / external stair / cellar hatch; merchant house, gable-front townhouse, corner house, terrace builders.' },
  { a: 'water', p: 'wat_', focus: 'water set on datum bank 0 / water -0.6 / bed -1.5 / piles -3.0: piers, boats, timber + stone bridges, quays, animated water wheel, mill pieces, fishing props (NET alpha), lavoir, fountain, pump; watermill, fisher hut, smokehouse, lavoir, riverside demo builders.' },
  { a: 'industry', p: 'ind_', focus: 'production chains: mine + rails + cart + ore/coal piles, quarry faces/floor, treadwheel crane, charcoal mound, bloomery, bellows, bottle kiln, clay pit, potters wheel, bricks, tanning, dye vats (liquid CLOTH_A), cloth rack, loom, spinning wheel, hides/wool piles, oast kiln, mash tun, cider press, skeps, herb bundles, cauldron, drying racks, dovecote; mine, quarry yard, charcoal burner, tannery, dyers yard, brewery, apiary, pottery builders.' },
  { a: 'defence', p: 'def_', focus: 'palisade set, stone town wall modules (walk 6.2, crenellations), corners, stair, step, ruin, round tower, gatehouse + portcullis + gate leaves as separate pieces, parapets, pyramid/cone roofs, training props, market cross, maypole, stage, stocks, pillory, low-wall gate arch, hedge; palisade demo, town wall demo, fortified tower house, training yard, festival green builders.' },
]
const SCHEMA = {
  type: 'object',
  properties: {
    module_path: { type: 'string' },
    text_name: { type: 'string' },
    pieces: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' }, description: { type: 'string' }, flags: { type: 'string' }, tris: { type: 'number' }, bbox: { type: 'string' } },
      required: ['name', 'description'] } },
    builders: { type: 'array', items: { type: 'object', properties: {
      signature: { type: 'string' }, description: { type: 'string' }, footprint: { type: 'string' } }, required: ['signature', 'description'] } },
    renders: { type: 'array', items: { type: 'string' } },
    integration_notes: { type: 'string' },
    unfinished: { type: 'array', items: { type: 'string' } },
  },
  required: ['module_path', 'text_name', 'pieces', 'builders', 'renders', 'integration_notes', 'unfinished'],
}
phase('Continue')
const results = await parallel(AGENTS.map(ag => () => agent(
`You are the "${ag.a}" building agent (module prefix "${ag.p}") in a multi-agent Blender workshop. A previous run of YOU was interrupted by an account usage limit after a lot of good work. DO NOT start over - continue from the existing state.

1. Re-read the rules: ${ROOT}\\code\\AGENT_BRIEF.md (hard rules protect other agents' work - follow them strictly) and your section "## ${ag.a}" in ${ROOT}\\code\\WS_MANIFEST.md. Spec sections are in ${ROOT}\\code\\full_judge_buildings.md.
2. Recover your state:
   - your module source ${ROOT}\\code\\ws_${ag.a}.py (source of truth, but it may be mid-edit: it can differ from the Blender text ws_${ag.a}; compare them, decide which is newer/better and make them identical; make sure it executes);
   - your renders in ${ROOT}\\renders2\\${ag.a}\\ (look at the most recent ones with Read to see where you were);
   - your Blender scene WS_${ag.a} with collections WS_${ag.a}_Pieces / WS_${ag.a}_Assembly.
   Use exec(bpy.data.texts["ws_common"].as_string()) then ws_ns / ws_build / ws_grid / ws_shot / ws_stats / ws_clear_assembly as described in the brief. Blender calls are shared with other agents and serialized - keep calls short and retry on communication errors.
3. Finish the work: ${ag.focus} Work down the manifest priority order; finish and polish what exists before adding new pieces. After every render, Read it and fix concrete problems (floating/intersecting parts, seams between modules, scale vs a 1.8 m person, flat silhouettes, z-fighting, stretched textures, style mismatch with the existing hand-painted WoW-style kit). Keep grid conventions (3 m modules, outer face -Y, corners at origin facing -X/-Y, roofs placed at wall top, origin on the ground).
4. Before finishing: (a) ${ROOT}\\code\\ws_${ag.a}.py identical to the Blender text; (b) in ONE fresh call: exec(ws_common); g=ws_ns("${ag.a}"); ws_build("${ag.a}", g=g) builds every WS_SPECS piece with no error; (c) run every builder once into your assembly without error; (d) render catalog_final.png and 1-3 hero_*.png at 1600x900 (one of them a high colony-camera view). Never save the .blend, never touch shared texts or other agents' scenes/objects.

Return the structured report: pieces (with tris/bbox from ws_stats), builders (signature, what, footprint in cells), final render paths, integration notes (dependencies on other agents' pieces, suggested sockets, anything the integrator must know), and an honest unfinished list.`,
  { label: `continue:${ag.a}`, phase: 'Continue', schema: SCHEMA }
)))
return results.map((r, i) => ({ agent: AGENTS[i].a, report: r }))
