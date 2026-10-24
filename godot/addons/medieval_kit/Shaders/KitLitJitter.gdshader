shader_type spatial;

// The roofs: one-sided KitLit with the per-object brightness jitter (instance uniform object_random). See kit_lit.gdshaderinc.
#define KIT_JITTER
#include "res://addons/medieval_kit/Shaders/kit_lit.gdshaderinc"
