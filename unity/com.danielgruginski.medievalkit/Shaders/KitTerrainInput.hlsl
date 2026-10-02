#ifndef MEDIEVALKIT_TERRAIN_INPUT_INCLUDED
#define MEDIEVALKIT_TERRAIN_INPUT_INCLUDED

#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/SurfaceInput.hlsl"

// _BaseMap / _BaseColor / _Cutoff only exist for URP's shadow and depth passes.
CBUFFER_START(UnityPerMaterial)
    float4 _BaseMap_ST;
    half4 _BaseColor;
    half _Cutoff;
    float4 _CtlScale;       // control map: uv = warped object xy * scale (Blender's CTL_MAP Mapping)
    float _ProjScale;       // paving / curb: object position x scale
    half _Rough;
    half _BumpStrength;
    half _Alpha;
CBUFFER_END

#define KIT_TEX(n) TEXTURE2D(n);
KIT_TEX(_MacroMap)
KIT_TEX(_CtlMap)
KIT_TEX(_GrassMap) KIT_TEX(_GrassH)
KIT_TEX(_SandMap) KIT_TEX(_SandH)
KIT_TEX(_DirtMap) KIT_TEX(_DirtH)
KIT_TEX(_CobbleMap) KIT_TEX(_CobbleH)
KIT_TEX(_CliffMap) KIT_TEX(_CliffH)
KIT_TEX(_MossMap) KIT_TEX(_MossH)
KIT_TEX(_StoneMap) KIT_TEX(_StoneH)
SAMPLER(sampler_trilinear_repeat);
SAMPLER(sampler_linear_clamp);

#endif
