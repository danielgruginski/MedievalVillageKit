// KitLit for Godot: the shader of every kit material, as in Unity (src/export/gdx_export.py writes their
// ShaderMaterials into res://kit/materials; the see-through and the shroud will clip every one of them). The same
// reduction as the Unity KitLit (vkx_export.analyze_material):
//   albedo    = albedo_map x base_color x vertex colour (linear, optional) x per-object jitter
//   roughness = rough_map.r x rough_scale (or roughness without a map)
//   normal    = normal_map at Blender's Normal Map strength (Godot's NORMAL_MAP_DEPTH mixes the same way)
//   specular  = Blender's Specular IOR Level, already converted to Godot's scale by the exporter
//   emission  = emission_map x emission_color x emission_strength
//   alpha     = albedo_map.a x base_color.a (variants below)
// and what the kit's Blender materials add:
//   - translucency (leaves, foliage, crops): Blender mixes (1 - t) x surface + t x Translucent BSDF; here albedo x
//     (1 - t) and Godot's BACKLIGHT t / (1 - t), which adds light from behind times the albedo;
//   - moss on top (vk_mat.mossy_material: rock, bark): a second texture set mixed in where the world-up normal plus
//     the moss height noise passes a smoothstep, gated by the vertex colour's alpha; the maps are mixed before decoding;
//   - the vki_rim glow (hearths, lava): emission from the gradient the exporter puts in the vertex colour's alpha;
//   - the roof brightness jitter (Blender's Object Info > Random): the instance uniform object_random, which the layout
//     builder sets per placement to the value Blender computes from the object's name (KIT_JITTER only: Godot gives
//     every instance of a material with instance uniforms 16 slots of a buffer of 4096 instances' worth);
//   - the shroud of an underground level (kit_shroud.gdshaderinc, Unity's KitShroud.hlsl): the surface darkened away
//     from the walkable ground while a KitShroud is on;
//   - the see-through round the walker (kit_see_through.gdshaderinc, Unity's KitSeeThrough.hlsl): every variant clips
//     the hole first thing; in the hidden check's view (KitSeeThroughProbe's camera) it draws only what the hole would
//     open, flat magenta (green: a building's tag);
//   - a bump from a height map over the geometric normal (vk_leafgen's leaves and herbs: Blender's Bump node, height
//     T_*_H; the flip on back faces it adds is Godot's own for two-sided materials). Unity keeps their flat cards.
// Variants (a .gdshader each: KitLit[TwoSided][Jitter][Clip|Hash|Blend|Glass].gdshader, defines and this file):
//   KIT_TWO_SIDED  both faces (the exporter's two-sided materials: sheets, cards, the interior kits); else one side
//   KIT_JITTER     the roofs' per-object brightness (only the six roof materials: KitLitJitter)
//   KIT_CLIP       Blender's cut-outs (alpha > threshold): alpha scissor at alpha_cut
//   KIT_HASH       dithered texture alpha that casts shadows: alpha hash
//   KIT_BLEND      blended or constant alpha (water, puddles, webs): alpha blend, the transparent pass
//   KIT_GLASS      opaque but casting no shadow (Blender's Is Shadow Ray -> Transparent: windows, stained glass):
//                  alpha 1 in the transparent pass, which Godot never draws into shadow maps, with depth written
#ifdef KIT_TWO_SIDED
#define KIT_CULL cull_disabled
#else
#define KIT_CULL cull_back
#endif
#ifdef KIT_GLASS
#define KIT_DEPTH depth_draw_always
#else
#define KIT_DEPTH depth_draw_opaque
#endif
render_mode blend_mix, KIT_DEPTH, KIT_CULL, diffuse_lambert, specular_schlick_ggx;
#include "res://addons/medieval_kit/Shaders/kit_noise.gdshaderinc"
#ifndef KIT_TWO_SIDED
#define KIT_SEE_THROUGH_SOLID
#endif
#include "res://addons/medieval_kit/Shaders/kit_see_through.gdshaderinc"
#include "res://addons/medieval_kit/Shaders/kit_shroud.gdshaderinc"

uniform vec4 base_color : source_color = vec4(1.0);
uniform sampler2D albedo_map : source_color, hint_default_white, filter_linear_mipmap_anisotropic, repeat_enable;
uniform bool use_vertex_color = true;
#ifdef KIT_JITTER
uniform vec2 jitter = vec2(1.0, 1.0);          // brightness factor at object_random 0 and 1
instance uniform float object_random = 0.5;
#endif
uniform float alpha_cut : hint_range(0.0, 1.0) = 0.5;
uniform float translucency : hint_range(0.0, 0.99) = 0.0;
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
uniform bool use_bump = false;
uniform sampler2D bump_map : hint_default_black, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float bump_strength = 0.25;
uniform float bump_distance = 0.02;            // Blender's Bump Distance (m)

void fragment() {
	bool kit_probe = (CAMERA_VISIBLE_LAYERS & KIT_PROBE_CAMERA) != 0u;
	if (kit_st_clipped((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, CAMERA_POSITION_WORLD, MODEL_MATRIX, FRAGCOORD.xy, kit_probe)) {
		discard;
	}
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
	vec3 albedo = tex.rgb * base_color.rgb;
#ifdef KIT_JITTER
	albedo *= mix(jitter.x, jitter.y, object_random);
#endif
	if (use_vertex_color) {
		albedo *= COLOR.rgb;
	}
	ALBEDO = albedo * (1.0 - translucency);
	if (translucency > 0.0) {
		BACKLIGHT = vec3(translucency / (1.0 - translucency));
	}
	METALLIC = metallic;
	SPECULAR = specular;
	ROUGHNESS = rough;
	if (use_normal_map || use_moss) {
		NORMAL_MAP = nrm;
		NORMAL_MAP_DEPTH = normal_strength;
	}
	if (use_bump) {
		vec3 nw = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
		vec3 pw = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
		NORMAL = normalize((VIEW_MATRIX * vec4(kit_bump(pw, nw, texture(bump_map, UV).r, bump_strength, bump_distance), 0.0)).xyz);
	}
	vec3 em = emission_color.rgb * emission_strength * texture(emission_map, UV).rgb;
	if (use_rim) {
		float rim = COLOR.a;
		em += mix(rim_color_a.rgb, rim_color_b.rgb, rim) * max(0.0, rim * rim_k.x + rim_k.y);
	}
	EMISSION = em;
#if defined(KIT_CLIP)
	ALPHA = tex.a * base_color.a;
	ALPHA_SCISSOR_THRESHOLD = alpha_cut;
#elif defined(KIT_HASH)
	ALPHA = tex.a * base_color.a;
	ALPHA_HASH_SCALE = 1.0;
#elif defined(KIT_BLEND)
	ALPHA = tex.a * base_color.a;
#elif defined(KIT_GLASS)
	ALPHA = 1.0;
#endif
	// underground: away from the walkable ground, into the dark (kit_shroud.gdshaderinc; Unity scales the lit colour,
	// here what makes it: the surface, its glow and its highlights)
	if (kit_shroud_args.x > 0.0) {
		float shroud = kit_shroud((INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz, (INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
		ALBEDO *= shroud;
		EMISSION *= shroud;
		SPECULAR *= shroud;
	}
	if (kit_probe) {                               // the hidden check's view: flat magenta, a building's tag in green
		ALBEDO = vec3(0.0);                        // (Godot allows no `return` in fragment(): it overrides at the end)
		BACKLIGHT = vec3(0.0);
		SPECULAR = 0.0;
		METALLIC = 0.0;
		ROUGHNESS = 1.0;
		EMISSION = kit_st_probe_color();
#if defined(KIT_CLIP) || defined(KIT_HASH) || defined(KIT_BLEND) || defined(KIT_GLASS)
		ALPHA = 1.0;
#endif
	}
}
