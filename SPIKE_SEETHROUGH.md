# Spike: the see-through (branch `spike/seethrough`)

Started 2026-10-13, after a day of see-through rounds landed straight in the kit and the game (HANDOFF 99-103). The
user's call, on a friend's advice: settle the graphics question in a spike -- try things freely, check them against a
fixed set of edge cases, then integrate once.

**The question.** How should the see-through hide what covers the walker and finish what it cuts, so that the hole never
shows geometry it was not meant to show (hollow insides, back faces, pieces overlapping inside a wall, a trunk sliced
lengthways, the grass inside a house)?

## Where things live

| | main line | spike |
|---|---|---|
| Kit (git) | `main` (263b0da: grass saturation, FreeAssets, one-sided materials) | branch `spike/seethrough` |
| MedievalSetting (Plastic) | `/main` (cs:26) | pending changes in the workspace + shelveset (latest: sh:3) |

MedievalSetting's side of the spike is six files left pending on `/main` -- `GameCamera.cs` (hidden check, cut
fields), `ClickToMove.cs` (cut test), `README.md`, `POLISH.md` (notes), the capture tool
`Assets/Game/Scripts/Editor/SeeThroughSpike.cs` (+ .meta, added) -- and kept safe in a shelveset, re-shelved after each
round (`cm shelveset create <files> --all -c=...`). Not a branch: switching the shared workspace would shelve and
re-apply every session's pending files (and rewrite them under a running Unity), and other sessions' check-ins would
then land on the spike branch. So: never check those six files in to `/main` until the spike ends.

The two go together: the game's spike code needs the kit's spike API (KitSeeThroughProbe, KitSeeThrough.CutY). Back to
the main game (not while Unity plays): `git checkout main` in the kit and `cm undo` the six files in MedievalSetting
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
| 18 | **the item on the player's back is cut** | user shot 4 | asked: shields and weapons use URP Lit (never cut); the shot's cut object looks like the vat in front of the player |
| 14 | a building on a terrain tier, a porch, an outside stair | ShepherdDowns / Greywall | untested |
| 15 | interiors, dungeons, sewers (no KitVillage: no caps, no groups) | | untested |
| 16 | player build: caps are made by an editor hook today | | open (bake at level build) |

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

## When the spike ends (integration)

1. Pick what stays; delete the dead ends (the back-face cap pass if the real caps cover everything).
2. Bake the caps at level build (a player build has no editor hook).
3. Fold HANDOFF 99-103 and this file into one HANDOFF entry; LEVEL_BUILDING; MedievalSetting README / POLISH; the itch
   waiting list.
4. Merge `spike/seethrough` into `main`; check the MedievalSetting files in to `/main` (the capture tool too, or drop
   it).
