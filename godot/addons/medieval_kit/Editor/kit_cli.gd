extends SceneTree
# Command-line entry to the kit's C# tools (Godot runs --script only as GDScript); the work is in KitBuilder.cs and
# KitCapture.cs. With the .NET build of Godot, after the project's C# is built:
#   Godot_..._mono_console.exe --headless --path <project> --script res://addons/medieval_kit/Editor/kit_cli.gd -- check [piece ...]
#   ...                         --headless ... -- build <layout> [<layout> ...]   (the world graph first)
#   ...                         --headless ... -- structures                      (the premade structures)
#   ...                         --headless ... -- travel                          (every link of every built world level)
#   ... (a window, no --headless)          ... -- capture <layout> <out dir> [WxH] [asbuilt]
#        (WxH "" or left out: the layout's own size; asbuilt: one pass with the level's own shadows, as its Blender renders)

const EDITOR := "res://addons/medieval_kit/Editor/"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var cmd: String = args[0] if args.size() > 0 else ""
	if cmd == "check":
		var bad: int = load(EDITOR + "KitBuilder.cs").new().CheckPieces(PackedStringArray(args.slice(1)))
		quit(1 if bad > 0 else 0)
	elif cmd == "build":
		await process_frame      # the root joins the tree after _initialize (the navmesh bake needs the tree)
		var b = load(EDITOR + "KitBuilder.cs").new()
		print(b.BuildWorld())
		for l in (args.slice(1) if args.size() > 1 else ["Pilot"]):
			print(b.BuildLayout(l))
		quit()
	elif cmd == "travel":
		root.add_child(load(EDITOR + "KitTravelTest.cs").new())
	elif cmd == "structures":
		print(load(EDITOR + "KitBuilder.cs").new().BuildStructures())
		quit()
	elif cmd == "capture":
		var res := ""
		for a in args.slice(3):
			if a.contains("x") and a.get_slice("x", 0).is_valid_int():
				res = a
		var c: Node = load(EDITOR + "KitCapture.cs").new()
		c.Setup(args[1], args[2], res, args.has("asbuilt"))
		root.add_child(c)
	else:
		push_error("kit_cli: check [piece ...] | build <layout> ... | structures | travel | capture <layout> <out dir> [WxH] [asbuilt]")
		quit(1)
