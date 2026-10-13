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
| Kit (git) | `main` (263b0da: grass saturation, FreeAssets, one-sided materials) | `spike/seethrough` |
| MedievalSetting (Plastic) | `/main` (cs:26) | `/main/spike-seethrough` |

The two go together: the game's spike code (GameCamera's hidden check, ClickToMove's cut test) needs the kit's spike
API (KitSeeThroughProbe, KitSeeThrough.CutY). Back to the main game: `git checkout main` in the kit and
`cm switch br:/main` in MedievalSetting (not while Unity plays). While MedievalSetting's workspace is on the spike
branch, check-ins from it land on the spike branch.

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
| 7 | **z-fighting at the cut**: caps of overlapping pieces in one plane | user shots (a cut cask/vat, chapel stub) | open |
| 8 | **grass inside a cut building**: needs a floor where the interior shows | user shots (stable, red-roofed house) | open |
| 9 | **stained-glass pane** standing in a cut wall's window | user shot (chapel) | open |
| 10 | **trunk cap with a gap** (a section polygon not filled right) | user shot (forest trunk) | open |
| 11 | bark caps show bark, not end grain | trees | open |
| 12 | market stall / awning | user shot (Hamlet stalls) | to look at |
| 13 | Greywall houses, the town wall ring and its corners | Greywall | untested with real caps |
| 14 | a building on a terrain tier, a porch, an outside stair | ShepherdDowns / Greywall | untested |
| 15 | interiors, dungeons, sewers (no KitVillage: no caps, no groups) | | untested |
| 16 | player build: caps are made by an editor hook today | | open (bake at level build) |

## Tools

- MedievalSetting **Tools > See-through Spike > Capture Cases** (`Assets/Game/Scripts/Editor/SeeThroughSpike.cs`, on the
  spike branch): in play, walks the gallery's cases for the level being played, shoots each one with the hole shut, as
  the game shows it, and without the real caps, plus the hidden check's view, into
  `Logs/SeeThroughSpike/<time>/` with a contact sheet. Add a case to its list when a new one turns up.
- `tools/zfight_scan_*.py`, `tools/cull_render_*.py` (main): the kit's overlap scans.

## When the spike ends (integration)

1. Pick what stays; delete the dead ends (the back-face cap pass if the real caps cover everything).
2. Bake the caps at level build (a player build has no editor hook).
3. Fold HANDOFF 99-103 and this file into one HANDOFF entry; LEVEL_BUILDING; MedievalSetting README / POLISH; the itch
   waiting list.
4. Merge `spike/seethrough` into `main`, `/main/spike-seethrough` into `/main`; switch both workspaces back.
