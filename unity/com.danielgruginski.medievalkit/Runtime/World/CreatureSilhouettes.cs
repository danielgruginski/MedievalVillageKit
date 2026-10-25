using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// Live creatures hidden by a wall, a rock or a roof show where they are hidden as a flat translucent red, so they can
    /// be seen and clicked (<see cref="ClickToMove"/> picks them through what is in front). A render pass the game camera
    /// queues each frame (no renderer asset change). A creature's renderers carry rendering layer <see cref="Bit"/>
    /// (<see cref="Creature"/> sets it and clears it on death); the player's carry <see cref="MarkBit"/>, so a rat behind
    /// the player does not show through the player. Hidden means more than <see cref="pull"/> metres behind what is
    /// drawn there: a rat's own far side and the ground under its belly do not count, nor, on a level with grass, its
    /// paws among the blades (<see cref="feetPull"/>; off in the caves, where it would cut the near half off a rat
    /// against a wall). Resources/CreatureSilhouette.shader.
    /// <para>The bits are 6 and 7 (2026-10-15; they were 8 and 9): the kit's see-through keeps a building's tag in bits
    /// 8-14 (KitSeeThrough.TagShift) and its own flags and cut in 15-31, so every building with an odd tag was drawn as
    /// a creature -- flat red wherever grass, a fern or the ground hid part of it (the user's shots: a tower's foot, a
    /// cottage behind a fern, red lines along its eaves). 1-7 are free (the project's light layers, unused: every
    /// saved renderer and light has mask 1).</para>
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public class CreatureSilhouettes : MonoBehaviour
    {
        /// <summary>how many actors could be drawn as silhouettes: the game sets it (its live creatures); 0 skips the
        /// pass</summary>
        public static System.Func<int> ActorCount = () => 1;

        public const int Bit = 6, MarkBit = 7;
        public static uint Mask => 1u << Bit;
        public static uint MarkMask => 1u << MarkBit;

        [Tooltip("The silhouette's colour; alpha: how much of it covers what hides the creature.")]
        public Color colour = new Color(0.86f, 0.30f, 0.24f, 0.55f);
        [Tooltip("Something less than this far (m) in front of a creature does not hide it.")]
        public float pull = 0.35f;
        [Tooltip("On a level with grass: this much more at the feet, fading out 0.6 m up (blades in front of the paws).")]
        public float feetPull = 0.6f;

        static readonly int ColourId = Shader.PropertyToID("_SilColor"), PullId = Shader.PropertyToID("_Pull"),
                            FeetPullId = Shader.PropertyToID("_FeetPull");
        Camera cam;
        Material mat;
        Pass pass;
        Scene level;
        bool grass;

        /// <summary>a body's renderers (inactive ones too) on or off the silhouettes: a creature's are drawn where hidden,
        /// anyone else's (the player's) only hide the creatures behind them. Either way never cut by the kit's see-through
        /// (KitSeeThrough.KeepBit: a body's props are drawn with the kit's materials)</summary>
        public static void Tag(GameObject go, bool creature, bool on = true)
        {
            if (go == null) return;
            uint bit = creature ? Mask : MarkMask;
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
                r.renderingLayerMask = (on ? r.renderingLayerMask | bit : r.renderingLayerMask & ~bit) | MedievalKit.KitSeeThrough.KeepBit;
        }

        void OnEnable()
        {
            cam = GetComponent<Camera>();
            var sh = Resources.Load<Shader>("CreatureSilhouette");
            if (sh == null || !sh.isSupported) { Debug.LogWarning("[CreatureSilhouettes] no CreatureSilhouette shader"); enabled = false; return; }
            mat = CoreUtils.CreateEngineMaterial(sh);
            pass = new Pass(mat) { renderPassEvent = RenderPassEvent.AfterRenderingTransparents };
            RenderPipelineManager.beginCameraRendering += Queue;
        }

        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering -= Queue;
            CoreUtils.Destroy(mat);
            mat = null;
        }

        void Queue(ScriptableRenderContext ctx, Camera c)
        {
            if (c != cam || mat == null || ActorCount() == 0) return;
            var here = SceneManager.GetActiveScene();
            if (here != level) { level = here; grass = FindAnyObjectByType<MedievalKit.KitGrass>() != null; }    // a new level
            mat.SetColor(ColourId, colour);
            mat.SetFloat(PullId, pull);
            mat.SetFloat(FeetPullId, grass ? feetPull : 0f);
            c.GetUniversalAdditionalCameraData().scriptableRenderer.EnqueuePass(pass);      // the queue empties each frame
        }

        class Pass : ScriptableRenderPass
        {
            static readonly List<ShaderTagId> Tags = new List<ShaderTagId>
            {
                new ShaderTagId("UniversalForward"), new ShaderTagId("UniversalForwardOnly"), new ShaderTagId("SRPDefaultUnlit"),
            };

            class Data { public RendererListHandle mark, fill; }

            readonly Material mat;

            public Pass(Material m)
            {
                mat = m;
                requiresIntermediateTexture = true;
                profilingSampler = new ProfilingSampler("Creature Silhouettes");
            }

            public override void RecordRenderGraph(RenderGraph rg, ContextContainer frame)
            {
                var res = frame.Get<UniversalResourceData>();
                if (res.isActiveTargetBackBuffer) return;
                var rd = frame.Get<UniversalRenderingData>();
                var cd = frame.Get<UniversalCameraData>();
                var ld = frame.Get<UniversalLightData>();
                var ds = RenderingUtils.CreateDrawingSettings(Tags, rd, cd, ld, SortingCriteria.CommonOpaque);
                ds.overrideMaterial = mat;
                ds.perObjectData = PerObjectData.None;
                ds.overrideMaterialPassIndex = 0;
                var markP = new RendererListParams(rd.cullResults, ds, new FilteringSettings(RenderQueueRange.opaque, -1, Mask | MarkMask));
                ds.overrideMaterialPassIndex = 1;
                var fillP = new RendererListParams(rd.cullResults, ds, new FilteringSettings(RenderQueueRange.opaque, -1, Mask));

                using var b = rg.AddRasterRenderPass<Data>("Creature Silhouettes", out var d, profilingSampler);
                d.mark = rg.CreateRendererList(markP);
                d.fill = rg.CreateRendererList(fillP);
                b.UseRendererList(d.mark);
                b.UseRendererList(d.fill);
                b.SetRenderAttachment(res.activeColorTexture, 0, AccessFlags.Write);
                b.SetRenderAttachmentDepth(res.activeDepthTexture, AccessFlags.ReadWrite);
                b.AllowPassCulling(false);
                b.SetRenderFunc(static (Data x, RasterGraphContext c) =>
                {
                    c.cmd.DrawRendererList(x.mark);
                    c.cmd.DrawRendererList(x.fill);
                });
            }
        }
    }
}
