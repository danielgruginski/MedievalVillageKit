// The shroud of an underground level (the Diablo-like cave look): what lies away from where the walker can go darkens
// with that distance, down to black a few metres in, and the rock's tops (faces turned up, well above the floor) keep
// only part of their light, so the rock between the passages reads as dark mass fading into the black round the level
// instead of pale tiles ending at a cliff edge. Off until the globals are set (KitShroud does it, from the level's
// navmesh):
//   _KitShroudTex    R: the distance (m) from the walkable ground, over _KitShroudArgs.w (a field of 0.5 m cells)
//   _KitShroudRect   xy: the field's world xz at uv 0, zw: 1 / its world size
//   _KitShroudArgs   x: on (> 0), y: the distance where the darkening starts, z: where it is black, w: the field's range
//   _KitShroudArgs2  x: the floor (world y), y: the light a top keeps (0..1)
#ifndef KIT_SHROUD_INCLUDED
#define KIT_SHROUD_INCLUDED

TEXTURE2D(_KitShroudTex);
SAMPLER(sampler_KitShroudTex);
float4 _KitShroudRect;
float4 _KitShroudArgs;
float4 _KitShroudArgs2;

half KitShroud(float3 positionWS, half3 normalWS)
{
    if (_KitShroudArgs.x <= 0) return 1;
    float2 uv = (positionWS.xz - _KitShroudRect.xy) * _KitShroudRect.zw;
    if (any(uv < 0) || any(uv > 1)) return 0;                  // past the field: the black round the level
    half d = SAMPLE_TEXTURE2D_LOD(_KitShroudTex, sampler_KitShroudTex, uv, 0).r * _KitShroudArgs.w;
    half k = 1 - smoothstep(_KitShroudArgs.y, _KitShroudArgs.z, d);
    k *= k;                                                    // the light falls off softly, then deep
    half top = saturate((normalWS.y - 0.5) / 0.3) * saturate((positionWS.y - _KitShroudArgs2.x - 1.0) / 0.6);
    return k * lerp(1, _KitShroudArgs2.y, top);
}

#endif
