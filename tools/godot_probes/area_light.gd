extends SceneTree
# An AreaLight3D (0.5 x 0.5 m, energy 10) 5 m over a floor of linear albedo 0.214, facing down, beside an omni of energy
# 10 (0.214 x 10 / 25 under it): the area light's on-axis intensity in omni units, normalized and not.

var vp: SubViewport
var frames := 0

func _initialize() -> void:
	vp = SubViewport.new()
	vp.size = Vector2i(600, 200)
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
	cam.size = 20          # 20 m tall, 60 m wide: 10 px a metre
	cam.position = Vector3(0, 20, 0)
	cam.rotation_degrees = Vector3(-90, 0, 0)
	vp.add_child(cam)
	cam.current = true
	for i in 2:
		var a := AreaLight3D.new()
		a.light_energy = 10.0
		a.area_size = Vector2(0.5, 0.5)
		a.area_normalize_energy = i == 0
		a.area_attenuation = 2.0
		a.area_range = 45.0
		a.position = Vector3(-20 + i * 20, 5, 0)
		a.rotation_degrees = Vector3(-90, 0, 0)
		vp.add_child(a)
	var o := OmniLight3D.new()
	o.light_energy = 10.0
	o.omni_attenuation = 2.0
	o.omni_range = 45.0
	o.position = Vector3(20, 5, 0)
	vp.add_child(o)

func _process(_d: float) -> bool:
	frames += 1
	if frames < 30:
		return false
	var img := vp.get_texture().get_image()
	var want := 0.214 * 10.0 / 25.0
	for i in 3:
		var cx := 100 + i * 200
		var row := []
		for dx in [0, 10, 20, 30, 50]:
			row.append("%.3f" % (img.get_pixel(cx + dx, 100).srgb_to_linear().r / want))
		print("AREA %s: 0 1 2 3 5 m out / omni centre: %s" % [["area normalized", "area raw", "omni"][i], " ".join(row)])
	return true
