// The sea (KitVillage's terrain "sea": the water quads Sea() merges), a cartoony port of VoxelRealm's VoxelWaterLit:
//   - transparent, ZWrite Off; refracts the opaque scene (URP Opaque + Depth textures: on in PC_RPAsset)
//   - a domain-warped five-wave ripple field for the normal, crossfaded to a coarse swell with distance, gust patches,
//     distance calming (VoxelWaterLit's anti-tiling)
//   - colour by the water's depth over the bed in a few hard bands (shallow -> deep), fresnel to the deep tint
//   - foam where the scene sits just behind the surface (the quay walls, hulls, piles, the beach): a hard-edged ragged
//     band plus a thin second line further out, drifting. Depths are true vertical ones (the scene rebuilt in world
//     space): the kit's sea is shallow (its bed 0.9 m under the water), so the foam's depths stay well under that
//   - a stepped sun glint (cartoony sparkles), lit by URP's main light (its shadows: ships shade the water) + ambient
//   - Stencil: pixels a KitWaterMask marked (bit 8: a hull's waterline footprint, KitVillage.SeaMasks) get no water,
//     so a boat sitting low stays dry inside
Shader "MedievalKit/KitSea"
{
    Properties
    {
        _ShallowColor("Shallow Color", Color) = (0.30, 0.72, 0.74, 1)
        _DeepColor("Deep Color", Color) = (0.06, 0.24, 0.40, 1)
        _DepthMax("Depth For Deep (m)", Range(0.2, 6)) = 1.6
        _ColorBands("Colour Bands (0 = smooth)", Range(0, 6)) = 3
        _BaseOpacity("Base Opacity (top-down)", Range(0, 1)) = 0.6
        _FresnelPower("Fresnel Power", Range(0.5, 8)) = 3.0

        _RippleScale("Ripple Scale", Float) = 0.55
        _RippleSpeed("Ripple Speed", Float) = 1.2
        _RippleNoise("Ripple Irregularity", Range(0, 1)) = 0.6
        _RippleStrength("Ripple Strength", Range(0, 0.5)) = 0.14
        _RefractionStrength("Refraction Strength", Range(0, 0.15)) = 0.03
        _RefractEdgeFade("Refraction Edge Fade (depth)", Range(0.01, 2)) = 0.35

        [Header(Glint)]
        _SpecStrength("Glint Strength", Range(0, 3)) = 1.2
        _GlintThreshold("Glint Threshold (stepped)", Range(0, 1)) = 0.55

        [Header(Foam)]
        _FoamColor("Foam Color", Color) = (0.95, 0.98, 1.0, 1)
        _FoamDistance("Foam Band Width (m of depth)", Range(0, 3)) = 0.28
        _FoamStrength("Foam Strength", Range(0, 1)) = 0.9
        _FoamScale("Foam Texture Scale", Float) = 2.2
        _FoamSpeed("Foam Drift Speed", Float) = 0.35
        _FoamHardness("Foam Edge Hardness", Range(0, 1)) = 0.8
        _FoamLine("Second Line Depth (m)", Range(0, 3)) = 0.4
        _FoamLineWidth("Second Line Width (m)", Range(0, 0.5)) = 0.04
        _FoamMinDepth("Foam Seam Cutoff", Range(0, 0.5)) = 0.03

        [Header(Anti tiling)]
        _WaveLodStart("Crossfade Start Distance", Float) = 24.0
        _WaveLodEnd("Crossfade End Distance", Float) = 90.0
        _FarScaleRatio("Far Wave Scale Ratio", Range(0.05, 1)) = 0.22
        _GustScale("Gust Scale (world)", Float) = 0.035
        _GustAmount("Gust Amount", Range(0, 1)) = 0.5
        _DistanceCalm("Distance Calming", Range(0, 0.05)) = 0.008
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent+1" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }

        Pass
        {
            Name "ForwardSea"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off
            Stencil { Ref 8 ReadMask 8 Comp NotEqual }

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareOpaqueTexture.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ShallowColor, _DeepColor;
                half _DepthMax, _ColorBands, _BaseOpacity, _FresnelPower;
                float _RippleScale, _RippleSpeed;
                half _RippleNoise, _RippleStrength, _RefractionStrength, _RefractEdgeFade;
                half _SpecStrength, _GlintThreshold;
                half4 _FoamColor;
                half _FoamDistance, _FoamStrength;
                float _FoamScale, _FoamSpeed;
                half _FoamHardness, _FoamLine, _FoamLineWidth, _FoamMinDepth;
                float _WaveLodStart, _WaveLodEnd, _FarScaleRatio, _GustScale;
                half _GustAmount;
                float _DistanceCalm;
            CBUFFER_END

            struct Attributes { float3 positionOS : POSITION; float3 normalOS : NORMAL; };
            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS   : TEXCOORD1;
                float  fogFactor  : TEXCOORD2;
            };

            Varyings Vert(Attributes v)
            {
                Varyings o;
                VertexPositionInputs p = GetVertexPositionInputs(v.positionOS);
                o.positionCS = p.positionCS; o.positionWS = p.positionWS;
                o.normalWS = TransformObjectToWorldNormal(v.normalOS);
                o.fogFactor = ComputeFogFactor(p.positionCS.z);
                return o;
            }

            float2 RippleWave(float2 p, float2 dir, float freq, float spd, float amp, float t)
            {
                float phase = dot(dir, p) * freq + t * spd;
                return dir * (amp * freq * cos(phase));
            }

            float2 RippleField(float2 p, float t)
            {
                float2 warp;
                warp.x = sin(p.y * 0.7 + t * 0.6) + 0.5 * sin(p.y * 1.9 - t * 1.1);
                warp.y = sin(p.x * 0.7 - t * 0.5) + 0.5 * sin(p.x * 1.9 + t * 0.9);
                p += warp * (_RippleNoise * 0.6);
                float2 s = 0;
                s += RippleWave(p, normalize(float2( 0.90,  0.44)), 1.00, 1.00, 0.50, t);
                s += RippleWave(p, normalize(float2(-0.30,  0.95)), 1.63, 1.27, 0.31, t);
                s += RippleWave(p, normalize(float2( 0.60, -0.80)), 2.41, 0.83, 0.21, t);
                s += RippleWave(p, normalize(float2(-0.85, -0.53)), 3.77, 1.51, 0.13, t);
                s += RippleWave(p, normalize(float2( 0.15,  0.99)), 5.13, 1.09, 0.10, t);
                return s;
            }

            half Band(half x)          // the cartoon: x in _ColorBands soft-edged steps (0 = smooth)
            {
                if (_ColorBands < 0.5) return x;
                half f = saturate(x) * _ColorBands, k = floor(f);
                return (k + smoothstep(0.42, 0.58, f - k)) / _ColorBands;
            }

            half4 Frag(Varyings i, FRONT_FACE_TYPE face : FRONT_FACE_SEMANTIC) : SV_Target
            {
                float3 geoN = normalize(i.normalWS) * IS_FRONT_VFACE(face, 1.0, -1.0);
                float3 V = normalize(GetWorldSpaceViewDir(i.positionWS));
                float viewDist = length(_WorldSpaceCameraPos - i.positionWS);

                // ---- ripples, distance crossfade, gusts, calming ----
                float t = _Time.y * _RippleSpeed;
                float2 slopeFine = RippleField(i.positionWS.xz * _RippleScale, t);
                float2 slopeCoarse = RippleField(i.positionWS.xz * (_RippleScale * _FarScaleRatio), t);
                float2 slope = lerp(slopeFine, slopeCoarse, smoothstep(_WaveLodStart, max(_WaveLodStart + 1.0, _WaveLodEnd), viewDist));
                float2 g = (i.positionWS.xz - float2(0.7, 0.3) * _Time.y) * _GustScale;
                float gm = 0.5 + 0.5 * sin(g.x * 6.2832 + sin(g.y * 3.7)) * sin(g.y * 6.2832 + sin(g.x * 4.3) + t * 0.15);
                slope *= lerp(1.0 - _GustAmount, 1.0, gm) / (1.0 + viewDist * _DistanceCalm);
                float up = saturate(geoN.y);
                float3 N = normalize(geoN + float3(-slope.x, 0, -slope.y) * (_RippleStrength * up));

                // ---- refraction (edge-aware), depth below the surface ----
                float2 suv = GetNormalizedScreenSpaceUV(i.positionCS);
                float waterEye = LinearEyeDepth(i.positionCS.z, _ZBufferParams);
                float sceneEye0 = LinearEyeDepth(SampleSceneDepth(suv), _ZBufferParams);
                float refrEdge = saturate((sceneEye0 - waterEye) / max(_RefractEdgeFade, 1e-3));
                float2 ruv = suv + slope * (_RefractionStrength * up * refrEdge / (1.0 + viewDist * 0.05));
                float sceneEye = LinearEyeDepth(SampleSceneDepth(ruv), _ZBufferParams);
                if (sceneEye < waterEye) { ruv = suv; sceneEye = sceneEye0; }
                half3 refracted = SampleSceneColor(ruv);
                // the water's true vertical depth here: the scene point behind the surface (unrefracted, so it holds
                // still), rebuilt in world space from the depth buffer; nothing behind (past the bed's edge): deep
                float rawD = SampleSceneDepth(suv);
                float3 sceneWS = ComputeWorldSpacePosition(suv, rawD, UNITY_MATRIX_I_VP);
                float depth = (sceneEye0 - waterEye > 80.0) ? 80.0 : max(0.0, i.positionWS.y - sceneWS.y);

                // ---- light ----
                Light sun = GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                half shadow = lerp(0.55, 1.0, sun.shadowAttenuation);
                half3 lighting = sun.color * (0.55 + 0.45 * saturate(dot(N, sun.direction))) * shadow + SampleSH(N) * 0.6;

                // ---- colour: banded depth gradient, fresnel ----
                half dk = Band(saturate(depth / _DepthMax));
                half fres = pow(1.0 - saturate(dot(V, geoN)), _FresnelPower);
                half3 tint = lerp(_ShallowColor.rgb, _DeepColor.rgb, saturate(dk + fres * 0.5));
                half opacity = saturate(lerp(_BaseOpacity, 1.0, max(fres, dk * 0.6)));
                half3 body = lerp(refracted, tint * lighting, opacity);

                // ---- foam: a ragged hard band at the contact, a thin line further out ----
                float2 fp = i.positionWS.xz * _FoamScale;
                float ft = _Time.y * _FoamSpeed;
                float foamTex = 0.5 + 0.5 * sin(fp.x + sin(fp.y * 1.3 + ft) + ft) * sin(fp.y - sin(fp.x * 1.1 - ft) + ft * 0.8);
                float edge = _FoamDistance * (0.45 + 0.55 * foamTex);
                float foam = 1.0 - saturate(depth / max(edge, 1e-3));
                float hard = lerp(0.45, 0.02, _FoamHardness);
                foam = smoothstep(0.5 - hard, 0.5 + hard, foam);
                float lineD = _FoamLine * (0.85 + 0.3 * foamTex);
                float line2 = 1.0 - smoothstep(0.0, max(_FoamLineWidth, 1e-3), abs(depth - lineD));
                line2 *= step(0.35, foamTex);                                     // broken into dashes
                foam = saturate(max(foam, line2 * 0.85)) * up * _FoamStrength * smoothstep(0.0, _FoamMinDepth, depth);
                body = lerp(body, _FoamColor.rgb * lighting, foam);

                // ---- stepped sun glint ----
                float3 H = SafeNormalize(sun.direction + V);
                half spec = pow(saturate(dot(N, H)), 96.0);
                spec = smoothstep(_GlintThreshold, _GlintThreshold + 0.05, spec) * _SpecStrength * sun.shadowAttenuation * (1 - foam);

                half3 color = body + sun.color * spec;
                color = MixFog(color, i.fogFactor);
                return half4(color, 1.0);
            }
            ENDHLSL
        }
        // no DepthOnly / ShadowCaster: the water neither hides what lies under it from the depth texture nor shades
    }
}
