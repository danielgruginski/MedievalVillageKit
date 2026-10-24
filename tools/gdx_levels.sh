#!/bin/sh
# The Godot side of the world levels (docs/GODOT_EXPORT.md): build every world-graph level (navmesh + walk test) and the
# premade structures, render each level's cameras at its own size with its own shadows and compare them with the
# Blender renders beside them (catalog/levels/<level>/blender_<camera>.png), then take every link (the travel test).
#   sh tools/gdx_levels.sh [project=E:/Unity/Godot/GameArtGeneration/medieval-kit] [level ...]
# Blender side first (the layouts and renders):
#   blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- world
#   blender -b blender/medievalDiorama.blend --python src/export/gdx_export.py -- structures
P="${1:-E:/Unity/Godot/GameArtGeneration/medieval-kit}"
[ $# -gt 0 ] && shift
G="${GODOT:-C:/Users/danie/Downloads/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CLI="res://addons/medieval_kit/Editor/kit_cli.gd"
LEVELS="$*"
[ -z "$LEVELS" ] && LEVELS="$(py -c "import json,sys; print(' '.join(json.load(open(sys.argv[1]))['levels']))" "$P/kit/data/world.json")"
dotnet build "$P/MedievalKit.csproj" -nologo -v q 2>&1 | grep -E "error|warn" | grep -v " 0 " | head -20
"$G" --headless --path "$P" --script "$CLI" -- build $LEVELS 2>&1 | grep -E "BUILD|SCRIPT ERROR|ERROR"
"$G" --headless --path "$P" --script "$CLI" -- structures 2>&1 | grep -E "STRUCTURES|  |SCRIPT ERROR|ERROR"
for L in $LEVELS; do
	"$G" --path "$P" --resolution 320x180 --script "$CLI" -- capture "$L" "$P/catalog/levels/$L" asbuilt 2>&1 \
		| grep -E "CAPTURE|SCRIPT ERROR|SHADER ERROR|ERROR"
	py "$REPO/tools/gdx_compare.py" "$P/catalog/levels/$L" | sed "s/^COMPARE /COMPARE $L /"
done
"$G" --headless --path "$P" --script "$CLI" -- travel 2>&1 | grep -E "^TRAVEL|SCRIPT ERROR|ERROR"
