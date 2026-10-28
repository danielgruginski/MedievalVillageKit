extends SceneTree
# Command-line entry to the kit's C# tools (Godot runs --script only as GDScript); the work is in KitBuilder.cs and
# KitCapture.cs. With the .NET build of Godot, after the project's C# is built:
#   Godot_..._mono_console.exe --headless --path <project> --script res://addons/medieval_kit/Editor/kit_cli.gd -- check [piece ...]
#   ...                         --headless ... -- build <layout> [<layout> ...]   (the world graph first)
#   ...                         --headless ... -- structures [name ...]           (the premade structures)
#   ...                         --headless ... -- travel                          (every link of every built world level)
#   ... (a window, no --headless)          ... -- capture <layout> <out dir> [WxH] [asbuilt]
#        (WxH "" or left out: the layout's own size; asbuilt: one pass with the level's own shadows, as its Blender renders)
#   ... (a window, no --headless)          ... -- seethrough <layout> <out dir>    (the see-through behind its structures)
#   ... (a window, no --headless)          ... -- clickwalk <layout> <out dir>     (the click-to-move walker: floor, hold, doors)
#   ...                         --headless ... -- bakecaps [layout ...]           (the see-through's caps -> res://kit/see_through_caps.res)
#   ... (a window, no --headless)          ... -- systems <out dir>                (fires, missile, silhouettes, usable things, decks)
#   ... (a window, no --headless)          ... -- gfx <out dir>                    (grass, the sea and a boat's water mask, the shroud)
#   ...                         --headless ... -- rooms golden [log]               (the kit's Blender rooms rebuilt by KitRoom)
#   ...                         --headless ... -- rooms validate [which] [count] [first seed]   (generators walk-tested)
#   ...                         --headless ... -- rooms dump <which> <count> <first seed> <out.jsonl>   (to diff with Unity's)
#   ...                         --headless ... -- rooms village <layout.json> <scene.tscn>   (an outdoor map built, walk-tested, saved)
#   ...                         --headless ... -- houses [count] [first seed]       (house set -> res://kit_houses/)
#   ...                         --headless ... -- chains sample <chain.tres> [seed] | bake <chain.tres> | validate [count] [first]
#   ...                         --headless ... -- chains stream <play.tscn>       (the streamer over a baked chain)
#   ... (a window, no --headless)          ... -- shot <scene.tscn> <out prefix> [WxH] [node|x,y [radius]]   (top-down and the game's view)

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
		print(load(EDITOR + "KitBuilder.cs").new().BuildStructuresOnly(PackedStringArray(args.slice(1))))
		quit()
	elif cmd == "capture":
		var res := ""
		for a in args.slice(3):
			if a.contains("x") and a.get_slice("x", 0).is_valid_int():
				res = a
		var c: Node = load(EDITOR + "KitCapture.cs").new()
		c.Setup(args[1], args[2], res, args.has("asbuilt"))
		root.add_child(c)
	elif cmd == "seethrough":
		var t: Node = load(EDITOR + "KitSeeThroughTest.cs").new()
		t.Setup(args[1], args[2])
		root.add_child(t)
	elif cmd == "bakecaps":
		await process_frame      # the root joins the tree after _initialize (the levels go in it)
		print(load(EDITOR + "KitSeeThroughCapsBake.cs").new().Bake(PackedStringArray(args.slice(1))))
		quit()
	elif cmd == "systems":
		var t: Node = load(EDITOR + "KitSystemsTest.cs").new()
		t.Setup(args[1])
		root.add_child(t)
	elif cmd == "gfx":
		var t: Node = load(EDITOR + "KitGfxTest.cs").new()
		t.Setup(args[1])
		root.add_child(t)
	elif cmd == "rooms":
		var r: Node = load(EDITOR + "KitRoomsCli.cs").new()
		r.Setup(PackedStringArray(args.slice(1)))
		root.add_child(r)
	elif cmd == "chains":
		var c: Node = load(EDITOR + "KitChainsCli.cs").new()
		c.Setup(PackedStringArray(args.slice(1)))
		root.add_child(c)
	elif cmd == "houses":
		var h: Node = load(EDITOR + "KitRoomsCli.cs").new()
		h.Setup(PackedStringArray(["houses"] + Array(args.slice(1))))
		root.add_child(h)
	elif cmd == "shot":
		var s: Node = load(EDITOR + "KitShot.cs").new()
		s.Setup(args[1], args[2], args[3] if args.size() > 3 else "", args[4] if args.size() > 4 else "", args[5] if args.size() > 5 else "")
		root.add_child(s)
	elif cmd == "clickwalk":
		var w: Node = load(EDITOR + "KitClickTest.cs").new()
		w.Setup(args[1], args[2])
		root.add_child(w)
	else:
		push_error("kit_cli: check [piece ...] | build <layout> ... | structures | travel | capture <layout> <out dir> [WxH] [asbuilt] | seethrough <layout> <out dir> | clickwalk <layout> <out dir> | bakecaps [layout ...] | systems <out dir> | gfx <out dir> | rooms golden|validate|dump|village ... | chains sample|bake|validate|stream ... | houses [count] [seed]")
		quit(1)
