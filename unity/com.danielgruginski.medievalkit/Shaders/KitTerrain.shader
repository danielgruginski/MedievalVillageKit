// The kit's object-space projected materials, ported from src/terrain/vk_terrain.py:
//   _KT_TERRAIN  terrain_material   grass / sand / dirt / cobble layers from the map's control texture, biplanar
//                                   cliffs with moss, TCol (R AO, G rock, B rim, A wet), macro tint
//   _KT_STAIR    stair_material     dressed stone with riser joints over cobbles (TCol G picks stone)
//   _KT_PAVING   paving_materials   cobbles, top projection (M_VKT_Paving) or box projection (M_VKT_Curb)
//   _KT_WATER    terrain_water_material  river water from two noises, slightly transparent
// Positions are Blender object coordinates (the meshes sit unrotated at their map origin): Unity's (-x, -z, y).
Shader "MedievalKit/KitTerrain"
{
    Properties
    {
        [KeywordEnum(Terrain, Stair, Paving, Water)] _KT("Recipe", Float) = 0
        [Toggle(_KT_BOX)] _Box("Box Projection (curb)", Float) = 0
        [NoScaleOffset] _MacroMap("Macro (data)", 2D) = "gray" {}
        [NoScaleOffset] _CtlMap("Ground Control (R dirt G cobble B sand A rock)", 2D) = "black" {}
        _CtlScale("Control Map Scale (1/(3W), 1/(3H))", Vector) = (0.01, 0.01, 0, 0)
        [NoScaleOffset] _GrassMap("Grass", 2D) = "white" {}
        [NoScaleOffset] _GrassH("Grass Height", 2D) = "gray" {}
        [NoScaleOffset] _SandMap("Sand", 2D) = "white" {}
        [NoScaleOffset] _SandH("Sand Height", 2D) = "gray" {}
        [NoScaleOffset] _DirtMap("Dirt", 2D) = "white" {}
        [NoScaleOffset] _DirtH("Dirt Height", 2D) = "gray" {}
        [NoScaleOffset] _CobbleMap("Cobble", 2D) = "white" {}
        [NoScaleOffset] _CobbleH("Cobble Height", 2D) = "gray" {}
        [NoScaleOffset] _CliffMap("Cliff", 2D) = "white" {}
        [NoScaleOffset] _CliffH("Cliff Height", 2D) = "gray" {}
        [NoScaleOffset] _MossMap("Moss", 2D) = "white" {}
        [NoScaleOffset] _MossH("Moss Height", 2D) = "gray" {}
        [NoScaleOffset] _StoneMap("Dressed Stone", 2D) = "white" {}
        [NoScaleOffset] _StoneH("Dressed Stone Height", 2D) = "gray" {}
        _ProjScale("Projection Scale (paving / curb)", Float) = 0.25
        _Rough("Roughness (paving / curb)", Range(0, 1)) = 0.8
        _BumpStrength("Bump Strength (paving / curb)", Range(0, 1)) = 0.5
        _Alpha("Alpha (water)", Range(0, 1)) = 0.9
        [HideInInspector] _BaseMap("", 2D) = "white" {}
        [HideInInspector] _BaseColor("", Color) = (1, 1, 1, 1)
        [HideInInspector] _Cutoff("", Float) = 0.5
        [HideInInspector] _SrcBlend("__src", Float) = 1
        [HideInInspector] _DstBlend("__dst", Float) = 0
        [HideInInspector] _ZWrite("__zw", Float) = 1
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "UniversalMaterialType" = "Lit" }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]
            Cull Off

            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _KT_TERRAIN _KT_STAIR _KT_PAVING _KT_WATER
            #pragma shader_feature_local_fragment _KT_BOX

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

            #define _SPECULAR_SETUP 1
            #include "KitTerrainInput.hlsl"
            #include "KitNoise.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 objB : TEXCOORD1;        // Blender object coordinates
                half3 normalWS : TEXCOORD2;
                half4 color : TEXCOORD3;
                half fogFactor : TEXCOORD4;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes v)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_TRANSFER_INSTANCE_ID(v, o);
                VertexPositionInputs vp = GetVertexPositionInputs(v.positionOS.xyz);
                o.positionCS = vp.positionCS;
                o.positionWS = vp.positionWS;
                o.objB = float3(-v.positionOS.x, -v.positionOS.z, v.positionOS.y);
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.color = v.color;
                o.fogFactor = ComputeFogFactor(vp.positionCS.z);
                return o;
            }

            #define S(t, uv) SAMPLE_TEXTURE2D(t, sampler_trilinear_repeat, uv)

            // biplanar side projection of vk_terrain's side_sample: image v = Blender z on every facing
            float4 SideSample(TEXTURE2D_PARAM(t, s), float3 p, float k, float ax, float ay)
            {
                float4 a = SAMPLE_TEXTURE2D(t, s, p.xz * k);
                float4 b = SAMPLE_TEXTURE2D(t, s, p.yz * k);
                return lerp(a, b, saturate((ax - ay) / 0.35 + 0.5));
            }

            void Layer(inout float3 col, inout float hgt, float3 Ck, float Hk, float w, float tau, float macB, float extra, bool outline)
            {
                float v = w - tau + (Hk - 0.5) * 0.35 + (macB - 0.5) * 0.15;
                float mk = max(saturate(v / 0.08 + 0.5), extra);
                col = lerp(col, Ck, mk);
                if (outline) col = lerp(col, float3(0.25, 0.2, 0.15), mk * (1 - mk) * 0.8 * 0.25);
                hgt = lerp(hgt, Hk, mk);
            }

            half4 Frag(Varyings i, bool front : SV_IsFrontFace) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(i);
                float3 p = i.objB;
                float3 N = normalize(i.normalWS) * (front ? 1 : -1);
                float Nz = N.y, ax = abs(N.x), ay = abs(N.z), az = abs(N.y);
                float3 col = 1; float hgt = 0.5; float rough = 0.8; float spec = 0.25;
                float bumpStr = 0.5, bumpDist = 0.04; float alpha = 1;

            #if defined(_KT_TERRAIN)
                float AO = i.color.r, RK = i.color.g, RIM = i.color.b, A = i.color.a;
                float3 p4 = p * 0.25;
                float3 mac = SAMPLE_TEXTURE2D(_MacroMap, sampler_trilinear_repeat, p.xy / 48.0).rgb;
                float3 pw = p + (KitNoise3(p, 0.35, 2.0) - 0.5) * 1.6;
                float4 ctl = SAMPLE_TEXTURE2D(_CtlMap, sampler_linear_clamp, pw.xy * _CtlScale.xy);
                // grass at two scales (the second turned 37 degrees), then Hue/Saturation/Value (0.505, 0.8, 0.97)
                float2 q = p.xy / 13.1;
                float cs37 = cos(radians(37.0)), sn37 = sin(radians(37.0));
                float2 q2 = float2(q.x * cs37 - q.y * sn37, q.x * sn37 + q.y * cs37);
                col = lerp(S(_GrassMap, p4.xy).rgb, S(_GrassMap, q2).rgb, smoothstep(0.3, 0.7, mac.b));
                col = KitHSV(col, 0.505, 0.8, 0.97);
                hgt = S(_GrassH, p4.xy).r;
                Layer(col, hgt, S(_SandMap, p4.xy).rgb, S(_SandH, p4.xy).r, ctl.b, 0.50, mac.b, smoothstep(0.2, 0.45, A), false);
                Layer(col, hgt, S(_DirtMap, p4.xy).rgb, S(_DirtH, p4.xy).r, ctl.r, 0.45, mac.b, 0, true);
                Layer(col, hgt, S(_CobbleMap, p4.xy).rgb, S(_CobbleH, p4.xy).r, ctl.g, 0.45, mac.b, 0, true);
                col = lerp(col, float3(0.66, 0.76, 0.38), RIM * 0.1);
                // cliffs: two biplanar samples blended by slow noise, rock from above on up-facing faces, tone drift
                float3 clC = SideSample(TEXTURE2D_ARGS(_CliffMap, sampler_trilinear_repeat), p, 1.0 / 6.0, ax, ay).rgb;
                float clH = SideSample(TEXTURE2D_ARGS(_CliffH, sampler_trilinear_repeat), p, 1.0 / 6.0, ax, ay).r;
                float3 po = p + float3(17.3, 5.9, 11.1);
                float3 clC2 = SideSample(TEXTURE2D_ARGS(_CliffMap, sampler_trilinear_repeat), po, 1.0 / 9.3, ax, ay).rgb;
                float clH2 = SideSample(TEXTURE2D_ARGS(_CliffH, sampler_trilinear_repeat), po, 1.0 / 9.3, ax, ay).r;
                float cbl = smoothstep(0.4, 0.6, KitNoise(p, 0.11, 1.5));
                clC = lerp(clC, clC2, cbl); clH = lerp(clH, clH2, cbl);
                float wz = smoothstep(0.6, 0.85, az);
                clC = lerp(clC, S(_CliffMap, p.xy / 6.0).rgb, wz); clH = lerp(clH, S(_CliffH, p.xy / 6.0).r, wz);
                clC *= lerp(float3(0.84, 0.84, 0.86), float3(1.08, 1.03, 0.95), smoothstep(0.3, 0.7, KitNoise(p, 0.045, 1.0)));
                float rockW = max(max(RK, smoothstep(0.80, 0.55, Nz)), smoothstep(0.45, 0.65, ctl.a));
                // moss on up-facing rock, in patches, toned towards the rock
                float3 mo = S(_MossMap, p.xy).rgb;
                float mz = smoothstep(0.54, 0.78, Nz + (S(_MossH, p.xy).r - 0.5) * 0.75);
                mz *= smoothstep(0.52, 0.6, KitNoise(p, 0.55, 3.0));
                float3 ccol = lerp(clC, lerp(mo, clC, 0.3), mz);
                col = lerp(col, ccol, rockW); hgt = lerp(hgt, clH, rockW);
                col *= AO;
                float wet = smoothstep(0.6, 0.95, A);
                col = lerp(col, 0, wet * 0.4);
                col *= 0.9 + mac.r * 0.2;
                col = lerp(col, col * float3(1.05, 1.0, 0.8), mac.g * 0.3);
                rough = lerp(lerp(0.9, 0.85, rockW), 0.35, wet);
                bumpStr = lerp(0.4, 0.8, rockW); bumpDist = 0.05;

            #elif defined(_KT_STAIR)
                float3 pc = p * 0.25;
                float3 cC = S(_CobbleMap, pc.xy).rgb; float cH = S(_CobbleH, pc.xy).r;
                float3 sC = SideSample(TEXTURE2D_ARGS(_StoneMap, sampler_trilinear_repeat), p, 0.8, ax, ay).rgb;
                float sH = SideSample(TEXTURE2D_ARGS(_StoneH, sampler_trilinear_repeat), p, 0.8, ax, ay).r;
                float wz = smoothstep(0.55, 0.8, az);
                sC = lerp(sC, S(_StoneMap, p.xy * 0.8).rgb, wz); sH = lerp(sH, S(_StoneH, p.xy * 0.8).r, wz);
                float joint = (1 - smoothstep(0.008, 0.022, KitVoronoiEdge1D(p.x + p.y, 1.7, 0.8))) * (1 - wz);
                sC = lerp(sC, float3(0.16, 0.14, 0.12), joint * 0.75); sH = lerp(sH, 0, joint);
                float stone = smoothstep(0.4, 0.6, i.color.g);
                col = lerp(cC, sC, stone) * i.color.r;
                hgt = lerp(cH, sH, stone);
                rough = lerp(0.82, 0.78, stone);
                bumpStr = lerp(0.55, 0.45, stone);

            #elif defined(_KT_PAVING)
                float3 pp = p * _ProjScale;
                #if defined(_KT_BOX)
                    // Blender BOX projection, blend 0.2
                    float3 w = pow(abs(N.xzy), 4); w /= (w.x + w.y + w.z);
                    float4 c4 = S(_StoneMap, pp.yz) * w.x + S(_StoneMap, pp.xz) * w.y + S(_StoneMap, pp.xy) * w.z;
                    hgt = S(_StoneH, pp.yz).r * w.x + S(_StoneH, pp.xz).r * w.y + S(_StoneH, pp.xy).r * w.z;
                    col = c4.rgb;
                #else
                    col = S(_CobbleMap, pp.xy).rgb; hgt = S(_CobbleH, pp.xy).r;
                #endif
                col *= i.color.rgb;
                rough = _Rough; bumpStr = _BumpStrength;

            #elif defined(_KT_WATER)
                float3 st = p * float3(0.18, 1.4, 1.0);
                float n1 = KitNoise(st, 0.9, 4.0);
                float n2 = KitNoise(p, 0.12, 1.0);
                col = lerp(float3(0.035, 0.17, 0.2), float3(0.06, 0.27, 0.28), smoothstep(0.35, 0.65, n2));
                col = lerp(col, float3(0.55, 0.75, 0.75), smoothstep(0.62, 0.8, n1) * 0.35);
                hgt = n1; rough = 0.05; spec = 0.6; bumpStr = 0.15; alpha = _Alpha;
            #endif

                float3 n = KitBump(i.positionWS, N, hgt, bumpStr, bumpDist);

                SurfaceData s = (SurfaceData)0;
                s.albedo = col;
                s.specular = 0.08 * spec;
                s.smoothness = 1 - rough;
                s.normalTS = half3(0, 0, 1);
                s.occlusion = 1;
                s.alpha = alpha;

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
                c.rgb = MixFog(c.rgb, d.fogCoord);
                c.a = alpha;
                return c;
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On ZTest LEqual ColorMask 0 Cull Off
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "KitTerrainInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/ShadowCasterPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On ColorMask R Cull Off
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex DepthOnlyVertex
            #pragma fragment DepthOnlyFragment
            #pragma multi_compile_instancing
            #include "KitTerrainInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthOnlyPass.hlsl"
            ENDHLSL
        }

        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode" = "DepthNormals" }
            ZWrite On Cull Off
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex DepthNormalsVertex
            #pragma fragment DepthNormalsFragment
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/RenderingLayers.hlsl"
            #include "KitTerrainInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthNormalsPass.hlsl"
            ENDHLSL
        }
    }
    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
