shader_type spatial;

// A hull's "negative space" in the sea: its waterline footprint (the village slices each moored hull at the water's
// height), drawn invisibly just before the sea (KitWaterMask.tres: render_priority -1 against the sea's 1), marks the
// stencil with 8 where it shows; KitSea draws no water there, so a boat sitting low stays dry inside instead of being
// filled with water. The depth test keeps it behind what hides it (the deck, the hull's near side), so only water the
// hull's inside would show through is cut. Unity: KitWaterMask.shader (there ColorMask 0; here alpha 0).
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled;
stencil_mode write, compare_always, 8;

void fragment() {
	ALBEDO = vec3(0.0);
	ALPHA = 0.0;
}
