// The shroud of an underground level (the Diablo-like cave look), for Godot: Unity's Shaders/KitShroud.hlsl. What lies
// away from where the walker can go darkens with that distance, down to black a few metres in, and the rock's tops
// (faces turned up, well above the floor) keep only part of their light, so the rock between the passages reads as dark
// mass fading into the black round the level instead of pale tiles ending at a cliff edge. Off until the globals are
// set (Runtime/KitShroud.cs does it, from the level's navmesh; the plugin declares them):
//   kit_shroud_tex    R: the distance (m) from the walkable ground, over kit_shroud_args.w (a field of 0.5 m cells)
//   kit_shroud_rect   xy: the field's world xz at uv 0, zw: 1 / its world size
//   kit_shroud_args   x: on (> 0), y: the distance where the darkening starts, z: where it is black, w: the field's range
//   kit_shroud_args2  x: the floor (world y), y: the light a top keeps (0..1)
// kit_lit.gdshaderinc and KitLitCap.gdshader scale their surface by kit_shroud(...) (Unity scales the lit colour).

global uniform sampler2D kit_shroud_tex : filter_linear, repeat_disable;
global uniform vec4 kit_shroud_rect;
global uniform vec4 kit_shroud_args;
global uniform vec4 kit_shroud_args2;

// the light kept at world point p with world normal n (1: all of it; also 1 while no shroud is on)
float kit_shroud(vec3 p, vec3 n) {
	if (kit_shroud_args.x <= 0.0) return 1.0;
	vec2 uv = (p.xz - kit_shroud_rect.xy) * kit_shroud_rect.zw;
	if (any(lessThan(uv, vec2(0.0))) || any(greaterThan(uv, vec2(1.0)))) return 0.0;   // past the field: the black round the level
	float d = textureLod(kit_shroud_tex, uv, 0.0).r * kit_shroud_args.w;
	float k = 1.0 - smoothstep(kit_shroud_args.y, kit_shroud_args.z, d);
	k *= k;                                                                             // the light falls off softly, then deep
	float top = clamp((n.y - 0.5) / 0.3, 0.0, 1.0) * clamp((p.y - kit_shroud_args2.x - 1.0) / 0.6, 0.0, 1.0);
	return k * mix(1.0, kit_shroud_args2.y, top);
}
