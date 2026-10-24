# Z-fights in the interior catalog (2026-10-24)

The game's z-fight watch (MedievalSetting `ZFightWatch`, F8) over Unity's `Catalog_KitInterior` (852 pieces), toured
through its 26 cameras with Tools > Medieval Kit > Look Around This Level (UNITY_EXPORT section 7; HANDOFF 149).

- `interior_spots.csv`: the watch's log as written (119 spots: 88 fights, 22 painted alike, 9 near; plus a stretch of
  free-camera flying after the tour).
- `interior_by_piece.csv`: the fights per piece: **108 pieces, every fight inside one piece** (none between two),
  nearly all wall pieces: the top caps flush with the wall faces (`*Block / *Cap`: dungeon, dwarf, sewer, ancient), the
  ashlar walls' dressed trims (`StoneBlockIn / Dress`), the timber and wattle door frames in the plaster's plane
  (`Plaster* / M_VK_Wood`), the mine walls' timbering (`CaveRock / M_VK_Hewn`), the orc walls (`OrcLogs / WoodDark`).
  Same kind of fix as HANDOFF 132-133 (shared builder code), checked with `tools/vk_zfight.py`.

The exterior catalog was not swept: drawing it crashed the Unity editor several times that day (D3D12 device hung),
cause not found.

## Outcome (HANDOFF 150)

Not flush trims: the catalog stands every wall alone, and a wall's end faces are deleted on purpose
(`vki_open_wall_ends`: a post or the next wall always covers them), so the watch looks into the hollow end and sees the
back-to-back contacts between the wall's own solids (the coping's inside bottom on the body's top, panel ends, coping
joints), drawn two-sided. `tools/vk_zfight.py -- sided` reproduces the sweep (105 of the 108, 2,187 contacts);
`-- sided closed` (ends covered, as in a level) leaves 5, of which the cave Gap / Passage crack and the ossuary's bones
were real and are fixed in shared code; the rest are a 1 mm column step and floor-level undersides. The catalog keeps
showing the open-end contacts until it covers wall ends (open question).
