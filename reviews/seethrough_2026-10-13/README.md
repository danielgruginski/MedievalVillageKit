# See-through check, 2026-10-13 (HANDOFF 99)

Only the summaries are in the repo (`summary.jpg`, `sheet_*.jpg`, the chapel close-ups); the full-size pairs named
below are kept outside it, in `GameArtGeneration/_captures/seethrough_2026-10-13/` (81 MB). Part of the see-through
spike (branch `spike/seethrough`, `SPIKE_SEETHROUGH.md`).

MedievalSetting play mode, the game camera's own view (50 degrees down, 22 m), the player warped to each spot.
Each `pair_*.png`: the see-through off (left), on (right).

- `pair_tree`: an oak between the camera and the player: a round hole through the canopy, no stump.
- `pair_bushL`, `pair_bushR`: a big bush just in front of the player stays whole (the round test). In `bushL` the
  stable's roof corner still loses a bite: the player stands against it, inside its box (the hidden check, next).
- `pair_house`, `pair_innB`, `pair_stableB`: behind a building: roof, chimney and walls open as one.
- `pair_houseC`, `pair_chapel2`: beside a building that does not hide the player: nothing opens.
- `pair_chapel1`: the player in the chapel's buttress recess: the buttress opens though it hides nothing (the
  hidden check, next).
- `pair_fin_*`: Greywall with the final settings (kept in front 0.25 m). `fin_approach_corner`: a roof edge bitten
  beside the player (the hidden check, next).
- `pair_tw0`, `pair_tw2`: outside Greywall's north wall: one round hole across the wall's modules and its round
  tower, the wall's foot kept.
- `near_margin_0.6_vs_0.25.png`: off / kept in front 0.6 m / 0.25 m, the player against a house's back wall.

The hamlet pairs were taken with the old 0.6 m margin (`GameCamera.seeThroughNear` came after).

## hidden_check/ (HANDOFF 100)

The same off (left) / game (right) pairs with the hidden check on, 1.5 s after the player was put down. Open behind
the oak, cottage_2, the inn, the stable, a Greywall house and the town wall; shut in the open, beside the bushes,
beside cottage_2, at the stable's roof corner (`pair_h_bushL`), in the chapel's buttress recess and at the Greywall
house corner: the bites above are gone. `probe_*.png`: what the probe saw (magenta: what the hole would open, over the
player's upper body). `sheet_hamlet.png`, `sheet_greywall.png`: the pairs side by side with the probe images.

## caps/ (HANDOFF 101)

`pair_u_*`: off / game, hamlet, with caps and the trunk rule: beside the oak (`u_oak_beside`, `u_oak_beside_w`) and the
blossom tree the trunk stays whole and the canopy opens round the player; behind them the whole tree opens.
`zoom_q_*`: Greywall close-ups (off / game): flat grey cut tops on the stone houses and the town wall, plank and
thatch buildings unchanged. `before_wall_cap_over_player.png`: a dropped try (caps over the player's own margin).
`summary.png`: the best of them.

## caps2/ (HANDOFF 102)

After the user's shots of the chapel and the bell tower: `pair_f_*` off / game with stone-textured, sunlit caps and open
buildings cut as a whole inside the hole (tower, chapel north side n1-n4, cottage_2, inn, stable, oak).
`before_tower_live.png`: the user's own session before (tower sliced along the player's line, grey cap strip).
`chapel_cut_zoom.png`: a cut chapel corner up close (the small fins are pieces overlapping inside the wall).
`dropped_lid_depth.png`: the dropped SV_Depth lid (buried back faces filled the nave). `summary.png`: six game views.

## realcaps/ (HANDOFF 103)

The prototype of real caps (each piece's own cross-section at 1.4 m over its base, sliced and filled): `pair_r_*` off /
game at the bell tower, the chapel's north side, cottage_2, the inn, the stable, beside and behind the oak, beside the
blossom tree. `chapel_corner_zoom.png` vs `chapel_corner_zoom_before.png`: a cut chapel corner with real caps (solid
stone tops) and with the shader's textured caps (fins of overlapping pieces showing). `summary.png`: eight game views.
