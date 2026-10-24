extends SceneTree
# One spot and one omni over a white Lambert floor, read back: Godot's light falloff against E/d^2 x cos.

var vp: SubViewport
var frames := 0

func _initialize() -> void:
	vp = SubViewport.new()
	vp.size = Vector2i(400, 400)
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(vp)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color.BLACK
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.BLACK
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	var we := WorldEnvironment.new()
	we.environment = env
	vp.add_child(we)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.5, 0.5, 0.5)
	mat.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT
	mat.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
	var floor := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(40, 40)
	pm.material = mat
	floor.mesh = pm
	vp.add_child(floor)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 20
	cam.position = Vector3(0, 20, 0)
	cam.rotation_degrees = Vector3(-90, 0, 0)
	vp.add_child(cam)
	cam.current = true
	# a spot 5 m up at x = -5, straight down: the floor under it at d = 5, cos 1
	var s := SpotLight3D.new()
	s.light_energy = float(OS.get_cmdline_user_args()[0]) if OS.get_cmdline_user_args().size() > 0 else 20.264
	s.spot_attenuation = 2.0
	s.spot_range = 45.0
	s.spot_angle = 12.0
	s.spot_angle_attenuation = 8.89
	s.position = Vector3(-5, 5, 0)
	s.rotation_degrees = Vector3(-90, 0, 0)
	vp.add_child(s)
	var o := OmniLight3D.new()
	o.light_energy = s.light_energy
	o.omni_attenuation = float(OS.get_cmdline_user_args()[1]) if OS.get_cmdline_user_args().size() > 1 else 2.0
	if OS.get_cmdline_user_args().size() > 2:
		var sun := DirectionalLight3D.new()
		sun.light_energy = float(OS.get_cmdline_user_args()[2])
		sun.rotation_degrees = Vector3(-90, 0, 0)
		vp.add_child(sun)
	o.omni_range = 45.0
	o.position = Vector3(5, 5, 0)
	vp.add_child(o)

func _process(_d: float) -> bool:
	frames += 1
	if frames < 30:
		return false
	var img := vp.get_texture().get_image()
	# world x -5 -> pixel 100, x 5 -> 300 (20 m over 400 px), z 0 -> 200
	var cs := img.get_pixel(100, 200)
	var co := img.get_pixel(300, 200)
	var cf := img.get_pixel(200, 20)
	print("SPOT_TEST far floor %.4f" % cf.srgb_to_linear().r)
	var want := 0.5 * float(s_energy()) / 25.0
	print("SPOT_TEST spot %.4f omni %.4f  expected albedo x E / d^2 = %.4f (linear; pixels sRGB-decoded)" % [cs.srgb_to_linear().r, co.srgb_to_linear().r, want])
	img.save_png("user://omni_spot_falloff.png")
	return true

func s_energy() -> float:
	return float(OS.get_cmdline_user_args()[0]) if OS.get_cmdline_user_args().size() > 0 else 20.264
