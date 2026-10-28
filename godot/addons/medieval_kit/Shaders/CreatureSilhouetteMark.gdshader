shader_type spatial;

// Creature silhouettes, pass 1 (CreatureSilhouettes.cs; Unity's CreatureSilhouette.shader pass 0): stencil bit 1 wherever
// a creature or the player is the visible surface (both faces: hair and cloth are two-sided), nothing drawn. Each vertex
// slides toward the camera along its own view ray (the same pixel, a nearer depth) so the body wins over itself. Never
// in the see-through's hidden check view.
render_mode unshaded, depth_draw_never, cull_disabled, blend_mix, shadows_disabled, fog_disabled;
stencil_mode write, compare_always, 1;

uniform float pull = 0.03;

const uint KIT_PROBE_CAMERA = 1048576u;     // KitSeeThrough.ProbeCameraBit

void vertex() {
	if ((CAMERA_VISIBLE_LAYERS & KIT_PROBE_CAMERA) != 0u) {
		POSITION = vec4(2.0, 2.0, 2.0, 1.0);
	} else {
		vec3 ws = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
		vec3 v = CAMERA_POSITION_WORLD - ws;
		float len = max(length(v), 1e-4);
		ws += v * (min(pull, len - 0.5) / len);
		POSITION = PROJECTION_MATRIX * (VIEW_MATRIX * vec4(ws, 1.0));
	}
}

void fragment() {
	ALBEDO = vec3(0.0);
	ALPHA = 0.0;
}
