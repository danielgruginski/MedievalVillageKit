// KitTerrain for Godot: the kit's object-space projected materials, ported from the Unity package's KitTerrain.shader
// (itself a port of src/terrain/vk_terrain.py). One variant per recipe (KitTerrain[Stair|Paving|Curb|Water].gdshader):
//   KT_TERRAIN  terrain_material   grass / sand / dirt / cobble layers from the map's control texture, biplanar cliffs
//                                  with moss, TCol (R AO, G rock, B rim, A wet), macro tint
//   KT_STAIR    stair_material     dressed stone with riser joints over cobbles (TCol G picks stone)
//   KT_PAVING   paving_materials   cobbles, top projection (M_VKT_Paving), or box projection with KT_BOX (M_VKT_Curb)
//   KT_WATER    terrain_water_material  river water from two noises, slightly transparent (no shadow, as in Unity)
// Positions are Blender object coordinates (the meshes sit unrotated at their map origin): Godot's model (x, -z, y).
#include "res://addons/medieval_kit/Shaders/kit_noise.gdshaderinc"

render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_lambert, specular_schlick_ggx;

uniform sampler2D macro_map : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;     // data
uniform sampler2D ctl_map : hint_default_black, filter_linear, repeat_disable;  // R dirt G cobble B sand A rock
uniform vec2 ctl_scale = vec2(0.01, 0.01);      // control map uv = warped object xy x scale (Blender's CTL_MAP Mapping)
uniform sampler2D grass_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D grass_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float grass_sat : hint_range(0.0, 1.5) = 0.6;    // the grass layer's saturation (MedievalSetting: 0.6)
uniform sampler2D sand_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D sand_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D dirt_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D dirt_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D cobble_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D cobble_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D cliff_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D cliff_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D moss_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D moss_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D stone_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D stone_h : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float proj_scale = 0.25;                // paving / curb: object position x scale
uniform float rough = 0.8;                      // paving / curb
uniform float bump_strength = 0.5;              // paving / curb
uniform float water_alpha : hint_range(0.0, 1.0) = 0.9;
uniform vec4 rim_tint = vec4(0.66, 0.76, 0.38, 0.1);     // terrain: the tiers' lip band tint (rgb) and strength (a)

varying vec3 obj_b;     // Blender object coordinates

// Blender (and Unity) put an image's v = 0 at its bottom, Godot at its top: a texture sampled at Blender coordinates
// takes v the other way round (mesh UVs need nothing: glTF turns them). kuv for the tiling maps, ctl_uv for the
// control map, which is a picture of the map (clamped) and was read from its wrong end.
vec2 kuv(vec2 b) {
	return vec2(b.x, -b.y);
}

vec2 ctl_uv(vec2 b) {
	return vec2(b.x, 1.0 - b.y);
}

void vertex() {
	obj_b = vec3(VERTEX.x, -VERTEX.z, VERTEX.y);
}

// biplanar side projection of vk_terrain's side_sample: image v = Blender z on every facing
vec4 side_sample(sampler2D t, vec3 p, float k, float ax, float ay) {
	vec4 a = texture(t, kuv(p.xz * k));
	vec4 b = texture(t, kuv(p.yz * k));
	return mix(a, b, clamp((ax - ay) / 0.35 + 0.5, 0.0, 1.0));
}

void layer(inout vec3 col, inout float hgt, vec3 ck, float hk, float w, float tau, float mac_b, float extra, bool outline) {
	float v = w - tau + (hk - 0.5) * 0.35 + (mac_b - 0.5) * 0.15;
	float mk = max(clamp(v / 0.08 + 0.5, 0.0, 1.0), extra);
	col = mix(col, ck, mk);
	if (outline) {
		col = mix(col, vec3(0.25, 0.2, 0.15), mk * (1.0 - mk) * 0.8 * 0.25);
	}
	hgt = mix(hgt, hk, mk);
}

void fragment() {
	vec3 p = obj_b;
	vec3 N = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);   // world (Godot flips it on back faces)
	vec3 pos_ws = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float nz = N.y, ax = abs(N.x), ay = abs(N.z), az = abs(N.y);
	vec3 col = vec3(1.0);
	float hgt = 0.5, rgh = 0.8, spec = 0.25, bump_str = 0.5, bump_dist = 0.04, alpha = 1.0;
#if defined(KT_TERRAIN)
	float ao = COLOR.r, rk = COLOR.g, rim = COLOR.b, wet_a = COLOR.a;
	vec3 p4 = p * 0.25;
	vec3 mac = texture(macro_map, kuv(p.xy / 48.0)).rgb;
	vec3 pw = p + (kit_noise3(p, 0.35, 2.0) - 0.5) * 1.6;
	vec4 ctl = texture(ctl_map, ctl_uv(pw.xy * ctl_scale));
	// grass at two scales (the second turned 37 degrees), then Hue/Saturation/Value (0.505, grass_sat, 0.97)
	vec2 q = p.xy / 13.1;
	float cs37 = cos(radians(37.0)), sn37 = sin(radians(37.0));
	vec2 q2 = vec2(q.x * cs37 - q.y * sn37, q.x * sn37 + q.y * cs37);
	col = mix(texture(grass_map, kuv(p4.xy)).rgb, texture(grass_map, kuv(q2)).rgb, smoothstep(0.3, 0.7, mac.b));
	col = kit_hsv(col, 0.505, grass_sat, 0.97);
	hgt = texture(grass_h, kuv(p4.xy)).r;
	layer(col, hgt, texture(sand_map, kuv(p4.xy)).rgb, texture(sand_h, kuv(p4.xy)).r, ctl.b, 0.50, mac.b, smoothstep(0.2, 0.45, wet_a), false);
	layer(col, hgt, texture(dirt_map, kuv(p4.xy)).rgb, texture(dirt_h, kuv(p4.xy)).r, ctl.r, 0.45, mac.b, 0.0, true);
	layer(col, hgt, texture(cobble_map, kuv(p4.xy)).rgb, texture(cobble_h, kuv(p4.xy)).r, ctl.g, 0.45, mac.b, 0.0, true);
	col = mix(col, rim_tint.rgb, rim * rim_tint.a);       // the tiers' lips
	// cliffs: two biplanar samples blended by slow noise, rock from above on up-facing faces, tone drift
	vec3 cl_c = side_sample(cliff_map, p, 1.0 / 6.0, ax, ay).rgb;
	float cl_h = side_sample(cliff_h, p, 1.0 / 6.0, ax, ay).r;
	vec3 po = p + vec3(17.3, 5.9, 11.1);
	vec3 cl_c2 = side_sample(cliff_map, po, 1.0 / 9.3, ax, ay).rgb;
	float cl_h2 = side_sample(cliff_h, po, 1.0 / 9.3, ax, ay).r;
	float cbl = smoothstep(0.4, 0.6, kit_noise(p, 0.11, 1.5));
	cl_c = mix(cl_c, cl_c2, cbl);
	cl_h = mix(cl_h, cl_h2, cbl);
	float wz = smoothstep(0.6, 0.85, az);
	cl_c = mix(cl_c, texture(cliff_map, kuv(p.xy / 6.0)).rgb, wz);
	cl_h = mix(cl_h, texture(cliff_h, kuv(p.xy / 6.0)).r, wz);
	cl_c *= mix(vec3(0.84, 0.84, 0.86), vec3(1.08, 1.03, 0.95), smoothstep(0.3, 0.7, kit_noise(p, 0.045, 1.0)));
	float rock_w = max(max(rk, smoothstep(0.80, 0.55, nz)), smoothstep(0.45, 0.65, ctl.a));
	// moss on up-facing rock, in patches, toned towards the rock
	vec3 mo = texture(moss_map, kuv(p.xy)).rgb;
	float mz = smoothstep(0.54, 0.78, nz + (texture(moss_h, kuv(p.xy)).r - 0.5) * 0.75);
	mz *= smoothstep(0.52, 0.6, kit_noise(p, 0.55, 3.0));
	vec3 ccol = mix(cl_c, mix(mo, cl_c, 0.3), mz);
	col = mix(col, ccol, rock_w);
	hgt = mix(hgt, cl_h, rock_w);
	col *= ao;
	float wet = smoothstep(0.6, 0.95, wet_a);
	col = mix(col, vec3(0.0), wet * 0.4);
	col *= 0.9 + mac.r * 0.2;
	col = mix(col, col * vec3(1.05, 1.0, 0.8), mac.g * 0.3);
	rgh = mix(mix(0.9, 0.85, rock_w), 0.35, wet);
	bump_str = mix(0.4, 0.8, rock_w);
	bump_dist = 0.05;
#elif defined(KT_STAIR)
	vec3 pc = p * 0.25;
	vec3 c_c = texture(cobble_map, kuv(pc.xy)).rgb;
	float c_h = texture(cobble_h, kuv(pc.xy)).r;
	vec3 s_c = side_sample(stone_map, p, 0.8, ax, ay).rgb;
	float s_h = side_sample(stone_h, p, 0.8, ax, ay).r;
	float wz = smoothstep(0.55, 0.8, az);
	s_c = mix(s_c, texture(stone_map, kuv(p.xy * 0.8)).rgb, wz);
	s_h = mix(s_h, texture(stone_h, kuv(p.xy * 0.8)).r, wz);
	float joint = (1.0 - smoothstep(0.008, 0.022, kit_voronoi_edge_1d(p.x + p.y, 1.7, 0.8))) * (1.0 - wz);
	s_c = mix(s_c, vec3(0.16, 0.14, 0.12), joint * 0.75);
	s_h = mix(s_h, 0.0, joint);
	float stone = smoothstep(0.4, 0.6, COLOR.g);
	col = mix(c_c, s_c, stone) * COLOR.r;
	hgt = mix(c_h, s_h, stone);
	rgh = mix(0.82, 0.78, stone);
	bump_str = mix(0.55, 0.45, stone);
#elif defined(KT_PAVING)
	vec3 pp = p * proj_scale;
#ifdef KT_BOX
	// Blender BOX projection, blend 0.2
	vec3 w = pow(abs(vec3(N.x, N.z, N.y)), vec3(4.0));
	w /= (w.x + w.y + w.z);
	vec4 c4 = texture(stone_map, kuv(pp.yz)) * w.x + texture(stone_map, kuv(pp.xz)) * w.y + texture(stone_map, kuv(pp.xy)) * w.z;
	hgt = texture(stone_h, kuv(pp.yz)).r * w.x + texture(stone_h, kuv(pp.xz)).r * w.y + texture(stone_h, kuv(pp.xy)).r * w.z;
	col = c4.rgb;
#else
	col = texture(cobble_map, kuv(pp.xy)).rgb;
	hgt = texture(cobble_h, kuv(pp.xy)).r;
#endif
	col *= COLOR.rgb;
	rgh = rough;
	bump_str = bump_strength;
#elif defined(KT_WATER)
	vec3 st = p * vec3(0.18, 1.4, 1.0);
	float n1 = kit_noise(st, 0.9, 4.0);
	float n2 = kit_noise(p, 0.12, 1.0);
	col = mix(vec3(0.035, 0.17, 0.2), vec3(0.06, 0.27, 0.28), smoothstep(0.35, 0.65, n2));
	col = mix(col, vec3(0.55, 0.75, 0.75), smoothstep(0.62, 0.8, n1) * 0.35);
	hgt = n1;
	rgh = 0.05;
	spec = 0.6;
	bump_str = 0.15;
	alpha = water_alpha;
#endif
	vec3 n = kit_bump(pos_ws, N, hgt, bump_str, bump_dist);
	NORMAL = normalize((VIEW_MATRIX * vec4(n, 0.0)).xyz);
	ALBEDO = col;
	SPECULAR = sqrt(spec * 0.5);    // Unity's F0 0.08 x spec in Godot's scale (F0 = 0.16 s^2)
	ROUGHNESS = rgh;
	METALLIC = 0.0;
#ifdef KT_WATER
	ALPHA = alpha;
#endif
}
