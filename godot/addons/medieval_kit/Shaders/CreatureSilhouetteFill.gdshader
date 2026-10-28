shader_type spatial;

// Creature silhouettes, pass 2 (CreatureSilhouettes.cs; Unity's CreatureSilhouette.shader pass 1): a creature drawn as a
// flat translucent colour where something lies in front of it by more than the pull (the inverted depth test) and the
// pixel is not marked (pass 1: the creature itself or the player in front), once per pixel (the stencil takes it), so
// one flat colour. The pull grows toward the feet (feet_pull more at the mesh's origin, fading out by feet_height):
// paws in the grass. Never in the see-through's hidden check view.
render_mode unshaded, depth_draw_never, depth_test_inverted, cull_back, blend_mix, shadows_disabled, fog_disabled;
stencil_mode read, write, compare_not_equal, 1;

uniform vec4 colour : source_color = vec4(0.86, 0.30, 0.24, 0.55);
uniform float pull = 0.35;
uniform float feet_pull = 0.0;
uniform float feet_height = 0.6;

const uint KIT_PROBE_CAMERA = 1048576u;     // KitSeeThrough.ProbeCameraBit

void vertex() {
	if ((CAMERA_VISIBLE_LAYERS & KIT_PROBE_CAMERA) != 0u) {
		POSITION = vec4(2.0, 2.0, 2.0, 1.0);
	} else {
		vec3 ws = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
		float up = ws.y - (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).y;     // above the mesh's origin: the feet
		float p = pull + feet_pull * clamp(1.0 - up / max(feet_height, 0.01), 0.0, 1.0);
		vec3 v = CAMERA_POSITION_WORLD - ws;
		float len = max(length(v), 1e-4);
		ws += v * (min(p, len - 0.5) / len);
		POSITION = PROJECTION_MATRIX * (VIEW_MATRIX * vec4(ws, 1.0));
	}
}

void fragment() {
	ALBEDO = colour.rgb;
	ALPHA = colour.a;
}
