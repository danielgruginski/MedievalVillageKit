#ifndef MEDIEVALKIT_KITLIT_INPUT_INCLUDED
#define MEDIEVALKIT_KITLIT_INPUT_INCLUDED

#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/SurfaceInput.hlsl"

// Blender kit material, reduced (src/export/vkx_export.py analyze_material):
//   albedo    = BaseMap * BaseColor * vertex colour (optional) * per-object jitter (Object Info > Random)
//   roughness = RoughMap * RoughScale (or Roughness when there is no map); smoothness = 1 - roughness
//   specular  = Blender's Specular IOR Level (0.5 = F0 0.04)
//   emission  = EmissionMap * EmissionColor, plus the vki_rim glow from the vertex colour's alpha
CBUFFER_START(UnityPerMaterial)
    float4 _BaseMap_ST;
    half4 _BaseColor;
    half4 _Jitter;          // x = min, y = max brightness factor per object
    half _BumpScale;
    half _RoughScale;
    half _Roughness;
    half _Metallic;
    half _Specular;
    half4 _EmissionColor;
    half4 _RimColorA;
    half4 _RimColorB;
    half4 _RimK;            // strength = rim * x + y
    half _Cutoff;
    half _Surface;
    half _MossTile;
    half4 _MossNoise;       // height h -> h * x + y
    half4 _MossRange;       // smoothstep(x, y, normal.up + noise)
    half _Translucency;     // Blender Mix Shader(surface, Translucent BSDF): share lit through from behind
CBUFFER_END

TEXTURE2D(_RoughMap);
SAMPLER(sampler_RoughMap);
TEXTURE2D(_MossMap);
TEXTURE2D(_MossBumpMap);
TEXTURE2D(_MossRoughMap);
TEXTURE2D(_MossHeightMap);

// Object Info > Random stand-in: a hash of the object's world position (stable per placement, SRP-batcher safe).
half KitObjectRandom()
{
    float3 o = UNITY_MATRIX_M._m03_m13_m23;
    return frac(sin(dot(o, float3(12.9898, 78.233, 37.719))) * 43758.5453);
}

#endif
