#if UNITY_EDITOR || DEVELOPMENT_BUILD
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// The z-fight watch (2026-10-13, the user: "a tool that automatically detected this happening? I would walk around with
    /// the tool on, playing, and it would keep track of the places where Zfighting is happening, logging them so you can
    /// check later"). F8 in play turns it on and off (editor and development builds only).
    /// <para>Once a <see cref="interval"/> it draws the game camera's view twice off screen, <see cref="height"/> pixels high
    /// and as wide as the game view's shape (Resources/ZFightProbe.shader): the nearest surface per pixel (which renderer and submesh, which
    /// triangle, its view depth, its flat normal, its world position), then the nearest other surface behind it. Where the
    /// two lie in one plane (normals within ~6 degrees) less than <see cref="near"/> apart, the pixel can fight; under
    /// <see cref="fight"/> it does, and the fight shows where the two are painted differently (the probe also keeps each
    /// surface's painted brightness: <see cref="lookDiff"/> apart). Such pixels are grouped by place (4 m of ground) and by
    /// the pair of renderers into spots, kept for the session: level, place, both renderers' paths and materials, the
    /// smallest gap, how many rounds and pixels saw it and on how many the fight shows -- "fight" (it shows), "same look"
    /// (one plane, painted alike: it fights unseen), "near" (apart enough for the game's depth buffer) -- and a cropped
    /// screenshot of a fight while it is in view, ringed. Written to Logs/ZFightWatch/&lt;time&gt;/spots.csv (+ spot_*.png)
    /// every few seconds and when it stops.</para>
    /// <para>What counts is what can be seen: the probe keeps each material's culling and alpha cut-out and the kit's
    /// see-through hole, skips transparent materials, shadow-only and unseen renderers (isVisible: off-screen and inactive
    /// LOD levels). Characters (skinned meshes) are left out unless <see cref="characters"/>.</para>
    /// </summary>
    public class ZFightWatch : MonoBehaviour
    {
        public static ZFightWatch Instance { get; private set; }

        [Tooltip("Watching (F8).")] public bool active;
        [Tooltip("A probe this often (s).")] public float interval = 1f;
        [Tooltip("The probe's height in pixels (its width follows the game view's shape).")] public int height = 540;
        [Tooltip("Two surfaces closer than this (m) fight.")] public float fight = 0.0002f;
        [Tooltip("Closer than this (m): logged as near (may fight on some GPUs).")] public float near = 0.001f;
        [Tooltip("Pixels a spot needs in one probe.")] public int minPixels = 4;
        [Tooltip("Painted brightness (0-255) two surfaces need apart for their fight to show.")] public int lookDiff = 10;
        public float maxDistance = 90f;
        [Tooltip("Skinned meshes too (characters' clothes over their bodies).")] public bool characters;
        [Tooltip("Save the probe's picture each round (tuning the watch).")] public bool debugImages;

        static readonly int DrawId = Shader.PropertyToID("_ZDrawId"), FirstId = Shader.PropertyToID("_ZFirst"),
            CamPosId = Shader.PropertyToID("_WorldSpaceCameraPos"), CullId = Shader.PropertyToID("_Cull"),
            CutoffId = Shader.PropertyToID("_Cutoff"), BaseMapId = Shader.PropertyToID("_BaseMap"), MainTexId = Shader.PropertyToID("_MainTex"),
            BaseColorId = Shader.PropertyToID("_BaseColor"), VertexColorId = Shader.PropertyToID("_ZVertexColor");

        class Spot
        {
            public int id;
            public string level, a, matA, b, matB, shot;
            public Vector3 sum;
            public int n, rounds, pixels, showing;
            public float minGap = float.MaxValue, first, last;
            public Vector3 Pos => n > 0 ? sum / n : Vector3.zero;
        }

        Shader shader;
        RenderTexture idA, idB;
        int pw, ph;                                            // the probe's size (the read-back's)
        Matrix4x4 camToWorld;                                  // the camera at the probe (it moves before the read-back)
        float tanHalf, aspect, orthoSize;
        bool ortho;                                            // an orthographic camera (the kit's catalogs)
        CommandBuffer cmd;
        readonly Dictionary<Material, Material> probeMats = new Dictionary<Material, Material>();
        readonly List<Renderer> renderers = new List<Renderer>();
        readonly List<(Renderer r, int sub)> draws = new List<(Renderer, int)>();
        (Renderer r, int sub)[] snapshot;
        Vector4[] bufA, bufB;
        int got;
        bool busy;
        float next, nextRefresh, lastWrite, lastShot;
        bool dirty;
        string dir;
        int shots;
        readonly Dictionary<(string, Vector3Int, int, int, int, int), Spot> spots = new Dictionary<(string, Vector3Int, int, int, int, int), Spot>();
        readonly List<Spot> inView = new List<Spot>();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Boot()
        {
            if (Instance != null) return;
            var go = new GameObject("ZFightWatch");
            DontDestroyOnLoad(go);
            go.AddComponent<ZFightWatch>();
        }

        /// <summary>on / off (the editor's Tools menu, F8 in play)</summary>
        public static void Toggle() { if (Instance != null) Instance.SetActive(!Instance.active); }

        void Awake() { Instance = this; SceneManager.sceneLoaded += OnLoaded; }

        void OnDestroy()
        {
            SceneManager.sceneLoaded -= OnLoaded;
            Write();
            Release();
            if (Instance == this) Instance = null;
        }

        void OnApplicationQuit() => Write();

        void OnLoaded(Scene s, LoadSceneMode m) => nextRefresh = 0f;

        void SetActive(bool on)
        {
            if (on == active) return;
            active = on;
            if (on)
            {
                shader = Resources.Load<Shader>("ZFightProbe");
                if (shader == null || !shader.isSupported) { Debug.LogWarning("[ZFightWatch] no ZFightProbe shader"); active = false; return; }
                if (dir == null)
                {
                    dir = System.IO.Path.Combine(Directory.GetParent(Application.dataPath).FullName, "Logs", "ZFightWatch", System.DateTime.Now.ToString("yyyyMMdd_HHmmss"));
                    Directory.CreateDirectory(dir);
                }
                nextRefresh = 0f;
                Debug.Log($"[ZFightWatch] on: {dir}");
            }
            else { Write(); inView.Clear(); Debug.Log($"[ZFightWatch] off: {spots.Count} spots in {dir}"); }
        }

        void Release()
        {
            foreach (var rt in new[] { idA, idB }) if (rt != null) { rt.Release(); Destroy(rt); }
            idA = idB = null;
            cmd?.Release(); cmd = null;
            foreach (var m in probeMats.Values) if (m != null) Destroy(m);
            probeMats.Clear();
        }

        void Update()
        {
            var kb = Keyboard.current;
            if (kb != null && kb.f8Key.wasPressedThisFrame) SetActive(!active);
            if (!active) return;
            if (Time.unscaledTime >= nextRefresh) Refresh();
            if (dirty && Time.unscaledTime - lastWrite > 5f) Write();
            if (busy || Time.unscaledTime < next) return;
            var cam = Camera.main;
            if (cam == null) return;
            next = Time.unscaledTime + interval;
            Probe(cam);
        }

        void LateUpdate()
        {
            // a fight in view not yet shot (the one showing most), at most one each 2 s
            if (!active || Time.unscaledTime - lastShot < 2f || shots >= 200) return;
            var cam = Camera.main;
            if (cam == null) return;
            Spot pick = null;
            foreach (var s in inView)
                if (s.shot == null && s.minGap < fight && s.showing >= minPixels && (pick == null || s.showing > pick.showing)) pick = s;
            if (pick == null) return;
            lastShot = Time.unscaledTime;
            Shoot(cam, pick);
        }

        void Refresh()
        {
            nextRefresh = Time.unscaledTime + 10f;
            renderers.Clear();
            renderers.AddRange(FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None));
            if (characters) renderers.AddRange(FindObjectsByType<SkinnedMeshRenderer>(FindObjectsSortMode.None));
        }

        Material ProbeMaterial(Material src)
        {
            if (probeMats.TryGetValue(src, out var m) && m != null) return m;
            m = new Material(shader) { name = "ZFightProbe_" + src.name, hideFlags = HideFlags.DontSave };
            m.SetFloat(CullId, src.HasProperty(CullId) ? src.GetFloat(CullId) : 2f);
            // the painted colour (the kit's: texture x tint x vertex colour) and the cut-out
            int tex = src.HasProperty(BaseMapId) ? BaseMapId : src.HasProperty(MainTexId) ? MainTexId : -1;
            if (tex != -1 && src.GetTexture(tex) != null)
            {
                m.SetTexture(BaseMapId, src.GetTexture(tex));
                m.SetTextureScale(BaseMapId, src.GetTextureScale(tex));
                m.SetTextureOffset(BaseMapId, src.GetTextureOffset(tex));
            }
            if (src.HasProperty(BaseColorId)) m.SetColor(BaseColorId, src.GetColor(BaseColorId));
            m.SetFloat(VertexColorId, src.HasProperty("_UseVertexColor") && src.GetFloat("_UseVertexColor") > 0.5f ? 1f : 0f);
            bool cut = src.IsKeywordEnabled("_ALPHATEST_ON") || (src.HasProperty("_AlphaClip") && src.GetFloat("_AlphaClip") > 0.5f);
            if (cut)
            {
                m.SetFloat(CutoffId, src.HasProperty(CutoffId) ? src.GetFloat(CutoffId) : 0.5f);
                m.EnableKeyword("_ALPHATEST_ON");
            }
            probeMats[src] = m;
            return m;
        }

        static RenderTexture Target(int w, int h, int depth) =>
            new RenderTexture(w, h, depth, RenderTextureFormat.ARGBFloat, RenderTextureReadWrite.Linear) { name = "ZFightWatch", filterMode = FilterMode.Point };

        void Probe(Camera cam)
        {
            int w = Mathf.Max(64, Mathf.RoundToInt(height * cam.aspect)), h = Mathf.Max(64, height);
            if (idA == null || idA.width != w || idA.height != h)
            {
                Release();
                // one colour target a pass, each with its own depth; places come from each pixel's view depth and the camera at
                // the probe
                idA = Target(w, h, 32); idB = Target(w, h, 32);
                idA.Create(); idB.Create();
            }
            // what is drawn: seen renderers within reach, opaque and cut-out submeshes
            draws.Clear();
            var planes = GeometryUtility.CalculateFrustumPlanes(cam);
            var eye = cam.transform.position;
            float reach2 = maxDistance * maxDistance;
            foreach (var r in renderers)
            {
                if (r == null || !r.enabled || !r.gameObject.activeInHierarchy || !r.isVisible || r.shadowCastingMode == ShadowCastingMode.ShadowsOnly) continue;
                var b = r.bounds;
                if (b.SqrDistance(eye) > reach2 || !GeometryUtility.TestPlanesAABB(planes, b)) continue;   // (nearest point: the ground's centre is far)
                Mesh mesh = r is SkinnedMeshRenderer sk ? sk.sharedMesh : r.GetComponent<MeshFilter>()?.sharedMesh;
                if (mesh == null) continue;
                var mats = r.sharedMaterials;
                for (int s = 0; s < mesh.subMeshCount && s < mats.Length; s++)
                    if (mats[s] != null && mats[s].renderQueue < 2500) draws.Add((r, s));
            }
            if (draws.Count > 65535) draws.RemoveRange(65535, draws.Count - 65535);   // ids share a float with the brightness
            snapshot = draws.ToArray();
            cmd ??= new CommandBuffer { name = "ZFightWatch" };
            cmd.Clear();
            // the camera's own projection: Unity makes it the GPU's itself (reversed depth, the flip into a texture, the winding);
            // an already converted one (GL.GetGPUProjectionMatrix) was converted twice and the farther surface won
            cmd.SetViewProjectionMatrices(cam.worldToCameraMatrix, cam.projectionMatrix);
            cmd.SetGlobalVector(CamPosId, eye);
            cmd.SetRenderTarget(idA);
            cmd.ClearRenderTarget(true, true, Color.clear);
            for (int i = 0; i < snapshot.Length; i++)
            {
                var (r, s) = snapshot[i];
                cmd.SetGlobalFloat(DrawId, i + 1);
                cmd.DrawRenderer(r, ProbeMaterial(r.sharedMaterials[s]), s, 0);
            }
            cmd.SetGlobalTexture(FirstId, idA);
            cmd.SetRenderTarget(idB);
            cmd.ClearRenderTarget(true, true, Color.clear);
            for (int i = 0; i < snapshot.Length; i++)
            {
                var (r, s) = snapshot[i];
                cmd.SetGlobalFloat(DrawId, i + 1);
                cmd.DrawRenderer(r, ProbeMaterial(r.sharedMaterials[s]), s, 1);
            }
            Graphics.ExecuteCommandBuffer(cmd);
            busy = true;
            got = 0;
            camToWorld = cam.cameraToWorldMatrix;
            tanHalf = Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad);
            aspect = cam.aspect;
            ortho = cam.orthographic;
            orthoSize = cam.orthographicSize;
            pw = w; ph = h;
            int n = pw * ph;
            if (bufA == null || bufA.Length != n) { bufA = new Vector4[n]; bufB = new Vector4[n]; }
            var level = SceneManager.GetActiveScene().name;
            AsyncGPUReadback.Request(idA, 0, r => Got(r, bufA, level));
            AsyncGPUReadback.Request(idB, 0, r => Got(r, bufB, level));
        }

        void Got(AsyncGPUReadbackRequest r, Vector4[] into, string level)
        {
            if (!r.hasError) r.GetData<Vector4>().CopyTo(into);
            if (++got < 2) return;
            busy = false;
            if (active) Compare(level);
        }

        static Vector3 Unpack(float f)
        {
            uint q = (uint)f;
            float ex = (q / 4096) / 4095f * 2f - 1f, ey = (q % 4096) / 4095f * 2f - 1f;
            var v = new Vector3(ex, ey, 1f - Mathf.Abs(ex) - Mathf.Abs(ey));
            if (v.z < 0f)
            {
                float x = v.x, y = v.y;
                v.x = (1f - Mathf.Abs(y)) * (x >= 0f ? 1f : -1f);
                v.y = (1f - Mathf.Abs(x)) * (y >= 0f ? 1f : -1f);
            }
            return v.normalized;
        }

        void Compare(string level)
        {
            var round = new Dictionary<(Vector3Int, int, int, int, int), (int count, int showing, float gap, Vector3 sum)>();
            int n = pw * ph;
            byte[] hit = debugImages ? new byte[n] : null;
            for (int p = 0; p < n; p++)
            {
                var a = bufA[p];
                if (a.z <= 0f) continue;
                var b = bufB[p];
                if (b.z <= 0f) continue;
                float gap = Mathf.Abs(b.z - a.z);
                if (gap > near) continue;
                if (Mathf.Abs(Vector3.Dot(Unpack(a.w), Unpack(b.w))) < 0.995f) continue;    // crossing, not lying in one plane
                int pa = (int)a.x, pb = (int)b.x;
                int ia = (pa & 0xFFFF) - 1, ib = (pb & 0xFFFF) - 1;
                bool shows = Mathf.Abs((pa >> 16) - (pb >> 16)) >= lookDiff;       // painted differently: the fight shows
                if (ia < 0 || ib < 0 || ia >= snapshot.Length || ib >= snapshot.Length) continue;
                var (ra, sa) = snapshot[ia];
                var (rb, sb) = snapshot[ib];
                if (ra == null || rb == null) continue;
                int ka = ra.GetInstanceID(), kb = rb.GetInstanceID();
                if (ka > kb || (ka == kb && sa > sb)) { (ka, kb) = (kb, ka); (sa, sb) = (sb, sa); }
                // the place: the pixel's ray from the camera at the probe, out to its view depth (row 0 is the bottom); an
                // orthographic camera's rays are parallel, half its size high
                float ndcX = ((p % pw) + 0.5f) / pw * 2f - 1f, ndcY = ((p / pw) + 0.5f) / ph * 2f - 1f;
                Vector3 w = camToWorld.MultiplyPoint3x4(ortho
                    ? new Vector3(ndcX * orthoSize * aspect, ndcY * orthoSize, -a.z)
                    : new Vector3(ndcX * tanHalf * aspect * a.z, ndcY * tanHalf * a.z, -a.z));
                var c4 = Vector3Int.FloorToInt(w / 4f); c4.y = 0;                 // one spot per pair and 4 m of ground
                var key = (c4, ka, sa, kb, sb);
                round.TryGetValue(key, out var e);
                round[key] = (e.count + 1, e.showing + (shows ? 1 : 0), e.count == 0 ? gap : Mathf.Min(e.gap, gap), e.sum + w);
                if (hit != null) hit[p] = (byte)(shows ? 2 : 1);
            }
            inView.Clear();
            var byId = new Dictionary<int, (Renderer, int)>();
            foreach (var d in snapshot) if (d.r != null) byId[d.r.GetInstanceID()] = d;
            foreach (var kv in round)
            {
                if (kv.Value.count < minPixels) continue;
                var (cell, ka, sa, kb, sb) = kv.Key;
                var key = (level, cell, ka, sa, kb, sb);
                if (!spots.TryGetValue(key, out var spot))
                {
                    if (!byId.TryGetValue(ka, out var da) || !byId.TryGetValue(kb, out var db)) continue;
                    spot = new Spot
                    {
                        id = spots.Count + 1, level = level, first = Time.unscaledTime,
                        a = PathOf(da.Item1), matA = Mat(da.Item1, sa), b = PathOf(db.Item1), matB = Mat(db.Item1, sb),
                    };
                    spots[key] = spot;
                }
                spot.rounds++;
                spot.pixels += kv.Value.count;
                spot.showing += kv.Value.showing;
                spot.minGap = Mathf.Min(spot.minGap, kv.Value.gap);
                spot.sum += kv.Value.sum; spot.n += kv.Value.count;
                spot.last = Time.unscaledTime;
                inView.Add(spot);
                dirty = true;
            }
            if (hit != null)
                try { DebugImage(hit); } catch (System.Exception e) { Debug.LogException(e); debugImages = false; }
        }

        static string PathOf(Renderer r)
        {
            var t = r.transform;
            var s = t.name;
            for (int k = 0; k < 4 && t.parent != null; k++) { t = t.parent; s = t.name + "/" + s; }
            return s;
        }

        static string Mat(Renderer r, int sub)
        {
            var m = r.sharedMaterials;
            return sub < m.Length && m[sub] != null ? m[sub].name : "?";
        }

        /// <summary>the game camera's view (its own shape, 1080 high) cropped round the spot, the spot ringed; false while the
        /// spot is out of view</summary>
        bool Shoot(Camera cam, Spot spot)
        {
            var v = cam.WorldToViewportPoint(spot.Pos);
            if (v.z <= 0f || v.x < 0.02f || v.x > 0.98f || v.y < 0.02f || v.y > 0.98f) return false;
            lastShot = Time.unscaledTime;
            const int H = 1080, cw = 640, ch = 400;
            int W = Mathf.Max(cw, Mathf.RoundToInt(H * cam.aspect));
            var rt = RenderTexture.GetTemporary(W, H, 24, RenderTextureFormat.ARGB32);
            var prev = cam.targetTexture;
            try
            {
                cam.targetTexture = rt;
                cam.Render();
                int cx = Mathf.RoundToInt(v.x * W), cy = Mathf.RoundToInt(v.y * H);
                int x0 = Mathf.Clamp(cx - cw / 2, 0, W - cw), y0 = Mathf.Clamp(cy - ch / 2, 0, H - ch);
                RenderTexture.active = rt;
                var tex = new Texture2D(cw, ch, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(x0, y0, cw, ch), 0, 0);
                RenderTexture.active = null;
                int rx = cx - x0, ry = cy - y0;
                for (int a = 0; a < 360; a++)
                    for (int rr = 22; rr <= 24; rr++)
                    {
                        int x = rx + Mathf.RoundToInt(Mathf.Cos(a * Mathf.Deg2Rad) * rr), y = ry + Mathf.RoundToInt(Mathf.Sin(a * Mathf.Deg2Rad) * rr);
                        if (x >= 0 && y >= 0 && x < cw && y < ch) tex.SetPixel(x, y, Color.magenta);
                    }
                tex.Apply();
                spot.shot = $"spot_{spot.id:000}.png";
                File.WriteAllBytes(System.IO.Path.Combine(dir, spot.shot), tex.EncodeToPNG());
                Destroy(tex);
                shots++;
                dirty = true;
            }
            finally { cam.targetTexture = prev; RenderTexture.active = null; RenderTexture.ReleaseTemporary(rt); }
            return true;
        }

        void DebugImage(byte[] hit)
        {
            // left: the nearest surface per pixel (by draw, darker farther), fights magenta (painted alike: cyan); right: the
            // surface behind it
            var tex = new Texture2D(pw * 2, ph, TextureFormat.RGB24, false);
            var px = new Color32[pw * 2 * ph];
            for (int y = 0; y < ph; y++)
                for (int x = 0; x < pw; x++)
                {
                    int p = y * pw + x;
                    px[y * pw * 2 + x] = hit[p] == 2 ? new Color32(255, 0, 255, 255) : hit[p] == 1 ? new Color32(0, 255, 255, 255) : Shade(bufA[p]);
                    px[y * pw * 2 + pw + x] = Shade(bufB[p]);
                }
            tex.SetPixels32(px);
            tex.Apply();
            File.WriteAllBytes(System.IO.Path.Combine(dir, $"probe_{Time.frameCount}.png"), tex.EncodeToPNG());
            Destroy(tex);
        }

        static Color32 Shade(Vector4 a)
        {
            if (a.z <= 0f) return new Color32(0, 0, 0, 255);
            uint h = ((uint)a.x & 0xFFFF) * 2654435761u;
            float k = Mathf.Clamp01(1.2f - a.z / 60f);
            return new Color32((byte)(((h >> 8) & 255) * k), (byte)(((h >> 16) & 255) * k), (byte)(((h >> 24) & 255) * k), 255);
        }

        void Write()
        {
            if (dir == null || spots.Count == 0) return;
            lastWrite = Time.unscaledTime;
            dirty = false;
            var sb = new StringBuilder("id,level,x,y,z,kind,gap_mm,rounds,pixels,showing,first_s,last_s,renderer_a,material_a,renderer_b,material_b,shot\n");
            var list = new List<Spot>(spots.Values);
            // the fights first, most seen first
            list.Sort((p, q) => Kind(p) != Kind(q) ? Kind(p).CompareTo(Kind(q)) : q.showing != p.showing ? q.showing.CompareTo(p.showing) : q.pixels.CompareTo(p.pixels));
            foreach (var s in list)
            {
                var p = s.Pos;
                sb.Append($"{s.id},{s.level},{p.x:F2},{p.y:F2},{p.z:F2},{KindName[Kind(s)]},{s.minGap * 1000f:F3},{s.rounds},{s.pixels},{s.showing},");
                sb.Append($"{s.first:F0},{s.last:F0},\"{s.a}\",{s.matA},\"{s.b}\",{s.matB},{s.shot}\n");
            }
            try { File.WriteAllText(System.IO.Path.Combine(dir, "spots.csv"), sb.ToString()); }
            catch (IOException) { dirty = true; }    // (open in a spreadsheet: next time)
        }

        static readonly string[] KindName = { "fight", "same look", "near" };

        int Kind(Spot s) => s.minGap >= fight ? 2 : s.showing >= minPixels ? 0 : 1;

        void OnGUI()
        {
            if (!active) return;
            var cam = Camera.main;
            GUI.color = Color.black;
            int fights = 0, seen = 0;
            foreach (var s in spots.Values) if (Kind(s) == 0) fights++;
            foreach (var s in inView) if (Kind(s) == 0) seen++;
            var label = $"Z-fight watch (F8): {fights} fights logged ({spots.Count - fights} unseen or near), {seen} in view";
            GUI.Label(new Rect(11, 11, 700, 22), label);
            GUI.color = Color.magenta;
            GUI.Label(new Rect(10, 10, 700, 22), label);
            if (cam == null) return;
            foreach (var s in inView)
            {
                if (Kind(s) != 0) continue;
                var sp = cam.WorldToScreenPoint(s.Pos);
                if (sp.z <= 0f) continue;
                var c = new Rect(sp.x - 10, Screen.height - sp.y - 10, 20, 20);
                GUI.DrawTexture(new Rect(c.x, c.y, c.width, 2), Texture2D.whiteTexture);
                GUI.DrawTexture(new Rect(c.x, c.yMax - 2, c.width, 2), Texture2D.whiteTexture);
                GUI.DrawTexture(new Rect(c.x, c.y, 2, c.height), Texture2D.whiteTexture);
                GUI.DrawTexture(new Rect(c.xMax - 2, c.y, 2, c.height), Texture2D.whiteTexture);
            }
            GUI.color = Color.white;
        }
    }
}
#endif
