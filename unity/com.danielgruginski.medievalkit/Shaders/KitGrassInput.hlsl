// KitGrass's blades, built in the vertex shader from the clump list (KitGrass.cs draws them with one indirect draw per
// camera: instance = a visible clump, 7 blades x 9 vertices each, unused blades collapse to a point). Shared by all
// passes so the depth, shadow and colour passes see the same blades.
#ifndef MEDIEVALKIT_GRASS_INPUT_INCLUDED
#define MEDIEVALKIT_GRASS_INPUT_INCLUDED

#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

CBUFFER_START(UnityPerMaterial)
    float4 _Wind;           // xy: the wind's direction (world xz), z: gust speed, w: gust frequency (per m)
    half _WindStrength;     // how far a tip sways (m)
    half _PushRadius;       // the walker parts the grass within this (m)
    half _PushStrength;     // how far a tip is pushed aside (m)
    half _RootDark;         // the blades' feet darkened by this (they stand in each other's shade)
    half4 _TipColor;        // the tips' tint (sun-bleached)
    half _Translucency;     // share lit through the blade from behind
    half _Specular;
CBUFFER_END

TEXTURE2D(_GrassMap);
TEXTURE2D(_MacroMap);
SAMPLER(sampler_trilinear_repeat);

// set per draw by KitGrass
StructuredBuffer<uint> _GrassClumps;    // 4 words a clump: x, y, z (asfloat), packed tint r, g, b (/200) and height
StructuredBuffer<uint> _GrassVisible;   // the clumps this camera draws (the compute shader's cull)
float4x4 _GrassObjectToWorld;
float4 _GrassParams;                    // x: min height, y: max height, z: seed

#include "KitSeeThrough.hlsl"       // the walker: _KitSeeThrough (its chest), _KitSeeThroughArgs.x (its feet)

struct KitBlade
{
    float3 positionOS;      // the grass's object space = the ground's (for its grass colour)
    float3 normalOS;
    half4 color;
    float h;                // 0 root .. 1 tip
};

static uint KitGrassRandState;     // (static: a global without it is a uniform, read-only)
float KitGrassRand()
{
    KitGrassRandState ^= KitGrassRandState << 13;
    KitGrassRandState ^= KitGrassRandState >> 17;
    KitGrassRandState ^= KitGrassRandState << 5;
    return (KitGrassRandState & 0xFFFFFF) / 16777216.0;
}

KitBlade KitGrassBlade(uint vid, uint iid)
{
    KitBlade o;
    uint ci = _GrassVisible[iid];
    float3 root = float3(asfloat(_GrassClumps[ci * 4]), asfloat(_GrassClumps[ci * 4 + 1]), asfloat(_GrassClumps[ci * 4 + 2]));
    uint pk = _GrassClumps[ci * 4 + 3];
    o.color = half4((pk & 255) / 200.0, ((pk >> 8) & 255) / 200.0, ((pk >> 16) & 255) / 200.0, 1);
    float tall = lerp(0.6, 1.25, ((pk >> 24) & 255) / 255.0);
    KitGrassRandState = ci * 747796405u + (uint)_GrassParams.z * 2891336453u + 1u;
    KitGrassRandState = KitGrassRandState == 0 ? 1u : KitGrassRandState;
    uint blades = 5u + (uint)(KitGrassRand() * 3.0);
    uint b = vid / 9u, k = vid % 9u;
    for (uint j = 0; j < b; j++)            // the draws of the blades before this one
        for (uint q = 0; q < 7; q++) KitGrassRand();
    float a = KitGrassRand() * 6.2831853, rr = sqrt(KitGrassRand()) * 0.16;
    float yaw = KitGrassRand() * 6.2831853;
    float len = lerp(_GrassParams.x, _GrassParams.y, KitGrassRand()) * tall;
    float wid = lerp(0.045, 0.075, KitGrassRand());
    float side = KitGrassRand() - 0.5, leanAmt = lerp(0.15, 0.45, KitGrassRand());
    float3 foot = root + float3(cos(a) * rr, 0, sin(a) * rr);
    float3 across = float3(cos(yaw), 0, sin(yaw));
    float3 face = float3(-across.z, 0, across.x);
    float3 lean = normalize(float3(cos(a), 0, sin(a)) * 0.7 + face * side) * leanAmt;
    // triangles (foot L, mid L, foot R), (foot R, mid L, mid R), (mid L, tip, mid R)
    static const uint corner[9] = { 0, 2, 1, 1, 2, 3, 2, 4, 3 };
    uint c = corner[k];
    float hh = c < 2 ? 0.0 : (c < 4 ? 0.5 : 1.0);
    float sx = c == 4 ? 0.0 : ((c & 1) ? 0.5 : -0.5) * (c < 2 ? 1.0 : 0.76);
    float3 p = foot + float3(0, len * hh, 0) + lean * (len * hh * hh) + across * (wid * sx);
    o.positionOS = b < blades ? p : root;   // unused blades collapse (no area, nothing drawn)
    o.normalOS = face;
    o.h = hh;
    return o;
}

// a blade vertex in the world, swayed by the wind (gusts travel along it, a flutter on top) and pushed aside round the
// walker; h: 0 at the root, 1 at the tip (only the upper blade moves, the root stays put)
float3 KitGrassWorld(float3 positionOS, float h)
{
    float3 ws = mul(_GrassObjectToWorld, float4(positionOS, 1)).xyz;
    float h2 = h * h;
    float2 wd = normalize(_Wind.xy + float2(1e-4, 0));
    float ph = dot(ws.xz, wd) * _Wind.w - _Time.y * _Wind.z;
    float gust = 0.5 + 0.5 * sin(ph);
    gust *= gust;
    float flutter = 0.22 * sin(_Time.y * 3.3 + ws.x * 1.9 + ws.z * 2.7);
    float2 off = wd * _WindStrength * (0.3 + gust + flutter) * h2;
    if (_KitSeeThrough.w > 0)
    {
        float2 d = ws.xz - _KitSeeThrough.xz;
        float dist = length(d);
        float k = saturate(1.0 - dist / max(_PushRadius, 1e-3)) * step(abs(ws.y - _KitSeeThroughArgs.x), 1.2);
        off += d / max(dist, 1e-3) * (k * _PushStrength * h2);
    }
    ws.xz += off;
    ws.y -= dot(off, off) * 1.2;                 // a bent blade is shorter
    return ws;
}

float3 KitGrassNormalWS(float3 normalOS) { return normalize(mul((float3x3)_GrassObjectToWorld, normalOS)); }

#endif
