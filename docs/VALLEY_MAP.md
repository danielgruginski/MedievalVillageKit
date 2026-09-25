# Valley Town: showcase map for review

Blender file (open and live, via the Blender MCP tool `mcp__blender__execute_blender_code`): `ROOT\blender\medievalDiorama.blend`, scene **VillageKit**.

- Terrain: collection `VK_ValleyTerrain` (chunk meshes `VKV_Chunk_*`, water `VKV_Water_*`, cobble paving `VKV_Paving`).
- Buildings, props and nature: collection `VK_ValleyTown` (about 4,400 instances).
- Generator source: `ROOT\src\maps\vk_town_map.py`, run inside `vk_kit_ns()`.
- Terrain kit: `ROOT\src\terrain\vk_terrain.py`.

`ROOT = E:\Unity\Projects\GameArtGeneration\MedievalVillageKit`

## Rendering (read-only review)

```python
import bpy
exec(bpy.data.texts["vk_render"].as_string())        # defines shot()
shot("review_<lens>_<name>", (x,y,z), (tx,ty,tz), lens=30, res=(1600,900), outdir=r"<ROOT>\renders\review\<lens>")
```

The PNG path is returned; look at it with the **Read** tool.
- Keep calls short. Other agents share Blender, and calls are serialized.
- Do NOT modify, move, add or delete anything. The only exception is that `shot()` reuses the camera `VK_CamTmp`.
- Never save.
- You may *inspect* data, for example object locations, bound boxes and ray casts, with read-only Python.

## Grid and coordinates

**Map frame.**
- Map-local (0,0) is world (1500, 0, 0).
- A cell (i, j) covers world x ∈ [1500+3i, 1500+3i+3] and y ∈ [3j, 3j+3].
- The map is 72 × 56 cells (216 × 168 m).
- A cell's ground height is level × 1.5 m. Water is 0.6 m below its level, and the river bed 1.5 m below.

**Terrain.** The terrain is marching-squares tiles.
- Cliffs sit on the cell borders between levels, with a turf lip, strata, a bulge and a toe.
- Ramps and stone stairs link levels.
- A world-space horizontal displacement makes contours organic.
- Tops are exactly flat, and "stiff" cells (under buildings, roads and plazas) are not displaced.

**Levels and districts** (cell rows j, columns i):

| Area | Level | Cells | Contents |
|---|---|---|---|
| South land | 1 | rows 0–9 | Hamlet in the west (i 2–24): longhouse, 3 hovels, pig sty, sheepfold, crop plots. Settler camp (i 29–33). Sawpit and stockpile (i 35–38). Palisade outpost (i 49–57). Barracks training yard (i 59–65). |
| River | 0 | water rows 12–15, sandy banks rows 10–11 and 16–17; it rises from a spring pool at i 3–7 (the valley head, i 0–2, is level 1, so no water reaches the west edge) | Spring: rock outcrop over the pool, boulders where the water wells up, reeds and ferns (`town_spring`). Stone bridge on the main road (x ≈ 1626). Wooden footbridge on the west road (x ≈ 1530, cells 9–10), with bank ramps at rows 10 and 17. Watermill on a level-0 inlet (i 23–29, rows 16–19), with a ramp up to the meadow at i 24–25, row 19. Quay with a barge (i 33–37). Lavoir and smokehouse on the north bank. A river road on row 9 links the footbridge lane to the main road. |
| Lake | 0 | irregular basin (an ellipse with a wavy radius, `_blob`), i 57–71, rows 5–19; water ends at least one sand cell before the east edge | Fisher hut with pier on the south shore. Shore ramp up to the south land at i 66–67, row 5. |
| North meadow | 1 | rows 18–23 | Tannery, pottery, dyers yard, apiary, windmill, granary. Construction sites at stages 0/1/2 (i 45–60). |
| West bench | 2 | i 0–19, rows 24–33 | Log cabin, woodcutter, forester, charcoal burner. Mine portal against the level-3 ridge. Quarry pit cut into the hill between level-4 shoulders (i 12–13 and 16–17, rows 31–33), with its mouth kept clear; treadwheel crane on the ridge top. A stone stair climbs to the ridge at i 9, at the end of the west road, and a second stair (i 10, row 36) goes on up to the level-4 quarry hill. A lane on row 30 leads east to the west postern. |
| Walled town plateau | 2 | i 20–63, rows 24–46 | Walls on vertex lines y=75, 138 and x=1569, 1689, with round towers. The gatehouse (4 cells wide, 3.5 m passage, leaves open flat, portcullis raised) sits at x=1626, centred on the road, on a level-2 apron (row 23, i 39–44). The gate ramp is at row 22. The west postern (`SM_VK_TownWall_Postern`) is at row 30. Contents: cobbled main street and plaza (separate paving mesh with curbs and missing-stone patches); the landmark **smithy** right inside the gate (x ≈ 1635, y ≈ 83.5, facing the main street); the landmark **inn** on the plaza's west side (x ≈ 1602, y ≈ 97.5); plaza with market cross, notice board and baker/fishmonger/potter/draper stalls; skyline street (north); the west quarter, where the merchant house, gable-front townhouse and corner house face north onto the postern street (row 30); fortified tower house; terrace (south-east, facing the row-29 street); festival green; brewery; chapel facing the plaza across a cobbled forecourt (rows 36–38); about 10 infill houses with district roof palettes; kitchen gardens. |
| North ridge | 3–5 | rows 47–55 | Forest. |
| West ridge | 3–4 | i 0–19, rows 34–46 | Forest. |

**Main road.** Cells i 41–42, cobbled all the way from the south map edge north across the stone bridge (the paving stops under the bridge's approach ramps, `town_paving_exclude`). Walled road ramps go up at rows 10, 17 and 22, then across the gate apron, through the gatehouse, and on to the plaza.

## Style target

- **Look:** a hand-painted, World-of-Warcraft-style stylised medieval kit for a Unity colony sim.
- **Shapes:** chunky and slightly irregular.
- **Readability:** readable from a colony camera about 40 m away at a 50° pitch.
