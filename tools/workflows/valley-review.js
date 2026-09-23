export const meta = {
  name: 'valley-review',
  description: 'Multi-lens visual review of the valley town + kit in Blender, then a verification/dedupe pass',
  phases: [{ title: 'Review', detail: '4 lenses render and inspect' }, { title: 'Verify', detail: 'confirm + dedupe + prioritise' }],
}
const ROOT = 'C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817'
const LENSES = [
  { k: 'ground', d: 'GROUND CONTACT and TERRAIN: objects floating above or sunk into the ground, props on the wrong level (e.g. on a cliff face or hanging over a lower level), buildings overhanging cliff edges, terrain holes/cracks/seams, water surface gaps or shore artefacts, bridges/ramps/stairs that do not connect to the ground they should (gaps, steps, deck/terrain mismatch), trees growing out of rock faces or buildings, lip grass/rocks floating. Check the river banks, bridges, mill, quay, lake, ramps, stairs, west bench, mine, quarry and the plateau edges.' },
  { k: 'build', d: 'BUILDINGS and KIT INTEGRITY: intersecting / overlapping buildings or props (houses clipping into each other, into walls, into trees), gaps between wall modules or roof bays, missing pieces, z-fighting, wrong rotations (doors facing walls, backs to streets), pieces clearly off the 3 m grid, broken roofs, props inside walls. Check the town interior (plaza, infill houses, terrace, skyline street, chapel, brewery, blacksmith), the gatehouse and walls, hamlet, meadow workshops, construction sites.' },
  { k: 'art', d: 'ART DIRECTION: consistency with the hand-painted WoW style, colour harmony (too many saturated colours, clashing roofs, flat/boring areas), texture scale problems (stretched or tiny textures, obvious tiling), repetition that reads as copy-paste, lighting/material problems (black or white-out materials, over-shiny surfaces), readability from the colony camera (40 m, 50 deg pitch). Render several colony-camera views across the map plus a few eye-level shots.' },
  { k: 'play', d: 'COLONY-SIM LAYOUT and GAMEPLAY READABILITY: can a colonist walk everywhere important (roads leading into walls or cliffs, doors blocked by props/walls/cliffs, gates, ramps and bridges usable, stairs reachable)? Do districts read clearly (farms, industry, town, defence)? Are building functions recognisable from above? Anything that would confuse a player or break pathing on a 3 m grid.' },
]
const ISSUES = {
  type: 'object',
  properties: {
    issues: { type: 'array', items: { type: 'object', properties: {
      title: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
      location: { type: 'string', description: 'world coordinates and/or cell (i,j) and object names if known' },
      evidence: { type: 'string', description: 'render path(s) and what is visible there' },
      suggested_fix: { type: 'string' } },
      required: ['title', 'severity', 'location', 'evidence', 'suggested_fix'] } },
    overall: { type: 'string' },
  },
  required: ['issues', 'overall'],
}
phase('Review')
const reviews = await parallel(LENSES.map(L => () => agent(
`You are a meticulous reviewer (lens: ${L.k}) of a procedural medieval village kit placed on marching-squares terrain in a live Blender scene.
Read ${ROOT}\\code\\VALLEY_MAP.md first (coordinates, districts, how to render READ-ONLY with shot()). Load the Blender tool with ToolSearch "select:mcp__blender__execute_blender_code".
Your lens: ${L.d}
Method: render at least 10 targeted views (mix of wide colony-camera shots and close eye-level shots) into ${ROOT}\\renders2\\review\\${L.k}\\ , Read every render, and also use read-only Python inspection where useful (e.g. compare object bound-box bottoms with the cell level height level*1.5 via the terrain chunk BVH ray casts, find overlapping building bound boxes). Be concrete: every issue needs a location (world xyz or cell i,j and object names when you can get them), evidence (render path) and a specific suggested fix. Do not report things that are fine. Do not modify the scene, never save.
Return the structured list, most severe first (aim for real, verified problems; 5-25 issues).`,
  { label: `review:${L.k}`, phase: 'Review', schema: ISSUES }
)))
phase('Verify')
const all = reviews.map((r, i) => ({ lens: LENSES[i].k, issues: (r && r.issues) || [], overall: r ? r.overall : 'no result' }))
const VERIFIED = {
  type: 'object',
  properties: {
    confirmed: { type: 'array', items: { type: 'object', properties: {
      title: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] }, lenses: { type: 'string' },
      location: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } },
      required: ['title', 'severity', 'location', 'evidence', 'fix'] } },
    rejected: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, reason: { type: 'string' } }, required: ['title', 'reason'] } },
  },
  required: ['confirmed', 'rejected'],
}
const verified = await agent(
`You are the adversarial verifier. Four reviewers inspected a Blender scene (see ${ROOT}\\code\\VALLEY_MAP.md for coordinates and the READ-ONLY render helper; load the Blender tool with ToolSearch "select:mcp__blender__execute_blender_code").
Their raw findings (JSON): ${JSON.stringify(all)}
Task: (1) merge duplicates across lenses; (2) for every high/medium finding, try to REFUTE it: re-render the location yourself (into ${ROOT}\\renders2\\review\\verify\\) and/or inspect geometry read-only; keep it only if you can see it yourself; (3) keep low findings only if clearly real and cheap to fix; (4) order confirmed issues by impact on the final showcase quality. Never modify the scene, never save.
Return confirmed (with merged lenses, precise location, evidence path, concrete fix) and rejected (with reason).`,
  { label: 'verify', phase: 'Verify', schema: VERIFIED })
return { reviews: all, verified }
