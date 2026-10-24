extends SceneTree
# A spot straight down 5 m over a black-ambient floor (linear albedo 0.214): the brightness across its pool, for a
# few cone settings, against an omni of the same energy (0.214 x E / 25 at the centre).

var vp: SubViewport
var frames := 0
var spots: Array = []
const CASES := [[12.0, 0.1125], [12.0, 1.0], [24.0, 0.1125], [30.0, 0.234], [12.0, 8.89]]

func _initialize() -> void:
	vp = SubViewport.new()
	vp.size = Vector2i(1000, 200)
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(vp)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
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
	pm.size = Vector2(200, 200)
	pm.material = mat
	floor.mesh = pm
	vp.add_child(floor)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 20          # 20 m tall, 100 m wide
	cam.position = Vector3(0, 20, 0)
	cam.rotation_degrees = Vector3(-90, 0, 0)
	vp.add_child(cam)
	cam.current = true
	for i in CASES.size():
		var s := SpotLight3D.new()
		s.light_energy = 10.0
		s.spot_attenuation = 2.0
		s.spot_range = 45.0
		s.spot_angle = CASES[i][0]
		s.spot_angle_attenuation = CASES[i][1]
		s.position = Vector3(-40 + i * 20, 5, 0)
		s.rotation_degrees = Vector3(-90, 0, 0)
		vp.add_child(s)

func _process(_d: float) -> bool:
	frames += 1
	if frames < 30:
		return false
	var img := vp.get_texture().get_image()
	var want := 0.214 * 10.0 / 25.0
	for i in CASES.size():
		var cx := 100 + i * 200        # 10 px a metre
		var row := []
		for dx in [0, 2, 4, 6, 8, 10, 15, 20, 30]:
			row.append("%.3f" % (img.get_pixel(cx + dx, 100).srgb_to_linear().r / want))
		print("CONE angle %s att %s: centre-out (0.2 m steps, then 1.5 2 3 m) / omni: %s" % [CASES[i][0], CASES[i][1], " ".join(row)])
	return true
