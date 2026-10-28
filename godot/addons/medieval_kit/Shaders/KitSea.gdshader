shader_type spatial;

// The sea (the village's terrain "sea": the water quads it merges), a cartoony water ported from Unity's KitSea:
//   - drawn after the opaque scene, writing no depth; refracts the opaque scene (Godot's screen and depth textures)
//   - a domain-warped five-wave ripple field for the normal, crossfaded to a coarse swell with distance, gust patches,
//     distance calming (anti-tiling)
//   - colour by the water's depth over the bed in a few hard bands (shallow -> deep), fresnel to the deep tint
//   - foam where the scene sits just behind the surface (the quay walls, hulls, piles, the beach): a hard-edged ragged
//     band plus a thin second line further out, drifting. Depths are true vertical ones (the scene rebuilt in world
//     space from the depth texture): the kit's sea is shallow (its bed 0.9 m under the water)
//   - a stepped sun glint (cartoony sparkles), lit by the sun (its shadows: ships shade the water) and the ambient light
//   - the stencil: pixels a KitWaterMask marked (value 8: a hull's waterline footprint) get no water, so a boat sitting
//     low stays dry inside (KitSea.tres draws after the mask: render_priority 1 against its -1)
// How it is lit: the body is emission (the refracted scene, unlit) plus albedo (the water's tint and the foam) lit in
// light() as Unity's sun term (0.55 + 0.45 N.L, shadow down to 0.55) and the ambient at 0.6 (AO); the glint is the
// lights' specular. Unity: KitSea.shader.
render_mode blend_mix, depth_draw_never, cull_disabled, shadows_disabled;
stencil_mode read, compare_not_equal, 8;

uniform vec4 shallow_color : source_color = vec4(0.30, 0.72, 0.74, 1.0);
uniform vec4 deep_color : source_color = vec4(0.06, 0.24, 0.40, 1.0);
uniform float depth_max : hint_range(0.2, 6.0) = 1.6;          // depth for deep (m)
uniform float color_bands : hint_range(0.0, 6.0) = 3.0;        // colour bands (0 = smooth)
uniform float base_opacity : hint_range(0.0, 1.0) = 0.6;       // seen from above
uniform float fresnel_power : hint_range(0.5, 8.0) = 3.0;

uniform float ripple_scale = 0.55;
uniform float ripple_speed = 1.2;
uniform float ripple_noise : hint_range(0.0, 1.0) = 0.6;       // irregularity
uniform float ripple_strength : hint_range(0.0, 0.5) = 0.14;
uniform float refraction_strength : hint_range(0.0, 0.15) = 0.03;
uniform float refract_edge_fade : hint_range(0.01, 2.0) = 0.35; // (m of depth)

group_uniforms glint;
uniform float spec_strength : hint_range(0.0, 3.0) = 1.2;
uniform float glint_threshold : hint_range(0.0, 1.0) = 0.55;   // stepped

group_uniforms foam;
uniform vec4 foam_color : source_color = vec4(0.95, 0.98, 1.0, 1.0);
uniform float foam_distance : hint_range(0.0, 3.0) = 0.28;     // band width (m of depth)
uniform float foam_strength : hint_range(0.0, 1.0) = 0.9;
uniform float foam_scale = 2.2;                                 // texture scale
uniform float foam_speed = 0.35;                                // drift speed
uniform float foam_hardness : hint_range(0.0, 1.0) = 0.8;      // edge hardness
uniform float foam_line : hint_range(0.0, 3.0) = 0.4;          // second line depth (m)
uniform float foam_line_width : hint_range(0.0, 0.5) = 0.04;   // second line width (m)
uniform float foam_min_depth : hint_range(0.0, 0.5) = 0.03;    // seam cutoff

group_uniforms anti_tiling;
uniform float wave_lod_start = 24.0;                            // crossfade start distance
uniform float wave_lod_end = 90.0;                              // crossfade end distance
uniform float far_scale_ratio : hint_range(0.05, 1.0) = 0.22;  // far wave scale ratio
uniform float gust_scale = 0.035;                               // (world)
uniform float gust_amount : hint_range(0.0, 1.0) = 0.5;
uniform float distance_calm : hint_range(0.0, 0.05) = 0.008;
group_uniforms;

uniform sampler2D screen_tex : hint_screen_texture, repeat_disable, filter_linear;
uniform sampler2D depth_tex : hint_depth_texture, repeat_disable, filter_nearest;

varying float sea_foam;     // fragment -> light: the foam (no glint on it)
varying vec3 sea_n;         // the rippled normal (view space; NORMAL in light() is it too, kept for clarity)

vec2 ripple_wave(vec2 p, vec2 dir, float freq, float spd, float amp, float t) {
	float phase = dot(dir, p) * freq + t * spd;
	return dir * (amp * freq * cos(phase));
}

vec2 ripple_field(vec2 p, float t) {
	vec2 warp;
	warp.x = sin(p.y * 0.7 + t * 0.6) + 0.5 * sin(p.y * 1.9 - t * 1.1);
	warp.y = sin(p.x * 0.7 - t * 0.5) + 0.5 * sin(p.x * 1.9 + t * 0.9);
	p += warp * (ripple_noise * 0.6);
	vec2 s = vec2(0.0);
	s += ripple_wave(p, normalize(vec2(0.90, 0.44)), 1.00, 1.00, 0.50, t);
	s += ripple_wave(p, normalize(vec2(-0.30, 0.95)), 1.63, 1.27, 0.31, t);
	s += ripple_wave(p, normalize(vec2(0.60, -0.80)), 2.41, 0.83, 0.21, t);
	s += ripple_wave(p, normalize(vec2(-0.85, -0.53)), 3.77, 1.51, 0.13, t);
	s += ripple_wave(p, normalize(vec2(0.15, 0.99)), 5.13, 1.09, 0.10, t);
	return s;
}

float band(float x) {           // the cartoon: x in color_bands soft-edged steps (0 = smooth)
	if (color_bands < 0.5) return x;
	float f = clamp(x, 0.0, 1.0) * color_bands, k = floor(f);
	return (k + smoothstep(0.42, 0.58, f - k)) / color_bands;
}

// the view-space point behind a screen pixel (from the depth texture; Godot's NDC z is the raw depth)
vec3 view_at(vec2 uv, mat4 inv_proj) {
	vec4 v = inv_proj * vec4(uv * 2.0 - 1.0, texture(depth_tex, uv).r, 1.0);
	return v.xyz / v.w;
}

void fragment() {
	vec3 pos_ws = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 geo_n = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);   // (Godot turns it to the side seen)
	vec3 V = normalize(CAMERA_POSITION_WORLD - pos_ws);
	float view_dist = length(CAMERA_POSITION_WORLD - pos_ws);

	// ---- ripples, distance crossfade, gusts, calming ----
	float t = TIME * ripple_speed;
	vec2 slope_fine = ripple_field(pos_ws.xz * ripple_scale, t);
	vec2 slope_coarse = ripple_field(pos_ws.xz * (ripple_scale * far_scale_ratio), t);
	vec2 slope = mix(slope_fine, slope_coarse, smoothstep(wave_lod_start, max(wave_lod_start + 1.0, wave_lod_end), view_dist));
	vec2 g = (pos_ws.xz - vec2(0.7, 0.3) * TIME) * gust_scale;
	float gm = 0.5 + 0.5 * sin(g.x * 6.2832 + sin(g.y * 3.7)) * sin(g.y * 6.2832 + sin(g.x * 4.3) + t * 0.15);
	slope *= mix(1.0 - gust_amount, 1.0, gm) / (1.0 + view_dist * distance_calm);
	float up = clamp(geo_n.y, 0.0, 1.0);
	vec3 N = normalize(geo_n + vec3(-slope.x, 0.0, -slope.y) * (ripple_strength * up));

	// ---- refraction (edge-aware), depth below the surface ----
	vec2 suv = SCREEN_UV;
	float water_eye = -VERTEX.z;
	vec3 scene_v0 = view_at(suv, INV_PROJECTION_MATRIX);
	float scene_eye0 = -scene_v0.z;
	float refr_edge = clamp((scene_eye0 - water_eye) / max(refract_edge_fade, 1e-3), 0.0, 1.0);
	vec2 ruv = suv + slope * (refraction_strength * up * refr_edge / (1.0 + view_dist * 0.05));
	if (-view_at(ruv, INV_PROJECTION_MATRIX).z < water_eye) {
		ruv = suv;
	}
	vec3 refracted = textureLod(screen_tex, ruv, 0.0).rgb;
	// the water's true vertical depth here: the scene point behind the surface (unrefracted, so it holds still), in
	// world space; nothing behind (past the bed's edge): deep
	vec3 scene_ws = (INV_VIEW_MATRIX * vec4(scene_v0, 1.0)).xyz;
	float depth = (scene_eye0 - water_eye > 80.0) ? 80.0 : max(0.0, pos_ws.y - scene_ws.y);

	// ---- colour: banded depth gradient, fresnel ----
	float dk = band(clamp(depth / depth_max, 0.0, 1.0));
	float fres = pow(1.0 - clamp(dot(V, geo_n), 0.0, 1.0), fresnel_power);
	vec3 tint = mix(shallow_color.rgb, deep_color.rgb, clamp(dk + fres * 0.5, 0.0, 1.0));
	float opacity = clamp(mix(base_opacity, 1.0, max(fres, dk * 0.6)), 0.0, 1.0);

	// ---- foam: a ragged hard band at the contact, a thin line further out ----
	vec2 fp = pos_ws.xz * foam_scale;
	float ft = TIME * foam_speed;
	float foam_tex = 0.5 + 0.5 * sin(fp.x + sin(fp.y * 1.3 + ft) + ft) * sin(fp.y - sin(fp.x * 1.1 - ft) + ft * 0.8);
	float edge = foam_distance * (0.45 + 0.55 * foam_tex);
	float foam = 1.0 - clamp(depth / max(edge, 1e-3), 0.0, 1.0);
	float hard = mix(0.45, 0.02, foam_hardness);
	foam = smoothstep(0.5 - hard, 0.5 + hard, foam);
	float line_d = foam_line * (0.85 + 0.3 * foam_tex);
	float line2 = 1.0 - smoothstep(0.0, max(foam_line_width, 1e-3), abs(depth - line_d));
	line2 *= step(0.35, foam_tex);                                   // broken into dashes
	foam = clamp(max(foam, line2 * 0.85), 0.0, 1.0) * up * foam_strength * smoothstep(0.0, foam_min_depth, depth);

	// body = lerp(refracted, tint x light, opacity), then lerp(body, foam x light, foam): the unlit part as emission,
	// the lit part as albedo (light() below)
	EMISSION = refracted * (1.0 - opacity) * (1.0 - foam);
	ALBEDO = tint * opacity * (1.0 - foam) + foam_color.rgb * foam;
	AO = 0.6;                    // the ambient at 0.6, as Unity's SampleSH(N) x 0.6
	AO_LIGHT_AFFECT = 0.0;
	SPECULAR = 0.0;              // no reflections: the glint is light()'s
	METALLIC = 0.0;
	ROUGHNESS = 1.0;
	sea_n = normalize((VIEW_MATRIX * vec4(N, 0.0)).xyz);
	NORMAL = sea_n;
	sea_foam = foam;
	ALPHA = 1.0;
}

void light() {
	vec3 n = sea_n;
	float nl = dot(n, LIGHT);
	vec3 sun = LIGHT_COLOR / PI;                 // (Godot's light colour carries a factor of pi)
	if (LIGHT_IS_DIRECTIONAL) {
		float shadow = mix(0.55, 1.0, ATTENUATION);
		DIFFUSE_LIGHT += sun * (0.55 + 0.45 * clamp(nl, 0.0, 1.0)) * shadow;
		// ---- stepped sun glint ----
		vec3 H = normalize(LIGHT + VIEW);
		float spec = pow(clamp(dot(n, H), 0.0, 1.0), 96.0);
		spec = smoothstep(glint_threshold, glint_threshold + 0.05, spec) * spec_strength * ATTENUATION * (1.0 - sea_foam);
		SPECULAR_LIGHT += sun * spec;
	} else {
		DIFFUSE_LIGHT += sun * clamp(nl, 0.0, 1.0) * ATTENUATION;
	}
}
