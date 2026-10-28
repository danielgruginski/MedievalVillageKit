shader_type spatial;

// The see-through's caps, Unity KitLit's SeeThroughCap pass: the next_pass of every one-sided solid KitLit material
// (gdx_export writes it). The kit's solid materials are one-sided, so a solid the hole opens shows hollow; inside the
// hole its back faces are drawn as if they lay on the level cut (the foot kept): its texture projected from above, lit as
// a level face by the sun (no shadow) and the sky, a little dimmed, pushed back a little in depth so a real face always
// wins. Only inside the open hole and below the foot kept; nothing while the hole is shut, in the hidden check's view,
// in a shadow pass, or for a piece out of the walker's way (the vertex stage drops it).
render_mode blend_mix, depth_draw_opaque, cull_front, diffuse_lambert, specular_disabled;
#define KIT_SEE_THROUGH_SOLID
#include "res://addons/medieval_kit/Shaders/kit_see_through.gdshaderinc"
#include "res://addons/medieval_kit/Shaders/kit_shroud.gdshaderinc"

uniform vec4 base_color : source_color = vec4(1.0);
uniform sampler2D albedo_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float alpha_cut = -1.0;                 // a cut-out's threshold (< 0: none)
uniform vec2 jitter = vec2(1.0, 1.0);           // the roofs' brightness at object_random 0 and 1 (KitLitJitter's)
instance uniform float object_random = 0.5;

const float KIT_CAP_SHADE = 0.8;                // a cap's light (sky + sun on a level face) times this
const float KIT_CAP_TILE = 0.5;                 // a cap's texture: tiles per metre on the cut plane

void vertex() {
	bool probe = (CAMERA_VISIBLE_LAYERS & KIT_PROBE_CAMERA) != 0u;
	if (kit_see_through.w <= 0.0 || probe || IN_SHADOW_PASS || (kit_layers & KIT_ST_CAP_MESH) != 0u
		|| !kit_st_in_the_way(CAMERA_POSITION_WORLD)) {
		POSITION = vec4(2.0, 2.0, 2.0, 1.0);         // outside the view: clipped away
	} else {
		POSITION = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0));
		POSITION.z -= 2e-5 * POSITION.w;             // a little behind (reversed z): a real face always wins
	}
}

void fragment() {
	vec4 tex = texture(albedo_map, UV);
	if (alpha_cut >= 0.0 && tex.a * base_color.a < alpha_cut) discard;
	vec3 p = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 cam = CAMERA_POSITION_WORLD, v, d;
	float L, t;
	kit_st_opens_at(p, cam, MODEL_MATRIX, v, d, L, t, true);
	float foot = kit_st_foot(MODEL_MATRIX);
	if (kit_see_through.w * t / L - length(v - d * t) < 0.0 || foot - p.y < 0.0) discard;   // off the hole, or above the foot
	vec3 r = p - cam;
	vec3 top = cam + r * clamp((foot - cam.y) / min(r.y, -1e-4), 0.0, 1.0);   // where the line of sight meets the cut
	ALBEDO = texture(albedo_map, top.xz * KIT_CAP_TILE).rgb * base_color.rgb * mix(jitter.x, jitter.y, object_random) * KIT_CAP_SHADE
		* kit_shroud(top, vec3(0.0, 1.0, 0.0));        // underground: the shroud at the cut
	NORMAL = normalize((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz);   // a level face
	ROUGHNESS = 1.0;
}

void light() {
	float nl = max(dot(NORMAL, LIGHT), 0.0) / PI;
	DIFFUSE_LIGHT += LIGHT_COLOR * nl * (LIGHT_IS_DIRECTIONAL ? 1.0 : ATTENUATION);   // the sun without its shadow
}
