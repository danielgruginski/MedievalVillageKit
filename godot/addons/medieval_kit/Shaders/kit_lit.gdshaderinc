// KitLit for Godot: the kit materials a StandardMaterial3D cannot express (src/export/gdx_export.py writes their
// ShaderMaterials into res://kit/materials). The same reduction as the Unity KitLit (vkx_export.analyze_material):
//   albedo    = albedo_map x base_color x vertex colour (linear, optional) x per-object jitter
//   roughness = rough_map.r x rough_scale (or roughness without a map)
//   normal    = normal_map at Blender's Normal Map strength (Godot's NORMAL_MAP_DEPTH mixes the same way)
//   specular  = Blender's Specular IOR Level, already converted to Godot's scale by the exporter
//   emission  = emission_map x emission_color x emission_strength
// and the three things the kit's Blender materials add:
//   - moss on top (vk_mat.mossy_material: rock, bark): a second texture set mixed in where the world-up normal plus
//     the moss height noise passes a smoothstep, gated by the vertex colour's alpha; the maps are mixed before decoding;
//   - the vki_rim glow (hearths, lava): emission from the gradient the exporter puts in the vertex colour's alpha;
//   - the roof brightness jitter (Blender's Object Info > Random): the instance uniform object_random, which the layout
//     builder sets per placement to the value Blender computes from the object's name.
// KitLit.gdshader draws one side (the kit's solids), KitLitTwoSided.gdshader both (KIT_TWO_SIDED).
#ifdef KIT_TWO_SIDED
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_lambert, specular_schlick_ggx;
#else
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_lambert, specular_schlick_ggx;
#endif

uniform vec4 base_color : source_color = vec4(1.0);
uniform sampler2D albedo_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool use_vertex_color = true;
uniform vec2 jitter = vec2(1.0, 1.0);          // brightness factor at object_random 0 and 1
instance uniform float object_random = 0.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.5;
uniform bool use_rough_map = false;
uniform sampler2D rough_map : hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float rough_scale = 1.0;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float specular : hint_range(0.0, 1.0) = 0.5;
uniform bool use_normal_map = false;
uniform sampler2D normal_map : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float normal_strength = 1.0;
uniform vec4 emission_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float emission_strength = 0.0;
uniform sampler2D emission_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool use_rim = false;
uniform vec4 rim_color_a : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform vec4 rim_color_b : source_color = vec4(1.0);
uniform vec2 rim_k = vec2(1.0, 0.0);           // strength = rim x k.x + k.y
uniform bool use_moss = false;
uniform sampler2D moss_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D moss_normal : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D moss_rough : hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D moss_height : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float moss_tile = 1.0;
uniform vec2 moss_noise = vec2(0.5, -0.25);    // height h -> h x x + y
uniform vec2 moss_range = vec2(0.38, 0.66);    // smoothstep(x, y, up + noise)

void fragment() {
	vec4 tex = texture(albedo_map, UV);
	float rough = use_rough_map ? clamp(texture(rough_map, UV).r * rough_scale, 0.0, 1.0) : roughness;
	vec3 nrm = texture(normal_map, UV).rgb;
	if (use_moss) {
		float up = (INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).y;      // Blender: Geometry > Normal (world) z
		vec2 muv = UV * moss_tile;
		float h = texture(moss_height, muv).r;
		float moss = smoothstep(moss_range.x, moss_range.y, up + h * moss_noise.x + moss_noise.y) * COLOR.a;
		tex.rgb = mix(tex.rgb, texture(moss_map, muv).rgb, moss);
		rough = mix(rough, texture(moss_rough, muv).r, moss);
		nrm = mix(nrm, texture(moss_normal, muv).rgb, moss);
	}
	vec3 albedo = tex.rgb * base_color.rgb * mix(jitter.x, jitter.y, object_random);
	if (use_vertex_color) {
		albedo *= COLOR.rgb;
	}
	ALBEDO = albedo;
	METALLIC = metallic;
	SPECULAR = specular;
	ROUGHNESS = rough;
	if (use_normal_map || use_moss) {
		NORMAL_MAP = nrm;
		NORMAL_MAP_DEPTH = normal_strength;
	}
	vec3 em = emission_color.rgb * emission_strength * texture(emission_map, UV).rgb;
	if (use_rim) {
		float rim = COLOR.a;
		em += mix(rim_color_a.rgb, rim_color_b.rgb, rim) * max(0.0, rim * rim_k.x + rim_k.y);
	}
	EMISSION = em;
}
