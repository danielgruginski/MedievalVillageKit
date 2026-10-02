using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Build by hand: Tools > Medieval Kit > Kit Palette. Pick a piece, click in the Scene view to place it on the kit's
    /// grid. Every piece is authored on that grid in Blender: exterior walls stand on cell edges, corners on grid nodes,
    /// roofs on the house's centre line -- all multiples of half a 3 m cell; interior pieces on quarters of their 1.5 m
    /// cell. Storeys stand at 0, 3, 5.8, 8.6 m (vk_helpers H1 / H2).
    /// Keys while a piece is armed: R rotate 90 degrees, [ and ] storey down / up, Esc stop.
    /// </summary>
    public class KitPalette : EditorWindow
    {
        public const float ExteriorSnap = 1.5f;   // half a 3 m cell
        public const float InteriorSnap = 0.75f;  // half a 1.5 m interior cell

        [MenuItem("Tools/Medieval Kit/Kit Palette")]
        public static void Open() => GetWindow<KitPalette>("Kit Palette");

        string search = "";
        string family = "";
        Vector2 scroll;
        GameObject armed;
        float yaw;
        int storey;
        Transform parent;
        List<(string family, GameObject prefab)> pieces;
        GameObject ghost;

        void OnEnable() { SceneView.duringSceneGui += OnSceneGUI; Reload(); }
        void OnDisable() { SceneView.duringSceneGui -= OnSceneGUI; Disarm(); }

        void Reload()
        {
            pieces = new List<(string, GameObject)>();
            foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { KitPaths.Prefabs }))
            {
                string p = AssetDatabase.GUIDToAssetPath(guid);
                string fam = Path.GetDirectoryName(p).Replace('\\', '/').Substring(KitPaths.Prefabs.Length).TrimStart('/');
                var go = AssetDatabase.LoadAssetAtPath<GameObject>(p);
                if (go != null) pieces.Add((fam, go));
            }
            // premade buildings (Build Structures) drop on the exterior grid like any piece
            foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { KitBuilder.StructuresFolder }))
            {
                var go = AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(guid));
                if (go != null) pieces.Add(("Structures", go));
            }
            pieces = pieces.OrderBy(x => x.family).ThenBy(x => x.prefab.name).ToList();
        }

        public const float FreeSnap = 0.25f;      // props, dressing and nature are scattered, not built on the grid
        static readonly string[] Loose = { "_Prop_", "_Deco_", "_Debris_", "_Overlay_", "_Tree_", "_Bush_", "_Rock_",
                                           "_Plant_", "_Mushroom_", "_Flower", "_Grass", "_Fern", "_Stump", "_Log" };

        /// <summary>The grid a piece snaps to: structure on its kit's grid (VKI interior 0.75 m, VK / VKT exterior
        /// 1.5 m), props / dressing / nature on a fine 0.25 m step.</summary>
        public static float SnapFor(GameObject prefab)
        {
            var kp = prefab != null ? prefab.GetComponent<KitPiece>() : null;
            string n = kp != null ? kp.piece : prefab != null ? prefab.name : "";
            if (n.StartsWith("SM_VKI_Rock_") || n.StartsWith("SM_VKI_Ground_")) return InteriorSnap;   // dual-grid tiles
            if (Loose.Any(k => n.Contains(k))) return FreeSnap;
            return n.StartsWith("SM_VKI_") ? InteriorSnap : ExteriorSnap;
        }

        /// <summary>Exterior storey heights (vk_helpers: H1 = 3, then H2 = 2.8 per storey); interior levels are 0.</summary>
        public static float StoreyHeight(GameObject prefab, int storey)
        {
            if (storey <= 0) return 0f;
            var rules = AssetDatabase.LoadAssetAtPath<KitHouseRules>(KitHouseTools.RulesAsset);
            float h1 = rules ? rules.h1 : 3f, h2 = rules ? rules.h2 : 2.8f;
            return h1 + h2 * (storey - 1);
        }

        public static Vector3 Snap(Vector3 p, float step) =>
            new Vector3(Mathf.Round(p.x / step) * step, p.y, Mathf.Round(p.z / step) * step);

        /// <summary>The grid point nearest a world point, in the parent's space (a building can sit anywhere and turn;
        /// its pieces stay on its own grid). Returns world position and the parent-space yaw snapped to 90 degrees.</summary>
        public static Vector3 SnapWorld(GameObject prefab, Vector3 world, int storey, Transform parent)
        {
            var local = parent ? parent.InverseTransformPoint(world) : world;
            local = Snap(local, SnapFor(prefab));
            local.y = StoreyHeight(prefab, storey);
            return parent ? parent.TransformPoint(local) : local;
        }

        /// <summary>Places a kit piece as a prefab instance, snapped to its grid (also used by tests and scripts).</summary>
        public static GameObject PlaceAt(GameObject prefab, Vector3 point, float yawDeg, int storey, Transform parent = null)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            go.transform.position = SnapWorld(prefab, point, storey, parent);
            go.transform.localRotation = Quaternion.Euler(0, Mathf.Round(yawDeg / 90f) * 90f, 0);
            Undo.RegisterCreatedObjectUndo(go, "Place " + prefab.name);
            return go;
        }

        void OnGUI()
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                search = EditorGUILayout.TextField(search, EditorStyles.toolbarSearchField);
                if (GUILayout.Button("Reload", GUILayout.Width(60))) Reload();
            }
            var fams = new[] { "(all)" }.Concat(pieces.Select(x => x.family).Distinct()).ToArray();
            int fi = Mathf.Max(0, System.Array.IndexOf(fams, string.IsNullOrEmpty(family) ? "(all)" : family));
            fi = EditorGUILayout.Popup("Family", fi, fams);
            family = fi == 0 ? "" : fams[fi];
            parent = (Transform)EditorGUILayout.ObjectField("Place under", parent, typeof(Transform), true);
            EditorGUILayout.HelpBox(armed == null ? "Pick a piece, then click in the Scene view." :
                $"{armed.name}: click to place  |  R rotate ({yaw:0})  |  [ ] storey ({storey})  |  Esc stop  |  grid {SnapFor(armed)} m",
                MessageType.None);

            var list = pieces.Where(x => (family == "" || x.family == family) &&
                                         (search == "" || x.prefab.name.IndexOf(search, System.StringComparison.OrdinalIgnoreCase) >= 0)).ToList();
            const int cellW = 92;
            int cols = Mathf.Max(1, (int)((position.width - 20) / cellW));
            scroll = EditorGUILayout.BeginScrollView(scroll);
            for (int i = 0; i < list.Count; i += cols)
            {
                using (new EditorGUILayout.HorizontalScope())
                    for (int j = i; j < Mathf.Min(i + cols, list.Count); j++)
                    {
                        var pf = list[j].prefab;
                        var tex = AssetPreview.GetAssetPreview(pf) ?? AssetPreview.GetMiniThumbnail(pf);
                        var label = pf.name.Replace("SM_VKI_", "").Replace("SM_VKT_", "").Replace("SM_VK_", "");
                        var style = new GUIStyle(GUI.skin.button) { imagePosition = ImagePosition.ImageAbove, fontSize = 9, wordWrap = true };
                        bool on = armed == pf;
                        GUI.backgroundColor = on ? new Color(1f, 0.85f, 0.4f) : Color.white;
                        if (GUILayout.Button(new GUIContent(label, tex, pf.name), style, GUILayout.Width(cellW - 4), GUILayout.Height(cellW + 14)))
                        { if (on) Disarm(); else Arm(pf); }
                        GUI.backgroundColor = Color.white;
                    }
            }
            EditorGUILayout.EndScrollView();
            if (AssetPreview.IsLoadingAssetPreviews()) Repaint();
        }

        void Arm(GameObject pf)
        {
            Disarm();
            armed = pf;
            ghost = (GameObject)PrefabUtility.InstantiatePrefab(pf);
            ghost.name = "~KitPalette ghost";
            ghost.hideFlags = HideFlags.HideAndDontSave;
            foreach (var c in ghost.GetComponentsInChildren<Collider>()) c.enabled = false;
            SceneView.lastActiveSceneView?.Focus();
        }

        void Disarm()
        {
            armed = null;
            if (ghost != null) DestroyImmediate(ghost);
            ghost = null;
        }

        void OnSceneGUI(SceneView view)
        {
            if (armed == null) return;
            var e = Event.current;
            HandleUtility.AddDefaultControl(GUIUtility.GetControlID(FocusType.Passive));
            if (e.type == EventType.KeyDown)
            {
                if (e.keyCode == KeyCode.R) { yaw = (yaw + 90f) % 360f; e.Use(); }
                else if (e.keyCode == KeyCode.RightBracket) { storey++; e.Use(); }
                else if (e.keyCode == KeyCode.LeftBracket) { storey = Mathf.Max(0, storey - 1); e.Use(); }
                else if (e.keyCode == KeyCode.Escape) { Disarm(); Repaint(); e.Use(); return; }
                Repaint();
            }
            // aim at the storey's plane (so upper walls go where the lower ones are, seen from above)
            var up = parent ? parent.up : Vector3.up;
            var planePoint = parent ? parent.TransformPoint(new Vector3(0, StoreyHeight(armed, storey), 0)) : new Vector3(0, StoreyHeight(armed, storey), 0);
            var ray = HandleUtility.GUIPointToWorldRay(e.mousePosition);
            var plane = new Plane(up, planePoint);
            if (!plane.Raycast(ray, out float t)) return;
            var p = SnapWorld(armed, ray.GetPoint(t), storey, parent);
            var rot = (parent ? parent.rotation : Quaternion.identity) * Quaternion.Euler(0, yaw, 0);
            if (ghost != null) ghost.transform.SetPositionAndRotation(p, rot);
            Handles.color = new Color(1f, 0.85f, 0.3f, 0.8f);
            float s = SnapFor(armed);
            using (new Handles.DrawingScope(Matrix4x4.TRS(p, rot, Vector3.one)))
                Handles.DrawWireCube(Vector3.zero, new Vector3(s * 2, 0.02f, s * 2));
            if (e.type == EventType.MouseDown && e.button == 0 && !e.alt)
            {
                var placed = PlaceAt(armed, p, yaw, storey, parent);
                Selection.activeGameObject = placed;
                e.Use();
            }
            view.Repaint();
        }
    }

    /// <summary>Moving placed kit pieces keeps them on the grid (hold Ctrl as usual to bypass Unity's own snapping).</summary>
    [InitializeOnLoad]
    static class KitSnapOnMove
    {
        static KitSnapOnMove()
        {
            Undo.postprocessModifications += mods =>
            {
                foreach (var m in mods)
                {
                    if (!(m.currentValue.target is Transform tr)) continue;
                    if (!m.currentValue.propertyPath.StartsWith("m_LocalPosition")) continue;
                    if (tr.GetComponent<KitPiece>() == null || tr.GetComponentInParent<KitHouseGenerator>() != null) continue;
                    if (!EditorPrefs.GetBool("MedievalKit.SnapOnMove", true)) continue;
                    float step = KitPalette.SnapFor(tr.gameObject);
                    var lp = tr.localPosition;
                    var sp = new Vector3(Mathf.Round(lp.x / step) * step, lp.y, Mathf.Round(lp.z / step) * step);
                    if ((sp - lp).sqrMagnitude > 1e-8) tr.localPosition = sp;
                }
                return mods;
            };
        }

        [MenuItem("Tools/Medieval Kit/Snap Pieces When Moved", false, 200)]
        static void Toggle() => EditorPrefs.SetBool("MedievalKit.SnapOnMove", !EditorPrefs.GetBool("MedievalKit.SnapOnMove", true));

        [MenuItem("Tools/Medieval Kit/Snap Pieces When Moved", true)]
        static bool ToggleValidate()
        {
            Menu.SetChecked("Tools/Medieval Kit/Snap Pieces When Moved", EditorPrefs.GetBool("MedievalKit.SnapOnMove", true));
            return true;
        }
    }
}
