// Blender-style AgX view transform for KitAgXFeature.
// AgX base after Troy Sobotka / Blender, with Benjamin Wrensch's polynomial fit of the sigmoid. The look's contrast is
// applied in log2 space around middle grey (Blender's AgX looks are primary-grading contrast in AgX log space).
// Output is display-referred, decoded back to linear so URP's final sRGB encode reproduces it.
Shader "Hidden/MedievalKit/AgX"
{
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off ZTest Always Blend Off Cull Off

        Pass
        {
            Name "KitAgX"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"

            float _KitExposure;
            float _KitContrast;

            float3 AgxSigmoid(float3 x)
            {
                float3 x2 = x * x;
                float3 x4 = x2 * x2;
                return 15.5 * x4 * x2 - 40.14 * x4 * x + 31.96 * x4 - 6.868 * x2 * x + 0.4298 * x2 + 0.1191 * x - 0.00232;
            }

            float4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                float4 src = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, input.texcoord);
                float3 c = max(src.rgb * _KitExposure, 1e-10);

                // inset (rows here = the columns of the GLSL reference matrix)
                const float3x3 inset = float3x3(
                    0.842479062253094, 0.0423282422610123, 0.0423756549057051,
                    0.0784335999999992, 0.878468636469772, 0.0784336,
                    0.0792237451477643, 0.0791661274605434, 0.879142973793104);
                const float3x3 outset = float3x3(
                    1.19687900512017, -0.0528968517574562, -0.0529716355144438,
                    -0.0980208811401368, 1.15190312990417, -0.0980434501171241,
                    -0.0990297440797205, -0.0989611768448433, 1.15107367264116);
                const float minEv = -12.47393;
                const float maxEv = 4.026069;
                const float greyEv = -2.47393;   // log2(0.18)

                c = mul(c, inset);
                float3 ev = log2(max(c, 1e-10));
                ev = (ev - greyEv) * _KitContrast + greyEv;
                ev = clamp(ev, minEv, maxEv);
                c = AgxSigmoid((ev - minEv) / (maxEv - minEv));
                c = mul(c, outset);
                c = pow(saturate(c), 2.2);        // display -> linear for URP's sRGB output
                return float4(c, src.a);
            }
            ENDHLSL
        }
    }
}
