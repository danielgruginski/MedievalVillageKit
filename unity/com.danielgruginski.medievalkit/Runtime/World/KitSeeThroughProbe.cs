using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MedievalKit
{
    /// <summary>
    /// The see-through's hidden check (2026-10-13, MedievalSetting: the hole was open all the time, so a roof's edge or a
    /// buttress beside a walker nobody hid lost a bite, and bush tops speckled round it): does anything the hole would
    /// open stand over the walker's upper body? A game camera owns one and calls <see cref="Look"/> each frame after it
    /// has set the see-through's globals; it reads <see cref="Cover"/> and opens or shuts the hole by it.
    /// How: a small camera of its own (32 x 40 px, at the game camera, framing the walker from its waist to over its
    /// head) renders with _KitSeeThroughProbe = 1, so the kit's shader draws only what the hole would open (in front of
    /// the walker, above the foot kept, of a piece in its way -- the cone left out) in flat magenta; everything else draws
    /// as usual, and what stands behind the walker is not drawn. An asynchronous read-back counts the magenta pixels in
    /// an ellipse over the body: <see cref="Cover"/> (0..1), a frame or two late. At most <see cref="Rate"/> renders a
    /// second, none while a read is pending; no shadows, no post-processing, no grass (<see cref="IsProbe"/>). About 0.7
    /// ms of CPU a render in the editor (MedievalSetting's hamlet, 2026-10-13), so ~0.2 ms a frame at 15 a second.
    /// </summary>
    public sealed class KitSeeThroughProbe : IDisposable
    {
        public const int Width = 32, Height = 40;
        /// <summary>the frame's width at the walker (m); its height follows the image's shape</summary>
        public const float FrameWidth = 0.8f;

        static readonly int ProbeId = Shader.PropertyToID("_KitSeeThroughProbe");
        static readonly HashSet<Camera> probes = new HashSet<Camera>();

        /// <summary>a hidden check's camera (the kit's per-camera work skips it: grass, the AgX grade)</summary>
        public static bool IsProbe(Camera c) => c != null && probes.Contains(c);

        readonly Camera view;
        readonly Camera cam;
        readonly RenderTexture rt;
        readonly Action<AsyncGPUReadbackRequest> done;
        bool pending;
        int gen, asked;                                                // reads asked before Forget are dropped

        /// <summary>the share of the walker's upper body behind what the hole would open, at the last read (0..1)</summary>
        public float Cover { get; private set; }
        /// <summary>reads so far (0: no answer yet)</summary>
        public int Reads { get; private set; }
        /// <summary>the probe's image, for a look while tuning</summary>
        public RenderTexture Image => rt;
        /// <summary>renders a second at most</summary>
        public float Rate = 15f;
        float last = -1f;

        public KitSeeThroughProbe(Camera view)
        {
            this.view = view;
            var go = new GameObject("KitSeeThroughProbe") { hideFlags = HideFlags.DontSave };
            go.transform.SetParent(view.transform, false);
            cam = go.AddComponent<Camera>();
            cam.enabled = false;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.clear;
            cam.allowHDR = false;
            cam.allowMSAA = false;
            cam.useOcclusionCulling = false;
            cam.nearClipPlane = 0.3f;
            var d = go.AddComponent<UniversalAdditionalCameraData>();
            d.renderPostProcessing = false;
            d.renderShadows = false;
            d.antialiasing = AntialiasingMode.None;
            d.requiresColorOption = CameraOverrideOption.Off;
            d.requiresDepthOption = CameraOverrideOption.Off;
            rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear) { name = "KitSeeThroughProbe" };
            cam.targetTexture = rt;
            cam.aspect = (float)Width / Height;
            probes.Add(cam);
            done = Done;
        }

        /// <summary>render the walker's view (feet: its feet, world; chest: its chest's height over them) unless a read is
        /// still pending; the see-through's globals must be set for this frame</summary>
        public void Look(Vector3 feet, float chest)
        {
            if (pending || cam == null || rt == null) return;
            if (last >= 0f && Time.unscaledTime - last < 1f / Mathf.Max(1f, Rate)) return;
            last = Time.unscaledTime;
            var from = view.transform.position;
            var at = feet + Vector3.up * (1.4f * chest);              // between its waist and its head
            var dv = at - from;
            float dist = dv.magnitude;
            if (dist < 1f) return;
            float frameH = FrameWidth * Height / Width;
            cam.transform.SetPositionAndRotation(from, Quaternion.LookRotation(dv / dist, Vector3.up));
            cam.fieldOfView = 2f * Mathf.Atan(0.5f * frameH / dist) * Mathf.Rad2Deg;
            cam.aspect = (float)Width / Height;
            cam.farClipPlane = dist + 3f;
            cam.cullingMask = view.cullingMask;
            Shader.SetGlobalFloat(ProbeId, 1f);
            try { cam.Render(); }
            finally { Shader.SetGlobalFloat(ProbeId, 0f); }
            pending = true;
            asked = gen;
            AsyncGPUReadback.Request(rt, 0, TextureFormat.RGBA32, done);
        }

        /// <summary>drop the answer (and a read still on its way): the walker was moved (a level's door, a teleport)</summary>
        public void Forget()
        {
            gen++;
            Cover = 0f;
            Reads = 0;
            last = -1f;
        }

        void Done(AsyncGPUReadbackRequest r)
        {
            pending = false;
            if (r.hasError || cam == null || asked != gen) return;
            var px = r.GetData<Color32>();
            int hit = 0, all = 0;
            for (int y = 0; y < Height; y++)
            {
                float v = (y + 0.5f) / Height * 2f - 1f;
                for (int x = 0; x < Width; x++)
                {
                    float u = (x + 0.5f) / Width * 2f - 1f;
                    if (u * u / 0.5f + v * v > 1f) continue;           // the body: an ellipse 0.57 m wide, the frame's height
                    all++;
                    var c = px[y * Width + x];
                    if (c.r > 240 && c.g < 16 && c.b > 240) hit++;
                }
            }
            Cover = all > 0 ? (float)hit / all : 0f;
            Reads++;
        }

        public void Dispose()
        {
            probes.Remove(cam);
            if (cam != null) UnityEngine.Object.Destroy(cam.gameObject);
            if (rt != null) { rt.Release(); UnityEngine.Object.Destroy(rt); }
        }
    }
}
