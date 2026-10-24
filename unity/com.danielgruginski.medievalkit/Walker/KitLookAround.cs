using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

namespace MedievalKit
{
    /// <summary>
    /// Looking at a level in play without a walker (Tools > Medieval Kit > Look Around This Level: the catalogs, the
    /// structures showcase, any level): Tab / Shift+Tab steps through the scene's cameras (the views the exporter's checks
    /// render), T tours them all once (<see cref="tourSeconds"/> each), F flies a free camera from the current view (hold
    /// the right mouse button to look, WASD, Q / E down and up, Shift faster, the mouse wheel sets the speed), H hides the
    /// help. The camera in use is the only one on and is tagged MainCamera, so tools that follow Camera.main follow it:
    /// the game's z-fight watch (F8) on, then T, logs the fights of a whole catalog. A catalog (a level named Catalog_*)
    /// starts it by itself on plain Play.
    /// Godot: KitDemoView.
    /// </summary>
    public class KitLookAround : MonoBehaviour
    {
        [Tooltip("Seconds on each camera while touring (T): the z-fight watch probes once a second.")]
        public float tourSeconds = 2.5f;

        /// <summary>the verification catalogs (vkx_build_catalog's levels, Catalog_*) have nothing else to drive their
        /// cameras: Play alone gives Tab / T / F (the menu's Look Around This Level does the same for any level)</summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void LookAroundCatalogs()
        {
            if (FindAnyObjectByType<KitLookAround>() != null) return;
            if (!FindObjectsByType<KitLevel>(FindObjectsSortMode.None)
                    .Any(l => l.levelName != null && l.levelName.StartsWith("Catalog_", System.StringComparison.Ordinal))) return;
            new GameObject("KitLookAround").AddComponent<KitLookAround>();
        }

        Camera[] cams = new Camera[0];
        int tourLeft;
        float tourNext;
        Camera free;
        int index = -1;
        bool flying, help = true;
        float yaw, pitch, speed = 6f;

        void Start()
        {
            cams = FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None)
                .Where(c => c.gameObject.scene.IsValid() && c.GetComponentInParent<KitLookAround>() == null)
                .OrderBy(c => c.name, System.StringComparer.Ordinal).ToArray();
            int on = System.Array.FindIndex(cams, c => c.isActiveAndEnabled && c.CompareTag("MainCamera"));
            Use(on >= 0 ? on : 0);
        }

        /// <summary>every camera once, from the first, <see cref="tourSeconds"/> each (T; scripts: a z-fight sweep)</summary>
        public void Tour()
        {
            if (cams.Length == 0) return;
            Use(0);
            tourLeft = cams.Length - 1;
            tourNext = Time.unscaledTime + tourSeconds;
        }

        public bool Touring => tourLeft > 0;
        public int CameraCount => cams.Length;

        void Use(int i)
        {
            if (cams.Length == 0) return;
            index = (i % cams.Length + cams.Length) % cams.Length;
            for (int k = 0; k < cams.Length; k++)
            {
                cams[k].gameObject.SetActive(k == index);
                cams[k].tag = k == index ? "MainCamera" : "Untagged";
            }
            if (free != null) { free.gameObject.SetActive(false); free.tag = "Untagged"; }
            flying = false;
        }

        void Fly()
        {
            var from = Camera.main != null ? Camera.main : index >= 0 && cams.Length > 0 ? cams[index] : null;
            if (from == null) return;
            if (free == null)
            {
                // a copy of a level camera keeps its render pipeline settings (post-processing, anti-aliasing)
                free = Instantiate(from, transform);
                free.name = "KitLookAround Free Camera";
                free.orthographic = false;
                free.fieldOfView = 50f;
                free.nearClipPlane = 0.05f;
                free.farClipPlane = 2000f;
            }
            free.transform.SetPositionAndRotation(from.transform.position, from.transform.rotation);
            var e = from.transform.eulerAngles;
            pitch = e.x > 180f ? e.x - 360f : e.x;
            yaw = e.y;
            foreach (var c in cams) { c.gameObject.SetActive(false); c.tag = "Untagged"; }
            free.gameObject.SetActive(true);
            free.tag = "MainCamera";
            flying = true;
        }

        void Update()
        {
            var kb = Keyboard.current;
            var mouse = Mouse.current;
            if (kb == null) return;
            if (kb.tabKey.wasPressedThisFrame) { tourLeft = 0; Use(index + (kb.shiftKey.isPressed ? -1 : 1)); }
            if (kb.tKey.wasPressedThisFrame)
            {
                if (Touring) tourLeft = 0;                          // T again stops it
                else Tour();
            }
            if (tourLeft > 0 && Time.unscaledTime >= tourNext)
            {
                Use(index + 1);
                tourNext = Time.unscaledTime + tourSeconds;
                if (--tourLeft == 0) Debug.Log($"[KitLookAround] tour done: {cams.Length} cameras");
            }
            if (kb.fKey.wasPressedThisFrame) { tourLeft = 0; Fly(); }
            if (kb.hKey.wasPressedThisFrame) help = !help;
            if (!flying || free == null) return;
            bool look = mouse != null && mouse.rightButton.isPressed;
            Cursor.lockState = look ? CursorLockMode.Locked : CursorLockMode.None;
            if (look)
            {
                var d = mouse.delta.ReadValue();
                yaw += d.x * 0.15f;
                pitch = Mathf.Clamp(pitch - d.y * 0.15f, -89f, 89f);
            }
            if (mouse != null)
            {
                float s = mouse.scroll.ReadValue().y;
                if (s > 0f) speed = Mathf.Min(speed * 1.25f, 200f);
                else if (s < 0f) speed = Mathf.Max(speed / 1.25f, 0.5f);
            }
            var t = free.transform;
            t.rotation = Quaternion.Euler(pitch, yaw, 0f);
            var v = Vector3.zero;
            if (kb.wKey.isPressed) v += t.forward;
            if (kb.sKey.isPressed) v -= t.forward;
            if (kb.dKey.isPressed) v += t.right;
            if (kb.aKey.isPressed) v -= t.right;
            if (kb.eKey.isPressed) v += Vector3.up;
            if (kb.qKey.isPressed) v -= Vector3.up;
            if (v != Vector3.zero) t.position += v.normalized * speed * (kb.shiftKey.isPressed ? 4f : 1f) * Time.unscaledDeltaTime;
        }

        void OnDisable() => Cursor.lockState = CursorLockMode.None;

        void OnGUI()
        {
            if (!help) return;
            string text = flying
                ? $"Free camera, {speed:0.#} m/s: hold the right mouse button to look, WASD move, Q / E down / up, Shift faster, wheel speed  ·  Tab the level's cameras  ·  H hide"
                : $"Camera {index + 1} of {cams.Length} ({(index >= 0 && index < cams.Length ? cams[index].name : "none")}): Tab next, Shift+Tab previous  ·  " +
                  (tourLeft > 0 ? "touring (T stops)" : "T tour them all") + "  ·  F free camera  ·  H hide";
            var r = new Rect(12, Screen.height - 34, Screen.width - 24, 24);
            GUI.color = Color.black;
            GUI.Label(new Rect(r.x + 1, r.y + 1, r.width, r.height), text);
            GUI.color = Color.white;
            GUI.Label(r, text);
        }
    }
}
