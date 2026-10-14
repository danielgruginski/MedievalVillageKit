# Spike: the see-through (branch `spike/seethrough`)

**Ended 2026-10-14:** merged into the kit's `main`, MedievalSetting's side checked in to `/main` as cs:27. The
see-through as it stands: HANDOFF 104. This file is the spike's record (moved to `docs/history/`).

Started 2026-10-13, after a day of see-through rounds landed straight in the kit and the game (HANDOFF 99-103). The
user's call, on a friend's advice: settle the graphics question in a spike -- try things freely, check them against a
fixed set of edge cases, then integrate once.

**The question.** How should the see-through hide what covers the walker and finish what it cuts, so that the hole never
shows geometry it was not meant to show (hollow insides, back faces, pieces overlapping inside a wall, a trunk sliced
lengthways, the grass inside a house)?

## Where things live

| | main line | spike |
|---|---|---|
| Kit (git) | `main` (the spike merged 2026-10-14) | branch `spike/seethrough` (kept on GitHub) |
| MedievalSetting (Plastic) | `/main` (cs:27: the spike's files checked in) | was: pending changes in the workspace + shelveset (last: sh:7) |

While the spike ran, MedievalSetting's side of it was fourteen files left pending on `/main` -- `GameCamera.cs` (hidden check, cut
fields), `ClickToMove.cs` (cut test), `README.md`, `POLISH.md` (notes), the capture tool
`Assets/Game/Scripts/Editor/SeeThroughSpike.cs` (+ .meta, added); round 1's `CreatureSilhouettes.cs` and
`Player/PlayerModel.cs` (the keep mark); the z-fight watch `Assets/Game/Scripts/ZFightWatch.cs` and
`Assets/Game/Resources/ZFightProbe.shader` (+ .metas, added); round 3's baked caps
`Assets/Game/Resources/KitSeeThroughCaps.asset` (+ .meta, added) -- and kept safe in a shelveset, re-shelved after each
round (`cm shelveset create <files> --all -c=...`). Not a branch: switching the shared workspace would shelve and
re-apply every session's pending files (and rewrite them under a running Unity), and other sessions' check-ins would
then land on the spike branch. So: never check those files in to `/main` until the spike ends.

The two go together: the game's spike code needs the kit's spike API (KitSeeThroughProbe, KitSeeThrough.CutY). Back to
the main game (not while Unity plays): `git checkout main` in the kit and `cm undo` the twelve files in MedievalSetting
(they are in the shelveset); back to the spike: `git checkout spike/seethrough` and `cm shelveset apply sh:<n>`.

## What the spike holds (HANDOFF 99-103)

- **Kept so far:** the hidden check (hole only while the walker is hidden, `KitSeeThroughProbe`); a building opens as one
  (CPU decision, rendering layers); loose pieces judged in front by their origin (trunks stay whole beside the walker);
  an open building cut as a whole inside the hole; the cut at 1.4 m over each piece's own base, kept in its rendering
  layer; **real caps** (`KitSeeThroughCaps`: each piece's cross-section, sliced and filled, drawn where the hole opened
  it) -- the most promising answer so far.
- **Tried and dropped:** caps behind the walker (painted the far roof slope over the street), caps over the walker's own
  margin, flat grey back-face caps, an `SV_Depth` lid (buried back faces filled the interiors), loose pieces opened to
  the feet (trees vanished: the obstacle could not be seen).
- **Still in, maybe not needed at the end:** KitLit's back-face `SeeThroughCap` pass (fallback where a piece has no real
  cap).

## Edge cases (the gallery)

Status after the last round. Shots: `reviews/seethrough_2026-10-13/` (summaries) and the user's screenshots.

| # | case | where | status |
|---|---|---|---|
| 1 | tree in front of the walker: canopy hole, capped trunk | Hamlet oak (-41.1, -72.7) | ok |
| 2 | tree beside the walker: trunk whole | Hamlet oak (-40.0, -70.5), blossom (-41.8, -106) | ok |
| 3 | bush beside the walker stays whole | Hamlet (-24.3, -84.5) | ok |
| 4 | overlapping pieces inside a cut wall (fins) | Hamlet chapel north (-35.6, -128.2) | ok with real caps |
| 5 | building beside the walker (no slicing along its line) | Hamlet bell tower (-26.6, -115.4) | ok |
| 6 | houses behind the walker: round hole through roof, chimney, walls | cottage_2, inn, stable | ok |
| 7 | **z-fighting at the cut** (stone house corners, both towns) | Greywall inn, smithy, approach_21 | ok, round 1 |
| 8 | **grass inside a cut building**: a floor where the interior shows | Greywall inn | ok, round 1 (planks) |
| 9 | **stained-glass pane** standing in a cut wall's window | Hamlet chapel window (-31.4, -125.2) | ok, round 1 |
| 10 | **trunk cap with a gap** (a root inside a trunk cut out as a hole) | Hamlet pine (-23.6, -50.6) | ok, round 1 (0 unfilled) |
| 11 | bark caps show bark, not end grain | Hamlet oak, pine | ok, round 1 (rings) |
| 12 | market stall / awning | Hamlet stall | looked at: a low piece not in the way stays (right) |
| 13 | Greywall houses, the town wall ring and its corners | Greywall | ok with real caps |
| 17 | **the gate does not dissolve** (portcullis, timber gallery stay) | Greywall gatehouse (-115, -80) | ok, round 1 |
| 18 | **a building behind the walker opens** (user shot 4: a vat hid the player, the barn behind him opened too) | every Greywall building, a vat planted before the walker | ok, round 2 (probe tags) |
| 19 | **z-fighting away from the cut**: kit meshes with two faces in one plane, painted differently | Greywall apothecary (-152, -180), chapel, wizard's tower | round 2: 15 pieces fixed (also on main); smaller ones left (below) |
| 14 | a building on a terrain tier, a porch, an outside stair | Greywall keep (on a tier, outer stair), windmill (tier), apothecary stair, main_n_2 porch | ok, round 3: the walker up a stair stood over a hole (the keep) -- a cut never lies under the walker's feet now |
| 15 | interiors, dungeons, sewers (no KitVillage: no caps, no groups) | Greywall_Inn's interior (8 spots), Greywall_Sewer (8 spots) | ok, 2026-10-14: walls low or pre-cut, nothing hides the walker, the hole stays shut (spots warped into the sewer's rock fill, unreachable, open a hole round the walker, as they should) |
| 16 | player build: caps were made by an editor hook | every level | ok, round 3 (baked before every build; pooled) |

## Round 1 (2026-10-13 evening)

The user's shots: the gate not dissolving, z-fighting at stone house corners in both towns, the item on the player's back
cut, grass inside cut buildings, plus the open cases 9-11. Before/after captures: MedievalSetting
`Logs/SeeThroughSpike/20261013_210608_Greywall` (before) and `..._212425_Greywall` (after).

- **Gate:** a piece under Props with many meshes (the gatehouse: 44, at their own heights) had each mesh cut over its own
  origin -- the gallery 6 m up was cut at 7.4 m and stayed. Now every mesh is cut over the base of the piece it belongs
  to (`KitVillage.PieceRoot`).
- **Z-fighting at corners:** measured, not guessed (a check over every cap mesh in play). Between pieces the caps were
  already apart; the fight was *inside* one piece's cap: a stone corner's quoin blocks sit embedded in its rubble core,
  so the cut gave two filled outlines in one plane -- 51 of Greywall's 161 cap meshes, 13 m2 doubled (the gatehouse
  alone 11.5). Now caps are stacked by area, larger below: inside a cap each outline 0.5 mm over the larger ones it
  overlaps, and in a building each piece's cap 8 steps over the larger caps it overlaps (a rank pass once its caps are
  made). After: 16 cap meshes with 0.15 m2 still tied (small self-overlaps of single outlines), 2 of 316 overlapping
  piece pairs at the same height. A first try that ranked caps by a depth bias in the shader was dropped (it did
  nothing for the overlaps inside one cap, which were the real ones).
- **Floors:** a house (not an L-shaped generated one) gets a plank floor over its walls' box, a cap of its building,
  drawn only where the hole opens it.
- **Outer loops vs holes** are now told by the faces' own direction, not by nesting: a root's outline inside a trunk's
  was cut out as a hole (case 10). Unfilled outlines in Greywall: 11 -> 0.
- **End grain:** bark caps take `M_VK_EndGrain`, the rings centred on each cut outline.
- **Sheets in a building** (stained glass, ivy, cloth) open down to the feet: no section to cap, their stubs stood in
  the cut.
- **Carried items are never cut:** a new rendering-layer bit (`KitSeeThrough.KeepBit`, 15) set by MedievalSetting on
  everything a character carries (`CreatureSilhouettes.Tag`, PlayerModel's weapon and shield props).
- Seen but right as it is: a low lean-to in front of the player at the Greywall bakery stays inside the hole -- it is
  below the sight line, so it does not hide the player.
- **After, both towns** (Tools > See-through Spike > Check Cap Overlaps): Greywall 16 cap meshes with 0.15 m2 tied
  (was 51, 13 m2), Hamlet 9 with 0.07 m2 (market stalls, chapel walls, bell tower, lean-tos: a centimetre square each);
  overlapping piece pairs at the same height: Greywall 2 of 316, Hamlet 0 of 72. Captures: Greywall `..._212425`,
  Hamlet `20261013_215339_Hamlet`.
- **Carried items:** checked in play -- all 43 of the player's renderers carry the keep bit; but the shields and weapons
  are URP Lit, not KitLit, so the see-through never touched them. The user's shot 4 (an item "on the back of the
  character" cut) shows a big vat in front of the player, cut because it hides him: asked what was meant.
- Noted: in the background the editor spreads cap making over ~10 s of wall time (8 ms a frame at the editor's slow
  background rate); in the focused editor it was ~1 s. Baking at level build removes this.

## The z-fight watch (2026-10-13 night)

The user, after round 1: z-fighting is left "in a lot of little places", mostly not at the cuts; a tool to log it while
playing. MedievalSetting `ZFightWatch` (F8 in play, or Tools > See-through Spike > Z-fight Watch; editor and development
builds only): once a second it draws the game camera's view twice off screen (`Resources/ZFightProbe.shader`) -- the
nearest surface per pixel and the nearest other surface behind it, each with its draw, triangle, view depth, flat normal
and painted brightness, keeping each material's culling, cut-out and the kit's hole. Two surfaces in one plane (normals
within ~6 degrees) under 0.2 mm apart fight; painted 10/255 apart, the fight shows. Spots (pair of renderers per 4 m of
ground) go to `Logs/ZFightWatch/<time>/spots.csv`, the fights first, with a cropped shot of each while in view.

- **Checks:** a duplicated fence planted in play was found at 0.000 mm; the trough's iron band flush on its wood; the
  camera's depth is reversed 32-bit float (near 0.3, far 400), so at 20-25 m it resolves well under 0.1 mm and anything
  that really fights is inside the 0.2 mm band.
- **Bugs met building it:** `CommandBuffer.SetViewProjectionMatrices` wants the camera's own projection (an already
  converted `GL.GetGPUProjectionMatrix` was converted twice: the farther surface won); the game view is wider than
  16:9 (shots and probe now take its shape); a `HideFlags.DontSave` object outlives play mode (one stale watch per
  session).
- **The apothecary** (the user had seen it there), a ring of 12 stops round it: 35 fights, 28 "same look", 16 near. The
  biggest are inside kit meshes: `SM_VK_Wall_StoneUp_Twin` / `_Loading` / `_Door` have a `M_VK_Stone_Warm` face and a
  `M_VK_StoneBlock` face in one plane (the twin window's reveal by the mullion swaps stone when the camera moves 4 mm:
  seen in a zoomed render); the outside stair `SM_VK_Stair_Stone_Ext` against `SM_VK_Wall_StoneUp_Door`; the stepped
  gable against the upper walls; `SM_VK_Roof_Pent` / `Roof_Gable_Stepped` slates over slates. Neighbours: the wizard's
  outside stair base on the ground, the chapel bell tower (`M_VK_Ashlar` over `M_VK_StoneDressed`), a plaster window
  wall's wood frame (`main_n_3`), a thatch gable's wood. Inside the apothecary: nothing within 1 mm.
- Faces that are exact copies (the same triangles twice) tie at bit-equal depth and do not flicker; the apothecary's
  pairs were not copies (depths differ), so they fight as the camera moves. Most fights are small slivers (tens to
  hundreds of probe pixels a sighting), which matches "little places".
- Next: fix the meshes in Blender (pull one face back or delete the hidden copy), piece by piece from the watch's list;
  re-walk with the watch to confirm.

## Round 2 (2026-10-13/14 night)

The user: shot 4's "item on the back" was not the item -- "The vat triggered the transparency, but the barn behind the
player got transparent as well, it didn't had to be transparent, as it was behind the player". And: "You can start
fixing things" (the watch's finds).

- **A building opens only where its own surface hides the walker.** The CPU test asked whether a sight line to the
  walker crossed a piece's *box*: a roof's box is mostly air above its slope, so a barn behind the walker crossed the
  lines (its roof did not) and opened as soon as anything else -- the vat -- opened the hole. Now each building's pieces
  carry a tag (rendering layer bits 8-14, `KitSeeThrough.TagShift`, 1..100); the hidden check's view draws every
  building's pieces that stand in front of the walker above their foot, open or not (`KitSeeThroughCovers`), magenta
  with the tag in green and alpha 0.5 (`KitSeeThroughProbeTag`; alpha marks the kit's pixels, so a pink shirt does not
  count); the read-back counts each tag over the body (`KitSeeThrough.Probed`), and `Building.Decide` opens a building
  while its tag covers 1% of the body (stays while any pixel does, held 0.3 s). Without a recent check (no probe, 1.5
  s) the box test decides as before.
- **Checked:** all 46 reachable Greywall buildings, the walker set 0.7 m before each (camera side) with a 2.4 m vat
  before him: the hole opened at 45; the old box test would have opened 4 buildings behind him (barracks, a keep-street
  house, both hovels), the new one opens 1 -- the bakery, whose lean-to roof really hangs over him. Capture Cases
  (`Logs/SeeThroughSpike/20261013_234356_Greywall`): every "behind" case still opens (cover 0.5-1.0), "beside a house"
  stays shut.
- **Z-fighting meshes** (kit main + spike, HANDOFF 98 "B, partly done"): reveals 3 mm into their openings (StoneUp twin
  window, loading door, door; shop reveals), the StoneUp door's hole up to its arch crown, the outer stair, the bell
  tower's plinth and belfry lintels, the stone gable parapet's seat, skirt tops, the plaster window's sill; 15 pieces
  rebuilt and exported, .blend saved. Measured with the watch: round the apothecary 40,057 fight pixels -> 4,514; with
  the chapel and the wizard's tower too, 2,546 (`Logs/ZFightWatch/20261014_000135`).
- **Left** (smaller, mostly faces crossing at a shallow angle rather than lying in one plane): a crop's soil on the
  ground (506 px), a turret segment against a StoneUp window wall (449), StoneUp corners' quoins against their core
  and the slit wall (490), slates crossing slates on the stepped gable and the pent roof (395), the thatch gable's wood
  (125), a grave cross, a town-wall module.
- How the meshes were worked: a background Blender (`blender -b medievalDiorama.blend --python <runner>`, jobs dropped
  in a folder) since the live Blender had the Humans file open; `flush_pairs` measured each piece (same-facing faces
  in one plane under 0.5 mm, visible from above), before and after.

## Round 3 (2026-10-14): caps baked and pooled

The user asked whether every instance gets its own cut model. It did not: the cut is the shader's (each instance only
keeps its cut height in its rendering layer) and cap meshes were shared per mesh, cut step and solid materials (Greywall
4,255 cut pieces, 161 cap meshes) -- but every cut piece had a cap renderer of its own, and the caps were made by an
editor hook in play, so a player build had none.

- **Bake:** `KitSeeThroughCapBank` (MedievalSetting `Assets/Game/Resources/KitSeeThroughCaps.asset`, loaded from
  Resources) holds each cap mesh as a sub-asset with its key and its source mesh's vertex count and bounds (a
  re-exported mesh no longer matches: ignored until the next bake). `KitSeeThroughCapsBake` (Tools > Medieval Kit >
  Bake See-through Caps, and `IPreprocessBuildWithReport` before every player build) opens each build scene that has a
  `KitVillage` (scene text checked for its script GUID first) additively, runs `KitVillage.SetUpSeeThrough()` with
  `KitSeeThroughCaps.Collecting` set (keys only; every renderer's rendering layers put back), makes each cap once and
  closes the scene unsaved. First bake: 8 levels, 295 keys, 263 cap meshes (12,034 triangles, 3 MB), 32 empty, 0
  unfilled, 9.4 s. In play Greywall registers its 4,255 caps from the bank in 110 ms (was ~1.4 s of slicing spread
  over frames); the editor still makes what the bank lacks.
- **Pool:** a cut piece is registered (`KitSeeThroughCaps.Piece`: renderer, shared cap mesh, materials, its own
  bounds, stacking offset) instead of getting a child renderer. Each main-camera frame
  (`RenderPipelineManager.beginCameraRendering`) 96 pooled renderers are laid over the registered pieces whose bounds
  meet the cone from the camera to the walker (the hole's radius at the walker), nearest first; the shader still draws
  each only where the hole opened it. Greywall: 96 cap renderers instead of 4,255; behind the inn 8 are in use.
  Stacking (round 1) is kept per piece (`Settle()` ranks a building's pieces once its caps are known).
- Capture Cases after (`Logs/SeeThroughSpike/20261014_131610_Greywall`): same pictures as before the pool.
- **Edge case 14** (a building on a terrain tier, an outer stair, a porch): the windmill and the keep from their low
  side, the main_n_2 porch and the apothecary's stair landing were right; on the keep's stair landing (5.5 m up) the
  walker stood over a hole to the ground -- the keep is cut 1.4 m over its floor, under the walker's feet. Now a cut
  never lies under the walker's feet + 5 cm (`KitSeeThroughFoot`, `KitSeeThrough.AboveFeet` / `CutAt`, MedievalSetting
  `ClickToMove.SeenThrough` follows); a real cap under that height is not drawn (its piece is kept over it) and the
  back-face cap pass finishes the cut there. After: the walker stands on the kept stone; the hidden check also stops
  counting the floor under the walker as cover. Shots in the scratchpad `edges3/`.
- Also this morning (HANDOFF 98, second batch): porches, plaster wall tops, the ale cask, the gable chimney, thatch
  gables (the user's own walk with the watch).

## Tools

- MedievalSetting **Tools > See-through Spike > Capture Cases** (`Assets/Game/Scripts/Editor/SeeThroughSpike.cs`, on the
  spike branch): in play, walks the gallery's cases for the level being played, shoots each one with the hole shut, as
  the game shows it, and without the real caps, plus the hidden check's view, into
  `Logs/SeeThroughSpike/<time>_<level>/` (not versioned) with `sheet.png` and `cases.txt` (the hidden check's cover
  and opening per case). Play Hamlet / Play Greywall (no saving) in the same menu. First run: 14 Hamlet cases in about a
  minute, 2026-10-13 20:27. Add a case to its list when a new one turns up.
- `tools/zfight_scan_*.py`, `tools/cull_render_*.py` (main): the kit's overlap scans.
- **Tools > See-through Spike > Check Cap Overlaps** (same file, round 1): in play, rasterises every cap mesh on a 2 cm
  grid and counts cells where two of its outlines tie in height, and the pairs of a building's caps at the same height
  whose footprints touch (console). The z-fighting measure: 0 is the goal.
- **Z-fight watch** (MedievalSetting `Assets/Game/Scripts/ZFightWatch.cs` + `Assets/Game/Resources/ZFightProbe.shader`):
  F8 in play or Tools > See-through Spike > Z-fight Watch; logs to `Logs/ZFightWatch/<time>/` (see above). Debug:
  `debugImages` on the ZFightWatch object saves each probe (nearest | behind, fights magenta, same-look cyan).

## When the spike ends (integration) -- done 2026-10-14

1. ~~Pick what stays~~: everything stays. The back-face cap pass is still needed: it caps what has no real cap (no
   KitVillage: interiors, dungeons, sewers) and a cut held up at a raised walker's feet (round 3). The box test stays
   as the fallback without a probe answer.
2. ~~Bake the caps at level build~~ -- done in round 3 (`KitSeeThroughCapsBake`, before every player build too).
3. ~~Fold HANDOFF 99-103 and this file into one HANDOFF entry~~ (104); LEVEL_BUILDING; MedievalSetting README /
   POLISH; the itch waiting list.
4. ~~Merge `spike/seethrough` into `main`~~; the MedievalSetting files checked in to `/main` as cs:27, the capture tool
   and the z-fight watch with them (dev tools).
