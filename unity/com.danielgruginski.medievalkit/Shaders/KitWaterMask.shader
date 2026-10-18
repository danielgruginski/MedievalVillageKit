// A hull's "negative space" in the sea: its waterline footprint (KitVillage.SeaMasks slices each moored hull at the
// water's height), drawn invisibly just before the sea, marks stencil bit 8 where it shows; KitSea draws no water there,
// so a boat sitting low stays dry inside instead of being filled with water. ZTest keeps it behind what hides it (the
// deck, the hull's near side), so only water the hull's inside would show through is cut.
Shader "MedievalKit/KitWaterMask"
{
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent-1" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }
        Pass
        {
            Name "WaterMask"
            Tags { "LightMode" = "UniversalForward" }
            ColorMask 0
            ZWrite Off
            ZTest LEqual
            Cull Off
            Stencil { Ref 8 WriteMask 8 Comp Always Pass Replace }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct A { float3 positionOS : POSITION; };
            float4 Vert(A v) : SV_POSITION { return TransformObjectToHClip(v.positionOS); }
            half4 Frag() : SV_Target { return 0; }
            ENDHLSL
        }
    }
}
