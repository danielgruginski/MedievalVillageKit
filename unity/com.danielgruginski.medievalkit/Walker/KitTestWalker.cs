using UnityEngine;
using UnityEngine.InputSystem;

namespace MedievalKit
{
    /// <summary>
    /// A stand-in player for trying levels and links: WASD / arrows to walk, E to take a link whose prompt shows,
    /// a camera at the kit's 50-degree pitch. Survives scene loads. Drop it into any kit level (or use
    /// Tools > Medieval Kit > Play From Start Level); a real game brings its own player and calls KitTravel.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class KitTestWalker : MonoBehaviour
    {
        public float speed = 4f;
        public float camDistance = 22f;
        public float camPitch = 50f;
        Camera cam;
        CharacterController cc;
        KitLink near;
        static KitTestWalker instance;

        void Awake()
        {
            if (instance != null && instance != this) { Destroy(gameObject); return; }
            instance = this;
            DontDestroyOnLoad(gameObject);
            gameObject.tag = "Player";
            cc = GetComponent<CharacterController>();
            KitTravel.SetWalker(transform);
            var cgo = new GameObject("KitTestWalker Camera");
            cgo.transform.SetParent(transform, false);
            cam = cgo.AddComponent<Camera>();
            cam.depth = 50;
            cam.nearClipPlane = 0.3f; cam.farClipPlane = 400f;
            cam.fieldOfView = 28f;
            KitTravel.Arrived += (_, __) => DisableLevelCameras();
            DisableLevelCameras();
        }

        void DisableLevelCameras()
        {
            foreach (var c in FindObjectsByType<Camera>(FindObjectsSortMode.None))
                if (c != cam) c.enabled = false;
            var level = FindAnyObjectByType<KitLevel>();
            if (level != null) camDistance = level.GetFloat("vki_cam_dist", camDistance);
        }

        void Update()
        {
            var kb = Keyboard.current;
            Vector2 mv = Vector2.zero;
            if (kb != null)
            {
                if (kb.wKey.isPressed || kb.upArrowKey.isPressed) mv.y += 1;
                if (kb.sKey.isPressed || kb.downArrowKey.isPressed) mv.y -= 1;
                if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) mv.x += 1;
                if (kb.aKey.isPressed || kb.leftArrowKey.isPressed) mv.x -= 1;
            }
            // the kit's camera looks along Unity -Z (Blender +Y): screen up = -Z, screen right = -X
            Vector3 dir = new Vector3(-mv.x, 0f, -mv.y);
            if (dir.sqrMagnitude > 0.01f)
            {
                dir.Normalize();
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(dir), 12f * Time.deltaTime);
                cc.Move(dir * speed * Time.deltaTime);
            }
            // stick to the ground (kit floors and terrain have colliders; no gravity drift where there are none)
            if (Physics.Raycast(transform.position + Vector3.up * 1.5f, Vector3.down, out var hit, 4f, ~0, QueryTriggerInteraction.Ignore))
            {
                cc.enabled = false;
                transform.position = new Vector3(transform.position.x, hit.point.y, transform.position.z);
                cc.enabled = true;
            }
            // links within reach
            near = null;
            foreach (var c in Physics.OverlapSphere(transform.position + Vector3.up, 0.6f, ~0, QueryTriggerInteraction.Collide))
            {
                var l = c.isTrigger ? c.GetComponentInParent<KitLink>() : null;
                if (l != null && l.CanUse(transform)) { near = l; break; }
            }
            if (near != null && kb != null && kb.eKey.wasPressedThisFrame) near.Use();

            float p = camPitch * Mathf.Deg2Rad;
            cam.transform.position = transform.position + new Vector3(0f, Mathf.Sin(p), Mathf.Cos(p)) * camDistance;
            cam.transform.rotation = Quaternion.LookRotation(transform.position + Vector3.up - cam.transform.position);
        }

        void OnGUI()
        {
            GUI.Label(new Rect(12, 10, 600, 22), $"{KitTravel.CurrentLevel}   (WASD walk, E use)");
            if (near != null)
                GUI.Label(new Rect(Screen.width / 2 - 120, Screen.height - 60, 400, 30), $"[E] {near.prompt}  -> {near.target}");
        }
    }
}
