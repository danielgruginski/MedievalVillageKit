export const meta = {
  name: 'village-kit-buildings',
  description: 'Eight parallel building agents extend the Blender village kit (each in its own WS_ scene/module)',
  phases: [{ title: 'Build', detail: 'humble, frontier, construction, skyline, town, water, industry, defence' }],
}
const ROOT = 'C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817'
const AGENTS = [
  { a: 'humble', p: 'hum_', focus: 'Early-game housing: the wattle-and-daub wall family (wall top 2.4 m), cruck thatch gable, thatch smoke vent, lean-to, livestock and animal props, then the Hovel, Longhouse, pig sty and sheepfold builders. Existing thatch roof pieces (see kit_pieces.txt: SM_VK_RoofThatch_*) are placed at the 2.4 m wall top; check the eave height stays sensible and doors are only on gable ends. Livestock must be charming chunky WoW-style animals (not blobs): readable heads, ears, legs, tails, colour patches.' },
  { a: 'frontier', p: 'fro_', focus: 'The log-cabin wall family (3.0 m, interlocking corners with end grain), the plank shed family (2.6 m), open post bays, and the S roof family (3 m deep, ridge 2.27) implemented with a prefixed context manager that temporarily switches HALF/EAVE/RIDGE/GX and restores them in finally. Then log cabin, woodcutter lodge, forester hut, granary on staddle stones and storehouse builders.' },
  { a: 'construction', p: 'con_', focus: 'Construction stages and stockpiles (spec M1): build sites, foundations, half-built walls, timber frames, roof frames (rafters that exactly follow the existing roof profile so frames sit where Roof_Mid/Roof_Gable go), scaffolding, piles of logs/planks/stone/sacks at 3 fill levels (each within 2.9x2.9x1.6), stockpile border, plus the settler camp (tents, campfire with GLOW, covered wagon) and early work props. Builders: a 3x2 two-storey cottage at stages 0,1,2 side by side next to a finished one (use existing SM_VK_Wall_Stone*, Corner_Stone, Wall_Timber*, Roof_* pieces for the finished parts), camp, stockpile yard, sawpit yard.' },
  { a: 'skyline', p: 'sky_', focus: 'Roofline variety (spec M2 + some M4 roofs): single-bay roofs, gable chimneys for several wall heights, party chimney, roof vents, flush / stepped / hoist gables and firewalls, half-hips, cross gables, hatch/skylight bays, bellcote, ridge emblems for trades, banners and bunting. Every roof piece must join the existing Roof_Mid / Roof_Gable exactly at x=+-1.5 (same profile roof_z + roof_sag) - verify by placing it next to SM_VK_Roof_Mid. Finish with build_skyline_street: 6-8 houses built from existing walls with varied roofs (Red/Slate/Shingle/Thatch/Green), end kinds, chimneys and emblems.' },
  { a: 'town', p: 'twn_', focus: 'Town-tier pieces (spec M4): stone and plaster upper-floor families that stack exactly on the 3.0 m ground walls (z=3.0 seam hidden by a belt course), shop fronts with counters/canopies and goods props, pent roof, passage arch + vault, timber galleries, corner turret stack, stone stoop / external stair / cellar hatch. Builders: stone merchant house, gable-front townhouse, corner house with turret, a terrace of 4 units. Use other agents pieces (e.g. SM_VK_Roof_Gable_Stepped from skyline) only through a fallback pick helper.' },
  { a: 'water', p: 'wat_', focus: 'The water set (spec M5) on the datum bank 0 / water -0.6 / bed -1.5 / piles -3.0: pier modules, rowboat and barge (lofted hulls, nice silhouettes), timber and stone bridges (the stone span must look great - WoW arched bridge), quays, animated water wheel as a separate piece with its hub at the origin, mill axle wall, millstone, fishing props (net rack uses NET alpha material), lavoir, wall fountain, hand pump. Builders: watermill, fisher hut, smokehouse, lavoir and a riverside demo; build your own stand-in riverbank + WATER plane in your assembly for the renders.' },
  { a: 'industry', p: 'ind_', focus: 'Production chains (spec M6 minus crops): mine portal + rails + minecart + ore/coal piles, quarry faces (3.0 m high = 2 terrain levels) and floor, treadwheel crane, charcoal mound, bloomery with GLOW, bellows, bottle kiln, clay pit, potters wheel, brick piles, tanning pit, hide frame, dye vats (liquid in CLOTH_A so style recolours it), cloth rack, loom, spinning wheel, hide and wool piles, oast kiln with white cowl, mash tun, cider press, skeps and bee bench, herb bundles, cauldron, drying racks, dovecote. Builders for mine, quarry yard, charcoal burner, tannery, dyers yard, brewery, apiary, pottery.' },
  { a: 'defence', p: 'def_', focus: 'Defence and civic (spec M7 + M8): palisade set (pointed logs, walk, gate with separate leaf, tower, beacon), stone town wall 3 m modules with walk at 6.2 and crenellations, corners, stair, step, ruin, round tower, gatehouse block with portcullis and gate leaves as separate pieces, parapets, pyramid and cone roofs, training props, market cross, maypole, stage, stocks, pillory, low-wall gate arch, trimmed hedge. Builders: palisade demo ring with gate and towers, town wall demo with gatehouse and tower, fortified tower house, training yard, festival green.' },
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
phase('Build')
const results = await parallel(AGENTS.map(ag => () => agent(
`You are the "${ag.a}" building agent (module prefix "${ag.p}") in a multi-agent Blender workshop.

FIRST read these files completely and follow them strictly:
- ${ROOT}\\code\\AGENT_BRIEF.md   (rules, API, workflow - the hard rules protect other agents' work)
- ${ROOT}\\code\\WS_MANIFEST.md   (your exact piece names and builder signatures under "## ${ag.a}", and what the other agents build)
Then read the spec sections named for you in the manifest inside ${ROOT}\\code\\full_judge_buildings.md, skim ${ROOT}\\code\\vk_helpers.py for the helpers you will reuse, check ${ROOT}\\code\\kit_pieces.txt, and look at a few reference renders in ${ROOT} (catalog_*.png, town_street.png, town_aerial.png, village_special_buildings.png) with the Read tool.

Your agent name is "${ag.a}": your scene is WS_${ag.a}, your Blender text is ws_${ag.a}, your local module file is ${ROOT}\\code\\ws_${ag.a}.py, your renders go to ${ROOT}\\renders2\\${ag.a}\\ (via ws_shot).

Focus: ${ag.focus}

Quality bar: this must look like a polished stylised game asset kit in the World-of-Warcraft hand-painted style, consistent with the existing kit. Iterate with renders (Read every PNG you render and critique it concretely, at least 3 improvement rounds on the key pieces). Prefer finishing fewer pieces well over many rough pieces; work down the manifest priority order. Keep pieces grid-correct (3 m modules, origins per the conventions) and snapping with existing pieces (test by placing them next to existing kit pieces in your assembly).

Before you finish: (1) make sure ${ROOT}\\code\\ws_${ag.a}.py is identical to the Blender text ws_${ag.a}; (2) in ONE fresh call run exec(ws_common); g=ws_ns("${ag.a}"); ws_build("${ag.a}", g=g) and confirm every WS_SPECS piece builds without error; (3) run each builder once into your assembly without error; (4) produce catalog_final.png and hero renders at 1600x900. Never save the .blend, never touch shared texts or other agents' scenes.

Return the structured report (pieces with tris/bbox from ws_stats, builders, render paths, integration notes incl. suggested sockets, and an honest list of unfinished items).`,
  { label: `build:${ag.a}`, phase: 'Build', schema: SCHEMA }
)))
return results.map((r, i) => ({ agent: AGENTS[i].a, report: r }))
