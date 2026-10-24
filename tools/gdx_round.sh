#!/bin/sh
# The Godot side of a GDX export (docs/GODOT_EXPORT.md): build the project's C#, import, check the pieces, build a
# layout, render its cameras and compare them with the Blender renders.
#   sh tools/gdx_round.sh [layout=Pilot] [project=E:/Unity/Godot/GameArtGeneration/medieval-kit] [shots dir] [WxH]
#   (the catalogs: sh tools/gdx_round.sh Catalog_Exterior "" <project>/catalog/exterior/shots 1920x1080;
#    a world level at its own size: sh tools/gdx_round.sh VKI_Tavern_F0 "" <project>/catalog/levels/VKI_Tavern_F0 "")
# Godot's .NET build (GODOT overrides it); the capture needs a window (Godot renders through the GPU). Blender side first:
#   blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- pilot
LAYOUT="${1:-Pilot}"
P="${2:-E:/Unity/Godot/GameArtGeneration/medieval-kit}"
SHOTS="${3:-$P/pilot/shots}"
RES="${4-1600x900}"   # "" = the layout's own resolution
G="${GODOT:-C:/Users/danie/Downloads/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CLI="res://addons/medieval_kit/Editor/kit_cli.gd"
dotnet build "$P/MedievalKit.csproj" -nologo -v q 2>&1 | grep -E "error|warn|Erro|Aviso" | grep -v " 0 " | head -20
"$G" --headless --path "$P" --import 2>&1 | grep -iE "warn|error" | grep -vE "Leaked|PagedAllocator|at: ~" | head -20
"$G" --headless --path "$P" --script "$CLI" -- check 2>&1 | grep -E "^CHECK|SCRIPT ERROR" | tail -20
"$G" --headless --path "$P" --script "$CLI" -- build "$LAYOUT" 2>&1 | grep -E "BUILD|SCRIPT ERROR|ERROR"
"$G" --path "$P" --resolution 320x180 --script "$CLI" -- capture "$LAYOUT" "$SHOTS" "$RES" 2>&1 \
	| grep -E "CAPTURE|SCRIPT ERROR|SHADER ERROR|ERROR"
py "$REPO/tools/gdx_compare.py" "$SHOTS" "$P/kit/data/layouts/$LAYOUT.json"
