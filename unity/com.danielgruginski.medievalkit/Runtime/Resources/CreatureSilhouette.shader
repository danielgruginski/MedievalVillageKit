// Live creatures where something hides them, as a flat translucent colour (CreatureSilhouettes draws it with the
// creatures' and the player's renderers). Pass 0 marks stencil bit 0 wherever a creature or the player is the visible
// surface (both faces: the player's hair and cloth are two-sided); pass 1 draws a creature where it is behind something
// by more than the pull and not marked, once per pixel (so one flat colour: whichever layer lands first must not
// matter). Both slide each vertex toward the camera along its own view ray: the same pixel, a nearer depth. The fill's
// pull grows toward the feet (_FeetPull more at the mesh's origin, fading out by _FeetHeight): paws in the grass.
Shader "Hidden/MedievalGame/CreatureSilhouette"
{
    Properties
    {
        _SilColor ("Colour", Color) = (0.86, 0.3, 0.24, 0.55)
        _Pull ("Pull toward the camera (m)", Float) = 0.35
        _FeetPull ("More pull at the feet (m)", Float) = 0.6
        _FeetHeight ("Feet up to (m)", Float) = 0.6
        _MarkPull ("Mark pull (m)", Float) = 0.03
    }
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "RenderType" = "Opaque" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            half4 _SilColor;
            float _Pull;
            float _FeetPull;
            float _FeetHeight;
            float _MarkPull;
        CBUFFER_END

        struct Attributes
        {
            float4 positionOS : POSITION;
            UNITY_VERTEX_INPUT_INSTANCE_ID
        };

        struct Varyings
        {
            float4 positionCS : SV_POSITION;
            UNITY_VERTEX_OUTPUT_STEREO
        };

        Varyings Pulled(Attributes i, float pull, float feet)
        {
            Varyings o = (Varyings)0;
            UNITY_SETUP_INSTANCE_ID(i);
            UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
            float3 ws = TransformObjectToWorld(i.positionOS.xyz);
            float up = ws.y - TransformObjectToWorld(float3(0, 0, 0)).y;     // above the mesh's origin: the feet
            pull += feet * saturate(1 - up / max(_FeetHeight, 0.01));
            float3 v = GetCameraPositionWS() - ws;
            float len = max(length(v), 1e-4);
            ws += v * (min(pull, len - 0.5) / len);
            o.positionCS = TransformWorldToHClip(ws);
            return o;
        }

        Varyings VertMark(Attributes i) { return Pulled(i, _MarkPull, 0); }
        Varyings VertFill(Attributes i) { return Pulled(i, _Pull, _FeetPull); }

        half4 FragMark(Varyings i) : SV_Target { return 0; }
        half4 FragFill(Varyings i) : SV_Target { return _SilColor; }
        ENDHLSL

        Pass
        {
            Name "SilhouetteMark"
            ZTest LEqual
            ZWrite Off
            ColorMask 0
            Cull Off
            Stencil { Ref 1 ReadMask 1 WriteMask 1 Comp Always Pass Replace }
            HLSLPROGRAM
            #pragma vertex VertMark
            #pragma fragment FragMark
            #pragma multi_compile_instancing
            ENDHLSL
        }

        Pass
        {
            Name "SilhouetteFill"
            ZTest Greater
            ZWrite Off
            ColorMask RGB
            Cull Back
            Blend SrcAlpha OneMinusSrcAlpha
            Stencil { Ref 1 ReadMask 1 WriteMask 1 Comp NotEqual Pass Replace }
            HLSLPROGRAM
            #pragma vertex VertFill
            #pragma fragment FragFill
            #pragma multi_compile_instancing
            ENDHLSL
        }
    }
}
