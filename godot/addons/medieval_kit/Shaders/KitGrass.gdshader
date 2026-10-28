shader_type spatial;

// Grass blades for the kit's outdoor maps (Runtime/World/KitGrass.cs draws them: MultiMesh chunks of clumps, one small
// mesh whose vertices carry only their blade and corner). The vertex shader grows each clump's 5-7 blades from a hash
// of its root (instance custom: the root in the grass's local space = the ground's object space; instance colour: the
// clump's tint, a its height), sways them in the wind (gusts travel along it, a flutter on top) and parts them round
// the walker (the see-through's walker position). Each blade takes the ground's own grass colour under it (KitTerrain's
// grass recipe at the ground's Blender object coordinates), darker at the root, tinted at the tip; two-sided, lit like
// the kit with a little light through the blade; it casts a small shadow (that, and the sunlit tips over darker roots, is
// what makes grass read from the game camera). Unity: KitGrass.shader + KitGrassInput.hlsl.
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_lambert, specular_schlick_ggx;
#include "res://addons/medieval_kit/Shaders/kit_noise.gdshaderinc"

uniform sampler2D grass_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;   // the ground's
uniform sampler2D macro_map : hint_default_black, filter_linear_mipmap, repeat_enable;                            // the ground's
uniform float grass_sat : hint_range(0.0, 1.5) = 0.6;      // the ground's grass saturation (KitTerrain's; the village copies it)
uniform vec4 wind = vec4(1.0, 0.35, 1.4, 0.3);              // xy: the wind's direction (world xz), z: gust speed, w: gust frequency (per m)
uniform float wind_strength : hint_range(0.0, 0.5) = 0.09;  // how far a tip sways (m)
uniform float push_radius : hint_range(0.0, 3.0) = 0.85;    // the walker parts the grass within this (m)
uniform float push_strength : hint_range(0.0, 1.0) = 0.32;  // how far a tip is pushed aside (m)
uniform float root_dark : hint_range(0.0, 1.0) = 0.45;      // the blades' feet darkened by this (they stand in each other's shade)
uniform vec4 tip_color : source_color = vec4(1.5, 1.42, 0.9, 1.0);   // the tips' tint (sun-bleached; the layout's "tip")
uniform float translucency : hint_range(0.0, 1.0) = 0.3;    // share lit through the blade from behind
uniform float specular_level : hint_range(0.0, 1.0) = 0.25;

// the walker (KitSeeThrough.Set: xyz its chest, set even while the hole is shut; args.x its feet)
global uniform vec4 kit_see_through;
global uniform vec4 kit_see_through_args;
instance uniform vec3 grass_params = vec3(0.3, 0.58, 1.0); // x: min blade length, y: max, z: seed (KitGrass sets it per chunk)

varying vec3 obj_b;     // the ground's Blender object coordinates (where its grass colour is read)
varying vec3 tint;
varying float blade_h;  // 0 root .. 1 tip

uint kit_pcg(uint v) {
	uint s = v * 747796405u + 2891336453u;
	uint w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u;
	return (w >> 22u) ^ w;
}

float kit_grass_rand(inout uint s) {
	s ^= s << 13u;
	s ^= s >> 17u;
	s ^= s << 5u;
	return float(s & 16777215u) / 16777216.0;
}

vec2 kuv(vec2 b) {      // Blender's v = 0 at an image's bottom, Godot's at its top (kit_terrain.gdshaderinc)
	return vec2(b.x, -b.y);
}

void vertex() {
	int b = int(UV.x + 0.5), c = int(UV.y + 0.5);
	vec3 root = INSTANCE_CUSTOM.xyz;
	tint = COLOR.rgb;
	float tall = mix(0.6, 1.25, COLOR.a);
	uint cs = kit_pcg(floatBitsToUint(root.x) ^ kit_pcg(floatBitsToUint(root.z) ^ kit_pcg(uint(int(grass_params.z)) + 17u)));
	uint s = cs | 1u;
	int blades = 5 + int(kit_grass_rand(s) * 3.0);
	s = kit_pcg(cs ^ (uint(b + 1) * 2654435769u)) | 1u;
	float a = kit_grass_rand(s) * TAU, rr = sqrt(kit_grass_rand(s)) * 0.16;
	float yaw = kit_grass_rand(s) * TAU;
	float len = mix(grass_params.x, grass_params.y, kit_grass_rand(s)) * tall;
	float wid = mix(0.045, 0.075, kit_grass_rand(s));
	float side = kit_grass_rand(s) - 0.5, lean_amt = mix(0.15, 0.45, kit_grass_rand(s));
	vec3 foot = vec3(cos(a) * rr, 0.0, sin(a) * rr);
	vec3 across = vec3(cos(yaw), 0.0, sin(yaw));
	vec3 face = vec3(-across.z, 0.0, across.x);
	vec3 lean = normalize(vec3(cos(a), 0.0, sin(a)) * 0.7 + face * side) * lean_amt;
	// corners: 0, 1 the foot (left, right), 2, 3 the middle, 4 the tip
	float h = c < 2 ? 0.0 : (c < 4 ? 0.5 : 1.0);
	float sx = c == 4 ? 0.0 : ((c % 2) == 1 ? 0.5 : -0.5) * (c < 2 ? 1.0 : 0.76);
	vec3 p = foot + vec3(0.0, len * h, 0.0) + lean * (len * h * h) + across * (wid * sx);
	if (b >= blades) {
		p = vec3(0.0);          // unused blades collapse (no area, nothing drawn)
	}
	obj_b = vec3(root.x + p.x, -(root.z + p.z), root.y + p.y);
	blade_h = h;

	// swayed by the wind and pushed aside round the walker (only the upper blade moves, the root stays put)
	vec3 ws = (MODEL_MATRIX * vec4(p, 1.0)).xyz;
	float h2 = h * h;
	vec2 wd = normalize(wind.xy + vec2(1e-4, 0.0));
	float ph = dot(ws.xz, wd) * wind.w - TIME * wind.z;
	float gust = 0.5 + 0.5 * sin(ph);
	gust *= gust;
	float flutter = 0.22 * sin(TIME * 3.3 + ws.x * 1.9 + ws.z * 2.7);
	vec2 off = wd * wind_strength * (0.3 + gust + flutter) * h2;
	if (any(notEqual(kit_see_through.xyz, vec3(0.0)))) {
		vec2 d = ws.xz - kit_see_through.xz;
		float dist = length(d);
		float k = clamp(1.0 - dist / max(push_radius, 1e-3), 0.0, 1.0) * step(abs(ws.y - kit_see_through_args.x), 1.2);
		off += d / max(dist, 1e-3) * (k * push_strength * h2);
	}
	vec3 wo = vec3(off.x, -dot(off, off) * 1.2, off.y);       // a bent blade is shorter
	VERTEX = p + inverse(mat3(MODEL_MATRIX)) * wo;
	NORMAL = face;
	if ((CAMERA_VISIBLE_LAYERS & 1048576u) != 0u) {
		VERTEX = vec3(0.0);        // the see-through's hidden check (its camera's KIT_PROBE_CAMERA bit) sees no grass, as in Unity
	}
}

void fragment() {
	// the ground's grass at this spot (KitTerrain: two scales, macro blend, HSV)
	vec3 p = obj_b;
	vec3 mac = texture(macro_map, kuv(p.xy / 48.0)).rgb;
	vec2 q = p.xy / 13.1;
	float cs37 = cos(radians(37.0)), sn37 = sin(radians(37.0));
	vec2 q2 = vec2(q.x * cs37 - q.y * sn37, q.x * sn37 + q.y * cs37);
	vec3 col = mix(texture(grass_map, kuv(p.xy * 0.25)).rgb, texture(grass_map, kuv(q2)).rgb, smoothstep(0.3, 0.7, mac.b));
	col = kit_hsv(col, 0.505, grass_sat, 0.97);
	float h = blade_h;
	vec3 albedo = col * tint * mix(1.0 - root_dark, 1.0, sqrt(h)) * mix(vec3(1.0), tip_color.rgb, h);
	// a soft normal: the blade's face (Godot turns it to the side seen), leaned toward the sky, so the clump reads as a
	// tuft, not as cards
	vec3 up = (VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz;
	NORMAL = normalize(mix(NORMAL, up, 0.6));
	ALBEDO = albedo * (1.0 - 0.5 * translucency);
	BACKLIGHT = vec3(translucency / (1.0 - 0.5 * translucency));    // light through the blade from behind (x albedo)
	SPECULAR = sqrt(0.5 * specular_level);    // Unity's F0 0.08 x level in Godot's scale (F0 = 0.16 s^2)
	ROUGHNESS = 0.7;
}
