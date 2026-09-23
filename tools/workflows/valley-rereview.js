export const meta = {
  name: 'valley-rereview',
  description: 'Re-review the rebuilt valley town: confirm the 33 earlier issues are fixed and find regressions, then adversarially verify new findings',
  phases: [{ title: 'Review' }, { title: 'Verify' }],
}
const ROOT = 'C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817'
const COMMON = `
You are reviewing a procedural WoW-style medieval valley town built in a live Blender 4.4 session (Blender MCP tool mcp__blender__execute_blender_code; load it with ToolSearch "select:mcp__blender__execute_blender_code").
Read first: ${ROOT}\\code\\VALLEY_MAP.md (map guide, coordinates, how to render with shot()). Earlier review findings (33 issues, each with LOC and FIX): ${ROOT}\\code\\review_confirmed.txt. Generator source: ${ROOT}\\code\\vk_town_map.py (read it to know the new layout and passes).
The map was just rebuilt with fixes: gate centred on the road with a level-2 apron and the ramp moved to row 22; per-object clash test (spatial hash) for buildings, walls, towers, gatehouse; occupancy of the wall band; tree spacing and willow rules; door keep-clear pass; props-on-wrong-level pass; worn ground; kitchen gardens; district roof palettes + roof desaturation + per-instance jitter; west quarter rotated to face a new street on row 30 with a new west postern piece SM_VK_TownWall_Postern; chapel rotated with a forecourt; quarry between level-4 shoulders; footbridge moved onto the west road with bank ramps; mill inlet ramp; lake reshaped (superellipse, one sand cell from the east edge) with a fisher ramp; training yard, tannery, brewery, terrace, blacksmith moved; biplanar cliff sampling; water material reworked; grass desaturated; a shadowless fill light VK_Fill added.
NOT in your scope: tree/willow/birch/pine/hydrangea MESH quality (another agent is rebuilding those meshes right now) - ignore how trees look, but DO check tree placement.
Rules: read-only. Only render with shot() into ${ROOT}\\renders2\\rereview\\<your lens> and inspect data with read-only Python. Never move/add/delete objects, never change materials, never save. Keep each Blender call short (< 60 s); others share Blender. Look at every render you make with the Read tool.
Be concrete: every claim needs world coordinates or object names and a render path or a numeric check.`
const LENSES = [
  { key: 'ground', ids: '1,4,6,12,17,19,21,25,26,28', focus: 'terrain, ramps, stairs, cliffs, water edges, roads/paths continuity, props on cliffs/ramps' },
  { key: 'build', ids: '2,3,5,11,14,16,18,20,22,24,31,33', focus: 'building placement, clashes between buildings/walls/towers/gatehouse/props, doors blocked, facing of fronts to streets, anything floating or sunk' },
  { key: 'art', ids: '7,8,9,13,15,30,32', focus: 'colour palette, roofs, grass, water, readability from a colony camera (~40 m away, 50 deg pitch), composition' },
  { key: 'play', ids: '1,5,6,10,16,17,19,26,27', focus: 'walkable access for colonists: can every building door be reached by a continuous walkable path (no cliffs, no water) from the main road? postern, footbridge, fisher hut, quarry, mill, chapel' },
]
const REVIEW_SCHEMA = { type: 'object', properties: {
  issue_status: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'integer' }, status: { type: 'string', enum: ['fixed', 'partial', 'not_fixed'] }, evidence: { type: 'string' } }, required: ['id', 'status', 'evidence'] } },
  new_findings: { type: 'array', items: { type: 'object', properties: {
    title: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] }, location: { type: 'string' },
    evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['title', 'severity', 'location', 'evidence', 'fix'] } },
}, required: ['issue_status', 'new_findings'] }
const VERIFY_SCHEMA = { type: 'object', properties: {
  verdicts: { type: 'array', items: { type: 'object', properties: {
    title: { type: 'string' }, real: { type: 'boolean' }, reason: { type: 'string' } }, required: ['title', 'real', 'reason'] } },
}, required: ['verdicts'] }

const results = await pipeline(LENSES,
  l => agent(COMMON + `
Your lens: ${l.key} (${l.focus}).
1) For each earlier issue id in [${l.ids}] from review_confirmed.txt, decide fixed / partial / not_fixed with evidence (render and/or numeric check at the issue's LOC; note many objects moved, so re-locate them).
2) Hunt for NEW problems (regressions) in your lens anywhere on the map, especially around the changed areas. Report only concrete, visible or measurable defects with a cheap concrete fix. At most 8 new findings, most important first.`,
    { label: `review:${l.key}`, phase: 'Review', schema: REVIEW_SCHEMA }),
  (rev, l) => {
    if (!rev || !rev.new_findings.length) return { lens: l.key, rev, ver: null }
    return agent(COMMON + `
You are an adversarial verifier. Another reviewer (lens ${l.key}) claims these NEW defects. For each, try to REFUTE it by checking the scene yourself (render the location, measure). Mark real=false if it is not reproducible, is subjective, is outside the stated scope (tree mesh looks), or the evidence is wrong. Default to real=false when uncertain.
Claims:
` + JSON.stringify(rev.new_findings, null, 1), { label: `verify:${l.key}`, phase: 'Verify', schema: VERIFY_SCHEMA })
      .then(ver => ({ lens: l.key, rev, ver }))
  })
return results
