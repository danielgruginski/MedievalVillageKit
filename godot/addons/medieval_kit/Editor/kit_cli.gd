extends SceneTree
# Command-line entry to the kit's C# tools (Godot runs --script only as GDScript); the work is in KitBuilder.cs and
# KitCapture.cs. With the .NET build of Godot, after the project's C# is built:
#   Godot_..._mono_console.exe --headless --path <project> --script res://addons/medieval_kit/Editor/kit_cli.gd -- check [piece ...]
#   ...                         --headless ... -- build <layout>
#   ... (a window, no --headless)          ... -- capture <layout> <out dir> [WxH]

const EDITOR := "res://addons/medieval_kit/Editor/"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var cmd: String = args[0] if args.size() > 0 else ""
	if cmd == "check":
		var bad: int = load(EDITOR + "KitBuilder.cs").new().CheckPieces(PackedStringArray(args.slice(1)))
		quit(1 if bad > 0 else 0)
	elif cmd == "build":
		print(load(EDITOR + "KitBuilder.cs").new().BuildLayout(args[1] if args.size() > 1 else "Pilot"))
		quit()
	elif cmd == "capture":
		var c: Node = load(EDITOR + "KitCapture.cs").new()
		c.Setup(args[1], args[2], args[3] if args.size() > 3 else "1600x900")
		root.add_child(c)
	else:
		push_error("kit_cli: check [piece ...] | build <layout> | capture <layout> <out dir> [WxH]")
		quit(1)
