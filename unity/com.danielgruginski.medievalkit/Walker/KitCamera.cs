using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering.Universal;

namespace MedievalKit
{
    /// <summary>
    /// The kit's play camera and the see-through's driver. The kit's view (looking north, 50 degrees down), never turned --
    /// the art is made to be seen from this side. Follows <see cref="target"/> smoothly, cuts with it between levels
    /// (KitTravel.Arrived: no glide across a door), the mouse wheel zooms between <see cref="near"/> and <see cref="far"/>.
    /// The levels' own cameras and listeners are switched off as they come in; the listener ("Ears") stands at the target.
    /// The sun's shadows are drawn only as far as the view reaches. Optionally it stops short of a level's border
    /// (<see cref="keepInBorder"/>: <see cref="KitWalkWindow"/> over the level's <see cref="KitMapFrame"/>).
    /// <para>The see-through: each frame it sets the shader's globals (_KitSeeThrough: the hole round the target's chest;
    /// _KitSeeThroughArgs: its feet, the height kept, the near and body margins) and, with
    /// <see cref="seeThroughWhenHidden"/>, opens the hole only while the kit's pieces really hide the target
    /// (<see cref="KitSeeThroughProbe"/>), with hysteresis so it does not flicker. Without this camera (or another driver
    /// setting the globals) the kit's shader draws everything whole.</para>
    /// <para>A game's own rules come in through the static hooks (<see cref="MapFrameOf"/>, <see cref="Keeps"/>,
    /// <see cref="Entered"/>, and <see cref="KitPointer.Blocked"/>), or a subclass (MedievalSetting: GameCamera).
    /// From the Guild RPG's GameCamera (FULL_PORT_PLAN phase 3b).</para>
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public class KitCamera : MonoBehaviour
    {
        public Transform target;
        public float pitch = 50f;
        public float distance = 22f;
        public float near = 13f, far = 32f;
        public float fov = 30f;
        [Tooltip("Follow lag (seconds).")]
        public float smooth = 0.12f;
        [Header("See-through (the kit's shader): what stands between the camera and the target fades")]
        [Tooltip("The hole's radius round the target (m); 0 turns it off.")]
        public float seeThroughRadius = 2.4f;
        [Tooltip("Kept below this height over the target's feet (the ground, low and cut walls).")]
        public float keepBelow = 1.4f;
        [Tooltip("Only pieces in the target's way fade: those reaching into the wedge from the camera to its body, " +
                 "this far (m) each side of it -- a wall beside it stays whole. Under the navmesh's agent radius " +
                 "(0.3), or a wall the walker walks along fades again. 0: every piece in the hole's cone fades.")]
        public float seeThroughBody = 0.2f;
        [Tooltip("Kept whole this far (m) in front of the target, level (an eave over it, a post beside it). 0.6 opened " +
                 "nothing of a house's back wall the walker stood against (0.3-0.5 m in front).")]
        public float seeThroughNear = 0.25f;
        [Tooltip("Open the hole only while the kit's pieces really hide the target (KitSeeThroughProbe: a small render of " +
                 "its upper body, about every other frame). Off: the hole is always open.")]
        public bool seeThroughWhenHidden = true;
        [Tooltip("The share of the target's upper body that must be hidden to open the hole, and the share under which it shuts.")]
        public float seeThroughCoverOpen = 0.12f, seeThroughCoverShut = 0.04f;
        [Tooltip("How long the hole takes to open and to shut (s), and how long it stays open once the target is seen again.")]
        public float seeThroughOpenTime = 0.2f, seeThroughShutTime = 0.35f, seeThroughHold = 0.3f;
        [Header("The border (levels with a map frame: MapFrameOf)")]
        [Tooltip("Stop short of the level's border (off: the camera always centres the target).")]
        public bool keepInBorder = false;
        [Tooltip("How far past the walkable ground the view may reach (m): the wall, the forest's edge.")]
        public float borderPad = 3f;
        [Tooltip("The part of the screen the target is kept in (viewport: left, bottom, right, top), clear of the HUD.")]
        public Vector4 keepIn = new Vector4(0.15f, 0.22f, 0.85f, 0.82f);
        [Tooltip("How long the border's bounds take to move (s): a road out coming into view swings the view over.")]
        public float borderLag = 0.35f;

        /// <summary>a level's map frame (by KitTravel's level name; null: none, the camera follows freely). For
        /// <see cref="keepInBorder"/>.</summary>
        public static System.Func<string, KitMapFrame> MapFrameOf;
        /// <summary>a camera the take-over leaves on (MedievalSetting: the character maker's preview)</summary>
        public static System.Func<Camera, bool> Keeps;
        /// <summary>the camera took a level over (true: outdoors, a level built as a village with a sky): the game's
        /// ambience</summary>
        public static System.Action<bool> Entered;

        static readonly int SeeId = Shader.PropertyToID("_KitSeeThrough"), SeeArgsId = Shader.PropertyToID("_KitSeeThroughArgs");

        protected Camera cam;
        Vector3 vel;
        AudioListener ears;
        readonly KitWalkWindow border = new KitWalkWindow();
        KitSeeThroughProbe probe;
        float seeOpen, seeHiddenAt = -99f;

        /// <summary>the hidden check's last answer: the share of the target's upper body hidden (-1: no check)</summary>
        public float SeeThroughCover => probe != null ? probe.Cover : -1f;
        /// <summary>how far the hole is open (0 shut .. 1 open)</summary>
        public float SeeThroughOpen => seeOpen;

        protected virtual void Awake()
        {
            cam = GetComponent<Camera>();
            cam.fieldOfView = fov; cam.nearClipPlane = 0.3f; cam.farClipPlane = 400f;
            gameObject.tag = "MainCamera";
            // the ears stand at the target, facing as the camera does: from the camera, 22 m up, every sound would be
            // about as far as every other
            if (TryGetComponent<AudioListener>(out var own)) { own.enabled = false; Destroy(own); }
            ears = new GameObject("Ears").AddComponent<AudioListener>();
            ears.transform.SetParent(transform, false);
            DontDestroyOnLoad(gameObject);
            KitTravel.Arrived += OnArrived;
        }

        protected virtual void OnDestroy()
        {
            KitTravel.Arrived -= OnArrived;
            probe?.Dispose();
            probe = null;
        }

        protected virtual void OnDisable()
        {
            Shader.SetGlobalVector(SeeId, Vector4.zero);                       // the editor's views stay whole
            foreach (var kv in shadowRest) if (kv.Key != null) kv.Key.shadowDistance = kv.Value;   // the pipeline asset as it was
            shadowRest.Clear();
        }

        /// <summary>the pipeline assets' own shadow distances, put back when the camera goes</summary>
        readonly System.Collections.Generic.Dictionary<UniversalRenderPipelineAsset, float> shadowRest =
            new System.Collections.Generic.Dictionary<UniversalRenderPipelineAsset, float>();

        /// <summary>the sun's shadows drawn only as far as the view reaches (a road of 3,300 shadow-casting trees: 50 m of
        /// shadow at the default zoom drew hundreds of them outside the picture): the ground point the screen's top
        /// corners see, from the camera, plus a margin for a shadow cast in from just outside; about 39 m at the default
        /// zoom, 53 m zoomed out</summary>
        void FitShadows()
        {
            if (!(UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)) return;
            if (!shadowRest.ContainsKey(urp)) shadowRest[urp] = urp.shadowDistance;
            float half = cam.fieldOfView * 0.5f;
            float down = (pitch - half) * Mathf.Deg2Rad;                      // the top edge's ray below the horizon
            float reach = 400f;
            if (down > 0.05f)
            {
                float h = distance * Mathf.Sin(pitch * Mathf.Deg2Rad) + 1f;
                float side = Mathf.Atan(Mathf.Tan(half * Mathf.Deg2Rad) * cam.aspect);
                reach = h / Mathf.Sin(down) / Mathf.Cos(side) + 4f;
            }
            float want = Mathf.Clamp(reach, 25f, shadowRest[urp] + 5f);
            if (Mathf.Abs(urp.shadowDistance - want) > 0.5f) urp.shadowDistance = want;
        }

        protected virtual void Start() { TakeOver(); Snap(); }

        void OnArrived(string level, KitSpawn spawn) { TakeOver(); Snap(); }

        /// <summary>switch off the level's cameras (and listeners) and keep their post-processing choice; the backdrop is
        /// the sky outdoors (a level built as a village) and black anywhere else (rooms, cellars, caves: every kit level
        /// carries the default sky, which would show through gaps and the see-through hole)</summary>
        protected virtual void TakeOver()
        {
            bool outdoors = FindAnyObjectByType<KitVillage>() != null && RenderSettings.skybox != null;
            foreach (var c in FindObjectsByType<Camera>(FindObjectsSortMode.None))
            {
                if (c == cam || !c.enabled || (Keeps != null && Keeps(c))) continue;
                if (c.TryGetComponent<UniversalAdditionalCameraData>(out var d))
                    cam.GetUniversalAdditionalCameraData().renderPostProcessing = d.renderPostProcessing;
                c.enabled = false;
            }
            cam.enabled = true;                                         // (a level's own helper may have switched it off)
            if (ears != null) ears.enabled = true;
            Entered?.Invoke(outdoors);
            cam.clearFlags = outdoors ? CameraClearFlags.Skybox : CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            foreach (var l in FindObjectsByType<AudioListener>(FindObjectsSortMode.None))
                if (l != ears) l.enabled = false;
        }

        Quaternion Rot => Quaternion.Euler(pitch, 180f, 0f);       // the kit's north is Unity -Z
        /// <summary>where the camera wants to be, looking at its focus (dt: the border's easing step; 0: at once)</summary>
        Vector3 Want(float dt) => Focus(dt) + Vector3.up - Rot * Vector3.forward * distance;

        /// <summary>jump to the target at once (after a cut: a level change, a teleport); the hidden check asks again</summary>
        public void Snap()
        {
            if (target == null) return;
            border.Reset();
            transform.SetPositionAndRotation(Want(0f), Rot);
            vel = Vector3.zero;
            seeOpen = 0f; seeHiddenAt = -99f;
            probe?.Forget();
        }

        /// <summary>what the camera looks at: the target (with <see cref="keepInBorder"/>: held back from the level's border
        /// where it has a map frame)</summary>
        Vector3 Focus(float dt)
        {
            var p = target.position;
            if (!keepInBorder || MapFrameOf == null) return p;
            var d = KitTravel.Travelling ? null : MapFrameOf(KitTravel.CurrentLevel);
            if (d == null || d.fogW <= 0) return p;
            var uv = d.ToMap(p);
            if (uv.x < -0.3f || uv.x > 1.3f || uv.y < -0.3f || uv.y > 1.3f) return p;   // far off its picture: not this level's
                                                                                       // ground (a road's last stretch out may run past it)
            Seen(d, out var view, out var keep);
            var pad = new Vector2(borderPad / Mathf.Max(1f, d.right.magnitude), borderPad / Mathf.Max(1f, d.down.magnitude));
            var f = border.Fit(d, uv, view, keep, pad, dt <= 0f ? 1f : 1f - Mathf.Exp(-dt / Mathf.Max(0.01f, borderLag)));
            var w = d.FromMap(f);
            return new Vector3(w.x, p.y, w.y);
        }

        /// <summary>the ground the camera sees round its focus at this zoom, on the map frame (offsets round the focus):
        /// the whole view (its bounds) and the part the target is kept in (inside it)</summary>
        void Seen(KitMapFrame d, out Rect view, out Rect keep)
        {
            var o = Vector3.up - Rot * Vector3.forward * distance;            // the camera, from the focus on the ground
            float ty = Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad), tx = ty * cam.aspect;
            Vector2 Ground(float x, float y)                                  // a viewport point -> where it meets the ground
            {
                var dir = Rot * new Vector3((2f * x - 1f) * tx, (2f * y - 1f) * ty, 1f);
                var g = o + dir * (dir.y < -1e-3f ? -o.y / dir.y : 200f);      // (over the horizon: far off)
                return d.MapDelta(new Vector2(g.x, g.z));
            }
            view = Box(Ground(0f, 0f), Ground(1f, 0f), Ground(0f, 1f), Ground(1f, 1f), false);
            keep = Box(Ground(keepIn.x, keepIn.y), Ground(keepIn.z, keepIn.y), Ground(keepIn.x, keepIn.w), Ground(keepIn.z, keepIn.w), true);
        }

        /// <summary>four corners' bounds; inner: the box inside them (the screen's trapezoid on the ground is narrower at
        /// the bottom: the second smallest and second largest of each)</summary>
        static Rect Box(Vector2 a, Vector2 b, Vector2 c, Vector2 e, bool inner)
        {
            float[] us = { a.x, b.x, c.x, e.x }, vs = { a.y, b.y, c.y, e.y };
            System.Array.Sort(us); System.Array.Sort(vs);
            int lo = inner ? 1 : 0, hi = inner ? 2 : 3;
            return Rect.MinMaxRect(us[lo], vs[lo], us[hi], vs[hi]);
        }

        protected virtual void LateUpdate()
        {
            if (target == null) return;
            var m = Mouse.current;
            if (m != null && !KitPointer.BlockedAt(m.position.ReadValue()))
            {
                float s = m.scroll.ReadValue().y;
                if (Mathf.Abs(s) > 0.01f) distance = Mathf.Clamp(distance - Mathf.Sign(s) * 1.5f, near, far);
            }
            float dt = Mathf.Min(Time.unscaledDeltaTime, 0.1f);                                 // it follows while paused
            transform.position = Vector3.SmoothDamp(transform.position, Want(dt), ref vel, smooth, Mathf.Infinity, dt);
            transform.rotation = Rot;
            var p = target.position;
            if (ears != null) ears.transform.SetPositionAndRotation(p + Vector3.up * 1.6f, Quaternion.Euler(0f, 180f, 0f));
            SeeThrough(p, dt);
            FitShadows();
        }

        /// <summary>the kit's see-through round the target (feet p): the hole opens while the kit's pieces hide the target
        /// (a roof's edge, a buttress, bush tops were cut round a walker nobody hid) and shuts when it is seen again,
        /// growing from and shrinking to its middle</summary>
        void SeeThrough(Vector3 p, float dt)
        {
            Vector4 Hole() => new Vector4(p.x, p.y + 1f, p.z, seeThroughRadius * Mathf.SmoothStep(0f, 1f, seeOpen));
            Shader.SetGlobalVector(SeeId, Hole());
            Shader.SetGlobalVector(SeeArgsId, new Vector4(p.y, keepBelow, seeThroughNear, seeThroughBody));
            float want = 1f;
            if (seeThroughWhenHidden && seeThroughRadius > 0f)
            {
                if (probe == null) probe = new KitSeeThroughProbe(cam);
                probe.Look(p, 1f);                                            // (it renders with the globals just set)
                if (probe.Reads > 0 && probe.Cover > (seeOpen > 0f ? seeThroughCoverShut : seeThroughCoverOpen)) seeHiddenAt = Time.unscaledTime;
                want = Time.unscaledTime - seeHiddenAt < seeThroughHold ? 1f : 0f;
            }
            seeOpen = Mathf.MoveTowards(seeOpen, want, dt / Mathf.Max(0.01f, want > seeOpen ? seeThroughOpenTime : seeThroughShutTime));
            Shader.SetGlobalVector(SeeId, Hole());
        }
    }
}
