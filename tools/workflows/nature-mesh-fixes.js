export const meta = {
  name: 'nature-mesh-fixes',
  description: 'Fix willow, birch, pine and hydrangea meshes in the Blender village kit, then critique via renders',
  phases: [{ title: 'Implement' }, { title: 'Critique' }, { title: 'Fix' }],
}
const ROOT = 'C:\\Users\\danie\\AppData\\Roaming\\Claude\\scratch-workspaces\\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\\scratch-2026-09-23-d49817'
const CONTEXT = `
You work on a procedural, hand-painted WoW-style medieval village kit that lives in a live Blender 4.4 session.
- Drive Blender with the MCP tool mcp__blender__execute_blender_code (load it first with ToolSearch "select:mcp__blender__execute_blender_code"). Every call is a fresh Python namespace.
- Loader (gives one namespace with every kit function incl. nature): 
    import bpy; exec(bpy.data.texts["vk_kit"].as_string()); g=vk_kit_ns()
  After exec, g["make_willow"], g["nk_finish"], g["Kit"] etc. are available (vk_nature and vk_leafgen are loaded by it).
- Source of truth: local files ${ROOT}\\code\\vk_nature.py and ${ROOT}\\code\\vk_leafgen.py mirror Blender texts "vk_nature" and "vk_leafgen". Edit the LOCAL file with your file tools, then push it: bpy.data.texts["vk_nature"].from_string(open(r"<path>",encoding="utf8").read()).
- Nature masters live in collection VK_NaturePieces (scene VillageKit), hidden, names SM_VK_Tree_Willow, SM_VK_Tree_Birch, SM_VK_Tree_Birch_Single, SM_VK_Tree_Pine_A, SM_VK_Tree_Pine_B, SM_VK_Tree_Pine_Young, SM_VK_Bush_Hydrangea, ... nk_finish(k,name,coll,...) rebuilds a master IN PLACE (old.user_remap(new mesh)) so thousands of existing instances update automatically. Find how each master is generated: search all Blender texts for call sites of make_willow / make_birch / make_pine / make_bush (e.g. [t.name for t in bpy.data.texts if "make_willow(" in t.as_string()]) and reuse exactly the same parameters, seeds, cells and nk_finish arguments when rebuilding.
- Render helper: exec(bpy.data.texts["vk_render"].as_string()) defines shot(name, cam_loc, target, lens=35, res=(1280,720), scene="VillageKit", samples=..., outdir=...) and returns a PNG path; view it with the Read tool. Save renders to ${ROOT}\\renders2\\nature.
- To look at masters, link temporary instances (obj.copy() of the master, or bpy.data.objects.new(name, master.data)) into a temporary collection "VK_TmpNature" under scene VillageKit at world x 900..960, y -320 (empty area), unhide them, render, and DELETE the temporary collection and objects when done. Real in-town examples also exist in collection VK_ValleyTown around world x 1500-1716, y 0-168 (read-only for you).
- Other agents share this Blender (calls are serialized): keep each call short (< ~60 s), never delete or modify anything except the listed nature masters, their materials/leaf atlas, and your temporary collection. NEVER save the .blend file. Do not touch VK_ValleyTown / VK_ValleyTerrain or any SM_VK_ building pieces.
- Style target: WoW-like stylised foliage, chunky readable clumps, readable from a colony-sim camera ~40 m away at 50 degrees pitch.
`
const TASKS = `
Fix these confirmed review issues:
1. SM_VK_Tree_Willow reads as a dark hairy dome: 150 thin hanging "hair" cards over the dome plus a 90-card curtain; the underside renders near-black. Rebuild make_willow as fewer, broader drooping leaf clumps (in the style of the oak's clump_cards leaf clumps, with the "willow" leaf cell) plus a lighter curtain of hanging strands at the rim, keep the overall size (radius ~3.9 m, total height ~5-5.5 m) and trunk, and make the canopy normals spherical (nfn) with brighter AO underneath (aofn floor >= 0.7) so the underside is not near-black. Keep it a recognisable weeping willow.
2. SM_VK_Tree_Birch (and Birch_Single if it uses make_birch): white birch bark on the thin branches/twigs shows as white slashes through the canopy. Keep BARK_BIRCH on the stems/trunks but put the branches on a darker bark slot (e.g. BARK_OAK, or BARK_PINE) - bark_tubes accepts a (trunk_mat, branch_mat) tuple like make_pine does - and/or shorten the branch tubes so their tips stay inside the leaf clumps.
3. SM_VK_Tree_Pine_A / Pine_B (and Pine_Young): brown branch-axis sticks poke through the needle cards. Make the whorl branch tubes thinner and stop them at ~60-70% of their length (the needle cards cover the rest), and/or darken them toward the needle colour.
4. SM_VK_Bush_Hydrangea flowers are over-saturated vivid blue. Reduce saturation (about -35%) and, if cheap, mix in pink/white flower heads. The flowers come from the leaf atlas (vk_leafgen) or a flower cell; find where their colour is defined. If regenerating the atlas is needed, make sure the other atlas cells come out identical (same seeds).
Rebuild only these masters in place. Verify with close-up renders (and one render of real instances in VK_ValleyTown, e.g. willows on the river banks around world (1530-1560, 30-55), birches/pines on the north ridge around (1600-1680, 140-165)).
`
phase('Implement')
const impl = await agent(CONTEXT + TASKS + `
Return a concise report: what you changed (functions, parameters), which masters you rebuilt, before/after render paths, anything left undone.`, { label: 'implement nature fixes', phase: 'Implement' })
phase('Critique')
const crit = await agent(CONTEXT + `
Another agent just changed these nature masters to fix review issues:
` + TASKS + `
Its report:
` + String(impl) + `
Your job: act as a strict art critic. Render close-ups of each changed master (temporary instances as described) from a colony camera (~40 m, 50 deg pitch) AND at eye level, plus real instances in VK_ValleyTown. Judge: does the willow still read as a willow and no longer as a dark hairy dome? any white birch twig slashes left? any pine branch sticks visible through needles? hydrangea saturation OK? any new artifacts (floating cards, holes, black faces, broken normals, missing materials)? Do not edit code.`, {
  label: 'critique renders', phase: 'Critique',
  schema: { type: 'object', properties: {
    ok: { type: 'boolean', description: 'true if all four issues are resolved without new artifacts' },
    problems: { type: 'array', items: { type: 'string' } },
    renders: { type: 'array', items: { type: 'string' } } }, required: ['ok', 'problems', 'renders'] } })
let fix = null
if (crit && !crit.ok && crit.problems.length) {
  phase('Fix')
  fix = await agent(CONTEXT + TASKS + `
A first pass was done:
` + String(impl) + `
A critic found these remaining problems:
- ` + crit.problems.join('\n- ') + `
Fix them (edit the local files, push the texts, rebuild the masters in place), verify with renders, and return a concise report.`, { label: 'fix critic issues', phase: 'Fix' })
}
return { impl, crit, fix }
