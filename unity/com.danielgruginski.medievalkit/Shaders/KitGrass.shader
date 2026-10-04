// Grass blades for the kit's outdoor maps, made on the GPU: KitGrass (KitGrass.cs) culls the map's clumps with a
// compute shader each frame and draws the visible ones with one indirect draw; the vertex shader builds each clump's
// blades (KitGrassInput.hlsl). Each blade takes the ground's own grass colour under it (KitTerrain's grass recipe,
// sampled in the ground's object space), darker at the root, tinted at the tip; it sways in the wind and parts round
// the walker. Two-sided, lit like the kit (URP PBR, a little light through the blade); each tuft casts a small shadow
// (that, and the sunlit tips over darker roots, is what makes grass read from the game camera).
Shader "MedievalKit/KitGrass"
{
    Properties
    {
        [NoScaleOffset] _GrassMap("Grass (the ground's)", 2D) = "white" {}
        [NoScaleOffset] _MacroMap("Macro (the ground's)", 2D) = "gray" {}
        _Wind("Wind (xy direction, z gust speed, w gust frequency)", Vector) = (1, 0.35, 1.4, 0.3)
        _WindStrength("Wind Sway (m)", Range(0, 0.5)) = 0.09
        _PushRadius("Walker Parts Within (m)", Range(0, 3)) = 0.85
        _PushStrength("Walker Push (m)", Range(0, 1)) = 0.32
        _RootDark("Root Darkening", Range(0, 1)) = 0.45
        _TipColor("Tip Tint", Color) = (1.5, 1.42, 0.9, 1)
        _Translucency("Translucency", Range(0, 1)) = 0.3
        _Specular("Specular Level", Range(0, 1)) = 0.25
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "UniversalMaterialType" = "Lit" "IgnoreProjector" = "True" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Cull Off

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex Vert
            #pragma fragment Frag

            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile _ _LIGHT_LAYERS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile_fragment _ _LIGHT_COOKIES
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Fog.hlsl"
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"

            #define _SPECULAR_SETUP 1
            #include "KitGrassInput.hlsl"
            #include "KitNoise.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 objB : TEXCOORD1;        // the ground's Blender object coordinates (where its grass colour is read)
                half3 normalWS : TEXCOORD2;
                half4 color : TEXCOORD3;
                half h : TEXCOORD4;
                half fogFactor : TEXCOORD5;
            };

            Varyings Vert(uint vid : SV_VertexID, uint iid : SV_InstanceID)
            {
                Varyings o = (Varyings)0;
                KitBlade bl = KitGrassBlade(vid, iid);
                float3 ws = KitGrassWorld(bl.positionOS, bl.h);
                o.positionWS = ws;
                o.positionCS = TransformWorldToHClip(ws);
                o.objB = float3(-bl.positionOS.x, -bl.positionOS.z, bl.positionOS.y);
                o.normalWS = KitGrassNormalWS(bl.normalOS);
                o.color = bl.color;
                o.h = bl.h;
                o.fogFactor = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            #define S(t, uv) SAMPLE_TEXTURE2D(t, sampler_trilinear_repeat, uv)

            half4 Frag(Varyings i, bool front : SV_IsFrontFace) : SV_Target
            {
                // the ground's grass at this spot (KitTerrain: two scales, macro blend, HSV)
                float3 p = i.objB;
                float3 mac = S(_MacroMap, p.xy / 48.0).rgb;
                float2 q = p.xy / 13.1;
                float cs37 = cos(radians(37.0)), sn37 = sin(radians(37.0));
                float2 q2 = float2(q.x * cs37 - q.y * sn37, q.x * sn37 + q.y * cs37);
                float3 col = lerp(S(_GrassMap, p.xy * 0.25).rgb, S(_GrassMap, q2).rgb, smoothstep(0.3, 0.7, mac.b));
                col = KitHSV(col, 0.505, 0.8, 0.97);
                half h = i.h;
                half3 albedo = col * i.color.rgb * lerp(1.0 - _RootDark, 1.0, sqrt(h)) * lerp(half3(1, 1, 1), _TipColor.rgb, h);

                // a soft normal: the blade's face, two-sided, leaned toward the sky (the clump reads as a tuft, not as cards)
                half3 bn = normalize(i.normalWS) * (front ? 1 : -1);
                half3 n = normalize(lerp(bn, half3(0, 1, 0), 0.6));

                SurfaceData s = (SurfaceData)0;
                s.albedo = albedo * (1 - 0.5 * _Translucency);
                s.specular = 0.08 * _Specular;
                s.smoothness = 0.3;
                s.occlusion = 1;
                s.alpha = 1;
                InputData d = (InputData)0;
                d.positionWS = i.positionWS;
                d.positionCS = i.positionCS;
                d.normalWS = n;
                d.viewDirectionWS = GetWorldSpaceNormalizeViewDir(i.positionWS);
                #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
                d.shadowCoord = TransformWorldToShadowCoord(i.positionWS);
                #endif
                d.fogCoord = InitializeInputDataFog(float4(i.positionWS, 1), i.fogFactor);
                d.bakedGI = SampleSH(n);
                d.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(i.positionCS);
                d.shadowMask = half4(1, 1, 1, 1);
                half4 c = UniversalFragmentPBR(d, s);
                // light through the blade from behind
                Light ml = GetMainLight(d.shadowCoord, d.positionWS, d.shadowMask);
                half3 back = SampleSH(-n) + ml.color * ml.distanceAttenuation * ml.shadowAttenuation * saturate(dot(-bn, ml.direction));
                c.rgb += albedo * _Translucency * back;
                c.rgb = MixFog(c.rgb, d.fogCoord);
                c.a = 1;
                return c;
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull Off

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex ShadowVert
            #pragma fragment ShadowFrag
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "KitGrassInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            float4 ShadowVert(uint vid : SV_VertexID, uint iid : SV_InstanceID) : SV_POSITION
            {
                KitBlade bl = KitGrassBlade(vid, iid);
                float3 ws = KitGrassWorld(bl.positionOS, bl.h);
                float3 n = KitGrassNormalWS(bl.normalOS);
                #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                float3 ld = normalize(_LightPosition - ws);
                #else
                float3 ld = _LightDirection;
                #endif
                float4 pcs = TransformWorldToHClip(ApplyShadowBias(ws, n, ld));
                #if UNITY_REVERSED_Z
                pcs.z = min(pcs.z, UNITY_NEAR_CLIP_VALUE);
                #else
                pcs.z = max(pcs.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                return pcs;
            }
            half4 ShadowFrag() : SV_Target { return 0; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R
            Cull Off

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex DepthVert
            #pragma fragment DepthFrag
            #include "KitGrassInput.hlsl"

            float4 DepthVert(uint vid : SV_VertexID, uint iid : SV_InstanceID) : SV_POSITION
            {
                KitBlade bl = KitGrassBlade(vid, iid);
                return TransformWorldToHClip(KitGrassWorld(bl.positionOS, bl.h));
            }
            half DepthFrag(float4 positionCS : SV_POSITION) : SV_Target { return positionCS.z; }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On
            Cull Off

            HLSLPROGRAM
            #pragma target 4.5
            #pragma vertex DNVert
            #pragma fragment DNFrag
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            #include "KitGrassInput.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"

            struct V { float4 positionCS : SV_POSITION; half3 normalWS : TEXCOORD0; };
            V DNVert(uint vid : SV_VertexID, uint iid : SV_InstanceID)
            {
                V o;
                KitBlade bl = KitGrassBlade(vid, iid);
                o.positionCS = TransformWorldToHClip(KitGrassWorld(bl.positionOS, bl.h));
                o.normalWS = normalize(lerp(KitGrassNormalWS(bl.normalOS), half3(0, 1, 0), 0.6));
                return o;
            }
            half4 DNFrag(V i) : SV_Target
            {
                float3 n = normalize(i.normalWS);
                #if defined(_GBUFFER_NORMALS_OCT)
                float2 oct = PackNormalOctQuadEncode(n);
                return half4(PackFloat2To888(saturate(oct * 0.5 + 0.5)), 0.0);
                #else
                return half4(n, 0.0);
                #endif
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
