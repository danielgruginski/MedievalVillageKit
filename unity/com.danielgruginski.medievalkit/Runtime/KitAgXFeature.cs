using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;
using UnityEngine.Rendering.Universal;

namespace MedievalKit
{
    /// <summary>Runs KitAgX before URP's post-processing (camera colour is still HDR there).</summary>
    public class KitAgXFeature : ScriptableRendererFeature
    {
        public Shader shader;
        Material material;
        Pass pass;

        public override void Create()
        {
            if (shader == null) shader = Shader.Find("Hidden/MedievalKit/AgX");
            if (shader != null) material = CoreUtils.CreateEngineMaterial(shader);
            pass = new Pass(material) { renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing };
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            if (material == null) return;
            var agx = VolumeManager.instance.stack.GetComponent<KitAgX>();
            if (agx == null || !agx.IsActive()) return;
            if (renderingData.cameraData.cameraType == CameraType.Preview) return;
            renderer.EnqueuePass(pass);
        }

        protected override void Dispose(bool disposing) => CoreUtils.Destroy(material);

        class Pass : ScriptableRenderPass
        {
            static readonly int ExposureId = Shader.PropertyToID("_KitExposure");
            static readonly int ContrastId = Shader.PropertyToID("_KitContrast");
            readonly Material material;

            public Pass(Material m)
            {
                material = m;
                requiresIntermediateTexture = true;
            }

            public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
            {
                var res = frameData.Get<UniversalResourceData>();
                if (res.isActiveTargetBackBuffer) return;
                var agx = VolumeManager.instance.stack.GetComponent<KitAgX>();
                material.SetFloat(ExposureId, Mathf.Pow(2f, agx.exposure.value));
                material.SetFloat(ContrastId, agx.contrast.value);
                var src = res.activeColorTexture;
                var desc = renderGraph.GetTextureDesc(src);
                desc.name = "KitAgX";
                desc.clearBuffer = false;
                var dst = renderGraph.CreateTexture(desc);
                renderGraph.AddBlitPass(new RenderGraphUtils.BlitMaterialParameters(src, dst, material, 0), "Kit AgX");
                res.cameraColor = dst;
            }
        }
    }
}
