using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

namespace MedievalKit.Editor
{
    /// <summary>Renders a level's main camera to a PNG, for side-by-side checks against the Blender renders.</summary>
    public static class KitCapture
    {
        public static string Capture(string levelName, string outPng, int width = 960, int height = 540)
        {
            string path = $"{KitPaths.Levels}/{levelName}.unity";
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            Camera cam = null;
            foreach (var root in scene.GetRootGameObjects())
                foreach (var c in root.GetComponentsInChildren<Camera>(false))
                    if (c.CompareTag("MainCamera")) cam = c;
            if (cam == null) return "no MainCamera in " + path;
            return Render(cam, outPng, width, height);
        }

        /// <summary>Every camera of a level (inactive ones too) -> outDir/unity_{level}_{camera}.png.</summary>
        public static int CaptureAll(string levelName, string outDir, int width = 960, int height = 540)
        {
            var scene = EditorSceneManager.OpenScene($"{KitPaths.Levels}/{levelName}.unity", OpenSceneMode.Single);
            var cams = new System.Collections.Generic.List<Camera>();
            foreach (var root in scene.GetRootGameObjects())
                cams.AddRange(root.GetComponentsInChildren<Camera>(true));
            foreach (var c in cams) c.gameObject.SetActive(false);
            foreach (var c in cams)
            {
                c.gameObject.SetActive(true);
                Render(c, Path.Combine(outDir, $"unity_{levelName}_{c.name}.png"), width, height);
                c.gameObject.SetActive(false);
            }
            return cams.Count;
        }

        /// <summary>Renders any camera to a PNG (shaders compiled synchronously).</summary>
        public static string RenderCamera(Camera cam, string outPng, int width = 960, int height = 540) => Render(cam, outPng, width, height);

        static string Render(Camera cam, string outPng, int width, int height)
        {
            // the editor compiles shader variants asynchronously and skips objects whose variant isn't ready
            // (a first capture showed only their shadows): compile synchronously while capturing
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            try { return RenderSync(cam, outPng, width, height); }
            finally { ShaderUtil.allowAsyncCompilation = async; }
        }

        static string RenderSync(Camera cam, string outPng, int width, int height)
        {
            var rt = new RenderTexture(width, height, 24, GraphicsFormat.R8G8B8A8_SRGB) { antiAliasing = 4 };
            rt.Create();
            var req = new RenderPipeline.StandardRequest { destination = rt };
            if (RenderPipeline.SupportsRenderRequest(cam, req))
                RenderPipeline.SubmitRenderRequest(cam, req);
            else
            {
                cam.targetTexture = rt; cam.Render(); cam.targetTexture = null;
            }
            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            Directory.CreateDirectory(Path.GetDirectoryName(outPng));
            File.WriteAllBytes(outPng, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            rt.Release();
            return outPng;
        }
    }
}
