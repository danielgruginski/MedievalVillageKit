// Lit shader for the Medieval Village Kit (URP 17, Forward and Forward+).
// Mirrors the kit's Blender materials: painted texture x vertex colour (baked AO / grime) x per-object jitter,
// roughness map, normal map, Blender's specular level, emission and the vki_rim glow gradient.
Shader "MedievalKit/KitLit"
{
    Properties
    {
        _BaseMap("Base Map", 2D) = "white" {}
        _BaseColor("Base Color", Color) = (1, 1, 1, 1)
        [Toggle(_VKX_VERTEX_COLOR)] _UseVertexColor("Multiply Vertex Colour", Float) = 1
        _Jitter("Per-object brightness (x min, y max)", Vector) = (1, 1, 0, 0)
        [Normal][NoScaleOffset] _BumpMap("Normal Map", 2D) = "bump" {}
        _BumpScale("Normal Strength", Float) = 1
        [NoScaleOffset] _RoughMap("Roughness Map", 2D) = "white" {}
        _RoughScale("Roughness Map Scale", Float) = 1
        _Roughness("Roughness (no map)", Range(0, 1)) = 0.5
        _Metallic("Metallic", Range(0, 1)) = 0
        _Specular("Specular Level (Blender)", Range(0, 1)) = 0.5
        [NoScaleOffset] _EmissionMap("Emission Map", 2D) = "white" {}
        [HDR] _EmissionColor("Emission", Color) = (0, 0, 0, 1)
        [Toggle(_VKX_RIM)] _UseRim("Rim Glow (vertex alpha)", Float) = 0
        [HDR] _RimColorA("Rim Colour at 0", Color) = (0, 0, 0, 1)
        [HDR] _RimColorB("Rim Colour at 1", Color) = (1, 1, 1, 1)
        _RimK("Rim Strength (rim * x + y)", Vector) = (1, 0, 0, 0)
        [Toggle(_VKX_MOSS)] _UseMoss("Moss On Top (Blender mossy_material)", Float) = 0
        [NoScaleOffset] _MossMap("Moss Base", 2D) = "white" {}
        [Normal][NoScaleOffset] _MossBumpMap("Moss Normal", 2D) = "bump" {}
        [NoScaleOffset] _MossRoughMap("Moss Roughness", 2D) = "white" {}
        [NoScaleOffset] _MossHeightMap("Moss Height", 2D) = "gray" {}
        _MossTile("Moss Tiling (x base UV)", Float) = 1
        _MossNoise("Moss Height Noise (h * x + y)", Vector) = (0.5, -0.25, 0, 0)
        _MossRange("Moss Threshold (smoothstep x..y of up + noise)", Vector) = (0.38, 0.66, 0, 0)
        _Translucency("Translucency (leaves: share lit from behind)", Range(0, 1)) = 0
        [Toggle(_ALPHATEST_ON)] _AlphaClip("Alpha Clip", Float) = 0
        _Cutoff("Alpha Cutoff", Range(0, 1)) = 0.5
        [HideInInspector] _Surface("__surface", Float) = 0
        [HideInInspector] _SrcBlend("__src", Float) = 1
        [HideInInspector] _DstBlend("__dst", Float) = 0
        [HideInInspector] _ZWrite("__zw", Float) = 1
        [Enum(UnityEngine.Rendering.CullMode)] _Cull("Cull", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "UniversalMaterialType" = "Lit" "IgnoreProjector" = "True" }
        LOD 300

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex KitVert
            #pragma fragment KitFrag

            #pragma shader_feature_local _VKX_VERTEX_COLOR
            #pragma shader_feature_local _VKX_RIM
            #pragma shader_feature_local _NORMALMAP
            #pragma shader_feature_local_fragment _ALPHATEST_ON
            #pragma shader_feature_local_fragment _SURFACE_TYPE_TRANSPARENT
            #pragma shader_feature_local_fragment _VKX_ROUGHMAP
            #pragma shader_feature_local_fragment _EMISSION
            #pragma shader_feature_local_fragment _VKX_MOSS

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
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"

            #define _SPECULAR_SETUP 1
            #include "KitLitInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "KitSeeThrough.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float4 tangentOS : TANGENT;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                half4 tangentWS : TEXCOORD3;
                half4 color : TEXCOORD4;
                half fogFactor : TEXCOORD5;
                half jitter : TEXCOORD6;
                #ifdef _ADDITIONAL_LIGHTS_VERTEX
                half3 vertexLight : TEXCOORD7;
                #endif
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings KitVert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                VertexPositionInputs vp = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs vn = GetVertexNormalInputs(input.normalOS, input.tangentOS);
                o.positionCS = vp.positionCS;
                o.positionWS = vp.positionWS;
                o.normalWS = vn.normalWS;
                o.tangentWS = half4(vn.tangentWS, input.tangentOS.w * GetOddNegativeScale());
                o.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                o.color = input.color;
                o.fogFactor = ComputeFogFactor(vp.positionCS.z);
                o.jitter = lerp(_Jitter.x, _Jitter.y, KitObjectRandom());
                #ifdef _ADDITIONAL_LIGHTS_VERTEX
                o.vertexLight = VertexLighting(vp.positionWS, vn.normalWS);
                #endif
                return o;
            }

            half4 KitFrag(Varyings input, bool frontFace : SV_IsFrontFace) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                half4 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv);
                half alpha = tex.a * _BaseColor.a;
                #ifdef _ALPHATEST_ON
                clip(alpha - _Cutoff);
                #endif
                KitSeeThroughClip(input.positionWS, input.positionCS.xy);
                half3 n = normalize(input.normalWS);
                n = frontFace ? n : -n;     // the kit's cards and open-backed pieces render both sides

                half rough = _Roughness;
                #ifdef _VKX_ROUGHMAP
                rough = saturate(SAMPLE_TEXTURE2D(_RoughMap, sampler_RoughMap, input.uv).r * _RoughScale);
                #endif
                half4 nrmTex = SAMPLE_TEXTURE2D(_BumpMap, sampler_BumpMap, input.uv);

                #ifdef _VKX_MOSS
                // Blender: smoothstep(range, normal.z + height * k0 + k1) x vertex alpha; maps mixed before decoding
                float2 muv = input.uv * _MossTile;
                half mh = SAMPLE_TEXTURE2D(_MossHeightMap, sampler_BaseMap, muv).r;
                half moss = smoothstep(_MossRange.x, _MossRange.y, n.y + mh * _MossNoise.x + _MossNoise.y) * input.color.a;
                tex.rgb = lerp(tex.rgb, SAMPLE_TEXTURE2D(_MossMap, sampler_BaseMap, muv).rgb, moss);
                rough = lerp(rough, SAMPLE_TEXTURE2D(_MossRoughMap, sampler_BaseMap, muv).r, moss);
                nrmTex = lerp(nrmTex, SAMPLE_TEXTURE2D(_MossBumpMap, sampler_BumpMap, muv), moss);
                #endif

                half3 albedo = tex.rgb * _BaseColor.rgb * input.jitter;
                #ifdef _VKX_VERTEX_COLOR
                albedo *= input.color.rgb;
                #endif

                #ifdef _NORMALMAP
                half3 nts = UnpackNormalScale(nrmTex, _BumpScale);
                half3 t = normalize(input.tangentWS.xyz);
                half3 b = cross(n, t) * input.tangentWS.w;
                n = normalize(TransformTangentToWorld(nts, half3x3(t, b, n)));
                #endif

                half3 emission = 0;
                #ifdef _EMISSION
                emission = SAMPLE_TEXTURE2D(_EmissionMap, sampler_BaseMap, input.uv).rgb * _EmissionColor.rgb;
                #endif
                #ifdef _VKX_RIM
                half rim = input.color.a;
                emission += lerp(_RimColorA.rgb, _RimColorB.rgb, rim) * max(0, rim * _RimK.x + _RimK.y);
                #endif

                SurfaceData s = (SurfaceData)0;
                s.albedo = albedo * (1 - _Metallic);
                s.specular = lerp(0.08 * _Specular.xxx, albedo, _Metallic);
                s.metallic = 0;
                s.smoothness = 1 - rough;
                s.normalTS = half3(0, 0, 1);
                s.emission = emission;
                s.occlusion = 1;
                s.alpha = alpha;

                InputData d = (InputData)0;
                d.positionWS = input.positionWS;
                d.positionCS = input.positionCS;
                d.normalWS = n;
                d.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input.positionWS);
                #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
                d.shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                #endif
                d.fogCoord = InitializeInputDataFog(float4(input.positionWS, 1), input.fogFactor);
                #ifdef _ADDITIONAL_LIGHTS_VERTEX
                d.vertexLighting = input.vertexLight;
                #endif
                d.bakedGI = SampleSH(n);
                d.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                d.shadowMask = half4(1, 1, 1, 1);

                // Blender: (1 - t) x surface + t x Translucent BSDF, which takes light arriving on the other side
                half tl = _Translucency;
                s.albedo *= 1 - tl;
                s.specular *= 1 - tl;
                half4 c = UniversalFragmentPBR(d, s);
                if (tl > 0)
                {
                    half3 back = SampleSH(-n);
                    Light ml = GetMainLight(d.shadowCoord, d.positionWS, d.shadowMask);
                    back += ml.color * ml.distanceAttenuation * ml.shadowAttenuation * saturate(dot(-n, ml.direction));
                    c.rgb += albedo * tl * back;
                }
                c.rgb = MixFog(c.rgb, d.fogCoord);
                #ifndef _SURFACE_TYPE_TRANSPARENT
                c.a = 1;
                #endif
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
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            #pragma shader_feature_local _ALPHATEST_ON
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "KitLitInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/ShadowCasterPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex DepthOnlyVertex
            #pragma fragment KitDepthOnlyFragment
            #pragma shader_feature_local _ALPHATEST_ON
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include "KitLitInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthOnlyPass.hlsl"
            #include "KitSeeThrough.hlsl"

            half KitDepthOnlyFragment(Varyings input) : SV_TARGET
            {
                KitSeeThroughClipCS(input.positionCS);
                return DepthOnlyFragment(input);
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex DepthNormalsVertex
            #pragma fragment KitDepthNormalsFragment
            #pragma shader_feature_local _ALPHATEST_ON
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #include "KitLitInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthNormalsPass.hlsl"
            #include "KitSeeThrough.hlsl"

            void KitDepthNormalsFragment(Varyings input, out half4 outNormalWS : SV_Target0
            #ifdef _WRITE_RENDERING_LAYERS
                , out uint outRenderingLayers : SV_Target1
            #endif
            )
            {
                KitSeeThroughClipCS(input.positionCS);
                DepthNormalsFragment(input, outNormalWS
                #ifdef _WRITE_RENDERING_LAYERS
                    , outRenderingLayers
                #endif
                );
            }
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
