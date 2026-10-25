// The z-fight watch's probe (ZFightWatch, 2026-10-13): the game's view drawn twice, off screen, at a reduced size. Pass 0
// writes, per pixel, the nearest surface: which draw (_ZDrawId, set per renderer and submesh) with the brightness of its
// painted colour (the kit's texture x tint x vertex colour, 8 bits over the id), which triangle (SV_PrimitiveID), its
// view depth and its flat normal (packed). Pass 1 draws the nearest surface that is not that triangle of that draw
// (reading pass 0 at the same pixel): the next surface behind. Where the two lie in one plane, a hair apart, the depth
// test cannot tell them apart -- the pixel fights, and it shows where the two are painted differently. Both passes keep
// the material's culling and alpha cut-out and the kit's see-through hole (KitSeeThrough.hlsl), so only what can be
// seen counts.
Shader "Hidden/MedievalGame/ZFightProbe"
{
    Properties
    {
        _BaseMap ("Base Map", 2D) = "white" {}
        _BaseColor ("Base Color", Color) = (1, 1, 1, 1)
        _ZVertexColor ("Multiply Vertex Colour", Float) = 0
        _Cutoff ("Alpha Cutoff", Float) = 0.5
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull", Float) = 2
    }
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "RenderType" = "Opaque" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        TEXTURE2D(_BaseMap);
        SAMPLER(sampler_BaseMap);
        float4 _BaseMap_ST;
        float4 _BaseColor;
        float _ZVertexColor;
        float _Cutoff;
        float _Cull;
        float _ZDrawId;              // set before each draw (ZFightWatch), under 65536
        TEXTURE2D_FLOAT(_ZFirst);    // pass 0's surfaces (pass 1 reads it)

        #define KIT_SEE_THROUGH_SOLID (_Cull > 1.5)
        #include "Packages/com.danielgruginski.medievalkit/Shaders/KitSeeThrough.hlsl"

        struct Attributes
        {
            float4 positionOS : POSITION;
            float2 uv : TEXCOORD0;
            float4 color : COLOR;
        };

        struct Varyings
        {
            float4 positionCS : SV_POSITION;
            float2 uv : TEXCOORD0;
            float3 positionWS : TEXCOORD1;
            float viewZ : TEXCOORD2;
            float4 color : TEXCOORD3;
        };

        Varyings Vert(Attributes i)
        {
            Varyings o;
            float3 ws = TransformObjectToWorld(i.positionOS.xyz);
            o.positionWS = ws;
            o.positionCS = TransformWorldToHClip(ws);
            o.uv = TRANSFORM_TEX(i.uv, _BaseMap);
            o.viewZ = -TransformWorldToView(ws).z;
            o.color = i.color;
            return o;
        }

        // a unit normal in 24 bits (octahedral, 12 + 12): exact in a float
        float PackNormal(float3 n)
        {
            n /= abs(n.x) + abs(n.y) + abs(n.z);
            float2 e = n.z >= 0 ? n.xy : (1 - abs(n.yx)) * (n.xy >= 0 ? 1 : -1);
            uint2 q = (uint2)round(saturate(e * 0.5 + 0.5) * 4095);
            return (float)(q.x * 4096 + q.y);
        }

        float3 FlatNormal(float3 ws) { return normalize(cross(ddy(ws), ddx(ws))); }

        // the draw and its painted brightness in one float: id + brightness * 65536 (under 2^24, exact)
        float Surface(Varyings i)
        {
            float4 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, i.uv);
            #ifdef _ALPHATEST_ON
            clip(tex.a - _Cutoff);
            #endif
            KitSeeThroughClip(i.positionWS, i.positionCS.xy);
            float3 c = tex.rgb * _BaseColor.rgb * (_ZVertexColor > 0.5 ? i.color.rgb : 1);
            float luma = dot(c, float3(0.299, 0.587, 0.114));
            return _ZDrawId + round(saturate(luma) * 255) * 65536;
        }
        ENDHLSL

        Pass
        {
            Name "Nearest"
            Cull [_Cull]
            ZTest LEqual
            ZWrite On

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _ALPHATEST_ON

            float4 Frag(Varyings i, uint prim : SV_PrimitiveID) : SV_Target
            {
                float id = Surface(i);
                return float4(id, (float)prim, i.viewZ, PackNormal(FlatNormal(i.positionWS)));
            }
            ENDHLSL
        }

        Pass
        {
            Name "Behind"
            Cull [_Cull]
            ZTest LEqual
            ZWrite On

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _ALPHATEST_ON

            float4 Frag(Varyings i, uint prim : SV_PrimitiveID) : SV_Target
            {
                float id = Surface(i);
                float4 first = LOAD_TEXTURE2D(_ZFirst, uint2(i.positionCS.xy));
                if (((uint)first.x & 0xFFFF) == (uint)_ZDrawId && first.y == (float)prim) discard;     // the nearest surface itself
                return float4(id, (float)prim, i.viewZ, PackNormal(FlatNormal(i.positionWS)));
            }
            ENDHLSL
        }
    }
}
