# Script log index

Every script this project ran through the Blender MCP connection (and the shell/patch commands), extracted from the
session transcripts on 2026-09-23. Each block has its timestamp (UTC; local São Paulo time is UTC−3), `ok`/`ERROR`,
and a short excerpt of the result. The maintained code is in `src/`; these logs are the history (how pieces, maps and
fixes were made, including scenes whose build calls were never saved as texts, e.g. the first MedievalColony diorama).
Blocks are not meant to be re-run as a whole: later blocks often supersede earlier ones.
Extracted with `archive/dev_scripts/extract_logs.py`.

## Main session

- Blender calls: 453 (24 errors) -> `main_session\blender_calls_part01.py`, `main_session\blender_calls_part02.py`
- Shell commands / script writes: 254 -> `main_session\shell_and_writes.log`

## Workflow agents (multi-agent runs)

- **valley-rereview** (`wf_0eb94baf-61d`)
  - `agents\valley-rereview\agent-a32999cbfb63f790b*`: 72 calls
  - `agents\valley-rereview\agent-a566dfaef9de86f6e*`: 22 calls
  - `agents\valley-rereview\agent-a606e2482c9428bb8*`: 21 calls
  - `agents\valley-rereview\agent-a9443d3c9a8f63004*`: 18 calls
  - `agents\valley-rereview\agent-ac12452b28630d828*`: 31 calls
  - `agents\valley-rereview\agent-ac910b8221bab24cf*`: 44 calls
  - `agents\valley-rereview\agent-ad3b9a1ab2e178f2e*`: 63 calls
  - `agents\valley-rereview\agent-ada0d012842d11eb2*`: 20 calls
- **village-kit-buildings-continue** (`wf_a3b3c835-925`)
  - `agents\village-kit-buildings-continue\agent-a05c077fc5ebd3274*`: 53 calls
  - `agents\village-kit-buildings-continue\agent-a0dbc47a9891e1abd*`: 44 calls
  - `agents\village-kit-buildings-continue\agent-a1353f236cacb93f5*`: 44 calls
  - `agents\village-kit-buildings-continue\agent-a21525f828f455b32*`: 52 calls
  - `agents\village-kit-buildings-continue\agent-a727ba2132fe4f265*`: 46 calls
  - `agents\village-kit-buildings-continue\agent-a79552092548192bf*`: 31 calls
  - `agents\village-kit-buildings-continue\agent-aa93fbabc3acab1c2*`: 48 calls
  - `agents\village-kit-buildings-continue\agent-aca1ca98295d25113*`: 45 calls
- **village-kit-buildings** (`wf_b274fa73-285`)
  - `agents\village-kit-buildings\agent-a1bc477b1b71f39f7*`: 10 calls
  - `agents\village-kit-buildings\agent-a298577f76e256120*`: 16 calls
  - `agents\village-kit-buildings\agent-a3aa15cb0ee2a88dc*`: 18 calls
  - `agents\village-kit-buildings\agent-a3b366aa5a7f28d2b*`: 24 calls
  - `agents\village-kit-buildings\agent-a5d0a1f38c90e2f32*`: 14 calls
  - `agents\village-kit-buildings\agent-a8d31a3d7f6b1d761*`: 15 calls
  - `agents\village-kit-buildings\agent-ac0a88e8b934db1ab*`: 18 calls
  - `agents\village-kit-buildings\agent-aecc8c98edd38702a*`: 15 calls
- **valley-review** (`wf_b4907a13-928`)
  - `agents\valley-review\agent-a1dc3749fd3f86fcb*`: 67 calls
  - `agents\valley-review\agent-a22da4524a53f3c5f*`: 58 calls
  - `agents\valley-review\agent-a2d9ebb88fe5e4d79*`: 66 calls
  - `agents\valley-review\agent-ac1830a198e7e92a0*`: 20 calls
  - `agents\valley-review\agent-ad0ed44e6e1dabe12*`: 40 calls
- **nature-mesh-fixes** (`wf_f739cf47-3de`)
  - `agents\nature-mesh-fixes\agent-a0b2db0c9917161b8*`: 53 calls
  - `agents\nature-mesh-fixes\agent-acfe405d3cf78e084*`: 40 calls
  - `agents\nature-mesh-fixes\agent-afb843eaa996fc523*`: 33 calls
