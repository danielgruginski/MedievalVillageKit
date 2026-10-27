// The see-through round a game's walker, for Godot: Unity's Shaders/KitSeeThrough.hlsl line for line (read its header
// for the why of each rule). What stands between the camera and the walker -- in a cone from the camera to a disc round
// the walker's chest, in front of the walker along the camera's level heading, above its feet -- opens with a thin
// dithered rim, and only a piece in the walker's way opens. Godot has no per-renderer rendering layers or bounds in a
// shader, so the marks KitSeeThrough.cs sets come as instance uniforms (kit_layers, kit_bmin, kit_bmax: set on each
// GeometryInstance3D once a level starts; unset, a piece is plain and opens as Unity's unmarked pieces do), and the hidden
// check's view is told apart by its camera's cull mask (KIT_PROBE_CAMERA, a bit over the visual layers).
// Off until a game sets the globals (RenderingServer.GlobalShaderParameterSet; the plugin declares them):
//   kit_see_through       xyz: the walker's chest (world), w: the hole's radius at the walker (m); w <= 0: shut
//   kit_see_through_args  x: the walker's feet (world y), y: a building's pieces kept up to feet + y, z: kept within z
//                         (m) in front of the walker, w: the walker's half-width for "in its way" (<= 0: every piece)
// Include it after the material's uniforms; first thing in fragment(): discard when kit_st_clipped(...) (kit_lit.gdshaderinc). KIT_SEE_THROUGH_SOLID: a one-sided (solid) material.

global uniform vec4 kit_see_through;
global uniform vec4 kit_see_through_args;
instance uniform uint kit_layers = 0u;          // KitSeeThrough's bits (Unity: the renderer's rendering layer mask)
instance uniform vec3 kit_bmin = vec3(0.0);     // the piece's world bounds (Unity: unity_RendererBounds); equal: none
instance uniform vec3 kit_bmax = vec3(0.0);

#ifdef KIT_SEE_THROUGH_SOLID
const bool KIT_ST_SOLID = true;
#else
const bool KIT_ST_SOLID = false;
#endif

const float KIT_ST_RIM = 0.15;                  // the dithered rim: this share of the hole's radius
const uint KIT_ST_LOOSE = 65536u;               // 1 << 16  KitSeeThrough.LooseLayer
const uint KIT_ST_ROUND = 131072u;              // 1 << 17  RoundLayer
const uint KIT_ST_GROUP = 262144u;              // 1 << 18  GroupLayer: decided on the CPU
const uint KIT_ST_OPEN = 524288u;               // 1 << 19  OpenLayer: its building is in the way
const uint KIT_ST_CAP_MESH = 1048576u;          // 1 << 20  CapLayer: a real cap
const uint KIT_ST_CUT = 2097152u;               // 1 << 21  CutLayer: its cut kept in bits 22-31
const float KIT_ST_CUT_STEP = 0.05;             // KitSeeThroughCaps.Step
const uint KIT_ST_KEEP = 32768u;                // 1 << 15  KeepBit: never cut (what a character carries)
const uint KIT_ST_TAG_SHIFT = 8u;               // a building's tag, bits 8-14
const float KIT_ST_ABOVE_FEET = 0.05;           // a cut never under the walker's feet + this
const uint KIT_PROBE_CAMERA = 1048576u;         // 1 << 20: set in the hidden check's camera's cull mask, over the 20 visual
                                                // layers (a camera's default mask has all of those), so no other camera has it

float kit_bayer4(vec2 pixel) {
	const float b[16] = float[](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	ivec2 q = ivec2(mod(floor(pixel), 4.0));
	return (b[q.y * 4 + q.x] + 0.5) / 16.0;
}

void kit_st_le(float a, float b, inout float lo, inout float hi) {
	if (a > 1e-6) hi = min(hi, b / a);
	else if (a < -1e-6) lo = max(lo, b / a);
	else if (b < 0.0) hi = -1.0;
}

bool kit_st_has_bounds() {
	return all(greaterThanEqual(kit_bmax, kit_bmin)) && any(notEqual(kit_bmax, kit_bmin));
}

bool kit_st_hits_unit(vec3 a, vec3 b) {
	vec3 d = b - a;
	vec3 q = a + d * clamp(-dot(a, d) / max(dot(d, d), 1e-6), 0.0, 1.0);
	return dot(q, q) < 1.0;
}

bool kit_st_in_the_way(vec3 cam) {
	float w = kit_see_through_args.w;
	if (w <= 0.0) return true;
	if ((kit_layers & KIT_ST_GROUP) != 0u) return (kit_layers & KIT_ST_OPEN) != 0u;
	if (!kit_st_has_bounds()) return true;                       // no bounds given: as before
	vec3 bmin = kit_bmin, bmax = kit_bmax;
	float feet = kit_see_through_args.x, chest = kit_see_through.y - feet;
	float waist = feet + 0.9 * chest, head = feet + 1.9 * chest;
	if ((kit_layers & KIT_ST_ROUND) != 0u) {
		vec3 o = 0.5 * (bmin + bmax), inv = 1.0 / max(0.5 * (bmax - bmin) + w, vec3(1e-3)), a = (cam - o) * inv;
		return kit_st_hits_unit(a, (vec3(kit_see_through.x, 0.5 * (waist + head), kit_see_through.z) - o) * inv)
			|| kit_st_hits_unit(a, (vec3(kit_see_through.x, head, kit_see_through.z) - o) * inv);
	}
	vec3 c = vec3(kit_see_through.x, 0.5 * (waist + head), kit_see_through.z);
	vec3 e = vec3(w, 0.5 * (head - waist), w);
	vec3 dc = c - cam;
	float lo = 0.0, hi = 1.0;
	for (int i = 0; i < 3; i++) {
		kit_st_le(dc[i] - e[i], bmax[i] - cam[i], lo, hi);
		kit_st_le(-(dc[i] + e[i]), cam[i] - bmin[i], lo, hi);
	}
	return lo <= hi;
}

vec3 kit_st_level_point(vec3 p, vec3 origin) {
	if ((kit_layers & KIT_ST_LOOSE) != 0u && KIT_ST_SOLID && kit_st_has_bounds()) {
		bool inside = all(greaterThanEqual(origin.xz, kit_bmin.xz - 0.5)) && all(lessThanEqual(origin.xz, kit_bmax.xz + 0.5));
		return inside ? vec3(origin.x, p.y, origin.z) : 0.5 * (kit_bmin + kit_bmax);
	}
	return p;
}

float kit_st_foot(mat4 model) {
	if ((kit_layers & KIT_ST_GROUP) != 0u && !KIT_ST_SOLID) return kit_see_through_args.x - 0.25;
	if ((kit_layers & KIT_ST_CUT) != 0u) {
		int q = int((kit_layers >> 22u) & 1023u);
		if (q >= 512) q -= 1024;
		return max(model[3].y + model[1].y * (float(q) * KIT_ST_CUT_STEP), kit_see_through_args.x + KIT_ST_ABOVE_FEET);
	}
	return kit_see_through_args.x + ((kit_layers & KIT_ST_LOOSE) != 0u ? -0.25 : kit_see_through_args.y);
}

bool kit_st_in_front(vec3 lv, vec3 cam, vec3 d, float L) {
	vec2 h = d.xz;
	float hl = length(h);
	if (hl > 0.05) {
		h /= hl;
		return dot(lv.xz, h) <= dot(kit_see_through.xz - cam.xz, h) - kit_see_through_args.z;
	}
	return dot(lv, d) <= L - kit_see_through_args.z;
}

bool kit_st_opens_at(vec3 p, vec3 cam, mat4 model, out vec3 v, out vec3 d, out float L, out float t, bool ask_foot) {
	d = kit_see_through.xyz - cam;
	L = length(d);
	d /= max(L, 1e-4);
	v = p - cam;
	t = dot(v, d);
	if (t <= 0.0) return false;
	if ((kit_layers & KIT_ST_GROUP) == 0u && !kit_st_in_front(kit_st_level_point(p, model[3].xyz) - cam, cam, d, L)) return false;
	if (ask_foot && p.y < kit_st_foot(model)) return false;
	return kit_st_in_the_way(cam);
}

bool kit_st_covers(vec3 p, vec3 cam, mat4 model) {
	vec3 d = kit_see_through.xyz - cam;
	float L = length(d);
	d /= max(L, 1e-4);
	vec3 v = p - cam;
	return dot(v, d) > 0.0 && kit_st_in_front(v, cam, d, L) && p.y >= kit_st_foot(model);
}

// the hidden check's colour of a piece: magenta, green its building's tag / 255 (linear; 0: not a building's). Unity
// writes tag x 2 into a linear target; Godot's view comes back sRGB-encoded, and tag / 255 keeps it under 0.66 there,
// clear of a white object's green (KitSeeThroughProbe tells the two apart by it)
vec3 kit_st_probe_color() {
	return vec3(1.0, float((kit_layers >> KIT_ST_TAG_SHIFT) & 127u) / 255.0, 1.0);
}

// true: the pixel is gone (call `discard` on it). probe: the camera is the hidden check's (its cull mask)
bool kit_st_clipped(vec3 p, vec3 cam, mat4 model, vec2 pixel, bool probe) {
	vec3 v, d;
	float L, t;
	if ((kit_layers & KIT_ST_CAP_MESH) != 0u) {
		if (probe || kit_see_through.w <= 0.0 || p.y < kit_see_through_args.x + KIT_ST_ABOVE_FEET - 0.01
			|| !kit_st_opens_at(p, cam, model, v, d, L, t, false)) return true;
		float rc = kit_see_through.w * t / L;
		float kc = clamp((rc - length(v - d * t)) / max(rc * KIT_ST_RIM, 1e-3), 0.0, 1.0);
		return kc - kit_bayer4(pixel) - 1e-3 < 0.0;
	}
	if (probe) {
		bool draw = (kit_layers & KIT_ST_KEEP) == 0u
			&& ((kit_layers & KIT_ST_GROUP) != 0u ? kit_st_covers(p, cam, model) : kit_st_opens_at(p, cam, model, v, d, L, t, true));
		return !draw;
	}
	if ((kit_layers & KIT_ST_KEEP) != 0u) return false;
	float r = kit_see_through.w;
	if (r <= 0.0) return false;
	if (!kit_st_opens_at(p, cam, model, v, d, L, t, true)) return false;
	float rr = r * t / L;
	float off = length(v - d * t);
	float k = clamp((rr - off) / max(rr * KIT_ST_RIM, 1e-3), 0.0, 1.0);
	return kit_bayer4(pixel) - k < 0.0;
}
